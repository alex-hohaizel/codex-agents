#!/usr/bin/env python3
"""Plan and reconcile explicit ticket effects with a mapped tracker."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

import ticket_tree as trees
import ticket_replan_store as store

cx = trees.context
MAPPING = "codex-agents.tracker-mapping/1"
PREVIEW = "codex-agents.tracker-sync-preview/1"
LEDGER = "codex-agents.tracker-operation/1"
FIELDS = ("title", "status", "parent_id", "blocker_ids")
PROVIDERS = {"github", "linear", "jira", "notion", "trello"}
MARKER = re.compile(r"\[codex-agents:[a-f0-9]{64}\]")


def encoded(obj):
    return store.projection_bytes(obj)


def sha(obj):
    return cx.digest(encoded(obj))


def stable(value):
    cx.require(isinstance(value, str) and 1 <= len(value) <= 256 and value == value.strip()
               and not any(ord(c) < 32 or ord(c) == 127 for c in value), "invalid stable tracker ID")
    return value


def field_value(field, value):
    if field == "title":
        cx.require(isinstance(value, str) and 1 <= len(value.strip()) and len(value) <= 4096, "invalid tracker title")
        return value
    if value is None and field in ("status", "parent_id", "blocker_ids"):
        return None
    if field == "blocker_ids":
        cx.require(isinstance(value, list) and len(value) <= 256, "invalid blockers")
        ids = [stable(item) for item in value]
        cx.require(len(set(ids)) == len(ids), "duplicate blockers")
        return sorted(ids)
    return stable(value)


def snapshot_local(root, projection, config, mapping):
    snap = trees.Snapshot(root)
    board = trees.project_board(root, projection, snapshot=snap)
    cfg = cx.json_object(snap.read(config))
    mp = cx.json_object(snap.read(mapping))
    cx.require(set(mp) == {"schema_version", "project_id", "provider", "container_id", "statuses", "tickets"}
               and mp["schema_version"] == MAPPING, "unsupported tracker mapping")
    cx.require(cfg.get("provider") in PROVIDERS and isinstance(cfg.get("container"), dict), "invalid tracker config")
    provider = cfg["provider"]
    container = stable(cfg["container"].get("id"))
    cx.require(mp["provider"] == provider and mp["container_id"] == container
               and mp["project_id"] == board["project_id"], "mapping, provider and local project scope disagree")
    statuses = mp["statuses"]
    cx.require(isinstance(statuses, dict) and set(statuses) <= trees.STATUSES,
               "unsupported local status selector in mapping")
    for selector in statuses.values():
        stable(selector)
    local = {t["id"]: t for t in board["tickets"] if not t.get("replan_retirement")}
    cx.require(isinstance(mp["tickets"], list) and len(mp["tickets"]) <= 256, "expected bounded tracker mappings")
    mapped, remote_ids = {}, set()
    for row in mp["tickets"]:
        cx.require(isinstance(row, dict) and set(row) == {"ticket_id", "id", "key", "last"},
                   "invalid mapped entity")
        tid, rid, key = [stable(row[k]) for k in ("ticket_id", "id", "key")]
        cx.require(tid in local and tid not in mapped and rid not in remote_ids, "unknown or repeated mapped entity")
        last = row["last"]
        cx.require(isinstance(last, dict) and set(last) <= set(FIELDS), "invalid prior observed field state")
        mapped[tid] = {"ticket_id":tid,"id":rid,"key":key,"last":{k:field_value(k,v) for k,v in last.items()}}
        remote_ids.add(rid)
    pins = {k: {"path":p,"sha256":cx.digest(snap.read(p))}
            for k,p in (("projection",projection),("config",config),("mapping",mapping))}
    pins["inputs"] = {p: cx.digest(b) for p,b in sorted(snap.paths.items())}
    return snap, board, cfg, statuses, local, mapped, pins


def safe_item(raw, container):
    cx.require(isinstance(raw, dict) and raw.get("container_id") == container, "provider returned wrong container")
    item = {k: stable(raw.get(k)) for k in ("id","key","container_id")}
    for key in FIELDS:
        if key in raw:
            item[key] = field_value(key, raw[key])
    cx.require("title" in item, "provider omitted tracker title")
    marker = raw.get("marker")
    if marker is not None:
        cx.require(isinstance(marker,str) and MARKER.fullmatch(marker), "invalid provider marker")
    item["marker"] = marker
    return item


def marker_for(provider, container, project, ticket):
    return "[codex-agents:" + sha([provider, container, project, ticket]) + "]"


def exact_container(client, config):
    raw = client.verify_container()
    expected = config["container"]
    cx.require(isinstance(raw,dict) and raw.get("id") == expected["id"] and
               ("key" not in expected or raw.get("key") == expected["key"]), "provider container read-back disagrees")
    return raw["id"]


def check_remote_set(rows, container):
    cx.require(isinstance(rows,list) and len(rows) <= 1200,"tracker listing exceeds reviewed bounds")
    safe = [safe_item(item,container) for item in rows]
    cx.require(len({r["id"] for r in safe}) == len(safe),"provider returned duplicate issue identities")
    return safe


def make_actions(board, config, statuses, local, mapped, remote, capabilities):
    observed = {row["id"]: row for row in remote}
    proj = board["project_id"]
    provider, container = config["provider"], config["container"]["id"]
    generated, notes = {}, []
    managed_ids = {row["id"] for row in mapped.values()}
    def note(ticket, code, **extra):
        notes.append({"ticket_id":ticket,"code":code,**extra})
    def action(ticket, op, **fields):
        body = {"ticket_id":ticket,"operation":op,**fields}
        generated[sha(body)] = body
    for tid in board["evaluation_order"]:
        if tid not in local:
            continue
        ticket = local[tid]
        marker = marker_for(provider, container, proj, tid)
        seen = [r for r in remote if r["marker"] == marker]
        if tid not in mapped:
            if len(seen) > 1:
                note(tid,"duplicate-marker")
            elif seen:
                entry = seen[0]
                if entry["id"] in managed_ids:
                    note(tid,"marker-belongs-to-another-mapped-ticket")
                else:
                    note(tid,"mapping-candidate",mapped={"ticket_id":tid,"id":entry["id"],"key":entry["key"],
                         "last":{k:entry[k] for k in FIELDS if k in entry}})
            elif "create" not in capabilities:
                note(tid,"create-unsupported")
            elif ticket["parent"] is not None and ticket["parent"] not in mapped:
                note(tid,"map-parent-first",parent=ticket["parent"])
            else:
                if ticket["parent"] is not None:
                    parent = mapped[ticket["parent"]]
                    if parent["id"] not in observed or observed[parent["id"]]["key"] != parent["key"]:
                        note(tid,"mapped-parent-not-observed",parent=ticket["parent"])
                        continue
                    if "update:parent_id" not in capabilities:
                        note(tid,"parent-unsupported",parent=ticket["parent"])
                        continue
                action(tid,"create",desired={"title":ticket["title"],"kind":ticket["kind"],"marker":marker})
            continue
        target = mapped[tid]
        row = observed.get(target["id"])
        if row is None or row["key"] != target["key"]:
            note(tid,"mapped-identity-unobserved")
            continue
        if len(seen) > 1 or (seen and seen[0]["id"] != row["id"]):
            note(tid,"marker-mapping-conflict")
            continue
        desired = {"title":ticket["title"]}
        status = ticket["recorded_status"]
        if status in statuses and (status != "accepted" or ticket["acceptance_status"] == "supported"):
            desired["status"] = statuses[status]
        else:
            note(tid,"local-acceptance-unproved" if status == "accepted" else "status-unmapped",status=status)
        parent = ticket["parent"]
        if parent is None or parent in mapped:
            desired["parent_id"] = None if parent is None else mapped[parent]["id"]
        else:
            note(tid,"parent-unmapped",parent=parent)
        deps = ticket["depends_on"]
        if all(d in mapped for d in deps):
            desired["blocker_ids"] = sorted(mapped[d]["id"] for d in deps)
        else:
            note(tid,"prerequisites-unmapped",tickets=[d for d in deps if d not in mapped])
        for field, want in desired.items():
            if field not in row or (field in ("status","blocker_ids") and row[field] is None):
                if want not in (None, []):
                    note(tid,"provider-field-unobserved",field=field)
                continue
            have = row[field]
            if have == want:
                continue
            if field in ("parent_id","blocker_ids"):
                endpoints = have if isinstance(have,list) else [] if have is None else [have]
                unmanaged = sorted(set(endpoints)-managed_ids)
                if unmanaged:
                    note(tid,"unmapped-remote-relationship-held",field=field,endpoints=unmanaged)
                    continue
            if field not in target["last"]:
                note(tid,"baseline-required",field=field,local=want,remote=have)
                continue
            last = target["last"][field]
            if want == last:
                note(tid,"inbound-proposal",field=field,remote=have,acceptance_granted=False)
            elif have != last:
                note(tid,"concurrent-change",field=field,local=want,remote=have,previous=last)
            elif "update:"+field not in capabilities:
                note(tid,"unsupported-change",field=field,local=want,remote=have)
            else:
                action(tid,"update",target={k:row[k] for k in ("id","key","container_id")},
                       field=field,before=have,desired=want)
    discovered = [r for r in remote if r["id"] not in managed_ids]
    return generated,notes,discovered


def preview(root, projection, config, mapping, factory):
    snap, board, cfg, statuses, local, mapped, pins = snapshot_local(root,projection,config,mapping)
    client = factory(cfg)
    container = exact_container(client,cfg)
    remote = check_remote_set(client.list_items(),container)
    seen = {row["id"]: i for i,row in enumerate(remote)}
    for row in mapped.values():
        index = seen.get(row["id"])
        if index is not None and remote[index]["key"] == row["key"]:
            detail = safe_item(client.read_item(row["id"],row["key"]),container)
            cx.require(detail["id"]==row["id"] and detail["key"]==row["key"],"mapped issue identity changed while reading details")
            remote[index]=detail
    capabilities = sorted(client.capabilities)
    actions, notes, discovered = make_actions(board,cfg,statuses,local,mapped,remote,capabilities)
    snap.verify_unchanged()
    result = {"schema_version":PREVIEW,"checkout_sha256":cx.digest(os.fsencode(root)),
            "observed_at":datetime.now(timezone.utc).isoformat(),
            "project_id":board["project_id"],"provider":cfg["provider"],"container_id":container,
            "pins":pins,"capabilities":capabilities,"observed":remote,"actions":actions,"findings":notes,
            "unmapped_remote":discovered,"requests":list(client.receipts),"writes":0}
    cx.require(len(encoded(result)) <= cx.MAX_BOUND_SOURCE,"preview exceeds local bound; narrow the provider target")
    return result


def check_id(value):
    cx.require(isinstance(value,str) and cx.HASH.fullmatch(value),"expected exact SHA-256 selector")
    return value


def fsync(path):
    fd = os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save(path, data, known):
    raw = encoded(data)
    cx.require(len(raw) <= 64*1024,"operation receipt exceeds the local journal limit")
    if known:
        store.atomic_replace(path,raw,lambda: cx.require(not path.is_symlink(),"linked tracker journal"))
    else:
        fd,name = tempfile.mkstemp(prefix=".tracker-sync-",dir=path.parent)
        try:
            with os.fdopen(fd,"wb") as file:
                file.write(raw); file.flush(); os.fsync(file.fileno())
            os.link(name,path)
            fsync(path.parent)
        finally:
            Path(name).unlink(missing_ok=True)


def effect_for(obj, action):
    return {**action, "project":obj["project_id"], "provider":obj["provider"], "container":obj["container_id"]}


def slot(effect):
    scope = (effect["project"], effect["provider"], effect["container"])
    if effect["operation"] == "create":
        return (*scope, "create", effect["desired"]["marker"])
    return (*scope, "update", effect["target"]["id"], effect["field"])


def read_operation(root, path):
    info = path.lstat()
    cx.require(stat.S_ISREG(info.st_mode) and info.st_nlink==1, "invalid tracker journal file")
    ledger = cx.json_object(cx.bound_bytes(root,path.relative_to(root).as_posix()))
    cx.require(ledger.get("schema_version")==LEDGER and isinstance(ledger.get("effect"),dict)
               and path.stem==sha(ledger["effect"]) and ledger.get("checkout_sha256")==cx.digest(os.fsencode(root))
               and ledger.get("status") in ("attempting","observed","rejected"), "tracker journal identity mismatch")
    return ledger


def other_pending(root, directory, effect):
    records = list(directory.glob("*.json"))
    cx.require(len(records) <= 2000, "tracker journal inventory needs operator review")
    for record in records:
        pending = read_operation(root,record)
        if pending["status"]=="attempting" and pending["effect"] != effect and slot(pending["effect"]) == slot(effect):
            return record.stem


def reconcile(client, action, mapping, container):
    if action["operation"] == "create":
        desired = action["desired"]
        rows = check_remote_set(client.find_marker(desired["marker"]),container)
        cx.require(all(r["marker"] == desired["marker"] for r in rows),"provider marker read-back disagrees")
        if len(rows) > 1:
            return "ambiguous-create", None
        if not rows:
            return "not-observed", None
        observed = safe_item(client.read_item(rows[0]["id"],rows[0]["key"]),container)
        cx.require(all(observed[k] == rows[0][k] for k in ("id","key","marker")),"create identity changed during read-back")
        if observed["title"] != desired["title"]:
            return "remote-drift", None
        other = next((k for k,v in mapping.items() if v["id"] == observed["id"]),None)
        cx.require(other is None, "created marker conflicts with an existing mapping")
        return "observed", {"ticket_id":action["ticket_id"],"id":observed["id"],"key":observed["key"],
                            "last":{k:observed[k] for k in FIELDS if k in observed}}
    target = action["target"]
    item = safe_item(client.read_item(target["id"],target["key"]),container)
    cx.require(all(item[k] == v for k,v in target.items()),"mapped issue identity changed")
    field = action["field"]
    cx.require(field in item and not (field in ("status","blocker_ids") and item[field] is None),"cannot re-read approved field")
    if item[field] == action["desired"]:
        row = mapping[action["ticket_id"]]
        return "observed", {**row,"last":{**row["last"],field:item[field]}}
    return ("not-observed" if item[field] == action["before"] else "remote-drift"), None


def read_back(root,obj,expected,action_id,factory):
    from tracker_providers import ProviderError
    action = obj["actions"][action_id]
    cx.require(sha(action)==action_id,"invalid tracker action identity")
    effect = effect_for(obj,action)
    directory = cx.local(root,".atelier/tracker-sync",existing=False)
    out = {"action_id":action_id,"review_sha256":expected,"ticket_id":action["ticket_id"],"writes":0}
    if not directory.exists():
        return {**out,"status":"unattempted"}
    with store.projection_lock(directory / "lock-marker"):
        path = cx.local(root,f".atelier/tracker-sync/{sha(effect)}.json",existing=False)
        if not path.exists():
            return {**out,"status":"unattempted"}
        ledger = read_operation(root,path)
        cx.require(ledger["effect"]==effect and ledger["approved_sha256"]==expected,
                   "use the original approval to reconcile this journal")
        pin = obj["pins"]["config"]
        config_bytes = cx.bound_bytes(root,pin["path"])
        cx.require(cx.digest(config_bytes)==pin["sha256"],"restore the exact reviewed provider config for reconciliation")
        cfg = cx.json_object(config_bytes)
        cx.require(cfg["provider"]==obj["provider"] and cfg["container"]["id"]==obj["container_id"],"approval refers to another provider")
        client = factory(cfg)
        mapping = ledger["mapping_at_attempt"]
        try:
            container=exact_container(client,cfg)
            status,suggestion=reconcile(client,action,mapping,container)
        except ProviderError as exc:
            return {**out,"status":"pending","reason":exc.code,"requests":list(client.receipts)}
        if status=="observed":
            if ledger["status"]!="observed":
                save(path,{**ledger,"status":"observed","mapping_candidate":suggestion},True)
        elif ledger["status"]=="observed":
            status="post-observation-drift"
        elif ledger["status"]=="rejected":
            status="rejected"
        elif status=="not-observed":
            status="pending"
        return {**out,"status":status,"mapping_candidate":suggestion,"requests":list(client.receipts),
                "mapping_candidate_requires_current_local_review":True}


def execute(root, preview_path, expected, action_id, factory, *, apply=False, retry_rejected=False):
    from tracker_providers import ProviderError
    raw = cx.bound_bytes(root,preview_path)
    cx.require(cx.digest(raw)==check_id(expected),"not the exact approved tracker preview")
    obj = cx.json_object(raw)
    cx.require(obj.get("schema_version")==PREVIEW and obj.get("checkout_sha256")==cx.digest(os.fsencode(root)),
               "tracker approval belongs to another checkout or schema")
    action_id = check_id(action_id)
    if not apply:
        return read_back(root,obj,expected,action_id,factory)
    paths = [obj["pins"][n]["path"] for n in ("projection","config","mapping")]
    snap,board,cfg,statuses,local,mapping,pins = snapshot_local(root,*paths)
    cx.require(pins==obj["pins"] and board["project_id"]==obj["project_id"]
               and cfg["provider"]==obj["provider"] and cfg["container"]["id"]==obj["container_id"],"local state changed; refresh the preview")
    client = factory(cfg)
    cx.require(sorted(client.capabilities)==obj["capabilities"],"provider capabilities changed")
    remote = check_remote_set(obj["observed"],obj["container_id"])
    actions,_,_ = make_actions(board,cfg,statuses,local,mapping,remote,obj["capabilities"])
    cx.require(action_id in actions and obj["actions"]==actions,"action is not a canonical member of the approved preview")
    action = actions[action_id]
    out = {"action_id":action_id,"review_sha256":expected,"provider":obj["provider"],"container_id":obj["container_id"],
           "ticket_id":action["ticket_id"],"writes":0}
    directory = cx.local(root,".atelier/tracker-sync",existing=False)
    directory.parent.mkdir(mode=0o700,exist_ok=True)
    directory.mkdir(mode=0o700,exist_ok=True)
    fsync(root)
    fsync(directory.parent)
    with store.projection_lock(directory / "lock-marker"):
        # Action identity is stable across regenerated previews of the same change.
        # A different local approval cannot replay a pending write.
        effect = effect_for(obj,action)
        path = cx.local(root,f".atelier/tracker-sync/{sha(effect)}.json",existing=False)
        prior = path.exists()
        if prior:
            ledger = read_operation(root,path)
            cx.require(ledger["effect"]==effect,"tracker journal effect mismatch")
        else:
            blocked_by = other_pending(root,directory,effect)
            if blocked_by is not None:
                return {**out,"status":"previous-effect-pending","blocking_journal":blocked_by}
            ledger = {"schema_version":LEDGER,"effect":effect,"checkout_sha256":obj["checkout_sha256"],
                      "approved_sha256":expected,"mapping_at_attempt":mapping,
                      "prior_rejections":[]}
        retry = bool(retry_rejected and prior and ledger["status"]=="rejected" and ledger["approved_sha256"]!=expected)
        if retry_rejected and not retry:
            return {**out,"status":"retry-needs-definite-rejection-and-fresh-exact-preview"}
        snap.verify_unchanged()
        try:
            container = exact_container(client,cfg)
            status,suggestion = reconcile(client,action,mapping,container)
        except ProviderError as exc:
            return {**out,"status":"pending" if prior else "blocked","reason":exc.code,"requests":list(client.receipts)}
        if status == "observed":
            changed = ledger.get("status") != "observed"
            if changed:
                save(path,{**ledger,"status":"observed","mapping_candidate":suggestion},prior)
            return {**out,"status":"observed","mapping_candidate":suggestion,"requests":list(client.receipts)}
        if (prior and not retry) or status != "not-observed":
            current = ("post-observation-drift" if prior and ledger["status"]=="observed"
                       else "rejected" if prior and ledger["status"]=="rejected"
                       else "pending" if prior and status=="not-observed" else status)
            return {**out,"status":current,"requests":list(client.receipts)}
        if not getattr(client,"authenticated",True):
            return {**out,"status":"write-authentication-required","requests":list(client.receipts)}
        if retry:
            pending = other_pending(root,directory,effect)
            if pending:
                return {**out,"status":"previous-effect-pending","blocking_journal":pending}
            rejected = ledger.get("prior_rejections",[])
            cx.require(isinstance(rejected,list) and len(rejected)<10,"rejected-attempt history needs operator review")
            ledger = {**ledger,"approved_sha256":expected,"mapping_at_attempt":mapping,
                      "prior_rejections":[*rejected,{"approval":ledger["approved_sha256"],"reason":ledger["reason"]}]}
            ledger.pop("reason",None)
        if action.get("field") in ("parent_id","blocker_ids"):
            related = action["desired"]
            if related:
                keys = {x["id"]:x["key"] for x in mapping.values()}
                for rid in related if isinstance(related,list) else [related]:
                    item = safe_item(client.read_item(rid,keys[rid]),container)
                    cx.require(item["id"]==rid and item["key"]==keys[rid],"related item identity changed")
        current = None
        if action["operation"]=="update":
            target = action["target"]
            current = client.read_item(target["id"],target["key"])
            observed = safe_item(current,container)
            cx.require(all(observed[k]==v for k,v in target.items())
                       and action["field"] in observed and observed[action["field"]]==action["before"],
                       "approved value changed immediately before dispatch")
        snap.verify_unchanged()
        ledger = {**ledger,"status":"attempting"}
        save(path,ledger,prior)
        out["writes"] = 1
        try:
            if action["operation"]=="create":
                client.create_item(action["desired"])
            else:
                client.update_item(current,{action["field"]:action["desired"]})
        except ProviderError as exc:
            if not exc.uncertain:
                save(path,{**ledger,"status":"rejected","reason":exc.code},True)
                return {**out,"status":"rejected","reason":exc.code,"requests":list(client.receipts)}
        try:
            status,suggestion=reconcile(client,action,mapping,container)
        except ProviderError as exc:
            return {**out,"status":"pending","reason":exc.code,"requests":list(client.receipts)}
        if status=="observed":
            save(path,{**ledger,"status":"observed","mapping_candidate":suggestion},True)
        return {**out,"status":"pending" if status=="not-observed" else status,
                "mapping_candidate":suggestion,"requests":list(client.receipts)}


def main():
    from tracker_providers import ProviderError, build_provider
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="mode",required=True)
    for mode in ("preview","apply","read-back"):
        command = subs.add_parser(mode)
        command.add_argument("--root",type=Path,required=True)
        if mode=="preview":
            for p in ("projection","config","mapping"):
                command.add_argument("--"+p,required=True)
        else:
            for p in ("preview","sha256","action"):
                command.add_argument("--"+p,required=True)
            if mode=="apply":
                command.add_argument("--retry-rejected",action="store_true")
    args=parser.parse_args()
    try:
        root=args.root.resolve(strict=True)
        if args.mode=="preview":
            result=preview(root,args.projection,args.config,args.mapping,build_provider)
        else:
            result=execute(root,args.preview,args.sha256,args.action,build_provider,apply=args.mode=="apply",
                           retry_rejected=getattr(args,"retry_rejected",False))
        print(encoded(result).decode(),end="")
        return 0 if args.mode=="preview" or result["status"]=="observed" else 2
    except ProviderError as exc:
        print(json.dumps({"status":"blocked","reason":exc.code}),file=sys.stderr)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)}),file=sys.stderr)
    return 2


if __name__=="__main__":
    sys.exit(main())
