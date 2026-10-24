/* Unofficial Claude certification mock exams, browser edition.
 * Static and offline: loads data/bank.json (built by tools/build_web_bundle.py) and stores
 * progress only in this browser's localStorage. All text is inserted with textContent,
 * never innerHTML, so question content can never execute as markup.
 */
"use strict";

const STORE_KEY = "claude-cert-zero-to-hero.progress.v1";
const WEAK_THRESHOLD = 70;
const $ = (id) => document.getElementById(id);

let bank = null;
let session = null;
let timerHandle = null;

// ---------------------------------------------------------------- storage
function loadProgress() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    const data = raw ? JSON.parse(raw) : null;
    if (data && Array.isArray(data.attempts) && data.questions) return data;
  } catch (_) { /* storage unavailable or corrupt: start fresh */ }
  return { version: 1, attempts: [], questions: {} };
}
function saveProgress(data) {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); } catch (_) { /* ignore */ }
}

// ---------------------------------------------------------------- dom helpers
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return node;
}
function show(id, visible = true) { $(id).hidden = !visible; }

// On the GitHub Pages site (body[data-site="pages"]) Markdown pages are published as .html,
// with README.md becoming index.html. When served from the repository, link to the .md file.
function studyHref(module) {
  const path = document.body.dataset.site === "pages"
    ? module.replace(/(^|\/)README\.md$/, "$1index.html").replace(/\.md$/, ".html")
    : module;
  return `../../${path}`;
}

// ---------------------------------------------------------------- selection
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function allocate(weights, count) {
  const total = Object.values(weights).reduce((s, w) => s + w, 0);
  const raw = Object.fromEntries(Object.entries(weights).map(([d, w]) => [d, (count * w) / total]));
  const alloc = Object.fromEntries(Object.entries(raw).map(([d, v]) => [d, Math.floor(v)]));
  let left = count - Object.values(alloc).reduce((s, n) => s + n, 0);
  Object.keys(raw).sort((a, b) => (raw[b] - alloc[b]) - (raw[a] - alloc[a]))
    .slice(0, left).forEach((d) => { alloc[d] += 1; });
  return alloc;
}
function selectQuestions(track, count, domain, weakIds) {
  const order = (qs) => {
    const s = shuffle(qs);
    return weakIds ? s.sort((a, b) => weakIds.has(b.id) - weakIds.has(a.id)) : s;
  };
  let pool = track.questions.filter((q) => domain === "all" || q.domain === Number(domain));
  count = Math.min(count, pool.length);
  if (domain !== "all") return order(pool).slice(0, count);
  const byDomain = {};
  pool.forEach((q) => { (byDomain[q.domain] ||= []).push(q); });
  const weights = {};
  track.domains.forEach((d) => { if (byDomain[d.id]) weights[d.id] = d.weight; });
  const alloc = allocate(weights, count);
  let chosen = [], spare = [];
  for (const [d, qs] of Object.entries(byDomain)) {
    const o = order(qs);
    chosen = chosen.concat(o.slice(0, alloc[d]));
    spare = spare.concat(o.slice(alloc[d]));
  }
  chosen = chosen.concat(shuffle(spare).slice(0, count - chosen.length));
  return shuffle(chosen);
}

// ---------------------------------------------------------------- setup screen
function currentTrack() { return bank.tracks.find((t) => t.code === $("track").value); }

function populateSources() {
  const track = currentTrack();
  const src = $("source");
  src.replaceChildren(el("option", { value: "all", text: "All domains (blueprint-weighted)" }));
  track.domains.forEach((d) => src.append(el("option", { value: `d${d.id}`, text: `Domain ${d.id}: ${d.name} (${d.weight}%)` })));
  track.forms.forEach((f) => src.append(el("option", { value: `form:${f.id}`, text: `${f.title} — ${f.question_ids.length} items, ${f.minutes} min` })));
  $("bank-info").textContent = `${track.questions.length} practice questions available for ${track.code}. Official exam: ${track.items} items in ${track.minutes} minutes.`;
}

