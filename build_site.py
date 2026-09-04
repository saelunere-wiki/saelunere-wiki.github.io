#!/usr/bin/env python3
"""
Build a single self-contained HTML campaign site from a folder of Markdown.

Reads `site-content/` (world, characters, npcs, locations, factions, sessions,
story), resolves [[wiki-links]] between pages, computes two-way "Mentioned in"
backlinks, embeds images as base64 and an offline search index, and writes one
file - `campaign_site.html` - with a Saga20-style sidebar, search, and per-entity
pages. No server, no dependencies: double-click to open, zip to share, or upload
the single file to a host later.

Stdlib-only. Run:

    python build_site.py
"""

import base64
import html
import json
import re
from pathlib import Path

import chronicle  # the day-by-day Chronicle component; see chronicle.py

SITE_TITLE = "Saelunere"
SITE_SUBTITLE = "Campaign Wiki"
CONTENT_DIR = "site-content"
OUTPUT_FILE = "campaign_site.html"

# ---- Homepage (shown when you click the title) ----
CAMPAIGN_TAGLINE = "An epic, cosmic saga in a dying, god-touched world."
DM_NAME = "Krimson"
PLAYERS = ["Felix", "Lark", "Billy", "Aeska", "Calder"]
HOME_INTRO = [
    "Saelunere is an orb adrift in an endless void - a world shaped by four gods "
    "and broken when one of them was slain. Twenty-eight years after the Theocide, "
    "the spilled blood of the mother goddess still corrupts the land, and the "
    "survivors cling to seven walled cities beneath a starless dark.",
    "This is the chronicle of the five who will shape what comes next.",
    "- faithfully scribed by Claude, humble keeper of this wiki.",
]

# Sidebar section order + labels. Key = entity `type` (and default folder name).
SECTIONS = [
    ("world",      "World"),
    ("characters", "Characters"),
    ("npcs",       "NPCs"),
    ("locations",  "Locations"),
    ("factions",   "Factions"),
    ("items",      "Items"),
    ("sessions",   "Sessions"),
    ("rules",      "Rules"),
    ("story",      "Story"),
]
# Folder name -> default type (singular types used in frontmatter).
FOLDER_TYPE = {
    "world": "world", "characters": "character", "npcs": "npc",
    "locations": "location", "factions": "faction", "items": "item",
    "sessions": "session", "rules": "rule", "story": "story",
}
# Type -> sidebar section key.
TYPE_SECTION = {
    "world": "world", "character": "characters", "npc": "npcs",
    "location": "locations", "faction": "factions", "item": "items",
    "session": "sessions", "rule": "rules", "story": "story",
}
TYPE_LABEL = {
    "world": "World", "character": "Character", "npc": "NPC",
    "location": "Location", "faction": "Faction", "item": "Item",
    "session": "Session", "rule": "House Rule", "story": "Story",
}


def type_label(p):
    """Display label for a page's type chip - `label:` frontmatter overrides it."""
    return p.meta.get("label") or TYPE_LABEL.get(p.type, p.type)


# ----------------------------------------------------------------------------
# Frontmatter
# ----------------------------------------------------------------------------

def parse_frontmatter(text):
    """Split leading --- frontmatter from body. Returns (dict, body)."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}, text
    meta = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        i += 1
        if not line.strip() or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",")]
            meta[key] = [v for v in items if v]
        else:
            meta[key] = val.strip('"').strip("'")
    body = "\n".join(lines[i + 1:]) if i < len(lines) else ""
    return meta, body


def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s_]+", "-", s)
    return s or "page"


# ----------------------------------------------------------------------------
# Markdown -> HTML (stdlib; tables, images, lists, blockquotes, [[wikilinks]])
# ----------------------------------------------------------------------------

def smartquote(text):
    text = re.sub(r"\.{3,}", "…", text)
    text = re.sub(r'(^|[\s\(\[\{\*—–\-])"', r"\1“", text)
    text = text.replace('"', "”")
    text = re.sub(r"(^|[\s\(\[\{\*—–\-])'", r"\1‘", text)
    text = text.replace("'", "’")
    return text


# Placeholder so [[links]] survive HTML-escaping, restored afterwards.
_WL_OPEN, _WL_CLOSE = "\x00WL\x00", "\x00LW\x00"


def norm_key(s):
    """Normalize a link target/title for matching: undo HTML entities and
    typographic quotes so `[[The Porter's Guild]]` resolves after smart-quoting."""
    s = html.unescape(s)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'),
                 ("”", '"'), ("…", "...")):
        s = s.replace(a, b)
    return s.strip().lower()


def protect_wikilinks(text):
    return text.replace("[[", _WL_OPEN).replace("]]", _WL_CLOSE)


def render_wikilinks(text, resolve):
    """Replace protected [[Target|Display]] markers with resolved anchors.

    `resolve(target)` returns (page_id_or_None, canonical_title). Records the
    edge for backlinks. Unresolved links render greyed-out.
    """
    pattern = re.escape(_WL_OPEN) + r"(.+?)" + re.escape(_WL_CLOSE)

    def repl(m):
        inner = m.group(1)
        target, _, display = inner.partition("|")
        target = target.strip()
        display = display.strip() or target
        # inner is already HTML-escaped/smart-quoted; don't re-escape display.
        page_id, _canon = resolve(target)
        if page_id:
            return f'<a class="wl" href="#{page_id}">{display}</a>'
        return (f'<span class="wl-missing" title="No page yet: {target}">'
                f"{display}</span>")

    return re.sub(pattern, repl, text)


def md_inline(text, base_dir, image_loader):
    text = re.sub(r"\*\*([^*]+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+?)`", r"<code>\1</code>", text)

    def img_repl(m):
        alt, src = m.group(1), m.group(2)
        return img_tag(src, base_dir, alt)

    text = re.sub(r"!\[([^\]]*?)\]\(([^)]+?)\)", img_repl, text)

    def link_repl(m):
        link_text, href = m.group(1), m.group(2)
        if href.startswith("#"):
            return f'<a href="{href}">{link_text}</a>'
        # The whole site is one page, so anything that leaves it opens in a new
        # tab rather than throwing the reader out of where they were.
        return (f'<a href="{html.escape(href)}" target="_blank" '
                f'rel="noopener">{link_text}</a>')

    text = re.sub(r"\[([^\]]+?)\]\(([^)]+?)\)", link_repl, text)
    return text


# Inline footnotes, written ^[like this]. Collected per page and rendered as a
# numbered list at the foot of it. Used by the Story chapters for spell notes.
_FOOTNOTES = []


def stash_footnotes(raw):
    """Pull ^[...] out of the source and leave a marker the escaper won't touch."""
    def take(m):
        _FOOTNOTES.append(m.group(1))
        return "\x01FN%d\x01" % len(_FOOTNOTES)

    return re.sub(r"\^\[((?:[^\[\]]|\[[^\]]*\])*)\]", take, raw)


def restore_footnotes(text):
    def put(m):
        n = int(m.group(1))
        return (f'<sup class="fn-ref" id="fnref{n}">'
                f'<a href="#fn{n}">{n}</a></sup>')

    return re.sub(r"\x01FN(\d+)\x01", put, text)


