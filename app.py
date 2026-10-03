import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret-change-me")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    local, _, domain = email.partition("@")
    error = None
    if not name or len(name) > 100:
        error = "Please enter your name (up to 100 characters)."
    elif not local or not domain or "@" in domain or len(email) > 254:
        error = "Please enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."

    if error is None:
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "An account with that email already exists."
        finally:
            conn.close()

    return render_template("register.html", error=error, name=name, email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        error = "Please enter your email and password."
    else:
        conn = get_db()
        try:
            user = conn.execute(
                "SELECT id, password_hash FROM users WHERE email = ?", (email,)
            ).fetchone()
        finally:
            conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Invalid email or password."
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))

    return render_template("login.html", error=error, email=email)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Hardcoded demo data — replaced by real queries in Step 5.
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "January 2026",
    }
    user["initials"] = "".join(w[0] for w in user["name"].split()[:2]).upper()

    transactions = [
        {"date": "25 Sep 2026", "description": "Groceries", "category": "Food", "amount": 780},
        {"date": "20 Sep 2026", "description": "Stationery", "category": "Other", "amount": 200},
        {"date": "16 Sep 2026", "description": "Headphones", "category": "Shopping", "amount": 2499},
        {"date": "12 Sep 2026", "description": "Movie tickets", "category": "Entertainment", "amount": 350},
        {"date": "08 Sep 2026", "description": "Pharmacy", "category": "Health", "amount": 650},
        {"date": "05 Sep 2026", "description": "Electricity bill", "category": "Bills", "amount": 1800},
        {"date": "03 Sep 2026", "description": "Auto rickshaw fare", "category": "Transport", "amount": 120},
        {"date": "01 Sep 2026", "description": "Lunch at cafe", "category": "Food", "amount": 450},
    ]

    totals = {}
    for t in transactions:
        totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]
    total_spent = sum(totals.values())
    categories = [
        {"name": name, "total": total, "percent": round(total / total_spent * 100)}
        for name, total in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    ]

    stats = {
        "total_spent": total_spent,
        "transaction_count": len(transactions),
        "top_category": categories[0]["name"],
    }

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
