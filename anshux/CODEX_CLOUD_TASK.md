# Codex Cloud — paste at https://chatgpt.com/codex/cloud

**Repo to select:** `anshumansribeast-prog/semicolon` (not jarvis).

**Task title:** Simple Semicolon: drop Generator, fix mobile Ada

Paste everything below the line into the Codex Cloud task box:

---

You are Codex, an ANSHUX main agent. Do the work. Do not idle. Do not rebuild the Code Generator.

Repo: github.com/anshumansribeast-prog/semicolon  
Live site: https://semicolon.punah.pro/

Goal: make Semicolon as simple as it was BEFORE the Code Generator. Those Generator features are broken. Remove them. Fix Ada on phones so the message box is large enough to type.

Do this:

1. Delete `pages/generate.html` and `js/generate.js`.

2. Remove every link to Generator / generate.html from:
   - all `*.html` nav bars
   - footer
   - `index.html` hero “Code Generator” button and Generator shot-card
   - `pages/projects.html` CTAs
   - `pages/ada.html` (workshop should not point at generate.html)
   - `sitemap.xml`

3. On `pages/playground.html`:
   - Restore the Practice lede to: code runs in the browser, nothing to install. Do not mention generating a project.
   - Remove the **Run generated** tab (`#tabGen`) and the whole `#modeGen` panel (Generate / Run generated UI).
   - Keep Challenges, Python+Ada, Web Builder, Free Build.

4. Ada mobile (`css/style.css`), replace the existing `@media (max-width: 860px)` Ada block with:

```css
@media (max-width: 860px) {
  .ada-layout { grid-template-columns: 1fr; }
  .ada-rail { display: none; }
  .ada-chips { display: none; }
  .ada-page { padding-bottom: 0; }
  .ada-shell {
    min-height: 100dvh;
    min-height: 100vh;
    border-radius: 0;
  }
  .ada-log {
    flex: 1 1 auto;
    min-height: 0;
    max-height: none;
  }
  .ada-form {
    flex-direction: column;
    align-items: stretch;
    position: sticky;
    bottom: 0;
    background: var(--bg);
    padding: .85rem 1rem calc(.85rem + env(safe-area-inset-bottom));
  }
  .ada-form textarea {
    width: 100%;
    min-height: 7.5rem;
    font-size: 16px;
    line-height: 1.45;
  }
  .ada-form-actions { width: 100%; }
  .ada-form-actions .btn { min-height: 44px; flex: 1 1 auto; }
}
```

5. Cache-bust Ada CSS: `pages/ada.html` (and home if it uses the same query) set `style.css?v=20260818a`.

6. In `ada_server.py`, if any user-facing string tells people to open the Code Generator, change it to keep chatting on Ada.

Keep: Learn tracks, Practice (without generator), Ada chat, blog, about, contact.

Commit with a clear message and open a PR to `main`. After merge/deploy, `https://semicolon.punah.pro/pages/generate.html` should 404.

---
