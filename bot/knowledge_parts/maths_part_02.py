"""Part 2 of 6 of a large module, split out of `maths`.

Everything here is re-exported from `maths`, so callers import it from there as before.
"""
import re

from ..memory.saving import a_rate_put_right
from ..knowledge import units
from .maths_part_01 import (
    _amount, _number, _COUNT, _COUNTS, _parse,
)


def _what_percent(clean):
    """One number as a percentage of another: "what percentage is 15 of 80"."""
    part = total = None
    match = re.search(r"what (?:percentage|percent) of ([\d,.]+) is ([\d,.]+)", clean)
    if match:
        total, part = _amount(match.group(1)), _amount(match.group(2))
    if part is None:
        match = re.search(r"what (?:percentage|percent) (?:is )?([\d,.]+) (?:of|out of) "
                          r"([\d,.]+)", clean)
        if match:
            part, total = _amount(match.group(1)), _amount(match.group(2))
    if part is None:
        # The same sum the other way round: "20 is what percent of 80" puts the part first and
        # the question in the middle, which nothing read, so the line got an ack.
        match = re.search(r"([\d,.]+)\s+(?:is\s+)?what\s+(?:percentage|percent)\s+of\s+([\d,.]+)",
                          clean)
        if match:
            part, total = _amount(match.group(1)), _amount(match.group(2))
    if part is None:
        match = re.search(r"([\d,.]+) (?:out of|of) ([\d,.]+) (?:as a |in )?"
                          r"(?:percentage|percent)", clean)
        if match:
            part, total = _amount(match.group(1)), _amount(match.group(2))
    if part is None:
        match = re.search(r"([\d,.]+) as a (?:percentage|percent) of ([\d,.]+)", clean)
        if match:
            part, total = _amount(match.group(1)), _amount(match.group(2))
    if part is None or not total:
        return None
    share = part / total * 100
    said = _number(round(share, 1))
    exact = abs(share - round(share)) < 1e-9
    return f"{_number(part)} is {'exactly ' if exact else 'about '}{said}% of {_number(total)}."


def _a_share_of_a_group(clean):
    """A share scaled to a bigger group: "1 in 5 of 200" is 40 people.

    "if 1 in 5 people do it how many in 200" is the commonest way this turns up, and nothing
    answered it: the line was only noted back to the person. The share can be said in words
    ("one in five people") and the group can come before the question ("out of 200 people how
    many if 1 in 5"), so the two numbers are read separately: first the share, then the size of
    the group, from whatever wording carries it.
    """
    bare = _COUNT.strip("()")  # the alternation without its own group, so the two
    # numbers land in groups 1 and 2
    share = re.search(r"\b(%s)\s+in\s+(%s)\b" % (bare, bare), clean)
    if not share:
        return None
    top = _COUNTS.get(share.group(1))
    bottom = _COUNTS.get(share.group(2))
    if top is None or bottom is None:
        try:
            top, bottom = int(share.group(1)), int(share.group(2))
        except ValueError:
            return None
    if not bottom or top > bottom:
        return None
    rest = clean[:share.start()] + " " + clean[share.end():]
    # The size of the group, in any of the shapes people put it in, and never the share itself
    # (the share is cut out of the line first, so "1 in 5" cannot be read as a group of 5).
    size = None
    for pattern in (r"how many (?:people |of them |would that be )?(?:are |is )?"
                    r"(?:in|of|out of|from|out of a)\s+(\d+)",
                    r"\b(?:in|of|out of|from)\s+(\d+)\s+(?:people|persons|students|"
                    r"adults|children|kids|men|women|workers|drivers|homes|households)",
                    r"\b(?:out of|of|from)\s+(\d+)\b"):
        match = re.search(pattern, rest)
        if match:
            size = int(match.group(1))
            break
    if not size or size < 2:
        return None
    count = top * size / bottom
    if abs(count - round(count)) < 1e-9:
        answer = _number(int(round(count)))
    else:
        answer = "about " + _number(round(count, 1))
    said = "%s in %s" % (_number(top), _number(bottom))
    if top == 1:
        said = "1 in %s" % _number(bottom)
    return (f"{said} of {_number(size)} is {answer}. That is the share times the group: "
            f"{_number(size)} divided by {_number(bottom)}"
            + (f", times {_number(top)}." if top > 1 else "."))


