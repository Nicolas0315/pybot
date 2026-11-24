"""Part 8 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews, fallback, pick
from ..compose.badnews import reads_as_bad_news, reads_like_a_symptom
from ..compose.goodnews import reads_as_good_news
from ..compose import loss as loss_reading
from ..compose import unseen as unseen_reading
from ..compose import reading as reading_reply


from ..understanding import understand as understanding
from .chat_part_01 import (
    REACTION_CHEERFUL, _news_before, _nobody_would_call_it_nice, AGREEMENT_ONLY,
    REACTION_BARE_FUNNY, REACTION_BARE_GOOD, REACTION_COPULA, REACTION_HOW, REACTION_LEAD,
    REACTION_SIGH, REACTION_SIGH_WORD, REACTION_SUBJECT, REACTION_TAIL, REACTION_WHAT_A,
    REACTION_WORDS, _the_agreement_pool, _letting_someone_down,
)
from .chat_part_07 import (
    SORRY_MET, MOVED_BY, A_NAMED_LOW, CANT_STOP_IT, MY_TEARS, NOT_THEIR_TEARS, NOT_WANTING_IT,
    SOMEBODY_ELSE, SOMEONE_IN_THEIR_OWN_TEARS, WANT_TO_WEEP, WEEPING_WITH_JOY, WHY_THE_TEARS,
    _good_news, HEAVY_FEELINGS, GOING_ON, KEEPS_HOW_I_AM,
)


def _the_answer_met_it_as_news(memory):
    """True when the bot's own last line answered the person as if they had brought bad news."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for turn in reversed([t for t in (turns or []) if isinstance(t, dict)]):
        line = str(turn.get("bot") or "")
        if line:
            return bool(SORRY_MET.search(line) or NEWS_MET.search(line))
    return False


def _a_loss_before(said, memory=None):
    """True when the turn the reaction is about was answered as a death, which no reaction word may answer.

    The tell is the answer, not the words: `loss` and `grief` answer a death and nothing else
    (`NEWS_MODULES`), so a line of theirs is a thread with a death in it whatever it says. Reading
    the person's own words instead stands the reaction aside for a miscarriage and a stillbirth
    too - "we had a miscarriage" then "what a blow" is the line this reading exists for, and the
    word reading threw it back to the floor's search hedge (@happy-clock, #7903). Where the memory
    holds no module there is nothing better to go on, so the word reading is the fallback.
    """
    try:
        turns = memory.get("turns") if isinstance(memory, dict) else None
        last = [turn for turn in (turns or []) if isinstance(turn, dict)]
        if last:
            module = str(last[-1].get("module") or "")
            if module:
                return module in NEWS_MODULES
        if loss_reading.reads_as_loss(said) or loss_reading.a_pet_died(said):
            return True
        return bool(badnews.reads_as_sudden_loss(said))
    except Exception:  # noqa: BLE001 - a reading that cannot be imported adds no guard
        return False


def _reaction(clean, tokens, memory):
    """The pool for a line that only reacts to the last thing said, or None."""
    pool = _reaction_pool(clean, tokens, memory)
    if pool in REACTION_CHEERFUL and _nobody_would_call_it_nice(_news_before(memory)):
        return "react_sigh"
    return pool


def _reaction_pool(clean, tokens, memory):
    """The pool for a line that only reacts to the last thing said, or None.

    Only the reaction itself counts: "the film was scary" has a subject of its own and is not a
    reaction to the last turn, so it passes. Nor is a reaction the first line of a chat - there
    is nothing for it to be about yet.
    """
    if "?" in clean or not tokens or len(tokens) > 7:
        return None
    if not [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]:
        return None
    # "thats a lot isnt it" after a price is a question about the figure, not a reaction to the
    # answer: the reading places it against the range the answer gave ("they said 150" / "thats a
    # lot isnt it" came back "It is. You don't have to be sensible about it straight away.").
    try:
        if reading_reply.judges_a_figure(clean, memory):
            return None
    except Exception:  # noqa: BLE001 - a reading that raises is a line this pool does not judge
        pass
    words = [word.strip(".,!?;:") for word in tokens]
    # A breather is only a breather when something follows it: "so annoying" is the whole line,
    # and "so" there is the intensifier of the reaction, not a word in front of it.
    while len(words) > 2 and words[0] in REACTION_LEAD:
        words.pop(0)
    while words and words[-1] in REACTION_TAIL:
        words.pop()
    if not words:
        return None
    # "me too", "same here", "so am i": nothing but the agreement, so what it agrees with is
    # the whole of the line. Read before the shapes below, which find no subject in it either
    # and answered it as approval of the turn before ("im shattered today" / "so am i" came
    # back "Glad to hear it") or with a stock line about anything ("Great - shout if you need
    # anything else").
    if AGREEMENT_ONLY.match(clean):
        return _the_agreement_pool(memory)
    # "what a blow", "what a nightmare": a reaction with a thing in it instead of a word for the
    # feeling. Read before the shapes below, which find no pronoun and no feeling word in it and
    # left it to the floor's search hedge ("my mum has been diagnosed with cancer" / "what a blow"
    # was answered "I don't know enough to answer that honestly. A search should sort you out
    # quickly."). The thing is what she is reacting to, so the pool is the thing's: the same
    # agreement a "thats awful" gets, and the good ones get the good-news pool.
    if len(words) in (3, 4) and words[0] == "what" and words[1] in ("a", "an"):
        rest = words[2:]
        while rest and rest[0] in {"bloody", "right", "proper", "total", "absolute", "real",
                                   "complete", "utter", "such"}:
            rest = rest[1:]
        thing = " ".join(rest)
        if thing in REACTION_WHAT_A:
            said = _news_before(memory)
            kind = REACTION_WHAT_A[thing]
            if kind == "good":
                # "what a relief" is only about good news that the answer above met as good.
                if said and reads_as_good_news(said):
                    return "react_good"
                return None
            # The bad ones are only for a turn the bot met as news: after a how-to answer the
            # thing is the fault itself ("my boiler is leaking" / "what a mess"), and the pools
            # that answer a fault - "Annoying, that. Is it sorted, or still hanging over you?" -
            # are more use than an agreement with a feeling the person did not name.
            # A death is not a "blow" to be agreed with: "my dad died last week" then "what a
            # shame" is the loss thread's turn, and the agreement pool answered it "Fair enough,
            # and no wonder it's the whole of your head right now" - a register that fits a
            # written-off car and not a funeral. The reading stands aside the way the agreement
            # pool already does for a loss.
            if said and not _a_loss_before(said, memory) and _the_answer_met_it_as_news(memory):
                return "react_" + kind
        return None
    # "how scary", "so grim": the exclamation with no subject at all.
    if len(words) == 2 and words[0] in REACTION_HOW and words[1] in REACTION_WORDS:
        return "react_" + REACTION_WORDS[words[1]]
    # "oh no", "oh dear", "aw god": a sigh about the turn before, with no subject and no word
    # for the feeling in it. A plain "no" is an answer rather than a sigh, so the sigh word has
    # to be there for this shape.
    if len(words) <= 3 and words[0] in REACTION_SIGH and all(
            word in REACTION_SIGH_WORD for word in words[1:]):
        return "react_sigh"
    # "lovely", "brilliant": approval of the news in the turn before, which has to have been
    # good news for the word to be about anything.
    said = _news_before(memory)
    if len(words) <= 2 and all(word in REACTION_BARE_GOOD for word in words):
        if said and reads_as_good_news(said):
            return "react_good"
        if said and _nobody_would_call_it_nice(said):
            # "lovely" said through shock: a reaction with nothing in it to approve, met with the
            # news rather than with a "good luck with it" that fits any message.
            return "react_sigh"
        return None
    # "hilarious", "funny": approval of a turn that was funny, and nothing else.
    if len(words) <= 2 and all(word in REACTION_BARE_FUNNY for word in words):
        return "react_funny"
    # "thats scary", "it sounds awful", "that is so worrying"
    if words[0] in REACTION_SUBJECT:
        rest = words[1:]
        while rest and rest[0] in REACTION_COPULA:
            rest = rest[1:]
        while rest and rest[0] in {"so", "really", "very", "proper", "well"}:
            rest = rest[1:]
        if len(rest) == 1 and rest[0] in REACTION_WORDS:
            return "react_" + REACTION_WORDS[rest[0]]
        # "thats a lot": a reaction like the rest, said with no word for the feeling.
        if rest == ["a", "lot"] or rest == ["a", "hell", "of", "a", "lot"]:
            return "react_bad"
    return None


