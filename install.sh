#!/bin/bash
set -e

echo "Installing Crafter CLI..."

CLI_NAME="crafter"
INSTALL_DIR="/usr/local/bin"
REPO_URL="https://raw.githubusercontent.com/TU-USUARIO/crafter-cli/main"

# ---- check python ----
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# ---- check pipx ----
if ! command -v pipx &> /dev/null
then
    echo "⚠️ pipx not found. Installing via pip..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
fi

# ---- install crafter package ----
echo "Installing crafter via pipx..."
pipx install git+https://github.com/TU-USUARIO/crafter-cli.git || true

# ---- download wrapper ----
echo "Installing CLI wrapper..."
curl -fsSL "$REPO_URL/crafter.sh" -o $CLI_NAME

chmod +x $CLI_NAME
sudo mv $CLI_NAME $INSTALL_DIR/$CLI_NAME

echo ""
echo "✅ Crafter CLI installed successfully!"
echo "👉 Run: crafter --help"