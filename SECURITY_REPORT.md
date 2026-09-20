# Web Application Security Report
### Demonstrated Vulnerabilities and Their Fixes

This report accompanies a small demo application built in two
versions — one deliberately vulnerable, one patched — so the team can
see exactly what each issue looks like in real code and how it was
fixed. Each section below covers one vulnerability: what it is, where
it lived in our demo app, how an attacker could exploit it, what we
changed, and how to avoid it in future work.

---

## 1. SQL Injection

**What it is**
SQL Injection happens when user-supplied input is inserted directly
into a database query as raw text, instead of being treated as data.
This lets an attacker change the meaning of the query itself — reading
data they shouldn't see, bypassing logins, or in the worst case
modifying or deleting data.

**Where it was**
In the login form's server-side code, the username and password
entered by the user were glued directly into a SQL string using
ordinary string concatenation before being sent to the database.

**How it could be exploited**
An attacker doesn't need the real password. Typing something like
`' OR '1'='1` into the username field changes the underlying query so
that it always evaluates to true, logging the attacker in as the first
user in the table — often an administrator — without knowing any
credentials.

**What we changed**
The query was rewritten to use a *parameterized query* (also called a
prepared statement): the SQL text and the user's input are sent to the
database separately, with placeholders (`?`) standing in for the
values. The database driver guarantees that whatever the user typed is
only ever treated as data, never as part of the query's logic.

**How to prevent it going forward**
- Never build a SQL query by concatenating or formatting strings with
  user input, even for "internal" or "trusted" fields.
- Always use parameterized queries / prepared statements, or an
  ORM (e.g., SQLAlchemy, Django ORM) that does this for you.
- Apply this rule to every place user input reaches a database:
  search boxes, filters, login forms, admin tools — not just obvious
  ones.

---

## 2. Cross-Site Scripting (XSS)

**What it is**
XSS happens when user-supplied input is inserted into a page's HTML
without being properly encoded, allowing an attacker to inject their
own script into the page. That script then runs in the browser of
anyone who views the page, with the same access as the real site —
meaning it can steal session cookies, log keystrokes, or perform
actions as the victim.

**Where it was**
The search page took the user's search term from the URL and inserted
it straight into the HTML response using simple string formatting,
with no encoding of special characters.

**How it could be exploited**
Instead of a normal search term, an attacker crafts a link containing
a snippet of JavaScript as the search value and sends it to a victim
(e.g., in an email or chat message). When the victim clicks the link,
the injected script runs in their browser under our site's identity.

**What we changed**
The page is now rendered through the template engine's normal
templating mechanism instead of manual string formatting. The template
engine automatically encodes special HTML characters (such as `<`,
`>`, `"`, `'`) in any value it renders, so injected script tags are
displayed as harmless visible text instead of being executed.

**How to prevent it going forward**
- Always render dynamic content through your templating engine's
  standard output mechanism, and never disable its automatic escaping
  (Flask/Jinja2, Django templates, and React/JSX all escape by
  default — the danger is turning that protection off).
- Never build HTML by hand-concatenating or formatting strings with
  user input.
- Add a Content-Security-Policy header as a second layer of defense,
  so that even if an XSS bug slips through, injected scripts are
  restricted in what they can do.

---

## 3. Clickjacking

**What it is**
Clickjacking tricks a user into clicking something on our site without
realizing it, by loading our page inside an invisible or disguised
`<iframe>` on an attacker's site. The user thinks they're clicking a
button on the attacker's page, but they're actually clicking a
button on our real site underneath it (e.g., "Confirm transfer" or
"Change email").

**Where it was**
The app didn't send any header telling the browser whether it's
allowed to be displayed inside a frame on another website, so by
default any site could embed our pages.

**How it could be exploited**
An attacker builds a page with our site loaded in a transparent
iframe, positions a fake button over a real button of ours, and gets
the victim to click. The click lands on our page, not the attacker's.

**What we changed**
We added the `X-Frame-Options: DENY` header (understood by all major
browsers) and a matching `Content-Security-Policy: frame-ancestors
'none'` header (the modern replacement) to every response. Together
they tell the browser our pages must never be shown inside a frame on
any site — including our own, unless that's explicitly required.

