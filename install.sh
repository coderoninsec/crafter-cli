#!/usr/bin/env bash

set -e

GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RESET="\033[0m"

VERSION="v0.1"

have_cmd() {
    command -v "$1" >/dev/null 2>&1
}

is_wsl() {
    [[ -n "${WSL_INTEROP:-}" || -n "${WSL_DISTRO_NAME:-}" ]] && return 0
    grep -qi microsoft /proc/version 2>/dev/null
}

detect_pkg_manager() {
    if [[ "$(uname -s)" == "Darwin" ]]; then
        PKG_MANAGER="brew"
        return
    fi

    if is_wsl; then
        PKG_MANAGER="apt"
        return
    fi

    if [[ -r /etc/os-release ]]; then
        . /etc/os-release
        case "${ID:-}" in
            debian|ubuntu)
                PKG_MANAGER="apt"
                ;;
            arch|manjaro|endeavouros|artix)
                PKG_MANAGER="pacman"
                ;;
            fedora|rhel|centos|rocky|almalinux)
                PKG_MANAGER="dnf"
                ;;
            *)
                case "${ID_LIKE:-}" in
                    *debian*) PKG_MANAGER="apt" ;;
                    *arch*) PKG_MANAGER="pacman" ;;
                    *fedora*|*rhel*) PKG_MANAGER="dnf" ;;
                    *) PKG_MANAGER="" ;;
                esac
                ;;
        esac
    fi
}

run_pkg_manager() {
    if [[ "$PKG_MANAGER" == "brew" ]]; then
        "$@"
        return
    fi

    if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
        if ! have_cmd sudo; then
            echo "sudo is required to install system dependencies."
            exit 1
        fi
        sudo "$@"
        return
    fi

    "$@"
}

install_system_dependencies() {
    local -a packages=()

    if [[ -z "$PKG_MANAGER" ]]; then
        echo "Unsupported operating system."
        exit 1
    fi

    if ! have_cmd "$PKG_MANAGER"; then
        echo "${PKG_MANAGER} is required but not installed."
        exit 1
    fi

    case "$PKG_MANAGER" in
        apt)
            packages=(python3 python3-pip python3-venv curl git)
            ;;
        pacman)
            packages=(python python-pip python-virtualenv curl git)
            ;;
        dnf)
            packages=(python3 python3-pip python3-virtualenv curl git)
            ;;
        brew)
            packages=(python curl git)
            ;;
        *)
            echo "Unsupported operating system."
            exit 1
            ;;
    esac

    if ! have_cmd python3 || ! python3 -m pip --version >/dev/null 2>&1 || ! have_cmd curl || ! have_cmd git; then
        echo -e "${YELLOW}Installing system dependencies...${RESET}"
        case "$PKG_MANAGER" in
            apt)
                run_pkg_manager apt update -y >/dev/null 2>&1
                run_pkg_manager apt install -y "${packages[@]}" >/dev/null 2>&1
                ;;
            pacman)
                run_pkg_manager pacman -Sy --noconfirm --needed "${packages[@]}" >/dev/null 2>&1
                ;;
            dnf)
                run_pkg_manager dnf install -y "${packages[@]}" >/dev/null 2>&1
                ;;
            brew)
                brew install "${packages[@]}" >/dev/null 2>&1
                ;;
        esac
    fi
}

run_with_spinner() {
    "$@" >/dev/null 2>&1 &
    local pid=$!
    spinner "$pid"
    set +e
    wait "$pid"
    local status=$?
    set -e
    return "$status"
}

run_with_retry() {
    local -a cmd=("$@")
    local attempt=1

    while (( attempt <= 2 )); do
        if run_with_spinner "${cmd[@]}"; then
            return 0
        fi

        if (( attempt == 1 )); then
            echo -e "${YELLOW}Retrying...${RESET}"
        fi

        attempt=$(( attempt + 1 ))
    done

    return 1
}

# -------------------------
# UNINSTALL MODE
# -------------------------
if [[ "$1" == "--uninstall" ]]; then
    echo ""
    echo "🗑 Removing Crafter CLI..."

    if have_cmd pipx; then
        pipx uninstall crafter >/dev/null 2>&1 || true
    elif have_cmd python3 && python3 -m pipx --version >/dev/null 2>&1; then
        python3 -m pipx uninstall crafter >/dev/null 2>&1 || true
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
    local pid="${1:-$!}"
    local spin='-\|/'
    local i=0

    tput civis 2>/dev/null || true

    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\rInstalling... %s " "${spin:$i:1}"
        sleep 0.1
    done

    printf "\rInstalling... done ✔\n"
    tput cnorm 2>/dev/null || true
}

# -------------------------
# SYSTEM DEPENDENCIES
# -------------------------
detect_pkg_manager
install_system_dependencies

# -------------------------
# CHECK PYTHON
# -------------------------
if ! have_cmd python3; then
    echo "Python3 is required but not installed."
    exit 1
fi

if ! python3 -m pipx --version >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing pipx...${RESET}"

    run_with_retry python3 -m pip install --user pipx

    python3 -m pipx ensurepath >/dev/null 2>&1 || true
fi

export PATH="$HOME/.local/bin:$PATH"
export PATH="$(python3 -m site --user-base)/bin:$PATH"

# INSTALL CLI
# -------------------------
echo -e "${CYAN}Installing Crafter CLI...${RESET}"

if ! run_with_retry python3 -m pipx install --force git+https://github.com/coderoninsec/crafter-cli.git; then
    echo "Crafter installation failed."
    exit 1
fi

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
    echo -e "${YELLOW}If 'crafter' not found, fix your PATH with:${RESET}"
    echo "  export PATH=\$HOME/.local/bin:\$PATH"
    echo "  python3 -m pipx ensurepath"
    echo "  restart your terminal"
fi
