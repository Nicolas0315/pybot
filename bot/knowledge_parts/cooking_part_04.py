"""Part 4 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

from ..knowledge.lookup import find
# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.cooking_tables import (
    FREEZE_FACTS, FOOD_CALORIES, FOOD_NUTRIENTS, FOOD_CALORIE_MEALS,
)
from .cooking_part_02 import (
    _same,
)


# How much milk sugar is in the everyday dairy foods. A dairy-free swap is the wrong answer for a
# lactose intolerance: the sugar is what is missing from aged cheese and butter, and it is the
# whole of a glass of milk, so the answer names the level rather than saying no.
LACTOSE_LOW = ("cheese", "butter", "cream")


LACTOSE_HIGH = ("milk", "yoghurt", "yogurt", "ice cream")


_LACTOSE_SAYS = {
    "cheese": ("Yes, usually: ageing eats almost all of the lactose, so a hard cheese such as "
               "cheddar or parmesan is the dairy food most people with a lactose intolerance can "
               "eat without trouble. Soft cheese - brie, cottage cheese, ricotta, mozzarella - "
               "has more of it left, so try a small amount with a meal first."),
    "butter": ("Yes: butter is mostly fat with only a trace of milk sugar left in it, so a normal "
               "spread is fine for most people with a lactose intolerance. Cream and ghee are the "
               "same idea; milk, yoghurt and ice cream are the ones with real lactose in them."),
    "cream": ("Yes, in a small amount: cream has far less lactose than milk, so a spoonful in a "
              "sauce is usually fine. Milk, soft cheese, yoghurt and ice cream are where most of "
              "the lactose is."),
    "milk": ("Not much of it, and not on its own: milk is where most of the lactose is, so a "
             "small glass with a meal is the test, and lactose-free milk is ordinary milk with the "
             "sugar already split - it does the same job in tea, on cereal and in cooking."),
    "yoghurt": ("Often yes: live yoghurt is easier than milk because the cultures do part of the "
                "digesting, so a small pot with a meal is usually fine. A big tub on its own, or "
                "ice cream, is where people notice it."),
    "yogurt": ("Often yes: live yogurt is easier than milk because the cultures do part of the "
               "digesting, so a small pot with a meal is usually fine. A big tub on its own, or "
               "ice cream, is where people notice it."),
    "ice cream": ("Not much of it: ice cream is milk and cream with sugar on top, so it is one of "
                  "the higher ones. A couple of spoons after a meal is a different thing from a "
                  "whole tub, and lactase tablets taken with the first mouthful cover it."),
}


def _bans(names, idea, banned):
    """True when an idea needs, or tells them to add, a food the eater avoids."""
    for name in names:
        if name in banned:
            return True
        if any(part in banned for part in name.split()):
            return True
    text = idea.lower()
    return any(re.search(r"\b" + re.escape(word) + r"\b", text) for word in banned)


# A dairy word after one of these is not dairy: "coconut milk", "peanut butter" and "butter
# beans" are foods a person avoiding milk can eat, and reading them as the dairy would take a
# good answer away from them.
# Gluten is not checked after the swap, only swapped: "stirred through pasta" and "mashed onto
# toast" are a job a coeliac can still do - with the gluten-free version - where declining the
# card would have left them with a shrug. The word is only swapped when the line itself did not
# name it: someone asking about leftover pasta is asking about pasta.
GLUTEN_WORDS = ("pasta", "toast")


SWAP_WINDOW = 34


def _first_sentence(idea):
    """One idea cut to its opening sentence.

    Two ideas side by side have to stay a short answer: "got mince and rice" is two lines of
    cooking, not two paragraphs. The whole idea is still there when it answers on its own.
    """
    parts = re.split(r"(?<=[.!?])\s+", idea.strip(), maxsplit=1)
    return parts[0] if parts else idea


def _lentils(memory, understood):
    """Lentils by colour, because the times and the texture are the whole question."""
    return ("No soaking: rinse and simmer in plenty of water. Red lentils split and go soft in 15 "
            "to 20 minutes, which soups and dal want; green or brown stay whole at 20 to 25; puy "
            "take about 25 and hold their shape in salads. Salt near the end, not at the start, and "
            "taste at 15 minutes: a minute either way is firm against mushy. One mug of dried makes "
            "two cooked, and a bay leaf and half an onion in the water do more for flavour than "
            "anything added later.")


# A pet is not a dinner. The pantry keys the food ("rabbit", "guinea pig") and cannot tell the
# animal in the hutch from the one at the butcher's, so "my rabbit ate the leftovers" was given a
# braise and "my rabbit has eaten the leftovers" the same. An animal the line owns, or one that
# has eaten something, is a pet question: the pets rows answer it, and the kitchen stands down.
PET_ANIMALS = ("rabbit", "rabbits", "bunny", "bunnies", "guinea pig", "guinea pigs", "guineapig",
               "hamster", "hamsters", "gerbil", "gerbils", "chinchilla", "chinchillas",
               "degus", "degu", "hedgehog", "hedgehogs", "tortoise", "tortoises", "parrot",
               "parrots", "budgie", "budgies")


_PET_OWNED = ("my ", "our ", "pet ", "the pet ")


_PET_EATING = ("ate", "eaten", "eats", "chewed", "chewing", "nibbled", "nibbling", "got into",
               "stole", "stolen", "swallowed")


# An order question names an ingredient, so every "what about <food>" meal path reads it as "what
# can I make with <food>": in a tea thread the follow-up "what about milk first or last" was
# answered "A white sauce: butter and flour cooked a minute, then milk whisked in". The person is
# asking what goes in first, not what to cook, so the dinner rows stand down on the wording that
# asks for a sequence and leave the line to the row that knows the drink or the dish.
_ORDER_NOT_A_MEAL = ("first or last", "last or first", "first or after", "before or after",
                     "in first", "in last", "go in first", "goes in first", "go in last",
                     "goes in last", "which goes in", "which one goes in", "which first",
                     "in what order", "what order", "order do i", "either way round",
                     "milk first", "milk last")


# The other half of the same subject: a line about the milk that goes in a cup of tea is a drink
# question, and "is oat milk good in tea" was answered with porridge because the dish table read
# the two foods in it (oats and milk) as a pair to cook.
_MILK_IN_TEA_NOT_A_MEAL = ("in tea", "in my tea", "in the tea", "in a cup of tea",
                           "in a mug of tea", "in a brew", "in my brew", "in the brew",
                           "for a cup of tea", "for my tea with milk")


def _a_brew_not_a_dinner(line):
    """True when the line is about the order or the milk of a brew rather than what to cook."""
    low = " " + str(line or "").lower() + " "
    if any(f" {phrase} " in low for phrase in _ORDER_NOT_A_MEAL):
        return True
    if " milk " not in low and not low.startswith(" milk"):
        return False
    return any(f" {phrase} " in low or f" {phrase}." in low
               for phrase in _MILK_IN_TEA_NOT_A_MEAL)


def _an_order_not_a_dinner(line):
    """True when the line asks which thing goes in first rather than what to cook."""
    low = " " + str(line or "").lower() + " "
    return any(f" {phrase} " in low for phrase in _ORDER_NOT_A_MEAL)


# A plant is not a dinner. The pantry keys the food and cannot tell the lemon in the fruit bowl
# from the one in the ground: "i bought a lemon tree" was answered "Lemon and garlic chicken, or
# just a squeeze over the finished dish", an apple tree got the stewed apple and a fig tree the
# figs. The words that put the food in the ground or on the windowsill belong to the garden rows,
# so a line that names one stands this table down - unless it also asks what to cook, because
# "what can i cook with the tomatoes from my plant" is still a dinner.
_PLANT_NOT_A_DINNER = ("tree", "trees", "bush", "bushes", "shrub", "shrubs", "sapling",
                       "saplings", "seedling", "seedlings", "plant", "plants", "potted",
                       "bare root", "bare-root", "root ball", "compost", "greenhouse",
                       "allotment", "windowsill", "window sill", "cuttings", "cutting")


_PLANT_GARDEN_VERB = ("bought", "buy", "buying", "planted", "planting", "grow", "growing",
                      "grew", "repot", "repotted", "died", "dying", "dead", "water", "watering",
                      "feed", "feeding", "prune", "pruning", "sow", "sowing", "sowed",
                      "transplant", "potted on", "flowering", "fruiting")


_PLANT_COOK_ASK = ("cook", "cooks", "cooking", "recipe", "recipes", "make", "makes", "making",
                   "eat", "eating", "dinner", "supper", "lunch", "roast", "bake", "baking",
                   "fry", "boil", "serve", "dish", "meal", "use up", "use them", "use it")


# A source only makes the food the subject when the line asks what to do with it. "the apples on
# the tree are rotten" names the same source and is a tree question, so the ask is the second half
# of the test.
# A herb bought as a plant is the windowsill's, not the garden's: nobody grows "a herb" outside.
_PLANT_KITCHEN_PLANT = ("herb", "herbs")


# A plant that is carrying the fruit has stopped being the subject: "my fig tree has fruit what do
# i do with them" is the figs in the kitchen, and the bare-root month is no answer to it.
_PLANT_BEARS = ("has fruit", "have fruit", "had fruit", "with fruit", "full of fruit",
                "loaded with fruit", "in fruit", "covered in fruit", "bears fruit",
                "bearing fruit", "producing fruit")


_PLANT_DO_WITH = ("do with", "use", "using", "used up", "glut", "too many", "loads of",
                  "all these", "all this", "all the", "bumper", "plenty of", "left over",
                  "what can i", "what should i", "what do i")


def _the_garden_has_this_plant(line):
    """Whether a garden row takes this line, so the pantry may stand aside for it.

    Asked of the garden's own entries rather than guessed from the words: the plant table stood
    down on any plant word, and where the garden had no row the turn landed on an echo. The
    reading is built here because only the clean line is in hand, which is all the keys need.
    """
    from ..knowledge.garden import ENTRIES as _GARDEN_ENTRIES
    text = str(line or "")
    words = tuple(word for word in re.split(r"[^a-z0-9']+", text.lower()) if word)
    reading = {"clean": text, "text": text, "words": words, "kind": "ask"}
    return find(reading, entries=_GARDEN_ENTRIES) is not None


# A plant that came home from the shop as a bush, a bare-root tree or a pot is not a thing to
# cook, whether or not the garden table has a row that takes the line yet: "i bought a blueberry
# bush" was answered with a blueberry compote when the garden's own table had nothing to say.
# The woody and the bought shapes are the test together, so a named herb in a pot stays the
# kitchen's ("i bought a basil plant") and a tomato glut stays the pantry's.
_PLANT_WOODY = ("tree", "trees", "bush", "bushes", "shrub", "shrubs", "sapling", "saplings",
                "bare root", "bare-root", "root ball", "climber", "climbers", "hedge", "hedges")


_PLANT_PURCHASE = ("bought", "buy", "buying", "picked up", "came home with", "brought home",
                   "arrived", "delivered", "got it home")


def _a_plant_from_the_shop(line):
    """A woody plant that has just been bought: the garden's, even when no row answers yet."""
    low = " " + str(line or "").lower().replace("'", " ") + " "
    return (any(f" {word} " in low for word in _PLANT_WOODY)
            and any(f" {word} " in low for word in _PLANT_PURCHASE))


