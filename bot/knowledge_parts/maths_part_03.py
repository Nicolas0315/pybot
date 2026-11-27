"""Part 3 of 6 of a large module, split out of `maths`.

Everything here is re-exported from `maths`, so callers import it from there as before.
"""
import re

from ..memory.saving import the_money_already_held, the_pot_said_alone
from .maths_part_01 import (
    _parse, _number,
)
from .maths_part_02 import (
    A_DEBT_CLEARED, OWED, SAID_A_RATE, SPENDING_CLAUSE, _sums, _user_lines, _worked_in_chat,
    _rate_in_chat, TIME_ASKED, TIME_ELSEWHERE, _duration_reply, A_HORIZON, RATE, _asks_a_new_sum,
    _last_takes, PERIODS, _each_hundred, WORKED,
)


def _goal_in_chat(memory, rate=None):
    """The biggest figure earlier in the chat that is a goal rather than a bill or a wage."""
    lines = _user_lines(memory)
    total = None
    # What the money is for can be said on a different line from the sum: "im trying to save up
    # for a car" / "i can put by 150 a month" / "the car is 2500". A reader that wanted a goal
    # word on the same line as the figure answered "how long will that take" by asking for the
    # figure again - the one the person had just given two turns earlier - so a plain sum in a
    # chat that already named a goal and a rate is the total being saved towards.
    a_goal_is_named = rate is not None and any(GOAL.search(line) for line in lines)
    owed = None
    for line in lines:
        if not GOAL.search(line) and not a_goal_is_named:
            continue
        if not GOAL.search(line) and SPENDING_CLAUSE.search(line):
            continue  # a bill or a wage, not what is being saved towards
        if the_pot_said_alone(line):
            # Money already in the pot is not the total being saved towards. A chat that said
            # "we need 8000 for a new kitchen" and then "weve got 3000 in savings" was told
            # "£3,000 at £250 a month is 12 months": the pot was read as the goal, and the
            # length it gave was for the money they already hold.
            continue
        if OWED.search(line) and not A_DEBT_CLEARED.search(line):
            # Money they are carrying, kept aside until nothing better is named: a chat about a
            # car that also mentions a loan saves towards the car.
            for value in _sums(SAID_A_RATE.sub(" ", line)):
                if rate and value < rate * 2:
                    continue
                if value >= 50 and (owed is None or value > owed):
                    owed = value
            continue
        for value in _sums(SAID_A_RATE.sub(" ", line)):
            # a total the rate has to work through is worth many of its payments
            if rate and value < rate * 2:
                continue
            if value >= 50 and (total is None or value > total):
                total = value
    if total is None:
        # "we can put away 400 a month" was answered "£20,000 at £400 a month is 50 months", so the
        # "how long would that take" after it is about the 20,000 the chat has already divided.
        total = _worked_in_chat(memory, rate)
    return total if total is not None else owed


def _rate_and_total(memory):
    """A rate per period and a total to reach, both stated in the chat, or (None, None, None)."""
    rate, period = _rate_in_chat(memory)
    if rate is None:
        return None, None, None
    total = _goal_in_chat(memory, rate)
    held = the_money_already_held(memory)
    if total and 0 < held < total:
        # The pot is not the goal: "im saving for a 15000 deposit" / "i have 4200 saved" /
        # "i put by 400 a month" / "when will i have enough" was answered "at 400 a month, 15,000
        # takes about 38 months", while the answer two turns earlier had worked out "£10,800
        # still to find ... 22 months". The chat had the figure and the arithmetic both, and the
        # last turn gave back the whole goal. What is still to find is the goal less the pot, the
        # same sum `bot/memory/saving.py` works out.
        total = total - held
    return rate, period, total


def _time_to_reach(clean, memory):
    """How long it takes to reach a total at a rate, when the chat said both and the line asks."""
    if not TIME_ASKED.search(clean) or TIME_ELSEWHERE.search(clean):
        return None
    if _parse(clean):
        return None  # the line brings its own numbers: the other forms answer those
    rate, period, total = _rate_and_total(memory)
    if not rate or not total:
        return None
    return _duration_reply(rate, period, total)


def _time_at_a_new_rate(clean, memory):
    """A rate the line itself proposes for the same total: "what if we do 700?"

    The question is implied, the way people ask it straight after an answer: the chat holds the
    total, the bot has just said how long it takes, and this line changes the rate.
    """
    if not _asks_a_new_sum(clean) or TIME_ELSEWHERE.search(clean):
        return None
    before = _last_takes(memory)
    if before is None:
        return None
    rate, period, total = _rate_and_total(memory)
    if not total:
        return None
    match = RATE.search(clean)
    numbers = _parse(clean)
    if match:
        rate, period = float(match.group("amount").replace(",", "")), match.group("period")
    elif len(numbers) == 1 and numbers[0] < total:
        if A_HORIZON.search(clean):
            return None  # "what if we want it done in 18 months" is a deadline, not a rate
        rate, period = numbers[0], before[1]
    else:
        return None  # a number bigger than the total is a different total, not a rate
    if not rate or not period:
        return None
    return _duration_reply(rate, period, total)


def _time_at_a_new_total(clean, memory):
    """A bigger price for the same saving rate: "and what if i find one for 6000, is that daft?"

    Same shape as the rate change, the other way round: the person keeps the money they can put
    away and asks about a dearer thing, which is a question about how much longer it takes.
    """
    if not _asks_a_new_sum(clean) or TIME_ELSEWHERE.search(clean):
        return None
    before = _last_takes(memory)
    if before is None:
        return None
    rate, period, total = _rate_and_total(memory)
    if not rate or not total:
        return None
    numbers = _parse(clean)
    if len(numbers) != 1 or numbers[0] <= total:
        return None
    dearer = numbers[0]
    count = dearer / rate
    old = total / rate
    nearest = round(count)
    said = _number(nearest if abs(count - nearest) < 0.05 else round(count, 1))
    name = period if count == 1 else period + "s"
    extra = round(count - old)
    more = f", so {_number(extra)} {name} more than {_number(total)}" if extra >= 1 else ""
    return (f"At {_number(rate)} a {period}, {_number(dearer)} takes {said} {name}{more}. "
            f"Only you know if the dearer one is worth the wait.")


