"""Part 10 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import ack
from . import (why)
from .badnews import (reads_as_bad_news)
from .goodnews import (reads_as_good_news)

from .fallback_data import (
    ANIMALS,
    ASK_ONLY,
    BARE_FOLLOW_UP_REPLIES,
    BODY_PARTS,
    BODY_WORD_FOR_A_THING,
    FORECAST,
    FORECAST_A_FALL,
    FORECAST_BODY_WORDS,
    FORECAST_HE_SHE,
    FORECAST_I_ASK,
    FORECAST_ILL,
    FORECAST_OFF_THEIR_FOOD,
    FORECAST_POOLS,
    FORECAST_RELATION,
    FORECAST_STRUGGLE,
    GREETING_WORDS,
    HEALTH_WORDS,
    HEDGE_POOL,
    HELP_ALREADY,
    NEUTRAL,
    NOT_AN_ANSWER,
    NOT_A_NAME,
    PARTICLE,
    POINTING,
    PRAISE,
    PUNT,
    QUESTION_WORDS,
    RULED_OUT_DETERMINER,
    SAME_AGAIN, SYMPTOM_WORDS,
    UNKNOWN,
    UNKNOWN_WEIRD_BARE,
    UNKNOWN_WORRY,
    VIEW_ONLY_WORDS,
    WORD_ANYWHERE,
    _ECHO_FILLER,
    _THREAD_PEOPLE,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    WORDING_SOMEONE,
)
from .fallback_part_01 import (
    FEELING_SAID, WEIRD_ASK, _worry_is_about_the_body, _plain,
)
from .fallback_part_02 import (
    _nothing_but_the_ask, _the_line_before, _without_the_idioms, ALREADY_SAID_OFF, KEEP_IT_RUNNING,
    SMOKE_ABOUT, SWITCH_OFF_ADVISE, SWITCH_OFF_ALREADY, SWITCH_OFF_ASK, SWITCH_OFF_BATTERY,
    SWITCH_OFF_FAULT, SWITCH_OFF_GET_OUT, SWITCH_OFF_THINGS, _reads_as_heavy_news,
    _thread_is_about_a_pet, _thread_is_about_someone_else, UNKNOWN,
)
from .fallback_part_03 import (
    NOT_A_NAME, _thread_is_about_a_person,
)
from .fallback_part_09 import (
    A_DOUBT_IN_FRONT, WORDING_ASKS, WORDING_SAYS, WORDING_TELL, _yours,
)


def _the_weird_ask_pool(clean, memory):
    """The pool for "is that weird / normal", or None when the line is a question of fact.

    The reassurance pool already answers "am i overreacting", and this is the same ask in the
    words people use for it. It is kept apart from `_reads_as_worry` because it needs the thread:
    "is that normal" on its own is a question of fact, and only the feeling before it makes it
    about them. Asked as the first thing in a chat with nothing after it, there is no feeling and
    no subject either, so it gets the question the pools should have asked ("weird in what way"),
    which is the same shape as a view asked for with nothing behind it.
    """
    found = WEIRD_ASK.search(clean)
    if not found:
        return None
    memory = memory if isinstance(memory, dict) else {}
    if _worry_is_about_the_body(clean, clean.split()) or _thread_is_about_the_body(memory):
        return None
    if FEELING_SAID.search(clean) or FEELING_SAID.search(_the_line_before(memory)):
        return UNKNOWN_WORRY
    if not _the_line_before(memory) and _nothing_but_the_ask(clean, found):
        return UNKNOWN_WEIRD_BARE
    return None


def _thread_is_about_the_body(memory, look_back=4):
    """True when the last few things the person said named a symptom or a body part."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in turns[-look_back:]:
        said = (turn.get("user") or "").lower()
        if not said:
            continue
        # The forecast's own verb goes too: "will they come back next year" is not a spine.
        said = _without_the_things_named_after_a_body(_without_the_forecast_verb(said))
        words = _without_the_idioms(said)
        if words & SYMPTOM_WORDS or words & BODY_PARTS or words & HEALTH_WORDS:
            return True
    return False


def _a_switch_off_asked(memory, clean):
    """The pool for "should i turn it off" about a machine in a thread the bot has just answered.

    Nothing at all when the thread names no machine this is safe to answer for: the honest shrug
    is better than advice about a thing the bot cannot see.
    """
    if not SWITCH_OFF_ASK.search(clean):
        return None
    said = " " + _the_line_before(memory).lower() + " "
    answer = " " + memory_bot(memory).lower() + " "
    thread = said + answer
    things = set(re.findall(r"[a-z']+", thread))
    if not (things & SWITCH_OFF_THINGS):
        return None
    if things & KEEP_IT_RUNNING:
        return None
    if "battery" in clean and (things & frozenset(("alarm", "alarms", "smoke"))):
        # Only the chirp of a dying battery: a nuisance alarm that keeps going off at the pan is a
        # different question, and the answer to it is where the alarm sits, not the battery.
        if things & frozenset(("beeping", "beeps", "chirping", "chirps", "chirp", "beep")):
            return SWITCH_OFF_BATTERY
        return None
    if SWITCH_OFF_GET_OUT.search(said):
        return None
    # The bot's own last answer can be the safety one, and then the question is not a household
    # judgement at all: "the plug socket is sparking" is answered "unplug it if you can do it
    # without touching anything hot ... ring 999 or 911", and "should i turn it off" back at that
    # was told "off at the wall", which sends somebody back to a socket that is spitting. Where
    # the safety line has spoken this turn it keeps the thread, so the only answer here is none.
    if SWITCH_OFF_GET_OUT.search(answer) or "999" in answer or "911" in answer:
        return None
    if ALREADY_SAID_OFF.search(answer):
        return SWITCH_OFF_ALREADY
    if SMOKE_ABOUT.search(said):
        return None
    if things & SWITCH_OFF_FAULT:
        return SWITCH_OFF_ADVISE
    return None


THE_SAME_ASK_AS_A_STATEMENT = ((re.compile(r"\bhow\s+to\b"), "how do i"),
                              (re.compile(r"\bwhat\s+to\b"), "what should i"))


TELL_NOT_WORDS = re.compile(
    r"\b(?:difference|apart|apart\s+from)\b"
    # A command taught to an animal is an instruction, not a message: "how do i tell my dog off"
    # was offered a template for wording something to somebody. Only the command shapes go, so
    # "how do i tell my neighbour their dog barks all night" is still a wording ask.
    r"|\b(?:dog|cat|puppy|kitten|puppies|kittens|horse|rabbit|parrot)s?\s+"
    r"(?:off|to\s+(?:stop|sit|stay|come|leave|drop|wait|heel))\b")


def _the_ask_for_words_behind_a_doubt(clean):
    """True when a doubt about how to say something is really the ask for words.

    "idk how to tell my boss" is not a report that the bot cannot answer: it is the ask, in the
    word order people who are stuck use. The line is read in the other order and the wording
    patterns answer it, with the doubt and heavy news as the two guards above.
    """
    if not A_DOUBT_IN_FRONT.search(clean) or _reads_as_heavy_news(clean):
        return False
    said = clean
    for pattern, instead in THE_SAME_ASK_AS_A_STATEMENT:
        said = pattern.sub(instead, said)
    if said == clean or TELL_NOT_WORDS.search(said):
        return False
    return bool(WORDING_ASKS.search(said) or WORDING_SOMEONE.search(said)
                or WORDING_TELL.search(said)
                # "idk what to say to my landlord": the same shape the branch above reads as a
                # wording ask when the person names who it is for.
                or (WORDING_SAYS.search(said) and WORDING_WHERE.search(said)))


