"""Part 2 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re
import string

from .. import memory as mem
from ..knowledge import by_topic, home
from ..knowledge.lookup import find
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import named
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..understanding.kinds import ANSWERING_A_QUOTED_ASK
from ..memory import keywords
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory import topics as said_topic
from ..memory.topics import current as the_topic
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import keywords
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory.narrow import flat
from ..understanding import understand
from .answers_part_01 import (
    _flat, ABOUT_YOU, REFERRING,
)


# The words that ask for the rest of what the entry knows. A line with one of them is not asking
# about a part of the answer, it is asking whether there is more; a line with none of them ("and
# how long should i walk him") is asking to be answered, and the narrow reading or the repeat
# machinery answers it better than a claim that there is nothing further.
MORE_ASK = frozenset("""
    else more other others another anything something nothing everything different instead
    anyway anyhow otherwise
""".split())


def _asks_for_more(text):
    """True when the line asks for the rest of the answer rather than about a part of it."""
    return any(word in MORE_ASK for word in keywords(text))


def _the_answer_on_screen(memory):
    """The whole answer the person is looking at, which is the dictionary a lead-in may name from."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for turn in reversed(list(turns or ())[-2:]):
        if isinstance(turn, dict) and isinstance(turn.get("bot"), str) and turn["bot"].strip():
            return turn["bot"]
    return ""


def _already_said(reply, memory, keep=3):
    """True when the bot has just given this answer, with only a lead-in in front of it.

    A composer may put a sentence of its own before an entry's body ("Nerves before an
    interview are normal. Prepare four stories..."), and then the same answer comes back word
    for word without the openings matching. A reply that a recent answer *ends* with is that
    case. A reply the earlier answer only starts with is a part of it, which is how a follow-up
    is answered ("How do I fix it?" gets the steps of the last answer).
    """
    mine = " ".join(str(reply or "").lower().split())
    if not mine:
        return False
    for turn in (memory.get("turns") or [])[-keep:]:
        if not isinstance(turn, dict):
            continue
        bot = " ".join(str(turn.get("bot") or "").lower().split())
        if bot and (bot == mine or bot.endswith(mine) or _the_same_sentences(bot, mine)):
            return True
    return False


def _the_same_sentences(said, mine):
    """True when two replies are the same sentences with one of them moved to the front.

    A row that declares the sentence it owes a whether-line (`lead=("yesno", sentence)`) answers
    with that sentence first and the rest of the card after it, so the card that is on the screen
    is the entry's own reply with its sentences in a different order. Read as a string that is not
    the answer already given, and a follow-up about the card reaches it again as if new: "can i
    compost cooked food" / "and bones?" lost "The same goes for the bones: no cooked food or meat"
    and got the whole paragraph back instead.
    """
    if not said or not mine or said == mine:
        return False
    # Compared in lower case here rather than trusted from the caller: a call site that forgets to
    # flatten the case would otherwise make two replies the same sentences on case alone.
    parts = [part.lower() for part in re.split(r"(?<=[.!?])\s+", said) if part]
    others = [part.lower() for part in re.split(r"(?<=[.!?])\s+", mine) if part]
    return len(parts) > 1 and len(parts) == len(others) and sorted(parts) == sorted(others)


# "who are you", "what can you do", "where are you": a question about the bot carries no subject
# word either, so every follow-up reader in here took it as a question about the last thing
# discussed, and after "how do i cook rice" the person got "Same as before: Rinse it until the
# water runs clear" (brave-canoe, main watch). Understanding calls most of these about_bot and
# leaves a line with a subject of its own alone ("can you reheat rice", "what are you cooking" are
# not about_bot); the shapes here are the ones it misses, and they end where the line ends, so
# "where are you going on holiday" stays a holiday question.
WHO_IS_THE_BOT = re.compile(
    r"^\s*(?:so\s+|and\s+|ok\s+|okay\s+|but\s+|sorry\s+)?"
    r"(?:who|what|where)\s+(?:are|r)\s+(?:you|u)\s*[?.!]*$"
    r"|^\s*(?:what\s+can\s+you\s+do|what\s+do\s+you\s+do|who\s+made\s+you"
    r"|tell\s+me\s+about\s+yourself)\s*[?.!]*$",
    re.IGNORECASE)


# A line that asks how to answer a question is not a question to the bot about itself, even when
# the question quoted in it is about the bot: "how do i answer what are your weaknesses" is an
# interview question the person expects in a room with somebody else in it, and understanding
# reads the quoted words as the bot's own. The frame itself lives in the reading
# (`understanding.kinds.ANSWERING_A_QUOTED_ASK`), which stood the same reading down, so there is
# one definition of it and this is the same answer given to the composer.
def _asks_who_the_bot_is(understood, text):
    """True when the line asks who or what the bot is, not what the last answer was about."""
    text = text or ""
    if ANSWERING_A_QUOTED_ASK.search(text) and not WHO_IS_THE_BOT.search(text):
        return False
    if isinstance(understood, dict) and understood.get("about_bot"):
        return True
    return bool(WHO_IS_THE_BOT.search(text))


# The words an entry's own key uses when it answers a length ask. An entry found through a noun
# the action shares with it is not an answer to "how long": "im moving house" then "how long will
# it take" reached the deposit entry (which asks "how much", not "how long") because both say
# "house", and answered a question about moving with a figure about a Lifetime ISA. An entry may
# take the written-out ask only when its own key already reads a length, which is the entry
# saying that a length is one of the questions it answers.
LENGTH_WORDS = frozenset((
    "long", "soon", "months", "month", "years", "year", "weeks", "week",
    "hours", "hour", "days", "day", "minutes", "minute"))


# A length stated in an answer: a number of days, weeks, months, years, hours or minutes. A sum of
# money followed by a period ("\u00a3333 a month for five years", "\u00a34,000 a year") is a rate of
# payment, not a length, and an answer full of them (how to save a deposit, what a loan costs) is
# not answering "how long will it take" however many periods it mentions.
_A_LENGTH = re.compile(
    r"(?<![\u00a3$\u20ac\d.,])\b(?:\d{1,4}|a|an|one|two|three|four|five|six|seven|eight|nine|ten"
    r"|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty)\s+"
    r"(?:to\s+\w+\s+)?(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b", re.I)


# A length that is spent doing the thing, rather than a wait before it or a total to reach it:
# "20 minutes", "half an hour", "ten minutes a day". An answer that opens with one of these is
# answering "how long should i ..." in the form it was asked.
_A_DURATION = re.compile(r"\b(?:minutes?|mins?|hours?|hrs?)\b", re.I)


