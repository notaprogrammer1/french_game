from french_phonics_game.app import StudySession, ordered_learn_cards
from french_phonics_game.data import PATTERNS, WORDS
from french_phonics_game.utils import level_filter


def test_learn_patterns_are_in_data_order():
    cards = ordered_learn_cards("1", 2)
    expected = level_filter(PATTERNS, 2)
    assert [card["id"] for card in cards] == [card["id"] for card in expected]


def test_learn_words_are_in_data_order():
    cards = ordered_learn_cards("2", 2)
    expected = level_filter(WORDS, 2)
    assert [card["id"] for card in cards] == [card["id"] for card in expected]


def test_learn_mixed_groups_by_level_patterns_then_words():
    cards = ordered_learn_cards("3", 2)
    ids = [card["id"] for card in cards]
    expected = []
    for level in [1, 2]:
        expected.extend(card["id"] for card in PATTERNS if card["level"] == level)
        expected.extend(card["id"] for card in WORDS if card["level"] == level)
    assert ids == expected


def test_study_session_avoids_immediate_repeats_across_cycles():
    cards = [
        {"id": "card:a"},
        {"id": "card:b"},
        {"id": "card:c"},
    ]
    session = StudySession()
    seen = []

    for _ in range(30):
        card = session.next_card("demo", cards)
        seen.append(card["id"])

    assert all(left != right for left, right in zip(seen, seen[1:]))


def test_study_session_exhausts_pool_before_repeating():
    cards = [
        {"id": "card:a"},
        {"id": "card:b"},
        {"id": "card:c"},
    ]
    session = StudySession()
    first_cycle = [session.next_card("demo", cards)["id"] for _ in range(3)]
    assert set(first_cycle) == {"card:a", "card:b", "card:c"}
