"""Render reviewed document data to editable Markdown and safe offline HTML."""

from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit

from ticket_tree import context

TICKS = chr(96) * 3
SAFE_ELEMENTS = set("""
html head body meta title style main header footer article section aside div p h1 h2 h3 h4
h5 h6 blockquote ul ol li table caption thead tbody tr th td span strong em small
code pre hr br figure figcaption nav details summary
""".split())
SAFE_ATTRIBUTES = set("""
class id lang title role aria-label aria-labelledby aria-describedby charset name content
data-field data-section data-body data-rest hidden open
""".split())
VOID = {"meta", "hr", "br"}
COMMON_CSS = """
:root{color-scheme:light;font-family:system-ui,sans-serif;color:#172b37;background:#eff4f4}
body{margin:0}main{max-width:70ch;margin:0 auto;padding:clamp(1.2rem,5vw,3.8rem)}
h1{font-size:clamp(1.9rem,4vw,3.4rem);line-height:1.05;margin:.65rem 0;color:#132e39}
h2{margin:2rem 0 .65rem;border-top:1px solid #9db0b7;padding-top:.85rem;line-height:1.2}
p,li{line-height:1.6;overflow-wrap:anywhere}a{color:#075f76;text-decoration:underline}
a:focus-visible{outline:2px solid #a84223;outline-offset:4px}
.meta{font-size:.9rem;color:#38545f}.card{background:#fff;border-radius:.45rem;padding:1rem 1.25rem}
pre{background:#e2ecee;padding:.8rem;white-space:pre-wrap;overflow-wrap:anywhere}
table{width:100%;border-collapse:collapse}th,td{border:1px solid #b3c1c6;text-align:left;padding:.45rem}
figure{margin:1rem 0}figcaption{font-size:.88rem}.provenance{font-size:.88rem;margin-top:.6rem}
@media print{:root{background:#fff}main{padding:0}h2{break-after:avoid}.slide{break-after:page}}
"""
CSP = ("<meta http-equiv=\"Content-Security-Policy\" "
       "content=\"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'\">")
INLINE = re.compile(r"(`[^`\n]+`|\*\*[^*\n]+\*\*|\*[^*\n]+\*|\[[^\]\n]+\]\([^()\s]+\))")
FENCE = re.compile(r"^(?:`{3,}|~{3,})\s*([a-zA-Z0-9_+-]*)\s*$")
LIST = re.compile(r"^\s{0,3}(?:([-*+])|([0-9]+)[.)])[ \t]+(.+)$")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")


def safe_css(css):
    context.require(not re.search(r"\\|</|@import|\b(?:url|image-set|expression)\s*\(", css, re.I),
                    "CSS view must be entirely local and contain no active or fetched content")
    return css


def safe_url(value):
    if value.startswith("#") and re.fullmatch(r"#[\w-]+", value):
        return True
    if re.fullmatch(r"[A-Za-z0-9_][\w.-]*[.]md", value):
        return True
    try:
        parts = urlsplit(value)
        return parts.scheme in ("https", "http") and bool(parts.hostname) and not parts.username
    except ValueError:
        return False


def inline(text):
    output = []
    for chunk in INLINE.split(text):
        if chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 4:
            output.append("<strong>" + escape(chunk[2:-2]) + "</strong>")
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            output.append("<em>" + escape(chunk[1:-1]) + "</em>")
        elif chunk.startswith("`") and chunk.endswith("`") and len(chunk) > 2:
            output.append("<code>" + escape(chunk[1:-1]) + "</code>")
        elif chunk.startswith("[") and "](" in chunk and chunk.endswith(")"):
            label, url = chunk[1:-1].split("](", 1)
            if safe_url(url):
                output.append(f'<a href="{escape(url, quote=True)}" rel="noreferrer">{escape(label)}</a>')
            else:
                output.append(escape(chunk))
        else:
            output.append(escape(chunk))
    return "".join(output)


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_divider(line):
    return "|" in line and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells(line))