function syncCount() {
  const track = currentTrack();
  const isForm = $("source").value.startsWith("form:");
  $("count").disabled = isForm;
  if ($("mode").value === "timed" && $("source").value === "all") $("count").value = track.items;
}

// ---------------------------------------------------------------- session
function startSession() {
  const track = currentTrack();
  const mode = $("mode").value;
  const source = $("source").value;
  const progress = loadProgress();
  const weakIds = $("weak").checked
    ? new Set(Object.entries(progress.questions).filter(([, s]) => s.last_correct === false).map(([id]) => id))
    : null;

  let questions, minutes;
  if (source.startsWith("form:")) {
    const form = track.forms.find((f) => f.id === source.slice(5));
    const byId = Object.fromEntries(track.questions.map((q) => [q.id, q]));
    questions = shuffle(form.question_ids.map((id) => byId[id]).filter(Boolean));
    minutes = form.minutes;
  } else {
    const count = Math.max(1, parseInt($("count").value, 10) || 20);
    const domain = source === "all" ? "all" : source.slice(1);
    questions = selectQuestions(track, count, domain, weakIds);
    minutes = Math.max(1, Math.round((track.minutes * questions.length) / track.items));
  }
  if (!questions.length) { alert("No questions match that selection."); return; }

  session = {
    track, mode, questions, index: 0, responses: {}, skipped: [], start: Date.now(),
    deadline: mode === "timed" ? Date.now() + minutes * 60000 : null,
  };
  show("setup", false); show("results", false); show("history", false); show("quiz");
  if (session.deadline) startTimer(); else show("timer", false);
  renderQuestion();
}

function startTimer() {
  show("timer");
  clearInterval(timerHandle);
  const tick = () => {
    const left = Math.max(0, session.deadline - Date.now());
    const m = Math.floor(left / 60000), s = Math.floor((left % 60000) / 1000);
    $("timer").textContent = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    $("timer").classList.toggle("low", left < 5 * 60000);
    if (left === 0) { clearInterval(timerHandle); finishSession(true); }
  };
  tick();
  timerHandle = setInterval(tick, 1000);
}

function renderQuestion() {
  const q = session.questions[session.index];
  const multi = q.type === "multiple";
  $("qmeta").textContent = `Question ${session.index + 1} of ${session.questions.length} · ${q.id} · Domain ${q.domain} · ${q.difficulty}`;
  $("scenario").textContent = q.scenario;
  $("question").textContent = q.question;
  $("select-hint").textContent = multi ? `Choose ${q.answer.length}.` : "Choose one.";
  const form = $("options");
  form.replaceChildren();
  Object.entries(q.options).sort().forEach(([letter, text]) => {
    const input = el("input", { type: multi ? "checkbox" : "radio", name: "opt", value: letter, id: `opt-${letter}` });
    form.append(el("label", { class: "option", for: `opt-${letter}` }, input, el("span", { text: `${letter}. ${text}` })));
  });
  show("feedback", false);
  show("submit"); show("next", false);
  $("skip").hidden = session.mode !== "timed";
}

function chosenLetters() {
  return [...$("options").querySelectorAll("input:checked")].map((i) => i.value).sort();
}
function isCorrect(q, given) {
  return Array.isArray(given) && given.length === q.answer.length && given.every((g, i) => g === [...q.answer].sort()[i]);
}

function submitAnswer() {
  const q = session.questions[session.index];
  const given = chosenLetters();
  if (given.length !== q.answer.length) {
    alert(`Select exactly ${q.answer.length} option(s).`);
    return;
  }
  session.responses[q.id] = given;
  if (session.mode === "learn") {
    renderFeedback(q, given);
    show("submit", false); show("next");
  } else {
    advance();
  }
}

function renderFeedback(q, given) {
  const ok = isCorrect(q, given);
  $("options").querySelectorAll("label.option").forEach((label) => {
    const letter = label.querySelector("input").value;
    label.querySelector("input").disabled = true;
    if (q.answer.includes(letter)) label.classList.add("correct");
    else if (given.includes(letter)) label.classList.add("wrong");
  });
  const fb = $("feedback");
  fb.className = `feedback ${ok ? "good" : "bad"}`;
  fb.replaceChildren(feedbackContent(q, ok));
  show("feedback");
}

