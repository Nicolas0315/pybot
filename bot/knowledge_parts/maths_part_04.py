"""Part 4 of 6 of a large module, split out of `maths`.

Everything here is re-exported from `maths`, so callers import it from there as before.
"""
import re

from .maths_part_01 import (
    MONTHS,
)
from .maths_part_03 import (
    _MONTH_TAIL, _leap, _month_year, _christmas_date_of, _christmas_name, _CHRISTMAS_COUNTDOWN,
    _CHRISTMAS_DATE, _CHRISTMAS_FIXED, _CHRISTMAS_TAIL, _CHRISTMAS_TODAY, _CHRISTMAS_WEEKDAY,
    _CHRISTMAS_DAY, _WEEKDAYS,
)


def _days_in_month(clean):
    """How long one month is, when that is the whole question.

    The month has to be the thing asked about: "how many days in February" and "how
    many days does August have" are questions about a month, while "how many days
    should I take off in August" is a question about leave that happens to name a
    month, and "August has 31 days" would be a wrong answer to it.
    """
    text = _plain(clean)
    for month, days in MONTHS.items():
        if re.fullmatch(rf"(?:how many days (?:are there )?in (?:the month of )?{month}|"
                        rf"how many days (?:does|do) {month} have|"
                        rf"how many days (?:do i have|have i got|are left) in {month}|"
                        rf"{month} has how many days)" + _MONTH_TAIL, text):
            year = _month_year(text)
            if month == "february":
                if year is not None:
                    longer = _leap(year)
                    return (f"February {year} has {29 if longer else 28} days: "
                            f"{year} is {'a leap year' if longer else 'not a leap year'}.")
                return ("February has 28 days in an ordinary year and 29 in a leap year. Leap "
                        "years are divisible by 4, except centuries unless they divide by 400.")
            if year is not None:
                return f"{month.capitalize()} {year} has {days} days."
            return f"{month.capitalize()} has {days} days."
    # "how many days in a leap year": no month named, and the answer is the length of the
    # year rather than of February, which is what the February row above explains.
    if re.fullmatch(rf"(?:how many |how long )(?:days? )?(?:are there |does |is |has )?"
                    rf"(?:in )?(?:a |one |the )?leap year"
                    rf"(?: have| last| long| then| again)?{_MONTH_TAIL}",
                    text):
        return ("A leap year has 366 days: 29 February, and the rest of the year as usual. "
                "The rule is every four years, except centuries unless they divide by 400.")
    return None


def _christmas_day(text=""):
    """The Christmas Day the line means, and how many days away it is (negative once past).

    A word that names the year decides which Christmas is meant: "until christmas next year"
    is twelve months after the one "until christmas" counts, so answering it with this year's
    number is a year out and said with confidence. "this year" in late December has already
    gone, and the countdown says so instead of quietly counting next year's.
    """
    import datetime
    today = datetime.date.today()
    said = str(text or "")
    if re.search(r"\bnext (?:year|christmas)\b", said):
        christmas = _christmas_date_of(said, today.year + 1)
    else:
        christmas = _christmas_date_of(said, today.year)
        if christmas < today and not re.search(r"\bthis (?:year|christmas)\b", said):
            christmas = _christmas_date_of(said, today.year + 1)
    return christmas, (christmas - today).days


def _wait_text(days, name="Christmas"):
    """How the wait reads: ahead of us, today, or already gone this year."""
    if days == 0:
        return f"{name} is today."
    if days < 0:
        ago = -days
        return f"{name} this year was {ago} day{'' if ago == 1 else 's'} ago."
    return f"{days} days until {name}."


def _months_between(start, when):
    """Whole months from one day to another on the calendar, and the days left over.

    A month is a calendar month, not thirty days: from 9 November to 25 December is one month
    and sixteen days, and thirty-day arithmetic would call it one month and two weeks. The
    month is taken with the day clamped (`_month_on`), so 31 January plus a month is the end of
    February rather than something that does not exist.
    """
    months = (when.year - start.year) * 12 + (when.month - start.month)
    if months > 0 and _month_on(start, months) > when:
        months -= 1
    return months, (when - _month_on(start, months)).days


def _count_in(unit, days, when=None):
    """The count in the unit the line asked for, so "in weeks" comes back in weeks.

    `when` is the date being counted to, when the line asked for months: that unit is counted
    on the calendar, so the answer says how many months and days away it is rather than
    dividing by thirty.
    """
    import datetime
    unit = (unit or "days").lower()
    if unit.startswith("sleep"):
        return f"{days} sleeps"
    if unit.startswith("week"):
        weeks, spare = divmod(days, 7)
        if not spare:
            return f"{weeks} weeks"
        return f"{weeks} weeks and {spare} day" + ("" if spare == 1 else "s")
    if unit.startswith("month"):
        if when is not None and days > 0:
            # The start is taken from the count itself, so the two arguments always agree even
            # if a caller works the days out differently.
            start = when - datetime.timedelta(days=days)
            months, spare = _months_between(start, when)
        else:
            months, spare = divmod(days, 30)
        if months and spare:
            return (f"{months} month{'' if months == 1 else 's'} and "
                    f"{spare} day{'' if spare == 1 else 's'}")
        if months:
            return f"{months} month{'' if months == 1 else 's'}"
        return f"{spare} day{'' if spare == 1 else 's'}"
    return f"{days} days"


def _shopping_days(days):
    """How many of the days before Christmas are days the shops are open.

    Sundays do not count: the big shops in Britain are shut or on short hours, so the number
    people mean by "shopping days" is the count without them. It is always given with the
    plain number of days, because the two are different and both are useful.
    """
    import datetime
    today = datetime.date.today()
    sundays = 0
    for step in range(1, days):
        if (today + datetime.timedelta(days=step)).weekday() == 6:
            sundays += 1
    return days - sundays


