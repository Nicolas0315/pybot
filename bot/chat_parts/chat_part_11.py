"""Part 11 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import fallback, pick
from ..understanding.kinds import EMOTION_WORDS
from ..memory import user

from ..memory import ack, user

from ..memory import facts
from ..knowledge import travel as travel_kb
from ..understanding.topics import PLACES as KNOWN_PLACES
from .chat_part_01 import (
    JOKES, SHORT_JOKES, PLACE_TAIL, PLACE_IDIOM, PLACE_LAST, PLACE_MOST, PLACE_POINTS, PICK_WORDS,
)
from .chat_part_02 import (
    PLACE_NOBODY, PLACE_THING_OPENS, PLACE_TIME, PLACE_TIME_OPENS, PET_ANY, SAID_POOR,
    WATCHED_THINGS, SOME_WHEN, TRIP_SHORT_COUNTRIES, TRIP_TIME_TAIL, WHEN_DONE, BAD_NEWS,
)
from .chat_part_05 import (
    SOFTEN,
)
from .chat_part_06 import (
    BARE_FILLER,
)
from .chat_part_07 import (
    SOMEBODY_ELSE,
)
from .chat_part_10 import (
    FED_UP_BARE, FED_UP_STOPS, FED_UP_THING, ABOUT_REPLIES, FEDUP_GERUND_SAFE, FEDUP_LEAD,
    FEDUP_REPLIES, GENERIC_OTHER_REPLIES, OTHER_REPLIES,
)


# A tail left as the opener of the clause it came from names nothing: "fed up with how they treat
# me" stops at "they", and what is left ("how") is not a thing to ask about, so the line goes to
# the pool that asks how long it has been going on.
FED_UP_THIN = frozenset("""how what why when where way the a an that this these those to of
    in on at for with about""".split())


NOT_A_THING = frozenset("""it this that them him her everything anything all life nothing
    everyone someone everything you u ya yuo us""".split())


# A tail that opens with one of these is about a person or the whole of it, not about a thing to
# ask after: "done with you", "done with us", "sick of us always arguing". `this` and `that` are
# not here, because "fed up of this flat" does name the flat.
NOT_A_THING_FIRST = frozenset("""it them him her you u ya yuo us me everything anything nothing
    all life everyone someone""".split())


# The words that say how a person is, gathered from the reading's own table, so a line that is
# only a feeling word is never mistaken for a line that names something.
FEELING_WORD = frozenset(
    word for words in EMOTION_WORDS.values() for word in words) | frozenset(
        """feel feels feeling felt think thought know mean means
        sure understand follow get see sense""".split())


# What "im confused about it" is about is not a thing: it is the whole of it, said with a word
# that names nothing. The same is true of "the whole thing" and "any of this".
NOTHING_NAMED = (BARE_FILLER | NOT_A_THING | FEELING_WORD | frozenset("""
    whole thing things stuff lot bit way ways part parts point now honest lol lmao yes no ok
    okay right yeah all both either neither more less much many some any none