# An answer that defines the unit is not a length to spend doing the thing. "how long should i
# practise each day" reached the row that says what a day is ("A day is 24 hours - the time from
# one noon to the next") and that answer holds a figure of hours, so it looked like the length the
# person asked for. The unit's own definition answers "how long is a day", never "how long should
# i do this for".
_DEFINES_THE_UNIT = re.compile(
    r"^\W*(?:a|an|one|the)\s+(?:second|minute|hour|day|week|month|year|decade|century)s?\b"
    r"\W+(?:is|are|has|have|takes|lasts|means)\b", re.I)


def _answers_a_length(item, reply):
    """Whether this entry answers a length ask: its own key asks one and its answer gives one."""
    reply = str(reply or "")
    if not reply or any(mark in reply for mark in ("\u00a3", "$", "\u20ac")):
        return False
    if _DEFINES_THE_UNIT.match(reply):
        return False
    if not _A_LENGTH.search(reply):
        return False
    for part in getattr(item, "key", ()) or ():
        for phrase in part:
            if set(str(phrase).lower().split()) & LENGTH_WORDS:
                return True
    return False


def _the_article(subject, memory):
    """The article a rewritten line puts in front of the thing: "the " or, for a name, nothing.

    "im going to rome in june" then "is it expensive" is written out as "is rome expensive",
    because a name takes no article. "is the rome expensive" is not only wrong English, it is
    read as a different question: the price word is all the reading is about, so the domain the
    answer is in (travel) is one the reading never touched, the day rate is passed over, and the
    person gets the search hedge. Only the head of the subject is asked about, and only names the
    store has met count as names - a place, a person, a pet, the person themselves.
    """
    head = (subject.split() or [""])[0].strip(".,!?;:'\"").lower()
    if not head:
        return "the "
    user = memory.get("user") if isinstance(memory, dict) else None
    if not isinstance(user, dict):
        return "the "
    names = set()
    for key in ("name", "city"):
        value = user.get(key)
        if isinstance(value, str) and value.strip():
            names.update(word.lower() for word in value.split())
    for key in ("places", "people", "pets"):
        found = user.get(key)
        if isinstance(found, (list, tuple)):
            for value in found:
                if isinstance(value, str) and value.strip():
                    names.update(word.lower() for word in value.split())
    return "the " if head not in names else ""


# A follow-up can ask about a property of the thing without naming it: "what temperature should
# the oven be?" after a cake. These are the words that ask about a property, not about a thing.
PROPERTY = re.compile(r"\b(?:temperature|oven|gas mark|degrees|how long|how much|how many|"
                      r"minutes?|hours?|cost|price|expensive|when|how early|how hot)\b",
                      re.IGNORECASE)


def _about_subject(text, memory, about=None):
    """"What temperature should the oven be?" -> "... for the birthday cake?"."""
    asks_which_one = mem.KIND_ASK.search(text)
    if len(text.split()) > 14 or not (PROPERTY.search(text) or asks_which_one):
        return text
    subject = mem.subject(memory) if about is None else about
    if not subject or not mem.current(memory):
        return text
    wanted = [word.strip(".,!?;:").lower() for word in subject.split()]
    if any(word in text.lower() for word in wanted):
        return text  # it already says what it is about
    return text.rstrip("?.! ") + " for " + _the_article(subject, memory) + subject + "?"


# "what was I planning?" asks for the plan itself, and the store has it: read with the topic on
# the end it lands on the move-house checklist, which answers "how do I plan a move" instead of
# "you're planning to move house in March". "what's my plan?" is not here - that one is followed
# up with advice on purpose, because the person asking it wants the next step.
# "i need something for a headache" names the problem and asks for the thing that helps, and
# no entry is keyed on "something": the entries are keyed on the problem and on the ask ("what do
# i do for a headache", "what helps a headache", "what can i take for a headache"), so the vague
# frame the person put in front of the problem kept all of them out and the line was answered as
# a request for a suggestion ("Something for a headache? Tell me what you've enjoyed before and
# I'll suggest something."). The frame is read away and the rest asked as the question it is.
#
# It runs only where the lookup found nothing, so every line that has an answer keeps it, and the
# rest must name a thing rather than a person: "something for my mum" and "something to do with
# the kids" are the gift and the plans questions, which have answers of their own.
SOMETHING_FOR = re.compile(
    r"\b(?:something|anything|somef?in\w*|anyf\w*|summat|sommat|stuff)\s+"
    r"(?:for|to\s+(?:take|help|ease|soothe|settle|stop|calm|clear|put\s+on|rub\s+on|"
    r"drink|eat|use))\b\s*(.+)", re.I)


SOMETHING_FOR_PEOPLE = frozenset("""
mum mom dad mother father husband wife partner boyfriend girlfriend son daughter kid kids child
children baby brother sister friend friends gran granny grandma grandad grandpa nan aunt uncle
cousin nephew niece boss colleague neighbour neighbor her him them they us we people someone
anybody somebody everyone my his their our
""".split())


# Words at the end of the thing that say when, not what: "something for a headache now" is the
# headache, and the time is the ask ("fast", "quickly") rather than part of the problem.
SOMETHING_FOR_FILLER = frozenset("""
do doing use using later now anything something nothing else other general
""".split())


SOMETHING_FOR_TAIL = frozenset("""
please pls fast quickly quick now asap soon
""".split())


# A problem that is qualified by a pregnancy is not the plain problem. "what helps a headache in
# pregnancy" lands on whichever pregnancy row matches the ask word (back pain, heartburn), and a
# headache remedy handed to a pregnant woman is the ibuprofen problem: the qualifier changes the
# answer, so the frame is left alone and the line keeps the hedged reply it had before.
# The words behind "something for" that name *when* rather than *what*: a birthday, an
# anniversary, a wedding, an age. "get my dad something for his 60th" was framed as "what helps
# 60th", and there is no ailment in that reading - the line asks what to buy someone, which the
# gift rows answer. Kept as its own set because the frame is the only thing wrong with these
# lines: the thing they name is a date, not a problem.
_OCCASION_WORDS = frozenset("""
birthday birthdays bday anniversary anniversaries wedding weddings christening retirement
graduation leaving housewarming
""".split())


SOMETHING_FOR_STATE = frozenset("""
breastfeeding breast-feeding breast feeding trimester expecting
""".split())


# The give, the dose and the feed are what make the person in the line the patient: whatever
# comes back from the tables has to be right for them and not for a grown-up.
SOMETHING_FOR_GIVEN_TO = re.compile(
    r"\b(?:give|gives|giving|gave|given|feed|feeds|feeding|dose|dosing|treat|treating|use|using"
    r"|used)\s+(?:it to\s+|them\s+|him\s+|her\s+)?"
    r"(?:my|the|your|his|her|their|our|this|that|a|an)?\s*"
    r"(baby|babies|newborn|toddler|child|children|kid|kids|son|daughter|boy|girl|child|"
    r"teenager|teen|patient|mum|mom|dad|father|mother|partner|husband|wife|friend)\b")