def _percent_on(clean):
    """A percentage added to an amount: "add 20% to 40", "40 plus VAT", "add VAT to 240"."""
    # The school shape: "increase 40 by 25%" and "decrease 60 by 10%" name the amount first and
    # the change after it. A sum said that way had no row, so the line got an ack.
    match = re.search(r"\b(increase|decrease|raise|reduce|lower|go up|go down|goes up|goes down)"
                      r"\s+(?:of\s+)?(?:£|\$)?([\d,.]+)\s+by\s+(\d+(?:\.\d+)?)\s*"
                      r"(?:%|percent|per cent)", clean)
    if match:
        total, part = _amount(match.group(2)), _amount(match.group(3))
        going_down = match.group(1) in ("decrease", "reduce", "lower", "go down", "goes down")
        changed = total * (1 - part / 100 if going_down else 1 + part / 100)
        return (f"{_number(total)} {'decreased' if going_down else 'increased'} by "
                f"{_number(part)}% is {_number(round(changed, 2))}.")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s+"
                      r"(?:on(?:\s+top\s+of)?|onto|added\s+to)\s+"
                      r"(?:£|\$)?([\d,.]+)", clean)
    if match:
        part, total = _amount(match.group(1)), _amount(match.group(2))
        return f"{_number(total)} plus {_number(part)}% is {_number(total * (1 + part / 100))}."
    # "20 percent more than 45" and "20 percent less than 45" put the comparison in words, and
    # the answer is the new amount, not the percentage on its own - which is all the definition
    # of a percentage could give.
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s+"
                      r"(more|less|fewer|higher|lower)\s+than\s+(?:£|\$|€)?\s*([\d,.]+)", clean)
    if match:
        part, way, total = _amount(match.group(1)), match.group(2), _amount(match.group(3))
        if way in ("more", "higher"):
            return f"{_number(total)} plus {_number(part)}% is {_number(total * (1 + part / 100))}."
        return (f"{_number(total)} less {_number(part)}% is "
                f"{_number(total * (1 - part / 100))}.")
    # "a 45 pound thing with 20 percent off": the amount comes first and the discount after it.
    # The currency word is required, so "3 things with 20 percent off" is not read as a sum, and
    # a line that already says what the thing is or costs - "a coat is 60 pounds with 25 percent
    # off" - keeps the "off" row's wording below, which also says what is saved.
    if re.search(r"(?:costs?|priced at|is|are|was)\s+(?:£|\$|€)?\s*[\d,.]+\D.*?"
                 r"(?:\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s*off", clean):
        return None
    match = re.search(r"(?:£|\$|€)?\s*([\d,.]+)\s*(?:pounds?|quid|euros?|dollars?|bucks?)\s+"
                      r"(?:[a-z]+\s+){0,3}?(?:with|at|minus|less)\s+(\d+(?:\.\d+)?)\s*"
                      r"(?:%|percent|per cent)\s*off\b", clean)
    if match:
        total, part = _amount(match.group(1)), _amount(match.group(2))
        return (f"{_number(total)} less {_number(part)}% is "
                f"{_number(total * (1 - part / 100))}.")
    match = re.search(r"(?:add|increase)\s+(?:a\s+)?(\d+(?:\.\d+)?)\s*"
                      r"(?:%|percent|per cent)\s*(?:tip|service|tax|charge)?\s*"
                      r"(?:on|to|onto)\s+(?:£|\$)?([\d,.]+)", clean)
    if match:
        part, total = _amount(match.group(1)), _amount(match.group(2))
        return f"{_number(total)} plus {_number(part)}% is {_number(total * (1 + part / 100))}."
    # The same sum taken away: "subtract 10 percent from 55", "55 minus 10 percent", "knock
    # 15% off 80". The words are the only difference from the rows above, and a line that says
    # the amount is going down is asking for a smaller number, not a bigger one.
    # "knock 15% off 80" is the plain "15% off 80" line with a verb in front, and _percent
    # already answers it in its own words ("15% off 80 leaves 68 (you save 12)"). Only the
    # lines nothing answered change here.
    if re.search(r"\d+(?:\.\d+)?\s*(?:%|percent|per cent)\s*off\s+(?:£|\$)?[\d,.]+", clean):
        return None
    match = re.search(r"(?:subtract|deduct|minus|take|taking|remove|knock|strip)\s+(?:a\s+|off\s+)?"
                      r"(?:the\s+)?(\d+(?:\.\d+)?)\s*(?:%|percent|per cent|per cent)\s*"
                      r"(?:off|from|of)\s+(?:£|\$)?([\d,.]+)", clean)
    if match:
        part, total = _amount(match.group(1)), _amount(match.group(2))
        return (f"{_number(total)} less {_number(part)}% is "
                f"{_number(total * (1 - part / 100))}.")
    match = re.search(r"([\d,.]+)\s*(?:minus|less|without)\s*(\d+(?:\.\d+)?)\s*"
                      r"(?:%|percent|per cent)", clean)
    if match:
        total, part = _amount(match.group(1)), _amount(match.group(2))
        return (f"{_number(total)} less {_number(part)}% is "
                f"{_number(total * (1 - part / 100))}.")
    match = re.search(r"([\d,.]+)\s*(?:plus|and)\s*(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)",
                      clean)
    if match:
        total, part = _amount(match.group(1)), _amount(match.group(2))
        return f"{_number(total)} plus {_number(part)}% is {_number(total * (1 + part / 100))}."
    match = re.search(r"([\d,.]+)\s*(?:plus|with|including|before)\s+vat", clean)
    if match:
        total = _amount(match.group(1))
        return (f"{_number(total)} plus VAT at 20% is {_number(total * 1.2)}.")
    # The same sum the other way round in the sentence: "add VAT to 240". People put the
    # amount after the word as often as before it, and "add 20% VAT to 240" is the same line.
    match = re.search(r"(?:add|plus)\s+(?:(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s+)?"
                      r"(?:the\s+)?vat\s+(?:on|to|onto)\s*(?:£|\$)?([\d,.]+)", clean)
    if match:
        part = _amount(match.group(1)) if match.group(1) else 20.0
        total = _amount(match.group(2))
        return f"{_number(total)} plus VAT at {_number(part)}% is {_number(total * (1 + part / 100))}."
    # And the price with the VAT taken back off it, which is what a receipt asks for.
    match = re.search(r"(?:take|takes|taking|remove|removing|strip|knock)\s+(?:the\s+)?vat\s+"
                      r"(?:off|from|out of)\s*(?:£|\$)?([\d,.]+)", clean)
    if not match:
        match = re.search(r"([\d,.]+)\s*(?:minus|less|without|excluding|ex)\s+vat", clean)
    if match:
        total = _amount(match.group(1))
        return (f"{_number(total)} with VAT taken off is {_number(total / 1.2)}, "
                f"and the VAT in it is {_number(total - total / 1.2)}.")
    return None


# A price, a rent or a wage that gains or loses a percentage: "my rent is 800 and is going up
# 5 percent", "a 3 percent rise on 24000". The line names what the money is for, but what it
# asks for is still a sum - the tenancy row and the pay-rise row would answer the advice and
# never give the number - so the arithmetic is done here, ahead of the entries.
_PERCENT_UP = (r"(?:going|goes|went|gone|is|are)\s+up|up\s+by|rise|rises|rising|rose|"
               r"increase|increases|increased|more|higher|extra|hike|hikes|hiked|"
               r"jump|jumps|jumped|on\s+top|raise|raises|raised")


_PERCENT_DOWN = (r"(?:going|goes|went|gone|is|are)\s+down|down\s+by|drop|drops|dropped|"
                 r"fall|falls|fell|cut|cuts|slashed|reduce|reduced|less|cheaper|lower")


_PERCENT_ADVICE = ("should i", "fair", "legal", "allowed", "normal", "refuse", "worth it",
                   "can they", "can my landlord", "too much", "right", "negotiate", "accept")


_MONEY_WORD = re.compile(r"\b(?:rent|bill|price|salary|wage|wages|pay|cost|quote|fare|"
                         r"mortgage|charge|rate|total|fee|premium|budget|balance|"
                         r"deposit|pension|tax|income|earnings)\b")


def _percent_rise(clean):
    """The money a percentage adds to or takes off: "rent 800 going up 5 percent"."""
    percents = re.findall(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)", clean)
    if len(percents) != 1:
        return None
    part = float(percents[0])
    if not 0 < part <= 100:
        return None
    # The amount is the other number in the line, and it has to read as money: a currency
    # sign, three figures or more, or a word that says whose money it is. One of those keeps
    # "my pace went up 10 percent" out of here.
    money_word = bool(_MONEY_WORD.search(clean))
    amount = None
    for raw in re.finditer(r"(?:£|\$|€)?\s*(\d[\d,]*(?:\.\d+)?)", clean):
        number = _amount(raw.group(1))
        if abs(number - part) < 1e-9:
            continue
        if raw.group(0).strip()[:1] in "£$€" or number >= 100 or money_word:
            amount = number
            break
    if amount is None:
        return None
    if any(phrase in clean for phrase in _PERCENT_ADVICE):
        return None
    up = re.search(r"\b(?:%s)\b" % _PERCENT_UP, clean)
    down = re.search(r"\b(?:%s)\b" % _PERCENT_DOWN, clean)
    if bool(up) == bool(down):
        # nothing said about direction, or both said: leave it to the rows that read the line.
        return None
    change = amount * part / 100
    if up:
        return (f"{_number(part)}% of {_number(amount)} is {_number(change)}, so it goes up to "
                f"{_number(amount + change)}.")
    return (f"{_number(part)}% of {_number(amount)} is {_number(change)}, so it comes down to "
            f"{_number(amount - change)}.")


