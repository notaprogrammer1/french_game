# French Phonics Game

A terminal game for learning how written French maps to spoken French.

This is a **French sound-spelling chunk** trainer. It does not treat French as a simple letter-for-letter swap with English. Instead, it drills patterns like:

- `ou` → "oo"
- `ch` → "sh"
- `eau` / `au` → "oh"
- `an` / `en` → nasal "ahn"
- `ç` → "s"
- final consonants are often silent

The goal is to build the real reading/writing reflexes:

1. **Reading**: French spelling → sound
2. **Writing**: sound/meaning → French spelling
3. **Chunking**: build whole words from French sound-spelling pieces
4. **Learning**: view answers directly before drilling
5. **Reviewing**: revisit cards you missed until they start sticking

## Requirements

Python 3.10 or newer. No third-party packages required.

## Run it

```bash
python3 -m french_phonics_game
```

Or install locally:

```bash
python3 -m pip install -e .
french-phonics
```

## Levels

Levels are cumulative. Level 3 includes Levels 1, 2, and 3.

- **Level 1**: first high-value chunks
- **Level 2**: includes Level 1 + more vowel spellings and silent finals
- **Level 3**: includes Levels 1–2 + nasals, `ç`, `gn`, and more common words
- **Level 4**: includes Levels 1–3 + harder sounds like French `u`, French `r`, and final `e`

## Modes

0. **Learn mode** — Shows the answers directly.
1. **Pattern → sound** — See `ou`; answer `oo`.
2. **Sound → pattern** — See `oo`; answer `ou`.
3. **Word → rough sound** — See `rouge`; answer something like `ghoozh`.
4. **Sound/meaning → French word** — See `ghoozh` and `red`; answer `rouge`.
5. **Build from chunks** — See shuffled chunks like `ge / r / ou`; type `rouge`.
6. **Review cards that need work** — Missed cards come back until you answer them correctly twice in a row.
7. **Mixed drill** — Randomly chooses from the main drill modes and lightly weights missed cards.

## In-game commands

```text
q        quit
menu     return to mode menu
hint     show a hint
score    show this session's score
stats    show saved progress
```

## Progress saving

Progress is saved automatically to `~/.french_phonics_game/progress.json`.

To use a different file:

```bash
export FRENCH_PHONICS_PROGRESS=/path/to/progress.json
```

## Mac accent tip

You can usually type accented letters on a Mac by holding the base letter: hold `e` for `é`, `è`, `ê`, or `ë`; hold `c` for `ç`; hold `a` for `à` or `â`.

The game is forgiving: if you type `francais`, it will say "almost" and show the correct accented spelling `français`.