""".split()))


def _confusion_names_a_thing(understood):
    """True when the line says what the person cannot follow, and it is a thing of theirs.

    "im confused about my medication" names the medication, and the row for it answers (a weekly
    box from the chemist, filled on a Sunday together); a pool line that asks "which part is
    clear and which part is foggy?" throws that away. "im confused about it" names nothing, so
    the pool is the answer.
    """
    if not isinstance(understood, dict):
        return False
    # The keywords are the line's content words with the fillers already taken out, and an empty
    # list means the line named nothing: "i dont get it" must not fall back to its raw words.
    named = understood.get("keywords")
    if not isinstance(named, list):
        named = understood.get("words") or []
    for word in named:
        if not isinstance(word, str):
            continue
        word = word.strip(".,!?;:'\"()").lower()
        if word and word not in NOTHING_NAMED and word not in CONFUSION_IDIOM_WORDS:
            return True
    return False


# The words the state is said with when it is said as a picture: "i cant get my head round this",
# "i cant make head nor tail of it". They are the line's content words, so the check above read
# them as the thing the person cannot follow and stood the confused pool down for every one of
# these lines - the pool that asks "which part is clear and which part is foggy", which is exactly
# the question these lines want. A line that adds a real thing ("round the tax form") is not
# affected: the thing is still named.
CONFUSION_IDIOM_WORDS = frozenset("""cant cannot can not get got make my head round around
    straight nor tail of this that it understand follow struggling to""".split())


# The thing is said back in the second person, and the rest of the tail follows it: "fed up with
# my sister borrowing my clothes" is about the clothes too, and "sick of my mum telling me what
# to do" is her telling *you*, not telling me.
SECOND_PERSON = {"my": "your", "our": "your", "me": "you", "us": "you", "mine": "yours",
                 "ours": "yours"}


SECOND_PERSON_RE = re.compile(r"\b(my|our|me|us|mine|ours)\b")


# "im not fed up" is somebody saying it is fine, not somebody who has had enough: the phrase has
# to be said, not denied, for the fed-up branch to take the turn.
FED_UP_DENIED = re.compile(
    r"\b(?:not|never|n't|no longer|no way)\b(?:\s+\w+){0,2}\s+"
    r"(?:fed up|browned off|peeved|sick of|tired of|had enough|had it with|done with)\b"
    # "i never said i was fed up" and "i didnt say i was sick of it" deny the line too, and the
    # words in between are what makes them longer than the shape above.
    r"|\b(?:never said|didnt say|didn't say|never claimed|dont remember saying|"
    r"don't remember saying)\b[^,.;!?]*\b(?:fed up|browned off|peeved|sick of|tired of)\b")


# The question about the bot's own patience: "do you ever get tired of answering questions" is
# not the person being tired of anything, so the branch that asks about the thing named must not
# take it. A second-person subject in front of the phrase is what says so.
FED_UP_ABOUT_THE_BOT = re.compile(
    r"\b(?:do|does|did|are|were|would|will|can|could|have|has|ever|dont|don't|doesnt|doesn't)\b"
    r"[^.?!]*\b(?:you|u|ya)\b")


# "...with me" is how two people are with each other, not a free-floating annoyance: "she is
# browned off with me" has the relationship answer on main ("You seem a bit off with me - have I
# done something?"), and the venting pool asks what the worst part is instead.
FED_UP_WITH_A_PERSON = re.compile(
    r"\b(?:fed up|browned off|peeved|sick of|tired of|done with|had enough of|had it with)\s+"
    r"with\s+(?:me|us|him|her|them)\b")


# Chatter after the pronoun is still the pronoun: "sick of it tbh" names nothing to ask about,
# and the filler used to be carried into the reply as if it were the thing ("fed up with it tbh").
FED_UP_FILLER = frozenset("""tbh tho though like honestly lol haha innit tbf ngl atm really just
    now today rn 2bh imo""".split())


FEDUP_SAID_PHRASE = re.compile(
    r"(fed up with|fed up of|fed up|browned off with|browned off of|browned off|peeved with|"
    r"peeved about|peeved at|peeved|sick and tired of|sick of|tired of|done with|had enough of|"
    r"had it with)")


def _fedup_phrase(said, at):
    """The phrase the line used for being fed up: "fed up of" in "im fed up of this flat"."""
    hit = FEDUP_SAID_PHRASE.match(str(said or "")[at:])
    return hit.group(1) if hit else "tired of"


def _fed_up_with(clean):
    """The thing a fed-up line names, in the second person, or "" when it names none."""
    hit = FED_UP_THING.search(" ".join(str(clean or "").split()))
    if not hit:
        return ""
    tail = FED_UP_STOPS.split(hit.group(1))[0].strip(" .")
    if not tail:
        return ""
    # A filler is not part of the thing, whatever it is: "sick of it tbh" is the pronoun alone.
    # Only the ends, though: a filler in the middle of a distress line is the person's own words
    # ("sick of feeling like this" came back as "feeling this"), so `like` stays where it was said.
    parts = tail.split()
    while parts and parts[0] in FED_UP_FILLER:
        parts.pop(0)
    while parts and parts[-1] in FED_UP_FILLER:
        parts.pop()
    tail = " ".join(parts)
    if not tail:
        return ""
    owner = re.match(r"^(?:my|our)\b(.*)$", tail)
    if not owner and not FED_UP_BARE.match(tail):
        return ""
    # "sick of it" names nothing to ask about, but "fed up of this flat" names the flat: only a
    # tail that is the pronoun alone is nothing.
    first = tail.split()[0]
    if tail in NOT_A_THING or first in NOT_A_THING_FIRST:
        return ""
    if all(word in FED_UP_THIN for word in tail.split()):
        return ""
    if owner:
        tail = "your" + owner.group(1)
    return SECOND_PERSON_RE.sub(lambda hit: SECOND_PERSON[hit.group(1)], tail)


# The pools above are written for another adult: "low patches", "something off his plate", "the
# weight off her mind". Said of a four-year-old they read as a diagnosis of somebody small, so a
# chat that has told the bot about one child under nine gets words for a child. Nothing here
# claims a number, so it reads the same for a toddler and for a seven-year-old.
OTHER_REPLIES_SMALL_CHILD = (
    "A little one that upset is hard on everyone. What happens just before it starts?",
    "That is a lot for a small child. Is it worse at a particular time of day?",
    "Young children feel things hard and have no other way to say it yet. Does anything set it off?",
)


def _the_small_child(memory):
    """The age of the one young child this chat has been told about, or None.

    "my son is 4" then "he just cries all the time": the reply about him has to be about a small
    child, not about an adult's low patch. Only a chat with one person in it counts, because with
    two there is no telling which of them the pronoun means, and the reader that gave us the
    pronoun is the one that knows.
    """
    if not isinstance(memory, dict):
        return None
    others = [entry for entry in (memory.get("others") or []) if isinstance(entry, dict)]
    if len(others) != 1:
        return None
    age = others[0].get("age")
    if isinstance(age, int) and 0 < age < 9:
        return age
    return None


def _someone_reply(memory, feeling, obj, poss, plural, thing="", said=""):
    values = {"obj": obj, "poss": poss, "plate": "plates" if plural else "plate",
              "target": "to carry" if plural else "for one person to be carrying",
              "thing": thing, "subj": {"her": "she", "him": "he"}.get(obj, "they")}
    # "Is they talking about it?" is not English, so the verb follows the subject: she is, he
    # is, they are.
    values["subj_is"] = "is" if values["subj"] != "they" else "are"
    values["Subj_is"] = "Is" if values["subj"] != "they" else "Are"
    values["subj_does"] = "does" if values["subj"] != "they" else "do"
    values["Subj_has"] = "Has" if values["subj"] != "they" else "Have"
    if feeling == "sad" and _the_small_child(memory):
        # Seeded with the line, so two different lines about the same child do not get the same
        # sentence just because they are the second turn of their chat.
        return pick(list(OTHER_REPLIES_SMALL_CHILD), memory, said)
    if feeling == "fedup":
        # The lead is the phrase the line used, the same as for the person writing: "my husband is
        # sick of his job" is not handed back "Being fed up with".
        fed = re.search(r"\b(fed up with|fed up of|fed up|sick and tired of|sick of|tired of|"
                        r"done with|had enough of|had it with)\b", said or "")
        values["lead"] = FEDUP_LEAD.get(fed.group(1) if fed else "fed up", "Being fed up with")
        if (thing or "").startswith(("being ", "having ")):
            options = list(FEDUP_GERUND_SAFE)
        else:
            options = list(FEDUP_REPLIES)
        options = [option.format(**values) for option in options]
    elif feeling.endswith("_about"):
        options = [option.format(**values) for option in
                   ABOUT_REPLIES.get(feeling[:-6]) or GENERIC_OTHER_REPLIES]
    else:
        # A feeling group with no pool of its own used to be a KeyError, and the runtime swallows
        # it: the line fell out of this module to the greeting and came back as an echo ("Noted:
        # your mum is relieved."), which is the one reply class this bot must not produce. A
        # missing pool is now the general line about the person, so a new feeling word costs a
        # dull reply at worst and never an echo.
        options = [option.format(**values) for option in
                   OTHER_REPLIES.get(feeling) or GENERIC_OTHER_REPLIES]
    return pick(options, memory).replace("  ", " ")


def _last_was_joke(memory):
    turns = memory.get("turns") or []
    if not turns or turns[-1].get("module") != "chat":
        return False
    return turns[-1].get("bot") in set(JOKES.values()) | set(SHORT_JOKES)


def _drop_tail(phrase):
    """The phrase without what follows its place: "cork last year" is Cork.

    Each tail is applied to the end of what is left, so "leeds at the moment" and "leeds
    originally, but i live in bristol now" both come down to the name."""
    phrase = " ".join((phrase or "").split())
    changed = True
    while phrase and changed:
        changed = False
        for tail in PLACE_TAIL:
            shorter = tail.sub("", phrase).strip(" ,.;:-'")
            if shorter != phrase:
                phrase, changed = shorter, True
    # A name cut short by what the pattern could not read: "cork in 2019" leaves "cork in".
    return re.sub(r"\s+(?:in|to|at|near|from|of|on)\s*$", "", phrase)


def _place_of(phrase):
    """The place in what they said: "leeds with my two kids" is Leeds, and "a small flat in
    manchester" is Manchester, not a small flat in Manchester."""
    phrase = _drop_tail(phrase)
    if PLACE_TIME_OPENS.match(phrase.strip(" ,.;:-'")):
        return ""
    # "i live in york not leeds" names York: the words after them take back the value in front,
    # and a name that ran on through them was echoed as "York Not Leeds". A "not" that qualifies
    # instead ("not far from the station") stays, because those are the words they said about
    # Leeds and the reply says them back rather than dropping them.
    phrase = facts.take_back_cut(phrase).strip(" ,.;:-'")
    if PLACE_THING_OPENS.match(phrase):
        inner = PLACE_LAST.match(phrase)
        if inner:
            phrase = _drop_tail(inner.group(1))
    else:
        phrase = PLACE_TIME.sub("", phrase).strip(" ,.;:-'")
    if phrase.strip(" ,.;:-'").lower() in ("in", "on", "at", "to"):
        # "im moving in on friday" leaves "in" once the time is cut off the end, and a bare
        # preposition is not a place either.
        return ""
    if PLACE_NOBODY.match(phrase):
        return ""
    if not phrase or any(char.isdigit() for char in phrase):
        return ""
    if len(phrase.split()) > PLACE_MOST:
        return ""
    if phrase.split()[0].lower() in PLACE_IDIOM or phrase.lower() in PLACE_IDIOM:
        return ""
    if phrase.lower() in PLACE_POINTS:
        return ""
    return phrase


