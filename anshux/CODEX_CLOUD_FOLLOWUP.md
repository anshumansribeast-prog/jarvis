# Follow-up for this Codex Cloud task

Open: https://chatgpt.com/codex/cloud/tasks/task_e_6a8542fc5b5c832598c087710241dfcf

If the task is on the **wrong repo**, set environment to **github.com/anshumansribeast-prog/semicolon**.

Paste this as the next message on that task:

---

You are **MAIN** for project ANSHUX (new Codex account). Cursor only checks the live site after you ship. Do not idle. Do not rebuild the Code Generator.

Work in **github.com/anshumansribeast-prog/semicolon**.

Make Semicolon simple like before Generator:

1. Delete `pages/generate.html` and `js/generate.js`.
2. Remove every Generator / generate.html link (nav, footer, index hero + shot-card, projects, ada, sitemap).
3. On `pages/playground.html` remove **Run generated** (`#tabGen` and `#modeGen`). Keep Challenges, Python+Ada, Web Builder, Free Build. Lede: code runs in the browser, nothing to install.
4. Mobile Ada in `css/style.css` `@media (max-width: 860px)`: hide `.ada-rail` and `.ada-chips`; shell `min-height: 100dvh`; sticky `.ada-form`; textarea `min-height: 7.5rem` and `font-size: 16px`; buttons `min-height: 44px`. Cache-bust `pages/ada.html` to `style.css?v=20260818a`.
5. If `ada_server.py` tells people to open the Code Generator, tell them to stay in Ada chat.
6. Commit and open a PR to `main`. After deploy, `https://semicolon.punah.pro/pages/generate.html` must 404.

Keep looping on polish (nav, mobile Ada) until the human sets STOP. You are MAIN.

---
