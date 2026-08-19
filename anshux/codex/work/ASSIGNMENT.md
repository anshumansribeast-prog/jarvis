# Codex SUB-2 — Semicolon + Cosmos (paste this if the repo is missing)

Project: **ANSHUX**. You are the **sub implementer**. Do not idle.

Wrong folder: `Documents\Codex\2026-08-17\role-*\work` (empty).  
Right folder: git clone of `anshumansribeast-prog/jarvis`.

There **are** sites. They are live on the internet, not files in `work/`.

## Sites (check these)

1. https://semicolon.punah.pro/
2. https://semicolon.punah.pro/robots.txt
3. https://semicolon.punah.pro/.well-known/security.txt
4. https://cosmos.punah.pro/
5. https://cosmos.punah.pro/robots.txt
6. https://cosmos.punah.pro/back
7. https://cosmos.punah.pro/back/
8. https://cosmos.punah.pro/backend.html
9. https://cosmos.punah.pro/.well-known/security.txt

Follow in-page links on (1) and (4) for tracks, Ada, planets, quiz, Beast, etc.

## If you have no network — use this Cursor probe (2026-08-17T18:04Z)

Do not say “there are no sites.” Write the report from this table.

| URL | HTTP | Notes |
| --- | --- | --- |
| https://semicolon.punah.pro/ | 200 | HTML ~24393 bytes. HSTS max-age=31536000. X-Frame-Options SAMEORIGIN. Referrer-Policy strict-origin-when-cross-origin. **No** CSP, **no** X-Content-Type-Options in response. |
| https://semicolon.punah.pro/robots.txt | 200 | text/plain, 475 bytes |
| https://semicolon.punah.pro/.well-known/security.txt | 404 | missing security.txt |
| https://cosmos.punah.pro/ | 200 | HSTS. X-Frame-Options SAMEORIGIN. X-Content-Type-Options nosniff. Referrer-Policy strict-origin-when-cross-origin. **No** CSP listed. |
| https://cosmos.punah.pro/robots.txt | 404 | missing robots.txt |
| https://cosmos.punah.pro/backend.html | 404 | Jarvis “open backend” still uses this URL |
| https://cosmos.punah.pro/back | 200 | Cosmos v2 / accounts API (static GET) |
| https://cosmos.punah.pro/back/ | 200 | same |
| https://cosmos.punah.pro/.well-known/security.txt | 404 | missing security.txt |

Product notes from Jarvis `config/projects.json`:

- Semicolon: Ada widget `js/ada.js` → local `ada_server.py` port **8420** (laptop only).
- Cosmos: Beast `js/chat.js` → local `beast_server.py` port **8422**; NASA APOD; `/back` is read-only GET baked to static files.

## Rules

Defensive review only. No exploits, PoCs, payloads, brute force, or auth bypass.

## Write this file

`anshux/codex/outputs/SITE_SECURITY_REPORT.md`

If you cannot write into the git repo, write the same markdown into **your** `outputs/` folder **and** say the path.

Include: site map, findings (high/medium/low/info), hardening list, Jarvis stale backend URL, Ada/Beast not public, what you did not test.

Then append one row to `AGENT_LOG.md` as **Codex** (if that file exists).