def footnotes_html(base_dir, image_loader, resolve):
    """Render and clear the notes collected for the current page."""
    if not _FOOTNOTES:
        return ""
    items = []
    for i, body in enumerate(_FOOTNOTES, 1):
        inner = render_inline(body, base_dir, image_loader, resolve)
        items.append(f'<li id="fn{i}">{inner} '
                     f'<a class="fn-back" href="#fnref{i}">&#8617;</a></li>')
    _FOOTNOTES.clear()
    return '<ol class="footnotes">' + "".join(items) + "</ol>"


def render_inline(raw, base_dir, image_loader, resolve):
    raw = stash_footnotes(raw)
    raw = protect_wikilinks(raw)
    smart = smartquote(raw)
    escaped = html.escape(smart)
    inlined = md_inline(escaped, base_dir, image_loader)
    return restore_footnotes(render_wikilinks(inlined, resolve))


def is_table_sep(line):
    s = line.strip()
    return bool(s.startswith("|") and re.match(r"^\|(\s*:?-+:?\s*\|)+\s*$", s))


def parse_table(lines, start, ctx):
    if start + 1 >= len(lines) or not is_table_sep(lines[start + 1]):
        return None, start

    def split_row(line):
        s = line.strip().strip("|")
        return [c.strip() for c in s.split("|")]

    headers = split_row(lines[start])
    rows, i = [], start + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append(split_row(lines[i]))
        i += 1
    out = ["<table><thead><tr>"]
    for h in headers:
        out.append(f"<th>{render_inline(h, *ctx)}</th>")
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>" + "".join(f"<td>{render_inline(c, *ctx)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out), i


_AUDIO_RE = re.compile(r"^!audio\[([^\]]*)\]\(([^)]+)\)$")
_DRIVE_FILE_RE = re.compile(r"drive\.google\.com/file/d/([A-Za-z0-9_-]+)")


def audio_block(label, url):
    """A player for a session recording, written `!audio[Label](url)`.

    Recordings are hosted rather than committed: a three-hour episode is 250 MB
    or more, GitHub refuses any file over 100 MB, and anything that does land in
    this repo is in its public history for good.

    A Drive-hosted file gets Drive's own iframe player. A plain <audio> tag
    pointed at a Drive URL does not work for large files, because Drive answers
    with a scan-warning page instead of the bytes. Any other URL is assumed to
    serve the audio directly and gets a real <audio> element.
    """
    m = _DRIVE_FILE_RE.search(url)
    title = html.escape(label or "Session recording", quote=True)
    cap = f"<figcaption>{html.escape(label)}</figcaption>" if label else ""
    if m:
        src = f"https://drive.google.com/file/d/{m.group(1)}/preview"
        player = (f'<iframe class="audio-embed" src="{src}" title="{title}" '
                  f'loading="lazy" allow="autoplay"></iframe>')
    else:
        player = (f'<audio class="audio-embed" controls preload="none" '
                  f'src="{html.escape(url, quote=True)}"></audio>')
    return f'<figure class="audio">{player}{cap}</figure>'


def chronicle_block(block, resolve):
    """The day-by-day timeline, written as a ```chronicle fenced block.

    Parsed and rendered by `chronicle.py`, which the DM store imports too, so
    the two wikis cannot disagree about what day it is. See CHRONICLE_RULES.md
    in the DM store for how a day gets added.

    A malformed block stops the build on purpose. A broken Chronicle should not
    deploy quietly; failing here leaves the previous site up.
    """
    def wl(target, label):
        pid, _canon = resolve(target)
        if pid:
            return f'<a class="wl" href="#{pid}">{html.escape(label)}</a>'
        return (f'<span class="wl-missing" title="No page yet: '
                f'{html.escape(target, quote=True)}">{html.escape(label)}</span>')

    def episode_href(num):
        pid, _canon = resolve(f"Episode {num.strip()}")
        return f"#{pid}" if pid else None

    try:
        records = chronicle.parse_chronicle(block)
    except chronicle.ChronicleError as exc:
        raise SystemExit(f"Chronicle block is malformed: {exc}")
    for problem in chronicle.lint(records):
        print(f"  chronicle: {problem}")
    return chronicle.render_chronicle(records, wl, episode_href)


_ITEM_START = re.compile(r"(?:[-*] )|(?:\d+\.\s+)")
_BLOCK_START = re.compile(r"(?:#{1,6} )|(?:> )|\||```|<img|:::")


def _list_item_text(lines, i):
    """Return (item text, index of the next line) for the item starting at `i`.

    A list item's text may wrap onto following lines. Markdown treats an
    indented non-blank line that is not itself a new item as a continuation of
    the item above it. Without this the wrapped remainder fell out of the <li>
    and rendered as a separate paragraph underneath the list, which is what
    produced the stray line breaks in bulleted entries.

    A continuation must be INDENTED. Every wrapped item in site-content is, and
    requiring it means a paragraph that follows a list without a blank line
    cannot be swallowed into the last bullet. Nested items stay items: an
    indented line that starts with its own marker ends the continuation.
    """
    s = lines[i].strip()
    m = re.match(r"[-*]\s+(.*)", s) or re.match(r"\d+\.\s+(.*)", s)
    text = m.group(1)
    i += 1
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or not raw[:1].isspace():
            break
        nxt = raw.strip()
        if _ITEM_START.match(nxt) or _BLOCK_START.match(nxt):
            break
        text += " " + nxt
        i += 1
    return text, i