def blocks(text):
    """Render practical Markdown without sending the source to a browser parser."""
    result, paragraph = [], []
    lines, index = text.splitlines(), 0

    def flush():
        if paragraph:
            result.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        code, heading, bullet = FENCE.fullmatch(line), HEADING.fullmatch(line), LIST.fullmatch(line)
        if code:
            flush()
            marker = line.lstrip()[0]
            content = []
            index += 1
            while index < len(lines):
                closing = FENCE.fullmatch(lines[index])
                if closing and not closing[1] and lines[index].startswith(marker):
                    break
                content.append(lines[index])
                index += 1
            safe = "<pre><code>" + escape("\n".join(content)) + "</code></pre>"
            result.append("<figure><figcaption>Mermaid diagram source</figcaption>" + safe + "</figure>"
                          if code[1].lower() == "mermaid" else safe)
        elif heading:
            flush()
            level = max(3, len(heading[1]))
            result.append(f"<h{level}>" + inline(heading[2]) + f"</h{level}>")
        elif bullet:
            flush()
            tag = "ul" if bullet[1] else "ol"
            items = []
            while index < len(lines):
                match = LIST.fullmatch(lines[index])
                if not match or ("ul" if match[1] else "ol") != tag:
                    break
                items.append("<li>" + inline(match[3]) + "</li>")
                index += 1
            result.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        elif "|" in line and index + 1 < len(lines) and table_divider(lines[index + 1]):
            flush()
            columns = "".join('<th scope="col">' + inline(cell) + "</th>" for cell in cells(line))
            items = []
            index += 2
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                items.append("<tr>" + "".join("<td>" + inline(cell) + "</td>" for cell in cells(lines[index])) + "</tr>")
                index += 1
            table = "<table><thead><tr>" + columns + "</tr></thead><tbody>"
            result.append(table + "".join(items) + "</tbody></table>")
            continue
        elif line.startswith("> "):
            flush()
            result.append("<blockquote>" + inline(line[2:]) + "</blockquote>")
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
        index += 1
    flush()
    return "\n".join(result)


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


