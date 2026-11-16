#!/usr/bin/env python3
"""Build the current illustrated showcase as HTML, PDF and an offline ZIP."""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSETS = ROOT / "assets/marketing/current"
CONCEPT_ART = ROOT / "assets/marketing/concepts"
SITE = "https://github.com/alex-hohaizel/codex-agents"
SHOWCASE_RUNS = f"{SITE}/actions/workflows/validate.yml?query=branch%3Amain"
SECTIONS = {"install", "first-task", "workflow", "retrieval", "evals", "workbench", "operations", "catalog"}
ASSET_NAMES = ("overview", "product", "game", "conversation", "operations", "documents", "specialists",
               "retrieval", "evaluation", "workbench")
MORE_CONCEPTS = ("lifecycle", "continuity", "next-task")
CONCEPT_NAMES = (*ASSET_NAMES[:7], *MORE_CONCEPTS)
RAG = "docs/OPERATING_MODEL.md#retrieval-and-rag"
EVALS = "docs/OPERATING_MODEL.md#evals-and-evidence"
DETAILS = {
    "operations": ("docs/OPERATING_MODEL.md#tools-evidence-and-recovery", "engineering"),
    "retrieval": ("docs/technical/RETRIEVAL.md", "worked_retrieval"),
    "evaluation": (EVALS, "engineering"),
    "continuity": ("docs/OPERATING_MODEL.md#project-context-and-handoffs", "engineering"),
    "workbench": ("apps/agent-atelier/README.md", "engineering"),
}
CSS = """*{box-sizing:border-box}html{color-scheme:dark;scroll-behavior:smooth}body{margin:0;
background:#061922;color:#f6eedc;font:1rem/1.58 system-ui,sans-serif}a{color:#77f4de}
a:focus-visible{outline:3px solid #ffce6d;outline-offset:4px}
header,main,footer{max-width:72rem;margin:auto;padding:1.5rem clamp(1rem,5vw,4rem)}
header{border-bottom:1px solid #315562}header>a{font-weight:700}
nav{display:flex;flex-wrap:wrap;gap:.4rem 1rem;padding-top:.6rem}
nav a[aria-current=page]{color:#f6eedc;font-weight:700}
.skip{position:absolute;left:1rem;top:-10rem}.skip:focus{top:1rem;background:#102c36;padding:.8rem}
h1,h2{font-family:Georgia,serif;line-height:1.14}h1{font-size:clamp(2.45rem,7vw,5rem);
max-width:14ch;margin:.7rem 0 1.2rem}h2{font-size:clamp(1.75rem,4vw,2.8rem);margin:.5rem 0 1rem}
p{max-width:64ch}img{display:block;width:100%;height:auto;border-radius:.5rem}
figure{margin:0}figcaption{margin:1rem 0 0}.scene-label{font-size:.95rem;color:#bed5d7;margin:.5rem 0}
details{margin:1.15rem 0}summary{cursor:pointer;font-weight:700;color:#77f4de}
details[open] summary{margin-bottom:.7rem}details figure{max-width:50rem}
.actions{display:flex;flex-wrap:wrap;gap:.6rem 1rem;list-style:none;padding:0}
.actions a{display:inline-block;border:1px solid #58e6d3;border-radius:.4rem;padding:.45rem .8rem}
.sections{padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:.3rem 1rem}
.exhibits{display:grid;gap:2.5rem;margin:2rem 0}
.exhibits section{border-top:1px solid #315562;padding-top:.9rem;min-width:0}.intro{color:#bed5d7}
.diagram{max-width:50rem}.diagram img{width:100%}
footer{border-top:1px solid #315562}
@media(max-width:43rem){.exhibits{grid-template-columns:1fr;gap:2rem}}
@media print{html{color-scheme:light}body{color:#102c36;background:#fff}nav,.actions,footer,.skip{display:none}
.exhibits{display:block}.exhibits section{break-inside:avoid}a{color:#102c36}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}"""


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def asset_records():
    from PIL import Image, ImageChops

    from render_boards import BOARDS

    result = {}
    expected = {f"{name}.png" for name in ASSET_NAMES}
    seen = {path.name for path in ASSETS.iterdir() if path.is_file()}
    if seen != expected:
        raise ValueError("The showcase must contain exactly the declared cover and diagrams")
    for identifier in ASSET_NAMES:
        path = ASSETS / f"{identifier}.png"
        with Image.open(path) as image:
            width, height = image.size
            if image.format != "PNG" or width < 900 or not 1.73 <= width / height <= 1.82:
                raise ValueError(f"Unexpected visual source dimensions or format: {path.name}")
            image.verify()
        if identifier in BOARDS:
            with Image.open(path) as image:
                produced = BOARDS[identifier]().image
                if produced.size != image.size or ImageChops.difference(produced, image.convert("RGB")).getbbox():
                    raise ValueError(f"Generated diagram differs from its drawing source: {path.name}")
        original = path.read_bytes()
        result[identifier] = {"file": path.name, "width": width, "height": height,
                              "sha256": sha256(original).hexdigest()}
    return result


