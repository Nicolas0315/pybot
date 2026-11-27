"""Rows 10 of 10 of `home_craft.entries()`: `wash-at-30` .. `a-nail-in-a-wall`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _a_nail_in_the_wall,
    _a_wash_is_named,
    _the_wood_and_the_nail,
)


def rows():
    from ..knowledge.home import (
        _BATH_CITY, _asks_the_ceiling_colour, _bath_length, _chemical_safety, _colour_advice,
        _small_appliance_not_heating, entry
    )
    return [
        # Cats in a garden: nobody's table answered it, so the line was a shrug.
        # "is it cheaper to wash at 30" was "I don't know enough to answer that honestly" on main,
        # though the cost table further up this file holds the numbers.
        # This is the COST question only. The dial itself - "what temperature should i wash at",
        # "is 30 degrees enough" - is #3821's entry, so the second group holds cost words and nothing
        # else; "better", "enough" and "temperature" used to be here and took those lines, and also
        # "is it better to wash at night or morning", which is not even a laundry question.
        # The reply must not open with "Yes:": it catches cost questions of every shape, and "how much
        # does a wash cost" is not a yes/no.
        # Anything that names something other than laundry - a car, a dog, a window - is not this.
        entry("wash-at-30",
              (("30", "30c", "30 c", "30 degrees", "thirty", "20c", "40", "40c", "40 degrees",
                "wash", "washing", "laundry", "wash cycle"),
               ("cheaper", "cheap", "cost", "costs", "save", "saves", "saving", "worth",
                "money", "bill", "bills", "pence", "expensive", "add up")),
              "About 15p a wash at 30C in electricity, against 25p at 40C: heating the water is most "
              "of what a wash costs, so 30C is the cheapest cycle that still cleans everyday clothes, "
              "shirts and jeans properly with a modern detergent. Go to 40C for heavily soiled work "
              "clothes and 60C for towels, bedding and anything with a stomach bug or a cold, because "
              "that is about killing germs rather than shifting dirt. A cold or 20C cycle saves a few "
              "pence more but struggles with grease.",
              # "how much should i have in savings at 40" was this row's: "40" is one of its
              # temperatures and "savings" folds to "saving". The money words stand it down.
              avoid=("savings", "in savings", "have saved", "i have saved", "how much saved",
                     "by 40", "at 40", "by 50", "at 50", "by 60", "at 60", "pension", "pensions",
                     "retire", "retirement", "salary", "income", "put by", "put aside",
                     "how much should i have", "by now", "at my age",
                     # an age is not a temperature: "is it worth going to university at 30" was
                     # answered with the cost of a 30C wash
                     "university", "uni", "degree", "college", "college course", "a level",
                     "gcse", "apprenticeship", "masters", "phd", "exam", "exams",
                     "car", "cars", "van", "bike", "bicycle", "motorbike", "vehicle", "car wash",
                     "jet wash", "driveway", "patio", "bin", "bins", "wheelie", "dog", "dogs",
                     "puppy", "cat", "horse", "hair", "face", "hands", "shower", "bath", "window",
                     "windows", "brush", "brushes", "paint", "dishwasher", "dishes", "washing up",
                     "washing-up", "machine not", "not draining", "wont drain", "won't drain",
                     "smell", "smells", "mould", "mold", "drain", "hose", "filter", "wool",
                     "woollen", "woolen", "silk", "cashmere", "dry clean", "dryer", "tumble",
                     "iron", "stain", "stains", "shrink", "shrunk", "bleach", "whites", "darks",
                     # the towels and bedding answer names 60C and is the better one for those lines,
                     # so "what temperature should i wash towels at" must not land here
                     "towel", "towels", "bedding", "sheets", "sheet", "linen", "pillow", "pillows",
                     "duvet", "nappy", "nappies", "gym kit", "sports kit", "dishcloth", "tea towel",
                     "flannel", "blanket", "throws", "curtains", "mop",
                     # The key holds the bare digits "30" and "40" beside the money words, and a
                     # journey is said the same way: "the money one is 40 mins further" is a job
                     # choice, and it was answered with this card. A time or a distance in the line
                     # is the other question, so those words stand this row down - the same shape
                     # as "car" and "dishwasher" above, not a new mechanism.
                     "mins", "minute", "minutes", "miles", "further", "journey", "commute",
                     "commuting", "travel", "travelling"),
              # The key holds the bare figures "30" and "40", and a figure on its own is what a
              # bill, a battery or a bus fare is said with: with "month" no longer read as a when,
              # "my phone bill is 30 a month" and "button battery 30 a month" were both answered
              # with what a wash costs to run. A temperature is only the subject of a line that is
              # already about washing, so the row asks for the wash first. The same shape as the
              # "car" and "dishwasher" words above: a row standing aside for the other question.
              guard=_a_wash_is_named),
        entry("cats-garden", (("cat", "cats", "kitten", "kittens", "neighbours cat", "neighbour's cat"),
                              # The garden words and the ask words are two parts, not one. With the
                              # ask in with the nouns, a cat and "stop" were enough: "how do i stop my
                              # cat knocking the cups off" and "how do i stop my cat getting on the
                              # counters" were level with the right entry and won the tie on registry
                              # order, and both got soil and citrus peel. A garden noun is now
                              # required, and "how do i stop cats pooing in my flowerbed" still finds
                              # it.
                              ("garden", "gardens", "lawn", "flowerbed", "flower bed", "flowerbeds",
                               "borders", "vegetable patch", "sandpit", "poo", "poos", "pooing",
                               "toilet", "dig", "digging", "seedlings")),
              "Cats dig in bare, dry soil, so the reliable fix is to take that away: mulch the beds, lay "
              "chicken wire just under the surface, or plant through a membrane. Citrus peel, coffee "
              "grounds and a scattering of holly leaves or pine cones make the surface unpleasant, and a "
              "water pistol or a motion-triggered sprinkler teaches one cat to go elsewhere fast - "
              "renew it after rain, because scents fade.",
              # the cat's own behaviour is the pet answer's: scratching the sofa, the litter tray,
              # spraying indoors
              # "toilet" stays a key word here: a cat using a flowerbed as a toilet is the question
              avoid=("litter", "litter tray", "toilet training", "my cat is", "my cat wont",
                     "my cat won't", "pregnant", "fleas", "worms", "scratch", "scratching",
                     # A cat that wakes you is a sleep question, not a flowerbed one: "how do i
                     # stop my cat waking me up at 5am" reached this answer on cat + stop alone.
                     # The guard is the waking phrase, so a garden line that happens to say
                     # "stop" still keeps its soil answer.
                     "waking me", "wakes me", "woke me", "woken me", "wake me up", "waking us",
                     "wakes us", "woke us", "waking the baby", "waking my baby", "waking my partner",
                     "waking my husband", "waking my wife", "waking my child", "waking my kids",
                     "keeping me awake", "keeps me awake", "kept me awake", "keeping us awake",
                     "keeps us awake",
                     # a cat that bites or nips a hand is not a cat in the beds: "how do i stop my
                     # cat biting" keyed on cat + stop and got this answer
                     # A bed in a house is where a cat sleeps, and "beds" in this key turned
                     # "my cat sleeps on my bed" into soil advice. The singular is not in the key at
                     # all now, and the sleep words are a guard on the garden plural as well, so a
                     # cat asleep in a flower bed is not a cat digging in it.
                     "sleeps on my bed", "sleeping on my bed", "sleeps in my bed",
                     "sleeping in my bed", "sleeps on the bed", "sleeping on the bed",
                     "sleeps on our bed", "sleeping on our bed", "sleeps with me", "in bed with me",
                     "my pillow", "duvet", "bedroom",
                     # An accident indoors is not a flowerbed, and "poo" is a garden noun in this
                     # key, so "my cat pooed on the bed" was answered with mulch and chicken wire.
                     # A soft thing or a room in the line stands this row down and the pet answer
                     # takes it; a real garden line names the garden, the lawn or the beds.
                     "on the bed", "on my bed", "on our bed", "in the bed", "in my bed",
                     "on the carpet", "on the rug", "on the sofa", "on the settee", "on the couch",
                     "on the floor", "on the mat", "indoors", "in the house", "in the hall",
                     "in the kitchen", "in the bathroom", "in the bath", "litter",
                     "bite", "bites", "biting", "bit", "bit me", "nip", "nips", "nipping",
                     "scratches", "sofa", "couch", "furniture", "curtains", "spraying", "spray",
                     # What a cat carries in is hunting, and that is the pet answer's: with only
                     # "cat" and "stop" needed to reach this one, "my cat keeps leaving dead mice in
                     # my bed, how do i stop it" was a soil-and-citrus answer. A poo-or-digging
                     # line never names the animal it caught.
                     "mouse", "mice", "rat", "rats", "vole", "voles", "prey", "dead", "bird",
                     "birds", "pigeon", "pigeons", "brought", "brings", "bringing", "caught",
                     "dragged", "drops off")),
        # "how do i choose a paint colour" names no colour, so the table cannot answer it: the rule
        # is the answer, and it is its own entry because the pair words are not in the line at all.
        entry("colour-choice",
              (("colour", "colours", "color", "colors", "palette", "scheme"),
               ("choose", "choosing", "pick", "picking", "decide", "deciding", "help me", "stuck",
                "no idea", "go for", "paint", "room", "rooms", "hall", "hallway", "walls",
                "bedroom", "kitchen", "lounge", "living room",
                # "which colour for a small bathroom" was a shrug: a room this row answers for had
                # no word in its own key
                "bathroom", "bathrooms", "nursery")),
              ("Pick the thing you cannot change - the floor, the tiles, the worktop, the sofa - and "
               "take the wall "
               "colour out of it in a paler version of itself. Then add one deeper tone from the same "
               "family for a rug or cushions and a wood or a metal to warm it: three colours, one of "
               "them a near-neutral. Paint a sample patch you can watch in the morning and again under "
               "the lamp before you buy a tin, because a colour on a small card lies."),
              # a bare "what colour" or "which" is in every colour fact question - "what colour is
              # the sky" - so the gate is a choosing word, not the shape of the question.
              ask=("choose", "choosing", "pick", "picking", "decide", "deciding", "help me", "stuck",
                   "no idea", "how do i go for", "what colour should i paint",
                   "which colour should i paint",
                   # the same question without an "i": "what colour to paint a small room" and
                   # "what colour walls for a dark room" call the same row as "what colour should i
                   # paint my kitchen", and both were a shrug. Still no bare "what colour", so
                   # "what colour is the sky" stays out of a decorating answer.
                   "what colour to", "what colour for", "what colour walls", "what colour goes",
                   "colour to paint", "which paint", "which white", "colour for a room",
                   "colour for my",
                   # "which colour for the living room walls" names its choosing word as "which"
                   # and its room in the second half, and no gate above carries that shape
                   "which colour for", "which color for",
                   # the advice-shaped questions put "good", "best" or "neutral" where the choosing
                   # word normally sits, so the key matched and the gate alone said no: "what is a
                   # good neutral paint colour" was a punt with the answer one word away
                   "neutral", "good colour", "good paint", "best colour", "best paint",
                   "what paint colour", "what colour paint", "paint colour for"),
                   # ("paint colour" is left out on purpose: as a gate it also caught the follow-up
                   # "and what about the hallway", and the lead-in that names the new room turned
                   # into "Same as before". "which paint" covers "which paint colour for a room".)
              # a named colour is the table's question, and a spilled or peeling paint job is the
              # painting entry's
              avoid=("blue", "navy", "grey", "gray", "green", "sage", "teal", "black", "brown",
                     "beige", "cream", "white", "yellow", "mustard", "pink", "red", "terracotta",
                     "purple", "orange", "silver", "charcoal", "gold", "peel", "peeling", "bubbling",
                     "stain", "tin", "tins", "brush", "roller", "how do i paint", "spill", "spilled",
                     # a ceiling is its own colour question (see ceiling-colour below): "what colour
                     # should i paint the ceiling" got the floor-tiles-sofa palette for a whole room
                     "ceiling", "ceilings")),
        # A ceiling is not a wall. The palette rule above picks three colours for a room you look at
        # from the door, and it has nothing to say about the one surface over your head that decides
        # how much light comes back into the room.
        entry("ceiling-colour",
              (("ceiling", "ceilings"),
               ("colour", "color", "paint", "painting", "white", "which", "what colour",
                "what color")),
              "Matt white, or the palest tint of the wall colour, and one shade lighter than the walls "
              "if you want a tint at all: a ceiling painted as deep as the walls comes down on you and "
              "makes a small room feel lower. White bounces light back into the room, which is why a "
              "dark hallway or a north-facing room looks better with a warm white than a cool one, "
              "and a sunlit south room can take a cool white. In a kitchen or a bathroom use a "
              "moisture-resistant matt emulsion, because ordinary emulsion flakes over the steamy "
              "half of the room. Two coats of matt, rolled on a pole in strips, and paint the ceiling "
              "before the walls.",
              # a stain, a leak or a crack in the ceiling is its own answer in this file
              avoid=("stain", "stains", "leak", "leaking", "damp", "mould", "mold", "crack",
                     "cracks", "cracked", "peel", "peeling", "flake", "flaking", "spot", "spots",
                     "water", "fan", "fans", "light", "lights", "bulb", "insulation", "height"),
              guard=_asks_the_ceiling_colour,
              bias=1),
        # The whole colour family: what goes with a named colour, whether two colours work, and the
        # rule when the line names none. The colour is data in COLOUR_PARTNERS, so one row adds one.
        entry("colour-pairing",
              (("colour", "colours", "color", "colors", "goes with", "go with", "go together",
                "match", "matches", "matching", "pairs with", "pair with", "compliment", "scheme",
                "together", "clash", "clashes"),
               # the colour names are the second half of the key: "what goes with blue" needs one, and
               # "what colour should i paint the hall" is caught by the words above instead
               ("blue", "navy", "grey", "gray", "green", "sage", "teal", "black", "brown", "beige",
                "cream", "white", "yellow", "mustard", "pink", "red", "terracotta", "purple",
                "orange", "silver", "charcoal", "gold")),
              _colour_advice,
              # a how-to about painting, a tin of paint, tie-dye and a phone case's colour are not
              # this question; the paint it entry and the technology entries answer those.
              # Three neighbours already have their own answers and must keep them: a colour question
              # about food, about clothes, and about a fact ("what colour is the sky"). The words
              # below are the ones those lines use, not the room's.
              avoid=("paint brush", "paintbrush", "roller", "undercoat", "primer", "emulsion",
                     "dulux", "farrow", "tin", "tins", "stain", "mould", "peel", "peeling",
                     "bubbling", "screen", "phone", "nail varnish", "hair dye", "dye",
                     "how do i paint", "how to paint",
                     # food and drink
                     "salad", "plate", "plateful", "cheese", "recipe", "sauce", "cook", "cooking",
                     "eat", "eating", "food", "bread", "dish", "meal", "menu", "cake", "icing",
                     "curry", "pasta", "wine", "cocktail", "smoothie", "cocktail",
                     # clothes and how a person looks
                     "tie", "suit me", "suits me", "a suit", "grey suit", "navy suit", "black suit",
                     "blue suit", "suit jacket", "suit and tie", "dress", "outfit", "shoes", "boots",
                     "shirt", "jacket", "coat", "chinos", "trousers", "skirt", "jumper", "to wear",
                     "wearing", "what colours suit", "what colors suit", "what colour suits",
                     "what colour should i wear"),
              bias=1),
        entry("shower-goes-cold",
              (("shower", "showers", "shower head"),
               ("goes cold", "gone cold", "runs cold", "turns cold", "going cold", "cold after",
                "cold quickly", "not hot", "warm then cold", "hot then cold", "cuts out", "heat up",
                "hot water runs out", "boiler",
                # "my shower is cold" and "the electric shower is cold" name no moment and no
                # boiler, and they were getting an echo or a chat question back
                "is cold", "is lukewarm", "stays cold", "never hot", "never gets hot",
                "wont get hot", "won't get hot", "not getting hot", "runs lukewarm",
                "goes lukewarm", "is freezing", "water is cold", "runs hot")),
              "A shower that goes cold after a few minutes is usually the hot water, not the shower: "
              "a combi boiler only heats what you draw, so check whether the hot tap is still hot. If "
              "the tap is fine, the shower valve is scaled or failing, and cleaning the head in "
              "vinegar is the first free test. If the tap runs cold too, look at the boiler: its "
              "pressure gauge wants 1 to 1.5 bar while cold, and its fault code when it cuts out says "
              "what it is unhappy about.",
              ask=("cold", "hot", "cuts", "heat", "boiler", "gone", "goes", "runs", "turns",
                   "lukewarm", "freezing", "warm", "stays", "never"),
              # a shower that will not get hot at all, a shower that leaks and a shower going mouldy
              # are three other answers
              avoid=("mould", "mold", "leak", "leaking", "drip", "dripping", "smell", "drain",
                     "blocked", "pressure", "weak", "install", "fit a", "buy", "replace")),
        entry("stripped-screw",
              (("screw", "screws", "screw head", "screwdriver", "bolt", "nut"),
               ("stripped", "rounded", "rounded off", "wont come out", "won't come out",
                "stuck", "seized", "sheared", "chewed", "no grip", "spinning", "removed",
                "remove", "undo", "loosen", "stuck screw",
                # "i cant get this screw out" names the job and no state of the screw at all
                "get this screw out", "get the screw out", "get it out", "cant get")),
              "Once the cross is rounded there is no grip, so give it grip or give it something else "
              "to hold: press a wide rubber band or a steel-wool pad into the head and turn slowly "
              "with real downward force, or tap a slightly larger Torx or Phillips bit in with a "
              "hammer for a bite. If the head stands proud, cut a slot with a hacksaw and use a flat "
              "blade. Last resorts are pliers on the head, or drilling it out and using a screw "
              "extractor.",
              ask=("stripped", "rounded", "stuck", "seized", "chewed", "remove", "undo", "out"),
              bias=1,
              # putting a shelf up, a wall plug and a door hinge are other jobs
              avoid=("shelf", "wall plug", "raw plug", "rawlplug", "plasterboard", "stud", "hinge",
                     "drill bit", "anchor")),
        # --- the ordinary machine faults people describe by the noise ------------
        entry("small-appliance-not-heating",
              (("microwave", "microwaves", "microwave oven", "kettle", "kettles", "toaster",
                "toasters", "sandwich toaster"),
               ("not heating", "not heating up", "isnt heating", "isn't heating", "isnt heating up",
                "isn't heating up", "wont heat", "won't heat", "wont heat up", "won't heat up",
                "doesnt heat", "doesn't heat", "doesnt get hot", "stays cold", "stays cold food",
                "food stays cold", "food is cold", "cold food", "no heat", "not getting hot",
                "stopped heating", "heats nothing", "wont warm", "won't warm", "not warm",
                "cold in the middle", "lukewarm", "takes ages", "stone cold")),
              _small_appliance_not_heating,
              # "heating" and "heat" are the verb here and the noun in a hundred other lines, so the
              # row needs the appliance word as well as the fault words, and it stands aside for
              # every appliance that already has its own answer: the oven, the hob, the iron, the
              # tumble dryer, the air fryer and the boiler all have one, and a radiator that will not
              # heat is the plumbing question.
              avoid=("oven", "ovens", "cooker", "hob", "ring", "iron", "irons", "dryer",
                     "tumble dryer", "air fryer", "airfryer", "air-fryer", "boiler", "radiator",
                     "radiators", "immersion", "water", "shower",
                     # a microwave that sparks or smokes is the fire card, and the metal question has
                     # its own answer: neither is a repair question
                     "spark", "sparks", "sparking", "sparked", "smoke", "smokes", "smoking",
                     "flames", "caught fire", "on fire", "smell", "smells", "burning",
                     "metal", "foil", "tinfoil", "tin foil", "cutlery", "fork", "forks",
                     # cleaning is a different answer, and so is how it works
                     "clean", "cleaning", "descale", "limescale", "scale", "furred", "furring",
                     "noisy", "noise", "loud", "rattling", "humming",
                     # a thank-you that mentions the machine is not a fault
                     "thanks", "thank you", "worked", "sorted", "perfect", "glad", "helped",
                     # and the deciding question is the money rule's, not this one's
                     "worth replacing", "worth fixing", "worth repairing", "fix or replace",
                     "cheaper to buy", "should i buy", "which one", "best"),
              # "my kettle isnt heating up" ties this row with the general fault card and with the
              # money rule at five, and a tie is file order - so the appliance's own answer needs the
              # say-so to be the one the person gets.
              bias=1,
              # The answer is about the appliance, so it is the reply a line saying the appliance has
              # gone still gets: without this the line was read as one that needs a working machine.
              fault=True),
        # An oven that bakes one half of the tray and leaves the other pale is not the same fault
        # as an oven that will not heat: "my oven cooks unevenly" was answered with the element
        # test and an engineer, where the person wanted the shelf, the gap round the tin and the
        # thermometer. It comes before the not-heating row so the tie on "oven" goes to the
        # uneven bake.
        entry("oven-bakes-unevenly",
              (("oven", "cooker", "fan oven", "fan"),
               ("uneven", "unevenly", "cooks unevenly", "one side", "one half", "in patches",
                "patchy", "browns unevenly", "burns on one side", "burns on the top",
                "burns at the back", "takes longer", "front of",
                # the bottom catching is the same uneven bake, read from the other side
                "burn the bottom", "burns the bottom", "burning the bottom", "burns on the bottom",
                "burns underneath", "bottom burns", "burnt bottom", "burned bottom",
                "burns the base", "soggy bottom")),
              "Fill the middle of the shelf, not the edges: a fan oven runs hottest near the door "
              "and the sides, so keep tins in the middle third with a gap of two fingers between "
              "them, and turn the tray round halfway through. Give it 15 minutes to preheat and "
              "check the dial with a cheap oven thermometer - most ovens are out by 10 to 20C, and "
              "an oven that reads 20C low browns the back before the front. If it is always the "
              "bottom that catches, the tin is too low or it is a dark one: move it up a shelf, "
              "use a lighter tin and drop the heat 10C. If the same side is always pale while the "
              "other catches, that is the element or the fan, not your baking.",
              avoid=("not heating", "not heating up", "isnt heating", "isn't heating", "not hot",
                     "wont heat up", "won't heat up", "gas", "smell", "smells", "clean",
                     "cleaning", "oven chips", "recipe", "how long", "what temperature",
                     "gas mark", "turkey", "roast"),
              fault=True),
        entry("oven-not-heating",
              (("oven", "cooker"),
               ("not heating", "not heating up", "not hot", "not getting hot", "isnt heating",
                "isn't heating", "takes ages", "slow to heat", "cold", "warm up", "not warming",
                "temperature", "thermostat", "element", "uneven", "unevenly", "isnt getting hot",
                "isnt hot", "wont heat up", "won't heat up")),
              "On an electric oven the heating element is almost always the fault, and it fails in the "
              "way you can see: heat the oven for ten minutes in the dark and look for the element to "
              "glow red - a dull patch or a cold half is a broken element, about £20 to £40 for the part "
              "and £60 to £90 for an engineer. A fan oven that runs cold is often the fan motor or the "
              "thermostat instead. Turn the power off at the wall before you touch anything, and a gas "
              "oven that will not light is a gas-safe job, not a DIY one.",
              avoid=("fan oven", "roast", "roasting", "bake", "baking", "bread", "cake", "chicken",
                     "pizza", "chips", "recipe", "how long", "minutes", "turkey", "yorkshire",
                     "temperature for", "what temperature", "gas mark",
                     # a thank-you that mentions the oven is not a fault: "thanks, the oven
                     # temperature was perfect" was getting the element diagnosis
                     "thanks", "thank you", "perfect", "worked", "sorted", "glad", "helped",
                     "delicious", "came out", "was lovely", "brilliant", "spot on"),
              # The answer is about the oven, so it is the one reply a line saying the oven has
              # gone still gets: "my oven wont heat up" was read as a kitchen with no oven and the
              # element answer was thrown away as one that needs an oven.
              fault=True),
        entry("weak-flow",
              # A weak flow and a slow flow are two faults: one is at the outlet, the other is the
              # wait for the boiler, so the flow entry is checked first and only when the line says
              # the water is not strong. A shower is left to the shower entry (#1148): the same line
              # answered twice would be two entries for one meaning, and a shower has its own first
              # moves (the head, the hose, the mixer).
              (("tap", "taps", "mixer", "hot water", "cold water"),
               ("pressure", "low pressure", "weak", "dribble", "dribbles", "trickle", "low flow",
                "not strong", "losing pressure")),
              "A weak flow is almost always at the outlet, not in the boiler: unscrew the tap nozzle "
              "and soak it in descaler, open the isolator under the sink all the way, and check the "
              "stopcock has not been half shut. A combi only gives full flow at one tap at a time, so "
              "if the pressure drops when a second tap runs that is normal. If it is weak on every tap "
              "in the house, the stopcock or the mains is the place to look, not the plumbing.",
              bias=1,
              avoid=("bar", "gauge", "boiler pressure", "dropping", "radiators", "heating",
                     "shower", "showers", "showerhead", "shower head", "electric shower",
                     "power shower")),
        entry("hot-water-slow",
              # Not every cold shower is a slow pipe: a shower that runs cold or lukewarm is the
              # boiler, the mixer or the immersion, so only waiting-time words open this answer.
              (("hot water", "tap", "shower"),
               ("takes ages", "slow", "slowly", "come through", "waiting", "hot then cold")),
              "On a combi boiler, about 20 to 30 seconds is normal: you are waiting for the boiler to "
              "fire and for the hot water to travel down the pipe from it. If it is minutes, or the "
              "water runs hot then cold, the plate heat exchanger is scaled (a typical 5 to 10 year "
              "service item) or the boiler is undersized for two taps at once. If the flow is weak as "
              "well, check the isolator under the sink is fully open and unscrew the tap nozzle to "
              "clear the scale.",
              # a boiler losing pressure is its own answer; a weak shower or tap is this one
              avoid=("dropping", "bar", "gauge", "radiator", "radiators")),
        entry("floor-gone-dull",
              (("floor", "flooring", "floorboards"),
               ("dull", "dullness", "shiny", "shine", "worn", "wear", "scratched", "grey", "greyish",
                "tired", "restore", "polish")),
              "A dull wooden floor has worn through its finish, not its wood, so clean it with a "
              "diluted wood floor soap rather than a polish or a steam mop, then put a maintenance coat "
              "of the same hard wax oil or lacquer back on - one coat on the traffic lanes every year or "
              "two. Sanding is only for deep scratches; a whole-room sand and re-finish is £20 to £30 "
              "a square metre if you have it done.",
              avoid=("deep scratch", "scratches down", "scuffed", "laminate", "click", "install", "worktop",
                     "worktops", "counter", "countertop", "sink", "bath", "table")),
        entry("mice-in-the-house",
              (("mice", "mouse"),
               ("loft", "attic", "kitchen", "house", "flat", "garage", "shed", "cupboard", "droppings",
                "scratching", "noise", "noises", "get rid", "rid of", "infestation", "coming in",
                # "how do i stop mice getting in" names the way in rather than the room they are in,
                # and it was handed off to a pest controller without an answer.
                "getting in", "get in", "got in", "get into", "getting into", "coming into",
                "keep out", "keep them out", "stopping", "stop")),
              "Find the way in first: mice follow pipes and cables, so check the gap round the pipework "
              "under the sink, the air brick, and any gap wider than a pencil behind kitchen units, and "
              "block those with wire wool and filler. Then bait two or three traps along the wall, "
              "because mice run against edges, and clear the food source - a sealed bin and nothing left "
              "out overnight. Skip poison in a loft if there are pets or children, and the council pest "
              "control team is usually cheaper than a private firm.",
              # rats are a different job: outside they want locked bait stations and no bird seed,
              # and the indoor mouse advice is wrong for a shed, a garden or a compost heap
              avoid=("cat", "cats", "kitten", "dog", "hamster", "pet", "rat", "rats", "rodent",
                     "garden", "outside", "compost", "bird feeder", "bird seed", "field mouse"), report=True),

        # Woodlice are damp, not an infestation: nothing answered them at all, and "how do i get rid
        # of woodlice" was a search hedge.
        entry("woodlice",
              (("woodlice", "woodlouse", "wood lice", "slaters", "sow bugs", "pill bugs", "pillbugs",
                "isopods"),
               ("get rid", "rid of", "kill", "killing", "coming in", "come in", "in the house",
                "in my house", "in the kitchen", "in my kitchen", "in the bathroom", "everywhere",
                "keep finding", "finding", "remove", "stop", "why", "damp", "in the corner")),
              "Woodlice eat rotting wood and need damp, so drying the damp out is the whole job: fix "
              "the leak, clear wet leaves and timber away from the outside walls, and ventilate the "
              "room they keep appearing in. They do not damage anything in a dry house and they die "
              "within days indoors. Find the wet wood or the damp corner they are living under, and a "
              "dehumidifier or a line of salt buys you time while you sort it.",
              # they are not lice, not a bite and not a pest control job
              avoid=("bite", "bites", "bitten", "itch", "itching", "rash", "head lice", "nits",
                     "cat", "dog", "pet", "eat", "eating", "poison", "harmful", "dangerous",
                     "get in my hair"), report=True),

        # The mouse answer stands rats down on purpose - outside, the advice is the opposite one, and
        # there was no row to catch them: "how do i get rid of rats" was a shrug and "rats in the
        # garden" was the same, so a common garden question had nothing behind it.
        entry("rats-outside",
              (("rat", "rats", "rodent", "rodents"),
               ("garden", "shed", "outside", "outdoors", "compost", "bin", "bins", "bird feeder",
                "bird feeders", "bird seed", "decking", "garage", "drive", "greenhouse", "pond",
                "scratching", "droppings", "get rid", "rid of", "house", "loft", "under the",
                "in the day", "daytime", "getting in", "get in", "coming in", "keep out", "stop")),
              "Cut the food and the cover before you bait: take the bird feeders down or use a seed "
              "tray, keep the compost heap closed and stop putting cooked food in it, and clear the "
              "long grass and rubbish they are running behind. Then use two lockable bait stations "
              "along the wall where you have seen them and check them every couple of days - loose "
              "poison is a real risk to cats, dogs and children. If they are in the house, the "
              "council's pest control team is usually cheaper than a private firm.",
              # Somebody else's pet is not a rat, and a rat in the road is not your problem.
              avoid=("cat", "cats", "kitten", "dog", "dogs", "hamster", "pet", "pets", "gerbil",
                     "ferret", "road", "attic"), report=True),

        # "Is the bait safe with a toddler in the house" had no answer at all: the search hedge, or a
        # referral to a pest controller who was never asked. Poison, powder, pellets and cleaner are
        # ordinary things under a sink or in a shed, and the question about them is not what they are
        # for - it is who can reach them. One row reads the hazard and the person, because the rule is
        # the same for all of them: the box, the locked cupboard, the wash, and who to ring.
        entry("chemicals-and-a-child-or-pet",
              # not the bare adjectives "poison" and "poisonous": half the toxicity questions in the
              # house have them ("which plants are poisonous to cats" is the plants answer), so the
              # poison has to be the named product.
              (("bait", "rat bait", "mouse bait", "bait box", "bait station",
                "rat poison", "mouse poison", "rodenticide", "slug pellet", "slug pellets",
                "ant powder", "ant killer", "ant bait", "insect powder", "weedkiller", "weed killer",
                "pesticide", "mouse trap", "mouse traps", "rat trap", "rat traps",
                "flea bomb", "flea bombs", "fogger", "bug bomb", "oven cleaner", "drain cleaner",
                "bleach", "paint thinner", "turps", "turpentine", "antifreeze", "air freshener",
                "air fresheners", "diffuser", "reed diffuser", "plug in air freshener", "chemical",
                "chemicals",
                # A spray is in the room rather than in a cupboard, so the question about it is the
                # air and the person breathing it: "is the spray safe with a cat" was the cat's
                # cystitis card and "is fly spray safe with a baby" was the flying-with-a-baby one.
                "spray", "sprays", "aerosol", "fly spray", "insect spray", "ant spray",
                "wasp spray", "flea spray", "bug spray", "mosquito spray", "room spray",
                "fly killer", "insect killer"),
               ("toddler", "toddlers", "baby", "babies", "newborn", "child", "children", "kid",
                "kids", "grandchild", "grandchildren", "pregnant", "pregnancy", "expecting",
                "cat", "cats", "kitten", "kittens", "dog", "dogs", "puppy", "puppies", "pet",
                "pets", "hamster", "rabbit", "bird", "birds", "parrot", "fish", "safe", "unsafe",
                "dangerous", "harmful", "poisonous", "risky", "ok around", "get at",
                "breathe", "breathing", "breathe in", "breathing in", "fumes", "inhale",
                "in the room", "same room", "the room", "ventilate",
                # "is the spray safe with a cat" was the cat's cystitis card and now ties with
                # the rain-driving row at four, which takes it on order. The way it is asked is
                # "safe with"/"safe around"/"safe for", and a two-word match outweighs the one
                # word that row and this one share.
                "safe with", "safe around", "safe for", "safe to use", "is it safe",
                "ok with", "ok around", "harmful to", "harmful for", "dangerous to",
                "dangerous for", "bad for")),
              _chemical_safety,
              # somebody else's food is a vet question with its own answers (chocolate, onions,
              # grapes, lilies); and bleach on white cotton is the laundry answer, not this one.
              avoid=("chocolate", "onion", "onions", "garlic", "grape", "grapes", "raisin",
                     "raisins", "sultana", "sultanas", "xylitol", "lily", "lilies", "poinsettia",
                     "avocado", "alcohol", "caffeine", "whites", "white cotton", "cotton",
                     "laundry", "washing", "nappies", "nappy", "stain", "stains", "toilet",
                     "mould", "limescale", "descale", "drain", "blocked", "smell in", "how do i clean",
                     "how to clean",
                     # a plant, a bulb and a mushroom are poisonous without anybody putting them
                     # there: "which plants are poisonous to cats" is the houseplants answer.
                     "plant", "plants", "houseplant", "houseplants", "bulb", "bulbs", "flowers",
                     "shrub", "shrubs", "tree", "trees", "mushroom", "mushrooms", "berries",
                     "cat grass", "ivy", "holly", "oak", "acorn", "acorns",
                     # a spray is asked about the room it was used in, and the room's smell and
                     # its stains are other answers. Not "flea": the bomb that is the point of this
                     # row is a flea bomb, and as a bare avoid word it stood the row down on the
                     # one product people ask about most - "are flea bombs safe with a fish tank"
                     # and "can i use a flea bomb with a dog in the house" were the fleas card.
                     # "flea collar" stays: a collar on the animal is the fleas answer.
                     "stain", "stains", "carpet", "carpets", "mattress", "sofa", "odour",
                     "smell", "smells", "stinks", "flea collar", "bite", "bites",
                     "bitten", "itch", "itching", "marking", "litter",
                     # not "spraying": that is the form of "spray" the key wants, and as an avoid
                     # word it stood the whole row down for every line that said spray at all.
                     # A pet that has eaten the spray is a dose question rather than a fumes one,
                     # and the poisoning card asks the three things that matter: "my dog ate some
                     # fly spray" was this card once the spray was keyed here. Only the words that
                     # reach that card are fenced - "licked" and "drank" were tried too, and they
                     # stood the row down with nothing behind it, which lost the weedkiller card
                     # for "my cat licked weedkiller".
                     "ate", "eaten", "eating", "swallowed", "swallowing", "poisoned",
                     "keeps spraying", "is spraying", "spraying indoors", "cat spraying")),

        # A damp bathroom used to reach the fan-cleaning answer, which is the wrong diagnosis: the
        # water is on the walls because the air carries it there, and the fan is only part of the cure.
        entry("damp-bathroom",
              (("bathroom", "shower room", "ensuite", "en suite", "wet room", "loo", "toilet"),
               ("damp", "damper", "damp patch", "steamy", "steam", "condensation", "wet walls",
                "sweating", "always wet", "stays wet")),
              ("Run the extractor while you shower and for twenty minutes after, or open a window, and "
               "keep the door shut so the wet air stays in one room. Wipe the walls down, dry washing "
               "outside rather than over a radiator, and keep the heating on low: warm air holds the "
               "water, a cold bathroom drops it on the walls. If it carries on, the fan is "
               "under-powered or the duct is blocked."),
              # a leak, a dripping fan and mould treatment are other answers; a spray-on mould killer
              # is a step after the damp is fixed, not the fix.
              avoid=("leak", "leaks", "leaking", "dripping", "water coming", "from above", "roof",
                     "pipe", "burst", "remove mould", "get rid of the mould", "black mould", "kill")),
        # A bath or a shower is a choice between two everyday things, and the cleaning card took it
        # because `bath` is in its key. The numbers are the ones a person can act on: a five-minute
        # shower is roughly half the water of a full bath, and a warm bath an hour or two before bed
        # is one of the few home remedies for dropping off that has evidence behind it.
        # Length and frequency, which is a different question from which is nicer and from the water
        # meter: "how long should a bath be" and "do i need to shower every day" were answering the
        # water comparison, whose own second sentence admitted it was guessing at the question.
        entry("bath-length",
              (("bath", "baths", "bathtub", "shower", "showers", "showering", "shower gel"),
               ("how long", "how often", "every day", "daily", "too long", "how many times",
                "need to shower", "need to bathe", "should i shower", "should i bathe",
                "yes or no", "length of", "much time")),
              _bath_length,
              avoid=("clean", "cleaning", "cleaner", "scum", "limescale", "mould", "drain", "blocked",
                     "dog", "dogs", "cat", "cats", "baby", "babies", "newborn", "toddler", "plug",
                     "boiler", "leak", "before bed", "help me sleep",
                     # the comparison keeps its own lines
                     "or a shower", "or a bath", "bath or shower", "shower or a bath",
                     "better than", "which is better",
                     # and the time of day is another card's: "should i shower in the morning or at
                     # night" is a routine question, not a length one
                     "morning", "evening", "at night", "before work", "after work") + _BATH_CITY),

        # How hot the water should be is the first thing anyone asks about a bath, and no card
        # answered it: "what temperature should a bath be for a toddler" was the fever card ("rest,
        # drink plenty and take paracetamol") and "how warm should a baby bath be" was the
        # bottle-warming card ("stand the bottle in a jug of warm water"). The bath word is the
        # subject and a heat word is the question, and the fever and bottle rows stand aside for
        # it rather than the other way round, because a bath is not a body and not a feed.
        entry("bath-water-heat",
              (("bath", "baths", "bathtub", "bath tub", "bath water", "bathwater", "baby bath",
                "baby's bath", "babys bath", "babies bath", "toddler bath", "a bath", "the bath",
                # the compound reads as one thing to the word reader, so the ways people write it
                # are named here rather than left to the two ordinary words
                "baby bath be", "baby bath temperature", "bath be for a toddler",
                "bath be for a baby", "bath for a toddler", "bath for a baby"),
               ("how hot", "how warm", "too hot", "temperature", "degrees", "warm enough",
                "hot enough", "what temperature", "right temperature", "37c", "38c", "40c")),
              "A bath is right at 37 to 38C - the elbow test is the reliable one, because a hand "
              "that has been in the water stops being a judge. Run the cold in first and top it up "
              "with hot, never the other way round, and never add hot water with a child already "
              "in it. For a baby or a toddler it is the same 37 to 38C and only up to the waist "
              "when they are sitting, with the cold tap run last, and a bath above 40C is too hot "
              "for anyone to sit in for long.",
              # the cleaning job, the pet, the sleep bath and the shower comparison are other cards
              avoid=("clean", "cleaning", "cleaner", "scum", "limescale", "stain", "stains",
                     "mould", "drain", "blocked", "dog", "dogs", "cat", "cats", "plug",
                     "boiler", "leak", "hot tub", "jacuzzi", "sitz", "bath salts", "bath bomb",
                     "bath mat", "bathroom", "before bed", "help me sleep",
                     "or a shower", "or a bath", "bath or shower", "shower or a bath",
                     "which is better", "better than", "how long", "how often", "how deep",
                     "swimming", "swim", "pool", "spa") + _BATH_CITY,
              bias=1),

        # A baby in the bath is a safety question and the answer is a temperature and a depth, so it
        # is its own card rather than a comparison with a shower.
        # A bare "washing" was in the subject below and it made this row every "how often should i
        # wash <thing>" line in the language: "washing" matched and "how often" was the second
        # signal, so "how often should i wash my pyjamas" (the pyjamas-often row), "my coat" and "my
        # bra" (clothing) and "bedsheets" (bedsheets-often) all got 5cm of water at 37C. The subject
        # is now the bath itself, or a wash that says whose it is, so the row still answers "how do i
        # wash my newborn" and "how often should i bathe a baby" and leaves the rest of the washing
        # to the rows that keep it.
        entry("baby-bath",
              (("bath", "bathtub", "bathe", "bathing", "top and tail",
                "wash a baby", "wash the baby", "wash my baby", "wash your baby",
                "washing a baby", "washing the baby", "washing my baby", "washing your baby",
                "wash a newborn", "wash the newborn", "wash my newborn", "washing a newborn",
                "washing the newborn", "washing my newborn", "wash babys hair", "wash baby hair",
                "wash the babys hair", "wash the baby's hair", "wash my babys hair",
                "wash my baby's hair"),
               ("baby", "babies", "newborn", "infant", "toddler", "how hot", "temperature",
                "how often", "how deep", "safe", "first bath", "umbilical", "cord")),
              "Fill it to about 5 to 8 cm with water at 37 to 38C - elbow or wrist temperature, which "
              "feels neither warm nor cool - and have the towel, nappy and clean clothes within reach "
              "before you start, because you never leave a baby alone in water, not for a second. "
              "Support the head and shoulders with one forearm, wash with plain water for the first "
              "month or so, and keep the room warm since a wet baby loses heat fast. Twice or three "
              "times a week is enough for a newborn; top and tail in between.",
              avoid=("clean the bath", "cleaning", "scum", "limescale", "mould", "drain", "blocked",
                     "dog", "cat", "hot tub", "jacuzzi", "sitz", "bath salts", "bath bomb",
                     # a bath a pregnant woman is asking about is her own bath, not a baby's: "is a
                     # hot bath safe in pregnancy" was told to fill it 5 to 8 cm deep
                     "pregnant", "pregnancy", "trimester", "weeks pregnant",
                     # a load of washing is not a baby in water: "what temperature should i wash
                     # clothes at" matched "washing" here and "temperature" in the second group,
                     # and got 5cm of water at 37C instead of the washing-machine dial
                     "clothes", "laundry", "wash clothes", "washing clothes", "load of washing",
                     "washing machine", "colours", "colors", "darks", "whites", "lights",
                     "bedding", "sheets", "duvet", "towels",
                     # a bottle to wash and a load of baby clothes are the bottle-feeding and the
                     # baby-clothes rows in family.py: "how do i wash my babys bottles" was getting
                     # 5cm of bath water, and the bath avoids them there but not here
                     "bottle", "bottles", "sterilise", "sterilising", "sterilize", "formula", "pump",
                     "baby clothes", "babygrow", "baby grow", "vest", "muslin", "nappy", "nappies",
                     # and the rest of the washing nobody means as a bath: hands, dishes, a face, a
                     # shower. "what temperature should i wash my hands at" was getting 5cm of water
                     # at 37C because this row reads "washing" and "temperature" and nothing else
                     "hand", "hands", "dishes", "dish", "plates", "pots", "pans", "face", "hair",
                     "shower", "washing up", "car", "car wash",
                     # the rest of the linen: "sheets" and "towels" are above, and a pillow, a
                     # mattress or a bath mat is the same question with another word for it
                     "pillow", "pillows", "pillowcase", "pillowcases", "mattress", "bath towel",
                     "bath towels", "linen", "flannel", "flannels", "face cloth", "bath mat",
                     "curtain", "curtains")
                     + _BATH_CITY),

        entry("bath-or-shower",
              (("bath", "baths", "bathtub", "shower", "showers", "showering"),
               ("better", "best", "worse", "prefer", "rather", "or a bath", "or a shower",
                "bath or shower", "bath or a shower", "shower or bath", "shower or a bath",
                "instead of", "worth it",
                # "what uses less water a bath or a shower" asks about the water, not about which
                # is nicer, so the water words count as the ask too
                "less water", "more water", "uses less")),
              "Showering wins on time and water - five minutes with a normal head is about 40 to 50 "
              "litres against 80 or so for a full bath - so if it is the water you are asking about, "
              "shower and keep it short. Neither is better for your skin; long hot water is what "
              "leaves it tight and itchy, so keep it warm rather than hot and pat dry instead of "
              "rubbing. If a bath leaves you light-headed, get out slowly and drink some water.",
              # cleaning a bath or a screen is the cleaning lane's answer, and a bath for a baby, a
              # dog or a cat belongs to those cards
              avoid=("clean", "cleaning", "cleaner", "scum", "limescale", "stain", "stains", "mould",
                     "drain", "blocked", "dog", "dogs", "cat", "cats", "baby", "babies", "newborn",
                     "toddler", "plug", "water pressure", "boiler", "leak",
                     # a bath for sleep or for aches is the next card, whose answer leads with that
                     "before bed", "help me sleep", "aches", "ache", "relax", "unwind", "sore",
                     "stiff", "muscles",
                     # length and frequency are their own card below: "how long should a bath be"
                     # is not a comparison with a shower
                     "how long", "how often", "every day", "daily", "too long", "how many times")
                     + _BATH_CITY),

        # The same bath, asked about the night rather than the water meter: "is a hot bath good
        # before bed" wants the sleep answer first, not a comparison with a shower.
        entry("bath-for-sleep",
              (("bath", "baths", "bathtub", "hot bath", "warm bath", "long bath", "deep bath",
                "shower", "showers"),
               ("before bed", "before bedtime", "help me sleep", "help you sleep", "to sleep",
                "sleep", "aches", "ache", "aching", "relax", "unwind", "sore", "stiff", "muscles",
                "winding down", "cant sleep", "can't sleep")),
              "Yes - a warm bath 10 to 15 minutes long, an hour or two before bed, is one of the few "
              "home things that reliably helps you drop off: the water warms you and the climb back "
              "down afterwards is what makes you sleepy. Keep it warm rather than hot, which leaves "
              "skin tight and can make you light-headed, and get out slowly if the room spins. The "
              "same bath eases aching muscles for the same reason.",
              # the water comparison, the cleaning job and a bath for a baby or a pet are other cards
              avoid=("clean", "cleaning", "cleaner", "scum", "limescale", "stain", "mould", "drain",
                     "blocked", "dog", "dogs", "cat", "cats", "baby", "babies", "newborn", "toddler",
                     "plug", "boiler", "leak", "less water", "more water", "uses less")
                     + _BATH_CITY),

        # "is it normal to feel dizzy after a hot bath" was a shrug on main: the water comparison is
        # the wrong answer for it, because the question is what the heat does to your blood pressure.
        entry("bath-dizzy",
              (("bath", "hot bath", "bathtub", "shower", "hot shower", "jacuzzi", "hot tub"),
               ("dizzy", "dizziness", "light headed", "light-headed", "faint", "fainted", "spins",
                "spinning", "woozy", "sick", "nausea", "head rush", "stand up", "standing up")),
              "Hot water opens up the blood vessels near the skin, so blood pressure drops and standing "
              "up quickly leaves you light-headed - it is common, and it is not a sign of anything "
              "wrong in a healthy person. Get out slowly, sit down on the edge for a minute, keep the "
              "water warm rather than hot, drink some water and eat beforehand. If you actually faint, "
              "or it happens every time, or it comes with chest pain or palpitations, get it checked.",
              avoid=("clean", "cleaning", "scum", "limescale", "mould", "blocked", "drain", "dog",
                     "cat", "baby", "babies", "newborn", "toddler", "before bed", "help me sleep",
                     "less water", "more water") + _BATH_CITY),

        entry("bathroom-fan-wont-stop",
              (("fan", "extractor", "extractor fan", "ventilation"),
               ("runs all the time", "runs on", "wont turn off", "won't turn off",
                "wont switch off", "won't switch off", "wont go off", "won't go off",
                "never stops", "never turns off", "keeps running", "stays on", "left on",
                "all night", "all the time", "after the light goes off", "timer")),
              "Ten or fifteen minutes of running on after the light goes off is the timer doing its "
              "job, and it is what keeps the damp out. A fan that never stops has an overrun set too "
              "long, a stuck timer, or a humidistat turned up too high: take the cover off and look "
              "for the overrun screw or a dial inside, set the overrun to about fifteen minutes, and "
              "turn the humidistat down to around 60% - if neither is there, or it will not change, "
              "the module is a swap, around £25 to £60. A fan that runs only when nobody is in the "
              "room, or one that is still going after the isolator is off, is a wiring job.",
              # a fan that drips, leaks or drips condensation is a duct and airflow problem, not a
              # timer one, and the noisy entry below owns the noise and the cleaning.
              avoid=("drip", "drips", "dripping", "water", "leak", "leaks", "leaking",
                     "condensation", "cold", "black mould", "bathroom is damp", "steam",
                     # a machine's fan is not a bathroom extractor: "my laptop fan is loud all the
                     # time" was told to look for the overrun screw behind the cover, and a cooling
                     # fan that runs while the machine is on is the ordinary way it behaves
                     "laptop", "lap top", "computer", "pc", "desktop", "macbook", "mac book",
                     "phone", "console", "playstation", "ps4", "ps5", "xbox", "gpu",
                     "graphics card", "car", "van", "motorbike", "engine", "overheating",
                     "overheat", "oven", "fridge", "freezer", "tumble dryer"),
              # "keeps running after the light goes off" also matches the laundry-colour table's
              # "light" and "goes off": a fan that will not stop is this answer.
              bias=3),
        entry("bathroom-fan-noisy",
              (("bathroom", "shower", "loo", "toilet", "wet room", "ensuite"),
               # a damp or steamy bathroom is ventilation and a mould treatment, not a dirty fan:
               # "steam", "steamy", "damp" and "mould" were in this key and took `my bathroom is damp`
               # "not working" is not here: this row answers a fan that is noisy, humming or
               # weak, and with the phrase in the key "the shower is not working" and "the toilet
               # is not working" were both told to wipe the blades of an extractor fan. A fan that
               # is dead is the appliance or the isolator, and both have their own rows.
               ("fan", "extractor", "ventilation", "vent", "humming", "rattling", "buzzing", "whirring",
                "noisy", "loud", "noise", "weak")),
              "Clean the cover and the blades first: a dust-clogged fan in a steamy room is both weak "
              "and loud, and the grille usually comes off with a push and the blades wipe with a damp "
              "cloth once the isolator is off. A rattle is normally the cover or the backdraught flap in "
              "the duct; a buzz or a grind means the bearing has gone, and a new fan is £25 to £60 for "
              "the part with about an hour of an electrician. A fan that runs on for ten or fifteen "
              "minutes after the light goes off is the timer doing its job and is what actually stops "
              "the damp; one that never stops has a stuck timer or a humidistat set too high, and the "
              "module is a swap.",
              # buying, pricing and fitting a fan is a shopping job, and "damp" on its own is the
              # damp answer: this entry is the fan that already exists and is noisy or weak
              avoid=("kitchen", "hob", "cooker", "grease", "oven", "cost", "costs", "price",
                     # a fan that never stops is the timer or the humidistat, not the dust: the
                     # "wont stop" entry above leads with that
                     "runs all the time", "runs on", "wont turn off", "won't turn off",
                     "wont switch off", "won't switch off", "wont go off", "won't go off",
                     "never stops", "keeps running", "stays on", "after the light goes off",
                     # a fan that drips is water in the duct or condensation, not dust on a blade
                     "drip", "drips", "dripping", "water", "leak", "leaks", "leaking",
                     "condensation",
                     "how much", "cheap", "cheapest", "buy", "buying", "which", "best", "install",
                     "installing", "installation", "fitter", "fitted", "fit one", "replace",
                     "replacing", "replacement", "new fan", "new bathroom fan", "quote",
                     # a weak shower is a water fault, not a fan one: the shower entry (#1148)
                     # answers it, and "electric shower + weak" was getting the fan cleaned
                     "electric shower", "power shower", "shower pressure", "shower is weak",
                     "shower dribbles", "shower head", "showerhead")),
    # The radiator's ordinary life had no rows at all: the drain job, the dust between the fins and the
    # foil behind it were punts or another card ("how do i clean a radiator" got "that's beyond what I
    # know well"; "how do i drain a radiator" the plumber fence; "how do i take a radiator off the
    # wall" the pencil-rubber paint card).
    entry(
        "radiator-drain",
        (("drain", "draining", "drained", "empty", "emptying", "take off", "taking off",
          "take out", "remove", "removing", "come off", "swap", "replace",
          # "take a radiator off the wall" is the same job, and "take off" is not in it
          "off the wall", "to decorate", "decorating", "for decorating",
          # and so is putting the water back: "how do i fill a radiator back up" was a punt, and the
          # valve row then took it on the word "up"
          "fill", "filling", "fill up", "fill it up", "refill", "refilling", "top up",
          "topping up", "back up"),
         # not "towel rail": a follow-up "and the towel rail" after a radiator question belongs to
         # the chat, and a towel rail often has no numbered head to answer about
         ("radiator", "radiators", "rad", "rads",
          # the whole system is emptied the same way, only at the lowest drain cock
          "central heating", "the heating", "heating system", "the system")),
        "Turn the heating off and let it go cold, then close the valve at both ends: the wheelhead on "
        "the flow and the lockshield on the return, and count the turns on the lockshield so you can "
        "set it back the same, because that is what balances the house. Put a shallow tray and old "
        "towels under the bottom union and open the bleed valve at the top to let air in - the water "
        "comes out of the nut slowly and it is filthy black, so do it in short goes. Take the bracket "
        "off, and when you refit it open the bleed valve and top the pressure up at the filling loop "
        "to about 1.2 bar, then bleed every radiator once more. If it is a sealed combi system and the "
        "pressure will not hold, that is a plumber's job. For the whole house rather than one "
        "radiator, do the same at the lowest drain cock with every bleed valve open, because one "
        "radiator holds only a bucket or two.",
        # a radiator that is cold, noisy or leaking is a fault with its own row, and an oil-filled one
        # holds no water at all
        avoid=("cold", "colder", "not heating", "not getting hot", "cold at the top", "cold at the "
               "bottom", "bleed", "bleeding", "bleed it", "noisy", "banging", "knocking", "gurgling",
               "leak", "leaking", "dripping", "towel rail not", "boiler", "no pressure",
               "lost pressure", "pressure is low", "electric", "oil filled", "oil-filled",
               "oil radiator",
               "clothes", "dry clothes", "car", "van", "engine", "phone",
               "laptop", "battery", "pasta", "sink", "bath", "pond", "pool", "garden", "account",
               "bank", "pool of water",
               # a mark on the wall next to a radiator is the paint row's, not a plumbing job: "how
               # do i get scuff marks off the wall near the radiator" was told to drain it
               "scuff", "scuffs", "mark", "marks", "crayon", "ink", "stain", "stains", "dirty",
               "clean", "cleaning", "wipe", "wash", "paint", "painting", "repaint", "repainting",
               # rust is a paint-and-prep job on the outside of the metal, not plumbing
               "rust", "rusty", "rusting"),
        bias=3),

    entry(
        "radiator-clean",
        (("clean", "cleaning", "dust", "dusty", "hoover", "hoovering", "vacuum", "vacuuming",
          "wash", "wipe", "wipe down", "fins"),
         ("radiator", "radiators", "rad", "rads", "behind the radiator")),
        "Dust between the fins does more to cut the heat than anything you can do on the outside: run "
        "a vacuum cleaner's crevice tool down each gap with the heating off, and a long flexible "
        "duster gets the space behind without moving the radiator. For the paintwork plain warm water "
        "with a drop of washing-up liquid is enough - skip anything abrasive, which takes the enamel "
        "off - and keep water away from the valves and away from an electric one. Once before the "
        "heating goes on in autumn, and again in mid-winter if a room is slower to warm than it used "
        "to be.",
        avoid=("drain", "draining", "bleed", "bleeding", "leak", "leaking", "dripping", "cold",
               "not heating", "noisy", "banging", "gurgling", "paint", "painting", "decorate",
               "decorating", "rust", "rusty", "clothes", "towel rail", "boiler", "car", "van",
               "engine", "oven", "kitchen", "phone", "laptop", "floor", "carpet", "pond",
               # "how do i clean the wall behind the radiator" is about the wall, and the wall row
               # was answering it well before this row existed
               "wall", "walls", "skirting", "behind the wall", "the wall behind"),
        bias=2),

    entry(
        "radiator-foil",
        (("foil", "tin foil", "reflector", "reflective", "reflect", "insulate", "insulation"),
         ("radiator", "radiators", "rad", "behind")),
        "Worth it only on an outside wall with no cavity insulation: a sheet of radiator foil behind "
        "the radiator, shiny side facing the room, pushed back so it does not touch the brackets, "
        "gives you a few percent rather than the half the adverts claim. Keep the gap under the "
        "radiator clear, because that is where the cold air comes in and the warm air goes out - a "
        "shelf or a curtain hanging over the top cancels the gain. Foil on an inside wall, or over a "
        "cavity, does nothing at all.",
        avoid=("loft", "roof", "cavity wall", "wall insulation", "shed", "greenhouse", "drain",
               "bleed", "bleeding", "leak", "leaking", "cold", "noisy", "boiler", "cooker", "oven",
               "food", "garden", "pond", "cake", "chicken"),
        bias=2),

    # A ruck in a carpet is a room job, and the word is a rugby rule: "how do i stop a carpet from
    # rucking up" and "the carpet is rucking up" were both answered "A maul is a ball carrier held
    # up with teammates bound on to him". The sport row now stands down on the floor words, and
    # the ripple, the baggy edge and the rug that slides all want this answer.
    entry(
        "carpet-ruck",
        (("carpet", "carpets", "rug", "rugs", "carpet tile", "carpet tiles", "underlay",
          "gripper", "grippers", "flooring"),
         ("rucking", "rucked", "ruck", "rucks", "ripple", "ripples", "rippled", "wrinkle",
          "wrinkles", "wrinkled", "bubble", "bubbles", "bubbling", "baggy", "puckered",
          "puckering", "lifting", "come up", "coming up", "creased", "creases", "wavy",
          "sliding", "slides", "slipping", "moves", "moving", "loose")),
        "A carpet that ripples or wrinkles has stretched, and the fix is a re-stretch rather than "
        "an iron: the pile gives over the years, and a wet clean, a hot radiator or a heavy chair "
        "in one spot speeds it up. A fitter lifts the carpet off the gripper along one or two "
        "walls, pulls it tight with a knee kicker or a power stretcher and hooks it back on, which "
        "is an hour or two of work and far cheaper than a new carpet. One small bubble can be "
        "worked towards the nearest wall by hand and taken out the same way, and a bump that comes "
        "back after a day means the underlay has gone, not the carpet. A rug that slides on a "
        "wooden floor is the other problem: a rubber or felt underlay pad, or a strip of double-"
        "sided carpet tape, stops it without marking the boards.",
        bias=1),

        # A workshop edge is not a kitchen knife, a garden shear or a pair of scissors: each of
        # those has its own row and its own angle. A chisel, a plane iron and a masonry bit had
        # nothing at all - "how do i sharpen a chisel" got "that's beyond what I know well, sorry"
        # and "my drill bit is blunt" the shrug.
        entry("workshop-edge",
              (("chisel", "chisels", "wood chisel", "bevel edge chisel", "mortise chisel",
                "plane iron", "plane blade", "hand plane", "block plane",
                "drill bit", "drill bits", "masonry bit", "masonry bits", "hss bit", "spade bit",
                "auger bit", "forstner bit", "hole saw", "utility knife", "stanley knife",
                "craft knife"),
               ("sharpen", "sharpening", "sharpened", "sharper", "blunt", "dulled", "dull",
                "hone", "honing", "whetstone", "oilstone", "grind", "grinding", "file", "filing",
                "wont cut", "won't cut", "doesnt cut", "doesn't cut", "not cutting", "burr",
                "rounded", "chipped", "nicks", "nicked")),
              "Chisel and plane iron: the bevel is 25 degrees off the flat back, so a honing guide "
              "set to 25 and a strip of wet-and-dry on a flat tile does it - 240 grit if the edge "
              "is nicked, then 600 and 1200, ten strokes on the bevel, then lay the back flat on "
              "the finest paper and pull it back a few times to take the burr off. A blunt chisel "
              "crushes the wood and takes more force to steer, so it is the sharp one that is "
              "safer. A masonry bit is blunt when the tip is rounded: a few strokes of a diamond "
              "file on the wings either side of the point, at the angle they already have, brings "
              "it back. An HSS bit filed by hand is slow going and a new one costs a few pounds, so "
              "buy a bit rather than an afternoon; a Drill Doctor type jig, about \u00a330, earns "
              "its place only if you go through a lot of them. In a utility knife, swap the blade: "
              "a snap-off blade is sharper than anything you can dress at home.",
              # the other edges in the house have their own rows, and a sharp word about a picture
              # or a pain is not an edge at all
              avoid=("knife", "knives", "kitchen", "cooking", "chef", "scissors", "shears",
                     "secateurs", "hedge", "hedges", "axe", "chainsaw", "mower", "lawn", "pencil",
                     "pencil sharpener", "image", "photo", "picture quality", "sound", "pain",
                     "eyes", "vision", "glasses", "tooth", "teeth", "sharply"),
              bias=2),
        # A nail is a piece of metal before it is a fingernail. body.py stands its nail rows down
        # when the line has a workshop noun in it, which is why "how do i stop wood splitting when
        # i nail it" no longer gets "Nails grow about 3mm a month"; these two rows are what the
        # line falls to instead.
        entry("wood-splits-when-nailed",
              (("wood", "wooden", "plank", "planks", "timber", "batten", "battens", "board",
                "boards", "mdf", "hardwood", "softwood", "decking", "board end",
                "floorboard", "floorboards", "skirting", "skirting board", "skirting boards",
                "architrave", "beading", "joist", "joists", "stud", "studs", "door frame",
                "doorframe", "fence", "fencing", "shed"),
               ("split", "splits", "splitting", "crack", "cracks", "cracking", "splinter",
                "splinters", "splintering", "nail", "nails", "nailed", "nailing", "hammer",
                "pilot hole", "screw")),
              _the_wood_and_the_nail,
              # the joinery row answers how to fix two pieces together, and the sanding row is a
              # different job on the same board
              avoid=("glue two", "join", "joining", "dowel", "sanding", "sand it", "sandpaper",
                     "firewood", "fire wood", "log", "logs", "log burner", "stove", "season",
                     "seasoned", "kiln",
                     # a fence panel that came down is a post that has moved, and that row says
                     # so: "how do i nail a fence panel back up" is not a pilot hole
                     "fence panel", "fence panels", "panel", "panels", "post", "posts",
                     "gate", "back up"),
              # the firewood row holds "wood" and "when", which is half this line's words
              bias=2),
        entry("a-nail-in-a-wall",
              (("nail", "nails", "nailing", "nailed", "picture hook", "picture hooks",
                "rawlplug", "rawlplugs", "rawl plug", "rawl plugs", "wall plug", "wall plugs"),
               ("wall", "walls", "brick", "plasterboard", "stud", "studs", "picture",
                "pictures", "put up", "putting up", "hang", "hanging", "remove", "removing",
                "out", "pull", "old", "stuck", "left in")),
              _a_nail_in_the_wall,
              avoid=("fingernail", "fingernails", "toenail", "toenails", "my nail", "my nails",
                     "cut my nails", "bite", "biting", "polish", "varnish", "manicure",
                     "tyre", "tyres", "tire", "tires", "puncture", "wood", "plank", "timber",
                     "door", "doors", "decking", "fence", "fencing",
                     # a plasterboard wall already has a fixing card of its own, and it names the
                     # stud finder and the hollow-wall fixing, which is more than this row can
                     "plasterboard", "plaster board", "hollow wall", "hollow walls",
                     "stud finder", "plasterboard fixing", "plasterboard fixings"),
              # the wall-wipe and wall-mark rows hold "wall" and "remove" as well, and each of
              # them answers a mark or a grease film
              bias=2),
    ]
