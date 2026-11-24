"""Part 7 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re

from .. import memory as mem
from ..compose import fit as shapes
from ..knowledge import cooking, dishes, entries as all_entries
from ..knowledge.lookup import about_the_topic, find, names_its_own_subject
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import repeat
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import a_year_of_birth
from ..memory import repeat
from ..memory import keywords
from ..memory.again import AGAIN_HELP
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory import repeat
from ..memory import topics as said_topic
from ..memory.topics import already_said, pairing, stem
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import repeat
from ..memory import keywords
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory import repeat
from ..memory.narrow import flat, narrow
from ..understanding import understand
from .answers_part_01 import (
    AGAIN, _in_short, _said_before, WORD, _answer_said, _flat,
)
from .answers_part_02 import (
    CHOOSING, CHOOSING_PRONOUN, MODAL, MODALS, PREPOSITION_OF, TIME_WORD, _a_clause, _a_trip,
    _bare_subject, _the_month, _head_thing, _key_words,
)
from .answers_part_03 import (
    _is_about,
)
from .answers_part_05 import (
    _asked_again, _figure_missing, _payload, _a_definition_of_the_entry, _a_why_line_that_names,
    _agrees_with_its_own_field, _names_its_own_thing, _names_the_entry, _says_the_ask_whole,
    _the_field_on_the_screen, _reply_of,
)
from .answers_part_06 import (
    COOK_VERB, DEGREES, _repeat_short,
)


def _choosing(text, memory):
    """The entry a bare choosing question is about, with the reading and the reply.

    "what should i see" after "i'm going to rome in july" is "what should i see in rome", which
    the entries answer. Only tried when the line on its own found nothing, and the entry has to be
    keyed by the thing itself, so nothing is answered about a neighbour. The reading comes back
    with it because the entry builds its answer from that reading: the city guide needs the city.
    """
    match = CHOOSING.search(text.strip())
    if not match:
        return None
    subject = _bare_subject(mem.subject(memory) or "")
    if not subject:
        return None
    if TIME_WORD.match(subject.strip()):
        return None  # a month or a weekend is not a thing to choose for
    a_clause = _a_clause(subject)
    prep = PREPOSITION_OF[match.group("verb").lower()]
    shapes = [prep + " {s}"]
    if prep == "to":
        shapes.append("to a {s}")
    recent_user = mem.last_user(memory, 3)
    recent_user = " ".join(recent_user) if isinstance(recent_user, list) else str(recent_user or "")
    month = _the_month(text) or _the_month(mem.topic_text(memory) or "") or _the_month(recent_user)
    if month and _a_trip(memory):
        # "what should we pack" about a trip in may is "what should we pack for lisbon in may":
        # the season is part of the question, and the entries answer by season.
        shapes = [shape + " in " + month for shape in shapes] + shapes
    stem = CHOOSING_PRONOUN.sub("", text.strip()).rstrip("?").strip()
    declined = set()
    said = None
    for modal in MODALS:
        asked = MODAL.sub(modal, stem)
        for fuller in (asked + " " + shape.format(s=subject) for shape in shapes):
            reading = understand(fuller, memory)
            item = find(reading)
            if item is None or item.id in declined:
                continue
            if not (_is_about(item, subject) or (month and _a_trip(memory) and _is_about(item, month))):
                continue  # the entry has to be about the thing we put in the line
            # A fact from a field the talk never touched is not this conversation's fact - but
            # only when the words that reached it are the borrowed subject's. A thing borrowed
            # into the ask ("wear to marquee", "get for nan") makes a line the ask itself words,
            # and the entry that answers it is the right one even when the talk is about
            # something else: a nan's birthday must still reach the gifts entry. A clause cannot
            # be borrowed that way, and there the veto stands.
            if a_clause and not about_the_topic(item, reading):
                continue
            reply = _payload(item, memory, reading)
            if not reply.strip():
                declined.add(item.id)  # nothing to say about it
                continue
            if _said_before(reply, memory):
                # The entry was answered earlier in this chat, so the same paragraph would come
                # round word for word: give the part of it this ask names ("what should i see"
                # after a city guide wants the places, not the weather). That is the answer the
                # ask is for even though the whole of it has been said.
                part = narrow(reply, text)
                if (isinstance(part, str) and part.strip() and flat(part) != flat(reply)
                        and not _said_before(part, memory)):
                    return reading, item, part
                if said is None:
                    said = (reading, item, reply)
                continue
            return reading, item, reply
    if said is not None and _asked_again(text, said[2], memory):
        # Nothing fresh and nothing narrower, and this is the same question again: say that is
        # what was said before rather than leave the person with a shrug. "what should i see"
        # after the city guide read "I'd rather not guess" while the sights had been named a turn
        # earlier; a friend says "same as I said: ..." and stops.
        #
        # A different ask ("my washing machine is leaking", then "what do I do?") is not that:
        # the follow-up module says "stop the cycle first, then work down the list I gave you",
        # which is better than handing back the paragraph, so it is left to answer.
        reading, item, reply = said
        if _asks_only_the_length(text):
            # The paragraph is all there is for "how long will that take", and reading it out
            # behind "Same as before" answers nothing: say the answer holds no time and give its
            # first step. The arbiter rightly prefers a search to the paragraph again, so this is
            # the line that has to be here for the person to get an answer at all.
            honest = _figure_missing(reply, text)
            if honest:
                return reading, item, honest
        return reading, item, AGAIN[0].format(reply=_in_short(reply))
    return None


def _about_the_talk(item, text, memory, reading):
    """False when the entry is from a part of the knowledge base this talk never touched.

    A follow-up names no thing of its own, so its bare words can look like a thing they are not:
    "we got a puppy" and then "how long until he is house trained" reached the first-home entry
    off "house" and answered with a deposit plan the puppy conversation had nothing to do with.
    The entry has to be about the thing the conversation is on, or about a topic the line itself
    names; when it is neither, this module steps aside and the one with the real answer gets it.

    A line that says it is changing the subject is not a follow-up at all: "ok changing the
    subject, im planning a curry tonight" after a dripping tap is about the curry, and reading
    its words against the tap threw away the recipe that answers it. The person has told us the
    old thing is done with, so nothing below treats them as still leaning on it.
    """
    read = (memory or {}).get("understood") if isinstance(memory, dict) else None
    if isinstance(read, dict) and read.get("change_of_subject"):
        return True
    subject = mem.subject(memory)
    record = mem.current(memory)
    if not isinstance(record, dict) or record.get("turn") == len(memory.get("turns") or []):
        # The record the subject would be read from is the line being answered, so there is no
        # other subject this talk is on yet: the first line of a conversation, or one that
        # started a new one, is the whole of it so far. Read back as a thing the answer has to
        # be about, that line's own noun throws away every answer that speaks to the situation
        # without saying the noun again - "how do i deal with a friend who always cancels" is
        # about the friend, the advice is about the pattern, and the person got the search hedge
        # instead of "Say it once, about the pattern rather than the last time". It is the same
        # mistake the store itself avoids in `bot/memory/topics.py::is_follow_up`, which does
        # not read a record written for this very line as the thing before it.
        return True
    thing = _head_thing(subject)
    if not thing:
        return True  # nothing the talk is on: the bare words are all the line has
    if _is_about(item, thing):
        return True
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not turns:
        # The first line of a talk is not a follow-up: it contradicts nothing, because there is no
        # earlier turn to contradict. Whatever the head of that line reads as, the subject the
        # memory holds is the line's own words, so an entry about them is the answer it has and
        # there is nothing this talk has "never touched" yet. Read as a follow-up the line loses
        # it: the head reading takes the verb ("what should i eat before a football match" is
        # about "eat"), and "should i take vitamin d in winter" reads as "take", so the person got
        # a hedge for two things the knowledge base answers well. A later line keeps the whole
        # guard: "we got a puppy" / "how long until he is house trained" steps aside for "house".
        return True
    if _names_the_entry(text, item):
        return True  # the line names the thing the entry is about, in so many words
    if _a_definition_of_the_entry(text, item):
        return True  # the line asks what the thing the entry is about means
    if _names_the_thing_apart_from_the_talk(item, text, subject, reading):
        return True  # the line names the entry's own subject and none of the talk's
    # A why-line says what it is about, so the entry that knows that thing is its
    # answer whatever this talk is on: the domain test above is for a follow-up that
    # names nothing of its own, and applied to a why-line it stood the allergy answer
    # down after a chat about cats.
    if _a_why_line_that_names(item, reading):
        return True
    if _the_field_on_the_screen(item, text, reading, memory):
        return True
    if _says_the_ask_whole(text, item):
        # A hand-over names nothing but the ask itself: "quiz me", "test me", "hit me with a
        # question". There is no subject in it to read against the thing this talk is on, so the
        # guard above threw the quiz away a turn after a chat about somebody's son ("my son loves
        # quizzes" / "quiz me" got "Thanks for telling me - I'm here if you want to dig into any
        # of that"). A whole line that is one of the entry's own key phrases, two words or more,
        # is about that entry whatever else the conversation holds - and a single key word is not
        # enough (`_names_the_entry`'s determiner test is what keeps a puppy chat's "house
        # trained" off the first-home entry).
        return True
    if _names_its_own_thing(text, memory) and _agrees_with_its_own_field(item, reading):
        # The line names a thing of its own, so it is judged by its own field and not by the field
        # of the answer before it: "my boiler is making a clunking noise" and then "is it worth
        # getting a smart meter" was turned down as a boiler talk, and the boiler's meter row took
        # the turn. The line still has to agree with its own field, so "should i tip a hotel
        # cleaner" is not handed the money table.
        return True
    return about_the_topic(item, reading)


def _names_the_thing_apart_from_the_talk(item, text, subject, reading):
    """True when the line ends on this entry's own subject and says nothing of the talk's.

    A subject the store carries forward is only evidence about the line when the line still
    speaks to it. "i went to the shop today" and then "how do i build endurance" is a new
    question with its own word in it ("endurance", the fitness row's own subject), and the shop
    has no part in it; read against the shop's topic the row stood down and the person got a
    hedge. The word the line ends on is the test, so a loose row still stands down: "how do i
    bake brownies" ends on the brownies, not on "bake", and the row that answers how to start
    baking does not take the turn from the brownie recipe. So does the loud case: "my kids wont
    listen to me" and then "what can i do" names nothing of the music row's at all.
    """
    if not isinstance(reading, dict) or reading.get("kind") != "question":
        return False  # a statement that names a thing loosely is a follow-up about a feeling
    if not names_its_own_subject(item, reading):
        return False
    said = said_topic.words(text)
    if not said:
        return False
    if not _is_about(item, said[-1]):
        return False
    if PRONOUN_OBJECTS.intersection(WORD.findall(str(text or "").lower())):
        return False  # a pronoun is the line pointing back at the talk
    thing = _head_thing(subject)
    if not thing:
        return False
    words = {word.rstrip("s") or word for word in WORD.findall(str(text or "").lower())}
    return (thing.rstrip("s") or thing) not in words


def _the_plan_for(text, memory, understood):
    """The dish plan's answer to a part question the last answer did not state, or None.

    "what temperature should the oven be?" after a cake's baking time names no subject: the
    time answer has no heat in it, and no other entry is about the cake. The dish the
    conversation is on says the heat itself, so the plan answers for it.
    """
    if not _the_plan_answers_this(memory):
        return None
    answer = dishes.follow_up(memory, understood)
    if isinstance(answer, str) and answer.strip():
        return answer
    return None


# Heating up leftovers is the third clock: not the pan's time, not the fridge life, and the
# keeping answer has no reheat time in it. "how long do i reheat it for" after a keeping answer
# was handed the storage figure ("2 days."), which is the one number that must not be used.
PRONOUN_OBJECTS = frozenset(("it", "them", "that", "this", "one", "these", "those", "him",
                             "her", "his", "hers", "the rest", "some"))


REHEAT_ASK = re.compile(r"\b(?:re-?heat|re-?heating|heat (?:it|them|that|this) up|heat up|"
                        r"warm (?:it|them|that|this) up|warm up|microwave)\b", re.I)


# What is true of every leftover, and the only thing that is: the test is piping hot right
# through, not a number of minutes, because the time is the portion's size and the shape of the
# food. Said as a range so it is useful, and with the once-only rule because that part is food
# safety rather than preference.
REHEAT_REPLY = ("No fixed time: reheat it until it is piping hot right through, not just warm. "
                "A portion takes 2 to 4 minutes in the microwave with a splash of water, "
                "stirring halfway; a whole joint or a big tub needs 15 to 25 minutes covered in "
                "the oven at 180C. Piping hot means steaming all the way through, and reheat it "
                "once only.")


def _names_another_food(understood, subject):
    """True when the line names a thing of its own that is not the food we are on.

    The pronoun line ("how long do i reheat it for") names nothing, and the food named again
    ("how long do i cook pasta for") names the same thing the keeping answer did - both are
    follow-ups about this food. "how long do i reheat a pizza" is not: pizza is a new question,
    and the entry that knows pizza is where it belongs.
    """
    if not subject:
        return False
    words = set(subject.split())
    for ent in understood.get("entities") or []:
        if not isinstance(ent, dict) or str(ent.get("type") or "") == "person":
            continue
        text = str(ent.get("text") or "").lower().strip()
        if not text:
            continue
        # The understanding names the action as a thing: "how long do i reheat it for" comes
        # back with "reheat" among its entities, and reading that as a second food stood this
        # guard down on the one line it exists for, leaving the keeping figure ("2 days.") as
        # the answer. An action is not a food of its own, and neither is a pronoun.
        if text in PRONOUN_OBJECTS or COOK_VERB.search(text):
            continue
        if words & set(text.split()):
            return False
        return True
    return False


# The subject the store keeps after a keeping question carries the ask's own verb ("cooked rice
# keep", "cooked chicken keep"), which is not part of the food. Written into the follow-up it made
# "how long does the cooked rice keep take to cook", which reaches nothing, so the keeping figure
# stayed as the answer to a question about the pan. The food is what is left without it.
KEEPING_WORD = re.compile(r"^(?:keep|keeps|keeping|kept|last|lasts|lasting|store|stored|"
                          r"storage|freeze|freezes|frozen|fridge|freezer|long)$", re.I)


def _the_food_named(subject):
    """The subject without the keeping words in it: "cooked rice keep" -> "cooked rice"."""
    return " ".join(word for word in str(subject or "").split()
                    if not KEEPING_WORD.match(word))


def _the_plan_answers_this(memory):
    """True when the last answer was about cooking the dish, so its plan is the answer here.

    "how long?" after "what temperature for a cake" wants the plan's time. "how long?" after
    "how long does chicken last in the fridge" does not: that conversation is about keeping
    food, and the plan would say how long to roast it - a wrong answer, and worse than the
    search hedge it replaced. The plan is about one oven at one heat, so it only answers while
    the answer we are on was about that oven: a fridge-life answer has no heat in it, and an
    air fryer answer has a different one.
    """
    said = str(mem.last_bot(memory) or "")
    if "air fryer" in said.lower() or "airfryer" in said.lower():
        return False
    return bool(DEGREES.search(said) or mem.has_time(said))


def _the_plan_said_again(understood, text, memory):
    """The same property asked again about the plan we just gave, said as a repeat.

    A bare ask ("what temperature?" after "what temperature for a cake") repeats the answer it is
    about without repeating the line, so it is counted by the sentence we gave and not by the
    line that asked for it. The answer comes whole, with the lead-in a repeated answer gets, and
    this runs before the guard that sends a figure we do not have to a search: the plan is not
    another entry guessing, it is the answer we already gave."""
    if not (mem.asks_only(understood) and mem.last_module(memory) == "answers"):
        return None
    if not _the_plan_answers_this(memory):
        return None
    plan = dishes.follow_up(memory, understood)
    if not isinstance(plan, str) or not plan.strip():
        return None
    said = 0 if pairing(text) else _answer_said(plan, memory)
    if said >= 3:
        return AGAIN_HELP.format(reply=plan)
    if said:
        # The same ask again gets the sentence of the plan that answers it, not the whole plan
        # twice: "can i make the frosting the day before" is answered by the plan's sentence
        # about the day, and the keeps-sentence in front of it is the same paragraph again.
        return AGAIN[said - 1].format(reply=_repeat_short(plan, text, memory))
    return None


# While an emergency is open, a bare statement is the person filling in what happened, and the
# nouns in it are not the subject of the turn: after "i can't breathe properly", "it started this
# morning when i was in the garden" is when it began, not a garden to plan, and it was answered
# with "take one bed, not the garden: strim or mow the lot". A question is still a question
# ("should i use my inhaler"), and the guard lapses with the case, so it only covers the turn
# right after the safety reply.
def _filling_in_an_emergency(understood, memory):
    """True when the line only adds detail to a safety reply the bot has just given."""
    if not isinstance(memory, dict):
        return False
    said = [turn for turn in mem.recent(memory, 1) if isinstance(turn, dict)]
    if not said or said[-1].get("module") != "safety":
        return False
    if not isinstance(understood, dict):
        return True
    # "when i was in the garden" is read as an ask for a time, so the asks are no sign of a
    # question: what the person said, not what the line contains, is what the guard goes on.
    signals = understood.get("signals") or {}
    return not (understood.get("kind") == "question" or signals.get("question_mark"))


def _usable(item, reading, memory):
    """False when the answer needs something the line says the kitchen has not got."""
    # An answer about the appliance itself is not a cooking instruction: "my oven wont heat up"
    # says the oven is not working, and the element diagnosis is the answer to it, not a recipe
    # that needs an oven. Only a dish is held out by what the kitchen has not got.
    if getattr(item, "fault", False):
        return True
    return not cooking.unusable(_reply_of(item, reading, memory), reading)


def _next_usable(item, reading, memory):
    """The best entry that answers the same line without what the line has not got."""
    kept = [one for one in all_entries() if one is not item and _usable(one, reading, memory)]
    return find(reading, entries=kept) if kept else None


def _without_names(reading):
    """The same reading with a place word the line uses as a name taken out.

    "my mate paris is visiting for the weekend" is a friend coming over, and "my nan is called
    florence" is a name: the city guide and the city weather are answers to a different question.
    The understanding engine says which words those are, so every domain gets the same answer.
    """
    names = [name for name in (reading.get("person_names") or ()) if isinstance(name, str)]
    if not names:
        return reading
    drop = set(names)
    narrowed = dict(reading)
    words = reading.get("words")
    if isinstance(words, list):
        narrowed["words"] = [word for word in words
                             if not (isinstance(word, str) and word.lower() in drop)]
    clean = reading.get("clean")
    if isinstance(clean, str) and clean:
        narrowed["clean"] = " ".join(word for word in clean.split()
                                     if word.lower().strip(".,!?;:") not in drop)
    return narrowed


# A line that hands over text and asks for a tone wants that text rewritten: "make this sound
# less angry: i want my deposit back now" is a writing job, not a question about deposits, and
# the entry that answers deposits used to claim it and answer the wrong thing - the tenancy
# rules instead of a softer sentence. So these lines are recognised first, the rewrite is built
# from the text itself (so it works on anything someone pastes in), and no entry gets the turn.
REWORD_ASKS = (
    "make this sound", "make that sound", "make it sound", "make mine sound",
    "make this a bit", "make this more", "make this less", "make that more", "make that less",
    "make it more", "make it less", "can you make this", "could you make this",
    "can you make it", "could you make it", "rewrite this", "rewrite that", "rewrite it",
    "can you rewrite", "could you rewrite", "reword this", "reword that", "reword it",
    "can you reword", "rephrase this", "rephrase that", "can you rephrase",
    "how do i word this", "how would you word", "how should i word", "how do i phrase this",
    "word this better", "say this more", "say it more", "say that more", "say this less",
    "say it less", "put this more", "put it more", "so it sounds", "so it doesnt sound",
    "so it doesn't sound", "so it sounds", "so that it sounds", "make this shorter",
    "make it shorter", "shorter please", "cut this down", "make this briefer",
    "make it a bit", "make this a little", "make it a little", "make this sound a bit",
    # A message pasted in to be checked is the same job as a rewrite: "can you check this sounds
    # all right: Hi Sarah, ..." used to be shrugged at, and then the follow-ups about it had
    # nothing to work on either.
    "check this sounds", "check that sounds", "check how this sounds", "check this reads",
    "does this sound", "does this read", "check this email", "check this message",
    "check this text", "check this note", "check this letter", "look over this",
    "check over this", "read this over", "read it over", "does this come across",
)


# A line that hands text over to be checked rather than told to change its tone. The answer says
# what is right about the sentence instead of pretending it was an angry one.
CHECK_ASKS = (
    "check this", "check that", "check how this", "does this sound", "does this read",
    "look over this", "check over this", "read this over", "read it over",
    "does this come across", "sounds all right", "sounds alright", "sound all right",
)


# The tone the line asks for, as the words a person uses for it.
TONE_WORDS = {
    "warm": ("friendl", "nice", "nicer", "warm", "polite", "politer", "kind", "gentler",
             "gentle", "softer", "soft", "tactful", "diplomatic", "angry", "harsh", "rude",
             "aggressive", "blunt", "cross", "snappy"),
    "formal": ("formal", "professional", "businesslike", "official"),
    "casual": ("casual", "informal", "less stiff"),
    "short": ("short", "shorter", "brief", "concise", "punchy"),
}


# The words a follow-up tones the sentence with, and the joining words between them, are not the
# sentence: "make it shorter and less angry" and "can you make it a bit warmer and less jokey"
# hand over nothing, and quoting "and less jokey" back at the person is nonsense. Flattened
# stems, because TONE_WORDS holds them ("friendl", "politer").
TONING_WORDS = frozenset(word for words in TONE_WORDS.values() for word in words)


JOINING_WORDS = frozenset("""
and but or also plus then so just please bit little really very quite rather still too as well
less more much slightly now thanks thank you for me mate ok okay
to be sound sounds read reads look looks come comes across
""".split())


# How the message sounds, as a person names it, when the word is not one the rewriter acts on:
# "less jokey" is a tone whether or not there is a rule for making a joke quieter.
TONE_DESCRIPTORS = frozenset("""
joke jokes jokey jokingly jokier funny funnier fun silly serious light lighter cheery cheerful
breezier breezy flowery salesy pushy needy desperate posh chatty direct firm sweary swearing
angry cross snappy blunt harsh rude
""".split())


def _only_the_tone(rest):
    """True when what follows the instruction is the tone again, not text to rewrite."""
    words = [word.strip(".,!?;:'\"") for word in str(rest or "").lower().split()]
    words = [word for word in words if word and word not in JOINING_WORDS]
    if not words:
        return True
    for word in words:
        if word in TONE_DESCRIPTORS or CONTINUED.search(word):
            continue
        if any(stem in word for stem in TONING_WORDS):
            continue
        return False
    return True


# The wording that makes a demand, and the wording that asks. Only these swap, because a rewrite
# that changes the meaning of what someone wants to say is worse than no rewrite at all.
DEMANDS = (
    (re.compile(r"\bi want\b", re.I), "I'd like"),
    (re.compile(r"\bi need you to\b", re.I), "Could you"),
    (re.compile(r"\bi demand\b", re.I), "I'd ask for"),
    (re.compile(r"\bgive me\b", re.I), "could I have"),
    (re.compile(r"\byou need to\b", re.I), "could you"),
    (re.compile(r"\byou must\b", re.I), "would you be able to"),
    (re.compile(r"\byou never\b", re.I), "it sometimes feels like you don't"),
    (re.compile(r"\byou always\b", re.I), "it sometimes feels like you always"),
    (re.compile(r"\bi'm sick of\b", re.I), "I'm fed up with"),
    (re.compile(r"\bi am sick of\b", re.I), "I'm fed up with"),
    (re.compile(r"\bi'm fed up of\b", re.I), "I'm fed up with"),
    (re.compile(r"\bsort it out\b", re.I), "look into it"),
    (re.compile(r"\bright now\b", re.I), ""),
    (re.compile(r"\bimmediately\b", re.I), "as soon as you can"),
)


def _reword_ask(text):
    """The text the line wants rewritten, or None when the line is not a rewrite request.

    An empty string means the line asks for a rewrite but hands over nothing to rewrite.
    """
    flat = _flat(text)
    lowered = " ".join(str(text or "").lower().split())
    asked = any(phrase in flat for phrase in REWORD_ASKS)
    tone = any(word in flat for group in TONE_WORDS.values() for word in group)
    if not (asked and (tone or ":" in lowered)):
        return None
    head, sep, tail = lowered.rpartition(":")
    if sep and len(tail.split()) >= 2 and any(phrase in _flat(head) for phrase in REWORD_ASKS):
        return tail.strip(" .\"'")
    # The instruction is what comes before the text: take the earliest one, so "rewrite this
    # email so it sounds professional" hands over the email, not the word "professional".
    at, found = len(flat) + 1, ""
    for phrase in REWORD_ASKS:
        where = flat.find(phrase)
        if where >= 0 and (where < at or (where == at and len(phrase) > len(found))):
            at, found = where, phrase
    rest = flat[at + len(found):] if found else flat
    # "so it sounds professional" and "so it doesn't sound rude" are the tone again, said after
    # the text rather than before it.
    rest = re.sub(r"\bso (it|that) (sounds?|reads?) (more |less )?.*$", "", rest)
    rest = re.sub(r"\bso (it|that) does ?n[o']?t sound .*$", "", rest)
    # What follows the instruction is the tone, not the text: "make this sound less angry please
    # i need to tell my boss i quit" hands over the sentence after the tone words.
    rest = re.sub(r"^\s*(a bit |abit |a little |alittle )?(sound|sounds|read|look)?\s*"
                  r"(less|more|softer|warmer|friendlier|nicer|politer|politelier|formal|"
                  r"professional|casual|shorter|briefer|blunt|harsh|rude|angry|aggressive|"
                  r"gentle|tactful|diplomatic|kind)\b\s*(angry|harsh|blunt|rude|aggressive|"
                  r"formal|polite)?",
                  "", rest)
    for _ in range(3):
        rest = re.sub(r"^\s*(a bit|a little|please|thanks|thank you|for me|mate)\b[ ,]*",
                      "", rest)
    rest = rest.strip(" .,:;\"'")
    if len(rest.split()) < 3 or _only_the_tone(rest):
        return ""
    return rest


def _tone_of(text):
    flat = _flat(text)
    tones = set()
    for tone, words in TONE_WORDS.items():
        if any(word in flat for word in words):
            tones.add(tone)
    if "less formal" in flat:
        tones.add("casual")
    if any(phrase in flat for phrase in CHECK_ASKS) and not tones:
        tones.add("check")
    return tones


def _softened(sentence, tones):
    """The sentence with its demands asked instead, no shout in it, and the tone asked for."""
    out = sentence.strip()
    for pattern, better in DEMANDS:
        out = pattern.sub(better, out)
    out = out.replace("!", ".")
    # "now" is what makes a request read as a demand; "as soon as you can" keeps the urgency.
    out = re.sub(r"\bnow\b(?=\s*(?:[.,;!?]|$|or\b|and\b))", "", out)
    out = re.sub(r"\s+", " ", out).strip(" ,;")
    out = re.sub(r"\bi\b", "I", out)
    # A typist who leaves the apostrophe out still wants the apostrophe in the sentence they send.
    for bare, proper in (("cant", "can't"), ("dont", "don't"), ("wont", "won't"),
                         ("doesnt", "doesn't"), ("didnt", "didn't"), ("couldnt", "couldn't"),
                         ("wouldnt", "wouldn't"), ("isnt", "isn't"), ("im", "I'm"),
                         ("ive", "I've"), ("ill", "I'll")):
        out = re.sub(r"\b%s\b" % bare, proper, out)
    if out and out[0].islower():
        out = out[0].upper() + out[1:]
    if "formal" in tones:
        for short, long in (("I'm", "I am"), ("I've", "I have"), ("I'd", "I would"),
                            ("I'll", "I will"), ("don't", "do not"), ("doesn't", "does not"),
                            ("can't", "cannot"), ("won't", "will not"), ("it's", "it is"),
                            ("couldn't", "could not"), ("wouldn't", "would not")):
            # the sentence may open on the contraction, so the swap has to survive a capital
            out = re.sub(re.escape(short), long, out)
            cap_short, cap_long = short[0].upper() + short[1:], long[0].upper() + long[1:]
            out = out.replace(cap_short, cap_long)
    if "casual" in tones:
        for long, short in (("I would", "I'd"), ("I am", "I'm"), ("do not", "don't"),
                            ("cannot", "can't"), ("will not", "won't")):
            out = out.replace(long, short)
    # Days and months are names, and a sentence someone is about to send should not have them
    # in lower case.
    for name in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
                 "January", "February", "March", "April", "May", "June", "July", "August",
                 "September", "October", "November", "December"):
        out = re.sub(r"\b%s\b" % name.lower(), name, out)
    # A person's name is a name too: "Hi sarah, just checking in" is how it was typed, and
    # nobody sends that. Only after a greeting, where a lower-case word is certainly a name.
    out = re.sub(r"\b(Hi|Hello|Dear|Hey|Thanks|Thank you|Morning|Afternoon)\s+([a-z])",
                 lambda m: m.group(1) + " " + m.group(2).upper(), out)
    if out and out[-1] not in ".?!":
        out += "."
    return out


# A rewrite is a conversation: "make this less angry: ..." then "shorter" then "and friendlier".
# The text is in the last line that handed one over, so a follow-up returns that same sentence
# with the tone it asks for now added rather than asking the person to paste it again.
CONTINUED = re.compile(r"\b(more|less|softer|friendlier|friendly|nicer|polite|politer|shorter|"
                       r"briefer|formal|casual|tone|warmer|pushy|rude|blunt|harsh|strong|needy|"
                       r"desperate|unprofessional)\b")


def _last_rewrite(memory):
    """The text and tones of the rewrite before this turn, or None.

    Only lines that handed text over count, so a follow-up after an ordinary answer is not read
    as one about a sentence that was never there.
    """
    turns = memory.get("turns") or []
    for turn in reversed(turns[-4:]):
        if not isinstance(turn, dict):
            continue
        said = turn.get("user")
        asked = _reword_ask(said) if isinstance(said, str) else None
        if asked:
            return asked, _tone_of(said)
    return None


# The sentences people hand over most often are the ones they find hardest to say, and a
# mechanical softening of "i need to tell my boss i quit" is no use to anyone: it needs the
# words, not the punctuation tidied. These are the meanings, keyed by what the line is about,
# so the reply says the thing in a way the person can actually send.
HARD_TO_SAY = (
    (re.compile(r"\b(quit|quits|resign|resigning|resigned|hand in my notice|leave my job)\b"),
     "I've decided to move on, and I'd like to agree a leaving date.",
     "Say it out loud first and keep to that one line: the date and a thank you are the parts "
     "they remember, and the reasons are for the exit interview."),
    (re.compile(r"\b(pay me|owe me|my money|the money back|refund|invoice)\b"),
     "I'd like to sort out what I'm owed, please.",
     "Put the amount and the date in the message, and say what you will do next if it is not "
     "settled, once, without heat."),
)


def _hard_to_say(asked):
    """A known hard sentence, said properly, or None."""
    flat = " ".join(asked.lower().split())
    for pattern, sentence, tail in HARD_TO_SAY:
        if pattern.search(flat):
            return sentence, tail
    return None


def _rewritten(asked, tones, from_followup=False):
    """The rewrite, phrased as the answer: the sentence, then what to leave in or out."""
    body = _softened(asked, tones)
    known = _hard_to_say(asked)
    # The canned words for the hardest sentences are for a request made in full ("make this
    # sound less angry: i need to tell my boss i quit"), not for "make it shorter" three turns
    # later: shortening a message about an invoice must not replace it with a sentence about a
    # resignation or a refund.
    if from_followup:
        known = None
    if known is not None and ("warm" in tones or "short" in tones):
        body, tail = known
        return 'Softer, same point: "%s" %s' % (body, tail)
    if tones == {"check"}:
        # Handed over to be checked, not told off: say what is right about it and what is missing.
        return 'Reads all right: "%s" Nothing needs fixing: it is short, it says what you want, and ' \
               'it leaves them an easy way to say yes. Add the date you need an answer by if there ' \
               'is one.' % body
    polite = any(t in tones for t in ("warm", "formal"))
    # "please" belongs on a request. A sentence that only tells someone something ("I need to
    # tell my boss I quit") is not rude for leaving it out, and "please" on it reads as a mistake.
    asking = bool(re.search(r"\b(want|need|give|send|pay|refund|back|fix|sort|complain|explain|"
                            r"ask|book|change|cancel|return|replace|stop|reply|respond|"
                            r"could|would|can)\b", body.lower()))
    if re.search(r"\bneed to (tell|say|let)\b", body.lower()):
        asking = False
    if polite and asking and "please" not in body.lower() and not body.endswith("?"):
        body = body[:-1] + ", please." if body.endswith(".") else body + "?"
    if "short" in tones:
        body = re.sub(r"\b(just|really|actually|basically|obviously|literally)\b ?", "", body)
        body = re.sub(r"\s+", " ", body).strip()
    tail = ("Ask for what you want and a date, and leave out the anger: a short, specific message "
            "gets answered more often than a hot one.")
    if not asking:
        tail = ("Say it plainly, name the date, and stop there: the calmer and shorter it is, the "
                "better it lands.")
    if "formal" in tones:
        tail = ("Formal but human works best: the request, the date, and one line of reason, with no "
                "apology for asking.")
    elif "casual" in tones:
        tail = ("Keep it short and say it as you would out loud; the subject still has to be clear.")
    elif "short" in tones:
        tail = ("Cut everything that is not the request: the ask and the date are the whole message.")
    return 'Softer, same point: "%s" %s' % (body, tail)


# A line about what *someone else* eats is the memory store's, not a dinner idea. "she doesnt
# eat meat" is a fact about the mum that wants saying back, and "what did i say she doesnt eat"
# asks what is already known; the vegetarian-dish entry answers both with cooking advice, and
# the person is left without knowing their line was taken in.
THEIR_EAT = re.compile(r"\b(?:eat|eats|eating|diet|diets|vegetarian|vegan|pescatarian|meat"
                       r"|gluten|dairy|halal|kosher)\b", re.I)


# Words that make the line a request for a meal rather than a fact about the person: "what can
# i cook for my mum" is a cooking question even though it names her diet.
COOK_WORD = re.compile(r"\b(?:cook|cooks|cooking|cooked|make|makes|making|recipe|recipes|meal"
                       r"|meals|dinner|lunch|tea|supper|dish|dishes|serve|serving|menu|feed"
                       r"|buy|shop"
                       # The oven verbs and the meals people name on their own. "my son cant
                       # have dairy, what can i bake" was a fact kept and said back ("Your son
                       # is dairy-free.") with the ask left unanswered, because "bake" was not
                       # in this list while "cook" and "make" were: the same line in those words
                       # got the swaps. A line that names what to bake is a request for food,
                       # exactly as one that names what to cook is.
                       r"|bake|bakes|baking|baked|roast|roasts|roasting|grill|grills|grilling"
                       r"|fry|fries|frying|breakfast|breakfasts|snack|snacks|pudding|puddings"
                       r"|dessert|desserts|cake|cakes|biscuit|biscuits|bread|packed lunch)\b",
                       re.I)


# A line that asks what was already said ("what did i say she doesnt eat").
SAID_WORD = re.compile(r"\b(?:say|said|saying|tell|told|ask|asked|mention|mentioned|remember"
                       r"|remind)\b", re.I)


# "can he eat cake", "can she eat pesto": the question is about the *food*, and the knowledge
# base has an answer for it (the allergy entry, the meat-free dishes). Read as a question about
# the guest it only gets the store's shrug - "You haven't told me what your son eats" - which is
# wrong when the line before said what he cannot have. A question whose object is the diet
# itself ("does she eat meat", "what does she eat") is still a question about the person.
EAT_VERB = re.compile(r"\b(?:eat|eats|eating|have|has|having|drink|drinks|drinking|try|trying"
                      r"|tuck)\b")


DIET_WORDS = frozenset("""
meat dairy gluten nut nuts egg eggs fish pork wheat soya soy lactose halal kosher vegetarian
vegan pescatarian cheese milk sugar carbs alcohol shellfish peanut peanuts seafood chicken beef
lamb bacon ham butter cream yoghurt yogurt bread pasta rice potato chips
""".split())


NOT_THE_THING = frozenset("""
a an the some any this that it my your his her their our at on in for with too as well again
today tonight now though really then there here and but or so
""".split())


def _asks_about_a_food(low):
    """Whether a question about someone puts a thing to eat after the verb ("can he eat cake")."""
    found = EAT_VERB.search(low)
    if not found:
        return False
    words = [word.strip(".,!?;:'\"") for word in low[found.end():].split()]
    words = [word for word in words if word and word not in NOT_THE_THING]
    if not words:
        return False
    return words[0] not in DIET_WORDS


def _someones_else_diet(text, memory, understood):
    """True when the line is about what someone other than the person eats.

    The memory store keeps a visitor's diet against the visitor and says it back with their name
    ("Your mum doesn't eat meat."); the knowledge base has one answer for meat-free eating and it
    is a request for dish ideas, so it reads both the fact and the question about it as a cooking
    question. A statement about them, or a question about what is already known, is theirs.
    """
    low = " ".join(str(text or "").lower().split())
    if not low or COOK_WORD.search(low):
        return False
    if not THEIR_EAT.search(low) or not isinstance(understood, dict):
        return False
    if not _names_someone_else(low):
        return False
    if not memory.get("others"):
        return False  # nobody else has been talked about: there is nothing to be right about
    if understood.get("kind") != "question" and _a_guest_restriction(text, memory, understood):
        # "my friend doesnt eat dairy" is a constraint on the dinner, and the kitchen has the
        # swaps for it: the store's "Your friend doesn't eat dairy." says the line back and
        # answers nothing. The swaps are the better reply, so the knowledge base keeps the line.
        # A question about them is still the store's: "is my mum vegetarian or what" is asking
        # what was said, and a dinner idea is no answer to it.
        return False
    if understood.get("kind") == "question":
        if SAID_WORD.search(low):
            return True
        if _asks_about_a_food(low):
            return False  # "can he eat cake" is the knowledge base's, allergy and all
        return not _about_them_alone(low)
    if MEAT_FREE.search(low):
        # A meat-free diet is always the kitchen's: over a dish being cooked it changes the dish,
        # and over a question that was not about cooking it gets the swap and the portion. The
        # store's "Your daughter doesn't eat meat." says the line back either way.
        return False
    return True


def _a_guest_restriction(text, memory, understood):
    """Whether the kitchen has a cooking answer for the diet this line names for someone else.

    One question, asked of the dish table: a diet the table has swaps for, or the meat-free
    dinner, is a constraint on what to cook rather than a fact to keep. A line the table does
    not answer is still the store's ("my mum ate dairy and was ill").
    """
    try:
        from bot.knowledge import dishes
    except Exception:
        return False
    return bool(dishes.has_a_diet_reply(memory, understood)
                or dishes.has_a_veggie_reply(memory, understood))


# The diets the dish tables have an answer for. A meat-free request has a dinner idea
# (dishes.VEGGIE_IDEA, dishes.VEGAN_IDEA); dairy, fish and the rest do not, so a line naming one
# of those over a dish keeps the store's echo, which is true, instead of being handed to whatever
# entry is about that food ("my husband doesnt eat dairy" used to be answered with the cheese
# calorie line, "she doesnt eat fish" with how to tell fish is done).
MEAT_FREE = re.compile(
    r"\b(?:vegetarian|vegetarians|veggie|veggies|vegan|vegans|meat\s?free|flexitarian)\b|"
    r"\b(?:doesn'?t|doesnt|don'?t|dont|won'?t|wont|can'?t|cant|never|refuses to|hates)\s+"
    r"(?:eat|eats|eating|touch|touches)\s+(?:any\s+)?meat\b|"
    r"\b(?:no|without|off)\s+meat\b", re.I)


def _names_someone_else(low):
    """Whether the line names or points at a person other than the speaker."""
    for relation in mem.facts.RELATIONS:
        if re.search(r"\b" + relation + r"\b", low):
            return True
    return bool(re.search(r"\b(?:he|she|they|him|her|them|his|their)\b", low))


# A thank-you line can still be a writing job: "thank you letter for a present" and "thank you
# card for a wedding present" name the thing to write straight after the thanks, and the note to
# send is what the person wants help with - "Happy to help." answers nothing. The thanks are the
# member of the pair that came first; what follows the "you" decides.
WRITE_OBJECT = frozenset("""
letter letters card cards note notes message messages text texts email emails wording words
verse poem speech toast
""".split())


def _a_writing_job(understood):
    """True when the line asks for the words by naming the thing to write itself."""
    norm = list((understood or {}).get("norm") or ())
    for at, word in enumerate(norm):
        if word not in ("thank", "thanks", "thankyou", "thank you", "thx", "ta"):
            continue
        rest = [w for w in norm[at + 1:] if w != "you"]
        if rest and rest[0] in WRITE_OBJECT:
            return True
    return False


# A question about what somebody else likes is a fact the memory store keeps against that person
# ("she's vegetarian and cant stand museums" -> "and what does she not like"), and the kitchen has
# an answer that is a dinner idea instead: the meat-free dish, because the vegetarian line was said
# a turn before. The store says the fact back with the person's name; a card about a dish answers a
# question nobody asked. Only the open ask is read here - "what does my mum hate" - because a yes/no
# about a named thing ("does she like museums") can be a real question about the thing.
A_TASTE_OF_THEIRS = re.compile(
    r"\b(?:what|which)\s+(?:does|do|did)\s+"
    r"(?:(?:my|our)\s+[a-z][a-z'\u2019-]*|he|she|they)\s+(?:not\s+)?"
    r"(?:like|love|enjoy|hate|dislike|mind|prefer|fancy)\b", re.I)


def _asks_about_their_taste(text):
    """Whether the line asks what somebody else likes or hates."""
    return bool(A_TASTE_OF_THEIRS.search(" ".join(str(text or "").lower().split())))


def _about_them_alone(low):
    """"what can she eat" asks for the person; "my mum" is the guest, not the speaker."""
    theirs = "|".join(mem.facts.RELATIONS)
    if re.search(r"\b(?:my|our)\s+(?:" + theirs + r")\b", low):
        return False
    return bool(re.search(r"\b(?:i|im|i'm|me|my|we|us|our)\b", low))


COMPLAINT = re.compile(r"\b(?:i (?:get|have|had|keep getting|keep|suffer from|live with)|"
                       r"i(?:'ve|ve) (?:got|had|been having))\b", re.I)


HEALTH_DOMAINS = frozenset(("body", "science", "fitness"))


_HEALTH = []


def _health_entries():
    """The answers about a person's own body, read once."""
    if not _HEALTH:
        _HEALTH.extend(one for one in all_entries()
                       if (getattr(one, "domain", "") or "") in HEALTH_DOMAINS)
    return _HEALTH


def _names_a_typed_word(item, text):
    """True when the entry is about a word the person actually typed."""
    said = {word.strip(".,!?;:").lower() for word in _flat(text).split()}
    return bool(said & _key_words(item))


# A detail that narrows a trouble is still about the answer on the screen: "it's worse when I lie
# down" after the heartburn answer is the line that answer already carries ("leave three hours
# between dinner and bed"). Read on its own words it asks for nothing, and the reply it used to
# get was "I'm listening - say more if it helps", which is what a person says when they have not
# heard you. The circumstance words are the join: the detail names when it is at its worst and the
# answer names the same time of day in its own words, so a family of them is how the two meet.
DETAIL_LINE = re.compile(r"\b(?:worse|better|only|mostly|mainly|usually|always|hurts|aches|sore)\b"
                         r"[^.!?]{0,30}?\b(?:when|if|at|after|before|in the|during|while)\b|"
                         r"\b(?:when|if|whenever) (?:i|we)\b", re.I)


CIRCUMSTANCE = (
    ("bed", "lie", "lying", "lay", "sleep", "sleeping", "night", "nights", "overnight",
     "pillow", "reclining", "wake", "waking", "morning", "mornings"),
    ("sit", "sitting", "sat", "chair", "desk", "seated", "screens", "screen", "computer", "work"),
    ("stand", "standing", "stood", "feet", "upright"),
    ("eat", "eating", "meal", "meals", "food", "dinner", "lunch", "breakfast", "swallow"),
    ("walk", "walking", "run", "running", "stairs", "steps", "climb", "climbing", "kneel"),
    ("bend", "bending", "stoop", "lift", "lifting", "carry", "carrying"),
    ("cold", "chilly", "damp", "winter", "weather", "rain"),
    ("stress", "stressed", "anxious", "worry", "worried", "tension", "busy"),
)


def _circumstances(text):
    """The circumstance family of every circumstance word in a line, and nothing else.

    Only the words in `CIRCUMSTANCE` count. Starting from every word of the line made the join
    between a detail and a sentence a shared pronoun: "it gets worse when its cold" and "It is
    ready when a fork twists easily in the middle" met on "it" and "when", and the doneness line
    of a slow roast was handed over as "the part for that" for a detail about the weather.
    """
    words = {word.strip("'") for word in re.findall(r"[a-z']+", str(text).lower())}
    found = set()
    for family in CIRCUMSTANCE:
        if words & set(family):
            found |= set(family)
    return found


# How the part of the answer that speaks to the detail is handed over. One frame is a little
# different from the next so that two details in a row do not come back in the same words.
DETAIL_FRAMES = ("Then this is the part that helps: {part}",
                 "That's the bit to work on: {part}",
                 "This is the part for that: {part}")


def _detail_frame(part):
    return DETAIL_FRAMES[len(part) % len(DETAIL_FRAMES)].format(part=part)


def _a_figure_the_answer_has(text, memory):
    """The sentence of the last answer that carries a figure this line names, or None."""
    from ..memory import detail as detail_reading  # noqa: PLC0415 - its own reader
    try:
        return detail_reading.the_fact_the_answer_has(text, memory)
    except Exception:  # noqa: BLE001 - a reader that cannot read is no answer here
        return None


def _a_detail_answered(text, memory):
    """The sentence of the last answer that speaks to this detail, or None."""
    line = str(text or "")
    if not DETAIL_LINE.search(line):
        return None
    reply = str(mem.last_bot(memory) or "")
    if not reply:
        return None
    want = _circumstances(line)
    known_first = None
    said = {stem(word) for word in keywords(line) if len(word) > 2}
    best, best_score, known = "", 0, False
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", reply) if part.strip()]
    for index, sentence in enumerate(sentences):
        if len(sentence.split()) < 6:
            continue
        if index == 0 and known_first is None and already_said(memory, sentence):
            known_first = sentence
        # A circumstance the two share is the join ("worse lying down" is "between dinner and
        # bed"), and a word the two share is the subject. A sentence that does not name the same
        # circumstance is not about this detail, however many words it shares.
        shared = want & _circumstances(sentence)
        if not shared:
            continue
        there = {stem(word) for word in keywords(sentence) if len(word) > 2}
        score = 2 * len(shared) + len(said & there)
        if score > best_score:
            best, best_score = sentence, score
            known = already_said(memory, sentence)
    if best and best == known_first:
        # The sentence that speaks to the detail is the opening of the answer they are reading:
        # handing it back, framed or not, is the paragraph they have just been given.
        return None
    if not best:
        return None
    if len(best.split()) * 2 >= len(str(reply).split()):
        # The part is most of the answer on the screen ("keep the room cool and dark, and don't
        # lie there fighting it - get up, then go back when you feel heavy again" is all but the
        # first nine words of it), so framing it as the part for the detail says the paragraph
        # again in other words. A part is only worth handing over when it is a part.
        return None
    # The line is a detail of the answer they are looking at, so the part of it for that detail
    # is named as such: the whole paragraph again, or the bare sentence with no lead-in, reads as
    # if the bot had not heard the detail at all.
    part = best[0].lower() + best[1:] if best[:1].isupper() else best
    return _detail_frame(part)


def _a_dish_was_offered(memory):
    """Whether the meal being planned has already been answered with food.

    The line before a diet said of a guest is the difference between the two: straight after
    "my mum is coming over on sunday for dinner" the diet is news about her, while after "what
    should i cook" it is telling the bot what the dish has to be.
    """
    if not isinstance(memory.get("meal"), dict):
        return False
    turns = memory.get("turns") or ()
    return bool(turns) and (turns[-1] or {}).get("module") == "answers"


def observe(text, memory):
    """Keep what the line says about the meal it is planning, for the next short line to narrow."""
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = understand(text, memory)
    try:
        a_year_of_birth.observe(text, memory)
    except Exception:  # noqa: BLE001 - a year of birth must never cost a turn
        pass
    try:
        plan = cooking.remembered(understood, memory)
    except Exception:  # noqa: BLE001 - a plan hint must never cost a turn
        return
    if plan:
        memory["meal"] = plan


# A line that asks only for a length of the thing just answered: "how long does it last",
# "how long does that take", "how many days then". Every word is the ask or a word pointing
# back at the answer, so the line names no thing of its own and the length is the answer's own.
# A line that names one - "how long until he is house trained", "how long should i rest it" -
# is another entry's question, and the length of the answer before it is no fact about it.
LENGTH_SAID = frozenset("""
    how long much many it that this these those them they he she you i
    do does did is are was were be been will would should can could
    a an the of to for in on at about more time day days week weeks month months
    hour hours minute minutes last lasts lasted going gone left
    take takes taking me us mine
""".split())


def _asks_only_the_length(text):
    """Is every word of this line the length ask or a word pointing back at the answer?"""
    words = [re.sub(r"[^a-z']", "", word.lower()) for word in str(text or "").split()]
    words = [word for word in words if word]
    if not words or not set(words) & {"long", "many", "much"}:
        return False
    return set(words) <= LENGTH_SAID


def TAKES_AS_IT_COMES(text, memory=None):
    """A request for less is answered with the answer they already have, cut down.

    The arbiter passes over a reply that is the last answer said again (the never-repeat rule),
    because a bare follow-up read as a fresh line comes back as "Same as before: <the opening>".
    A request for less is the one line where that shape is the whole answer, so the module says
    so on the line in front of it. Only where the hand-back is really there: on a request for
    less with nothing to cut down, this module has no claim and the lookup's reply is its own.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return False
    return bool(repeat.asks_for_less(text) and repeat.shorter_for(text, memory))
