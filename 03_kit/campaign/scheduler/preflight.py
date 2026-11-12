"""Machine check for the things no file can carry. Read-only, no Claude call. Prints one JSON line:
{"ok": bool, "problems": [...]} . The daily chain runs it first and puts problems in the popup.
Connector logins and site logins cannot be checked from here: the runs report those (SESSION EXPIRED,
LOGIN_WALL, connector errors) in their reports."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import platform_env as pe  # noqa: E402  (reads ROOT\.env; works on Windows, Linux and macOS)
with open(os.path.join(HERE, '..', '00_profile', 'personalisation_map.json'), encoding='utf-8') as _f:
    ME = json.load(_f)
PROFILE_DIR = ME['CHROME_PROFILE']           # campaign Chrome profile with the Claude extension
ACCOUNT = ME['GMAIL_ACCOUNT']                  # the account that profile is signed in with
EXT = 'fcoeoabgfenejglbffodgkkbkcdhcgfn'   # Claude in Chrome

def check():
    p = []
    if not pe.claude_path():
        p.append('Claude Code not found (~/.local/bin/claude or on PATH; CLAUDE_PATH in ROOT/.env overrides)')
    for mod in ('docx', 'openpyxl', 'pypdf'):
        try:
            __import__(mod)
        except ImportError:
            p.append(f'Python library missing: {mod} (pip install -r 01_install/requirements.txt)')
    engine = pe.pdf_engine()
    if not engine:
        p.append('No PDF engine: build.py needs Microsoft Word (Windows/macOS, with docx2pdf) or LibreOffice')
    elif engine == 'word':
        try:
            __import__('docx2pdf')
        except ImportError:
            p.append('Python library missing: docx2pdf (PDF_ENGINE=word needs it)')
    if not pe.chrome_path():
        p.append('Chrome not found (CHROME_PATH in ROOT/.env overrides)')
    ud = pe.chrome_user_data()
    try:
        info = json.load(open(os.path.join(ud, 'Local State'), encoding='utf-8'))['profile']['info_cache']
        prof = info.get(PROFILE_DIR)
        if not prof:
            p.append(f'Chrome profile "{PROFILE_DIR}" missing: fix CHROME_PROFILE in 00_profile/personalisation_map.json')
        elif prof.get('user_name') != ACCOUNT:
            p.append(f'Chrome "{PROFILE_DIR}" is signed in as {prof.get("user_name")}, not {ACCOUNT}')
        if not os.path.isdir(os.path.join(ud, PROFILE_DIR, 'Extensions', EXT)):
            p.append(f'Claude in Chrome extension not installed in "{PROFILE_DIR}"')
    except Exception as e:
        p.append(f'cannot read Chrome Local State: {e}')
    return {'ok': not p, 'problems': p}

if __name__ == '__main__':
    print(json.dumps(check()))
