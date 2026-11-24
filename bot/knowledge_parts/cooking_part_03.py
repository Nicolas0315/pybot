"""Part 3 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

from ..understanding import line_as_read
# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.units import BIRD_GRAMS
from .cooking_part_01 import (
    _bird_weight, _in_words,
)
from .cooking_part_02 import (
    _same, _asks_why, _the_bake_named,
)


# "im bored of chicken, what else can i cook", "im sick of pasta": the line names a food to
# rule it out, so an entry answering "how long do i roast that" or "how do i boil that" has
# the ask wrong. The meal table answers with a dish that leaves the food out.
_FREEZE_AVOID = ("make with", "cook with", "do with", "what can i make", "what can i cook", "ideas", "dinner", "tonight", "use up")


_CHEAP_AVOID = ("cheap", "cheap recipe", "cheap recipes", "cheap meal", "budget")


_MEAL_ASK_AVOID = ("cook with", "cooking with", "make with", "do with", "ideas", "idea", "dinner", "tonight", "meal", "meals", "recipes", "recipe")


WANT_SOMETHING_ELSE = ("bored", "bored of", "sick of", "tired of", "fed up", "had enough",
                       "what else", "something else", "anything else", "instead",
                       "other ideas")


_CLUMP_WORDS = ("clump", "clumps", "clumped", "clumping", "lump", "lumps", "stuck", "sticks",
                "sticking", "together", "gluey", "sticky")


_EGG_STORE = ("store", "storing", "stored", "keep", "keeps", "keeping", "last", "lasts",
              "longer", "fridge", "fridged", "freeze", "room", "counter", "cupboard")


_EGG_STORE_TEXT = ("Keep eggs cold and steady: in the fridge, in their carton, pointy end down, "
                   "away from anything strong-smelling, because the shells are porous. Stored that "
                   "way they keep well past their date. ")


_EGG_TEST_TEXT = ("Put a suspect egg in a glass of water: one that lies flat on the bottom is "
                  "fresh, one that stands on end is older but fine, and one that floats is past it. ")


def _eggs(memory, understood):
    """How to store eggs, or how to test one: whichever the line asked about comes first."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(word in ("fresh", "off", "bad", "rotten", "float", "test", "edible", "safe",
                    "date", "dated", "expired", "expiry", "ok", "okay", "fine", "use",
                    "usable", "eat", "eaten", "yesterday", "week", "weeks", "old")
           for word in words) and not any(word in _EGG_STORE for word in words):
        return _EGG_TEST_TEXT + _EGG_STORE_TEXT.strip()
    return _EGG_STORE_TEXT + _EGG_TEST_TEXT.strip()


def _pasta_cook(memory, understood):
    """How to cook pasta, plus the clumping answer when that is what went wrong."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    text = ("Use a big pan of well-salted water, about 10g of salt per litre, and cook the pasta "
            "one minute less than the packet says. Keep a mug of the cooking water: a splash of it "
            "makes any sauce cling to the pasta.")
    if any(word in _CLUMP_WORDS for word in words):
        text += (" Clumping is the pasta sitting still in water that is not deep or hot enough, so "
                 "stir it for the first minute and again every couple of minutes, and leave the "
                 "oil out: it stops the sauce clinging.")
    return text


def _popcorn_make(memory, understood):
    """The pan, the microwave and no oil are three ways to make the same bowl.

    The card carries all three, so the one the line names goes first: "how do i make popcorn in
    the microwave" wanting the pan method first reads as the wrong answer.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    pan = ("Three kernels and a tablespoon of oil in a big lidded pan over medium heat, and when "
           "those three pop, add a single layer of kernels and put the lid back on. Shake the pan "
           "every so often and take it off the heat when the pops slow to one every few seconds, "
           "about 3 minutes for four tablespoons of kernels. Tip it into a bowl, salt it while it "
           "is hot, and leave the lid off so the steam gets away and it stays crisp.")
    microwave = ("Put a quarter of a cup of kernels in a paper bag or a bowl with a plate over it "
                 "and give it 2 to 3 minutes on full power, stopping the moment the pops slow to "
                 "one every few seconds; a bag is the easy way because the steam escapes. Salt it "
                 "while it is hot and leave the lid off the bowl so it stays crisp.")
    dry = ("Dry kernels pop without any oil: shake a single layer of them in a heavy lidded pan "
           "over medium heat, lifting the pan off the ring every few seconds so the bottom does "
           "not scorch, until the pops slow. Or use an air popper, which is the same thing with "
           "the stirring done for you.")
    if any(_same(word, way) for word in words
           for way in ("microwave", "microwaved", "microwaving", "microwaves", "bag", "bags")):
        return microwave + " " + pan if "hob" in words or "pan" in words else microwave
    if any(_same(word, way) for word in words
           for way in ("oil", "air", "popper", "diet", "healthy")):
        return dry
    return pan


