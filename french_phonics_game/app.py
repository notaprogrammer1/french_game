import random
from .data import LEVELS, PATTERNS, WORDS
from .progress import ProgressStore, Score
from .utils import (
    accent_insensitive_equal,
    choose,
    join_or,
    level_filter,
    loose_equal,
    normalize,
    shuffled,
)


HELP = """
Commands during a round:
  q        quit
  menu     return to mode menu
  hint     show a hint, if available
  score    show this session's score
  stats    show saved progress

Level behavior:
  Levels are cumulative. Level 3 includes cards from Levels 1, 2, and 3.

Review behavior:
  A missed card goes into review. Two correct answers in a row clears it.
"""


def print_header() -> None:
    print("\nFrench Phonics Game")
    print("===================")
    print("Drill French spelling chunks, pronunciation hints, and word building.")
    print("Type 'q' to quit, 'menu' to change modes, or 'hint' during a round.\n")


def read_input(prompt: str) -> str:
    return input(prompt).strip()


def check_command(answer: str, score: Score | None = None, progress: ProgressStore | None = None) -> str | None:
    lowered = normalize(answer)
    if lowered in {"q", "quit", "exit"}:
        return "quit"
    if lowered == "menu":
        return "menu"
    if lowered == "score" and score is not None:
        print(score.summary())
        return "continue"
    if lowered == "stats" and progress is not None:
        print(progress.summary())
        return "continue"
    return None


def describe_level(active_level: int) -> str:
    info = LEVELS[active_level]
    pattern_count = len(level_filter(PATTERNS, active_level))
    word_count = len(level_filter(WORDS, active_level))
    return (
        f"Level {active_level}: {info['name']} — {info['focus']}\n"
        f"Includes {pattern_count} pattern cards and {word_count} word cards."
    )


def choose_level(current_level: int) -> int:
    print("\nChoose a cumulative level:")
    for number, info in LEVELS.items():
        marker = " current" if number == current_level else ""
        print(f"  {number}. {info['name']} — {info['focus']}{marker}")
    print("  Enter. Keep current level")

    answer = read_input("> ")
    if not answer:
        return current_level

    try:
        level = int(answer)
    except ValueError:
        print("Please choose a number.")
        return choose_level(current_level)

    if level not in LEVELS:
        print(f"Please choose one of: {', '.join(str(x) for x in LEVELS)}")
        return choose_level(current_level)

    print("\n" + describe_level(level))
    return level


def show_pattern_card(card: dict) -> None:
    print("\nPattern card")
    print("------------")
    print(f"Level:    {card['level']}")
    print(f"Pattern:  {join_or(card['graphemes'])}")
    print(f"Sound:    {card['sound']}")
    print(f"Examples: {', '.join(card['examples'])}")
    print(f"Note:     {card['note']}")


def show_word_card(card: dict) -> None:
    print("\nWord card")
    print("---------")
    print(f"Level:    {card['level']}")
    print(f"French:   {card['french']}")
    print(f"Meaning:  {card['meaning']}")
    print(f"Sound:    {card['sound']}")
    print(f"Chunks:   {' + '.join(card['chunks'])}")
    print("Notes:")
    for note in card["notes"]:
        print(f"  - {note}")


def register_result(score: Score, progress: ProgressStore, card: dict, result: str) -> None:
    if result == "correct":
        score.add_correct()
    elif result == "almost":
        score.add_almost()
    else:
        score.add_missed()
    progress.record(card["id"], result)


def choose_weighted(cards: list[dict], progress: ProgressStore) -> dict:
    weights = [progress.weight_for(card["id"]) for card in cards]
    return random.choices(cards, weights=weights, k=1)[0]


def learn_mode(active_level: int, score: Score, progress: ProgressStore) -> str | None:
    print("\nLearn mode")
    print("==========")
    print("This mode gives you the answer directly.")
    print(describe_level(active_level))
    print("\nChoose:")
    print("  1. Pattern cards")
    print("  2. Word cards")
    print("  3. Mixed learn cards")
    print("  menu. Return to menu")
    print("  q. Quit")

    choice = read_input("> ")
    action = check_command(choice, score, progress)
    if action in {"quit", "menu"}:
        return action

    if choice not in {"1", "2", "3"}:
        print("Choose 1, 2, 3, menu, or q.")
        return None

    patterns = level_filter(PATTERNS, active_level)
    words = level_filter(WORDS, active_level)

    print("\nPress Enter for next card. Type 'menu', 'stats', or 'q' any time.")

    while True:
        if choice == "1":
            show_pattern_card(choose(patterns))
        elif choice == "2":
            show_word_card(choose(words))
        else:
            if random.choice(["pattern", "word"]) == "pattern":
                show_pattern_card(choose(patterns))
            else:
                show_word_card(choose(words))

        answer = read_input("\nNext? ")
        action = check_command(answer, score, progress)
        if action == "continue":
            continue
        if action in {"quit", "menu"}:
            return action


