#!/usr/bin/env bash

set -e

# -------------------------
# COLORS
# -------------------------
GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RESET="\033[0m"

# -------------------------
# VERSION
# -------------------------
VERSION="v0.1"

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
# DOWNLOAD EFFECT
# -------------------------
echo -e "${CYAN}Downloading Crafter CLI (${VERSION})...${RESET}"

for i in {1..30}; do
  echo -n "#"
  sleep 0.$((RANDOM % 3 + 1))
done

echo ""
echo ""

# -------------------------
# SPINNER FUNCTION
# -------------------------
spinner() {
    local pid=$!
    local spin='-\|/'
    local i=0

    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r${CYAN}Installing... ${spin:$i:1}${RESET}"
        sleep .1
    done

    printf "\r"
}

# -------------------------
# INSTALL pipx (if needed)
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
# INSTALL CLI
# -------------------------
echo -e "${CYAN}Installing Crafter CLI...${RESET}"

pipx install --force git+https://github.com/coderoninsec/crafter-cli.git >/dev/null 2>&1 &
spinner
wait

# -------------------------
# SUCCESS
# -------------------------
echo -e "${GREEN}✔ Crafter CLI installed successfully${RESET}"
echo ""
echo -e "${CYAN}Next steps:${RESET}"
echo "  crafter help"
echo ""