def _keyed_on_the_person(item, who):
    """Whether the entry answers for this kind of person, not just for the word in the line.

    "can i give my son anything for a cold" reached the cool-bag entry on the words "can" and
    "cold", and that entry says nothing about a son. Only an entry whose own key names the
    person (a child, a baby, a toddler) is that person's answer.
    """
    if not who:
        return False
    keys = _key_words(item)
    person = who.rstrip("s")
    if person in keys:
        return True
    child = {"baby", "toddler", "child", "kid", "son", "daughter", "newborn", "boy", "girl"}
    return bool(keys & child) and (person in child or person in ("teenager", "teen"))


def _something_for(text):
    """The problem from "i need something for a headache" as a question, or "".

    "something for a headache" -> "what helps headache": the entries are keyed on the problem and
    an ask word, and this is the same ask in the words the tables use.
    """
    match = SOMETHING_FOR.search(_flat(text))
    if not match:
        return ""
    rest = [word for word in re.split(r"\s+", match.group(1).strip(" ?.!")) if word]
    # The article stays: the entries key the phrase as people say it ("a cold sore", "a nettle
    # sting"), and "what helps cold sore" is not the same row as "what helps a cold sore". A
    # possessive does not stay: "something for my hay fever" is a question about hay fever.
    while rest and rest[-1] in SOMETHING_FOR_TAIL:
        rest = rest[:-1]
    while rest and rest[0] in ("my", "your", "his", "her", "their", "our"):
        rest = rest[1:]
    if not 1 <= len(rest) <= 6:
        return ""
    # A date is not a problem to ask the tables about. "something for his 60th", "something for
    # my mums birthday", "something for the wedding" all name when the thing is for, and the
    # only thing the frame can do with them is invent "what helps 60th". "something for a
    # headache", "something for his back" and "something for the kids party" name a thing and
    # are untouched, and a bare age is read the same way.
    if all(word in _OCCASION_WORDS or re.fullmatch(r"\d{1,3}(?:st|nd|rd|th)?", word)
           for word in rest):
        return ""
    if {word for word in rest} & SOMETHING_FOR_PEOPLE:
        return ""
    if [word for word in rest if "pregnan" in word or word in SOMETHING_FOR_STATE]:
        return ""
    # "something to do with the kids", "something for later": the thing behind the frame is the
    # frame's own filler, and there is no problem to ask the tables about.
    if not [word for word in rest if word not in SOMETHING_FOR_FILLER]:
        return ""
    return " ".join(rest)


PLAN_RECALL = re.compile(r"\bwhat (?:was|were|am|are) (?:i|we) (?:planning|up to)\b|"
                         r"\bwhat did i say i (?:was|am) (?:planning|up to)\b|"
                         # One part of the plan asked for on its own is the same fact: "which
                         # month are we going" after a trip was answered with the travel entry
                         # for the country, and "when am i moving" with the moving checklist.
                         r"\bwhere (?:are|were|was|am) (?:we|i) (?:going|off|headed|heading|away)\b|"
                         r"\bwhen (?:are|were|was|am) (?:we|i) (?:off|going|away|moving|flying|travelling)\b|"
                         r"\b(?:which|what) (?:month|day|week|date) (?:are|am|is) (?:we|i)\b|"
                         # Only "that": "what day is it" asks what today is, not what the
                         # plan says, so the entry keeps that line.
                         r"\b(?:which|what) (?:month|day|week|date) (?:is|was) that\b",
                         re.IGNORECASE)


def _keeps_a_plan(memory):
    """Whether the store holds a plan to say back. A recall line with nothing kept stays here,
    where the topic's advice is better than "you haven't told me a plan"."""
    known = (memory or {}).get("user") or {}
    return bool(known.get("plan") or known.get("plans"))


# A line that asks what was said before is a memory question, not a question about the topic:
# "what did I call my cats?" after a scratching question is not another scratching question.
RECALL = re.compile(r"\bremind me (?:what|when|where|which|who|how much|how many|that|again)\b|"
                    r"\bdo you remember\b|"
                    r"\bwhat did (?:i|you|we) (?:call|name|say|tell|mention|order|ask)\b|"
                    r"\bwhat (?:do|did) (?:i|you|we) (?:call|name)\b|"
                    # "what do i order" is not a recall: it is what to order, and the place it
                    # names is the question ("what do i order at a kebab shop" was sent here and
                    # came back as a shrug). Only the past tense asks what was ordered.
                    r"\bwhat did (?:i|you|we) order\b|"
                    r"\bwhat (?:was|were) (?:i|we) (?:saying|talking about)\b|"
                    # "how did we start?" asks about this conversation, not about starting a
                    # savings plan: read with the subject on the end it becomes "how did we
                    # start save 3000 pounds car", which the savings entry would answer.
                    # "what have i told you?" is the memory store's whole picture, and read
                    # with the topic written back in ("... money") the savings entry answered
                    # it with advice the person had already been given.
                    r"\bwhat have i (?:told|said|mentioned)(?: you)?(?: so far| again)?\b|"
                    r"\bwhat (?:do|would) you know about me\b|"
                    r"\bhow (?:did|do) (?:we|you and i) (?:start|begin|open)\b|"
                    r"\bhow did (?:this|it|the (?:chat|conversation|talk)) (?:start|begin|open)\b",
                    re.IGNORECASE)


# "what am I planning?" is a question about the conversation itself: the plans memory keeps are
# the answer, and putting the subject on the end turns it into "planning holiday", which the
# holiday checklist then wrongly takes.
# A question about the person themselves: "what am i planning?", "where do i live", "how old am
# i". The answer is in memory, so the subject of the last turn must not be put back on the end of
# it: "where do i live" plus "a trip to rome" is the holiday checklist. Only a question about
# where or who they *are* counts: "where do i start" and "what do i say when they ask why i
# left" are questions about the topic, and they need the subject.
# A "when" that puts the person in the sentence as its subject - "when am i going", "when are we
# back" - asks about their own plan, and the plans memory is where the answer is. The modal forms
# ("when should i go") keep the topic: those ask what to do about it.
WHEN_AM_I = re.compile(
    r"\bwhen\s+(?:(?:am|are|was|were)\s+(?:i|we)\b|"
    r"(?:do|does|did|will)\s+(?:i|we)\s+(?:go|goes|going|leave|leaves|leaving|fly|head off|"
    r"set off|get back|be back)\b)", re.IGNORECASE)


ASKS_MEMORY = re.compile(r"\b(?:what|where|who|when|which|how old|how much|how many)\s+"
                         r"(?:am|was|were|is)\s+(?:i|we)\b|"
                         r"\bwhere (?:do|did|does) (?:i|we) (?:live|work|come from|belong)\b|"
                         r"\bwhat (?:do|did) you know about (?:me|us|my)\b|"
                         r"\bwhat(?:'s| is| was) (?:on|coming up)\b", re.IGNORECASE)