# The follow-up: "and 20 percent of that", "what would 5 percent be". The amount is not in the
# line because it was in the chat a turn or two ago, so the sum is worked out on that figure.
# A bare "my rent went up 5 percent" is not this - it has no ask and no "of that" - and stays
# with the rows that read the whole line.
_PERCENT_ASK_TAIL = re.compile(
    r"\b(?:of|off|on)\s+(?:that|it|this|those|them|the\s+(?:rent|bill|price|salary|total|"
    r"figure|number|amount|money))\b|\b(?:be|come\s+to|work\s+out\s+to)\b[\s?.!]*$")


_PERCENT_ASK_WORD = re.compile(r"\b(?:what|whats|what's|how\s+much|how\s+many|would|"
                               r"will|could|should|does|is|was)\b")


def _amount_in_the_chat(memory):
    """The last amount the person said, skipping the percentages in what they said."""
    for said in reversed((memory.get("turns") or [])[-3:]):
        if not isinstance(said, dict):
            continue
        text = re.sub(r"\d+(?:\.\d+)?\s*(?:%|percent|per cent)", " ",
                      str(said.get("user") or "").lower())
        numbers = re.findall(r"\d[\d,]*(?:\.\d+)?", text)
        if not numbers:
            continue
        value = _amount(numbers[-1])
        if value >= 10:
            return value
    return None


def _percent_of_the_figure_in_the_chat(clean, memory):
    """A percentage of the amount the chat already holds: "and 20 percent of that"."""
    percents = re.findall(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)", clean)
    if len(percents) != 1:
        return None
    if re.search(r"\d", re.sub(r"\d+(?:\.\d+)?\s*(?:%|percent|per cent)", " ", clean)):
        return None  # the line carries an amount of its own, so this is another row's sum
    reference = re.search(r"\b(?:of|on)\s+(?:that|it|this|those|them|the\s+(?:rent|bill|"
                         r"price|salary|total|figure|number|amount|money))\b", clean)
    off_reference = re.search(r"\b(?:off)\s+(?:that|it|this|those|them)\b", clean)
    asked = (_PERCENT_ASK_WORD.search(clean)
             and re.search(r"\b(?:be|come\s+to|work\s+out\s+to)\b[\s?.!]*$", clean))
    if not (reference or off_reference or asked):
        return None
    amount = _amount_in_the_chat(memory)
    if amount is None:
        return None
    part = float(percents[0])
    if not 0 < part <= 100:
        return None
    change = amount * part / 100
    if off_reference:
        return (f"{_number(part)}% off {_number(amount)} leaves {_number(amount - change)} "
                f"(you save {_number(change)}).")
    return f"{_number(part)}% of {_number(amount)} is {_number(change)}."


# --- tips and saving goals ------------------------------------------------
def _tip(clean):
    """A tip on a bill: "15% tip on 45", "tip on 80 at 15 percent"."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s*(?:tip|service|gratuity)"
                      r"\s*(?:on(?:\s+top\s+of)?|for|of)\s*(?:(?:a|an|the|my|our)\s+)?"
                      r"(?:(?:bill|total|check|tab)\s+of\s+)?(?:£|\$|€)?\s*([\d,.]+)", clean)
    if match:
        part, total = _amount(match.group(1)), _amount(match.group(2))
    else:
        match = re.search(r"(?:tip|service|gratuity)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*"
                          r"(?:%|percent|per cent)\s*(?:on|for|of)\s*(?:£|\$|€)?\s*([\d,.]+)",
                          clean)
        if match:
            part, total = _amount(match.group(1)), _amount(match.group(2))
        else:
            match = re.search(r"(?:tip|service|gratuity)\s*(?:on|for)\s*(?:£|\$|€)?\s*"
                              r"([\d,.]+)\s*(?:at|of)\s*(\d+(?:\.\d+)?)\s*"
                              r"(?:%|percent|per cent)", clean)
            if not match:
                return None
            total, part = _amount(match.group(1)), _amount(match.group(2))
    tip = total * part / 100
    return (f"A {_number(part)}% tip on {_number(total)} is {_number(tip)}, so "
            f"{_number(total + tip)} in total.")


# What somebody left on a bill, and whether it is enough: "we left 60 on a 48 bill" is a sum
# about the tip, and the laundry row read the 60 as a wash temperature and answered about towels.
_YOU_LEFT = re.compile(
    r"(?:left|leave|leaving|gave|give|put down|tipped|tip)\s+"
    r"(?:£|\$|€)?\s*(?P<left>\d[\d,]*(?:\.\d+)?|a tenner|a fiver|a twenty)\s*"
    r"(?:pounds?|quid|euros?|dollars?|bucks?)?\s*"
    r"(?:on|for|towards)\s+(?:a|an|the|our|my)?\s*(?:£|\$|€)?\s*"
    r"(?P<bill>\d[\d,]*(?:\.\d+)?)\s*(?:pounds?|quid|euros?|dollars?|bucks?)?\s*"
    r"(?P<what>bill|check|tab|meal|dinner|lunch|round)\b")


# The same sum with the bill word elsewhere: "i left 5 on 40 for the meal".
_YOU_LEFT_ANYWHERE = re.compile(
    r"(?:left|leave|leaving|gave|put down|tipped)\s+(?:£|\$|€)?\s*"
    r"(\d[\d,]*(?:\.\d+)?|a tenner|a fiver|a twenty)\s*"
    r"(?:pounds?|quid|euros?|dollars?|bucks?)?\s+"
    r"(?:on|for|towards)\s+(?:a|an|the|our|my)?\s*(?:£|\$|€)?\s*"
    r"(\d[\d,]*(?:\.\d+)?)")


_BILL_WORD = re.compile(r"\b(?:bill|tip|meal|dinner|lunch|check|tab|round|service)\b")


_A_NOTE = {"a tenner": 10, "a fiver": 5, "a twenty": 20}


def _two_places(value):
    """Money in a card's shape: 4.80 rather than 4.8, and 6 rather than 6.00."""
    text = f"{value:.2f}"
    return text[:-3] if text.endswith(".00") else text


def _left_on_the_bill(clean):
    """The percentage somebody left on a bill, and the usual tip on that bill."""
    match = _YOU_LEFT.search(clean)
    if match:
        left_text, bill_text = match.group("left"), match.group("bill")
    else:
        loose = _YOU_LEFT_ANYWHERE.search(clean)
        if not (loose and _BILL_WORD.search(clean)):
            return None
        left_text, bill_text = loose.group(1), loose.group(2)
    left = _A_NOTE.get(left_text) or _amount(left_text)
    bill = _amount(bill_text)
    if not left or not bill or left <= 0 or bill <= 0:
        return None
    percent = left / bill * 100
    money = next((sign for sign in ("£", "$", "€") if sign in clean), "£")
    usual = (f"{money}{_two_places(round(bill * 0.10, 2))} to "
             f"{money}{_two_places(round(bill * 0.125, 2))}")
    said = _number(round(percent, 1))
    if percent >= 10:
        return (f"That's {said}% of the {money}{_number(bill)} - the usual tip is ten to twelve "
                f"and a half ({usual}), so it's enough.")
    return (f"That's {said}% of the {money}{_number(bill)}, under the usual ten to twelve and a "
            f"half ({usual}). Check the bill for a service charge first, since that is the tip "
            f"already on it.")


