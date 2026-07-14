from __future__ import annotations

from app.models.settings import Emotion, SplitMode, SynthesisSettings
from app.services.settings_service import SettingsService


def test_settings_service_round_trips_settings(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"
    service = SettingsService(settings_path)
    settings = SynthesisSettings(split_mode=SplitMode.PARAGRAPHS, speed=1.15, emotion=Emotion.DRAMATIC)

    service.save(settings)
    loaded = service.load()

    assert loaded.split_mode is SplitMode.PARAGRAPHS
    assert loaded.speed == 1.15
    assert loaded.emotion is Emotion.DRAMATIC
