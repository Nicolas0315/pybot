"""Part 5 of 6 of a large module, split out of `maths`.

Everything here is re-exported from `maths`, so callers import it from there as before.
"""
import re
from fractions import Fraction

from ..memory.topics import in_a_safety_thread
from ..knowledge import units
from .maths_part_01 import (
    MONTHS, _AMOUNT, _number, _add_fractions, _box_volume, _calc, _circle_measure, _common_factors,
    _equation, _fraction, _fraction_decimal, _fraction_of, _percent, _percentage_change, _prime,
    _quadratic, _root, _roots, _round_to, _share, _simplify, _the_factors,
)
from .maths_part_02 import (
    _a_share_of_a_group, _at_a_pace, _left_on_the_bill, _percent_of_the_figure_in_the_chat,
    _percent_on, _percent_rise, _save_time, _tip, _travel, _wage, _what_percent,
)
from .maths_part_03 import (
    _a_goal_without_a_rate, _area, _average, _deadline_for_a_goal, _each_month_for_a_goal,
    _figure_just_given, _perimeter_of_a_room, _save_by_a_date, _saving, _time_at_a_new_rate,
    _time_at_a_new_total, _time_to_reach, _time_without_a_goal,
)
from .maths_part_04 import (
    _MONTH_NAMES, _WORKING_ASK, _WORKING_LEFT, _a_known_day_the_line_names_next, _bank_holidays,
    _bank_where, _plain, _said_with_a_weekday, _ASK_DATE, _DATE_TAIL, _EASTER_OFFSETS,
    _easter_sunday, _feast_year, _NAMED_DAYS, _nth_weekday, _COUNT_ASK, _MONTHS_SAID, _SEASONS,
    _THE_TURN_OF_THE_YEAR, _count_in, _month_number, _MONTHS_OR, _SAYS_WEEKDAY, _day_in_a_month,
    _ordinal, _BANK_HOLIDAY_COUNT, _BANK_HOLIDAY_LIST, _BANK_HOLIDAY_NEXT, _TODAY_ASK, _day_text,
    _short_date, _weekday_of, _a_working_week, _date_counted_from_today, _days_in_month,
    _days_left_in_the_month_or_the_year, _days_until, _days_until_a_named_day,
    _days_until_a_relative_day, _how_long_ago,
)


def _convert(clean, memory=None):
    """A unit conversion, from the one table of units (bot/knowledge/units.py).

    A plain pair of units may already have a hand-written fact in _unit_fact() with a
    second useful measure in it ("16 ounces in a pound, and 14 pounds in a stone"), and
    that wording is kept. Everything else - a named food's cups and grams, an oven heat,
    every pair nobody wrote a fact for - comes from the table.
    """
    fact = _unit_fact(clean)
    table = units.convert(clean, memory)
    if fact and not units.answers_more_than_a_pair(clean):
        return fact
    return table or fact


