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
    m = re.search(r"^(?:" + _ME + r")の(" + D.PETS + r")は\s*" + _VAL + r"(?:" + _END + r")?[。.!！\s]*$", t)
    if m and not re.search(r"(何|どう|どこ)", t):
        kind, nm = m.group(1), _clean_value(m.group(2))
        facts[kind + "の名前"] = nm
        st["subject"] = kind
        return "{}の名前は{}なんですね。覚えました！".format(kind, nm)
    m = re.search(r"^(" + _VAL + r")という名前(?:です|だ|だよ)", t)
    if m and st.get("subject"):
        facts[st["subject"] + "の名前"] = m.group(2).strip()
        return "{}の名前は{}なんですね。覚えました！".format(st["subject"], m.group(2).strip())
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
    m = re.search(r"^(?:(?:" + _ME + r")は)?([^\s、。は]{1,10}?)が(?:大)?好き(?:です|だ|なんです|なの|だよ|$|[。!！])", t)
    if m:
        likes = st.setdefault("likes", [])
        if m.group(1) not in likes:
            likes.append(m.group(1))
        return "{}がお好きなんですね。覚えておきます！".format(m.group(1))
    m = re.search(r"([^\s、。]{1,10}?)(?:の仕事|として働い|で働い|をしてい)", t)
    if m and re.search(_ME + r"|仕事", t):
        facts["仕事"] = m.group(1)
        return "{}のお仕事なんですね。大変なこともありますか？".format(m.group(1))


# ---- R3: arithmetic and facts ---------------------------------------------------------------
_KD = D.NUM_WORDS
_KU = {"十": 10, "百": 100, "千": 1000}
_KB = {"万": 10000, "億": 100000000}
_KANJI_RUN = re.compile(r"[零〇一二三四五六七八九十百千万億]+")


def kansuji(s):
    """Kanji numeral -> int (二十三, 百二十, 三万五千, 一二三). None when not a numeral."""
    if not s:
        return None
    if all(c in _KD for c in s):
        return int("".join(str(_KD[c]) for c in s))
    total, block, cur = 0, 0, None
    for c in s:
        if c in _KD:
            cur = _KD[c]
        elif c in _KU:
            block += (cur if cur is not None else 1) * _KU[c]
            cur = None
        elif c in _KB:
            block += cur or 0
            total += (block or 1) * _KB[c]
            block, cur = 0, None
        else:
            return None
    return total + block + (cur or 0)


def to_arabic(t):
    return _KANJI_RUN.sub(lambda m: str(kansuji(m.group(0))) if kansuji(m.group(0)) is not None else m.group(0), t)


def _fmt(x):
    from fractions import Fraction
    x = Fraction(x).limit_denominator(10**6)
    if x.denominator == 1:
        return "{:,}".format(x.numerator) if abs(x.numerator) >= 10000 else str(x.numerator)
    f = float(x)
    return ("%.4f" % f).rstrip("0").rstrip(".")


_N = r"(-?\d+(?:\.\d+)?)"
_OPS = [
    (r"(?:たす|足す|足して|プラス|\+|加えると|を足)", lambda a, b: a + b, "{a}たす{b}"),
    (r"(?:ひく|引く|引いて|マイナス|-|－|を引)", lambda a, b: a - b, "{a}引く{b}"),
    (r"(?:かける|掛ける|掛けて|かけて|×|\*|x|X|をかけ|を掛け)", lambda a, b: a * b, "{a}かける{b}"),
    (r"(?:わる|割る|割って|÷|/|で割)", lambda a, b: a / b, "{a}割る{b}"),
]


