"""Part 1 of 6 of a large module, split out of `maths`.

Everything here is re-exported from `maths`, so callers import it from there as before.
"""
import ast
import operator
import re
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction




ANSWERS = ("maths-and-numbers",)


MONTHS = {
    "january": 31, "february": 28, "march": 31, "april": 30, "may": 31, "june": 30,
    "july": 31, "august": 31, "september": 30, "october": 31, "november": 30, "december": 31,
}


_NUMBER = r"-?\d+(?:[.,]\d+)?"


def _number(value):
    """A number the way a person writes it: 12, 2.5, 1,081."""
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    # the extra place only when it makes the number exact: 3 divided by 8 is 0.375, not 0.38,
    # while a third stays 0.33 because no short decimal will ever be right.
    shown = f"{value:.2f}"
    for places in (2, 3, 4):
        if abs(float(f"{value:.{places}f}") - value) < 1e-9:
            shown = f"{value:.{places}f}"
            break
    return shown.rstrip("0").rstrip(".")


def _parse(text):
    """The numbers in a line, in order."""
    found = []
    for raw in re.findall(r"\d+(?:\.\d+)?", text.replace(",", "")):
        try:
            found.append(float(raw))
        except ValueError:
            continue
    return found


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 64:
            raise ValueError("exponent too large")
        return _BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    raise ValueError("not arithmetic")


def _expression(clean):
    """The arithmetic expression in a line, or None. Only digits and operators survive."""
    text = clean
    text = re.sub(r"\b(?:what's|whats|what is|calculate|work out|how much is|how much does|"
                  r"please|tell me|the answer to)\b", " ", text)
    # "how do i divide 3 by 8" is the same sum as "3 divided by 8": the asking words carry no
    # number and no operator, so they go before the operator words are read.
    text = re.sub(r"\b(?:how do i|how do you|how can i|how would i|how to|can you|could you|"
                  r"whats the answer to|what is the answer to)\b", " ", text)
    text = text.replace(",", "")
    text = re.sub(r"\bmultiplied by\b|\btimes\b|\bx\b", "*", text)
    # "divide 3 by 8" is a sum with its instruction in front: the numbers say which way round.
    text = re.sub(r"\bdivide\b\s+(\d[\d.]*)\s+by\s+(\d[\d.]*)", r"\1/\2", text)
    text = re.sub(r"\bdivided by\b|\bover\b", "/", text)
    text = re.sub(r"\bplus\b|\band\b", "+", text)
    text = re.sub(r"\bminus\b|\btake away\b|\bsubtract\b", "-", text)
    text = re.sub(r"\bsquared\b", "**2", text)
    text = re.sub(r"\bcubed\b", "**3", text)
    text = re.sub(
        r"\b(?:to the power of|to the power|raised to the power of|raised to the|raised to)\b",
        "**", text)
    text = text.replace("^", "**")
    text = text.replace("?", " ").strip()
    if not re.fullmatch(r"[0-9+\-*/().\s]+", text or ""):
        return None
    if not re.search(r"\d", text) or not re.search(r"[+\-*/]", text):
        return None
    if len(text) > 80:
        return None
    return text