def _countdown_text(found, text):
    """The countdown in the unit that was asked for, and for the year that was named."""
    import datetime
    groups = found.groupdict()
    unit = groups.get("unit2") or groups.get("unit")
    year = groups.get("year")
    name = _christmas_name(text)
    christmas, days = _christmas_day(text)
    if year:
        christmas = _christmas_date_of(text, int(year))
        days = (christmas - datetime.date.today()).days
        if days < 0:
            ago = -days
            return f"{name} {year} was {ago} day{'' if ago == 1 else 's'} ago."
        if days == 0:
            return f"{name} {year} is today."
        return f"{_count_in(unit, days, christmas)} until {name} {year}."
    if days < 0:
        return _wait_text(days, name)
    if days == 0:
        return f"{name} is today."
    if re.match(r"is it\b", text):
        # "is it nearly christmas" is a yes/no question: answer it and then say how far off.
        return f"Not yet - {_count_in(unit, days, christmas)} until {name}."
    if "shopping day" in text:
        return (f"{days} days until {name} - {_shopping_days(days)} of them shopping days.")
    return f"{_count_in(unit, days, christmas)} until {name}."


def _days_until(clean):
    """A countdown to Christmas, only when the line asks for one.

    "How many days until Christmas" is a countdown; "what should I buy my sister for
    Christmas" is a shopping question that must not be answered with a number. The whole
    cleaned line has to be that question, so a mention in passing never counts, and the ask
    is spelled out in the pattern rather than guessed at with a second list of phrases.
    """
    text = _plain(clean)
    if re.fullmatch(_CHRISTMAS_TODAY, text):
        _, days = _christmas_day("")
        if days == 0:
            return "Yes - it's Christmas Day today."
        # The wording main already uses for "is it christmas day today", so the two shapes of
        # the same question answer alike.
        return f"Not yet - {days} days until Christmas."
    # Christmas Day does not move, so "is christmas early or late this year" has an answer
    # rather than a hedge: the question only makes sense about a date that moves, and saying so
    # is more use than "I'd rather not guess". It sits after the countdown forms so it can never
    # take "is it nearly christmas" or "is christmas on a friday".
    if re.fullmatch(_CHRISTMAS_FIXED, text):
        name = _christmas_name(text)
        when, days = _christmas_day(text)
        if days == 0:
            return f"{name} is today, 25 December, the same date every year."
        if days < 0:
            return (f"{name} is always 25 December, so it is neither early nor late: "
                    f"it was on {when.day} {_MONTH_NAMES[when.month - 1]} {when.year}.")
        return (f"{name} is always 25 December, so it is neither early nor late: it is "
                f"{days} days away.")
    found = re.fullmatch(_CHRISTMAS_COUNTDOWN + _CHRISTMAS_TAIL, text)
    if found:
        return _countdown_text(found, text)
    guessing = re.fullmatch(_CHRISTMAS_WEEKDAY + _CHRISTMAS_TAIL, text)
    if guessing:
        return _weekday_text(text, guessing.groupdict().get("guess"))
    found = re.fullmatch(_CHRISTMAS_DATE + _CHRISTMAS_TAIL, text)
    if found:
        when, days = _christmas_day(text)
        name = _christmas_name(text)
        # The date is said in full: "Christmas Day", not "Christmas", which would leave the
        # person to work out which day of it.
        named = name if name == "Christmas Eve" else "Christmas Day"
        # A named year is the date they asked about, so it is said rather than the count of
        # the wait: "when is christmas 2027" wants the day, not "56 days away".
        if found.group("year"):
            return (f"{named} is on {when.day} December {found.group('year')}.")
        if days < 0:
            return _wait_text(days, named)
        day = "today" if days == 0 else f"on {when.day} December, {days} days away"
        return f"{named} is {day}."
    return None


def _weekday_text(text, guess=None):
    """"Is christmas on a friday this year", "what day of the week is christmas", answered
    from the calendar. A guess in the line is answered yes or no rather than repeated."""
    when, days = _christmas_day(text)
    name = _christmas_name(text)
    weekday = when.strftime("%A")
    date = f"{when.day} December {when.year}"
    if guess:
        if guess.lower() == weekday.lower():
            return f"Yes - {name} is on a {weekday} this year, {date}."
        return (f"No - {name} is on a {weekday} this year, {date}, "
                f"not a {guess.capitalize()}.")
    return f"{name} is on a {weekday} this year, {date}. That is {days} days away."


# Easter Sunday is the first Sunday after the first full moon on or after 21 March, which
# is computable rather than a table: one rule gives every year. These are the days counted
# from Easter that people ask about by name, and the words that name each one.
_EASTER_OFFSETS = (
    (r"easter(?:\s+(?:sunday|day))?", 0, "Easter Sunday"),
    (r"good friday", -2, "Good Friday"),
    (r"easter monday", 1, "Easter Monday"),
    (r"palm sunday", -7, "Palm Sunday"),
    (r"maundy thursday", -3, "Maundy Thursday"),
    (r"(?:ash wednesday|lent)", -46, "Ash Wednesday"),
    (r"(?:shrove tuesday|pancake day)", -47, "Shrove Tuesday"),
    (r"ascension day", 39, "Ascension Day"),
    (r"(?:whit sunday|pentecost)", 49, "Pentecost"),
)


_MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December")


# The ways people ask for a date, then whatever trails the ask without changing it.
# "what day is it the day before christmas" and "what day is it on the 24th" put an "it"
# between the question and the thing asked about, and without it here they were a punt. The
# "it" is optional and only ever read as part of a longer fullmatch, so "what day is it" is
# still the clock's own line.
_ASK_DATE = (r"(?:when(?:'s| is| will it be| does)|what (?:date|day|days) (?:is|are)(?: it)?|"
             r"which (?:date|day) (?:is|are)|whats the date of)")


_DATE_TAIL = (r"(?:(?:\s+(?:in\s+)?20\d{2})|\s+(?:this year|next year|this easter|"
              r"next easter|now|again|yet|exactly|left|to go))*")


def _easter_sunday(year):
    """Easter Sunday in the Gregorian calendar: the computus, in ten lines, no table."""
    import datetime
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return datetime.date(year, month, day + 1)


def _feast_year(text):
    """The year the line means, and whether it named one itself."""
    import datetime
    today = datetime.date.today()
    four_digits = re.search(r"\b(20\d{2})\b", text)
    if four_digits and 2000 <= int(four_digits.group(1)) <= 2100:
        return int(four_digits.group(1)), True, today
    if re.search(r"\bnext (?:year|easter)\b", text):
        return today.year + 1, False, today
    return today.year, False, today