def _popcorn_keep(memory, understood):
    """Keeping popcorn is a cupboard question; chewy popcorn is a fault with this batch.

    The card answers both, so the cause goes first when the line is about how the batch came
    out: "my popcorn came out chewy" wants the reason, and "how long does popcorn keep" wants
    the tin.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(_same(word, fault) for word in words
           for fault in ("chewy", "soggy", "squidgy", "tough", "rubbery")):
        return ("Chewy popcorn was either stale to start with or it did not get hot enough: use "
                "kernels under a year old, keep them in a sealed jar rather than the fridge, and "
                "give the pan a few more seconds after the pops slow to one every few seconds. "
                "Leave the lid off the bowl once it is out, because the steam it sits in is what "
                "turns the rest soft.")
    return ("Kernels keep for about a year in a sealed jar in a cool cupboard, and popped corn goes "
            "soft within a day or two, so an airtight tin is what keeps it crisp. Popcorn that "
            "comes out chewy was stale to start with or did not get hot enough: use kernels under "
            "a year old and give the pan a few more seconds after the pops slow.")


_STEWED_FRUIT = ("apple", "apples", "pear", "pears", "rhubarb", "plum", "plums",
                 "cherry", "cherries", "apricot", "apricots", "berry", "berries",
                 "fruit", "quince", "peach", "peaches")


# Why a stewed fruit stayed hard is the fruit's own business: a Bramley collapses where a Cox
# holds, and rhubarb's stalk decides its five minutes. One sentence, named for the fruit.
_STEWED_WHY = (
    (("apple", "apples"), "apple", "a Bramley collapses to a fluff while a Cox or a Braeburn "
     "holds its shape, so use Bramleys for a sauce, a crumble or a compote"),
    (("pear", "pears"), "pear", "a Conference softens where a Comice is for eating raw, and a "
     "hard pear wants 10 more minutes"),
    (("rhubarb",), "rhubarb", "thin young stalks give way in 5 minutes and thick old ones want "
     "15, so pick the thin ones and add the sugar once they have softened"),
    (("plum", "plums"), "plum", "a ripe plum collapses in 5 minutes and a firm one holds, so "
     "halve them and taste at 5"),
    (("cherry", "cherries"), "cherry", "cherries want 5 to 8 minutes and go from firm to jam "
     "quickly, so take them off while they still hold"),
    (("apricot", "apricots", "peach", "peaches"), "apricot", "a ripe one collapses in 5 minutes "
     "and an underripe one stays firm whatever you do, so halve them and poach them gently"),
    (("berry", "berries"), "berry", "berries want only 2 or 3 minutes and a hard one was "
     "underripe to begin with"),
    (("quince",), "quince", "a quince stays hard for 40 minutes and then turns pink and soft all "
     "at once, so give it the time and taste it"),
)


def _stewed_fruit(words):
    named, why = "fruit", ("a firm one holds its shape where a ripe one collapses, so use the "
                           "ripe ones for a compote")
    for forms, name, reason in _STEWED_WHY:
        if any(_same(word, form) for word in words for form in forms):
            named, why = name, reason
            break
    return ("A stewed %s that stays hard was the fruit rather than the cooking: %s. Give it 10 "
            "more minutes with a splash of water and taste as it goes, because it goes from firm "
            "to pulp quickly once it starts." % (named, why))


def _tough(memory, understood):
    """Chewy food that is meat, squid or a batter each wants a different answer."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(_same(word, "squid") for word in words):
        return ("Squid is either 2 minutes or 40: flash it in a very hot pan, or stew it slowly with "
                "tomatoes and wine for 40 minutes. Anything in between turns it to rubber.")
    # Stewed fruit is the same word about a different thing: a tough stewed apple was a hard
    # apple, and it is not going to soften in another 30 minutes without turning to pulp. It gets
    # the fruit's own answer, named, because the fruit decides why it stayed hard.
    if (any(_same(word, fruit) for word in words
            for fruit in _STEWED_FRUIT)
            and any(_same(word, way) for word in words
                    for way in ("stewed", "stew", "poached", "compote", "baked", "puree"))):
        return _stewed_fruit(words)
    # Tough meat in a pot is the one case where the fix is more time and not a hotter pan: "my
    # stew is tough" was getting the batter line ("pancakes and batters want a lumpy mix"), which
    # is the wrong pan and the wrong food. This goes before the meat branch because the pot
    # decides the answer, whatever meat is in it.
    if (any(_same(word, pot) for word in words
            for pot in ("stew", "stews", "casserole", "braise", "braised", "braising", "goulash",
                        "hotpot", "tagine", "ragu", "chilli", "chili"))
            and not any(_same(word, fruit) for word in words for fruit in _STEWED_FRUIT)):
        return ("A tough stew is an underdone one rather than an overcooked one: another 30 to 45 "
                "minutes at a bare simmer with the lid on, and top the liquid up if it is running "
                "low. A simmer that is really a boil tightens the meat instead of softening it, so "
                "keep it just trembling and test a piece with a fork - it is ready when it gives "
                "way without resistance.")
    if any(_same(word, meat) for word in words
           for meat in ("steak", "meat", "beef", "pork", "lamb", "chicken", "chop", "chops",
                        "turkey", "sausage", "sausages", "burger", "burgers", "roast", "gammon",
                        "duck", "ribs")):
        if _asks_why(words):
            return ("It went tough from cooking too fast or from not resting: the muscle fibres "
                    "contract and squeeze the juice out, and a cheap cut needs longer at a lower "
                    "heat to break down instead - 2 hours at 160C with liquid in the pan. This "
                    "piece is best sliced thinly across the grain and served with something wet.")
        return ("Slice it thinly across the grain and serve it with something wet; that rescues more "
                "tough meat than anything else. It went tough from cooking too fast or not resting, "
                "so next time go slower: a cheap cut wants 2 hours at 160C with liquid in the pan.")
    # Tough pasta or rice is the opposite fault to tough meat: it is underdone, and more time is
    # the fix. Vegetables of every kind are answered by dishes' own vegetable table, so they are
    # not named here; the batter line below is the last fallback.
    if any(_same(word, starch) for word in words
           for starch in ("pasta", "noodle", "noodles", "rice")):
        return ("Tough here is underdone rather than overcooked: give it 5 more minutes in boiling "
                "water and test it with the tip of a knife, and cut the pieces the same size so they "
                "finish together. A pan that never came back to the boil is the usual reason it is "
                "still hard in the middle when the outside is done.")
    # A tough cake or scone is over-mixed, not undercooked: every stir after the flour goes in starts
    # gluten, and the batter line below would send someone back to the pan for nothing.
    if any(_same(word, bake) for word in words
           for bake in ("cake", "cakes", "sponge", "sponges", "muffin", "muffins", "cupcake",
                        "cupcakes", "scone", "scones", "brownies", "brownie", "bun", "buns",
                        "traybake", "traybakes", "loaf", "loaves")):
        thing, plural = _the_bake_named(words)
        return ("Tough " + thing + (" are" if plural else " is") if thing else "A tough bake is") + (
            " mixed too much or a little too long in the oven, or short of fat. Stir only until "
            "the flour disappears, fold rather than beat, and weigh the butter rather than "
            "eyeballing it, because a sponge wants as much fat as eggs by weight. One that is "
            "already tough is best eaten warm with something wet, or torn up for a trifle.")
    # Pastry goes tough in the other direction from a vegetable: it was worked too much or made
    # too wet, and cooking it longer only makes it worse. The batter line would be nonsense here.
    if any(_same(word, pastry) for word in words
           # bare `dough` is not pastry: a tough bread dough is an over-kneaded loaf, and the
           # bread branch below answers it.
           for pastry in ("pastry", "shortcrust", "shortcrust pastry", "pie crust",
                          "pie", "tart", "quiche", "crumble")):
        return ("Tough pastry is over-worked or too wet: keep the fat cold, rub it in with your "
                "fingertips only until it looks like fine breadcrumbs, add iced water a spoon at a "
                "time and bring it together fast. Shortcrust wants about half its weight in fat to "
                "flour, and 20 minutes in the fridge before it is rolled; roll it between two sheets "
                "of greaseproof so you never stretch it. Pastry that is already baked cannot be "
                "rescued, so serve it with something wet.")
    if any(_same(word, bread) for word in words
           for bread in ("bread", "loaf", "roll", "rolls", "baguette", "pitta", "naan", "bun",
                         "buns", "bagel", "bagels")):
        return ("Tough bread is usually over-kneaded or baked too slowly: knead until the dough "
                "springs back and stops tearing, prove it somewhere warm until it has doubled, and "
                "bake it hot (220C) for the first 10 minutes so it rises before the crust sets. "
                "Bread that has already gone leathery comes back in a hot oven for 5 minutes with a "
                "splash of water in the tin.")
    if any(_same(word, egg) for word in words for egg in ("egg", "eggs", "omelette", "scrambled")):
        # "the eggs went rubbery in the microwave" was getting the pancake-batter answer, which
        # is a different food and a different fix.
        return ("Rubbery eggs have been cooked too long, and in a microwave that happens in seconds: "
                "beat them, give them 30 seconds at a time on medium, stir hard between each go, "
                "and stop while they still look a little wet, because they carry on setting as "
                "they stand. The same rule in a pan - low heat, slow stirring, off the heat early.")
    return ("Rubbery is overcooked, or a batter that was beaten too much: pancakes and batters want "
            "a lumpy mix and a minute less in the pan. It's hard to rescue on the plate, so serve it "
            "with something wet and cook it less next time.")


_BAKE = ("cake", "cakes", "sponge", "bread", "loaf", "buns", "bun", "scones", "scone",
         "muffins", "muffin", "brownies", "brownie", "pancakes", "yorkshire pudding", "biscuits",
         "biscuit", "pastry", "dough", "batter", "pie")