def read_concepts():
    from PIL import Image

    provenance = read_json(HERE / "concept-art.json")
    reference = provenance["source_commit"]
    if (len(reference) != 40 or any(char not in "0123456789abcdef" for char in reference)
            or tuple(provenance["languages"]) != ("en", "uk")):
        raise ValueError("Concept art needs an exact source commit and both original languages")
    for language, group in provenance["languages"].items():
        directory = CONCEPT_ART / language
        if tuple(group) != CONCEPT_NAMES or set(directory.iterdir()) != {directory / f"{key}.webp" for key in group}:
            raise ValueError(f"Unexpected concept-art inventory: {language}")
        for identifier, plate in group.items():
            expected_path = f"assets/marketing/campaign/{language}/"
            if (plate["file"] != f"{identifier}.webp" or not plate["master_path"].startswith(expected_path)
                    or Path(plate["master_path"]).parent.as_posix() != expected_path.rstrip("/")):
                raise ValueError(f"Unbound concept-art source: {language}/{identifier}")
            path = directory / plate["file"]
            with Image.open(path) as image:
                if (image.format != "WEBP" or image.size != (plate["width"], plate["height"])
                        or sha256(image.convert("RGB").tobytes()).hexdigest() != plate["rgb_sha256"]):
                    raise ValueError(f"Concept art differs from its original pixels: {language}/{identifier}")
            if sha256(path.read_bytes()).hexdigest() != plate["sha256"]:
                raise ValueError(f"Concept art differs from its delivery digest: {language}/{identifier}")
    return provenance


def repo_link(path, medium, *, depth="../../"):
    if medium == "github":
        return depth + path
    return f"{SITE}/blob/main/{path}"


def concept_plate(concepts, identifier, locale):
    language = "uk" if locale == "uk" else "en"
    return language, concepts["languages"][language][identifier]


def master_url(concepts, plate):
    return f'{SITE}/blob/{concepts["source_commit"]}/{plate["master_path"]}'


def campaign_pdf(concepts, locale):
    language = "uk" if locale == "uk" else "en"
    return f'{SITE}/blob/{concepts["source_commit"]}/marketing/campaign/pdf/Campaign.{language}.pdf'


def handbook_link(locale, section, *, medium):
    if medium == "github":
        return f"../../docs/{locale}/GUIDE.md#{section}"
    return f"{SITE}/blob/main/docs/{locale}/GUIDE.md#{section}"


