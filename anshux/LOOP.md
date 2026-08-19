# ANSHUX loop — every office member

**STATUS: LOOP** until `AGENT_TASK.md` is `STOP`.
**The loop is incomplete if any office member is missing from the floor or has no task.**

**Architect: OpenCode.** Drawing + assign + chat: `python team.py office`.

| Desk (must exist) | Agent | Role | Default task |
| --- | --- | --- | --- |
| Architect’s table | **OpenCode** | Architect | Inspect both sites/PRs; assign tasks in the office chat |
| Check | **Cursor** | Checker | Confirm every member is on the floor; pytest |
| Build | **Aider** | Builder | Restore Ada API on PR #8 |
| Editor | **Continue** | Editor | `anshux.code-workspace` |
| Optional build | **Cline** | Extra builder | Help Aider if assigned |
| Tutor | **Ada** | Semicolon | Teach on ada.html |
| Tutor | **Beast** | Cosmos | Astronomy on cosmos.punah.pro |

Assign in the office UI, or:

```powershell
python team.py assign aider Restore Ada API on PR 8
python team.py assign ada Stay on Semicolon chat only
```

Chat with the architect on the office page (needs `python team.py office` running).
