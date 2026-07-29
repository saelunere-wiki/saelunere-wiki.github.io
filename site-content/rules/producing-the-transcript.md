---
type: rule
name: Producing the Transcript
label: Guide
group: For the Archivist
order: 3
summary: How a session recording becomes the speaker-labelled transcript the archivist writes from (WhisperX).
---

# Producing the Transcript

The transcript is the raw material for everything else. It's made with **WhisperX**
(OpenAI Whisper transcription + speaker diarization, which adds the
`[SPEAKER_00]:` labels). This page is the recipe for each session; the one-time
install and Hugging Face token setup are in
[WhisperX — Full Setup](#rules-whisperx-setup).

## Pipeline

1. **Record** the session as audio (`.mp3`, `.m4a`, `.mp4` all fine).
2. **Convert to 16 kHz mono WAV** with FFmpeg (WhisperX works best on this):
   ```
   ffmpeg -i "session.mp3" -vn -ac 1 -ar 16000 -c:a pcm_s16le "session.wav"
   ```
3. **Run WhisperX** with diarization (Windows + NVIDIA GPU example):
   ```
   python -m whisperx "session.wav" --device cuda --model medium --language en ^
     --diarize --min_speakers 5 --max_speakers 10 --output_format all --output_dir "."
   ```
   Set `--min_speakers` to about party size + 1 (for the GM); `--max_speakers` a
   couple higher for guest NPC voices. On CPU it works but is much slower.
4. **Put the output** (the `[SPEAKER_XX]`-labelled `.txt`, plus the `.json`/`.srt`)
   into that episode's `transcript/` folder. The `.txt` is the canonical source.
5. **Map speakers → people** in the episode's notes: read the first few minutes
   (players usually get named early) and record which `SPEAKER_XX` is who. If
   WhisperX splits one person into two speakers, map both to that person; if it
   merges two, rerun with a higher `--min_speakers`.

## The one secret you provide yourself

Diarization downloads a **gated model from Hugging Face**, which needs a free
account:

- Accept the model terms once on the pyannote speaker-diarization model page
  (while logged in to Hugging Face).
- Create a **Read** access token and log in locally with `huggingface-cli login`.
- **Keep this token private. Never commit it or paste it into these files.**

## Common gotchas

| Symptom | Fix |
|---|---|
| `403 / gated repo` during diarization | Accept the pyannote model terms on Hugging Face, then log in |
| `CUDA out of memory` | Use `--model small`, or `--device cpu` |
| `WinError 2 ffmpeg` | Install FFmpeg inside the same environment |
| One person split across several `SPEAKER_XX` | Normal — map them all to the same person |
| Two people merged into one speaker | Rerun with a higher `--min_speakers` |
