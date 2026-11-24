"""Part 5 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from .cooking_part_02 import (
    _same,
)
from .cooking_part_03 import (
    _SUGAR_MAKING, _SUGAR_TROUBLE,
)


def _sugar_work(memory, understood):
    """Sugar as a thing you work with: dissolving it, boiling it to caramel, keeping it clear.

    Three questions arrive with the same words. A syrup that will not go clear wants warm water
    and a stir; sugar that has gone grainy wants the crystals melted back and the pan side wiped;
    and "how do i make caramel" is not a fault at all but the cooking itself. The diet answer used
    to take all three, because "how do i" plus "sugar" was enough for it.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]

    def has(*names):
        return any(_same(word, name) for word in words for name in names)

    if has("bitter", "burnt", "burned", "burning", "smoky", "smells"):
        # "get burnt sugar out of a pan" is a pan to clean, not a caramel that went too far: the
        # bitter caramel line ("start again, pull it at the colour of a copper penny") is no use
        # to somebody holding a burnt pan.
        if _burnt_on_the_pan(" ".join(words)):
            return ""
        return ("A bitter caramel has gone past the colour: sugar keeps cooking after it leaves "
                "the heat, so it went from amber to dark before it came off. Start again and pull "
                "it at the colour of a copper penny, and have the cream ready to add off the heat "
                "so it stops at once. One that tastes of the pan is not worth saving.")
    if has("hard", "hardened", "hardens", "block", "solid", "lumps", "lumpy", "stuck",
           "soften", "softens", "softening"):
        return ("Sugar that has set hard has taken up damp and dried out again: put the bag in the "
                "microwave for 10 seconds at a time, or stand a slice of bread or a peeled apple in "
                "the jar overnight, and it breaks up. Keep it in an airtight jar away from the "
                "steam of the kettle, because it is the damp that sets it into a block.")
    if has(*_SUGAR_TROUBLE) and not has("dissolve", "dissolves", "dissolving", "dissolved", "melt",
                                        "melts", "melting", "melted"):
        return ("Sugar crystallises when it is stirred once it is boiling, or when one grain from "
                "the side of the pan drops back in. Melt it back with a tablespoon of water over a "
                "low heat without stirring, and next time stir only until the sugar has dissolved, "
                "wipe the pan sides down with a wet pastry brush, and add a squeeze of lemon or a "
                "spoonful of golden syrup at the start.")
    if (has("syrup", "coffee", "cocktail", "cocktails", "tea", "dissolve", "dissolves",
            "dissolving", "dissolved", "melt", "melts", "melting", "melted")
            or not has(*_SUGAR_MAKING)):
        return ("Sugar dissolves fastest in hot liquid: warm the water or milk first, stir until "
                "the liquid is clear rather than for a set time, and use about 200g of sugar to "
                "100ml of water for a syrup. Caster sugar goes in quicker than granulated and "
                "icing sugar dissolves almost at once. A spoonful of lemon juice or golden syrup "
                "stops a syrup crystallising as it cools.")
    if has("toffee", "toffees", "fudge", "praline", "brittle", "candy"):
        return ("Caramel is the base of all of them, then the temperature sets what you get: "
                "200g sugar in a dry heavy pan, swirled not stirred, to the colour of a copper "
                "penny. Toffee is that plus 60g butter and a splash of cream stirred in off the "
                "heat, cooked on to 150C (hard crack) and poured to set; fudge comes off at 116C "
                "(soft ball), then you beat it in the pan as it cools so it stays smooth instead "
                "of grainy. A sugar thermometer earns its keep here.")
    return ("Caramel is sugar cooked until it changes colour, and nothing else: 200g sugar in "
            "a dry heavy pan over a medium heat, not stirred but swirled, until it is the "
            "colour of a copper penny - then straight off the heat, because it keeps cooking. "
            "For a sauce, add a splash of warm cream off the heat, as it spits. A wet caramel "
            "is 200g sugar with 60ml water and a squeeze of lemon, boiled without stirring.")


# An oven but no hob: roast and bake everything in one tray.
NO_OVEN_ONLY = (
    "With an oven and no hob, cook in one tray: chicken thighs or sausages with chopped potato, "
    "onion and pepper, oil, salt and herbs, 40 minutes at 200C (180C fan), turned once. Jacket "
    "potatoes take an hour at the same heat, baked pasta or a tin of tomatoes with butter and "
    "breadcrumbs bakes in 25 minutes, and roasted veg with a drained tin of chickpeas makes a "
    "meal on its own.")


NO_MICROWAVE = (
    "Without a microwave, a pan does the same jobs: reheat rice or leftovers with a splash of water "
    "over a low heat, defrost in the fridge overnight, and cook porridge or scrambled eggs in a "
    "saucepan in about five minutes.")


# Naming what is in the kitchen is how people ask what to make of it, oven or no oven.
LISTING = ("i have", "i've got", "ive got", "i only have", "only have", "only got", "just have",
           "just got", "there's", "theres", "in the fridge", "in my fridge", "in the cupboard",
           "in my cupboard", "sat in")


# The words a line uses when it wants a meal, which a kitchen problem alone does not say.
COOKING_ASKS = ("cook", "cooking", "make", "making", "dinner", "dinners", "supper", "tea",
                "meal", "meals", "eat", "eating", "recipe", "recipes", "idea", "ideas", "food",
                "lunch", "breakfast", "roast", "bake", "baking", "hungry",
                # "i need a dessert for 12 people with no oven" wants the sweet course, and
                # "need" and "want" are how people ask for a thing rather than a meal: without
                # them the no-oven answer was never reached and the question went back as a
                # "what kind of dessert do you usually go for".
                "need", "needs", "want", "wants", "dessert", "desserts", "pudding", "puddings",
                "sweet", "cake", "cakes", "biscuits", "cookies")


# A pudding for a crowd is the same pudding twice over: "gotta bring a dessert, family do, 12 of
# us" is answered with a crumble, and the useful part is how much of it to make.
PUDDING_IDEAS = (
    "An apple and blackberry crumble is the easiest crowd-pleaser: fruit in a dish, a crumble of "
    "butter, flour and sugar on top, 35 minutes at 180C, and custard. Baked rice pudding and bread "
    "and butter pudding are just as easy and soft enough for anyone who finds chewing hard; Eton "
    "mess takes five minutes if you buy the meringues.")


# The one appliance a line says it has ("i've only got a kettle"), and the ones it names as there
# ("no hob, but the oven works"): what to cook depends on what is left, not on what is missing.
ONLY_ONE = {
    "kettle": ("only got a kettle", "only have a kettle", "only a kettle", "just a kettle",
               "only the kettle"),
    "microwave": ("only have a microwave", "only got a microwave", "only a microwave",
                  "just a microwave", "just have a microwave", "just got a microwave",
                  "microwave only", "only the microwave"),
    "hob": ("only a hob", "just a hob", "only have a hob", "only got a hob", "hob only",
            "only have one hob"),
    "oven": ("only an oven", "only have an oven", "only got an oven", "oven only"),
}


HAVE_ONE = {
    "oven": ("got an oven", "have an oven", "have the oven", "the oven works", "there's an oven",
             "theres an oven", "oven works"),
    "hob": ("got a hob", "have a hob", "there's a hob", "theres a hob", "got a cooker",
            "have a cooker"),
    "microwave": ("got a microwave", "have a microwave", "there's a microwave",
                  "theres a microwave"),
    "kettle": ("got a kettle", "have a kettle", "there's a kettle", "theres a kettle"),
}


def available(text, gone):
    """What the kitchen has, as far as the line says: what it names, else whatever is not gone.

    A thing the line names as gone is not there, however it was named: "i dont have an oven"
    and "i dont have an oven but i have a hob" both reached the oven-and-no-hob answer, because
    the words "have an oven" sit inside "dont have an oven". Naming what is missing leaves the
    rest of a normal kitchen, so dropping the gone one from the named ones is the whole fix.
    """
    text = str(text).lower()
    for name, phrases in ONLY_ONE.items():
        if any(one in text for one in phrases):
            return {name}
    named = {name for name, phrases in HAVE_ONE.items() if any(one in text for one in phrases)}
    named -= set(gone or ())
    if named:
        return named
    return {"oven", "hob", "microwave", "kettle"} - set(gone or ())


