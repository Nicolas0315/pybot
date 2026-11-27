"""Part 2 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.cooking_tables import SIDES
from .cooking_part_01 import (
    _OCCASIONS,
)


_CROWD_NOT_A_MEAL = ("poison", "poisoning", "hygiene", "allergy", "allergic", "reaction",
                     "ill", "sick", "sickness", "waste", "bin", "bins", "food bank",
                     "dog food", "cat food", "pet food", "baby food", "fast food")


def _occasion(text):
    """True when the line is a day that matters: a birthday, a wake, or a "70th"."""
    if any(word in text for word in _OCCASIONS):
        return True
    # "my mums 70th next saturday" names the day by its number, not by the word birthday.
    return bool(re.search(r"\b\d{1,3}(?:st|nd|rd|th)\b", text))


def plan_side(memory, text):
    """The side the conversation's own dish has, or None: the public face of _plan_side."""
    found = _plan_side(memory, str(text or "").lower())
    return found[1] if found else None


def side_for(memory, text):
    """What to put beside the dish this conversation is cooking, or None.

    A plan's own side comes first. The plans do not all carry one (steak's does not), so the
    sides table is asked about the conversation's own lines as well: a follow-up that says only
    "what can i have with it" has no dish of its own for the table to read.
    """
    side = plan_side(memory, text)
    if side:
        return side
    from ..knowledge import dishes
    for line in [str(text or "")] + list(dishes.recent_texts(memory))[:3]:
        found = _table_side(line.lower())
        if found:
            return found[1]
    return None


def _table_side(text):
    """The longest name in the sides table this line uses, and its reply."""
    best = None
    for names, reply in SIDES:
        for name in names:
            if re.search(r"\b" + re.escape(name) + r"\b", text) and (
                    best is None or len(name) > best[0]):
                best = (len(name), reply)
    return best


def _plan_side(memory, text):
    """The side for the one dish this line names, with that plan's own name for it.

    One dish, read the way the rest of the kitchen reads a dish (dishes.dish_in), and only that
    dish's plan: walking the plans for the first name found in the line let a bare "chicken" hand
    "what goes with a chicken curry" the roast chicken's potatoes. A dish whose plan has no side
    of its own passes, so the sides table can answer for it instead of another plan's side.
    """
    from ..knowledge import dishes
    lines = [text]
    if isinstance(memory, dict):
        lines += list(dishes.recent_texts(memory))[:2]
    for line in lines:
        name = dishes.dish_in(line)
        plan = dishes.PLANS.get(name or "")
        if not plan:
            continue
        if not plan.get("sides"):
            return None
        names = [wanted for group in plan.get("names", ()) for wanted in group]
        return (len(name), plan["sides"])
    return None


# The reply when the line asks for meal ideas but does not name anything in the kitchen.
ANY_MEAL = ("Ten-minute dinners: pasta with garlic, chilli and olive oil; eggs on toast; or cold "
            "rice fried with frozen veg, an egg and soy sauce. Tell me what is in the fridge and "
            "I will pick one.")


# Diabetes rules no food out, so there is no ban for the dish table to work around: it changes
# how much of the plate is starch. The ten-minute list is the wrong shape of answer, and the
# health table's plate rule answers a different question (what can I eat at all, not what to
# cook), so cooking for a diabetic guest is its own answer.
DIABETIC_PLATE = (
    "Cook the same sort of dinner as for anyone, with the starchy part smaller and the "
    "vegetables bigger: chicken or fish with two veg, a chilli with beans instead of rice, or an "
    "omelette and salad. Halve the potatoes, rice or pasta rather than cutting them out, go "
    "wholegrain where you can, skip the sugary drinks, and keep pudding small - and ask them "
    "what they usually do rather than guessing.")


DIABETES_WORDS = ("diabetic", "diabetics", "diabetes", "sugar diabetes", "type 1", "type 2",
                  "blood sugar")


def _says_diabetes(text):
    """True when this line, or the conversation before it, named diabetes.

    Coeliac and a nut allergy hold on a follow-up because the ban they spell out is read from
    the last few turns; diabetes spells out no ban, so the words that say it are read the same
    way. "What should i cook for her" after "my sister is diabetic" is the same question.
    """
    folded = " " + re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip() + " "
    return any(" %s " % word in folded for word in DIABETES_WORDS)


# A week is a different question from tonight: it is asked with a shop, a plan or a freezer in
# mind, and answering it with one dinner leaves the person where they started.
PLAN_WEEK = ("Pick four dinners you already cook and plan the week on one list before you shop, "
             "then cook once for two nights: a big chilli or a tray of roast vegetables tonight, "
             "the rest in "
             "a pasta bake or wraps tomorrow, and one night that needs no cooking at all. Put one "
             "double batch in the freezer for the night you are late home, and keep two fallbacks "
             "in the cupboard - pasta and a tin of tomatoes, rice and eggs - for the night the "
             "plan falls apart.")


PLAN_CHEAP = ("Cheap weeks come from the same eight things: rice, pasta, tins of tomatoes, "
              "chickpeas or lentils, onions, carrots, frozen veg and eggs. Pick four dinners you "
              "already cook from those and put them on the fridge: a big chilli or bolognese "
              "stretched with lentils so it eats twice, a tray of roast vegetables with the rest "
              "in a pasta bake, a lentil dhal, and beans on toast. That is about 20 pounds a head "
              "for the week, and nothing in it goes off.")


PLAN_BATCH = ("Cook two big pots on one afternoon and the week is half done: a chilli or "
              "bolognese and a curry or dhal, each cooled and split into portions, then frozen "
              "flat in bags so they thaw in minutes. Cook rice and pasta fresh while a portion "
              "reheats, label the bags with the date, and eat them within three months.")


# A hurry is a request for what fits in the time, not a shrug: "i only have 20 minutes to cook"
# and "dinner in 15 minutes" want a dinner that is ready when the clock runs out.
TIME_PHRASES = (("quarter of an hour", 15), ("half an hour", 30), ("an hour", 60))


TIME_WORDS = (("forty five", 45), ("forty", 40), ("thirty", 30), ("twenty five", 25),
              ("twenty", 20), ("eighteen", 18), ("fifteen", 15), ("twelve", 12), ("ten", 10),
              ("five", 5))


# The reply names the minutes the line gave itself: "i only have 20 minutes to cook" was answered
# with "Twenty-five minutes is enough for ...", which reads as if we had moved the deadline. Under
# twenty-five minutes the roast is left out too, because it does not fit in twenty.
TIME_TWENTY = ("Twenty minutes is enough for: a stir-fry, with the rice on before anything else; "
               "pasta with garlic, chilli and a tin of tomatoes; or an omelette with bread and "
               "salad, which is the quickest of the three.")


TIME_SOON = ("Twenty-five minutes is enough for: a stir-fry, with the rice on before anything "
             "else; pasta with garlic, chilli and a tin of tomatoes; an omelette with bread and "
             "salad; or vegetables cut small and roasted 25 minutes at 200C while couscous "
             "steeps in the same time.")


TIME_MIDDLING = ("Half an hour is enough for: chicken pieces or sausages in the oven while the "
                 "potatoes boil, a tray of vegetables cut small roasted with couscous, or pasta "
                 "baked with a tin of tomatoes and cheese. Put the oven on first and the kettle "
                 "second, and with an hour you can leave a chilli or a curry to simmer.")


def _minutes_named(said):
    """How many minutes the line gives itself, or None when it names no time at all."""
    found = re.search(r"\b(\d{1,3})\s*(?:minutes?|mins?)\b", said)
    if found:
        return int(found.group(1))
    for phrase, minutes in TIME_PHRASES:
        if phrase in said:
            return minutes
    for phrase, minutes in TIME_WORDS:
        if re.search(r"\b" + phrase + r"\b", said):
            return minutes
    return None


