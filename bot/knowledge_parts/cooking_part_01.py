"""Part 1 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

from ..knowledge.lookup import find
# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.prices import a_price_is_judged
from ..knowledge.cooking_tables import SEASONINGS



# The topics this domain answers (bot/understanding/topics.py); answers.py declares the union.
ANSWERS = ("cooking", "food-and-drink")


# Keeping entries only answer when the line is actually asking. "we keep pasta in the cupboard"
# and "i keep burning the bread" are things people tell you, not questions about storage; the
# shapes below are how the keeping question gets asked. Fridge, freezer and freeze are left out on
# purpose: "we keep our bread in the freezer" is a statement too.
# The small baked things people ask the same clock about. The name carries a table, not a list:
# the keep table further down stands aside on the words of this one, and that list is called
# BAKED_LINE_WORDS so a second BAKED_GOODS cannot quietly shadow this dict. A tray of brownies, a
# tin of biscuits, a batch of muffins: each is one row, because "how long do brownies keep" had no
# answer at all and a batch is the unit people think in. The first value is what to call one, the
# second is how long it keeps and where, the third is one sentence about the freezer.
BREAD_TIP = ("A slice of bread in the tin keeps them soft; 15 seconds in the microwave brings one "
             "back the next day.")


BAKED_GOODS = {
    "brownie": ("Brownies", "4 to 5 days in a sealed tin at room temperature",
                "They freeze for 3 months, cut into squares first.", BREAD_TIP),
    "blondie": ("Blondies", "4 to 5 days in a sealed tin", "They freeze for 3 months.", BREAD_TIP),
    "cookie": ("Cookies", "a week in an airtight tin",
               "The dough freezes for 3 months, shaped and ready to bake from frozen.", BREAD_TIP),
    "biscuit": ("Biscuits", "a week or two in a tin", "A baked tin freezes for 3 months.",
                BREAD_TIP),
    "muffin": ("Muffins", "2 to 3 days in a tin, best the day they are baked",
               "They freeze for 2 months.", BREAD_TIP),
    "flapjack": ("Flapjacks", "a week in a tin", "They freeze for 3 months.", BREAD_TIP),
    # A bought or homemade oat bar is the same traybake as a flapjack, and the keeping table's oats
    # row stands down for "oat bars": without a row here the keeping question fell through to the
    # porridge method and a person asking how long their oat bars keep got a recipe.
    "oat bar": ("Oat bars", "a week in a tin", "They freeze for 3 months.", BREAD_TIP),
    # the same fence stands the oats row down for "oat crackers", and a cracker keeps like the
    # biscuit it is rather than like the bag
    "oat cracker": ("Oat crackers", "a week or two in a tin",
                    "A baked tin freezes for 3 months.", BREAD_TIP),
    "cupcake": ("Cupcakes", "2 to 3 days in a tin, unfrosted",
                "They freeze for 2 months, unfrosted.", BREAD_TIP),
    "doughnut": ("Doughnuts", "only the day you buy them", "They do not freeze well.",
                 "Ten seconds in the microwave brings one back closer to fresh than you would "
                 "think."),
}


BAKED_GOODS_WORDS = ("oat bar", "oat bars", "oat cracker", "oat crackers", "brownie", "brownies", "blondie", "blondies",
                     "cookie", "cookies",
                     "biscuit", "biscuits", "muffin", "muffins", "flapjack", "flapjacks",
                     "cupcake", "cupcakes", "doughnut", "doughnuts", "donut", "donuts")


# The foods a jar holds, as against the glass: "a jar of jam" is the keeping question as well as
# the lid, so the lid answer says how long it keeps afterwards. A bare "jar" is not here, because
# an empty jar is only a jar. One list, read by the lid answer and by the follow-up below: two
# copies drifted apart once already, and the narrower one silently won.
CONTAINER_FOODS = ("jam", "pesto", "pickle", "pickles", "chutney", "marmalade", "ketchup",
                   "mustard", "mayonnaise", "mayo", "salsa", "tahini", "preserve", "preserves",
                   "olives", "gherkins", "relish")


# A jar of something keeps its own fridge life, and the lid question is what brings the jar into
# the conversation: after "how do i open a jar of jam" the line "how long does it last in the
# fridge" is about the jam. No keeping entry can be keyed on that line, because "it" names nothing
# until the turn before is read; so this entry is keyed on the shape of the question and reads the
# container from the last turn, and it stands aside (an empty reply) when no container was named,
# so the food named in the line or the general cooked-food answer has it instead.
# The jars that keep for months once opened, as against the sauces that want eating in a fortnight.
CONTAINER_MONTHS = ("jam", "pickle", "pickles", "chutney", "marmalade", "preserve", "preserves",
                    "olives", "gherkins", "relish", "mustard", "ketchup")


def _container_keep(memory, reading):
    """The keeping sentence for the container named a turn ago, or "" when none was named."""
    turns = (memory or {}).get("turns") or []
    for turn in reversed(turns[-2:]):
        said = str(turn.get("user") or "").lower() if isinstance(turn, dict) else ""
        named = [word for word in CONTAINER_FOODS if word in said]
        if named:
            food = named[0].capitalize()
            if named[0] in CONTAINER_MONTHS:
                # "olives keep", "jam keeps": the food names are plural as often as not
                keep = "keep" if food.endswith("s") else "keeps"
                return (f"{food} {keep} for months in the fridge once it is opened, and an opened "
                        "sauce or pesto 1 to 2 weeks. The label's once-opened line beats any "
                        "general rule, so bin it if it smells sharp or the lid bulges.")
            return (f"An opened {named[0]} is best within 1 to 2 weeks, kept in the fridge, and "
                    "the label's once-opened line beats any general rule. Bin it if it smells "
                    "sharp, looks odd or the lid bulges.")
    return ""


def _stuck_jar(memory, reading):
    """The lid answer, with the keeping sentence when the jar holds something worth keeping."""
    line = str((reading or {}).get("text") or (reading or {}).get("clean") or "").lower()
    said = ("Tap the edge of the lid all the way round with the handle of a knife, then grip it "
            "through a rubber glove, a silicone mat or a wide rubber band - the grip is usually "
            "what is missing. If it still will not turn, stand the jar in a bowl of hot water for "
            "two minutes so the metal lid swells, or slide the back of a spoon under the rim to "
            "let air in.")
    if any(word in line for word in CONTAINER_FOODS):
        said += " Once open, jam, pickles and chutney keep for months, an opened sauce 1 to 2 weeks."
    return said


def _baked_keep():
    """The keeping answer for the small baked things, from the row the line names."""
    def reply(memory, reading):
        line = str(reading.get("text") or reading.get("clean") or "").lower()
        for name in sorted(BAKED_GOODS, key=len, reverse=True):
            if name in line:
                label, keeps, frozen, tip = BAKED_GOODS[name]
                return f"{label} keep {keeps}. {frozen} {tip}"
        return ""
    return reply


KEEP_ASK = ("how", "what", "which", "can", "could", "should", "would", "where", "is", "are",
            "does", "do i", "will",
            "worth", "ok", "okay", "safe", "still", "long", "last", "lasts", "store", "storing",
            "stored", "leftover", "leftovers", "left over", "next day", "tomorrow", "reheat",
            "gone off", "go off", "goes off", "going off", "shelf life", "shelf-life")


# A lid that will not turn is a job on the lid, not a keeping question. The keeping key of a jar
# reads "jar" and "open", and "how" is in KEEP_ASK, so the fridge paragraph answered "how do i
# open a tight jar" and "cant get the lid off the jam". Every entry that names a container carries
# these words, so an opening line passes to the entry that turns the lid.
OPEN_ASK = ("open a tight", "open a stuck", "open a stubborn", "get the lid off",
            "get this lid off", "get the cap off", "lid is stuck", "lid stuck",
            "lid wont come off", "lid won't come off", "wont open", "won't open",
            "wont turn", "won't turn", "wont budge", "won't budge", "cant open", "can't open",
            "cannot open", "hard to open", "struggling to open", "stubborn lid", "tight lid",
            "stuck lid", "how do i open", "how to open", "how can i open")


# A fault only means something about cooking when the line is also about food: "too dry" on its own
# can be the weather, the washing or a cough. Every "it went wrong" entry below needs one of these
# words as well as its fault word.
_FOOD = ("sauce", "soup", "stew", "curry", "chilli", "casserole", "gravy", "dish", "dinner",
         "supper", "meal", "food", "cooked", "cook", "cooking", "taste", "tastes", "tasted",
         "made", "make", "fix", "fixing", "came out", "turned out", "went wrong",
         "chicken", "meat", "rice", "pasta", "cake", "bread", "pastry", "potatoes", "stir fry",
         "custard", "mash", "roast", "bake", "baking", "bolognese", "lasagne", "lasagna",
         "risotto", "pie", "cobbler", "traybake", "noodles", "eggs", "fish", "mince", "beef",
         "pork", "lamb", "vegetables", "veg", "pancakes", "porridge", "stock", "broth",
         "salt", "seasoning", "spices", "herbs", "pepper", "marinade", "dressing", "steak",
         "squid", "prawns", "bacon", "sausages", "turkey", "burgers",
         # The dish names the fault answers did not know, so "my ragu is too thin" and "my
         # meatballs are dry" were shrugs. One list, because every fault answer reads it: watery,
         # dry, bland, burnt, salty and hot all reach a dish named here.
         "ragu", "rag\u00f9", "bolognaise", "meatballs", "meatloaf", "tagine", "daal", "dhal",
         "biryani", "paella", "ratatouille", "goulash", "gnocchi", "hummus", "burrito", "katsu",
         "macaroni cheese", "mac and cheese", "waffles", "frittata", "ramen", "quesadilla",
         "cottage pie", "shepherds pie", "shepherd's pie", "fish pie", "quiche", "couscous",
         "pesto", "guacamole", "tapenade", "dip", "dips", "pilaf", "pilau",
         "burger", "hamburger", "falafel", "patty", "patties",
         # The trimmings and the batter: every fault answer reads this list, and without these
         # words "the parsnips burnt", "my stuffing burnt" and "my yorkshire puddings burnt" had
         # no food in them at all, so the burnt row could not match and one of them got a random
         # pancake idea from the pantry instead.
         "parsnip", "parsnips", "carrot", "carrots", "sprouts", "brussels sprouts", "cabbage",
         "kale", "leek", "leeks", "beetroot", "swede", "turnip", "cauliflower", "broccoli",
         "roast potatoes", "roast veg", "stuffing", "dumplings", "yorkshire pudding",
         "yorkshire puddings", "yorkshires", "toad in the hole", "batter", "crepe", "crepes")


# How a fault is said is not a food. "It came out flat" names no subject of its own - the thing
# it is about was named in the line before it - so a taste row that counted "came out" as its
# food word answered the saying alone, and a cake that sank was told to season itself. The rows
# that read a fault ("watery", "dry", "burnt") keep the phrases: "the moussaka came out watery"
# is that row's own question. A taste is something a dish *tastes*, not something it came out.
_A_FAULT_SAID = ("came out", "turned out", "went wrong")


_A_TASTE = tuple(word for word in _FOOD if word not in _A_FAULT_SAID)


# The everyday staples: the plain "how do I cook it" that comes up whatever else people are
# cooking. One row per staple, keyed on the staple's own names, and the entry below wants a
# cooking word as well, so a line that puts the staple on the side ("what goes with rice"),
# asks about what is left of it, or says it went wrong, goes to those entries instead.
def _corn(understood):
    """Sweetcorn, leading with the way the line asks for it.

    The row answered the boil and the grill and nothing else, so "how do i microwave corn on the
    cob" and "can you microwave sweetcorn" were a search punt while the row sat there with the
    wrong method in it. The equipment named in the line is the tell, and the microwave is the way
    most people cook a cob at home.
    """
    said = " " + " ".join(str(word).lower() for word in (understood.get("words") or [])) + " "
    if any(cue in said for cue in (" microwave ", " microwaved ", " microwaving ",
                                   " microwaves ", " micro ")):
        return ("In the microwave a cob takes 3 to 4 minutes on full power for one and 5 to 6 for "
                "two: leave it in its husk, or wrap it in a damp piece of kitchen paper, and turn "
                "it once. It carries on cooking as it stands, so give it a minute before you "
                "butter it. Loose kernels in a covered bowl with a splash of water take 2 to 3 "
                "minutes, stirred halfway.")
    if any(cue in said for cue in (" air fryer ", " airfryer ", " air fried ", " airfry ")):
        return ("In the air fryer rub the cobs with a little oil and give them 10 to 12 minutes at "
                "190C, turning once: the kernels blister at the tips and that is the point. Two "
                "cobs fit in a normal basket; more than that and they steam instead of browning.")
    if any(cue in said for cue in (" grill ", " grilled ", " grilling ", " barbecue ", " bbq ",
                                   " char ", " charred ")):
        return ("Under a hot grill or on the barbecue, 10 to 12 minutes, turning every few "
                "minutes until the kernels start to char in patches - rub them with a little "
                "butter or oil first so they colour rather than dry. Boiled instead, 6 to 8 "
                "minutes in unsalted water; salt toughens it.")
    return ("Boil it in unsalted water for 6 to 8 minutes - salt toughens it - or grill it, "
            "turning it now and then, for 10 to 12 minutes until the kernels start to char. In "
            "the microwave a cob takes 3 to 4 minutes on full power. Butter, salt and pepper, and "
            "it needs nothing else.")


BASICS = (
    (("brown rice",),
     # the rest is in a sentence of its own: a follow-up "how long does brown rice take" is
     # narrowed to a time in the first sentence, and "then 10 minutes off the heat" would be it
     "Brown rice wants more water and longer than white: one mug of rice to two mugs of water, "
     "lid on, 25 to 30 minutes on the lowest heat. Then 10 minutes off the heat before you fork "
     "it through. Rinse it first and don't stir it."),
    # The grains that answer "how do i cook it" but not "how long does it take": couscous, quinoa,
    # barley and bulgur were a shrug on the time question. The time leads, because a time is what
    # was asked for.
    (("quinoa",),
     "Quinoa takes 12 to 15 minutes: one part quinoa to two of water, lid on, simmering, then 5 "
     "minutes off the heat and fork it through. Rinse it first, or it tastes soapy."),
    (("couscous",),
     "Couscous needs no cooking: same volume of boiling water or stock as couscous, cover the bowl "
     "and leave it 5 minutes, then fork it through with a knob of butter and a squeeze of lemon so "
     "it stays loose."),
    (("barley", "pearl barley"),
     "Pearl barley takes 25 to 30 minutes simmered in three times its volume of water or stock, "
     "and whole barley 45 to 60. It is done when a grain squashes between your fingers with no "
     "chalky middle, so taste it rather than time it."),
    (("bulgur", "bulgur wheat"),
     "Bulgur wheat takes 10 to 12 minutes simmered in twice its volume of water, or pour boiling "
     "stock over it, cover and leave it 20 minutes off the heat. Fork it through with a little "
     "olive oil."),
    (("wild rice",),
     "Wild rice is a grass seed rather than a rice, so it takes 40 to 45 minutes in plenty of "
     "boiling water - about three parts water to one of rice - until the grains split and taste "
     "nutty. Drain it and rinse off the starch."),
    (("rice cooker",),
     "Rinse the rice first, then the same one mug of rice to one and a half mugs of water, level "
     "off with the back of a finger and don't go past the line inside the bowl. Let it finish on "
     "its own, leave it on warm for 10 minutes, then fork it through."),
    (("rice", "basmati", "long grain rice", "white rice", "jasmine rice", "rice cooker"),
     "One mug of rice to one and a half mugs of water, lid on, 10 to 12 minutes on the "
     "lowest heat, then 10 minutes off the heat with the lid still on before you fork it "
     "through. Rinse it until the water runs clear first. Don't stir it and don't drain it - "
     "that is what makes it gluey."),
    (("porridge", "oats", "oatmeal", "porridge oats"),
     "50g of oats to 300ml of milk or water per person, with a pinch of salt, stirred over a "
     "medium heat for 4 to 5 minutes. Take it off while it still looks a little loose, because it "
     "thickens as it stands, and stir in a splash more milk if it sets."),
    (("white sauce", "cheese sauce", "bechamel", "béchamel"),
     "About 10 minutes start to finish. Melt 50g of butter, stir in 50g of plain flour and cook "
     "that for a minute, then add 500ml of milk a good splash at a time, whisking each one in "
     "before the next goes in. Simmer it for 5 minutes until it coats the back of a spoon, then "
     "season it. For a cheese sauce, stir in 100g of grated cheddar once it is off the heat."),
    (("mash", "mashed potato"),
     "Use a floury potato like Maris Piper or King Edward, cut into even chunks and boiled in "
     "salted water for 15 to 20 minutes. Drain them, leave them in the colander for a minute to "
     "steam dry, then mash with butter and warm milk - cold milk makes it gluey - and don't use a "
     "food processor."),
    (("vegetables", "veg"),
     "The one rule for vegetables is short and hot: steam or boil them 5 to 7 minutes so "
     "they still have a bite, or roast them at 200C (180C fan) for 25 to 35 minutes in oil "
     "with salt. Cut them to a similar size and they finish together, and salt the water "
     "rather than the pan."),
    # "how do i chop an onion" is a knife question, and the onion row under it answers the pan:
    # "chop it, then soften it in oil" is the one thing the person already knows how to do. The
    # sentence is the method, and it sits above the onion row so the plain cooking question keeps
    # its answer.
    (("chop an onion", "chop onions", "chopping an onion", "chopping onions", "dice an onion",
      "dice onions", "dicing an onion", "dice onions", "slice an onion", "cut an onion",
      "cut up an onion", "prepare an onion"),
     "Halve it top to bottom through the root, lay a half cut side down and slice across it "
     "towards the root, then cut the slices the other way, and it is diced. Leave the root end on "
     "until the last cut, because it holds the layers together. Use the sharpest knife you have "
     "and keep the tip on the board: a blunt knife crushes the cells and releases more of the "
     "sulphur that makes your eyes water."),
    # The everyday jobs in a kitchen are prep jobs, and the same ask comes for every ingredient:
    # "how do i peel a potato", "how do i chop garlic", "how do i cut an avocado". A line like
    # that names the ingredient and the knife, and the cooking rows answered the pan ("chop it,
    # then soften it in oil") or nothing at all. One row per ingredient, keyed on the phrase, so
    # the plain "how long do i boil potatoes" keeps the method it already has.
    (("peel a potato", "peel potatoes", "peeling potatoes", "peel a potato quickly",
      "how do i peel potatoes", "prepare potatoes", "prepare a potato"),
     "Take the skin off in strips with a peeler, working away from you and turning the potato as "
     "you go, then dig any eyes out with the tip of the peeler. Drop them into a bowl of cold "
     "water if they are not going in the pan straight away, because peeled potato goes pink in "
     "the air. Peel floury ones like Maris Piper just before they cook, not the night before."),
    (("chop garlic", "crush garlic", "mince garlic", "chop a garlic clove",
      "prepare garlic", "chop garlic cloves", "peel a garlic clove", "peel garlic cloves"),
     "Lay the clove on the board, put the flat of the knife on top and press down with the heel "
     "of your hand: the skin slips off and the clove is already crushed. Chop it roughly, "
     "sprinkle a pinch of salt on it and drag the flat of the knife over it in circles to turn it "
     "into a paste. Crushed like that it sweetens in the pan; left in chunks it burns."),
    (("peel ginger", "chop ginger", "grate ginger", "prepare ginger", "mince ginger"),
     "Scrape the skin off with the edge of a teaspoon, which follows the knobs better than a "
     "peeler and wastes less of the root. Grate it on the fine side of a grater, or freeze the "
     "knob whole and grate it from frozen, which is quicker and keeps for months. The skin is "
     "thin and edible, so it can stay on if it is going into a curry."),
    (("chop a carrot", "chop carrots", "dice a carrot", "dice carrots", "slice a carrot",
      "slice carrots", "prepare carrots", "prepare a carrot"),
     "Top and tail it, cut it in half lengthways and lay the flat side down so it cannot roll. "
     "For sticks, cut each half into lengths and slice those; for dice, cut the lengths into "
     "batons first, then turn them and slice across. Keep every piece the same size, because "
     "that is what makes them cook at the same rate."),
    (("chop mushrooms", "slice mushrooms", "prepare mushrooms", "cleaning mushrooms",
      "cleaning a mushroom"),
     "Wipe the caps with damp kitchen paper, or rinse them quickly under the tap and dry them on "
     "a tea towel - either works, because a few seconds of water adds nothing a mushroom did not "
     "already have, and only a bowl of soaking water makes them watery. Snap the stalk out level "
     "with the cap and slice straight down through cap and stalk together. Do not crowd the pan - "
     "a crowded pan of mushrooms boils in its own water and never browns."),
    (("cut an avocado", "prepare an avocado", "peel an avocado", "stone an avocado",
      "remove the stone from an avocado", "slice an avocado", "how do i cut an avocado"),
     "Run the knife round the stone from top to bottom, twist the two halves apart, then lever "
     "the stone out with a spoon rather than the knife. Peel the skin back or scoop the flesh out "
     "with a spoon, and slice it while it is still in its shell. Squeeze lemon or lime over it if "
     "it is going to sit, because cut avocado goes brown in the air."),
    (("peel a mango", "cut a mango", "prepare a mango", "slice a mango",
      "how do i cut a mango"),
     "Slice the two cheeks off either side of the flat stone, score the flesh in a grid without "
     "cutting the skin, then push the skin inside out and cut the cubes off it. A peeler and a "
     "knife down the sides of the stone works too and wastes a little more. A ripe mango gives "
     "slightly under your thumb; a hard one is stringy and sour."),
    (("cut up a pineapple", "cut a pineapple", "prepare a pineapple", "peel a pineapple",
      "how do i cut a pineapple", "how do i cut up a pineapple", "slice a pineapple"),
     "Slice the top and the base off flat so it stands up, then cut the skin away in strips from "
     "top to bottom, taking the eyes with it. Cut it into quarters, stand each one up and slice "
     "the core out, then cut the rest into the pieces you want. The core is tough raw but fine "
     "in a smoothie."),
    (("juice a lemon", "juice a lime", "squeeze a lemon", "squeeze a lime", "juice an orange",
      "juice lemons", "squeeze lemons"),
     "Roll it on the worktop with the heel of your hand first to break the cells inside, then cut "
     "it across the middle rather than top to tail. Push a fork into the cut face and squeeze, "
     "turning as you go, and strain out the pips. A lemon at room temperature gives more juice "
     "than one out of the fridge."),
    (("onions", "onion"),
     "Chop it, then soften it in oil on a low heat for 8 to 10 minutes with a pinch of salt: "
     "that is what makes it sweet and golden. A hot pan browns the outside and leaves the "
     "middle raw and sharp, so turn the heat down and give it the time."),
    # `_corn`, because the way a cob is cooked depends on the machine the line names
    (("corn on the cob", "sweetcorn", "corn"), _corn),
    (("butternut squash", "butternut", "squash"),
     "Halve it, scoop out the seeds, rub the cut sides with oil and roast face down at 200C "
     "(180C fan) for 40 to 45 minutes. Cubed it takes 25 to 30 minutes, and it is done when "
     "a knife goes in with no resistance."),
    (("pork chops", "pork chop"),
     "Pat them dry, season, and sear in a hot pan 3 to 4 minutes a side, then rest 5 minutes "
     "- pork is safe slightly pink now, at 70C in the middle. A thick chop also finishes in "
     "the oven at 200C (180C fan) for 10 to 12 minutes."),
    (("fish", "white fish", "cod", "haddock", "salmon fillet", "fillet of fish"),
     # "how long do i bake salmon fillets" wants the clock and "is my cod cooked through" wants
     # the test, and one sentence can carry both: the time is the clause the how-long ask reads
     # first, and the flake test follows it in the same sentence rather than a sentence later.
     "Bake fillets at 200C (180C fan) for 12 to 15 minutes - done when the thickest part flakes "
     "into opaque white, so keep it a minute short rather than a minute long - or fry them skin "
     "side down in a hot pan for 4 minutes, then 2 on the other side."),
    (("potato wedges", "wedges"),
     "Cut them into wedges about 2cm at the thick edge, toss in oil, salt and paprika and roast "
     "at 200C (180C fan) for 25 to 30 minutes, turning once at halfway: they are done when the "
     "edges are deep gold and a knife slides into the thick part. Parboiling 8 minutes first "
     "makes them crisper outside and fluffier in."),
    (("chard", "swiss chard"),
     "Cook the stems first: slice them and fry 4 to 5 minutes, then add the leaves for 2 to 3 "
     "minutes more, because the stems take far longer. A knob of butter, a pinch of salt and a "
     "squeeze of lemon, and the leaves wilt down to almost nothing."),
    (("peppers", "bell peppers", "bell pepper"),
     "Fry sliced peppers in a hot pan with oil for 6 to 8 minutes until the edges soften and "
     "catch a little colour, or roast halves at 200C (180C fan) for 25 minutes. They go sweet "
     "with long cooking and stay crunchy with short cooking, so it depends what you want."),
    (("celery", "celery sticks"),
     "Slice it and soften it in butter for 6 to 8 minutes: that is the base of a soup or a "
     "stew, and it goes sweet rather than stringy. On its own, braise the sticks with stock "
     "and a lid for 20 minutes, or shave them raw into a salad with lemon and salt."),
    (("fennel", "fennel bulb"),
     "Slice it thin and roast at 200C (180C fan) for 25 minutes with oil, salt and a little "
     "lemon - the aniseed goes sweet. Raw and shaved with olive oil, lemon and parmesan it is "
     "a salad in 5 minutes. Cut out the tough core first."),
    (("celeriac",),
     "Peel it thickly, cube it and boil for 15 to 20 minutes, then mash it half and half with "
     "potato - it is wet on its own and needs the potato to hold it. It browns fast once it is "
     "cut, so drop the pieces in water with a squeeze of lemon until they go in the pan; raw and "
     "shredded with mayonnaise, mustard and lemon it is remoulade."),
    (("turnip", "turnips"),
     "Small young turnips only want 10 to 12 minutes boiled, or 25 minutes roasted in wedges "
     "at 200C (180C fan) with oil and honey. Big older ones are woody and bitter, so peel "
     "them well and mash them with potato and butter instead."),
    (("broad beans", "fava beans"),
     "Boil them for 4 to 5 minutes, then pop them out of their skins - the skins are tough and "
     "bitter, and the beans inside are sweet. Small ones can stay in their skins. Dress them "
     "with oil, lemon, mint and a little salt."),
    (("shallots", "shallot"),
     "Slice them and soften in butter for 6 to 8 minutes on a low heat - they are sweeter and "
     "milder than onions, so they need less time and brown faster. Whole, roast them at 200C "
     "(180C fan) for 25 to 30 minutes with oil and a pinch of salt."),
    (("pak choi", "bok choy", "pak choy"),
     "Halve it lengthways and fry cut side down in a hot pan for 2 to 3 minutes, then add a "
     "splash of soy sauce, a little garlic and a lid for 1 minute more. It is done when the "
     "base is tender and the leaves have just wilted, so it takes about 5 minutes in all."),
    (("mange tout", "mangetout", "sugar snap peas", "snow peas"),
     "Stir-fry them in a very hot pan for 2 to 3 minutes, or steam them for 3: they are done "
     "as soon as they are hot through and still squeak when you bite one. Don't boil them, or "
     "the sweetness goes into the water."),
    (("buttermilk", "leftover buttermilk"),
     "Buttermilk is not cooked on its own: it is what makes soda bread rise with bread soda, it "
     "thins a pancake batter, and it tenderises chicken in a marinade for an hour before frying. "
     "It is naturally sour and thick, so in a recipe you can stand in for it with milk and a "
     "squeeze of lemon left for 10 minutes."),
    (("marrow", "vegetable marrow", "marrows"),
     "Roast it in thick rings: peel it, scoop out the seeds, cut 2cm rings, oil and salt them and "
     "give them 30 to 35 minutes at 200C (180C fan) until the edges colour. Or halve it, salt it "
     "and let it drain 20 minutes, then stuff it with mince and rice and bake 45 minutes at 190C "
     "(170C fan) - it is mostly water, so the salt-and-drain is what stops it going to mush."),
    (("chicory", "endive"),
     "Halve it and braise cut side down in butter for 3 to 4 minutes, then add a splash of "
     "stock and a lid for 10 minutes, which takes the bitterness down. Raw, the leaves are a "
     "scoop for a dip, and a little sugar or orange in the pan helps too."),

)


# A staple inside a dish is that dish's question. Rice pudding, potato salad, a potato gratin,
# scalloped potatoes, sweet potato, pasta bake and spaghetti bolognese all have their own times
# and their own methods, so the plain staple does not answer for them.
# "rice without a rice cooker" is a question about the pan, not about the machine.
# A staple named in a line that is not asking how to cook it is that line's business: what to
# make with it ("what can i make with half a cabbage" wants a dish, not a method), what to do
# with the rest of it, and who in the house will not eat it. A method given for one of those is
# a confident wrong answer to a question nobody asked.
NOT_A_METHOD = ("make with", "made with", "make using", "use up", "using up", "use it up",
                "what can i", "what should i", "what could i", "hate", "hates", "hated",
                "dislike", "dislikes", "allergic", "allergy", "cant stand", "cannot stand",
                "doesnt like", "does not like", "dont like", "do not like", "wont eat",
                "wont touch", "fussy", "left with", "half a",
                # "i cooked rice yesterday, can i eat it" is a keeping question about a bowl in
                # the fridge, and a staple method is a confident wrong answer to it: the day the
                # person names is what tells the two apart, so the method rows stand down there
                # and keeping.py's own row for the food answers it.
                "yesterday", "yesterdays", "last night", "the day before", "day before",
                "the day after", "day after", "day later", "a day later", "days ago",
                "a couple of days ago", "2 days ago", "two days ago",
                # a game shares its name with a food, and a shot at it is not a pan question:
                # "how do i improve my backhand at squash" was told to halve a butternut squash
                "backhand", "forehand", "racket", "racquet", "tennis court", "squash court",
                "badminton", "volleyball", "netball", "the ball", "cricket")


# The words that make a line a question about whether a crop is ready to pick, rather than about
# cooking it. "how do i know when my onions are ready" is onions in the ground; the harvest row in
# garden.py answers it, so the staple method turns itself down (see `_staple`).
KNOWS_READY = ("know when", "how do i know", "how will i know", "how can i tell",
               "when are they ready", "when are mine ready", "are they ready", "are mine ready",
               "are they done yet", "when do i know")


# The words that make a line a question about cooking the staple rather than a mention of it.
STAPLE_ASK = ("cook", "cooking", "make", "making", "how", "long", "boil", "boiling",
              "time", "much", "ratio", "method", "properly", "instructions", "best way",
              "minutes", "do i", "should i", "recipe")


# The two directions of one question, which need different first sentences: "my soup is too
# thick" wants it thinned, and "how do i thicken my soup" wants it thickened. One reply cannot
# open with both, so the words of the line pick the half (see `_body`).
_BODY_TOO_THICK = (
    "Too thick: add hot stock, milk or just water a splash at a time, stirring, until it pours the "
    "way you want it, then taste it again because thinning takes the salt with it. A spoon of "
    "butter or cream stirred in at the end does the same with more flavour, and a stew that has "
    "cooked down only needs the lid on for ten minutes."
)


_BODY_TOO_THIN = (
    "Simmer it uncovered for 10 minutes to reduce it, or blend a ladleful and stir it back in for "
    "body without flour. A handful of red lentils thickens a soup or stew in 15 minutes; for a "
    "stew, take the lid off for the last half hour."
)


# A complaint about the pot, in the shapes people write it. "How do i make thick soup" has the
# word "thick" and wants the other direction, so a bare "thick" is not enough on its own.
_TOO_THICK_SAID = ("too thick", "so thick", "very thick", "really thick", "is thick", "its thick",
                   "it's thick", "thick and", "stodgy", "claggy", "gluey", "thinner",
                   "less thick", "thin down", "thin it", "make it thinner", "soup thinner",
                   "make my soup thinner")


# A shoulder, a hip and a back are all cuts of meat and all parts of a person, so the meat
# words alone cannot tell "how long should i rest my shoulder" from "how long to rest a
# shoulder of lamb". A body word on its own, with no cut named, is the training question.
_REST_BODY = ("my shoulder", "my knee", "my back", "my hip", "my leg", "my arm", "my neck",
              "injured", "injury", "injuries", "pain", "painful", "hurts", "hurting",
              "sore", "stiff", "stiffness", "sprain", "sprained", "pulled a muscle",
              "after a fall", "physio", "physiotherapist", "gym", "workout", "worked out",
              "exercise", "exercising", "training", "trained", "running", "run", "sports day",
              # a joint is a body part and also a cut of meat, and `joint` sits in the cut list
              # below, so "should i rest my joints" was answered with the four-meat paragraph
              "my joint", "my joints", "joint pain", "aching", "ache", "aches")


_REST_CUT = ("lamb", "pork", "beef", "veal", "venison", "joint", "roast", "brisket",
             "turkey", "chicken", "duck", "goose", "steak", "ribs", "rib", "ham", "gammon",
             "shoulder of", "leg of", "of lamb", "of pork", "of beef", "meat", "wellington")


# The cut phrases that really do name a joint of meat: "my leg of lamb" is both, and the dish
# row for a leg of lamb has the better answer, so these keep the cut in charge.
_REST_CUT_PHRASE = ("of lamb", "of pork", "of beef", "of veal", "shoulder of", "leg of")


def _resting_a_body_part(said):
    """True when the line is about resting a body, not about standing meat."""
    body = any(" " + word + " " in said for word in _REST_BODY)
    cut = any(" " + word + " " in said for word in _REST_CUT)
    # A body word wins outright unless the line names a cut of meat, because "joint" is on both
    # lists: "should i rest my joints" and "how long should i rest a sprained joint" were meat.
    if body and not any(phrase in said for phrase in _REST_CUT_PHRASE):
        return True
    return body and not cut


def _rest_the_meat(memory, understood):
    """How long to rest the meat, unless the dish table already has the rest for this dish.

    `do i need to rest a steak` and `why should i rest a chicken` were answered by the dish rows
    in dishes.py, each with the minutes for that one dish and the reason in the same sentence. A
    four-meat paragraph is a worse answer to a line that names one of them, so this entry turns
    the line down and the dish row answers, the way the roast rows stand down for a rest question.
    """
    from ..knowledge.dishes import ask_kind, reply as dish_reply
    from ..knowledge.lookup import find
    said = " " + " ".join(str(word) for word in ((understood or {}).get("words") or [])) + " "
    if " the rest " in said or " rest of " in said:
        # "what do i do with the rest of the joint" is the leftovers question. The "rest" there
        # is the remainder, not the standing time, and meals.py's use-up row answers it.
        return None
    if _resting_a_body_part(said):
        # "how long should i rest my shoulder" is a training question: a shoulder is a cut of
        # pork and lamb as well as a joint on a person, and the meat words alone cannot tell them
        # apart. A body word with no cut named is never this answer.
        return None
    if ask_kind(understood) == "rest" and dish_reply("rest", memory, understood):
        # The dish table has the minutes for the one dish the line named. Stand down only when
        # its own row is what answers next: "why rest a steak" and "how should i rest a steak"
        # reach nothing but a shrug or the red-meat limit of the day, and the four-meat
        # paragraph is the better answer to both.
        next_row = find(understood, reject=lambda item: item.id == "rest-meat")
        if getattr(next_row, "id", None) == "plan-followup":
            return None
    minutes = ("loosely under foil and off the heat, not back in the oven: 15 to 20 minutes for "
               "a chicken or a turkey, 10 to 20 for a joint of beef, lamb or pork, 5 to 10 for a "
               "steak or chops, and 20 to 30 for a brisket")
    reason = ("standing lets the heat that has built up round the outside move back into the "
              "middle, so the juice stays in the meat when you carve it instead of running out "
              "onto the board")
    if "why" in ((understood or {}).get("asks") or ()):
        # a why line wants the reason first, with the minutes behind it
        return ("Rest it because " + reason + " - " + minutes + ". It stays hot that long under "
                "the foil, so nothing is lost by waiting.")
    return (minutes[0].upper() + minutes[1:] + ". " + reason[0].upper() + reason[1:]
            + ". It stays hot that long under the foil, so nothing is lost by waiting.")


# A child who will not eat veg, named in this line or in the one just before it: "my son wont eat
# vegetables, hes 4" and then "should i just blend veg into a sauce" are the same question asked
# twice, and a follow-up names the method, not the child, so the key cannot carry the child word.
CHILD_WORDS = (" kid", " kids", " child", " children", " son", " daughter", " toddler", " baby",
               " fussy", " picky", " wont eat", " won't eat", " refuses", " weaning",
               " nursery", " school dinner", " school dinners", " he wont", " she wont")


def _about_a_child(memory, understood):
    """True when the veg question is a parent's, here or in the last few turns."""
    line = " " + ((understood or {}).get("clean") or "") + " "
    if any(word in line for word in CHILD_WORDS):
        return True
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for turn in reversed(turns[-3:]):
        said = " " + (turn.get("user") or "") + " " if isinstance(turn, dict) else ""
        if any(word in said for word in CHILD_WORDS):
            return True
    return False


