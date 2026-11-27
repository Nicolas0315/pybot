"""Rows 8 of 10 of `home_craft.entries()`: `appliance-broken` .. `fence-repair`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _a_machine_that_will_not_empty,
    _not_the_food_in_the_fridge,
    _the_fly_is_not_a_verb,
    _the_stopped_fixture_entries,
)


def rows():
    from ..knowledge.home import not_a_sound
    from ..knowledge.home import (
        EXTRACTOR_GREASE_FILTER, NOISE_WORDS, TUMBLE_DRYER_FILTER, WASHING_MACHINE_FILTER,
        _a_machine_consumable, _appliance_noise, _not_a_cook_ask, _place_smell,
        _repair_judgement, _soft_smell, _where_the_consumable_goes, entry, the_filter_of
    )
    return [
        # An appliance that is simply dead had no answer at all: "my dishwasher is broken, what can i
        # do", "my washing machine wont come on", "my fridge is broken what do i do", "my toaster is
        # broken" all got a shrug or an echo. `repair-or-replace` needs a decision word in the line, so
        # a plain fault was nobody's answer. This is the first-aid half: the cheap checks, then the
        # fault code, then the call. The money rule stays in `repair-or-replace`, which its own `ask`
        # gate keeps, and every named fault (a leak, a smell, a drum that will not turn, a fridge that
        # is warm) keeps the entry that knows it.
        entry("appliance-broken",
              (("washing machine", "washer", "washer dryer", "tumble dryer", "dryer", "dishwasher",
                "fridge", "freezer", "fridge freezer", "oven", "cooker", "hob", "microwave", "kettle",
                "toaster", "vacuum", "hoover", "blender", "extractor fan", "telly", "television",
                "appliance", "white goods"),
               ("broken", "broke", "dead", "died", "has died", "packed in", "packing in", "given up",
                "stopped working", "stopped", "wont come on", "won't come on", "wont turn on",
                "won't turn on", "wont switch on", "won't switch on", "wont start", "won't start",
                "not working", "isnt working", "isn't working", "faulty", "nothing happens",
                "what can i do", "what do i do")),
              "A dead appliance is usually the plug, the fuse or a door switch: swap the fuse, try "
              "another socket, shut the door firmly and look the fault code up in the manual. If it "
              "stays dead, take the model number off the sticker and ask the maker or a local repairer "
              "for a fixed-price quote, because under six years old a repair is usually the cheaper "
              "way.",
              # A named fault is another entry's line: the leak, the smell, the drum that will not
              # turn, the machine that trips the house, and the fridge that runs but is warm.
              avoid=("leak", "leaks", "leaking", "drain", "drains", "draining", "wont drain",
                     "not draining", "smell", "smells", "smelly", "musty", "damp", "tripping",
                     "trips", "trip", "fuse box", "rcd", "cuts out", "cutting out", "keeps stopping",
                     "switches itself off", "switching itself off", "noise", "noisy", "banging",
                     "rumbling", "beep", "beeping", "cold", "not cold", "warm", "freezing", "ice",
                     "frost", "defrost", "condenser", "dry properly", "takes ages",
                     # the heating is a system and a gas boiler is Gas Safe work: both have answers
                     "boiler", "the heating", "central heating", "radiator", "radiators",
                     # a machine someone else owns or wants to buy, and a thing that is not one
                     "landlord", "letting agent", "rent", "worth", "repair", "repairing", "replace",
                     "replacing", "new one", "buy a new one", "buy new", "scrap", "scrapping",
                     "engineer", "phone", "laptop", "computer", "tablet", "console", "car", "van",
                     "bike", "bicycle", "cook it", "recall",
                     # "my freezer is full what can i do" is a full freezer, not a dead one, and the
                     # "what can i do" in the key above was all it needed to take that line
                     "full", "full up", "too full", "packed", "overfull", "no room", "no space",
                     "stuffed"),
              # "what can i do with half a bag of spinach in the fridge" is a cooking question that
              # names a fridge, and the "what can i do" in the key above took it: a line that asks
              # what to make with a food it names belongs to the kitchen, not to this row.
              guard=_not_a_cook_ask),
        # The fixtures that are not appliances, and the first check for each: see
        # `_the_fixture_that_stopped` for the lines this took off the bank card, the fibre answer
        # and the extractor fan. The guard is the row's own reading, so a named symptom keeps its
        # own answer and a fixture the table does not know is passed over to the rows that do.
        *list(_the_stopped_fixture_entries(entry)),
        # A broken appliance is a decision, not a shopping question and not a how-to: "is it worth
        # repairing" needs the money rule, and it is the same rule for a washing machine, a dishwasher
        # and an oven, so it is one entry and the appliance words are the first key.
        entry("repair-or-replace",
              (("washing machine", "washer", "tumble dryer", "dryer", "dishwasher", "fridge", "freezer",
                "oven", "cooker", "hob", "microwave", "vacuum", "hoover", "boiler", "kettle", "toaster",
                "mower", "lawnmower", "strimmer", "hedge trimmer", "leaf blower", "blender",
                "hair dryer", "hairdryer", "appliance", "machine", "white goods"),
               ("worth repairing", "worth fixing", "worth mending", "worth replacing", "repair or replace",
                "replace or repair", "fix it or", "repair it or", "buying new", "buy new", "worth",
                "repair", "repairing", "fix", "fixing", "replace", "replacing", "mend", "mending",
                "scrap", "scrapping", "broken", "broke", "engineer", "call someone",
                # The decision often arrives with the symptom instead of the word "repair": "my dryer
                # isnt heating up should i buy a new one" names the fault and the new machine and
                # never says repair, and with only one key word covered it reached no entry at all.
                "not heating", "isnt heating", "isn't heating", "wont heat", "won't heat", "heat up",
                "not spinning", "wont spin", "won't spin", "not turning", "wont turn", "won't turn",
                "not draining", "wont drain", "won't drain", "not drying", "takes ages", "still wet",
                "new one", "buy a new one",
                # The skill question names no money word, so its own words are what such a line
                # shares with the machine: "can i service my lawnmower myself" is a machine and a
                # skill and nothing else.
                "myself", "my self", "diy", "my own", "on my own", "have a go", "give it a go",
                "can i fix", "can i repair", "can i replace", "can i change", "could i fix",
                # "do i need a new washer" is the plainest way the decision is put, and the line
                # names the machine and nothing else: the phrase is the second position the key
                # needs, and nobody asks whether they need a new one of something they do not own.
                "need a new", "need new", "needs a new")),
              _repair_judgement,
              # A how-to is not a decision: "how do i fix a leaking washing machine" keeps its own answer.
              ask=("worth", "replace", "replacing", "repair or", "or repair", "new one", "buying new",
                   "buy new", "scrap", "scrapping", "mend or", "fix it or", "repair it or", "either",
                   # "my dishwasher is broken should i repair it" asks the same question without the
                   # comma, and it was reaching the landlord letter instead of the rule.
                   "repair it", "fix it", "replace it", "should i repair", "should i fix",
                   "should i replace", "mend it",
                   # The decision said the other way round, which is how most people say it: "is it
                   # worth fixing or should i get a new one", "should i get it fixed or buy a new one".
                   # "get a new one" is the same ask as "a new one", and "fixing"/"fixed" alone is not
                   # enough, because "how do i stop the door fixing" is a how-to.
                   "worth fixing", "worth mending", "fixed or", "fixing or", "get it fixed",
                   "get a new one", "get a replacement",
                   # "should i get a new dishwasher or fix this one": the machine is named and the
                   # repair word comes after the "or", which is the same weighing-up as "repair it
                   # or". Without these the line matched the keys and the ask gate refused it, so it
                   # fell through to a shrug.
                   "fix this one", "repair this one", "mend this one", "or fix this", "or repair this",
                   "or fix that", "or repair that",
                   # Who to call is the same decision, and "should i get an engineer out for my dryer"
                   # was answered with the should-I-buy-one take.
                   "engineer", "engineers", "call someone out", "call someone", "call out",
                   "get someone in", "someone in",
                   # The skill question is asked with its own words and no money words at all:
                   # "can i fix my washing machine myself", "can i change the oven element myself".
                   # The rule answers it with the parts list rather than the quote.
                   "can i fix", "could i fix", "can i repair", "could i repair", "can i replace",
                   "can i change", "myself", "my self", "diy", "diy job", "have a go",
                   "give it a go",
                   # "do i need a new washer" is the plainest way the decision is put, and it was
                   # answered with a drill bit (a washer is a fixing as well as a machine) or with
                   # drum sizes. Nobody asks whether they need a new one of something they do not
                   # own, so the phrase carries both the ask and the owning.
                   "need a new", "need new", "needs a new"),
              # "broken" and "repair" are in every line about a machine, and they are also the two
              # words of the landlord letter and of the shopping entry: the decision has to outrank
              # both, which the bias does, and the ask gate keeps it off every other repair line
              # A thing that is not an appliance is not this decision: a jumper that shrank, a car, a
              # laptop, a rented flat and a landlord are all "worth fixing" questions for other answers.
              avoid=("jumper", "wool", "shrank", "shrink", "clothes", "shirt", "coat", "curtains",
                     "car", "bike", "bicycle", "laptop", "phone", "computer", "rent", "landlord",
                     "flat", "radiator", "boiler service",
                     # the heating is the system, not one machine: "the heating is broken" is the
                     # boiler entry's, while "my dryer is not heating" is this one.
                     "the heating", "central heating",
                     # buying one is a shopping question, and a symptom is a how-to: "is it worth
                     # getting a slow cooker" and "my oven is noisy, is it worth fixing" are not this.
                     # "getting" and "get a" are not here: the decision is asked "should i get it
                     # fixed or get a new one" far more often than "is it worth getting a ...", and a
                     # bare "get" would catch both. "worth getting"/"worth buying" keep the shopping
                     # question out without touching "get it fixed".
                     "worth getting", "worth buying", "shop for", "choose", "choosing", "slow cooker",
                     "pressure cooker", "rice cooker", "air fryer", "dishwasher tablets",
                     "noise", "noisy", "banging", "leak", "leaking", "mould", "musty", "smell",
                     "smells",
                     # nor is a machine that will not drain: "i need my washing machine fixed, it
                     # won't drain" carries "fixed" and "washing machine", and the filter answer is
                     # the one that helps. The decision is for a machine that runs but is not worth
                     # repairing, not for one with a jammed pump.
                     "drain", "drains", "draining", "wont drain", "won't drain", "pump", "filter",
                     "water everywhere", "not emptying",
                     # and a line that names the part is the part's own row: "how do i replace the
                     # drive belt on my tumble dryer" is the belt, not the decision about the dryer.
                     "belt", "belts", "drive belt", "brush bar", "brushbar", "brush roll",
                     "impeller", "beater bar"),
              bias=2),
        entry("extractor-fan-noisy",
              # "hood" alone is a car's bonnet in American English and "vent" alone is a tumble dryer,
              # a loft or a heating duct, so the hill phrases carry the kitchen and the bare words are
              # refused below.
              (("extractor", "cooker hood", "extractor hood", "kitchen hood", "range hood", "hob",
                "grease filter", "filter", "filters"),
               ("noisy", "loud", "noise", "rattling", "rattle", "vibrating", "buzzing", "humming",
                "grinding", "sucking", "suck", "weak", "clean", "filter", "filters", "grease filter",
                "smells")),
              avoid=("bathroom", "loo", "toilet", "shower", "bath", "fan oven", "car", "cars", "engine",
                     "bonnet", "truck", "van", "bike", "loft", "tumble dryer", "dryer", "heating",
                     "radiator", "air vent", "air conditioning", "aircon"),
              reply=the_filter_of(("extractor", "cooker hood", "extractor hood", "kitchen hood",
                                   "range hood", "hob", "grease filter"),
                                  EXTRACTOR_GREASE_FILTER)),
        # A smell in a place is not the thing the place word usually means: "how do i get rid of the
        # smell in the garage" was a decluttering plan, "...in the shed" was weight loss (the verb), and
        # "...in the boot" was the football boots' studs. The subject is the smell; the place only says
        # where to look. The fridge, the bin and the car keep their own answers below and beside this.
        entry("place-smell",
              (("smell", "smells", "smelly", "smelling", "stink", "stinks", "stinking", "reek",
                "reeks", "reeking", "odour", "odor", "smells like",
                # the phrase rather than the bare word: "the smell in the boot" is a place question,
                # and the bare words alone lose to whichever row owns the place word
                "smell in", "smells in", "smell from", "smells from", "smell of", "stink in",
                "stinks in", "get rid of the smell", "how do i get rid of the smell"),
               ("shed", "garage", "loft", "attic", "cellar", "basement", "cupboard",
                "wardrobe", "spare room", "conservatory", "porch", "hall", "hallway", "utility",
                "utility room", "outhouse", "bin store", "storage room", "room", "rooms", "house",
                "flat", "empty house", "holiday let", "under the stairs", "stair cupboard",
                "bathroom", "bedroom", "kitchen", "landing", "cloakroom", "guest room",
                # a wet room and a shower room are rooms like the rest: on main "the wet room smells"
                # was answered by the hotel-complaint row, because "room" was all it needed
                "wet room", "shower room", "en suite", "ensuite", "wash room",
                # "the boot" on its own is footwear far more often than it is the back of a car, and
                # the boots keep the answer that knows them; only the phrase says a car. golden-boar
                # measured "how do i stop the boot smelling" losing its pair-of-boots answer to this
                # row, and "smell in the boot of the car" still needs to land here.
                "car boot", "boot of the car", "boot of my car", "the boot of", "boot of a car")),
              # the reply is picked from what the line says the smell is: a place that smells of wee
              # wants the enzyme cleaner, a loft that smells of mice wants the droppings check, and a
              # kitchen that smells of chips wants the pan of water, while a smell nobody can name is
              # the source hunt below.
              _place_smell,
              avoid=("fridge", "freezer", "bin", "bins", "bin day", "wheelie", "car", "cars", "van",
                     "washing machine", "dishwasher", "drain", "drains", "plughole", "toilet", "loo",
                     "sink", "shower", "bath", "mould", "mold", "mildew", "damp", "condensation",
                     "smoke", "gas", "carbon monoxide",
                     # A smell of a named substance is a hazard, not a mystery: the person already
                     # knows what they are smelling, so the answer is what to do about that and not how
                     # to hunt for a source. The paint row, the petrol-fumes row and the oil row all
                     # keep their lines this way - "the garage smells of petrol" was getting bicarbonate
                     # of soda in a bowl, and "how do i stop the garage smelling of paint" lost the
                     # cure-it-and-air-it answer it already had.
                     "petrol", "petrol fumes", "diesel", "fuel", "oil", "paraffin", "kerosene",
                     "paint", "paint fumes", "painting", "painted", "thinner", "white spirit",
                     "solvent", "bleach", "ammonia", "chlorine", "sewage", "rotten", "rot",
                     # a smell *of* a known thing names its own cause, so the person is not hunting
                     # for a mystery: the laundry answer knows sweat, the cupboard answer knows mice,
                     # and the airing card is what vomit in a bedroom wants. bright-plum found these
                     # three losing their answers to this row, and probed the words as a group:
                     # "my shed smells of mice", "the garage smells of sweat", "my hallway smells of
                     # cabbage", "my basement smells of fish", "my bedroom smells of pee" and "how do
                     # i get rid of the smell of sick in the car" are all unchanged by them.
                     "sweat", "sweaty", "mice", "mouse", "vomit", "sick", "urine", "pee",
                     "curry", "cabbage", "weed", "fish",
                     # a musty smell is a damp question, and the damp answer knows what to look for
                     "musty", "damp smell", "smells of damp", "smell of damp", "dog", "cat", "pet", "my breath", "breath",
                     "feet", "foot", "body", "armpit", "mouth", "kettle", "oven", "microwave",
                     "food", "cooking", "fish", "fridge freezer", "tap", "water", "hoover", "vacuum",
                     "washing", "clothes", "mattress", "sofa", "carpet",
                     # a boot of a car and a pair of boots are one word, and the bare plural in an
                     # avoid list stood this row down on its own lines ("boots" is a loose form of
                     # "boot", so even "the boot" met it), so the boots are named as phrases
                     "my boots", "my shoes", "my trainers", "these boots", "these shoes",
                     "pair of boots", "football boots", "work boots", "walking boots",
                     "hiking boots", "shoes", "shoe", "trainers", "slippers", "sandals",
                     "wellies", "welly",
                     # a smell that is cooking, burning or being made nice has its own answer: this
                     # one is for a smell nobody can name the source of
                     "cabbage", "burnt", "burning", "burn", "fried", "frying", "bacon", "curry",
                     "garlic", "spices", "boiled", "drains smell", "nice", "nicer", "lovely",
                     "fresh", "fresher", "freshen", "pleasant", "good", "better"),
              bias=2),
        # A soft thing that has taken a smell up is not the room it is in, and it is not the pet
        # either: on main `1abf1c69` "my sofa smells of dog" was answered "A dog - how long has it been
        # with you?" and "my car smells of wet dog" got the skid answer. The bare noun keeps its own
        # cleaning card ("my rug smells" is still the carpet shampoo) - it is only this row's when the
        # line names what it smells of.
        entry("soft-thing-smell",
              (("soft furnishing", "carpet", "carpets", "rug", "rugs", "sofa", "sofas", "settee",
                "settees", "armchair", "armchairs", "cushion", "cushions", "curtain", "curtains",
                "car seat", "car seats", "car", "cars", "mattress",
                "carpet smells of", "carpet smells like", "carpets smell of", "rug smells of",
                "rug smells like", "sofa smells of", "sofa smells like", "settee smells of",
                "settee smells like", "armchair smells of", "cushion smells of", "cushions smell of",
                "curtains smell of", "car smells of", "car smells like", "seat smells of",
                "mattress smells of", "mattress smells like"),
               ("smells of", "smells like", "smells", "smell of", "stinks of", "stinks", "stink",
                "reeks of", "reeks", "reeking", "pong", "whiffs", "whiff", "scent")),
              _soft_smell,
              # damp, mould, smoke and fuel are their own answers, and the pet, the bin and the machine
              # each keep the question about the animal or the appliance
              avoid=("damp", "musty", "mould", "mouldy", "mold", "moldy", "mildew", "condensation",
                     "smoke", "smoky", "cigarette", "gas", "petrol", "diesel", "fuel", "paint",
                     "bleach", "bin", "bins", "washing machine", "washer", "dryer", "dishwasher",
                     "fridge", "freezer", "oven", "microwave", "kettle", "drain", "drains",
                     "sink", "toilet", "loo", "new car", "nice", "fresh", "freshen", "clean",
                     "remove", "get out", "how do i clean", "wash", "shampoo", "vacuum",
                     # a stain on a soft thing already has a method on main, and the upholstery and
                     # mattress rows give the scrap-and-rinse-cold and the do-not-soak-the-foam that
                     # the enzyme cleaner drops: "the sofa smells of sick" and "my car seat smells of
                     # milk" were both a fuller answer before this row reached them.
                     "sick", "vomit", "vomited", "vomiting", "milk", "wine", "coffee", "tea",
                     "juice", "spilt", "spilled", "spilling", "stain", "stains", "stained",
                     # a smell of burning in a car, or off a machine, is a fault and not a thing to
                     # clean: "my car smells of burning" and "my car smells like burning rubber" were
                     # both handed the enzyme cleaner for upholstery. The car row knows the brakes.
                     "burning", "burnt", "burn", "scorching", "scorched", "hot smell",
                     "smells hot", "overheating", "overheated", "brakes", "brake pads", "clutch",
                     "exhaust", "burning rubber", "electrical", "smoke", "fumes")),
        entry("fridge-smell",
              (("fridge", "freezer", "fridge freezer"),
               ("smell", "smells", "smelly", "stink", "stinks", "odour", "odor", "reek")),
              "Throw out whatever has gone off, then wash the shelves and drawers with hot soapy water "
              "and dry them. The usual hiding places are the door seal, which needs wiping in the folds, "
              "and the drain hole at the back, which you can clear with a cotton bud or a bit of wire. A "
              "small bowl of bicarbonate of soda on a shelf takes out what's left; change it monthly.",
              guard=_not_the_food_in_the_fridge),

        # --- appliances and the quick jobs round them ---------------------------
        entry("appliance-noise",
              (("fridge", "refrigerator", "freezer", "fridge freezer", "washing machine", "washer",
                "dishwasher", "dish washer", "tumble dryer", "dryer", "oven fan", "oven", "kettle",
                "microwave", "vacuum", "hoover",
                # a plain fan is an appliance that hums, and it was reaching the tinnitus answer
                # before the gate and a shrug after it; the oven fan and the extractor are avoided
                # below because each names a machine with its own answer
                "fan", "fans", "ceiling fan", "desk fan", "pedestal fan", "floor fan"),
               ("hum", "hums", "humming", "buzz", "louder",
                "buzzing", "rattle", "rattles", "rattling", "click", "clicks", "clicking",
                "knock", "knocks", "knocking", "bang", "bangs", "banging", "squeak", "squeaks",
                "squeaking", "squeal", "squeals", "squealing", "grind", "grinds", "grinding",
                # A screech and a shriek are a squeal, and a clunk is a rattle: the washer's own
                # table has read them for a while, so "my washing machine is screeching" was
                # answered while "my tumble dryer is screeching" was met with a nod, which is one
                # sound reaching two answers depending on the machine.
                "screech", "screeches", "screeching", "shriek", "shrieks", "shrieking",
                "scream", "screams", "screaming", "clunk", "clunks", "clunking",
                "clank", "clanks", "clanking",
                "gurgle", "gurgles", "gurgling", "whirr", "whirring", "scrape", "scraping",
                "vibrate", "vibrating", "shaking", "thump", "thumping", "whine", "whining",
                "tick", "ticking", "whistling") + NOISE_WORDS),
              _appliance_noise,
              # a fridge, a washer, a boiler and a laptop fan all have their own answers elsewhere, and an
              # appliance that also smells, smokes or leaks is a fault question, not this one: the
              # noise is the least of it
              avoid=("fridge", "freezer", "refrigerator", "washing machine", "washer", "boiler",
                     "radiators", "radiator", "heating", "laptop", "computer", "pc",
                     # a games console that roars is cooling itself, in `console-noisy`
                     "playstation", "ps5", "ps4", "xbox", "console", "games console", "nintendo",
                     "phone", "car", "engine", "mot", "neighbour", "neighbours", "music", "tv",
                     "radio", "fan heater", "smell", "smells", "smelling", "smelly", "stink",
                     "stinks", "burning", "burnt", "burn", "smoke", "smoking", "smoky", "fire",
                     "spark", "sparks", "sparking", "gas", "fumes", "leak", "leaks", "leaking",
                     "leaked", "flood", "flooding", "wiring", "sockets",
                     # a crowd is not a fan motor: "the fans were shrieking at the ref" is people
                     # in a stand, and it must not be told to oil a bearing
                     "ref", "referee", "crowd", "stadium", "terrace", "sang", "seat", "seats",
                     # a cooker hood has its own entry (`extractor-fan-noisy`), so this table never
                     # claims one: a hood is noisy when it is only greasy, and that entry answers
                     # the filters, the duct and the smell as well
                     "extractor", "extractor fan", "cooker hood", "extractor hood", "range hood",
                     "kitchen hood", "hood", "hoods", "hob", "grease filter",
                     # a fan in a bathroom is that room's extractor and has the timer and cleaning
                     # answers above: this table's "a fan hums because that is what it does" was
                     # answering "why is my bathroom fan so loud" instead of them
                     "bathroom", "loo", "toilet", "shower", "shower room", "wet room", "en suite",
                     "ensuite")),
        # A machine that will not stop is not a laundry-sorting question: "my washing machine keeps
        # running" was answered "sort by colour, not by kind of garment" on main `16d3db7a`, because
        # sorting-wash keys on "washing" and the "running" that means a colour bleeding. Nothing
        # answered the fault itself, and "the washing machine wont stop filling" got the dead-machine
        # card (check the fuse), which is the wrong end of the fault.
        entry("washing-machine-wont-stop",
              (("washing machine", "washer", "washer dryer", "washing mashine", "drum"),
               ("keeps running", "keep running", "kept running", "runs forever", "running forever",
                "running for hours", "wont stop", "won't stop", "wont stop filling", "wont stop beeping",
                "keeps filling", "keep filling", "doesnt stop", "doesn't stop", "never stops",
                "wont turn off", "won't turn off", "keeps going", "stuck on a cycle",
                "stuck on the same cycle")),
              "A machine that will not stop is waiting for something it cannot do: switch it off at the "
              "wall and turn the water off at the valve behind it, then clean the filter behind the kick "
              "plate and check the drain hose is not kinked. Set it to drain or spin only and start it "
              "again. If it fills even with the water off, the water-level pressure switch has failed, "
              "which is an engineer's job.",
              # sorting-wash keys on "washing" and the "running" of a colour, and the two rank level,
              # so the fault only wins on bias: the registry's domain order would hand the line back
              bias=2,
              # a machine that will not drain, will not spin or will not open its door has its own
              # answer; this one is the cycle that never ends
              avoid=("door", "doors", "locked", "lock", "wont open", "won't open", "smell", "smells",
                     "leak", "leaking", "noise", "noisy", "banging", "rattling", "which", "best",
                     "buy", "sort", "colours", "colors", "whites", "darks")),
        entry("washing-machine-wont-drain",
              # "cycle" on its own meant the washing machine to this entry, so "the water cycle"
              # in a school question was a drum that would not empty. The appliance or its cycle
              # has to be named, which every real line does.
              (("washing machine", "washer", "drum", "spin cycle", "wash cycle"),
               ("drain", "draining", "wont drain", "won't drain", "empty", "water", "pump",
                # "blocked" is how most people say it, and the words were not here, so
                # "the washing machine is blocked" was the laundry-sorting card
                "blocked", "blockage", "clogged", "not emptying", "backed up", "backing up")),
              "The filter is the usual culprit, behind the little kick plate at the bottom front: put a "
              "shallow bowl and a towel down, unscrew it slowly and pull out the coins and hair. Then "
              "check the drain hose behind the machine isn't kinked or pushed too far into the standpipe. "
              "If it still won't empty, the pump needs replacing, which is a cheap part and a half-hour "
              "job for an engineer.",
              # the laundry-sorting row keys on "washing" and ranks level with this one, so the
              # fault only wins on bias - "the washing machine is blocked" was the sorting card
              # otherwise, exactly as `washing-machine-wont-stop` says below
              bias=2,
              # "stuck" used to be in the key above, and "the door is stuck" is the door question:
              # the drain entry now passes on a door, a lock or a shut drum. Water *coming out* is the
              # leak entry's line, not a blocked filter, so it passes on that too.
              # the fault has to be named, not just the water: the guard above is what keeps the
              # litres, the heat and the smell out, and this row's bias only wins a tie it reaches
              guard=_a_machine_that_will_not_empty,
              avoid=("buy", "which", "best", "door", "doors", "locked", "lock", "shut", "open",
                     "leak", "leaks", "leaked", "leaking", "coming out", "pouring out", "pouring",
                     "flooded", "flooding", "underneath",
                     # a car's screen wash is a washer too: "my washer jets are blocked" is the
                     # car, so the car's own words go with the guard that asks for a fault
                     "jet", "jets", "nozzle", "nozzles", "windscreen", "windshield",
                     "screen wash", "washer fluid", "washer jet", "washer jets")),
        # The filter is the job people ask about on its own, and the smell entry was taking it. It is
        # a small hatch and a bowl, not a service wash, so it gets its own answer.
        entry("washing-machine-filter",
              # "filter" is a word here as well as the parts, so a follow-up that names only the part
              # is in play; the reply stands down unless the machine is this one
              (("washing machine", "washer", "washer dryer", "washing mashine", "filter", "filters"),
               ("filter", "filters", "filter cap", "pump filter",
                # the pump sits behind the same kick plate, so "how do i clean the drain pump" is this
                # job; a bare "pump" is not here because "my washing machine pump is noisy" is the
                # banging-and-walking row's line
                "drain pump", "pump cap", "clean the pump", "clear the pump")),
              # the extractor hood's grease filter is the other filter a house has, and on a tie it
              # was winning this line: a machine named in the line is this row's question
              bias=3,
              reply=the_filter_of(("washing machine", "washer", "washer dryer", "washing mashine"),
                                  WASHING_MACHINE_FILTER)),
        # The detergent drawer is the third place a machine grows black, and it is the only one a
        # person can take out and scrub, so it is its own job: "how do i clean the washing machine
        # drawer" was the door-seal answer, which is no help with a drawer full of softener.
        entry("washing-machine-drawer",
              (("washing machine", "washer", "washer dryer", "washing mashine", "laundry",
                "detergent drawer", "soap drawer", "powder drawer", "dispenser drawer",
                "fabric softener drawer"),
               # no bare "clean" or "smell" here: "how do i clean my washing machine" and "my washing
               # machine smells" are the service wash, and with those two words in this group the
               # drawer took both, and the filter question with them
               ("drawer", "drawers", "dispenser", "compartment", "detergent", "soap", "powder",
                "trap", "gunk", "slimy", "sticky", "scrub")),
              "Pull the drawer right out until it stops, press the release catch in the middle of the "
              "softener compartment, and take it to the sink. Lift out the cap and the siphon tube, "
              "soak everything in hot water with a little washing-up liquid or a dishwasher tablet for "
              "half an hour, then scrub the corners with an old toothbrush. Reach into the housing left "
              "in the machine and scrub the top and the back of it too, because that is where the black "
              "grows, and run an empty hot rinse before the next load. Use powder now and then and "
              "leave the drawer open between washes: softener is what feeds it.",
              # the black in the rubber seal is the mould row's answer, and a drawer that is a kitchen
              # or a bedside drawer is not this one
              avoid=("door seal", "rubber", "seal", "mould in the seal", "black around the door",
                     "kitchen", "bedside", "desk", "chest of drawers", "cutlery", "sock", "socks",
                     "fridge", "freezer", "wardrobe", "bathroom cabinet",
                     # "where do i put the detergent" is the compartment question, not this job:
                     # taking the drawer out and scrubbing it answers a different ask, and the
                     # consumables row has the three compartments
                     "where do i put", "where do the", "where does", "where should i put",
                     "which compartment", "what compartment", "where do the tablets",
                     # a dishwasher has a detergent drawer too, and its own clean is another job
                     "dishwasher", "dish washer", "tumble dryer", "tumble drier"),
              # the mould row keys "detergent drawer" and "drawer" too and sits earlier in the file,
              # so the drawer needs the higher bias to win the tie "how do i clean the detergent
              # drawer" makes
              bias=3),
        # A machine that is scaled up leaves white flakes on the washing and takes longer to heat, and
        # the question was a punt: nothing in the knowledge base talks about limescale in a washer.
        entry("washing-machine-descale",
              (("washing machine", "washer", "washer dryer", "washing mashine", "washing",
                "laundry", "drum"),
               ("descale", "descaling", "descaler", "limescale", "scale", "scaled", "scaling",
                "calcium", "hard water", "chalky", "white flakes", "flakes on the washing")),
              "Run a descaler through an empty drum on the hottest cycle: a 500g bag of citric acid "
              "from a hardware shop, or a washing-machine descaler, straight into the drum rather than "
              "the drawer, at 60C or 90C, then a rinse cycle with nothing in it. In a hard water area "
              "that is every three months; where the water is soft, once a year is enough. White "
              "flakes on dark washing and a machine that takes longer to heat are the two signs it is "
              "due, and a filter full of grit after the cycle is normal. Skip vinegar: it is hard on "
              "the rubber and the seals, and citric acid does the job better.",
              avoid=("kettle", "coffee machine", "coffee", "dishwasher", "shower head", "shower",
                     "iron", "steam iron", "tap", "taps", "boiler", "dehumidifier", "humidifier",
                     "water softener", "hot tub", "pool", "fish tank", "aquarium", "toilet",
                     "buy", "best", "which", "brand", "price", "cheap", "worth it"),
              # the mould row keys "get rid" and "rid of" for a machine, so "how do i get rid of
              # limescale in my washing machine" tied with it and lost on file order
              bias=3),
        # A dryer's lint filter is the one job nobody does until the load takes two goes, and the
        # line was read back at the person ("Noted: the tumble dryer filter is full of fluff").
        entry("tumble-dryer-filter",
              # "filter" is a word as well as the parts, so a follow-up naming only the part is in play
              (("tumble dryer", "tumble drier", "tumble", "dryer", "drier", "filter", "filters"),
               ("filter", "filters", "fluff", "lint", "blocked", "clogged", "clean", "cleaning",
                "full",
                # pet hair is what a lint filter is full of: "how do i get dog hair out of the tumble
                # dryer" was told a dryer is worth it if you would use it three times a week
                "hair", "pet hair", "dog hair", "cat hair", "fur")),
              # a bare "hair" used to be avoided here so that a "hair dryer" never reached a tumble
              # dryer's filter; the two phrases do that job on their own, and the word itself is now
              # what the row is asked with
              avoid=("hairdryer", "hair dryer", "hair drier", "washing machine", "washer", "dishwasher",
                     # "is a tumble dryer worth it for pet hair" is a buying question that names the
                     # hair, and the filter row now keys the same words
                     "worth", "worth it", "should i", "do i need", "need a",
                     "buy", "which", "best", "price", "repair", "not heating", "wont heat",
                     "not spinning", "makes a noise", "squeak"),
              # the filter is this row's job even when the hair is the subject: "how do i get dog hair
              # out of the tumble dryer" is the same claw-out-the-fluff job with a different noun
              bias=3,
              reply=the_filter_of(("tumble dryer", "tumble drier", "tumble", "dryer", "drier"),
                                  TUMBLE_DRYER_FILTER)),
        entry("washing-machine-door-stuck",
              (("washing machine", "washer", "dryer", "tumble dryer"),
               ("door", "stuck", "wont open", "won't open", "locked", "shut", "open")),
              "Give it three or four minutes: the lock holds until the drum has stopped and the water has "
              "drained. If there's water inside, run a drain or spin cycle first. When it's empty and "
              "still locked, most machines have an emergency release: a small plastic tag or cord behind "
              "the filter hatch that you pull down while pushing the door. Don't force the handle, "
              "because the catch breaks before the door does.",
              avoid=("buy", "which", "best")),
        entry("dishwasher-wont-drain",
              (("dishwasher", "dish washer", "dishdrawer", "dish drawer"),
               # no bare "water", "empty" or "emptying": "the dishwasher is leaking water" is a
               # leak under the machine, "wont fill with water" is the inlet valve, and
               # "how much water does a dishwasher use" is neither, and empty/emptying is what
               # you do to a finished load.
               ("drain", "draining", "wont drain", "won't drain", "not draining", "emptying",
                "not emptying", "wont empty", "won't empty", "full of water", "water in the bottom",
                "water left in", "standing water", "puddle", "left in the bottom",
                "sitting in the bottom",
                # "blocked" is how most people say it
                "blocked", "blocked up", "blockage", "clogged")),
              "Start with the filter: it twists out of the bottom of the drum, and a rinse under the hot "
              "tap with a check for glass or a label in the sump usually fixes it. Then look at the drain "
              "hose where it joins the waste under the sink, because a kink or a blockage there leaves "
              "exactly that water in the bottom. If it hums and still won't empty with both clean, the "
              "drain pump needs swapping, which is a cheap part and a quick job for a repairer.",
              # the cleaning and cloudiness lines belong to the service-wash answer
              avoid=("smell", "smells", "clean", "cleaning", "cloudy", "streaks", "salt", "rinse aid",
                     "buy", "which", "best", "leak", "leaking", "fill", "fills", "filling",
                     "how much water", "uses", "use a lot", "efficient",
                     # "emptying" has to stay in the key for "the dishwasher isnt emptying", and
                     # that one word also reaches the unloading question
                     "empty the dishwasher", "emptied", "unload", "unloading", "quickly")),
        # A dishwasher that has water where water should not be is a fault, not the drain
        # question: the row above keeps "leak" out of its own key on purpose, and nothing else
        # held the line, so "water is coming out of the bottom of my dishwasher" fell to "I'm
        # listening - say more". The mirror of the washing-machine leak row, because the two
        # machines leak in the same places: the door seal and the filter at the front, the inlet
        # and drain hoses underneath.
        entry("dishwasher-leak",
              (("dishwasher", "dish washer", "dishdrawer", "dish drawer"),
               ("leak", "leaking", "leaks", "leaked", "puddle", "puddles", "dripping", "flooding",
                "water coming out", "water coming from", "water coming", "water under",
                "water underneath", "water all over", "water on the floor", "on the floor",
                "all over the floor", "coming out of the bottom", "underneath it", "under it",
                "wont stop leaking", "won't stop leaking")),
              "Turn it off at the wall and shut the water off at the little isolator tap under the "
              "sink, then get the water up - a shallow tray and a towel is enough for a slow one. "
              "Water at the front of the door is usually the door seal or the filter, so twist the "
              "filter out and check the seal for food or a split; water underneath is the inlet or "
              "drain hose where it joins the machine or the waste, so check those joints first. "
              "Leave it off until that seal or joint is fixed: a leak from inside the machine "
              "itself is a repairer's job.",
              # a machine that will not drain, a load that comes out wet, a smell and a box of
              # salt all have their own rows, and a new one to buy is the shopping answer
              avoid=("buy", "which", "best", "cheapest", "price", "cost",
                     "wont drain", "won't drain", "not draining", "not emptying", "wont empty",
                     "won't empty", "full of water", "water in the bottom", "standing water",
                     "left in the bottom", "filter", "pump", "empty", "emptying",
                     "smell", "smells", "smelly", "cloudy", "streaks", "salt", "tablet",
                     "rinse aid", "still wet", "wont dry", "won't dry", "how much water",
                     "uses", "use a lot", "install", "installing", "fit a", "fitting"),
              bias=1),
        entry("machine-consumables",
              (("salt", "tablet", "tablets", "powder", "detergent", "liquid", "pod", "pods",
                "capsule", "capsules", "rinse aid", "rinse-aid", "softener", "conditioner",
                "dishwasher cleaner"),
               ("where do i put", "where do the", "where do i add", "where do i fill",
                "where does", "where should i put", "where to put", "where in the",
                "which compartment", "what compartment", "top up", "topup", "how much",
                "which bit", "run out", "ran out", "refill", "where", "put", "fill", "go",
                "goes",
                # a follow-up that names only the next consumable is the same question about the
                # same machine: "where does the salt go in my dishwasher" then "and the rinse aid?"
                "and the", "what about the", "and what about the", "how about the")),
              _where_the_consumable_goes,
              # a cloudy load, a wet load and a machine that will not drain all have their own rows,
              # and a box of salt to buy is the shopping answer
              avoid=("cloudy", "streaks", "white marks", "film", "smell", "smells", "smelly",
                     "wont dry", "won't dry", "still wet", "wet dishes", "drain", "draining",
                     "leak", "leaking", "buy", "which", "best", "price", "cost", "how often",
                     "repair", "broken", "not working", "error"),
              guard=_a_machine_consumable, bias=1),
        entry("dishwasher-wet",
              (("dishwasher", "dish washer", "dishdrawer", "dish drawer"),
               ("dishes are wet", "dishes still wet", "dishes come out wet", "leaves the dishes wet",
                "leaves everything wet", "not drying", "isnt drying", "isn't drying", "wont dry",
                "won't dry", "still wet", "wet dishes", "wet after", "water on the dishes",
                "water left on", "comes out wet", "everything is wet"),
               # "the dishes" is a third thing the line says, so a drying fault outranks the
               # cooking.fix-dry entry that keys the bare word "dry"; the ask gate keeps a line
               # that only names the load out of it.
               ("dishes", "dish", "plates", "glasses", "crockery")),
              "Rinse aid and salt first: without rinse aid the water clings in drops, so fill the "
              "rinse-aid compartment and set it to 4 or 5, and top up the salt. Use the hottest "
              "programme you have and open the door an inch when it finishes so the steam escapes; "
              "plastic always dries worse than china. If the load is still soaked, clean the filter "
              "and check the spray arms turn freely.",
              # A drain fault, a leak, a smell and a cloudy load all have their own entries; this is
              # only the load that comes out wet from an otherwise working wash.
              ask=("wet", "drying", "dry", "damp", "water", "soaked"),
              avoid=("wont drain", "won't drain", "not draining", "drain", "draining",
                     "full of water", "water in the bottom", "standing water", "leak", "leaking",
                     "smell", "smells", "smelly", "cloudy", "white marks", "streaks", "clean",
                     "cleaning", "worth", "replace", "repair", "quote", "cost", "buy", "which",
                     "best",
                     # A noise named in the same line is the noise table's answer, however wet the
                     # plates are: "my dishwasher is humming but the dishes are wet" is one fault
                     # named twice and the hum is the one the person is worried about. Only the
                     # noise words go here. A smell or a drain word would leave both dishwasher
                     # entries standing aside, and "Got it." is worse than either answer.
                     "hum", "hums", "humming", "hummed", "noise", "noisy", "loud", "louder",
                     "rattle", "rattles", "rattling", "squeak", "squeaks", "squeaking",
                     "bang", "bangs", "banging", "knock", "knocks", "knocking", "grind",
                     "grinding", "vibrate", "vibrating", "clunk", "clunks", "clunking")),
        # The timer on the boiler, in a house where the heating is not on a smart stat. Not the
        # phone's timer and not the thermostat's own schedule: the programmer with the two channels.
        entry("heating-programmer", (("boiler", "heating", "thermostat", "boiler timer",
                                      "timer on the boiler",
                                      "boiler programmer", "heating programmer", "heating timer",
                                      "programmer", "programmer on the boiler", "timer for the "
                                      "heating", "heating times", "heating clock",
                                      # the clock and the schedule live on the programmer, and people
                                      # name whichever box is on the wall: "how do i set a thermostat
                                      # schedule", "how do i change the time on my thermostat"
                                      "thermostat schedule", "thermostat times", "thermostat timer",
                                      "time on the thermostat", "thermostat clock",
                                      "clock on the thermostat", "heating schedule",
                                      "heating programme", "heating program"),
                                     # The clock is on whichever box is on the wall, and the way a
                                     # person asks for it names the thermostat and the time, not the
                                     # word "programmer": "how do i change the time on my thermostat"
                                     # and "my thermostat clock is wrong" were both answered with the
                                     # room temperatures until these phrases were keyed here.
                                     ("timer", "set", "setting", "change", "times", "time",
                                      "programme", "program", "adjust", "clock", "am", "pm")),
              "Set the clock and the day on the programmer first, because every on and off time you "
              "enter is measured from it. Then give each channel two blocks: heating on about half an "
              "hour before you get up and off when you leave, then on again before you come back and "
              "off at bedtime, and the hot water channel set to a morning and an evening block. Put "
              "the room thermostat at 18 to 19C while you are in and 15 to 16C overnight, and let the "
              "thermostat do the switching rather than turning the programmer up and down. A combi "
              "boiler with a smart thermostat wants the heating channel left on constant, because the "
              "thermostat is doing the timing.",
              # A clock, a schedule or a timer is what makes a line this entry's, and the setting of
              # the temperature is not: "how do i set my thermostat" has no clock word, so it keeps
              # the number answer, while "how do i change the time on my thermostat" and "my
              # thermostat clock is wrong" come here. Without the gate, "set" plus "thermostat" was
              # enough for this row to take every thermostat line in the house.
              ask=("time", "times", "clock", "clocks", "schedule", "schedules", "programme",
                   "program", "programmer", "timer", "timing", "am", "pm", "on and off",
                   "what time", "the time", "change the time", "set the time"),
              # the temperature of the flow is energy-bill's dial question, and a boiler that is
              # faulty or leaking is a fault answer
              avoid=("phone", "app", "oven", "washing machine", "dishwasher", "sprinkler", "light",
                      "christmas", "fault", "error", "not working", "broken", "temperature",
                      "flow", "pressure", "leak", "leaking", "noise", "noisy", "smell")),
        # The dial on the boiler has one number on it and no bill in the question: "how do i lower
        # my boiler temperature", "what should the flow temperature be", "how hot should my boiler
        # be" were a plumber hedge on main, because the bill answer wanted a bill word and the
        # programmer answer stands down on "temperature" and "flow" on purpose.
        entry("boiler-flow",
              (("boiler flow", "boiler flow temperature", "flow temperature", "flow temp",
                "boiler temperature", "boiler thermostat", "boiler dial", "boiler setting",
                "temperature on the boiler", "temperature of the water in the boiler",
                # the word order is the person's, and "what temperature should the boiler be" puts
                # the box first: the dial word in the second group is what makes it a dial question
                "boiler", "boilers"),
               ("temperature", "hot", "hotter", "cooler", "lower", "turn down", "turn it down",
                "flow", "what temperature", "how hot", "number", "what number",
                "set", "setting", "should", "what", "how hot", "change", "adjust", "efficient",
                "efficiency", "55", "60", "condensing", "combi")),
              "Set the flow temperature on the boiler dial to 55 to 60C. That is the temperature of "
              "the water going round the radiators, and the lower it is the less gas each hour costs, "
              "because a condensing boiler only recovers its waste heat with a cool return. If the "
              "house is slow to warm, go to 65C and turn the room thermostat down again rather than "
              "going higher than that. A hot water cylinder stays at 60C whatever the heating is set "
              "to, so the two numbers are not the same dial.",
              # a boiler that is not working, or is leaking, noisy or smoking, is a fault answer
              avoid=("pressure", "leak", "leaking", "fault", "error", "not working", "broken",
                     # one radiator's valve is its own row, not the boiler's dial
                     "turn down a radiator", "turn down the radiator", "one radiator",
                     "rad valve", "radiator valve", "trv", "thermostatic valve",
                     "too hot", "very hot", "overheat", "overheating", "scald", "scalding",
                     "noise", "noisy", "smell", "fumes", "carbon monoxide", "pilot light",
                     "service", "serviced", "servicing", "engineer", "install", "replace",
                     "how much", "price", "bill", "tariff", "cost"),
              # a named sound is the noise row's question: "the boiler buzzes when the hot water
              # runs" holds "boiler" and "hot" and was answered with the flow-temperature dial.
              guard=not_a_sound),
        # Where the plate with the model and serial number is. "where is the model number on my
        # boiler" was the flow-temperature card, because the dial row keys "number" and "boiler",
        # and the same question about a washing machine, a fridge and an oven was a search hedge:
        # the place is the answer, and it is a place on every appliance.
        entry("where-is-the-model-number",
              (("model number", "model no", "model num", "serial number", "serial no",
                "rating plate", "data plate", "data badge", "spec plate", "type plate",
                "product number", "benchmark sheet", "benchmark logbook", "benchmark"),
               ("boiler", "boilers", "combi", "washing machine", "washer", "dishwasher",
                "fridge", "freezer", "fridge freezer", "oven", "cooker", "dryer",
                "tumble dryer", "microwave", "vacuum", "hoover", "kettle", "toaster",
                "appliance", "appliances", "the machine", "my machine", "white goods",
                "manual", "user guide", "sticker", "rating plate", "data plate")),
              "It is on a plate or sticker you can read without moving the machine: on a boiler, "
              "under the case near the pipes, behind the drop-down flap or on the side panel, and "
              "the Benchmark sheet in the manual carries the same serial. On a washing machine or "
              "dishwasher it is on the rim inside the door, on a fridge or freezer inside on a "
              "side wall or the inner door, on an oven on the frame or the door edge, and on a "
              "kettle, toaster or microwave underneath. The model number is the short code and "
              "the serial is the longer one - the parts shop or the maker's site wants both, so "
              "photograph the plate once you have found it.",
              # which boiler to buy, and a boiler that is faulty, are other rows
              avoid=("which boiler", "what boiler", "new boiler", "buy", "buying", "replace",
                     "replacing", "price", "cost", "how much", "quote", "efficiency", "size",
                     "kw", "output", "fault", "error", "not working", "broken", "leak",
                     "leaking", "noise", "noisy", "pressure", "service", "serviced")),
        # Turning one radiator down is the valve on that radiator, not the boiler dial: "how do i
        # turn down a radiator" was the bill card on this branch, because "radiator" is in the bill's
        # key and nothing else answers the valve.
        entry("radiator-turn-down",
              (("radiator", "radiators", "rad valve", "radiator valve", "trv", "thermostatic valve",
                "valve on the radiator", "towel rail"),
               ("turn down", "turn it down", "turning down", "lower", "too hot", "hot", "cooler",
                "adjust", "set", "setting", "one radiator", "in the bedroom", "in a bedroom",
                "which way", "number",
                # "how do i turn my bedroom radiator down" puts the room between the verb and "down",
                # so the phrase "turn down" is never there; the word "down" is. The words that say
                # the radiator is too warm are keys too, because that is the same valve.
                "down", "full", "on full", "full blast", "max", "maximum", "on high",
                "roasting", "scorching", "boiling", "overheating", "cant sleep", "cannot sleep",
                # the other positions of the same head, and the words printed on it: "how do i turn
                # a radiator up" and "how do i turn a radiator off" were both a punt, and "what do
                # the numbers on a radiator valve mean" was the physics of how a radiator heats a
                # room. "turn down" is a phrase, so it never matched "turn a radiator down": the
                # single words go here too. Not the bare "switch" - a follow-up is merged with the
                # line before it, and "how do i switch a radiator off for the summer" plus "and the
                # towel rail" then became a line this row took.
                "up", "turn up", "turn it up", "turning up", "turn", "turning", "turned",
                "off", "turn off", "turn it off", "switch off", "switched off", "off position",
                "numbers", "dial", "trv", "thermostatic", "snowflake", "frost setting",
                "frost mark", "what setting")),
              "Turn the numbered head at one end of the radiator down a notch or two - that is the "
              "valve that sets the room, and the numbers are roughly 2 for 16C, 3 for 18C and "
          "4 for 21C. A bedroom "
              "wants 16 to 18C for sleep, so 2 is usually the setting there, and turning it down is "
              "the way to cool a room that a radiator has made too warm. Leave the plain "
              "valve at the other end alone; it is the balance for the whole system. Turn it to the "
              "snowflake - frost protection, about 7C - in a room nobody uses, and give it until "
          "the next morning, because a radiator takes an hour to show a change. If the head does "
          "not click and the radiator stays as "
              "hot, the pin under it is stuck: take the head off and work the pin free with pliers.",
              avoid=("leak", "leaking", "drip", "puddle", "bleed", "bled",
                 # "down" is a word about the system as well as about the valve: "the radiator is
                 # down on pressure" and "the heating is down to half a bar" are the sealed
                 # system's gauge, and the bare key word pulled them onto this card. The pressure
                 # words stand this row down; heating-pressure answers them.
                 "pressure", "bar", "psi", "gauge", "filling loop", "top up", "topping up",
                 "cold at the top",
                     "cold at the bottom", "not heating", "stays cold", "noise", "banging", "kettling",
                     "buy", "which radiator", "which rad", "which boiler", "which one", "which type",
                     "best", "how many", "size", "boiler", "install", "replace")),
        # A thermostat that says low battery is a how-to, and on this branch the science row about
        # what a battery is took it: "how do i change the batteries in my thermostat" was a chemistry
        # lesson. The cells are behind the front, and the whole answer is which ones and what to do
        # after.
        entry("thermostat-battery",
              (("thermostat", "thermostats", "room thermostat", "boiler thermostat", "hive", "nest",
                "tado", "smart thermostat", "heating controls", "thermostat display"),
               ("battery", "batteries", "low battery", "battery low", "battery flat", "change the "
                "batteries", "replace the batteries", "new batteries", "cell", "cells",
                "goes blank", "blank screen", "keeps losing the signal", "flashing")),
              "Take the front off the thermostat and change the cells: most take two AA or AAA, and "
              "the battery cover is either the whole front pulling off its wall plate, as on a Hive, "
              "or a small slide-out tray at the side. Use alkalines rather than rechargeables, because "
              "a rechargeable cell sits at 1.2V and the unit reads that as low. After new cells give "
              "it five minutes to find the hub again, then check the time and schedule, which is what "
              "a dead battery loses.",
              # a battery that is being thrown away is the bin answer, and a phone or a watch is
              # their own
              avoid=("bin", "recycle", "recycling", "dispose", "disposal", "phone", "iphone", "watch",
                     "car", "key fob", "smoke alarm", "doorbell", "camera")),
        entry("heating-temperature",
              (("heating", "radiator", "radiators", "thermostat", "house", "flat", "home", "room",
                "rooms", "bedroom", "bedrooms", "living room", "sitting room"),
               ("temperature", "how warm", "how hot", "warm enough", "too cold", "freezing", "cold",
                "keep it at", "set it at", "set the", "keep the heating", "all day", "overnight",
                "at night", "timer",
                # "when should i put the heating on" was a search hedge: the number answer was here,
                # and the words a person uses for the switch were not in either group. What turns it
                # on is a room below 18C, not a date, so both belong to this entry.
                "put the heating on", "put the heating", "turn the heating on", "turn the heating off",
                "turn the heating", "switch the heating", "heating on yet", "heating off",
                # the possessive forms belong in this group as well as the subject group: group one
                # has already spent the word "heating" by the time this group is read, so the phrase
                # never matched and "how do i turn my heating down" reached no row at all. They are
                # kept whole on purpose - the bare phrase is in the follow-up context of a
                # cold-radiator chat and pulled the next turn onto the room temperature.
                "my heating up", "my heating down", "our heating up", "our heating down",
                "turn my heating up", "turn my heating down", "turn our heating up",
                "turn our heating down", "turn down my heating", "turn up my heating",
                "turn down our heating", "turn up our heating",
                "turn it on", "turn it off", "have the heating",
                # "how do i set my thermostat" and "what temperature should i set my thermostat to"
                # are this row's question, but "set" alone only counted as "set it at"/"set the",
                # so the reset row took them and answered with a pinhole. The ways a person says
                # "put it at a number" go here, and the reset stays the reset.
                "set my thermostat", "set the thermostat", "change my thermostat",
                # "what should i set my bedroom thermostat to at night" was the gym answer, because
                # the question is one bare "what should i set" and nothing else carried it
                "bedroom thermostat", "thermostat at night", "set my bedroom",
                "what should i set my", "what should i set the",
                "change the thermostat", "thermostat setting", "thermostats", "what temperature",
                "what temp", "what should i set", "how should i set", "set it to", "set the heating",
                "set the heating times", "set the heating timer", "heating timer", "heating times",
                "programme the heating", "program the heating")),
              "18C is the usual living-room setting and 16C for bedrooms, with 20C to 21C for a baby's "
              "room, for someone ill or elderly, or for anyone who feels the cold. Go by the room, not "
              "the calendar: put it on when the living room drops below about 18C, or when you are "
              "sitting still and feel cold, and then set it and leave it, turning it down at night or "
              "when you're out rather than running it low all day. If the rooms never get to 18C with "
              "the heating on, that's a boiler or radiator problem rather than a thermostat one.",
              # bleeding, noise, leaks, pressure, bills and feeling the cold are all separate questions
              avoid=("bleed", "bleeding", "bottom", "top", "noise", "noisy", "bang", "banging", "kettle",
                     "leak", "leaking", "drip", "dripping", "pressure", "boiler", "landlord", "bill",
                     "bills", "cheaper", "cost", "price", "money", "saving", "save", "feel", "feeling",
                     "always", "hands", "feet", "shivering", "tired", "thyroid",
                     # "home with a cold" is an illness, "back home from Greece, 30 degrees" is a
                     # holiday report, and "a small flat and i work all day" is about the day
                     "flu", "cough", "stuck", "company", "greece", "spain", "holiday", "raining",
                     "rain", "sun", "heatwave", "work all day", "out all day",
                     # A house left empty wants the away answer (low, and the water off), not a
                     # setting for a room someone is sitting in: "should i leave my heating on when
                     # i go on holiday" and "...so the pipes dont freeze" are the away and frost
                     # questions, and both have their own row.
                     "go away", "going away", "away for", "when im away", "when i am away",
                     "while im away", "on holiday", "empty house", "house is empty", "nobody in",
                     # the cooling row's question: keeping the heat out, not setting a number
                     "keep the heat out", "heat out", "stop the sun", "sun heating", "block the sun",
                     "the sun coming in", "sun comes in", "sun through",
                     "pipes", "pipes freeze", "pipes dont freeze", "pipes from freezing",
                     # a room at 39 is a heat emergency, not a thermostat setting
                     "room temperature is", "39", "40", "41", "42", "fever",
                     # a cooking temperature, a hot bath, a fault code or a thermometer reading is
                     # not the setting for the house
                     "oven", "cook", "cooking", "roast", "bake", "chicken", "meat", "bath", "water",
                     # "room temperature" is a recipe's phrase as well as a thermostat's: "should
                     # eggs be at room temperature" was told the living-room setting, and the
                     # bedroom row hands its own food lines on, so the food words stand this down.
                     "egg", "eggs", "butter", "milk", "cheese", "dough", "yeast", "batter",
                     "chocolate", "cake", "yoghurt", "yogurt", "defrost", "thaw",
                     "not working", "broken", "fault", "error", "thermometer", "sick", "unwell",
                     "garage",
                     # a heating that will not come on is the boiler's answer, not a setting
                     "wont", "won't", "come on", "coming on", "wont come on", "stuck on",
                     "not coming on", "no heating",
                     # the clock, the schedule and the on and off times live on the programmer, and
                     # "how do i change the time on my thermostat" was getting the room temperatures
                     "change the time", "set the time", "the time on", "clock", "clocks",
                     "clock is wrong", "clock wrong", "schedule", "schedules", "set the schedule",
                     "the schedule for", "programmer",
                     # a flat battery has its own row: "how do i change the thermostat battery"
                     # was the room temperatures, because the key holds "change the thermostat"
                     "battery", "batteries", "low battery", "blank screen", "display blank",
                     "keeps losing the signal"),
              # two of the words above are in the key for the ordinary shape of the question, so a
              # line has to say something about the heat as well as the place or the day
              # "freezing" and "at night" are not in the ask list: a person who says "my bedroom is
              # freezing at night" wants the room warm, which is heat-a-room's answer, while "how warm
              # should a bedroom be" is the number question and asks with "how warm"
              ask=("temperature", "how warm", "how hot", "warm enough", "keep it at", "set it at",
                   "keep the heating", "leave the heating", "leave it on", "heating on", "thermostat",
                   "degrees", "timer", "overnight", "too cold",
                   # the switch and the calendar are the same question as the setting: "when should
                   # i put the heating on", "should i put the heating on yet", "should i turn the
                   # heating off at night". "at night" on its own is not here on purpose - "my bedroom
                   # is freezing at night" wants heat-a-room.
                   "put the heating", "turn the heating", "switch the heating", "heating off",
                   "heating on yet", "turn it on", "turn it off", "have the heating",
                   # a possessive is the same question and it was a punt: "how do i turn my heating
                   # down" reached no row at all, because this gate knows only "the heating"
                   "turn my heating", "turn our heating", "my heating up", "my heating down",
                   "our heating up", "our heating down", "turn down my heating", "turn up my heating",
                   "turn down our heating", "turn up our heating")),
        # A bare "water" made "why is my boiler not heating water" a leak: the leak has to be
        # described (a drip, a puddle, water under it), not just mentioned.
        entry("boiler-leak",
              ("boiler", ("drip", "dripping", "drips", "leak", "leaking", "leaks", "puddle",
                          "underneath", "overflow", "water under", "water coming", "water everywhere",
                          "water all over", "spraying", "spurting",
                          # "water is coming out of my boiler" and "how do i get water out of my
                          # boiler" are the same leak with the verb in the middle, so the phrase
                          # "water coming" alone never reached them
                          "water is coming", "water coming out", "water out", "water is dripping",
                          "water leaking", "water pouring", "water is pouring", "water coming from")),
              "Turn the boiler off at the wall switch (not at the fuse board, you want the pump to run on "
              "for a minute first), put a bowl under it and turn the water off at the stopcock if it's "
              "more than a drip. A leak from the boiler casing itself is a Gas Safe engineer's job: don't "
              "take the cover off, and don't keep resetting it. Water running from the pressure relief "
              "pipe outside means the pressure is too high, which needs looking at too.",
              avoid=("buy", "best", "cost", "price", "install", "new", "landlord", "tenant",
                     # a boiler with cold water is not a boiler with a puddle under it
                     "not heating", "isn't heating", "isnt heating", "heating the water", "no hot water",
                     "no heating")),
        entry("leak-under-sink",
              (("sink", "under the sink", "waste", "trap", "u-bend", "ubend", "pipe"),
               # "wet patch" and "puddle" are how a person describes water they found rather
               # than saw fall: "wet patch under the sink" reached the child-wets-bed card, and
               # "the wet patch under the sink is spreading" reached a card about going away.
               # The row that answers a puddle answers a wet patch too.
               # The second key is what the water is doing, never where it is: "sink",
               # "under the sink" and "underneath" are in the first key, so putting the place in
               # both halves made any line that names the place a match with no water word in it
               # at all - "mould under the sink" and "mould in the cupboard under the sink" left the
               # mould card for this one. A line that names where the water is already matches on
               # the first key, so the second key only has to say it is water.
               ("leak", "leaking", "drip", "dripping", "water", "puddle", "fix", "wet patch",
                "wet", "soaked", "pool", "pooling", "spreading", "damp patch", "damp")),
              "Dry everything, put a bowl under the trap and run the tap to see where the water appears. "
              "A drip at a plastic joint is nearly always a hand-tight nut: give it another quarter turn, "
              "no more, because overtightened plastic splits. If it's the trap, unscrew it, clean out the "
              "gunge, check the rubber washer is seated and put it back. Wrapping PTFE tape on a plastic "
              "thread makes it worse, not better.",
              avoid=("blocked", "smell", "slow", "drain",
                     # an ear is not a sink: "water trapped in my ear" is the ear's own answer
                     "ear", "ears",
                     # and "how do i waste less water" is the saving, not the trap: a bare
                     # "waste" is in this row's key, so the saving words have to stand it down
                     "less water", "save water", "saving water", "wasting water", "waste less",
                     "water use", "water usage", "water bill", "use so much water")),
        # A room under water had no card at all: "i flooded the bathroom" and "water everywhere in
        # the kitchen" reached the intake form - "Got it. Is there anything you'd like a hand
        # with?" - because every water row here keys the thing that is leaking (a tap, a trap, a
        # radiator) and the flood has no thing, only a place. The place is what this one keys,
        # with a flood word beside it, so the leak rows keep their own lines.
        entry("flooded-room",
              (("flood", "flooded", "flooding", "under water", "water everywhere",
                "ankle deep", "inches of water", "deep in water", "swimming in water"),
               ("bathroom", "kitchen", "flat", "house", "room", "rooms", "floor", "floors",
                "carpet", "carpets", "hall", "hallway", "cellar", "basement", "bedroom",
                "utility", "downstairs", "upstairs", "everywhere", "lino", "floorboards")),
              "Turn the water off first: the stopcock is usually under the kitchen sink, and if "
              "water is near a socket or a light, switch that circuit off at the consumer unit. "
              "Then stop whatever is running, bail and mop, and get air moving with a fan and an "
              "open window - a floor or skirting that stays wet a day warps and grows mould. "
              "Photograph it before you clear up, and ring the insurer and whoever owns the "
              "building today if it came through the ceiling.",
              # the garden, the road and the car have their own flood rows, and a washing
              # machine or a toilet that has done this is a machine with a fault, not a room
              avoid=("garden", "lawn", "greenhouse", "shed", "car", "van", "road", "street",
                     "village", "river", "field", "fields", "warning", "risk",
                     # a cellar that fills when it rains is water coming in from outside: the
                     # stopcock is no use there, and it is not the same repair. It has a row of
                     # its own now, so the whole of the outside is fenced off here rather than
                     # one word of it.
                     "rain", "rains", "raining", "rainwater", "storm", "storms", "winter",
                     "groundwater", "water table", "cellar", "basement", "outside", "drain",
                     "drains", "back door", "under the door", "doorway",
                     "insurance quote", "washing machine", "dishwasher", "toilet",
                     "loo", "radiator", "boiler", "tap", "taps", "sink")),
        # Water coming in from outside is the other half of the same night: "my cellar is
        # flooding" and "it is raining and the cellar is flooding" were a shrug, and the burst-pipe
        # card above is wrong for them, because the stopcock stops nothing in a storm. The drain,
        # the doorway and the insurer are what a person needs, and not standing in it.
        entry("water-coming-in",
              (("flood", "flooded", "flooding", "floods", "water", "wet", "seeping", "seeps",
                "rising", "inches deep", "ankle deep", "filling", "coming in", "coming under",
                "coming through", "getting in"),
               ("cellar", "basement", "rain", "rains", "raining", "rainwater", "storm", "storms",
                "outside", "groundwater", "water table", "drain", "drains", "back door",
                "under the door", "doorway", "up through the floor")),
              "Water coming in from outside is not a stopcock: it stops taps, not rain or a "
              "rising water table. Stay out of a cellar with sockets in it, or switch the whole "
              "supply off at the consumer unit first, and pump or wet-vac the water out rather "
              "than mopping it about. Sandbags or a flood door across the doorway help tonight, "
              "photographs help the insurer, and a drain that backs up in a storm is the water "
              "company's to clear.",
              # the indoor flood, the garden, the road and the car keep their own rows
              avoid=("stopcock", "washing machine", "dishwasher", "toilet", "loo", "radiator",
                     "boiler", "tap", "taps", "sink", "pipe", "pipes", "burst", "car", "van",
                     "road", "street", "village", "river", "lawn", "greenhouse", "shed",
                     "garden", "yard", "insurance quote", "warning", "risk", "sandbag"),
              # a line that has the outside in it and a flood with it is this card whatever else
              # it also mentions: "my basement fills with water when it storms" and "rain water is
              # coming into my cellar" were a science lecture and a plumbing musing on the score
              bias=2),
        # The fly and smell-nice answers used to exist twice, once here and once in cleaning.py,
        # worded differently; home.py keeps them because it also owns the house facts around them.
        entry("fruit-flies",
              (("fruit fly", "fruit flies", "fruitfly", "gnats", "flies", "fly"),
               ("kitchen", "bin", "get rid", "rid", "stop", "bananas", "everywhere", "plague",
                "sink", "drain", "fruit", "bowl", "traps", "around", "how do i",
                # The noun with no kitchen word in the line: "there are flies in my house",
                # "a fly keeps landing on me", "flies all over the bedroom". The verb is fenced
                # by the guard below, so a place or an annoyance is enough here.
                "house", "home", "flat", "room", "rooms", "bedroom", "landing", "land", "lands",
                "on me", "keep", "keeps", "buzzing", "buzz", "swarming", "swarm", "air",
                "window", "windows", "in here", "indoors", "coming in")),
              "Put a little cider vinegar or red wine in a glass with a drop of washing-up liquid: they "
              "fly in and sink. Then take away what they are breeding in - the ripe fruit (into the "
              "fridge for a week), the bottles and the bin, and the plughole, which gets a kettle of "
              "boiling water at night. The glass catches the rest in a day or two.",
              # a suitcase that comes back damaged is not a fly in the kitchen: "how do i protect
              # my suitcase when flying" was reaching this card on "fly" + "how do i". The phrases
              # say "flying" without the bare word, because the matcher reads "fly" as that form of
              # it and "there is a fly in my kitchen" would lose the card (reviewer fair-orca).
              # A fly tip is a dumped mattress in a lay-by, and the council collects it: "how do i
              # report fly tipping" was told to put cider vinegar in a glass.
              avoid=("fly to", "flight", "flights", "when flying", "by plane", "on a plane",
                     "checked in", "suitcase", "suitcases", "luggage", "checked bag", "hold bag",
                     "holiday", "airport", "insect bite", "butterfly", "butterflies", "dragonfly",
                     "flight home", "fly tip", "fly tipping", "fly-tip", "fly-tipping", "tipping",
                     "tipped", "dumped", "dumping", "mattress", "lay-by", "fly poster",
                     # the fear of it is not a fly in the kitchen either: with the grief row's
                     # "get over" fenced off, "how do i get over a fear of flying" fell to this
                     # card and got cider vinegar, so the phrase is named here.
                     "fear of flying", "scared of flying", "afraid of flying",
                     # a zip fly is not an insect: "how do i put a zip fly in" got cider vinegar
                     # in a glass, because a fly is exactly what this row is about.
                     "zip", "zips", "zipper", "zippers", "zip fly",
                     # A plane, not a gnat, and the matcher reads "flying" as "fly": "im flying
                     # at 6am" got the cider vinegar, and the bare word cannot fence it off
                     # because "there is a fly in my kitchen" would lose its card with it. The
                     # phrase is the signal, so the phrases are what stand the row down.
                     "am flying", "flying at", "flying out", "flying home", "flying back",
                     "flying off", "flying from", "flying into", "flying tomorrow",
                     "flying next", "flying this", "flying in the morning", "flying on",
                     "fly out", "fly back", "fly home", "fly at", "flying with", "flying over",
                     "anxiety about flying", "nervous about flying",
                     # a kite is flown, not caught: the bare noun "fly" in this key answered
                     # "how do i fly a kite" with cider vinegar in a glass. entertainment.py's
                     # fly-a-kite row owns the kite lines.
                     "kite", "kites",
                     # a pet that flies with you is not a fly in the kitchen: "how do i fly with
                     # a dog" was told to put cider vinegar in a glass, and travel.py's
                     # pet-travel row is the answer
                     "dog", "dogs", "cat", "cats", "puppy", "puppies", "kitten", "kittens",
                     "pet", "pets", "rabbit", "ferret", "hamster", "parrot", "budgie"),
              # the verb is a shape, so the list of phrases above is no longer what holds it out
              guard=_the_fly_is_not_a_verb,
              report=True),
        entry("house-smell-nice",
              (("house", "flat", "home", "room", "living room", "hallway", "bedroom"),
               ("smell nice", "smell nicer", "smelling nice", "smell good", "smell fresh",
                "nice smell", "nicer smell", "fresh smell", "smell better", "nice scent", "fresh",
                "freshen", "smells", "smell", "smelly", "stinks")),
              "Open windows at both ends of the flat for ten minutes; that shifts more than anything you "
              "spray. Then wash the things that hold smell: bedding, cushions, the bath mat, the bin lid. "
              "Bicarbonate of soda on the carpet, left an hour and vacuumed, lifts stale air, and a pan "
              "of water with lemon peel and a cinnamon stick simmered for ten minutes does the rest. "
              "Air fresheners mask it; the fix is finding the source, often the bin, the drain or damp.",
              avoid=("damp", "musty", "mould", "mold", "drain", "gas", "burning", "smoke"),
              ask=("nice", "nicer", "fresh", "freshen", "home", "house", "flat", "bedroom")),
        entry("gutters",
              (("gutter", "gutters", "downpipe", "downpipes", "fascia"),
               ("clean", "cleaning", "blocked", "overflowing", "often", "leaves", "sagging", "drip")),
              "Twice a year, after the leaves fall and again in spring: scooped out by hand in gloves "
              "from a stable ladder, with the rubbish into a bag rather than down the drain. Then flush "
              "each downpipe with a hose to check it runs. If water still spills over the edge on a wet "
              "day, the run of the gutter has dropped or the downpipe is blocked at the bottom, not the top.",
              avoid=("buy", "cost", "install", "replace", "quote")),
        # "how do i fix a leaky gutter" was a shrug: the row above answers the cleaning and the
        # overflow, and its words are clean/blocked/overflowing, so a leak on a dry day matched
        # nothing. A leak in one place and water over the edge are two different repairs.
        entry("gutter-leak",
              (("gutter", "gutters", "downpipe", "downpipes", "fascia"),
               ("leak", "leaks", "leaky", "leaking", "drip", "dripping", "drips", "joint", "joints",
                "seal", "sealing", "sealant", "hole", "holes", "crack", "cracked", "fix", "repair",
                "water", "waterfall", "pouring")),
              "A leak is nearly always a joint or a hole, and it is a dry-day job: a leaking joint at "
              "the stop end or between two lengths is cleaned out, dried and sealed with gutter "
              "sealant; a hole or crack is covered with a self-adhesive flashing strip pressed on "
              "over a clean, dry surface, which lasts a few years. Before any of that, check the "
              "downpipe is not blocked - water backing up finds the weakest joint and pours out "
              "there - and re-clip a run that has sagged so it falls towards the downpipe, about "
              "1cm in 3 metres. Never do it off a ladder in the wind or on your own: a ladder on "
              "wet ground is the fall that puts people in hospital.",
              avoid=("clean", "cleaning", "clear", "clear out", "scoop", "leaves", "blocked",
                     "overflowing", "cost", "costs", "price", "quote", "install", "replace",
                     "new gutters")),
        # A fence that came down in the wind is one of the commonest winter questions in the whole
        # home domain and it reached nothing: "my garden fence is falling down" and "my fence post
        # has rotted" both had a shrug, "how do i fix a fence panel that blew down" was turned down
        # honestly, and "how do i stop my fence blowing down again" was read as a letter to a friend.
        # The repair, the windproofing and the rotten post are three answers, so they are three rows.
        entry("fence-repair",
              (("fence is falling down", "fence has fallen down", "fence fell down", "fence blew down",
                "fence has blown down", "fence panel", "fence panels", "broken fence",
                "fence is broken", "fence is leaning", "wobbly fence", "fence is wobbly",
                "fence post", "fence posts", "post has rotted", "posts have rotted",
                "fence is sagging", "fence sagging", "fence has sagged",
                "gate is hanging", "gate has dropped"),
               ("fence", "garden", "wind", "storm", "repair", "fix", "replace", "rotten", "rotted",
                "concrete", "blown", "fell", "leaning", "gate", "put back", "again")),
              "A panel that came out in the wind is usually a post that has moved, not the panel, so "
              "check the posts are upright with a spirit level before you fix it back: a new panel on "
              "a rotten post goes over again. Replace a rotted post base with a concrete repair spur, "
              "or set a new post 600mm into the ground in Postcrete, and brace it until it is solid.",
              avoid=("cost", "quote", "how much", "neighbour", "neighbor", "who owns", "boundary",
                     "fence paint", "paint it", "stain", "creosote",
                     # a depth is a fourth fence question and has its own row below: without these,
                     # "how deep should fence posts go" read as a repair on the words "fence posts"
                     "deep", "depth", "deep enough", "foot down", "feet down")),
    ]