def _asks_for_words(said, words):
    """True when this line is a person asking for the words to say.

    Read off the whole line: the ask can be a question shape, somebody to say it to, or a doubt
    about how to put it. Nothing about the spelling is decided here, so the same test answers for
    the line as typed and for the line as repaired - which is what lets a slip in the key verb
    keep its ask (`bot.compose.fallback_chain` asks it of both).
    """
    return bool(WORDING_ASKS.search(said) or WORDING_SOMEONE.search(said)
                or (WORDING_TELL.search(said) and not TELL_NOT_WORDS.search(said))
                or _the_ask_for_words_behind_a_doubt(said)
                or (WORDING_SAYS.search(said)
                    and (WORDING_WHERE.search(said) or len(words) <= 6)))


# Telling someone something hard wants the same help in a different register: "say what
# happened, what you want and by when" is a note to a landlord, not a divorce. The hard subject
# only chooses the pool; it never decides whether the line is a wording ask.
TELL_HARD = re.compile(
    r"\b(divorce|separat\w*|split up|break(ing)? up|broke up|leav(e|ing) (him|her|them)|"
    r"quit|resign\w*|fired|sacked|redundan\w*|lost (my|his|her|their) job|cancer|dying|died|terminal|miscarr\w*|"
    r"pregnan\w*|affair|cheat\w*|debt\w*|bankrupt\w*|autis\w*|diagnos\w*|addict\w*|"
    # coming out is hard news in the same way: "two or three lines, what happened, what you
    # want and by when" reads like a note to a landlord (honey-bat).
    r"gay|lesbian|trans|transgender|non-?binary|bisexual|coming out|came out)\b")


WORDING_WHERE = re.compile(
    r"\b(to (my|the|him|her|them|his|our|your)|when i (ring|call|phone|text|email|speak|write|ask)|"
    r"text|message|email|letter|card|note)\b")


# "about who should pay", "over what to do": a question word as the object of a preposition is
# an indirect question, part of something being reported rather than asked.
INDIRECT = re.compile(r"\s(?:about|over|of|on|at|to)\s+(?:who|what|where|when|why|how|whether)\s")


ASK_SHAPES = re.compile(
    r"\s(who|what|where|when|why|how|which)\s+(should|do|does|can|could|would|will|might|"
    r"is|are|am)\s"
    r"|\s(should|shall|do|does|can|could|would|will|did)\s+(i|we|you)\s"
    r"|\sany (idea|ideas|advice|tips|suggestions|thoughts)\s"
    r"|\swhat (do|should|can|would) (you|i)\s"
    r"|\sis it worth\s|\sworth (it|doing|paying|getting|fixing|buying)\s")


# A hello that does not open with "hi": "nice to meet you sam", "how are you", "long time no
# see". Left out of the pool below, these lines get a neutral "got it", which drops the hello
# and answers the wrong half of "nice to meet you - i'm thinking about getting a dog".
GREETING_OPEN = re.compile(
    r"^\s*(?:(?:nice|good|great|pleased|lovely|glad|happy|grand)\s+to\s+(?:meet|see|hear\s+from)"
    r"\s+(?:you|u|ya)\b"
    r"|(?:good|great|lovely|nice)\s+to\s+have\s+you\b"
    r"|how\s+(?:are|r)\s+(?:you|u|ya)\b"
    r"|how(?:'s|s|\s+is)\s+(?:it\s+going|things|tricks|you\s+doing|your\s+day)\b"
    r"|how\s+do\s+you\s+do\b"
    r"|long\s+time\s+no\s+see\b)", re.I)


def _reads_as_greeting(words, text=""):
    """True when the line opens with a greeting.

    This is the loose half of the test: it says the line opens with a hello and nothing more,
    so the caller can then ask whether the rest of the line is a hello too
    (understanding.kinds.greeting_only) before it gives the turn to the greeting pool. A
    greeting in front of a question is still the question; the caller checks that with
    _reads_as_question, so "hello! whats the weather like today" goes to the forecast.
    """
    plain = [w.replace("'", "") for w in words]
    if not plain:
        return False
    if plain[0] in GREETING_WORDS:
        return True
    if GREETING_OPEN.match(text or " ".join(plain)):
        # A hello in front of news is still the news: "good to see you, i've got a new job" wants
        # "lovely news - well done", not "hey! what would you like to talk about?".
        return not (reads_as_good_news((text or "").lower()) or reads_as_bad_news((text or "").lower()))
    return " ".join(plain[:2]) in ("good morning", "good afternoon", "good evening", "good day")


def _reads_as_taste(clean, words):
    """'Cats or dogs?' is a choice between two things, not a fact anyone can settle."""
    if " or " not in clean:
        return False
    if len(words) > 6:
        return False
    return not any(word in clean.split() for word in QUESTION_WORDS)


# Something of the person's own, asked for by name: "what's my brother called", "what did i call
# my car", "my landlord's name?". Memory answers these when it holds the name; when it holds
# nothing the search shrug tells them to look their own brother up online, which is a worse reply
# than saying the bot has not got it. The pool says "noted" rather than "you never told me"
# because the person may well have said it and the store may have missed it: it only ever stands
# where nothing already knows.
#
# Only a recall frame counts. "what do you call a baby rabbit" and "what is a female dog called"
# are vocabulary questions with an answer, and "what should i call my band" asks for ideas: both
# keep the pools they had.
#
# The object after the verb has to be the person's own: "what did i call my car", "what did i
# call him", "and what did i call it?". A thing with "the" in front of it is what a person
# *telephones* ("i called the council yesterday" then "what did i call the council"), and the
# Citizens Advice answer for that is better than being asked for a name that never existed. So
# the possessive or pronoun is part of the shape, not the bare verb.
RECALL_NAME = (
    re.compile(r"\bwhat\s+(?:did|do)\s+(?:i|we)\s+(?:call|name)\s+"
               r"(?:my|our|his|her|their|it|them|him|us|this|that)\b"),
    re.compile(r"\bwhat(?:'s| is| was)?\s+(?:my|our)\s+\w+(?:'s)?\s+(?:name|called)\b"),
    re.compile(r"\bwhat(?:'s| is| was)\s+(?:my|our)\s+(?:name|called)\b"),
    re.compile(r"\b(?:remember|recall)\b[^.?!]{0,30}\b(?:name|called|call)\b"),
    re.compile(r"\bwhat\s+(?:did|do)\s+(?:i|we)\s+(?:say|tell(?: you)?)\b[^.?!]{0,30}"
               r"\b(?:name|called|call)\b"),
)


# A name of the person's own offered back as a bare question: "my cat's name?". It has to open
# the line: "what about the water company, my name's not on anything" is a statement about a bill.
RECALL_BARE = re.compile(r"^(?:and |so |but )?(?:my|our)\b[^.?!]{0,24}\bnames?\b")