def _salty(memory, understood):
    """A cake that is salty cannot be bulked out with potatoes, so baking has its own answer."""
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    if any(_same(word, bake) for word in words for bake in _BAKE):
        return ("Baking is the one place salt cannot be cooked out or bulked out: leave it and cut the "
                "salt from whatever goes with it, or add a little more sugar and fat to push it into "
                "the background. Next time weigh the salt with the measuring spoons rather than "
                "shaking it in, and remember salted butter is already about a quarter salt.")
    return ("Don't add water: bulk it out with more of what's already in it — potatoes, rice, tinned "
            "tomatoes, cream or unsalted stock — and finish with a squeeze of lemon. In a soup or "
            "stew, a peeled potato simmered in it for 15 minutes takes up some of the salt too.")


def _scramble(memory, understood):
    """Scrambled eggs that went watery and scrambled eggs that went rubbery are two faults.

    "How do I make scrambled eggs" is neither: with no fault word in the line it is the method.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]
    # A line that only asks how is the method; a line that says what went wrong is a fault, and a
    # misspelt fault still reads as one because the method answer is not the one a person wants
    # when they tell you their eggs always come out rubbery.
    asks_how = (understood.get("kind") == "question"
                or any(_same(word, "how") for word in words))
    if asks_how and not any(_same(word, fault) for word in words
                            for fault in ("watery", "wet", "sloppy", "rubbery", "rubber", "tough",
                                          "dry", "hard", "overcooked", "chewy", "curdled",
                                          "mushy")):
        return ("Beat 2 or 3 eggs with a pinch of salt, melt a knob of butter in a pan over a low "
                "heat, pour them in and stir slowly with a spatula, pushing the set egg in from the "
                "edges. Take them off while they still look a little wet, after 2 or 3 minutes, "
                "and stir in a little more butter off the heat.")
    if any(_same(word, wet) for word in words for wet in ("watery", "wet", "sloppy")):
        return ("Watery scrambled eggs have been cooked too long: the curds squeeze out their "
                "water as they tighten. Cook them low and slow, stirring, and take them off while "
                "they still look a little loose, then stop the heat with a knob of cold butter or "
                "a spoon of creme fraiche.")
    return ("Rubbery scrambled eggs come from too much heat: cook them low and slow, stirring, and "
            "take them off while they still look slightly wet, because they carry on setting. A "
            "knob of butter at the end stops them going dry.")


# An egg in a pan, an egg in a quiche and an egg in a jug are three different faults with three
# different fixes, and the fault word is the same in all of them: "my omelette is rubbery" was
# reaching the pancake-batter answer, "my frittata is rubbery" the same one, "my quiche is
# rubbery" the tough-pastry answer, and "my creme anglaise is grainy" nothing at all.
_EGG_DISH = ("omelette", "omelet", "omelettes", "omelets", "frittata", "frittatas", "quiche",
             "quiches", "fried egg", "fried eggs", "creme anglaise", "creme patissiere",
             "creme patisserie", "pastry cream", "custard sauce")


_EGG_FAULT = ("rubbery", "rubber", "tough", "leathery", "overcooked", "over cooked",
              "fell apart", "falls apart", "falling apart", "wouldnt fold", "wont fold",
              "split", "splits", "curdled", "grainy", "gritty", "watery", "weeping", "dense",
              "soggy", "lumpy", "chewy")


_EGG_PAN = ("omelette", "omelet", "omelettes", "omelets")


_EGG_FRITTATA = ("frittata", "frittatas")


_EGG_QUICHE = ("quiche", "quiches")


_EGG_FRIED = ("fried egg", "fried eggs")


_EGG_SAUCE = ("creme anglaise", "creme patissiere", "creme patisserie", "pastry cream",
              "custard sauce")


def _egg_fault(memory, understood):
    """A fault in an egg dish, answered by the dish: the pan, the oven or the jug.

    "My omelette fell apart" is not overcooking at all, so the fold has its own answer, and a
    curdled sauce is a temperature problem while a rubbery quiche is simply a minute too long.
    """
    words = [str(word).lower() for word in ((understood or {}).get("words") or [])]
    if not words:
        return None
    said = " ".join(words)

    def named(names):
        return any(name in said for name in names)

    def fault(*names):
        return any(_same(word, name) for word in words
                   for name in names) or any(name in said for name in names)

    if named(_EGG_SAUCE) and fault("grainy", "gritty", "split", "splits", "curdled", "curdles",
                                  "lumpy", "scrambled"):
        return ("A grainy or split creme anglaise has curdled, because the eggs went above about "
                "82C. Take it off the heat at once, whisk in a splash of cold milk to stop it "
                "cooking, then strain it through a sieve and it comes back smooth. Next time cook "
                "it over a low heat, stirring all the time, and pull it off as soon as it coats "
                "the back of the spoon.")
    if named(_EGG_SAUCE):
        return None
    if named(_EGG_QUICHE):
        if fault("rubbery", "rubber", "tough", "dense", "overcooked", "over cooked"):
            return ("A rubbery quiche is a custard that stayed in too long: the filling is firm "
                    "at about 80C, so bake it at 180C for 30 to 35 minutes, until the middle "
                    "still has a slight wobble, and let it cool for 20 minutes, because it firms "
                    "as it stands. Two eggs to 200ml of double cream in a 20cm tin sets soft; "
                    "more egg than that sets like rubber.")
        # A watery or dry quiche already has an answer on the bake and the pastry case, so this
        # only speaks for the set custard, which is the fault nothing else knew.
        return None
    if named(_EGG_FRIED):
        return ("Fried eggs go rubbery when the white sets hard before the yolk is warm: cook "
                "them on a medium heat with a lid on for 2 to 3 minutes, so the top sets in the "
                "steam, and take them out while the yolk still wobbles. On a high heat the white "
                "blisters and toughens long before the yolk is hot.")
    if named(_EGG_FRITTATA) or named(_EGG_PAN):
        if fault("fell apart", "falls apart", "falling apart", "wouldnt fold", "wont fold",
                 "broke", "tears", "tore"):
            return ("An omelette tears when the eggs are too thin for the pan, so use a 20cm pan "
                    "and no more than three eggs, let the base set for 45 seconds before you fold, "
                    "and fold it with a spatula in the pan instead of lifting it out. A frittata "
                    "is finished under the grill and never folded, which is the same dish without "
                    "the part that breaks.")
        if fault("soggy", "watery", "wet"):
            # A frittata or an omelette that will not set is wet vegetables, not heat: the water
            # they hold comes out in the pan and the eggs cannot firm around it.
            return ("An omelette or frittata that stays wet is a vegetable problem: mushrooms, "
                    "courgette, spinach and onion all give out water as they cook. Fry them first, "
                    "on their own, until their water has gone and they are starting to colour, and "
                    "let them cool a little before the eggs go in. A pinch of salt in the beaten "
                    "egg also helps it set.")
        if fault("rubbery", "rubber", "tough", "leathery", "overcooked", "over cooked",
                 "chewy"):
            return ("An omelette goes rubbery from the pan and the clock rather than the eggs: a "
                    "20cm pan on a medium heat, two beaten eggs with a pinch of salt, and pull the "
                    "set edges into the middle for 60 to 90 seconds, then fold and slide it out "
                    "while the top still looks a little wet. A small pan steams it instead of "
                    "setting it, and one more minute is enough to make it leathery.")
        return None
    return None


def _cookies(memory, understood):
    """Cookies that spread too far, and the opposite fault, cookies that never spread at all."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    said = " ".join(words)
    # "my cookies didnt spread" is the other fault: the dough went in as balls and came out as
    # balls, which is too much flour or butter that was too cold, not dough that was too warm.
    if any(phrase in said for phrase in ("didnt spread", "didn't spread", "did not spread",
                                        "not spread", "not spreading", "wont spread",
                                        "won't spread", "stayed in a ball", "stayed in balls",
                                        "too thick", "too small", "didnt flatten",
                                        "didn't flatten", "did not flatten", "stayed round")):
        return ("Cookies that stay in a ball have usually had too much flour or butter that was "
                "too cold: weigh the flour rather than scooping the cup, use soft butter, and "
                "press each ball down to about 1cm with the back of a spoon before it goes in. A "
                "tablespoon of milk or an extra yolk loosens a dry dough, and the oven wants to be "
                "properly hot, 180C (160C fan), so they set before they can spread.")
    return ("Cookies spread when the dough is warm or the butter is too soft: chill the dough 30 "
            "minutes and put it on a cool tray, and leave a good 5cm between them. Too much sugar "
            "or a greased tin makes them spread further, and a fan oven needs 20C less than the "
            "recipe.")


