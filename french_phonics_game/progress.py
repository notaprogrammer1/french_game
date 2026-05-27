from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
from typing import Iterable


DEFAULT_PROGRESS_PATH = Path.home() / ".french_phonics_game" / "progress.json"


@dataclass
class Score:
    correct: int = 0
    almost: int = 0
    missed: int = 0

    @property
    def total(self) -> int:
        return self.correct + self.almost + self.missed

    def add_correct(self) -> None:
        self.correct += 1

    def add_almost(self) -> None:
        self.almost += 1

    def add_missed(self) -> None:
        self.missed += 1

    def summary(self) -> str:
        if self.total == 0:
            return "No rounds yet."
        percent = round((self.correct + 0.5 * self.almost) / self.total * 100)
        return (
            f"Score: {self.correct} correct, {self.almost} almost, "
            f"{self.missed} missed — {percent}% adjusted accuracy"
        )


class ProgressStore:
    """Tiny JSON progress store.

    A card is considered to need review if it has been missed and does not yet
    have a streak of two correct answers.
    """

    def __init__(self, path: Path | None = None) -> None:
        env_path = os.getenv("FRENCH_PHONICS_PROGRESS")
        self.path = path or Path(env_path).expanduser() if env_path else path or DEFAULT_PROGRESS_PATH
        self.data = {"version": 1, "cards": {}}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return
        if isinstance(data, dict) and isinstance(data.get("cards"), dict):
            self.data = data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")

    def record(self, card_id: str, result: str) -> None:
        cards = self.data.setdefault("cards", {})
        entry = cards.setdefault(
            card_id,
            {"attempts": 0, "correct": 0, "almost": 0, "missed": 0, "streak": 0},
        )

        entry["attempts"] = int(entry.get("attempts", 0)) + 1
        entry[result] = int(entry.get(result, 0)) + 1
        entry["last_result"] = result

        if result == "correct":
            entry["streak"] = int(entry.get("streak", 0)) + 1
        else:
            entry["streak"] = 0

        self.save()

    def entry(self, card_id: str) -> dict:
        return self.data.get("cards", {}).get(card_id, {})

    def needs_review(self, card_id: str) -> bool:
        entry = self.entry(card_id)
        return int(entry.get("missed", 0)) > 0 and int(entry.get("streak", 0)) < 2

    def review_cards(self, cards: Iterable[dict]) -> list[dict]:
        return [card for card in cards if self.needs_review(card["id"])]

    def weight_for(self, card_id: str) -> int:
        entry = self.entry(card_id)
        missed = int(entry.get("missed", 0))
        streak = int(entry.get("streak", 0))
        return 1 + missed * 2 + max(0, 2 - streak)

    def summary(self) -> str:
        cards = self.data.get("cards", {})
        attempts = sum(int(card.get("attempts", 0)) for card in cards.values())
        correct = sum(int(card.get("correct", 0)) for card in cards.values())
        almost = sum(int(card.get("almost", 0)) for card in cards.values())
        missed = sum(int(card.get("missed", 0)) for card in cards.values())
        review = sum(1 for card_id in cards if self.needs_review(card_id))

        if attempts == 0:
            return "Saved progress: no saved attempts yet."

        adjusted = round((correct + 0.5 * almost) / attempts * 100)
        return (
            f"Saved progress: {attempts} attempts across {len(cards)} cards — "
            f"{correct} correct, {almost} almost, {missed} missed, "
            f"{review} cards need review, {adjusted}% adjusted accuracy."
        )
