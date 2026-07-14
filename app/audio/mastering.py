from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass(slots=True)
class MasteringSettings:
    target_peak: float = 0.95
    trim_silence: bool = True
    silence_threshold: float = 0.005
    padding_seconds: float = 0.08


class AudioMasteringService:
    def process_file(self, input_path: Path, output_path: Path, settings: MasteringSettings | None = None) -> None:
        settings = settings or MasteringSettings()
        audio, sample_rate = sf.read(input_path, always_2d=False)
        processed = self.process_audio(audio, sample_rate, settings)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, processed, sample_rate)

    def process_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
        settings: MasteringSettings | None = None,
    ) -> np.ndarray:
        settings = settings or MasteringSettings()
        processed = audio.astype(np.float32, copy=True)
        if settings.trim_silence:
            processed = self._trim_silence(processed, sample_rate, settings)
        return self._normalize_peak(processed, settings.target_peak)

    def _normalize_peak(self, audio: np.ndarray, target_peak: float) -> np.ndarray:
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak <= 0:
            return audio
        return np.clip(audio / peak * target_peak, -1.0, 1.0)

    def _trim_silence(self, audio: np.ndarray, sample_rate: int, settings: MasteringSettings) -> np.ndarray:
        if audio.size == 0:
            return audio
        mono = np.max(np.abs(audio), axis=1) if audio.ndim > 1 else np.abs(audio)
        non_silent = np.flatnonzero(mono > settings.silence_threshold)
        if non_silent.size == 0:
            return audio
        padding = int(settings.padding_seconds * sample_rate)
        start = max(int(non_silent[0]) - padding, 0)
        end = min(int(non_silent[-1]) + padding + 1, audio.shape[0])
        return audio[start:end]
