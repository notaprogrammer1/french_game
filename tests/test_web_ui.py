"""Optional real-browser checks: FRENCH_GAME_BROWSER_TESTS=1 python -m pytest.

Install playwright and its Chromium browser first. These run in GitHub Actions;
the default CLI test suite does not require a browser or listening sockets.
"""

import os
import threading
from pathlib import Path
from wsgiref.simple_server import make_server

import pytest

from french_phonics_game import conjugation_core
from french_phonics_game.conjugations import CONJUGATIONS
from french_phonics_game.web import ThreadedServer, application

pytestmark = pytest.mark.skipif(
    os.environ.get("FRENCH_GAME_BROWSER_TESTS") != "1",
    reason="Set FRENCH_GAME_BROWSER_TESTS=1 to run browser checks.",
)


@pytest.fixture(scope="module")
def website():
    server = make_server("127.0.0.1", 0, application, server_class=ThreadedServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture
def phone(website, monkeypatch):
    # Keep the exercise order deterministic for browser assertions.
    monkeypatch.setattr(conjugation_core.random, "shuffle", lambda deck: None)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={"width": 393, "height": 851}, is_mobile=True, has_touch=True)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(website)
        page.locator("#exercise").wait_for(state="visible")
        yield page
        browser.close()
        assert errors == []


def test_phone_layout_and_touch_targets(phone):
    assert phone.locator("#position").inner_text() == "1 / 5"
    assert phone.locator("#verb").inner_text() == "être"
    for width in [320, 360, 393, 768, 1280]:
        phone.set_viewport_size({"width": width, "height": 851})
        assert phone.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    phone.set_viewport_size({"width": 393, "height": 851})
    for selector in ["#answer", "#submit", "#hint", "#skip", ".accents button"]:
        for control in phone.locator(selector).all():
            assert control.bounding_box()["height"] >= 44
    Path("artifacts").mkdir(exist_ok=True)
    phone.screenshot(path="artifacts/phone.png", full_page=True)


def test_hint_accent_insertion_correct_feedback_and_auto_next(phone):
    phone.locator("#hint").click()
    assert "present" in phone.locator("#hint-text").inner_text()
    assert phone.locator("#score").inner_text() == "0 / 0 correct"
    phone.locator("#answer").fill("su")
    phone.locator("#answer").evaluate("input => input.setSelectionRange(2, 2)")
    phone.get_by_role("button", name="é", exact=True).click()
    assert phone.locator("#answer").input_value() == "sué"
    phone.locator("#answer").fill("suis")
    phone.locator("#answer").press("Enter")
    phone.locator(".feedback.correct").wait_for(state="visible")
    assert "Correct!" in phone.locator("#feedback-title").inner_text()
    assert phone.locator("#score").inner_text() == "1 / 1 correct"
    phone.wait_for_function("document.getElementById('position').textContent === '2 / 5'")
    assert phone.locator("#answer").input_value() == ""
    assert not phone.locator("#feedback").is_visible()
    assert phone.locator("#submit").is_enabled()


def test_incorrect_almost_skip_pause_and_score(phone):
    phone.locator("#answer").fill("wrong")
    phone.locator("#submit").click()
    phone.locator(".feedback.missed").wait_for(state="visible")
    phone.locator("#pause").click()
    assert "suis" in phone.locator("#feedback-answer").inner_text()
    assert "1 missed" in phone.locator("#score-details").inner_text()
    phone.locator("#next").click()
    phone.locator("#skip").click()
    phone.locator(".feedback.skipped").wait_for(state="visible")
    phone.locator("#pause").click()
    assert phone.locator("#score").inner_text() == "0 / 1 correct"
    assert "1 skipped" in phone.locator("#score-details").inner_text()
    phone.locator("#next").click()
    phone.locator("#answer").fill("ete")
    phone.locator("#submit").click()
    phone.locator(".feedback.almost").wait_for(state="visible")
    phone.locator("#pause").click()
    assert "été" in phone.locator("#feedback-answer").inner_text()
    assert phone.locator("#score").inner_text() == "0 / 2 correct"
    assert "1 almost" in phone.locator("#score-details").inner_text()


def test_all_modes_and_learn_do_not_score(phone):
    for mode in ["learn-current", "learn-cumulative", "drill-cumulative", "mixed-cumulative"]:
        phone.locator("#settings").evaluate("node => node.open = true")
        phone.locator("#level").select_option("2")
        phone.locator("#mode").select_option(mode)
        phone.locator("#start").click()
        phone.wait_for_function("!document.getElementById('settings').open")
        assert phone.locator("#position").inner_text() == ("1 / 5" if mode == "learn-current" else "1 / 10")
        if mode.startswith("learn-"):
            assert phone.locator("#learn-answer").is_visible()
            assert not phone.locator("#answer-form").is_visible()
            phone.locator("#learn-next").click()
            assert phone.locator("#position").inner_text().startswith("2 /")
            assert phone.locator("#score").inner_text() == "0 / 0 correct"
        else:
            assert phone.locator("#answer-form").is_visible()


def test_deck_end_restarts_and_session_score_continues(phone):
    for card in CONJUGATIONS[:5]:
        phone.locator("#answer").fill(card["answer"])
        phone.locator("#submit").click()
        phone.locator(".feedback.correct").wait_for(state="visible")
        phone.locator("#next").click()
    phone.locator("#finished").wait_for(state="visible")
    assert "5 of 5" in phone.locator("#finish-summary").inner_text()
    phone.locator("#again").click()
    phone.locator("#exercise").wait_for(state="visible")
    assert phone.locator("#score").inner_text() == "5 / 5 correct"
    assert phone.locator("#position").inner_text() == "1 / 5"


def test_failed_requests_do_not_score_or_advance(phone):
    phone.route("**/api/answer", lambda route: route.abort())
    phone.locator("#answer").fill("suis")
    phone.locator("#submit").click()
    phone.wait_for_function("document.getElementById('notice').textContent.includes('Could not check')")
    assert phone.locator("#score").inner_text() == "0 / 0 correct"
    assert phone.locator("#position").inner_text() == "1 / 5"
    assert phone.locator("#answer").input_value() == "suis"
    assert phone.locator("#submit").is_enabled()
    phone.unroute("**/api/answer")
    phone.locator("#submit").click()
    phone.locator(".feedback.correct").wait_for(state="visible")
    assert phone.locator("#score").inner_text() == "1 / 1 correct"


def test_pwa_service_worker_and_offline_explanation(phone):
    phone.wait_for_function("navigator.serviceWorker.controller !== null")
    assert phone.evaluate("navigator.serviceWorker.controller.scriptURL.endsWith('/sw.js')")
    phone.context.set_offline(True)
    phone.reload()
    phone.wait_for_function("document.getElementById('notice').textContent.includes('needs a connection')")
    assert phone.locator("h1").inner_text() == "Conjugations."
    assert not phone.locator("#exercise").is_visible()