# The dishes, not the paragraph: "cheap dinners, no cheese" was answered with a tray of roast
# vegetables and feta, because the money question and the cheese ban were read separately.
CHEAP_DISHES = (
    "a big spag bol with lentils cooked in with the mince",
    "a tray of roast vegetables with couscous and feta",
    "sausages with mash and onion gravy",
    "a chickpea and tomato curry with rice",
    "beans on toast with a poached egg",
)


CHEAP_TAIL = ("Eggs, tins, pasta, rice and frozen veg are where the money goes furthest, and the "
              "mince stretched with lentils does two dinners.")


CHEAP_TAIL_MEATFREE = ("Eggs, tins, pasta, rice and frozen veg are where the money goes furthest, "
                       "and a pot of lentils or beans does two dinners.")


# The protein answer is a list of cheap sources, which is the wrong shape for "is rice and beans a
# complete protein": that line asks whether a pair of plant foods does the whole job, and the
# answer is yes, at any meal of the day. One entry answers both, because both are the same
# question - how to get the protein without meat - asked from either end.
PROTEIN_SOURCES = ("You can get plenty without meat: eggs, milk, cheese and yogurt, a tin of beans "
                   "or chickpeas (about 15g of protein), lentils (about 18g per 100g dry), tofu, "
                   "nuts, seeds and wholegrains. Spread it over the day rather than one meal - "
                   "beans at lunch, eggs or tofu at dinner, yogurt and nuts as a snack - and there "
                   "is no need to count anything.")


PROTEIN_COMPLETE = ("Rice and beans together give all the amino acids the body cannot make itself, "
                    "and so do beans on toast, lentils with rice, and hummus with bread. You do "
                    "not have to pair them at the same meal, either: it is the day's food that "
                    "counts, not one plate, so a peanut butter sandwich and a bean chilli on the "
                    "same day is enough.")


def _protein(memory, understood):
    """Enough protein without meat, or whether a named pair of plant foods is a complete one."""
    text = str((understood or {}).get("clean") or "").lower()
    if re.search(r"\bcomplete\b", text):
        return PROTEIN_COMPLETE
    return PROTEIN_SOURCES


# An apple is the one fruit people bake whole, and the time depends on what kind it is: a Bramley
# collapses and an eater holds its shape. "how long do i bake apples for" was a search hedge, so
# the oven, the pan and the microwave are read from the line and each gets its own minutes.
BAKED_APPLES = ("Baked apples take 25 to 30 minutes at 180C (160C fan, gas 4): core them, score "
                "the skin round the middle so they do not burst, fill the hole with raisins, brown "
                "sugar and a knob of butter, and stand them in a dish with a splash of water so "
                "they do not dry out. A big Bramley needs 35 to 40 minutes and goes to a fluff, "
                "while an eater keeps its shape and is done when a knife slides in with no push.")


# The other fruit people put in the oven are the same question with a different number, and
# "how long do i roast a pear" was a search hedge because only the apple had a row. Halved and
# stoned, cut side up in a dish with sugar and a splash of water, is the method for all of them,
# so the minutes and the test for done are the whole of the difference - and the fruit the person
# named is the one the reply names.
BAKED_FRUIT = {
    "pear": ("Baked pears take 25 to 30 minutes at 180C (160C fan, gas 4): halve them and scoop "
             "the core out with a teaspoon, then sit them cut side up in a dish with a splash of "
             "water, a knob of butter and a spoon of sugar. A firm Conference needs 35 to 40 "
             "minutes and a ripe one 20, and either is done when a knife slides in with no push."),
    "plum": ("Baked plums take 15 to 20 minutes at 180C (160C fan, gas 4): halve them and take "
             "the stones out, sit them cut side up in a dish with a spoon of sugar and a splash "
             "of water. They give off a lot of juice, and that syrup is the best part; a whole "
             "one needs 10 minutes more."),
    "peach": ("Baked peaches and nectarines take 20 to 25 minutes at 180C (160C fan, gas 4): "
              "halve them and take the stones out, cut side up in a dish with a knob of butter "
              "and a spoon of sugar. A ripe one gives to a knife at 20 minutes, and a hard one "
              "needs 10 minutes more and is better poached."),
    "quince": ("Baked quince takes far longer than the softer fruit: about 1 hour 30 minutes at "
               "160C (140C fan, gas 3), halved and cored, cut side up in a dish with sugar and a "
               "splash of water. It goes from pale and hard to pink and soft, and it is done when "
               "a knife goes in with no resistance."),
}


# The pan is the other way round from the oven: the softer the fruit the shorter it takes, and a
# plum falls apart in the time a pear needs to soften at all.
STEWED_FRUIT = {
    "apple": ("Stewed or poached: peel, core and slice them, then simmer in a pan with a spoon "
              "of sugar, a splash of water and a squeeze of lemon for 8 to 10 minutes with the "
              "lid on, until they fall apart. A Bramley takes 5, and an eater holds its shape."),
    "pear": ("Stewed or poached pears: peel, halve and core them, then simmer with a spoon of "
             "sugar, a splash of water and a squeeze of lemon for 10 to 15 minutes with the lid "
             "on, until a knife goes in easily. A firm pear takes the 15, and poaching them whole "
             "in wine or syrup wants 20 to 25."),
    "plum": ("Stewed plums: halve them and take the stones out, then simmer with a spoon of sugar "
             "and a splash of water for 6 to 8 minutes with the lid on, until they slump. They "
             "fall apart quickly, so stop while they still hold their shape."),
    "peach": ("Stewed peaches: halve and stone them, then simmer with a spoon of sugar and a "
              "splash of water for 5 to 8 minutes with the lid on. The skins slip off after a "
              "minute in the hot liquid if you want them off."),
    "quince": ("Stewed quince: peel, quarter and core them, then simmer with sugar and a squeeze "
               "of lemon for 45 minutes to an hour with the lid on, until they turn pink and "
               "soft."),
}


MICROWAVED_FRUIT = {
    "apple": ("In a microwave: core them, stand them in a dish with a centimetre of water, cover "
              "it and give two medium apples 6 to 8 minutes on full power, turning them once. "
              "They go soft rather than brown, so finish them under the grill for 3 minutes if "
              "you want the tops caught."),
    "pear": ("In a microwave: halve and core them, stand them cut side up in a dish with a "
             "centimetre of water, cover it and give two halves 4 to 6 minutes on full power. "
             "They go soft rather than brown, so finish them under the grill for 3 minutes if "
             "you want the tops caught."),
    "plum": ("In a microwave: halve and stone them, stand them in a dish with a centimetre of "
             "water and a spoon of sugar, cover it and give four halves 3 to 4 minutes on full "
             "power. They collapse fast, so check them at 3."),
    "peach": ("In a microwave: halve and stone them, stand them cut side up in a dish with a "
              "centimetre of water, cover it and give two halves 4 to 6 minutes on full power. A "
              "ripe one is done at 4; a hard one is better in the oven than longer in there."),
    "quince": ("A quince will not soften in a microwave - it is too hard and too dry - so give it "
               "the oven, or the pan with sugar and lemon for 45 minutes to an hour."),
}


def _the_baked_fruit(text):
    """Which fruit the line names, reading the ones this row knows before the garden's quince."""
    for name, fruit in (("quince", "quince"), ("nectarine", "peach"), ("peach", "peach"),
                        ("plum", "plum"), ("pear", "pear")):
        if re.search(r"\b" + name + r"(?:es|s)?\b", text):
            return fruit
    return "apple"


