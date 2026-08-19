Paste into **OpenCode** (`python team.py opencode`). Use **Ollama**, not Claude Sonnet.

You are **site inspection in charge** for ANSHUX. Cursor checks that you actually inspected. Aider implements Semicolon code. Do not idle.

Inspect **both** live sites and **both** PR streams:

1) Semicolon live: https://semicolon.punah.pro/
   Ada: /pages/ada.html  Concepts: /pages/concepts.html
   Generator: /pages/generate.html  (should become 404)

2) Semicolon PR: https://github.com/anshumansribeast-prog/semicolon/pull/8
   Keep Generator deleted.
   Flag if PR deletes js/ada-api.js, /api/ada, Concepts, img/ada.jpg — those must be restored.

3) Cosmos live: https://cosmos.punah.pro/ and https://cosmos.punah.pro/back
   backend.html 404 is expected.

4) Cosmos PRs: open PRs on the Cosmos GitHub repo if you have it cloned (`../cosmos` or `projects/cosmos`). If there is no repo access, inspect live Cosmos only and write that in the office.

Write findings into the office: run `python team.py office` or tell Cursor. Do not rebuild the Code Generator.
