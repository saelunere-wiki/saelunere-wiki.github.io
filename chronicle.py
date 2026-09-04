# -*- coding: utf-8 -*-
"""
chronicle.py  --  the day-by-day Chronicle: parser, renderer, stylesheet.

The Chronicle is a running timeline of the campaign as it is played: one node
per in-world day, one or two lines each, starting at Day 1 and growing forward.
It is not the history timeline, which runs backwards into the Theocide.

★ THIS FILE IS THE ONE IMPLEMENTATION, AND IT LIVES HERE ON PURPOSE.

This repository has to build on its own inside GitHub Actions, so the renderer
cannot sit in the DM store and be imported across. It therefore lives here, and
the DM store's `sheet_scripts/gen_chronicle.py` imports it by absolute path -
the same way every other script in that store addresses this clone. One copy of
the calendar maths, so the two wikis cannot disagree about what day it is.

The source is a ```chronicle fence inside a markdown page. A record needs a date
and a line of text; everything else is derived:

    date: Tide 01, 756
    episode: 2                 (optional -- "2-3" if two sessions played the day)
    status: open               (optional -- the day is not finished in play yet)
    gap: two weeks of downtime (optional -- overrides the auto "N days later")
    text: One or two lines. Shorter is better.
    ---                        (record separator)

Derived, so nobody has to get it right by hand:
  * weekday      -- from the day of the year; day 00 is always Kinsdae
  * festival     -- day 00 of each season
  * season bands -- inserted whenever the season or the year changes
  * gaps         -- any jump of more than one day becomes a zigzag with a label
                    ("2 weeks later" -- an in-world week is TEN days)

Calendar rules (see site-content/world/the-calendar.md):
  400-day year, four 100-day seasons Aela -> Ember -> Terr -> Tide.
  A season runs 01..99 and then CLOSES on day 00, which is its 100th and final
  day and its festival. So Terr 00 = day 300 of the year, Tide 00 = day 400.

Stdlib only.
"""
import re
import html as _html

SEASONS = ["Aela", "Ember", "Terr", "Tide"]
SEASON_OF_YEAR = {"Aela": "Spring", "Ember": "Summer", "Terr": "Autumn", "Tide": "Winter"}
FESTIVAL = {"Aela": "Everbring", "Ember": "Highbreath", "Terr": "Harvestfest", "Tide": "Frostmorn"}
WEEKDAYS = ["Aelsdae", "Ersdae", "Wexdae", "Lumesdae", "Varsdae",
            "Vesdae", "Yunsdae", "Depsdae", "Salsdae", "Kinsdae"]

DATE_RE = re.compile(r"^(Aela|Ember|Terr|Tide)\s+(\d{1,2})\s*,\s*(\d{2,4})$")
FENCE_RE = re.compile(r"```chronicle\s*\n(.*?)\n```", re.S)
WL_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


# ---------------------------------------------------------------- calendar --

def day_of_year(season, day):
    """1..400. Day 00 is the 100th (final) day of its season, not a zero."""
    return SEASONS.index(season) * 100 + (100 if day == 0 else day)


def absolute_day(year, season, day):
    return year * 400 + day_of_year(season, day)


def weekday_of(season, day):
    return WEEKDAYS[(day_of_year(season, day) - 1) % 10]


def gap_label(days):
    """days = the distance between two played days. 1 = consecutive."""
    if days <= 1:
        return None
    if days % 10 == 0:
        n = days // 10
        return "a week later" if n == 1 else "%d weeks later" % n
    return "%d days later" % days


# ------------------------------------------------------------------ parser --

class ChronicleError(Exception):
    pass


def has_chronicle(text):
    return bool(FENCE_RE.search(text))