def pattern_to_sound(score: Score, progress: ProgressStore, active_level: int, cards: list[dict] | None = None) -> str | None:
    pool = cards or level_filter(PATTERNS, active_level)
    card = choose_weighted(pool, progress)
    grapheme = choose(card["graphemes"])

    print(f"\nPattern:  {grapheme}")
    answer = read_input("Sound hint? ")

    action = check_command(answer, score, progress)
    if action == "continue":
        return None
    if action:
        return action

    if normalize(answer) == "hint":
        print(f"Hint: examples include {', '.join(card['examples'])}")
        answer = read_input("Sound hint? ")
        action = check_command(answer, score, progress)
        if action == "continue":
            return None
        if action:
            return action

    if loose_equal(answer, card["sound"]):
        print("✅ Correct.")
        register_result(score, progress, card, "correct")
    else:
        print(f"❌ Not quite. {grapheme} → {card['sound']}")
        print(f"Examples: {', '.join(card['examples'])}")
        print(f"Note: {card['note']}")
        register_result(score, progress, card, "missed")

    return None


def sound_to_pattern(score: Score, progress: ProgressStore, active_level: int, cards: list[dict] | None = None) -> str | None:
    pool = cards or level_filter(PATTERNS, active_level)
    card = choose_weighted(pool, progress)
    expected = card["graphemes"]

    print(f"\nSound hint:  {card['sound']}")
    print(f"Examples:    {', '.join(card['examples'][:3])}")
    answer = read_input("French spelling chunk? ")

    action = check_command(answer, score, progress)
    if action == "continue":
        return None
    if action:
        return action

    if normalize(answer) == "hint":
        print(f"Hint: one answer appears in: {', '.join(card['examples'])}")
        answer = read_input("French spelling chunk? ")
        action = check_command(answer, score, progress)
        if action == "continue":
            return None
        if action:
            return action

    normalized_expected = [normalize(x) for x in expected]
    if normalize(answer) in normalized_expected:
        print("✅ Correct.")
        register_result(score, progress, card, "correct")
    else:
        print(f"❌ Not quite. For {card['sound']}, try {join_or(expected)}.")
        print(f"Note: {card['note']}")
        register_result(score, progress, card, "missed")

    return None


def word_to_sound(score: Score, progress: ProgressStore, active_level: int, cards: list[dict] | None = None) -> str | None:
    pool = cards or level_filter(WORDS, active_level)
    card = choose_weighted(pool, progress)

    print(f"\nFrench word:  {card['french']}")
    print(f"Meaning:      {card['meaning']}")
    answer = read_input("Rough sound? ")

    action = check_command(answer, score, progress)
    if action == "continue":
        return None
    if action:
        return action

    if normalize(answer) == "hint":
        print("Hint chunks:", " + ".join(card["chunks"]))
        answer = read_input("Rough sound? ")
        action = check_command(answer, score, progress)
        if action == "continue":
            return None
        if action:
            return action

    if loose_equal(answer, card["sound"]):
        print("✅ Correct.")
        register_result(score, progress, card, "correct")
    else:
        print(f"One beginner-friendly pronunciation hint is: {card['sound']}")
        print("Chunks:", " + ".join(card["chunks"]))
        for note in card["notes"]:
            print(f"- {note}")
        # This mode is intentionally forgiving because rough pronunciation spelling varies.
        register_result(score, progress, card, "almost")

    return None


def sound_to_word(score: Score, progress: ProgressStore, active_level: int, cards: list[dict] | None = None) -> str | None:
    pool = cards or level_filter(WORDS, active_level)
    card = choose_weighted(pool, progress)

    print(f"\nSound hint:  {card['sound']}")
    print(f"Meaning:     {card['meaning']}")
    answer = read_input("Type the French word: ")

    action = check_command(answer, score, progress)
    if action == "continue":
        return None
    if action:
        return action

    if normalize(answer) == "hint":
        print("Hint chunks:", " + ".join(card["chunks"]))
        answer = read_input("Type the French word: ")
        action = check_command(answer, score, progress)
        if action == "continue":
            return None
        if action:
            return action

    if loose_equal(answer, card["french"]):
        print("✅ Correct.")
        register_result(score, progress, card, "correct")
    elif accent_insensitive_equal(answer, card["french"]):
        print(f"🟡 Almost — accent issue. Correct spelling: {card['french']}")
        register_result(score, progress, card, "almost")
    else:
        print(f"❌ Not quite. Correct answer: {card['french']}")
        print("Chunks:", " + ".join(card["chunks"]))
        for note in card["notes"]:
            print(f"- {note}")
        register_result(score, progress, card, "missed")

    return None