def _chocolate(memory, understood):
    """Melting chocolate in the first place, and rescuing a bowl that has seized."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    # "white" is a kind of chocolate as well as a fault on one: "how do i melt white chocolate" and
    # "white chocolate ganache" are melting questions, so the word only counts as bloom when it is
    # not in front of the word chocolate.
    said = " ".join(words)
    told_apart = re.sub(r"\bwhite\s+(?=chocolate\b)", "", said).split()
    if any(_same(word, fault) for word in told_apart
           for fault in ("bloom", "white", "streak", "streaks", "grey", "gray")):
        return ("White streaks on chocolate are bloom, and it is harmless: either cocoa butter or "
                "sugar has come to the surface because the chocolate got warm and then cool again. "
                "It still tastes the same and it is fine to eat or to melt. To stop it happening, "
                "store it cool and steady, around 15 to 18C, and never in the fridge.")
    # "is white chocolate real chocolate" and "is dark chocolate healthy" are questions about what
    # the stuff is, not about melting it, so they are answered before the method.
    if any(phrase in said for phrase in ("healthy", "good for you", "bad for you",
                                        "better for you", "fattening", "sugar", "calorie",
                                        "calories", "diet")):
        return ("As a treat, chocolate is fine: dark with 70% cocoa or more has the least sugar, so "
                "it is the one to pick if you are watching it, and two squares is a normal "
                "portion. White chocolate is the sweetest of the three because it is cocoa butter, "
                "milk and sugar with no cocoa solids at all.")
    if any(phrase in said for phrase in ("real chocolate", "is it chocolate", "actually chocolate",
                                        "made of", "made from", "contain", "contains",
                                        "what is chocolate", "is white chocolate",
                                        "whats in chocolate", "what's in chocolate")):
        if "white" in words:
            return ("White chocolate is cocoa butter, milk powder and sugar, with no cocoa solids "
                    "at all, which is why it tastes of vanilla and milk rather than of chocolate. "
                    "It is still real chocolate by the labelling rules - at least 20% cocoa butter "
                    "in Europe - just a different thing from dark, and it is the sweetest of the "
                    "three.")
        return ("What most people mean by chocolate is dark: cocoa solids and cocoa butter with "
                "sugar, and the higher the percentage the less sugar there is. Milk chocolate "
                "adds milk powder and more sugar, and white chocolate is cocoa butter, milk and "
                "sugar with no cocoa solids at all.")
    if any(_same(word, "temper") for word in words):
        return ("To temper chocolate, melt two thirds of it in a bowl over barely simmering water "
                "to 45C (or 40C for white), take it off the heat and stir in the rest, chopped, "
                "until it drops to 27C, then warm it gently back to 31C for dark or 29C for milk "
                "and white. That sets it glossy and hard at room temperature. A thermometer earns "
                "its keep; without one, a clean spoon dipped in should set firm in 5 minutes.")
    # "how do i melt chocolate for dipping" is a melting question: only a line that does not ask
    # about melting gets the dipping method
    if (any(_same(word, want) for word in words
            for want in ("dip", "dipped", "dipping", "strawberry", "strawberries"))
            and not any(_same(word, want) for word in words
                        for want in ("melt", "melting", "melted"))):
        return ("Melt it slowly, then dip: dry the fruit first so the chocolate grips, dip about "
                "two thirds of the way in, let the extra drip back into the bowl, and set them on "
                "baking paper in the fridge for 10 minutes to set hard. If the chocolate feels "
                "thin, stir in a handful more chopped chocolate off the heat.")
    if any(_same(word, fault) for word in words
           for fault in ("seize", "seized", "seizing", "grainy", "lumpy", "stiff")):
        return ("Chocolate seizes when even a drop of water gets in, and the fix is more water, "
                "not less: stir in a teaspoon of boiling water at a time, off the heat, until it "
                "goes smooth again. A tablespoon of warm cream does the same and leaves you with "
                "a ganache.")
    return ("Melt chocolate in a bowl over barely simmering water, with the bowl not touching the "
            "water, or in 20-second bursts in the microwave, stirring between them. Keep every "
            "spoon and bowl dry, because a drop of water makes it seize, and take it off while "
            "most of it is melted - the rest will go as you stir.")


_GRAIN_FOOD = ("fudge", "toffee", "caramel", "icing", "frosting", "buttercream", "fondant",
               "praline", "brittle", "tablet", "syrup", "candy", "custard")


_GRAIN_WORD = ("grainy", "gritty", "crystal", "crystals", "crystallised", "crystallized",
               "crystalised", "crystalized", "granular", "sandy", "crunchy", "grain")


def _grainy(memory, understood):
    """Sugar that has set with crystals in it: a fudge, a toffee, a caramel or an icing.

    The cause is the same in every one - sugar stirred once it is boiling, or a single crystal
    from the side of the pan getting back in - but the rescue is not, so it goes by the sweet in
    the line: an icing is sifted and beaten, a fudge is warmed with milk and beaten, and a caramel
    is melted back with a spoonful of water.
    """
    words = [str(word).lower() for word in (understood.get("words") or [])]

    def has(*names):
        return any(_same(word, name) for word in words for name in names)

    if has("icing", "frosting", "buttercream", "glaze", "fondant", "drizzle"):
        return ("Grainy icing is undissolved sugar: sift the icing sugar first, then add the "
                "liquid a teaspoon at a time, and if it is already made, beat in a spoonful of "
                "warm milk or a few drops of lemon juice and it goes smooth. Cold liquid and "
                "coarse sugar are what leave the grain, so warm the milk slightly next time and "
                "give it a full minute of beating.")
    if has("fudge", "tablet", "praline", "brittle", "candy"):
        return ("Grainy fudge has sugar crystals in it, which happens when it is stirred while it "
                "boils or a crust of sugar from the pan gets back in. Warm it very gently with two "
                "tablespoons of milk and beat it hard until it is smooth again, or press it out "
                "flat and call it tablet. Next time stir only until the sugar dissolves, then "
                "wipe the pan sides down with a wet pastry brush and leave it to 116C.")
    if has("custard", "creme", "anglaise"):
        # A grainy custard is curdled egg, not sugar, so the rescue is cold milk and a sieve
        return ("Grainy custard has curdled: the eggs got too hot too fast. Take it off the heat "
                "at once, whisk in a splash of cold milk to stop it cooking, then strain it "
                "through a sieve into a jug and it comes back smooth. Next time cook it over a "
                "low heat, stirring all the time, and take it off at about 82C or as soon as it "
                "coats the back of the spoon.")
    if has("toffee", "caramel"):
        return ("Grainy caramel or toffee has crystallised: add a tablespoon of water and warm it "
                "very gently without stirring until the crystals melt, then let it cool slowly. "
                "It crystallises when the sugar is stirred once it is boiling, or when one "
                "crystal from the side of the pan gets back in, so stir only until the sugar has "
                "dissolved and keep the sides of the pan wiped clean.")
    return ("Sugar that sets grainy has crystallised, from stirring once it boils or a crystal "
            "from the pan getting back in. Warm it gently with a tablespoon of water until it "
            "melts back, and next time stir only until the sugar dissolves, wipe the pan sides "
            "with a wet pastry brush, and add a spoonful of golden syrup or a squeeze of lemon "
            "at the start.")


_SUGAR_MAKING = ("caramel", "caramels", "toffee", "praline", "brittle", "fudge", "candy")


_SUGAR_TROUBLE = ("crystallise", "crystallised", "crystallising", "crystallize", "crystallized",
                  "crystallizing", "crystalise", "crystalised", "crystalize", "crystalized",
                  "crystals", "crystal", "grainy", "grain", "crust", "crusty", "seize", "seized")


def _soup(memory, understood):
    """Making soup, or making a soup that is already made taste of something."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(_same(word, want) for word in words
           for want in ("better", "flavour", "improve", "boring", "lifeless", "interesting")):
        return ("Add salt first, then a squeeze of lemon or a splash of vinegar: most dull soup is "
                "short of both, not of spice. After that something savoury - a stock cube, a spoon "
                "of miso, a parmesan rind or a knob of butter - and roast the vegetables next time "
                "rather than boiling them.")
    return ("Soften an onion and a carrot in butter with a pinch of salt, add whatever vegetables "
            "or pulses you have and enough stock to cover them, and simmer 20 minutes. Blend it "
            "smooth or leave it chunky, taste it, and finish with salt, pepper and a squeeze of "
            "lemon.")


