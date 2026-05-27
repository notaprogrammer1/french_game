from french_phonics_game.app import learn_mode
from french_phonics_game.progress import ProgressStore, Score


def make_ask(responses):
    responses = iter(responses)
    return lambda prompt: next(responses)


def test_learn_mode_accepts_standard_mode_signature(monkeypatch, tmp_path):
    progress = ProgressStore(tmp_path / "progress.json")
    score = Score()
    monkeypatch.setattr("french_phonics_game.app.read_input", make_ask(["1", "menu"]))

    assert learn_mode(score, progress, 1) == "menu"
    assert score.total == 0