def _calc(clean):
    expression = _expression(clean)
    if expression is None:
        return None
    try:
        value = _eval(ast.parse(expression, mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
        return None
    if not isinstance(value, (int, float)) or value != value or abs(value) == float("inf"):
        return None
    return f"That's {_number(value)}."


def _root(clean):
    """A square root: "what's the square root of 144", "sqrt 81"."""
    if "cube root" in clean or "fourth root" in clean:
        return None
    match = re.search(r"(?:square root(?: of)?|sqrt|root(?: of)?)\s*([\d,.]+)", clean)
    if not match:
        return None
    value = float(match.group(1).replace(",", ""))
    if value < 0:
        return "A negative number has no real square root."
    root = value ** 0.5
    if abs(root - round(root)) < 1e-9:
        return f"The square root of {_number(value)} is {_number(root)}."
    return f"The square root of {_number(value)} is about {_number(root)}."


def _roots(clean):
    """A root asked for in words: "the square root of 144", "cube root of 27"."""
    match = re.search(r"(square root|cube root)\s*(?:of|is)?\s*(-?[\d,.]+)", clean)
    if not match:
        return None
    value = float(match.group(2).replace(",", ""))
    if match.group(1) == "cube root":
        root = (-1 if value < 0 else 1) * abs(value) ** (1 / 3)
        exact = round(root) ** 3 == value
        name = "cube root"
    else:
        if value < 0:
            return None
        root = value ** 0.5
        exact = round(root) ** 2 == value
        name = "square root"
    if exact:
        return f"The {name} of {_number(value)} is {_number(round(root))}."
    return f"The {name} of {_number(value)} is about {_number(round(root, 4))}."


def _prime(clean):
    """"Is 91 a prime number?": a yes or no answer with the reason, since 91 looks prime."""
    match = re.search(r"is\s+(\d+)\s+(?:a\s+)?prime", clean)
    if not match:
        return None
    number = int(match.group(1))
    if number < 2:
        return f"{number} is not prime: primes start at 2."
    divisor = next((d for d in range(2, int(number ** 0.5) + 1) if number % d == 0), None)
    if divisor:
        return f"No: {number} is {divisor} × {number // divisor}, so it is not prime."
    return f"Yes: nothing but 1 and {number} divides {number}, so it is prime."


_FRACTIONS = {
    "half": (1, 2), "halves": (1, 2), "third": (1, 3), "thirds": (1, 3),
    "quarter": (1, 4), "quarters": (1, 4), "fifth": (1, 5), "fifths": (1, 5),
    "sixth": (1, 6), "sixths": (1, 6), "eighth": (1, 8), "eighths": (1, 8),
    "tenth": (1, 10), "tenths": (1, 10),
}


_COUNTS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


# A fraction of a fraction is the question that catches more people than any other in a kitchen:
# "half of 3/4 cup". The plain fraction-of-a-number reader below took the "3" of "3/4" and said
# "half of 3 is 1.5", which is a confident answer to a question nobody asked. These helpers read
# the fraction as a fraction and keep the unit the person used.
_COUNT = r"(a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)"


_PART = (r"(half|halves|third|thirds|quarter|quarters|fifth|fifths|sixth|sixths|eighth|eighths|"
         r"tenth|tenths|\d+\s*/\s*\d+)")


_AMOUNT = r"(\d+(?:\s+\d+)?\s*/\s*\d+|\d+(?:\.\d+)?)"


_FRACTION_UNITS = (r"(cups?|tbsp|tablespoons?|tsp|teaspoons?|grams?|g|kg|ml|litres?|liters?|"
                   r"ounces?|oz|pounds?|pints?|sticks?)")


_SINGULAR = {
    "cups": "cup", "tablespoons": "tablespoon", "teaspoons": "teaspoon", "grams": "gram",
    "litres": "litre", "liters": "liter", "ounces": "ounce", "pounds": "pound", "pints": "pint",
    "sticks": "stick",
}


_CUP_IN_TBSP = 16


_CUP_IN_ML = 240


# "half of 3/4 cup", "three quarters of 200 grams", "2/3 of 3/4 cup", "half of 3/4 of a cup",
# "half of 1/2 a teaspoon", "half of 1.5 cups". The count ("three quarters"), the "of a" and the
# "a" are all how people say it.
_FRACTION_OF_FRACTION = re.compile(
    r"\b(?:(?:" + _COUNT + r")\s+)?" + _PART + r"\s+of\s+(?:a\s+|an\s+)?" + _AMOUNT +
    r"(?:\s+of)?\s+(?:a\s+|an\s+)?" + _FRACTION_UNITS + r"\b")


# The same question with no unit at all: "2/3 of 3/8" used to read the 3 of the 3/8 and answer
# "2/3 of 3 is 2". Only a fraction amount matches here, so "2/3 of 60" keeps its own row.
_FRACTION_OF_A_FRACTION = re.compile(
    r"\b(?:(?:" + _COUNT + r")\s+)?" + _PART + r"\s+of\s+\d+\s*/\s*\d+\b")


def _as_fraction(text):
    """'3/4', '1 1/2' or '1.5' as a Fraction, or None."""
    text = " ".join(str(text).split())
    whole, _, part = text.rpartition(" ")
    if "/" in part:
        top, _, bottom = part.partition("/")
        try:
            value = Fraction(int(top), int(bottom))
        except (ValueError, ZeroDivisionError):
            return None
        if whole.strip():
            try:
                value += int(whole)
            except ValueError:
                return None
        return value
    try:
        return Fraction(part)
    except (ValueError, ZeroDivisionError):
        return None


def _fraction_text(value):
    """A Fraction the way a recipe reads it: 3/8, 1 1/2, 2."""
    value = Fraction(value).limit_denominator(64)
    if value.denominator == 1:
        return str(value.numerator)
    whole, rest = divmod(value.numerator, value.denominator)
    if whole:
        return "%d %d/%d" % (whole, rest, value.denominator)
    return "%d/%d" % (rest, value.denominator)


def _fraction_of_a_fraction(clean):
    """A part of a fraction, or of a mixed number: "half of 3/4 cup", "2/3 of 3/8"."""
    match = _FRACTION_OF_FRACTION.search(clean)
    bare = not match
    if bare:
        match = _FRACTION_OF_A_FRACTION.search(clean)
    if not match:
        return None
    count_word, part_word = match.group(1), match.group(2)
    part = (Fraction(*_FRACTIONS[part_word]) if part_word in _FRACTIONS
            else _as_fraction(part_word))
    if not part:
        return None
    if count_word:
        count = int(count_word) if count_word.isdigit() else _COUNTS.get(count_word, 1)
        part = part * count
    amount_text = match.group(3) if not bare else match.group(0).split(" of ")[-1]
    amount = _as_fraction(amount_text)
    if amount is None:
        return None
    value = part * amount
    unit = "" if bare else match.group(4)
    # a quantity of one or less is singular whatever the person typed: half of 1 1/2 cups is
    # 3/4 cup, not 3/4 cups
    if value <= 1:
        unit = _SINGULAR.get(unit, unit)
    said = " ".join(word for word in (count_word, part_word) if word)
    said = said[0].upper() + said[1:]
    said_amount = _fraction_text(amount) + ((" " + match.group(4)) if not bare else "")
    answer = "%s of %s is %s%s" % (said, said_amount, _fraction_text(value),
                                   (" " + unit) if unit else "")
    if unit.startswith("cup"):
        spoons = value * _CUP_IN_TBSP
        millilitres = value * _CUP_IN_ML
        # a third of a third of a cup is not a spoon anybody measures, so the spoons are rounded
        spoon_text = (_fraction_text(spoons) if spoons.denominator == 1
                      else "about %d" % round(float(spoons)))
        answer += ", which is %s tablespoons (%d ml)" % (spoon_text, round(millilitres))
    if bare or "/" in amount_text:
        # the rule only makes sense when the amount is a fraction of something
        if part == Fraction(1, 2):
            answer += ": halve the top number and keep the bottom one."
        else:
            answer += ": multiply the tops and the bottoms."
    else:
        answer += "."
    return answer


def _fraction_of(clean):
    """A simple fraction of an amount: "half of 96", "three quarters of 200", "2/5 of 60"."""
    kitchen = _fraction_of_a_fraction(clean)
    if kitchen:
        return kitchen
    match = re.search(r"\b(\d+)\s*/\s*(\d+)\s+of\s+([\d,.]+)", clean)
    if match:
        top, bottom = float(match.group(1)), float(match.group(2))
        amount = float(match.group(3).replace(",", ""))
        label = f"{_number(top)}/{_number(bottom)}"
    else:
        match = re.search(r"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                          r"\d+)?\s*"
                          r"(half|halves|third|thirds|quarter|quarters|fifth|fifths|sixth|sixths|"
                          r"eighth|eighths|tenth|tenths)\s+of\s+([\d,.]+)", clean)
        if not match:
            return None
        said = match.group(1) or "a"
        count = int(said) if said.isdigit() else _COUNTS.get(said, 1)
        if said.isdigit():
            said = next((word for word, number in _COUNTS.items() if number == count), said)
        part, whole = _FRACTIONS[match.group(2)]
        top, bottom = part * count, whole
        amount = float(match.group(3).replace(",", ""))
        label = " ".join(word for word in match.group(1, 2) if word)
        if said.isdigit() or (match.group(1) or "").isdigit():
            label = f"{said} {match.group(2)}"  # "3 quarters" is said "three quarters"
    if not bottom or not top:
        return None
    value = amount * top / bottom
    # Keep the unit the person used: "three quarters of 60 grams" is 45 grams, not 45.
    unit = re.match(r"\s*(?:g|grams?|kg|kilograms?|ml|litres?|liters?|pounds?|oz|ounces?|"
                    r"minutes?|hours?|miles?|km|metres?|meters?)\b", clean[match.end():])
    said = f" {unit.group(0).strip()}" if unit else ""
    return (f"{label[0].upper() + label[1:]} of {_number(amount)}{said} is "
            f"{_number(round(value, 4))}{said}.")


def _share_reply(total, people, clean):
    if people < 2:
        return None
    money = next((sign for sign in ("£", "$", "€") if sign in clean), "")
    share = total / people
    return (f"That's {money}{_number(round(share, 2))} each: {money}{_number(total)} split "
            f"{people} ways.")


# A count of people as people write it: "between the three of us" is the same question as
# "between 3 of us", and the split row answered only the second one.
_A_COUNT = r"(?:\d+|two|three|four|five|six|seven|eight|nine|ten)"


_COUNT_VALUE = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10}


