from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class VoiceProfile:
    name: str
    directory: Path
    reference_audio: Path
    transcript: str
    settings: dict[str, Any]


class VoiceLibrary:
    def __init__(self, root: Path) -> None:
        self.root = root

    def list_voices(self) -> list[VoiceProfile]:
        if not self.root.exists():
            return []
        voices: list[VoiceProfile] = []
        for directory in sorted(path for path in self.root.iterdir() if path.is_dir()):
            profile = self._load_voice(directory)
            if profile is not None:
                voices.append(profile)
        return voices

    def _load_voice(self, directory: Path) -> VoiceProfile | None:
        metadata_path = directory / "voice.json"
        transcript_path = directory / "transcript.txt"
        reference_path = directory / "reference.wav"
        settings_path = directory / "settings.json"
        if not metadata_path.exists() or not transcript_path.exists() or not reference_path.exists():
            return None
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
        except (OSError, json.JSONDecodeError):
            return None
        name = str(metadata.get("name", directory.name))
        transcript = transcript_path.read_text(encoding="utf-8")
        return VoiceProfile(
            name=name,
            directory=directory,
            reference_audio=reference_path,
            transcript=transcript,
            settings=settings,
        )
