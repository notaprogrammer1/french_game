# French Phonics Game

A small repo with two terminal games for learning French:

1. **French Phonics Game** — learn how written French maps to spoken French.
2. **French Conjugation Game** — drill verb forms in short contextual sentences.

Both games are beginner-friendly, require no third-party packages, and run in the terminal.

## Requirements

Python 3.10 or newer. No third-party packages required.

## Run it

Run the phonics game directly:

```bash
python3 -m french_phonics_game
```

Or install locally:

```bash
python3 -m pip install -e .
french-phonics
```

Run the standalone conjugation game after installing locally:

```bash
french-conjugations
```

## French Phonics Game

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

### Phonics levels

Levels are cumulative. Level 3 includes Levels 1, 2, and 3.

- **Level 1**: first high-value chunks
- **Level 2**: includes Level 1 + more vowel spellings and silent finals
- **Level 3**: includes Levels 1–2 + nasals, `ç`, `gn`, and more common words
- **Level 4**: includes Levels 1–3 + harder sounds like French `u`, French `r`, and final `e`

### Phonics modes

0. **Learn mode** — Shows the answers directly in a steady order.
1. **Pattern → sound** — See `ou`; answer `oo`.
2. **Sound → pattern** — See `oo`; answer `ou`.
3. **Word → rough sound** — See `rouge`; answer something like `ghoozh`.
4. **Sound/meaning → French word** — See `ghoozh` and `red`; answer `rouge`.
5. **Build from chunks** — See shuffled chunks like `ge / r / ou`; type `rouge`.
6. **Review cards that need work** — Missed cards come back until you answer them correctly twice in a row.
7. **Mixed drill** — Rotates between the main drill modes.
8. **Conjugation in context** — A lightweight conjugation drill kept in the phonics app for convenience.

Drill modes use shuffled decks rather than pure randomness. You should see each card in a mode's current pool before that deck reshuffles, and the game tries not to show the same card twice in a row.

## French Conjugation Game

The standalone conjugation game is intentionally separate from the phonics app. It has no saved progress file and keeps only a session score. That makes it easier to experiment with verb levels without tying it to the phonics review system.

### Conjugation levels

Conjugation levels are cumulative by verb:

```text
Level 1: être
Level 2: être + avoir
Level 3: être + avoir + aller
...
Level 20: all 20 verbs
```

Each level unlocks one new verb while keeping earlier verbs in the practice pool.

### Conjugation modes

1. **Learn new verb** — Show only the verb unlocked at the current level.
2. **Drill new verb** — Quiz only the verb unlocked at the current level.
3. **Learn cumulative** — Show every verb unlocked so far.
4. **Drill cumulative** — Quiz every verb unlocked so far.
5. **Mixed cumulative** — Run a shuffled cumulative drill.

The conjugation game accepts either the missing form or the full French sentence. Accent-only mistakes are marked as "almost." Different forms are not treated as accent variants: `été` and `était` are different answers.

The game already normalizes cards so future data can provide multiple blank-sentence examples per form without changing the game loop.

## In-game commands

```text
q        quit
menu     return to mode menu
hint     show a hint
score    show this session's score
stats    show saved phonics progress / session score depending on game
level    change level in the conjugation game
```

## Progress saving

The phonics game saves progress automatically to `~/.french_phonics_game/progress.json`.

To use a different file:

```bash
export FRENCH_PHONICS_PROGRESS=/path/to/progress.json
```

The standalone conjugation game does **not** save progress. It only tracks the current session score.

## Mac accent tip

You can usually type accented letters on a Mac by holding the base letter: hold `e` for `é`, `è`, `ê`, or `ë`; hold `c` for `ç`; hold `a` for `à` or `â`.

The games are forgiving: if you type `francais`, they will say "almost" and show the correct accented spelling `français`.

## Suggested phonics learning routine

This game works best as a small daily drill, not as a giant cram session. Ten focused minutes is better than forcing an hour and hating it.

### 1. Start with Learn mode

Choose **Level 1**, then choose **Learn mode**.

Learn mode is intentionally organized instead of random. Pattern cards are shown in level order, word cards are shown in level order, and mixed learn cards are grouped by level. Do not quiz yourself yet. Just look at the cards and say the examples out loud. The point is to let your brain notice patterns:

- `ou` keeps sounding like "oo"
- `ch` keeps sounding like "sh"
- final letters like `t` or `s` often disappear

Stay here until the cards stop looking completely alien. You do not need to memorize everything before moving on.

### 2. Drill reading first

After Learn mode, use:

- **Pattern → sound**
- **Word → rough sound**

These modes train reading: seeing French and getting a sound from it.

This is usually easier than spelling, so it makes a good first active step. Say the answer out loud before typing it, even if your pronunciation is rough.

### 3. Then drill spelling

Once reading feels less scary, switch to:

- **Sound → pattern**
- **Sound/meaning → French word**
- **Build from chunks**

These modes train writing. They are harder because French has multiple spellings for similar sounds, like `o`, `au`, and `eau`. Getting accents wrong is normal. The game will mark accent-only mistakes as "almost" and show the correct spelling.

### 4. Use Review mode every session

If you miss cards, they enter review. Use **Review cards that need work** before ending a session.

A missed card leaves review after you answer it correctly twice in a row. This keeps the game focused on what is actually giving you trouble instead of endlessly repeating things you already know.

### 5. Move up a level when the current one feels boring

Do not wait until you are perfect. Move from Level 1 to Level 2 when Level 1 starts feeling familiar and slightly boring.

Because levels are cumulative, Level 2 still includes Level 1. You are not abandoning the old material; you are adding a new layer on top of it.

A simple path is:

```text
Learn mode → Pattern → sound → Word → sound → Build from chunks → Review
```

Then move up a level and repeat.

### 6. Use Mixed drill when you want a normal practice session

Once you have seen the cards in Learn mode, **Mixed drill** is the easiest default mode. It rotates between reading, spelling, and chunk-building.

The drill modes are not fully random. They use shuffled decks so you get a steady stream of the current material instead of seeing the same card over and over.

### 7. Keep the English-ish sounds temporary

The pronunciation hints are training wheels. They are useful at the beginning, but they are not perfect French. Over time, try to think:

```text
ou → French ou sound
```

instead of:

```text
ou → English "oo"
```

That shift is the real goal: seeing French spelling and hearing a French-ish sound in your head.