def _with_subject_tail(text, memory, understood=None):
    """The follow-up with what the conversation is about put on the end: "where do i start"
    after "I'm trying to save money" becomes "where do i start save money", which the knowledge
    base can answer. Empty when there is nothing to add, so the line is left alone."""
    tails = _subject_tails(text, memory, understood)
    return tails[0] if tails else ""


def _subject_tails(text, memory, understood=None):
    """The line with the subject on the end, longest subject first, then shorter runs of it.

    "what do i wear" after "a job interview at a warehouse on friday" is about the interview,
    but the whole gist ("job interview warehouse friday") can land on an entry already
    answered, so the shorter runs ("interview warehouse friday", "warehouse friday") are tried
    too and the first one that finds a new entry is the one used.
    """
    subject = mem.subject(memory)
    if not isinstance(understood, dict):
        understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = {}
    if not subject or len(text.split()) > 10 or len(subject.split()) > 4:
        return []
    if understood.get("kind") == "statement" or not understood.get("asks"):
        return []  # only a follow-up question is written out with the subject
    if understood.get("about_bot") or ABOUT_YOU.search(text):
        return []  # "do you cook much?" is about the bot, not about the dish just discussed
    if re.match(r"\s*(?:what|which|how|who|when|where|why)\b", subject, re.IGNORECASE):
        return []  # "what favourite food" is the leftover of a question, not a thing to name
    if RECALL.search(text) or ASKS_MEMORY.search(text):
        return []  # "what did I call my cats?" is a question for memory, not the topic
    said = {word.strip(".,!?;:").lower() for word in text.split()}
    if said & {word.lower() for word in subject.split()}:
        return []  # the line already says what it is about
    words = subject.split()
    if len(words) == 1:
        # A subject of one word is still a thing: "im thinking of getting a cat" then "what about
        # holidays" reached the work's paid holiday because the tail loop below only builds runs
        # of two words or more, so there was nothing to try and the line's own "holidays" was
        # the whole question. The entry still has to be named by this word and be about the
        # thing (`_named_by` and `_is_about` above), so a line that has nothing to do with the
        # cat is not answered from the cat's rows.
        return [text.rstrip("?.,! ") + " " + words[0]]
    tails = []
    for start in range(0, max(len(words) - 1, 0)):
        tail = " ".join(words[start:])
        if len(tail.split()) < 2:
            break
        tails.append(text.rstrip("?.,! ") + " " + tail)
    return tails


# A question that picks between things and names nothing to pick for: "what should I see?"
# after a trip, "what should I wear?" after an interview, "what could I get her?" after a
# birthday. The thing was said last turn, so the question is answered about it, in the words the
# verb takes: what you see is *in* a place, what you wear is *to* an occasion, what you get is
# *for* a person. Only a line that ends on the verb is read this way, so "what should I wear to
# the wedding" stays its own question.
CHOOSING = re.compile(r"(?:what|which|where)\s+(?:should|could|can|would|do|shall)\s+(?:i|we)\s+"
                      r"(?:[a-z]+\s+){0,2}?(?P<verb>see|visit|watch|play|do|eat|drink|try|wear|"
                      r"take|bring|pack|get|buy|cook|make|give|order|book)\s*"
                      r"(?:her|him|them|there)?\s*\??$", re.I)


# "what could i get her" names the person with a pronoun, and "what should we see there" points at
# the place rather than naming it: the thing under discussion is still the subject, so the line is
# read without the pronoun or the "there".
CHOOSING_PRONOUN = re.compile(r"\s+(?:her|him|them|there)\s*\??$", re.I)


PREPOSITION_OF = {}


for _prep, _verbs in (("in", "see visit watch play do eat drink try"),
                      ("to", "wear take bring pack"),
                      ("for", "get buy cook make give order book")):
    for _verb in _verbs.split():
        PREPOSITION_OF[_verb] = _prep


# The day or the month says when, not what: "job interview thursday" is an interview, and an
# entry keyed "interview" is the one to answer it.
HOLDING_A_NUMBER = re.compile(r"^\d+(?:st|nd|rd|th)?$")


WHEN_WORDS = frozenset("""january february march april may june july august september october
november december jan feb mar apr jun jul aug sep sept oct nov dec monday tuesday wednesday
thursday friday saturday sunday next this last tonight today tomorrow weekend week month year
morning afternoon evening""".split())


def _bare_subject(subject):
    """The subject without the words that say when or how many: "rome july" -> "rome".

    "mum 80th" is a question about mum, and an entry about presents for a mum is the one to answer
    it, so the number goes with the date.
    """
    words = [word for word in (subject or "").split()
             if word.lower() not in WHEN_WORDS and not HOLDING_A_NUMBER.match(word)]
    return " ".join(words) or (subject or "")


# An entry is written for one way of asking and not for another: "what should i get for mum"
# reaches the present entry and "what could i get for mum" does not. The modal is not part of the
# question, so the line is tried with each of them.
MODAL = re.compile(r"\b(?:should|could|can|would|shall|do)\b", re.I)


MODALS = ("should", "can", "could")


# The month the conversation named, when the line itself names none: the packing entry answers by
# season ("For a warm week: light cotton tops..."), so "what should we pack" about a trip in may
# reaches nothing until the may is put back in with the place.
MONTH = re.compile(r"\b(january|february|march|april|may|june|july|august|september|october|"
                   r"november|december)\b", re.I)


# A time word on its own is not a thing to choose for. "i'm getting married in june" leaves june as
# the topic, and "what should i wear to june" is the warm-weather packing entry - a wedding outfit
# answered with shorts and sun cream. So the subject has to be a thing the person named.
TIME_WORD = re.compile(r"^(?:january|february|march|april|may|june|july|august|september|october|"
                       r"november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|"
                       r"spring|summer|autumn|fall|winter|"
                       r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
                       r"today|tonight|tomorrow|yesterday|week|weekend|month|year|"
                       r"(?:next|this|last) (?:week|weekend|month|year|christmas|summer|winter|"
                       r"spring|autumn|fall))$", re.I)


def _the_month(text):
    match = MONTH.search(text or "")
    return match.group(1).lower() if match else ""


# The month only refines a trip. "i'm getting married in june" / "what should i wear" is a
# wedding outfit, and read with the month on the end it became the warm-weather packing entry -
# shorts and sun cream for a wedding. The conversation's own topic says which of the two it is.
TRIP_TOPICS = ("geography-and-travel", "travel", "holidays-and-trips")