function feedbackContent(q, ok) {
  const frag = document.createDocumentFragment();
  frag.append(el("p", {}, el("strong", { text: ok ? "Correct. " : "Incorrect. " }), `Answer: ${q.answer.join(", ")}`));
  frag.append(el("p", { text: q.explanation }));
  const list = el("ul");
  Object.entries(q.why_incorrect).sort().forEach(([l, why]) => list.append(el("li", { text: `${l}: ${why}` })));
  frag.append(list);
  if (q.module) frag.append(el("p", { class: "muted" }, "Study: ", el("a", { href: studyHref(q.module), text: q.module })));
  if (q.references && q.references[0]) {
    frag.append(el("p", { class: "muted" }, "Docs: ", el("a", { href: q.references[0], rel: "noopener noreferrer", target: "_blank", text: q.references[0] })));
  }
  return frag;
}

function skipQuestion() {
  session.skipped.push(session.questions[session.index]);
  advance();
}

function advance() {
  session.index += 1;
  if (session.index >= session.questions.length) {
    const pending = session.skipped.filter((q) => !(q.id in session.responses));
    if (pending.length) {
      // Revisit skipped questions at the end, as in the real exam interface.
      session.questions = session.questions.concat(pending);
      session.skipped = [];
    } else {
      finishSession(false);
      return;
    }
  }
  renderQuestion();
}

// ---------------------------------------------------------------- results
function finishSession(timedOut) {
  clearInterval(timerHandle);
  show("timer", false); show("quiz", false);
  const { track, mode } = session;
  const unique = [...new Map(session.questions.map((q) => [q.id, q])).values()];
  const domains = {};
  unique.forEach((q) => {
    const d = (domains[q.domain] ||= { correct: 0, total: 0 });
    d.total += 1;
    if (isCorrect(q, session.responses[q.id])) d.correct += 1;
  });
  const correct = Object.values(domains).reduce((s, d) => s + d.correct, 0);
  const pct = unique.length ? (100 * correct) / unique.length : 0;
  const missed = unique.filter((q) => !isCorrect(q, session.responses[q.id]));

  const progress = loadProgress();
  progress.attempts.push({
    track: track.code, mode, total: unique.length, correct, percent: Math.round(pct * 10) / 10,
    timed_out: timedOut, finished_at: new Date().toISOString(),
  });
  unique.forEach((q) => {
    if (mode === "learn" && !(q.id in session.responses)) return;
    const s = (progress.questions[q.id] ||= { seen: 0, correct: 0, last_correct: null });
    const ok = isCorrect(q, session.responses[q.id]);
    s.seen += 1; s.correct += ok ? 1 : 0; s.last_correct = ok;
  });
  saveProgress(progress);

  const box = $("results");
  const minutes = Math.round((Date.now() - session.start) / 60000);
  box.replaceChildren(
    el("h2", { text: `${track.code} ${mode} result` }),
    el("p", {}, el("strong", { text: `${correct} / ${unique.length} correct (${pct.toFixed(1)}%)` }),
      ` in about ${minutes} min${timedOut ? " — time expired; unanswered questions count as incorrect" : ""}.`),
  );
  const table = el("table");
  table.append(el("tr", {}, el("th", { text: "Domain" }), el("th", { text: "Score" }), el("th", { text: "" })));
  track.domains.forEach((d) => {
    const r = domains[d.id];
    if (!r) return;
    const p = (100 * r.correct) / r.total;
    const fill = el("span");
    fill.style.width = `${p.toFixed(0)}%`; // CSSOM, not an inline style attribute, so the CSP allows it
    const bar = el("div", { class: "bar" }, fill);
    table.append(el("tr", {},
      el("td", {}, `D${d.id} ${d.name}`, p < WEAK_THRESHOLD ? el("span", { class: "flag", text: "  review" }) : ""),
      el("td", { class: "num", text: `${r.correct}/${r.total} (${p.toFixed(0)}%)` }),
      el("td", {}, bar)));
  });
  box.append(table);

  const counts = {};
  missed.forEach((q) => { if (q.module) counts[q.module] = (counts[q.module] || 0) + 1; });
  const recs = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  if (recs.length) {
    const ul = el("ul");
    recs.forEach(([m, n]) => ul.append(el("li", {}, el("a", { href: studyHref(m), text: m }), ` (${n} missed)`)));
    box.append(el("h3", { text: "Recommended study" }), ul);
  }
  if (mode === "timed" && missed.length) {
    box.append(el("h3", { text: "Review missed questions" }));
    missed.forEach((q) => {
      const item = el("div", { class: "review-item" },
        el("p", { class: "qmeta", text: `${q.id} · Domain ${q.domain}` }),
        el("p", { text: q.scenario }), el("p", { class: "question", text: q.question }));
      const opts = el("ul");
      Object.entries(q.options).sort().forEach(([l, t]) => opts.append(el("li", { text: `${l}. ${t}` })));
      item.append(opts, el("p", { class: "muted", text: `You chose: ${(session.responses[q.id] || ["nothing"]).join(", ")}` }), feedbackContent(q, false));
      box.append(item);
    });
  }
  box.append(
    el("p", { class: "muted", text: "Unofficial practice. This percentage is not an Anthropic scaled score (100–1,000, cut score 720) and does not predict an official result." }),
    el("div", { class: "actions" },
      el("button", { class: "primary", text: "New session", onclick: () => { show("results", false); show("setup"); } }),
      el("button", { text: "Retry missed questions", onclick: () => retryMissed(missed) })),
  );
  show("results");
  box.scrollIntoView({ behavior: "smooth" });
}