class SafeLayout(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        context.require(tag in SAFE_ELEMENTS, f"unsupported element in HTML view: {tag}")
        properties = dict(attrs)
        context.require(len(properties) == len(attrs) and set(properties) <= SAFE_ATTRIBUTES,
                        f"unsupported or duplicate attribute in HTML view: {tag}")
        context.require(tag != "meta" or properties.get("name", "") in ("", "viewport", "description"),
                        "unsupported HTML view metadata")
        markers = set(properties) & {"data-field", "data-section", "data-body", "data-rest"}
        context.require(len(markers) <= 1 and (not markers or tag not in VOID | {"style", "head", "html", "body"}),
                        "invalid HTML slot")
        node = Element(tag, properties)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        context.require(len(self.stack) > 1 and self.stack[-1].tag == tag,
                        f"unpaired HTML view tag: {tag}")
        self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def handle_decl(self, decl):
        context.require(decl.lower() == "doctype html", "unsupported HTML declaration")

    def handle_pi(self, data):
        context.require(False, "HTML processing instructions are unsupported")

    def parse(self, text):
        self.feed(text)
        self.close()
        context.require(len(self.stack) == 1, "incomplete HTML view")
        root = [child for child in self.root.children if isinstance(child, Element)]
        context.require(len(root) == 1 and root[0].tag == "html", "view requires one HTML root")
        groups = [child.tag for child in root[0].children if isinstance(child, Element)]
        context.require(groups == ["head", "body"], "view requires head then body")
        return root[0]


def matching_nodes(node, marker):
    if isinstance(node, Element):
        yield from ((node,) if marker in node.attrs else ())
        for child in node.children:
            yield from matching_nodes(child, marker)


def section_html(section, title=True):
    heading = f'<h2 id="{escape(section["id"], quote=True)}">{escape(section["heading"])}</h2>' if title else ""
    return heading + section["html"]


def fill_layout(layout, sections, fields, override):
    root = SafeLayout().parse(layout)
    by_heading = {section["heading"].casefold(): section for section in sections}
    used_headings = {node.attrs["data-section"].casefold() for node in matching_nodes(root, "data-section")
                     if isinstance(node.attrs["data-section"], str)}
    remainder = [section for section in sections if section["heading"].casefold() not in used_headings]
    has_rest = any(matching_nodes(root, "data-rest"))

    def fill(node, body=None):
        if isinstance(node, str):
            return escape(node)
        attrs, children = node.attrs, node.children
        allowed = {k: v for k, v in attrs.items() if not k.startswith("data-")}
        tag = node.tag
        opening = "<" + tag + "".join(
            f' {k}="{escape(v, quote=True)}"' if v is not None else f" {k}" for k, v in allowed.items()
        ) + ">"
        if tag in VOID:
            return opening
        if "data-field" in attrs:
            value = fields.get(attrs["data-field"], "")
            if not value:
                return ""
            inside = escape(value)
        elif "data-section" in attrs:
            name = attrs["data-section"]
            context.require(isinstance(name, str) and name.strip(), "data-section requires a heading")
            section = by_heading.get(name.casefold())
            if section is None:
                return ""
            slots = list(matching_nodes(node, "data-body"))
            inside = "".join(fill(child, section["html"]) for child in children) if slots else section["html"]
        elif "data-rest" in attrs:
            if not remainder:
                return ""
            inside = "".join(section_html(section) for section in remainder)
        elif "data-body" in attrs:
            context.require(body is not None, "data-body must be inside a matching data-section")
            inside = body
        elif tag == "style":
            context.require(all(isinstance(child, str) for child in children), "invalid style contents")
            inside = safe_css("".join(children))
        else:
            inside = "".join(fill(child, body) for child in children)
        if tag == "head":
            inside = CSP + inside + (f"<style>{override}</style>" if override else "")
        return opening + inside + "</" + tag + ">"

    return "<!doctype html>\n" + fill(root), [sec["id"] for sec in remainder] if not has_rest else []


def item_blocks(items):
    markdown, markup = [], []
    for item in items:
        if "title" in item:
            markdown.append(f'### {item["title"]}')
            markup.append(f'<h3>{escape(item["title"])}</h3>')
        source_markdown = ", ".join(f"`{path}`" for path in item["sources"])
        source_html = ", ".join(f"<code>{escape(path)}</code>" for path in item["sources"])
        markdown += [f'**{item["id"]}**', item["body"], f"Sources: {source_markdown}"]
        markup.append(f'<p><strong>{escape(item["id"])}</strong></p>' + blocks(item["body"]))
        markup.append(f'<p class="provenance">Sources: {source_html}</p>')
    return "\n\n".join(markdown), "\n".join(markup)


def output_sections(record):
    rows = []
    for row in record["template"]["sections"]:
        if row["rule"] == "index":
            rows.append({**row, "markdown": "", "html": ""})
        elif record["sections"][row["id"]]["include"]:
            mdown, markup = item_blocks(record["sections"][row["id"]]["items"])
            rows.append({**row, "markdown": mdown, "html": markup})
    for row in rows:
        if row["rule"] == "index":
            content = [each for each in rows if each["rule"] != "index"]
            row["markdown"] = "\n".join(f'- [{each["heading"]}](#{each["id"]})' for each in content)
            row["html"] = '<nav aria-label="Contents">' + blocks(row["markdown"]) + '</nav>'
    assumptions = record["assumptions"]
    if assumptions:
        markers = [f'[ASSUMPTION: {item["text"]}]' if item["status"] == "open"
                   else f'{item["id"]} · {item["status"]}. {item["resolution"]}' for item in assumptions]
        rows.append({"id": "recorded-assumptions", "heading": "Recorded assumptions",
                     "markdown": "\n".join("- " + marker for marker in markers),
                     "html": blocks("\n".join("- " + marker for marker in markers)), "rule": "notes"})
    return rows


def standard_page(title, revision, sections, slides, override):
    heading = escape(title)
    if slides:
        rows = "".join('<article class="card slide">' + section_html(row) + '</article>'
                       for row in sections if row["rule"] != "index")
    else:
        rows = "".join("<section>" + section_html(row) + "</section>" for row in sections)
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8">{CSP}
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{heading}</title><style>{COMMON_CSS}{override}</style></head>
<body><main><header><p class="meta">Draft · revision {revision}</p><h1>{heading}</h1></header>
{rows}</main></body>
</html>
"""


def build(record, snapshot):
    sections = output_sections(record)
    title = record["title"]
    markdown = [f'# {title}', f'Draft · revision {record["revision"]} · template {record["template"]["template"]} {record["template"]["version"]}']
    markdown.extend(f'## {row["heading"]}\n\n{row["markdown"]}' for row in sections)
    companions = []
    payloads = {}
    for name, row in record["companions"].items():
        if row["include"]:
            mdown, _ = item_blocks(row["items"])
            label = name.removesuffix(".md").replace("-", " ")
            payloads[name] = f'# {title} · {label}\n\n{mdown}\n'.encode("utf-8")
            companions.append(f"- [{label}]({name})")
    if companions:
        markdown.append("## Companion documents\n\n" + "\n".join(companions))
        sections.append({"id": "companion-documents", "heading": "Companion documents", "rule": "notes",
                         "html": blocks("\n".join(companions))})
    omitted = [f'- {ident} · {row["reason"]}' for ident, row in record["sections"].items() if not row["include"]]
    omitted += [f'- {name} · {row["reason"]}' for name, row in record["companions"].items() if not row["include"]]
    if omitted:
        markdown.append("## Omitted sections and companions\n\n" + "\n".join(omitted))
    payloads["document.md"] = ("\n\n".join(markdown) + "\n").encode("utf-8")
    unplaced = []
    if record["render_html"]:
        plan = record["template"]
        assets = plan["resources"]
        css = safe_css(snapshot.read(assets["style"]["path"]).decode("utf-8")) if "style" in assets else ""
        if "view" in assets:
            layout = snapshot.read(assets["view"]["path"]).decode("utf-8")
            fields = {"title": title, "status": "Draft", "updated": f'Revision {record["revision"]}',
                      "id": record["id"], "template": plan["template"], "version": plan["version"]}
            html, unplaced = fill_layout(layout, sections, fields, css)
        else:
            html = standard_page(title, record["revision"], sections, plan["meta"].get("view") == "slides", css)
        payloads["document.html"] = html.encode("utf-8")
    return payloads, unplaced
