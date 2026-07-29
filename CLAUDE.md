# CLAUDE.md - Saelunere

Project context for AI-assisted sessions on the Saelunere campaign.

## What this is

Our new, big campaign. The goal is a **shareable campaign website** that the
players and DM can browse: a cross-linked world wiki, NPC pages (with
relationships and political standing), per-session "what happened" pages, and
optional story chapters.

## How it's built

- **Master source:** Markdown in `site-content/` (one folder per entity type:
  `world/`, `characters/`, `npcs/`, `locations/`, `factions/`, `sessions/`,
  `story/`). Authoring rules are in `site-content/README.md`.
- **Generator:** `python build_site.py` turns the Markdown into one
  self-contained `campaign_site.html` - sidebar nav, search, `[[wiki-links]]`,
  two-way "Mentioned in" backlinks, and hover-preview cards. No dependencies;
  stdlib Python only.
- **Sharing:** the single HTML file can be emailed/zipped (opens offline by
  double-click) or, later, uploaded to a private host (Cloudflare Pages + Access).

## Conventions

- Link between pages with `[[Page Name]]` or `[[Page Name|display text]]`.
- Give every page a one-line `summary:` in frontmatter - it powers the hover
  card and search result label.
- **Character stat sheets are intentionally left off** the shared site (players
  shouldn't see each other's builds). Can be added later if wanted - see
  `site-content/README.md`.
- **No em dashes** in any written content (chat replies included) - use a
  regular hyphen, a comma, or split into two sentences instead. House style
  preference from the DM; em dashes read as an AI tell.

## Sessions / episodes structure

Each episode is a **folder** under `site-content/sessions/` (e.g. `episode-01/`)
containing:

- `episode-NN.md` - the episode container (date, attendance, in-brief)
- `episode-NN-summary.md` - the scannable "what happened" record (nests under the
  container via `parent:`)
- `episode-NN-story.md` - the optional narrative chapter
- `transcript/` - the raw WhisperX output (not published; just source material)

`site-content/sessions/_template/` holds a copy-me template (folders starting
with `_` are ignored by the builder). See its `HOW_TO_USE.txt`.

## Rules for the archivist (READ BEFORE WRITING)

Before writing any session notes, read the process rules in `site-content/rules/`
(the "For the Archivist" pages) - especially **Canon & Discipline** (the
transcript is the only source of truth; default to omission, never invention).
These render on the site too, so players can see how the archive is made.

## Common task: after a session

1. Copy `sessions/_template/` to `sessions/episode-NN/`, rename the files, and
   drop the WhisperX transcript into its `transcript/` folder.
2. Add/update any NPC, location, or faction pages touched this session - fold in
   newly-revealed allegiances, relationships, status changes, and "fun to know"
   quirks (loves cats, hates coffee…). The wiki is living. See the **Updating
   Entities** guide in `site-content/rules/`.
3. Write the episode Summary (and optionally the Story), linking entities with
   `[[double square brackets]]`.
4. Run `python build_site.py` and share the fresh `campaign_site.html`.