# Countries people type in capitals: "i live in the uk" is "the UK", not "The uk".
COUNTRY_CAPS = {"uk": "UK", "us": "US", "usa": "USA", "uae": "UAE", "eu": "EU", "nz": "NZ"}


# Names that carry "the" and are places: "the Netherlands", "the Midlands".
ARTICLE_PLACES = {"uk", "us", "usa", "uae", "netherlands", "philippines", "united states",
                  "united kingdom", "bahamas",
                  "gambia", "maldives", "seychelles", "czech republic", "midlands",
                  "isle of wight", "isle of man", "highlands", "cotswolds"}


def _tidy(phrase):
    """Capitalise a place name: "new york" -> "New York", but "a small flat" -> "A small flat"."""
    words = phrase.split()
    if words and words[0].lower() in COUNTRY_CAPS:
        return COUNTRY_CAPS[words[0].lower()] + phrase[len(words[0]):]
    if words and words[0].lower() == "the":
        # "the uk" is "The UK" and "the netherlands" is "The Netherlands", but "the city centre"
        # is a thing rather than a name, so only a name after "the" gets its capitals.
        rest = " ".join(words[1:])
        if rest.lower() in ARTICLE_PLACES:
            return "The " + _tidy(rest)
        return "The" + (" " + rest if rest else "")
    if words and words[0] in {"a", "an", "my", "our", "this"}:
        return words[0][:1].upper() + words[0][1:] + (" " + " ".join(words[1:]) if len(words) > 1 else "")
    small = {"in", "of", "the", "and", "at", "on", "by", "near", "upon", "under", "next", "to"}
    return " ".join(w if w in small else w[:1].upper() + w[1:] for w in words)


def _numbers(values):
    """Small numbers the way people say them: [4, 7] -> "four and seven"."""
    words = [facts.KID_NUMBER_WORDS.get(int(value), str(value)) for value in values]
    if len(words) <= 1:
        return "".join(words)
    return ", ".join(words[:-1]) + " and " + words[-1]


def _place_values(named):
    """A place as the pools say it: {X} opens a sentence, {x} sits inside one.

    A name keeps its capitals inside a sentence ("Back from Portugal", "Shame about Rome"), and a
    name that carries "the" loses it in the middle ("Back from the US"), because "Back from The US"
    is how a heading reads, not a sentence.
    """
    words = named.split()
    if words and words[0][:1].isupper() and words[0].lower() in {"the", "a", "an"}:
        # "Shame about A film" reads as a heading: an article that opens a name is the article
        # of the sentence when the name sits inside one.
        inside = words[0].lower() + (" " + " ".join(words[1:]) if words[1:] else "")
    else:
        inside = named
    return {"X": named, "x": inside}


def _note_the_pool(memory, kind):
    """Note which pool the answer came from, for the turn after (`_the_weight_said` says why a
    note made here is trustworthy). The next turn is read for what was celebrated: a win the
    person puts in a past year is a memory to ask about, not this morning's news, and which
    wording of the cheer they got cannot decide that - the pool can."""
    if not isinstance(memory, dict):
        return
    turns = memory.get("turns")
    memory["said_kind"] = {"kind": kind, "turn": len(turns) if isinstance(turns, list) else 0}


def _just_named(memory, name):
    """The one pet a line has just named ("we named him biscuit"), or None.

    The store keeps the name before this module replies, so the pet already carries it: the
    line names that pet when the name it gives is the one the only pet now has."""
    if not name:
        return None
    pets = [pet for pet in (user(memory).get("pets") or []) if isinstance(pet, dict)]
    named = [pet for pet in pets if str(pet.get("name") or "").lower() == name.lower()]
    # The pet this line named is the last one carrying that name: a second pet named later in
    # the chat ("we got a kitten" then "hes called alfie") is announced like the first, and a
    # name that only an earlier pet has is still the earlier pet rather than a new one.
    return named[-1] if named else None


def _name_said(name):
    """A pet's name the way it is written: "Mr Whiskers", not "Mr whiskers".

    The line is read in lower case, so a name of two words loses every capital it had: the reply
    has to put them back, and it cannot know where they were, so it puts one on every word."""
    name = (name or "").strip()
    if name and not any(char.isupper() for char in name):
        name = " ".join(word[:1].upper() + word[1:] for word in name.split())
    return name


def _pet_name(flat, match):
    """The name given for the pet just mentioned ("a puppy called Sam"), or "".

    Only the words between this pet and the next animal count, so "a dog and a cat called
    Tom" does not name the dog Tom."""
    rest = flat[match.end():]
    stop = len(rest)
    for other in PET_ANY.finditer(rest):
        stop = min(stop, other.start())
    # "we got a puppy and named him Rex": the animal is a pronoun by the time the name is said,
    # so "him" is not the name and the word after it is. It was read as a puppy called "Him".
    found = re.search(r"\b(?:called|named)\s+(?:([a-z][a-z'-]+)\s+)?([a-z][a-z'-]+)",
                      rest[:stop])
    if found and found.group(1) and found.group(1).lower() in facts.NOT_A_PRONOUN_NAME:
        return found.group(2)
    # A title in front of the name belongs to it: "a cat called mr whiskers" is Mr Whiskers, not
    # a cat called Mr. This is the reader the store uses, so a reply cannot announce "Lady And"
    # where the store filed a cat called Lady.
    titled = facts.PET_NAME.search(rest[:stop])
    if titled:
        return facts._with_title(titled)
    if found:
        return found.group(2)
    # "we adopted a rescue dog, biscuit": the name given as an aside, no "called" needed.
    return facts.pet_appositive(flat, match.start()) or ""


def _question_coming(understood):
    """Does the line say a question is on its way without asking it yet?

    "got a q abt me boiler", "quick question about my tax", "ive got a q". The reading labels
    these `question_coming` because nothing has been asked, so there is nothing to answer; the
    only good reply is room to ask. "Noted! What would be most useful to talk about?" is the
    wrong shape for a line that has just said what it wants to talk about.
    """
    if not isinstance(understood, dict):
        return False
    return "question_coming" in (understood.get("asks") or ())


# Topics that are the chat itself rather than something in the person's life.
NOT_A_SUBJECT = frozenset({"small-talk"})


# The same is true of the feeling a line says in its own words: "i feel stuck" and "i feel lost"
# are read as being about feelings because the line says "feel", and that reading then looked
# like the subject the not-knowing should stand aside for - so the two lines a friend answers with
# "what's the situation?" were left to the composer's placeholder ("I'm listening - say more if it
# helps"). A feeling named in the line itself is how the person is, not what they are asking about.
A_FEELING_SAID = frozenset({"feelings"})


