from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from app.models.settings import SynthesisRequest
from app.services.f5_tts_service import F5TTSService, SynthesisResult


class SynthesisSignals(QObject):
    progress = Signal(int, str)
    completed = Signal(object)
    failed = Signal(str, str)


class SynthesisWorker(QRunnable):
    def __init__(self, service: F5TTSService, request: SynthesisRequest) -> None:
        super().__init__()
        self.service = service
        self.request = request
        self.signals = SynthesisSignals()

    @Slot()
    def run(self) -> None:
        try:
            result: SynthesisResult = self.service.synthesize(
                self.request,
                progress=lambda value, message: self.signals.progress.emit(value, message),
            )
        except Exception as exc:
            self.signals.failed.emit(str(exc), traceback.format_exc())
            return
        self.signals.completed.emit(result)