def _my_own_tears(clean):
    """Whether the tears in the line are the person's own, not somebody else's.

    "my daughter cried at the film" is hers, and a condolence or a question about the film
    answers the wrong person. The first "i" has to come before the person named, the way the
    rest of this module reads whose line it is.
    """
    moved = MOVED_BY.search(clean)
    before = clean[:moved.start()] if moved else clean
    mine = FIRST_PERSON.search(before)
    if not mine:
        return False
    someone = SOMEONE_ELSE.search(before)
    return not someone or mine.start() < someone.start()


def _tears_said_as_a_verb(clean):
    """The pool for the person's own tears said as a plain verb ("i cry every morning"), or None.

    The same guards `_weeping` uses, because it is the same sentence with the wanting taken out:
    a why in the line belongs to the answer that explains the tears ("i keep crying and i dont
    know why" is the pressure-valve entry's line), somebody else's tears are not the speaker's,
    the tears of joy are not a low, and a line that also names a low of its own is that low.
    On top of those, nobody may sit between the person and the verb: "should we let her cry it
    out" is a question about a baby's sleep training, and a condolence about it answers the
    wrong person.
    """
    match = MY_TEARS.search(clean)
    if not match:
        return None
    if SOMEONE_IN_THEIR_OWN_TEARS.search(match.group(0)):
        # "i watched him cry", "we let her cry it out": the tears in the line are still nobody's
        # but the person the line is about.
        return None
    if (WANT_TO_WEEP.search(clean) or NOT_WANTING_IT.search(clean)
            or CANT_STOP_IT.search(clean)
            or NOT_THEIR_TEARS.search(clean) or SOMEBODY_ELSE.search(clean)
            or WEEPING_WITH_JOY.search(clean) or WHY_THE_TEARS.search(clean)
            or A_NAMED_LOW.search(clean)):
        return None
    if _good_news(clean):
        return None
    # Tears that keep coming are the low that has been there a while, not one afternoon of it,
    # and `_going_on` is that pool's own reading.
    return "sad" if _going_on(clean) else "tears"


def _a_low_just_before(memory):
    """Whether the line before this one said how the person feels, in a bad way.

    A follow-up has to be read against what it is following. The reading of the previous line is
    asked for again here rather than kept, the way bot/memory/ack.py does: memory["understood"]
    is this turn's reading, and modules answer in any order.
    """
    if not isinstance(memory, dict):
        return False
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return False
    note = memory.get("heavy_reply")
    if (isinstance(note, dict) and note.get("feeling") in HEAVY_FEELINGS
            and note.get("turn") == len(turns) - 1):
        # The pool the last reply came from is the second reading, the way bot/memory/ack.py
        # does it: the engine files some heavy lines as news ("i miss my mum"), and the person
        # saying nothing helps after one of those is the same follow-up.
        return True
    last = turns[-1]
    said = last.get("user") if isinstance(last, dict) else None
    if not isinstance(said, str) or not said.strip():
        return False
    try:
        read = understanding(said)
    except Exception:  # noqa: BLE001 - a follow-up is never worth a failed turn
        return False
    if read.get("intent") != "feeling" or (read.get("polarity") or 0) > 0:
        return False
    # "im feeling really down today" comes back with no polarity at all, so the mood word is
    # what says it was a bad one to follow.
    return read.get("emotion") not in ("happy", "relieved", "excited", "proud")


# An answer that met heavy news as news. Read from the bot's own last line, because every module
# that takes heavy news writes it there (loss, grief, greeting, answers, chat), so this is one
# gate for all of them rather than a list of their pools: "my mum has cancer" is answered "Sorry
# to hear that. What would help most right now?", and the nod after it must not be "Sounds good."
# The words are the ones the bot only says when it has heard something bad, so a colloquial "my
# phone died" - answered "Leave it off the charger and let it cool down" - keeps its ordinary nod.
NEWS_MET = re.compile(
    r"\b(?:sorry to hear|i'm sorry|i am sorry|so sorry|really sorry|such sad news|"
    r"a lot to carry|that's rough|that is rough|how awful|that's awful|that's hard|"
    r"that is hard|hardest days?|a real loss|nothing about that is a fault|no wonder)\b", re.I)


# The two modules whose own turn is heavy news whatever their wording: they answer a death and
# nothing else, so a line of theirs that does not say "sorry" is still a thread with a death in
# it ("Night, then. Get a proper sleep." closes a bereaved evening).
NEWS_MODULES = frozenset(("loss", "grief"))


# A nod has no subject. "great", "nice one", "fair enough" and "ok then" are the whole line, and
# the ack pool is written for exactly those. "it was great", "that was nice" and "it was alright"
# are three words with an acknowledgement word in them and they were read as the same nod, so a
# person saying how something went got "Fair enough." - a shrug that reads as agreement, because
# the pool it came from answers a shrug. The subject and its verb are what tell the two apart.
NOT_A_NOD = re.compile(
    r"^(?:it|that|this|there|they|he|she|today|yesterday|last night|"
    r"the (?:day|week|weekend|trip|meal|film|game|match|party|wedding|gig|show|interview))\s+"
    r"(?:was|were|is|are|has been|had been|s been|went|got|ended up|turned out)\b", re.I)


# The question form of a nod-sized line: the verb first and a word the ack pool knows after it.
# Only the words a person uses about how their own thing went, so a bare "was it rubbish" still
# has an ask of its own elsewhere and nothing wider is claimed.
ASKED_HOW_IT_WENT = re.compile(
    r"^(?:was|were)\s+(?:it|that|this|they)\s+"
    r"(?:(?:really|actually|very|too|that|so|pretty)\s+)?"
    r"(?:bad|good|nice|hard|tough|rough|scary|easy|awful|ok|okay|alright|fine|fun|horrible|"
    r"dreadful|painful|tiring|stressful|busy|long|slow|worrying|grim|lovely|great|sunny|warm|cold|wet|windy|hot)"
    r"\s*(?:for\s+(?:you|her|him|them))?\s*[?!.]*$", re.I)


def _asked_how_it_went(line):
    """True when the line is the question form of a nod: "was it nice", "did it go ok"."""
    return ASKED_HOW_IT_WENT.match(" ".join(str(line or "").lower().split())) is not None


