from pathlib import Path
import os
import sqlite3
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "secret_room.db"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-key")

ROOMS = [
    {
        "id": 1, "name": "The Entrance", "subtitle": "A message in the static",
        "story": "The monitor flickers awake. Someone left a message for whoever found this place.",
        "clue": "The first note reads: “When the world looks ordinary, LOOK CLOSER.” Enter the two words without a space.",
        "answer": "LOOKCLOSER",
        "hint": "Join the two words printed in the note. Do not include a space."
    },
    {
        "id": 2, "name": "The Terminal", "subtitle": "A small shift in the alphabet",
        "story": "A terminal blinks in the dark. One line survived the corruption: KHOOR.",
        "clue": "The archive says every letter was moved three places forward. Move each letter three places backward to recover the word.",
        "answer": "HELLO",
        "hint": "K becomes H, H becomes E. Apply the same shift to every letter."
    },
    {
        "id": 3, "name": "The Forgotten Archive", "subtitle": "The file that should not exist",
        "story": "A folder contains three fragments. Together, they point to a strange phrase.",
        "clue": "Fragment A: PAPER. Fragment B: a thing you see in the night sky. Fragment C: the note says the moon is only a projection. Join the two words that form the phrase.",
        "answer": "PAPERMOON",
        "hint": "The phrase is a familiar expression for something that looks real but is not."
    },
    {
        "id": 4, "name": "The Forbidden Door", "subtitle": "The timestamp",
        "story": "A keypad is wired to a frozen clock. The door opens only for the time the signal first appeared.",
        "clue": "Every recovered log begins at 03:17. Enter the four digits, without punctuation.",
        "answer": "0317",
        "hint": "Use the hour first, then the minutes. Keep the leading zero."
    },
    {
        "id": 5, "name": "The Final Secret", "subtitle": "The truth behind the signal",
        "story": "The final screen asks one question: what has this place been trying to tell you?",
        "clue": "Revisit the message from the entrance and the archive. Complete the thought: “Nothing is ____ it seems.” Enter the missing words without spaces.",
        "answer": "ASIT",
        "hint": "The complete sentence is “Nothing is as it seems.” Enter only the missing words."
    },
]

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_progress (
                player_id TEXT PRIMARY KEY,
                completed TEXT NOT NULL DEFAULT '',
                hints_used INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def valid_player_id(value):
    return isinstance(value, str) and 8 <= len(value) <= 80 and all(c.isalnum() or c in "-_" for c in value)

def get_progress(player_id):
    if not valid_player_id(player_id):
        return {"completed": [], "hints_used": 0}
    with connect() as conn:
        row = conn.execute("SELECT completed, hints_used FROM player_progress WHERE player_id = ?", (player_id,)).fetchone()
        if row is None:
            conn.execute("INSERT OR IGNORE INTO player_progress (player_id) VALUES (?)", (player_id,))
            return {"completed": [], "hints_used": 0}
    completed = [int(x) for x in row["completed"].split(",") if x.isdigit()]
    return {"completed": completed, "hints_used": row["hints_used"]}

def save_progress(player_id, completed=None, add_hint=False):
    with connect() as conn:
        row = conn.execute("SELECT completed, hints_used FROM player_progress WHERE player_id = ?", (player_id,)).fetchone()
        current = set(int(x) for x in row["completed"].split(",") if x.isdigit()) if row else set()
        hints = row["hints_used"] if row else 0
        if completed is not None:
            current = set(completed)
        if add_hint:
            hints += 1
        joined = ",".join(str(x) for x in sorted(current))
        conn.execute("""
            INSERT INTO player_progress (player_id, completed, hints_used, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(player_id) DO UPDATE SET
                completed=excluded.completed, hints_used=excluded.hints_used, updated_at=CURRENT_TIMESTAMP
        """, (player_id, joined, hints))

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/privacy")
def privacy():
    return render_template("legal.html", page_title="Privacy Policy", page_key="privacy")

@app.get("/terms")
def terms():
    return render_template("legal.html", page_title="Terms and Conditions", page_key="terms")

@app.get("/cookies")
def cookies():
    return render_template("legal.html", page_title="Cookie and Storage Policy", page_key="cookies")

@app.get("/third-party")
def third_party():
    return render_template("legal.html", page_title="Third-Party Content", page_key="third-party")

@app.get("/api/status")
def status():
    player_id = request.args.get("player_id", "")
    if not valid_player_id(player_id):
        return jsonify({"error": "A valid player ID is required."}), 400
    progress = get_progress(player_id)
    public_rooms = [{k: v for k, v in room.items() if k not in ("answer", "hint")} for room in ROOMS]
    return jsonify({"rooms": public_rooms, "progress": progress})

@app.post("/api/solve")
def solve():
    data = request.get_json(silent=True) or {}
    player_id, room_id, answer = data.get("player_id", ""), data.get("room_id"), data.get("answer", "")
    if not valid_player_id(player_id):
        return jsonify({"ok": False, "message": "Your player session looks invalid. Refresh the page to start a new session."}), 400
    try:
        room_id = int(room_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "That room does not exist."}), 400
    room = next((r for r in ROOMS if r["id"] == room_id), None)
    if room is None:
        return jsonify({"ok": False, "message": "That room does not exist."}), 404

    progress = get_progress(player_id)
    completed = set(progress["completed"])
    if room_id > 1 and (room_id - 1) not in completed:
        return jsonify({"ok": False, "message": "That room is still locked. Solve the previous room first."}), 403
    normalized = "".join(ch for ch in str(answer).upper() if ch.isalnum())
    expected = "".join(ch for ch in room["answer"].upper() if ch.isalnum())
    if normalized != expected:
        return jsonify({"ok": False, "message": "Not quite. Check the clue and try again."}), 200
    completed.add(room_id)
    save_progress(player_id, completed=completed)
    return jsonify({
        "ok": True,
        "message": "Signal accepted. Room unlocked.",
        "completed": sorted(completed),
        "game_complete": len(completed) == len(ROOMS)
    })

@app.post("/api/hint")
def hint():
    data = request.get_json(silent=True) or {}
    player_id, room_id = data.get("player_id", ""), data.get("room_id")
    if not valid_player_id(player_id):
        return jsonify({"error": "A valid player ID is required."}), 400
    try:
        room_id = int(room_id)
    except (TypeError, ValueError):
        return jsonify({"error": "That room does not exist."}), 400
    room = next((r for r in ROOMS if r["id"] == room_id), None)
    if room is None:
        return jsonify({"error": "That room does not exist."}), 404
    progress = get_progress(player_id)
    if room_id > 1 and (room_id - 1) not in progress["completed"]:
        return jsonify({"error": "This room is still locked."}), 403
    save_progress(player_id, add_hint=True)
    return jsonify({"hint": room["hint"], "hints_used": get_progress(player_id)["hints_used"]})

@app.post("/api/reset")
def reset():
    data = request.get_json(silent=True) or {}
    player_id = data.get("player_id", "")
    if not valid_player_id(player_id):
        return jsonify({"error": "A valid player ID is required."}), 400
    with connect() as conn:
        conn.execute("UPDATE player_progress SET completed = '', hints_used = 0, updated_at = CURRENT_TIMESTAMP WHERE player_id = ?", (player_id,))
    return jsonify({"ok": True})

init_db()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