def html_locale(books, record, concepts, locale, *, embedded=False):
    book = books[locale]
    e = escape
    source = "art/" if embedded else "../../assets/marketing/current/"
    medium = "html"
    actions = [
        (handbook_link(locale, "install", medium=medium), book["guide"]),
        (repo_link(RAG, medium), f'{book["cards"][7]["title"]} (RAG)'),
        (repo_link(EVALS, medium), book["cards"][8]["title"]),
        ("Showcase.pdf", book["pdf"]),
        (repo_link("README.md", medium), book["home"]),
    ]
    offline_help = ""
    if not embedded:
        actions.append((SHOWCASE_RUNS, book["offline"]))
        offline_help = f'<p>{e(book["offline_help"])}</p>'
    sections = []
    concepts_source = "art/concepts/" if embedded else "../../assets/marketing/concepts/"

    def concept_html(card, loading):
        language, plate = concept_plate(concepts, card["id"], locale)
        source_url = f'{concepts_source}{language}/{plate["file"]}'
        language_label = book["ukrainian_art"] if language == "uk" else book["english_art"]
        text_alt = card.get("concept_alt", card["alt"])
        return (
            f'<p class="scene-label">{e(book["concept_label"])} · {e(language_label)}</p><figure>'
            f'<a href="{source_url}" aria-label="{e(book["full_art"], quote=True)}">'
            f'<img src="{source_url}" width="{plate["width"]}" height="{plate["height"]}" loading="{loading}" '
            f'alt="{e(text_alt, quote=True)}"></a><figcaption>{e(text_alt)}</figcaption></figure>'
        )

    def workflow_html(card):
        url = handbook_link(locale, card["section"], medium=medium)
        links = [f'<a href="{url}">{e(book["view"])}</a>']
        if card["id"] in DETAILS:
            detail, label = DETAILS[card["id"]]
            links.append(f'<a href="{repo_link(detail, medium)}">{e(book[label])}</a>')
        return f'<p>{" · ".join(links)}</p>'

    for index, card in enumerate(book["cards"]):
        identifier = card["id"]
        art = record[identifier]
        loading = "eager" if index == 0 else "lazy"
        diagram = (
            f'<figure class="diagram">'
            f'<img src="{source}{art["file"]}" width="{art["width"]}" height="{art["height"]}" '
            f'loading="{loading}" alt="{e(card["alt"], quote=True)}"><figcaption>{e(card["caption"])}'
            "</figcaption></figure>"
        )
        figures = diagram
        if identifier in CONCEPT_NAMES:
            disclosure = book["alternate_cover"] if identifier == "overview" else book["technical"]
            figures = (concept_html(card, loading) + f'<details><summary>{e(disclosure)}</summary>'
                       f"{diagram}</details>")
        sections.append(
            f'<section id="{identifier}"><h2>{e(card["title"])}</h2>{figures}'
            f'{workflow_html(card)}</section>'
        )
    sections.append(f'<h2>{e(book["more_concepts"])}</h2>')
    for card in book["more"]:
        identifier = card["id"]
        sections.append(
            f'<section id="{identifier}"><h2>{e(card["title"])}</h2>{concept_html(card, "lazy")}'
            f'{workflow_html(card)}</section>'
        )
    active = ' aria-current="page"'
    nav = "".join(
        f'<a href="{code}.html" hreflang="{code}" lang="{code}"'
        f'{active if code == locale else ""}>{e(other["label"])}</a>'
        for code, other in books.items()
    )
    top = "".join(f'<li><a href="{url}">{e(label)}</a></li>' for url, label in actions)
    jumps = "".join(f'<li><a href="#{card["id"]}">{e(card["title"])}</a></li>'
                    for card in [*book["cards"], *book["more"]])
    return (
        f'<!doctype html><html lang="{locale}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{e(book["title"])} | Codex Agent System</title><style>{CSS}</style></head>'
        f'<body><a class="skip" href="#showcase">{e(book["title"])}</a><header>'
        f'<a href="index.html">Codex Agent System</a><nav aria-label="{e(book["choose"], quote=True)}">'
        f'{nav}</nav></header><main id="showcase"><h1>{e(book["title"])}</h1>'
        f'<p class="intro">{e(book["intro"])}</p><ul class="actions">{top}</ul>'
        f'<ul class="sections">{jumps}</ul><p>{e(book["concept_note"])}</p>{offline_help}'
        f'<div class="exhibits">{"".join(sections)}</div></main></body></html>\n'
    ).encode()


