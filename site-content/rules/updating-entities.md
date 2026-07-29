---
type: rule
name: Updating Entities
label: Guide
group: For the Archivist
order: 6
summary: The wiki is living - after each session, fold newly-revealed facts into the NPC, location, and faction pages.
---

# Updating Entities

A session doesn't only produce a Summary and a Story. It also **teaches us new
things about the people and places** in the world - and those belong on the
relevant entity pages, not buried in a session log.

After writing the session notes, go back through what was revealed and **update
every entity that changed or grew**.

[Canon & Discipline](#rules-canon-and-discipline) still applies: only add what
the transcript actually established. No invention. If it wasn't on tape (or in an
existing canon page), it doesn't go in.

## What to fold into a page

- **Status changes** - alive/dead, promoted, exiled, imprisoned, etc. Update the
  `status:` chip and the prose.
- **Allegiance & politics** - who they back, who they've turned against, where
  they sit in a faction's power struggle.
- **Relationships** - who they trust, owe, love, or hate, **and why**. Link the
  other party by name in double square brackets.
- **Goals & secrets revealed** - what they're after, what the party found out.
- **Quirks & "fun to know" details** - the small, characterful stuff: *hates
  coffee*, *keeps three cats*, *terrified of the Bellows*, *only drinks tea*.
  These make NPCs memorable. Keep them as short bullets.
- Keep the one-line **`summary:`** current too - it's the hover card and search
  blurb.

## Suggested NPC page shape

```markdown
---
type: npc
name: Dean Edmund Whitaker
faction: The College of Arcanographers
status: Dean
summary: Dean of the Arcanographers; cautious academic, no friend of the Council.
---

# Dean Edmund Whitaker

A sentence or two of who he is and how he reads.

## Relationships
- Mentor to [[Player Character]] - took them on as a student
- Wary of [[The City Council]] - thinks the guilds starve research

## Fun to know
- Drinks only tea; loudly distrusts coffee
- Keeps three cats in his study
- Has never once been seen in the Bellows
```

## Don't spoil the table

The site is shared with the players. Keep **GM-only secrets and future plot**
off these pages - only record what the party has actually learned. If something
is for the DM's eyes only, it stays out of the wiki.

## New faces and places

If a session introduces a new NPC, location, faction, or significant item, make a
**new page** for it (see the folder it belongs in), link it from the session, and
give it a `summary:`. Even a two-line stub is worth it - the cross-links and
"Appears in" timeline start working immediately.
