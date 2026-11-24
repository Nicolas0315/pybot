"""Part 4 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re

from ..understanding import lexicon, normalize

from .facts_part_01 import (
    DRINK, GAVE_UP_DRINK, GAVE_UP_DRINK_THING, NOT_DRINKING, NO_DRINK, NO_DRINK_THING, DAYS, MONTHS,
    NAME_FILLER_PHRASES, NAME_FILLER, NAME_FOLLOWERS, NAME_PLACE_WORDS, NAME_SAYS_ABOUT_ME,
    PLACE_JOIN, NAME_ASIDES, DIET_WORDS, NOT_A_NAME_FEELING, NOT_A_NAME_ILLNESS, NOT_NAMES,
    NOT_NAMES_EXTRA, SOBER_WORDS, NAMES_THAT_LOOK_LIKE_STATES, NAME_TAIL_MIN, NOT_A_NAME_STATE,
    NUMBER_WORDS, JOB_WORDS,
)
from .facts_part_02 import (
    TITLE_WORDS,
)
from .facts_part_03 import (
    SELF_JUDGEMENT, JUDGEMENT_NOUNS, ROLE_YOU_CAN_FAIL, A_TIME_INSTEAD, CHANGED_BARE, CHANGED_NOW,
    CHANGED_TO, CORRECTION_A_DATE, MOVED_BY_ITS_OWN_VERB, A_DAY_I_MEANT, A_DAY_TAKEN_BACK,
    TRIP_DATE_MOVED, CORRECTION_TAIL_WORDS, ARTICLES, CORRECTION_OPENER_WORDS,
)


def _the_drink_they_do_not_take(text):
    """What the line says they do not drink, as the word a diet says "no" to, or "".

    "i dont drink" names no drink and means alcohol - that is the idiom - and so does a drink
    given up ("ive given up drinking", "im teetotal"). A named drink counts only when it is one
    of the drinks a person gives up on purpose, so a shortfall about water stays a shortfall.
    """
    low = " ".join(str(text or "").split())
    if not low:
        return ""
    if NOT_DRINKING.search(low) or GAVE_UP_DRINK.search(low) or NO_DRINK.search(low):
        return "alcohol"
    for pattern in (NO_DRINK_THING, GAVE_UP_DRINK_THING):
        drank = pattern.search(low)
        if drank:
            thing = _finish(drank.group("thing"))
            words = [word for word in re.split(r"[ ,]+", thing.lower())
                     if word not in ("or", "and")]
            if words and all(word in DRINK for word in words):
                return thing
    return ""


# "poor" is a judgement only in front of a role: "im a poor parent" is how they feel about the
# job they are doing, and "im poor this month" is about money, which the store does keep.
SELF_JUDGEMENT_ROLE_ONLY = frozenset("poor".split())


# The relation in "im a bad mum" / "im a mum of two" is the role they are describing themselves
# in, not another person: the subject is the speaker and the relation is what they are, said with
# an article rather than "i have". "my mum is ill" and "im a nurse, and my mum is a nurse too"
# are still about a person, so only the frame straight before the word counts.
SELF_AS_A_ROLE = re.compile(
    r"\b(?:i'?m|i am|im|we'?re|we are)\s+(?:a|an|such a|such an)\s+(?:[a-z][a-z'-]*\s+)?$"
    r"|\b(?:feel|feels|felt|feeling)\s+like\s+(?:a|an|such a|such an)\s+",
    re.I)


# A word that is a judgement about themselves is one about how they are, not about a stretch of
# time: "im an awful lot better now", "im a bad week away from finishing" are not verdicts, and
# answering them with "that is a hard thing to say about yourself" reads as not listening.
NOT_A_JUDGEMENT_AFTER = (r"(?!\s+(?:lot|bit|deal|day|days|week|weekend|month|year|time|times|"
                         r"mood|thing|things|while|way|shame|pity|job)\b)")


# The judgement said rather than compared: "im a bad mum", "im an idiot", "i feel useless". The
# words alone are not enough ("i had a terrible day" is about the day), so the speaker has to be
# the subject and the word has to be what they say they are.
SELF_JUDGEMENT_SAID = re.compile(
    r"\b(?:im|i am|i feel|i felt|feeling|feel)\s+(?:like\s+)?"
    r"(?:such\s+|a bit of\s+|a bit\s+|a right\s+|a total\s+|a complete\s+|really\s+|so\s+|"
    r"just\s+|always\s+|pretty\s+|very\s+|quite\s+)*(?:a\s+|an\s+)?"
    r"(?:" + "|".join(sorted(SELF_JUDGEMENT)) + r")\b" + NOT_A_JUDGEMENT_AFTER
    + r"|\b(?:im|i am|i feel|i felt|feeling|feel)\s+(?:like\s+)?(?:a\s+|an\s+|a right\s+|such a\s+)"
    r"(?:" + "|".join(sorted(SELF_JUDGEMENT_ROLE_ONLY)) + r")\s+"
    r"(?!(?:lot|bit|day|days|week|weekend|month|year|time|times|mood|thing|things|while|"
    r"lot better|deal)\b)[a-z]+", re.I)


# The word and the noun after it: "im a bad mum", "im a bad sleeper". Which noun it is decides
# whether the line is a verdict on a role or a fact about a habit.
SELF_JUDGEMENT_ABOUT_A_NOUN = re.compile(
    r"\b(?:im|i am|i feel|i felt|feeling|feel)\s+(?:like\s+)?(?:a|an)\s+(?P<judged>"
    + "|".join(sorted(SELF_JUDGEMENT | SELF_JUDGEMENT_ROLE_ONLY))
    + r")\s+(?P<next>[a-z][a-z'-]*)", re.I)


# The word after the judgement is only a noun that qualifies it when it is not the rest of the
# sentence: "im a bad sleeper" is a habit, and "im a failure and i know it" is still a verdict on
# themselves - the word judged decides on its own there, where the line carries on in a connective
# or a preposition rather than in a noun.
JUDGEMENT_TAIL = frozenset("""and but so because though although when whenever if at in on
really tbh again today tonight now honestly actually anyway though still even too also as for
with of from to that which who""".split())


def is_a_judgement(text):
    """Whether the line is the speaker judging themselves, not telling a fact about the world.

    "im a bad mum" is not news about a mum, "im an idiot" is not a job, and neither is something
    the store should say back to them as a fact ("you said you are a bad mum" agrees with them).
    The chat answers these as feelings (bot/modules/chat.py, OWN_HARSH): this is the one reading
    the other parts share, so a judgement is never filed and never recalled as one.
    """
    low = " ".join(str(text or "").lower().replace("\u2019", "'").replace("'", "").split())
    about = SELF_JUDGEMENT_ABOUT_A_NOUN.search(low)
    if about:
        # Where the word is followed by a noun, that noun decides: "im a bad mum" is a verdict and
        # is never said back, "im a bad sleeper" is a fact about a habit and is kept.
        noun = about.group("next")
        if noun in JUDGEMENT_TAIL:
            # The line carries on in "and"/"at"/"really" rather than in a noun, so there is no
            # habit being described and the word judged is the whole verdict: "im a failure and i
            # know it" is the same line as "im a failure".
            return about.group("judged") in SELF_JUDGEMENT or about.group("judged") in ROLE_YOU_CAN_FAIL
        return noun in ROLE_YOU_CAN_FAIL or noun in SELF_JUDGEMENT or noun in JUDGEMENT_NOUNS
    return bool(SELF_JUDGEMENT_SAID.search(low))


# The words that take back the value said before them, in the shapes people say them: "im a
# teacher not a nurse", "an engineer rather than an accountant", "york instead of leeds". A fact
# said with the one it replaces in the same breath is the value in front of these words.
TAKE_BACK = (" not ", " rather than ", " instead of ")


TAKE_BACK_SPLIT = re.compile(r"\s*(?:,|;)?\s+(?:not|rather than|instead of)\b", re.I)


# "not" does two jobs. One takes a value back ("not leeds" names another place); the other
# qualifies the value in front of it ("not far from the station" says where Leeds is, and is not
# another place at all). These are the words that make it the qualifier, so a place keeps its name
# and the words after it are said instead of being thrown away.
QUALIFYING = frozenset("""
far too very that quite long much more near close nearby just only really entirely totally
always good bad great nice close
""".split())


def take_back_cut(phrase):
    """The phrase up to the words that take it back, with a qualifier's own words left in.

    "i live in york not leeds" is York, and "i live in leeds not far from the station" is the
    whole phrase: the second says where Leeds is rather than naming another place, so cutting at
    it would throw away what the person told us.
    """
    text = str(phrase or "")
    for match in TAKE_BACK_SPLIT.finditer(text):
        after = text[match.end():].split()
        if after and after[0].lower().strip(".,;:!?") in QUALIFYING:
            continue
        return text[:match.start()]
    return text


def qualified_by(phrase):
    """The qualifier said after a value ("not far from the station"), or "".

    The words are the person's own, so a reply can say them back: "Leeds, not far from the
    station" is the answer they gave, not just the name.
    """
    text = str(phrase or "")
    for match in TAKE_BACK_SPLIT.finditer(text):
        after = text[match.end():].split()
        if not after or after[0].lower().strip(".,;:!?") not in QUALIFYING:
            continue
        said = text[match.start():].strip(" ,.;:-'")
        if said:
            return said
    return ""


def _the_role(words):
    """The role in the first words of a phrase, with a joining word left off its end.

    "im a nurse on a ward" kept "nurse on a" - three words cut into the place phrase - and the
    store said that back as a job ("You're a nurse on a") which reads as a sentence cut in half. A
    role is a noun and its qualifiers ("primary school teacher", "head of sales"), so a tail of
    prepositions, articles and conjunctions is dropped rather than kept.
    """
    words = list(words[:3])
    while words and words[-1].lower().strip(".,!?") in JOB_DANGLING:
        words.pop()
    return " ".join(word.lower() for word in words)


# Words that cannot end a role: "nurse on a", "teacher at the", "driver for" are the line turning to
# something else, cut three words in, and the person's job is what is left in front of them.
JOB_DANGLING = frozenset("""a an the on at in of for with to and but so who that my our their his her
its this these those over under near across by from as""".split())


JOB_TAIL = (" in ", " at ", " for ", " with ", " who ", " that ", " and ", " but ", " so ") + TAKE_BACK


# With a place preposition the job is the place, and what follows is a shift or a day rather
# than part of it: "i work in a warehouse on the night shift" is a warehouse.
JOB_TAIL_PLACE = JOB_TAIL + (" on ", " near ", " across ", " covering ", " doing ",
                         " starting ", " starts ", " beginning ", " begins ")


# A job the person says they have changed is the job now, and the line rarely says it the way
# "i work as a nurse" does: "i changed jobs, im in a hospital now" names the new place in a
# clause of its own. Read on its own that clause could be anywhere ("im in a hospital" visiting),
# so it is only a job when the same line has said the old one is gone.
CHANGED_WORK = re.compile(r"\b(?:(?:changed|switched|left|quit|packed in|gave up|lost)\s+"
                          r"(?:my |the )?(?:job|jobs|work|role|career)\b|new job\b)", re.I)


WORK_NOW = re.compile(r"\b(?:i(?:'m| am)|im|we(?:'re| are))\s+(?:now\s+)?"
                      r"(?:working\s+)?(in|at)\s+(an?|the)?\s*"
                      r"([a-z][a-z '-]{2,30}?)\s+(?:now|these days)\b", re.I)


# When or where a person works is not what they do: "i work nights", "i work from home",
# "i work two jobs". The store keeps the line as work ("you work nights"), but a detail like
# this must never take the place of a job they have already given.
WORK_DETAIL = frozenset("""
    night nights day days evening evenings morning mornings afternoon afternoons weekend
    weekends weekday weekdays shift shifts earlies lates late early overtime flexi flexitime
    home away abroad remotely onsite hybrid