def _bake_fruit(memory, understood):
    """The oven time for the fruit named, the pan time for stewed, the minutes in a microwave."""
    text = str((understood or {}).get("clean") or "").lower()
    fruit = _the_baked_fruit(text)
    # boiling a fruit is stewing it, not baking it: 8 to 10 minutes in a pan, not 25 in the oven
    if re.search(r"\b(?:stew|stews|stewed|stewing|boil|boils|boiled|boiling|simmer|simmered|"
                 r"simmering|poach|poached|poaching|puree|pureed)\b", text):
        return STEWED_FRUIT[fruit]
    if re.search(r"\bmicrowave\b", text):
        return MICROWAVED_FRUIT[fruit]
    return BAKED_FRUIT.get(fruit, BAKED_APPLES)


JACKET_BAKE = (
    "Prick it, rub it with oil and salt, and bake at 200C (180C fan) for about an hour for a "
    "medium potato, until a knife slides in with no resistance. The oil and salt are what make "
    "the skin crisp; 8 minutes in the microwave first cuts the oven time to 25.")


JACKET_FILL = (
    "Cheese and beans, tuna mayo, coleslaw, chilli or last night's bolognese: butter and salt "
    "first, then the topping, and back in the oven for 5 minutes if you want the cheese melted. "
    "A wet filling wants something crisp alongside - a pickled onion, a handful of salad.")


def _jacket(understood):
    """The bake is one question and what goes in it is another, and they share an entry."""
    said = str((understood or {}).get("clean") or "").lower()
    if re.search(r"\b(fill|filling|fillings|topping|toppings|goes with|what with|put in|"
                 r"beans|cheese|tuna|coleslaw|chilli)\b", said):
        return JACKET_FILL
    return JACKET_BAKE


JAM_RECIPE = (
    "Weigh the fruit, then add the same weight of sugar and simmer it until it reaches 104 to "
    "105C, which is 10 to 15 minutes of hard boiling: test a drop on a cold plate and if it "
    "wrinkles when you push it, it is ready. Soft fruit needs a squeeze of lemon for pectin, and "
    "the jars go in hot.")


CHUTNEY_RECIPE = (
    "Chutney is fruit or veg with half its weight of sugar and enough vinegar to cover, simmered "
    "down until a spoon drawn across the pan leaves a trail - an hour or two - then potted in hot "
    "jars and left 3 to 4 weeks to mellow. The vinegar is what keeps it, so do not skimp on it.")


def _jam_make(understood):
    """Jam and chutney are the same pan of fruit and sugar with different amounts of vinegar."""
    said = str((understood or {}).get("clean") or "").lower()
    if "chutney" in said or "preserve" in said:
        return CHUTNEY_RECIPE
    return JAM_RECIPE


POACH_FISH = (
    "Poach {fish} in water that is trembling rather than bubbling, about 80C, for 6 to 8 minutes "
    "for a fillet, or 15 to 20 minutes for a whole side in a 120C oven. It is done when a knife "
    "goes into the thick end and the flakes just separate; milk, a bay leaf and a few peppercorns "
    "in the water are what a restaurant poach tastes of.")


def _poach_fish(understood):
    """"haddock poached in milk" is the same method and a different fish, so name the one said."""
    text = str((understood or {}).get("clean") or "").lower()
    for name in ("haddock", "cod", "trout", "salmon"):
        if re.search(r"\b" + name + r"\b", text):
            return POACH_FISH.format(fish=name)
    return POACH_FISH.format(fish="salmon")


MUSHROOM_WASH = (
    "Rinse them quickly under the tap and dry them on a tea towel - mushrooms take on very "
    "little water in a few seconds, and a wipe with damp kitchen paper leaves the grit in the "
    "gills. Do not leave them soaking in a bowl, which is the one thing that does make them "
    "watery, and cook them straight after.")


MUSHROOM_PEEL = (
    "No need: the skin on button, chestnut and portobello mushrooms is thin and it is flavour, so "
    "wipe or rinse them, snap out the stalk if it is woody, and slice. Peel only a field mushroom "
    "with gritty skin or a shiitake with a tough stem, and cut the stem off at the cap rather "
    "than peeling it.")


def _mushroom_wash(understood):
    """Whether to peel is a different question from whether to wash, and they share an entry."""
    said = str((understood or {}).get("clean") or "").lower()
    if re.search(r"\bpeel", said) or re.search(r"\bskin\b", said):
        return MUSHROOM_PEEL
    return MUSHROOM_WASH


def _same(word, wanted):
    """One word matches another loosely: eggs/egg, potatoes/potato, minced/mince."""
    return bool(word) and bool(wanted) and (word == wanted or word.startswith(wanted))


_BAKED_GOODS = ("cake", "cakes", "cupcake", "cupcakes", "muffin", "muffins", "bun", "buns",
                "scone", "scones", "brownie", "brownies", "blondie", "blondies", "cookie",
                "cookies", "biscuit", "biscuits", "shortbread", "flapjack", "flapjacks",
                "sponge", "sponges", "loaf", "loaves", "bun loaf", "traybake", "traybakes",
                "cheesecake", "cheesecakes", "madeira", "doughnut", "doughnuts", "donut",
                "donuts", "fruit cake", "victoria sponge")


_CAKE_NAMES = ("cake", "cakes", "cupcake", "cupcakes", "sponge", "sponges", "loaf cake",
               "victoria sponge", "madeira", "fruit cake", "traybake", "traybakes")


_BAKE_KEEPING = ("keep", "keeps", "keeping", "kept", "last", "lasts", "how long", "freeze",
                 "freezes", "freezer", "fridge", "refrigerate", "store", "storing", "stored",
                 "stays fresh", "stay fresh", "still good", "gone off", "go off", "use by")


# "bake" and "baked" are verbs as often as they are cakes: a pasta bake and a baked potato are not
# a sponge, so the cake answer asks for a named baked good and the bake dishes get their own below.
_BAKED = _BAKED_GOODS + ("baking", "bread", "breadcrumbs", "waffle", "waffles")


_BAKE_NAMES = (("cupcake", "cupcakes"), ("muffin", "muffins"), ("brownie", "brownies"),
               ("cookie", "cookies"), ("biscuit", "biscuits"), ("flapjack", "flapjacks"),
               ("scone", "scones"), ("sponge", "sponges"), ("loaf", "loaves"),
               ("traybake", "traybakes"), ("bread", "bread"), ("cake", "cakes"),
               ("bun", "buns"), ("tart", "tarts"), ("pie", "pies"), ("pastry", "pastry"))


def _the_bake_named(words):
    """(the bake's name, whether it takes "are"), or ("", False) when the line names none.

    The name is the plural one, because "Dry muffin is usually" is not English and "Dry muffins
    are" answers a person holding one just as well. Bread and pastry are mass nouns and keep "is".
    """
    mass = ("bread", "pastry")
    for one, many in _BAKE_NAMES:
        if any(_same(word, many) or _same(word, one) for word in words):
            return (one, False) if one in mass else (many, True)
    return "", False


# A bake or a pie is dry for its own reasons: it went in uncovered, or it stayed in too long.
_BAKE_DISH = ("pasta", "lasagne", "lasagna", "moussaka", "cannelloni", "macaroni",
              "macaroni cheese", "fish pie", "cottage pie", "shepherds pie", "shepherd's pie",
              "quiche", "frittata", "gratin")


# A rice dish that goes dry is the rice answer's: a biryani or a paella names no rice.
_RICE_DISH = ("biryani", "paella", "pilaf", "pilau", "fried rice", "risotto", "couscous")


# A dip or a paste that goes dry wants loosening, not resting under foil.
_DIP_DISH = ("hummus", "houmous", "pesto", "guacamole", "tapenade", "dip", "dips")


# And a sauce is not a roast: "my bolognese is dry", "my curry is dry", "my stew is dry" and "my
# soup is dry" were all told to take it out 5 minutes earlier and rest it under foil. A wet dish
# that has dried out wants liquid back and a lid, which is the opposite instruction.
_SAUCE_DISH = ("bolognese", "bolognaise", "bol", "ragu", "curry", "chilli", "chili", "stew",
               "casserole", "soup", "sauce", "dahl", "dal", "tagine", "goulash", "stroganoff")