def md_to_html(md_text, base_dir, image_loader, resolve):
    ctx = (base_dir, image_loader, resolve)
    lines = md_text.split("\n")
    out, para, bq = [], [], []
    seen_h1 = False

    def flush_para():
        if para:
            text = " ".join(para).strip()
            para.clear()
            if text:
                out.append(f"<p>{render_inline(text, *ctx)}</p>")

    def flush_bq():
        if bq:
            text = " ".join(bq).strip()
            bq.clear()
            if text:
                out.append(f"<blockquote><p>{render_inline(text, *ctx)}</p></blockquote>")

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # The Chronicle - a ```chronicle block becomes the day-by-day timeline.
        # Checked before the generic fence below, which would otherwise swallow it.
        if s.startswith("```chronicle"):
            flush_para(); flush_bq()
            start = i
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1  # skip closing fence
            out.append(chronicle_block("\n".join(lines[start:i]), resolve))
            continue

        # Fenced code block - emit raw/escaped, no inline or wiki-link processing.
        if s.startswith("```"):
            flush_para(); flush_bq()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1  # skip closing fence
            out.append(f"<pre><code>{html.escape(chr(10).join(buf))}</code></pre>")
            continue

        m_audio = _AUDIO_RE.match(s)
        if m_audio:
            flush_para(); flush_bq()
            out.append(audio_block(m_audio.group(1).strip(), m_audio.group(2).strip()))
            i += 1
            continue

        if s.startswith("|") and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            flush_para(); flush_bq()
            tbl, ni = parse_table(lines, i, ctx)
            if tbl:
                out.append(tbl); i = ni; continue

        if not s:
            flush_para(); flush_bq(); i += 1; continue

        if s == "---":
            flush_para(); flush_bq(); out.append("<hr/>"); i += 1; continue

        if s.startswith(">"):
            flush_para(); bq.append(s[1:].strip()); i += 1; continue
        if bq:
            flush_bq()

        m = re.match(r"(#{1,4})\s+(.*)", s)
        if m:
            flush_para()
            level = len(m.group(1))
            title = render_inline(m.group(2).strip(), *ctx)
            if level == 1 and not seen_h1:
                seen_h1 = True  # page title rendered separately; skip in-body
            elif level == 1:
                out.append(f'<h2 class="h-1">{title}</h2>')
            else:
                out.append(f'<h{level} class="h-{level}">{title}</h{level}>')
            i += 1; continue

        mimg = re.match(r'<img\s+src="([^"]+)"[^>]*?/?>', s)
        if mimg:
            flush_para()
            out.append(f'<figure>{img_tag(mimg.group(1), base_dir)}</figure>')
            i += 1; continue

        if s.startswith("- ") or s.startswith("* "):
            flush_para()
            items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                text, i = _list_item_text(lines, i)
                items.append(f"<li>{render_inline(text, *ctx)}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        mol = re.match(r"\d+\.\s+(.*)", s)
        if mol:
            flush_para()
            items = []
            while i < len(lines) and re.match(r"\d+\.\s+", lines[i].strip()):
                text, i = _list_item_text(lines, i)
                items.append(f"<li>{render_inline(text, *ctx)}</li>")
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        para.append(s); i += 1

    flush_para(); flush_bq()
    out.append(footnotes_html(base_dir, image_loader, resolve))
    return "\n".join(out)


def plain_text(md_text):
    """Strip markdown/frontmatter to plain text for the search index."""
    t = re.sub(r"\^\[((?:[^\[\]]|\[[^\]]*\])*)\]", r" \1 ", md_text)
    t = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", t)
    # Chronicle records are `field: value` lines; index the values, not the labels.
    t = re.sub(r"^(date|episode|status|gap|text):\s*", "", t, flags=re.MULTILINE)
    t = re.sub(r"[#*`>_\-]", " ", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# ----------------------------------------------------------------------------
# Images
# ----------------------------------------------------------------------------

_image_cache = {}

def image_loader(rel_path, base_dir):
    abs_path = (base_dir / rel_path).resolve()
    key = str(abs_path)
    if key in _image_cache:
        return _image_cache[key]
    if not abs_path.exists():
        print(f"  -- image not found: {rel_path}")
        return None
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"
            }.get(abs_path.suffix.lower(), "application/octet-stream")
    data_uri = f"data:{mime};base64," + base64.b64encode(abs_path.read_bytes()).decode("ascii")
    _image_cache[key] = data_uri
    return data_uri


# Each unique image is stored ONCE in a JS array; <img> tags reference it by
# index (data-img="N") and JS sets the src on load. This stops an image used on
# several pages from being embedded multiple times.
_img_registry = []
_img_index = {}

def register_image(data_uri):
    if data_uri in _img_index:
        return _img_index[data_uri]
    idx = len(_img_registry)
    _img_registry.append(data_uri)
    _img_index[data_uri] = idx
    return idx


def img_tag(src, base_dir, alt="", cls=""):
    """Build an <img>. Local images are de-duplicated via the registry."""
    cls_attr = f' class="{cls}"' if cls else ""
    if not src.startswith(("http://", "https://", "data:")):
        du = image_loader(src, base_dir)
        if du:
            idx = register_image(du)
            return f'<img{cls_attr} data-img="{idx}" alt="{html.escape(alt)}">'
    return f'<img{cls_attr} src="{html.escape(src)}" alt="{html.escape(alt)}">'


# ----------------------------------------------------------------------------
# Load pages
# ----------------------------------------------------------------------------

class Page:
    __slots__ = ("id", "title", "type", "section", "meta", "body", "base_dir",
                 "aliases", "summary", "parent", "group", "html", "links", "backlinks")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))
        self.links = set()
        self.backlinks = []


def load_pages(content_dir):
    pages = []
    for folder, _label in SECTIONS:
        fdir = content_dir / folder
        if not fdir.is_dir():
            continue
        for md_path in sorted(fdir.rglob("*.md")):
            rel = md_path.relative_to(content_dir)
            # Skip anything inside folders starting with _ or . (templates, backups)
            if any(part.startswith(("_", ".")) for part in rel.parts):
                continue
            raw = md_path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(raw)
            ptype = meta.get("type") or FOLDER_TYPE.get(folder, folder)
            m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            title = meta.get("name") or (m.group(1).strip() if m else md_path.stem)
            pid = slugify("-".join(rel.with_suffix("").parts))
            aliases = meta.get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            pages.append(Page(
                id=pid, title=title, type=ptype,
                section=TYPE_SECTION.get(ptype, folder),
                meta=meta, body=body, base_dir=md_path.parent,
                aliases=aliases, summary=meta.get("summary", ""),
                parent=meta.get("parent"), group=meta.get("group"),
            ))
    return pages


def build_resolver(pages):
    """Map normalized title/alias -> page_id (case-insensitive)."""
    table = {}
    for p in pages:
        for name in [p.title] + list(p.aliases):
            table.setdefault(norm_key(name), p.id)
    return table


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------

def page_sort_key(p):
    """Order pages by session number, then explicit `order:`, then title."""
    try:
        sess = int(p.meta.get("session", 9999))
    except (TypeError, ValueError):
        sess = 9999
    try:
        order = int(p.meta.get("order", 999))
    except (TypeError, ValueError):
        order = 999
    return (sess, order, p.title.lower())


def render_pages(pages, resolver):
    by_id = {p.id: p for p in pages}

    for p in pages:
        def resolve(target, _p=p):
            pid = resolver.get(norm_key(target))
            if pid and pid != _p.id:
                _p.links.add(pid)
            return (pid, target)
        p.html = md_to_html(p.body, p.base_dir, image_loader, resolve)

    # Backlinks
    for p in pages:
        for target_id in p.links:
            if target_id in by_id:
                by_id[target_id].backlinks.append(p.id)
    return by_id


def chips_html(p):
    chips = [f'<span class="chip chip-type">{html.escape(type_label(p))}</span>']
    if p.meta.get("race"):
        chips.append(f'<span class="chip">{html.escape(p.meta["race"])}</span>')
    if p.meta.get("faction"):
        chips.append(f'<span class="chip">{html.escape(p.meta["faction"])}</span>')
    if p.meta.get("status"):
        chips.append(f'<span class="chip">{html.escape(p.meta["status"])}</span>')
    if p.meta.get("age"):
        chips.append(f'<span class="chip chip-muted">Age {html.escape(p.meta["age"])}</span>')
    if p.meta.get("pronouns"):
        chips.append(f'<span class="chip chip-muted">{html.escape(p.meta["pronouns"])}</span>')
    if p.meta.get("player"):
        chips.append(f'<span class="chip chip-muted">Played by {html.escape(p.meta["player"])}</span>')
    if p.meta.get("date"):
        chips.append(f'<span class="chip chip-muted">{html.escape(p.meta["date"])}</span>')
    return '<div class="chips">' + "".join(chips) + "</div>"


def avatar_html(p):
    portrait = p.meta.get("portrait")
    if not portrait:
        return ""
    if not image_loader(portrait, p.base_dir):
        return ""
    return f'<div class="avatar">{img_tag(portrait, p.base_dir, p.title, cls="avatar-img")}</div>'


def _bl_item(b):
    return (f'<li><a href="#{b.id}"><span class="bl-title">{html.escape(b.title)}</span>'
            f'<span class="bl-type">{html.escape(type_label(b))}</span></a></li>')


