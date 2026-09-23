# Live Demo Guide — Attacking Method Walkthrough

Use this as a script to run the demo live in front of your team. It's
"Paw & Pour," a fictional pet café's staff console, built as two
separate pages:

- `vulnerable.html` — all five flaws live
- `patched.html` — same UI and data, each flaw fixed
- `clickjack-test.html` — both loaded in an iframe side by side

All five attacks run entirely in the browser against mock, in-memory
data — nothing here touches a real server or a real database, so it's
safe to demonstrate on a shared screen or projector.

---

## Demo 1: SQL Injection — logging in without a password

**Open `vulnerable.html`**, scroll to **Staff login**.

1. Point out the mock account shown on the page: `staff_manager` /
   `Marigold@2024`. Type it in correctly first and click **Log in** to
   show the normal, expected behavior — it succeeds.
2. Now show the live query box above the form — as you type in either
   field, the exact query text updates. Explain: *this is built by
   gluing the text you type directly into a SQL command, which is
   exactly what the original vulnerable backend code does.*
3. Clear both fields. In **Username**, type:
   ```
   staff_manager' OR '1'='1
   ```
   Leave **Password** as anything, e.g. `wrongpassword`. Click **Log in**.
4. **Result:** login succeeds anyway, and the result box shows the
   actual query that got evaluated. Walk through it out loud: the `'`
   closes the string early, `OR '1'='1'` adds a condition that is
   always true, so the password check becomes irrelevant.
5. Optional second payload, for an account name the attacker doesn't
   even know — type in **Username**:
   ```
   ' OR '1'='1' --
   ```
   Explain: the `--` is a SQL comment marker — everything after it
   (including the real password check) is ignored entirely.

**The point to land:** the attacker never needed a real password.
Because input was *trusted and concatenated* instead of treated as
pure data, they could rewrite the logic of the query itself.

**Then open `patched.html`** and repeat the exact same input. It
returns "Invalid credentials" — the input is compared as a plain
value, never interpreted as part of a command.

---

## Demo 2: Cross-Site Scripting (XSS) — running a script through search

**On `vulnerable.html`**, scroll to **Find a pet or customer**.

1. Search for a normal term first (e.g. `Biscuit`) to show expected
   behavior.
2. Now search for:
   ```
   <img src=x onerror="alert('XSS executed!')">
   ```
3. **Result:** a JavaScript alert box pops up. Explain: *this "search
   term" wasn't treated as text — it was inserted directly as HTML, so
   the browser parsed it as a real image tag, tried to load a broken
   image, and ran the attacker's script when it failed.*
4. Tie it to real-world impact: in a real app, this script could steal
   the staff session cookie (see Demo 5), log keystrokes, or silently
   take actions as the logged-in staff member — anyone who views a
   page with this payload is affected, not just the person who typed it.

**On `patched.html`**, paste the same payload into search. The tag is
displayed as plain visible text — no alert box.

---

## Demo 3: Clickjacking — hiding the real console inside a fake page

**Open `clickjack-test.html`.**

1. Point out the two panels: the vulnerable console loads normally
   inside its iframe on the left. The patched console on the right
   immediately detects it's being framed and blocks its own content.
2. Explain the real-world attack: an attacker builds a lookalike page,
   loads the real (vulnerable) console inside an invisible iframe, and
   positions a fake button exactly over a real one underneath — e.g. a
   "Claim your free coffee" button sitting on top of the console's
   real "Update email" or "Log in" button. The victim thinks they're
   clicking the attacker's page; they're actually clicking the real
   console through the invisible layer.
3. Land the point: the vulnerable console has no instruction telling
   the browser "don't let anyone put me in a frame." The patched
   console does, so it refuses to render when embedded.

---

## Demo 4: CSRF — changing a setting without the staff member's knowledge

**On `vulnerable.html`**, scroll to **Notification settings**.

1. Show the legitimate flow first: type a new email and click
   **Update email**. It works normally — this is the real, expected
   use of the form.
2. Now click **"Simulate a forged request from another site."** This
   stands in for a hidden form on an attacker's page that
   auto-submits to this same action the moment a logged-in staff
   member visits it.
3. **Result:** the reminder email silently changes to
   `attacker@evil-site.example` — nobody filled out anything. Point
   out the request preview box: no `csrf_token` field is present or
   checked at all.

**On `patched.html`**, repeat the forged-request click. It's
rejected — the preview box shows a `csrf_token` value that only this
page's own form legitimately carries, so the forged request has no way
to produce a valid one.

---

## Demo 5: Insecure session cookie — why cookie flags matter

**On `vulnerable.html`**, scroll to **Session cookie**.

1. Click **"Simulate login (issue session cookie)."**
2. Click **"Read cookie via JavaScript."** **Result:** the actual
   cookie value is printed. Explain: *this is standing in for what the
   XSS payload from Demo 2 could do — read the session cookie directly
   and send it to an attacker, hijacking the session even without the
   SQLi or login bugs.*

**On `patched.html`**, repeat both clicks. Nothing readable comes
back. Explain: a real `HttpOnly` cookie is never exposed to JavaScript
at all — even a successful XSS injection couldn't read it. Combined
with `Secure` (HTTPS only) and `SameSite` (limits cross-site sending),
this closes off a whole class of session-hijacking techniques even if
another bug slips through elsewhere.

---

## Closing summary for the room

- All five attacks worked because user input, requests, or client
  state were trusted by default instead of being treated as untrusted.
- All five fixes follow the same underlying pattern: separate data
  from code/structure (SQL, HTML, requests, framing rules), and make
  the safe behavior the default rather than something developers have
  to remember to add every time.
- Point the team to `SECURITY_REPORT.md` in the repo for the full
  written explanation of each vulnerability and fix, including the
  original server-side code.
