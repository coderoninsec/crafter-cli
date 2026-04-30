#!/usr/bin/env bash

set -e

GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RESET="\033[0m"

VERSION="v0.1"

# -------------------------
# UNINSTALL MODE
# -------------------------
if [[ "$1" == "--uninstall" ]]; then
    echo ""
    echo "🗑 Removing Crafter CLI..."

    if command -v pipx &> /dev/null; then
        pipx uninstall crafter >/dev/null 2>&1 || true
    fi

    echo -e "${GREEN}✔ Crafter removed${RESET}"
    echo ""
    exit 0
fi

# -------------------------
# BANNER
# -------------------------
echo ""
echo -e "${GREEN}   ██████╗ ██████╗ ██████╗ ███████╗${RESET}"
echo -e "${GREEN}  ██╔════╝██╔═══██╗██╔══██╗██╔════╝${RESET}"
echo -e "${GREEN}  ██║     ██║   ██║██║  ██║█████╗  ${RESET}"
echo -e "${GREEN}  ██║     ██║   ██║██║  ██║██╔══╝  ${RESET}"
echo -e "${GREEN}  ╚██████╗╚██████╔╝██████╔╝███████╗${RESET}"
echo -e "${GREEN}   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝${RESET}"
echo ""
echo -e "${GREEN}  ██████╗  ██████╗ ███╗   ██╗██╗███╗   ██╗${RESET}"
echo -e "${GREEN}  ██╔══██╗██╔═══██╗████╗  ██║██║████╗  ██║${RESET}"
echo -e "${GREEN}  ██████╔╝██║   ██║██╔██╗ ██║██║██╔██╗ ██║${RESET}"
echo -e "${GREEN}  ██╔══██╗██║   ██║██║╚██╗██║██║██║╚██╗██║${RESET}"
echo -e "${GREEN}  ██║  ██║╚██████╔╝██║ ╚████║██║██║ ╚████║${RESET}"
echo -e "${GREEN}  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝${RESET}"
echo ""
echo -e "${CYAN}        Crafter CLI${RESET}"
echo ""

# -------------------------
# DOWNLOAD BAR
# -------------------------
echo -e "${CYAN}Downloading Crafter CLI (${VERSION})...${RESET}"

BAR_WIDTH=30
for ((i=0; i<=BAR_WIDTH; i++)); do
  percent=$(( i * 100 / BAR_WIDTH ))
  filled=$(printf "%${i}s" | tr ' ' '#')
  empty=$(printf "%$((BAR_WIDTH-i))s" | tr ' ' '.')
  printf "\r[%s%s] %d%%" "$filled" "$empty" "$percent"
  sleep 0.02
done

echo ""
echo ""

# -------------------------
# SPINNER
# -------------------------
spinner() {
    local pid=$!
    local spin='-\|/'
    local i=0

    tput civis 2>/dev/null || true

    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\rInstalling... %s " "${spin:$i:1}"
        sleep 0.1
    done

    printf "\rInstalling... done ✔\n"
    tput cnorm 2>/dev/null || true
}

# -------------------------
# SYSTEM DEPENDENCIES (Debian / WSL)
# -------------------------
if [[ -f /etc/debian_version ]]; then
    echo -e "${YELLOW}Installing system dependencies...${RESET}"

    sudo apt update -y >/dev/null 2>&1

    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        git >/dev/null 2>&1
fi

# -------------------------
# CHECK PYTHON
# -------------------------
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed."
    exit 1
fi

# -------------------------
# pipx
# -------------------------
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}Installing pipx...${RESET}"

    python3 -m pip install --user pipx >/dev/null 2>&1 &
    spinner
    wait

    python3 -m pipx ensurepath >/dev/null 2>&1
    export PATH="$HOME/.local/bin:$PATH"
fi

# -------------------------
# VERIFY pipx
# -------------------------
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}pipx installed but not in PATH.${RESET}"
    echo "Run:"
    echo "  export PATH=\$HOME/.local/bin:\$PATH"
    exit 1
fi

# -------------------------
# INSTALL CLI
# -------------------------
echo -e "${CYAN}Installing Crafter CLI...${RESET}"

pipx install --force git+https://github.com/coderoninsec/crafter-cli.git >/dev/null 2>&1 &
spinner
wait

# -------------------------
# SUCCESS
# -------------------------
echo ""
echo -e "${GREEN}✔ Crafter CLI installed successfully${RESET}"
echo ""

echo -e "${CYAN}Next steps:${RESET}"
echo "  crafter help"
echo ""

echo ""
echo -e "${CYAN}Next steps:${RESET}"
echo "  crafter --help"
echo ""

if ! command -v crafter &> /dev/null; then
    echo -e "${YELLOW}If 'crafter' not found, restart your terminal.${RESET}"
fi