# 01_install

What the campaign needs on the PC, with the versions it was tested with on 18 October 2026. It runs on
Windows 10/11, Linux or macOS.

| Tool | Tested version | How to get it |
|---|---|---|
| Claude Code | 2.1.302 | Windows: `irm https://claude.ai/install.ps1 \| iex`; Linux/macOS: `curl -fsSL https://claude.ai/install.sh \| bash`; then `claude` and `/login` |
| Python | 3.12.10 (3.10 or newer) | Windows: per user (`%LOCALAPPDATA%\Programs\Python\Python312\python.exe`), python.org or install.ps1 (winget). Linux/macOS: the system python3; install.sh makes a venv in `<ROOT>/.venv` |
| Python libraries | python-docx 1.2.0, openpyxl 3.1.5, pypdf 6.19.0, docx2pdf 0.1.8 (Windows/macOS only) | `requirements.txt` (the install script installs them) |
| Node.js | 24.21.0 (npm 11.19.0) | nodejs.org, LTS |
| Node package | pptxgenjs 3.12.0 (`package.json`, same as campaign\00_profile\interview_deck) | the setup runs `npm install` there |
| PDF engine | Microsoft 365 Word 16.0, or LibreOffice 24+ | Word: open it once after installing. LibreOffice: libreoffice.org or `apt install libreoffice`; on Linux also `fonts-crosextra-carlito` (Calibri metrics, so the CV stays on one page) |
| Google Chrome | 155 | google.com/chrome |
| Claude in Chrome extension | current | Chrome Web Store; site access "On all sites", permission mode "Act without asking" |
| claude.ai connectors | Gmail, Google Drive, Google Calendar, Indeed | claude.ai, Settings, Connectors |

Run the install script in this folder:
- Windows: `powershell -ExecutionPolicy Bypass -File .\install.ps1`
- Linux, macOS: `bash install.sh` (never uses sudo: it prints the apt/dnf/brew line for anything missing)

It installs the Python libraries, lists anything missing, and writes `<ROOT>\.env` (ROOT is the folder that
holds sniper) from `.env.example` if there is none. It also copies the /ask-me command (help on a step you
are stuck on) into `~/.claude/commands`, so it works in every folder. It schedules nothing.

## .env

`<ROOT>\.env` holds machine settings only, never personal data: PYTHON, PDF_ENGINE (auto, word or
libreoffice), SOFFICE_PATH, CHROME_PATH, CHROME_USER_DATA, CLAUDE_PATH. Every key is optional; empty means
auto-detect. `python campaign/scheduler/platform_env.py` (before the setup:
`sniper/03_kit/campaign/scheduler/platform_env.py`) prints what this machine has.