# A feeding question about a hutch pet is the pets table's, not the pantry's. "Can rabbits eat
# lettuce" names two foods, so the table below answered it with a braise and a lettuce idea: the
# animal was read as the dinner. The pantry cannot see the difference between the rabbit in the
# hutch and the one at the butcher's, so the shape of the question decides it - an animal that is
# the one eating, or a food weighed up for it, is not a thing to cook.
_FEEDING_ANIMALS = (r"rabbits?|bunn(?:y|ies)|guinea\s?pigs?|hamsters?|gerbils?|chinchillas?|"
                    r"degus?|hedgehogs?|tortoises?|budgies?|parrots?")


# A line that is about cooking the animal is the meat, however it is worded: "a good recipe for
# rabbit" is a plate, not a hutch, and "safe to eat" is the shopper's question.
FEEDING_NOT_FOOD = ("recipe", "recipes", "roast", "braise", "casserole", "stew", "fry", "bake",
                    "butcher", "joint", "dinner", "supper", "meal", "chef", "oven", "pan",
                    "sous vide", "marinade", "rub")


def _pet_not_dinner(line):
    """True when the line is about somebody's pet rather than about what to cook."""
    low = " " + str(line or "").lower() + " "
    animals = [animal for animal in PET_ANIMALS if f" {animal} " in low]
    if not animals:
        return False
    if any(f" {owner}{animal} " in low for animal in animals for owner in _PET_OWNED):
        return True
    # "rabbit ate the leftovers" is a pet too: a dish is not said to eat
    return any(f" {verb} " in low for verb in _PET_EATING)


# The animals in the pantry that are also bought as meat. Main's `_pet_not_dinner` covers the ones
# nobody eats - a hamster, a tortoise, a budgie - and a hutch pet; a duck, a goose, a pigeon, a quail,
# a pheasant and a deer are both, so the possessive alone does not settle them and a word that puts
# the animal in the house does. "My duck is called donald" is not a dinner, and "what can i cook with
# my duck in the room" was answered with duck breast on c955e20.
PET_MEAT_ANIMALS = ("duck", "goose", "gander", "pigeon", "quail", "pheasant", "deer")


# A word that says the bird or the beast came from a butcher, a shoot or a freezer is the meat.
PET_NOT_FOOD = ("bought", "butcher", "from the shop", "from the market", "farmers market",
                "in the freezer", "frozen", "from the farm shop", "shot", "from a shoot",
                "joint", "breast", "thigh", "leg", "casserole")


# A care question about the animal is not a line about cooking it, and neither is the animal that
# has eaten something: "my rabbit ate the leftovers" has the pets answer and no braise in it.
PET_CARE = ("feed", "feeding", "fed", "food for", "called", "named", "care", "vet", "hutch",
            "litter", "breed", "groom", "sick", "ill", "not eating", "wont eat", "won't eat",
            "ate", "eaten", "eats", "chewed", "chewing", "nibbled", "nibbling", "got into",
            "stole", "stolen", "swallowed")


