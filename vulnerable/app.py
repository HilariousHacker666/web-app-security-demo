"""
VULNERABLE DEMO APP - FOR INTERNAL SECURITY TRAINING ONLY
Do not deploy this app anywhere reachable from the internet.
This app intentionally contains: SQL Injection, XSS, Clickjacking,
CSRF, and insecure cookie configuration.
See patched/app.py for the fixed version, and SECURITY_REPORT.md
for a plain-English explanation of each issue.
"""

from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecret"

# VULNERABILITY 5: Insecure cookie configuration
# The session cookie can be read by JavaScript (no HttpOnly), sent over
# plain HTTP (no Secure), and sent along with cross-site requests
# (no SameSite). This makes session hijacking and CSRF easier.
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE=None,
)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db():
    return sqlite3.connect(DB_PATH)


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


LOGIN_PAGE = """
<html><body>
<h2>Login</h2>
<form method="POST" action="/login">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <input type="submit" value="Login">
</form>
</body></html>
"""
# VULNERABILITY 4: No CSRF token on this state-changing form.
# Any external site can auto-submit a form to this exact URL on a
# logged-in user's behalf.


@app.route("/")
def index():
    return LOGIN_PAGE


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # VULNERABILITY 1: SQL Injection.
    # User input is concatenated directly into the SQL string instead
    # of being passed as a parameter. An attacker can submit something
    # like:  ' OR '1'='1  as the username to bypass the password check,
    # or extract data from other tables entirely.
    conn = get_db()
    query = (
        "SELECT * FROM users WHERE username = '"
        + username
        + "' AND password = '"
        + password
        + "'"
    )
    cur = conn.execute(query)
    user = cur.fetchone()
    conn.close()

    if user:
        return f"Welcome, {username}!"
    return "Invalid credentials"


SEARCH_PAGE = """
<html><body>
<h2>Search</h2>
<form method="GET" action="/search">
  <input name="q">
  <input type="submit" value="Search">
</form>
<div>Results for: {results}</div>
</body></html>
"""


@app.route("/search")
def search():
    q = request.args.get("q", "")
    # VULNERABILITY 2: Reflected Cross-Site Scripting (XSS).
    # The search term is inserted straight into the HTML response with
    # no encoding. A URL like /search?q=<script>alert(1)</script> will
    # run attacker-controlled JavaScript in the victim's browser.
    page = SEARCH_PAGE.format(results=q)
    return page


@app.route("/frame-test")
def frame_test():
    # VULNERABILITY 3: Clickjacking.
    # No X-Frame-Options or Content-Security-Policy header is set, so
    # this page can be loaded inside an <iframe> on any attacker site
    # and tricked into being clicked ("UI redressing").
    return "This page can be embedded in an iframe on any external site."


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