def _time_without_a_goal(clean, memory):
    """A rate without a figure to reach yet: "how long would that take?"

    There is nothing to divide, so the answer says what the rate comes to in a year, what one
    hundred of the price costs in weeks at that rate, and asks for the one number that is missing.
    Better than a shrug, and it is the question they will ask next: "i put 20 by every week
    towards a bike" then "so how many weeks until i can buy it" was a search hedge, when 20 a
    week is five weeks for every 100 of the bike.
    """
    if not TIME_ASKED.search(clean) or TIME_ELSEWHERE.search(clean) or _parse(clean):
        return None
    rate, period = _rate_in_chat(memory)
    if not rate:
        return None
    if _goal_in_chat(memory, rate):
        return None  # there is a figure to reach, so _time_to_reach answers this
    yearly = rate * 12 / PERIODS[period]
    said = f"At {_number(rate)} a {period} that's about {_number(round(yearly))} a year"
    each_hundred = _each_hundred(rate, period)
    if each_hundred:
        said += f", so every 100 of the price takes {each_hundred}"
    return (said + ". Tell me the figure you are saving towards and I will work out how long "
            "it takes.")


# The figure has to be money being put by, not any number with a goal word beside it. "i want to
# run 100 miles" / "how long will it take" was answered "Getting to 100 depends on what you can put
# by", because GOAL counts "want" and the plan is a figure like any other.
MONEY_GOAL = re.compile(
    r"\b(?:save|saves|saving|saved|put by|put aside|set aside|put away|deposit|afford|owe|owes|"
    r"owed|debt|debts|repay|repaying|pay off|paying off|towards|toward)\b")


def _a_saving_goal_in_chat(memory):
    """The biggest figure on a line that says money is being put by."""
    best = None
    for line in _user_lines(memory):
        if not MONEY_GOAL.search(line) or SPENDING_CLAUSE.search(line):
            continue
        for value in _sums(SAID_A_RATE.sub(" ", line)):
            if value >= 50 and (best is None or value > best):
                best = value
    return best


def _the_plan_figure(memory):
    """The figure the **newest** plan names, if that plan is about money.

    "im trying to save 2000 for a used car" then "actually its 3000" leaves the plan reading
    "Save 3000 for a used car" (bot/memory/topics.py writes the correction), while the old sum is
    still on the first line of the chat. Reading the lines alone answered a later ask with 2,000.

    Only the newest plan, because a later plan is a new subject: "i want to run 100 miles" after the
    car leaves the store holding both, and the goal in hand is the run. A plan with no money word in
    it is not money at all, so this is also the fence that keeps 100 miles from being read as £100.
    """
    user = memory.get("user") or {}
    if not isinstance(user, dict):
        return None
    plans = [plan for plan in list(user.get("plans") or []) if plan]
    newest = plans[-1] if plans else user.get("plan")
    if not newest or not MONEY_GOAL.search(str(newest).lower()):
        return None
    sums = [value for value in _sums(str(newest)) if value >= 50]
    return max(sums) if sums else None


# The fallback when the sums at the rates people save at have already been said: the missing half
# of the sum is the rate, so that is what is asked for. Kept as words of its own so a test can hold
# on to it.
ASKED_FOR_RATE = "how much could you set aside each month?"


def _a_goal_without_a_rate(clean, memory):
    """A figure to reach but no rate to reach it at: "im trying to save 2000 for a used car" then
    "how long will it take".

    _time_without_a_goal is the same sum the other way round: with a rate and no figure, the answer
    says what the rate comes to in a year and asks for the figure. With a figure and no rate there
    is nothing to divide either, and the missing half is the one a friend asks for. Nothing said it,
    so the question was answered from the card for the thing being saved for - "ask how long they've
    owned it and why they're selling" - which is a question to put to a stranger about the car,
    not an answer about time.
    """
    if not TIME_ASKED.search(clean) or TIME_ELSEWHERE.search(clean) or _parse(clean):
        return None
    rate, _period = _rate_in_chat(memory)
    if rate:
        return None  # both halves are in the chat, so _time_to_reach divides them
    total = _the_plan_figure(memory)
    if total is None:
        user = memory.get("user") or {}
        if isinstance(user, dict) and (user.get("plan") or user.get("plans")):
            return None  # the plan in hand is not money, so this is a new subject
        total = _a_saving_goal_in_chat(memory)
    if not total:
        return None
    # The sums at the rates people save at are the answer money.py already gives a line that names
    # its own goal ("i need a deposit of 15000" / "how long will that take"), and it gives the same
    # one for a goal the chat named a turn earlier when the entry that carries it is reached. This
    # is the door for the bare follow-up, so the wording is theirs, not a second table.
    from ..knowledge.money import _time_to_save
    return (_time_to_save(memory, {"clean": clean, "text": clean})
            or f"Getting to {_number(total)} depends on what you can put by - {ASKED_FOR_RATE}")


# the exact words _time_without_a_goal uses, so the figure it asked for can be answered next turn
ASKED_FOR_FIGURE = "the figure you are saving towards"


# A line that does nothing but put a new total into the plan: "say i need 12000", "make it 15000".
# The words before the figure are the ones people say when they swap a number, and nothing else
# in the line, so the reply can only be about that number.
JUST_A_TOTAL = re.compile(
    r"^\s*(?:no[, ]+|actually[, ]+|okay[, ]+|ok[, ]+|well[, ]+)?"
    r"(?:say|lets say|let's say|make it|make that|call it|change it to|put it at)\s+"
    r"(?:i|we)?\s*(?:need|needs|want|wants)?\s*(?:about\s+|around\s+)?"
    r"£?([\d,.]+)\s*(k|thousand|pounds?|quid)?\s*[.!]*\s*$")


def _a_new_total_only(clean):
    """True when the whole line is a swap of the total: "say i need 12000"."""
    return bool(JUST_A_TOTAL.search((clean or "").strip()))


