"""Fills every {{KEY}} placeholder in an installed copy of the kit from your answers file.

usage:  python fill_placeholders.py <answers.json> <root folder>        (fills, then reports what is left)
        python fill_placeholders.py <answers.json> <root folder> --check (reports only, writes nothing)

<root folder> is the folder that holds campaign\\, interviews\\ and "my documents\\" (the copy of 03_kit).
Derived keys are computed when the answers leave them out: WORKSPACE (ROOT\\campaign), MEMORY_KEY (the
Claude Code project key of WORKSPACE), FIRST_NAME, FILE_STEM, USER_HOME, CONTACT_LINE, CAMPAIGN_FILE_STEM
(CAMPAIGN_NAME without spaces: names the runbook and Build Guide files in guides).
The answers are then saved as campaign\\00_profile\\personalisation_map.json: build.py and preflight.py read
it, and /forever uses it to turn your rules back into templates. Keys starting with _ are notes.
Only text that is still a placeholder changes, so running it again on a filled folder changes nothing."""
import json, os, re, sys

TEXT = ('.md', '.py', '.js', '.json', '.toml', '.txt', '.csv', '.html', '.ps1')
PH = re.compile(r'\{\{([A-Z][A-Z0-9_]*)\}\}')

def derive(a):
    a = dict(a)
    a.setdefault('WORKSPACE', os.path.join(a['ROOT'].rstrip('\\/'), 'campaign'))   # \ on Windows, / on Linux/macOS
    a.setdefault('MEMORY_KEY', re.sub(r'[^A-Za-z0-9]', '-', a['WORKSPACE']))
    a.setdefault('FIRST_NAME', a['FULL_NAME'].split()[0])
    a.setdefault('FILE_STEM', '_'.join([a['FULL_NAME'].split()[0], a['FULL_NAME'].split()[-1]]))
    a.setdefault('USER_HOME', os.path.expanduser('~'))
    a.setdefault('CAMPAIGN_FILE_STEM', re.sub(r'[^A-Za-z0-9]', '', a.get('CAMPAIGN_NAME', 'PFE 2027')))
    a.setdefault('CONTACT_LINE', ' | '.join(x for x in (a.get('HOME_CITY'), a.get('PHONE'), a.get('CONTACT_EMAIL'), a.get('LINKEDIN')) if x))
    return a

def files(root):
    for base, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '__pycache__', 'backups', 'sniper', 'archive', '.venv', '.git')]
        for f in fs:
            if f.lower().endswith(TEXT):
                yield os.path.join(base, f)

def fill(text, a, is_json):
    def rep(m):
        v = a.get(m.group(1))
        if not isinstance(v, str):
            return m.group(0)
        return json.dumps(v, ensure_ascii=False)[1:-1] if is_json else v
    return PH.sub(rep, text)

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    a = derive(json.load(open(sys.argv[1], encoding='utf-8')))
    root, check = sys.argv[2], '--check' in sys.argv
    changed, left = 0, {}
    for p in files(root):
        with open(p, encoding='utf-8', newline='') as f:
            t = f.read()
        n = fill(t, a, p.lower().endswith('.json'))
        if n != t and not check:
            with open(p, 'w', encoding='utf-8', newline='') as f:
                f.write(n)
            changed += 1
        for k in PH.findall(n if not check else t):
            if not check or not isinstance(a.get(k), str):
                left.setdefault(k, set()).add(os.path.relpath(p, root))
    if not check:
        mp = os.path.join(root, 'campaign', '00_profile', 'personalisation_map.json')
        if os.path.isdir(os.path.dirname(mp)):
            with open(mp, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(a, f, ensure_ascii=False, indent=1)
            print('wrote', mp)
    print(f'files changed: {changed}')
    for k, ps in sorted(left.items()):
        print(f'  NO VALUE: {{{{{k}}}}} in {", ".join(sorted(ps))}')
    print(f'placeholders left: {len(left)}')
    sys.exit(1 if left else 0)

if __name__ == '__main__':
    main()