KIDS_VEG = ("Keep serving one small piece of veg next to something they already like, without a "
            "fight or a reward: it can take ten tries before a toddler accepts a new one. Roasting "
            "carrots or broccoli in a little oil makes them sweeter, and a dip to dunk turns it "
            "into a game. Grated or blended into what they already eat - carrot in the bolognese, "
            "courgette in a muffin, spinach in a soup - gets the veg in without a standoff.")


ADULT_VEG = ("Put them where you already eat rather than on a separate pile: grated carrot or "
             "courgette in the mince, a handful of spinach stirred into pasta at the end, frozen "
             "peas straight into rice, beans or lentils bulking out a chilli. Frozen and tinned "
             "count, and so does a bag of mixed veg thrown into a tray bake. Aim for one extra "
             "portion at a meal you already have rather than a new meal you have to keep up.")


def _the_veg_card_was_just_said(memory):
    """True when the bot's last turn already opened with this card."""
    opening = KIDS_VEG[:40].lower()
    for last in (memory.get("turns") or [])[-2:]:
        if isinstance(last, dict) and opening in (last.get("bot") or "").lower():
            return True
    return False


def _kids_veg(memory, understood):
    """The feeding answer, or nothing when the conversation has no child in it.

    Once the card has been given, saying it again is the repeat STYLE.md forbids: a bare "any
    tips" or "how do i get him to try it" one turn after it is the same question, and the answer
    is the paragraph the person has just read. The row stands down and lets whatever else can
    answer the turn take it - the composer reads the card the person already has.
    """
    if not _about_a_child(memory, understood):
        return None
    return None if _the_veg_card_was_just_said(memory) else KIDS_VEG