# The judgement words people put in a yes/no question on their own, with nothing named: "is that
# ok", "is that fine", "will that help", "is that too much". Which pool answers depends on the word
# - a verdict wants the thing, a quantity wants what it has to cover, help wants the job - so the
# word decides it and not the pool.
A_JUDGEMENT_ASKED = re.compile(
    r"^(?:and |so |but |ok |okay |also |sorry |oh |hmm |well )*"
    r"(?:is|are|was|were|will|would|does|do|did|should|shall|can|could)\s+"
    r"(?:that|this|it|these|those|there|they|he|she|we|you)"
    # The words that sit between the pronoun and the judgement, and only those: "is that going to
    # be ok", "is that about right". Any word at all used to be allowed here, which read the tail
    # of "is it alright or all right" as the judgement word "right".
    r"(?:\s+(?:all|really|actually|very|too|that|this|so|still|even|just|quite|pretty|any|much|"
    r"a bit|be|being|been|getting|going|gonna|to|about|like|sound|sounds|seem|seems|look|looks|"
    r"feel|feels)){0,4}"
    r"\s*"
    r"(?P<word>all right|too little|too much|too late|a problem|a worry|a big deal|worth it|"
    # "good enough", "big enough", "old enough": the measure word with the positive in front of
    # it, which is how the quantity is usually asked.
    r"(?:good|well|big|old|fast|strong|warm|long|soon) enough|"
    r"ok|okay|fine|alright|right|correct|good|bad|poorly|safe|dangerous|serious|normal|common|"
    r"wise|sensible|worse|better|enough|much|use|help|helpful|work|do|suit)"
    r"(?:\s+(?:the job|the trick|the business|or not|or no))?"
    r"(?:\s+(?:then|though|honestly|now|yet|here|you|me|us|"
    r"(?:with|for|by|to) (?:you|me|us)))?\s*$",
    re.I)


JUDGEMENT_POOLS = (
    ("enough_no_subject", frozenset(("enough", "too little", "much"))),
    ("too_much_no_subject", frozenset(("too much",))),
    ("help_no_subject", frozenset(("help", "helpful"))),
    ("work_no_subject", frozenset(("work", "do"))),
)


# The composer already asks for the subject of "is that normal", "is that weird" and "is that
# common" in wording written for them ("What is it you are doing and wondering whether it is odd?"),
# so those keep that turn and this pool only takes the ones nothing else asks about.
A_SUBJECT_ALREADY_ASKED = frozenset(("normal", "weird", "odd", "wise", "sensible"))


def _a_judgement_asked(line):
    """Which pool answers a judgement asked with nothing said yet, or "" for anything else."""
    found = A_JUDGEMENT_ASKED.match(" ".join(str(line or "").lower().split()).strip(" .,!?"))
    if not found:
        return ""
    word = found.group("word").lower()
    if word.endswith(" enough"):
        word = "enough"
    if word in A_SUBJECT_ALREADY_ASKED:
        return ""
    flat = " ".join(str(line or "").lower().split())
    # "is it any good" already gets the composer's recommendation ask ("Name the last thing you
    # enjoyed and I'll say whether that is like it"), which is a better answer than asking what
    # the thing is: the pool here only takes the wordings nothing else asks about.
    if word == "good" and re.search(r"\bany good\b", flat):
        return ""
    if re.search(r"\btoo (?:much|little)\b", flat):
        return "too_much_no_subject"
    # "is that ok with you", "does that suit you": the judgement asked about the bot itself, and
    # the true answer is that there is nothing on this end to work around - no diary, no plans.
    if word == "suit" or re.search(
            r"\b(?:with|for|by|to) (?:you|me|us)\b|\bsuits? (?:you|me)\b|\bworks? for you\b",
            flat):
        return "for_you_no_subject"
    for pool, words in JUDGEMENT_POOLS:
        if word in words:
            return pool
    return "judge_no_subject"


def _is_a_nod(line):
    """A line that only acknowledges what was just said: it carries no subject of its own."""
    said = str(line).lower().replace("'", "").replace(",", " ")
    words = said.split()
    if NOT_A_NOD.match(said):
        return False
    return len(words) <= 3 and bool(set(words) & fallback.ACKS)


