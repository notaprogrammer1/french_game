"""Small, stateless WSGI adapter for the existing conjugation game.

Run with python -m french_phonics_game.web, or use application with any WSGI
server. The browser holds the session score; no database or server sessions.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from dataclasses import asdict
from pathlib import Path
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs
from wsgiref.simple_server import WSGIServer, make_server

from .conjugation_core import (
    MODES, Score, current_verb, drill_exercises, examples_for, grade_answer,
    mode_cards, note_for, ordered_learn_cards, verb_order,
)
from .conjugations import CONJUGATIONS

STATIC = Path(__file__).with_name("static")
CARDS = {card["id"]: card for card in CONJUGATIONS}
ASSETS = {
    "/": "index.html", "/index.html": "index.html",
    "/app.js": "app.js", "/style.css": "style.css", "/sw.js": "sw.js",
    "/manifest.webmanifest": "manifest.webmanifest",
    "/icon-192.png": "icon-192.png", "/icon-512.png": "icon-512.png",
    "/favicon.svg": "favicon.svg",
}


def build_deck(level: int, mode: str) -> dict:
    cards = mode_cards(level, mode)
    learning = mode.startswith("learn-")
    if learning:
        selected = [(card, 0) for card in ordered_learn_cards(cards)]
    else:
        selected = [(exercise.card, exercise.example_index) for exercise in drill_exercises(cards)]
    exercises = []
    for card, index in selected:
        example = examples_for(card)[index]
        exercise = {
            "id": card["id"], "example_index": index,
            "verb": card["verb"], "meaning": card["meaning"],
            "prompt": example.prompt, "translation": example.translation,
            "hint": f"{card['tense']}. {note_for(card)}",
        }
        if learning:
            exercise.update(answer=card["answer"], examples=[asdict(e) for e in examples_for(card)])
        exercises.append(exercise)
    return {"verb": current_verb(level), "exercises": exercises}


def score_from(values: object) -> Score:
    if not isinstance(values, dict):
        raise ValueError("Invalid session score.")
    counts = [values.get(key, 0) for key in ("attempts", "correct", "almost")]
    if any(type(n) is not int or not 0 <= n <= 1_000_000 for n in counts):
        raise ValueError("Invalid session score.")
    score = Score(*counts)
    if score.missed < 0:
        raise ValueError("Invalid session score.")
    return score


def check_answer(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Expected an answer object.")
    card_id = payload.get("id")
    if not isinstance(card_id, str) or card_id not in CARDS:
        raise ValueError("Unknown exercise.")
    card = CARDS[card_id]
    index = payload.get("example_index", 0)
    examples = examples_for(card)
    if type(index) is not int or not 0 <= index < len(examples):
        raise ValueError("Unknown example.")
    action = payload.get("action", "answer")
    if action not in ("answer", "skip"):
        raise ValueError("Unknown action.")
    answer = payload.get("answer", "")
    if not isinstance(answer, str) or len(answer) > 512:
        raise ValueError("Answer must be text of at most 512 characters.")
    if action == "answer" and not answer.strip():
        raise ValueError("Type an answer first.")
    score = score_from(payload.get("score", {}))
    result = "skipped" if action == "skip" else grade_answer(answer, card)
    if result != "skipped":
        score.record(result)
    return {
        "result": result, "answer": card["answer"],
        "sentence": examples[index].full_sentence, "note": note_for(card),
        "score": {**asdict(score), "missed": score.missed, "summary": score.summary()},
    }


def application(environ, start_response):
    method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
    status = "200 OK"
    content_type = "application/json; charset=utf-8"
    cache = "no-store"
    try:
        if path == "/api/settings" and method == "GET":
            data = {"verbs": verb_order(), "modes": MODES}
        elif path == "/api/deck" and method == "GET":
            query = parse_qs(environ.get("QUERY_STRING", ""))
            level = int(query.get("level", ["1"])[0])
            if not 1 <= level <= len(verb_order()):
                raise ValueError("Choose a valid level.")
            data = build_deck(level, query.get("mode", ["drill-current"])[0])
        elif path == "/api/answer" and method == "POST":
            size = int(environ.get("CONTENT_LENGTH") or 0)
            if not 0 < size <= 8192:
                raise ValueError("Invalid request size.")
            data = check_answer(json.loads(environ["wsgi.input"].read(size)))
        elif path in ASSETS and method in ("GET", "HEAD"):
            file = STATIC / ASSETS[path]
            body = file.read_bytes()
            content_type = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            if file.suffix in (".html", ".css", ".js"):
                content_type += "; charset=utf-8"
            if file.suffix == ".webmanifest":
                content_type = "application/manifest+json"
            cache = "no-cache"
            data = None
        elif path in ASSETS or path in ("/api/settings", "/api/deck", "/api/answer"):
            status, data = "405 Method Not Allowed", {"error": "Method not allowed."}
        else:
            status, data = "404 Not Found", {"error": "Not found."}
    except (ValueError, TypeError, UnicodeError):
        status, data = "400 Bad Request", {"error": "Invalid request. Check the level, mode, or answer."}
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", content_type), ("Content-Length", str(len(body))),
        ("Cache-Control", cache), ("X-Content-Type-Options", "nosniff"),
    ]
    start_response(status, headers)
    return [] if method == "HEAD" else [body]


class ThreadedServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Play French conjugations in a browser.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()
    with make_server(args.host, args.port, application, server_class=ThreadedServer) as server:
        print(f"French Conjugations: http://{args.host}:{args.port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
