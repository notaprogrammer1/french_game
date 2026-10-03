"use strict";

const $ = (id) => document.getElementById(id);
let deck = [], index = 0, mode = "drill-current", level = 1;
let score = { attempts: 0, correct: 0, almost: 0, missed: 0 }, skipped = 0;
let busy = false, answered = false, nextTimer = null, installPrompt = null;

function notice(message = "") {
  $("notice").textContent = message;
  $("notice").hidden = !message;
}

async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(path, { ...options, signal: controller.signal, cache: "no-store" });
    if (!response.ok) throw new Error("Request failed");
    return await response.json();
  } finally { clearTimeout(timer); }
}

function updateScore() {
  $("score").replaceChildren(document.createTextNode(`${score.correct} / ${score.attempts} `));
  const label = document.createElement("span");
  label.textContent = "correct";
  $("score").append(label);
  $("score-details").textContent = `${score.almost} almost · ${score.missed} missed · ${skipped} skipped`;
}

function cancelTransition() {
  clearTimeout(nextTimer);
  nextTimer = null;
  $("transition").hidden = true;
}

function lock(locked) {
  for (const id of ["submit", "hint", "skip", "answer"]) $(id).disabled = locked;
  for (const button of $("accents").children) button.disabled = locked;
  $("start").disabled = busy;
}

function renderPrompt(prompt) {
  $("prompt").replaceChildren();
  const parts = prompt.split("___");
  parts.forEach((part, i) => {
    if (i) {
      const blank = document.createElement("span");
      blank.className = "blank";
      blank.textContent = "…";
      blank.setAttribute("aria-label", "blank");
      $("prompt").append(blank);
    }
    $("prompt").append(document.createTextNode(part));
  });
}

function renderExercise() {
  cancelTransition();
  answered = false;
  notice();
  $("feedback").hidden = true;
  $("hint-text").hidden = true;
  $("hint").setAttribute("aria-expanded", "false");
  $("hint").textContent = "Show hint";
  $("answer").value = "";
  if (index >= deck.length) {
    $("exercise").hidden = true;
    $("finished").hidden = false;
    $("finish-summary").textContent = mode.startsWith("learn-")
      ? `You studied ${deck.length} cards. Your session score is unchanged.`
      : `${score.correct} of ${score.attempts} answers correct this session. ${score.almost} almost, ${score.missed} missed, ${skipped} skipped.`;
    $("again").focus({ preventScroll: true });
    return;
  }
  const card = deck[index], learning = mode.startsWith("learn-");
  $("exercise").hidden = false;
  $("finished").hidden = true;
  $("verb").textContent = card.verb;
  $("meaning").textContent = card.meaning;
  renderPrompt(card.prompt);
  $("translation").textContent = card.translation;
  $("position").textContent = `${index + 1} / ${deck.length}`;
  $("progress").max = deck.length;
  $("progress").value = index;
  $("instruction").textContent = learning ? "LEARN THE FORM" : "COMPLETE THE SENTENCE";
  $("answer-form").hidden = learning;
  document.querySelector(".secondary-controls").hidden = learning;
  $("learn-next").hidden = !learning;
  $("learn-answer").hidden = !learning;
  if (learning) {
    const form = document.createElement("strong");
    form.lang = "fr";
    form.textContent = card.answer;
    $("learn-answer").replaceChildren(form);
    for (const example of card.examples) {
      const sentence = document.createElement("p"), translation = document.createElement("p");
      sentence.lang = "fr";
      sentence.textContent = example.full_sentence;
      translation.className = "small muted";
      translation.textContent = example.translation;
      $("learn-answer").append(sentence, translation);
    }
    const hint = document.createElement("p");
    hint.className = "small";
    hint.textContent = card.hint;
    $("learn-answer").append(hint);
  }
  lock(false);
}

async function startDeck(event) {
  if (event) event.preventDefault();
  if (busy) return;
  const chosenLevel = Number($("level").value), chosenMode = $("mode").value;
  busy = true;
  cancelTransition();
  lock(true);
  $("again").disabled = true;
  notice("Loading practice…");
  try {
    const data = await api(`/api/deck?level=${chosenLevel}&mode=${encodeURIComponent(chosenMode)}`);
    level = chosenLevel;
    mode = chosenMode;
    deck = data.exercises;
    index = 0;
    $("session-label").textContent = `Level ${level} · ${data.verb}`;
    $("settings").open = false;
    busy = false;
    renderExercise();
  } catch {
    notice("Cannot reach the game. Connect to the internet and tap Start practice to try again.");
    $("settings").open = true;
  } finally {
    busy = false;
    lock(answered);
    $("again").disabled = false;
  }
}

