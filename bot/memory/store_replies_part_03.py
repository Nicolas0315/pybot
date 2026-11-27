"""Part 3 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import forms, keywords, last_bot, last_user, name, others, resumed, stem, user
from ..memory import ack
from ..memory import condition
from ..memory import guest
from ..memory import plans
from ..memory import facts as extract
from ..knowledge.maths import solve
from ..memory.topics import STOPWORDS
from ..memory import topics as _topics
from ..memory.repeat import HEDGE as _HEDGE
from ..understanding import understand
from ..understanding.topics import PLACES
from ..memory.store_lines import (
    PRONOUN_FITS, CHILD_RELATIONS, CHILD_OF, FOOD_PHRASES, CAT_NAMES, DOG_NAMES, SMALL_NAMES,
    RESUME, WEEK, PLURAL_PEOPLE, DIET_RULES_OUT, CHILD_RELATIONS, DIET_FOOD, PERSON_GROUP,
    PLURAL_PEOPLE,
)
from ..memory.relations import (
    _a_list_of_names, _animal_family, _called, _in_the_group, _plural_person, _pronoun_for,
    _relations_of, _the_group_word,
)
from ..modules.memory_tables import (
    CALENDAR_SAID, DAY_OF_MONTH, POINTS_BACK, THAT_DATE, TIME_THING, WEEKDAY_WORD, WHEN_END_ASK,
    WHEN_END_WORD, WHEN_QUALITY, WHEN_START_ASK, WHEN_THING, WHEN_THING_VERB, WHEN_VAGUE, WHEN_VERB,
)
from bot.memory.corrected import AT_TIME, DATE_PHRASE, MONTH_WORD
from .store_replies_part_01 import (
    STOPWORDS, FOOD_HAS,
)
from .store_replies_part_02 import (
    _swapped_lines,
)


def _answer_the_new_one(memory, fixed):
    """The answer about the thing a correction swapped in, or None when there is nothing to say.

    A month or a number is a value of the fact, not a thing with an answer of its own, so
    "make that july" keeps the short note alone. More than one word of the line before can be
    the one that moved ("Portugal in june" and "A trip to Lisbon in May"), so each is tried and
    the first one the answers have something to say about is the one taken.
    """
    if isinstance(fixed, dict) and fixed.get("quiet"):
        # The note already says the thing in the sentence it was said in, so there is no line to
        # read the new value off and nothing to add (see `_an_amount_on_the_measure`).
        return None
    lines = _swapped_lines(memory, fixed)
    if not lines:
        return None
    before = memory.get("understood")
    from ..modules import answers
    from ..memory import again as same_again
    try:
        for line in lines[:4]:
            memory["understood"] = understand(line, memory)
            reply = answers.respond(line, memory)
            if not isinstance(reply, str) or not reply.strip():
                continue
            if same_again.unframed(reply):
                # The only answer the new thing has is the paragraph already on the screen, and
                # it comes back under the repeat's lead-in: "Got it — Spain on the 4th of June.
                # Same answer, and it covers this: Spain: Barcelona for a city and a beach...".
                # The note is the turn; the store does not answer itself inside it.
                return None
            return reply
    finally:
        if before is None:
            memory.pop("understood", None)
        else:
            memory["understood"] = before
    return None


def _name_fixed_this_turn(text, memory):
    """The line that says a person's name has been moved: "Dana, not Dave - got it."

    Without it the name changed quietly and the turn went to whichever module liked a word in
    the line - "no shes called dana" was answered with advice about cold callers - so the person
    had no way to know the correction had landed.
    """
    fixed = memory.get("name_fixed") if isinstance(memory, dict) else None
    if not isinstance(fixed, dict) or fixed.get("said") != " ".join(str(text or "").lower().split()):
        return None
    memory.pop("name_fixed", None)
    name = str(fixed.get("name") or "")
    before = str(fixed.get("from") or "")
    if not name:
        return None
    if before and before.lower() != name.lower():
        return "{Name}, not {Before} \u2014 got it.".format(
            Name=name[:1].upper() + name[1:], Before=before[:1].upper() + before[1:])
    return "{Name} \u2014 got it.".format(Name=name[:1].upper() + name[1:])


def _a_place_new_to_the_chat(memory, low):
    """True when the line names a place nothing said so far named."""
    named = {word.lower() for word in re.findall(r"[a-z][a-z'\-]+", " ".join(str(low or "").split()))}
    places = {word for word in named if word in PLACES or word in extract.COUNTRIES}
    if not places:
        return False
    said = " ".join(" ".join(str(line or "").lower().split())
                    for line in last_user(memory, 12))
    return not any(place in said for place in places)


def _pet_names(family):
    if family == "cat":
        return CAT_NAMES
    if family in ("rabbit", "hamster", "fish", "parrot"):
        return SMALL_NAMES
    return DOG_NAMES


def _the_pet_in_play(low, memory):
    """The animal the naming question is about: the one in the line, or the one just mentioned."""
    named = [word for word in re.findall(r"[a-z']+", low) if word in extract.ANIMALS]
    if named:
        return _animal_family(named[0])
    for turn in reversed((memory.get("turns") or [])[-3:]):
        line = str((turn or {}).get("user") or "").lower()
        said = [word for word in re.findall(r"[a-z']+", line) if word in extract.ANIMALS]
        if said:
            return _animal_family(said[0])
    pets = user(memory).get("pets") or []
    if pets and isinstance(pets[0], dict) and pets[0].get("animal"):
        return _animal_family(pets[0].get("animal"))
    return None


def _a_pet_of_theirs_is_named(low, family, memory):
    """True when the animal the naming ask points at already carries a name in the store."""
    if not re.search(r"\b(?:it|him|her|them|this one|that one)\b", low or ""):
        return False
    for pet in user(memory).get("pets") or []:
        if (isinstance(pet, dict) and pet.get("name")
                and _animal_family(pet.get("animal")) == _animal_family(family)):
            return True
    return False


def _count_of_a_kind(pets):
    """How many animals are in this group, when one of them says how many there are.

    A store can hold the same animal twice: "we have two cats, milly and fred" keeps an entry per
    name, and a later "sorry, 3 cats" moves the count onto the first of them. Adding those up
    says four. A count that was said as a correction is a total for that animal, so when one entry
    carries a number at least as big as the group, that number is the group's count.
    """
    said = [int(p.get("count") or 0) for p in pets if int(p.get("count") or 0) > 1]
    if said and max(said) >= len(pets):
        return max(said)
    return sum(int(p.get("count") or 1) for p in pets)


def _return_reply(text, memory):
    """Greet a return to an earlier topic: "ok back to the boiler", "as I was saying, Rome".

    Only when the line names a topic already talked about and asks nothing itself: "back to the
    laptop, which would you get?" carries a question, so the answer modules deal with it with the
    topic put back in front. Asking what they want to know is right here, because the person went
    back to the topic but did not say what they wanted from it.
    """
    record = resumed(memory)
    if not record or record.get("asks"):
        return None
    thing = (record.get("asked") or "").strip()
    if not thing or len(thing.split()) > 4:
        return None
    return pick([line.format(thing=_same_case(thing, text)) for line in RESUME], memory)


def _same_case(thing, text):
    """Keep a name a name: someone typing "as I was saying, Rome" gets "Back to Rome"."""
    for word in text.split():
        if word.strip(" ,.!?").lower() == thing.lower() and word[:1].isupper():
            return thing[:1].upper() + thing[1:]
    return thing


def _name_reply(memory, low=""):
    who = name(memory)
    plan = user(memory).get("plan") or ""
    if who and plan and re.search(r"\bplan(?:ning|s)?\b|\bdoing\b|\bup to\b", low):
        first, rest = plan[:1], plan[1:]
        clause = first.lower() + rest if not rest[:1].isupper() else plan
        return "You're " + who + ", and you're planning " + clause.rstrip(".") + "."
    if not who:
        # The store says which fact it asked for, so the answer is read as that fact and not as
        # whatever the wording of the line happens to look like: every "I don't know it" line is
        # the same shape, and the age ask must not open the door for a name.
        memory["asked_for"] = "name"
        return pick(["You haven't told me your name yet.", "I don't know it yet — you haven't said."],
                    memory)
    return pick(["You're " + who + ".", who + " — you told me.", "Your name's " + who + "."], memory)


def _the_day_of(plan):
    """The day the plan falls on, as somebody would answer "what day?": "on friday" -> "On Friday".

    A numbered day is a day too ("my driving test is on the 14th" -> "On the 14th."), and it is
    the day the plan holds, so it answers the same ask. "" when the plan names neither, so the
    caller can stand aside for whoever can answer the day asked for.
    """
    said = str(plan or "").lower()
    found = WEEKDAY_WORD.search(said)
    if found:
        return "On " + found.group(0).capitalize() + "."
    number = DAY_OF_MONTH.search(said)
    if number:
        return "On the " + number.group(1) + "."
    return ""


def _at_the_clock(plan):
    """The hour the plan says, as somebody would answer "what time?": "at 6" -> "At 6".

    "" when the plan carries no time of day, so the caller can say the plan itself instead: "my
    driving test is on the 14th" answers "what time is my driving test" with the day it has.
    """
    found = AT_TIME.search(str(plan or ""))
    if not found:
        return ""
    said = " ".join(found.group(0).split())
    return "At " + said[3:] + "." if said.lower().startswith("at ") else ""


def _the_day_before(plan):
    """The weekday the plan is on and the one before it, or None when it names no weekday.

    "i have a big work thing on friday" is on friday, so its prep is thursday. A weekday with a
    month or a day of the month is a date in the calendar ("friday 3 may") rather than this
    week's, and the day before it is not known from the name alone.
    """
    low = " ".join(str(plan or "").lower().split())
    found = [day for day in WEEK if re.search(r"\b" + day + r"\b", low)]
    if len(found) != 1:
        return None
    if MONTH_WORD.search(low) or DATE_PHRASE.search(low):
        return None
    day = found[0]
    return day, WEEK[WEEK.index(day) - 1]


def _the_date_behind_that(memory, low, plans):
    """"And what date is that" after the calendar has been read out is a date, not the plan.

    The pronoun points at the last thing said. Said back a plan ("You're moving to bristol in
    june"), the plan is what it means and WHEN_PLAN answers it. Said a reading of the calendar
    ("It's Saturday, 7 November."), it is the day the plan names, and what they asked for is the
    date of that day: the plan's weekday is worked out as a date ("Monday is 2 days away, on 9
    November") instead of their own news handed back. None when the last answer was not the
    calendar, or when the plan names no weekday, so the plan reading keeps those lines.
    """
    if not THAT_DATE.search(low) or not CALENDAR_SAID.search(str(last_bot(memory) or "")):
        return None
    for plan in reversed(plans):
        day = WEEKDAY_WORD.search(plan.lower())
        if day:
            worked = solve("what date is " + day.group(0), {}, memory)
            if worked:
                return worked
    return None


def _the_whole_word_in(text, word):
    """Where the word sits in the line as a word of its own, or -1.

    "when are my exams again" holds "exam", but only as the front of "exams", and the letter left
    over was read as the verb the ask named: the plan "exam on the 14th of june" came back "Your
    exam ses is on the 14th of June". The plural is the same thing said again, and the plan said
    as it is answers it.
    """
    if not word:
        return -1
    found = re.search(r"(?<![\w'])" + re.escape(word) + r"(?![\w'])", str(text or ""))
    return found.start() if found else -1


def _third_person(word):
    """The form a verb takes after "he": "start" -> "starts", "go" -> "goes", "try" -> "tries"."""
    word = str(word or "").strip(".,!?;:")
    if not word or not word.isalpha():
        return word
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("o") and len(word) > 1 and word[-2] not in "aeiou":
        # "go" is "goes" and "do" is "does", not "gos" and "dos".
        return word + "es"
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _the_line_that_said(memory, plan):
    """The recent line that carries the plan, for a plan the log kept as one of several.

    "my niece turns 5 in may and my nephew in june" logs both halves under one line, and
    `plan_line` only finds the first of them: the second half's own words are still in the line
    they said, which is where the verb it left out is."""
    wanted = " ".join(str(plan or "").lower().split())
    if not wanted:
        return None
    for line in reversed(last_user(memory, 6) if isinstance(last_user(memory, 6), list) else []):
        if wanted in " ".join(str(line).lower().split()):
            return line
    return None


def _naming_words(text):
    """The words of a line that name something, in one spelling both sides compare them in."""
    return [word for word in _topics.words(text or "")
            if word not in _topics.STOPWORDS and len(word) > 2]


def _the_day_is_the_whole_date(plan):
    """True when the day is all the plan says about when, so the day is the whole answer.

    "your exam is on the 4th of June" answered with "On the 4th." loses the month, and "your
    dentist is at 3 on Thursday" answered with "On Thursday." loses the hour: a plan with a month
    or a clock on it is said back whole, because the day alone is less than what they told us.
    """
    low = str(plan or "").lower()
    if _at_the_clock(plan):
        return False
    return not any(re.search(r"\b" + name + r"\b", low) for name in extract.MONTHS)


def _the_plan_was_just_said_back(memory, plan):
    """True when the reply above is this plan in the store's own words.

    The confirmation of a correction ("Got it - you begin your new job on Tuesday.") is the plan
    said back, so the ask that follows it wants the part it asks for rather than the sentence
    again. Only the words of the plan count: a warm word about the news, or an answer about it,
    shares nothing with the plan and leaves the plan the answer.
    """
    mine = set(re.findall(r"[a-z']+", str(plan or "").lower()))
    if len(mine) < 3:
        return False
    said = set(re.findall(r"[a-z']+", str(last_bot(memory) or "").lower()))
    return len(mine & said) >= max(3, -(-len(mine) * 7 // 10))


def _the_answer_about_it_is_on_the_screen(memory, plan, text):
    """True when the last line on the screen is the answer the plan's own line was given.

    "im training for a marathon in may" is answered out of the knowledge base with a programme, and
    "what am i doing this week" is answered by that same programme: reading the plan back with a
    question after it ("You're training for a marathon in may. What do you want to have ready for
    it?") is the plan they just said rather than the answer, and it takes the turn from the repeat.
    The plan read back is only a repeat of their own words, so it adds nothing when the answer
    already said what the line asks about - "what am i doing this week" after the training answer
    is "week", and the answer spends three runs a week.

    Three things stop it being the same answer. The answer has to be a real answer: a hedge says
    nothing to repeat, and neither does a line that asked them something back or only acknowledged
    the plan ("Got it - I have to leave for the airport at 5"). And it has to say what this ask
    names: "what am i planning" names planning, and what to see in Spain says nothing about it, so
    there the plan is still the answer.
    """
    mine = {word for word in str(plan or "").lower().split()
            if word.isalpha() and len(word) > 2 and word not in _topics.STOPWORDS}
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not mine or not isinstance(turns, list) or not turns:
        return False
    asked = set(_naming_words(text))
    if not asked:
        return False  # a bare "what am i up to" asks for the plan itself
    screen = set()
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            continue
        on_screen = str(turn.get("bot") or "").strip()
        if not on_screen:
            continue
        if _topics.only_acknowledges(on_screen):
            continue  # a courtesy between the two asks is not the answer leaving the screen
        screen = set(_naming_words(on_screen))
        break
    if not screen:
        return False
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            continue
        named = mine & set(_topics.keywords(str(turn.get("user") or "")))
        if not (len(named) >= 2 and len(named) * 2 >= len(mine)):
            continue
        answer = str(turn.get("bot") or "").strip()
        if not answer:
            continue  # the turn in hand, before anything has been said back
        if (_HEDGE.search(answer) or answer.endswith("?")
                or len(answer.split()) <= _topics.SHORT_TURN):
            return False
        if not asked & set(_naming_words(answer)):
            return False  # the answer says nothing about what this ask names
        return bool(screen) and bool(screen & set(_naming_words(answer)))


def _a_time_for_the_job_itself(low):
    """Whether the when ask is about the best time for a job rather than about their calendar."""
    for pattern in (WHEN_THING, TIME_THING):
        found = pattern.search(low)
        if not found:
            continue
        said = re.findall(r"[a-z][a-z'-]*", found.group(1))
        if said and all(word in WHEN_QUALITY for word in said):
            return True
    return False


def _thing_is_a_quality(low):
    """True when a when ask names a quality of the world and nothing of its own.

    "when is the best time to take a mortgage" names no plan of theirs; "when is the best time to
    prep for it" names nothing at all beyond a verb and a word that points back at the plan they
    told us, so that plan is still its answer.
    """
    found = WHEN_THING.search(low)
    if not found:
        return False
    said = [word for word in re.findall(r"[a-z][a-z'-]*", found.group(1))]
    if not said or any(word not in WHEN_QUALITY for word in said):
        return False
    return _names_something_of_its_own(low, found.end())


def _names_something_of_its_own(low, start):
    """Whether the rest of the line names a thing, rather than a verb and a word pointing back."""
    for word in re.findall(r"[a-z][a-z'-]*", low[start:]):
        if (word in STOPWORDS or word in WHEN_VERB or word in POINTS_BACK or word in WHEN_QUALITY
                or word in WHEN_VAGUE or len(word) < 3):
            continue
        return True
    return False


def _when_thing(low, wide=False):
    """The thing a when ask names, as a content word: "when is the wedding" -> "wedding".

    "" when there is nothing definite named ("when is the next full moon"), which keeps a
    question about the world out of the store's plans.

    `wide` reads past a vague lead word, because English puts one where the thing should be:
    "when is the *next* general election", "when is the *next* bank holiday", "when is the
    *next* leap year". Reading only the first word left the thing invisible, so the line reached
    the empty-store line ("Nothing so far - you haven't mentioned anything coming up") in front
    of an answer the bot already has. Only a content word counts, and a phrase that is still
    vague after the lead ("the next time we meet", "my next thing") gives nothing, so the asks
    about their own diary keep the store's answer. Used where nothing they told us is a plan, so
    a conversation that has plans in it is read exactly as it was.
    """
    found = WHEN_THING.search(low) or WHEN_THING_VERB.search(low)
    if not found:
        return ""
    said = keywords(found.group(1))
    if wide and said and all(word in WHEN_VAGUE for word in said):
        for word in re.findall(r"[a-z][a-z'-]*", low[found.end():])[:4]:
            words = keywords(word)
            if not words:
                continue
            if words[0] in WHEN_VAGUE:
                return ""  # "the next time we meet" is still their own diary
            said = words
            break
    for word in said:
        if word not in WHEN_VAGUE:
            return word
    return ""


def _ask_verb(low):
    """The verb the ask puts after the thing: "when does my job end" -> "end"."""
    found = WHEN_THING_VERB.search(low)
    return found.group(2) if found else ""


def _asks_the_end(low):
    """Whether the ask wants the end of the plan rather than when it happens."""
    verb = _ask_verb(low)
    return bool(verb) and stem(verb) in WHEN_END_ASK


def _asks_the_start(low):
    """Whether the ask wants the beginning of the plan."""
    verb = _ask_verb(low)
    return bool(verb) and stem(verb) in WHEN_START_ASK


def _says_the_end(plan):
    """Whether the plan's own words name its end: "i finish my course in june" does."""
    return any(word.strip(".,!?;:").lower() in WHEN_END_WORD
               or stem(word.strip(".,!?;:")) in WHEN_END_WORD for word in (plan or "").split())


def _answers_the_end_asked(plan, low):
    """Whether the plan answers the end of it the ask names: a plan that says its end answers
    "when does my holiday end", and one that says neither end can only be about the date they
    gave it. A plan the ask's own verb names ("when does my course start" against "i start my
    course in june") is about that end and answers it."""
    verb = _ask_verb(low)
    if verb and _says_the_verb(plan, verb):
        return True
    if _asks_the_end(low):
        return _says_the_end(plan)
    return not _says_the_end(plan)


def _says_the_verb(plan, verb):
    """True when the plan names that verb: "start" is in "i start my new job on monday"."""
    verb = verb.lower()
    forms = {verb, verb + "s", verb + "ing", verb + "ed"}
    if verb.endswith("e"):
        forms |= {verb[:-1] + "ing", verb + "d"}
    if verb.endswith("y"):
        forms.add(verb[:-1] + "ied")
    if verb.endswith(("s", "x", "z", "ch", "sh")):
        forms.add(verb + "es")
    for other in VERB_ALSO.get(verb, ()):
        forms |= {other, other + "s", other + "ing", other + "ed"}
        if other.endswith("e"):
            forms |= {other[:-1] + "ing", other + "d"}
    return any(word.strip(".,!?;:").lower() in forms for word in plan.split())


VERB_ALSO = {
    "start": ("begin", "began", "beginning"),
    "begin": ("start", "starts", "starting", "started", "began"),
    "end": ("finish", "finishes", "finishing", "finished"),
    "finish": ("end", "ends", "ending", "ended", "finishes", "finishing", "finished"),
}


def _yours(value):
    """The value said back with their own words turned round: "for myself" -> "for yourself"."""
    out = []
    for word in value.split():
        low = word.lower().strip(".,!?")
        out.append({"myself": "yourself", "my": "your", "me": "you", "i": "you",
                    "myself.": "yourself.", "our": "your", "us": "you"}.get(low, word))
    return " ".join(out)


def _place_phrase(place):
    """Where they work, as the line said it: "in a school", "at Tesco".

    "at" alone is followed by a name, which keeps its capital, as the job reply does for the same
    frame.
    """
    place = str(place or "").strip()
    head, _, rest = place.partition(" ")
    # Only a bare "at" names a place by its own name: "at Tesco" keeps the capital, and
    # "at the hospital" is an ordinary place, said as it was said.
    if (head.lower() == "at" and rest and rest.lower() == rest
            and rest.split()[0].lower() not in ("the", "a", "an")):
        return "at " + rest[:1].upper() + rest[1:]
    return place


def _grown_up_reply(memory):
    """Where they grew up, said as growing up rather than as where they are from."""
    known = user(memory)
    origin, city = known.get("from"), known.get("city")
    if isinstance(origin, str) and origin:
        return pick(["You grew up in " + origin + ".",
                     origin + " — that's where you grew up."], memory)
    if isinstance(city, str) and city:
        return pick(["You haven't said where you grew up — I know you live in " + city + ".",
                     "Not sure where you grew up. You mentioned " + city + " though."], memory)
    return pick(["You haven't said where you grew up yet.",
                 "I don't know that one — you haven't told me where you grew up."], memory)


def _from_reply(memory):
    """Where they are from, which is a different question from where they live now."""
    known = user(memory)
    origin, city = known.get("from"), known.get("city")
    if origin and city and origin.lower() != city.lower():
        return pick(["You're from " + origin + " originally, and you live in " + city + " now.",
                     "You said you're from " + origin + ", and you're in " + city + " now."],
                    memory)
    if origin:
        return pick(["You're from " + origin + ".", origin + " — you told me you're from there."],
                    memory)
    if city:
        return pick(["You haven't said where you're from — I know you live in " + city + ".",
                     "Not sure where you're from. You mentioned " + city + " though."], memory)
    return pick(["You haven't said where you're from yet.",
                 "I don't know that one — you haven't said."], memory)


def _is_are(who):
    return " are " if _plural_person(who) else " is "


def _eats(who):
    return " eat" if _plural_person(who) else " eats"


def _does_not(who):
    return " don't" if _plural_person(who) else " doesn't"


def _they(who):
    """The word for the person at the front of a sentence of their own: "She", "He", "They"."""
    low = str(who or "").lower().strip()
    if low in extract.SHE:
        return "she"
    if low in extract.HE:
        return "he"
    return "they"


def _their_pronoun(who):
    """The word for the person in the second half of a sentence: "for her", "for them".

    A word that is in both lists is a person either way - a mate, a friend, a colleague, a
    flatmate - and `SHE` was read first, so "my mate is teetotal" then "what can he have" ended
    "that's all I have on food for her". A word that says nothing about which it is says "them".
    """
    low = str(who or "").lower().strip()
    hers, his = low in extract.SHE, low in extract.HE
    if hers and not his:
        return "her"
    if his and not hers:
        return "him"
    return "them"


def _no_diet(who):
    """An ask about how someone else eats when nothing food-shaped is kept for them.

    Saying "you haven't told me what your dad eats" on its own is true and cold, and it is what
    someone with a diabetic dad gets. The offer is the part that helps: the fact is one line away.

    A baby is left to the weaning answers: the store keeps the age, and "my baby is 7 months what
    can she eat" is a question about that age, not about a diet the store has never heard.
    """
    if str(who or "").strip().lower() == "baby":
        return None
    return ("You haven't told me what " + (("your " + who) if who else "they") + _eats(who)
            + " \u2014 tell me and I'll plan the meals round it.")


def _a_condition_rules_out(condition):
    """Whether a condition rules a food out, by the bot's own table: coeliac is gluten.

    Only the conditions bot/memory/ack.CONDITION_FOOD knows are a food fact. A diabetic keeps
    their condition and nothing is claimed about their plate, so the store asks what they eat.
    """
    kept = condition if isinstance(condition, (list, tuple)) else [condition]
    return any(ack.CONDITION_FOOD.get(str(word).strip().lower()) for word in kept)


def _allergy_is_their_food(who, allergies, only=True, low=""):
    """What a person can eat, from the only food fact kept for them: the allergy.

    "my mum is allergic to shellfish" then "what can she eat" is a question the store can answer,
    and answering it "you haven't told me what your mum eats" tells someone the allergy they just
    gave is not food at all. The allergy is what is ruled out; nothing else is claimed.
    """
    owner = ("Your " + who) if who else "They"
    said = [str(a) for a in allergies if str(a).strip()]
    for one in said:
        named, thing = _what_the_food_has(str(low or ""), one) if low else ("", "")
        if named:
            # "is peanut butter ok for her" after "my nan is allergic to nuts" is about the
            # peanut butter: naming it answers the question, and repeating the allergy again in
            # the same words is the sentence the person has just read. The allergy is not named
            # here - "my nan cant eat dairy" is kept as an allergy, and calling that an allergy
            # back is a claim the person did not make.
            return (named[:1].upper() + named[1:] + " has " + thing + " in it, so it's off the "
                    "table for " + _their_pronoun(who) + ".")
    ruled = said[0] if len(said) == 1 else "any of " + ", ".join(said)
    tail = ("" if only else "")
    if only:
        tail = " \u2014 that's all I have on food for " + _their_pronoun(who)
    return (owner + _is_are(who) + "allergic to " + ", ".join(said) + ", so nothing with "
            + ruled + " in it" + tail + ".")


def _what_the_food_has(low, ruled):
    """The food the line names, when it is a thing the person cannot have: ("cheese", "dairy").

    "can he have cheese" after "my husband is lactose intolerant" is answered about the cheese,
    not only about dairy in general: a person asking about one food has that food in their hand.
    Only an everyday food that is that thing every time it is eaten is named, so nothing is
    claimed about a dish the store was not told the recipe of; and a food that is the ruled-out
    thing itself ("what about eggs" of a vegan's eggs) is left to the sentence that names it.
    """
    for thing in re.split(r"\s*(?:,|\bor\b|\band\b)\s*", str(ruled or "")):
        thing = thing.strip().lower()
        if not thing:
            continue
        for phrase in FOOD_PHRASES.get(thing, ()):
            if re.search(r"\b" + re.escape(phrase) + r"s?\b", low):
                return phrase, thing
        # The longest food word wins, so "peanut butter" is not answered as "peanut".
        for word in sorted(FOOD_HAS.get(thing, ()), key=len, reverse=True):
            if word == thing:
                continue
            if re.search(r"\b" + re.escape(word) + r"s?\b", low):
                return word, thing
    return "", ""


def _diet_is_their_food(who, diet, low="", plain=False):
    """What a person cannot have, from the diet kept for them, or None when the diet says it.

    "my wife is vegetarian" then "what cant she have" is the ask the allergy answer already
    works out, and with the diet kept the store can still say what it rules out. Only a named
    diet is read this way, so nothing is claimed about food the store was not told.
    """
    said = " ".join(str(low or "").lower().split())
    diet_low = " ".join(str(diet or "").lower().split())
    owner = ("Your " + who) if who else "They"
    if diet_low.startswith("no "):
        if plain:
            return None
        # "my mum doesnt eat meat" then "what cant she have": the food said as missing is the
        # answer, and saying the diet's name again would be the sentence already on the screen.
        return (owner + " can't have " + diet_low[3:] + " \u2014 that's all I have on food for "
                + _their_pronoun(who) + ".")
    ruled = DIET_RULES_OUT.get(diet_low)
    if not ruled or (plain and re.search(r",|\bor\b|\band\b", ruled[0])):
        return None
    named, thing = _what_the_food_has(said, ruled[0]) if said else ("", "")
    if named:
        # The food in their hand is the answer: "cheese has dairy in it, and your husband is
        # lactose intolerant". A diet that rules out a list ("meat, fish, dairy or eggs") is not
        # named this way, because naming one of them would answer about only the one.
        return (named[:1].upper() + named[1:] + " has " + thing + " in it, and " + owner.lower()
                + _is_are(who) + diet_low + ".")
    return (owner + _is_are(who) + diet_low + ", so nothing with " + ruled[0] + " in it"
            + ruled[1] + " \u2014 that's all I have on food for " + _their_pronoun(who) + ".")


def _other_fact(memory, key):
    """Someone else's fact the user mentioned: (who, values), or ("", []) when there is none.

    It is what stops "he is allergic to nuts" then "what am I allergic to?" being answered as
    "you're allergic to nuts": the store knows whose allergy it was.
    """
    for entry in others(memory):
        values = entry.get(key)
        if isinstance(values, list) and values:
            return entry.get("who") or "", values
    return "", []


def _last_answer(memory):
    """The bot's last knowledge answer, or "" when the previous turn was something else."""
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return ""
    last = turns[-1]
    if not isinstance(last, dict) or last.get("module") != "answers":
        return ""
    reply = last.get("bot")
    return reply if isinstance(reply, str) else ""


def _one_half_of_the_dish(food, taste):
    """True when the food the guest reader found is one half of the dish the line names.

    Only "and" and "with" make a dish out of two foods. "i dont want pasta or rice tonight" is
    two things turned down, and reading "pasta" as one half of a dish called "pasta or rice" meant
    the whole family went unanswered ("Noted: you don't want pasta or rice tonight") while a
    single "i dont like pasta" got "no pasta in anything I suggest".
    """
    if not isinstance(taste, dict):
        return False
    thing = str(taste.get("thing") or "").strip().lower()
    food = str(food or "").strip().lower()
    if not thing or not food or thing == food:
        return False
    joined = re.match(r"^(?P<one>.+?)\s+(?P<how>and|with|&)\s+(?P<two>.+)$", thing)
    if not joined:
        return False
    return bool(re.search(r"\b" + re.escape(food) + r"\b",
                          joined.group("one") + " " + joined.group("two")))


def _dislikes_here(text):
    """[(food, kind)] in the line, a taste nobody else is named for read as their own.

    The subject reader looks at the words in front of the food, so "fish isn't really my
    thing" names no subject at all (the "my" comes after it) and a bare "not a huge fan of
    mushrooms" names nobody: both are plainly the speaker's own taste, and left as "" the
    store said nothing and the greeting pool echoed the line back.
    """
    out = []
    for food, at in guest.found(text):
        kind, who = extract.subject(text, at)
        out.append((food, kind or "user"))
    return out


def _the_take_back(memory, key):
    """The last line that took the fact back, and the value it took back, or ("", "")."""
    for turn in reversed(memory.get("turns") or []):
        line = str((turn or {}).get("user") or "") if isinstance(turn, dict) else ""
        if not line.strip():
            continue
        gone = (extract.denials(line) or {}).get(key)
        if gone:
            # Said back as the fact it took, not as the words the take-back used: the store holds
            # "cutting out sugar", and a line that names only the food ("im back on sugar") would
            # otherwise be answered "You told me you stopped sugar."
            record = memory.get("denial") or {}
            if " ".join(line.split()) == str(record.get("said") or ""):
                dropped = record.get(key)
                if isinstance(dropped, list) and dropped:
                    gone = dropped[0]
                elif dropped:
                    gone = dropped
            return " ".join(line.split()), str(gone)
    return "", ""


def _said_of_someone_else(line, wanted):
    """Whether every place the line has the fact's word it is said of another person.

    "my mums budget is 100" carries the word a budget denial would deny and is not their
    budget, so quoting it back answers a question they did not ask: it has to be their own
    line or nothing, and the denial is the honest reply.
    """
    kinds = []
    for match in wanted.finditer(line):
        try:
            kinds.append(extract.subject(line, match.start())[0])
        except (ValueError, IndexError):
            return False
    return bool(kinds) and all(kind == "other" for kind in kinds)


def _diet_words(value):
    """A diet as a person would say it: "slimming world", not the store's "slimming-world"."""
    return str(value).replace("-", " ")


def _the_pronoun_is_one_of_the_two(by_who, low):
    """Whether a pronoun in the line fits one of the two people the store holds an age for.

    "how much older is she" about two sons is not a question about either of them, and answering
    it from their two ages puts a girl in the answer they never mentioned. A line with no
    pronoun at all is the pair itself, so it passes.
    """
    if re.search(r"\b(?:she|her|hers)\b", low):
        fits = extract.SHE
    elif re.search(r"\b(?:he|him|his)\b", low):
        fits = extract.HE
    else:
        return True
    return any((entry.get("who") or "").lower() in fits for entry in by_who.values())


def _pointed_at(aged, low):
    """The person an age comparison points at with a pronoun, or the last one heard of.

    A pronoun only points at a person it fits: "am i older than him" with a wife in the store is
    not a question about her, so nobody is returned and the turn stays free. With no pronoun at
    all the comparison is against the last person the store heard about.
    """
    fits = None
    if re.search(r"\b(?:she|her|hers)\b", low):
        fits = extract.SHE
    elif re.search(r"\b(?:he|him|his)\b", low):
        fits = extract.HE
    if fits:
        for entry in reversed(aged):
            if (entry.get("who") or "").lower() in fits:
                return entry
        return None
    return aged[-1]


def _diet_food(diet):
    """The food a diet rules out, or () for a diet the table does not know."""
    low = str(diet or "").strip().lower()
    if low in DIET_FOOD:
        return DIET_FOOD[low]
    if low.startswith("no "):
        # "no meat" is the limit said as the food already, so there is nothing to work out.
        return (low[3:].strip(),) if low[3:].strip() else ()
    if low.endswith(" free"):
        return (low[:-5].strip(),) if low[:-5].strip() else ()
    return ()


def _said_list(items):
    """Two things are joined with "and"; three or more take commas and a final "and".

    A bare comma between two things reads wrong in the answer: "nothing with peanuts, shellfish in
    it" looks like a typo, and "you're coeliac, lactose intolerant" argues with itself.
    """
    items = [str(item) for item in items]
    if not items:
        return ""
    if len(items) < 2:
        return items[0]
    if len(items) == 2:
        return items[0] + " and " + items[1]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _object_pronoun(who, known=None):
    """The pronoun a person takes as an object: "her", "him" or "them"."""
    said = _pronoun_for(who, known)
    return {"she": "her", "he": "him"}.get(said, "them")


def _who_the_pronoun_means(low, memory, pronoun):
    """The last person the chat named whose pronoun fits, for "whats his name".

    The store keeps the people the chat has heard of, with what it knows about each: the last one
    the pronoun fits is who a bare "his"/"her" means, the same way `_person_from_pronoun` reads
    a bare "she"/"he" in a fact.
    """
    fits = PRONOUN_FITS.get(str(pronoun or "").lower(), ())
    allowed = set()
    for key in fits:
        allowed |= set(extract.HE if key == "he" else extract.SHE)
    if not allowed:
        return ""
    people = [who for who in (user(memory).get("people") or []) if isinstance(who, str)]
    people += [str(entry.get("who")) for entry in others(memory) if entry.get("who")]
    for who in reversed(people):
        if who in allowed:
            return who
    # A role can be held by anybody, so the word for the person says nothing about their sex and
    # a tutor or a childminder was nobody a "his" or a "her" could mean. The title the chat was
    # given says it ("my tutor is called mrs owens" then "whats her name"), and with one person
    # on the table the pronoun means them whatever their word says.
    record = _topics.about(memory)
    if record is None:
        return ""
    who = str(record.get("who") or "")
    titled = ""
    for entry in others(memory):
        if str(entry.get("who") or "") != who:
            continue
        title = str(entry.get("name") or "").split(" ")[0].strip(".").lower()
        if title in extract.TITLE_GENDER:
            titled = extract.TITLE_GENDER[title]
    if titled:
        # The title says it plainly, so it settles the pronoun both ways: a "his" after "my tutor
        # is called mrs owens" is not the tutor, and is answered honestly rather than as her.
        return who if titled in fits else ""
    if who and who not in extract.SHE and who not in extract.HE \
            and len({said for said in people if said}) == 1:
        return who
    return ""


def _the_group(who):
    """The people a group word names, or nothing: "children", "childrens", "kids", "boys".

    The plural of the word and its possessive form are the same ask ("what are my childrens
    names"), and a word that names no group is left to the relation readers.
    """
    return PERSON_GROUP.get(_the_group_word(who), ())


def _in_group(who, group):
    """Whether what the store filed a person under is in a group of relations."""
    who = str(who or "").lower()
    return (who in group or CHILD_OF.get(who, "") in group
            or (who.endswith("s") and who[:-1] in group))


def _the_people(entries):
    """The people as one phrase: "daughter and son", "sons", "children"."""
    words = []
    counts = {}
    for entry in entries:
        # The word they were filed under is the word the answer uses: a "my kids are 4, 7 and 9"
        # entry says "your kids", not "your kid".
        who = str(entry.get("who") or "").lower()
        counts[who] = counts.get(who, 0) + 1
        if who not in words:
            words.append(who)
    spoken = []
    for word in words:
        if counts[word] > 1 and not word.endswith("s"):
            word += "s"
        spoken.append(word)
    return _and_list(spoken)


def _which_one_of_them(memory, who):
    """The several people a one-person word covers, when the store cannot say which is meant.

    Two names on file for the group is the case worth asking about: saying either one is a guess
    about the chat's own family, and denying the pair is denying what was said a turn before.
    With one person on file there is nothing to ask, so the caller answers with them.
    """
    group = _relations_of(who)
    mine = [entry for entry in others(memory) if isinstance(entry, dict)
            and _in_the_group(entry.get("who"), group)]
    said = []
    for entry in mine:
        names = [str(one) for one in (entry.get("names") or []) if str(one).strip()]
        if len(names) > 1:
            said.extend(_called(one) for one in names)
        elif entry.get("name"):
            said.append(_called(str(entry["name"])))
    if len(said) < 2:
        return None
    return ("You told me your " + _the_people(mine) + " are "
            + _a_list_of_names(said) + " - which one do you mean?")


def _what_the_group_is_called(group, memory):
    """The names of the people a group word covers: "Emma and Jack - your daughter and son."

    Only the people the chat was told about are named, and the ones with no name are said so: a
    group the store half knows is answered honestly rather than denied. Nothing is guessed when
    the group is empty - the caller falls through to what it did before.
    """
    mine = [entry for entry in others(memory)
            if isinstance(entry, dict) and _in_group(entry.get("who"), group)]
    if not mine:
        return None
    named = [entry for entry in mine if entry.get("name") or entry.get("names")]
    unnamed = [entry for entry in mine if not (entry.get("name") or entry.get("names"))]
    if not named:
        # "my kids are 4, 7 and 9" is several people filed as one entry, so the plural is the
        # word they were filed under as well as the count.
        many = len(mine) > 1 or any(str(entry.get("who") or "").lower() in PLURAL_PEOPLE
                                    for entry in mine)
        return ("You've told me about your " + _the_people(mine) + ", not what "
                + ("they are" if many else "he or she is") + " called.")
    said = []
    paired = False
    for entry in named:
        names = [str(one) for one in (entry.get("names") or []) if str(one).strip()]
        if len(names) > 1:
            said.extend(_called(one) for one in names)
            paired = True
        else:
            said.append(_called(str(entry.get("name") or names[0])))
    names = _and_list(said)
    if paired and not unnamed:
        # "my parents are called janet and brian" is one fact about two people: the line never
        # said which name is whose, so both are said back. Naming only the first dropped a name
        # the chat had just given ("Your parents are called Janet.").
        return "You told me your " + _the_people(mine) + " are called " + names + "."
    if not unnamed:
        if len(said) > 1:
            return names + " \u2014 your " + _the_people(mine) + "."
        return names + ", your " + _the_people(mine) + "."
    return names + ", and your " + _the_people(unnamed) + " you haven't named."


def _everyone_they_mean(memory):
    """"What are their names" after two children were named, and nothing else was: them.

    The pronoun only answers when every person the store holds is a child, so a chat with a mum
    and a son still leaves "their" unanswered rather than naming the wrong two people.
    """
    told = [entry for entry in others(memory) if isinstance(entry, dict)]
    if len(told) < 2 or not all(_in_group(entry.get("who"), CHILD_RELATIONS)
                                for entry in told):
        return None
    return _what_the_group_is_called(CHILD_RELATIONS, memory)


def _and_list(words):
    """The words as one phrase: "nuts", "mum and dad", "Meg, Dan and Sam"."""
    words = [str(word) for word in words if word]
    if len(words) < 2:
        return "".join(words)
    return ", ".join(words[:-1]) + " and " + words[-1]


def _lines_a_person_moved(memory):
    """The lines about someone whose fact a later line gave again with another value.

    The person's facts live under one `"other"` entry each (a dict), which the general moved-line
    reader skips because a dict may be a thing that grows. Here the dict is read key by key, so
    "my sister is 12" is known to be out of date once "sorry shes 14" has given the age 14.
    """
    last = {}
    moved = set()
    for entry in memory.get("facts_log") or ():
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if not isinstance(value, dict):
            continue
        who = str(value.get("who") or "").lower()
        if not who:
            continue
        text = " ".join(str(entry.get("text") or "").lower().split())
        if not text:
            continue
        for key, held in value.items():
            if key == "who" or isinstance(held, (list, dict)):
                continue
            slot = (who, key)
            older = last.get(slot)
            if older and older[0] != str(held).lower():
                moved.add(older[1])
            last[slot] = (str(held).lower(), text)
    return moved
