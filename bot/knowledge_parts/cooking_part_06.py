"""Part 6 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.bake_faults import _BAKE_FAULT_FAMILIES
from .cooking_part_02 import (
    _BAKED,
)
from .cooking_part_05 import (
    _DIP_FIXES,
)


_DIP_PLAIN = ("A cold dip is put right cold, so leave the pan alone: a spoonful of water or lemon "
              "loosens it, a pinch of salt and twenty minutes in a sieve thickens it, and a little "
              "oil whisked in slowly brings back one that has split.")


OIL_SMOKE_POINTS = (
    ("butter, or clarified butter", "about 150C"),
    ("extra virgin olive oil", "about 180 to 200C"),
    ("a plain or light olive oil", "about 200 to 240C"),
    ("rapeseed, sunflower or vegetable oil", "about 220 to 230C"),
    ("groundnut or rice bran oil", "about 230C"),
)


_ONTO_A_PERSON = ("splashed", "splashes", "splash", "spat", "spits", "spitting", "spit",
                  "flicked", "jumped out", "pops", "popped", "scalded", "burnt my", "burned my",
                  "burnt me", "burnt himself", "burnt herself", "burned me")


def _a_dish_with_a_heat(text):
    """True when the line names a dish the dish table has an oven heat for."""
    from ..knowledge import dishes
    plan = dishes.PLANS.get(dishes.dish_in(str(text or "")) or "")
    return bool(isinstance(plan, dict) and plan.get("temp"))


# What a line has to say for the fat to be the fault: it is smoking, burning, foaming, spitting
# or too hot. The row's key can be reached on its subject alone, and the default answer is about a
# fire, so the fire (or the heat on the way to it) has to be named.
_SOMETHING_IS_WRONG_WITH_THE_PAN = (
    "smoke", "smokes", "smoking", "smoked", "smoky", "smoke point", "smoking point",
    "burnt", "burn", "burns", "burning", "burned", "too hot", "overheat", "overheating",
    "on fire", "caught fire", "in flames", "flaming", "flamed", "black", "spoiled",
    "ruined", "wasted", "not right", "gone wrong", "tastes", "taste", "smell", "smells",
    "stinks", "bubbling", "bubbles", "foam", "foams", "foaming", "foamy",
    "spat", "spits", "spitting", "spattered", "splashed", "jumped out", "popped",
)


def _dip_fault(understood):
    """The one sentence that fixes the dip the line named."""
    text = ((understood or {}).get("clean") or "").lower()
    # Houmous has two opposite faults, so it cannot share one sentence: a thick pot wants
    # loosening, but a watery one wants draining and tahini. The old reply answered both with
    # "loosen it with cold water", which is the wrong way round for half the people who ask.
    if any(name in text for name in ("houmous", "hummus", "humous")):
        if any(word in text for word in ("watery", "too thin", "runny", " thin")):
            return ("Watery houmous usually has too much liquid or not enough tahini: drain the "
                    "chickpeas well, then stir in a spoonful of tahini and a little olive oil and "
                    "chill it for 20 minutes, because it firms up cold. Taste for salt and lemon "
                    "at the end.")
    for names, fix in _DIP_FIXES:
        if any(name in text for name in names):
            return fix
    return _DIP_PLAIN


_SOGGY_BREAD = ("sandwich", "sandwiches", "wrap", "wraps", "roll", "rolls", "baguette", "sub",
                "subs", "ciabatta", "pitta", "pita", "tortilla", "toastie", "butty", "butties",
                "bread", "loaf", "bun", "buns", "brioche", "focaccia", "sourdough")


# The leaves are the other family, and a watery salad is the same water as a watery coleslaw.
_SOGGY_LEAF = ("salad", "salads", "lettuce", "leaves", "coleslaw", "slaw", "pasta salad",
               "greens", "spinach", "rocket", "cucumber", "tomato", "tomatoes")


_BAKE_FOLLOW_SHAPES = ("what did i do wrong", "what went wrong", "why did that happen",
                       "why does that happen", "why did it happen", "what else could it be",
                       "why did they sink", "why did it sink", "why did that sink",
                       "why did some of them sink", "why do they sink", "why does it sink",
                       "how do i stop that next time", "how do i stop it next time",
                       "stop it next time", "what should i do differently",
                       "how do i get it right", "will it happen again", "what do i change",
                       "what could i do differently next time",
                       "can i still use it", "can i still eat it", "can i still use them",
                       "is it still ok", "are they still ok", "how do i use it up",
                       "what do i do with it now")


_NEXT_SHAPES = ("stop", "differently", "next time", "get it right", "happen again",
                "what do i change")


_USE_SHAPES = ("still use", "still eat", "still ok", "use it up", "what do i do with")


_BAKE_KEEP_SHAPES = ("how long does it keep", "how long will it keep", "how long do they keep",
                     "how long will they keep", "how long does it last", "how long will it last",
                     "how long do they last", "how long will they last", "will it keep",
                     "do they keep", "will they last")


def _bake_keep_sentence(bakes):
    """The keeping sentence for the bakes named in these turns, or the cake's when unnamed."""
    said = " ".join(bakes)
    if any(word in said for word in ("scone", "scones", "biscuit", "biscuits", "cookie",
                                     "cookies", "shortbread")):
        return ("Scones and biscuits are at their best the day they are baked and keep 2 days in "
                "a tin; freeze them baked for 2 months and warm them through for 5 minutes at "
                "150C, which brings back most of the crust.")
    if any(word in said for word in ("bread", "loaf", "loaves", "sourdough", "bun", "buns",
                                     "roll", "rolls", "focaccia", "baguette")):
        return ("Bread keeps 2 to 3 days in a paper bag or a bread bin, cut side down, and a "
                "month in the freezer sliced; the fridge is what makes it stale fastest, so "
                "freeze what you will not eat in two days.")
    if "cupcake" in said or "muffin" in said:
        return ("Cupcakes and muffins keep 2 to 3 days in a tin, best the day they are baked, "
                "and they freeze well undecorated for 2 months: defrost them at room "
                "temperature in a single layer.")
    return ("A cake keeps 3 days in a tin, or freezes for 2 months undecorated; a crumbly or "
            "dry one is best eaten in the next day or two, or frozen in slices.")


