"""Part 3 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re
import string

from .. import memory as mem
from ..compose import pick
from ..knowledge import cooking
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import named
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import keywords
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory import topics as said_topic
from ..understanding import kinds
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
from ..memory.narrow import asks_a_part, flat, kind_of as asked_kind
from .answers_part_01 import (
    SENTENCE, _flat,
)
from .answers_part_02 import (
    _about_a_lack, _says_it_leaves_it_out, _key_words, DESCRIBING,
)


def _hands_back_the_refusal(item, refused):
    """True when the entry is the thing the line ruled out and its answer does not skip it."""
    if not refused or not _is_about(item, refused):
        return False
    if _about_a_lack(item):
        # "no hot water" is not a person refusing hot water, it is a person with none: the entry
        # is keyed on the lack itself ("no hot water", "hot water gone"), so its reply is the
        # answer to the line. Without this the refusal reader stood `no-hot-water` down and a
        # three-word fault got "Got it. Is there anything you'd like a hand with?"
        return False
    reply = getattr(item, "reply", "")
    if callable(reply):
        # The entry worked its reply out for this line, so it has already taken the refusal
        # into account ("No onion then: a leek or a celery stick does the same job"), and
        # there is no fixed text here to read. Only an entry that stores a string can be
        # asked whether it says the thing was left out.
        return False
    return not _says_it_leaves_it_out(reply, refused)


def _from_another_domain(item, off_topic):
    """True when the entry is about neither the topic's words nor the topic's own kind of thing."""
    words, domain = off_topic[0], off_topic[1]
    if domain and str(getattr(item, "domain", "") or "") == domain:
        return False
    return not _names_a_topic_word(item, words)


def _names_a_topic_word(item, wanted):
    """True when the entry is keyed on one of the words, in any of their forms.

    Only the word itself or its stem: a looser match makes "plant" and "plan" the same thing,
    and the meal plan came back as an answer about tomato plants that way.
    """
    keys = {str(key).lower() for key in _key_words(item)}
    for word in wanted:
        if word in keys or said_topic.stem(word) in keys:
            return True
    return False


# Words that say how the ask is meant, not what it is about: "what should I change first" is a
# question about whatever the conversation is on, and "first" is in the keys of half the world.
BARE_GENERIC = frozenset("""first next best else last thing things way ways part bit most least
    change changing start starting stop stopping more right now then again still only just""".split())


# The verbs of asking, which name nothing on their own: "what should I look for" is a question
# about whatever the conversation has been about, "what could I bake for a birthday" is not.
ASKING = frozenset("""look looking wear wearing do does get getting pick choose need buy
    prepare bring bring take taking use check expect know say tell ask want find worth""".split())


# Asking what to say, rather than what to do: an answer about clothes or a timetable does not
# answer it, however well the topic fits.
SPEECH = frozenset("""say saying tell telling ask asking talk talking phrase wording word
    mention explain explaining""".split())


# A time says when, not what: an entry keyed to "june" is a holiday in the sun, and a move in
# June is not one. So a word the topic and the entry only share as a when never carries an entry.
TIME_WORDS = frozenset("""january february march april may june july august september october
november december jan feb mar apr jun jul aug sep sept oct nov dec monday tuesday wednesday
thursday friday saturday sunday weekend weekday morning afternoon evening night tonight today
tomorrow yesterday week weeks month months year years next this last first soon""".split())


def _topic_words(line, memory):
    """The words of the topic this line carries on from, without the words the line already
    says and without the words that only say when: those name nothing the entry can be about."""
    said = set(mem.content(line))
    record = mem.topics.carried_topic(memory or {}, line) or {}
    return [word for word in mem.content(record.get("text") or "")
            if word not in said and word not in BARE_GENERIC and word not in TIME_WORDS]


def _lent_words(reading, memory):
    """The words the topic lent this line when it was read with it.

    The topic can be the last line, which says little ("something funny but not stupid"), or the
    question two turns back that it belongs to ("what should I watch tonight"): the reading that
    was widened is the one that knows which of them the ask is really on, so its added words are
    what the entry has to be about.
    """
    line = str(reading.get("clean") or reading.get("text") or "")
    said = set(mem.content(line))
    wider = mem.followup_reading(reading, memory or {})
    added = str(wider.get("clean") or wider.get("text") or "") if isinstance(wider, dict) else ""
    words = [word for word in mem.content(added) if word not in said]
    if not words:
        return _topic_words(line, memory)
    return [word for word in words if word not in BARE_GENERIC and word not in TIME_WORDS]


def _same_word(word, said):
    """True when two words are the same word, endings and all: "friend" is not "friendship" but
    "friend" and "friends" are, and "ruin" and "ruining" are."""
    if word == said:
        return True
    if len(word) < 4 or len(said) < 4:
        return False
    return word.startswith(said) or said.startswith(word)


def _writes_its_own_reply(item):
    """True when the entry writes its answer from the reading instead of storing one.

    The weather answers are a function of the place and the month ("May in Rome is usually about
    15 to 24C"), so the entry's own text has the topic's words nowhere in it: `hits` is empty
    for every one of them however well the entry fits, and the check that an entry is about the
    topic cannot be made against the reply. Such an entry is reached only by the place and the
    month in the reading, which is the topic's own word, so it is about the topic by
    construction - and without this, "whats the weather like there" after "im going to rome in
    may" stopped being the figures and became "No live weather here, sorry" (main, where the
    only match was the widening and the guard turned it down).
    """
    return callable(getattr(item, "reply", None))


# The verbs a bare ask is made of, which name nothing an entry can be about: "what helps", "what
# works", "how do i fix it" are all questions about the thing the chat is already on.
ASKING_VERBS = frozenset("""help helps helped helping work works worked working fix fixes fixing
                         sort sorts sorted deal deals coping cope handle handles try tries""".split())


def _leans_on(reading, item, memory=None):
    """True when an entry reached only with the last topic belongs to the line's own words too.

    A short question with no subject of its own is read with the topic, which is what makes
    "what should I wear" an outfit question after a wedding. A question that names something of
    its own ("what could I bake for a birthday") must not be carried off to whatever the last
    turn was about: the entry has to be about one of the line's own words, in its keys or in
    what it says. And a line asking what to *say* needs an entry about words, not about clothes.
    """
    line = reading.get("clean") or reading.get("text") or ""
    line_words = mem.content(line)
    # A month or a season says when, not what: "and in october" after the Rome figures in May is
    # the same question about another month, and the month is the entry's slot rather than a
    # word in its keys, so it is not a subject the entry has to name.
    # A verb that is the ask itself is not a thing the entry has to be about: "what helps" after
    # the shower-drain answer is the same question about the same drain, and the drain entry does
    # not have to say "help" anywhere for that to be true. Without this the line counted "help"
    # as a subject of its own, the entry was read as not about the line, and the turn went to the
    # search hedge - while the same word in the entry's own paragraph ("what helps most") would
    # have made it a follow-up.
    own = [word for word in line_words
           if word not in ASKING and word not in BARE_GENERIC and word not in ASKING_VERBS
           and word not in mem.topics.MONTH_NAMES and word not in mem.topics.SEASONS]
    # "what should I change first" is all ask: no subject of its own and nothing but first/next
    # in it, so one shared word ("security") must not decide which entry answers it.
    vague = not own and any(word in BARE_GENERIC for word in line_words)
    keyed = _key_words(item)
    says = set(keyed)
    reply = getattr(item, "reply", "")
    if isinstance(reply, str):
        says |= {word.strip(string.punctuation).rstrip("s") for word in reply.lower().split()}
    topic = _topic_words(line, memory)
    carried = (mem.topics.carried_topic(memory or {}, line) or {}).get("text") or ""
    topic_text = " ".join(str(carried).lower().split())
    subject_of_the_topic = ([str(word).lower() for word in mem.key_subject(carried, memory)]
                            if carried else [])
    about = subject_of_the_topic or topic
    about_text = " ".join(subject_of_the_topic) or topic_text
    lent = _lent_words(reading, memory)
    hits = {word for word in lent if any(_same_word(word, other) for other in says)}
    # An entry that names what the topic is *not* is not about the topic: a phone that dies by
    # lunchtime is not the car battery the entry is written for, and its "phone" is in that
    # entry's avoid list. Saying so with the topic's words is the same test the line gets, but
    # only when the topic is all the entry has: a line that names the entry itself is its own
    # subject, and an entry that keeps feelings out of a packing question is still the packing
    # answer for "the packing is the worst bit" after a line about being stressed.
    avoid = getattr(item, "avoid", ()) or ()
    # Only a word that names something counts as naming the entry: "first" is in half the keys in
    # the world ("what happens at security first"), so the property words are left out here.
    named = [word for word in own if word not in PROPERTY_WORDS] or own
    names_it = any(_same_word(word, said) for word in named for said in keyed)
    # An entry that names what the topic is *not* is not about the topic: a phone that dies by
    # lunchtime is not the car battery the entry is written for, and its "phone" is in that
    # entry's avoid list. This one is checked even when the line names the entry ("should i get
    # the battery replaced" is about the phone), because the topic decides what the thing is.
    # A feeling in the topic is not a thing, though: an entry that keeps feelings out of a
    # packing question is still the packing answer for "the packing is the worst bit" after a
    # line about being stressed.
    def _it_says_it_is_not(phrase):
        """True when the avoid list names what the topic is: a word of the topic, or a phrase
        said across the topic's own sentence ("learn to swim" is two words of the topic list).

        It is the thing the topic is about that is tested, not the ask it made about it: the
        topic "when did the romans leave britain" is about the Romans in Britain, and "leave"
        is only what was asked there, so it does not make the length of the stay a different
        subject. The whole of the topic is used when its subject words are not known, which is
        where the test was before.
        """
        phrase = phrase.strip().lower()
        if not phrase or phrase in FEELINGS:
            return False
        return phrase in about or (" " in phrase and phrase in about_text)
    if any(_it_says_it_is_not(word) for word in avoid if isinstance(word, str)):
        return False
    if not own:
        # The line names nothing at all ("what can I do", "what should I change first"), so the
        # entry has to be about the topic by more than one word: a single generic word is enough
        # to take "security codes by text" to the airport scanner, which is a wrong answer where
        # an honest shrug is not.
        return len(hits) >= (2 if vague else 1)
    ask_side = [word for word in own if word not in PROPERTY_WORDS]
    if not ask_side:
        # The line names a property of the topic and nothing of its own ("what can we do before
        # the first day" in a thread about starting school), so the entry has to be about the
        # topic, not about the property: the words before/first/day decide no entry by
        # themselves, and every entry has a "day" somewhere in it.
        return bool(hits)
    if not any(_same_word(word, said) for word in own for said in says):
        if not _a_money_question(own, keyed):
            return False
        # The two ways of asking what a thing costs are one question, and an entry is written
        # with whichever of them the person it was written for would use: the Rome budget row is
        # keyed on "expensive", so "is that cheap" after the same trip was dropped here and the
        # search hedge went out while "is it expensive" got the price. "cost" and "price" are in
        # the family too, because the price rows are keyed with those words as well.
    if (not hits and not _writes_its_own_reply(item)
            and mem.topics.next_slot_reading(reading, memory or {}) is None):
        # The line names its own thing and the entry is not about the topic at all: it is only
        # the words the ask put back in that reached it, so the answer would be about something
        # else ("what should I pack first" answered with a holiday when the move is the subject).
        # A line that only names the next thing of the same ask ("and for lunch") is the ask
        # carried on rather than the topic, so the topic is not what the entry has to match.
        return False
    if set(line.lower().split()) & SPEECH and not says & SPEECH:
        return False  # "what should I say on the first day" is not a question about clothes
    return True


def _is_about(item, subject):
    """True when the entry is about the thing, not about a neighbour: a stew is not a steak."""
    words = [word for word in subject.split() if word not in DESCRIBING] or subject.split()
    head = (words or [""])[-1]
    head = head.rstrip("s") or head
    if not head or head not in _key_words(item):
        return False
    if head in kinds.VERBISH or (len(head) > 4 and head.endswith(("ed", "ing"))):
        # A whole clause can stand where the thing should be, and a clause puts its verb last:
        # "my headphones stopped working" is about the headphones, and the pension entry answers
        # "how long does it last" only because "working" is one of its keys ("stop working").
        # When the head is the verb, the entry also has to name something else the clause says.
        named = [word for word in words if word not in kinds.VERBISH
                 and not (len(word) > 4 and word.endswith(("ed", "ing")))]
        keys = _key_words(item)
        return any(word.rstrip("s") in keys or word in keys for word in named)
    return True


# Where a thing is cooked or kept is not a new subject: "how long does it keep in the fridge" and
# "how long in the oven?" stay about the food the last answer was about.
PLACE_WORDS = frozenset("""
fridge freezer oven grill hob microwave pan pans pot pots tray tin tins dish dishes shelf
cupboard counter worktop sink kettle toaster air fryer barbecue bbq fridge-freezer larder
room kitchen outside indoors
""".split())


# A reply that works a goal out at several rates each month, e.g. "£100 a month is 50 months".
SUM_TABLE = re.compile(r"£[\d,]+ a month is \d")


# A state of mind, not a thing the entry could be about: an avoid list keeps these out of a
# question about the subject ("not while you're stressed"), and the topic saying one does not
# make the entry about something else.
FEELINGS = frozenset("""stressed stress stressed-out worried worry anxious anxiety nervous sad
    upset feeling feelings scared afraid frightened terrified angry cross annoyed frustrated
    happy glad excited relieved tired exhausted shattered overwhelmed guilty ashamed embarrassed
    lonely fed-up down low rubbish awful terrible horrible upset gutted excited keen fuming
    panicking panic crying upset""".split())


PROPERTY_WORDS = frozenset("""long time times minute minutes hour hours day days much many far often temperature temp temps
degrees centigrade fahrenheit heat
hot warm cold size price cost spend pressure bar psi
spending pay paying per kilo kilos kg gram grams start finish last first take takes need needs
one ones
rest resting hard soft runny jammy medium rare fan gas thick thin large small whole skimmed semi
cook cooking bake baking roast roasting boil boiling fry frying grill grilling leave leaving
sit sitting wait waiting cool cooling chill chilling set setting
causing caused cause causes why reason worth worths valued value
# A date is a property of the answer too: after a dated answer, "when did that happen" and
# "what year was that" name the part they want and no subject of their own.
year years date happen happened done
""".split())


def _only_a_property(words):
    """True when the line names no subject, only the property it asks about."""
    return bool(words) and not [word for word in words if word not in PROPERTY_WORDS]


# A property word can also be the thing itself: a cold is an illness, a light is a lamp, a price
# is what something costs, a date is when it happens. The words are in PROPERTY_WORDS because the
# same word asks about a property ("how cold is it", "what price is that"), so the article is what
# tells the two apart. Without this, "i have a cold" -> "how long does a cold last" read the
# second line as a bare length ask about the first answer, and the greeting said how long a job
# takes instead of answering the cold.
PROPERTY_WORD_THAT_NAMES_A_THING = re.compile(
    # A determiner before the word makes it a thing: "a cold", "my light", "the price".
    r"\b(?:a|an|the|my|your|his|her|their|our|this|that|these|those|any|no)\s+"
    r"(?:colds?|heats?|lights?|darks?|prices?|costs?|sizes?|times?|dates?|years?|days?"
    r"|starts?|finishes?)\b"
    # A plural of one of these words is a thing even with no determiner: "how long do colds
    # last" was still read as a bare length ask, while "how cold is it" keeps the adjective.
    r"|\b(?:colds|lights|prices|costs|sizes|dates|starts|finishes)\b",
    re.I,
)


def _a_property_word_names_a_thing(text):
    """True when a property word in the line is the thing the line is about, not the ask.

    "how long does a cold last" is the cold's question; "how cold is it" is the sky's. Only a
    line that is otherwise all property words needs this test, so it is cheap.
    """
    return bool(PROPERTY_WORD_THAT_NAMES_A_THING.search(str(text or "")))


# What a thing costs, said either way round. A person asks "is it expensive" as often as "is
# that cheap", and a knowledge entry keeps one of the two in its keys, so an entry about the
# price is about both questions.
MONEY_ASK = frozenset("""
cheap cheaper cheapest expensive pricey costly dear affordable cost costs costing price prices
priced charge charges fee fees
""".split())


def _a_money_question(own, keyed):
    """True when the line asks what a thing costs and the entry is keyed on what a thing costs.

    The keys, not the answer's words: a bike-buying entry says "worth" and "check" and talks about
    a price in its answer, and it is not the price row the pronoun question is asking for.
    """
    return bool(set(own) & MONEY_ASK) and bool(set(keyed) & MONEY_ASK)


def _remember_answer(memory, item, reply, keys=()):
    """Keep what a follow-up can ask about again: the answer, what it is about, its turn.

    `keys` is for an answer that came from no entry: the words the answer was chosen for, when
    there is no entry to take them from.
    """
    if not isinstance(reply, str) or not reply.strip():
        return
    turns = memory.get("turns")
    memory["last_answer"] = {
        "reply": reply,
        "keys": sorted(_key_words(item) | set(keys)),
        "id": getattr(item, "id", None),
        "domain": getattr(item, "domain", "") or "",
        "turn": len(turns) if isinstance(turns, list) else 0,
    }


def _last_answer(memory):
    """The answer just given, while the conversation is still about the same thing.

    The answer has to be recent and from this module. A new topic ends the run, so "how long
    should I rest it" after a knee statement cannot reach the potatoes from three turns back.
    A detail line that stays on the subject ("my oven is fan assisted") does not end it: the
    answer is still about what is being said when the entry and the line share a word.
    """
    record = memory.get("last_answer")
    if not isinstance(record, dict) or not record.get("reply"):
        return None
    turns = memory.get("turns")
    if not isinstance(turns, list):
        return None
    turn = record.get("turn")
    if not isinstance(turn, int) or turn < 0 or turn >= len(turns):
        return None
    if len(turns) - 1 - turn > 4:
        return None
    said = turns[turn] if isinstance(turns[turn], dict) else {}
    if said.get("module") != "answers":
        return None
    topic = mem.current(memory)
    if not isinstance(topic, dict) or not isinstance(topic.get("turn"), int):
        return None
    if topic["turn"] > turn:
        here = set(keywords(topic.get("text") or ""))
        if not here & set(record.get("keys") or ()):
            return None  # a new subject started after the answer
    return record


def _asks_part(text):
    """True when the line asks for one part of the answer and names no subject of its own."""
    if asked_kind(text) == "cause" and not keywords(text):
        return True  # "why?" is the ask on its own
    if asked_kind(text) is not None:
        return _only_a_property(keywords(text))
    # A step or a property question names the part in its own words ("parboil", "crisp");
    # narrow() matches those against the answer and returns None when it cannot.
    return asks_a_part(text)


# A yes/no about a thing the last answer named: "will salt work", "does vinegar help", "can i use
# a hairdryer". The line names no subject of its own, so it is a question about the answer just
# given, and the sentence of that answer which names the thing is the part that answers it.
YES_NO_ABOUT_A_THING = re.compile(
    r"^\s*(?:will|would|does|do|did|can|could|should|shall|is|are|was|were|has|have|must|might)\b",
    re.I)


# Words a line uses about an answer rather than about a thing in it: "will salt work" asks about
# salt, and "work" is there because it is a yes/no, not because the answer has to say it.
# The words a line uses to ask a question of its own rather than to name a thing in the answer:
# a short line holding one of these is asking afresh ("what should i do", "how long?").
ASKING_FRESH = frozenset("""
what which how why when where who whose should would could can will shall do does did is are
was were need needs must if
""".split())


# An option offered with its own time ("tuna pasta in 15", "a frittata in 20"): two of them in
# one sentence make it a menu rather than an answer.
OPTION_TIMING = re.compile(r"\bin\s+\d+\b", re.I)


# A figure or a length of time in the line ("an hour", "2 days", "45 minutes").
DIGIT_OR_SPAN = re.compile(
    r"\d|\b(?:an?|one|two|three|four|five|six|seven|eight|nine|ten|twelve|fifteen|twenty|thirty|"
    r"forty|fifty|sixty|ninety|hundred)\s+(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|"
    r"weeks?|months?|years?)\b", re.I)


# A sentence that opens by pointing back is a continuation of the sentence before it, not an
# answer on its own: "There is chilli as well.", "It keeps for three days.", "That is the one."
DEPENDENT_SENTENCE = re.compile(
    r"^\s*(?:there|it|this|that|these|those|also|and|so|then|plus|but)\b", re.I)


ABOUT_THE_ANSWER = frozenset("""
work works working help helps helped use using used try trying need needs needed
better best good good idea worth right wrong okay ok actually really still just also
instead thing things way ways method enough any more much option
""".split())


# A "who should I call" about the thing in hand is answered by whoever the answer on the screen
# already names: "...that is a Gas Safe engineer", "get a roofer out". The ask carries the words
# of the asking ("who", "call") and none of the answer's, so every sentence reader above passes
# the answer by and the person was sent to a search engine about their own broken boiler. The
# trades are the ones the knowledge base sends people to; a sentence that says who to get is
# preferred over one that merely mentions somebody, so a leak answer gives "get a roofer out"
# rather than the line about the landlord.
WHO_TO_CALL = re.compile(
    r"^\s*(?:(?:so|and|but|ok|okay|then|also|right|now|sorry|hmm)[\s,]+)*"
    r"(?:who|which)\b(?:(?!\?).){0,40}?"
    r"\b(?:call|ring|phone|contact|get\s+(?:in|out|somebody|someone|a\\s)|ask|speak\s+to|"
    r"talk\s+to|come\s+out|do\s+i\s+get)\b", re.I)


A_TRADE = frozenset("""
engineer plumber electrician roofer locksmith glazier builder surveyor landlord
landlady letting agent council insurer insurance vet doctor gp dentist nurse optician
pharmacist mechanic garage sweep decorator plasterer joiner drain drains
""".split())


# A sentence that opens on a condition is advice for whoever the condition fits ("If you rent,
# tell the landlord"), not the answer to "who should I call".
CONDITIONS_THE_LINE = re.compile(r"^\s*(?:if|when|unless|where|in\s+case)\b", re.I)


OPENING_CONNECTIVE = re.compile(r"^(?:then|and|so|but|now|next|first|also)[\s,]+", re.I)


SAYS_TO_GET_SOMEBODY = re.compile(
    r"^\s*(?:then|so|and|now|next|first)?[\s,]*"
    r"(?:get|call|ring|phone|contact|ask|book|hire|find|use|see|tell|speak\s+to|talk\s+to)\b",
    re.I)


SOMEONE_TO_GET = re.compile(
    r"\b(?:call|ring|phone|get|ask|tell|book|find|hire|contact|use)\b", re.I)


# A detail added to the answer ("its a worcester bosch") is met with the store saying it back
# ("Got it - it's a worcester bosch"), and that stock line then sits between the answer and the
# ask. Only a stock line is stepped over: a turn that answered a question of its own is the
# answer this ask belongs to, and reading an older one would answer the last question but one.
STOCK_ACKNOWLEDGEMENT = re.compile(
    r"^\s*(?:got\s+it|noted|right|ok|okay|thanks|thank\s+you|of\s+course|sure|understood|"
    r"no\s+problem|fair\s+enough)\b", re.I)


ACK_MODULES = frozenset({"greeting", "memory_store"})


MOST_ACKS = 2


MOST_WORDS_OF_AN_ACK = 24


def _a_stock_acknowledgement(turns, back):
    """Whether the turn `back` from the end only handed part of the chat back, and nothing more.

    Two shapes: the store saying the person's own detail back ("Got it - it's a worcester
    bosch"), and the bot repeating a sentence of the answer before it ("A whistling boiler is
    usually the same pump or a flow problem"). Neither is a new answer, so the ask behind it is
    still about the answer before them.
    """
    turn = turns[-1 - back]
    if not isinstance(turn, dict):
        return False
    reply = str(turn.get("bot") or "").strip()
    if not reply:
        return False
    if turn.get("module") in ACK_MODULES and len(reply.split()) <= MOST_WORDS_OF_AN_ACK:
        if STOCK_ACKNOWLEDGEMENT.match(reply):
            return True
    before = turns[-2 - back] if len(turns) > 1 + back else None
    if isinstance(before, dict):
        earlier = flat(str(before.get("bot") or ""))
        said = flat(reply)
        if earlier and said and len(said.split()) >= 4 and said in earlier:
            return True
    return False


# A long sentence of an answer often does everything at once - the cause, the three jobs to do,
# and then who to get: "Banging or rumbling ... is usually air ...: bleed the radiators, check
# the pressure ..., and if it carries on get a heating engineer to look at the pump." Handing
# that whole sentence back is repeating the answer for an ask that only wants the last clause.
CLAUSE_BREAK = re.compile(r"\s*[,;:]\s*|\s+(?:and|but|then|so)\s+", re.I)


LONG_SENTENCE_WORDS = 24


def _the_clause_that_says_who(part):
    """The clause of a long sentence that names who to get, or the sentence as it stands.

    Only a clause that both names a trade and says to get them will do, and only when the
    sentence is long enough that handing it all back is repeating the answer. A short sentence
    is already the one thing the ask wants.
    """
    if len(part.split()) <= LONG_SENTENCE_WORDS:
        return part
    pieces = [one.strip() for one in CLAUSE_BREAK.split(part) if one.strip()]
    for piece in reversed(pieces):
        named = A_TRADE.intersection(re.findall(r"[a-z']+", piece.lower()))
        if named and SOMEONE_TO_GET.search(piece):
            piece = OPENING_CONNECTIVE.sub("", piece).strip() or piece
            return piece[:1].upper() + piece[1:]
    return part


# The words a "who should I call" is made of. A line with anything else in it names a thing of
# its own and is left to the entries.
WHO_ASK_WORDS = frozenset("""
who which what should shall do does can could would will might i we you they me my our
call ring phone contact get ask speak talk to about now then also just really
somebody someone anybody anyone person people trade tradesman professional expert
kind sort type best good right one out in come
""".split())


# A "which one" after a recommendation is the recommendation asked for again, and the answer
# is already in the reply the person has just read: "get 16GB of RAM and a 512GB SSD" is what
# decides it. Handing back the search shrug refuses a question the bot itself answered a
# moment ago, and handing the whole paragraph back is the machine thing STYLE names. Only a
# short line that names nothing of its own qualifies; a comparison ("which one is better, the
# iphone or the samsung") names the two things and has an answer of its own.
CHOICE_ASK = re.compile(
    r"^\s*(?:so |ok |okay |right |and |then )*(?:"
    r"which (?:one|ones|of those|of them|of these)"
    r"|which should i (?:get|buy|pick|choose|go for)"
    r"|which would you|which do you"
    r"|what (?:should|would) (?:i|you) (?:get|buy|pick|choose|go for)"
    r"|what do you recommend|what would you recommend"
    r"|any recommendations?|any suggestions?)\s*[?.!]*\s*$")


# ... and it is only about a choice when the answer it follows was about buying one. "which one"
# after a dripping tap, or after a list of dinners, is a line with nothing to pick from.
CHOICE_CONTEXT = re.compile(
    r"\b(?:buy|buying|bought|get|getting|purchase|recommend|recommendation|best|worth|"
    r"choose|choosing|pick|picking|upgrade|look for|looking for|which|new)\b")


# A word that is a size, a number or a spec: the sentence that decides between two things has
# one of these in it, and a sentence that only says why the thing is worth having does not.
A_SPEC = re.compile(
    r"\d|\b(?:gb|tb|mb|ghz|mah|kg|litres?|litre|ml|cm|mm|inch|inches|watt|watts|hours?|"
    r"minutes?|percent|pounds?|quid|years?|months?|weeks?|degrees?|spin|speed|drum|size|"
    r"tog|thread|bar|btu)\b")


# The sentence that decides is the answer, in the words the bot has already used, so all the
# reply adds is which part of the last answer this is. It goes after the sentence, not before:
# the answer comes first (STYLE), and a lead-in with a colon in it would be read as a list of
# options by the memory store.
CHOICE_TAIL = (
    "That is the bit that decides it.",
    "That is the one I would go for.",
    "That is what to go by.",
)


# A sentence that carries the spec is often a long one, with the rest of the answer after it:
# the pick is the clause that names the size, so a second clause is dropped when there is
# enough of the sentence left without it.
CHOICE_CUT = re.compile(r",?\s+(?:and |but |so |which |because )|;\s+")


CHOICE_SHORTEST = 60


def _the_clause_that_picks(sentence):
    """The first clause of a long sentence, when the rest of it is a second thought."""
    if len(sentence) <= 150:
        return sentence
    for found in CHOICE_CUT.finditer(sentence):
        start = found.start()
        if start >= CHOICE_SHORTEST:
            return sentence[:start].strip(" ,;")
    return sentence


# The thing to take is named inside the deciding sentence, not by it: the concrete one usually
# comes after the colon ("...: a 10 to 12 litre one"), and a list of things to choose between
# starts at its first item. Handing the whole sentence back is the last turn said again, which
# is the one thing a "which one?" reply must not be.
# A figure or a size in the thing itself is what a "which one?" is asking for: it is the part of
# the recommendation a person can act on, and an answer with none of it in it ("an air fryer is a
# small oven that blows hot air fast: chips, roast veg") has nothing to pick between.
CHOICE_FIGURE = re.compile(
    r"\d|\b(?:gb|tb|mb|ghz|mah|kg|litres?|ml|cm|mm|inch|inches|watt|watts|tog)\b", re.I)


CHOICE_LIST_HEAD = re.compile(r"\b(?:get|buy|make|go|choose|take|pick|spend|aim|look for|opt for)"
                              r"\b", re.I)


CHOICE_ITEM = re.compile(r",\s+")


CHOICE_LEAD_VERB = re.compile(r"^(?:get|buy|choose|take|go for|pick|look for|aim for|spend|opt for"
                              r"|go with)\s+", re.I)


CHOICE_CONDITION = re.compile(r"\s+(?:if|unless|when)\s+")


# A price is a figure too, and a sentence whose deciding figure is what a thing costs answers a
# "which one" with a number rather than a thing: "About 100 pounds is the usual gift" is not a
# choice to make, and neither is "a 10 to 12 litre one" once the figure has been cut off it.
CHOICE_COST = re.compile(r"[£$€]\s*\d[\d,.]*|\b\d[\d,.]*\s*(?:pounds?|quid|dollars?|euros?)\b", re.I)


# A price that opens a span and is then explained is a statement about money, not a thing.
CHOICE_PRICE_OPENS = re.compile(
    r"^(?:about|around|roughly|approx(?:imately)?|maybe|somewhere|up to|over|under)?\s*"
    r"(?:[£$€]\s*\d[\d,.]*|\d[\d,.]*\s*(?:pounds?|quid|dollars?|euros?))\b"
    r"(?=\s*(?:[a-z]+\s+){0,4}?(?:is|are|was|were)\b)", re.I)


# What is left of a price once it has been read as a price: the number, the currency and the
# words people put around a price ("about", "the usual", "going rate"). A span with nothing
# but those in it sized the thing without naming it.
CHOICE_PRICE_ONLY = re.compile(
    r"(?:about|around|roughly|approx(?:imately)?|maybe|somewhere|up to|over|under|less than|more"
    r" than|between)?\s*(?:[£$€]\s*\d[\d,.]*|\d[\d,.]*\s*(?:pounds?|quid|dollars?|euros?))"
    r"(?:\s*(?:to|-|and)\s*(?:[£$€]\s*)?\d[\d,.]*)?", re.I)


def _a_list_of_things(tail):
    """True when a clause lists three or more things, each a phrase of its own.

    A list of things to get is a run of short noun phrases ("a proper thermos, a voucher for the
    place she likes, a photo book of the family"). A sentence explaining why the advice is right
    splits on the same commas ("a 30 pound supermarket one sits too high off the neck, hurts your
    fingers and is why people stop after a fortnight") and every item in it is a whole clause, so
    an item longer than a phrase rules the list out.
    """
    items = [one.strip(" .!?") for one in re.split(r",\s*|\s+and\s+", tail)]
    items = [re.sub(r"^(?:or|and)\s+", "", one) for one in items if one]
    return (len(items) >= 3
            and all(2 <= len(one.split()) <= 11 for one in items))


def _the_thing_that_picks(sentence):
    """The shortest span of a deciding sentence that names the thing to take, or None.

    A recommendation has two halves when it has a colon at all: the things to get, and either the
    reason for them ("the running cost over ten years beats the purchase price difference") or
    the list itself ("a proper thermos, a voucher, a photo book"). Which half decides is read off
    the sentence: a list of things after an instruction is the list, otherwise the half with the
    figures in it wins. What comes back is one thing to take - never the whole sentence, because
    the whole sentence is the last turn said again - and None when the sentence names nothing a
    person could choose on.
    """
    span = sentence.strip()
    listed = sized = False
    if ": " in span:
        head, tail = span.split(": ", 1)
        head, tail = head.strip(), tail.strip()
        if len(tail.split()) >= 3:
            if (CHOICE_LIST_HEAD.search(head) and not CHOICE_FIGURE.search(head)
                    and _a_list_of_things(tail)):
                # "Make something she uses every week a bit nicer: a proper thermos, a voucher,
                # ..." - the instruction names no thing and says no figure, so the list is the
                # answer. When the head already sizes the thing ("Buy a used acoustic ..., 80 to
                # 150 pounds") the figures in it decide instead.
                span, listed = tail, True
            elif len(CHOICE_FIGURE.findall(head)) > len(CHOICE_FIGURE.findall(tail)):
                span, sized = head, True
            elif len(CHOICE_FIGURE.findall(tail)) > len(CHOICE_FIGURE.findall(head)):
                span, sized = tail, True
            else:
                span = head
    first = CHOICE_ITEM.split(span, 1)
    takes_the_figure = (len(first) == 2 and CHOICE_FIGURE.search(span)
                        and not CHOICE_FIGURE.search(first[0]))
    if len(first) == 2:
        if len(first[0].split()) < 2:
            return None  # "chips, roast veg and salmon" is a list of dishes, not of things to get
        if takes_the_figure:
            # The comma takes the only figure with it, and that figure is why this sentence decides
            # the choice: cut there and what is left is the why of the answer, not the thing the
            # why is about ("a proper pair makes a real difference to your knees"). The sentence
            # stays whole then, so the pick still carries what makes it a size to go by.
            pass
        else:
            span = first[0]
    span = CHOICE_LEAD_VERB.sub("", span)
    conditional = CHOICE_CONDITION.search(span)
    if conditional and conditional.start() >= 8:
        span = span[:conditional.start()]
    span = _the_clause_that_picks(span).strip(" ,;:.!?")
    if len(span.split()) < 2:
        return None  # one word is a noun to look up, not a thing to go and get
    if _a_price_and_nothing_else(span):
        return None  # a figure on its own answers "how much", not "which one"
    if listed:
        return span  # a list of things to get, and every item in it is a thing to get
    if sized or CHOICE_FIGURE.search(span):
        return span  # the part of the answer with the figure that decides
    return None


CHOICE_NOT_A_THING = frozenset("""
    about around roughly approx approximately maybe perhaps somewhere between up over under less
    more than to and or the a an it its that this these those is are was were be being been of
    for per at in on with without plus altogether total totals overall usually usual typical
    typically average norm normally going rate price prices cost costs cheap cheaper cheapest
    expensive budget spend spending paying pay paid altogether cheaper worth pounds quid dollars
    euros notes coins roughly
""".split())


def _a_price_and_nothing_else(span):
    """True when the span is a price rather than a thing, so it answers "how much", not "which".

    Three shapes of it: nothing but the figure and the words people put around a price ("About 100
    pounds", "90 to 130 pounds" - a figure beside a noun is a thing sized by that figure, so
    "16GB of RAM" passes); a price that opens the span and is then explained ("About 50 pounds is
    the usual gift"); and a price at the very end ("A good one is about 100 pounds"), where the
    span is only a way of getting to the number.
    """
    rest = CHOICE_PRICE_ONLY.sub(" ", span)
    if not any(word not in CHOICE_NOT_A_THING for word in re.findall(r"[a-z]{2,}", rest.lower())):
        return True
    bare = span.rstrip(" .!?")
    if CHOICE_PRICE_OPENS.match(bare):
        return True  # "About 50 pounds is the usual gift": the thing is the gift, not the figure
    ends = CHOICE_COST.search(bare)
    if ends and bare[ends.end():].strip(" .,!?"):
        ends = None
    return bool(ends)  # "... and fit you for 90 to 130 pounds": the span only leads to the number


def _the_composer_has_options(memory):
    """True when the bot's last answer offered named options the composer can pick between."""
    try:
        from ..compose import fallback as composer
        return bool(composer._offered(memory))
    except Exception:  # noqa: BLE001 - a composer that cannot be asked adds no reason to decline
        return False


# A question can put two things up without any word of buying in it: "should we go to spain or
# italy", "the train or the coach". `CHOICE_CONTEXT` reads the buying verbs, so a choice like
# that was invisible to the choice reader, and the answer was a shrug or a request that the
# person pick the thing the bot had already picked. The two things are the question's own words,
# and the answer's first word is one of them.
_AN_ALTERNATIVE = re.compile(r"\b(?:or|vs\.?)\b", re.I)


_NOT_AN_OPTION = frozenset("""a an the i we you it that this these those and but so if for to of
in on at by is are was were be been do does did would could should can will go get got one
both either neither""".split())


def _the_option_that_decides(said, reply):
    """The option of theirs the answer opened with, or '' when it opened with something else."""
    head = re.split(r"[.!?\u2014:;]", str(reply or "").strip(), 1)[0]
    in_the_question = set(re.findall(r"[a-z][a-z'\u2019-]*", said.lower()))
    for word in re.findall(r"[A-Za-z][A-Za-z'\u2019-]*", head)[:5]:
        low = word.lower()
        if low in in_the_question and low not in _NOT_AN_OPTION:
            return word
    return ""


def _the_answer_to_a_choice_behind(memory):
    """The answer that decided between two things the person put up, or None.

    A choice is not always asked again on the next turn. "should we go to spain or italy" is
    answered "Italy", then a detail about the kids, then "so which one" - and the answer on the
    screen is about the kids. Reading only that answer refused a choice the bot had already
    made. A line that offered two things is the one to read, and its answer's first word is the
    pick when it is one of those two.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for row in reversed(turns if isinstance(turns, list) else ()):
        if not isinstance(row, dict):
            continue
        said = " ".join(str(row.get("user") or "").lower().split())
        reply = str(row.get("bot") or "").strip()
        if not said or not reply or len(said.split()) > 16:
            continue
        if not _AN_ALTERNATIVE.search(said):
            continue
        option = _the_option_that_decides(said, reply)
        if not option:
            continue
        return f"{option[:1].upper()}{option[1:]}. That is the one I would go for."
    return None


def _the_one_to_pick(text, memory):
    """The sentence of the last answer that decides which one of the things to take."""
    clean = " ".join(str(text or "").lower().split())
    if not CHOICE_ASK.match(clean):
        return None
    if " or " in f" {clean} " or " vs " in f" {clean} " or "better" in clean:
        return None  # a comparison names the two things, and has an answer of its own
    earlier = _last_answer(memory)
    if not earlier:
        return _the_answer_to_a_choice_behind(memory)
    turns = memory.get("turns") or []
    turn = earlier.get("turn")
    before = ""
    if isinstance(turn, int) and 0 <= turn < len(turns) and isinstance(turns[turn], dict):
        before = str(turns[turn].get("user") or turns[turn].get("text") or "").lower()
    if not CHOICE_CONTEXT.search(before):
        return None  # nothing was being chosen before this line, so there is nothing to pick
    # The composer already picks out of a list it offered ("*Groundhog Day* for comedy,
    # *Knives Out* ..."), in the bot's own voice and with the note that goes with it. That pick
    # is better than handing a sentence of the last answer back, so this reader stands down.
    if _the_composer_has_options(memory):
        return None
    reply = str(earlier.get("reply") or "").strip()
    if not reply:
        return None
    sentences = [one.strip() for one in SENTENCE.split(reply) if one.strip()]
    if not sentences:
        return None
    choose_from = [one for one in sentences if not one.rstrip().endswith("?")]
    if not choose_from:
        return None
    # The answer's own first sentence is the recommendation (STYLE puts the answer there); a
    # later sentence only wins when the first one names no size, figure or spec at all and the
    # later one does, which is the answer that keeps its number in the second sentence.
    best = choose_from[0]
    if not A_SPEC.search(best):
        for sentence in choose_from[1:]:
            if A_SPEC.search(sentence):
                best = sentence
                break
    said = _flat(best)
    if not said or said == _flat(mem.last_bot(memory) or ""):
        return None
    pick = _the_thing_that_picks(best)
    if not pick or len(pick.split()) < 2 or _flat(pick) == _flat(mem.last_bot(memory) or ""):
        return None  # nothing shorter to say than the last answer: not a pick
    tail = CHOICE_TAIL[len(said) % len(CHOICE_TAIL)]
    pick = pick.rstrip('. ') or pick.rstrip()
    return f"{pick[:1].upper()}{pick[1:]}. {tail}"


# A meal idea states the whole dish's time in brackets ("I'd do dhal (30 minutes): ..."), and the
# step inside it keeps a count of its own ("simmer for 25 minutes"). "how long does that take"
# after that answer is asking about the answer we gave, so the bracket is the reply. Left to the
# part reader, the step's 25 minutes came back as the dhal's time when we had said 30, and on a
# diet answer whose closing sentence carries no number the line was not read at all: after "I'd
# do tomato pasta (20 minutes): ..." the bot asked "You haven't said - how long does that take?".
_DISH_TIME = re.compile(r"\(\s*(\d+)\s*(minutes?|mins?|hours?|hrs?)\s*\)")


# The same whole-dish time is written as a sentence of its own when the method comes first ("I'd
# do spaghetti bolognese: Brown the mince ... while the spaghetti cooks. 30 minutes, give or
# take."). A sentence that *starts* with the duration is the dish's; a sentence with the count
# inside it ("simmer it 20 minutes while the spaghetti cooks") is that step's.
_WORD_NUMBER = (r"\d+|an?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen"
                r"|twenty|thirty|forty|fifty|sixty|ninety|twenty[-\s]five|twenty[-\s]ten"
                r"|thirty[-\s]five|forty[-\s]five")


_A_WHOLE_TIME = re.compile(r"(__N__)(?:\s*(?:to|or|-|and a half)\s*(__N__))?\s*"
                           r"(minutes?|mins?|hours?|hrs?)\b".replace("__N__", _WORD_NUMBER), re.I)


_A_BARE_TIME = re.compile(r"^\s*(?:about\s+|roughly\s+|around\s+)?(?:%s)"
                          % _A_WHOLE_TIME.pattern, re.I)


# Only a line that asks the one thing points back at our answer. "how long should i rest it"
# after a meal has a verb of its own, and the dish's time is no answer to it.
# A dish named and then its time: "Curry: 35 to 45 minutes from scratch: 10 minutes of frying the
# onions ... then 25 to 30 minutes simmering." The whole time is the figure in front of the first
# colon, and the ones after it are the steps.
_A_LABELLED_TIME = re.compile(r"^\s*[A-Z][\w' -]{0,40}:\s*([^:.;\n]{0,90})")


# A figure is the dish's time only when it is the whole of what its sentence says: a rate ("20
# minutes per 500g plus 20 minutes at 190C, so a 2kg bird takes 1 hour 40") opens with a time and
# is not one, and a range written in two halves ("6 minutes for a soft egg, 10 for a hard one")
# opens with the lower end of a range that is the answer. What may follow the figure is only
# words that say the same time again another way.
_RATE = re.compile(r"\b(?:per|each)\b|\ba\s+\d+(?:\.\d+)?\s*(?:g|kg|lb|oz)\b", re.I)


# A sentence that states the time and nothing else may say it again in one of these ways and no
# other: "35 minutes, give or take", "Roughly 35 minutes in all", "Twenty minutes, no packet
# needed". A sentence that opens with a time and then explains something ("Two hours before
# departure is the safe rule") is not a sentence of its own about the time.
_TIME_TAIL = re.compile(r"^(?:give or take|in all|altogether|from scratch|start to finish|or so"
                        r"|no packet needed|flat|to make|total)?$", re.I)


_HOW_LONG_ONLY = frozenset((
    "how", "long", "many", "much", "does", "do", "did", "will", "would", "that", "it", "this",
    "them", "take", "takes", "then", "so", "roughly", "about", "and", "to", "cook", "make",
    "minute", "minutes", "mins", "hour", "hours", "time", "the", "a", "is", "are", "s", "for",
    "of", "altogether", "total", "start", "finish", "from", "scratch"))


def _one_total(rest, whole_sentence=False):
    """Whether what follows a figure in its sentence leaves that figure as the one total.

    Three ways the rest of a sentence takes the figure back: the time carries on with a number of
    its own ("1 hour 40"), a rate follows it ("per 500g", "for each kilo"), or the same clause
    gives another figure of its own ("6 minutes for a runny yolk, 7 for jammy, 9 to 10 for hard
    boiled" is a range written out, not one total). A second clause after a semicolon is a
    different way of doing the same dish and leaves the first figure where it is ("20 to 25
    minutes at 200C from frozen, turning once; an air fryer does them in 12 to 15"), and a
    temperature is not a time, so "25 minutes at 200C" is still 25 minutes.
    """
    rest = " ".join(str(rest or "").strip(" .,;:!?-").split())
    if rest[:1].isdigit() or _RATE.search(rest):
        return False
    # A number glued to a unit or a degree ("200C", "170C") is a heat, not another time.
    if re.search(r"\b\d+(?:\.\d+)?(?![\w\u00b0])", rest.split(";")[0]):
        return False
    if whole_sentence:
        # The sentence shape is the least certain of the three, so it asks the most: what follows
        # the figure has to be one of the ways of saying the same time again.
        return bool(_TIME_TAIL.match(rest))
    return True


def _the_dish_time(understood, memory):
    """The whole-dish time in the answer just given, when the line asks for it.

    A meal answer gives its total in one of three shapes, and each is read in turn because each
    is more certain than the next:

    * the bracket: "I'd do tuna pasta (15 minutes): stir a tin of tuna through hot pasta".
    * a sentence that states nothing but the time: "About 30 minutes.", "35 minutes, give or
      take.", "Twenty minutes, no packet needed."
    * a name and then the time in the very next words: "Curry: 35 to 45 minutes from scratch:
      10 minutes of frying the onions and spices, then 25 to 30 minutes simmering." A label in
      front of a list of three ("Quick: tuna pasta in 15, a frittata in 20, or ...") is not this
      one: the time has to be the first thing the label says.

    A count inside a step is a step, which is why the shapes are read in that order, and a figure
    only counts when the rest of its sentence leaves it as the one total: "About 20 minutes per
    500g plus 20 minutes at 190C, so a 2kg bird takes 1 hour 40" opens with a rate and "6 minutes
    for a runny yolk, 7 for jammy" opens with half of a range, so neither is a whole-dish time.
    Unless one of them names a single total, the answer does not give the dish's time and the
    turn is left to the reader it had.
    """
    text = str((understood or {}).get("clean") or "")
    if asked_kind(text) != "time":
        return None
    # The reading's words keep the pronouns `words_of` drops: a line with a verb or a food of its
    # own ("how long should i rest it", "how long do i boil an egg") names something else.
    words = [str(word).lower() for word in (understood or {}).get("words") or ()]
    if not words or [word for word in words if word not in _HOW_LONG_ONLY]:
        return None
    earlier = _last_answer(memory)
    if not earlier:
        return None
    reply = str(earlier.get("reply") or "")
    whole = None
    bracketed = {"%s %s" % (one.group(1), one.group(2).lower())
                 for one in _DISH_TIME.finditer(reply)}
    if len(bracketed) == 1:
        whole = bracketed.pop()
    if whole is None:
        sentences = set()
        for part in re.split(r"(?<=[.!?])\s+", reply.strip()):
            bare = _A_BARE_TIME.match(part)
            if bare and _one_total(part[bare.end():], whole_sentence=True):
                sentences.add(" ".join(bare.group(0).lower().split())
                              .replace("about ", "").replace("roughly ", "").replace("around ", ""))
        if len(sentences) == 1:
            whole = sentences.pop()
    if whole is None:
        labelled = _A_LABELLED_TIME.match(reply.strip())
        if labelled:
            # The time has to be the first thing the label says: "Curry: 35 to 45 minutes from
            # scratch: ..." is the dish, and "Quick: tuna pasta in 15, a frittata in 20" is a
            # list of three dishes that happens to open with a label.
            first = _A_BARE_TIME.match(labelled.group(1))
            if first and _one_total(labelled.group(1)[first.end():]):
                whole = (" ".join(first.group(0).lower().split())
                         .replace("about ", "").replace("roughly ", "").replace("around ", ""))
    if whole is None:
        return None
    # A food of its own that our answer never mentioned is a new question, not this one.
    for food in cooking.ingredients(understood):
        if str(food).lower() not in reply.lower():
            return None
    return "About %s for that one, start to finish." % whole


# A correction of a figure: "sorry i meant 1.5", "no, 1.5", "make that 4". What follows the
# frame is the figure itself, and a figure with no unit names no amount on its own.
CORRECTION_FRAME = re.compile(
    r"^\s*(?:(?:no|nope|sorry|actually|wait|hold\s+on|oops|oh|and|so|right|ok|okay)\b[\s,]*)*"
    r"(?:i\s+(?:mean|meant)(?:\s+to\s+say)?|make\s+that|sorry|no|nope|actually|wait)\b[\s,]*",
    re.I)


A_BARE_FIGURE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([a-z]{0,6})?\s*[.!]?\s*$", re.I)


# The unit a bare figure is missing, as the amount was last said: "2 kilos" makes "1.5" a weight.
A_UNIT = re.compile(
    r"\b\d+(?:\.\d+)?\s*(kg|kgs|kilos?|kilograms?|g|grams?|lb|lbs|pounds?|litres?|liters?"
    r"|l|ml|pints?)\b", re.I)


UNIT_WORDS = {"kilo": "kg", "kilos": "kg", "kilogram": "kg", "kilograms": "kg",
              "kgs": "kg", "gram": "g", "grams": "g", "pound": "lb", "pounds": "lb", "lbs": "lb",
              "litre": "litres", "liter": "litres", "liters": "litres", "pint": "pints"}


def _the_unit_last_said(memory, reply):
    """The unit of the last amount the conversation said, or None.

    The person's own "its 2 kilos" is the amount a "sorry i meant 1.5" corrects, so their words
    decide what the figure measures. A rate is not an amount to copy: the first figure in the
    chicken answer is the "500g" of "20 minutes per 500g".
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for said_turn in reversed(turns or []):
        said = A_UNIT.search(str(said_turn.get("user") or ""))
        if said:
            return said.group(1).lower()
    for said in A_UNIT.finditer(reply or ""):
        before = (reply or "")[:said.start()].rstrip().lower()
        if before.endswith("per"):
            continue  # the rate, not the size this answer was written for
        return said.group(1).lower()
    return None


def _the_figure_they_meant(text, memory, reply):
    """The correction as the amount it corrects to ("and for 1.5 kilos"), or None.

    Only a line that is a correction frame and then a figure, so "sorry i meant the other one"
    is untouched, and only when the figure comes without a unit of its own and the conversation
    has one to give it.
    """
    said_line = str(text or "")
    body = CORRECTION_FRAME.sub("", said_line)
    if body.strip() == said_line.strip():
        return None  # no correction frame in the line
    found = A_BARE_FIGURE.match(body)
    if not found:
        return None
    figure, unit = found.group(1), (found.group(2) or "").lower()
    if unit not in ("kg", "g", "lb", "l", "ml", "cm", "mm"):
        unit = _the_unit_last_said(memory, reply)
        if not unit:
            return None
    # The amount reader knows a short list of units: "1.5 kilos" is the same amount as "1.5kg",
    # and the long word is how people say it.
    return "and for {} {}".format(figure, UNIT_WORDS.get(unit, unit))
