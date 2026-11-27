"""Part 2 of 6 of a large module, split out of `arbiter`.

Everything here is re-exported from `arbiter`, so callers import it from there as before.
"""
import importlib
import re

from ..compose import badnews, fallback, leaving
from .arbiter_part_01 import (
    _reading, LONG_ENOUGH, WORD, CARRIES_NO_SUBJECT, FIRST_VERB, _the_same_plain_word,
    _an_answer_behind_the_ask, _asks_for_the_answer_again, _priority, _repeat,
    DECLARED_CLAIMS_INSTEAD, DECLARED_AS_IT_COMES, DECLARED_ABOUT_THE_CHAT, OWN_ABOUT_THE_CHAT,
    CARE_THREAD, THREAD, DECLARED_DEFERS, WHOLE_LINE_BAND, _naming, _harm, _dream, _loss,
    _STEP_WHEN_LOW,
)


def _a_bare_doubt_reply(candidate, text, memory):
    """Is this candidate the composer's own reply to a doubt with no range behind it?

    "my electricity is 90 a month" / "is that a lot" is a doubt about a figure, and the composer's
    answer to a doubt with nothing to judge against asks for a second figure ("90 a month is only
    high or low next to another figure for the same thing: what you were paying before... What was
    it before?"). That is the honest reply when nothing in the chat can place the figure - and it is
    not the answer when a card can: the electricity card says "No, that is normal for electricity
    for a typical home. £90 a month is £1,080 a year, and electricity... is usually £60 to £120 a
    month". The pool sits at `chat`'s priority 300 and the card at 0, so the hand-back won.

    The reading is the composer's own call, the same one the module makes (`reply_to_a_bare_doubt`),
    so the arbiter compares two replies rather than keeping a second copy of a wording.
    """
    reply = _content(candidate.get("reply"))
    if not reply or _reading is None:
        return False
    try:
        own = _content(_reading.reply_to_a_bare_doubt(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails is not a claim
        return False
    return bool(own) and own == reply


def _about_the_line(reply, words, clean=""):
    """Whether a reply names something of the subject the line is on.

    A topic label is not the subject: "i told the school and nothing happened" is read as a
    family-and-parenting line and a school-and-study line, and the entry that answered it was
    the sleep card ("Get up after 20 minutes of lying there awake ..."), which names nothing the
    person said. The candidate in front named the school and the meeting.

    So a lift by topic alone is checked against the words: a reply that shares one of the line's
    own subject words is about it, and a shared word is not enough on the other side of the test
    either - the candidate in front has to name what was said before a lift is held back at all.

    The words are compared as subjects, not as strings of letters. A card about eggs is about a
    line that says eggs, and `LONG_ENOUGH` dropped every word of three letters, so "one egg
    becomes 60g of yoghurt" named nothing of "my son wont eat eggs": the store's echo, which
    repeats the line, was `_about_the_line` and the card was not, so the lift was held back and
    the person got "Your son doesn't eat eggs." with no help in it. "my son wont eat egg" got the
    card, because there the two said the same letters. So the same crude stem `_subject_words`
    uses is what counts here ("egg"/"eggs", "bin"/"bins", "tap"/"taps" - three-letter subjects
    are ordinary), a filler word is not a subject at all, and only words of four letters or more
    are matched loosely, on a shared opening.
    """
    said = _subject_words(reply)
    if not said:
        return False
    for word in words or ():
        stems = _subject_words(word)
        if not stems:
            # A short or filler word: only a longer word may be matched loosely on it, the way
            # every word was matched before this test read subjects.
            if len(word) < LONG_ENOUGH:
                continue
            for one in WORD.findall(str(reply or "").lower()):
                if one.startswith(word) or word.startswith(one):
                    return True
            continue
        for stem in stems:
            for one in said:
                if one == stem:
                    return True
                if (len(stem) >= LONG_ENOUGH and len(one) >= LONG_ENOUGH
                        and (one.startswith(stem) or stem.startswith(one))):
                    return True
    return False


def _names_the_thing(word, reply, line_words):
    """Whether the reply is about the thing `word` names, not just holding the word.

    A shared word is not a shared subject. "there is blood in my pee" then "is that bad" was
    answered by the card for a blood test - "A blood test is a small sting and a vial or two" -
    because the card and the line share "blood", and the question was about blood in the person's
    water, not about having blood taken. The card opened on the word and went on to name something
    the line never did, so it was answering a question nobody asked (#general, the steer on a
    shared word; deck row `csp-01`).

    So a word of the thread that the reply opens on has to be the thing the opening is about: no
    fuller name may follow it inside the opening phrase ("blood test", "blood pressure", "car
    seat" for a line about blood or a car) unless that name is one the line has too ("blood in your
    pee" is the same blood). A reply the word appears later in is left alone: by then it is
    describing the thing, not naming a different one, so "A machine that bangs or walks across the
    floor is almost always an uneven load" still answers a line about the spin cycle.

    Whole words only, either way round with a plural: a shared pair of letters is not a shared
    word ("care" is not "car", "catch" is not "cat").
    """
    tokens = _content(reply).split()
    opening = []
    for token in tokens:
        if token in FIRST_VERB:
            break
        opening.append(token)
    for index, token in enumerate(tokens):
        if not _the_same_plain_word(word, token):
            continue
        if index >= len(opening) or token != word:
            # The word later in the reply is describing the thing by then, and an inflected form
            # ("toothache", "boiler's", "berries") is the thing itself: only the same token can
            # be the front of a fuller name ("blood test", "car seat").
            return True
        for after in opening[index + 1:]:
            if len(after) >= 3 and after not in CARRIES_NO_SUBJECT and after not in line_words:
                break
        else:
            return True
    return False


def _a_repeat_to_hold(memory, text=""):
    """Whether this line is an ask to hear the last answer again, with that answer to give back.

    The three halves the routing rules share, so no rule can drift from another: the line is made
    of nothing but the pointer (see `_asks_for_the_answer_again`), the last thing the bot said is
    an answer rather than a nod (`_an_answer_behind_the_ask`), and the ask names no measure of its
    own (`_names_a_figure`). A measure is a part of the answer - "how long did you say", "what time
    did you say" - and the store answers those with the part itself ("Sure - 18 to 20 minutes");
    the card that holds the number keeps the turn then, which is what
    `tests.test_a_repeat_ask_keeps_the_recall` pins.
    """
    return (_asks_for_the_answer_again(memory, text)
            and _an_answer_behind_the_ask(memory)
            and not _names_a_figure(text))


def _a_shorter_said_again(candidates, last):
    """The index of the composer's own shorter form of the last answer, else None.

    Asked only when every real candidate only says the last answer again (see `_choose`), and
    only for a line the composer wrote as a cut of that answer: the frame is the module's and the
    words behind it are the answer's own, in its own order. That is what makes it new - a person
    who typed "what did you say" has read the paragraph once already - and it is why a stock line
    in the fallback band is never taken for one.
    """
    if not last:
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) >= 0:
            continue
        if fallback.is_the_answer_shorter(candidate.get("reply"), last):
            return index
    return None


def _asks_a_question(memory):
    """True when the understanding engine read the line as a question, else False.

    "is that fair" after the answer about a dog on its own all day is a question, and chat's ack
    pool answered it "Sounds good." while the card beside it said the sentence with the verdict in
    it. The reading is the understanding engine's (`understood["kind"]`), so the arbiter keeps no
    words of its own for what a question is.
    """
    understood = (memory or {}).get("understood")
    if not isinstance(understood, dict):
        return False
    return understood.get("kind") == "question" or understood.get("intent") == "question"


def _asks_for_a_judgement(text, memory=None):
    """True when the line asks the bot to rule on the plan on the table, else False.

    The reading is the composer's (`bot/compose/judgement.py`), so nothing here is a second word
    list for "is that a good idea": the module that owns the pools decides what the ask is.
    """
    try:
        from ..compose import judgement
        return bool(judgement.asks_for_a_judgement(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False


def _hands_the_decision_back(reply):
    """True when the reply hands the choice back rather than answering the line.

    `chat`'s pool for "is that a good idea" says the decision is the person's to weigh and asks
    what matters to them ("I cannot call that one for you. Tell me what matters most about getting
    a cat..."). It is a better reply than the one it replaced, which signed the person off - and it
    is still not an answer to the line: it asks the question back. A take from under the floor that
    says the one thing the bot can say about the thing ("Yes, that is a reasonable way to do it -
    getting a cat is worth doing. The one thing...") is the answer, so a hand-back does not outrank
    it. Measured on twenty chats of a judgement asked after news: seven turns went from that answer
    to a hand-back (#6689), and every one of them read worse.

    The reading is the module's own: `chat` publishes `hands_it_back`, cut from its pools, so the
    arbiter keeps no wording of anybody's.
    """
    try:
        module = importlib.import_module(".chat", 'bot.modules')
        return bool(module.hands_it_back(reply))
    except Exception:  # noqa: BLE001 - a module that cannot answer counts as having answered
        return False


# The modules whose replies are pools of stock lines read off the line rather than answers held
# in a card: `chat` reads a mood or a kind of line and picks a line for it, and `greeting` is the
# floor itself. Everything else proposes from a table of its own about a subject.
POOL_MODULES = frozenset(("chat", "greeting"))


# A line that says something and then asks about it has two halves, and only the second one is a
# question: "my sister is veggie and shes coming to dinner, what can i cook" states a fact the
# person already knows and then asks something they do not. The clause that carries the ask is
# set off by a comma or a full stop and opens on the word it asks with.
THE_ASK_OPENS = re.compile(
    r"^(?:and |so |but |also |then |please )*"
    r"(?:what|how|which|where|when|who|why|any|ideas|thoughts|suggestions|advice|tips|"
    r"recommend\w*|should|could|shall|can|do|is|are|help)\b")


# The words that carry no content when a reply is held up against the line it came from.
ECHO_STOP = frozenset(("the", "and", "for", "you", "your", "with", "that", "this", "have", "has",
                       "was", "were", "are", "but", "not", "his", "her", "she", "him", "they",
                       "them", "its", "out", "about", "some", "from", "been", "what", "how",
                       "would", "will", "just", "one", "now", "day", "like"))


# The store says a line back in the second person, so the line's own words are read that way too:
# "my sister" comes back as "your sister", "i" as "you".
THEIR_VOICE = {"my": "your", "mine": "yours", "i": "you", "im": "youre", "me": "you",
               "myself": "yourself", "we": "you", "our": "your", "ours": "yours"}


def _the_ask_after_the_facts(text):
    """The ask at the end of a line that states something first, or "" when the line has none.

    Only a clause set off by a comma or a full stop counts, and only when it opens on a question
    word, so "my sister is veggie and shes coming to dinner" on its own is left entirely alone.
    """
    low = (text or "").lower().rstrip(" .?!")
    cut = max(low.rfind(","), low.rfind(";"), low.rfind("."))
    if cut <= 0:
        return ""
    if len(WORD.findall(low[:cut])) < 3:
        return ""
    ask = low[cut + 1:].strip(" .?!")
    return ask if THE_ASK_OPENS.match(ask) else ""


# The words that say nothing about a subject are written once, further down, beside the reader
# that uses them (`_subject_words`). This name used to be defined here as well, 950 lines from the
# copy that is read: the later definition is the one that wins, so this table never applied and
# `_names_the_subject` has always been read against the longer set. One definition, one truth.
# A word in a reply that could be the subject of the line: three letters or more.
A_SUBJECT_WORD = re.compile(r"[a-z']{3,}")


# The determiners that introduce the thing a line is about: "my bins", "the washing machine",
# "your landlord". Used to read the subject off the line itself, not off a list of subjects.
A_SUBJECT_PHRASE = re.compile(
    r"\b(?:my|our|your|his|her|their|the|this|that|these|those|a|an)\s+((?:[a-z']+\s+){0,2}[a-z']+)")


# The endings a word takes without becoming a different word: the plural, the past, the doing, the
# doer and the adverb. `walk`/`walking`, `coach`/`coaches`, `shower`/`showering`, `hop`/`hopping`.
WORD_ENDINGS = ("s", "es", "ed", "d", "ing", "er", "ers", "est", "ly")


def _one_word(one, other):
    """True when the two words are one word with an ending on, else False.

    A word that only *opens* the other is not the same word: `card` opens `cardiac`, `pain` opens
    `painting`, `care` opens `careers`, `read` opens `readable`, `star` opens `start`. Those were
    taken for the same subject by the first form of this test, which let a cardiac rehab card
    answer "my bank card was declined" and a book pick answer "im going to read before bed" - a
    reply kept because it matched on a word, which is the fault this test exists to stop. So the
    longer word is the whole of the shorter one plus one ending and nothing else, and an ending
    that starts with a vowel is only taken on a stem that ends with a consonant ("care" is not the
    stem of "careers"; that is "career" with a plural on it). A form this reads as a different
    word - "worry"/"worries", "tire"/"tiring" - costs nothing: the test is only used to give a
    reply credit for the line's subject, and a miss leaves the turn where it was.
    """
    shorter, longer = (one, other) if len(one) <= len(other) else (other, one)
    if shorter == longer:
        return True
    if len(shorter) < 4:
        return False  # "go" is not the subject of "going"
    tail = longer[len(shorter):] if longer.startswith(shorter) else ""
    if tail in WORD_ENDINGS:
        if not (tail[0] in "aeiou" and shorter[-1] in "aeiou"):
            return True
        return False
    # The last letter doubled before the ending: "shop"/"shopping", "stop"/"stopped".
    if tail[:1] == shorter[-1] and tail[1:] in WORD_ENDINGS:
        return True
    # The stem's "e" dropped before "-ing" or "-ed": "shine"/"shining", "smile"/"smiled".
    if shorter.endswith("e") and len(shorter) >= 5:
        for ending in ("ing", "ed"):
            if longer == shorter[:-1] + ending:
                return True
    return False


# A measure asked for on its own: "when did you say", "how long was it again", "what time was
# that". The answer is the part, not the whole of it, so the card that holds the number keeps the
# turn (`_names_a_figure`). Kept beside POINTS_BACK because it is the same kind of reading - the
# words a repeat ask is made of - and it is only read for a line that already points back.
A_MEASURE_ASKED = re.compile(
    r"\bwhen\b|\bhow\s+(?:long|soon|much|many|hot|warm|old|far|big|often)\b"
    r"|\bwhat\s+(?:time|temperature|day|date)\b", re.I)


def _names_a_figure(text):
    """True when the line asks for a number, time or amount rather than to hear it all again.

    Read with the store's own patterns (`repeat.FIGURE_ASKS`), as `the_figure_asked` reads the
    same line, so a figure ask added there is read here too.
    """
    line = str(text or "")
    if not line.strip():
        return False
    if A_MEASURE_ASKED.search(line):
        return True
    for figure in getattr(_repeat, "FIGURE_ASKS", ()) or ():
        try:
            _name, ask, _says = figure
        except (TypeError, ValueError):
            continue
        try:
            if ask.search(line):
                return True
        except AttributeError:
            continue
    return False


# The label the chat module declares is the kind of line, not a subject of the world. `ANSWERS =
# ("small-talk",)` in bot/modules/chat.py says which lines it answers, and every manners question
# is read as exactly that topic, so a declaration of it says nothing about who knows the line: the
# composer's own reading is the narrower one there. Left in, it settled a take the wrong way - after
# an answer, "hows your day been" gave way to the chat module's reply about the thing above (the egg
# answer, then the sentence about keeping boiled eggs in the fridge).
NOT_A_SUBJECT = frozenset(("small talk",))


def _a_question_about_the_bot(text, memory):
    """True when the line asks about the bot itself, else False.

    The reading is the composer's (`fallback.reads_as_about_itself`), the same one that makes the
    claim: a question about the bot's own make, limits or handling of what it is told. It is read
    here for the one thing the arbiter needs from it - that no entry about the world is a
    specialist on such a line - and a reading that fails is not one.
    """
    if not isinstance(text, str):
        return False
    try:
        return bool(fallback.reads_as_about_itself(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails holds nothing back
        return False


def _declares_claims_instead(module_name, text, memory):
    """True when the module says the claimed line is its own answer (README.md, "Interface")."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
        hook = getattr(module, DECLARED_CLAIMS_INSTEAD, None)
        return bool(callable(hook) and hook(text, memory))
    except Exception:  # noqa: BLE001 - a module that cannot answer claims nothing
        return False


def _declares_as_it_comes(module_name, text, memory):
    """True when the module says this line is one to answer as it comes (README.md, "Interface")."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
        hook = getattr(module, DECLARED_AS_IT_COMES, None)
        return bool(callable(hook) and hook(text, memory))
    except Exception:  # noqa: BLE001 - a module that cannot answer declares nothing
        return False


def _asks_about_the_chat(module_name, text, memory):
    """True when the module says this line is about the conversation, not about the world.

    The reading belongs to the module that has it (README.md, "Interface"): the memory store's
    gate already knows every recap shape, so `_fit` asks it rather than growing a second word
    list here. A module that cannot answer, or that raises, says nothing.
    """
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
        hook = getattr(module, DECLARED_ABOUT_THE_CHAT, None)
        if not callable(hook):
            hook = getattr(module, OWN_ABOUT_THE_CHAT, None)
        return bool(callable(hook) and hook(text, memory))
    except Exception:  # noqa: BLE001 - a module that cannot answer keeps the ordinary rules
        return False


# A step handed back in the answer's own words is one instruction, and the instruction is the
# sentence the answer wrote it in: "Give them sun, a big pot or grow bag, and water at the base
# regularly" is one move, and a module that stops it at the answer's first comma hands over half of
# it ("The first thing to do: Give them sun, a big pot or grow bag."). How long the whole sentence
# may run, and how much of a reply has to be the answer's words to count as its step, are the two
# numbers the rule already uses for a step. See `_the_whole_move`.
WHOLE_MOVE_WORDS = 60


CUT_MARKS = ",;:"


TOKEN = re.compile(r"[a-z0-9']+")


def _the_line_is_news(text):
    """Whether the line reports the thing the last answer was about coming back.

    Read by `_choose` to keep an answer announced as a repeat off a line that says the trouble has
    returned. The reading is `bot/memory/returned.says_it_happened_again`, which is where "the
    thing came back" already lives, so there is one definition of it rather than two.
    """
    try:
        from ..memory import returned
    except Exception:  # noqa: BLE001 - a memory lane that cannot be read treats the line as no news
        return False
    return returned.says_it_happened_again(text)


def _announces_a_repeat(reply):
    """True when a reply opens on one of the lead-ins the other lanes give an answer again in.

    Those lead-ins are the other lanes\' vocabulary, read here the way this rule reads the memory
    lane\'s leads elsewhere (`_a_lead_line`): "Same as before: {reply}" is `bot/memory/topics.py`\'s
    `REPEAT`, and "As I said: {reply}" is `bot/modules/answers.py`\'s `AGAIN`. A reply under one of
    them says it is giving the answer again rather than answering, and STYLE.md forbids saying the
    same thing twice in a row - so where every candidate left is the answer read out again, the
    one that does not announce itself as a repeat is the one to give.
    """
    said = str(reply or "").strip().lower()
    if not said:
        return False
    return any(said.startswith(lead) for lead in _repeat_leads())


def _repeat_leads():
    """The lead-ins the other lanes put in front of an answer they are handing over again."""
    leads = []
    try:
        from ..memory import topics as _topics
        for lead in getattr(_topics, "REPEAT_LEADS", ()):
            leads.append(" ".join(str(part) for part in lead))
    except Exception:  # noqa: BLE001 - a lane that cannot be read adds no lead-in
        pass
    try:
        from ..modules import answers as _answers
        for frame in getattr(_answers, "AGAIN", ()):
            head = str(frame).split("{")[0].strip().lower()
            if head:
                leads.append(head)
    except Exception:  # noqa: BLE001 - a lane that cannot be read adds no lead-in
        pass
    return tuple(leads)


def _carries_on(words, run):
    """True when `run` is a stretch of `words` with more of the answer's step after it."""
    length = len(run)
    for start in range(len(words) - length):
        if words[start:start + length] == run:
            return True
    return False


def _run_in_the_answer(words, tokens, answer):
    """The longest tail of these words that the answer says in one go: (words, end, index)."""
    for length in range(min(8, len(words)), 2, -1):
        tail = words[-length:]
        for start in range(len(tokens) - length + 1):
            if all(tokens[start + offset][0] == tail[offset] for offset in range(length)):
                return tail, tokens[start + length - 1][1], start + length
    return None


# The questions that ask for the cause of a thing failing rather than for comfort: a living thing
# going under ("why are my fish dying", "why are my plants wilting"), and the open ask that comes
# with it ("what am i doing wrong", "what is killing them"). A person is never diagnosed here, so
# the rule stands down on a line about one (see `_the_cause_asked_for`).
THE_CAUSE = re.compile(r"\bwhy\b[^,.;?!]{0,60}\b(?:dying|wilting|drooping)\b"
                       r"|\bwhat (?:am i|are we) doing wrong\b"
                       r"|\bwhat(?:'s| is| are) (?:killing|causing)\b")


# The words that make a line about somebody, so a condolence is the right answer to it and no card
# is asked for the cause of what is happening to them.
_PEOPLE = frozenset("""mum mom mother mum's dad father gran granny nan nana grandad grandpa
son daughter child baby wife husband partner boyfriend girlfriend brother sister friend mate
fiance fiancee aunt uncle cousin niece nephew he she him her his hers they them their people
person someone somebody anyone everyone""".split())


# The openers of a condolence, as every pool of them in the composer begins: "I'm so sorry to hear
# that", "I'm really sorry", "That's a real loss". A reply that opens this way is comfort, whatever
# else it says.
_CONDOLENCE = re.compile(r"^(?:oh\s+)?(?:(?:i'?m|i am|so|that'?s|that is)\s+)?"
                         r"(?:so\s+|really\s+|very\s+|truly\s+)?sorry\b"
                         r"|^that'?s (?:a real|such a|awful|terrible|heartbreaking)\b")


# The words of a line that name nothing, so a reply "naming" one of them is not about the subject.
_THE_NAMELESS = frozenset("""about after again also been before being both could does doing down
even every from have here into just like made make many more most much must need never only other
ought over same should since some such than that their them then there these they thing things
this those through under until very were what when where which while will with would your yours
really actually still might shall upon got gets going gone want wants wanted know knows saying
said tells told feel feels felt look looks looked take takes took today yesterday tomorrow week
month year time days just""".split())


def _my_workings():
    """The kinds the composer claims as questions about how it works, from the composer."""
    try:
        return frozenset(getattr(fallback, "MY_WORKINGS", ()) or ())
    except Exception:  # noqa: BLE001 - a set that cannot be read claims nothing
        return frozenset()


def _reads_as_a_verdict(text, memory=None):
    """The composer's reading of a line that is only a verdict on the news, or False."""
    reader = getattr(fallback, "reads_as_a_verdict", None)
    if reader is None:
        return False
    try:
        return bool(reader(text, memory))
    except Exception:  # noqa: BLE001 - a reading that cannot run claims nothing
        return False


def _in_a_careful_thread(clean, memory):
    """True while the conversation is inside a live emergency or its next line.

    A verdict after "my husband hit me" is not a light turn: the person is still in the thread
    the bot answered, and the composer's continuation ("You did the right thing telling someone.
    Stay with a person you trust tonight...") is the turn. `_verdict_pool` is a light pool, so it
    must stand down for the whole thread - the same judgment `_thread_index` makes, read here so
    the verdict rule cannot take the turn before that block is reached. The composer's own reader
    for the thread is asked first (it knows the wording), and the arbiter's own question after it
    (was the last word a safety answer) so a thread the reading misses is still not answered with
    a light line.
    """
    kind, _target = _composer_reading(clean, memory)
    if kind in (THREAD, CARE_THREAD):
        return True
    try:
        return bool(getattr(fallback, "in_a_safety_thread", lambda _memory: False)(memory))
    except Exception:  # noqa: BLE001 - a thread that cannot be read is not claimed
        return False


# The modules whose own answer to a verdict stands: both keep the conversation and read the line
# and the thread before they speak, so their answer is about the thing the verdict is about rather
# than about the verdict's word. A pool line is the right reply for the floor, the echo of the last
# answer and the search hedge, which is what this rule is for - not for an answer that already
# answered: "my dog died" then "what a shame" is a pet-loss card, and "im so tired" then "thats
# annoying" is the store's line about that tiredness. Standing the pool up over those traded the
# answer the person had just been given for a general line (gray-cypress, crisp-jackal on #5479).
# The fact store first: it answers with the thing the person said about themselves ("That kind of
# tired needs an early night, not more coffee") where chat answers for anyone.
KEEPS_ITS_OWN_ANSWER = ("memory_store", "chat")


# A card that answers the news keeps the turn too, but only by the news test - never by the
# opener. "my cat was put down yesterday" / "what a shame" got the pool line, and the card it
# stood down opens "I'm sorry, that's one of the hardest days. Nothing has to be decided today:
# the vet can arrange cremation" - the one thing the person can actually do (cowbird-note on
# #5479). The noun's own card cannot come in this way: the headache card is about a word of the
# verdict, not about the news, so `_about_the_news` is false for it.
ANSWERS_THE_NEWS = ("answers",)


# The line a module writes for the verdict itself opens by taking the verdict up ("It is.",
# "That would ... too", "You're right", "That kind of tired ..."), so that opener is one way an
# answer shows it is about this turn.
A_VERDICT_BACK = re.compile(
    r"^\W*(?:it\s+is|it'?s|it\s+does|it\s+doesn'?t|that\s+is|that'?s|that\s+would|that'?d|"
    r"that\s+kind|that\s+sounds|you'?re\s+right|you\s+are\s+right|yeah|yes|true|fair\s+enough|"
    r"of\s+course|same\s+here|i\s+know|i\s+don'?t\s+blame|anyone\s+would)\b")


# The words that only hold a sentence together, so they never make a reply "about" anything.
NOT_A_SUBJECT_WORD = frozenset((
    "the", "and", "but", "for", "with", "you", "your", "yours", "they", "them", "their", "his",
    "her", "hers", "she", "him", "our", "ours", "us", "its", "it", "that", "this", "these",
    "those", "was", "were", "been", "are", "am", "is", "be", "does", "did", "done", "have",
    "has", "had", "can", "cant", "cannot", "will", "would", "should", "could", "may", "might",
    "must", "not", "nor", "off", "out", "down", "too", "very", "really", "much", "many", "some",
    "any", "all", "more", "most", "just", "only", "then", "there", "here", "now", "how", "what",
    "when", "where", "why", "who", "which", "about", "than", "into", "onto", "over", "under",
    "again", "still", "even", "ever", "never", "get", "got", "gets", "one", "two", "put", "say",
    "says", "said", "think", "know", "like", "want", "need", "make", "made", "take", "took",
    "going", "went", "gone", "come", "came", "keep", "keeps", "kept", "let", "lets"))


def _subject_words(text):
    """The words of a line that could be what it is about, roughly singular.

    A crude stem on purpose: "landlords" and "landlord" have to match for the test below to hold,
    and the words a plural adds ("-es") are the same word to a reader.
    """
    words = set()
    for word in WORD.findall(str(text or "").lower()):
        if len(word) < 3 or word in NOT_A_SUBJECT_WORD:
            continue
        for ending in ("ies", "es", "s"):
            if word.endswith(ending) and len(word) > len(ending) + 2:
                word = word[:-len(ending)] + ("y" if ending == "ies" else "")
                break
        words.add(word)
    return words


def _about_the_news(reply, memory):
    """True when a module's answer names something in the news the verdict is about.

    The answer the pool must not take over is the one about the thing the person just told the
    bot about, and it says so with the news's own words: chat's "Landlords have to do most
    repairs in a reasonable time" is about the boiler, and the store's "That kind of tired needs
    an early night" is about the tiredness. The answers the pool must take the turn from are about
    the verdict's word instead: "Nightmares usually follow stress" for "what a nightmare" after a
    question about washing, and a scarecrow joke for "thats a joke" after a broken laptop. Both of
    those name nothing in the news, which is the reading here.
    """
    news = set()
    turns = (memory or {}).get("turns") if isinstance(memory, dict) else None
    if isinstance(turns, list) and turns and isinstance(turns[-1], dict):
        news |= _subject_words(turns[-1].get("user"))
        news |= _subject_words(turns[-1].get("bot"))
    return bool(news & _subject_words(reply))


def _says_the_same_thing_again(reply, last):
    """True when a candidate only re-tells the answer the bot has just given.

    A verdict on the news asks to be heard, not answered again. After "my washing machine is
    broken" the card's own second sentence came back as the answer to "what a pain" ("Check the
    cheap things before you pay anyone..."), and after the landlord letter "what a headache" got
    a second landlord paragraph. Both are the topic the last answer already covered, so the words
    say it: when most of what the candidate says is already in the last answer, it is a re-telling
    and not a second answer to the verdict (tidy-panther on #5479).
    """
    if not last:
        return False
    words = _subject_words(reply)
    said = _subject_words(last)
    if not words or not said:
        return False
    shared = words & said
    return len(shared) >= 2 and len(shared) * 2 >= len(words)


def _the_subject_was_answered(candidate, memory):
    """True when the module that answered last is now saying about this subject again.

    A verdict asks to be heard, not answered again. After the landlord letter, "what a headache"
    came back with a second landlord paragraph ("Landlords have to do most repairs in a reasonable
    time, and anything that came with the flat counts"), and that is the subject the last answer
    had already covered - so the pool is the turn, not another sentence on the same topic.

    Whose words they are is what separates the two (tidy-panther, cowbird-note, blue-hedgehog on
    #5479). The rest of the letter answer is the same module saying the letter again - `answers`
    both times, ten content words of the one before it. The card for a pet that died that opens
    "I'm sorry, that's one of the hardest days" comes from the card the person has not been given
    yet, after `loss` said its condolence, and the two paragraphs share the words every condolence
    in English shares: "sorry", "today", "gentle", "heavy". So it is not a re-telling at all, and
    a second answer to the same question is: the module that answered last, saying it again.
    """
    turns = (memory or {}).get("turns") if isinstance(memory, dict) else None
    if not (isinstance(turns, list) and turns and isinstance(turns[-1], dict)):
        return False
    last = turns[-1]
    if str(last.get("module") or "") != str(candidate.get("module") or ""):
        return False
    said = {word for word in _subject_words(last.get("bot")) if len(word) >= 5}
    return len(said & {word for word in _subject_words(candidate.get("reply")) if len(word) >= 5}) >= 2


# Where a two-part line puts its question. "a funeral on tuesday and i need something dark" names
# the situation in the first clause and asks in the last, and the same goes for a comma ("my phone
# screen cracked on holiday, where do i go to fix it").
ASK_CLAUSE_SPLIT = re.compile(r",|\band\b|\bbut\b|\bsince\b|\bbecause\b|\bso\b", re.I)


# A clause is an ask when it asks for something or names a thing to do, not when it describes the
# person: "my cat died and i keep crying" is about the person in front of us, and the pet-loss card
# answers it, so the crying is not an ask another entry can take the turn with.
ASKS_FOR_A_THING = re.compile(
    r"\b(?:what|which|where|who|whose|when|why|how|should|shall|can|could|do|does|did|is|are"
    r"|was|were|will|would)\b"
    r"|\b(?:need|needs|needed|want|wants|wanted|looking for|have to|has to|had to|got to|"
    r"gotta|after a|after some|in need of)\b")


def _the_ask_clause(line):
    """The words of the clause a two-part line puts its question in, else ().

    The last clause only when it carries the ask: two or more words and one of four letters. A
    line of one clause is not split at all, which is nearly every line, so the rule costs nothing
    on "my dad died in march".
    """
    text = str(line or "")
    if not text:
        return ()
    parts = [part.strip() for part in ASK_CLAUSE_SPLIT.split(text) if part.strip()]
    if len(parts) < 2:
        return ()
    last = parts[-1]
    if not ASKS_FOR_A_THING.search(last.lower()):
        return ()
    words = tuple(word for word in WORD.findall(last.lower()) if len(word) >= LONG_ENOUGH)
    if len(words) < 2:
        return ()
    return words


def _defers_to(module_name):
    """The declaring module's `DEFERS_TO` test on a reply, or None when it declares none."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
    except Exception:  # noqa: BLE001 - a module that cannot be read defers to nobody
        return None
    test = getattr(module, DECLARED_DEFERS, None)
    return test if callable(test) else None


def _asks(reply):
    """True when a reply is a question, so it is not a sign-off for a line that says goodbye."""
    return "?" in str(reply or "")


def _a_sign_off(reply):
    """True when a reply lets the person go (bot/compose/leaving.py owns the vocabulary)."""
    try:
        return leaving.reads_as_a_sign_off(reply)
    except Exception:  # noqa: BLE001 - a reading that fails adds no rule
        return False


def _a_leaving_said_plain(candidates, pool, clean, memory):
    """The index of the composer's reply to a leaving said as the news it is, or None.

    "my husband has left me" is the news, not a question about money, and the entry for a
    divorce answered it with the first job of a settlement: "Get the money apart quietly and
    early: open a current account in your own name". A plan for the day is not an answer to
    having just said your life has come apart - STYLE.md's worst reply is the one that reads as
    not having heard - so when the reply in front of this line hands over a job, the composer's
    line that hears it takes the turn.

    Only the line that says nothing else. An ask is answered by the entry ("my husband has left
    me, where do i stand on the house"), and so is a reply that already hears it (the entry for
    the same news says "Nothing you do this week makes it hurt less, so do not make decisions in
    it", which is not a job). The reading is bot/compose/badnews.py's and the wording is
    `fallback.LEFT_POOL`'s, so this is only the routing decision.
    """
    if not clean:
        return None
    try:
        if not (badnews.reads_as_the_leaving(clean)
                or badnews.reads_as_a_leaving_already_gone(clean)):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    understood = memory.get("understood") or {}
    if (understood.get("kind") == "question"
            or understood.get("intent") in ("question", "request")
            or understood.get("help_ask") or understood.get("asks_a_verdict")):
        return None
    index = _is_loss_reply_in(candidates, pool,
                              pools=(fallback.LEFT_POOL, fallback.LEFT_POOL_GONE))
    if index is None:
        return None
    best = pool[0] if pool else None
    if best is None or not _opens_on_a_job(candidates[best].get("reply")):
        return None
    return index


def _sudden_loss_reply(candidates, pool, clean):
    """The index of the composer's reply to a sudden loss, or None.

    A pregnancy that has ended and a suicide among the people a person knows are read here
    rather than only in the gentle pool, because the pool's words ("that's frustrating, want a
    hand working out the next step") are for a setback, and because a module with a general
    bad-news line must not answer a bereavement as one. Bleeding in pregnancy comes with them:
    it is a midwife today, not a chat.

    The reading lives in bot/compose/badnews.py and the wording in bot/compose/fallback.py, so
    this is only the routing decision: when the composer has a line for this, it gets the turn.

    One ask is not a condolence: "my husband died in march and i dont know how to tell our
    daughter" wants the words to say to the child, and the knowledge base has them
    (`explaining-death-to-a-child`). The composer's own reading says when the ask is that
    (`fallback.asks_what_to_tell_a_child`), and on the day itself it says no, so a fresh death
    keeps the condolence whoever else proposed.
    """
    try:
        if not clean:
            return None
        if not (badnews.reads_as_sudden_loss(clean)
                or badnews.reads_as_pregnancy_bleeding(clean)):
            return None
        if fallback.asks_what_to_tell_a_child(clean) and _a_knowledge_entry_has_it(candidates):
            return None
        pools = (fallback.SUDDEN_LOSS, fallback.PREGNANCY_BLEEDING,
                 fallback.THE_FIRST_HOUR_AND_A_CHILD)
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    return _is_loss_reply_in(candidates, pool, pools)


def _a_whole_line_module_spoke(candidates):
    """True when a module that reads a whole line (grief, loss) has an answer of its own.

    Those modules answer the same follow-up better than a pool can: grief's `TELLING_REPLIES`
    has the name and the day ("\"your wife died on Tuesday\" is kinder than a soft way round
    it") where the child's words are three lines about how to say it at all. The reading is
    there for the turn those modules leave alone - the ask with no name in it, "how do i tell a
    4 year old", which grief reads as no question it knows and passes. So it stands aside the
    moment one of them speaks, the same way `_the_subject_was_answered` does for a card.
    """
    for candidate in candidates:
        if _priority(candidate) >= WHOLE_LINE_BAND and candidate.get("module") != fallback.FALLBACK_MODULE:
            return True
    return False


# A how-to about someone else is not about the speaker. "how do i stop my teenager staying up all
# night" was answered by the small-talk card written for the speaker's own night ("That's a hard
# one to carry into a day. Go easy on yourself today and aim for bed an hour earlier tonight"),
# with the entry that has the answer ("in the teen years the body clock shifts later by up to two
# hours") underneath it at a lower PRIORITY. The card never mentions the person the line is about.
# So on a how-to line that names someone else, a card that says nothing about them is passed over
# for a reply that does - the answer to "how do I stop my teenager" cannot be about my night.
# Only cards below the recall band are passed over (7000 and the safety band are answered as they
# come), and only for a knowledge entry that does say something about the person.
_A_HOW_TO = re.compile(
    r"^(?:how\s+(?:do|can|should|could|would)\s+(?:i|we|you)|how\s+to\b|"
    r"what(?:'?s|\s+is)\s+the\s+best\s+way\s+to|whats\s+the\s+best\s+way\s+to|"
    r"any\s+tips\s+(?:for|on)|what\s+should\s+i\s+do\s+(?:about|with))\b", re.I)


# The person the line is about, said as a relation rather than a name ("my teenager", "our son").
_THE_ONE_NAMED = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:teenager|teen|son|daughter|child|kid|boy|girl|mum|mom|"
    r"mother|dad|father|partner|husband|wife|boyfriend|girlfriend|flatmate|housemate|roommate|"
    r"friend|boss|manager|colleague|brother|sister|gran|granny|grandma|grandad|grandpa|baby|"
    r"toddler|nephew|niece|aunt|uncle|cousin)\b", re.I)


# Any person a line names, in either form: the relation a how-to is about ("my teenager") or
# somebody it meets by article ("a friend"). Only the first one in the line decides, because the
# how-to's subject is the person it starts with: "how do i console a friend whos just lost their
# dad" is a how-to about the friend and their grief, and the "their dad" further along is the
# person they lost, not the person to answer about.
_A_PERSON_NAMED = re.compile(
    r"\b(?:(?:my|our|his|her|their)\s+(?:teenager|teen|son|daughter|child|kid|boy|girl|mum|mom|"
    r"mother|dad|father|partner|husband|wife|boyfriend|girlfriend|flatmate|housemate|roommate|"
    r"friend|boss|manager|colleague|brother|sister|gran|granny|grandma|grandad|grandpa|baby|"
    r"toddler|nephew|niece|aunt|uncle|cousin)|"
    r"(?:a|an|the|this|that|one)\s+(?:friend|mate|neighbour|neighbor|colleague|coworker|"
    r"co-worker|classmate|loved\s+one|relative|family\s+member))\b", re.I)


# Whether a reply is about somebody other than the person being spoken to.
_ABOUT_SOMEONE_ELSE = re.compile(
    r"\b(?:they|them|their|theirs|themselves|he|she|him|his|hers)\b", re.I)


def _the_name_they_gave(candidates, text, memory):
    """The reply that takes up the name the bot has just asked for, or None.

    "we got a puppy on saturday" is answered "What's its name?", and the next line - "hes called
    biscuit", or just "biscuit" - is the answer to that question. The knowledge base reads the
    name as a subject instead: biscuit is a food, so the puppy got the biscuit recipe, which is
    the one reply nobody asked for. A line that only gives the name goes to the highest reply
    that says the name back, because that reply is the one that has taken the answer up.
    """
    if _naming is None:
        return None
    name = _naming.the_name_given(text, memory)
    if not name:
        return None
    said = name.lower()
    for index, candidate in enumerate(candidates):
        if _priority(candidate) < 0:
            continue
        if said in str(candidate.get("reply") or "").lower():
            return index
    return None


def _a_knowledge_entry_has_it(candidates):
    """Whether the knowledge base proposed an answer to this line.

    The composer stands down for "how do I tell a child" only when something does have the
    words. The reading is a rough match on words, and a line it reads which no entry answers
    would otherwise lose its condolence to a nod: "my son died and i have to tell my daughter"
    is a bereaved parent, and the child who has to be told is the next turn, not this one.
    """
    for candidate in candidates:
        if int(candidate.get("priority") or 0) >= 0 and candidate.get("module") == "answers":
            return True
    return False


def _hurting_reply(candidates, pool, clean):
    """The index of the composer's reply to a wish to hurt somebody, or None.

    "i want to smack my son" reached the answer written for a child who is being hit, and came
    back "Being hit needs dealing with every time ... say the rule in one sentence" - a parent
    being told how to handle somebody else's violence while saying they want to smack their own
    child. The reading and the wording both live in bot/compose/harm.py, so this is only the
    routing decision: when the composer has a line for this, it gets the turn.
    """
    if _harm is None or not clean:
        return None
    try:
        if not _harm.reads_as_hurting_someone(clean):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    for index in list(pool) + list(range(len(candidates))):
        try:
            if _harm.reads_as_our_reply(candidates[index].get("reply")):
                return index
        except Exception:  # noqa: BLE001 - a reply we cannot read answers nothing
            continue
    return None


def _a_story_opened(memory):
    """Whether the last turn or two said a death or a leaving, rather than news about somebody living.

    The listening line is for the line after a story has begun - "my nan died last week" / "he
    took the car", "my wife left me" / "she packed her things last night" - because there is
    nothing to answer and the person is telling it. After news about somebody who is still here
    ("my mum has cancer", "my son is in hospital") the next line asks about that: "she keeps
    falling" wants the falls card, and a listening line takes it away.
    """
    if _loss is None:
        return True  # no reading, no narrowing: the rule stays as it was
    for turn in (memory.get("turns") or [])[-2:]:
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("user") or "").strip().lower()
        if not said:
            continue
        if _dream is not None and _dream.named(said) and not _dream.a_death_came_first(said):
            # A dream is not a story of a death that happened, so the listening line it lifted is
            # wrong on the turn after it: "i dreamt my dad died" / "hes fine its just a dream" was
            # met with "I'm listening - say more if it helps" instead of the dream's own answer.
            # A death said before the dream ("my dad died and i dreamt about him") still counts.
            continue
        if _loss.reads_as_loss(said):
            return True
        try:
            if badnews.reads_as_the_leaving(said) or badnews.reads_as_a_leaving_already_gone(said):
                return True
        except Exception:  # noqa: BLE001 - a reading that fails just adds no widening
            continue
    return False


# A line that says somebody will not do something: "she wont eat", "she wont talk about it".
# After news about somebody living this is their state of mind rather than an event to act on, so
# it keeps the listening line - the feeding card ("one new food next to one they already eat") is
# advice for a fussy toddler, and a wife with cancer who will not eat is not that.
REFUSAL = re.compile(r"\b(?:won'?t|wont|wouldn'?t|refus\w*|isn'?t eating|not eating|"
                     r"doesn'?t want|does not want|gives? up|gave up|stops? eating)\b")


def _a_refusal(text):
    """Whether the line is somebody refusing something, rather than something happening to them."""
    return bool(REFUSAL.search(str(text or "").lower().replace("\u2019", "'")))


def _is_loss_reply_in(candidates, pool, pools):
    """The index of the candidate whose reply is one of these pools' lines, else None."""
    for index in list(pool) + list(range(len(candidates))):
        text = str(candidates[index].get("reply") or "").strip()
        if text and any(text in wanted for wanted in pools):
            return index
    return None


def _composer_reading(clean, memory):
    """What the composer says this line is: (kind, target), or ("", ()) for an ordinary line.

    The routing lane's one door to bot/compose/: a line still inside a safety thread is the one
    kind of line the rest of the app must not answer as small talk, and the composer owns both
    the judgement and the wording. The arbiter only decides when a module keeps the turn
    instead. Adding a second kind is one branch in the composer and one here, never a second
    scanning loop.
    """
    try:
        from ..compose import fallback as composer
        kind, target = composer.reading(clean, memory)
    except Exception:  # noqa: BLE001 - a composer that cannot answer changes no reply
        return "", ()
    return (kind, target) if kind else ("", ())


def _carries_the_answer(reply, memory):
    """True when a reply comes back to the answer the bot gave a turn ago, else False.

    The reading is the composer's (bot/compose/verdict.py): the step a follow-up asks for is in
    that answer, so a line that carries a run of its words is answering the same question, and
    one that shares nothing with it is a different fact about the same topic.
    """
    if not reply:
        return False
    try:
        from ..compose import verdict as composer
        return bool(composer.carries_the_answer(reply, memory))
    except Exception:  # noqa: BLE001 - a composer that cannot answer holds nothing back
        return False


def _a_check_on_the_answer(reply):
    """True when a reply is the composer's answer to a check on the answer above, else False.

    The reading is the composer's (bot/compose/verdict.py): "will that work", "would that be worth
    it" and "is that the right thing to do" are the same check on the method just given, and the
    composer's line for it is that method's own reading.
    """
    if not reply:
        return False
    try:
        from ..compose import verdict as composer
        return bool(composer.a_check_on_the_reply(reply))
    except Exception:  # noqa: BLE001 - a composer that cannot answer holds nothing back
        return False


def _opens_on_a_job(reply):
    """True when a reply opens on an instruction, so it is already the next step, else False."""
    if not reply:
        return False
    try:
        from ..compose import verdict as composer
        return bool(composer.opens_on_a_job(reply))
    except Exception:  # noqa: BLE001 - a composer that cannot answer holds nothing back
        return False


def _is_a_generic_step(reply):
    """True when a reply is one of the composer's own generic first-step lines, else False.

    The pool is the composer's (bot/compose/__init__.py, `STEP_WHEN_LOW`), read here rather than
    restated: the step lines say the same few things to everybody, which is what makes them a
    fallback, and an entry that answers the subject with something concrete is not a fallback.
    A composer without the pool declares nothing, and then nothing is read as one.
    """
    if not reply or not _STEP_WHEN_LOW:
        return False
    return reply.strip() in _STEP_WHEN_LOW


# The label the reader gives a line that carries no subject of its own ("how are you" is
# "small-talk", not a topic). A module that declares it is not answering a question asked, so
# it is not a reason to take a live emergency thread away from the composer: what the person
# is doing mid-emergency is checking the bot is still there, and chat's "Doing well, thanks"
# was the answer. Content labels (health, cooking) still keep their turn, as before.
CHITCHAT = frozenset(("small talk",))


def _answers_this_line(reply):
    """True when a line from below the floor tells the person something to do, else False.

    Asked only where every real candidate is a slice of the last answer, so the choice is between
    the paragraph again and a line the composer wrote. A line that opens on a job ("Fix it if it is
    a part and a few pounds; bin it if the repair is half the price of new") answers the turn - it
    says what to do about the thing the person asked about - and it takes the turn. A nod is not:
    "Got it - it goes off in two days" and "I'm not sure about that one, sorry" would fit any
    message, and the answer's slice again is better than either. The reading is the composer's
    (`bot/compose/verdict.py: opens_on_a_job`), so the arbiter keeps no vocabulary of its own.
    """
    if not reply or fallback.is_said_it_already(reply):
        return False
    return _opens_on_a_job(reply)


def _content(reply):
    """A reply reduced to what it says, for the never-repeat rule."""
    return " ".join(WORD.findall(str(reply or "").lower()))
