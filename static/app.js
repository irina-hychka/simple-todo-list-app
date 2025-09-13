// app.js (frontend logic for To-Do app v2)
// -----------------------------------------------------------------------------
// Features:
// - Fetches tasks from backend API (Flask /api/tasks)
// - Add / toggle / delete single tasks
// - Bulk delete (all or completed)
// - Filters: All / Active / Completed
// - Toast notifications for user feedback
// - Dark UI (style.css)
// -----------------------------------------------------------------------------

// Keep track of the currently active filter ("all" | "active" | "completed")
let currentStatus = "all";

// -----------------------------------------------------------------------------
// Toast notification system
// -----------------------------------------------------------------------------
function toast(msg, type = "info") {
  // Create a toast element and append to container
  const cont = document.getElementById("toast-container");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  cont.appendChild(el);

  // Animate in (slight delay so CSS transition applies)
  setTimeout(() => {
    el.classList.add("show");
  }, 10);

  // Auto-hide after 2.5s
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => cont.removeChild(el), 300);
  }, 2500);
}

// -----------------------------------------------------------------------------
// Load tasks from API and render into <ul id="tasks">
// -----------------------------------------------------------------------------
async function loadTasks() {
  const res = await fetch(`/api/tasks?status=${currentStatus}`);
  const tasks = await res.json();

  const list = document.getElementById("tasks");
  list.innerHTML = ""; // clear previous

  tasks.forEach((t) => {
    const li = document.createElement("li");
    li.className = t.is_done ? "done" : "";

    // HTML structure for each task row
    li.innerHTML = `
      <span class="title">${escapeHtml(t.title)}</span>
      <div class="actions">
        <button class="toggle" title="Toggle" data-id="${t.id}">
          ${t.is_done ? "✓" : "○"}
        </button>
        <button class="delete" title="Delete" data-id="${t.id}">✕</button>
      </div>`;

    list.appendChild(li);
  });
}

// -----------------------------------------------------------------------------
// Small helper: escape HTML to prevent XSS in task titles
// -----------------------------------------------------------------------------
function escapeHtml(s) {
  return s.replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c])
  );
}

// -----------------------------------------------------------------------------
// API calls
// -----------------------------------------------------------------------------

// Create new task
async function addTask(title) {
  const res = await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });

  if (res.ok) {
    toast("Task added", "success");
    loadTasks();
  } else {
    toast("Title required", "error");
  }
}

// Toggle (mark done/undone)
async function toggleTask(id) {
  const res = await fetch(`/api/tasks/${id}/toggle`, { method: "PATCH" });
  if (res.ok) {
    toast("Toggled", "success");
    loadTasks();
  } else {
    toast("Not found", "error");
  }
}

// Delete one task
async function deleteTask(id) {
  const res = await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  if (res.ok) {
    toast("Deleted", "success");
    loadTasks();
  } else {
    toast("Not found", "error");
  }
}

// Bulk delete (all or completed)
async function clearAll(status = "all") {
  const res = await fetch(`/api/tasks?status=${status}`, { method: "DELETE" });
  if (res.ok) {
    const data = await res.json();
    toast(`Deleted ${data.deleted}`, "success");
    loadTasks();
  } else {
    toast("Error", "error");
  }
}

// -----------------------------------------------------------------------------
// Event bindings
// -----------------------------------------------------------------------------

// Add form submit handler
document.getElementById("add-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = document.getElementById("new-task");
  const val = input.value.trim();
  if (!val) {
    toast("Title required", "error");
    return;
  }
  addTask(val);
  input.value = "";
  input.focus();
});

// Delegate clicks inside tasks list (toggle/delete buttons)
document.getElementById("tasks").addEventListener("click", (e) => {
  if (e.target.classList.contains("toggle")) {
    toggleTask(e.target.dataset.id);
  } else if (e.target.classList.contains("delete")) {
    deleteTask(e.target.dataset.id);
  }
});

// Filter buttons (All / Active / Completed)
document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll(".filter-btn")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentStatus = btn.dataset.status;
    loadTasks();
  });
});

// Bulk clear buttons
document.getElementById("clear-all").addEventListener("click", () => {
  if (confirm("Delete ALL tasks?")) clearAll("all");
});
document.getElementById("clear-completed").addEventListener("click", () => {
  clearAll("completed");
});

// -----------------------------------------------------------------------------
// Initial load
// -----------------------------------------------------------------------------
loadTasks();
