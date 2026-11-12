"""Regenerates sniper\\03_kit\\campaign from the live campaign, then runs the privacy scan.
Run by /forever step 4 (and again after step 6):  python make_kit.py   (PFE_WS overrides the campaign path)

- Rules (CLAUDE.md, .claude\\commands\\*.md, .claude\\settings.json) are copied with every text value of
  campaign\\00_profile\\personalisation_map.json replaced by {{KEY}}, longest value first, line breaks and
  spaces matched loosely. Then the EXAMPLE blocks of kit_blocks.json are applied; a block whose text is
  not found is an error (the live wording changed: update kit_blocks.json).
- Code is copied byte for byte: it holds no personal fact (build.py and preflight.py read
  personalisation_map.json, build_deck.js reads profile_deck.json).
- VERSION is written from the CLAUDE.md version line.
- /forever and /magic are the author's only (AUTHOR_ONLY): never copied into the kit, and removed from it if
  found, so a received kit holds 9 commands (locked install, 18 Oct 2026).
- MANIFEST.txt lists every package file, so the setup's LOCKDOWN step can tell them from the user's own files.
- Privacy scan over the whole of sniper (text files, docx and pdf text): the private values of the
  map, and any PFE-ID on a line that names a company of the live tracker. Any hit: exit code 1.
  Residue words (organisations and projects of the live campaign) are listed as warnings.
python make_kit.py scan   runs only the privacy scan."""
import os, sys, re, json, shutil, csv, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ZOK = os.path.dirname(HERE)
WS = os.environ.get('PFE_WS') or os.path.join(os.path.dirname(ZOK), 'campaign')
KIT = os.path.join(ZOK, '03_kit', 'campaign')
MAP = json.load(open(os.path.join(WS, '00_profile', 'personalisation_map.json'), encoding='utf-8'))
AUTHOR_ONLY = {'forever.md', 'magic.md'}
TEMPLATED = ['CLAUDE.md', '.claude/settings.json'] + [
    '.claude/commands/' + f for f in sorted(os.listdir(os.path.join(WS, '.claude', 'commands')))
    if f.endswith('.md') and f not in AUTHOR_ONLY]
VERBATIM = ['02_tracker/tracker_tools.py', '02_tracker/unblock_tools.py', '04_outbound/_gen/run34/build.py',
            '00_profile/interview_deck/build_deck.js', '00_profile/interview_deck/package.json',
            'scheduler/gate.py', 'scheduler/preflight.py', 'scheduler/snapshot.py', 'scheduler/platform_env.py']
PRIVATE = ['FULL_NAME', 'GMAIL_ACCOUNT', 'CONTACT_EMAIL', 'PHONE', 'GMAIL_LABEL_ID', 'CHROME_PROFILE', 'LINKEDIN',
           'CONTACT_LINE', 'FILE_STEM', 'USER_HOME', 'MEMORY_KEY']
RESIDUE = MAP.get('_RESIDUE_WORDS', [])   # words of the live campaign that should not reach the kit

def pattern(value):
    """regex for a map value: whitespace runs match any whitespace, letters at the ends are not glued to others"""
    body = r'\s+'.join(re.escape(w) for w in value.split())
    pre = r'(?<![A-Za-z0-9])' if re.match(r'\w', value) else ''
    post = r'(?![A-Za-z0-9])' if re.search(r'\w$', value) else ''
    return re.compile(pre + body + post)

def templatise(text):
    # FORM_* values only fill the hand-written FORM_ANSWERS template; short ones ("no", "Male") must never be templated
    items = sorted(((k, v) for k, v in MAP.items() if not k.startswith(('_', 'FORM_')) and isinstance(v, str) and v.strip()),
                   key=lambda kv: -len(kv[1]))
    for k, v in items:
        text = pattern(v).sub('{{' + k + '}}', text)
    return text

def blocks(rel, text, used):
    for i, b in enumerate(json.load(open(os.path.join(HERE, 'kit_blocks.json'), encoding='utf-8'))['blocks']):
        if b['file'] != rel: continue
        nl = '\r\n' if '\r\n' in text else '\n'          # the rules use CRLF; blocks are written with \n
        rep = b['replace'].replace('\n', nl)
        new, n = re.subn(b['find'].replace('\\n', '\\r?\\n'), lambda m: rep, text)
        if not n: sys.exit(f'block not found in {rel}: {b["find"][:80]!r} (update kit_blocks.json)')
        used.add(i); text = new
    return text