def _herbs_keep(memory, understood):
    """A herb that can be saved goes in water; a slimy one is past saving and the reply says so."""
    words = set((understood or {}).get("words") or ())
    clean = " " + ((understood or {}).get("clean") or "") + " "
    if {"slimy", "slime", "rotten", "mouldy", "moldy"} & words or "gone over" in clean:
        return ("A slimy herb is past saving, so bin the slimy stems and pick out the ones that are "
                "still green to use today. It happens when the leaves stay wet: a bag with damp "
                "kitchen paper is right, a wet one sat in a warm fridge is not. Next bunch, stand "
                "the stems in an inch of water with a bag over the top, or freeze what you cannot "
                "use in the next few days.")
    return ("Stand soft herbs in a jar with an inch of water, loosely covered with a bag, or wrap "
            "them in damp kitchen paper in the fridge. Basil hates the cold, so keep that one on "
            "the windowsill instead.")


# The words people meet in a recipe and are too polite to look up.
COOK_WORDS = {
    # "what is a simmer" and "simmer or boil" belong to the simmer-and-boil entry (#1041), which
    # measures them against each other; these are the words nothing else explains.
    "reduce": "Reducing is simmering a sauce uncovered until water boils off and it thickens and "
              "tastes stronger. Watch it at the end - the last two minutes do most of the work.",
    "sear": "Searing is browning meat hard in a hot pan, for flavour and colour, not for cooking "
            "it through. Pat it dry first and leave it alone until it releases by itself.",
    "blanch": "Blanching is a minute or two in boiling water, then straight into cold water: it "
              "sets the colour of green vegetables and loosens tomato and peach skins.",
    "sweat": "Sweating is softening onion or vegetables slowly in a little fat with the lid on, "
             "without colouring them. Low heat, five to ten minutes.",
    "al dente": "Al dente means pasta with a little bite left in the middle: take a minute off "
                "the packet time, taste it, and keep testing.",
    "fold": "Folding is mixing gently with a big spoon, turning the bowl and cutting through, so "
            "you keep the air in whipped egg white or cream.",
    "deglaze": "Deglazing is pouring wine, stock or water into a hot pan after frying and "
               "scraping the brown bits up: that is where the flavour is.",
}


# What each word acts on, so a click in a recipe is not read as a click in the body or the house.
WORD_SUBJECT = {
    "reduce": ("sauce", "stock", "gravy", "wine", "juice", "glaze", "syrup", "liquid",
               "broth", "soup", "half", "pan", "thicken", "thickens", "jam", "cream"),
    "fold": ("flour", "egg", "eggs", "white", "whites", "batter", "mixture", "dough",
             "cream", "sugar", "meringue", "ingredient", "ingredients", "pastry", "bowl",
             "spoon", "spatula", "filling", "chocolate"),
    "sear": ("steak", "meat", "beef", "chicken", "fish", "salmon", "pork", "lamb", "tuna",
             "pan", "joint", "roast", "sausage", "tofu", "scallop"),
    "sweat": ("onion", "onions", "shallot", "shallots", "leek", "garlic", "carrot",
              "vegetables", "veg", "celery", "mushroom", "pan", "butter", "fat", "oil"),
    "blanch": ("vegetable", "vegetables", "greens", "bean", "beans", "broccoli", "tomato",
               "tomatoes", "peach", "almond", "almonds", "potato", "potatoes", "chips",
               "spinach", "cauliflower", "cabbage"),
    "deglaze": ("pan", "wine", "stock", "sauce", "bits", "meat", "roast", "gravy"),
}


# "what does searing pain mean" and "how do i reduce my electricity bill" are not glossary
# questions whatever verb they contain. Words rather than phrases where the bare word cannot be
# about food, phrases where it can (a baking sheet is a real thing in a kitchen).
NOT_A_COOKING_LINE = ("pain", "pains", "maths", "math", "percentage", "equation", "fraction",
                      "algebra", "fitted sheet", "bed sheet", "sheets", "towel", "towels",
                      "laundry", "pillow", "duvet", "hands sweating", "sweaty", "armpits",
                      "my hands", "my feet", "fever", "night sweats", "anxious", "anxiety",
                      "nerves", "doctor", "gp appointment", "hospital", "sick", "ill",
                      "temperature of the room", "heating bill", "electricity", "gas bill",
                      # "fold", "sweat" and "sear" are ordinary words elsewhere: a card game, a
                      # folded sheet of paper, a rock face, a relationship. Each of these was a
                      # wrong answer where main declined, and the list costs nothing because a
                      # cooking line that carries the food word still answers.
                      "poker", "cards", "card game", "blackjack", "origami", "folding chair",
                      "folding table", "geology", "tectonic", "fold in the rock",
                      "relationship", "boyfriend", "girlfriend",
                      "belly fat", "my back", "my shoulder",
                      # a glossary of cooking words is not a mail server: "how do i reduce
                      # spam" was answered with a definition, because "reduce" is a cooking
                      # verb too. Nothing in a kitchen line carries these.
                      "spam", "email", "emails", "e-mail", "inbox", "junk mail", "scam",
                      "unsubscribe", "newsletter", "mailbox",
                      # "reduce" is a cooking verb and also how everyone asks about a screen,
                      # a volume or a bill: "how do i reduce the brightness on my phone" was
                      # answered with a definition of reducing a sauce.
                      "brightness", "bright", "brighter", "dim", "dimmer", "screen", "screens",
                      "display", "volume", "louder", "loud", "screen time", "data usage",
                      # "how do i reduce sugar in my diet" was a definition of reducing, because
                      # "reduce" is a cooking verb and "sugar" is a cooking word: the diet in the
                      # line is what says it is not a sauce.
                      "my diet", "diet", "diets", "dieting", "sugar intake", "blood sugar",
                      "less sugar", "down on sugar", "cut out sugar", "sugary", "cravings")


# The shape of a "what does it mean" question.
DEFINITION_WORDS = ("mean", "means", "meaning", "difference", "what is", "what's", "whats",
                    "between", "versus", "vs", "definition")


def _names_a_subject(word, said):
    """True when the line says the food this word acts on, or points at it: "sear it"."""
    if any(subject in said for subject in WORD_SUBJECT.get(word, ())):
        return True
    return any(word + pronoun in said for pronoun in (" it", " them", " this", " these"))


def _cook_word_hit(word, said):
    """Where the line says this word, as (position, the table key), or None."""
    if word in said:
        return said.find(word), word
    stem = word.rstrip("e")
    if len(stem) > 3 and stem in said:
        return said.find(stem), word
    return None


# A mash that must leave butter or milk out, or that is for a baby, is not the plain method: the
# method starts with salted water and ends with warm milk and butter. Held out of the plain entry
# so the answer that suits those lines is the one that takes them.
_MASH_NOT_THIS = ("without butter", "no butter", "butter free", "without milk", "no milk",
                  "milk free", "dairy free", "dairy-free", "no dairy", "without dairy",
                  "vegan", "baby", "babies", "for my baby", "for a baby", "weaning", "weaned",
                  "toddler", "6 months", "six months", "9 months", "first foods",
                  # "how long" is back in the key for the boiling time, and it is in every
                  # keeping question too: "how long does mashed potato keep in the fridge"
                  # belongs to the keeping entry, not to the method.
                  "keep", "keeps", "keeping", "store", "storing", "storage", "fridge",
                  "freezer", "freeze", "refrigerate", "reheat", "reheated", "leftover",
                  "left over", "last", "lasts", "gone off", "safe",
                  # "how long does" is not a keeping word on its own: it took "how long does it
                  # take to make mash" as well, which is the boiling time this method opens
                  # with. Every keeping line about mash says keep, fridge, last or gone off
                  # anyway, and those are all above.
                  )


# A burger with no beef and no mince in it is a pulses method, not the 20%-fat one.
_NO_MEAT = ("without mince", "no mince", "without beef", "no beef", "without meat", "no meat",
            "meat free", "meat-free", "vegetarian", "veggie", "vegan", "lentil", "lentils",
            "bean", "beans", "chickpea", "chickpeas", "pulse", "pulses")


