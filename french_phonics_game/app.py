import random

from .data import LEVELS, PATTERNS, WORDS
from .progress import ProgressStore, Score
from .utils import accent_insensitive_equal, choose, join_or, level_filter, loose_equal, normalize, shuffled

HELP = """
Commands during a round:
  q        quit
  menu     return to mode menu
  hint     show a hint
  score    show this session's score
  stats    show saved progress

Levels are cumulative. Level 3 includes cards from Levels 1, 2, and 3.
A missed card enters review. Two correct answers in a row clears it.
"""


def ask(prompt: str) -> str:
    return input(prompt).strip()


def command(text: str, score: Score, progress: ProgressStore) -> str | None:
    text = normalize(text)
    if text in {"q", "quit", "exit"}:
        return "quit"
    if text == "menu":
        return "menu"
    if text == "score":
        print(score.summary())
        return "continue"
    if text == "stats":
        print(progress.summary())
        return "continue"
    return None


def describe_level(level: int) -> str:
    info = LEVELS[level]
    return (
        f"Level {level}: {info['name']} — {info['focus']}\n"
        f"Includes {len(level_filter(PATTERNS, level))} pattern cards and "
        f"{len(level_filter(WORDS, level))} word cards."
    )


def choose_level(current: int) -> int:
    print("\nChoose a cumulative level:")
    for number, info in LEVELS.items():
        marker = " current" if number == current else ""
        print(f"  {number}. {info['name']} — {info['focus']}{marker}")
    answer = ask("> ")
    if not answer:
        return current
    try:
        level = int(answer)
    except ValueError:
        print("Please choose a number.")
        return current
    if level not in LEVELS:
        print("That level does not exist yet.")
        return current
    print("\n" + describe_level(level))
    return level


def show_pattern(card: dict) -> None:
    print("\nPattern card")
    print("------------")
    print(f"Level:    {card['level']}")
    print(f"Pattern:  {join_or(card['graphemes'])}")
    print(f"Sound:    {card['sound']}")
    print(f"Examples: {', '.join(card['examples'])}")
    print(f"Note:     {card['note']}")


def show_word(card: dict) -> None:
    print("\nWord card")
    print("---------")
    print(f"Level:    {card['level']}")
    print(f"French:   {card['french']}")
    print(f"Meaning:  {card['meaning']}")
    print(f"Sound:    {card['sound']}")
    print(f"Chunks:   {' + '.join(card['chunks'])}")
    for note in card["notes"]:
        print(f"  - {note}")


def record(score: Score, progress: ProgressStore, card: dict, result: str) -> None:
    score.add(result)
    progress.record(card["id"], result)


def weighted(cards: list[dict], progress: ProgressStore) -> dict:
    return random.choices(cards, weights=[progress.weight_for(c["id"]) for c in cards], k=1)[0]


def learn(score: Score, progress: ProgressStore, level: int) -> str | None:
    patterns = level_filter(PATTERNS, level)
    words = level_filter(WORDS, level)
    print("\nLearn mode gives you the answer directly.")
    print("1. Pattern cards  2. Word cards  3. Mixed")
    choice = ask("> ")
    cmd = command(choice, score, progress)
    if cmd:
        return cmd
    if choice not in {"1", "2", "3"}:
        return None
    print("Press Enter for another card. Type menu/q/stats any time.")
    while True:
        if choice == "1":
            show_pattern(choose(patterns))
        elif choice == "2":
            show_word(choose(words))
        else:
            show_pattern(choose(patterns)) if random.choice([True, False]) else show_word(choose(words))
        cmd = command(ask("\nNext? "), score, progress)
        if cmd == "continue":
            continue
        if cmd:
            return cmd


def pattern_to_sound(score: Score, progress: ProgressStore, level: int, pool: list[dict] | None = None) -> str | None:
    card = weighted(pool or level_filter(PATTERNS, level), progress)
    grapheme = choose(card["graphemes"])
    print(f"\nPattern: {grapheme}")
    answer = ask("Sound hint? ")
    cmd = command(answer, score, progress)
    if cmd == "continue":
        return None
    if cmd:
        return cmd
    if normalize(answer) == "hint":
        print(f"Examples: {', '.join(card['examples'])}")
        answer = ask("Sound hint? ")
    if loose_equal(answer, card["sound"]):
        print("✅ Correct.")
        record(score, progress, card, "correct")
    else:
        print(f"❌ Not quite. {grapheme} → {card['sound']}")
        print(card["note"])
        record(score, progress, card, "missed")
    return None


def sound_to_pattern(score: Score, progress: ProgressStore, level: int, pool: list[dict] | None = None) -> str | None:
    card = weighted(pool or level_filter(PATTERNS, level), progress)
    print(f"\nSound hint: {card['sound']}")
    print(f"Examples: {', '.join(card['examples'][:3])}")
    answer = ask("French spelling chunk? ")
    cmd = command(answer, score, progress)
    if cmd == "continue":
        return None
    if cmd:
        return cmd
    if normalize(answer) == "hint":
        print(f"Try one of the spellings used in: {', '.join(card['examples'])}")
        answer = ask("French spelling chunk? ")
    if normalize(answer) in [normalize(g) for g in card["graphemes"]]:
        print("✅ Correct.")
        record(score, progress, card, "correct")
    else:
        print(f"❌ Not quite. Try {join_or(card['graphemes'])}.")
        print(card["note"])
        record(score, progress, card, "missed")
    return None