def _the_nod(memory):
    """Which nod a bare acknowledgement gets, and what to seed it on: (kind, seed).

    The seed is the line the news was in, so a cancer thread and a redundancy thread do not get
    the same sentence twice: with one seed for every thread the four lines collapse to whichever
    one a thread-shaped seed lands on, which is the stock line by another route.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return "ack", ""
    # Three turns, because the person answers heavy news with more than one nod ("ok", then
    # "yeah"), and the third "Sounds good." in a bereaved thread is as wrong as the first. The
    # walk stops at a turn that was not a nod: "my dad died in march" then "how long do i boil an
    # egg" then "ok" is a nod about eggs, and the death being three turns back does not make it
    # a nod at the death.
    recent = [t for t in turns[-3:] if isinstance(t, dict)]
    for index in range(len(recent) - 1, -1, -1):
        turn = recent[index]
        if index < len(recent) - 1 and not _is_a_nod(str(recent[index + 1].get("user") or "")):
            break
        if str(turn.get("module") or "") in NEWS_MODULES:
            return "nod_after_news", str(turn.get("user") or "")
        if NEWS_MET.search(str(turn.get("bot") or "")):
            return "nod_after_news", str(turn.get("user") or "")
        # The person's own line decides it where the answer was practical rather than warm:
        # "i got made redundant today" is answered with "Ask for the offer in writing", and the
        # "ok" after that is still the nod after bad news. `badnews` is the shared reading for
        # this and it is deliberately narrow - "i failed my driving test", "i got a parking
        # ticket" and "my phone died" are not on it, so their nods stay cheerful.
        if reads_as_bad_news(str(turn.get("user") or "")):
            return "nod_after_news", str(turn.get("user") or "")
    return "ack", ""


# "my husband is angry all the time" is a line about him, and the advice to book a GP for weeks
# of a mood is the wrong person's. A person named before the person writing makes it his line.
SOMEONE_ELSE = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:husband|wife|partner|boyfriend|girlfriend|mum|mom|mam|"
    r"mother|dad|father|son|daughter|child|kid|kids|baby|brother|sister|friend|mate|boss|"
    r"colleague|nan|gran|grandad|grandma|aunt|uncle)\b")


FIRST_PERSON = re.compile(r"\b(?:i|im|ive|id|i'm|i've|i'd|feel|feeling|felt)\b")


# An age said in a thread about work that has gone wrong is the age worry, and not the reason for
# anything. "i lost my job last week" then "im 52" was answered "You're 52 \u2014 so that is the
# part behind it. What has been hardest about it?", which hands the person their own age as the
# cause of the redundancy and asks them to open up about it. What a friend does with that line is
# say what age means for the hunt: what to apply for, and how to write the CV that gets read.
AN_AGE_SAID = re.compile(
    r"^(?:i'?m|im|i am|ive|i've)\s+(\d{1,3})(?:\s*(?:years?|yrs?)(?:\s+old)?)?"
    r"(?:\s+(?:now|this year))?\s*[.!]?$", re.I)


# The words that make the thread one about work rather than about a day, so "i had a rotten day" /
# "im 52" keeps whatever it had: a job lost, a search going badly, a boss.
WORK_IN_THE_THREAD = re.compile(
    r"\b(?:job|jobs|work|worked|working|redundan\w*|sacked|fired|laid off|let go|"
    r"interview\w*|cv|career|employer|employed|unemployed|shift|shifts|boss)\b", re.I)


# No age is written into these lines: the person's own figure is put in by the reader below. A
# pool that spells one out ("Fifty-two is not the problem ...") states a made-up fact about
# whoever is not 52 - a 19-year-old was told fifty-two is young for the jobs worth having, and a
# 30-year-old that fifty-two was not the problem. `{age}` is the only number allowed here.
AGE_IN_A_WORK_THREAD = (
    "{age} is not the problem \u2014 the trap is going for the same jobs as people half your "
    "age. Apply for the ones that ask for someone who has done it before.",
    "Age is a real filter in some places and invisible in others. What gets read is a CV that "
    "says what you ran, how big it was and what it saved, not a list of dates.",
    "The roles worth having at your age are the senior versions of what you were doing, and the "
    "quickest way in is the people who already know your work. Ask them before the job boards.",
    "You have years of doing the job properly, and that is what you are selling. Most people who "
    "land well at your age do it through somebody who has seen them work.",
    "It is a fair thing to worry about and it is survivable: apply upwards rather than sideways, "
    "and lead the CV with what you fixed and what it was worth.",
    "{age} is young for the jobs worth having. What were you doing before? I can tell you how "
    "to pitch it.",
)


# The doubt that follows a job going, and follows an age: "will anyone take me on", "am i too old
# to get work". It is not a question about the world, so the search hedge ("that's beyond what I
# know well, sorry") answers nothing and is the coldest reply STYLE.md names. What a friend says
# is what the doubt gets wrong, and where the work actually is.
A_DOUBT_ABOUT_WORK = re.compile(
    r"\b(?:will|would|does|is)\s+(?:anyone|anybody|any one|someone|somebody)\s+"
    r"(?:take me on|hire me|employ me|have me|want me|give me a job)\b"
    r"|\b(?:who|anyone|anybody|someone|somebody)(?:'s| is)?\s+(?:going to|gonna)\s+"
    r"(?:hire|take on|employ|have)\s+me\b"
    r"|\b(?:any|much) (?:chance|hope) (?:of|for) (?:me )?(?:getting )?(?:work|a job|being hired)\b",
    re.I)


A_TOO_OLD = re.compile(
    r"\bam i too old\b"
    r"|\btoo old\s+(?:to\s+(?:get|find|be)\s+(?:a\s+)?(?:job|work)|for (?:this|it|the job))\b"
    r"|\btoo old (?:at|for) my age\b", re.I)


# Two doubts, two answers. "Will anyone take me on" is about the calls coming, and "am i too old"
# is about the age itself: one pool for both answered the second with a "Yes, but ..." that reads
# as "yes, you are too old", which is the worst sentence to hand somebody who has just asked.
TAKEN_ON_REPLIES = (
    "Plenty of people will. The ones who do not call are reading a CV that lists jobs \u2014 name "
    "what you fixed and what it was worth, and the calls come.",
    "Some will and some will not, and the ones who do are worth all of your effort. Ask two people "
    "who have worked with you for a name before you send out anything else.",
    "The ones worth having will, and they hire on what you did rather than on how long ago you "
    "started doing it.",
    "Yes \u2014 the work that wants somebody who has done it before is where your age counts for "
    "you, and that is where to aim.",
)


TOO_OLD_REPLIES = (
    "Not for the jobs worth having. The work that wants somebody who has done it before is where "
    "your age counts for you, so aim at that rather than at the same job you had.",
    "No, though a CV that lists dates will make it look that way. Name what you fixed and what it "
    "was worth and the age stops being the first thing read.",
    "Age is a filter in some places and invisible in others, and the way round both is the people "
    "who have worked with you: ask them for a name before you send anything out.",
    "Old for a warehouse shift, young for the jobs that need somebody who can run the thing. What "
    "did you do before? I can tell you how it reads.",
)


def _a_doubt_about_being_taken_on(clean, memory):
    """The reply to "will anyone take me on" in a thread about work, or None.

    Only in that thread: the same words after a chat about a hobby are a different question, and
    the reading below the lot is left to answer them. A work thread is one of the last three
    turns naming work with something heavy in it, or an age said in it (the age worry and the
    doubt are the same worry, and the person says them one after the other).
    """
    said = str(clean or "")
    found = A_DOUBT_ABOUT_WORK.search(said) or A_TOO_OLD.search(said)
    if not found:
        return None
    if not _in_a_work_thread(memory):
        return None
    pool = TOO_OLD_REPLIES if A_TOO_OLD.search(found.group(0)) else TAKEN_ON_REPLIES
    return pick(pool, memory, clean)


def _in_a_work_thread(memory):
    """Whether the last three turns are about work that has gone wrong.

    "i lost my job last week" / "they gave me a month" / "will anyone take me on" is one thread,
    and a job word three turns back without anything heavy in it ("i work in a warehouse") is a
    thread about the job they still have, which is not this.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    for turn in turns[::-1][:3]:
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("user") or "")
        if not said or not WORK_IN_THE_THREAD.search(said):
            continue
        if reads_as_bad_news(said) or reads_like_a_symptom(said) or AN_AGE_SAID.match(said.strip()):
            return True
    return False


def _the_age_in_a_work_thread(clean, memory):
    """The reply to an age said after a job has gone, or None when that is not this turn.

    Only an age on its own: "im 52 and no one will interview me" names the trouble itself and is
    answered by whoever owns it. And only while the thread is about work - the last three turns
    are walked because "i lost my job last week" / "they gave me a month" / "im 52" is one thread,
    and a line about the age three turns back is not the thread any more.
    """
    found = AN_AGE_SAID.match(str(clean or "").strip())
    if not found:
        return None
    age = int(found.group(1))
    if age < 18 or age > 99:
        return None
    if _in_a_work_thread(memory):
        # The figure is theirs, so the two lines that carry one say the age they gave rather than a
        # number written into the sentence.
        return pick(AGE_IN_A_WORK_THREAD, memory, clean).replace("{age}", str(age))
    return None


def _going_on(clean):
    """True when a mood is said to have been going on, in the person's own words.

    Only then: "my husband is angry all the time" is about him, and the weeks-of-it line would be
    advice for the wrong person.
    """
    # The habit verb is the only thing that says it comes back, and GOING_ON's habit arm names
    # three verbs ("keep feeling", "keep crying", "keep being"), so the rest of the tears family
    # was read as a single bad day: "i keep weeping" and "i keep welling up" got the pool
    # written for one afternoon, while "i keep crying" got the one that says the coming back
    # itself is what is worth mentioning. A mood said with "i keep" is a mood that keeps coming
    # back, whatever the verb after it is.
    if not (GOING_ON.search(clean) or KEEPS_HOW_I_AM.search(clean)):
        return False
    other = SOMEONE_ELSE.search(clean)
    if not other:
        return True
    mine = FIRST_PERSON.search(clean)
    return bool(mine and mine.start() < other.start())