# The turn where the person gave the name: "i named my car betty", "my car is called betty",
# "my landlord is mr patel". The name comes after the verb and the thing's own noun before it,
# which is what the question has to agree with; "i called the council yesterday" is a phone call,
# not a name, which is why a word that is not a name is turned away below.
GAVE_A_NAME = (
    re.compile(r"\b(?:named|called)\s+(?:my|our|his|her|their|the)\s+(\w+)\s+(.+?)"
               r"\s*[.!]*$", re.I),
    re.compile(r"\b(?:my|our)\s+(\w+)(?:'s)?\s+is\s+((?:mr|mrs|ms|miss|dr)\.?\s+\w+|\w+)"
               r"\s*[.!]*$", re.I),
    # "my brother-in-law is called raj" names him and says who he is in one breath. The person
    # the giving line was about is read too, so a later ask about somebody else ("what is my
    # brother called") is not answered with this name: a brother in law is not the brother.
    re.compile(r"\b(?:my|our)\s+([\w-]+)\s+(?:is|was|are|were)\s+(?:called|named)\s+"
               r"(\w+)\s*[.!]*$", re.I),
    re.compile(r"\b(?:named|called)\s+(\w+)\s*[.!]*$", re.I),
)


def _name_given_before(clean, memory):
    """The name the person gave a turn or two ago for this, as they wrote it, or ""."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-2:]
    if not turns:
        return ""
    asked = {w for w in re.sub(r"[^a-z0-9 ]", " ", str(clean or "").lower()).split()
             if w not in ASK_ONLY}
    for turn in reversed(turns):
        said = str(turn.get("user") or "").strip()
        if not said:
            continue
        name, subject = "", set()
        for rule in GAVE_A_NAME:
            found = rule.search(said)
            if not found:
                continue
            groups = found.groups()
            if len(groups) == 2:
                subject, tail = {groups[0].lower()}, groups[1].strip()
            else:
                tail = groups[0].strip()
            words = [w for w in tail.replace(",", " ").split() if w]
            if not words:
                continue
            # "i named my car betty" leaves "betty", "my landlord is mr patel" leaves "mr patel":
            # the name is the end of it, and anything before it belongs to the subject.
            name = words[-1]
            subject |= {w.lower() for w in words[:-1]}
            if len(words) > 1 and words[0].lower() in ("mr", "mrs", "ms", "miss", "dr"):
                name = " ".join(words[-2:])
            break
        lowered = re.sub(r"[^a-z]", "", name.lower())
        if not name or lowered in NOT_A_NAME or lowered in ASK_ONLY:
            continue
        # A question that names the thing counts when the giving turn named it too; a pronoun
        # question ("and what did i call it?") counts on the turn just before it.
        if not asked or not subject or (asked & subject):
            if name.lower() not in said:
                continue
            bits = [b[:1].upper() + b[1:] for b in name.split()]
            return " ".join(bits)
    return ""


def _asks_a_name_back(clean, words=()):
    """True when the line asks for a name of the person's own that nothing here knows."""
    text = " ".join(str(clean or "").lower().split())
    mine = words or re.sub(r"[^a-z0-9' ]", " ", text).split()
    if not set(mine) & {"i", "we", "my", "our"}:
        return False
    if set(mine) & {"should", "shall", "could"}:
        return False
    if any(phrase in text for phrase in WORD_ANYWHERE):
        # The line asks what a word means: "what's my ... called in french" is a word question.
        return False
    if any(rule.search(text) for rule in RECALL_NAME):
        return True
    return bool(RECALL_BARE.search(text) and "?" in text)


# A line that asks for the move: "what can we do before the first day", "what do i do now",
# "where do we start", "what should we try next". The words are plumbing around one of the shapes
# below, and a line in one of those shapes wants the step of the answer in hand - not a claim that
# the answer above was all of it.
MOVE_ASK = re.compile(
    r"\bwhat\s+(?:else\s+)?(?:can|could|should|shall|do)\s+(?:i|we|you)\s+(?:do|try)\b"
    r"|\bwhat\s+(?:now|next)\b"
    r"|\bwhere\s+(?:do|should|can)\s+(?:i|we)\s+(?:start|begin)\b"
    r"|\bwhats\s+the\s+(?:first|next)\s+(?:thing|step|move)\b"
    r"|\bhow\s+(?:do|can|should)\s+(?:i|we)\s+(?:start|begin|prepare|get\s+going)\b", re.I)


def _asks_for_the_move(line):
    """True when the line asks what to do, rather than what the last answer said."""
    return bool(MOVE_ASK.search(str(line or "")))


def _names_a_new_thing(word, clean):
    """True when the line names `word` as a thing (or a plurality of something) of its own."""
    words = clean.split()
    for i, here in enumerate(words):
        if here != word and here.rstrip("s") != word:
            continue
        before = words[i - 1] if i else ""
        after = words[i + 1] if i + 1 < len(words) else ""
        if before in RULED_OUT_DETERMINER and after not in PARTICLE:
            return True
        # "how long is the flight": a plural is a count of things on its own.
        if here.endswith("s") and len(here) > 3 and here != words[0]:
            return True
    return False


def content_words(text):
    """The words a line actually asks with: no pointing words, nothing of three letters or less."""
    words = _flat_words(text)
    return [word for word in words if word not in POINTING and len(word) > 2]


def _flat_words(text):
    """The words of a reply, lowercased and without punctuation, for comparing two of them."""
    return re.sub(r"[^a-z0-9 ]", " ", str(text or "").lower()).split()


def memory_bot(memory):
    """The reply the bot gave on the turn just before this one."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict) and t.get("bot")]
    return str(turns[-1].get("bot")) if turns else ""


def is_the_answer_shorter(reply, last):
    """True when `reply` is the last answer said shorter by the composer.

    The said-it-already lines above are the composer's own wording for a repeat; a short form of
    the answer is the other thing it writes for one, and the arbiter has to be able to tell the
    two apart from a stock line, because only the second is the answer's own words. The reading is
    the shortening module's (`bot/compose/why.py`, `is_the_answer_shorter`), so nothing here owns
    a second copy of the frame.
    """
    try:
        return why.is_the_answer_shorter(reply, last)
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False


def is_said_it_already(reply):
    """True when `reply` is one of the said-it-already lines, in any of its wordings."""
    flat = " ".join(_flat_words(reply))
    return any(flat == " ".join(_flat_words(line))
               for line in HELP_ALREADY + SAME_AGAIN)


# A line can be nothing but a finger pointed at something: "what does that mean", "which one",
# "how does that work", "whos that", "how come". Every word in one of these is the pointing;
# none of them is a subject, so a line that is all pointing words names nothing at all. The
# list is of the joints a person uses to point with, not of sentences: a wh-word, the thing
# pointed at (that, this, it, one), and the verb of asking (mean, work, explain, be, do).
POINTING_WORDS = frozenset("""
    what whats how why which who whos whom when whens where wheres
    that this it those these one ones thats
    mean means meant meaning explain work works working come
    do does did is are was were be been am
    you u about by for to of in on at with
    much many long again then please exactly really about
    so ok okay oh ah right well and but
    say tell know