# A time, a heat or a "how long" is the timing entry's question, not the recipe's.
_TIMING_ASKS = ("how long", "minutes", "temperature", "what temp", "fan", "gas mark", "preheat",
                "how hot")


_ALREADY_BAKED_PHRASES = ("use up", "using up", "used up", "left over", "left from",
                          "already made", "got spare", "going stale")


_NONSTICK_CLEAN = ("clean", "cleaning", "wash", "washing", "scrub", "scouring", "burnt",
                   "stained")


_NONSTICK_KEEP = ("safe", "safety", "still use", "use it", "throw", "bin it", "replace",
                  "replacing", "worn", "bits", "coming off", "flakes", "scratched", "scratches",
                  "scratch", "flaking", "peeling", "coating")


def _non_stick_pan(memory, understood):
    """The sponge for a cleaning line, the verdict first for a "is it still safe" line."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    wants_clean = any(word in said for word in _NONSTICK_CLEAN)
    if not wants_clean and any(word in said for word in _NONSTICK_KEEP):
        return ("Small scratches are fine to keep cooking on. Once it is scratched through to the "
                "metal, or the coating is flaking or peeling into the food, replace the pan: you "
                "do not want flakes of coating in a meal, and a worn pan stops being non-stick "
                "anyway. Until then, keep metal tools, scouring pads and an empty pan on high "
                "heat away from it, because those are what scratch it.")
    return ("Warm water, washing-up liquid and a soft sponge, then dry it with a cloth: no "
            "scouring pad, no wire wool and no metal tools, because a scratch in the coating is "
            "what ruins it. For burnt-on food, simmer a little water in the pan for five minutes "
            "and lift it with a wooden spatula rather than scraping. If the coating is flaking or "
            "peeling, replace the pan - that is not something to cook through.")


# A cup of tea is four things people get wrong in the same order: fresh water, water just off
# the boil, enough time, and taking the bag out before it turns bitter. The other three shapes -
# a pot, iced tea and the cloudy cup - are the same subject and different answers, so one row
# reads the line and picks, the way the coffee fault row does.
TEA_METHOD_TEXT = (
    "Fresh water boiled once, one teabag per mug, three to four minutes and then the bag out: "
    "that is the whole of a good cup, and the milk goes in last. Green tea wants cooler water, "
    "about 80C, for two to three minutes, and black tea wants it just off the boil, three to "
    "five. Bitter tea has steeped too long in water that was too hot, and a mug that tastes of "
    "the last one is a bag left sitting in it.")


TEA_POT_TEXT = (
    "Warm the pot first with a splash of boiling water swirled round and tipped away, then one "
    "teabag or one teaspoon of leaves per cup and one extra for the pot, water just off the "
    "boil, three to four minutes. Take the bags or leaves out before it goes to the table, and a "
    "cosy keeps the second cup hot without stewing it.")


TEA_ICED_TEXT = (
    "Cold brew it: eight teabags to a litre of cold water in the fridge overnight, bags out in "
    "the morning, then lemon and sugar to taste, which has none of the bitterness of a hot brew "
    "cooled down. In a hurry, brew double strength in a mug of boiling water for four minutes, "
    "take the bags out, and pour it over a jug of ice.")


TEA_CLOUDY_TEXT = (
    "Cloudy tea is the minerals in hard water binding with the tannin, and it is harmless to "
    "drink: filter the water, or use bottled, to get it clear, or add a small pinch of "
    "bicarbonate of soda to the pot, which keeps the tannin dissolved. It is not a dirty kettle "
    "and it is not a sign the tea has gone off.")


TEA_FAULT_TEXT = (
    "Green tea wants water at about 80C for 2 to 3 minutes; black tea wants it just off the "
    "boil for 3 to 5. Bitter tea is nearly always tea that steeped too long in water that was "
    "too hot, and sour or stewed tea is a pot left standing on a warmer or in the leaves: "
    "pour it off them and make the next one weaker and shorter.")


# Green tea is the one brew with its own temperature, and the plain method opens with boiling
# water: "how do i make green tea" and "how do i make a cup of green tea with a teabag" got the
# black-tea card the moment the method row took those lines back from the green-tea fact.
TEA_GREEN_TEXT = (
    "Green tea wants water at about 80C rather than boiling, for two to three minutes: boil the "
    "kettle and let it stand for a minute or two, or add a splash of cold water first. Water "
    "straight off the boil makes it bitter, and green tea goes bitter quickly, so pull the bag "
    "out at three minutes and drink it soon after.")


TEA_TWICE_TEXT = (
    "A second cup from the same teabag is weak and mostly colour, but it is harmless: if you "
    "want it stronger, use a fresh bag and pull it out sooner instead. Reuse one within the same "
    "hour at most, and not once it has been sitting in milk.")


def _rice_time(memory, understood):
    """The time the line asked about: brown and wholegrain rice take twice as long as white.

    The same entry answers two questions - how long it takes, and how much water it wants - so the
    answer opens on the one that was asked. "How long does rice take" used to get the ratio first
    and the minutes in the middle of the paragraph, which is STYLE.md's miss: a good paragraph
    about rice that is not the answer to the question. The brown answer already opened on its time
    (`test_a_brown_rice_question_leads_with_the_brown_rice_time`), and this is the same rule for
    the white one. A water question keeps the water first, because that is what it asked.
    """
    words = set((understood or {}).get("words") or ())
    asks = set((understood or {}).get("asks") or ())
    brown = words & {"brown", "wholegrain", "whole"}
    if brown:
        return ("Brown rice takes 25 to 30 minutes, with a little more water: 1 part rice to 2 "
                "parts water, lid on, low simmer. Let it sit 5 minutes off the heat, still covered, "
                "before you fork it through. White long grain is 1 part rice to 1.5 parts water for "
                "12 minutes, then 10 minutes off the heat. Too much water is what turns rice to "
                "porridge.")
    if asks & {"how_long", "when"}:
        # The minutes first, the ratio after them, for the same reason the brown row does it.
        return ("White long grain takes 10 to 12 minutes on a low simmer with the lid on, then 10 "
                "more off the heat. Use 1 part rice to about 1.5 parts water by volume, or the "
                "fingertip test: water one knuckle above the rice. Brown and wholegrain are the "
                "ones that take longer. Too much water is what turns rice to porridge.")
    return ("Use 1 part rice to about 1.5 parts water by volume for long grain, or the fingertip "
            "test: water one knuckle above the rice, and give it 12 minutes on a low simmer with the "
            "lid on, then 10 more off the heat. Brown and wholegrain rice are the ones that take "
            "longer. Too much water is what turns rice to porridge.")


# The ways a line says the loaf has none of the yeast this answer is about.
_NO_YEAST = ("no yeast", "without yeast", "yeastless", "yeast free", "yeast-free",
             "no need for yeast", "dont need yeast", "don't need yeast")


def _bread_rise_answer():
    """Why a loaf or a dough is slow, worded for the prove the person is actually doing.

    A night in the fridge is a deliberate slow prove - telling that person to find somewhere warm
    undoes it - and "do I need to prove it twice" is a question about the second, shaped prove.
    The time comes first, because that is what was asked; the reason follows it.
    """
    def answer(memory, understood):
        # only this line: a fridge mentioned two turns ago is not this prove
        said = str(understood.get("clean") or " ".join(understood.get("words") or [])).lower()
        # There is no rise to explain when there is no yeast in the loaf: a soda loaf is the
        # no-yeast recipe's line, and proving words cannot apply to it.
        if any(one in said for one in _NO_YEAST):
            return None
        # A sourdough loaf does not rise on warmth and a sachet of yeast: what lifts it is the
        # starter, and "my sourdough is flat" was told to leave it an hour at 25C "until the dough
        # has doubled", which is the advice for a yeasted loaf and never fixes a weak starter.
        if "sourdough" in said or "sour dough" in said or "starter" in said:
            return ("A sourdough loaf rises on the starter, not on warmth alone: a starter that "
                    "doubles in 4 to 6 hours after a feed is strong enough to bake with, and one "
                    "that only bubbles is not, so feed it twice a day for three days first. Then "
                    "give the bulk 4 to 6 hours at room temperature with three or four sets of "
                    "stretch and fold in the first two hours, and shape it with real tension. A "
                    "flat loaf usually wants a stiffer dough and a longer, colder second prove.")
        if "fridge" in said or "overnight" in said or "in the cold" in said:
            return ("A night in the fridge is a slow prove on purpose, not a fault: shape it cold, "
                    "then leave it an hour at room temperature before it goes in the oven. If it "
                    "hasn't risen at all by the morning, the yeast is dead, so check the date.")
        if "twice" in said or "second prove" in said or "second rise" in said or "two proves" in said:
            return ("Yes, twice: the first is done when the dough has doubled, and the second is the "
                    "shaped loaf, about an hour, until it springs back slowly when you poke it. "
                    "Skipping the second gives you a tight, close crumb.")
        if ("wont" in said or "won't" in said or "isnt" in said or "isn't" in said
                or "not rising" in said or "didnt" in said or "didn't" in said
                or "hasnt risen" in said or "stalled" in said):
            return ("Give it another hour somewhere around 25C, until it has doubled, and check the "
                    "water was warm rather than hot and that the yeast is in date. If it still "
                    "hasn't moved at all, the yeast is dead, so start again with fresh yeast.")
        return ("Leave it somewhere around 25C for 1 to 2 hours, until the dough has doubled. Yeast "
                "eats the sugars in the flour and gives off gas, and the stretchy gluten holds it "
                "in bubbles, so warmth and time are the whole job. If it hasn't moved at all, the "
                "yeast is dead, so check the date and use water that's warm rather than hot.")
    return answer


# A bitter cup and a sour one are the same dial turned opposite ways, so they share one entry.
# The first sentence is still the user's own word: "why does my coffee taste sour" was told
# "Bitter coffee is over-extracted" and had to read on to the third sentence for its answer.
_COFFEE_BITTER = (
    "Bitter coffee is over-extracted: grind it coarser, let the water come off the boil for half "
    "a minute, and take it off the grounds sooner - about 4 minutes in a cafetiere, 25 to 30 "
    "seconds for an espresso. Sour is the same dial the other way and wants a finer grind, hotter "
    "water and a little longer. Stale beans and a dirty machine make both, and instant tastes "
    "bitter when it is made with boiling water - let the kettle rest first.")


_COFFEE_SOUR = (
    "Sour coffee is under-extracted: grind it finer, use water just off the boil rather than "
    "boiling, and give it longer on the grounds - about 4 minutes in a cafetiere, 25 to 30 "
    "seconds for an espresso. Bitter is the same dial the other way and wants a coarser grind and "
    "a shorter brew. A sour note that only shows up with milk is usually the milk.")


_COFFEE_BURNT = (
    "A burnt taste is over-extraction or too dark a roast: grind it coarser, let the water come "
    "off the boil for half a minute and shorten the brew, and try a medium roast instead of a "
    "dark one. Scrub the pot and the filter basket too, because old oils go acrid and taste "
    "burnt even with fresh beans.")


def _coffee_fault(memory, understood):
    """The fault the line named, said back to them: sour, burnt or the bitter default."""
    words = set(re.findall(r"[a-z']+", (understood or {}).get("clean") or ""))
    if words & {"sour", "soured", "acidic", "acid", "vinegary"}:
        return _COFFEE_SOUR
    if words & {"burnt", "burned", "burning", "scorched", "scorching"}:
        return _COFFEE_BURNT
    return _COFFEE_BITTER


# The leaves people keep in the fridge door - lettuce, spinach, rocket, a bag of mixed greens -
# are one subject, so the names live in one tuple that two entries share. Keeping the next bag
# crisp and bringing a limp one back are different answers, so they are separate entries:
# whichever way the line leans, the first sentence is the fix it needs.
LEAFY = ("salad", "lettuce", "leaves", "leafy", "greens", "spinach", "rocket", "arugula",
         "watercress", "salad leaves", "mixed leaves", "lambs lettuce")


# A slug, a plant in the garden and a person who is not well are not a bag of leaves: "my baby
# is limp" is a 999 line, so the words that make a line about a body or a bed take it away.
LEAFY_AVOID = ("slug", "slugs", "snail", "pest", "garden", "grow", "growing", "plant", "plants",
               # "baby spinach" is a bag of leaves, so the baby words are the possessive ones;
               # the word alone kept the commonest bag in the shop out of the answer
               # ("babies" cannot be here either: _forms() makes it a form of "baby", and it
               # would veto "baby spinach" the same way)
               "my baby", "the baby", "baby is", "baby has", "a baby", "newborn",
               "child", "children", "toddler",
               "dog", "dogs", "cat", "cats", "puppy", "feel", "feeling", "tired", "exhausted",
               "weak", "unwell", "limp after", "run",
               # "and how long does that take" is a cooking time: the composer puts the subject
               # of the turn before it back on the end ("how long does the spinach take"), so the
               # bare verb goes in too, not just the phrases
               "that take", "does that take", "will that take", "this take", "it take",
               "take", "takes", "taking", "took",
               # "i have a bag of spinach going limp, what can i do with it" is asking for a
               # dish, not for a way to crisp it up: the meal table answers those lines
               "what can i make", "what can i do with", "what should i make", "use up",
               "use it up", "recipe", "recipes", "cook", "cooking", "soup", "pan", "side dish",
               # a drink made from leaves is not a bag of leaves: "how long to infuse loose leaf
               # tea" was answered with five days in the salad drawer, because "leaf" is in this
               # subject and the tea is not
               "tea", "teas", "infuse", "infusing", "infused", "brew", "brewing", "brewed",
               "coffee")


# A pan with a *dish* burnt into it is the dish's question, not the pan's: "i burnt the garlic in
# the pan" was told to simmer bicarbonate in it, and "i burnt the bottom of a pan of rice" was
# told nothing at all, because burnt-pan avoided the word rice and fix-burnt avoided the word
# pan. The cleaning words are what tell the two apart: a line that asks how to get it off wants
# the bicarbonate, and a line that says what it burnt wants the rescue. A pan with nothing named
# burnt in it is still the pan question.
_PAN_DISH = ("rice", "sauce", "soup", "stew", "curry", "porridge", "pasta", "potatoes",
             "eggs", "chicken", "meat", "fish", "mince", "cake", "gravy", "custard", "beans",
             # an omelette, a frittata and a fried egg are dishes named for themselves, and the
             # word "pan" in the line is where they cooked rather than what is burnt: "my
             # omelette stuck to the pan" was the bicarbonate-of-soda cleaning card, and the
             # omelette rows that answer it lost to it on the registry's order alone. The dish
             # words live here so a pan line that names a dish is the dish's, which is what the
             # rest of this list already does for rice, sauce and cake.
             "omelette", "omelettes", "omelet", "omelets", "frittata", "frittatas",
             "scrambled egg", "fried egg", "poached egg", "pancake", "pancakes",
             "lentils", "chilli", "beef", "pork", "lamb", "veg", "vegetables", "noodles",
             "garlic", "onion", "onions", "bread", "steak", "bacon", "sausages", "oats",
             "tomato", "tomatoes", "mushrooms", "cheese", "butter", "oil", "toast")


_PAN_CLEAN = ("clean", "cleaning", "cleaned", "scrub", "scour", "soak", "soaking", "wash",
              "washing", "comes off", "come off", "off the bottom", "off my pan", "off the pan",
              "off the inside", "off the base", "get it off", "gets it off", "still stuck",
              "stuck on", "wont come", "won't come",
              # a tin is cleaned the same way a pan is, and "off the tin" is how people say it:
              # "how do i get the burnt off my cake tin" was answered with butter and flour
              "off the tin", "off my tin", "off the tray", "off my tray", "off the sheet",
              "get the burnt off", "burnt off", "stained")


_BURNT_PAN_REPLY = ("Put an inch of water and two tablespoons of bicarbonate of soda in it and "
                    "simmer for ten minutes, then lift the burnt layer with a wooden spoon: "
                    "almost nothing needs scrubbing after that. Stainless steel and enamel can "
                    "take a vinegar soak instead, but never scour a non-stick pan, since it "
                    "takes the coating off for good.")


# A pan with no dish named burnt in it is the pan's question, so `fix-burnt` hands those lines
# back: "food stuck to the bottom of the pan" has nothing burnt in it, and the rescue below would
# tell the person to treat their dinner as burnt.
_PAN_WORDS = ("pan", "pans", "pot", "pots", "saucepan", "saucepans", "wok", "tray", "trays",
              "casserole", "skillet")


# How a person asks for the burnt layer to come out of the pan: "get burnt milk out of a pan"
# and "get burnt sugar out of a pan" are both the pan's to clean, and the pot keeps the burnt
# dish's answer for a dish that went wrong ("i burnt the sauce in a pan").
_REMOVAL_FROM_A_PAN = ("out of the pan", "out of my pan", "out of a pan", "out of the pot",
                       "out of my pot", "out of a pot", "out of the wok", "out of the saucepan",
                       "out of the casserole", "out of it", "out of there", "get it out",
                       "get the burnt out", "get the burnt off", "get it off")


# Something burnt on a pan and to be got off it: "get burnt milk out of a pan", "how do i get
# burnt milk off the bottom of a pan", "the pan has burnt black on the outside". Each of these is
# a pan to clean, and three different entries were taking them - the oil's, because its key has a
# bare "burnt" beside "pan", the sugar's, because a burnt caramel is its own answer, and the
# burnt dish's. The thing that burnt is not what the person asked about: the pan is.
_BURNT_ON_A_PAN = _REMOVAL_FROM_A_PAN + (
    "off the pan", "off my pan", "off a pan", "off the bottom", "off my bottom", "off the base",
    "off the inside", "off the outside", "burnt on", "burned on", "burnt-on", "burnt black",
    "burned black", "black on the outside", "black on the bottom", "black outside",
    "scorched on the outside", "scorched on the bottom",
    # "how do i get rid of a scorch mark on a pan" names the pan in the middle of the line,
    # not at the end of a "get X off" phrase, and reached the oil-disposal answer.
    "on the pan", "on my pan", "on a pan", "in the pan", "in my pan", "on the saucepan",
    "on the tray", "in the tray", "on the bottom of the pan", "at the bottom of the pan",
    # The line usually says what was burnt and not how to get it off: "i burnt the bottom of a
    # pan" and "i burnt a pan" were both told the fat was past its smoke point, which is a
    # lecture about heat when the job is the soak. A pan named as burnt is the pan's question
    # however the sentence is put together.
    "burnt the bottom of", "burned the bottom of", "burnt a pan", "burned a pan",
    "burnt my pan", "burned my pan", "burnt the pan", "burned the pan", "burn the pan",
    "burnt my saucepan", "burnt the saucepan", "burnt a saucepan", "burned my saucepan",
    "burnt my pot", "burned my pot", "burnt the pot", "burnt a pot", "burnt my wok",
    "burnt the tray", "burnt my tray", "burnt the base of", "burnt a frying pan")


def _burnt_on_the_pan(text):
    """True for a pan with something burnt on it that the person wants off."""
    # "how do i get rid of a scorch mark on a pan" reached the oil-disposal answer through "get
    # rid": a mark on the pan is the pan's job, not the fat's, so a scorch, a stain and a scratch
    # count as burnt on it too.
    return (_says(text, _BURNT_ON_A_PAN)
            and _says(text, ("burnt", "burned", "black", "blackened", "scorched", "scorch",
                             "burn mark", "scorch mark", "scorched on", "stain", "stained",
                             "discoloured", "discolored", "scratch", "scratched")))


_BURNT_DISH_REPLY = ("Take it off the heat and lift out the burnt bits rather than stirring them "
                     "in, because the smoky taste spreads through everything. If it has gone all "
                     "the way through, a splash of stock and something creamy hides a little of "
                     "it, but a properly burnt sauce is better started again.")


# A joint in a tin is not a pot on a hob: "take it off the heat and lift out the burnt bits rather
# than stirring them in" was the answer to "my roast is burnt", and there is nothing to lift out of
# a roast. The meat's own rescue is to carve the burnt edge away and keep the juices off the gravy.
_BURNT_MEAT = ("roast", "joint", "chicken", "turkey", "lamb", "beef", "pork", "gammon", "duck",
               "steak", "sausage", "sausages", "bacon", "ham", "ribs", "brisket", "meatloaf",
               "meatballs", "whole chicken", "thighs", "drumsticks", "wings")


_BURNT_MEAT_REPLY = (
    "Take it out of the tin and carve or cut the black edge away rather than scraping at it, and "
    "taste a slice from the middle before you decide anything, because a joint that caught on one "
    "side is usually fine underneath. Leave the burnt fat and juices in the tin instead of pouring them "
    "into the gravy, and if the middle is still underdone, cover the joint with baking paper and "
    "give it another 10 to 15 minutes at 20C lower. Next time stand it on a rack or a bed of onion "
    "and carrot so it is not sitting in the tin, and cover it loosely once it has browned.")


# A roast potato is not a joint. "the roast potatoes burnt" was told to carve the black edge off
# and keep the burnt juices out of the gravy, because "roast" on its own is a joint word.
_BURNT_VEG = ("potato", "potatoes", "parsnip", "parsnips", "carrot", "carrots", "swede",
              "turnip", "sprouts", "broccoli", "cauliflower", "onion", "onions", "chips",
              "roast veg", "roast vegetables", "vegetables", "veg", "squash", "pumpkin",
              "courgette", "courgettes", "aubergine", "peppers", "beetroot", "sweet potato",
              "sweet potatoes", "leek", "leeks", "kale", "cabbage")


_BURNT_VEG_REPLY = (
    "Cut the black edges off with the corner of a spatula rather than scraping them, toss what is "
    "left in a fresh spoon of oil and give it 10 more minutes at 20C lower: a roast vegetable "
    "catches on the edges long before the middle. Anything black right through goes in the bin, and "
    "a tray that is badly caught is better mashed with butter than carved.")


# Batter catches as batter: a Yorkshire or a toad in the hole is a pan of hot fat and a poured
# mix, so there is nothing to lift the burnt bits out of and nothing to carve.
_BURNT_BATTER = ("yorkshire", "yorkshires", "yorkshire pudding", "yorkshire puddings",
                 "toad in the hole", "batter", "popover", "popovers", "dutch baby")


_BURNT_BATTER_REPLY = (
    "Cut the black tops off rather than scraping them and eat the rest: batter burns because the "
    "fat was smoking before it went in, or the tin sat too high. Next time put the tin on the middle "
    "shelf, get the fat hot but not smoking - a drop of batter should sizzle rather than spit - pour "
    "the batter in cold, and do not open the door for the first 20 minutes.")


# The other half of a burnt dinner: whether it is still all right to eat. "is burnt food bad for
# you", "can you eat burnt food", "does burnt meat cause cancer" and "is charred meat bad for you"
# were the pot's rescue (lift the burnt bits out), a bread card and a punt - none of them answers
# it, and the toast entry's acrylamide sentence is the only place the eating side was written.
_BURNT_EATING_ASK = ("bad for", "bad for you", "bad for me", "harmful", "dangerous",
                     "cancer", "carcinogen", "carcinogenic", "poison", "poisonous", "toxic",
                     "safe to eat", "still eat", "can i eat", "can you eat", "can i still",
                     "ok to eat", "okay to eat", "alright to eat", "healthy", "unhealthy",
                     "does it matter", "is it ok", "is it okay", "is it safe", "is it bad",
                     "is charred", "is burnt food", "burnt food bad", "charred food bad",
                     # the burnt thing named as food rather than as a dish in a pan: "what about
                     # burnt bbq food" was the grill's cleaning card, then the pan's rescue.
                     "burnt food", "burned food", "charred food", "burnt meat", "charred meat",
                     "bbq food", "barbecue food")


_BURNT_EATING_REPLY = (
    "It is not poisonous, and one burnt dinner is nothing to worry about. The black is carbon, plus "
    "acrylamide where the food was starchy - bread, potatoes, chips - and other compounds where it "
    "was meat, and the advice is about habit rather than about a single meal. So scrape the black "
    "off toast and roast potatoes and eat the rest, cut the charred edge off meat, and keep properly "
    "blackened food to the odd occasion rather than most weeks. The fat that drips onto a hot grill "
    "and smokes is best kept off the food: cook a little slower and turn things instead of leaving "
    "them in one spot.")


# The parts of a roast that are not the joint and that main's vegetable list does not name:
# they catch on top, the black comes off with a knife, and there is nothing to carve. "the
# stuffing burnt" and "the crackling burnt" got an echo, because neither word was a food this
# package knew.
_ROAST_PARTS = ("stuffing", "crackling")


_ROAST_PART_REPLY = (
    "Cut the burnt patches away and keep what is underneath - whatever caught on top is usually "
    "fine in the middle, and a black patch comes off with a knife before it goes on the plate. If "
    "what is left is dry, spoon a little stock or gravy over it, and next time put it in later "
    "than the joint, so it gets less time at the heat.")


# Words that name something being *baked*, as against the tin or the oven it bakes in. A line
# with none of these is not asking about a cake: "the inside of my oven is burnt on", "my baking
# tray is burnt on how do i clean it" and "burnt on grease on the oven door" were all told to lay
# foil over the top, which is the rescue for something still in the oven and going brown. The tin
# and the oven are in the entry's key because a bake question names them, so the gate for this
# reply is whether a bake is named at all.
_BAKE_NOUNS = ("cake", "cakes", "sponge", "loaf", "bread", "buns", "biscuits", "cookies",
               "muffins", "brownies", "cheesecake", "pastry", "pie", "pies", "tart", "tarts",
               "traybake", "scones", "flapjack", "quiche", "yorkshire", "pizza", "madeira",
               "fruit cake", "victoria sponge", "bakewell")


_GRIME_WORDS = ("grease", "greasy", "stuck", "stuck on", "marks", "mark", "stains", "stained",
                "clean", "cleaning", "cleaned", "scrub", "scrubbing", "scour", "soak",
                "soaking", "bicarbonate", "get off", "get it off", "comes off", "wipe",
                "wiping", "washing", "washed")


_TIN_OR_OVEN = ("oven", "tin", "tray", "hob", "grill", "glass", "rack", "shelf", "dish",
                "plate", "pan", "cooker", "door", "inside")


# "a cake tin", "a pie dish", "a muffin tray": the bake's name is in front of the vessel, and the
# vessel is what got burnt on. So the vessel phrase comes out before the bake is looked for.
# "the oven is burnt on", "something baked on the tray": the bake name is missing and the vessel
# is what got black, so this is the cleaning question however the line is worded. Without this the
# bottom words put those lines on the bake answer and they were told to lay foil over the top.
_BURNT_ON = ("burnt on", "burned on", "baked on", "stuck on", "stuck", "black inside",
             "inside of my oven", "black on the inside", "black at the back")


def _words_and_text(understood):
    """The line as one lower-case string, with the word list unquoted and joined by spaces.

    `norm` holds a list, and dropping it in with str() writes the brackets and quotes into the
    text, so "cake tin" came out as "cake', 'tin" and no phrase in it could be read.
    """
    parts = []
    for key in ("clean", "norm_text"):
        parts.append(str((understood or {}).get(key) or ""))
    words = (understood or {}).get("norm")
    if isinstance(words, (list, tuple)):
        parts.append(" ".join(str(word) for word in words))
    else:
        parts.append(str(words or ""))
    return " ".join(parts).lower()


def _says(said, phrases):
    """True when one of these phrases is in the line as whole words.

    Whole words, because "sauce" is not in "saucepan": a saucepan burnt inside was read as a dish
    of sauce and this entry passed the line to fix-burnt, which had nothing for it.
    """
    return re.search(r"\b(?:%s)\b" % "|".join(re.escape(one) for one in phrases), said) is not None


def _burnt_pan(memory, understood):
    """The pan's answer for a pan line, and nothing for a line whose dish is what burnt."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    if _says(said, _PAN_CLEAN):
        return _BURNT_PAN_REPLY
    if _says(said, _PAN_DISH):
        return ""       # a dish is burnt, not the pan: fix-burnt has that line
    return _BURNT_PAN_REPLY


