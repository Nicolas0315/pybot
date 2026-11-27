"""Part 3 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""
import re

from . import lexicon
from .normalize_part_01 import (
    LEXICON, _a_word_the_bot_writes, ME_FOR_MY_CLOSES, PHRASES, _MEASURE, AUX_WORDS, BE_WORDS,
    REPORTING, DETERMINERS,
)
from .normalize_part_02 import (
    AUX_OPENS, _AFTER_PARTICIPLE, _A_STATE_OF_THE_PERSON, _HAVE_ASKING, _HAVE_NEGATIONS,
    _HAVE_PARTICIPLES, _HAVE_THING, _PREDICATE_ONLY, _STATE_FILLER, _STATE_TAIL, _SUBJECTLESS_AUX,
    _SUBJECTLESS_ONLY, _SUBJECTS, DROPPED_SUBJECT_AUX, CAUSE_A_CLAUSE_VERB, CAUSE_A_SUBJECT_FOLLOWS,
    spelled, DIGIT_WORDS, BEFORE_VERB,
)


def opens_without_subject(words, index):
    """True when `words[index]` is an auxiliary and nothing that can be its subject follows.

    "am off to bed" and "was thinking of quitting" have no subject; "am i too late" and "was the
    film good" do, so they are questions and are left alone.
    """
    if index >= len(words) or not words[index]:
        return False
    word = words[index]
    if word not in AUX_OPENS:
        return False
    rest = [w for w in words[index + 1:] if w != "|"]
    if not rest:
        return False
    second = rest[0]
    if second in _SUBJECTS:
        return False
    if word == "am":
        # "am" has one subject only, "I", and if it is not in the line then the person left it
        # off: "am hungry", "am skint", "am freezing", "am not sure", "am nearly done". A
        # question with "am" in it puts the pronoun back ("am i too late"), which the line above
        # has already let through, so there is nothing else a bare "am" can open. Every one of
        # those lines was read as an inverted yes/no question instead: "am hungry" got a search
        # hedge, "am skint" the money shrug, and "am freezing" the cold-weather answer.
        return True
    if second in _PREDICATE_ONLY:
        return True
    if word in _SUBJECTLESS_AUX:
        clause = []
        for word_after in words[index + 1:]:
            if word_after == "|":
                break
            clause.append(word_after)
        at = 0
        while at < len(clause) and clause[at] in _STATE_FILLER:
            # "were both tired", "am so relieved": the intensifier is not the state.
            at += 1
        if (at < len(clause) and clause[at] in _A_STATE_OF_THE_PERSON
                and (at + 1 == len(clause) or clause[at + 1] in _STATE_TAIL
                     or clause[at + 1] in _STATE_FILLER)):
            return True
    if second in _HAVE_NEGATIONS and word == "have":
        return True
    if word == "have" and second in _HAVE_PARTICIPLES and len(rest) > 2:
        # A time on the end makes it an arrangement rather than something the person has the
        # wrong way: "have got the kids tonight" is a plan, and the reply for a plan is better
        # than the note-back a dropped subject gets.
        return (rest[1] in _HAVE_THING and rest[2] not in _HAVE_ASKING
                and not any(w in TIME_WORDS for w in rest[1:]))
    if len(second) > 4 and (second.endswith("ing") or second.endswith("ed")):
        if len(rest) < 2:
            return True                   # "was shattered", "am starving"
        # "am" and "was" cannot take a gerund for a subject, so the person was left off: "was
        # thinking of quitting". "is cooking with gas cheaper" can - "cooking" is what the
        # question is about - so there the verb has to be shown by a verb after it.
        if word in _SUBJECTLESS_ONLY:
            return rest[1] in _AFTER_PARTICIPLE
        after = rest[2] if len(rest) > 2 else ""
        return rest[1] in _AFTER_PARTICIPLE and after.endswith(("ing", "ed"))
    return False


def subject_missing(words, index):
    """True when the subject after this auxiliary was dropped and it was the person typing."""
    return words[index] in DROPPED_SUBJECT_AUX and opens_without_subject(words, index)


# A noun after "cause" is the verb's object ("cause trouble", "cause a fuss"), except after one of
# these, where the cause is the thing being asked about or described: "the cause of the fire",
# "a cause for concern".
CAUSE_BEFORE_A_NOUN = frozenset("the a an this that my your our his her their any no every some "
                                "another one".split())


# A word in front that only a verb follows: "what could cause it", "to cause trouble", "it may
# cause this". These settle the reading whatever comes after.
CAUSE_BEFORE_A_VERB = frozenset("to could would can may might must should will shall does did do "
                                "doesnt didnt dont wont cant cannot never not".split())


# A demonstrative can start a clause ("cause this is a problem") or be the verb's object ("what
# could cause this", "cause this problem"); the word after it decides.
CAUSE_A_DEMONSTRATIVE = frozenset("this that these those".split())


def _cause_in_place_is_the_verb(before, after, after_words=None):
    """Whether a typed `cause` is the verb or the noun rather than the chat spelling of because.

    A subject after it is "because" ("cause i was late", "cause my bus was late"), and so is the
    end of a line with no article in front ("i did it just cause"). Anything else keeps the word.
    """
    if before in CAUSE_BEFORE_A_VERB:
        # "what could cause it", "to cause trouble": only the verb follows these.
        return True
    if before in CAUSE_BEFORE_A_NOUN:
        # "the cause is unknown", "a cause for concern": the article makes it the noun whatever
        # follows, including the "is" that would otherwise look like a clause.
        return True
    if after in CAUSE_A_DEMONSTRATIVE:
        # "what could cause this" and "cause this problem" are the verb; "cause this is a
        # problem" and "cause that i was late" are "because".
        rest = list(after_words or ())[1:2]
        return not rest or rest[0] not in CAUSE_A_SUBJECT_FOLLOWS
    if after in CAUSE_A_SUBJECT_FOLLOWS:
        return False
    if after is None:
        # The end of a line: "i did it just cause" is because, and the noun cases were taken above.
        return False
    if after == "the" and any(word in CAUSE_A_CLAUSE_VERB
                              for word in (after_words or ())[1:4]):
        return False
    return True


# A food that is written as two words and kept as one. The kitchen's pantry is keyed on the one
# word ("chickpeas", "sweetcorn"), so the two-word spelling reached it as two other foods: "chick
# peas" came back as pea soup and "sweet corn" as a line about seasoning. Only pairs that name
# one food both ways, so joining them cannot change what the line is about.
ONE_WORD_FOODS = (
    (re.compile(r"(?<![a-z])chick pea(?![a-z])"), "chickpea"),
    (re.compile(r"(?<![a-z])chick peas(?![a-z])"), "chickpeas"),
    (re.compile(r"(?<![a-z])sweet corn(?![a-z])"), "sweetcorn"),
)


def _one_word_food(clean):
    """The foods written as two words set down as the one word the pantry and answers use."""
    for pattern, one in ONE_WORD_FOODS:
        clean = pattern.sub(one, clean)
    return clean


JOINED_WORDS = re.compile(r"(?<![a-z])(?:%s)(?![a-z])"
                           % "|".join(sorted(lexicon.JOINED_WORDS, key=len, reverse=True)))


def _joined_words(clean):
    """The words people write as one and say as two, set down as the two in `clean`.

    Nothing here is a word, so there is nothing to lose by repairing it where it is written: the
    fed-up reader matches on `clean`, so "im fedup with my job" used to be a shrug while "im fed up
    with my job" got the fed-up reply.
    """
    if not JOINED_WORDS.search(clean):
        return clean
    return JOINED_WORDS.sub(lambda m: lexicon.JOINED_WORDS[m.group(0)], clean)


def _z_for_s(word):
    """A plural written with a z, where the s is a word the engine knows: "ideaz", "dogz".

    People type the plural with the letter that sounds like it - "ideaz 4 tea", "my kidz",
    "thingz" - and the line reaches nothing, so a question about dinner comes back as a
    search hedge. Only a z that stands where an s would is spelled, and only when the word
    that makes is one the engine or the knowledge base already knows, so "jazz", "quiz",
    "buzz" and every real word ending in z are left alone (a word the bot writes stops the
    lookup, and a typed z-word that is a real word is not spelled).

    The knowledge base is read as well as the lexicon because a plural is not always one of
    the lexicon's own words: "ants" is the word the pest rows answer, while the lexicon only
    holds "ant", so "antz" was left alone and "how do i get rid of antz" got the search hedge
    that its correctly spelt twin does not.
    """
    if len(word) < 4 or not word.endswith("z"):
        return None
    if word in LEXICON or _a_word_the_bot_writes(word):
        return None
    fixed = word[:-1] + "s"
    return fixed if fixed in LEXICON or _a_word_the_bot_writes(fixed) else None


def _ache_for_aike(word):
    """"headaike" is "headache": -ache written the way it is said.

    Only the tail is read, and only where the word the tail makes is one the engine knows, so
    a name or a place that happens to end in -aike is never bent into a body part.
    """
    for tail in ("aike", "ayke", "eake"):
        if word.endswith(tail) and len(word) > len(tail):
            fixed = word[:-len(tail)] + "ache"
            if fixed in LEXICON:
                return fixed
    return None


# A contraction typed with a space where the apostrophe is: "she s 84", "i m not sure", "what s
# the point", "we re going", "they ve gone", "you ll see", "he d never say", and the same slip on
# a "not" - "don t worry", "isn t it". The readers are written on the joined word, so the split
# line reached nothing: "she s 84" was answered "I'm listening - say more if it helps" where
# "shes 84" and "she's 84" were both noted. Only a pronoun can take these letters straight on,
# so a plural noun keeps its own ("the dogs ears"), and the "not" needs the joined word to be one
# the engine knows, so a real word in front of a "t" is left alone.
SPLIT_CONTRACTION = re.compile(
    r"\b(i|u|you|he|she|it|we|they|that|there|what|who|where|when|how|this|these|those|let)"
    r"\s+(s|m|re|ve|ll|d)\b(?=\s|[.,!?;:)]|$)", re.IGNORECASE)


SPLIT_NOT = re.compile(r"\b([a-z]{2,}n)\s+t\b(?=\s|[.,!?;:)]|$)", re.IGNORECASE)


# The only words English makes with a "not" are these, so the joined letters are checked against
# them: no other word takes a "t" on the end.
NOT_WORDS = frozenset("""dont doesnt didnt isnt wasnt arent werent havent hasnt hadnt cant couldnt
    shouldnt wouldnt wont mustnt neednt aint shant mightnt""".split())


def _a_contraction_typed_with_a_space(clean):
    """The line with a contraction's two halves put back together, where the halves are its own.

    "she s 84" is how "she's 84" is typed when the apostrophe is left out and the space is kept,
    and the letters after the pronoun are never a word: no line says "she s" or "i m". The
    apostrophe goes back with them, because the joined letters are a word of their own
    elsewhere - "we re based in leeds" is not "were based in leeds". The
    "not" half is joined only when the word it makes is one the engine knows, so "an t" and a
    real word in front of a stray "t" keep their letters.
    """
    if not SPLIT_CONTRACTION.search(clean) and not SPLIT_NOT.search(clean):
        return clean
    clean = SPLIT_CONTRACTION.sub(lambda m: m.group(1) + "'" + m.group(2), clean)

    def join_not(match):
        if match.group(1) + "t" not in NOT_WORDS:
            return match.group(0)
        return match.group(1) + "'t"

    return SPLIT_NOT.sub(join_not, clean)


# "what u up too", "what are you up too": the doubled o is the slip people make on "up to".
# Only after a `what` opener of the same clause, so "are you up too?" (awake as well, thanks)
# keeps its word.
UP_TOO_ASKS = re.compile(r"(\b(?:what|whats|watcha|whatcha|wotcha)\b[^.!?]{0,24}?\b)up too\b")


# A broken heart, said out as a phrase. People write it this way far more often than they type
# "heartbroken", and without this the other words in the line decided the reading: "my heart is
# broken and i dont know what to do" reached the resting heart-rate answer ("the heart beats
# faster... 60 to 100 beats a minute is normal"), and "my heart is broken over a boy" reached
# nobody at all ("Got it. Is there anything you'd like a hand with?"). The words around "heart"
# are the ones that make this safe to read as a feeling: a state (broken, breaking, shattered,
# crushed, in pieces, in bits) is how a feeling is said, while a measure or an action is a body
# ("my resting heart rate", "my heart beats faster when i run", "my heart is racing") and stays
# as it was typed. Any number of measure words is stepped over, so "my heart is so so broken"
# reads the same as "my heart is broken", and the phrase is spelled out as the feeling word so
# every reader that already knows "heartbroken" answers it.
HEART_MEASURES = """so really very too pretty quite still just totally completely absolutely
    utterly properly well a bit a little kind of sort of that this""".split()


# The states a heart is in when the line is about how the person feels, each with the feeling word
# it is spelled out as: broken, breaking, shattered, crushed, torn and the phrases that mean it
# ("in pieces", "in bits", "in two"); a heart that sank or dropped is disappointment. A heavy or
# aching heart is left to the reader that already answers it, as its own advice is better than a
# rewrite. "broken open with joy" is left alone - that is
# the other meaning of a broken heart - and so is a third person's heart ("his heart is broken"),
# which the pattern below only ever reads for "my" and "me".
HEART_FEELINGS = (
    ("heartbroken", ("broken", "breaking", "shattered", "crushed", "torn", "broke", "snapped",
                     "in pieces", "in bits", "in two")),
    ("disappointed", ("sank", "sinking", "dropped")),
)


HEART_SAID_AS_A_FEELING = tuple(
    (re.compile(
        r"(?<![a-z0-9])(?:"
        # "my heart is broken", "me heart's so broken", "my heart was in bits", "my heart aches"
        r"(?:my|me)\s+heart(?:'s|s)?\s+(?:(?:is|was|feels|felt|looks)\s+)?(?:(?:%s)\s+)*"
        r"(?:%s)\b(?!\s+open)(?:\s+(?:in\s+(?:two|bits|pieces)|into\s+(?:a\s+million\s+)?pieces"
        r"|to\s+pieces))?"
        # "she broke my heart"
        r"|(?:[a-z']+\s+)?(?:broke|breaks|breaking|broken)\s+(?:my|me)\s+heart"
        r")" % ("|".join(re.escape(word) for word in HEART_MEASURES),
                "|".join(re.escape(word) for word in states))),
     " i am " + feeling + " ")
    for feeling, states in HEART_FEELINGS)


# The same grief said without the word "heart": "im broken hearted", "my world fell apart". Two
# words a keyboard splits, or the phrase people reach for when the feeling is bigger than one
# word, and both read as no feeling at all: "im broken hearted" was answered "Thanks for telling
# me - I'm here if you want to dig into any of that" and "my world fell apart" with the shrug. The
# phrases are spelled out as the feeling word, the same way a heart is, so the readers that know
# "heartbroken" and "sad" answer them. "broken hearted" needs the word boundary on both sides so
# "a broken hearted song" is read the same, and the world one is only ever the person's own.
SAID_AS_A_FEELING = (
    (re.compile(r"(?<![a-z0-9])broken[\s-]?hearted(?![a-z0-9])"), " heartbroken "),
    (re.compile(r"(?<![a-z0-9])broken[\s-]?heart(?![a-z0-9])"), " heartbroken "),
    (re.compile(r"(?<![a-z0-9])heart[\s-]?broken(?![a-z0-9])"), " heartbroken "),
    (re.compile(r"(?<![a-z0-9])(?:my|me)\s+(?:whole\s+)?(?:world|life)\s+"
                r"(?:fell|has\s+fallen|had\s+fallen|is\s+falling|came|came\s+crashing)\s+"
                r"(?:apart|down|crashing\s+down)(?![a-z0-9])"), " i am sad "),
    # The heart idioms that name dread rather than grief. "my heart is in my mouth" and "my heart
    # is in my boots" are both the fear before something, and neither one is a heart that has been
    # broken, so the readers that answer a heart answered them with the grief card or with the
    # shrug that says the line held no feeling at all. The feeling word is the one the line means:
    # nervous. "my heart is in my throat" is the same and is spelled the same way.
    (re.compile(r"(?<![a-z0-9])(?:(?:my|me)\s+)?heart(?:'s|s)?\s+"
                r"(?:(?:is|was|feels|felt)\s+)?in\s+(?:my|me)\s+"
                r"(?:mouth|boots|throat|stomach|shoes)(?![a-z0-9])"), " i am nervous "),
    # "im crushed", "i feel crushed" - said of the person, not "i crushed my finger"
    (re.compile(r"(?<![a-z0-9])(?:im|i\s+am|i\s+feel|i\s+felt|i\s+was)\s+"
                r"(?:so\s+|really\s+|totally\s+|completely\s+|utterly\s+|absolutely\s+)?"
                r"crushed(?![a-z0-9])(?!\s+by\b)"), " i am sad "),
)


# "what was it i said i was growing" is "what did i say i was growing" with the reaching-back
# `was it` in the middle of it, and no reader downstream could see through that: the memory store's
# recall readers are all written on the plainer spelling, so the ask went to whatever the verb in
# it named. "growing" is a knowledge topic (hair grows) and "painting" is another (emulsion), so a
# turn after the chat had been told about the tomatoes the person was given the hair card. The
# wrapper is folded into the ask it carries, so the reading every module gets is the one the plain
# spelling already gets. `clean` still holds the line as it was typed, which a reply quotes.
SAID_IT = re.compile(
    r"\bwhat (?:was|is) it (?:that )?(?P<who>i|we) (?:said|told you|mentioned)\b"
    r"|\bwhat (?:was|is) it (?:that )?(?P<saying>i|we) (?:was|were|am|are) (?:saying|telling you)\b")


def _the_ask_said_plainer(text):
    """`what was it i said about the oven` -> `what did i say about the oven`.

    The `saying` half keeps its tense and its word order, because "what was i saying about the
    car" is the ask the store already answers and "what i was saying about the car" is not.
    """
    return SAID_IT.sub(
        lambda one: (f"what did {one.group('who')} say" if one.group("who")
                     else f"what {'was' if one.group('saying') == 'i' else 'were'} "
                          f"{one.group('saying')} saying"), text)


_A_CLOSING_WORD = "|".join(sorted((re.escape(word) for word in ME_FOR_MY_CLOSES),
                                  key=len, reverse=True))


_A_HEAD_IN_THE_IDIOM = re.compile(r"(?<![a-z0-9])me head(?=\s+in(?![a-z0-9]))")


_A_CLIPPED_HEAD = re.compile(
    r"(?<![a-z0-9])(?:me|my) (?:ed|ead)(?!s?(?:[a-z0-9]))"
    r"(?=\s+(?:" + _A_CLOSING_WORD + r")(?![a-z0-9])|\s*$|\s*[,.;:!?])")


def _me_for_my_pass(text):
    """`me ed in` and `me head in` -> `my head in`, the two shapes `possessive_me` misses.

    The rest of the possessive "me" is that pass's job, with its own fences (a kin word after a
    verb, the owning verbs, the prepositions), so nothing here overrides it: "she told me mum
    died" and "give me car keys back" keep their "me" because this pass never sees them.
    """
    text = _A_HEAD_IN_THE_IDIOM.sub(" my head", text)
    return _A_CLIPPED_HEAD.sub(" my head", text)


def _phrase_pass(text):
    """Replace whole phrases ("cn u", "b/c", "okey dokey") before words are split."""
    text = _me_for_my_pass(text)
    for heart, feeling in HEART_SAID_AS_A_FEELING:
        if heart.search(text):
            text = heart.sub(feeling, text)
    for pattern, feeling in SAID_AS_A_FEELING:
        if pattern.search(text):
            text = pattern.sub(feeling, text)
    for phrase, value in PHRASES:
        pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            text = re.sub(pattern, " " + value + " ", text)
    text = UP_TOO_ASKS.sub(r"\1up to", text)
    text = _the_ask_said_plainer(text)
    return text


PUNCT_BREAK = re.compile(r"\s*[,;:!?]\s*")


# A full stop between sentences also ends a clause: "we got a puppy called sam. how long ...".
# One letter before the stop is an abbreviation ("e.g."), and a digit after it is a decimal.
SENTENCE_END = re.compile(r"(?<=[a-z0-9]{2})\.(?=\s|$)")


TOKEN = re.compile(_MEASURE + r"|\|")


THOUSANDS = re.compile(r"(\d),(?=\d\d\d\b)")


# A space where the comma would go is the same thousand: "£1 000", "1 200 a month", "£1 000 000".
# It is how a lot of people type a big number, and it was read as the number and then three digits
# left over beside it - "i have £1 000 saved" was answered as a budget of one pound, because the
# money rows read "£1" and stopped at "000". Only groups of exactly three digits join, and only
# when the number starts there, so a phone number ("07700 900 123") keeps its spaces.
THOUSANDS_SAID_WITH_A_SPACE = re.compile(r"(?<!\d)(?<!\d{4} )(\d{1,3})((?:[ \u00a0]\d{3})+)(?!\d)")


# A price typed with a sign is a price with a word in it - and the sign is not a word, so nothing
# after this point saw the money at all: "i have £20 until friday" arrived as "i have 20 until
# friday", the same line typed as "i have 20 pound until friday" was answered about money. The
# sign is written out as the noun people say, so every row that matches on a money word matches
# the figure whether it was typed with a sign or spelled out.
CURRENCY_SIGNS = {"\u00a3": "quid", "$": "dollars", "\u20ac": "euros"}


# The figure can be written the English way or the European one ("1,500.50" and "1.500,50"), and
# a short way with a multiplier ("£1.5k", "£2m"), so all three are read as one amount.
CURRENCY_SIGN = re.compile(r"([\u00a3$\u20ac])\s*(\d+(?:[.,]\d+)*)\s*([km])?(?![\w])", re.I)


CURRENCY_FACTOR = {"k": 1000, "m": 1000000}


def _the_figure(figure):
    """The number a typed amount stands for: "1,500" is 1500 and "1,50" is 1.5."""
    if "," in figure and "." in figure:
        # Both marks: the one that comes last is the decimal point, the other counts thousands.
        decimal = "," if figure.rfind(",") > figure.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        figure = figure.replace(thousands, "").replace(decimal, ".")
    elif "," in figure:
        # "1,500" is a thousand and five hundred, "1,50" is one and a half.
        figure = figure.replace(",", "") if len(figure.split(",")[-1]) == 3 else figure.replace(",", ".")
    value = float(figure)
    return ("%d" % value) if value == int(value) else ("%.2f" % value).rstrip("0")


def _a_sign_is_a_word(text):
    """A currency sign in front of a figure becomes the word for it: "£20" is "20 quid"."""
    def spelled(match):
        sign, figure, scale = match.group(1), match.group(2), (match.group(3) or "").lower()
        value = float(_the_figure(figure).replace(",", ""))
        if scale:
            value = value * CURRENCY_FACTOR[scale]
        written = ("%d" % value) if value == int(value) else ("%.2f" % value)
        return written + " " + CURRENCY_SIGNS[sign]

    return CURRENCY_SIGN.sub(spelled, text)


# A thing, or the far side of a sentence: "me back is ...", "me mum 4 xmas". A word on this
# list is never a thing "me" could own, so "me" in front of it is the pronoun.
NOT_A_THING = frozenset("""
a an the this that these those my your his her its our their some any no every each another
i you he she it we they me him us them who whom whose which what when where why how
is am are was were be been being do does did have has had can could will would shall should
may might must not so as than then too also either neither nor and or but if because
while whilst until till unless whether whenever wherever though although since whereas
in on at to for with from by about into over under after before between through during
up down out off away here there now later soon again still just only even ever never always
please thanks sorry ok okay
myself yourself himself herself itself ourselves yourselves themselves
thinks
""".split())


# What follows the thing "me" owns: a be-word or an auxiliary ("me back is bad"), a number
# ("me mum 4 xmas") or a word of saying ("me mate said"). A joiner is not enough: "owed me
# money and has not paid" and "called me yesterday and" are both the pronoun.
AFTER_A_THING = BE_WORDS | AUX_WORDS | REPORTING | frozenset(DIGIT_WORDS)


# What comes in front of a possessive "me": nothing at all, a joiner that opens the next thing
# said ("and me sister is coming"), or a preposition, which has no object of its own here ("with
# me sister", "on me own", "in me head"). A verb does not: "she gave me keys" and "bought me
# lunch" are the pronoun, so the verb has to be out of the way before "me" can be "my".
BEFORE_A_THING = frozenset("""
with for about of on in at from to over under into by off near round around behind
and but so then also plus because when if or though although since
wiv wid wif abt frm
""".split())


# A person the speaker has: "me mum", "me nan", "me sister". A verb in front of "me" makes
# it the pronoun ("she gave me keys", "bought me lunch"), but a person is not a thing done for
# somebody - nobody "rang me mum" means they rang me instead - so a kin word is the one thing
# "me" owns after a verb too. It is still the pronoun when the kin word has a verb of its own
# ("she told me mum died" told me that Mum died), which is what `after` is asking about.
# The prepositions that carry the British "me" for "my" ("with me sister", "on me phone", "for
# me tea"). After one of these "me" is far more often the object of the preposition than a
# possessive - "the shop near me", "come with me" - so the word after it has to be a thing before
# it is repaired, and a word that is doing something is not one.
BEFORE_A_PREPOSITION = frozenset("""
with for about of on in at from to over under into by off near round around behind
wiv wid wif abt frm
""".split())


# A thing never ends in these: "the bus near me stopped running" was "my stopped", because any
# word after a preposition was taken as a thing to own. A plural noun never ends in "ed" or
# "ing" uninflected, so the endings are safe to use - with two guards. The first is length: a
# short word ending in "-ed" is a thing ("in me bed" was "in me bed", and "in me shed", "in me
# red coat" too), because the verbs of that shape are longer. The second is the closed list
# below, since no length tells "ceiling" from "running".
NOT_A_THING_ENDING = ("ed", "ing")


LONG_ENOUGH_TO_BE_A_VERB = {"ed": 5, "ing": 6}


# What people own that ends in "-ing": a thing, not a verb doing something. Listed because a
# noun and a verb of this shape are one word, which is how this file handles the rest of them.
ING_THINGS = frozenset("""
ceiling ceilings landing landings building buildings bedding wedding weddings pudding
puddings dressing dressings shopping evening evenings morning mornings washing parking
meeting meetings ceiling fencing railing railings
""".split())


DOING_NOT_THING = frozenset("""
shut went goes gone came come left leaves broke broken breaks keeps kept got get gives gave
said says say told tells tell makes made takes took put puts ran runs run fell falls sees saw
seen knew knows know thought thinks think found finds feel feels felt closes close opens open
stops stop starts start works work sits sit""".split())


def _is_doing_something(word):
    """True when a word after a preposition is a verb, and so nothing "me" could own."""
    if word in DOING_NOT_THING:
        return True
    for ending in NOT_A_THING_ENDING:
        if word.endswith(ending) and len(word) >= LONG_ENOUGH_TO_BE_A_VERB[ending]:
            return word not in ING_THINGS
    return False


KIN = frozenset("""
mother mum mom mam mammy mummy father dad daddy son daughter sister brother wife husband
partner nan nana granny gran grandma grandad grandpa grandmother grandfather aunt auntie uncle
cousin niece nephew kid kids child children baby toddler boyfriend girlfriend fiance fiancee
""".split())


# Never a thing "me" could own either, when the line runs on: "up to me honestly", "for me
# please", "to me first". These say how or when, not what, so "me" in front of one is the
# pronoun. The far side of a joiner is here too: "you and me both", "you and me together",
# "him and me forever" are two people, not a thing "me" owns, and the thing before it is the
# partner "me" is named with.
NOT_A_THING_AFTER = NOT_A_THING | frozenset("""
first last next once twice today tonight tomorrow yesterday afterwards afternoons personally
anyway anyhow anymore anymore later sooner honestly really actually probably maybe usually
normally mostly nearly almost quite rather fairly simply clearly obviously certainly
definitely absolutely totally completely entirely exactly precisely again yet ever still
both too either neither together alike forever
alone sometimes earlier meanwhile eventually awhile anyway
""".split())


# A word of time is never a thing "me" can own, wherever it stands: "give it to me Tuesday" and
# "he came with me Monday" are the pronoun and a day, and "he works with me part time" says how
# the work is done. The day can come after the thing too:
#
# Where a thing is not: "wait for me outside", "come with me upstairs".
TIME_WORDS = frozenset("""
monday tuesday wednesday thursday friday saturday sunday
january february march april may june july august september october november december
morning afternoon evening night tonight tomorrow today yesterday midday noon midnight
week weekend weekday month year hour minute
""".split())


PLACE_WORDS = frozenset("""
outside inside indoors outdoors upstairs downstairs home ahead nearby nowhere somewhere
anywhere everywhere
""".split())


# How, not what, in two words: "he works with me part time", "i do it full time".
NOT_A_THING_PAIR = frozenset(("part time", "full time", "half time", "day time",
                               "night time", "real time", "spare time", "free time",
                               "every time"))


# A verb whose object is the thing and never a person it is done for: nobody loses, burns,
# drops or breaks something for you, so "i lost me keys" and "i burnt me toast" are "my".
# A verb that can be done for someone ("bought me lunch", "cut me a slice") is not here, and
# the determiner guard below keeps "i cut me a slice" out even if it were.
OWNING_VERBS = frozenset("""
lost lose losing dropped drop broke broken break cut burnt burned burn forgot forget forgotten
left spilled spilt ripped tore torn smashed chipped scratched hurt banged stubbed twisted
strained scraped find finding wash washing washed ironed ironing doing doin
""".split())


# A question that asks whose something is puts "me" where "my" belongs: "wheres me keys",
# "whats me password", "where is me passport". A question word in front of the thing leaves "me"
# no verb to be the object of, so the thing is what the speaker owns. A word that is doing
# something is not a thing here - "what is me supposed to do", "whats me doing" - so a verb form
# after "me" keeps the pronoun.
# `wher`, `whers` and `wer` are the same question with a letter missing: this pass runs before
# the word repair loop, so it has to hold the typed spellings itself or "whers me keys" keeps
# "me" as the pronoun.
ASKS_WHOSE = frozenset("where wheres what whats wher whers wer wers".split())


def possessive_me(tokens):
    """'me' used for 'my' in front of a thing: "me back is killing me", "me mum 4 xmas".

    British informal writing uses "me" where "my" belongs, and it is the difference between a
    line the bot can act on and one it cannot. Only taken when what follows the thing is a
    be-word, an auxiliary, a number or a word of saying, when "me" opens the phrase it is in
    (nothing in front of it, a joiner, or a preposition: "with me sister", "in me head"), or when
    a question asks whose it is ("wheres me keys"), so an object "me" ("tell me more", "help me
    plan", "gave me keys") is never touched. A kin word is the one exception to the verb: "he
    rang me mum" and "she told me dad" own their person.

    Public because the echo says a line back with the same repair (`bot.memory`'s you()), so
    "i dont get on with me sister" is never said back as "you ... with you sister".
    """
    out = []
    for index, token in enumerate(tokens):
        if token == "me" and index + 1 < len(tokens):
            thing = tokens[index + 1]
            after = tokens[index + 2] if index + 2 < len(tokens) else None
            before = tokens[index - 1] if index else None
            before_before = tokens[index - 2] if index >= 2 else None
            asks_whose = (before in ASKS_WHOSE
                          or (before in BE_WORDS and before_before in ASKS_WHOSE))
            owns_a_person = (thing in KIN
                             and (after is None or after in AFTER_A_THING
                                  or after in BEFORE_A_THING or after in TIME_WORDS
                                  or after in PLACE_WORDS))
            owns_the_thing = (after in AFTER_A_THING
                              or before in OWNING_VERBS
                              or owns_a_person
                              # A part of the body with the word of pain after it, where "me"
                              # opens the phrase: "me belly hurts", "me tummy aches", "me
                              # stomach is bad". A word of pain was not one of the words that
                              # follow a thing, so "me belly hurts" read as the pronoun and the
                              # line as an acknowledgement, while "me head hurts" (which the
                              # body list happened to carry a be-word saying for) was repaired.
                              # Where "me" is an object it is left alone: "it gives me stomach
                              # aches" opens on no joiner, so the thing is still the pronoun's.
                              or (after in lexicon.PAIN_WORDS
                                  and (before is None or before in BEFORE_A_THING))
                              or (asks_whose and thing not in NOT_A_THING_AFTER
                                  and not thing.endswith(("ly", "ing", "ed")))
                              or ((before is None or before in BEFORE_A_THING)
                                  and thing not in NOT_A_THING_AFTER
                                  and not thing.endswith("ly")
                                  # After a preposition the word has to be a thing: a word
                                  # doing something is the verb of its own clause, and "the
                                  # shop near me shut early" owns nothing.
                                  and not (before in BEFORE_A_PREPOSITION
                                           and _is_doing_something(thing))))
            # How or where, and not what: "with me part time", "wait for me outside",
            # "give it to me Tuesday". None of those is a thing, so none is "my". A person is
            # still the person: "he rang me mum yesterday" rang my mum, and the day is when.
            how_or_when = (thing in TIME_WORDS or thing in PLACE_WORDS or after in TIME_WORDS
                           or f"{thing} {after}" in NOT_A_THING_PAIR)
            if (owns_the_thing and thing.isalpha() and len(thing) > 2
                    and thing not in NOT_A_THING and (owns_a_person or not how_or_when)):
                out.append("my")
                continue
        out.append(token)
    return out


# What goes with the sun and never with a child: "my sun cream", "our sun lounger", "her sun
# hat". After one of these the word is the star, not a person.
SUN_WORDS = frozenset("""
bed beds cream creams lounger loungers tan tans burn burns burnt burned hat hats roof roofs
light lights shine shines shining shiny screen screens glasses lotion deck decks rise set
heat trap traps flower flowers dial lamp star stroke dried dry baked bathing baked
""".split())


# Who a sun can belong to: "my son", "our son", "their son". The star belongs to nobody, so a
# possessive in front of it is the one shape that says the person was meant.
OWNING_A_PERSON = frozenset("my our their your his her me".split())


# The second half of the test, and the half that carries it: after a possessive, a person is
# followed by a verb or a copula ("my sun has got a temperature", "my sun is being bullied", "my
# sun keeps waking"), while the star is followed by a noun that goes with it ("my sun allergy",
# "my sun damage", "my sun room", "my sun visor"). A list of star words can never be finished -
# "allergy", "damage" and "room" are all missing from it - but a verb list does not have to be:
# a word that is not a verb here leaves the line exactly as a spell-check would, so a gap costs a
# gain and never buys a wrong reading.
SON_VERBS = AUX_WORDS | frozenset("""
got gotten gets get keeps keep kept went goes gone came comes coming said says saying told tells
telling feels feel felt seems seem seemed looks look looked needs need needed wants want wanted
hates hate hated loves love loved likes like liked hurts hurt hurting cuts cut broke broken breaks
started starts woke wakes woken sleeps slept eats ate eating drinks drank drinking walks walked
talks talked cries cried crying swims swam swim wont cant doesnt didnt isnt wasnt hasnt havent
couldnt wouldnt shouldnt
""".split())


def a_son_not_the_sun(tokens):
    """'"my sun has got a temperature" is about a child, so after a possessive "sun" is "son".

    "sun" and "son" are one sound, and a parent typing about a poorly child writes the star:
    "my sun has got a tempreture of 39" found no person at all and came back as a shrug, where
    "my son has ..." answers it. The star belongs to nobody - it is "the sun" - so a possessive
    in front of it is the shape that says the person was meant.

    The test is on the word after it, twice over. The star's own words fence it off ("my sun
    cream", "our sun lounger", "her sun hat", "my sun burn"), and the person needs a verb or a
    copula there ("my sun allergy" is the star on a person's skin, "my sun has a temperature" is
    the person). The verb half is what keeps a noun nobody listed safe.
    """
    out = []
    for index, token in enumerate(tokens):
        if (token in ("sun", "suns") and index
                and tokens[index - 1] in OWNING_A_PERSON):
            after = tokens[index + 1] if index + 1 < len(tokens) else None
            if after not in SUN_WORDS and after in SON_VERBS:
                out.append("son" if token == "sun" else "sons")
                continue
        out.append(token)
    return out


# A person loses weight; a waistband, a tile and a screw are loose. The two are one sound in
# most English accents, so "loose weight" is what people type, and every reader that looks for
# the losing - the weight answer, the strength answer, the "how is it going" follow-up - was
# looking for a word the line did not have: "i need to loose weight" got a paragraph on squats
# where "i need to lose weight" gets the food answer, "loosing weight is hard" got "I'm
# listening", and "ive loosed 5 pounds" got "Got it."
#
# Only a weight word after it makes it the verb, and only in a short run of the words people put
# between ("loose some weight", "loose a bit of weight", "loose 5 pounds"): a loose handle, a
# loose tile, loose change and loose tea keep their own word, because none of them is followed by
# one of these.
LOOSE_FOR_LOSE = {"loose": "lose", "looses": "loses", "loosing": "losing", "loosed": "lost"}


THE_LOSING = frozenset("""weight pounds lb lbs kilos kilo kg kgs stones stone inches inch
    centimetres centimeters cm""".split())


BEFORE_THE_LOSING = frozenset("""some a an any that the this bit little more few of
    couple coupleof stone
    # "sum" is "some" with the o left out, and it stands where "some" stands: "i gotta loose sum
    # weight b4 the weddin" was "Got it. Is there anything you'd like a hand with?" because the
    # word between "loose" and "weight" was not one the reader knew, while "i gotta lose some
    # weight before the wedding" gets the weight answer.
    sum""".split())


# A word that is a real word, so the corrector leaves it alone by design, standing in the place
# of another one that is a letter away: "pan" for "pain", "hart" for "heart", "ware" for "wear",
# "desert" for "dessert", "live" for "leave", "saw" for "sore". The lexicon holds both words, so
# `fix_typo` refuses - "a confident wrong correction is worse than none" - and the line went to
# the readers with a word in it that names something else: "i have a pan in my chest" came back
# as "Noted: you have a pan in your chest", "my chest panes are bad" as "go easy on yourself",
# "i think im having a hart attack" as "Got it", "i think hes chocked" (a woman writing about a
# choking man) as "Got it", "what can i make for desert" as a list of dinners.
#
# The other word in the line is what says which of the two is meant, so every pair here carries
# the words that decide it, and a pair with none of them in the line is left as it was typed.
# Where the two words are both everyday things - a frying pan, a pane of glass, a saw - the
# body word has to be within three words of the slip, and the words for the object ("window",
# "oven", "frying") fence the pair off, so "two panes of glass" and "the pan in the back of the
# cupboard" keep their own word.
A_PART_THE_PAIN_IS_IN = frozenset("""chest stomach tummy throat ear ears tooth teeth jaw shoulder
    shoulders hip hips neck wrist ankle elbow heel knee knees ribs rib kidney kidneys groin
    armpit chests leg legs arm arms foot feet hand hands head""".split())


# The things a pane of glass is in, and the tools a pan is: none of them is a body, so a line
# about one is not a line about a pain.
A_GLASS_OR_A_PAN = frozenset("""window windows windscreen windscreens glass door doors
    frame frames greenhouse glazing mirror mirrors skylight skylights leaded stained shutter
    shutters cupboard drawer drawers kitchen oven hob handle handles lid lids frying roasting
    saucepan nonstick teflon wok tray freezer freezers""".split())


# A part that is only a body when somebody owns it: "in my back" is the ache, "the back of the
# cupboard" and "the side of the table" are not.
A_PART_A_PERSON_OWNS = frozenset("""back side head belly gut upper lower middle shoulder
    tummy chest arm arms leg legs foot feet hand hands""".split())


A_PAIN_WORD = {"pan": "pain", "pane": "pain", "panes": "pains"}


# A pan is kept and put away; a pain is not. "i keep my pan in my chest" is a pan with a place,
# so the verb in front of it says which word it is.
A_KEEPING_A_THING = frozenset("""keep keeps kept store stored stores storing hang hangs hung
    put puts putting stick stuck stash stashed""".split())


THE_HEART_SAID_THE_OTHER_WAY = frozenset("""attack attacks racing pounding murmur murmer murmurs
    failure bypass flutter flutters palpitations transplant stent pacemaker cardiologist
    valve valves arrest disease angina ecg""".split())


# Who a choke happens to, or what it happens on. A person or a thing eaten, and nothing else: a
# wheel is chocked, a boat is chocked on a trailer, and "on" on its own says neither ("the boat is
# chocked on the trailer" is a boat on a trailer, not somebody choking). "on" was a cue here and
# cost the everyday sense of the word, so the person or the food has to be there.
A_CHOKE_SAID_THE_OTHER_WAY = frozenset("""think he she hes shes im i we they baby son daughter child
    kid kids boy girl man woman dad mum someone somebody anyone anyone food blue bit sweet grape
    nearly started being""".split())


A_THING_WORN = frozenset("""wedding funerals funeral party interview dress dressed suit suits
    shoes shoe coat coats jeans jacket jackets gym tonight outside today work smart casual
    layers boots hat""".split())


A_STATE_YOU_CAN_FEEL = frozenset("""sick ill tired low anxious depressed dizzy faint better
    worse fine ok okay good great awful terrible rough rubbish angry sad happy nervous scared
    worried guilty lonely numb hot cold shaky weepy tearful emotional strange odd funny like
    sickly unwell pleased proud relieved""".split())


A_COPULA = frozenset("""am is are was were be been get got gets getting really very quite so
    still bit too pretty rather always""".split())


BEFORE_A_JOB = frozenset(("my", "the", "this", "a"))


A_JOB = frozenset("""job jobs work role position post company school course flat house city
    country marriage""".split())


# What follows the job when the line is leaving it: a time, or the end of the clause. "i live the
# country life" is a life and not a job, and the word after it is what tells them apart: "life"
# there, "in june"/"next month" or nothing in "i live my job in june" and "i want to live my
# job".
A_TIME_TO_LEAVE = frozenset("""in next on at by from after before tomorrow tonight soon then end
    month week year monday tuesday wednesday thursday friday saturday sunday january february
    march april may june july august september october november december""".split())


def _a_slip_that_is_a_word(tokens):
    """(tokens with the word meant in them, {as typed: the word meant}) for a line that has one.

    Only the pairs above, and only where the line says which word was meant: this is the curated
    route `fix_typo` leaves open for exactly this class, not a guesser.
    """
    lowered = [token.lower() for token in tokens]
    out = list(tokens)
    slips = {}
    for index, token in enumerate(lowered):
        right = None
        before = lowered[index - 1] if index else None
        after = lowered[index + 1] if index + 1 < len(lowered) else None
        after_that = lowered[index + 2] if index + 2 < len(lowered) else None
        if token in A_PAIN_WORD:
            # "i keep my pan in my chest" is a pan with a place, "i keep getting panes in my
            # chest" is the ache: the keeping verb has to be the verb of the slip itself, with
            # a determiner between it and the word.
            kept = (before in DETERMINERS and index > 1
                    and lowered[index - 2] in A_KEEPING_A_THING)
            # A pan dropped on a foot, or a pan that hit a head, is the thing and not the ache:
            # the slip has to stand in a pain frame. "pan in my chest" has the body after it;
            # "chest panes are bad" has the body before it and a state after. "dropped the pan
            # on my foot" has the body after "on", and "the pan hit my head" has a verb after,
            # so neither is the ache.
            after_body = False
            if after == "in":
                for place in range(index + 2, min(len(lowered), index + 5)):
                    part = lowered[place]
                    if part in A_PART_THE_PAIN_IS_IN:
                        after_body = True
                        break
                    if (part in A_PART_A_PERSON_OWNS
                            and lowered[place - 1] in OWNING_A_PERSON):
                        after_body = True
                        break
            before_body = (before in A_PART_THE_PAIN_IS_IN
                           or (before in A_PART_A_PERSON_OWNS and index > 1
                               and lowered[index - 2] in OWNING_A_PERSON))
            feels = after in A_STATE_YOU_CAN_FEEL or after in A_COPULA or after in (
                "hurt", "hurts", "ache", "aches", "aching", "kill", "killing",
                "throb", "throbbing")
            pain_frame = (before_body and feels) or after_body
            if (not kept and not any(word in A_GLASS_OR_A_PAN for word in lowered)
                    and pain_frame):
                right = A_PAIN_WORD[token]
        elif token == "hart" and any(word in THE_HEART_SAID_THE_OTHER_WAY
                                     for word in lowered):
            right = "heart"
        elif (token in ("chocked", "chockes")
              and after not in DETERMINERS
              and any(word in A_CHOKE_SAID_THE_OTHER_WAY for word in lowered)):
            # A determiner after it is a thing being chocked ("i chocked the wheel on the camper"),
            # which is the everyday sense of the word and not somebody choking.
            right = "choked" if token == "chocked" else "chokes"
        elif token in ("ware", "wared") and any(word in A_THING_WORN for word in lowered):
            right = "wear" if token == "ware" else "wore"
        elif token == "desert" and before == "for":
            # "what can i make for desert" is the pudding. A desert with "the" in front of it is
            # the sand ("i came back from the desert"), and one with no "for" is left alone.
            right = "dessert"
        elif (token == "live" and after in BEFORE_A_JOB and after_that in A_JOB
              and (lowered[index + 3:index + 4] or [None])[0] in
              (A_TIME_TO_LEAVE | {None, "|"})):
            right = "leave"
        elif (token == "saw" and before in A_COPULA
              and any(part in A_PART_THE_PAIN_IS_IN for part in lowered)):
            # "my legs are saw after the gym" is the ache, not the tool: a saw is named by a
            # person, never by a body that is a thing.
            right = "sore"
        elif token == "felling" and after in A_STATE_YOU_CAN_FEEL:
            right = "feeling"
        if right and right != token:
            out[index] = right
            slips[tokens[index]] = right
    return out, slips


def loose_is_lose(tokens):
    """'"i need to loose weight" is "lose weight": nobody is loose while putting on trousers."""
    out = []
    for index, token in enumerate(tokens):
        fixed = LOOSE_FOR_LOSE.get(token)
        if fixed:
            for step in (1, 2, 3, 4):
                after = tokens[index + step] if index + step < len(tokens) else None
                if after is None:
                    break
                if after in THE_LOSING:
                    out.append(fixed)
                    break
                if after not in BEFORE_THE_LOSING and not after.isdigit():
                    break
            else:
                out.append(token)
                continue
            if out and out[-1] == fixed:
                continue
        out.append(token)
    return out


# A digit that stands for the word people type it for. "2" and "4" are "to" and "for" in
# front of a word that begins a phrase (a determiner, a pronoun, a question word): a count is
# never written before one of those, so "2 the kids", "4 my mum", "2 u" and "2 my mother" have
# to be words, while "2 cats", "2kg" and "4 of them" stay numbers.
#
# A demonstrative is both ways, and what follows it decides. A period after it makes the digit
# a count of things done in that period ("i did 4 this week", "2 this morning", "4 this
# month"); without one the demonstrative is what the person is talking about and the digit is
# the word ("thx 4 that", "do it 4 that", "what can i do 4 this cough").
DIGIT_AS_WORD = {"2": "to", "4": "for"}


# "2" after a verb of going is "to", whatever place follows: a count cannot follow one, so
# "going 2 spain", "i went 2 benidorm" and "off 2 bed" are all "to". A period is the exception,
# because "going 2 weeks without a drink" counts them.
MOTION_BEFORE = frozenset("""go goes going went gone come comes coming came back off
    goin gona gonna""".split())


DEMONSTRATIVE = frozenset(("this", "that", "these", "those"))


A_PERIOD_FOLLOWS = frozenset("""time times week weeks weekend month months year years
    morning afternoon evening night term semester summer winter spring autumn day days
    hour hours minute minutes second seconds""".split())


A_WORD_CAN_FOLLOW = frozenset((
    "the", "a", "an", "my", "your", "his", "her", "our", "their",
    "you", "u", "ur", "it", "me", "us", "him", "them", "myself",
    "what", "how", "why", "where", "when", "who",
))


# "no" is also how people type "know". A subject in front of it and a pronoun, a question
# word, a determiner or the end of the clause after it make it the verb; every other "no" is
# the word no, which is what "i have no time", "no one" and "no thanks" need.
KNOW_SUBJECT = frozenset((
    "i", "u", "you", "we", "they", "he", "she", "anyone", "any1", "ne1",
    "someone", "some1", "everyone", "every1", "ppl", "people",
))


# The words people put in front of a "no" they mean as "know" without typing a subject in
# front of them: "i dont no how to tell them", "didnt no what to say", "dno where to start".
# One of these is already a whole verb and its "not", so the "no" behind it can only be the
# verb left over - there is nothing else in the clause for it to be. Every other "no" is the
# word no, which "there is no time", "i said no" and "no thanks" need.
NOT_BEFORE_KNOW = frozenset((
    "not", "dont", "don't", "didnt", "didn't", "doesnt", "doesn't", "dnt",
    "havent", "haven't", "havnt", "aint", "ain't", "never",
))


A_VERB_CAN_FOLLOW = frozenset((
    "you", "u", "ur", "it", "me", "us", "him", "them", "i", "we", "he", "she",
    "they", "what", "how", "why", "were", "wer",
    "where", "when", "who", "that", "the", "a", "an", "my", "your", "his", "her",
    "our", "their", "something", "anything", "nothing",
    # "i dont no yet", "dont no if i can make it", "dont no about that", "dont no much about
    # cars": the verb left over after a "no" that is a "know" takes the same words a verb
    # does, and none of these can follow the word no ("there is no yet", "no if") which is
    # what keeps "there aint no milk" and "aint no way" as they are.
    "yet", "if", "whether", "about", "for", "much", "many", "anyone", "anybody",
    "anymore", "either", "myself",
))


BE_FORMS = frozenset("am is are was were".split())


HAVE_FORMS = frozenset("have has had having".split())


MODAL_FORMS = frozenset("could would should must might may ought shall will can".split())


# A contraction written without its apostrophe is often a word in its own right, and only the
# word after it says which one the person meant: "were going to spain" is "we are", while
# "we were late" and "were you there" are what they look like. The reading takes the
# contraction only where the next word leaves no other way to read the line, so a line that
# already makes sense is never rewritten. Typed flat, "were going to spain in may" lost its
# subject: the plan in it was read as a statement about nothing, so the store never noted it
# and the line got the shrug.
#
# "ill" is the same shape ("ill call you later") and is deliberately left alone here: read as
# "i will" a plan stops being an illness, which is right, but a line in the middle of a health
# conversation that stops reading as health loses the topic the next line needs, and the cold
# answer it earned turned into a lecture. A real word that also stands for two words is only
# rewritten where the reply cannot come out worse.
LEFT_OFF_CONTRACTION = {
    "were": ("we", "are"),
}


# What a contraction can be followed by and the plain word cannot: a verb the line goes on
# with, or a word that can only sit after a helper ("were both knackered").
CONTRACTION_NEXT = BEFORE_VERB | frozenset("""
    be been being have had not never also just only still both already always definitely
    probably going off back home away
    having moving getting thinking trying staying doing seeing planning hoping
    let ring phone pop drop grab manage chase quit resign hire rent lock measure weigh need
    love like want miss mean mind aim assume bet guess hope wish promise remind stay sow weed
    mow dig sand tile grout seal glue screw drill hang level varnish log batch bottle
    """.split())


# People, and the words that stand for them, so a "bin" after one is the "been" it sounds like
# ("my mums bin in hospital", "hes bin at work") and a "bin" after anything else stays a bin
# ("the bin in the garden is full", "my bin in the kitchen smells").
PLURAL_SUBJECTS = frozenset("i you we they".split())


THIRD_PERSON = frozenset("he she it".split())


PERSON_WORDS = frozenset("""
    i you he she we they it mum mums mom moms mother mother's fathers dad dads father sister
    sisters brother brothers son sons daughter daughters wife husband partner mates mate
    friend friends boss kid kids baby gran nans nan grandad grandma granny aunt uncle cousin
    neighbour neighbor neighbour's colleague doctor nurse teacher cat cats dog dogs puppy
    puppies kitten kittens rabbit rabbits hamster budgie bird birds horse horses fish
""".split())


PERSON_PREPS = frozenset("in at on to out back away off home there round around up down".split())


# What follows the "been" a "bin" stands for: a verb with its -ing or -ed on, a participle that
# has no ending, or the state somebody has been in ("my cats bin sick", "its bin awful").
HOW_FOLLOWS = frozenset("""much many long far old often big deep quick soon fast come
    did do does can could would should is are was were about of to lot""".split())


BEEN_WORDS = frozenset("""sick ill unwell poorly bad awful great good alright quiet busy
    late away round back out down off twice""".split())


# The subjects a "bin" belongs to when nothing in front of it says so: "bin thinkin bout it",
# "cats bin sick". A determiner never gets here, so "the bin" and "my bin" stay bins.
BEEN_SUBJECT = frozenset("""i you we they he she it that thats its hes shes this these those
    there which what who everything nothing something""".split())


# The word in front of the thing that has "bin": "my phones bin actin up all wk", "our boiler bin
# leaking since tuesday". The thing is not one of the person-words above, so the person rule
# never sees those lines, and the word after the "bin" has to be a verb with its -ing on (or the
# state the thing has been in) - "my bin bags", "my bin is full", "my bin needs emptying" and
# "my bin men come friday" keep their bin.
THING_POSSESSIVES = frozenset("my our your his her their its".split())


# The g people drop off a verb in a hurry: "actin", "tryin", "leakin". A word ending in "in"
# is the verb unless it is one of the few nouns that end the same way, so those keep their word
# ("my cabin bin" is a bin in a cabin, and "my cousin bin" is not a cousin who has been).
IN_NOUNS = frozenset("""
cabin robin basin margin satin ruin twin grin coin pumpkin napkin muffin raisin resin
vitamin protein aspirin insulin cousin dolphin penguin violin mandolin origin virgin cabbage
""".split())


# A thing that is a bin is a bin whatever its -ing word looks like. "my kitchen bin smelling",
# "my compost bin overflowing", "my food bin attracting flies" are a container with a problem,
# and reading the container as a thing that has *been* handed the line to a damp-room answer
# ("find the source before you treat the air"). The words in front of the "bin" name the
# container, and the verbs after it are what a container does.
BIN_CONTAINERS = frozenset("""
kitchen compost food wheelie recycling waste rubbish trash dust garden nappy nappies sharps
bathroom pedal swing carrier paper
""".split())
