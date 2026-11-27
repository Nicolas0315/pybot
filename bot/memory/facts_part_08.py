"""Part 8 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re

from ..understanding import lexicon, normalize
from ..understanding.kinds import EMOTION_WORDS
from ..understanding.topics import WORD_NUMBERS

from .facts_part_01 import (
    NOT_A_NAME_THING, NOT_A_NAME_TRAIT, ANNOUNCED_NAME_PATTERNS, CLAUSE_SPLIT, GOES_BY_NAME,
    GUESSED_NAME_PATTERNS, DIET_WORDS, GO_BY_WAYS, NAMES_THAT_LOOK_LIKE_STATES, NOT_A_NAME_LAUGH,
    NOT_A_NAME_STATE, NOT_NAMES, NOT_NAMES_EXTRA, NUMBER_WORDS, SOBER_WORDS, JOB_WORDS, CLAUSE_EDGE,
    DIET_FREE_WORDS, DIET_NAMES, DAYS, MONTHS, NOT_A_PET_NAME,
)
from .facts_part_02 import (
    _names_something_else, PREPOSITIONS, PARTICLES, PERSON_OPEN, POINTING, DAY_AND_MONTH,
    MONTH_NAMES,
)
from .facts_part_03 import (
    PAST_STATES, ARTICLES, ASKED_BEFORE, ASKING, FUTURE, CORRECTION_TAKEBACK, NEGATED,
    SECOND_PERSON, CORRECTION_LEAD, OWN, PAST, a_deed,
)
from .facts_part_04 import (
    _finish, SAYS_A_NAME, _a_judgement_on_themselves, _a_state_written_as_a_comparison_or_a_double,
    _followers_fit, _lowercase_name_fits, _sounds_like_a_state, ROLE_ENDING, _tidy,
)
from .facts_part_06 import (
    PREGNANCY_STATES, NAMES_THAT_END_LIKE_A_VERB,
)
from .facts_part_07 import (
    bare_name, _pets, DESCRIBING_ENDS, DESCRIBING_WORDS, ED_NAMES, NOT_A_NAME_WORD, _not_a_name,
    is_a_contraction, COMMON_WORDS, NOT_A_NAME_ENDINGS, subject,
)


def reads_as_a_name(word):
    """Whether a word on its own, in answer to a name question, is what a person is called.

    The rules that read "im Jess" decide it, so a word that says how something is ("its cold",
    "this is tired") never becomes a name. Returns the name in its spelled form, or None.
    """
    if not bare_name(word):
        return None
    low = _finish(str(word or ""))
    if not low or low in NOT_A_NAME_THING or low in NOT_A_NAME_TRAIT \
            or _names_something_else(low):
        return None
    name = _name("im " + low)
    if name and _finish(name) == low:
        return name
    return None


def _name(text):
    # One line can give two names at once: "my names tom but i go by tommy" says the one that is
    # on the paperwork and then the one they answer to, and the second is the name. Read as the
    # first alone it told a person called Tomas that their name was Tom, so the go-by reading
    # stands in front of the announced one when the line holds both. A go-by said by itself is
    # still read in the pass below, unchanged.
    went_by = _name_from(GOES_BY_NAME, text, guessed=True)
    if not went_by and GOES_BY_NAME.search(text):
        # The go-by can keep a clause of its own: "my names tom but i go by tommy". Read over the
        # whole line the frame is not the first thing in it - a name statement comes first, and a
        # name is not filler - so the reading is made again on its own clause.
        for clause in CLAUSE_SPLIT.split(text):
            if not GOES_BY_NAME.search(clause):
                continue
            went_by = _name_from(GOES_BY_NAME, clause, guessed=True)
            if went_by:
                break
    for pattern in ANNOUNCED_NAME_PATTERNS:
        name = _name_from(pattern, text, guessed=False)
        if name:
            if went_by and went_by.lower() != name.lower():
                return went_by
            return name
    for pattern in GUESSED_NAME_PATTERNS:
        name = _name_from(pattern, text, guessed=True)
        if name:
            return name
    return None


def _name_from(pattern, text, guessed):
    """The first word this pattern offers that could be a name, or None."""
    for match in pattern.finditer(text):
        word = match.group(1)
        low = _finish(word)
        if (low in NOT_NAMES or low in NOT_NAMES_EXTRA or low in GO_BY_WAYS
                or low in DIET_WORDS or low in SOBER_WORDS
                or low in lexicon.JOINED_WORDS or len(low) < 2):
            continue  # "im sickof my brother" is "sick of", two words, not somebody Sickof
        if not word[:1].isupper() and (low in NOT_A_NAME_STATE or _a_judgement_on_themselves(low)
                                       or low in NOT_A_NAME_LAUGH or lexicon.is_a_laugh(low)):
            # "my name is quiet" is the same refusal as "im quiet": a describing word is what
            # the person is like however they introduce it, and one session calling them
            # Quiet is worse than not having a name for them. A name that only looks like a
            # state is kept by NAMES_THAT_LOOK_LIKE_STATES below.
            continue  # "im mad" is how they are, not what they are called
        spelled = normalize.spelled(low)
        # A curated spelling of how they are is how they are, however many letters it drops:
        # "im hungrey" is "im hungry" and not somebody called Hungrey. Only the tables speak
        # here; the fixer's guesses stay under the length guard below, because a cut is not
        # evidence.
        if low not in NAMES_THAT_LOOK_LIKE_STATES and any(
                one in NOT_NAMES or one in NOT_NAMES_EXTRA or one in NOT_A_NAME_STATE
                for one in spelled if one != low):
            continue
        if low in NUMBER_WORDS:
            continue  # "im forty" is an age, and nobody is called Forty
        repaired = normalize.repaired_tokens(low)
        # Only a repair that says more than the word did: "gd" is "good", "gud" is "good".
        # A cut is not evidence ("ann" collapses to "an" and is a name), so a shorter reading
        # never talks anybody out of a name.
        if low not in NAMES_THAT_LOOK_LIKE_STATES and any(
                one in NOT_NAMES or one in NOT_NAMES_EXTRA or one in NOT_A_NAME_STATE
                for one in repaired if one != low and len(one) >= len(low)):
            # A chat spelling of how they are is still how they are: "im gd" is "im good", and
            # "im gud" was answered "Nice to meet you, Gud", with the name kept for the chat.
            continue
        if guessed and low not in NAMES_THAT_LOOK_LIKE_STATES and _describes_them(low):
            # The list the store already keeps for "my mum is messy" answers the guessed
            # introduction too, and it answers it with the one test rather than a second list.
            # "im noisy", "im stubborn", "im overweight" and "im tall" are how somebody is, and
            # each was answered "Nice to meet you, Noisy" - or "Overweight" in the deck chat
            # `dq-aug5-06` - and then said back for the rest of the chat. The words that say how
            # a person is are one list (`DESCRIBING_WORDS`), asked by this reader and by the
            # relation reader, so a word added for "my sister is chatty" is refused here as well
            # and the two cannot drift apart. A line that says outright it is giving a name is
            # giving one, the same exception every other reading has, and the names that only
            # look like states (Ahmed, Jared, Mohamed, all "-ed") are kept by the list above.
            continue
        if guessed and low not in NAMES_THAT_LOOK_LIKE_STATES and any(
                one != low and len(one) >= len(low) and _sounds_like_a_state(one)
                for one in repaired):
            # A state typed the way people say it is still a state: "im coughin" is coughing and
            # "im burnin" is burning, and the endings test below cannot see either, because the
            # ending is the part the typing dropped. The repair is the one the reading already
            # makes (`plain` reads "im coughing"), and it can only take a name off a word that is
            # nothing but a state once its last letter is back, so no name loses out: none of the
            # 649 common names repairs to a word with a state's ending. Only the guessed reading
            # ("im ...") is read this way: a line that says it is giving a name is giving one, and
            # "my brother is called crispin" stays a Crispin rather than becoming a crisping.
            continue
        if _a_state_written_as_a_comparison_or_a_double(low) and not SAYS_A_NAME.search(text):
            # A feeling typed with a letter wrong is still how they are, not what they are
            # called: "im knackerd", "im tierd", "im worrid" were all answered "Nice to meet
            # you, ..." because the endings test cannot see a slip. Capitals do not help:
            # "Im Knackerd", "Im Tierd" and "IM SHATTERD" are the same slip, and no name
            # people are given lowers to a feeling word. The one exception is the line that
            # says outright it is giving a name, the same way the sound reading below has it:
            # "my name is board" introduces somebody called Board, and no feeling table should
            # take the name off them.
            continue
        if normalize.reads_as_a_sound(low) and not SAYS_A_NAME.search(text):
            # "im board" is bored, and nobody is called that. A line that says outright that it
            # is giving a name keeps it however the word sounds: "my name is board" is a name.
            continue
        if not word[:1].isupper():
            if _sounds_like_a_state(low) and not SAYS_A_NAME.search(text):
                # The third place the sound of a word stands a name down, and the only one that
                # had no exception for a line that says outright it is naming: "my name is
                # happier" says nothing at all, because a comparison now reads as a state
                # (bot/modules/... the -er table) and the sound test answers True for it.
                continue  # "im knackered", "im coeliac", "im welsh"
            if guessed and (not _lowercase_name_fits(text, match)
                            or not _followers_fit(text, match.end(1), word)):
                continue
        return word[0].upper() + word[1:]
    return None


def _was_names_a_role(phrase, article=None):
    """Whether a phrase said after "i was" names what they did, not how they were.

    "i was a nurse" and "i was head chef at the pub" are roles. "we were flat out", "i was eight
    weeks pregnant" and "i was born in leeds" are a state, a length and a birth, and read as roles
    they came back late in a chat as "You were a flat out". What a role is said with is an article
    in front of it ("a nurse", "an electrician"), or a word the job lexicon knows ("head chef",
    "student"), or an ending only a role has ("a plumber", "a barrister"). A participle is a verb
    ("i was managing a shop") and a state word is how they were ("flat out", "retired"), so
    neither is a role however noun-like the line looks.
    """
    low = [word.lower().strip(".,!?;:") for word in str(phrase or "").split() if word.strip()]
    while low and low[0] in ("both", "all", "just", "only", "still", "now", "then", "also"):
        low.pop(0)  # "we were both nurses" is the same role said with a word in front of it
    low = low[:3]
    if article and low:
        return True
    if not low:
        return False
    if any(len(word) > 4 and word.endswith(("ing", "ed")) for word in low):
        return False
    head = low[-1]
    if head in STATE_WORDS or head in PAST_STATES or head in PREGNANCY_STATES:
        return False
    # The lexicon is written in the singular and people say the plural: "we were both nurses".
    single = [word[:-1] if word.endswith("s") and word not in JOB_WORDS else word for word in low]
    if any(word in JOB_WORDS for word in low + single):
        return True
    return len(head) > 4 and head.endswith(ROLE_ENDING)


def _the_clause_before(text, start, edges=4):
    """The clause before the fact at `start`, with the clause it continues put back.

    A list drops the subject: "my brother has a son and a daughter" is one clause with two
    relations in it, and read on its own the second one looks like the person's own. So the
    clause is read back to the nearest one that opens with a subject - "and i have a son" is
    its own clause and stops the walk.
    """
    parts, last = [], 0
    head = text[:start]
    for edge in CLAUSE_EDGE.finditer(head):
        parts.append(head[last:edge.end()])
        last = edge.end()
    parts.append(head[last:])
    said, walked = parts[-1], 0
    # The walk stops at the first part as well as at a subject: `parts[-1 - walked]` was read
    # one part too far back on a line whose only edge left a clause that opens with no subject -
    # "and for my dad", "and some for my sister" - and the reader raised IndexError instead of
    # reading the line, so the relation the follow-up named was never filed and every reader of
    # the line died with it: nothing was proposed at all and the person got "Hello!" back.
    while (walked + 1 < len(parts) and walked < edges
           and not _opens_a_subject(parts[-1 - walked])):
        walked += 1
        said = parts[-1 - walked] + said
    return said


def _opens_a_subject(clause):
    """Whether this clause starts by naming who it is about."""
    words = str(clause or "").replace(",", " ").split()
    if not words:
        return False
    return re.sub(r"[^a-z']", "", words[0].lower()) in ANY_SUBJECT


def pet_counts(text):
    """The animals a corrected line counts: "3 cats", "two dogs" -> [{"animal", "count"}].

    Read through the same pet reader, so "sorry, 3 cats" counts the cat the person already told
    us about rather than making a second one.
    """
    found = _pets("i have " + str(text or ""))
    return [{"animal": pet["animal"], "count": pet["count"]}
            for pet in found if pet.get("count")]


def _describes_them(word):
    """Whether a word says how somebody is rather than what they are called."""
    low = str(word or "").lower()
    if not low:
        return False
    if low in STATE_WORDS or low in DESCRIBING_WORDS or low in lexicon.A_STATE:
        return True
    if low in DIET_WORDS or low in DIET_NAMES or low in DIET_FREE_WORDS or low in SOBER_WORDS:
        # "my mum is dairy free" and "my veggie sister" say what she eats, so the word is not her
        # name: read as one, the store told the person their mum was called Dairy.
        return True
    if low in ED_NAMES:
        return False
    if low.endswith("ed") and len(low) > 3:
        return True
    return any(low.endswith(end) and len(low) > len(end) + 2 for end in DESCRIBING_ENDS)


def _bare_name(word, pair=False):
    """The name a line gives without the naming verb, or "" when the word is something else.

    "my mum is sue" names the mum; "my mum is tired" and "my brother is older" say how they are,
    and filing "Tired" as a name would be worse than holding nothing at all. The test is the
    bot's own word list: a word it already knows is the word it is, and a word it does not know
    - or one typed with a capital, the way a name is written - is the person's name. Tom, Rose
    and Sam are ordinary words as well as names, so those are read only from a capital.

    `pair` is for a line that gives two of them at once - "my mum and dad are dave and sue", "my
    kids are ada 7 and sam 4". Two names side by side is the line's own sign that the words are
    names, so a word the lexicon knows is taken as one there.
    """
    said = str(word or "").strip().strip(".,!?;:'\"")
    low = said.lower()
    if not re.fullmatch(r"[a-z][a-z'-]{1,19}", low):
        return ""
    if _not_a_name(said, strict_ly=False):
        return ""
    if low in WORD_NUMBERS:
        # "my son is seven" is an age written out, and Seven is nobody's name.
        return ""
    if low in NOT_A_NAME_WORD:
        # "my daughters name" is a question with the verb left off, not a person called Name.
        return ""
    if is_a_contraction(low):
        return ""
    if low in lexicon.COMMON_NAMES or low in NAMES_THAT_END_LIKE_A_VERB:
        # A name typed in lower case is still a name. "my husband is tom" filed the husband with
        # no name - though the bot had just said "Noted: your husband is tom." - so the next ask,
        # "whats my husbands name", answered "You haven't told me your husband's name." People
        # type the name the way they type everything else; the reading already knows these words
        # are names (the same list that keeps "hi im lisa" an introduction), so the capital is
        # not needed to tell them from a state. A word that only says how somebody is ("tired",
        # "late", "asleep") is not on that list and is turned down below, as before.
        return _tidy(_finish(said))
    if not said[:1].isupper() and _describes_them(low):
        # A capital is how a name is written, so "my mum is Sue" is her name whatever else the
        # word means; without one, a word that says how somebody is says nothing about a name.
        return ""
    if not pair and low in normalize.LEXICON and not said[:1].isupper():
        return ""
    return _tidy(_finish(said))


def a_name_could_be(word):
    """Whether a single word could be somebody's name, with nothing else in the line to say so.

    People put a name right with the name and no other words: "no its dave", "i meant dave",
    "sorry, dave". Nothing in the line says the word is a name, so the word itself has to hold
    up: one word, not a word the bot reads as language ("fine", "tired", "complicated",
    "plumber"), and not a month or a day. A word kept as a first name wins even when it is an
    ordinary word as well ("grace", "hope", "rob"), because that is what those names are.
    """
    low = str(word or "").strip().lower()
    if not re.fullmatch(r"[a-z][a-z'-]{1,19}", low):
        return False
    if low in MONTHS or low in DAYS:
        return False
    if low in lexicon.COMMON_NAMES:
        return True
    if low in NOT_A_PET_NAME or low in NOT_NAMES or low in NOT_NAMES_EXTRA:
        return False
    if low in STATE_WORDS or low in DESCRIBING_WORDS:
        return False  # "its fine", "its complicated", "its rubbish": a word said of the person
    if low not in COMMON_WORDS and low.endswith(NOT_A_NAME_ENDINGS):
        # A describing word that the word lists happen to miss still wears a describing word's
        # ending ("complicated", "amazing", "real"), and names rarely do. Names that do - Lily,
        # Molly, Kelly, Teddy - are in the list of first names, which is read before this.
        return False
    return low not in COMMON_WORDS


def _object_words(rest):
    """The words of a plan's object, once the preposition and the article are out of the way."""
    words = [w for w in re.findall(r"[a-z']+", str(rest or "").lower()) if w not in ARTICLES]
    return [w for w in words if w not in PREPOSITIONS] if words else []