PET_COOKING_ASK = ("cook", "make", "recipe", "dinner", "tea", "supper", "meal", "roast",
                   "braise", "use up")


ANY_BREAKFAST = ("Porridge with a spoon of peanut butter and a banana, eggs on toast, or yoghurt "
                 "with fruit and oats: any of the three takes under ten minutes and keeps you going "
                 "until lunch. If mornings are rushed, boil an egg the night before and take a "
                 "piece of fruit with it.")


# "keeps you going until lunch" is the plain answer's own wording, and it costs the follow-up:
# after a breakfast that says "lunch", "and for lunch" shares its only word with the sentence
# that said it and the breakfast is given again. The diet answers say "all morning" instead, so
# the lunch question that comes next reaches the lunch answer.
BREAKFAST_TAIL = (": any of the three takes under ten minutes and keeps you going all morning.")


# The packed lunch for someone who has said nothing about what they cannot eat. It is the
# plain entry's own text, kept word for word so the lines with no diet on them read as they
# always have; anyone with a diet gets the same answer read around it (`_lunch_ideas`).
ANY_LUNCH = ("A sandwich or wrap with something filling (cheese, tuna, ham, hummus), fruit, "
             "something crunchy and a drink is a packed lunch in five minutes; cook extra dinner "
             "and take the leftovers in a tub and it is quicker still. Keep anything with meat, "
             "fish, egg or dairy cold until you eat it.")


# What freezes, and what each thing needs: keyed by the food the line names, so "can I freeze
# milk" gets milk's answer rather than a lecture about bags. 3 months is the safe home-freezer
# limit for most things, not the taste limit.
# How long a thing keeps once it is in the freezer, which is a different number from the fridge
# days people ask about. Safe for longer than this; quality is what runs out.
FREEZER_KEEP = ("In the freezer, about 3 months for most things before the quality drops: raw "
                "meat and fish, cooked dishes, soup, stock, bread, cake, cheese and butter. A whole "
                "bird or a joint goes 6 months, blanched veg and fruit 6 to 12, and ice cream 2 to "
                "3. It stays safe long past that, just drier, so write the date on the bag. The "
                "fridge is much shorter: raw meat 1 to 2 days, cooked food 3 to 4.")


FREEZE_ANY = ("Most food freezes well for about 3 months: cool it fast, portion it into bags, press "
              "the air out and write the date on. Defrost in the fridge overnight rather than on the "
              "counter.")


HONEY_BABY = (
    "No honey at all before the first birthday: it can carry botulism spores that a baby's gut is "
    "too young to deal with, and heat does not destroy them, so cooked honey is out too. That "
    "covers honey in porridge, on a dummy or in a homemade cough remedy. From the first birthday it "
    "is fine, so a toddler or an older child can have it.")


HONEY_OLDER = (
    "From the first birthday honey is fine, so a toddler can have it in porridge or a warm drink - "
    "keep the spoon small and brush teeth afterwards, because it is sugar. The one rule is no honey "
    "at all under a year, and that includes cooked honey, because botulism spores survive heat.")


def _honey_age(memory, understood):
    """The age in the line decides which side of the first birthday the answer opens on."""
    text = understood.get("clean") or ""
    if re.search(r"\b(toddlers?|2 year old|3 year old|two year old|three year old)\b", text):
        return HONEY_OLDER
    return HONEY_BABY


_FREEZE_WORD_FORMS = ("freeze", "freezes", "freezing", "frozen", "freezer", "freezers",
                      "freezed", "freezed")


_FREEZE_POINTS_AT = ("it", "this", "that", "these", "those", "them", "the rest", "the other half",
                     "the remainder", "whats left", "what is left", "the spare", "some",
                     "any left", "any spare", "a portion", "the leftovers", "left over",
                     "the whole lot", "the remainder of it")


def _points_at_something(words):
    """True when the line says "freeze it" rather than talking about freezing in general.

    "i can read it fine but freeze when someone talks to me" is a person freezing up, and a
    pointing word in it ("it") would otherwise reach the food answers. A pointer only counts when
    it sits against the freezing word itself - "freeze it", "freezing this", "this freeze", "the
    freezer for it" - and a pointer of two or three words ("the rest", "what is left", "the other
    half") counts as a whole, because those are the words people point with.
    """
    clean = [word.strip(".,!?").replace("'", "").lower() for word in words]
    for at in range(len(clean)):
        for size in (3, 2, 1):
            if " ".join(clean[at:at + size]) not in _FREEZE_POINTS_AT:
                continue
            for step in (-1, -2, size, size + 1):
                i = at + step
                if 0 <= i < len(clean) and clean[i] in _FREEZE_WORD_FORMS:
                    return True
    return False


def _freeze_units(words):
    """Every run of the line's words worth comparing with a food name, up to three words long."""
    units = list(words)
    for size in (2, 3):
        units += [" ".join(words[i:i + size]) for i in range(len(words) - size + 1)]
    return units


def _a_freeze_fact(words):
    """The most specific food freeze fact the words carry, or None."""
    best = None
    for names, fact in FREEZE_FACTS:
        for name in names:
            for at, word in enumerate(_freeze_units(words)):
                if _same(word, name):
                    # a name that is the whole unit beats one that only sits inside it:
                    # "cream cheese" is not the cream row, however the words line up.
                    score = (word == name, len(name.split()), at)
                    if best is None or score > best[0]:
                        best = (score, fact)
    return best[1] if best else None


def _names_one_food(words):
    """The one food name a line carries, or None when it carries two or more.

    "what can i cook with mince and a tin of tomatoes" names two things and is about neither of
    them: the answer for tomatoes (freeze them whole, the skins slip off) is a bad answer to
    "can i freeze the rest" about a ragù, and the plain three-month answer is a true one. Two
    names is a list, so the chat does not name a dish.
    """
    seen = set()
    for names, fact in FREEZE_FACTS:
        for name in names:
            for at, unit in enumerate(_freeze_units(words)):
                if _same(unit, name):
                    seen.add(fact)
                    break
    return next(iter(seen)) if len(seen) == 1 else None


def _the_dish_the_chat_names(memory):
    """The food the person's own last few lines are about, or None: the thing "it" points at.

    "do i need to freeze them" after a line about green beans is a question about beans, and
    "can i freeze it" after bread is bread's question. The line itself names nothing, so the
    dish has to come out of the chat, nearest line first.

    Only the person's lines count. The bot's own reply is where the wrong dish came from: after
    "i have half a bag of potatoes going soft" the reply offered cheese on the mash, and the
    next turn's "could i freeze them" was answered with how to freeze grated cheese. A reply
    also mentions the carcass making stock and the stock answer arrived for a roast chicken.
    """
    try:
        from ..memory import recent
        turns = recent(memory, 4) or ()
    except Exception:
        return None
    for turn in reversed(list(turns)):
        if not isinstance(turn, dict):
            continue
        said = turn.get("user")
        if not isinstance(said, str) or not said.strip():
            continue
        fact = _names_one_food(said.lower().split())
        if fact is not None:
            return fact
    return None