def h_math(t, mem):
    from fractions import Fraction
    tt = to_arabic(t)
    tt = re.sub(r"(\d),(\d{3})", r"\1\2", tt)
    if not re.search(r"\d", tt):
        return None
    # power / root / percent / half / times first
    m = re.search(_N + r"の" + _N + r"乗", tt)
    if m:
        a, b = Fraction(m.group(1)), Fraction(m.group(2))
        if b.denominator == 1 and 0 <= b <= 64:
            return "{}の{}乗は{}です。".format(m.group(1), m.group(2), _fmt(a ** int(b)))
    m = re.search(_N + r"の(?:2乗|二乗)", tt) or re.search(_N + r"を(?:2乗|二乗)", tt)
    m3 = re.search(_N + r"の(?:平方根|ルート)|(?:√|ルート)\s*" + _N, tt)
    if m3:
        import math
        v = float(m3.group(1) or m3.group(2))
        r = math.sqrt(v) if v >= 0 else None
        if r is not None:
            return "{}の平方根は{}です。".format(_fmt(Fraction(v)), _fmt(Fraction(r)) if r == int(r) else "約" + ("%.4f" % r).rstrip("0"))
    m = re.search(_N + r"(?:円|個|人|kg|キロ|m|メートル|ページ|本|枚|台)?の\s*" + _N + r"\s*(?:%|パーセント|割)", tt)
    if m:
        a, p = Fraction(m.group(1)), Fraction(m.group(2))
        pct = p * 10 if "割" in tt[m.end() - 2:m.end()] else p
        return "{}の{}%は{}です。".format(m.group(1), _fmt(pct), _fmt(a * pct / 100))
    m = re.search(_N + r"[^\d]{0,3}の(?:半分|半額)", tt)
    if m:
        return "{}の半分は{}です。".format(m.group(1), _fmt(Fraction(m.group(1)) / 2))
    m = re.search(_N + r"[^\d]{0,3}の(\d+(?:\.\d+)?)倍", tt)
    if m:
        return "{}の{}倍は{}です。".format(m.group(1), m.group(2), _fmt(Fraction(m.group(1)) * Fraction(m.group(2))))
    # unit conversion: "2時間は何分" / "5キロは何メートル"
    m = re.search(_N + r"\s*([^\d\sはが]{1,8}?)(?:は|って|を)?(?:何|なに|いくつ)\s*([^\d\s？?です]{1,8}?)(?:ですか|です|になる|か|\?|？|$)", tt)
    if m:
        for fr, to, fac, fl, tl in D.UNIT_CONV:
            if re.fullmatch(fr, m.group(2)) and re.fullmatch(to, m.group(3)):
                return "{}{}は{}{}です。".format(m.group(1), fl, _fmt(Fraction(m.group(1)) * fac), tl)
    # binary operators in natural or symbolic form
    pure = not re.sub(r"[0-9.,+\-－×÷*/xX=＝?？!！。\s]|は|って|いくつ|答え|計算|です|か|の|を|いくら|何|なに|になる|は？", "", tt)
    for pat, fn, label in _OPS:
        m = re.search(_N + r"\s*(?:を)?" + pat + r"\s*" + _N, tt)
        if m and not pure and re.fullmatch(r"[+\-－×÷*/xX]", m.group(0)[len(m.group(1)):-len(m.group(2))].strip() or "?"):
            m = None
        if m:
            a, b = Fraction(m.group(1)), Fraction(m.group(2))
            if label.endswith("割る{b}") and b == 0:
                return "0で割ることはできません。"
            r = fn(a, b)
            if isinstance(r, Fraction) or True:
                return "{}は{}です。".format(label.format(a=m.group(1), b=m.group(2)), _fmt(r))
    return None


def _pref(k):
    return k if k == "北海道" else k + {"東京": "都", "京都": "府", "大阪": "府"}.get(k, "県")


def _entity_in(t, table):
    best = None
    for k in table:
        if k in t and (best is None or len(k) > len(best)):
            best = k
    return best


def h_fact(t, mem):
    st = _state(mem)
    m = re.search(r"(東京|大阪|京都|横浜|名古屋|札幌|福岡|神戸|仙台|広島|沖縄|北海道)(都|府|県|市)?の人口", t)
    if m:
        pop = {"東京": "約1400万人（東京都）", "大阪": "約275万人（大阪市）", "京都": "約140万人（京都市）", "横浜": "約375万人",
               "名古屋": "約230万人", "札幌": "約197万人", "福岡": "約163万人", "神戸": "約150万人", "仙台": "約110万人",
               "広島": "約120万人", "沖縄": "約145万人", "北海道": "約510万人"}
        return "{}の人口は、{}です（おおよその数字です）。".format(m.group(1), pop[m.group(1)])
    tt = to_arabic(t) if re.search(r"[0-9]", t) is None and False else t
    # capitals
    if re.search(r"首都|県庁|州都", t):
        if re.search(r"県庁|府庁|道庁|都庁", t) or _entity_in(t, D.PREF_CAPITALS) and not _entity_in(t, D.CAPITALS):
            k = _entity_in(t, D.PREF_CAPITALS)
            if k and re.search(r"県庁所在地|県庁|都庁|府庁|道庁", t):
                return "{}の県庁所在地は{}です。".format(_pref(k), D.PREF_CAPITALS[k])
        k = _entity_in(t, D.CAPITALS)
        if k:
            _set_topic(mem, "capital", "fact")
            return "{}の首都は{}です。".format(k, D.CAPITALS[k])
    m = re.search(r"(北海道|[^\s、。]{1,3}[県府都]|[^\s、。]{1,3})の県庁所在地|県庁所在地は", t)
    if m:
        k = _entity_in(t, D.PREF_CAPITALS)
        if k:
            return "{}の県庁所在地は{}です。".format(k, D.PREF_CAPITALS[k])
    for pat, ans in D.FACTS:
        if re.search(pat, t):
            return D.YEAR_ANSWER if ans == "ONEYEAR" else ans


