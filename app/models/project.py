from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class NarrationProject:
    name: str
    root: Path
    script_path: Path
    narration_path: Path
    settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, root: Path, name: str) -> NarrationProject:
        project_root = root / name
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "Voice").mkdir(exist_ok=True)
        (project_root / "Exports").mkdir(exist_ok=True)
        script_path = project_root / "Script.md"
        if not script_path.exists():
            script_path.write_text("", encoding="utf-8")
        return cls(
            name=name,
            root=project_root,
            script_path=script_path,
            narration_path=project_root / "Narration.wav",
        )
