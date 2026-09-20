# Web Application Security Training Demo

This repository contains two versions of the same tiny Flask app:

- `vulnerable/` — intentionally contains SQL Injection, XSS,
  Clickjacking, CSRF, and insecure cookie configuration, each marked
  with a `VULNERABILITY:` comment.
- `patched/` — the same app with each issue fixed, each marked with a
  matching `FIX:` comment.

Read **SECURITY_REPORT.md** for a plain-English write-up of every
vulnerability and its fix, intended for sharing with the wider team.

## Running locally (optional, for anyone who wants to try the app)

Each folder is a self-contained Flask app with its own
`requirements.txt`. Install the dependencies for the version you want
to run, then start it, and open the address it prints in a browser.

> The vulnerable version is for an isolated local/training environment
> only — never deploy it anywhere publicly reachable.

## Demo credentials

Both versions seed the same test database with:

- `admin` / `admin123`
- `alice` / `alicepass`
