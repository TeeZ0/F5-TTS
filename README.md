# F5Narrator

F5Narrator is a local-first Windows desktop narration studio built around F5-TTS. It provides a PySide6 interface for loading a reference voice, entering the reference transcript, pasting a script, generating narration, previewing playback, and exporting WAV audio.

The codebase is intentionally modular so later phases can add Whisper transcription, voice libraries, project management, batch queues, richer Czech normalization, and professional mastering without rewriting the MVP.

## MVP features

- Load a reference `.wav`
- Enter the transcript for that reference voice sample
- Paste a synthesis script
- Split text by sentence or paragraph
- Adjust speaking speed
- Choose calm, neutral, or dramatic pacing
- Generate speech with `f5_tts.api.F5TTS`
- Keep the UI responsive with a `QRunnable` worker
- Preview playback in the app
- Save WAV output
- Persist settings in `config/settings.json`
- Load reusable voices from `voices/<VoiceName>/`

## Architecture

```text
F5Narrator/
├── app/
│   ├── ui/          # PySide6 windows, widgets, and theme
│   ├── models/      # Typed domain models and settings
│   ├── audio/       # Playback and mastering helpers
│   ├── text/        # Preprocessing and normalization pipeline
│   ├── workers/     # Threaded synthesis and future job queues
│   ├── voices/      # Voice library loading
│   ├── services/    # F5-TTS and settings services
│   └── utils/       # Paths and logging
├── cache/
├── config/
├── exports/
├── projects/
├── tests/
├── assets/
├── main.py
├── requirements.txt
└── README.md
```

## Windows setup

1. Install Python 3.12.10 or newer. Earlier Python 3.12 patch releases can
   crash while F5-TTS imports `six` through PySide6/Shiboken on Windows.
2. Install FFmpeg and ensure `ffmpeg.exe` is on `PATH`.
3. Install a CUDA-compatible PyTorch build if you have an NVIDIA GPU.
4. Create and activate a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python --version
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   Confirm that `python --version` reports `Python 3.12.10` or newer.

5. Launch the app:

   ```powershell
   python main.py
   ```

The first generation downloads the F5-TTS model checkpoint locally. No cloud service is used for inference.

## Using the MVP

1. Click **Browse...** and select a short reference WAV. F5-TTS works best with a sample under 12 seconds and a small silence at the end.
2. Paste the exact transcript of the reference audio.
3. Paste the narration script.
4. Select split mode, speaking speed, and emotion.
5. Click **Generate**.
6. Click **Play** to preview.
7. Click **Save** to export the generated WAV.

Generated files are also written to `exports/`.

## Voice library format

Create a folder under `voices/`:

```text
voices/
└── Narrator/
    ├── voice.json
    ├── reference.wav
    ├── transcript.txt
    └── settings.json
```

Example `voice.json`:

```json
{
  "name": "Narrator"
}
```

`settings.json` is optional and reserved for future per-voice defaults.

## Text preprocessing

The pipeline currently includes:

- whitespace cleanup
- Czech normalization for common speeds, years, times, decimals, and acronyms
- sentence/paragraph splitting with simple pacing rules

The pipeline is implemented in `app/text/preprocessing.py`; add new processors by implementing a `process(text, settings)` method and registering it with `TextPreprocessingPipeline`.

## Tests and lint

```bash
python -m pytest
python -m ruff check .
```

## Roadmap

- Whisper Large-v3 transcript autofill
- Segment-level regeneration for long scripts
- MP3/FLAC export via FFmpeg
- loudness normalization, EQ, compression, limiting, and noise-floor control
- live waveform and utilization monitors
- project autosave/reopen
- Markdown batch mode with a persistent queue
