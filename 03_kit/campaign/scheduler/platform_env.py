"""Where the campaign's tools live on this machine (Windows, Linux or macOS), and the .env that overrides them.

The .env file sits in ROOT (the folder that holds campaign\\, interviews\\, my documents\\ and guides\\);
01_install\\.env.example lists every key. load_env() reads the first .env found walking up from a folder,
without overriding a variable already set in the environment. Every key is optional: auto-detection
covers a standard install.

  PYTHON            interpreter for the campaign scripts (default: the one running this file)
  PDF_ENGINE        auto | word | libreoffice   (auto: Word on Windows/macOS when present, else LibreOffice)
  SOFFICE_PATH      LibreOffice soffice binary
  CHROME_PATH       Chrome or Chromium binary (render_guides.py prints the guides with it)
  CHROME_USER_DATA  Chrome user-data folder (preflight.py reads its Local State)

usage: python platform_env.py   prints what was found, as one JSON line."""
import json, os, shutil, subprocess, sys, tempfile

IS_WIN = sys.platform == 'win32'
IS_MAC = sys.platform == 'darwin'
HERE = os.path.dirname(os.path.abspath(__file__))


def load_env(start=HERE, levels=6):
    """Read KEY=VALUE lines of the nearest .env above start into os.environ (existing values win)."""
    d = os.path.abspath(start)
    for _ in range(levels):
        p = os.path.join(d, '.env')
        if os.path.isfile(p):
            with open(p, encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip()
                    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
                        v = v[1:-1]
                    if k and v:
                        os.environ.setdefault(k, os.path.expandvars(os.path.expanduser(v)))
            return p
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


ENV_FILE = load_env()


def _first(env, candidates=(), names=()):
    if os.environ.get(env):
        return os.environ[env]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    for n in names:
        w = shutil.which(n)
        if w:
            return w
    return None


def python_path():
    return os.environ.get('PYTHON') or sys.executable


def claude_path():
    home = os.path.expanduser('~')
    return _first('CLAUDE_PATH', [os.path.join(home, '.local', 'bin', 'claude.exe' if IS_WIN else 'claude')], ['claude'])


def chrome_path():
    pf = [os.environ.get(k, '') for k in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA')]
    return _first('CHROME_PATH',
                  [os.path.join(p, 'Google', 'Chrome', 'Application', 'chrome.exe') for p in pf if p] +
                  ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'],
                  ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome'])


def chrome_user_data():
    if os.environ.get('CHROME_USER_DATA'):
        return os.environ['CHROME_USER_DATA']
    if IS_WIN:
        return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
    if IS_MAC:
        return os.path.expanduser('~/Library/Application Support/Google/Chrome')
    return os.path.expanduser('~/.config/google-chrome')


def word_path():
    if IS_MAC:
        return _first('WORD_PATH', ['/Applications/Microsoft Word.app'])
    if not IS_WIN:
        return None
    pf = [os.environ.get(k, '') for k in ('ProgramFiles', 'ProgramFiles(x86)')]
    return _first('WORD_PATH', [os.path.join(p, 'Microsoft Office', 'root', 'Office16', 'WINWORD.EXE') for p in pf if p],
                  ['winword'])


def soffice_path():
    pf = [os.environ.get(k, '') for k in ('ProgramFiles', 'ProgramFiles(x86)')]
    return _first('SOFFICE_PATH',
                  [os.path.join(p, 'LibreOffice', 'program', 'soffice.exe') for p in pf if p] +
                  ['/Applications/LibreOffice.app/Contents/MacOS/soffice'],
                  ['soffice', 'libreoffice'])


def pdf_engine():
    """'word', 'libreoffice' or None (nothing can make PDFs)."""
    want = os.environ.get('PDF_ENGINE', 'auto').lower()
    if want in ('word', 'libreoffice'):
        return want
    if word_path():
        try:
            import docx2pdf  # noqa: F401
            return 'word'
        except ImportError:
            pass
    return 'libreoffice' if soffice_path() else None


def docx_to_pdf(docx, pdf=None):
    """Convert docx to pdf (default: same name, .pdf) with PDF_ENGINE; returns the pdf path."""
    docx = os.path.abspath(docx)
    pdf = os.path.abspath(pdf or os.path.splitext(docx)[0] + '.pdf')
    engine = pdf_engine()
    if engine == 'word':
        import docx2pdf
        docx2pdf.convert(docx, pdf)
    elif engine == 'libreoffice':
        soffice = soffice_path()
        if not soffice:
            raise RuntimeError('LibreOffice not found: install it or set SOFFICE_PATH in ROOT/.env')
        with tempfile.TemporaryDirectory() as tmp:
            # a private profile, so a LibreOffice window already open does not swallow the job
            profile = 'file:///' + os.path.join(tmp, 'lo_profile').replace('\\', '/').lstrip('/')
            r = subprocess.run([soffice, f'-env:UserInstallation={profile}', '--headless',
                                '--convert-to', 'pdf', '--outdir', tmp, docx],
                               capture_output=True, text=True, timeout=180)
            made = os.path.join(tmp, os.path.splitext(os.path.basename(docx))[0] + '.pdf')
            if not os.path.exists(made):
                raise RuntimeError(f'LibreOffice did not convert {docx}: {r.stderr.strip() or r.stdout.strip()}')
            shutil.move(made, pdf)
    else:
        raise RuntimeError('no PDF engine: install Microsoft Word (Windows/macOS) or LibreOffice, '
                           'or set PDF_ENGINE / SOFFICE_PATH in ROOT/.env')
    return pdf


def summary():
    return {'platform': sys.platform, 'env_file': ENV_FILE, 'python': python_path(), 'claude': claude_path(),
            'chrome': chrome_path(), 'chrome_user_data': chrome_user_data(), 'word': word_path(),
            'soffice': soffice_path(), 'pdf_engine': pdf_engine()}


if __name__ == '__main__':
    print(json.dumps(summary()))
