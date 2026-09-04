EPISODE 3 - RAW TRANSCRIPT
==========================

WhisperX output from the session recording, with speaker diarisation.
Source material. None of this is published to the website: the site builder
only reads .md files, so everything in this folder lives in the repository
only. It is here so that players and the DM can work from the same source
instead of passing files around.

FILES
-----
  episode-03.txt      the readable transcript, one line per utterance,
                      prefixed with the speaker tag
  episode-03.srt      the same content with timestamps, so it can be played
                      alongside the audio in any media player
  speaker_map.json    which SPEAKER_NN tag belongs to which person

The word-level .json and the .vtt are deliberately not committed. The .json
is roughly 5 MB per episode and the .vtt duplicates the .srt.

THREE THINGS TO KNOW BEFORE YOU TRUST IT
----------------------------------------
1. REAL NAMES HAVE BEEN REPLACED. Where someone said a real person's name out
   of character, it has been replaced with that person's CHARACTER name in
   square brackets, e.g. "[Lark]", "[Krimson]", or with a neutral placeholder
   such as "[a friend]" where the person named is not at the table. Five lines
   are affected in this episode. Nothing else has been altered.

2. THE DIARISATION IS WORSE THAN USUAL THIS EPISODE. Two tags, SPEAKER_02 and
   SPEAKER_03, are both mapped to Krimson, and SPEAKER_03 in particular picks
   up lines that belong to Felix and to other players. There are also long
   stretches where a single word is repeated for dozens of lines, which is the
   model looping on background noise rather than anything anyone said. Read
   the speaker tags as a hint, not a fact.

   WhisperX also mangles proper nouns throughout. In this episode: "Kalle",
   "Colbert", "Carter" and "Golda" are Calder; "Mark" and "Larkki" are Lark;
   "Asuka", "Asker", "Eske" and "Escar" are Aeska; "Phelis" is Felix; "Wendy"
   is Annie; "Bugman" is Buckman; "Spernhold" and "Spernholt" are Spurnhold;
   "Shrepnel" is Shrapnel; "Pollenbob" and "Pullman Bob" are the Plumb and Bob;
   "Crimson" and "Grimzin" are Krimson. Check names against the wiki rather
   than copying them out of here.

3. THE SPEAKER MAP IS PER-EPISODE. WhisperX assigns SPEAKER_00, SPEAKER_01 and
   so on in the order it happens to find voices, so the numbering is different
   in every episode and carries no meaning across them. Always read the
   speaker_map.json sitting in the same folder as the transcript you are using.

Per the Canon & Discipline rules, the transcript is the only source of truth
for what happened in a session. That still holds. Just read it knowing the
labels are approximate even where the words are not.