def h_datetime(t, mem):
    import datetime
    now = datetime.datetime.now()
    wd = "月火水木金土日"[now.weekday()]
    if re.search(r"今日.*(何日|なんにち|日付|何月|いつ)|今日の日付|今日は何日", t):
        return "今日は{}年{}月{}日（{}曜日）です。".format(now.year, now.month, now.day, wd)
    if re.search(r"今日.*(何曜日|なんようび)|何曜日", t):
        return "今日は{}曜日です。".format(wd)
    if re.search(r"(今|いま).*(何時|なんじ)|今何時|時刻", t):
        return "いまは{}時{}分ごろです。".format(now.hour, now.minute)


# ---- R4: advice (cooking / home / health / travel) -------------------------------------------
from ..knowledge import ja_advice as A

_PLACES = ["東京", "大阪", "京都", "名古屋", "新大阪", "博多", "福岡", "広島", "仙台", "札幌", "函館", "金沢", "新潟", "長野", "沖縄", "那覇",
           "横浜", "鎌倉", "箱根", "日光", "奈良", "神戸"]
_TRAVELISH = r"旅行|観光|旅|行き|行く|行って|行こう|スポット|見どころ|見所|名所|おすすめ|オススメ|お勧め|遊び|デート|何がある|見る|食べ|ツアー|泊"
_HEALTH_ASK = r"どうしたら|どうすれば|どうすれ|治したい|治す|治る|対処|対策|予防|改善|楽になる|いい(ですか|かな|？|\?)|効く|痛い|つらい|辛い"


def h_transit(t, mem):
    if not re.search(r"かか(る|ります)|所要|何時間|何分|どのくらい|どれくらい|どれぐらい|距離|遠い|時間", t):
        return None
    hits = []
    for p in _PLACES:
        i = t.find(p)
        if i >= 0:
            hits.append((i, p))
    hits.sort()
    names = []
    for _, p in hits:
        if p not in names:
            names.append(p)
    if len(names) >= 2:
        for a in names:
            for b in names:
                if a != b and frozenset((a, b)) in A.TRANSIT:
                    st = _state(mem)
                    st["topic"] = "transit"
                    return "{}から{}までは、{}".format(names[0], names[1], A.TRANSIT[frozenset((a, b))])
        return "{}から{}までの正確な時間は分かりませんが、新幹線や飛行機を使うのが一般的です。乗換案内アプリで調べると確実です。".format(names[0], names[1])


def _set_topic(mem, tid, kind):
    st = _state(mem)
    st["topic"] = tid
    st["topic_kind"] = kind
    st["topic_turn"] = len(mem.get("turns") or [])


def _first(table, t):
    for tid, pat, reply in table:
        if re.search(pat, t):
            return tid, reply
    return None


def h_advice(t, mem):
    for kind, table in (("cooking", A.COOKING), ("home", A.HOME)):
        hit = _first(table, t)
        if hit:
            _set_topic(mem, hit[0], kind)
            return hit[1]
    hit = _first(A.HEALTH, t)
    if hit:
        _set_topic(mem, hit[0], "health")
        return hit[1]
    return None


_OVERSEAS = r"海外|外国|ハワイ|ソウル|韓国|台湾|タイ|バンコク|パリ|ロンドン|ニューヨーク|ヨーロッパ|アメリカ|シンガポール|ベトナム|中国|フランス|イタリア|ドイツ|スペイン|イギリス|オーストラリア|カナダ|グアム|バリ"


def h_travel(t, mem):
    if re.search(r"持っ(て|ていく)|持ち物|荷物|準備|必要なもの", t) and re.search(r"旅|行(く|き)|観光|キャンプ|出張", t):
        key = "pack_overseas" if re.search(_OVERSEAS, t) else "pack_domestic"
        for tid, pat, reply in A.TRAVEL_MISC:
            if tid == key:
                _set_topic(mem, tid, "travel")
                return reply
    hit = _first(A.TRAVEL_MISC[:2], t)
    if hit:
        _set_topic(mem, hit[0], "travel")
        return hit[1]
    for tid, pat, reply in A.DESTINATIONS:
        if re.search(pat, t) and (re.search(_TRAVELISH, t) or tid in ("hakone",)):
            _set_topic(mem, tid, "travel")
            return reply
    hit = _first(A.TRAVEL_MISC[2:], t)
    if hit:
        _set_topic(mem, hit[0], "travel")
        return hit[1]