def _bake_keep(memory, reading):
    """The keeping sentence for the bake named in the last few turns, or "" when none was."""
    line = str((reading or {}).get("text") or (reading or {}).get("clean") or "").lower()
    if not any(shape in line for shape in _BAKE_KEEP_SHAPES):
        return ""
    turns = (memory or {}).get("turns") or []
    for turn in reversed(turns[-3:]):
        said = str(turn.get("user") or "").lower() if isinstance(turn, dict) else ""
        if not any(name in said for name in _BAKED):
            continue
        if "cupcake" in said or "muffin" in said:
            return _bake_keep_sentence([said])
        return ""
    return ""


def _bake_follow(memory, reading):
    """The cause, the next-time fix or the rescue for the bake fault named a turn ago, or ""."""
    line = str((reading or {}).get("text") or (reading or {}).get("clean") or "").lower()
    if not any(shape in line for shape in _BAKE_FOLLOW_SHAPES):
        return ""
    turns = (memory or {}).get("turns") or []
    bakes = []
    for turn in reversed(turns[-3:]):
        said = str(turn.get("user") or "").lower() if isinstance(turn, dict) else ""
        if any(name in said for name in _BAKED):
            bakes.append(said)
    if not bakes:
        return ""
    family = None
    for said in [line] + bakes:
        for candidate in _BAKE_FAULT_FAMILIES:
            if any(word in said for word in candidate[0]):
                family = candidate
                break
        if family is not None:
            break
    if family is None:
        if any(shape in line for shape in _USE_SHAPES + _BAKE_KEEP_SHAPES):
            return _bake_keep_sentence(bakes)
        return ""
    _, cause, cure, rescue = family
    if any(shape in line for shape in _USE_SHAPES):
        return f"It is still worth eating: {rescue}."
    if any(shape in line for shape in _NEXT_SHAPES):
        if not cause[0].isupper():
            cause = cause[0].upper() + cause[1:]
        return f"Next time, {cure}. {cause}."
    return f"{cause}. {cure[0].upper() + cure[1:]}."


_BREAD_WORDS = ("bread", "loaf", "loaves", "sourdough", "bun", "buns", "roll", "rolls", "baguette",
                "focaccia", "pitta", "pita", "brioche", "ciabatta")


_GUMMY_CAKE = ("Gummy means it needed longer, not a hotter oven: the outside set while the middle "
               "was still wet. Give it another 5 to 10 minutes at the same heat with foil over the "
               "top, and test the centre with a skewer, not the edge.")


_GUMMY_BREAD = ("A gummy loaf is under-baked rather than under-proved: tap the base for a hollow "
                "sound, and if the middle feels heavy put it back for 10 minutes at the same heat. "
                "Next time prove until a floured finger springs back slowly.")


def _gummy(memory, understood):
    """The bake the line names decides the answer: bread sets by its bake, a cake by its batter."""
    clean = (understood.get("clean") or "").lower()
    if any(re.search(r"(?<![a-z])" + word + r"(?![a-z])", clean) for word in _BREAD_WORDS):
        return _GUMMY_BREAD
    return _GUMMY_CAKE


# A date question - "is my butter out of date" - is still a keeping question, and KEEP_WORDS has
# no date words because no row above needed one. Keyed by the food, because these words are only
# wanted where a person says them: "is my potato out of date" is not a sentence anyone says.
KEEP_DATE_WORDS = ("out of date", "past the date", "past its date", "use by", "best before",
                   "still ok", "still good", "still fine")


# How to store cheese, and what to do about the mould on it, is `cheese-store`'s question; this
# table is for how long the food keeps, so the row stands down on those words.
MOULD_WORDS = ("mould", "mouldy", "mold", "moldy")


# The words that say a food has already turned, which is the spoilage entry's question and not
# the shelf-life one: "the mince has gone grey" wants to know whether to bin it, not how many
# days raw mince keeps.
_SPOILT_WORDS = ("smell", "smells", "smelly", "smelt", "off", "gone off", "going off", "slimy",
                 "sour", "grey", "gray", "tacky", "separated", "watery", "fizzy", "mould",
                 "mouldy", "mold", "moldy", "pink", "rot", "rotten", "bad", "went bad")


