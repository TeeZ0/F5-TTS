from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from app.models.settings import Emotion, SplitMode, SynthesisSettings


class TextProcessor(Protocol):
    def process(self, text: str, settings: SynthesisSettings) -> str: ...


@dataclass(slots=True)
class WhitespaceNormalizer:
    def process(self, text: str, settings: SynthesisSettings) -> str:
        del settings
        normalized_lines = [" ".join(line.split()) for line in text.splitlines()]
        return "\n".join(line for line in normalized_lines if line)


@dataclass(slots=True)
class CzechTextNormalizer:
    letter_names: dict[str, str]

    @classmethod
    def default(cls) -> CzechTextNormalizer:
        return cls(
            letter_names={
                "A": "á",
                "B": "bé",
                "C": "cé",
                "D": "dé",
                "E": "é",
                "F": "ef",
                "G": "gé",
                "H": "há",
                "I": "í",
                "J": "jé",
                "K": "ká",
                "L": "el",
                "M": "em",
                "N": "en",
                "O": "ó",
                "P": "pé",
                "Q": "kvé",
                "R": "er",
                "S": "es",
                "T": "té",
                "U": "ú",
                "V": "vé",
                "W": "vé",
                "X": "iks",
                "Y": "ypsilon",
                "Z": "zet",
            }
        )

    def process(self, text: str, settings: SynthesisSettings) -> str:
        del settings
        text = re.sub(r"\b(\d{1,3})\s*km/h\b", self._normalize_speed, text, flags=re.IGNORECASE)
        text = re.sub(r"\b(\d{1,2}):(\d{2})\b", self._normalize_time, text)
        text = re.sub(r"\b(\d+)[,.](\d+)\b", self._normalize_decimal, text)
        text = re.sub(r"\b(19\d{2}|20\d{2})\b", self._normalize_year, text)
        text = re.sub(r"\b([A-ZČŠŽ]{2,})(?:\s+([A-Z]\d))?\b", self._normalize_acronym, text)
        return text

    def _normalize_speed(self, match: re.Match[str]) -> str:
        number = int(match.group(1))
        return f"{_cz_number(number)} kilometrů za hodinu"

    def _normalize_time(self, match: re.Match[str]) -> str:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if minute == 0:
            return f"{_cz_number(hour)} hodin"
        return f"{_cz_number(hour)} {_cz_number(minute)}"

    def _normalize_decimal(self, match: re.Match[str]) -> str:
        left = int(match.group(1))
        right = match.group(2)
        right_words = " ".join(_cz_digit(int(digit)) for digit in right)
        return f"{_cz_number(left)} celá {right_words}"

    def _normalize_year(self, match: re.Match[str]) -> str:
        return _cz_year(int(match.group(1)))

    def _normalize_acronym(self, match: re.Match[str]) -> str:
        acronym = match.group(1)
        model = match.group(2)
        spoken = " ".join(self.letter_names.get(letter, letter.lower()) for letter in acronym)
        if model is None:
            return spoken
        return f"{spoken} {model[0]} {_cz_number(int(model[1:]))}"


@dataclass(slots=True)
class PacingProcessor:
    max_sentence_chars: int = 160

    def process(self, text: str, settings: SynthesisSettings) -> str:
        chunks = split_text(text, settings.split_mode, self.max_sentence_chars)
        separator = "\n\n" if settings.split_mode is SplitMode.PARAGRAPHS else "\n"
        text = separator.join(chunks)
        if settings.emotion is Emotion.DRAMATIC:
            text = re.sub(r"([.!?])\s+", r"\1\n\n", text)
        elif settings.emotion is Emotion.CALM:
            text = text.replace("...", ".")
        return text


class TextPreprocessingPipeline:
    def __init__(self, processors: list[TextProcessor] | None = None) -> None:
        self.processors = processors or [
            WhitespaceNormalizer(),
            CzechTextNormalizer.default(),
            PacingProcessor(),
        ]

    def process(self, text: str, settings: SynthesisSettings) -> str:
        processed = text
        for processor in self.processors:
            processed = processor.process(processed, settings)
        return processed.strip()


def split_text(text: str, split_mode: SplitMode, max_chars: int = 160) -> list[str]:
    if split_mode is SplitMode.PARAGRAPHS:
        raw_chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]
    else:
        raw_chunks = [
            chunk.strip()
            for chunk in re.split(r"(?<=[.!?…])\s+(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ0-9])", text)
            if chunk.strip()
        ]
        if not raw_chunks and text.strip():
            raw_chunks = [text.strip()]

    chunks: list[str] = []
    for chunk in raw_chunks:
        chunks.extend(_split_long_chunk(chunk, max_chars))
    return chunks


def _split_long_chunk(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts = [part.strip() for part in re.split(r"([,;:])", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current}{part}" if part in ",;:" else f"{current} {part}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(_ensure_terminal_punctuation(current))
            current = part
        else:
            current = candidate
    if current:
        chunks.append(_ensure_terminal_punctuation(current))
    return chunks


def _ensure_terminal_punctuation(text: str) -> str:
    if text.endswith((".", "!", "?", "…")):
        return text
    return f"{text}."


def _cz_digit(value: int) -> str:
    digits = {
        0: "nula",
        1: "jedna",
        2: "dva",
        3: "tři",
        4: "čtyři",
        5: "pět",
        6: "šest",
        7: "sedm",
        8: "osm",
        9: "devět",
    }
    return digits[value]


def _cz_number(value: int) -> str:
    if value < 0:
        return f"mínus {_cz_number(abs(value))}"
    ones = {
        0: "nula",
        1: "jedna",
        2: "dva",
        3: "tři",
        4: "čtyři",
        5: "pět",
        6: "šest",
        7: "sedm",
        8: "osm",
        9: "devět",
        10: "deset",
        11: "jedenáct",
        12: "dvanáct",
        13: "třináct",
        14: "čtrnáct",
        15: "patnáct",
        16: "šestnáct",
        17: "sedmnáct",
        18: "osmnáct",
        19: "devatenáct",
    }
    tens = {
        20: "dvacet",
        30: "třicet",
        40: "čtyřicet",
        50: "padesát",
        60: "šedesát",
        70: "sedmdesát",
        80: "osmdesát",
        90: "devadesát",
    }
    hundreds = {
        100: "sto",
        200: "dvě stě",
        300: "tři sta",
        400: "čtyři sta",
        500: "pět set",
        600: "šest set",
        700: "sedm set",
        800: "osm set",
        900: "devět set",
    }
    if value < 20:
        return ones[value]
    if value < 100:
        base = value // 10 * 10
        remainder = value % 10
        return tens[base] if remainder == 0 else f"{tens[base]} {_cz_number(remainder)}"
    if value < 1000:
        base = value // 100 * 100
        remainder = value % 100
        return hundreds[base] if remainder == 0 else f"{hundreds[base]} {_cz_number(remainder)}"
    if value < 1_000_000:
        thousands = value // 1000
        remainder = value % 1000
        prefix = "tisíc" if thousands == 1 else f"{_cz_number(thousands)} tisíc"
        return prefix if remainder == 0 else f"{prefix} {_cz_number(remainder)}"
    return str(value)


def _cz_year(value: int) -> str:
    if 2000 <= value <= 2099:
        remainder = value - 2000
        return "dva tisíce" if remainder == 0 else f"dva tisíce {_cz_number(remainder)}"
    return _cz_number(value)
