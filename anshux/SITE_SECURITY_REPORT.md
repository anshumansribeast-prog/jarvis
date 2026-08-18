# ANSHUX site security report — Semicolon + Cosmos

Reviewer: **Cursor** (main). Date: 2026-08-18. Method: HTTPS GET/HEAD on owner sites only. No exploits, no POST to chat, no fuzzing.

**LOOP:** Cursor and Codex re-check this until `AGENT_TASK.md` is `STATUS: STOP`. Knowledge brains: Ada (Semicolon), Beast (Cosmos).

**Generator:** Live Semicolon still has `/pages/generate.html`. Removal is in `anshux/patches/semicolon-remove-generator.patch` (this agent cannot push the semicolon repo).

## Site map

| URL | Status | Notes |
| --- | --- | --- |
| http://semicolon.punah.pro/ | 200 after redirect | Lands on HTTPS |
| https://semicolon.punah.pro/ | 200 | Home. HSTS, X-Frame-Options SAMEORIGIN, Referrer-Policy. No CSP, no nosniff |
| https://semicolon.punah.pro/robots.txt | 200 | Allow /, sitemap.xml, crawl-delay 1 |
| https://semicolon.punah.pro/sitemap.xml | 200 | 31 public URLs (learn, blog, Ada, lessons, generator, …) |
| https://semicolon.punah.pro/pages/ada.html | 200 | Ada UI |
| https://semicolon.punah.pro/js/ada-api.js | 200 | `ADA_URL = "/api/ada"` POST JSON |
| https://semicolon.punah.pro/api/ada | 200 GET JSON | Public health-style payload (see findings) |
| https://semicolon.punah.pro/.well-known/security.txt | 404 | |
| https://semicolon.punah.pro/.git/HEAD | 404 | good |
| https://semicolon.punah.pro/.env | 404 | good |
| http://cosmos.punah.pro/ | 200 after redirect | HTTPS |
| https://cosmos.punah.pro/ | 200 | HSTS, nosniff, SAMEORIGIN. No CSP |
| https://cosmos.punah.pro/robots.txt | 404 | |
| https://cosmos.punah.pro/sitemap.xml | 404 | |
| https://cosmos.punah.pro/js/chat.js | 200 | Beast: `/api/beast`, NASA `DEMO_KEY` |
| https://cosmos.punah.pro/api/beast | 404 | POST URL not a GET page |
| https://cosmos.punah.pro/api/beast/learned | 200 JSON | Daily APOD/moon/fact — no emails in sample |
| https://cosmos.punah.pro/back | 200 | Cosmos v2 UI (accounts/quiz copy in HTML) |
| https://cosmos.punah.pro/backend.html | 404 | Jarvis still opens this |
| https://cosmos.punah.pro/package.json | 200 | `astronomy-site` 2.0.0, `node server/index.js` |
| https://cosmos.punah.pro/.well-known/security.txt | 404 | |
| https://cosmos.punah.pro/.git/HEAD | 404 | good |
| https://cosmos.punah.pro/.env | 404 | good |

## Findings

| Sev | Item |
| --- | --- |
| Medium | Semicolon **`GET /api/ada` is public** and returns JSON (`ok`, `model`, `ollama`, `api`, `visitor`, `notes`). Ada is not laptop-only `:8420` on this deploy; it is on the same origin. Restrict GET info, rate-limit POST `/api/ada`, keep Ollama off the public internet. |
| Medium | Cosmos **/back HTML says Phase 3 can write** (accounts, quiz on the server). Jarvis `projects.json` still says read-only GET static. Align docs and lock down writes (auth, CSRF, rate limits) if writes are real. |
| Low | Neither origin sends **Content-Security-Policy**. Semicolon also lacks **X-Content-Type-Options: nosniff**. |
| Low | **security.txt** missing on both. Cosmos **robots.txt** and **sitemap.xml** missing. |
| Low | Public **package.json** on cosmos.punah.pro describes the Node start script (info leak, not a secret). |
| Low | Beast uses NASA **DEMO_KEY** (documented public demo key; quota sharing). Fine until rate-limited. |
| Info | `.git` and `.env` not exposed on either origin (HEAD/GET 404). |
| Info | HTTP→HTTPS works for both homes. HSTS `max-age=31536000` present. |
| Info | Jarvis `SITES["backend"]` = `https://cosmos.punah.pro/backend.html` (**404**). Use `/back`. |
| Info | `/api/beast/learned` sample was space facts only, not account PII. |

## Hardening (no exploit steps)

1. Add CSP (default-src self; allow highlight.js CDN on Semicolon if still used).
2. Add `X-Content-Type-Options: nosniff` on Semicolon; `Permissions-Policy` on both.
3. Publish `/.well-known/security.txt`. Add Cosmos `robots.txt` / sitemap if you want indexing.
4. Do not return visitor nicknames or model names on unauthenticated `GET /api/ada`.
5. Confirm `/api/ada` POST cannot reach a public Ollama; laptop bridge should stay off the public host.
6. Fix Jarvis backend URL to `/back`.
7. Hide or unpublish production `package.json` if you do not need it public.

## Not tested

POST bodies to Ada/Beast, account signup on /back, XSS in user content, password storage, local `:8420` / `:8422` on the laptop.