def _flat(memory, understood):
    """A bake that stayed flat: pancakes, Yorkshire pudding, scones and muffins fail differently."""
    words = [str(word).lower() for word in (understood.get("words") or [])]

    def has(*wanted):
        return any(_same(word, want) for word in words for want in wanted)

    if has("pancake", "pancakes", "batter", "crepe", "crepes"):
        return ("Flat pancakes are usually old baking powder or a batter that was beaten too much: "
                "use a fresh tin, stir until it is just combined, and let the batter rest 10 "
                "minutes before it hits the pan. A properly hot pan matters too - the first one is "
                "always the test.")
    if has("yorkshire", "puddings"):
        return ("Yorkshire puddings want a smoking tin and cold batter: put a little oil in each "
                "hole, heat it in a 220C oven until it shimmers, pour the batter in and don't open "
                "the door for 20 minutes.")
    if has("scon", "scones"):
        return ("Flat scones come from handling: keep the butter cold, rub it in quickly, pat the "
                "dough out rather than rolling it hard, and cut straight down with a sharp cutter so "
                "the edges stay free to rise.")
    return ("Something that came out flat is short of rise, because the baking powder was past "
            "its date, the flour was beaten after it went in, or the oven was not up to heat. "
            "Check the baking powder is in date (about half a teaspoon to 100g of flour), stop "
            "beating once the flour is in, and let the oven come fully up to heat before the tin "
            "goes in.")


_FROM_FROZEN = ("from frozen", "cook it frozen", "cooked from frozen", "without defrosting",
                "without thawing", "no need to defrost", "skip the defrosting",
                "do i have to defrost", "have to defrost", "need to defrost")


# "how long do i have to defrost 500g of mince" carries "have to defrost" and asks for a time: the
# words are the same and the question is not. A timing ask stays a thaw question.
_FROZEN_TIME = ("how long", "how many hours", "how many days", "how many minutes", "overnight",
                "thaw time", "how long does it take", "what temperature", "what temp")


# The shapes that ask whether a thaw can be skipped. "need to defrost something for dinner" names
# nothing and asks nothing, so it is not this entry's line.
# A meal ask: "what can i cook/make from frozen" wants the meal, not the thaw rule.
_FROZEN_WHAT = ("what can i cook", "what can i make", "what can we cook", "what can we make",
                "what should i cook", "what should i make", "what to cook", "meal ideas",
                "what could i cook", "what could i make")


_FROZEN_ASK = ("can i", "could i", "may i", "is it", "should i", "do i", "how do i", "ok to",
               "okay to", "safe to", "fine to", "am i able", "any way to", "is there a way")


# The cuts this answers for, and the verb that goes with each: mince is broken up in the pan, the
# rest are turned. A whole bird or a joint is not in either list - it is too thick to cook through
# from frozen, so those lines keep the thaw times they already had.
_FROZEN_CUTS = (("mince", "beef mince", "lamb mince", "pork mince"), "break it up as it loosens")


# Each cut with the way it leads the sentence, and whether it is one thing: "Bacon can go straight
# into the pan ... cook it", "Chops can ... cook them". A fixed "them" read wrong for bacon, steak
# and liver, and a bare "Chop can go straight in" needed its article - a count noun said on its own
# is a fault in the first sentence of the reply.
_FROZEN_WHOLE = (("sausage", "A sausage", True), ("sausages", "Sausages", False),
                 ("bacon", "Bacon", True), ("chops", "Chops", False), ("chop", "A chop", True),
                 ("steak", "A steak", True), ("steaks", "Steaks", False),
                 ("liver", "Liver", True), ("kidneys", "Kidneys", False))


_FROZEN_ONE = ("{} can go straight into the pan from frozen: cook it a few minutes longer than you "
               "would thawed, turning it so it colours on all sides, and check it is piping hot in "
               "the middle.")


_FROZEN_MANY = ("{} can go straight into the pan from frozen: cook them a few minutes longer than "
                "you would thawed, turning so they colour on all sides, and check they are piping "
                "hot in the middle.")


def _frozen_from_the_bag(understood):
    """Whether the line is "can I cook it from frozen", which is not a question about thaw times.

    The meat is often named in the turn before ("i forgot to defrost the mince") rather than in
    this line, so the freezer words are a key part of the entry and the reply names the cuts that
    are safe and the ones that are not.
    """
    text = " ".join(str(understood.get("clean") or "").lower().split())
    if any(word in text for word in ("turkey", "joint", "whole bird", "roasting")):
        # a bird or a joint keeps its thaw time: it is the answer to "can i cook a turkey from
        # frozen" as much as to "how long does a turkey take"
        return False
    if not any(word in text for word in _FROM_FROZEN):
        return False
    if any(word in text for word in _FROZEN_WHAT):
        # "what can i cook from frozen" is a meal question, and the quick-meal answer it had is
        # better than a yes/no about meat. The entry answers "can i cook *it* from frozen".
        return False
    if any(word in text for word in _FROZEN_TIME):
        # "how long do i have to defrost 500g of mince" asks for a time, not for a yes
        return False
    if any(word in text for word in _FROZEN_ASK):
        return True
    # with no ask in the line, only the words that name the question itself carry it
    return any(word in text for word in ("from frozen", "cooked from frozen", "cook it frozen",
                                         "without defrosting", "without thawing",
                                         "no need to defrost", "skip the defrosting"))


