"""Part 3 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re


from .facts_part_01 import (
    DAYS, MONTHS, NUMBER_WORDS, NOT_PLACES,
)
from .facts_part_02 import (
    DAY_AND_MONTH, CORRECTION_WHY, TAKES_BACK_THE_VALUE, MOVED_TO, MOVED_VERB, CLOCK_SAID,
    AFTER_THE_VALUE, A_DATE_VALUE, _A_SAID_NAME, _the_same_name, CORRECTION_HEDGE, CORRECTION_STALL,
    NOT_A_VALUE_START,
)


ARTICLES = frozenset("""a an the my our your his her their""".split())


# "i've got" / "ive got" with no infinitive after it is what somebody owns or has, and only the
# date on it makes it something coming up.
# "ive got to go, speak later" is a goodbye: the infinitive carries no object and the clause after
# it ends the conversation, so nothing about it is coming up.
_FAREWELL = re.compile(r"\b(?:speak|talk|chat|text|see you|see ya|catch you|bye|goodbye|later|ttyl|"
                       r"gtg|cya|night)\b", re.I)


_GOT_A = re.compile(r"\b(?:i'?ve|ive|i have)\s+got\b(?!\s+to\b)", re.I)


_GOT_TO = re.compile(r"\b(?:i'?ve|ive|i have)\s+got\s+to\b", re.I)


# A date ahead is what makes a line a plan, whatever words carry it: "i start my new job on
# monday", "my holiday is in august", "my daughter's party is next saturday". The event itself is
# open, so this reads any future-dated statement rather than a list of events.
FUTURE = re.compile(
    r"\b(?:tomorrow|tonight|this (?:weekend|week|evening|morning|afternoon|month|year|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)|next (?:week|weekend|month|year|"
    r"summer|winter|spring|autumn|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"january|february|march|april|may|june|july|august|september|october|november|december)|"
    r"(?:(?:on|by|before|until) (?:the )?(?:monday|tuesday|wednesday|thursday|friday|saturday|"
    r"sunday|\d{1,2}(?:st|nd|rd|th))|"
    r"(?:is|are) (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"(?:is|are) (?:on |in )?the \d{1,2}(?:st|nd|rd|th))|"
    r"(?:on|by|before|until) (?:the )?" + DAY_AND_MONTH + r"|"
    r"(?:is|are) (?:on )?" + DAY_AND_MONTH + r"|"
    # A date after the verb that says what comes up is a date: "my course starts december 3",
    # "the term ends 12 july". Such a line has neither "is" nor "on", so the date was read and
    # the plan was not.
    r"(?:starts?|starting|begins?|beginning|ends?|ending|finishes|finishing|opens?|closes?|due|"
    r"scheduled|booked) (?:on )?" + DAY_AND_MONTH + r"|"
    r"in (?:january|february|march|april|may|june|july|august|september|october|november|december|"
    r"the (?:summer|winter|spring|autumn|morning|afternoon|evening))|"
    r"(?:the )?(?:week|month|summer) after|at the end of the (?:week|month|year)|"
    r"later (?:this|next) (?:week|month|year)|in (?:a|\d+|a few|two|three) (?:days?|weeks?|months?))\b",
    re.I)


# A clause about what already happened is not a plan.
PAST = re.compile(r"\b(?:was|were|went|had|did|didnt|didn't|last|yesterday|ago|already|used to|back in|"
                  r"just|never|kept|used)\b", re.I)


# A report of something already done is not a plan: "i saw my mum on sunday" and "my daughter
# started school in september" are news, not what is coming up. The verb right after the person
# is what says so: it ends in -ed ("started", "booked") or it is one of the irregular ones
# ("saw", "met", "went"). A word that ends in -ed but describes how someone is ("tired",
# "excited") is not a deed, and neither is a past verb whose object is an arrangement they have
# already made ("i agreed to help on saturday", "i booked a table for friday").
PAST_VERBS = frozenset("""saw met took made got went came said told gave found thought felt knew
left ran sat stood spent paid sent held won lost ate drank drove flew slept read wrote spoke broke
chose forgot began rang phoned watched visited played finished started cleaned painted fixed
argued fought moved booked texted emailed ordered carried""".split())


PAST_ARRANGED = frozenset("""agreed promised arranged booked planned sorted organised organized
reserved scheduled offered""".split())


PAST_STATES = frozenset("""tired bored excited worried wrecked shattered interested pleased scared
annoyed confused stressed exhausted married engaged retired aged blessed wicked naked sacred
beloved rugged hundred""".split())


# What turns an -ed verb into a wish or a decision about later rather than a report: "hoped to",
# "needed to", "decided we could".
INTENTION_AFTER = frozenset(("to", "i", "we", "you", "he", "she", "they", "that"))


# The person, then their verb: "i saw", "we started", "my daughter started".
PAST_DEED = re.compile(r"^(?:ok(?:ay)?[, ]+|and |so |but |also |well |oh )*"
                       r"(?:i|we|he|she|they|(?:my|our)\s+[a-z]+)\s+([a-z']+)(?:\s+([a-z']+))?\b",
                       re.I)


def a_deed(clause):
    """Whether the clause reports something the person has already done.

    Only the verb right after the person is read, so "im excited about my holiday next week"
    (the verb is "am") and "my daughter's party is next saturday" (the verb is "is") are still
    plans, and a past verb that names an arrangement made for later is not a report.
    """
    match = PAST_DEED.match(clause or "")
    if not match:
        return False
    word = match.group(1).lower()
    if word in PAST_ARRANGED:
        return False
    if word in PAST_VERBS:
        return True
    if word.endswith("ed") and len(word) >= 5 and word not in PAST_STATES:
        # An -ed verb that opens a clause of its own is an intention said in the past tense, not
        # something done: "i hoped to start my course in september", "i decided to go to rome in
        # may", "i hoped we could meet on monday" are all still ahead of them. The irregular past
        # forms are deeds whatever follows: "i went to see my mum on friday".
        return (match.group(2) or "").lower() not in INTENTION_AFTER
    return False


# The plan has to be the person's own business, in their own voice.
OWN = re.compile(r"^(?:ok(?:ay)?[, ]+|and |so |but |also |well |oh )*"
                 r"(?:i|i'm|im|i've|we|we're|were|we've|weve|my|our|me)\b", re.I)


# A plan is the person's own week, not something they say to the bot: "i'll call you tomorrow".
SECOND_PERSON = re.compile(r"\b(?:you|your|you're|u|ur|yours)\b", re.I)


# A line that says what is not happening, or how today feels, is not a plan.
NEGATED = re.compile(r"\b(?:cant|can't|cannot|dont|don't|doesnt|doesn't|wont|won't|not|never|no)\b", re.I)


# Words that say the next word is a thing, not a verb: "going to the gym" is not "going to visit".
DETERMINERS = frozenset("""a an the my our his her their your some any this that these those
one two three""".split())


# The words before a plan verb that make the line a question about the plan, not a plan.
ASKED_BEFORE = re.compile(r"\b(?:what|when|where|which|remind me|tell me)\b", re.I)


# A question is about the plan, not a plan.
# People leave the apostrophe out of the question word as often as not, and "whats my plan for
# saturday" was read as a plan of its own: kept as "whats my plan on Saturday" and said back as
# "You're planning to whats my plan on Saturday." One optional tail on the wh-word is enough for
# every shape of it they type ("whats", "what's", "hows", "wheres", "whens", "whos") and the word
# boundary after it keeps a longer word ("whatsoever") out.
ASKING = re.compile(r"\b(?:what|when|where|which|who|why|how)(?:'s|s|'re|re)?\b|"
                    r"\b(?:should|shall|can|could|would|do|does|did|is|are|was|will|any)\b", re.I)


CORRECTION = re.compile(
    r"(?:\b(?:sorry,?\s*)?(?:no,?\s+)?(?:i\s+meant|i\s+mean)"
    r"|^(?:\s*(?:ok|okay|actually|sorry|no|oh)[, ]+)*make\s+that)\s+(?:it'?s\s+|its\s+)?"
    r"([£$\u20ac]?\s?[a-z0-9][a-z0-9 '£$\u20ac-]{0,30}?)"
    r"(?:,?\s+not\s+([a-z0-9][a-z0-9 '-]{0,30}?))?"
    r"(?:\s+instead|[,.]|$|(?=" + CORRECTION_WHY + r"))",
    re.I)


# The pair is often said with a verb in front of it: "actually weve got 900 not 1500, the boiler
# just went" is the same correction as "actually 900 not 1500", and read without it the line named
# no value at all, so the 1500 stayed on record. Only the words that carry the fact - what a
# person has, or has got - are allowed between, so the marker is still what marks the correction.
CORRECTION_PAIR = re.compile(
    r"\b(?:sorry|no|actually|oops)[, ]+"
    r"(?:(?:it'?s|its|it\s+is|that'?s|thats|that\s+is)\s+)?"
    r"(?:(?:i|we|you|they|he|she)\s*(?:'ve|ve|have|had)\s*(?:got\s+|get\s+|now\s+)?)?"
    r"((?:the\s+)?[a-z0-9][a-z0-9'-]{1,20}(?: [a-z0-9][a-z0-9'-]{1,15})?),?\s+"
    + TAKES_BACK_THE_VALUE + r"\s+"
    r"((?:the\s+)?[a-z0-9][a-z0-9'-]{1,20}(?: [a-z0-9][a-z0-9'-]{1,15})?)"
    r"(?:\s+instead\b|\s*[-,.;!?]|$)", re.I)


# "make that 4", "make it the 15th", "change it to friday": the value goes back up for a second
# go with no verb that names what is being corrected. The line has to start with it (or with the
# "no"/"sorry" that marks a correction), so "i make it 4" - an estimate - is not a correction.
CORRECTION_MAKE = re.compile(
    r"^\s*(?:(?:no|nope|sorry|actually|oops|ok|okay)[,.]?\s+)?"
    r"(?:make\s+(?:that|it)|change\s+(?:that|it)\s+to|switch\s+(?:that|it)\s+to)\s+"
    r"((?:the\s+)?[a-z0-9][a-z0-9 '£$\u20ac-]{0,25}?)"
    r"(?:,?\s+(?:please|then|instead|actually|now))?\s*[.!?]?\s*$", re.I)


# "no, I said 700": the person says the value again with "I said" in front of it. It is the same
# move as "I meant", in the words people reach for when the first go was simply wrong, and the
# "no"/"sorry" in front is what marks it as a correction rather than something they said once.
CORRECTION_SAID = re.compile(
    r"\b(?:no|nope|sorry|actually|oops)[,.]?\s+(?:i\s+said|i\s+did\s+say|i\s+actually\s+said|"
    r"i\s+meant\s+to\s+say)\s+(?:it'?s\s+|its\s+)?([a-z0-9][a-z0-9 '-]{0,30}?)"
    r"(?:,?\s+not\s+([a-z][a-z '-]{1,30}?))?(?:\s+instead|[,.]|$)", re.I)


CORRECTION_MOVED = re.compile(
    r"(?:"
    # "i got it moved to thursday", "they've had the appointment changed to friday": the thing
    # that moved comes before the verb, because it is the one they already told us about.
    r"\b(?:got|had|get|have|has)\s+(?:it|that|this|them|the\s+[a-z]+)\s+" + MOVED_VERB + MOVED_TO +
    r"|"
    # "it's been moved to thursday", "its moved to the 4th": the thing that moved is the subject
    # of a passive, so the line points back with "it" and nothing else. A bare "they"/"she's" is
    # not a pointing back: "i live in bristol / she's moved to manchester" is news about her, and
    # reading it as a correction of where the person lives moved a fact they never changed.
    r"\b(?:it'?s|its|it\s+is|it\s+was|it\s+has|they'?ve|they\s+have|"
    r"has\s+been|have\s+been|had\s+been|been)\s+" + MOVED_VERB +
    r"(?:\s+(?:it|that|this|them))?" + MOVED_TO +
    r"|"
    # "they moved it to thursday", "she moved it to saturday", "the hospital moved it to the
    # 10th": someone else did the moving, and the thing they moved is named as "it".
    r"\b(?:they|he|she|we|i|the\s+[a-z]+)\s+" + MOVED_VERB +
    r"\s+(?:it|that|this|them)" + MOVED_TO +
    # "its now on thursday", "the scan is now on the 4th": the new time said as where the thing
    # sits, which is how a moved appointment is usually put.
    r"|\b(?:it'?s|its|it\s+is)\s+now\s+(?:on|for)\s+"
    r")"
    r"((?:the\s+)?[a-z0-9][a-z0-9 ':-]{0,25}?)"
    # A time that was moved is rarely said on its own: the reason follows it in the same breath
    # ("we moved it to sunday because of the football", "they pushed it to friday as we're
    # away"). The value is the time before that clause, or the line reads as no correction at
    # all and the move is answered as if it were news.
    r"(?:\s+(?:because|cos|cause|coz|due|since|so|as|seeing|what\s+with)\b"
    r"|\s+instead|[,.;!?]|$)", re.I)


# The value a correction says on its own ("2pm", "at 8pm").
CLOCK_VALUE = re.compile(r"^(?:the\s+|at\s+)?(" + CLOCK_SAID + r")$", re.I)


# The clock a plan already says. A plan's own clock is often written without am or pm ("dinner at
# 8"), and that hour is still the one a correction names, so the word in front of the figure is
# what makes it a clock here.
CLOCK_IN_PLAN = re.compile(
    r"(?<![\d.:])(?:" + CLOCK_SAID + r")"
    r"|(?<=\bat )\d{1,2}(?![\d:.,a-z%])", re.I)


def a_clock_time(phrase):
    """The clock time a phrase is, said the way the person said it ("2pm", "noon"), or "".

    Only a time nothing else can read as counts. A bare figure is not a clock ("make it 8" has
    no am or pm on it and may be any number a plan holds), and neither is a price: "8.30" is a
    minute on the clock only when an hour and a whole minute are written against each other and
    am or pm says which half of the day it is in.
    """
    match = CLOCK_VALUE.match(" ".join(str(phrase or "").split()))
    return match.group(1) if match else ""


def the_clock_in(text):
    """The clock a plan says, as the match to replace, or None."""
    return CLOCK_IN_PLAN.search(str(text or ""))


def a_moved_time(phrase):
    """True when a phrase is a time a plan can be moved to: a day, a month, a date or a clock.

    A thing can be moved to something that is not a time - "they changed it to a cheaper
    tariff", "its now on the table" - and that is a fact about the thing, not a time taken back.
    Only the three shapes a time is said in make the line a correction of a plan.
    """
    words = [word for word in re.split(r"[^a-z0-9]+", str(phrase or "").lower()) if word]
    if not words:
        return False
    if any(word in MONTHS or word in DAYS for word in words):
        return True
    if a_clock_time(phrase):
        return True  # "they moved it to 2pm" moves the clock of the plan, not its day
    # "the 10th", "the 12th of june", "12 june": a date is a number the month or the ordinal
    # makes one, so a bare number is only a date when nothing else in it is a word.
    return bool(DATE_VALUE.fullmatch(str(phrase or "").strip())) or bool(
        re.fullmatch(r"(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?", str(phrase or "").strip(), re.I))


def _a_day_taken_back(text):
    """The day the line puts right, as a correction: "sorry saturday i got the day wrong".

    The value is the day, which is what the shapes for a moved time carry, so the store puts a
    plan's day to it rather than filing a plan of its own.
    """
    return A_DAY_TAKEN_BACK.search(text) or A_DAY_I_MEANT.search(text)


def _a_moved_time(text):
    """The moved-time correction in the line, when what it moves to is a time.

    The shape says something was moved; only the value says it was moved to a time, and that is
    what makes the line a correction of a plan. `a_moved_time` is the value's side of it.
    """
    for moved in CORRECTION_MOVED.finditer(text):
        if a_moved_time(moved.group(1)):
            return moved
    return None


# "no, 4 times not 3 times": the same side-by-side shape with a number and its unit on each
# side. The numbers carry the meaning, so the words after them are optional.
CORRECTION_NUMBER_PAIR = re.compile(
    r"\b(?:sorry|no|actually|oops)[, ]+(\d+(?:\.\d+)?(?:\s+[a-z]+)?)\s+"
    + TAKES_BACK_THE_VALUE + r"\s+"
    r"(\d+(?:\.\d+)?(?:\s+[a-z]+)?)(?:\s+instead|[,.]|$)", re.I)


# "we moved it to july": the date of a plan is moved, and the plan itself is pointed at ("it",
# "the booking", "our trip") rather than named. People say the new date and leave the old one
# out, because the plan already holds it.
CHANGED_TO = re.compile(
    r"\b(?:we|i|they)(?:\s*'?ve|\s+have|\s+had)?\s+"
    r"(?:moved|changed|pushed|shifted|switched|brought|put|bumped|made)\s+"
    r"(?:it|that|this|the\s+[a-z]{2,15}|our\s+[a-z]{2,15}|my\s+[a-z]{2,15})\s+"
    r"(?:back\s+|forward\s+|on\s+)?(?:to|until|for)\s+"
    + A_DATE_VALUE + AFTER_THE_VALUE, re.I)


# The same move said with no subject: "make it july", "change it to august". A question is not
# a change ("can we move it to july?"), so the reader refuses a line with a question mark.
CHANGED_BARE = re.compile(
    r"^\s*(?:(?:ok|okay|right|well|so|and|actually|no|sorry|oh)[, ]+)?"
    r"(?:make|change|move|push|put|shift|bring)\s+"
    r"it\s+(?:to\s+)?" + A_DATE_VALUE + AFTER_THE_VALUE, re.I)


# A change of date said with no verb at all: "its actually july", "its july instead". The
# "actually" or the "instead" is what makes it a correction rather than a fact about the world,
# so "its july" on its own states something else and is left alone. A bare "now" is not enough:
# "its monday now" is someone remarking on the day they are having, and reading it as "move the
# exam to Monday" put an exam a week earlier than the person had said it.
CHANGED_NOW = re.compile(
    # "its actually july", "its actually on saturday": the "actually" is the marker.
    r"^\s*(?:it'?s|its|that'?s|thats)\s+(?:actually|really)\s+"
    r"(?:(?:on|in|at)\s+)?([a-z]{3,10})(?:\s+now)?\s*[.!?]?\s*$"
    # "its saturday instead", "its on saturday instead".
    r"|^\s*(?:it'?s|its|that'?s|thats)\s+(?:(?:on|in|at)\s+)?([a-z]{3,10})\s+instead"
    r"(?:\s+now)?\s*[.!?]?\s*$"
    # The correction word in front is the marker, and a day is said with its "on" as often as
    # without: "no, its on thursday" after "the dentist is on tuesday" is the same correction as
    # "no, thursday", and neither read the day before. The "it's" is optional here for the same
    # reason: "sorry, on saturday" is what people say when the thing is already in the air.
    r"|^\s*(?:(?:ok|okay)[,.]?\s+)?"
    r"(?:(?:no|nope|sorry|wait|ah|oh|oops|hold\s+on|hold\s+up|hang\s+on|hmm|um+|erm+|well)"
    r"[,.]?\s+){1,3}"
    r"(?:(?:it'?s|its|that'?s|thats)\s+)?(?:actually\s+|really\s+)?"
    r"(?:(?:on|in|at)\s+)?([a-z]{3,10})(?:\s+now)?\s*[.!?]?\s*$", re.I)


# A date put right with no subject of its own: "sorry, it's the 4th", "no, the 4th of june",
# "actually the 4th instead". The marker in front is what makes it a correction rather than a
# date about something else, and the value has to be a date, so "no its fine" and "sorry, the
# dog" put nothing right. People say it this way when the date they gave was simply wrong.
CORRECTION_A_DATE = re.compile(
    r"^\W*(?:(?:ok|okay|right|so|and|no|nope|sorry|actually|oops|wait|oh|hmm)[,.]?\s+)+"
    r"(?:(?:it'?s|its|it\s+is|that'?s|thats|the\s+date\s+is)\s+)?"
    r"(?:(?:now|on|for)\s+)?"
    + A_DATE_VALUE + AFTER_THE_VALUE, re.I)


# A day put right in the words people use when they got the day wrong. `CORRECTION_A_DATE` wants
# the line to be nothing but the date, and these two shapes are not: the day comes with the reason
# after it ("sorry saturday i got the day wrong") or with "now" after it ("actually its sunday
# now because of the football"). Left unread, the day they took back is the day that answers:
# "when is it again" said "On Friday" over a dinner they had just moved to Sunday.
#
# The day has to be the thing the line puts up, so a day that starts a clause of its own is not a
# correction - "no saturday is the football", "actually sunday was lovely" are about the day and
# not a new answer for the plan. The reason after the day is what makes the first shape one at
# all: "sorry saturday" on its own is an apology about a day, not a date put right.
A_DAY_TAKEN_BACK = re.compile(
    r"^\W*(?:(?:ok|okay|right|so|and|no|nope|sorry|actually|oops|wait|oh|hmm)[,.]?\s+)+"
    r"(?:(?:it'?s|its|it\s+is|make\s+it)\s+)?"
    r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    r"(?!\s+(?:is|was|are|were|and|or|but)\b)"
    r"(?:\s+(?:now|instead)\b"
    r"|[,.]?\s*(?:i\s+(?:got|had|put)\s+(?:the|that)\s+day\s+wrong|wrong\s+day|"
    r"my\s+mistake|i\s+was\s+wrong|im\s+wrong|silly\s+me|\s+i\s+meant\b))", re.I)


# The day said with the words people use when they got it wrong in front of it: "sorry i meant
# friday", "no i mean sunday", "i said thursday". The shapes above put the reason after the day
# ("sorry saturday i got the day wrong") or the word "instead"; the way most people correct a day
# is to say "i meant" and then the day, and that line was read as nothing at all:
#
#     i got the job and i start thursday / sorry, i meant friday
#       before  On Thursday.   (the day they had just taken back)
#       after   On Friday.
#
# The marker in front is still needed, so "i meant it" and a line that means something else about a
# day ("i meant to ring on monday") are not a date put right.
A_DAY_I_MEANT = re.compile(
    r"^\W*(?:(?:ok|okay|right|so|and|no|nope|sorry|actually|oops|wait|oh|hmm)[,.]?\s+)+"
    r"i\s+(?:meant|mean|said|was\s+thinking)\s+"
    r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    r"(?!\s+(?:is|was|are|were)\b)", re.I)


# The same date said only as the thing that replaces the old one: "its the 4th instead". With no
# marker in front, the "instead" is the whole of what makes it a correction, so it is required.
A_TIME_INSTEAD = re.compile(
    r"^\W*(?:it'?s|its|that'?s|thats)\s+"
    + A_DATE_VALUE +
    r"\s+instead\b" + AFTER_THE_VALUE, re.I)


# The date moved by saying what the thing does now: "actually it starts tuesday", "the move
# slipped to september", "it got pushed back to the 4th". Only the verbs a date moves with are
# read, and the value still has to be a date: "it went to london" moves nothing, and "it is red"
# is not a change of anything.
MOVED_BY_ITS_OWN_VERB = re.compile(
    r"\b(?:it|that|this|the\s+[a-z]{2,15}|our\s+[a-z]{2,15}|my\s+[a-z]{2,15})\s+"
    r"(?:(?:has|have|had|got|was|is|been)\s+)?"
    r"(?:starts?|started|slips?|slipped|moves?|moved|pushes?|pushed|changes?|changed|"
    r"shifts?|shifted|lands?|landed|happens?|puts?)\s+"
    r"(?:back\s+|forward\s+|on\s+|to\s+|until\s+|for\s+)?"
    + A_DATE_VALUE +
    r"(?:\s+instead)?\s*[.!]?\s*$", re.I)


# The trip they already told us about, said again with a new date and none of the "moved" words:
# "actually we fly in september", "no we're going in august now", "sorry we go in june". The
# going verb is what makes this a trip and not a date on its own, and a marker in front is what
# makes it a change: "we fly in september" says a trip, not that an earlier one moved. A date at
# the end is still only read when it is one, so "actually we fly in a bit" moves nothing.
TRIP_DATE_MOVED = re.compile(
    r"^\W*(?:(?:ok|okay|right|well|so|and)[,.]?\s+)?"
    r"(?:(?:no|nope|sorry|actually|oops|wait|ah|oh|hmm)[,.]?\s+){1,3}"
    # "we're" typed as "were", "i'm" as "im": chat-speak drops the apostrophe, and the
    # subject still has to be there or "no flying in september" is a plan, not a move.
    r"(?:(?:we|were|i|im|they|theyre|he|hes|she|shes)\s*(?:'re|'ve|'ll|'m|'s|\s+are|"
    r"\s+have|\s+had|\s+will)?\s+)?"
    r"(?:fly|flies|flying|go|goes|going|leave|leaves|leaving|head|heading|"
    r"travel|travelling|traveling|drive|driving|sail|sailing|arrive|arriving)\b"
    r"[^.!?]{0,40}?"
    r"\b(?:in|on|for)\s+"
    + A_DATE_VALUE +
    r"(?:\s+(?:now|instead))?\s*[.!]?\s*$", re.I)


# "sorry, not peanuts": the value taken back with nothing put in its place. The "no"/"sorry" in
# front is what makes it a correction rather than part of the fact, so "i'm not allergic to
# peanuts" states something else and is left alone.
# "no, not today", "sorry, not now", "not again": a refusal of the moment, not a value that goes.
NOT_A_DAY = frozenset("""today tonight tomorrow now anymore yet again either neither even sure
really quite very much bad good great one""".split())


CORRECTION_NOT = re.compile(
    r"\b(?:sorry|no|nope|actually|oops)[, ]+not\s+(?:the\s+)?([a-z][a-z'-]{1,20}"
    r"(?: [a-z][a-z'-]{1,15})?)(?:\s+instead\b|\s*[-,.;!?]|$)", re.I)


# "take that back", "scratch that", "strike it out": the last thing they said goes and no value is
# named, so the store is the only place that can undo it. Only phrases that can mean nothing else
# are here: "forget that" and "never mind" also change the subject, and the understanding lane
# reads those, so a retraction must not take those turns.
RETRACT = re.compile(
    r"^\W*(?:(?:ok|okay|no|nope|sorry|actually|wait|oh|hmm|um|yeah)[,.]?\s+)*"
    r"(?:take|taking)\s+(?:that|it|this)\s+back\b(?:\s+(?:then|please|sorry|yeah))?\W*$"
    r"|^\W*(?:(?:ok|okay|no|nope|sorry|actually|wait|oh|hmm|um|yeah)[,.]?\s+)*"
    r"(?:scratch|strike|disregard|ignore|undo|delete)\s+(?:that|it|this)\b"
    r"(?:\s+(?:out|then|please|yeah))?\W*$"
    r"|^\W*(?:(?:ok|okay|no|nope|sorry|actually|wait|oh|hmm|um|yeah)[,.]?\s+)*"
    r"forget\s+(?:what\s+)?i\s+(?:just\s+)?(?:said|told you)\b\W*$", re.I)


# "not lisbon, porto", "not lisbon - porto instead": the value they want is said after the one they
# are taking back. The line is a correction, not a bare take-back: the old value is replaced, so the
# plan (or the place) keeps everything else it said and only that word moves.
CORRECTION_NOT_TO = re.compile(
    r"\b(?:sorry|no|nope|actually|oops)[, ]+not\s+(?:the\s+)?"
    r"([a-z][a-z'-]{1,20}(?: [a-z][a-z'-]{1,15})?)\s*(?:,|;|-|\u2013|\u2014|\bto\b)\s*"
    r"(?:(?:it'?s|its|that'?s)\s+)?"
    r"([a-z][a-z'-]{1,20}(?: [a-z][a-z'-]{1,15})?)(?:\s+instead)?\s*[.!?]?$", re.I)


# "no, not Friday, Monday": the value taken back, and the right one after it. People say a
# correction in this order as often as the other way round ("Monday, not Friday"), and reading
# only the first value is worse than reading neither: "sorry, not peanuts, tree nuts" took the
# peanut allergy off the list and filed nothing, so an allergic person was left with no allergy
# on record. The comma is what tells the pair from a two-word value ("not tree nuts"), and the
# right value is kept as `to` because that is the value the store goes with from now on.
CORRECTION_NOT_PAIR = re.compile(
    r"\b(?:sorry|no|nope|actually|oops)[, ]+not\s+(?:the\s+)?([a-z0-9][a-z0-9'-]{1,20}"
    r"(?: [a-z0-9][a-z0-9'-]{1,15})?)\s*,\s*(?:its\s+|it's\s+|the\s+)?"
    r"([a-z0-9][a-z0-9'-]{1,20}(?: [a-z0-9][a-z0-9'-]{1,15})?)(?:\s+instead\b|\s*[.;!?]|$)",
    re.I)


# "no he isn't Dave" and "no he isn't, it's Dan": a line that denies a name says the pronoun
# first and the value after it, which is the opposite of the pair above, and the pronoun was read
# as the value - "no hes not dave" filed "Hes" as the son's name, answered "Hes, got it." and
# then "Your son is called Hes." A denial on its own takes a name away and puts nothing in its
# place, so nothing here is kept; a denial with a name after the pronoun ("it's Dan", "she's
# called Dana", "hes dan") is the usual way people put a name right, and that name is kept.
DENIAL_OF_A_VALUE = re.compile(
    r"^\W*(?:(?:ok|okay|ah|oh|no|nope|sorry|actually|wait)\b[,.]?\s+){1,2}"
    r"(?P<whose>he|she|it|they)(?:'?s|s)?\s*"
    r"(?:isnt|is\s+not|not|wasnt|was\s+not)\b\W*"
    r"(?:(?:the\s+)?(?!(?:its|it'?s|hes|he'?s|shes|she'?s|theyre|they'?re|called|named)\b)"
    r"(?P<wrong>[a-z][a-z'-]{1,20})?\s*[,.;!?-]*\s*)?"
    r"(?:(?P<says>its|it'?s|hes|he'?s|shes|she'?s|theyre|they'?re"
    r"|(?:he|she|it|they)\s+(?:is|are)|called|named"
    r"|the\s+name\s+is|his\s+name\s+is|her\s+name\s+is|their\s+name\s+is)\b\s*"
    r"(?:called\s+|named\s+)?)?"
    r"(?P<value>[a-z][a-z'-]{1,20})?\s*[.!?]?$", re.I)


# The naming word after a denial belongs to the clause being denied, not to a new value: "no he
# isnt called max" says the dog is not called Max, and reading "called max" as a rename gave the
# dog the name the person had just ruled out ("Max - got it, I'll call the dog Max"). A rename
# said in the same breath names the old value too ("no he isnt max, hes called leo"), and that
# line does not reach this reader at all, so the naming word there still names.
A_NAME_IS_TAKEN_BACK = frozenset(("called", "named"))


def a_name_is_taken_back(text):
    """True when the line denies a name rather than giving one: "no hes not called max".

    The tense is the tell: "no hes not called max" is about the name it had, and "no hes called
    max" is the name it has now. Only the denying frame is read here, so the second line is left
    to the rename route that already reads it.
    """
    denial = DENIAL_OF_A_VALUE.match(str(text or "").strip())
    return bool(denial and denial.group("value")
                and (denial.group("says") or "").strip().lower() in A_NAME_IS_TAKEN_BACK
                and not denial.group("wrong"))


NAME_TAKEN_BACK = re.compile(
    r"^\W*(?:(?:no|nope|sorry|ah|oh|actually|wait|oi|hey)[,.!]?\s+){0,2}"
    r"(?:"
    r"i(?:'?m|\s+am)\s+not\s+(?P<said>" + _A_SAID_NAME + r")"
    r"|my\s+name(?:'?s|\s+is)?\s*(?:is|was)?\s*not\s+(?P<said2>" + _A_SAID_NAME + r")"
    r"|my\s+name(?:'?s)?\s*(?:isn'?t|ain'?t|aint)\s+(?P<said3>" + _A_SAID_NAME + r")"
    r"|(?:that|this)(?:'?s|\s+is|\s+was)\s+not\s+my\s+name"
    r"|my\s+name(?:'?s)?\s+(?:is\s+)?wrong"
    r"|you(?:'?ve|\s+have)?\s+got\s+my\s+name\s+wrong"
    r"|(?:please\s+)?(?:don'?t|do\s+not|stop)\s+(?:call|calling)\s+me\s+"
    r"(?P<said4>" + _A_SAID_NAME + r")"
    r")\W*(?:[.!]|\?)?$", re.I)


def the_name_they_take_back(text, stored=""):
    """The name on record a line takes back, "" when it denies the name without saying which,
    or None when the line does not take the name back at all.

    Read against the name the store holds, so the denial is never a guess: "im not kay" only
    denies a name when Kay is the one the bot was told, and every other use of the same words
    ("im not sure" being the commonest line in any chat) is left to the readers that know it.
    """
    known = str(stored or "").strip()
    if not known:
        return None
    said = " ".join(str(text or "").split())
    # The chat-speak hangs off the end of the denial as it does off every other line: "im not kay
    # lol" takes the name back exactly as "im not kay" does.
    from . import filler as _filler
    denial = NAME_TAKEN_BACK.match(_filler.without_filler(said))
    if not denial:
        return None
    named = ""
    for group in ("said", "said2", "said3", "said4"):
        named = named or (denial.group(group) or "").strip()
    if named and not _the_same_name(named, known):
        return None
    return known


# "scratch that, 800" after "my budget is 500", "strike that, in august" after the trip: the words
# that take the last thing back, with the right value after them, are a correction and not a
# retraction. The retraction reader takes "scratch that" on its own - it is anchored to the end of
# the line - so the lined line "scratch that, 800" matched neither: the reply said "Got it -
# scratch that, 800." and the store still had 500, and the next ask said the old figure back.
CORRECTION_TAKEBACK = (r"(?:(?:scratch|strike|disregard)\s+(?:that|it|this)"
                       r"|(?:take|taking)\s+(?:that|it|this)\s+back"
                       r"|forget\s+(?:what\s+)?i\s+(?:just\s+)?said"
                       # Owing the mistake is as plain a way of taking the last thing back as
                       # "scratch that": "i got that wrong, its 4 may" and "im wrong, its 4 may"
                       # carry the corrected date exactly as "actually its 4 may" does, and with
                       # no opener here the whole line fell through to the greeting, which said
                       # it back - "Got it - you got that wrong, it's 4 may" - while the store
                       # kept the date that had just been taken back.
                       r"|i\s+got\s+(?:that|it|this)\s+wrong"
                       r"|i\s+had\s+(?:that|it|this)\s+wrong"
                       r"|i\s+(?:was|got\s+it)\s+wrong"
                       r"|i\s+made\s+a\s+mistake"
                       r"|i\'?m\s+wrong"
                       r"|my\s+mistake)")


CORRECTION_LEAD = (r"^\s*(?:(?:ok|okay)[,.]?\s+)?"
                   r"(?:(?:(?:no|nope|sorry|wait|ah|oh|actually|oops|"
                   + CORRECTION_STALL + r"|" + CORRECTION_HEDGE + r"|"
                   + CORRECTION_TAKEBACK + r")[,.]?\s+){1,3})")


# The correction word on the end of the line instead of in front of the value: "its the 4th
# actually", "my budget is 400 actually". People put the marker after the thing as often as before
# it, and every reader in the correction block anchors the value to the end of the line, so a
# marker there left the line with nothing taken back at all: after "the party is on 3 june", "its
# the 4th actually" was answered "It's the 4th, good to know" and the store still held the 3rd, so
# the next ask said their own correction was the date they had taken back. The word is the same
# word, so a line that ends with it is read as the line with it in front.
A_MARKER_ON_THE_END = re.compile(r"\s+(?:actually|really|honestly)\s*[.!?]*\s*$", re.I)


# A bare value can carry the unit it is said in ("no wait, 8 kilos", "no, 5 minutes"): which
# fact it corrects is still decided by the line before, and memory_store refuses a unit the fact
# on the table is not measured in.
# A name put right says the pronoun before it ("no hes called max", "no she's called dana"),
# and without that frame the line read as three words and no value at all, so the correction was
# lost and the line went on to be answered as something else.
# The frame the corrected value usually wears - "it's 4 may", "that's on thursday" - is written
# without its apostrophe as often as with: "actually it is on 4 may" says the corrected day as
# plainly as "actually it's on 4 may", and with only the contractions listed the line was read as
# a statement and the store kept the date that had just been taken back. One frame, so the date,
# the clock and the bare value cannot drift apart.
CORRECTION_FRAME = (r"(?:(?:it'?s|its|it\s+is|it\s+was|that'?s|thats|that\s+is|that\s+was"
                    r"|he'?s|hes|she'?s|shes|they'?re|theyre|they\s+are)\s+)")


CORRECTION_BARE = re.compile(
    CORRECTION_LEAD
    + r"(?:" + CORRECTION_FRAME + r""
       r"|(?:his|her|its|their|the)\s+names?\s+(?:is\s+|not\s+|was\s+)?)?"
    + NOT_A_VALUE_START +
    r"(?!(?:oops|sorry|wait|hold|hang|hmm|um+|erm+|nope?|actually|oh|ah"
    r"|eh|well)\b)"
                             r"([a-z][a-z'-]{1,20}(?:[ ][a-z][a-z'-]{1,15})?"
                             r"|[\u00a3$\u20ac]?\s?\d[\d,]*(?:\.\d+)?"
                             r"(?:\s?(?:pounds?|quid|euros?|dollars?|k|kilos?|kgs?|kg"
                             r"|stones?|st|lbs?|lb|grams?|g|litres?|liters?|miles?|km"
                             r"|minutes?|mins?|hours?|days?|weeks?|months?|years?)\b)?)"
                             r"\s*[.!?]?$",
                             re.I)


# A figure on its way back is usually hedged: "actually just 6", "no, only 2", "sorry, about
# five". The hedge is neither a second correction word nor a value, so the readers above stop on
# it and the line is left as something said rather than something put right: a table for eight
# stayed eight after "actually just 6", and the readback then gave the person both numbers ("you
# are 8 for dinner on Saturday; you said actually just six"). Only a figure can follow the hedge.
# "no just checking" and "sorry about that" are the words people use to get off a subject, and
# they correct nothing to a word: the value after the hedge is read only as a number, with the
# unit it is said in, so the correction needs the figure the person actually changed.
CORRECTION_HEDGED = re.compile(
    CORRECTION_LEAD
    + r"(?:just|only|about|around|roughly|nearly|almost|exactly|more\s+like|closer\s+to)"
    r"\s+(?:(?:it'?s|its|that'?s|thats|the)\s+)?"
    + r"([\u00a3$\u20ac]?\s?\d[\d,]*(?:\.\d+)?"
      r"(?:\s?(?:pounds?|quid|euros?|dollars?|k|kilos?|kgs?|kg|stones?|st|lbs?|lb|grams?|g"
      r"|litres?|liters?|ml|miles?|km|minutes?|mins?|hours?|days?|weeks?|months?|years?"
      r"|people|guests?|adults?|kids?|of\s+us)\b)?"
      r"|" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + r")"
    r"\s*(?:now\b)?\s*(?:[.!?,]|$)",
    re.I)


# A clock said again: "sorry, its at 8pm", "no wait, 8pm". The plan on the table holds the
# clock this replaces, so the line names only the new one. Only a time with am or pm (or a clock
# written as one) is read here, because a bare figure after "no" is a number and belongs to the
# reader that reads numbers. A clock often arrives with a word of preference on the end ("4.30pm
# is better", "8 works"), which says the time is the one they want and nothing else.
CLOCK_PREFERENCE = (r"(?:\s+(?:is|would\s+be|works|suits|sounds)\s*"
                    r"(?:(?:much|a\s+lot|way|far)\s+)?"
                    r"(?:better|best|fine|good|easier|ok|okay)?)?")


CORRECTION_CLOCK = re.compile(
    CORRECTION_LEAD + r"(?:" + CORRECTION_FRAME + r")?(?:at\s+|for\s+)?"
    r"(" + CLOCK_SAID + r")" + CLOCK_PREFERENCE + r"\s*(?:instead|now)?\s*[.!]?$", re.I)


# The same clock with no correction word in front of it, because the preference is the whole
# line: "4.30pm is better", "2pm works better", "9am suits". Nothing in the line says what it
# corrects, so the store asks it of the plan on the table and refuses it when that plan holds no
# clock: "morning is better" is not a time, and a clock with no plan is a remark about some other
# time, not a change to a turn of theirs. A line that goes on to compare two clocks ("4pm is
# better than 3pm") names no single value and is left alone.
CLOCK_PREFERRED = re.compile(
    r"^\s*(?:(?:and|but|or|so)\s+)?"
    r"(" + CLOCK_SAID + r")\s+"
    r"(?:(?:is|would\s+be|sounds|seems)\s+)?(?:(?:much|a\s+lot|way|far)\s+)?"
    r"(?:better|best|fine|good|easier|ok|okay|w(?:orks|ould\s+work)|suits?|sounds?)"
    r"(?:\s+(?:better|best|fine|good))?"
    r"\s*(?:instead|then|though|now)?\s*[.!]?$", re.I)


# A number corrected in its own line: "my budget is 500" then "actually make that 800". The
# value is the number, and what it corrects is decided by the line before ("$ 500" is a budget).
# The whole line has to be the correction. The verb alone is not enough: "put it 20 in the oven"
# is a step in a recipe, and reading the 20 as a new budget answered "put it in the oven at 200"
# over the number they had given. A period qualifier is the one thing allowed after the number
# ("make it 800 a month"), because it says what the same amount is measured over.
AMOUNT_CORRECTION = re.compile(
    r"^\W*(?:(?:sorry|actually|no|nope|ok|okay|wait|well|hmm|um)\b[,.]?\s*)*"
    r"(?:(?:make|makes|change|changed|put)\s+(?:it|that|them)\s+(?:to\s+)?"
    r"|more\s+like\s+(?:[£$\u20ac]\s?)?)"
    r"(\d[\d,. ]{0,12}?)"
    r"(?:\s*(?:a|per|each)\s+(?:day|week|month|year|person|head)\b|"
    r"\s+for\s+(?:the|a|an|our|my|this|that)\s+[\w' -]{1,20}|"
    r"\s*(?:pounds?|quid|euros?|dollars?|bucks)\b|"
    r"\s+(?:instead|now)\b)?\W*$", re.I)


# The same correction said without the verb: "my budget is 300" then "sorry, 400 a month". People
# correct a figure by saying the figure again with what it is measured over, and the line has to
# open with a correction word so a plain "i pay 400 a month" is a new statement, not a replacement.
# The period qualifier is required: "sorry, 400" on its own says too little to move anything, and
# the number this replaces is decided by the line before ("$ 300" is a budget).
AMOUNT_CORRECTION_BARE = re.compile(
    r"^\W*(?:(?:sorry|actually|no|nope|ok|okay|wait|well|hmm|um)\b[,.]?\s*)+"
    r"(?:(?:it'?s|that'?s)\s+)?(?:make\s+(?:it|that|them)\s+(?:to\s+)?)?"
    r"(\d[\d,. ]{0,12}?)\s*(?:a|per|each)\s+(?:day|week|month|year|person|head)\b\W*$",
    re.I)


# "i want to make it to 30 countries" is a wish about the future, not a correction of a number
# already given: the verb only changes a value when nothing in front of it is hoping.
AMOUNT_WISH = frozenset("""want wants wanted wanting hope hopes hoped hoping wish wishes
wishing try tries trying tried going gonna like love plan plans planning intend intends
aim aims aiming""".split())


# "no im 35" after "im 34" is a correction too: a marker in front of a plain statement of the
# same kind of fact means the statement's own value is the one to keep, and people say it that
# way when the first go was simply wrong - "no im 35", "actually im 35", "no i live in york" -
# with no "i meant" anywhere in the line. The word after the marker has to open a statement about
# the person, so "sorry to bother you" and "no the dog is called rex" stay ordinary lines, and
# the keys it may correct are the person's own values only: a pet, a relative or a diet never
# lands on the user by this route.
CORRECTION_MARK = re.compile(r"^\W*(?:no|nope|sorry|actually|oops)\b[,.]?\s+"
                             r"(?=(?:i|im|i'm|i've|ive|i'd|my|we|we're|we've|its|it's|i'll|"
                             r"it\s+is|that\s+is)\b)",
                             re.I)


CORRECT_FROM_MARK = ("age", "height", "city", "places", "name", "job", "budget")


# "no thanks", "no idea", "no worries" are answers, not values.
CORRECTION_BARE_NO = frozenset("""thanks thank idea ideas worries worry problem way chance
doubt rush need matter point wonder clue reason sorry luck harm""".split())


# The sentence shape each fact arrives in, so a corrected value can be read the way the fact it
# corrects was read: "no I mean 43" after "I'm 34" is an age, not a name.
CORRECTION_SHAPE = {"name": "my name is {}", "age": "i am {}", "budget": "my budget is {}",
                    "city": "i live in {}",
                    "places": "i live in {}", "job": "i work as a {}", "diet": "i am {}",
                    "allergies": "i am allergic to {}", "pets": "i have a {}"}


# A corrected value names a thing. It is not a clause: "no, i am not on shift" and "sorry, it's
# not far from york" are things people say, and the value in them is a sentence, not a value.
CLAUSE_OPENERS = frozenset("""i i'm im i've ive i'd id it it's its that that's thats this
we we're we've you you're he she they there here not no yes and but so don't dont doesn't didnt
can't cant won't wont isn't aren't was wasn't weren't is are am was were do does did have has had
could would should can will must might may be been being sorry thanks thank please just really
""".split())


# A value is a name, a place or a number, so it ends where a verb starts: "no i said bristol is
# fine" corrects the place, and "is fine" is a comment on it, not part of the name.
COPULA_SPLIT = re.compile(r"\s+(?:is|was|are|were|be|been|being|seems|seemed|looks|looked|"
                          r"now|then|actually|though|anyway)\b", re.I)


# Words that point at something instead of naming it. A correction has to name the value, and a
# line that names nothing - "no i said the other one", "i said nothing", "three of them" - is a
# complaint or a shrug, not a new fact. Reading one of those as the value would replace a fact the
# person did give with one that was never said, which is worse than not correcting at all.
NOT_A_VALUE = frozenset("""nothing anything something everything nobody none someone somebody
anybody everybody them they it him her us you me that this these those there here
anywhere somewhere nowhere everywhere whatever whoever whichever whenever wherever
other another else one ones same such what which who whom whose when where why how whether
he she his hes shes theyre he's she's they're thats im i'm ive i've weve we've
""".split())


# A phrase that ends by pointing back ("three of them", "any of those") names nothing either,
# however the words before it read.
POINTING_AT = frozenset("""them they it him her us you me that this these those""".split())


ARTICLES = frozenset("""a an the""".split())


# A date is a value however many little words it is said with: "the 12th", "the 13th of june",
# "june the 12th". The word count below is about clause-fragments, and a date is not one.
_MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))


DATE_VALUE = re.compile(
    r"(?:the\s+)?\d{1,2}(?:st|nd|rd|th)(?:\s+of\s+(?:" + _MONTH_ALT + r"))?"
    r"|(?:the\s+)?\d{1,2}\s+(?:" + _MONTH_ALT + r")"
    r"|(?:" + _MONTH_ALT + r")\s+(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?", re.I)


# A date said again is a value with more than one word in it, and the one-word reader above
# cannot carry it: "my birthday is 3rd may" then "sorry, its the 4th of may" left the month where
# it was, so the store answered with the day the person had just taken back. A day and a month, a
# month on its own or a day on its own is the value here; which fact it moves is the store's
# question, because a birthday and a trip are both kept with a date on them.
_DAY_NUMBER = r"(?:0?[1-9]|[12]\d|3[01])"


CORRECTION_DATE = re.compile(
    CORRECTION_LEAD + r"(?:" + CORRECTION_FRAME + r")?(?:on\s+|in\s+)?"
    r"(?P<date>(?:the\s+)?" + _DAY_NUMBER + r"(?:st|nd|rd|th)?"
    r"(?:\s+(?:of\s+)?(?:" + _MONTH_ALT + r"))?"
    r"|(?:" + _MONTH_ALT + r")(?:\s+(?:the\s+)?" + _DAY_NUMBER + r"(?:st|nd|rd|th)?)?)"
    r"\s*[.!?]?$", re.I)


# A date is moved on a plan by saying the going itself, and the going sits between the correcting
# word and the date: "im going to spain in june" then "actually we fly in july now". The words say
# which of the person's dates moved, the way "actually its cornwall we go to" says which place -
# and without them the line read as no correction at all, so the month in the plan stayed June and
# the line went on to be answered as something else ("we fly in july now" was answered about fruit
# flies). Only the going is allowed there, and only in the present: "actually we went in june" is a
# line about a trip already taken, not a plan being moved.
_GOING_VERB = (r"(?:fly|flies|flying|go|goes|going|travel|travels|travelling|traveling|head|heads"
               r"|heading|leave|leaves|leaving|visit|visits|visiting|get|gets|getting|are|is)")


_GOING_SAID = (r"(?:(?:we|i|they|he|she)(?:'?re|'?m|'?s)?\s+" + _GOING_VERB +
               r"|(?:the\s+|our\s+|their\s+)?(?:flight|trip|holiday|booking|wedding|party"
               r"|appointment|visit)\s+(?:is|are|'s))")


_GOING_DATE = (r"(?:the\s+)?(?:0?[1-9]|[12]\d|3[01])(?:st|nd|rd|th)?"
               r"(?:\s+(?:of\s+)?(?:" + _MONTH_ALT + r"))?"
               r"|(?:" + _MONTH_ALT + r")(?:\s+(?:the\s+)?" + r"(?:0?[1-9]|[12]\d|3[01])"
               r"(?:st|nd|rd|th)?)?")


CORRECTION_DATE_GOING = re.compile(
    CORRECTION_LEAD + _GOING_SAID + r"\s+(?:out\s+)?(?:on\s+|in\s+)?(?P<date>" + _GOING_DATE
    + r")", re.I)


# The same move said with the marker behind it instead of in front: "we fly out in august now",
# "we travel in december instead". The word at the end is what makes it a change rather than a
# statement ("we fly in june every year" is not read here), and the plan it moves is the store's
# question, so the reader only says which date the line names.
CORRECTION_GOING_MOVED = re.compile(
    r"^\s*" + _GOING_SAID + r"\s+(?:out\s+)?(?:on\s+|in\s+)?(?P<date>" + _GOING_DATE + r")"
    r"\s+(?:now|instead|this\s+time|from\s+now\s+on)\b", re.I)


# A correction is rarely the value and nothing else: people put a word of apology or a shrug after
# it, or say the value and then which one it replaces ("no bristol sorry", "in july instead",
# "sorry, in august thanks", "no, 500 i mean"). The readers above are anchored at the end of the
# line, so one of those words stopped the value being read at all, and the person's own line went
# back to them ("Got it — no in july sorry."), which is the restatement STYLE.md rules out. The
# words here name nothing, so a run of them after the value is still the value.
CORRECTION_TAIL_WORDS = frozenset("""sorry soz thanks cheers please pls
    instead then now though tho anyway either too also again ok okay ha haha lol lmao""".split())


# "i mean" and "i meant" trail a correction in the same way ("sorry, in july i mean"), and they
# are two words, so they are their own run.
CORRECTION_TAIL = (r"(?:" + CORRECTION_WHY + r")?"
                   r"(?:\s*,?\s*(?:i\s+mean|i\s+meant|i\s+mean\s+it|"
                   r"(?:" + "|".join(sorted(CORRECTION_TAIL_WORDS)) + r")))"
                   r"*\s*[.!?]?\s*$")


def _a_tail_hangs_off(pattern, then=""):
    """`pattern` with a run of the words that name nothing allowed after its value.

    Every reader here finishes at the end of the line, so the run goes on the end: the value is
    what the reader already knows how to find, and what follows the value is said around it -
    `then` is what may come between the value and the run.
    """
    if not pattern.rstrip().endswith("$"):
        return pattern
    return pattern.rstrip()[:-1] + then + CORRECTION_TAIL


# A place corrected to can be said with the going that shows which fact it is: "actually its
# cornwall we go to" after "im going to rome in may". The words are the frame around the place,
# the way "in july instead" is a frame around the month, and the value is the place.
CORRECTION_TRIP_FRAME = (r"(?:\s+(?:we|i)\s+(?:go|went|'re\s+going|are\s+going|'m\s+going"
                         r"|am\s+going)(?:\s+to)?)?")


# The value readers, opened up to the run of words that name nothing after the value.
CORRECTION_BARE = re.compile(_a_tail_hangs_off(CORRECTION_BARE.pattern,
                                               CORRECTION_TRIP_FRAME), re.I)


# "no the 12th of july at 6": the time of day comes after the date people correct to, and the
# date is still the date with it there.
CORRECTION_DATE = re.compile(
    _a_tail_hangs_off(CORRECTION_DATE.pattern,
                      r"(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm|o'?clock)?)?"), re.I)


AMOUNT_CORRECTION_BARE = re.compile(_a_tail_hangs_off(AMOUNT_CORRECTION_BARE.pattern), re.I)


def a_value(phrase):
    """True when a phrase reads as a value (a name, a place, a number), not as a clause.

    Two things can go wrong. A clause ("no, i am not on shift") is a sentence, not a value, and is
    refused by its opener. A phrase that only points at something ("the other one", "nothing",
    "three of them") has no thing in it to keep, so it is refused by what it is made of: if none
    of its words names anything, there is nothing here to remember."""
    parts = re.findall(r"[a-z0-9']+", str(phrase or "").lower())
    if not parts:
        return False
    if len(parts) > 3 and not DATE_VALUE.fullmatch(str(phrase or "").strip()):
        return False
    if parts[0] in CLAUSE_OPENERS or parts[0] in NOT_A_VALUE:
        return False
    if any(word in POINTING_AT for word in parts[1:]):
        return False
    names = [word for word in parts if word not in ARTICLES]
    return any(word not in NOT_A_VALUE and word not in CLAUSE_OPENERS for word in names)


# "no a vegan" says the thing they mean with the article chat-speak keeps in front of it, and the
# bare-value reader cannot see it: its value starts at a letter run of two, so "a" is no value at
# all, and the line filed nothing at all - "im vegetarian" stayed the only diet in the store while
# the person said they were vegan. Only the whole line is read here, and only the article plus one
# to two words, so "no a bit tired" and "no a good idea really" stay lines about nothing. The
# animal is left out on purpose: "no a cat" after "i have a dog" is another pet, and the pet
# reader already has it (see NO_THEN_A_THING above). "actually a stir fry" is left out for the
# same reason: the swap reader already moves the dish, and claiming the line here changed which
# pairing the drink answer was for.
NO_THEN_A_THING_NAMED = re.compile(
    r"^\s*(?:no|nope|sorry|oops)[,.]?\s+(?:a|an)\s+"
    r"([a-z][a-z'-]{1,20}(?:\s[a-z][a-z'-]{1,15})?)\s*[.!?]?\s*$", re.I)


# a job after "I'm a ..." / "I work as ..." / "my job is ..."
# "I'm a nurse": the article is the signal. Without it "I'm caught outside" reads as a job.
JOB_AFTER = re.compile(r"\b(?:i(?:'m| am)|im)\s+(?:now |just )?(?:a|an)\s+([a-z][a-z '-]{2,30})",
                       re.I)


# "i've just become a teacher", "i retrained as a plumber": the job arrives as a change, and it
# is still the job they have now. "i'm now a teacher" is the same move, said with "now".
# Only the verbs that cannot mean anything else: "i switched to a cheaper tariff" and "i moved
# into a studio flat" take the same shape and would file a tariff or a flat as the job.
JOB_BECOME = re.compile(r"\b(?:(?:i(?:'ve| have)?|ive)\s+(?:just\s+)?(?:become|became|retrained as|"
                        r"qualified as))\s+(?:a|an)\s+([a-z][a-z '-]{2,30})",
                        re.I)


# How the job was said decides how it is said back: "i work as a nurse" is "you're a nurse",
# while "i work in a warehouse" is "you work in a warehouse" and never "you're a warehouse".
# The article is part of the match so "in an office" leaves "office" and not "n office".
# A job said in the past is still their job. Somebody coming back to work after years at home
# says it this way - "i was a teaching assistant before the kids", "i used to be a nurse", "i
# worked as a carer" - and the store took only the present tense ("i work as", "i'm a"), so the
# line was filed nothing and a turn later the bot denied it: "what was my job before" got "You
# haven't told me what you do yet". The noun phrase stops at the word that says when, because
# "before the kids" and "until 2019" are not part of the job.
JOB_WAS = re.compile(
    r"\b(?:i|we)\s+(?:was|were|used to be|used to work as|worked as|was working as|"
    r"were working as)\s+(?:(as)\s+)?((?:an?|the)\s+)?"
    r"([a-z][a-z '-]{2,30}?)(?=\s+(?:before|until|till|then|after|years|when|but|and|"
    r"in \d{4}|at the time)\b|[,.;!?]|$)", re.I)


# A word for how old they were is not a job: "i was a kid", "i was a teenager", "i used to be a
# lad". What they did all day is the job; these only say when.
WAS_NOT_A_JOB = frozenset("""kid kids child children boy girl baby toddler teenager teen lad lass
man woman person human""".split())


JOB_WORK = re.compile(r"\b(?:i work (as|in|at|for|on)|i work|my job is|"
                      r"i(?:'m| am) working as|im working as)"
                      r"\s+((?:an?|the)\s+)?([a-z][a-z '-]{2,30})", re.I)


JOB_FRAME = frozenset(("in", "at", "for", "on"))


JOB_APPOSITIVE = re.compile(r",\s*(?:a|an)\s+([a-z][a-z '-]{2,30})", re.I)


# A comma and a noun after something they have is the thing itself, not what they do: "we have
# two cars, a fiesta and a focus" and "i have a bike, a giant" were filed as the job `fiesta`
# and `giant`, and the store then answered "what do i do" with them. A person naming their job
# after a comma ("im jess, 28, from dublin, a nurse") has no having word before the comma.
POSSESSION = re.compile(
    r"\b(?:i|we)(?:\s+(?:have|had|has|got|own|bought|keep|kept|just got|recently got))\b[^,]*,\s",
    re.I)


# Nothing but the way a correction opens is not a person for a noun to be about: "i have a dog" and
# "no, a cat" was filed as the job `cat`, and the store then answered "what do i do for work" with
# "You told me you're a cat." The appositive that reads "im jess, 28, from dublin, a nurse" needs
# somebody before its comma to be about.
CORRECTION_OPENER_WORDS = frozenset("""no nope not sorry soz ok okay well actually oh ah
    yes yeah nah right wait anyway and but so then also just hi hey hello thanks please""".split())


# "i got a job at tesco", "i just got the job at the co-op", "i start my new job at tesco on
# monday": the line names where they work without ever saying "i work there", so the store kept
# nothing and the follow-up ask ("where do i work now") denied it - "You haven't told me what you
# do yet". The job word is required: "i started at the gym" names no job at all.
JOB_GOT_AT = re.compile(
    r"\b(?:i|i've|ive)\s+(?:just\s+|finally\s+|only\s+|now\s+|recently\s+)?"
    r"(?:got|get|gotten|landed|bagged|start|started|began|begin|begun)"
    # "work" is not a job word here: "i got work at the weekend" names a shift and "i got my work
    # at the office done" names a task, and both were read as an employer. "job interview" and
    # "job offer" are not the job either: a person who is still being interviewed has not got it.
    r"\b[^.!?]{0,25}?\b(?:job|role|position|contract)\b"
    r"(?!\s+(?:interview|interviews|offer|offers|application|applications|trial))"
    r"[^.!?]{0,20}?\b(at|with|in)\s+(an?\s+|the\s+)?([a-z][a-z '&.-]{2,30})", re.I)


# "with" is a frame like "at": "i got a job with the council" is where they work.
JOB_GOT_FRAME = frozenset(("at", "with", "in"))


# What the words after "at"/"with" must not be. Not every line that gets a job says where: "i got
# a job at christmas" is a date, "at the weekend" a shift, "at my old firm" the person's own words
# about the past and "with a start date in may" the paperwork. Filed as places they were answered
# "You work at Christmas" and "You work at Your old firm", where the line had only been quoted.
JOB_GOT_NOT_A_PLACE = NOT_PLACES | frozenset("""soon notice point start beginning first last next
day week weeks month months moment present past future offer interview application trial salary
wage wages money hours shift shifts nights evenings mornings""".split())


JOB_GOT_POSSESSIVE = re.compile(r"^(?:my|our|your|their|his|her|its|mine|ours|yours)\b", re.I)


# Somewhere people are employed that is also a word for going there: "i got a job at the
# hospital", "... at a school" and "... at the office" are the commonest way of naming an
# employer there is, and these words are on the not-a-place list so that "im in hospital" is
# not read as a city. After a job word they can only be where the person works.
JOB_GOT_AN_EMPLOYER = frozenset("""hospital school college university office surgery
practice nursery""".split())


def a_place_that_employs(phrase):
    """Whether the words after "at"/"with" name somewhere a person works.

    "i got a job at tesco" names an employer. "i got a job at christmas" (a date), "at the
    weekend" (a shift), "at my old firm" (the person's own words) and "with a start date in may"
    (the paperwork) name no employer, so they are left to the readers that quote the line.
    """
    words = str(phrase or "").strip(" .!?,").split()
    if not words:
        return False
    said = " ".join(words)
    if JOB_GOT_POSSESSIVE.match(said):
        return False
    if (words[0].lower() in JOB_GOT_NOT_A_PLACE
            and words[0].lower() not in JOB_GOT_AN_EMPLOYER):
        return False
    return True


# "i got a new job as a nurse", "i start my job as a carer on monday": the job is named after
# "job as", and whether it is the speaker's own is read from the clause in front of it.
JOB_AS_A = re.compile(r"\bjob\s+as\s+(?:an?\s+)?([a-z][a-z '-]{2,30})", re.I)


JOB_OWN_VOICE = re.compile(r"\b(?:i|i've|ive|im|i'm)\b", re.I)


# "my new job as a nurse" is theirs; "my brother got a job as a chef" is his, and the mine
# frame is the word "my" with nothing about a person between it and the job.
JOB_MINE = re.compile(r"\bmy\s+(?:new\s+|first\s+|current\s+)?$", re.I)


# A job they want, or are applying for, is not one they have: "i want a job as a teacher" was
# said back as "you're a teacher".
JOB_WANTED = re.compile(r"\b(?:want|wanted|wanting|wants|looking for|hoping|hope|apply|applied|"
                        r"applying|application|would like|thinking of|considering|training to|"
                        r"study|studying|studied|need|needs|trying|try|dream|goal|someday|"
                        r"one day|qualified|interview|interviewing)\b", re.I)


# A noun that only exists in a judgement of oneself. "i'm a doormat" and "i'm a problem for my
# team at work" have the same shape as "i'm a nurse" to the job reader below, so they were filed
# as a job and read back as "Noted: you're a doormat." - the coldest answer there is to somebody
# saying what they think of themselves. Nothing here is a thing a person does.
# A noun that is itself an insult is a verdict whenever it is said about the speaker, whether or
# not it is also a role: "im an awful coward", "im a right brat". The insult nouns are on the same
# list as the ones above, so the job reader and the judgement reading can never disagree about
# what a word is.
JUDGEMENT_NOUNS = frozenset("""
burden joke doormat letdown disappointment waste problem mistake nuisance embarrassment fraud
imposter impostor hypocrite mess failure loser idiot muppet moron fool clown
coward liar cheat bully crybaby slob brat wimp
""".split())


# Who somebody is is not what they do all day. "im a woman", "im a girl" and "im a pensioner"
# were kept as jobs, and the chat pool answered "A woman - nice one. What's a normal day like for
# you?" - a workplace question about a line that named no workplace. The family words below are
# the same shape, and a line that says both ("im a mum of two") keeps the person.
JOB_STOP = frozenset("""bit little big huge real good bad terrible complete total rubbish great
boring bored stressful exhausting tiring draining demanding repetitive mind numbing busy quiet slow
fine okay ok awful horrible crap pants nightmare easy hard tough long short dull repetitive
massive proper new first second lot lots fan week month year while bit bit more less couple
surprise
few kind sort mum dad mother father parent nan granny grandad
woman women man men girl boy lady ladies bloke guy teenager teen pensioner
brit briton englishman englishwoman scotsman scotswoman
somewhere anywhere nowhere""".split())


# A judgement said about themselves is not a fact about the world. "im an idiot" is how they
# feel today, not what they do all day, and "im a bad mum" does not mean they have told the chat
# about a mum. The words are the ones people reach for when they are being hard on themselves;
# the shape that matters is the speaker as the subject ("im a hopeless cook", "im a lazy
# student"), so "my mum is a teacher" and "im a nurse like my mum" are untouched.
SELF_JUDGEMENT = frozenset("""
bad terrible awful horrible rubbish useless hopeless worthless pathetic stupid dumb thick
idiot imbecile moron failure loser letdown disappointment burden nuisance waste mess disaster
wreck nightmare fool clown muppet fraud imposter impostor hypocrite doormat lazy selfish
greedy ungrateful nasty boring shit crap lousy naff rotten dreadful
shitty crappy crapola shite pants wank bollocks tosser twat prick git sod bugger arse arsehole
""".split())


# The same words said the ruder way, and the ones built out of them ("im shitty", "im crappy",
# "im bollocks", "im pants"), were kept as names because none of them is in the state lists the
# name reader asks. The note is out here on purpose: a "#" line written inside the triple quotes
# above is data, not a comment, so `.split()` turned every word of it into a judgement - and any
# reader that builds a shape out of this set then matched the prose ("the", "in", "and", "of",
# "as", "all", "is", "them"), which read a plain fact about the person as a verdict on themselves:
# "im in bristol" answered "you're being harder on yourself than you'd be on a friend".
# The noun after the word is what makes a judgement a verdict. A role with somebody on the other
# side of it - "im a bad mum", "im a shit driver", "im a lazy student" - is a verdict on the job
# they are doing, and saying it back to them agrees with it. A habit being described - "im a bad
# sleeper", "im a terrible dancer" - is a fact about them like any other, kept and said back, and
# only how the chat answers it changes (bot/modules/chat.py, `_judged_a_role`).
ROLE_YOU_CAN_FAIL = frozenset("""
mum mom mummy mam mother mumma dad daddy father parent parents guardian carer friend partner
husband wife son daughter brother sister sibling child kid colleague coworker boss manager
employee worker teacher nurse doctor cook driver parent person student pupil apprentice learner
""".split())
