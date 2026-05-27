from french_phonics_game.progress import ProgressStore


def test_progress_records_and_flags_review(tmp_path):
    path = tmp_path / "progress.json"
    progress = ProgressStore(path)

    progress.record("word:chat", "missed")
    assert progress.needs_review("word:chat")

    progress.record("word:chat", "correct")
    assert progress.needs_review("word:chat")

    progress.record("word:chat", "correct")
    assert not progress.needs_review("word:chat")


def test_progress_persists(tmp_path):
    path = tmp_path / "progress.json"
    progress = ProgressStore(path)
    progress.record("pattern:ou", "correct")

    loaded = ProgressStore(path)
    assert loaded.entry("pattern:ou")["correct"] == 1