def _save_time(clean):
    """How long a regular amount takes to reach a goal: "save 50 a month for 1000"."""
    if not re.search(r"how long|how many (?:months|weeks|years)|when will", clean):
        return None
    per = re.search(r"(?:save|saving|put away|putting away|set aside|setting aside)\s+"
                    r"(?:£|\$|€)?\s*([\d,.]+)\s*(?:a|per|each)\s*(month|week|year)", clean)
    goal = re.search(r"(?:to save|save up|reach|get to|hit|for)\s+(?:£|\$|€)?\s*([\d,.]+)",
                     clean)
    if not per or not goal:
        return None
    amount = _amount(per.group(1))
    total = _amount(goal.group(1))
    unit = per.group(2)
    if amount <= 0 or total <= 0:
        return None
    count = total / amount
    whole = int(count)
    if abs(count - whole) < 1e-9:
        length = f"{whole} {unit}{'' if whole == 1 else 's'}"
    else:
        length = f"about {_number(round(count, 1))} {unit}s"
    return f"Saving {_number(amount)} a {unit}, you get to {_number(total)} in {length}."


_PAY_WORDS = re.compile(r"\b(?:earn|earns|earning|wage|wages|salary|salaried|paid|pay|income|"
                        r"come to|comes to|coming to)\b")


_NOT_PAY = re.compile(r"\b(?:after tax|take home|take-home|national insurance|pension|"
                      r"student loan|miles? an hour|mph)\b")


_RATE = re.compile(r"(?:£|\$|€)?\s*(\d+(?:\.\d+)?)\s*"
                   r"(?:pounds?|quid|euros?|dollars?|bucks?)?\s*"
                   r"(?:an hour|a hour|per hour|hourly|/\s*hours?|/\s*hr|p/h)\b")


_HOURS_WEEK = re.compile(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*"
                         r"(?:a|per|each|/)\s*(?:week|wk)\b")


_ANNUAL = re.compile(r"(?:£|\$|€)?\s*(\d+(?:[.,]\d+)?)\s*(k)?\s*"
                     r"(?:pounds?|quid|euros?|dollars?|bucks?)?\s*"
                     r"(?:a|per|/)?\s*(?:year|annum|yr)\b(?!\s+olds?\b)")


# The word that tells a yearly figure from a length of time: a currency, a unit, or the language
# of pay itself. Without one, "3 year" is an age and "5 years" is how long something has been
# going on, and neither is a salary: "is an hour of cartoons a day too much for a 3 year old" was
# read as 3 pounds a year and answered with "£3 a year at 40 hours a week is about £0 an hour
# before tax" instead of the screen-time advice.
_MONEY_BESIDE = re.compile(
    r"£|\$|€|\b(?:pounds?|quid|euros?|dollars?|bucks?|salary|salaried|wage|wages|income|"
    r"earn|earns|earning|paid|pay|annum|per annum|pa)\b", re.I)


def _money(clean, amount):
    """The amount with the currency the person used, so a dollar question stays in dollars."""
    if "€" in clean or "euro" in clean:
        sign = "€"
    elif "$" in clean or "dollar" in clean:
        sign = "$"
    else:
        sign = "£"
    text = f"{amount:,.2f}"
    if text.endswith(".00"):
        text = text[:-3]
    return f"{sign}{text}"


def _annual_pay(clean):
    """The yearly figure in the line, or None when the number is an age or a length of time.

    Every part of _ANNUAL is optional, which is what lets "30000 a year" and "30k a year" both
    read as a salary; the price is that a bare "3 year" reads as one too. So a figure with no
    currency, no unit, no "k" and fewer than four digits has to be carried by the language of pay
    somewhere in the line ("i earn 40 a year" is odd but it is a wage question; "my 3 year old"
    is not).
    """
    match = _ANNUAL.search(clean)
    if not match:
        return None
    if match.group(2):
        return match  # "30k"
    digits = re.sub(r"[.,]", "", match.group(1))
    if len(digits) >= 4:
        return match  # "30000"
    if _MONEY_BESIDE.search(clean):
        return match
    return None


def _wage(clean):
    """Pay worked out from an hourly rate, or an hourly rate from a yearly salary.

    The line has to be about pay: "120 miles at 60 miles an hour" is travel, not a wage.
    Hours default to 40 a week because that is the assumption most people mean, and it is
    said in the reply. Tax is deliberately left out: the answer is the gross figure, and a
    question that asks for take-home is passed on rather than answered with a guess.
    """
    if _NOT_PAY.search(clean):
        return None
    hours_match = _HOURS_WEEK.search(clean)
    hours = float(hours_match.group(1)) if hours_match else 40.0
    if hours <= 0 or hours > 100:
        return None
    rate = _RATE.search(clean)
    annual = _annual_pay(clean)
    # The "a week" in "37 hours a week" says how much they work, not that they want the
    # answer weekly, so it comes out before the asked-for period is read.
    asked = _HOURS_WEEK.sub(" ", clean)
    asks_year = re.search(r"\b(?:a|per|each|/)\s*(?:year|annum)|\bannual(?:ly)?\b", asked)
    asks_month = re.search(r"\b(?:a|per|each|/)\s*month|\bmonthly\b", asked)
    asks_week = re.search(r"\b(?:a|per|each|/)\s*week|\bweekly\b", asked)
    asks_hour = re.search(r"\b(?:an|a|per|each|/)\s*hour|\bhourly\b", asked)
    # A rate with a unit of time is a pay question even when the line never says earn or
    # wage: "12 pounds an hour a year" is the same ask as "I earn 12 an hour".
    if not (_PAY_WORDS.search(clean)
            or (rate and (hours_match or asks_year or asks_month or asks_week))
            or (annual and asks_hour)):
        return None
    if rate and not annual:
        hourly = float(rate.group(1))
        weekly = hourly * hours
        yearly = weekly * 52
        if asks_month and not asks_year:
            return (f"{_money(clean, hourly)} an hour at {_number(hours)} hours a week is "
                    f"about {_money(clean, yearly / 12)} a month before tax.")
        if asks_week and not (asks_year or asks_month):
            return (f"{_money(clean, hourly)} an hour at {_number(hours)} hours a week is "
                    f"{_money(clean, weekly)} a week.")
        if asks_year:
            return (f"{_money(clean, hourly)} an hour at {_number(hours)} hours a week is "
                    f"about {_money(clean, yearly)} a year before tax.")
        # A rate and a pay word are enough to be a wage question: "what do i earn at 12
        # pounds an hour" asks for the same sum as "how much do i earn at 12 an hour".
        if _PAY_WORDS.search(clean):
            return (f"{_money(clean, hourly)} an hour at {_number(hours)} hours a week is "
                    f"{_money(clean, weekly)} a week, about {_money(clean, yearly)} a year "
                    f"before tax.")
        if hours_match:
            return (f"{_money(clean, hourly)} an hour at {_number(hours)} hours a week is "
                    f"{_money(clean, weekly)} a week, about {_money(clean, yearly)} a year "
                    f"before tax.")
        return None
    if annual and (asks_hour or "hourly rate" in clean):
        value = float(annual.group(1).replace(",", ""))
        if annual.group(2):
            value *= 1000
        per_hour = value / (hours * 52)
        return (f"{_money(clean, value)} a year at {_number(hours)} hours a week is about "
                f"{_money(clean, per_hour)} an hour before tax.")
    if "hourly rate" in clean and ("salary" in clean or "annual" in clean) and not _parse(clean):
        return ("Divide your yearly salary by the hours you work in a year. At 40 hours a "
                "week that is 2,080 hours, so £30,000 is about £14.42 an hour.")
    return None


