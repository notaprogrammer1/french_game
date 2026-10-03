"""Standalone terminal game for drilling French verb conjugations.

This game intentionally keeps no saved progress. It uses a simple cumulative
level structure: each level unlocks one new verb, while keeping prior verbs in
practice.
"""

from __future__ import annotations

import random
from typing import Callable

# Re-export the existing helpers for callers of this module.
from .conjugation_core import (
    Score, Example, EXTRA_NOTES, verb_order, level_count, clamp_level,
    current_verb, unlocked_verbs, cards_for_verbs, current_verb_cards,
    cumulative_cards, examples_for, note_for, answers_for, answer_matches,
    accent_only_matches, grade_answer, ordered_learn_cards, drill_exercises,
)
from .utils import normalize

HELP = """
French Conjugation Game
-----------------------

Levels are cumulative by verb:
  Level 1 unlocks être.
  Level 2 adds avoir, while keeping être.
  Level 20 includes all verbs.

Modes:
  1. Learn new verb       show only the verb unlocked at this level
  2. Drill new verb       quiz only the verb unlocked at this level
  3. Learn cumulative     show every verb unlocked so far
  4. Drill cumulative     quiz every verb unlocked so far
  5. Mixed cumulative     same pool, shuffled each round

Commands:
  hint     show tense and notes
  score    show this session's score
  level    change level
  menu     return to mode menu
  q        quit

Accents matter, but accent-only mistakes are marked almost. Different forms
are different answers: été and était are not the same thing.
""".strip()

def read_input(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "q"


def check_command(text: str, score: Score) -> str | None:
    command = normalize(text)
    if command in {"q", "quit", "exit"}:
        return "quit"
    if command in {"menu", "m"}:
        return "menu"
    if command in {"level", "l"}:
        return "level"
    if command in {"score", "stats"}:
        print(score.summary())
        return "continue"
    if command in {"help", "h"}:
        print(HELP)
        return "continue"
    return None


def print_header(level: int) -> None:
    order = verb_order()
    verb = current_verb(level)
    print("\nFrench Conjugation Game")
    print("=" * 24)
    print(f"Level {level}/{len(order)} unlocks: {verb}")
    print(f"Cumulative pool: {level} verb(s), {len(cumulative_cards(level))} card(s)")


def print_card(card: dict, number: int | None = None, total: int | None = None) -> None:
    prefix = f"[{number}/{total}] " if number is not None and total is not None else ""
    print(f"\n{prefix}{card['verb']} — {card['meaning']}")
    print(f"Form:     {card['answer']}")
    print(f"Tense:    {card['tense']}")
    for idx, example in enumerate(examples_for(card), start=1):
        label = "Example" if len(examples_for(card)) == 1 else f"Example {idx}"
        print(f"{label}:  {example.prompt}")
        print(f"Answer:   {example.full_sentence}")
        print(f"English:  {example.translation}")
    print(f"Note:     {note_for(card)}")


def learn(cards: list[dict], score: Score) -> str | None:
    if not cards:
        print("No cards available.")
        return None
    ordered = ordered_learn_cards(cards)
    print("\nPress Enter for the next card. Type menu, level, or q any time.")
    for index, card in enumerate(ordered, start=1):
        print_card(card, index, len(ordered))
        response = read_input("\nNext? ")
        action = check_command(response, score)
        if action == "continue":
            continue
        if action:
            return action
    print("\nEnd of learn list.")
    return None


def drill(cards: list[dict], score: Score) -> str | None:
    if not cards:
        print("No cards available.")
        return None
    for exercise in drill_exercises(cards):
        card, example = exercise.card, exercise.example
        print(f"\nVerb:     {card['verb']} — {card['meaning']}")
        print(f"Context:  {example.prompt}")
        print(f"English:  {example.translation}")
        answer = read_input("French form? ")
        action = check_command(answer, score)
        if action == "continue":
            continue
        if action:
            return action
        if normalize(answer) == "hint":
            print(f"Hint: {card['tense']}. {note_for(card)}")
            answer = read_input("French form? ")
            action = check_command(answer, score)
            if action == "continue":
                continue
            if action:
                return action
        result = grade_answer(answer, card)
        if result == "correct":
            print("✅ Correct.")
            score.record("correct")
        elif result == "almost":
            print(f"🟡 Almost — accent issue. Correct form: {card['answer']}")
            print(f"Sentence: {example.full_sentence}")
            score.record("almost")
        else:
            print(f"❌ Not quite. Correct form: {card['answer']}")
            print(f"Sentence: {example.full_sentence}")
            print(f"Note: {note_for(card)}")
            score.record("missed")
    print("\nEnd of deck. Returning to the menu.")
    return None


def choose_level() -> int | None:
    print(f"\nChoose a level from 1 to {level_count()}.")
    print("Each level unlocks one new verb and keeps earlier verbs available.")
    for idx, verb in enumerate(verb_order(), start=1):
        print(f"  {idx:2}. {verb}")
    text = read_input("> ")
    if normalize(text) in {"q", "quit", "exit"}:
        return None
    try:
        return clamp_level(int(text))
    except ValueError:
        print("Please type a level number.")
        return choose_level()


def choose_mode(level: int, score: Score) -> tuple[str, Callable[[list[dict], Score], str | None], list[dict]] | str | None:
    print_header(level)
    print(score.summary())
    print("\nChoose a mode:")
    print("  1. Learn new verb")
    print("  2. Drill new verb")
    print("  3. Learn cumulative")
    print("  4. Drill cumulative")
    print("  5. Mixed cumulative")
    print("  l. Change level")
    print("  h. Help")
    print("  q. Quit")
    choice = read_input("> ")
    action = check_command(choice, score)
    if action in {"continue", "menu"}:
        return choose_mode(level, score)
    if action in {"quit", "level"}:
        return action
    pools = {
        "1": ("learn-current", learn, current_verb_cards(level)),
        "2": ("drill-current", drill, current_verb_cards(level)),
        "3": ("learn-cumulative", learn, cumulative_cards(level)),
        "4": ("drill-cumulative", drill, cumulative_cards(level)),
        "5": ("mixed-cumulative", drill, cumulative_cards(level)),
    }
    if choice not in pools:
        print("Choose 1–5, l, h, or q.")
        return choose_mode(level, score)
    return pools[choice]


def main() -> None:
    score = Score()
    level = 1
    print(HELP)
    while True:
        selected = choose_mode(level, score)
        if selected is None or selected == "quit":
            print("\nÀ bientôt.")
            print(score.summary())
            return
        if selected == "level":
            new_level = choose_level()
            if new_level is None:
                print("\nÀ bientôt.")
                return
            level = new_level
            continue
        _, mode, cards = selected
        result = mode(cards, score)
        if result == "quit":
            print("\nÀ bientôt.")
            print(score.summary())
            return
        if result == "level":
            new_level = choose_level()
            if new_level is None:
                print("\nÀ bientôt.")
                return
            level = new_level


if __name__ == "__main__":
    main()
