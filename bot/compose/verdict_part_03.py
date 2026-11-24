"""Part 3 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re

from ..understanding.normalize import normalise
from . import A_STEP_ASK, pick, why
from ..memory import healing
from .verdict_part_01 import (
    _the_sign_words, A_BODY_IN_THE_LINE, MONEY_NOT_MET, MONEY_NOUN_WORDS, NOT_MONEY_PAY,
    A_COMPARISON, A_FIGURE, BOTH_LINES, CONDITION_LINES, DO_LINES, METHOD_OK_LINES,
    MET_CONDITION_LINES, MET_LINES, MONEY_TROUBLE_LINES, NO_LINES, CARE, HARD_NEWS,
    A_PERSON_THEY_KNOW, A_RELATION_TROUBLE, A_SYMPTOM_WORD, A_PLAN, A_DECISION_ASK, BODY_WORD,
    SOMEONE_ELSE, _reads_as_good_news, CONDITIONAL,
)
from .verdict_part_02 import (
    IMPERATIVES, OWN_LINES, _own_pattern, BACKSTOP_LINES, CARE_NORMAL, CARE_NORMAL_UNKNOWABLE,
    CARE_NOW_NORMAL, CONDITION_NORMAL, DO_NORMAL, HELPED_LINES, NOTHING_WARNED_NORMAL,
    ORDINARY_NORMAL, SOON_LINES, YES_LINES, REFER, A_BODY_WORD, A_THING_THEY_OWN, NAMES_A_CLINICIAN,
    NOT_TOLD_TO, ONE_OPTION, TESTING, THROW_AWAY, STATED_NO,
)


def _a_job_somewhere(reply):
    """True when any clause of a reply is an instruction, not only the first one.

    `opens_on_a_job` reads the opening because a bare "what do i do" wants the reply that starts
    with the job. The step a follow-up points at is not always the opening one: the boiler answer
    that ends "..." / "ok and what about the radiators, they're cold at the top" answers with
    "Radiators that are hot at the bottom and cold at the top have air in them: open the bleed
    valve at the top with a radiator key ...", which opens on a fact and carries its job after
    the colon. "and does that fix the pressure too" after it still means the bleeding, so the
    job has to be read wherever it is in the line.
    """
    flat = _flat(reply)
    if not flat:
        return False
    for clause in re.split(r"[:;.!?]|,?\s+and\s+", flat):
        words = _WORD.findall(clause.strip(" ,-"))
        if not words or words[0] not in IMPERATIVES:
            continue
        if len(words) > 1 and words[1] in ("me", "us"):
            continue
        if len(words) > 1 and words[1] in _AFTER_A_NOUN:
            continue
        return True
    return False


def _they_named_the_sign_themselves(call, memory):
    """True when the person's own line already says the sign the call is for."""
    words = _the_sign_words(call)
    if not words:
        return False
    said = _flat(_the_line_behind(memory) or "")
    return bool(words & set(re.findall(r"[a-z']+", said)))


def _a_doubt_about_money(memory):
    """True when the doubt this turn is about money, or "".

    Read off the person's own line one turn back, not off the answer: the answer over a money
    line is a knowledge card about rent or a card or a bill, and its own "what would matter is it
    getting worse" is the thing this replaces.
    """
    said = _flat(_last_person_line(memory) or "")
    if not said or len(said.split()) > 16:
        return ""
    words = set(_words(said))
    if not words & MONEY_NOUN_WORDS:
        return ""
    if not MONEY_NOT_MET.search(said):
        return ""
    if A_BODY_IN_THE_LINE.search(said):
        return ""
    if NOT_MONEY_PAY.search(said):
        return ""
    return said


def _is_a_comparison(said):
    """Whether the answer above quotes a usual figure for the person's own to be read against."""
    if A_FIGURE.search(said or ""):
        return True
    return _first(said, A_COMPARISON) is not None


OWN_PATTERN = re.compile("|".join(_own_pattern(line) for line in OWN_LINES),
                        re.IGNORECASE)


# A line that only takes a fact the person gave ("Got it - he shares with his sister", "Noted: your
# sofa smells of dog"), left open where the thing they said goes. `bot/memory/ack.py` writes those,
# so its own frames are what says which lines they are: a reader that guesses from "Got it" reads
# "Right, so that hasn't helped. How is it now" as an acknowledgement too, and that line has
# something to say.
_ACK_PATTERN = None


# How long a line may be and still be only an echo: `bot/memory/ack.py` keeps the thing they said
# to a clause or two, so anything longer has a tail of its own ("he shares with his sister - how's
# it going?" is nine).
ECHO_WORDS = 14


def takes_a_fact_back(said):
    """True when the line only says the bot heard, so the answer behind it is still the answer.

    "my son is 4 and wont sleep" / "he shares with his sister" / "any tips" was answered "Sure.
    What have you tried so far?", a plea thrown back at somebody the bot had just told what to do,
    because the acknowledgement sat between the ask and the answer it is about.
    """
    global _ACK_PATTERN
    if _ACK_PATTERN is None:
        from ..memory import ack
        frames = ack.FRAMES + ack.HABIT_TAIL + ack.GOING_TAIL + ack.EXPLAIN_TAIL
        _ACK_PATTERN = re.compile("|".join(_own_pattern(line) for line in frames), re.IGNORECASE)
    text = " ".join(str(said or "").split())
    if not text or not _ACK_PATTERN.match(text):
        return False
    # The acknowledgement carries the person's own words and nothing else: "Got it - you're 40"
    # taking "im 40" is one, and "Got it - so start with the wake-up time and give it two weeks"
    # is an acknowledgement that has gone on to answer, so the step in it must not be read past.
    words = re.findall(r"[a-z']+", text.lower())
    return len(words) <= ECHO_WORDS and not any(word in IMPERATIVES for word in words)