function retryMissed(missed) {
  if (!missed.length) { alert("Nothing missed. Well done."); return; }
  session = { track: session.track, mode: "learn", questions: shuffle(missed), index: 0, responses: {}, skipped: [], start: Date.now(), deadline: null };
  show("results", false); show("quiz"); show("timer", false);
  renderQuestion();
}

function renderHistory() {
  const data = loadProgress();
  const box = $("history");
  box.replaceChildren(el("h2", { text: "History (this browser only)" }));
  if (!data.attempts.length) {
    box.append(el("p", { class: "muted", text: "No attempts yet." }));
  } else {
    const table = el("table");
    table.append(el("tr", {}, ...["Finished", "Track", "Mode", "Score"].map((h) => el("th", { text: h }))));
    data.attempts.slice(-25).reverse().forEach((a) => table.append(el("tr", {},
      el("td", { text: a.finished_at.replace("T", " ").slice(0, 16) }), el("td", { text: a.track }),
      el("td", { text: a.mode }), el("td", { class: "num", text: `${a.correct}/${a.total} (${a.percent}%)` }))));
    box.append(table);
  }
  show("history");
  box.scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- boot
async function boot() {
  try {
    const res = await fetch("data/bank.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    bank = await res.json();
  } catch (err) {
    $("bank-info").textContent = "Could not load data/bank.json. Serve the repository with `python3 -m http.server` "
      + "from the repository root and open /18-mock-examinations/web/. (" + err.message + ")";
    $("start").disabled = true;
    return;
  }
  bank.tracks.forEach((t) => $("track").append(el("option", { value: t.code, text: `${t.code} — ${t.name}` })));
  populateSources();
  $("track").addEventListener("change", () => { populateSources(); syncCount(); });
  $("mode").addEventListener("change", syncCount);
  $("source").addEventListener("change", syncCount);
  $("start").addEventListener("click", startSession);
  $("submit").addEventListener("click", submitAnswer);
  $("next").addEventListener("click", advance);
  $("skip").addEventListener("click", skipQuestion);
  $("finish").addEventListener("click", () => { if (confirm("Finish now? Unanswered questions count as incorrect.")) finishSession(false); });
  $("history-btn").addEventListener("click", renderHistory);
  $("reset").addEventListener("click", () => {
    if (confirm("Delete all locally stored progress?")) { try { localStorage.removeItem(STORE_KEY); } catch (_) { /* ignore */ } renderHistory(); }
  });
  $("options").addEventListener("submit", (e) => e.preventDefault());
}

boot();