def _turkey(memory, understood):
    """A turkey crown and a whole bird take different times, so they get different numbers.

    The weight in the line is the weight the timetable is worked out on: "how long do you cook
    a 4kg turkey" was given the example's figure - "a 5kg bird takes about 3 hours 10" - for a
    bird two pounds lighter, and the two numbers in one answer did not agree.
    """
    said = " ".join([str(word).lower() for word in (understood.get("words") or [])]
                    + [str(understood.get("text") or "").lower()])
    # a line about a crown is the crown's; a plain "how long does a turkey take" is the whole bird,
    # which is what people mean in December and what the crown numbers would undercook by an hour
    if "crown" not in said:
        kilos, weight_said = _bird_weight(understood) or (5.0, "5kg")
        return ("A whole turkey roasts at 180C (160C fan) for 20 minutes per kg plus 70 minutes: a "
                f"{weight_said} bird takes about {_in_words(20 * kilos + 70)}. Cook the stuffing in "
                "a separate tray, because a stuffed bird needs longer and the middle of the "
                "stuffing is the last thing to get hot. Check the thigh at the deepest point, not "
                "the breast, for 74C, and rest it 30 to 45 minutes under foil before carving.")
    return ("Roast a turkey crown at 180C (160C fan) for 20 minutes per 500g plus 20 minutes, until "
            "a thermometer in the thickest part reads 74C, then rest it 30 minutes under foil. Salt "
            "it the night before or push butter under the skin, and cover the top with foil if it "
            "browns too fast.")


def _cut_time(understood, per_kilo, extra, example):
    """The time for the weight the line names, or the worked example when it names none.

    People nearly always say the size - "how long do i cook a 3kg turkey breast" - so the
    timetable is worked out on their own weight rather than the example's.
    """
    weight = _bird_weight(understood)
    if not weight:
        return example
    kilos, said = weight
    return "so a %s one is about %s." % (said, _in_words(kilos * per_kilo + extra))


def _turkey_cut(memory, understood):
    """A turkey cut is not a whole bird: a breast is minutes, not the three hours a bird takes."""
    said = " ".join([str(word).lower() for word in (understood.get("words") or [])]
                    + [str(understood.get("text") or "").lower()])

    def has(*words):
        return any(word in said for word in words)

    # White meat is done at 74C; the dark cuts are better taken to 80C, so each cut carries its
    # own finish line rather than one sentence bolted on the end (a leg that says 80C and then
    # "take it to 74C" is telling a person two different things).
    done = "Take it to 74C in the thickest part and rest it 10 minutes under foil."
    dark = ("Take the thickest part to 80C, where dark meat goes tender rather than tight, and "
            "rest it 10 minutes under foil.")
    if has("spatchcock"):
        return ("A spatchcocked bird is flat, so it roasts fast and even: 200C (180C fan) at 20 "
                "minutes per kg, "
                + _cut_time(understood, 20, 0, "so a 4kg one is about 1 hour 20 minutes.")
                + " " + done)
    if has("wing", "wings"):
        return ("Turkey wings roast at 200C (180C fan) in 25 to 30 minutes, turned once, and they "
                "are done at 74C in the thickest part, so rest them 5 minutes under foil.")
    if has("drumstick", "drumsticks"):
        return ("Turkey drumsticks take 35 to 40 minutes at 200C (180C fan), turned once so the "
                "skin browns all over. " + dark)
    if has("leg", "legs"):
        return ("Turkey legs take 45 to 50 minutes at 190C (170C fan), skin side up, turned once. "
                + dark)
    if has("thigh", "thighs"):
        return ("Boneless turkey thighs take 40 to 45 minutes at 190C (170C fan); bone-in ones "
                "want 10 minutes more. " + dark)
    if has("fillet", "fillets", "steak", "steaks", "scallop", "scallops"):
        return ("Turkey fillets, steaks and escalopes are thin and quick: 20 to 25 minutes at "
                "190C (170C fan), or 8 to 10 minutes in a hot pan. They are done at 74C, so "
                "check one and rest them 5 minutes under foil.")
    # a breast, bone in or rolled: the last of the timetables, because every other cut is a
    # longer word that would also match this one
    boneless = has("boneless", "rolled", "butterflied", "flat")
    if boneless:
        return ("A boneless, rolled turkey breast wants 30 minutes per 500g at 190C (170C fan), "
                + _cut_time(understood, 60, 0, "so a 1.5kg one takes about 1 hour 30 minutes.")
                + " " + done)
    return ("A bone-in turkey breast takes 20 minutes per 500g plus 20 at 190C (170C fan), "
            + _cut_time(understood, 40, 20, "so a 2kg one is about 1 hour 40 minutes.")
            + " " + done)


def _hummus(memory, understood):
    """Hummus, and hummus when there is no tahini in the house."""
    said = " ".join([str(word).lower() for word in (understood.get("words") or [])]
                    + [str(understood.get("text") or "").lower()])
    no_tahini = ("no tahini" in said or "without tahini" in said or "tahini free" in said
                 or "tahini" in said and any(phrase in said for phrase in (
                     "dont have", "don't have", "ran out", "out of", "none", "substitute",
                     "instead of", "replace")))
    if no_tahini:
        return ("Without tahini, blitz the drained tin of chickpeas with the juice of a lemon, a "
                "small garlic clove, a good pinch of salt and 2 tablespoons of olive oil, then "
                "loosen it with iced water a spoon at a time. A spoon of yogurt or a second squeeze "
                "of lemon stands in for the richness the tahini would give.")
    return ("Blitz a drained tin of chickpeas with 2 tablespoons of tahini, the juice of a lemon, a "
            "small garlic clove and half a teaspoon of salt, then loosen it with iced water a spoon "
            "at a time - that is what makes it fluffy. A pinch of bicarbonate of soda in the pan "
            "softens the skins if you boil your own chickpeas.")


# A joint is three timetables, and a pork question must not open with "beef and lamb": the meat
# in the line picks the row, and a line that names none gets the rule that covers them all.
JOINT_BEEF = ("Beef or lamb: 20 minutes at 220C (200C fan) to brown it, then 190C (170C fan) for "
              "15 minutes a 500g for rare, 20 for medium and 25 for well done. The reliable check "
              "is a meat thermometer in the thickest part - 52C rare, 60C medium, 70C well done - "
              "and rest it 20 minutes under foil before carving.")


JOINT_PORK = ("Pork wants 30 minutes a 500g at 180C (160C fan), cooked right through with no pink "
              "in the middle, and crackling needs the oven at 220C (200C fan) for the first 25 "
              "minutes. A meat thermometer in the thickest part should read 70C, then rest the "
              "joint 20 minutes under foil before carving.")


# What turns a line about a joint into a line about keeping it.
GOING_OFF_ASK = ("go off", "goes off", "going off", "gone off", "went off", "shelf life",
                 "use by", "freezer", "fridge", "leftover", "leftovers")


KEEPING_VERB = ("keep", "keeps", "keeping", "kept", "last", "lasts", "freeze", "freezes")


# The words that make the line a line about cooking the joint, whatever it says about keeping it.
IN_THE_OVEN = ("oven", "roast", "roasting", "roasted", "cook", "cooks", "cooking", "cooked",
               "temperature", "gas mark", "how long do i", "how long should i")


