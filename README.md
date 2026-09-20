# Web Application Security Training Demo

**Live demo:** https://hilarioushacker666.github.io/web-app-security-demo/

This repository has two things:

1. **`docs/`** — a single-page static application, safe to host
   publicly (no real backend or database — everything runs in the
   browser against mock data). It has a Vulnerable/Patched toggle that
   switches the login, search, and framing behavior between the
   insecure and fixed versions, plus an embedded clickjacking
   self-test. This is what's deployed via GitHub Pages above, and
   what you'd use for a live, click-through demo with your team.
2. **`vulnerable/`** and **`patched/`** — the real two versions of the
   same tiny Flask app the static demo is modeled on, each with
   `VULNERABILITY:` / `FIX:` comments in the code, for anyone who wants
   to see (or run locally) the actual server-side logic.

Read **SECURITY_REPORT.md** for a plain-English write-up of every
vulnerability and its fix, and **ATTACK_DEMO_GUIDE.md** for a
step-by-step script to run the live demo in front of your team.

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