def _object_plan(rest):
    """Whether the rest of a plan is one the verb has to carry.

    Two things say the verb belongs in the plan. The rest opens with a preposition, so on its own
    it says only what the verb is about: "for a bike" is what the money is for, and "You're
    planning to for a bike" is not a sentence. Or the verb took a particle of its own ("writing
    up", "saving up"), which leaves the object needing its verb to mean anything."""
    if not rest:
        return False
    first = re.sub(r"[^a-z]", "", rest.split()[0].lower())
    return first in PREPOSITIONS


def _plan_verb(match, rest):
    """The verb the plan pattern stopped after, when the plan is that verb and its object.

    "i'm saving up for a bike" keeps "saving up": "for a bike" on its own is what the money is
    for, not what they are doing. A plan with a thing straight after the verb ("i'm buying a
    bike") needs no verb, because the thing is the plan."""
    verb = PERSON_OPEN.sub("", match.group(0), count=1).strip(" .")
    words = verb.split()
    if not words or not words[0].lower().endswith("ing"):
        return ""
    if _object_plan(rest) or words[-1].lower() in PARTICLES:
        return verb[:1].upper() + verb[1:]
    return ""


def _a_plan_has_a_thing(rest):
    """Whether the object of the verb names something, rather than pointing at it.

    "saving up for a bike" names the bike; "saving up for it" and "saving up for the one i saw"
    name nothing, so there is no plan to keep and no plan to say back."""
    if not _object_plan(rest):
        return True
    words = _object_words(rest)
    return bool(words) and words[0] not in POINTING


