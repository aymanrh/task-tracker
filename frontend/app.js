// Task Tracker frontend (baseline). Talks to the FastAPI backend.
const API = "http://localhost:8000";

const COLUMNS = [
  { key: "todo", label: "To do" },
  { key: "in_progress", label: "In progress" },
  { key: "done", label: "Done" },
];

const board = document.getElementById("board");
const backdrop = document.getElementById("modal-backdrop");
const form = document.getElementById("task-form");
const formError = document.getElementById("form-error");
const modalTitle = document.getElementById("modal-title");

// Current query filters (extended by features).
const filters = {};

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.status === 204 ? null : res.json();
}

function buildQuery() {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== null && v !== "") params.set(k, v);
  }
  const q = params.toString();
  return q ? `?${q}` : "";
}

async function loadBoard() {
  let tasks = [];
  try {
    tasks = await api("/tasks" + buildQuery());
  } catch (e) {
    board.innerHTML = `<p class="error">Cannot reach API at ${API}. Is the backend running?</p>`;
    return;
  }
  render(tasks);
}

function render(tasks) {
  board.innerHTML = "";
  for (const col of COLUMNS) {
    const inCol = tasks.filter((t) => t.status === col.key);
    const el = document.createElement("section");
    el.className = "column";
    el.innerHTML = `<h2>${col.label} <span>${inCol.length}</span></h2>`;
    if (inCol.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "No tasks";
      el.appendChild(empty);
    }
    for (const t of inCol) el.appendChild(cardEl(t));
    board.appendChild(el);
  }
}

function cardEl(t) {
  const card = document.createElement("div");
  card.className = `card prio-${t.priority}`;
  card.onclick = () => openModal(t);

  const parts = [`<div class="title">${escapeHtml(t.title)}</div>`];
  if (t.description) parts.push(`<div class="desc">${escapeHtml(t.description)}</div>`);

  const meta = [`<span class="pill">${t.priority}</span>`];
  if (t.assignee) meta.push(`<span class="pill assignee">${escapeHtml(t.assignee)}</span>`);
  // Feature hooks append extra meta here (see cardExtras).
  meta.push(...cardExtras(t));
  parts.push(`<div class="meta">${meta.join("")}</div>`);

  card.innerHTML = parts.join("");
  return card;
}

// Baseline adds nothing; features override to add pills/chips.
function cardExtras(_t) {
  return [];
}

// Baseline modal has no extra fields; features inject inputs into #feature-fields.
function renderFeatureFields(_t) {
  document.getElementById("feature-fields").innerHTML = "";
}

function collectFeatureFields(_payload) {
  // Features add their values to the payload here.
}

function openModal(task = null) {
  formError.hidden = true;
  form.reset();
  document.getElementById("task-id").value = task ? task.id : "";
  modalTitle.textContent = task ? "Edit task" : "New task";
  if (task) {
    document.getElementById("f-title").value = task.title;
    document.getElementById("f-description").value = task.description || "";
    document.getElementById("f-status").value = task.status;
    document.getElementById("f-priority").value = task.priority;
    document.getElementById("f-assignee").value = task.assignee || "";
  }
  renderFeatureFields(task);
  ensureDeleteButton(task);
  backdrop.hidden = false;
}

function ensureDeleteButton(task) {
  const existing = document.getElementById("delete-btn");
  if (existing) existing.remove();
  if (!task) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.id = "delete-btn";
  btn.className = "btn";
  btn.textContent = "Delete";
  btn.onclick = async () => {
    await api(`/tasks/${task.id}`, { method: "DELETE" });
    closeModal();
    loadBoard();
  };
  document.querySelector(".modal-actions").prepend(btn);
}

function closeModal() {
  backdrop.hidden = true;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.hidden = true;
  const id = document.getElementById("task-id").value;
  const payload = {
    title: document.getElementById("f-title").value,
    description: document.getElementById("f-description").value,
    status: document.getElementById("f-status").value,
    priority: document.getElementById("f-priority").value,
    assignee: document.getElementById("f-assignee").value,
  };
  collectFeatureFields(payload);
  try {
    if (id) {
      await api(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(payload) });
    } else {
      await api("/tasks", { method: "POST", body: JSON.stringify(payload) });
    }
    closeModal();
    loadBoard();
  } catch (err) {
    formError.textContent = err.message;
    formError.hidden = false;
  }
});

document.getElementById("new-task-btn").onclick = () => openModal();
document.getElementById("cancel-btn").onclick = closeModal;
backdrop.addEventListener("click", (e) => { if (e.target === backdrop) closeModal(); });

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

loadBoard();
