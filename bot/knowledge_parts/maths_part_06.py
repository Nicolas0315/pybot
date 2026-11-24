"""Part 6 of 6 of a large module, split out of `maths`.

Everything here is re-exported from `maths`, so callers import it from there as before.
"""
import re

from ..knowledge.lookup import entry
from .maths_part_05 import (
    _a_rounding_question, _ROUND_IS_AROUND, ROUND_IS_NOT_THE_VERB, _averages,
)


def _rounding_is_the_ask(understood):
    """The card needs the verb and needs a number or the name: "round work" is neither."""
    return _round_is_the_verb(understood) and _a_rounding_question(understood)


def _round_is_the_verb(understood):
    """True when "round" in the line is the maths verb rather than a way of saying "around"."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "text")).lower()
    return not _ROUND_IS_AROUND.search(said)


# An hour with nothing to do in it is a free-time question, and the rate row answered it:
# "what can i do for an hour" and "i have an hour to kill, what can i do" were told to divide the
# yearly pay by the hours actually paid for. The word "an hour" is in this row's key because the
# rate is asked that way, so the asking shape is what stands it down - not the hour.
_FREE_TIME_ASK = ("what can i do", "what should i do", "what do i do", "what to do",
                  "shall i do", "should i do", "anything to do", "something to do",
                  "things to do", "to kill", "kill an hour", "keep busy")


# A rate is paid for something. "What should i watch in an hour" and "how many minutes in an hour
# and a half" name a length of time and no money at all, and this row answered both with a salary
# sum - it is keyed on "an hour", and an hour on its own is not a rate. So the row stands down on
# any line that names time and no pay, and the figure being paid, the pay words and the year keep
# the lines that really are about a rate.
_A_LENGTH_OF_TIME = re.compile(r"\bhours?\b|\bminutes?\b|\bseconds?\b")


_A_PAY_WORD = re.compile(r"\b(?:pay|paid|pays|paying|salary|salaries|wage|wages|earn|earns|earning|"
                         r"rate|rates|hourly|take home|contract|overtime|per hour|a year|annual|"
                         r"annually|yearly|a month|monthly)\b|"
                         r"\d+(?:\.\d+)?\s*(?:pounds?|quid|an hour|per hour)|"
                         # "how much do i make an hour" is a rate with no pay word in it: the
                         # verb is what says the money, so it counts only asked that way
                         r"\bhow\s+much\s+(?:do|does|would|will|did)\s+"
                         r"(?:i|you|we|they|it|that|he|she)\s+(?:make|makes|get|take)\b")


def _not_a_spare_hour(understood):
    """False when the line asks what to do with the hour rather than what it pays."""
    said = understood if isinstance(understood, dict) else {}
    line = str(said.get("clean") or said.get("text") or "").lower()
    if any(phrase in line for phrase in _FREE_TIME_ASK):
        return False
    if _A_LENGTH_OF_TIME.search(line) and not _A_PAY_WORD.search(line):
        return False
    return True


PRIME_DEFINITION = (
    "A prime number is a whole number greater than 1 that divides only by 1 and itself: 2, 3, 5, "
    "7, 11 and so on. 1 is not prime, and 2 is the only even prime.")


PRIME_TEST = (
    " To test one, try dividing it by 2, 3, 5, 7, 11 and the rest of the primes up to its square "
    "root: if none of them goes in exactly, it is prime. So 97 needs only a check against 2, 3, 5 "
    "and 7, since 11 squared is past it. Anything that ends in 0, 2, 4, 5, 6 or 8, or whose digits "
    "add up to a multiple of 3, is not prime.")


def _prime_definition(memory, understood):
    """The definition, with the test of a number added only when the line asks how to test one."""
    said = " ".join(str((understood or {}).get("clean")
                       or (understood or {}).get("text") or "").lower().split())
    if re.search(r"\b\d+\b", said):
        # a named number wants a verdict, which the number reader gives
        return None
    if re.search(r"\b(how|work out|check|test|tell|know)\b", said):
        return PRIME_DEFINITION + PRIME_TEST
    return PRIME_DEFINITION


ENTRIES = [
    entry("pi", ("pi", ("what", "value", "number", "3.14", "3.14159")),
          "Pi (π) is about 3.14159: the circumference of any circle divided by its diameter. For "
          "most everyday sums, 3.14 is close enough."),
    # "what is a prime number" wants the definition, and "how do i work out if a number is
    # prime" wants the test: one row, and the test only comes when the line asks how. A line
    # that names a number ("is 51 prime", "how do i check if 51 is prime") wants a verdict, not
    # a definition, so this row stands down and the number reader answers it.
    entry("prime-number", (("prime", "prime number", "prime numbers"),
                           ("what", "number", "definition", "mean", "work out", "how", "check",
                            "test", "tell", "know")),
          _prime_definition,
          ask=("what", "define", "meaning", "explain", "how", "work out", "check", "tell"),
          # "prime" is a verb in the decorating sense, and those lines are all about paint:
          # "how do i prime a wall before painting" wants a primer and a roller
          avoid=("wall", "walls", "wood", "woodwork", "paint", "painting", "painted", "primer",
                 "undercoat", "metal", "gate", "gates", "door", "doors", "skirting", "ceiling",
                 "plaster", "render", "mdf", "bare wood", "filler", "roller", "brush", "minis",
                 "miniature", "prime minister", "amazon prime", "prime video", "prime day")),
    entry("percent-how", (("percentage", "percent", "percentages"),
                          ("work", "calculate", "out", "how", "formula", "explain")),
          "To find a percentage of something, divide the amount by 100 and multiply by the "
          "percentage: 15% of 80 is 80 ÷ 100 × 15 = 12. To turn a fraction into a percentage, "
          "divide the top by the bottom and multiply by 100.",
          ask=("how", "what", "explain", "formula", "calculate", "work out")),
    # The method, for the line that asks how and not for one particular equation. Every
    # "solve x squared ..." line is worked out above by _quadratic(), so this only takes the
    # general question, and the ask words keep it off "quadratic graphs" and "what is a
    # quadratic" - though it answers that too, since it is the same shape of answer.
    entry("quadratic-formula",
          (("quadratic", "quadratics", "quadratic equation", "quadratic equations",
            "quadratic formula"),
           ("solve", "solving", "formula", "method", "roots", "root", "factorise", "factorize",
            "factor", "how", "what", "work out", "explain", "equation", "equations")),
          "Arrange it as ax² + bx + c = 0, then put the numbers into x = (-b ± √(b² - 4ac)) / 2a. "
          "If b² - 4ac is positive there are two answers, zero means one answer, and negative "
          "means none without imaginary numbers. Try factorising first when the numbers are "
          "small: x² + 5x + 6 is (x + 2)(x + 3), so x is -2 or -3.",
          ask=("how", "what", "solve", "method", "explain", "roots", "formula")),
    entry("bodmas", (("bodmas", "bidmas", "order of operations"),
                     ("what", "maths", "mean", "rules")),
          "Work in this order: brackets, then powers or roots, then multiplication and division "
          "left to right, then addition and subtraction left to right. So 2 + 3 × 4 is 14, not "
          "20.", ask=("what", "how", "order", "mean")),
    # "how do i work out square metres" is the same sum in the units people buy carpet and turf
    # in, and it was a shrug: the working is here, in one sentence, so the words are in the key.
    entry("area-formula", (("area", "square metres", "square meters", "square footage",
                            "square foot", "square feet", "m2", "sqm"),
                           ("formula", "work out", "calculate", "how", "what", "many")),
          "For a rectangle, area = length × width; for a triangle, ½ × base × height; for a "
          "circle, π × radius². Keep all the measurements in the same unit. So a room 4m by 3m "
          "is 12 square metres, and an L-shaped floor is two rectangles added together.",
          # the sum, not the thing being bought: a turf, carpet or tile quantity is that
          # product's own card, and "square metres" was pulling it here
          avoid=("turf", "grass", "lawn", "carpet", "carpets", "carpeting", "flooring", "floor",
                 "tiles", "tiling", "gravel", "soil", "decking", "paint", "wallpaper", "border",
                 "grout", "adhesive", "plasterboard"),
          ask=("how", "formula", "calculate", "work")),
    # "how many days in a leap year" is the length of the year (above); this is the reason for
    # it, so the ask words are the question and not the noun.
    entry("leap-year-why", (("leap year", "leap years", "leap day", "february 29", "29 february",
                             "29th of february"),
                            ("why", "reason", "exist", "needed", "needs", "happen", "happens",
                             "extra", "added", "invented", "what is", "whats", "mean")),
          "A leap year is a year with 366 days and a 29th of February, because a year is really "
          "about 365 and a quarter: without the extra day the calendar would slip a day every "
          "four years. One correction keeps it exact, since the year is not quite a quarter "
          "longer - a century is only a leap year if it divides by 400, which is why 1900 was not "
          "one and 2000 was.",
          avoid=("how many days", "how long", "how many weeks", "days in february")),
    entry("fraction-decimal", (("fraction",), ("decimal", "convert", "change")),
          "To turn a fraction into a decimal, divide the top number by the bottom: 3/4 is "
          "3 ÷ 4 = 0.75. Some fractions repeat for ever, like 1/3 = 0.333…", ask=("how", "convert", "change", "decimal")),
    entry("average-mean", (("average", "averages", "mean", "median", "mode", "statistics",
                            "the mean", "the median", "the mode"),
                           ("what", "how", "work out", "calculate", "find", "difference",
                            "define", "explain", "vs")),
          _averages,
          # "what do you mean" and "i mean" are the conversational mean, not the statistic
          # "portrait mode" and "bokeh" are the camera's, not the mode of a set of numbers
          # "whats that mean" and "what does it actually mean" are the same conversational
          # question in a quicker spelling: a line with no subject of its own, or with "that",
          # "it" or "this" as one, is never asking what a mean average is
          avoid=("you mean", "i mean", "does that mean", "what do you",
                 "that mean", "it mean", "this mean", "mean by",
                 "portrait", "portrait mode", "bokeh", "selfie", "camera", "photo", "photos",
                 # "how do i turn him down without being mean" is the refusal, and the only word
                 # it shared with this row was the adjective: a statistic is never asked for
                 # with "without being mean", and no one refuses a date with a formula.
                 "without being mean", "not being mean", "be mean", "being mean", "sound mean",
                 "mean to", "mean about", "turn him down", "turn her down", "turn them down",
                 "let him down", "let her down", "let them down")),
    # The everyday sums people ask how to do rather than what the answer is: VAT added to a
    # price and taken back off it, and an hourly rate from a salary. Both were shrugs, and
    # "how do i work out vat" was worse than a shrug - fitness read "work out" as the verb of a
    # session and answered "three half-hour sessions a week".
    entry("vat-how",
          (("vat", "value added tax"),
           ("how", "work out", "calculate", "add", "take off", "remove", "price", "included",
            "charge", "deduct", "minus")),
          "VAT in the UK is 20%: add it by multiplying the price by 1.2, so £80 becomes £96, and "
          "take it off a VAT-inclusive price by dividing by 1.2, so £96 is £80 plus £16 of VAT. "
          "The VAT on a net price is simply a fifth of it.",
          ask=("how", "work out", "calculate", "add", "take off", "remove", "deduct"),
          # "what is vat" is the definition and money has it; a VAT number, a refund or a
          # registration is another question again
          avoid=("number", "registration", "register", "refund", "return", "rebate",
                 "what is vat", "what's vat")),
    entry("hourly-rate",
          (("hourly rate", "hourly pay", "rate an hour", "rate per hour", "per hour",
            "an hour"),
           ("work out", "calculate", "from my salary", "salary", "annual", "yearly",
            "take home", "contract", "hours")),
          "Divide the yearly pay by the hours you are actually paid for: £30,000 over 37.5 "
          "hours a week is £30,000 ÷ (37.5 × 52) = about £15.40 an hour, and only the paid "
          "weeks count, so unpaid breaks or a term-time contract change the figure. Take-home "
          "hourly pay uses the figure after tax and pension, not the salary.",
          ask=("how", "work out", "calculate", "what"),
          guard=_not_a_spare_hour,
          # "what can i make with half an hour" names an hour, and the rate row took the dinner
          # question: a line that asks what to cook with the time it has names a dish, and a row
          # about a rate cannot answer it. Only the make/cook words - DISH_ASK also holds "do
          # with", which would take "i have half an hour free after work, whats the best thing
          # to do with it" off the answer it has now, and that line is not about money either
          # but it is not this row's to fix.
          avoid=("make with", "made with", "make using", "make from", "make out of",
                 "what can i make", "what can i cook", "what should i make", "cook with",
                 "cooking with",
                 # "what is a quarter of an hour" and "how many minutes in an hour and a half"
                 # name an hour and ask "what", which is this row's key, and neither is about
                 # money: the answer is the span in minutes, and units.py has it. A length of
                 # time is never a rate, so the words that only ever ask for one stand the row
                 # down - a rate is asked about pay, hours worked or a year, and keeps those.
                 "fraction", "of an hour", "of a day", "hour and a half", "minutes", "seconds",
                 "how long", "how many minutes",
                 "electricity", "energy", "gas", "water", "parking", "charge", "charging",
                 "battery", "kilowatt", "kwh", "boiler", "car", "van", "hire", "rent",
                 "babysit", "childcare", "cleaner", "tradesman", "plumber", "electrician",
                 # an hour in the oven is not an hour of pay: "half an hour in the oven, what
                 # temperature for a cake" and "an hour in the oven then what" were both handed
                 # the salary divided down to an hourly rate, because "an hour" is a key here
                 # and "what" is the ask. Anything that says the oven is the cooking clock.
                 "oven", "bake", "baked", "baking", "roast", "roasting", "roasted",
                 "temperature", "gas mark", "fan oven", "simmer", "simmering", "boil",
                 "boiling", "marinate", "marinade", "prove", "proving", "knead", "chill",
                 "chilling", "fridge", "freezer", "recipe", "casserole", "cake", "bread",
                 "biscuits", "pastry", "pasties", "batter", "dough",
                 # "how much is garage labour per hour" is the garage's rate, and the word
                 # "labour" is not the wage of the person asking: a trade or a car in the line
                 # is somebody else's hourly rate, and cars.py prices those.
                 "garage", "garages", "mechanic", "mechanics", "labour", "clutch", "cambelt",
                 "mot", "servicing", "bodywork")),
    entry("compound-interest", (("compound interest", "interest rate", "interest rates",
                                 "compound"),
                                ("what", "how", "work out", "calculate", "means", "works",
                                 "worth", "better")),
          "Compound interest pays interest on the interest as well as on what you put in, so "
          "£1,000 at 5% is £1,050 after a year and £1,102.50 after two, because the second year "
          "pays 5% of £1,050. The rule of 72 is the shortcut: divide 72 by the rate to get the "
          "years it takes to double, so 5% doubles in about 14 years.",
          avoid=("no interest", "not interested", "hobby", "hobbies", "common interest",
                 "in common", "of interest",
                 # "what is a good interest rate for a savings account" asks which account pays
                 # well, not what compounding is: the rate to look for is a different answer
                 "good rate", "good interest", "best rate", "best interest", "decent rate",
                 "decent interest", "what rate", "which rate", "highest rate", "savings")),
    # --- the school questions that ask how ---------------------------------
    # "how do I work out a ratio" has no numbers in it, so nothing can be computed: the answer
    # is the method, with one worked example so it can be followed. Each of these was a shrug.
    # "how do i find half of a number" was a half marathon on main: the word "half" and the word
    # "how" are all `race-distance-half` needed, and nothing held the sum. Halving is the first
    # fraction anybody meets, and it is the one people ask for by name rather than as a fraction.
    entry("half-of-a-number",
          (("half", "halve", "halves", "half of", "half of a number"),
           ("number", "numbers", "amount", "figure", "sum", "of a number", "work out", "find",
            "calculate", "how")),
          "Divide it by 2: half of 46 is 23, and half of 7 is 3.5. For a quarter, halve it twice; "
          "for 10 per cent divide by 10, and for 5 per cent halve that.",
          ask=("how", "what", "find", "work out", "calculate", "of a number"),
          # a half marathon, half an hour, half term and half price are all other answers
          # "how do i use up half a tin of coconut milk" is a leftover question: half of a
          # container is a use-up row, so every container noun and the use-up wording stands down
          avoid=("marathon", "5k", "10k", "race", "run", "running", "ran", "training", "train",
                 "distance", "miles", "km", "kilometres", "kilometers", "an hour", "hour",
                 "past", "term", "price", "half price", "a day", "a week", "pint", "recipe",
                 "cooking", "bottle", "glass", "cup",
                 "use up", "use it up", "using up", "used up", "leftover", "left over",
                 "leftovers", "tin", "tins", "tin of", "can", "cans", "can of", "jar", "jars",
                 "packet", "packets", "packet of", "carton", "carton of", "tub", "pots", "pot",
                 "punnet", "bag", "bags", "bunch", "tray", "half a tin", "half a can",
                 "half a jar", "half a packet",
                 # "im going to halve my dose and see how i go" is a plan about a prescription:
                 # "Divide it by 2: half of 46 is 23" is arithmetic help for a sum nobody asked,
                 # and the medicine is not a number. A medicine word in the line means the sums
                 # row stands down, whatever the words around it.
                 "dose", "doses", "dosage", "tablet", "tablets", "pill", "pills", "capsule",
                 "capsules", "medication", "medicine", "medicines", "insulin", "steroid",
                 "steroids", "inhaler", "inhalers", "antibiotic", "antibiotics", "statins",
                 "painkillers", "antidepressants", "prescription")),
    entry("ratio-how",
          (("ratio", "ratios", "proportion", "proportions", "share in a ratio"),
           ("how", "work", "out", "share", "divide", "simplify", "what", "explain", "split",
            "mean", "means")),
          "Add the parts of the ratio first, then divide the amount by that: sharing £50 in the "
          "ratio 2:3 is 5 parts, so each part is £10 and the shares are £20 and £30. To simplify "
          "a ratio, divide both numbers by the same thing, so 10:15 becomes 2:3.",
          ask=("how", "what", "explain", "mean", "work", "share", "simplify")),
    entry("standard-form",
          (("standard form", "scientific notation", "powers of ten", "powers of 10"),
           ("what", "how", "write", "maths", "explain", "mean", "convert", "big", "small",
            "number", "numbers")),
          "Standard form writes a number as something between 1 and 10 times a power of ten: "
          "4,500 is 4.5 x 10³, and 0.0002 is 2 x 10⁻⁴. Count how many places the decimal point "
          "moves, and make it negative when the number is below 1. To multiply, multiply the "
          "front numbers and add the powers.",
          ask=("what", "how", "write", "explain", "convert", "mean")),
    entry("simultaneous-equations",
          (("simultaneous equations", "simultaneous", "two equations", "equations with two"),
           ("solve", "how", "what", "method", "explain", "work", "find")),
          "Write one equation under the other and add or subtract them to lose a letter: "
          "2x + y = 7 and x + y = 4 gives x = 3 straight away, then y = 1 from either one. If "
          "nothing cancels, multiply one equation until it does. Put both numbers back into both "
          "equations to check.",
          ask=("how", "what", "solve", "explain", "method")),
    entry("factors-and-multiples",
          (("factor", "factors", "multiple", "multiples", "prime factor", "prime factors",
            "hcf", "lcm", "highest common factor", "lowest common multiple"),
           ("what", "difference", "how", "mean", "explain", "find", "vs", "between")),
          "A factor divides into a number exactly - 1, 2, 3, 4, 6 and 12 for 12 - and a multiple "
          "is in its times table: 12, 24, 36. A prime factor is a factor that is also prime, so "
          "12 is 2 x 2 x 3. The highest common factor of two numbers is the biggest one they "
          "share; the lowest common multiple is the smallest one they both divide into.",
          ask=("what", "how", "difference", "mean", "explain", "find")),
    entry("negative-numbers",
          (("negative number", "negative numbers", "minus number", "minus numbers"),
           ("what", "how", "add", "subtract", "multiply", "divide", "explain", "mean", "work")),
          "Use a number line: adding a negative moves you left, subtracting a negative moves you "
          "right, so 5 - (-3) is 8. Multiplying or dividing two negatives gives a positive, and "
          "one negative gives a negative: -2 x -3 is 6, and -6 / 2 is -3.",
          ask=("what", "how", "explain", "mean", "add", "subtract", "multiply", "work")),


    entry("rounding-how",
          (("rounding", "round", "decimal places", "significant figures", "nearest"),
           ("how", "what", "rules", "explain", "mean", "number", "work")),
          "Look at the digit just after the place you are keeping: 5 or more rounds the last "
          "kept digit up, 4 or less leaves it. So 3.456 to two decimal places is 3.46 and to the "
          "nearest whole number it is 3. Round once, at the end of a sum, not at every step.",
          # "round" is also what a cold does in an office and what a dog does at the park, and
          # with "how" in the key every one of those scored four: "how do i stop colds going
          # round the office" was told how to round 3.456 to two decimal places.
          avoid=ROUND_IS_NOT_THE_VERB + (
              "cold", "colds", "flu", "virus", "illness", "office", "park", "dog", "dogs",
              # and a round is a delivery, a drink, a fight and a golf hole: "what age can you
              # get a paper round" and "how much does a paper round pay" were both told how to
              # round 3.456 to two decimal places.
              "paper round", "paper rounds", "newspaper round", "paperboy", "papergirl",
              "paper route", "deliver papers", "round of drinks", "round of golf", "in a round"),
          ask=("how", "what", "rules", "explain", "mean", "work"),
          guard=_rounding_is_the_ask),
    # "what do the angles in a triangle add up to" was a search signpost: the shape entries
    # answer area and perimeter, and no entry knew the one fact every pupil is asked for.
    entry("triangle-angles",
          (("angle", "angles", "degree", "degrees"),
           ("triangle", "triangles", "add up", "add up to", "inside", "corner", "corners",
            "total", "sum", "180")),
          "The three angles inside any triangle add up to 180 degrees, so if you know two of "
          "them, take their total away from 180 for the third: 60 and 70 leaves 50. An "
          "equilateral triangle is 60 degrees each, and a right angle is 90. In a quadrilateral "
          "(a four-sided shape) the four angles add up to 360.",
          ask=("add up", "add up to", "total", "sum", "what", "how many", "inside")),

    entry("reading-a-graph",
          (("graph", "graphs", "line graph", "bar chart", "bar graph", "axis", "axes"),
           ("read", "reading", "how", "what", "plot", "draw", "explain", "mean")),
          "Read what each axis is measured in first, including the units and the step between "
          "the numbers. To read a value, go up from the number you know to the line, then across "
          "to the other axis. A straight line means the same change each time; a curve means it "
          "changes faster or slower.",
          ask=("how", "what", "read", "explain", "mean")),
    entry("fractions-how",
          (("add fractions", "adding fractions", "subtract fractions", "subtracting fractions",
            "common denominator", "fractions with different"),
           ("how", "add", "subtract", "different", "bottom", "denominator", "common", "explain")),
          "Give them the same bottom number first, then add or subtract the tops: 1/2 + 1/3 is "
          "3/6 + 2/6, which is 5/6. Use the lowest bottom both numbers divide into, which is 6 "
          "here and 4 for 1/2 + 1/4, then cancel the answer down.",
          ask=("how", "add", "subtract", "explain", "different")),
    entry("volume-how",
          (("volume", "cubic"),
           ("how", "work out", "calculate", "formula", "box", "cube", "cylinder", "what")),
          "For a box it is length x width x height, so 10cm by 5cm by 2cm is 100cm³. A cylinder "
          "is pi x radius² x height, and a sphere is 4/3 x pi x radius³. Put every measurement in "
          "the same unit before multiplying.",
          ask=("how", "what", "calculate", "formula", "work"),
          # "volume" is also the loudness of a phone, a television and a speaker: this entry is
          # the maths sum, so the sound words hand those lines over (technology's phone-louder)
          # the volume of a room is a sum; the volume of a TV, a phone or a speaker is a sound
          # setting, and "how do i reduce the volume on my tv" was getting the maths answer
          avoid=("phone", "iphone", "android", "mobile", "tv", "television", "speaker",
                 "speakers", "headphones", "airpods", "sound", "louder", "quieter", "quiet",
                 "hear", "music", "podcast", "calls", "ringtone", "laptop", "computer", "telly",
                 "soundbar", "sound bar", "radio", "earbuds", "turn up", "turn down", "mute",
                 "volume up", "volume down", "the volume on")),
    entry("circumference-how",
          (("circumference",),
           ("how", "work out", "calculate", "formula", "what", "circle", "mean")),
          "The circumference is pi times the diameter, or 2 x pi x radius: a circle with a radius "
          "of 5 has one of about 31.4. Pi is 3.14 to two decimal places. The area of the same "
          "circle is pi x radius², which is a different sum.",
          ask=("how", "what", "calculate", "formula", "work", "mean")),
    entry("simplify-fraction-how",
          (("simplify a fraction", "simplifying fractions", "simplify fractions",
            "simplest form", "lowest terms", "cancel down", "cancel a fraction"),
           ("how", "what", "explain", "mean", "simplify", "fraction", "fractions")),
          "Divide the top and the bottom by the same number until nothing goes into both: 6/8 "
          "divides by 2 to give 3/4, and that is as far as it goes. The number to start with is "
          "the highest common factor of the two.",
          ask=("how", "what", "explain", "mean", "simplify")),
    entry("decimals-how",
          (("decimal", "decimals", "decimal point", "decimal places"),
           ("multiply", "multiplying", "divide", "dividing", "how", "work", "explain", "times")),
          "Multiply as if the points were not there, then put the point back with as many "
          "decimal places as the two numbers had between them: 0.3 x 0.4 is 0.12. To divide, "
          "move both points the same number of places until the number you are dividing by is "
          "whole: 1.2 / 0.4 is 12 / 4, which is 3.",
          ask=("how", "explain", "work", "multiply", "divide", "times")),
]


# The words a school maths lesson defines, and the everyday senses that share them: a safe
# area to live, a perimeter fence, a variable mortgage rate. Each key names its own subject;
# the narrow ask keeps "what is the area of a 4m by 3m room" for the sum, not the definition.
_DEFINITION_ASK = ("what is", "what's", "whats", "what are", "what does", "what do",
                   "how does", "define", "definition", "meaning", "mean", "explain")


ENTRIES.append(entry(
    "decimal-what",
    (("decimal", "decimals"),
     ("what", "whats", "is a", "are", "mean", "meaning", "definition", "explain", "number")),
    "A decimal is a way of writing a number using place values for tenths, hundredths and so "
    "on, with a point after the units: 0.75 means seven tenths and five hundredths, which is the "
    "same as 3/4. The digits after the point tell you the place value, so 0.5 is five tenths and "
    "0.05 is five hundredths.",
    avoid=("betting", "odds", "bookmaker", "currency", "exchange rate", "binary", "hexadecimal",
           "hex", "binary code", "timesheet", "invoice"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "percentage-what",
    (("percentage", "percentages", "percent"), ("what", "mean", "meaning", "definition", "explain")),
    "A percentage is a fraction of 100: 25% means 25 out of every 100, or a quarter, and 100% is "
    "the whole thing. To turn a fraction into a percentage, divide the top by the bottom and "
    "multiply by 100, so 3/5 is 60%.",
    avoid=("of", "increase", "decrease", "change", "off", "discount", "tip", "vat", "tax",
           "interest", "raise", "calculator", "how much"),
    ask=_DEFINITION_ASK))


ENTRIES.append(entry(
    "area-what",
    (("area",), ("what", "mean", "meaning", "definition", "explain", "measured", "measure")),
    "Area is the amount of surface inside a shape, measured in square units: a room 4 m by 3 m "
    "has an area of 12 square metres. For a rectangle it is length times width, for a triangle "
    "half base times height, and for a circle pi times the radius squared.",
    avoid=("of", "live", "living", "move", "moving", "neighbourhood", "neighborhood", "postcode",
           "safe", "rough", "nice", "local area", "catchment", "deprived", "crime",
           # "in my area" is a place and not a surface: "what gyms are in my area" was answered
           # with the definition of area, and the areas of a town are the same word
           "in my area", "my area", "in our area", "our area", "in the area", "this area",
           "near me", "near us", "nearby", "nearest", "around here", "round here",
           "where i live", "gyms", "gym",
           # a place name or a dialling code is not the surface inside a shape
           "code", "codes", "dialling", "dialing", "zip", "51", "52", "area 51", "area 52",
           "place", "place name"),
    ask=_DEFINITION_ASK))


ENTRIES.append(entry(
    "perimeter-what",
    (("perimeter",), ("what", "mean", "meaning", "definition", "explain", "measured", "measure")),
    "The perimeter is the distance all the way round the outside of a shape, found by adding the "
    "lengths of its sides: a room 4 m by 3 m has a perimeter of 14 m. Area is the surface inside; "
    "the perimeter is the edge round it.",
    avoid=("of", "fence", "fencing", "security", "alarm", "guard", "patrol", "wall", "boundary",
           "camera", "sensor", "dog"),
    ask=_DEFINITION_ASK))


ENTRIES.append(entry(
    "variable-what",
    (("variable", "variables"),
     ("what", "mean", "meaning", "definition", "explain", "maths", "math", "algebra")),
    "In maths a variable is a letter standing for a number you do not know yet, or one that can "
    "change, such as x in 3x + 4 = 19. You work with it as if it were a number, then solve to "
    "find what it must be.",
    avoid=("weather", "speed", "wind", "temperature", "rate", "mortgage", "interest", "tariff",
           "energy", "salary", "income", "cost", "costs", "price", "prices", "mood", "quality",
           "signal", "power"),
    ask=_DEFINITION_ASK))


ENTRIES.append(entry(
    "probability-what",
    (("probability",), ("what", "mean", "meaning", "definition", "explain")),
    "Probability is how likely something is, written as a number from 0 (impossible) to 1 "
    "(certain): a fair coin landing heads has a probability of 1/2, or 50%. You find it by "
    "dividing the number of ways the thing can happen by the number of equally likely outcomes.",
    avoid=("of", "rain", "weather", "forecast", "rolling", "roll", "dice", "die", "coin",
           "cards", "lottery", "odds", "chance of"),
    ask=_DEFINITION_ASK))


ENTRIES.append(entry(
    "square-number-what",
    (("square number", "square numbers", "perfect square", "perfect squares"),
     ("what", "mean", "meaning", "definition", "explain")),
    "A square number is what you get when a whole number is multiplied by itself: 1, 4, 9, 16, "
    "25 and so on, because 4 × 4 = 16. It is called square because that many dots make a square "
    "grid, and it is always a whole number.",
    avoid=("metre", "meter", "foot", "feet", "mile", "room", "floor", "roof", "garden", "tile",
           "tiles", "root"),
    ask=_DEFINITION_ASK))


ENTRIES.append(entry(
    "numerator-denominator-what",
    (("numerator", "numerators", "denominator", "denominators"),
     ("what", "mean", "meaning", "definition", "explain", "fraction", "top", "bottom")),
    "In a fraction the numerator is the top number, the one being counted, and the denominator is "
    "the bottom number, the one that says how many equal pieces the whole is cut into. In 3/4 the "
    "numerator is 3 and the denominator is 4, so you have three of four equal pieces.",
    avoid=("lowest common denominator", "common denominator", "idiom", "politics", "tv",
           "television", "film", "music", "audience"),
    ask=_DEFINITION_ASK,
    bias=2))


# --- the next definitions a lesson asks for
MATHS_DEFINITION_ASK = ("what is", "what's", "what are", "what does", "what do", "how does",
                       "how do", "how is", "how are", "why is", "why are", "why does",
                       "explain", "tell me about", "define")


ENTRIES.append(entry(
    "angle-what",
    (("angle", "angles"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "number", "degrees", "degrees", "measure")),
    "An angle is the amount of turn between two lines that meet at a point, measured in degrees: a "
    "quarter turn is 90 degrees, a half turn 180 and a full turn 360. A right angle is exactly 90, an "
    "acute angle is less than that and an obtuse one is between 90 and 180.",
    avoid=("camera", "photo", "photos", "photography", "shoot", "shooting", "best",
           "wrong", "fishing", "fish", "park", "parking", "at an angle", "an angle on",
           "of a roof", "roof", "roofs", "roof pitch", "of a wall"),
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "integer-what",
    (("integer", "integers"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "number", "numbers", "whole")),
    "An integer is a whole number - positive, negative or zero - with no fraction or decimal part. "
    "So 4, -7 and 0 are integers, while 2.5 and 1/3 are not; the integers are the counting numbers, "
    "their negatives, and zero.",
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "power-maths-what",
    (("power", "powers", "power of", "exponent", "exponents"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "number", "numbers", "squared", "index")),
    "In maths a power tells you how many times to multiply a number by itself: 3 to the power 4 "
    "means 3 x 3 x 3 x 3, which is 81. The small raised number is the exponent and the number being "
    "multiplied is the base; a square is a power of 2 and a cube is a power of 3.",
    avoid=("electricity", "electric", "electrical", "solar", "nuclear", "wind", "battery",
           "outage", "cut", "cuts", "station", "plant", "political", "government", "prime",
           "minister", "president", "abuse", "corrupt", "money", "bank", "save", "saving"),
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "expression-maths-what",
    (("expression", "expressions", "algebraic expression"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "algebra", "number", "numbers", "equation")),
    "In maths an expression is a group of numbers, letters and operations with no equals sign, such "
    "as 3x + 4 or 2(a - b). It can be simplified or evaluated, but it is not a statement that two "
    "things are equal - that is an equation.",
    avoid=("facial", "face", "faces", "art", "artistic", "creative", "freedom", "gene", "genes",
           "protein", "protein expression", "emotional", "feelings", "yourself", "myself",
           "of interest", "expression of interest", "of concern", "letter"),
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "coefficient-what",
    (("coefficient", "coefficients"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "algebra", "number", "numbers", "letter", "variable")),
    "A coefficient is the number multiplying a letter in an expression: in 3x the coefficient is 3, "
    "and in -5y squared it is -5. If a letter stands alone the coefficient is 1, because x means 1x.",
    avoid=("drag", "lift", "friction", "correlation", "alpha", "beta", "regression"),
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "term-maths-what",
    (("term", "terms", "like terms"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "algebra", "expression", "equation", "number", "numbers", "add")),
    "In maths a term is one part of an expression, separated from the others by plus or minus signs: "
    "in 3x + 4y - 7 there are three terms, 3x, 4y and -7. Terms with the same letter part are like "
    "terms and can be added together, so 2x + 3x becomes 5x.",
    avoid=("school", "school term", "term dates", "dates", "contract", "lease", "insurance",
           "loan", "mortgage", "pregnancy", "pregnant", "fixed term", "long term", "short term",
           "terms and conditions", "conditions", "half term", "autumn", "spring", "summer",
           "of endearment", "endearment", "of office", "of address", "term of"),
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "symmetry-what",
    (("symmetry", "symmetrical", "line of symmetry", "lines of symmetry"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "shape", "shapes", "line", "mirror", "turn")),
    "Symmetry is when a shape or object looks the same after a fold, turn or flip. A line of "
    "symmetry divides a shape into two halves that are mirror images - a square has four, a circle "
    "has infinitely many - and rotational symmetry is how many times it matches in a full turn.",
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "polygon-what",
    (("polygon", "polygons"),
     ("what", "define", "definition", "mean", "meaning", "explain", "called", "maths",
      "mathematics", "shape", "shapes", "sides", "closed")),
    "A polygon is a closed flat shape made only of straight sides that do not cross. A triangle has "
    "3 sides, a quadrilateral 4, a pentagon 5 and a hexagon 6; a circle is not a polygon because its "
    "edge is curved.",
    ask=MATHS_DEFINITION_ASK))


ENTRIES.append(entry(
    "equation-what",
    (("equation", "equations"),
     ("what", "mean", "meaning", "definition", "explain", "difference", "expression")),
    "An equation says two things are equal, and the equals sign is the point: 3x + 4 = 19 is an "
    "equation. An expression such as 3x + 4 has no equals sign, so it can be simplified but not "
    "solved. Solving an equation means finding the number that makes both sides balance.",
    avoid=("solve", "solving", "work out", "find x", "value of x", "simultaneous", "quadratic",
           "rearrange", "balance", "check", "steps"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "algebra-what",
    (("algebra", "algebraic"),
     ("what", "mean", "meaning", "definition", "explain", "used", "use", "basic", "basics")),
    "Algebra is arithmetic with letters standing in for numbers, so a rule works for every number "
    "at once: if a notebook costs n pounds, three cost 3n. The letters are called variables, and "
    "the usual job is to rearrange an equation until the letter is alone.",
    avoid=("solve", "solving", "simplify", "factorise", "factorize", "expand", "rearrange",
           "brackets", "simultaneous", "quadratic", "worksheet", "homework", "test", "exam"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "ratio-what",
    (("ratio", "ratios"),
     ("what", "mean", "meaning", "definition", "explain", "difference", "proportion")),
    "A ratio compares two amounts by division, so a ratio of 2:3 means the second amount is one and "
    "a half times the first. A recipe using 2 cups of flour to 3 of milk is in the ratio 2:3, and "
    "scaling both numbers by the same amount keeps the ratio the same.",
    avoid=("how", "work out", "share", "sharing", "split", "divide", "simplify", "calculate",
           "smoothie", "coffee", "paint", "mortar", "concrete", "cement", "dough", "bread",
           "rice", "porridge"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "parallelogram-what",
    (("parallelogram", "parallelograms"),
     ("what", "mean", "meaning", "definition", "explain", "area", "shape")),
    "A parallelogram is a four-sided shape with both pairs of opposite sides parallel and equal, "
    "so its opposite angles are equal too. A rectangle is a special parallelogram with right "
    "angles. Its area is the base times the perpendicular height, not the slanted side.",
    avoid=("parking", "park", "car", "road", "drive", "space", "space-saving", "shelf"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "rhombus-what",
    (("rhombus", "rhombuses", "rhombi"),
     ("what", "mean", "meaning", "definition", "explain", "area", "shape", "diamond")),
    "A rhombus is a four-sided shape with all four sides the same length and both pairs of opposite "
    "sides parallel; a square is a rhombus with right angles, and a diamond shape is one too. Its "
    "area is half the product of its two diagonals.",
    avoid=("ring", "engagement", "wedding", "jewellery", "jewelry", "diamond", "carat",
           "brilliant", "mine", "stone", "ring size"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "trapezium-what",
    (("trapezium", "trapeziums", "trapezoid", "trapezoids"),
     ("what", "mean", "meaning", "definition", "explain", "area", "shape")),
    "A trapezium is a four-sided shape with exactly one pair of parallel sides; in the US the same "
    "shape is usually called a trapezoid. Its area is half the sum of the two parallel sides times "
    "the height between them.",
    avoid=("bone", "wrist", "hand", "thumb", "carpal", "table", "desk", "garden", "land"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "cube-what",
    (("cube", "cubes"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A cube is a solid with six square faces of the same size, twelve edges and eight corners: a "
    "sugar lump and a die are cubes. Its volume is the side multiplied by itself three times, so a "
    "2 cm cube holds 8 cm³, and its surface area is six times one face.",
    avoid=("ice", "ice cube", "stock", "stock cube", "bouillon", "sugar cube", "rubik",
           "rubik's", "puzzle", "cube steak", "cubicle", "van", "van hire", "storage",
           "packing", "freezer", "whisky", "whiskey", "drink", "number", "numbers"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "cuboid-what",
    (("cuboid", "cuboids"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A cuboid is a box shape with six rectangular faces, like a brick or a cereal box. Its volume "
    "is length times width times height, and a cube is the special cuboid where all three are equal.",
    avoid=("bone", "foot", "feet", "ankle", "toe", "wrist", "fracture", "tarsal"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "sphere-what",
    (("sphere", "spheres"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A sphere is the solid round shape where every point on the surface is the same distance from "
    "the centre, like a ball or a marble. Its volume is 4/3 times pi times the radius cubed, and "
    "its surface area is 4 times pi times the radius squared.",
    avoid=("public", "social", "political", "private", "influence", "sphere of", "work",
           "home", "life", "music", "fashion", "media", "online", "dyson"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "cylinder-what",
    (("cylinder", "cylinders"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A cylinder has two flat circular ends and one curved side, like a tin or a tube. Its volume "
    "is pi times the radius squared times the height, and the curved surface is 2 times pi times "
    "the radius times the height.",
    avoid=("gas", "oxygen", "gas bottle", "bottle", "lock", "brake", "hydraulic", "clutch",
           "engine", "boiler", "hot water", "mower", "car", "van", "propane", "butane",
           "co2", "compressed"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "cone-what",
    (("cone", "cones"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A cone has one circular base and a curved side that comes to a point, like a party hat or a "
    "road cone. Its volume is one third of the cylinder with the same base and height: 1/3 times "
    "pi times the radius squared times the height.",
    avoid=("ice cream", "pine", "waffle", "nose", "hedge", "plant",
           "flower", "evergreen", "fir", "eye", "retina"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "prism-what",
    (("prism", "prisms"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A prism is a solid with the same cross-section all the way along, like a triangular prism or "
    "a long box. Its volume is the area of that cross-section times the length. A cube and a "
    "cuboid are prisms too.",
    avoid=("political", "politics", "politic", "media", "public", "social", "through the prism", "prism of",
           "optics", "rainbow", "light", "camera", "lens", "glasses"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "pyramid-what",
    (("pyramid", "pyramids"),
     ("what", "mean", "meaning", "definition", "explain", "volume", "surface", "shape")),
    "A pyramid has a flat base and triangular faces that meet at a point above it; the base can be "
    "any polygon, and a square-based pyramid is the one people picture. Its volume is one third of "
    "the area of the base times the height.",
    avoid=("scheme", "schemes", "scam", "selling", "food", "diet", "egypt", "giza", "tomb",
           "pharaoh", "saqqara", "maya", "aztec", "chichen", "tour", "ticket", "hotel",
           "great pyramid", "pyramid of giza"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "vertex-what",
    (("vertex", "vertices"),
     ("what", "mean", "meaning", "definition", "explain", "corner", "edge", "edges")),
    "A vertex is a corner where two or more edges meet: a cube has eight vertices and a triangle "
    "has three. The plural is vertices, and in a graph a vertex is a point with lines, called "
    "edges, joining it to other points.",
    avoid=("shader", "graphics", "blender", "3d", "game", "engine", "computer", "software",
           "pharma", "pharmaceutical", "stock", "share", "nasdaq"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "cube-number-what",
    (("cube number", "cube numbers", "cubed number", "cubed numbers"),
     ("what", "mean", "meaning", "definition", "explain")),
    "A cube number is what you get when a whole number is multiplied by itself three times: 1, 8, "
    "27, 64, because 4 × 4 × 4 = 64. It is written 4³ and read as four cubed; a square number is "
    "the same idea with two multiplications.",
    avoid=("solid", "shape", "sugar", "ice", "stock", "dice", "die", "rubik", "box", "volume",
           "faces", "root"),
    ask=_DEFINITION_ASK,
    bias=3))


ENTRIES.append(entry(
    "range-maths-what",
    (("range",), ("what", "mean", "meaning", "definition", "explain", "maths", "math",
                  "statistics", "data", "numbers")),
    "In maths the range is the gap between the smallest and largest number: for 3, 7, 9 and 15 it "
    "is 15 - 3 = 12. Put the numbers in order first, then subtract the smallest from the largest.",
    avoid=("cooker", "oven", "hob", "car", "electric", "driving", "mile", "miles", "mountain",
           "golf", "shooting", "rifle", "archery", "price", "product", "salary", "age",
           "temperature", "tide", "wave", "frequency", "radio", "wifi", "signal", "exercise",
           "motion", "kitchen", "range hood", "free range", "range rover", "long range"),
    ask=_DEFINITION_ASK,
    bias=2))


ENTRIES.append(entry(
    "place-value-what",
    (("place value", "place values"), ("what", "mean", "meaning", "definition", "explain")),
    "Place value is what a digit is worth because of where it sits: in 4,582 the 4 is four "
    "thousands, the 5 is five hundreds, the 8 is eight tens and the 2 is two ones. The same digit "
    "means different things in different columns, which is why 0.5 is five tenths and 0.05 is five "
    "hundredths.",
    avoid=("parking", "park", "house", "market", "asset", "valuation", "property", "invest",
           "estate", "neighbourhood", "neighborhood", "area"),
    ask=_DEFINITION_ASK,
    bias=2))