def _travel(clean):
    match = re.search(r"([\d,.]+)\s*(miles?|km|kilometres?|kilometers?)\b.*?"
                      r"(?:at|of)\s*([\d,.]+)\s*(?:miles?|km|kilometres?|kilometers?)?\s*"
                      r"(?:an hour|per hour|/hour|mph|kmh|km/h)", clean)
    if not match:
        return None
    distance = float(match.group(1).replace(",", ""))
    speed = float(match.group(3).replace(",", ""))
    if not speed:
        return None
    hours = distance / speed
    if hours < 1:
        return f"About {_number(hours * 60)} minutes at {_number(speed)} miles an hour."
    return f"About {_number(hours)} hours at {_number(speed)} miles an hour."


# A journey that names its distance and how it is made, but no speed, is the way people actually
# ask this: "how long does it take to walk three miles", "how long to cycle 3 miles", "how far can
# you walk in an hour". Walking pace, cycling pace and running pace are common knowledge, so the
# missing speed comes from the mode word and the line's own distance answers it.
_PACES = (
    (r"\bwalk(?:s|ed|ing)?\b|\bon foot\b|\bby foot\b|\bpedestrian\b", 3.0,
     "at walking pace", "20 minutes a mile", "on foot", "Allow a bit more for hills and a stop.",
     "A brisk one gets a little more, and hills and a bag take it back."),
    (r"\bcycl(?:e|es|ed|ing)\b|\bbikes?\b|\bbicycles?\b|\bpushbike\b|\bby bike\b", 12.0,
     "on a bike", "five minutes a mile", "on a bike",
     "Allow a bit more for hills and a stop.",
     "A good day with the wind behind you gets a little more."),
    (r"\brun(?:s|ning)?\b|\bjog(?:s|ging)?\b", 6.0,
     "at running pace", "10 minutes a mile", "running",
     "Allow a bit more for hills and a stop.",
     "A brisk one gets a little more, and hills take it back."),
    (r"\bdriv(?:e|es|ing)\b|\bby car\b|\bin the car\b|\bcar journey\b", 50.0,
     "in the car", "a bit over a minute a mile", "in the car",
     "Motorway miles are quicker, A roads and a town slower, so treat it as the middle.",
     "Motorway miles get you further, a town and its traffic get you less."),
)


# Any of the way-words in the pace table, for a line that carries only the distance and gets the
# way of doing it from the turn before.
_A_PACE_WORD = re.compile("|".join(pattern for pattern, *_ in _PACES))


_DISTANCE = re.compile(
    r"(?P<num>\d+(?:\.\d+)?|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|half)\s*(?P<unit>miles?|mile|km|kms|kilometres?|kilometers?|metres?|meters?)\b")


_AFTER_HALF = re.compile(r"\bhalf (?:a|an|one)\s*(?:mile|km|kilometre|kilometer)\b")


def _distance_in_miles(match, clean):
    """The distance in the line as miles. "half a mile" and "a mile and a half" are both said."""
    word = match.group("num")
    units = match.group("unit")
    if _AFTER_HALF.search(clean):
        value = 0.5
    elif word == "half":
        value = 0.5
    else:
        value = float(word) if word[0].isdigit() else float(_COUNTS.get(word, 0))
    if re.search(r"\band a half\b", clean):
        value += 0.5
    if units.startswith(("km", "kilomet")):
        return value * 0.621371
    if units.startswith("met"):
        return value / 1609.34
    return value


def _duration(hours):
    """An hour and a bit the way a person says it: 75 minutes, or two hours 15 minutes."""
    minutes = int(round(hours * 60))
    if minutes < 60:
        return f"{minutes} minutes"
    hours_, mins = divmod(minutes, 60)
    if mins <= 2:
        return "an hour" if hours_ == 1 else f"{hours_} hours"
    if mins >= 58:
        hours_ += 1
        return "an hour" if hours_ == 1 else f"{hours_} hours"
    hour_word = "an hour" if hours_ == 1 else f"{hours_} hours"
    return f"{hour_word} {mins} minutes"


# A distance to work said on its own names no way of getting there, and it is the one place where
# the way is not in doubt enough to ask: "its 4 miles each way to the office" is a car or a bike
# for most people, and the two figures side by side are what says which is worth it.
_TO_WORK = re.compile(r"\b(?:to work|to the office|to my office|to the job|commute|commuting|"
                      r"into work|to the workplace)\b")


# A distance stated rather than asked about, in a chat that is already about getting somewhere
# under your own steam: "its about 4 miles each way" after the cycling-to-work answer. The line
# asks nothing on its own, but the minutes are what decide whether the number is a lot, and
# saying them keeps the journey and its length in one place instead of leaving the next line with
# nothing to stand on. Only the shape below counts: a count of miles and at most a few words
# around it, with no verb of its own.
_A_DISTANCE_STATED = re.compile(
    r"^(?:(?:and|but|so|well|ok|okay|its|it'?s|it is|thats|that is|about|roughly|around|"
    r"approximately|maybe|probably|just|only)\s+){0,5}"
    r"(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|half|\d+(?:\.\d+)?)"
    r"(?:\s+and a half)?\s*(?:miles?|km|kms|kilometres?|kilometers?)\b[^.?!]{0,26}$")


# "is that too far" straight after a distance said out loud asks for the verdict on it, and the
# number it is about is in the turn before: the minutes are the whole answer, so they are said
# again with the verdict on them.
_IS_THAT_TOO_MUCH = re.compile(
    r"\bis (?:that|this|it) (?:too far|too much|too long|a lot|alright|ok|okay|doable)\b|"
    r"\b(?:is|would) that be (?:too far|too much|a lot)\b")


def _the_size_of_the_trip(minutes_there_and_back):
    """What a friend says about a trip of that length - the verdict, not the arithmetic."""
    if minutes_there_and_back <= 45:
        return "That is a short trip - easy to do every day."
    if minutes_there_and_back <= 100:
        return "That is a real part of the day, but plenty of people do it."
    return "That is a long way to do every day - fine now and then, hard as a routine."