# A line that asks the reason wants the cause first, not what to do with the plate: "why is my
# chicken dry" was answered with what to serve with it. The cause is what a cook can change.
def _asks_why(words):
    """True when the line asks the reason: "why", "how come", or "what did i do wrong"."""
    said = " ".join(words)
    return ("why" in words or "howcome" in words or "what did i do wrong" in said
            or "what went wrong" in said or "what am i doing wrong" in said)


def _dry(memory, understood):
    """Dry is a texture fault, and what is dry changes the answer: cake, rice, pastry or meat."""
    text = str(understood.get("clean") or "").lower()
    words = [str(word).lower() for word in (understood.get("words") or [])]
    # A biscuit comes out while the middle still looks soft, so the skewer and the foil below are
    # the wrong tests for one. The biscuit row already has the sentence for dry biscuits, dry
    # cookies and dry shortbread, so this passes and lets the row answer.
    if any(_same(word, wanted) for word in words
           for wanted in ("biscuit", "biscuits", "cookie", "cookies", "shortbread")):
        return None
    rescue = ("Serve it with something wet — gravy, a spoon of yoghurt, a squeeze of lemon and oil — "
              "and next time take it out 5 minutes earlier and rest it under foil. Dry meat or fish is "
              "nearly always overcooked, and resting is what keeps the juice in.")
    # A line that asks the reason wants the reason first: "why is my chicken dry" was answered
    # with what to serve with it, and the cause is the thing a cook can change next time.
    if _asks_why(words):
        rescue = ("Dry meat or fish is nearly always overcooked: it went past the point where the "
                  "juices set, or it was cooked hard and fast without a rest, so the juice ran out "
                  "of it. Take it out 5 minutes earlier next time and rest it under foil, and serve "
                  "this one with something wet - gravy, a spoon of yoghurt, a squeeze of lemon and "
                  "oil.")
    # The dish names here can be two words ("fish pie", "macaroni cheese"), and a line is a list
    # of single words, so the whole line is read for those as well as each word on its own.
    said = " ".join(words)
    # Overcooked pasta is not a bake that dried out: it is starch that gave up, and no amount of
    # sauce and foil brings it back. It was reaching the pasta-bake line because "pasta" is in
    # _BAKE_DISH and "overcooked" is the key.
    if any(word in ("pasta", "spaghetti", "penne", "macaroni", "tagliatelle", "fusilli", "noodles",
                    "noodle", "rice noodles", "udon") for word in words) and any(
                        word in ("overcooked", "over-cooked", "over cooked", "mushy", "soggy")
                        for word in words):
        return ("Overcooked pasta cannot be brought back, but it can be used: drain it, toss it in "
                "oil so it stops sticking, and fold it into a bake, a frittata or a soup where soft "
                "is fine. Next time salt the water properly, take it off a minute before the packet "
                "says, and taste a piece rather than trusting the clock, because a big pan of "
                "boiling water comes back to the boil slowly and the first minute is not cooking.")
    named = any(_same(word, wanted) for word in words for wanted in _BAKE_DISH) or any(
        " " in wanted and wanted in said for wanted in _BAKE_DISH)
    if named and any(
            word in ("bake", "baked", "baking", "oven", "overcooked", "over-cooked", "dry")
            for word in words):
        return ("A bake or a pie dries out when it goes in uncovered or stays in too "
                "long: stir a "
                "splash of milk or a spoon of passata through the sauce, cover it with foil and "
                "give it 10 minutes at 180C to come back. Next time keep a little bechamel back "
                "to pour over the top, and cover it for the first 20 minutes.")
    if any(_same(word, wanted) for word in words for wanted in _BAKED):
        # Gravy on a dry sponge is the wrong answer, so baking gets its own.
        thing, plural = _the_bake_named(words)
        head = ("Dry " + thing + (" are" if plural else " is")) if thing else "A dry bake is"
        return (head + " usually a minute or two too long in the oven, or a little too much "
                "flour. Take it out as soon as a skewer comes out with a crumb on it, weigh the "
                "flour rather than scooping it with a cup, and don't overbeat - and a dry bake is "
                "still good with cream, custard or something wet on it.")
    if any(word in ("rice", "ricecooker") for word in words) or any(
            _same(word, wanted) for word in words for wanted in _RICE_DISH):
        return ("Dry rice means too little water or too long on the heat: add a splash of hot water, "
                "put the lid back on and steam it for 5 minutes on the lowest heat. Next time use one "
                "and a half parts water to one of rice, lid on, 10 minutes, then rest it off the heat.")
    if any(word in _DIP_DISH for word in words):
        return ("Loosen it a spoonful at a time rather than all at once: a splash of cold water and "
                "a squeeze of lemon for hummus, or a little more oil for a pesto, blitzed or stirred "
                "through until it is soft again. A dull, dry taste is usually not enough salt or "
                "acid rather than not enough oil.")
    if any(_same(word, wanted) for word in words for wanted in _SAUCE_DISH):
        return ("A sauce that has gone dry wants liquid back, not less time in the pan: a little "
                "stock, the water the pasta cooked in, a spoon of tinned tomatoes or a splash of "
                "milk, then the lid on and five minutes at a bare simmer. A stew, a "
                "curry or a chilli tightens as it stands, so loosen it at the end rather than "
                "watering it at the start, and keep the heat low enough that it does not catch.")
    if any(_same(word, "pastry") for word in words):
        return ("Dry pastry wants a sprinkle of cold water and a 20 minute rest in the fridge, then roll "
                "it between two sheets of baking paper. Next time keep the fat cold and add water a "
                "tablespoon at a time, because pastry dries out fast once the flour is in.")
    if "safe to eat" in text or "ok to eat" in text or any(
            word in ("safe", "safely", "food-poisoning", "ill") for word in words):
        return ("Dry is a texture problem, not a safety one: if it was cooked through (75C inside, no "
                "pink meat and clear juices) it is fine cold, or reheated once until steaming. " + rescue)
    return rescue


