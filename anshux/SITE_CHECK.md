# Site check (Cursor) — 2026-08-18T12:00Z

Live hosts only. Generator is still **on** production until OpenCode applies `semicolon-simple-again.patch`.

| URL | Status | Proper? |
| --- | --- | --- |
| https://semicolon.punah.pro/ | 200 | Home up. Still links Generator (not simple yet). |
| https://semicolon.punah.pro/pages/generate.html | 200 | **Should go away** after patch (feature reported broken). |
| https://semicolon.punah.pro/pages/playground.html | 200 | Practice up; still has Run generated / Generate. |
| https://semicolon.punah.pro/pages/ada.html | 200 | Chat up; **mobile composer too small** until CSS patch. |
| https://semicolon.punah.pro/pages/learn.html | 200 | Tracks OK. |
| https://cosmos.punah.pro/ | 200 | OK. |
| https://cosmos.punah.pro/back | 200 | OK (Jarvis open-backend). |
| https://cosmos.punah.pro/backend.html | 404 | Expected stale path. |

**Verdict:** Sites are reachable. Semicolon is **not** simple yet on punah.pro. OpenCode must apply the patch on the **semicolon** repo (this Cursor run cannot push that repo). After deploy, Cursor should see generate.html 404 and Ada mobile CSS `20260818a`.