# A cooked thing left over wants a different answer from a raw one, so a leftover line reads
# these first.
LEFTOVER_IDEAS = {
    # a glut of eggs is a volume question: the dishes that take several at a time answer it, and
    # what to do with the whites and the yolks separately is the rest of it.
    "egg": "Eggs going spare: a frittata or a tortilla takes six or eight at once with whatever "
           "veg is in the fridge, a quiche takes four plus milk and cheese, and meringues or a "
           "pavlova use up whites on their own. Hard boiled, they keep a week and make "
           "sandwiches, or halve them into a salad with mustard and oil.",
    "chicken": "Cooked chicken: shred it into a salad with mayonnaise, lemon and something "
               "crunchy, or stir it through fried rice with soy sauce and peas for a 10-minute "
               "dinner.",
    "potato": "Leftover potatoes: crush them a little and fry them in hot oil until crisp, or "
              "slice them into a frittata with eggs.",
    "pasta": "Leftover pasta: loosen it in a hot pan with a splash of water and a little oil, or "
             "bake it with a spoon of tomato sauce and cheese on top.",
    "salmon": "Leftover salmon: flake it through pasta or a salad with lemon and yoghurt, and "
              "don't reheat it hard or it dries out.",
    "bread": "Stale bread: tear it into croutons fried in oil and garlic, or blitz it into "
             "breadcrumbs and freeze them.",
    "lentil": "Leftover dhal: thin it with a splash of stock into soup, or eat it cold as a dip "
              "with bread and yoghurt.",
    "coconut milk": "Half a tin of coconut milk: simmer it with curry paste and whatever veg you "
                    "have for 10 minutes, or stir it into rice instead of water for a coconut "
                    "rice. It freezes in an ice cube tray for next time.",
    "cream": "Cream or soured cream going spare: stir it into a chilli or curry off the heat so "
             "it does not split, spoon it over baked potatoes or fruit, or let it down with a "
             "squeeze of lemon and use it as a dressing. Soured cream also freezes badly, so use "
             "it rather than keep it.",
    "sprout": "Leftover sprouts: halve them and fry cut side down in butter until they caramelise, "
              "about 8 minutes, or shred them raw into a salad with lemon, oil and toasted nuts.",
    "marrow": "Half a marrow left: scoop out the seeds, stuff it with mince and rice and bake it "
              "45 minutes at 190C (170C fan), or grate it into a curry - the water it gives up "
              "thickens the sauce as it cooks.",
    "buttermilk": "Buttermilk going spare: soda bread takes 284ml, or thin a pancake batter with "
                  "it, or marinate chicken in it for an hour before frying - it tenderises the meat.",
    "hot cross bun": "Buns going stale: butter them and bake them in a bread and butter pudding, "
                     "or halve and toast them under a grill with a little sugar on top.",
    "stuffing": "Leftover stuffing: shape it into balls and fry or roast them 15 minutes at 200C "
                "(180C fan), or press it into a tray and cut it into crisp squares - it is the "
                "best part of the tray, so do not bin it.",
    "porridge": "Leftover porridge: loosen it with milk and reheat it, or beat in an egg and fry "
                "spoonfuls in butter for oat fritters with jam.",
    "bolognese": "Leftover bolognese: bake it with pasta and white sauce, spoon it over a jacket "
                 "potato, or thin it with stock and beans into a soup.",
    "curry": "Leftover curry: reheat it once until piping hot and eat it with rice, or bake it "
             "under a mash topping for a curry pie.",
}


# The answer for "i have leftovers, what can i make", when the line names no food this kitchen
# has an idea for. A line that does name one gets that food's answer instead: see
# _leftover_meal_reply.
LEFTOVER_SOUP = ("Soup is the easiest use of leftovers: soften an onion, add whatever veg you "
                 "have in order of toughness, cover with stock, simmer 20 minutes and blend or "
                 "leave it chunky - season at the end. Any cooked meat goes in for the last five "
                 "minutes only, and a spoon of something sharp (lemon, mustard, a splash of "
                 "vinegar) is what stops it tasting like a fridge. Whatever you reheat must be "
                 "piping hot all the way through once, and rice that has sat out is the one "
                 "thing to bin.")


# The word in front that turns a pantry name into a different food ("bean sprouts").
NOT_THIS_FOOD = {
    "sprout": ("bean sprout", "alfalfa", "mung", "soy sprout", "soya sprout"),
    "bean": ("bean sprout",),
    "butter": ("peanut butter", "peanut", "cocoa butter", "apple butter"),
    "corn": ("sweetcorn", "corned"),
    "cream": ("ice cream", "cream cheese", "cream cracker"),
    # A hot chocolate is a drink: "i fancy a hot chocolate" is not a bag of chocolate and a
    # reason to bake brownies.
    "chocolate": ("hot chocolate",),
    # Powder is not the jug: a spoon of buttermilk powder goes in a dry mix for scones or a
    # pancake batter, and the soda bread answer needs the liquid kind.
    "buttermilk": ("buttermilk powder", "powdered buttermilk"),
    # A rice cake is not a bowl of rice: "can i eat rice cakes every day" was answered with egg
    # fried rice, because the table read "rice" and stopped. The snack has its own row in
    # nutrition.py, so here the pantry name only has to step aside. The other things made of rice
    # are the same: a rice cracker, rice paper, rice vinegar or rice flour is not the grain you
    # boil, and "rice crispy cakes" is a cake to make rather than a bag of rice.
    # "rice pudding" is deliberately NOT here: the pudding has its own recipe row, and fencing the
    # head word out under it made a statement about one ("rice pudding in the slow cooker") fall
    # through to the wrong dish. A dish row's own name outranks the plain rice row anyway.
    # An animal's food is what goes in its bowl, not a dish: "he says theyre rabbit food" is a
    # verdict on the vegetables and got a braise on main, because the table read the animal and
    # stopped. The phrase steps the pantry name aside, so the line is answered by whatever it is
    # really about.
    "rabbit": ("rabbit food", "rabbit pellets"),
    "duck": ("duck food",),
    "chicken": ("chicken food", "chicken pellets"),
    "rice": ("rice cake", "rice cakes", "rice crispy",
             "rice crispies", "rice krispie", "rice krispies", "rice cracker", "rice crackers",
             "rice paper", "rice vinegar", "rice wine", "rice flour", "rice drink"),
}


PLANT_MILKS = ("coconut milk", "oat milk", "soy milk", "almond milk", "rice milk",
               "cashew milk", "coconut cream")


# The same thing said with two words, which a word list cannot see.
LEFT_POINTER = ("what's left", "whats left", "what is left", "anything left", "some left",
                "is left", "left over", "leftovers", "use up", "using up")


LEFTOVER_PHRASES = ("left over", "left from", "use up", "using up", "got spare", "spare ",
                    # "what can i do with what's left" is the same question as "leftovers": the
                    # food is already cooked, and the leftover idea is the answer that starts there.
                    "what's left", "whats left", "what is left", "anything left", "some left",
                    "is left", "left of the")