def _count_value(text):
    text = str(text or "").strip().lower()
    return int(text) if text.isdigit() else _COUNT_VALUE.get(text)


def _share(clean):
    """"Split 84 pounds between 6 people": a sum divided among a number of people.

    The ways round people say it differ only in where the count is ("between 6 people",
    "4 ways", "5 of us"), so the sum and the count are found separately rather than with
    one pattern per phrasing.
    """
    match = re.search(r"[£$€]?\s*([\d,.]+)\s*(?:pounds?|quid|euros?|dollars?)?\s*"
                      r"(?:split|shared|divided|share)\s+(?:it\s+)?(?:equally\s+)?"
                      r"(?:between|among|across)\s+(?:the\s+)?(" + _A_COUNT + r")\b", clean)
    if not match:
        match = re.search(r"(?:split|share|divide)\s+(?:the bill of\s+|the\s+|it\s+)?[£$€]?\s*"
                          r"([\d,.]+)\s*"
                          r"(?:pounds?|quid|euros?|dollars?)?\s*(?:equally\s+)?"
                          r"(?:between|among|across)\s+(\d+)", clean)
    if not match:
        # "96 between the three of us": no split verb at all, just the sum and who paid it.
        # Nothing else in this family puts the count straight after "between", so the shape
        # is narrow on purpose - "the difference between 84 and 96" is another row's.
        between = re.search(r"[£$€]?\s*([\d,.]+)\s*(?:pounds?|quid|euros?|dollars?|bucks?)?\s+"
                            r"between\s+(?:the\s+)?(" + _A_COUNT + r")\s+"
                            r"(?:of\s+us|of\s+them|people|friends|adults|ways)\b", clean)
        if between:
            total = float(between.group(1).replace(",", ""))
            people = _count_value(between.group(2))
            if people and people >= 2:
                return _share_reply(total, people, clean)
    if not match:
        # "we split the bill 4 ways on 86 pounds": the verb and the count, then the sum.
        if not re.search(r"\b(?:split|splitting|share|sharing|divide|dividing)\b", clean):
            return None
        ways = re.search(r"(" + _A_COUNT + r")\s*(?:ways?|people|of us|friends|adults)", clean)
        if not ways:
            return None
        money_word = re.search(r"([\d,.]+)\s*(?:pounds?|quid|euros?|dollars?|bucks?)", clean)
        if money_word:
            total_text = money_word.group(1)
        else:
            sign_sum = re.search(r"[£$€]\s*([\d,.]+)", clean)
            if sign_sum:
                total_text = sign_sum.group(1)
            else:
                left = [n for n in re.findall(r"\d+(?:\.\d+)?", clean)
                        if n != ways.group(1)]
                if not left:
                    return None
                total_text = max(left, key=float)
        match = None
        total = float(total_text.replace(",", ""))
        people = _count_value(ways.group(1))
        if not people:
            return None
        return _share_reply(total, people, clean)
    total = float(match.group(1).replace(",", ""))
    people = _count_value(match.group(2))
    if not people or people < 2:
        return None
    return _share_reply(total, people, clean)


def _dec(value, places=6):
    """A decimal the way a person writes it: 0.125, 0.75, 12."""
    text = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return text or "0"


