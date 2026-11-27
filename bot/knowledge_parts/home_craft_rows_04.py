"""Rows 4 of 10 of `home_craft.entries()`: `oven-racks` .. `plaster-dries`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _paint_for_the_room,
    _wallpaper_for_the_room,
    re,
)


def rows():
    from ..knowledge.home import (
        MACHINE_BURNING, MACHINE_DEAD, MACHINE_LEAKING, NORMAL_CUTOUT, _SMOKING_THING,
        _TAKING_PAINT_OFF, _alarm_nuisance, _appliance_cutting_out, _consumer_unit,
        _kettle_will_not_stop, _machine_fault, _smoking_appliance, entry
    )
    from ..knowledge.lookup import a_sanding_job
    return [
        # The racks are the dirtiest part of an oven and the paste is the wrong shape for them: they
        # lift out, so they can be soaked, and the cavity answer ("coat the inside, not the elements")
        # was what "how do i clean oven racks" got. Same job, one thing named differently.
        entry("oven-racks",
              (("oven racks", "oven rack", "oven shelves", "oven shelf", "wire racks", "wire rack",
                "grill rack", "grill racks", "rack in the oven", "racks in the oven",
                "shelves in the oven", "shelf in the oven"),
               ("clean", "cleaning", "cleaned", "grease", "greasy", "scrub", "wash", "soak",
                "burnt", "stuck", "filthy", "dirty")),
              "Lift them out and soak them in the bath or a big sink in hot water with a good squirt "
              "of washing-up liquid and a couple of tablespoons of bicarbonate of soda, for an hour "
              "or overnight: the burnt-on grease then comes off with a nylon scourer or foil. If they "
              "fit, a dishwasher does most of it, and a bin bag with a splash of ammonia left outside "
              "overnight lifts the worst without scrubbing.",
              # a burnt hand on a rack is the safety module's, and a rack that has snapped, sags or
              # will not sit level is a repair, not a cleaning job
              avoid=("hand", "hands", "finger", "fingers", "thumb", "arm", "wrist", "scald",
                     "blister", "burnt my", "burned my", "wont fit", "won't fit", "broken",
                     "sagging", "wobbly", "wont sit", "won't sit", "fell", "falls", "loose",
                     "dishwasher not draining", "dishwasher filter", "wine", "spice", "spices"),
              ask=("clean", "cleaning", "cleaned", "grease", "greasy", "scrub", "wash", "soak",
                   "burnt", "stuck", "filthy", "dirty"),
              bias=1),
        # The second group is the cleaning sense of the line, and the reader says it as a state as
        # often as a job: "the oven is greasy", "my oven is dirty" and "the oven is disgusting" all
        # reached the greeting module, because the key held only the job words `clean` and `grease`
        # and none of those lines had one. A state word is the same question. The door glass keeps
        # its own row above, which this one stands down for through the `glass` words below.
        entry("oven-clean", ("oven", ("clean", "cleaning", "grease", "greasy", "burnt", "smoke",
                                      "filthy", "dirty", "dirt", "grime", "grimy", "grubby",
                                      "stained", "stains", "scrub", "wipe", "ick", "disgusting")),
              "Make a paste of bicarbonate of soda and water, coat the inside (not the elements), leave "
              "it overnight and wipe it out with a damp cloth and a little vinegar. It takes some "
              "scrubbing but doesn't fill the kitchen with fumes like caustic oven cleaner. The racks "
              "soak in hot water with a dishwasher tablet while the paste works.",
              # A burn is answered by the safety module, and the line that follows it is still about the
              # burn: "i burnt my hand on the oven" then "should i put butter on it" was getting the
              # oven-cleaner paste because "oven" and "burnt" were in the conversation. Cleaning the
              # inside of an appliance is never what someone with a burnt hand or a blister is asking.
              # and "burn" alone is a cooking line, not a cleaning one: "my roast burnt in the oven"
              # wants nothing to do with the paste, so the cleaning sense has to be in the line too.
              avoid=("hand", "hands", "finger", "fingers", "thumb", "arm", "arms", "wrist", "skin",
                     "scald", "scalded", "blister", "butter", "myself",
                     # a line that asks whether the grease is dangerous wants an answer to that, not
                     # the method: "is a dirty oven a fire risk" was handed the paste instead
                     "fire", "fire risk", "catch fire", "dangerous", "danger", "safe", "unsafe",
                     "hazard", "a risk",
                     # the door glass is its own row above, and it names the glass
                     "glass", "panes", "pane", "window", "door glass"),
              ask=("clean", "cleaning", "cleaned", "cleaner", "grease", "greasy", "scrub", "wipe",
                   "smoke", "smokes", "smoking", "smells", "smell", "get off",
                   "burnt bits", "burnt on", "burnt stuff", "burnt grease", "use to clean",
                   # how people describe the state rather than the job: "burnt marks on the oven",
                   # "the bottom of the oven is black and burnt", "my oven door glass is filthy".
                   # Without these the line left the bake entry (which should not have it) and
                   # landed on a shrug.
                   "marks", "stains", "black", "stuck on", "scorched", "charred",
                   "filthy", "dirty", "grime", "filth", "grubby", "ick", "disgusting",
                   # the state said as a sentence rather than a job: "the bottom of my oven is
                   # burnt" named no cleaning word at all and left the bake entry, which answered
                   # with foil over a cake. "is burnt" is the shape; a bare "burnt" stays out, so
                   # "my roast burnt in the oven" keeps its cooking answer.
                   "is burnt", "burnt on the bottom", "burnt bottom", "burnt floor",
                   "oven floor", "inside is burnt", "is black", "burnt inside",
                   # "how do i get burnt off the bottom of my oven" is the same job said as a
                   # removal: the safety module reads "get burnt" as an injury and answered with
                   # twenty minutes under the tap, and this is the entry that takes the line once
                   # the burn word stands in front of an "off".
                   "burnt off", "off the bottom", "off the floor", "get rid of")),
        # "is a dirty oven a fire risk" is a yes-or-no question about the grease, and the cleaning
        # method is not an answer to it: the paste went to a line that asked about danger. It is a
        # question about tonight, so the answer says how it usually starts and what is not needed.
        entry("oven-grease-risk",
              (("oven", "cooker", "grill", "hob", "air fryer", "cooker hood"),
               ("fire", "fire risk", "catch fire", "dangerous", "danger", "risk", "risky",
                "safe", "unsafe", "hazard", "hazardous")),
              "Yes, if it is greasy: a thick layer of grease and burnt crumbs on the base, the "
              "door seal or the grill pan is what catches, and it usually starts when a spill or a bit "
              "of foil drops onto the element the next time the oven is on. It does not go up on its "
              "own, so it is not an emergency tonight: clean the base and the seal when it is cold, "
              "keep the grill pan clear, and never leave a grill or a chip pan unattended. If it does "
              "catch, close the door, switch it off at the wall and smother the pan with a lid or a "
              "fire blanket - never water on a fat fire.",
              bias=2,
              # the grease is what the yes is about, so the line has to say the oven is dirty: "is my
              # oven dangerous" on its own could be a gas smell, and that has no one answer
              ask=("dirty", "grease", "greasy", "greasy bits", "filthy", "grime", "grimy", "grubby",
                   "crumbs", "burnt", "stains", "stained", "disgusting")),
        # An appliance that smokes is a small fire or a greasy one, and the person wants to know what
        # to do tonight. The safety module keeps its fire card for flames and for smoke at room scale
        # (see APPLIANCE_SMOKE in bot/modules/safety.py), so this is the answer for one thing that
        # smokes. It leads with off at the wall, because the card used to be the only thing that said
        # anything and it said "leave the building and ring 999" about a toaster.
        entry("appliance-smoking",
              (_SMOKING_THING, ("smoke", "smokes", "smoking", "smoky", "smokey", "sparks",
                                "sparking", "scorch", "scorched",
                                "smells like burning", "smell of burning", "smells of burning",
                                "burning smell", "smells burning", "smell burning",
                                # The past tense is how people tell you what happened: "my iron
                                # smelt of burning" named nothing this entry held, so it fell
                                # through to a shrug.
                                "smelt of burning", "smelt like burning", "smelt burning",
                                "smelled of burning", "smelled like burning", "smelling of burning")),
              _smoking_appliance,
              # A burn or a scald in the same line is the safety module's: "smoke came out of the oven
              # when i burnt my hand" is about the hand. The room-scale words belong to the fire card,
              # and the non-appliance smoke (a bonnet, a chimney, a barbecue) is not this answer.
              avoid=("hand", "hands", "finger", "fingers", "thumb", "arm", "arms", "wrist",
                     "skin", "scald", "scalded", "blister", "myself", "the house", "the flat",
                     "the kitchen", "hallway", "stairs", "bonnet", "chimney", "exhaust",
                     "barbecue", "bbq", "cigarette", "cigarettes", "joint", "weed",
                     "chiminea", "firepit", "fire pit",
                     # Flames are not smoke, and the advice is not the same: "there are flames coming
                     # out of the plug socket" must not be told to unplug it. The safety module's fire
                     # card is for flame words and for smoke at room scale, so any of them stands this
                     # answer down and leaves the line to that card (or, where nothing matches, to the
                     # same shrug main gave: neither answer is worse than the wrong one).
                     "flames", "on fire", "caught fire", "alight", "ablaze", "blazing",
                     "pouring out", "billowing", "everywhere"),
              # "smells" alone is a musty machine, which has its own answer, so only the burning
              # sense of the word is a key here: "my washing machine smells" is not a fire.
              ask=("smoke", "smokes", "smoking", "smoky", "smokey", "sparks", "sparking",
                   "scorch", "scorched", "smells like burning", "smell of burning",
                   "smells of burning", "burning smell", "smells burning", "smell burning",
                   "smelt of burning", "smelt like burning", "smelt burning",
                   "smelled of burning", "smelled like burning", "smelling of burning"),
              bias=1),
        # A smoke alarm that goes off whenever the grill is on is doing its job from the wrong place,
        # and "how do i stop it going off when i cook" is a weekly question, not a fire. The cooking
        # word is what separates it from a real alarm and from the low-battery chirp, which has its own
        # answer: the same sensor that smells toast does not tell you a battery is flat.
        entry("smoke-alarm-nuisance",
              (("smoke alarm", "smoke detector", "fire alarm", "heat alarm", "alarm"),
               ("going off", "goes off", "keeps going off", "set off", "setting off", "triggered",
                "sounds", "sounding", "stop it", "silence it", "wont stop", "won't stop",
                # "my smoke alarm went off for no reason" is the line this row exists for and the
                # past tense was missing, so it fell through to the stock line
                "went off", "gone off")),
              _alarm_nuisance,
              avoid=("chirp", "chirping", "chirps", "battery", "batteries", "beep every",
                     "every few minutes", "test", "real fire", "flames", "smoke in the",
                     "landlord", "rent",
                     # the key has a bare "alarm" in it and "went off for no reason" is what
                     # anybody says about any alarm, so a burglar alarm, a house alarm, a car alarm
                     # and a phone alarm were all told to vacuum the sensing chamber of a smoke
                     # detector. The other alarms are not smoke alarms.
                     "burglar", "burglary", "house alarm", "car alarm", "vehicle alarm",
                     "phone alarm", "alarm clock", "intruder", "security alarm",
                     "security system", "panic alarm", "shop alarm", "office alarm"),
              # An alarm with nothing going on is the same nuisance alarm and the same answer.
              # "my smoke alarm went off for no reason" names no cooking and no steam, so it missed
              # this row and got the stock line, which is the coldest answer to a thing that woke
              # somebody at three in the morning: dust or an insect in the chamber, steam, and a
              # sensor past ten years are what sets a smoke alarm off when nothing is burning.
              ask=("cook", "cooking", "cooked", "toast", "toasting", "grill", "grilling", "oven",
                   "hob", "fry", "frying", "roast", "roasting", "bake", "baking", "shower",
                   "steam", "kitchen", "burning", "burnt",
                   "for no reason", "for no apparent reason", "for no obvious reason",
                   "no reason", "no reason at all", "nothing burning", "nothing was burning",
                   "nothing is burning", "nothing on fire", "no smoke",
                   "no fire", "was no fire", "nothing caught fire", "nothing cooking",
                   "nothing was cooking", "nothings cooking", "wasnt cooking", "wasn't cooking",
                   "not cooking", "randomly", "out of nowhere", "middle of the night",
                   "at 3am", "at 2am", "last night"),
              bias=1),
        # The inside of a slow cooker is not a pan on the hob, and the pan's answer would put the
        # ceramic pot over a flame it is not made for. Two things matter here: the pot cracks if
        # anything cold touches it hot, and the burnt crust on a stew lifts on its own overnight.
        entry("slow-cooker-clean", (("slow cooker", "slow cookers", "slow cooker pot", "crock pot",
                                     "crockpot", "ceramic pot", "slow cooker bowl"),
                                    ("clean", "cleaning", "cleaned", "wash", "washing", "scrub",
                                     "burnt", "burnt on", "baked on", "stuck", "crusted",
                                     "stained", "inside", "pot", "bowl", "dishwasher")),
              "Scrape it out and let the pot cool before anything cold touches it, because a hot "
              "ceramic pot can crack under cold water, and the pot and lid are then usually "
              "dishwasher safe. A crusted pot lifts clean if you soak it overnight with hot water and "
              "a dishwasher tablet or a tablespoon of bicarbonate of soda and wipe it with a sponge, "
              "with nothing abrasive on the glaze. The base is the part you do not wash: unplug it and "
              "wipe it out with a damp cloth.",
              # a slow cooker meal, a slow cooker to buy and a slow cooker that has stopped working
              # are other answers
              avoid=("recipe", "recipes", "meal", "meals", "curry", "chilli", "stew", "soup",
                     "should i buy", "worth it", "buy", "broken", "not heating", "wont heat",
                     "slow cook", "how long", "what can i make"),
              ask=("clean", "cleaning", "cleaned", "wash", "scrub", "burnt", "stuck", "crusted",
                   "stained", "smells", "smell", "dishwasher")),
        # Bread crumbs, not water: a toaster has live elements in it even when it looks cold, so the
        # answer is to empty it out dry. "How do i clean a toaster" was a shrug on main.
        entry("toaster-clean", (("toaster", "toasters"),
                                ("clean", "cleaning", "cleaned", "wash", "crumbs", "crumb tray",
                                 "burnt", "stuck", "dirty", "greasy")),
              "Unplug it and tip the crumbs out over the bin, then brush the inside with a dry pastry "
              "brush or an old toothbrush: never put water in a toaster. Wipe the outside with a damp "
              "cloth once it is cold, and empty the crumb tray every week or so, since that is what "
              "smells when it burns.",
              # what to buy, why it trips the power and why the toast is pale are other answers. A
              # toaster that smells of burning is the appliance-smoking entry above, which says to
              # pull the plug first; cleaning is the answer only when the line asks to clean it.
              avoid=("buy", "worth it", "best", "tripping", "not working", "broken", "pale",
                     "uneven", "how long", "browns", "fuse", "smells like burning", "smell of burning",
                     "smells of burning", "burning smell", "smells burning", "smoking", "smoke",
                     "sparks", "sparking"),
              ask=("clean", "cleaning", "cleaned", "wash", "crumbs", "crumb", "burnt", "dirty",
                   "greasy", "inside")),
        # An appliance that takes the power out is a different fault from a fuse in a plug, and the
        # appliance name is what tells them apart: "my kettle keeps tripping the electrics" used to
        # get the socket-fuse answer, so the appliance gets its own entry and outranks it.
        entry("appliance-tripping", (("tripping", "trips", "trip", "blowing", "blows", "cuts out",
                                      "knocking off", "keeps going off"),
                                     ("electrics", "electric", "power", "fuse box", "circuit", "rcd",
                                      "breaker", "trip switch", "mains", "socket")),
              "An appliance that trips the power is usually the appliance itself: unplug it, try it in "
              "a socket on another circuit, and if it trips again stop using it and get it repaired. "
              "Anything that takes the RCD out the moment it is plugged in has a fault to earth, so "
              "don't keep resetting the switch to check - that one needs an electrician.",
              ask=("kettle", "washing", "washer", "dryer", "tumble", "oven", "dishwasher", "fridge",
                   "freezer", "appliance", "toaster", "microwave", "hoover", "vacuum", "iron",
                   "heater", "shower", "immersion", "machine", "tv", "lamp", "extension",
                   "air fryer", "airfryer", "slow cooker", "pressure cooker", "rice cooker",
                   "bread maker", "blender", "food processor", "coffee machine", "kettle"),
              bias=2),
        entry("kitchen-machine-fault",
              (("air fryer", "airfryer", "air-fryer", "slow cooker", "pressure cooker", "instant pot",
                "multi cooker", "rice cooker", "bread maker", "bread machine", "blender",
                "food processor", "stand mixer", "kettle", "toaster", "sandwich toaster",
                "microwave", "coffee machine", "soup maker", "waffle maker", "deep fat fryer",
                "griddle", "panini", "machine", "appliance"),
               MACHINE_BURNING + MACHINE_DEAD + MACHINE_LEAKING),
              _machine_fault,
              ask=("my", "our", "the", "is", "wont", "won't", "keeps", "and", "stopped", "stopping",
                   "why", "what", "how", "should", "smoke", "smokes", "smoking", "spark", "sparks",
                   "heating", "heat", "working", "leaking", "dead", "power", "switch", "on"),
              # a fuse, a tripping circuit or a machine that shuts itself off part way has its own
              # answer above; a food that smokes in the pan is not the machine
              avoid=("fuse box", "rcd", "breaker", "circuit", "guilt",
                     # the laundry, the oven, the fridge and the boiler have their own fault entries
                     "washing machine", "washer", "dryer", "tumble dryer", "laundry", "spin",
                     "drum", "dishwasher", "oven", "fridge", "freezer", "boiler", "hoover",
                     "vacuum", "iron", "pan", "oil", "bbq",
                     "barbecue", "smoker", "cigarette", "vape", "candle", "fire alarm", "chimney",
                     "burnt my", "burnt the", "when it boils", "as it boils"),
              bias=1),
        entry("appliance-normal-cutout",
              (("kettle", "microwave", "oven", "washing machine", "washer", "dishwasher", "dryer",
                "tumble dryer", "toaster", "appliance", "boiler"),
               NORMAL_CUTOUT),
              "A kettle cutting out as the water boils, a microwave stopping when the door opens, an "
              "oven stopping when its timer ends or it reaches temperature, a washer or dryer "
              "finishing at the end of the programme: that is the machine working as designed, and "
              "there is nothing to fix. A fault looks different - it gives up part way through a job "
              "with work left to do, or it stops sooner each time it is used.",
              bias=1),
        entry("appliance-cutting-out",
              (("switches off", "switching off", "switches itself off", "switching itself off",
                "turns itself off", "turning itself off", "cuts out", "cutting out", "stops mid",
                "stopping mid", "stops halfway", "stopped mid", "keeps stopping", "keeps cutting out",
                "keeps switching off", "keeps turning itself off", "wont stay on", "won't stay on",
                "switching off before", "pops up", "popping up", "pops", "popping", "pop up",
                "stops after", "stopped after", "stops every", "stops early", "stops suddenly"),
               ("kettle", "microwave", "washing machine", "washer", "dishwasher", "toaster", "oven",
                "dryer", "tumble dryer", "coffee machine", "iron", "appliance", "hoover", "vacuum",
                "boils", "cycle", "mid cycle", "halfway", "toast")),
              _appliance_cutting_out,
              bias=1,
              # tripping the house electrics is its own answer, a laptop shutting down is the
              # machine's, not an appliance's, and an appliance that stops when its job is done is
              # not faulty at all
              avoid=("trip", "trips", "tripping", "fuse", "fuse box", "rcd", "breaker", "mains",
                     "power cut", "laptop", "computer", "pc", "phone", "iphone", "tv", "router",
                     # a hair dryer is not a tumble dryer, and its cut-out is the grille rather
                     # than the lint filter: "my hair dryer keeps cutting out" was told to empty
                     # the dryer's filter and clear its condenser
                     "hair dryer", "hairdryer", "hair drier")
                    + NORMAL_CUTOUT),
        # A kettle that will not stop is the mirror of the row above, and the mirror needs its own
        # words: "switches off" is the cut-out working too early, so none of those shapes are here.
        # The key is the fault shape first and the kettle second, and every phrase is a boil or a
        # switch, so a pan that boils dry, a toaster that will not stay down and a lamp that will not
        # turn off all keep the row they had.
        entry("kettle-will-not-switch-off",
              (("boils dry", "boiled dry", "boiling dry", "boils away", "boiled away",
                "keeps boiling", "kept boiling", "keeps bubbling", "wont stop boiling",
                "won't stop boiling", "doesnt stop boiling", "never stops boiling",
                "wont switch off", "won't switch off", "doesnt switch off", "never switches off",
                "wont switch itself off", "never switches itself off", "wont turn off",
                "won't turn off", "doesnt turn off", "wont shut off", "doesnt shut off",
                "wont stop", "doesnt stop"),
               ("kettle", "kettles", "boil", "boils", "boiling", "spout", "steam switch")),
              _kettle_will_not_stop,
              bias=2,
              # a hob, a pan, an oven and a TV each have their own answer for a thing that will not
              # turn off; "boils over" or "boils too long" is a full kettle rather than a fault with
              # the switch; and a smell after a boil-dry is the smell row's, which is about scale.
              avoid=("pan", "pans", "saucepan", "pot", "pots", "hob", "hobs", "ring",
                     "rings", "oven", "ovens", "grill", "microwave", "toaster", "air fryer",
                     "slow cooker", "washer", "washing machine", "dishwasher", "dryer", "iron",
                     "boiler", "immersion", "radiator", "heating", "tv", "telly", "light", "lights",
                     "lamp", "phone", "laptop", "fan", "heater",
                     # a full kettle boiling up the spout, and a long boil, are not a failed switch
                     "boils over", "boiled over", "boiling over", "overflow", "too full", "too long",
                     "takes ages", "slow to boil", "boils slowly",
                     # a smell afterwards is the scale-and-standing-water answer, which helps more
                     "smell", "smells", "smelt", "smelled", "smelly", "burnt", "burning", "scorch",
                     # a kettle never holds a dinner: a soup, a stew, a sauce or a pan of pasta
                     # that boiled dry was being told to bin its kettle, and the dish's own
                     # rescue (dish-caught-on-the-bottom) is the answer it needs
                     "soup", "soups", "stew", "stews", "casserole", "curry", "chilli", "chili",
                     "bolognese", "sauce", "sauces", "gravy", "stock", "broth", "porridge",
                     "pasta", "rice", "risotto", "lentils", "beans", "chickpeas", "milk",
                     "hotpot", "tagine", "goulash", "daal", "dal", "dhal"),
              ),
        # "Where is my fuse box" and "how do i reset a trip switch" were the plumber shrug, and "how do
        # i turn off the electricity" was answered with the physics of electric charge. The plug-fuse
        # entry next door is a different job (open the plug, change the 13A fuse), so this one names
        # the box and the switches rather than the fuse, and the fall and guilt-tripping guards stay.
        entry("consumer-unit",
              (("fuse box", "fuse board", "consumer unit", "trip switch", "trip switches", "rcd",
                "breaker", "breakers", "mcb", "main switch", "electricity", "power", "power supply",
                "electricity supply"),
               ("where", "find", "locate", "reset", "resetting", "tripped", "trips", "keeps", "kept",
                "turn off", "turn the power", "turn the power off", "turning off", "switch off",
                "switching off", "switch the power off", "switching the power off", "off", "on",
                "the power", "house", "home", "flat", "lights", "everything", "down")),
              _consumer_unit,
              bias=2,
              # a plug fuse, a socket and an appliance that trips are the fuse-tripping answer; a
              # person who keeps tripping over is a falls question; a laptop or a phone on the mains
              # is a battery; and a boiler, a pump or a shower tripping its own circuit is the
              # appliance answer.
              avoid=("plug", "plugs", "appliance", "appliances", "kettle",
                     "washing machine", "washer", "dryer", "dishwasher", "oven", "toaster", "shower",
                     "boiler", "pump", "immersion", "laptop", "macbook", "computer", "phone", "tablet",
                     "charger", "charging", "battery", "tripping over", "trips over", "trip over",
                     "tripped over", "over my feet", "over her feet", "over his feet", "feet", "foot",
                     "stairs", "rug", "carpet", "pavement", "kerb", "fell", "fallen", "falls",
                     "falling", "guilt tripping", "guilt trip", "guilt trips", "guilt-tripping",
                     "guilt-trip", "tripping me",
                     # a power cut, a power of attorney and a power station are not the switch
                     "cut", "cuts", "outage", "blackout", "attorney", "station", "solar", "wind",
                     "nuclear", "horsepower", "powerful", "washing",
                     # a power station, a steel plant and the grid are the electricity supply's
                     # business, not the box in the hall: "the power plant is closing" was
                     # answered with how to turn the big switch off before working on a socket
                     "plant", "plants", "factory", "factories", "grid", "pylon", "pylons",
                     "closure", "power station", "power stations")),
        entry("fuse-tripping", (("fuse", "plug", "socket", "rcd", "trip", "tripping"),
                                ("blown", "change", "keeps", "not working", "keeps tripping", "stopped",
                                 "dead")),
              "If one socket has stopped working, switch it off at the wall, open the plug and replace "
              "the fuse with one of the same rating (13A for most appliances, 3A for lamps). If the RCD "
              "or a breaker keeps tripping, unplug everything on that circuit and get an electrician: "
              "that's not a DIY job.",
              # a laptop on the mains is a battery question, not a blown fuse, and a person who keeps
              # tripping over is a falls question: "my dad keeps tripping over" was being told to
              # change a 13A fuse.
              avoid=("laptop", "macbook", "computer", "phone", "tablet", "charger", "charging",
                     "battery", "mains", "overnight",
                     # A trip is a journey on most lines: "how do i keep the kids occupied on a road
                     # trip" was told to change a 13A fuse. The bare "trip" in the key stays, because
                     # "the fuse keeps tripping" is this row's own line.
                     "road trip", "day trip", "long trip", "on a trip", "school trip",
                     "camping trip", "trip to ", "trip with", "travelling", "traveling",
                     "tripping over", "trips over", "trip over", "tripped over", "over my feet",
                     "over her feet", "over his feet", "feet", "foot", "stairs", "rug", "carpet",
                     "pavement", "kerb", "doorstep", "walking", "fell", "fallen", "falls", "falling",
                     # guilt tripping is not electrics: "keeps" plus "tripping" was enough, so
                     # "my mum keeps guilt tripping me" was told to change a 13A fuse
                     "guilt tripping", "guilt trip", "guilt trips", "guilt-tripping", "guilt-trip",
                     "tripping me")),
        # "how do i reset a tripped switch" and "a switch on the fuse box tripped" had nothing: the
        # plug-fuse card wants a plug, and the appliance card wants the appliance. A switch that has
        # gone down in the consumer unit is its own job.
        entry("fuse-box-trip",
              # The board's own words only: bare "switch", "power", "electric" and "mains" took "how do
              # i switch my phone off", "i can't switch off from work" and "how do i switch off the
              # boiler" away from the answers main already gave them.
              (("fuse box", "fuse board", "fuse", "consumer unit", "trip switch", "breaker",
                "breakers", "rcd", "rcbo", "circuit", "electrics"),
               ("tripped", "trip", "trips", "tripping", "reset", "gone off", "gone down", "off",
                "keeps", "blown", "board", "consumer unit", "circuit")),
              ("Look at which switch is down before you reset it: a single breaker is one circuit, a "
               "wider switch marked RCD or RCBO is a fault to earth. Unplug everything on that circuit, "
               "push the switch fully down and then back up, and if it holds, plug things back one at a "
               "time until it trips again - that appliance is the fault. If it will not reset with "
               "nothing plugged in, or it is the RCD that keeps going, leave it up and get an "
               "electrician. Never tape a breaker up or fit a bigger one."),
              bias=1,
              # an appliance that takes the power out has its own card, and a plug fuse is a plug
              avoid=("kettle", "washing", "washer", "dryer", "tumble", "oven", "dishwasher", "fridge",
                     "freezer", "toaster", "microwave", "hoover", "vacuum", "iron", "heater",
                     "shower", "immersion", "machine", "plug", "13a", "3a", "13 amp", "3 amp")),
        # Loft insulation is the cheapest thing a house can do to its bills and it was answering with
        # the declutter plan ("clear out the loft") and with the loft conversion's £25,000 to £60,000.
        entry("loft-insulation",
              # "roof" on its own is a subject word here as well as a costing word, so "how much does a
              # new roof cost" and "my roof is leaking" were answered with mineral wool: the roof
              # wording has to be the insulation itself.
              (("loft", "attic", "roof space", "roof insulation", "loft insulation",
                "attic insulation"),
               ("insulate", "insulated", "insulation", "lagging", "lag", "wool", "rolls", "roll",
                "cheap", "cheapest", "cost", "much", "how much", "grant", "draught", "draft")),
              ("Lay mineral wool 270mm deep, which is two layers of 100mm plus one of 70mm criss-crossed, "
               "and it costs about £300 to £600 for a typical semi if you do it yourself: it is the "
               "cheapest thing a house can do to its bills and pays back in a few years. Keep the "
               "eaves clear at the edge for ventilation, do not squash the wool down, and leave a gap "
               "round downlights unless they are marked fire-rated. Bigger jobs - a flat roof, a "
               "dormer, spray foam - want someone registered, and there are often grants."),
              # a bit of a clear-out in the loft is the declutter answer, and a roof that leaks or
              # needs replacing is a repair or a roofer's price, not insulation
              avoid=("clear out", "clearout", "declutter", "clear the loft", "tidy", "junk",
                     "conversion", "convert", "dormer", "extension", "storage", "store things",
                     "board out", "floor it",
                     "leak", "leaking", "leaks", "leaked", "replace", "replacing", "replacement",
                     "repair", "repairs", "tile", "tiles", "slate", "slates", "felt", "flat roof",
                     "repoint", "repointing", "fix", "fixing", "damp", "gutter", "gutters",
                     "chimney", "ridge", "moss")),

        # --- how much of it to buy -------------------------------------------------------------
        # `paint-room` answered any "how much paint" line with its shopping list (filler, sandpaper,
        # a dust sheet) and never said how many litres, which is the question. The quantity words
        # stand the shopping list down and this row answers with the sum and a figure.
        entry("paint-quantity",
              (("paint", "emulsion", "paint tin", "undercoat", "gloss"),
               # how many coats is its own answer already ("two coats on bare plaster, two when the
               # colour changes"), so the word is not here: this row is how many litres
               ("how much paint", "much paint", "how many litres", "litres of paint", "liters of paint",
                "how many tins", "tins of paint",
                "enough paint", "quantity of paint", "how much do i need")),
              _paint_for_the_room,
              # a colour question, a mark on the wall and a how-to-prepare line are other answers, and
              # a painted surface that is peeling or bubbling is a repair question
              avoid=("what colour", "what color", "which colour", "which color", "colour scheme",
                     "mark", "marks", "scuff", "stain", "stains", "peeling", "bubbling", "blistering",
                     "damp", "mould", "mold", "woodchip", "wallpaper", "fence", "shed", "door",
                     "radiator", "kitchen cabinet", "cupboard", "car", "bike", "model", "art",
                     "paint a picture", "nails", "makeup",
                     # what a tin costs is a price question and a live price is not something this
                     # bot has: the honest line about not looking prices up is the right answer there
                     "cost", "costs", "price", "prices", "cheap", "cheapest", "expensive",
                     "how much is", "how much does",
                     # a tin being kept is a storage question, and "keep" is how it is asked: "how do
                     # i store a part used tin of paint" was answered with litres. The gap between
                     # coats is the drying row's figure too, and it read as a quantity because the
                     # coats answer lives in this paragraph's last line.
                     "store", "storing", "stored", "part used", "part-used", "partly used",
                     "half a tin", "leftover", "left over", "lid on", "keep it",
                     "between coats", "how long between", "how long after", "wait between",
                     "second coat", "third coat", "recoat", "re-coat")),
        # A roll of wallpaper is a count of drops rather than a litre figure, and people ask it the
        # same way ("how much wallpaper do i need"), which was a shrug.
        entry("wallpaper-quantity",
              (("wallpaper", "wall paper", "wallcovering", "lining paper"),
               ("how much", "much wallpaper", "how many rolls", "many rolls", "rolls of wallpaper",
                "need", "needs", "buy", "quantity", "enough")),
              _wallpaper_for_the_room,
              # stripping, painting over and a wall that is damp or cracked are other answers
              avoid=("strip", "stripping", "remove", "removing", "woodchip", "paint over", "paint",
                     "damp", "mould", "mold", "crack", "cracked", "peel", "peeling", "feature wall",
                     "which wallpaper", "what wallpaper", "choose", "border", "phone", "laptop",
                     "screen", "wallpaper app", "windows wallpaper",
                     # and a roll's price is the same live price the bot cannot know
                     "cost", "costs", "price", "prices", "cheap", "cheapest", "expensive",
                     "how much is", "how much does"),
              bias=1),
        # A bag of it is not a watering, and "how much" on a material is a sum rather than a price.
        # Paint and wallpaper have their rows above; everything you buy by the tonne, the cubic metre
        # or the bag had none: "how much gravel do i need", "how much bark do i need for a border",
        # "how much topsoil do i need", "how much sand do i need for a patio" and "how much concrete
        # do i need for a fence post" were each a search hedge or another row's answer (a border soak,
        # a laid patio's price). One method answers all of them, because it is the same sum: an area
        # times a depth, then a weight per cubic metre. The depths below are the ones that make the
        # answer right, so they are in the one reply rather than in a row per material.
        entry("bulk-quantity",
              (("gravel", "gravels", "shingle", "pea gravel", "pea shingle", "pebbles",
                "slate chippings", "chippings", "bark", "bark chippings", "mulch", "topsoil",
                "top soil", "compost", "soil", "sand", "sharp sand", "builder's sand", "grit",
                "ballast", "hardcore", "sub base", "type 1", "concrete", "postcrete", "turf",
                "grass seed"),
               # the quantity ask, and the depth one, because "how deep should gravel be" is the
               # same question asked the other way round
               ("how much", "how many", "how deep", "how thick", "depth of", "depth should",
                "much do i need", "much will i need", "many bags", "many tonnes", "many tons",
                "bags of", "tonnes of", "tons of", "cubic", "cubic metres", "cubic feet",
                "square metres of", "coverage", "cover the", "need for", "do i need")),
              "Work it out as a volume: length times width times depth, all in metres. Gravel and slate "
              "chippings go down about 5cm deep, or 10cm if a car drives on them, so a 5m by 3m drive "
              "at 5cm is 0.75 cubic metres - about 1.2 tonnes, or fifty 25kg bags. Bark and mulch are "
              "the same sum at 5 to 7cm over the soil. Topsoil is the deep one: 10 to 15cm for a new "
              "bed, and a 20cm fill in a 3m by 1m raised bed wants 0.6 cubic metres. A cubic metre is "
              "roughly 1.5 tonnes of gravel and about a tonne of soil or compost, and a builder's bulk "
              "bag is about 0.8 of a cubic metre, so check which one the price is for. Turf and grass "
              "seed are sold by area instead: measure the lawn and add 5 per cent for the cuts.",
              # a price is a live figure this bot cannot know, and the laying and choosing of it are
              # their own answers: this row is only the quantity
              avoid=("cost", "costs", "price", "prices", "cheap", "cheapest", "expensive",
                     "how much is", "how much does", "how much would", "laid", "fitted", "quote",
                     "quotes", "hire", "rent", "which", "what type", "what sort", "best type",
                     "what kind", "what colour", "what color",
                     "how do i lay", "how to lay", "lay a", "laying a", "laying the", "install",
                     "installing", "membrane", "weed", "weeds", "weeding", "level", "edge",
                     # "sanding" folds back to "sand", so "how long do i need to leave filler before
                     # sanding" was this row's: it read the sanding as a bag of sand and answered the
                     # volume of a drive. Filler before sanding is paint-drying-time's question, and
                     # the phrases are the shape of a decorating line.
                     "leave filler", "before sanding", "sanding down", "sand it", "sanding filler",
                     "wait before sanding", "filler before",
                     # the sand and bark words are written whole: "sanding" and "barks" fold back to
                     # the material and a bare "bark" here stood the row down on its own subject
                     "sand down", "sandpaper", "sand paper", "sand pit", "sandpit", "play sand",
                     "kinetic sand", "sand castle", "sandwich", "sandwiches",
                     "dog", "dogs", "puppy", "bark at", "why does my dog",
                     "neighbour", "neighbor", "boundary", "who owns",
                     "pay half", "who pays", "cake", "potting bench", "houseplant", "indoor",
                     # a pot of compost is litres per pot, not a cubic metre of ground
                     "pot", "pots", "potting", "container", "containers", "tub", "tubs",
                     "window box", "hanging basket", "hanging baskets", "seed tray", "seed trays",
                     "houseplants",
                     # sowing and planting are their own cards, and so is watering: "how deep should
                     # i sow grass seed" and "how much water does grass seed need" were the volume
                     # sum only because "how much" and "how deep" are the ask
                     "water", "watering", "watered", "sow", "sowing", "sowed", "plant", "planting",
                     "planted", "per square metre", "per sq m", "sandbox", "sand box",
                     "chicken", "chickens",
                     # a post hole is the fence-post card's, which names the depth and the one 20kg
                     # bag of Postcrete that does a post - better than a volume sum
                     "fence post", "fence posts", "post hole", "post holes", "posthole", "postholes",
                     "postcrete", "concrete post", "concrete posts",
                     # a mix is bought by the bag and measured per square metre of wall or bed, not
                     # by the tonne of fill: "how much sharp sand and cement for a block paved drive"
                     # was this row's volume of gravel. The mortar rows answer the mix.
                     "mortar", "mortar mix", "sand and cement", "sharp sand and cement",
                     "building sand and cement", "cement mix", "how much cement", "bags of cement"),
              bias=1,
              # "do i need to sand the wall" is in the ask words ("do i need") and has the key word
              # "sand", so standing the bag-of-sand row down was not enough: this row then worked
              # out the volume of a drive, in gravel. The job that rubs a wall down is read off the
              # line, and the sanding row answers it.
              guard=lambda u: not a_sanding_job(u)),

        # "do i need to sand before painting" was the bag of sand on main ("a 25kg bag of play
        # sand covers about 0.6 square metres"), or the two-coats answer, or gravel by volume: the
        # question is whether the job wants sanding at all, and then how coarse. The verdict opens
        # the reply because that is what was asked, and the grit is in the same sentence.
        entry("sanding-before-painting",
              (("sand", "sanding", "sanded", "sandpaper", "sand paper", "sander",
                "rub it down", "rub down", "rubbed down", "key the surface", "key it"),
               ("before paint", "before painting", "before the paint", "before undercoat",
                "before a primer", "before the primer", "before gloss", "before the gloss",
                "do i need to sand", "should i sand", "need to sand", "have to sand",
                "do i need to rub", "should i rub", "do i need to key", "should i key",
                "sand it first", "sand first", "sand it down", "sanding before",
                "is sanding needed", "is it sanded", "does it need sanding",
                "sand the wall", "sand the walls", "sand the door", "sand the doors",
                "sand the woodwork", "sand the ceiling", "sand the trim",
                "do i have to sand", "should i sandpaper", "need sanding",
                "does it need sanding first",
                # the coat is named so a line asked inside a painting talk ("do i need to sand
                # it first", after "how long between coats of gloss") is about the thing the
                # conversation is on, and answers instead of standing down as another subject.
                "before the next coat", "before the second coat", "before a second coat",
                "before another coat", "before recoating", "between coats", "coats")),
              "Yes, give it a sand first: 120 grit on a block for painted woodwork and 80 to 100 on a "
              "filler patch, with the grain and light enough to take the shine off rather than the "
              "paint, then dust it down and wipe it over with a damp cloth. Old gloss has to be "
              "keyed or the new coat slides off it, and a filled patch has to be flatter than the "
              "wall around it or it shows through. Bare wood wants 120 grit, then 180, and the dust "
              "off before the first coat.",
              # the quantity and the price are the material rows' own question, and a time is the
              # filler and paint cards': this row is the yes and the grit. "between" keeps the
              # gym "sets" reading away from "how long does filler take to set".
              avoid=("how much", "how many", "cost", "costs", "price", "prices", "cheap",
                     "expensive", "bags of", "tonnes", "tons", "cubic", "square metres",
                     # new plaster has its own answer (a mist coat after two to four days) and
                     # sanding it first is not the advice: "do i need to sand a new plastered wall
                     # before painting" read as woodwork was worse than the plaster card.
                     "coverage", "between", "how long", "leave filler", "leave it to",
                     "filler take", "filler set", "drying", "wait",
                     "plaster", "plastered", "plastering", "skim", "mist coat",
                     # which of the two jobs comes first is an order, and the ordering card
                     # answers it: "do i sand first or fill first" was this row's yes.
                     "or fill", "fill first", "filler first", "before i fill", "before filling"),
              # Two jobs joined by "or" and the word "first" is a question about which comes
              # first - "varnish or sand first", "primer or sand first", "do i sand first or fill
              # first" - and this row opens with "yes", which is the wrong shape for it. The
              # ordering card in the fallback pool answers those.
              guard=lambda u: not re.search(r"\bor\b[^.?]*\bfirst\b|\bfirst\b[^.?]*\bor\b",
                                            str((u or {}).get("clean") or (u or {}).get("text") or ""),
                                            re.I),
              bias=3),
        # The commonest paint question is which paint to buy, and nothing answered it: "what paint
        # should i get", "which paint should i buy", "what kind of paint for woodwork", "do i need a
        # primer" and "what is eggshell paint for" were all hedges or a colour shrug. The paint rows
        # around it answer litres, coats, drying, the time a room takes and the shopping list, and
        # none of them names the tin.
        entry("which-paint",
              (("paint", "painting", "repaint", "emulsion", "gloss", "eggshell", "satinwood",
                "satin", "silk", "undercoat", "primer", "priming", "matt", "matte"),
               ("what paint", "which paint", "what kind", "what type", "what sort", "kind of paint",
                "type of paint", "sort of paint", "best paint", "best", "should i get",
                "should i buy", "should i use", "do i need", "need for", "for walls", "for wall",
                "for the walls", "for the wall", "for ceilings", "for a ceiling", "for the ceiling",
                "for woodwork", "for the woodwork", "for skirting", "for doors", "for a door",
                "for plaster", "new plaster", "for a bathroom", "for the bathroom",
                "for a kitchen", "for the kitchen", "for a hallway", "for the hallway",
                "for a radiator", "for kids", "kids room", "washable", "what is", "whats",
                "what's", "eggshell paint for", "gloss or", "or satinwood", "matt or", "silk or")),
              "Emulsion for walls and ceilings: matt for a bedroom or a living room, and a washable "
              "matt or eggshell where it has to take scrubbing, such as a hallway, a kitchen or a "
              "kids' room. Woodwork wants eggshell or satinwood rather than gloss, because gloss "
              "shows up every lump and brush mark. Bare wood or metal gets a primer then an "
              "undercoat; plastic, melamine and old gloss need an adhesion primer first or the paint "
              "peels; anything that gets hot, like a radiator or a pipe, wants a heat-resistant "
              "paint made for metal. New plaster wants a mist coat - emulsion thinned by about a "
              "fifth with water, no vinyl - to soak in and seal the dust. Buy a sample pot before the "
              "big tin, because colour on a wall is not colour on a card.",
              # the litre figure, the coats, the drying time, the day a room takes, a colour, a
              # price, a mark on the wall and a surface that is peeling are all other questions
              avoid=("how much paint", "much paint", "how many litres", "litres of paint",
                     "how many tins", "how many coats", "coats of paint", "second coat",
                     "between coats", "how long", "dry", "drying", "how many days", "how much",
                     "how many", "cost", "costs", "price", "prices", "cheap", "expensive",
                     "what colour", "what color", "which colour", "which color", "colour scheme",
                 # a colour is not a tin: "what is a good neutral paint colour" matched this row
                 # on "paint" and "what is" as well as colour-choice's gate, and the tie went to
                 # the tin card. The colour question keeps its own row.
                 "neutral", "good colour", "best colour", "colour choice", "colour to paint",
                 "colour for", "which white",
                     "mark", "marks", "scuff", "stain", "stains", "peeling", "bubbling",
                     "blistering", "wallpaper", "fence", "shed", "car", "bike", "model", "art",
                     "paint a picture", "nails", "makeup", "store", "storing", "leftover",
                     "left over", "dispose", "get rid of", "thin", "white spirit",
                     # a room that is already the subject has its own rows, and each answers the
                     # question it was asked: the steamy room, the kitchen, the radiator, the order
                     # of work and the filler-and-sandpaper list were all better than this card
                     "bathroom", "kitchen", "radiator", "ceiling first",
                     "paint a room", "paint the room", "paint my room", "paint a bedroom",
                     # the order to paint a ceiling in is its own card, and it was better than
                     # the shopping list
                     "ceiling", "ceilings", "ceiling first",
                     "paint the walls", "paint the wall", "paint a wall", "to paint a room",
                     "matt or silk", "silk or matt", "decorate", "decorating", "decorated",
                     # a door, a run of skirting and a metal gate each have a how-to row that says
                     # what to do to that surface, and those answers were better than this card
                     "door", "doors", "front door", "back door", "skirting", "skirting boards",
                     "gate", "gates", "garden gate", "metal gate", "metal", "railings")),
        # Painting over a colour that is already there is a different job from kitting out a room
        # for paint: it is a question about coats and undercoat, and "how do i cover dark paint"
        # was being answered with how to roll a ceiling while "how do i paint a wall over dark
        # paint" got the shopping list.
        entry("paint-over-a-colour",
              # "cover" is not a key word: it is the everyday verb of a lid and a stew, and
              # "ok back to the chicken, should i cover it" was answered with two coats of
              # emulsion. What makes this the painting line is the paint, and the colour under it.
              (("paint", "painting", "repaint", "go over", "going over", "paint over"),
               ("dark", "darker", "darkest", "strong colour", "strong color", "bright colour",
                "bright color", "bright red", "red wall", "dark green", "dark blue",
                "old colour", "old color", "previous colour", "previous color", "dark paint",
                "block the colour", "hide the colour", "cover the wall", "over the top",
                "grimy white", "yellowed")),
              "Two coats of a decent emulsion usually cover a dark wall, and going much lighter "
              "than the old colour can need three; sand and wipe the wall down first and do not "
              "thin the paint. If the old colour is a strong red or a dark green, ask for a "
              "combined primer and undercoat tinted towards the new colour - it saves a coat and "
              "stops the old shade grinning through.",
              bias=1),
        entry("paint-room", (("paint", "painting"), ("room", "wall", "walls", "living", "need",
                                                    "before", "prepare",
                                                    # A room named is a room to paint: "what do i
                                                    # need to paint the front room" and "gonna paint
                                                    # the spare room at the wknd" both want the
                                                    # shopping list before they start. The hall and
                                                    # the landing are left out on purpose: a
                                                    # correction naming one of them ("i want to
                                                    # paint the kitchen" / "i meant the hallway")
                                                    # has to keep the advice already on the screen,
                                                    # and a row keyed on the hall re-answers from
                                                    # the top instead.
                                                    "bedroom", "bedrooms", "lounge", "living room",
                                                    "front room", "dining room", "spare room",
                                                    "nursery", "whole flat", "whole house")),
              "Before paint you need filler for the holes, fine sandpaper, masking tape, a dust sheet, "
              "a roller and tray, a brush for edges and an old screwdriver to open the tin. One litre "
              "of emulsion covers about 12 square metres, so measure the walls and buy two coats' "
              "worth.",
              # "what colour should i paint my living room" is a colour question, and this entry was
              # answering it with the shopping list: `paint-room` keeps the how-to and gives up the
              # choosing.
              avoid=("what colour", "what color", "which colour", "which color", "colour", "colours",
                     "color", "colors",
                     # "marks on the painted wall" and "how do i get a mark off the wall" are not a
                     # shopping list for painting the room, and this entry was answering both
                     "mark", "marks", "marked", "scuff", "scuffs", "stain", "stains",
                     "fingerprint", "fingerprints", "smudge", "smudges",
                     # how much to buy is paint-quantity's question, not the shopping list's
                     "how much paint", "much paint", "how many litres", "litres of paint",
                     "how many coats", "coats of paint",
                     # which tin to buy is the which-paint row's question: "what paint do i need
                     # for the walls" and "washable paint for a kids room" were given the filler and
                     # sandpaper shopping list
                     "what paint", "which paint", "what kind of paint", "what type of paint",
                     "best paint", "washable", "washable paint", "kids room"),
              # No ask here on purpose: a room named is a room to paint, with or without a
              # question word - "gonna paint the spare room at the wknd" wants the shopping list
              # as much as "what do i need to paint the front room" does. A correction
              # ("i meant the hallway") is screened off in the composer instead.
              ),
        # A "how long before I paint over it" line was the shopping list: `paint-room` is keyed on
        # paint beside "before", so "how long should i wait before painting over filler" got a list of
        # sandpaper and dust sheets and never a drying time, which is the whole question. The duration
        # words stand the list down and this row answers with the hours.
        entry("paint-drying-time",
              (("paint", "painting", "repaint", "repainting", "filler", "filling", "undercoat",
                "gloss", "emulsion", "primer", "silicone", "sealant", "caulk", "wood filler"),
               ("how long", "wait", "waiting", "dry", "dries", "drying", "cure", "curing",
                "overnight", "hours", "before painting", "before i paint", "before sanding")),
              # The answer leads with the paint, because "how long does paint take to dry" is the
              # line people send most and it used to be met with the filler timing. Filler and
              # silicone keep their own sentences after it.
              "Emulsion takes a second coat in 2 to 4 hours and is properly hard in about a day; "
              "undercoat and gloss want overnight, 16 to 24 hours, and longer in a cold room. A "
              "small hole of filler is hard in about an hour, so it can be sanded and painted the "
              "same day, but a deep fill wants overnight or it shrinks back and shows. Silicone has "
              "to be a paintable one - most sanitary silicones cannot be painted at all - and it "
              "wants 24 hours to cure before a brush goes near it.",
              # how long the job takes, how much paint, how many coats, a price and a colour are all
              # other questions, and a finish that is coming off is a repair
              avoid=("how long does it take to paint", "how long to paint", "take to paint",
                     "paint a room", "paint the room", "paint my room", "paint the walls",
                     "how many coats", "how much paint", "how many litres", "much paint",
                     "cost", "costs", "price", "prices", "cheap", "expensive", "how much is",
                     "how much does", "what colour", "what color", "which colour", "which color",
                     "peeling", "peeling off", "flaking", "bubbling", "blistering", "strip",
                     "stripping", "wallpaper", "last", "lasts", "goes off", "shelf life",
                     # how often to recoat is the coats row's, and it already gives the hours
                     "between coats", "how many coats", "coats of paint", "recoat", "re-coat",
                     "second coat", "third coat",
                     # and keeping a paint workable is not asking how long it takes: the row below
                     # answers that, and this one answered it with filler times
                     "drying too fast", "drying too quickly", "dries too fast", "dry too fast",
                     "from drying", "keeps drying", "before it dries", "open time", "wet edge")),
        # The same hours, asked from the filler's side: "how long do i need to leave filler before
        # sanding" is the sanding question, and it was read as a bag of sand to buy and then as the
        # paint's drying times, with the filler in the second sentence. The filler's own hour is the
        # answer, so it leads here.
        entry("filler-drying-time",
              (("filler", "wood filler", "polyfilla", "filling", "filled", "skim", "skimming"),
               ("how long", "leave", "wait", "dry", "dries", "drying", "set", "sets", "harden",
                "hardens", "sand", "sanding", "sanded", "rub down", "rubbing down", "before")),
              "A thin skim of filler is hard in about an hour and can be sanded the same day; a deep "
              "fill wants overnight, because it shrinks back if the middle is still soft when you rub "
              "it down. Rub it with 120 grit on a block rather than with your fingers, and stop when "
              "the edge blends into the wall - two thin fills are quicker than one thick one that has "
              "to be dug out. Give it a coat of watered-down emulsion before the paint, or the patch "
              "drinks the first coat and shows as a dull spot.",
              # how much filler or sand to buy is the quantities rows' question, and a pipe, a car
              # or a cake has a filler of its own
              avoid=("how much", "how many", "bags", "cost", "costs", "price", "prices",
                     "quid", "pounds", "£", "fuel", "petrol", "diesel", "radiator",
                     "car", "pipe", "sink", "bath", "cake", "sandwich", "sandpaper",
                     "what is", "what are", "what's", "meaning", "recipe",
                     # which of the two comes first is an order of work, not a drying time:
                     # "do i sand first or fill first" keeps the row that says the step that
                     # would spoil the other goes last
                     "first", "which one first", "before that", "order", "order to"),
              bias=2),
        # The other half of the drying question: not how long it takes but how to keep it workable.
        # "how do i keep my paint from drying too fast" was answered by the leftover-tin card ("stir
        # sand into it and take it to the tip"), which is a worse answer than none, because it sounds
        # like advice. Heat, sun, a draught and a wide tray are what dry a paint too fast, and a wet
        # edge is what the job stands or falls on.
        entry("paint-drying-fast",
              (("paint", "painting", "emulsion", "gloss", "undercoat", "eggshell", "satin",
                "roller", "brush", "wet edge", "paint tin", "tin of paint", "tray"),
               ("drying too fast", "drying too quickly", "dries too fast", "dries too quickly",
                "dry too fast", "dry too quickly", "keeps drying", "from drying", "stop it drying",
                "before it dries", "going off the brush", "drying out", "wet edge", "open time",
                "workable", "flash", "dry so fast", "dries so fast", "dry so quick", "dries so quick",
                "drying so fast", "so fast", "too hot", "in this heat"),),
              "Heat and moving air are what dry a paint too fast, so keep the room cool and out of "
              "direct sun, shut the window and turn any fan off. Lid the tin and decant only what you "
              "will use in ten minutes, because a wide tray is all surface; a smaller tub keeps it "
              "workable. Water-based paint can take a splash of water, no more than one part in ten, "
              "or a paint conditioner from a decorator's shop. Then work to a wet edge: do one wall at "
              "a time in one go, roll into the bit you just did rather than next to it, and do not "
              "stop halfway across. A brush or roller you are coming back to in a few minutes goes in "
              "a damp cloth or a bag, and a skin on the paint in the tin gets lifted off, not stirred "
              "back in.",
              # how long it takes to dry is paint-drying-time, a leftover tin is paint-tins, and a
              # finish that has dried badly is a repair
              avoid=("how long", "how many hours", "overnight", "second coat", "between coats",
                     "how many coats", "get rid", "dispose", "throw", "bin", "tip", "recycle",
                     "leftover", "old paint", "how much paint", "cost", "price", "cheap",
                     "peeling", "flaking", "cracking", "bubbling", "blistering", "strip",
                     "wallpaper", "smell", "smells", "fume", "fumes", "colour", "color",
                     "which paint", "best paint", "nail polish", "spray")),
        # Keeping a part-used tin is the third question about a tin, after how long it takes to dry
        # and what to do with a finished one: "how do i stop my paint going lumpy", "my paint has
        # gone lumpy", "can i use paint that has been frozen", "how do i stop paint skinning over"
        # and "how do i store paint over winter" were a search hedge or the wallpaper card.
        entry("paint-keeping",
              (("paint", "painting", "emulsion", "gloss", "undercoat", "eggshell", "satin",
                "tin of paint", "paint tin", "part used paint", "part-used paint"),
               ("store", "storing", "storage", "keep", "keeping", "kept", "lumpy", "lumps",
                "lumpy paint", "skin", "skinned over", "skinning over", "skin on the paint",
                "gone thick", "gone hard", "thickened", "separated", "frozen", "gone off",
                "between coats", "between jobs", "over winter", "in the garage", "in the shed")),
              ("Paint keeps for years if the lid is sealed: wipe the rim clean, press the lid down "
               "with a block of wood until it clicks, and store the tin upside down so any skin forms "
               "at the bottom rather than on top. Keep it somewhere frost-free, because paint that has "
               "frozen is never right again. A tin that has gone lumpy or thick can often be saved: "
               "lift the skin off, strain it through a pair of tights or a paint strainer into a clean "
               "tub, and stir it well - water-based paint takes a splash of water, oil-based takes "
               "white spirit, no more than one part in ten. When it is full of hard lumps, or it "
               "smells sour, it is past saving and goes to the tip."),
              # a brush or a roller is washed, a tin nobody will open again is dried out for the tip,
              # and how long a coat takes to dry is the drying row's question
              avoid=("brush", "brushes", "paintbrush", "paintbrushes", "roller", "rollers",
                     "get rid", "dispose", "throw", "bin", "the tip", "to the tip", "recycle",
                     "how long does it take", "how long to paint", "how many coats", "how much paint",
                     "second coat", "between coats of", "drying too fast", "dries too fast",
                     # thinning is its own answer and it leads with the ratio: "how do i thin lumpy
                     # emulsion" wants that, not how to keep a tin
                     "thin", "thins", "thinning", "thin it", "thin the", "thinner", "water it down",
                     "wet edge", "peeling", "flaking", "bubbling", "strip", "wallpaper", "smell",
                     "smells", "fumes", "colour", "color", "which paint", "nail polish", "spray"),
              bias=1),
        # A colour that came out darker than the tin promised is the same complaint people make about
        # henna and about a foundation, and the bot had nothing for it here: "my emulsion looks too
        # dark" and "my paint is too bright" got the shrug, "the paint came out darker than the
        # sample" and "my gloss came out too dark" got the stain-removal card, "my wood stain is too
        # dark" got the white-water-ring card, "the colour i painted the wall is too strong" got "are
        # you pleased with it?", and "can i lighten paint that is too dark" got the search hedge. The
        # answer is the same in all of them and it is not "repaint the wall in darker paint": a wet
        # paint reads lighter than it dries, so the first thing to do is let it dry and look again in
        # daylight, and a coat that has dried too dark is not lightened by anything that can be added
        # to it - it is sanded and covered, or left and lived with.
        entry("paint-too-dark",
              (("paint", "painted", "painting", "emulsion", "gloss", "undercoat", "eggshell",
                "satin", "satinwood", "varnish", "lacquer", "wood stain", "stain", "wood dye",
                "fence stain", "decking stain", "paint tin", "tin of paint", "roller"),
               ("too dark", "come out dark", "came out dark", "came up dark", "darker than",
                "much darker", "so dark", "dried dark", "dries dark", "goes dark", "went dark",
                "too strong", "too bright", "too intense", "too deep", "too orange", "too yellow",
                "too red", "lighten", "lightening", "lighter", "pale it down", "palest",
                "hate the colour", "wrong colour", "wrong color", "not the colour", "regret",
                "darker sample", "the sample")),
              "Give it a day before you judge it: paint reads about a shade lighter while it is wet, "
              "so a wall that looks too strong tonight has usually settled by tomorrow, and the light "
              "you look at it in changes it as much as the paint does. If it is still too dark once it "
              "is hard, nothing can be added to a coat to lighten it - so the fix is either one coat "
              "of the colour you wanted over the top (a pale colour covers a dark one in two or three "
              "coats, and a test patch on a scrap of plasterboard or lining paper will tell you how "
              "many before you buy another tin), or a glaze of white emulsion wiped over it while it "
              "is tacky to lift it a shade. If the tin was a match to a sample, take a photo in "
              "daylight and the tin back to the shop: most will retint or exchange one they mixed "
              "wrong. A wood stain that went too dark sands back to bare wood and starts again with a "
              "pale one, since stain sinks in rather than sitting on top.",
              # a streak or a patch is an uneven coat, not the wrong colour; a mark on the wall, a
              # carpet or a shirt is a stain to lift; how much to buy, how long it takes to dry, which
              # paint to choose, stripping it off and what a tin costs are all answered elsewhere
              avoid=("streak", "streaks", "streaky", "patchy", "patchy coverage", "blotchy",
                     "uneven", "roller marks", "brush marks", "lap marks",
                     "mark", "marks", "scuff", "scuffs", "smudge", "spill", "spilled", "drip",
                     "drips", "carpet", "sofa", "shirt", "clothes", "fabric", "curtain", "hands",
                     "skin", "nail", "nails", "hair",
                     "how much", "how many litres", "litres", "tins of", "cost", "costs", "price",
                     "prices", "cheap", "expensive", "how much is", "how much does",
                     "how long", "drying time", "dry between", "second coat", "how many coats",
                     "which paint", "what paint", "best paint", "what colour should",
                     "which colour should", "what color should", "strip", "stripping", "remove",
                     "removing", "peel", "peeling", "flaking", "bubbling", "blistering",
                     "wallpaper", "woodchip", "fence up", "shed", "car", "bike", "model", "canvas",
                     "picture", "art", "nails", "makeup", "printing", "printer", "photo"),
              # a colour that came out wrong is a judgement on the finish, and a card that offers to
              # lift a mark off a carpet must not win it
              bias=2),
        # --- and the paper on the wall --------------------------------------------------------
        # Taking old paper off and painting over it are two different jobs, and the bot had neither:
        # "how do i strip wallpaper", "how do i remove woodchip", "can i paint over wallpaper" and
        # even "do i need to strip it first" after "its got woodchip on it" all got the search hedge.
        # Woodchip is its own entry because it comes off in two goes and wetting it first ruins the
        # top layer; one paragraph about both would have to hedge both.
        entry("woodchip-off",
              (("woodchip", "wood chip", "woodchip paper", "anaglypta", "textured wallpaper"),
               ("strip", "strips", "stripping", "remove", "removing", "off", "get off",
                "come off", "take down", "steam", "steamer", "scrape", "scraping", "soak",
                "soaking", "stuck", "peel", "peeling", "paint", "painting", "over", "cover")),
              "Woodchip comes off in two goes: lift the top layer dry with a wide scraper first (it "
              "comes away in sheets), then score and soak the backing paper for 10 to 15 minutes and "
              "scrape that off. Do not wet it before the top is off, or the chips turn to mush and "
              "smear across the wall.",
              # a line about the paint colour, or about buying the house, is not this job
              avoid=("buy", "buying", "selling", "sell", "price", "cost", "how much is",
                     "wood chip boiler", "boiler", "biomass")),
        entry("wallpaper-peeling",
              (("wallpaper", "wall paper", "lining paper", "paper"),
               ("peel", "peels", "peeled", "peeling", "lifting", "lifts", "loose", "bubble",
                "bubbles", "bubbling", "blister", "blistering", "corner", "corners", "seam",
                "seams", "coming away", "came away", "flapping", "repair")),
              "Paste it back rather than strip it: lift the loose edge with a knife, scrape the old "
              "paste off the wall behind it with a filling knife, spread a thin even coat of overlap "
              "adhesive (border and overlap adhesive) on the wall, press the paper back and smooth it "
              "out from the middle with a damp sponge. A bubble in the middle gets a slit with a "
              "stanley knife, paste, and the same press. Damp patches that keep coming back are not a "
              "paper problem.",
              # how long it stays up, or a colour, is not the repair, and a damp wall is the damp
              # question's.
              avoid=("how long", "strip", "stripping", "remove all", "whole room", "damp", "mould",
                     "mold", "wet", "leak", "what colour", "which colour", "paint over"),
              bias=1),
        entry("paint-over-wallpaper",
              (("paint", "painting", "repaint", "emulsion", "undercoat"),
               ("wallpaper", "wall paper", "lining paper", "paper", "walls", "wall", "over")),
              "Not over woodchip or any textured paper: the pattern shows through, every seam lifts, "
              "and a thinned first coat will not hold it down. Smooth, sound lining paper can be "
              "painted with a mist coat (emulsion thinned by about a tenth) and then two ordinary "
              "coats, and any bubble or lifted seam comes off before the roller comes out.",
              # the paper has to be the thing being painted: the shopping list for a room, a colour,
              # and the stain on the wall are all other answers'.
              ask=("wallpaper", "wall paper", "lining paper", "paper", "over"),
              avoid=("what colour", "what color", "which colour", "which color", "colour",
                     "colours", "color", "colors", "toilet paper", "newspaper", "exam paper",
                     "printer paper", "wrapping paper", "sandpaper", "paint stripper",
                     "paintbrush", "paint brush", "fence", "door", "doors", "radiator",
                     "ceiling")),
        entry("wallpaper-off",
              (("wallpaper", "wall paper", "wallpapers", "lining paper", "paper"),
               ("strip", "strips", "stripping", "remove", "removing", "off", "get off",
                "come off", "comes off", "take down", "steam", "steamer", "scrape", "scraping",
                "soak", "soaking", "stuck", "peel", "peeling", "old")),
              "Score it all over, soak it, then scrape it: a paper tiger (or a fork) gives the water "
              "somewhere to go, warm water with a splash of washing-up liquid needs 10 to 15 minutes "
              "to do its work, and a scraper held almost flat lifts the paper without gouging the "
              "plaster. A steamer is quicker than a sponge for a whole room, and an old papered room "
              "is a weekend's job.",
              # the key word is the paper on a wall, not paper: a phone's wallpaper, printing, an exam
              # and a newspaper are all someone else's answer, and a stain on papered walls is the
              # damp question.
              # a corner that has lifted is the paste-back repair, above, not the whole job.
              avoid=("peel", "peels", "peeled", "peeling", "lifting", "bubble", "bubbles",
                     "bubbling", "corner", "corners", "phone", "iphone", "android", "mobile",
                     "tablet", "ipad", "laptop",
                     "computer", "pc", "desktop", "screen", "lock screen", "home screen",
                     "background", "download", "app", "print", "printer", "printing", "exam",
                     "essay", "newspaper", "toilet paper", "damp", "mould", "mold",
                     "condensation", "woodchip",
                     # A mark on papered wall is a mark, not a paper to come off: "how do i get a
                     # mark off the wallpaper" was told to score it all over and soak it, because
                     # "get off" and "wallpaper" are both in this key. Nothing to strip is being
                     # asked about there, and `wallpaper-mark` answers it.
                     "mark", "marks", "stain", "stains", "dirty", "clean", "cleaning", "wash",
                     "washed", "scuff", "scuffs", "smudge", "smudges", "grease", "greasy",
                     "fingerprints", "fingerprint", "spot", "spots", "wipe")),
        # --- a mark on papered wall -----------------------------------------------------------
        # "marks on the wallpaper", "dirty wallpaper" and "how do i get a mark off the wallpaper"
        # all had no answer on main: the paint and strip cards know the paper, not the mark on it,
        # and the wall card's answer is a pencil rubber on emulsion.
        entry("wallpaper-mark",
              (("wallpaper", "wall paper", "papered wall", "papered walls", "lining paper",
                "vinyl wallpaper", "flocked wallpaper", "woodchip"),
               ("mark", "marks", "stain", "stains", "dirty", "clean", "cleaning", "wash",
                "washable", "scuff", "scuffs", "smudge", "smudges", "grease", "greasy",
                "fingerprints", "fingerprint", "spot", "spots", "wipe")),
              "Go at it dry first and test a hidden corner: a soft pencil rubber or a clean, barely "
              "damp cloth with a drop of washing-up liquid lifts most marks off paper, working from "
              "the bottom up so drips do not streak. Water is what ruins wallpaper, so keep the "
              "cloth as dry as it can be - a washable vinyl paper takes a mild soap, a printed or "
              "flocked one usually will not, and a mark that will not lift is better patched or "
              "covered than scrubbed.",
              # the job of stripping, hanging or painting the paper is each its own card, and a
              # damp patch is the damp question
              avoid=("strip", "stripping", "remove the paper", "remove the wallpaper", "take down",
                     "hang", "hanging", "hanging paper", "paste", "repaste", "put up", "putting up",
                     "put wallpaper", "put the wallpaper", "put paper", "putting paper", "paper the",
                     "paper a wall", "papering", "ceiling", "ceilings", "size", "sizing", "how much",
                     "how much do i need", "choose", "which wallpaper", "what colour", "what color",
                     "border", "borders", "peel", "peeling", "lifting", "bubble", "bubbling",
                     "seam", "seams", "repair", "replace", "paint", "painting", "paint over",
                     "damp", "mould", "mold", "condensation", "phone", "iphone", "laptop",
                     "screen"),
              bias=1),
        # Wallpaper off and over is above; these are the paint jobs people ask for by the thing
        # being painted - woodwork, a ceiling, a door, a radiator, tiles, a table - plus hanging
        # paper. One row per actual question, keyed on the thing painted and what is asked.
        # "what colour should i paint the bathroom" is the colour row's question, so every new
        # decorating row holds the same colour words `paint-room` holds.
        entry("paint-over-gloss", (("paint over", "painting over", "paint on top of", "over gloss",
                                    "over the gloss", "over old paint", "gloss paint",
                                    "paint gloss", "paint a gloss", "undercoat", "primer",
                                    "priming"),
                                   ("gloss", "glossy", "satin", "sheen", "undercoat", "primer",
                                    "cupboard", "cupboards", "kitchen", "door", "doors",
                                    "woodwork", "skirting", "banister", "radiator")),
              "Sand it dull first: new paint needs a key to grip, so take the shine off old gloss with "
              "120 grit, wipe off the dust, then one coat of undercoat and your topcoat. A water-based "
              "satin goes on after the sanding alone and dries in a couple of hours; oil gloss straight "
              "onto old gloss is the way to get peeling in a year.",
              avoid=("what colour", "what color", "which colour", "which color", "colour",
                     "colours", "color", "colors", "peeling off") + _TAKING_PAINT_OFF),
        entry("paint-bathroom", (("paint", "painting", "repaint", "emulsion"),
                                 ("bathroom", "kitchen", "shower room", "steamy", "steam",
                                  "mould resistant", "mould-resistant", "mould proof")),
              "Use a mid-sheen, eggshell or bathroom paint rather than matt emulsion: it shrugs off "
              "steam and can be wiped, where matt goes patchy over a bath. Two coats is a day's work "
              "for a kitchen or bathroom. Paint does not stop mould on its own, so sort the extractor "
              "fan or open a window while you steam.",
              avoid=("what colour", "what color", "which colour", "which color", "colour",
                     "colours", "color", "colors", "mould on", "mould in", "black mould")
                    + _TAKING_PAINT_OFF),
        # How long the job takes is its own question, and it was reaching the row above for the
        # life of a coat: "how long does it take to paint a room" was answered with how many years
        # two coats last, because "how long" was in the keeping row's key and none of the paint
        # rows asked for it (garnet-orca followed "i want to paint the kitchen" with "how long
        # will it take" and got "Five to ten years").
        entry("paint-time", (("paint", "painting", "repaint", "decorate", "decorating",
                               "decorated", "emulsion", "walls"),
                              ("how long", "how many days", "how many hours", "time", "take",
                               "takes", "long", "day", "days", "weekend", "afternoon")),
              "A normal room is a day's work with two coats: an hour or two to cut in and roll, then "
              "about four hours before the second coat, so most people do the first coat in the "
              "evening and the second the next morning. A whole flat or house is roughly a day per "
              "room, plus a day for the ceilings and woodwork. A single door, a run of skirting or a "
              "radiator is a morning: an hour or two a coat, with overnight between the coats.",
              avoid=("how many coats", "coats of paint", "coat of paint", "between coats",
                     "recoat", "drying time", "how long to dry", "how long does paint take",
                     "how long does it last", "how long will it last", "last", "lasts",
                     "mould", "how much", "cost", "price", "pricey",
                     # "how long does it take for paint to dry" is the coats-and-drying row's
                     # question, not the time the job takes
                     "to dry", "dry", "drying",
                     # "where do i take old paint" is a disposal question and it answered the hours
                     # a room takes, because "take" is in the ask and the tin rows said none of the
                     # words below. A tin that has to go is not a tin being painted with.
                     "old paint", "take old paint", "leftover paint", "left over paint",
                     "part used tin", "unused paint", "dispose", "disposal", "get rid of",
                     "getting rid of", "tip", "the tip", "recycling centre", "recycling center",
                     "household waste", "waste centre", "skip", "throw away", "throw out",
                     "throwing out", "goes", "where can i take", "where do i take",
                     # a drying time is the row below's question, and "how long should i wait
                     # before painting over filler" and "how long before i can paint silicone" both
                     # answered how long a whole room takes. The things that are drying name it.
                     "filler", "filling", "filled", "silicone", "sealant", "caulk",
                     "undercoat", "primer", "priming", "before painting", "before i paint",
                     "before sanding", "before i sand", "wait", "waiting", "to dry", "till it dries",
                     "before the second coat", "between coats"),
              ask=("how long", "how many", "time", "take", "takes", "day", "days", "hours",
                   "decorate", "decorating", "decorated"),
              bias=1),
        # How many years a coat lasts is its own question, and it had no answer: the years were a
        # sentence inside the steamy-room card, which is how a follow-up of "how long will it take"
        # was answered with "Five to ten years" (garnet-orca). The fact has a card now, and the
        # steamy card keeps the day the job takes.
        entry("paint-life",
              (("how long", "how many years", "how often", "lifespan", "life of", "last", "lasts",
                "lasted", "recoat"),
               ("paint", "painting", "painted", "repaint", "repainting", "emulsion", "gloss",
                "satin", "eggshell", "walls", "woodwork", "exterior", "outside")),
              "Interior emulsion on a sound wall is good for about five to ten years, and gloss on "
              "woodwork about the same; a steamy bathroom sits at the shorter end because the steam "
              "lifts the edges first. Pale colours fade slowly and dark ones show scuffs, so most "
              "rooms get a refresh coat at five years rather than a full repaint.",
              avoid=("to dry", "drying", "take to", "between coats", "how many coats", "coats",
                     "how long to dry", "mould", "cost", "price", "much does", "how long does it take")),
        entry("paint-coats", (("how many coats", "coats of paint", "coat of paint", "second coat",
                               "two coats", "how long between coats", "between coats", "recoat",
                               "drying time", "how long to dry", "how long does paint take",
                               # "how long does it take for paint to dry" says "to dry" and not
                               # "how long to dry", and with no part-1 match it scored 2 and reached
                               # nothing
                               "to dry", "take to dry", "long to dry"),
                              # The paint is the fence, and "dry" is not a paint word: with it
                              # here the fence held the line on its own, and "i hung my washing
                              # out to dry" and "my hair takes ages to dry" were both answered
                              # "Two coats on bare or patched plaster". Every drying question
                              # about paint says paint, a coat, a wall, a door or the finish it is
                              # going on, so the fence keeps those and "dry" alone stops being
                              # enough.
                              ("paint", "painting", "coat", "coats", "wall",
                               "walls", "emulsion", "door", "woodwork")),
              "Two coats on bare or patched plaster, and two whenever the colour changes; a pale wall "
              "going a pale colour can take one. Leave about two to four hours between coats, and a "
              "full day before you push furniture back against it. Touch the wall first: hard and not "
              "tacky means it is ready."),
        # How long plaster takes to dry is its own question and it had no row of its own: the line
        # reached the bone-healing row, because "plaster" is in that row's parts and "how long" in
        # its time, so "how long does plaster take to dry" was answered "About six weeks for most
        # bones - six for a wrist or collarbone" (found typing at main 8e89c21). A wall that has
        # been plastered, skimmed or soaked is a drying question, and the paint rows above stand
        # down for "to dry" on purpose, so nothing else in the domain answers it.
        entry("plaster-dries", (("plaster", "plasters", "plastering", "plastered", "skim",
                                 "skims", "skimmed", "skimming", "render", "rendering",
                                 "plasterboard", "backing coat"),
                                ("dry", "dries", "drying", "to dry", "dried", "fully dry",
                                 "before i paint", "before painting", "before i can paint",
                                 "paint over it", "paint on it", "paint it", "mist coat",
                                 "when can i paint", "how long before", "wait", "cure",
                                 "curing")),
              "A thin skim is ready for a mist coat after two to four days and painted properly "
              "after about a week. A backing coat, or a wall taken back to brick, is roughly a "
              "week for every 10mm of thickness, so a fortnight or more. The colour is the best "
              "gauge - pale, chalky and the same all over means dry, and a patch that is still "
              "dark and cool has not finished, which wants a day or two more. Painting it before "
              "it has gone pale traps the water and blows the paint within a month.",
              # an arm in plaster, a cast and a fracture are the bone row's questions; a plaster
              # on a cut is the wound answer's; a damp wall, a wet patch and a ceiling that has
              # dried are the damp rows' own questions, with their own answers
              avoid=("in plaster", "plaster on", "plaster cast", "cast", "surgery", "arm", "arms",
                     "leg", "legs", "wrist", "ankle", "knee", "bone", "bones", "broken",
                     "broke", "break", "fracture", "fractured", "hospital", "cut", "cuts",
                     "wound", "graze", "blister", "tooth", "teeth",
                     # a colour, a price or a product is another row's question
                     "what colour", "what color", "which colour", "which color", "colour",
                     "colours", "color", "colors", "how much", "cost", "price", "how many",
                     "wallpaper", "hang", "hanging", "strip", "stripping", "tiles", "tiling",
                     "tile the", "mould", "mold", "black mould", "condensation",
                     # a damp wall, a wet patch and a ceiling that has dried are the damp and
                     # water-stain rows' questions, and this row took all of them on its first
                     # run: "how do i dry out a damp wall" is finding the water, not a mist coat
                     "damp", "dampness", "damp patch", "wet patch", "wet", "water", "leak",
                     "leaking", "stain", "stains", "yellow marks", "brown patch"),
              bias=2),
    ]
