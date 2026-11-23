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


# ---- R2: names and personal facts ----------------------------------------------------------
_END = r"(?:です|でございます|といいます|と言います|と申します|っていいます|って言います|と呼んでください|と呼んで|だよ|だ|といいます)"
_VAL = r"([^\s、。,.!?？！]{1,14}?)"
_ME = D.FIRST_PERSON
_STRIP = re.compile(r"(さん|くん|ちゃん|様)$")


def _clean_value(v):
    return re.sub(r"(です|だよ|だ|ね|よ)$", "", v.strip("「」『』\"' ")).strip()


def _is_nonname(v):
    return (not v) or bool(re.match(D.NOT_A_NAME, v))


def h_name_tell(t, mem):
    st = _state(mem)
    if "?" in t or re.search(r"(何|なに|誰|だれ|覚え|わかる|分かる|知って|言える)", t):
        return None
    m = re.search(r"(?:" + _ME + r")?の?(?:名前|なまえ|お名前)は\s*" + _VAL + _END + r"?[。.!！\s]*$", t)
    explicit = bool(m)
    if not m:
        m = re.search(r"^(?:" + _ME + r"は|" + _ME + r"の名前を)\s*" + _VAL + r"\s*(?:" + _END + r"|といいます)[。.!！\s]*$", t)
    if not m:
        m = re.search(r"^" + _VAL + r"(?:と呼んでください|と呼んで|って呼んで|と呼ばれて)", t)
        explicit = bool(m)
    if not m:
        m = re.search(r"^" + _ME + r"は\s*" + _VAL + r"(?:です|だよ|だ)?[。.!！\s]*$", t)
        if m and re.search(r"(といい|と申|と言|っていい|って言)", t):
            pass
        elif m and not _is_nonname(m.group(1)) and not re.search(r"[がをにへで]", m.group(1)):
            pass
        else:
            m = None
    if not m:
        return None
    name = _STRIP.sub("", _clean_value(m.group(1)))
    if _is_nonname(name) and not explicit:
        return None
    if not name or len(name) > 12:
        return None
    # a topic subject set earlier ("猫を飼っています") owns a bare "名前は X です"
    subj = st.get("subject")
    if subj and re.match(r"^名前は", t) and "私" not in t and "僕" not in t:
        st.setdefault("facts", {})[subj + "の名前"] = name
        return "{}の名前は{}なんですね。素敵な名前です！覚えておきますね。".format(subj, name)
    st["name"] = name
    st.setdefault("facts", {})["名前"] = name
    return _pick(D.NAME_ACK, mem).format(n=name)


def h_name_ask(t, mem):
    st = _state(mem)
    if re.search(D.SECOND_PERSON + r"の?(?:お)?名前|(?:お|ご)名前は|" + D.SECOND_PERSON + r"は(?:何|なん)て(?:呼|名前)|名前(?:は)?何(?:て|と)(?:言|いう)|あなたの呼び名", t):
        return "私はPyBotです。ルールだけで動く、おしゃべりプログラムです。あなたのお名前も教えてくださいね。"
    if re.search(r"(?:" + _ME + r")?の?名前(?:を|は|って|が|、)?\s*(?:覚えて|おぼえて|わかる|分かる|知って|言える|言って|何|なに|なん|だれ|誰|わかります|ですか|でしたっけ|だっけ|[?？]|$)", t) \
            and not re.search(r"(猫|犬|ペット|友達|家族|" + D.PETS + r")の名前", t):
        if st.get("name"):
            return _pick(D.NAME_RECALL, mem).format(n=st["name"])
        return _pick(D.NAME_UNKNOWN, mem)
    if re.search(r"^(?:" + _ME + r"は(?:誰|だれ|どなた)|私が誰)", t):
        if st.get("name"):
            return "{}さんですよね。覚えていますよ。".format(st["name"])
        return _pick(D.NAME_UNKNOWN, mem)


def _owner_key(noun):
    return noun.strip()