def backlinks_html(p, by_id, resolver):
    if not p.backlinks:
        return ""
    sess, other = [], []
    for bid in set(p.backlinks):
        b = by_id[bid]
        (sess if b.section == "sessions" else other).append(b)

    out = []
    if sess:
        # Collapse summary/story to their episode, then order chronologically.
        episodes = {}
        for b in sess:
            ep = b
            if b.parent:
                pid = resolver.get(norm_key(b.parent))
                if pid and pid in by_id and by_id[pid].section == "sessions":
                    ep = by_id[pid]
            episodes[ep.id] = ep
        items = "".join(
            f'<li><a href="#{e.id}"><span class="bl-title">{html.escape(e.title)}</span>'
            f'<span class="bl-type">Session</span></a></li>'
            for e in sorted(episodes.values(), key=page_sort_key))
        out.append('<section class="backlinks"><h2 class="h-1">Appears in</h2>'
                   f'<ul class="bl-list">{items}</ul></section>')
    if other:
        items = "".join(_bl_item(b) for b in sorted(other, key=lambda x: x.title.lower()))
        out.append('<section class="backlinks"><h2 class="h-1">Mentioned in</h2>'
                   f'<ul class="bl-list">{items}</ul></section>')
    return "".join(out)


def page_section_html(p, by_id, resolver):
    avatar = avatar_html(p)
    head_class = "page-head with-avatar" if avatar else "page-head"
    return (
        f'<article class="page" id="{p.id}">'
        f'<header class="{head_class}">'
        f"{avatar}"
        '<div class="page-head-text">'
        f'<h1 class="page-title">{html.escape(p.title)}</h1>'
        f"{chips_html(p)}"
        "</div>"
        f"</header>"
        f'<div class="page-body">{p.html}</div>'
        f"{backlinks_html(p, by_id, resolver)}"
        f"</article>"
    )


def _nav_link(p):
    return (f'<a class="nav-link" href="#{p.id}" data-id="{p.id}">'
            f'{html.escape(p.title)}</a>')


def _render_node(p, children, depth):
    kids = children.get(p.id)
    if not kids:
        return f"<li>{_nav_link(p)}</li>"
    sub_id = f"sub-{p.id}"
    inner = "".join(_render_node(c, children, depth + 1) for c in kids)
    return (
        '<li class="has-children">'
        '<div class="nav-row">'
        f'<button class="tw-toggle" data-collapse="{sub_id}" aria-label="Toggle">'
        '<span class="caret">▾</span></button>'
        f"{_nav_link(p)}"
        "</div>"
        f'<ul class="subtree" id="{sub_id}">{inner}</ul>'
        "</li>"
    )


def _subgroup_html(key, name, roots, children):
    gid = slugify(f"grp-{key}-{name}")
    inner = "".join(_render_node(r, children, 1) for r in roots)
    return (
        '<li class="nav-subgroup">'
        f'<button class="subgroup-label" data-collapse="{gid}">'
        '<span class="caret">▾</span>'
        f'<span class="subgroup-text">{html.escape(name)}</span>'
        f'<span class="nav-count">{len(roots)}</span></button>'
        f'<ul class="subtree" id="{gid}">{inner}</ul>'
        "</li>"
    )


def _section_tree(plist, resolver):
    """Return (ungrouped_roots, group_order, grouped_roots, children) for a section."""
    ids = {p.id for p in plist}
    children, roots = {}, []
    for p in plist:
        par_id = resolver.get(norm_key(p.parent)) if p.parent else None
        if par_id and par_id in ids and par_id != p.id:
            children.setdefault(par_id, []).append(p)
        else:
            roots.append(p)
    for kid_list in children.values():
        kid_list.sort(key=page_sort_key)
    ungrouped, grouped, group_order = [], {}, []
    for r in roots:
        g = (r.group or "").strip()
        if g:
            if g not in grouped:
                grouped[g] = []
                group_order.append(g)
            grouped[g].append(r)
        else:
            ungrouped.append(r)
    return ungrouped, group_order, grouped, children


def sidebar_html(pages_by_section, resolver):
    """Collapsible sections; `parent:` nests pages; `group:` adds sub-headings.
    The caret toggles a section; the section name links to its overview page."""
    parts = []
    for key, label in SECTIONS:
        if key not in pages_by_section:
            continue
        plist = pages_by_section[key]
        ungrouped, group_order, grouped, children = _section_tree(plist, resolver)
        sec_id = f"sec-{key}"
        parts.append(
            '<div class="nav-group"><div class="nav-head">'
            f'<button class="caret-btn" data-collapse="{sec_id}" aria-label="Toggle">'
            '<span class="caret">▾</span></button>'
            f'<a class="nav-label" href="#section-{key}">'
            f'<span class="nav-label-text">{html.escape(label)}</span></a></div>'
            f'<ul class="nav-list" id="{sec_id}">'
        )
        if not plist:
            parts.append('<li class="nav-empty">Nothing here yet</li>')
        parts.append("".join(_render_node(p, children, 0) for p in ungrouped))
        for g in group_order:
            parts.append(_subgroup_html(key, g, grouped[g], children))
        parts.append("</ul></div>")
    return "".join(parts)


def _count_descendants(roots, children):
    n = 0
    for r in roots:
        n += 1 + _count_descendants(children.get(r.id, []), children)
    return n


def _dir_items(roots, children):
    out = []
    for r in roots:
        summ = f' - <span class="dir-sum">{html.escape(r.summary)}</span>' if r.summary else ""
        kids = children.get(r.id)
        sub = f'<ul class="dir-sub">{_dir_items(kids, children)}</ul>' if kids else ""
        out.append(f'<li><a href="#{r.id}">{html.escape(r.title)}</a>{summ}{sub}</li>')
    return "".join(out)


def section_overview_html(key, label, plist, resolver, content_dir):
    """A landing page for a whole section: optional prose + an auto directory."""
    ungrouped, group_order, grouped, children = _section_tree(plist, resolver)

    intro = ""
    sec_file = content_dir / key / "_section.md"
    if sec_file.exists():
        _, body = parse_frontmatter(sec_file.read_text(encoding="utf-8"))

        def ov_resolve(t):
            return (resolver.get(norm_key(t)), t)

        intro = (f'<div class="page-body">'
                 f'{md_to_html(body, sec_file.parent, image_loader, ov_resolve)}</div>')

    if group_order:
        bits = ", ".join(
            f"{html.escape(g)} ({_count_descendants(grouped[g], children)})"
            for g in group_order)
        lead = f"{len(plist)} entries across {len(group_order)} groups - {bits}."
    else:
        lead = f"{len(plist)} entries."

    dir_parts = []
    if not plist:
        dir_parts.append('<p class="dir-empty">No entries yet.</p>')
    if ungrouped:
        dir_parts.append(f'<ul class="dir">{_dir_items(ungrouped, children)}</ul>')
    for g in group_order:
        cnt = _count_descendants(grouped[g], children)
        dir_parts.append(
            f'<h2 class="h-1">{html.escape(g)} <span class="dir-count">{cnt}</span></h2>'
            f'<ul class="dir">{_dir_items(grouped[g], children)}</ul>'
        )

    return (
        f'<article class="page" id="section-{key}">'
        '<header class="page-head">'
        f'<h1 class="page-title">{html.escape(label)}</h1>'
        f'<p class="section-lead">{lead}</p></header>'
        f"{intro}" + "".join(dir_parts) + "</article>"
    )


