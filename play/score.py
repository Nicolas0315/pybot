#!/usr/bin/env python3
"""Fixed scoring harness for PyBot Japanese conversation. Do NOT edit between rounds.

usage: python score.py --bot DIR --set dev.json [--out result.json]
Each case: {"id","cat","turns":[user,...],"expect":[regex,...]}  (regex tested on the LAST reply; any match passes)
A case passes iff last reply is Japanese (>=30% of non-space chars are kana/kanji) AND matches an expect regex
(empty expect => only the Japanese check). Deterministic: random.seed(0) before every case.
Also reports ja_rate (replies that are Japanese at all) and failure taxonomy.
"""
import argparse, json, random, re, sys, time, collections

JA = re.compile(r'[぀-ヿ一-鿿]')

def ja_ratio(s):
    chars = [c for c in s if not c.isspace()]
    return sum(1 for c in chars if JA.match(c)) / len(chars) if chars else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bot', required=True); ap.add_argument('--set', required=True); ap.add_argument('--out')
    a = ap.parse_args()
    sys.path.insert(0, a.bot)
    from bot import runtime
    cases = json.load(open(a.set, encoding='utf-8'))
    res, bycat, tax = [], collections.defaultdict(lambda: [0, 0]), collections.Counter()
    ja_n = tot_replies = 0
    for c in cases:
        random.seed(0); mem = {}; reply = ''; module = None; transcript = []
        for t in c['turns']:
            r = runtime.turn(t, mem); reply, module = r['reply'], r['module']
            transcript.append((t, reply, module)); tot_replies += 1
            ja_n += ja_ratio(reply) >= 0.3
        isja = ja_ratio(reply) >= 0.3
        match = (not c.get('expect')) or any(re.search(p, reply) for p in c['expect'])
        ok = isja and match
        why = 'pass' if ok else ('not_japanese' if not isja else 'wrong_content')
        if not ok and reply.strip() in ('Hello!', ''): why = 'fallback_hello'
        tax[why] += 1; bycat[c['cat']][0] += ok; bycat[c['cat']][1] += 1
        res.append({'id': c['id'], 'cat': c['cat'], 'ok': ok, 'why': why, 'transcript': transcript})
    n = len(cases); p = sum(r['ok'] for r in res)
    summ = {'set': a.set, 'n': n, 'pass': p, 'score': round(p / n, 4), 'ja_reply_rate': round(ja_n / tot_replies, 4),
            'taxonomy': dict(tax), 'by_cat': {k: f'{v[0]}/{v[1]}' for k, v in sorted(bycat.items())}, 'ts': time.strftime('%F %T')}
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    if a.out: json.dump({'summary': summ, 'cases': res}, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__': main()