def _the_way_it_is_done(memory, back=4):
    """What the person said on the last few turns, newest first: the way they mean to travel.

    Only the person's own lines count. The bot's answer names every way it can think of - the
    running plan says "one minute of easy jogging, two minutes of walking" - and a distance said
    after it would be timed at the bot's walking pace rather than the running the person asked
    about. Newest first, because the last way named is the one the chat is on.
    """
    said = []
    for turn in reversed(((memory or {}).get("turns") or [])[-back:]):
        if isinstance(turn, dict):
            said.append(str(turn.get("user") or ""))
    return said


def _at_a_pace(clean, memory=None, a_verdict=False):
    """How long a walk, a ride or a run takes when the line gives the distance, not the speed."""
    asked_time = re.search(r"\bhow long\b|\bhow many (?:minutes|hours)\b|\bhow much longer\b",
                           clean)
    asked_far = re.search(r"\bhow far\b", clean)
    # A distance said on its own, in a chat already about a way of getting there: the way is in
    # this line ("4 miles each way on the bike") or in the turn before it (the ride to work).
    stated = bool(_A_DISTANCE_STATED.match(clean)) and bool(
        re.search(_A_PACE_WORD, clean + " " + " ".join(_the_way_it_is_done(memory)))
        or _TO_WORK.search(clean))
    if not (asked_time or asked_far or stated):
        # "is that too far" about a distance said last turn: the number is the answer, so it is
        # read back out of the chat and the verdict is put on it.
        if _IS_THAT_TOO_MUCH.search(clean):
            said_before = _the_way_it_is_done(memory)
            for line in said_before:
                if _A_DISTANCE_STATED.match(line.strip()):
                    # the way of getting there came from the chat, so it is read from there too
                    return _at_a_pace(line.strip(), memory, a_verdict=True)
        return None
    pace = None
    for pattern, speed, said, per_mile, far_said, tail, far_tail in _PACES:
        if re.search(pattern, clean):
            pace = (speed, said, per_mile, far_said, tail, far_tail)
            break
    if not pace and stated and _TO_WORK.search(clean):
        # the trip to work, with no way of getting there named: the two ways most people take it
        match = _DISTANCE.search(clean)
        miles = _distance_in_miles(match, clean) if match else 0
        if miles and miles > 0:
            each_way = bool(re.search(r"\beach way\b|\bboth ways\b", clean))
            car = miles / 50.0 * 60
            bike = miles / 12.0 * 60
            if each_way:
                return (f"About {_duration(car / 60)} in the car and {_duration(bike / 60)} on a "
                        f"bike, each way - so around {_duration(2 * car / 60)} to "
                        f"{_duration(2 * bike / 60)} there and back. "
                        + (_the_size_of_the_trip(2 * car) if a_verdict
                           else "A ride that short is well within reach, and it is the cheaper "
                                "of the two."))
            return (f"About {_duration(car / 60)} in the car and {_duration(bike / 60)} on a bike "
                    f"- the ride is the one that saves the money at that distance.")
    if not pace and stated:
        # the way of getting there is in what was said before, newest turn first
        for line in _the_way_it_is_done(memory):
            for pattern, speed, said, per_mile, far_said, tail, far_tail in _PACES:
                if re.search(pattern, line):
                    pace = (speed, said, per_mile, far_said, tail, far_tail)
                    break
            if pace:
                break
    if not pace:
        return None
    speed, said, per_mile, far_said, tail, far_tail = pace
    match = _DISTANCE.search(clean)
    if match:
        miles = _distance_in_miles(match, clean)
        if not miles or miles <= 0:
            return None
        minutes = miles / speed * 60
        if asked_far and not asked_time:
            return None
        if stated:
            # "its about 4 miles each way" is half of a day's travel each way, so the round trip
            # is the figure that decides whether the number is a lot - and it is what the person
            # is telling the bot they have taken on.
            if re.search(r"\beach way\b|\bboth ways\b", clean):
                tail_said = (" " + _the_size_of_the_trip(2 * minutes) if a_verdict else "")
                return (f"About {_duration(minutes / 60)} {said}, so roughly "
                        f"{_duration(2 * minutes / 60)} there and back - {speed:g} miles an hour, "
                        f"so {per_mile}.{tail_said}")
            return (f"About {_duration(minutes / 60)} {said} - {speed:g} miles an hour, so "
                    f"{per_mile}. {tail}")
        return (f"About {_duration(miles / speed)} {said} - {speed:g} miles an hour, so "
                f"{per_mile}. {tail}")
    # "how far can you walk in an hour" is the same pace asked the other way round: the hour is
    # the distance, so the answer is the miles that fit in it.
    hour = re.search(r"\b(?:in|within|for)\s+(?:an?|one|1)\s+hour\b|\ban hour\b", clean)
    if hour and asked_far:
        return (f"About {speed:g} miles in an hour {far_said} - {per_mile}. {far_tail}")
    return None


# A line like "how long will that take?" carries no numbers of its own: the numbers were in
# earlier turns ("hoping to spend about 5000", "i can put away 250 a month"). Those two add up to
# a real answer, so this reads the chat the way a friend would.
TIME_ASKED = re.compile(
    r"\bhow long\b|\bhow many (?:months|weeks|years|fortnights)\b|\bhow soon\b|"
    r"\bwhen (?:will|would|should|do|can|am) (?:i|we)\b|\bwhen do i\b")


# The times of day, cooking and travel are answered from entries or from the line's own numbers.
# "what if we do 700?" right after the bot said how long it takes: the question is implied.
# "what about 300 a week?" and "how about 400?" ask the same thing, as long as the line is about
# money and not about a time of day ("how about 2 o'clock").
WHAT_IF = re.compile(r"\bwhat if (?:i|we)\b|\band if (?:i|we)\b")


ABOUT_ASK = re.compile(r"\b(?:what|how) about\b")


CLOCK = re.compile(r"\bo'?\s?clock\b|\b\d{1,2}\s*(?:am|pm)\b|"
                   r"\b(?:morning|afternoon|evening|tonight|tuesday|wednesday|thursday|friday|"
                   r"saturday|sunday|monday)\b")


# The bot's own sentence, hedge included: a count that is not whole comes back as
# "takes about 12 months", and the turn after that still has to be able to read it.
TAKES = re.compile(r"takes (?:about |roughly |around )?(?P<amount>[\d,.]+) "
                   r"(?P<period>days?|weeks?|fortnights?|months?|years?)\b")


# A number with a period after it and no "a" or "per" between them is a deadline the person
# named ("in 18 months", "in two years"), not a rate: "18 months" is not "18 a month".
A_HORIZON = re.compile(r"\b(?:in|within|by|after)\s+(?:\d+|an?|[a-z-]+)\s+"
                       r"(?:days?|weeks?|fortnights?|months?|years?)\b|"
                       r"\b\d+\s*(?:months?|years?|weeks?)\s+(?:from now|time)\b")


TIME_ELSEWHERE = re.compile(
    r"\b(?:cook|roast|boil|bake|fry|grill|simmer|rest|leave|marinate|drive|walk|fly|cycle|"
    r"ride|run|swim|wait|queue|charge|download|install)\b")