def _a_trip(memory):
    """Whether the conversation is about going somewhere, so a month means a season there.

    The last few user lines are read, not just the last one: "we're going to lisbon in may" is
    followed by "it's me and my wife" often enough, and the trip is still the conversation.
    """
    lines = [((mem.current(memory) or {}).get("text") or "")]
    recent = mem.last_user(memory, 5)
    lines.extend(recent if isinstance(recent, (list, tuple)) else [recent])
    for text in lines:
        if not text or not isinstance(text, str):
            continue
        if any(topic in TRIP_TOPICS for topic in understand(text, memory).get("topics") or ()):
            return True
    return False


# A subject with a verb in it is a clause, not a thing. "my kids wont listen to me" leaves the
# subject "kid wont listen", and the shapes below hang a preposition on the subject ("what can i
# do in kid wont listen"), which is not a line at all: the entry it reaches off the one word
# "listen" is a fact from another part of the knowledge base. A thing - "marquee", "nan", "our
# anniversary" - takes the preposition honestly, and the ask's own verb ("what should i wear to
# marquee", "what do i get her") is what names the field.
FINITE = frozenset("""is are was were am be been being do does did dont doesnt didnt wont cant
couldnt shouldnt wouldnt isnt arent wasnt aint not never always keep keeps kept will would
should can could may might must have has had""".split())


def _a_clause(subject):
    """True when the subject carries a verb, so a preposition cannot be hung on it."""
    return any(word.strip(string.punctuation).lower() in FINITE for word in str(subject or "").split())


def _only_a_size_of(item, text):
    """True when every word of the line is this entry's own, a size, or the ask itself.

    "how long for 250g" is the chicken question about another weight, so its rate answers it.
    "how long do i roast a 2kg leg of lamb" names a thing this entry is not about, so the
    chicken rate must not be worked out for it.
    """
    words = _key_words(item)
    for word in mem.topics.keywords(text):
        if mem.topics.AMOUNT.search(word) or word in words:
            continue
        return False
    return True


# A person narrowing the choice without naming it: "something funny but not silly" after a film
# question, "nothing scary", "something shorter". The line names no thing and carries no key word
# of its own, so the knowledge base cannot read it: "funny" alone is 2 points against a threshold
# of 4. But the chat has just said what is being chosen between, so the same line with that word
# added ("something funny but not silly film") is one it can read - and it reaches the narrowed
# entry (`film-family-funny`) rather than the general one the bot has just given.
QUALIFIER_OPEN = re.compile(r"^(?:something|anything|nothing|everything)\b")


QUALIFIER_MAX_WORDS = 9


def _choice_words(text, memory):
    """The domain the chat is in and the word naming what it is choosing between.

    The head of the first key part of the entry that answered the topic: "film" for a film
    question, "meal" for a question about dinner. Nothing comes from the line itself, so a
    qualifier that names no thing is only ever rewritten towards the thing already being chosen.
    The topic is the line before this one: the store has already noted this line as the current
    topic, so reading that back would only hand the qualifier its own words.
    """
    line = " ".join(str(text or "").split()).lower()
    earlier = [one for one in mem.context(memory, 3)
               if " ".join(str(one).split()).lower() != line]
    topic = earlier[-1] if earlier else ""
    if not topic:
        return None, []
    found = []
    item = find(understand(topic, memory))
    for part in getattr(item, "key", ()) or ():
        options = (part,) if isinstance(part, str) else part
        # Every word of the first part, because a two-letter head leaves the rewrite unreadable:
        # the entry that answers "nothing on tv tonight" is keyed ("tv", "series", "watch"), and
        # "something funny tv" reaches nothing while "something funny watch" reaches the film
        # table. The head still comes first, so the plainest rewrite is tried first.
        for option in options:
            if isinstance(option, str):
                for word in option.split()[:1]:
                    if word.lower() not in found:
                        found.append(word.lower())
        break  # only the first part: the thing itself, not the words that qualify it
    domain = item.domain if item is not None else None
    return domain, [word for word in found if len(word) > 2]


def _qualifier_rewrites(text, memory):
    """The qualifier line with one word of the choice added, one rewrite per candidate word."""
    clean = " ".join(text.split())
    if len(clean.split()) > QUALIFIER_MAX_WORDS or not QUALIFIER_OPEN.match(clean.lower()):
        return []
    if not mem.current(memory):
        return []
    domain, words = _choice_words(text, memory)
    # A line that leaves a thing out ("anything but a horror") is still a narrowing and is still
    # rewritten: the entry it reaches first is the thing refused, and the refusal guard in
    # `_in_context` and `_offer` passes over that one to the entry that answers around it
    # ("skip horror and gore: *Knives Out* ..."), which is the answer the line is asking for.
    said = {word.strip(".,!?;:").lower() for word in clean.split()}
    rewrites = []
    for word in words:
        if word not in said:
            rewrites.append((clean.rstrip("?.! ") + " " + word, word, domain))
    return rewrites


# A line can refuse a thing in two shapes: the refusal is the whole line ("nothing funny",
# "no horror"), or it is the thing left out of a choice ("anything but a horror", "something
# except horror"). In the second shape the quantifier stands in for a thing, so whatever follows
# "but" is the thing refused, and read only for its own words the line reaches the entry for
# that very thing ("anything but a horror" reached the horror films, because "horror" was the
# one word in it the entries know). Only the bare shape counts as a refusal: "something quick
# but healthy" asks for healthy, and "something funny but not silly" leaves out a way of being,
# which is still a narrowing of the same choice and not a thing the entries answer by name.
#
# The negation alone does not decide it either, because "nothing scary" is a line the horror
# entry answers around ("skip horror and gore"): what matters is whether the answer respects the
# refusal, so the refused thing is what the entries are searched past, not what the line means.
REFUSE_OPEN = re.compile(r"^(?:nothing|no|not)\b(?:\s+(?:a|an|too|very|really))*\s+([a-z']+)", re.I)


REFUSE_CHOICE = re.compile(
    r"^(?:anything|something|everything)\s+(?:but|except|apart from|other than|besides)\s+"
    r"(?:not\s+)?(?:a\s+|an\s+|the\s+|any\s+)?([a-z']+)", re.I)