def _figure_just_given(clean, memory):
    """The total, given on the next line: "say i need 12000".

    _time_without_a_goal asked for one number, and when it arrives the question it stood in for
    ("how long will that take") is answered now that both numbers are in the chat. A chat that
    worked a time for its own total ("£20,000 at £200 a month is 100 months, about 8 years and
    4 months") is the same case without the asking: "say i need 12000" is that question again
    about 12,000, and asking for a figure the chat is already holding would be the worse answer.
    """
    turns = memory.get("turns") or []
    if not turns or not isinstance(turns[-1], dict):
        return None
    if TIME_ELSEWHERE.search(clean):
        return None
    said = turns[-1].get("bot") or ""
    if ASKED_FOR_FIGURE not in said and not (_a_new_total_only(clean)
                                             and WORKED.search(" ".join(said.split()))):
        # Either the bot asked for the figure, or it has just worked a time for the plan's own
        # total ("£20,000 at £200 a month is 100 months") and this line only puts another total
        # in its place: "say i need 12000" is the same question about 12,000. A line with more
        # in it than the total is not this one - "and what if i find one for 6000, is that daft"
        # asks how much worse off the dearer one leaves them, and has its own answer.
        return None
    numbers = _parse(clean)
    rate, period = _rate_in_chat(memory)
    if len(numbers) != 1 or not rate or numbers[0] < rate * 2:
        return None
    return _duration_reply(rate, period, numbers[0])


HOW_MUCH_EACH = re.compile(
    r"how much (?:should|do|would|will|can|need|have) (?:i|we)\b[^?]*\b(?:day|week|month)\b|"
    r"how much\b[^?]*\b(?:put away|put by|set aside|put aside|save each|save per)\b")


# The same question with no verb left in it: "how much a month", "how much would that be a week".
# The person has the total in front of them - they gave it a turn or two ago - and what they want is
# the one figure that comes out of a pay packet, not the card about the thing they are saving for.
# "im saving for a car" / "i need about 4000" / "how much a month" came back as a car-buying card
# about dealer targets. Only the whole line counts, so a real question that carries a rate word
# ("what is a gym a month") is somebody else's.
A_BARE_RATE_ASK = re.compile(
    r"^\s*(?:(?:and|so|ok|okay|right|but|then|well)\b[\s,]*)*"
    r"(?:how\s+much|what)\b"
    r"(?:\s+(?:would|will|do|should|could|does|did)\b"
    r"(?:[\s,]+(?:that|it|i|we|you)\b)?(?:[\s,]+(?:need|have|be|take|come\s+to)\b)?)?"
    r"\s+(?:a|per|each|every|once\s+a)\s+(?P<period>day|week|fortnight|month)\b"
    r"(?:\s+(?:would|will|could|should)\s+(?:that|it|this)\s+be\b)?"
    r"[\s?.!]*$", re.I)


# The period the person is asking about: "each week" wants a weekly figure, and answering it in
# months is answering a different question.
EACH_PERIOD = re.compile(r"\b(?:each|a|per|every|once a)\s+(day|week|fortnight|month)\b")


PERIODS_IN_A_YEAR = {"day": 365, "week": 52, "fortnight": 26, "month": 12}


# A deadline the person named and we cannot count to ("by december", "before christmas") makes
# any figure per week a guess about how much of the year is left, so this line stays quiet.
# A day of the month is a deadline too, and it is the one the store writes when a person puts a
# date right: "save 500 by june" / "no, the 4th of july" leaves "Save 500 by the 4th of July", and
# a reader that only knew month names counted to the first of the month or gave up and repeated
# the older answer with its older figure.
# "the end of december" is a deadline the same way "the end of the month" is, and it was the one
# form of it that did not match: the month names stood bare in the pattern, so the days left were
# counted nowhere and the goal fell back to whatever else the line said.
DEADLINE_NAMED = re.compile(
    r"\b(?:by|before|until|till|in time for|ready for)\s+(?:(?:the\s+)?\d{1,2}"
    r"(?:st|nd|rd|th)(?:\s+of)?\s+)?(?:christmas|easter|summer|the summer|"
    r"winter|the winter|next (?:week|month|year|summer|christmas|easter)|"
    r"the end of (?:the |next |this )?(?:month|year|week|january|february|march|april|may"
    r"|june|july|august|september|october|november|december)|"
    r"january|february|march|april|may|june|july|august|september|october|november|december)\b"
    r"|\bfor (?:christmas|the summer|summer|the holiday|our holiday)\b")


GOAL = re.compile(r"\b(?:save|saves|saving|saved|deposit|need|needs|want|wants|afford|"
                  r"cost|costs|price|budget|goal|target|towards|toward|for a|for the|owe|owes|"
                  r"owing|owed|debt|debts|repay|repaying|pay off|paying off)\b")


def _each_month_for_a_goal(clean, memory):
    """A figure to reach but no date: how much to put by each month."""
    bare = A_BARE_RATE_ASK.search(clean)
    if not (HOW_MUCH_EACH.search(clean) or bare):
        return None
    if _parse(clean) or TIME_ELSEWHERE.search(clean):
        return None
    total = _goal_in_chat(memory)
    if not total:
        return None
    if DEADLINE_NAMED.search(clean) or _a_deadline_in_chat(memory):
        # how much a week depends on how much of the time is left, and the chat named the time, so
        # the figure is worked out to the date rather than over a year the person never said.
        dated = _a_month_for_the_deadline_in_chat(total, memory)
        if not dated:
            return None
        return dated
    period = _asked_period(clean)
    per_year = PERIODS_IN_A_YEAR[period]
    year, two = total / per_year, total / (per_year * 2)
    return (f"Saving {_number(total)} over a year is about {_number(round(year))} a {period}; "
            f"over two years, about {_number(round(two))} a {period}.")


# A date the person names for a figure the chat already holds, said in months or years:
# "i want it in a year", "in six months", "within 2 years", "18 months from now".
HORIZON_SAID = re.compile(
    r"\b(?:in|within|inside|over|after)\s+(?P<count>\d+|an?|one|two|three|four|five|six|seven|"
    r"eight|nine|ten|eleven|twelve|couple\s+of|few)\s*(?P<unit>days?|weeks?|fortnights?|"
    r"months?|years?)\b(?:\s*(?:from now|time))?")


HORIZON_COUNTS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                  "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
                  "twelve": 12, "couple of": 2, "few": 3}


# "I saved 200 in 3 months" is a report of what happened, not a plan: the past tense means the
# time has already gone. The money the person still has to find is what these replies are for.
PAST_REPORT = re.compile(
    r"\b(?:saved|spent|paid|lent|borrowed|bought|earned|received|got|took|have had|ago)\b")


# A named date is a deadline the arithmetic can use: the time left between today and the date
# is what the monthly figure divides the goal by. "how do i save 3000 by christmas" was answered
# as a Christmas shopping budget on main, and "i want to save 5000 by next summer" not at all.
DEADLINE_DAYS = {"christmas": (12, 25), "the end of the year": (12, 31), "the end of the month": None,
                 "the end of the week": None, "next year": (1, 1), "next month": None,
                 "next week": None, "easter": None, "summer": (7, 1), "the summer": (7, 1),
                 "winter": (12, 1), "the winter": (12, 1)}