# "i feel like ..." is how people describe a state they have no single word for: "i feel like
# im not doing enough", "i feel like the only one doing the housework", "i feel like i dont
# know what to do with my life". No word in FEELINGS is in any of those, so they used to get a
# stock acknowledgement ("Noted! What would be most useful to talk about?") that says nothing
# back. The comparison the person draws decides the reply, so the patterns below sort the line
# by what it compares itself to, not by a word list that can never be long enough.
FEEL_LIKE = re.compile(
    r"\bfeel(?:s|ing)?\s+like\s+(?:i\b|i'm\b|im\b|me\b|my\b|myself\b|we\b|everyone\b|"
    r"everybody\b|nobody\b|no one\b|no-one\b|nothing\b|things\b|life\b|"
    r"a (?:failure|fraud|mess|joke|burden|disappointment|let ?down|useless|rubbish|terrible|"
    r"awful|horrible|bad)\b|"
    r"an? (?:idiot|imposter|impostor|bad (?:mum|mom|dad|mother|father|parent|person|friend))\b|"
    r"the worst (?:mum|mom|dad|mother|father|parent|person|friend|wife|husband|partner|son|"
    r"daughter)\b)")


# "i feel like i need a holiday" is a want said with a feeling frame, and main asks about the
# holiday ("What kind of holiday do you usually go for?"). FEEL_LIKE only reads as far as
# "feel like i", so without this the want was read as a mood. No "should" here: "i feel like i
# should be further along by now" is a comparison and keeps its own reply.
FEEL_LIKE_WANT = re.compile(
    r"\bfeel(?:s|ing)? like (?:i|we)\s+(?:need|want|could do with|fancy|"
    r"(?:am|'m) going to)\b")


# "i feel like nobody listens to me" is about not being heard, and main answers it ("I'm
# listening - say more if it helps."). The left-out reply is about a group, which is a
# different complaint, and talking to "the one person you'd genuinely want to see" answers
# neither.
FEEL_LIKE_NOT_HEARD = re.compile(
    r"\bnobody (?:ever )?(?:listens|listened|hears|hearing|understands|understood)\b|"
    r"\bno ?-?one (?:ever )?(?:listens|listened|hears|hearing|understands|understood)\b")


# "my mum feels like a failure" and "he feels like nobody listens" are about them, not the
# person writing, so they are left to whoever answers lines about other people.
OTHER_FEELS_LIKE = re.compile(
    r"\b(?:my|his|her|their|our)\s+\w+\s+(?:feels?|is feeling)\s+like\b|"
    r"\b(?:he|she|they)\s+(?:feels?|is feeling)\s+like\b")


# Too little done: the person is scoring themselves and finding themselves short.
FEEL_LIKE_NOT_ENOUGH = re.compile(
    r"\bnot (?:doing |being |getting )?(?:good )?enough\b|\bnever (?:good |doing )?enough\b|"
    r"\bdoing (?:everything|it all) (?:wrong|badly)\b|"
    r"\b(?:can'?t|cant|cannot) (?:do|get) (?:anything|it) right\b|"
    r"\bletting (?:everyone|everybody|people|them|her|him|down)\b|"
    r"\blet (?:everyone|everybody|people|them|down) down\b|"
    r"\b(?:(?:such )?a|like a) (?:failure|fraud|mess|joke|burden|disappointment|let ?down)\b|"
    r"\b(?:useless|worthless|hopeless|a rubbish|a bad|a terrible) (?:mum|mom|dad|mother|father|"
    r"parent|person|friend|wife|husband|partner|son|daughter)\b|"
    r"\bnot good at (?:anything|my job|this|being)\b|"
    r"\b(?:rubbish|bad|useless) at (?:my |the )?(?:job|work|everything)\b|"
    # "the worst mum in the world" is the same comparison said at its loudest, and the stock
    # acknowledgement answered it before. Only the words above, so "the worst day at work" is
    # not read as this.
    r"\bthe worst (?:mum|mom|dad|mother|father|parent|person|friend|wife|husband|partner|"
    r"son|daughter) (?:in the world|ever|alive)\b")


# The composer's worth line ("That is a hard standard to hold yourself to. Whose is it - yours,
# or somebody else's?") already answers the lines where the person is measured against a
# standard: not enough, useless, behind everyone. It asks them something and this reading would
# only say it back, so those lines stand down and the composer keeps them.
FEEL_LIKE_WORTH = re.compile(
    r"\bnot (?:doing |being |getting )?(?:good )?enough\b|\bnever (?:good |doing )?enough\b|"
    r"\b(?:can'?t|cant|cannot) (?:do|get) (?:anything|it) right\b|"
    # The self-insult nouns: main's worth pool answers "i feel like a failure" with "I doubt
    # that's the whole picture - you're being harder on yourself than you'd be on a friend",
    # which asks nothing of them and presumes no task list. A pool line cannot beat it.
    r"\b(?:a|an|like a) (?:failure|fraud|mess|joke|burden|disappointment|waste of space)\b|"
    r"\bmy (?:\w+ )?(?:is|was|isnt|isn'?t|wasnt|wasn'?t)?\s*(?:just |never |still |always )?"
    r"(?:not\s+)?(?:good\s+)?enough\b|"
    r"\b(?:im |i'?m |i am )?useless\b|\bbehind (?:everyone|in life|on everything)\b|"
    # "i feel like im failing at everything" is the person scoring the whole of themselves, and
    # main's worth line ("That weighs a day, not a life. What set it off?") meets the feeling
    # where the week pool went straight to a task list.
    r"\bfail(?:ed|ing)? at everything\b")


# A role the person is failing at ("i feel like a bad dad", "im failing as a mother", "the
# worst wife in the world") has an answer of its own already, and it names the standard and asks
# what happened: "That is a hard thing to say about yourself. What happened today?", "That weighs
# a day, not a life. What set it off?". The comparison pools below can only answer that with a
# to-do list they never mentioned ("You are being measured against a version of the day that
# nobody has"), so the role stands down and lets that reading keep the turn.
FEEL_LIKE_ROLE = re.compile(
    # the "im" form is how most people write it: "i feel like im a bad mum" says the same role as
    # "i feel like a bad mum", and leaving it out sent the line to the measuring pool instead of
    # the reply that names the standard and asks what happened.
    r"\bfeel(?:s|ing)? like (?:(?:im|i'?m|i am) )?(?:a|an) (?:really |proper |right |useless |"
    r"rubbish |terrible |"
    r"awful |horrible |bad |lousy )*(?:mum|mom|mother|dad|father|parent|person|friend|wife|"
    r"husband|partner|son|daughter|boss|manager)\b|"
    r"\bfeel(?:s|ing)? like (?:(?:im|i'?m|i am) )?the worst (?:mum|mom|mother|dad|father|"
    r"parent|person|friend|wife|"
    r"husband|partner|son|daughter)\b|"
    r"\bfailing (?:as|at being) a (?:mum|mom|mother|dad|father|parent|partner|wife|husband)\b")


# "i feel like i cant cope" already gets a warm question that offers something ("That's a heavy
# place to be. Is there one thing that would help, even a small one?"), and the generic pool below
# only asks them to say more, so the line stands down.
FEEL_LIKE_COPE = re.compile(
    r"\b(?:can'?t|cant|cannot) (?:cope|manage)(?: any ?more| at all| with (?:it|this|anything))?\b")


# "im invisible at home" names a family, not a table of friends, and the left-out pool is about
# friends. Home goes to the plain pool, which presumes no place at all.
FEEL_LIKE_AT_HOME = re.compile(
    r"\b(?:at|in) (?:my |our |the )?(?:home|house|flat|family)\b|\bmy family\b")