# The ways people ask what to do with an ingredient without a meal word ("what can I do with
# these", "use up the spinach").
# A meal wanted, said as a want rather than a question: "i fancy something with mince", "i could
# go for a curry". Without these a line with one ingredient fell foul of the "one ingredient is a
# question about that ingredient" guard below, and got nothing at all; the pantry can answer a
# want as well as a "what can I make".
MEAL_WANTS = ("i fancy", "i really fancy", "fancy something", "fancy a ", "could go for",
              "could murder", "in the mood for", "i'd love", "i would love", "i quite fancy",
              "i'd quite like", "i would quite like")


MEAL_PHRASES = MEAL_WANTS + ("what can i do with", "what do i do with", "what to do with", "use up",
                # "something with pasta", "make with leeks", "recipes for cabbage": one named
                # ingredient is enough when the line says it wants a dish made of it.
                "something with", "something quick", "something easy", "make with",
                "cook with", "recipes with", "recipes for", "recipe with", "recipe for",
                "ideas with", "meal with", "dish with", "recipe", "recipes", "idea", "ideas",
                "dinner ideas", "lunch ideas", "meal ideas",
                "what can i make", "what can i cook", "what should i make", "what should i cook",
                "thing to do with", "things to do with", "easiest thing to do with",
                "using up", "any ideas", "got left",
                # "what should I do with the rest of the potatoes" is the same question as
                # "what can I do with it", and people say both.
                "what should i do with", "what should i make", "what should i cook",
                "what else can i do with",
                # A list of what is in the kitchen is a meal question even without a "make":
                # "i only have eggs and potatoes", "ive got mushrooms and cream".
                "i have", "i've got", "ive got", "we have", "we've got", "weve got",
                "only have", "only got", "just have", "just got", "left in the",
                "in the fridge", "in the cupboard",
                "on their way out", "on the way out", "past its best", "past their best",
                "need using", "needs eating", "going over", "starting to go")


# A line that says what somebody brought home is a what-shall-I-do-with-it line: "i bought a
# chicken" and "i picked up some leeks" were a stock ack, and the food is the question. Only
# when the line also names something in the kitchen, so "i bought a car" stays where it is.
BOUGHT_PHRASES = ("i bought", "i've bought", "ive bought", "just bought", "i got a",
                  "i got some", "picked up a", "picked up some", "i brought home",
                  "we bought", "we got a")


# The phrases that ask what to cook, as opposed to saying what is in the kitchen ("i've got two
# cats, pickle and bean"). A line of these can carry a meal question out of another topic; a line
# that only says what it has cannot.
MEAL_ASK_PHRASES = MEAL_WANTS + ("what can i do with", "what do i do with", "what to do with",
                                 "use up", "using up", "any ideas", "ideas", "idea", "got left",
                                 "thing to do with", "things to do with",
                    "easiest thing to do with",
                    # "any ideas" and "what else": a follow-up that asks for ideas without
                    # naming a food is still asking what to cook with the one just named.
                    "what else", "anything else", "something else", "any suggestions",
                    "suggestions",
                    # "going soft", "needs using": the food is on its way out, which is a use-it-up
                    # question even when the line ends there.
                    "going soft", "gone soft", "going off", "on its way out", "needs using",
                    "to use up", "left over", "leftover",
                    # People say it of a bag of things, not one: "mushrooms on their way out",
                    # "the apples past their best". Same question, so the same answer.
                    "on their way out", "on the way out", "past its best", "past their best",
                    "need using", "needs eating", "going over", "starting to go",
                    # A surplus is the same question as a leftover: "i have too much mint",
                    # "i have a lot of mint" and "i have a glut of courgettes" all ask what to
                    # do with a food that is about to go over. The reading of the line does not
                    # always name the food as the subject (mint is also a word for money and for
                    # mint condition), so a line that says too much of something reaches the
                    # food tables on the surplus words alone.
                    "too much", "too many", "a lot of", "lots of", "loads of", "plenty of",
                    "glut of", "overrun with", "spare ")


# "How do I use up the spinach" is the same question as "use up the spinach": the "how" is how
# people start it, not a request for a method, and the use-up words are the whole ask. Only a
# line whose sole technique word is that opening "how" is read this way, and only when it says
# use-up: "how long does leftover rice keep" and "how do i reheat chicken" are other rows'
# questions and still stand the table down. bot/knowledge/meals.py reads its leftover row the
# same way, for the same reason.
USE_UP_ASKS = ("use up", "using up", "use it up", "use them up", "use this up",
               "use that up", "use these up", "use those up", "to use up", "uses up",
               "use the rest", "what can i do with", "what do i do with", "what to do with",
               "what can i make with", "what can i cook with", "what should i do with")


# "my four year old will only eat bread and cheese" names bread and cheese, but it is not a
# question about what to cook with them: it is a worry about a child who eats nothing else, and
# a toastie recipe answers the wrong thing. Read as a meal question, `eat` is enough of a cue on
# its own, so the shapes that say someone is *restricted* to a food have to be taken back out.
RESTRICTED_EATING = (
    "only eat", "only eats", "only ate", "only ever eats", "will only eat",
    "will only eats", "only drink", "only drinks", "wont eat", "won't eat",
    "will not eat", "wont touch", "refuses to eat", "refuse to eat", "refuses to touch",
    "eats nothing but", "eat nothing but", "eats hardly anything", "lives on",
    "fussy eater", "picky eater", "is that normal", "is it normal",
)


# An illness is not an ingredient: "i have chicken pox and a fever" names the word chicken, but
# the person is not asking what to cook with chicken, and the health answers own those lines.
# "a cold" and "a temperature" are phrases because both words have ordinary cooking senses.
# Things a food is used for that are not eating: crafts, decorations and games.
ACTIVITY_PHRASES = ("easter egg", "easter eggs", "play dough", "playdough", "decorate", "decorating",
                    "dye ", "dyed", "paint the", "painted", "craft", "costume", "trick or treat",
                    "stocking filler", "advent calendar", "science experiment", "volcano")