# A burnt top on a cake is not a burnt pan of sauce: nothing is stirred, and the answer is the
# oven and the foil. The pot line stays for everything that is actually in a pan.
_BAKED_BURNT = ("cake", "cakes", "sponge", "loaf", "loaves", "bread", "buns", "bun", "scones",
                "scone", "muffins", "muffin", "brownies", "brownie", "biscuits", "biscuit",
                "pastry", "pie", "tart", "quiche", "roast potatoes", "roasties", "chips", "fries")


_TIN_SIZE = ("A 2lb loaf tin is 19 x 11cm for a 900g loaf and a 1lb tin is 15 x 9.5cm for a "
             "450g one; a 20cm round cake tin takes the 4-egg sponge and an 18cm one the 3-egg.")


_TIN_FILL = ("Fill a bread tin two-thirds full and a cake tin three-quarters at most.")


_TIN_LINE = ("Line bread with baking parchment; for a cake, grease the tin and line only the base, "
             "because loose paper at the sides makes the sponge climb rather than rise.")


_TIN_GREASE = ("Rub the inside of the tin all over with butter or a little oil, then dust it with "
               "flour and tip the extra out; a circle of baking paper on the base does the same job.")


_TIN_FRUIT = ("A fruit cake or a Christmas cake wants a deep tin, not a sponge tin: a 20cm round "
              "one for a 2kg mix, lined with a double thickness of parchment and a collar of "
              "paper round the outside, because it bakes for two and a half hours or more.")


