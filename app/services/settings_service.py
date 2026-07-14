from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.settings import SynthesisSettings
from app.utils.paths import CONFIG_DIR


class SettingsService:
    def __init__(self, settings_path: Path | None = None) -> None:
        self.settings_path = settings_path or CONFIG_DIR / "settings.json"

    def load(self) -> SynthesisSettings:
        if not self.settings_path.exists():
            return SynthesisSettings()
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return SynthesisSettings()
        if not isinstance(data, dict):
            return SynthesisSettings()
        return SynthesisSettings.from_dict(data)

    def save(self, settings: SynthesisSettings) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = settings.to_dict()
        self.settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
