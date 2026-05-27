from french_phonics_game.data import LEVELS, PATTERNS, WORDS
from french_phonics_game.utils import accent_insensitive_equal, level_filter, strip_accents, normalize


def test_strip_accents():
    assert strip_accents("français") == "francais"
    assert strip_accents("café") == "cafe"


def test_accent_insensitive_equal():
    assert accent_insensitive_equal("francais", "français")
    assert accent_insensitive_equal(" cafe ", "café")


def test_normalize_spacing_and_case():
    assert normalize("  BON   JOUR ") == "bon jour"


def test_levels_are_cumulative():
    level_1_patterns = level_filter(PATTERNS, 1)
    level_2_patterns = level_filter(PATTERNS, 2)
    level_3_patterns = level_filter(PATTERNS, 3)
    assert len(level_1_patterns) < len(level_2_patterns) < len(level_3_patterns)


def test_all_cards_have_valid_levels_and_ids():
    valid = set(LEVELS)
    all_cards = PATTERNS + WORDS
    assert all(card["level"] in valid for card in all_cards)
    assert all(card.get("id") for card in all_cards)
    assert len({card["id"] for card in all_cards}) == len(all_cards)
