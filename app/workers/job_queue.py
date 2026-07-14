from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from app.models.settings import SynthesisSettings, VoiceReference


@dataclass(slots=True)
class NarrationJob:
    script_path: Path
    output_path: Path
    voice: VoiceReference
    settings: SynthesisSettings
    job_id: str = field(default_factory=lambda: uuid4().hex)


class JobQueue:
    def __init__(self) -> None:
        self._jobs: deque[NarrationJob] = deque()

    def add(self, job: NarrationJob) -> None:
        self._jobs.append(job)

    def next(self) -> NarrationJob | None:
        if not self._jobs:
            return None
        return self._jobs.popleft()

    def __len__(self) -> int:
        return len(self._jobs)
