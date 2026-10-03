# Spec: Registration

## Overview
Turn the static `/register` page into a working sign-up flow. A visitor submits name, email and password; the server validates the input, hashes the password with werkzeug, inserts a row into the existing `users` table, and redirects to `/login`. This is the first write path into the database built in Step 1 and unblocks login/logout (Step 3).

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, `init_db()`).

## Routes
- `GET /register` — render the registration form — public (already exists; unchanged)
- `POST /register` — validate input, create the user, redirect to `/login` on success or re-render the form with an error on failure — public

Implement by extending the existing `register()` view in `app.py` to accept `GET` and `POST`. Do not add a new route.

## Database changes
No database changes. The `users` table already has `name`, `email` (UNIQUE), `password_hash` and `created_at`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html`
  - Change `action="/register"` to `action="{{ url_for('register') }}"`
  - Preserve submitted `name` and `email` on error (`value="{{ name or '' }}"` / `value="{{ email or '' }}"`); never re-fill the password
  - Add `minlength="8"` to the password input
  - Existing `{% if error %}` block is reused for error display

## Files to change
- `app.py` — accept POST on `/register`, validation, insert, redirect
- `templates/register.html` — see above

## Files to create
- `tests/test_registration.py` — pytest tests for the registration flow (uses a temporary database; must not touch `expense_tracker.db`)

## New dependencies
No new dependencies.

## Validation rules
- `name`: required, trimmed, 1–100 characters
- `email`: required, trimmed, lower-cased, must contain `@` with text on both sides, max 254 characters
- `password`: required, minimum 8 characters
- Duplicate email: catch `sqlite3.IntegrityError` (do not pre-check with a SELECT only) and show "An account with that email already exists."
- On any error: HTTP 200, re-render `register.html` with `error` plus the submitted `name` and `email`

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never format values into SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`; never store or log the plain password
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for(...)` for links and redirects
- Open the connection with `get_db()` and always close it (`try/finally`)
- Replace the existing `register()` stub in place; keep the other routes untouched
- Do not log the user in on registration (sessions arrive in Step 3); redirect to `/login`
- Keep the demo seed user (`demo@spendly.com`) working

## Definition of done
- [ ] `GET /register` still renders the form
- [ ] Submitting valid name/email/password creates a row in `users` and redirects (302) to `/login`
- [ ] The stored `password_hash` is a werkzeug hash, not the plain password
- [ ] Registering the same email again (any letter case) shows "An account with that email already exists." and creates no second row
- [ ] Empty name, empty email, malformed email, or a password under 8 characters each re-render the form with a clear error and create no row
- [ ] After an error, name and email stay filled in; password is empty
- [ ] Email is stored trimmed and lower-cased
- [ ] The form posts via `url_for('register')`
- [ ] `pytest tests/test_registration.py` passes
- [ ] App starts without errors and the seeded demo user is unaffected
