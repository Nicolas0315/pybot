"""Part 8 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from .kinds_part_07 import (
    _A_COUNT, _A_DEFINITION, _A_RECORD, _A_AN_AMOUNT_OF_A_THING, _A_AN_OCCASION_OF_THEIR_OWN,
    _A_ARITHMETIC, _A_A_CONVERSION, _A_A_DIFFERENCE, _A_A_PLAN_ABOUT_THE_WEATHER,
    _A_A_TRAFFIC_LIGHT, _A_BARE_RECORD, _A_DID_YOU_SEE, _A_FRESHENING, _A_HAS_A_NUMBER,
    _A_HISTORY_ITSELF, _A_HOW_A_THING_MEASURES, _A_HOW_IT_WORKS, _A_HOW_MUCH_A_FEELING,
    _A_HOW_MUCH_ENOUGH, _A_HOW_MUCH_IS_IN, _A_HOW_MUCH_IT_HOLDS, _A_HOW_MUCH_I_SPENT,
    _A_HOW_MUCH_OF_A_UNIT, _A_HOW_OLD_IS_THE_WORLD, _A_MY_OWN_FIGURE, _A_MY_OWN_PLAN, _A_PAST_YEAR,
    _A_SAYS_NOW, _A_THE_CLOCK, _A_WEATHER_HERE, _CHANGING, _MONEY,
)


_A_WORKING = re.compile(r"\bhow\s+(?:does|do)\b.{0,40}\bwork\b|"
                        r"\bwhy\s+(?:does|do|is|are|did)\b")


_A_HISTORY = re.compile(
    r"\bwhen\s+(?:was|were|did)\b.*\b(?:built|invented|discovered|founded|written|composed|"
    r"painted|made|begin|began|start|end|ended|happen|happened|become)\b|"
    r"\bwho\s+(?:invented|discovered|founded|wrote|composed|built|painted)\b|"
    r"\bhistory\s+of\b")


# A measurement of a thing that does not move: "how tall is everest", "how deep is the ocean".
# "how old is the queen" is left out on purpose - an age is a figure with a date on it.
_A_MEASURE = re.compile(
    r"\bhow\s+(?:tall|high|deep|wide|long|heavy|big|far)\s+is\b|"
    r"\bhow\s+far\s+away\b")


# What a thing is made of is a fact about the thing, not a figure with a date on it.
_A_MADE_OF = re.compile(r"\bmade\s+(?:of|from|out\s+of)\b")


_A_METHOD = re.compile(
    r"\bhow\s+to\b|\bhow\s+(?:do|can|should)\s+(?:i|you|we)\b|\bhow\s+long\s+(?:do|does|should|to)\s+.*"
    r"\b(?:cook|boil|bake|roast|keep|last|take|soak|chill|freeze)\b|"
    r"\bhow\s+often\s+should\s+i\b")


# A line that asks what a *word* means is not asking what the thing is doing: "what does available
# mean" and "what does opening hours mean" were read as the availability and the hours, because the
# live word is the very word being defined. The ask names the word itself, so it settles.
_A_WORD_MEANS = re.compile(
    r"\bwhat\s+(?:does|do|did)\b.{1,40}?\bmean\b\s*[?!.]*\s*$|"
    r"\bwhats?\s+(?:is\s+)?the\s+meaning\s+of\b|\bwhat\s+is\s+(?:the\s+)?meaning\b|"
    r"\bwhat\s+is\s+the\s+definition\s+of\b|\bwhat\s+do\s+you\s+mean\s+by\b|"
    r"\bdefine\b")


_SETTLED = (_A_COUNT, _A_RECORD, _A_DEFINITION, _A_WORKING, _A_HISTORY, _A_MEASURE,
            _A_MADE_OF, _A_METHOD)


# A conversion is arithmetic: the numbers do not move.
_SEALED_ASKS = frozenset(("maths",))


# A line asks something when it says so: an ask the reading already labelled, a question mark,
# a question word anywhere in it, or an auxiliary on the front ("is the shop open", "any jobs
# going"). The label alone is not enough - "any news on the strike" and "timetable for the 42"
# are asks the rest of the reading files as a statement - and a question word anywhere is the
# general rule for the rest, because a line that carries one is asking or quoting an ask.
# A question word only makes a line an ask at the front of it, behind an opener at most. Inside a
# statement it belongs to a relative clause and asks nothing: "the oven door drops when i open
# it" is a report about a door, not a question about opening hours.
_ASKS_WITH_A_QUESTION_WORD = re.compile(
    r"^\s*(?:(?:and|but|so|then|also|ok|okay|right|oh|well|now|sorry|ta|hi|hello|"
    r"excuse\s+me)\s+)*(?:what|whats|what's|when|whens|where|which|who|whose|why|how|"
    r"hows|how's)\b")


# A second question in the same line starts a new clause with an auxiliary: "my train was 40
# minutes late, can i get money back" is two questions and the second one is what they want.
_ASKS_MID_LINE = re.compile(
    r"\b(?:is|are|was|were|do|does|did|can|could|will|would|shall|should|am|have|has|had)\s+"
    r"(?:i|we|you|they)\b")


_ASKS_AFTER_A_COMMA = re.compile(
    r",\s*(?:(?:and|but|so|then|also)\s+)?(?:is|are|was|were|do|does|did|can|could|will|"
    r"would|shall|should|am|have|has|had)\s+(?:i|you|we|they|it|he|she|there|the\s+\w+)\b")


# A question word that starts a new clause after a comma is a second question, whatever the
# clause before it was: "she said shes leaving, what should i do" is a report and an ask.
_ASKS_AFTER_A_COMMA_WORD = re.compile(
    r",\s*(?:(?:and|but|so|then|also)\s+)?(?:what|whats|when|whens|where|which|who|why|how|"
    r"hows)\b")


_ASKS_WITH_AN_AUXILIARY = re.compile(
    r"^(?:is|are|was|were|do|does|did|can|could|will|would|shall|should|has|have|had|any|"
    r"anything|anyone|anyway|tell)\b")


# A question word inside what somebody knows or what was told them asks nothing: "i know what the
# price is" and "i told him what time it starts" are reports, and reporting that you know a figure
# is not asking for it. The verb has to be on the front of the line for that, so "do you know what
# the price is" keeps asking, which is what it is.
_A_REPORTS_THE_ASK = re.compile(
    r"^\s*(?:(?:and|but|so|then|also|well|oh|anyway)\s+)*(?:i|we|they|he|she|everyone|"
    r"someone)\s+(?:already\s+|still\s+|just\s+|now\s+|never\s+|definitely\s+)?"
    r"(?:know|knows|knew|told|tell|tells|said|says|explained|explains|mentioned|mentions|"
    r"remember|remembers|reminded|found\s+out)\b")


def _a_line_asks(read, said):
    """Whether the line asks for something to be told or checked, so a fact is what it wants.

    A request to *do* something - "i need to cancel my booking" - is not an ask about the world,
    so only a question counts here. The things a line was read as asking about (`asks`) and a
    question mark stand on their own.
    """
    if read.get("kind") == "question":
        return True
    if _A_REPORTS_THE_ASK.search(said):
        # The question word is inside the report, so only a question on the front of the line or
        # a question mark makes it an ask.
        return bool("?" in said or _ASKS_WITH_A_QUESTION_WORD.search(said)
                    or _ASKS_WITH_AN_AUXILIARY.match(said.strip())
                    or _ASKS_AFTER_A_COMMA_WORD.search(said.replace(" ,", ",")))
    if read.get("asks"):
        return True
    if read.get("intent") == "question":
        return True
    if "?" in said:
        return True
    return bool(_ASKS_WITH_A_QUESTION_WORD.search(said)
                or _ASKS_MID_LINE.search(said)
                or _ASKS_AFTER_A_COMMA.search(said.replace(" ,", ","))
                or _ASKS_WITH_AN_AUXILIARY.match(said.strip()))


def _as_typed(line):
    """The line exactly as it was typed, lower case and padded, signs and digits kept."""
    said = line.get("text") or line.get("clean") or ""
    if not isinstance(said, str):
        said = ""
    return " " + said.strip().lower() + " "


def _carried_on(read, previous, words):
    """The reading a short follow-up carries on from the last line, or None.

    After "how much is a single to leeds", "and a return" and "is it cheaper after 9" ask the same
    question about the same kind of thing, and read on their own they say nothing about it. The
    carry-on needs all of: this line read as a follow-up, few words, the last line's answer still
    standing, and a different line than the last one - so "and the icing" after a cake is not a
    price, and a reading written during the same turn never carries itself on.
    """
    if not isinstance(previous, dict) or not previous.get("over_time"):
        return None
    if not read.get("followup") or len(words) > _A_FOLLOW_UP_WORDS:
        return None
    if previous.get("text") and previous.get("text") == read.get("text"):
        return None
    return True, previous.get("over_time_what")


def _text(line):
    """The line for matching, in the spelling the writer meant, space-padded for whole words."""
    said = line.get("plain") or line.get("clean") or ""
    if not isinstance(said, str):
        said = ""
    return " " + said.strip().lower() + " "


# The thing itself, with no verb and no question in it, is the world's version asked for: "the
# news", "any headlines", "opening hours", "any delays on the trains this morning", "and the
# weather". A report about the same thing is not an ask, so a verb of being or seeming after the
# noun takes the line back: "the weather looks bad this weekend", "i heard the news".
_BARE_LIVE_LEAD = (r"^\s*(?:(?:and|so|but|then|also|ok|okay|right|oh)\s+|"
                   r"(?:what|how)\s+about\s+)?")


_A_BARE_LIVE = (
    ("news", re.compile(_BARE_LIVE_LEAD + r"(?:the\s+|any\s+|got\s+any\s+)?(?:news|headlines?)\b")),
    ("hours", re.compile(_BARE_LIVE_LEAD + r"(?:the\s+|any\s+)?(?:opening\s+(?:hours|times)|"
                                              r"opening|closing\s+time|bank\s+holiday\s+hours)\b")),
    ("timetable", re.compile(_BARE_LIVE_LEAD + r"(?:the\s+|any\s+)?(?:delays?|roadworks?|"
                                                  r"traffic|bus\s+times?|train\s+times?|"
                                                  r"departures|arrivals|timetable)\b")),
    ("weather", re.compile(_BARE_LIVE_LEAD + r"(?:the\s+|any\s+)?(?:weather|forecast)\b")),
    ("price", re.compile(_BARE_LIVE_LEAD + r"(?:the\s+|any\s+)?(?:price|prices|cost|costs|"
                                            r"fares?|ticket\s+prices?)\b")),
)


_A_REPORTS = re.compile(
    r"\b(?:looks?|looked|seems?|seemed|sounds?|sounded|feels?|felt|was|were|is|are|has|have|"
    r"had|said|says|told|hear|heard|got|get|gets|makes?|made|turns?|turned|went|goes|"
    r"coming|comes|hit|hits|does|doesnt|did|didnt|wont|cant|helps?|ruined|spoils?)\b")


# A line with no question in it that is nothing but the thing itself - "timetable for the 42",
# "bus times", "opening hours" - is a request for that thing. The class word has to be at the
# front, behind nothing but a determiner, and the line has to be no longer than the thing and
# its qualifier, so "i checked the timetable yesterday" and "the price went up again" stay
# statements.
_A_BARE_ASK = 4


# A line that is the thing itself runs a little longer than a bare noun: "any delays on the
# trains this morning" is five words and no verb.
_A_BARE_LIVE_WORDS = 9


# How long a follow-up can be and still be nothing but the question it carries on.
_A_FOLLOW_UP_WORDS = 7


# What may follow the thing itself in a short request for it: when, or a please.
_A_BARE_TAIL = re.compile(
    r"^(?:for|on|at|in|this|next|today|tonight|tomorrow|now|here|there|please|pls|thanks|ta|"
    r"anyone|anywhere)\b")


_A_DETERMINER = frozenset(("", "the", "a", "an", "any", "your", "this", "our", "these"))


def over_time(line, read, previous=None, carrying_on=False):
    """Whether the line asks about something that holds only for the day: (True/False/None, what).

    See the module docstring. `what` is the class of changing thing (`price`, `hours`,
    `weather`, `news`, `availability`, `timetable`, `rate`, `event`, `post`) when the answer is
    True, and None for the other two answers. `previous` is the last turn's reading, used only
    for a follow-up that says nothing of its own: `carrying_on` asks for that second look alone,
    once the reading of this line is complete, and answers None when the line carries nothing on.
    """
    read = read if isinstance(read, dict) else {}
    text = _text(line if isinstance(line, dict) else {})
    asking = _a_line_asks(read, text)
    words = text.split()
    bare = len(words) <= _A_BARE_ASK
    if asking and _A_HOW_IT_WORKS.search(text) and not _A_SAYS_NOW.search(text):
        return False, None
    # A sum is arithmetic, and a year that has gone is a date: both are settled before any class
    # is looked for, whichever live word sits next to them.
    if _A_ARITHMETIC.search(text) or _A_ARITHMETIC.search(_as_typed(line)):
        return False, None
    if (_SEALED_ASKS & set(read.get("asks") or ()) and _A_HAS_A_NUMBER.search(text)
            and not _A_AN_AMOUNT_OF_A_THING.search(text)):
        return False, None
    if (_A_PAST_YEAR.search(text) or _A_HOW_OLD_IS_THE_WORLD.search(text)
            or _A_HISTORY_ITSELF.search(text)):
        return False, None
    if _A_A_DIFFERENCE.search(text):
        return False, None
    # How hot, deep or heavy a named thing is is a measurement of that thing, not the sky here.
    if _A_HOW_A_THING_MEASURES.search(text) and not _A_WEATHER_HERE.search(text):
        return False, None
    # A traffic light is not traffic, and "the weather plan" is a plan about the weather.
    if _A_A_TRAFFIC_LIGHT.search(text):
        return None, None
    if _A_A_PLAN_ABOUT_THE_WEATHER.search(text) and not _A_WEATHER_HERE.search(text):
        return None, None
    # A quantity of a thing is a fact about the thing: how much water a bath holds, how much
    # water a day to drink, how much pasta for four. None of it is a figure the world sets.
    if (_A_HOW_MUCH_IT_HOLDS.search(text) or _A_HOW_MUCH_IS_IN.search(text)
            or _A_HOW_MUCH_ENOUGH.search(text) or _A_HOW_MUCH_A_FEELING.search(text)):
        return False, None
    if _A_AN_OCCASION_OF_THEIR_OWN.search(text):
        return None, None
    # A conversion is arithmetic and a measure of a unit is a fact about the unit, unless a money
    # word is in the line: "how much is a pint of milk" is what it costs.
    if not _MONEY.search(text) and (_A_A_CONVERSION.search(text)
                                    or _A_HOW_MUCH_OF_A_UNIT.search(text)):
        return False, None
    if _A_HOW_MUCH_I_SPENT.search(text) or _A_MY_OWN_FIGURE.search(text):
        return None, None
    if _A_THE_CLOCK.search(text):
        return None, None
    if _A_DID_YOU_SEE.search(text):
        return None, None
    if _A_BARE_RECORD.search(text) and not asking:
        return False, None
    # A word for freshness does not change what the thing is: "what is the latest score" is the
    # score and "the current price of petrol" is the price.
    fresh = _A_FRESHENING.sub(" ", text)
    if _A_WORD_MEANS.search(text):
        return False, None
    # The thing itself and nothing else is the world's version asked for.
    for what, pattern in _A_BARE_LIVE:
        found = pattern.search(fresh)
        if found and not _A_REPORTS.search(text) and len(words) <= _A_BARE_LIVE_WORDS:
            return True, what
    for what, pattern in _CHANGING:
        found = pattern.search(fresh)
        if not found:
            continue
        # A person's own plan is not a place's hours or a service's timetable.
        if what in ("hours", "timetable", "event") and _A_MY_OWN_PLAN.search(text):
            continue
        # "what is stamp duty", "what is inflation": the line asks what the live word itself is,
        # which is a definition and settles. With a determiner the line asks for the thing's
        # state instead - "what is the weather", "what is the price" - and stays live.
        if (_A_DEFINITION.search(text)
                and fresh[:found.start()].strip() in ("what is", "what are", "whats", "what's")
                and not fresh[found.end():].strip(" ?!.,")):
            return False, None
        if asking:
            return True, what
        # A short line that is the thing itself, with nothing said about it, is a request for
        # the world's version: "timetable for the 42", "bus times", "opening hours". A statement
        # about the thing is not - "inflation is 4", "the weather doesnt help" - so the line has
        # to run out after the class word, or carry only a tail that says when.
        if bare and not _A_REPORTS.search(text):
            tail = fresh[found.end():].strip()
            if (fresh[:found.start()].strip() in _A_DETERMINER
                    and (not tail or _A_BARE_TAIL.match(tail))):
                return True, what
    if carrying_on:
        return _carried_on(read, previous, words)
    if not asking:
        return None, None
    if _SEALED_ASKS & set(read.get("asks") or ()):
        return False, None
    for pattern in _SETTLED:
        if pattern.search(text):
            return False, None
    return None, None
