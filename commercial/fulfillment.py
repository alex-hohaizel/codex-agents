#!/usr/bin/env python3
"""Seller-local test redemption and immutable acquired-rights records.

This tool is not a payment processor or production activation service. It writes
only a seller-local private database and buyer-selected delivery destinations.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import stat
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OFFER = Path(__file__).with_name("offer.json")
LEGAL = Path(__file__).with_name("legal")
SCHEMA = "codex-agents.purchase-entitlement/1"
HEX = re.compile(r"[a-f0-9]{64}\Z")
COMMIT = re.compile(r"[a-f0-9]{40}\Z")
REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[A-Za-z0-9.-]+)?\Z")
CODE = re.compile(r"AS-[A-Za-z0-9_-]{40,64}\Z")
MAX_JSON = 2 * 1024 * 1024


def require(value, message):
    if not value:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def encode(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    obj = {}
    for key, value in items:
        require(key not in obj, "duplicate JSON field")
        obj[key] = value
    return obj


def parse(raw):
    require(len(raw) <= MAX_JSON, "JSON record exceeds limit")
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def path_safe(path, *, exists=False):
    path = Path(path).expanduser().absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), "linked path rejected")
    if exists:
        require(path.is_file() and path.stat().st_size <= MAX_JSON, "missing/oversized JSON file")
    return path


def read_json(path):
    return parse(path_safe(path, exists=True).read_bytes())


def identifier(value, label):
    require(isinstance(value, str) and REF.fullmatch(value), "invalid opaque " + label)
    return value


def version(value):
    require(isinstance(value, str) and VERSION.fullmatch(value), "invalid product version")
    return int(value.split(".")[0])


def file_pin(path):
    path = path_safe(path)
    require(path.is_file(), "artifact not found")
    before = path.stat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "artifact is not an owned regular file")
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "artifact changed during read")
    return {"sha256": h.hexdigest(), "size": before.st_size}


def check_offer(value):
    require(value.get("schema") == "codex-agents.commercial-offer/1", "unsupported offer")
    require(value.get("product_id") == "codex-agent-system", "wrong offer product")
    for name in ("license_version", "support_version", "refund_version"):
        require(isinstance(value.get(name), str) and VERSION.fullmatch(value[name]), "invalid terms version")
    require(set(value.get("editions", {})) == {"solo", "team"}, "missing edition")
    for name, seats in (("solo", 1), ("team", 5)):
        row = value["editions"][name]
        require(row["named_seats"] == seats and row["use_right"] == "perpetual-purchased-product-major"
                and row["included_updates"] == "purchased-product-major", "edition weakens acquired rights")
        require(type(row["price_minor"]) is int and row["price_minor"] >= 0, "invalid configured price")
    return value


def select_artifact(catalog, name, edition):
    require(catalog.get("schema") == "codex-agents.commercial-build/1", "unsupported artifact catalog")
    require(catalog.get("product_id") == "codex-agent-system", "wrong artifact product")
    require(COMMIT.fullmatch(catalog.get("source_commit", "")), "missing exact source commit")
    version(catalog.get("product_version"))
    rows = catalog.get("files")
    require(isinstance(rows, list) and 1 <= len(rows) <= 40, "invalid artifact inventory")
    hits = [row for row in rows if row.get("name") == name]
    require(len(hits) == 1, "artifact selection is absent or ambiguous")
    item = hits[0]
    require(item.get("edition") == edition, "artifact does not match purchased edition")
    require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,179}", name),
            "unsafe download filename")
    require(HEX.fullmatch(item.get("sha256", "")) and type(item.get("size")) is int
            and item["size"] > 0, "invalid artifact pin")
    path = path_safe(item.get("path", ""))
    require(path.is_absolute() and file_pin(path) == {"sha256": item["sha256"], "size": item["size"]},
            "artifact bytes differ from reviewed catalog")
    return {"name": name, "path": str(path), "sha256": item["sha256"], "size": item["size"],
            "product_version": catalog["product_version"], "source_commit": catalog["source_commit"]}


def private_db(path):
    path = path_safe(path)
    require(not path.is_relative_to(ROOT), "seller records must stay outside the reusable source")
    require(path.suffix == ".sqlite", "use a dedicated private .sqlite file")
    if not path.parent.exists():
        path.parent.mkdir(parents=True, mode=0o700)
    if path.exists():
        info = path.stat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) & 0o077 == 0, "seller database must be owner-only")
    else:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    connection = sqlite3.connect(path, timeout=5, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.executescript("""
      CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY, code TEXT UNIQUE NOT NULL,
        code_hash TEXT UNIQUE NOT NULL, request_sha TEXT NOT NULL,
        entitlement TEXT NOT NULL, artifact TEXT NOT NULL,
        offer TEXT NOT NULL, license_text TEXT NOT NULL, created_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS deliveries (
        order_id TEXT PRIMARY KEY REFERENCES orders(order_id),
        delivery_id TEXT UNIQUE NOT NULL, first_at TEXT NOT NULL, opened_count INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS seats (
        order_id TEXT NOT NULL REFERENCES orders(order_id), slot INTEGER NOT NULL,
        member_ref TEXT, revision INTEGER NOT NULL, PRIMARY KEY(order_id,slot)
      );
      CREATE TABLE IF NOT EXISTS seat_history (
        operation_id TEXT PRIMARY KEY, request_sha TEXT NOT NULL,
        order_id TEXT NOT NULL REFERENCES orders(order_id), slot INTEGER NOT NULL,
        prior_ref TEXT, next_ref TEXT, recorded_at TEXT NOT NULL
      );
    """)
    return connection


@contextmanager
def transaction(connection):
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise


def atomic_file(path, raw, *, same_ok=False):
    path = path_safe(path)
    require(not path.is_relative_to(ROOT), "buyer private documents must stay outside reusable source")
    if path.exists():
        require(same_ok and path.is_file() and path.read_bytes() == raw, "output already exists with different bytes")
        return
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".purchase-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as file:
            os.fchmod(file.fileno(), 0o600)
            file.write(raw)
            file.flush()
            os.fsync(file.fileno())
        os.link(temporary, path)
        d = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(d)
        finally:
            os.close(d)
    finally:
        Path(temporary).unlink(missing_ok=True)


def issue(connection, offer, catalog, *, edition, artifact_name, order_id, buyer_ref,
          organization_ref=None, mode="test", license_path=LEGAL / "LICENSE.txt"):
    offer = check_offer(offer)
    require(mode == "test", "production issuance disabled until seller, legal and delivery launch gates are approved")
    identifier(order_id, "order reference")
    identifier(buyer_ref, "buyer reference")
    require(edition in offer["editions"], "unknown edition")
    if edition == "team":
        identifier(organization_ref, "organization reference")
    else:
        require(organization_ref is None, "solo does not carry an organization plan")
    item = select_artifact(catalog, artifact_name, edition)
    acquired_major = version(item["product_version"])
    spec = offer["editions"][edition]
    license_bytes = path_safe(license_path, exists=True).read_bytes()
    require(("Version " + offer["license_version"]).encode() in license_bytes, "license text version differs from offer")
    request = {"offer": offer, "edition": edition, "artifact": item, "order_id": order_id,
               "buyer_ref": buyer_ref, "organization_ref": organization_ref,
               "license_sha256": digest(license_bytes), "mode": mode}
    request_sha = digest(encode(request))
    with transaction(connection):
        old = connection.execute("SELECT request_sha,entitlement,code FROM orders WHERE order_id=?", (order_id,)).fetchone()
        if old:
            require(old[0] == request_sha, "order reference already binds another immutable purchase")
            return parse(old[1].encode()), old[2]
        now = utc()
        entitlement = {
            "schema": SCHEMA, "mode": "test-not-a-purchase",
            "product_id": offer["product_id"], "order_id": order_id, "buyer_ref": buyer_ref,
            "organization_ref": organization_ref, "edition": edition, "named_seats": spec["named_seats"],
            "purchased_product_major": acquired_major, "acquired_use": "perpetual-purchased-product-major",
            "included_updates": "purchased-product-major", "purchased_version": item["product_version"],
            "license_version": offer["license_version"], "license_sha256": digest(license_bytes),
            "support_version": offer["support_version"], "refund_version": offer["refund_version"],
            "offer_snapshot": {k: spec[k] for k in spec},
            "support_snapshot": offer["support"], "refund_snapshot": offer["refunds"],
            "currency": offer["sale_currency"], "price_minor": spec["price_minor"],
            "seller": offer["seller"], "source_commit": item["source_commit"],
            "artifact": {k: item[k] for k in ("name", "sha256", "size")},
            "issued_at": now, "channel": "isolated-local-test",
            "authenticity": "verify-original-trusted-delivery-and-purchase-confirmation; not signed or DRM"
        }
        # Return the same detached JSON snapshot that is persisted. In-memory
        # caller edits to the current offer must not mutate an issued receipt.
        entitlement = parse(encode(entitlement))
        code = "AS-" + secrets.token_urlsafe(32)
        connection.execute("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?,?)",
                           (order_id, code, digest(code.encode()), request_sha,
                            encode(entitlement).decode(), encode(item).decode(),
                            encode(offer).decode(), license_bytes.decode(), now))
        for seat in range(1, spec["named_seats"] + 1):
            connection.execute("INSERT INTO seats VALUES(?,?,?,?)",
                               (order_id, seat, buyer_ref if edition == "solo" and seat == 1 else None, 0))
        return entitlement, code


def order_for_code(connection, code):
    require(isinstance(code, str) and CODE.fullmatch(code), "redemption code not found")
    row = connection.execute("SELECT order_id,entitlement,artifact,license_text FROM orders WHERE code_hash=?",
                             (digest(code.encode()),)).fetchone()
    require(row is not None, "redemption code not found")
    return {"order_id": row[0], "entitlement": parse(row[1].encode()),
            "artifact": parse(row[2].encode()), "license_text": row[3]}


def checked_artifact(order):
    artifact = order["artifact"]
    require(file_pin(artifact["path"]) == {"sha256": artifact["sha256"], "size": artifact["size"]},
            "delivery held: recorded artifact bytes changed or unavailable")
    return artifact


def redeem(connection, code):
    order = order_for_code(connection, code)
    checked_artifact(order)
    with transaction(connection):
        row = connection.execute("SELECT delivery_id,first_at,opened_count FROM deliveries WHERE order_id=?",
                                 (order["order_id"],)).fetchone()
        if row:
            connection.execute("UPDATE deliveries SET opened_count=opened_count+1 WHERE order_id=?", (order["order_id"],))
            delivery_id, when = row[0], row[1]
        else:
            delivery_id, when = "delivery-" + secrets.token_hex(16), utc()
            connection.execute("INSERT INTO deliveries VALUES(?,?,?,?)", (order["order_id"], delivery_id, when, 1))
    return {**order, "confirmation": {
        "schema": "codex-agents.purchase-confirmation/1", "delivery_id": delivery_id,
        "first_delivered_at": when, "mode": "test-not-a-purchase",
        "entitlement": order["entitlement"], "license_sha256": digest(order["license_text"].encode()),
        "artifact": {k: order["artifact"][k] for k in ("name", "sha256", "size")},
        "support_reference": {"order_id": order["order_id"], "product_version": order["artifact"]["product_version"],
                              "edition": order["entitlement"]["edition"]},
        "payment_processed": False, "external_channel_integrated": False
    }}


def deliver_to(connection, code, destination):
    order = redeem(connection, code)
    destination = path_safe(destination)
    require(not destination.is_relative_to(ROOT), "private buyer delivery must be outside reusable source")
    destination.mkdir(parents=True, mode=0o700, exist_ok=True)
    artifact = checked_artifact(order)
    target = destination / artifact["name"]
    if target.exists():
        require(file_pin(target) == {"sha256": artifact["sha256"], "size": artifact["size"]},
                "existing downloaded artifact differs")
    else:
        fd, temp = tempfile.mkstemp(prefix=".delivery-", dir=destination)
        try:
            with os.fdopen(fd, "wb") as output, Path(artifact["path"]).open("rb") as source:
                shutil.copyfileobj(source, output)
                output.flush()
                os.fsync(output.fileno())
            require(file_pin(temp) == {"sha256": artifact["sha256"], "size": artifact["size"]}, "copy changed")
            os.link(temp, target)
        finally:
            Path(temp).unlink(missing_ok=True)
    atomic_file(destination / "purchase-confirmation.json", encode(order["confirmation"]), same_ok=True)
    atomic_file(destination / "entitlement.json", encode(order["entitlement"]), same_ok=True)
    atomic_file(destination / "LICENSE.txt", order["license_text"].encode(), same_ok=True)
    text = ("# Your test delivery\n\nThis is not an actual purchase. Keep entitlement.json, LICENSE.txt "
            "and purchase-confirmation.json outside any public project.\n\n"
            "Extract the exact archive and open START_HERE.html. Follow setup's audit, install, "
            "verify and first-task steps. Keep the original ZIP and recovery journal.\n")
    atomic_file(destination / "READ_ME_FIRST.md", text.encode(), same_ok=True)
    return {"status": "delivered", "destination": str(destination), "artifact": target.name,
            "sha256": artifact["sha256"], "delivery_id": order["confirmation"]["delivery_id"],
            "entitlement": str(destination / "entitlement.json"), "payment_processed": False}


def inspect_entitlement(entitlement, target_version=None):
    require(entitlement.get("schema") == SCHEMA, "unsupported entitlement")
    require(entitlement.get("mode") in ("test-not-a-purchase", "purchased"), "unrecognized entitlement status")
    require(entitlement.get("product_id") == "codex-agent-system", "wrong entitlement product")
    identifier(entitlement.get("order_id"), "order reference")
    require(entitlement.get("edition") in ("solo", "team"), "invalid edition")
    require(entitlement.get("named_seats") == {"solo": 1, "team": 5}[entitlement["edition"]], "edition seat mismatch")
    major = entitlement.get("purchased_product_major")
    require(type(major) is int and major >= 0 and version(entitlement.get("purchased_version")) == major,
            "invalid acquired major")
    require(entitlement.get("acquired_use") == "perpetual-purchased-product-major"
            and entitlement.get("included_updates") == "purchased-product-major", "unsupported rights snapshot")
    eligible = None if target_version is None else version(target_version) == major
    return {"status": "test-record" if entitlement["mode"] == "test-not-a-purchase" else "document-record",
            "acquired_major": major, "acquired_use_persists_without_store": True,
            "target_version": target_version, "target_major_included": eligible,
            "existing_project_files_changed": False, "signature_verified": False,
            "authenticity": "requires original trusted delivery/purchase records; this checks structure and recorded rights only"}


def replace_seat(connection, *, order_id, slot, expected_revision, retired_ref, next_ref, operation_id):
    identifier(order_id, "order reference")
    identifier(operation_id, "operation reference")
    identifier(next_ref, "replacement member reference")
    if retired_ref is not None:
        identifier(retired_ref, "retired member reference")
    require(type(slot) is int and 1 <= slot <= 5 and type(expected_revision) is int and expected_revision >= 0,
            "invalid seat selector")
    request = {"order_id": order_id, "slot": slot, "expected_revision": expected_revision,
               "retired_ref": retired_ref, "next_ref": next_ref}
    request_sha = digest(encode(request))
    with transaction(connection):
        prior = connection.execute("SELECT request_sha FROM seat_history WHERE operation_id=?", (operation_id,)).fetchone()
        if prior:
            require(prior[0] == request_sha, "seat operation already binds a different request")
            return {"status": "already-recorded", "operation_id": operation_id}
        found = connection.execute("SELECT entitlement FROM orders WHERE order_id=?", (order_id,)).fetchone()
        require(found is not None and parse(found[0].encode())["edition"] == "team", "seat replacement requires a Team order")
        row = connection.execute("SELECT member_ref,revision FROM seats WHERE order_id=? AND slot=?", (order_id, slot)).fetchone()
        require(row is not None and row[0] == retired_ref and row[1] == expected_revision,
                "seat changed; review current assignment before replacement")
        require(retired_ref != next_ref, "replacement must identify a different named member")
        duplicate = connection.execute("SELECT slot FROM seats WHERE order_id=? AND member_ref=?", (order_id, next_ref)).fetchone()
        require(duplicate is None, "replacement is already assigned another seat")
        connection.execute("UPDATE seats SET member_ref=?,revision=revision+1 WHERE order_id=? AND slot=?",
                           (next_ref, order_id, slot))
        connection.execute("INSERT INTO seat_history VALUES(?,?,?,?,?,?,?)",
                           (operation_id, request_sha, order_id, slot, retired_ref, next_ref, utc()))
    return {"status": "recorded", "operation_id": operation_id, "slot": slot,
            "new_revision": expected_revision + 1, "prior_member_access_must_be_retired": True}


def redemption_page():
    style = """
*{box-sizing:border-box}body{margin:0;background:#081d27;color:#eaf8fa;font:17px/1.55 system-ui,sans-serif}
main{max-width:760px;margin:5vh auto;padding:36px}header{display:flex;justify-content:space-between;gap:20px;align-items:center}
h1{font-size:clamp(32px,7vw,54px);line-height:1.06;letter-spacing:-.04em}small{color:#9ed9df}label{display:block;font-weight:700;margin-bottom:8px}
input{width:100%;font:inherit;background:#102e3a;color:#fff;border:1px solid #80b9c5;padding:14px;border-radius:7px}
button,a{font:inherit}button{cursor:pointer;background:#72ebd8;color:#061d24;border:0;border-radius:6px;padding:11px 18px;font-weight:750}
button:disabled{opacity:.6;cursor:wait}.language{background:transparent;color:#c4eaee;border:1px solid #7aabb4;padding:6px 10px}
form{margin:30px 0;padding:24px;border:1px solid #315d6b;border-radius:12px;background:#0d2732}form button{margin-top:14px}
:focus-visible{outline:3px solid #ffe09e;outline-offset:4px}section{border-top:1px solid #315d6b;padding-top:20px}
a{display:inline-block;color:#92f0de;margin:8px 22px 8px 0;text-underline-offset:4px;overflow-wrap:anywhere}
#status{min-height:30px;font-weight:650}.facts{white-space:pre-wrap;overflow-wrap:anywhere;background:#102e3a;padding:14px;border-radius:7px}
@media(max-width:500px){main{padding:22px}header{align-items:flex-start}form{padding:18px}}
"""
    script = r"""
(() => {
 const words = {
 en:{tag:"SELLER-LOCAL TEST / NO PAYMENT",title:"Receive your test package",intro:"Use the private code from the controlled test order. This demonstration does not process a purchase or activate a product.",label:"Private redemption code",button:"Get test delivery",privacy:"The code stays in this page only for this request. Never include it in a public screenshot.",pending:"Checking the exact test order…",error:"Delivery unavailable. Check the code and ask the seller to verify the original artifact.",success:"Test delivery ready. Reuse your order confirmation to download the same package again.",download:"Download exact package",license:"Read recorded license",confirmation:"Save order confirmation",notes:"Preserve the archive, entitlement and accepted license. Use the package start page after download. Model accounts and usage are separate.",edition:"Edition",order:"Test order",version:"Product version",digest:"Archive SHA-256",mode:"This is a test, not an actual purchase."},
 uk:{tag:"ЛОКАЛЬНЕ ДЕМО ПРОДАВЦЯ / БЕЗ ОПЛАТИ",title:"Отримайте тестовий комплект",intro:"Введіть приватний код контрольного тестового замовлення. Це демо не проводить покупку й не активує продукт.",label:"Приватний код отримання",button:"Отримати тестову доставку",privacy:"Код використовується лише для цього запиту. Не показуйте його на публічних знімках.",pending:"Перевіряємо точне тестове замовлення…",error:"Доставка недоступна. Перевірте код і попросіть продавця звірити початковий артефакт.",success:"Тестова доставка готова. Підтвердження замовлення дає повторно отримати той самий комплект.",download:"Завантажити точний комплект",license:"Прочитати збережену ліцензію",confirmation:"Зберегти підтвердження",notes:"Збережіть архів, документ прав і прийняту ліцензію. Після завантаження відкрийте стартову сторінку комплекту. Моделі й акаунти оплачуються окремо.",edition:"Редакція",order:"Тестове замовлення",version:"Версія продукту",digest:"SHA-256 архіву",mode:"Це тест, а не фактична покупка."}
 };
 let language="en", result=null, busy=false;
 const text=(id,value)=>{document.getElementById(id).textContent=value};
 const form=document.getElementById("redeem"),code=document.getElementById("code"),button=document.getElementById("submit");
 function draw(){
  const w=words[language]; document.documentElement.lang=language;
  for(const id of ["tag","title","intro","label","button","privacy","notes"])text(id==="button"?"submit":id,w[id]);
  text("toggle",language==="en"?"Українська":"English");
  if(result)show(result);else text("status",busy?w.pending:"");
 }
 function show(receipt){
  const w=words[language],purchase=receipt.confirmation.entitlement;
  text("status",w.success);
  text("facts",w.mode+"\n"+w.order+": "+purchase.order_id+"\n"+w.edition+": "+purchase.edition+" ("+purchase.named_seats+")\n"+w.version+": "+purchase.purchased_version+"\n"+w.digest+": "+receipt.confirmation.artifact.sha256);
  const links=document.getElementById("links");links.replaceChildren();
  for(const [key,label] of [["download_url",w.download],["license_url",w.license],["confirmation_url",w.confirmation]]){
   const url=new URL(receipt[key],location.origin);
   if(url.origin!==location.origin)throw new Error("Unexpected origin");
   const a=document.createElement("a");a.href=url.href;a.textContent=label;a.rel="noreferrer";links.append(a);
  }
  document.getElementById("result").hidden=false;
 }
 document.getElementById("toggle").addEventListener("click",()=>{language=language==="en"?"uk":"en";draw()});
 form.addEventListener("submit",async event=>{
  event.preventDefault();if(busy)return;busy=true;button.disabled=true;result=null;
  document.getElementById("result").hidden=true;text("status",words[language].pending);
  const value=code.value.trim();code.value="";
  try{
   const response=await fetch("/redeem",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code:value}),credentials:"omit",cache:"no-store"});
   if(!response.ok)throw new Error("Unavailable");
   result=await response.json();show(result);
  }catch{result=null;text("status",words[language].error)}
  finally{busy=false;button.disabled=false}
 });
 draw();
})();
"""
    def hash_source(raw):
        return base64.b64encode(hashlib.sha256(raw.encode()).digest()).decode()
    csp = ("default-src 'none'; style-src 'sha256-" + hash_source(style)
           + "'; script-src 'sha256-" + hash_source(script)
           + "'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Codex Agent System — Local test delivery</title><style>""" + style + """</style>
<main><header><small id="tag"></small><button class="language" id="toggle" type="button">Українська</button></header>
<h1 id="title"></h1><p id="intro"></p><form id="redeem"><label id="label" for="code"></label>
<input type="password" id="code" autocomplete="off" spellcheck="false" required maxlength="70" aria-describedby="privacy">
<small id="privacy"></small><br><button id="submit" type="submit"></button></form>
<p id="status" role="status" aria-live="polite"></p><section id="result" hidden><div id="facts" class="facts"></div><nav id="links" aria-label="Delivery links"></nav></section>
<p id="notes"></p></main><script>""" + script + """</script></html>"""
    return page.encode(), csp


def serve(database, host, port, ready):
    require(host == "127.0.0.1", "test delivery only listens on IPv4 loopback")
    sessions = {}
    class Handler(BaseHTTPRequestHandler):
        server_version = "LocalDeliveryTest/1"
        def log_message(self, *_):
            pass
        def headers_json(self, status, value):
            raw = encode(value)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        def local_request(self):
            hostvalue = self.headers.get("Host", "")
            require(hostvalue == f"127.0.0.1:{self.server.server_port}", "unexpected local Host")
            origin = self.headers.get("Origin")
            require(origin is None or origin == "http://" + hostvalue, "cross-origin request rejected")
        def do_POST(self):
            connection = None
            try:
                self.local_request()
                require(self.path == "/redeem", "unknown route")
                require(self.headers.get("Content-Type", "").split(";")[0] == "application/json", "JSON required")
                size = self.headers.get("Content-Length", "")
                require(size.isdecimal() and 0 < int(size) <= 4096, "bounded request length required")
                body = parse(self.rfile.read(int(size)))
                require(isinstance(body, dict) and set(body) == {"code"}, "one redemption code required")
                connection = private_db(database)
                order = redeem(connection, body["code"])
                require(len(sessions) < 1000, "session bound reached")
                token = secrets.token_urlsafe(32)
                sessions[token] = {"order": order, "expires": time.monotonic() + 900}
                prefix = f"http://127.0.0.1:{self.server.server_port}"
                self.headers_json(200, {"mode": "test-not-a-purchase", "confirmation": order["confirmation"],
                    "download_url": prefix + "/download/" + token,
                    "license_url": prefix + "/license/" + token,
                    "confirmation_url": prefix + "/confirmation/" + token})
            except (ValueError, KeyError, OSError, sqlite3.Error):
                self.headers_json(400, {"status": "blocked", "message": "Cannot redeem this exact test order; check private seller diagnostics."})
            finally:
                if connection:
                    connection.close()
        def do_GET(self):
            try:
                self.local_request()
                if self.path == "/":
                    raw, policy = redemption_page()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Security-Policy", policy)
                    self.send_header("Referrer-Policy", "no-referrer")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                    return
                route = urlsplit(self.path)
                require(not route.query and not route.fragment, "query is not supported")
                parts = route.path.strip("/").split("/")
                require(len(parts) == 2 and parts[0] in ("download", "license", "confirmation"), "unknown route")
                session = sessions.get(parts[1])
                require(session is not None and session["expires"] > time.monotonic(), "session unavailable")
                order = session["order"]
                if parts[0] == "confirmation":
                    self.headers_json(200, order["confirmation"])
                    return
                if parts[0] == "license":
                    raw, name = order["license_text"].encode(), "LICENSE.txt"
                    stream = None
                else:
                    item = checked_artifact(order)
                    stream = Path(item["path"]).open("rb")
                    info = os.fstat(stream.fileno())
                    require(info.st_size == item["size"], "artifact changed before download")
                    raw, name = None, item["name"]
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", 'attachment; filename="' + name + '"')
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(raw) if raw is not None else item["size"]))
                self.end_headers()
                if stream:
                    with stream:
                        shutil.copyfileobj(stream, self.wfile)
                else:
                    self.wfile.write(raw)
            except (ValueError, KeyError, OSError):
                self.headers_json(404, {"status": "unavailable"})
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    record = {"schema": "codex-agents.local-delivery-server/1", "mode": "isolated-test",
              "url": f"http://{host}:{server.server_port}", "pid": os.getpid(),
              "external_payment_integration": False}
    atomic_file(ready, encode(record))
    try:
        server.serve_forever(poll_interval=.2)
    finally:
        server.server_close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    issue_cmd = sub.add_parser("issue")
    issue_cmd.add_argument("--database", type=Path, required=True)
    issue_cmd.add_argument("--offer", type=Path, default=OFFER)
    issue_cmd.add_argument("--catalog", type=Path, required=True)
    issue_cmd.add_argument("--edition", choices=("solo", "team"), required=True)
    issue_cmd.add_argument("--artifact", required=True)
    issue_cmd.add_argument("--order-id", required=True)
    issue_cmd.add_argument("--buyer-ref", required=True)
    issue_cmd.add_argument("--organization-ref")
    issue_cmd.add_argument("--code-file", type=Path, required=True)
    redeem_cmd = sub.add_parser("redeem")
    redeem_cmd.add_argument("--database", type=Path, required=True)
    redeem_cmd.add_argument("--code-file", type=Path, required=True)
    redeem_cmd.add_argument("--destination", type=Path, required=True)
    inspect_cmd = sub.add_parser("inspect")
    inspect_cmd.add_argument("--entitlement", type=Path, required=True)
    inspect_cmd.add_argument("--target-version")
    seat_cmd = sub.add_parser("replace-seat")
    seat_cmd.add_argument("--database", type=Path, required=True)
    seat_cmd.add_argument("--order-id", required=True)
    seat_cmd.add_argument("--slot", type=int, required=True)
    seat_cmd.add_argument("--expected-revision", type=int, required=True)
    seat_cmd.add_argument("--retired-ref")
    seat_cmd.add_argument("--next-ref", required=True)
    seat_cmd.add_argument("--operation-id", required=True)
    serve_cmd = sub.add_parser("serve")
    serve_cmd.add_argument("--database", type=Path, required=True)
    serve_cmd.add_argument("--listen", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=0)
    serve_cmd.add_argument("--ready", type=Path, required=True)
    args = parser.parse_args(argv)
    connection = None
    try:
        if args.action == "inspect":
            result = inspect_entitlement(read_json(args.entitlement), args.target_version)
        elif args.action == "serve":
            serve(args.database, args.listen, args.port, args.ready)
            return 0
        else:
            connection = private_db(args.database)
            if args.action == "issue":
                entitlement, code = issue(connection, read_json(args.offer), read_json(args.catalog),
                    edition=args.edition, artifact_name=args.artifact, order_id=args.order_id,
                    buyer_ref=args.buyer_ref, organization_ref=args.organization_ref)
                atomic_file(args.code_file, (code + "\n").encode(), same_ok=True)
                result = {"status": "test-order-issued", "order_id": entitlement["order_id"],
                          "edition": entitlement["edition"], "named_seats": entitlement["named_seats"],
                          "code_file": str(args.code_file), "payment_processed": False}
            elif args.action == "redeem":
                code = path_safe(args.code_file, exists=True).read_text().strip()
                result = deliver_to(connection, code, args.destination)
            else:
                result = replace_seat(connection, order_id=args.order_id, slot=args.slot,
                    expected_revision=args.expected_revision, retired_ref=args.retired_ref,
                    next_ref=args.next_ref, operation_id=args.operation_id)
        print(encode(result).decode(), end="")
        return 0
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
