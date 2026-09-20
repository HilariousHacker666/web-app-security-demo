"""
PATCHED DEMO APP
This is the fixed version of vulnerable/app.py. Every fix is labeled
with a "FIX:" comment that maps to the matching "VULNERABILITY:"
comment in the vulnerable version. See SECURITY_REPORT.md for the
full write-up.
"""

from flask import Flask, request, render_template
from flask_wtf import CSRFProtect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

# FIX for Vulnerability 5 (insecure cookies): the session cookie is now
# marked HttpOnly (JavaScript can't read it), Secure (only sent over
# HTTPS), and SameSite=Lax (not sent along with most cross-site requests).
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# FIX for Vulnerability 4 (CSRF): every POST form in this app now
# requires a valid, per-session CSRF token, checked automatically by
# this extension. A request forged from another site won't have a
# valid token and will be rejected.
csrf = CSRFProtect(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    )
    conn.execute("DELETE FROM users")
    conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    conn.execute("INSERT INTO users (username, password) VALUES ('alice', 'alicepass')")
    conn.commit()
    conn.close()


@app.after_request
def set_security_headers(response):
    # FIX for Vulnerability 3 (clickjacking): these headers tell the
    # browser this page must never be rendered inside a frame/iframe
    # on another site, which neutralizes clickjacking attacks.
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    return response


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # FIX for Vulnerability 1 (SQL injection): user input is passed as
    # bound parameters ("?") instead of being glued into the query
    # string. The database driver treats the input purely as data, so
    # it can never change the structure of the SQL statement.
    conn = get_db()
    cur = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    )
    user = cur.fetchone()
    conn.close()

    if user:
        # render_template() also auto-escapes "username" below, which
        # is part of the XSS fix too (see Vulnerability 2).
        return render_template("welcome.html", username=username)
    return "Invalid credentials", 401


@app.route("/search")
def search():
    q = request.args.get("q", "")
    # FIX for Vulnerability 2 (XSS): the template engine (Jinja2)
    # auto-escapes any value inserted with {{ }}, so characters like
    # < > " ' are converted to safe HTML entities before they reach
    # the page. Attacker-supplied HTML/JavaScript is displayed as
    # harmless text instead of being executed.
    return render_template("search.html", query=q)


@app.route("/frame-test")
def frame_test():
    return "This page is protected against framing by X-Frame-Options and CSP."


if __name__ == "__main__":
    init_db()
    app.run(debug=False, port=5001)