def build():
    used = set()
    for rel in TEMPLATED:
        with open(os.path.join(WS, rel), encoding='utf-8', newline='') as f:
            text = f.read()
        text = blocks(rel, templatise(text), used)
        out = os.path.join(KIT, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    cmds = os.path.join(KIT, '.claude', 'commands')
    for f in os.listdir(cmds):
        if f.endswith('.md') and '.claude/commands/' + f not in TEMPLATED:
            os.remove(os.path.join(cmds, f)); print('  removed from kit:', f)
    for rel in VERBATIM:
        out = os.path.join(KIT, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(os.path.join(WS, rel), out)
    m = re.search(r'^Version (\d+), (\d+ \w+ \d{4})', open(os.path.join(WS, 'CLAUDE.md'), encoding='utf-8').read(), re.M)
    import datetime as dt
    d = dt.datetime.strptime(m.group(2), '%d %B %Y').date()
    with open(os.path.join(ZOK, 'VERSION'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'rules version {m.group(1)}, {d.isoformat()}\n')
    print(f'kit: {len(TEMPLATED) + len(VERBATIM)} files ({len(TEMPLATED)} templated, {len(VERBATIM)} copied); VERSION {m.group(1)} {d}')

def manifest():
    out = []
    for base, dirs, files in os.walk(ZOK):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '__pycache__')]
        out += [os.path.relpath(os.path.join(base, f), ZOK) for f in files if f != 'answers.json']
    with open(os.path.join(ZOK, 'MANIFEST.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(sorted(set(out) | {'MANIFEST.txt'})) + '\n')
    print(f'manifest: {len(out)} files')

def texts():
    """(path, text) for every file in sniper whose text can be read"""
    for base, dirs, files in os.walk(ZOK):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '__pycache__')]
        for f in files:
            p = os.path.join(base, f); ext = os.path.splitext(f)[1].lower()
            try:
                if ext == '.docx':
                    from docx import Document
                    d = Document(p)
                    yield p, '\n'.join([x.text for x in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells])
                elif ext == '.pdf':
                    import pypdf
                    yield p, '\n'.join((pg.extract_text() or '') for pg in pypdf.PdfReader(p).pages)
                elif ext in ('.pptx', '.xlsx', '.png', '.jpg', '.zip'):
                    yield p, ''
                else:
                    yield p, open(p, encoding='utf-8', errors='replace').read()
            except Exception as e:
                print('  cannot read', p, e); yield p, ''

def companies():
    out = set()
    for name in ('tracker.csv', 'blocked.csv', 'screened_out.csv'):
        p = os.path.join(WS, '02_tracker', name)
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding='utf-8-sig')):
                c = (r.get('company') or '').strip()
                if len(c) > 3: out.add(c.lower())
    return out

def scan():
    priv = [(k, MAP[k]) for k in PRIVATE if isinstance(MAP.get(k), str) and MAP[k].strip()]
    pats = [(k, pattern(v)) for k, v in priv] + [(k, re.compile(re.escape(v), re.I)) for k, v in priv if '@' in v]
    comp = companies()
    hits, warn = [], {}
    for p, text in texts():
        rel = os.path.relpath(p, ZOK)
        for k, rx in pats:
            for m in rx.finditer(text):
                hits.append(f'{rel}: {k} "{m.group(0)}"')
        for line in text.split('\n'):
            if re.search(r'PFE-\d{4}', line):
                low = line.lower()
                for c in comp:
                    if re.search(r'(?<![a-z0-9])' + re.escape(c) + r'(?![a-z0-9])', low):
                        hits.append(f'{rel}: PFE-ID with company "{c}": {line.strip()[:100]}'); break
        for w in RESIDUE:
            n = len(re.findall(r'(?<![A-Za-z])' + re.escape(w) + r'(?![A-Za-z])', text))
            if n: warn.setdefault(rel, []).append(f'{w} x{n}')
    for h in sorted(set(hits)): print('  HIT', h)
    for rel, ws in sorted(warn.items()): print('  residue (check it is generic or an EXAMPLE):', rel, ', '.join(ws))
    print(f'privacy hits: {len(set(hits))}')
    return not hits

if __name__ == '__main__':
    if sys.argv[1:] != ['scan']:
        build()
        manifest()
    sys.exit(0 if scan() else 1)