def html_index(books):
    links = "".join(
        f'<li><a href="{code}.html" hreflang="{code}" lang="{code}">{escape(book["label"])}</a></li>'
        for code, book in books.items()
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Codex Agent System | Showcase</title><style>{CSS}</style></head>'
        '<body><main><h1>Codex Agent System</h1><p>Choose a language to explore the illustrated '
        f'workflows.</p><ul class="actions">{links}</ul></main></body></html>\n'
    ).encode()


def markdown_locale(books, concepts, locale):
    book = books[locale]
    listing = " · ".join(f'[{other["label"]}](../{code}/README.md)' for code, other in books.items())
    guide = handbook_link(locale, "install", medium="github")
    lines = [
        f'# {book["title"]}', "", listing, "", book["intro"], "",
        f'[{book["guide"]}]({guide}) · [{book["pdf"]}](../campaign/Showcase.pdf) · '
        f'[{book["offline"]}]({SHOWCASE_RUNS})', "", book["offline_help"], "",
        f'[RAG]({repo_link(RAG, "github")}) · [Evals]({repo_link(EVALS, "github")}) · '
        f'[{book["home"]}](../../README.md)', "",
        " · ".join(f'[{card["title"]}](#{heading_id(card["id"])})' for card in book["cards"]), "",
        book["concept_note"], "",
    ]

    def concept_markdown(card):
        language, plate = concept_plate(concepts, card["id"], locale)
        artwork = f'../../assets/marketing/concepts/{language}/{plate["file"]}'
        text_alt = card.get("concept_alt", card["alt"])
        language_label = book["ukrainian_art"] if language == "uk" else book["english_art"]
        return [
            f'**{book["concept_label"]}** · {language_label}', "",
            f'[![{text_alt}]({artwork})]({artwork})', "", text_alt, "",
            f'[{book["full_art"]}]({master_url(concepts, plate)})', "",
        ]

    def workflow_markdown(card):
        url = handbook_link(locale, card["section"], medium="github")
        links = [f'[{book["view"]}]({url})']
        if card["id"] in DETAILS:
            target, label = DETAILS[card["id"]]
            links.append(f'[{book[label]}]({repo_link(target, "github")})')
        return [" · ".join(links), ""]

    for card in book["cards"]:
        identifier = card["id"]
        lines += [f'<a id="{heading_id(identifier)}"></a>', f'## {card["title"]}', ""]
        diagram = [
            f'![{card["alt"]}](../../assets/marketing/current/{identifier}.png)', "",
            card["caption"], "",
        ]
        if identifier in CONCEPT_NAMES:
            disclosure = book["alternate_cover"] if identifier == "overview" else book["technical"]
            lines += concept_markdown(card) + [
                "<details>", f'<summary>{escape(disclosure)}</summary>', "",
                *diagram, "</details>", "",
            ]
        else:
            lines += diagram
        lines += workflow_markdown(card)
    lines += [f'## {book["more_concepts"]}', ""]
    for card in book["more"]:
        lines += [f'### {card["title"]}', "", *concept_markdown(card), *workflow_markdown(card)]
    return "\n".join(lines).encode()


def heading_id(identifier):
    return f"showcase-{identifier}"


