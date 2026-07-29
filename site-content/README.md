# Campaign Site - Authoring Guide

This folder is the **master source** for your campaign website. You write plain
Markdown here (works great in Obsidian); running `python build_site.py` turns it
into a single self-contained `campaign_site.html` you can email, zip, or host.

## Folder = entity type

Put each note in the folder that matches what it is:

| Folder        | What goes here                                   |
|---------------|--------------------------------------------------|
| `world/`      | Lore, history, overview pages                     |
| `characters/` | Player characters                                 |
| `npcs/`       | Non-player characters (politics, relationships)   |
| `locations/`  | Places - cities, planets, buildings               |
| `factions/`   | Houses, guilds, governments, groups               |
| `items/`      | **Significant items only** - artifacts, plot/named objects (not loot) |
| `sessions/`   | One page per session: what happened               |
| `rules/`      | House rules / homebrew                             |
| `story/`      | Optional narrative/novel chapters                 |

You can leave any folder empty.

**Portraits** show as an avatar in a page's header - set `portrait: name.png`
(image beside the file) in the frontmatter. **Backlinks** appear at the bottom of
every page: *Appears in* lists the sessions that mention it (in order), and
*Mentioned in* lists everything else that links to it.

**Pages are living.** As sessions reveal more, fold new facts into the entity
(not just the session log). A good NPC page grows a `## Relationships` list and a
`## Fun to know` bullet list (quirks, allegiances, likes/dislikes). Only add what
was actually established in play - see the *Updating Entities* guide in `rules/`.

## Frontmatter (the bit at the top between `---` lines)

Optional, but it powers the sidebar, chips, and link resolution:

```markdown
---
type: npc                       # usually auto-detected from the folder
name: Senator Vex               # display name (defaults to the # heading)
aliases: [Vex, The Senator]     # other names that [[link]] to this page
faction: House Auren            # shown as a chip (npc)
status: Senator, loyalist       # shown as a chip (npc / character)
pronouns: she/her               # shown as a chip (optional)
player: Felix                   # character only - "Played by …" chip
parent: Parvo                   # nests this page UNDER another in the sidebar tree
portrait: vex.png               # image next to this file
summary: Ambitious House Auren senator.   # one-liner shown in lists
date: 2026-07-01                # sessions only
session: 1                      # sessions only - controls ordering
---
```

## Nesting pages (towns, districts, taverns…)

Add `parent: <Page Name>` to make a page nest **under** another in the sidebar
tree. This is how locations build up:

- `Parvo` (a city, no parent)
  - `The Stacks` (`parent: Parvo`)
    - `The Rusty Cog Tavern` (`parent: The Stacks`)

So when you collect a lot of detail about one tavern, give it its own file with
`parent:` set to the district (or city) it sits in, and it slots into the tree
automatically. The same works for factions (a sub-guild `parent:` its guild).
Sidebar sections and any branch with children can be collapsed by clicking them.

## Character sheets (optional, off by default)

This site intentionally does **not** show D&D stat blocks (class, HP, AC,
ability scores, skills). Putting everyone's numbers on a shared page means
players can see each other's builds, which spoils the table.

If you ever *do* want them, character sheets can be added later - either as a
collapsible block per character or, more simply, by dropping in an image of the
sheet. For now they're left out on purpose.

## Cross-links - the important part

Link to any other page with double brackets, exactly like Obsidian:

- `[[Governor Thal]]` → links to that NPC, text shows "Governor Thal"
- `[[Governor Thal|Thal]]` → links there but shows "Thal"
- `[[The Ledger Affair]]` → works for any page (location, faction, session…)

Every link is **two-way**: open any page and you'll see a **"Mentioned in"**
list of every other page that links to it. That's how you get
"Ahaa - Vex hated Thal over the Ledger Affair" at a glance.

If a `[[link]]` points at a page that doesn't exist yet, it shows greyed-out -
a reminder to write that note later.

## Build it

```
python build_site.py
```

Output: `campaign_site.html` in the repo root. Open it in any browser.