MONTH_NUMBERS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                 "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
                 "december": 12}


# "save 10k in 6 months" is money with a shorthand on it, not a race: the entries answer a
# distance when the line is about running, and this only reads a k as a thousand when the line
# also has a goal word in it.
K_THOUSANDS = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*k\b")


# The line itself has to be about putting money by, not just carry a date: "how do i budget for
# christmas" after a saving goal in the chat was answered with the goal's arithmetic instead of
# the Christmas shopping budget, and that is a different question.
# A date put on the thing already in the chat, with no saving word in it: "i want it by next
# summer", "we need it before june", "i have to have it by august". The figure is on the turn
# before, so this is the other half of one sum - and without it the line was read as a new plan
# and said back to the person ("It by next summer - fair enough. What's stopped it happening so
# far?"), which answers a question they did not ask.
A_DATE_FOR_THE_THING = re.compile(
    r"^\s*(?:(?:and|but|so|ok|okay|right|well|then)\b[\s,]*)*"
    r"(?:i|we)\s+(?:want|need|would\s+like|have\s+to\s+have|must\s+have|'d\s+like)\s+"
    r"(?:it|that|them|this)\b[^0-9]*\b(?:by|before|in\s+time\s+for)\b", re.I)


SAVE_VERB = re.compile(r"\b(?:save|saves|saving|saved|put by|put aside|set aside|put away|"
                       r"pay in|paying in)\b")


SAVING_CUE = re.compile(r"\b(?:save|saves|saving|saved|put by|put aside|set aside|put away|"
                        r"need|want|afford|goal|target|towards|toward|budget)\b")


def _k_as_money(clean):
    """The figure in a line that writes 10k, read as 10,000 when the line is about money.

    Only used by the goal arithmetic below, so a race stays a race: "how far is a 10k" has no
    goal word in it and is never read here.
    """
    found = K_THOUSANDS.search(clean)
    if not found or not SAVING_CUE.search(clean):
        return None
    amount = float(found.group(1)) * 1000
    return amount if amount >= 100 else None


def _easter_day(year):
    """The date of Easter Sunday, so "save 3000 by easter" has a date to count back from.

    The Gregorian rule in eight lines rather than a table: Easter is the first Sunday after the
    first full moon on or after 21 March, and the arithmetic below is the standard way to get
    that without a calendar lookup.
    """
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return month, day


A_DEADLINE_DAY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\s+(?:of\s+)?([a-z]+)\b", re.I)


def _the_last_day_of(month, today):
    """The day the month ends on: 31 for December, 30 for June, 28 or 29 for February."""
    import calendar

    year = today.year + (1 if month < today.month else 0)
    return calendar.monthrange(year, month)[1]


def _a_named_deadline(clean, today=None):
    """The date a line names for the money already in it: ("christmas", date) or None.

    The months and days left are what a per-month figure is for, so a date that can be read
    exactly is taken; a movable feast like Easter is left alone rather than guessed at.
    """
    import datetime
    today = today or datetime.date.today()
    found = DEADLINE_NAMED.search(clean)
    if not found:
        return None
    said = found.group(0).lower()
    name = said.split()[-1]
    a_day = A_DEADLINE_DAY.search(said)
    for phrase in ("the end of next month", "the end of this month", "the end of next week",
                   "the end of this week", "the end of next year", "the end of this year",
                   "the end of the year", "the end of the month",
                   "the end of the week",
                   "next summer", "next christmas", "next year", "next month", "next week",
                   "the summer", "the winter"):
        if phrase in said:
            name = phrase
            break
    if a_day and a_day.group(2) in MONTH_NUMBERS:
        month, day = MONTH_NUMBERS[a_day.group(2)], int(a_day.group(1))
        name = "the " + a_day.group(0).lower()
        if not 1 <= day <= 31:
            return None
    elif name in MONTH_NUMBERS:
        month = MONTH_NUMBERS[name]
        # "by december" is the month from its first day, but "by the end of december" is the last
        # one, and it was read as the first: said in mid-November, "i need to save 3000 by the end
        # of december" got "by december is 21 days away, so it is one pay packet" when there were
        # 51 days left. The words "end of" are the whole of what was dropped.
        at_the_end = "end of" in (said + " " + clean[max(0, found.start() - 12):found.start()])
        day = _the_last_day_of(month, today) if at_the_end else 1
        name = "the end of " + name if at_the_end else name
    elif name in ("next summer", "next christmas"):
        month, day = DEADLINE_DAYS[name.replace("next ", "")] or (7, 1)
    elif name == "easter":
        month, day = _easter_day(today.year)
    elif name in DEADLINE_DAYS and DEADLINE_DAYS[name]:
        month, day = DEADLINE_DAYS[name]
    elif name == "next month":
        year, month = (today.year + (today.month == 12), today.month % 12 + 1)
        return name, datetime.date(year, month, 1)
    elif name == "next week":
        return name, today + datetime.timedelta(days=7)
    elif name in ("the end of the month",):
        # The last day of this month, not the first of the next: "by the end of the month" said on
        # the 10th is 20 days away, and the first of next month is a day late and reads as a date
        # nobody named.
        return name, datetime.date(today.year, today.month, _the_last_day_of(today.month, today))
    elif name in ("the end of the week",):
        return name, today + datetime.timedelta(days=7 - today.weekday())
    elif name in ("the end of next month", "the end of this month"):
        # Counted from today, because the line names no month: the last day of next month, or of
        # this one. December needs the year moved on, which _the_last_day_of does not do.
        import calendar

        step = 1 if "next" in name else 0
        month = today.month + step
        year, month = today.year + (month - 1) // 12, (month - 1) % 12 + 1
        return name, datetime.date(year, month, calendar.monthrange(year, month)[1])
    elif name in ("the end of next year", "the end of this year", "the end of the year"):
        # The last day of the year rather than the first day of the next one: "i want it gone by
        # the end of next year" said in November is 415 days, and the phrase loop took "next
        # year" out of it and answered 51 - a year early, on a sum the person is paying interest
        # on. The year words have to be tested before "next year" for that reason.
        return name, datetime.date(today.year + (1 if "next" in name else 0), 12, 31)
    elif name in ("the end of next week", "the end of this week"):
        # The Sunday of the week in hand, and a week on when the person says next.
        return name, today + datetime.timedelta(days=7 - today.weekday() + (7 if "next" in name else 0))
    else:
        return None
    try:
        when = datetime.date(today.year, month, day)
        if when <= today:  # the date has gone this year, so it is next year's
            when = datetime.date(today.year + 1, month, day)
    except ValueError:  # "the 31st of february" is not a date, and a day that is not one is no
        return None  # deadline to count to
    return name, when


