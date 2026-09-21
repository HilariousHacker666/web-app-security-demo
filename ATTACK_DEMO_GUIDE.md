# Live Demo Guide — Attacking Method Walkthrough

Use this as a script to run the demo live in front of your team. It's
one single-page application (`index.html`) with a **Vulnerable /
Patched** switch in the top right — flip it to move between the two
versions of the same login, search, and framing behavior, without
navigating to a different page.

All five attacks run entirely in the browser against mock, in-memory
data — nothing here touches a real server or a real database, so it's
safe to demonstrate on a shared screen or projector.

---

## Demo 1: SQL Injection — logging in without a password

**Make sure the toggle is set to "Vulnerable."** Go to the Login section.

1. Point out the mock account shown on the page: `demo_admin` /
   `DemoPass!2024`. Type it in correctly first and click **Login** to
   show the normal, expected behavior — it succeeds.
2. Now show the live query box above the form — as you type in either
   field, the exact query text updates. Explain: *this is built by
   gluing the text you type directly into a SQL command, which is
   exactly what the original vulnerable code does.*
3. Clear both fields. In **Username**, type:
   ```
   demo_admin' OR '1'='1
   ```
   Leave **Password** as anything, e.g. `wrongpassword`. Click **Login**.
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

**The point to land:** the attacker never needed to know a real
password. Because user input was *trusted and concatenated* instead of
treated as pure data, they could rewrite the logic of the query itself.

**Then flip the toggle to "Patched"** and repeat the exact same input.
Show that it returns "Invalid credentials" — the input is compared as
a plain value, never interpreted as part of a command, so the
injection has no effect. Notice the query preview box also changes to
reflect that no string is being built anymore.

---

## Demo 2: Cross-Site Scripting (XSS) — running a script through a search box

**Toggle still set to "Vulnerable."** Go to the Search section.

1. Type a normal search term first (e.g. `laptop`) and click
   **Search** to show the expected behavior.
2. Now type this into the search box:
   ```
   <img src=x onerror="alert('XSS executed!')">
   ```
3. Click **Search**. **Result:** a JavaScript alert box pops up. Explain:
   *this "search term" wasn't treated as text — it was inserted directly
   as HTML, so the browser parsed it as a real image tag, tried to load
   a broken image, and ran the attacker's script when it failed.*
4. Tie it to real-world impact: in a real app, this script could steal
   session cookies, log keystrokes, or silently take actions as the
   logged-in user — anyone who views a page with this payload in it
   (e.g. a malicious link, a comment, a shared search) is affected, not
   just the person who typed it.

**Then flip the toggle to "Patched"** and paste the same payload into
search. **Result:** the tag is displayed as plain visible text, not
executed — no alert box. Explain: the output is now inserted as text
content, not parsed as HTML, so markup characters have no special
meaning.

---

## Demo 3: Clickjacking — hiding a real page inside a fake one

**Scroll down to the "Clickjacking self-test" section** at the bottom
of the app. It embeds two copies of the same app inside iframes, one
locked to each mode.

1. Point out the two panels: the vulnerable copy loads normally inside
   its iframe on the left. The patched copy on the right immediately
   detects it's being framed and blocks its own content, showing a
   "Blocked" message instead.
2. Explain the real-world attack: an attacker builds a lookalike page,
   loads the real (vulnerable) site inside an invisible iframe, and
   positions a fake button exactly over a real button underneath —
   e.g. a "Claim your prize" button sitting on top of the real site's
   "Confirm transfer" or "Delete account" button. The victim thinks
   they're clicking the attacker's page; they're actually clicking the
   real site through the invisible layer.
3. Land the point: the vulnerable page has no instruction telling the
   browser "don't let anyone put me in a frame." The patched page does
   (a framing check equivalent to the `X-Frame-Options` /
   `Content-Security-Policy` headers used in the real backend), so it
   refuses to render when embedded, breaking the attack.

---

## Demo 4: CSRF — changing an account setting without the user's knowledge

**Toggle set to "Vulnerable."** Scroll to the "Change email" section.

1. Show the legitimate flow first: type a new email and click **Update
   email**. It works normally — this is the real, expected use of the
   form.
2. Now click **"Simulate a forged request from another site."** This
   stands in for a hidden form on an attacker's page that
   auto-submits to this same action the moment a logged-in victim
   visits it.
3. **Result:** the email silently changes to `attacker@evil-site.example`
   — the real user never filled out anything. Point out the request
   preview box: no `csrf_token` field is present or checked at all.

**Then flip the toggle to "Patched"** and repeat the forged-request
click. **Result:** it's rejected — the preview box now shows a
`csrf_token` value that only this page's own form legitimately carries,
so the attacker's forged request has no way to produce a valid one.

---

## Demo 5: Insecure session cookie — why cookie flags matter

**Toggle set to "Vulnerable."** Scroll to the "Session cookie" section.

1. Click **"Simulate login (issue session cookie)."**
2. Click **"Read cookie via JavaScript."** **Result:** the actual
   cookie value is printed on the page. Explain: *this is standing in
   for what an XSS payload — like the one from Demo 2 — could do: read
   the session cookie directly and send it to an attacker, letting
   them hijack the session even without the SQLi or login bugs.*

**Then flip the toggle to "Patched"** and repeat both clicks.
**Result:** nothing readable comes back. Explain: a real `HttpOnly`
cookie is never exposed to JavaScript at all — even a successful XSS
injection couldn't read it. Combined with `Secure` (HTTPS only) and
`SameSite` (limits cross-site sending), this closes off a whole class
of session-hijacking techniques even if another bug slips through
elsewhere.

---

## Closing summary for the room

- All five attacks worked because user input, requests, or client state were trusted by default
  instead of being treated as untrusted data.
- All five fixes follow the same underlying pattern: separate data
  from code/structure (SQL, HTML, or framing rules), and make the safe
  behavior the default rather than something developers have to
  remember to add every time.
- Point the team to `SECURITY_REPORT.md` in the repo for the full
  written explanation of each vulnerability and fix, including the
  original server-side code.