def _say(pool, memory, flat, **gaps):
    """One line from a pool of templates, chosen after its gaps are filled in.

    pick() drops the reply just given, but the pool holds "{Step}, and take it from there." and
    the reply just given was "Keep it plain, and take it from there.", so the two are never equal
    and a person asking twice got the same sentence twice running. Filling the gaps first is what
    lets the never-repeat rule see them.
    """
    rendered = list(pool)
    for name, value in gaps.items():
        for template, gap in ((name, "{%s}" % name),
                              (name[:1].upper() + name[1:], "{%s}" % (name[:1].upper() + name[1:]))):
            filled = value if gap == "{%s}" % name else value[:1].upper() + value[1:]
            rendered = [line.replace(gap, filled) for line in rendered]
    return pick(rendered, memory, flat)


def _a_report_line(said):
    """Whether the bot's own last line was the composer's report on the advice it had given.

    The report lines are spoken under whichever module proposes them (`greeting` under the floor),
    so the module name says nothing and the composer's own list of them does. A doubt two turns
    after the answer - "im 34 and i still bite my nails" / "ive tried everything" / "is that bad" -
    is about the nails, and the report in between is not the answer it is about.
    """
    try:
        from .fallback import is_a_report_reply
    except Exception:  # noqa: BLE001 - a reading that fails is a reading not made
        return False
    return bool(is_a_report_reply(said))


def _flat(text):
    return " ".join(str(text or "").lower().replace("\u2019", "'").split())


# Only a knowledge answer is read back. "im 6 weeks pregnant and cant keep anything down" is
# answered by a referral to a GP, and "should i be worried" after it must not be told "no": the
# answer to that line was already the careful one, and this composer has nothing to add to it.
READABLE = frozenset(("answers", "chat", "trouble", "fallback", "greeting"))


# A step is the instruction as the answer wrote it, and answers write them longer than a handful
# of words: "turn the boiler off at the wall switch" is eight, and "three times a week do
# sit-to-stands" opens with when it is done rather than with the verb.
# The lines this composer may not read a follow-up from: a safety answer has already said what to
# do, and a death, a grief or an emergency is not a topic to point back at ("do the first thing I
# said" after "ring 999" is the wrong sentence, and after a condolence it is worse).
UNREADABLE = frozenset(("safety", "urgent", "loss", "grief"))


# The module names a composer's line is spoken as. A composer line is the fallback module
# whichever helper wrote it, so the module name cannot tell one composer from another; the text
# has to be read when it matters (see `_last_reply`).
COMPOSED = frozenset(("greeting", "fallback"))


# The pools that rule on a doubt the person asked about, as opposed to the ones that talk about
# the answer it followed (NOTHING_WARNED_LINES), ask for more (FLOOR_LINES, NEUTRAL_ASK_LINES) or
# hand the question back. The arbiter reads this list (bot/modules/arbiter.py, `_reads_the_doubt`):
# on a bare doubt an entry that only inherits the topic stands down to a reply that reads the
# doubt, and this is what "reads" means - the composer saying what it thinks about the thing, in
# one of the pools that does that. A pool that gains a ruling line is read as one with no change
# in the arbiter; a note or a floor never is, however it is worded.
RULED_BY_THE_COMPOSER = (
    ORDINARY_NORMAL, CARE_NORMAL, CARE_NORMAL_UNKNOWABLE, CARE_NOW_NORMAL, DO_NORMAL,
    CONDITION_NORMAL, NOTHING_WARNED_NORMAL, NO_LINES, BOTH_LINES, DO_LINES, CONDITION_LINES,
    MET_LINES, MET_CONDITION_LINES, METHOD_OK_LINES, YES_LINES, BACKSTOP_LINES, SOON_LINES,
    HELPED_LINES, MONEY_TROUBLE_LINES,
)


def rules_on_the_doubt(said):
    """True when a reply is one of the composer's lines that rules on a doubt, for the arbiter.

    The pools carry no slots in the part that tells them apart - a {when} or {topic} comes later
    in the sentence - so the first 40 characters are compared, the way `fallback.is_a_hedge` reads
    its pools, and a pool that reflows its wording keeps working.
    """
    said = str(said or "").strip()
    if not said:
        return False
    head = said[:40].lower()
    return any(head == line[:40].lower() for pool in RULED_BY_THE_COMPOSER for line in pool)


# A follow-up asking what to do next is answered from the answer the person was given a turn
# ago. The step is in that answer and nowhere else, so a line that comes back to it carries a run
# of its words; an entry that shares the conversation's topic but none of those words is a
# different fact about the same subject, and answering with it reads as a change of subject.
RUN = 4


_WORD = re.compile(r"[a-z0-9']+")


# The words that follow a noun and never an instruction: "water at the front" is about water
# though `water` is a verb in IMPERATIVES, and an answer that opens on it is a diagnosis, not a job.
_AFTER_A_NOUN = frozenset("at in on from of for to with by near under behind over into about".split())


def opens_on_a_job(reply):
    """True when a reply opens on an instruction ("Ring or log in and ask why it went up").

    Read by the arbiter beside `carries_the_answer`, on the turn where a bare follow-up asks what
    to do next: an entry that opens on a job is already answering that question, so it keeps the
    turn over the step from the answer a turn ago. An entry that opens on a fact ("Five a day is
    400g", "The things that work: same wake-up time every day") is telling the person something
    else about the subject, and the step they asked for is in the answer they already have.
    """
    flat = _flat(reply)
    if not flat:
        return False
    head = re.split(r"[:;.!?]", flat, 1)[0].strip(" ,-")
    words = _WORD.findall(head)
    if not words or words[0] not in IMPERATIVES:
        return False
    if len(words) > 1 and words[1] in ("me", "us"):
        # "Tell me what has gone on, even roughly, and I will help you work out the first step"
        # opens on a verb from the list, but the job in it is not the person's: it asks them for
        # the thing, which is why "say" and "name" were left out of IMPERATIVES. After "my
        # youngest and my eldest fight all the time", "what do i do" was answered with that line
        # instead of the step the answer already had ("You've got it: Separate them first and deal
        # with it when everyone is calm"), so the person was asked to tell the bot what they had
        # just told it. "Tell the school the same day" is a real job and is untouched.
        return False
    return len(words) == 1 or words[1] not in _AFTER_A_NOUN


