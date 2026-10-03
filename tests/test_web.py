import io
import json

import pytest

from french_phonics_game.web import application


def request(path, method="GET", payload=None, raw=None, query=""):
    body = raw if raw is not None else json.dumps(payload).encode() if payload is not None else b""
    response = {}
    def start(status, headers):
        response.update(status=int(status.split()[0]), headers=dict(headers))
    response["body"] = b"".join(application({
        "REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
        "CONTENT_LENGTH": str(len(body)), "wsgi.input": io.BytesIO(body),
    }, start))
    return response


def answer(**changes):
    return {"id": "conjugation:etre-past-participle", "answer": "été", **changes}


def test_settings_and_deck_share_existing_verb_levels():
    settings = json.loads(request("/api/settings")["body"])
    assert len(settings["verbs"]) == 20
    assert len(settings["modes"]) == 5
    drill = request("/api/deck", query="level=2&mode=drill-cumulative")
    assert drill["status"] == 200
    assert drill["headers"]["Cache-Control"] == "no-store"
    cards = json.loads(drill["body"])["exercises"]
    assert len(cards) == 10
    assert {card["verb"] for card in cards} == {"être", "avoir"}
    assert all("answer" not in card and "examples" not in card for card in cards)
    learn = json.loads(request("/api/deck", query="level=2&mode=learn-current")["body"])["exercises"]
    assert len(learn) == 5
    assert all(card["verb"] == "avoir" and card["answer"] and card["examples"] for card in learn)


def test_grading_and_session_score_use_shared_rules():
    score = {}
    for text, expected in [("été", "correct"), ("ete", "almost"), ("était", "missed")]:
        response = request("/api/answer", "POST", answer(answer=text, score=score))
        assert response["status"] == 200
        data = json.loads(response["body"])
        assert data["result"] == expected
        assert data["sentence"] == "Il a été malade hier."
        score = data["score"]
    assert (score["attempts"], score["correct"], score["almost"], score["missed"]) == (3, 1, 1, 1)
    fresh = json.loads(request("/api/answer", "POST", answer())["body"])
    assert fresh["score"]["attempts"] == 1  # Other browsers have independent sessions.


def test_skip_reveals_answer_without_counting_an_attempt():
    data = json.loads(request("/api/answer", "POST", answer(action="skip", answer=""))["body"])
    assert data["result"] == "skipped"
    assert data["answer"] == "été"
    assert data["score"]["attempts"] == 0


@pytest.mark.parametrize("payload", [
    [], answer(id="missing"), answer(id=[]), answer(answer=""), answer(answer=42),
    answer(answer="x" * 513), answer(example_index=-1), answer(example_index=True),
    answer(action="unknown"), answer(score=[]), answer(score={"correct": 2}),
    answer(score={"attempts": -1}), answer(score={"attempts": True}),
])
def test_invalid_answers_return_a_client_error(payload):
    assert request("/api/answer", "POST", payload)["status"] == 400


@pytest.mark.parametrize("query", ["level=0", "level=21", "level=abc", "mode=invalid"])
def test_invalid_practice_settings(query):
    assert request("/api/deck", query=query)["status"] == 400


def test_malformed_json_oversized_requests_and_routes():
    assert request("/api/answer", "POST", raw=b"{")["status"] == 400
    assert request("/api/answer", "POST", raw=b"x" * 8193)["status"] == 400
    assert request("/api/answer")["status"] == 405
    assert request("/api/deck", "POST")["status"] == 405
    assert request("/../pyproject.toml")["status"] == 404
    assert request("/missing")["status"] == 404


@pytest.mark.parametrize("path,mime", [
    ("/", "text/html"), ("/app.js", "text/javascript"), ("/style.css", "text/css"),
    ("/sw.js", "text/javascript"), ("/manifest.webmanifest", "application/manifest+json"),
    ("/icon-192.png", "image/png"), ("/icon-512.png", "image/png"),
])
def test_web_and_pwa_assets(path, mime):
    response = request(path)
    assert response["status"] == 200
    assert mime in response["headers"]["Content-Type"]
    assert len(response["body"]) == int(response["headers"]["Content-Length"])
    head = request(path, "HEAD")
    assert head["status"] == 200 and head["body"] == b""


def test_pwa_has_installable_icons_and_start_url():
    manifest = json.loads(request("/manifest.webmanifest")["body"])
    assert manifest["display"] == "standalone"
    assert request(manifest["start_url"])["status"] == 200
    for icon in manifest["icons"]:
        assert icon["sizes"] in {"192x192", "512x512"}
        assert request(icon["src"])["body"].startswith(b"\x89PNG")