# A line that says it wants to make the thing itself names the food as the thing being made, not
# as something to cook with. The idea table answered all of these with a dinner: "can i make my own
# yoghurt from milk" was a raita, "can i make my own cheese" an omelette, "can i make my own cream
# cheese" macaroni cheese, "can i make my own butter" a cheese toastie and "can i make my own baked
# beans" a baked potato. The making rows answer them (butter, ice cream, pasta, a soft cheese,
# kefir, ketchup and yoghurt have one), and a food with no making row gets the honest hedge rather
# than a dinner nobody asked for.
MAKING_IT_YOURSELF_PHRASES = ("make my own", "make our own", "making my own", "making our own",
                              "made my own", "made our own", "make it myself",
                              "make them myself", "make it ourselves", "make them ourselves",
                              "make your own", "making your own", "from scratch")


ILLNESS_PHRASES = ("a cold", "my cold", "his cold", "her cold", "got a cold", "a temperature",
                   "runny nose", "sore throat", "feel sick", "feeling sick", "being sick")


FOOD_SAFETY_RULES = (
    "Four things do most of the work: wash your hands before you cook and after you touch raw "
    "meat; keep raw meat and fish away from anything you eat raw - its own board, the bottom "
    "shelf of the fridge; cook meat right through and reheat leftovers until they are piping "
    "hot; and get anything that should be cold into the fridge within two hours, rice within "
    "the hour. The fridge wants to be 5C or below, and a use-by date only holds while the pack "
    "has stayed cold.")


# A line asking whether something is still all right to eat is a food-safety question, not a
# request for a recipe, and the words for it are phrases rather than single words.
PROBLEM_PHRASES = ("from frozen", "still frozen", "when frozen", "cook it frozen", "is it frozen",
                   "still ok", "ok to eat", "okay to eat", "gone off", "left out", "off the "
                   "counter", "is it ok", "is it safe")


# "theres nothing in", "no food in the house": the same question as a full fridge, asked the
# other way round, and the useful answer is a short shopping list plus what it makes tonight.
EMPTY_PHRASES = ("no food", "nothing to eat", "nothing in the fridge", "nothing in the cupboard",
                 "nothing in the cupboards", "nothing in the kitchen", "bare cupboard",
                 "cupboard is bare", "cupboards are bare", "empty fridge")


# "whats for dinner when theres nothing in": the meal words are already in the line, so the
# vaguer forms are enough here.
EMPTY_ASK_PHRASES = ("nothing in", "nothing left in the", "nothing at all in",
                     "nothing in the house")


EMPTY_KITCHEN = ("An empty kitchen still makes supper: pasta with a tin of tomatoes and garlic, "
                 "eggs on toast, or rice with a tin of beans and chilli. The shop that fixes it is "
                 "short and cheap: eggs, pasta, rice, tinned tomatoes, a tin of chickpeas or beans, "
                 "onions, frozen peas, cheese, bread and milk. Those cover twenty dinners between "
                 "them, and the frozen and tinned things keep for months.")


# "i havent got fresh tomatoes" is the same question the other way round: what they have run out
# of is the form they named, so the answer is what stands in for it.
OUT_ASKS = ("havent got", "havent", "dont have", "didnt have", "ran out", "run out", "out of",
            "no fresh")


OUT_OF_FRESH = ("Out of fresh {food}, tinned or frozen is the stand-in: tinned is the better one "
                "in a sauce, drained and given 10 minutes to lose the tinny edge, and frozen goes "
                "in straight from the bag for a soup or a stew. Only a salad really wants it fresh.")


# The same question the other way round for every form, not only the fresh one: what they have
# run out of is the form they named, so the answer is what stands in for it. "i havent got any
# tinned tomatoes" was answered "Tinned tomatoes, yes: drain off the liquid...", which is the
# answer to a question they did not ask, and "weve run out of dried lentils" the same.
OUT_OF_FORM = {
    "fresh": OUT_OF_FRESH,
    "tinned": ("Nothing tinned, so the same food in another form stands in: frozen goes in "
               "straight from the bag with 3 or 4 minutes extra, fresh wants adding later than the "
               "tin would and a taste for salt at the end, and dried beans or chickpeas want "
               "soaking overnight and 40 minutes in the pan. For tomatoes, passata, a carton of "
               "chopped ones or a spoon of puree does the tin's job."),
    "frozen": ("Nothing in the freezer, so fresh does the same job: it cooks faster and brings "
               "less liquid, so add it later than the recipe says and taste for salt at the end. "
               "Tinned works in anything simmered, and dried wants soaking first."),
    "dried": ("No dried {food}, so tinned is the stand-in: it is already cooked, so it goes in for "
              "the last 10 minutes rather than at the start, and a tin is roughly what 100g of "
              "dried would have given. Frozen needs no soaking either."),
    "jarred": ("No jar of {food}, so the fresh or frozen version does the job: a jar is drained "
               "and rinsed only because it is salty, so taste at the end and add a little more "
               "salt than you would have. Frozen goes in straight from the bag."),
}