def h_fact_ask(t, mem):
    """私のNは？ / 私のNの名前は何？ -> recall facts stored earlier."""
    st = _state(mem)
    facts = st.get("facts", {})
    m = re.search(r"^(?:" + _ME + r")の(.{1,16}?)(?:って|は|を|が)\s*(?:" + D.WH + r"|覚えて|おぼえて|わかる|分かる|知って|言える|でしたっけ|だっけ|ですか|か)?[?？]*$", t)
    if m:
        key = m.group(1)
        key = re.sub(r"(の|って)$", "", key)
        for k, v in facts.items():
            if k == key or k.endswith(key) or key.endswith(k) and len(k) > 1:
                return _pick(D.FACT_RECALL, mem).format(k=k if k.startswith(tuple("私僕")) else "{}".format(k), v=v)
        # "私の猫の名前は" when the pet was stored as the bare kind
        pet = st.get("pets", [])
        if pet and re.search(D.PETS + r"の名前", key):
            return "{}の名前は、まだ聞いていません。教えてもらえますか？".format(re.match(D.PETS, key).group(0))
        return _pick(D.FACT_UNKNOWN, mem).format(k=_ME_less(key))
    m = re.search(r"^(?:" + _ME + r")は(?:何歳|いくつ|何才)", t)
    if m and "年齢" in facts:
        return "{}ですよね。覚えています。".format(facts["年齢"])
    m = re.search(r"^(?:" + _ME + r")は(?:どこ|何処)に住んで", t)
    if m and "住所" in facts:
        return "{}にお住まいなんですよね。".format(facts["住所"])
    m = re.search(r"^(?:" + _ME + r")は(?:何|なに|どんな)(?:が|を)?(?:好き|すき)|私の好きなもの", t)
    if m and st.get("likes"):
        return "{}がお好きなんですよね。覚えています。".format("、".join(st["likes"]))
    m = re.search(r"^(?:" + _ME + r")は(?:何|なに)(?:の仕事|をして|してる)|私の仕事", t)
    if m and "仕事" in facts:
        return "{}のお仕事をされているんですよね。".format(facts["仕事"])


def _ME_less(k):
    return k if k.startswith("あなた") else "あなたの" + k


def h_fact_tell(t, mem):
    st = _state(mem)
    if re.search(r"[?？]$", t) or re.search(D.WH + r"[?？]?$", t):
        return None
    facts = st.setdefault("facts", {})
    # ペットを飼っている
    m = re.search(r"(" + D.PETS + r")を?(?:飼って|飼ってる|飼っています|飼ってます|買ってる|育てて|います|いる)", t)
    if m and re.search(_ME + r"|うち|家で|飼", t):
        kind = m.group(1)
        st.setdefault("pets", []).append(kind)
        st["subject"] = kind
        return "{}を飼っているんですね！いいですね。名前は何ていうんですか？".format(kind)
    # 私のNは Vです
    m = re.search(r"^(?:" + _ME + r")の(" + D.THING_OWNED + r")は\s*" + _VAL + r"(?:" + _END + r")?[。.!！\s]*$", t)
    if m:
        k, v = m.group(1), _clean_value(m.group(2))
        if v and k != "名前":
            facts[k] = v
            return _pick(D.FACT_ACK, mem).format(x="{}は{}".format(k, v))
    m = re.search(r"^(?:" + _ME + r"の)?(" + D.THING_OWNED + r")は\s*" + _VAL + r"(?:" + _END + r")?[。.!！\s]*$", t)
    if m and m.group(1) not in ("名前",) and m.group(1) != "年":
        k, v = m.group(1), _clean_value(m.group(2))
        if v:
            facts[k] = v
            return _pick(D.FACT_ACK, mem).format(x="{}は{}".format(k, v))
    # N の名前は V (「猫の名前はミケです」)
    m = re.search(r"^(?:" + _ME + r"の)?(" + D.PETS + r"|友達|友だち|家族|彼女|彼氏|子供|息子|娘|兄|姉|弟|妹|母|父)の名前は\s*" + _VAL + r"(?:" + _END + r")?[。.!！\s]*$", t)
    if m:
        k, v = m.group(1) + "の名前", _clean_value(m.group(2))
        facts[k] = v
        st["subject"] = m.group(1)
        return "{}の名前は{}なんですね。覚えました！".format(m.group(1), v)
    m = re.search(r"(\d{1,3})(?:歳|才|さい)(?:です|だ|だよ)?", t)
    if m and re.search(_ME + r"|^\d", t):
        facts["年齢"] = m.group(1) + "歳"
        return "{}歳なんですね。覚えておきます。".format(m.group(1))
    m = re.search(r"^(?:" + _ME + r"は|今は|現在は)?([^\s、。は]{1,8}?)に住んで", t)
    if m:
        facts["住所"] = m.group(1)
        return "{}にお住まいなんですね。いいところですか？".format(m.group(1))
    m = re.search(_ME + r"?は([^\s、。]{1,10}?)が(?:大)?好き(?:です|だ|なんです|なの|だよ)", t)
    if m:
        likes = st.setdefault("likes", [])
        if m.group(1) not in likes:
            likes.append(m.group(1))
        return "{}がお好きなんですね。覚えておきます！".format(m.group(1))
    m = re.search(r"([^\s、。]{1,10}?)(?:の仕事|として働い|で働い|をしてい)", t)
    if m and re.search(_ME + r"|仕事", t):
        facts["仕事"] = m.group(1)
        return "{}のお仕事なんですね。大変なこともありますか？".format(m.group(1))


HANDLERS = [h_thanks, h_bye, h_name_ask, h_name_tell, h_fact_ask, h_fact_tell, h_greeting, h_fallback]


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
