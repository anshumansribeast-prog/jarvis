#!/usr/bin/env bash
# Deploy AnshuX to https://anshux.punah.pro (run on your Linux server as root/sudo)
set -euo pipefail

REPO_DIR="${1:-/opt/anshux}"
PUBLIC_URL="${ANSUX_PUBLIC_URL:-https://anshux.punah.pro}"

echo "==> Installing AnshuX to ${REPO_DIR}"
mkdir -p "${REPO_DIR}"
rsync -a --exclude venv --exclude .git --exclude __pycache__ ./ "${REPO_DIR}/"

cd "${REPO_DIR}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
fi

grep -q '^ANSUX_PUBLIC_URL=' .env && sed -i "s|^ANSUX_PUBLIC_URL=.*|ANSUX_PUBLIC_URL=${PUBLIC_URL}|" .env || echo "ANSUX_PUBLIC_URL=${PUBLIC_URL}" >> .env
grep -q '^ANSUX_HUD_HOST=' .env && sed -i 's|^ANSUX_HUD_HOST=.*|ANSUX_HUD_HOST=127.0.0.1|' .env || echo 'ANSUX_HUD_HOST=127.0.0.1' >> .env
grep -q '^ANSUX_TEXT_ONLY=' .env && sed -i 's|^ANSUX_TEXT_ONLY=.*|ANSUX_TEXT_ONLY=true|' .env || echo 'ANSUX_TEXT_ONLY=true' >> .env

echo "==> Installing systemd service"
sudo cp scripts/deploy/anshux.service /etc/systemd/system/anshux.service
sudo sed -i "s|/opt/anshux|${REPO_DIR}|g" /etc/systemd/system/anshux.service
sudo systemctl daemon-reload
sudo systemctl enable anshux
sudo systemctl restart anshux

echo "==> Installing nginx config"
sudo cp scripts/deploy/nginx-anshux.conf /etc/nginx/sites-available/anshux
sudo ln -sf /etc/nginx/sites-available/anshux /etc/nginx/sites-enabled/anshux
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "AnshuX deployed!"
echo "  Public URL: ${PUBLIC_URL}"
echo "  Service:    sudo systemctl status anshux"
echo ""
echo "If SSL is not set up yet, run:"
echo "  sudo certbot --nginx -d anshux.punah.pro"