# The one sentence each family needs when it is said alongside a nut allergy: the Plenty list is
# about nuts, and the reply that answers half of a two-allergen line is the fault being fixed.
ALSO_OUT = {
    "shellfish": "And nothing with shellfish in it either: prawns, crab, lobster, mussels, squid, "
                 "and check sauces and stocks for seafood.",
    "soya": "And nothing with soya in it either: tofu, edamame, soya sauce, and check the label "
            "on bread and chocolate.",
}


# --- missing ingredients, and what stands in for them ---------------------
# "What can I use instead of X" is one of the most asked kitchen questions. The words below are
# ways of asking for a stand-in rather than for a dish, and the pantry table reads a line naming
# two ingredients as a "what can I make" question, so it has to be held back for these (see
# SUBSTITUTE_PHRASES in meal()).
# The other half of "what can i use instead of": "i have run out of", "i am out of" and "no
# butter left" are the same question, and they were reaching the swap entries only when the line
# also carried one of the ask words above.
# "no butter left" is "none left", not "left": a bare "left" also reads a quantity question
# ("how much yeast is left in a sachet") as the thing having run out.
_HAVE_NONE = ("havent any", "haven't any", "have got none", "have none", "has none", "got none",
              "there is no ", "there's no ", "there are no ", "none in the house",
              "none in the cupboard", "none at home", "none left at home",
              "nothing in the house", "nothing in the cupboard", "nothing in the fridge",
              "theres none", "there's none",
              "have no egg", "have no eggs", "have no milk", "have no butter", "have no yeast",
              "have no cream", "have no buttermilk", "have no cornflour", "have no flour",
              "have no plain flour", "have no baking powder", "have no sugar", "have no cheese",
              "have no rice", "have no onions", "have no bread")


_OUT_ASK = ("out of", "none left", "nothing left", "empty", "what do i do", "what do i use") \
    + _HAVE_NONE


# A line that asks for a bake with no egg, no butter or no milk in it. Every vegan variant below is
# the same question - "how do i make vegan pastry", "a dairy free sponge", "a cake with no eggs" -
# and the recipes in BAKES all use butter or egg, so the dairy one has to stand down for these.
_VEGAN_ASK = ("vegan", "vegans", "plant based", "plant-based", "dairy free", "dairy-free",
              "dairyfree", "egg free", "egg-free", "eggless", "no egg", "no eggs", "no butter",
              "without butter", "no milk", "milk free", "milk-free")


def _asks_vegan(folded):
    """True when the line asks for a bake with no dairy or no egg in it."""
    said = " ".join(folded)
    return any(phrase in said for phrase in _VEGAN_ASK)


# A step that swaps one ingredient for another is not a "what can I cook" line, whatever else it
# names: "can i use milk instead of cream" is about the cream, not about milk.
SUBSTITUTE_PHRASES = ("instead of", "in place of", "substitute", "swap ", "what can i use",
                      "what do i use", "ran out of", "run out of", "havent got", "haven't got",
                      "dont have", "don't have")


# A dish entry answers "what can I make or cook with this". A line asking how long it keeps, or
# whether it is still safe, is a storage question and belongs to the storage entries, so every dish
# entry stays out of it.
KEEPING = ("keep", "keeps", "keeping", "shelf life", "shelf-life", "last", "lasts",
           "safe", "still ok", "ok to eat",
           "gone off", "went off", "go off", "goes off", "going off", "off", "left out",
           "use by", "days", "how long",
           "reheat", "reheating", "warmed up")


# The words that make "how long" a cooking question rather than a keeping one. A storage entry
# that keys on "how long" has to stay out of these.
COOK_VERBS = ("boil", "boiling", "boiled", "roast", "roasting", "roasted", "steam", "steaming",
              "steamed", "fry", "frying", "fried", "bake", "baking", "baked", "microwave",
              "grill", "grilling", "grilled", "parboil", "poach", "poaching", "simmer",
              "simmering", "air fry", "air-fry", "in the oven", "on the hob", "blanch")


# How long a thing is stored, as opposed to how long it cooks: "how long does lasagne keep in the
# fridge" must not get the oven time. "how long" is left out on purpose, because the oven lines
# are asked that way.
STORAGE = ("keep", "keeps", "keeping", "shelf life", "shelf-life", "fridge", "freezer",
           "freeze", "frozen", "refreeze",
           "refreezing", "reheat", "reheating", "reheated", "last", "lasts",
           "left out", "use by", "gone off", "go off", "goes off", "going off",
           "still ok", "ok to eat", "safe")


# The columns the table has: the words people use for each, and how to say it in the reply.
NUTRIENT_COLUMNS = {
    "protein": ("protein", "protein"),
    "carbs": ("carbs", "carbohydrate"),
    "sugar": ("sugar", "sugar"),
    "fat": ("fat", "fat"),
    "fibre": ("fibre", "fibre"),
    "iron": ("mg", "iron"),
    "calcium": ("mg", "calcium"),
    "potassium": ("mg", "potassium"),
    "salt": ("g", "salt"),
}


# The one sentence that makes a figure useful, for the nutrients where a person has no feel for
# the number: the daily target, so the figure lands somewhere instead of being read and dropped.
NUTRIENT_CONTEXT = {
    "iron": "Women need about 15mg a day and men about 9mg, and the iron in plants and grains "
            "is taken up better with something containing vitamin C.",
    "calcium": "Adults need about 700mg a day.",
    "potassium": "The target is about 3,500mg a day.",
    "salt": "The daily limit is 6g, and bread, cheese and cured meat are where most of it hides.",
}


# The minerals the table carries, per portion. A row without the column has no figure for that
# nutrient, and the line passes rather than being told there is none of it.
_MINERALS = ("iron", "calcium", "potassium", "salt")


# Which column a line asks about. Longer words first, so "carbohydrate" is not read as "carbs"
# and "sugar free" is read as a sugar question rather than a fat one.
_NUTRIENT_WORDS = (
    ("carbohydrates", "carbs"), ("carbohydrate", "carbs"), ("carbs", "carbs"), ("carb", "carbs"),
    ("protein", "protein"), ("proteins", "protein"),
    ("saturated fat", "fat"), ("saturates", "fat"), ("fat", "fat"), ("fats", "fat"),
    ("sugar", "sugar"), ("sugars", "sugar"),
    ("fibre", "fibre"), ("fiber", "fibre"),
    # The minerals are rare words, so they can be key words: the food still has to be in the
    # table for the entry to answer, which is what keeps "how much iron in a shirt" the ironing
    # question and "how much salt should i eat" a daily-limit question.
    ("iron", "iron"), ("calcium", "calcium"), ("potassium", "potassium"),
    ("salt", "salt"), ("salty", "salt"),
)


