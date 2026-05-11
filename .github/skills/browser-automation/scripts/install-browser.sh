#!/usr/bin/env bash
#
# Install Playwright Chromium browser for browser automation skill
# Usage: ./install-browser.sh
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }

if ! command -v npx &> /dev/null; then
    warn "npx not found. Install Node.js first."
    exit 1
fi

# Check if Chromium is already installed
playwright_cache="$HOME/.cache/ms-playwright"
if [ -d "$playwright_cache" ] && ls "$playwright_cache"/chromium-* >/dev/null 2>&1; then
    info "Playwright Chromium already installed"
    ls -d "$playwright_cache"/chromium-* | head -1
    exit 0
fi

info "Installing Playwright Chromium browser..."
if npx playwright install chromium; then
    success "Playwright Chromium installed"
    ls -d "$playwright_cache"/chromium-* | head -1
else
    warn "Installation failed. Try: npx playwright install chromium"
    exit 1
fi