""".split())


# The words a detail is said with, which say nothing on their own: "from home", "two jobs",
# "part time", "late shifts".
WORK_DETAIL_FILLER = frozenset("""
    a an the from at in on to my two three four both all full part time times job jobs of and
    every most some
""".split())


def is_a_place_of_work(frame):
    """Whether the frame says where they work rather than what they do.

    "i work in a school" is a place told with a preposition; "i work as a nurse" and "im a
    teacher" are the work itself. `facts.extract` writes the frame, so the two are told apart
    without looking at the word: a school, an office and a bakery are all places, and what is
    inside the question "what do you do" is the role beside them.
    """
    preposition = str(frame or "").strip().split(" ")[0].lower()
    return preposition in ("in", "at", "on")


def is_a_work_detail(value, frame=None):
    """Whether what a line says about their work is only when or where it is, not what it is.

    "i work nights" says when, "i work in a school" says where; "im a nurse" says what. The
    store keeps all three, but only the what is the job, so a shift or a place never takes the
    place of a role: after "im a nurse" and "i work nights" the job is still nurse, and after
    "im a teacher" and "i work in a school" it is still teacher.
    """
    if is_a_place_of_work(frame):
        return True
    words = re.findall(r"[a-z']+", str(value or "").lower())
    meaningful = [word for word in words if word not in WORK_DETAIL_FILLER]
    if not meaningful:
        # "from home", "two jobs", "part time": nothing but the filler that says it is a detail.
        return bool(words)
    return all(word in WORK_DETAIL or word == "job" or word == "jobs" for word in meaningful)


def work_weight(value, frame=None):
    """How much a line about their work says: 3 for the role, 2 for a place, 1 for a shift.

    A role is what they do, a place is where, a shift is when, and a fuller answer never loses
    to a thinner one: "i work in a bakery" keeps the bakery when "i work nights" comes after it,
    and "im a teacher" keeps the teacher when either comes after it.
    """
    if not is_a_work_detail(value, frame):
        return 3
    return 2 if is_a_place_of_work(frame) else 1


def _finish(word):
    return word.strip().strip(".,!?;:'\"").lower()


# A word at the end that says *when*, not *what*, is no part of a name. "im a chef now" was kept
# as the job "chef now" and said back as "You told me you're a chef now", and "my car is a corsa
# now" was kept as "Corsa Now" and came back as "You drive a Corsa Now." - the same line said an
# hour earlier, without the "now", read as a different job and a different car. The moment the
# line was said belongs to the line, so it is dropped wherever a name is read.
THE_MOMENT = ("right now", "at the moment", "at present", "just now", "these days", "for now",
              "nowadays", "currently", "anymore", "any more", "already", "still", "now",
              "today", "tonight")


def without_the_moment(words):
    """The same words with the moment they were said in taken off the end.

    Only the end is touched, so "a chef in a kitchen now" keeps its kitchen, and a name that is
    nothing but the moment ("now") comes back empty for the caller to drop.
    """
    words = [word for word in words if str(word or "").strip()]
    while len(words) > 1:
        cut = 0
        for span in (3, 2, 1):
            if len(words) >= span and _finish(" ".join(words[-span:])) in THE_MOMENT:
                cut = span
                break
        if not cut:
            break
        words = words[:-cut]
    if len(words) == 1 and _finish(words[0]) in THE_MOMENT:
        return []
    return words


# Words people put round what they say, which say nothing about the thing itself: "my sister is
# called meg tbh", "i work as a nurse haha", "my budget is 300 though". The lexicon expands some
# of them before the store sees the line ("tbh" -> "to be honest"), so both shapes are listed.
# A value that ends with one of them is the value without it: nobody is called Meg To Be Honest,
# and "you're a nurse tbh" reads like a machine reading a transcript back.
TONE_TAIL = ("to be honest", "if i am honest", "if im honest", "i must say", "by the way",
             "for the record", "just so you know", "i suppose", "i guess", "to be fair",
             "haha", "hehe", "lol", "lmao", "hmm", "though", "honestly", "actually",
             "anyway", "tbf", "ngl", "imo", "tbh", "tho")


# A tail is only a tail when the line still stands without it. "my sister is called meg to be
# honest" is Meg, but "im not going to be honest" is about being honest: the phrase is what the
# verb in front of it takes, and taking it off leaves "im not going" - a different thing, said as
# if it were a fact. The same goes for a line that would end on a word that cannot end a
# sentence ("i dont like it, i have to be honest" would come back as "i dont like it, i have").
INFINITIVE = re.compile(r"\b(?:going|go|goes|went|want|wants|wanted|need|needs|needed|try|tries|"
                        r"trying|tried|mean|means|meant|promise|promised|learn|learned|learnt|"
                        r"used|rather|hope|hoping|hate|hates|love|loves|have|has|had|like|likes|"
                        r"prefer|plan|planning|planning)\s*$", re.I)


# Words that a sentence cannot end on: an auxiliary or a determiner left with nothing after it.
NOT_AN_END = frozenset("""to of and but or nor not never the a an my your his her their our its
is am are was were be been do does did has have had will would shall should can could must
may might""".split())


# "may" is the one word on that list that is also a month, and a month can end a sentence: "im
# going to york in may honestly" is a plan for May with a "honestly" after it, not a modal left
# hanging. The word in front says which one it is.
MAY_AS_A_MONTH = frozenset("""in on by from until till to before after during through for
early late mid this next last coming end start""".split())


DAY_OF_A_MONTH = re.compile(r"^\d{1,2}(?:st|nd|rd|th)?$")


def _can_end(words):
    """Whether the last word of a sentence can be the end of it ("may" is the month or the modal)."""
    if not words:
        return False
    last = words[-1].lower().strip(".,!?;:'\"")
    if last not in NOT_AN_END:
        return True
    if last == "may" and len(words) > 1:
        before = words[-2].lower().strip(".,!?;:'\"")
        return before in MAY_AS_A_MONTH or bool(DAY_OF_A_MONTH.match(before))
    return False


def no_tone(text):
    """The same words with the tone words people leave at the end taken off.

    Only the end is touched, so "i actually work in a bakery" keeps its shape, and a value that
    is nothing but tone ("haha") becomes "" so the caller can drop it.
    """
    out = str(text or "").strip()
    for _ in range(3):
        low = out.lower().rstrip(" .,!?;:")
        cut = next((phrase for phrase in TONE_TAIL
                    if low.endswith(" " + phrase) or low == phrase), None)
        if not cut:
            break
        left = out[:len(low) - len(cut)].rstrip(" ,;:-.)")
        words = left.split()
        if cut.startswith("to ") and INFINITIVE.search(" ".join(words)):
            break
        if words and not _can_end(words):
            break
        out = left
    return out if out.strip(" ,;:-.") else ""


def _date_change(text):
    """The date a plan is moved to, or None: "we moved it to july", "it's july now".

    Only a month or a day is read, because that is what a plan carries: "put it to one side"
    moves nothing. A question is not a change, so "can we move it to july?" leaves the plan
    where it is until they say they have moved it.
    """
    line = str(text or "")
    if "?" in line:
        return None
    for pattern in (CHANGED_TO, CHANGED_BARE, CHANGED_NOW, CORRECTION_A_DATE,
                    A_TIME_INSTEAD, MOVED_BY_ITS_OWN_VERB):
        found = pattern.search(line)
        if found is None:
            continue
        for group in found.groups():
            if group and _a_date(group):
                return _tidy(group)
    return None


# A day of the month is a date the same way a month or a weekday is: "sorry, it's the 4th"
# moves the appointment to a numbered day, and "the 4th of june" moves it to the day and month
# together. The ordinal ending is what says a number is a day rather than an amount, so "the 4th"
# is a date and "4" on its own stays a number.
ORDINAL_DAY = re.compile(r"(?:the\s+)?\d{1,2}(?:st|nd|rd|th)", re.I)


A_DATE_WORD = MONTHS | DAYS


# A plan's destination is put right the way its date is: "no we changed it to devon", "we moved
# it to florence", "the booking has been moved to portugal". The verb is the same one a date uses
# ("we moved it to july"), so the two are told apart by what the words after it name: a month or a
# day is the date reader's, a place is this one's.
MOVED_PLACE_TO = re.compile(
    r"\b(?:we|i|they|you|we've|weve|i've|ive|they've)\b[^.!?]{0,24}?"
    r"\b(?:changed|change|moved|move|switched|switching|swap|swapped|shifted|transferred|"
    r"rebooked|booked)\s+(?:it|that|this|the\s+booking|the\s+trip|the\s+holiday|the\s+flight)"
    r"\s+(?:to|for|instead\s+to)\s+([A-Za-z][A-Za-z' -]{1,30})", re.I)


MOVED_PLACE_PASSIVE = re.compile(
    r"\b(?:booking|trip|holiday|flight|plan|reservation|its|it's|it)\b[^.!?]{0,30}?"
    r"\b(?:has|have|had|is|its|it's|was|were|been)\s+(?:been\s+)?"
    r"(?:changed|moved|switched|swapped|shifted)\s+to\s+([A-Za-z][A-Za-z' -]{1,30})", re.I)


# The words that name no place at all, however much they look like one after a move: "we changed
# it to the other one", "we changed it to one side".
NOT_A_PLACE_NAME = frozenset("""one ones other others same thing place somewhere else front back
side left right first second third last next top bottom middle here there it that this""".split())


def a_date_put_right(text):
    """True when the line is only a date put right, with no subject of its own.

    "sorry, it's the 4th" and "its the 4th instead" say what the date is and nothing else about
    it, so the date belongs to the thing already in the air. A line that also names something of
    its own - "my exam is on the 4th" - is a date of its own and is read as one.
    """
    line = str(text or "")
    if "?" in line:
        return False
    return bool(CORRECTION_A_DATE.search(line) or A_DAY_TAKEN_BACK.search(line)
                or A_DAY_I_MEANT.search(line) or A_TIME_INSTEAD.search(line))


def the_date_put_right(text):
    """The date the line puts right: "sorry, it's the 4th" -> "the 4th", else ""."""
    line = str(text or "")
    if "?" in line:
        return ""
    for pattern in (CORRECTION_A_DATE, A_DAY_TAKEN_BACK, A_DAY_I_MEANT, A_TIME_INSTEAD):
        found = pattern.search(line)
        if found is not None:
            for group in found.groups():
                if group and _a_date(group):
                    return group.strip(" .,")
    return ""


def a_trip_date_put_right(text):
    """The date a trip is moved to by a line that says how they travel, or "".

    "im going to spain in june" / "actually we fly in september" is the plan they already gave
    us, with its month put right. The line is not a plan of its own, so the store is the only
    one that can read it: it knows whether there is a trip on record to move. A question is not
    a change, so "do we fly in september?" leaves the plan where it is.
    """
    line = str(text or "")
    if "?" in line:
        return ""
    found = TRIP_DATE_MOVED.search(line)
    if found is None:
        return ""
    for group in found.groups():
        if group and _a_date(group):
            return _tidy(group)
    return ""


def _a_date(word):
    """A month or a day: the only values a plan carries, so the only ones a change can name.

    A date is read word by word, so every way of saying one lands here: a month, a weekday, "the
    4th", "the 4th of june", "12 june". The words of a date are only those - a month or a day
    word, an ordinal day, or the "of" that joins them - so "put it to one side" and "it went to
    london" name no date and move nothing.
    """
    phrase = str(word or "").strip()
    if not phrase:
        return False
    seen = False
    a_month = False
    a_plain_number = False
    for piece in re.split(r"\s+", phrase.lower()):
        if piece in ("of", "the"):
            continue
        if ORDINAL_DAY.fullmatch(piece) or piece in A_DATE_WORD:
            seen = True
            a_month = a_month or piece in MONTHS
            continue
        if piece.isdigit() and len(piece) <= 2 and not a_plain_number:
            # A day typed as a plain number, which is how "no, 4 june" is written: it counts
            # only with a month or a day word beside it, because "4" on its own is an amount.
            a_plain_number = True
            continue
        return False
    return seen or (a_plain_number and a_month)


def _tidy(word):
    word = word.strip().strip(".,!?;:'\"")
    return word[:1].upper() + word[1:] if word else word


def _tidy_a_titled_name(word):
    """A name that starts with a title is written the way a name is: "mr smith" -> "Mr Smith".

    Only the title was capitalised in "my landlord is called mr smith", so the store said the
    surname back the way it was typed and the reply had to repair it. Repairing it here means the
    name is stored the way it is said back.
    """
    words = str(word or "").split()
    if len(words) > 1 and words[0].strip(".").lower() in TITLE_WORDS:
        return " ".join(_tidy(part) for part in words)
    return _tidy(word)


# A correction usually arrives with the preposition the fact is said with: "no, to rome instead",
# "no, in naples", "the dentist is on tuesday / no, on thursday". The value is what gets filed, so
# the preposition belongs to the sentence and not to the thing: left on, the plan read back
# "you're going to To rome in may" and the store answered "To rome" when asked where they were
# going (main kept Naples, so this is the one way a correction could make the chat worse).
A_LEAD_PREPOSITION = ("to", "in", "at", "on", "for", "into")


# ... unless the words after it are an idiom rather than a thing: "no, in fact", "no, at all",
# "no, in person" name nothing at all, so there is no value and no correction to file. A place
# that people go to ("no, at home", "no, at work") is a thing and stays.
A_LEAD_IDIOM = frozenset("""fact facts all general public advance particular least long
last once time times order case place touch person people""".split())


def _the_value_alone(phrase):
    """`phrase` without the word of apology, the shrug, or the preposition around a value.

    "no bristol sorry" names Bristol and says sorry for it, and the value on its own is what the
    store wants: left on, the apology went into the city ("Bristol sorry") and the plan read it
    back that way. Only the words that name nothing come off, and the phrase is handed back as it
    is when they are all it has ("no thanks" names nothing either way).

    The preposition in front goes the same way ("no, to rome instead" names Rome) when what is
    left of it is still a thing, and stays when it is only an idiom ("no, in fact").
    """
    words = str(phrase or "").split()
    while len(words) > 1 and words[-1].strip(".,!?;:'\"").lower() in CORRECTION_TAIL_WORDS:
        words.pop()
    if len(words) > 2 and [w.lower() for w in words[-2:]] in (["i", "mean"], ["i", "meant"]):
        words = words[:-2]
    if (len(words) > 1 and words[0].lower() in A_LEAD_PREPOSITION
            and words[1].strip(".,!?;:'\"").lower() in A_LEAD_IDIOM):
        return ""
    if (len(words) > 1 and words[0].lower() in A_LEAD_PREPOSITION
            and re.search(r"[a-z]", words[1], re.I)
            # "sorry for moaning" is an apology for a doing, not a value with "for" in front
            and not (words[0].lower() == "for" and words[1].lower().endswith("ing"))):
        words = words[1:]
    return " ".join(words)


def _tidy_apart(word):
    """The old value said beside the new one. An article in front of it stays lower case, because
    the pair is said as one sentence - "the 12th, not the 5th" - and only a name is a capital."""
    word = word.strip().strip(".,!?;:'\"")
    first, _, rest = word.partition(" ")
    if first.lower() in ARTICLES:
        return (first.lower() + (" " + rest if rest else "")).strip()
    return word[:1].upper() + word[1:] if word else word


INTRO_WORDS = ("hi", "hey", "hello", "yo", "morning", "evening", "alright", "howdy", "hullo")


# The frames a name is given in, with the words in front of it as they read once the filler is
# off: the greeting and the correcting word are filler, the frame is not.
NAME_FRAMES = ("", "im", "iam", "i'm", "i am", "i go by", "i goes by", "we go by",
               "we goes by")


def _lowercase_name_fits(text, match):
    """A name written without a capital only passes if its clause reads as an introduction:
    "hi im alex", a bare "im alex", "sorry i forgot to say, im alex". "im cold" and "im
    caught outside" are sentences about how they are, not introductions."""
    head = text[:match.start(1)]
    for mark in ".!?;":
        at = head.rfind(mark)
        if at != -1:
            head = head[at + 1:]
    head = head.lower().replace("\u2019", "'")
    for phrase in NAME_FILLER_PHRASES:
        head = head.replace(phrase, " ")
    words = [word.strip(",.!?;:'\"()") for word in head.split()]
    # Everything before the name has to be filler and the frame that carries it. "i go by kit"
    # is the same introduction as "im kit" and the whole of "i go by" is the frame, so the
    # lowercase reading has to know it: without it the frame was read as words that are not
    # filler and a name given that way was no name at all.
    left = [word for word in words if word and not _filler_or_intro(word)]
    return " ".join(left) in NAME_FRAMES