function advance() {
  if (busy) return;
  index += 1;
  renderExercise();
}

function scheduleNext(result) {
  $("transition").hidden = false;
  $("pause").hidden = false;
  $("next-label").textContent = "Next exercise shortly…";
  // Keep corrections readable. Pause stops the timer without losing the card.
  nextTimer = setTimeout(advance, result === "correct" ? 1800 : 6500);
}

async function submit(action) {
  if (busy || answered || !deck[index]) return;
  if (action === "answer" && !$("answer").value.trim()) {
    notice("Type your French answer first.");
    $("answer").focus();
    return;
  }
  busy = true;
  lock(true);
  notice();
  try {
    const card = deck[index];
    const data = await api("/api/answer", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: card.id, example_index: card.example_index, answer: $("answer").value, action, score }),
    });
    answered = true;
    score = data.score;
    if (data.result === "skipped") skipped += 1;
    updateScore();
    const titles = { correct: "✓ Correct!", almost: "Almost — check the accents", missed: "Not quite — here’s the correct form", skipped: "Skipped — here’s the answer" };
    $("feedback").className = `feedback ${data.result}`;
    $("feedback-title").textContent = titles[data.result];
    $("feedback-answer").textContent = `${data.answer} · ${data.sentence}`;
    $("feedback-note").textContent = data.result === "correct" ? "Nicely done. Keep going." : data.note;
    $("feedback").hidden = false;
    $("feedback").scrollIntoView({ behavior: "smooth", block: "nearest" });
    scheduleNext(data.result);
  } catch {
    notice("Could not check the answer. Your score has not changed. Check your connection and try again.");
  } finally {
    busy = false;
    lock(answered);
  }
}

$("settings-form").addEventListener("submit", startDeck);
$("answer-form").addEventListener("submit", (event) => { event.preventDefault(); submit("answer"); });
$("skip").addEventListener("click", () => submit("skip"));
$("hint").addEventListener("click", () => {
  const show = $("hint-text").hidden;
  $("hint-text").textContent = deck[index].hint;
  $("hint-text").hidden = !show;
  $("hint").setAttribute("aria-expanded", String(show));
  $("hint").textContent = show ? "Hide hint" : "Show hint";
});
$("accents").addEventListener("click", (event) => {
  if (event.target.tagName !== "BUTTON" || event.target.disabled) return;
  const field = $("answer"), start = field.selectionStart, end = field.selectionEnd;
  field.setRangeText(event.target.textContent, start, end, "end");
  field.focus();
});
$("pause").addEventListener("click", () => {
  clearTimeout(nextTimer);
  nextTimer = null;
  $("next-label").textContent = "Paused. Take your time with the correction.";
  $("pause").hidden = true;
});
// Do not change exercises while the player has switched apps or locked the phone.
document.addEventListener("visibilitychange", () => {
  if (document.hidden && nextTimer !== null) $("pause").click();
});
$("next").addEventListener("click", advance);
$("learn-next").addEventListener("click", advance);
$("again").addEventListener("click", startDeck);
$("change").addEventListener("click", () => { $("settings").open = true; $("level").focus(); });

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt = event;
  $("install").hidden = false;
});
$("install").addEventListener("click", async () => {
  if (!installPrompt) return;
  await installPrompt.prompt();
  installPrompt = null;
  $("install").hidden = true;
});
window.addEventListener("appinstalled", () => { $("install").hidden = true; });
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});

async function initialize() {
  notice("Loading practice…");
  try {
    const settings = await api("/api/settings");
    $("level").replaceChildren(...settings.verbs.map((verb, i) => new Option(`${i + 1} · ${verb}`, i + 1)));
    $("mode").replaceChildren(...Object.entries(settings.modes).map(([value, label]) => new Option(label, value)));
    $("mode").value = mode;
    $("level").disabled = false;
    $("mode").disabled = false;
    $("start").disabled = false;
    await startDeck();
  } catch {
    notice("The game needs a connection to load exercises and check answers. Reconnect, then reload this page.");
  }
}
initialize();
