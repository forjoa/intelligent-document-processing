#!/usr/bin/env bash
set -euo pipefail

# ── colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}✓${RESET}  $*"; }
fail() { echo -e "${RED}✗${RESET}  $*"; exit 1; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "━━━ Intelligent Document Processing — startup ━━━"
echo ""

# ── 1. Python 3.11+ ───────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    major=${version%%.*}
    minor=${version##*.}
    if [[ "$major" -ge 3 && "$minor" -ge 11 ]]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

[[ -z "$PYTHON" ]] && fail "Python 3.11+ not found. Install it and retry."
ok "Python $($PYTHON --version 2>&1 | awk '{print $2}') found ($PYTHON)"

# ── 2. DATABASE_URL ───────────────────────────────────────────────────────────
if [[ -f ".env" ]]; then
  ok ".env file exists"
fi

if [[ -n "${DATABASE_URL:-}" ]] || { [[ -f ".env" ]] && grep -qE '^\s*DATABASE_URL\s*=' .env; }; then
  ok "DATABASE_URL is defined"
else
  fail "DATABASE_URL is not set. Define it in .env or as an environment variable."
fi

# ── 3. venv ───────────────────────────────────────────────────────────────────
VENV_DIR=".venv"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  if [[ ! -d "$VENV_DIR" ]]; then
    warn "Virtual environment not found — creating $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
    ok "Virtual environment created"
  fi
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  ok "Virtual environment activated"
else
  ok "Virtual environment already active ($VIRTUAL_ENV)"
fi

if [[ -f "requirements.txt" ]]; then
  warn "Installing/updating dependencies from requirements.txt"
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  ok "Dependencies installed"
else
  warn "requirements.txt not found — skipping dependency install"
fi

# ── 4. Tesseract ──────────────────────────────────────────────────────────────
install_tesseract() {
  local os
  os="$(uname -s)"
  if [[ "$os" == "Darwin" ]]; then
    if ! command -v brew &>/dev/null; then
      fail "Homebrew not found. Install it from https://brew.sh and retry."
    fi
    warn "Installing Tesseract via Homebrew…"
    brew install tesseract
  elif [[ "$os" == "Linux" ]]; then
    if command -v apt-get &>/dev/null; then
      warn "Installing Tesseract via apt-get…"
      sudo apt-get update -qq && sudo apt-get install -y -qq tesseract-ocr
    elif command -v dnf &>/dev/null; then
      warn "Installing Tesseract via dnf…"
      sudo dnf install -y tesseract
    elif command -v pacman &>/dev/null; then
      warn "Installing Tesseract via pacman…"
      sudo pacman -Sy --noconfirm tesseract
    else
      fail "Cannot detect package manager. Install tesseract-ocr manually and retry."
    fi
  else
    fail "Unsupported OS: $os. Install tesseract manually and retry."
  fi
}

if command -v tesseract &>/dev/null; then
  ok "Tesseract found ($(tesseract --version 2>&1 | head -1))"
else
  install_tesseract
  command -v tesseract &>/dev/null || fail "Tesseract installation failed."
  ok "Tesseract installed ($(tesseract --version 2>&1 | head -1))"
fi

# ── 5. spaCy model en_core_web_sm ─────────────────────────────────────────────
if python -c "import spacy; spacy.load('en_core_web_sm')" &>/dev/null 2>&1; then
  ok "spaCy model en_core_web_sm is available"
else
  warn "spaCy model en_core_web_sm not found — downloading"
  python -m spacy download en_core_web_sm
  ok "spaCy model en_core_web_sm downloaded"
fi

# ── parse flags ───────────────────────────────────────────────────────────────
RUN_UI=true
for arg in "$@"; do
  [[ "$arg" == "--no-ui" ]] && RUN_UI=false
done

# ── 7. UI dev server ──────────────────────────────────────────────────────────
if [[ "$RUN_UI" == true ]]; then
  if ! command -v node &>/dev/null; then
    fail "Node.js not found. Install it from https://nodejs.org and retry."
  fi
  ok "Node.js found ($(node --version))"

  UI_DIR="$SCRIPT_DIR/ui"

  if [[ ! -d "$UI_DIR/node_modules" ]]; then
    warn "UI dependencies not installed — running npm install"
    npm --prefix "$UI_DIR" install --silent
    ok "UI dependencies installed"
  fi

  npm --prefix "$UI_DIR" run start &
  UI_PID=$!
  ok "UI dev server started (PID $UI_PID) on http://localhost:5173"

  trap 'kill "$UI_PID" 2>/dev/null || true' EXIT
else
  ok "UI skipped (--no-ui)"
fi

# ── 8. Launch ─────────────────────────────────────────────────────────────────
echo ""
echo "━━━ All checks passed — starting server ━━━"
echo ""

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