def _fraction_decimal(clean):
    """Both directions: "3/4 as a decimal" and "0.25 as a fraction".

    The number in the answer is the one the person wrote, so "0.375 as a fraction" says
    0.375 and not a rounded 0.38, and "1/8 as a decimal" says 0.125 rather than 0.12.

    A share said as "1 in 10" is one part in ten, so it is 10% and not 1000%: the number before
    "in" is the top of the fraction and the one after it is the bottom. Without this the line
    was read as "10 as a percentage" and the answer was wrong by a factor of a hundred. A
    percentage asked as a fraction or a decimal is the same sum the other way round, so
    "25% as a fraction" is 1/4 and "25% as a decimal" is 0.25 rather than a lecture on fractions.
    """
    match = re.search(r"(\d+)\s*in\s*(\d+)\s*(?:as|to|into)\s*(?:a\s+)?"
                      r"(fraction|decimal|percentage|percent)", clean)
    if match:
        top, bottom, kind = int(match.group(1)), int(match.group(2)), match.group(3)
        if not bottom:
            return None
        if kind.startswith("percent"):
            return f"{top} in {bottom} is {_dec(top / bottom * 100, 2)}%."
        if kind == "decimal":
            return f"{top} in {bottom} as a decimal is {_exact_decimal(top, bottom)}."
        part = Fraction(top, bottom).limit_denominator(1000)
        return f"{top} in {bottom} as a fraction is {part.numerator}/{part.denominator}."
    match = re.search(r"([\d,.]+)\s*(%|percent|per cent)\s*(?:as|to|into)\s*(?:a\s+)?"
                      r"(fraction|decimal)", clean)
    if match:
        written = match.group(1).rstrip(".")
        # The person's own sign: "25 percent as a fraction" is answered with "percent" in it.
        sign = "%" if match.group(2) == "%" else " percent"
        value = float(written.replace(",", ""))
        if match.group(3) == "decimal":
            return f"{written}{sign} as a decimal is {_dec(value / 100, 6)}."
        part = Fraction(value / 100).limit_denominator(1000)
        if part.denominator == 1:
            return f"{written}{sign} as a fraction is {part.numerator}."
        return f"{written}{sign} as a fraction is {part.numerator}/{part.denominator}."
    match = re.search(r"(\d+)\s*/\s*(\d+)\s*(?:as|in|to)\s*(?:a\s+)?(decimal|percentage|percent)",
                      clean)
    if match:
        top, bottom = int(match.group(1)), int(match.group(2))
        if not bottom:
            return None
        if match.group(3).startswith("percent"):
            return f"{top}/{bottom} is {_dec(top / bottom * 100, 2)}%."
        return f"{top}/{bottom} as a decimal is {_exact_decimal(top, bottom)}."
    match = re.search(r"([\d,.]+)\s*(?:as|in|to)\s*(?:a\s+)?(fraction|percentage|percent)", clean)
    if not match:
        return None
    if re.match(r"\s+of\s+[\d,.]+", clean[match.end():]):
        return None  # "15 as a percentage of 80" is a share of a whole: _what_percent has it
    written = match.group(1).rstrip(".")
    value = float(written.replace(",", ""))
    if match.group(2) == "fraction":
        part = Fraction(value).limit_denominator(1000)
        if part.denominator == 1:
            return f"{written} is a whole number: {part.numerator}."
        return f"{written} is {part.numerator}/{part.denominator}."
    return f"{written} as a percentage is {_dec(value * 100, 2)}%."


def _exact_decimal(top, bottom):
    """A fraction as a decimal: 3/8 is 0.375, not 0.38, and 1/3 is 0.33 recurring.

    A decimal that stops is written out in full, because "as a decimal" asks for the number
    itself; one that never stops is rounded to two places and marked as recurring, so it does
    not read as exact.
    """
    left = bottom
    for prime in (2, 5):
        while left % prime == 0:
            left //= prime
    if left == 1:
        return f"{top / bottom:.6f}".rstrip("0").rstrip(".")
    # "0.33" on its own reads as exact, so a value that never stops says so.
    return f"{_number(top / bottom)} recurring"


def _fraction(clean):
    """A fraction as a decimal or percentage, or a fraction of a number."""
    match = re.search(r"(-?\d+)\s*/\s*(\d+)", clean)
    if not match:
        # "3 over 8" is the same fraction said out loud
        match = re.search(r"(-?\d+)\s+(?:over|upon)\s+(\d+)", clean)
    if not match:
        return None
    top, bottom = int(match.group(1)), int(match.group(2))
    if bottom == 0:
        return None
    if "decimal" in clean:
        return f"{top}/{bottom} as a decimal is {_exact_decimal(top, bottom)}."
    if "percent" in clean:
        return f"{top}/{bottom} is {_number(top / bottom * 100)}%."
    # not a second fraction: "2/3 of 3/8" is a fraction of a fraction, and the 3 of the 3/8 is
    # not the amount being taken a share of
    of = re.search(r"/\s*\d+\s*of\s*([\d,.]+)(?!\s*/\s*\d)", clean)
    if of:
        total = float(of.group(1).replace(",", ""))
        return f"{top}/{bottom} of {_number(total)} is {_number(top / bottom * total)}."
    return None


# --- school arithmetic that carries its own numbers -----------------------
#
# A pupil writes the sum into the question - "simplify 6 over 8", "add 1/2 and 1/3", "round
# 3.456 to two decimal places", "the circumference of a circle with radius 5" - so a canned
# reply cannot answer it. Each of these reads the numbers off the line and works the answer
# out. The entries below answer the general "how do I do this" question, which has no numbers.
_FRACTION = r"(\d+)\s*(?:/|over|upon)\s*(\d+)"


_PLACES = {"one": 1, "two": 2, "three": 3, "1": 1, "2": 2, "3": 3, "a": 1}


def _reduced(top, bottom):
    """The same fraction with the common factors divided out, and what was divided out."""
    a, b = abs(top), abs(bottom)
    while b:
        a, b = b, a % b
    if not a:
        return top, bottom, 1
    return top // a, bottom // a, a


def _simplify(clean):
    """\"simplify 6 over 8\": the same fraction with no common factor left."""
    match = re.search(r"simplif(?:y|ies|ied)\s+(?:the\s+)?(?:fraction\s+)?" + _FRACTION, clean)
    if not match:
        match = re.search(_FRACTION + r"\s*(?:in|to)\s+(?:its\s+)?(?:simplest form|lowest terms)",
                          clean)
    if not match:
        return None
    top, bottom = int(match.group(1)), int(match.group(2))
    if not bottom or not top:
        return None
    simple_top, simple_bottom, by = _reduced(top, bottom)
    if by == 1:
        return (f"{top}/{bottom} is already as simple as it goes: nothing divides both "
                f"numbers.")
    return (f"{top}/{bottom} simplifies to {simple_top}/{simple_bottom}: divide the top and the "
            f"bottom by {by}.")