# A figure with a period on it. The saving verb often sits between the two words - "i put 20 by
# every week", "i put 50 aside each month", "putting 100 away a week" - and the phrase
# "20 by every week" matched nothing, so the whole chat below (how long until i can buy it) had
# no rate to work with and punted.
RATE = re.compile(r"(?P<amount>\d[\d,]*(?:\.\d+)?)\s*"
                  r"(?:pounds?|quid|euros?|dollars?|grand|k\b)?\s*"
                  r"(?:(?:by|aside|away|back|to (?:one|the) side)\s+)?"
                  r"(?:a|an|per|each|every|/)\s*(?P<period>day|week|fortnight|month|year)\b")


MONEY = re.compile(r"\b(?:save|saves|saving|saved|spend|spends|spending|cost|costs|afford|"
                   r"budget|need|needs|want|wants|goal|target|total|price|deposit|pay|paying|"
                   r"put away|putting away|put by|putting by|earn|earning|owe|owing)\b")


# The money has to be going towards the thing, not just leaving the account every month: rent and
# bills are not savings, so "my rent is 800 a month" never becomes the rate for a car fund.
TOWARDS = re.compile(r"\b(?:save|saves|saving|saved|put away|putting away|put by|putting by|"
                     r"set aside|setting aside|towards|toward|pay off|paying off|paid off|"
                     r"pay towards|paying towards|pay down|paying down|pay back|paying back|"
                     r"afford|spare|extra|repay|repaying|return)\b")


# ...and the direction has to be in the same clause as the rate itself. "i spend 100 a month on
# coffee" and "i pay 800 a month rent" both have a monthly figure and a saving word later in the
# line, and neither of them is money being put by.
CLAUSE_SPLIT = re.compile(r"[,;.]|\band\b|\bbut\b|\bthen\b|\bso\b")


SAVING_CLAUSE = re.compile(
    r"\b(?:save|saves|saving|saved|savings|put|puts|putting|put away|putting away|put by|"
    r"putting aside|set aside|setting aside|stash|stashing|squirrel|towards|toward|into|"
    r"pay off|paying off|paid off|pay towards|paying towards|paid towards|pay down|paying down|"
    r"pay back|paying back|paid back|overpay|overpaying|give|gives|giving|gave|send|sends|"
    r"sending|transfer|transfers|transferred|repay|repays|repaying|return|returning)\b")


SPENDING_CLAUSE = re.compile(
    r"\b(?:spend|spends|spending|spent|cost|costs|costing|rent|bills?|charges?|wage|wages|"
    r"salary|earn|earns|earning|lose|losing|lost|burn|burns|burning|waste|wasting)\b")


# Money the person is carrying, not money they are putting by: "theres 4000 left on a loan", "i
# owe 3000 on the card", "my overdraft is 1200". A saving chat often holds both figures - what they
# are saving towards and what they already owe - and the debt is usually the bigger of the two, so
# read as a pot it answered "how long will that take" with the loan paid off at the saving rate
# (4,000 at 150 a month is 27 months) and never reached the car they had just priced.
OWED = re.compile(r"\b(?:owe|owes|owed|owing|debt|debts|loan|loans|overdraft|mortgage|"
                  r"finance|financed|borrow|borrowed|borrowing|credit\s*card|left\s+on)\b", re.I)


# The same sum said as the thing they are clearing is a goal: "i owe 3000 on the card and want it
# gone", "how long to pay off 3000". Reads the money going the other way.
A_DEBT_CLEARED = re.compile(r"\b(?:pay(?:ing)?\s+(?:it\s+|them\s+)?off|clear(?:ing)?|"
                            r"repay(?:ing)?|gone|off|rid)\b", re.I)


def _rate_clause(line, match):
    """The part of the line the rate sits in, so its direction can be read on its own."""
    start = 0
    for part in CLAUSE_SPLIT.split(line):
        end = start + len(part)
        if start <= match.start() and match.end() <= end + 1:
            return part
        start = end + 1
    return line


# how many months one of each period is, for the "about a year and eight months" aside
PERIODS = {"day": 1 / 30.44, "week": 1 / 4.345, "fortnight": 1 / 2.17, "month": 1, "year": 12}


def _user_lines(memory, back=8):
    """What the user said on the last few turns, oldest first."""
    lines = []
    for turn in (memory.get("turns") or [])[-back:]:
        if not isinstance(turn, dict):
            continue
        text = turn.get("user")
        if isinstance(text, str) and text.strip():
            lines.append(" ".join(text.lower().split()))
    return lines


def _a_rate_was_said(lines):
    """True when one of these lines puts money by at a rate ("put away 250 a month")."""
    for line in lines:
        for match in RATE.finditer(line):
            clause = _rate_clause(line, match)
            if SAVING_CLAUSE.search(clause) and not SPENDING_CLAUSE.search(clause):
                return True
    return False


def _rate_in_chat(memory):
    """The most recent rate per period in the chat, when the money is going towards something.

    A rate put right counts as the most recent one. "i can put away 250 a month" and then
    "actually i can do 300 now ive paid the car off" is one rate written twice, and the second
    line has no "a month" on it because the month never changed - so it matched nothing here, and
    the length of the saving was worked out at the rate the person had already left behind.
    """
    lines = _user_lines(memory)
    for index in range(len(lines) - 1, -1, -1):
        line = lines[index]
        put_right = a_rate_put_right(line, lines[index - 1] if index else "")
        if put_right and _a_rate_was_said(lines[:index]):
            return float(put_right), "month"
        for match in RATE.finditer(line):
            clause = _rate_clause(line, match)
            if not SAVING_CLAUSE.search(clause) or SPENDING_CLAUSE.search(clause):
                continue
            amount = float(match.group("amount").replace(",", ""))
            if amount > 0:
                return amount, match.group("period")
    return None, None


# A figure with a period on it is a rate, not a pot: "i want to save 200 a month" names no goal at
# all. Read as one it became the total behind the next question - "what would that get me in a
# year" answered "200 in a year is 17 a month", which is the rate divided out as if it were a sum
# to be reached. The rate is taken out before the figures of the line are read, so a line that
# names both keeps its goal: "i want to save 200 a month towards 3000" still has the 3000.
SAID_A_RATE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:k|grand|thousand)?\s*(?:pounds?\s+)?"
                         r"(?:a|per|each|every|/)\s*(?:month|week|fortnight|year|day)\b", re.I)


# A reply that divided a total by a rate and said how long it takes: "£20,000 at £200 a month is
# 100 months, about 8 years and 4 months". The total and the rate are both in it.
# The count is part of the division and not just the verb: a reply that says what a rate comes to
# in a month ("£1,400 at £1,800 a month is a single month at that rate") did no division at all,
# and reading its figure as the total made a spend into a goal - "how much could i put away each
# month" answered "£1,400 by next summer ... about £184 a month". So a figure has to follow the
# verb that says the sum is worked.
WORKED = re.compile(
    r"£([\d,]+)\s+at\s+£?[\d,.]+\s*(?:a|per|each)\s+(?:month|week|fortnight|year)s?\s+"
    r"(?:is|takes|gives|comes to)\s+(?:about\s+|around\s+|roughly\s+)?\d"
    r"|\bat\s+£?[\d,.]+\s*(?:a|per|each)\s+(?:month|week|fortnight|year)s?\s*,\s*"
    r"(?:about\s+)?£?([\d,]+)\s+takes\s+(?:about\s+|around\s+|roughly\s+)?\d",
    re.IGNORECASE)