# A turn that only says the person was heard, with nothing about the thing itself: the echo the
# fallback hands back ("Got it - she likes pasta.", "Got it. Is there anything you'd like a hand
# with?", "Noted."). It is not the answer a follow-up reads, and it does not put the answer out of
# reach either: "my washer bangs" / "only when it spins" (echoed as "Got it. Is there anything
# you'd like a hand with?") / "is that bad" got a search hedge, though the washer answer was one
# turn back. One such turn is looked past and not a run of them, so a person who has moved on
# still gets the line that was just said.
PUNT_START = re.compile(r"^(?:got it|noted|ok(?:ay)?|alright|all right|right|fair enough|"
                        r"i see|makes sense|understood|sure|cool)\b", re.I)


PUNT_OFFER = re.compile(r"\b(?:is there anything|anything else|what else|let me know|"
                        r"anything (?:i|we) can do)\b", re.I)


PUNT_CHAT = re.compile(r"\b(?:good luck|sounds good|fair enough|nice one|lovely|alright then|"
                      r"ok then|well then|makes sense|hope (?:it|that) (?:goes|works))\b", re.I)


def _a_punt(last):
    """True for a bot turn that said nothing about the thing being discussed."""
    module = last.get("module")
    if module not in ("greeting", "fallback", "chat"):
        return False
    said = _flat(last.get("bot"))
    if not said or not PUNT_START.match(said):
        return False
    if module == "chat" and not PUNT_CHAT.search(said):
        # The chat pool also answers with something about the thing ("Keep it plain and separate:
        # one new food next to one they already eat...") and that is an answer, not an echo. Only
        # its goodbye and its nod count here.
        return False
    if PUNT_OFFER.search(said):
        return True
    # A question is something said, even a short one ("Right. What have you tried so far?"), so
    # only the echo and the bare nod are shrugs.
    if "?" in said:
        return False
    return len(said.split()) <= 8


def _skip_the_derived(turns, memory):
    """The turns to read when the last one was read off the answer behind it.

    A frequency line ("Every night, then. That is enough to get it looked at") and a healing line
    ("Most back pain is muscular and settles in two to six weeks", said of the card above it) are
    both taken from the answer before them rather than from anything of their own, so the card is
    what a doubt this turn is about. Both are skipped, and no other turn is.
    """
    if not isinstance(memory, dict) or len(turns) <= 1:
        return turns
    if memory.get("frequency_reply") or healing.derived(memory):
        return turns[:-1]
    return turns


def _the_news_just_before(memory):
    """Whether the turn before this ask was hard news, not a feeling to sit with.

    A comfort line that ends in a question is an offer about how the person is doing when the line
    before it was about them ("im feeling really low"): there is nothing more concrete to say than
    the first step of a bad day, so the question comes back. When the line before it was news that
    names a thing ("bailiffs turned up", "i got a letter about a court date"), the ask that follows
    is about the thing, and whoever read the news answers it.
    """
    if not isinstance(memory, dict):
        return False
    try:
        from .badnews import reads_as_bad_news
    except Exception:  # noqa: BLE001 - a reading that fails is a reading not made
        return False
    turns = memory.get("turns") or []
    turn = turns[-1] if turns and isinstance(turns[-1], dict) else {}
    said = " ".join(str(turn.get("user") or "").lower().split())
    return bool(said) and reads_as_bad_news(said)


# The words a line back to the person is made of. An echo is the bot saying the person's own
# point back to them, which is the right thing in a conversation and no answer at all:
# "my cat keeps bringing in mice" / "hes 2" / "is that normal" was read from "Got it - he's two",
# so there was nothing to give a verdict on and the question got the search hedge. What is left
# of an echo once these words and the person's own words are taken out is nothing.
ECHO_FILLER = frozenset("""
a an the and or so but then too that thats that's this it its it's is are was were be been
i we you he she they his her their our your yours mine theirs
my me us them him got get note noted right ok okay
sure yes yeah no not ah oh mm good fine well still just only also very really quite
know sounds thanks hope glad
have has had do did does for to of in on at with about from by as if
one two three four five six seven eight nine ten eleven twelve half twice both all some
""".split())


def _words(text):
    """The words of a line, lowercased and bare, for the echo test below.

    The apostrophe goes, so "he's two" and the person's "hes 2" are the same two words.
    """
    return [word.replace("'", "") for word in re.findall(r"[a-z0-9']+", str(text or "").lower())]


def _is_an_echo(turn):
    """True when the bot's line only says the person's own words back.

    Short on purpose: a long line has said something of its own even if it repeats a lot of the
    person's words (a paraphrase of what they described is an answer), so only a line of a dozen
    words or fewer that adds nothing is skipped.
    """
    said = _words(turn.get("bot"))
    theirs = set(_words(turn.get("user")))
    if not said or not theirs or len(said) > 12:
        return False
    return all(word in ECHO_FILLER or word in theirs for word in said)


# The words a recap is made of on top of the answer it quotes: the lead-in, and the words for
# saying the same thing again ("Same as before: ..."). A recap adds nothing of its own, so the
# only words allowed outside the answer above are these.
RECAP_FILLER = frozenset("""
thing things one ones first next step steps again before said same short version part bit
here that this it its is are was the a an and or of to for in on at with about from
""".split())


def _is_a_recap(turn, before):
    """True when the bot's line is the answer above, said shorter: a step quoted out of it.

    The quote is shorter than the card it came from and holds no word the card does not, apart
    from the lead-in ("The thing to do first:") and the words for saying it again. A line that
    brings a word of its own is an answer of its own, however much it repeats.
    """
    said = _words(turn.get("bot"))
    had = set(_words(before.get("bot")))
    if not said or not had or len(said) >= len(had):
        return False
    if before.get("module") != "answers":
        return False
    return all(word in had or word in RECAP_FILLER or word in ECHO_FILLER for word in said)