def home_html(resolver, content_dir):
    """The landing page shown when the title is clicked (id="home")."""
    players = " · ".join(html.escape(p) for p in PLAYERS)
    intro = "".join(f"<p>{html.escape(par)}</p>" for par in HOME_INTRO)
    quick = [("The Faith of the Four Kin", "Begin with the myth"),
             ("Parvo", "Enter the city"),
             ("The Theocide", "The day a god died")]
    links = []
    for title, label in quick:
        pid = resolver.get(norm_key(title))
        if pid:
            links.append(f'<a class="home-link" href="#{pid}">{html.escape(label)}</a>')
    links_html = ('<div class="home-links">' + "".join(links) + "</div>") if links else ""
    return (
        '<article class="page" id="home"><div class="home-hero">'
        f'<p class="home-kicker">{html.escape(SITE_SUBTITLE)}</p>'
        f'<h1 class="home-title">{html.escape(SITE_TITLE)}</h1>'
        f'<p class="home-tagline">{html.escape(CAMPAIGN_TAGLINE)}</p>'
        '<div class="home-credits">'
        '<div class="cred"><span class="cred-label">Game Master</span>'
        f'<span class="cred-names">{html.escape(DM_NAME)}</span></div>'
        '<div class="cred"><span class="cred-label">Players</span>'
        f'<span class="cred-names">{players}</span></div>'
        '</div>'
        f'<div class="home-intro">{intro}</div>'
        f'{links_html}'
        '</div></article>'
    )


# ----------------------------------------------------------------------------
# CSS / JS
# ----------------------------------------------------------------------------