def _bread(memory, understood):
    """One bread method, with the flour the line named: a wholemeal loaf drinks more and rises less."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    said = " ".join(words)
    wholemeal = any(word in ("wholemeal", "wholewheat", "whole") for word in words) or any(
        phrase in said for phrase in ("whole wheat", "whole-wheat", "wholemeal flour"))
    brown = any(word in ("brown", "granary", "malted") for word in words)
    if wholemeal or brown:
        return ("Use 500g of wholemeal flour (or 300g wholemeal flour and 200g strong white "
                "flour, which rises more easily), 7g of dried yeast, 10g of salt and 350ml of warm "
                "water: wholemeal drinks "
                "more and takes longer, so leave it somewhere warm 2 to 3 hours until it has "
                "doubled rather than 1 to 2. Knead 10 minutes, shape it into a tin, leave it 45 "
                "minutes more, then bake at 220C (200C fan) for 35 to 40 minutes and tap the base: "
                "a hollow sound means it is done.")
    return ("Put 500g strong white flour, 7g of dried yeast, 10g of salt and 320ml of warm water in "
            "a bowl, mix it to a sticky dough and knead 10 minutes until it stops tearing. Leave it "
            "somewhere warm 1 to 2 hours until it has doubled, shape it into a tin, leave it another "
            "45 minutes, then bake at 220C (200C fan) for 30 to 35 minutes and tap the base: a "
            "hollow sound means it is done.")


# --- a dish that comes apart -------------------------------------------------------------- #
# "Falls apart" is one complaint with a different cause for every food: a fish breaks up when it
# is wet or moved too soon, a meatball when it has no binder, tofu when it was never pressed, and
# a stew is meant to. The words are in the row's key and the food decides the answer, so the rule
# covers every dish instead of the one somebody happened to write down.
COMING_APART = ("falls apart", "fall apart", "falling apart", "fell apart", "fallen apart",
                "falls to bits", "falling to bits", "fell to bits", "came apart", "coming apart",
                "breaks up", "breaking up", "breaks apart", "breaking apart", "broke up",
                "broken up", "does not hold together", "doesn't hold together",
                "doesnt hold together", "will not hold together", "won't hold together",
                "wont hold together", "not holding together", "disintegrates",
                "disintegrated", "crumbling", "crumbles")


_FISH_NAMES = ("fish", "fillets", "fillet", "white fish", "cod", "haddock", "pollock",
               "hake", "tilapia", "basa", "fish fillet", "fish fillets", "salmon",
               "fishcake", "fishcakes", "fish cake", "fish cakes", "monkfish", "plaice",
               "trout", "sea bass", "bream", "swordfish", "tuna steak")


# A stew, a pulled pork and a slow-cooker joint are supposed to come apart. The words below say
# the dish was meant to break up, so the answer is that nothing has gone wrong.
_COMING_APART_ON_PURPOSE = ("stew", "casserole", "pulled", "slow cooker", "slow cooked",
                            "braise", "braised", "tagine", "goulash", "how long", "until it")


# A soft noodle, a pea or a grain of rice gone mushy is a different fault with its own row, and
# this one would only repeat it.
_MUSHY_OWN_ROW = ("pasta", "spaghetti", "penne", "macaroni", "noodles", "noodle", "rice",
                  "peas", "beans", "lentils", "porridge", "oats", "couscous")


def _falls_apart(memory, understood):
    """A dish that comes apart, answered by the food that came apart.

    The fault is the same few words in every kitchen - falls apart, breaks up, crumbles, will not
    hold together - but the fix is not: fish is dried and left alone in a hot pan, a meatball needs
    something to bind it, tofu needs the water pressed out, a joint coming apart is a joint that is
    done, and a stew is doing what it was asked to. So the entry below is keyed on the fault words
    and on food, and this reads which food the line named.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    said = " " + " ".join(words) + " "
    text = str(understood.get("clean") or "").lower()
    whole = said + " " + text + " "
    why = _asks_why(words)

    def names(*wanted):
        return any(_same(word, one) for word in words for one in wanted)

    if names(*_FISH_NAMES):
        if names("pie", "pies", "fish pie"):
            return ("A fish pie comes apart because the sauce is thin, not because the fish broke: "
                    "make the white sauce thick enough to hold a spoon (about 40g butter and 40g "
                    "flour to 400ml milk) and let the pie stand 10 minutes out of the oven before "
                    "you cut it, so the starch sets. A crumble or a pastry lid that slides off is "
                    "the same fault - too much liquid under the crust.")
        if why:
            return ("A fillet comes apart for two reasons: it went into the pan wet, so it steamed "
                    "instead of sealing, or it was moved before the skin had set. Dry it with "
                    "kitchen paper, get the pan properly hot, lay it in skin side down, press it "
                    "flat for ten seconds and leave it four minutes before you turn it once. A "
                    "fillet that still breaks up was probably overcooked, so take it out the "
                    "moment the thickest part just flakes.")
        return ("Pat the fillet dry with kitchen paper and get the pan properly hot before it goes "
                "in: wet fish on a cool pan steams instead of sealing, and that is what makes it "
                "break up. Lay it in skin side down, press it flat for ten seconds, then leave it "
                "alone for four minutes - it releases itself when the skin has set - turn once and "
                "give it two more, and take it out the moment the thickest part just flakes. "
                "Baking at 200C (180C fan) for 12 to 15 minutes on baking paper is the gentler "
                "way, and a fish stew is meant to break up: stir it in at the end.")

    if names("meatballs", "meatball", "kofta", "koftas", "rissoles", "falafel", "sausage meat",
             "meatloaf", "patties", "patty"):
        return ("Something ground and shaped needs a binder and a rest: one egg and a handful of "
                "breadcrumbs per 500g, mix it just until it holds - overworking makes it springy "
                "- then chill it 20 minutes before it meets the pan, because cold holds together "
                "and warm does not. Sear it in a hot pan without moving it for two minutes a side "
                "so a crust forms, then finish it in a 200C oven rather than turning it again. Too "
                "lean a mince is the other cause: 20% fat is what keeps it in one piece.")

    if names("tofu", "paneer", "halloumi", "tempeh"):
        return ("Press the water out first: wrap the block in a clean tea towel with a weight on it "
                "for 15 minutes, then dust it in cornflour before it goes in the pan. That dry "
                "coat is what holds a crust together, and a hot pan with a little oil that you "
                "leave alone for three minutes does the rest. In a stir-fry, add it last and fold "
                "rather than stir.")

    if names("potatoes", "potato", "mash"):
        return ("Floury potatoes break up and waxy ones hold their shape, so buy the right one: "
                "Maris Piper or King Edward for mash and roast, Charlotte or Jersey Royal for a "
                "salad or a tray of boiled ones. Cut them the same size, cook them from cold "
                "water at a bare simmer rather than a rolling boil, and drain them in a colander "
                "for a minute to steam dry before they go in the oven.")

    if names("dumplings", "dumpling", "gnocchi"):
        return ("A dumpling falls apart when the dough is too wet or the pot is at a rolling boil: "
                "use 100g of suet to 200g of self-raising flour with just enough cold water to "
                "bring it together, drop them onto the stew, put the lid on and keep it at a bare "
                "simmer for 20 minutes without lifting the lid. Gnocchi want the same gentle heat, "
                "and they are done a minute after they float.")

    if names("cake", "cakes", "sponge", "bread", "loaf", "loaves", "pastry", "scone", "scones",
             "biscuit", "biscuits", "cookie", "cookies", "brownie", "brownies", "muffin",
             "muffins", "traybake", "yorkshire pudding", "yorkshires", "burger", "burgers",
             "rice", "peas", "pasta", "noodles", "omelette", "pancake", "pancakes"):
        # Baking, rice, pasta and a burger each have a fault row that names the cause (too much
        # flour, too little water, a cold pan), and a generic "cook it less" answer would be
        # worse than the one that is already there.
        return None

    if names("chicken", "turkey", "lamb", "beef", "pork", "roast", "joint", "shoulder",
             "brisket", "ham", "gammon"):
        return ("Coming apart is how you know it is done: a shoulder, a brisket or a chicken thigh "
                "is ready when it pulls apart with no resistance, and a whole bird is done at 74C "
                "in the thickest part of the thigh. If it is coming apart before it is cooked "
                "through, the heat was too high - turn it down to 150C (130C fan), add a splash of "
                "water to the tin and give it another hour covered, because slow and low is what "
                "turns the connective tissue to gelatine rather than drying the meat out.")

    if names("stew", "casserole", "tagine", "goulash", "braise", "pulled"):
        return ("Nothing has gone wrong: a stew, a braise and a slow-cooked shoulder are meant to "
                "come apart, and that is the sign the connective tissue has turned to gelatine. A "
                "shoulder at 150C takes 3 to 4 hours; if it is coming apart before you want it to, "
                "take it off the heat 20 minutes early and let it sit covered, or lift the pieces "
                "out and reduce the liquid on its own.")

    if any(cue in whole for cue in _COMING_APART_ON_PURPOSE):
        return ("Nothing has gone wrong if it is a stew, a braise or a slow-cooked shoulder: they "
                "are meant to come apart, and that is the connective tissue turning to gelatine. A "
                "shoulder at 150C takes 3 to 4 hours. If it is breaking up before you want it to, "
                "take it off the heat early and let it sit covered.")

    if names(*_MUSHY_OWN_ROW):
        return None

    if why:
        return ("It is nearly always one of two things: it was cooked too long, so what held it "
                "together gave up, or it was turned and moved before it had a crust to hold onto. "
                "Take it off the heat a little earlier next time and leave it alone in the pan "
                "until it releases itself.")
    return ("Handle it less and cook it a little less: food comes apart when it is overcooked, or "
            "when it is moved in the pan before it has sealed. Dry the surface, get the pan hot, "
            "leave it alone until it releases itself, and turn it once. If it is already in "
            "pieces, a bake, a soup or a sauce is the way to serve it rather than a plate.")


