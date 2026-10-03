# French Phonics Game

A small repo with two games for learning French:

1. **French Phonics Game** — learn how written French maps to spoken French.
2. **French Conjugation Game** — drill verb forms in short contextual sentences, in the terminal or a phone browser.

Both games are beginner-friendly and work without third-party runtime packages. The conjugation game also has a mobile web interface and basic installable PWA.

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

Or run it without installing:

```bash
python3 -m french_phonics_game.conjugation_game
```

## Play on a phone

From the repository directory, start the web interface:

```bash
python3 -m french_phonics_game.web
```

Open **http://localhost:8000** in a browser. There is no frontend build step or Node.js requirement. After installing the package, `french-conjugations-web` starts the same server.

To play on an Android phone on the same Wi-Fi network:

```bash
python3 -m french_phonics_game.web --host 0.0.0.0 --port 8000
```

On the phone, open `http://<your-computer's-LAN-IP>:8000` in Chrome. Allow port 8000 through the computer's firewall if needed, and keep the server running. The phone only needs a browser; it never needs a terminal or Python.

The interface starts at level 1 with **Drill new verb**. **Change practice** offers all 20 verb levels and all five existing modes. It shows one card at a time, with a large answer field, accent keys, a submit button, hints, skip, and a session score. Hints do not affect the score. Skips reveal the answer and count separately, without recording an attempt.

Correct answers advance after about two seconds. Corrections and skipped answers stay visible for about six seconds before advancing. **Pause** keeps the feedback on screen; **Next now** moves immediately. Switching away from the app pauses a pending transition. A deck ends after every card has appeared, and **Practice again** starts another shuffled deck. Learn modes show answers in the existing order and advance when you tap **Next card**.

### Install on Android

Visit a deployed **HTTPS** URL in Chrome. Tap **Install app** when available, or use Chrome's menu → **Add to Home screen** → **Install**. It opens as a standalone app from the home screen.

The PWA caches the interface and displays a reconnect message offline. Loading exercises, checking answers, and skipping still require a connection to the Python server. The local Wi-Fi HTTP URL is fine for playing, but Android PWA installation and service workers require HTTPS. Localhost is an exception on the computer itself.

### Architecture

- `conjugations.py` retains the original verb list and all exercise data.
- `conjugation_core.py` contains the existing level/pool rules, example normalization, answer matching, notes, and `Score`, plus shared grading and deck helpers. It has no terminal or web input/output.
- `conjugation_game.py` remains the CLI, using the shared core for learn order, drills, and grading. Its entry point and terminal commands remain available. The phonics CLI and its saved progress remain separate.
- `web.py` is a small standard-library WSGI app. It serves static assets and three JSON routes: settings, a deck, and answer/skip feedback. It uses the same Python core to select cards, grade answers, and update scores.
- `static/` contains plain HTML, CSS, and JavaScript, a manifest, icons, and a small service worker. JavaScript handles presentation and timing; it does not implement a second conjugation grader.

The web app has no database, login, cookies, or server session store. Each open page holds its own temporary score and deck; the score is passed to Python with an answer and returned updated. Changing level/mode or replaying a deck keeps that score; reloading starts a new session. Web and CLI scores are independent, matching the original conjugation game's session-only design.

### Easiest deployment: Render

This needs a Python server, so GitHub Pages alone cannot host the complete game. The included `render.yaml` configures a small Render web service with Gunicorn and HTTPS:

1. Push these changes to your GitHub repository.
2. In Render, choose **New → Blueprint**, connect this repository, and choose the branch containing `render.yaml`.
3. Review the service/plan and deploy. Open Render's HTTPS URL on your phone and install it from Chrome.

You can also create a Render **Web Service** manually with:

```text
Build command: pip install '.[web]'
Start command: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 30 french_phonics_game.web:application
Health check: /api/settings
```

Only production hosting needs the optional Gunicorn dependency; local play remains dependency-free. Other Python hosts supporting WSGI and HTTPS can run the same application. Serve it at the domain root, since the PWA assets and API use root-relative URLs. The standard-library server is for local development.

### Tests

```bash
python3 -m pip install '.[test]'
python3 -m pytest -q
```

This runs the original phonics tests plus shared conjugation, CLI, web API, and PWA asset tests. Optional browser tests are skipped by default. To also check the phone layout, touch targets, all modes, feedback, automatic transitions, network failures, and the offline PWA shell:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
FRENCH_GAME_BROWSER_TESTS=1 python3 -m pytest -q
```

GitHub Actions runs both suites and saves a phone screenshot as the `phone-preview` artifact. The pre-existing mixed-learn test was updated to use menu option 4 and include conjugation cards, matching the current phonics menu; option 3 is conjugation learning.

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