def _filler_or_intro(word):
    """Whether a word in front of a name is filler or the greeting that opens a line.

    People stretch a greeting when they are pleased to be there: "hii im dan", "heyy im
    jo", "hellooo im sam" are the same introduction as "hi im dan". The letters held are
    settled here as well, so the greeting still counts as one and the name is kept.
    """
    if word in NAME_FILLER or word in INTRO_WORDS:
        return True
    settled = re.sub(r"(.)\1+", r"\1", word)
    if settled == word:
        return False
    # "hellooo" settles to "helo" with its double l gone too, so the greeting is compared
    # with the runs squeezed on both sides: "hellooo" and "hello" are the same word held.
    return (settled in NAME_FILLER or settled in INTRO_WORDS
            or _squeezed(word) in _SQUEEZED_INTROS)


def _squeezed(word):
    return re.sub(r"(.)\1+", r"\1", word)


# The greetings people stretch, held: "hellooo", "heyyy", "hiii" all squeeze to one of these.
_SQUEEZED_INTROS = frozenset(_squeezed(word) for word in INTRO_WORDS) | {
    _squeezed(word) for word in NAME_FILLER}


# A verb said with the person as its subject ends like this: "sendin", "sortin", "leavin",
# "going", "waitin". A name can too ("justin", "martin"), so the ending on its own is not
# evidence - but a name is followed by the person saying who they are ("im dan my daughter is
# 6"), and a verb is followed by what it is being done to ("im sendin my cv off"). So the
# ending only counts against the name when the line goes on with a determiner and no verb:
# "im sendin my cv off" is not somebody called Sendin, and "im dan my daughter is 6" still is.
VERB_ISH = re.compile(r"^[a-z]{3,}(?:in|ing)$", re.I)


