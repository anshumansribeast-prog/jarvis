# AGENT_TASK

PROJECT: ANSHUX
STATUS: REVIEW

MAINS: Cursor, Codex
KNOWLEDGE: Claude, ChatGPT, Gemini
REMOVED: Claude Code

## Codex job (now)

Read `.\work\` and `../SITE_SECURITY_REPORT.md` if this is the git repo, or write `.\outputs\SITE_SECURITY_REPORT.md` in the role folder. Same defensive rules. You are a **main**, not a sub.

Codex: you are in the role folder. **Do not idle.** `.\work\` is seeded. There are sites to review as files.

## Codex job (now)

1. Read every file in `.\work\`
2. Write `.\outputs\SITE_SECURITY_REPORT.md`
3. Append one row to `.\AGENT_LOG.md` as Codex

### Sites in work/ (snapshots of live pages, 2026-08-17)

| File | Live URL | HTTP |
| --- | --- | --- |
| `work/semicolon-punah-pro.html` | https://semicolon.punah.pro/ | 200 |
| `work/semicolon-robots.txt` | https://semicolon.punah.pro/robots.txt | 200 |
| `work/cosmos-punah-pro.html` | https://cosmos.punah.pro/ | 200 |
| `work/cosmos-punah-pro-back.html` | https://cosmos.punah.pro/back | 200 |
| `work/HEADERS.md` | probe of all URLs including 404s | — |

Also note (no HTML snapshot; 404): https://cosmos.punah.pro/backend.html and both origins’ `/.well-known/security.txt`. Cosmos `/robots.txt` is 404.

Defensive review only. No exploits. Cover HTTPS/HSTS/headers/CSP, missing security.txt, Ada :8420 / Beast :8422 must stay laptop-only, `/back` must not leak accounts, Jarvis stale backend.html shortcut.