# A question uses the words a plan does: "what do we need to pack?", "how much do i need to save?",
# "do i need to book?". The frame a plan is written with ("i need to", "im going to") is the
# person's own doing only when the clause that carries it is theirs, so a frame that opens its
# clause with an asking word names nothing, and neither does one a wrapper asks the plan for.
PLAN_CLAUSE_BREAK = re.compile(r"[.!?,;:]|\s+(?:and|but|so|then|or)\s+", re.I)


# The words people put in front of a question, which do not make it a statement: "and what do we
# need to take?" asks just as "what do we need to take?" does.
PLAN_CLAUSE_OPENER = re.compile(r"^(?:(?:and|but|so|then|or|ok|okay|also|well|oh|plus|now)\b[ ,]*)*",
                                re.I)


def _asks_about_the_plan(text, at):
    """Whether the plan frame at `at` sits in a question rather than in a statement.

    Two ways it does. A wrapper asks for the plan before naming the frame ("remind me what im
    saving for" was kept as "For" and said back as "You're saving for"), which ASKED_BEFORE
    reads. Or the clause the frame is in opens with an asking word, which is how the rest of the
    asks are worded: "how much do i need to save?" left "Save?", "do i need to book?" left
    "Book?", and "what am i planning?" said "You're planning to save." either way."""
    before = text[:at]
    if ASKED_BEFORE.search(before):
        return True
    clause = PLAN_CLAUSE_BREAK.split(before)[-1]
    clause = PLAN_CLAUSE_OPENER.sub("", clause.strip()).strip()
    return bool(clause) and bool(ASKING.match(clause))


def _plan_text(text, start):
    """The plan itself: from the verb the pattern stopped after, to the end of its clause.

    "I want to save 480 pounds in 6 months, how much should I put away" states the plan and then
    asks a question about it: the plan is the part before the comma, and the rest is the ask.
    """
    rest = text[start:].strip(" ,;:-")
    rest = re.split(r"(?<=[.!?])\s|\s+(?:but|and then|so)\s+", rest, 1)[0].strip(" ,;:-")
    rest = re.split(r",\s+(?:(?:how|what|which|where|when|who|why|should|can|could|would|do|does|"
                    r"is|are|will|any|and)\b)", rest, 1)[0].strip(" ,;:-")
    if not rest:
        return ""
    return rest[0].upper() + rest[1:] if rest else ""


# How the person is, rather than what they are doing. A feeling with a date on it - "im really
# low this week", "i feel awful this week", "im feeling better this week" - is not something
# coming up: the store kept it as a plan, read it back as "Noted: you're really low this week",
# and answered "what are my plans?" with how they felt. The words that can fill the clause
# after the copula are the state adjectives this file already lists, so "im on holiday next
# week" and "im at the dentist on monday" are untouched: a holiday and a dentist are not states.
COPULA = re.compile(
    r"^\W{0,2}(?:i(?:'m| am)|im|i\s+feel|i\s+felt|i(?:'ve| have)\s+been|we(?:'re| are)|were|"
    r"we\s+feel)\s+(?P<rest>.+)$", re.I)