def marketing_index(books, concepts):
    choices = " · ".join(f'[{book["label"]}]({code}/README.md)' for code, book in books.items())
    b = books["en"]
    return (
        "# Codex Agent System showcase\n\n"
        f"{choices}\n\n"
        f"{b['intro']}\n\n"
        "[My Day](en/README.md#showcase-product) · [Global Logistics](en/README.md#showcase-operations) · "
        "[Game studio](en/README.md#showcase-game) · [Assistant](en/README.md#showcase-conversation) · "
        f"[RAG](../{RAG}) · [Evals](../{EVALS})\n\n"
        f"![{b['cards'][0]['concept_alt']}](../assets/marketing/concepts/en/overview.webp)\n\n"
        f"{b['concept_note']} Open a scenario for its full product concept and technical workflow.\n\n"
        "[Repository home](../README.md) · [Read the user guide](../docs/en/GUIDE.md) · "
        "[Technical diagrams PDF](campaign/Showcase.pdf)\n\n"
        f"[Original campaign PDF in English]({campaign_pdf(concepts, 'en')}) · "
        f"[Оригінал кампанії українською у PDF]({campaign_pdf(concepts, 'uk')})\n\n"
        "For offline viewing, open `marketing/campaign/index.html` from a checkout of `main`. "
        "The standalone download contains all seven language editions and their shared artwork. "
        f"{b['offline_help']} [Validation runs for main]({SHOWCASE_RUNS})\n"
    ).encode()


def markdown_files(books, concepts):
    return {ROOT / "marketing/README.md": marketing_index(books, concepts)} | {
        ROOT / f"marketing/{locale}/README.md": markdown_locale(books, concepts, locale) for locale in books
    }


def load(*, refresh=False):
    books = read_json(HERE / "catalog.json")
    locales = read_json(ROOT / "locales.json")["locales"]
    if tuple(books) != tuple(entry["code"] for entry in locales):
        raise ValueError("Showcase language inventory differs from advertised documentation")
    for locale, book in books.items():
        if tuple(card["id"] for card in book["cards"]) != ASSET_NAMES:
            raise ValueError(f"Unexpected exhibit inventory: {locale}")
        labels = ("label", "title", "intro", "guide", "view", "pdf", "offline", "choose", "offline_help",
                  "concept_note", "concept_label", "english_art", "ukrainian_art", "full_art", "technical",
                  "more_concepts", "home", "engineering", "alternate_cover", "worked_retrieval")
        if any(not book[key].strip() for key in labels):
            raise ValueError(f"Incomplete showcase copy: {locale}")
        if any(not all(card[key].strip() for key in ("title", "alt", "caption")) or card["section"] not in SECTIONS
               for card in book["cards"]):
            raise ValueError(f"Incomplete or unbound exhibit copy: {locale}")
        if (any(not card["concept_alt"].strip() for card in book["cards"][:7])
                or tuple(card["id"] for card in book["more"]) != MORE_CONCEPTS
                or any(not card["title"].strip() or not card["alt"].strip() or card["section"] not in SECTIONS
                       for card in book["more"])):
            raise ValueError(f"Incomplete concept-art descriptions: {locale}")
    assets = asset_records()
    if assets != read_json(HERE / "artwork.json")["assets"]:
        raise ValueError("An artwork source differs from its recorded digest")
    concepts = read_concepts()
    for path, content in markdown_files(books, concepts).items():
        if refresh:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        elif not path.is_file() or path.read_bytes() != content:
            raise ValueError(f"Generated Markdown is stale: {path.relative_to(ROOT)}")
    return books, assets, concepts


def pdf_bytes(record):
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    output = BytesIO()
    doc = canvas.Canvas(output, pagesize=(960, 540), invariant=1, pageCompression=1)
    doc.setTitle("Codex Agent System | Illustrated showcase")
    doc.setAuthor("Codex Agent System")
    for art in record.values():
        width, height = art["width"], art["height"]
        scale = min(960 / width, 540 / height)
        w, h = width * scale, height * scale
        doc.setFillColorRGB(.027, .098, .129)
        doc.rect(0, 0, 960, 540, fill=1, stroke=0)
        doc.drawImage(ImageReader(str(ASSETS / art["file"])), (960 - w) / 2, (540 - h) / 2, w, h)
        doc.showPage()
    doc.save()
    return output.getvalue()


