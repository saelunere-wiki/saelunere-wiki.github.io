EPISODE 5 - RAW TRANSCRIPT
==========================

Played 20 September 2026. Three hours forty-three minutes.

WhisperX output from the session recording, with speaker diarisation.

FILES
-----
  episode-05.txt      the readable transcript, one line per utterance,
                      prefixed with the speaker tag. Start here.
  episode-05.srt      the same content with timestamps, so it can be played
                      alongside the audio in any media player
  episode-05.vtt      the same again in WebVTT, for browser players
  episode-05.tsv      start/end milliseconds and text, for scripting
  episode-05.json     word-level timings. Large, and only useful if you are
                      doing something programmatic with it.
  speaker_map.json    which SPEAKER_NN tag belongs to which person

Source material. None of this is published to the website: the site builder
only reads .md files, so everything in this folder lives in the repository
only. The word-level .json, the .vtt and the .tsv are deliberately not
committed; the .json alone is over 6 MB.

THREE THINGS TO KNOW BEFORE YOU TRUST IT
----------------------------------------
1. SOME LINES ARE REDACTED OR MUTED. This episode was recovered from the Twitch
   VOD rather than a local recording, so it contains Aeska's player talking to
   stream chat as well as to the table.

     - Two lines where someone said a real name out of character now carry that
       person's CHARACTER name in square brackets instead.
     - Twelve lines of chat interaction read "[stream chat, muted]". The table's
       own conversation running through the same stretch is untouched.

   Nothing else has been altered, in any of these files.

2. THE DIARISATION IS GOOD THIS TIME. Six tags, one per person, and no bin tag.
   It is still not perfect and swaps speakers here and there, but it is a lot
   more reliable than Episodes 3 and 4.

   WhisperX still mangles proper nouns. In this episode: "Larc" and "Lak" are
   Lark; "Kaldor", "Goldor" and "Colder" are Calder; "Asuka", "Asker", "Oscar",
   "Asko" and "Escavalan" are Aeska; "Kirsten" and "Quinton" are Krimson;
   "Claringbones", "Claringburns" and "Clarenode" are Claringbold's Yard;
   "Porteous" and "Portis" are the Porter's Guild; "Korite Guild" is the
   Corewright's Association; "Fixfield" and "Vexfield" are Fexfield;
   "Scrapnel" and "Shrepto" are Shrapnel; "Parvozzi" is Pavosi; "Plum", "Pum"
   and "Bub" are the Plumb and Bob. "Kyle" in one line is Calder, and "Lou" in
   another is not a person at all.

3. THE SPEAKER MAP IS PER-EPISODE. WhisperX assigns SPEAKER_00, SPEAKER_01 and
   so on in the order it happens to find voices, so the numbering is different
   in every episode and carries no meaning across them. Always read the
   speaker_map.json sitting next to the transcript you are using.

4. ONE TRANSCRIPTION LOOP. At around the 25 minute mark the model loses the
   thread and repeats the word "Horace." for 44 lines, covering 27 seconds of
   audio. This is a known WhisperX failure on crosstalk or quiet passages, not a
   corrupt file. What is lost is the greeting between Billy and the two workers
   at the yard; the substance either side of it is intact. Note also that
   "Horace" and "Hollis" are the same man, introduced under both names in the
   same breath.

The transcript is the only source of truth for what happened in a session.
That still holds. Just read it knowing the labels are approximate even where
the words are not.