# The words that sit between the copula and the state ("im feeling really low"), and the date,
# which is not part of what they are.
STATE_FILLER = frozenset("""really so very quite pretty rather too still just feeling feel felt
been absolutely completely totally a bit kind of sort of kind sort getting more less somewhat
this that week weekend morning evening afternoon night today tomorrow month year""".split())


# Particles and adverbs that look like a state ("im back", "im online", "im off", "im late") and
# are not: a line about where they are is about something coming up once it carries a date.
STATE_PARTICLE = frozenset("""up down in on at out off away back home here there over around
from with for by of to near into than as after upstairs downstairs online offline asleep awake
outside inside late early soon nearly almost definitely probably maybe honestly seriously
literally actually totally completely absolutely half mid bloody""".split())


# A feeling said plainly that the lists do not carry on their own.
STATE_MORE = frozenset("""low flat blue rough rubbish manky wiped better worse ill sick
                             unwell poorly""".split())


STATE_WORDS = frozenset(
    word for word in (NOT_NAMES_EXTRA | STATE_MORE |
                      frozenset(word for cues in EMOTION_WORDS.values()
                                for cue in cues for word in cue.split()))
    if word not in STATE_PARTICLE)


# "off sick" is an absence, not a mood: "im off sick next week" is a week they are not at work,
# and the store has to keep it as something coming up (happy-linden, #1869: the state reading
# dropped that plan). A word said about being off work is doing, not being.
OFF_ABSENCE = re.compile(r"\boff (?:sick|work|school|college|uni|university|shift|shifts|rota)\b",
                         re.I)


# ...when the absence is still to come ("im off sick next week", "im off work tomorrow"). "im off
# sick this week" is where they are now, so it stays a state and is not filed as something ahead.
OFF_AHEAD = re.compile(r"\bnext\b|\btomorrow\b|\bon\s+(?:mon|tues|wednes|thurs|fri|satur|sun)day"
                       r"|\bin\s+(?:january|february|march|april|may|june|july|august|september"
                       r"|october|november|december)\b", re.I)


def _how_they_are(clause):
    """True when the clause only says how the person is, so a date on it is not a plan."""
    match = COPULA.match(clause)
    if not match:
        return False
    if OFF_ABSENCE.search(match.group("rest")) and OFF_AHEAD.search(clause):
        return False  # "im off sick next week" is a week at home still to come, not a mood
    rest = " " + match.group("rest").lower() + " "
    rest = re.sub(r"[^a-z' ]", " ", FUTURE.sub(" ", rest))
    words = [word for word in rest.split() if word not in STATE_FILLER]
    words = [word for word in words if word not in STATE_PARTICLE]
    return bool(words) and all(word in STATE_WORDS for word in words)


# The same test for a thing of theirs rather than for them: "my budget is tight this month" and
# "my back has been bad this month" are how things are, and the date on them is when it has been
# like that, not something coming up. Read as a plan, the whole line came back at them as what
# they are doing ("You're planning to my budget is tight this month"), and it took the place of
# the plan they had actually told us: "my budget is tight this month" after "a holiday in spain"
# left the holiday out of `user["plan"]`. The thing, the copula and a state, in that order, is the
# shape; a date or a place after the copula ("my holiday is in august", "the car is in the garage
# on friday") is still a plan, and a doing ("my course starts in september") never gets here.
THING_COPULA = re.compile(
    r"^\W{0,2}(?:my|our|the)\s+[a-z'\u2019\-]+(?:\s+[a-z'\u2019\-]+)?\s+"
    r"(?:is|are|was|were|has been|have been|had been|feels?|felt|seems?|seemed|looks?|looked|"
    r"gets?|got|remains?)\s+(?P<rest>.+)$", re.I)


# A thing of theirs with a date on it is a state only when the predicate says how the thing is
# *today*. A predicate that names something still to come is an event with a date on it, and the
# plan store has to keep it: "my essay is due on friday", "my pay rise is due in april", "my rent
# is going up in may" all name a day, and reading them as states emptied the store (lime-frame,
# #8159: "what am i planning" answered "You haven't told me about anything coming up yet" after
# all three). Same in the other direction for how a thing is now: "broken", "leaking", "playing
# up" were not in the state words, so "my car is broken this month" was filed as a plan.
AHEAD_OF_THE_THING = re.compile(
    r"\b(?:due|booked|scheduled|expected|coming|starting|beginning|renewal|renewed|renewing|"
    r"up\s+for|going\s+up|out\s+on|in\s+for|on\s+order|happening)\b", re.I)


# How a thing of theirs is today. Kept apart from the state words the *person* is read with: a
# broken boiler says nothing about how they are, and "im flat out" is not this reader's business.
THING_TODAY = frozenset("""
    broken bust bursting cracked leaking leaky dripping damp mouldy mouldering rusty
    clogged blocked jammed faulty dead knackered noisy slow patchy scratched chipped wonky
    playing playing-up playin sticking wobbling rattling screeching smoking
    """.replace("playing-up", "playing up").split())


def _how_their_things_are(clause):
    """True when the clause only says how a thing of theirs is, so a date on it is not a plan."""
    match = THING_COPULA.match(clause)
    if not match:
        return False
    raw = match.group("rest").lower()
    if AHEAD_OF_THE_THING.search(raw):
        return False
    rest = " " + raw + " "
    rest = re.sub(r"[^a-z' ]", " ", FUTURE.sub(" ", rest))
    words = [word for word in rest.split() if word not in STATE_FILLER]
    words = [word for word in words if word not in STATE_PARTICLE]
    return bool(words) and all(word in STATE_WORDS or word in THING_TODAY for word in words)


# A thing with a clock on it and no verb: "dentist at 3 on tuesday", "train at 7.15", "lunch
# with sam at 1 on friday", "haircut saturday at 10". This is how people name an appointment;
# every other plan reader here wants a subject ("i'm meeting sam at 6") or a future word
# ("my holiday is in august"), so these lines were read as nothing at all: "dentist at 3 on
# tuesday" got "I'm listening - say more if it helps", and "what time is my dentist" and
# "what time is the train" got a hedge, though the clock was in the line.
#
# The thing, its clock and its day are the arrangement. What keeps a line out is a subject of
# their own (the plan reader has it), a question, a pronoun for the thing ("it's at 3"), and
# anything past ("yesterday", "was", "had").
APPOINTMENT_CLOCK = re.compile(
    r"\b(?:at|around|about|for|by)\s+((?:1[0-2]|0?[1-9])(?:[:.][0-5]\d)?\s*(?:am|pm)?|noon|midday|"
    r"midnight|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b", re.I)


APPOINTMENT_DAY = re.compile(
    r"\b(?:(?:on|this|next)\s+)?(?:mon|tues|wednes|thurs|fri|satur|sun)day\b|\b(?:today|tomorrow|"
    r"tonight|this (?:morning|afternoon|evening))\b|\b(?:(?:on|by)\s+)?" + DAY_AND_MONTH +
    r"\b", re.I)


APPOINTMENT_PAST = re.compile(
    r"\b(?:yesterday|was|were|went|had|did|last (?:night|week|monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday)|ago|already)\b", re.I)