TAIL_DETERMINERS = frozenset("my our the a an this that some his her their".split())


def _tail_has_a_verb(words):
    """Whether a clause says something, rather than being the object of the word before it.

    The verbs an introduction carries are the ones a person says about themselves: "im dan my
    daughter is 6", and the body that hurts ("im justin my back hurts"), the thing that broke
    ("im robin my car broke down") and the day that went wrong ("im justin my boss shouted at
    me"). A guess from the ending is not safe the way it is for a name: "im packin my bags" ends
    in an s too, and the bags are what is being packed, not something the line says about the
    person. So an -s word has to be one of the verbs named here, and the -ed ending has to be
    four letters and more, because "my old shed" and "my bed" end the same way.
    """
    for word in words:
        low = word.lower()
        if low in SAYS_SOMETHING_VERBS or low.endswith("'s") or low.endswith("\u2019s"):
            return True
        if low in SAYS_SOMETHING_ELSE:
            return True
        if len(low) > 4 and low.endswith("ed"):
            # a clause about the person almost always has a past tense in it: "escaped",
            # "shouted", "started", "snapped". A plural noun is what the -s guard is for.
            return True
    return False


# The verbs that turn the words after a determiner into a clause: "im dan my daughter is 6",
# "im sam my sister lives in cork", "im robin my flat is tiny".
SAYS_SOMETHING_VERBS = frozenset("""is are am was were be been being have has had got get gets
do does did will would can could should shall may might must need needs want wants live lives
work works like likes love loves hate hates know knows say says go goes come comes died passed
lost found""".split())