""".split())


# The words that make the line a pointer rather than a question of its own.
POINTERS = frozenset("that this it those these one ones thats".split())


# The words that make the line an ask about the words on the table rather than a question of
# its own: "what do you mean" and "explain that" point at whatever was said, and there is
# nothing they can be asked about until something has been said.
MEAN_WORDS = frozenset("mean means meant meaning explain".split())


POINTING_ASK = frozenset("what whats how why which who whos when whens where wheres".split())


# "how come" and "what for" point with no pointer in them at all.
POINTING_IDIOMS = frozenset(["how come", "how comes", "what for", "how so"])


# Nothing in the chat or on the bot's side can be what the finger is on: the bot cannot see the
# letter, the screen or the doctor's words the person is reading, and it has said nothing they
# could be asking about. So it says that in a few words and asks for the thing itself. Every
# line names the thing pointed at with quotes, so it reads as the pointer being answered and not
# as a shrug at the person.
POINTING_LINES = (
    "I can't see what you're looking at, so 'that' could be anything. Put the thing in a "
    "couple of words and I'll answer it properly.",
    "There's nothing on my side for 'that' to land on - tell me the thing itself and I'll take "
    "it from there.",
    "'That' could be a lot of things and I've none of them in front of me - say the thing "
    "you mean and I'll come at it properly.",
    "'That' has nothing behind it here. What is the thing you're pointing at?",
)


def _a_previous_line_named_something(memory, look_back=3):
    """True when a line the person already said in this chat carried a subject of its own.

    "how long was it" after "i watched a film for two hours" has its referent: the film. Only the
    person's own lines are read - the bot's replies are its offers and questions, and one of them
    always has words in it - and only for a word the memory's topic reading keeps.
    """
    from ..memory.topics import keywords  # noqa: PLC0415 - the chat's own reading of a line

    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-look_back:]
    return any(keywords(str(turn.get("user") or "")) for turn in turns)


# The repair joke about a person: "is it worth fixing myself", "should i just fix me". Only the
# reflexive is read, so a real question about a body ("is it worth getting it looked at") keeps
# the advisor's line.
OFFERS_TO_FIX_THEMSELVES = re.compile(
    r"\b(?:fix(?:ing|ed)?|mend(?:ing|ed)?|patch(?:ing|ed)?|servic(?:e|ing)|replace)"
    r"\s+(?:it\s+)?(?:myself|me|yourself|himself|herself)\b")


def _offers_to_fix_themselves(clean):
    return bool(OFFERS_TO_FIX_THEMSELVES.search(clean or ""))


def is_a_forecast(said):
    """True when a reply is one of the forecast's own lines, which say no one can call it.

    A forecast line is not a receipt of the person's words, but it can look like one: "will that
    get better if i keep at it" after the breathlessness card shares "get", "better" and "keep"
    with the first self line, so the greeting module read the line as an echo and said the card's
    second sentence back - repeating the answer already on the screen. The greeting module asks
    this before it hands a leftover back.
    """
    head = str(said or "").strip()
    if not head:
        return False
    # Up to the first placeholder, since "{who}" in the template is a name in the reply.
    return any(head.startswith(line.split("{")[0]) for pool in FORECAST_POOLS for line in pool)


def _the_forecast_subject(clean, memory):
    """('person'|'self'|'pet', "your dad") for the one a forecast is about, or (None, "").

    Whose body it is decides which building the answer sends them to, so it is read before the
    reply: a pet keeps its own doctor, a person's health is theirs and not the speaker's, and
    only a thread about the speaker's own body takes the GP line. "they" is left out on purpose:
    "will they come back next year" about the slugs is not somebody with a doctor.
    """
    recent = [str(t.get("user") or "").lower()
              for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-3:]
    asked_about_self = bool(FORECAST_I_ASK.search(clean or ""))
    for said in [clean] + ([] if asked_about_self else list(reversed(recent))):
        found = FORECAST_RELATION.search(said or "")
        if found:
            relation = found.group(1)
            return ("pet" if relation in ANIMALS else "person"), "your " + relation
    if asked_about_self:
        # "will i be ok" is about the asker even when the thread named somebody else: a car
        # accident is theirs, the coping is the speaker's.
        return "self", "you"
    if _thread_is_about_a_pet(memory):
        return "pet", "them"
    whose = _whose_body(clean, recent)
    if whose == "mine":
        return "self", "you"
    if whose == "theirs":
        return "person", "them"
    if FORECAST_HE_SHE.search(clean or ""):
        return "person", "them"
    if _a_body_in_the_thread(memory):
        # "will it get better" one line after "i cant get up the stairs since my knee op": the
        # thread says whose body it is, and the line itself says nothing at all. Read with the
        # things named after a body taken out, so a garden by the back door is not a spine.
        return "self", "you"
    if _thread_is_about_someone_else(memory) or _thread_is_about_a_person(memory):
        return "person", "them"
    return None, ""


def _without_the_things_named_after_a_body(text):
    """The line with "back door" and "foot of the stairs" taken out before a body is read."""
    return BODY_WORD_FOR_A_THING.sub(" ", str(text or ""))


def _whose_body(clean, recent):
    """'mine', 'theirs' or "" for the body a forecast is about.

    "my shoulder aches when i lift the kids" is the speaker's shoulder, and reading the kids in
    the line as the subject sent the shoulder to somebody else's doctor - "ask them how them is
    doing". The possessor is what decides it: `my` in front of a body word is the speaker's,
    and a body word beside a person is theirs.
    """
    for said in [clean] + list(reversed(recent)):
        tokens = re.findall(r"[a-z']+", _without_the_things_named_after_a_body(
            _without_the_forecast_verb(said or "")))
        for at, token in enumerate(tokens[:-1]):
            if token == "my" and tokens[at + 1] in FORECAST_BODY_WORDS:
                return "mine"
        if set(tokens) & FORECAST_BODY_WORDS and (set(tokens) & _THREAD_PEOPLE
                                                  or FORECAST_HE_SHE.search(said or "")):
            return "theirs"
    return ""


def _without_the_forecast_verb(line):
    """The line with the forecast's own words taken out, so they cannot pass for a subject.

    "will they come back next year" about the slugs is a question about a garden, and "back"
    is a body part: read with the verb in, the line named a spine and sent a gardener to a
    physio. What is left after the verb is the thing the forecast is about.
    """
    found = FORECAST.search(line or "")
    if not found:
        return line or ""
    return (line[:found.start()] + " " + line[found.end():]).strip()


def _thread_said(memory, look_back=4):
    """The last few things the person said, as one line."""
    turns = [t for t in (memory or {}).get("turns") or [] if isinstance(t, dict)][-look_back:]
    return " ".join(str(turn.get("user") or "").lower() for turn in turns)


def _a_body_in_the_thread(memory, look_back=4):
    """True when the last few things said were about a body or a health worry.

    Read here rather than through `_thread_is_about_the_body` because that one also counts the
    health words of a thing ("my sister is really struggling" has none, "my mum had a fall" has
    several), and the two pools answer different questions: one names who is treating somebody,
    the other says what the person asking can do.
    """
    for turn in [t for t in (memory or {}).get("turns") or [] if isinstance(t, dict)][-look_back:]:
        said = str(turn.get("user") or "").lower()
        # A thing named after a body ("the back door") and the forecast's own verb ("will they
        # come back") are not bodies, so both go before the words are read.
        said = _without_the_things_named_after_a_body(_without_the_forecast_verb(said))
        words = _without_the_idioms(said)
        if (words & BODY_PARTS or words & SYMPTOM_WORDS or words & HEALTH_WORDS
                or words & FORECAST_ILL or FORECAST_OFF_THEIR_FOOD.search(said)
                or FORECAST_A_FALL.search(said)):
            return True
    return False


def _a_hard_patch_in_the_thread(clean, memory, look_back=3):
    """True when the thread is somebody having a hard time rather than somebody ill."""
    said = [str(clean or "").lower()]
    said += [str(t.get("user") or "").lower()
             for t in (memory or {}).get("turns") or [] if isinstance(t, dict)][-look_back:]
    return any(FORECAST_STRUGGLE.search(line) for line in said if line)


# A definition wants a definition, not a person to ring: "what does a mortgage broker do" and
# "the difference between a credit card and a debit card" are facts about the world.
TIPS_ASKS = re.compile(r"\b(any|some|got any|need some|need any|want some)\s+(tips|tip|advice|"
                       r"pointers|suggestions|ideas|tricks|trick)\b")


# "Tricks" is the same plea as "tips" ("any tricks", "got any tricks for sleeping", "any tricks for
# the first thirty seconds"), and it was the one word missing from the list, so a person asking for
# tricks got the flat nod. Only the ask frame above counts, so "trick or treat" and "my dog does a
# trick" are untouched; the one shape that carries the frame without asking is named here.
NOT_A_TIPS_ASK = re.compile(r"\btricks?\s+or\s+treat\b")


def _is_a_tips_ask(line):
    """True for a plea for tips in this spelling: the frame, without the phrase that is not one.

    The frame and its guard in one test, so a caller can read the typed line and the repaired
    one through `_reads` without writing the guard twice.
    """
    return bool(TIPS_ASKS.search(line)) and not NOT_A_TIPS_ASK.search(line)


# A plea for tips carries its subject in the line ("any tips for my first half marathon", "i
# need a new bath, any tips"), and the tip depends on where the person is with it. Saying the
# subject back and asking the one thing that decides it beats "tell me what you've got so far",
# which would fit any message at all, and it invents no fact. Two shapes: something coming up
# (timing decides it) and a thing to get or do (what they have decides it).
TIPS_SUBJECT_FOR = re.compile(r"\b(?:tips?|advice|suggestions?|recommendations?|ideas?)\s+"
                              r"(?:for|on|about|with)\s+(?P<subject>.+)$")


TIPS_SUBJECT_TAIL = re.compile(
    r"(?:^|[,.;!?]\s*|\s)(?:any\s+|some\s+|got any\s+)?(?:tips?|advice|suggestions?|"
    r"recommendations?|ideas?)\b.*$")


TIPS_LEAD = re.compile(r"^(?:so|and|but|ok|okay|well|hi|hey|also|then|just)\s+")


# "ok give me a quick dinner idea" asks for a suggestion, not for tips on "give me a quick
# dinner": the request frame is not part of the subject.
TIPS_ANY_IDEA = re.compile(r"\b(?:any|some|got any|need some|need any|want some)\s+ideas?\b")


TIPS_WORD = re.compile(r"\b(?:tips?|advice|suggestions?|recommendations?)\b")


TIPS_REQUEST = re.compile(r"^(?:give|tell|show|send|find|list|suggest|recommend|get)\s+"
                          r"(?:me|us)\s+")


# Something with a date on it: how long there is decides which tips are worth giving.
TIPS_SOON = re.compile(r"\b(?:first|before|wedding|holiday|interview|exam|lesson|marathon|"
                       r"race|move|trip|course|test|appointment|driving\s+lesson|birthday|"
                       r"anniversary|christmas|funeral|hen\s+do|stag\s+do|due\s+date)\b")


def _hedged_recently(memory, look_back=3):
    """True when the bot has said it does not know, on any of the last few turns.

    "what is the planning policy on ferret hutches in bogota" / "anything i can do about it":
    the bot could not answer, so the ask has no answer behind it and the hedge stands - it
    must not become "that's most of what I know on it", which claims knowledge it never had.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-look_back:]
    for turn in turns:
        said = str(turn.get("bot") or "").strip()
        if said and any(said[:40] == line[:40] for line in UNKNOWN):
            return True
        # A punt is a hedge said in other words: "that's beyond what I know well, sorry" does not
        # become "that was the whole of my answer on it" for the question it never answered.
        if said and any(punt in said.lower() for punt in PUNT):
            return True
    return False