def word_to_sound(score: Score, progress: ProgressStore, level: int, pool: list[dict] | None = None) -> str | None:
    card = weighted(pool or level_filter(WORDS, level), progress)
    print(f"\nFrench word: {card['french']}")
    print(f"Meaning: {card['meaning']}")
    answer = ask("Rough sound? ")
    cmd = command(answer, score, progress)
    if cmd == "continue":
        return None
    if cmd:
        return cmd
    if normalize(answer) == "hint":
        print("Chunks:", " + ".join(card["chunks"]))
        answer = ask("Rough sound? ")
    if loose_equal(answer, card["sound"]):
        print("✅ Correct.")
        record(score, progress, card, "correct")
    else:
        print(f"One rough version is: {card['sound']}")
        print("Chunks:", " + ".join(card["chunks"]))
        record(score, progress, card, "almost")
    return None


def sound_to_word(score: Score, progress: ProgressStore, level: int, pool: list[dict] | None = None) -> str | None:
    card = weighted(pool or level_filter(WORDS, level), progress)
    print(f"\nSound hint: {card['sound']}")
    print(f"Meaning: {card['meaning']}")
    answer = ask("Type the French word: ")
    cmd = command(answer, score, progress)
    if cmd == "continue":
        return None
    if cmd:
        return cmd
    if normalize(answer) == "hint":
        print("Chunks:", " + ".join(card["chunks"]))
        answer = ask("Type the French word: ")
    if loose_equal(answer, card["french"]):
        print("✅ Correct.")
        record(score, progress, card, "correct")
    elif accent_insensitive_equal(answer, card["french"]):
        print(f"🟡 Almost — accent issue. Correct spelling: {card['french']}")
        record(score, progress, card, "almost")
    else:
        print(f"❌ Not quite. Correct answer: {card['french']}")
        print("Chunks:", " + ".join(card["chunks"]))
        record(score, progress, card, "missed")
    return None


def build_from_chunks(score: Score, progress: ProgressStore, level: int, pool: list[dict] | None = None) -> str | None:
    card = weighted(pool or level_filter(WORDS, level), progress)
    print(f"\nMeaning: {card['meaning']}")
    print(f"Sound hint: {card['sound']}")
    print("Chunks:", " / ".join(shuffled(card["chunks"])))
    answer = ask("Build/type the French word: ")
    cmd = command(answer, score, progress)
    if cmd == "continue":
        return None
    if cmd:
        return cmd
    if loose_equal(answer, card["french"]):
        print("✅ Correct.")
        record(score, progress, card, "correct")
    elif accent_insensitive_equal(answer, card["french"]):
        print(f"🟡 Almost — accent issue. Correct spelling: {card['french']}")
        record(score, progress, card, "almost")
    else:
        print(f"❌ Not quite. Correct answer: {card['french']}")
        record(score, progress, card, "missed")
    return None


def review(score: Score, progress: ProgressStore, level: int) -> str | None:
    patterns = progress.review_cards(level_filter(PATTERNS, level))
    words = progress.review_cards(level_filter(WORDS, level))
    if not patterns and not words:
        print("\nNo cards need review at this level yet.")
        return None
    if patterns and (not words or random.choice([True, False])):
        return random.choice([pattern_to_sound, sound_to_pattern])(score, progress, level, patterns)
    return random.choice([word_to_sound, sound_to_word, build_from_chunks])(score, progress, level, words)


def mixed(score: Score, progress: ProgressStore, level: int) -> str | None:
    return random.choice([pattern_to_sound, sound_to_pattern, word_to_sound, sound_to_word, build_from_chunks])(score, progress, level)


MODES = {
    "0": ("Learn mode", learn),
    "1": ("Pattern → sound", pattern_to_sound),
    "2": ("Sound → pattern", sound_to_pattern),
    "3": ("Word → rough sound", word_to_sound),
    "4": ("Sound/meaning → French word", sound_to_word),
    "5": ("Build from chunks", build_from_chunks),
    "6": ("Review cards that need work", review),
    "7": ("Mixed drill", mixed),
}


def choose_mode(level: int, progress: ProgressStore) -> str | None:
    print("\n" + describe_level(level))
    print(progress.summary())
    print("\nChoose a mode:")
    for key, (name, _) in MODES.items():
        print(f"  {key}. {name}")
    print("  l. Change level")
    print("  h. Help")
    print("  q. Quit")
    choice = ask("> ").lower()
    if choice in {"q", "quit", "exit"}:
        return None
    if choice == "h":
        print(HELP)
        return choose_mode(level, progress)
    if choice == "l":
        return "level"
    if choice not in MODES:
        print("Choose 0–7, l, h, or q.")
        return choose_mode(level, progress)
    return choice


def main() -> None:
    score = Score()
    progress = ProgressStore()
    level = 1
    print("\nFrench Phonics Game")
    print("===================")
    while True:
        choice = choose_mode(level, progress)
        if choice is None:
            print("\n" + score.summary())
            print(progress.summary())
            print("À bientôt!")
            return
        if choice == "level":
            level = choose_level(level)
            continue
        name, mode = MODES[choice]
        print(f"\nMode: {name}")
        while True:
            result = mode(score, progress, level)
            if choice != "0":
                print(score.summary())
            if result == "quit":
                print("\nÀ bientôt!")
                return
            if result == "menu" or choice == "0":
                break


if __name__ == "__main__":
    main()
