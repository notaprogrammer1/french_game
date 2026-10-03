"""Conjugation rules shared by the CLI and web interface; no input/output."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

from .conjugations import CONJUGATIONS, VERBS
from .utils import accent_insensitive_equal, loose_equal

EXTRA_NOTES = {
    "conjugation:etre-past-participle": "été is the past participle used after a helper verb: il a été. Était is imperfect: il était. They can both translate as was, but they are different forms.",
}


@dataclass
class Score:
    attempts: int = 0
    correct: int = 0
    almost: int = 0

    @property
    def missed(self) -> int:
        return self.attempts - self.correct - self.almost

    def record(self, result: str) -> None:
        self.attempts += 1
        if result == "correct":
            self.correct += 1
        elif result == "almost":
            self.almost += 1

    def summary(self) -> str:
        if self.attempts == 0:
            return "Score: no attempts yet."
        pct = round((self.correct / self.attempts) * 100)
        return f"Score: {self.correct}/{self.attempts} correct ({pct}%), {self.almost} almost, {self.missed} missed."


@dataclass(frozen=True)
class Example:
    prompt: str
    full_sentence: str
    translation: str


def verb_order() -> list[str]:
    return [verb["infinitive"] for verb in VERBS]


def level_count() -> int:
    return len(verb_order())


def clamp_level(level: int) -> int:
    return max(1, min(level, level_count()))


def current_verb(level: int) -> str:
    return verb_order()[clamp_level(level) - 1]


def unlocked_verbs(level: int) -> set[str]:
    return set(verb_order()[:clamp_level(level)])


def cards_for_verbs(verbs: Iterable[str]) -> list[dict]:
    allowed = set(verbs)
    return [card for card in CONJUGATIONS if card["verb"] in allowed]


def current_verb_cards(level: int) -> list[dict]:
    return cards_for_verbs([current_verb(level)])


def cumulative_cards(level: int) -> list[dict]:
    return cards_for_verbs(unlocked_verbs(level))


def examples_for(card: dict) -> list[Example]:
    # Newer data can provide multiple examples per form. The current deck has
    # one prompt per card, so normalize that shape here instead of making the
    # game care about the storage format.
    if "examples" in card:
        return [Example(**example) for example in card["examples"]]
    return [Example(card["prompt"], card["full_sentence"], card["translation"])]


def note_for(card: dict) -> str:
    extra = EXTRA_NOTES.get(card["id"])
    if extra and extra not in card["note"]:
        return f"{card['note']} {extra}"
    return card["note"]


def answers_for(card: dict) -> list[str]:
    answers = [card["answer"]]
    answers.extend(example.full_sentence for example in examples_for(card))
    return answers


def answer_matches(answer: str, card: dict) -> bool:
    return any(loose_equal(answer, expected) for expected in answers_for(card))


def accent_only_matches(answer: str, card: dict) -> bool:
    return any(accent_insensitive_equal(answer, expected) for expected in answers_for(card))
MODES = {
    "learn-current": "Learn new verb",
    "drill-current": "Drill new verb",
    "learn-cumulative": "Learn cumulative",
    "drill-cumulative": "Drill cumulative",
    "mixed-cumulative": "Mixed cumulative",
}


def grade_answer(answer: str, card: dict) -> str:
    if answer_matches(answer, card):
        return "correct"
    if accent_only_matches(answer, card):
        return "almost"
    return "missed"


def ordered_learn_cards(cards: list[dict]) -> list[dict]:
    return sorted(cards, key=lambda card: (verb_order().index(card["verb"]), card["id"]))


@dataclass(frozen=True)
class Exercise:
    card: dict
    example: Example
    example_index: int


def drill_exercises(cards: list[dict]) -> list[Exercise]:
    deck = cards[:]
    random.shuffle(deck)
    exercises = []
    for card in deck:
        examples = examples_for(card)
        example = random.choice(examples)
        exercises.append(Exercise(card, example, examples.index(example)))
    return exercises


def mode_cards(level: int, mode: str) -> list[dict]:
    if mode not in MODES:
        raise ValueError("Choose a valid mode.")
    if mode.endswith("-current"):
        return current_verb_cards(level)
    return cumulative_cards(level)