def _add_fractions(clean):
    """\"add 1/2 and 1/3\": a common bottom, then the tops."""
    match = re.search(_FRACTION + r"\s*(\+|plus|and|minus|-)\s*" + _FRACTION, clean)
    sentence = r"(?:add|subtract|take away)\s+(?:the fractions\s+)?" + _FRACTION + \
               r"\s+(?:and|from|to)\s+" + _FRACTION
    other = re.search(sentence, clean)
    if match:
        top_a, bottom_a = int(match.group(1)), int(match.group(2))
        sign = "-" if match.group(3) in ("-", "minus") else "+"
        top_b, bottom_b = int(match.group(4)), int(match.group(5))
    elif other:
        top_a, bottom_a = int(other.group(1)), int(other.group(2))
        top_b, bottom_b = int(other.group(3)), int(other.group(4))
        sign = "-" if clean.startswith("subtract") or "take away" in clean else "+"
    else:
        return None
    if not (bottom_a and bottom_b):
        return None
    # The common bottom is the lowest one, not the two multiplied: 1/2 + 1/4 is over 4, the way
    # it is taught, so the gcd of the bottoms is what is divided out of the product.
    _, _, shared = _reduced(bottom_a, bottom_b)
    bottom = bottom_a * bottom_b // (shared or 1)
    left, right = bottom // bottom_a, bottom // bottom_b
    top = top_a * left + (top_b * right if sign == "+" else -top_b * right)
    simple_top, simple_bottom, _ = _reduced(top, bottom)
    way = "add the tops" if sign == "+" else "subtract the tops"
    if bottom_a == bottom_b:
        return (f"{top_a}/{bottom_a} {sign} {top_b}/{bottom_b} = {simple_top}/{simple_bottom}: "
                f"the bottoms are the same, so just {way}.")
    return (f"{top_a}/{bottom_a} {sign} {top_b}/{bottom_b} = {simple_top}/{simple_bottom}. Put both "
            f"over {bottom} ({top_a * left}/{bottom} and {top_b * right}/{bottom}), {way}, "
            f"then cancel down.")