def parse_chronicle(text):
    """Read the ```chronicle fence out of a markdown page's text.

    Returns a list of dicts, in file order, each carrying the fields as written
    plus the derived season/year/weekday/festival/absolute-day.
    """
    m = FENCE_RE.search(text)
    if not m:
        raise ChronicleError("no ```chronicle block found")

    records = []
    for n, chunk in enumerate(m.group(1).split("\n---"), start=1):
        chunk = chunk.strip()
        if not chunk:
            continue
        rec, key = {}, None
        for line in chunk.split("\n"):
            fm = re.match(r"^([a-z]+):\s*(.*)$", line.strip())
            if fm:
                key = fm.group(1)
                rec[key] = fm.group(2).strip()
            elif key and line.strip():
                rec[key] = (rec[key] + " " + line.strip()).strip()
        if "date" not in rec:
            raise ChronicleError("record %d has no `date:`" % n)
        if not rec.get("text"):
            raise ChronicleError("record %d (%s) has no `text:`" % (n, rec["date"]))

        dm = DATE_RE.match(rec["date"])
        if not dm:
            raise ChronicleError(
                "record %d: date %r is not `Season DD, YYY` "
                "(seasons: %s)" % (n, rec["date"], ", ".join(SEASONS)))
        season, day, year = dm.group(1), int(dm.group(2)), int(dm.group(3))

        rec.update(
            season=season, day=day, year=year,
            daynum="%s %02d" % (season, day),
            weekday=weekday_of(season, day),
            festival=FESTIVAL[season] if day == 0 else None,
            abs=absolute_day(year, season, day),
            open=(rec.get("status", "").lower() == "open"),
        )
        records.append(rec)

    if not records:
        raise ChronicleError("the ```chronicle block is empty")
    for a, b in zip(records, records[1:]):
        if b["abs"] <= a["abs"]:
            raise ChronicleError("%s does not come after %s -- records must be "
                                 "in date order" % (b["date"], a["date"]))
    return records


def lint(records):
    """Soft problems: over-long lines, a misplaced `status: open`.

    Returns a list of strings. Never raises; parse_chronicle already refused
    anything that cannot be rendered.
    """
    out = []
    for r in records:
        plain = WL_RE.sub(lambda m: (m.group(2) or m.group(1)), r["text"])
        if len(plain) > 230:
            out.append("%s: %d characters. Two lines is the ceiling; cut it."
                       % (r["date"], len(plain)))
    open_days = [r for r in records if r["open"]]
    if len(open_days) > 1:
        out.append("more than one day is `status: open`: %s"
                   % ", ".join(r["date"] for r in open_days))
    elif open_days and open_days[0] is not records[-1]:
        out.append("`status: open` is on %s, which is not the last day"
                   % open_days[0]["date"])
    return out


# ---------------------------------------------------------------- renderer --

def _default_resolve(target, label):
    """No host wiki: [[wikilinks]] render as plain emphasised text."""
    return '<span class="cd-wl">%s</span>' % _html.escape(label)


def inline(text, resolve):
    """Escape the prose, hand the [[wikilinks]] to `resolve` unescaped.

    The order matters: escaping first would feed resolve() an already-escaped
    page title, which then gets escaped a second time by the resolver.
    """
    out, pos = [], 0
    for m in WL_RE.finditer(text):
        out.append(_html.escape(text[pos:m.start()]))
        target = m.group(1).strip()
        out.append(resolve(target, (m.group(2) or target).strip()))
        pos = m.end()
    out.append(_html.escape(text[pos:]))
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", "".join(out))


def _zigzag_svg():
    pts, y = [], 0
    for i in range(7):
        pts.append("%d,%d" % (9 if i % 2 else -9, y))
        y += 9
    return ('<svg class="cg-zig" viewBox="-12 0 24 54" width="24" height="54" '
            'aria-hidden="true" preserveAspectRatio="none">'
            '<polyline points="%s" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linejoin="round"/></svg>' % " ".join(pts))


