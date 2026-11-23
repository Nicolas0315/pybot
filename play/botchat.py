#!/usr/bin/env python3
"""Two PyBot instances (separate memories) talk to each other. Logs JSONL transcripts.
usage: python play/botchat.py --turns 30 --openers openers.txt --seeds 0-4 --out chats.jsonl
"""
import argparse, json, random, sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bot import runtime

OPENERS = ["hi, i'm Sam", "how long should i boil an egg", "my kettle is full of limescale", "what's the meaning of life?",
           "I think I'm getting a cold", "こんにちは", "do you like cats?", "I need a holiday"]

def chat(opener, seed, turns):
    random.seed(seed); ma, mb = {}, {}; text = opener; log = []
    for i in range(turns):
        bot, mem = ('B', mb) if i % 2 == 0 else ('A', ma)  # opener is "A" speaking to B
        r = runtime.turn(text, mem); reply = ' '.join(str(r['reply']).split())
        log.append({'i': i, 'from': 'A' if i % 2 == 0 else 'B', 'said': text, 'replied_by': bot, 'reply': reply, 'module': r['module']})
        text = reply
    return log

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--turns', type=int, default=30); ap.add_argument('--seeds', default='0-2')
    ap.add_argument('--out', required=True); ap.add_argument('--loop', action='store_true')
    a = ap.parse_args(); lo, hi = map(int, a.seeds.split('-')); seed0 = lo
    while True:
        with open(a.out, 'a', encoding='utf-8') as f:
            for s in range(lo, hi + 1):
                for o in OPENERS:
                    t = time.time(); log = chat(o, s, a.turns)
                    uniq = len({x['reply'] for x in log}); mods = sorted({x['module'] or 'none' for x in log})
                    f.write(json.dumps({'opener': o, 'seed': s, 'turns': log, 'unique_replies': uniq, 'modules': mods, 'sec': round(time.time() - t, 1)}, ensure_ascii=False) + '\n'); f.flush()
        if not a.loop: break
        lo, hi = hi + 1, hi + (hi - lo + 1)
        time.sleep(30)
if __name__ == '__main__': main()
