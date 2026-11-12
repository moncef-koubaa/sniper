"""Mirror the campaign data into a destination folder (a spare copy you choose).
Workspace: the folder above this script (campaign)  ->  dest, given on the command line.
Since 18 Oct 2026 (v19) there is no default destination: the older snapshot is frozen in
..\\archive\\data snapshot and is never written again.
Copies new or changed files, deletes files that no longer exist in the workspace. Read-only on the workspace.
Skipped: 02_tracker\\backups (thousands of copies; tracker_tools recreates it), caches, temp files, the lock.
Run by hand only. Usage: python snapshot.py <dest> [workspace];  python snapshot.py test"""
import os, shutil, sys, json, datetime as dt

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SKIP_DIRS = {'backups', '__pycache__', '_to_delete', '.git'}
SKIP_FILES = {'.running'}

def skip(name):
    return name in SKIP_FILES or name.endswith('.tmp') or name.startswith('~$') or name.startswith('.tracker_')

def mirror(ws, dest):
    copied = deleted = 0
    seen = set()
    for base, dirs, files in os.walk(ws):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(base, ws)
        out = os.path.normpath(os.path.join(dest, rel))
        os.makedirs(out, exist_ok=True)
        seen.add(out)
        for f in files:
            if skip(f):
                continue
            src, dst = os.path.join(base, f), os.path.join(out, f)
            seen.add(dst)
            s = os.stat(src)
            if os.path.exists(dst):
                d = os.stat(dst)
                if d.st_size == s.st_size and int(d.st_mtime) == int(s.st_mtime):
                    continue
            try:
                shutil.copy2(src, dst); copied += 1
            except PermissionError:
                pass                                    # locked by OneDrive/Excel: next run copies it
    for base, dirs, files in os.walk(dest, topdown=False):
        for f in files:
            p = os.path.join(base, f)
            if p not in seen and os.path.basename(p) != 'SNAPSHOT.json':
                os.remove(p); deleted += 1
        if base != dest and os.path.normpath(base) not in seen and not os.listdir(base):
            os.rmdir(base)
    info = {'taken': dt.datetime.now().isoformat(timespec='seconds'), 'workspace': ws,
            'copied': copied, 'deleted': deleted}
    with open(os.path.join(dest, 'SNAPSHOT.json'), 'w', encoding='utf-8') as fh:
        json.dump(info, fh, indent=1)
    return info

if __name__ == '__main__':
    if sys.argv[1:] == ['test']:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            ws, de = os.path.join(t, 'ws'), os.path.join(t, 'de')
            os.makedirs(os.path.join(ws, '02_tracker', 'backups'))
            open(os.path.join(ws, 'a.txt'), 'w').write('1')
            open(os.path.join(ws, '02_tracker', 'backups', 'b.csv'), 'w').write('x')
            open(os.path.join(ws, '02_tracker', '.tracker_x.tmp'), 'w').write('x')
            assert mirror(ws, de)['copied'] == 1
            assert os.path.exists(os.path.join(de, 'a.txt'))
            assert not os.path.exists(os.path.join(de, '02_tracker', 'backups'))
            os.remove(os.path.join(ws, 'a.txt'))
            assert mirror(ws, de)['deleted'] == 1
        print('snapshot self-check ok')
    else:
        if not sys.argv[1:]:
            sys.exit('usage: python snapshot.py <dest> [workspace]')
        print(json.dumps(mirror(sys.argv[2] if sys.argv[2:] else WS, sys.argv[1])))
