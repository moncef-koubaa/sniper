#!/usr/bin/env bash
# Linux / macOS twin of install.ps1: creates ROOT/.venv with the Python libraries of requirements.txt,
# writes ROOT/.env from .env.example (if missing) and checks the tools the campaign needs.
# Run by hand:  bash install.sh
# It never uses sudo and never creates a cron job, a service or anything that runs by itself:
# a missing system tool is listed under TO FIX with the command to install it.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"          # the folder that holds sniper
venv="$root/.venv"
problems=()

# install hint for the system package manager
if command -v apt-get >/dev/null; then pkg='sudo apt-get install -y'
elif command -v dnf >/dev/null; then pkg='sudo dnf install -y'
elif command -v pacman >/dev/null; then pkg='sudo pacman -S'
elif command -v brew >/dev/null; then pkg='brew install'
else pkg='<your package manager> install'; fi

py=''
for c in python3.12 python3.13 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then py="$c"; break; fi
done
if [ -z "$py" ]; then
  problems+=("Python 3.10 or newer missing: $pkg python3 python3-venv")
else
  if [ ! -x "$venv/bin/python" ]; then
    echo "Creating $venv with $py ..."
    "$py" -m venv "$venv" || problems+=("could not create the venv: $pkg python3-venv")
  fi
  if [ -x "$venv/bin/python" ]; then
    "$venv/bin/python" -m pip install --upgrade pip >/dev/null
    "$venv/bin/python" -m pip install -r "$here/requirements.txt"
    "$venv/bin/python" -c "import docx, openpyxl, pypdf; print('python libraries ok')" \
      || problems+=('Python libraries did not import')
  fi
fi

# ROOT/.env: machine settings (never personal data); an existing one is kept as it is
if [ ! -f "$root/.env" ]; then
  sed "s|^PYTHON=.*|PYTHON=$venv/bin/python|" "$here/.env.example" > "$root/.env"
  echo "wrote $root/.env"
else
  echo "kept $root/.env"
fi

command -v node >/dev/null || problems+=("Node.js missing (nodejs.org, LTS, or $pkg nodejs npm): needed for the interview decks")
if [ ! -x "$HOME/.local/bin/claude" ] && ! command -v claude >/dev/null; then
  problems+=('Claude Code missing: curl -fsSL https://claude.ai/install.sh | bash')
fi
if ! command -v google-chrome >/dev/null && ! command -v google-chrome-stable >/dev/null \
   && [ ! -d '/Applications/Google Chrome.app' ]; then
  problems+=('Google Chrome missing (google.com/chrome): the Claude in Chrome extension needs Chrome itself')
fi
if ! command -v soffice >/dev/null && ! command -v libreoffice >/dev/null \
   && [ ! -d '/Applications/LibreOffice.app' ] && [ ! -d '/Applications/Microsoft Word.app' ]; then
  problems+=("LibreOffice missing (build.py makes PDFs with it): $pkg libreoffice")
fi
# the CV and letters are set in Calibri; Carlito has the same metrics, so pages break as in Word
if command -v fc-list >/dev/null && ! fc-list | grep -qiE 'calibri|carlito'; then
  problems+=("Calibri-compatible font missing (one-page CV may overflow): $pkg fonts-crosextra-carlito")
fi

# /ask-me (help on a step you are stuck on) works in every folder once it is in your own ~/.claude/commands
ask="$here/../03_kit/campaign/.claude/commands/ask-me.md"
if [ -f "$ask" ]; then mkdir -p "$HOME/.claude/commands" && cp -f "$ask" "$HOME/.claude/commands/" && echo '/ask-me installed'
else problems+=("ask-me.md missing at $ask"); fi

if [ ${#problems[@]} -gt 0 ]; then
  echo; echo 'TO FIX:'; for p in "${problems[@]}"; do echo " - $p"; done; exit 1
fi
echo; echo 'all checks passed. Next: 00_START_HERE.md step 4 (the setup prompt). Stuck on a step? In Claude Code type /ask-me and paste the step.'
