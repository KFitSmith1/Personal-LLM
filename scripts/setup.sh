#!/usr/bin/env bash
# One-shot bootstrap for a fresh Ubuntu 22.04/24.04 GPU server.
# Installs Docker + NVIDIA container toolkit, then brings the stack up.
# Re-running is safe (idempotent-ish). Review before running as root.
set -euo pipefail

echo "==> Updating packages..."
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y curl git ufw ca-certificates gnupg openssl

echo "==> Installing Docker (if missing)..."
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  echo "    Docker installed. Log out/in (or run 'newgrp docker') for group changes."
fi

echo "==> Installing NVIDIA container toolkit (for GPU passthrough)..."
if command -v nvidia-smi >/dev/null 2>&1; then
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y nvidia-container-toolkit
  sudo nvidia-ctk runtime configure --runtime=docker
  sudo systemctl restart docker
else
  echo "    No nvidia-smi found. Skipping GPU toolkit. Remove the 'deploy:' block"
  echo "    from docker-compose.yml to run CPU-only."
fi

echo "==> Configuring firewall (SSH + web UIs)..."
sudo ufw allow OpenSSH || true
sudo ufw allow 3000 || true   # Open WebUI
sudo ufw allow 8502 || true   # Open Notebook UI
# NOTE: deliberately NOT opening 11434 (Ollama), 8000 (SurrealDB), 5055 (API).
sudo ufw --force enable || true

echo "==> Creating .env if missing..."
if [ ! -f .env ]; then
  cp .env.example .env
  # Auto-fill secrets
  sed -i "s/CHANGE_ME_run_openssl_rand_hex_32/$(openssl rand -hex 32)/" .env
  sed -i "s/CHANGE_ME_strong_password/$(openssl rand -hex 16)/" .env
  sed -i "s/CHANGE_ME_strong_db_password/$(openssl rand -hex 16)/" .env
  echo "    Generated .env with random secrets. Review it: cat .env"
fi

echo "==> Starting the stack..."
docker compose up -d

echo "==> Pulling models..."
./scripts/pull-models.sh

echo ""
echo "============================================================"
echo " Setup complete."
echo "   Open Notebook : http://<server-ip>:8502"
echo "   Open WebUI    : http://<server-ip>:3000"
echo " Next: configure Ollama inside Open Notebook (see README)."
echo "============================================================"
