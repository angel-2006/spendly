# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Spendly — a personal expense tracker (amounts in ₹) built with Flask + SQLite as a step-by-step learning project. Most backend features are intentionally unimplemented and labelled with a step number ("coming in Step N"); only the UI pages exist so far.

## Commands

- Setup: `python -m venv venv`, activate (`venv\Scripts\Activate.ps1` on Windows), `pip install -r requirements.txt`
- Run: `python app.py` (debug mode, http://localhost:5001)
- Tests: `pytest` (pytest and pytest-flask are in requirements; no tests exist yet). Single test: `pytest path/to/test_file.py::test_name`
- No linter or build step is configured.

## Architecture

- `app.py` — single Flask app with all routes. Working routes just `render_template` (`/`, `/register`, `/login`, `/terms`, `/privacy`). Placeholder routes return stub strings and mark which step implements them (logout, profile, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`). Replace the stubs in place rather than adding new routes.
- `database/db.py` — currently only a comment spec: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (dev sample data).
- `templates/` — all pages extend `base.html` (navbar, footer, blocks: `title`, `head`, `content`, `scripts`). Use `url_for(...)` for links.
- `static/css/style.css` — single stylesheet (DM Serif Display / DM Sans fonts); `static/js/main.js` — page scripts (e.g. the YouTube modal on the landing page).

## Notes

- `file.txt` / `file.md` are scratch notes (terminal transcripts, commit commands), not project docs.
- `venv/` lives inside the project directory; it is gitignored.
- Commit messages follow the style `landing: <what changed>`.