# What the line asks for comes first: a tin is three questions in the same words, and a person
# asking how to grease a tin should not have to read two sentences about loaf sizes to find it.
_TIN_GREASE_WORDS = ("grease", "greased", "greasing", "butter the", "dust with flour", "dust it")


_TIN_LINE_WORDS = ("line", "lined", "lining", "parchment", "baking paper", "greaseproof", "paper",
                   "line it", "line the")


_TIN_FRUIT_WORDS = ("fruit cake", "christmas cake", "rich fruit", "wedding cake", "simnel",
                    "dark fruit")


def _tin_answer(memory, understood):
    """Lead with the question the tin was named in: its size, its lining, or a fruit cake's tin."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    if any(word in said for word in _TIN_FRUIT_WORDS):
        return " ".join((_TIN_FRUIT, _TIN_SIZE))
    if any(word in said for word in _TIN_LINE_WORDS):
        return " ".join((_TIN_LINE, _TIN_SIZE, _TIN_FILL))
    if any(word in said for word in _TIN_GREASE_WORDS):
        return " ".join((_TIN_GREASE, _TIN_SIZE))
    return " ".join((_TIN_SIZE, _TIN_FILL, _TIN_LINE))


_CAKE_FAULT_WORDS = (
    ("domed", "dome", "domes", "doming", "raised in the middle", "rises in the middle"),
    ("cracked", "cracks", "cracking", "crack", "split on top", "splits on top"),
    ("eggy", "tastes of egg", "taste of egg", "smells of egg", "egg taste", "tasting of egg"),
    ("soggy bottom", "soggy underside", "wet bottom", "soggy base"),
)


def _cake_fault(memory, understood):
    """A dome, a crack, an eggy taste and a soggy bottom are four different mistakes."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    words = said
    if any(word in words for word in _CAKE_FAULT_WORDS[0]):
        return ("A dome is the outside setting before the middle has caught up: bake 10C lower, "
                "170C (150C fan) on the middle shelf, use the tin the recipe names rather than a "
                "smaller one, and stop beating the moment the flour is in. Trim the dome flat with "
                "a bread knife before you fill it, and nobody sees it.")
    if any(word in words for word in _CAKE_FAULT_WORDS[1]):
        return ("A split top is the crust setting while the middle is still rising: lower the oven "
                "10C, put the tin on the middle shelf, and keep the door shut for the first 20 "
                "minutes. Cool it in the tin for 10 minutes, then on a rack, because a cake cooled "
                "in a hot tin goes clammy and splits.")
    if any(word in words for word in _CAKE_FAULT_WORDS[2]):
        return ("An eggy taste is too many eggs for the flour or a bake that stopped a few minutes "
                "short: add a quarter teaspoon of salt and a teaspoon of vanilla or the zest of a "
                "lemon, and give it 5 more minutes, checking with a skewer. The same mix tastes "
                "eggier cold, so try it once it has cooled rather than from the tin.")
    if any(word in words for word in _CAKE_FAULT_WORDS[3]):
        return ("A soggy bottom is underbaked underneath: use a metal tin rather than a ceramic "
                "dish, bake on the middle shelf and not above a tray of water, and give it 5 to 10 "
                "minutes longer with foil over the top once it is brown. A cold filling or a wet "
                "fruit layer under a thick batter does the same thing.")
    # the rise itself: "how do i get cakes to rise evenly"
    return ("An even rise is a level batter and a steady oven: sift the raising agent through the "
            "flour rather than adding it last, spread the batter level with the back of a spoon, "
            "and use a tin that the mix fills by two thirds. Turn the tin once, after 15 minutes, "
            "if your oven browns the back corner first.")