# The refusal a person makes by saying what they would rather not have: "i dont want a scary
# film", "i hate horror", "i cant stand gore", "im not a fan of musicals". The negation is the
# same one REFUSE_OPEN reads, and what sits in front of it is only a softener ("i really", "i
# just") and the want ("wouldnt want", "dont feel like"), which say nothing about the thing
# refused - but they were enough to stop the line being read as a refusal at all. "i dont want a
# scary film" reached the entry for scary films, whose own choice words ("want", "tonight") are a
# want, and the chat module nodded the line back: "Noted: you don't want a scary film". A want
# with "to" after it is an activity rather than a thing to leave out ("i dont want to cook
# tonight" is a cooking question), so the verb after it stops the match. So does a verb of
# knowing: "i dont know what job i want" rules nothing out, and read as a refusal of "know" it
# stood every row keyed on "dont know" or "no idea" down - the career answer survived only
# because its wording happened to carry the word "nothing" (lime-weasel, #answers 94483).
REFUSE_WISH = re.compile(
    r"^(?:i|we)\s+(?:(?:just|really|actually|honestly)\s+)*"
    r"(?:don'?t|do\s+not|didn'?t|wouldn'?t|won'?t|hate|dislike|loathe|"
    r"can'?t\s+stand|don'?t\s+like|not\s+into|"
    r"(?:im|am|'m)\s+not\s+(?:keen\s+on|a\s+fan\s+of)|not\s+a\s+fan\s+of)"
    r"(?:\s+(?:want|wants|wanting|need|needs|fancy|feel\s+like|like))?"
    r"(?:\s+(?:a|an|the|any|anything|something|everything|nothing|too|very|really|more|"
    r"another|much|lots|of|as))*"
    r"\s+(?!(?:to|be|have|go|get|do|see|watch|read|eat|cook|make|talk|hear|listen|work|"
    r"know|understand|remember|recall|decide|think|believe|reckon|guess|say|tell|imagine|"
    r"it|this|that|one|ones|thing|things|stuff|me|us|them|him|her|my|your|our|their|"
    # A verb of state or feeling is the want, not the thing wanted: "i dont feel anything" was
    # read as a refusal of the word "feel", and an entry about the feeling was stood down as the
    # thing the person had just ruled out, so "i dont feel anything for my baby" got a shrug
    # instead of the post-natal card. The words after the negation here are the want, not the
    # thing, so there is no refusal in the line.
    r"feel|feels|felt|feeling|want|wants|need|needs|fancy|like|likes|care)\b)"
    r"([a-z']+)", re.I)


# What an answer says when it is answering around a refusal rather than ignoring it.
REFUSAL_ACK = re.compile(
    r"\b(?:skip|avoid|steer clear|stay away from|without|instead of|rather than|except|nothing)\b")


# The phrases above that are also how a cooking answer compares two ways of doing something.
# "Wipe rather than wash them" says nothing about leaving the mushrooms out, so "rather than" is
# a refusal only when it stands next to the thing the line refused.
WEAK_ACKS = frozenset(("rather than",))


# A bare refusal is the whole line ("no horror", "nothing too scary"), so the refused word is the
# last one that means anything; only the kind of thing being chosen can come after it ("no sad
# films"). A "no" that is followed by where the thing is, or what it is for, is not a refusal but
# a lack: "no internet on my laptop", "no hot water", "no ideas for dinner". Those lines are about
# the missing thing, and the entry for it - the laptop's wifi, the boiler's hot water - is the
# answer rather than the thing to search past. Reading them as refusals used to throw that entry
# away and leave a line like "no signal on my phone" with an empty acknowledgement.
CHOICE_NOUNS = frozenset(
    "film films movie movies show shows series programme programmes book books game games "
    "music song songs thing things one ones stuff food meal meals recipe recipes".split())


SAID_POLITELY = frozenset("please thanks ta though".split())


def _a_lack_not_a_refusal(flat, end):
    """True when the words after the negated word say what is missing, not what to leave out."""
    for word in flat[end:].strip(" .,!?;:'\"").split():
        word = word.strip(".,!?;:'\"").lower()
        if word and word not in CHOICE_NOUNS and word not in SAID_POLITELY:
            return True
    return False


def _refused(text):
    """The word a line like "nothing funny" or "anything but a horror" rules out, if any."""
    flat = " ".join(str(text or "").split())
    match = REFUSE_CHOICE.match(flat)
    if not match:
        match = REFUSE_OPEN.match(flat)
        if match:
            if _a_lack_not_a_refusal(flat, match.end()):
                return ""
        else:
            # a wish said politely reads the same refusal out of the line
            match = REFUSE_WISH.match(flat)
            if match and _a_lack_not_a_refusal(flat, match.end()) \
                    and not _ASKS_AFTER_A_TASTE.search(flat[match.end():]):
                # The words after a taste are read the way the words after a "no" are, so "i
                # dont like the smell in my fridge" keeps the fridge-smell answer and "i dont
                # like spiders in my house" the spider one. A line that then asks for something
                # is not describing a thing, it is leaving it out of what it asks for: "i dont
                # like mushrooms what can i cook" is a dislike and an ask, and the ask is not
                # the thing that is short.
                return ""
    if not match:
        return ""
    word = match.group(1).strip(".,!?;:").lower()
    return word if len(word) > 2 else ""


# The ask that makes a taste a constraint on it: "i dont like mushrooms what can i cook", "i dont
# want pasta, what should i have instead".
_ASKS_AFTER_A_TASTE = re.compile(
    r"\b(?:what|which|anything|something|suggest|suggestions?|recommend|ideas?|instead|else|"
    r"can i|could i|should i|shall i|do i)\b", re.IGNORECASE)


def _says_it_leaves_it_out(reply, refused):
    """Whether the answer says the refused thing is left out, not merely uses the same words.

    "i dont like mushrooms what can i cook" reached the mushrooms row and was told "Wipe rather
    than wash them", which is how the answer describes a pan: the refusal acknowledgement was
    found in a sentence about something else, and the person who said they did not like the food
    got a recipe for it. A real acknowledgement says it about the thing the line refused - "No
    mushrooms then", "skip horror and gore", "without the cream" - so the phrase has to stand
    next to the refused word to count.
    """
    text = " ".join(str(reply or "").lower().split())
    word = str(refused or "").strip().lower()
    if not text or not word:
        return False
    named = re.compile(r"\b%s\w*\b" % re.escape(word))
    for found in REFUSAL_ACK.finditer(text):
        if found.group(0) not in WEAK_ACKS:
            # "skip horror and gore" leaves the thing out by naming what to avoid, which is
            # not the refused word itself (the line said "scary"), so the strong phrases count
            # wherever they stand.
            return True
        if named.search(text[found.end():found.end() + 40]):
            return True
        if named.search(text[max(0, found.start() - 30):found.start()]):
            return True
    return False


# A key that names the lack itself: "no hot water", "not heating up", "without an oven".
LACK_OPEN = re.compile(r"^(?:no|not|nothing|without)\b", re.I)


def _about_a_lack(item):
    """True when the entry is keyed on a thing being missing, not on choosing one."""
    for part in getattr(item, "key", ()) or ():
        options = (part,) if isinstance(part, str) else part
        for option in options:
            if isinstance(option, str) and LACK_OPEN.match(option.strip()):
                return True
    return False


def _key_words(item):
    """Every word an entry says it is about."""
    found = set()
    for part in getattr(item, "key", ()) or ():
        options = (part,) if isinstance(part, str) else part
        for option in options:
            for word in str(option).lower().split():
                found.add(word.rstrip("s") or word)
    return found


