# HTTP probe (Cursor, 2026-08-17T18:04Z) — no network required

Defensive inventory only.

## semicolon.punah.pro/

```
HTTP/2 200
content-type: text/html
strict-transport-security: max-age=31536000
x-frame-options: SAMEORIGIN
referrer-policy: strict-origin-when-cross-origin
content-length: 24393
```

Missing vs Cosmos: `x-content-type-options`. Missing both: Content-Security-Policy, Permissions-Policy.

## semicolon.punah.pro/robots.txt

HTTP/2 200 text/plain. Allows `/`. Sitemap: https://semicolon.punah.pro/sitemap.xml

## semicolon.punah.pro/.well-known/security.txt

HTTP/2 404

## cosmos.punah.pro/

```
HTTP/2 200
content-type: text/html; charset=utf-8
strict-transport-security: max-age=31536000
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
referrer-policy: strict-origin-when-cross-origin
```

Missing: Content-Security-Policy.

## cosmos.punah.pro/robots.txt

HTTP/2 404

## cosmos.punah.pro/backend.html

HTTP/2 404 — Jarvis `SITES["backend"]` still points here.

## cosmos.punah.pro/back  and  /back/

HTTP/2 200 HTML (Cosmos v2, read-only GET / static).

## cosmos.punah.pro/.well-known/security.txt

HTTP/2 404

## Product notes

- Ada: `js/ada.js` → local ada_server.py :8420
- Beast: `js/chat.js` → local beast_server.py :8422
- Do not treat localhost bridges as public sites
