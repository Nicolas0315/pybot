"""Part 7 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

from ..knowledge.dishes import KEEP_QUALITY_WORDS
from ..knowledge.keeping_cooked import COOKED_KEEP_ASK, COOKED_KEEP_AVOID, COOKED_KEEPS
from ..knowledge.lookup import (
    entry, kinds_entries, says_it_has_gone_off as _says_it_has_gone_off, TOOTH_OR_GUM,
)
from ..knowledge.meals import says_a_diet as _says_a_diet
# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.units import people_in_groups
from ..knowledge.cooking_tables import (
    NOT_WANTED, MEAL_IDEAS, FOOD_CALORIES, FOOD_NUTRIENTS, FOOD_CALORIE_MEALS, BAKES, KEEPS, PANTRY,
    DISHES, RECIPES,
)
from .cooking_part_01 import (
    BASICS, _BODY_TOO_THICK, _BODY_TOO_THIN, _TOO_THICK_SAID, ADULT_VEG, KIDS_VEG, _about_a_child,
    _the_veg_card_was_just_said, KNOWS_READY, NOT_A_METHOD, _done_words, _harvest_crops,
    _AN_APPLIANCE, _an_appliance_has_the_line, _spelled_counts, _CROWD_PHRASES, _people_after,
    _TABLE_PHRASES, _CROWD_FOOD, _CROWD_QUANTITY, _CROWD_VERBS, _a_seasoning, _bird_weight,
    _hours_words,
)
from .cooking_part_02 import (
    _CROWD_NOT_A_MEAL, _occasion, _plan_side, _table_side, ANY_MEAL, TIME_MIDDLING, TIME_SOON,
    TIME_TWENTY, _minutes_named, PLAN_BATCH, PLAN_CHEAP, PLAN_WEEK, _BAKED_GOODS, _CAKE_NAMES,
    _same, DIABETIC_PLATE, _says_diabetes,
)
from .cooking_part_03 import (
    _FROZEN_CUTS, _FROZEN_WHOLE, _FROZEN_MANY, _FROZEN_ONE, _FROZEN_WHAT, _frozen_from_the_bag,
    KEEPING_SENSE, _BOLOGNESE_WORDS, FOOD, _list_words, _NOT_LACTOSE_WORDS, _a_lactose_intolerance,
    _said_so_far, _their_diet_is_a_lactose_intolerance, _the_guest, FISH_SPLIT,
    NOT_SETTLED_BY_THE_RECIPE,
)
from .cooking_part_04 import (
    _LACTOSE_SAYS, _PLANT_NOT_A_DINNER, _PLANT_BEARS, _PLANT_COOK_ASK, _PLANT_DO_WITH,
    _PLANT_GARDEN_VERB, _PLANT_KITCHEN_PLANT, _a_plant_from_the_shop, _the_garden_has_this_plant,
    _FEEDING_ANIMALS, FEEDING_NOT_FOOD, PET_MEAT_ANIMALS, PET_NOT_FOOD, _pet_not_dinner,
    PET_ANIMALS, PET_CARE, PET_COOKING_ASK, _a_brew_not_a_dinner, _bans, ANY_BREAKFAST,
    BREAKFAST_TAIL, ANY_LUNCH, FREEZE_ANY, _a_freeze_fact, _points_at_something,
    _the_dish_the_chat_names, ALSO_OUT, _HAVE_NONE, _NUTRIENT_WORDS, NUTRIENT_COLUMNS,
    NUTRIENT_CONTEXT, _CALORIE_PLURAL, _PROTEIN_SHARES, _figure, _nutrient_asked, _nutrient_food,
    _plurals, _portion_size, _weight_in_the_line, CALORIE_ASKS, _CALORIE_DISH, _CALORIE_JOIN,
    _CALORIE_NOT_A_DISH, _CALORIE_OWN, _names_a_food, _the_food_named_by_a_slip, GLUTEN_FACT_DIET,
    GLUTEN_FREE_ASKS, GLUTEN_FACT_NAMED_SWAP, GLUTEN_FACT_NOT_PLAIN, LACK_HEADS, LACK_NOUNS, LACKS,
    _line, _says_gone, _GRIDDLE_BATTER, _GRIDDLE_DOUGH, _GRIDDLE_WARM, _GRIDDLE_TAIL, NO_BAKING,
    NO_OVEN_BREAD, NO_HOB, NO_KETTLE, NO_OVEN, _asks_vegan, SUBSTITUTE_PHRASES,
)
from .cooking_part_05 import (
    _words_and_text, PUDDING_IDEAS, COOKING_ASKS, HAVE_ONE, LISTING, NO_MICROWAVE, NO_OVEN_ONLY,
    ONLY_ONE, available, COOK_WORDS, DEFINITION_WORDS, _cook_word_hit, _names_a_subject,
    _ALREADY_BAKED_PHRASES, _NO_YEAST, _TIMING_ASKS, TEA_CLOUDY_TEXT, TEA_FAULT_TEXT,
    TEA_GREEN_TEXT, TEA_ICED_TEXT, TEA_METHOD_TEXT, TEA_POT_TEXT, TEA_TWICE_TEXT, _BURNT_BATTER,
    _BURNT_BATTER_REPLY, _BURNT_DISH_REPLY, _BURNT_EATING_ASK, _BURNT_EATING_REPLY, _BURNT_MEAT,
    _BURNT_MEAT_REPLY, _BURNT_VEG, _BURNT_VEG_REPLY, _PAN_DISH, _PAN_WORDS, _ROAST_PARTS,
    _ROAST_PART_REPLY, _TIN_OR_OVEN, _says, _BAKED_BURNT, _BAKE_BOTTOM_REPLY, _BAKE_BURNT,
    _BAKE_NOUNS, _BAKE_PREVENTION, _burnt_on_the_pan,
)
from .cooking_part_06 import (
    _recent_user_turns, LEFTOVER_PHRASES, MEAL_ASK_PHRASES, NOT_THIS_FOOD, _ONTO_A_PERSON,
    OIL_SMOKE_POINTS, _SOMETHING_IS_WRONG_WITH_THE_PAN, _a_dish_with_a_heat, _SOGGY_BREAD,
    _SOGGY_LEAF, KEEP_DATE_WORDS, MOULD_WORDS, _SPOILT_WORDS, LEFTOVER_IDEAS, LEFTOVER_SOUP,
    FOOD_SAFETY_RULES, _plain_words, FORM_ADVICE, FORM_FOODS, FROZEN_FRUIT, FROZEN_MEAT, OUT_ASKS,
    OUT_OF_FORM, REFUSAL_REACH, RULING_OUT_PHRASES, DIETS, _READ_FOR_INGREDIENTS,
    _READ_FOR_INGREDIENTS_KEEP, NEGATION_REACH, FOOD_CLASSES, COOKED_REACH, _VEG_DINNER,
    _VEG_DINNER_CHEAP, _VEG_PHRASES, _CHOICE_WORDS, _COOKING_MEDIUM, ACTIVITY_PHRASES,
    BOUGHT_PHRASES, EMPTY_ASK_PHRASES, EMPTY_KITCHEN, EMPTY_PHRASES, ILLNESS_PHRASES, LEFT_POINTER,
    MAKING_IT_YOURSELF_PHRASES, MEAL_PHRASES, MEAT_SWAPS, PLANT_MILKS, PROBLEM_PHRASES,
    RESTRICTED_EATING, USE_UP_ASKS, _USE_UP_WORDS, _reads_as_news, _NUMBER_WORD, _RECIPE_ANSWERS,
    _this_line_only, POINT_BACK_STOP, _words_of, PAIRING_WORDS, POINT_BACK, SECOND_IDEA, SCALE_DOWN,
    SCALE_UP, SCALE_UP_WORDS,
)


_STAPLE_NAMES = tuple(name for _names, _reply in BASICS for name in _names)


# "how do i cook" is in the learner's key below, and the phrase is the whole of "how do i cook
# potatoes", "how do i cook pasta" and "how do i cook chard": the four-things card then answered a
# hundred lines that name a food, ahead of the row that knows the food. Those lines are the food's
# own question, so the card stands down when the line names one of the things the pantry and the
# staples tables already answer, and keeps the lines it was written for - "how do i learn to
# cook", "where do i start cooking", "how do i cook from scratch", "how do i cook for my family".
# The food names are read from the tables when the line arrives, because they are written below
# this entry.
def _learn_to_cook(memory, understood):
    said = {_fold(str(word).lower()) for word in (understood.get("words") or ())}
    # The tables are folded the same way the line is, and not before _fold is defined, which is
    # further down this file: "how do i cook ribs" arrived as "rib" and the pantry lists "ribs",
    # so 133 of the food names - ribs, carrots, apples, chickpeas, oats, chicken breasts - never
    # fired this stand-down and the beginner's card answered a dish's own question.
    if said & _foods_said():
        return None
    return ("Learn four things and the rest follows: pasta with a sauce, an omelette, a tray of "
            "roasted vegetables, and a one-pot curry or stew. Cook the same one twice in a week "
            "rather than a new one each night, and taste as you go - food that tastes flat "
            "usually wants salt, a squeeze of lemon, or more time in the pan. A cheap "
            "thermometer takes the fear out of chicken and pork.")


# The dish word can also be the food the staple is made into or served as: cauliflower rice,
# sushi rice, paella rice, an overnight oats pot, rice krispie cakes, a rice bowl. Each of those
# is its own answer, and a staple method given for one of them is a confident wrong answer.
DISH_BEFORE = frozenset("sweet fried roast roasted baked mashed creamed scalloped glazed "
                        "cauliflower sushi paella overnight egg fried".split())


DISH_AFTER = frozenset("pudding salad bake gratin pie bread cake cakes balls bolognese cheese "
                       "curry soup stew krispie crispy noodle noodles bowl paper wrap sushi "
                       "ball bite finger patty".split())


def _body(memory, understood):
    """Which way the pot is wrong, so the reply leads with the fix the person asked for."""
    said = " " + " ".join(_fold(str(word)) for word in (understood.get("words") or [])) + " "
    thickening = "thicken" in said or "thicker" in said or "thickening" in said
    complaining = any(shape in said for shape in _TOO_THICK_SAID)
    if complaining and not thickening:
        return _BODY_TOO_THICK
    return _BODY_TOO_THIN


def _more_veg(memory, understood):
    """The same question from a parent gets the feeding answer, not the adult portions one."""
    if not _about_a_child(memory, understood):
        return ADULT_VEG
    return None if _the_veg_card_was_just_said(memory) else KIDS_VEG


# A portion question and a timing question both start with "how much" or "how many": "how much
# rice do i need for four people" is the portion table's, and "how many minutes per side for pork
# chops" is this row's own. The avoid list used to hold the two bare words, so the timing question
# was stood down as well and got a shrug while the same line with "how long do i cook" in it was
# answered. A how-much ask that names a time or a heat is a method question, so the row keeps it.
_A_HEAT_OR_TIME = re.compile(
    r"\b(minutes?|mins?|minutes'|hours?|hrs?|seconds?|degrees?|celsius|fahrenheit|gas mark|"
    r"temp|temperature|oven)\b|\bhow long\b")


_A_HOW_MUCH = re.compile(r"\bhow (much|many)\b")


# "a side" is a face of the meat once the line names a time ("3 minutes a side"), and the rest of
# the plate when it does not ("what side with steak", "any sides for a roast").
_A_SIDE_SAID = re.compile(r"\bsides?\b")


def _not_a_portion_ask(understood):
    """False when a "how much" line asks an amount, or a "side" line means the plate."""
    text = str(understood.get("clean") or understood.get("norm_text")
               or " ".join(understood.get("words") or [])).lower()
    if _A_HOW_MUCH.search(text) and not _A_HEAT_OR_TIME.search(text):
        return False
    if _A_SIDE_SAID.search(text) and not _A_HEAT_OR_TIME.search(text):
        return False
    return True


def _staple(memory, understood):
    """How to cook the everyday staple the line names, or nothing when it names none."""
    from ..knowledge import cooking

    said = [_fold(str(word).lower()) for word in (understood.get("words") or [])]
    joined = " " + " ".join(said) + " "
    for phrase in NOT_A_METHOD:
        if phrase in joined:
            return None
    if any(phrase in joined for phrase in KNOWS_READY):
        # The words that make it a pan question after all: "how do i know when my carrots are
        # done" is a cook asking for the time, and the harvest rows stand down for it (their
        # avoid list carries the same words), so this method has to answer it.
        done = _done_words()
        if not any(" %s " % word in joined for word in done):
            _harvest = _harvest_crops()
            if any(" %s " % crop in joined for crop in _harvest):
                return None
    # cooking_entries extends the facade's table during import.
    for names, reply in cooking.BASICS:
        for name in names:
            parts = [_fold(piece) for piece in name.split()]
            size = len(parts)
            for start in range(len(said) - size + 1):
                if said[start:start + size] != parts:
                    continue
                before = said[start - 1] if start else ""
                after = said[start + size] if start + size < len(said) else ""
                if before in DISH_BEFORE or after in DISH_AFTER:
                    continue
                # "how do i make a sauce for pasta" wants a sauce, not how to boil pasta:
                # the two sauce rows are named, so a bare sauce word stands this one down
                if name not in ("white sauce", "cheese sauce", "bechamel", "béchamel") and (
                        "sauce" in said or "saucy" in said):
                    continue
                # a guard word counts either side of the staple's name: "lamb chops" puts the
                # cut after the meat, and "onions smell in the fridge" puts the problem after it
                rest = said[:start] + said[start + size:]
                # the row's own name carries the guard, so "onion" and "onions" are one row
                guards = NOT_WANTED.get(names[0], ())
                if name != names[0]:
                    guards = guards + NOT_WANTED.get(name, ())
                # The row's own words are a case it already answers, so a guard that the answer
                # itself says is not a reason to stand it down: the lamb shank row gives the
                # slow cooker time for a shank, and "can i do it in a slow cooker" after "how do
                # i cook a lamb shank" wants that row, not its own "slow cooker" guard.
                own = _fold(reply.lower()) if isinstance(reply, str) else ""
                if _a_guard_said(rest, joined, guards, own):
                    continue
                # A staple whose method depends on the equipment the line names answers as a
                # function of the line; the plain rows are strings and are returned as they are.
                return reply(understood) if callable(reply) else reply
    return None


def _a_guard_said(rest, joined, guards, own=""):
    """Whether the line carries one of a row's guard words, or one of its guard phrases.

    A single word is read either side of the staple's name ("onions smell in the fridge", "the
    smell of onions"), because it belongs to the staple. A phrase is read across the whole line,
    because its words can sit on both sides of the name: "how many lamb chops per person" has
    "how many" before the name and nothing of it in `rest`. Every phrase in these tables was
    checked one word at a time, so none of them ever fired, and the rows they were written for
    answered lines they were meant to stand down for.
    """
    for guard in guards:
        if " " in guard:
            phrase = _fold(guard)
            if phrase in joined and phrase not in own:
                if guard not in _AN_APPLIANCE or not _an_appliance_has_the_line(joined):
                    return True
        elif guard in rest:
            return True
    return False


# "chicken tender" is two senses: the piece, which has an oven time, and the texture of the
# meat ("how do i make my chicken tender"), which has none. The plural, or the piece named on
# its own, is the piece; "tender" standing after "my", "so" or "is" is the adjective.
TENDER_ADJECTIVE_BEFORE = frozenset(("my", "so", "really", "very", "more", "most", "too", "not",
                                     "is", "super", "nice", "them", "properly", "and", "are"))


def _tenders_are_a_piece(understood):
    """True when the line asks about the piece, false when it says tender as a texture."""
    words = [w.lower() for w in (understood.get("words") or []) if isinstance(w, str)]
    if "tenders" in words or "strips" in words or "goujons" in words:
        return True
    for i, word in enumerate(words):
        if word == "chicken" and i + 1 < len(words) and words[i + 1] in ("tender", "strip",
                                                                        "goujon"):
            before = words[i - 1] if i else ""
            return before not in TENDER_ADJECTIVE_BEFORE
    # no piece word at all: "how do i cook beef so it is tender" says tender about the meat
    return False


# What to put *on* the meat rather than beside it. "What goes with lamb" is the sides table, but
# "what spice goes with lamb" and "seasoning for lamb" were answered with new potatoes and mint -
# the rest of the plate - and "what spice for beef" with a shrug. The line asks about the herbs and
# spices, so the same entry answers with those instead. Ordered most specific first, and read by
# the longest name in the line, the way the sides table is.
# A bare "season" is not enough: a season is episodes, a league and the close season for fishing.
# "what is the close season for fishing" reached this table, read "fish" and answered with lemon
# and dill instead of the rod licence, so the verb is what the season has to be - season a chicken,
# season it, seasoned - and the noun "seasoning" carries the rest.
SEASONING_ASKS = re.compile(
    r"\b(?:spices?|herbs?|seasoning|flavours?|flavors?|rub|marinade)\b"
    r"|\bseason(?:ed)?\s+(?:a|an|the|it|them|my|your|with|before|after|well|up)\b"
    r"|\bhow\s+(?:do|to|should)\s+(?:i|you)\s+season\b"
    r"|\bput\s+on\b")


# The ways a line asks about the rest of the plate rather than about the dish itself.
SIDE_ASKS = re.compile(
    r"\b(?:go|goes|going|went)\s+(?:well\s+|nicely\s+|best\s+)?with\b"
    r"|\b(?:what|which)\s+(?:side|sides)\b"
    r"|\bside\s+(?:dish|dishes|for|to)\b|\bsides\s+(?:for|to|with)\b"
    r"|\bserve\s+(?:it\s+|them\s+|this\s+)?with\b|\bserving\s+with\b"
    r"|\bto\s+serve\s+with\b|\balongside\b|\bon\s+the\s+side\b"
    r"|\bpairs\s+with\b|\bwhat\s+(?:can|should)\s+i\s+(?:have|serve)\s+with\b")


_CROWD_NUMBERS = _spelled_counts()


# Longest first, so "thirty five" is read before "thirty".
_CROWD_SPELLED = "|".join(sorted(_CROWD_NUMBERS, key=len, reverse=True))


_CROWD_FOR = re.compile(r"\bfor\s+(" + _CROWD_SPELLED + r")\b")


_CROWD_WITHIN = re.compile(r"\b(" + _CROWD_SPELLED
                           + r")\s+(?:people|of us|adults|guests|coming)\b")


def _crowd(text):
    """How many people the line is cooking for, or 0 when it is an ordinary dinner."""
    text = str(text or "").lower().replace("-", " ")
    numbers = [int(match.group(1)) for match in re.finditer(r"\bfor\s+(\d{1,3})\b", text)
               if _people_after(text, match.end())]
    numbers += [_CROWD_NUMBERS[match.group(1)] for match in _CROWD_FOR.finditer(text)
                if _people_after(text, match.end())]
    # "eight people coming", "ten of us", "twelve guests": the count is in the line even when
    # nobody says "for".
    numbers += [_CROWD_NUMBERS[word] for word in _CROWD_WITHIN.findall(text)]
    # The same count typed as a number: "theres 14 of us for dinner", "12 people coming".
    for count in re.findall(r"\b(\d{1,3})\s+(?:people|of us|adults|guests|coming)\b", text):
        numbers.append(int(count))
    # Every group of people the line names adds up: "with 4 adults and 3 kids" is seven at the
    # table, and counting only the adults put the shopping 600 g short. The reader is the
    # portion maths' own, so a count answers the same whoever asks about it.
    grouped = people_in_groups(text)
    if grouped:
        numbers.append(grouped)
    if numbers:
        return max(numbers)
    if any(phrase in text for phrase in _CROWD_PHRASES):
        return 6
    return 0


# A table named by the people at it, not counted: "i'm cooking for my in laws on sunday" is the
# same dinner-for-a-table question as "i'm cooking for eight", and the reason to ask it is that
# people who are not your household are coming. It is the relation after "for" that says so, so
# a bare "cooking for one" and "cooking for the dog" stay out of it.
_NAMED_TABLE = re.compile(
    r"\b(?:cook|cooking|cooked|make|making|made|bake|baking|hosting|having|feed|feeding)\b"
    r"[^.?!]{0,24}\b(?:for|to)\s+(?:my|our|the|his|her|their)\s+(?:\w+'?s\s+)?"
    r"(?:in\s?laws?|parents?|mums?|moms?|mothers?|dads?|fathers?|folks|familys?|relatives?|"
    r"friends?|neighbou?rs?|guests?|colleagues|workmates|sisters?|brothers?|grandparents?)\b"
    r"|\b(?:my|our)\s+(?:\w+'?s\s+)?(?:in\s?laws?|parents?|mums?|moms?|mothers?|dads?|"
    r"fathers?|folks|familys?|friends?|neighbou?rs?|grandparents?)\b[^.?!]{0,24}"
    r"\b(?:coming|come|round|over|visiting|staying)\b[^.?!]{0,18}"
    r"\b(?:dinner|lunch|tea|supper|meal|eat)\b",
    re.IGNORECASE)


def _named_table(text):
    """True when the line names the people it is cooking for, instead of a number."""
    return bool(_NAMED_TABLE.search(str(text or "")))


def _table_text(text):
    """True when the line is about feeding a table rather than one plate.

    Eight or more is a crowd on the number alone. Four or five is a table only when the line says
    people are coming and asks what to cook - "i have 4 people coming for dinner what should i
    cook" wants the one-dish answer, while "dinner for four" is an ordinary dinner.
    """
    text = str(text or "").lower()
    count = _crowd(text)
    if count >= 6:
        return True
    if not count:
        # "i'm cooking for my in laws on sunday" counts nobody, and is still a table.
        return _named_table(text)
    # Three to five is a table when the line says people or guests are coming round, in either
    # of the two ways the module already knows ("people coming", "dinner party"): the count was
    # read as four and then stood down to the ten-minute list, which is the wrong card for four
    # people somebody is cooking for.
    # "of us" is a table counted by the people at it: "whats a good lunch for 4 of us" and
    # "lunch for 3 of us" are not one person's lunchbox, and with the lunchbox row standing down
    # for them there was nothing else to take the line. It is read here, where the count is
    # known, and not in _CROWD_PHRASES: that list is also the default six for a line with no
    # number, and a table of four counted as six was handed the six-player games.
    if count >= 3 and any(phrase in text for phrase in _CROWD_PHRASES + ("of us",)):
        return True
    if any(phrase in text for phrase in _TABLE_PHRASES) and any(
            word in text for word in ("cook", "cooking", "make", "feed", "serve")):
        return True
    # The ask can be a lunch as readily as a dinner: "whats a good lunch for 4 of us" names no
    # word of cooking at all, and with the lunchbox row standing down for the count of us it
    # reached nothing until the meal itself counted as the ask. Three or more, because "lunch
    # for 2 of us" is a sandwich apiece and not a dish to cook for a table.
    return (count >= 3 and any(phrase in text for phrase in _TABLE_PHRASES)
            and any(word in text for word in ("lunch", "lunches", "meal", "meals", "eat")))


def _crowd_ask(clean):
    """True for a how-to line that is really a dinner for a table.

    "how do i cook for a crowd" is a how-to in form and a dinner question in substance: at a
    table of eight the question is what to cook, not which pan to use. A line that only states
    the table ("i have 12 people over for dinner") asks it too, so dinner and tea count here.
    """
    text = str(clean or "").lower()
    if not _table_text(text):
        return False
    if any(word in text for word in _CROWD_VERBS):
        return True
    if any(phrase in text for phrase in _CROWD_NOT_A_MEAL):
        return False
    if any(word in text for word in _CROWD_FOOD):
        return not any(phrase in text for phrase in _CROWD_QUANTITY)
    return False


_CROWD_WORDS = {v: k for k, v in _CROWD_NUMBERS.items()}


def _trays(count):
    """How many trays the table needs, so a table of twelve is not told about eight."""
    if count >= 13:
        return ("two or three trays of it, on the top and middle shelves, or one dish made in "
                "the biggest pot you own")
    if count >= 9:
        return ("two trays of it, on the top and middle shelves and swapped halfway, to feed "
                + _CROWD_WORDS.get(count, str(count)))
    if count and count <= 5:
        # A table of four is one tray with plenty left over, and telling them it "feeds eight"
        # reads as though nobody read the number in the line.
        return ("one tray of it is plenty for " + _CROWD_WORDS.get(count, str(count)))
    if not count:
        # A table named by its people ("cooking for my in laws") carries no number, so claim
        # none: "feeds eight" to two guests reads as though nobody read the line.
        return "which does four to six, so count the potatoes yourself"
    return "which feeds eight from one oven"


def _crowd_meal(banned, occasion, count=0):
    """One dish that scales, for a birthday or a table of eight, instead of a ten-minute dinner."""
    vegetarian = bool({"meat", "chicken", "beef", "pork", "lamb", "mince", "bacon",
                       "sausage", "sausages", "ham", "turkey", "fish", "salmon", "cod",
                       "tuna", "prawn", "prawns"} & banned)
    if vegetarian:
        # "a big lasagne" to a vegetarian is a dish of unknown filling: name the meat-free one
        dish = ("a big mushroom and lentil lasagne or a chickpea and vegetable traybake, made in "
                "the largest dish you own")
        amount = "about 300g of the dish per person"
    else:
        dish = ("a tray of chicken thighs or sausages with halved potatoes, peppers and onions at "
                "200C (180C fan) for 45 minutes")
        amount = "about 200g of meat and a big potato each"
    reply = ("Cook one big oven dish rather than several pans: " + dish + ", " + _trays(count)
             + ". Allow " + amount + ", add a loaf of bread and a bowl of salad, and write the "
             "times down so nothing needs the oven at once.")
    if occasion:
        reply += (" Anything that can be made that morning - a chilli, a stew, a lasagne - just "
                  "gets reheated, which leaves the day free.")
    return reply


def _crowd_or_any(text, banned):
    """The fallback list, unless the line is a meal for a table or an occasion."""
    if _table_text(text):
        return _crowd_meal(banned, _occasion(text), _crowd(text))
    if _occasion(text) and any(
            phrase in text for phrase in ("what should i cook", "what can i cook",
                                          "what shall i cook", "what to cook", "what to make",
                                          "meal", "dinner", "cook", "no idea")):
        # "it's my mum's 70th birthday, what should I cook" names no ingredient and no number:
        # a ten-minute dinner is the wrong answer to a day like that.
        return _crowd_meal(banned, True, _crowd(text))
    return _any_meal(banned)


# "How many minutes a side for steak" is a timing question that happens to say "a side", and the
# pair row's key holds the phrase "side for": steak, pork chops and chicken were all answered with
# what to serve beside them when they asked how long to cook. A line that asks a time or a heat is
# the timings' question, so the pair row stands down for it.
A_TIME_OR_HEAT_ASK = re.compile(
    r"\b(how many minutes?|how many mins?|how long|how much time|minutes a side|mins a side|"
    r"minutes per side|what temperature|what temp|what heat|gas mark|how do i time)\b")


def _sides(memory, understood):
    """What to put beside the dish a line names, or None when it names none I know."""
    text = str(understood.get("clean") or " ".join(understood.get("words") or [])).lower()
    # "a pain in my side" and "side effects" are not about the plate.
    if re.search(r"\bpain\b|\bstitch\b|\bside effects?\b|\bleft side\b|\bright side\b", text):
        return None
    # "how many minutes a side for steak" is a time, not the rest of the plate.
    if A_TIME_OR_HEAT_ASK.search(text):
        return None
    # "what spice goes with lamb" is the herbs, not the new potatoes: the same entry, told which
    # of the two questions it is answering.
    if SEASONING_ASKS.search(text):
        seasoned = _a_seasoning(text)
        if seasoned:
            return seasoned
    table = _table_side(text)
    plan = _plan_side(memory, text)
    # The plan names the one dish the line is about, so its side answers first: the table reads
    # the first food word it finds, and a bare "chicken" in it was handing "what goes with a
    # chicken curry" the roast chicken's potatoes. A line whose dish has no plan, or whose plan
    # has no side, falls through to the table.
    if plan:
        return plan[1]
    if table:
        return table[1]
    # A pairing ask about a food with no dish of its own and no side in the table is not a punt:
    # "what goes with cheese", "what goes with penne", "what cheese goes with apple" and "what
    # sauce goes with lentils" were four "I'd rather not guess" lines, and the rule underneath
    # the tables is the answer - fat wants acid, plain starch wants something wet on top, and
    # anything else wants one of each.
    from ..knowledge import dishes
    if dishes.asks_for_a_side_of_a_food(text):
        return dishes.general_sides(text)
    return None


# A month named in the line does not make it a holiday: "cheap meals for a week in january" is
# the new-year meal plan and "a week in spain in october" is a holiday, and the word that differs
# is a meal word, not a place. So the twelve months stand this row down only when the line names
# nothing to eat, which is the shape of a line that is asking where to go.
MONTHS_SAID = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november"
    r"|december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec)\b")


# A line that asks where to go is asking about a place, not a shop - unless the place it names is
# a shop for food: "where can i go for cheap food" came back with this row's eight cheap foods, and
# standing the row down on the phrase alone turned a shopping answer into a search hedge.
GOING_SAID = re.compile(
    r"\bwhere (?:should|can|could|shall|do|to) (?:i|we)? ?(?:go|get|find|shop)\b"
    r"|\bwhere to (?:go|shop)\b|\bweeks? abroad\b")


# The words that say the week is about eating: the plural is undone by _fold, so the singulars
# are enough here.
EATING_WORDS = frozenset("meal dinner cook cooking eat eating food shop shopping menu recipe "
                         "supper lunch tea feed leftover batch portion".split())


PLAN_WORDS = frozenset("batch batches batchcook freezer freeze freezing portion portions".split())


CHEAP_PLAN_WORDS = frozenset("cheap cheapest skint budget broke money afford tight".split())


TONIGHT_WORDS = frozenset("tonight tonite tnite today now".split())


def _time_budget(memory, understood, text=None):
    """What fits in the minutes the line gives itself, or None when it names no hurry."""
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    said = " ".join(_fold(word) for word in words)
    minutes = _minutes_named(said)
    if minutes is None:
        return None
    if minutes <= 15:
        return ANY_MEAL
    if minutes <= 22:
        return TIME_TWENTY
    if minutes <= 28:
        return TIME_SOON
    if minutes <= 90:
        return TIME_MIDDLING
    return None


# A fruit on its way out is still this row's question when the line names the oven: "i have four
# peaches going soft, how long do they need in the oven" wants the minutes, not the case for
# eating a soft one. The soft words were in the avoid list on their own, which stood the row down
# for the very line that was asking it.
_SOFT_FRUIT = re.compile(r"\b(?:going soft|gone soft|soft spot|soft spots|getting soft|"
                         r"turning soft)\b")


_SOFT_FRUIT_WANTS_THE_OVEN = re.compile(
    r"\b(?:oven|bake|baked|baking|roast|roasted|roasting|stew|stewed|stewing|poach|poached|"
    r"poaching|microwave|microwaved|use up|using up|what can i do with|what can i make with|"
    r"what do i do with)\b")


def _a_soft_fruit_is_still_a_cooking_question(understood):
    """False for a soft fruit asked about keeping, true once the line names a way of cooking it."""
    text = str((understood or {}).get("clean") or "").lower()
    return bool(_SOFT_FRUIT_WANTS_THE_OVEN.search(text)) or not _SOFT_FRUIT.search(text)


def _meal_plan(memory, understood):
    """A week of dinners, a cheap week, or a batch cook, from the same three replies.

    "meal plan for the week" names nothing in the kitchen, so the pantry has nothing to build
    from; what the line wants is the shape of the week. The words that say which shape it wants
    are cheapness and the freezer, and both are read with the turns before this one, because
    "im skint this week" then "what should i plan for dinners" is still a cheap week.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    text = " ".join([str(understood.get("clean") or "").lower()] + _recent_user_turns(memory))
    folded = [_fold(word) for word in words]
    # Cheapness carries over the way "batch" does: "im skint this week" then "what should i plan
    # for dinners" is still a cheap week, and the plan for one is a different list of dinners.
    said = folded + [_fold(word) for word in re.findall(r"[a-z']+", text)]
    # A month with nothing to eat in the line is a holiday: "where should i go for a week in
    # october on a budget" came back with the eight cheap foods. The same line with a meal word
    # in it - "cheap meals for a week in january" - is the meal plan said with a month in it.
    if ((MONTHS_SAID.search(text) or GOING_SAID.search(text))
            and not set(said).intersection(EATING_WORDS)):
        return None
    if any(word in PLAN_WORDS for word in said) or re.search(r"\bfreez|\bbatch", text):
        return PLAN_BATCH
    if any(word in CHEAP_PLAN_WORDS for word in said):
        return PLAN_CHEAP
    return PLAN_WEEK


_NO_SPREAD_RISE = tuple(name for name in _BAKED_GOODS
                        if name not in ("cookie", "cookies", "biscuit", "biscuits", "shortbread"))


_NO_CAKE_RISE = tuple(name for name in _NO_SPREAD_RISE if name not in _CAKE_NAMES)


_NO_LOAF_RISE = tuple(name for name in _NO_SPREAD_RISE
                      if name not in ("loaf", "loaves", "bun loaf"))


_FROZEN_CUT_WORDS = tuple(_FROZEN_CUTS[0]) + tuple(word for word, _, _ in _FROZEN_WHOLE)


def _frozen_cook_reply(understood):
    text = " ".join(str(understood.get("clean") or "").lower().split())
    words = text.split()
    if not any(cut in words for cut in _FROZEN_CUT_WORDS):
        # "can i just cook it from frozen" names no meat: the cut is in the turn before ("i
        # forgot to defrost the mince"). Naming it back is the whole point of the reply, so the
        # meat the line leans on is read as if it had been said here, and only the cut words
        # are taken from it - "it" leaning on a defrost is not a chop.
        lean = understood.get("leans_on")
        if isinstance(lean, dict):
            subject = str(lean.get("subject") or "").lower().split()
            words = words + [word for word in subject if word in _FROZEN_CUT_WORDS]
    if any(cut in words for cut in _FROZEN_CUTS[0]):
        led = ("Mince can go straight into the pan from frozen: brown it over a high heat, "
               "break it up as it loosens and give it a few extra minutes before the sauce goes in.")
    else:
        said, one = next(((said, one) for word, said, one in _FROZEN_WHOLE if word in words),
                        ("", False))
        if said:
            led = (_FROZEN_ONE if one else _FROZEN_MANY).format(said)
        else:
            led = ("Usually yes for small cuts - mince, sausages, bacon, chops: they can go "
                   "straight into a hot pan or a sauce from frozen, a few minutes longer than "
                   "thawed and piping hot all the way through.")
    return led + (" A whole bird or a big joint is the exception: it has to thaw first, or the "
                  "outside overcooks while the middle stays raw. Do not refreeze it once it has "
                  "started to thaw.")


def _meat_defrost(memory, understood):
    """A whole bird or a big joint needs a day or two; mince and sausages need overnight."""
    text = " ".join(str(understood.get("clean") or "").lower().split())
    if any(word in text for word in _FROZEN_WHAT) and any(
            word in text for word in ("frozen", "freezer")):
        # "what can i cook from frozen" wants a meal, and the meal answer it had on main ("Quick:
        # tuna pasta in 15, a frittata in 20") is better than the thaw times. The entry declines
        # the line so the meal entry below it gets the turn.
        return None
    if _frozen_from_the_bag(understood):
        return _frozen_cook_reply(understood)
    # A small cut named in the line wins over "joint": the composer re-asks a line like "how long
    # does it take to thaw 500g of mince" as "... for the joint?" and the answer has to stay mince.
    small = ("mince", "sausage", "sausages", "chop", "chops", "steak", "steaks", "bacon",
             "liver", "kidney", "kidneys")
    if not any(word in text for word in small) and ("turkey" in text or "bird" in text):
        # The figure first and inside its own sentence: the composer hands a time follow-up the
        # sentence around the figure, and "so a 5kg turkey wants two and a half days: ..." was
        # read back as "So a 5kg turkey wants two."
        kilos, said = _bird_weight(understood) or (None, None)
        time = f"{_hours_words(24 * kilos / 2)}" if kilos else "two and a half days"
        return (f"A turkey wants {time} in the fridge. That is 24 hours for every 2kg: leave it in "
                "its wrapper in a tray on the bottom shelf and never on the worktop, and once it is "
                "thawed cook it within 2 days. A crown thaws in 24 hours.")
    if not any(word in text for word in small) and "joint" in text:
        # The figure the line asked about, so the answer is a time and not a rate: a rate is what
        # "how long for 500g of mince" reads back as if the joint is still the subject.
        kilos, said = _bird_weight(understood) or (None, None)
        hours = f"about {_hours_words(24 * kilos / 2)}" if kilos else "a day for every 2kg"
        # The time the line asked about, not a rate the next line can reuse for something else:
        # "how long does it take to thaw 500g of mince" after this one read back the joint's rate.
        # Short sentences on purpose: a follow-up that names another cut is read by the composer
        # as "the same question with a new amount", and the first sentence is what narrow() hands
        # back, so it has to stand on its own.
        return (f"Give it {hours} in the fridge. A {said or '2kg'} one goes in the night before: "
                "leave it in its wrapper in a tray on the bottom shelf, never on the worktop, and "
                "cook it within 2 days of thawing. A rolled or boned one is quicker than one on the "
                "bone.")
    if not any(word in text for word in small):
        # A follow-up that names no meat at all ("where do i put it", "can i leave it out
        # overnight") stays on the bird or joint it was about, not on mince.
        return ("In the fridge, on a plate on the bottom shelf, never on the worktop or in warm "
                "water. A turkey or a big joint wants a day or two there; mince, sausages and "
                "chops thaw overnight, and the microwave's defrost setting is the shortcut if you "
                "are short of time - cook the meat straight away when you use it.")
    return ("In the fridge, on a plate on the bottom shelf: mince, sausages and chops thaw "
            "overnight. If you are short of time use the microwave's defrost setting and cook the "
            "meat straight away, and never thaw it on the worktop or in warm water.")


# The same objection one word up: a mince pie is fruit and suet in pastry, so it has no pan
# juice and no browning to get wrong, and "my mince pies went grainy" was handed the hot-pan
# card. It is the two words together, not "pie" anywhere: a cottage pie and a shepherd's pie are
# mince dishes and real gains, so a bare "pie" cannot go in the entry's avoid list.
_MINCE_PIE_PHRASE = re.compile(r"\bmince ?pies?\b")


def _mince_grainy(memory, understood):
    """Mince that has gone grainy: the pan was not hot enough, so it boiled instead of browning.

    The cause is the same for a bolognese, a ragu, a chilli and a lasagne, so the answer is one
    and the rescue is in the pot already on the stove.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(_same(word, sense) for word in words for sense in KEEPING_SENSE):
        return None  # a keeping question about mince belongs to the keeping rows
    if _MINCE_PIE_PHRASE.search(" ".join(words)):
        return None  # a mince pie is fruit and suet: no browning to get wrong
    if (any(_same(word, name) for word in words for name in _BOLOGNESE_WORDS)
            and not any(_same(word, "sauce") for word in words)):
        return None  # dishes.py keeps the fuller answer for a named grainy bolognese
    # The first instruction is written as one, in its own sentence, because the follow-up rows
    # hand the first step of the last answer back to a "how do i stop that": read out of a
    # "next time get the pan hot, brown it, then add the tomatoes", that row found "add the
    # tomatoes" and told the person to do the last thing first.
    return ("A grainy sauce is usually the mince: it went into a pan that was not hot enough, so "
            "it boiled in its own juice instead of browning. Heat a heavy pan until a drop of "
            "water sizzles, then brown the mince in two batches. Leave it alone for 2 to 3 "
            "minutes at a time so it colours before the liquid goes in. For the pot you have, "
            "give it a slow half hour with the lid on, which softens the grains, and stir in a "
            "spoon of butter at the end.")


VAGUE = frozenset({"vegetables", "veg"})


# The same words as the pantry keys them, so a pair drops "veg" whichever form reached it.
_VAGUE_KEYS = frozenset({"vegetables", "vegetable", "veg"})


# Food families an eater may name as something they avoid. A group word ("meat", "dairy")
# stands for every food in that family, so "no meat" also rules out chicken and bacon.
MEAT = frozenset("meat chicken beef pork lamb mince bacon sausage sausages ham turkey prawn "
                 "prawns".split())


# Fish is the one food people who say "i don't eat meat" often do eat, so a bare meat ban does
# not confiscate it: it is a family of its own, and a vegetarian or vegan ban carries both. A
# prawn stays in meat as well as shellfish, because a vegetarian does not eat one either.
FISH = frozenset("fish salmon cod tuna".split())


DAIRY = frozenset("dairy milk cheese butter cream yoghurt yogurt".split())


# "no cheese" is a ban on the cheeses, and feta and halloumi are cheeses the dish names by their
# own name: a cheap dinner with feta crumbled over it was offered to someone who had just said no
# cheese, because the reply never says the word "cheese".
CHEESES = frozenset("feta halloumi parmesan mozzarella cheddar gruyere stilton brie camembert "
                    "ricotta paneer pecorino gouda edam wensleydale".split())


EGGS = frozenset("egg eggs".split())


NUTS = frozenset("nut nuts peanut peanuts".split())


# What gluten is, in the words a recipe uses: a coeliac is not avoiding a word, they are
# avoiding bread, pasta and flour, so the family is every everyday food those are made of.
GLUTEN = frozenset("gluten wheat pasta spaghetti bread toast flour couscous noodles barley rye "
                   "bulgur semolina cracker crackers cake biscuit biscuits pastry pitta".split())


# Shellfish is its own family: a prawn is meat to a vegetarian and a shellfish to someone who
# carries an epipen, and a ban on one is not a ban on the other.
SHELLFISH = frozenset("shellfish prawn prawns crab crabs lobster mussels oysters squid clams "
                      "scallops".split())


FAMILIES = {"meat": MEAT, "fish": FISH, "dairy": DAIRY, "egg": EGGS, "nut": NUTS,
            "gluten": GLUTEN, "shellfish": SHELLFISH}


# A vegetarian or a vegan does not eat fish either, and the diet words carry both families.
NO_MEAT_DIET = MEAT | FISH


# A condition said out loud rules out a food the way an allergy does: "im coeliac" is gluten,
# "im lactose intolerant" is dairy. Without this the ack promised to plan around it and the
# next meal was pasta and toast anyway.
CONDITION_BANS = {"coeliac": GLUTEN, "celiac": GLUTEN, "gluten intolerant": GLUTEN,
                  "lactose intolerant": DAIRY}


# "im not coeliac, what can i cook" is the one thing that must not turn the list gluten free: the
# words of a denial are the words of the condition, and the negator in front is what tells them
# apart. Same guard as bot/memory/facts.DENIAL_WORDS, kept here so the knowledge base stays data.
NOT_THIS = re.compile(r"(?:\bnot|\bnon|\bnever|\bno longer|\bn't|\baint|\bain't)\s+"
                      r"(?:really\s+|actually\s+|even\s+)?(?:a\s+|an\s+|any\s+|\bat all\s+)?$")


AVOIDED = re.compile(
    r"\b(?:no|without)\s+(?:(?:any|more|the|any more)\s+)?" + FOOD + r"\b"
    r"|\b(?:dont|don't|do not|doesnt|doesn't|does not|didnt|didn't|did not|cant|can't|"
    r"cannot|wont|won't|will not|wouldnt|wouldn't|refuse|refuses|refused|never)\s+"
    r"(?:eat|eating|have|use|using|cook with|want|touch|order)\s+(?:any\s+)?"
    r"(?:really\s+|usually\s+)?" + FOOD + r"\b"
    r"|\b(?:allergic|allergy|intolerant|intolerance)\s+to\s+" + FOOD + r"\b"
    r"|\b(?:hate|hates|avoid|avoiding|skip|skipping|off|cutting out|cut out)\s+"
    r"(?:the\s+|all\s+)?" + FOOD + r"\b"
    r"|\bnot\s+(?:a fan of|keen on|fussed about)\s+" + FOOD + r"\b"
    # A food said to be missing rather than refused: "i havent got any cheese", "there's no
    # milk left", "we got no rice". Said after an idea, it is a limit on that idea, and the
    # dish that needs it is no answer.
    r"|\b(?:havent|haven't|hasnt|hasn't|hadnt|hadn't)\s+(?:got|any)\s+(?:any\s+)?" + FOOD
    + r"\b"
    r"|\b(?:there\s+is\s+no|there's\s+no|theres\s+no|got\s+no|we\s+have\s+no|i\s+have\s+no)\s+"
    + FOOD + r"\b")


FREEFROM = re.compile(
    r"\b(meat|dairy|milk|cheese|gluten|wheat|nut|nuts|peanut|peanuts|egg|eggs)\s+free\b")


# "a nut allergy", "lactose intolerant" name the family before the problem word.
TROUBLE = re.compile(
    r"\b(nut|nuts|peanut|peanuts|dairy|milk|lactose|egg|eggs)\s+"
    r"(?:allergy|allergies|intolerance|intolerant)\b")


# A question about whether a food is vegetarian ("is a croissant vegetarian", "does gelatin count
# as vegetarian") is not this person saying they are one. Reading it as a diet made every reply
# that named the thing being asked about unusable - "are chips vegetarian" lost the answer about
# dripping and "is wine vegetarian" the one about isinglass, because the reply named beef and fish
# and the filter that keeps the food a person refuses out of an answer threw it away. The words
# that open the question are the whole distinction: "im vegetarian" and "ive been vegetarian for
# years" keep their reading, and a question keeps the food.
_DIET_ASKED = re.compile(
    r"\b(?:is|are|was|were|does|do|isnt|isn't|arent|aren't)\s+"
    r"((?:[a-z']+\s+){0,3}?)(?:vegetarian|vegan|veggie|vego)\b", re.I)


# The words between the opening and the diet word say whether a food is being asked about. "are
# chips vegetarian" and "does gelatin count as vegetarian" name the thing; "is there anything
# vegetarian", "is it vegetarian" and "is that ok for a vegetarian" do not, and those stay a diet.
_DIET_ASK_NOT_A_FOOD = frozenset(
    "there anything something any this that it these those he she they him her them my your our "
    "their his its ok okay fine alright safe suitable good bad healthy fine too also still".split())


def _ask_about_the_food(text, at):
    """Whether the diet word at this position is a question about a food, not a diet."""
    for match in _DIET_ASKED.finditer(text[:at]):
        if match.end() <= at and not (_DIET_ASK_NOT_A_FOOD & set(match.group(1).split())):
            return True
    return False


def _excluded(text):
    """The food words a line says to leave out, with group words expanded to their family.

    Any mention of the diet counts, not only "i'm a vegan": "lunch for a vegetarian", "something
    for someone who is vegan" and "a veggie guest" are the same diet, and the food words a person
    states elsewhere in the line still have to be left out. The mentions are then read in the
    order they were said, because the last thing said about a food is the one that holds: "im
    allergic to nuts" and then "im not allergic to nuts" is a person taking it back, not both at
    once. That is also how a condition is read, so a denied allergy and a denied coeliac are the
    same question and get the same answer.
    """
    text = str(text or "").lower().replace("\u2019", "'").replace("-", " ")
    events = []

    def note(position, families, positive=True):
        events.append((position, families, positive))

    for match in re.finditer(r"\b(?:vegetarian|veggie|vego)\b", text):
        if _ask_about_the_food(text, match.start()):
            continue
        note(match.start(), NO_MEAT_DIET, not _denied_at(text, match.start()))
    for match in re.finditer(r"\b(?:vegan|plant based|plantbased)\b", text):
        if _ask_about_the_food(text, match.start()):
            continue
        note(match.start(), NO_MEAT_DIET | DAIRY | EGGS, not _denied_at(text, match.start()))
    # A food named inside a denial is a food they can eat again: "im not allergic to nuts" is the
    # opposite of an allergy, and the words before the match are what tell the two apart.
    for pattern in (AVOIDED, FREEFROM, TROUBLE):
        for match in pattern.finditer(text):
            word = next((part for part in match.groups() if part), "")
            if not word:
                continue
            families = _families_of(word)
            denied = _denied_at(text, match.start())
            note(match.start(), families, not denied)
            # The list the food was said in is a list: the words after it ("peanuts and
            # cheese") and, for "X and Y free", the words before it are read too.
            note(match.start(), _foods_in_list(_list_words(text[match.end():match.end() + 80])),
                 not denied)
            if pattern is FREEFROM:
                note(match.start(),
                     _foods_in_list(_list_words(text[max(0, match.start() - 80):match.start()],
                                              backwards=True)), not denied)
    for condition, foods in CONDITION_BANS.items():
        for match in re.finditer(r"\b" + condition.replace(" ", r"\s+") + r"\b", text):
            note(match.start(), foods, not _denied_at(text, match.start()))
    state = {}
    for _position, families, positive in sorted(events, key=lambda event: event[0]):
        for word in families:
            state[word] = positive
    banned = {word for word, on in state.items() if on}
    # "no cheese" is a ban on the cheeses, and a feta or a halloumi is a cheese the dish names by
    # its own name: a cheap dinner with feta crumbled over it was offered to someone who had just
    # said no cheese, because the reply never says the word "cheese".
    if "cheese" in banned or DAIRY & banned:
        banned.update(CHEESES)
    return banned


# The words that join a list of foods: "allergic to peanuts and cheese", "gluten and dairy
# free". Only the connectors are skipped, so the reading stops at the first word that is not a
# food and a clause like "i dont eat meat, what can i cook" does not invent a ban on "what".
LIST_JOINERS = frozenset(("and", "or", "plus", "with", "also", "as", "well", "&", "+", ","))


# Every word that names a food or a food family on its own, so a list can be read word by word.
LIST_FOODS = frozenset(FAMILIES) | EGGS | NUTS | GLUTEN | DAIRY | SHELLFISH | FISH | MEAT \
    | CHEESES | frozenset(("lactose",))


def _families_of(word):
    """What one food word rules out: the family it names, or the word itself."""
    if word == "lactose":
        return DAIRY
    if word == "wheat":
        return GLUTEN  # "wheat free" is the same shop as "gluten free"
    return FAMILIES.get(word, {word})


def _foods_in_list(words):
    """The foods a list names, read until something that is not one.

    "allergic to peanuts and cheese" named two foods and only the first was read, and the same
    with "gluten and dairy free" - a coeliac who cannot have milk got one of the two.
    """
    found = set()
    for word in words:
        word = word.strip(".,!?;:'")
        if not word:
            continue
        if word in LIST_JOINERS:
            continue
        if word not in LIST_FOODS:
            break
        found |= _families_of(word)
    return found


def _denied_at(text, start):
    """True when the words just before `start` deny what is said at it ("im not ...")."""
    return bool(NOT_THIS.search(text[max(0, start - 30):start]))


# "Can I eat this?" after they have told us what they avoid. The answer is not a recipe, it is
# a yes or a no about one food, and the store already knows the constraint: the food a person
# names is checked against what they said, so "is satay safe for me" after a peanut allergy is
# a no about peanuts rather than a search hedge. Only the first person counts, because the
# answer is about them.
EAT_ASK = re.compile(
    r"\b(?:can|could|may|should|shall)\s+i\s+(?:eat|have|drink|order|try)\s+(?P<a>[\w ']+)"
    r"|\b(?:is|are)\s+(?P<b>[\w ']+?)\s+(?:ok|okay|fine|alright|safe|allowed)\s+"
    r"(?:for\s+me|for\s+us)\b"
    r"|\bam\s+i\s+(?:ok|okay|fine|alright|safe|allowed)\s+(?:to\s+(?:eat|have|drink)\s+)?"
    r"(?P<c>[\w ']+)"
    r"|\b(?:is|would)\s+(?P<d>[\w ']+?)\s+(?:be\s+)?(?:bad|wrong|a\s+problem)\s+for\s+me\b",
    re.I)


# A dish a person is only considering is the same yes-or-no question as "can I eat this", said
# as a plan: "i was thinking of a satay" a turn after a peanut allergy wants the check, not
# agreement. Only the first person and only the considering words, because a dish they are
# already cooking is the plan table's line ("im making a lasagne tonight").
FANCY_ASK = re.compile(
    r"\b(?:i\s+(?:fancy|fancied|fancying|crave|craved|craving|feel like|quite fancy|"
    r"really fancy|was thinking (?:of|about)|thought (?:i'd|i would|of having|about having)|"
    r"was going to (?:have|make|get)|was planning (?:to have|to make|on))|"
    r"i(?:'m| am)\s+(?:thinking (?:of|about)|craving|feeling like)|"
    r"i(?:'d| would)\s+(?:go for|have|make))\s+", re.I)


# The same question about somebody else: "can she eat pesto", "can my son have cake", "is satay
# ok for him". It is a question about that person's own record, never about the person typing,
# so it is answered from the guest's allergy or condition and from nobody else's.
EAT_ASK_THEM = re.compile(
    r"\b(?:can|could|may|should|shall)\s+(?:he|she|they|him|her|them|it"
    r"|(?:my|our|the)\s+[a-z']+)\s+(?:eat|have|drink|order|try)\s+(?P<a>[\w ']+)"
    r"|\b(?:is|are)\s+(?P<b>[\w ']+?)\s+(?:ok|okay|fine|alright|safe|allowed)\s+for\s+"
    r"(?:him|her|them|(?:my|our|the)\s+[a-z']+)\b"
    r"|\b(?:is|would)\s+(?P<d>[\w ']+?)\s+(?:be\s+)?(?:bad|wrong|a\s+problem)\s+for\s+"
    r"(?:him|her|them|(?:my|our)\s+[a-z']+)\b",
    re.I)


# The foods whose usual recipe is what makes them what they are, with the families they are
# made of. A dish is only here when leaving a family out would leave a different dish: satay is
# peanuts and a croissant is butter, while a caesar salad can be made without anchovy. A food
# with no family at all is one we can say yes about.
MADE_OF = {}


for _names, _families in (
        (("peanut", "peanuts", "satay", "pesto", "marzipan", "baklava", "praline", "nutella", "muesli", "granola",
          "nut roast", "peanut butter", "almond", "almonds", "cashew", "cashews", "walnut",
          "walnuts", "hazelnut", "hazelnuts", "pecan", "pecans", "pistachio", "pistachios"),
         (NUTS,)),
        (("pasta", "spaghetti", "bread", "toast", "noodles", "couscous", "pastry", "cake",
          "biscuit", "biscuits", "cracker", "crackers", "pitta", "flour", "crumpet", "bagel",
          "wrap", "wraps", "barley", "rye", "semolina", "scone", "scones", "pizza", "sandwich",
          # Ordinary soy sauce is brewed with wheat, which is the one that catches people out.
          "soy sauce", "soya sauce"),
         (GLUTEN,)),
        # A cake is flour and butter and egg, and a quiche is pastry, cream and egg: a table that
        # says only "wheat" turns a milk allergy into a confident yes about a cake. These are
        # still not everything a bought one can hold, which is why the yes about them is hedged.
        (("cake", "cakes", "quiche", "quiches"), (GLUTEN, DAIRY, EGGS)),
        (("cheese", "butter", "cream", "milk", "yoghurt", "yogurt", "ice cream", "custard",
          "paneer", "halloumi", "mozzarella"), (DAIRY,)),
        # A plant milk is not milk. The table only knew the word "milk", so "is oat milk ok" after
        # "im allergic to dairy" was answered "no: that is dairy" - and the drink a dairy-free
        # person can have is the one thing the answer must not take off them. The nut milks keep
        # the nut they are made of, because almond milk is still almonds.
        (("oat milk", "soy milk", "soya milk", "rice milk", "coconut milk", "hemp milk",
          "pea milk", "plant milk", "oat drink", "soya drink"), ()),
        (("almond milk", "cashew milk", "hazelnut milk"), (NUTS,)),
        (("croissant",), (GLUTEN, DAIRY)),
        (("chicken", "beef", "steak", "pork", "lamb", "bacon", "ham", "sausage", "sausages",
          "turkey", "mince", "gelatine", "lard"), (MEAT,)),
        (("fish", "salmon", "tuna", "cod"), (FISH,)),
        (("prawn", "prawns", "crab", "crabs", "lobster", "mussels", "oysters", "squid", "clams",
          "scallops", "shellfish"), (MEAT, SHELLFISH)),
        (("egg", "eggs", "mayonnaise", "mayo", "meringue", "omelette"), (EGGS,)),
        # Plain foods that are in none of the families, so a "can I eat this" about one gets a
        # yes rather than a search hedge from someone who has just told us what they avoid.
        (("rice", "potato", "potatoes", "chips", "lentils", "chickpeas", "beans", "quinoa",
          "corn", "tofu", "fruit", "vegetables", "veg", "salad", "broccoli", "carrot",
          # The flours and grains people ask about by name: none of these is wheat, and
          # "is cornflour gluten free" was a shrug while the answer was the table's own.
          "buckwheat", "cornflour", "corn flour", "rice flour", "gram flour", "tamari",
          # The raising agents: a plain baking powder is rice flour and bicarbonate, and
          # "is baking powder gluten free" got the gluten-free cake blend.
          "baking powder", "bicarbonate of soda", "bicarb", "cream of tartar", "yeast",
          "baking soda",
          "carrots", "spinach", "peas", "banana", "bananas", "apple", "apples", "oranges",
          "oats", "porridge", "honey", "fig", "figs", "olive oil", "oil", "salt", "sugar", "tinned tomatoes",
          "tomato", "tomatoes", "onion", "onions", "garlic", "courgette", "courgettes",
          "sweet potato", "sweet potatoes", "squash", "mushrooms"), ()),
):
    for _name in _names:
        MADE_OF[_name] = frozenset().union(*_families)


# How to say what the food is, and what does the same job without it. The first part is the
# whole predicate, because a chicken is meat and not made with it.
FAMILY_SAY = {
    id(NUTS): ("is made with nuts", "sunflower seeds or a spoon of yoghurt give the same crunch"),
    id(GLUTEN): ("is made with wheat flour", "rice, potatoes or a corn pasta do the same job"),
    id(DAIRY): ("is made with milk", "olive oil or a dairy-free spread does the same job"),
    id(EGGS): ("is made with egg", "a spoon of yoghurt where a recipe asks for one does the same"),
    id(MEAT): ("is meat", "chickpeas, lentils or tofu fill the same gap"),
    id(FISH): ("is fish", "chickpeas, lentils or tofu fill the same gap"),
    id(SHELLFISH): ("is shellfish", "chickpeas, lentils or tofu fill the same gap"),
}


# A food that *is* the family ("can i eat eggs" for a vegan) cannot be "made with egg": the
# honest answer is that the food is the thing itself. Gluten is left out on purpose, because
# bread is made with wheat flour rather than being it, and that sentence already reads right.
SELF_SAY = {id(NUTS): "that is nuts", id(DAIRY): "that is dairy", id(EGGS): "that is egg",
            id(MEAT): "that is meat", id(FISH): "that is fish", id(SHELLFISH): "that is shellfish"}


# "What can I eat?" with nothing named is the same question the other way round: the list to
# choose from, not a single food.
# The same question with the "for me" left off: "is pesto ok", "is a beef burger alright", "is the
# pesto safe". On its own that is the food entry's question, and often not about eating at all ("is
# the milk still ok" is the fridge), so it only counts when the store holds something the person
# avoids and the food they name is made of it - then the line can only be about them, and the
# answer is the no. The yes stays with the entries, so a bare ask never claims a food is safe.
EAT_ASK_BARE = re.compile(
    r"\b(?:is|are|was|were)\s+(?P<e>[\w ']+?)\s+(?:ok|okay|fine|alright|safe|allowed)"
    r"\s*[?.!,]*$", re.I)


# "is cheese ok if im lactose intolerant" is the same yes or no as "is cheese ok", said with the
# condition after it rather than before it, and the diet card answered it with a swaps list.
EAT_ASK_IF = re.compile(
    r"\b(?:is|are|was|were)\s+(?P<f>[\w ']+?)\s+(?:ok|okay|fine|alright|safe|allowed)\s+"
    r"(?:if|since|because|as|when|now that)\b", re.I)


EAT_ANY = re.compile(r"\bwhat\s+(?:can|could|should)\s+i\s+(?:eat|have)\b"
                     r"|\bwhat\s+(?:food|foods)\s+can\s+i\s+(?:eat|have)\b", re.I)


# The words a bare "what can I eat" is made of. A line that says more than these is asking for a
# meal rather than for the list ("what can i have for lunch" is the lunch idea's question), so the
# list only answers the line that carries nothing else.
EAT_ANY_WORDS = frozenset("what can could should shall i eat have to now then instead please "
                          "today tonight for a also still tonight really actually at the moment "
                          "me us we just more".split())


# Foods whose bought or restaurant version often has a family in it even though the recipe does
# not need it. This is why allergy advice ends with "read the label": a plain cake needs no nuts
# at all, and plenty of bought ones have them in the icing, the decoration or the same factory.
MAY_HAVE = {}


for _name in ("cake", "cakes", "icing", "biscuits", "biscuit", "cookies", "chocolate", "dessert",
              "desserts", "ice cream", "muesli", "cereal", "granola", "flapjack", "brownie",
              "brownies", "pie", "pastry", "curry", "curries", "salad", "sandwich", "sandwiches",
              "bread", "sauce", "sauces"):
    MAY_HAVE[_name] = NUTS


# What a person's own ban is called when the answer is a yes.
BAN_SAY = ((NUTS, "nuts"), (GLUTEN, "gluten"), (DAIRY, "dairy"), (EGGS, "egg"), (MEAT, "meat"),
           (FISH, "fish"), (SHELLFISH, "shellfish"))


ANY_FAMILY = (NUTS, GLUTEN, DAIRY, EGGS, MEAT, FISH, SHELLFISH)


def _food_named(text):
    """The dish or food a line names that we can answer about, longest phrase first, or None."""
    words = re.findall(r"[a-z']+", str(text or "").lower())
    for size in (2, 1):
        for start in range(len(words) - size + 1):
            phrase = " ".join(words[start:start + size])
            if phrase in MADE_OF:
                return phrase
    return None


def _foods_named(text):
    """Every food the line names that we can answer about, longest phrase first.

    A two-word dish wins over the word inside it ("peanut butter" is not "butter"), so a line
    naming both that dish and another food says so with two entries."""
    words = re.findall(r"[a-z']+", str(text or "").lower())
    found, taken = [], set()
    for size in (2, 1):
        for start in range(len(words) - size + 1):
            if any(at in taken for at in range(start, start + size)):
                continue
            phrase = " ".join(words[start:start + size])
            if phrase in MADE_OF:
                found.append(phrase)
                taken.update(range(start, start + size))
    return found


# A food word ending in "s" that is still one thing: "couscous is made with wheat" is right and
# "couscous are made with wheat" is not. A plural one needs the plural verb, or the answer reads
# like a machine talking: "almonds are made with nuts", "potatoes have no gluten in them".
SINGULAR_IN_S = frozenset("couscous hummus muesli asparagus fish veg molasses".split())


def _is_plural(food):
    word = food.split()[-1]
    if word in SINGULAR_IN_S or word.endswith("ss"):
        return False
    return word.endswith("s")


def _named_as(text, food):
    """The food the way the line named it: "a croissant" keeps its article, "croissant" alone
    stays bare, because the answer is about the thing they pointed at."""
    text = str(text or "").lower()
    for match in re.finditer(r"\b" + r"\s+".join(re.escape(part) for part in food.split()) + r"\b",
                             text):
        # "a peanut butter sandwich": the article belongs to the sandwich, and answering "a
        # peanut butter is made with nuts" talks about a food nobody asked for.
        after = re.match(r"[\s-]+([a-z']+)", text[match.end():])
        if after and after.group(1) in MADE_OF:
            continue
        before = text[:match.start()].rstrip()
        # The words they used to name it belong in the answer: "can i have lactose free milk" is
        # not a question about milk, and "milk has no dairy in it" is a riddle rather than a yes.
        # Whatever they said a food is free of stays in front of it.
        free = re.search(r"([a-z]+)\s+free$", before)
        qualifier = ""
        if free and free.group(1) in FREE_OF:
            qualifier = free.group(1) + " free "
            before = before[:free.start()].rstrip()
        article = re.search(r"([a-z']+)$", before)
        if article and article.group(1) in ("a", "an", "the"):
            return article.group(1) + " " + qualifier + food
        return qualifier + food
    return food


def _bans_for(understood, memory):
    """What this person avoids: the store's own record, plus what the turns said in the first
    person. A guest's allergy is not theirs, so "can i eat satay" after "my son is allergic to
    peanuts" is not a no about the person, and the store keeps the two apart already (the text
    is read here only for what the store has no key for, like "no cheese please")."""
    banned = _bans_from_store(memory) | _excluded(_mine_only(_said_so_far(understood, memory)))
    # Lactose intolerance is not a dairy allergy. The reader that says "no" to a dairy allergy says
    # it here too, so "can i eat cheese if im lactose intolerant" was told that dairy is off the
    # table - and hard cheese is the dairy food most of those people can eat. The word they used is
    # kept next to the family it reaches, so the answer can tell the two apart: the marker means a
    # reply may name dairy, because how much milk sugar is in it is the whole question.
    line = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    if any(word in line for word in _NOT_LACTOSE_WORDS):
        # "im lactose intolerant and vegan" is a vegan plate: the line said both, and the stronger
        # of the two is the one that decides
        pass
    elif _a_lactose_intolerance(line) or _their_diet_is_a_lactose_intolerance(memory):
        banned = set(banned) | {"lactose"}
    return banned


# Who a clause is about. A sentence about someone else says nothing about what the person in
# front of us can eat, and their allergy must not come back as the person's own answer.
THIRD_PERSON = re.compile(
    r"^\s*(?:my\s+(?!own\b)[a-z']+|the\s+(?:baby|kid|kids|child|children|little one|dog|cat)|"
    r"he|she|they|his|her|their|hubby|other half|partner's)\b", re.I)


def _mine_only(text):
    """The parts of a line that are about the person themselves, joined back up.

    "im coeliac and my wife is coeliac" is both of them; "my wife is coeliac" is only her, and
    reading her condition as theirs would answer a question about their own dinner with hers.
    """
    parts = [part.strip() for part in re.split(r"(?<=[.!?;])\s+|\s*,\s*|\s+and\s+|\s+but\s+",
                                               str(text or "")) if part.strip()]
    return " ".join(part for part in parts if not THIRD_PERSON.match(part))


def _bans_from_store(memory):
    """What the person themselves avoids, as the store has it, or an empty set.

    The store keeps a person's own allergy, condition and diet apart from a guest's, and a line
    read for food words cannot: "my son is allergic to peanuts" is his allergy, so what he cannot
    eat is not an answer about whether the person can.
    """
    user = memory.get("user") if isinstance(memory, dict) else None
    if not isinstance(user, dict):
        return set()
    return _bans_of(user)


def _bans_of(facts):
    """What one person avoids, from their own record of allergies, condition and diet."""
    banned = set()
    if not isinstance(facts, dict):
        return banned
    for item in facts.get("allergies") or ():
        word = str(item).lower()
        banned.update(FAMILIES.get(word) or {word})
    for item in facts.get("condition") or ():
        said = str(item).lower()
        for condition, foods in CONDITION_BANS.items():
            if condition in said:
                banned.update(foods)
    diet = str(facts.get("diet") or "").lower()
    if diet in ("vegetarian", "veggie", "vego"):
        banned.update(NO_MEAT_DIET)
    elif diet in ("vegan", "plant based", "plantbased"):
        banned.update(NO_MEAT_DIET | DAIRY | EGGS)
    elif diet.startswith("no "):
        word = diet[3:].strip()
        banned.update(FAMILIES.get(word) or {word})
    return banned


def _named_families(banned):
    """The families the person named outright, which is not every family they touch.

    A ban on shellfish reaches the word "prawn", and the word "prawn" is also in the meat family,
    so intersecting the families alone would say a shellfish allergy is a meat one. The name the
    person used is the one that decides."""
    return {family for family, name in BAN_SAY if name in banned}


def _bans_said(banned):
    """The names of what they avoid, in the order the families are listed.

    A ban on meat already covers the shellfish in it, so a person who avoids meat is not also
    told they avoid shellfish: that lists the same food twice and reads like a machine."""
    named = _named_families(banned)
    names = [name for family, name in BAN_SAY if family in named]
    if not names:
        names = [name for family, name in BAN_SAY if family & banned]
    if "meat" in names and "shellfish" in names:
        names.remove("shellfish")
    if "meat" in names and "fish" in names:
        names.remove("fish")  # a vegetarian avoids both, and "meat" already says it once
    return names


# What a "somebody else can't have X" answer calls each family when it names the label to look
# for: "a jar that says nut-free" is the check a person can act on in a shop.
BAN_SAY_NAME = {id(NUTS): "nuts", id(GLUTEN): "gluten", id(DAIRY): "milk",
                id(EGGS): "egg", id(MEAT): "meat", id(FISH): "fish",
                id(SHELLFISH): "shellfish"}


FREE_OF = {id(NUTS): "nut-free", id(GLUTEN): "gluten-free", id(DAIRY): "dairy-free",
           id(EGGS): "egg-free", id(MEAT): "meat-free", id(FISH): "fish-free",
           id(SHELLFISH): "shellfish-free"}


def _food_may(text):
    """A food we know the bought version of, longest phrase first, or None.

    Chocolate is not something you make at home, so it is not in the recipe table, and "can she
    eat chocolate" is still a label question for a nut allergy.
    """
    words = re.findall(r"[a-z']+", str(text or "").lower())
    for size in (2, 1):
        for start in range(len(words) - size + 1):
            phrase = " ".join(words[start:start + size])
            if phrase in MAY_HAVE:
                return phrase
    return None


def _not_for_them(food, banned, guest, text=""):
    """The answer to "can my wife eat pesto" from her own record.

    Two answers: a plain no when the dish's own recipe has what they avoid, and the label check
    when the bought one often does. A food that is neither keeps the answer the entries give it,
    because "can he eat cake" gets the icing and the decorations from the allergy entry and a
    one-line yes would be the thinner reply.
    """
    named = _named_as(text, food)
    who = str((guest or {}).get("who") or "").strip().lower()
    them = ("your " + who) if who else "them"
    named_here = _named_families(banned)
    hits = [family for family in ANY_FAMILY if family & MADE_OF.get(food, frozenset())
            and family & banned]
    hits.sort(key=lambda family: 0 if family in named_here else 1)
    if hits:
        said = FAMILY_SAY[id(hits[0])][0]
        if _is_plural(food):
            said = re.sub(r"\bis\b", "are", said)
        return ("No: " + named + " " + said + ", so it is off the table for " + them + ". "
                "A pack or a menu that says " + FREE_OF.get(id(hits[0]), "free from it") +
                " is the only check that settles it.")
    may = [family for family in ANY_FAMILY if family & MAY_HAVE.get(food, frozenset())
           and family & banned]
    if not may:
        return None
    family = may[0]
    what = "nuts" if family is NUTS else BAN_SAY_NAME.get(id(family), "it")
    return (named.capitalize() + " can be made without " + what + ", but the bought or "
            "restaurant version often has " + ("them" if what == "nuts" else "it") + " in, so for " +
            them + " the pack or the menu has to say " + FREE_OF.get(id(family), "free from it") +
            ".")


# A follow-up that names a food and nothing else: "what about pesto", "and pesto?", "is bread
# out then", "how about a satay". People do not ask "can my son eat pesto" a second time, they
# point at the dish - and the record of what the guest cannot have is what answers it. The words
# below are the noise around the food (the pointing, the yes-or-no, the little adverbs); a line
# whose words are the food plus only these is a question about that food, and any other word in
# it makes it somebody else's line. Cooking verbs are left out on purpose, so that a statement
# ("i eat pesto") is not read as a question.
_POINTING = frozenset((
    "what", "how", "about", "and", "or", "then", "instead", "also", "so", "but", "just", "please",
    "with", "without", "for", "to", "can", "could", "may", "should", "shall", "would", "will",
    "do", "does", "did", "a", "an", "the", "be", "is", "are", "was", "were", "am", "i", "we",
    "you", "he", "she", "they", "him", "her", "them", "it", "that", "this", "those", "these",
    "ok", "okay", "fine", "alright", "safe", "allowed", "out", "off", "table", "no", "good",
    "wrong", "problem", "any", "some", "still", "too", "as", "well", "me", "my", "our", "us",
    "now", "next", "there", "again", "one", "thing", "things", "either", "neither", "not", "yes",
    "much", "many", "all", "right", "dodgy", "bad", "avoid", "of", "on", "in", "at",
))


_LEAVE_IT_OUT = frozenset((
    "no", "not", "dont", "doesnt", "didnt", "without", "avoid", "skip", "drop", "leave", "hold",
    "minus", "except", "apart",
))


def _foods_a_line_points_at(line):
    """The foods a line is made of, when it is made of nothing else, or none.

    A line of more than seven words is a sentence about something, and a word of its own beyond
    the pointing ("what about **using** pesto") is that sentence, so neither is claimed here."""
    words = re.findall(r"[a-z']+", str(line or "").lower())
    if not words or len(words) > 7:
        return []
    foods = _foods_named(line)
    if not foods:
        may = _food_may(line)
        return [may] if may else []
    spare = set(" ".join(foods).split())
    left = [word for word in words if word not in spare and word not in _POINTING]
    if left:
        return []
    # "and no cheese either" names a food and tells us to leave it out, so the dish on the table
    # without it is the answer and the record has nothing to say: only a line that points at the
    # food asks about it.
    if any(word in _LEAVE_IT_OUT for word in words):
        return []
    return foods


def pointed_at_a_food(understood, memory):
    """A follow-up that names only a food, answered from the condition on file, or None.

    "My son is allergic to nuts" then "what about pesto" is one question, and the answer is the
    no that "can he eat pesto" already gets: the recipe for a pesto is the one thing this line
    must not be answered with. The store keeps the guest and what they cannot have, so the same
    record answers both shapes.

    Only a food whose own recipe is made of what they avoid is claimed here: that is the line
    where the recipe would put the ingredient they cannot have on the plate. A food that is
    merely one a shop often adds it to ("what about cake" for a nut allergy) keeps the entry on
    labels and icing, because a one-line check says less than that does. A line naming two foods
    is a dish ("a peanut butter sandwich") unless exactly one of them is one they cannot have.
    """
    if not isinstance(understood, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "")
    foods = _foods_a_line_points_at(line)
    if not foods:
        return None
    # A guest whose record says what they cannot have is the person the line is about, so their
    # record answers it and the person typing's own allergies are not borrowed for it.
    guest = _the_guest(memory, line)
    guest_bans = _bans_of(guest) if guest else frozenset()
    if guest_bans:
        hits = [food for food in foods if food in MADE_OF and _bans_it(food, guest_bans)]
        return _not_for_them(hits[0], guest_bans, guest, line) if len(hits) == 1 else None
    banned = _bans_for(understood, memory)
    if not _bans_said(banned):
        return None
    hits = [food for food in foods if food in MADE_OF and _bans_it(food, banned)]
    return _one_food_answer(hits[0], banned, line) if len(hits) == 1 else None


# What a line can say a food is free of, and the family each word stands for. A food's own
# recipe is not the whole answer when the line in front of it says what is not in it.
FREE_OF = {"meat": MEAT, "fish": FISH, "dairy": DAIRY, "milk": DAIRY, "lactose": DAIRY,
           "cheese": DAIRY, "gluten": GLUTEN, "wheat": GLUTEN, "nut": NUTS, "nuts": NUTS,
           "peanut": NUTS, "peanuts": NUTS, "egg": EGGS, "eggs": EGGS, "shellfish": SHELLFISH,
           "sugar": frozenset(), "soya": frozenset(), "soy": frozenset()}


def _free_of(text, food):
    """The families the line itself says this food is free of, or nothing.

    "is lactose free milk ok" was a no about dairy for somebody who is lactose intolerant, and
    "is gluten free bread ok" is the same shape: the words in front of the food say what is not in
    it, and an answer that reads only the food's own recipe takes away the one thing they can
    have. Only the word in front counts, because "milk from a lactose free farm" says nothing.
    """
    text = str(text or "").lower().replace("\u2019", "'").replace("-", " ")
    phrase = r"\s+".join(re.escape(part) for part in food.split())
    for match in re.finditer(r"\b([a-z]+)\s+free\s+" + phrase + r"\b", text):
        if match.group(1) in FREE_OF:
            return FREE_OF[match.group(1)]
    for match in re.finditer(phrase + r"\s+(?:is\s+|are\s+)?([a-z]+)\s+free\b", text):
        if match.group(1) in FREE_OF:
            return FREE_OF[match.group(1)]
    return frozenset()


def _bans_it(food, banned):
    """True when a food's usual recipe is made of something the person avoids."""
    return any(family & MADE_OF[food] and family & banned for family in ANY_FAMILY)


_LACTOSE_FREE_ASK = re.compile(r"lactose[\s-]*free", re.I)


def _lactose_answer(food, text):
    """What a lactose intolerance can have of this food, or None for a food with no milk in it."""
    if _LACTOSE_FREE_ASK.search(str(text or "")):
        # the product itself is the question, and the answer to it is yes
        return ("Yes: lactose-free milk is ordinary milk with the milk sugar already split, so it "
                "does the same job in tea, on cereal and in cooking. There are lactose-free "
                "yoghurts and soft cheeses too, though a hard cheese or butter has almost none "
                "left in it anyway.")
    if food in _LACTOSE_SAYS:
        return _LACTOSE_SAYS[food]
    if DAIRY & MADE_OF.get(food, frozenset()):
        return ("It depends how much milk is in it: milk, soft cheese, yoghurt and ice cream hold "
                "most of the lactose, while a hard cheese or butter has almost none left. Try a "
                "small portion with a meal, and lactose-free milk and lactase tablets are there "
                "for the ones that catch you out.")
    return None


def _one_food_answer(food, banned, text, bare=False):
    """The yes or no about one food, from the families its usual recipe is made of."""
    avoid = _bans_said(banned)
    if "lactose" in banned:
        # "im lactose intolerant" reaches the dairy family, the same as "im allergic to dairy", so
        # this reader was saying "no" to a lactose intolerance too. How much milk sugar is in the
        # food is the question, so that is the answer.
        answer = _lactose_answer(food, text)
        if answer:
            return answer
    made_of = MADE_OF[food] - _free_of(text, food)
    hits = [family for family in ANY_FAMILY if family & made_of and family & banned]
    # The family they named comes before one they only reached through a word inside it.
    named_here = _named_families(banned)
    hits.sort(key=lambda family: 0 if family in named_here else 1)
    if bare and not hits:
        # A bare "is X ok" with nothing of theirs in it is not this reader's line: it belongs to
        # the food entry, which says what the food is for without claiming it is safe for them.
        return None
    if not hits:
        if food in FISH and MEAT in named_here and FISH not in named_here:
            # A bare "i don't eat meat" does not settle fish: plenty of people who say it eat
            # fish, so neither a no nor a yes is honest, and the answer names the split.
            return FISH_SPLIT
        if len(avoid) == 1:
            what = avoid[0]
        else:
            what = ", ".join(avoid[:-1]) + " or " + avoid[-1]
        named = _named_as(text, food)
        if food == "honey" and {"meat", "dairy", "egg"} <= banned:
            # Honey is the plain food a vegan can refuse and a table of families cannot see: no
            # meat, dairy or egg in it, so a confident yes is a claim about somebody's principles
            # rather than about the food. A no would be just as wrong about a vegan who counts it.
            return ("Some vegans avoid honey, so it depends how strict you are - sugar or golden "
                    "syrup does the same job in a recipe.")
        if made_of:
            # A dish is made of more than the families this table lists, and a bought one can
            # hold what the recipe does not: a quiche is pastry, cream and egg, and the shop's
            # can carry nuts. "A quiche has no nuts in it" is a confident claim the table cannot
            # back, and a wrong yes about an allergy is the one thing this answer must not do,
            # so the yes is about the plain dish and the label is named.
            them = "them" if what in ("nuts",) else "it"
            return ("Nothing in " + named + " needs " + what + ", but a bought one can have " +
                    them + " in - check the label.")
        # A food we know the recipe of, made of none of it: the honest answer to "can I eat this"
        # is a yes, and "I'd rather not guess" about plain rice is a worse one.
        if "gluten" in avoid and food in NOT_SETTLED_BY_THE_RECIPE:
            return NOT_SETTLED_BY_THE_RECIPE[food]
        if _is_plural(food):
            return ("Yes: " + named + " have no " + what + " in them, so they are fine for you.")
        return "Yes: " + named + " has no " + what + " in it, so it is fine for you."
    said, swap = FAMILY_SAY[id(hits[0])]
    named = _named_as(text, food)
    if food in hits[0] and id(hits[0]) in SELF_SAY:
        # The food is the family itself ("can i eat eggs" for a vegan, "can i eat peanuts" for a
        # nut allergy), and "eggs are made with egg" is a riddle rather than an answer.
        return ("No: " + SELF_SAY[id(hits[0])] + ", and it is off the table for you. " +
                swap[0].upper() + swap[1:] + ".")
    if _is_plural(food):
        said = re.sub(r"\bis\b", "are", said)
    return ("No: " + named + " " + said + ", and that is off the table for you. " +
            swap[0].upper() + swap[1:] + ".")


def _no_meat_also_means_fish(banned):
    """What a meal idea leaves out when a bare "no meat" is all the person has said.

    The split in suits_them is for a yes/no question about fish. A suggestion is not that: an
    idea that offers tuna to someone who has just said they do not eat meat is worse than the
    idea the split protects, so a meal leaves both families out."""
    return banned | FISH if MEAT & banned else banned


# --- a reply that names a food the person does not eat ---------------------------------------
# The bans above are used to choose between things to cook, and the words they cover are the
# short ones a line says out loud ("bacon", "butter"). A reply says them in full ("chopped
# bacon", "a knob of butter", "flaked salmon", "feta"), so the check on a finished reply needs
# the wider list: what a recipe calls a meat, a fish or a dairy.
MEAT_SAYS = MEAT | frozenset(
    "chorizo salami pancetta prosciutto pepperoni steak brisket liver kidney venison duck "
    "goose rabbit pheasant partridge anchovies anchovy sardines mackerel haddock kippers".split())


FISH_SAYS = FISH | frozenset(
    "anchovies anchovy sardines mackerel haddock kipper kippers shellfish prawns crab lobster "
    "mussels oysters squid clams scallops".split())


DAIRY_SAYS = DAIRY | CHEESES | frozenset("mozzarella creme buttermilk ghee".split())


EGG_SAYS = EGGS | frozenset("mayonnaise mayo omelette quiche custard meringue".split())


NUT_SAYS = NUTS | frozenset("almonds almond cashews cashew walnuts walnut pistachios pistachio "
                           "hazelnuts hazelnut pecans pecan brazil marzipan praline satay "
                           "nutella pesto".split())


SHELLFISH_SAYS = SHELLFISH | frozenset("prawn crab lobster mussel oyster squid clam scallop "
                                       "prawns crabs lobsters mussels oysters clams scallops".split())


# The dairy words that can be swapped for something everyone has, so the answer stays an answer
# instead of being thrown away. "peanut butter" and "butter beans" are not dairy, and a butter
# bean is not a butter, so both keep their word.
DAIRY_SWAPS = (
    (re.compile(r"\ba knob of butter\b", re.I), "a little oil"),
    (re.compile(r"\b(?:a|one) spoon of cream\b", re.I), "a spoon of oat cream"),
    (re.compile(r"\bdouble cream\b", re.I), "oat cream"),
    (re.compile(r"\bmashed with butter\b", re.I), "mashed with olive oil"),
    (re.compile(r"\b(?<!peanut )(?<!cocoa )(?<!shea )(?<!apple )(?<!nut )(?<!butter )butter\b"
                r"(?!\s*beans?\b)", re.I), "oil"),
    (re.compile(r"\b(?<!coconut )(?<!oat )(?<!soy )(?<!almond )(?<!plant )(?<!rice )(?<!hemp )"
                r"(?<!butter )(?<!goat )(?<!sheep )milk\b", re.I), "plant milk"),
    # The dairy that a dairy-free cook is told to use as a substitute is the same problem one
    # step along: "in marinades and dressings: sour cream, creme fraiche or buttermilk" answers
    # "what can i use instead of yoghurt" with three things they cannot have.
    (re.compile(r"\bsour cream\b", re.I), "soya yogurt"),
    (re.compile(r"\bcr[eè]me fra[iî]che\b", re.I), "soya cream"),
    # "or buttermilk" in a list, but not the heading "For 250ml of buttermilk:", which is the
    # thing the person is asking to replace.
    (re.compile(r"\bor buttermilk\b", re.I), "or plant milk with a squeeze of lemon"),
    # "one egg becomes 60g of yoghurt" is the vegan substitute card telling a vegan what to buy,
    # so the yoghurt in it is the one swap the card cannot do without.
    (re.compile(r"\b(?<!soya )(?<!soy )(?<!coconut )(?<!plant )(?<!oat )(?<!almond )"
                r"(?<!greek )(?:yoghurt|yogurt)\b", re.I), "soya yoghurt"),
)


# A nut in a reply is usually a substitution, not the dish: the dairy-free card says "oat, soya or
# almond milk", and handing that to a household with a nut allergy is one word away from useful.
# Swapping keeps the card instead of throwing it away.
NUT_SWAPS = (
    (re.compile(r"\balmond milk\b", re.I), "oat milk"),
    (re.compile(r"\balmond flour\b", re.I), "plain flour"),
    (re.compile(r"\bground almonds\b", re.I), "ground seeds"),
    (re.compile(r"\bflaked almonds\b", re.I), "seeds"),
    (re.compile(r"\b(?<!sunflower )(?<!seed )(?<!soya )(?<!olive )peanut butter\b", re.I),
     "sunflower seed butter"),
    (re.compile(r"\bnut butter\b", re.I), "seed butter"),
)


GLUTEN_SWAPS = (
    ("pasta", re.compile(r"\b(?<!free )(?<!free- )pasta\b", re.I), "gluten-free pasta"),
    ("toast", re.compile(r"\b(?<!free )(?<!free- )toast\b", re.I), "gluten-free toast"),
)


# A dairy word after one of these is not dairy: "coconut milk", "peanut butter" and "butter
# beans" are foods a person avoiding milk can eat, and reading them as the dairy would take a
# good answer away from them.
NOT_THE_DAIRY = re.compile(r"\b(?:oat|soy|soya|coconut|almond|plant|rice|hemp|cashew|peanut|"
                           r"shea|cocoa|apple|nut)\s+$", re.I)


# A reply that names the food and tells the person how to be safe with it is doing its job:
# "a bought one can have it in - check the label" is the careful answer about an allergen, and
# reading the word itself as the food served threw it away.
CAUTION_SAID = re.compile(
    r"\b(?:check|read|look at|watch)\s+(?:the\s+)?(?:label|labels|packet|packets|ingredients|"
    r"ingredient list|back of the (?:pack|packet|tin|box|jar)|pesto|chocolate|jar)"
    r"|\bmay contain\b|\ballergen|\bcross[- ]contamination"
    r"|\bask (?:the staff|them|whoever|at the counter|before)" 
    r"|\bcan have (?:it|them) in\b|\bcan (?:sometimes )?carry\b|\bmay have\b"
    r"|\boff the table for\b|\bnot for you\b|\brather not risk\b|\bstay (?:well )?clear\b"
    r"|\b(?:avoid|avoiding|watch out for)\b|\bfree from\b|\b(?:nut|dairy|gluten)[- ]free\b", re.I)


# The plant versions said out loud: a reply that carries these is a reply written for someone who
# does not eat the dairy or the egg, and the dairy words in it are the things being replaced.
PLANT_SAID = re.compile(r"\b(?:vegan|vegetarian|plant based|plant-based|dairy free|dairy-free|"
                        r"egg free|"
                        r"margarine|flax egg|flaxseed|oat milk|soya milk|soy milk|almond milk|"
                        r"oat cream|soya cream|nutritional yeast|aquafaba)\b", re.I)


# A food named to say what replaces it is the answer for someone who does not eat it: a vegan
# cake is "a flax egg for each egg ... margarine for every 100g of butter", and reading those
# words as the dish took the one entry that knows the bake away from the person. The marker has
# to sit against the word, not somewhere in the sentence: "crumble into a sprout and bacon dish
# ... sweet enough without cream" is a bacon dish with a note about the cream.
SWAP_BEFORE = re.compile(r"(?:instead of|in place of|rather than|swap for|substitute for|"
                         r"no need for|without|free of|for (?:each|every|the)|per|"
                         r"flax|chia|linseed|vegan|plant|soya|soy|oat|coconut|almond|nut)\s+"
                         r"(?:\d+\s*(?:g|ml)\s+(?:of\s+)?)?$", re.I)


SWAP_AFTER = re.compile(r"\s*-?\s*(?:free|replacer|substitute|swap)\b", re.I)


def avoids(memory, understood=None):
    """What the person themselves does not eat, from the store and from the turns.

    A module outside this one answers with a row written for everyone, so it needs the same
    reading of a diet that the meal tables use. Everything here is optional: a memory with no
    store and no line is a person with no bans, which is the answer for every line that is not
    about food.
    """
    if not isinstance(memory, dict):
        return frozenset()
    read = understood if isinstance(understood, dict) else memory.get("understood")
    if not isinstance(read, dict):
        read = {}
    try:
        return frozenset(_bans_for(read, memory))
    except Exception:
        return frozenset()


def _family_of(word):
    """The family a word names, singular or plural: "nuts" is NUTS, "peanuts" is NUTS."""
    word = str(word or "").strip().lower()
    if not word:
        return set()
    for key in (word, word[:-1] if word.endswith("s") else word):
        if key in FAMILIES:
            return set(FAMILIES[key])
    return {word}


def avoids_for_the_one_talked_about(memory):
    """What the person the chat is *about* cannot eat, when that is somebody else.

    avoids() is the person in front of us on purpose: "can i eat satay" after "my son is allergic
    to peanuts" is not a no about them. But a long chat about packing a daughter's lunch is about
    her, and the store keeps her allergies apart (memory["others"]) with the person the chat is
    about already named (memory["person"]). Without this the card for her lunch was checked
    against nobody, and a snack list headed "nuts, fruit, yoghurt" came back to a family who had
    just said nuts are off the table.

    Only allergies: a diet or a condition said about somebody else is theirs to be asked about,
    and a card rewritten free of meat because a guest is vegetarian is answering about the guest.
    """
    if not isinstance(memory, dict):
        return frozenset()
    person = memory.get("person")
    if not isinstance(person, dict):
        return frozenset()
    who = str(person.get("who") or "").strip().lower()
    if not who:
        return frozenset()
    banned = set()
    for record in memory.get("others") or ():
        if not isinstance(record, dict):
            continue
        if str(record.get("who") or "").strip().lower() != who:
            continue
        for item in record.get("allergies") or ():
            banned |= _family_of(item)
        break
    return frozenset(banned)


# A clause that is itself saying the swap is the answer, not a food to fix. The dairy-free card
# opens "Dairy free is easy to cook around: oat, soya or almond milk in place of milk, olive oil
# instead of butter" - a card written for the person - and the dairy swap rewrote it into "in
# place of plant milk, olive oil instead of oil", which is the one reply that needed nothing.
SWAP_CLAUSE = re.compile(r"\b(?:in place of|instead of|rather than|or use|substitute for|"
                         r"swap for|no need for|works too)\b", re.I)


# A reply whose sense is that the food is out is a reply *about* the avoided food, and it is the
# one a vegan most needs: "can i eat eggs" answered "No: that is egg, and it is off the table for
# you. A spoon of yoghurt where a recipe asks for one does the same." Reading the egg in that as a
# fault handed the person a shrug instead. "Since you are not eating meat, I'd leave that out and
# do dhal" is the same shape.
SAYS_THE_FOOD_IS_OUT = re.compile(
    r"off the table|not for you|you (?:cannot|can't|can not|shouldn't|should not) have|"
    r"leave (?:that|it|them|those) out|leave out the|you (?:do not|don't|dont) eat|"
    r"since you (?:are |'re )?(?:not eating|vegan|vegetarian|dairy|gluten)|"
    r"not eating (?:meat|dairy|gluten|eggs)|you avoid|you're avoiding|you are avoiding|"
    r"no meat|without the meat|swap (?:it|that)|there is no egg|that is egg|that's egg|"
    r"that is meat|those are meat|no dairy", re.I)


# A food that is already the gluten-free one: "rice, potatoes or a corn pasta do the same job"
# was rewritten into "a corn gluten-free pasta", which says the same thing twice.
GLUTEN_FREE_ALREADY = re.compile(
    r"\b(?:gluten[- ]free|corn pasta|rice pasta|rice noodles|corn noodles|buckwheat|polenta|"
    r"cornmeal|chickpea pasta|lentil pasta|gram flour|rice flour)\b", re.I)


# A line asking for a replacement names the food it wants to replace, so the food is the card's
# subject and not a fault in it: a vegan asking "what can i use instead of eggs" wants the list of
# substitutes, and the list says eggs.
SUBSTITUTE_ASK = re.compile(
    r"\b(?:instead of|in place of|rather than|substitute|alternative to|replacement for|"
    r"replace|what can i use (?:for|in)|swap (?:it |that )?for|do without|without)\b", re.I)


def _any_meal(banned):
    """The default list, changed only when the line has ruled an everyday dinner out."""
    if GLUTEN & banned:
        # Everything here is gluten free by construction: rice, potatoes and pulses, no bread,
        # pasta or flour. The egg and the cheese go when the same line rules them out too.
        egg = "" if {"egg", "eggs"} & banned else " and an egg"
        cheese = "hummus" if DAIRY & banned else "cheese"
        return ("Ten-minute dinners, all gluten free: rice fried with frozen veg" + egg +
                "; a jacket potato with beans and " + cheese +
                "; or a chickpea and tomato curry with rice. Tell me what is in the fridge and "
                "I will pick one.")
    if {"egg", "eggs"} & banned:
        if DAIRY & banned:
            return ("Ten-minute dinners: a chickpea and tomato curry with rice; pasta with garlic, "
                    "chilli and olive oil; or beans on toast with hummus. Tell me what is in the "
                    "fridge and I will pick one.")
        return ("Ten-minute dinners: a chickpea and tomato curry with rice; pasta with garlic, "
                "chilli and olive oil; or beans on toast with a little cheese or hummus. Tell me "
                "what is in the fridge and I will pick one.")
    if MEAT <= banned:
        return ("Ten-minute dinners: pasta with garlic, chilli and olive oil; a chickpea and "
                "tomato curry with rice; or eggs on toast. Tell me what is in the fridge and I "
                "will pick one.")
    return ANY_MEAL


# Words that say when to cook or how it should feel, never what to cook: a recipe "for tonight"
# or "something quick" is a meal question with no dish in it.
_NOT_A_DISH = frozenset((
    "tonight", "today", "now", "later", "tomorrow", "weekend", "evening", "lunchtime", "noon",
    "quick", "quickly", "fast", "easy", "easier", "simple", "cheap", "cheaper", "healthy",
    "healthier", "nice", "tasty", "good", "new", "different", "something", "anything", "nothing",
    "some", "one", "two", "few", "first", "family", "kids", "friends", "guests", "everyone",
    "vegetarian", "vegan", "gluten", "dairy", "free", "light", "filling", "cosy", "comfort",
))


def _cauliflower_rice(memory, understood):
    """Cauliflower rice, and the low-carb reason people ask for it in the same sentence."""
    words = {_fold(str(word)) for word in (understood.get("words") or [])}
    method = ("Grate or blitz a head of cauliflower into rice-sized bits, wrap it in a tea towel "
              "and squeeze out the water, then fry it in a little oil for 4 to 5 minutes with salt "
              "until it is hot but still has a bite. Do not boil it: that is what makes it soggy. "
              "One head makes four good portions and keeps three days in the fridge.")
    if words & {"carb", "carbs", "keto", "diet", "diabetes", "sugar", "low"}:
        return ("Cauliflower is one of the lowest-carb vegetables there is: about 3g of carbs per "
                "100g, against about 28g in cooked rice, so it works on a low-carb or diabetic "
                "plate. " + method)
    return method


def _leftover(folded, clean):
    """True when the food named has already been cooked: a leftover question, not a recipe."""
    return (any(word in LEFTOVER_WORDS for word in folded)
            or any(phrase in clean for phrase in LEFTOVER_PHRASES))


# Beans that will not soften, and beans with no time to soak, are the two things people write
# about dried pulses. Both are the same entry's question, so the entry reads the line rather
# than three entries guarding each other's lines.
_PULSES_HARD = re.compile(
    r"\b(?:still (?:hard|firm|crunchy|tough|chalky)|not soft(?:ening)?|wont (?:soften|go soft)"
    r"|will not (?:soften|go soft)|never soften|hard after|too hard|too firm|took ages"
    r"|been cooking (?:for )?(?:an|two|2|three|3) hours?)\b")


_PULSES_NO_SOAK = re.compile(
    r"\b(?:without (?:a )?soaking|without a soak|no soak(?:ing)?|skip(?:ped)? the soak"
    r"|skip(?:ping)? soaking|didnt soak|did not soak|forgot to soak|forget to soak"
    r"|no time to soak|havent soaked|have not soaked|not soaked|quick soak|quick-soak"
    r"|in a hurry|short on time|last minute|just cook|straight from the bag"
    r"|without the soak|unsoaked)\b")


# A tin or a jar is not a bag of dried beans: that line is a dish, and another entry has it.
_PULSES_TIN = re.compile(r"\b(?:tinned|canned|jarred|jar|tin|tins|packet|carton)\b"
                         r"|\bcans? of\b")


# A green bean, a runner, a broad bean and a mangetout are vegetables with a four-minute answer,
# and "my green beans are stringy" is dishes.py's. Only the dried pulses are this entry's.
_PULSES_FRESH = re.compile(
    r"\b(?:green|runner|broad|french|string|stringy|snap|mangetout|edamame|pea|peas)\b")


# An appliance does the cooking, and its own card says how: "how do i cook beans in a slow
# cooker" wants the slow cooker's times, not the soaking times. The kidney bean is the exception
# - raw kidney beans in a slow cooker are a safety line, and that one is this entry's.
# A dried bean is not the fresh pod however the line names it: "broad beans" is a fresh vegetable
# for four minutes in salted water, but "do broad beans need soaking" is a bag of them, and the
# soak is the whole question. These words take the fresh reading off the line.
_PULSES_DRIED = re.compile(
    r"\b(?:soak|soaks|soaked|soaking|overnight|quick soak|no soak|dried|dry|bag|bags|packet"
    r"|packets|tinned|tin|canned|can)\b")


_PULSES_APPLIANCE = re.compile(
    r"\b(?:slow cooker|slow cookers|crock ?pot|pressure cooker|pressure cookers|instant pot"
    r"|air fryer|air fryers|multicooker|multi cooker)\b")


_PULSES_KIDNEY = re.compile(r"\b(?:kidney|kidney beans?)\b")


def _pulses(memory, understood):
    """A bag of dried beans wants the soak and the time; a pan that will not soften wants why.

    Old beans and early acid are the two reasons a bean stays hard however long it cooks, and
    "can I skip the soaking" is a different answer again (the two-minute boil and the hour in
    the water), so this reads the line instead of putting all three in one card.
    """
    said = _words_and_text(understood)
    if (_PULSES_FRESH.search(said) and "split peas" not in said
            and not _PULSES_DRIED.search(said)):
        return None     # a green bean is a vegetable: four minutes in salted water, not a soak
    if _PULSES_TIN.search(said) and not _PULSES_HARD.search(said):
        return None     # a tin of beans is a dish: beans on toast, a chilli, a salad
    if _PULSES_APPLIANCE.search(said) and not _PULSES_KIDNEY.search(said):
        return None     # the appliance's own card has the times for its pot
    if _PULSES_HARD.search(said):
        return ("Old beans are usually the reason: a bag that has sat in the cupboard for years "
                "takes twice as long however you cook it. Keep it at a bare simmer with the lid "
                "just off, top it up with hot water, and give it another 20 to 30 minutes with a "
                "half teaspoon of bicarbonate of soda in the pan - and leave the salt, tomato and "
                "vinegar until the beans are soft, because acid early is the other thing that "
                "keeps the skins tough. Hard water does the same, so use filtered water if yours "
                "is very chalky.")
    if _PULSES_NO_SOAK.search(said):
        return ("You can skip the soaking: boil them hard for 2 minutes, take the pan off the "
                "heat and leave it covered for an hour, then simmer as usual - or cook them "
                "straight from the bag for 30 to 45 minutes longer and top up with hot water. "
                "Kidney beans are the one exception: boil them hard for 10 minutes before the "
                "simmer, and never cook them raw in a slow cooker.")
    return ("Dried chickpeas and beans want 8 hours of cold water, then 45 to 60 minutes of hard "
            "simmering; lentils need no soaking at all, just 20 to 30 minutes in the pan. Kidney "
            "beans must be boiled hard for 10 minutes, never slow cooked raw.")


# The shapes that ask for a plan for the week rather than a dish for tonight.
_PLAN_ASK = re.compile(
    r"\b(?:meal plans?|meal planning|planning meals|plan (?:my |the |a )?(?:week|meals)\b"
    r"|meals for the week|weekly meal|food plan|plan a week of meals)")


def _keeps_its_own_name(memory, understood, idea):
    """Whether the line names a food the pantry has a row for under that very word, and the
    dish about to be sent never says it.

    The dish table files the charcuterie together, so "what can I make with chorizo" was
    answered "do a bacon and egg hash" - a dish with no chorizo in it, about a food the person
    had not mentioned - while the pantry held a chorizo idea all along. Ham, kale, hummus and
    bean sprouts went the same way (bacon hash, a spinach frittata, a chickpea curry, beans on
    toast). A food is answered under its own name when the pantry has one for it: the idea for
    the food beats the idea for the group it was filed with.

    Only for a line that names one food, and only when the reply does not say the word: "what
    can I make with chicken breast" is answered about chicken and that is the same food.
    """
    from ..knowledge import meals

    words = [_fold(word) for word in (understood.get("words") or ())]
    named = []
    for place, word in enumerate(words):
        if _INGREDIENT_WORDS.get(word) != _INGREDIENT_WORDS.get(word, word):
            continue
        name = _INGREDIENT_WORDS.get(word)
        if name and _fold(name) == word and word not in named:
            named.append(word)
        # a two-word name ("pork belly") counts as one food, not as two
        if place + 1 < len(words):
            pair = word + " " + words[place + 1]
            if _INGREDIENT_WORDS.get(pair) and _fold(_INGREDIENT_WORDS[pair]) == pair:
                named.append(pair)
    if len(named) != 1:
        return False
    text = " ".join(words)
    if (any(word in LEFTOVER_WORDS for word in words)
            or any(phrase in text for phrase in LEFTOVER_PHRASES)):
        # A food that is already going over is a use-it-up question, and the dish table is the
        # one that answers it ("old bread" becomes crumbs; a plain bread idea is a loaf they do
        # not have): the food is named, and the idea for naming it is not the answer.
        return False
    if meals._diet_said(memory):
        # a diet said a turn ago has its own answer, and it is the one that names the food as
        # something to leave out: a plain idea about that food is the wrong reply
        return False
    if any(f"{marker} {named[0]}" in text for marker in ("old", "stale", "dry", "yesterday")):
        return False
    if meals._is_the_ruled_out_food(named[0], " ".join(words)):
        # The food is named in order to leave it out: "what can i cook without an onion" reached
        # the onion's own row and was answered with onion soup. The dish table reads the exclusion
        # and has a dinner the line can actually eat, so its idea is the answer and the row for
        # the food is not. The names differ by the group the pantry files them under - the line
        # says "fish" and the table rules out `white fish` - so the word is matched as a form of
        # the food rather than as a spelling.
        return False
    said = [_fold(word) for word in re.findall(r"[a-z']+", idea.lower())]
    return named[0] not in said


# Where a plant word comes from, it is the source and not the subject: "what can i do with a glut
# of courgettes from the allotment" is a courgette question, and so are the apples off the tree,
# the tomatoes in the greenhouse and the rhubarb from my plot. The preposition (and the
# determiner after it) is what tells the two apart.
_PLANT_SOURCE = re.compile(
    r"\b(?:from|off|out of|in|on|at)\s+(?:the\s+|my\s+|our\s+|a\s+|an\s+|his\s+|her\s+"
    r"|their\s+)?(?:" + "|".join(_PLANT_NOT_A_DINNER) + r")\b")


def _a_plant_not_a_dinner(line):
    """True when the line is about the plant rather than the fruit or the leaf on the plate."""
    low = " " + str(line or "").lower().replace("'", " ") + " "
    if not any(f" {word} " in low for word in _PLANT_NOT_A_DINNER):
        return False
    if (any(f" {word} " in low for word in _PLANT_KITCHEN_PLANT)
            and any(f" {word} " in low for word in ("bought", "buy", "buying", "got", "picked up"))):
        # Buying "a herb plant" is buying a thing to cook with - there is no herb called "herb"
        # to grow. The named herbs keep their growing cards ("i bought a basil plant"), and a
        # herb that is ailing keeps the plant-care card, because that is not a purchase.
        return False
    if any(f" {word} " in low for word in _PLANT_GARDEN_VERB):
        # A garden verb is the garden's question only when the garden has a row for the plant
        # or the line is a bush, a bare-root tree or a pot straight from the shop: standing aside
        # for a row that does not exist is how a pantry answer became an echo.
        return _the_garden_has_this_plant(line) or _a_plant_from_the_shop(line)
    if any(f" {phrase} " in low for phrase in _PLANT_BEARS):
        # The fruit is the subject now, even though no ask word is on the line: the pantry keys
        # the fruit and answers it.
        return False
    # A plant named as where the food came from is the pantry's line still: the subject is the
    # courgette or the apple, and the allotment is only its address. Every plant word being a
    # source is what makes the food the subject; one that is not ("i bought a lemon tree") is
    # the garden's.
    named = sum(low.count(f" {word} ") for word in _PLANT_NOT_A_DINNER)
    asked = (any(f" {word} " in low for word in _PLANT_COOK_ASK)
             or any(f" {word} " in low for word in _PLANT_DO_WITH))
    if named and asked and len(_PLANT_SOURCE.findall(low.replace("  ", " "))) >= named:
        return False
    if any(f" {word} " in low for word in _PLANT_COOK_ASK):
        return False
    # A plant the garden has nothing to say about stays the pantry's: standing aside there left
    # the person with an echo. "i bought a potted parsley", "i bought a blueberry bush" and
    # "i picked up a fig tree" each had a pantry answer and no garden row, so the stand-down was
    # a warm nothing. The garden rows are the test: if none of them takes the line, it is not
    # their question.
    return _the_garden_has_this_plant(line) or _a_plant_from_the_shop(line)


FEEDING_EATS = re.compile(
    r"\b(?:" + _FEEDING_ANIMALS + r")\b(?:\W+\w+){0,3}?\W+(?:eat|eats|eating|have|has|drink|"
    r"drinks|be\s+fed|be\s+given|be\s+allowed|allowed|take|tolerate)\b")


FEEDING_GIVEN = re.compile(
    r"\b(?:feed|feeding|fed|give|giving|gave)\b(?:\W+\w+){0,2}?\W+(?:my|our|the|a|an)?\W*"
    r"(?:" + _FEEDING_ANIMALS + r")\b")


FEEDING_SAFE_FOR = re.compile(
    r"\b(?:safe|ok|okay|fine|bad|good|toxic|poisonous|dangerous|harmful|lethal)\b"
    r"(?:\W+\w+){0,4}?\W+(?:for|to)\b(?:\W+\w+){0,2}?\W+(?:" + _FEEDING_ANIMALS + r")\b")


def _feeding_ask(line):
    """True when the line asks what an animal may eat, rather than what to cook with it."""
    low = " " + str(line or "").lower() + " "
    if any(word in low for word in FEEDING_NOT_FOOD):
        return False
    return bool(FEEDING_EATS.search(low) or FEEDING_GIVEN.search(low)
                or FEEDING_SAFE_FOR.search(low))


PET_HOME = re.compile(
    r"\b(?:in\s+the\s+(?:room|house|home|lounge|living\s+room|front\s+room|kitchen|bedroom|"
    r"garden)|indoors|hutch|cage|coop|aviary|litter\s+tray|is\s+called|named|kept\s+in)\b")


def _reads_as_a_pet(line):
    """True when the animal a line names is somebody's own, not the meat on the counter."""
    low = " " + str(line or "").lower() + " "
    if any(marker in low for marker in PET_NOT_FOOD):
        return False
    if _pet_not_dinner(line):
        return True
    owned = any(f"my {animal} " in low or f"our {animal} " in low
                for animal in PET_MEAT_ANIMALS)
    return owned and bool(PET_HOME.search(low))


def _pet_or_meat(line):
    """The answer for a line that names an animal it may own: a pet is not dinner, the meat is.

    "What can i cook with my rabbit in the room" was a braise on main before the pet gate, and a
    shrug after it. The line can mean either, so the reply says which reading it took and then
    gives the pantry's cooking for the meat. None when the line is a care question, an animal that
    has eaten something, or not a line about cooking at all: those have their own answers.
    """
    low = str(line or "").lower()
    if not any(word in low for word in PET_COOKING_ASK):
        return None
    if any(word in low for word in PET_CARE):
        return None
    if not _reads_as_a_pet(low):
        return None
    for name, (aliases, idea) in PANTRY.items():
        if name not in PET_ANIMALS + PET_MEAT_ANIMALS:
            continue
        if f" {name} " not in low and f" {name}s " not in low:
            continue
        meat = str(idea)
        head, _, rest = meat.partition(": ")
        if not rest or not head or head.lower().split()[0] not in name:
            rest = meat
        rest = rest.strip()
        if not rest:
            return None
        return ("That reads as a pet rather than a dinner, and I would keep it off the plate. "
                "If you meant the meat, " + rest[0].lower() + rest[1:])
    return None


def _meal_ideas(memory, understood):
    """Dinner ideas come from bot/knowledge/meals.py, one table of dishes by ingredient.

    This entry stays because the arbiter still routes meal questions here; the crowd and
    occasion paths answer a meal for a table when the table has no dish to offer.
    """
    from ..knowledge import meals

    words = understood.get("words")
    if not isinstance(words, list):
        words = " ".join(words or ()).split()
    line = str(understood.get("clean") or " ".join(str(word) for word in words))
    text = line
    turns = memory.get("turns")
    if isinstance(turns, list):
        text += " " + " ".join(str(turn.get("user") or "") for turn in turns[-4:]
                               if isinstance(turn, dict))
    if _pet_not_dinner(line):
        # "my rabbit ate the leftovers" is not a braise: the pets rows answer it. A line that does
        # ask what to cook with the animal it owns gets the reading and then the cooking.
        return _pet_or_meat(line)
    if _a_brew_not_a_dinner(line):
        # "what about milk first or last" and "is oat milk good in tea" are the brew, not a
        # dinner idea: the tea-milk row answers both
        return None
    if _PLAN_ASK.search(line.lower()):
        # A plan for the week is a method, not one dish: the useful answer is how to plan, and
        # the dish table would give a single dinner to a question about five of them.
        return ("Pick four dinners you already cook and put them on the fridge, then shop for "
                "just those - one double batch goes in the freezer for the night you are late "
                "home. Keep one night loose for eggs on toast or a takeaway, and plan whatever "
                "spoils first for the day after you shop.")
    if any(word in line.lower() for word in ("dessert", "puddings", "pudding", "afters",
                                             "ice cream", "sweet thing")):
        # A pudding is the end of the dinner, not another dinner: the dessert entry above
        # answers these lines, and a traybake is a reply to a different question.
        return None
    # A food the line only names in order to rule it out ("without an onion", "no pasta",
    # "i dont like mushrooms") is no more use than one they have not got, and the pantry reads
    # every food it knows. The older ban list names only the foods a diet or an allergy is said
    # in, so the food named beside "without" was read as what to cook with, and the idea for it
    # was the answer to a dinner with none of it.
    # A food they are short of is left out of every meal, not only breakfast: "im out of eggs
    # what can i have for dinner" was answered "Scrambled eggs: 3 eggs on a low heat". It is not
    # a diet - the person may eat eggs tomorrow - so it is read for this answer only.
    banned = (frozenset(_no_meat_also_means_fish(_excluded(text)))
              | frozenset(_short_of_food(text))
              | frozenset(negated_ingredients(understood)))
    # A meal for a table, or a day that matters, is the crowd answer: twelve people are not
    # a weeknight pick. Otherwise the dish table answers, and only a line it has no dish for
    # gets the generic list.
    # "for 20 minutes" is a clock, not twenty people: the crowd count reads the line
    # without the times in it.
    table = re.sub(r"\bfor\s+\d{1,3}\s*(?:min|mins|minute|minutes|hour|hours|sec|seconds)\b",
                   " ", text).lower()
    # A line that says who cannot eat what keeps the dish table: one tray of chicken
    # thighs is the wrong answer to a vegetarian dinner party.
    # Only a line that asks for a meal can get the crowd answer: "maybe i will cook her
    # favourite thing", said about someone who has died, is not a request for a traybake.
    asking = str(understood.get("intent") or "") != "news" and (
        str(understood.get("kind") or "") == "question"
        or str(understood.get("intent") or "") in ("question", "request")
        or any(word in line.lower() for word in (
            "what", "idea", "ideas", "something", "suggest", "suggestion", "dinner",
            "dinners", "meal", "meals", "menu", "tea", "supper", "lunch", "cook for",
            "make for", "feed", "recipe", "anything", "any", "need", "want", "party",
            "guests", "everyone")))
    # A table of three to five is still a table when the line says a party or guests rather than
    # only a number: "dinner party for four" was the crowd card with "feeds eight from one oven"
    # in it, and standing it down from the crowd answer sent it to the ten-minute list instead.
    table_count = _crowd(table)
    at_table = asking and not _says_a_diet(line) and (
        table_count >= 6
        or (table_count >= 3
            and any(phrase in line.lower() for phrase in _CROWD_PHRASES))
        or (
            _occasion(table) and any(
                phrase in line.lower() for phrase in ("what should i cook", "what can i cook",
                                                      "what shall i cook", "what to cook",
                                                      "what to make", "meal", "dinner", "cook",
                                                      "no idea"))))
    if at_table:
        return _crowd_or_any(table, banned)
    idea = meals.suggest(memory, understood)
    if idea and banned and _bans((), str(idea), banned):
        # The dish table does not read a diet: "im egg free what can i have for tea" was answered
        # "How about an omelette: whisk two or three eggs...". A dish whose own words name a food
        # they cannot eat is not an idea for them, and the list below reads the diet.
        idea = None
    if idea and _keeps_its_own_name(memory, understood, idea):
        # The food has a row of its own, and the dish was built for the group it was filed
        # with: the own-name idea is the answer, said about the food they named.
        words = understood.get("words")
        if not isinstance(words, list):
            words = " ".join(words or ()).split()
        own = _pantry_idea([str(word) for word in words] + str(
            understood.get("clean") or "").split(), banned, line.lower())
        if own and isinstance(own[1], str) and own[1].strip():
            idea = own[1]
    if idea:
        return idea
    # The dish table has no row for this food, but the pantry below knows a hundred and
    # forty of them: "what can i make with parsnips" is the pantry's roast parsnips, and
    # "with feta" its baked feta, where the generic quick list is worse than either.
    asks_food = (understood.get("topic") in ("cooking", "food-and-drink")
                 or any(phrase in line.lower() for phrase in MEAL_ASK_PHRASES))
    if asks_food:
        from_pantry = meal(understood, banned=banned, memory=memory)
        if (isinstance(from_pantry, str) and from_pantry.strip()
                and not _bans((), from_pantry, banned)):
            return from_pantry
    if meals.unknown_food(understood):
        # A food nobody here knows either: the line is about an ingredient, and a dish
        # picked at random answers a different question.
        return None
    if not banned and re.search(r"\bwithout\b", line.lower()) and not _says_a_diet(line):
        # "what can i make without money" leaves out nothing this kitchen can cook around. The
        # word after "without" can be anything a line is short of, and ten-minute dinners are an
        # answer to a question nobody asked.
        return None
    if _says_diabetes(text):
        # The balance of the plate, not a food to leave out: the dish table has nothing to say
        # about it, so "any dinner ideas" after "my sister is diabetic" was the plain pasta
        # list. Read from the recent turns, so the follow-up gets the same answer as the line
        # that named the condition.
        return DIABETIC_PLATE
    return _any_meal(banned)


def _pantry_idea(words, banned, clean=""):
    """The pantry's idea for the first food the line names, when no meal idea covers it.

    MEAL_IDEAS names forty foods and the pantry a hundred and forty, so "what can I make with
    bananas" or "with cabbage" fell past both and got the default ten-minute list while the
    pantry held a good answer all along. Same shape as the loop above: earliest food in the
    line wins, and an idea the line has ruled out is skipped.

    A name here has to be that name: `_same` reads a prefix as the same word, which is right for
    eggs/egg but made "peanut butter" a pea and "bean sprouts" the beans on toast, so the match
    is the folded word (and `NOT_THIS_FOOD` steps the name aside when a word in front makes it a
    different food).
    """
    found = None
    # Where the name was found and how much of the line it covers, so a longer name wins the same
    # spot: "beef shin" is the braise row, not the steak the word "beef" would give it.
    reached = None
    for name, (aliases, idea) in PANTRY.items():
        if _bans(aliases, idea, banned):
            continue
        if any(phrase in clean for phrase in NOT_THIS_FOOD.get(name, ())):
            continue
        for alias in aliases:
            parts = alias.split()
            for start in range(len(words) - len(parts) + 1):
                if all(_fold(words[start + offset]) == _fold(parts[offset])
                       for offset in range(len(parts))):
                    spot = (start, -len(parts))
                    if reached is None or spot < reached:
                        reached = spot
                        found = (start, idea)
                    break
    return found


def _crowd_or_any(text, banned):
    """The fallback list, unless the line is a meal for a table or an occasion."""
    if _table_text(text):
        return _crowd_meal(banned, _occasion(text), _crowd(text))
    if _occasion(text) and any(
            phrase in text for phrase in ("what should i cook", "what can i cook",
                                          "what shall i cook", "what to cook", "what to make",
                                          "meal", "dinner", "cook", "no idea")):
        # "it's my mum's 70th birthday, what should I cook" names no ingredient and no number:
        # a ten-minute dinner is the wrong answer to a day like that.
        return _crowd_meal(banned, True, _crowd(text))
    return _any_meal(banned)


# What a breakfast is made of, and what is in it, so a diet is read against the food rather than
# hand-written into a branch of its own. The branches used to be eggs, dairy and nuts, and
# "im gluten free what can i have for breakfast" fell through all three to the plain answer and
# offered "eggs on toast" - toast is the one thing a coeliac cannot have. A table also composes:
# a vegan coeliac with a nut allergy gets the porridge and the fruit, not a text that suits one.
# `needs` is the food a line has to allow for the idea to be offered.
def _porridge(banned):
    """Porridge, made with what the diet allows.

    Ordinary oats are grown and milled alongside wheat, so a coeliac has to look for oats
    labelled gluten free: the plain line was right for every other diet and handed the one
    person who must not have wheat a bowl of it.
    """
    if GLUTEN & banned:
        # "gluten free oats" is what the box says, so it is what the shopper looks for.
        milk = "oat milk" if DAIRY & banned else "milk"
        return "Porridge made with gluten free oats and " + milk
    if DAIRY & banned:
        return "Porridge made with oat milk and a spoon of jam"
    return "Porridge with a banana and a spoon of jam"


BREAKFAST_CHOICES = (
    # porridge is oats and water: the dairy in it is only ever what it is made with
    (frozenset(), lambda banned: _porridge(banned)),
    # The order is the order the plain answer gives, so a diet that rules out one thing still
    # gets the familiar breakfast: the toast ideas come before the ones nobody thinks of first.
    (EGGS | GLUTEN, "eggs on toast"),
    (GLUTEN | NUTS, "toast with peanut butter"),
    (GLUTEN, "beans on toast"),
    (GLUTEN, "toast with hummus"),
    (DAIRY | GLUTEN, "yoghurt with fruit and oats"),
    (DAIRY, "rice cakes with cheese"),
    (EGGS, "a boiled egg with fruit"),
    (NUTS, "a banana with a handful of nuts"),
)


# "im out of eggs", "we have none left": a food they are short of is not a food they cannot
# eat, and the plain list may name the very thing they have run out of. The shortage is read as
# an exclusion for this turn, which is all a kitchen needs: the list is built without it.
SHORT_OF_ASK = re.compile(r"\b(?:out of|ran out of|run out of|none left|nothing left|"
                          r"short of|outta|havent got|haven't got)\s+")


def _short_of_food(text):
    """The foods a line says they have none of, as opposed to cannot eat."""
    found = set()
    for match in SHORT_OF_ASK.finditer(str(text or "").lower()):
        found |= _foods_in_list(_list_words(str(text).lower()[match.end():match.end() + 60]))
    return found


def _rushed(banned):
    """The second sentence of a diet breakfast, so the answer is two sentences like the plain one.

    One sentence is not only short: "and for lunch" after it was narrowed to the only clause that
    shared a word with the line ("Keeps you going until lunch."), because the sentence-choosing
    in `answers` reads a one-sentence answer differently from a two-sentence one. The plain text
    ends with the egg, and that is the one thing an egg-free person cannot do.
    """
    if not (EGGS & banned):
        return (" If mornings are rushed, boil an egg the night before and take a piece of fruit.")
    return (" If mornings are rushed, put it out the night before and eat it on the way, because "
            "a breakfast you can pick up beats one you skip.")


def _breakfast_ideas(memory, understood):
    """Breakfast for someone who has just said what they cannot eat."""
    text = _said_so_far(understood, memory)
    banned = _no_meat_also_means_fish(_excluded(text))
    # A shortage is not a diet, but it is a food the breakfast cannot name: "im out of eggs" got
    # a list that began with eggs, and the baking-swap card.
    short = _short_of_food(text)
    if not banned and not short:
        return ANY_BREAKFAST
    banned = banned | short
    ideas = []
    for needs, idea in BREAKFAST_CHOICES:
        if needs & banned:
            continue
        ideas.append(idea(banned) if callable(idea) else idea)
        if len(ideas) == 3:
            break
    if not ideas:
        # a line that rules out everything: say what is left rather than name a food twice
        return ("A bowl of fruit and a glass of juice, or a slice of toast with jam if bread is "
                "allowed" + BREAKFAST_TAIL + _rushed(banned))
    if len(ideas) == 1:
        return ideas[0] + BREAKFAST_TAIL + _rushed(banned)
    said = ", ".join(ideas[:-1]) + (" or " if len(ideas) == 2 else ", or ") + ideas[-1]
    return said + BREAKFAST_TAIL + _rushed(banned)


def _lunch_ideas(memory, understood):
    """A packed lunch for someone who has just said what they cannot eat."""
    words = understood.get("words")
    if not isinstance(words, list):
        words = " ".join(understood.get("words") or []).split()
    text = _said_so_far(understood, memory)
    banned = _no_meat_also_means_fish(_excluded(text))
    if not banned:
        return ANY_LUNCH
    # A filling is usable when none of the foods it is made of is ruled out.
    fillings = [name for name, needs in (("cheese", DAIRY), ("tuna", {"tuna"}),
                                        ("ham", {"ham"}), ("egg", EGGS),
                                        ("hummus", set()), ("avocado", set()),
                                        ("roasted vegetables", set()))
                if not (needs & banned)]
    if "gluten" in banned:
        if fillings:
            return ("For a lunch that is not a sandwich: a rice or potato salad with " +
                    ", ".join(fillings[:3]) + ", fruit and a drink. Cook extra dinner and take the "
                    "leftovers in a tub and it is quicker still. Keep it in a cool bag until lunch.")
        return ("For a lunch that is not a sandwich: cook extra dinner and take the leftovers in a "
                "tub with rice, potatoes or salad, fruit and a drink. Keep it in a cool bag until "
                "lunch.")
    if not fillings:
        return ("Cook extra dinner and take the leftovers in a tub with fruit and something crunchy: "
                "that is a packed lunch in five minutes. Keep it in a cool bag until lunch.")
    reply = ("A sandwich or wrap with " + ", ".join(fillings[:3]) + ", fruit, something crunchy and "
             "a drink is a packed lunch in five minutes. Cook extra dinner and take the leftovers "
             "in a tub and it is quicker still.")
    if banned:
        return reply + " Keep it in a cool bag until lunch."
    return reply + " Keep anything with meat, fish, egg or dairy cold until you eat it."


# A thing frozen by an app, not by a freezer: "i lost my bank card, should i freeze it first"
# is the bank's answer, and a food row that reads "freeze it" as a freezer took that turn away
# from the money card that had been giving it. The words are what can be frozen that is not
# food, and any of them in the line is enough for this row to say nothing.
_NOT_A_FREEZER = frozenset("""
    card cards account accounts subscription subscriptions membership phone credit file
    report reports score payment payments direct debit standing order
""".split())


def _freeze_food(memory, understood):
    """The food the line names gets its own answer; a thing named earlier gets that one too."""
    words = understood.get("words")
    if not isinstance(words, list):
        words = " ".join(understood.get("words") or []).split()
    words = [str(word).lower() for word in words]
    if _NOT_A_FREEZER & {word.strip(".,!?\"'") for word in words}:
        # a card, an account, a subscription: someone else's answer
        return None
    fact = _a_freeze_fact(words)
    if fact is not None:
        return fact
    if not _points_at_something(words):
        # no dish in the line and nothing pointed at: this is not a freezing question about a
        # thing, so the row says nothing and a lower one gets the turn
        return None
    earlier = _the_dish_the_chat_names(memory)
    if earlier is not None:
        return earlier
    return FREEZE_ANY


SOYA = frozenset("soya soy soya bean soy bean soya sauce tofu edamame".split())


def _nut_free(memory, understood):
    """A nut allergy: food that is safe, and the cake question when that is what is cooking."""
    # This card is a nut-free list, and an allergy said in the same breath used to go unanswered:
    # "peanuts and shellfish" got the list and not a word about the shellfish. Each other family
    # gets the one sentence that names what to keep out of it.
    banned = avoids(memory)
    if (GLUTEN | EGGS) & banned:
        # The list itself names pasta and eggs, so for a coeliac or an egg allergy it is the wrong
        # list and the turn goes to whoever answers that.
        return None
    also = [ALSO_OUT[name] for name in ("shellfish",) if FAMILIES[name] & banned]
    if SOYA & banned:
        also.append(ALSO_OUT["soya"])
    turns = memory.get("turns")
    recent = ""
    if isinstance(turns, list):
        recent = " ".join(str(turn.get("user") or "") for turn in turns[-2:]
                          if isinstance(turn, dict)).lower()
    if "cake" in recent or "bake" in recent or "birthday" in recent:
        return ("Then go for a plain chocolate sponge: cocoa, flour, eggs, butter and sugar, no "
                "nuts. Check the chocolate, the icing sugar and any sprinkles for 'may contain "
                "nuts', and keep the tin and worktop clean if the allergy is serious.")
    return ("Plenty: meat, fish, eggs, rice, pasta, potatoes and plain fruit and veg are all "
            "nut-free, so pasta with tomato sauce or roast chicken and potatoes works. Check the "
            "labels on chocolate, muesli, pesto and satay, and anything marked 'may contain "
            "nuts'." + (" " + " ".join(also) if also else ""))


# The bake decides which of the three swaps matters: pancakes need no egg at all, a scone is a
# rubbing-in job, and a brownie is all fat and egg, so one vegan answer for all of them was telling
# a pancake line about a cake.
def _vegan_bake(memory, understood):
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    folded = {_fold(word) for word in words}
    # the folded forms, so "brownies" and "cookies" are the words they are
    if folded & {_fold(one) for one in ("pancake", "pancakes", "crepe", "crepes", "waffle",
                                        "waffles", "drop scone")}:
        return ("Pancakes need no egg at all: 100g of plain flour, a teaspoon of baking powder, a "
                "pinch of salt and 300ml of unsweetened soya or oat milk, whisked and rested 20 "
                "minutes, then cooked in a little oil. The first one always fails, so make it the "
                "cook's. For thicker American ones, add a tablespoon of oil and a teaspoon of "
                "sugar.")
    # A scone and a pastry case are both a rubbing-in job, but they are not the same job: a scone
    # is raised with self-raising flour and cut into rounds, and a tart case is plain flour, cold
    # fat and a rest in the fridge. One answer for both was giving a pastry question a scone recipe.
    if folded & {_fold(one) for one in ("scone", "scones", "drop scone", "drop scones")}:
        return ("Rub 50g of a hard vegan block margarine, or 40ml of neutral oil, into 225g of "
                "self-raising flour, then bring it together with about 120ml of unsweetened soya "
                "milk and a squeeze of lemon. Pat it out, cut the scones and bake at 220C for 12 "
                "to 15 minutes. The block margarine, not a tub spread, is what makes it short.")
    if folded & {_fold(one) for one in ("pastry", "shortcrust", "shortcrust pastry", "pie",
                                        "pie crust", "tart", "tarts", "tart case", "flan",
                                        "quiche", "quiche case")}:
        return ("Vegan shortcrust is the same weights with the fat swapped: 225g plain flour, a "
                "pinch of salt and 100g of a hard vegan block margarine (or 90ml of neutral oil), "
                "rubbed in until it looks like breadcrumbs, then cold water a spoon at a time until "
                "it just comes together. Rest it 30 minutes in the fridge, roll it thin on a floured "
                "board, and blind bake at 190C (170C fan) for 15 minutes for a tart or quiche case. "
                "Brush the top with plant milk rather than egg and it browns just as well.")
    if folded & {_fold(one) for one in ("crumble", "crumbles", "fruit crumble", "cobbler")}:
        return ("Swap the butter and nothing else changes: rub 100g of a hard vegan block "
                "margarine into 200g plain flour with 75g sugar until it looks like breadcrumbs, "
                "scatter it over the fruit and bake at 190C (170C fan) for 35 to 40 minutes, until "
                "the fruit bubbles at the edges and the top is golden.")
    if folded & {_fold(one) for one in ("biscuit", "biscuits", "cookie", "cookies",
                                        "shortbread")}:
        return ("Biscuits are the easiest bake to make vegan: a hard block margarine in place of "
                "the butter at the same weight, and a tablespoon of plant milk if the dough will "
                "not come together. No egg and no raising agent needed, so nothing else changes, "
                "and they keep a day or two less.")
    # A flapjack is oats held together with fat and syrup: there is no egg to replace, so the
    # butter is the only swap, and it was being told "for brownies, two flax eggs...".
    if folded & {_fold(one) for one in ("flapjack", "flapjacks", "oat bar", "oat bars",
                                        "granola bar", "granola bars")}:
        return ("A flapjack needs no egg, so the only swap is the butter: 150g of a hard vegan "
                "block margarine or 120ml of neutral oil with 120g of golden syrup is the sticky "
                "part. Melt them together, stir in 300g of porridge oats, press it into a lined "
                "20cm tin and bake at 180C (160C fan) for 20 to 25 minutes. Let it go completely "
                "cold in the tin or it will crumble when you cut it.")
    # Bread is the one bake with no egg and often no fat at all, so "vegan bread" was being told
    # about flax eggs in a cake. An enriched loaf - banana bread, brioche, a milk loaf - is a cake
    # in a loaf tin and keeps the swaps above.
    if (folded & {_fold(one) for one in ("bread", "loaf", "loaves", "roll", "rolls", "baguette",
                                         "focaccia", "pizza", "pizza dough", "flatbread", "naan")}
            and not folded & {_fold(one) for one in ("banana", "carrot", "courgette", "zucchini",
                                                     "apple", "date", "pumpkin", "lemon", "fruit",
                                                     "soda", "cake", "brioche", "challah")}):
        return ("Ordinary bread is vegan already: flour, water, yeast and salt, with oil or a hard "
                "block margarine where the recipe wants a fat, and sugar feeds the yeast without "
                "leaving any behind. Only an enriched loaf needs a swap - oil for the butter, plant "
                "milk for the milk, and golden syrup for the honey. Check a bought loaf, though: "
                "milk powder and dried egg turn up in cheap sliced bread and in brioche.")
    if folded & {_fold(one) for one in ("brownie", "brownies", "blondie", "blondies")}:
        return ("For brownies, two flax eggs do the job: a tablespoon of ground flaxseed and "
                "three of water each, left five minutes to go gluey. Use an oil-based or vegan "
                "block margarine for the butter and keep the oven 10C lower, because brownies are "
                "meant to come out fudgy and the flax makes them catch sooner.")
    return ("A cake takes three swaps: 60g of yoghurt or half a mashed banana, or a flax egg (a "
            "tablespoon of ground flaxseed and three of water, left five minutes), for each egg; "
            "unsweetened soya or oat milk for the milk; and a block margarine or 80g of neutral oil "
            "for every 100g of butter. Add an extra half teaspoon of baking powder, because the egg "
            "was doing some of the lifting, and give it five minutes longer in the oven. Soya milk "
            "browns best, and a sponge made this way keeps a day less.")


# "is oil a good replacement for butter" wanted the same answer as "what can i use instead of
# butter" and got a shrug, because nothing in this gate was the word people write.
_SWAP_ASK = ("instead", "substitute", "swap", "replace", "replacement", "alternative",
             "without",
             "what can i use", "what do i use", "what should i use", "what else can i use",
             "ran out", "run out", "havent got", "haven't got", "dont have", "don't have",
             # A shortage is the same question as a swap: "im out of butter" wants what stands
             # in for butter. The subject is in the phrase because "out of" alone is the oven and
             # the fridge ("how long can butter stay out of the fridge" is a keeping line).
             "im out of", "i'm out of", "were out of", "we're out of", "are out of",
             "im all out",
             "i'm all out", "out of stock of", "none of", "none left", "nothing left",
             "no longer have",
             # A statement of having none is the same question as a swap: the foods it may
             # name are listed in _HAVE_NONE above, off the bare verb.
             *_HAVE_NONE,
             # "egg free cake recipe" and "a cake with no eggs" are the same question as
             # "what can i use instead of eggs", and the scrambled-eggs entry was taking the first.
             "egg free", "egg-free", "eggless", "no egg", "no eggs")


# The words that ask what is *in* a food rather than how to cook it. A nutrient column is a
# different question about the same food, so an egg asked for its portion must not be told how
# long to boil: "boiled egg calories" and "boiled egg protein" were both the six-to-ten-minute
# answer, because the timing entry matches "egg" and "boiled" and the portion entries match lower.
_NUTRIENT_ASK_WORDS = (tuple(word for word, _column in _NUTRIENT_WORDS)
                       + ("calorie", "calories", "cals", "kcal", "kilocalories", "nutrition"))


# "A bowl of cereal", "a plate of chips": an amount this table cannot work out from its portion.
# No figure is better than the figure for a different amount.
_AMOUNT_ASKED = re.compile(r"\d|\b(?:half|quarter|dozen|pints?|litres?|liters?|bowls?|plates?|"
                           r"glasses?|mugs?|cups?|slices?|pieces?|portions?|servings?|tins?|"
                           r"spoons?|tablespoons?|teaspoons?)\b")


def _nutrients(memory, understood):
    """What an ordinary portion of the food the line names holds of the nutrient it asks about."""
    clean = (understood.get("clean") or "").lower()
    if not clean:
        return None
    # A nutrient word or a food word typed a letter short gets nowhere, and the reading already
    # repairs it - in `plain`, "the same words with each one repaired in place", which nothing in
    # the knowledge base reads. "how much protien in chicken" was a hedge with the figure one
    # repaired word away. Each word is looked for in the line as typed first, so a line spelt
    # right reads exactly as it did, and the repair is only consulted when that found nothing.
    # The amount stays the line as typed: `plain` says the digits out as words.
    plain = (understood.get("plain") or "").lower()
    if plain == clean:
        plain = ""
    column = _nutrient_asked(clean)
    read = clean
    if column is None and plain:
        column = _nutrient_asked(plain)
        read = plain if column is not None else clean
    if column is None:
        return None
    found = _nutrient_food(read, FOOD_NUTRIENTS)
    if found is None and plain:
        found = _nutrient_food(plain if read == clean else clean, FOOD_NUTRIENTS)
    if found is None:
        return None
    food, count = found
    subject, portion, numbers = FOOD_NUTRIENTS[food]
    if column not in numbers:
        # the food is in the table but not for this nutrient: a pass, not "none of it"
        return None
    value = numbers[column] * count
    # the amount the line names, when the row can be measured against it
    scaled, said_amount = None, None
    if count == 1:
        weighed = _weight_in_the_line(clean, portion)
        if weighed is not None:
            scaled, said_amount = weighed
            if abs(scaled - 1.0) < 0.01:
                scaled = None
        elif _portion_size(portion) is None:
            # "a bowl of cereal" for a row written as "a medium one": an amount this table cannot
            # work out, and no figure is better than the figure for a different amount. An amount
            # word that is the row's own thing ("a slice of bread" for a slice) is not an amount.
            for word in _AMOUNT_ASKED.findall(clean):
                if not word:
                    return None
                if word in portion.lower() or _plurals(word) in portion.lower():
                    continue
                if word in subject.lower() or _plurals(word) in subject.lower():
                    continue
                return None
    said = subject[:1].upper() + subject[1:]
    if count > 1:
        # "two eggs" is twice an egg, so the portion is the count and the subject goes plural.
        # The plural goes on the noun that is being counted, not always the first word: "two
        # chocolate bars", not "two chocolates bar", and "two digestive biscuits". In "a slice of
        # bread" the counted noun is the one before "of".
        pieces = said.split()
        if pieces[0] in ("A", "An"):
            pieces = pieces[1:]
        head = pieces.index("of") - 1 if "of" in pieces else len(pieces) - 1
        pieces[head] = _plurals(pieces[head])
        said = ("%g " % count if count != int(count) else
                {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                 9: "Nine", 10: "Ten"}.get(int(count), str(int(count)))) + " " + " ".join(pieces)
        subject = said
        portion = ""
    name = NUTRIENT_COLUMNS[column][1]
    unit = "mg" if column in ("iron", "calcium", "potassium") else "g"
    plural = count > 1 or food in _CALORIE_PLURAL or subject[:2] not in ("a ", "an", "A ", "An ")
    if scaled:
        # the line asked for its own weight, so that is the subject: "100g of chicken has ..."
        said = said_amount[:1].upper() + said_amount[1:]
        if food not in said.lower():
            said += " of " + food
        value *= scaled
    amount = _figure(value) if value else None
    if amount is None:
        sentence = "%s %s no %s to speak of" % (said, ("have" if plural else "has"), name)
    else:
        sentence = ("%s %s about %s%s of %s" % (said, ("have" if plural else "has"), amount,
                                                unit, name))
    if portion and portion != "one" and not scaled and portion.lower() not in said.lower():
        sentence += " (%s)" % portion
    sentence += "."
    if column == "protein" and value:
        if value >= 50:
            sentence += " That is more protein than an adult needs in a day."
        else:
            for share, word in _PROTEIN_SHARES:
                if value / 50.0 >= share:
                    # "most of a day's protein" is said without a hedge on the number
                    hedge = "" if word == "most" else "about "
                    sentence += (" That is %s%s of a day's protein for an adult."
                                 % (hedge, word))
                    break
    if column in NUTRIENT_CONTEXT:
        sentence += " " + NUTRIENT_CONTEXT[column]
    return sentence


def _calories(memory, understood):
    """The calories in the food the line names, from FOOD_CALORIES."""
    clean = understood.get("clean") or ""
    # The same repair the nutrient reader uses, made once for the whole line: when no food the
    # tables hold is named in the line as typed, the line with its words repaired is read
    # instead. "how many calories in a bananna" is a hedge with the figure one repaired word
    # away. A line that names a food already reads exactly as it did.
    plain = understood.get("plain") or ""
    if plain and plain != clean and not _names_a_food(clean):
        clean = plain
    if not any(word in clean for word in CALORIE_ASKS):
        return None
    if any(food in clean for food in _CALORIE_OWN):
        return None
    # Read as whole words: "dough" inside "sourdough" turned the sourdough slice down, and the
    # list is of dish words, not of letter runs.
    if any(re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", clean)
           for word in _CALORIE_NOT_A_DISH):
        return None
    words = re.findall(r"[a-z0-9']+", clean)

    def _part_of_a_dish(name):
        """True when the line goes on to name a dish after this one: "chicken soup", "coffee cake".

        The meal table is matched before the ingredient table's own check, so a compound it does
        not hold landed on its first word and gave a confident number for a food nobody asked
        about: "how many calories in chicken soup" was a portion of roast chicken, and "coffee
        cake" was a mug of white coffee. A dish word after the name means this name is an
        ingredient of the dish, so the next candidate is the one to read.
        """
        tail = name.split()[-1]
        for i, word in enumerate(words):
            if word == tail:
                after = words[i + 1] if i + 1 < len(words) else None
                return after in _CALORIE_DISH
        return False

    meal = None
    for dish in sorted(FOOD_CALORIE_MEALS, key=len, reverse=True):
        if _part_of_a_dish(dish):
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(dish) + r"(?![a-z0-9])", clean):
            meal = dish
            break
    if meal:
        subject, portion, count = FOOD_CALORIE_MEALS[meal]
        said = subject[:1].upper() + subject[1:]
        return f"{said} is about {count} calories ({portion})."
    matches = [food for food in FOOD_CALORIES
               if re.search(r"(?<![a-z0-9])" + re.escape(food) + r"s?(?![a-z0-9])", clean)]
    if not matches:
        # "how many calories in a bananna" is the same slip the nutrient reader now reads: the
        # figure is in the table and the line only has one letter wrong.
        slipped = _the_food_named_by_a_slip(words, FOOD_CALORIES)
        if slipped is None:
            return None
        matches = [slipped[0]]
    best = max(matches, key=len)
    # another food from the table in the same line: "chicken and chips" is not a portion of
    # chips. A name inside the winner is the same portion - "milk" in "a glass of milk" - so the
    # table can carry the short name beside the portioned one.
    if any(food not in best for food in matches):
        return None
    head, tail = best.split()[0], best.split()[-1]
    before = after = None
    for i, word in enumerate(words):
        if word == tail:
            after = words[i + 1] if i + 1 < len(words) else None
            back = i - len(best.split()) + 1
            before = words[back - 1] if back >= 1 else None
    if after and (after in _CALORIE_DISH or after in _CALORIE_JOIN):
        return None
    if before and before in _CALORIE_JOIN:
        return None
    subject, portion, count = FOOD_CALORIES[best]
    said = subject[:1].upper() + subject[1:]
    # "a packet of crisps" is one thing, so the subject decides the verb, not the count.
    verb = "are" if best in _CALORIE_PLURAL and subject[:2] not in ("a ", "an") else "is"
    return f"{said} {verb} about {count} calories ({portion})."


GLUTEN_FACT_ASKS = tuple(
    [ask for ask in GLUTEN_FREE_ASKS if ask not in GLUTEN_FACT_DIET]
    + ["free of gluten", "gluten in it", "have gluten", "has gluten", "contain wheat"])


# Every food the table can answer about, so a new food added above is answerable by itself.
GLUTEN_FACT_FOODS = tuple(sorted(MADE_OF))


# The staples where the swap sentence reads as an answer; on a sauce or a condiment "rice,
# potatoes or a corn pasta do the same job" is advice for the wrong dish.
GLUTEN_FACT_SWAPS = frozenset(
    "bread toast pasta spaghetti noodles couscous pastry cake cakes biscuit biscuits cracker "
    "crackers pitta flour crumpet bagel wrap wraps barley rye semolina scone scones pizza "
    "sandwich".split())


# A fact about a food is asked as a question. "im coeliac and i miss pasta" has the ask and the
# food in it and is telling us something, not asking whether pasta has gluten: the answer there is
# what to buy instead, and it is the row below that has it. "can i make bread without gluten" is
# a question and is still a how-to, so the making words are read with the food taken out of the
# line: "baking powder" is a food, and "baking" in it is not the verb.
GLUTEN_FACT_OPENING = re.compile(
    r"^\s*(?:is|are|does|do|did|can|could|should|would|will|was|were|has|have)\b", re.I)


GLUTEN_FACT_MAKING = re.compile(
    r"\b(?:make|makes|making|bake|bakes|baking|cook|cooks|cooking|recipe|recipes|how do i|"
    r"how can i|how to|homemade|from scratch)\b", re.I)


def asks_a_gluten_fact(understood):
    """Whether this line, in its own words, asks the yes or no about one food.

    The reading a line gets can carry the last few turns, so "what can i do with butter beans"
    after "im coeliac" reaches the gluten rows on a word it does not say. This is a guard, so the
    row is never even chosen for such a line and the card that answers it keeps its turn.
    """
    if not isinstance(understood, dict):
        return False
    clean = understood.get("clean") or ""
    if not GLUTEN_FACT_OPENING.match(clean):
        return False
    lowered = clean.lower()
    if not any(ask in lowered for ask in GLUTEN_FACT_ASKS):
        return False
    food = _food_named(clean)
    if food is None:
        return False
    return not GLUTEN_FACT_MAKING.search(lowered.replace(food, " "))


def _free_of_gluten_fact(memory, understood):
    """The yes or no about one food, from the families the table says its usual recipe is made of."""
    clean = understood.get("clean") or ""
    if not GLUTEN_FACT_OPENING.match(clean):
        return ""
    food = _food_named(clean)
    if food is None:
        return ""
    if GLUTEN_FACT_MAKING.search(clean.lower().replace(food, " ")):
        return ""
    if food in GLUTEN_FACT_NOT_PLAIN:
        return GLUTEN_FACT_NOT_PLAIN[food]
    # "is gluten free bread ok" is not "is bread gluten free" the other way round: the words in
    # front of the food say it is the free-from version, and that line belongs to the food's own
    # safety answer. This row only answers the fact, so it stands back.
    phrase = r"\s+".join(re.escape(part) for part in food.split())
    if re.search(r"\b(?:[a-z]+)\s+free\s+" + phrase + r"\b", clean.lower()):
        return ""
    named = _named_as(clean, food)
    plural = _is_plural(food)
    if GLUTEN & MADE_OF[food]:
        said = "are made with wheat flour" if plural else "is made with wheat flour"
        reply = "No: " + named + " " + said + ", so it is not gluten free."
        if food in GLUTEN_FACT_NAMED_SWAP:
            return reply + " " + GLUTEN_FACT_NAMED_SWAP[food]
        if food in GLUTEN_FACT_SWAPS:
            swap = FAMILY_SAY[id(GLUTEN)][1]
            return reply + " " + swap[:1].upper() + swap[1:] + "."
        return reply + " The gluten-free one is a different product, so check the label."
    if food in NOT_SETTLED_BY_THE_RECIPE:
        # Oats are the plain food a recipe table cannot settle: the packet is what decides it.
        return NOT_SETTLED_BY_THE_RECIPE[food]
    if plural:
        return ("Yes: " + named + " have no gluten in them. The plain ones are gluten free; "
                "check the packet on flavoured or own-brand versions.")
    return ("Yes: " + named + " has no gluten in it. The plain one is gluten free; check the "
            "packet on flavoured or own-brand versions.")


_SWAP_VERDICTS = (
    (("yoghurt", "yogurt", "greek yoghurt", "greek yogurt"),
     ("cream", "double cream", "single cream", "creme fraiche"),
     "Yes, in anything cold or stirred in at the end: spoon it in off the heat, because yoghurt "
     "splits if it boils. It will not whip and it will not thicken a sauce the way cream does."),
    (("cornflour", "corn starch", "cornstarch"),
     ("plain flour", "self-raising flour", "self raising flour", "flour"),
     "Not in baking: cornflour has no gluten, so a cake or a loaf will not hold or rise. As a "
     "thickener it works, at one tablespoon where the recipe asks for two of plain flour, mixed "
     "into cold liquid first."),
    (("oil", "olive oil", "vegetable oil", "sunflower oil", "rapeseed oil"),
     ("butter", "margarine"),
     "In cakes, yes: use 80g of oil for every 100g of butter, and expect a slightly denser crumb. "
     "Not in pastry or shortbread, and not where you cream butter and sugar for air."),
    (("honey",),
     ("sugar",),
     "Yes, at three-quarters of the weight, and take a tablespoon or two out of the liquid. Bake "
     "10C cooler than the recipe says, because honey browns faster than sugar."),
    (("frozen peas", "frozen sweetcorn", "frozen veg", "frozen vegetables"),
     ("fresh", "fresh peas", "fresh vegetables"),
     "Yes, straight from the bag with no thawing: give them a minute or two longer in the pan. "
     "Frozen peas are sweeter than fresh ones that have sat about."),
    (("stock cube", "stock cubes", "bouillon", "stock powder", "stock pot", "stock pots"),
     ("stock", "chicken stock", "beef stock", "vegetable stock"),
     "Yes: one cube per 500ml of water for a stock-strength base, and half a cube in a small or "
     "already salty dish. Crumble it in rather than dropping it whole."),
    (("margarine",),
     ("butter",),
     "Yes in cakes and biscuits, at the same weight, if it is a block margarine meant for baking. "
     "The soft spread in a tub holds more water and gives a wetter, paler bake."),
    (("bicarbonate of soda", "bicarb", "baking soda"),
     ("baking powder",),
     "Not on its own: bicarbonate is about four times stronger than baking powder and needs an "
     "acid to work. Use a quarter of a teaspoon of bicarbonate with a teaspoon of lemon juice or "
     "vinegar in place of each teaspoon of baking powder."),
    (("evaporated milk",),
     ("cream", "double cream", "single cream"),
     "Yes for cooking, sauces and coffee: it will not whip, but it will not split in a hot sauce "
     "either, so it is the safer one to keep in the cupboard."),
)


LACK_SAID = tuple((name, head + " " + noun)
                  for name, nouns in LACK_NOUNS.items()
                  for head in LACK_HEADS for noun in nouns)


def missing(understood):
    """The appliances this line says it does not have."""
    text = _line(understood)
    segments = text.split("|")
    gone = set()
    for name, phrases in LACKS:
        if _says_gone(phrases, segments):
            gone.add(name)
    for name, phrase in LACK_SAID:
        if name not in gone and _says_gone((phrase,), segments):
            gone.add(name)
    return gone


GRIDDLE_BAKES = re.compile(
    r"\b(?:" + "|".join(_GRIDDLE_DOUGH + _GRIDDLE_BATTER + _GRIDDLE_WARM) + r")\b", re.I)


GRIDDLE_DOUGH = re.compile(r"\b(?:" + "|".join(_GRIDDLE_DOUGH) + r")\b", re.I)


GRIDDLE_BATTER = re.compile(r"\b(?:" + "|".join(_GRIDDLE_BATTER) + r")\b", re.I)


def _griddle_answer(said):
    """The pan answer for the bake the line names, because a hob cooks it and a fridge cake is not it."""
    text = str(said or "").lower()
    batter = GRIDDLE_BATTER.search(text)
    if batter:
        return ("A " + batter.group(0).rstrip("s") + " is a pan job as it is: the batter goes into a "
                "hot non-stick pan with a little butter, about a minute a side until bubbles pop and "
                "the edges set. Crumpets want rings in a dry pan on a low heat until the top sets and "
                "the holes stay open. " + _GRIDDLE_TAIL)
    dough = GRIDDLE_DOUGH.search(text)
    if dough:
        # Name the bake the line names, then the pan method once: "A chapati cooks in a heavy pan"
        # reads as a recipe for what they asked, where a scone answer is the wrong dish again.
        name = dough.group(0)
        if name.rstrip("s") not in ("scone", "drop scone", "pikelet"):
            return ("A " + name.rstrip("s") + " cooks in a heavy dry pan, not a tin: the same dough "
                    "made a little thicker and patted out, about 5 minutes a side on a low heat "
                    "with a lid on, until the middle is set and the edges have caught. Scones, "
                    "pikelets and roti are the same trick. " + _GRIDDLE_TAIL)
        return ("A scone cooks in a heavy pan: the same dough made a little thicker and patted out, "
                "in a dry pan on a low heat with a lid on for about 5 minutes a side, until the "
                "middle is set and the edges have caught. Drop scones, pikelets, chapatis and roti "
                "are the same trick on a hot dry pan. " + _GRIDDLE_TAIL)
    warm = re.search(r"\b(?:wrap|wraps|tortilla|tortillas|pitta|pittas|pita|pitas)\b", text)
    named = warm.group(0).rstrip("s") if warm else "wrap"
    other = "and a wrap warms the same way" if named.startswith("pitt") else "and a pitta puffs the same way"
    return ("A " + named + " is warmed rather than baked: 30 seconds a side in a dry hot pan and it "
            "is soft enough to fold, " + other + ". " + _GRIDDLE_TAIL)


# A dessert with no oven is the no-bake answer, not a list of things to cook on the hob: "no oven
# tho just need something i can make ahead" was getting pasta and a one-pan curry, which is
# dinner. "sweet potato" is a vegetable, so it never counts as the sweet course.
SWEET_ASK = re.compile(r"\b(?:desserts?|puddings?|sweets?|biscuits?|cookies?|meringues?"
                       r"|possets?|trifles?|make ahead|make-ahead)\b")


CROWD = re.compile(r"\b(?:[89]|1[0-9]|[2-9][0-9])\b")


# A line that asks for bread rather than for a bake in general.
BREAD = re.compile(r"\b(?:bread|loaf|loaves|flatbread|naan|pitta|pita)\b", re.I)


# ...and a line that names a cake as well as bread is asking about the cake.
CAKEISH = re.compile(r"\b(?:cake|cakes|biscuit|biscuits|cookie|cookies|brownie|brownies|"
                     r"muffin|muffins|scone|scones|meringue|meringues|pastry|pastries|"
                     r"flapjack|flapjacks)\b", re.I)


def _asks_for_sweet(text):
    """Whether the line is asking for the sweet course rather than a meal."""
    text = str(text).lower()
    if "sweet potato" in text:
        return False
    return bool(SWEET_ASK.search(text))


def _no_baking(text):
    """The no-oven answer, with the quantities doubled when the line says how many are coming."""
    said = str(text or "")
    # A scone or a pancake is a griddle bake, not a cold-set one: the pan answer is the true one,
    # and it is given before bread and cakes because a scone is neither.
    if GRIDDLE_BAKES.search(said):
        return _griddle_answer(said)
    if BREAD.search(said) and not CAKEISH.search(said):
        base = NO_OVEN_BREAD
    else:
        base = NO_BAKING + (" " + NO_OVEN_BREAD if BREAD.search(said) else "")
    many = CROWD.search(said)
    if not many:
        return base
    return base + (" For " + many.group() + " people make two tins of it and cut it small, "
                        "or set one big cheesecake in a deep tin and chill it overnight.")


def _pudding_ideas(memory, understood):
    """The pudding answer, with the quantity worked out when the line says how many are coming."""
    text = str(((understood or {}).get("clean") or "")).lower()
    many = CROWD.search(text)
    if not many:
        return PUDDING_IDEAS
    return PUDDING_IDEAS + (" For " + many.group() + " people make two dishes of it and put the "
                            "custard out in a jug.")


def without(understood):
    """An answer for a line that says the kitchen has no oven or no microwave, or None."""
    gone = missing(understood)
    if not gone:
        return None
    words = (understood or {}).get("words") if isinstance(understood, dict) else None
    text = " ".join(words) if isinstance(words, list) else _line(understood)
    text = str(text).lower()
    asking = any(re.search(r"\b" + re.escape(one) + r"\b", text) for one in COOKING_ASKS)
    listing = any(one in text for one in LISTING)   # "i've got chicken and rice and no oven"
    if not (asking or listing):
        # "no oven tho just a hob" names the kitchen and asks nothing at all, and it was being
        # acknowledged as a remark. In this module a line that names both what is missing and
        # what is there is the what-can-i-cook question, so long as it says nothing else.
        named = any(one in text for one in HAVE_ONE["hob"] + HAVE_ONE["microwave"]
                    + HAVE_ONE["kettle"] + HAVE_ONE["oven"] + ONLY_ONE["hob"]
                    + ONLY_ONE["microwave"] + ONLY_ONE["kettle"])
        if not (named and len(text.split()) <= 8):
            return None
    # A roast is not a no-bake cake: "can i roast a chicken with no oven" got the fridge cake,
    # because "roast" was in the list that sends the line to the no-bake answer. Anything that
    # comes out of a tin - pastry, bread, cakes, biscuits - is the no-bake answer; a roast is
    # dinner, and with no oven it is the hob.
    baking = ("bake", "baking", "cake", "cakes", "bread", "pie", "pastry", "pastries",
              "biscuit", "biscuits", "cookie", "cookies", "meringue", "meringues",
              "yorkshire", "scone", "scones", "loaf", "loaves", "muffin", "muffins",
              "brownies", "flapjack", "flapjacks")
    how = "bake" if any(one in text for one in baking) or _asks_for_sweet(text) else ""
    if "oven" in gone and how == "bake" and "hob" not in gone:
        return _no_baking(text)
    # Nothing in "can i make roti with no oven" is a baking word, so it fell through to the list of
    # hob meals - pasta, a one-pan curry - which is dinner and not what was asked. A pan bake named
    # in the line gets the pan answer whether or not the line says "bake".
    if "oven" in gone and "hob" not in gone and GRIDDLE_BAKES.search(text):
        return _griddle_answer(text)
    have = available(text, gone)
    if "hob" in gone or "hob" not in have:
        if "oven" in have:
            return NO_OVEN_ONLY
        if "microwave" in have:
            return NO_HOB
        return NO_KETTLE
    if "oven" in gone or "oven" not in have:
        return NO_OVEN
    if "microwave" in gone and how != "bake":
        return NO_MICROWAVE
    return None


# The words that are also ordinary cooking instructions: "how do i reduce a sauce" is a how-to,
# not a definition, so these only get their line when the line asks what it means. A how-to line
# counts as well when it names the thing the word acts on, which is why each of these has a
# subject list below: "how do i fold in egg whites" is the mixing line, "how do i fold a fitted
# sheet" is not about food at all.
NEEDS_DEFINITION = frozenset(("reduce", "fold", "sear", "sweat"))


def _cook_word(memory, understood):
    said = str(understood.get("clean") or " ".join(understood.get("words") or [])).lower()
    # The order the person said them in, but a longer phrase wins over the plain word inside it,
    # so "rolling boil" is not also read as "boil". A word catches its own -ing form too:
    # "deglazing" is the deglaze line.
    found = sorted(hit for hit in (_cook_word_hit(word, said) for word in COOK_WORDS) if hit)
    named = []
    for pos, word in found:
        if any(pos >= other_pos and pos + len(word) <= other_pos + len(other) and word != other
               for other_pos, other in found):
            continue
        named.append(word)
    if not named:
        return None
    if not any(word in said for word in DEFINITION_WORDS):
        # Not a definition question, so this has to be a how-to about the food itself: drop every
        # word whose subject is missing, and pass if that leaves nothing.
        named = [word for word in named
                 if word not in NEEDS_DEFINITION or _names_a_subject(word, said)]
        if not named:
            return None
    if len(named) == 1:
        return COOK_WORDS[named[0]]
    # A line naming two of them is asking for the difference, so both lines come back together.
    return "%s %s" % (COOK_WORDS[named[0]], COOK_WORDS[named[1]])


# Longest name first, so "chocolate chip cookies" is cookies and "loaf of bread" is bread. The
# aliases are folded the same way the line's words are, or "brownies" (which folds to "browny")
# and "scones" (which folds to "scone") would never meet the name they were written for. Built
# on first use because _fold is defined further down the file.
_BAKE_ALIASES = None


def _bake_aliases():
    global _BAKE_ALIASES
    if _BAKE_ALIASES is None:
        _BAKE_ALIASES = tuple(sorted(
            (([_fold(part) for part in alias.split()], name)
             for name, (aliases, _) in BAKES.items() for alias in aliases),
            key=lambda pair: -len(pair[0])))
    return _BAKE_ALIASES


# A bake whose name is one word the pantry also builds dinners from ("bread", "pastry") is not a
# bake the pantry has to step aside for: "bread and cheese" is still a sandwich question.
_PANTRY_AS_WORDS = None


def _pantry_words():
    global _PANTRY_AS_WORDS
    if _PANTRY_AS_WORDS is None:
        _PANTRY_AS_WORDS = frozenset(_fold(name) for name in PANTRY)
    return _PANTRY_AS_WORDS


def _bake_hits(folded, skip_pantry=False):
    """[(parts, name), ...] for the bakes these words name, longest name first.

    skip_pantry leaves out a name that is one word the pantry also cooks with, so a line naming
    two foods ("bread and cheese") is not read as a request for the bread recipe.
    """
    hits = []
    for parts, name in _bake_aliases():
        if skip_pantry and len(parts) == 1 and parts[0] in _pantry_words():
            continue
        for start in range(len(folded) - len(parts) + 1):
            if folded[start:start + len(parts)] == parts:
                hits.append((parts, name))
                break
    return hits


def _names_a_bake(understood):
    """True when the line names a bake ("banana bread", "brownies"), not a food to cook with."""
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    folded = [_fold(word) for word in words]
    # A bake already in the kitchen is a food to use up, not a recipe to follow: "i have leftover
    # puff pastry, what can i do with it" is the pantry's question. Every bake name here stood
    # the pantry and the dish table down, so the line got no answer at all.
    return any(not _already_baked(folded, parts)
               for parts, _name in _bake_hits(folded, skip_pantry=True))


# A bake someone already has in the kitchen is not a request to make it: "what can i make with
# leftover bread" and "use up stale scones" want something to do with the thing, which is the
# pantry's leftover answer. Only a marker in front of the bake's own name counts, so "i have old
# bananas, what can i bake" and "can i bake bread with leftover milk" still get the recipe.
_ALREADY_BAKED_WORDS = frozenset("leftover leftovers stale old yesterday already".split())


def _already_baked(folded, parts):
    """True when a "leftover"/"stale"/"old" sits just in front of this bake's name."""
    for start in range(len(folded) - len(parts) + 1):
        if folded[start:start + len(parts)] != parts:
            continue
        window = folded[max(0, start - 3):start]
        if any(word in _ALREADY_BAKED_WORDS for word in window):
            return True
        return any(phrase in " ".join(window) for phrase in _ALREADY_BAKED_PHRASES)
    return False


def _bake(memory, understood, text=None):
    """The recipe for the bake the line names and asks about, or None when it names none."""
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    folded = [_fold(word) for word in words]
    if text:
        folded = folded + [_fold(word) for word in str(text).lower().split()]
    said = " ".join(folded)
    if any(phrase in said for phrase in _TIMING_ASKS):
        return None
    if any(phrase in said for phrase in _NO_YEAST):
        # a loaf with no yeast in it is the soda loaf's line, not this yeast recipe's
        return None
    if not (understood.get("asks") or any(word in ("how", "what", "whats", "recipe")
                                          for word in folded)):
        # "i baked brownies yesterday" is telling the bot about a cake, not asking how.
        return None
    if _asks_vegan(folded):
        # Every recipe in BAKES uses butter or egg: a vegan ask is the vegan entry's question, and
        # it was being told to rub cold butter into flour.
        return None
    hits = _bake_hits(folded, skip_pantry=len(ingredients(understood)) > 1)
    if not hits or _already_baked(folded, hits[0][0]):
        # They have the loaf already: the pantry and the leftover answers know what to do with it.
        return None
    return BAKES[hits[0][1]][1]


# "Tea" is the evening meal as well as the drink, and the request shapes in the row - "can i
# have", "i'll have" - are what a meal question is asked with too: "what can i have for tea" was
# answered with how to brew a cup, while "whats for tea" and "what shall i have for tea" got
# dinner (royal-zipper, #8152 was the drink half of the same row). A line that asks what to have
# for a meal is asking about the plate, whatever the request shape around it.
_ASKS_WHAT_TO_HAVE = re.compile(
    r"\b(?:what|anything|something|whats|what's)\b[^.?!]*\b(?:have|eat|cook|make|do)\b")


_FOR_A_MEAL = re.compile(
    r"\bfor\s+(?:my\s+|our\s+|the\s+|his\s+|her\s+)?"
    r"(?:tea|dinner|lunch|supper|breakfast|brekkie|supper|teatime|tea time)\b")


def _tea_reply(memory, understood):
    """The brewing answer the line asked for: a method, a pot, iced, a cloudy cup, or a fault."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    if _FOR_A_MEAL.search(said) and _ASKS_WHAT_TO_HAVE.search(said):
        # "what can i have for tea" is the evening meal: the meal table answers it.
        return None
    words = set(re.findall(r"[a-z']+", said))
    if words & {"iced", "ice"}:
        return TEA_ICED_TEXT
    if words & {"pot", "teapot", "teapots"}:
        return TEA_POT_TEXT
    if words & {"cloudy", "cloudiness", "scum", "murky", "film"}:
        return TEA_CLOUDY_TEXT
    if words & {"green", "greens", "sencha", "matcha", "jasmine"}:
        return TEA_GREEN_TEXT
    if words & {"twice", "again", "reuse", "re-use", "second"}:
        return TEA_TWICE_TEXT
    if words & {"bitter", "sour", "soured", "stewed", "weak", "strong", "stronger", "watery",
                "tastes", "taste", "tasting", "stewing"}:
        return TEA_FAULT_TEXT
    return TEA_METHOD_TEXT


def _burnt_dish(memory, understood):
    """The burnt dish's rescue, or nothing when the line is really about cleaning the pan.

    A dish named as what burnt is this entry's turnover; a pan on its own, with no dish in it, is
    the burnt-pan entry's line and this one declines so that entry can take it. A joint in a tin
    gets the meat's own rescue, since there is nothing in a roast to lift the burnt bits out of.
    """
    said = " ".join(str((understood or {}).get(k) or "")
                    for k in ("clean", "norm_text", "norm")).lower()
    # Whether the black is bad for the person eating it is the health question,
    # and the rescue below ("lift out the burnt bits") is about a pot still on the
    # heat. It comes before the batter and the vegetables because "are burnt roast
    # potatoes bad for you" names a vegetable and is still the eating question.
    if _says(said, _BURNT_EATING_ASK):
        return _BURNT_EATING_REPLY
    if _says(said, _BURNT_BATTER):
        return _BURNT_BATTER_REPLY
    if (_says(said, _BURNT_VEG)
            and not _says(said, ("chicken", "beef", "lamb", "pork", "turkey", "gammon", "duck",
                                 "steak", "sausage", "sausages", "bacon", "ham", "joint",
                                 "brisket", "meatballs"))):
        return _BURNT_VEG_REPLY
    # The tin comes out of the line before the joint is looked for. "my roast burnt in the oven"
    # and "the roast tin is burnt" both put a vessel word in front of a joint, and the vessel
    # check below sent the first one to the tin's answer (a roast that caught in the oven got
    # nothing at all) and would have sent the second to the meat's.
    without_vessel = _VESSEL_PHRASES.sub(" ", said)
    if _says(without_vessel, _ROAST_PARTS):
        return _ROAST_PART_REPLY
    if (_says(without_vessel, _BURNT_MEAT)
            and not _says(without_vessel, _PAN_WORDS + ("sauce", "gravy", "soup", "stew",
                                                        "curry", "rice"))):
        return _BURNT_MEAT_REPLY
    # A cake tin, a loaf tin or a baking tray is a thing to clean, and its own name carries a
    # bake's word into the food list: "my cake tin has burnt bits stuck to it" was told to take
    # it off the heat and lift the burnt bits out. The vessel comes out before the food is looked
    # for, the way `_bake_burning` already does it, and with no dish left over the line is the
    # tin's (`burnt-tin`).
    baked = _VESSEL_PHRASES.sub(" ", said)
    if _says(baked, _PAN_DISH):
        return _BURNT_DISH_REPLY
    if _says(said, _PAN_WORDS) or _says(baked, _TIN_OR_OVEN):
        return ""
    return _BURNT_DISH_REPLY


_VESSEL_PHRASES = re.compile(
    r"\b(?:cake|loaf|pie|tart|muffin|bun|biscuit|bread|traybake|flan|roast|toast)\s+"
    r"(?:tins?|trays?|pans?|moulds?|molds?|dishes?|dish|sheets?|cases?|liners?|tins?)\b")


# A burnt bottom is the other end of the oven from a burnt top, and the foil-over-the-top answer
# is no help with it: the heat came from underneath, so the fix is the shelf up, a sheet or two
# between the tin and the element, and a tin that is not black. "why do my cakes burn on the
# bottom" and "my muffins burn on the bottom" were getting the burnt-sauce card and a one-line
# fragment of the top answer.
_BAKE_BOTTOM = re.compile(r"\b(?:bottom|bottoms|underneath|underside|base of the tin)\b", re.I)


_BAKE_STOP = re.compile(r"\b(?:stop|stops|prevent|avoid)\b|\bwhy\b", re.I)


_BAKE_DONE = re.compile(r"\b(?:burnt|burned|caught)\b", re.I)


def _bake_burning(memory, understood):
    """A bake still in the oven gets the foil; a burnt bottom gets the heat from underneath.

    "My cake is burnt" is somebody holding the cake, not somebody asking how to stop it
    catching, and the prevention answer made them read four sentences before the one that
    helps. The tense decides: "stop", "why" and "burning" are still the oven question, and
    "burnt", "burned" and "caught" are the rescue. Which end of the bake is burnt decides
    between the foil over the top and the shelf up for the bottom.

    A line with a bake in it is this entry's; a tin, tray, shelf or oven floor that is burnt on
    is the cleaning job, and with no bake named the answer here is a rescue for food nobody is
    holding - "the bottom of my oven is burnt" was told to grate the black off a fruit cake.
    """
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    # burnt grime on a tin or an oven is the cleaning question, and this reply is for something
    # still in the oven going brown. The vessel comes out of the line first, so "my cake tin is
    # burnt on" is read as the tin and not as a cake.
    text = _words_and_text(understood)
    baked = _VESSEL_PHRASES.sub(" ", text)
    if (not _says(baked, _BAKE_NOUNS) and not _says(baked, _BAKED_BURNT)
            and _says(text, _TIN_OR_OVEN)):
        return ""
    if _BAKE_BOTTOM.search(said):
        return _BAKE_BOTTOM_REPLY
    if _BAKE_STOP.search(said) or "burning" in said:
        return _BAKE_PREVENTION
    if _BAKE_DONE.search(said):
        return _BAKE_BURNT
    return _BAKE_PREVENTION


# A fat that has landed on a person is a scald, not a pan temperature: "hot oil splashed on my
# arm" was answered with "Around 180C for most frying, 170C for chips", which is advice about the
# pan given to somebody who has just been burnt. The body part and a splash word together are the
# line that says so, and health.py's scald row has the twenty minutes of cool water.
_BODY_PART = re.compile(
    r"\b(?:arm|arms|hand|hands|finger|fingers|thumb|thumbs|foot|feet|toe|toes|wrist|wrists|"
    r"leg|legs|chest|tummy|stomach|belly|lap|neck|shoulder|shoulders|eye|eyes|face|skin|"
    r"baby|child|toddler|kid)\b")


def _fat_has_landed_on_a_person(text):
    """True when the line is about a fat on a body, which is first aid and not the pan."""
    return bool(_BODY_PART.search(text)) and any(word in text for word in _ONTO_A_PERSON)


def _oil_smoking(memory, understood):
    """Why the fat is smoking, and what to do with the pan and the bottle."""
    understood = understood if isinstance(understood, dict) else {}
    text = str(understood.get("clean") or understood.get("text") or "").lower()
    if _fat_has_landed_on_a_person(text):
        return ""
    # A pan with something burnt on it is the pan's question, not the fat's: "the pan has burnt
    # black on the outside" and "how do i get burnt milk off the bottom of a pan" were both told
    # the fat was past its smoke point, which is a lecture about a fire when the job is a soak.
    if _burnt_on_the_pan(text):
        return ""
    if _says(text, ("smoke point", "smoking point", "smokes at", "smoke at", "smoke too")):
        return ("Every fat has a smoke point: " + "; ".join(
            f"{name} {temp}" for name, temp in OIL_SMOKE_POINTS) +
            ". Above that it is breaking down, so keep the pan under it - a thermometer takes the "
            "guesswork out, and a drop of the oil in a cold pan, brought up slowly, tells you when "
            "it is ready.")
    # Pan first or oil first is the same subject as the heat of the fat, and "when do i put the
    # oil in the pan" was the car's dipstick: a wick of engine oil in an engine that is off.
    # The fat going into water is not the pan at all. "Should i put oil in pasta water" reached
    # the pan-order arm's own words and was told the fat was past its smoke point, because the
    # question is about the pot and the water rather than a hot pan; the pot of water is another
    # row's question, so this one stands down.
    if _says(text, ("in the water", "pasta water", "rice water", "boiling water", "the water for",
                    "water for the pasta", "water for the rice", "in the pot of water",
                    "into the water", "salt water", "salted water", "the pasta water")):
        return ""
    if _says(text, ("put the oil in", "put in the oil", "add the oil", "adding the oil",
                    # people leave the article out: "should i preheat the pan before adding oil"
                    # was a "can't call that one" while the order was sitting in this arm
                    "put oil in", "add oil to", "adding oil", "add oil",
                    "oil go in", "oil goes in", "oil first or the pan", "pan first",
                    "oil in the pan", "oil in a pan", "oil in pan",
                    "hot pan first",
                    # "should the pan be hot before the oil" was a punt: the order is the
                    # question and the words that ask it are the pan and the heat, not "put"
                    "pan be hot", "pan hot before", "before the oil", "before adding the oil",
                    "before adding oil", "hot pan",
                    "pan hot before", "when do i add the oil")):
        return ("Pan first, then the oil: a dry pan heats faster and you can watch the oil for the "
                "heat - it thins and shimmers at about 180C, and a cube of bread turns golden in 30 "
                "seconds. Give the oil 20 seconds before the food goes in. Cold oil in a cold pan "
                "is for rendering fat, not a sear.")
    # "What temperature for chips" is the dish's own heat, not the fat's: this arm claimed every
    # "what temperature for ..." line, so the dish table never got its turn. When the line names a
    # dish that has a heat of its own, and nothing hot in it (no fat, no pan, no fry), the dish
    # answers it.
    if not _says(text, ("oil", "fat", "pan", "fry", "frying", "deep fry", "chip pan",
                         "dripping", "lard", "ghee", "wok")) and _a_dish_with_a_heat(text):
        return ""
    if _says(text, ("how hot", "hot enough", "what temperature", "temperature for", "hot should",
                    "heat of the oil", "temperature does",
                    # the same question with the word left out: "how do i know when the pan is
                    # hot" reaches the row on the key and was then told the fat had passed its
                    # smoke point, which is the answer to a pan that is already too hot
                    "is hot", "is ready", "pan heat", "the heat", "test the heat",
                    "check the heat", "hot oil", "oil is hot", "oil is ready", "fat is hot",
                    "fat is ready", "heat the pan", "heating the pan", "heat the oil",
                    "heating the oil")):
        # The number people want is the oil's own heat, and the bread cube is the thermometer most
        # kitchens have. The smoke points follow, because that is the ceiling on it.
        # The number first, the bread cube as the thermometer most kitchens have, then the ceiling
        # on it. Kept to the two sentences someone will read before the pan overheats.
        return ("Around 180C for most frying, 170C for chips so they cook through before they "
                "colour; with no thermometer a cube of day-old bread turns golden in about 30 "
                "seconds. Heat the oil with nothing in it and fry in small batches so it does not "
                "drop. Stay under the fat's smoke point: "
                + "; ".join(f"{name} {temp}" for name, temp in OIL_SMOKE_POINTS[:1] + OIL_SMOKE_POINTS[2:4])
                + ".")
    # ...and only with a fat named: "where do i put a hot pan" is a question about the surface
    # under it, and there is nothing in it to pour into a bottle. This is the disposal arm''s
    # condition alone - "my pan is smoking" names no fat and is still the pan - so it is a flag
    # rather than a stand-down for the whole row.
    _fat_named = _says(text, ("oil", "fat", "dripping", "lard", "ghee", "grease", "butter"))
    if _fat_named and _says(text, ("down the sink", "down the drain", "down the toilet",
                                   "down the loo", "down the plug hole", "down the plughole")):
        # "can i pour oil down the sink" is a yes or no, and the general disposal arm below
        # answers a where: it opened on the bottle and reached "never down the sink" third. The
        # no is the first word here, and the why is one clause.
        return ("No - never down the sink, the loo or the drain: fat sets hard as it cools and "
                "closes the pipe, and hot water only pushes it further down to block somewhere "
                "worse, which is a plumber's bill. Let it cool, pour it into the bottle or a jar "
                "you were going to bin, and put that in the rubbish; wipe the pan out with kitchen "
                "roll before you wash it.")
    if _fat_named and _says(text, ("throw out", "throw away", "throwing out", "get rid", "getting rid",
                    "dispose", "disposal", "bin it", "bin used", "bin the oil", "recycle",
                    "recycling", "down the sink", "where do i put", "where do i pour",
                    "what to do with",
                    "where does it go", "where can i put", "put used", "pour it", "pour old",
                    # "what do i do with old oil" reached the entry and was answered as a pan
                    # that had smoked: the question is the bottle, and "do with" is the ask.
                    "do with old oil", "do with used oil", "do with the oil", "do with the fat",
                    "do with leftover oil", "what do i do with", "where does it go", "pour it",
                    "pour the oil", "tip it")):
        # "how do i get rid of used cooking oil" was answered with which oil to cook with: the
        # bottle, not the pan, is the question, and the one thing not to do is the sink.
        return ("Let it cool completely, then funnel it back into the bottle it came in or any "
                "screw-top jar you were going to bin, and put that in the rubbish - never down the "
                "sink, because it sets in the drain and it is what makes fatbergs. A small amount "
                "from one pan can be soaked up with kitchen roll and binned; a big batch goes to "
                "the tip, and most councils and some supermarkets take used cooking oil for "
                "recycling. Keep a jar under the sink and pour into it while it is still warm, and "
                "it never gets as far as the drain.")
    if _says(text, ("reuse", "re-use", "again", "second time", "keep the oil", "straining",
                    "strain", "can i use", "can i still use", "still use", "still good",
                    "fine to use", "ok to use", "okay to use", "fry in", "fry with")):
        # the action is the answer, so it leads: "is it safe to reuse oil" was opening with the
        # chemistry and stopping there when the sentence was trimmed as a repeat.
        return ("Let it cool, strain it through a fine sieve or a coffee filter, and use it once "
                "more for something at a lower heat. Oil that has smoked has started to break "
                "down, so it will taste acrid and it will smoke sooner next time; bin it if it "
                "smells bitter or looks dark and sticky.")
    if _says(text, ("foam", "foams", "foamy", "foaming", "foamed", "bubbling up", "bubbles up",
                    "spitting",
                    "spits", "spattered", "spattering")):
        # Foam is water, not heat: the food went in wet, the pan was overcrowded, or the oil has
        # been used too often and its breakdown products are foaming.
        return ("Oil that foams has water in it rather than too much heat: dry the food with kitchen "
                "paper and lower it in gently, cook in two batches so the pan does not drop below "
                "its temperature, and keep the lid or the basket dry. If oil you have already used "
                "a few times foams as soon as anything goes in, it is spent - let it cool, bin it "
                "in a bottle, and start with fresh.")
    # A row that answers a fault falls back on the fault, so the default answer is only for a
    # line that says something is wrong. The key takes two signals and one of them can be a plain
    # subject word: "should i put oil in pasta water" reached the pan-order arm's subject and no
    # arm applied, so it was told the fat was past its smoke point - a lecture about a fire
    # nobody has. Naming the trouble is what earns the fault card; a line that only says where
    # the oil goes is another row's question, or nobody's.
    if not _says(text, _SOMETHING_IS_WRONG_WITH_THE_PAN):
        return ""
    return ("The fat is past its smoke point, so turn the heat down and take the pan off the ring "
            "for a minute rather than carrying on. Open a window or put the extractor on, and once "
            "it has cooled wipe the pan out and start again with fresh fat - the smoked oil has "
            "turned acrid and it will make the food taste of it. Butter and extra virgin olive oil "
            "smoke first (about 150C and 180C), so use a plain vegetable oil or clarified butter "
            "when you want the pan very hot. If it ever actually catches, put a lid or a baking "
            "tray over the pan and turn the heat off - never water.")


def _soggy_lunch(memory, understood):
    """A wet sandwich and a wet salad are both water in the wrong place, but not the same fix."""
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    said = " ".join(words)

    def _names(family):
        return (any(_same(word, name) for word in words for name in family)
                or any(" " in name and name in said for name in family))

    if _names(_SOGGY_BREAD):
        return ("A sandwich goes soggy because the wet filling soaks into the bread: butter both "
                "slices right to the edges first, or spread mayonnaise or soft cheese as a "
                "barrier, and keep tomato, cucumber and lettuce in the middle rather than against "
                "the bread. Packed in the morning, the wet things go in a separate tub and are "
                "added at lunchtime, which is the only thing that really works on a hot day.")
    if _names(_SOGGY_LEAF):
        return ("A salad goes soggy because the leaves are still wet or the dressing went on early: "
                "dry them properly in a tea towel or a salad spinner, dress it at the table, and keep "
                "the wet things - tomato, cucumber, dressing - at the bottom of the bowl until you "
                "eat. Salt draws the water out too, so season it in the last minute rather than "
                "ahead.")
    # Nothing named at all - a soggy lunchbox, a lunch that went wet - is water getting in, and
    # the fix is the same either way.
    return ("A packed lunch goes soggy because water gets in from somewhere. Keep the wet things "
            "- tomato, cucumber, dressing, a drink - in their own tub and stand the leaky ones "
            "upright, put a layer of kitchen paper or a lettuce leaf under the bread, and pack the "
            "dry things on top. A leaking drink and a damp fork do more damage than a whole "
            "morning in the bag.")


# The list of questions lives in cooking_entries.py: this file was over the world's 1 MB upload
# limit and a list of data is the cheapest thing to move. It is copied back here, in place, so
# everything below sees the entries exactly as it did before.
from ..knowledge.cooking_entries import ENTRIES as _LISTED_ENTRIES  # noqa: F401


from ..knowledge.cooking_entries import NO_SUGAR as _NO_SUGAR  # noqa: F401


ENTRIES = list(_LISTED_ENTRIES)


# ---------------------------------------------------------- what kinds a thing comes in
# The shape is read once, in bot/knowledge/lookup.py (`KINDS_WORDS`, `asks_the_kinds`); a subject
# is data here. What was wrong on main: "what kinds of tea are there" was answered with a dinner
# pick, and pasta, oil, honey, milk, beans, lettuce, wine, coffee and yoghurt were answered with a
# search hedge, because the rows that knew the subject knew one of its kinds (brewing a cup,
# frying an egg) and no row knew the question. The ask is for the families a thing comes in.
#
# Only the subjects nothing else answers are here. A subject whose card already names the families
# (potato, apple, rice, cheese, mushroom, onion, tomato, flour, chocolate) keeps that card: it
# answers the shape, and a second answer for the same ask would only be longer.
#
# (the line's subject words, the subject for the row's id, the answer)
_KINDS = (
    (("tea", "teas"), "tea",
     "Black, green, white and oolong are the same leaf, picked and processed differently: black "
     "is fully oxidised and malty, green is steamed or pan-fired and grassy, white is the young "
     "leaf dried, and oolong sits between green and black. Everything else - peppermint, "
     "chamomile, rooibos, fruit - is a herbal infusion rather than tea, so it brews and keeps "
     "differently."),
    (("pasta", "pastas"), "pasta",
     "Long pasta - spaghetti, linguine, tagliatelle - is for thin sauces that coat it. Short "
     "shapes - penne, fusilli, rigatoni - hold chunkier sauces, and the ridges and tubes are there "
     "to catch them. Filled pasta - ravioli, tortellini - is a meal with its sauce inside. Dried "
     "is durum wheat and water; fresh is egg and soft wheat, cooks in two or three minutes, and "
     "is richer. Wholewheat is the same shapes with the bran left in, and takes a minute longer."),
    (("oil", "oils"), "oil",
     "Olive oil splits in two: extra virgin is the cold-pressed first press, peppery and best "
     "raw or for low heat, and ordinary olive oil is refined, plainer and fine for frying. "
     "Rapeseed is the mild all-rounder and the cheapest British one. Sunflower and vegetable oil "
     "are neutral and take high heat, which is what chips and stir-fries want. Sesame is for "
     "flavour, a teaspoon at the end, and coconut oil tastes of coconut. Groundnut oil is the "
     "one restaurants fry in, because it is neutral and stable when hot."),
    (("honey", "honeys"), "honey",
     "It is named for the flower the bees worked: clover and acacia are light and mild, heather "
     "and chestnut are dark and strong, and orange blossom is perfumed. Runny or set is the same "
     "honey - set has simply crystallised, which a warm jug of water undoes. Raw or unfiltered "
     "means it has not been heated, so it is cloudier and tastes more of the flowers. Never give "
     "any honey to a baby under one, because of the botulism risk."),
    (("milk", "milks"), "milk",
     "Cow's milk comes by fat: whole at about 3.5%, semi-skimmed at 1.7% and skimmed at almost "
     "nothing, and the fat is what carries the taste in coffee and sauces. Fresh and UHT are the "
     "same milk, one pasteurised hotter so it keeps for months unopened. Goat's and sheep's are "
     "the other animals, sharper and richer. Plant milks - oat, soya, almond, coconut - are a "
     "different drink, and the barista ones are the ones that do not split in hot coffee."),
    (("bean", "beans"), "bean",
     "Dried or tinned is the first split: dried needs soaking overnight and a hard ten-minute "
     "boil, tinned is cooked and ready. After that it is the bean: kidney is the chilli one, "
     "cannellini and haricot are creamy and white (baked beans are haricot in tomato), black "
     "beans are earthy for Mexican food, and butter beans are the big soft ones. Chickpeas, "
     "lentils and split peas are the same family - pulses - and they cook without soaking."),
    (("lettuce", "lettuces"), "lettuce",
     "Crisphead - iceberg - is the crunchy one that keeps for a week and is mostly water. Cos, "
     "or romaine, is the upright one with a spine, and it is the one for Caesar. Butterhead - "
     "round and little gem - is soft and sweet, and wilts first. Loose-leaf - oakleaf, lollo "
     "rosso, frisée - is the curly one to tear into a bowl. Rocket and spinach are leaves sold "
     "beside it, not lettuce, and they are peppery or earthy rather than crisp."),
    (("wine", "wines"), "wine",
     "Red, white and rosé are about the skin, not the grape: red is fermented on it, white off "
     "it, and rosé briefly on it. Sparkling is a second fermentation for the bubbles, and "
     "fortified - sherry, port, madeira - has spirit added, which is why it keeps for weeks after "
     "opening. The other axis is the grape and where it grew, which is what makes a Chablis lean "
     "and a Chardonnay from a hot place buttery, and a wine dry or sweet."),
    (("coffee", "coffees"), "coffee",
     "Two beans: arabica is the fruity, slightly acidic one in most good coffee, and robusta is "
     "stronger, more bitter and has about twice the caffeine, which is why instant and cheap "
     "espresso blends use it. Roast runs from light, which keeps the fruit and the acidity, to "
     "dark, which tastes of the roast itself. Then it is ground to the brew: fine for espresso, "
     "medium for a filter machine, coarse for a cafetière. Instant is brewed and dried, a "
     "different drink, not a weaker one."),
    (("yoghurt", "yogurt", "yoghurts", "yogurts"), "yoghurt",
     "Natural is milk and cultures and nothing else, and it is what to cook with. Greek is the "
     "same yoghurt strained of its whey, so it is thicker and higher in protein; Greek-style is "
     "thickened with milk powder and is cheaper and sweeter. Set is cultured in the pot and stays "
     "firm, stirred is smooth. Skyr is strained further still, so it is very thick and very high "
     "in protein. Live yoghurt has the cultures still alive, which is the kind that helps an "
     "unsettled stomach."),
)


ENTRIES.extend(kinds_entries(_KINDS))


# The pair is matched on both words wherever they sit, so the reverse question ("can i use plain
# flour instead of cornflour") would land here too. It is a different question, answered by the
# swap entry for the ingredient being replaced, so a verdict steps aside when the line offers
# what it replaces: "butter instead of oil" is not the oil-for-butter question.
for _offered, _replaced, _verdict in _SWAP_VERDICTS:
    ENTRIES.append(entry("uses-%s-for-%s" % (_offered[0].replace(" ", "-"),
                                             _replaced[0].replace(" ", "-")),
                         (_offered, _replaced), _verdict, bias=2, ask=_SWAP_ASK,
                         avoid=tuple("%s instead of" % name for name in _replaced)))


# --- keeping food: one table, so every way of asking a food's shelf life agrees ------------
# The reason each food spoils is different, so the reply is written per food, but the question
# is always the same shape: a food (potato, onion, carrot) plus a keeping word ("keep", "last",
# "store", "gone soft", "sprouting", "how long", "mouldy"). A line that only names the food
# ("what can I do with mushrooms") is a meal question and stays with the pantry table.
# "fresh" is not in here on purpose: in a question it is an adjective about the food ("do i need
# fresh eggs for meringue"), not a question about keeping it, and it costs main's egg answer.
# "use up" and "freezer" are out for the same reason - a leftover wants a recipe, and a freezer
# line is about freezing, not storing.
# The freezer, for the cooked-keeping rows in bot/knowledge/keeping_cooked.py. A cooked food
# put in the freezer keeps for a stated time, and every one of those rows says it. Only the
# freezer's own words are here: "how do i defrost cooked chicken" and "how long do i reheat it
# for" are the how-to questions, and answering them with the keeping clock is not an answer.
FREEZER_WORDS = ("freeze", "freezes", "freezer", "frozen", "freezing")


# Cooking a thing that is still frozen is a different question from freezing it once it is cooked,
# and these rows have nothing to say about it: "can i cook chicken from frozen" was answered with
# the cooked chicken's keeping clock, which is about the wrong bird. The words say the food has not
# been thawed yet, so the row stands down and the thaw entry answers.
STILL_FROZEN_WORDS = ("from frozen", "still frozen", "cooked from frozen", "cook it frozen",
                      "without defrosting", "without thawing", "no need to defrost")


# A line that asks how to cook the food is not asking how long cooked food keeps, and a freezer
# word alone does not make it one: "can i cook frozen chicken" is about the raw bird, where main
# answered the chicken's own keeping row. The want rule in `lookup` lets such a line in without any
# of the row's ask words, so the row stands down for a line with a cooking verb in it that never
# says the food is already cooked. A follow-up keeps working: "can i freeze it" after "i cooked a
# big pot of mince" has no cooking verb in it, so the row is still the one that answers.
COOKING_VERBS = re.compile(r"\b(?:cook|cooks|cooking|roast|roasts|roasting|bake|bakes|baking|"
                           r"fry|fries|frying|boil|boils|boiling|simmer|simmering|grill|"
                           r"grilling|steam|steaming)\b")


def _already_cooked_is_the_question(understood):
    """True when the line is about a food that is cooked already, or asks nothing about cooking."""
    text = " ".join(str((understood or {}).get("clean") or "").lower().split())
    if any(word in text for word in COOKED_KEEP_ASK):
        return True
    return not COOKING_VERBS.search(text)


KEEP_WORDS = ("keep", "keeps", "keeping", "shelf life", "shelf-life", "store", "storing",
              # "can i reheat cooked mince" and "reheating leftover chicken" ask the keeping
              # clock, not how to cook it: how many days it keeps and how it goes back hot.
              "reheat", "reheats", "reheating", "reheated",
              "storage", "stored", "last",
              "lasts", "longer", "go off", "goes off", "gone off",
              "going off", "sprout", "sprouts", "sprouting", "soft", "gone soft", "bendy",
              "mouldy", "mould", "moldy", "dried out", "dry out", "wilt", "wilted", "limp",
              "rot", "rotten", "green", "greening", "fridge",
              # the day after, and the date on the pack: "can i eat a jacket potato the next day"
              # and "can i eat cheese past its date" are keeping questions with neither "keep"
              # nor "last" in them
              "next day", "the next day", "tomorrow", "past its date", "past the date",
              "out of date", "once opened", "once open",
              # "are my mushrooms still ok" is how people ask whether they dare eat it, and it
              # has no keeping word in it at all: the food plus one of these is the whole shape.
              # Without them the line reached the dish-plan entry, which had nothing to say
              # about a punnet of mushrooms in the fridge.
              "still ok", "still good", "still fine", "still safe", "still edible",
              "are they ok", "are these ok", "ok to eat", "safe to eat",
              # a food that has turned is a keeping question said by its smell or its taste:
              # "the flour tastes old" and "my flour smells musty" reached a house-damp card and
              # the raw-flour sauce card, and neither row can tell a turned food from a fresh one
              "smell", "smells", "smelling", "smelly", "tastes old", "taste old", "tastes off",
              "tastes funny", "tastes strange", "tasted old", "gone stale", "tastes stale",
              "tastes sour", "smells off", "smells funny", "smells sour", "smells musty")


# A pot that has gone mouldy or smells off is not a keeping question, and the keeping number is
# the dangerous direction: "my soup has gone mouldy" was answered "Soup keeps 3 to 4 days in the
# fridge", which invited someone to eat it. Mould in a wet dish sends threads under the surface
# where you cannot see them and heating does not make it safe, so the answer is bin it - the
# opposite of the cheese rule, and the reason this is a row of its own rather than a line in the
# pot row above. Nothing here is keyed on "still ok" or "safe to eat": those carry no sign of
# spoiling, and "is my rice still ok" wants the reheating answer, not the bin.
ENTRIES.append(entry("gone-off-pot",
                     (("soup", "soups", "stew", "stews", "broth", "curry", "curries",
                       "chilli", "casserole", "gravy", "sauce", "sauces", "dahl", "dal",
                       "tagine", "goulash", "leftovers", "yogurt", "yoghurt", "custard",
                       "cream", "rice", "risotto rice", "pasta", "pot", "tub", "batch", "food",
                       "potato", "potatoes", "jacket potato", "boiled potatoes", "spuds",
                       # "my bolognese went mouldy" says the dish by its sauce's name
                       "bolognese", "ragu", "risotto", "chowder", "hotpot", "stock", "stocks"),
                      ("mould", "moulds", "mouldy", "mold", "moldy", "gone off", "gone bad",
                       # a cooked grain, potato or pasta that has turned is slick and slimy
                       # before it smells, and "my rice is slimy" was answered with the calorie
                       # comparison because "slimy" is one letter from "slimming"
                       "slimy", "sliminess", "slick", "smells odd", "smell odd",
                       "gone sour", "smells off", "smells funny", "smells wrong", "smells bad",
                       "smelt off", "tastes off", "tastes funny", "tastes wrong",
                       # "bubbling" is a pot on the heat as often as it is a pot on the turn:
                       # "why is my risotto bubbling" was binned, and a risotto is stirred.
                       "tastes sour", "smelly", "fizzy", "fizzing",
                       "fuzz", "furry", "fuzzy")),
                     "Bin it. Mould, an off smell or a slimy feel in a soup, sauce, stew or a "
                     "cooked grain means threads and bacteria under the surface where you cannot "
                     "see them, and heating it through does not make it safe - the opposite of "
                     "hard cheese. A pot that tastes sharp, fizzes or has bubbles is the same "
                     "answer with no mould showing.",
                     bias=2,
                     # hard cheese keeps its own rule (cut an inch around the mould), a loaf has
                     # a row, and sour cream is a thing you buy rather than something that has
                     # turned
                     # the raw-chicken and raw-meat rows say it better and say it about the
                     # smell that matters ("a sour or ammonia smell, a tacky or slimy feel"), so
                     # this row keeps off them
                     avoid=("cheese", "cheeses", "bread", "loaf", "loaves", "sour cream",
                            # a cream for the skin is not a pot on the hob: "has my shaving
                            # cream gone off" was binned as a stew. The cosmetic row keeps
                            # its own lifetime for these.
                            "hand cream", "body cream", "shaving cream", "nappy cream",
                            "face cream", "facial cream", "eye cream", "spot cream",
                            "eczema cream", "cold cream", "moisturiser", "moisturizer",
                            "sun cream", "suncream", "sunscreen", "sunblock", "lip balm",
                            "lip salve", "aftershave", "toner",
                            # a pot of compost is not a pot on the hob: "why is there mould in
                            # my plant pot" was binned as a stew, and the soil-mould row is the
                            # answer to it
                            "plant", "plants", "houseplant", "house plant", "compost",
                            # NOT "potting": its forms are {pot, potte, potting, pott}, so it
                            # turns this row down for every line with "pot" in it, and "my pot
                            # of curry went mouldy" stopped being binned. The same stem trap as
                            # "ironing" in nutrient-a-day. `potting soil` and `potting compost`
                            # say the same thing without the bare stem.
                            "potting soil", "potting compost", "soil", "seedling", "seedlings",
                            "garden", "terracotta", "saucer",
                            "chicken", "chickens", "meat", "beef", "pork", "lamb", "fish",
                            # a dog or a cat that has gone off its food is a refusal to eat, and
                            # "my dogs gone off his food" was binned as a stew. The pet rows say
                            # when to ring the vet.
                            "dog", "dogs", "puppy", "pup", "pups", "cat", "cats",
                            "kitten", "kittens", "pet", "pets", "vet", "rabbit", "hamster",
                            # "does pasta go off" and "how do i stop food going off" ask how
                            # long it keeps and how to make it last, not whether this pot is
                            # already gone: the shelf life is the keeping tables' answer.
                            "going off", "goes off", "do they go off", "does it go off",
                            "keep food from", "keep from", "prevent", "stop food", "last longer",
                            "make it last", "shelf life", "how long",
                            # "tell me a funny joke about soup" is a joke: "funny" is only a
                            # sign of spoiling next to a smell or a taste word.
                            "joke", "jokes", "comedy",
                            # a bubbling sourdough, a fizzing kombucha and a curdling sauce are
                            # cooking, not spoiling
                            "sourdough", "dough", "starter", "yeast", "prove", "proving",
                            "rise", "rising", "ferment", "fermenting", "kombucha", "kimchi",
                            "brew", "brewing", "curdle", "curdled", "curdling", "separated",
                            "stock cube", "stock cubes", "stock pot", "stockpot",
                            "split", "split sauce", "sauce split",
                            # "gone off" with a person's possessive is appetite, not spoiling:
                            # "my sister has gone off her food since her op" is the one thing
                            # nobody wants answered "Bin it." A pot has no owner.
                            "off her food", "off his food", "off their food",
                            "off our food", "off my food", "off your food",
                            "gone off food", "gone off eating",
                            # "the dog has gone off his food today" is a dog refusing his bowl,
                            # not a pot on the turn: a pet named in the line is the pet's answer.
                            "dog", "dogs", "puppy", "pup", "puppies", "cat", "cats",
                            "kitten", "kittens", "pet", "pets", "vet")))


# The commonest egg keeping question is about the raw ones in the box, and the keeping table's
# single egg answer opened with boiled eggs, so "how long do eggs keep" and "should i keep my eggs
# in the fridge or on the counter" both got a week of boiled eggs. Two entries, one apposite each.
ENTRIES.append(entry("keep-eggs", (("egg", "eggs"), KEEP_WORDS),
                     "Raw eggs keep about three weeks past the date on the box if they have stayed "
                     "cold, so the fridge is the place for them: in their carton on a shelf rather "
                     "than in the door, where the temperature swings. Go by the date and by how "
                     "they smell when you crack one.",
                     bias=1,
                     # a dish made of boiled egg is not a box of raw eggs: "how long does egg
                     # salad keep" was getting three weeks, which is the dangerous direction.
                     avoid=("salad", "sandwich", "sandwiches", "sarnie", "butty", "mayo",
                            "mayonnaise", "cress", "filler",
                            # "is it ok to eat eggs every day" and "are eggs good for you" are
                            # how many a week, not how many weeks in the box, and this row was
                            # answering them with the shelf life.
                            "every day", "everyday", "every morning", "daily", "a day",
                            "per day", "how many",
                            # the "every day" shapes only: a bare "ok to eat" is also how the
                            # date question is asked ("is it ok to eat eggs past the date"), and
                            # that one wants the three weeks in the box.
                            "ok to eat a day", "ok to eat every", "okay to eat every",
                            "fine to eat every", "good for you",
                            "healthy", "cholesterol", "too many", "how often")))


# What people actually put in the fridge is the made dish, and it keeps for days not weeks.
ENTRIES.append(entry("keep-egg-salad", (("egg salad", "egg mayonnaise", "egg mayo",
                                         "egg sandwich", "egg sandwiches", "egg sarnie",
                                         "egg and cress"),
                                        KEEP_WORDS + ("out", "overnight", "tomorrow")),
                     "Egg salad keeps 2 days in the fridge, covered, on a shelf rather than in the "
                     "door, and no more than 2 hours out at room temperature before it should go "
                     "in the bin: mayonnaise and boiled egg together is the part that turns. If it "
                     "has sat out at a picnic since morning, don't risk it.",
                     bias=2))


ENTRIES.append(entry("keep-boiled-eggs", (("egg", "eggs"),
                                          ("boil", "boiled", "boiling", "cooked", "hard boiled",
                                           "shell on", "peeled", "devilled", "deviled")),
                     "Boiled eggs keep about a week in the fridge with the shell on, and 2 to 3 "
                     "days once peeled, in a covered bowl of water. Raw ones in their shells keep "
                     "far longer: about three weeks past the date on the box if they stayed cold.",
                     # "boiled" is the cooking word as well as the keeping word, so this entry
                     # needs the keeping half of the question before it answers: "how long to
                     # boil an egg" is a timer, and the timer entry has that.
                     ask=("keep", "keeps", "keeping", "kept", "last", "lasts", "store", "stored",
                          "fridge", "ok", "safe", "week", "days",
                          # "how long are boiled eggs good for" is this question in the words
                          # most people use, and the timing row took it on "boiled"
                          "good for"),
                     bias=2))


# A food that is already cooked is a leftovers question, not a keeping one: "i have leftover
# boiled potatoes in the fridge" wants the 3-to-4-day reheating rule, not how to store a raw
# potato.
COOKED_WORDS = ("boil", "boiled", "boiling", "cooked", "leftover", "leftovers", "left over",
                "reheat", "reheated", "mashed", "roasted")


# "what can i do with a bag of apples going soft" is a request for a dish, not a shelf-life
# question, and it already has an answer: stewed apple. The keeping reply is now the more
# specific match for the food, so each keeping entry holds out the shapes that hand the food
# over to be cooked with.
USE_UP_WORDS = ("what can i do with", "what do i do with", "what to do with",
                "what can i make with", "what can i cook with", "use up", "use them",
                "using up", "recipe", "recipes", "idea", "ideas")


# "ok and how long in the oven", after a line about apples, is a question about cooking them:
# the food in the line is smaller than the question being asked. A keeping question almost
# never names the oven, so the cooking words take the line away from the shelf-life reply.
COOKING_WORDS = ("oven", "bake", "baking", "baked", "roast", "roasted", "fry", "frying",
                 "grill", "temperature", "minutes", "heat",
                 # "how long do i microwave an apple" was answered with how long apples keep,
                 # because the microwave is a way of cooking the food and not a way of storing
                 # it, and "heat" did not cover the word anyone actually says
                 "microwave", "microwaved", "microwaving", "steam", "steamed", "steaming",
                 "poach", "poached", "poaching")


STORING = ("how do i store", "how should i store", "how do you store", "best way to store",
           "how to store", "storing")


KEEP_EXTRA_WORDS = {food: KEEP_DATE_WORDS for food in ("butter", "cheese")}


# A curry paste, powder or spice mix is a jar in the cupboard, not a pot on the stove, and its
# keeping question is a different one (months, not days). "curry" is in the pot row's names, so
# the cupboard words hold the row off those lines.
KEEP_STAND_DOWN = {# "how long does garlic breath last" was answered with how long whole bulbs
                   # keep, because "how long" and "last" are the keeping words and "breath" was
                   # not a reason to stand down. A burned clove is the burn row's question too.
                   "garlic": ("breath", "bad breath", "garlic breath", "breathe", "breathing",
                              "smell", "smells", "smelt", "smelled", "stinks", "burn", "burnt",
                              "burned", "burning", "bitter", "black", "went black"),
                   "cheese": STORING + MOULD_WORDS + (
                       # "is my cheese off" is the mould question, and the row that cuts an
                       # inch around it answers better than the number of days does.
                       "off", "is bad", "are bad", "gone bad"),
                   # A pot that has gone mouldy or smells wrong is not asking how many days it
                   # keeps, and the keeping number is the dangerous direction: "my soup has gone
                   # mouldy" was answered "Soup keeps 3 to 4 days in the fridge". The same words
                   # that hold the cheese row off, plus the smell and the signs a person notices.
                   # "my cream smells off", "my mince has gone grey" and "the ham is slimy" are
                   # the spoilage cards next door, which say what to look at and when to bin it.
                   # "how long does sun cream last" and "how long does a cream tea keep" are not
                   # questions about a pot of double cream in the fridge: the cream in them is a
                   # different thing with its own date, so the row stands down for those words.
                   "cream": _SPOILT_WORDS + ("sun cream", "sunscreen", "hand cream", "face cream",
                                             "eye cream", "shaving cream", "moisturiser",
                                             "ice cream", "cream cheese", "cream tea",
                                             "cream cake", "cream cakes", "cream cracker",
                                             "cream crackers", "cream soda", "clotted",
                                             "creme egg", "cream liqueur"),
                   "avocado": _SPOILT_WORDS,
                   "mince": _SPOILT_WORDS,
                   "ham": _SPOILT_WORDS,
                   # "how long does orange juice keep" was this row, because "oranges" is in it
                   # and "juice" is not in any fruit row: squeezed fruit is a different
                   # question with a different number of days, so the row stands down for it.
                   "lemons": ("juice", "juices", "squash", "cordial"),
                   "soup": ("paste", "pastes", "powder", "powders", "spice", "spices",
                            "seasoning", "seasonings", "stock cube", "stock cubes")
                           + MOULD_WORDS + ("moulds",)}


# "how long to melt butter" and "can you toast cheese" carry "how long" like a keeping question
# and want the pan, not the fridge. "grated" is not here on purpose: "how long does grated cheese
# last" is still a shelf-life question.
METHOD_WORDS = ("melt", "melts", "melting", "melted", "toast", "toasted", "toasting")


# "soft" is a keeping word ("why have my potatoes gone soft") and a cooking word ("how do i know
# when potatoes are soft"), so the doneness questions have to be kept off the keeping entries.
# "how long to" was a bare phrase in here, and it took the keeping shape with it ("how long to
# keep potatoes" stopped answering at all), so the cooking verbs are spelled out instead.
DONENESS = ("know when", "know if they are done", "when they are done", "when it is done",
            "how long to cook", "how long to boil", "how long to roast", "how long to bake",
            "how long to microwave", "how long to air fry", "how long to airfry",
            "how long to grill", "how long to fry", "how long to steam", "tender")


# "can i eat green potatoes" is a safety question about solanine, not a shelf-life one, and
# "green" is one of the keeping words: the keeping answer said nothing about eating them.
GREEN_SAFETY_WORDS = ("can i eat", "eat them", "eat green", "safe", "poison", "poisonous",
                      "toxic", "solanine", "solamine")


# A cake is not the fruit it is named after: "how long does a lemon drizzle cake last" got the
# lemon shelf life, because "lemon" and "last" are the whole of that question's words. The baked
# goods are kept in their own answers, so every row of this table stands aside when the line
# names one.
BAKED_LINE_WORDS = ("cake", "cakes", "sponge", "sponges", "drizzle", "muffin", "muffins",
                    "cupcake", "cupcakes", "biscuit", "biscuits", "cookie", "cookies", "scone",
                    "scones", "brownie", "brownies", "loaf", "loaves", "bread", "bun", "buns",
                    "pastry", "pie", "pies", "tart", "tarts", "flapjack", "shortbread",
                    "crumpet", "crumpets", "teacake", "teacakes")


# The general cooked-food table answers what is left over, so any food with a keeping row of its
# own - a carrot, a lemon, a block of butter - must reach that row instead. The names come from
# KEEPS itself rather than from a list kept in step by hand.
# A cooked food keeps like cooked food whatever it was: the words that say the food is cooked,
# and the words that say the line is about keeping it. Both are needed - "how long do i roast
# potatoes" is a cooking time, and only "how long do roast potatoes keep in the fridge" is this
# table's question.
_COOKED_KEEPING = ("cooked", "cook", "boiled", "mashed", "stewed", "roast", "roasted",
                   "leftover", "leftovers", "left over")


# The ask of the cooked-food table. "fridge" is not in it, and it was: "nothing in the fridge what
# can i cook" and "what can i cook with an empty fridge" matched the subject on the loose form of
# "cooked" and the ask on the bare word "fridge", and were handed this keeping table instead of
# anything to cook. A fridge is where cooked food is kept; it is not a way of asking how long it
# keeps, and every keeping question either says keep/last/store or names what it keeps.
_KEEPING_ASK = ("keep", "keeps", "keeping", "store", "stored", "storage",
                "last", "lasts", "still ok", "still good", "gone off", "going off",
                "out of date", "use by", "overnight", "til tomorrow", "till tomorrow")


for _row in ENTRIES:
    if _row.id == "fridge-life":
        _row.avoid = _row.avoid + tuple(_name for _names, _ in KEEPS for _name in _names)
        # A cooked one of those foods is the other way round: it is cooked food, and it keeps
        # like cooked food, not like the raw carrot in the drawer. The keeping rows below hold
        # out COOKED_WORDS for exactly that reason, so this row picks the line up again when the
        # line says cooked - one entry, whatever the food, since the cooked table is one table.
        # The food itself is deliberately not in this key: "how long do i roast potatoes" is a
        # cooking time and "roast potato recipe" is a recipe, and both of those name a cooked
        # food. A line is this table's question when it says the food is cooked AND asks for how
        # long it keeps, and then the cooked table is the answer whatever the food was.
        # Cooked rice has a stricter rule than the rest (24 hours, and cool it fast), and it has
        # its own row, so it is not this table's answer even when the line says cooked.
        # A burnt dinner is not a keeping question: "i burnt the roast, is it still ok" and "the
        # roast is burnt, is it still ok" were given the cooked-food days, because "roast" is a
        # cooked word and "still ok" is the ask. The burnt-food answer says what to do with the
        # black and whether it can be eaten, and this row stands down for it.
        ENTRIES.append(entry("fridge-life-cooked", (_COOKED_KEEPING, _KEEPING_ASK),
                             _row.reply, bias=1,
                             avoid=("rice", "burnt", "burned", "charred", "scorched",
                                    "burnt on", "caught on the bottom")))


# A keeping question is about a food, and "stuff" is what people say when they have not named
# one. "my freezer is full of stuff, whats the oldest thing i can keep" reached the stuffing row,
# because the forms of "stuffing" include "stuff" (the -ing strip with the doubled letter taken
# off it), so a word that names no food put a food in the line. These rows stand down for a line
# like that and leave the question to the answer that names no food of its own, or to a punt.
# Only words that never name a food are here: "things" and "bits" sat in the first draft and
# stood the chicken row down for "some bits of chicken left over".
_A_BLANK_FILLER = re.compile(r"\b(?:stuff|junk|odds and ends)\b")


def _a_food_and_not_a_blank(understood):
    """False when the line says "stuff" where the food should be, and that is all it says."""
    clean = str((understood or {}).get("clean") or "").lower()
    return not _A_BLANK_FILLER.search(clean)


# "Are my mushrooms off" is the keeping question in the words people use most, and it was not
# a keeping question at all: the ask above knew "gone off" and "going off" but not the plain
# "is off" people type, so the line fell through to whatever dish happened to name the food -
# roast potatoes for "are my potatoes off", garlic mushrooms for "are my mushrooms off", carrot
# soup for the carrots. The words here are the bare ones that only a spoilage question says;
# "off the heat" and the rest of the prepositions are held out because a line about keeping a
# food has to keep it, not take it off something.
_OFF_ASK = ("off", "is bad", "are bad", "gone bad", "gone over", "past it", "off yet",
            "already off", "off to eat", "off by now")


# A bare "off" is also a preposition, and the same list the spoilage rows use keeps those lines
# out of the keeping rows: the skin off a fish, the pan off the heat, the day off.
_OFF_THE_THING = ("off the", "off my", "off your", "off his", "off her", "off its", "off them",
                  "off it", "cut off", "cutting off", "chop off", "chopping off", "slice off",
                  "skin off", "take the skin", "fat off", "off the bone", "turn off", "turned off",
                  "switch off", "switched off", "day off", "days off", "time off", "off work",
                  "off sick", "show off", "better off", "worse off", "off the menu",
                  "off the heat", "off the hob", "off the plate", "off the pan", "take it off",
                  "take them off")


# The vegetables whose only other keeping answer is the general "most veg keeps a week" card.
KEEP_AHEAD_OF_THE_GENERAL = frozenset(("courgette", "aubergine", "broccoli", "radish",
                                       "butternut squash", "cabbage"))


for _names, _reply in KEEPS:
    # bias keeps these ahead of the cooking-time entries, which also match "how long" - a
    # potato that is being kept is not a potato that is being boiled.
    # eggs are not in this table any more: raw and boiled eggs keep for such different times
    # that each has its own entry below. The guards stay as they were for everything else.
    _avoid = (STORING if "egg" in _names[0]
              else COOKED_WORDS + USE_UP_WORDS + COOKING_WORDS + DONENESS + METHOD_WORDS
              ) + BAKED_LINE_WORDS
    if _names[0] == "potato":
        _avoid = _avoid + GREEN_SAFETY_WORDS
    _avoid += KEEP_STAND_DOWN.get(_names[0], ()) + KEEP_QUALITY_WORDS + _OFF_THE_THING
    _key = KEEP_WORDS + _OFF_ASK + KEEP_EXTRA_WORDS.get(_names[0], ())
    # bias=2 for the six vegetables added with no row of their own: `veg-keep` names them all
    # and keys the phrase "how long", which scores higher than this row's plain "keep", so
    # "how long do radishes keep" was told "most veg keeps about a week" while the radish row
    # sat one place below it. A row named on the food itself is the more specific answer.
    _bias = 2 if _names[0] in KEEP_AHEAD_OF_THE_GENERAL else 1
    ENTRIES.append(entry("keep-%s" % _names[0], (_names, _key), _reply, avoid=_avoid,
                         bias=_bias, guard=_a_food_and_not_a_blank))


for _names, _reply in COOKED_KEEPS:
    # bias=2: the cooking-time entry for the same food matches "how long" with a phrase and
    # scores higher than a plain word, and a cooked food that is being kept is not being cooked
    # again. ask= keeps every "how long to cook/simmer/fry it" line with the method entry.
    # "how long is cooked bacon good for" is shelf life said plainly: the phrase is here and
    # not in KEEP_WORDS because "is butter good for you" is a health question, and the day's
    # keeping clock is the wrong answer to it. A cooked word has to be in the line as well
    # (ask=COOKED_KEEP_ASK), so the phrase cannot reach those.
    # The freezer words are here rather than in KEEP_WORDS: a raw food in the freezer is a
    # different question (potatoes go black, beans get blanched), and every one of these rows
    # says how long the cooked food freezes for. "can i freeze cooked mince" was answered with
    # how to brown mince, and "can i freeze cooked chicken" with the raw chicken's fridge days.
    ENTRIES.append(entry("cooked-keep-%s" % _names[0],
                         (_names, KEEP_WORDS + ("good for",) + FREEZER_WORDS),
                         _reply,
                         avoid=USE_UP_WORDS + ("raw", "uncooked", "freezer burn") + STILL_FROZEN_WORDS
                         # "shelf life of cooked chicken" is main's chicken-storage row, which
                         # carries the same days: two keeping entries for one food is one too
                         # many, so the newer one holds that phrase out.
                         + ("shelf life", "shelf-life")
                         + COOKED_KEEP_AVOID,
                         bias=2, ask=COOKED_KEEP_ASK,
                         guard=lambda u: _already_cooked_is_the_question(u)
                         and _a_food_and_not_a_blank(u)))


# The cooked and bought things people ask about the day after. These are rows in the same table,
# but their line often says "cooked" or "baked" about the food itself, which the KEEPS guard reads
# as a different question, so they hold out only the shapes that really are one.
KEEPS_COOKED = (
    (("jacket potato", "jacket potatoes", "baked potato", "baked potatoes", "potato skins"),
     "A jacket potato is fine the next day: cool it within an hour, keep it in the fridge covered "
     "and eat it within 2 days, skin and all. Reheat it until it is piping hot right through, or "
     "cut it up and fry it - a foil-wrapped one left on the side overnight goes in the bin."),
    (("coleslaw", "slaw"),
     "Coleslaw keeps 3 days in the fridge once it is opened, and homemade 2, because it is the "
     "mayonnaise that turns. Keep the tub cold and eat it by the date on it, and bin slaw that "
     "smells sharp or has gone watery in the bottom of the tub."),
    (("scone", "scones", "fruit scone", "cheese scone"),
     "Scones are best the day they are made and keep 2 days in a tin, or a day in the fridge. "
     "Sprinkle them with water and give them 3 minutes in a warm oven to bring them back; freeze "
     "them on the day and refresh from frozen, and bin any with green on them."),
    (("sushi", "shop sushi", "sushi box"),
     "Shop sushi is made to be eaten the day you buy it: keep it in the fridge, eat it within 24 "
     "hours and do not leave it out on the side. The rice and the raw fish are what go off, so "
     "bin what is left rather than keeping it for tomorrow."),
    (("tuna", "tinned tuna", "tin of tuna", "canned tuna"),
     "An opened tin of tuna keeps 2 days in the fridge, emptied into a bowl with a lid - left in "
     "the tin it tastes of metal. Eat it cold in a sandwich or flake it through a sauce, and do "
     "not freeze it, because it comes back dry and woolly."),
    (("cooked salmon", "cooked fish", "leftover salmon", "leftover fish", "smoked salmon"),
     "Cooked salmon keeps 2 days in the fridge, covered, and it is better cold in a salad than "
     "reheated, which dries it out. Cool it within an hour of cooking and bin it after 2 days; "
     "smoked salmon keeps 3 days once the pack is open and freezes for a month."),
    (("prawn", "prawns", "cooked prawns", "king prawns"),
     "Cooked prawns keep 2 days in the fridge, in a sealed box away from anything raw, and ones "
     "from the deli counter keep a day less than a sealed pack. Eat them cold or warm them through "
     "in a sauce rather than frying them again, and bin any that smell of ammonia."),
    # The dinner-table leftovers are a shorter keep than the roast that made them, and every one
    # of these was a shrug or the 3 to 4 days of a general cooked-food rule. Gravy and custard
    # especially: both are liquid, both cool slowly in the jug, and 3 to 4 days is too long.
    (("gravy", "gravies", "onion gravy", "leftover gravy", "brandy sauce"),
     "Gravy keeps 2 days in the fridge, less than the meat does, because it is mostly liquid and "
     "it cools slowly in the jug: get it in within 2 hours of making it, standing the jug in a "
     "bowl of cold water if it is still hot. Reheat it until it boils right through, and bin any "
     "that has sat out on the table all evening."),
    (("stuffing", "sage and onion", "forcemeat", "stuffing balls"),
     "Cooked stuffing keeps 2 days in the fridge and it is the leftover to be strict with, because "
     "it has been inside the bird and soaked up the juices: cool it within 2 hours, box it, and "
     "reheat it until it is piping hot right through. Stuffing that never went in the oven is a "
     "different thing and keeps as long as the bread in it."),
    (("custard", "homemade custard", "custard sauce", "creme anglaise"),
     "Homemade custard keeps 2 days in the fridge, in a jug with a lid or a sheet of cling film "
     "pressed onto the surface so no skin forms. Reheat it gently and stir rather than boiling it, "
     "and bin any that has stood on the table through dinner."),
    (("trifle", "trifles", "sherry trifle"),
     "A trifle keeps 2 days in the fridge, and it is the cream and the fruit that turn rather than "
     "the sponge: cover it once it is made and eat it within a day or two. Do not freeze it - the "
     "cream splits and the sponge goes watery."),
)


# "can i reheat gravy" is a keeping question with none of the keeping words in it, so the rows
# whose food is a sauce or a set pudding take the reheat shapes as well as the shelf-life ones.
# "can i do the gravy ahead" and "can i do the stuffing the night before" are keeping questions in
# the doing-it form, and the list held only the making-it form ("make ahead", "make it ahead")
# and "the day before". So the plain "do the X ahead" shape reached nothing and the person got the
# hedge, while "can i do the cake ahead" worked only because cake has a card of its own. "ahead"
# is here as a word and not only in the two phrases for that reason: what follows the food is
# "ahead", "ahead of time" or "the night before", and the food name is already the other half of
# the key. This is the making-ahead frame for every cooked food, not one line's wording.
KEEPS_COOKED_WORDS = KEEP_WORDS + ("reheat", "reheating", "reheated", "heat up", "heated up",
                                  "warm up", "warmed up", "make ahead", "make it ahead",
                                  "do it ahead", "do that ahead", "ahead", "ahead of time",
                                  "in advance", "the day before", "day before", "the night before",
                                  "night before", "keep it warm")


for _names, _reply in KEEPS_COOKED:
    ENTRIES.append(entry("keep-" + _names[0].replace(" ", "-"), (_names, KEEPS_COOKED_WORDS),
                         _reply,
                         bias=1,
                         guard=_a_food_and_not_a_blank,
                         avoid=USE_UP_WORDS + DONENESS + (
                             "how long to cook", "how long to bake", "how long to boil",
                             "how long to fry", "how do i cook", "how do i make", "recipe",
                             "in the oven", "microwave", "air fryer", "temperature")))


# The general cooked-food table is the answer for a food with no keeping row of its own, and the
# rows above are the list of the ones that have one: "how long does stuffing last in the fridge"
# was getting "cooked food keeps 3 to 4 days" while the stuffing row sat one line away. This is
# the same stand-down the raw keeping rows write for themselves further up, written here because
# the cooked table is defined below it.
for _row in ENTRIES:
    if _row.id == "fridge-life":
        _row.avoid = _row.avoid + tuple(_name for _names, _reply in KEEPS_COOKED
                                        for _name in _names)


# "what can i make with the leftovers" is a meal question, not a keeping one: the keeping
# entries answer how long they last, and this one answers what to do with them. It is written
# here, after the pantry table, because the foods it must stand down for are the pantry's own:
# a line that names one of them keeps the answer that names it.
_NAMED_FOODS = tuple(sorted({word for aliases, _reply in PANTRY.values() for word in aliases}))


_FOODS_SAID = None


def _foods_said():
    """Every food name the pantry and the staples table know, with its plural undone."""
    global _FOODS_SAID
    if _FOODS_SAID is None:
        _FOODS_SAID = ({_fold(str(word).lower()) for word in _NAMED_FOODS}
                       | {_fold(str(word).lower()) for word in _STAPLE_NAMES})
    return _FOODS_SAID


def _leftover_meal_reply(memory, understood):
    """Soup for the leftovers nobody named, and the named food's own use when one is named.

    "What can i do with leftover chard" was answered with the soup paragraph above, which is the
    answer to a fridge with odds and ends in it and not to a chard. The food named is asked for
    its own use first; where the pantry's idea for it is a dish, that idea wins in the meal table
    and this row never sees the line.
    """
    from ..knowledge import meals
    words = understood.get("words") or ()
    if isinstance(words, str):
        words = words.split()
    words = tuple(words) or tuple(str(understood.get("clean") or "").lower().split())
    named = meals.named_food(words, understood)
    if named in LEFTOVER_IDEAS:
        # Mince, chicken, rice and the rest have an idea of their own, and it is a use.
        return LEFTOVER_IDEAS[named]
    if named:
        idea = PANTRY.get(named, (None, ""))[1] if isinstance(PANTRY.get(named), tuple) else ""
        if not meals.idea_is_a_dish(idea):
            said = meals.use_it_up(named)
            if said:
                return said
    return LEFTOVER_SOUP


ENTRIES.append(entry(
    "leftover-meal",
    (("leftovers", "leftover", "left over", "odds and ends", "bits and pieces",
      "left in the fridge"),
     ("make", "made", "cook", "meal", "dinner", "tea", "supper", "soup", "ideas",
      "recipe", "recipes", "what can i", "do with", "use up", "using up", "turn into",
      "throw", "waste")),
    _leftover_meal_reply,
    ask=("how", "what", "can", "could", "any", "ideas", "should", "do i", "i have",
         "need", "got", "have"),
    # A line that names the food keeps the entry that names it: "what can I make with leftover
    # rice" is the rice question, "leftover mince" is the ragù and "half a roast chicken left
    # over" is the chicken one. This entry answers the general "i have leftovers, what can i
    # make", so it stands down for every food the pantry knows, and for the rest bias keeps a
    # named food ahead of it.
    bias=-2,
    # a keeping, freezing or safety question is not the cooking one
    avoid=("how long", "safe", "safely", "fridge", "freezer", "freeze", "frozen", "refreeze",
           "re-freeze", "refroze", "defrost", "defrosted", "thawed", "reheat", "reheated",
           "room temperature", "left out", "gone off", "smell", "smells", "sick", "pregnant",
           "dog", "cat", "bin", "keep") + _NAMED_FOODS))


LEFTOVER_WORDS = frozenset("leftover leftovers cooked stale yesterday".split())


# Words that say an ingredient is already cooked, so a dish whose first step is browning or
# boiling it is the wrong answer: "leftover roast chicken and rice" wants the fried rice, not a
# pan of raw thighs. A dish takes a cooked ingredient only when it says so in "cooked".
COOKED_WORDS = frozenset("""
leftover leftovers cooked roast roasted mashed already precooked pre-cooked yesterday
""".split())


# "leftover roast chicken and rice": the "leftover" belongs to the chicken, not to the rice on
# the other side of the "and", so a look-back stops at a word that joins two ingredients.
JOINERS = frozenset("and or plus with also then &".split())


def _words_just_before(folded, place, reach):
    """The words before an ingredient that still describe it, up to a word that joins things."""
    window = []
    for word in reversed(folded[max(0, place - reach):place]):
        if word in JOINERS:
            break
        window.append(word)
    return window


# The words that make a line a meal question rather than a question about one ingredient.
MEAL_CUES = frozenset("""
make makes made making cook cooking bake baking baked meal meals dinner tea lunch supper brunch snack
idea ideas recipe recipes quick quickish something anything leftover leftovers use eat
""".split())


# Food words strong enough to make a meal question on their own, even when the reading of the
# line missed the cooking topic.
FOOD_CUES = frozenset("""
dinner lunch supper brunch meal meals tea cook cooking bake baking recipe recipes idea ideas
leftover leftovers
""".split())


# A timing or a temperature wants a number, not a meal idea, and so does a question about why
# something went wrong.
NOT_MEAL_ASKS = frozenset("how_long how_much how_often how why".split())


# A line asking what to use in place of a food wants a substitute, not a dish that needs it
# ("what can i use instead of eggs and milk" is not a request for a cheese omelette).
SUBSTITUTE_WORDS = frozenset("""
substitute substitutes substitution substitutions instead swap swaps swapping replace replaces
replacing replacement alternative alternatives
""".split())


# A line with one of these is asking whether something is safe, raw or off, which is a fact the
# knowledge entries answer, not a meal to cook.
PROBLEM_WORDS = frozenset("""
safe safely safety poison poisoning reheat reheated reheating raw undercooked overcooked
overcook undercook mould mouldy mold moldy expired expiry defrost thaw thawed freezer
ill sick stomach allergic allergy date burnt burned
pox chickenpox flu fever cough poorly unwell infection virus covid sore headache migraine
toothache nausea nauseous vomiting diarrhoea rash bleeding pregnant
""".split())


# "What do I eat while I'm ill" is a food question, and the food is the plain one. The illness is
# named as a phrase, never as the single word "cold": "is it safe to eat cold rice" is a keeping
# question, not somebody with a cold.
SICK_PHRASES = ("im sick", "i'm sick", "i am sick", "ive been sick", "i've been sick",
                "being sick", "feel sick", "feeling sick", "felt sick", "im ill", "i'm ill",
                "i am ill", "been ill", "feeling ill", "poorly", "unwell", "stomach bug",
                "tummy bug", "sick bug", "food poisoning", "a cold", "my cold", "got a cold",
                "have a cold", "flu", "a temperature", "sore throat", "nauseous", "nausea",
                "throwing up", "vomiting", "hangover", "recovering from", "getting over",
                "no appetite", "lost my appetite", "off my food",
                # naming the bug rather than being ill with it: "how do i avoid cross
                # contamination" is the same prevention question as food poisoning is.
                "cross contamination", "cross-contamination", "contamination",
                # the worry without the name, but with the food in it: "how do i avoid
                # getting ill from food". A bare "get sick" is left out on purpose: it is
                # how an intolerance reads ("i get sick when i eat dairy").
                "ill from food", "sick from food")


# The eating words that make it a question about food rather than a report of being ill.
SICK_EAT_WORDS = ("eat", "eating", "food", "drink", "drinking", "appetite", "meal", "meals",
                  "dinner", "tea", "lunch", "breakfast", "snack", "keep down", "stomach",
                  # the cause rather than the illness: "cross contamination" is a food-safety
                  # word, and the entry's reply reads it as the prevention question.
                  "contamination", "contaminated", "cross contamination")


# Keeping it off the plate is the question before this one. "how do i not get food poisoning on
# holiday" names an illness and eats something ("food" is half of the illness), so the
# what-to-eat-while-ill answer took it and told a person who was not ill yet what to eat when
# they were. A line that asks how to avoid it is a prevention question, and the entry stands
# down on the shape of the ask rather than on a place, so "how do i avoid getting dehydrated"
# named with the same words still reaches whichever entry is about the water.
PREVENTION_ASK = re.compile(
    r"\b(?:avoid|avoiding|prevent|preventing|not\s+get|don'?t\s+get|dont\s+get|never\s+get|"
    r"stop\s+(?:me\s+)?getting|protect\s+(?:myself|yourself|against))\b"
    # Being ill is the thing the line is trying not to be: "how do i defrost a chicken without
    # giving myself food poisoning" is a kitchen question with a worry attached, and it was told
    # to eat toast and crackers. The worry comes in the same shapes as the ones above, only with
    # a verb of giving in place of avoid: "without poisoning everyone", "so we dont all get ill".
    r"|\b(?:without|so\s+(?:i|we|they|he|she)\s+don'?t|so\s+(?:i|we|they|he|she)\s+dont)\s+"
    r"(?:\w+\s+){0,3}?(?:poison\w*|getting\s+ill|get\s+ill|becoming\s+ill|going\s+off)\b")


# A prevention line that names no food and no place is the general question - "how do i avoid
# food poisoning", "how do i avoid food poisoning at home" - and it had no answer at all: the
# travel entry took it and gave street-food advice for a trip abroad, and once that stood down
# the line fell to the search hedge. The four rules below are the answer to it.
AWAY_FROM_HOME = frozenset("""
abroad holiday holidays travelling traveling trip trips camping mexico india egypt thailand
turkey morocco peru kenya bali spain france greece italy portugal america usa canada australia
airport plane flight hotel resort street beach restaurant takeaway abroad
""".split())


# "how do i avoid getting ill from food" is the same question in plainer words.
_SICK_FROM_FOOD = re.compile(r"\b(?:ill|sick)\s+(?:from|off)\s+food\b")


def _eat_when_ill(memory, understood):
    """What to eat while you are ill: plain, small, and more to drink than you want."""
    text = ((understood or {}).get("clean") or "").lower()
    if PREVENTION_ASK.search(text) or "contamination" in text or _SICK_FROM_FOOD.search(text):
        # How to keep it off the plate, when the line names nothing that has its own answer:
        # a food ("how do i store rice without getting food poisoning") or a trip
        # ("how do i avoid food poisoning on holiday") is that entry's question, not this one.
        if ingredients(understood) or set(_plain_words(text)) & AWAY_FROM_HOME:
            return None
        return FOOD_SAFETY_RULES
    return ("Keep it plain and small: toast, crackers, rice, a banana, clear soup or plain "
            "yoghurt, and sip more than you feel like - little and often beats one big glass. "
            "Go back to proper meals over a day or two, and get advice the same day if you "
            "cannot keep any drink down or you are passing much less urine than usual.")


# The meal words that make a vague "nothing in" a kitchen line: "theres nothing in for tea" is
# about supper, and "i have nothing in the house to wear" is not. A wardrobe, a letter and a
# dog's bowl all have nothing in them, so the vague forms only count next to one of these.
MEAL_WORDS = frozenset("dinner tea supper lunch eat eating cook cooking food meal meals "
                       "bite takeaway order".split())


# A line about the dog's dinner is not a line about an empty kitchen.
PET_WORDS = frozenset("dog dogs cat cats puppy kitten hamster rabbit pet pets bird".split())


_INGREDIENT_WORDS = {}


def _fold(word):
    """A word with its plural undone, so eggs/egg and tomatoes/tomato are one word."""
    word = str(word).lower().replace("\u2019", "'").strip(".,!?;:'\"")
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith("oes"):
        return word[:-2]
    if len(word) > 3 and word.endswith("es") and word[-3] in "sxzh":
        return word[:-2]
    if len(word) > 2 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _fold_meal_ideas():
    """Fold the older meal-ideas list into PANTRY, so one table answers every way of asking.

    The list at the top of the file and the pantry below hold the same knowledge kept twice: an
    ingredient's fuller idea there, a shorter one here, so the same ingredient was answered one
    way by a pair ("eggs and spinach") and another by a single name ("what can I make with
    eggs"), and an ingredient in neither table fell through to "I don't know" ("got some turkey
    mince in"). Each row joins the pantry row that already answers for it and adds any name the
    pantry did not have; a name that is nobody's yet becomes a row of its own. A name another
    row already answers for is left where it is, so "salmon" stays salmon and never becomes fish.
    """
    # "veg" and "vegetables" were aliases of broccoli, which answers a question about broccoli
    # wrongly: they are the vague word for whatever greens are in. They get a row of their own
    # below; in a pair they are dropped (VAGUE), because "mince and some veg" is one dinner.
    vague = {_fold(word) for word in VAGUE}
    for name in list(PANTRY):
        aliases, idea = PANTRY[name]
        kept = tuple(alias for alias in aliases if _fold(alias) not in vague)
        if kept and kept != tuple(aliases):
            PANTRY[name] = (kept, idea)
    claimed = {}
    for name, (aliases, _idea) in PANTRY.items():
        claimed.setdefault(name, name)
        for alias in aliases:
            claimed.setdefault(_fold(alias), name)
    for names, idea in MEAL_IDEAS:
        group = tuple(name for name in names if _fold(name) in vague)
        solid = tuple(name for name in names if _fold(name) not in vague)
        if group and all(_fold(name) in claimed for name in solid):
            # A row that leads with "vegetables" and lists real greens beside it is the idea for
            # the group word: each green already has its own row, so the idea is the veg row's.
            PANTRY.setdefault(_fold(group[0]), (group, idea))
            for name in names:
                claimed.setdefault(_fold(name), _fold(group[0]))
            continue
        # The row joins the row of the food it leads with, and only that one: a row written as
        # ("fish", "salmon", "cod") is an idea for fish, and folding it into the salmon row made
        # "cod" and "fish" answer "Roast salmon at 200C", which is a different fish. A later name
        # that already has a row of its own keeps it, because that row knows more.
        key = None
        for name in names:
            if _fold(name) in vague:
                continue
            key = claimed.get(_fold(name))
            break
        if key is None:
            key = _fold(names[0])
            alone = tuple(name for name in names
                          if _fold(name) not in claimed or name == names[0])
            PANTRY[key] = (alone, idea)
        else:
            aliases, short = PANTRY[key]
            extra = tuple(name for name in names
                          if _fold(name) not in claimed and _fold(name) not in vague)
            PANTRY[key] = (tuple(aliases) + extra, short)
            # The row keeps the pantry's own wording: the older list holds the same knowledge,
            # and the pantry's is the one the other entries already answer with.
        for name in names:
            claimed.setdefault(_fold(name), key)


_fold_meal_ideas()


for _name, (_aliases, _idea) in PANTRY.items():
    for _alias in _aliases:
        _INGREDIENT_WORDS[_fold(_alias)] = _name


# Every name the pantry answers for, longest first: a two-word name ("turkey mince", "chicken
# thigh") has to be tried before either of its words on their own, or one food counts as two.
_ALIASES_BY_LENGTH = sorted(((tuple(_fold(_alias).split()), _name)
                             for _name, (_aliases, _idea) in PANTRY.items()
                             for _alias in _aliases),
                            key=lambda pair: -len(pair[0]))


# The alias as people write it, because a reply says "frozen spinach" and not "frozen spinac":
# the folded parts are what the matcher sees, the alias is what the answer shows.
_ALIAS_TEXT = {tuple(_fold(_alias).split()): _alias
               for _name, (_aliases, _idea) in PANTRY.items()
               for _alias in _aliases}


# --- the same food in another form -----------------------------------------------------------
#
# "can i use frozen spinach instead" and "tinned tomatoes instead of passata" name one food in a
# different form, not a second food. The pair verdicts above need two foods, so they pass, and the
# pantry table read the line as a dish ("what can i make with spinach"). The adjustment is the
# same whichever food it is - water, salt, heat, time - so the table is per form and the food's
# own word goes into the sentence.
FORMS = (
    ("frozen", ("frozen", "freezer")),
    ("tinned", ("tinned", "canned", "tin of", "can of")),
    ("dried", ("dried", "dry")),
    ("jarred", ("jarred", "jar of")),
    ("fresh", ("fresh",)),
)


FRUIT_WORDS = frozenset("""fruit fruits berry berries raspberry raspberries strawberry
    strawberries blueberry blueberries blackberry blackberries cherry cherries plum plums peach
    peaches mango mangoes pineapple banana bananas apple apples rhubarb currant currants
    gooseberry gooseberries""".split())


def _form_word(words, start, span):
    """The form the matched food is sold in: in its own name or just in front of it."""
    for word in words[start:start + span]:
        for form, names in FORMS:
            if word in names:
                return form
    for word in words[max(0, start - 2):start]:
        for form, names in FORMS:
            if word in names:
                return form
    return ""


def _form_swap(memory, understood, text=None):
    """The same food in another form, asked with an "instead"/"what can i use" line, or None."""
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    folded = [_fold(word) for word in words]
    if text:
        folded += [_fold(word) for word in str(text).lower().split()]
    said = " ".join(folded)
    if not any(ask in said for ask in _SWAP_ASK):
        return None
    used = [False] * len(folded)
    first = None
    seen = []
    head = ""
    for parts, name in _ALIASES_BY_LENGTH:
        span = len(parts)
        for start in range(len(folded) - span + 1):
            if any(used[start:start + span]):
                continue
            if all(folded[start + offset] == parts[offset] for offset in range(span)):
                for offset in range(span):
                    used[start + offset] = True
                seen.append(name)
                form = _form_word(folded, start, span)
                if form and first is None:
                    first = (start, span, form, _ALIAS_TEXT.get(parts, " ".join(parts)), name)
                    head = next(names for one, names in FORMS if one == form)
                break
    if first is None:
        # "can i use frozen fruit instead of fresh" names a class the pantry has no row for, and
        # the freezer answers the same way for all of it.
        for index, word in enumerate(folded):
            if word in FRUIT_WORDS and _form_word(folded, index, 1) == "frozen":
                return FROZEN_FRUIT
        return None
    start, span, form, spoken, food = first
    # The key no longer names the foods, so the reply says which ones a form question is asked
    # about: fresh, frozen, tinned or dried is a real choice for those, and not for milk.
    if food not in FORM_FOODS:
        return None
    # A second, different food is the pair verdicts' question ("yoghurt instead of cream"), and
    # this entry would answer it with half an answer. The same food in another form is not:
    # "tinned tomatoes instead of passata" is still a form question, and the tin has its say.
    if any(other != food for other in seen):
        return None
    # "tinned tomatoes" already says the form, and the sentence says it too
    first_word = spoken.split()[0].lower() if spoken.split() else ""
    if first_word and any(first_word == form_word for form_word in head):
        spoken = " ".join(spoken.split()[1:]) or spoken
    # The lack has to come before the food: "frozen peas out of the bag" is about using them,
    # "i havent got frozen peas" is about not having them.
    if any(ask in " ".join(folded[:start + span]) for ask in OUT_ASKS):
        return OUT_OF_FORM[form].format(food=spoken)
    if form == "frozen":
        if food in MEAT:
            return FROZEN_MEAT.format(food=spoken)
        if food in FRUIT_WORDS:
            return FROZEN_FRUIT
    return FORM_ADVICE[form].format(food=spoken)


# The words those foods answer to, folded the way the line's words are.
_FORM_FOOD_WORDS = tuple(sorted({word
                                 for name in FORM_FOODS
                                 for alias in PANTRY.get(name, ((), ""))[0]
                                 for word in _fold(alias).split()}
                                | set(FORM_FOODS)))


# The form question: a form word, and a line that is asking to swap one form for another. The
# food itself is not in the key: a key that names every food in the pantry makes those words
# common to the whole table and costs the dish entries the rarity that lets them win ("quick
# dinner ideas using tinned tomatoes and pasta" went to the meal ideas instead of the sauce).
# Without the swap wording it is a dish question ("what can i make with fresh tuna"), and
# without a form word it is the pair verdicts' question ("milk instead of cream").
FORM_SWAP_WORDS = ("instead", "swap", "swapping", "substitute", "replace", "out of",
                   "ran out", "run out", "havent got", "havent any", "dont have", "didnt have",
                   "no fresh")


# Bare "canned" is left out of the key: "can" is read as the tinned form, so "can i use milk
# instead of cream" would score here too, and that line is the pair verdicts' question. "can of"
# stays, because the modal is never followed by "of".
ENTRIES.append(entry("form-swap", (tuple(word for _form, names in FORMS for word in names
                                        if word != "canned"),
                                  FORM_SWAP_WORDS),
                     # no bias: where a swap entry of its own exists ("dried herbs instead of
                     # fresh" is the dried-herbs row), that row is the one to answer.
                     _form_swap, ask=_SWAP_ASK,
                     # a keeping question is the KEEPS table's, not this one
                     avoid=("keep", "keeps", "keeping", "store", "storing", "last", "lasts",
                            "gone off", "going off", "mouldy")))


# A food behind one of these words is a food the line has not got, and "no", "without" and "out
# of" were here already. The have/has/had/did family was not, so "i havent got any potatoes" was
# read as potatoes in the house: the potatoes were named as an ingredient and kept in the plan,
# and the dinner built from that kitchen a turn later was a plate of mash. They are the same
# limit as "no potatoes" in the wording people actually use, so they belong in the same list.
NEGATIONS = frozenset("""
without no not except minus avoiding avoid hate hates hateful allergic dislike dont don't
never leave skip skipped out off
stand wont won't refuse refuses sick
havent haven't hasnt hasn't hadnt hadn't didnt didn't
""".split())


# The words that start a new thought, so a refusal in front of them is about another food: "no
# pasta but chicken" keeps the chicken.
CLAUSE_BREAK = frozenset("but though although however except apart besides instead also".split())


def _refused_before(folded, place):
    """True when a phrase in front of the food rules it out ("im not a fan of lentils")."""
    if place <= 0:
        return False
    window = []
    for word in reversed(folded[max(0, place - REFUSAL_REACH):place]):
        if word in CLAUSE_BREAK:
            break
        window.insert(0, word)
    plain = " " + " ".join(window) + " "
    return any((" " + cue + " ") in plain for cue in RULING_OUT_PHRASES)


# The words that carry no food of their own, so a line made only of them and of pantry names is
# a list of what is in the kitchen and nothing else ("potatoes and cheese", "eggs, spinach").
FILLER = frozenset("""
a an the and or plus too also some a bit little half of with without im i am m we us my our
have has got get only just thats that it is are so oh hey hi and its ive weve some more
i'm im you're we're theyre
nah nope yeah yep yeh eh well ok okay hmm hm um umm er erm literally honestly actually
""".split())


_DIET_WORDS = frozenset(word for _cues, _ruled in DIETS for _cue in _cues for word in _cue.split())


# A negation softened by one of these is not a refusal: "i dont have much cheese" and "im not
# sure about cheese" both still want cheese, and answering them with a list that has none in it
# ignores the only food the line named.
# "just" and "only" are in here for a different reason: "no, just eggs and rice" is the person
# turning down the bot's suggestion and naming what they have, and read as a negation of the eggs
# it answered "No egg then: a spoon of cornflour..." to a full fridge.
SOFTENED = frozenset("much many sure enough lots lot bit little some just only".split())


# A food word with one of these in front of it is part of the day's own object, not something to
# cook: an "easter egg", a "christmas cake" and a "chocolate egg" are answered by the day, not by
# the pantry. It also stops "easter egg ideas for toddlers" coming back as a scrambled egg recipe.
EVENT_HEADS = frozenset("""christmas easter thanksgiving halloween birthday wedding anniversary
christening funeral wake valentine valentines chocolate""".split())


def _renamed_by_an_event(folded, place):
    """True when the word just before the food makes it another thing ("easter egg")."""
    if place == 0:
        return False
    return folded[place - 1] in EVENT_HEADS


def _named_ingredients(understood):
    """Every pantry ingredient the line names, with whether the line rules it out.

    Returns (named, negated): the ingredient names in the order the line names them, and the
    ones a word like "no", "without" or "allergic to" in front of them takes back out again.

    The longest name wins: "turkey mince" is turkey rather than turkey and mince, and a word
    already used by a longer name is not counted twice, so one food in the kitchen gives one
    ingredient instead of two half answers.
    """
    if not isinstance(understood, dict):
        return [], []
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    folded = [_fold(word) for word in words]
    # A slipped food name is still that food: "a chickn recipe", "im lookin for a recipe wiv
    # chickn" and "chickn and broccoli" named no ingredient at all, so "a chickn recipe" got
    # "Thanks for telling me" while "a chicken recipe" got the roast. The engine has already
    # repaired the slips in `plain`, in the same places and the same number of words, so the
    # table is read against the repaired line. It is swapped in place rather than added to the
    # end, because a name in the wrong place reads as a thing somebody ruled out.
    repaired = [_fold(word) for word in str(understood.get("plain") or "").split()]
    if len(repaired) == len(folded) and repaired != folded:
        folded = repaired
    told = _READ_FOR_INGREDIENTS.get(tuple(folded))
    if told is None:
        told = _work_out_ingredients(folded)
        if len(_READ_FOR_INGREDIENTS) >= _READ_FOR_INGREDIENTS_KEEP:
            _READ_FOR_INGREDIENTS.clear()   # a card of lines, not a leak
        _READ_FOR_INGREDIENTS[tuple(folded)] = told
    return list(told[0]), list(told[1])


def _work_out_ingredients(folded):
    """(the ingredients these folded words name, the ones they rule out).

    Every row about a dish or a recipe asks this about the same line, so the answer is worked
    out once for the words and kept (see _named_ingredients). An alias is only looked at when
    its first word is in the line - a 419-alias table against a six-word line is otherwise
    mostly questions with no answer, and this was 14% of a reply.
    """
    used = [False] * len(folded)
    present = set(folded)
    hits = []
    for parts, name in _ALIASES_BY_LENGTH:
        if parts[0] not in present:
            continue
        span = len(parts)
        for start in range(len(folded) - span + 1):
            if any(used[start:start + span]):
                continue
            if all(folded[start + offset] == parts[offset] for offset in range(span)):
                for offset in range(span):
                    used[start + offset] = True
                hits.append((start, name, span))
                break
    named, negated = [], []
    refused_ends = []
    for place, name, span in sorted(hits):
        if name in named:
            continue
        if _renamed_by_an_event(folded, place):
            continue
        named.append(name)
        before = folded[max(0, place - NEGATION_REACH):place]
        ruled = _refused_before(folded, place) or (
                any(word in NEGATIONS for word in before)
                and not any(word in SOFTENED for word in before))
        if not ruled and _on_a_list_already_ruled_out(folded, place, refused_ends):
            # A negation covers the whole list it starts: "i havent got any potatoes or carrots"
            # rules out both. Read one food at a time the second one is past the three words a
            # negation reaches, so the carrots were kept as food in the kitchen while the
            # potatoes were struck off, and the next "what can i cook tonight" planned carrot
            # soup for somebody who had just said they had no carrots.
            ruled = True
        if ruled:
            negated.append(name)
            refused_ends.append(place + span)
    return named, negated


# The words between two foods that make them one list, so the negation on the first covers the
# second. A word of its own between them is not a list, and neither is a clause break: "no
# potatoes but carrots are fine" still cooks with the carrots.
REFUSAL_JOINERS = frozenset("or and nor either plus also both".split())


def _on_a_list_already_ruled_out(folded, place, refused_ends):
    """True when the food at `place` is joined to one the line has already ruled out."""
    for end in refused_ends:
        between = folded[end:place]
        if between and all(word in REFUSAL_JOINERS for word in between):
            return True
    return False


def diet_exclusions(understood):
    """The pantry foods a stated diet rules out ("i'm vegan" rules out eggs, cheese and meat)."""
    if not isinstance(understood, dict):
        return []
    clean = str(understood.get("clean") or "").lower()
    words = understood.get("words") if isinstance(understood.get("words"), (list, tuple)) else None
    folded = [_fold(word) for word in (words or clean.split())]
    classes = set()
    for cues, ruled in DIETS:
        for cue in cues:
            if " " in cue:
                if cue in clean:
                    classes.update(ruled)
                    break
            elif cue in folded:
                classes.update(ruled)
                break
    if not classes:
        return []
    return [name for name, kinds in FOOD_CLASSES.items() if classes.intersection(kinds)]


# An idea for a food that needs nothing a diet rules out, so a line like "rice and no eggs" still
# gets something to cook: these name only their own food, and a word the line ruled out drops
# them the same way it drops a pantry idea.
WITHOUT = {
    "rice": "Fry the cold rice hard with frozen veg and soy sauce, or cook it in stock with a "
            "handful of chopped herbs.",
    "pasta": "Toss the pasta with olive oil, sliced garlic and a little chilli, and keep back a splash "
             "of the cooking water to loosen it.",
    "potato": "Cut the potatoes into wedges, toss with oil and salt, and roast at 200C (180C fan) for 35 "
              "minutes.",
    "potato_wedges": "",
    "bread": "Toast the bread and rub a cut garlic clove over it, then spoon over chopped tomatoes with "
             "olive oil.",
    "spinach": "Wilt the spinach in a hot pan with a little oil, garlic and a grate of nutmeg, 2 minutes.",
    "cabbage": "Shred the cabbage and fry it hard in oil with a pinch of salt until the edges char, 5 "
               "minutes.",
    "chickpea": "Roast a drained tin of chickpeas at 200C (180C fan) for 25 minutes with oil, salt and paprika.",
    "bean": "Fry a drained tin of beans with garlic, cumin and a tin of tomatoes, and simmer 15 minutes.",
    "lentil": "Simmer the lentils with a tin of tomatoes, cumin and stock for 20 minutes.",
    "tomato": "Halve the tomatoes and roast at 200C (180C fan) for 25 minutes with oil, salt and thyme.",
    "mushroom": "Fry the mushrooms hard in oil until they squeak and brown, then finish with garlic and "
                "parsley.",
    "courgette": "Slice the courgette thick, oil and salt it, and grill 4 minutes a side.",
    "pepper": "Roast the pepper halves at 200C (180C fan) for 25 minutes, then peel and dress with oil.",
    "carrot": "Roast the carrot batons at 200C (180C fan) for 30 minutes with oil, salt and cumin.",
    "onion": "Slice the onions thick and cook slowly in oil for 20 minutes until sweet and brown.",
    "banana": "Slice the banana over porridge, or mash it into a batter and fry small pancakes.",
    "apple": "Stew the apple in slices with a splash of water and cinnamon for 8 minutes.",
    "sweetcorn": "Fry a drained tin of sweetcorn in a hot pan with oil, chilli and lime, 5 minutes.",
    "pea": "Simmer the peas 3 minutes and crush them with oil, salt and mint.",
    "garlic": "Warm sliced garlic slowly in oil and spoon it over anything plain.",
    "lemon": "Squeeze the lemon over greens with oil and salt, or steep the zest in hot water for tea.",
    "oats": "Simmer the oats with water or a dairy-free drink for 5 minutes and top with fruit.",
    "egg": "Boil the eggs 7 minutes, cool them, and eat with salt and toast.",
    "milk": "Warm the milk with a spoon of honey and a pinch of cinnamon.",
    "cheese": "Grate the cheese over hot pasta or potatoes with plenty of black pepper.",
    "yoghurt": "Stir the yoghurt into soup off the heat, or spoon it over fruit.",
    "butter": "Melt the butter into hot potatoes or pasta with salt and pepper.",
    "cream": "Stir the cream into a pan of mushrooms off the heat with salt and pepper.",
    "flour": "Mix the flour with water and a pinch of salt into a batter for pancakes.",
}


WITHOUT.pop("potato_wedges")


def _is_food_list(folded, clean):
    """Whether the line is only foods, so the meal question is there with the words left out."""
    named = False
    for word in folded:
        if not word or word in FILLER or word in _DIET_WORDS or word in NEGATIONS:
            continue
        if word in _INGREDIENT_WORDS:
            # "veg" is the vague half of a list, never the list itself: "im veg" is somebody
            # saying what they eat, not a kitchen to build a dinner from, and it was answered
            # with a tray of roast vegetables instead of an "I'll remember that".
            if _INGREDIENT_WORDS[word] not in _VAGUE_KEYS:
                named = True
            continue
        return False
    return named


def ingredients(understood):
    """The pantry ingredients the line names, in the order it names them."""
    named, negated = _named_ingredients(understood)
    kept = [name for name in named if name not in negated]
    # "coconut milk" is one ingredient, not coconut plus milk: a name that is part of a longer
    # name in the same line ("milk" in "coconut milk") would otherwise get an idea of its own,
    # which is how half a tin of coconut milk was answered with a white sauce.
    kept = [name for name in kept
            if not any(name != other and name in other.split() for other in kept)]
    # A word in front can make it a different food: "bean sprouts" are not the Christmas
    # vegetable, and a stir fry of them does not want a butter-and-lid recipe.
    clean = str((understood or {}).get("clean") or "").lower()
    return [name for name in kept
            if not any(phrase in clean for phrase in NOT_THIS_FOOD.get(name, ()))]


def negated_ingredients(understood):
    """The pantry ingredients the line says it has not got ("but no flour", "without cheese")."""
    named, negated = _named_ingredients(understood)
    return [name for name in negated if name in named]


def _mentions(text, names):
    """Whether a reply names one of these pantry ingredients ("150g flour", "grated cheese")."""
    if not names:
        return False
    words = [_fold(word) for word in str(text or "").lower().split()]
    for word in words:
        name = _INGREDIENT_WORDS.get(word)
        if name is None:
            for ending in ("", "s", "es"):
                name = _INGREDIENT_WORDS.get(_fold(word.rstrip(",.")) + ending)
                if name is not None:
                    break
        if name in names:
            return True
    return False


def cooked_ingredients(understood):
    """The ingredients the line says are already cooked ("leftover roast chicken")."""
    words = understood.get("words") if isinstance(understood, dict) else None
    if not isinstance(words, (list, tuple)):
        words = str((understood or {}).get("clean") or "").split()
    folded = [_fold(word) for word in words]
    ready = []
    for place, word in enumerate(folded):
        name = _INGREDIENT_WORDS.get(word)
        if not name or name in ready:
            continue
        if not any(word in COOKED_WORDS
                   for word in _words_just_before(folded, place, COOKED_REACH)):
            continue
        before = folded[max(0, place - NEGATION_REACH):place]
        if any(word in NEGATIONS for word in before):
            continue
        ready.append(name)
    return ready


_VEG_WORDS = frozenset("vegetarian vegetarians veggie veggies vegan vegans".split())


# Half the table eats no meat, so the one dish cooked for everybody has to be meat free. The
# count has to be next to the word, or "14 of us and my sister is veggie" would read as all 14.
_VEG_GUESTS = re.compile(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|some|half|a few"
                         r"|\d+)\b[^.]{0,40}\bveg(?:gie|gies|an|ans|etarian|etarians)\b")


# "my sister is veggie" says nothing about the person asking: the diet words are about them, so
# the line is not read as a vegetarian's. A count is still a signal ("3 are veggies"), and that
# is what _VEG_GUESTS is for.
_VEG_ELSEWHERE = re.compile(r"\b(?:my|his|her|their|our)\b[^.]{0,30}"
                            r"\b(?:is|are|was|doesn'?t|does not|don'?t|do not|won'?t|will not)\b"
                            r"[^.]{0,30}\bveg")


_SELF_VEG = re.compile(r"\b(?:i'?m|im|i am|we'?re|we are|as a)\b[^.]{0,30}"
                       r"\bveg(?:gie|gies|an|ans|etarian|etarians)\b")


def _veg_dinner(missing, cheap=False):
    """Two veggie dinners, unless one asks for a food the eater has ruled out.

    Its dhal comes "with rice or bread", and a coeliac reading that has just been told the list
    is gluten free is the one line that must not mention bread. What the two cost is said only
    when the line asked about money.
    """
    if _mentions(_VEG_DINNER, missing):
        return _any_meal(set(missing))
    return _VEG_DINNER + (_VEG_DINNER_CHEAP if cheap else "")


def _diet(folded, clean):
    """'vegan', 'vegetarian' or '': what the line says it, or its guests, can eat."""
    if _VEG_ELSEWHERE.search(clean) and not _SELF_VEG.search(clean):
        return ""
    if any(word in ("vegan", "vegans") for word in folded):
        return "vegan"
    if (any(word in _VEG_WORDS for word in folded)
            or any(phrase in clean for phrase in _VEG_PHRASES)
            or _VEG_GUESTS.search(clean)):
        return "vegetarian"
    return ""


def _diet_from_turns(earlier):
    """The diet the eater said a turn or two ago, or "" when they said none."""
    for said in reversed(earlier):
        found = _diet(re.findall(r"[a-z0-9']+", said.lower()), said.lower())
        if found:
            return found
    return ""


# The cues a person's own refusal is said with, as against a bare "no" or "without" in front of
# a food, which the cupboard can be short of as easily as somebody can refuse it.
_BARE_NO_CUES = frozenset(("no", "none", "without", "not", "nothing"))


# The words that follow a food and make it a shortage rather than a refusal: "no flour left",
# "no cheese in the house", "no eggs at all today" (not "no eggs for him").
SHORTAGE_AFTER = frozenset(("left", "house", "home", "cupboard", "fridge", "freezer", "gone",
                            "shop", "shops", "supermarket", "kitchen", "larder", "pantry"))


def _refused_foods(text, families=False):
    """The foods the line says somebody will not eat, from the kitchen's own word list.

    AVOIDED above reads the families that make people ill - meat, dairy, nuts, gluten - and a
    bare "no"/"without" in front of them. The rest of the kitchen is named the same way and was
    not read at all: "my wife hates mushrooms, any ideas for dinner" got mushrooms on toast, and
    "my son wont eat onions what can i cook" got the toddler feeding answer. A refused food is a
    limit on the dinner in exactly the words of an allergy, so the meal picker has to see it.

    Only a cue near the food counts, and only across the little words that join them ("wont eat
    onions", "no more of those tomatoes", "no cheese at all"). "i dont know what to do with
    chicken" is not a ban: "know what to do with" is not one of them.
    """
    said = _fold(str(text or ""))
    # "i'm tired of pasta" and "i'm sick of rice" are refusals, but bare "tired" and "sick" are
    # not: "i am tired, is chicken ok for dinner" is a person with chicken in the fridge. The
    # phrase is what refuses, so it is folded into the plain "no" and the two bare words are not
    # cues at all.
    said = re.sub(r"\b(?:tired|sick|bored)\s+of\b|\bfed\s+up\s+(?:of|with)\b", " no ", said)
    refused = set()
    words = re.findall(r"[a-z']+", said)
    # The refusal is read forwards from the cue, not backwards from each food, so that every food
    # the cue governs is refused: "she wont eat fish or meat" refused the fish and went on to
    # offer chicken thighs, which is the food the same line had just ruled out. "or", "and" and
    # "nor" are what join two foods under one refusal, and the scan stops at the first word that
    # is neither a food, a joiner, nor one of the little words between ("wont eat any of the
    # onions").
    for start, word in enumerate(words):
        if word not in _REFUSAL_CUES:
            continue
        index = start + 1
        while index < len(words):
            here = words[index]
            # The pantry files every name with its plural undone, so the line has to be read the
            # same way: "my husband doesnt eat tomatoes what can i cook" kept its "tomatoes" and
            # the refusal was not seen, while the same words with the ask in front had been
            # rewritten to "tomato" by the reading engine and worked. `_fold` is the kitchen's
            # own plural rule, so potatoes, chillies and berries are read from either side.
            name = _INGREDIENT_WORDS.get(here) or _INGREDIENT_WORDS.get(_fold(here))
            if name:
                # "no flour left" and "no cheese in the house" say the kitchen has none of it,
                # which is the swap table's question and not a person refusing to eat it: the
                # food is followed by the word that makes it a shortage.
                after = words[index + 1:index + 3]
                if word in _BARE_NO_CUES and any(part in SHORTAGE_AFTER for part in after):
                    break
                refused.add(name)
                index += 1
                continue
            if here in FAMILIES:
                # A family name ("meat", "dairy", "gluten") is a diet card's question and not one
                # food's, so it is normally stepped over - but the food after it is still read
                # ("fish or meat"). A caller that has to honour the family, such as the swap
                # table checking that its substitute is not the food just ruled out, asks for it.
                if families:
                    refused.update(DAIRY if here == "lactose" else FAMILIES[here])
                index += 1
                continue
            if here in _REFUSAL_FILLER or here in _REFUSAL_JOINERS:
                index += 1
                continue
            break
    return refused


# What a line that asks what to cook says, once the word "eat" has been taken out of it: "my son
# wont eat onions" is the refusal and its substitute, not a dinner asked for, and "eat" is in
# MEAL_CUES for the lines that do ask ("what can i eat tonight").
DINNER_ASK_WORDS = frozenset("""
make makes making cook cooking meal meals dinner tea lunch supper snack idea ideas recipe recipes
something anything
""".split())


# The foods whose absence is never a limit on a dinner: nobody's dinner was going to have flour
# in it, so "no flour left" is the baking question and the no-flour loaf already says what to bake
# instead. Without this the line, which the store rewrites to "what can i make without flour",
# was answered with a potato hash that the flour had nothing to do with.
NOT_A_DINNER_LIMIT = frozenset(("flour",))


# The meals and the pans that make "with no X" a dinner question rather than a substitute one.
DINNER_NAMED = frozenset("""
dinner dinners tea supper lunch meal meals main cook cooking cooked roast fry fried bake baked
""".split())


# The meals with an idea card of their own, which already leave out what the person cannot eat:
# "i dont eat cheese, any ideas for a quick lunch" is the packed-lunch answer's line, and a
# single dinner dish is a narrower answer to it.
LUNCH_AND_BREAKFAST = frozenset("lunch lunches breakfast brunch lunchbox lunchboxes".split())


_STAND_IN_USE = re.compile(
    r"what (?:can|could|do|should) i use(?!\s+(?:it|them|that|this|those|these|leftovers?"
    r"|the rest)\b)")


# What a refusal is said with: a plain "no mushrooms", a person who will not eat them, and the
# words somebody uses when they are bored of a food.
_REFUSAL_CUES = frozenset((
    "no", "not", "without", "never", "hate", "hates", "hated", "dislike", "dislikes",
    "refuse", "refuses", "refused", "wont", "won't", "doesnt", "doesn't", "dont", "don't",
    "cant", "can't", "cannot", "avoid", "avoids", "avoids", "off",
    "fussy", "banned", "allergic", "intolerant", "skip", "skipping"))


# "fish or meat", "chicken and bacon": one refusal governs both foods.
_REFUSAL_JOINERS = frozenset(("or", "and", "nor", "plus", "also"))


# The words that may sit between the cue and the food and leave it refused.
_REFUSAL_FILLER = frozenset((
    "eat", "eats", "eating", "have", "has", "having", "use", "uses", "want", "wants",
    # "she doesnt like nuts" and "he does not want any fish" put the feeling word between the
    # refusal and the food, and the reader stopped at it: the line was answered with the nuts
    # card rather than a dinner with none in it.
    "like", "likes", "liked", "love", "loves", "loved", "care", "cares", "keen",
    "the", "any", "more", "much", "really", "at", "all", "a", "an", "this", "that",
    "these", "those", "it", "them", "some", "my", "his", "her", "their", "our", "of",
    "food", "foods", "stuff", "things", "thing", "dish", "dishes", "kind", "sort",
    "me", "us", "him", "her", "to", "for", "with", "is", "are", "was", "were"))


def _dishes_without(banned):
    """The whole meals that have none of the foods in `banned`, the biggest first."""
    banned = {str(name) for name in banned}
    found = []
    for dish in DISHES:
        uses = tuple(dish.get("uses") or ())
        if not uses or any(name in banned for name in uses):
            continue
        if _mentions(dish.get("text") or "", banned):
            continue
        found.append(dish)
    return found


def _best_dish(found, ready=(), missing=(), avoid=(), diet=""):
    """The dish using the most of the ingredients found, so pairs beat single-ingredient ones.

    A dish is skipped when it would cook again something the line already has cooked, unless
    the dish names that ingredient in "cooked", and when its text is in avoid: a follow-up
    about the same food gets the next dish that fits rather than the same words again. With a
    diet, a dish with meat in it is skipped: the line said what it does not eat, so an idea it
    cannot cook is no answer.
    """
    best, best_uses = None, 1        # a dish needs two of them to count as the answer here
    trimmed = None
    for candidate in DISHES:
        uses = candidate["uses"]
        if diet and any(name in MEAT for name in uses):
            continue
        if not all(name in found for name in uses):
            continue
        if candidate.get("text") in avoid:
            continue
        if missing and _mentions(candidate["text"], missing):
            # The dish's own words ask for a food the line has not got. When that food is one of
            # its ingredients it cannot be made at all; when it is only the trimmings (the frittata
            # is spinach and eggs, and offers "cheese on top") the same dish is still the answer
            # with that sentence left off, and one dish with one time keeps the clock follow-up
            # working after it.
            if any(name in uses for name in missing):
                continue
            cut = _without_the_trimmings(candidate["text"], missing)
            if cut and trimmed is None and len(uses) > 1:
                trimmed = dict(candidate, text=cut,
                               without=tuple(sorted(name for name in missing
                                                    if _mentions(candidate["text"], (name,)))))
            continue
        # The same dish can be worded twice ("leek and potato soup" as a dish and as an idea for
        # leeks), so a dish whose own name is in what was just said is left out too.
        if avoid and all(word in _fold(" ".join(avoid)) for word in candidate["id"].split("-")):
            continue
        if any(name in missing for name in uses):
            continue
        keeps = candidate.get("cooked", ())
        if any(name in ready and name not in keeps for name in uses):
            continue
        if len(uses) > best_uses:
            best, best_uses = candidate, len(uses)
    return best or trimmed


SENTENCE = re.compile(r"(?<=[.!?])\s+")


def _served_without(dish):
    """A dish said as itself with the trimmings left off ("A frittata, no cheese: whisk ...")."""
    left_out = " and ".join(dish.get("without") or ())
    text = str(dish.get("text") or "")
    name, colon, method = text.partition(": ")
    if colon and name and not _mentions(name, dish.get("without") or ()):
        return f"{name}, no {left_out}: {method}"
    return f"Without the {left_out}: " + (text[:1].lower() + text[1:] if text else text)


def _without_the_trimmings(text, missing):
    """The same dish with the sentences that offer a food the line has not got left off.

    A dish's own words offer more than its ingredients: "cheese on top is worth it" after the
    method, "serve with crusty bread" at the end. The offer is a sentence at the end, so it comes
    off whole and the method, with its one time, is what is left. A dish whose first sentence asks
    for the food is not this dish at all, and comes back empty for the caller to skip.
    """
    parts = [part.strip() for part in SENTENCE.split(str(text or "").strip()) if part.strip()]
    while len(parts) > 1 and _mentions(parts[-1], missing):
        parts.pop()
    if not parts or _mentions(parts[0], missing):
        return ""
    return " ".join(parts)


def dish(understood, avoid=(), memory=None):
    """The meal that uses most of the ingredients a line names, or None.

    Only for a line naming two or more pantry things: one ingredient on its own is covered by
    the entries, and those say more about it than one dish can. avoid holds what was already
    said, so a follow-up about the same food is not answered with the same words again.
    memory, when given, is read for what the eater ruled out a turn ago, so a dish is not
    cooked for somebody who said "I'm veggie" before naming the mince ("I'm veggie" then
    "mince and potatoes").
    """
    # "whats a good recipe for banana bread" names two foods, and a bread-and-banana dish is not
    # what it asked for: a bake has a recipe of its own.
    if _names_a_bake(understood):
        return None
    return meal(understood, dishes_only=True, avoid=avoid, memory=memory)


# "What should I eat when I'm ill" is a food question with a plain answer, and nothing in the
# knowledge base had it: the line fell through to the search hedge while a stove-and-saucepan
# answer was the thing the person wanted. Registered here because the reply reads the illness
# phrases, and the red flags stay with the health module.
ENTRIES.append(entry(
    "eat-when-ill", (SICK_PHRASES, SICK_EAT_WORDS), _eat_when_ill, bias=1,
    avoid=("blood", "chest pain", "cant breathe", "can't breathe", "short of breath",
           "pregnant", "weeks", "baby", "babies", "toddler", "my son", "my daughter",
           "my mum", "my dad", "my husband", "my wife", "my partner", "child", "children",
           "diarrhoea", "diarrhea", "three days", "four days", "a week", "doctor",
           "hospital", "medicine", "antibiotic", "tests", "why do i", "why am i",
           # a keeping question, not a somebody-who-is-ill question
           "cold rice", "cold chicken", "cold pizza", "left out", "gone off", "ok to eat",
           "safe to eat", "still ok", "is it ok",
           # and a mouth line is a dental one: "my teeth hurt when i have a cold drink" was
           # answered with what to eat when you are ill
           # "does tea with honey help a cold" asks whether a remedy works, not what to eat:
           # the honey-and-cough row names the remedy and answers it, so the does-it-help
           # shapes stand this row down.
           "help a cold", "help my cold", "help the cold", "help a cough", "help my cough",
           "help a sore throat", "help my throat", "does honey", "will honey", "honey help",
           "honey and lemon", "lemon and honey", "honey in warm water",
           #
           # An animal that is being sick is not a person who is: "my cat wont eat and is being
           # sick" and "my rabbit is off her food and being sick" were both told to eat toast
           # and crackers and to watch their urine output. The pet rows answer the animal, and
           # this row stands down for every animal the deck names, whether or not the line
           # remembers to say "my".
           "my cat", "my dog", "my puppy", "my kitten", "my rabbit", "my hamster",
           "my guinea pig", "my parrot", "my budgie", "my tortoise", "my pet", "my puppy",
           "cat", "dog", "puppy", "kitten", "rabbit", "hamster", "guinea pig", "parrot",
           "budgie", "tortoise", "the cat", "the dog", "the puppy", "the kitten",
           ) + TOOTH_OR_GUM))


# "is a potato a vegetable" and "are bananas berries" name food, but they ask what the
# food is; the pantry would read the words as an ingredient list and answer with a recipe.
# The category has to end the question (or be joined by "or") so "what is a good vegetable
# for roasting" is still a cooking question.
_WHAT_IS_IT = re.compile(
    r"\b(?:is|are)\s+(?:a|an)?\s*[a-z]+\s+(?:a|an)?\s*"
    r"(?:fruit|vegetable|berry|berries|tuber|root|grain|pulse)s?\s*(?:\?|$|or\b|,|\.)")


_ANY_FOOD_TEXT = None


def _any_food_text():
    """Every name the pantry answers to, longest first, as one alternation for the "or" test."""
    global _ANY_FOOD_TEXT
    if _ANY_FOOD_TEXT is None:
        names = sorted({_fold(str(alias)) for aliases, _idea in PANTRY.values()
                        for alias in aliases}, key=len, reverse=True)
        _ANY_FOOD_TEXT = "|".join(re.escape(name) for name in names if name)
    return _ANY_FOOD_TEXT


def _a_choice_of_foods(clean):
    """True when the line puts two foods on either side of an "or" and asks which to use."""
    low = _fold(str(clean or ""))
    if " or " not in low:
        return False
    if not any(word in low for word in _CHOICE_WORDS):
        return False
    foods = _any_food_text()
    if not foods:
        return False
    other = foods + "|" + _COOKING_MEDIUM
    return bool(re.search(r"\b(?:%s)\s+or\s+(?:%s)\b" % (foods, other), low))


def meal(understood, dishes_only=False, text=None, banned=None, diet=None, memory=None,
         avoid=(), pointed_back=False):
    """A meal idea for the ingredients a line names, or None when it names none it knows.

    understood: memory["understood"]. The line has to be a food question ("what can I make
    with...", "any dinner ideas with...", "use up the..."), read as the cooking topic, and it
    has to name at least one ingredient from PANTRY. A dish that uses more of the named
    ingredients wins, so eggs and spinach get the frittata rather than an omelette; without
    one, the line gets a quick idea for each of the first two ingredients it names.

    banned: the foods the eater has ruled out, this turn or in the turns before it. A dish or
    an idea that needs one of them is no answer ("I'm dairy free" then "what can I cook with
    the cheese" must not get cheese on toast). Left out, the line's own words are read for
    them, so "my partner doesnt eat cheese" never gets a cheese dish; a caller that also reads
    the turns before this one passes a wider set.

    diet: "vegetarian" or "vegan" when the eater said so a turn ago ("I'm veggie and skint this
    week" then "any ideas for dinner"). Left out, the line's own words decide.

    memory: the conversation, when the caller has it. What the person said a turn or two ago
    counts here too, so a diet or a food they ruled out is not forgotten the moment the next
    line names that food ("my partner doesnt eat cheese" then "potatoes and cheese").

    """
    if _names_a_bake(understood):
        return None
    if not isinstance(understood, dict):
        return None
    if _says_it_has_gone_off(understood.get("clean")):
        # A food that smells or has gone off is a sniff test, not an ingredient: "my salmon
        # smells is it still alright" and "my leftovers have gone slimy" were both answered with
        # a recipe here, because naming a food is all this table needs to pick a dish.
        return None
    # The line names a dish this kitchen has a recipe for: the dish is the subject and the table
    # below answers foods. "spaghetti bolognese recipe" is the bolognese method, not any pasta
    # dish, and "should i do a spag bol tonight" is that dish. A use-up line keeps the table: a
    # pan of last night's bolognese is a food in the fridge, not a dish to go and make.
    if names_a_dish(understood):
        _said = str(understood.get("clean") or "").lower()
        if not any(word in _said for word in _USE_UP_WORDS):
            return None
    # A line that is choosing a kind of ingredient is not asking what to make with it: "what
    # flour should i use for bread" names two pantry foods and was answered with a pancake
    # recipe. `picking` answers those, and this table stands down.
    from ..knowledge import picking
    if picking.choosing(understood):
        return None
    shared = " ".join([str(understood.get("clean") or "")]
                      + [str(word) for word in (understood.get("words") or ())])
    # "can rabbits eat lettuce" names two foods and was answered with a braise and a salad: the
    # animal was read as the dinner. A question about what an animal may eat is the pets table's.
    if _feeding_ask(shared):
        return None
    if _pet_not_dinner(shared) or _reads_as_a_pet(shared):
        # A pet is not a joint. When the line asks what to cook it still gets an answer, one that
        # says which reading it took; a care question gets None and keeps its own answer.
        return _pet_or_meat(shared)
    if _a_brew_not_a_dinner(shared):
        # A milk question about a cup of tea names two pantry foods (oats and milk) and was
        # answered with porridge: the brew row in cooking_entries.py is the answer, and no
        # dish this table holds is one.
        return None
    if _a_plant_not_a_dinner(shared):
        # A tree, a bush or a plant is the garden's question, not the pantry's: "i bought a lemon
        # tree" was answered with lemon chicken. The food the line names is still the subject, so
        # a line that asks what to cook keeps its idea.
        return None
    if understood.get("kind") in ("empty", "greeting", "thanks"):
        return None
    words = understood.get("words") or ()
    folded = [_fold(word) for word in words]
    earlier = _recent_user_turns(memory)
    clean_now = str(understood.get("clean") or "").lower()
    whole = " ".join([clean_now] + [str(said).lower() for said in earlier])
    crowd = _crowd_ask(clean_now)
    if (not crowd and earlier
            and any(word in clean_now for word in _CROWD_FOOD + _CROWD_VERBS)):
        # The table is set a turn or two back: "im doing something for my wifes 50th", "about
        # twenty people i think", "what food would be easy". The count is in the conversation,
        # and the question is still the crowd dinner rather than a search hedge.
        crowd = _crowd_ask(whole)
    if banned is None:
        banned = frozenset(_excluded(" ".join(
            [str(understood.get("clean") or ""), " ".join(str(word) for word in words)]
            + earlier)))
    # A food somebody at the table will not eat is a limit on the dinner the same way an
    # allergy or a bare "no" is, and the kitchen's own word list is what reads it: "my wife
    # hates mushrooms, any ideas for dinner" was answered with mushrooms on toast.
    refused = _refused_foods(" ".join([str(understood.get("clean") or "")] + earlier))
    if refused - set(banned):
        banned = frozenset(banned | refused)
    if text is not None:
        # A follow-up read with the topic put back in ("can you remember that?", "what about a
        # 3kg one") names an ingredient only through the context, and the person did not ask
        # what to cook. The pantry answers the line they typed, so it has to name something.
        lower = str(text).lower()
        typed = str(understood.get("text") or "").lower()
        repaired = str(understood.get("plain") or "").lower()
        if repaired and repaired != typed and lower == typed:
            # The caller hands over the line as it was typed, and a food word typed with a
            # slip ("a chickn recipe") is not a word this table knows: the engine has already
            # repaired it, and the repaired line is the one that names the food, so the check
            # below reads it. Only when the text is that same typed line, because a caller
            # that put the context into it is asking about the context, not about a repair.
            lower = repaired
        own = [_fold(word) for word in lower.split()]
        if (not any(word in _INGREDIENT_WORDS for word in own)
                # "theres nothing in for tea" says the kitchen is empty in the words of a
                # line that names no food, which is the line the empty-kitchen answer is
                # for: the pantry used to turn it down and the ack took the turn.
                and not any(phrase in lower for phrase in EMPTY_PHRASES)
                and not any(phrase in lower for phrase in EMPTY_ASK_PHRASES)
                # "what can i do with what's left" names the food in the turn before this one,
                # and the leftover idea answers the line they typed. The use-up ways of asking
                # count too: "what can i do with leftover curry" names a food this table knows
                # by its phrase rather than by a single word, so no word in it is a pantry word,
                # and the row that answers "how do i use up leftover curry" stood down only
                # because the question opened differently.
                and not any(phrase in lower for phrase in LEFT_POINTER + USE_UP_ASKS)
                # ...unless the line brings something else to work with: a table to feed.
                and not crowd):
            return None
    asks = set(understood.get("asks") or ())
    # "how do i cook for a crowd" is a how-to in form and a dinner question in substance: at a
    # table of eight the question is what to cook, not which pan to use. "how do i use up the
    # spinach" is the same shape one size smaller: the only method word is the opening "how"
    # and the line says use-up, so the food is the question.
    if (asks & NOT_MEAL_ASKS and not _crowd_ask(understood.get("clean") or "")
            and not (asks & NOT_MEAL_ASKS == {"how"}
                     and any(phrase in str(understood.get("clean") or "").lower()
                             for phrase in USE_UP_ASKS))):
        return None
    if any(word in PROBLEM_WORDS for word in folded):
        return None
    if any(word in SUBSTITUTE_WORDS for word in folded):
        return None
    clean = str(understood.get("clean") or "").lower()
    if _WHAT_IS_IT.search(clean):
        return None
    if _VEG_GUESTS.search(clean):
        # Somebody else at the table eats no meat ("theres 14 of us and 3 are veggies"), so the
        # one dish cooked for everybody has to be meat free. Only this line counts: a diet
        # stated for a guest is not the asker's own, which is what _diet is for.
        banned = frozenset(banned | MEAT)
    # "Can I use milk instead of cream" names two ingredients, but it is a question about one of
    # them, and a dish built from both answered something else.
    if any(phrase in clean for phrase in SUBSTITUTE_PHRASES):
        return None
    if any(phrase in clean for phrase in PROBLEM_PHRASES):
        return None
    # A line that says what someone will *only* eat is a fussy-eater question, not an
    # ingredients question, whatever food it names.
    if any(phrase in clean for phrase in RESTRICTED_EATING):
        # A line that says somebody will not eat a food is the fussy-eater worry when it is about
        # the eating ("my four year old will only eat bread and cheese"), and a dinner to pick when
        # it is a limit on the dinner and the line asks for one: "my son wont eat onions what can i
        # cook" got the toddler feeding answer, which is about getting a new food tried rather than
        # about the onion in the dinner. The refusal has to name a food and the line has to ask
        # for something to cook for this to be a dinner question.
        if not (any(word in MEAL_CUES for word in folded) and _refused_foods(clean)):
            return None
    if any(phrase in clean for phrase in ILLNESS_PHRASES):
        return None
    # A food named as the raw material for an activity is not dinner: "easter egg ideas for
    # toddlers" and "what can i dye with beetroot" want something to make *with* it, and a plate
    # of scrambled eggs answers the wrong question.
    if any(phrase in clean for phrase in ACTIVITY_PHRASES):
        return None
    if any(phrase in clean for phrase in MAKING_IT_YOURSELF_PHRASES):
        return None                      # the making question, not what to cook with it
    # "there is no food in the house" is the kitchen question asked the other way round. It is
    # checked before the topic, because that line reads as a home question, and the phrases that
    # name food are narrow enough to keep a wardrobe or a pet out of it.
    empty_kitchen = any(phrase in clean for phrase in EMPTY_PHRASES)
    if not empty_kitchen and any(phrase in clean for phrase in EMPTY_ASK_PHRASES):
        # the vague forms need a meal word beside them: see MEAL_WORDS
        empty_kitchen = any(word in MEAL_WORDS for word in folded)
    if empty_kitchen and not any(word in PET_WORDS for word in folded):
        return EMPTY_KITCHEN
    asked = (any(word in MEAL_CUES for word in folded)
             or any(phrase in clean for phrase in MEAL_PHRASES)
             # "what can i feed 20 people" and "what food for a table of twenty" name the table
             # and the food and no meal word at all, and they are the same question
             or crowd)
    bought = any(phrase in clean for phrase in BOUGHT_PHRASES)
    # "i bought a chicken" is its own way of asking what to do with it.
    asked = asked or bought
    asks_what_to_cook = (any(word in MEAL_CUES for word in folded)
                         or any(phrase in clean for phrase in MEAL_ASK_PHRASES))
    named = ingredients(understood)
    # The reading can put a food line in another topic: "half a cabbage" is a fraction before it
    # is a vegetable, and "i bought a whole chicken" is a purchase. When the line names something
    # in the kitchen and asks what to do with it, that is a meal question whatever the topic says.
    if (understood.get("topic") not in ("cooking", "food-and-drink")
            and not any(word in FOOD_CUES for word in folded)
            and not (named and (asks_what_to_cook or bought))
            # "what can i feed 20 people" reads as no topic at all and names no food cue word,
            # and the table is the subject: the count is what makes it a cooking question.
            and not crowd
            and not _is_food_list(folded, clean)):
        # "half a cabbage and some mince" reads as a maths line because of the "half", but a line
        # that is only foods is still the kitchen question.
        return None
    if not (asked or _is_food_list(folded, clean)):
        return None
    # "some veg" is not an ingredient, it is the vague way of saying there are vegetables in:
    # counting it as one half of a pair answered "mince and some veg" with two whole recipes.
    found = [name for name in named if name not in _VAGUE_KEYS
             and name not in VAGUE] or named
    missing = list(negated_ingredients(understood))
    # The foods the line itself turns down, before a diet adds the ones it never named. Only
    # these are a limit the person said out loud: a denied condition ("im not coeliac") reads
    # as the foods it would take away by `diet_exclusions`, and it does not take any away.
    said_no = list(missing)
    # A diet is a ruled-out food that was never named: vegan takes the eggs and the cheese out,
    # so the line gets something built on what is left rather than a dish it cannot eat.
    for name in diet_exclusions(understood):
        if name in found:
            found = [other for other in found if other != name]
        if name not in missing:
            missing.append(name)
    if banned:
        # A food ruled out this turn, or a turn or two ago, is no more use than one they have
        # not got: the idea that needs it is dropped the same way.
        refused_here = [name for name in found
                        if name in banned or any(part in banned for part in name.split())]
        missing.extend(refused_here)
        # A food nobody at the table will eat is not something to cook with either: the line
        # named it to rule it out. Left in `found` it counted as the one ingredient a line has
        # to ask what to cook with, and the dinner question it really is was passed on.
        found = [name for name in found if name not in refused_here]
    diet = diet or _diet(folded, clean) or _diet_from_turns(earlier)
    if not found:
        if any(phrase in clean for phrase in EMPTY_ASK_PHRASES):
            return EMPTY_KITCHEN
        # A table of people with no food named still has an answer: one big oven dish. "im having
        # 12 people over for dinner" and "4 people coming for dinner what should i cook" name no
        # ingredient, and "Got it." is not an answer to either.
        if crowd:
            return _crowd_meal(banned, _occasion(whole), _crowd(whole))
        # "what can i do with what's left" names no food: the food is the one the turns before
        # this one put on the table, and it is already cooked, so the leftover idea is the answer.
        if earlier and any(phrase in clean for phrase in LEFT_POINTER):
            for said in reversed(earlier):
                for name in ingredients({"words": str(said).lower().split(),
                                         "clean": str(said).lower()}):
                    if name in LEFTOVER_IDEAS:
                        return LEFTOVER_IDEAS[name]
        if diet:
            # "im vegetarian and skint, what should i make for dinner" names nothing in the
            # kitchen, so there is no dish to fit; the useful answer is a cheap one that fits
            # what they eat, not a shrug. A table of guests on top of that gets one big dish.
            whole = " ".join([clean] + [said.lower() for said in earlier])
            if _crowd(whole) >= 6 or _occasion(whole):
                return _crowd_meal(banned, _occasion(whole), _crowd(whole))
            return _veg_dinner(set(banned) | set(missing),
                              any(word in CHEAP_PLAN_WORDS for word in _plain_words(whole)))
        # "dinner without potatoes", "dinner with no potatoes please", "no mushrooms for dinner
        # please": the only food the line names is the one it leaves out, so there is nothing to
        # build a dish from and the table passed - a line that plainly asks for a dinner was met
        # with "I'm listening, say more if it helps". A meal word and a food ruled out, with no
        # other food named, is a request for a dinner that leaves that food out, and the default
        # list already knows what to do with what was ruled out. A line about the meal that
        # happened ("we had dinner with no potatoes") is news, and news is not a request.
        if _refused_foods(clean) and banned:
            # Somebody will not eat a food and the line names nothing else to cook with, so the
            # answer is a dinner that has none of it in rather than a shrug: "my son wont eat
            # onions what can i cook" used to get the toddler feeding answer, and "my wife
            # hates mushrooms, any ideas for dinner" the mushrooms on toast she just refused.
            # Only a food *this turn* rules out, or somebody who will not eat one: an allergy or
            # a diet the store already holds is a different card's question ("im coeliac" then
            # "what can i cook" is the gluten-free list, and a single dish answers less of it).
            for dish in _dishes_without(banned):
                if dish.get("text") and dish["text"] not in avoid:
                    return dish["text"]
        if said_no and any(word in MEAL_WORDS for word in folded) \
                and not _reads_as_news(understood, clean):
            return _any_meal(set(banned) | set(said_no))
        return None
    no_meat = bool(diet) or bool(MEAT & set(banned))
    leftover = _leftover(folded, clean)
    if (len(found) == 1
            and not pointed_back
            and not bought
            and not _is_food_list(folded, clean)
            and not any(phrase in clean for phrase in MEAL_PHRASES)
            and not leftover
            and not (no_meat and any(name in MEAT for name in found))):
        # One ingredient with no "what can I do with it" is a question about that ingredient
        # itself ("what's the best way to cook rice"), which the entries answer or honestly pass.
        # Meat and a diet that eats none of it is the exception: what to use instead is the answer.
        # A leftover is the other exception: it is already cooked, and the leftover idea is the
        # only answer that starts from that ("what can i make with leftover roast chicken").
        return None
    swap = ""
    if no_meat:
        # They have meat in and eat none of it, or somebody at the table does not: say what to put
        # in its place, then cook with the rest of what they named rather than sending a recipe
        # they will not make.
        left = [name for name in found if name in MEAT]
        if left:
            meat = left[0]
            instead = MEAT_SWAPS.get(meat, "chickpeas")
            swap = f"{instead[0].upper() + instead[1:]} do the same job in most dishes. "
            # The idea given has to be for what was named as the swap, or the two sentences
            # disagree ("lentils or butter beans..." then a chickpea recipe).
            picked = []
            for word in re.findall(r"[a-z]+", instead):
                name = _INGREDIENT_WORDS.get(_fold(word))
                if name and name not in banned:
                    picked.append(name)
                    break
            # The swap leads, but the rest of the line still counts: "chicken and rice" wants a
            # dish built from the chickpeas and the rice, not from the chickpeas alone.
            found = (picked or ["chickpea"]) + [name for name in found if name not in MEAT]
    best = _best_dish(found, cooked_ingredients(understood), missing, avoid, diet)
    if best is not None:
        if best.get("without"):
            # The same dish, offered without the trimmings the line has not got. It is said as that
            # and not as the dish again, or the second answer reads as the first one repeated.
            return swap + _served_without(best)
        return swap + best["text"]
    if dishes_only:
        return None
    # A leftover is not always answered by the pantry's idea for the food. "Roast beetroot whole
    # and unpeeled at 200C for an hour" is how to cook a beetroot from raw, and the one in the
    # fridge is already cooked and needs a use, not an hour in the oven; the same for "Quinoa:
    # rinse it, simmer 15 minutes". Where the idea names a dish it is a use and stays the answer
    # ("Leek and potato soup", "A 15-minute tomato sauce"), which is what the dish words decide.
    from ..knowledge import meals
    if (any(word in LEFTOVER_WORDS for word in folded)
            or any(phrase in clean for phrase in LEFTOVER_PHRASES)):
        for name in found:
            row = PANTRY.get(name)
            idea = row[1] if row else ""
            if not idea or _mentions(idea, missing) or idea in avoid:
                continue
            if meals.idea_is_a_dish(idea):
                continue
            # Their own word for it, so a plural stays plural in "Leftover parsnips: ...".
            said_name = name
            for word in re.findall(r"[a-z]+", clean):
                if _fold(word) == _fold(name) or _fold(word) == name:
                    said_name = word
                    break
            use = meals.use_it_up(said_name)
            if use:
                return use
    if not swap and (any(word in LEFTOVER_WORDS for word in folded)
                     or any(phrase in clean for phrase in LEFTOVER_PHRASES)):
        for name in found:
            if name in LEFTOVER_IDEAS and LEFTOVER_IDEAS[name] not in avoid \
                    and not _mentions(LEFTOVER_IDEAS[name], missing):
                if name == "milk" and _mentions(clean, PLANT_MILKS):
                    continue  # coconut, oat, soy and almond milk have their own ideas
                return LEFTOVER_IDEAS[name]
    # An idea that asks for something the line has not got is no answer ("butter and eggs but no
    # flour" must not get shortbread), so it is dropped rather than sent.
    # A line that names two foods and asks to choose between them ("butter or oil", "chicken or
    # lamb") is a pick, and one idea for each is two answers to a question with one: "should i
    # cook onions in butter or oil" got shortbread and onion soup. The pick is answered by the
    # row that knows the pair, and this table passes.
    if _a_choice_of_foods(clean):
        return None
    ideas = [PANTRY[name][1] for name in found[:2]
             if not _mentions(PANTRY[name][1], missing) and PANTRY[name][1] not in avoid]
    if not ideas:
        # Nothing left the line can eat: an idea for what it does have beats an honest shrug,
        # as long as that idea asks for nothing the line ruled out.
        ideas = [WITHOUT[name] for name in found[:2]
                 if name in WITHOUT and not _mentions(WITHOUT[name], missing)
                 and WITHOUT[name] not in avoid]
    said = " ".join(ideas) if ideas else None
    # A follow-up about the same food is not answered with the words just given ("broccoli and
    # cheese" then "what can I make with them" is not the same two ideas a second time).
    if said is not None and said in avoid:
        return None
    return said


def _meal_texts():
    """Every whole-meal answer this table can give, so a follow-up can tell one from an entry."""
    texts = [dish["text"] for dish in DISHES if dish.get("text")]
    for name in PANTRY:
        texts.extend([PANTRY[name][1], LEFTOVER_IDEAS.get(name, ""), WITHOUT.get(name, "")])
    texts.extend([EMPTY_KITCHEN, *EMPTY_ASK_PHRASES])
    return frozenset(text.strip() for text in texts if text)


_MEAL_TEXTS = _meal_texts()


# The method of each, after the dish's name: a dish served without the trimmings it offered says
# its own method, cut short, under a name of its own ("A frittata, no cheese: whisk 6 eggs ...").
_MEAL_METHODS = tuple(text.partition(": ")[2] for text in _MEAL_TEXTS if ": " in text)


_TIMING = re.compile(
    r"\b(?:%s)(?:\s*(?:to|or|-|and a half)\s*(?:%s))?\s*(?:minutes?|mins?|hours?|hrs?)\b"
    % (_NUMBER_WORD, _NUMBER_WORD), re.I)


# A timing follow-up points back at the answer ("how long does that take", "how long for it").
_BACK_REFERENCE = frozenset("""
that it this those these there them one dish recipe meal dinner supper thing
""".split())


_WORD = re.compile(r"[a-z']+")


# "How long does that keep?" points back at the dish just as "how long does that take" does, but
# the answer is a keeping fact, not the cooking time. These are the words that make the question
# a keeping one; the cooking senses ("how long do i keep it in the oven") are turned down below.
_KEEP_WORDS = frozenset("""
keep keeps keeping kept store stores stored storing fridge freezer freeze frozen last lasts
lasting leftover leftovers
""".split())


# How long a thing keeps is measured in days and weeks as often as in a cooking time, so the
# sentence that answers it is the one with either figure in it.
_KEEP_TIME = re.compile(
    r"%s|\b(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s*"
    r"(?:days?|weeks?|months?|years?)\b" % _TIMING.pattern, re.I)


# The ask a keeping follow-up makes: "how long does that keep", "how many days will it last".
_KEEP_TIME_ASK = re.compile(r"\bhow (?:long|many (?:days?|weeks?|hours?|months?))\b", re.I)


# A keeping question is about the food, never about the pan: "how long do i keep stirring it" and
# "how long does it keep in the oven" are cooking questions with a keeping word in them.
_COOKING_SENSE = frozenset("""
oven pan hob grill microwave boil boiling simmer fry frying stir stirring whisk whisking
roast roasting bake baking cook cooking heat
""".split())


# A reply that really says how long something keeps, rather than using "keep" for something
# else ("keep stirring", "keep the pan hot"). The figure is what makes it a keeping answer.
_SPEAKS_OF_KEEPING = re.compile(
    r"\b(?:keeps?|keeping|lasts?|lasting|stays? good)\b[^.]{0,60}\b(?:days?|weeks?|months?|years?"
    r"|hours?)\b"
    r"|\b(?:in|into|out of|from) the fridge\b|\bfreez(?:e|es|er|ing)\b"
    r"|\b(?:days?|weeks?)\b[^.]{0,40}\bin the fridge\b", re.I)


# A dish answer does not always carry its time in figures: "fry onion, garlic, ginger and cumin,
# add the chickpeas and a splash of stock, then wilt the spinach through" is a recipe with nothing
# to keep unless it says so. A step of cooking is what makes the thing on the plate cooked, so the
# cooked-food keeping fact is the answer to "how long will that keep" after one of these too.
# The sentence that states the whole dish's time, rather than one step's: it is the one that
# answers "how long does that take" wherever it sits in the answer.
_TOTAL_TIME = re.compile(
    r"start to finish|from start to finish|in total|altogether|all in\b|in all\b|end to end",
    re.I)


_RECIPE_STEP = re.compile(
    r"\b(?:fry|fries|frying|fried|add|adds|adding|simmer|simmering|bake|baking|roast|"
    r"roasting|boil|boiling|stir|stirring|grill|griddle|wilt|wilted|toss|mash|whisk|"
    r"blend|braise|poach|steam|season|drain|serve)\b", re.I)


_RECIPE_ASK = ("make", "making", "made", "cook", "cooking", "recipe", "recipes", "how", "what goes",
               "ingredients", "from scratch", "method", "proper", "best way", "how long", "simmer",
               "bake", "time", "worth", "should i",
               # "i fancy a curry" is a dish asked for without a question word in it: the want
               # itself is the ask, and it names the dish the method is for. These words are
               # shared with fifty recipe rows, so a word that was rare before must not be here:
               # "fancy" was in one entry's key only, and the meal ideas answer the follow-up
               # "nothing too fancy" by naming that phrase in their own key instead.
               # "love" is not here: "i love curry" is a taste the store says back, and the
               # taste module owns that line now (bot/knowledge/taste.py). Saying what you want
               # to eat is an ask; saying what you like is a fact about you.
               "fancy", "craving", "crave", "mood", "want", "wanting",
               # "i feel like a curry" wants the dish as plainly as "i fancy a curry" does, and
               # the feeling word was the one way of saying it the table did not hold: the line
               # was read as a feeling and answered "Thanks for telling me". A dish still has to
               # be named, so "i feel like a walk" reaches no row.
               "feel like", "feels like", "feeling like", "felt like",
               # the everyday way of asking for one: "whats a good dry rub for chicken" was the
               # "serve it with something wet" fault answer, because no ask word in it was this
               # table's. A dish name is still needed, so "whats a good film" reaches nothing here.
               "whats a good", "what's a good", "whats the best", "what's the best",
               "what is a good", "what is the best",
               # "sandwich filling ideas" asks for one as plainly as "whats a good sandwich
               # filling" does. Only the filling words: a bare "ideas" here took "curry ideas"
               # off the three curries to try and onto the method for one, which is not what
               # ideas are for. The row still needs a dish named, so "gift ideas" reaches nothing.
               "filling ideas", "fillings", "fillings for")


# The dish's own name is an ask for its method. "lasagne", "egg fried rice", "toad in the
# hole": people name a dish and press send, and that was the plainest way of asking for one and
# the only way that reached nothing at all - every row wanted a make-or-cook word as well as the
# dish, so the line fell past the whole table and the bot said "I'm listening". So each row takes
# its own names as ask words too (the names are its key already, so no word becomes common and no
# other row loses a point), and the wrapper below is what keeps every other line of that kind
# where it was.
_RECIPE_ASK_WORDS = re.compile(
    r"(?<![a-z])(?:" + "|".join(re.escape(one) for one in
                                sorted(_RECIPE_ASK, key=len, reverse=True)) + r")(?![a-z])")


# The words that can sit around a dish name and add nothing to it: a dish typed with one of these
# is still the dish on its own, and anything else in the line is a question about the dish rather
# than a request for the method ("lasagne for 8", "vegan lasagne", "lasagne in the air fryer").
_DISH_ON_ITS_OWN_FILLER = frozenset((
    "a", "an", "the", "some", "my", "our", "me", "please", "pls", "plz", "ta", "thanks",
    "thank", "you", "hi", "hello", "hey", "ok", "okay", "oh", "ah", "so", "well", "just",
    "quick", "easy", "simple", "nice", "good", "proper", "some", "and", "then", "for",
    "tonight", "today", "now", "it", "that", "one", "again", "recipe", "recipes"))


def _names_nothing_but_the_dish(text, names):
    """True when the line is one of these dish names and nothing else that says anything."""
    left = " " + " ".join(str(text or "").lower().split()) + " "
    named = False
    for name in sorted(names, key=len, reverse=True):
        needle = " " + str(name).lower() + " "
        if needle in left:
            left = left.replace(needle, " ")
            named = True
    return named and all(word in _DISH_ON_ITS_OWN_FILLER for word in left.split())


# A dish can be asked for by wanting it rather than by asking about it, and the reading calls
# that a statement of news ("i fancy a curry" is not a question). The want is the ask.
_WANT_PHRASES = re.compile(r"\b(?:fancy|fancied|craving|crave|in the mood for|really want|"
                           r"i want|would love|i'd love|i would love|feel like|feels like|"
                           r"feeling like)\b")


# The want has to be for a thing and not for something to happen. "i want to cancel my gym
# membership" carries the want too, and once a dish has been named it reached that dish's method:
# the swap reading puts the last dish in the line, and the curry came back in answer to a
# question about a gym. A want followed by "to" or a pronoun is about an action, not a dish.
_WANT_ACTION = re.compile(r"\b(?:want|wants|wanting|fancy|fancied|craving|crave|love|loves|"
                          r"feel|feels|feeling)\s+(?:like\s+)?"
                          r"(?:to|it|that|this|you|me|him|her|them|us|if|when|how|why|what)\b")


# A want to cook something is a want for the dish: "i want to make a curry" is the curry's
# method, whatever the wording says the want is about.
_WANT_TO_COOK = re.compile(r"\b(?:want|wants|wanting|fancy|fancied|would love|i'd love|"
                           r"i would love)\s+to\s+(?:make|cook|bake|roast|do|try)\b")


# A want to learn to make something is a want for the method: "i want to learn to make bread"
# reached the wish reading instead, so this row stood down and the dish table answered it with
# beans on toast, because bread is a tag on that dish. "i want to learn how to make curry" was
# read as a revision question and got "test yourself instead of rereading". The learning verb
# sits between the want and the make, which is the one place `_WANT_TO_COOK` above does not look,
# so this one allows the verb in between ("learn to make", "learn how to make", "start making").
_WANT_TO_LEARN_COOK = re.compile(
    r"\b(?:want|wants|wanting|fancy|fancied|would love|i'd love|i would love|would like|"
    r"i'd like|thinking of|planning to|going to|gonna|hope to|hoping to)\b[^.!?]{0,24}?"
    r"\b(?:learn|learning|learnt|learned|start|starting|started|try|trying)\s+"
    r"(?:to\s+|how\s+to\s+)?(?:make|cook|bake|roast)\b")


def _wants_the_dish(text):
    """Whether the want in this line is for a dish ("i fancy a curry") rather than an action."""
    if _WANT_TO_COOK.search(text) or _WANT_TO_LEARN_COOK.search(text):
        return True
    return bool(_WANT_PHRASES.search(text)) and not _WANT_ACTION.search(text)


# The lines that name a dish but ask for something else: the swap for a food they have not got
# ("shortbread without butter"), a diet the method breaks ("dairy free brownies"), another way of
# cooking it ("in the air fryer"), or another day ("reheat chilli", "how do i store scones").
# One guard for the whole table beats 33 `avoid` lists, and each of those lines has its own
# answer on main.
#
# A table is not one of them. "for 8 people" was here, and the guard reads the whole said-so-far
# line, not just this line, so the table sat in the text for the rest of the chat: "can i make
# chilli con carne for 14 people" then "how long does it take" stood the chilli method down and
# the reply was the growing time for chillies, 16 to 20 weeks from seed, to someone cooking
# dinner tonight. The number a table needs is read by the rows that answer amounts ("150 g of
# mince and 75 g of dry rice each, 2.1 kg and 1 kg in all" for that line), and they read it off
# the line itself, so nothing here has to stand down for it.
_RECIPE_NOT_THIS = re.compile(
    # "without" is a swap when an ingredient follows it - "scones without eggs", "pastry without
    # butter" - and it is the same method when what follows is a piece of kit: "how do i make
    # pastry without a food processor" was answered with a search suggestion because this one
    # word stood the pastry method down. A determiner before the word is what tells them apart ("a
    # food processor", "an oven", "my mixer"); an ingredient is said bare or with a quantity
    # ("without eggs", "without any sugar"), so the lookahead spares yeast and the determiners.
    # ...except the heat: an oven or a hob is kit you cannot do without either, and telling
    # someone with no oven to bake at 180C is worse than the hedge it replaced ("how do i make
    # pastry without an oven"). A determiner only spares the swap when what follows it is not
    # the thing that cooks.
    r"\b(?:without(?!\s+(?:(?:any\s+)?yeast|(?:a|an|the|my)\s+"
    r"(?!(?:an?\s+)?(?:oven|grill|hob|stove|range|microwave|air ?fryer|cooker|barbecue|bbq)\b)))"
    r"|dairy[- ]free|gluten[- ]free|egg[- ]free|nut[- ]free|sugar[- ]free|vegan|"
    r"vegetarian|substitute|substitutes|substitution|instead of|swap|swapped|swapping|"
    r"replace|replacing|alternative|reheat|reheated|reheating|leftover|leftovers|store|storing|"
    r"stored|storage|freeze|freezes|freezing|air fryer|slow cooker|pressure cooker|microwave|"
    # a keeping question is about the shelf life, not the method: "how long will guacamole keep"
    # was getting "About 10 minutes start to finish" - the method's own clock, which reads like
    # the answer and is not one
    r"keep|keeps|keeping|kept|last|lasts|lasting|go off|goes off|gone off|safe to eat|edible|"
    r"still good|still ok|still okay|"
    r"how much|how many|"
    # a dish that has gone wrong wants the fix, and every one of those lines has its own
    # answer: "how do i thicken curry sauce" is soup-thick, not the curry method.
    r"thicken|thickening|thickens|runny|watery|lumpy|curdled|curdles|split|splits|"
    r"too salty|too spicy|too sweet|bland|burnt|burning)\b")


def _recipe_only_when_asked_for_this(reply, names=(), no_yeast_ok=False):
    """This method, unless the line is not asking for it, wants a swap, or another way.

    no_yeast_ok is for the soda loaf: every other loaf row is a yeast method, and a line that
    says it has no yeast in it cannot use one. names are the row's own dish names, read here to
    tell a dish typed on its own from a line that only names the dish on the way to something
    else, which is a question for another row.
    """
    total = re.split(r"(?<=[.!?])\s+", reply.strip())[0]

    def answer(memory, understood):
        text = _said_so_far(understood, memory)
        alone = _names_nothing_but_the_dish(_this_line_only(understood), names)
        if not alone and not _RECIPE_ASK_WORDS.search(text):
            # The row's ask list now holds the dish's own names, so a line that names the dish
            # comes this far whatever the rest of it says. Every one of those lines was read by
            # another row before this one could reach it, so the make-or-cook word is still what
            # this row needs - except when the line is the dish and nothing else.
            return None
        if _WANT_ACTION.search(text) and not _WANT_TO_COOK.search(text) \
                and not _WANT_TO_LEARN_COOK.search(text):
            # The want in the line is for something to happen, not for the dish: once the swap
            # reading put the last dish back in the line, "i want to cancel my gym membership"
            # reached the curry's method because "want" was the ask word it matched on.
            return None
        if understood.get("intent") not in _RECIPE_ANSWERS and not _wants_the_dish(text) \
                and not alone:
            # A dish on its own is a statement of news by the reading ("lasagne" announces
            # nothing), so it is let through on its shape rather than its kind of line.
            return None
        if not no_yeast_ok and any(one in text for one in _NO_YEAST):
            # the soda loaf: every other loaf row is a yeast method
            return None
        if _RECIPE_NOT_THIS.search(text):
            return None
        # "how long does coleslaw last" and "how long do scones keep" are shelf-life questions
        # about a dish, and the first sentence of a method is the wrong clock for them; the
        # keeping rows answer, or the bot says it does not know rather than how long to boil it.
        line = str(understood.get("clean") or "").lower()
        if _RECIPE_KEEPING.search(line) and not _RECIPE_COOKING.search(line):
            return None
        if understood.get("asks") == ["how_long"]:
            # "how long does it take", with no dish of its own in the line, wants the clock and
            # not the method: the first sentence is the whole dish, start to finish.
            return total
        return reply
    return answer


# "How long does coleslaw last" is a shelf-life question about a dish, and the first sentence of
# a method is the wrong clock for it. Only the words that mean keeping and nothing else are here:
# "green" and "soft" are keeping words too, and "how long does green curry take" is a method line.
_RECIPE_KEEPING = re.compile(
    r"\b(?:keep|keeps|keeping|shelf[ -]life|last|lasts|lasted|store|stores|storing|storage|"
    r"go off|goes off|gone off|past its date|past the date|out of date|next day|tomorrow|"
    r"once opened|once open|mouldy|mould|moldy|mold|use by)\b")


_RECIPE_COOKING = re.compile(
    r"\b(?:cook|cooks|cooking|cooked|boil|boils|boiling|bake|bakes|baking|roast|roasting|"
    r"fry|frying|grill|grilling|steam|steaming|make|makes|making|recipe|prepare|prep|"
    r"assemble|heat|oven|simmer|reheat)\b")


# A recipe is how to make the dish, and a fault in it is a different question with a different
# first sentence: "how do i thicken curry sauce" got the forty-minute curry method, which says
# nothing about the pan in front of the person. So every recipe row stands aside for the
# thickness words, and the fault entries (soup-thick, fix-watery, the curdling ones) take them.
# A method is the pan and a sowing is the garden: "when should i sow salad leaves" is a row in
# the garden's table, and the salad recipe answered it because "should i" is an ask and a salad
# leaf is a dish. Only the words that mean a seed in the ground are here - "plant" and "grow"
# are too common in a kitchen ("plant based", "grow your own with this") to carry the rule.
_RECIPE_GROWING_WORDS = (
    "sow", "sows", "sowing", "sowed", "germinate", "germinating", "seedling", "seedlings",
    "allotment", "veg patch", "vegetable patch", "raised bed", "raised beds",
    "harvest", "harvesting", "crop", "crops", "plant out", "planting out", "thin out",
    "thin the seedlings")


# A dish someone says they are cooking now is an announcement, and the plan row answers it with
# the time, the heat and the one thing to get right ("Spag bol: an hour start to finish, and the
# sauce is worth the last half of it at a bare simmer"). Reading the whole method out to a line
# that only said what it was making is the recipe card for a question nobody asked - "im making a
# spag bol tonight" and "im gonna make a spag bol tnite any tips" both read like a recipe dump.
# So the recipe rows stand down for the first person doing it, which is the shape the plan row
# keys on. A question is untouched: "how do i make spag bol" and "spaghetti bolognese recipe"
# name no first person, and "we are having chilli tonight" is a table telling you the plan, which
# the recipe answers.
ANNOUNCED_DISH = (
    "im making", "i'm making", "im doing", "i'm doing", "im cooking", "i'm cooking",
    "im gonna make", "i'm gonna make", "im going to make", "i'm going to make",
    "im gonna do", "i'm gonna do", "im going to do", "i'm going to do",
    # the matcher reads the words as they were said, with the contraction written out, so each
    # shape is here twice: "im doing a spag bol tonight" is read as "i am doing"...
    "i am making", "i am doing", "i am cooking", "i am gonna make", "i am going to make",
    "i am gonna do", "i am going to do")


# A dish already made is the pot in the fridge, not the method. "stew made yesterday can i have
# it" was answered with "About 2 to 3 hours start to finish. Brown 1kg of chuck steak..." and the
# person had said when they cooked it: the day a dish was made, and the words for what is left of
# it, are the keeping row's question, which answers them with a verdict on that day count. A
# recipe ask never carries one of these - "how do i make a stew", "beef stew recipe" - so the
# recipe rows stand down for a line that points at the pot rather than at the dish.
_A_POT_ALREADY_MADE = re.compile(
    r"\b(?:made|cooked|done|ate|had)\b[^.?!]{0,24}\b(?:yesterday|last night|this morning|"
    r"the night before|the day before|days? ago|\d+ days?)\b"
    r"|\b(?:left ?overs?|left over)\b"
    r"|\b(?:in|been in) the (?:fridge|freezer|pot|tub)\b"
    r"|\bmade (?:on|for) (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)


def _a_made_pot_is_not_its_recipe(understood):
    """True when the recipe row may answer: the line asks for the method of a dish, not the pot."""
    if not isinstance(understood, dict):
        return True
    text = understood.get("norm_text") or understood.get("clean") or ""
    return not _A_POT_ALREADY_MADE.search(str(text))


_RECIPE_FAULT_WORDS = (
    "thicker", "thicken", "thickens", "thickening",
    "thinner", "too thick", "too thin", "watery", "runny", "stodgy", "lumpy",
    "curdled", "curdles", "split", "splits", "too salty", "too spicy", "too sweet",
    "bland", "burnt", "burning")


for _names, _key, _reply, _avoid in RECIPES:
    def _alone(line, _only=tuple(_names)):
        # a dish typed with nothing done to it: see _names_nothing_but_the_dish
        return _names_nothing_but_the_dish(line, _only)

    ENTRIES.append(entry("recipe-" + _key[0].replace(" ", "-"),
                         (_names, _RECIPE_ASK),
                         _recipe_only_when_asked_for_this(
                             _reply, _names, no_yeast_ok=_key[0] == "soda bread"),
                         # the dish's own name is the ask for its method: see _RECIPE_ASK_WORDS
                         ask=tuple(_RECIPE_ASK) + tuple(_names),
                         # the name is one signal and the shape is the second, which is what the
                         # two-position rule wants: a one-word dish ("lasagne") has no other
                         # word to be its own second position.
                         shape=(_alone,),
                         # "bread with no yeast" ties with the prove instructions on words, so
                         # the soda loaf needs the point on its side to take the line. The
                         # sandwich needs the same: the satiety row keys "filling" and carries a
                         # bias of 2, so "whats a good sandwich filling" was answered with pasta
                         # and a tin of tomatoes, and the sandwich row tied it on words.
                         bias=(2 if _key[0] in ("rice and peas", "soda bread")
                               else 1 if _key[0] == "sandwich" else 0),
                         # A recipe is the dish as it is, and a card that says "150g of
                         # sugar" is the wrong answer to "how do i make sugar free banana
                         # bread": the line names the dish with something left out of it, which
                         # the swap and cut-down rows answer. The same words stand the rows
                         # written in cooking_entries.py down.
                         avoid=tuple(_avoid) + _RECIPE_FAULT_WORDS + _RECIPE_GROWING_WORDS
                         + _NO_SUGAR + ANNOUNCED_DISH,
                         # a dish already made is the keeping row's question, not the method
                         guard=_a_made_pot_is_not_its_recipe))


_PANTRY_FOODS = frozenset(
    [_fold(alias) for aliases, _reply in PANTRY.values() for alias in aliases]
    + [_fold(name) for name in PANTRY])


def names_a_dish(understood):
    """The dish a line names from the recipe table, or None when it names no dish.

    The whole line is read, not only the words above MIN_SCORE, because a dish is a subject: the
    alias has to arrive whole ("spag bol" is one dish, not the word "bol"), and a single-word
    alias counts when the line says it and the kitchen holds a recipe for it.
    """
    if not isinstance(understood, dict):
        return None
    words = understood.get("words")
    if not isinstance(words, (list, tuple)):
        words = str(understood.get("clean") or "").split()
    folded = [_fold(word) for word in words if str(word).strip()]
    for aliases, _keys, _body, _avoid in RECIPES:
        for alias in aliases:
            parts = [_fold(part) for part in alias.split()]
            if not parts or " ".join(parts) in _PANTRY_FOODS:
                continue
            if len(parts) == 1:
                hit = parts[0] in folded
            else:
                hit = any(folded[at:at + len(parts)] == parts
                          for at in range(len(folded) - len(parts) + 1))
            if hit:
                return alias
    return None


# --- basics a kitchen asks for by name ---------------------------------------
# Three questions people put in the plainest words: a pastry case baked with nothing in it, a
# pan that has lost its coating, and the fastest way to get a clove out of its skin. Each is a
# method, so each answers the whole line rather than a fault ("why did my pastry shrink" is the
# fault table's, and these stand aside for it).
ENTRIES.append(entry(
    "blind-bake",
    # Every word here is one that other entries already use: the matcher weighs a key word by
    # how rare it is, so a word borrowed from a neighbour's key would quietly cost that entry a
    # point ("skin" belongs to the crispy chicken skin, "baked" to the jacket potato).
    (("pastry", "flan", "pastry case", "pastry base", "pie base", "tart base",
      "pie case", "tart case", "flan case", "blind bake", "blind baking",
      # "should i blind bake a quiche" is this job asked about the dish. It used to be avoided
      # here on the grounds that a quiche recipe answers it better, but the recipe entry needs a
      # make-or-cook word, so the line was a shrug.
      "quiche", "quiches"),
     ("blind", "blind bake", "blind baking", "bake", "baking", "line", "lined", "weights",
      "baking beans", "dry rice", "empty case", "before the filling",
      # "how long do i blind bake pastry" is the clock on this job, not a curtain to measure
      "how long", "how many minutes")),
    ("Line the tin with the pastry, prick the base all over with a fork, then cover it with a "
     "sheet of crumpled parchment and fill that with baking beans or dry rice. Bake at 200C "
     "(180C fan) for 15 minutes, lift the paper and beans out, and give it another 5 minutes to "
     "dry the base before the filling goes in. Blind just means baked empty - the weights stop "
     "the base rising and the sides slumping."),
    # "how long do i blind bake pastry" also fits the curtain-measuring entry (a blind is a
    # curtain, and a time question is a length to it), so this answer carries one point more
    bias=1,
    # a fault on a pastry case is the fault table's answer ("why did my pastry shrink"),
    # and a recipe for pastry itself is the shortcrust question
    avoid=("shrank", "shrink", "shrunk", "soggy", "sunk", "sank", "raw", "burnt", "burned",
           "cracked", "cracking", "crumbly", "falls apart", "how do i make pastry",
           "pastry recipe", "shortcrust", "rough puff", "puff pastry", "choux", "filo",
           "filling", "freeze", "frozen", "keep", "leftover",
           # "how do i make a quiche" is the recipe, which is its own entry: this one keys
           # "quiche" too, so it must not carry a make-or-cook word on the other side
           "make a quiche", "cook a quiche", "quiche recipe", "quiche recipe")))


ENTRIES.append(entry(
    "season-pan",
    (("pan", "pans", "wok", "skillet"),
     ("season", "seasoning", "seasoned", "reseason", "re-season", "cure", "curing",
      "sticking", "sticks", "ruined", "unusable", "lost its coating")),
    ("A pan that sticks has usually lost its thin layer of baked-on oil: scrub it, dry it on the "
     "hob, rub a film of neutral oil over the inside and heat it until it just smokes, then wipe "
     "the surplus off with kitchen paper. Twice more and it is slippery again. That works on "
     "stainless steel, carbon steel and cast iron. A non-stick pan is the exception - once the "
     "coating is scratched through, nothing brings it back, so replace it."),
    ask=("how", "what", "should", "do i", "can", "when", "why", "my"),
    # the cast iron pan and its washing, rust and seasoning are main's own entry, so this one
    # answers the plain pan; seasoning food in a pan is the recipe's business
    avoid=("cast iron", "cast-iron", "carbon steel", "rust", "rusty", "rusts", "dishwasher",
           "chicken", "steak", "salmon", "fish", "meat", "veg", "vegetables", "potatoes",
           "rice", "pasta", "soup", "stew", "curry", "to taste", "salt and pepper",
           "smoking", "smoke", "fire", "alarm", "burnt", "burning")))


# ... but only the bare ask points back. A line that says what the ideas are *for* names its own
# subject, and the food on the table is not it: "any ideas for using up leftover chicken" then
# "any ideas for a cheap day out on saturday" was answered with the chicken again, behind "The one
# I'd go back to:". The phrases above that point with a word ("with them", "use it up") still point
# back whatever follows them, because the pointing word is the object.
POINT_BACK_BARE = frozenset(("any ideas", "any idea", "any other ideas", "any suggestions",
                             "suggestions", "what else", "anything else", "something else",
                             "what do you suggest"))


# A pointing word after the preposition ("any ideas on this", "something else for it") is the
# food again, not a subject of its own. When the object of that preposition is the food in hand or
# the meal it is for - "any ideas for the rest" and "anything else for dinner" after a fridge
# full of chicken - the line is that food's follow-up again, not a new subject, so the fence reads
# the whole object rather than the first letter after the preposition.
THE_FOOD_OR_THE_MEAL = frozenset(("it them those these this rest leftover leftovers left other "
                                 "using use dinner tea supper lunch breakfast meal meals "
                                 "pudding dessert snack").split())


POINT_BACK_OBJECT = re.compile(r"\b(?:for|about|on)\s+(.+)$", re.I)


def _ideas_are_for_something_else(said):
    """Whether a bare ask for ideas or suggestions names a subject of its own."""
    named = POINT_BACK_OBJECT.search(said)
    if named is None:
        return False
    return not (set(re.findall(r"[a-z']+", named.group(1).lower())) & THE_FOOD_OR_THE_MEAL)


def _food_before(memory):
    """The words of the nearest earlier turn that named food, or none."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return []
    for turn in reversed(turns[-3:]):
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("user") or "")
        if any(phrase in said.lower() for phrase in POINT_BACK_STOP):
            return []
        words = _words_of(said)
        if ingredients({"words": words}):
            return words
    return []


def pointed(memory, understood):
    """The reading a line that points back at earlier food means, or None.

    "what can i make with them" names no food of its own, and a reply built from the words of
    that line alone has none to work with, so it falls back to a list of quick dinners. The food
    is the one the last turn or two named, so the line is read as if it had been said again:
    the earlier food in front of these words. None when the line names its own food, points at
    nothing in the kitchen, or points back at something that is off or unsafe.
    """
    if not isinstance(understood, dict):
        return None
    if ingredients(understood):
        return None
    clean = str(understood.get("clean") or "").lower()
    if not any(phrase in clean for phrase in POINT_BACK):
        return None
    if (not any(phrase in clean for phrase in POINT_BACK if phrase not in POINT_BACK_BARE)
            and _ideas_are_for_something_else(clean)):
        # The line is only a bare ask for ideas, and it says what they are for: that is its own
        # subject, not the food of the turn before.
        return None
    if any(phrase in clean for phrase in PAIRING_WORDS):
        # "what can i serve with it": the food is still the subject, but the question is the
        # thing beside it, and the method for the food alone is not that answer.
        return None
    earlier = _food_before(memory)
    if not earlier:
        return None
    reading = dict(understood)
    reading["words"] = earlier + _words_of(" ".join(understood.get("words") or ()))
    reading["clean"] = " ".join(earlier) + " " + clean
    if any(phrase in clean for phrase in SECOND_IDEA):
        # "and something else", "what else": only a dish that has not been served already.
        reading["new_dish_only"] = True
    return reading


ENTRIES.append(entry(
    "meal-prep",
    (("meal prep", "meal-prep", "meals prepped", "prep meals", "prep for the week",
      "prep on sunday", "batch cook", "batch cooking", "batch-cook", "cook ahead",
      "cook once eat twice", "cook once and eat twice"),
     # a key holds two parts: one phrase is one signal (weight 3, below the minimum of 4), so
     # the second part is how the question is asked, not what it is about
     ("how", "what", "should", "can", "start", "begin", "tip", "tips", "help", "want",
      "worth", "week", "weekly", "sunday", "idea", "ideas", "best", "way")),
    ("Cook two big things on one day and portion them: a pot of chilli or bolognese and a tray of "
     "roast veg, then cook rice or pasta fresh on the day. Cool it within two hours, box it in the "
     "portions you will actually eat, and keep three days in the fridge or freeze the rest. Chop "
     "an onion, wash a bag of salad and grate some cheese while you are there and a weekday dinner "
     "takes ten minutes. Cooked rice is the one to freeze on the day, not the next."),
    avoid=("safe", "food safety", "how long", "defrost", "gone off")))


ENTRIES.append(entry(
    "plan-the-week",
    # The week's dinners and the shop that goes with them: "how do i make a shopping list for
    # the week", "what should i cook this week", "meals for the week ahead". A line that asks
    # for a meal plan in so many words is the meal-ideas entry's own line (it answers it with
    # the plan), so this one stands down for it rather than saying it a second way.
    (("shopping list", "food shop", "weekly shop", "the week's shop", "weeks shop",
      "meals for the week", "dinners for the week", "week of dinners", "week of meals",
      "weeknight dinners", "what to cook this week", "cook this week", "food for the week"),
     ("how", "what", "should", "help", "start", "make", "write", "do", "tip", "tips", "idea",
      "ideas", "best", "way")),
    ("Write down five dinners, not seven: three you can cook without thinking, one new one and one "
     "night for leftovers or something from the freezer. Then shop once from that list, plus "
     "breakfast and lunch things, and buy the fresh veg you will use in the first three days. A "
     "plan you can move a night around is the one that survives; a strict seven-day plan usually "
     "gets abandoned by Wednesday."),
    # a line asking which shop is cheapest asks about shops, not about dinners: "whats the
    # cheapest supermarket for a weekly shop" was this plan because "weekly shop" is a key here
    avoid=("diet", "lose weight", "calories", "calorie", "baby", "toddler", "school lunch",
           "meal plan", "meal planning", "weekly meal plan", "airport", "flight",
           "supermarket", "supermarkets", "cheapest", "cheaper", "which shop", "price",
           "prices", "aldi", "lidl", "tesco", "asda", "sainsburys", "sainsbury's", "morrisons",
           "waitrose", "ocado", "iceland", "co-op", "co op"),
    bias=1))


ENTRIES.append(entry(
    "food-waste",
    # The complaint is the same when there is a "so much" in it: "i waste so much food every
    # week" said the amount and the frequency and neither phrase, so the row could not see it and
    # the kitchen bin answered instead ("Most of it is air and packaging: flatten cartons...").
    # The object is food in every phrase below, so the second half can carry the plain verbs.
    (("stop wasting food", "wasting food", "waste food", "food waste", "throw away food",
      "throwing food away", "food going off", "use up food", "reduce waste",
      "waste so much food", "wasting so much food", "waste food every week",
      "so much food goes off", "food goes off before", "throw so much food away",
      "throwing so much food away", "food in the bin", "ends up in the bin"),
     ("how", "what", "should", "can", "stop", "reduce", "avoid", "tips", "tip", "help",
      "way", "ways", "best", "less", "not", "waste", "wasting", "wasted", "throw", "throwing",
      "away", "week", "month", "much")),
    ("Look in the fridge before you go to the shop: see what is left, then plan the next two "
     "dinners around it. Keep the oldest veg at the front of the drawer, freeze bread, milk and "
     "any meat you will not use in two days on the day you buy it, and treat the freezer as a "
     "pause button rather than a cupboard. A weekly \"whatever is left\" soup or frittata uses up "
     "the odds and ends, and a written list stops you buying a third bag of carrots."),
    avoid=("bin", "council", "collection", "compost", "recycling", "smell", "smells")))


def _scaling_reply(memory, reading):
    """Halving or doubling, whichever the line asked for."""
    line = str((reading or {}).get("text") or (reading or {}).get("norm") or "").lower()
    words = set(re.findall(r"[a-z']+", line))
    if any(word in words or ((" " in word) and word in line) for word in SCALE_UP_WORDS):
        return SCALE_UP
    # "how do i scale a recipe up" puts the word between: the phrase forms miss it
    if "scale" in words and "up" in words:
        return SCALE_UP
    return SCALE_DOWN


ENTRIES.append(entry(
    "halve-a-recipe",
    # "how do i halve a recipe", "how do i double a recipe", "can i cut a recipe in half" and
    # "how do i scale a recipe down" were a search hedge each, and "how do i cut a recipe in
    # half" reached the half-marathon card because "half" is a race distance as well. The
    # scaling word is the subject, so it does the work, and the second half says what is being
    # scaled.
    (("halve", "halving", "halved", "half the recipe", "cut the recipe in half",
      "cut a recipe in half", "cut this recipe in half", "make half", "half a batch",
      "double", "doubling", "doubled", "double the recipe", "double up", "scale", "scaling",
      "scale down", "scale up", "times two", "times three", "third of the recipe",
      "scale a recipe", "scale up a recipe", "scale down a recipe", "scale the recipe",
      "double a recipe", "halve a recipe", "double the recipe", "halve the recipe",
      "two thirds of the recipe"),
     ("recipe", "recipes", "batch", "ingredients", "quantities", "amounts", "portions",
      "portion", "loaf", "cake", "mixture", "sauce", "soup", "stew", "casserole",
      "bolognese", "traybake", "biscuits", "cookies", "curry", "chilli", "pie", "roast",
      # "can i halve a recipe for two" was the dinner-ideas card and "how do i scale up a
      # recipe for 20 people" was a business one, because "scale up" is also how a company
      # grows: the number of people and the cooking time are what a scaling question says.
      "for two", "for four", "for six", "for eight", "for twelve", "for 20", "for 20 people",
      "for twenty", "for 30", "for a crowd", "for a big group",
      "cooking time", "baking time", "bake time", "oven time")),
    _scaling_reply,
    bias=1,
    # Doubling and halving is a kitchen question: a line about a race, a bill, a dose or a
    # portion of chips is not asking how to scale a recipe.
    avoid=("marathon", "half marathon", "race", "half price", "bill", "bills", "dose",
           "dosage", "paracetamol", "ibuprofen", "tablet", "tablets", "chips", "half a chicken",
           "half a pizza", "wine", "beer", "rent", "mortgage", "salary", "wage")))


ENTRIES.append(entry(
    "cook-for-one",
    # The one-person words are the evidence, not the subject: "on my own" is also how people
    # describe saving for a house or paying off a debt without help, and with "how" in the other
    # half this row took every one of those money lines.
    (("cook", "cooking", "cook for", "meal", "meals", "dinner", "dinners", "recipe", "recipes",
      "food", "eat", "eating"),
     ("for one", "for one person", "for myself", "on my own", "just me", "only me",
      "just for me", "single", "alone")),
    ("Cook two portions and let the second one be tomorrow's lunch or dinner: it is barely more "
     "work and it is the whole trick. Buy the smaller packs where they exist, freeze half a loaf "
     "and half a pack of mince on the day, and keep eggs, tinned tomatoes, pasta, rice and frozen "
     "veg in as the base of a ten-minute dinner. A frying pan and one small pot will do most of "
     "it."),
    # "easy meal ideas for cooking for one" is about cooking for one, not about one dish
    bias=1,
    # "cook" plus "for one" was reaching a dish the line named: "how do i cook a steak for one"
    # was being told to cook two portions. A person who names the dish wants that dish, so the
    # row answers the habit - ideas, worth it, batch, portions, cooking for one - and leaves the
    # method questions to the dish.
    ask=("ideas", "worth", "bother", "should", "plan", "planning", "batch", "portions",
         "portion", "leftovers", "what can i", "what should i", "meal ideas", "meals for",
         "dinner ideas", "recipes for", "cooking for one", "cook for one", "for myself",
         "on my own", "just me", "only me", "just for me", "cook for", "cooking for",
         "eat for", "what to cook", "ideas for"),
    # "on my own" and "just me" are how people describe both halves of a life: a meal for one,
    # moving a wardrobe upstairs without help, and raising two kids. A line that names a thing you
    # carry, fit or clean is not a meal question, and neither is one about the children or the
    # money, so those words take it out of the kitchen.
    avoid=("lonely", "loneliness", "widow", "grief", "died", "bereave",
           "upstairs", "downstairs", "stair", "stairs", "stairwell", "landing", "loft",
           "attic", "cellar", "garage", "gutter", "gutters", "roof",
           "wardrobe", "sofa", "settee", "couch", "furniture", "mattress", "bed frame",
           "bookcase", "bookshelf", "shelving", "shelf", "shelves", "flat pack", "flat-pack",
           "flatpack", "move house", "moving house", "house move", "curtain", "curtains",
           "blind", "blinds", "carpet", "paint", "wall", "walls", "door", "doors",
           "window", "windows", "tile", "tiles", "fence", "shed", "decking", "mower",
           "lawn", "drill", "hook", "hooks", "car", "van", "bike", "bicycle",
           "washing", "laundry", "ironing", "dishes", "washing up", "hoover", "vacuum",
           "cleaning", "washing machine", "dishwasher", "boiler", "radiator", "tap",
           "toilet", "fridge", "freezer", "bin", "bins",
           # raising children and paying for them is not a meal for one either
           "raise", "raising", "child", "children", "kid", "kids",
           "bring up", "bringing up", "single parent", "single mum", "single dad",
           "save money", "saving money", "afford", "rent", "bills", "money",
           # "is it ok to go for a meal on my own" is about eating out alone, and "on my own" is
           # in this row's ask words as well as its key, so a meal in a restaurant was read out as
           # how to cook for one. Eating out alone is opinions' out-on-your-own answer.
           "restaurant", "restaurants", "cafe", "pub", "eat out", "eating out", "meal out",
           "go for a meal", "going out for", "out for dinner", "out for lunch", "takeaway")))


ENTRIES.append(entry(
    "more-vegetables",
    (("eat more veg", "eat more vegetables", "more vegetables", "more veg", "get veg into",
      "vegetables in my diet", "eat veg", "five a day", "more greens",
      "blend veg", "blend vegetables", "blended veg", "blend the veg", "hide veg",
      "hide the veg", "hidden veg", "puree veg", "puree the veg", "puree vegetables",
      "sneak veg", "sneak the veg", "veg into a sauce", "vegetables into a sauce"),
     ("how", "what", "should", "shall", "can", "help", "tips", "tip", "ideas", "way", "ways",
      "best", "want", "need", "get", "eating", "hide", "blend", "sneak", "puree")),
    _more_veg,
    # a child who refuses veg is the feeding answer, and a batch of veg for the freezer is the
    # freezing one: this entry is only about getting more of it into ordinary meals
    avoid=("child", "children", "kids", "kid", "toddler", "baby", "son", "daughter", "fussy",
           "picky", "refuses", "wont eat", "won't eat", "freeze", "freezer", "freezing",
           "frozen", "blanch", "batch cook", "batch cooking")))


ENTRIES.append(entry(
    "freeze-meals",
    (("freeze", "freezing", "frozen", "freezer"),
     ("meal", "meals", "dinner", "dinners", "supper", "batch", "ahead", "well",
      "which food", "what food")),
    ("Stews, curries, chilli, bolognese, soup, lasagne and shepherd's pie all freeze well and come "
     "back the same; cook them a bit under and freeze in portions flat in bags so they thaw fast. "
     "Leave out potatoes cooked in a stew, pasta and rice cooked in it, and add fresh pasta, rice "
     "or a jacket potato on the day. Cool within two hours, label the date, eat within three "
     "months, and defrost in the fridge overnight."),
    avoid=("breast milk", "formula", "baby food", "wedding cake", "cake")))


ENTRIES.append(entry(
    "guests-cheap",
    (("guests", "guest", "party", "crowd", "lots of people", "big meal", "whole family",
      "table full", "people coming"),
     ("cheap", "cheaply", "budget", "save money", "afford", "stretch", "inexpensive",
      "cost", "money")),
    ("One big dish that stretches beats several small ones: a chilli, a curry or a pasta bake with "
     "bread and a big salad, where the cheap starch and veg do the filling and the meat is the "
     "flavour. Chicken thighs, mince, tinned tomatoes, lentils and beans cost far less than "
     "prime cuts or fillets, and a slow-cooked shoulder of pork or lamb feeds a table for very "
     "little. "
     "Ask people to bring the pudding or the drinks and nobody minds."),
    avoid=("restaurant", "takeaway", "wedding", "caterer", "catering")))


# Shellfish that stays shut is a food-safety rule, not a cooking tip, so it has its own entry
# rather than living in a recipe: people ask it while holding the pan.
ENTRIES.append(entry(
    "mussels-unopened",
    (("mussel", "mussels", "clams", "clam", "shellfish", "oysters", "oyster"),
     ("open", "opened", "closed", "unopened", "shut", "eat", "eating", "ok", "okay", "safe",
      "didnt", "didn't", "not", "still", "bin", "throw", "gone off", "cook", "cooking",
      "steam", "steamed", "how long")),
    "Tap each mussel before cooking and bin any that stays open, plus any with a broken shell; "
    "after cooking, bin the ones that stayed shut, because an unopened one was dead before it "
    "went in. Steam the rest in a covered pan with a splash of wine or water for four to five "
    "minutes, and eat them the same day rather than keeping them for tomorrow.",
    # A razor clam is asked for by its own name, and the pantry's clam row has the soak and
    # the steam: "how do i cook razor clams" was answered "Tap each mussel before cooking", a
    # mussel's rule for a shellfish that has no beard to pull.
    avoid=("paint", "shell", "seashell", "shells on the beach", "razor")))


# --- the tail of the list lives in cooking_more.py, for size ----------------------------------
# This file is over the publisher's 1 MiB upload limit and the world refuses any PR whose tree
# carries a file that big, so the sections from "how you tell it is cooked" to the end of the file
# moved to a file of their own: the rows are data, they are the end of the list, and they move as
# one block. The rows are put back here, where they used to stand, so `cooking.ENTRIES` is the same
# rows in the same order; the helpers that block defines come back with them, because other
# modules ask `cooking.follow_up(...)` and `cooking.first_plan(...)` and the tests ask for
# `minutes_said`. A name this file already defines is left as it is.
#
# The names are imported rather than copied, so a checker that reads this file can see where they
# come from and nothing is bound twice: `follow_up` and `first_plan` are what other modules ask
# this file for, `minutes_said` what the tests ask for, and `_clean` and `_said_words` are read by
# `a_dinner_without` below.
from ..knowledge.cooking_more import (ENTRIES as _TAIL_ENTRIES, asks_a_food_fact, first_plan, follow_up,  # noqa: F401
                           plan_recent, remembered, wants, _clean, _said_words)


ENTRIES.extend(_TAIL_ENTRIES)