# How far into the line the thing a line names for itself can sit and still be its own subject:
# "my knee keeps clicking, is that normal" opens with its knee, "how do I bring it up without
# ruining the friendship" only mentions a friend at the end.
OWN_THING_AT = 3


# How far into a longer line the same search goes: "i really do hate my job" puts the possessive
# four words in, and the thing after it is still what the line is about.
OWN_THING_SCAN = 12


# The words that make the next word a thing of the speaker's own: "my back hurts" opens with a
# back, whether or not the understanding engine calls it an entity.
POSSESSIVE = frozenset("my our his her their".split())


# A person in the line is usually the one doing something, not the thing being asked about: "my
# son spilt juice on it" is a question about the juice. These words are checked only when the
# understanding engine has not tagged the person itself.
PERSON_WORDS = frozenset("""son daughter husband wife mum mom dad father mother partner
    boyfriend girlfriend brother sister kid kids child children baby toddler friend mate
    neighbour neighbor colleague boss teacher nan grandma grandad granny grandchild flatmate
    housemate lodger guest visitor landlord tenant aunt auntie uncle cousin nephew niece
    grandparent parents folks family
dog cat puppy kitten pet""".split())


def _names_a_thing(understood):
    """True when the line names something other than a person: the juice in "my son spilt juice
    on it", the knee in "my knee keeps clicking"."""
    for ent in understood.get("entities") or []:
        if isinstance(ent, dict) and str(ent.get("type") or "") not in ("person", ""):
            return True
    return False


def _own_thing(understood):
    """The thing the line itself opens with, when it opens with one.

    A line can lean on the last topic and still start a subject of its own: after a friend who
    keeps cancelling, "my knee keeps clicking, is that normal" is a knee question, and after a
    bottle of wine it is still a knee question. Nothing is named here for a line that only asks
    about the old thing ("how long will it take?", "he's allergic to nuts").

    A person is not that subject when the line names a thing as well: "my son spilt juice on it"
    after a sofa-cleaning turn is still a question about the juice, and the cleaning answer is the
    right one. A person on their own ("my mum keeps forgetting things") is a subject, and it is
    not the last topic.
    """
    person = ""
    for ent in understood.get("entities") or []:
        if not isinstance(ent, dict):
            continue
        at = ent.get("at")
        if isinstance(at, int) and 0 <= at <= OWN_THING_AT:
            text = str(ent.get("text") or "")
            if str(ent.get("type") or "") == "person":
                person = person or text
                continue
            return text
    if person:
        return "" if _names_a_thing(understood) else person
    boilerplate = str(understood.get("clean") or understood.get("text") or "").split()
    # "i hate my job" opens with no subject of its own if only the first word is read, and the
    # line then leans on the last topic and is answered as if it were still about it: after
    # "i love dogs and cats" the words put back on the end reached the cats-and-dogs entry,
    # because "hate" is one of its key words. The thing a line calls its own is the thing after
    # "my", "our", "his", "her" or "their" wherever that falls in the line, not only when the
    # line starts with it: "i really do hate my job" is a job line in the same way "my job is
    # awful" is.
    for at, word in enumerate(boilerplate[:OWN_THING_SCAN]):
        if word.strip(".,!?;:").lower() not in POSSESSIVE:
            continue
        if at + 1 >= len(boilerplate):
            break
        span = [w.strip(".,!?;:").lower() for w in boilerplate[at + 1:at + 4]]
        if not span or span[0] in REFERRING:
            continue
        # "my new sofa" is a sofa: the engine has already named it, and its name is the last word
        # of the phrase rather than the word straight after the possessive.
        named = _thing_named_in(understood, span)
        if named:
            return named
        second = boilerplate[at + 1].strip(".,!?;:")
        if second.lower() in PERSON_WORDS and _names_a_thing(understood):
            continue
        if second:
            return second.lower()
    return ""


def _thing_named_in(understood, span):
    """The thing the understanding engine named among these words, if it named one."""
    for ent in understood.get("entities") or []:
        if not isinstance(ent, dict):
            continue
        text = [w.lower() for w in str(ent.get("text") or "").split()]
        if not text or len(text) > len(span):
            continue
        for i in range(len(span) - len(text) + 1):
            if span[i:i + len(text)] != text:
                continue
            if str(ent.get("type") or "") == "person" and _names_a_thing(understood):
                return ""
            return text[-1]
    return ""


def _new_thing(own, answer):
    """True when the line names a thing the answer never mentions: a knee is not leftovers.

    "my knee keeps clicking, is that normal" after a leftovers answer leaned on the last topic and
    came back with the sentence about how long they keep, because "keeps" was the only word the
    two lines had in common.
    """
    if not own:
        return False
    words = {word.strip(".,!?;:").lower() for word in str(answer).split()}
    return not any(word.rstrip("s") in words or word in words for word in own.lower().split())


def _the_run_said(memory, extra=""):
    """What this run of answers has said, read as one answer.

    A follow-up can follow a follow-up: "how do i make pancakes for four", "how many eggs is
    that", "and how much flour". The third line names a thing from the first answer, not from
    the short line just before it ("2 eggs." does not mention flour), so asking whether the
    line names something new has to read the whole run, or every second follow-up looks like a
    new question and drops to the fallback.
    """
    turns = memory.get("turns")
    said = [str(extra or "")]
    answered = 0
    if isinstance(turns, list):
        for turn in reversed(turns):
            if not isinstance(turn, dict):
                break
            if turn.get("module") != "answers":
                if answered:
                    break
                continue  # the line just typed carries no module yet
            said.append(str(turn.get("bot") or turn.get("reply") or ""))
            answered += 1
            if answered >= 4:
                break
    return " ".join(part for part in said if part)


def _head_thing(subject):
    """The thing a subject names, when it names one: "my sourdough keeps going flat" is the
    sourdough. A subject that names no thing ("im training for a marathon" is about the
    training) gives nothing back, and the subject's own words are all the reading there is."""
    return _own_thing(understand(subject)) if subject else ""


# A word that only describes the thing is not the thing: after "how do i keep herbs fresh" the
# subject is "keep herb fresh", and the entry that keeps herbs is about the herb, not the fresh.
DESCRIBING = frozenset("""
fresh frozen cooked raw uncooked leftover leftovers ripe open opened unopened whole sliced cut
peeled dried dried-out tinned canned stale
""".split())


