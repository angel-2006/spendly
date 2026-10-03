# Spec: Login and Logout

## Overview
Turn the static `/login` page into a working sign-in flow and replace the `/logout` stub. A visitor submits email and password; the server looks up the user, verifies the password against the stored werkzeug hash, stores the user id in the Flask session, and redirects. Logout clears the session. This is the first use of sessions in Spendly and unblocks every logged-in feature (profile in Step 4, expenses in Steps 7–9). The navbar also becomes session-aware.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, seeded demo user `demo@spendly.com` / `demo123`).
- Step 2 — Registration (users with hashed passwords; registration redirects to `/login`).

## Routes
- `GET /login` — render the sign-in form; if already logged in, redirect to `/profile` — public (already exists; extended)
- `POST /login` — validate input, verify credentials, set `session["user_id"]`, redirect to `/profile` on success or re-render the form with an error on failure — public
- `GET /logout` — clear the session and redirect to `/` — logged-in (harmless if not logged in; still redirects to `/`)

Implement by extending the existing `login()` view to accept `GET` and `POST`, and replacing the `logout()` stub in `app.py` in place. Do not add new routes.

## Database changes
No database changes. Login only reads `id`, `name`, `email`, `password_hash` from the existing `users` table.

## Templates
- **Create:** none
- **Modify:** `templates/login.html`
  - Change `action="/login"` to `action="{{ url_for('login') }}"`
  - Preserve submitted `email` on error (`value="{{ email or '' }}"`); never re-fill the password
  - Existing `{% if error %}` block is reused for error display
- **Modify:** `templates/base.html`
  - Navbar: when `session.user_id` is set, show a "Sign out" link (`url_for('logout')`) and a link to `url_for('profile')` instead of "Sign in" / "Get started"; otherwise keep the current links

## Files to change
- `app.py` — import `session` and `check_password_hash`; set `app.secret_key`; implement `POST /login`; implement `/logout`
- `templates/login.html` — see above
- `templates/base.html` — session-aware navbar

## Files to create
- `tests/test_login_logout.py` — pytest tests for login and logout (uses a temporary database; must not touch `expense_tracker.db`)

## New dependencies
No new dependencies.

## Validation and behaviour rules
- `email`: trimmed and lower-cased before lookup (matches how registration stores it)
- `password`: taken as-is (no trimming)
- Empty email or password: re-render `login.html` with "Please enter your email and password."
- Unknown email OR wrong password: the same generic message "Invalid email or password." (do not reveal which was wrong)
- On any error: HTTP 200, re-render `login.html` with `error` and the submitted `email`
- On success: `session.clear()` first (avoid session fixation), then `session["user_id"] = user["id"]`, then redirect (302) to `url_for("profile")`
- Logout: `session.clear()`, redirect (302) to `url_for("landing")`
- `app.secret_key` is read from the `SECRET_KEY` environment variable, falling back to a dev-only default so the app still starts locally

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never format values into SQL
- Passwords hashed with werkzeug; verify with `werkzeug.security.check_password_hash`; never store or log the plain password
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for(...)` for links and redirects
- Open the connection with `get_db()` and always close it (`try/finally`)
- Replace the existing `login()` and `logout()` views in place; keep other routes untouched
- Store only the user id in the session, nothing else sensitive
- Keep the demo seed user (`demo@spendly.com`) working

## Definition of done
- [ ] `GET /login` renders the form with the form posting via `url_for('login')`
- [ ] Logging in as `demo@spendly.com` / `demo123` redirects (302) to `/profile` and the session holds the user's id
- [ ] A user created via `/register` can log in with the same credentials (email in any letter case)
- [ ] Wrong password and unknown email both show "Invalid email or password." with HTTP 200 and no session set
- [ ] Empty email or password shows a clear error and sets no session
- [ ] After an error, the email stays filled in; the password field is empty
- [ ] Visiting `/login` while logged in redirects to `/profile`
- [ ] `/logout` clears the session and redirects to `/`; afterwards the navbar shows "Sign in" / "Get started" again
- [ ] While logged in, the navbar shows "Sign out" and a profile link instead of "Sign in" / "Get started"
- [ ] `pytest tests/test_login_logout.py` passes
- [ ] App starts without errors and registration still works
