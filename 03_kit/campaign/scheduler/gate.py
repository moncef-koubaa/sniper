"""Read-only gate for the daily chain. Prints one JSON line saying which steps have work.
No Claude call, no writes. Usage: python gate.py"""
import calendar, csv, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.join(HERE, '..', '02_tracker')
OUT = os.path.join(HERE, '..', '04_outbound')
sys.path.insert(0, TR)
import tracker_tools as tt  # noqa: E402

def read(name):
    p = os.path.join(TR, name)
    if not os.path.exists(p):
        return []
    with open(p, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def score(r):
    try: return float(r['match_score'])
    except ValueError: return 0.0

def gate(today=None):
    today = today or dt.date.today()
    rows, blocked = tt.load(), read('blocked.csv')
    held = {h['id'] for h in read('holds.csv')}
    live = {r['company_domain'] for r in rows if r['status'] in ('interview', 'offer') and r['company_domain']}
    is_held = lambda r: r['id'] in held or (r['company_domain'] in live and r['status'] not in ('interview', 'offer'))

    discovered = sum(r['status'] == 'discovered' for r in rows)
    # ponytail: text heuristic, a bounce is "open" until a later note mentions a verified/new address
    def bounced(r):
        n = r['notes'].lower()
        b = n.rfind('bounce')
        return b >= 0 and max(n.rfind('verified'), n.rfind('new address')) < b and r['status'] not in ('rejected', 'expired', 'screened_out')
    bounces = sum(bounced(r) for r in rows)

    no_browser = [r for r in blocked if re.search(r'no browser', r['notes'], re.I)
                  and os.path.isdir(os.path.join(OUT, r['id']))]
    queued = [r for r in rows if r['status'] == 'queued']
    enriched = [r for r in rows if r['status'] == 'enriched' and (r['priority'] in ('A', 'B') or score(r) >= 50)]
    targets = [r for r in no_browser + queued + enriched if not is_held(r)]

    last_day = calendar.monthrange(today.year, today.month)[1]
    return {
        'date': today.isoformat(),
        'hunter': discovered < 80,
        'checker': discovered > 0 or bounces > 0,
        'applier': bool(targets),
        'cleanup': today.day == last_day,
        'counts': {'discovered': discovered, 'bounced': bounces, 'applier_targets': len(targets),
                   'blocked_no_browser': len(no_browser), 'queued': len(queued), 'enriched_ok': len(enriched),
                   'held_ids': len(held)},
    }

if __name__ == '__main__':
    if 'test' in sys.argv:
        g = gate(dt.date(2026, 9, 28)); assert not g['cleanup']
        g = gate(dt.date(2026, 9, 30)); assert g['cleanup']
        print('gate self-check ok')
    else:
        print(json.dumps(gate()))