def _harvest_crops():
    """The crops with a harvest row, imported where they are used so the two tables stay apart."""
    from ..knowledge.garden import harvest_crops
    return harvest_crops()


def _done_words():
    """The words that make a crop question a pan question, shared with the harvest rows."""
    from ..knowledge.garden import DONE_NOT
    return DONE_NOT


# An appliance named beside a cut is answered by the two tables together: the dinner ideas stand
# down for it (they hand the cut to the table), so a cut row stood down for the appliance would
# leave the line with no answer at all. "how do i cook a leg of lamb in a slow cooker" was the
# lamb's oven time before these guards fired, and a shrug after.
_AN_APPLIANCE = ("slow cooker", "slow cookers", "crockpot", "crock pot", "air fryer",
                 "pressure cooker", "instant pot", "oven")


def _an_appliance_has_the_line(text):
    """True when an appliance and a cut are both named, so the cut row has to answer."""
    try:
        from ..knowledge import dishes
    except Exception:  # noqa: BLE001 - the guard is a courtesy, not the row
        return False
    return dishes._names_an_appliance_and_a_cut(text)


def _pancakes(memory, understood):
    """Pancakes, leading with the kind the line asks for.

    "how do i make american pancakes" used to get twelve thin pancakes and the American variant
    as an afterthought, which is the wrong first sentence for that line.
    """
    words = set(understood.get("words") or [])
    if "mix" in words and not words & {"make", "made", "making", "recipe", "batter", "whisk",
                                        "homemade", "from"}:
        # airy-deer's catch: "best pancake mix" and "where to buy pancake mix" are the box in the
        # shop, and "how do i make pancake mix" is the one that wants this batter. Passing lets
        # the shopping side have the packet lines.
        return None
    if words & {"american", "fluffy", "thick", "buttermilk", "scotch"}:
        return ("For a dozen thick American pancakes, whisk 150g plain flour, 2 teaspoons of baking "
                "powder, a tablespoon of sugar, 2 eggs and 250ml milk into a thick batter that "
                "holds its shape, and let it rest 10 minutes. Cook them in a buttered pan on a "
                "medium heat, 2 minutes a side, and turn them once, when bubbles pop and stay open. "
                "The baking powder is what lifts them; for thin pancakes leave it out and use "
                "300ml milk.")
    return ("For about 12 thin pancakes, whisk 100g plain flour, 2 eggs and 300ml milk with a pinch of "
            "salt, then let the batter rest 20 minutes. Cook them in a hot non-stick pan with a little "
            "butter, about a minute a side, until bubbles pop on top and the edges look dry. The rest "
            "is what stops them tearing; American ones want a teaspoon of baking powder and a "
            "thicker batter. Flat ones are a batter that was too thin, or an old raising agent.")


