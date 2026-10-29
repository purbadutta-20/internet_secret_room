 The Internet's Secret Room

A responsive, analog-horror inspired browser escape-room game built with Flask, SQLite, HTML, CSS, and vanilla JavaScript.

 Features

- Five original puzzle rooms with sequential unlocking
 -Server-side answer validation
 -SQLite progress storage per browser player ID
- Hints and hint-use counter
- Reset progress button
- Responsive CRT / analog-horror inspired interface
- No external APIs required for gameplay

 Requirements

- Python 3.10 or newer
- VS Code
- Python extension for VS Code

 Run locally (Windows PowerShell)

powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py


 Run locally (macOS/Linux)

bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py

 Puzzle answers (spoilers)

1. LOOKCLOSER
2. HELLO
3. PAPERMOON
4. 0317
5. ASIT

The puzzles are fictional. This starter project is designed for local learning and is not hardened for public deployment. Before deploying, use a strong `SECRET_KEY`, add rate limiting, consider authentication, and review database/player identity handling.