# Too much landed on them: the complaint is fairness, and the reply has to be about them not
# doing more of the work.
FEEL_LIKE_LOAD = re.compile(
    r"\bonly (?:one|person) (?:who |that )?(?:does|doing|is doing|cleans|cleaning|cooks|"
    r"cooking|remembers|notices|trying|tries|bothers|cares|helps|works)\b|"
    r"\bnobody (?:else )?(?:helps|bothers|does anything|notices|pulls their weight)\b|"
    r"\bno ?-?one (?:else )?(?:helps|bothers|does anything|notices)\b|"
    r"\b(?:carry|carrying|carried) (?:everything|it all|the lot)\b|"
    # "i feel like i have to do everything" is a load, not a want: "have to" is not in
    # FEEL_LIKE_WANT for that reason.
    r"\b(?:have|has|having) to do (?:everything|it all)\b|"
    r"\ball (?:the |of the )?(?:housework|chores|cleaning|cooking|washing|work|tidying)\b")


# The uneven-home-load entry answers "i do everything at home" with a named job on a named day,
# which is more use than any feeling reply, so this reading stands down on that exact complaint.
# "i do all the washing" and "im the only one doing the housework" are not that line and are not
# answered by the entry, so they keep the load reply.
FEEL_LIKE_HOME_LOAD = re.compile(
    r"\b(?:do|doing|does|did) (?:everything|it all) (?:at home|around the house|in the house|"
    r"in our house|around here)\b")


# "i feel like myself again" is good news, and the complaint pools read it as one more problem:
# the tail is what the person is reporting, so it gets its own line.
FEEL_LIKE_GOOD = re.compile(
    r"\b(?:myself|me|my old self|human) again\b|\ba (?:new|different) (?:person|woman|man)\b|"
    r"\bon top of the world\b|\bback to (?:my old self|normal|myself)\b|"
    # Good news said as a comparison rather than a feeling word: "im finally getting somewhere",
    # "i matter again", "im on top of things again". The complaint pools read every one of these
    # as one more problem ("I'd be feeling it too"), which turns a good week back into a bad one.
    r"\b(?:finally )?(?:getting|get|going|getting there) (?:somewhere|there)\b|"
    # "i feel like im doing everything right" is the good version of the not-enough line, and
    # the complaint pools read it as one ("not a mood to snap out of"), which congratulates
    # nobody on a week that is going well.
    r"\b(?:doing|getting) (?:it|everything) right\b|"
    r"\bmatter(?:ing)? again\b|\b(?:got|getting|back) (?:on top of|a handle on) (?:things|it|"
    r"everything)\b|\bon top of (?:things|everything)\b|"
    r"\b(?:coping|managing|handling it) (?:at last|again|better)\b|"
    r"\bback to (?:my usual self|normal|normality)\b|\bover the (?:worst|hump)\b|"
    r"\b(?:can|could) (?:keep up|cope|manage|handle (?:it|things)) (?:now|again|at last)\b")


# The one phrase in the good-news pool that means two things. "im finally getting there" and
# "getting there, thanks" are a report of progress; "how do we get there", "what time should i
# get there" and "i will call you when i get there" are a journey, and congratulating them answers
# nothing the person asked ("That's a good thing to hear" to a question about the way to Lisbon).
# The word in front of the phrase decides which it is: a question or a time word makes it the
# journey. Nothing else in the pool is read this way - "what a week, im on top of things again"
# is still progress.
ARRIVAL_WORDS = re.compile(
    r"\b(?:how|what|when|where|whether|which|why|who)(?:s|'s)?\b|\b(?:can|could|will|would|"
    r"shall|should|do|does|did|is|are|if|once|before|after|until|till|by|time|early|late|long|"
    r"far|soon|first|way|route|best|easiest|quickest|cheapest|drive|train|bus|taxi|walk)\b")


# Main has grown its own answer for these since this reading was built, and it is the better one:
# "Change one thing you do on autopilot - a different walk, a new lunch" for a person stuck in a
# rut, "Feeling like a fraud in a job you were hired for is close to universal" for one who does
# not belong. A second reading that replaced those with a mood line would be a step back, so the
# comparison stands down and lets them through. The "what do i want out of life" lines are the
# same story: `LIFE_ADRIFT` below names them and main answers them itself.
FEEL_LIKE_MAIN_ANSWERS = re.compile(
    r"\b(?:stuck|in a rut|going nowhere|treading water)\b|"
    r"\b(?:don'?t|dont|do not|doesn'?t|does not|never) belong\b|\bno longer belong\b|"
    r"\b(?:have |got )?no (?:friends|mates)\b")


# Too much landed on them at once. That is not a comparison to answer with a mood line: main
# reads the overload and offers the one thing that helps ("That is more than anyone can hold in
# your head - get it out of your head and onto paper"), which is more use than naming the weight
# back to them, so this reading stands down. "i feel like i cant keep my head above water" is not
# here: main has no answer for it and the comparison line is better than a shrug.
FEEL_LIKE_OVERLOAD = re.compile(
    r"\b(?:drown(?:ing|ed)?|spread(?:ing)? (?:too )?thin|snowed under|buried in)\b|"
    r"\b(?:can'?t|cant|cannot|struggl\w* to) keep up\b|\bkeeping up with\b|"
    r"\bjuggling (?:too much|everything|it all)\b")


# No idea where they are going.
FEEL_LIKE_ADRIFT = re.compile(
    r"\b(?:don'?t|dont|do not|doesn'?t) know (?:what to do|where to (?:start|begin|go)|"
    r"what i (?:want|should)|who i am|where i (?:am|am going|belong))\b|"
    r"\b(?:feel )?(?:lost|stuck|behind|adrift)\b|\bno (?:idea|clue) (?:what|where)\b|"
    r"\bwasting (?:my time|my life)\b")


# "im 34 and i still dont know what i want to do" names no feeling word either, and the
# comparison is the same one: no idea of the shape of their own life.
LIFE_ADRIFT = re.compile(
    r"\b(?:don'?t|dont|do not|still don'?t|still dont) know (?:what to do with my life|"
    r"what i want to do|what i want out of life|where to start with my life)\b|"
    r"\bno idea what to do with my life\b")


# Nothing in this reading may take a line that sounds like someone who does not want to be here:
# "i feel like im a burden to everyone" and "i feel like nobody would notice if i was gone" are
# not a comparison to answer with a line about measuring yourself. They stand down for whoever
# reads them properly.
IDEATION = re.compile(
    r"\b(?:a burden|burden to|better off without|better off if i|shouldn'?t be here|"
    r"should not be here|not (?:be|been) here any ?more|(?:would|wouldn'?t|will|won'?t|"
    r"might not) notice|in the way|if i (?:was|were) gone|if i (?:wasn'?t|was not|weren'?t) here|"
    r"no point (?:any ?more|in (?:anything|it|going on|carrying on|life))|no reason to (?:live|"
    r"be here|go on|carry on)|ending it|end it all|want to die|wanna die|kill myself|"
    r"hurt myself|harm myself|can(?:'?t| ?not) (?:go on|carry on|keep going)|cannot go on|"
    r"(?:not|never) wake up)\b")


# A thing that has already happened with a result on it: "I failed my driving test today and I
# feel like an idiot" names a test, and there is a better reply than a mood talk ("give it a
# day, then look at what you can control next time"). The line's own event decides that, so the
# plain "i feel like ..." reply stands down and lets whoever answers the event have it.
EVENT_DONE = re.compile(
    r"\b(?:failed|failed at|passed|sat|didn'?t get|didnt get|got turned down|was turned down|"
    r"got rejected|was rejected|missed|lost|blew|messed up|did badly)\b[^.]*\b"
    r"(?:test|tests|exam|exams|interview|interviews|audition|presentation|race|match|game|"
    r"course|driving|physical|assessment|trial|shift|application|deadline|review)\b")