# What a person says next about themselves without a helper verb: the body that hurts, the
# feeling, and the past tense of the everyday verbs that do not end in -ed and are not in the
# list above. Held as whole words, because the -s and -ed endings on their own are plurals and
# nouns as often as they are verbs ("my bags", "my old shed").
SAYS_SOMETHING_ELSE = frozenset("""hurts hurt aches ache aches bleeds bleed swells swells throbs
throb stings sting itches itch kills kill feels feel looked looks seems seems
ran fell left went came broke broke got lost found said told bought sold died ate slept hurt felt
became caught threw took gave made drove wrote saw heard thought stood sat woke quit
""".split())


def _followers_fit(text, end, name_word=None):
    """Whether the line goes on with the rest of an introduction after a name typed without
    a capital.

    An introduction ends where the name ends. "im jess" and "jess and im 34" are
    introductions; "im caught outside" and "im sat in the car" are sentences, and the word
    after the name is what says so. A new clause after a comma is not a tail, though: in
    "im sam, we are moving in june" the name ends at the comma. A capitalised name needs no such
    test: typing it with a capital is the person saying it is a name.
    """
    tail = re.split(r"[.!?;,]", text[end:], 1)[0]
    tail = _without_asides(tail)
    found = re.findall(r"[A-Za-z0-9']+", tail)
    at = 0
    while at < len(found):
        word = found[at]
        low = word.lower()
        at += 1
        if word.isdigit() or word[:1].isupper():
            continue  # an age, or a place or another name: "jess from Leeds", "jess and Tom"
        if low in NAME_SAYS_ABOUT_ME:
            if (name_word and VERB_ISH.match(str(name_word)) and low in TAIL_DETERMINERS
                    and not _tail_has_a_verb(found[at:])):
                # "im sendin my cv off": the determiner opens the object of a verb, and nothing
                # after it says anything about the person, so the word before it was the verb
                return False
            return True  # the rest of the line is the person saying who they are
        if low in NAME_FOLLOWERS:
            continue
        if low in NAME_PLACE_WORDS:
            # "jess from Leeds", "jess living in leeds": where they are is part of saying who
            # they are, so the introduction goes on through it. The place itself is one word
            # and the word in front of it may be the preposition that places it.
            if at < len(found) and found[at].lower() in PLACE_JOIN:
                at += 1
            if at >= len(found):
                return False  # "im jess from" says nothing about where
            at += 1  # the place
            continue
        return False
    return True