def _save_by_a_date(clean, memory):
    """A goal and a named date: what has to go by each month, and each week when it is close."""
    import datetime
    today = datetime.date.today()
    dated = _a_named_deadline(clean, today)
    if not dated:
        return None
    name, when = dated
    if PAST_REPORT.search(clean):
        return None
    total = _k_as_money(clean)
    if not total:
        numbers = [number for number in _parse(clean) if number >= 50]
        total = numbers[0] if len(numbers) == 1 else None
    if not total:
        if not SAVE_VERB.search(clean) and not A_DATE_FOR_THE_THING.search(clean):
            return None  # a date with no figure and no saving in it is someone else's question
        total = _goal_in_chat(memory)
    if not total:
        return None
    return _a_total_by_a_date(total, name, when, today)


def _a_total_by_a_date(total, name, when, today=None):
    """A total and a date: the figure that comes out of each pay packet, or None."""
    import datetime
    today = today or datetime.date.today()
    days = (when - today).days
    if days < 1:
        return None
    months = days / 30.44
    if months < 1.2:
        said = (f"\u00a3{_number(total)} by {name} is {days} days away, so it is one pay packet: "
                f"put the \u00a3{_number(round(total))} aside on payday before anything else")
    else:
        said = (f"\u00a3{_number(total)} by {name} is {days} days away, so about "
                f"\u00a3{_number(round(total / months))} a month")
        if days <= 120:
            # the week is what comes out of a pay packet, and rounding it up is what makes the
            # sum add up: the money entry's own weekly figure is worded the same way.
            weeks = -(-days // 7)
            a_week = -(-int(round(total)) // weeks)
            said += (f" - about \u00a3{_number(a_week)} a week over the {weeks} weeks left, which "
                     "is the number that actually comes out of a pay packet")
    return said + ". Take it off the top on payday rather than saving what is left at the end."


def _a_month_for_the_deadline_in_chat(total, memory):
    """The figure to the date the chat named: "how much a month" after a goal with a deadline.

    "im saving for a car" / "i need about 4000" / "i want it by next summer" / "how much a
    month" is one sum, and every number of it is already in the chat. The date is worked out the
    same way as when the person says it on the same line, so the two routes cannot disagree.
    """
    import datetime
    today = datetime.date.today()
    for line in reversed(_user_lines(memory)):
        dated = _a_named_deadline(line, today)
        if not dated:
            continue
        if PAST_REPORT.search(line):
            return None
        name, when = dated
        return _a_total_by_a_date(total, name, when, today)
    return None


def _deadline_for_a_goal(clean, memory):
    """A date on its own for a figure already in the chat: "i want it in a year".

    When both the goal and the time to reach it are known, the one number left is what it
    takes each month: 5,000 in a year is 417 a month. Without this the follow-up after "im
    saving for a car hoping to spend about 5000" was answered as small talk, and the person
    still had to do the division themselves. The line has to carry the date and nothing else:
    a line with its own figure or rate is a different sum, and the forms above answer it.
    """
    said = HORIZON_SAID.search(clean)
    if not said or TIME_ELSEWHERE.search(clean) or DEADLINE_NAMED.search(clean):
        # "by christmas", "by june", "by next summer": the date is read from the calendar and
        # the monthly figure worked out from the days left.
        return None if not DEADLINE_NAMED.search(clean) else _save_by_a_date(clean, memory)
    raw = said.group("count")
    count = float(raw) if raw.isdigit() else HORIZON_COUNTS.get(" ".join(raw.split()))
    if not count or RATE.search(clean):
        return None
    rest = (clean[:said.start()] + " " + clean[said.end():]).strip()
    numbers = _parse(rest)
    short_hand = _k_as_money(clean)
    if short_hand:
        # "10k" is read by _parse as 10, so the k has to win outright or the goal looks like
        # ten pounds and the line is passed on.
        numbers = [short_hand]
    if numbers:
        # a figure on the same line is the goal when it is one ("im saving 4000 and i want it
        # in 18 months"); anything else is a different question and stays out of this
        if len(numbers) != 1 or not GOAL.search(rest) or numbers[0] < 50:
            return None
        if PAST_REPORT.search(rest):
            return None  # a sum that has already happened is not a plan
        total = numbers[0]
    else:
        total = _goal_in_chat(memory)
    if not total:
        return None
    unit = said.group("unit").rstrip("s")
    months = count * PERIODS[unit]
    if months < 1 or months > 600:
        return None
    per = total / months
    if per < 1:
        return None
    when = ("a " + unit) if count == 1 else f"{_number(count)} {unit}s"
    return (f"{_number(total)} in {when} is {_number(round(per))} a month. "
            "Set the transfer for the day after payday so the money goes before you can spend it.")


def _asked_period(clean):
    """The period the line asks about, month when it names none."""
    asked = EACH_PERIOD.search(clean or "")
    return asked.group(1) if asked else "month"


def _a_deadline_in_chat(memory):
    """Whether the chat named a deadline ("by december") that a per-month figure would ignore."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    return any(DEADLINE_NAMED.search(turn.get("user") or "")
               for turn in turns[-4:] if isinstance(turn, dict))


def _saving(clean):
    """A monthly or weekly amount from "save 480 pounds in 6 months"."""
    if not any(word in clean for word in ("need", "want", "should", "how much", "each", "per",
                                          "plan")):
        return None
    amount = re.search(r"(?:save|saving|saved)\s+(?:up\s+)?[£$€]?\s*([\d,.]+)", clean)
    when = re.search(r"(?:in|over|within)\s+(\d+)\s*(month|week|year)s?", clean)
    if not amount or not when:
        return None
    total = float(amount.group(1).replace(",", ""))
    count = int(when.group(1))
    unit = when.group(2)
    if unit == "year":
        count, unit = count * 12, "month"
    if count < 1:
        return None
    per = total / count
    return f"Saving {_number(total)} over {count} {unit}s is {_number(per)} a {unit}."


def _average(clean):
    match = re.search(r"average(?: of)?\s+(.+)", clean)
    if not match:
        return None
    numbers = _parse(match.group(1))
    if len(numbers) < 2 or any(word in match.group(1) for word in ("speed", "month", "year")):
        return None
    mean = sum(numbers) / len(numbers)
    return f"The average is {_number(mean)}."


_LENGTH_UNIT = {
    "m": "m", "metre": "m", "metres": "m", "meter": "m", "meters": "m",
    "cm": "cm", "centimetre": "cm", "centimetres": "cm", "centimeter": "cm",
    "centimeters": "cm",
    "mm": "mm", "millimetre": "mm", "millimetres": "mm", "millimeter": "mm",
    "millimeters": "mm",
    "ft": "ft", "foot": "ft", "feet": "ft",
    "in": "in", "inch": "in", "inches": "in",
    "yd": "yd", "yard": "yd", "yards": "yd",
    "km": "km", "kilometre": "km", "kilometres": "km", "kilometer": "km",
    "kilometers": "km",
}


_LENGTH = (r"(?:m|cm|mm|km|ft|feet|foot|in|inch|inches|yd|yard|yards|metres?|meters?|"
           r"centimetres?|centimeters?|millimetres?|millimeters?|kilometres?|kilometers?)")


# one side, with a unit that may be missing on every side but the first
_SIDE = rf"(\d+(?:\.\d+)?)\s*({_LENGTH})?"


_SIDE_BY_SIDE = re.compile(
    rf"{_SIDE}\s*(?:by|x|×|\*)\s*(\d+(?:\.\d+)?)\s*({_LENGTH})?"
    rf"(?:\s*(?:by|x|×|\*)\s*(\d+(?:\.\d+)?)\s*({_LENGTH})?)?"
)


# "12 square metres" as a whole: the answer is in the unit the question was asked in
_SQUARE_WORD = {"m": "square metres", "cm": "square centimetres", "mm": "square millimetres",
                "ft": "square feet", "in": "square inches", "yd": "square yards",
                "km": "square kilometres"}


# The ask that wants a measurement of a surface, rather than a fact about shape words.
# The asks that want a measurement of a surface. The materials that are bought by area are in
# the list too: "how much carpet for a 4m by 3m room" is a question whose first number is the
# area, and 12 square metres is the answer that gets somebody to the shop counter.
_AREA_ASK = ("area", "how big", "how much space", "square metres", "square meters",
             "square feet", "square foot", "m2", "sqm", "floor area",
             "carpet", "flooring", "laminate", "lino", "tiles", "tiling", "turf", "lawn",
             "patio", "decking", "shed base", "gravel", "bark", "chippings")


_PERIMETER_ASK = ("perimeter", "skirting", "edging", "border", "how much fence", "fencing",
                  "how much beading", "trim for the edge", "goes all the way round")


def _sides(clean):
    """The side lengths named in a line as (value, unit, unit_from_the_line), or None.

    "a 4m by 3m room" gives 4m and 3m; "12ft x 10ft" gives 12ft and 10ft; "a 4 by 3"
    gives two bare numbers and no unit at all, which is still a rectangle somebody drew.
    """
    found = _SIDE_BY_SIDE.search(clean)
    if not found:
        return None
    sizes = []
    for value_at, unit_at in ((1, 2), (3, 4), (5, 6)):
        raw = found.group(value_at)
        if raw is None:
            continue
        unit = _LENGTH_UNIT.get(found.group(unit_at) or "", None)
        sizes.append((float(raw), unit))
    if len(sizes) < 2:
        return None
    # A unit given once carries down the line: "4m by 3" is 4 metres by 3 metres. With no
    # unit at all - "a 5 by 4 room" - the two numbers are still the two sides of something
    # real, so the pair comes back with no unit and the answer names both readings.
    named = next((unit for _, unit in sizes if unit), None)
    if named is None:
        return sizes, None
    return [(value, unit or named) for value, unit in sizes], named


# A shape named in the line is a shape, not a floor: "a 2 by 2 square has what area" and
# "area of a 6 by 4 rectangle" already have their own rows, which say "That rectangle's area is
# 24" - naming the shape back is the right answer, and "A 6 by 4 floor is 24 square metres if
# those are metres" is not. "square" is only a shape when it is not the unit ("square metres").
_SHAPE = re.compile(r"\b(?:rectangle|rectangular|oblong|triangle|triangular|circle|circular|"
                    r"square)\b(?!\s*(?:metres?|meters?|m|cm|mm|km|ft|feet|foot|inches?|"
                    r"yards?|yd)\b)")


# The unit the answer is wanted in, when the line asks for a different one from the sides:
# "what is 4m x 3m in square feet" is a square-feet question with metres in it.
_AREA_TARGET = (("square feet", "ft"), ("square foot", "ft"), ("sq ft", "ft"),
                ("square metres", "m"), ("square meters", "m"), ("square metre", "m"),
                ("square meter", "m"), ("m2", "m"), ("sqm", "m"),
                ("square yards", "yd"), ("square inches", "in"),
                ("square centimetres", "cm"), ("square centimeters", "cm"))


# one square metre, in the unit
_METRES_SQUARED = {"m": 1.0, "cm": 0.0001, "mm": 0.000001, "km": 1000000.0,
                   "ft": 0.09290304, "in": 0.00064516, "yd": 0.83612736}


# The thing being measured, named the way the line named it: "how much turf for a 5m by 4m
# lawn" is a lawn and not a floor. The first word found wins, and "floor" is the fallback.
_SURFACES = (("lawn", "lawn"), ("garden", "garden"), ("patio", "patio"), ("decking", "deck"),
             ("driveway", "driveway"), ("wall", "wall"), ("ceiling", "ceiling"),
             ("roof", "roof"), ("floor", "floor"), ("room", "room"), ("table", "table"),
             ("field", "field"), ("greenhouse", "greenhouse"), ("shed", "shed"),
             ("pond", "pond"), ("border", "border"))


def _surface(clean):
    """The word for the thing whose size was asked, or "floor" when the line names none."""
    for word, label in _SURFACES:
        if re.search(rf"\b{word}\b", clean):
            return label
    return "floor"


def _square_text(value, unit):
    word = _SQUARE_WORD.get(unit, "square units")
    return f"{_number(round(value, 2))} {word}"


# A count asked for by number is not an area: "how many tiles for a 3m by 2m wall" wants the
# tile count, which needs the size of a tile, so that line is left to the row that lays them.
# The thing counted is often named with a word in front of it - "how many decking boards",
# "how many skirting boards", "how many paving slabs for a 4 by 3 patio" - so up to three words
# may sit between "how many" and the noun; the noun still has to be the counted thing.
# The material does not have to follow "how many" at once - "how many paving slabs" and "how many
# plasterboard sheets" are counts - but the words in between are the material's own description,
# never a pronoun or a verb: a gap that took any three words read "how many rooms should we block"
# as a count of concrete blocks.
_COUNTED_GAP = (r"(?:(?!\b(?:i|we|you|they|he|she|it|to|do|does|did|should|could|would|can|"
                r"will|may|might|must|shall|is|are|was|were|be|am|have|has|had|not)\b)\w+\s+){0,3}")


_COUNTED = re.compile(r"\bhow many\s+" + _COUNTED_GAP + r"(?:tiles?|rolls?|packs?|bags?|cans?|tins?|"
                      r"boards?|planks?|squares|lengths?|coats?|slabs?|bricks?|blocks?|"
                      r"panels?|posts?|sheets?)\b")


# A material that is bought by the bag, the roll or the tonne is the materials table's
# question: "how much gravel for a 4m by 3m drive" wants the bags of gravel, and on main it got
# 12 square metres and went off to work out the rest itself. Asking the unit is still this row's
# question, so only the buying words hand the line over.
# Concrete, the ballast and the cement it is mixed from are bought the same way as gravel, by
# the cubic metre and the bag: "how much concrete do i need for a 2m by 2m shed base" was this
# row's 2 x 2 = 4 square metres instead of 0.4 cubic metres of concrete.
_BOUGHT_BY_THE_BAG = ("gravel", "shingle", "chippings", "bark", "mulch", "woodchip", "topsoil",
                      "soil", "compost", "manure", "sand", "slabs", "paving", "turf", "underlay",
                      "grout", "tile adhesive", "adhesive",
                      "concrete", "postcrete", "post mix", "ballast", "cement", "mortar")


_BUYING = re.compile(r"\bhow (?:much|many)\b")


def _floor_area(clean):
    """"a 4m by 3m room": the two sides of a surface, multiplied."""
    if not any(phrase in clean for phrase in _AREA_ASK):
        return None
    if _BUYING.search(clean) and any(word in clean for word in _BOUGHT_BY_THE_BAG):
        return None
    if _COUNTED.search(clean) or _SHAPE.search(clean):
        return None
    found = _sides(clean)
    if not found:
        return None
    sizes, unit = found
    area = sizes[0][0] * sizes[1][0]
    thing = _surface(clean)
    if unit is None:
        # no unit named: the number is right either way, so say which units give which answer
        return (f"A {_number(sizes[0][0])} by {_number(sizes[1][0])} {thing} is "
                f"{_number(round(area, 2))} square metres if those are metres, "
                f"{_number(round(area, 2))} square feet if they are feet.")
    sides = " by ".join(f"{_number(value)}{unit}" for value, _ in sizes[:2])
    # The answer is in the unit the question asked for, when the line names one that the
    # sides are not in: "what is 4m x 3m in square feet" wants square feet.
    target = next((to for word, to in _AREA_TARGET if word in clean), unit)
    if target != unit and target in _METRES_SQUARED and unit in _METRES_SQUARED:
        wanted = round(area * _METRES_SQUARED[unit] / _METRES_SQUARED[target], 2)
        return (f"A {sides} {thing} is {_square_text(wanted, target)}, which is "
                f"{_square_text(area, unit)}. That is the two sides multiplied: "
                f"{_number(sizes[0][0])} x {_number(sizes[1][0])}.")
    return (f"A {sides} {thing} is {_square_text(area, unit)}. "
            f"That is the two sides multiplied: {_number(sizes[0][0])} x "
            f"{_number(sizes[1][0])}.")


def _perimeter_of_a_room(clean):
    """"the skirting for a 4m by 3m room": the two sides added, then doubled."""
    if not any(phrase in clean for phrase in _PERIMETER_ASK):
        return None
    found = _sides(clean)
    if not found:
        return None
    sizes, unit = found
    length, width = sizes[0][0], sizes[1][0]
    if _SHAPE.search(clean):
        return None
    # "how much skirting for a 4m by 3m room" stops one step short with the perimeter alone: the
    # skirting is sold in 2.4m lengths, so the home row counts the lengths as well. Anything else
    # that asks how much edging or border a size takes still has its answer here.
    if re.search(r"\b(?:how many|how much)\s+(?:\w+\s+){0,2}skirting\b", clean):
        return None
    around = 2 * (length + width)
    thing = _surface(clean)
    if unit is None:
        return (f"A {_number(length)} by {_number(width)} {thing} has a perimeter of "
                f"{_number(round(around, 2))} metres if those are metres: twice "
                f"({_number(length)} + {_number(width)}).")
    return (f"A {_number(length)}{unit} by {_number(width)}{unit} {thing} has a perimeter of "
            f"{_number(round(around, 2))}{unit}: twice "
            f"({_number(length)} + {_number(width)}). That is how much skirting, edging or "
            f"border it takes.")


def _area(clean):
    sized = _floor_area(clean)
    if sized:
        return sized
    if not any(phrase in clean for phrase in ("area", "how big", "how much space")):
        return None
    if "circle" in clean:
        radius = re.search(r"radius(?: of| is)?\s*([\d,.]+)", clean)
        if radius:
            r = float(radius.group(1).replace(",", ""))
            return f"A circle with radius {_number(r)} has an area of {_number(3.14159265 * r * r)}."
        diameter = re.search(r"diameter(?: of| is)?\s*([\d,.]+)", clean)
        if diameter:
            r = float(diameter.group(1).replace(",", "")) / 2
            return f"A circle with diameter {_number(r * 2)} has an area of {_number(3.14159265 * r * r)}."
        return "The area of a circle is π × radius²: square the radius, then multiply by 3.14."
    if "triangle" in clean:
        numbers = _parse(clean)
        if len(numbers) >= 2:
            return f"That triangle's area is {_number(numbers[0] * numbers[1] / 2)}."
        return "The area of a triangle is ½ × base × height."
    if "rectangle" in clean or "square" in clean:
        numbers = _parse(clean)
        if len(numbers) >= 2:
            return f"That rectangle's area is {_number(numbers[0] * numbers[1])}."
        return "The area of a rectangle is length × width."
    return None


# Words that may trail a month question without changing it: "how many days in june this year",
# "how many days does august have again". The year itself is read off the same tail.
_MONTH_TAIL = (r"(?:\s+(?:this year|next year|this time|again|now|already|exactly|in total|"
               r"left|to go|please|though|then|anyway)|\s+(?:19|20)\d\d|"
               r"\s*,\s*[^.?!]{0,60}|"
               r"\s+(?:i|we)\s+(?:always\s+|never\s+|keep\s+)?(?:forget(?:ting)?|mix(?:ing)? "
               r"(?:it|them) up|get\s+(?:it|them)\s+mixed up))*")


def _month_year(text):
    """The year a month question names, if it names one ("this year" is the current one)."""
    import datetime
    today = datetime.date.today()
    if re.search(r"\bnext year\b", text):
        return today.year + 1
    if re.search(r"\b(?:this year|this time)\b", text):
        return today.year
    found = re.search(r"\b(?:in |of )?((?:19|20)\d\d)\b", text)
    if found:
        return int(found.group(1))
    return None


def _leap(year):
    """Whether February has 29 days in that year (the rule, not a table)."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


# Words that may trail the ask without changing it: "how many days till christmas this year".
_CHRISTMAS_TAIL = (r"(?:\s+(?:this year|next year|this christmas|next christmas|now|again|yet|"
                   r"already|exactly|left|to go|from now|from today|at the moment|please|then))*"
                   # the unit asked for at the end: "how long till christmas in weeks"
                   r"(?:\s+(?:in|as) (?P<unit2>days?|weeks?|sleeps?))?"
                   # a named year: "how many days till christmas 2027"
                   r"(?:\s+(?P<year>\d{4}))?")


# Words for the day itself, so "'til xmas" and "till crimbo" count. Christmas Eve is the day
# before, so it is counted from 24 December and named back the way it was asked about.
_CHRISTMAS_DAY = r"(?:christmas(?: day| eve)?|xmas(?: day| eve)?|crimbo)"


def _christmas_name(text):
    """The day the line asked about: "Christmas Eve" when it said eve, else Christmas."""
    said = str(text or "")
    return "Christmas Eve" if re.search(r"\b(?:christmas|xmas) eve\b", said) else "Christmas"


def _christmas_date_of(text, year):
    """Christmas Day or Christmas Eve in `year`, whichever the line named."""
    import datetime
    return datetime.date(year, 12, 24 if _christmas_name(text) == "Christmas Eve" else 25)


# The countdown, spelled out: every way of asking how long the wait is (#385 kept the whole
# line match; this widens it to the shapes people actually type). The unit is captured, so
# "how many weeks until christmas" comes back in weeks rather than always in days.
_CHRISTMAS_COUNTDOWN = (
    r"(?:"
    r"(?:how many |how much longer |how long )?"
    # "how many **more** days till christmas": the word people add sits between the ask and
    # the unit, and a whole-line match is unforgiving about it.
    r"(?:shopping )?(?:more |still )?(?P<unit>days?|weeks?|months?|sleeps?) "
    # "how many days are left until", "days there left", "days do we have left": a short
    # phrase may sit between the unit and "until", and missing it sent the line to the
    # search shrug or, with "shopping", to the roast-timing entry (#general 3830).
    r"(?:is it |are there |are left |left |to go |still |have i got left |have i got )?"
    r"(?:(?:are|is|there|left|to go|still|do we have|have we got|is it|was it|are they)\s+){0,3}"
    r"(?:until|'?till?|to|before) " + _CHRISTMAS_DAY +
    r"|(?:days|weeks) (?:until|'?till?|to|before) " + _CHRISTMAS_DAY +
    r"|how long (?:is it |have i got |has it been )?(?:until|'?till?|to|before) "
    + _CHRISTMAS_DAY +
    r"|how long (?:is it )?to go until " + _CHRISTMAS_DAY +
    r"|countdown to " + _CHRISTMAS_DAY +
    # "shopping days are left", "shopping days to go": no "until christmas", the words
    # themselves are the question.
    r"|(?:how many )?shopping days (?:are )?(?:left|to go)" +
    # "is it nearly christmas", "is it christmas day today": the date, not the count.
    r"|is it (?:almost|nearly|close to) " + _CHRISTMAS_DAY + r"(?: yet)?"
    r"|is it " + _CHRISTMAS_DAY + r"(?: (?:today|yet|this year))?"
    # "christmas countdown" is the same ask with the words the other way round.
    r"|(?:the )?" + _CHRISTMAS_DAY + r" countdown"
    r")")


# The plainest way to ask for the date itself: "when is christmas", "what date is xmas".
_CHRISTMAS_DATE = (
    r"(?:whens|when(?:'s| is| will it be)|what date is|what day is|which day is|"
    r"whats the date of)"
    r"(?: christmas| xmas| christmas day|xmas day| christmas eve|xmas eve"
    r"| christmas this year)?")


# "is christmas on a friday this year", "what day of the week is christmas": the day of the
# week comes from the calendar, so the line is answered from the date rather than a table.
_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


_CHRISTMAS_WEEKDAY = (
    r"(?:what day of the week (?:is|does) |what weekday (?:is|does) "
    r"|which day of the week (?:is|does) )?" + _CHRISTMAS_DAY +
    r"(?: fall| falls| land| lands)?(?: on)?(?: this year| this christmas)?"
    r"|is " + _CHRISTMAS_DAY + r"(?: this year| this christmas)? on a "
    r"(?P<guess>" + "|".join(_WEEKDAYS) + r")")


# "is it christmas today" is a yes-or-no, so it gets the answer and the count, not just one.
_CHRISTMAS_TODAY = r"(?:is it|is) (?:christmas|xmas)(?: day)?(?: today| yet| this year)?"


# "is christmas early or late this year": asking a fixed date to be early or late is the same
# question as asking its date, so the answer says the date does not move.
_CHRISTMAS_FIXED = (
    r"(?:is|was|is it|was it) (?:christmas|xmas)(?: day)?(?: this year| next year| this christmas)?"
    r"\s+(?:(?:early|late)\s+or\s+(?:early|late)|early|late)"
    r"(?: this year| next year| this christmas)?"
)


_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