# "ok whats your honest view" / "honest view?" / "what would you do": a view is asked for and
# nothing is named. It is not a question about the world - it is the person asking the bot to
# stand behind what it just said, so a search suggestion answers the wrong question. The ask
# itself is a small closed family; the words around it are plumbing ("ok", "so", "honestly"),
# and a line with any word outside that set names its own subject and keeps its own answer
# ("what do you think of my new haircut" is about a haircut, and is not this).
VIEW_ASKS = re.compile(
    r"\b(?:your|ur|yur)\s+(?:(?:honest|own|real|true|personal)\s+)?"
    r"(?:view|opinion|take|thoughts|verdict|read)\b"
    r"|\bwhat(?:'s|s| is)?\s+(?:is\s+|was\s+)?(?:your\s+|the\s+|a\s+)?"
    r"(?:(?:honest|own|real|true|personal)\s+)?(?:view|opinion|take|thoughts|verdict)\b"
    r"|\bwhat\s+(?:do|would|d)\s*(?:you|u|ya)\s+(?:reckon|think|say)\b"
    r"|\b(?:honest|own|real|true)\s+(?:view|opinion|take|thoughts|verdict)\b"
    r"|\b(?:honest|own|real|true)\s+answers?\b"
    r"|\b(?:your|ur|yur)\s+(?:honest|own|real|true|personal)\s+answers?\b"
    r"|\bwhat\s+would\s+(?:you|u)\s+do\b"
    r"|\b(?:view|opinion|take|thoughts|verdict)\s+on\s+(?:it|that|this)\b")


# A reply that mirrored a feeling back is company, not an answer, so there is no view to stand
# behind: "My view has not changed: sorry to hear that" is the bot quoting a kindness as though it
# were a claim (@sure-umbrella's read on #4809). The same goes for the opener that only names how
# the day went. The list is the openers the small-talk and feelings pools use, not a topic list.
VIEW_NOT_AN_ANSWER = re.compile(
    r"^(?:sorry\b|i'm sorry\b|im sorry\b|so sorry\b|that sounds\b|that's rough\b|"
    r"thats rough\b|that's hard\b|thats hard\b|that's a hard one\b|that's a lot\b|"
    r"ugh\b|ouch\b|hope\b|i'm here\b|im here\b|take care\b|nothing has to be decided\b|"
    # A nod is not an answer either. "Thanks for telling me - I'm here if you want to dig into any
    # of that" opens on a thank-you, so the anchored "i'm here" above missed it and a view of it
    # quoted the thank-you back as the bot's opinion. "Got it. Is there anything you'd like a hand
    # with?" and "Noted: ..." are the same: they file what was said and claim nothing.
    r"thanks\b|thank you\b|got it\b|noted\b|i'm listening\b|im listening\b|understood\b)")


