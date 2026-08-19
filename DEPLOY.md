# Deploy ANSHUX Command Office on a server

This is the **office site** (Commander + OpenCode + floor + VR + Progress + Ship).  
It is **not** semicolon.punah.pro or cosmos.punah.pro — it is this repo’s office on port **8765**.

Mail reports go to **abhiis@eleven11.pro**.

---

## What you need on the server

| Item | Notes |
| --- | --- |
| OS | Linux (Ubuntu 22.04+ recommended) |
| Python | 3.10+ |
| Git | to clone this repo |
| Port | **8765** open (firewall / security group) |
| Optional | nginx reverse proxy + HTTPS |

Repo: `https://github.com/anshumansribeast-prog/jarvis`  
Branch with office features: `cursor/anshx-qa-loop-8b8a` (or merge to `main` first)

---

## Fast deploy (copy-paste)

```bash
# 1) Clone
sudo mkdir -p /opt/anshux && sudo chown "$USER":"$USER" /opt/anshux
cd /opt/anshux
git clone https://github.com/anshumansribeast-prog/jarvis.git
cd jarvis
git checkout cursor/anshx-qa-loop-8b8a   # or main after merge

# 2) Python env
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install pytest   # used by Testing Agent

# 3) Env for server
export ANSHUX_OFFICE_HOST=0.0.0.0
export ANSHUX_OFFICE_NO_BROWSER=1
export ANSHUX_ABHISHEK_EMAIL=abhiis@eleven11.pro
# optional model label shown in UI:
# export COMMANDER_MODEL=ollama/llama3.2:3b

# 4) Start
./scripts/deploy-office.sh
```

Open: **http://YOUR_SERVER_IP:8765/**

Same page also at `/command/`.

---

## One-command start script

`scripts/deploy-office.sh` binds `0.0.0.0:8765`, skips opening a local browser, and keeps the office alive.

```bash
cd /opt/anshux/jarvis
./scripts/deploy-office.sh
```

Or:

```bash
ANSHUX_OFFICE_HOST=0.0.0.0 ANSHUX_OFFICE_NO_BROWSER=1 \
  .venv/bin/python team.py office
```

---

## systemd (stay up after reboot)

```bash
sudo cp /opt/anshux/jarvis/scripts/anshux-office.service /etc/systemd/system/
# edit WorkingDirectory / User if needed
sudo systemctl daemon-reload
sudo systemctl enable --now anshux-office
sudo systemctl status anshux-office
```

Logs:

```bash
journalctl -u anshux-office -f
```

---

## nginx + HTTPS (recommended for public)

Example `/etc/nginx/sites-available/office`:

```nginx
server {
    listen 80;
    server_name office.eleven11.pro;   # change to your DNS

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/office /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
# then certbot --nginx -d office.eleven11.pro
```

---

## Docker (optional)

```bash
cd /opt/anshux/jarvis
docker build -t anshux-office -f Dockerfile.office .
docker run -d --name anshux-office -p 8765:8765 \
  -e ANSHUX_ABHISHEK_EMAIL=abhiis@eleven11.pro \
  -e ANSHUX_OFFICE_NO_BROWSER=1 \
  anshux-office
```

---

## After deploy — what to click

| Page | URL path | Purpose |
| --- | --- | --- |
| Home / office | `/` | Commander + floor |
| VR office | nav → **VR office** | See what each desk/agent is doing |
| Progress | nav → **Progress** | Per-agent % charts |
| Storage | nav → **Storage** | Shared site files under `command_office/workspace/projects/` |
| Ship | nav → **Ship · GitHub · Mail** | Push + mail **abhiis@eleven11.pro** |

Assign everyone: seat **Everyone (whole floor)** → **Assign to whole office**.

---

## Main folders (what must be on the server)

```
jarvis/
  team.py                 # starts the office server
  office/index.html        # UI (do NOT open as a file:// page)
  command_office/         # Commander agents, planner, ship, storage
  scripts/deploy-office.sh
  scripts/anshux-office.service
  Dockerfile.office
  DEPLOY.md               # this file
```

Runtime data (created on the server, not required in git):

- `command_office/data/*.json` — tasks, agents, settings  
- `command_office/workspace/projects/<site>/` — shared site Storage  
- `office/briefing-abhishek.md` — last mail report  

---

## Firewall

```bash
# Ubuntu ufw
sudo ufw allow 8765/tcp
sudo ufw reload
```

If only nginx fronts it, open **80/443** and keep 8765 on localhost.

---

## Ship mail to Abhishek

Default email: **abhiis@eleven11.pro**

- UI: **Ship · GitHub · Mail** → Open mail / Ship all  
- Optional SMTP auto-send:

```bash
export ANSHUX_ABHISHEK_EMAIL=abhiis@eleven11.pro
export ANSHUX_SMTP_HOST=smtp.example.com
export ANSHUX_SMTP_PORT=587
export ANSHUX_SMTP_USER=...
export ANSHUX_SMTP_PASS=...
export ANSHUX_SMTP_FROM=office@eleven11.pro
```

---

## Health check

```bash
curl -s http://127.0.0.1:8765/api/office | head
curl -s http://127.0.0.1:8765/api/command/vr | head
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
```

Expect `200` and JSON with `boss: AnshuX`.

---

## Do not

- Do not double-click `office/index.html` — APIs will fail  
- Do not bind only `127.0.0.1` if users need remote access (use `0.0.0.0`)  
- Do not confuse this with Semicolon/Cosmos — those are separate sites  

---

## Contact

- Boss / AnshuX office UI greets **AnshuX**  
- Ship reports → **abhiis@eleven11.pro**  
- GitHub PR: https://github.com/anshumansribeast-prog/jarvis/pull/2  