FORM_ADVICE = {
    "frozen": ("Frozen {food}, yes: in a sauce, soup or curry it goes in frozen with 3 or 4 "
               "minutes extra, and anything wet wants thawing and squeezing first or the pan goes "
               "wet. Picked and frozen within hours, it cooks as good as fresh."),
    "tinned": ("Tinned {food}, yes: drain off the liquid, then taste before adding salt, because a "
               "tin is already seasoned, and give beans or chickpeas 10 minutes in a sauce to lose "
               "the tinny edge. Tinned tomatoes blended smooth are passata, and a tin is thinner "
               "than puree, so simmer it down by half to thicken."),
    "dried": ("Dried {food}, yes in anything cooked, at about half the weight of fresh, soaked or "
              "simmered first if it is a pulse or a mushroom and added early so there is time to "
              "soften. Fresh is for the end, where the green taste is the point."),
    "jarred": ("A jar of {food}, yes: drain or rinse before it goes in, and taste at the end, "
               "because a jar is saltier than the same thing cooked from scratch."),
    "fresh": ("Fresh {food} instead of frozen or tinned, yes, but fresh cooks faster and brings "
              "less liquid: add it later than the recipe says and check the salt at the end, "
              "because the tinned and frozen versions carry their own."),
}


# Frozen meat and fish is not the vegetable answer: it is thawed right through, or cooked from
# frozen with longer and slower heat, and the middle is what goes wrong.
FROZEN_MEAT = ("Frozen {food}, yes, but it has to be thawed right through first: overnight in the "
               "fridge on a plate on the bottom shelf, never on the worktop, then cooked as normal. "
               "Straight from the freezer it needs longer and slower, so the middle is done before "
               "the outside dries out. Fish thaws in a few hours and cooks in minutes.")


FROZEN_FRUIT = ("Frozen fruit is picked ripe and frozen within hours, so out of season it beats "
                "the fresh punnets: use it from frozen in a crumble, a smoothie or on porridge, "
                "or half thawed in yoghurt. It goes soft as it thaws, so it will not hold its "
                "shape in a tart; roast it from frozen with a spoon of sugar if you want it whole.")


# "without cheese", "no tomatoes", "off dairy": the ingredient named is the one to leave out,
# so a line that rules something out must not be answered with a dish that needs it.
# The foods a form question is actually asked about: fresh, frozen, tinned or dried is a real
# choice for these and not for a loaf or a jar of curry paste. The reply still reads any pantry
# food, this is only what the key names, so one entry rather than one per food.
FORM_FOODS = ("spinach", "mushroom", "tomato", "pea", "sweetcorn", "bean", "chickpea", "lentil",
              "fish", "salmon", "prawn", "chicken", "mince", "turkey", "bacon", "potato",
              "onion", "carrot", "broccoli", "kale", "cabbage", "cauliflower", "courgette",
              "aubergine", "squash", "pepper", "leek", "apple", "banana", "lemon", "berry",
              "peach", "mango", "fruit", "herb", "herbs", "garlic", "chilli", "ginger",
              "blackberry", "raspberry", "strawberry", "blueberry", "cod", "haddock", "tuna",
              "sardine", "anchovy", "coconut", "date", "fig", "plum", "cherry", "gooseberry",
              "rhubarb", "gooseberries")


# A refusal is often a phrase, and the words that make it one sit two or three back from the
# food: "im not a fan of lentils" and "i cant stand halloumi" were read word by word, the food
# stayed in the pantry, and the idea that came back was a lentil dhal and a plate of halloumi.
RULING_OUT_PHRASES = ("not a fan of", "not a fan", "not keen on", "not fussed about",
                      "cant stand", "can t stand", "cannot stand", "sick of", "tired of",
                      "bored of", "fed up of", "fed up with", "had enough of", "gone off",
                      "allergic to", "instead of", "hate", "hates", "dislike", "dislikes",
                      "loathe", "not into")


REFUSAL_REACH = 6       # how far back from the food a refusal phrase is still about it


# What a stated diet rules out. "eggs and spinach, i'm vegan" names its ingredients and then
# says one of them cannot be used, so a dish built on eggs is no answer even though eggs were
# named. The classes are coarse on purpose: a diet question is asked about whole foods.
FOOD_CLASSES = {
    "bacon": ("meat",), "chicken": ("meat",), "ham": ("meat",), "mince": ("meat",),
    "sausage": ("meat",), "prawn": ("shellfish", "fish"), "salmon": ("fish",),
    "tuna": ("fish",), "egg": ("egg",), "butter": ("dairy",), "cheese": ("dairy",),
    "cream": ("dairy",), "milk": ("dairy",), "yoghurt": ("dairy",),
    "bread": ("gluten",), "pasta": ("gluten",), "flour": ("gluten",),
    "tortilla": ("gluten",),
}


DIETS = (
    (("vegan", "plant based", "plantbased", "no animal"),
     ("meat", "fish", "shellfish", "dairy", "egg")),
    (("vegetarian", "veggie", "vego", "no meat"), ("meat", "fish", "shellfish")),
    (("pescetarian", "pescatarian"), ("meat",)),
    (("dairy free", "dairyfree", "lactose", "no dairy", "milk free"), ("dairy",)),
    (("gluten free", "glutenfree", "coeliac", "celiac", "no gluten", "wheat free"),
     ("gluten",)),
)


NEGATION_REACH = 3     # how many words before the ingredient still count as ruling it out


COOKED_REACH = 3       # how far back a "leftover"/"roast"/"mashed" still describes the ingredient


# The line read for its ingredients, worked out once for the words: a dozen rows about dishes
# and recipes ask the same question about the same line, so the second ask reads the card.
_READ_FOR_INGREDIENTS = {}


_READ_FOR_INGREDIENTS_KEEP = 4000


# What stands in for the meat when the line says they eat none of it. Saying the swap out loud
# is most of the help: "no meat please, what can i cook with chicken" is a person who wants a
# curry, not a lecture, and the rest of the ingredients still make the dish.
# What to cook instead, said without naming the food they have ruled out: main's rule is that a
# reply never says the word back to somebody who has just said they do not eat it.
MEAT_SWAPS = {"chicken": "chickpeas or tofu", "turkey": "chickpeas or lentils",
              "mince": "lentils or chickpeas", "sausage": "chickpeas or halloumi",
              "bacon": "mushrooms and smoked paprika", "ham": "mushrooms",
              "pork": "mushrooms or chickpeas", "lamb": "chickpeas or lentils",
              "beef": "lentils or mushrooms", "steak": "mushrooms or aubergine",
              "chorizo": "smoked paprika and mushrooms",
              "tuna": "chickpeas", "salmon": "chickpeas or tofu", "prawn": "chickpeas",
              "fish": "chickpeas or tofu"}


