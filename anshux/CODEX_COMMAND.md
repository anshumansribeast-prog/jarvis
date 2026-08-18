# Codex commands

## Codex Cloud (use this)

Open **https://chatgpt.com/codex/cloud**

1. New task
2. Repository: **`anshumansribeast-prog/semicolon`**
3. Paste the task from `anshux/CODEX_CLOUD_TASK.md` (the block after the line)

Full paste is in that file.

## Local Codex (laptop folder)

Only if Cloud is not used: `C:\Users\Anshu\semicolon` + `git apply` of `anshux/patches/semicolon-simple-again.patch`.

You are a **main** ANSHUX agent. Loop until `STATUS: STOP` in the jarvis `AGENT_TASK.md`. Do **not** idle. Do **not** rebuild the Code Generator.

## Goal

Make **Semicolon as simple as it was before** the Generator work.

Broken today (do not “fix” by keeping them):

- Code Generator page
- Practice “Run generated” / Generate tab

Also **fix** Ada on **mobile**: the chat box is too small to type.

## Do this in `C:\Users\Anshu\semicolon`

```powershell
cd C:\Users\Anshu\semicolon
git apply C:\Users\Anshu\jarvis\anshux\patches\semicolon-simple-again.patch
```

If `jarvis` is elsewhere, use that path. If `git apply` fails, do the same by hand:

1. Delete `pages/generate.html` and `js/generate.js`.
2. Remove every nav/footer/hero link to Generator.
3. Remove Practice tab **Run generated** / Generate project UI.
4. Keep Learn, Practice (challenges / web builder / free build / Python+Ada), Ada chat, blog, about.
5. In `css/style.css` under `@media (max-width: 860px)` for Ada: hide `.ada-rail` and `.ada-chips`; sticky `.ada-form` at the bottom; textarea `min-height: 7.5rem` and `font-size: 16px`; buttons min-height 44px. Cache-bust `style.css?v=20260818a` on `pages/ada.html`.

Then commit, push, deploy as you usually publish punah.pro.

## After apply

- `https://semicolon.punah.pro/pages/generate.html` should 404
- Practice should **not** say Generate a project
- Phone: Ada composer tall enough to type

Log as **Codex**. Leave jarvis `AGENT_TASK.md` as `STATUS: LOOP` until Anshuman writes STOP.
