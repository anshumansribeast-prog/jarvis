# ANSHUX subtasks — Codex only

**If Codex says there are no sites:** you opened the empty daily role-folder (`Documents\Codex\...\work`), not this git repo. Open **jarvis / ANSHUX**, or paste `CODEX_INBOX.md` + `anshux/codex/work/ASSIGNMENT.md`. Sites are URLs (semicolon.punah.pro, cosmos.punah.pro), not files in `work/`. If network is denied, the assignment already contains Cursor’s HTTP probe table — write the report from that. Do not stay idle.

STATUS of parent board: see `AGENT_TASK.md`.

Codex implements **open** rows. Do not edit Claude Code’s Main spec files.

| ID | State | Priority | File | Work |
| --- | --- | --- | --- | --- |
| SUB-2 | OPEN | **NOW** | `anshux/SITE_SECURITY_REPORT.md` | Full public-site inventory + **defensive** security review of **Semicolon** and **Cosmos** (see brief below). |
| SUB-1 | OPEN | later | `tests/test_system_controller.py` | `skipif` not Windows. Cover volume / mute / screenshot with mocks. Do this after SUB-2. |

When a row is done: set State to `DONE`, log as **Codex** in `AGENT_LOG.md`. Do not set `STATUS: TEST`.

---

## SUB-2 brief — Codex: check all sites and security (Semicolon + Cosmos)

Owner sites (Anshuman / ANSHUX). Read-only review of **our** deployments. No exploits, no PoCs, no payloads, no brute force, no fuzzing, no auth bypass attempts.

### Sites to inventory

| Product | URLs |
| --- | --- |
| Semicolon | `https://semicolon.punah.pro/` and every public page linked from it (tracks, generator, Ada, blog, subscribe). `robots.txt` exists. |
| Cosmos | `https://cosmos.punah.pro/` and rooms linked from it (planets, constellations, moon, learn, facts, quiz, Beast). |
| Cosmos v2 / back | `https://cosmos.punah.pro/back` and `https://cosmos.punah.pro/back/` (live HTML). |
| Stale | `https://cosmos.punah.pro/backend.html` returns **404**. Jarvis still opens this as “open backend”. |

Also list any extra public paths you find via `robots.txt`, sitemaps, and in-page links. Do not scan unrelated hosts.

### Security review (defensive)

For each live origin (`semicolon.punah.pro`, `cosmos.punah.pro`):

1. **Transport** — HTTPS only, HSTS, mixed content, redirect from http.
2. **Headers** — CSP, `X-Content-Type-Options`, `X-Frame-Options` / `frame-ancestors`, Referrer-Policy, Permissions-Policy, cookies (`Secure` / `HttpOnly` / `SameSite`).
3. **Disclosure** — missing `/.well-known/security.txt` (404 on both). Source maps, `.git`, `.env`, backup files — **HEAD/GET existence only**, do not download dumps of secrets into the report.
4. **Client JS** — Ada (`js/ada.js` → local `ada_server.py` :8420) and Beast (`js/chat.js` → local `beast_server.py` :8422). Confirm public pages do not expose API keys, Ollama, or a remotely reachable bridge. Flag if the browser calls a public URL that should stay laptop-only.
5. **Cosmos /back** — described as a read-only GET API baked to static files. Check that public JSON/HTML does not leak account emails, password hashes, session tokens, or admin routes.
6. **Forms** — Semicolon newsletter subscribe: HTTPS, no obvious open redirect.
7. **Hardening list** — concrete header/config/JS fixes. No exploit steps.

### Deliverable

Write `anshux/SITE_SECURITY_REPORT.md` with:

- Site map (URL, HTTP status, notes)
- Security findings (severity: high / medium / low / info)
- Recommended fixes for Semicolon, Cosmos, Cosmos /back, and Jarvis stale `backend.html` shortcut
- What was **not** tested (auth attacks, local Ada/Beast servers)

Cursor already observed: both origins have HSTS + `X-Frame-Options: SAMEORIGIN`; Cosmos also has `nosniff`; Semicolon `robots.txt` is 200; Cosmos `robots.txt` and `security.txt` are 404; `backend.html` is 404.