def _in_a_pool(text, pools=(NOT_AN_ANSWER,)):
    """True when a reply is one of the pool lines, with or without its question after it.

    "Love that - well done. How are you celebrating?" is the congrats line plus its question, so
    an exact match on the pool never fired and "what do you think" quoted the congratulations as
    the bot's view (@agile-poppy's read on #5606). The first forty characters are what every
    hedge in this file already compares by.
    """
    said = _plain(text)
    return bool(said) and any(_plain(line) and said.startswith(_plain(line))
                              for pool in pools for line in pool)


# The floor: a line that only hands the conversation back to the person. "Go on - I'm listening."
# (chat's "say something" pool), "Ask away, I'll do my best.", "Of course. Take your time." - the
# bot is saying it is ready to hear more, and there is no position in it to stand behind. So a view
# asked on top of one has nothing to give: "what's your take" was answered "Same as I said: go on -
# I'm listening." (@spry-elk's chat, #routing 62120), which tells the person the bot has a view and
# then offers to listen instead of saying it. Only a line made entirely of the floor and its
# courtesies stands down - "Go on, get it checked" still makes a claim.
FLOOR_CLAUSE = re.compile(
    r"^(?:(?:go|carry)\s+on\b|tell\s+me\s+more\b|say\s+more\b|keep\s+going\b|go\s+ahead\b"
    r"|ask\s+away\b|i'?m\s+listening\b|i\s+am\s+listening\b|i'?m\s+here\b"
    r"|take\s+your\s+time\b|over\s+to\s+you\b|what'?s\s+on\s+your\s+mind\b"
    r"|i'?ll\s+do\s+my\s+best\b|spill\s+it\b|i'?m\s+all\s+ears\b)", re.I)


FLOOR_COURTESY = re.compile(
    r"^(?:of\s+course|sure|ok|okay|right|yes|no|well|please|thanks|thank\s+you|"
    r"no\s+need(?:\s+to\s+apologise)?|you'?re\s+not\s+dumping\s+anything\s+on\s+me|"
    r"don'?t\s+apologise(?:\s+for\s+that)?|nothing\s+to\s+be\s+sorry\s+about|"
    r"no\s+problem|you'?re\s+welcome|that'?s\s+what\s+i'?m\s+here\s+for|"
    r"i'?d\s+rather\s+hear\s+it\s+than\s+not)$", re.I)


# "what should i do about the holiday i booked in august" is the same stuck line as "i dont know
# what to do about the holiday": the thing is named, the choice is theirs, and no search settles
# it - yet it got the hedge, which offered to find better sources for a holiday nobody else has
# booked. The pools that answer a decision want a doubt ("im not sure whether to move in with
# her"); this is the same choice asked straight, so it gets the same three questions about the
# part that will not move. Everything that knows the thing keeps its turn: it sits at the floor,
# after the knowledge base, the routes and the store.
# The health words that arrive wearing another ending: "the tiredness", "the anxiety", "the
# sleeplessness". A stem test catches them, and a question about the part that will not move is
# not what a person who cannot sleep needs.
HEALTH_STEMS = ("tire", "exhaust", "sleep", "insomnia", "anxi", "depress", "stress", "panic",
                "symptom", "sick", "unwell", "nause", "dizzi", "swell", "inflam")


WHAT_TO_DO_ABOUT = re.compile(
    r"^\W*(?:(?:and|but|so|oh|ok|okay|well|right|alright|honestly|anyway|also)\W+)*"
    r"what(?:'?s|\s+is)?\s+(?:should|shall|can|could|would|do|did|will|am\s+i)\s+"
    r"(?:i\s+)?(?:do|say|tell)\s+about\s+(?P<thing>[^?.!]+)$", re.I)


# A line that names a body, a blow or a death is somebody else's turn - the safety module and the
# urgent readings answer those, and a question about the part that will not move is not for them.
NOT_WHAT_TO_DO_ABOUT = re.compile(
    r"\b(?:die|died|dying|death|kill\w*|suicid\w*|hurt\w*|harm\w*|abus\w*|hit|hits|hitting|"
    r"beaten|chest|breath\w*|bleed\w*|overdose\w*|emergency|999|111)\b", re.I)


# The thing a stuck line named, with the tail that only says when or which cut away, so the
# question reads "the holiday" and not "your holiday i booked in august".
THING_TAIL = re.compile(
    r"\s+(?:i|i've|ive|im|i'm|we|i\b.*|that|which|who|he|she|they|you|my|me|it)\b.*$", re.I)


def _the_thing_alone(thing):
    """The thing as it can be said back: "the holiday i booked in august" -> "the holiday"."""
    said = _yours(" ".join(str(thing or "").split()).strip(" ,.;:-"))
    cut = THING_TAIL.sub("", said).strip(" ,.;:-")
    return cut or said


# One question about the thing they named, which is what a friend asks. The stock "weigh the
# parts" questions say nothing about the holiday, the deposit or the job; these name it.
WHAT_TO_DO_ABOUT_FRAMES = (
    "{thing} - what's the bit of it you'd want to sort first?",
    "Where would you want to start with {thing}?",
    "{thing} - what's the part that's bothering you most?",
    "{thing} - what would you want to change first?",
)


# "how are you feeling about the move" asks the bot about itself and then names something of
# theirs, and the two halves together left every reader standing: main offered to search the web
# for a better source on a move the bot is not making. A question put to the bot about the bot is
# answered by saying what the bot actually is, and then turning to the thing they named, because
# that is the part worth talking about. Only a hedge is replaced here - the module that answers a
# bot-about line already has its turn, and a line it answers never reaches this.
ABOUT_THE_BOT_NAMED = re.compile(
    r"^\W*(?:(?:and|but|so|oh|ok|okay|well|right|alright|honestly|anyway|also)\W+)*"
    r"(?:how\s+(?:are|do)\s+(?:you|u|ya)\s+feel(?:ing)?"
    r"|what\s+do\s+(?:you|u|ya)\s+(?:make|think)\s+of)"
    r"\s+(?:about|of|with|on)\s+(?P<thing>[^?.!]+)$"
    r"|^\W*(?:(?:and|but|so|oh|ok|okay|well|right|alright|honestly|anyway|also)\W+)*"
    r"how\s+do\s+(?:you|u|ya)\s+find\s+(?P<thing2>[^?.!]+)$", re.I)


# The same ask with nothing named - "how are you feeling about it", "how do you feel about all
# this" - is answered by the bot-about reader and never gets here, so a pronoun arriving here has
# no thing to be said back and the line keeps whatever reply it had.
ABOUT_THE_BOT_BORN = re.compile(
    r"^\W*(?:(?:and|but|so|oh|ok|okay|well|right)\W+)*"
    r"(?:where\s+(?:were|are)\s+(?:you|u|ya)\s+(?:from|born)"
    r"|(?:were|are)\s+(?:you|u|ya)\s+(?:born|raised|brought\s+up)"
    r"(?:\s+(?:here|there|locally|in\s+this\s+country))?)"
    r"(?:\s+originally)?[ ?!.,;]*$", re.I)


