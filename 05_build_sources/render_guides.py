"""Renders the two guides to PDF with headless Chrome (a temporary profile, never your own).
usage: python render_guides.py [out folder]     default: ..\\04_runbook_and_guides
PFE_MAP=<personalisation_map.json> fills the {{KEY}} placeholders first (a personal copy, e.g. for pfe workflow\\guides).
Without PFE_MAP the paths get a generic example (GENERIC), so the shared copy shows no one's folder."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if sys.argv[1:] else os.path.join(os.path.dirname(HERE), '04_runbook_and_guides')
sys.path.insert(0, os.path.join(os.path.dirname(HERE), '03_kit', 'campaign', 'scheduler'))
import platform_env  # noqa: E402  (Chrome or Chromium on Windows, Linux or macOS; CHROME_PATH in ROOT\.env)
CHROME = platform_env.chrome_path() or sys.exit('Chrome not found: install it or set CHROME_PATH in ROOT/.env')
GENERIC = {'USER_HOME': r'C:\Users\&lt;you&gt;', 'ROOT': r'C:\Users\&lt;you&gt;\Desktop\pfe workflow',
           'WORKSPACE': r'C:\Users\&lt;you&gt;\Desktop\pfe workflow\campaign', 'CAMPAIGN_FILE_STEM': 'PFE2027'}
FILL = json.load(open(os.environ['PFE_MAP'], encoding='utf-8')) if os.environ.get('PFE_MAP') else GENERIC
# the Build Guide is named after the campaign (CAMPAIGN_FILE_STEM); the shared copy stays PFE2027
GUIDES = {'build_guide_source.html': (FILL.get('CAMPAIGN_FILE_STEM') or 'PFE2027') + '_Build_Guide.pdf',
          'friendly_setup_and_usage.html': 'Friendly Setup and Usage.pdf'}

def fill(s):
    return re.sub(r'\{\{([A-Z][A-Z0-9_]*)\}\}',
                  lambda m: FILL[m.group(1)] if isinstance(FILL.get(m.group(1)), str) else m.group(0), s)

with tempfile.TemporaryDirectory() as tmp:
    for src, pdf in GUIDES.items():
        html = os.path.join(tmp, src)
        with open(os.path.join(HERE, src), encoding='utf-8') as f:
            text = f.read()
        with open(html, 'w', encoding='utf-8') as f:
            f.write(fill(text))
        out = os.path.join(OUT, pdf)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', f'--user-data-dir={os.path.join(tmp, "profile")}',
                        '--no-pdf-header-footer', f'--print-to-pdf={out}', Path(html).as_uri()],
                       check=True, capture_output=True, timeout=180)
        print(out, os.path.getsize(out))