def _the_not_knowing_has_a_subject(memory):
    """Whether the understanding engine already has a subject for this line to be about.

    It works the topic out from the conversation, so "i dont know what to do" on its own reaches
    nothing and carries no topic, while the same line after "i lost my job on friday" carries
    work. A line with a topic is answered from the thing it is about, not with the question.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    topic = understood.get("topic")
    # Small talk is not a subject: "how are you", then "idk what to do", is still the first real
    # line of the conversation, and the answer to it is the question. Nor is the feeling the line
    # says about itself.
    if understood.get("topic_own") in A_FEELING_SAID:
        return False
    return bool(topic) and topic not in NOT_A_SUBJECT


# The person's own trip to a doctor, a hospital, a scan or a result. Kept to the shapes people
# type: back from a place, went there, had a thing done, what the scan said, what the doctor
# said. A place on its own is not enough for the past tense — "i went to the doctors this
# morning" is the visit and "i went to the doctors in 2019" is a memory of one — so a "went"
# line has to carry the time too, or be short and carry nothing that puts it back in the past
# (see `_the_visit_was_this_week`).
PLACE_OF_CARE = (r"(?:the\s+)?(?:hospital|doctors?|doctor'?s|gp|surgery|clinic|"
                 r"a\s*&?\s*e|a and e|casualty|dentist|dentist'?s|physio|physiotherapy|"
                 r"chiropractor|optician|opticians|health centre|walk in centre)")


BACK_FROM_CARE = re.compile(
    r"\b(?:(?:i'?m|im|i am|we'?re|were)\s+(?:just\s+|only\s+|now\s+|finally\s+)?"
    r"(?:back|out)|(?:just|only|finally)\s+(?:got\s+)?back)\s+(?:of|from)\s+"
    r"(?P<place>" + PLACE_OF_CARE + r")\b", re.I)


WENT_TO_CARE = re.compile(
    r"\b(?:i|we)\s+(?:went|had to go|popped|nipped|headed)\s+(?:in\s+)?(?:to\s+|into\s+)?"
    r"(?P<place>" + PLACE_OF_CARE + r")\b", re.I)


# "i was in hospital last night", "i was in a and e yesterday": the same visit said the other way
# round, and still the person's own because the place is theirs and the time is this week.
WAS_IN_CARE = re.compile(
    r"\b(?:i|we)\s+(?:was|were)\s+(?:in|at)\s+(?P<place>" + PLACE_OF_CARE + r")\b", re.I)


THIS_WEEK = re.compile(
    r"\b(?:today|tonight|this morning|this afternoon|yesterday|"
    r"last night|last week|just now|this week|earlier)\b", re.I)


def _the_visit_was_this_week(flat):
    """Whether a "i went to the doctor" line is the visit rather than a memory of one.

    A time word settles it. Without one, "i went to the doctor" is still somebody telling you
    about their day and "i went to the doctors in 2019" is not, so the line is read as the visit
    when nothing in it puts it back in time and it is said in a handful of words: the long ones
    are the ones with the story and the year in them.
    """
    if THIS_WEEK.search(flat):
        return True
    return not LONG_AGO.search(flat) and len(flat.split()) <= 8


# Something they came away wearing: "they put a cast on my arm", "the nurse gave me a sling".
# A thing put on and not a thing taken off, which is the next reader's line.
PUT_ON = re.compile(
    r"\b(?:they|the (?:doctor|doctors|nurse|surgeon|hospital|physio))s?\s+"
    r"(?:put|gave me|fitted|sorted me out with)\s+(?:me\s+)?(?:a|an|the)?\s*"
    r"(?P<thing>cast|sling|brace|boot|splint|plaster|bandage|dressing|support|strapping)\b", re.I)


# "i had a tooth out this morning": the thing is gone and the day after it is the news.
# The things put on that come off again in a day or two, rather than holding a bone for weeks.
_A_DRESSING = re.compile(r"bandage|dressing|plaster(?!\s+cast)", re.I)


# "i had a tooth out this morning": the thing is gone and the day after it is the news.
TAKEN_OUT = re.compile(
    r"\b(?:i\s+)?(?:had|got)\s+(?:a|an|my|two|three)\s+"
    r"(?P<thing>tooth|teeth|wisdom tooth|back tooth|wisdom teeth)\s+out\b", re.I)


# The things people go and have done. A jab, a smear or a filling is the same kind of trip as a
# scan - their own care, on the day - and "i had my jabs today" and "i went for my smear test" were
# read as a nice day out ("Good to hear. What was the best bit?", "Nice one. How did the rest of it
# go?"), which is the wrong thing to say about a smear.
HAD_A_THING_DONE = re.compile(
    r"\b(?:i|we)\s+(?:had|got|been for|went for)\s+(?:my|a|an|the)?\s*"
    r"(?P<thing>scan|x-?ray|mri|ct scan|ultrasound|blood test|bloods|biopsy|appointment|"
    r"check-?up|procedure|operation|colonoscopy|endoscopy|ecg|"
    r"smear test|smear|cervical screening|screening|mammogram|jabs?|vaccination|injection|"
    r"booster|flu jab|physio|physiotherapy|filling|stitches|dressing)\b(?!\s+results?\b)", re.I)


RESULT_CLEAR = re.compile(
    r"\b(?:my|the)\s+(?P<thing>scan results|x-?ray results|mri results|biopsy results|"
    r"blood test results|blood results|test results|scan|x-?ray|mri|results|bloods|blood test|"
    r"biopsy)\s+"
    r"(?:came back|came|is|was|were|are)\s+(?:all\s+|totally\s+|completely\s+)?"
    r"(?:clear|fine|normal|ok|okay|good|nothing|negative)\b", re.I)


DOCTOR_SAID = re.compile(
    r"\b(?:the\s+)?(?:doctor|doctors|gp|consultant|surgeon|nurse|physio)s?\s+"
    r"(?:said|says|thinks?|reckons?|told me|has said)\s+"
    r"(?:that\s+)?(?:it'?s|its|it was|i have|i'?ve got|i had|there'?s)\s+"
    r"(?:just\s+|only\s+|probably\s+|most likely\s+|nothing but\s+)?"
    r"(?P<dx>[a-z][a-z' -]{2,30}?)(?:\s*(?:[,.;!]|$|and\b|but\b|so\b|which\b))", re.I)


# "they said my knee is fine but i should rest it": the check came back clean and there is
# still a job to do about it, which is the commonest shape of good news with a chore attached.
# A telling that puts the visit at night: the pool that says "never a fun morning" is the wrong
# one for it.
NIGHT = re.compile(
    r"\b(?:last night|tonight|overnight|all night|in the night|midnight|\d{1,2}\s*(?:am|\.\d\d)|"
    r"this evening|yesterday evening|after dark)\b", re.I)


# A time that puts the visit years back: "i had an operation on my knee in 2019" is a memory of
# one, and "the waiting is the worst of it" is the wrong thing to say about it now.
LONG_AGO = re.compile(
    r"\b(?:back in \d{4}|in \d{4}|\d+ (?:years|months) ago|years ago|months ago|"
    r"last (?:year|week|month|summer|winter|spring|autumn)|"
    r"a while (?:back|ago)|when i was (?:little|young|a kid|at school))\b", re.I)


PART_FINE = re.compile(
    r"\b(?:they|the doctor|the doctors|the gp|the hospital|the consultant|the nurse|the physio)"
    r"s?\s+(?:said|says|told me|reckon)\s+my\s+(?P<part>[a-z][a-z' -]{1,20}?)\s+is\s+"
    r"(?:fine|ok|okay|clear|all right|alright|not broken|nothing serious|nothing)\b", re.I)


# What resting actually helps. The last word of the part decides, so "lower back" rests and
# "blood pressure" does not: a number on a test is not a joint.
RESTED = frozenset("""
    knee knees shoulder shoulders ankle ankles back wrist wrists arm arms leg legs hip hips hand
    hands foot feet neck elbow elbows rib ribs thigh calf calves muscle muscles joint joints finger
    fingers thumb thumbnails toe toes spine hamstring hamstrings achilles groin shin shins forearm
    collarbone cuff tendon tendons ligament ankle heel heels
    """.split())


# A line that says so itself: "they said my back is fine but i should rest it".
REST_WORD = re.compile(r"\b(?:rest|resting|physio|exercises|take it easy|ice it)\b", re.I)


# "i got my results back today", "the results are in": the results themselves, before it is
# known whether they are clear.
GOT_RESULTS = re.compile(
    r"\b(?:(?:i|we)\s+(?:got|had|picked up)\s+(?:my|our|the)?\s*(?P<thing>scan results|"
    r"test results|blood test results|blood results|x-?ray results|mri results|biopsy results|"
    r"results)\s+back|(?:my|the)\s+(?P<thing2>scan results|test results|blood test results|"
    r"results)\s+(?:are|came)\s+in)\b", re.I)


# Words that make the sentence after "the doctor said" a sentence rather than a thing to say
# back: "the doctor said it is going to be fine" is not a diagnosis the pools can name.
NOT_A_DIAGNOSIS = frozenset((
    "fine", "ok", "okay", "nothing", "nothing serious", "all clear", "good", "clear",
    "going to be", "not", "no", "serious", "normal", "over", "a", "the", "my", "probably",
))


# A scan or a test named by its letters keeps them: "i had an mri" is the MRI, not the mri.
INITIALISMS = {"mri": "MRI", "ct": "CT", "ecg": "ECG", "ekg": "EKG", "eeg": "EEG",
               "xray": "x-ray", "x ray": "x-ray", "dna": "DNA", "hiv": "HIV"}


def _a_thing_of_care(phrase, article=True):
    """The place or the test as the pools say it: {X} opens a sentence, {x} sits inside one.

    A place takes its article back ("the hospital", "the dentist"), because "Hospital — that is
    never a fun morning" reads like a heading; a test taken with "my" or "a" does not ("my scan"
    is "the scan" in a sentence). `{A}` and `{a}` are the article for a diagnosis that needs one.
    """
    words = [word for word in re.split(r"\s+", str(phrase or "").strip()) if word]
    bare = " ".join(word for word in words if word.lower() not in {"the", "a", "an"})
    bare = re.sub(r"\bdoctors\b", "doctor", bare, flags=re.I) or "visit"
    if re.sub(r"[^a-z&]", "", bare.lower()) in {"a&e", "aande", "ande", "ae"}:
        return {"X": "A&E", "x": "A&E", "Xb": "A&E", "xb": "A&E", "A": "An", "a": "an"}
    inside = ("the " + bare) if article else bare
    # "an x-ray", "an mri": the article a diagnosis takes is read off the word it is in front of,
    # and a test named by its letters is said with the sound of them: "an MRI", "a CT".
    first = bare[:1].lower()
    vowel = (first in "aeiouw" and not bare.lower().startswith(("uni", "one", "once", "use"))) \
        or _keep_the_letters(bare) in {"MRI", "ECG", "EEG", "EKG", "x-ray"}
    return {"X": _keep_the_letters(inside[:1].upper() + inside[1:]),
            "x": _keep_the_letters(inside.lower()),
            "Xb": _keep_the_letters(bare[:1].upper() + bare[1:]),
            "xb": _keep_the_letters(bare.lower()),
            "A": "An" if vowel else "A", "a": "an" if vowel else "a"}


def _ends_plural(phrase):
    """Whether the last word of the phrase is a plural: "scan results" and "bloods" are."""
    word = str(phrase or "").split()[-1].lower() if str(phrase or "").split() else ""
    return word.endswith("s") and not word.endswith(("ss", "us", "is"))


def _keep_the_letters(text):
    """A scan or a test named by its letters keeps them: "i had an mri" is the MRI, not the mri."""
    for word, letters in INITIALISMS.items():
        text = re.sub(r"\b" + re.escape(word) + r"\b", letters, text, flags=re.I)
    return text


# Whose body the thing was put on: "on my arm" is theirs, "on my mums arm" is not.
WEARER = re.compile(
    r"\b(?:on|for|round|around|over)\s+(?P<owner>my|his|her|their|your|theirs|"
    r"[a-z]+'?s)\s*(?P<part>[a-z][a-z' -]{0,14})?", re.I)


# The bodies a brace, a boot or a sling can be put on: the parts the resting entries know, plus the
# few a cast or a support goes on that are not things you rest. A thing that is not in here was not
# put on a person: "they put a boot on my car", "they put a support on my bike" are the car and the
# bike, and the answer about a bone doing the work is about no bone at all.
A_BODY = RESTED | frozenset("""
    body skin shin jaw knuckle knuckles waist stomach tummy chest backbone pelvis shoulder scoliosis
    """.split())


def _wearer_is_themselves(flat, match):
    """True when what was put on is the person's own body, not somebody else's, and not a thing."""
    found = WEARER.search(flat, match.end() - 1)
    if not found:
        return True  # "the nurse gave me a sling" names no body at all
    if (found.group("owner") or "").lower() != "my":
        return False
    # "on my arm" is theirs. "on my mums arm" has another person between "my" and the arm, and
    # the same word list that spots a person in a line spots it here.
    rest = [word.strip(".,!?") for word in flat[found.end("owner"):].split()][:2]
    # "mums" loses its possessive s before the word list reads it, or the word boundary hides it.
    if len(rest) >= 2 and SOMEBODY_ELSE.match(re.sub(r"'?s$", "", rest[0], flags=re.I)):
        return False
    # The word after "my" is the body itself, or this was put on something that is not one. A
    # support on the bike and a boot on the car are not orthopaedic news.
    return bool(rest) and rest[0].lower() in A_BODY


def _names_a_person(word):
    """True when the word after "my" is somebody rather than a body part: "my son", "my mum".

    "they said my son is fine" is a fact about the son, and the reply about a knee that came back
    fine is about the wrong body. The word is checked against the relation words the store knows,
    the same list that decides who a line is about, and against the people a line can name.
    """
    low = str(word or "").strip().lower()
    if not low:
        return False
    if low in facts.RELATIONS or low in facts.KIN_WORDS or low in facts._BUILT_KIN:
        return True
    return bool(SOMEBODY_ELSE.match(low))


# The thing a verdict is about, when the line says which: "the match was terrible", "this film
# was great". Only a thing people sit and watch counts, so "the weather was awful" is left alone.
VERDICT_THING = re.compile(r"\b(?:the|this|that|that|my|our|a|an)\s+(?P<thing>[a-z][a-z'-]*)\b")


def _head_word(phrase):
    """The last word of a thing's name: "a good film" -> "film", "the grand prix" -> "prix"."""
    words = [word for word in re.split(r"[^a-z'-]+", str(phrase).lower()) if word]
    return words[-1] if words else ""


