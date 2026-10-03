import pytest

from french_phonics_game import conjugation_core as game
from french_phonics_game import conjugation_game as cli
from french_phonics_game.conjugations import CONJUGATIONS


def card(suffix):
    return next(card for card in CONJUGATIONS if card["id"] == f"conjugation:{suffix}")


@pytest.mark.parametrize("level,verb", [(1, "être"), (2, "avoir"), (20, "comprendre"), (-1, "être"), (99, "comprendre")])
def test_verb_levels_and_clamping(level, verb):
    assert game.level_count() == 20
    assert game.current_verb(level) == verb
    assert {c["verb"] for c in game.current_verb_cards(level)} == {verb}


def test_cumulative_levels_preserve_previous_cards():
    previous = set()
    for level in range(1, 21):
        cards = game.cumulative_cards(level)
        ids = {c["id"] for c in cards}
        assert previous < ids
        assert {c["verb"] for c in cards} == set(game.verb_order()[:level])
        previous = ids
    assert previous == {c["id"] for c in CONJUGATIONS}


@pytest.mark.parametrize("answer,result", [
    ("été", "correct"), ("  ÉTÉ  ", "correct"),
    ("Il a été malade hier.", "correct"), (" IL  A ÉTÉ malade hier. ", "correct"),
    ("ete", "almost"), ("Il a ete malade hier.", "almost"),
    ("était", "missed"), ("être", "missed"), ("", "missed"),
])
def test_answer_rules_preserve_forms_accents_case_and_spacing(answer, result):
    assert game.grade_answer(answer, card("etre-past-participle")) == result


def test_every_existing_form_and_full_sentence_is_accepted():
    for item in CONJUGATIONS:
        assert game.grade_answer(item["answer"], item) == "correct"
        assert game.grade_answer(item["full_sentence"], item) == "correct"


def test_multiple_examples_and_additional_note():
    item = {**card("etre-past-participle"), "examples": [
        {"prompt": "Il a ___ malade.", "full_sentence": "Il a été malade.", "translation": "He was sick."},
        {"prompt": "Elle a ___ ici.", "full_sentence": "Elle a été ici.", "translation": "She was here."},
    ]}
    assert len(game.examples_for(item)) == 2
    assert game.grade_answer("Elle a été ici.", item) == "correct"
    assert game.grade_answer("Il a ete malade.", item) == "almost"
    assert "Était is imperfect" in game.note_for(item)
    assert game.note_for({**item, "note": game.note_for(item)}) == game.note_for(item)


def test_score_tracks_all_results_without_io(capsys):
    score = game.Score()
    assert score.summary() == "Score: no attempts yet."
    for result in ["correct", "almost", "missed", "correct"]:
        score.record(result)
    assert (score.attempts, score.correct, score.almost, score.missed) == (4, 2, 1, 1)
    assert score.summary() == "Score: 2/4 correct (50%), 1 almost, 1 missed."
    assert capsys.readouterr().out == ""


def test_drill_exhausts_pool_and_does_not_mutate_source():
    cards = game.cumulative_cards(3)
    original_ids = [c["id"] for c in cards]
    exercises = game.drill_exercises(cards)
    assert sorted(e.card["id"] for e in exercises) == sorted(original_ids)
    assert [c["id"] for c in cards] == original_ids
    for exercise in exercises:
        assert exercise.example == game.examples_for(exercise.card)[exercise.example_index]
    assert game.drill_exercises([]) == []


def test_learn_order_and_mode_pools():
    cards = game.cumulative_cards(2)
    assert game.ordered_learn_cards(list(reversed(cards))) == sorted(cards, key=lambda c: (game.verb_order().index(c["verb"]), c["id"]))
    for mode in game.MODES:
        expected = game.current_verb_cards(2) if mode.endswith("-current") else cards
        assert game.mode_cards(2, mode) == expected
    with pytest.raises(ValueError):
        game.mode_cards(2, "invalid")


@pytest.mark.parametrize("responses,result,attempts", [
    (["hint", "été"], None, 1), (["hint", "menu"], "menu", 0),
    (["hint", "q"], "quit", 0), (["score"], None, 0),
])
def test_cli_hint_commands_and_scoring_still_work(monkeypatch, responses, result, attempts, capsys):
    answers = iter(responses)
    monkeypatch.setattr(cli, "read_input", lambda prompt: next(answers))
    score = game.Score()
    assert cli.drill([card("etre-past-participle")], score) == result
    assert score.attempts == attempts
    assert score.correct == attempts
    if responses[0] == "hint":
        assert "Hint:" in capsys.readouterr().out


def test_cli_quit_and_learn_keep_session_score(monkeypatch, capsys):
    monkeypatch.setattr(cli, "read_input", lambda prompt: "q")
    cli.main()
    assert "À bientôt" in capsys.readouterr().out
    monkeypatch.setattr(cli, "read_input", lambda prompt: "")
    score = game.Score()
    assert cli.learn([card("etre-past-participle")], score) is None
    assert score.attempts == 0


def test_cli_uses_the_same_score_and_rules():
    assert cli.Score is game.Score
    assert cli.answer_matches is game.answer_matches
    assert cli.examples_for is game.examples_for
