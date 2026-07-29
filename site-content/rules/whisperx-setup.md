---
type: rule
name: WhisperX - Full Setup
label: Guide
group: For the Archivist
order: 2
summary: One-time, from-scratch install of WhisperX - including the Hugging Face account, model permission, and access token.
---

# WhisperX - Full Setup

A complete, do-it-once walkthrough for getting WhisperX working, written for
someone who hasn't done it before. After this, see
[Producing the Transcript](#rules-producing-the-transcript) for the per-session
commands.

> **Contains no secrets.** Where a token is needed you create your **own** free
> one (Step 6) and keep it private - never paste it into these files or commit it.

## What you need

- **Windows** (these commands are Windows/Anaconda style) with **Anaconda or
  Miniconda** installed.
- Ideally an **NVIDIA GPU** - a 3-hour session transcribes in ~20–40 min on GPU.
  No NVIDIA GPU? It still works on CPU, just much slower (hours), and you'd drop
  the `--device cuda` flag.
- A free **Hugging Face** account (Step 6).

If you don't have Miniconda yet: install it from the official Miniconda page,
then open the **"Anaconda Prompt"** from the Start menu for all steps below
(use that, not PowerShell - the `^` line-continuation is cmd syntax).

## 1. Create an isolated environment

```
conda create -n whisperx311 python=3.11 -y
conda activate whisperx311
python -m pip install -U pip
```

## 2. Install PyTorch + CUDA

WhisperX 3.8.0 expects PyTorch ~2.8. Install the matched trio:

```
pip install --index-url https://download.pytorch.org/whl/cu128 ^
  torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128
```

Check it sees your GPU (should print a version and `cuda? True`):

```
python -c "import torch; print(torch.__version__); print('cuda?', torch.cuda.is_available())"
```

*(No NVIDIA GPU? Install plain `pip install torch torchvision torchaudio`
instead; `cuda?` will say False and you'll run on CPU.)*

## 3. Install WhisperX

```
pip install whisperx==3.8.0
```

## 4. Install FFmpeg inside the environment

Doing this inside the env avoids a `WinError 2` later:

```
conda install -c conda-forge "ffmpeg<8" -y
ffmpeg -version
```

## 5. (Only if you hit a DLL error)

If a Windows popup mentions `libtorchcodec_core*.dll`:

```
python -m pip uninstall -y torchcodec
python -m pip install torchcodec==0.7.0
python -c "import torchcodec; print('torchcodec ok')"
```

## 6. Hugging Face - account, permission, and token

Speaker diarization (the part that adds `[SPEAKER_00]` labels) downloads a
**gated** model, so you need a free account and a one-time permission grant:

1. Make a free account at huggingface.co and sign in.
2. Visit the **pyannote speaker-diarization** model page (the exact name WhisperX
   prints in its error if you skip this - currently
   `pyannote/speaker-diarization-community-1`) and click **Agree / Request
   access**. Approval is usually instant.
3. Create a token: **Settings → Access Tokens → New token → type: Read**. Copy it.
4. Back in the Anaconda Prompt, log in and paste the token when asked:

   ```
   huggingface-cli login
   ```

   When it asks *"Add token as git credential? (Y/n)"* answer **`n`**.

**Keep this token private.** It's tied to your account - don't share it, commit
it, or put it in any campaign file.

## 7. Test it

Grab any short audio clip and run:

```
python -m whisperx "clip.wav" --device cuda --model small --language en ^
  --diarize --min_speakers 2 --max_speakers 4 --output_format all --output_dir "."
```

If you get output files containing `SPEAKER_00`, `SPEAKER_01`, … it works. You're
ready to do real sessions - see [Producing the Transcript](#rules-producing-the-transcript).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `module not found whisperx` | Wrong env - run `conda activate whisperx311` |
| `403 / gated repo` on diarize | You skipped Step 6.2 (accept model terms) or aren't logged in |
| `CUDA out of memory` | Use `--model small`, or `--device cpu` |
| `WinError 2 ffmpeg` | FFmpeg not in the env - redo Step 4 |
| `libtorchcodec_core*.dll` popup | Do Step 5 |
| Output extension error | The output filename must end in `.wav`, not `.mp3` |