def _the_poor_describer(phrase):
    """The complaint word in a thing's name ("a terrible gig" -> "terrible"), or ""."""
    for word in str(phrase).lower().split():
        if word in SAID_POOR:
            return word
    return ""


def _the_thing_this_line_names(clean):
    """The watched thing the line says a verdict about ("the match"), or "" when it names none."""
    match = VERDICT_THING.search(clean)
    if not match:
        return ""
    thing = match.group("thing")
    for word in (thing, thing[:-1] if thing.endswith("s") else ""):
        if word in WATCHED_THINGS:
            return word
    return ""


def _trip_place(phrase, memory):
    """The place a trip line names, or "" when it names none the bot can stand behind.

    A city or a country the bot knows is a place it can answer about. So is a name they wrote
    with a capital ("we went to Cornwall"), and a single word the line gives a time to ("we went
    to cornwall in august"). A lower-case name the bot cannot place, with an article in front of
    it, could as easily be the tip as a place, so nothing is guessed at there.
    """
    name = _place_of(phrase)
    if not name:
        return ""
    words = name.split()
    if len(words) > 4:
        return ""
    low = [word.lower().strip("-'\u2019") for word in words]
    if not all(word.isalpha() for word in low):
        return ""
    article = low[0] in {"the", "a", "an"}
    bare = " ".join(word for word in low if word not in {"the", "a", "an"})
    if bare in KNOWN_PLACES or bare in facts.COUNTRIES or bare in travel_kb.CITIES:
        return name
    # "the US" and "the States" are the country the place tables spell "USA".
    if article and bare in TRIP_SHORT_COUNTRIES:
        return name
    typed = str((memory.get("understood") or {}).get("text") or "") \
        if isinstance(memory, dict) else ""
    if any(word[:1].isupper() and word.lower() in low for word in typed.split()):
        return name
    # A time phrase on the end of the name is not part of it: "we got back from portugal
    # yesterday" is Portugal, and the name is read again without it.
    shorter = _place_of(TRIP_TIME_TAIL.sub("", name))
    if shorter and (shorter.lower() in KNOWN_PLACES or shorter.lower() in facts.COUNTRIES
                    or shorter.lower() in travel_kb.CITIES):
        return shorter
    # A name the bot has no table for, given a time: "we went to cornwall in august". One word,
    # because "we went to the tip yesterday" is not a trip worth asking about. The time can be a
    # count of visits instead of a date ("we've been to cornwall twice"), so it is read on the
    # line as they said it and on the name with the time cut off - whichever leaves one word.
    if SOME_WHEN.search(str(phrase)):
        if len(low) == 1 and not article:
            return name
        short = _place_of(TRIP_TIME_TAIL.sub("", name)).split()
        if len(short) == 1 and short[0].lower() not in {"the", "a", "an"}:
            return short[0]
    return ""