def _without_asides(tail):
    """The tail of an introduction with a trailing hedge taken off: "and my daughter is 6 tbh"
    keeps the clause and drops the "tbh", and " to be honest" leaves nothing at all.

    Only an aside that ends the tail is removed, so the same words inside a clause about the
    person are left alone: "im sam, i think i need a new bike" is not cut.
    """
    low = tail.lower().replace("\u2019", "'").replace("'", "")
    changed = True
    while changed and low.strip():
        changed = False
        for aside in NAME_ASIDES:
            aside = aside.replace("'", "")
            stripped = low.rstrip(" ,.!?")
            if stripped.endswith(aside):
                cut = stripped[: -len(aside)].rstrip(" ,")
                low = cut
                tail = cut
                changed = True
                break
    return tail


# Nobody is called a number. Main keeps the list the rest of the reader uses (NUMBER_WORDS,
# above), and this is the one place that did not consult it: "im forty" and "im thirty" were
# read as introductions, so a person who gave their age that way lost their own name.
def _a_state_word(low):
    """Whether the word on its own is one of the states a person describes themselves with."""
    return (low in NOT_NAMES or low in NOT_NAMES_EXTRA or low in NOT_A_NAME_FEELING
            or low in NOT_A_NAME_ILLNESS or low in DIET_WORDS or low in SOBER_WORDS)


# English says a state comes in degrees: happy, happier, happiest; sad, sadder, saddest; hungry,
# hungrier. The ending is not one of NAME_TAIL_MIN's, because "er" is a person's ending as well
# ("im peter", "im oliver", "im jasper"), so nothing stood "im happier" and "im sadder" down and
# both were kept as names. What makes a comparative safe is its stem: "happier" is a feeling
# because "happy" is one, and "peter" is a name because "pet" is nothing.
STATE_DEGREES = (("iest", "y"), ("ier", "y"), ("iest", ""), ("ier", ""),
                 ("est", ""), ("er", ""))


# A doubled last letter is the commonest typo there is, and it is safe to undo because the word
# with one letter fewer is the state the person meant: "im stuckk", "im stresssed".
def _a_degree_of_a_state(low):
    for ending, restore in STATE_DEGREES:
        if not low.endswith(ending) or len(low) <= len(ending) + 2:
            continue
        stem = low[: -len(ending)] + restore
        if _a_state_word(stem):
            return True
        # A short state doubles its last letter before the ending: sad, sadder; big, bigger.
        if len(stem) >= 3 and stem[-1] == stem[-2] and _a_state_word(stem[:-1]):
            return True
    return False


def _a_letter_too_many(low):
    if len(low) < 5 or low[-1] != low[-2]:
        return False
    return _a_state_word(low[:-1])


def _sounds_like_a_state(low):
    """Whether a lower-case word after "im" describes the person rather than naming them."""
    if low in NAMES_THAT_LOOK_LIKE_STATES:
        return False
    if _a_degree_of_a_state(low) or _a_letter_too_many(low):
        return True
    for tail, shortest in NAME_TAIL_MIN.items():
        if len(low) >= shortest and low.endswith(tail):
            return True
    return False


# The states that are not one of the endings above, asked of a closed list rather than of the
# letters: every word here is how somebody is and never what they are called. No state is two
# letters long, and the filler words people put round an introduction are ("a", "an", "so"), so
# the length keeps "im ann" a name: a letter off its run is the article "an".
def _a_word_that_is_a_state(word):
    return len(word) >= 3 and (
        word in NOT_A_NAME_STATE or word in lexicon.FEELINGS or word in lexicon.A_STATE
        or word in NOT_NAMES_EXTRA)


# How somebody looks, said the same way a name is: "she is blonde", "her name is ginger".
# None of them ends in one of NAME_TAIL_MIN's tails, so the endings cannot catch them, and none of
# them is a state either - a hair colour is not a feeling. A closed list, because these are the
# ones people say about a person in a line that is not about their name.
LOOKS_WORDS = frozenset("""
blonde blond brunette ginger redhead fair pale tanned olive freckled spotty pimply
curly straight bald bearded
""".split())


def _a_word_not_a_name(low):
    """Whether a word after "is" says how somebody is rather than what they are called.

    A name put right is read from the word after "is" ("she is rosie"), and that is also how a
    person says everything else about somebody: "she is blonde", "she is twelve", "she is
    tired", "she is married". Without this the correction reader kept Blonde as a person's name
    and said "Blonde, not Amy - got it", the same open class as "im blonde" was for the
    introduction reader. The colours and the numbers written out have no ending to catch them,
    so they are listed; the states, the conditions and the nationalities are the ones the
    introduction reader already knows by their ending or by name.
    """
    return (low in LOOKS_WORDS or low in NUMBER_WORDS
            or _sounds_like_a_state(low) or _a_word_that_is_a_state(low))