def _the_same_kind_of_thing(item, memory, text=""):
    """True when the entry's domain answers the topic the chat is on.

    The thing in hand is read by the understanding engine ("my back hurts" is a health line) and
    every knowledge domain declares the topics it answers (bot/knowledge.by_topic), so an entry
    whose domain answers that topic is about the same kind of thing as the chat however few
    words the two happen to share.

    The thing in hand is the one the follow-up is about, and a turn that adds a detail moves the
    topic onto the detail: "my back hurts" then "i use a strap already" then "do i need to see a
    physio" is still a question about the back, but the topic the store is on by then is the
    strap, which no health entry answers. A detail is recorded with the thing it is a detail of
    (`of`, see bot/memory/topics), so the line is read back through that chain, which is what
    `topics.carried_topic` does for the rest of the reader.
    """
    try:
        domain = str(getattr(item, "domain", "") or "")
        if not domain:
            return False
        record = (mem.topics.carried_topic(memory, text) if text else None) or the_topic(memory)
        said = str((record or {}).get("text") or "")
        if not said:
            return False
        about = str((understand(said, {}) or {}).get("topic") or "")
        return bool(about) and about in by_topic().get(domain, ())
    except Exception:  # noqa: BLE001 - a reading that fails leaves the guard as it was
        return False


# A line that adds a detail to what the chat is on - "i water them every day" after "my tomato
# plants have yellow leaves" - is a line about that thing and nothing else: the pronoun has no
# other thing to point at. Read in context it carries the topic's words along, but the detail's
# own words travel with it too, and on their own they reach an entry from somewhere else
# entirely: "water" and "every day" reached the daily figure for drinking water, "feed" and
# "every week" reached a meal plan. So the entry that answers such a line has to belong to the
# answer on the screen - its domain, or a word of the topic it is meant to be about. One that
# does neither is answering a different question.
DETAIL_OF = re.compile(
    r"^\s*(?:and\s+|so\s+|also\s+)?(?:i|we)\s+(?:also\s+|just\s+|still\s+)?(?:[a-z']+\s+)?"
    r"(?:it|them|they|him|her|these|those)\b", re.I)


# A question about the thing in hand - "how long will it take", "can i make it the day before" -
# names no thing of its own either: "it" and "that" are the thing the chat is on. Its own words
# are the leftover ones which reach an entry about the thing's neighbour: "how long will that
# take" after "im going to paint my kitchen" reached the kitchen-cleaning routine.
ASK_OF = re.compile(
    r"^\s*(?:and\s+|so\s+)?(?:how|what|when|where|which|who|should|shall|can|could|do|does|"
    r"did|will|would|is|are|was|were|if|any)\b", re.I)


OBJECT_PRONOUN = re.compile(r"\b(?:it|them|that|this|those|these|one)\b", re.I)


# What a line about doing something to the thing in hand is made of: the verb of the doing, and
# the words that make it a report of what they do rather than a question - an amount, a
# frequency, a time. A line naming a thing of its own ("i bleed the radiators every year") is a
# follow-up of its own kind and is left alone.
DO_VERBS = frozenset("""
water feed clean wash trim cut prune mow repot mist move cover drain bleed charge replace change
check add give take put turn leave run walk play use paint sand oil service tidy hoover dust
eat drink make cook bake freeze reheat serve store keep need want get buy pay sell work go come
""".split())


REPORT_WORDS = frozenset("""
day days week weeks month months year years morning evening night time times once twice daily
weekly monthly yearly every each a an all the at in on of and but to for with it them they him
her these those i we my our just still also really always never usually sometimes about
much many lot little bit twice three four five six two one few several
last next ago past
""".split())


# The asking words of a question that names no thing of its own, so a line made of these and an
# object pronoun is a question about the thing in hand: "how long will it take", "can i make it
# the day before", "should i freeze it".
ASK_WORDS = frozenset("""
how what when where which who why should shall can could would will do does did is are was were
if any ok okay please before after since until tonight tomorrow today again too soon often long
take need want have has keep use get put make cook freeze reheat serve store prepare
it that this these those them they him her one ones
""".split())


# A colour said of the thing in hand is that thing's property, not a thing of its own: "i painted
# it green last year" is a detail about the room, and "green" on its own reached the bag of salad
# in the fridge. The colour belongs to the line's own object, so it cannot make the line a
# follow-up in its own right.
SAID_OF_THE_THING = frozenset("""
red blue green yellow white black grey gray brown pink purple orange cream beige navy teal
turquoise lilac mauve magenta gold silver bronze ivory charcoal
""".split())


def _off_the_topic(understood, memory):
    """(the topic's key words, the domain of the entry that answers it, whether the line says what
    the thing is) when this line is a detail about that topic, else (empty, "", False).

    The third part is what tells a detail that names something of its own from a detail that only
    says what was done: "i painted it green last year" says what the room is, and the salad in the
    fridge was answering it; "i painted it last year" says what they did, and leaves the subject
    to the chat - so the fence below is only thrown around the line that says what the thing is.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return frozenset(), "", False
    text = understood.get("clean") or understood.get("text") or ""
    detail = "?" not in text and bool(DETAIL_OF.search(text))
    # A question with an object pronoun and nothing else of its own is about the thing too.
    asking = bool(ASK_OF.search(text) and OBJECT_PRONOUN.search(text))
    if not (detail or asking):
        return frozenset(), "", False
    allowed = (REPORT_WORDS | DO_VERBS | (ASK_WORDS if asking else frozenset())
               | (SAID_OF_THE_THING if detail else frozenset()))
    # Anything it names of its own makes it a follow-up in its own right: "i bleed the
    # radiators every year" says what it is about, so it is left to the entries as it is.
    # A word in the form a person puts a verb ending on is still the allowed word: "i painted it
    # green last year" said "painted" where the list holds "paint", so the line was read as one
    # naming a thing of its own and the salad in the fridge answered a question about a room.
    says_what_it_is = False
    for word in said_topic.words(text):
        if word.isdigit() or word in allowed or (said_topic.forms(word) - {word}) & allowed:
            if detail and word in SAID_OF_THE_THING:
                says_what_it_is = True
            continue
        return frozenset(), "", False
    leans_on = understood.get("leans_on")
    if not isinstance(leans_on, dict):
        return frozenset(), "", False
    said = str(leans_on.get("text") or "")
    if not said:
        return frozenset(), "", False
    # What the detail is about is the answer that is on the screen: the entry behind it, and the
    # topic's own words. An entry from another domain is answering a different question that
    # happens to have the detail's words in it.
    last = memory.get("last_answer") if isinstance(memory.get("last_answer"), dict) else {}
    domain = str(last.get("domain") or "")
    if not domain:
        home = find(understand(said, memory))
        domain = str(getattr(home, "domain", "") or "")
    # Only the topic's own nouns: the doing words are shared with every entry about doing
    # something, so "eat" in "she doesnt eat meat" does not make a workout answer about her.
    words = {word for word in said_topic.keywords(said)
             if word not in REPORT_WORDS and word not in DO_VERBS and word not in ASK_WORDS}
    return frozenset(words), domain, says_what_it_is
