# Installs the Python libraries of requirements.txt and checks the tools the campaign needs.
# Run by hand:  powershell -ExecutionPolicy Bypass -File .\install.ps1
# It never creates a scheduled task, a service or anything that runs by itself.
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
$problems = @()

if (-not (Test-Path $py)) {
  Write-Host 'Python 3.12 not found. Installing it for this user with winget...'
  winget install --id Python.Python.3.12 -e --scope user --accept-package-agreements --accept-source-agreements
}
if (Test-Path $py) {
  & $py -m pip install --upgrade pip | Out-Null
  & $py -m pip install -r (Join-Path $here 'requirements.txt')
  & $py -c "import docx, openpyxl, docx2pdf, pypdf; print('python libraries ok')"
  if ($LASTEXITCODE -ne 0) { $problems += 'Python libraries did not import' }
} else { $problems += "Python 3.12 missing at $py" }

if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $problems += 'Node.js missing (nodejs.org, LTS): needed for the interview decks' }
if (-not (Test-Path (Join-Path $env:USERPROFILE '.local\bin\claude.exe')) -and -not (Get-Command claude -ErrorAction SilentlyContinue)) {
  $problems += 'Claude Code missing: irm https://claude.ai/install.ps1 | iex'
}
if (-not (Test-Path 'C:\Program Files\Google\Chrome\Application\chrome.exe')) { $problems += 'Google Chrome missing' }
$word = @('C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
          'C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE') | Where-Object { Test-Path $_ }
$soffice = @('C:\Program Files\LibreOffice\program\soffice.exe') | Where-Object { Test-Path $_ }
if (-not $word -and -not $soffice) { $problems += 'No PDF engine: install Microsoft Word or LibreOffice (build.py makes PDFs with one of them)' }

# ROOT\.env: machine settings (never personal data), read by campaign\scheduler\platform_env.py; an existing one is kept
$root = (Resolve-Path (Join-Path $here '..\..')).Path
$envFile = Join-Path $root '.env'
if (-not (Test-Path $envFile)) {
  (Get-Content (Join-Path $here '.env.example')) -replace '^PYTHON=.*', "PYTHON=$py" | Set-Content -Encoding UTF8 $envFile
  Write-Host "wrote $envFile"
} else { Write-Host "kept $envFile" }

# /ask-me (help on a step you are stuck on) works in every folder once it is in your own .claude\commands
$ask = Join-Path $here '..\03_kit\campaign\.claude\commands\ask-me.md'
$cmds = Join-Path $env:USERPROFILE '.claude\commands'
if (Test-Path $ask) { New-Item -ItemType Directory -Force $cmds | Out-Null; Copy-Item $ask $cmds -Force; Write-Host '/ask-me installed' }
else { $problems += "ask-me.md missing at $ask" }

if ($problems) { Write-Host "`nTO FIX:"; $problems | ForEach-Object { Write-Host " - $_" } }
else { Write-Host "`nall checks passed. Next: 00_START_HERE.md step 4 (the setup prompt). Stuck on a step? In Claude Code type /ask-me and paste the step." }