_PASTRY_SHRINK_WORDS = ("shrink", "shrank", "shrunk", "shrinking", "shrinks", "pulled away",
                        "pulls away", "slid down", "slides down", "slumped", "slumps",
                        "slumping", "limp")


def _pastry_fault(memory, understood):
    """A shrunken case and a soggy base are fixed in different places: the chill and the heat."""
    said = " ".join(str((understood or {}).get(key) or "")
                    for key in ("clean", "norm_text", "norm")).lower()
    if any(word in said for word in _PASTRY_SHRINK_WORDS):
        return ("Pastry shrinks when it is stretched into the tin: press it gently into the corners "
                "rather than pulling the sides up, chill the lined case for 20 minutes before it "
                "goes in, and leave the overhang on until after baking, because the spare pastry "
                "holds the sides up while they set.")
    return ("A soggy pastry base wants more heat underneath it and less water in the filling: "
            "blind bake it 5 minutes longer than the recipe says, brush the warm base with beaten "
            "egg white before the filling goes in, and stand the tin on a hot baking sheet so the "
            "heat reaches the pastry rather than stopping at the filling.")


_BAKE_PREVENTION = (
    "Lay a sheet of foil loosely over the top as soon as it starts to colour, and turn the "
    "oven down 10 to 20C (or move the tin a shelf lower): a cake that catches on top is "
    "nearly always an oven running hot, a shelf too high or a dark tin, not the mixture. If "
    "the top is brown and the middle still wobbles, cover it and give it another 10 to 15 "
    "minutes rather than turning the heat up. If the bottom is already black, cut that off, "
    "trim the dark top and serve the rest - and next time check your oven with a thermometer, "
    "since most run 10 to 20C hotter than the dial says.")


