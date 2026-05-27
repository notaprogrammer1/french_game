import random
import unicodedata
from typing import Iterable, Sequence


def normalize(text: str) -> str:
    """Normalize user input while preserving accents."""
    return " ".join(text.strip().lower().split())


def strip_accents(text: str) -> str:
    """Remove accent marks so we can detect 'almost' answers."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def loose_equal(answer: str, expected: str) -> bool:
    """Exact-ish comparison for terminal input."""
    return normalize(answer) == normalize(expected)


def accent_insensitive_equal(answer: str, expected: str) -> bool:
    """True if only accents/case/spacing differ."""
    return strip_accents(normalize(answer)) == strip_accents(normalize(expected))


def choose(items: Iterable):
    """Small wrapper for testability/readability."""
    return random.choice(list(items))


def shuffled(items: Iterable[str]) -> list[str]:
    items = list(items)
    random.shuffle(items)
    return items


def join_or(values: list[str]) -> str:
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} or {values[1]}"
    return ", ".join(values[:-1]) + f", or {values[-1]}"


def level_filter(cards: Sequence[dict], active_level: int) -> list[dict]:
    """Return cards up to and including active_level."""
    return [card for card in cards if card.get("level", 1) <= active_level]


def all_card_ids(cards: Sequence[dict]) -> set[str]:
    return {card["id"] for card in cards}
