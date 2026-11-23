"""Japanese conversation module. Wins the arbiter whenever the input contains kana/kanji.

Rule-based: normalise the line (NFKC), then try each handler in order; the first that
answers wins. Data lives in bot/knowledge/ja_data.py. State is kept in memory["ja"].
"""
import re
import unicodedata

from ..knowledge import ja_data as D

PRIORITY = 9500
JA_CHARS = re.compile(r"[぀-ヿ一-鿿]")


def has_japanese(text):
    return bool(isinstance(text, str) and JA_CHARS.search(text))


def norm(text):
    t = unicodedata.normalize("NFKC", text).strip()
    return t


def _state(memory):
    st = memory.get("ja")
    if not isinstance(st, dict):
        st = memory["ja"] = {}
    return st


def _pick(options, memory):
    n = len(memory.get("turns") or [])
    return options[n % len(options)]


# ---- handlers --------------------------------------------------------------------------
def h_thanks(t, mem):
    if re.search(D.THANKS, t, re.I) and len(t) < 40:
        return _pick(D.THANKS_REPLIES, mem)


def h_bye(t, mem):
    if len(t) < 30 and re.search(D.BYE, t, re.I):
        for pat, outs in D.BYE_REPLIES:
            if not pat or re.search(pat, t):
                return _pick(outs, mem)


def h_greeting(t, mem):
    if len(t) > 30:
        return None
    for pat, outs in D.GREETINGS:
        if re.search(pat, t, re.I):
            return _pick(outs, mem)


def h_fallback(t, mem):
    return _pick(D.FALLBACK_REPLIES, mem)


HANDLERS = [h_thanks, h_bye, h_greeting, h_fallback]


def observe(text, memory):
    return None


def respond(text, memory):
    if not has_japanese(text):
        return None
    t = norm(text)
    st = _state(memory)
    st["last_input"] = t
    for h in HANDLERS:
        r = h(t, memory)
        if r:
            st["last_handler"] = h.__name__
            return r
    return None