_DOUGH_WET = ("wet", "sticky", "slack", "runny", "sloppy", "tacky", "gooey")


# "hard" is left out on purpose: "hard to handle" and "hard to knead" are the wet dough's own
# complaint, not a dry one.
_DOUGH_DRY = ("tight", "stiff", "dry", "firm", "tough", "stretchy", "elastic", "springy",
              "tearing", "tears", "resists", "resist")


_DOUGH_NOT = ("not", "no", "never", "isnt", "isn't", "arent", "aren't", "dont", "don't",
              "doesnt", "doesn't", "wasnt", "wasn't", "cant", "can't", "hardly")


def _dough(memory, understood):
    """A dough's fault has a direction, and too stiff and too wet are fixed opposite ways.

    The last fault named wins, and a `not` in front of it turns it round: "not sticky enough" and
    "isn't wet enough" both want water, and "not dry enough" wants flour.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    direction = ""
    for index, word in enumerate(words):
        negated = any(
            earlier in _DOUGH_NOT or earlier.endswith("n't")
            for earlier in words[max(0, index - 2):index])
        if word in _DOUGH_WET:
            direction = "more flour" if not negated else "more water"
        elif word in _DOUGH_DRY:
            direction = "more water" if not negated else "more flour"
    if direction == "more flour":
        return ("Add flour a spoonful at a time and knead it in before you judge, because a dough "
                "is wettest in the first few minutes: it should cling to your hand and come away "
                "clean. Wetter is better for an open crumb, so stop as soon as it stops running "
                "and keep a little of the water back next time, since flour alone can be 10% "
                "different in how much it drinks.")
    return ("Add water a spoonful at a time and knead a minute after each one: a stiff dough "
            "reads drier than it is, because the flour takes a few minutes to take up what is "
            "already in there, and you only feel the difference after kneading. A bread dough "
            "should be tacky rather than sticky - it clings to your hand but comes away clean - "
            "and it is ready when a piece stretches thin enough to see light through without "
            "tearing. If you overshoot, a spoonful of flour brings it back.")


# Watery is a texture fault, and what is watery decides the fix: a mash, a dip, a pastry case,
# a pan of rice and a sauce each have their own cause. The dish names here are the ones people
# write on their own, and the sauce line stays the fallback for everything else.
_MASH_DISH = ("mash", "mashed potato", "mashed potatoes", "duchess potatoes")


# A "dip" is not one food: a hummus thins from water in the tin, a tzatziki from wet cucumber,
# a pesto from wet leaves, and a plain dip from whatever its base is. They are separate answers
# because the fix is the food, not the word "dip".
_CHICKPEA_WET = ("hummus", "houmous", "humus")


_GREEN_DIP_WET = ("pesto",)


_OLIVE_DIP_WET = ("tapenade",)


_DIP_DISH_WET = ("dip", "dips")


_AVOCADO_WET = ("guacamole", "guac", "avocado", "avocados")


# A pastry case holds a wet filling; pastry on its own is a dough, and a wet dough wants flour.
_PASTRY_WET = ("quiche", "pie", "tart", "flan", "pastry case")


_PASTRY_DOUGH_WET = ("pastry", "shortcrust", "shortcrust pastry", "pie crust")


# A dumpling is not a pan of sauce and it is not a bread dough either: it is shaped wet and
# dropped onto a stew, so a mix that will not hold wants flour and a lid. Without this the row
# read "my dumpling mix is watery" as a stew and told them to take the lid off and simmer it.
_DUMPLING_WET = ("dumpling", "dumplings", "suet", "dumpling mix", "cobbler topping")


_RICE_WET = ("rice", "ricecooker", "biryani", "paella", "pilaf", "pilau")


_RISOTTO_WET = ("risotto", "risotto rice", "arborio")


_COUSCOUS_WET = ("couscous", "bulgur", "bulghur")


# Every name above has to be a word the entry can key on, or the table carries a word that can
# never reach it: _FOOD has no bulgur, avocado, tart, flan, shortcrust, dough or arborio, so
# "my bulgur is watery" and "my avocado is watery" were shrugs with the fix sitting right here.
# The same for the oven dishes and the fried mixes: "my moussaka is watery", "my pastry is too
# wet to roll out" and "my falafel mixture is too wet to hold together" were all shrugs.
_WET_FOOD = ("bulgur", "bulghur", "avocado", "avocados", "guac", "tart", "flans",
             "shortcrust", "dough", "arborio", "rice cooker",
             "moussaka", "cannelloni", "gratin", "macaroni", "lasagne", "lasagna",
             "falafels", "fritter", "fritters", "bhaji", "bhajis", "kofta", "koftas",
             "fishcakes", "fish cakes", "patties", "burger", "burgers",
             # The same rule for the thick and the dressed below: the entry can only answer the
             # names its subject list carries. _FOOD has none of batter, oats, icing, smoothie,
             # yoghurt, dal, lentils or coleslaw, so those lines never reached the fix at all.
             # "oat" alone stays out: "my oat milk is watery" is a drink, not a pan of porridge.
             "batter", "oats", "oatmeal", "grits", "icing", "frosting", "buttercream",
             "ganache", "smoothie", "smoothies", "milkshake", "yoghurt", "yogurt", "raita",
             "tzatziki", "labneh", "dal", "lentils", "lentil", "coleslaw", "slaw", "salad",
             "meatball", "stuffing", "stuffings")


# An oven dish is not a pan of sauce and has no lid to take off: what made it watery is the sauce
# under the top, or vegetables that went in wet. A quiche and a tart are pastry cases, and they
# keep the pastry answer below.
_BAKE_WET = ("lasagne", "lasagna", "moussaka", "cannelloni", "pasta bake", "macaroni cheese",
             "mac and cheese", "fish pie", "cottage pie", "shepherds pie", "shepherd's pie",
             "gratin", "frittata", "traybake")


# Something fried in a mix is not simmered either: a wet mix will not hold together in the pan.
# A sausage meat, a stuffing and a meatloaf are the same fault: they are shaped by hand and they
# have to hold it.
_FRY_MIX_WET = ("falafel", "falafels", "fritter", "fritters", "bhaji", "bhajis", "kofta",
                "koftas", "fishcake", "fishcakes", "fish cake", "fish cakes", "patty", "patties",
                "burger", "burgers", "sausage", "sausages", "sausage meat", "meatloaf",
                "meatballs", "stuffing", "forcemeat")


# A dough is not one dough. Bread wants flour and kneading, pastry wants flour and a rest in the
# fridge, and the pastry answer told a bread dough to chill it.
_BREAD_DOUGH_WET = ("dough", "doughs", "bread dough", "pizza dough",
                    "sourdough", "focaccia", "naan", "ciabatta", "rolls", "buns", "brioche",
                    "bagels", "wholemeal", "pitta")


# A batter is poured, so it wants the right thickness rather than flour on its own.
_BATTER_WET = ("batter", "cake mixture", "sponge mixture", "pancake", "pancakes", "waffles",
               "yorkshire", "yorkshires", "crepe", "crepes", "drop scones")


# Porridge is a breakfast, not a sauce: a loose pan of oats wants less milk next time, not puree.
_PORRIDGE_WET = ("porridge", "oats", "oatmeal", "porridge oats", "oat", "grits")


# The thick and the dressed, not the pan: each of these was told to take the lid off and simmer,
# which is the one thing you cannot do to a bowl of icing or a jug of custard. They are separate
# answers because the fix is the food - icing wants sugar, custard wants heat, a dal wants time
# with the lid off, and a salad wants its water taken out before it is dressed.
_WET_CUSTARD = ("custard", "creme anglaise", "creme patissiere", "creme patisserie",
                "pastry cream")


_WET_ICING = ("icing", "frosting", "buttercream", "ganache", "glaze")


_WET_DRINK = ("smoothie", "smoothies", "milkshake", "milkshakes", "shake", "shakes")


_WET_YOGHURT = ("yoghurt", "yogurt", "raita", "tzatziki", "labneh", "yoghurt dip")


# The words that make it a dip rather than a pot: those lines get the draining answer first.
_WET_DIP_WORDS = ("raita", "tzatziki", "dip", "dips", "cucumber", "mint")


_WET_DAL = ("dal", "dhal", "daal", "lentil", "lentils", "lentil soup", "split peas")


_WET_SLAW = ("coleslaw", "slaw", "salad", "salads")


# A plant milk that looks watery is a carton that has separated, or a homemade one with too much
# water in it - not a pan of anything, so it is not the simmer answer. When the milk is in a dish
# (a curry, a cake, a smoothie) the dish is the subject and keeps its own answer.
_PLANT_MILK = ("oat milk", "oatmilk", "almond milk", "soy milk", "soya milk", "rice milk",
               "cashew milk", "hazelnut milk", "plant milk", "milk alternative", "coconut milk")


_PLANT_MILK_DISH = ("curry", "stew", "soup", "sauce", "cake", "batter", "smoothie", "porridge",
                    "rice pudding", "custard", "ice cream", "coffee", "tea", "chai", "latte")


def _watery(memory, understood):
    """Watery is a texture fault, and what is watery changes the answer: mash, dip, pastry or rice."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    said = " ".join(words)
    # "oat milk" is a drink, not a pan of oats: a food word with "milk" straight after it is the
    # milk, so it is not a food that has gone watery. "my oat milk is watery" was the porridge
    # answer, which tells you to put the pan back on the heat.
    words = [word for word in words if word + " milk" not in said]
    if any(name in said for name in _PLANT_MILK) and not any(
            word in said for word in _PLANT_MILK_DISH):
        return ("A carton of oat, almond or soy milk that pours thin has separated: shake it hard "
                "for half a minute before you open it and it comes back together, and a cheap "
                "barista one holds up better in coffee. Homemade oat milk is thin by nature - "
                "blend 1 part oats to 4 of water, strain it lightly, and add a pinch of salt; it "
                "thickens as it stands in the fridge.")
    named = [names for names in (_MASH_DISH, _CHICKPEA_WET, _GREEN_DIP_WET, _OLIVE_DIP_WET,
                                 _DIP_DISH_WET, _AVOCADO_WET, _BAKE_WET, _FRY_MIX_WET,
                                 _BREAD_DOUGH_WET, _BATTER_WET, _PORRIDGE_WET,
                                 _PASTRY_WET, _PASTRY_DOUGH_WET,
                                 _RICE_WET, _RISOTTO_WET, _COUSCOUS_WET,
                                 _WET_CUSTARD, _WET_ICING, _WET_DRINK, _WET_YOGHURT,
                                 _WET_DAL, _WET_SLAW, _DUMPLING_WET)
             if any(_same(word, wanted) for word in words for wanted in names)
             or any(" " in wanted and wanted in said for wanted in names)]
    if any(names is _MASH_DISH for names in named):
        return ("Mash goes watery when the potatoes come out of wet water or the milk goes in cold: "
                "drain them, put the pan back on a low heat for a minute to steam the rest off, "
                "then mash with warm milk and butter. If it has already gone loose, warm it through "
                "in the pan and stir rather than adding anything - it firms up as the extra water "
                "steams away.")
    if any(names is _CHICKPEA_WET for names in named):
        return ("A hummus goes watery from water or ice going in with the chickpeas, or from too much "
                "lemon: drain the tin well, add a spoon more tahini or a few more chickpeas and "
                "blitz again, and serve it chilled, because it thickens as it sits. Loosen it later "
                "with oil, not water.")
    if any(names is _OLIVE_DIP_WET for names in named):
        return ("Tapenade goes watery from olives that came out of the brine wet, or from too much "
                "oil: drain them, dry them on a tea towel, and pound or pulse them with the capers "
                "and anchovy before the oil goes in. A thin tapenade wants more olives and a few "
                "capers, not less oil, and it firms up in the fridge.")
    if any(names is _GREEN_DIP_WET for names in named):
        return ("Pesto goes watery from basil that was still wet, or from too much oil in one go: "
                "dry the leaves in a tea towel, pound or pulse them with the nuts and cheese first "
                "and add the oil last, a little at a time. A thin pesto in the jar wants more grated "
                "cheese and nuts rather than less oil.")
    if any(names is _DIP_DISH_WET for names in named):
        return ("A dip goes watery from water in the base: drain the tin or squeeze out the grated "
                "vegetable, then thicken it with a spoon of the same solid - chickpeas, yogurt, "
                "cream cheese - and taste it again, because thinning it dilutes the salt and the "
                "acid too.")
    if any(names is _AVOCADO_WET for names in named):
        return ("Guacamole goes watery from over-ripe avocado or too much lime: mash it with a fork "
                "rather than a blender, drain any liquid off and stir in a little more avocado, and "
                "leave the stone in if you are keeping it - it slows the browning, not the water.")
    if any(names is _BAKE_WET for names in named):
        # Not in a pan, no lid: the water came from a thin sauce or veg that went in wet, and the
        # heat that helps is dry heat, not more simmering.
        return ("A bake goes watery when the sauce was thin before it was layered, or the vegetables "
                "still had water in them. Next time drain and squeeze the veg and let the sauce "
                "come to a simmer with a spoon of cornflour slaked in cold water before it goes in. "
                "For this one, give it 10 to 15 minutes uncovered at the same heat, then rest it "
                "10 minutes before you cut it, and the sauce will firm up.")
    if any(names is _DUMPLING_WET for names in named):
        return ("A dumpling mix that is too wet wants plain flour a spoonful at a time until it "
                "stops sticking to the bowl, then shape them with wet hands and drop them onto a "
                "stew that is simmering, put the lid on and give them 20 minutes without lifting "
                "it. Too wet and they spread out into the gravy instead of sitting on top.")
    if any(names is _FRY_MIX_WET for names in named):
        # A fried mix is not simmered: a wet mix falls apart in the oil, and heat cannot dry it.
        return ("A mix that will not hold together is too wet to fry: squeeze grated onion or veg "
                "in a clean tea towel, stir in a spoonful of plain or gram flour, and chill it for "
                "30 minutes so the starch takes up the water. Make sure the oil is properly hot "
                "before the first one goes in - a cool pan is what turns a soft mix into a pancake.")
    if any(names is _BREAD_DOUGH_WET for names in named):
        # A bread dough is the one dough that is not improved by the fridge, so it keeps main's
        # own directional answer: too wet wants flour, and "not wet enough" wants water.
        return _dough(memory, understood)
    if any(names is _BATTER_WET for names in named):
        # A batter is poured, so thin batter is a pan of pale pancakes: it needs the right
        # thickness, not heat.
        return ("A batter that is too wet wants flour, not heat: whisk in a spoonful at a time "
                "until it coats the back of the spoon, then let it rest 20 minutes so the flour "
                "takes up the liquid. Too thin and it will not hold the bubbles, so pancakes come "
                "out pale and flat rather than risen, and a cake will not hold its rise either.")
    if any(names is _PORRIDGE_WET for names in named):
        return ("Porridge that has gone too loose wants a minute more on the heat with the lid off "
                "and a stir, and less milk next time: 40g of oats to 300ml of milk or water is "
                "enough for one, and it thickens as it stands. Do not add more oats once it is "
                "cooking, because they will not soften in time.")
    if any(names is _RISOTTO_WET for names in named):
        return ("Risotto that will not thicken wants more stirring, not more heat: keep it moving "
                "and add the stock a ladle at a time, waiting for each one to be taken up, then beat "
                "in cold butter and grated cheese off the heat at the end - that is what makes it "
                "creamy and loose at the same time.")
    if any(names is _COUSCOUS_WET for names in named):
        return ("Couscous goes watery from too much water: pour it into a wide dish, fork it through "
                "to break up the clumps and leave it uncovered for 5 minutes so the steam escapes. "
                "Next time use the same volume of couscous and boiling water, cover it for 5 "
                "minutes, then fork it with a knob of butter rather than stirring it.")
    if any(names is _PASTRY_WET for names in named):
        return ("A quiche or a pie goes watery when the filling is too wet or the egg is undercooked: "
                "give it 5 to 10 minutes more in a 180C oven and it will set, and next time cook the "
                "vegetables or the fruit down first and let them cool, then blind-bake the case "
                "before the filling goes in.")
    if any(names is _PASTRY_DOUGH_WET for names in named):
        return ("Pastry is a dough, not a filling: if it is wet and sticky, work in a little more "
                "flour a spoon at a time, wrap it and give it 20 minutes in the fridge, and roll it "
                "between two sheets of baking paper rather than dusting it with more flour. Shortcrust "
                "wants about half its weight in fat to flour, and cold hands.")
    if any(names is _RICE_WET for names in named):
        return ("Rice goes watery from too much water or the lid coming off: tip it into a sieve, "
                "then back in the pan with the lid on and 5 minutes on the lowest heat to steam dry. "
                "Next time one and a half parts water to one of rice, lid on, and leave it alone.")
    if any(names is _WET_CUSTARD for names in named):
        return ("Custard that is thin has not had enough heat: stir a teaspoon of cornflour into a "
                "splash of cold milk, whisk it in and give it 2 more minutes on a low heat until it "
                "coats the back of the spoon. It also thickens as it cools, so take it off before "
                "it looks set rather than after.")
    if any(names is _WET_ICING for names in named):
        return ("Icing that is too thin wants icing sugar, a spoon at a time, beaten in until it "
                "holds a soft peak: a teaspoon of water or milk goes a long way, so add that in "
                "drops. A glaze is meant to be thin - it should coat the back of the spoon and run "
                "off in ribbons, which is a different job from icing a cake.")
    if any(names is _WET_DRINK for names in named):
        return ("A thin smoothie or shake wants less liquid and something solid: half a banana, a "
                "spoon of oats or yoghurt, or a handful of frozen fruit, blended again - the fruit "
                "and the ice are what give it body. Pour the milk or juice in last, a splash at a "
                "time, instead of all at the start.")
    if any(names is _WET_YOGHURT for names in named):
        # A pot of yoghurt and a bowl of tzatziki have different causes: one has separated, the
        # other was made with wet vegetables. Both halves are in the reply and the one the line
        # names comes first, because "my yoghurt is watery" is a plain pot while "my raita is
        # watery" is the dip.
        pot = ("A pot of yoghurt that has gone watery has separated, and that is harmless: stir it "
               "back together, or spoon the whey off the top, or strain it through muslin or a "
               "clean tea towel in a sieve for an hour for a thicker pot.")
        dip = ("A yoghurt dip goes watery because the vegetables in it were wet: salt the grated "
               "cucumber or carrot for 10 minutes, squeeze it out in a tea towel, and fold it into "
               "thick yoghurt at the end - a spoon of cream cheese or labneh brings back one that "
               "has already split.")
        if any(word in said for word in _WET_DIP_WORDS):
            return dip + " " + pot
        return pot + " " + dip
    if any(names is _WET_DAL for names in named):
        return ("A thin dal wants the lid off for 10 more minutes, stirring now and then: it "
                "thickens as the lentils break up, and mashing a ladleful against the side of the "
                "pan and stirring it back in thickens it at once. Add water a splash at a time at "
                "the end, because dal sets as it cools.")
    if any(names is _WET_SLAW for names in named):
        return ("A watery salad is nearly always salt pulling the water out of the vegetables: salt "
                "the shredded cabbage or the cucumber for 10 minutes, squeeze it in a clean tea "
                "towel, and dress it just before it goes to the table. Mayo loosened with a splash "
                "of vinegar coats better than a thick spoonful.")
    # "Too wet" and "watery" are not the same fault: a mix or a batter is too wet, and a pan of
    # sauce is too thin. The pan answer is for a sauce, so a wet mix gets the mixing bowl instead
    # of tomato puree, which is what "my cake mixture is too wet" was being told to add.
    # A pan of something is a sauce whatever the word: a bolognese that is "too wet" wants
    # reducing, and it is the pan answer's own case.
    pan_food = any(word in ("sauce", "sauces", "stew", "curry", "chilli", "chili", "gravy", "ragu",
                            "bolognese", "bolognaise", "daal", "dhal", "dal", "tagine", "goulash",
                            "casserole", "cassoulet", "broth", "stock", "soup", "soups", "jus")
                   for word in words)
    thin = pan_food or any(word in ("watery", "runny", "thin", "sloppy", "liquid", "thickens",
                                    "thicken", "reduce", "reduces") for word in words) or any(
        phrase in said for phrase in ("never thickens", "wont thicken", "won't thicken",
                                      "not thickening", "doesnt thicken", "doesn't thicken"))
    if not thin and any(phrase in said for phrase in ("too wet", "a bit wet", "is wet", "went wet",
                                                      "bit wet")):
        # "Too wet" is a texture fault of a mix or a batter, and none of the rows above knows
        # this one: porridge, noodles, a loaf, a cake. The pan answer is the wrong answer to
        # every one of them, so the entry turns the line down (an empty reply) and a lower
        # entry - or the ack - gets the turn, which is worse than a good answer and much
        # better than "stir in a spoon of tomato puree".
        return ""
    return ("Take the lid off and let it simmer for 10 to 15 minutes: most of the water goes off in "
            "the steam. To thicken it properly, stir in a spoon of tomato puree, a handful of red "
            "lentils, or cornflour slaked in cold water, and give it 5 more minutes.")


