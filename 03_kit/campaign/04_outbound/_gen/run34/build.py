"""run33 builder: tailored CV from CV_MASTER_V2.docx + letter docx/pdf + email.md + notes.md.
usage: python3 build.py PFE-0498 [PFE-....]
Personal values (name, contact line, file-name stem, instruments, approved courses) come from
00_profile\\personalisation_map.json (since 18 Oct 2026, v19): the same code runs in every campaign."""
import sys, os, json, copy, re, subprocess
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MASTER = os.path.join(ROOT, '03_documents', 'CV_MASTER_V2.docx')
OUT = os.path.join(ROOT, '04_outbound')
SPECS = os.path.join(os.path.dirname(__file__), 'specs')
with open(os.path.join(ROOT, '00_profile', 'personalisation_map.json'), encoding='utf-8') as _f:
    ME = json.load(_f)
NAME = ME['FULL_NAME']
STEM = ME['FILE_STEM']
CONTACT = ME['CONTACT_LINE']
import datetime as _dt
DATE = f'{_dt.date.today().day} {_dt.date.today():%B %Y}'  # today, English; a spec 'date' overrides it
MASTER_INSTR = ME['INSTRUMENTS']
BANNED = ['passion','cutting-edge','world-class','dream','thrilled','delighted','journey','leverage','synergy','writing to express my interest','—']
COURSE_OK = set(ME['COURSES'])

def move_block(body, anchor, block):
    for el in block:
        anchor.addnext(el); anchor = el
    return anchor

def build_cv(sid, cv, stem):
    d = Document(MASTER); P = d.paragraphs
    assert P[3].text.startswith('Final-year') and P[5].text.startswith('Instruments') and P[38].text.startswith('Selected coursework')
    P[3].runs[0].text = cv['summary']
    instr = cv.get('instruments', MASTER_INSTR)
    assert sorted(instr) == sorted(MASTER_INSTR), 'instrument set changed'
    P[5].runs[1].text = ' ' + ', '.join(instr)
    cw = [c.strip() for c in cv['coursework'].split(',')] if isinstance(cv['coursework'], str) else cv['coursework']
    for c in cw: assert c in COURSE_OK, c
    P[38].runs[1].text = ' ' + ', '.join(cw)
    exp = [P[10:14], P[14:18], P[18:21]]
    res = [P[22:27], P[27:32], P[32:35]]
    eo = cv.get('exp_order', [0,1,2]); ro = cv.get('proj_order', [0,1,2])
    anchor = P[9]._p
    for i in eo: anchor = move_block(None, anchor, [p._p for p in exp[i]])
    anchor = P[21]._p
    for i in ro: anchor = move_block(None, anchor, [p._p for p in res[i]])
    path = os.path.join(stem, f'CV_{STEM}_{sid}_v1.docx'); d.save(path); return path

def build_letter(sid, L, stem):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = 7560310, 10692130
    s.top_margin = s.bottom_margin = Pt(51); s.left_margin = s.right_margin = Pt(62.35)
    st = d.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5); st.paragraph_format.space_after = Pt(6)
    p = d.add_paragraph(); p.paragraph_format.space_after = Pt(0); r = p.add_run(NAME); r.bold = True; r.font.size = Pt(13)
    d.add_paragraph(CONTACT)
    p = d.add_paragraph(DATE); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for line in L['to']:
        p = d.add_paragraph(line); p.paragraph_format.space_after = Pt(0)
    d.add_paragraph()
    p = d.add_paragraph(); r = p.add_run(L.get('subject_label','Subject: ') + L['subject']); r.bold = True
    for t in [L['salutation']] + L['paras'] + [L.get('close', 'Kind regards,')]:
        p = d.add_paragraph(t); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    d.add_paragraph(NAME)
    path = os.path.join(stem, f'Letter_{STEM}_{sid}_v1.docx'); d.save(path)
    with open(os.path.join(stem, 'letter.txt'), 'w') as f:
        f.write('\n'.join(L['to']) + '\n\n' + L.get('subject_label','Subject: ') + L['subject'] + '\n\n' + '\n\n'.join([L['salutation']] + L['paras'] + [L.get('close','Kind regards,'), NAME]) + '\n')
    return path

def words(txt): return len(re.findall(r"\S+", txt))

def check_text(label, txt, limit):
    low = txt.lower()
    bad = [b for b in BANNED if b in low]
    n = words(txt)
    return f'{label}: {n}/{limit} words' + (f' BANNED {bad}' if bad else '') + (' OVER' if n > limit else '')

def pdf(path, stem):
    subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',stem,path], capture_output=True, timeout=120)
    pp = path[:-5] + '.pdf'
    out = subprocess.run(['pdfinfo', pp], capture_output=True, text=True).stdout
    return int(re.search(r'Pages:\s+(\d+)', out).group(1))

def main(ids):
    for sid in ids:
        spec = json.load(open(os.path.join(SPECS, sid + '.json')))
        num = sid.split('-')[1]
        stem = os.path.join(OUT, sid); os.makedirs(stem, exist_ok=True)
        rep = [sid]
        cvp = build_cv(num, spec['cv'], stem); rep.append(f'CV pages={pdf(cvp, stem)}')
        L = spec['letter']
        lp = build_letter(num, L, stem); rep.append(f'Letter pages={pdf(lp, stem)}')
        body = '\n\n'.join(L['paras'])
        rep.append(check_text('letter', L['salutation'] + ' ' + body, 400))
        if spec.get('email'):
            E = spec['email']
            txt = f"To: {E['to']}\nSubject: {E['subject']}\n\n{E['body']}\n"
            open(os.path.join(stem, 'email.md'), 'w').write(txt)
            sig = E['body'].split('Kind regards,')[0]
            rep.append(check_text('email', sig, 180))
        open(os.path.join(stem, 'notes.md'), 'w').write(f"# {sid} run34 applier (2026-09-27)\n\nSite read this run (source of the organisation-specific sentence):\n{spec.get('source','')}\n\nCV: CV_{STEM}_{num}_v1 from CV_MASTER_V2 (summary, order, coursework and instrument order changed; no fact changed). Letter: Letter_{STEM}_{num}_v1.\n")
        print(' | '.join(rep))

# ---- run34 overrides: PDF through Word or LibreOffice (scheduler\platform_env.py, PDF_ENGINE in ROOT\.env),
# pypdf for page count, utf-8 files, per-spec date/language
import pypdf, builtins
sys.path.insert(0, os.path.join(ROOT, 'scheduler'))
import platform_env
_open = builtins.open
def open(f, mode='r', *a, **k):
    if 'b' not in mode and 'encoding' not in k: k['encoding'] = 'utf-8'
    return _open(f, mode, *a, **k)
def pdf(path, stem):
    pp = platform_env.docx_to_pdf(path, path[:-5] + '.pdf')
    return len(pypdf.PdfReader(pp).pages)
_bl = build_letter
def build_letter(sid, L, stem):
    global DATE
    old = DATE; DATE = L.get('date', DATE)
    try: return _bl(sid, L, stem)
    finally: DATE = old
BANNED += ['passionné','passion','rêve','ravi']
if __name__ == '__main__':
    main(sys.argv[1:])