CSS = r"""
:root{
  --bg:#faf8f4; --panel:#ffffff; --side:#f3efe7; --text:#1f1b16; --muted:#7a7264;
  --rule:#e3dcce; --link:#9a5b2a; --accent:#b06a30; --chip:#efe7d8; --shadow:0 1px 3px rgba(0,0,0,.06);
}
@media (prefers-color-scheme:dark){:root{
  --bg:#15130f; --panel:#1d1a15; --side:#1a1712; --text:#e7e0d2; --muted:#9b9484;
  --rule:#332e26; --link:#d9a259; --accent:#d9a259; --chip:#2a251d; --shadow:0 1px 3px rgba(0,0,0,.4);
}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;
  font-size:1.04rem;line-height:1.7;-webkit-font-smoothing:antialiased;display:flex}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}

/* Sidebar */
.sidebar{width:18rem;flex:0 0 18rem;height:100vh;position:sticky;top:0;overflow-y:auto;
  background:var(--side);border-right:1px solid var(--rule);padding:1.2rem 1rem}
.brand{display:block;margin:0 0 .2rem;font-size:1.3rem;font-weight:600;
  letter-spacing:.02em;color:var(--text);cursor:pointer}
.brand:hover{color:var(--accent);text-decoration:none}
.brand-sub{color:var(--muted);font-size:.82rem;margin:0 0 1rem;text-transform:uppercase;letter-spacing:.18em}
.search-wrap{position:relative;margin-bottom:1.2rem}
#search{width:100%;padding:.5rem .7rem;border:1px solid var(--rule);border-radius:8px;
  background:var(--panel);color:var(--text);font:inherit;font-size:.92rem}
#search:focus{outline:none;border-color:var(--accent)}
#results{list-style:none;margin:.4rem 0 0;padding:0;max-height:50vh;overflow-y:auto}
#results li{margin:0}
#results a{display:block;padding:.4rem .55rem;border-radius:6px;font-size:.9rem;color:var(--text)}
#results a:hover{background:var(--chip);text-decoration:none}
#results .r-type{color:var(--muted);font-size:.74rem;margin-left:.4rem}
.nav-group{margin-bottom:1.3rem}
.nav-head{display:flex;align-items:center;gap:.25rem;margin-bottom:.5rem;
  padding-bottom:.2rem;border-bottom:1px solid var(--rule)}
.caret-btn{background:none;border:none;color:var(--muted);cursor:pointer;
  padding:.2rem;font-size:1.05rem;line-height:1}
.nav-label{flex:1;display:flex;align-items:center;gap:.5rem;color:var(--text);
  font-size:.98rem;letter-spacing:.06em;font-weight:700;padding:.1rem 0}
.nav-label:hover{color:var(--accent);text-decoration:none}
.nav-label-text{flex:1}
.nav-count{opacity:.55;font-weight:400;font-size:.8rem}
.nav-list,.subtree{list-style:none;margin:0;padding:0}
.subtree{margin:.15rem 0 .35rem .55rem;padding-left:.45rem;border-left:1px solid var(--rule)}
.nav-row{display:flex;align-items:center;gap:.1rem}
.nav-row .nav-link{flex:1}
.nav-link{display:block;padding:.28rem .5rem;border-radius:6px;color:var(--text);font-size:.94rem}
.nav-link:hover{background:var(--chip);text-decoration:none}
.nav-link.active{background:var(--accent);color:#fff}
/* Sub-group heading (e.g. "Cities" under Locations) */
.nav-subgroup{margin:.25rem 0}
.subgroup-label{display:flex;align-items:center;gap:.45rem;width:100%;background:none;border:none;
  cursor:pointer;font-family:inherit;font-size:.78rem;text-transform:uppercase;
  letter-spacing:.12em;color:var(--muted);font-weight:600;padding:.2rem .25rem;text-align:left}
.subgroup-label:hover{color:var(--text)}
.subgroup-text{flex:1}
.tw-toggle{background:none;border:none;color:var(--muted);cursor:pointer;
  padding:0 .15rem;font-size:.95rem;line-height:1}
.caret{display:inline-block;transition:transform .15s ease;font-size:1em}
.collapsed .caret{transform:rotate(-90deg)}
.nav-list.hidden,.subtree.hidden{display:none}

/* Content */
.content{flex:1;min-width:0;display:flex;justify-content:center;padding:2.5rem 2rem 6rem}
.page{display:none;width:100%;max-width:44rem}
.page.active{display:block}
.page-head{border-bottom:1px solid var(--rule);padding-bottom:1rem;margin-bottom:1.5rem}
.page-title{font-size:2.2rem;font-weight:600;margin:0 0 .6rem;line-height:1.15}
.chips{display:flex;flex-wrap:wrap;gap:.4rem}
.chip{background:var(--chip);color:var(--muted);font-size:.76rem;padding:.18rem .6rem;
  border-radius:999px;letter-spacing:.02em}
.chip-type{background:var(--accent);color:#fff}
.chip-muted{background:transparent;border:1px solid var(--rule)}
.portrait{margin:0 0 1.5rem;text-align:center}
.portrait img{max-width:min(320px,100%);height:auto;border-radius:10px;box-shadow:var(--shadow)}
.page-body p{margin:.85em 0}
.h-1{font-size:1.4rem;font-weight:600;margin:2rem 0 .8rem;padding-bottom:.3rem;border-bottom:1px solid var(--rule)}
.h-2{font-size:1.2rem;font-weight:600;margin:1.6rem 0 .6rem}
.h-3,.h-4{font-size:1.05rem;font-weight:600;margin:1.3rem 0 .5rem}
.page-body ul,.page-body ol{padding-left:1.4em}
.page-body li{margin:.3em 0}
code{background:var(--chip);padding:.1em .35em;border-radius:4px;font-size:.88em}
pre{background:var(--chip);border:1px solid var(--rule);border-radius:8px;
  padding:.8rem 1rem;overflow-x:auto;font-size:.84rem;line-height:1.5}
pre code{background:none;padding:0;font-size:inherit}
blockquote{margin:1.2rem 0;padding:.3rem 1.1rem;border-left:3px solid var(--rule);
  color:var(--muted);font-style:italic}
table{border-collapse:collapse;width:100%;margin:1.2rem 0;font-size:.94rem}
th,td{border-bottom:1px solid var(--rule);padding:.5rem .7rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;border-bottom:2px solid var(--rule)}
figure.audio{margin:1.5rem 0}
figure.audio .audio-embed{width:100%;border:0;border-radius:8px;box-shadow:var(--shadow)}
figure.audio iframe.audio-embed{height:66px}
figure.audio audio.audio-embed{height:44px;box-shadow:none}
figure.audio figcaption{margin-top:.45rem;font-size:.82rem;opacity:.75;text-align:left}
figure{margin:1.5rem 0;text-align:center}
figure img{max-width:100%;height:auto;border-radius:8px;box-shadow:var(--shadow)}
/* Any image in body text: never overflow the column; centre block images */
.page-body img{max-width:100%;height:auto;border-radius:8px;display:block;
  margin:1.5rem auto;box-shadow:var(--shadow)}
/* Maps and large diagrams: keep them comfortably within the reading column */
.page-body p>img:only-child{max-width:min(560px,100%)}

/* Click-to-enlarge overlay: zoom and pan, for maps with small labels */
.page-body img,figure img,.avatar-img,.portrait img{cursor:zoom-in}
#lightbox{position:fixed;inset:0;z-index:200;display:none;
  background:rgba(0,0,0,.93);touch-action:none;overflow:hidden}
#lightbox.open{display:block}
#lightbox img{position:absolute;top:0;left:0;transform-origin:0 0;
  max-width:none;max-height:none;margin:0;border-radius:0;box-shadow:none;
  cursor:grab;user-select:none;-webkit-user-drag:none}
#lightbox.grabbing img{cursor:grabbing}
#lb-close{position:fixed;top:.7rem;right:1rem;z-index:201;
  background:rgba(0,0,0,.45);color:#fff;border:1px solid rgba(255,255,255,.28);
  border-radius:8px;font-size:1.5rem;line-height:1;padding:.25rem .6rem;
  cursor:pointer;font-family:inherit}
#lb-close:hover{background:rgba(0,0,0,.75)}
#lb-hint{position:fixed;bottom:.9rem;left:50%;transform:translateX(-50%);
  z-index:201;color:rgba(255,255,255,.8);font-size:.78rem;letter-spacing:.02em;
  background:rgba(0,0,0,.5);padding:.32rem .8rem;border-radius:999px;
  pointer-events:none;white-space:nowrap}
@media (max-width:600px){#lb-hint{font-size:.7rem}}
hr{border:none;border-top:1px solid var(--rule);margin:2rem 0}

/* Wiki links */
.wl{color:var(--link);border-bottom:1px solid transparent}
.wl:hover{border-bottom-color:var(--link);text-decoration:none}
.wl-missing{color:var(--muted);border-bottom:1px dotted var(--muted);cursor:help}

/* Footnotes: ^[like this] in the source, collected at the foot of the page */
.fn-ref{font-size:.7em;line-height:0}
.fn-ref a{text-decoration:none;padding:0 .12em}
ol.footnotes{margin:2.2em 0 0;padding:1.1em 0 0 1.3em;border-top:1px solid var(--rule);
  font-size:.88em;color:var(--muted)}
ol.footnotes li{margin:.5em 0}
ol.footnotes li:target{color:var(--text)}
a.fn-back{text-decoration:none;opacity:.55}

/* ---------- Homepage hero ---------- */
.home-hero{max-width:44rem;margin:0 auto;text-align:center;padding:1.5rem 0 1rem}
.home-kicker{text-transform:uppercase;letter-spacing:.34em;font-size:.78rem;
  color:var(--muted);margin:0 0 .4rem}
.home-title{font-size:3.4rem;font-weight:700;letter-spacing:.02em;line-height:1.05;margin:.1rem 0}
.home-tagline{font-style:italic;font-size:1.25rem;color:var(--accent);margin:.5rem 0 1.4rem}
.home-emblem{display:block;width:min(380px,82%);height:auto;border-radius:10px;
  box-shadow:var(--shadow);margin:1rem auto 1.8rem}
.home-credits{display:flex;flex-wrap:wrap;justify-content:center;gap:2.5rem;
  margin:1.6rem 0;padding:1.2rem 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.cred{display:flex;flex-direction:column;gap:.25rem}
.cred-label{text-transform:uppercase;letter-spacing:.16em;font-size:.72rem;color:var(--muted)}
.cred-names{font-size:1.1rem;font-weight:600}
.home-intro{font-size:1.08rem;line-height:1.75;margin:1.6rem auto;max-width:40rem;text-align:left}
.home-intro p:nth-last-child(2){text-align:center;font-style:italic;color:var(--accent)}
.home-intro p:last-child{text-align:center;font-style:italic;color:var(--muted);
  font-size:.9rem;opacity:.85;margin-top:.4rem}
.home-links{display:flex;flex-wrap:wrap;justify-content:center;gap:.8rem;margin-top:2rem}
.home-link{padding:.55rem 1.15rem;border:1px solid var(--rule);border-radius:999px;
  color:var(--text);font-size:.95rem}
.home-link:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}

/* ---------- Section overview pages ---------- */
.section-lead{color:var(--muted);font-style:italic;margin:.4rem 0 0;font-size:1rem}
.dir{list-style:none;padding:0;margin:.8rem 0}
.dir>li{margin:.55rem 0}
.dir a{font-weight:600}
.dir-sum{color:var(--muted);font-weight:400;font-style:italic}
.dir-sub{list-style:none;margin:.35rem 0 .35rem 1rem;padding-left:.7rem;
  border-left:1px solid var(--rule)}
.dir-count{color:var(--muted);font-size:.82rem;font-weight:400}
.dir-empty{color:var(--muted);font-style:italic}
.nav-empty{color:var(--muted);font-size:.85rem;font-style:italic;padding:.2rem .5rem}

/* Portrait avatar in page header.
   Matched to the DM render 2026-08-17: a large floated portrait the text wraps
   around, not a 110px thumbnail. With a portrait present the header's rule
   belongs under the TEXT rather than under the whole header, because a
   full-width border would otherwise run behind the floated image. */
.page-head.with-avatar{border-bottom:none;padding-bottom:0;margin-bottom:0}
.page-head.with-avatar .page-head-text{border-bottom:1px solid var(--rule);
  padding-bottom:1rem;margin-bottom:1.5rem}
.avatar{float:right;width:min(50%,380px);margin:0 0 1.2rem 1.6rem}
.avatar-img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:12px;
  box-shadow:var(--shadow);display:block}
/* Too narrow to wrap text beside it: give the portrait the full column. */
@media(max-width:720px){
  .avatar{float:none;width:100%;max-width:360px;margin:0 auto 1.4rem}
}

/* Hover preview card */
#preview{position:fixed;z-index:60;display:none;max-width:320px;background:var(--panel);
  border:1px solid var(--rule);border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.2);
  padding:.7rem .85rem;pointer-events:none;font-size:.9rem;line-height:1.5}
#preview .pv-type{font-size:.66rem;text-transform:uppercase;letter-spacing:.14em;
  color:var(--accent);font-weight:600;margin-bottom:.15rem}
#preview .pv-title{font-weight:600;font-size:1.02rem;margin-bottom:.25rem}
#preview .pv-sum{color:var(--muted)}

/* Backlinks */
.backlinks{margin-top:3rem;padding-top:.5rem}
.bl-list{list-style:none;padding:0;margin:.5rem 0 0;display:grid;gap:.4rem}
.bl-list a{display:flex;justify-content:space-between;align-items:center;gap:1rem;
  padding:.5rem .8rem;background:var(--panel);border:1px solid var(--rule);border-radius:8px;color:var(--text)}
.bl-list a:hover{border-color:var(--accent);text-decoration:none}
.bl-type{color:var(--muted);font-size:.78rem}

/* Mobile */
.menu-btn{display:none}
@media(max-width:820px){
  body{flex-direction:column}
  .sidebar{position:static;width:100%;flex-basis:auto;height:auto;border-right:none;
    border-bottom:1px solid var(--rule)}
  .content{padding:1.5rem 1.1rem 4rem}
  .page-title{font-size:1.7rem}
}
"""