def _roast_joint(memory, understood):
    """The joint the line names gets its own timetable first."""
    # A joint that is going off, or being kept, is a keeping question and not a roasting one:
    # "how long till ham goes off" got the 30-minutes-a-500g pork timetable. The same words
    # stand the roast-chicken row down, and the keeping tables answer with the days.
    line = " ".join(str((understood or {}).get("text") or "").lower().split())
    if any(phrase in line for phrase in GOING_OFF_ASK):
        return None
    # A bare keeping verb is not enough on its own: "how long should i keep a pork joint in the
    # oven" is the timetable that asks for, and standing the joint's row down handed it to the
    # red-meat allowance underneath (apt-scissors, #7891).
    if (any(phrase in line for phrase in KEEPING_VERB)
            and not any(word in line for word in IN_THE_OVEN)):
        return None
    words = [str(word).lower() for word in (understood.get("words") or [])]
    pork = ("pork", "pork joint", "leg of pork", "shoulder of pork", "loin of pork",
            "belly pork", "ham", "gammon")
    if any(_same(word, wanted) for word in words for wanted in ("pork", "gammon", "ham")):
        return JOINT_PORK
    if any(_same(word, wanted) for word in words for wanted in ("beef", "lamb", "mutton")):
        return JOINT_BEEF
    return JOINT_BEEF + " " + JOINT_PORK


# A keeping question about a food is the keeping tables' (bot/knowledge/keeping_cooked.py,
# cooking.py's own keep- rows), not how to cook it. "can i freeze cooked mince" was answered
# with how to brown a packet of it, because the food and the word "cook" in "cooked" were
# enough for the how-to row.
KEEPING_SENSE = ("freeze", "freezes", "freezer", "freezing", "frozen", "defrost", "defrosted",
                 "fridge", "refrigerate", "refrigerated", "reheat", "reheated", "reheating",
                 "refreeze", "keep", "keeps", "keeping", "kept", "last", "lasts", "storage",
                 "store", "stored", "storing", "leftover", "leftovers")


# A grainy sauce is the mince's question, not sugar's: "my bolognese came out grainy, not smooth"
# was a shrug, because the sugar row holds the word "grainy" and stands down on meat and pasta.
# Any mince dish goes, named the way people name it.
# "mincemeat" is not one: it is fruit and suet in a jar, with no browning and no pan juice, so
# "why is my mincemeat grainy" (a mince pie, more of it in December) was handed a confident and
# wrong cause by a word that reads like mince. A line that says mincemeat and meat together is a
# mince line, and the meat word is enough for it on its own.
_MINCE_GRAIN_DISH = ("bolognese", "bolognaise", "bol", "ragu", "ragout", "mince", "minced",
                     "chilli", "chili", "con carne", "lasagne", "lasagna",
                     "cottage pie", "shepherds pie", "shepherd's pie", "keema", "meat sauce",
                     "spag bol", "spaghetti bolognese", "taco", "tacos", "taco meat")


_MINCE_GRAIN_WORD = ("grainy", "gritty", "granular", "pellets", "grains")


# A named bolognese that went grainy already has a fuller answer of its own in dishes.py ("Grainy
# bolognese is the mince rather than the tomato ... a long bare simmer, a sieve"), so this row
# stands down for it and stays for the dishes dishes.py has no word for (a ragu, a chilli, a
# lasagne, a taco, a cottage pie). The one bolognese shape it keeps is "sauce": there the
# split-sauce row takes the line and offers cold cream, which is the wrong fault altogether.
_BOLOGNESE_WORDS = ("bolognese", "bolognaise", "spag bol", "spaghetti bolognese", "bol")


def _mince(memory, understood):
    """Browning mince, and why mince comes out tough, want different answers."""
    words = [str(word).lower() for word in (understood.get("words") or [])]
    if any(_same(word, sense) for word in words for sense in KEEPING_SENSE):
        return None  # a keeping question about mince belongs to the keeping rows
    if any(_same(word, tough) for word in words
           for tough in ("tough", "rubbery", "chewy", "dry")):
        return ("Minced meat goes tough and grainy when it is cooked too long or boiled in its own "
                "juice: brown it fast in a hot pan in batches, then add liquid only once it has "
                "coloured. A pinch of bicarb (half a teaspoon per 500g) keeps it soft in a long "
                "bolognese.")
    return ("Brown mince in batches over a high heat and don't stir it much: it should sizzle and "
            "colour, not steam. Pale, grey mince is mince that was crowded in the pan.")


# "no cheese", "without cheese", "i don't eat cheese", "allergic to nuts", "cheese free".
# The negator has to come from a short, explicit list of ways people refuse a food, so an
# ordinary "not sure about cheese" or "don't have much cheese" does not count.
FOOD = (r"(meat|chicken|beef|pork|lamb|mince|bacon|sausage|sausages|ham|turkey|fish|salmon|"
        r"cod|tuna|prawn|prawns|shellfish|crab|lobster|mussels|oysters|squid|clams|"
        r"dairy|milk|cheese|butter|cream|yoghurt|yogurt|egg|eggs|"
        r"nut|nuts|peanut|peanuts|gluten)")


def _said_so_far(understood, memory):
    """The line with the last few turns in front of it, oldest first.

    An exclusion given a turn or two ago still holds ("i'm vegetarian" then "what can I cook"),
    and the order matters: "im coeliac" then "im not coeliac" is a person taking it back, and only
    the later mention should count.
    """
    # The line as the engine read it, not as it was typed: a slip inside the asking word is
    # still the ask ("i need a recipie for shortbread" asks for the method), and every reader of
    # this text matches the words of it.
    line = line_as_read(understood)
    earlier = []
    turns = memory.get("turns")
    if isinstance(turns, list):
        earlier = [str(turn.get("user") or "") for turn in turns[-4:] if isinstance(turn, dict)]
    return " ".join(earlier + [line])


_PEOPLE_AFTER = r"(?:people|persons?|of us|of you|guests|adults|heads|folk|for dinner|for lunch)"


# The words for a count, as a pattern. Not "COUNT_WORDS": a table of that name further down is
# a dict, and the later binding wins for the whole module, so _head_count used to interpolate the
# dict's own text into its regexes and never match a number said in words - "a sunday roast for
# six people" lost its six, and the shopping list told ten people to buy for six.
_COUNT_WORD_SHAPES = "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"


_COUNT_VALUE = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


# A meatless roast is not a joint. "what do i need to buy for a nut roast" was told to buy 1.5kg
# of raw joint, which is the one thing the person is not buying, and the diet words above only
# catch a line that says "vegetarian" out loud. Naming the meatless roasts is the honest fix.
MEATLESS_ROAST = ("nut roast", "nutroast", "nut wellington", "nut loaf", "lentil roast",
                  "lentil loaf", "bean roast", "chickpea roast", "vegetable roast",
                  "vegetable wellington", "veg roast", "veggie roast", "tofu roast",
                  "tofu wellington", "seitan roast", "halloumi roast", "mushroom wellington",
                  "mushroom roast", "cauliflower roast", "beetroot roast", "vegan roast",
                  "vegetarian roast")