# What the bot can honestly say about a feeling it does not have, and the door back to the person.
BOT_FEELING_NAMED_LINES = (
    "No feelings on my side at all, and no view on {thing} worth having - I am a program. How are "
    "you finding it?",
    "I have no feelings about it - I am a program, so there is nothing in me for {thing} to land "
    "on. What do you make of it?",
    "No view worth having, and no moods to have one with. You are the one living with {thing} - "
    "how is it going?",
)


BOT_BORN_LINES = (
    "There is no born for me - I am a program, so no hometown and no childhood. Where are you "
    "from, if you do not mind me asking?",
    "Not born, and not from anywhere: I started as a program and stayed one. Are you far from "
    "where you grew up?",
)


# "is there a limit to how long we can talk" is a question about this conversation, and the one
# thing the bot can answer from where it stands - there is no clock on it. It was sent to a search
# engine instead, which is the one place that answer is not. Both ends are anchored and the talk
# itself has to be named, so "how long can i keep the leftovers" and "how long should i boil an
# egg" keep the answers they have.
_THE_TALK_ITSELF = r"(?:talk|chat|talking|chatting|keep\s+going|keep\s+you\s+here)"


ABOUT_THE_BOT_TALK = re.compile(
    r"^\W*(?:(?:and|but|so|oh|ok|okay|well|right|sorry|quick|just|question|one\s+question|quick\s+question|first\s+question|random\s+question)\W+)*"
    r"(?:"
    r"(?:is|are)\s+there\s+(?:a|any)\s+(?:time\s+)?limit(?:\s+(?:to|on)\s+"
    r"(?:(?:how\s+long|the\s+time)\s+)?(?:(?:we|i)\s+can\s+)?(?:"
    + _THE_TALK_ITSELF + r"|this|it|the\s+chat|our\s+chat))?"
    r"|(?:how\s+much\s+time\s+(?:do|have|did)\s+(?:we|i)\s+(?:have|got)\s+left)"
    r"|(?:do|have)\s+(?:we|you|i)\s+(?:have|got)\s+(?:a\s+|any\s+)?(?:time\s+)?limit"
    r"|(?:how\s+long|how\s+much\s+time)\s+(?:(?:can|could)\s+(?:we|i)\s+)?"
    r"(?:(?:have|has)\s+(?:we|you\s+and\s+i)\s+been\s+)?(?:" + _THE_TALK_ITSELF + r")"
    r"|(?:are|do)\s+(?:we|i)\s+(?:out\s+of|running\s+out\s+of|short\s+of)\s+time"
    r"|(?:do|should)\s+i\s+(?:need\s+to\s+)?hurry(?:\s+up)?"
    r"|(?:can|could|will)\s+(?:we|i|you\s+and\s+i)\s+(?:talk|chat|keep\s+going)\s+for\s+long"
    r"|have\s+(?:we|i|you\s+and\s+i)\s+got\s+long"
    r")(?:\s+(?:with|for)\s+(?:you|this|me|now)|\s+for|\s+much)?[ ?!.,;]*$", re.I)


# The same ask with a tally in it: "how long have we been talking" wants a number, and the honest
# answer is that the bot does not keep one.
ABOUT_THE_BOT_CLOCK = re.compile(
    r"^\W*(?:(?:and|but|so|oh|ok|okay|well|right|sorry|quick|just|question|one\s+question|quick\s+question|first\s+question|random\s+question)\W+)*"
    r"(?:how\s+(?:long|much\s+time)\s+(?:have|has|did)\s+(?:we|i|you|you\s+and\s+i)\s+been\s+"
    r"(?:" + _THE_TALK_ITSELF + r")"
    r"|how\s+long\s+has\s+this\s+been\s+going\s+on)"
    r"(?:\s+(?:to|with)\s+(?:you|me))?[ ?!.,;]*$", re.I)


BOT_TALK_LIMIT_LINES = (
    "No limit I know of on my side - I stay as long as you keep going, and nothing runs out. "
    "What do you want to get to?",
    "Nothing cuts this short at a set time as far as I know: the chat lasts while you are in it. "
    "Where would you like to take it?",
)


BOT_TALK_CLOCK_LINES = (
    "I don't keep a clock, so I can't put a number on it - but we have been going a while, and I "
    "am in no hurry.",
    "No clock on my side, sorry: I hold the words, not the minutes. There is plenty of time as "
    "far as I am concerned.",
)


def _only_the_floor(said):
    """True when every part of the line is the floor or a courtesy on its way to it."""
    said = _plain(said)
    if not said:
        return False
    parts = [p.strip(" ,.;:!?\u2014\u2013-\t") for p in
             re.split(r"[.!?;,\u2014\u2013]|\s-\s", said)]
    parts = [p for p in parts if p]
    if not parts or len(parts) > 4:
        return False
    for part in parts:
        if FLOOR_COURTESY.match(part):
            continue
        if not FLOOR_CLAUSE.match(part):
            return False
        # A floor phrase opens a long line as easily as a short one, so the part has to stop soon
        # after it - unless it goes on to say it will wait, which is still the floor.
        words = len(part.split())
        if words > 8 and not FLOOR_WAITING.search(part):
            return False
    return True


# The half of a floor line that says it will still be there ("I'm here if you want to come back to
# it"), so a longer line that opens with a floor phrase still counts as the floor.
FLOOR_WAITING = re.compile(
    r"\b(?:if|when)\s+you(?:'re|\s+are)?\s+(?:want|need|ready|like)|for\s+as\s+long\s+as"
    r"|\bwhenever\b|\bany\s+time\b", re.I)


def _the_words(text):
    """The words of a line that say something about its subject."""
    return {word for word in re.findall(r"[a-z']+", str(text or "").lower())
            if word not in _ECHO_FILLER and len(word) > 2}


def _an_echo_of(question, sentence):
    """True when a sentence is only the person's own line said back, not a claim.

    "Right, so a different cable is done. Clean the charging port out..." opens with a receipt
    built by another module (`bot/memory/tried.py`), and a helper that copied one module's frame
    list would keep missing the next one (@agile-poppy's read on #5606). So the test is the
    words: a sentence whose subject words are nearly all the person's own says nothing new,
    whatever wording the receipt was built from.
    """
    mine = _the_words(question)
    theirs = _the_words(sentence)
    if len(theirs) < 2 or not mine:
        return False
    return len(theirs & mine) / len(theirs) >= 0.75


# A reply from the small-talk module that only reacts and hands the conversation back is not a
# claim: "i got the job" was met with "Love that - well done. How are you celebrating?", and
# "what do you think" quoted the congratulations as the bot's view (@agile-poppy's read on
# #5606). The chat module's pools are its own tables, which this file cannot read without
# importing a module, so the test is the shape: a short reply that ends in a question is the
# bot asking, not the bot claiming.
def _only_a_reaction(module, said):
    if str(module or "") != "chat":
        return False
    said = str(said or "").strip()
    if not said.endswith("?") or len(said.split()) > 14:
        return False
    return any(phrase in said.lower() for phrase in PRAISE)