# A countdown to a date the bot cannot know: "how many sleeps until my birthday" is a count of
# nights, not an adult's sleep needs, and not something it can answer without the date. The
# answer a friend gives is "tell me the day and I'll count it", so that is what this says. The
# words after "until" have to be a named event ("my birthday", "our holiday", "the wedding") or
# a date, and the unit has to be a count of time, so no sleep question can land here.
_COUNT_ASK = (
    r"(?:how many|how much longer|how long)?\s*"
    r"(?:more\s+|still\s+)?"
    r"(?P<unit>days?|weeks?|months?|sleeps?|nights?)\s+"
    r"(?:is it\s+|are there\s+|are left\s+|left\s+|to go\s+|have i got left\s+)?"
    r"(?:until|'?till?|to|before)\s+"
    r"(?P<rest>.+)"
    # "how long until my due date", "countdown to my holiday": no unit word at all, so the
    # answer comes in days.
    r"|(?:how long(?:\s+(?:is it|have i got))?|countdown)\s+(?:to go\s+)?"
    r"(?:until|'?till?|to|before)\s+(?P<rest2>.+)"
)


_COUNTED_EVENT = (
    r"(?:(?:my|his|her|their|our|the)\s+)?(?:little\s+|big\s+)?"
    r"(?:birthday|holiday|holidays|wedding|anniversary|exam|exams|test|results day|due date|"
    r"operation|op|flight|trip|cruise|driving test|interview|retirement|graduation|move|"
    r"house move|scan|appointment|payday|pay day)"
    # A destination or a date may follow the event: "my holiday to spain" is the same wait as
    # "my holiday", and the count still needs the day, so the tail is allowed but not read here.
    r"(?:\s+(?:on|in|to|for)\s+(?P<when>.+))?"
)


_MONTHS_SAID = ("january", "february", "march", "april", "may", "june", "july", "august",
                "september", "october", "november", "december")


# The short spellings people type. "how many days until dec 5" and "how many weeks till sept 1"
# were a punt and a shrug while "5 december" was counted, which is the same question written the
# other way round. Only the spellings that cannot be an ordinary word are here; "may" is already
# a month name and is never read as the verb by a line with a date in it.
_MONTH_SHORT = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
                "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}


_MONTH_WORD = ("(?:january|february|march|april|may|june|july|august|september|october|november|"
               "december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec)")


_DAY_MONTH = (
    r"\b(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<month>" + _MONTH_WORD + r")\b"
    # The day after the month takes its ordinal too: "december 5th" was not read at all, because
    # the boundary after the figure has to sit after the "th".
    r"|\b(?P<month2>" + _MONTH_WORD + r")\s+(?P<day2>\d{1,2})(?:st|nd|rd|th)?\b"
)


def _month_number(word):
    """The month a name or short spelling stands for, or None."""
    word = (word or "").strip().lower()
    if word in _MONTHS_SAID:
        return _MONTHS_SAID.index(word) + 1
    return _MONTH_SHORT.get(word)


# "How many sleeps until the 25th": the month is the one coming, because the 25th of a month
# that has gone is not a countdown. The ordinal has to end the line, so "the 2nd interview" and
# "the 1st class ticket" are not read as dates.
_DAY_ONLY = re.compile(
    r"(?:^|\bthe\s+|\bof\s+)(?P<day>\d{1,2})(?:st|nd|rd|th)\b"
    r"(?:\s+(?:now|please|thanks|again|yet))*\s*$",
    re.I,
)


def _day_in_a_month(day, month_number, today):
    """That day in that month, the next time it comes round.

    Trying the years in turn is what makes "how many days until 29 february" countable: the date
    is not on the calendar this year or next, and answering "I do not know" for a date that
    exists every fourth year is the wrong kind of honesty.
    """
    import datetime
    for year in range(today.year, today.year + 9):
        try:
            when = datetime.date(year, month_number, day)
        except ValueError:
            continue
        if when >= today:
            return when
    return None


