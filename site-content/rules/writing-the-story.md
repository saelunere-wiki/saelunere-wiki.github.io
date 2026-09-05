---
type: rule
name: Writing the Story
label: Guide
group: For the Archivist
order: 5
summary: How to write an episode's Story chapter - narrative prose, no dice, readable as a book.
---

# Writing the Story

The Story (`sessions/episode-NN/episode-NN-story.md`) is the **narrative chapter** -
written so someone who wasn't at the table can read it like a book. It is optional
and made after the Summary.

First read [Canon & Discipline](#rules-canon-and-discipline) - those rules apply in
full, especially the per-scene presence ledger and citing every line of dialogue.

> The Summary is the record. **The Story is not a record, and should not try to be
> one.** Nobody needs to read it to know what happened in a session. It exists to
> be enjoyed, by the table and by anyone the table shares it with.

## Voice

- **Third person, past tense**, staying close to one point of view per scene
  (usually whoever is acting most).
- **Even, readable cadence** - what a competent novelist would do with the
  material. Scene-paced and dialogue-driven, not purple.
- Section breaks with `---` only; no headings inside the chapter.
- For the chosen tone / author palette, see [Style & Voice](#rules-style-and-voice).

## The house style, in six rules

Settled over Episode 1, mostly by getting them wrong first.

1. **Report, don't comment.** The narrator says what happened and what it looked
   like. It does not tell the reader how to feel about it, and it never explains
   a joke or a moment after landing it. If a line needs a sentence afterwards
   saying why it mattered, the line is not working yet.
2. **Feeling is carried by behaviour, not by adjectives.** Not *she was
   devastated*. She keeps her hands where they are, because as long as they are
   there she does not have to look at what is under them.
3. **No punchline beats.** A short flat sentence on its own line is powerful and
   should be spent about twice a chapter, on the facts that deserve it. Used
   every page it becomes a tic and the prose starts performing.
4. **Describe people when they arrive**, briefly, from what their player actually
   said at the table. Height, colour, horns, what they are wearing, how they move
   through a crowd. Two or three specifics, not an inventory.
5. **Nobody says a name they could not know.** Narration may use names throughout,
   so the reader can follow. Characters may not, until they have been introduced
   in the fiction.
6. **No borrowed vocabulary.** Do not lift terminology from other fantasy series
   for spellcasting or anything else. If a word feels satisfyingly genre, check
   whether it came from somebody else's books.

## Magic

**Describe the spell in the prose. Name it in a footnote.**

The prose says what a person saw: *a blade of fire*, *a charm*, *a layer of
thickened air*. It does not print the rulebook name mid-sentence, because nobody
in Parvo talks that way and it breaks the spell, so to speak.

The name and a short explanation go in an inline footnote, written `^[...]`:

```markdown
Felix drew a blade of fire out of nothing^[**Flame Blade.** A sword of fire
summoned into the hand and held there. It cuts and it burns, it throws light
like a torch, and it lasts as long as the caster keeps hold of it.]
```

Footnotes describe **what the working does and looks like**. They do not make
claims about the world - whether a spell is legal, common, restricted or watched
is setting canon and belongs to the GM.

If a spell was never named on tape, leave it unnamed and say so. Two in Episode 1
are unnamed for exactly this reason.

## No mechanics - outcomes only

The dice never appear in the prose. Translate every roll into what happened:

- ❌ *She rolled a 19 on the lock.* → ✅ *The lock gave on the second try.*
- ❌ *He failed the hide check.* → ✅ *He held his breath. They saw him anyway.*

**Banned in story prose:** *rolled*, *natural 20 / nat 20*, *DC*, *check*,
*modifier*, *advantage / disadvantage*, and any sheet currency (inspiration, fate
points, etc.). In-world money and named items are fine. Grep the draft for these.

## Dialogue & inner thought

- **Dialogue** is lifted from the transcript (trim filler and table chatter), and
  attributed to the **character**, not the player. If you cannot quote it, put it
  in **reported speech** rather than inventing a line and putting quote marks
  round it. Invented dialogue is the single easiest way to make a chapter read as
  machine-written, and other players notice it in their own characters instantly.
- **Inner thought** (italicised) is only allowed when the player said something
  like *"I'm like…"*, *"I think…"*, *"what the fuck"* on tape. No marker → no
  inner thought. Don't invent feelings.
- **Other people's characters** are only ever as deep as their player took them
  out loud. Where a player narrated what their character felt, use it. Where they
  did not, that character stays outside: seen, not entered.
- **Atmosphere** the GM didn't state but didn't contradict is allowed (smell,
  light, weather, body language). Named NPCs and new events are not.

## Length

Match the session. A three-hour episode runs long, and that is fine - the Summary
is there for anyone who wants the short version.

Do not compress the emotional beats to save space. The temptation is to summarise
the quiet parts and spend the words on the fight; it should be the other way
round. In Episode 1 the killing takes a page and a half and the ten minutes
afterwards, four people kneeling round a body not knowing what to do, takes three.

## After-write check

- [ ] Five random spoken lines each trace to the transcript.
- [ ] Presence is right in every scene (cross-check the speaker map).
- [ ] No NPC named who wasn't named on tape.
- [ ] No banned mechanics terms (grep the list above).
- [ ] No spell names in the prose; every one that is named is in a footnote.
- [ ] No character speaks a name they have not been told.
- [ ] No retrofitted dialogue and no sanitised fumbles.
- [ ] No forward knowledge - not even a wink at what happens next session.
- [ ] No invented backstory - every reference traces to a character/world page.
