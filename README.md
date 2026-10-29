# The Internet's Secret Room

A responsive, analog-horror inspired browser escape-room game built with Flask, SQLite, HTML, CSS, and vanilla JavaScript.

## Features

- Five original puzzle rooms with sequential unlocking
- Server-side answer validation
- SQLite progress storage per browser player ID
- Hints and hint-use counter
- Reset progress button
- Responsive CRT / analog-horror inspired interface
- No external APIs required for gameplay

## Requirements

- Python 3.10 or newer
- VS Code
- Python extension for VS Code

## Run locally (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, you can run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in your browser.

## Run locally (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

## Puzzle answers (spoilers)

1. LOOKCLOSER
2. HELLO
3. PAPERMOON
4. 0317
5. ASIT

The puzzles are fictional. This starter project is designed for local learning and is not hardened for public deployment. Before deploying, use a strong `SECRET_KEY`, add rate limiting, consider authentication, and review database/player identity handling.

## Privacy, legal and accessibility notes

- Policy pages: `/privacy`, `/terms`, `/cookies`, and `/third-party`.
- The game stores a random player identifier in browser local storage and progress/hint counts in SQLite. The reset button clears progress but does not remove the browser identifier.
- System fonts are used to avoid a Google Fonts network request. The game currently has no bundled images or third-party embeds.
- Keyboard focus styles, reduced-motion handling, progress-bar semantics, and descriptive legal navigation are included. Perform manual keyboard and screen-reader testing before launch.
- The policy pages are templates, not legal advice or proof of compliance. Before public deployment, add the real operator identity/contact, actual hosting details, retention periods, and any applicable notices/consent flows. Review India's DPDP Act and notified Rules as applicable, plus other relevant laws for your deployment.
