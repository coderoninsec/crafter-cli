#!/usr/bin/env bash
set -euo pipefail

# ---- colors ----
GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

CLI_NAME="crafter"
INSTALL_DIR="/usr/local/bin"
REPO_RAW="https://raw.githubusercontent.com/coderoninsec/crafter-cli/main"
REPO_GIT="https://github.com/coderoninsec/crafter-cli.git"

# ---- spinner ----
spin() {
  local pid=$!
  local delay=0.1
  local spinstr='|/-\'

  while ps a | awk '{print $1}' | grep -q "$pid"; do
    local temp=${spinstr#?}
    printf " [%c]  " "$spinstr"
    spinstr=$temp${spinstr%"$temp"}
    sleep $delay
    printf "\b\b\b\b\b\b"
  done

  printf "    \b\b\b\b"
}

# ---- banner ----
echo -e "${GREEN}"
cat << "EOF"

 ██████╗ ██████╗ ██████╗ ███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝
██║     ██║   ██║██║  ██║█████╗  
██║     ██║   ██║██║  ██║██╔══╝  
╚██████╗╚██████╔╝██████╔╝███████╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝


██████╗  ██████╗ ███╗   ██╗██╗███╗   ██╗
██╔══██╗██╔═══██╗████╗  ██║██║████╗  ██║
██████╔╝██║   ██║██╔██╗ ██║██║██╔██╗ ██║
██╔══██╗██║   ██║██║╚██╗██║██║██║╚██╗██║
██║  ██║╚██████╔╝██║ ╚████║██║██║ ╚████║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝

        Crafter CLI

EOF
echo -e "${RESET}"

echo -e "${CYAN}→ Installing Crafter CLI...${RESET}"
sleep 0.3

# ---- checks ----
if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}❌ Python3 is required.${RESET}"
  echo "👉 Install it from: https://www.python.org/"
  exit 1
fi

mkdir -p "$HOME/.local/bin"

# ---- ensure pip ----
if ! python3 -m pip --version >/dev/null 2>&1; then
  echo -e "${YELLOW}⚠ pip not found. Installing...${RESET}"
  python3 -m ensurepip --upgrade || true
fi

# ---- check venv availability ----
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo -e "${RED}❌ python3-venv is required.${RESET}"
  echo "👉 Install it (Ubuntu): sudo apt install python3-venv"
  exit 1
fi

# ---- install method ----
if command -v pipx >/dev/null 2>&1; then
  echo -e "${CYAN}→ Using pipx...${RESET}"
  sleep 0.3

  if pipx list 2>/dev/null | grep -q "^package crafter "; then
    echo -e "${CYAN}→ Updating existing installation...${RESET}"
    (pipx upgrade crafter || pipx reinstall crafter) & spin
  else
    echo -e "${CYAN}→ Installing package...${RESET}"
    pipx install "git+${REPO_GIT}" & spin
  fi

else
  echo -e "${YELLOW}⚠ pipx not found. Using isolated venv...${RESET}"
  sleep 0.3

  INSTALL_PATH="$HOME/.crafter"

  python3 -m venv "$INSTALL_PATH"

  echo -e "${CYAN}→ Installing dependencies...${RESET}"
  "$INSTALL_PATH/bin/pip" install --upgrade pip & spin
  "$INSTALL_PATH/bin/pip" install "git+${REPO_GIT}" & spin

  ln -sf "$INSTALL_PATH/bin/crafter" "$HOME/.local/bin/crafter"

  export PATH="$HOME/.local/bin:$PATH"
fi

# ---- download wrapper ----
TMP_FILE="$(mktemp)"

echo -e "${CYAN}→ Installing CLI wrapper...${RESET}"
sleep 0.3

if ! curl -fsSL "${REPO_RAW}/crafter.sh" -o "${TMP_FILE}"; then
  echo -e "${RED}❌ Failed to download wrapper.${RESET}"
  exit 1
fi

# ---- sanity check ----
if ! grep -q "python3 -m crafter.cli" "${TMP_FILE}"; then
  echo -e "${RED}❌ Invalid wrapper. Aborting.${RESET}"
  rm -f "${TMP_FILE}"
  exit 1
fi

chmod 0755 "${TMP_FILE}"

# ---- move to PATH ----
if [ -w "${INSTALL_DIR}" ]; then
  mv "${TMP_FILE}" "${INSTALL_DIR}/${CLI_NAME}"
else
  sudo mv "${TMP_FILE}" "${INSTALL_DIR}/${CLI_NAME}"
fi

echo ""
echo -e "${GREEN}✔ Crafter CLI installed successfully!${RESET}"
echo -e "${CYAN}👉 Try:${RESET} crafter task"

# ---- PATH hint ----
if ! command -v crafter >/dev/null 2>&1; then
  echo -e "${YELLOW}⚠ If command not found, run:${RESET}"
  echo "export PATH=\$HOME/.local/bin:\$PATH"
fi