def _pancake_batch(memory, understood):
    """Pancake amounts for the number of people the line names.

    The four-person batter is 200g flour, 3 eggs and 600ml milk, so the rule is 50g of flour, three
    quarters of an egg and 150ml of milk each. "How many pancakes for 10 people" was answered with
    the four-person numbers, which is the wrong amount for the question the person asked.
    """
    people = None
    for number in understood.get("numbers") or []:
        value, unit = number.get("value"), number.get("unit")
        if not isinstance(value, (int, float)) or not 2 <= value <= 40:
            continue
        if unit in (None, "", "people", "person", "persons", "adults", "adult", "kids", "guests",
                    "portions", "servings"):
            people = int(round(value))
            break
    if people is None:
        return ("For four people allow 200g plain flour, 3 eggs and 600ml milk, which makes about "
                "16 thin pancakes; a family with small children is happy on 150g. Cook them a "
                "minute a side in a hot pan until the bubbles pop and the edges look dry.")
    grams = 50 * people
    flour = "%dkg" % (grams // 1000) if grams % 1000 == 0 else (
        "%d and a half kg" % (grams // 1000) if grams > 1000 and grams % 500 == 0
        else "%dg" % grams)
    eggs = 0.75 * people
    whole = int(eggs)
    egg_words = ("%d or %d eggs" % (whole, whole + 1) if 0.4 <= eggs - whole <= 0.6
                 else "%d eggs" % int(round(eggs)))
    millilitres = 150 * people
    if millilitres < 1000:
        milk = "%dml of milk" % millilitres
    elif millilitres % 1000 == 0:
        milk = "%d litres of milk" % (millilitres // 1000)
    else:
        milk = ("%.1f litres of milk" % (millilitres / 1000.0)).replace(".0 litres", " litres")
    return ("For %d people allow %s plain flour, %s and %s, which makes about %d thin pancakes. "
            "Cook them a minute a side in a hot non-stick pan with a little butter, until the "
            "bubbles pop and the edges look dry; for thick American ones add a teaspoon of baking "
            "powder per 200g of flour." % (people, flour, egg_words, milk, 4 * people))


def _sweet_potato(memory, understood):
    """Sweet potato, leading with the method the line asks for.

    The wedges method is the answer to "how do i cook sweet potato", but "how long do i boil sweet
    potato" and "sweet potato mash" want the boiling time first: pointing a boil question at a
    25-minute oven method is a wrong answer, not just a different one.
    """
    words = set(understood.get("words") or [])
    if words & {"boil", "boiled", "boiling", "steam", "steamed", "steaming", "mash", "mashed",
                "puree", "pureed"}:
        return ("Boil peeled chunks for 12 to 15 minutes, until a knife slides in with no "
                "resistance: sweet potato softens faster than white potato, so test it at 10. "
                "Drain and steam it dry for a minute, then mash it with butter and a pinch of salt "
                "and go easy on the milk, because it is wetter than white potato.")
    if words & {"microwave", "microwaved", "microwaving", "quick", "quickly", "fast",
                "fastest", "hurry", "hurried", "hungry", "rush"}:
        # "how do i cook sweet potato in the microwave" was answered with twenty-five minutes in
        # the oven, and "how do i cook sweet potato quickly" with the same: the whole answer for
        # the fastest way was inside the last sentence of the oven method.
        return ("One medium sweet potato, pricked all over with a fork, takes 5 to 8 minutes on "
                "high: give it 5, turn it, then a minute at a time until a knife slides in with no "
                "resistance. Two take 10 to 12 minutes, and chunks for mash take 8. It steams in "
                "there rather than crisping, so give the skin 5 minutes in a hot oven or a dry pan "
                "afterwards if you want it crisp.")
    if words & {"fryer", "airfryer", "airfried"}:
        return ("In the air fryer, wedges cut into 2cm pieces take 15 to 18 minutes at 190C, shaken "
                "once halfway: toss them in a little oil, salt and paprika first and do not crowd "
                "the basket, or they steam instead of crisping. Whole ones take 35 to 40 minutes at "
                "180C, and fries cut thin take 12 to 15 minutes.")
    return ("For wedges, cut them into 2cm pieces, toss them in oil, salt and paprika and roast at "
            "200C (180C fan) for 25 to 30 minutes. Whole, they bake in about 45 minutes at 200C, or "
            "8 minutes in the microwave for one on its own. Boiled for mash, chunks take 12 to 15 "
            "minutes.")


# A pet that has eaten something is a vet question, not a kitchen one, and a dog that has taken the
# chicken out of the fridge is not asking how long to keep it. These words mark the pet, or a line
# already saying the food went down someone, so the cooking entries a pet line can reach share one
# guard instead of each carrying its own copy. The pets domain answers what a pet may eat; when
# nothing there fits, "I don't know" is better than a recipe.
# The bare "ate"/"eaten"/"eating" are not here: a person also eats pink chicken, and "is my
# chicken pink safe to eat" is a food-safety question, not a pet one. The animal words are what
# does the work, and a line with no animal in it was never certainly about a pet.
PET_LINE_WORDS = ("dog", "dogs", "puppy", "pup", "cat", "cats", "kitten", "kittens", "pet",
                  "pets", "vet", "swallowed", "swallow", "chewed", "choking", "choke",
                  "poisoned", "vomiting")


def _thighs(memory, understood):
    """Chicken thighs, with the lemon-and-potato traybake if that's what they have."""
    words = " ".join(understood.get("words") or [])
    if "lemon" in words or "potato" in words or "potatoes" in words:
        return ("Halve the potatoes, toss everything with oil, lemon slices and salt, and roast at "
                "200C (180C fan) for 35 to 40 minutes, skin side up, until the skin is crisp and the "
                "juices run clear. Squeeze the roasted lemon over before serving.")
    return ("Roast chicken thighs at 200C (180C fan) for 35 to 40 minutes, skin side up and spaced "
            "out, until the skin is crisp and the juices run clear. Salt the skin before they go in "
            "and don't crowd the tray, or they steam instead of crisping.")


def _weight_words(kilos):
    """"0.5" -> "500g", "1.5" -> "1.5kg": how a weight is said out loud."""
    if kilos < 1:
        return f"{int(round(kilos * 1000))}g"
    return f"{kilos:g}kg"


def _legs(memory, understood):
    """A chicken leg is a piece, not a bird: a drumstick and a whole leg take different times, and
    the whole-bird rule (20 minutes per 500g plus 20) is wrong for both.

    The oven time is only right for the oven: a line that names another way of cooking it gets
    that method's time, because "how long to boil chicken legs" was being told to roast them.
    Cooked from frozen takes longer whatever the method, and the follow-up after a method answer
    ("does that change if theyre from frozen") is the same question with one word added."""
    reply = _legs_method(understood)
    words = " ".join(understood.get("words") or [])
    if "frozen" in words or "freezer" in words:
        reply += " From frozen, add about 10 minutes and check at the bone before you serve it."
    return reply


def _legs_method(understood):
    """The time for the way of cooking the line names, the oven when it names none."""
    words = " ".join(understood.get("words") or [])
    small = "drumstick" in words or "drumsticks" in words
    done = ("It is done when the juices at the thickest part run clear and the meat pulls away from "
            "the bone - if you have a thermometer, 74C.")
    if "boil" in words or "boiling" in words or "poach" in words or "poached" in words or \
            "simmer" in words or "simmering" in words:
        return (f"Simmer {'drumsticks' if small else 'the legs'} in salted water for "
                f"{'20 to 25' if small else '25 to 30'} minutes. {done}")
    if "grill" in words or "grilled" in words or "grilling" in words or "barbecue" in words or \
            "barbeque" in words or "bbq" in words:
        return (f"Over medium heat, a {'drumstick' if small else 'leg'} takes about "
                f"{'8 to 10 minutes a side' if not small else '10 minutes a side'}, turning once and "
                f"moving it off the hottest spot if it colours too fast. {done}")
    if "slow" in words or "crockpot" in words or "crock" in words:
        return ("In a slow cooker, legs take 3 to 4 hours on low with a splash of stock or a tin of "
                f"tomatoes; drumsticks are done nearer 2 to 3. {done}")
    if "air" in words:
        return (f"In an air fryer, {'drumsticks' if small else 'legs'} take "
                f"{'20 to 25' if small else '25 to 30'} minutes at 190C, turned once, until the skin "
                f"is crisp. {done}")
    if small:
        return ("Roast drumsticks at 200C (180C fan) for 25 to 30 minutes, skin side up and spaced "
                "out, until the skin is crisp and the juices at the bone run clear. Salt the skin "
                "first, and give them a turn halfway if your oven has a hot spot.")
    return ("A whole chicken leg takes 35 to 40 minutes at 200C (180C fan), skin side up: a "
            "drumstick alone is 25 to 30. It is done when the juices at the thickest part run "
            "clear and the meat pulls away from the bone - if you have a thermometer, 74C. Salt "
            "the skin and don't crowd the tray, or it steams instead of crisping.")


# A chicken tender is a thin piece, so the whole-bird rule (20 minutes per 500g plus 20) is
# nearly an hour too long for it: "how do i cook chicken tenders" was given the time for a 2kg
# bird. Each way of cooking it has its own minutes, the same way a leg's do.
def _tenders_method(memory, understood):
    """The time for the way of cooking the line names, the oven when it names none."""
    words = " ".join(understood.get("words") or [])
    done = ("They are done when the middle is 74C and no pink is left - cut the thickest one "
            "open if you have no thermometer.")
    if "air" in words or "airfryer" in words or "airfryers" in words:
        return ("In an air fryer, chicken tenders take 9 to 10 minutes at 190C in a single layer, "
                "shaken once halfway. " + done)
    if "grill" in words or "grilled" in words or "grilling" in words:
        return ("Under a hot grill, chicken tenders take 4 to 5 minutes a side, turned once. " + done)
    if ("fry" in words or "fried" in words or "frying" in words or "pan" in words
            or "shallow" in words):
        return ("In a frying pan over a medium heat, chicken tenders take 3 to 4 minutes a side, "
                "until golden outside and white in the middle. " + done)
    return ("Chicken tenders are thin, so 10 to 12 minutes in a 200C (180C fan) oven is enough: "
            "spread out on an oiled tray and turned once halfway. " + done)


def _bird_weight(understood):
    """The weight of the bird, in kilos, when the line gives one: "a 1.5kg chicken"."""
    for number in understood.get("numbers") or []:
        value, unit = number.get("value"), number.get("unit")
        if not isinstance(value, (int, float)) or value <= 0:
            continue
        kilos = {"kg": value, "g": value / 1000.0, "lb": value * 0.4536,
                 "oz": value * 0.02835}.get(unit)
        if kilos and 0.4 <= kilos <= 12:
            said = str(number.get("text") or "")
            # The reading keeps the words the person typed, and for "half a kilo" that is the
            # bare "half": read back as "a half bird takes 40 minutes" it says the wrong thing.
            # The weight itself says it right, so it is used unless the words name a unit.
            if not re.search(r"\d|\b(?:kilo\w*|kg|g|lb|lbs|pound|pounds|oz|ounce|ounces)\b",
                             said.lower()):
                said = _weight_words(kilos)
            # "a kilo of pork" is answered "so a kilo one is about 50 minutes": the article is
            # the count, so saying it again after "a" reads as "a a kilo one".
            ours = re.match(r"(?:a|an)\s+(.+)$", said.lower())
            if ours:
                said = ours.group(1)
            return kilos, said
    return None


def _hours_words(hours):
    """18 -> "18 hours", 36 -> "a day and a half", 60 -> "two and a half days"."""
    hours = int(round(hours / 3.0)) * 3
    if hours < 24:
        return f"{hours} hours"
    days, rest = divmod(hours, 24)
    whole = {1: "a day", 2: "two days", 3: "three days", 4: "four days", 5: "five days"}
    half = {1: "a day and a half", 2: "two and a half days", 3: "three and a half days"}
    if rest == 0 and days in whole:
        return whole[days]
    if rest == 12 and days in half:
        return half[days]
    return f"{hours} hours"


def _in_words(minutes):
    """80 -> "1 hour 20 minutes", 100 -> "1 hour 40 minutes", 45 -> "45 minutes"."""
    minutes = int(round(minutes / 5.0)) * 5
    hours, rest = divmod(minutes, 60)
    if not hours:
        return f"{rest} minutes"
    hours_text = f"{hours} hour" + ("" if hours == 1 else "s")
    # "1 hour 40" on its end reads as a figure cut off: the same reply is given on its own as
    # the answer to "how long will it take", and a bare "1 hour 40." there loses its unit.
    return f"{hours_text} {rest} minutes" if rest else hours_text


def _chicken_time(memory, understood):
    """A whole chicken: 20 minutes per 500g plus 20, at 190C, for the weight they gave.

    "Is 4 pounds a lot for a chicken" carries a figure in pounds and asks whether it is dear, so
    the four pounds is money and not the bird: the minutes in the oven answer a question nobody
    asked, and the price row answers this one.
    """
    said_line = str((understood or {}).get("clean") or (understood or {}).get("text") or "")
    if a_price_is_judged(said_line):
        return None
    check = ("Check the thigh reads 74C on a thermometer and the juices run clear, then rest it "
             "for 15 minutes before carving.")
    kilos, said = _bird_weight(understood) or (2.0, "2kg")
    return ("About 20 minutes per 500g plus 20 minutes at 190C (170C fan), so a "
            f"{said} bird takes roughly {_in_words(20 * (kilos / 0.5) + 20)}. " + check)


# "how do i make a dry rub" names no food at all, and the answer is the method: what goes into
# one, in what proportion, and what to leave out. It was the blister card, because "rub" is a
# word a new pair of shoes also needs.
_A_RUB = (
    "A dry rub is salt, sugar, pepper and paprika in roughly equal parts, then whatever else the "
    "food wants - garlic powder, cumin, mustard powder, chilli, dried thyme. About a tablespoon "
    "of rub covers a kilogram of meat: rub it on with a little oil, leave it an hour or overnight "
    "in the fridge, and keep the sugar under a fifth of the mix if it is going on a hot barbecue, "
    "because sugar burns before the meat is done.")


def _a_seasoning(text):
    """The seasoning answer for the food this line names, or None when it names none I know."""
    best = None
    for names, reply in SEASONINGS:
        for name in names:
            if re.search(r"\b" + re.escape(name) + r"\b", text) and (
                    best is None or len(name) > best[0]):
                best = (len(name), reply)
    if best:
        return best[1]
    if re.search(r"\b(?:dry rub|spice rub|make a rub|what goes in a rub|rub recipe)\b", text):
        return _A_RUB
    return None


# A plate takes this many people before one pan stops being enough, so only six or more counts as
# a crowd. The small numbers are read as well as the large ones, because the count in the line has to win
# over a phrase that only suggests one: "dinner party for four" matched "dinner party", which
# stands for eight, and the card told a table of four that the dish "feeds eight from one oven".
# Reading it as four also lets a count of three to five reach the meal table at all - "dinner for
# four", "supper for four" and "cooking for four" all reached the store, which said the line back.
_ONES = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
         8: "eight", 9: "nine"}


_TEENS = {10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
          15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen"}


_TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy",
         80: "eighty", 90: "ninety"}


def _spelled_counts():
    """Every count a person spells out, from two up to a hundred.

    The written-out numbers used to stop at twenty, so "dinner for thirty people" was not a count
    at all and got the answer for one plate: it is the same question as "for twenty", read the
    way a typed number is read.
    """
    counts = {word: value for words in (_ONES, _TEENS, _TENS) for value, word in words.items()
              if value >= 2}
    for tens, tens_word in _TENS.items():
        for one, one_word in _ONES.items():
            counts[tens_word + " " + one_word] = tens + one
    counts["hundred"] = 100
    counts["a hundred"] = 100
    return counts


_CROWD_PHRASES = ("for a crowd", "a crowd", "big group", "lots of people", "loads of people",
                  "a dozen",
                  "dinner party", "buffet", "guests", "guest coming", "guests coming",
                  "people coming", "people round", "family over", "the in laws", "in-laws",
                  "entertaining", "everyone is coming", "everyone's coming", "a party",
                  "whole family", "big family", "family dinner", "big dinner", "large family",
                  "extended family",
                  # "im having friends over for dinner" names a table of people without a count:
                  # the company is the number, so it is not a question for a ten-minute dinner.
                  # The hosting shapes only: "i saw my friends over the weekend" is not a table.
                  "having friends", "having people", "friends round", "friends coming",
                  "family round", "family coming", "friends over for", "friends over to",
                  "people over for", "people over to", "mates over", "mates round")


# A birthday or a wake asking for dinner is not a ten-minute dinner either: the question is what
# to cook for several people on a day that matters.
_OCCASIONS = ("birthday", "anniversary", "christening", "wedding", "retirement",
              "graduation", "mother's day", "mothers day", "father's day", "fathers day",
              "christmas", "easter", "thanksgiving", "wake", "funeral", "celebration",
              "special occasion")


# What a number after "for" is when it is not people. "Dinner for 8" is a table and "cook it for
# 20 minutes" is a time, and both say "for <number>": the word after the number is what tells them
# apart. Without this, "what can i eat for 500 calories" was five hundred people to feed and got
# the one-big-oven-dish answer, and every "fry it for 5 minutes" line carried a table of five.
_NOT_A_TABLE = ("minute", "minutes", "min", "mins", "hour", "hours", "hr", "hrs", "second",
                "seconds", "sec", "secs", "calorie", "calories", "cal", "cals", "kcal",
                "kilo", "kilos", "kilogram", "kilograms", "kg", "gram", "grams", "g", "mg",
                "litre", "litres", "liter", "liters", "ml", "oz", "ounce", "ounces", "lb",
                "lbs", "pound", "pounds", "degree", "degrees", "c", "f", "cm", "mm", "inch",
                "inches", "quid", "dollar", "dollars", "euro", "euros", "pence", "pennies",
                "slices", "slice", "pieces", "piece", "tins", "tin", "cans", "can", "spoons",
                "spoon", "tablespoons", "teaspoons")


def _people_after(text, end):
    """True when what follows the count at `end` is not a unit, so the number is people.

    "Dinner for 8" is a table and "cook it for 20 minutes" is a time, and both say "for <number>":
    the word after the number is what tells them apart. Without this, "what can i eat for 500
    calories" was five hundred people to feed and got the one-big-oven-dish answer, and every
    "fry it for 5 minutes" line carried a table of five.
    """
    rest = text[end:].strip().split()
    after = rest[0].strip(".,!?;:").lower() if rest else ""
    return after not in _NOT_A_TABLE


# Ways of saying there are people to feed. With a count under six these are still a table
# question when the line asks what to cook: four people at the table is one oven dish, not a
# list of dinners for one. "dinner for four" has none of these, and stays ordinary cooking.
_TABLE_PHRASES = ("people coming", "people round", "people over", "people for dinner",
                  "people to feed", "people to cook for", "of us", "guests coming",
                  "guests for dinner")


# The verbs that make a table line a cooking question.
_CROWD_VERBS = ("cook", "cooking", "make", "serve", "feed", "dinner", "tea", "supper",
                "lunch", "eat", "eating")


# A table line can also be all nouns: "what food would be easy for twenty people", "easy food
# for twenty people", "what food is easy for a crowd". The count is what makes it a cooking
# question, so a food noun is enough without a verb. Before this, four of those phrasings got
# nothing but a search hedge or a "Got it", while "what should i cook for 20 people" answered.
_CROWD_FOOD = ("food", "foods", "meal", "meals", "dish", "dishes", "buffet", "nibbles",
               "finger food", "spread", "platter", "platters", "menu")


# Not every line with a count and a food noun is a table to cook for: "how much food for 30
# people" is the portions figure (units.py answers it, in kilos), and food poisoning, a food
# bank and the dog's dinner have their own answers.
_CROWD_QUANTITY = ("how much", "how many", "amount", "quantity", "weighs", "weight", "grams",
                   " kg", "kilos", "per head", "per person", "per guest")