# "i feel like im failing at everything" is the whole week, not one thing done badly. This is not
# `EVERYTHING_WRONG` above: that one is main's `not_enough` judgement, and a second definition of
# the same name further down the file would quietly shadow it and send "i always mess everything
# up" back to the stock acknowledgement.
FEEL_LIKE_EVERYTHING = re.compile(
    # not "failing at everything": that one is a worth line and is named in FEEL_LIKE_WORTH, which
    # stands down before this pool is reached.
    r"\b(?:ruining everything|getting everything wrong|"
    r"messing everything up|nothing i do (?:is|works))\b")


# Feeling sick is a body, not a mood: "i feel like im going to be sick" belongs to whoever
# answers that, so this reading stands down on it.
FEEL_LIKE_PHYSICAL = re.compile(
    r"\b(?:be sick|being sick|throw up|throwing up|vomit\w*|pass out|passing out|faint|"
    r"fainting|dizzy|collapse|collapsing)\b|"
    # A body going wrong is not a mood either: "i feel like im getting ill" is the cold coming
    # on, and a line about measuring yourself does not help with it.
    r"\b(?:getting|going|coming down with|feel|feeling) (?:ill|poorly|unwell|a cold|the flu|"
    r"the bug|something)\b")


# An illness named as the reason after "feel like": "i feel like im dying of this flu" is a body
# that is ill, and the knowledge base answers it ("Ugh, that's rotten. Take it slow today"). Only
# an illness word counts, so "dying of embarrassment" and "dying after that shift" stay feelings.
FEEL_LIKE_ILLNESS = re.compile(
    r"\b(?:dying|die|dead|suffering|rotting)\s+(?:of|from|with|off)\s+"
    r"(?:this\s+|the\s+|a\s+|my\s+|that\s+|these\s+)?"
    r"(?:flu|cold|virus|bug|migraine|headache|infection|cough|temperature|fever|"
    r"sore throat|chest infection|stomach bug|norovirus|sinusitis|bronchitis)\b|"
    r"\b(?:feel|feeling|felt) like (?:im |i am )?(?:dying|dead)\b[^.]*\b(?:flu|cold|virus|bug|"
    r"migraine|infection|cough|fever|temperature)\b")


# Nobody on their side.
FEEL_LIKE_LEFT = re.compile(
    r"\b(?:left out|on the outside|the odd one out|invisible|ignored|excluded|unwanted)\b|"
    r"\bnobody (?:likes|wants|invites|invited|talks to|listens|hears|understands|"
    r"sees|notices|takes me)\b|"
    r"\bno ?-?one (?:likes|wants|invites|talks to|listens|hears|understands|sees)\b|"
    r"\bno (?:friends|mates)\b")


# What the person holds themselves against, once "feel like i" has been read: a comparison,
# which is what the generic pool below answers. "i feel like im pregnant", "i feel like im
# losing weight" and "i feel like im on holiday" carry none of these, and they are a state
# somebody else answers better than a line about a bad week would.
FEEL_LIKE_JUDGEMENT = re.compile(
    r"\b(?:nothing|nobody|no ?-?one|never|alone|lonely|by myself)\b|"
    r"\b(?:useless|hopeless|worthless|pointless|stupid|thick|dumb|rubbish|crap)\b|"
    r"\b(?:can'?t|cannot|couldn'?t|unable to|head above water|keeping my head|keeping up)\b|"
    r"\b(?:on top of me|on top of everything|further along|left behind|by now|dying|dead)\b|"
    r"\b(?:an? (?:burden|joke|fraud|imposter|impostor|disappointment|let ?down|liability|"
    r"mess|waste)|a waste of|too much|not good enough|on the edge|at breaking point|"
    r"breaking point|going backwards|failing|falling apart|in pieces|broken|"
    r"losing my mind|going (?:mad|crazy|insane))\b")


def _a_journey_not_progress(clean, match):
    """True when "get there" in this line is the way to a place, not a report of progress.

    Only the journey words are read in their context ("there"), so the rest of the good-news
    pool keeps its reading. A question or a time word in the 60 characters in front of the
    phrase makes it the journey: "how do we get there", "what time should i get there", "how
    early should we get there", "do i just get changed when i get there". Anything the person
    reports about themselves keeps the good reading, including the "feel like" frame itself:
    "i feel like im finally getting there"."""
    if not re.search(r"\bthere\b", match.group(0)):
        return False
    before = clean[max(0, match.start() - 60):match.start()]
    if re.search(r"\bfeels?\b", before):
        return False
    return bool(ARRIVAL_WORDS.search(before))


# The words that only carry a good tail and never make one: "im finally getting somewhere" and
# "im over the worst of it" are progress; "how long will it take to get there" is a journey.
GOOD_TAIL_LEADS = frozenset("""finally nearly almost now slowly definitely really properly
at last getting get going coping managing doing matter mattering back over on top of the
it things a an up""".split())


# A good tail is about the person when the words in front of it are the person (or the state of
# their life) with a verb of being: "i'm", "we are", "things are back to normal", "its back to
# normal", "life is back to normal". "things are back to normal" is a progress report and the
# pool it belongs to is the good-week one; reading it as news cost that card its turn. The words
# that only look like this are the place lines ("how do i get there", "when i get there"), and
# none of them ends on a subject with a verb of being in front of the tail.
_STATE_OF_THEIRS = re.compile(
    r"\b(?:i'?m|i am|i'?ve|ive|we'?re|we are|we'?ve|weve|were|been|it'?s|its|it is|it was|"
    r"things are|things were|things get|things got|lifes|life is|life was|life gets|"
    r"everything'?s|everything is|everything was|everything gets|nothing is|nothing'?s|"
    r"stuff is|it all is|days are)\s*$")


def _said_about_themselves(before):
    """Whether the words in front of a good tail make it the person's own report.

    "i feel like myself again", "im finally getting somewhere" and "im over the worst of it now"
    are the person saying how they are doing. The same tails sit in ordinary lines: "how do i get
    there", "what should i do first when i get there", "my son wont call me again", "i cut myself
    again on glass". The reading that congratulates whoever said them is how "how do i get there"
    came to be answered "That's a good thing to hear. Whatever you have been doing, keep it going
    another week before you draw conclusions" - no answer at all to a person asking the way.
    """
    words = re.findall(r"[a-z']+", str(before or "").lower())
    while words and words[-1] in GOOD_TAIL_LEADS:
        words.pop()
    if not words:
        return False
    if re.search(r"\b(?:feel|feels|feeling|felt)\b", " ".join(words[-4:])):
        return True                  # "i feel like i matter again", "i felt like me again"
    if _STATE_OF_THEIRS.search(" ".join(words[-3:])):
        return True       # "things are back to normal", "its back to normal", "life is back"
    return bool(re.search(r"\b(?:i'?m|i am|i'?ve|ive|we'?re|we are|were|been)$",
                          " ".join(words[-2:])))