# A food named as part of a dish is a different food: "banana bread" is not a banana, and a
# curry with chicken in it is not a portion of chicken. The table counts a food on its own, so a
# dish word, another food from the table in the same line, or a food joined on with "and" or
# "with" all pass to whatever answers next.
_NUTRIENT_DISH = ("bread", "cake", "pie", "tart", "muffin", "sauce", "soup", "sandwich", "wrap",
                  "curry", "salad", "smoothie", "juice", "pudding", "jam", "chips", "butter",
                  "cheese", "cream", "biscuit", "cereal", "porridge", "pasta", "rice", "pizza",
                  "stew", "casserole", "roast", "bake", "baked", "fried", "milkshake",
                  "flapjack", "brownie", "cookie", "pancake", "waffle", "toast", "milk", "sugar",
                  "flour", "crisps", "chocolate", "yoghurt", "yogurt", "egg", "nuts", "peanut",
                  "roll", "rolls", "burger", "burgers", "bun", "buns", "pastry", "puff")


_NUTRIENT_JOIN = ("and", "with", "plus")


# How many of the food the line names: "two eggs" is twice an egg, and "3 eggs" is the same
# question typed in figures. A count of half a is half.
_COUNT_WORDS = {"one": 1, "1": 1, "two": 2, "2": 2, "three": 3, "3": 3, "four": 4, "4": 4,
                "five": 5, "5": 5, "six": 6, "6": 6, "seven": 7, "7": 7, "eight": 8, "8": 8,
                "nine": 9, "9": 9, "ten": 10, "10": 10}


def _plurals(word):
    """A food word with an s on the end, near enough for "two eggs" and "two slices"."""
    if not word.isalpha() or word.endswith("s"):
        return word
    if word.endswith(("ch", "sh", "ss", "x", "z")):
        return word + "es"
    if word in ("potato", "tomato", "hero"):
        return word + "es"
    if word.endswith("y") and word[-2:-1] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _portion_count(words, index):
    """How many of them the line names, from the words just before the food."""
    back = words[max(0, index - 4):index]
    said = " ".join(back)
    if said.endswith("a couple of") or said.endswith("couple of"):
        return 2
    if said.endswith("a few"):
        return 3
    if said.endswith("half a") or said.endswith("half an"):
        return 0.5
    for word in reversed(back):
        if word in _COUNT_WORDS:
            return _COUNT_WORDS[word]
    return 1


def _squashed(word):
    """The word with every run of one letter cut to one, so a doubled letter stops mattering."""
    return re.sub(r"(.)\1+", r"\1", word)


def _one_letter_apart(short, long):
    """Whether the shorter word is the longer one with a single letter taken out."""
    index = 0
    while index < len(short) and short[index] == long[index]:
        index += 1
    return short[index:] == long[index + 1:]


def _the_food_named_by_a_slip(words, table):
    """The one food in the table a word of the line is a slip of, with the number of portions.

    A name followed by a dish word ("a bananna cake") is an ingredient of a dish, and a name
    after a joining word ("chicken and bananna") is one of two foods: neither is this table's.
    """
    for index, word in enumerate(words):
        name = _a_food_word_misspelt(word, table)
        if name is None:
            continue
        before = words[index - 1] if index else None
        after = words[index + 1] if index + 1 < len(words) else None
        if after and (after in _NUTRIENT_DISH or after in _NUTRIENT_JOIN):
            return None
        if before and before in _NUTRIENT_JOIN:
            return None
        return name, _portion_count(words, index)
    return None


def _a_food_word_misspelt(word, names):
    """The name this word is a slip of, or None.

    Food words are the ones people mistype most, and the table is keyed on the dictionary
    spelling: "how much protein in a bananna", "in brocolli" and "in a avacado" all reached the
    punt on main while the same question spelled right was answered with the figure. The
    tolerance is deliberately mean, because a wrong food is a wrong number: the word has to
    start and end like the name, be five letters or more, and be the name with a letter doubled, a
    letter swapped for another, or one letter too many or too few.
    """
    if len(word) < 5 or not word.isalpha():
        return None
    if word in names:
        return None
    squashed = _squashed(word)
    for name in names:
        if " " in name or len(name) < 5 or name[0] != word[0]:
            continue
        if len(name) == len(word):
            if squashed == _squashed(name):
                return name
            # "rich" is one letter off "rice", and "iron rich foods" is not a portion of rice:
            # a swapped letter keeps the last one, so the two words have to end alike as well.
            if name[-1] == word[-1] and sum(one != other for one, other in zip(word, name)) == 1:
                return name
        elif abs(len(name) - len(word)) == 1 and name[-1] == word[-1]:
            shorter, longer = sorted((word, name), key=len)
            if _one_letter_apart(shorter, longer):
                return name
    return None


def _nutrient_food(clean, table):
    """The one food from the table the line names a portion of, or None.

    The longest name wins ("sweet potato" over "potato"), and a line that names two foods, or a
    dish made from one, gets nothing: the table has no portion for a curry.
    """
    matches = [food for food in table
               if re.search(r"(?<![a-z0-9])" + re.escape(food) + r"s?(?![a-z0-9])", clean)]
    words = re.findall(r"[a-z0-9']+", clean)
    if not matches:
        # Nothing is spelled the way the table spells it, so the line may still be about a food
        # with a slip in its name: one word of it one letter away from a name in the table.
        return _the_food_named_by_a_slip(words, table)
    best = max(matches, key=len)
    # "milk" inside "a glass of milk" is the same portion, and so is "potato" inside "sweet
    # potato"; a food that is not part of the winner is a second food, and the table has no
    # portion for two of them together.
    # ...and "biscuits" beside "a digestive biscuit" is that same one food, so the plural of a
    # name counts as part of the winner rather than as a second food.
    if any(food not in best and food.rstrip("s") not in best
           and _plurals(food) not in best for food in matches):
        return None
    parts = best.split()
    for index in range(len(words) - len(parts) + 1):
        chunk = words[index:index + len(parts)]
        if chunk[:-1] != parts[:-1]:
            continue
        # "two eggs" is the egg row: the last word of the name can carry the plural.
        if chunk[-1] != parts[-1] and chunk[-1] != _plurals(parts[-1]):
            continue
        before = words[index - 1] if index else None
        after = words[index + len(parts)] if index + len(parts) < len(words) else None
        if after and (after in _NUTRIENT_DISH or after in _NUTRIENT_JOIN):
            return None
        if before and before in _NUTRIENT_JOIN:
            return None
        return best, _portion_count(words, index)
    return None


def _nutrient_asked(clean):
    """The column of the table the line asks about, or None."""
    for word, column in _NUTRIENT_WORDS:
        if re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", clean):
            return column
    return None


# The words for a share of a day's protein, biggest first: an adult needs about 50g, so a
# chicken thigh is a half and an egg is a tenth. A whole takeaway pizza is more protein than
# anyone needs in a day, and "about half of a day's" would have been a wrong way to say it;
# the shares stop short of a day and the reply says so in words instead.
_PROTEIN_SHARES = ((0.8, "most"), (0.5, "half"), (0.3, "a third"), (0.22, "a quarter"),
                   (0.18, "a fifth"), (0.08, "a tenth"))


def _grams(value):
    """A number of grams as a person would say it."""
    if value <= 0:
        return None
    if value < 1:
        return "under a gram"
    if float(value) == int(value):
        return "%d" % int(value)
    return ("%.1f" % value).rstrip("0").rstrip(".")