def _last_line_that_named_a_call(memory):
    """The last line when the answer the person is asking about named somebody to ring, or "".

    A safety answer is the first case - "my cat is having trouble breathing" / "is that serious"
    came back as the search hedge, because the verdict reading only reads a knowledge answer and
    a safety line is not one. Another module hands a line on with a call in it too: "my baby has
    a rash on her cheeks" is answered "Your health visitor or the 111 line will talk it through
    with you today", and the verdict question after it has the same answer. A knowledge answer
    never comes here - its own reading above is better than a yes - and a line that named nobody
    has no call to point back at.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return ""
    last = turns[-1]
    if not isinstance(last, dict):
        return ""
    if last.get("module") == "answers":
        return ""
    said = _flat(last.get("bot"))
    if not said or (_first(said, CARE) is None and REFER.search(said) is None):
        return ""
    return said


# The words that make a named call a call for today. A named ordinary professional is not one of
# them: "i bleed when i brush my teeth" is answered with a dentist, and "ringing is not an
# overreaction here, it is the whole point of it" over a dentist is a 999-shaped over-reaction.
URGENT_CALL = re.compile(
    r"\b(?:999|911|112|a&e|accident and emergency|ambulance|111|out of hours|straight away"
    r"|right away|today|tonight|do not wait|dont wait|immediately)\b", re.I)


# A sentence that names the whole answer as an emergency, rather than naming a condition that
# would be one. The order is already given, so it is a call for now with no time word needed:
# "That's an emergency: ring 999 or 911", "That's an ambulance job", "Treat this as an emergency".
EMERGENCY_ORDER = re.compile(
    r"^\W*(?:that's|that is|this is|it's|it is)\s+(?:an?\s+)?(?:emergency|ambulance\b(?: job)?)"
    r"|^\W*treat (?:this|that) as (?:an? )?(?:emergency|ambulance)", re.I)


# The other way an answer gives the order in its opening clause: "Ring 999 or 911 and stay on the
# line." It is read only where nothing after it fences it - "Ring 999 if he goes blue" is the
# answer's condition, not its instruction, and reading that as a call for now gives a doubt on top
# of it the emergency reading for a thing the person may not have.
EMERGENCY_CALL_OPEN = re.compile(r"^\W*(?:ring|call|dial|phone)\s+(?:999|911|112|an ambulance)\b", re.I)


def _last_person_line(memory):
    """The person's own last line, skipping the echoes a doubt ask follows."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return ""
    for last in reversed(turns):
        if not isinstance(last, dict):
            return ""
        said = _flat(last.get("user"))
        if not said:
            continue
        return said
    return ""


def _the_worst_thing_they_said(memory):
    """Whether the thing this turn is a doubt about is a loss or a diagnosis, not a fault.

    The person's own last line decides it: "my dad has cancer" is the thing they brought, and
    "is that bad" on top of it is about that. A body in the line is still a body, so the doubt
    path's own readings come first wherever there is something to read.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ""
    for last in reversed(turns):
        if not isinstance(last, dict):
            return False
        said = _flat(last.get("user"))
        if said:
            return said if HARD_NEWS.search(said) else ""
    return ""


def _as_written(line):
    """The line as it was meant, for the ask patterns that read it: (spelled right, said out).

    "wat shud i cook 2nite" is "what should i cook tonight", and a misspelling is the person's
    ordinary way of writing rather than a rare slip: the understanding engine repairs every line
    and the composer was reading the raw text, so the same sentence spelled differently took two
    different routes through this file. The first return is that repair with the words in the
    order they were typed and the punctuation kept (`plain`); the second is the fuller reading
    (`norm_text`), which also expands "gonna" and "im". A line with nothing to repair comes back
    as it went in, and a reading that fails leaves the arms exactly as they were.
    """
    text = _flat(line)
    if not text:
        return "", ""
    try:
        read = normalise(text)
    except Exception:  # noqa: BLE001 - a reading that cannot run adds nothing
        return "", ""
    return _flat(read.get("plain") or ""), _flat(read.get("norm_text") or "")


def _a_thing_they_own(memory):
    """The noun for the thing whose answer this doubt is about, or "" for a body or a person.

    Read off the line the answer replied to, so it is the subject the person brought and not a
    word in the doubt, and only when that line names no body: "my boiler is making a knocking
    noise" is a machine, "my knee clicks" is not.
    """
    line = _the_line_behind(memory)
    if not line:
        return ""
    low = _flat(line)
    if A_BODY_WORD.search(low):
        return ""
    found = A_THING_THEY_OWN.search(low)
    return found.group(0).lower() if found else ""


def _a_person_they_know(memory, said):
    """The person whose situation this doubt is about, or "" when it is their body or nobody.

    Read off the line the answer replied to, and only when that line is about contact, company or
    quiet rather than a symptom: "my mum is 79 and lives on her own" is a week, "my baby is not
    feeding" is not. A fenced care in the answer ("if they seem low for weeks, help them see a GP")
    is the answer's own later step, not a referral now, so the verdict points at both halves.
    """
    line = _the_line_behind(memory)
    if not line:
        return ""
    low = _flat(line)
    if A_SYMPTOM_WORD.search(low):
        return ""
    if not A_PERSON_THEY_KNOW.search(low) or not A_RELATION_TROUBLE.search(low):
        return ""
    return "person"


def _the_line_behind(memory):
    """The person's own line that the answer this turn is a follow-up to replies to, or "".

    Read with the same walk `_last_reply` does, so the two agree about which answer is being
    followed up: a chat line of this composer's own is stepped past, and a safety answer ends it.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return ""
    # The same skip `_last_reply` makes: a frequency or healing line is about the turn before it,
    # so the person's line this turn follows is the one the trouble answer replied to, not "its
    # every night". Without this the two walks disagree and "is it worth seeing someone" loses the
    # referral in the cough answer.
    turns = _skip_the_derived(turns, memory)
    for index in range(len(turns) - 1, -1, -1):
        last = turns[index]
        if not isinstance(last, dict):
            return ""
        module = last.get("module")
        if module in UNREADABLE:
            return ""
        if module == "chat" and OWN_PATTERN.search(_flat(last.get("bot"))):
            continue
        if _is_an_echo(last):
            continue  # a line said back is not an answer: the line behind it is the one to read
        if A_STEP_ASK.match(_flat(last.get("user")) or "") and module != "answers":
            # Asking for a step is not a subject of its own, so it is not the line a doubt about
            # the answer is about (see the same skip in `_last_reply`, including why a step the
            # knowledge base answered is not stepped past).
            continue
        if index and _is_a_recap(last, turns[index - 1]):
            # A step quoted out of the card above was asked for, not asked about: "my laptop is
            # full" / "what should i do first" / "is that safe" is a doubt about the card, and
            # the ask-for-a-step in between is not the thing the doubt is about. The same walk
            # `_last_reply` makes, so the two agree on which answer is being followed up.
            continue
        if module in READABLE:
            return _flat(last.get("user"))
        return ""
    return ""