**How to prevent it going forward**
- Set both headers by default on every page, at the framework or
  reverse-proxy level, rather than per-route.
- If a specific page genuinely needs to be embedded (e.g., a widget
  meant for partner sites), scope the exception narrowly to that page
  and list the allowed origins explicitly rather than allowing
  everyone.

---

## 4. Cross-Site Request Forgery (CSRF)

**What it is**
CSRF tricks a logged-in user's browser into submitting a request to
our site that they never intended to make. Because the browser
automatically attaches the user's session cookie to requests, the
request looks legitimate to our server even though the user didn't
knowingly initiate it.

**Where it was**
The login form (and, in a fuller app, any form that changes state —
updating a password, transferring funds, changing an email) had no
mechanism to verify that the request actually came from a page we
served, rather than from an attacker's page auto-submitting a form on
the user's behalf.

**How it could be exploited**
An attacker hosts a page with a hidden form that targets our form's
exact URL and auto-submits it when a victim visits. If the victim is
already logged in, their browser sends the request along with their
valid session cookie, and our server has no way to tell it wasn't
intentional.

**What we changed**
We added CSRF protection that generates a unique, secret token per
user session and embeds it as a hidden field in every form. The server
checks that this token is present and correct before processing the
request. An attacker's page has no way to know or guess this token, so
their forged request is rejected.

**How to prevent it going forward**
- Use your framework's built-in CSRF protection (Flask-WTF, Django's
  CSRF middleware, Rails' `protect_from_forgery`, etc.) rather than
  writing your own.
- Apply it to every request that changes state (POST/PUT/DELETE), not
  just login forms.
- Combine with the `SameSite` cookie attribute below for defense in
  depth.

---

## 5. Insecure Cookie Configuration

**What it is**
Session cookies that aren't properly locked down can be read by
malicious JavaScript, sent over unencrypted connections, or attached
to requests originating from other sites — each of which makes other
attacks (XSS, network interception, CSRF) more damaging.

**Where it was**
The app's session cookie was configured without any of the three
standard protective flags.

**How it could be exploited**
- Without `HttpOnly`, a successful XSS attack (see Vulnerability 2)
  can read the session cookie directly with JavaScript and send it to
  the attacker, letting them hijack the session even after the XSS bug
  itself is patched elsewhere.
- Without `Secure`, the cookie can be sent over plain HTTP, where it's
  visible to anyone who can intercept network traffic (e.g., on public
  Wi-Fi).
- Without `SameSite`, the cookie is attached to requests triggered
  from other sites, widening the attack surface for CSRF.

**What we changed**
We set all three flags on the session cookie:
- `HttpOnly` — JavaScript can no longer read the cookie.
- `Secure` — the cookie is only ever sent over HTTPS.
- `SameSite=Lax` — the cookie is withheld from most cross-site
  requests, while still working normally for regular navigation.

**How to prevent it going forward**
- Set these three flags as a default for every cookie your
  application issues, not just the session cookie.
- Enforce HTTPS everywhere in production so the `Secure` flag doesn't
  break functionality.
- Treat cookie configuration as part of your standard project
  checklist for any new app.

---

## Summary Table

| # | Vulnerability | Root Cause | Fix Applied |
|---|---|---|---|
| 1 | SQL Injection | User input concatenated into SQL string | Parameterized queries |
| 2 | XSS | User input inserted into HTML without encoding | Template auto-escaping |
| 3 | Clickjacking | No frame-restriction headers | `X-Frame-Options` + CSP `frame-ancestors` |
| 4 | CSRF | No verification that requests came from our own forms | Per-session CSRF tokens |
| 5 | Insecure cookies | Missing `HttpOnly`/`Secure`/`SameSite` flags | All three flags enabled |

## Suggested next steps for the team

- Walk through the `vulnerable/` and `patched/` code side by side in a
  team session, using this report as the script.
- Add these five checks to code review checklists and/or CI
  (e.g., a linter or SAST tool that flags raw SQL string building or
  disabled template escaping).
- Consider extending this demo with a few more common issues over
  time — broken access control and insecure file uploads are natural
  next additions.
