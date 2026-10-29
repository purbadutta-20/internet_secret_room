const $ = (selector) => document.querySelector(selector);
const state = { playerId: null, rooms: [], completed: [], hintsUsed: 0, currentRoom: 1 };

const roomList = $("#roomList");
const feedback = $("#feedback");
const hintBox = $("#hintBox");

function getPlayerId() {
  let id = localStorage.getItem("secretRoomPlayerId");
  if (!id) {
    id = "player_" + (crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36));
    localStorage.setItem("secretRoomPlayerId", id);
  }
  return id;
}

async function api(path, payload = null, method = "POST") {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (payload) options.body = JSON.stringify(payload);
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || "The signal was interrupted.");
  return data;
}

function roomIsUnlocked(id) {
  return id === 1 || state.completed.includes(id - 1);
}

function renderRoomList() {
  roomList.innerHTML = "";
  state.rooms.forEach((room) => {
    const unlocked = roomIsUnlocked(room.id);
    const done = state.completed.includes(room.id);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "room-item" + (room.id === state.currentRoom ? " active" : "") + (done ? " completed" : "");
    button.disabled = !unlocked;
    button.setAttribute("aria-current", room.id === state.currentRoom ? "step" : "false");
    button.innerHTML = `<span class="room-num" aria-hidden="true">${done ? "✓" : String(room.id).padStart(2, "0")}</span><span><span class="room-name">${escapeHtml(room.name)}</span><span class="room-state">${done ? "SIGNAL RECOVERED" : unlocked ? "AVAILABLE" : "LOCKED // NO ACCESS"}</span></span>`;
    button.addEventListener("click", () => selectRoom(room.id));
    roomList.appendChild(button);
  });
  $("#progressText").textContent = `${state.completed.length} / ${state.rooms.length}`;
  $("#progressFill").style.width = `${(state.completed.length / state.rooms.length) * 100}%`;
  $("#progressBar").setAttribute("aria-valuemax", String(state.rooms.length));
  $("#progressBar").setAttribute("aria-valuenow", String(state.completed.length));
  $("#hintCount").textContent = `HINTS USED: ${state.hintsUsed}`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[char]);
}

function selectRoom(id) {
  if (!roomIsUnlocked(id)) return;
  state.currentRoom = id;
  const room = state.rooms.find((item) => item.id === id);
  $("#roomNumber").textContent = `ROOM ${String(id).padStart(2, "0")} / 05`;
  $("#roomTitle").textContent = room.name;
  $("#roomSubtitle").textContent = room.subtitle;
  $("#roomStory").textContent = room.story;
  $("#roomClue").textContent = room.clue;
  $("#roomStatus").textContent = state.completed.includes(id) ? "SIGNAL RECOVERED" : "SIGNAL FOUND";
  $("#answerInput").value = "";
  $("#answerInput").disabled = state.completed.includes(id);
  $("#answerForm").querySelector("button").disabled = state.completed.includes(id);
  $("#answerForm").querySelector("button").textContent = state.completed.includes(id) ? "SOLVED ✓" : "SUBMIT ↗";
  feedback.textContent = state.completed.includes(id) ? "This room has already been recovered. Continue when ready." : "";
  feedback.className = "feedback" + (state.completed.includes(id) ? " success" : "");
  hintBox.hidden = true;
  hintBox.textContent = "";
  $("#ending").hidden = state.completed.length !== state.rooms.length;
  renderRoomList();
}

async function loadStatus() {
  const data = await api(`/api/status?player_id=${encodeURIComponent(state.playerId)}`, null, "GET");
  state.rooms = data.rooms;
  state.completed = data.progress.completed;
  state.hintsUsed = data.progress.hints_used;
  state.currentRoom = state.completed.length === state.rooms.length ? 5 : Math.min(state.completed.length + 1, 5);
  renderRoomList();
  selectRoom(state.currentRoom);
}

$("#answerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  feedback.className = "feedback";
  feedback.textContent = "CHECKING SIGNAL...";
  const answer = $("#answerInput").value.trim();
  try {
    const result = await api("/api/solve", { player_id: state.playerId, room_id: state.currentRoom, answer });
    if (!result.ok) {
      feedback.textContent = result.message;
      return;
    }
    state.completed = result.completed;
    feedback.textContent = result.game_complete ? "All rooms recovered. The final file is yours." : "Correct. The next room is now available.";
    feedback.className = "feedback success";
    renderRoomList();
    $("#roomStatus").textContent = "SIGNAL RECOVERED";
    $("#answerInput").disabled = true;
    $("#answerForm").querySelector("button").disabled = true;
    $("#answerForm").querySelector("button").textContent = "SOLVED ✓";
    if (result.game_complete) {
      $("#ending").hidden = false;
    } else {
      const next = state.currentRoom + 1;
      setTimeout(() => selectRoom(next), 900);
    }
  } catch (error) {
    feedback.textContent = error.message;
  }
});

$("#hintBtn").addEventListener("click", async () => {
  hintBox.hidden = true;
  try {
    const result = await api("/api/hint", { player_id: state.playerId, room_id: state.currentRoom });
    hintBox.textContent = `HINT: ${result.hint}`;
    hintBox.hidden = false;
    state.hintsUsed = result.hints_used;
    renderRoomList();
  } catch (error) {
    feedback.textContent = error.message;
  }
});

$("#resetBtn").addEventListener("click", async () => {
  if (!window.confirm("Reset all room progress for this player?")) return;
  try {
    await api("/api/reset", { player_id: state.playerId });
    state.completed = [];
    state.hintsUsed = 0;
    selectRoom(1);
    feedback.textContent = "Investigation reset. The signal is waiting.";
    feedback.className = "feedback success";
    $("#ending").hidden = true;
  } catch (error) {
    feedback.textContent = error.message;
  }
});

$("#beginBtn").addEventListener("click", () => {
  $("#gameArea").scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  $("#answerInput").focus({ preventScroll: true });
});

(async function init() {
  state.playerId = getPlayerId();
  $("#playerLabel").textContent = `PLAYER: ${state.playerId.slice(0, 15).toUpperCase()}`;
  try {
    await loadStatus();
  } catch (error) {
    feedback.textContent = "Could not connect to the archive. Make sure the Flask server is running, then refresh.";
    feedback.className = "feedback";
    $("#roomStory").textContent = error.message;
  }
})();