def _the_plan_they_brought(memory, back=2):
    """The person's own plan or choice among their last few lines, or "".

    A plan is rarely the line immediately before the check. "im thinking of getting a dog" /
    "but i work all day" / "is that fair" is one thought in three lines, and the line behind the
    check is the *detail*, which no plan reader matches - so the arms below stood aside and the
    acknowledgement pool ended the conversation ("Sounds good."). Two lines is the reach: the plan
    and one line said about it. Further back and the check belongs to whatever was said last.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ""
    seen = 0
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            continue
        said = _flat(turn.get("user"))
        if not said:
            continue
        seen += 1
        if seen > back:
            break
        if A_PLAN.search(said) or CONSIDERING.search(said):
            return said
    return ""


A_CHECK_ON_A_PLAN_LINES = (
    "Say which part you are unsure about and we can weigh it up together.",
    "Tell me the bit that is nagging you and I will go through it with you.",
    "Which part of it is the one you keep coming back to? That is usually the part worth settling "
    "first.",
    "Put the two sides next to each other and the answer usually shows itself: what it costs you, "
    "and what it gives you. Which one is it for you?",
)


# The handful of words a check on a plan is made of: "is that fair", "is that right", "does that
# make sense", "does that sound ok". They are the same ask as "is that ok" - the person putting
# their own plan before somebody before they act on it - and they are not a question about how
# dangerous or how usual anything is, so the severity pools below are the wrong answer to them:
# "getting a dog / but i work all day / is that fair" was told "Nothing in that sounded like a
# warning sign", which is a ruling on a dog rather than on a fair working day.
A_CHECK_ON_A_PLAN = re.compile(
    r"^(?:and |so |but )?(?:is|was|does|did|do) (?:that|this|it) "
    r"(?:be |sound |look |seem )?"
    # "right" is deliberately not here. "is that right" after the bot has said something about
    # the world is the person checking the claim ("Cornwall in May ... the weather is usually
    # decent" / "is that right" -> "That's right."), and the plan pool's "that is yours to
    # decide" answers the wrong question. "fair" and "make sense" are asks about the plan itself.
    # "sensible" and "reasonable" are deliberately not here: a check on a plan written that way
    # already has a good answer of its own ("im going to ask my boss for a pay rise" / "does that
    # sound sensible" -> "Yes, that is a reasonable way to do it - wanting to ask your boss for a
    # pay rise is worth doing"), and this gate would take the turn from it and hand back the
    # general question instead.
    r"(?:fair|ok|okay|alright|all right|fine|"
    r"make (?:any )?sense|sound (?:ok|okay|fine|fair))(?: then| though)?$")


# A plan is not a complaint. "im thinking of getting a cat" then "is that bad" asks whether the
# plan is a bad idea, and the answer it follows is a shopping list ("plus a vet visit booked for
# the first week") whose "vet visit" is an errand, not a referral about an ache. Only getting or
# buying something counts, so "i want to lose weight" and "im going to be sick" keep their reads.
CONSIDERING = re.compile(
    r"\b(?:thinking (?:of|about)|considering|planning (?:to|on)|looking to|hoping to|"
    r"(?:i|we) (?:really )?(?:want|need|fancy)|want(?:ing)? to)\b[^.]{0,30}?"
    r"\b(?:get|getting|buy|buying|adopt|adopting|rescue|rescueing|book|booking)\b", re.I)


def _considering(memory):
    """Whether the line before this one is about a thing the person is considering getting."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            continue
        said = _flat(turn.get("user"))
        if said:
            return bool(CONSIDERING.search(said))
    return False