_BAKE_BURNT = (
    "Cut or grate the black off once it has cooled, and if only the top is dark the rest is "
    "fine - a dark top on a fruit cake is often just the sugar. If the middle is still wet, "
    "cover the tin loosely with foil and give it another 10 to 15 minutes. Next time move the "
    "oven shelf down one and tent the tin with foil after 20 minutes, because a bake burns on "
    "top while the middle is still wet.")


_BAKE_BOTTOM_REPLY = (
    "Lift the shelf up one, slide a baking sheet or two under the tin to take the direct heat and "
    "drop the oven 10C, because a bottom that burns first means too much heat from underneath and "
    "a hot oven burns the base while the middle is still wet. Line a dark or thin tin with baking "
    "paper, and turn the tin if one corner of the oven browns hard. If the top is browning before "
    "the middle is set, lay a sheet of foil loosely over it so the base can catch up. If the "
    "bottom has already caught, cut or grate the black off and eat the rest, and check the oven "
    "once with a thermometer, since most run 10 to 20C hotter than the dial says.")


def _burnt(memory, understood):
    """What burned changes the rescue: a pan is lifted off the heat, a bake is cut and covered."""
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    said = " ".join(words)
    if any(_same(word, bake) for word in words for bake in _BAKED_BURNT) or any(
            " " in bake and bake in said for bake in _BAKED_BURNT):
        return ("A burnt top on a bake is usually saveable: take it out at once, cover the tin loosely "
                "with foil so the middle carries on cooking, and when it is cool cut the black off "
                "with a serrated knife or grate it away - a dark top on a fruit cake is often just "
                "the sugar. Next time move the shelf down one, drop the oven 10C and tent the tin with "
                "foil after 20 minutes, because a bake burns on top while the middle is still wet.")
    if any(word in ("toast", "toaster") for word in words):
        return ("Scrape the black off with a knife and eat the rest: burnt toast is not dangerous, and "
                "a scrape takes the bitter taste with it. Next time set the toaster one notch lower "
                "and stay next to it, because toast goes from golden to black in under a minute.")
    return ("Take it off the heat and lift out the burnt bits rather than stirring them in, because "
            "the smoky taste spreads through everything. If it has gone all the way through, a splash "
            "of stock and something creamy hides a little of it, but a properly burnt sauce is better "
            "started again.")


# Greasy is one word and four different faults: frying oil that was not hot enough, fat left on a
# stew, a roast sitting in its own tin, and a wet filling under pastry. The food in the line picks
# the fix, so a person who says "my chips are greasy" is not told to skim a stew.
_FRIED_GREASY = ("chips", "chip", "fries", "fry", "pakora", "pakoras", "onion rings", "doughnut",
                 "doughnuts", "tempura", "batter", "fried", "sweet potato fries")


_POT_GREASY = ("stew", "curry", "sauce", "soup", "gravy", "chilli", "bolo", "bolognese", "ragu",
               "casserole", "dal", "daal", "stir fry", "stirfry", "stir-fry", "mince")


_MEAT_GREASY = ("roast", "chicken", "steak", "lamb", "pork", "beef", "sausage", "sausages",
                "bacon", "duck", "turkey", "gammon", "burger", "burgers", "meatballs")


_PASTRY_GREASY = ("quiche", "pie", "tart", "pastry", "pastry case", "flan")


def _greasy(memory, understood):
    """Greasy food, with the cause the food actually has."""
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    said = " ".join(words)
    have = lambda names: (any(_same(word, wanted) for word in words for wanted in names)  # noqa: E731
                          or any(" " in wanted and wanted in said for wanted in names))
    if have(_FRIED_GREASY):
        return ("Greasy fried food means the oil was not hot enough, so the food steamed instead of "
                "sealing and took the fat up like a sponge: 180C for chips and about 190C for a "
                "batter, test it with a cube of bread that should sizzle and go golden in 30 seconds, "
                "and do not crowd the pan, because the temperature drops as soon as it is full. "
                "Drain on a rack or kitchen paper, never on a plate, and salt it the moment it comes out.")
    if any(_same(word, wanted) for word in words
           for wanted in ("roast potatoes", "roasties", "potatoes", "potato", "wedges",
                          "hash browns")) and any(_same(word, wanted) for word in words
                                                  for wanted in ("roast", "roasted", "oven")):
        return ("Greasy roast potatoes mean the oil was not hot enough or the tin was crowded: parboil "
                "them 8 minutes, drain and shake the pan to rough the edges, then roast them in a "
                "thin layer of oil that is already smoking hot at 200C (180C fan), in one layer with "
                "room between them. Cold oil, or a full tin, is what leaves them oily, and a rack "
                "over the tin drains the rest.")
    if have(_PASTRY_GREASY):
        return ("A greasy pastry case is the filling rather than the pastry: cheese in a quiche gives "
                "up its fat, and mince in a pie floats it to the top. Drain the cooked filling in a "
                "sieve over a bowl, thicken it with a spoon of cornflour, and blind-bake the case "
                "first so the fat has somewhere to go; a layer of breadcrumbs on the base soaks up "
                "the rest.")
    if have(_MEAT_GREASY):
        return ("Most of that fat is meant to be there, so spoon it off rather than cook it away: tilt "
                "the tin and take the fat out with a spoon or a bulb baster, keeping a spoonful for "
                "the potatoes, and finish the meat uncovered at a higher heat for the last 10 minutes "
                "so the skin or the outside crisps. Resting it on a rack, not in the tin, keeps it "
                "out of the fat.")
    if have(_POT_GREASY):
        return ("Skim the fat off the top with a spoon, or lay a piece of kitchen paper flat on the "
                "surface and lift it out - that takes the oil and leaves the sauce. A stew that is "
                "still greasy wants the lid off for 10 minutes, and a spoon of something sharp "
                "(lemon, vinegar, tomato puree) cuts through what is left. Next time brown the meat "
                "and pour the fat out of the pan before the liquid goes in.")
    return ("Greasy comes from too much oil or oil that was not hot enough to seal the food: get the "
            "pan properly hot before anything goes in, shake the excess off in a sieve, and drain on "
            "kitchen paper rather than on a plate. In a sauce, skim the fat off the top with a spoon "
            "and finish with a squeeze of lemon.")