# The thing an appointment is about: a noun or two, never a pronoun standing in for something
# else and never a question word.
# "i start my new job on monday" is the plan reader's line; "my train at 7.15" has no subject in
# front of it, only a thing, and the plan reader does nothing with it.
APPOINTMENT_OWN_SUBJECT = re.compile(
    r"^(?:ok(?:ay)?[, ]+|and |so |but |also |well |oh )*"
    r"(?:i|i'm|im|i've|i'd|id|we|we're|were|we've|weve|we'd)\b", re.I)


# The words that take the last thing back name nothing, so they are never the thing a day is said
# about: "scratch that, saturday" after "im flying to dublin on friday" kept the plan "scratch that
# on saturday", and the store answered "Your scratch that is on Saturday" and moved no date. "make
# that" is the same family - it corrects the line before, it does not begin a plan of its own.
TAKE_BACK_WORDS = re.compile(CORRECTION_TAKEBACK + r"|mak(?:e|ing)\s+(?:that|it)", re.I)


# "anything", "something", "nothing", "everything" and "whatever" are the words a person uses
# when they have not named a thing yet: "anything on tonight" asks what there is, and it was kept
# as the appointment "anything tonight" and said back "You're anything tonight. What do you want
# to have ready for it?"
# The words that stand in for a thing the person has not named: "anything on tonight" was read
# as the plan "anything tonight". They are the placeholder words only. The people words are not
# here - "someone at 3 on tuesday" is still something to be ready for, and a name the person has
# not given yet is not a placeholder ("Somebody at 3 on tuesday" was answered "I'm listening").
APPOINTMENT_NOT_A_THING = frozenset("""it its it's that this he she they them there here we us
i im i'm you what when where which who why how the a an anything something nothing everything
whatever""".split())


# A past-tense verb is what makes a clock line a report of something that has already happened,
# and APPOINTMENT_PAST only knows the time words ("yesterday", "last night"). "the plumber came
# at 9" was kept as the thing "plumber came" and read back "Your plumber came is at 9": the verb
# is in the thing, so the thing is where it is caught. The irregulars come first because no "-ed"
# rule can see them.
APPOINTMENT_PAST_VERB = frozenset("""came went left rang arrived started finished met ate had was
were got sent made saw took gave told said ran sat stood put bought paid brought caught found
kept slept spoke drove flew drank began broke chose fell felt fought heard held hit hurt lost
meant read rode rose sold sang shut spent threw understood woke wore won wrote""".split())


# The same glue in the present: "my shed is coming at 3" would read back "Your shed is coming is
# at 3". A thing that has a verb phrase in it is a sentence, and an appointment's thing is a noun.
APPOINTMENT_A_VERB = frozenset("""is are am be being comes coming arrives arriving leaves leaving
starts starting finishes finishing returns returning waits waiting""".split())


# A verb in front of a date is the verb's own line, not a thing they have on a day: "the shop
# closes december 3" kept as an appointment was said back as "Your shop closes is on December 3".
# The same verb in front of a clock is left alone, because "the pharmacy opens at 9" is a thing
# worth answering and the store already says it the way the person typed it.
APPOINTMENT_A_DATE_VERB = frozenset("""closes closing opens opening begins beginning ends ending
starts starting finishes finishing runs running happens arrives arriving leaves leaving""".split())


# Words that end in "-ed" and are not a verb: a shed and a bed keep a delivery time.
APPOINTMENT_NOT_A_VERB = frozenset("""bed beds shed sheds red seed feed speed need hundred wed
aged kindred moped""".split())


# A line that opens with a word of taking something back is not an appointment of its own: it
# is the dentist's day being put right. Read as a thing with a day on it, "sorry thursday"
# became the thing "sorry" at its own day, and the store then corrected that instead of the
# dentist: "Got it — your sorry is on Thursday", and the appointment still said Tuesday.
APPOINTMENT_CORRECTION = frozenset("""sorry no nope nah actually wait oh ah oops rather instead
wrong not""".split())


# How the day itself is, which is a remark and not a thing anyone has on a day. "hot today",
# "freezing this morning" and "lovely weather today" name nothing the person is going to do, and
# kept as a thing with a day on it they came back as plans: "what have i got coming up" answered
# "You're planning to hot today", and "hot today" then "i might go to the beach" was two things
# ahead of them. The words below are the ones a day is described with, plus the weather itself; a
# thing made only of them is that remark. A thing with anything else in it ("dentist today",
# "the scan tomorrow", "nice meal out on friday") keeps its day.
DAY_REMARK_WORDS = frozenset("""hot cold warm freezing boiling chilly cooler warmer mild sunny
cloudy overcast windy wet rainy foggy misty grey gray bright dull damp humid muggy sticky close
lovely nice horrible awful miserable grim rubbish lousy great good fine better worse busy quiet
long short dark clear beautiful gorgeous stunning glorious pleasant freezing bitter fresh soft
weather rain rains raining snow snowing sun sunshine wind winds windy frost icy ice sleet hail
thunder storm stormy drizzle drizzling pouring showers downpour heatwave freezing""".split())


# The little words that hold a remark together: "lovely weather today", "very hot out today".
DAY_REMARK_GLUE = frozenset("""the a an and but its it is was out in up here there very really so
quite too bit rather enough still again today tonight tomorrow now morning afternoon evening all
day week week's end bit lot much more""".split())


def _the_day_described(thing):
    """True when the thing before the day is how that day is, not something they have on it.

    "hot today" and "lovely weather today" are remarks about the day, and the store that kept
    them as plans said them back as things ahead of the person. Only a thing with no other word
    in it is a remark: "nice meal out on friday" and "dentist today" have a thing of their own
    after the words a day is described with are taken out.
    """
    left = [word.strip(",.!;:'\u2019") for word in str(thing or "").lower().split()]
    left = [word for word in left if word and word not in DAY_REMARK_WORDS
            and word not in DAY_REMARK_GLUE]
    return not left