def _working_days_or_weekends_until(clean):
    """The weekdays, or the whole weekends, between tomorrow and the day the line names.

    A bank holiday is not a working day, so the England and Wales calendar comes out of it (the
    line can say Scotland or Northern Ireland, and then that list is used). Weekends are counted
    whole: a Saturday whose Sunday is the day itself is not a weekend off before it.
    """
    import datetime
    text = _plain(clean)
    today = datetime.date.today()
    if re.fullmatch(r"how many (?:working|work|business) days? (?:in|per) a year", text):
        return ("About 253 working days in a year: 261 weekdays, less the 8 bank holidays in "
                "England and Wales. Leap years add one.")
    # "how many working hours in a week" is 37.5 or 40, not the 168 hours a week has: the
    # plain hours row answers the calendar question and this one the job.
    if re.fullmatch(r"how many (?:working|work) hours? (?:in|per|to) (?:a|the) week", text):
        return ("A full-time week is usually 37.5 to 40 hours - 7.5 or 8 hours a day, five days. "
                "The law caps the average at 48 hours a week over 17 weeks unless the person "
                "signs to opt out, and part-time hours are usually written as a share of the "
                "full-time week.")
    if re.fullmatch(r"how many weekends (?:in|per) a year", text):
        return ("104 weekend days in a year - 52 Saturdays and 52 Sundays - plus a day or two "
                "in most years, because 365 is not a whole number of weeks.")
    found = _WORKING_ASK.fullmatch(text) or _WORKING_LEFT.fullmatch(text)
    if not found:
        return None
    weekends = "weekend" in found.group("count").lower()
    rest = (found.groupdict().get("rest") or "").strip()
    period = found.groupdict().get("period") or ""
    if rest:
        end, said = _a_known_day_the_line_names_next(rest)
        if end is None:
            # "until the end of the year" is a stretch of calendar, not a day; anything else
            # ("until my holiday", "until payday") is a date only the person has, so it passes.
            if not re.search(r"\b(?:the\s+|this\s+)?(year|month)\b", rest, re.I):
                return None
            period = "month" if re.search(r"\bmonth\b", rest, re.I) else "year"
    if not rest or end is None and period:
        if period == "month":
            end = datetime.date(today.year + (today.month // 12), today.month % 12 + 1, 1)
            end -= datetime.timedelta(days=1)
            said = f"the end of {_MONTH_NAMES[end.month - 1]}"
        else:
            end = datetime.date(today.year, 12, 31)
            said = f"the end of {today.year}"
    days = (end - today).days
    if days <= 0:
        return None
    span = [today + datetime.timedelta(days=step) for step in range(1, days + 1)]
    if weekends:
        count = sum(1 for day in span
                    if day.weekday() == 5 and day + datetime.timedelta(days=1) < end)
        if not count:
            return (f"There is no whole weekend between today and {said} - the next Saturday "
                    f"falls on {_said_with_a_weekday(end)} or later.")
        first = next(day for day in span if day.weekday() == 5)
        return (f"{count} weekend{'' if count == 1 else 's'} until {said}, the first starting "
                f"on {_said_with_a_weekday(first)}.")
    where, _ = _bank_where(rest or text)
    holidays = set()
    for year in {day.year for day in span} | {end.year}:
        holidays |= {day for _name, day in _bank_holidays(year, where)}
    count = sum(1 for day in span if day.weekday() < 5 and day not in holidays)
    return f"{count} working days until {said}, out of {days} days in all."


def _days_until_easter(clean):
    """When Easter and the days around it fall, only when the line asks for the date.

    "When is Easter" is a date question; "what should I cook for Easter" is a cooking one.
    "Is Easter late this year" asks where the date falls rather than for the day itself, so it
    gets the day and the judgement together: Easter can fall anywhere from 22 March to 25 April,
    and "late" means nothing without that range. The whole cleaned line has to be the date
    question, so a mention in passing never counts. Because the day moves, it is worked out from
    the rule each time rather than typed in.
    """
    import datetime
    text = _plain(clean)
    for subject, offset, name in _EASTER_OFFSETS:
        asked = (rf"(?:(?:{_ASK_DATE})\s+(?:the\s+)?(?:{subject})"
                 rf"(?:\s+(?:start|starts|begin|begins))?"
                 rf"|(?:{subject})\s+(?:date|dates|20\d{{2}}))")
        # "how many days until easter" is the same day, asked as a wait.
        waiting = (rf"(?:how many |how long |how much longer )?(?:days?|weeks?|sleeps?) "
                   rf"(?:is it |are there |left |to go |still )?"
                   rf"(?:until|till|to|before) (?:the\s+)?(?:{subject})")
        # "is easter early or late this year", "is easter late this year": the ends of one scale
        # about the date, which the calendar can place inside the range Easter falls in.
        # The year can come before the judgement ("is easter next year late") or after it
        # ("is easter late this year"), so it is allowed in both places.
        judging = (rf"(?:(?:is|was|will)|(?:{_ASK_DATE}))\s*(?:the\s+)?(?:{subject})\s+"
                   rf"(?:going to be\s+)?"
                   rf"(?:(?:next year|this year|next easter|this easter|(?:in )?20\d{{2}})\s+)?"
                   rf"(?:(?:early|late)\s+or\s+(?:early|late)"
                   rf"|early|late|on the early side|on the late side)")
        counting = bool(re.fullmatch(waiting + _DATE_TAIL, text))
        where = bool(re.fullmatch(judging + _DATE_TAIL, text))
        if not counting and not where and not re.fullmatch(asked + _DATE_TAIL, text):
            continue
        year, named, today = _feast_year(text)
        day = _easter_sunday(year) + datetime.timedelta(days=offset)
        if day < today and not named and not re.search(r"\bthis (?:year|easter)\b", text):
            day = _easter_sunday(year + 1) + datetime.timedelta(days=offset)
        said = f"{day.day} {_MONTH_NAMES[day.month - 1]}"
        if where:
            # Easter Sunday can fall on any Sunday from 22 March to 25 April, so each feast has
            # the same range shifted by its own distance from Easter.
            # The range belongs to the year the answer is in: asked in November, Easter has
            # gone, so the answer is next year's date and next year's range.
            first = datetime.date(day.year, 3, 22) + datetime.timedelta(days=offset)
            last = datetime.date(day.year, 4, 25) + datetime.timedelta(days=offset)
            span = f"{first.day} {_MONTH_NAMES[first.month - 1]} to {last.day} {_MONTH_NAMES[last.month - 1]}"
            tense = "was" if day < today else "is"
            if day <= first + datetime.timedelta(days=9):
                sense = "early"
            elif day >= last - datetime.timedelta(days=9):
                sense = "late"
            else:
                return (f"{name} {tense} on {said}, which is about the middle of the range it can "
                        f"fall in ({span}) - neither early nor late.")
            return (f"{name} {tense} on {said}, which is {sense}: it can fall anywhere from {span}.")
        if counting and not named and day >= today:
            days = (day - today).days
            if days == 0:
                return f"{name} is today."
            return f"{days} days until {name}."
        if named:
            return f"{name} is on {said} {day.year}."
        days = (day - today).days
        if days == 0:
            return f"{name} is today."
        if days < 0:
            ago = -days
            return f"{name} this year was on {said}, {ago} day{'' if ago == 1 else 's'} ago."
        return f"{name} is on {said}, {days} days away."
    return None


def _named_day_date(clean):
    """When one of the days above falls: "when is mothers day", "how many days until halloween".

    The whole cleaned line has to be the date question for that day, so "what do i write in a
    mothers day card" and "do bank holidays count towards my holiday" never land here. A year in
    the line is answered with that year's date; without one, a day that has already gone this year
    is answered as next year's, the way the Christmas countdown does it.
    """
    import datetime
    text = _plain(clean)
    for words, rule, name, extra in _NAMED_DAYS:
        subject = "|".join(words)
        asked = rf"(?:{_ASK_DATE})\s+(?:the\s+)?(?:{subject})"
        waiting = (rf"(?:how many |how long )?(?:days?|weeks?|sleeps?) "
                   rf"(?:is it |are there |left |to go )?(?:until|till|to|before) "
                   rf"(?:the\s+)?(?:{subject})")
        counting = bool(re.fullmatch(waiting + _DATE_TAIL, text))
        if not counting and not re.fullmatch(asked + _DATE_TAIL, text):
            continue
        year, named_year, today = _feast_year(text)
        if rule[0] == "fixed":
            when = datetime.date(year, rule[1], rule[2])
        elif rule[0] == "easter":
            when = _easter_sunday(year) + datetime.timedelta(days=rule[1])
        else:
            when = _nth_weekday(year, rule[1], rule[2], rule[3])
        if when < today and not named_year and "this year" not in text:
            if rule[0] == "fixed":
                when = datetime.date(year + 1, rule[1], rule[2])
            elif rule[0] == "easter":
                when = _easter_sunday(year + 1) + datetime.timedelta(days=rule[1])
            else:
                when = _nth_weekday(year + 1, rule[1], rule[2], rule[3])
        said = f"{when.day} {_MONTH_NAMES[when.month - 1]}"
        if named_year:
            return f"{name} is on {said} {when.year}.{extra}"
        days = (when - today).days
        if days == 0:
            return f"{name} is today.{extra}"
        if counting:
            return f"{days} days until {name}."
        if days < 0:
            return f"{name} this year was on {said}, {-days} days ago.{extra}"
        return f"{name} is on {said}, {days} days away.{extra}"
    return None


def _days_until_a_month_or_season(clean):
    """The countdown to a bare month, a season, or New Year, or None.

    The count is to the first day of what was named - December starts on 1 December, summer on
    1 June - and it is said in the unit the line asked for, the same way the Christmas countdown
    replies in weeks when it is asked in weeks. A month or season that has already started this
    year counts to the next turn of it, because "how many days until december" asked on the 4th
    of December is about the next December and not about a date three days behind.
    """
    import datetime
    text = _plain(clean)
    found = re.fullmatch(_COUNT_ASK, text, re.I)
    if not found:
        return None
    rest = (found.groupdict().get("rest") or found.groupdict().get("rest2") or "").strip()
    rest = re.sub(r"^(?:the|my|our)\s+", "", rest, flags=re.I)
    rest = re.sub(r"\s+(?:please|then|now|exactly|roughly|again|yet)$", "", rest, flags=re.I)
    # "how long until september starts" is the same wait as "how long until september".
    rest = re.sub(r"\s+(?:start|starts|begin|begins|come|comes|arrive|arrives|get here)$", "",
                  rest, flags=re.I)
    if not rest or re.search(r"\b(?:holiday|holidays|break|term|half term|exam|exams|payday|pay "
                             r"day|deadline|due|start|starts|begin|begins|end|ends)\b", rest,
                            re.I):
        return None
    today = datetime.date.today()
    unit = (found.groupdict().get("unit") or "days").lower()
    # The turn of the year, asked as a wait: the next 1 January, or the eve of it.
    if rest in _THE_TURN_OF_THE_YEAR:
        eve = "eve" in rest
        when = datetime.date(today.year, 12, 31) if eve else datetime.date(today.year, 1, 1)
        if when < today:
            when = datetime.date(when.year + 1, when.month, when.day)
        days = (when - today).days
        name = "New Year's Eve" if eve else "New Year's Day"
        said = f"{when.day} {_MONTH_NAMES[when.month - 1]}"
        if days == 0:
            return f"{name} is today, {said}."
        # New year is said as the day people mean - the 1st - with the eve named where it is
        # the night people are counting to.
        after = " New Year's Eve is the night before it." if not eve else ""
        return f"{_count_in(unit, days, when)} until {name} - it is {said}.{after}"
    # A season is a stretch of the year, so a season already running is answered as running
    # rather than counted down to: "how long till summer" in July is not "338 days".
    for words, (month, day), last_month in _SEASONS:
        if rest not in words:
            continue
        start = datetime.date(today.year, month, day)
        end = datetime.date(today.year, last_month, MONTHS[_MONTH_NAMES[last_month - 1].lower()])
        if end < start:  # winter runs over the turn of the year
            end = datetime.date(today.year + 1, last_month,
                                MONTHS[_MONTH_NAMES[last_month - 1].lower()])
        name = rest.capitalize()
        if start <= today <= end:
            return (f"{name} is here now - it runs to the end of "
                    f"{_MONTH_NAMES[end.month - 1]}. "
                    f"The next one starts on {start.day} {_MONTH_NAMES[start.month - 1]} "
                    f"next year.")
        if start < today:
            start = datetime.date(today.year + 1, month, day)
        days = (start - today).days
        return (f"{_count_in(unit, days, start)} until {name} - it starts on "
                f"{start.day} {_MONTH_NAMES[start.month - 1]}.")
    # A year on its own is a date too: "how many days until 2027" is the count to 1 January,
    # which the calendar knows, and it was a punt before. A year that has already started is not
    # a countdown at all, so it stands down rather than answering with a negative number.
    year_said = re.fullmatch(r"(?:(?:the\s+)?year\s+)?(20\d{2}|21\d{2})", rest)
    if year_said:
        year = int(year_said.group(1))
        when = datetime.date(year, 1, 1)
        if when <= today:
            return None
        days = (when - today).days
        return (f"{_count_in(unit, days, when)} until {year} - it starts on "
                f"{when.day} {_MONTH_NAMES[when.month - 1]} {year}.")
    # A month on its own: the turn of it, not a day inside it.
    month = _month_number(rest)
    if month is None and rest in [name[:3] for name in _MONTHS_SAID]:
        month = [name[:3] for name in _MONTHS_SAID].index(rest) + 1
    if month is None:
        return None
    when = datetime.date(today.year, month, 1)
    next_year = False
    if when < today:
        when = datetime.date(today.year + 1, month, 1)
        next_year = True
    days = (when - today).days
    label = _MONTH_NAMES[month - 1] + (" next year" if next_year else "")
    return (f"{_count_in(unit, days, when)} until {label} - it starts on "
            f"{when.day} {_MONTH_NAMES[when.month - 1]}"
            f"{' ' + str(when.year) if next_year else ''}.")


def _the_weekday_of_a_date(clean):
    """The weekday a date falls on: "what day is the 24th of december".

    Only the whole line counts, so "i get paid on the 24th" stays a plan. A line that names a
    weekday as well ("is the 24th a friday") is a yes or no question and is left alone, as is a
    line asking how many days it is until a date, which the countdown answers.
    """
    import datetime
    text = _plain(clean)
    today = datetime.date.today()
    said = re.match(r"^(?:what|which)\s+(?:day|date|weekday)\s+(?:of\s+the\s+week\s+)?"
                    r"(?:is|was|will)\s+(?:it\s+)?(?:be\s+)?(?:on\s+)?(?:the\s+)?", text)
    if not said:
        said = re.match(r"^what\s+day\s+does\s+(?:the\s+)?", text)
    if not said:
        return None
    # "what day was the 3rd" asks backwards: the most recent one, not the next.
    backwards = bool(re.search(r"\bwas\b", said.group(0)))
    rest = text[said.end():].strip()
    rest = re.sub(r"\s+(?:fall|falls|land|lands)\s+on$", "", rest)
    year_said = None
    year_found = re.search(r"\s+(?:in\s+)?(20\d{2})$", rest)
    if year_found:
        year_said = int(year_found.group(1))
        rest = rest[:year_found.start()].strip()
    rest = re.sub(r"\s+(?:this|next)\s+year$", "", rest)
    if not rest or _SAYS_WEEKDAY.search(rest):
        return None
    found = (re.fullmatch(rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({_MONTHS_OR})", rest)
             or re.fullmatch(rf"({_MONTHS_OR})\s+(\d{{1,2}})(?:st|nd|rd|th)?", rest))
    if found:
        first, second = found.group(1), found.group(2)
        day, month = (int(first), second) if first.isdigit() else (int(second), first)
        if _month_number(month) is None:
            return None
        if year_said:
            try:
                when = datetime.date(year_said, _month_number(month), day)
            except ValueError:
                return None
            return f"{when.day} {when:%B} {when.year} is a {when:%A}."
        if backwards:
            when = None
            for years_back in range(2):
                try:
                    guess = datetime.date(today.year - years_back, _month_number(month), day)
                except ValueError:
                    continue
                if guess <= today:
                    when = guess
                    break
        else:
            when = _day_in_a_month(day, _month_number(month), today)
        if when is None:
            return None
        days = (when - today).days
        if days < 0:
            ago = -days
            return (f"{when.day} {when:%B} was a {when:%A}, {ago} day"
                    f"{'' if ago == 1 else 's'} ago.")
        if days == 0:
            return f"{when.day} {when:%B} is today, a {when:%A}."
        if days == 1:
            return f"{when.day} {when:%B} is tomorrow, a {when:%A}."
        return f"{when.day} {when:%B} is a {when:%A}, {days} days away."
    bare = re.fullmatch(rf"(\d{{1,2}})(?:st|nd|rd|th)?", rest)
    if not bare:
        return None
    day = int(bare.group(1))
    this_month = None
    for step in range(3):
        # forwards for "what day is the 31st" (past months have gone by), backwards for "what
        # day was the 3rd", which wants the one just gone
        shift = -step if backwards else step
        month = (today.month - 1 + shift) % 12 + 1
        year = today.year + (today.month - 1 + shift) // 12
        try:
            guess = datetime.date(year, month, day)
        except ValueError:
            continue
        if backwards and guess > today:
            continue
        if not backwards and guess < today:
            continue
        this_month = guess
        break
    if this_month is None:
        return None
    next_month = today.month % 12 + 1
    next_year = today.year + (1 if today.month == 12 else 0)
    try:
        following = datetime.date(next_year, next_month, day)
    except ValueError:
        following = None
    if backwards or following is None or (following.month == this_month.month
                                          and following.year == this_month.year):
        said_next = ""
    else:
        said_next = f", and the {_ordinal(day)} of next month is a {following:%A}"
    days = (this_month - today).days
    if days == 0:
        return f"Today is the {_ordinal(day)}, a {this_month:%A}{said_next}."
    month_said = "this month" if this_month.month == today.month else this_month.strftime("%B")
    if days < 0:
        ago = -days
        return (f"The {_ordinal(day)} of {month_said} was a {this_month:%A}, "
                f"{ago} day{'' if ago == 1 else 's'} ago.")
    return (f"The {_ordinal(day)} of {month_said} is a {this_month:%A}, "
            f"{days} days away{said_next}.")


def _next_bank_holiday(clean):
    """The next bank holiday, its countdown, or the year's list: "when is the next bank holiday"."""
    import datetime
    text = _plain(clean)
    asking = _BANK_HOLIDAY_NEXT.fullmatch(text)
    counting = _BANK_HOLIDAY_COUNT.fullmatch(text)
    listing = _BANK_HOLIDAY_LIST.fullmatch(text)
    if not (asking or counting or listing):
        return None
    year, named_year, today = _feast_year(text)
    where, told_where = _bank_where(text)
    rows = _bank_holidays(year, where)
    ahead = [row for row in rows if row[1] >= today]
    if not ahead:
        year += 1
        rows = _bank_holidays(year, where)
        ahead = rows
    when = ahead[0]
    after = ahead[1] if len(ahead) > 1 else _bank_holidays(year + 1, where)[0]
    days = (when[1] - today).days
    if listing and not asking and not counting:
        left = [row for row in rows if row[1] >= today]
        said = ", ".join(f"{name} on {_said_with_a_weekday(day)}" for name, day in left)
        if where != "england":
            return f"{told_where[:1].upper()}{told_where[1:]} the bank holidays left this year are {said}."
        return (f"In England and Wales the bank holidays left this year are {said}. "
                "Scotland and Northern Ireland keep a few of their own as well.")
    if days == 0:
        return (f"Today is a bank holiday {told_where}: {when[0][:1].upper()}{when[0][1:]}, "
                f"{_said_with_a_weekday(when[1])}. The next one after that is {after[0]} on "
                f"{_said_with_a_weekday(after[1])}.")
    if counting:
        return (f"{days} day{'' if days == 1 else 's'} until the next bank holiday {told_where}: "
                f"{when[0]} on {_said_with_a_weekday(when[1])}.")
    return (f"The next bank holiday {told_where} is {when[0]} on "
            f"{_said_with_a_weekday(when[1])}, {days} day{'' if days == 1 else 's'} away. "
            f"After that it is {after[0]} on {_said_with_a_weekday(after[1])}.")


def _today(clean):
    """Today's date, and when the next Monday is.

    "What day is it today" is arithmetic on the clock, not knowledge, so it is worked out
    rather than guessed: the bot already counts days to Christmas the same way. The whole
    cleaned line has to be the question, so "what day is christmas" stays a date question
    about Christmas and "what day suits you" stays a plan.
    """
    import datetime
    text = _plain(clean)
    today = datetime.date.today()

    if re.fullmatch(_TODAY_ASK, text):
        return f"It's {_day_text(today)}."

    # "is it friday today" asks for a yes or a no, not a date.
    name, index, _ = _weekday_of(text, r"is (?:it|today) (?:still )?")
    if name:
        if index == today.weekday():
            return f"Yes, it's {_day_text(today)}."
        return f"No, it's {_day_text(today)}."

    ask = (r"(?:how many (?:days?|sleeps?) (?:is it |are there |do i have )?"
           r"(?:until|till|til|to go before|before|to) |how long (?:until|till|til|to) "
           r"|what date is |what date is it on |what day is |what day is it on "
           r"|which date is |what day does |what date does "
           r"|what(?:'s|s| is) the date(?: of| on| next| this)? "
           r"|what(?:'s|s| is) the (?:day|date) of "
           r"|when(?:'s|s) |when is |when does )")
    name, index, next_one = _weekday_of(text, ask)
    if name:
        ahead = (index - today.weekday()) % 7
        if ahead == 0 and next_one:
            ahead = 7
        when = today + datetime.timedelta(days=ahead)
        if ahead == 0:
            return f"{name} is today, {_short_date(when)}."
        if ahead == 1:
            return f"{name} is tomorrow, {_short_date(when)}."
        if ahead == 7:
            return f"{name} is a week away, on {_short_date(when)}."
        return f"{name} is {ahead} days away, on {_short_date(when)}."
    return None


_UNITS = {
    "second": ("second", "seconds", "sec", "secs"),
    "minute": ("minute", "minutes", "min", "mins"),
    "hour": ("hour", "hours", "hr", "hrs"),
    "day": ("day", "days"),
    "week": ("week", "weeks"),
    "month": ("month", "months"),
    "year": ("year", "years"),
    "ounce": ("ounce", "ounces", "oz"),
    "pound": ("pound", "pounds", "lb", "lbs"),
    "stone": ("stone", "stones"),
    "gram": ("gram", "grams", "g", "gr"),
    "kilogram": ("kilogram", "kilograms", "kilo", "kilos", "kg"),
    "centimetre": ("centimetre", "centimetres", "centimeter", "centimeters", "cm"),
    "inch": ("inch", "inches"),
    "metre": ("metre", "metres", "meter", "meters"),
    "foot": ("foot", "feet", "ft"),
    "mile": ("mile", "miles"),
    "pint": ("pint", "pints", "pt"),
    "millilitre": ("millilitre", "millilitres", "milliliter", "milliliters", "ml"),
    "litre": ("litre", "litres", "liter", "liters", "l"),
    "cup": ("cup", "cups"),
    "tablespoon": ("tablespoon", "tablespoons", "tbsp"),
    "teaspoon": ("teaspoon", "teaspoons", "tsp"),
}


_UNIT = {alias: name for name, aliases in _UNITS.items() for alias in aliases}


# How many of the first unit go into one of the second. The answer is written out, not
# calculated from a factor, so each one can say the thing a person actually wants to know.
FACTS = {
    ("second", "minute"): "There are 60 seconds in a minute.",
    ("minute", "hour"): "There are 60 minutes in an hour.",
    ("hour", "day"): "There are 24 hours in a day.",
    ("day", "week"): "There are 7 days in a week, so a fortnight is 14.",
    ("hour", "week"): "There are 168 hours in a week: 7 days × 24 hours.",
    ("minute", "day"): "There are 1,440 minutes in a day: 24 hours × 60 minutes.",
    ("second", "day"): "There are 86,400 seconds in a day: 24 × 60 × 60.",
    ("second", "year"): ("There are 31,536,000 seconds in an ordinary year (365 × 24 × 60 × 60), "
                          "and 31,622,400 in a leap year."),
    ("minute", "year"): ("There are 525,600 minutes in an ordinary year, and 527,040 in a leap "
                          "year."),
    ("hour", "year"): "There are 8,760 hours in an ordinary year, and 8,784 in a leap year.",
    ("week", "year"): ("There are 52 weeks and 1 day in an ordinary year (52 weeks and 2 days "
                         "in a leap year), or about 52.14 weeks if you divide 365 by 7."),
    ("day", "year"): ("An ordinary year has 365 days; a leap year has 366, with 29 February. "
                        "Leap years come every four years, except most century years."),
    ("month", "year"): "There are 12 months in a year, from January to December.",
    ("ounce", "pound"): "There are 16 ounces in a pound, and 14 pounds in a stone.",
    ("pound", "stone"): "There are 14 pounds in a stone.",
    ("gram", "kilogram"): ("There are 1,000 grams in a kilogram, and 1,000 kilograms in a "
                            "tonne."),
    ("gram", "ounce"): "There are about 28.35 grams in an ounce, so 100g is about 3.5oz.",
    ("pound", "kilogram"): ("There are about 2.2 pounds in a kilogram, so 70kg is about 154lb "
                             "and 1lb is about 0.45kg."),
    ("centimetre", "metre"): "There are 100 centimetres in a metre, and 1,000 metres in a kilometre.",
    ("centimetre", "inch"): "There are 2.54 centimetres in an inch, so 30cm is just under 12 inches.",
    ("inch", "foot"): "There are 12 inches in a foot, and 3 feet in a yard.",
    ("foot", "mile"): "There are 5,280 feet in a mile, which is 1,760 yards.",
    ("millilitre", "litre"): "There are 1,000 millilitres in a litre.",
    ("millilitre", "cup"): ("A US cup is about 240ml and a UK cup is 250ml, so half a cup is "
                              "around 120ml."),
    ("gram", "cup"): ("It depends what you're measuring: a cup is about 120g of flour, 200g of "
                       "sugar, 225g of butter or 185g of rice."),
    ("millilitre", "tablespoon"): ("A tablespoon is 15ml and a teaspoon is 5ml, so three "
                                    "teaspoons make a tablespoon."),
    ("millilitre", "pint"): "A UK pint is 568ml and a US pint is 473ml, so a UK pint is just over half a litre.",
    ("pint", "litre"): "There are about 1.76 UK pints in a litre, or 2.1 US pints.",
    ("teaspoon", "tablespoon"): ("Three teaspoons make a tablespoon, and a tablespoon is 15ml "
                                  "against a teaspoon's 5ml."),
}


_TAILS = (
    r"(?:are there |is there |are |is )?(?:in|to|per) (?:a |an |one |1 )?([a-z']+)(?: of .*)?",
    r"(?:does|do) (?:a |an |one )?([a-z']+)(?: have| contain| make up)?",
    r"(?:is|are) (?:a |an |one |1 )?([a-z']+)(?: of .*)?",
    r"([a-z']+) (?:has|have)(?: how many)?",
)


# "how much is a kilo in grams", "how much is a cup in ml"
_HOW_MUCH = (r"how much (?:is |are )?(?:a |an |one |1 )?([a-z']+)(?: of [a-z]+)? (?:in|to) "
             r"(?:a |an |one |1 )?([a-z']+)(?: of .*)?")


# "how heavy is a stone", "how much does a pound weigh": the weight of one unit on its own,
# which is not a conversion, so the FACTS table never saw it. On main these were a punt
# ("how heavy is an ounce", "what does a kilogram weigh"), a live-price hedge ("how much does
# a pound weigh", "how much is a stone") and, for "how heavy is a kilo", the lose-weight plan -
# because "kilo" is in the diet row's key. The answer is the unit written out in the others,
# which is the same fact the conversions use, so it lives here beside them.
HOW_HEAVY = {
    "stone": ("A stone is 14 pounds, which is about 6.35kg: 10 stone is 63.5kg and 12 stone is "
              "about 76kg."),
    "stones": ("A stone is 14 pounds, which is about 6.35kg: 10 stone is 63.5kg and 12 stone is "
               "about 76kg."),
    "pound": "A pound is 16 ounces, about 454g, and 14 pounds make a stone.",
    "pounds": "A pound is 16 ounces, about 454g, and 14 pounds make a stone.",
    "lb": "A pound is 16 ounces, about 454g, and 14 pounds make a stone.",
    "lbs": "A pound is 16 ounces, about 454g, and 14 pounds make a stone.",
    "ounce": "An ounce is about 28.35g, and there are 16 ounces in a pound.",
    "ounces": "An ounce is about 28.35g, and there are 16 ounces in a pound.",
    "oz": "An ounce is about 28.35g, and there are 16 ounces in a pound.",
    "kilo": "A kilo is 1,000 grams, which is about 2.2 pounds: 70kg is about 11 stone.",
    "kilos": "A kilo is 1,000 grams, which is about 2.2 pounds: 70kg is about 11 stone.",
    "kilogram": "A kilo is 1,000 grams, which is about 2.2 pounds: 70kg is about 11 stone.",
    "kilograms": "A kilo is 1,000 grams, which is about 2.2 pounds: 70kg is about 11 stone.",
    "kg": "A kilo is 1,000 grams, which is about 2.2 pounds: 70kg is about 11 stone.",
    "gram": "A gram is a thousandth of a kilo. A paperclip or a sachet of sugar is about a gram.",
    "grams": "A gram is a thousandth of a kilo. A paperclip or a sachet of sugar is about a gram.",
    "g": "A gram is a thousandth of a kilo. A paperclip or a sachet of sugar is about a gram.",
    "tonne": "A tonne is 1,000kg, which is about 2,205 pounds.",
    "tonnes": "A tonne is 1,000kg, which is about 2,205 pounds.",
    "ton": ("A ton is 1,016kg in the UK and 907kg in the US; a tonne, spelled with the e, is "
            "1,000kg."),
    "tons": ("A ton is 1,016kg in the UK and 907kg in the US; a tonne, spelled with the e, is "
             "1,000kg."),
}


# The whole line has to be the question, for the same reason as the conversions: "how heavy is
# a bag of sugar" is answered by its own row, and "how much does a share weigh on my mind" is
# not about a unit at all.
_HEAVY = re.compile(r"(?:how (?:heavy|much) (?:is|does|do|are)|what (?:does|is)|"
                    r"how much does)\s+(?:a |an |one |1 )?([a-z']+?)\s*"
                    r"(?:weigh(?:s)?|weigh in at|in weight)?\s*(?:in kilos|in kg|in pounds|"
                    r"in pounds and ounces|in lbs)?")


def _unit_pair(counted, of_unit):
    """The fact for this pair, whichever way round the question asked it."""
    return FACTS.get((counted, of_unit)) or FACTS.get((of_unit, counted))


def _unit_fact(clean):
    """How many of one unit make another, when that is the question asked.

    The question has to be the whole line: "how many hours in a week" is the fact, and
    "how many hours a week should I work out" is a training plan that must not be
    answered with 168. This is why these facts are computed here instead of being
    entries: an entry matches words anywhere in a line, and words like "hours" and
    "week" turn up in questions that are not about arithmetic at all.
    """
    text = _plain(clean)
    match = re.fullmatch(_HEAVY, text)
    if match:
        return HOW_HEAVY.get(match.group(1))
    match = re.fullmatch(_HOW_MUCH, text)
    if match:
        counted, of_unit = _UNIT.get(match.group(1)), _UNIT.get(match.group(2))
        if counted and of_unit:
            return _unit_pair(counted, of_unit)
        return None
    match = re.fullmatch(_AMOUNT, text)
    if not match:
        return None
    counted = _UNIT.get(match.group(1))
    if not counted:
        return None
    for pattern in _TAILS:
        tail = re.fullmatch(pattern, match.group(2))
        if tail:
            of_unit = _UNIT.get(tail.group(1))
            if of_unit:
                return _unit_pair(counted, of_unit)
    return None


_WAGE = r"£?\s*(\d[\d,]*(?:\.\d+)?)\s*(k|grand|thousand)?"


_WAGE_UNIT = re.compile(r"\s*(?:a|per|each|every|/)\s*(?:month|week|fortnight|year|day|hour)\b",
                        re.IGNORECASE)


_AN_HOUR = ("an hour", "per hour", "/hour", "/hr", "/h ", "a hour", "hourly rate of")


_HOURS_WORKED = re.compile(r"\b(\d{1,2}(?:\.\d+)?)\s*(?:-|to)?\s*(?:\d{1,2}(?:\.\d+)?\s*)?"
                           r"(?:hours?|hrs?)\b", re.IGNORECASE)


# The cue, then the setting: "an hour" alone is a half hour run, and "32k a year" alone is a
# mortgage question. Both words together are someone asking what their time is paid.
_WAGE_CUE = re.compile(r"\b(?:hourly|hour rate|rate an hour|per hour|an hour)\b")


_WAGE_CONTEXT = re.compile(r"\b(?:salary|wage|wages|pay|paid|earn|earns|earning|get|gets|worth|"
                           r"job|offer|contract|work|year|annual|month)\b")


def _hours_a_week(text):
    """The hours the line says they work: "37.5 hours a week", "40 hours". 0 when it says none."""
    for match in _HOURS_WORKED.finditer(text):
        try:
            value = float(match.group(1))
        except ValueError:
            continue
        if 5 <= value <= 70:
            return value
    return 0.0


def _hourly_named(text):
    """The rate the line states, in pounds and pence: "12.50 an hour" is not £12."""
    for match in re.finditer(_WAGE + r"\s*([^.;!?]{0,18})", text):
        tail = " " + (match.group(3) or "").lower()
        if any(unit in tail for unit in _AN_HOUR):
            try:
                amount = float(match.group(1).replace(",", ""))
            except ValueError:
                continue
            return amount * 1000 if match.group(2) else amount
    return 0.0


def _yearly_named(text):
    """A bare salary: "on 25k", "i earn 45000". A figure with a rate unit after it is not one."""
    best = 0.0
    for match in re.finditer(_WAGE, text):
        try:
            amount = float(match.group(1).replace(",", ""))
        except ValueError:
            continue
        if match.group(2):
            amount *= 1000
        if _WAGE_UNIT.match(text[match.end():match.end() + 16]):
            continue
        if amount >= 1000 and amount > best:
            best = amount
    return best


def _pounds(value):
    return f"{int(round(value)):,}"


def _rate(hours):
    """37.5 stays 37.5 and 12.50 stays 12.50: pence in a rate are not noise."""
    return f"{hours:.2f}" if abs(hours - round(hours)) > 1e-9 else str(int(round(hours)))


def _a_yearline(text):
    """The yearly figure the line names, from "30000 a year", "2200 a month" or a bare "25k"."""
    for pattern, scale in ((_WAGE + r"\s*(?:a|per|each|every)\s*year", 1),
                           (_WAGE + r"\s*(?:a|per|each|every)\s*month", 12)):
        for match in re.finditer(pattern, text):
            try:
                amount = float(match.group(1).replace(",", ""))
            except ValueError:
                continue
            if match.group(2):
                amount *= 1000
            return amount * scale
    return 0.0


def _wage_rate(text):
    """A salary in hours, or an hourly rate in a year. None when the line is not that sum."""
    hours = _hours_a_week(text) or 37.5
    rate = _hourly_named(text)
    yearly = _a_yearline(text) or _yearly_named(text)
    asks_a_year = bool(re.search(r"\b(?:a year|per year|annual|annually|yearly|salary)\b", text))
    if rate and not yearly and rate <= 500:
        year = rate * hours * 52
        return (f"£{_rate(rate)} an hour over {_rate(hours)} hours a week is about £{_pounds(year)} "
                f"a year before tax, £{_pounds(year / 12)} a month. Over 40 hours a week the same "
                f"rate is £{_pounds(rate * 40 * 52)}, and paid holiday is already in the 52 weeks.")
    if yearly >= 1000:
        hourly = yearly / (hours * 52)
        said = (f"£{_pounds(yearly)} a year over {_rate(hours)} hours a week is about "
                f"£{_number(round(hourly, 2))} an hour before tax, £{_pounds(yearly / 12)} a "
                f"month, £{_pounds(yearly / 52)} a week.")
        if abs(hours - 40) > 0.01:
            said += (f" Over 40 hours a week it is £{_number(round(yearly / (40 * 52), 2))}.")
        return said + " Take off any unpaid lunch break first: you are only paid for the hours you work."
    if asks_a_year and re.search(r"\b(?:hourly|hour rate|an hour|per hour)\b", text):
        return ("Take the yearly salary and divide it by the hours you actually work: £30,000 over "
                "37.5 hours a week for 52 weeks is £15.38 an hour, and over 40 hours it is £14.42. "
                "Do it before tax, drop any unpaid lunch break, and divide by 12 for the month.")
    return None


def solve(text, understood, memory):
    """A computed maths reply, or None when the line is not a calculation."""
    clean = (understood or {}).get("clean") or " ".join(str(text).lower().split())
    # Nothing here answers while the bot's last real answer was an emergency: a number said out
    # loud in that thread is not a sum to work out, it is the person still in the emergency.
    if in_a_safety_thread(memory):
        return None
    if _WAGE_CUE.search(clean) and _WAGE_CONTEXT.search(clean):
        # _wage answers the period the person actually asked for ("how much is that a
        # week" gets a week), so it goes first; _wage_rate is the fallback for a line it
        # declines, where the extra monthly and 40-hour figures still help.
        said = _wage(clean) or _wage_rate(clean)
        if said:
            return said
    for answer in (_quadratic(clean), _simplify(clean), _add_fractions(clean),
                   _the_factors(clean), _common_factors(clean), _round_to(clean), _circle_measure(clean),
                   _box_volume(clean), _equation(clean), _root(clean), _roots(clean),
                   _prime(clean),
                   _what_percent(clean), _percent_on(clean), _a_share_of_a_group(clean),
                   _fraction_decimal(clean),
                   _fraction(clean), _fraction_of(clean), _share(clean), _percent(clean),
                   _percentage_change(clean), _percent_rise(clean),
                   _percent_of_the_figure_in_the_chat(clean, memory), _tip(clean),
                   _left_on_the_bill(clean),
                   _wage(clean), _travel(clean),
                   _at_a_pace(clean, memory),
                   _save_by_a_date(clean, memory), _save_time(clean), _saving(clean),
                   _time_to_reach(clean, memory),
                   _a_goal_without_a_rate(clean, memory),
                   _time_at_a_new_rate(clean, memory),
                   _time_at_a_new_total(clean, memory),
                   _time_without_a_goal(clean, memory),
                   _figure_just_given(clean, memory),
                   _deadline_for_a_goal(clean, memory), _save_by_a_date(clean, memory),
                   _each_month_for_a_goal(clean, memory), _a_working_week(clean),
                   _convert(clean, memory), _unit_fact(clean),
                   _average(clean), _area(clean), _perimeter_of_a_room(clean),
                   _days_in_month(clean),
                   _today(clean), _days_until(clean), _date_counted_from_today(clean),
                   _days_until_easter(clean), _named_day_date(clean), _the_weekday_of_a_date(clean),
                   _next_bank_holiday(clean),
                   _days_until_a_relative_day(clean),
                   _days_until_a_named_day(clean),
                   _days_until_a_month_or_season(clean),
                   _days_left_in_the_month_or_the_year(clean),
                   _working_days_or_weekends_until(clean),
                   _how_long_ago(clean)):
        if answer:
            return answer
    return _calc(clean)


# The unit facts people ask for by name ("how many grams in an ounce") are computed in
# _unit_fact() above, because they need the shape of the whole question to answer safely.
# --- averages -----------------------------------------------------------------
# "What is an average" is a definition, but "what is the median of 3, 5 and 10" is a sum
# waiting to be done, so one entry answers both: the line's own numbers are worked out when
# it types two or more, and the three averages are explained when it only asks what they are.
_AVERAGE_FILLER = {
    "what", "whats", "is", "are", "an", "a", "the", "how", "do", "does", "i", "you", "we",
    "work", "worked", "out", "working", "calculate", "find", "workout", "mean", "means",
    "average", "averages", "median", "mode", "difference", "between", "and", "define",
    "explain", "statistics", "vs", "in", "maths", "math", "to", "of", "that", "this", "for",
    "get", "tell", "me", "know", "it", "called", "please", "explanation", "definition",
    "set", "numbers", "number", "data", "list", "values", "value", "group", "series",
    "sequence", "sample", "figures", "bits",
}


_AVERAGE_EXPLAIN = (
    "The mean, which is what most people mean by an average, is the total shared out evenly: "
    "4, 6 and 11 add to 21, and 21 ÷ 3 = 7, so the mean is 7. The median is the middle one "
    "once they are in order (6 above), and the mode is the value that appears most often.")


# A line that asks for the median gets the median in the first sentence, not the mean.
_MEDIAN_EXPLAIN = (
    "The median is the middle one once the numbers are in order: 1, 4 and 11 is 4, and "
    "1, 4, 6 and 11 is halfway between 4 and 6, so 5. It is the one to use when a few big "
    "numbers would drag a mean up, like house prices or wages. The mean is the total shared "
    "out evenly, and the mode is the value that appears most often.")


_MODE_EXPLAIN = (
    "The mode is the value that appears most often: in 2, 3, 3 and 7 it is 3, and if nothing "
    "repeats there is no mode at all. It is the one to use for the commonest answer rather "
    "than a middle one, like the most usual shoe size. The mean is the total shared out "
    "evenly, and the median is the middle one once the numbers are in order.")


def _figures(clean):
    """The numbers the line types out, in order: "the median of 3, 5 and 10" is 3, 5 and 10."""
    found = re.findall(r"(?<![\w.])\d+(?:\.\d+)?", clean)
    return [Fraction(number) for number in found]


def _short(value):
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


# The "mean" that ends "what does the median mean" is the question's verb, not the statistic
# being asked about, so it is taken off before the words are read as keywords. Otherwise a line
# that names the median looked like the comparison "mean and median", and the mean explainer
# answered a question about the median. Anything after the verb is filler too ("what does the
# median mean in maths"), so the words after it are skipped while they are filler and the verb
# is dropped when it is the last real word.
_MEAN_VERB = ("mean", "means", "meaning")


# The statistic the line names is what is being asked about; "that", "it" and "this" are the
# thing meant, so the "mean" after them is the line's verb. "whats that mean" and "what does it
# mean" were answered with the mean explainer - a definition of the mean average for a person
# asking what the bot's last answer meant - because every word of them is filler, "mean"
# included. The same line with "does" in it was read correctly, so the spelling was what decided
# it. A line that names a statistic of its own ("what does the median mean") still answers.
_STATISTIC_WORDS = ("average", "averages", "mean", "means", "median", "mode", "statistics")


_OTHER_STATISTICS = ("average", "averages", "median", "mode")


_POINTS_AT_A_THING = ("that", "this", "it", "these", "those", "you", "me", "we", "they",
                      "he", "she", "them", "what", "whats", "how", "which")


def _names_a_statistic(asked):
    """Whether the line names the statistic it asks about, rather than pointing at a thing."""
    words = [word.strip("?.!,") for word in asked.split()]
    for index, word in enumerate(words):
        if word not in _STATISTIC_WORDS:
            continue
        if word in _MEAN_VERB:
            before = words[index - 1] if index else ""
            if before in _POINTS_AT_A_THING:
                continue
            if any(other in _OTHER_STATISTICS for other in words):
                continue
        return True
    return False


def _about_words(asked):
    words = asked.split()
    i = len(words) - 1
    while i > 0 and words[i].strip("?.!,") in _AVERAGE_FILLER \
            and words[i].strip("?.!,") not in _MEAN_VERB:
        i -= 1
    if i > 0 and words[i].strip("?.!,") in _MEAN_VERB:
        words = words[:i] + words[i + 1:]
    return " ".join(words)


def _averages(memory, understood):
    clean = (understood or {}).get("clean") or (understood or {}).get("text") or ""
    figures = _figures(clean)
    asked = clean.lower()
    about = _about_words(asked)
    if len(figures) < 2:
        # A definition, not a sum: answer only when the line is all ask and no subject
        # ("what is the average rent in london" is a different question, so pass).
        words = [word for word in re.findall(r"[a-z']+", asked)]
        if all(word in _AVERAGE_FILLER for word in words) and _names_a_statistic(asked):
            if ("median" in asked and "mean" in about) or "difference" in asked:
                return _AVERAGE_EXPLAIN  # the comparison is the question, so name them all
            if "median" in asked:
                return _MEDIAN_EXPLAIN
            if "mode" in asked:
                return _MODE_EXPLAIN
            return _AVERAGE_EXPLAIN
        return None
    ordered = sorted(figures)
    listed = ", ".join(_short(figure) for figure in ordered)
    mean = sum(ordered) / len(ordered)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        median = ordered[middle]
    else:
        median = (ordered[middle - 1] + ordered[middle]) / 2
    counts = {}
    for figure in ordered:
        counts[figure] = counts.get(figure, 0) + 1
    top = max(counts.values())
    if "median" in asked:
        return (f"The median of {listed} is {_short(median)}: in order, that is the middle "
                f"one.")
    if "mode" in asked:
        if top == 1:
            return (f"No number in {listed} repeats, so there is no mode. The mean is "
                    f"{_short(mean)} and the median is {_short(median)}.")
        mode = [figure for figure, count in counts.items() if count == top][0]
        return f"The mode of {listed} is {_short(mode)}, the number that appears most often."
    total = sum(ordered)
    return (f"The mean of {listed} is {_short(mean)}: they add to {_short(total)} and "
            f"{_short(total)} ÷ {len(ordered)} = {_short(mean)}.")


# "round" is a word about people and places far more often than it is the maths verb, and the
# rounding card keyed on it answered all of them: "my friends are coming round what should i
# watch" and "how do i stop my mum coming round" both got the digit rule, and "how many in a
# round of golf" got it too. These phrases name the other subject - someone moving about, a
# place, a thing that comes in rounds - so the card stands down and the family, watching or
# golf entry has the line. Every one of them is a phrase of two or three words on purpose: a
# bare "round" in the avoid list would stand down "how do i round to two decimal places" as
# well, which is the line the card exists for.
ROUND_IS_NOT_THE_VERB = (
    "come round", "came round", "coming over round", "go round", "went round",
    "walk round", "run round", "ran round", "drive round", "drove round", "crawl round",
    "crawling round", "show round", "look round", "turn round", "round the corner",
    "round the house", "round the garden", "round the shops", "round the floor",
    "round the back", "round the world", "round here", "year round", "all year round",
    "round for dinner", "round for tea", "round for lunch", "round to see", "round trip",
    "round of drinks", "round of golf", "round of applause", "rounds of",
    # a round of boxing is three minutes, not a number read to two decimal places
    "boxing", "boxer", "boxers", "boxercise", "round of boxing", "rounds of boxing",
    "a fight", "fights", "sparring",
    # "round the bath", "round the window" and "round the worktop" are places a seal goes, not a
    # number: "how do i reseal round the bath" was told how to round 3.456 to two decimal places
    "round the bath", "round the bath and", "round a bath", "round the shower", "round the sink",
    "round the basin", "round the window", "round the window frame", "round the door",
    "round the worktop", "round the edges", "round the tiles", "round the skirting",
    "round the tiles and", "round the bottom", "round the toilet", "round the outside",
)


# "round" is a preposition more often than it is the maths verb, and it is "around" in every one
# of those lines: "how do i fit the stair gate round the newel post" was told how to round 3.456
# to two decimal places. Listing the places does not work - a list of the ones we thought of is
# always missing the next one - so the shape does it: "round" followed by an article and a noun
# is a place or a thing gone around, unless that noun is one of the number words the card is for.
_ROUND_IS_AROUND = re.compile(
    r"\brounds?\s+(?:the|a|an|my|your|his|her|its|our|their|this|that)\s+"
    r"(?!(?:number|numbers|digit|digits|decimal|decimals|answer|answers|figure|figures|value|"
    r"values|sum|total|result|nearest|whole|next)\b)\w+")


# "round work", "round the kids", "round the traffic", "how do you work round a toddler": the
# preposition, not the verb. `_ROUND_IS_AROUND` above reads the "round the thing" shapes; the one
# it cannot read is the bare noun, and on a line with a "how" and a "work" - "how do i fit the
# studying round work" - the card still answered with the digit rule. Rounding is an answer to a
# line that carries a number or names the thing itself, so that is the second half of the gate.
ROUNDING_NAMED = re.compile(
    r"\bround(?:s|ed|ing)?\s+(?:a\s+|the\s+|off\s+|up\s+|down\s+)?"
    r"(?:number|numbers|decimal|decimals|figure|figures|digit|digits|whole|thousand|thousands"
    r"|hundred|hundreds|ten|tens)\b"
    r"|\b(?:number|numbers|decimal|decimals|figure|figures|digit|digits)\s+(?:is\s+|are\s+)?"
    r"round(?:s|ed|ing)?\b"
    r"|\bround(?:ed|ing)?\s+(?:up|down)\s+(?:the\s+|a\s+|your\s+)?"
    r"(?:price|prices|cost|bill|total|number|figure|amount|sum|pence|penny|pennies|pounds|pound"
    r"|decimal|decimals|digit|digits)\b"
    # A bare "nearest" is not a number: "whats the nearest cashpoint", "where is the nearest
    # chemist", "how do i find my nearest recycling centre" are all place questions, and the card
    # answered them with the digit rule ("Look at the digit just after the place you are keeping")
    # because the word alone was the sign. Rounding is what "nearest" means when a place value
    # follows it - nearest whole, nearest ten, nearest penny - or when it is the end of a line
    # that has already said round ("how do i round to the nearest").
    r"|\brounding\b|\bdecimal places?\b|\bsignificant figures?\b"
    r"|\bnearest\s+(?:whole|ten|tens|hundred|hundreds|thousand|thousands|million|penny|pence"
    r"|pound|pounds|decimal|digit|digits|number|numbers|integer|unit|one|\d)\b"
    r"|\bround(?:s|ed|ing)?\s+(?:it\s+)?(?:to|at)\s+(?:the\s+)?nearest\b"
    # "what does round mean in maths": the word is the subject of the question, and maths is what
    # the line says it is about.
    r"|\bmaths?\b|\bmathematics\b")


def _a_rounding_question(understood):
    """True when the line is about rounding a number, not about working round something.

    A digit anywhere in the line is the plain sign of it - "round 3.456 to two decimal places",
    "what is 2.5 rounded to the nearest whole number", "round 47 to the nearest ten". Without one
    the line has to name the thing: "how do you round numbers", "what are the rules for rounding".
    """
    line = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    if re.search(r"\d", line):
        return True
    return ROUNDING_NAMED.search(line) is not None