# A good time they had, said as a thing they had rather than a place they went: "i had a lovely
# walk today", "we had a great afternoon", "i had a really nice lunch". The place reader wants a
# "went to", so these lines reached the stock nod - "Thanks for telling me - I'm here if you want
# to dig into any of that" - which fits any message at all, and the one thing the line gave was
# the thing that went well. The describer has to be a good one and the thing has to be one people
# have, so "i had a long day" (tired) and "i had a nice surprise" (news, not a time) stay out.
GOOD_TIME_WORDS = (
    "lovely|nice|great|good|brilliant|wonderful|amazing|fantastic|superb|cracking|smashing"
    "|relaxing|fun|excellent")


GOOD_TIME_THINGS = (
    "walk|day|morning|afternoon|evening|night|weekend|week|break|lunch|dinner|meal|bath|shower"
    "|swim|run|ride|cycle|sleep|lie in|nap|catch up|chat|time|hour|film|read")


GOOD_TIME = re.compile(
    r"\b(?:i|we)\s+had\s+(?:(?:a|an|such a|quite a|really)\s+)?"
    r"(?:really |properly |long |short |big |little |quiet |slow |easy )?"
    r"(?P<good>" + GOOD_TIME_WORDS + r")\s+(?P<thing>" + GOOD_TIME_THINGS + r")(?:\s+out)?\b"
    # "today" and "tonight" are not in WHEN_DONE, which reads the other way round ("last night"),
    # so they are allowed beside it: "i had a lovely walk today" is the commonest form of all.
    r"(?:\s+(?:today|tonight)\b|\s+" + WHEN_DONE + r")?"
    r"(?:\s+with\s+[a-z][a-z' -]{1,20})?\s*[.!]?$")


# The reply names the thing back, so it is about the walk they had and not about listening in
# general. One line asks something about it; the others leave room to answer or not.
GOOD_TIME_LINES = (
    "{X} - glad it was a good one. What made it?",
    "{X} - what was the best bit?",
    "{X}, then. Those are worth having more of.",
    "Good to hear. {X} is the sort of thing a week needs.",
)


def _a_good_time_they_had(flat, memory):
    """A good time the person had, named back to them, or None."""
    match = GOOD_TIME.search(flat)
    if not match:
        return None
    said = "a " + match.group("good") + " " + match.group("thing")
    if isinstance(memory, dict):
        memory["good_time"] = {"thing": match.group("thing"),
                               "turn": len(memory.get("turns") or [])}
    return pick([line.format(X=_tidy(said)) for line in GOOD_TIME_LINES], memory)


# The detail the person adds about the good time they just had: "i had a lovely walk today" then
# "it was along the canal and the sun came out" was answered "Got it - it was along the canal and
# the sun came out", which hands their own sentence back and says nothing about it. The detail is
# the pleasant part of the day, so the reply says that the thing was worth having.
DETAIL_LINES = (
    "That is what makes {article} {thing} worth repeating, then.",
    "So it was the good sort of {thing} - the kind worth having again.",
    "Then it did what {article} good {thing} should. Keep that one.",
)


def _the_detail_of_the_good_time(flat, clean, tokens, memory):
    """The pleasant detail of the good time just named, answered about that time, or None."""
    seen = memory.get("good_time") if isinstance(memory, dict) else None
    if not isinstance(seen, dict) or not seen.get("thing"):
        return None
    # Only the turn right after, and only a line that adds something: a question is an ask, and a
    # line that turns the day round ("but then my knee went") is the trouble's, not this.
    if len(memory.get("turns") or []) != seen.get("turn", -9) + 1:
        return None
    if clean.endswith("?") or not 3 <= len(tokens) <= 30:
        return None
    if re.search(r"\b(?:but|however|though|except|apart from)\b", clean):
        return None
    if any(pattern.search(flat) for pattern in BAD_NEWS):
        return None
    thing = seen["thing"]
    article = "an" if thing[:1] in "aeiou" else "a"
    return pick([line.format(thing=thing, article=article) for line in DETAIL_LINES], memory)