_VEG_PHRASES = ("no meat", "meat free", "meat-free", "without meat", "dont eat meat",
                "don't eat meat", "doesnt eat meat", "does not eat meat", "eat no meat")


_VEG_DINNER = ("A red lentil dhal is the dinner I would cook: lentils, an onion, garlic, cumin "
               "and a tin of tomatoes simmered 20 minutes, with rice or bread. Or chickpeas and "
               "spinach: fry onion, garlic and spices, add a tin of chickpeas and a tin of "
               "tomatoes, simmer 15 minutes and stir spinach through at the end.")


# The price is only worth saying when money is the question: "what should i cook tonight" from a
# vegetarian is not asking what dinner costs.
_VEG_DINNER_CHEAP = " Both cost about 50p a head."


def _plain_words(text):
    """The words of a line, without the comma or full stop a word can carry at the end."""
    return re.findall(r"[a-z']+", str(text).lower())


def _recent_user_turns(memory, count=4):
    """What the person typed in the last few turns, oldest first."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return []
    return [str(turn.get("user") or "") for turn in turns[-count:]
            if isinstance(turn, dict)]


# "with no eggs" is the cupboard's absence, not a person's refusal: the line is asking what to
# use instead, which the substitute entry answers. Only a line that names a meal or a pan sends
# it to the dinner picker, and then the dish leaves the food out as it does for a refusal.
AND_NO = ("with no", "with none", "with not much", "with only")


# A food the kitchen has none of is a different question: "no cheese in the house what can i
# make" already had a dinner, and "im out of butter" is the swap entries' line. Only a person
# refusing a food is this answer's business.
SHORTAGE_WORDS = ("ran out", "run out", "out of", "none left", "nothing left", "havent got",
                  "haven't got", "dont have", "don't have", "have no", "has no", "not got",
                  "no more", "all gone",
                  "in the house", "in the cupboard", "in the fridge", "in the freezer")


# A person changing one thing in a dish they mean to keep is asking what stands in for it, which
# the substitute entries answer. A dish that has none of the thing in it is no answer at all:
# "no buttermilk, what else can i use" came back as a potato hash, which is a dinner for a line
# about baking. Only "what can i use" needs care, because "what can i use it for" is asking for a
# dish and its "it" is the food in hand.
_STAND_IN_ASK = ("instead", "instead of", "substitute", "substitutes", "sub for", "sub for it",
                 "swap", "swaps", "replace", "replacement", "in place of", "stand in for",
                 "what else can i use", "what else could i use", "what do i use instead")


def _reads_as_news(understood, clean=""):
    """True when the line is news of a meal that happened, not a request for one.

    "we had dinner with no potatoes" names a meal word and a food left out, like "dinner with
    no potatoes please", and only the tense tells the two apart. The meal table already reads
    that difference, so its reading is the one used here.
    """
    from ..knowledge import meals

    return meals.reads_as_news(understood, clean)


# Two foods on either side of an "or" are a choice, not a pair to cook together: "butter or oil"
# and "chicken or lamb" name two things and ask for one of them. The choice words are what says
# so - a line that merely mentions both ("potatoes and carrots", "chicken, then the butter") is
# still one dinner, and the two ideas below are right for it.
_CHOICE_WORDS = ("should i", "shall i", "do i use", "can i use", "could i use", "which",
                 "better", "instead", "rather", "or is", "or would", "or should", "or do i",
                 "what about", "worth using", "go for", "stick to")


# The other half of a choice is not always a food: "butter or oil" and "rice or pasta" pick
# between two things, and oil, water, stock or wine are what a pan is cooked in rather than an
# ingredient of its own, so the pantry has no row for them.
_COOKING_MEDIUM = ("oil|olive oil|water|stock|wine|milk|cream|margarine|ghee|lard|dripping|"
                   "suet|vinegar|lemon|honey|syrup|sugar|salt|pepper|flour|cornflour|"
                   "butter|yoghurt|juice|sauce|gravy|rub|marinade|foil|paper|trays?|tins?")


# "How long does that take?" after a meal idea is a question about the answer just given, so the
# time it already stated is the answer. Numbers come out of the reply in words or digits ("ten
# minutes", "1 hour 40"), because the dish lines are written both ways.
_NUMBER_WORD = (r"\d+|an?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|"
                r"twenty|thirty|forty|fifty|sixty|ninety")


COOKED_KEEPING = ("Once it is cooked, cool it within two hours and keep it covered in the fridge: "
                  "it keeps 3 to 4 days, and you can reheat it once, piping hot all the way "
                  "through. Anything with rice or chicken should go in the fridge straight away "
                  "rather than sit out.")


def _this_line_only(understood):
    """This turn's line and not the turns before it, lower-cased, for the dish-on-its-own test.

    `_said_so_far` puts the earlier turns in front for the exclusions, and "im vegetarian" then
    "lasagne" would read as a line with two subjects in it.
    """
    words = understood.get("words")
    if isinstance(words, list) and words:
        return " ".join(str(word).lower() for word in words)
    return str(understood.get("clean") or "").lower()


# A table of methods answers a line that asks for one ("how do i make scones", "give me a chilli
# recipe") or names the dish and what to do with it ("chilli con carne recipe"). It does not
# answer news ("i made a big chilli tonight and theres loads left"), a feeling ("i love lasagne")
# or a verdict on the last one ("my chilli was too spicy"): those lines ask for the leftovers,
# keeping or seasoning answer, and each of them already has one on main.
_RECIPE_ANSWERS = ("question", "request", "statement")


# A dish named in a line is the dish, not the foods it is made of. "spaghetti bolognese recipe"
# was answered with aglio e olio and "should i do a spag bol tonight" with mac and cheese, while
# "how do i make spag bol" got a shrug: the ingredient table reads "spaghetti" as a food to cook
# with and hands back whichever pasta dish it holds, and the dish the person named is not an
# ingredient at all. The recipe table is the list of dishes this kitchen knows by name, so a line
# that names one has a subject of its own, and the tables that answer foods rather than dishes
# (the pantry's ideas, a free evening, a day out) stand down for it.
#
# A food that is also a dish - bread, prawns, sprouts - stays the pantry's: "what can i make with
# prawns" is a use-up question and the ingredient table is the one that answers it.
_USE_UP_WORDS = ("leftover", "leftovers", "left over", "left from", "use up", "using up",
                 "used up", "spare", "stale", "already made", "goes off", "go off",
                 "out of date")


# A line that points back at food instead of naming it ("what can i make with them", "what
# should i do with it"). The food is the one a turn or two earlier named, so the pantry answers
# for that food, and it does not serve the same dish it just served.
POINT_BACK = ("with them", "with it", "with those", "with these", "with that",
              "make with them", "make with it", "make with those", "make with these",
              "do with them", "do with it", "do with those", "do with that",
              "use it up", "use them up", "use those up", "use these up", "use that up",
              "use up the rest", "using it up", "using them up", "using those up",
              "using these up", "using that up", "using up the rest",
              "out of them", "out of it", "what about them",
              "what about it", "else can i do with", "else can i make with",
              "else could i do with", "else to do with", "else can i use",
              # A bare ask for ideas, after a turn that named food, is the same follow-up: "i
              # have some kale" then "any ideas" was answered "tell me what you've got so far".
              "any ideas", "any idea", "any other ideas", "any suggestions", "suggestions",
              "what else", "anything else", "something else", "what do you suggest")


# A follow-up that asks what goes *beside* the food is not a question about the food itself:
# pointing it back at the food answered it with the cooking of that food again ("what can i
# serve with it" after chicken got roast chicken thighs a second time, thighs for the breasts
# the person had said).
PAIRING_WORDS = ("goes with", "go with", "to go with", "serve with", "served with",
                 "serve on the side", "on the side", "side dish", "side dishes",
                 "what can i serve", "what should i serve", "what to serve",
                 "pair with", "pair it with", "pairing", "accompany")


# A line that asks for a second idea has already had the first one, so it is only answered when
# the table has a *different* dish for the food: the same one again behind "The one I'd go back
# to" reads canned the second time (cream-orange, leeks over three turns).
SECOND_IDEA = ("what else", "anything else", "something else", "another idea",
               "another one", "any other", "other ideas", "what other")


# The food a turn named may be the wrong subject to point back at: something that is going off,
# out of date, or that made somebody ill is a safety question, not a proposal for dinner.
POINT_BACK_STOP = ("going off", "gone off", "went off", "off the", "use by", "best before",
                   "out of date", "still ok", "ok to eat", "okay to eat", "safe to eat",
                   "mouldy", "moldy", "mould", "mold", "smells", "smelly", "slimy",
                   "defrost", "raw", "undercooked", "allergic", "food poisoning", "vomit",
                   "diarrhoea", "threw up", "sick after", "my cat", "my dog", "the cat",
                   "the dog")


def recent_replies(memory, count=2):
    """The last few replies the bot gave, newest last, so a follow-up is not a repeat."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ()
    said = [str(turn.get("bot") or "") for turn in turns[-count:] if isinstance(turn, dict)]
    return tuple(said[-count:])