# A curdled custard is a broken emulsion's cousin with a different cause: the eggs got hot too
# fast and the protein in them set into grains, so the rescue is a sieve and a cooler pan.
_CUSTARD_NAMES = ("custard", "custards", "creme anglaise", "crème anglaise", "creme patissiere",
                  "crème pâtissière", "pastry cream", "custard tart", "custard tarts",
                  "custard filling", "creme caramel", "crème caramel")


def _split(memory, understood):
    """A split sauce has three different causes: heat, oil added too fast, and butter too hot."""
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    said = " ".join(words)
    if any(_same(word, name) for word in words for name in _CUSTARD_NAMES) or any(
            " " in name and name in said for name in _CUSTARD_NAMES):
        return ("A curdled custard is the eggs getting hot too fast, so the protein in them sets "
                "into grains: take it off the heat at once, whisk in a spoonful of cold cream or "
                "milk to stop it cooking, then push it through a sieve and it comes back smooth. "
                "Next time pour the hot milk into the beaten eggs a splash at a time, keep the pan "
                "over a low heat, stir all the time, and take it off at 82C, because a custard that "
                "comes to the boil will always curdle.")
    if any(word in ("mayonnaise", "mayo", "aioli", "garlic mayo", "garlic mayonnaise", "remoulade")
           for word in words):
        return ("Mayonnaise splits when the oil goes in faster than the yolk can take it up, so start "
                "again with a clean bowl: an egg yolk, a teaspoon of water and a pinch of salt, then "
                "the oil a drop at a time until it thickens and only then in a thin stream. To rescue "
                "a split one, put a fresh yolk in a clean bowl and whisk the split mayonnaise into it "
                "a spoon at a time - one yolk will bring back up to about a mugful.")
    if any(word in ("hollandaise", "béarnaise", "bearnaise", "butter sauce") for word in words):
        return ("Hollandaise splits when the bowl gets too warm or the butter goes in too hot: take "
                "the bowl off the water at once, add a teaspoon of cold water and whisk hard. If it "
                "will not come back, start a fresh yolk in a clean bowl with a spoon of water and "
                "whisk the split sauce into it a little at a time, off the heat. Next time keep the "
                "water barely trembling and let the melted butter cool for a minute first.")
    return ("A sauce splits when it gets too hot: take it off the heat and whisk in a spoonful of cold "
            "cream or butter to bring it back. Next time, lower the heat and add dairy at the end.")


# Undercooked is the other half of the fault table: a cake wet in the middle, rice still crunchy, a
# potato hard at the centre. What to do about it is the food's own next step, never one line.
_UNDER_BAKE = ("cake", "cakes", "sponge", "muffin", "muffins", "loaf", "loaves", "bread", "buns",
               "bun", "scone", "scones", "brownie", "brownies", "traybake", "yorkshire",
               "yorkshires", "pudding", "puddings", "pie", "tart", "quiche")


_UNDER_BREAD = ("bread", "loaf", "loaves", "sourdough", "bread roll", "bread rolls")


_UNDER_STARCH = ("rice", "couscous", "quinoa", "bulgur", "bulghur", "barley", "lentils", "lentil",
                 "porridge", "oats", "polenta", "pasta", "noodles", "noodle", "spaghetti",
                 "macaroni", "penne", "tagliatelle", "gnocchi", "dumplings", "dumpling")


_UNDER_VEG = ("vegetables", "vegetable", "veg", "greens", "potato", "potatoes", "carrots", "carrot", "parsnips", "parsnip", "swede", "turnip",
              "sprouts", "broccoli", "cauliflower", "cabbage", "beans", "peas", "leeks", "leek",
              "beetroot", "squash", "pumpkin", "courgette", "courgettes", "aubergine")


def _undercooked(memory, understood):
    """What is still hard changes the next step: a bake goes back in the oven, rice wants water."""
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    said = " ".join(words)
    have = lambda names: (any(_same(word, wanted) for word in words for wanted in names)  # noqa: E731
                          or any(" " in wanted and wanted in said for wanted in names))
    if have(_UNDER_BREAD):
        return ("A doughy loaf has not had long enough in the oven, or it did not prove enough: put it "
                "back in at 200C (180C fan) for 10 minutes, then turn it out and tap the base - a "
                "hollow sound means it is done, a dull thud means it wants 5 more. Next time let it "
                "prove until a poke springs back slowly and bake it to 96C in the middle rather than "
                "trusting the time on the packet.")
    if have(_UNDER_BAKE):
        return ("Put it back in the oven at 160C (140C fan) for 10 minutes with a sheet of foil "
                "loosely over the top, so the middle catches up without the top burning, and test it "
                "again with a skewer: it wants a few damp crumbs, not wet mixture. Next time drop "
                "the oven 10C and give it 5 minutes longer, and check with a skewer before you take "
                "it out - a cake that looks set and wobbles in the middle is not done.")
    if have(_UNDER_STARCH):
        return ("It wants more time and a little more water: a splash of hot water, the lid back on "
                "and 5 minutes on the lowest heat will finish rice, couscous or quinoa. Pasta and "
                "noodles go back into the boiling water for 2 to 3 minutes, and lentils want another "
                "10. Taste a piece rather than looking at the clock, because the packet time assumes "
                "a pan that came back to the boil quickly.")
    if have(_UNDER_VEG):
        return ("Boiled vegetables go hard in the middle when the pieces are different sizes or the "
                "water never got back to a rolling boil: cut them the same size, salt the water, and "
                "give them another 5 minutes, testing with the point of a knife - it should slide in "
                "with no resistance at all. Roast ones want 10 more minutes in a hotter oven, and "
                "parboiling potatoes for 8 minutes before they go in the tin stops the hard centre.")
    return ("It needs a few more minutes rather than more heat: cover it and give it 5, then test it "
            "with a knife or a skewer in the middle, where the heat gets last. A wider, shallower "
            "dish cooks through faster than a deep one.")


# The dip a line names decides the words it gets: houmous thickens in the fridge, tzatziki goes
# thin from a wet cucumber, and a split aioli comes back. Anything else gets the plain advice.
_DIP_FIXES = (
    (("houmous", "hummus", "humous"),
     "Houmous thickens in the fridge, so loosen it with a spoonful of cold water or lemon juice "
     "and a little more oil, taste for salt, and serve it at room temperature."),
    (("tzatziki", "raita", "yogurt dip", "yoghurt dip"),
     "Sit it in a sieve over a bowl for twenty minutes: thin tzatziki or raita is nearly always a "
     "wet cucumber, so squeeze the grated cucumber dry and stir it back in with a pinch of salt."),
    (("aioli", "mayonnaise", "mayo"),
     "A thin mayonnaise takes more oil whisked in slowly; a split one comes back from a fresh "
     "yolk in a clean bowl with the split mixture drizzled in a few drops at a time."),
    (("guacamole",),
     "Guacamole browns where the air gets at it: press cling film right onto the surface, keep "
     "the stone in the bowl if you have one, and a squeeze of lime slows it down. It is still "
     "fine to eat brown."),
    (("salsa",),
     "Drain the chopped tomato in a sieve for ten minutes and salt it at the end: salsa goes "
     "watery from the tomato juice, and a spoonful of tomato puree thickens what is left."),
    (("baba ganoush", "tapenade"),
     "It wants balancing rather than more of anything: a squeeze of lemon and a little olive oil "
     "stirred in slowly will loosen it, and salt and lemon are what it usually lacks."),
)
