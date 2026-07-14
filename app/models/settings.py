from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class SplitMode(StrEnum):
    SENTENCES = "sentences"
    PARAGRAPHS = "paragraphs"


class Emotion(StrEnum):
    CALM = "calm"
    NEUTRAL = "neutral"
    DRAMATIC = "dramatic"


@dataclass(slots=True)
class SynthesisSettings:
    split_mode: SplitMode = SplitMode.SENTENCES
    speed: float = 1.0
    emotion: Emotion = Emotion.NEUTRAL
    model_name: str = "F5TTS_v1_Base"
    device: str | None = None
    remove_silence: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SynthesisSettings:
        return cls(
            split_mode=SplitMode(data.get("split_mode", SplitMode.SENTENCES.value)),
            speed=float(data.get("speed", 1.0)),
            emotion=Emotion(data.get("emotion", Emotion.NEUTRAL.value)),
            model_name=str(data.get("model_name", "F5TTS_v1_Base")),
            device=data.get("device"),
            remove_silence=bool(data.get("remove_silence", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["split_mode"] = self.split_mode.value
        data["emotion"] = self.emotion.value
        return data


@dataclass(slots=True)
class VoiceReference:
    audio_path: Path
    transcript: str

    def validate(self) -> None:
        if not self.audio_path.exists():
            msg = f"Reference audio does not exist: {self.audio_path}"
            raise FileNotFoundError(msg)
        if self.audio_path.suffix.lower() != ".wav":
            msg = "F5Narrator MVP expects a WAV reference file."
            raise ValueError(msg)
        if not self.transcript.strip():
            msg = "Reference transcript is required for stable voice cloning."
            raise ValueError(msg)


@dataclass(slots=True)
class SynthesisRequest:
    voice: VoiceReference
    script: str
    output_path: Path
    settings: SynthesisSettings

    def validate(self) -> None:
        self.voice.validate()
        if not self.script.strip():
            msg = "Synthesis script cannot be empty."
            raise ValueError(msg)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