def _head_count(text):
    """The number of people a roast line says, or None when it only has a time in it.

    "my roast chicken needs 10 more minutes" is a timing line: reading its 10 as people is how a
    shopping list once told someone to buy 2.5kg of meat. A number only counts people when people
    are named beside it, or when it closes a "for N" phrase.
    """
    text = str(text or "").lower()
    when = (r"(?:on\s+\w+day|tonight|tomorrow|this weekend|next week|at the weekend|"
            r"this christmas|for christmas)")
    shapes = (rf"\bfor\s+(\d{{1,2}})\s*{_PEOPLE_AFTER}", rf"\bfor\s+({_COUNT_WORD_SHAPES})\s*{_PEOPLE_AFTER}",
              rf"\b(\d{{1,2}})\s*{_PEOPLE_AFTER}", rf"\b({_COUNT_WORD_SHAPES})\s*{_PEOPLE_AFTER}",
              rf"\bfor\s+(\d{{1,2}})\s*{when}", rf"\bfor\s+({_COUNT_WORD_SHAPES})\s*{when}",
              rf"\bfor\s+(\d{{1,2}})\s*(?=[,.!?]|$)", rf"\bfor\s+({_COUNT_WORD_SHAPES})\s*(?=[,.!?]|$)",
              # "we are 9 for christmas dinner" says how many are coming
              rf"\bwe(?:'re| are)\s+(\d{{1,2}})\b", rf"\bwe(?:'re| are)\s+({_COUNT_WORD_SHAPES})\b")
    for shape in shapes:
        found = re.search(shape, text)
        if not found:
            continue
        value = found.group(1)
        number = int(value) if value.isdigit() else _COUNT_VALUE.get(value)
        if number and 2 <= number <= 20:
            return number
    return None


def _roast_shopping(memory, understood):
    """A shopping list for a roast dinner, sized by the people in the line.

    "what do i need to buy for a sunday roast" was a shrug: the dish words were there and the
    buying word was there, but nothing joined them. The amount is the useful half, and it depends
    on what is being roasted, so a bird gets a bird's amount and never the word "joint".
    """
    text = str(understood.get("clean") or understood.get("text") or "").lower()
    people = _head_count(text)
    trimmings = ("potatoes, carrots, parsnips or swede, and something green like cabbage or "
                 "sprouts, plus oil, and stock and flour for the gravy")
    if "turkey" in text or "christmas dinner" in text or "xmas dinner" in text:
        per, bird, timing = BIRD_GRAMS, "turkey", "20 minutes per 500g plus 90"
        if people:
            body = (f"About {people * per / 1000:g}kg of turkey for {people}, at {per}g a person "
                    f"on the bone")
        else:
            body = ("Most people do turkey: about 500g a person on the bone, so a 4kg bird feeds "
                    "eight")
    elif "chicken" in text:
        # A bird feeds people on the bone, and units.BIRD_GRAMS is where the bot keeps that
        # number: 500g a person, so the same chicken asked in three ways gets one amount.
        per, bird, timing = BIRD_GRAMS, "chicken", "20 minutes per 500g plus 20"
        if people:
            body = (f"About {people * per / 1000:g}kg of chicken for {people}, at {per}g a person "
                    f"on the bone")
        else:
            body = (f"About {per}g of chicken a person on the bone, so a 3kg bird feeds six and a "
                    "1.5kg one feeds three")
    else:
        per, bird = 250, ""
        timing = "20 minutes per 500g plus 20"
        if people:
            body = (f"About {people * per / 1000:g}kg of raw joint for {people}, which is 250g a "
                    f"person")
        else:
            body = "For a roast: about 250g of raw joint a person, so 1.5kg feeds six"
    text_out = (f"{body}. Then {trimmings}. For timing, work on {timing} at 200C (180C fan), and "
                "rest it 15 minutes before carving.")
    if not bird:
        text_out += (" Add flour, eggs and milk for Yorkshire puddings, and mint or apple sauce if "
                     "it is lamb or pork.")
    return text_out


# A lactose intolerance is about how much milk sugar is in the portion, so it is not the same
# plate as a dairy allergy or a vegan diet: the words that say it, and the words that say one of
# those instead (which keep the dairy ban as it is).
_LACTOSE_WORDS = ("lactose", "milk sugar", "lactase")


_NOT_LACTOSE_WORDS = ("vegan", "dairy free", "dairy-free", "no dairy", "allergic", "allergy",
                      "anaphyla", "milk protein", "cut out dairy", "give up dairy", "avoid dairy")


def _a_lactose_intolerance(said):
    """True when the words say a lactose intolerance and nothing that is a dairy allergy."""
    if not any(word in said for word in _LACTOSE_WORDS):
        return False
    plain = said.replace("\u2019", "'")
    return not any(word in plain for word in _NOT_LACTOSE_WORDS)


def _record_says_lactose(known):
    """True when one person's record says a lactose intolerance and nothing stronger."""
    if not isinstance(known, dict):
        return False
    said = []
    for key in ("allergies", "diet", "diets", "condition", "conditions"):
        value = known.get(key)
        if isinstance(value, str):
            said.append(value)
        elif isinstance(value, (list, tuple, set)):
            said.extend(str(one) for one in value)
    return _a_lactose_intolerance(" ".join(said).lower().replace("-", " "))


def _their_diet_is_a_lactose_intolerance(memory):
    """True when what the store keeps about this person says a lactose intolerance.

    "my husband is lactose intolerant" then "what can he have" is the same question a turn later,
    and the line itself no longer says the words.
    """
    if not isinstance(memory, dict):
        return False
    known = None
    try:
        import bot.modules.memory_store as _store
        known = _store.user(memory) or {}
    except Exception:
        known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    return _record_says_lactose(known)


def _list_words(text, backwards=False):
    if backwards:
        return list(reversed(re.findall(r"[a-z']+|[&+,]", str(text or "").lower())))
    return re.findall(r"[a-z']+|[&+,]", str(text or "").lower())


# "i don't eat meat" is the ban people mean differently, and neither a no nor a yes about fish
# is honest: the answer names the split, so a person who does eat fish is not told they cannot.
FISH_SPLIT = ("Fish is the one people mean differently - if you do not eat it either, chickpeas, "
              "lentils or tofu fill the same gap.")


def _the_guest(memory, text):
    """The record of the person the line is about, when the store keeps one, or None.

    A named relation is the guest it names ("can my wife eat pesto" is the wife's record). A line
    that only points with a pronoun means the one guest on record: with two of them there is no
    way to tell which one is meant, and a guess about an allergy is the one guess not worth
    making.
    """
    others = memory.get("others") if isinstance(memory, dict) else None
    if not isinstance(others, list) or not others:
        return None
    low = " ".join(str(text or "").lower().split())
    named = [other for other in others
             if isinstance(other, dict) and other.get("who")
             and re.search(r"\b" + re.escape(str(other["who"]).lower()) + r"\b", low)]
    if len(named) == 1:
        return named[0]
    if named:
        return None
    return others[0] if len(others) == 1 and isinstance(others[0], dict) else None


# A yes about a plain food is a claim about the food's own recipe, and a few foods are not
# settled by their recipe: an oat has no gluten in it, but oats are grown and milled next to
# wheat, so ordinary porridge oats are not safe for a coeliac. This file's own gluten-free card
# already says "porridge made with gluten free oats", so "im gluten free / can i have porridge"
# answering "porridge has no gluten in it, so it is fine for you" contradicted it in the next
# turn. The packet is what settles these, and the answer says so.
NOT_SETTLED_BY_THE_RECIPE = {
    "oats": ("With the right packet: an oat has no gluten in it, but oats are grown and milled "
             "next to wheat, so ordinary porridge oats are not safe for a coeliac. The ones "
             "marked gluten free are, and they cost about the same."),
    "porridge": ("With the right packet: an oat has no gluten in it, but oats are grown and "
                 "milled next to wheat, so ordinary porridge oats are not safe for a coeliac. "
                 "The ones marked gluten free are, and they cost about the same."),
    "oatmeal": ("With the right packet: an oat has no gluten in it, but oats are grown and "
                "milled next to wheat, so ordinary porridge oats are not safe for a coeliac. "
                "The ones marked gluten free are, and they cost about the same."),
}