def build_from_chunks(score: Score, progress: ProgressStore, active_level: int, cards: list[dict] | None = None) -> str | None:
    pool = cards or level_filter(WORDS, active_level)
    card = choose_weighted(pool, progress)
    pieces = shuffled(card["chunks"])

    print(f"\nMeaning:     {card['meaning']}")
    print(f"Sound hint:  {card['sound']}")
    print("Chunks:      " + " / ".join(pieces))
    answer = read_input("Build/type the French word: ")

    action = check_command(answer, score, progress)
    if action == "continue":
        return None
    if action:
        return action

    if normalize(answer) == "hint":
        first = card["french"][0]
        print(f"Hint: starts with '{first}'")
        answer = read_input("Build/type the French word: ")
        action = check_command(answer, score, progress)
        if action == "continue":
            return None
        if action:
            return action

    if loose_equal(answer, card["french"]):
        print("✅ Correct.")
        register_result(score, progress, card, "correct")
    elif accent_insensitive_equal(answer, card["french"]):
        print(f"🟡 Almost — accent issue. Correct spelling: {card['french']}")
        register_result(score, progress, card, "almost")
    else:
        print(f"❌ Not quite. Correct answer: {card['french']}")
        print("Correct chunks:", " + ".join(card["chunks"]))
        register_result(score, progress, card, "missed")

    return None


def review_mode(score: Score, progress: ProgressStore, active_level: int) -> str | None:
    patterns = progress.review_cards(level_filter(PATTERNS, active_level))
    words = progress.review_cards(level_filter(WORDS, active_level))

    if not patterns and not words:
        print("\nNo cards need review at this level yet. Miss a card and it will show up here.")
        return None

    if patterns and words:
        drill = random.choice(["pattern", "word"])
    elif patterns:
        drill = "pattern"
    else:
        drill = "word"

    if drill == "pattern":
        return random.choice([pattern_to_sound, sound_to_pattern])(score, progress, active_level, patterns)

    return random.choice([word_to_sound, sound_to_word, build_from_chunks])(score, progress, active_level, words)


def mixed(score: Score, progress: ProgressStore, active_level: int) -> str | None:
    mode = random.choice([
        pattern_to_sound,
        sound_to_pattern,
        word_to_sound,
        sound_to_word,
        build_from_chunks,
    ])
    return mode(score, progress, active_level)


MODES = {
    "0": ("Learn mode", learn_mode),
    "1": ("Pattern → sound", pattern_to_sound),
    "2": ("Sound → pattern", sound_to_pattern),
    "3": ("Word → rough sound", word_to_sound),
    "4": ("Sound/meaning → French word", sound_to_word),
    "5": ("Build from chunks", build_from_chunks),
    "6": ("Review cards that need work", review_mode),
    "7": ("Mixed drill", mixed),
}


def choose_mode(active_level: int, progress: ProgressStore) -> str | None:
    print("\n" + describe_level(active_level))
    print(progress.summary())
    print("\nChoose a mode:")
    for key, (name, _) in MODES.items():
        print(f"  {key}. {name}")
    print("  l. Change level")
    print("  h. Help")
    print("  q. Quit")

    choice = read_input("> ").lower()

    if choice in {"q", "quit", "exit"}:
        return None
    if choice in {"h", "help"}:
        print(HELP)
        return choose_mode(active_level, progress)
    if choice == "l":
        return "level"
    if choice not in MODES:
        print("Choose 0–7, l, h, or q.")
        return choose_mode(active_level, progress)
    return choice


def main() -> None:
    score = Score()
    progress = ProgressStore()
    active_level = 1
    print_header()
    print(describe_level(active_level))

    while True:
        choice = choose_mode(active_level, progress)
        if choice is None:
            print("\n" + score.summary())
            print(progress.summary())
            print("À bientôt!")
            return

        if choice == "level":
            active_level = choose_level(active_level)
            continue

        mode_name, mode_func = MODES[choice]
        print(f"\nMode: {mode_name}")
        if choice != "0":
            print("Press Enter after each answer. Type 'menu' to switch modes.\n")

        while True:
            result = mode_func(score, progress, active_level)
            if choice != "0":
                print(score.summary())

            if result == "quit":
                print("\nÀ bientôt!")
                return
            if result == "menu":
                break
            if choice == "0":
                # Learn mode returns after one learn session.
                break


if __name__ == "__main__":
    main()
