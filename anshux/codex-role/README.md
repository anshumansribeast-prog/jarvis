# Archive — Codex role folder (do not use)

**MAIN is OpenCode now.** See `anshux/OPENCODE_START.md`. This folder was for old Codex Cloud/Documents paths.

---

# Codex role folder — COPY THIS WHOLE DIRECTORY

Codex is idle because it only reads **this folder**:

`C:\Users\Anshu\Documents\Codex\2026-08-17\<role-folder>\`

It looks for `.\work\`, `.\outputs\`, `.\AGENT_TASK.md`, `.\AGENT_LOG.md`, `.\README.md`.

Those files live here in git: `anshux/codex-role/`

## On the Windows laptop, seed Codex (one command)

Open PowerShell and run (fix the role folder name if it differs):

```powershell
$src = "C:\Users\Anshu\jarvis\anshux\codex-role"
$dst = Get-ChildItem "C:\Users\Anshu\Documents\Codex\2026-08-17" -Directory | Select-Object -First 1
Copy-Item -Path "$src\*" -Destination $dst.FullName -Recurse -Force
Write-Host "Seeded:" $dst.FullName
Get-ChildItem $dst.FullName, "$($dst.FullName)\work", "$($dst.FullName)\outputs"
```

If Jarvis is not at `C:\Users\Anshu\jarvis`, change `$src` to this repo’s `anshux\codex-role`.

Then tell Codex: **STATUS is REVIEW. Sites are the HTML files in .\work\. Write .\outputs\SITE_SECURITY_REPORT.md. Do not idle.**