def _lumpy(memory, understood):
    """Lumps depend on what they're in: mash, custard, porridge and sauce all lump differently."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(_same(word, "mash") or word in ("potato", "potatoes") for word in words):
        return ("Mash them while they're hot with plenty of butter and warm milk, and beat with a "
                "wooden spoon rather than a fork. Lumps come from cold potatoes or too little fat; "
                "if they're stubborn, push the mash through a sieve or a potato ricer.")
    if any(_same(word, "custard") for word in words):
        return ("Take it off the heat and whisk hard, then push it through a sieve. Custard goes "
                "lumpy when the heat is too high or the eggs go in too fast, so next time pour the "
                "hot milk into the eggs a splash at a time and cook it slowly, stirring.")
    if any(_same(word, "porridge") or _same(word, "oats") for word in words):
        return ("Beat in a splash more milk or water and whisk it hard; porridge lumps come from "
                "dry oats hitting hot liquid too fast. Next time stir the oats into cold liquid and "
                "bring it up slowly, stirring all the time.")
    return ("Whisk it hard with the pan off the heat and push it through a sieve, because lumps "
            "break up far better off the ring. Next time stir the flour into the fat before any "
            "liquid goes in, then add the liquid a splash at a time.")


def _occasion(text):
    """True when the line is a day that matters: a birthday, a wake, or a "70th"."""
    if any(word in text for word in _OCCASIONS):
        return True
    # "my mums 70th next saturday" names the day by its number, not by the word birthday.
    return bool(re.search(r"\b\d{1,3}(?:st|nd|rd|th)\b", text))
