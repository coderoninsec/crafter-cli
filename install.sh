#!/usr/bin/env bash
set -euo pipefail

CLI_NAME="crafter"
INSTALL_DIR="/usr/local/bin"
REPO_RAW="https://raw.githubusercontent.com/coderoninsec/crafter-cli/main"
REPO_GIT="https://github.com/coderoninsec/crafter-cli.git"

echo "Installing Crafter CLI..."

# ---- checks ----
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python3 is required but not installed."
  exit 1
fi

# ---- ensure pipx ----
if ! command -v pipx >/dev/null 2>&1; then
  echo "⚠️ pipx not found. Installing via pip..."
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
  export PATH="$HOME/.local/bin:$PATH"
fi

# ---- install or upgrade package ----
echo "Installing/Updating crafter via pipx..."
if pipx list 2>/dev/null | grep -q "^package crafter "; then
  pipx upgrade crafter || pipx reinstall crafter
else
  pipx install "git+${REPO_GIT}"
fi

# ---- download wrapper safely ----
TMP_FILE="$(mktemp)"
echo "Installing CLI wrapper..."
curl -fsSL "${REPO_RAW}/crafter.sh" -o "${TMP_FILE}"

# basic sanity check
if ! grep -q "python3 -m crafter.cli" "${TMP_FILE}"; then
  echo "❌ Downloaded wrapper does not look valid. Aborting."
  rm -f "${TMP_FILE}"
  exit 1
fi

chmod +x "${TMP_FILE}"

# ---- move to PATH ----
if [ -w "${INSTALL_DIR}" ]; then
  mv "${TMP_FILE}" "${INSTALL_DIR}/${CLI_NAME}"
else
  sudo mv "${TMP_FILE}" "${INSTALL_DIR}/${CLI_NAME}"
fi

echo ""
echo "✅ Crafter CLI installed successfully!"
echo "👉 Run: crafter --help"

# ---- PATH hint ----
if ! command -v crafter >/dev/null 2>&1; then
  echo "⚠️ If 'crafter' is not found, restart your terminal or ensure:"
  echo "   export PATH=\$HOME/.local/bin:\$PATH"
fi