# The amount a line can name is either a count of the row's own thing ("two eggs", which
# _portion_count reads) or a weight ("100g of chicken", "a pint of milk"). The table is written
# one portion at a time, so a line that names its own weight has to be worked out from that
# portion: answering "100g of chicken" with the figure for 150g is a wrong number, not a
# rounding. A weight the row cannot be measured in (a "medium one") is left alone and the
# portion's own figure is used.
_WEIGHT_WORDS = (("kilograms?|kg", 1000.0, "g"), ("grammes?|grams?|g", 1.0, "g"),
                 ("millilitres?|milliliters?|ml", 1.0, "ml"), ("centilitres?|cl", 10.0, "ml"),
                 ("litres?|liters?|l", 1000.0, "ml"), ("pints?", 568.0, "ml"))


def _portion_size(portion):
    """The figure a row is written for, and its unit: "a 200ml glass" -> (200.0, "ml")."""
    found = re.search(r"(\d+(?:\.\d+)?)\s*(g|ml)\b", str(portion).lower())
    return (float(found.group(1)), found.group(2)) if found else None


def _weight_in_the_line(clean, portion):
    """The weight the line asks about as a multiple of the row's portion, and the words used."""
    base = _portion_size(portion)
    if base is None:
        return None
    for pattern, scale, unit in _WEIGHT_WORDS:
        found = re.search(r"(\d+(?:\.\d+)?)\s*(?:" + pattern + r")\b", clean)
        if found and base[1] == unit:
            return float(found.group(1)) * scale / base[0], found.group(0)
    if base[1] == "ml":
        found = re.search(r"\b(half a pint|a pint|one pint)\b", clean)
        if found:
            many = 0.5 if found.group(1).startswith("half") else 1.0
            return many * 568.0 / base[0], found.group(1)
    return None


def _figure(value):
    """A figure the way a person says it: 2.7, 30, 900."""
    if value >= 10:
        return "%d" % int(round(value))
    return ("%.1f" % value).rstrip("0").rstrip(".")


# The plurals, which take "are" rather than "is".
_CALORIE_PLURAL = ("strawberries", "grapes", "chips", "crisps", "peanuts")


# A pizza base is not a pizza: the dough, a base and a homemade one are the ingredients of the
# dish rather than the dish, and the whole-dish rows above have no number for them.
_CALORIE_NOT_A_DISH = ("dough", "base", "bases", "recipe", "homemade", "home made")


# Which line asks about the calories in a named food: the food has to be there, and the ask
# has to be about what is in it.
CALORIE_ASKS = ("calorie", "calories", "cals", "kcal", "kilocalories",
                "how many calories")


# The foods whose own entries already carry a calorie figure, which answer better than a table.
_CALORIE_OWN = ("chicken breast", "chicken breasts")


# A food named as part of a dish is a different food: "banana bread" is not a banana, and a
# sandwich with cheese and tomato in it is neither, so the table (which counts a food on its own)
# has nothing to say about it. A dish word after the food, another food from the table in the same
# line, or a food joined to something with "and" or "with", all pass instead of guessing.
_CALORIE_DISH = ("bread", "cake", "pie", "tart", "muffin", "sauce", "soup", "sandwich", "wrap",
                 "curry", "salad", "smoothie", "juice", "pudding", "jam", "crisps", "chips",
                 "butter", "cheese", "cream", "biscuit", "cereal", "porridge", "pasta", "rice",
                 "pizza", "stew", "casserole", "roast", "bake", "baked", "fried", "milkshake",
                 "flapjack", "brownie", "cookie", "pancake", "waffle", "toast", "milk", "sugar",
                 # "a sausage roll is not a sausage" (nor is a turkey burger a portion of
                 # turkey, or a ham roll two slices of ham): the word after the food decides.
                 "roll", "rolls", "burger", "burgers", "bun", "buns", "pastry", "puff")


_CALORIE_JOIN = ("and", "with", "plus")


def _names_a_food(line):
    """True when a word of the line is a food one of the calorie and nutrient tables holds."""
    lowered = line.lower()
    for table in (FOOD_CALORIES, FOOD_CALORIE_MEALS, FOOD_NUTRIENTS):
        for name in table:
            if name and name in lowered:
                return True
    return False


# "How do I make a cake gluten free" and "can i make bread without gluten" were a shrug and a
# hedge on main, and "how do i make gluten free pastry" got the plain wheat shortcrust - gluten,
# to the person who asked for none. Making a dish without gluten is a question about the dish,
# not about one ingredient, because a blend behaves differently from flour: it needs something to
# hold it and it needs a rest. One answer for the bakes, one for the pastry, one for bread, which
# is the one to buy.
GLUTEN_FREE_ASKS = ("gluten free", "gluten-free", "glutenfree", "without gluten", "no gluten",
                    "free from gluten", "wheat free", "wheat-free", "without wheat", "no wheat",
                    "gluten allergy", "coeliacs", "coeliac", "contain gluten",
                    "contains gluten",
                    # the two things people cut out at once are one ask: "a gluten and dairy free
                    # cake" has no "gluten free" in it, so the plain phrase never matched it and the
                    # dairy answer took the line
                    "gluten and dairy free", "dairy and gluten free", "gluten and egg free",
                    "egg and gluten free", "gluten and dairy-free", "dairy-free and gluten-free")


# The dish is the question, so one of these has to be in the line as well: "im gluten free, what
# can i eat" is a meal-ideas line with another answer, and a roux or a sauce is made by its own
# entry (the plain flour method is the right method for a roux, badly wrong though it is here).
GLUTEN_FREE_DISHES = ("make", "making", "made", "bake", "baking", "baked", "cook", "cooking",
                      "recipe", "version", "instead", "cake", "cakes", "sponge", "brownie",
                      "brownies", "cookie", "cookies", "muffin", "muffins", "biscuit",
                      "biscuits", "bread", "loaf", "loaves", "roll", "rolls", "pastry",
                      "shortcrust", "scone", "scones", "pancake", "pancakes", "batter",
                      "flour", "pasta", "spaghetti", "noodles", "macaroni", "lasagne",
                      "how do i", "can i", "how can i")


# The dishes and diets a blend would ruin: a sauce, a gravy and a porridge are made by their own
# entries, the Yorkshire tin answer keeps the hot-fat method, and a coeliac question is about
# reading labels rather than about a bake.
_GLUTEN_FREE_SKIP = ("gravy", "porridge", "sauce", "soup", "curry", "stew", "casserole", "stock",
                     "marinade", "dressing", "coating", "roux", "thicken", "thickening",
                     "yorkshire", "shortbread", "beer", "lager", "ale", "cider", "wine", "what can i eat", "what can i cook",
                     "what should i eat", "what can i have", "meal", "meals", "dinner", "lunch",
                     "snack", "ideas", "what to eat", "taste", "tastes", "tasting", "healthier",
                     "better for you", "good for you", "worth it", "is it bad", "lose weight",
                     # "how do i know if i have coeliac" reached this row on "how do i" alone and
                     # was told how a bake changes: a question about the condition, and about
                     # being tested for it, is not a dish. The disease row answers these.
                     "how do i know", "do i have", "have i got", "diagnosed", "diagnosis",
                     "symptoms", "signs", "blood test", "test for", "contagious", "curable",
                     "cause", "causes", "anaemia", "underactive", "deficiency")


