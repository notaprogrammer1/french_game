from french_phonics_game.app import build_from_chunks, pattern_to_sound, sound_to_word
from french_phonics_game.progress import ProgressStore, Score


def make_ask(responses):
    responses = iter(responses)
    return lambda prompt: next(responses)


def test_pattern_hint_then_menu_does_not_record(monkeypatch, tmp_path):
    progress = ProgressStore(tmp_path / "progress.json")
    score = Score()
    card = {
        "id": "pattern:test",
        "level": 1,
        "graphemes": ["ou"],
        "sound": "oo",
        "examples": ["nous"],
        "note": "test",
    }
    monkeypatch.setattr("french_phonics_game.app.read_input", make_ask(["hint", "menu"]))

    assert pattern_to_sound(score, progress, 1, [card]) == "menu"
    assert progress.entry("pattern:test") == {}
    assert score.total == 0


def test_sound_to_word_hint_then_quit_does_not_record(monkeypatch, tmp_path):
    progress = ProgressStore(tmp_path / "progress.json")
    score = Score()
    card = {
        "id": "word:test",
        "level": 1,
        "french": "chat",
        "sound": "shah",
        "meaning": "cat",
        "chunks": ["ch", "a", "t"],
        "notes": ["test"],
    }
    monkeypatch.setattr("french_phonics_game.app.read_input", make_ask(["hint", "q"]))

    assert sound_to_word(score, progress, 1, [card]) == "quit"
    assert progress.entry("word:test") == {}
    assert score.total == 0


def test_build_hint_then_stats_does_not_record(monkeypatch, tmp_path, capsys):
    progress = ProgressStore(tmp_path / "progress.json")
    score = Score()
    card = {
        "id": "word:test",
        "level": 1,
        "french": "chat",
        "sound": "shah",
        "meaning": "cat",
        "chunks": ["ch", "a", "t"],
        "notes": ["test"],
    }
    monkeypatch.setattr("french_phonics_game.app.read_input", make_ask(["hint", "stats"]))

    assert build_from_chunks(score, progress, 1, [card]) is None
    assert "Saved progress" in capsys.readouterr().out
    assert progress.entry("word:test") == {}
    assert score.total == 0
