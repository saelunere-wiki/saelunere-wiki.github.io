---
type: rule
name: Writing the Summary
label: Guide
group: For the Archivist
order: 4
summary: How to write an episode's Summary - the scannable record of what happened, for players and the DM.
---

# Writing the Summary

The Summary (`sessions/episode-NN/episode-NN-summary.md`) is a **memory aid for
the people who were at the table**, not a record for someone who wasn't. Reading
a line should be enough to bring the scene back; it does not have to contain the
scene. It is factual, brief, and - unlike the Story - **some mechanics are
allowed** here, within the limits below.

If a bullet is doing work that the transcript already does, cut it. The
transcript holds the detail, the Story holds the texture, and the Summary holds
the shape. It is the shortest of the three.

First read [Canon & Discipline](#rules-canon-and-discipline) - those rules apply.

## Format

```markdown
# Episode N - [Title]

- **Date played:** [in-world or real date]
- **In attendance:** [characters present]
- **In brief:** [one sentence]

## Key events

- **[Beat]** - 1–3 sentences: who, what, outcome. Mechanics fine if relevant.
- ...

## NPCs, locations, factions

- [[Name]] - what happened with them this session

## Loot, contacts, consequences

- [acquired item / new contact / debt / reveal]

## Threads to follow

- [unresolved hook introduced this session]
```

## Rules

- **Link every entity** you mention (NPC, place, faction, item) using double
  square brackets around its name - that's what makes it show up under "Appears
  in" on that entity's page and builds the cross-referenced wiki.
- **Mechanics, but only where the mechanic is the memory.** A **natural 20 or a
  natural 1** is a table event people quote back at each other for weeks, so name
  it. *"+2 standing with the Porters"* is fine. **Never damage numbers, distances,
  hit points or check totals** - that is bookkeeping, and it appears nowhere in
  Episodes 1 or 2.
- **Compress combat hardest of all.** Who fought, who went down, who won, and
  what changed as a result. Never the turn order. A fight that took ninety
  minutes at the table is three or four bullets.
- **Indent a bullet** to hang a consequence under the event that caused it, or to
  set out a long piece of testimony. Nested bullets render as a nested list.
- **Names only from the transcript.** Unnamed NPCs stay as roles.
- **Brief.** Bullets, not paragraphs. **1200-1600 words** for a session. If a
  draft comes out longer, the fix is almost always merging rather than deleting:
  a character's whole evening is one or two bullets, not a scene of its own. If
  you're writing flowing prose, staging a moment, or arranging sentences for
  effect, that belongs in the Story instead.
- **Don't say it twice.** The closing sections are for what Key events could not
  carry. If an NPC line or a consequence just restates a bullet from above, cut
  it to the part that is new.
- **It is a list, not an account.** Describe nothing unless the description is
  itself the fact. *"He walked out through the wall two storeys up"* is the
  fact. *"crossed to the window Billiam was clinging to, staying level in the
  air"* is the Story doing its job on the Summary's page. When a bullet has a
  second sentence, check whether it is carrying information or scenery.
- **Put a horizontal rule** between Key events and the closing sections, so it
  is obvious where the account of the session stops and the reference lists
  start.

## After-write check

- [ ] Every event traces to the transcript (a quote or a timestamp).
- [ ] Every named NPC/item actually appears in the transcript.
- [ ] "In attendance" matches the speaker map - no one added who wasn't there.
- [ ] Entities are linked with double square brackets.
- [ ] No invented loot, contacts, or threads.
- [ ] No damage numbers, distances or check totals.
- [ ] Nothing staged for effect. Read the combat bullets back and cut any
      sentence that exists for its rhythm rather than its content.