def offline_zip(books, record, concepts, pdf):
    files = {"index.html": html_index(books), "Showcase.pdf": pdf}
    files.update({f"{locale}.html": html_locale(books, record, concepts, locale, embedded=True) for locale in books})
    files.update({f'art/{art["file"]}': (ASSETS / art["file"]).read_bytes() for art in record.values()})
    for language, group in concepts["languages"].items():
        files.update({f'art/concepts/{language}/{plate["file"]}':
                      (CONCEPT_ART / language / plate["file"]).read_bytes() for plate in group.values()})
    contents = BytesIO()
    with ZipFile(contents, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, value in sorted(files.items()):
            info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, value, compresslevel=9)
    return contents.getvalue()


def manifest(files, books, assets, concepts):
    return encode_json({
        "schema": "codex-agents.showcase-export/1",
        "languages": list(books),
        "artworks": assets,
        "concept_art": concepts,
        "files": [{"path": name, "sha256": sha256(value).hexdigest(), "size": len(value)}
                  for name, value in sorted(files.items())],
    })


def outputs(books, assets, concepts, *, offline=False):
    pdf = pdf_bytes(assets)
    if offline:
        files = {"Showcase.zip": offline_zip(books, assets, concepts, pdf), "Showcase.pdf": pdf}
    else:
        files = {"index.html": html_index(books), "Showcase.pdf": pdf}
        files.update({f"{locale}.html": html_locale(books, assets, concepts, locale) for locale in books})
    return files | {"exports.json": manifest(files, books, assets, concepts)}


def verify_pdf(pdf, assets):
    from PIL import Image, ImageChops
    from pypdf import PdfReader

    pages = PdfReader(BytesIO(pdf)).pages
    if len(pages) != len(assets):
        raise ValueError("PDF page count differs from the illustration inventory")
    for page, item in zip(pages, assets.values()):
        if len(page.images) != 1 or tuple(page.mediabox)[2:] != (960, 540):
            raise ValueError("PDF page does not contain exactly one illustration")
        with Image.open(ASSETS / item["file"]) as original:
            rendered = page.images[0].image.convert("RGB")
            if rendered.size != original.size or ImageChops.difference(rendered, original.convert("RGB")).getbbox():
                raise ValueError(f'The PDF changed illustration pixels: {item["file"]}')


def write_or_check(directory, files, *, check):
    if not check:
        directory.mkdir(parents=True, exist_ok=True)
    for name, value in files.items():
        path = directory / name
        if check:
            if not path.is_file() or path.read_bytes() != value:
                raise ValueError(f"Generated showcase file differs: {path}")
        else:
            path.write_bytes(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE)
    parser.add_argument("--artifacts-output", type=Path)
    command = parser.add_mutually_exclusive_group()
    command.add_argument("--check-source", action="store_true")
    command.add_argument("--check", "--verify", action="store_true")
    command.add_argument("--export", action="store_true", help="Generate the current showcase (default)")
    command.add_argument("--refresh-markdown", action="store_true", help="Refresh GitHub-native locale pages")
    args = parser.parse_args()
    try:
        if args.artifacts_output and args.artifacts_output.resolve() == args.output.resolve():
            raise ValueError("Set separate directories for repository exports and the offline archive")
        books, assets, concepts = load(refresh=args.refresh_markdown)
        if not (args.check_source or args.refresh_markdown):
            site = outputs(books, assets, concepts)
            if args.check:
                verify_pdf(site["Showcase.pdf"], assets)
            write_or_check(args.output, site, check=args.check)
            if args.artifacts_output:
                write_or_check(args.artifacts_output, outputs(books, assets, concepts, offline=True), check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "locales": list(books), "illustrations": len(assets),
                      "concept_plates": sum(len(group) for group in concepts["languages"].values())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