# A good time they had, said as a thing they did rather than a day they had: "i had a lovely walk
# today", "we had a really nice lunch", "i had a good swim". Everything with a day or a time in it
# ("i had a good day today") is already read in bot/compose/fallback.py, which knows a good day in
# a hard week is a different line from a good day on its own, and this reader leaves those alone.
# What it takes is the thing itself, because the reply can name the thing back and the fallback's
# pools cannot: "Thanks for telling me - I'm here if you want to dig into any of that" fits any
# message at all, and the one thing the line gave was the thing that went well.
GOOD_TIME_THINGS = (
    "walk|swim|run|ride|cycle|lunch|dinner|meal|picnic|bath|shower|breakfast|coffee|nap"
    "|lie in|catch up|chat|read|game of (?:cards|chess|golf|tennis)")


GOOD_TIME = re.compile(
    r"\b(?:i|we)\s+had\s+(?:(?:a|an|such a|quite a|really)\s+)?"
    r"(?:really |properly |long |short |big |little |quiet |slow |easy )?"
    r"(?P<good>lovely|nice|great|good|brilliant|wonderful|amazing|fantastic|superb|cracking"
    r"|smashing|relaxing|fun|excellent)\s+(?P<thing>" + GOOD_TIME_THINGS + r")(?:\s+out)?\b"
    # "today" and "tonight" are not in WHEN_DONE, which reads the other way round ("last night"),
    # so they are allowed beside it: "i had a lovely walk today" is the commonest form of all.
    r"(?:\s+(?:today|tonight)\b|\s+" + WHEN_DONE + r")?"
    r"(?:\s+(?:in|at|on|round|by)\s+[a-z][a-z' -]{1,24})?"
    r"(?:\s+with\s+[a-z][a-z' -]{1,20})?\s*[.!]?$")


# The reply names the thing back, so it is about the walk they had and not about listening in
# general. One line asks something about it; the others leave room to answer or not.
GOOD_TIME_LINES = (
    "{X} - glad it was a good one. What made it?",
    "{X} - what was the best bit?",
    "{X}, then. Those are worth having more of.",
    "Good to hear. {X} is the sort of thing a week needs.",
)


# The detail the person adds about the good time they just had: "i had a lovely walk today" then
# "it was along the canal and the sun came out" was answered "Got it - it was along the canal and
# the sun came out", which hands their own sentence back and says nothing about it.
DETAIL_LINES = (
    "That is what makes {article} {thing} worth repeating, then.",
    "So it was the good sort of {thing} - the kind worth having again.",
    "Then it did what {article} good {thing} should. Keep that one.",
)


def _the_thread_is_heavy_here(memory):
    """True in a thread with a death, an emergency or a hospital stay in it."""
    try:
        return bool(fallback._the_thread_is_heavy(memory))
    except Exception:
        return False


def _a_good_time_they_had(flat, memory):
    """A good time the person had, named back to them, or None."""
    match = GOOD_TIME.search(flat)
    if not match:
        return None
    if _the_thread_is_heavy_here(memory):
        # A good walk in a week like this one is the fallback's line, which answers both halves.
        return None
    said = "a " + match.group("good") + " " + match.group("thing")
    if isinstance(memory, dict):
        memory["good_time"] = {"thing": match.group("thing"),
                               "turn": len(memory.get("turns") or [])}
    return pick([line.format(X=_tidy(said)) for line in GOOD_TIME_LINES], memory)


def _the_detail_of_the_good_time(flat, clean, tokens, memory):
    """The pleasant detail of the good time just named, answered about that time, or None."""
    seen = memory.get("good_time") if isinstance(memory, dict) else None
    if not isinstance(seen, dict) or not seen.get("thing"):
        return None
    # Only the turn right after, and only a line that adds something: a question is an ask, and a
    # line that turns the day round ("but then it poured") is the trouble's, not this.
    if len(memory.get("turns") or []) != seen.get("turn", -9) + 1:
        return None
    if clean.endswith("?") or not 3 <= len(tokens) <= 30:
        return None
    if re.search(r"\b(?:but|however|though|except|apart from)\b", clean):
        return None
    if _the_thread_is_heavy_here(memory):
        return None
    if any(pattern.search(flat) for pattern in BAD_NEWS):
        return None
    thing = seen["thing"]
    article = "an" if thing[:1] in "aeiou" else "a"
    return pick([line.format(thing=thing, article=article) for line in DETAIL_LINES], memory)


def _a_pick_is_in_hand(memory):
    """True when the chat's own last exchange was about a pick: a film, a series, a book, a gig.

    "what can i watch tonight" then "im in the mood for something funny" is a film request, and
    the joke line answered it with a pun about a scarecrow because the line names no medium of
    its own. The medium the line leaves out is the one the chat is already on.
    """
    if not isinstance(memory, dict):
        return False
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return False
    last = turns[-1]
    said = " ".join(str(last.get(key) or "") for key in ("user", "bot")).lower()
    return bool(set(re.findall(r"[a-z']+", said)) & PICK_WORDS)


# A line that names something the person is weighing up, or an annoyance they keep meeting.
# A stock ack ("Got it. Is there anything you'd like a hand with?") fits any message, which is
# exactly what makes it a bad reply: when the line names a thing, the reply is about that thing
# (STYLE.md: stay on their topic, never a stock line).
INTENTION = re.compile(
    r"\b(?:i'm|im|i am|we're|were|we are)\s+(?:thinking (?:of|about)|considering|toying with|"
    r"planning to|hoping to|looking to|keen to|meaning to)\s+(.+)$")


# "I need a cable for that" is a question someone asked, and "I have to top it up every week" is
# a fact, not a wish: only a real want counts, and only in a line that is not itself a question.
# A want is put the same way whether or not a small word stands in front of the verb - the same
# words as INTENT_RE above reads past. "Only" is left out on purpose: it is usually a limit and
# not a softener ("i only want to spend 20 quid"), so it says something the want does not.
WANT = re.compile(r"\b(?:i|we)\s+" + SOFTEN + r"(?:want|need|fancy|would like|"
                  r"'d like)\s+(?:to\s+)?(.+)$")


QUESTION = re.compile(r"^(?:ok |okay |so |and |but |well )*(?:do|does|did|can|could|should|would|"
                      r"will|is|are|was|were|what|where|when|why|how|who|which|any)\b")


# A line that asks for help or admits not knowing where to start wants an answer, not a plan
# ("hi i need help writing a cv", "i want to clear out the garage but i don't know where to
# start" - the answer module has the concrete one). Those lines are passed on.
THING_SKIP = re.compile(r"\bhelp\b|\b(?:don'?t|dont|do not) know (?:if|where|how|what|whether)\b|"
                        r"\bnot sure (?:if|whether|where|how|what)\b|"
                        r"\bwhere (?:do|should|can) i (?:start|begin)\b")


KEEPS = re.compile(r"\b(?:i|we)\s+keep\s+(\w+ing)\b\s*(.*)$")


# A kept thing that is done to somebody is about the relationship, not about a nuisance, so the
# "Annoying" reply is the wrong one for it: "i keep saying sorry to my wife" and "i keep letting
# people down" are the person minding their own conduct, where "i keep biting my cheek" is a
# nuisance and keeps the pool it had. Only a kept thing that names somebody else takes the
# second-person pool below.
KEEP_ABOUT_SOMEONE = re.compile(r"\b(?:" + "|".join(ack.facts.RELATIONS) + r")s?\b"
                                r"|\b(?:people|someone|somebody|everyone|anyone|myself|friends"
                                r"|mates|colleagues|classmates|boss)\b")