# ---- R5: self, emotion, small talk, graceful fallback -------------------------------------------
_CAUSES = [(r"仕事|会社|上司|職場|残業|バイト", "お仕事のことなんですね。"), (r"学校|勉強|テスト|試験|受験|宿題", "学校や勉強のことなんですね。"),
           (r"友達|友だち|人間関係|喧嘩|けんか", "人間関係のことなんですね。"), (r"家族|親|母|父|夫|妻|子供", "ご家族のことなんですね。"),
           (r"彼氏|彼女|恋|失恋", "恋愛のことなんですね。")]


def h_self(t, mem):
    for pat, reply in A.SELF:
        if re.search(pat, t, re.I):
            _set_topic(mem, "self", "self")
            return reply


def h_emotion(t, mem):
    if re.search(r"(何|どう|どうし|なぜ|どうして).*(ですか|[?？])$", t) and not re.search(r"嬉し|楽し", t):
        return None
    for tid, pat, replies in A.EMOTIONS:
        if re.search(pat, t):
            r = replies[len(mem.get("turns") or []) % len(replies)]
            if tid in ("down", "tired", "angry", "anxious", "sad", "lonely"):
                for cp, cr in _CAUSES:
                    if re.search(cp, t):
                        r = cr + r
                        break
            _set_topic(mem, "emotion_" + tid, "emotion")
            return r


def h_misc(t, mem):
    hit = _first(A.MISC, t)
    if hit:
        _set_topic(mem, hit[0], "misc")
        return hit[1]


def h_smalltalk(t, mem):
    if re.search(r"^(はい|うん|ええ|そう(だね|ですね|なんだ|か)?|なるほど|へえ|へー|ふーん|そっか|なるほどね|了解|りょうかい|オッケー|OK|いいね|いいですね)[。!！\s]*$", t):
        return "そうなんですね。他にも聞きたいことや、お話ししたいことがあれば、何でも言ってくださいね。"
    if re.search(r"^(ごめん|ごめんね|すみません|すいません|申し訳)", t):
        return "いえいえ、気にしないでください。大丈夫ですよ。"
    if re.search(r"いい(天気|お天気)|天気がいい|晴れ(てる|ている|た)|雨(だ|ですね|が降って)|お出かけ", t):
        return "そうですね、天気がいいとお出かけしたくなりますよね。今日は何か予定はありますか？"
    if re.search(r"^(好き|大好き|すごい|えらい|賢い|かわいい|可愛い|面白い|おもしろい)(です|だね|ね|よ)?[。!！\s]*$|あなたはすごい|いい子|えらいね", t):
        return "ありがとうございます、うれしいです！もっとお役に立てるように頑張りますね。"
    if re.search(r"(つまり|どういう意味|意味が分から|わからない|分からない)", t) and len(t) < 20:
        return "分かりにくくてごめんなさい。どの部分が分かりにくかったか教えてもらえますか？別の言い方で説明しますね。"
    if re.search(r"(何|なに)を(話|しゃべ)", t) or re.search(r"話(そう|しましょう|したい|を聞いて)|おしゃべり|雑談", t):
        return "いいですね、お話ししましょう！今日あったことでも、好きなことでも、最近気になっていることでも、何でも聞かせてください。"
    return None


def _echo(t):
    m = re.match(r"^([^、。!?！？\s]{2,10}?)(?:は|が|を|って|も|に|の)", t)
    if not m or re.search(r"[たいくてだるう]$", m.group(1)):
        return None
    return m.group(1)


def h_fallback(t, mem):
    n = len(mem.get("turns") or [])
    q = re.search(r"[?？]$|ですか|ますか|でしょうか|かな$|教えて|どう(すれば|したら|やって)|何|なに|どこ|いつ|だれ|誰|なぜ|どうして|どれ", t)
    if q:
        outs = ["ごめんなさい、それについては詳しく分かりません。調べものなら、信頼できるサイトや専門家に聞くのが確実です。もう少し詳しく教えてもらえれば、できる範囲でお答えします。",
                "うまくお答えできなくてごめんなさい。別の言い方や、もう少し具体的な内容で聞いてもらえますか？"]
        return outs[n % len(outs)]
    e = _echo(t)
    if e and n % 2 == 0:
        return "「{}」のことなんですね。もう少し詳しく聞かせてもらえますか？".format(e)
    return _pick(D.FALLBACK_REPLIES, mem)