# The endings English makes a comparison with. A state takes -er and -est, and a name can carry
# the same two letters by accident (peter, heather, summer), so the stem has to be a state from
# the closed list before the word counts as one.
COMPARED = (("er", 5), ("est", 6))


def _the_state_compared(word):
    """The state a comparison is written in, or None: "happier" is happy, "sadder" is sad.

    The endings table has no room for -er and -est: it answers what a word is built with, and
    "er" is Peter's ending as much as it is a comparison's, so nothing in the name reader could
    tell "im happier" from an introduction and each of them was welcomed by name (agile-jay).
    Only a stem that is a state counts, which is what keeps "im peter" and "im heather" names.
    "happier" keeps the y it lost as an i, and "sadder" carries the doubled consonant English
    puts in front of -er, so both are put back before the stem is asked about.
    """
    for ending, shortest in COMPARED:
        if len(word) < shortest or not word.endswith(ending):
            continue
        stem = word[: -len(ending)]
        if not stem:
            continue
        for state in (stem, _with_its_y_back(stem), stem + "y", stem + "e",
                      *_a_letter_off_each_run(stem)):
            if state and _a_word_that_is_a_state(state):
                return state
    return None


def _with_its_y_back(stem):
    """The y a comparison turned into an i: "happi" is "happy", "angri" is "angry".

    English writes -ier and -iest on a state that ends in y (happy, happier, happiest), so the
    stem of the comparison is one letter off the word it was made from. Only an i is put back,
    because that is the only letter the ending ever changes.
    """
    if stem.endswith("i"):
        return stem[:-1] + "y"
    return None


def _a_letter_off_each_run(word):
    """The word with one letter taken out of each run of the same letter: "stuckk" gives "stuck".

    A held key repeats one letter, so a word typed that way is one letter too long where the key
    stuck, and every run is a place that can happen: "im stuckk", "im worrried", "im sleeeepy"
    are how they are, and each of them was answered "Nice to meet you, ...". One letter off a
    run at a time, not a run cut to one letter, because a state carries a real doubled letter of
    its own ("happy", "worried") and cutting every run would leave "hapy". A word with no run of
    two letters gives nothing back, so no name is bent by this ("im matt" is still Matt).
    """
    out = []
    at = 0
    while at < len(word):
        end = at
        while end + 1 < len(word) and word[end + 1] == word[at]:
            end += 1
        if end > at:
            out.append(word[:end] + word[end + 1:])
        at = end + 1
    return tuple(out)


def _a_state_written_as_a_comparison_or_a_double(low):
    """Whether this word is how they are, in a shape the endings table and the fixer both miss.

    `normalize.reads_as_a_feeling` asks the tables and the one-edit fixer, which between them
    see a feeling and a slip of one. Two shapes of the same word are outside both: the
    comparison ("im happier", "im saddest") and the word typed with a letter held down ("im
    stuckk"). "Nice to meet you, Happier" is the worst of them, because the false name is kept
    for the rest of the conversation and "whats my name" then answers Happier.
    """
    if normalize.reads_as_a_feeling(low) or _the_state_compared(low):
        return True
    if normalize.the_feeling_two_letters_are_gone_from(low):
        # Two letters gone from a long feeling is still how they are: "im stessd" is stressed.
        # The reading repairs it and the reply is right, and the store went on keeping the typed
        # word as the person's name, so the same turn said "Hi Stessd" and "whats my name" then
        # answered Stessd. The repair itself is fenced to a word standing on its own after the
        # be-form ("im stessd", not "my phone screen is cracked"), so it cannot take a name off a
        # word said of a thing.
        return True
    for cut in _a_letter_off_each_run(low):
        if _a_word_that_is_a_state(cut) or _the_state_compared(cut):
            return True
    return False


# The lines that say outright that the word is a name, so a word that sounds like a feeling is
# still a name there.
SAYS_A_NAME = re.compile(r"\b(?:my name is|my name's|my names|i am called|im called|"
                         r"call me|you can call me|known as)\b", re.I)


# A judgement on the speaker is how they are, never what they are called. The file already keeps
# the words people reach for when they are being hard on themselves - `SELF_JUDGEMENT` answers
# "im an idiot" and "im a hopeless cook" when the store is deciding whether a word is a job - and
# the name reader never asked it, so "im shit" was answered "Hi Shit - that's the tiredness
# talking, not the truth", and "im naff", "im muppet", "im clown", "im waste" and "im nightmare"
# were kept as names and said back for the rest of the chat. The building of a judgement is a
# judgement too: English makes "shitty" and "crappy" out of the same word with a "-y", and a
# doubled last letter is written before it ("crapp" -> "crap").
def _a_judgement_on_themselves(low):
    if low in SELF_JUDGEMENT:
        return True
    for ending in ("ish", "y"):
        if not low.endswith(ending) or len(low) <= len(ending) + 2:
            continue
        stem = low[: -len(ending)]
        if stem in SELF_JUDGEMENT:
            return True
        if stem[-1] == stem[-2] and stem[:-1] in SELF_JUDGEMENT:
            return True
    return False


def _first_tail(phrase, tails=JOB_TAIL):
    """The earliest place the job phrase stops: its position and the word it stops on.

    The order the tails are listed in says nothing about the order they come in the line, so
    "I'm a nurse and I live in Leeds" has to stop at "and", not at the "in" that follows it,
    or the job is kept as "nurse and i".
    """
    found = None
    for tail in tails:
        at = phrase.find(tail)
        if at != -1 and (found is None or at < found[0]):
            found = (at, tail)
    return found


# What a judgement word is followed by without making the phrase a job: the reason for it
# ("im a nuisance to my flatmates", "a waste of space") and when or how often the person thinks
# it ("im an idiot sometimes"). A word that names a thing straight after it is the job the noun
# describes instead: "a problem solver", "a waste engineer", "a joke writer".
JUDGEMENT_AFTER = frozenset("""to for at in of on with and but because when yet either too
about around""".split() + """sometimes today lately honestly though mostly usually always really
actually generally now these days""".split())