# "I keep meaning to" is an intention, not a thing that keeps going wrong.
KEEP_INTENT = frozenset("meaning wanting thinking trying hoping planning".split())


# "i keep thinking about X" is a deliberation about a thing, and the plan reply fits it ("About
# quitting your job - fair enough. What's stopped it happening so far?"). What follows a thinking
# verb when the subject is "it", or the speaker, is the thought itself, and there is no thing in it
# to get on with: "i keep thinking its me at work" was answered "Its you at work - fair enough.
# What's stopped it happening so far?", which states the doubt as a fact and then asks why they have
# not got on with it, and "i keep thinking itll go away" the same. Left to the reading a thought
# belongs to, those lines get "Going round it that many times is exhausting".
#
# A thought with a subject of its own keeps the reading it has: "i keep thinking my mum is
# disappointed in me" is about her, and taking the plan away from it only reaches the floor.
KEEP_A_BELIEF = frozenset(("thinking",))


A_THOUGHT_THAT_IS_NOT_A_THING = re.compile(
    r"^(?:it|its|it's|itll|it'll|im|i'm|ive|i've|id|i'd|everyone|everyones|everybody|nobody"
    r"|no one|people)\b")


# A bare "it" is not enough on its own: "i keep thinking its friday", "its bin day", "its 4 oclock",
# "its going to snow" are facts about the day, and standing the plan down for them hands the line to
# the worry pool, which reads any predicate as distress ("A worry at 2am is rarely the same shape as
# one in daylight" for "its friday"). What follows the "it" has to be a doubt about them or about how
# the thing ends - "its me at work", "itll go away", "its my fault" - and a fact about the day or the
# weather keeps the reading it had (emerald-carpet, #13724).
A_DOUBT_ABOUT_IT = re.compile(
    r"\b(?:me|my\b|myself|go(?:es|ne|ing)?\s+away|get(?:s|ting)?\s+better|never|"
    r"not\s+going\s+to|wont|won't|worse|worth|hopeless|pointless|too\s+late|fault|"
    r"watching|judging|noticed?|found\s+out|fail(?:ed|ing|s)?|ruin(?:ed|ing|s)?|"
    r"useless|stupid|wrong|happen(?:s|ed|ing)?\s+to\s+me|forever|for\s+good|"
    r"over|keep\s+me|stop\s+me|blow\s+over|blow\s+past|sort\s+itself\s+out|"
    r"work\s+itself\s+out|come\s+back|come\s+right|come\s+round|be\s+over|"
    r"pass\s+on\s+its\s+own)\b", re.I)


# A thought about how everyone else sees them is about the speaker whatever the predicate says.
A_THOUGHT_ABOUT_OTHERS = re.compile(
    r"^(?:everyone|everyones|everybody|nobody|no one|people)\b")


# The same thought said as a verdict on everything ("its not worth it", "it is hopeless", "its too
# late for me") is not a plan either, and standing the plan down for it leaves the floor, which
# answers an unread line with "I'm not sure about that one, sorry". A verdict on their own life is
# the heavy line, so the pool that answers "im running on empty" answers this.
A_HOPELESS_THOUGHT = re.compile(
    r"\b(?:not\s+worth|no\s+point|hopeless|no\s+hope|too\s+late)\b", re.I)


# "i need a new bath, any tips" asks for an answer with a statement in front of it.
ASK_TAIL = re.compile(r"\b(?:any tips|any advice|tips|advice)\b", re.I)


# A thing a person needs to have or use now is not a plan to start: an ambulance, a doctor, an
# inhaler, the toilet. "i need an ambulance" got *start with the smallest version of it*, which
# is the worst reply this module could give, so a body, a medicine, a clinician or the loo passes.
NEED_NOW = frozenset("""
ambulance hospital a&e ae doctor doctors gp nurse nurses paramedic paramedics 999 911 111
inhaler insulin epipen adrenaline medicine medicines meds medication tablets painkiller
painkillers prescription chemist pharmacy water drink loo toilet wee pee bathroom rest sleep
nap lie-down sickbag bucket ambulance crew
""".split())


# A medicine or a treatment is not a task to break into a smaller version: "i want to stop my
# antidepressants" got "Start with the smallest version of it, not the whole thing", which is
# advice about a project, and a course of treatment is not one. The line belongs to the health
# reading (or to the honest "I don't know"), so the plan stays out of it.
MEDICINE = re.compile(
    r"\b(?:antidepressants?|ssris?|snris?|tablets?|pills?|medication|medicines?|meds|insulin|"
    r"inhalers?|steroids?|statins?|hormones?|the pill|chemotherapy|radiotherapy|painkillers?|"
    r"antibiotics?|methadone|antipsychotics?|anti-psychotics?|lithium|beta[- ]blockers?|"
    r"blood thinners?|diazepam|tranquillisers?|tranquilizers?)\b", re.I)


# A symptom that keeps happening is for the health and knowledge modules, not for the routine
# reply: "i keep fainting" is not "i keep forgetting to water the plants".
KEEPS_SYMPTOM = re.compile(
    r"\b(?:faint|faints|fainting|fall|falls|falling|black out|blacking out|bleed|bleeds|bleeding|"
    r"throw up|throwing up|vomit|vomiting|dizzy|shaking|shake|fit|fits|seizure|seizures|"
    r"cold|colds|headache|headaches|migraine|migraines|rash|rashes|cough|coughing|wheez\w*|"
    r"pain|pains|hurting|hurts|ache|aches|aching|cramp|cramps|blister|blisters|nosebleed\w*|"
    # A tiredness that keeps coming back is the constant-tiredness answer's line, not a routine.
    r"tired|tiredness|knackered|exhausted|shattered|worn out|drained|washed out|fatigued)\b",
    re.I)


# "i want something funny to read" asks for a pick, not for a plan to start: nothing about it is
# hard to begin. The reply that helps names the choice instead.
# A time hanging off the end of a named thing is not part of it: "i fancy a curry tonight" names
# a curry, and the head is not "tonight" (which got "What kind of tonight do you usually go for?"
# for a line about a curry). The words before the time are the thing.
TIME_TAIL = re.compile(
    r"\s+\b(?:tonight|today|tomorrow|this (?:evening|afternoon|morning|weekend|week|year)|"
    r"next (?:week|weekend|month|year)|at the weekend|at some point|later on|later|soon|now)\b.*$",
    re.I)


# Words after "the" that name no thing, so a question that uses them is still a bare ask ("where
# is the best place to park" asks about a place, not about "best").
NOT_A_THING = frozenset("""best worst first last same other rest next whole only most least right
wrong near far point idea thing things way ways time times lot end start top bottom left side
kind sort bit piece one ones amount number reason chance rate rates price prices cost costs fee
fees charge charges total value balance interest worth percentage percent term length duration size
weight height depth day days week weeks month months year years hour hours minute minutes
morning afternoon evening night weekend""".split())