def _date_the_line_gave(text):
    """The day and month the line names, as the next date it falls, and how to say it."""
    import datetime
    today = datetime.date.today()
    found = re.search(_DAY_MONTH, text, re.I)
    if found:
        day = found.group("day") or found.group("day2")
        month = (found.group("month") or found.group("month2") or "").lower()
        try:
            when = _day_in_a_month(int(day), _month_number(month), today)
        except (ValueError, TypeError):
            return None, None
        return (when, f"{when.day} {when.strftime('%B')}") if when else (None, None)
    bare_day = _DAY_ONLY.search(text)
    if not bare_day:
        return None, None
    day = int(bare_day.group("day"))
    for step in range(13):
        month_index = today.month - 1 + step
        try:
            when = datetime.date(today.year + month_index // 12, month_index % 12 + 1, day)
        except ValueError:
            continue
        if when >= today:
            return when, f"{when.day} {when.strftime('%B')}"
    return None, None


# --- a day counted from today, not from a date on the calendar -----------------
# "how many days until tomorrow", "what date is it in two weeks": the line names no date and no
# event, so nothing above can count it, and the arithmetic is the whole answer. A relative day is
# a small closed set in English, so each phrase is turned into the date it means and then the
# same count is done on it; that keeps one countdown voice for every shape of the question.
_SMALL_NUMBER = {"a": 1, "an": 1, "one": 1, "couple of": 2, "a couple of": 2,
                 "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                 "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


_HOW_FAR = re.compile(
    r"(?:in\s+)?(?P<num>\d{1,3}|a couple of|couple of|a|an|one|two|three|four|five|six|"
    r"seven|eight|nine|ten|eleven|twelve)\s+"
    r"(?P<unit>days?|weeks?|months?|years?)"
    r"(?:\s*'?s?\s*time|\s+from\s+(?:now|today|tomorrow))?",
    re.I,
)


def _month_on(day, months_ahead):
    """The same day that many months on, in the month that has it."""
    import calendar
    import datetime
    month_index = day.month - 1 + months_ahead
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return datetime.date(year, month, min(day.day, last))


def _first_of_the_month(day, months_ahead):
    """The 1st of the month that many months on: the turn of the month, not a day inside it."""
    import datetime
    month_index = day.month - 1 + months_ahead
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return datetime.date(year, month, 1)


def _relative_day(text):
    """The date a phrase counted from today points at, and how to say it.

    The phrase is turned into a date rather than into a rule about adding days, so every way of
    saying the same day lands on one date: "tomorrow", "in a day" and "a day from now" are the
    same count, and a month is a month on the calendar rather than thirty days.
    """
    import datetime
    today = datetime.date.today()
    said = " ".join(str(text or "").lower().split()).strip(" .!?")
    if re.fullmatch(r"(?:today|tonight|this day)", said):
        return today, "today"
    if re.fullmatch(r"tomorrow", said):
        return today + datetime.timedelta(days=1), "tomorrow"
    if re.fullmatch(r"(?:the )?day after tomorrow", said):
        return today + datetime.timedelta(days=2), "the day after tomorrow"
    # Saturday is the weekend people mean: on a Saturday the weekend has started, so the count
    # is nothing rather than a week.
    if re.fullmatch(r"(?:the|this) weekend", said):
        return today + datetime.timedelta(days=(5 - today.weekday()) % 7), "the weekend"
    if re.fullmatch(r"next weekend", said):
        return today + datetime.timedelta(days=(5 - today.weekday()) % 7 + 7), "next weekend"
    if re.fullmatch(r"next week", said):
        return today + datetime.timedelta(days=(7 - today.weekday()) % 7 or 7), "next week"
    # "next month" and "next year" are when the calendar turns, not this day next month: the turn
    # of the month is the 1st, the same way "next week" is the Monday. A countdown is where the
    # difference shows - "365 days until next year" on the 6th of November is a year nobody meant.
    if re.fullmatch(r"next month", said):
        return _first_of_the_month(today, 1), "next month"
    if re.fullmatch(r"next year", said):
        return datetime.date(today.year + 1, 1, 1), "next year"
    found = _HOW_FAR.fullmatch(said)
    if not found:
        return None, None
    raw = found.group("num").lower()
    count = int(raw) if raw.isdigit() else _SMALL_NUMBER.get(raw)
    if not count or count > 999:
        return None, None
    unit = found.group("unit").lower()
    if unit.startswith("day"):
        return today + datetime.timedelta(days=count), None
    if unit.startswith("week"):
        return today + datetime.timedelta(days=7 * count), None
    if unit.startswith("month"):
        return _month_on(today, count), None
    return _month_on(today, 12 * count), None


def _relative_count_text(unit, days):
    """The count in the unit the line asked for, in the singular when it is one."""
    unit = (unit or "days").lower()
    counted = "sleeps" if unit.startswith(("sleep", "night")) else unit
    if days == 1:
        return counted[:-1] if counted.endswith("s") else counted
    return counted


def _days_until_a_relative_day(clean):
    """A countdown to a day counted from today: "how many sleeps until the weekend"."""
    import datetime
    text = _plain(clean)
    found = re.fullmatch(_COUNT_ASK, text, re.I)
    if not found:
        return None
    rest = (found.groupdict().get("rest") or found.groupdict().get("rest2") or "").strip()
    if not rest:
        return None
    when, said = _relative_day(rest)
    if when is None:
        return None
    days = (when - datetime.date.today()).days
    unit = (found.groupdict().get("unit") or "days").lower()
    one = _relative_count_text(unit, days)
    if days <= 0:
        return f"That is today - no {_relative_count_text(unit, 2)} left to wait."
    if days == 1:
        if said == "tomorrow":
            return f"Tomorrow, so one {one}."
        return f"One {one} until {said}."
    return f"{_count_in(unit, days, when)} until {said or _short_date(when)}."


def _date_counted_from_today(clean):
    """"what date is it in two weeks": the calendar arithmetic, said as a date."""
    import datetime
    text = _plain(clean)
    rest = None
    # "the date" needs no connector before a day word: "whats the date tomorrow" and "what's the
    # day tomorrow" are the same question as "what date is it tomorrow", and the "in|of" that made
    # the pattern work for "the date in two weeks" made them reach nothing at all.
    for pattern in (r"what(?:'s|s| is)? the (?:date|day) (?:(?:in|of) )?(?P<rest>.+)",
                    r"what date (?:is it|is|will it be) (?P<rest>.+)",
                    r"what day (?:is it|will it be) (?P<rest>.+)",
                    r"what date is it on (?P<rest>.+)"):
        found = re.fullmatch(pattern, text)
        if found:
            rest = found.group("rest").strip()
            break
    if not rest:
        return None
    when, _ = _relative_day(rest)
    if when is None:
        return None
    if when == datetime.date.today():
        return f"That is today, {_short_date(when)}."
    return f"That is {_day_text(when)}."


def _days_until_a_named_day(clean):
    """A countdown to an event whose date the bot cannot know: ask for the day, then count.

    "How many sleeps until my birthday" used to reach the sleep-needs entry and come back with
    seven to nine hours a night (#1519), which is a different question about a different thing.
    "How many sleeps till christmas" works because Christmas is a known date; a birthday, a
    holiday or a wedding is not, so the honest answer is to ask for it and say how the count
    works. A date said in the line is counted rather than asked for again.
    """
    import datetime
    text = _plain(clean)
    if re.search(_CHRISTMAS_DAY + r"\b", text) or re.search(r"\beaster\b", text):
        return None
    found = re.fullmatch(_COUNT_ASK, text, re.I)
    if not found:
        return None
    rest = (found.groupdict().get("rest") or found.groupdict().get("rest2") or "").strip()
    # "how many days until i go on holiday": the going is part of the event, not a
    # determiner, so the same words answer as "how many days until my holiday".
    rest = re.sub(r"^(?:i|we)\s+(?:go|am going|are going|'m going|'re going|leave)\s+(?:on\s+)?",
                 "", rest, flags=re.I)
    if not rest:
        return None
    unit = (found.groupdict().get("unit") or "days").lower()
    counted = "sleeps" if unit.startswith("sleep") or unit.startswith("night") else unit
    event = re.fullmatch(_COUNTED_EVENT + r"(?:\s+(?:please|thanks|now|yet))?", rest, re.I)
    named = bool(event)
    if not named and not _date_the_line_gave(rest)[0]:
        return None
    when, said = _date_the_line_gave(rest)
    if when is not None:
        days = (when - datetime.date.today()).days
        if days == 0:
            return f"That is today - no {counted} left to wait."
        return f"{_count_in(unit, days, when)} until {said}."
    if re.search(r"\bpay ?day\b", rest):
        # A payday is a date only the person's own payslip knows, and the child-waiting tail
        # below is a strange thing to say about it.
        return ("I can't see your payday from here, so tell me the date it lands on and I'll "
                f"count the {counted} to it.")
    asked = ("I can't see a calendar from here, so tell me the date - the day and the month - and "
             f"I'll count it: how many {counted} from today.")
    if counted.startswith("month"):
        # A paper chain counts nights, so it is no help to somebody counting in months, and a
        # birthday, a payday or a holiday already has a date the person can give.
        return asked
    return (asked + " If it is a child waiting, a paper "
            "chain or a row of crosses on the calendar is the same count, and they can do one a "
            "night, which does more for the waiting than the number does.")


# --- the rest of a period, and how long ago a day was -----------------------
# "how many days left in the month", "how many weeks left in the year": the line names no date
# and no event, only the stretch of calendar it is standing in, so nothing above counts it and
# the answer people want is a number. The cue word ("left", "to go", "the end of") is what makes
# it a count rather than "how many days in a year", which is a fact about the calendar.
_REST_OF_A_PERIOD_WORDS = frozenset("""
how many much long day days week weeks are is left to go remaining remain in of until till the
this end month year tax now already exactly please today january february march april may june july
august september october november december jan feb mar apr jun jul aug sep sept oct nov dec
""".split())


_REST_OF_A_PERIOD = re.compile(
    r"\b(?:month|year|tax year|january|february|march|april|may|june|july|august|september|october|"
    r"november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b", re.I)


def _days_left_in_the_month_or_the_year(clean):
    """How much of the month or the year is still to come, counted from today.

    The count starts tomorrow, because that is what "left" means to someone looking at a
    calendar, and the answer says both numbers: "21 days left in November after today, 22
    counting today". Saying only the first would be short by one for anyone counting today in.
    A month that has not begun yet is counted to its last day instead, because "how many days
    left in December" said in November is a wait, not the length of a month that is not here.
    """
    import datetime
    text = _plain(clean)
    if not _REST_OF_A_PERIOD.search(text) or "how" not in text.split():
        return None
    words = re.findall(r"[a-z0-9]+", text)
    if any(word not in _REST_OF_A_PERIOD_WORDS for word in words):
        return None
    if not ({"left", "go", "remaining", "remain", "end"} & set(words)):
        return None
    today = datetime.date.today()
    unit = "weeks" if "weeks" in words or "week" in words else "days"
    month = None
    for number, name in enumerate(_MONTH_NAMES, start=1):
        if name.lower() in words or name[:3].lower() in words:
            month = number
    waiting = False
    extra = ""
    if "tax" in words:
        # The tax year runs from 6 April to 5 April, so it is a period of its own that the
        # calendar already knows: "how many days left in the tax year" is a count, not the
        # P60 card it used to get.
        end = datetime.date(today.year, 4, 5)
        if end < today:
            end = datetime.date(today.year + 1, 4, 5)
        said = "the tax year"
        extra = f" It ends on {_said_with_a_weekday(end)}."
    elif "year" in words:
        end = datetime.date(today.year, 12, 31)
        said = f"{today.year}"
    elif month is not None and month != today.month:
        year = today.year + (1 if month < today.month else 0)
        end = datetime.date(year + (month // 12), month % 12 + 1, 1) - datetime.timedelta(days=1)
        said = (f"{_MONTH_NAMES[end.month - 1]}: the last day of it is "
                f"{_said_with_a_weekday(end)}")
        waiting = True
    else:
        end = datetime.date(today.year + (today.month // 12), today.month % 12 + 1, 1)
        end -= datetime.timedelta(days=1)
        said = f"{_MONTH_NAMES[end.month - 1]}"
    days = (end - today).days
    if days <= 0:
        return (f"That is today - nothing left of {said} after today, and {_count_in(unit, 1)} "
                f"in all if you count it.")
    if waiting:
        return (f"{_count_in(unit, days)} until the end of {said}. "
                f"That is {_count_in(unit, days + 1)} counting today.")
    return (f"{_count_in(unit, days)} left in {said} after today, "
            f"{_count_in(unit, days + 1)} counting today." + extra)


# "how many days since 3 march", "how long ago was the 3rd": the count runs backwards, to the
# last time the day came round, which is the opposite of every count above.
_SINCE_ASK = re.compile(
    r"(?:how many\s+(?P<unit>days?|weeks?)\s+(?:has it been\s+|have passed\s+)?"
    r"(?:since|ago\s+was)"
    r"|how long\s+(?:has it been\s+)?(?:since|ago\s+was))", re.I)


_SINCE_FILLER = re.compile(r"\b(?:was|is|it|the|on|of|now|already|today|date|day)\b", re.I)


_A_YEAR_IN_THE_LINE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")


def _year_the_line_gave(text):
    """"How long ago was 3 March 2020" names a year, and the year is half the question.

    Without it the count runs back to the last time the day came round, which for a date years
    back is a confident number about the wrong year - worse than saying nothing. So a year in
    the line is read, used, and put in the answer.
    """
    found = _A_YEAR_IN_THE_LINE.search(text or "")
    return int(found.group(1)) if found else None


def _how_long_ago(clean):
    """The days between a date the line gives and today, counting backwards.

    "How long ago was 3 March" is the same arithmetic as a countdown with the sign turned
    round, and the answer says which weekday it was, because that is how people place a date
    they half remember.
    """
    import datetime
    text = _plain(clean)
    found = _SINCE_ASK.search(text)
    if not found:
        return None
    rest = (text[:found.start()] + " " + text[found.end():]).strip()
    rest = " ".join(_SINCE_FILLER.sub(" ", rest).split())
    if not rest:
        return None
    year = _year_the_line_gave(rest)
    when, said = _date_the_line_gave(rest)
    if when is None:
        when, said = _a_known_day_that_has_gone(rest, year)
    elif year is not None:
        try:
            when = when.replace(year=year)
        except ValueError:  # 29 February in a year that has none
            return None
        said = f"{said} {year}"
    if when is None:
        return None
    today = datetime.date.today()
    if when > today:
        if year is not None:  # a year that has not happened yet is not a time ago
            return None
        try:
            when = when.replace(year=when.year - 1)
        except ValueError:
            return None
    days = (today - when).days
    unit = (found.groupdict().get("unit") or "days").lower()
    if days == 0:
        return f"That was today - {said} is today, so no days ago at all."
    count = _count_in(unit, days)
    if days >= 1000 and unit.startswith("day"):
        count = f"{days:,} days"
    return f"{count} since {said} - that was a {_WEEKDAYS[when.weekday()]}."


# --- working days, and weekends, between today and a day ---------------------
# "how many working days until christmas" is the count a person does when they are planing a
# job, a move or a handover: the days that are not weekends and not bank holidays. "How many
# weekends until christmas" is the same idea the other way round, and both need a date, which
# the line either gives or the bot already knows.
_WORKING_ASK = re.compile(
    r"(?P<count>how many\s+(?:(?:working|work|business)\s+days?|weekends?))\s+"
    r"(?:are there\s+|are left\s+|is it\s+|do i have\s+|left\s+|to go\s+)?"
    r"(?:until|till|to|before)\s+(?P<rest>.+)", re.I)


_WORKING_LEFT = re.compile(
    r"(?P<count>how many\s+(?:(?:working|work|business)\s+days?|weekends?))\s+"
    r"(?:are\s+|is\s+|have i got\s+)?(?:left|to go)\s+(?:in\s+|of\s+)?"
    r"(?:the\s+|this\s+)?(?P<period>year|month)", re.I)


def _a_known_day_the_line_names_next(text):
    """The next time the day the line names comes round, as a date and how to say it."""
    import datetime
    today = datetime.date.today()
    if re.search(_CHRISTMAS_DAY + r"\b", text):
        eve = bool(re.search(r"\beve\b", text))
        when = datetime.date(today.year, 12, 24 if eve else 25)
        if when < today:
            when = datetime.date(today.year + 1, 12, 24 if eve else 25)
        return when, ("Christmas Eve" if eve else "Christmas")
    if re.search(r"\bnew year(?:'s|s')? (?:day|eve)\b|\bnew year\b", text):
        when = datetime.date(today.year, 1, 1)
        if when < today:
            when = datetime.date(today.year + 1, 1, 1)
        return when, "New Year's Day"
    if re.search(r"\beaster\b", text):
        when = _easter_sunday(today.year)
        if when < today:
            when = _easter_sunday(today.year + 1)
        return when, "Easter Sunday"
    return _date_the_line_gave(text)


# "how many working hours in a week" is the job's week, not the calendar's: 37.5 or 40 hours.
# The plain unit rows answer "how many hours in a week" with 168 and "how many days in a week"
# with 7, and they are right to; the word "working" is what makes it a question about work.
# `_plain` drops that word as filler, so this reads the line before the filler goes.
_WORKING_SHAPE = re.compile(
    r"(?:how many|what is|whats|what's|what are) (?:the )?(?P<which>working|work) "
    r"(?P<unit>hours?|days?)(?: in| per| to| into| a| of)?(?: a| the| one)? (?P<week>week|day|month)"
    r"(?: is (?:full|normal) time)?(?: of work)?", re.I)


def _a_working_week(clean):
    said = " ".join(str(clean or "").lower().strip().strip("?.!").split())
    found = _WORKING_SHAPE.fullmatch(said)
    if not found:
        return None
    unit, span = found.group("unit"), found.group("week")
    if unit.startswith("hour") and span == "week":
        return ("A full-time week is usually 37.5 to 40 hours - 7.5 or 8 hours a day over five "
                "days. The law caps the average at 48 hours a week over 17 weeks unless the "
                "person signs to opt out, and part-time hours are usually written as a share of "
                "that full-time week.")
    if unit.startswith("hour") and span == "day":
        return ("A full-time day is usually 7.5 or 8 hours, and a break of 20 minutes after six "
                "hours is the legal minimum in the UK. Contracted hours are the ones that count "
                "for pay, so check the contract rather than the rota.")
    if unit.startswith("day") and span == "week":
        return ("Five, for a full-time job - Monday to Friday - which is why a week off is five "
                "days of leave, not seven. Shift work and four-day weeks are the usual "
                "exceptions, and the contract says which one you are on.")
    return None


def _a_known_day_that_has_gone(text, year=None):
    """The last time a day the bot knows came round, for a count backwards.

    "How long ago was Christmas" names a fixed date, so it can be counted the same way as a date
    the line gives. Easter moves, so it is worked out from its own rule. A year in the line
    ("Christmas 2019") is that year's Christmas, not the last one.
    """
    import datetime
    today = datetime.date.today()
    tail = f" {year}" if year else ""
    named = re.search(_CHRISTMAS_DAY + r"\b", text)
    if named:
        when = datetime.date(year or today.year, 12, 25)
        if year is None and when > today:
            when = datetime.date(today.year - 1, 12, 25)
        return when, f"Christmas Day{tail}"
    if re.search(r"\bnew year(?:'s|s')? (?:day|eve)\b|\bnew year\b", text):
        when = datetime.date(year or today.year, 1, 1)
        if year is None and when > today:
            when = datetime.date(today.year - 1, 1, 1)
        return when, f"New Year's Day{tail}"
    if re.search(r"\beaster (?:sunday|day)\b|\beaster\b", text):
        when = _easter_sunday(year or today.year)
        if year is None and when > today:
            when = _easter_sunday(today.year - 1)
        return when, f"Easter Sunday{tail}"
    return None, None


def _nth_weekday(year, month, weekday, nth):
    """The nth weekday of a month: Father's Day is the third Sunday in June."""
    import datetime
    day = datetime.date(year, month, 1)
    day += datetime.timedelta(days=(weekday - day.weekday()) % 7)
    return day + datetime.timedelta(days=7 * (nth - 1))


# The named days whose date the calendar knows, in the words people use for them, with the rule
# that gives the date. Before this, "when is mothers day" was answered with a present suggestion
# (the gift entry owns the words and nothing else answered the ask) and "when is valentines day"
# with "I don't know enough to answer that honestly" - both are dates a friend knows.
#   ("fixed", month, day)             never moves
#   ("easter", offset)                hangs off Easter Sunday
#   ("nth", month, weekday, n)        the nth weekday of a month
_NAMED_DAYS = (
    (("valentines day", "valentine's day", "valentines"), ("fixed", 2, 14), "Valentine's Day", ""),
    (("halloween", "hallowe'en"), ("fixed", 10, 31), "Halloween", ""),
    (("bonfire night", "guy fawkes night", "guy fawkes"), ("fixed", 11, 5), "Bonfire Night", ""),
    # "the day before christmas" and "the day after christmas" are the same two days said the
    # long way, and they were a punt and a Christmas film respectively.
    (("christmas eve", "xmas eve", "day before christmas"), ("fixed", 12, 24), "Christmas Eve",
     ""),
    (("boxing day", "day after christmas"), ("fixed", 12, 26), "Boxing Day", ""),
    (("new years eve", "new year's eve", "hogmanay", "day before new year",
      "day before new years day", "day before new year's day"), ("fixed", 12, 31),
     "New Year's Eve", ""),
    (("new years day", "new year's day"), ("fixed", 1, 1), "New Year's Day", ""),
    # Mothering Sunday is the fourth Sunday of Lent, which is three weeks before Easter Sunday;
    # "mothers day" is what most people type for it here.
    (("mothering sunday", "mothers day", "mother's day"), ("easter", -21), "Mothering Sunday",
     " That is the UK date; the American Mother's Day is a Sunday in May."),
    (("fathers day", "father's day"), ("nth", 6, 6, 3), "Father's Day", ""),
)


# --- a count to a month, a season, or the turn of the year -------------------
#
# "how many days until december", "how long till the summer", "how long until new year": the
# wait is the whole question and the calendar already knows the day it ends, so the answer is
# arithmetic rather than a fact to look up. None of these lines holds a date, which is why the
# counts above leave them alone: a bare month is not a day, and a season is a stretch of the year
# rather than one date. Before this they got "That's beyond what I know well", or - for new year -
# a plan to make a resolution, which answers a different question.
#
# Narrow on purpose: the whole line has to be the countdown, and the thing waited for has to be
# one of these words with nothing else said about it, so "how long until june exams", "how many
# days until december payday" and "how long until the summer holidays" are left to whatever else
# answers them: a school holiday, a payday or an exam season moves by council, employer and
# school, and nothing here knows those dates.
_SEASONS = (
    # the words people use, the first day of the season, its last month, and that month's name
    (("spring",), (3, 1), 5),
    (("summer",), (6, 1), 8),
    (("autumn", "fall"), (9, 1), 11),
    (("winter",), (12, 1), 2),
)


# A month named on its own, or the turn of the year, with the only words that can sit around it
# without turning the line into a different question.
_COUNTED_SUBJECT_TAIL = r"(?:\s+(?:now|again|yet|please|roughly|this year|next year|20\d{2}))*"


_THE_TURN_OF_THE_YEAR = ("new year", "new years", "new year's", "the new year",
                         "new year's day", "new years day", "new year's eve", "new years eve",
                         "hogmanay")


# --- the bank holidays ------------------------------------------------------
#
# Eight days a year in England and Wales, and all eight are computable: two hang off Easter, three
# are the first or last Monday of a month, and three are fixed dates that move to the next weekday
# when they land on a weekend. Before this, "when is the next bank holiday" was answered with
# "Nothing so far - you haven't mentioned anything coming up", which is the wrong kind of reply to
# a question about the calendar, and the countdown "how many days until the next bank holiday" had
# no answer at all. A person asking either of those wants one date, and then the one after it.
_BANK_HOLIDAY_TAIL = (r"(?:\s+(?:in\s+)?(?:england|wales|scotland|scottish|"
                      r"northern ireland|england and wales|the uk|the united kingdom|britain|edinburgh|"
                      r"glasgow|belfast|here|then|now|please|left|to go|coming up|off|in a row|weekend|"
                      r"in\s+20\d\d|this year|next year))*")


_BANK_HOLIDAY_NEXT = re.compile(
    rf"(?:when|what|whats|what's|which)(?:'s| is|s| are| will it be)?\s+(?:the\s+)?"
    rf"(?:next|coming|nearest|first)\s+(?:bank|public)\s+holiday(?:s)?"
    rf"(?:\s+(?:after this one|after that|after|next))?{_BANK_HOLIDAY_TAIL}")


_BANK_HOLIDAY_COUNT = re.compile(
    rf"(?:how many|how long)\s+(?:days?|weeks?|sleeps?)\s+(?:is it |are there |left |to go )?"
    rf"(?:until|till|to|before)\s+(?:the\s+)?(?:next\s+)?(?:bank|public)\s+holiday"
    rf"{_BANK_HOLIDAY_TAIL}")


_BANK_HOLIDAY_LIST = re.compile(
    rf"(?:when|what)(?:'s| are| is)?\s+(?:the\s+|all\s+the\s+)?(?:bank|public)\s+holidays?"
    rf"(?:\s+(?:this year|next year|in\s+20\d\d|left|left this year|this coming year|"
    rf"which are left|are left|coming up))?{_BANK_HOLIDAY_TAIL}")


# "What day is the 24th of December" is a calendar question with the answer in it, and every
# form of it was a punt: "what day is the 24th", "what day is it on the 24th", "what day does the
# 24th fall on", "what day is december 24th". The weekday a date falls on is worked out from the
# calendar, so it is never a guess. The month is optional; without one the answer gives this
# month's day and next month's, so a person's bare "the 24th" is covered either way.
_SAYS_WEEKDAY = re.compile(
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tues|tue|weds|wed|"
    r"thurs|thur|thu|fri|sat|sun)\b", re.I)


_MONTHS_OR = "|".join(sorted(list(_MONTHS_SAID) + list(_MONTH_SHORT), key=len, reverse=True))


def _ordinal(number):
    """24 -> "24th", 1 -> "1st", 22 -> "22nd"."""
    if 11 <= number % 100 <= 13:
        return f"{number}th"
    return f"{number}{('th', 'st', 'nd', 'rd')[min(number % 10, 4) % 4] if number % 10 < 4 else 'th'}"


def _the_wider_day(day, taken):
    """A fixed bank holiday that lands at the weekend is taken on the next free weekday."""
    import datetime
    while day.weekday() > 4 or day in taken:
        day += datetime.timedelta(days=1)
    return day


def _last_weekday(year, month, weekday):
    """The last weekday of a month: the summer bank holiday is the last Monday in August."""
    import datetime
    if month == 12:
        last = datetime.date(year, 12, 31)
    else:
        last = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    return last - datetime.timedelta(days=(last.weekday() - weekday) % 7)


def _bank_holidays(year, where="england"):
    """Every bank holiday in one year, as (name, date), in order.

    The three calendars are not the same list: Scotland has 2 January, St Andrew's Day and the
    first Monday of August rather than the last, and Northern Ireland has St Patrick's Day and the
    Battle of the Boyne. All of them are computable from the same pieces: the fixed dates (moved to
    the next free weekday when they land at a weekend), the two that hang off Easter, and the
    Mondays of a named week of a month.
    """
    import datetime
    easter = _easter_sunday(year)
    if where == "scotland":
        fixed_days = (("New Year's Day", 1, 1), ("2 January", 1, 2),
                      ("St Andrew's Day", 11, 30), ("Christmas Day", 12, 25),
                      ("Boxing Day", 12, 26))
    elif where == "northern ireland":
        fixed_days = (("New Year's Day", 1, 1), ("St Patrick's Day", 3, 17),
                      ("the Battle of the Boyne", 7, 12), ("Christmas Day", 12, 25),
                      ("Boxing Day", 12, 26))
    else:
        fixed_days = (("New Year's Day", 1, 1), ("Christmas Day", 12, 25),
                      ("Boxing Day", 12, 26))
    taken = set()
    rows = []
    for name, month, day in fixed_days:
        moved = _the_wider_day(datetime.date(year, month, day), taken)
        taken.add(moved)
        rows.append((name, moved))
    rows.append(("Good Friday", easter - datetime.timedelta(days=2)))
    if where != "scotland":
        rows.append(("Easter Monday", easter + datetime.timedelta(days=1)))
    rows.append(("the early May bank holiday", _nth_weekday(year, 5, 0, 1)))
    rows.append(("the spring bank holiday", _last_weekday(year, 5, 0)))
    if where == "scotland":
        rows.append(("the summer bank holiday", _nth_weekday(year, 8, 0, 1)))
    else:
        rows.append(("the summer bank holiday", _last_weekday(year, 8, 0)))
    return sorted(rows, key=lambda row: row[1])


# The three lists have their own names in the line, and the answer says which list it is reading.
_BANK_WHERE = (
    (re.compile(r"\bscotland\b|\bscottish\b|\bedinburgh\b|\bglasgow\b"), "scotland",
     "in Scotland"),
    (re.compile(r"\bnorthern ireland\b|\bbelfast\b|\bderry\b"), "northern ireland",
     "in Northern Ireland"),
)


def _bank_where(text):
    for pattern, where, said in _BANK_WHERE:
        if pattern.search(text):
            return where, said
    return "england", "in England and Wales"


def _said_with_a_weekday(when):
    import datetime
    return f"{_WEEKDAYS[when.weekday()]} {when.day} {_MONTH_NAMES[when.month - 1]}"


_POLITE = (r"(?:ok|okay|so|and|but|right|hi|hey|please|sorry|quick one|quick question|"
           r"can you tell me|do you know|tell me|just wondering|i was wondering|"
           r"wondering|out of interest)")


_FILLER = (r"(?:please|for me|thanks|thank you|exactly|roughly|about|approximately|again|"
           r"then|altogether|in total|by the way|actually)")


# The days of the week, and the other ways people name each one.
_WEEKDAY_WORDS = (
    (r"monday|mon", 0, "Monday"),
    (r"tuesday|tues|tue", 1, "Tuesday"),
    (r"wednesday|weds|wed", 2, "Wednesday"),
    (r"thursday|thurs|thur|thu", 3, "Thursday"),
    (r"friday|fri", 4, "Friday"),
    (r"saturday|sat", 5, "Saturday"),
    (r"sunday|sun", 6, "Sunday"),
)


_MONTH_TITLE = ("January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December")


_TODAY_ASK = (
    r"(?:what|whats|what's|which)\s+(?:is\s+)?(?:the\s+)?(?:day|date)"
    r"(?:\s+of\s+the\s+week)?(?:\s+(?:is\s+)?(?:it|today|now))?"
    r"|what\s+day\s+(?:is\s+it|are\s+we)(?:\s+on)?(?:\s+today)?"
    # "today's date" is how most people type it, apostrophe and all, and the curly one too
    r"|(?:what|whats|what's)?\s*(?:is\s+)?today[’']?s\s+(?:date|day)"
    r"|(?:what|whats|what's)\s+is\s+today\b(?:\s+(?:the\s+)?(?:date|day))?"
    r"|the\s+(?:date|day)(?:\s+today)?"
    r"|any\s+idea\s+what\s+day\s+it\s+is"
)


def _day_text(day):
    """A date the way a friend says it: the weekday first, then the day and the month."""
    return f"{day:%A}, {day.day} {_MONTH_TITLE[day.month - 1]}"


def _short_date(day):
    """Just the day and the month, for when the weekday is already in the sentence."""
    return f"{day.day} {_MONTH_TITLE[day.month - 1]}"


def _weekday_of(text, tail):
    """The weekday the line names, its index, and whether it said "next"."""
    for words, index, name in _WEEKDAY_WORDS:
        if re.fullmatch(rf"{tail}(?:(?:the|this|next|coming|on|a week on)\s+)*(?:{words})"
                        rf"(?:\s+(?:today|now|already|yet))*", text):
            return name, index, bool(re.search(r"\bnext\b", text))
    return None, None, False


def _plain(clean):
    """The line without politeness and filler, so a question can be matched whole."""
    text = str(clean or "").strip().strip("?.!")
    text = re.sub(r"\s*[,;]\s*", " ", text)
    text = re.sub(rf"^(?:{_POLITE}\b[\s]+)+", "", text)
    text = re.sub(rf"\b{_FILLER}\b", " ", text)
    return " ".join(text.split())
