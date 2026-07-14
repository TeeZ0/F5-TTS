from __future__ import annotations

from app.models.settings import SplitMode, SynthesisSettings
from app.text.preprocessing import CzechTextNormalizer, TextPreprocessingPipeline, split_text


def test_czech_normalizer_handles_common_narration_patterns() -> None:
    normalizer = CzechTextNormalizer.default()
    text = normalizer.process("BMW M3 jede 100 km/h v roce 2026 v 15:30 a má 3.14.", SynthesisSettings())

    assert "bé em vé M tři" in text
    assert "sto kilometrů za hodinu" in text
    assert "dva tisíce dvacet šest" in text
    assert "patnáct třicet" in text
    assert "tři celá jedna čtyři" in text


def test_pipeline_splits_sentences_and_long_phrases() -> None:
    pipeline = TextPreprocessingPipeline()
    processed = pipeline.process(
        "Ahoj dneska se podíváme na EV6 GT, který je rychlý, tichý a překvapivě praktický. Myslím, že vás překvapí.",
        SynthesisSettings(split_mode=SplitMode.SENTENCES),
    )

    assert "Ahoj dneska" in processed
    assert "Myslím" in processed
    assert "\n" in processed


def test_paragraph_split_preserves_paragraph_boundaries() -> None:
    chunks = split_text("První odstavec.\n\nDruhý odstavec.", SplitMode.PARAGRAPHS)

    assert chunks == ["První odstavec.", "Druhý odstavec."]