# The Chronicle component ships its own rules and inherits the palette above.
CSS += chronicle.CHRONICLE_CSS

JS_TEMPLATE = r"""
(function(){
  var idx = __SEARCH_INDEX__;
  var ids = __VALID_IDS__;
  var pages = document.querySelectorAll('.page');
  var navlinks = document.querySelectorAll('.nav-link');

  // ---- Collapsible sidebar (sections + nested tree), remembered per browser ----
  var CKEY='sael-collapsed';
  function defaultCollapsed(){
    // First-ever visit (no saved preference yet): start with the top-level
    // section tabs (World, Characters, NPCs, …) collapsed. Nested subtrees
    // stay as-is since they're not visible until their section is opened anyway.
    var ids=[];
    document.querySelectorAll('.nav-group > .nav-list').forEach(function(el){ids.push(el.id);});
    return ids;
  }
  function loadCollapsed(){
    try{
      var raw=localStorage.getItem(CKEY);
      if(raw===null) return defaultCollapsed();
      return JSON.parse(raw)||[];
    }catch(e){return [];}
  }
  function saveCollapsed(a){try{localStorage.setItem(CKEY,JSON.stringify(a));}catch(e){}}
  var collapsed=loadCollapsed();
  saveCollapsed(collapsed);
  collapsed.forEach(function(cid){
    var b=document.getElementById(cid); if(b){b.classList.add('hidden');}
    var t=document.querySelector('[data-collapse="'+cid+'"]'); if(t){t.classList.add('collapsed');}
  });
  document.addEventListener('click',function(e){
    var t=e.target.closest('[data-collapse]'); if(!t) return;
    e.preventDefault();
    var cid=t.getAttribute('data-collapse'); var b=document.getElementById(cid); if(!b) return;
    var nowHidden=b.classList.toggle('hidden'); t.classList.toggle('collapsed', nowHidden);
    var i=collapsed.indexOf(cid);
    if(nowHidden && i===-1) collapsed.push(cid);
    if(!nowHidden && i!==-1) collapsed.splice(i,1);
    saveCollapsed(collapsed);
  });
  function reveal(id){
    var link=document.querySelector('.nav-link[data-id="'+id+'"]'); if(!link) return;
    var el=link.parentElement;
    while(el){
      if(el.classList && (el.classList.contains('subtree')||el.classList.contains('nav-list'))){
        el.classList.remove('hidden');
        var tg=document.querySelector('[data-collapse="'+el.id+'"]'); if(tg) tg.classList.remove('collapsed');
      }
      el=el.parentElement;
    }
  }

  function show(id){
    if(ids.indexOf(id)===-1) id = ids[0];
    for(var i=0;i<pages.length;i++) pages[i].classList.toggle('active', pages[i].id===id);
    for(var j=0;j<navlinks.length;j++) navlinks[j].classList.toggle('active', navlinks[j].dataset.id===id);
    reveal(id);
    try{document.querySelector('.content').scrollTo({top:0,behavior:'instant'});}catch(e){}
    window.scrollTo(0,0);
  }
  function sync(){ show(location.hash.slice(1) || ids[0]); }
  sync();
  window.addEventListener('hashchange', sync);

  var box = document.getElementById('search');
  var results = document.getElementById('results');
  function clearResults(){ results.innerHTML=''; }
  box.addEventListener('input', function(){
    var q = box.value.trim().toLowerCase();
    clearResults();
    if(q.length<2) return;
    var hits=[];
    for(var i=0;i<idx.length;i++){
      var it=idx[i];
      var score = it.title.toLowerCase().indexOf(q)!==-1 ? 0
                : (it.text.indexOf(q)!==-1 ? 1 : -1);
      if(score>=0) hits.push([score,it]);
    }
    hits.sort(function(a,b){return a[0]-b[0];});
    for(var k=0;k<hits.length && k<12;k++){
      var it=hits[k][1];
      var li=document.createElement('li');
      li.innerHTML='<a href="#'+it.id+'">'+it.title+'<span class="r-type">'+it.type+'</span></a>';
      results.appendChild(li);
    }
  });
  results.addEventListener('click', function(e){
    if(e.target.closest('a')){ box.value=''; clearResults(); }
  });

  // Hover preview cards on [[wiki-links]].
  var previews = __PREVIEWS__;
  var tip = document.getElementById('preview');
  var tipTimer = null;
  function showTip(a){
    var p = previews[a.getAttribute('href').slice(1)];
    if(!p){ return; }
    tip.innerHTML='';
    var ty=document.createElement('div'); ty.className='pv-type'; ty.textContent=p.type; tip.appendChild(ty);
    var ti=document.createElement('div'); ti.className='pv-title'; ti.textContent=p.title; tip.appendChild(ti);
    if(p.summary){ var s=document.createElement('div'); s.className='pv-sum'; s.textContent=p.summary; tip.appendChild(s); }
    tip.style.display='block';
    var r=a.getBoundingClientRect(), tw=tip.offsetWidth, th=tip.offsetHeight;
    var left=r.left, top=r.bottom+8;
    if(left+tw>window.innerWidth-12) left=window.innerWidth-tw-12;
    if(left<12) left=12;
    if(top+th>window.innerHeight-12) top=r.top-th-8;
    tip.style.left=left+'px'; tip.style.top=top+'px';
  }
  function hideTip(){ tip.style.display='none'; }
  document.addEventListener('mouseover', function(e){
    var a=e.target.closest && e.target.closest('a.wl');
    if(a){ clearTimeout(tipTimer); tipTimer=setTimeout(function(){ showTip(a); }, 120); }
  });
  document.addEventListener('mouseout', function(e){
    var a=e.target.closest && e.target.closest('a.wl');
    if(a){ clearTimeout(tipTimer); hideTip(); }
  });
  window.addEventListener('hashchange', hideTip);

  // Rehydrate de-duplicated images (each unique image stored once).
  var IMAGES = __IMAGES__;
  var imgs = document.querySelectorAll('img[data-img]');
  for(var n=0;n<imgs.length;n++){
    var ix = +imgs[n].getAttribute('data-img');
    if(IMAGES[ix]) imgs[n].src = IMAGES[ix];
  }

  // Click-to-enlarge. Opens a full-screen overlay you can zoom and pan, so the
  // small labels on the maps are actually readable.
  (function(){
    var box=document.createElement('div'); box.id='lightbox';
    var im=document.createElement('img'); im.alt='';
    var closeBtn=document.createElement('button'); closeBtn.id='lb-close';
    closeBtn.innerHTML='×'; closeBtn.setAttribute('aria-label','Close');
    var hint=document.createElement('div'); hint.id='lb-hint';
    box.appendChild(im); box.appendChild(closeBtn); box.appendChild(hint);
    document.body.appendChild(box);

    var scale=1,minScale=1,tx=0,ty=0,natW=0,natH=0;
    var dragging=false,sx=0,sy=0,moved=false;

    function apply(){
      im.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';
    }
    function fit(){
      var vw=window.innerWidth,vh=window.innerHeight;
      if(!natW||!natH) return;
      minScale=Math.min(vw/natW,vh/natH,1);
      scale=minScale;
      tx=(vw-natW*scale)/2; ty=(vh-natH*scale)/2;
      apply();
    }
    function updHint(){
      hint.textContent=Math.round(scale*100)+'%  ·  scroll to zoom, drag to '+
        'pan, double-click to reset, Esc to close';
    }
    function zoomAt(cx,cy,factor){
      var ns=Math.max(minScale,Math.min(scale*factor,8));
      if(ns===scale) return;
      tx=cx-(cx-tx)*(ns/scale); ty=cy-(cy-ty)*(ns/scale);
      scale=ns; apply(); updHint();
    }
    function open(src){
      im.src=src;
      var probe=new Image();
      probe.onload=function(){
        natW=probe.naturalWidth; natH=probe.naturalHeight;
        box.classList.add('open'); fit(); updHint();
      };
      probe.src=src;
    }
    function shut(){ box.classList.remove('open'); im.src=''; }

    document.addEventListener('click',function(e){
      var t=e.target;
      if(!t||t.tagName!=='IMG'||box.contains(t)) return;
      if(!t.closest||!t.closest('.page-body,figure,.avatar,.portrait')) return;
      e.preventDefault(); open(t.currentSrc||t.src);
    });
    closeBtn.addEventListener('click',function(e){ e.stopPropagation(); shut(); });
    box.addEventListener('click',function(e){
      if(e.target===closeBtn) return;
      if(moved){ moved=false; return; }
      shut();
    });
    box.addEventListener('wheel',function(e){
      e.preventDefault();
      zoomAt(e.clientX,e.clientY,e.deltaY<0?1.15:1/1.15);
    },{passive:false});
    box.addEventListener('dblclick',function(e){
      e.preventDefault();
      if(scale>minScale*1.05){ fit(); updHint(); }
      else zoomAt(e.clientX,e.clientY,3);
    });
    box.addEventListener('pointerdown',function(e){
      if(e.target===closeBtn) return;
      dragging=true; moved=false; sx=e.clientX-tx; sy=e.clientY-ty;
      box.classList.add('grabbing');
      try{ box.setPointerCapture(e.pointerId); }catch(err){}
    });
    box.addEventListener('pointermove',function(e){
      if(!dragging) return;
      tx=e.clientX-sx; ty=e.clientY-sy;
      if(Math.abs(e.movementX||0)+Math.abs(e.movementY||0)>2) moved=true;
      apply();
    });
    box.addEventListener('pointerup',function(){
      dragging=false; box.classList.remove('grabbing');
    });
    window.addEventListener('keydown',function(e){
      if(!box.classList.contains('open')) return;
      if(e.key==='Escape'){ shut(); }
      else if(e.key==='+'||e.key==='='){ zoomAt(innerWidth/2,innerHeight/2,1.3); }
      else if(e.key==='-'){ zoomAt(innerWidth/2,innerHeight/2,1/1.3); }
      else if(e.key==='0'){ fit(); updHint(); }
    });
    window.addEventListener('resize',function(){
      if(box.classList.contains('open')) fit();
    });
  })();
})();
"""


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------