# The day can also be said first: "december 3 my course starts", "21 october the boiler service is
# booked". Nothing is in front of the day to be the thing, so the thing is the clause after it, cut
# where the clause says what happens on the day. Without this the line kept no plan at all: the
# course was noted as a line that says nothing, and "when does my course start" was answered "No
# date from you on that one".
A_DAY_SAID_FIRST = re.compile(
    r"^(?:on\s+|in\s+)?(?:the\s+)?(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?)?"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(?:st|nd|rd|th)?\b", re.I)


# "dinner for 6 on saturday" is six people, not six o'clock. A figure after "for" is a clock only
# when nothing in front of it is what people are counted for - "be there for 6", "booked for 7" -
# and a count when a meal, a table or a party is the thing said before it. Kept as a clock, the
# plan was filed "dinner at 6 on saturday", so "actually make that 8" moved the dinner to eight
# o'clock instead of putting the table up to eight people, and "how many am i cooking for" could
# not be answered at all.
_A_COUNT_NOT_A_CLOCK = re.compile(
    r"\b(?:dinner|lunch|breakfast|brunch|supper|tea|meal|table|tables|party|round|booking|"
    r"seats?|covers|guests?|people|plates?|portions?|helpings?|rooms?)\b", re.I)


def _the_thing_said_after_the_day(low, day):
    """The thing named after a day said at the front of the line, "" when the rest is not a thing.

    The clause tells what happens on the day in its own verb ("my course starts", "the boiler
    service is booked"), so the thing is the clause up to that verb: what is kept is the thing and
    the day, which is the order every other appointment is kept in.
    """
    if day.start() > 4:
        return ""  # the day is not the opening: something in front of it was the thing already
    rest = low[day.end():].strip(" ,;:-")
    rest = re.sub(r"^(?:on|in|at)\s+", "", rest)
    kept = []
    for word in rest.split():
        bare = word.strip(",.!;:")
        if bare in APPOINTMENT_A_VERB or bare in APPOINTMENT_A_DATE_VERB:
            break
        if len(bare) > 3 and bare.endswith("ed") and bare not in APPOINTMENT_NOT_A_VERB:
            break
        kept.append(word)
    thing = " ".join(kept).strip(" ,;:-")
    thing = re.sub(r"^(?:the|my|our|a|an)\s+", "", thing)
    return thing


def _appointment(text):
    """The appointment in a line that names a thing and a time and nothing else.

    "dentist at 3 on tuesday" -> "dentist at 3 on tuesday"; "" for every other line, so the
    plan reader and the deed reader keep every line they had."""
    said = " ".join(text.split()).strip(" .,!;:-")
    words = said.split()
    if not words or "?" in said or len(words) > 12:
        return ""
    low = said.lower()
    if APPOINTMENT_OWN_SUBJECT.match(low):
        return ""  # a line with their own subject in front is the plan reader's
    if ASKING.match(low) or APPOINTMENT_PAST.search(low) or NEGATED.search(low):
        return ""
    if SECOND_PERSON.search(low):
        return ""  # "your appointment is at 3" is about the bot
    clock, day = APPOINTMENT_CLOCK.search(low), APPOINTMENT_DAY.search(low)
    if clock and re.match(r"for\s", clock.group(0), re.I) and _A_COUNT_NOT_A_CLOCK.search(low[:clock.start()]):
        clock = None
    if not clock and not day:
        return ""
    if clock:
        # Whatever follows the clock has to be the day and nothing else: "the shop is at 3 the
        # parade" puts a street after the number, and that is a place, not an appointment.
        after = low[clock.end():].strip(" ,.;:-")
        if after and not re.match(r"^(?:on\s+)?" + APPOINTMENT_DAY.pattern + r"$", after, re.I):
            return ""
    cut = min([m.start() for m in (clock, day) if m])
    thing = low[:cut].strip(" ,;:-")
    thing = re.sub(r"^(?:the|my|our)\s+", "", thing)
    thing = re.sub(r"\s+(?:is|at|on|for)$", "", thing).strip()
    if not thing and day is not None and cut == day.start():
        thing = _the_thing_said_after_the_day(low, day)
    if not thing or len(thing.split()) > 4:
        return ""
    if _the_day_described(thing):
        return ""  # "hot today" is how the day is, not a thing they have on it
    if TAKE_BACK_WORDS.search(thing):
        return ""  # the line takes the last thing back; it does not name something on a day
    if thing.split()[0] in APPOINTMENT_NOT_A_THING:
        return ""
    if thing.split()[0].strip(",.!") in APPOINTMENT_CORRECTION:
        return ""  # "sorry, its at 8pm" is the clock being put right, not a thing called Sorry
    if not re.search(r"[a-z]{3}", thing):
        return ""
    # A thing the line says has already happened is not an appointment: "the nurse arrived at 6"
    # is news, and kept as a thing on a clock it answers "Your nurse arrived is at 6".
    for word in thing.split():
        if word in APPOINTMENT_PAST_VERB or word in APPOINTMENT_A_VERB:
            return ""
        if len(word) > 3 and word.endswith("ed") and word not in APPOINTMENT_NOT_A_VERB:
            return ""
    if day is not None and re.search(r"\d|" + MONTH_NAMES, day.group(0), re.I):
        if thing.split()[-1].strip(",.!") in APPOINTMENT_A_DATE_VERB:
            return ""
    # The plan is kept the way the ask will read it back: the thing, then its clock, then its
    # day ("dentist at 3 on tuesday"). The day goes last because that is the order the when ask
    # says it back in, and a plan that keeps their word order says "You're planning to dentist
    # saturday at 10" - a machine reading a phrase.
    when = []
    if clock:
        when.append("at " + " ".join(clock.group(1).split()))
    if day:
        day_text = " ".join(day.group(0).split())
        # A day already carries its own word ("on tuesday", "next friday", "this morning"),
        # and "tomorrow" takes none: "on tomorrow" is not something anyone says. Every other day
        # needs the "on", a date written month-first included: "the scan is december 3" kept as
        # "scan december 3" was read back as "You're planning to scan december 3".
        if not re.match(r"^(?:on|this|next|today|tomorrow|tonight)\b", day_text, re.I):
            day_text = "on " + day_text
        when.append(day_text)
    return thing + " " + " ".join(when)


# A clock on its own puts nothing in the future: "i woke at 3" is this morning, not tonight. So
# the plan reader asks for a word of coming up, and a thing the person has to do carries its own:
# "i have to pick up the kids at 3" is today, and read as nothing at all it was answered with a
# hedge. Only the present says so - "i had to" and "i needed to" have already happened.
OBLIGATION = re.compile(r"\b(?:have|has|ve|need|needs|got|gotta|must)\s+(?:to\s+)?[a-z]", re.I)


# A thing they do on repeat is how their week runs, not something coming up: "i have to get up at
# 6 every day" is a habit, and kept as a plan it turned "whats coming up" into a list of their
# routine. The words that put a thing on repeat refuse it, the way PAST refuses "i had to". A
# one-off with a day on it still stands ("i have to work this weekend", "the dentist on monday").
RECURRENCE = re.compile(
    r"\b(?:every|each|most\s+(?:days?|nights?|mornings?|weeks?|weekends?|evenings?)|"
    r"usually|always|never|twice|daily|nightly|weekly|monthly|fortnightly|"
    r"weekdays?|weeknights?|on\s+weekends?|weekends)\b", re.I)


# A clock on a train that leaves, a shift that starts or a flight that lands is a time they have
# to be somewhere, and it is ahead of them with no "tomorrow" in the line: "my train leaves at
# 8.15" was read as nothing at all ("I'm listening - say more if it helps") while "my bus gets in
# at 7" was a plan, because "gets in" is not one of the verbs that make a thing a sentence.
A_CLOCKED_EVENT = re.compile(
    r"\b(?:leaves?|leaving|departs?|departing|starts?|starting|begins?|beginning|arrives?|"
    r"arriving|lands?|landing|gets?\s+(?:in|there|back)|takes?\s+off|checks?\s+in|"
    r"sails?|sailing|flies?|flying|boards?|boarding|opens?|opening|closes?|closing)\b", re.I)


def _coming_up(clause):
    """True when the clause says something that is still to come.

    A future word says it ("tomorrow", "on monday", "in july"), and so does a thing they have to
    do with a clock or a day on it: "i have to pick up the kids at 3" names no future word and is
    the rest of today.
    """
    if RECURRENCE.search(clause):
        return False
    if FUTURE.search(clause):
        return True
    if OBLIGATION.search(clause):
        return bool(APPOINTMENT_CLOCK.search(clause) or APPOINTMENT_DAY.search(clause))
    return bool(A_CLOCKED_EVENT.search(clause) and APPOINTMENT_CLOCK.search(clause))


def _dated_plan(text, deed=None):
    """The plan in a line that puts something in the future, however it is worded.

    "i start my new job on monday", "my holiday is in august" and "my daughter's party is next
    saturday" all say what is coming up, and none of them opens with "i'm going to". The clause
    that carries the date is the plan: it has to be the person's own business, in their own
    voice, and not a question or something that already happened.

    A clause that already happened is news rather than a plan, and it is still a fact about them
    worth answering with the thing itself ("you paid the rent on friday - noted"), so the deed is
    put in the list a caller passes in instead of being dropped."""
    # A line with nothing coming up in it is not a plan whatever its halves look like: a thing
    # with a clock on it ("we've got a plumber coming at 9") is read by the appointment reader,
    # and taking it here would keep the half and lose the sentence the person said.
    if not _coming_up(text):
        return ""
    for clause in _dated_plans(text, deed):
        return clause
    return ""


# The same coming thing is said with another verb too: "my mum is coming to stay in may" then
# "my brother in june" is one person's plan and another's, and the second half is said without a
# verb because the first half carries it.
CLAUSE_SUBJECT = re.compile(
    r"^\W*(?:(?:and|but|so|also|then|oh|ok|okay|well|plus)[\s,]+)*"
    r"(?:my|our|the|his|her|their|i|we|me)\b"
    r"(?:\s+(?!(?:is|are|was|were|am|in|on|at|next|this|tomorrow|tonight|over|for|by|"
    r"before|after)\b)[\w'\u2019.\-]+){0,4}", re.I)


WHEN_OR_WHERE = re.compile(
    r"\b(?:in|on|at|next|this|tomorrow|tonight|over|for|by|from|before|after)\b|"
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
    re.I)


A_SHARED_VERB = re.compile(r"^(?:is|are|was|were|am)\b", re.I)


CORRECTION_LEAD_RE = re.compile(CORRECTION_LEAD, re.I)


# A word that can open a correction, and is also an ordinary word in front of a noun: "no heat",
# "no comedy", "sorry business", "wait list". What tells the two apart is the punctuation the
# person put after the opener - "no, four brothers" - or an opener that is more than one word and
# announces itself - "no wait, three sisters", "oh actually, six". Written once, so the reader that
# takes the opener off and the one that asks whether the words are only an opener agree.
OPENER_WORDS = ("ok", "okay")


OPENER_PUNCTUATION = re.compile(r"[,.:;!?\-\u2013\u2014]\s*$")


def _the_opener_end(said):
    """Where the correction opener in front of `said` ends, or 0 when it does not open with one."""
    lead = CORRECTION_LEAD_RE.match(said)
    if not lead:
        return 0
    front = lead.group(0)
    if OPENER_PUNCTUATION.search(front):
        return lead.end()
    words = [one for one in re.split(r"[^a-z']+", front.lower()) if one]
    words = [one for one in words if one not in OPENER_WORDS]
    return lead.end() if len(words) >= 2 else 0


def without_the_correction_opener(text):
    """The line after the opener that says the last thing is being said again, or "" when the
    line does not open with one.

    The opener is the person's, but it names nothing the line is about: "sorry, four brothers"
    and "no wait, three sisters" both go back over the fact the turn before stated, and the apology
    in front of one says only that the value is being said again. Every reader that takes a
    subject, a thing or a key out of a line reads it here first, so a correction never arrives
    wearing an opener that a card can match on - "sorry, three sisters" after "i have two sisters"
    was answered by the apology row, whose ask word is "sorry"
    (bot/knowledge/lookup.py, `_past_a_correction`; bot/memory/named.py, `about_it`).
    Only a lead the person punctuated - or one that is two words and announces itself ("no wait",
    "oh actually") - is taken off. "no" and "sorry" are ordinary words too: "no heat in my car",
    "no time to cook dinner" and "sorry i snapped at her" are the line, not an opener with a value
    behind it, and stripping the word off those took a heater, a dinner and an apology away from
    their own answers.
    """
    said = " ".join(str(text or "").lower().split())
    end = _the_opener_end(said)
    if not end:
        return ""
    return said[end:].strip(" ,.;:\t\u2013\u2014")


def is_a_correction_opener(text):
    """True when the words are nothing but the opener that announces a correction.

    The words are the person's ("no wait,", "sorry,", "oh, actually,", "scratch that,"), and they
    name nothing on their own: they say that the last thing is being said again. Read off the same
    lead as the correction itself, so a reader that has to tell an opener from a value cannot
    disagree with the one that reads the correction - "wait, four brothers" was said back as
    "Got it - wait, four brothers" because the echo took "wait," for part of the value
    (bot/memory/ack.py, `_only_the_correction_in_front`).
    """
    said = " ".join(str(text or "").lower().split())
    if not said:
        return False
    lead = CORRECTION_LEAD_RE.match(said + " ")
    return bool(lead and lead.end() > len(said))


def _said_after_the_subject(clause):
    """What the clause says about its subject, before the time or place it is nailed to:
    "is coming" in "my sister is coming in may", and "" in "my brother in june"."""
    match = CLAUSE_SUBJECT.match(clause)
    rest = clause[match.end():] if match else clause
    where = WHEN_OR_WHERE.search(rest)
    return (rest[:where.start()] if where else rest).strip(" ,")


def _the_verb_for(body, subject):
    """The lent verb agreeing with the person it now belongs to: "are going to spain" said of
    "my mum" is "is going to spain", and said of "i" is "am going to spain"."""
    first = body.split()[0].lower() if body.split() else ""
    person = str(subject or "").strip().lower()
    plural = person in ("we", "they", "you") or " and " in person
    if not plural:
        if first == "am":
            return "is" + body[2:]
        if first in ("are", "were"):
            return ("is" if first == "are" else "was") + body[len(first):]
    if person == "i" and first == "is":
        return "am" + body[2:]
    return body


def _with_the_verb_lent(clause, earlier):
    """The clause with the verb of the clause before it put back: "my brother in june" after
    "my sister is coming in may" is "my brother is coming in june". Left alone when either
    half says something other than this sharing, or when the clause has a verb of its own."""
    if not clause or not earlier or _said_after_the_subject(clause):
        return clause
    body = _said_after_the_subject(earlier)
    if not A_SHARED_VERB.match(body):
        return clause
    match = CLAUSE_SUBJECT.match(clause)
    subject = match.group(0) if match else ""
    body = _the_verb_for(body, subject)
    rest = clause[match.end():].lstrip() if match else clause
    if not rest:
        return clause
    return (clause[:match.end()].rstrip() + " " + body + " " + rest).strip()


def _dated_plans(text, deed=None):
    """Every plan a line carries, in the order it says them.

    "my sister is coming in may and my brother in june" is two things coming up, and the second
    is said without a verb of its own: the verb of the first is lent to it ("my brother is coming
    in june"), because that is how the person said it."""
    # The words that put a thing in the future are not the only ones a plan is said with: "we've
    # got a plumber coming at 9" has a clock on it and no "going to", and the line's own coming-up
    # reader knows the difference. Either one opens the line; the clause still has to carry it.
    if not FUTURE.search(text) and not _coming_up(text):
        return
    at = 0
    earlier = ""
    for piece in re.split(r"(?<=[.!?])\s+|,|;|\s+(?:but|and|so|then)\s+", text):
        # Where this piece sits, so the person it was joined to can be taken back: the "and" in
        # "my sister and i are going to italy in june" splits the subject, not two clauses, and
        # the half that is left ("i are going to italy in june") agrees with nobody and says the
        # sister is not going. The same line read against one person is "you are going to italy".
        start = text.find(piece, at) if piece else -1
        ahead = text[:start] if start != -1 else ""
        if start != -1:
            at = start + len(piece)
        clause = " ".join(piece.split()).strip(" ,.;:-!")
        if not clause:
            continue
        # A correction opens with a lead and the rest of it is still the plan it is about:
        # "actually my brother is coming in july" is the brother's plan with the new date. Left
        # whole, the lead keeps the clause from being read as theirs at all, so the newer date is
        # never filed and the ask is answered from the older plan the store kept.
        opened = CORRECTION_LEAD_RE.sub("", clause, count=1).strip()
        if opened and OWN.match(opened):
            clause = opened
        # The person the clause was split from is put back before anything is asked of it: it is
        # what makes the clause theirs, so "me and sarah are going to the cinema on friday" (kept
        # as "sarah are going to the cinema on friday") and "me and the kids are going to spain
        # in july" (kept as "the kids are going to spain in july") are one plan, not none.
        joined = _with_the_person_joined_to_the_subject(ahead, clause)
        # Either half can be the half that says whose plan it is: "the kids and i are going to
        # spain" opens with the kids, "me and the kids are going to spain" opens with the person.
        if not (OWN.match(joined) or OWN.match(clause)
                or THE_THING_HAS_A_DAY.match(clause)) or "?" in joined:
            # A thing of the household with a day on it is theirs too ("the rent is due on 1
            # july"), which `OWN` cannot see because it names no person.
            continue
        clause = _with_the_verb_lent(joined, earlier)
        if not _coming_up(clause) or PAST.search(clause):
            continue
        if ASKING.match(re.sub(r"^(?:ok(?:ay)?[, ]+|and |so |but |also |well |oh )+", "", clause,
                               flags=re.I)):
            continue
        if SECOND_PERSON.search(clause):
            continue  # "i'll call you tomorrow" is about the bot, not about their week
        if NEGATED.search(clause):
            continue  # "i can't sleep tonight" is how today is, not a plan
        if _how_they_are(clause) or _how_their_things_are(clause):
            # "im really low this week" is how they are, and "my budget is tight this month" is
            # how a thing of theirs is: neither is what they are doing
            continue
        if a_deed(clause):
            if deed is not None:
                deed.append(clause)
            continue  # "i saw my mum on sunday" has happened; it is not coming up
        words = clause.split()
        if len(words) < 3 or len(words) > 18:
            continue
        if not (re.search(r"\b(?:my|our|i|we|i'm|im|me)\b", clause, re.I)
                or THE_THING_HAS_A_DAY.match(clause)):
            continue
        if len(re.findall(r"\b(?:i|my|we|our)\b", clause, re.I)) > 3:
            continue  # a whole paragraph said in one breath is not one plan
        earlier = clause
        yield clause


# A thing of the household with a day on it is theirs as much as "my" makes it: "the rent is due
# on 1 july", "the car tax is due on 3 august", "the boiler service is on 21 october". The clause
# names no person, so the plan reader skipped it and the store kept nothing - the person's own
# arrangement got the dead "Thanks for telling me" and the next ask about it was a search offer,
# while the knowledge base answered a general card about road tax or a boiler service. Only the
# shapes where the thing comes round on a day are read: "the weather is nice this weekend" is how
# the weekend is, and "the shop closes at 5" already names its own verb.
THE_THING_HAS_A_DAY = re.compile(
    r"^the\s+[a-z][a-z' \-]{1,30}?\s+(?:is|are|was|were)\s+"
    r"(?:due|on|booked|scheduled|expected|renewed)\b"
    r"|^the\s+[a-z][a-z' \-]{1,30}?\s+(?:expires?|expiring|runs?\s+out|renews?)\b", re.I)


# The one half of a subject that can come before the "and": "me", "i" and a person of theirs
# ("my sister", "the kids"). Requiring one of those shapes is what keeps an "and" between two
# things they are doing ("we went to spain and my sister is coming too") from joining them.
JOINED_PERSON = r"(?:me|i|(?:my|our|the|his|her|their)\s+[a-z'\u2019]{2,20})"


SUBJECT_JOIN = re.compile(
    r"^(?:and|but|so|also|well|ok|okay|oh|then|plus)?[\s,]*"
    r"(?:" + JOINED_PERSON + r")\s+and(?:\s+(?:me|i))?"
    r"(?:\s+" + JOINED_PERSON + r")?$", re.I)


def _with_the_person_joined_to_the_subject(ahead, clause):
    """The clause with the person it was split from, when the split went through a subject.

    "my sister and i are going to italy in june" keeps "i are going to italy in june", which is
    neither of them and is said back as "You're planning to i are going to italy". Only a piece
    that names a person and has no verb of its own joins, so "i'm 34 and i live in leeds" (whose
    first half says something) and "we are going to spain and my sister is coming too" (whose
    second half does) are split the way they were."""
    person = " ".join((ahead or "").split())
    if not person or not SUBJECT_JOIN.match(person):
        return clause
    return person + " " + clause


# A self-introduction is often typed as a list of who they are: "im sam, 34, live in
# leeds", "im jess, 28, from dublin, a nurse". Read on its own the line names the person
# and drops the rest, because the parts after a comma have no "i" in front of them. Each
# part is read the way the line would be if it were said by itself, and a part that talks
# about someone else ("my sister lives in cork") is left to the readers that expect it.
# A part that already has an "i" of its own is a clause, not a half clause: "im in bristol, i
# moved in march" is two facts, and the second one put under an "i'm" of its own comes out as
# "i'm i moved in march" and is read back as "you're you moved in march".
SELF_INTRO = re.compile(
    r"^\W{0,2}(?:(?:hi+|hey+|hello+|hiya)\b[\s,]*)*(?:im|i'm|i am)\s+"
    r"[a-z'\u2019\-]{2,}(?:\s+[a-z'\u2019\-]{2,})?\s*,(?P<rest>[^?]*)$", re.I)


OTHER_START = frozenset("my our his her their the it we they she he there this that".split())


# A part that starts with one of these is not a fact about them: it is the rest of a question
# ("im tired, should i go to bed") and reading it would name them after a question word.
NOT_A_PART = frozenset("""what how why when where who which should can could do does did is are
was were will would shall may might help thanks thank sorry please so but and if maybe just""".split())


# A second clause that leaves the subject out still says something about the person: "im 34 and
# live in leeds", "i work in a bakery and drive a van", "im 34, live in leeds". The subject of
# the line carries over the "and", and English drops it whenever it repeats, so the clause is
# read with it put back. Only when the clause it follows was about them: "my mum is 72 and lives
# in York" carries her subject over, not theirs.
CONTINUATION_SPLIT = re.compile(r",|;|\s+(?:and|but)\s+", re.I)


PERSON_SUBJECT = frozenset("""i im i'm i've ive i'd id we we're we've""".split())


ANY_SUBJECT = PERSON_SUBJECT | frozenset("""my our his her their he she it they there this that
you your""".split())