def _the_last_line_was_mine(memory):
    """True when the bot's last line is a line of this composer's, whichever module filed it.

    The pools that answer a question a second time ("Same answer as a moment ago: nothing in what
    I said was a warning sign") are only true when the bot itself said the answer the first time.
    Reading the words alone is not enough, because these lines are templates: `{Step} first.` fits
    any sentence that ends in that word, and a knowledge card that says "the last resort, not the
    first" is not a verdict of mine.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    for last in reversed(turns):
        if not isinstance(last, dict):
            return False
        module = last.get("module")
        if not module:
            continue
        return module == "chat" or module in COMPOSED
    return False


def _last_module(memory, past_the_nod=False):
    """The module that wrote the answer `_last_reply` reads, or "" if there is not one."""
    punt_module = ""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return ""
    turns = _skip_the_derived(turns, memory)
    for index in range(len(turns) - 1, -1, -1):
        last = turns[index]
        if not isinstance(last, dict):
            return punt_module
        module = last.get("module")
        if module in UNREADABLE:
            return punt_module
        if module == "chat" and OWN_PATTERN.search(_flat(last.get("bot"))):
            continue
        if _a_report_line(last.get("bot")):
            continue  # the composer's report on the answer: the answer behind it is the module
        if module in COMPOSED and why.is_a_reason_line(_flat(last.get("bot"))):
            continue
        if module in READABLE and takes_a_fact_back(last.get("bot")):
            continue  # only taking a fact back: the answer behind it is the module to read
        if A_STEP_ASK.match(_flat(last.get("user"))) and module != "answers":
            continue  # a step ask is not a subject of its own: same walk as `_last_reply`
        if _a_punt(last):
            # Same walk as `_last_reply`.
            if not past_the_nod or punt_module:
                return module if not past_the_nod else punt_module
            punt_module = module
            continue
        if _is_an_echo(last):
            continue
        if index and _is_a_recap(last, turns[index - 1]):
            continue  # a step quoted out of the answer above is that answer's module
        if module in READABLE:
            if punt_module and module != "answers":
                return punt_module
            return module
        return punt_module
    return punt_module


# "is that bad" after a line about the person's own habit or mood is a question about them, and
# the floor above answers it. After a line about the world it is a different question: "my hedge
# is dying" / "is that bad" is not "what does it take out of your week", and neither is
# "im 52 and nobody will hire me" - a state or somebody else's behaviour is not a doing of theirs.
# What somebody *has* is not what they do, and the difference matters: "i have a lump in my
# breast" matched this and the backstop answered a lump with "I wouldn't call it bad ... what does
# it take out of your week", which is the one thing a person must not be told. The possession
# verbs are excluded with the copula, so the floor stays on lines about the person's own days.
OWN_DOING = re.compile(
    r"^i\s+(?!am\b|m\b|'m\b|have\b|had\b|havent\b|got\b|ve\b|need\b|want\b"
    r"|found\b|noticed\b|spotted\b|saw\b|seen\b|might\b|may\b|could\b|probably\b)"
    r"[a-z']+\b", re.I)


# A plan that can hurt is not a plan to weigh. The person states it, then checks it, and the
# doubt path used to hand back a shrug or a yes: "stop taking my antidepressants" / "is that ok"
# was answered "Nothing in that sounded like a warning sign - so yes, it is fine", which takes
# back the answer before it ("Keep taking it until a pharmacist, nurse or GP tells you to stop").
# Five families, each one a thing that injures somebody when it goes wrong, so an ordinary plan
# is untouched: an engine or a fire in a space with no chimney, a medicine somebody else
# prescribes, mains electricity, a blade with the guard off, and a job at height or one that
# brings a structure down.
CAN_HURT = (
    # Carbon monoxide first, because it is the one that kills without any sign: an engine or a
    # charcoal fire running in a garage, a shed, a tent or any room with the door shut.
    ("carbon monoxide", re.compile(
        r"\b(?:car|engine|van|generator|mower|bbq|barbecue|charcoal|stove)\b"
        r"(?:\W+\w+){0,4}?\W+(?:running|left\s+on|on|lit|going|burning)\b", re.I),
     re.compile(r"\b(?:garage|shed|indoors?|inside|tent|room)\b", re.I)),
    # Stopping, doubling, halving or skipping a medicine: "stop my insulin", "double the dose",
    # "stop taking my antidepressants", "cut my tablets in half". The medicine has to be what is
    # being stopped - "the pill stopped working" is a report about the pill, not a plan of the
    # person's, and the window after the verb is what keeps the two apart.
    ("a medicine", re.compile(
        r"\b(?:stop|stopping|quit|quitting|come\s+off|coming\s+off|double|doubling|halve|halving|"
        r"skip|skipping|cut\s+(?:it\s+)?(?:in\s+half|down)|take\s+more|up\s+the\s+dose)\b"
        r"(?!\s+(?:working|helping|hurting))"
        r"(?:\W+\w+){0,4}?\W+(?:insulin|antidepress\w*|antibiotic\w*|medication|medications|"
        r"meds|tablets?|pills?|statins?|steroids?|inhaler|epipen|epi\s*pen|"
        r"blood\s+pressure\s+(?:tablets?|meds?)|dose|dosage|prescription)\b", re.I), None),
    # Mains electricity and gas, done by hand: "wire the socket myself", "fit the fuse box",
    # "can i fix the boiler myself".
    ("the mains", re.compile(
        r"\b(?:rewire|re-wire|wire\s+(?:it|up|the\s+socket|a\s+socket|the\s+lights?)|"
        r"fit\s+(?:a\s+|the\s+)?(?:socket|fuse\s*box|consumer\s+unit)|"
        r"move\s+(?:a\s+|the\s+)?(?:socket|fuse\s*box)|"
        r"(?:socket|fuse\s*box|consumer\s+unit|wiring|boiler)\b(?:\W+\w+){0,4}?\W+"
        r"(?:myself|ourselves|himself|herself))\b", re.I), None),
    # A blade or a saw with the guard off, or in front of the eyes with nothing over them.
    ("that blade", re.compile(
        r"\b(?:angle\s+grinder|grinder|chainsaw|chain\s+saw|circular\s+saw|table\s+saw|"
        r"chop\s+saw|bench\s+saw|saw)\b", re.I),
     re.compile(r"\b(?:no\s+guard|without\s+(?:the\s+|a\s+|its\s+)?guard|guard\s+off|"
                r"took\s+(?:the\s+|its\s+)?guard\s+off|no\s+goggles|without\s+goggles)\b",
                re.I)),
    # A job at height, or one that brings a structure down on the person doing it. The doing has
    # to be theirs: "moss on the roof" and "my knee is not good on a ladder" are about the roof
    # and the knee, not a plan, and they keep their card.
    ("a job like that", re.compile(
        r"\b(?:take|taking|knock|knocking|pull|pulling|remove|removing)\s+(?:the\s+|my\s+|our\s+)?"
        r"(?:chimney|wall|ceiling|lintel)\b(?:\W+\w+){0,3}?\W+(?:out|down|off)\b"
        r"|\b(?:on\s+the\s+roof|up\s+(?:a|the)\s+ladder|on\s+(?:a|the)\s+ladder)\b"
        r"(?:\W+\w+){0,3}?\W+(?:myself|ourselves|alone|on\s+my\s+own|by\s+myself)\b"
        r"|\b(?:myself|ourselves)\b(?:\W+\w+){0,4}?\W+"
        r"(?:on\s+the\s+roof|up\s+(?:a|the)\s+ladder|off\s+the\s+ladder)\b", re.I), None),
)


# A line that already names the tradesperson is a plan to hire one, which is what this pool
# says, so it stands aside rather than handing the advice back.
NAMES_A_TRADE = re.compile(
    r"\b(?:electrician|plumber|builder|roofer|chimney\s+sweep|gas\s+safe|engineer|"
    r"handyman|scaffold\w*)\b", re.I)


# A sentence in the answer that tells the person to keep doing the thing, stop it, or ask first.
# It is what makes the warning the answer's own rather than a new one over the top of it.
A_KEEP_OR_STOP = re.compile(
    r"\b(?:keep|carry\s+on|stopping|stop|do\s+not|don\u2019t|dont|never|ask|check|review|"
    r"until|rather\s+than)\b", re.I)


# Each pool says the same thing in its own words: not on your own, here is what it does, and here
# is the person to ask. None of them is an alarm - what the person did was check, and the check
# is right - so they open on the check being right rather than on the danger.
THE_PLAN_CAN_HURT_LINES = {
    "carbon monoxide": (
        "Good that you checked. Not with the engine running in there, though - that is carbon "
        "monoxide, and it puts people to sleep before they notice it. Run it outside, and if the "
        "door has to stay shut, have somebody with you.",
        "Right to ask. That one gives off carbon monoxide, and a garage or a tent holds it: do it "
        "out in the open, or with the doors wide open and somebody knowing you are in there.",
        "Worth asking: an engine or a fire in a closed space is carbon monoxide, and that is the "
        "kind that takes people quietly. Move it outside before you start it.",
    ),
    "a medicine": (
        "Not without the person who prescribes it: stopping it, doubling it or cutting a tablet "
        "in half is the one change they want to hear about first. Ring the surgery, a pharmacist "
        "or 111 and ask what to do today.",
        "That one goes through whoever prescribes it - a change of dose or a stop is not "
        "something to work out alone. Ring the surgery or a pharmacist, and keep taking it as "
        "written until they say otherwise.",
        "Ask the prescriber before you change it, and carry on as written until then. A "
        "pharmacist will answer this the same day, and 111 will at night.",
    ),
    "the mains": (
        "Not by hand: that is mains, and it is not a thing to learn on. Get a registered "
        "electrician in - a socket or a fuse box done wrong is the sort of fault that waits.",
        "Not on your own. Mains wiring has to be done and signed off by somebody registered, and "
        "the part that goes wrong is inside the wall where you cannot see it.",
    ),
    "that blade": (
        "Not with the guard off. That guard is the part that comes between you and the blade, "
        "and a saw does not give you a second go: put it back, or get somebody who has one.",
        "Put the guard back on first, and goggles too - that is the half of the job that keeps "
        "your hands the shape they are.",
    ),
    "a job like that": (
        "Not from a ladder on your own, and not by taking it down yourself: that wants somebody "
        "who has done it before, and a second pair of hands. Get a builder or a chimney sweep "
        "round, and let them say what it is.",
        "A job like that is one to hand over rather than climb to - a ladder on your own is how "
        "people get hurt at home. Ring somebody who does it for a living.",
    ),
}


def _the_plan_can_hurt(said):
    """The family of harm the plan behind the check is in, or None.

    An ordinary plan is untouched: this only answers a doubt when the line states one of the five
    things that injure people, and each family needs both halves - the act and the thing that
    makes it dangerous. "stop taking my antidepressants" is the medicine; "stop taking the bins
    out on tuesday" is nothing.
    """
    if not said or NAMES_A_TRADE.search(said):
        return None
    for family, act, guard in CAN_HURT:
        if act.search(said) is None:
            continue
        if guard is not None and guard.search(said) is None:
            continue
        return family
    return None


def _the_answer_already_warned(said):
    """The warning the answer above already gave, when it gave one, else "".

    "stop taking my antidepressants" / "is that ok" follows an answer that says "Keep taking it
    until a pharmacist, nurse or GP tells you to stop". The best reply is that sentence, not a
    new one, so a warning the answer already carries is handed back rather than rewritten.
    """
    if not said or not NAMES_A_CLINICIAN.search(said):
        return ""
    for sentence in re.split(r"(?<=[.!?])\s+", said):
        sentence = sentence.strip()
        if not 6 <= len(sentence.split()) <= 40:
            continue
        if NAMES_A_CLINICIAN.search(sentence) is None:
            continue
        if A_KEEP_OR_STOP.search(sentence) is None:
            continue
        return sentence.rstrip(" .") + "."
    return ""


def _about_the_person(memory):
    """The line the ask follows, when it opens on the person: "i have a lump", "ive a cough".

    A dying hedge or a hiring market is somebody else's business, and a verdict question about
    one is not the person's own ("is that bad" after "my hedge is dying" is a question about the
    hedge). What somebody has or noticed is theirs, and it may be a lump - which is why this is a
    looser test than `_own_doing` and only ever feeds the pool that claims nothing.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or len(turns) < 1:
        return False
    for last in reversed(turns):
        if not isinstance(last, dict):
            return False
        if _is_an_echo(last):
            continue
        said = _flat(last.get("user"))
        if not said or len(said.split()) < 3:
            return False
        return re.match(r"(?:i\s|ive\s|i've\s|i\u2019ve\s)", said, re.I) is not None
    return False