_GLUTEN_MAKING = ("make", "making", "bake", "baking", "cook", "cooking", "recipe", "version",
                  "how do i", "how can i", "how to")


def _gluten_free(memory, understood):
    """How the dish changes when the gluten comes out, and the pastry and the loaf are not one job."""
    clean = understood.get("clean") or ""
    folded = " " + re.sub(r"[^a-z0-9 ]+", " ", clean.lower()) + " "
    # "is bread gluten free" is a fact, not a recipe: the answer is that wheat is what ordinary
    # bread is made of, and a loaf made without it is a different product.
    if (re.match(r"(is|are|does|do|can|should)\b", clean)
            and not any(" %s " % word in folded for word in _GLUTEN_MAKING)):
        return ("Not the ordinary one: wheat flour is what bread, pasta, cakes and most biscuits "
                "are made from, so unless the packet says gluten free it is not. A gluten-free "
                "loaf is a different product rather than the same loaf without something in it, "
                "and check the label for 'may contain wheat' on sauces, stock and chips.")
    if any(" %s " % word in folded for word in ("bread", "loaf", "loaves", "roll", "rolls",
                                                "baguette", "pizza", "naan", "focaccia")):
        return ("Buy this one rather than bake it: a gluten-free loaf needs a batter, not a dough, "
                "plus psyllium or xanthan to stand in for the stretch, and it is the one thing a "
                "shop does better. For a bun or a pizza base, a gluten-free bread flour blend "
                "with a teaspoon of xanthan per 500g and a wet dough, proved in the tin, gets "
                "there.")
    if any(" %s " % word in folded for word in ("pasta", "spaghetti", "penne", "macaroni",
                                                "lasagne", "noodles")):
        return ("Buy it: dried pasta made from corn, rice or buckwheat is the one gluten-free swap "
                "that works, and the fresh gluten-free pasta in the chiller is better still. Cook "
                "it in plenty of salted water and taste a minute before the packet says, because "
                "it goes from firm to mushy quickly, and dress it straight away - it does not "
                "wait like wheat pasta does.")
    if any(" %s " % word in folded for word in ("pastry", "shortcrust", "tart", "pie", "quiche",
                                                "flan", "crust")):
        return ("Gluten-free shortcrust: 200g of a gluten-free plain flour blend with half a "
                "teaspoon of xanthan gum, 100g of cold butter rubbed in, then a beaten egg or a "
                "few spoons of iced water to bring it together. Rest it 30 minutes in the fridge "
                "and roll it between two sheets of baking paper, because it tears. It needs no "
                "blind-bake change: 15 minutes at 190C (170C fan).")
    said = ("A gluten-free bake needs a blend, not one flour: a shop gluten-free plain flour blend "
            "with a quarter teaspoon of xanthan gum per 200g, and a splash more liquid than the "
            "recipe says, because there is no stretch in it to hold water. Let the batter stand "
            "20 minutes before it goes in the oven and it stops tasting gritty. Expect it to "
            "brown faster, so drop the oven 10C and give it five minutes longer.")
    if any(" %s " % word in folded for word in ("dairy", "milk", "butter", "cheese", "yoghurt",
                                                "yogurt", "vegan", "plant")):
        # the dairy half is a straight swap and a short one, so the blend answer carries it too
        said += (" For the dairy, unsweetened soya or oat milk goes in one for one, and a hard "
                 "dairy-free block margarine replaces the butter at the same weight.")
    return said


# A yes/no question about a food's own recipe: "is rice gluten free", "does soy sauce contain
# gluten", "is butter gluten free". The answer is a verdict about that food, not a recipe for it,
# and it comes from the same table every other answer in this file uses - so a food nobody wrote a
# card for still gets an honest yes or no. The ask is only the fact form ("gluten free", "contain
# gluten"); a line that asks to make something without gluten is the blend row's, and a line that
# says the food is already gluten free ("is gluten free bread ok") is the food's own answer.
# The asks that make a food the subject of a fact: "glutten free", "contain gluten", "without
# wheat". A diet said of the person ("im coeliac", "my son has a gluten allergy") is not one of
# them, and on a later line ("what can i do with butter beans" after "im coeliac") it was: the
# diet is carried into the reading, this row claimed the line, declined it, and the bean card on
# main never got its turn.
GLUTEN_FACT_DIET = ("gluten allergy", "coeliacs", "coeliac")


# The one food where the wheat-free version has its own name, and people know it: tamari.
GLUTEN_FACT_NAMED_SWAP = {
    "soy sauce": "Tamari is made without wheat and tastes the same.",
    "soya sauce": "Tamari is made without wheat and tastes the same.",
}


# The foods where the usual shop version has wheat in it even though the food itself is not made
# of it: a sausage is rusk as much as meat, and chips from a chip shop are often dusted with
# flour. A confident "yes" would be wrong for a coeliac, and a recipe is no answer at all, so
# these say what to look at instead.
GLUTEN_FACT_NOT_PLAIN = {
    "sausage": ("Usually not: most sausages have rusk in them, which is bread, so look for the "
                "ones marked gluten free."),
    "sausages": ("Usually not: most sausages have rusk in them, which is bread, so look for the "
                 "ones marked gluten free."),
    "chips": ("Not always: chips from a chip shop are sometimes dusted with flour, so ask there "
              "and read the packet on oven chips."),
}


# The ways people say an appliance is not in the kitchen.
LACKS = (
    ("oven", ("no oven", "without an oven", "dont have an oven", "don't have an oven", "no ovens",
              "oven is broken", "oven's broken", "ovens broken", "oven doesnt work",
              "oven doesn't work", "just a hob", "only a hob", "hob only", "no cooker",
              "no stove", "only a microwave", "just a microwave", "microwave only",
              "no grill", "without a grill", "only have a microwave", "only got a microwave",
              "just have a microwave", "just got a microwave", "only have the hob",
              "only got a hob", "only have one hob", "no oven at home", "broken oven",
              "oven broke", "oven packed in", "no working oven", "oven isnt working",
              "oven is not working", "oven has broken",
              # the many ways people say the oven has gone, kept one word away from the bare
              # verbs: "my dog died" is not a broken oven, "my oven has died" is
              "oven has packed in", "ovens packed in", "oven packed up", "oven has packed up",
              "oven conked out", "oven has conked out", "oven died", "oven has died",
              "oven is dead", "oven broke down", "oven has broken down", "oven has broke",
              "oven stopped working", "oven has stopped working", "oven is on the blink",
              "oven has gone", "oven is gone", "oven has had it", "oven is knackered",
              "oven not heating", "oven isnt heating", "oven won't heat", "oven wont heat",
              "no oven space", "ova has gone")),
    ("hob", ("no hob", "without a hob", "no cooker", "no stove", "only a microwave",
             "only got a kettle", "only have a kettle", "just a kettle", "only the kettle",
             "just a microwave", "microwave only", "no rings", "no burners",
             "only have a microwave", "only got a microwave", "just have a microwave",
             "only have the microwave")),
    ("microwave", ("no microwave", "without a microwave")),
    ("freezer", ("no freezer", "without a freezer", "no room in the freezer")),
    ("kettle", ("no kettle", "without a kettle")),
)