def _factors_in_list(words):
    """The whole-number factors of one number, smallest first."""
    out = []
    step = 1
    while step * step <= words:
        if words % step == 0:
            out.append(step)
            if step != words // step:
                out.append(words // step)
        step += 1
    return sorted(out)


def _said_list(numbers):
    """1, 2, 3 and 6 - the way a list of numbers is written out loud."""
    said = [str(number) for number in numbers]
    if len(said) <= 1:
        return "".join(said)
    return ", ".join(said[:-1]) + " and " + said[-1]


def _the_factors(clean):
    """\"the factors of 12\", \"what are the factors of 36\", \"list the factors of 24\".

    A factor is a number that divides in with nothing left over, and people ask for the list far
    more often than they ask what the word means: "the factors of 12" reached nothing at all and
    "what are the factors of 36" was answered with the definition of a factor. The definition is
    kept as the second sentence, where it belongs.
    """
    if re.search(r"common factor|common multiple|prime factor|factorise|factorize|factor tree|"
                 r"factor the|factor out|scale factor|conversion factor|factor of safety",
                 clean):
        return None
    # "is 3 a factor of 12" and "is 15 or 20 a factor of 30": the answer is a yes or a no with the
    # sum behind it, and both numbers have to be answered when the line names two.
    found = re.search(r"\bis\s+(\d+)\s*(?:,|\bor\b|\band\b|/)?\s*(?:and\s+)?(\d+)?\s+"
                      r"a\s+factor\s+of\s+(\d+)\b", clean)
    if found:
        asked = [int(found.group(1))]
        if found.group(2):
            asked.append(int(found.group(2)))
        whole = int(found.group(3))
        if whole < 1 or max(asked) > 1000000:
            return None
        said = []
        for number in asked:
            if number > whole:
                said.append(f"{number} is bigger than {whole}, so no: it cannot divide into it "
                            f"even once.")
            elif whole % number == 0:
                said.append(f"{number} is a factor of {whole}: {whole} divided by {number} is "
                            f"{whole // number}.")
            else:
                times = whole // number
                left = whole - times * number
                said.append(f"{number} is not a factor of {whole}: {number} goes in {times} "
                            f"time{'s' if times != 1 else ''} with {left} left over.")
        if len(said) == 1:
            return said[0]
        return " ".join(said)
    # "is 12 a multiple of 3" is the same question the other way round
    found = re.search(r"\bis\s+(\d+)\s+a\s+multiple\s+of\s+(\d+)\b", clean)
    if found:
        number, base = int(found.group(1)), int(found.group(2))
        if not base or max(number, base) > 1000000:
            return None
        if number % base == 0:
            return (f"Yes: {number} is {base} x {number // base}, so it is in the {base} times "
                    f"table.")
        return (f"No: {base} x {number // base} is {base * (number // base)}, and {base} x "
                f"{number // base + 1} is {base * (number // base + 1)}, so {number} is not in "
                f"the {base} times table.")
    # the list, when the line asks for the factors rather than whether one is a factor
    found = re.search(r"\bfactors? of\s+(\d+)\b(?!\s*(?:and|&)\b)", clean)
    if found:
        number = int(found.group(1))
        if number < 1 or number > 100000:
            return None
        factors = _factors_in_list(number)
        pairs = []
        for small in factors:
            if small * small > number:
                break
            pairs.append(f"{small} x {number // small}")
        said = (f"The factors of {number} are {_said_list(factors)}: those are the numbers that "
                f"divide into {number} with nothing left over, counting 1 and {number} itself.")
        if len(factors) == 2:
            return said + f" That makes {number} a prime number."
        said += f" You only have to try up to {int(number ** 0.5)} - the square root - because "
        said += "the pairs do the rest: " + ", ".join(pairs) + "."
        return said
    return None


def _common_factors(clean):
    """\"highest common factor of 12 and 18\", \"lowest common multiple of 4 and 6\"."""
    asked = None
    if re.search(r"highest common factor|greatest common (?:factor|divisor)|\bhcf\b|\bgcd\b",
                 clean):
        asked = "highest common factor"
    elif re.search(r"lowest common multiple|least common multiple|\blcm\b", clean):
        asked = "lowest common multiple"
    if not asked:
        return None
    numbers = re.findall(r"\b(\d+)\b", clean)
    if len(numbers) < 2:
        return None
    first, second = int(numbers[0]), int(numbers[1])
    if not first or not second:
        return None
    a, b = first, second
    while b:
        a, b = b, a % b
    if asked == "highest common factor":
        return f"The highest common factor of {first} and {second} is {a}."
    return (f"The lowest common multiple of {first} and {second} is "
            f"{first // a * second}.")


_NEAREST = {"whole": 0, "unit": 0, "units": 0, "one": 0, "ten": -1, "tens": -1, "10": -1,
            "hundred": -2, "hundreds": -2, "100": -2, "thousand": -3, "thousands": -3,
            "1000": -3}


def _round_to(clean):
    """\"round 3.456 to two decimal places\", \"round 2.5 to the nearest whole number\"."""
    match = re.search(r"round\s+(-?\d+(?:\.\d+)?)\s*(?:to|at)\s*(?:the\s+)?(\w+)\s*"
                      r"(decimal places?|places?|dp|significant figures?)", clean)
    if not match:
        # "round 2.5 to the nearest whole number" is the commonest way of saying it, and the
        # counting word carries the place: whole number, ten, hundred, thousand.
        near = re.search(r"round\s+(-?\d+(?:\.\d+)?)\s*(?:up|down|off)?\s*(?:to|at)\s*"
                         r"(?:the\s+)?nearest\s+(\w+)", clean)
        if not near or near.group(2) not in _NEAREST:
            # "how do i round 4.6" names a number and no place, which almost always means the
            # whole number. The card that explains the rule answered it without ever rounding
            # the number they gave, so the rule is said and applied in one line. A decimal point
            # is required: "round 3" on its own is a sports line as often as a sum.
            bare = re.search(r"\bround\s+(-?\d+\.\d+)\s*$", clean)
            if not bare:
                return None
            written = bare.group(1)
            kept = _places(written, 0)
            value = Decimal(str(written))
            why = "up" if value.quantize(Decimal(1), rounding=ROUND_HALF_UP) > value else "down"
            return (f"{written} is {kept} to the nearest whole number: the digit after the "
                    f"point decides it, so the whole number goes {why}.")
        written, word = near.group(1), near.group(2)
        below = _NEAREST[word]
        if below:
            stepped = Decimal(str(written)).quantize(Decimal(1).scaleb(-below),
                                                     rounding=ROUND_HALF_UP)
            return f"{written} is {stepped:f} to the nearest {word}."
        what = "whole number" if _NEAREST[word] == 0 else word
        return f"{written} is {_places(written, 0)} to the nearest {what}."
    written = match.group(1)
    value = float(written)
    places = _PLACES.get(match.group(2))
    if places is None:
        return None
    plural = "s" if places != 1 else ""
    if "figure" in match.group(3):
        if not value:
            return None
        from math import floor, log10
        digits = places - int(floor(log10(abs(value)))) - 1
        rounded = round(value, digits)
        return (f"{written} is {_number(rounded)} to {match.group(2)} significant "
                f"figure{plural}.")
    return (f"{written} is {_places(written, places)} to {match.group(2)} "
            f"decimal place{plural}.")


def _places(written, places):
    """A decimal rounded by the hand rule, so 2.675 is 2.68.

    `round(2.675, 2)` gives 2.67, because 2.675 is stored just under itself in binary and the
    half never arrives; a school answer has to round a half up, which is what Decimal does on
    the digits as written.
    """
    kept = Decimal(str(written)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    text = f"{kept:f}"
    if "." not in text:
        return text
    return text.rstrip("0").rstrip(".") or "0"


def _circle_measure(clean):
    """The circumference of a circle, from its radius or its diameter."""
    if "circumference" not in clean:
        return None
    match = re.search(r"radius\s*(?:of\s*)?(\d+(?:\.\d+)?)", clean)
    if match:
        radius = float(match.group(1))
    else:
        match = re.search(r"diameter\s*(?:of\s*)?(\d+(?:\.\d+)?)", clean)
        if not match:
            return None
        radius = float(match.group(1)) / 2
    around = 2 * 3.141592653589793 * radius
    return (f"The circumference is 2 x pi x radius, so about {_number(round(around, 2))} "
            f"(3.14 x {_number(round(2 * radius, 2))}).")


def _box_volume(clean):
    """\"volume of a box 10cm by 5cm by 2cm\": length x width x height."""
    if "volume" not in clean:
        return None
    numbers = re.findall(r"(\d+(?:\.\d+)?)\s*(?:cm|m|mm|metres?|centimetres?|inches?|in\b)?"
                         r"\s*(?:by|x|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|m|mm)?\s*"
                         r"(?:by|x|\*)\s*(\d+(?:\.\d+)?)", clean)
    if not numbers:
        return None
    length, width, height = (float(size) for size in numbers[0])
    volume = length * width * height
    unit = "cm" if "cm" in clean else "m" if re.search(r"\bmetres?\b|\bm\b", clean) else ""
    return (f"{_number(length)} x {_number(width)} x {_number(height)} is "
            f"{_number(round(volume, 2))}{(' ' + unit + '3') if unit else ''}.")


_MATHS_WORDS = (
    (r"(?<![a-z])x\s*squared\b|\bxsquared\b", "x^2"),
    (r"\bplus\b", "+"),
    (r"\bminus\b", "-"),
    (r"\bequals\b|\bequal\s+to\b", "="),
    (r"\bzero\b", "0"),
    (r"\bnegative\s+", "-"),
    (r"\b(?:find|work\s+out|solve\s+for)\s+x\b", "solve"),
)


# A quadratic nobody asked to solve is not a question: "x squared plus 5x plus 6" on its own
# is a phrase, and only these words make it the school task.
_QUADRATIC_ASK = ("solve", "solves", "root", "roots", "zero", "zeros", "factorise", "factorize",
                  "factor", "factors", "find", "work", "value")


# The asks that want the brackets rather than the roots.
_FACTOR_ASK = ("factorise", "factorize", "factor", "factors", "brackets")


def _factorised(a, b, c):
    """(m, (p, q, r, s)) for m(px + q)(rx + s) in whole numbers, or None.

    The common factor comes out first: 2x squared minus 8 is 2(x - 2)(x + 2), and searching
    the brackets alone found (x - 2)(2x + 4), which is right but not the way it is written.
    """
    if a != int(a) or b != int(b) or c != int(c) or a < 1:
        return None
    a, b, c = int(a), int(b), int(c)
    common = 0
    for number in (a, b, c):
        common = _gcd(common, number)
    if common < 1:
        common = 1
    a, b, c = a // common, b // common, c // common
    reach = abs(b) + abs(c) + 1
    for p in range(1, a + 1):
        if a % p:
            continue
        r = a // p
        # s follows from p*s + r*q = b, so only q has to be tried: 3x squared plus 6x is
        # 3x(x + 2), and searching the pairs of the constant alone missed it because the
        # constant is zero.
        for q in range(-reach, reach + 1):
            top = b - r * q
            if top % p:
                continue
            s = top // p
            if q * s == c:
                return (common, (p, q, r, s))
    return None


def _gcd(one, other):
    while other:
        one, other = other, one % other
    return abs(one)


def _said(found):
    """(1, 3, 1, 4) said as (x + 3)(x + 4), and twice the same bracket as (x + 1)^2."""
    common, (p, q, r, s) = found

    def bracket(lead, tail):
        left = "x" if lead == 1 else f"{lead}x"
        if not tail:
            return f"({left})"
        return f"({left} + {tail})" if tail > 0 else f"({left} - {abs(tail)})"

    first, second = bracket(p, q), bracket(r, s)
    if common != 1 and first == "(x)":
        # 3x squared plus 6x is 3x(x + 2): the common factor and the bare x are one word
        return f"{common}x{second}"
    said = f"{first}^2" if first == second else first + second
    return said if common == 1 else f"{common}{said}"


def _quadratic(clean):
    """A quadratic equation with x squared in it, worked out: "x squared + 5x + 6 = 0"."""
    text = clean
    for pattern, swap in _MATHS_WORDS:
        text = re.sub(pattern, swap, text)
    text = re.sub(r"\s+", " ", text).strip()
    lead = re.search(r"(?:^|\s)([+-]?\d*\.?\d*)\s*\*?\s*x\s*\^\s*2", text)
    if not lead:
        return None
    rest = text[lead.end():].strip()
    # the linear term, if there is one
    b = 0.0
    linear = re.match(r"([+-])\s*(\d*\.?\d*)\s*\*?\s*x(?![\w^])", rest)
    if linear:
        size = float(linear.group(2)) if linear.group(2) else 1.0
        b = size if linear.group(1) == "+" else -size
        rest = rest[linear.end():].strip()
    # the constant, if there is one
    c = 0.0
    constant = re.match(r"([+-])\s*(\d*\.?\d*)", rest)
    if constant:
        size = float(constant.group(2)) if constant.group(2) else 1.0
        c = size if constant.group(1) == "+" else -size
        rest = rest[constant.end():].strip()
    # the right-hand side, which is usually zero
    right = 0.0
    if rest.startswith("="):
        side = rest[1:].strip()
        if not re.fullmatch(r"[+-]?\d+\.?\d*", side):
            return None
        right = float(side)
        rest = ""
    if rest:
        return None
    raw = lead.group(1)
    a = 1.0 if raw in ("", "+") else -1.0 if raw == "-" else float(raw)
    if not a:
        return None
    asked = clean.replace("^2", " ").split()
    if right == 0 and not any(word in asked for word in _QUADRATIC_ASK):
        return None
    c -= right
    discriminant = b * b - 4 * a * c
    factorised = _factorised(a, b, c)
    wants_brackets = any(word in asked for word in _FACTOR_ASK)
    if discriminant < -1e-9:
        if wants_brackets:
            return (f"It does not factorise with whole numbers, and no real number solves it "
                    f"either: the square of a number is never negative, so the formula stops "
                    f"at the square root of a negative number.")
        return (f"No real number solves that: the square of a number is never negative, so "
                f"there is no real answer. (The formula gives the square root of a negative "
                f"number here.)")
    if abs(discriminant) < 1e-9:
        root = -b / (2 * a)
        if wants_brackets and factorised:
            return (f"It factorises as {_said(factorised)}, so x = {_number(root)} is the only "
                    f"answer: both brackets are the same, which is why there is one root, not "
                    f"two.")
        said = (f"x = {_number(root)}. There is one answer, not two, because both roots of the "
                f"formula are the same.")
        if factorised:
            said += f" The factorised form is {_said(factorised)}."
        return said
    roots = sorted(((-b + discriminant ** 0.5) / (2 * a), (-b - discriminant ** 0.5) / (2 * a)))
    whole = all(abs(root - round(root)) < 1e-9 for root in roots)
    # "factorise x squared plus 7x plus 12" asks for the brackets, not for the roots: the
    # roots are how you check it. The brackets come out in whole numbers whenever the
    # equation has them, and 2x squared plus 3x minus 2 gives (2x - 1)(x + 2), which the
    # roots alone would have printed as 0.5 and -2 with an apology that it does not factor.
    if wants_brackets:
        if factorised:
            said = (f"It factorises as {_said(factorised)}, so x = "
                    f"{_number(roots[0])} or x = {_number(roots[1])}.")
            if abs(roots[0] - roots[1]) > 1e-9:
                return said + " Multiply the brackets out to check you get the equation back."
            return said
        return (f"It does not factorise with whole numbers, so put a = {_number(a)}, "
                f"b = {_number(b)} and c = {_number(c)} into x = (-b +/- the square root of "
                f"b squared - 4ac) / 2a: that gives x = {_number(round(roots[0], 2))} or "
                f"x = {_number(round(roots[1], 2))}.")
    if whole:
        left, high = int(round(roots[0])), int(round(roots[1]))
        said = (f"x = {left} or x = {high}. Put either one back in and the equation comes to "
                f"zero, which is the check.")
        if factorised:
            said += f" The factorised form is {_said(factorised)}."
        return said
    # 2x squared plus 3x minus 2 has the exact roots -2 and 0.5 and the brackets (2x - 1)(x + 2),
    # so "to two decimal places" and "it does not factor" were both untrue of it. A root that
    # stops at two decimals is printed as it is, and the formula is only named when the roots
    # really do run on.
    exact = all(abs(root - round(root, 2)) < 1e-9 for root in roots)
    if factorised:
        return (f"x = {_number(roots[0])} or x = {_number(roots[1])}, and both are exact: the "
                f"factorised form is {_said(factorised)}. Put either one back in and the "
                f"equation comes to zero.")
    if exact:
        return (f"x = {_number(roots[0])} or x = {_number(roots[1])}. Put either one back in "
                f"and the equation comes to zero, which is the check.")
    return (f"x = {_number(round(roots[0], 2))} or x = {_number(round(roots[1], 2))}, to two "
            f"decimal places: it does not factor with whole numbers, so use the formula "
            f"x = (-b +/- the square root of b squared - 4ac) / 2a.")


def _equation(clean):
    """A one-variable equation with x: "solve 2x + 3 = 11"."""
    if "=" not in clean or not re.search(r"(?<![a-z])x(?![a-z])", clean):
        return None
    if not (any(word in clean for word in ("solve", "find x", "value of x", "what is x"))
            or re.fullmatch(r"[\s0-9x+\-=*.]*", clean)):
        return None
    match = re.search(r"([+-]?\d*)\*?x(?![a-z])\s*([+-]\s*\d+(?:\.\d+)?)?\s*=\s*"
                      r"([+-]?\d+(?:\.\d+)?)", clean)
    if not match:
        return None
    coefficient = float(match.group(1)) if match.group(1) not in ("", "+", "-") else 1.0
    if match.group(1) == "-":
        coefficient = -1.0
    add = float(match.group(2).replace(" ", "")) if match.group(2) else 0.0
    right = float(match.group(3).replace(" ", ""))
    if not coefficient:
        return None
    x = (right - add) / coefficient
    return f"x = {_number(x)}."


def _percent(clean):
    # A tip line wants the tip and the total, which _tip gives below. Only a "what is 20
    # percent of 60" line is a plain share and belongs here.
    if re.search(r"(?:%|percent|per cent)\s*(?:tip|gratuity)\b", clean):
        return None
    after = re.search(r"(?:costs?|priced at|is|are|was)\s+(?:£|\$)?([\d,.]+)\D.*?"
                      r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s*off", clean)
    if after:
        total, part = _amount(after.group(1)), _amount(after.group(2))
        amount = total * part / 100
        return (f"{_number(part)}% off {_number(total)} leaves {_number(total - amount)} "
                f"(you save {_number(amount)}).")
    # A named share of a bill is the same sum: "20 percent service charge on 85" is 17.
    # A tip is not here: a tip question wants the tip and the total, which _tip gives.
    # "off" keeps its own wording below.
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)\s*"
                      r"(?:service(?:\s+charge)?|tax|charge|vat)?\s*"
                      r"(of|off|on(?:\s+top\s+of)?)\s*"
                      r"(?:(?:my|our|the|a|an)\s+)?"
                      r"(?:(?:bill|total|check|tab)\s+of\s+)?([\d,.]+)", clean)
    if not match:
        match = re.search(r"what(?:'s| is)\s*(\d+(?:\.\d+)?)\s*(of|off)\s*([\d,.]+)\s*%", clean)
        if not match:
            return None
        part, kind, total = float(match.group(1)), match.group(2), float(match.group(3).replace(",", ""))
    else:
        part, kind, total = float(match.group(1)), match.group(2), float(match.group(3).replace(",", ""))
    amount = total * part / 100
    if kind == "off":
        return (f"{_number(part)}% off {_number(total)} leaves {_number(total - amount)} "
                f"(you save {_number(amount)}).")
    return f"{_number(part)}% of {_number(total)} is {_number(amount)}."


def _percentage_change(clean):
    match = re.search(r"(?:percentage|percent)\s+(?:increase|change|difference)\s+from\s+"
                      r"([\d,.]+)\s+to\s+([\d,.]+)", clean)
    if not match:
        return None
    start = float(match.group(1).replace(",", ""))
    end = float(match.group(2).replace(",", ""))
    if not start:
        return None
    change = (end - start) / start * 100
    word = "increase" if change >= 0 else "decrease"
    return f"That's a {_number(abs(change))}% {word}."


def _amount(text):
    """The number a short phrase gives, as a float."""
    return float(text.replace(",", ""))


# "how many grams in an ounce": the counted unit, then the unit it goes into.
_AMOUNT = r"(?:how many|number of)\s+([a-z']+)\s+(.*)"