def _own_doing(memory):
    """The line the verdict ask follows, when it is about something the person does themselves."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or len(turns) < 1:
        return False
    for last in reversed(turns):
        if not isinstance(last, dict):
            return False
        if _is_an_echo(last):
            continue
        said = _flat(last.get("user"))
        return bool(said) and len(said.split()) >= 3 and OWN_DOING.match(said) is not None
    return False


def _a_plan_or_a_choice(memory):
    """The line the doubt follows, when it is the person's own plan, choice or wish.

    "is that ok" after a plan is not a symptom check and there is no answer to read it out of, so
    without this the doubt path stands aside and the ack pool reads "ok" as a nod. Anything with a
    body in it is somebody else's reading ("should i get my mole checked" has an answer in the
    knowledge base and a verdict in it), so it is left alone here, as is a line about another
    person.
    """
    said = _flat(_the_line_behind(memory))
    if not said or not (A_PLAN.search(said) or A_DECISION_ASK.search(said)):
        return False
    words = _words(said)
    return not any(word in BODY_WORD for word in words) and not any(
        word in SOMEONE_ELSE for word in words)


def _good_news(memory):
    """The line the verdict ask follows, when it is news that something went well.

    "i got the job" / "is that bad" was met with "How long has it been going on, and what would
    you like to do about it?", which reads as if the job were an illness. A floor that asks how
    long it has been going on only belongs over a condition; news of a thing that went well is
    not one, and it keeps whatever the composer had for it.
    """
    if _reads_as_good_news is None:
        return False
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    for last in reversed(turns):
        if not isinstance(last, dict):
            return False
        if _is_an_echo(last):
            continue
        said = _flat(last.get("user"))
        return bool(said) and _reads_as_good_news(said)
    return False


# A first-person past form: the event it names has happened and finished. Only the common ones -
# this is a shape test, not a vocabulary, and anything it misses keeps the floor it always had.
OVER_VERB = re.compile(
    r"\bi\s+(?:\w+ed|did|ran|got|went|came|made|took|won|bought|wrote|sent|met|found|gave|had|"
    r"kept|left|put|saw|spoke|sold|paid|drove|flew|finished|passed|booked|handed|signed|told|"
    r"started|stopped|began|broke|lost|held|built|caught|chose|felt)\b")


# ...unless the line says it is still going on: a state that repeats or continues is a thing a
# floor may ask about, however it is put.
STILL_GOING = re.compile(
    r"\b(?:yet|still|again|every (?:day|night|week|morning|time)|keeps?|always|constantly|"
    r"anymore|any more|since|for (?:weeks|months|years|days)|all the time|at the moment|"
    r"now|these days|lately)\b")


def _an_event_that_is_over(memory):
    """The line the verdict ask follows, when it is about something that happened and finished.

    "i finished my essay" / "is that bad" was met with "What would you like to do about it, and
    how long has it been like that?", which asks a person how long their essay has been going on.
    A floor that asks how long is for a state, so a finished event keeps whatever the composer
    had for it.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    for last in reversed(turns):
        if not isinstance(last, dict):
            return False
        if _is_an_echo(last):
            continue
        said = _flat(last.get("user"))
        if not said or STILL_GOING.search(said):
            return False
        return OVER_VERB.search(said) is not None
    return False