def _the_answer_in_reply(question, said):
    """The reply without the receipt or reaction sentences in front of it, or "".

    A receipt sometimes opens a reply that goes on to answer ("Right, so a different cable is
    done. Clean the charging port out..."), and the answer is the part after it. Only the
    opening is stripped: later sentences are the answer qualifying itself.
    """
    said = str(said or "").strip()
    for _ in range(3):
        sentences = re.split(r"(?<=[.!?])\s+", said)
        first = sentences[0].strip() if sentences else ""
        rest = " ".join(sentences[1:]).strip()
        if not rest:
            return said
        # A sympathy opener is deliberately not stripped: "Sorry to hear that. A walk and
        # someone to talk to usually help" is company with a suggestion attached, and standing
        # behind the suggestion alone would undo the call on #4809. A receipt is different - the
        # answer after it is the answer the bot gave.
        if not (ack.reads_as_a_receipt(first) or _in_a_pool(first)
                or _an_echo_of(question, first)):
            return said
        said = rest
    return said


def _reads_as_a_claim(said):
    """True when the reply made a claim, so a view of it is the bot's own view.

    A line that mirrors a feeling back, or that puts its question where the answer should be, has
    nothing in it to stand behind. "Sorry to hear that. A walk and someone to talk to usually
    help" is sympathy with a suggestion attached, and "Worth planning rather than rushing into:
    what would have to go right for you?" is a question asked back - quoting the front of either
    gives the person a view the bot never had.
    """
    said = str(said or "").strip()
    if not said or VIEW_NOT_AN_ANSWER.match(said.lower()):
        return False
    if ack.reads_as_a_receipt(said):
        # A receipt is the person's own line said back ("Got it - but your mum says it's too
        # soon"), so quoting it as a view stands behind nothing: "what would you do" after a
        # detail turn answered "My view has not changed: Got it - but your mum says it's too
        # soon".
        return False
    if _in_a_pool(said):
        # The reaction pools are the same shape of nothing: "I'm listening - say more if it
        # helps" is an offer to hear more, and "Good for you. Is there much to sort out before
        # it?" is a congratulations, so "what do you think" on top of either would stand behind
        # a line the bot only said to be polite.
        return False
    if _only_the_floor(said):
        # An offer to listen is not a position: "what's your take" on the back of "Go on - I'm
        # listening" was answered "Same as I said: go on - I'm listening".
        return False
    first = re.split(r"(?<=[.!?])\s+", said)[0].strip()
    if first.endswith("?") and ":" in first:
        # A claim that led into its own question: the part before the colon is a lead-in, not a
        # view, and the part after it is the question the person is being asked.
        return False
    return True


def _nothing_to_stand_behind(said):
    """True when the bot's line left the answer where it was, so the view is the one behind it.

    A receipt ("Got it - but your mum says it's too soon") and a neutral line both put nothing on
    the table, and neither does the floor: "Go on - I'm listening." is the bot saying it is ready
    to hear more. Walking past them is what keeps "what's your take" on the answer the bot
    actually gave instead of quoting the offer to listen back at the person.
    """
    said = str(said or "").strip()
    return bool(said) and (ack.reads_as_a_receipt(said) or _in_a_pool(said, (NEUTRAL,))
                           or _only_the_floor(said))


# An ask for the bot's own view on the first turn is a bare ask - the person has the subject in
# their head and has not said it - except when the line names somebody ("what do you think of me",
# "what do you reckon about us"), where the subject did come with the line.
VIEW_NAMES_SOMEBODY = re.compile(r"\b(?:me|my|mine|myself|us|our|ours|i|im|i'm)\b")


def _is_a_view_ask(clean):
    """True when the line asks for a view and names nothing of its own.

    "your take", "honest view?", "honest answer" - every word is plumbing, so the only thing the
    person can be asking about is the answer just given. A word outside the set names a subject
    ("what do you think of my new haircut") and that line has its own answer to look up.
    """
    if not VIEW_ASKS.search(clean):
        return False
    words = re.findall(r"[a-z']+", clean)
    return bool(words) and not any(
        word.strip("'") not in VIEW_ONLY_WORDS for word in words)


def _the_view_asked_for(clean, memory):
    from .fallback_pools import _the_view_asked_for as _moved
    return _moved(clean, memory)


def _after_a_colon(said):
    """The answer's first word, after a colon: "My view: find the water..." reads as one line."""
    if len(said) > 1 and said[0].isupper() and not said.startswith("I ") and not said.startswith("I'"):
        return said[0].lower() + said[1:]
    return said


# A hedge that names the thing it could not answer is formatted before it is said ("... a map
# app search for plumber near you ..."), so its head is only the part before the first
# placeholder. Comparing that much is enough to recognise the reply as a hedge, which is all the
# arbiter and the greeting module ask of this.
HEDGE_HEADS = tuple(line[:40] for pool in HEDGE_POOL for line in pool)


HEDGE_PREFIXES = tuple(line.split("{")[0] for pool in HEDGE_POOL for line in pool
                       if "{" in line)


# What settles a kind of ask (bot/compose/the_rule_for_it.py) stands exactly where these shrugs
# stand: it is said when nothing else knows the line, so anything that does know it has to win
# the turn over it, the same as it wins over a hedge. "How long do i cook them", a turn after
# "200g of plain flour for four people", was given the time rule instead of the minute a side
# that answer already held - the arbiter passes a hedge over for a real answer, and a rule it
# could not recognise cost the person the better reply.
from .the_rule_for_it import RULE_HEADS as _RULE_HEADS  # noqa: F401, E402 - after the pools


HEDGE_HEADS = HEDGE_HEADS + _RULE_HEADS


# The reply that asks a person to say which bit they mean. It is not a hedge: it says the bot did
# not follow the line rather than that nobody has written the answer down. A chat that is already on
# a card can answer the follow-up instead of asking the question back.
def _is_an_ask_which_bit(said):
    """True when a reply is the "tell me which bit" line rather than an answer or a hedge."""
    head = (said or "").strip()
    return bool(head) and head in BARE_FOLLOW_UP_REPLIES


is_an_ask_which_bit = _is_an_ask_which_bit


def _is_a_hedge(said):
    """True when a reply is one of the pools that mean the bot cannot answer."""
    head = said[:40]
    return (any(head == line for line in HEDGE_HEADS)
            or any(said.startswith(prefix) for prefix in HEDGE_PREFIXES))


# The same test under a name another package can call: `bot/memory/carry.py` has to tell a real
# answer from a hedge before it puts one on the screen in place of the last one, and reaching for a
# private name across packages is the kind of thing that breaks when this file changes.
is_a_hedge = _is_a_hedge


def is_a_hedge(said):
    """The public name for the test above, for the arbiter.

    A reply that says the bot cannot answer is never an improvement on a card that can, so the
    arbiter asks this before it moves the front card aside for a reply about somebody else. The
    reply it holds has been reduced to its words and so has no capital letters, which is why this
    compares without them.
    """
    head = str(said or "")[:40].lower()
    return (any(head == line.lower() for line in HEDGE_HEADS)
            or any(str(said or "").lower().startswith(prefix.lower())
                   for prefix in HEDGE_PREFIXES))