# What an answer needs to be cooked: the words a method uses for each appliance.
REQUIRES = {
    "oven": ("oven", "roast", "roasting", "roasted", "bake", "baking", "baked", "grill",
             "grilled", "traybake", "tray bake", "casserole", "190c", "200c", "180c", "220c",
             "160c", "170c", "210c", "230c", "fan oven"),
    "hob": ("fry", "fried", "frying", "pan", "simmer", "boil", "boiling", "saucepan", "hob",
            "stir fry", "stir-fry", "poach", "steam", "griddle"),
    "microwave": ("microwave", "microwaved"),
    "freezer": ("freezer", "freeze", "frozen", "defrost"),
}


# The plainest way to say an appliance has gone is "I don't have a hob", and the article is what
# the phrase lists kept losing: "dont have an oven" was listed but "i dont have an oven" with the
# article was not, and "i dont have a microwave" said nothing at all. The heads and the nouns are
# kept apart so every appliance gets every wording, rather than one list per appliance.
LACK_HEADS = ("dont have", "don't have", "do not have", "doesnt have", "doesn't have", "didnt have",
              "didn't have", "havent got", "haven't got", "hasnt got", "hasn't got",
              "have not got", "has not got", "not got", "got no", "no longer have")


LACK_NOUNS = {"oven": ("an oven", "a oven", "oven"), "hob": ("a hob", "hob"),
              "microwave": ("a microwave", "microwave"), "freezer": ("a freezer", "freezer"),
              "kettle": ("a kettle", "kettle")}


# A thing that hangs on an appliance is not the appliance: "i dont have an oven thermometer" is a
# question about a thermometer, so the oven is not what is missing.
LACK_ATTACHED = ("thermometer", "gloves", "glove", "mitt", "mitts", "tray", "dish", "rack",
                 "shelf", "light", "bulb", "door", "liner", "paper", "foil", "bag", "bags")


def _says_gone(phrases, segments):
    """True when a segment says one of these phrases, unless a word hangs off the appliance."""
    for segment in segments:
        for phrase in phrases:
            for found in re.finditer(re.escape(phrase), segment):
                after = segment[found.end():].strip().split(" ", 1)[0].strip(".,!?;:")
                if after not in LACK_ATTACHED:
                    return True
    return False


def _line(understood):
    """The line as this module reads it: what they typed, and the words it was read into."""
    return (((understood or {}).get("clean") or "") + " "
            + ((understood or {}).get("norm_text") or "")).lower()


# A sentence that turns the appliance down is not an instruction to use it: "nothing here needs an
# oven", "no oven needed", "a hob alone will do".
TURNS_DOWN = ("no", "not", "without", "nothing", "never", "needs none", "free")


# A decision about the appliance is not an instruction to cook with it: "is it worth repairing my
# broken oven" wants the money rule, and the rule has to name the oven it is about.
DECIDING = ("repair", "repairing", "replace", "replacing", "mend", "mending", "fix", "fixing",
            "service", "servicing", "quote", "quotes", "scrap", "scrapping", "engineer",
            "warranty", "guarantee", "call-out")


def _sentences(text):
    return [one for one in re.split(r"(?<=[.!?;:])\s+|\n+", text) if one.strip()]


# What to cook when the kitchen has no oven: a list of hob-only meals, because that is the meal
# people mean when they say "no oven tho just a hob".
NO_OVEN = (
    "With a hob you can still eat well: pasta with a sauce made in the pan, rice with stir-fried "
    "veg and an egg on top, a one-pan curry of chickpeas or lentils with tomatoes, quesadillas or "
    "toasted sandwiches pressed in a dry pan, or potatoes boiled and then crushed into a pan with "
    "butter and greens. Eggs, tinned fish and beans all cook in a pan in minutes.")


NO_HOB = (
    "With only a microwave you can still eat properly: jacket potatoes (10 minutes, turned once), "
    "rice or pasta cooked in a big bowl of water, porridge, scrambled eggs, steamed frozen veg, "
    "tinned soup or beans, and a poached egg in a mug of water. Give a jacket potato a rub of oil "
    "and salt first and it comes out closer to oven-baked.")


# The oven is mostly missed for baking, and there are cakes that need no oven at all.
NO_BAKING = (
    "You cannot bake without an oven, but a fridge cake needs none: melt 100g butter, 200g "
    "chocolate and 2 tablespoons of golden syrup in a pan, stir in 200g crushed biscuits and a "
    "handful of raisins, press it into a tin and chill it for 2 hours. A cheesecake that sets in "
    "the fridge, tiramisu and lemon posset are the same trick: they set cold, not in the oven.")


# A scone, a pancake and a drop scone are not cakes: they were cooked on a girdle or in a pan long
# before every kitchen had an oven, and the fridge cake was answering "can i make scones with no
# oven" - a different food, since a scone dough pats out and cooks in a pan while anything that
# sets in the fridge is chocolate and crushed biscuits. So the pan bakes get their own answer,
# named for the thing the line asks about, and everything that wants a tin keeps the no-bake one.
_GRIDDLE_DOUGH = ("scone", "scones", "drop scone", "drop scones", "pikelet", "pikelets",
                  "chapati", "chapatis", "chapatti", "chapattis", "roti", "rotis")


_GRIDDLE_BATTER = ("pancake", "pancakes", "crumpet", "crumpets", "pikelet", "pikelets")


_GRIDDLE_WARM = ("wrap", "wraps", "tortilla", "tortillas", "pitta", "pittas", "pita", "pitas")


# What will not work on a hob is anything that has to rise and brown in a tin, so each answer ends
# on that, because the next question is always "so what about the birthday cake".
_GRIDDLE_TAIL = ("What will not work on a hob is anything that has to rise and brown in a tin - a "
                 "sponge, a loaf, pastry - and those are the no-bake answers instead.")


# Bread is the one bake with a real no-oven answer, and it is a pan, not a tin. It gets its own
# answer: told as a tail on the fridge cake, "how do i bake bread with no oven" was mostly a
# recipe for something they did not ask for.
NO_OVEN_BREAD = (
    "Bread with no oven is flatbread: flour, water, salt and a little oil, rested 20 minutes, "
    "rolled thin and cooked in a dry hot pan for two minutes a side. The same dough pushed into a "
    "hot oiled frying pan, lid on, turned once, makes a thick loaf that will do for toast.")


# Nothing but a kettle: couscous is the one proper meal it can make, and it is a good one.
NO_KETTLE = (
    "A kettle still makes a real meal out of couscous: put it in a bowl, pour boiling water over "
    "to just cover it, cover the bowl for five minutes, then fork it through with tinned "
    "chickpeas or tuna, chopped tomato, olives and lemon. Overnight oats (soak them in the "
    "fridge), instant porridge, pot noodles and cup soup need nothing more. If you can stretch to "
    "a cheap single-ring hob, it opens up pasta, rice, eggs and tinned soup.")


SUBSTITUTE_PHRASES = ("out of", "ran out", "run out", "no more", "none left", "in place of")