def _feel_like(clean):
    """The reply for "i feel like ...", or None when the line is a want or about someone else.

    "i feel like a curry" and "i feel like going out" are wants, and the patterns above do not
    match them. Only the person writing is read here: "my mum feels like a failure" is a line
    about her."""
    if (FEEL_LIKE_PHYSICAL.search(clean) or FEEL_LIKE_ILLNESS.search(clean)
            or IDEATION.search(clean)):
        return None
    if FEEL_LIKE_WANT.search(clean) or FEEL_LIKE_NOT_HEARD.search(clean):
        return None
    if unseen_reading.reads(clean):
        # "i feel like im invisible at work", "i feel like nobody cares", "i feel like nobody is
        # on my side": the unseen reading already answers not being seen by the people around
        # you, and it answers with a line and a question ("That would get to anyone... Is there
        # one person you could say this to?"). Naming the mood back is less use than that, and no
        # list of places here would cover the lines it hears, so it keeps the turn.
        return None
    if FEEL_LIKE_OVERLOAD.search(clean):
        return None
    if LIFE_ADRIFT.search(clean) or FEEL_LIKE_MAIN_ANSWERS.search(clean):
        return None
    if EVENT_DONE.search(clean):
        return None
    if FEEL_LIKE_HOME_LOAD.search(clean):
        return None
    if FEEL_LIKE_WORTH.search(clean):
        return None
    if FEEL_LIKE_ROLE.search(clean) or FEEL_LIKE_COPE.search(clean):
        return None
    good = FEEL_LIKE_GOOD.search(clean)
    if (good and not _a_journey_not_progress(clean, good)
            and (_said_about_themselves(clean[:good.start()])
                 # "getting there" on its own is a progress report - the answer to "how's it
                 # going" - and it is easy to say without saying who it is about. The bare
                 # "get there" is a place: "how do i get there", "when i get there".
                 or (not clean[:good.start()].strip()
                     and good.group(0).startswith("getting")))):
        return "feel_like_good"
    # "Everything I do is wrong" only reads as a comparison when the line contains one: "i keep
    # messing everything up" names no "feel like", and reading it as one took main's worth reply
    # ("you're being harder on yourself than you'd be on a friend") and swapped in a week line.
    match = FEEL_LIKE.search(clean)
    if not match:
        return None
    if FEEL_LIKE_EVERYTHING.search(clean):
        return "against_me"
    if OTHER_FEELS_LIKE.search(clean):
        return None
    if not re.search(r"\b(?:i|im|i'm|i've|ive|me|my|myself|we|us)\b", clean[:match.end()]):
        return None
    if FEEL_LIKE_NOT_ENOUGH.search(clean):
        # "i feel like im letting everyone down" is the reader above's own line
        # (`LET_SOMEONE_DOWN`), and its pool answers the reason line after it better than the
        # "not enough" comparison does: "i forgot her birthday" was answered "there is always one
        # more thing that could have been done", where main's reading of it is about being hard
        # on yourself.
        if _letting_someone_down(clean):
            return None
        return "feel_like_not_enough"
    if FEEL_LIKE_LOAD.search(clean):
        return "feel_like_load"
    if FEEL_LIKE_LEFT.search(clean):
        if FEEL_LIKE_AT_HOME.search(clean):
            # "i feel like im invisible at home" is answered already, and better, by the reading
            # that hears being talked over ("Talking and getting nothing back wears a person
            # down"), so this one leaves it there.
            return None
        return "feel_like_left"
    if FEEL_LIKE_ADRIFT.search(clean):
        return "feel_like_adrift"
    if fallback._someone_else_minding(clean, clean.split()):
        # "i feel like my friends dont care about me" is a complaint about what people keep
        # doing, and that reading asks about it ("Do you want to work out what to say to them,
        # or is it more a case of letting off steam?"). The generic pool would say the mood
        # back instead, so the other reading keeps the turn.
        return None
    if not FEEL_LIKE_JUDGEMENT.search(clean[match.end():]):
        # The pool below names a misery back, which is only right when the tail says what the
        # person is measuring themselves against. Without a comparison the tail is a plain
        # state - "i feel like im pregnant", "i feel like im losing weight", "i feel like im
        # on holiday" - and a line about a bad week answers a word they never said.
        return None
    return "feel_like"


# "nothing is going right", "everything is going wrong": the whole week is the complaint, and
# the stock acknowledgement answered it before. The line has to be the person's own life (an
# "i", or a "this week" that dates it) so a line about a machine ("nothing works on this
# laptop") keeps whatever can fix it.
AGAINST_ME = re.compile(
    r"\b(?:nothing|nothing much) (?:is |ever |seems to )?(?:going|goes|worked|working) right\b|"
    r"\beverything (?:is |was |'s )?(?:going )?wrong\b|"
    r"\b(?:everything|it all) (?:is |was )?(?:falling apart|too much|a mess|on top of me)\b|"
    r"\bnothing (?:helps|works|goes right) (?:any ?more|at the moment|lately|these days)\b")


AGAINST_ME_SELF = re.compile(
    r"\b(?:i|im|i'm|i've|ive|me|my|we|us)\b|\b(?:this week|today|lately|at the moment|right now)\b|"
    # "everything is going wrong" is the whole line, and the whole line is their week.
    r"^(?:(?:and|so|but|and then) )?(?:everything|nothing)\b")


# The complaint a line makes is either the whole week or one thing in it. "everything is going
# wrong with the car" and "nothing is going right with this project" name the thing, and the
# week's pool ("Some weeks are like that...") answers a mood the person did not describe. The
# scopes below are the ones that are the week itself; anything else is a subject of its own, and
# an answer about a thing belongs to whoever can help with the thing.
AGAINST_ME_ITS_SCOPE = re.compile(
    r"\b(?:with|at|in|on|about)\s+(?:(?:the|a|an|this|that|these|those|my|our|his|her|their|"
    r"its)\s+)?([a-z']+)")


AGAINST_ME_THE_WEEK = frozenset("""
work life home house moment minute time day week month year today now everything anything all
thing things order place world universe general hand head top least most me him her them us
you it something nothing none everybody everyone
""".split())


# A feeling tacked onto the turn before. "my boss had a go at me" then "i just feel like i
# cant win": the "just" says the feeling is about the line they have just written, and the answer
# that met that subject a turn back ("Ask for a specific example first...") fits the pair better
# than naming the mood back at them - it was the answer a turn later, not the same answer twice.
# A feeling that opens a subject of its own ("i feel like a failure", or "i just feel like i cant
# win" as the first line) keeps its own reply.
JUST_A_CONTINUATION = re.compile(
    r"\b(?:just|still|also|anyway)\s+feel(?:s|ing)?\s+like\b|\b(?:and|so|but|then)\s+(?:i\s+)?"
    r"feel(?:s|ing)?\s+like\b")


def _a_feeling_riding_on_the_thread(clean, memory):
    """True when the comparison is about what they have just been saying."""
    if not JUST_A_CONTINUATION.search(clean or ""):
        return False
    if not isinstance(memory, dict) or not (memory.get("turns") or []):
        return False
    try:
        from ..memory import topics as remembered
        return bool(remembered.carried_topic(memory, clean))
    except Exception:  # noqa: BLE001 - a reading that fails leaves the reply with the pool
        return False


def _against_me(clean):
    """"nothing is going right" is a line about the week, not a thing to look up."""
    if not AGAINST_ME.search(clean):
        return None
    if not AGAINST_ME_SELF.search(clean):
        return None
    for found in AGAINST_ME_ITS_SCOPE.finditer(clean):
        if found.group(1).lower() not in AGAINST_ME_THE_WEEK:
            return None
    return "against_me"


FIRST_PERSON = re.compile(r"\b(?:i|im|i'm|me|my|mine|us|our|we)\b")