def render_chronicle(records, resolve=None, episode_href=None):
    """Return the HTML fragment. Both wiki builders drop this straight in.

    resolve(target, label) -> html      how [[wikilinks]] become links
    episode_href(n) -> href or None     where an "Episode N" chip points
    """
    resolve = resolve or _default_resolve
    out = ['<div class="chron">']
    prev = None

    for rec in records:
        # Season / year band whenever either changes.
        if prev is None or (rec["season"], rec["year"]) != (prev["season"], prev["year"]):
            out.append(
                '<div class="chron-band"><span>%s %d <i>%s</i></span></div>'
                % (_html.escape(rec["season"]), rec["year"], SEASON_OF_YEAR[rec["season"]]))

        # Gap, if the last played day was not yesterday.
        if prev is not None:
            label = rec.get("gap") or gap_label(rec["abs"] - prev["abs"])
            if label:
                out.append(
                    '<div class="chron-gap"><div class="cg-rail">%s</div>'
                    '<div class="cg-label">%s</div></div>'
                    % (_zigzag_svg(), _html.escape(label)))

        cls = ["chron-day"]
        if rec["festival"]:
            cls.append("is-festival")
        if rec["open"]:
            cls.append("is-open")

        date_bits = ['<div class="cd-daynum">%s</div>' % _html.escape(rec["daynum"]),
                     '<div class="cd-year">%d</div>' % rec["year"]]
        if rec["festival"]:
            date_bits.append('<div class="cd-festival">%s</div>' % _html.escape(rec["festival"]))
        date_bits.append('<div class="cd-weekday">%s</div>' % _html.escape(rec["weekday"]))

        meta = []
        if rec.get("episode"):
            # "2" -> Episode 2;  "2-3" -> Episodes 2-3 (a day the next session
            # finished, so two episodes cover it).
            word = "Episode" if re.match(r"^\d+$", rec["episode"].strip()) else "Episodes"
            ep = "%s %s" % (word, _html.escape(rec["episode"]))
            href = episode_href(rec["episode"]) if episode_href else None
            meta.append('<a class="cd-ep" href="%s">%s</a>' % (_html.escape(href), ep)
                        if href else '<span class="cd-ep">%s</span>' % ep)
        if rec["open"]:
            meta.append('<span class="cd-open">still unfolding</span>')

        out.append(
            '<div class="%s" id="chron-%s">'
            '<div class="cd-date">%s</div>'
            '<div class="cd-rail"><span class="cd-dot"></span></div>'
            '<div class="cd-body"><p class="cd-text">%s</p>%s</div>'
            '</div>' % (
                " ".join(cls),
                "%s-%02d-%d" % (rec["season"].lower(), rec["day"], rec["year"]),
                "".join(date_bits),
                inline(rec["text"], resolve),
                ('<div class="cd-meta">%s</div>' % "".join(meta)) if meta else "",
            ))
        prev = rec

    out.append('<div class="chron-now">'
               '<span class="cn-label">the story continues</span></div>')
    out.append("</div>")
    return "\n".join(out)


def render_markdown_fence(text, resolve=None, episode_href=None):
    """Swap the ```chronicle fence in `text` for the rendered fragment.

    Returns (before_markdown, fragment_html, after_markdown) so a builder can
    render the prose around it with its own markdown pipeline.
    """
    m = FENCE_RE.search(text)
    if not m:
        return text, "", ""
    records = parse_chronicle(text)
    return (text[:m.start()],
            render_chronicle(records, resolve, episode_href),
            text[m.end():])


