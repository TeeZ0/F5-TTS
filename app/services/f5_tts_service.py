from __future__ import annotations

import logging
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.audio.mastering import AudioMasteringService
from app.models.settings import SynthesisRequest
from app.services.import_compat import prepare_f5_tts_import
from app.text.preprocessing import TextPreprocessingPipeline

ProgressCallback = Callable[[int, str], None]


@dataclass(slots=True)
class SynthesisResult:
    output_path: Path
    processed_text: str
    sample_rate: int | None = None


class F5TTSService:
    def __init__(
        self,
        preprocessing_pipeline: TextPreprocessingPipeline | None = None,
        mastering_service: AudioMasteringService | None = None,
    ) -> None:
        self.preprocessing_pipeline = preprocessing_pipeline or TextPreprocessingPipeline()
        self.mastering_service = mastering_service or AudioMasteringService()
        self._engine_by_key: dict[tuple[str, str | None], object] = {}
        self._logger = logging.getLogger(__name__)

    def synthesize(self, request: SynthesisRequest, progress: ProgressCallback | None = None) -> SynthesisResult:
        request.validate()
        progress = progress or self._noop_progress
        progress(5, "Preprocessing text")
        processed_text = self.preprocessing_pipeline.process(request.script, request.settings)

        progress(20, "Loading F5-TTS model")
        engine = self._get_engine(request.settings.model_name, request.settings.device)

        progress(35, "Generating speech")
        temp_output = request.output_path.with_suffix(".tmp.wav")
        engine.infer(
            ref_file=str(request.voice.audio_path),
            ref_text=request.voice.transcript,
            gen_text=processed_text,
            speed=request.settings.speed,
            remove_silence=request.settings.remove_silence,
            file_wave=str(temp_output),
            show_info=self._logger.info,
        )

        progress(90, "Mastering audio")
        self.mastering_service.process_file(temp_output, request.output_path)
        temp_output.unlink(missing_ok=True)
        progress(100, "Complete")
        return SynthesisResult(output_path=request.output_path, processed_text=processed_text)

    def _get_engine(self, model_name: str, device: str | None) -> object:
        key = (model_name, device)
        if key not in self._engine_by_key:
            try:
                prepare_f5_tts_import()
                from f5_tts.api import F5TTS
            except ImportError as exc:
                if shutil.which("f5-tts_infer-cli") is None:
                    msg = (
                        "F5-TTS is not installed. Install the package with `pip install -e .` "
                        "from an F5-TTS checkout or install `f5-tts` in this environment."
                    )
                    raise RuntimeError(msg) from exc
                msg = "The f5_tts Python API could not be imported even though the CLI is available."
                raise RuntimeError(msg) from exc
            self._engine_by_key[key] = F5TTS(model=model_name, device=device)
        return self._engine_by_key[key]

    def _noop_progress(self, value: int, message: str) -> None:
        del value, message
