EPISODE 6 - RAW TRANSCRIPT
==========================

Played 25 September 2026. Three hours twenty-seven minutes.

WhisperX output from the session recording, with speaker diarisation.

FILES
-----
  episode-06.txt      the readable transcript, one line per utterance,
                      prefixed with the speaker tag. Start here.
  episode-06.srt      the same content with timestamps, so it can be played
                      alongside the audio in any media player
  episode-06.vtt      the same again in WebVTT, for browser players
  episode-06.tsv      start/end milliseconds and text, for scripting
  episode-06.json     word-level timings. Large, and only useful if you are
                      doing something programmatic with it.
  speaker_map.json    which SPEAKER_NN tag belongs to which person

Source material. None of this is published to the website: the site builder
only reads .md files, so everything in this folder lives in the repository
only. The word-level .json, the .vtt and the .tsv are deliberately not
committed; the .json alone is over 5 MB.

THREE THINGS TO KNOW BEFORE YOU TRUST IT
----------------------------------------
1. ONE LINE IS REDACTED. A player was referred to by their real name once,
   out of character, and that now reads "[Lark]". Nothing else has been
   altered. This one was recorded locally rather than off the stream, so
   unlike Episode 5 there is no chat interaction to mute.

   The first two minutes are pre-game conversation about cartoon dubbing and
   where the word "Uralic" comes from. Left in; it contains nothing private.

2. ONE TAG IS A BIN. SPEAKER_06 is mapped to UNCERTAIN because it is not one
   person: it collects short interjections from several speakers. The other
   six tags are reliable.

   WhisperX mangles proper nouns throughout. In this episode: "Caldera",
   "Kaldor", "Kaldur", "Kolder" and "Carlos" are Calder; "Blark" and "Lach"
   are Lark; "Asger", "Askar" and "Aesca" are Aeska; "Biliam" is Billiam;
   "Quimson" is Krimson; "Sacha" is Sasha Langford; "Eavan" is Evan Langford;
   "Emmeryn" is Emory; "Lucy" and "Lisa" are Lucile Fexfield; "Rourke" and
   "Roque" are Madame Rooke; "Shrepnoy" is Shrapnel; "Steenbund" is Steam Bun;
   "Fixfield" is Fexfield; "Wallace" appears where Hollis is meant.

3. THE SPEAKER MAP IS PER-EPISODE. WhisperX assigns SPEAKER_00, SPEAKER_01 and
   so on in the order it happens to find voices, so the numbering is different
   in every episode and carries no meaning across them. Always read the
   speaker_map.json sitting next to the transcript you are using.

The transcript is the only source of truth for what happened in a session.
That still holds. Just read it knowing the labels are approximate even where
the words are not.