# The component inherits the host page's palette: --bg, --text, --muted,
# --rule, --accent, --chip. Both wikis already define all six.
CHRONICLE_CSS = r"""
/* --- The Chronicle: day-by-day timeline ------------------------------- */
.chron{--rail:7.5rem;--railw:2.4rem;margin:1.6rem 0 0}
.chron-day{display:grid;grid-template-columns:var(--rail) var(--railw) 1fr;
  align-items:stretch;position:relative}

.cd-date{text-align:right;padding:.85rem .1rem .85rem 0;line-height:1.25}
.cd-daynum{font-weight:600;font-size:1.02rem;letter-spacing:.01em}
.cd-year{color:var(--muted);font-size:.78rem;letter-spacing:.1em}
.cd-festival{color:var(--accent);font-size:.8rem;font-style:italic;margin-top:.15rem}
.cd-weekday{color:var(--muted);font-size:.76rem;text-transform:uppercase;
  letter-spacing:.13em;margin-top:.3rem}

.cd-rail{position:relative}
.cd-rail::before{content:"";position:absolute;left:50%;top:0;bottom:0;width:2px;
  transform:translateX(-1px);background:var(--rule)}
.cd-dot{position:absolute;left:50%;top:1.15rem;width:11px;height:11px;
  border-radius:50%;transform:translateX(-50%);background:var(--accent);
  box-shadow:0 0 0 4px var(--bg);z-index:1}
.chron-day.is-festival .cd-dot{width:15px;height:15px;top:1.05rem;
  background:var(--bg);border:3px solid var(--accent)}
.chron-day.is-open .cd-dot{background:var(--bg);border:2px solid var(--accent)}

.cd-body{padding:.85rem 0 1.05rem .95rem}
.cd-text{margin:0;font-size:1.02rem;line-height:1.55}
.cd-wl{border-bottom:1px solid var(--rule)}
.cd-meta{margin-top:.45rem;display:flex;gap:.4rem;flex-wrap:wrap;align-items:center}
.cd-ep{background:var(--chip);color:var(--muted);font-size:.72rem;
  padding:.16rem .55rem;border-radius:999px;text-transform:uppercase;
  letter-spacing:.1em;text-decoration:none;white-space:nowrap}
a.cd-ep:hover{color:var(--accent);text-decoration:none}
.cd-open{color:var(--accent);font-size:.72rem;font-style:italic;
  letter-spacing:.06em;border:1px solid var(--rule);border-radius:999px;
  padding:.16rem .55rem}

.chron-band{display:grid;grid-template-columns:var(--rail) var(--railw) 1fr;
  align-items:center;margin:.2rem 0}
.chron-band span{grid-column:3;padding-left:.95rem;color:var(--muted);
  font-size:.74rem;text-transform:uppercase;letter-spacing:.2em}
.chron-band i{color:var(--accent);font-style:italic;text-transform:none;
  letter-spacing:.02em;font-size:.82rem}
.chron-band::before{content:"";grid-column:2;justify-self:center;width:2px;
  height:1.9rem;background:var(--rule)}

.chron-gap{display:grid;grid-template-columns:var(--rail) var(--railw) 1fr;
  align-items:center;padding:.35rem 0}
.cg-rail{grid-column:2;justify-self:center;color:var(--muted);opacity:.65;
  display:flex}
.cg-label{grid-column:3;padding-left:.95rem;color:var(--muted);font-style:italic;
  font-size:.9rem}

.chron-now{display:grid;grid-template-columns:var(--rail) var(--railw) 1fr;
  align-items:center;height:3.2rem}
.chron-now::before{content:"";grid-column:2;justify-self:center;width:2px;
  height:100%;background:linear-gradient(var(--rule),transparent)}
.cn-label{grid-column:3;padding-left:.95rem;color:var(--muted);font-style:italic;
  font-size:.86rem;opacity:.7}

@media (max-width:620px){
  .chron{--rail:0px;--railw:1.6rem}
  .chron-day{grid-template-columns:var(--railw) 1fr}
  .cd-date{grid-column:2;text-align:left;padding:.85rem 0 0}
  .cd-daynum,.cd-year,.cd-festival,.cd-weekday{display:inline-block;
    margin:0 .5rem 0 0;vertical-align:baseline}
  .cd-weekday{margin-top:0}
  .cd-rail{grid-column:1;grid-row:1 / span 2}
  .cd-body{grid-column:2;padding:.25rem 0 1.05rem}
  .chron-band,.chron-gap,.chron-now{grid-template-columns:var(--railw) 1fr}
  .chron-band span,.cg-label,.cn-label{grid-column:2;padding-left:.8rem}
  .chron-band::before,.chron-now::before,.cg-rail{grid-column:1}
}
"""