def _words_of(text):
    return re.findall(r"[a-z0-9']+", str(text or "").lower())


# --- feeding yourself through the week ------------------------------------
# Not a recipe and not a keeping question: how to get dinners out of a fridge on a Tuesday. The
# questions are "how do i meal prep", "what can i batch cook", "how do i stop wasting food", and
# they are answered as a plan rather than as a dish, so every entry here has a key of its own and
# stands down for a line that names a food (the pantry table and the dish entries know that food).
_PLANNED_FOOD = ("chicken", "beef", "pork", "lamb", "mince", "fish", "salmon", "pasta", "rice",
                 "curry", "chilli", "soup", "stew", "bread", "cake", "potato", "potatoes",
                 "courgette", "spinach", "chickpeas", "lentils", "eggs", "cheese", "milk")


# --- halving and doubling a recipe -------------------------------------
# The answer opens with the operation the line asks about: telling someone who asked how to
# double a recipe to "halve every ingredient" answers a question they did not ask.
SCALE_DOWN = (
    "Halve every ingredient and leave the oven temperature alone: the tin goes one size down if "
    "the batter looks thin in it, and start checking five minutes early. Cooking time does not "
    "halve - a smaller cake or loaf takes about two thirds as long - so test it with a skewer "
    "sooner than you think. Halve the raising agent exactly, and if the sum gives you half an "
    "egg, beat one and use half of it.")


SCALE_UP = (
    "Double every ingredient and use a bigger tin rather than a deeper one, so the middle cooks "
    "at the same speed. It takes longer than twice the time is worth assuming: start checking at "
    "the original time and give it another ten or fifteen minutes if the skewer comes out wet. "
    "Salt, spice and raising agent go up by less than double, to taste, and a big batch is better "
    "split between two tins than crammed into one.")


SCALE_UP_WORDS = ("double", "doubling", "doubled", "times two", "scale up", "for 20",
                  "for twenty", "for 30", "for a crowd", "for a big group", "bigger batch")