def _nothing_to_be_long_about(memory):
    """True when the floor's "how long has it been going on" would be asked of no such thing.

    Two shapes: news that went well ("i got the job", read by the shared good-news reading) and
    an event that has finished ("i finished my essay"). Neither is a condition, and both keep
    what the composer had for them instead of being asked how long they have lasted.
    """
    return _good_news(memory) or _an_event_that_is_over(memory)


def _first(text, words):
    """Where the first of these words sits in the text, read case-blind.

    A knowledge answer is written as sentences and starts them with a capital: "See a GP if the
    arm is weak or numb" carried the referral that answers "is that bad", and a cue written
    "see a gp" never saw it, so the arm got "Alright then - good luck with it"."""
    text = str(text or "").lower()
    best = None
    for word in words:
        at = text.find(word)
        if at >= 0 and (best is None or at < best):
            best = at
    return best


def _a_throw_away(said):
    """The thing the answer told the person to get rid of, and whether it was written as a test.

    "If milk smells sour, bin it" is not that: the answer is a rule for testing the milk, and a
    bare "is that bad" on top of it is a question about the rule, not a report that the milk is
    off, so the same fence `_unconditional_care` uses stands this reading down.
    """
    said = str(said or "")
    for match in THROW_AWAY.finditer(said):
        before = said[:match.start()]
        if NOT_TOLD_TO.search(before) or ONE_OPTION.search(before):
            continue
        sentence = before.split(".")[-1]
        action = match.group(0)
        action = action[0].upper() + action[1:]
        # The fence is the one the throw-away hangs off, not any "when" in the list of signs it
        # is reaching past: "flesh that stays dented when you press it ... means bin it" is a
        # verdict, while "if milk smells sour, bin it" is a test.
        if TESTING.search(sentence) or CONDITIONAL.search(sentence.split(",")[-1]):
            return action, True
        return action, False
    return None, False


# The answer's rule names a sign - "if milk smells or tastes sour" - and the person who has
# already said that sign is not asking what the test is: "my milk has gone sour" was given "Bin
# it if it has actually turned. The test is the answer", which is a step behind the answer they
# can already see. Asking *how* to tell is the row that wants the test back.
SIGN = re.compile(r"\b(?:sour|off|mouldy|moldy|curdled|smelly|smells|stinks|stinking|fizzy|"
                  r"rancid|turned|slimy|furry|green|black|gone bad|gone off|past it)\b", re.I)


ASKING_HOW_TO_TELL = re.compile(r"\b(?:how do i (?:know|tell|check)|how can i tell|how to tell|"
                               r"how do you tell|how do i spot|what should i look for|"
                               r"what do i look for|what should i check|is it still (?:ok|okay|fine))\b",
                               re.I)


def _the_person_line(memory, said):
    """The person's own last line, the one this doubt is a doubt about."""
    said = str(said or "").strip()
    for turn in reversed(list((memory or {}).get("turns") or [])):
        line = str(turn.get("user") or "").strip()
        if line and line != said:
            return line
    return ""


def _said_no(said):
    """The answer's own sentence saying the thing is not safe, or None.

    Read sentence by sentence, because the no is often not the opening: "There is no safe number
    of drinks before driving. The England and Wales limit is 35 micrograms ..." puts the verdict in
    its first sentence and the numbers after it. The sentence is handed back as it was written, so
    the reply repeats the answer rather than making a new claim about how serious the thing is.
    """
    for sentence in re.split(r"(?<=[.!?])\s+", str(said or "")):
        if STATED_NO.search(sentence) is not None:
            sentence = sentence.strip().strip("\"'\u201c\u201d").strip()
            if sentence:
                # The full stop stays: the pools above put the answer's sentence in the middle of
                # their own, so "driving What to do instead" would read as a run-on.
                return sentence.rstrip(".") + "."
    return None