def _worked_in_chat(memory, rate=None):
    """The total this chat has already worked a time for, read from the bot's own answer.

    "we can put away 400 a month" is answered "£20,000 at £400 a month is 50 months", so the
    "how long would that take" that follows is a question about the 20,000 the chat itself
    divided - and a total named beside a rate is the plan's own figure, not an example or an
    aim. Only a reply that did the division counts: the one before it says what to aim for and
    no rate, so its figure is never taken as the plan.
    """
    total = None
    for turn in (memory.get("turns") or [])[-8:]:
        if not isinstance(turn, dict):
            continue
        text = turn.get("bot")
        if not isinstance(text, str):
            continue
        for found in WORKED.findall(" ".join(text.split())):
            raw = next((part for part in found if part), "")
            try:
                value = int(raw.replace(",", ""))
            except ValueError:
                continue
            if rate and value < rate * 2:
                continue
            if value >= 50:
                total = value
    return total


# A sum said the way people say sums: "20 grand", "twenty thousand", "20k". `_parse` reads the
# digits of a line and nothing else, so "i need 20 grand" came back as twenty pounds - under the
# fifty a goal has to clear - and the chat that had both the target and the rate was asked for the
# target again: "i need 20 grand" / "im putting away 400 a month" / "how long will that take me"
# was answered "At 400 a month that's about 4,800 a year. Tell me the figure you are saving
# towards", one turn after the same entry had worked with the £20,000 it can no longer see.
# Only the words that are always money scale the figure: a bare "5k" is a run, so a k needs a
# money word on the same line before it counts as thousands.
_TENS_WORDS = {"ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
               "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
               "eighty": 80, "ninety": 90}


_WORD_THOUSANDS = re.compile(r"\b(" + "|".join(_TENS_WORDS) + r")\s+(?:grand|thousand)\b", re.I)


_NUMBER_THOUSANDS = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:grand|thousand)\b", re.I)


_K_THOUSANDS_HERE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*k\b", re.I)


_MONEY_HERE = re.compile(r"£|\bpounds?\b|\bquid\b|\beuros?\b|\bdollars?\b|\bsav(?:e|ing|ings)\b|"
                         r"\bcost(?:s|ing)?\b|\bpay(?:ing|s|day)?\b|\bmoney\b|\bbudget\b|"
                         r"\bprice\b|\bafford\b|\bdeposit\b|\bspen[dt]\b|\bowe[sd]?\b", re.I)


def _sums(text):
    """The sums in a line, with a scale word read as thousands: "20 grand" is 20,000."""
    text = str(text or "")
    text = _WORD_THOUSANDS.sub(lambda m: str(_TENS_WORDS[m.group(1).lower()] * 1000), text)
    text = _NUMBER_THOUSANDS.sub(lambda m: str(int(float(m.group(1)) * 1000)), text)
    if _MONEY_HERE.search(text):
        text = _K_THOUSANDS_HERE.sub(lambda m: str(int(float(m.group(1)) * 1000)), text)
    return _parse(text)


def _in_months(count, period):
    """A count of one period said in months, for the parenthesis in the reply."""
    return count * PERIODS[period]


def _duration_reply(rate, period, total):
    """The sentence for "X a month for Y": the count, and how long that is in years."""
    count = total / rate
    if count < 1 or count > 1200:
        return None  # not a sum anyone asks about, or not a rate at all
    # A part payment is another payment, which is the rule the rate card itself follows ("£900
    # at £200 a month is 5 months" - saving.py works the count out with a ceiling), so a half is
    # never rounded down here: the same chat said "5 months" and then, on the next line, "about 4
    # months" for the same rate and the same goal.
    nearest = int(count + 0.5)
    if abs(count - nearest) < 0.05:
        said_count, about = _number(nearest), ""
    else:
        said_count, about = _number(round(count, 1) if count < 3 else nearest), "about "
    name = period if count == 1 else period + "s"
    reply = f"At {_number(rate)} a {period}, {_number(total)} takes {about}{said_count} {name}"
    months = _in_months(count, period)
    if period != "year" and months >= 12:
        years, rest = divmod(int(round(months)), 12)
        said = f"{years} year" + ("" if years == 1 else "s")
        if rest:
            said += f" and {rest} month" + ("" if rest == 1 else "s")
        # the aside gets "about" only when it is not the exact count itself
        loose = "about " if about or abs(months - round(months)) >= 0.05 else ""
        reply += f" ({loose}{said})"
    return reply + "."


def _asks_a_new_sum(clean):
    """A line that proposes its own numbers for the sum the chat already holds."""
    if WHAT_IF.search(clean):
        return True
    return bool(ABOUT_ASK.search(clean)) and not CLOCK.search(clean)


def _last_takes(memory):
    """The rate and period the bot worked out on the turn before, when it worked one out."""
    turns = memory.get("turns") or []
    if not turns or not isinstance(turns[-1], dict):
        return None
    found = TAKES.search(turns[-1].get("bot") or "")
    if not found:
        return None
    return float(found.group("amount").replace(",", "")), found.group("period").rstrip("s")


# The next unit down and how many of it make one of the larger: a hundred of the price at 300 a
# month is a third of a month, which nobody says, and "eight days" is the same figure said plainly.
_SMALLER_PERIOD = {"year": ("month", 12), "month": ("week", 4.345), "fortnight": ("week", 2),
                   "week": ("day", 7), "day": ("hour", 24)}


def _each_hundred(rate, period):
    """How long 100 of the price takes at a rate: "five weeks", "eight days", "2.5 months".

    The figure that makes an empty sum useful without inventing a price: it is the rate read the
    other way round, and a price can then be done in the head in steps of one hundred. The unit
    follows the count down, so a rate of 300 a month answers in days rather than in "a third of a
    month", and the count is rounded to the half that a person would say.
    """
    if not rate or rate <= 0:
        return None
    count = 100.0 / rate
    while count < 1 and period in _SMALLER_PERIOD:
        period, many = _SMALLER_PERIOD[period]
        count *= many
    if count < 1:
        return None  # 100 of the price in under an hour is not a rate anyone is saving at
    while count >= 13 and period in ("day", "week", "fortnight"):
        period, many = _SMALLER_PERIOD[period]
        count /= many
    if period == "hour" and count >= 12:
        return None  # the yearly figure above says this better than hours do
    if count < 3:
        value = round(count * 2) / 2
        said = _number(int(value) if value == int(value) else value)
    else:
        value = round(count)
        said = _number(int(value))
        if abs(count - value) >= 0.5:
            said = f"about {said}"
    name = period if abs(value - 1) < 0.05 else period + "s"
    return f"{said} {name}"