def _is_a_judgement_phrase(words):
    """Whether "im a <judgement noun> ..." judges the person rather than naming what they do.

    "im a doormat" and "im an idiot sometimes" are what the person thinks of themselves and must
    never be kept as their job. "im a problem solver" uses the noun to describe a job, so the
    phrase is only a judgement when nothing but when or how often comes after the noun.
    """
    if not words or words[0].lower() not in JUDGEMENT_NOUNS:
        return False
    # The noun is the phrase ("a doormat") or the second word opens the reason or says when
    # ("a waste of space", "a nuisance to my flatmates", "an idiot sometimes"). Anything else
    # straight after the noun extends it into a role: a problem solver, a waste engineer.
    return len(words) == 1 or words[1].lower() in JUDGEMENT_AFTER


def _only_discourse_before(before):
    """True when the words in front of a comma name nobody, only the way a correction opens."""
    words = re.findall(r"[a-z']+", str(before or "").lower())
    return all(word in CORRECTION_OPENER_WORDS for word in words)


def _the_correction_named_a_thing(text, match):
    """True when the noun after a correction opens the line and names a thing, not a person.

    "no, a cat" and "no, a fiesta" come after the correction's "no" and name a thing the pet and
    car readers already have; filed as a job they came back as "You told me you're a cat". A
    person comes the same way, so a noun the job lexicon knows is still their job: "what do you
    do" then "actually, a teacher" is a job, and so is "no, a nurse" after one.
    """
    if not _only_discourse_before(text[:match.start()]):
        return False  # somebody before the comma: "im jess, 28, from dublin, a nurse"
    groups = match.groups()
    phrase = ((groups[-1] if len(groups) > 2 else groups[0]) or "").strip().lower()
    words = phrase.split()
    return bool(words) and words[0] not in JOB_WORDS


# The endings a word that names a role has and a word that names a state rarely does: a plumber,
# a barrister, a dentist, a pianist, a chairman, an assistant. The lexicon is the first test and
# this is the second, because the roles people type are endless and the lexicon is not.
ROLE_ENDING = ("er", "or", "ist", "ian", "man", "woman", "ess", "ant", "ent")


# The words that take back the value said before them: "i live in york not leeds" names York, and
# the place kept was "York Not Leeds" because a name runs until a word that is not part of one, and
# "not" was not one of those words.
TAKES_ONE_BACK = frozenset(("not", "rather", "instead"))


# "i drive a corsa", "i drive an old fiesta": the car is the thing the verb takes, and it is a
# fact the store keeps under `car`. The ask side has named a car since the slot list was written
# (`_FACT_SLOT`, bot/modules/memory_store.py) and nothing ever filed one, so "what do i drive" and
# "whats my car" had nothing to read. The verb on its own is not a fact: "i drive to work", "i
# drive a lot", "i drive for a living", "i drive carefully" name a place, an amount, a job or a
# manner, and each of those is refused below.
I_DRIVE = re.compile(r"\bi (?:drive|drives|driving)\s+(?P<art>a |an |my |the )?"
                     r"(?P<what>[a-z0-9][\w'-]*(?: [a-z0-9][\w'-]*)?)", re.I)


# Words that make what follows the verb something other than a car. A manner ("carefully"), a
# place ("to work", "home"), an amount ("a lot", "200 miles") and a purpose ("for a living") are
# all things a person drives, and none of them is a thing they own. The class of the thing is not
# the thing either: "i drive a car" and "i drive my mums car" say nothing a "what do i drive" can
# be answered from.
NOT_A_CAR = frozenset("""
about across along around away back badly bargain bike bikes carefully car cars everywhere far
fast for from hard home in into like lorries lorry lots lot me message miles mine motorbike
motorbikes myself nail nowhere off on out point safely slowly somewhere stake that them there
these this those to too truck trucks up us van vans vehicle very wedge work
""".split())


# A distance or a length of time is what follows a drive: "i drive 200 miles a week".
MEASURED = frozenset("miles mile km kms kilometres kilometers hours hour mins minutes day week".split())


# "do i drive a corsa" asks rather than says, and a question states nothing to keep.
CAR_ASKED = re.compile(r"\b(?:do|does|did|should|can|could|would|will|have|has)\s+i\s+drive\b"
                       r"|\bdrive\s+a\b[^?.!]*\?", re.I)


# The car is named without the verb far more often than with it: "its a 2016 fiesta" is how
# somebody answers what they have got, and "my fiesta wont start" says whose it is. Neither
# line was filed, so the chat that had just said what the car was answered "what car was it
# again" with "you haven't told me what you drive". The name is what carries it: the words after
# the frame are read as a car only when one of them is a name from the table the car answers
# already keep (`bot/knowledge/cars.py`), which is the same table that leaves out every word that
# is also an ordinary thing (golf, focus, mini, leaf), so "my focus is on work" names no car.
CAR_NAMED = re.compile(
    r"\b(?:its|it's|it is)\s+(?:a|an)\s+(?:(?:19|20)\d\d\s+)?(?P<what>[a-z][\w'-]*(?:\s+[a-z][\w'-]*)?)"
    r"|\bmy\s+(?P<mine>[a-z][\w'-]*(?:\s+[a-z][\w'-]*)?)", re.I)


# The names, longest first, so "range rover" is read whole rather than as "range".
_CAR_NAMES = []


def _the_car_name_in(phrase):
    """The car name the phrase starts with, or "" when the words name no car."""
    if not _CAR_NAMES:
        from ..knowledge.cars import MODELS  # lazy: the facts need no table to be read
        _CAR_NAMES.extend(sorted(set(MODELS), key=len, reverse=True))
    flat = " ".join(str(phrase or "").replace("'", "").lower().split())
    for name in _CAR_NAMES:
        if flat == name or flat.startswith(name + " "):
            return name
    return ""


# "my fiesta used to do the same", "i sold my corsa last year": a car named in the past was
# theirs and is not what they drive now, so the possessive frame files nothing in a line that
# says so. The answering frame is not read this way - "its a 2016 fiesta" names the car in front
# of them however the chat got there.
CAR_IN_THE_PAST = re.compile(
    r"\b(?:used to|used it|sold|selling|sale|wrote off|written off|scrapped|traded in|part "
    r"exchanged|had|old|previous|previously|before|last car|first car|was|were|years ago)\b", re.I)


def _car_named_in_passing(text):
    """The car a line names without the verb, or None."""
    past = bool(CAR_IN_THE_PAST.search(text))
    for match in CAR_NAMED.finditer(text):
        mine = match.group("mine")
        if mine and past:
            continue
        name = _the_car_name_in(match.group("what") or mine)
        if name:
            return name
    return None