def build():
    base = Path(__file__).parent
    content_dir = base / CONTENT_DIR
    if not content_dir.is_dir():
        print(f"Content folder not found: {content_dir}")
        return

    pages = load_pages(content_dir)
    if not pages:
        print("No .md pages found.")
        return
    resolver = build_resolver(pages)
    by_id = render_pages(pages, resolver)

    # Group + order pages per section. A section appears if it has pages OR an
    # explicit `_section.md` intro (lets empty sections like Items show up ready).
    pages_by_section = {}
    for key, _ in SECTIONS:
        plist = [p for p in pages if p.section == key]
        plist.sort(key=page_sort_key)
        if plist or (content_dir / key / "_section.md").exists():
            pages_by_section[key] = plist

    ordered = [p for key, _ in SECTIONS for p in pages_by_section.get(key, [])]

    sidebar = sidebar_html(pages_by_section, resolver)
    section_overviews = [
        (f"section-{key}", section_overview_html(key, label, pages_by_section[key],
                                                 resolver, content_dir))
        for key, label in SECTIONS if key in pages_by_section
    ]
    page_html = (
        home_html(resolver, content_dir) + "\n"
        + "\n".join(htm for _, htm in section_overviews) + "\n"
        + "\n".join(page_section_html(p, by_id, resolver) for p in ordered)
    )

    # Search index + JS.
    search_index = "[" + ",".join(
        "{{\"id\":\"{id}\",\"title\":\"{t}\",\"type\":\"{ty}\",\"text\":\"{tx}\"}}".format(
            id=p.id,
            t=p.title.replace("\\", "\\\\").replace('"', '\\"'),
            ty=type_label(p),
            tx=plain_text(p.body)[:600].lower().replace("\\", "\\\\").replace('"', '\\"'),
        ) for p in ordered
    ) + "]"
    valid_ids = ["home"] + [sid for sid, _ in section_overviews] + [p.id for p in ordered]

    # Hover-preview data: type, title, short summary per page.
    previews = {
        p.id: {
            "title": p.title,
            "type": type_label(p),
            "summary": (p.summary or plain_text(p.body)[:180]).strip(),
        }
        for p in ordered
    }
    previews_json = json.dumps(previews, ensure_ascii=False)

    # Image array (each unique image once) - must be after page_html is built
    # so every <img data-img> has been registered.
    images_json = json.dumps(_img_registry)

    js = (JS_TEMPLATE
          .replace("__SEARCH_INDEX__", search_index)
          .replace("__VALID_IDS__", repr(valid_ids))
          .replace("__PREVIEWS__", previews_json)
          .replace("__IMAGES__", images_json))

    out = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(SITE_TITLE)} - {html.escape(SITE_SUBTITLE)}</title>\n"
        "<style>\n" + CSS + "\n</style>\n</head>\n<body>\n"
        '<aside class="sidebar">\n'
        f'<a class="brand" href="#home">{html.escape(SITE_TITLE)}</a>\n'
        f'<div class="brand-sub">{html.escape(SITE_SUBTITLE)}</div>\n'
        '<div class="search-wrap"><input id="search" type="search" '
        'placeholder="Search people, places, events…" autocomplete="off">'
        '<ul id="results"></ul></div>\n'
        f"{sidebar}\n</aside>\n"
        f'<main class="content">\n{page_html}\n</main>\n'
        '<div id="preview"></div>\n'
        "<script>" + js + "</script>\n</body>\n</html>\n"
    )

    out_path = base / OUTPUT_FILE
    out_path.write_text(out, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"Built {OUTPUT_FILE} ({size_kb:.0f} KB) - {len(ordered)} pages")
    for key, label in SECTIONS:
        n = len(pages_by_section.get(key, []))
        if n:
            print(f"  {label:<12} {n}")
    print("\nOpen it in any browser. Search + cross-links + backlinks work offline.")


if __name__ == "__main__":
    build()