# ---- R6: follow-ups, recap, repeat, chained math ---------------------------------------------------------
_FOLLOW_START = r"^(それ|その|これ|この|あれ|あの|じゃあ|じゃ|では|あと|ほかに|他に|もっと|ちなみに|それで|それなら|で、|でも|それって|なんで|どうして|どのくらい|いつ|どこ|いくら|大丈夫|他には|ほかには|もう少し|詳しく|具体的に)"


def _label(st):
    return D_LABELS.get(st.get("topic"), "") or {"cooking": "料理の話", "home": "お掃除の話", "health": "体調の話", "travel": "旅行の話",
                                                  "emotion": "あなたの気持ちの話", "misc": "さっきの話", "self": "私のこと"}.get(st.get("topic_kind"), "")


D_LABELS = A.TOPIC_LABELS


def _fresh(st, mem, window=3):
    return st.get("topic") and len(mem.get("turns") or []) - st.get("topic_turn", -99) <= window


def _followup(t, mem, loose):
    st = _state(mem)
    turns = mem.get("turns") or []
    # repeat
    if re.search(r"もう(一度|一回|いっかい|1回)(言って|お願い|教えて)|もう一回|もういちど|聞こえなかった|繰り返して|くりかえして", t) and turns:
        return "もう一度お伝えしますね。" + turns[-1]["bot"]
    # what were we talking about
    if re.search(r"(何|なに)の話|さっきの話|何を話して|何について話|今まで(の|何)|話(を)?(戻|もど)|前の話", t):
        lab = _label(st)
        if lab:
            return "さっきは「{}」のお話をしていましたね。続きをお話ししましょうか？".format(lab) if not lab.endswith("話") else "さっきは{}をしていましたね。続きをお話ししましょうか？".format(lab)
        return "まだ、特にお話ししたことはありませんね。何でも気軽に話しかけてくださいね。"
    # chained arithmetic on the previous result
    if "last_num" in st and re.search(r"^(それ|答え|その数)", t) or (re.search(r"それに|その数に|答えに", t) and "last_num" in st):
        from fractions import Fraction
        tt = to_arabic(t)
        m = re.search(_N, tt)
        if m:
            b = Fraction(m.group(1))
            a = Fraction(st["last_num"])
            for pat, fn, label in _OPS:
                if re.search(pat, tt[m.end():]) or re.search(pat, tt[:m.start()]):
                    if "割" in label and b == 0:
                        return "0で割ることはできません。"
                    if label.startswith("{a}引く") and re.search(r"から", tt[:m.start()]):
                        r = b - a
                    else:
                        r = fn(a, b)
                    st["last_num"] = r
                    return "答えは{}です。".format(_fmt(r))
    if not _fresh(st, mem):
        return None
    starts = bool(re.search(_FOLLOW_START, t))
    if loose and (starts or len(t) > 16):
        return None
    if not loose and not starts:
        return None
    for intent, pat in A.FOLLOW_INTENTS:
        if re.search(pat, t):
            subs = A.SUBS.get(st["topic"], {})
            r = subs.get(intent) or A.KIND_SUBS.get(st.get("topic_kind"), {}).get(intent)
            if r:
                st["topic_turn"] = len(turns)
                return r
            lab = _label(st)
            if lab:
                return "「{}」についての詳しいことは、まだ十分に分かりません。もう少し具体的に教えてもらえますか？".format(lab.replace("の話", ""))
    if loose and st.get("topic_kind") == "emotion" and len(t) <= 40 and not re.search(D.THANKS, t):
        return "話してくれてありがとうございます。そう感じるのは自然なことですよ。もう少し聞かせてもらえますか？無理のない範囲で大丈夫です。"
    return None


def h_followup(t, mem):
    return _followup(t, mem, False)


def h_followup_loose(t, mem):
    return _followup(t, mem, True)


def h_math_state(t, mem):
    r = h_math(t, mem)
    if r:
        st = _state(mem)
        m = re.search(r"は(-?[\d,\.]+)(?:です|%)", r) or re.search(r"は約(-?[\d\.]+)です", r)
        if m:
            try:
                st["last_num"] = float(m.group(1).replace(",", "")) if "." in m.group(1) else int(m.group(1).replace(",", ""))
            except ValueError:
                pass
        _set_topic(mem, "math", "fact")
    return r


HANDLERS = [h_thanks, h_bye, h_name_ask, h_name_tell, h_fact_ask, h_fact_tell, h_followup, h_self, h_math_state, h_transit, h_fact, h_datetime,
            h_travel, h_advice, h_misc, h_followup_loose, h_emotion, h_greeting, h_smalltalk, h_fallback]


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
