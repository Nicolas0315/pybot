"""Part 5 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import last_bot, last_user
from ..understanding import understand
from . import (badnews, loss)
from .badnews import (reads_like_a_symptom)

from .fallback_data import (
    AXIS_MIN,
    BODY_SAYS_WHY,
    DONE_VERB,
    FLAT_CORE,
    FLAT_LEAD,
    KNOCKED_SPOTS,
    NARROW_ANSWERED,
    NARROW_SUBSTANCE,
    REACTION_DISBELIEF,
    REACTION_LEAD,
    REACTION_MISHAP,
    REACTION_OUCH,
    REACTION_RELIEF,
    REACTION_REPEAT,
    REACTION_REPEAT_FIRST,
    REACTION_WORD,
    THING_AFTER,
    VERDICT_ANNOY,
    VERDICT_BAD,
    VERDICT_FIRST,
    VERDICT_HEAVY,
    VERDICT_LUCK,
    VERDICT_NUMB,
    VERDICT_QUEUE,
    VERDICT_ROUGH,
    VERDICT_SETBACK,
    VERDICT_SHAME,
    VERDICT_WORD,
    _VERDICT_DET,
    _VERDICT_LEAD,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    HEAVY_NEWS,
)
from .fallback_part_01 import (
    _worry_is_about_the_body, _plain,
)
from .fallback_part_03 import (
    HEAVY_ABOVE, HAPPENING_NOW,
)
from .fallback_part_04 import (
    BABY_ON_THE_WAY, BODY_SAYS_WHY_PHRASE, DECLINE_TIME, DECLINE_ABOUT_THE_BOT, DECLINE_AFTER,
    DECLINE_ASK, DECLINE_BE_THERE, DECLINE_DATE, DECLINE_MUST, DECLINE_OCCASION, DECLINE_OTHER,
    DECLINE_OTHER_SUBJECT, DECLINE_VERB, VERB_PARTICLE, DECLINE_SOMEONE_ELSE,
)


def _the_reason_is_on_the_body(text):
    """True when this part of the line is the body giving the reason for the decline.

    Both sides of the verb are read. In front of it is the plain shape ("my back is bad and i cant
    come", "i feel awful and i cant come"); behind it the reason rides along with the day that
    follows the verb ("i cant come in today im sick", "i cant come in today my back is bad"), and
    the verb's own particle is taken off first so "come back on saturday" stays a day.
    """
    if not text:
        return False
    words = set(re.findall(r"[a-z']+", text))
    return bool(words & BODY_SAYS_WHY
                or _worry_is_about_the_body(text, words)
                or LATE_NOT_A_TIME.search(text)
                or BABY_ON_THE_WAY.search(text)
                or BODY_SAYS_WHY_PHRASE.search(text))


def _the_turn_before_was_a_heavy_one(memory, line=""):
    """True when the line before this one was a feeling, a symptom, or a body that is bad.

    "i had a panic attack" then "i cant come" is one thought: the panic is the reason and the plan
    is what it cost them. Answered as a plan dropped it asked somebody mid-panic whether they
    wanted to rearrange it, and the panic card - the words that say it passes and cannot hurt you -
    went missing. Three readers are asked, because the engine files these lines three ways:

    - the bot's own heavy pool, which `bot/modules/chat.py` notes when its reply is the one the
      person got: "im depressed" and "im really struggling" are filed as news, and the note is
      the only thing that knows they were answered as a mood;
    - the engine's reading of that line, for a feeling (`i feel awful`) and for a body
      (`i feel sick`, `my back is bad`, `i had a panic attack`);
    - the composer's own body reader, so a symptom said the plain way counts here too.

    Asked of the line before and never of this one: "i cant come" on its own says nothing about
    how they are, and a plan dropped in an ordinary week keeps the plan's answer.
    """
    # Only a decline that names nothing. "my back is bad" then "cant make it tonight" names the
    # evening, and the plan's own answer - the one that offers to rearrange it - beats the back
    # card said a second time.
    plain = _plain(line) if line else ""
    if plain and not (_a_declined_plan(plain, without_a_thing=True)
                      and not DECLINE_TIME.search(plain)):
        return False
    if not isinstance(memory, dict):
        return False
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    said = str(turns[-1].get("user") or "").strip().lower()
    if not said:
        return False
    try:
        read = understand(said)
    except Exception:  # noqa: BLE001 - a reading that fails is not a reason to take the turn
        read = None
    if isinstance(read, dict) and (
            read.get("intent") in ("question", "ask") or read.get("kind") == "question"):
        # An ask is not a feeling. "how do i stop feeling sick" then "i cant come" is a question
        # followed by a new line, and standing the decline down there answered it with the
        # conflict-advice card ("say what you want to change rather than what they did wrong").
        # Asked before the heavy note, because the bot answers that question with a heavy pool
        # and the note alone would call it a feeling.
        return False
    note = memory.get("heavy_reply")
    if isinstance(note, dict) and note.get("turn") == len(turns) - 1:
        return True
    if reads_like_a_symptom(said) or _the_reason_is_on_the_body(said):
        return True
    if not isinstance(read, dict):
        return False
    if read.get("intent") == "feeling" and (read.get("polarity") or 0) < 0:
        return True
    return bool(read.get("emotion") or read.get("body"))


def _a_declined_plan(clean, without_a_thing=False):
    """True when the line is the person saying they cannot make a plan.

    A friend hears "i cant come" as a plan being dropped, and answers the plan. The reading only
    says yes when the negated ability is about coming or making it and nothing follows but an
    apology, a day, or the thing itself, so every other sense of the same verbs keeps its own
    reply (see `DECLINE_OTHER`).

    `without_a_thing` is for the claim (`TAKES_AS_IT_COMES`), which takes a line off whatever else
    proposed it. Only the lines nothing is likely to answer well are claimed: the bare decline and
    the one with a day in it. A line that names the occasion - "cant come to the party" - is
    claimed by nobody here, because the entry about telling someone you cannot come answers it
    better than this pool can.
    """
    line = " ".join(str(clean or "").replace("\u2019", "'").replace("'", "").strip().split())
    if not line or DECLINE_ASK.match(line) or line.endswith("?"):
        return False
    found = None
    for pattern in (DECLINE_VERB, DECLINE_MUST):
        for match in pattern.finditer(line):
            if DECLINE_ABOUT_THE_BOT.search(line[:match.start()]):
                continue
            found = match
            break
        if found:
            break
    if not found:
        return False
    # "my period is late and i cant come", "the baby is due and i cant come": the reason is the
    # body, and the line has a health answer behind this one.
    if (_the_reason_is_on_the_body(line[:found.start()])
            or _the_reason_is_on_the_body(VERB_PARTICLE.sub(" ", found.group(1)))):
        return False
    tail = DECLINE_AFTER.sub("", found.group(1).strip(" ,.-!?")).strip(" ,.-!?")
    if not tail:
        return True
    # "i cant be there for him" / "for her mum" / "for the birth": being there for somebody is
    # not a plan, and the tail's "for" is what this reading otherwise calls the thing itself.
    if tail.startswith("for ") and DECLINE_BE_THERE.search(line[:found.end(0) - len(found.group(1))].rstrip()):
        return False
    # "i have to cancel" is a plan dropped; "i have to cancel my dentist appointment" is a job, and
    # the entry that cancels one has the answer. Only the plan-shaped tail gets the plan reply.
    if found.re is DECLINE_MUST and not DECLINE_TIME.search(tail):
        return False
    if DECLINE_DATE.search(tail):
        return True
    # A day is a plan whether or not the tail opens with a particle: "i cant come on saturday" is
    # as much a plan as "i cant come on the 14th". The particle keeps its own sense for a thing
    # ("my heating wont come on tonight"), which is why the person has to be in the line.
    if DECLINE_TIME.search(tail):
        if not DECLINE_OTHER.match(tail) or not DECLINE_OTHER_SUBJECT.match(line):
            return True
    if DECLINE_OTHER.match(tail):
        return False
    # The bare plan without a day: "i cant make it", "cant make it im afraid". The claim takes it
    # too, because the other pools read "afraid" as a worry and answer it with "what's one thing
    # you can check", which is not words for somebody dropping an evening.
    if tail in ("it", "there", "along"):
        return True
    # The thing itself: "cant come to the party", "cant make it to sams", "cant come out for it",
    # "cant make the wedding", "cant come on the 14th".
    if without_a_thing:
        return False
    if tail.startswith(("to ", "for ", "it to ", "it on ", "it for ", "it at ", "it next ")):
        return True
    return bool(DECLINE_OCCASION.search(tail))


def _someone_else_dropped_it(clean):
    """True when the plan being dropped is somebody else's, not the person's own.

    The same match `_a_declined_plan` takes, so the two readings can never disagree about which
    "cant come" the line is about: the words in front of it decide who cannot come.
    """
    line = " ".join(str(clean or "").replace("\u2019", "'").replace("'", "").strip().split())
    if not line or not _a_declined_plan(clean):
        return False
    for pattern in (DECLINE_VERB, DECLINE_MUST):
        for match in pattern.finditer(line):
            if DECLINE_ABOUT_THE_BOT.search(line[:match.start()]):
                continue
            return bool(DECLINE_SOMEONE_ELSE.search(line[:match.start()]))
    return False


# The answer above has to be about that axis, or the cut asks about a subject the answer never
# raised: "my washing machine is leaking" / "not too far" got "Nearer, then. How far are you happy
# to travel?", and "i cant sleep" / "cheaper" got "Cheaper, then. What's your limit?" Both are
# worse than the bland ack they replaced, because a confident question about the wrong thing is
# worse than a shrug. A procedure has nothing to narrow; an answer that offers things to choose
# between has, and it says so in the axis's own words.
# The answer has to offer the person a cut, and what it offers is a quantity or a bound: "takes 2
# minutes", "a frittata in 20", "£300 to £700", "40 minutes on the train". A word that happens to be
# in the answer is not enough, which is what went wrong the first time: "what helps a headache" /
# "smaller" cut for size because the answer said "a quiet dark room", and "i want to start running"
# / "something easy" cut for effort because the answer said "easy jogging". Neither answer offered
# anything to narrow. A number with its unit is the plainest sign that an answer does.
# The other sign that an answer offered things to choose between, and one that does not need the
# axis's word: it named them. "Cyprus or Crete ... the Canaries ... Seville and Marrakesh" never
# says "travel", and it is plainly a list of places to pick from. Two or more names that are not at
# the start of a sentence is the plainest reading of that, and it leaves a procedure alone, because
# a procedure names nothing to choose between ("Try a warm bath or a glass of milk").
#
# The "or" is what separates a choice from a list of parts. "Cyprus or Crete ... the Canaries ...
# Seville and Marrakesh" offers things to pick between; "the pressure gauge, the thermostat and the
# boiler's reset button" is everything to check on one boiler, and "not too far" after it is not a
# narrowing but a person still talking about a fault. Both list names, and only one of them is
# offering the person a choice, so the reading needs the word a choice is made with.
def _names_things_to_choose(said):
    """True when the answer puts two or more named things in front of the person, to pick from."""
    said = str(said or "")
    if not re.search(r"\bor\b", said, re.I):
        return False        # a list of parts to check ("the gauge, the thermostat and the button")
    words = said.split()
    named = set()
    for index, word in enumerate(words):
        bare = word.strip(".,;:!?*()\u2014-\u2019'\"")
        if len(bare) < 2 or not bare[0].isupper() or not bare[1:].islower():
            continue
        if index == 0:
            continue
        before = words[index - 1].rstrip()
        if before.endswith((".", "!", "?", ":")) and not before.endswith("..."):
            continue      # the first word of a sentence is a capital for grammar, not a name
        named.add(bare)
    return len(named) >= 2


AXIS_SAID = {
    "far": re.compile(r"\b\d+\s*(?:miles?|km)\b"
                      r"|\b(?:nearer|nearby|close by|local|walkable|travel|journey|commute)\b", re.I),
    "price": re.compile(r"[\u00a3$\u20ac]\s?\d|\b\d+\s*(?:pounds?|quid|dollars?|euros?)\b"
                        r"|\b(?:cost|costs|price|prices|budget|afford|spend)\b", re.I),
    "time": re.compile(r"\b\d+\s*(?:min(?:ute)?s?|mins?|hours?|hrs?)\b"
                       r"|\b(?:in|takes?|leave it|for) \d+\b", re.I),
    "effort": re.compile(r"\b(?:easier|simple|simpler|effort|faff|fiddly|elbow grease|hard work)\b",
                         re.I),
    "size": re.compile(r"\b\d+\s*(?:cm|mm|m|inch|inches|ft|feet)\b"
                       r"|\b(?:size|measurements?|width|depth|height|fits?|fitting)\b", re.I),
}


# A fault has nothing to choose between, so a cut after one is the same wrong question: "my boiler
# is broken" / "under 20 minutes" got "Then the short version. How many minutes have you got?" -
# and the boiler answer had already said how long the fix takes. Nothing after a fault is a
# narrowing.
# The words are the ones people use for a thing that has gone wrong, not the names of faults: "keeps
# cutting out", "very slow", "dies by lunchtime" and "freezes" are as much a fault as "broken", and
# each was a cut that asked a worried person about their holiday.
A_FAULT = re.compile(
    r"\b(?:broken|leaking|leaks|leaked|wont|won't|stopped|jam(?:med)?|stuck|blocked|"
    r"smells?|smelling|dripping|drips|dead|fault|faulty|error|blinking|not working|"
    r"isn't working|isnt working|no hot water|no power|tripping|cracked|crack|smashed|dented|"
    r"damaged|torn|ripped|soaked|flooded|not charging|wont charge|seized|"
    r"cutting out|cuts out|cut out|keeps (?:stopping|dying|cutting|freezing|restarting|turning off)"
    r"|dies|dying|freezes|freezing|frozen|sluggish|laggy|super slow|very slow|too slow|so slow"
    r"|slow(?:ed)? (?:down|up)|rattl\w+|noisy|clogged|gunked|corroded|rusty|worn out|"
    r"keeps (?:flashing|beeping|going off)|flashing|beeping|overheating|too hot|smoking|sparking)\b",
    re.I)


def the_answer_to_cut(memory, axis=""):
    """The answer still on the screen, or {} when the turn above is not one to narrow.

    A question from the bot is not an answer to narrow ("what have you tried so far?" then "not
    too far" is the person answering it), and neither is a loss or anything a person said about
    themselves: those threads are held by the modules that opened them.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return {}
    last = turns[-1]
    if not isinstance(last, dict) or last.get("module") not in NARROW_ANSWERED:
        return {}
    said = last.get("bot")
    if not isinstance(said, str) or len(said.split()) < NARROW_SUBSTANCE:
        return {}
    if said.rstrip().endswith("?"):
        return {}
    if axis:
        raised = AXIS_SAID.get(axis, re.compile(r"(?!)")).findall(said)
        if len(raised) < AXIS_MIN.get(axis, 1) and not _names_things_to_choose(said):
            return {}       # the answer never raised the axis the line narrows on
    if A_FAULT.search(str(last.get("user") or "")):
        return {}       # a fault is not a list of things to choose between
    return last


# The laughter itself, not the word "funny": a bare "funny" is either the joke module's ask
# ("my son said something funny") or a doubt ("funny that the bus never came"), and neither is a
# laugh to answer with a laugh.
LAUGHING = re.compile(
    r"\b(?:laugh(?:ed|s|ing)?|laughter|giggl(?:e|ed|es|ing)|in stitches|"
    r"cracked (?:me|us) up|crackin(?:g)? (?:me|us) up|hilarious|hysterical|"
    r"(?:can'?t|cant|couldn'?t|couldnt) (?:stop|help) laughing|"
    r"wet (?:myself|himself|herself) laughing|"
    r"had (?:a|such a|a right|a proper|the best) laugh|bit of a laugh|"
    r"so funny|funniest thing)\b", re.I)


# Not every mention of a laugh is a laugh at something good: being laughed at is a bad day, and
# "it is not funny" is the person saying the opposite of the pool's line.
# Being laughed at is being mocked, and the object is rarely "me": "she laughed at my hair",
# "they laughed at my name", "the class laughed at my drawing" were all answered with a laugh
# back, which is the bot joining in. Any possessive or person after the at is the same shape, and
# so is "he laughed when i fell over", where the laugh is at the accident rather than with them.
LAUGHING_AT = re.compile(
    r"\b(?:laugh(?:s|ed|ing)?|giggl(?:e|es|ed|ing)|snigger\w*|snicker\w*|titter\w*|"
    r"a laugh)\s+(?:at|about)\s+(?:me|us|him|her|them|you|my|his|her|their|our|your)\b"
    r"|\b(?:laugh(?:s|ed|ing)?|giggl(?:e|es|ed|ing))\s+(?:when|after|because)\s+i\b"
    r"|\bnot (?:even |that |remotely )?funny\b|"
    # "nobody laughed" is the same fault as "she laughed at my hair": the laugh did not happen,
    # and a line about it happened is what the person is telling the bot.
    r"\b(?:nobody|no one|no-one|nobodys|no ones)(?:'s)? (?:is |was |did |has )?"
    r"(?:laughing|laughed|laugh)\b|\bno laughing matter\b"
    # A laugh that is wanted rather than had: "we could do with a laugh" and "i need a laugh"
    # are asking for one, and answering as if the day had been funny misses the ask.
    r"|\b(?:could do with|could use|needs?|needed|want(?:s|ed)?|in need of|short of) "
    r"(?:a|a bit of a|a good|a right) laugh\b"
    # The person about themselves: "im so funny" names no thing that was funny, so there is
    # nothing for "what set it off?" to be about.
    r"|\bi(?:'m|m| am)\b\s+(?:so |really |very |quite |well |proper )*funny\b", re.I)


FLAT_LINE = re.compile(r"^\W*" + FLAT_LEAD + FLAT_CORE + r"\W*$")


REACTION_LEAD += r"but|ok|okay|bloody|hell|damn|fucking)\s+)*"


REACTION_LINE = re.compile(
    r"^\W*" + REACTION_LEAD + r"(?:" + REACTION_WORD + r")"
    r"(?:[\s,]+(?:and\s+)?" + REACTION_WORD + r"){0,6}\W*$")


# What makes the line a reaction rather than a line made of the same small words. The pool is the
# first signature that is in it, so "oh no, that sucks" is sympathy and "oh no" is the mishap.
REACTION_SIGNS = (
    (REACTION_RELIEF, re.compile(
        r"\b(?:phew|finally|thank (?:god|goodness|heavens|christ|fuck))\b")),
    # A swear is a wince at something that happened, not a mishap of the bot's own: "i lost my
    # job today" / "dammit" was answered "Whoops. What happened?", which is the pool for a spill.
    (REACTION_OUCH, re.compile(
        r"\b(?:ouch\w*|ow+|yikes|eek|oof|yowch|sucks|brutal|awful|terrible|horrible|rough|"
        r"dammit|damn it|bugger|crap|shoot)\b")),
    (REACTION_MISHAP, re.compile(
        r"\b(?:oops|whoops|oh (?:no|dear)|dear me)\b")),
    (REACTION_DISBELIEF, re.compile(
        r"\b(?:seriously|are you serious|you(?:'?re| are)? (?:joking|kidding)|for real|no way|"
        r"no chance|surely|really|honestly|wtf|what the (?:hell|heck|devil|fuck|blazes|dickens)|"
        r"what (?:on|in) (?:earth|the world)|why (?:on|in) (?:earth|the world)|"
        r"get out|you what|"
        r"come on|wow+|woah|whoa|omg|oh my (?:god|word)|blimey|crikey)\b")),
    (REACTION_REPEAT, re.compile(r"\b(?:huh|eh|pardon)\b")),
)


def _the_person_already_said_it(memory):
    """True when the last thing the person said was the story the reaction is reacting to."""
    said = str(last_user(memory) or "").strip()
    if not said or said.rstrip().endswith("?"):
        return False
    return len(said.split()) >= 4


# A miscarriage is a loss the grief reading does not hold ("i had a miscarriage" is not a death in
# its words), and it is the shape the deck row that started this guard is.
BABY_LOSS = re.compile(r"\bmiscarriage(?:s)?\b(?! of justice)|\bmiscarried\b|\bstillborn\b"
                       r"|\bstillbirth\b", re.IGNORECASE)


def _the_last_few_lines(memory):
    """The person's own last few lines, as the thread left them."""
    return [" ".join(str(turn.get("user") or "").lower().split())
            for turn in [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-4:]
            if str(turn.get("user") or "").strip()]


def baby_loss(clean):
    return bool(BABY_LOSS.search(str(clean or "")))


# Only the words that are a verdict on their own. "what a day" and "what a week" are left out on
# purpose: those two are the rough-day reading chat already has, and a pool that asks what
# happened is the wrong question to a person who has just said the week was long.
VERDICT_SAID = re.compile(
    r"^\W*" + _VERDICT_LEAD + _VERDICT_DET + r"(?P<noun>" + VERDICT_BAD + r")\b" +
    # A word said after the verdict belongs to it ("what a nightmare honestly"), and it is a
    # closed list, so "what a mess at the office" is still a line with a subject in it.
    r"(?:\s+(?:honestly|really|though|today|now|again|here|seriously|mate|man))*\W*$")


# The words people type with nothing in front of them at all: "nightmare", "a nightmare". Only
# the strong ones, because a bare "pain" is more often where it hurts and a bare "state" is not a
# verdict anybody types alone.
VERDICT_BARE = re.compile(
    r"^\W*" + _VERDICT_LEAD + r"(?:a|an|the|right|proper|absolute|total|complete|right old)?\s*"
    r"(?P<noun>nightmare|mess|disaster|shambles|farce|palaver|shower)\W*$")


# A verdict on the thing before it is a verdict on what the bot has just said, and when that was a
# joke the person asked for, "what a joke" is them rating the joke. Read as a verdict on something
# that happened to them, it got sympathy: "tell me a joke" / "what a joke" was answered "Ouch.
# Sorry, that sounds rough." - the bot sympathising with its own punchline, where the joke entry
# used to tell another one. The request is read with the narrow shape chat.py's `JOKE_ASK` reads,
# because "joke" is in "my mate made a joke about my dad" too, and only a request makes the answer
# above a punchline.
JOKE_WANTED = re.compile(
    r"\b(?:tell|say|make|give|got|know|another|more|one more)\b[^.]{0,24}"
    r"\b(?:joke|jokes|pun|puns|funny|riddle|limerick|meme)\b|"
    r"\bmake me laugh\b|\bcheer me up\b|\banything funny\b|\bjoke please\b", re.I)


# A line that asks the jokes to stop ("dont make jokes about my mum", "no more puns") names one
# without wanting one, and the answer above it was not a punchline.
JOKE_UNWANTED = re.compile(r"\b(?:dont|don't|do not|stop|no more|enough|pack it in)\b")


def _the_answer_above_was_a_joke(memory):
    """True when the person's own last line asked for a joke, so the answer above was one."""
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return False
    asked = " ".join(str(turns[-1].get("user") or "").lower().split())
    if JOKE_UNWANTED.search(asked):
        return False
    return bool(JOKE_WANTED.search(asked))


def _a_verdict_line(text, memory=None):
    """The pool for a line that is only a verdict on the thing before it, or None."""
    text = " ".join(str(text or "").lower().split())
    found = VERDICT_SAID.match(text)
    if not (found or VERDICT_BARE.match(text)):
        return None
    # Only the word "joke" is the person rating the punchline: "what a mess" or "what a state"
    # said to a bot that has just told a joke is still a verdict on something else, and standing
    # down on those handed the line to the search hedge.
    if found and found.group("noun") == "joke" and memory is not None \
            and _the_answer_above_was_a_joke(memory):
        # The thing before it was the bot's own punchline, so this is the person's opinion of it,
        # and the turn goes back to the entry that told the joke.
        return None
    return REACTION_OUCH


# A verdict about the situation takes the turn; a verdict about a thing the person named does
# not. "it was rubbish" after "we went to spain six weeks ago" is chat's line ("Shame about
# Spain"), and "its not fair" has a pool of chat's own, so the past tense is read as a thing and
# the bare/shouted words are the reading here. See `reads_as_a_verdict`.
VERDICT_LINE = re.compile(
    r"^\W*(?:(?:that|thats|that'?s|this|it|it'?s|how|so|very|really|bloody|just)\s+"
    r"(?:is\s+)?)?(?:" + VERDICT_WORD + r")"
    r"(?:\W+(?:isnt\s+it|innit|though|honestly|really|mate|god|ugh))?\W*$"
    r"|^\W*(?:it|it'?s|that|thats|that'?s|this)\s+(?:is\s+)?"
    r"(?:rubbish|pants|crap|a\s+nightmare|a\s+mess|a\s+joke)"
    r"(?:\W+(?:isnt\s+it|innit|though|honestly|really|mate))?\W*$"
    r"|^\W*(?:typical(?:\s+(?:isnt\s+it|innit|that|again|honestly))?|just\s+my\s+luck|"
    r"that\s+figures|figures|sod'?s\s+law|of\s+course\s+it\s+(?:did|was|is)|"
    r"what\s+a\s+(?:pain|hassle|shame|nightmare|joke|mess|headache|letdown))\W*$")


# The news a rough verdict lands on: the person's own body or sleep, not a thing that broke.
# The words are read off the line the verdict is about, so "my landlord wont fix the boiler" and
# "our move got pushed back" are none of them - they are news about a thing and a plan.
STATE_ABOVE = re.compile(
    r"\b(?:can'?t\s+sleep|cant\s+sleep|not\s+sleeping|no\s+sleep|keep\s+waking|"
    r"hurts?|hurting|ache|aches|aching|sore|in\s+pain|pain\s+in|"
    r"ill|sick|poorly|a\s+temperature|migraine|dizzy|shaking|shivery|"
    r"no\s+energy|worn\s+out|exhausted|knackered|burnt?\s+out)\b")


def a_death_just_said(memory=None):
    """True when the news the verdict lands on is a death, not a hard week or a diagnosis.

    The difference matters for the wording: a diagnosis or a fall can be asked about, and a
    friend does, but the turn after a death is not a question.
    """
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if not line:
            continue
        try:
            if loss.reads_as_loss(line):
                return True
        except Exception:  # noqa: BLE001 - a reading that cannot run claims nothing
            continue
    return False


def a_verdict_on_the_person(memory=None):
    """True when the verdict is landing on a state of the person rather than on news.

    Read from the person's own line a turn or two back, the same shape as `a_heavy_verdict`.
    """
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if line and STATE_ABOVE.search(line):
            return True
    return False


# The news those two pools are for, read off the person's own line the same way the heavier
# readings are. Only these alternatives of `HEAVY_NEWS` are here: a diagnosis, a hospital and a
# leaving are in neither list and keep the sympathy pool above.
WAITING_NEWS = re.compile(
    r"\b(?:wait(?:ing)?\s+(?:\w+\s+){0,4}(?:weeks|months)|on\s+a\s+waiting\s+list|"
    r"months?\s+for\s+(?:the\s+|an\s+|a\s+)?(?:appointment|scan|referral|operation))\b")


JOB_GONE_NEWS = re.compile(
    r"\b(?:lost\s+my\s+(?:job|work|hours)|laid\s+off|made\s+redundant|been\s+(?:sacked|"
    r"fired)|got\s+(?:sacked|fired|let\s+go)|sacked\s+(?:from|on)|let\s+go\s+from)\b")


def _the_last_two_lines(memory=None):
    """The person's own lines for this turn and the one before - never the bot's wording."""
    lines = []
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if line:
            lines.append(line)
    return lines


def _a_loss_in_the_same_breath(memory=None, lines=()):
    """True when the heavier news is there too, so the middle pools must stand aside.

    A queue is not the whole story when the same line carries the thing being waited on: "waiting
    to hear if my dad pulled through" is not a wait to be asked about, and a redundancy that came
    with a diagnosis is a diagnosis.
    """
    if a_death_just_said(memory) or a_heavy_verdict(memory):
        return True
    for line in lines:
        if HEAVY_ABOVE.search(line):
            return True
        try:
            if (badnews.reads_as_sudden_loss(line) or badnews.reads_as_the_leaving(line)
                    or loss.reads_as_loss(line)):
                return True
        except Exception:  # noqa: BLE001 - a reading that cannot run claims nothing
            continue
    return False


def a_wait_with_no_loss(memory=None):
    """True when the heavy news is a queue rather than a person lost."""
    lines = _the_last_two_lines(memory)
    if not any(WAITING_NEWS.search(line) for line in lines):
        return False
    return not _a_loss_in_the_same_breath(memory, lines)


def a_setback_with_no_loss(memory=None):
    """True when the heavy news is a job gone rather than a person lost."""
    lines = _the_last_two_lines(memory)
    if not any(JOB_GONE_NEWS.search(line) for line in lines):
        return False
    return not _a_loss_in_the_same_breath(memory, lines)


def _the_heavy_pool(memory=None):
    """The pool for a verdict on news with no repair in it: a loss, a queue or a setback."""
    if a_death_just_said(memory):
        return VERDICT_NUMB
    if a_wait_with_no_loss(memory):
        return VERDICT_QUEUE
    if a_setback_with_no_loss(memory):
        return VERDICT_SETBACK
    return VERDICT_HEAVY


# The line above a verdict that makes it a heavy one: missing somebody, in tears, worn down by
# a loss that is still being carried. Not a death said out loud (that stands the verdict down
# whole, `a_verdict_stands_down`), but the turn after the death, and the crying that has no
# event in it yet.
GRIEF_ABOVE = re.compile(
    r"\b(?:miss(?:es|ed|ing)?\s+(?:my|his|her|their|our|you|them|him|her|mum|dad|mother|father|"
    r"sister|brother|son|daughter|nan|grandma|grandad|gran|grandpa|friend)|"
    r"crying|cry(?:ing)?\s+(?:myself|a lot)|can'?t\s+stop\s+crying|keep\s+crying|"
    r"griev(?:e|ing)|bereave\w*|heartbroken|wish\s+(?:he|she|they)\s+(?:was|were)\s+(?:still\s+)?"
    r"here|empty\s+without|lonely\s+without|still\s+can'?t\s+believe\s+(?:he|she|they)\s+"
    r"(?:has|have)\s+gone)\b")


def a_heavy_verdict(memory=None):
    """True when the verdict is landing on grief rather than on news.

    Read from the person's own line a turn or two back, the same shape as the demonstrable
    readings (`a_verdict_stands_down`), because the bot's wording for the turn before is not the
    thing being judged: "i miss my mum" was answered by chat's own comfort line, and the verdict
    the person brings next is still about the missing.
    """
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if line and GRIEF_ABOVE.search(line):
            return True
    return False


def a_happening_now(memory=None):
    """True when the thing above is still going on, so a sympathy line is not the turn."""
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if line and HAPPENING_NOW.search(line):
            return True
    return False


# A verdict points back at something: the news the person brought, or the answer the bot just
# gave. It is read from the words where the words say so on their own ("thats annoying", "such a
# pain", "how annoying") and from the conversation where they do not ("a nightmare", "typical"
# as the whole of the line). Without a turn before it there is nothing it is a verdict on: a bare
# "a nightmare" as the first line of a chat was answered "Annoying. Is it a quick fix or a whole
# thing?" instead of the floor (crisp-jackal on #5479).
VERDICT_POINTS_BACK = re.compile(
    r"^\W*(?:that|thats|that'?s|this|it|it'?s|how|what\s+a|such\s+a|of\s+course\s+it)\b")


def _a_verdict_on_something(text, memory):
    """True when there is a turn for this verdict to be about.

    A verdict is a comment, so it needs the thing it comments on: the news the person brought a
    turn ago, or the answer the bot gave after it. A demonstrative carries its own subject
    ("thats annoying" is about what was just said), so those stand whatever the conversation has
    in it; the bare sayings only count once the conversation has a turn in it.
    """
    if VERDICT_POINTS_BACK.match(text):
        return True
    try:
        turns = (memory or {}).get("turns") or []
    except Exception:  # noqa: BLE001 - a conversation that cannot be read has no turn in it
        return False
    return any(isinstance(turn, dict) for turn in turns)


def _verdict_pool(clean, memory=None):
    """The pool for a verdict on the news, or None when the line is anything more."""
    text = " ".join(str(clean or "").lower().split())
    if not text or not VERDICT_LINE.match(text) or "?" in text:
        return None
    if memory is not None and not _a_verdict_on_something(text, memory):
        return None
    # A verdict with nothing before it is the whole turn: the person is reacting to the day, not to
    # an answer, and every light pool line asks about the news ("Is it a quick fix or a whole
    # thing?" of nothing). The reaction pool is what main answered with, and it is right - "Ouch.
    # What happened?" - so the pool stands down and the reaction takes the turn
    # (steward-frank-chicken on #5479, who was reading a red test on main).
    if isinstance(memory, dict):
        turns = memory.get("turns") or []
        if not any(isinstance(turn, dict) for turn in turns):
            return None
    if re.search(r"\b(?:shame|letdown)\b", text):
        return VERDICT_SHAME
    if re.search(r"\b(?:typical|figures|luck|law|of course)\b", text):
        return VERDICT_LUCK
    if a_verdict_on_the_person(memory):
        return VERDICT_ROUGH
    return VERDICT_ANNOY


def a_heavy_news(memory=None):
    """True when the news the verdict lands on has no repair in it.

    Read from the person's own line a turn or two back, like the readings beside it: the bot's
    wording for the turn before is not what is being judged.
    """
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if not line:
            continue
        if HEAVY_NEWS.search(line):
            return True
        try:
            if badnews.reads_as_the_leaving(line):
                return True
        except Exception:  # noqa: BLE001 - a reading that cannot run claims nothing
            continue
    return False


def reads_as_a_verdict(text, memory=None):
    """True when the whole line is a verdict on the news, for the arbiter's routing.

    A verdict has no subject of its own, so the topic the conversation is on must not stand in
    for it: "thats annoying" after a cooking answer is not a question about cooking, and it was
    answered with a recipe.
    """
    try:
        return _verdict_pool(text, memory) is not None
    except Exception:  # noqa: BLE001 - a reading that cannot run just claims nothing
        return False


# The verdict shapes a person opens with, which is a longer list than the verdicts the pools above
# take: a first line has no subject anywhere in the chat, so a reaction word is the whole of what
# the bot has to go on. "thats tough going" was the commonest line tawny-donkey found reaching the
# intake form on main (#routing 82965).
FIRST_TURN_VERDICT = re.compile(
    r"^\W*(?:(?:that|thats|that'?s|this|it|it'?s|how|what\s+a)\s+"
    r"(?:is\s+|was\s+)?(?:so\s+|very\s+|really\s+|bloody\s+|just\s+|proper\s+)?"
    r"(?:tough|hard|rough|grim|annoying|a\s+pain|a\s+shame|a\s+nightmare|a\s+hassle|"
    r"a\s+joke|a\s+mess|frustrating|rubbish|sad|depressing|draining|exhausting|"
    r"a\s+slog|a\s+grind|a\s+bummer))"
    r"(?:\s+(?:going|innit|though|honestly|really|mate|god|ugh|isnt\s+it))?\W*$"
    r"|^\W*(?:typical(?:\s+(?:isnt\s+it|innit|again|honestly))?|just\s+my\s+luck|"
    r"that\s+figures|figures|bloody\s+hell|what\s+a\s+(?:pain|hassle|shame|nightmare|"
    r"joke|mess|headache|letdown))\W*$")


def _reaction_pool(clean, memory=None):
    """The pool for a bare reaction, or None when the line is anything more than one."""
    text = " ".join(str(clean or "").lower().split())
    # Before the reaction grammar, because the verdict shapes are not made of reaction words.
    verdict = _a_verdict_line(text, memory)
    if verdict:
        return verdict
    # A verdict with no turn before it: the pool above needs something to point back at, and
    # standing the verdict down whole left the intake form underneath it. The shape is read here
    # rather than by widening `VERDICT_WORD`, because a verdict inside a thread belongs to the
    # pools above ("thats tough going" after a hard week has chat's "Fair enough. What has been
    # the hardest bit?"), and only the first-turn case is unclaimed.
    if FIRST_TURN_VERDICT.match(text) and not ((memory or {}).get("turns") or []):
        return VERDICT_FIRST
    if not text or not REACTION_LINE.match(text):
        return None
    for pool, sign in REACTION_SIGNS:
        if sign.search(text):
            return pool
    if re.fullmatch(r"[\w']*\s*(?:what|pardon)\W*", text):
        # "what?" is the person asking for the last answer again, so there has to be one: on an
        # empty conversation "I'll put it another way - what bit was unclear?" answers nothing.
        if memory is not None and not last_bot(memory):
            return REACTION_REPEAT_FIRST
        return REACTION_REPEAT
    return None


# The apology in front, with the small words people put before it.
_SORRY_LEAD = re.compile(
    r"^\W*(?:(?:oh|and|but|so|yeah|yep|ok|okay|well|hi|hey|right|alright|also)\W+)*"
    r"(?:(?:so|very|really)\s+)?(?:sorry|apologies|apologise)\b")


# Being late is not a job under way: "im running late for work" was read off the verb as a thing
# in the middle ("im painting my kitchen") and answered "Nice - is it the messy bit yet?" at
# somebody rushing to get in. A lateness report has one useful reply - say it now, with the time
# you will be there - and the question back is about the holding up, which is the part they can
# talk about while they move. Only the speaker's own lateness: "its too late", "my period is
# late" and "the train was late" are different lines.
LATE_NOW = re.compile(
    r"\b(?:i'm|im|i am|i'll|ill|i will)\s+((?:so\s+|really\s+|a bit\s+|a little\s+|still\s+|"
    r"definitely\s+|probably\s+|going to be\s+|gonna be\s+|will be\s+|running\s+|be\s+|b\s+)*)"
    r"(?:late|behind)\b"
    r"|^\s*late(?: again)?\b")


# "im not late" and "im never late" are the opposite report, and the word that says so sits between
# the speaker and it: the guard reads only that stretch, so "i'm late and i've not eaten" is still
# a lateness. "we're late" is about a group of people including whoever they are answering to, so
# it is not the speaker's own report either.
LATE_NOT_IT = re.compile(r"\b(?:not|never|n't)\b")


# A period that has not come is not a person running behind, and "im late for my period" would take
# the pool ahead of the health card that reads it.
LATE_NOT_A_TIME = re.compile(r"\b(?:period|periods|pregnan\w*)\b")


# "im late again, what do i say to my boss" is a request for the words, and the late-for-work card
# has them: the pool is for the report, not for the ask on top of it.
LATE_ASKS = re.compile(
    r"\b(?:what|how|should i|do i|can i|shall i|what do i say|what should i say|tell my|"
    r"explain|apolog\w*)\b")


DONE_SUBJECT = re.compile(r"\b(?:i|we)\s+(?:just\s+|also\s+|finally\s+|only\s+|actually\s+)?"
                          r"([a-z]+)\b")


# A report is a finished sentence. "cleaned the kitchen" is news; "cleaned the kitchen what about
# the oven" is news and a question, and the question is the turn the person asked for - chat-speak
# drops the question mark, so the "?" test alone let every one of these through and the cheer took
# the turn away from the answer that was there ("cleaned the kitchen what about the oven" lost the
# oven paste, "booked the hotel is it refundable" the refund answer). The asks are named rather
# than guessed, because a bare "what" is also in a plain report ("painted the fence what colour
# she wanted").
# The other second half is a grumble, and a grumble is the turn: "cleaned it and now it smells" is
# a person with a problem, not a person reporting a job well done. Only the negative states, so
# "cleaned the kitchen and now it looks lovely" keeps the cheer.
TAIL_GRUMBLE = re.compile(
    r"\bnow (?:it|they|that)\b[^.!?]{0,20}?\b(?:smells?|stinks?|worse|broken|leaking|mouldy|"
    r"moldy|damp|still|not)\b", re.I)


# The third second half is a problem, and it is the turn too: "paid the deposit and the landlord
# says its not showing" is a person with a deposit, not a person reporting a job well done, and
# the same for "booked the hotel and then found it cheaper". TAIL_GRUMBLE reads a state that
# changed ("now it smells"), and these say it as a sentence of somebody else's or as a find, so
# the trouble words are read wherever they sit: the trouble is the tail.
TAIL_TROUBLE = re.compile(
    r"\b(?:says?|said|told\s+me|tells\s+me|reckons?|claims?|because)\b[^.!?]{0,30}?\b(?:not|never|"
    r"no|wont|won't|cant|can't|couldnt|couldn't|refus\w*|wrong|missing|lost|broken|damaged|"
    r"cheaper|expensive|late|still|again|failed)\b"
    r"|\bfound\s+(?:it|them|that|out)\b[^.!?]{0,24}?\b(?:cheaper|expensive|broken|wrong|"
    r"damaged|dirty|damp|missing|late|cancelled|canceled|cracked|faulty|empty)\b"
    r"|\b(?:is|was|were|are|isnt|isn't|wasnt|wasn't)\s+(?:not\s+|never\s+)?(?:showing|shown|"
    r"arrived|arriving|working|registered|covered|paid|come\s+through|turned\s+up)\b[^.!?]{0,16}?"
    r"\b(?:not|never|no|still|yet|nothing)\b"
    r"|\b(?:didnt|didn't|hasnt|hasn't|hadnt|hadn't|never)\s+(?:show|shown|arrive|work|come|"
    r"register|turn\s+up|pay|go\s+through)\b", re.I)


# The same fault in its plainest form: the second half is a complaint and the complaint has no
# shape to name - "sorted the boiler service and now the radiators are cold", "cancelled the gym
# and they still took the money", "paid the deposit and its not showing on my account". The tail
# after the joining word is the whole test: a complaint word in it means the person is not
# reporting a job well done, whatever the first half said. Kept to the plain words so a report
# that ends in praise ("painted the fence and it looks brilliant") still gets the cheer.
TAIL_JOIN = re.compile(r"\b(?:and|then|but|so|because)\b")


TAIL_COMPLAINT = re.compile(
    r"\b(?:not|never|still|yet|again|cold|leaking|dripping|damp|mouldy|moldy|smelly|smells|"
    r"stinks|blocked|stuck|broken|broke|faulty|cracked|dirty|empty|flat|dead|late|slow|"
    r"missing|lost|wrong|worse|cancelled|canceled|refused)\b")


TAIL_ASK = re.compile(
    r"\b(?:what about|what next|what now|what else|how long|how much|how do i|how can i|how should i|"
    r"can i|could i|should i|shall i|do i|does it|will it|will they|is it|is that|are they|"
    r"was it|was that|where do i|when will|when do i|when should|who do i|any idea|any chance|"
    r"do you know|do you think|is there|are there)\b", re.I)


HARM_AFTER = re.compile(
    r"\b(?:my|his|her|their|the)\s+(?:\w+\s+)?(?:back|knee|knees|shoulder|shoulders|hip|hips|"
    r"ankle|ankles|foot|feet|leg|legs|arm|arms|wrist|hand|hands|chest|stomach|head|neck|"
    r"shin|calf|thigh|elbow|joint|joints|body)\b[^.!?]{0,14}?\bis (?:much |a lot |now )?"
    r"(?:worse|sore|stiff|swollen|aching|playing up)\b")


def _tail_complains(clean):
    """True when the clause after the joining word is a complaint, not a report.

    "sorted the boiler service and now the radiators are cold" is a person with cold radiators
    and the service is only how the line starts, so the tail is what they are telling the bot.
    The last word of the test is deliberately narrow: only the plain complaint words, so
    "painted the fence and it looks brilliant" keeps the cheer.
    """
    joins = list(TAIL_JOIN.finditer(clean))
    if not joins:
        return False
    return bool(TAIL_COMPLAINT.search(clean[joins[0].end():]))


# The verbs of going and doing need their object, because the verb alone is every day: "i went to
# the doctor", "i went home", "i did the washing up". The object names the thing done, so the
# object is what is in the list. "went to my first yoga class" has words between the preposition
# and the noun, hence the gap.
WENT_AT_IT = re.compile(
    r"\b(?:i|we)\s+(?:just\s+|also\s+|finally\s+|only\s+|actually\s+)?"
    r"(?:have\s+|had\s+|'ve\s+)?went\s+(?:"
    r"for\s+(?:a\s+|an\s+|my\s+|our\s+|the\s+)?(?:run|walk|swim|cycle|ride|hike|jog|"
    r"long\s+walk|length\s+swim|bike\s+ride|day\s+out)\b"
    r"|(?:swimming|running|cycling|walking|hiking|jogging|rambling|shopping)\b"
    r"|to\s+(?:\w+\s+){0,3}?(?:gym|pool|parkrun|class|classes|yoga|pilates|zumba|sauna|"
    r"climbing)\b"
    r")")


# "i did a workout", "i did yoga", "i did my exercises": the same afternoon with "did" in front.
DID_AT_IT = re.compile(
    r"\b(?:i|we)\s+(?:just\s+|also\s+|finally\s+|only\s+|actually\s+)?did\s+"
    r"(?:a\s+|an\s+|my\s+|our\s+|the\s+|some\s+|two\s+|three\s+)?"
    r"(?:workout|workouts?|run|session|class|swim|laps?|lengths?|weights|press[- ]?ups|"
    r"yoga|pilates|exercises?|exercise|stretches|set\s+of\s+\w+|\d+\s?k(?:m)?|km|miles?)\b")


# A job said as it is being done, with no time span: "im painting my kitchen", "we're tiling the
# bathroom", "im sorting out the garage". The person is telling you what their day is, and the
# neutral nod ("I'm listening - say more if it helps") answers that as if they had said nothing.
# The verb carries it, so "im going to the gym" and "im thinking of painting it" are not this: the
# first is a plan of its own and the second has not started.
FUTURE_TIME = re.compile(
    r"\b(?:today|tomorrow|tonight|later|next\s+(?:week|weekend|month|year|saturday|sunday|monday|"
    r"tuesday|wednesday|thursday|friday)|this\s+(?:weekend|week|evening|afternoon|morning)|"
    r"on\s+(?:saturday|sunday|monday|tuesday|wednesday|thursday|friday))\b")


AT_IT = re.compile(r"\b(?:i'm|im|i am|we're|we are)\s+(?:just\s+|currently\s+|still\s+|now\s+"
                   r"|in the middle of\s+)?(?:re)?([a-z]+ing)\b")


# A repeating thing is not a job under way: "i'm doing a yoga class every week" is a habit the
# memory store says back, and "how long have you got left?" is asked of a fence, not of a class
# that comes round again on Tuesday.
HABIT_TIME = re.compile(
    r"\b(?:every|each)\s+(?:day|week|month|year|morning|evening|weekend|night|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    r"|\b(?:once|twice|three times|four times|\d+ times)\s+a\s+(?:day|week|month|year)\b")


# Something wrong at the end of a job, or coming off it: the cheerful question is for an
# afternoon well spent and reads as deaf on one of these. The words are the ones people use for a
# job that is not going well, and they say nothing about a job that is ("im painting the hall and
# its going ok" keeps its question).
A_TROUBLE_IN_THE_TAIL = re.compile(
    r"\b(?:ran out|run out|run short|havent got|hasnt got|haven't got|hasn't got|so far behind|"
    r"stuck|nightmare|disaster|forever|taking ages|taking so long|drag(?:ging|ged) on|"
    r"junk|clutter|chaos|a mess|in a mess|messy|wont go|wont fit|doesnt fit|dont fit|"
    r"gone wrong|went wrong|broke|broken|snapped|hate it|hate this|give up|giving up|"
    r"struggling|too much for me|killing me|a pain|hard work|no idea what i)\b")


# How a body says a job has gone too far, in words that are not about the job at all: the fumes,
# the dizziness. A line with one of these in it is answered by the safety and trouble readers.
FEELING_OFF = re.compile(
    r"\b(?:dizzy|light-?headed|fumes|faint(?:ed|ing)?|bleeding|nauseous|throwing up|"
    r"cant breathe|can't breathe|blurred vision|heart racing)\b")


def _a_thing_after(rest):
    """True when the words after the verb name the thing the person is working on."""
    return any(word not in THING_AFTER and len(word) > 2
               for word in re.findall(r"[a-z']+", rest))


# The same afternoon said with the time span instead of the finished verb: "i spent the morning
# repainting the kitchen", "i've been sorting the photos all afternoon". The verb is still the
# thing that decides it, so "i spent the morning at the hospital" stays as it was.
SPENT_TIME = re.compile(r"\b(?:i|we)\s+spent\s+(?:the\s+|all\s+|most of the\s+|my\s+|our\s+)?"
                        r"(?:morning|afternoon|evening|day|weekend)\s+(?:re)?([a-z]+ing)\b")


BEEN_AT_IT = re.compile(r"\b(?:i|we)\s+(?:have\s+|had\s+|'ve\s+)?been\s+(?:re)?([a-z]+ing)\b")


TIME_SPAN = re.compile(r"\b(?:all (?:morning|afternoon|evening|day|weekend)|most of the "
                       r"(?:morning|afternoon|day|evening)|since (?:breakfast|lunch|this morning)|"
                       r"the (?:morning|afternoon|evening) away)\b")


def _done_ing():
    """The "-ing" forms of DONE_VERB, which is how the same afternoon is said with a time span."""
    out = set()
    for verb in DONE_VERB:
        stem = verb[:-2] if verb.endswith("ed") else verb
        out.add(stem + "ing")
        out.add(verb + "ing")
        if len(stem) > 2:
            out.add(stem + stem[-1] + "ing")
    out.update(("running", "swimming", "making", "writing", "cutting", "digging", "hanging",
                "building", "sweeping", "freezing", "sitting", "getting", "decorating",
                "repainting", "reorganising", "reorganizing"))
    return frozenset(out)


DONE_ING = _done_ing()


# Words that make the line a grumble rather than a thing done, so the question ("how did it go")
# would be the wrong shape for it.
# A cheerful question is for an afternoon well spent, not for harm. "i washed down two packets of
# pills" and "i chopped my finger" are a done verb with nothing in DONE_NOT_THIS to stop them, so
# the cheerful pool asked an overdose "are you pleased with it?". Nothing after a verb says it was
# harm, so the words that name harm stop the shape outright and the safety arm keeps the turn.
HARM_NAMED = re.compile(
    r"\b(?:pills?|tablets?|paracetamol|ibuprofen|painkillers?|meds|medication|overdosed?|"
    r"dose|wound|blood|bleeding|bled|bleach|ammonia|antifreeze|poison\w*)\b")


# A person who says they hurt themselves is never having a day that went neither way, and the
# cheerful day pool ("Good to hear. What was the best bit?") is the worst reply the bot could give
# it. `HARM_ON_ME` below needs a body part, so the ordinary case is caught by the safety band and
# the figurative one was not: "i cut myself from society" was congratulated, while its own sibling
# "i cut myself off from everyone" is answered by the friendship reading. Read by shape, so every
# wording of it stands the day question down - and "i cut myself a slice", "i cut myself some
# slack" give the person something rather than take it, so those are not this.
A_HURT_MYSELF = re.compile(
    r"\b(?:i|i've|ive)\b\s*(?:just\s+|almost\s+|nearly\s+|really\s+|actually\s+)?"
    r"(?:cut|cutting|hurt|hurting|harm|harmed|harming|burn|burned|burnt|burning|hit|hitting|"
    r"punish|punished|punishing|starve|starved|starving|poison|poisoned|poisoning)\s+myself\b"
    # "i cut myself a slice", "i cut myself some slack" hand the person something rather than take
    # it, so a quantity in front of the object means this is not that.
    r"(?!\s+(?:a|an|the|some|another|either|neither|one|two|three)\b)")


# The verb alone is not enough - "i chopped the onions", "i burnt the toast" are a supper - so a
# verb of harm only counts when the line says it landed on the person.
HARM_ON_ME = re.compile(
    r"\b(?:chopped|sliced|cut|stabbed|burned|burnt|scalded|slashed|gashed|split|hit|knocked|"
    # the same harm said while it is happening, which is how a person types it: "im cutting my
    # finger" was congratulated ("Nice one - nearly there, or still in the middle of it?") because
    # the -ing forms of these verbs are in DONE_ING and only the past tense was fenced.
    r"chopping|slicing|cutting|stabbing|burning|scalding|slashing|gashing)\b"
    r"[^.!?]{0,20}?\b(?:my|myself)\b[^.!?]{0,16}?"
    r"\b(?:finger|fingers|thumb|hand|hands|arm|arms|leg|legs|foot|feet|toe|toes|wrist|head|"
    r"eye|eyes|knee|face|shoulder|skin|chest|stomach)\b"
    r"|\bi\s+(?:chopped|sliced|cut|stabbed|burned|burnt|scalded|slashed|gashed)\s+myself\b")


KNOCK_ON_ME = re.compile(
    # "i hit my thumb with a hammer", "i dropped a tin on my foot"
    r"\bi\s+(?:just\s+|already\s+|then\s+|also\s+)?(?:hit|dropped|knocked|banged|stubbed|"
    r"trapped|caught|whacked|smashed|slammed|clonked|smacked|bashed|pinched|nipped|grazed|"
    r"scraped|trod|stood)\b[^.!?]{0,26}?\b(?:my|myself)\b[^.!?]{0,18}?"
    r"\b(?:" + KNOCKED_SPOTS + r")\b"
    # "i got my finger stuck in the drawer", "i got my hand caught in the door". Said the other
    # way round from the verb, so the first branch never saw it - and "stuck my finger" on its own
    # is left out on purpose, because "i stuck my foot in it" and "i stuck my neck out" are not
    # knocks on either.
    r"|\bi\s+(?:got|had)\s+(?:my|a)\s+(?:" + KNOCKED_SPOTS + r")\s+"
    r"(?:stuck|caught|trapped|nipped|slammed|squashed|crushed)\b"
    # "i shut my finger in the door", "i slammed my hand in the drawer"
    r"|\bi\s+(?:shut|slammed|squashed|crushed)\s+my\s+(?:" + KNOCKED_SPOTS + r")\s+in\b")


# A whole day on your feet is not a knock on them, and a line about the coming days is a plan
# ("i'll be on my feet all day"), so a span of time in the line stands the pool down.
A_SPAN_OF_TIME = re.compile(
    r"\b(?:all\s+(?:day|morning|afternoon|evening|week)|for\s+(?:hours|a\s+while|days)|"
    r"hours|again|every\s+day|tomorrow|next\s+week)\b")


def _a_knock_on_oneself(clean):
    """True for a knock the person did to their own body, with nothing else in the line."""
    if not clean or "?" in clean or " but " in clean:
        return False
    if not KNOCK_ON_ME.search(clean):
        return False
    return not A_SPAN_OF_TIME.search(clean)


# The same knock with no part of the body named in it - "i walked into a door frame", "i walked
# straight into a table", "i ran into the gate" - is the shape the thing-done scan reads as a walk
# ("walked" is a verb of going), so the person got "What made you start on that?", a question
# about a job they had begun, for walking into a door. There is no spot to put ice on, so these
# get the reaction and a question back, and nothing about a task. The verbs are the ones a person
# travels on their own feet: "i drove into a wall" is a car into a wall and may be somebody hurt
# in it, and "does it hurt to put weight on it" is not the reading for that.
WALKED_INTO = re.compile(
    r"\bi\s+(?:just\s+|then\s+)?(?:walked|ran|stepped|bumped|crashed)\s+"
    r"(?:straight\s+|smack\s+|right\s+|bang\s+|head\s+)?(?:into|against|over)\s+"
    r"(?:a|the|my|our)\s+(?:door|doorway|door\s?frame|frame|table|chair|bed|cot|cupboard|wall|"
    r"shelf|shelves|desk|fridge|freezer|sofa|gate|fence|cabinet|worktop|dresser|sideboard|"
    r"stairs|stair|banister|post|beam|radiator|window)\b")


def _a_knock_into_a_thing(clean):
    """True for walking or bumping into a piece of furniture, with no body part named."""
    if not clean or "?" in clean or " but " in clean:
        return False
    return bool(WALKED_INTO.search(clean))


# A body word or a harm word anywhere makes the line the careful reading's: "washed the cut with
# soap" is a care line and not a thing done, and "mowed the lawn and now my back hurts" is the
# back. Read off the whole line rather than off the verb, because the verb forms this shape reads
# are past tenses, and a past tense in front of a hurt is the story of the hurt.
HARM_ANYWHERE = re.compile(
    r"\b(?:back|backs|knee|knees|shoulder|shoulders|hip|hips|ankle|ankles|foot|feet|leg|legs|"
    r"arm|arms|wrist|wrists|hand|hands|chest|stomach|head|neck|thigh|elbow|elbows|joint|joints|"
    r"skin|cut|cuts|wound|wounds|burn|burns|burnt|scab|scabs|graze|grazes|bruise|bruises|"
    r"blister|blisters|blood|bleeding|bled|pain|pains|ache|aches|aching|hurts?|hurting|"
    r"throbbing|swollen|swelling)\b")


# A mishap: something that landed on a person, said as the account of a day rather than as a
# question. None of these lines has a harm word in it and most name no body part, so neither
# HARM_NAMED nor HARM_ANYWHERE sees them, and the composer's pleasantry took the turn: "i stepped
# on a nail in the garden" was asked what the best bit of it was, "i got glass in my foot" was told
# "nice one", "my baby rolled off the bed" got "how did the rest of it go", and "my vision has gone
# in my left eye" was told "sounds alright, anything good in it?". The cheer is the worst reply in
# the file on those turns, so the reading has two jobs: keep the day question off them, and ask the
# one question a friend asks - how bad it is.
#
# Who fell is a person, so the fall has to have one in front of it: "the shelf fell down", "my
# phone fell in the sink" and "the fence blew over" are things going wrong in a house, and the
# repair pools answer those. The names are the ones the whole file uses for the people a line can
# be about, so a new relation word is added in one place.
FALLEN_PEOPLE = (
    r"i|we|he|she|they|the\s+(?:baby|child|kid|boy|girl|little\s+one|toddler|old\s+lady|old\s+man)|"
    r"(?:my|our|his|her|their)\s+(?:mum|mom|mam|dad|father|mother|son|daughter|child|kid|boy|girl|"
    r"baby|toddler|husband|wife|partner|boyfriend|girlfriend|brother|sister|nan|nana|gran|granny|"
    r"grandad|grandpa|grandma|grandmother|grandfather|cousin|friend|mate|neighbour|neighbor|"
    r"uncle|aunt|nephew|niece|little\s+one|lad|lass)"
    # "my 6 month old fell", "the 18 month old rolled off the sofa": an age in place of a
    # name, which is how a parent types it
    r"|(?:my|our|his|her|their|the)\s+\d+\s*(?:month|week|year)s?\s*old")


# The fall itself needs somewhere to land, which is also what keeps the idioms out without
# listing them: "fell asleep", "fell out with her", "fell in love" and "fell behind at work" have
# no surface after the verb.
MISHAP_FELL = re.compile(
    r"\b(?:" + FALLEN_PEOPLE + r")\b[^.?!]{0,24}?\b(?:fell|rolled|tumbled|toppled|tripped|"
    r"slipped|went|come|came)\s+(?:(?:right|straight|back|clean|smack|flat|head)\s+)?"
    # (a fall has a surface, and it comes straight after the verb: "we fell owt over money" is
    # the dialect for "fell out over money" and must not be read as a fall)
    r"(?:over|off|down|from|onto|into|through|out\s+of|on\s+the|down\s+the|off\s+the)\b"
    # "i fell on the stairs", "fell on the ice": the surface named is a floor rather than a piece
    # of furniture, because "i fell asleep on the sofa" and "fell in the bath" (asleep again) name
    # the same prepositions and are the day, not the mishap.
    r"|\b(?:" + FALLEN_PEOPLE + r")\b[^.?!]{0,24}?\b(?:fell|rolled|tumbled|tripped|slipped|"
    r"went)\s+on\s+the\s+(?:stairs|stair|steps|ice|pavement|paving|kerb|curb|path|floor|"
    r"ground|road|decking|tiles|lino|linoleum|concrete|gravel|deck)\b"
    r"|\b(?:" + FALLEN_PEOPLE + r")\b[^.?!]{0,18}?\bhad\s+a\s+(?:bad\s+|nasty\s+|really\s+)?"
    r"(?:fall|tumble|trip)\b"
    # "my 6 month old fell", "she fell" with nothing after the verb: a fall with no surface named
    # is still a fall when the line ends there, and the idioms all carry a word after the verb
    # ("fell out with", "fell in love", "fell behind", "fell through") or a place to sleep ("fell
    # asleep", "fell over laughing").
    r"|\b(?:" + FALLEN_PEOPLE + r")\b[^.?!]{0,18}?\bfell\b(?=\s*(?:[.,!]|$|and\b|but\b))")
