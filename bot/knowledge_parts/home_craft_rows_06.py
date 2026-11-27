"""Rows 6 of 10 of `home_craft.entries()`: `bath-seal` .. `hinge-sag`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
def rows():
    from ..knowledge.home import _a_room_being_heated, _door_lock_stiff, _lost_keys, entry
    from ..knowledge.lookup import not_the_heat_of_an_argument
    from ..knowledge.lookup import asks_where
    THE_APPLIANCE_ITSELF = (
        "my fridge", "the fridge", "our fridge", "fridge is", "fridge not", "fridge too",
        "fridge door", "fridge keeps", "in the fridge", "fridge cold",
        "my freezer", "the freezer", "our freezer", "freezer is", "freezer not", "freezer cold",
        "in the freezer", "freezer door",
        "my oven", "the oven", "our oven", "oven is", "oven not", "oven too", "oven on",
        "in the oven", "oven door", "fan oven", "oven cold",
    )
    return [
        # A toilet seat that moves is two bolts and a hinge, and main gave it either the falls card
        # ("wobbly" is a balance word) or "say more if it helps".
        # The silicone round a bath is the most-replaced seal in a house and nothing answered it:
        # "how do i seal a bath" was a shrug, and so was "how do i reseal round the bath".
        entry("bath-seal",
              (("bath", "baths", "bathtub", "bath tub", "shower tray", "shower base", "bath panel",
                "bathroom seal", "silicone", "silicon", "sealant", "mastic"),
               ("seal", "sealing", "sealed", "reseal", "re seal", "re-seal", "silicone", "sickaflex",
                "mould", "mold", "black", "gaps", "gap", "water getting behind", "leaking", "leak",
                "coming away", "peeling", "replace", "replacing", "strip", "stripping", "around",
                "along", "edge", "edges")),
              "Cut the old silicone out and scrub the joint back to dry, grease-free tile and bath "
              "before anything else, because fresh silicone will not stick to the old. Fill the bath "
              "with water first, so the bead is made at the weight it has to carry, then run anti-mould "
              "silicone along it and smooth it with a wet finger or a tool. Leave it 24 hours before "
              "you let the water out, and it will not part from the bath in a month.",
              # the bath that will not fill, will not drain or is not hot is another answer
              avoid=("fill", "filling", "filler", "drain", "draining", "slow", "blocked", "hot water",
                     "cold", "not hot", "boiler", "tap", "taps", "shower", "shower not working",
                     "paint", "painting", "bath bomb",
                     # the tiles are where the seal is, not the job: "how do i seal a bath round
                     # the tiles" was a grout scrub because this row stood down for the word
                     # "tile". What it stands down for is tiling the wall itself.
                     "tile the", "tiling the", "tiling a", "how do i tile", "grout the",
                     "regrout", "re-grout", "grouting the")),

        entry("toilet-seat-wobble",
              ("toilet seat", ("wobble", "wobbles", "wobbly", "loose", "loosening", "coming loose",
                               "moves", "moving", "slides", "sliding", "not tight", "fix", "tighten",
                               "broken", "cracked")),
              "Tighten the two bolts under the seat where the hinges meet the pan: they are usually "
              "plastic nuts you can turn by hand from underneath, and a quarter turn each side takes "
              "the movement out. If the seat still slides it is the hinge, and a replacement seat with "
              "a top-fix kit is about £10 to £20 and fits in ten minutes without getting under the "
              "pan. If the holes in the hinge have gone oval, a wipe of plastic wood in them holds the "
              "screws again.",
              bias=1),
        # A washing machine that walks across the floor is not level, and the transport bolts are the
        # thing nobody remembers.
        entry("washer-wobble",
              (("washing machine", "washer"),
               ("wobble", "wobbles", "wobbly", "shaking", "shakes", "vibrating", "vibration",
                "walking", "moves", "moving", "banging", "noisy", "noise", "spinning", "loud")),
              # "tumble dryer" and "dryer" used to be in this key, and a dryer does not have transport
              # bolts or a levelling drum: the noise table above owns a dryer that shakes, and it says
              # the thing that is actually wrong with one (coins, a bra wire, an even load).
              "Level it first: the machine must not rock on the floor, so turn the front feet out until "
              "it sits flat on all four and lock the nuts. If it is new, the four transport bolts at "
              "the back have to come out or the drum is still locked to the frame. After that, an even "
              "load stops most of it - mix towels with lighter things rather than washing one heavy "
              "item - and check the shipping bolts are the right length for a laminate floor.",
              # "the machine moves when it spins" is this row; taking the machine to a new flat is
              # the transport-bolt card, so the removal words stand this one down
              avoid=("tumble dryer", "tumble dryers", "dryer", "dryers", "washer dryer",
                     "washer-dryer", "condenser",
                     "move house", "moving house", "moving flat", "move flat", "new flat",
                     "new house", "new home", "upstairs", "downstairs", "van", "removals",
                     "take it with me", "moving it", "moving the machine", "moving my",
                     # "isnt spinning" is not a wobble: the drum is not turning at all, and
                     # levelling a machine that will not spin does not touch the cause. Levelling
                     # advice is for a machine that shakes, walks or bangs while it spins, which
                     # is what "wobbles", "shaking" and "walks" in the key say.
                     "isnt spinning", "isn t spinning", "not spinning", "no spin", "wont spin",
                     "won t spin", "wont turn", "won t turn", "drum isnt", "drum not")),
        entry("curtain-measure",
              (("curtain", "curtains", "blind", "blinds", "drapes"),
               ("measure", "measuring", "how wide", "how long", "buy", "size", "sized", "fit",
                "hanging", "hang")),
              "Measure the pole or track, not the window, and add 10 to 20cm either side so the "
              "curtains cover the edges when closed. For the length, measure from the pole to where "
              "you want them to finish, then double the width for a full gather: one and a half times "
              "the width looks skimped.",
              bias=1),

        entry("hang-picture", (("picture", "mirror", "shelf", "shelves", "shelf unit",
                                "floating shelf", "brackets",
                                # the same fixing question by its other subjects: a telly, a coat
                                # hook, a framed print
                                "tv", "television", "telly", "coat hook", "coat hooks", "frame",
                                "frames", "picture rail",
                                # a telly on a wall is the same fixing job; the phrases are here as
                                # well so that a telly that will not switch on is not one
                                "tv on the wall", "tv on a wall", "wall mounted tv", "wall-mount tv",
                                "mount a tv", "mount the tv", "tv bracket", "television on the wall",
                                "wall bracket",
                                # the fixing asked for by the thing that holds it: "i need a nail
                                # in the wall" and "what nail for plasterboard" were a chat
                                # module question ("What kind of nail do you usually go for?")
                                # and a fingernail-ridges card
                                "nail", "nails", "rawlplug", "rawlplugs", "rawl plug", "rawl plugs",
                                "rawplug", "rawplugs", "wall plug", "wall plugs", "anchor",
                                "anchors", "fixing", "fixings"),
                               ("hang", "hanging", "wall", "drill", "heavy",
                                "plaster wall", "plaster walls", "plasterboard wall", "brick wall",
                                "brick", "chimney breast", "lath and plaster", "no studs",
                                # "put up a shelf" and "what fixings do i need for a shelf" are the
                                # same job as hanging a picture: something goes on a wall and the
                                # fixing decides whether it stays there. "put up" without a shelf
                                # word is a tent or a curtain rail, and stays out.
                                "put up", "putting up", "fixings", "fixing", "fix", "mount",
                                "attach", "level", "stud", "studs", "plasterboard",
                                # "what bracket do i need", "which bracket should i buy": the
                                # buying words are the ask, and the noun above is the thing. A
                                # bracket that is a mark in a sentence is the writing row's own
                                # question, so every way of saying that is fenced out below.
                                "need", "needs", "needed", "buy", "buying", "should i get",
                                "what size", "which one",
                                # the fixing asked for by what it holds up: "what nails for a
                                # shelf" has the nail in the subject group and nothing else this
                                # row knows, so the for-tail is what says it is a fixing job
                                "for", "into", "in a wall")),
              "It is the fixing that matters, not the drill: find the studs with a stud finder or by "
              "tapping, and screw into one where you can. On plasterboard use proper hollow-wall "
              "fixings, not a bare rawl plug, for anything over a couple of kilos, and a shelf wants a "
              "bracket every 60cm or so. Two hooks 10cm apart keep a picture level far better than "
              "one. Check for pipes and wires before you drill, and check it with a spirit level "
              "before you tighten anything up.",
              # the mark in a sentence, the sum in a bracket and the band a wage falls in are all
              # the same word and none of them is a thing screwed to a wall.
              avoid=("writing", "sentence", "sentences", "sentenced", "essay", "essays", "grammar",
                     "punctuation", "comma", "commas", "paragraph", "paragraphs", "spell",
                     "spelling", "english", "algebra", "algebraic", "maths", "math", "equation",
                     "equations", "expand", "expanding", "simplify", "multiply", "x", "xy",
                     "tax", "taxed", "income", "salary", "wage", "wages", "band", "bands",
                     "percentage", "percent", "40k", "20k", "50k",
                     # the nail on a person, not the one in the wall: the filing, the polish, the
                     # biting and the clippers are the health and routines rows' lines
                     "file", "files", "clippers", "clipper", "polish", "varnish", "manicure",
                     "pedicure", "gel", "acrylic", "bitten", "biting", "cut my", "trim my",
                     "grow", "growing", "grew", "peeling", "ridges", "ridged", "fungus", "fungal",
                     "toenail", "toenails", "fingernail", "fingernails", "thumbnail", "toe", "toes",
                     "finger", "fingers", "nail fold", "ingrown")),
        # A bill question is about the cost, not about the boiler or the gas supply: a gas leak is
        # #safety's line, and "cut the gas to my boiler myself" is a plumbing job.
        entry("energy-bill", (("energy", "electric", "electricity", "gas", "heating", "utility",
                               "fuel",
                               # "my bill is massive" names no fuel at all: the bill itself is the
                               # subject, and the size words sit in the second group so a bare bill
                               # only counts when it is said to be big
                               "bill", "bills",
                               # the other half of a heating bill, asked by name: "how do i save
                               # on my hot water" was answered with the dry-eye card, because
                               # "heating" is in that reply and "hot water" was in no fuel list
                               "hot water", "hot-water",
                               # the dials the heating is turned down with, which people ask
                               # about by name: "how do i lower my boiler temperature",
                               # "how do i turn down my heating" were a plumber hedge and a shrug
                               "boiler", "thermostat", "radiator", "radiators", "flow temperature"),
                              ("bill", "bills", "cheaper", "reduce", "lower", "save", "cost",
                               "expensive", "price", "tariff", "spend less", "keep warm", "warm",
                               # the size of it, which people say instead of a question: "my bill is
                               # massive", "the gas bill was huge this month", "my bill is high".
                               # The words for a number that moved ("doubled", "gone up", "up again")
                               # stay out: that is the why-did-it-move question, and energy-use-up
                               # answers it with the meter and the estimated read.
                               "massive", "huge", "enormous", "sky high", "through the roof",
                               "so big", "big", "bigger", "high",
                               # the same question as a verb: "how do i stop wasting
                               # electricity" was the physics definition of electricity, and
                               # "i am wasting so much gas" was the bin's answer. What is being
                               # wasted is the fuel this row is about, so the verb belongs here.
                               "waste", "wasting", "wasted", "stop wasting",
                               # the same question in the words of the dial rather than the bill
                               "turn down", "turn it down", "turn up", "turn it up", "how low",
                               # "what temperature", "set" and "setting" used to be here, and they
                               # are the thermostat-setting question rather than the bill: with
                               # "thermostat" in the first group they won "what temperature should i
                               # set my thermostat to" and answered it with the flow temperature.
                               # The heating-temperature row says the numbers, so the setting words
                               # are its own now.
                               # the way-to-pay asks: "cheapest way to pay my gas and electricity",
                               # "is it cheaper to pay my bill by direct debit", a payment plan
                               "pay", "paying", "paid", "payment", "direct debit", "instalments",
                               "installments",
                               # the same ask in the words of a saving rather than a bill: "how
                               # do i save on my heating" was answered with the argument card,
                               # because "heating" is read as "heated" there and "save" only
                               # counted once. The turn-down phrases are not here: main's
                               # heating-temperature row owns the dial, and its comment says so.
                               # "save money" on its own was here and took one line back from
                               # the row that owns it: "whats the point of leaving the heating on
                               # all the time, does it save money" asks whether leaving it on
                               # saves anything, and `heating-all-day` says no and why. The bare
                               # phrase is true of that line too, so only the asks that name what
                               # the saving is on stay here.
                               "save on", "save money on", "cut my", "cut the",
                               "cheap to heat", "cheaper to heat", "get it cheaper",
                               "spend less", "spend less on")),
              "Heating and hot water are most of the bill, so start there: on gas, turn the boiler flow "
              "temperature down to 55 to 60C and heat only the rooms someone is in; all electric, put "
              "the immersion and any room heaters on a timer for the hours you actually use. Then "
              "standby and lighting, which is about a quarter, so switch off at the wall. Ask your "
              "supplier in writing for the standing charge and unit rate of their cheapest tariff; a "
              "fixed deal usually beats the standard variable one.",
              avoid=("smell", "leak", "leaking", "fumes", "carbon monoxide", "myself", "baby",
                     # one radiator's valve is its own row, not the boiler's dial
                     "turn down a radiator", "turn down the radiator", "one radiator",
                     "rad valve", "radiator valve", "trv", "thermostatic valve",
                     # and turning the house's own heating down is a setting, not a bill: "how do i
                     # turn down my heating" was the boiler-flow money answer
                     "turn my heating", "turn down my heating", "turn up my heating",
                     "turn our heating", "turn down our heating", "turn up our heating",
                     "toddler", "child", "clammy", "flue", "pilot light",
                     # "electric" is also the first word of things that are not a bill: a car, a
                     # blanket, a shower, a bike. Their running cost is a buying question.
                     "car", "vehicle", "blanket", "shower", "bike", "bicycle", "scooter",
                     "heater to buy", "which",
                     # a hob or an oven is a cooking question even when it names the fuel: "is an
                     # induction hob cheaper to run than gas" was answered with the boiler advice,
                     # which is about heating the house. The cooking-fuel entry below takes it.
                     "hob", "hobs", "induction", "oven", "ovens", "cooker", "cook", "cooking",
                     # a bill that is wrong or unpaid is a different question: money and the supplier,
                     # not how to use less heat
                     "can't pay", "cant pay", "afford", "debt", "arrears", "final notice",
                     "wrong", "mistake", "council tax", "tax", "water", "water bill", "phone",
                     # "why is my electric bill so high" asks what moved the number, and the
                     # energy-use-up row answers that with the meter and the estimated read: this
                     # row is the one that says what to do about it.
                     "why is my", "why has my", "why did my", "why are my", "why does my", "why so",
                     # asking to haggle or to ring them for a better price wants the call itself,
                     # not how to use less heat: that is the ring-about-a-price answer.
                     "haggle", "haggling", "haggled", "better price", "lower price",
                     # whether leaving it on saves anything is the habit row's question, and it
                     # answers yes or no where this row only says how to use less
                     "leaving it on", "leaving the heating on", "leaving the boiler on",
                     "left on all day", "on all the time", "on all day", "does it save",
                     "point of leaving",
                     # the other direction of the same fence: a bill at a table is not the fuel
                     # bill, and "the bill at the restaurant was too high" got the boiler flow
                     # temperature because "bill" and "high" are both in this row's key. The
                     # table's bill is `meal-bill-wrong`, which already names the fuels.
                     "restaurant", "restaurants", "waiter", "waitress", "split the bill",
                     "split bill", "the bill at the", "meal out", "card slip", "takeaway",
                     "cafe", "pub", "bistro", "pizzeria",
                     "mobile", "broadband", "tv licence", "licence", "rent", "insurance",
                     # Which deal to be on is a different question from what to turn down: the
                     # tariff and standing-charge answers live with the bills, and this one used to
                     # win them and talk about the boiler instead.
                     "switch", "switching", "tariff", "tariffs", "standing charge", "fixed deal",
                     "fixed tariff", "fixed rate", "worth",
                     # "is it cheaper to pay my energy bill by direct debit" is about how the
                     # money leaves the account, which money's paying-a-bill answers: the boiler
                     # flow temperature is not an answer to it.
                     "pay", "paying", "paid", "payment", "direct debit", "debit", "payment plan",
                     "how do i pay", "way to pay")),
        # "is it cheaper to leave the heating on all day" is one of the most-asked heating questions
        # there is, and it was answered with the general savings card - the flow temperature, the
        # standby, the standing charge - which never says yes or no. The habit words are the key and
        # the heating is the subject, so a setting, a timer, the hours someone is out and the hour
        # they come back are all the same question.
        # "is it safe to leave the boiler on all night" asks about the flame, not the bill, and it
        # reached the city-after-dark card because "safe" and "night" were the only two words in it
        # that anything knew. The tell is the safety ask in front of a boiler or the heating: what to
        # do about the money is the row below.
                entry("heating-all-day",
              (("heating", "central heating", "boiler", "radiators", "radiator", "hot water",
                "thermostat", "heating system"),
               ("all day", "all evening", "leave it on", "leave on", "leaving on", "left on",
                # "leave the heating on" is not "leave on": the thing being left comes between the
                # two words, so each way of saying it has to be a phrase of its own.
                "leave the heating on", "leaving the heating on", "left the heating on",
                "leave my heating on", "keep the heating on", "keeping the heating on",
                "heating on all day", "heating on all the time", "heating on low", "heating on at night",
                "on low", "all the time", "constant", "always on", "overnight", "timer",
                "programmer", "time clock", "when im out", "when i am out", "out at work",
                "out all day", "turn it off", "turn off", "switch it off", "switching it off",
                "come home", "coming home")),
              "No, it is not cheaper, for the heating or the hot water: keeping a house warm all day "
              "costs more than heating it when you are in it, and it shows on the bill. Every degree "
              "the rooms are held at is heat leaking out through the walls, so the timer wins - on an hour before you get up, off half an hour before bed, 18C in "
              "the living room and 16C in the bedrooms while you are up. Coming home to a cold house "
              "is a comfort problem rather than a cost one, and it is cheaper to warm the room you "
              "sit in for an hour than to keep the whole house up from midday. Hot water is the same "
              "story: heat the cylinder for an hour morning and evening with a jacket on it rather "
              "than leaving the immersion on. The exception is a well-insulated house on a heat "
              "pump, which is cheaper held at a steady low temperature than pushed up and down.",
              avoid=("broken", "not working", "isnt working", "isn't working", "fault", "faulty",
                     "no hot water", "cold water", "pressure", "bleed", "bleeding", "cold at the",
                     "radiator is cold", "radiators are cold", "noise", "noisy", "banging", "kettle",
                     "leak", "leaking", "smell", "carbon monoxide", "frost", "frozen", "condensation",
                     "mould", "damp",
                     # what to set it to is the room-temperature answer, and it is a different
                     # question from whether to leave it running
                     "what temperature", "how warm", "degrees", "what should i set", "set the",
                     "set my", "set it to", "how hot",
                     # the bill, the deal and the meter are the money questions
                     "bill", "bills", "tariff", "supplier", "standing charge", "price cap", "switch",
                     "switching", "smart meter", "can't pay", "cant pay", "afford", "debt",
                     "arrears", "council tax", "which boiler", "new boiler", "buy", "buying",
                     "worth getting", "service", "servicing",
                     # cold as an illness, and cold as the weather
                     "a cold", "my cold", "got a cold", "with a cold", "bad cold", "cold and flu",
                     "sore throat", "sneezing", "cough", "flu", "unwell", "sick", "chesty",
                     # a pet left in the house is its own question (how long a dog can be left,
                     # how warm a room a cat wants), and one sentence about the timer is not it
                     "cat", "cats", "dog", "dogs", "puppy", "kitten", "pet", "pets",
                     # a room for a baby is a safety answer, and "why is my heating always on" is
                     # a stuck programmer, not a habit: neither is this entry's question
                     "baby", "babies", "baby's", "newborn", "toddler", "cot", "nursery",
                     "why is my heating", "why does my heating", "why is the heating",
                     "why does the heating", "comes on by itself", "coming on by itself",
                     "on by itself", "keeps coming on", "wont go off", "won't go off",
                     # the boiler is the same fault in the same words: "why is my boiler always on"
                     # is a programmer that has stuck, and the answer is a plumber rather than an
                     # argument about the timer. The habit question asks whether it is cheaper and
                     # never asks why, so the why-shapes and the boiler's own symptoms stand this
                     # entry down.
                     "why is my boiler", "why does my boiler", "why is the boiler",
                     "why does the boiler", "why has my boiler", "why is my boiler on",
                     "boiler is always on", "boiler is on all", "boiler always on",
                     "boiler keeps", "boiler wont turn off", "boiler won't turn off",
                     "wont turn off", "won't turn off", "wont switch off", "won't switch off",
                     # the understanding layer reads "won't" as "will not" and "can't" as "cannot"
                     # before a key or an avoid word is matched, and a line read that way reaches no
                     # phrase written with the contraction: "my heating wont turn off" came back as
                     # the habit answer through that reading. Each of these is the same fault said
                     # the other way, so both spellings are named.
                     "will not turn off", "will not switch off", "does not turn off",
                     "doesnt turn off", "doesn't turn off", "can not turn", "cannot turn",
                     "cant turn it off", "can't turn it off", "cant turn off", "can't turn off",
                     "cant switch it off", "cant switch it off", "cant switch off",
                     "cant turn the heating off", "cant get it to go off",
                     "stuck on", "is stuck", "has stuck", "programmer is wrong",
                     "wrong time", "wrong times",
                     # A house nobody is in is the away question, and it wants the opposite answer:
                     # "should i leave my heating on when i go on holiday" and "...in an empty
                     # house" are both the same words as the staying-in habit line, and they were
                     # being told that the timer wins, which is advice to turn off the one thing
                     # that stops a hard frost bursting a pipe. The away row below answers them.
                     "go away", "going away", "gone away", "away for", "when im away",
                     "when i am away", "when were away", "while im away", "while i am away",
                     "while were away", "on holiday", "holiday", "empty house", "house is empty",
                     "nobody in", "no one in", "not at home for",
                     # "pipes dont freeze" is read as "pipes do not freeze" before a key is matched,
                     # so the phrase spelling never hits: the noun alone is the frost line, and the
                     # pipe row answers it.
                     "pipe", "pipes")),
        # The away question, said with the same words as the habit question: "should i leave my
        # heating on when i go on holiday" reads as "leave my heating on", which is the all-day row's
        # key, so the person planning a week away was told the timer wins - true of a house someone is
        # in, and the wrong advice for a house that will sit empty through a frost. The reply is the
        # away answer: low rather than off, and the water off as well.
        entry("heating-while-away",
              (("heating", "central heating", "boiler", "radiators", "radiator", "hot water",
                "thermostat", "heating system", "immersion", "pipes"),
               ("go away", "going away", "gone away", "away for", "when im away",
                "when i am away", "when were away", "while im away", "while i am away",
                "while were away", "on holiday", "holiday", "empty house", "house is empty",
                "nobody in", "no one in", "not at home for", "leave it on when",
                "leave the heating on when", "leave my heating on when", "turn it off when",
                # a frost line names the pipe, and the answer below is the one that says why it
                # must not go off
                "pipe", "pipes")),
              "Leave it on low rather than off if it will be cold: 12 to 15C, or the thermostat's "
              "frost setting, costs a few pounds a week and is far cheaper than a burst pipe, which "
              "is what a hard frost does to a cold house. Turn the water off at the stopcock before "
              "you go as well, and hot water can be switched off entirely. For a summer trip, or a "
              "house that will not drop below about 5C, off is fine.",
              avoid=("broken", "not working", "fault", "faulty", "leak", "leaking", "noise",
                     "noisy", "banging", "kettle", "carbon monoxide", "smell", "bleed",
                     "bleeding", "pressure", "condensation", "mould", "damp", "bill", "bills",
                     "tariff", "switch", "supplier", "standing charge", "price cap", "afford",
                     "debt", "arrears", "what temperature", "how warm", "degrees",
                     "what should i set", "how hot", "baby", "babies", "newborn", "toddler",
                     "cat", "cats", "dog", "dogs", "puppy", "kitten", "pet", "pets",
                     "why is my boiler", "why does my boiler", "stuck on", "wont turn off",
                     "will not turn off", "comes on by itself", "on by itself")),
        # "what time is electricity cheapest" was the science definition of electricity, and
        # "is it cheaper to run the washing machine at night" was the cost of one cycle: neither
        # answered the question, which is about the hour of the day and the tariff.
        entry("cheapest-hours", (("electricity", "energy", "power", "electric", "washing machine",
                                  "washer", "washers", "dishwasher", "tumble dryer", "dryer",
                                  "drier", "oven", "cooker", "appliance", "appliances",
                                  "immersion", "hot water", "economy 7", "economy7", "off peak",
                                  "off-peak", "time of use",
                                  # Most people do not say "washing machine" when they mean the
                                  # hour: "whats the cheapest time to do laundry" was a search punt
                                  # and "should i put the washing on overnight" was the overnight
                                  # SOAK (warm water and biological detergent, then wash it in the
                                  # morning), which is a different job with the same words. The
                                  # load and the laundry are what this row is about, so their
                                  # names are here.
                                  "laundry", "washing", "the washing", "put the washing",
                                  "a wash", "the wash", "wash a load", "a load of washing",
                                  "load of laundry", "clothes wash",
                                  # "can i do laundry overnight" was the overnight SOAK by a
                                  # point: the phrase is what puts the hour question in front.
                                  "do laundry", "laundry overnight", "washing overnight"),
                                 ("cheapest", "cheaper", "cheap", "cheaply", "night", "overnight",
                                  "at night", "off peak", "off-peak", "economy 7", "economy7",
                                  "time of use", "best time", "what time", "delay", "timer", "timed",
                                  "low rate",
                                  # the same question the other way round: "can i run a dishwasher
                                  # in the morning" is about the hour as much as the night one, and
                                  # the hour is what this row answers
                                  "morning", "in the morning", "evening", "in the evening",
                                  "afternoon", "in the afternoon", "during the day")),
              "Night is cheaper only on a two-rate tariff such as Economy 7 or an EV one; on a "
              "single rate the hour makes no difference at all, so check the tariff name on your "
              "bill. Where there is a cheap window, usually about half past midnight to half seven "
              "and charged at roughly a third to a half of the day rate, put the washing machine and "
              "the dishwasher on a delay. Whatever the tariff, never leave the tumble dryer running "
              "overnight, because of the fire risk.",
              # This row answers when an appliance is cheap to run, not where to get one: "where
              # can i get a cheap dishwasher" said "get" rather than "buy", so the avoid list
              # below did not catch it and the night tariff answered a question about a shop.
              guard=lambda understood: not asks_where(understood),
              # A tired body also says "energy" and a time of day: "im always low on energy in
              # the afternoons" was told which hours a two-rate tariff is cheap in, because
              # "energy" is in the first arm and "afternoon" in the second. The body words are
              # what say the question is the person's own energy and not the meter's.
              avoid=("tired", "tiredness", "tiring", "exhausted", "drained", "knackered",
                     "sluggish", "flagging", "sleepy", "no energy", "low on energy",
                     "low in energy", "energy levels", "my energy", "afternoon slump",
                     "cant keep my eyes open", "keep falling asleep", "always tired", "so tired",
                     "feel flat", "feeling flat", "run down", "worn out", "burned out",
                     "burnt out",
                     "car", "vehicle", "blanket", "shower", "bike", "bicycle", "buy", "buying",
                     # not the bare "best": "when is the best time to run the dishwasher" is this
                     # row's own question, and the word only says which-machine when it is one with
                     # the noun. The comparison shapes are named instead.
                     "best washing machine", "best dishwasher", "best dryer", "best tumble dryer",
                     "best oven", "best appliance", "best brand", "best buy", "best value",
                     "which washing machine", "which dishwasher", "which dryer", "which appliance",
                     "which", "boiler", "radiator",
                     # "is it cheaper to pay my energy bill by direct debit" is a way-to-pay line,
                     # and the night-hours answer is about when to run an appliance: the payment
                     # words hand it back to energy-bill, which is what answered it before the
                     # cheapest-hours entry existed.
                     # "tariff" is not in this list: "cheap tariff for electric heating" is the
                     # night-hours line itself, and holding it out sent that question to the price cap.
                     "pay", "paying", "paid", "payment", "direct debit", "debit", "standing charge",
                     "how do i pay", "way to pay", "supplier", "bill", "bills",
                     # which fuel is cheaper is a question about the hob, not about the hour: "is it
                     # cheaper to cook with gas or electric" was told about Economy 7. The cooking-fuel
                     # entry below answers it.
                     "hob", "hobs", "induction", "cook with", "cooking with", "gas or electric",
                     "electric or gas", "gas hob", "gas oven", "electric oven",
                     # which fuel is cheaper for the whole house is the heating-fuel row's: the
                     # hour of the day is not what "is gas cheaper than electricity" is asking.
                     "gas or electricity", "electricity or gas", "cheaper than electricity",
                     "cheaper than gas", "cheaper to heat", "cheapest way to heat",
                     "which is cheaper", "compare gas", "gas vs", "gas versus",
                     # "what time should i put a chicken in the oven" is a cooking time, not an hour
                     # of the day to run an appliance: it wants the roasting answer, and the oven in
                     # the key plus "what time" in the second arm held it here. A line that puts food
                     # in the oven is the cooking question, and the food is what says so.
                     "put a chicken", "put the chicken", "chicken in", "turkey", "chicken",
                     "roast", "roasting", "joint of", "casserole", "cake", "baking", "bake",
                     "scones", "biscuits", "pizza", "lasagne", "how long", "how many minutes",
                     "gas mark", "preheat", "at 180", "at 190", "at 200", "at 220",
                     # A complaint about a wash that is sitting in the machine is the wash's
                     # question, not the tariff's: "my washing smells after a night in the
                     # machine" was answered with Economy 7 once the laundry words were in this
                     # row's key, because "a night" is the second signal and "washing" the first.
                     # The dirt, the smell and the colour are what say the hour is not being
                     # asked about.
                     "smell", "smells", "smelling", "smelly", "musty", "stink", "stinks",
                     "stinky", "mouldy", "mildew", "damp wash", "service wash", "fluff", "lint",
                     "stain", "stains", "stained", "shrunk", "shrink", "shrinking", "gone grey",
                     "gone greyish", "went grey", "yellowed", "bobbled", "pilling", "oil stain",
                     "grease stain", "sweat", "blood", "sick", "nappy", "nappies"),
              bias=1),
        # The room question, not the bill one: "cheapest way to heat a room" and "my house is cold"
        # are about what to do tonight. A cold house that is also a sad one stays with the person.
        # "why is my flat so cold even with the heating on" is not the keep-warm answer: the
        # person already has the heating on and wants to know why it is not working. The keep-warm
        # row answered it with a 1kW electric radiator for one room, which is the answer to a
        # different question, and once the mood row and the body-cold row stood aside for a home
        # it was the only card left. Four causes cover nearly every one of these, cheapest
        # first, so the row names them in the order a person can check them.
        entry("cold-house-even-with-the-heating-on",
              (("cold", "colder", "freezing", "chilly", "perishing", "never gets warm",
                "never warms up", "wont get warm", "won't get warm", "not getting warm",
                "not warming up", "wont warm up", "won't warm up", "doesnt get warm",
                "doesn't get warm", "lukewarm"),
               ("house", "home", "flat", "room", "rooms", "bedroom", "living room", "sitting room",
                "kitchen", "heating on", "heating is on", "heatings on", "radiators are on",
                "radiator is on", "the heating", "central heating", "upstairs", "downstairs",
                # an outbuilding is the same four causes, and a cold shed, cellar or basement was
                # answered with the season instead: "why is my shed so cold" got the Earth's tilt.
                "shed", "sheds", "cellar", "cellars", "basement", "basements", "workshop",
                "workshops", "garage", "garages", "conservatory", "loft", "attic", "outbuilding",
                "outbuildings", "hallway", "porch", "caravan", "bungalow", "cottage")),
              ("Usually one of four things, and the cheap checks come first. Feel the radiator in "
               "the cold room: cold at the top is air, so bleed it; hot at the top and cold at the "
               "bottom is sludge; and a thermostatic valve turned right down or stuck shut does the "
               "same. Then look at where the thermostat sits - in a cold hall, or near a radiator "
               "or a window, it reads the wrong room and stops the heating before the bedrooms get "
               "warm. Then the boiler's flow temperature: 55 to 60C suits a condensing boiler, and "
               "set much lower than that the radiators never get hot enough on a cold day. If all "
               "that is right the heat is leaving - draughts under the doors, an open chimney, the "
               "loft hatch, and loft insulation under 270mm - and that is what to spend on next."),
              bias=1,
              # said with the fault already named, these are the fault rows, not the why row
              ask=("even with", "with the heating", "heating is on", "heating on", "heatings on",
                   "heating is running", "heating is going", "radiators are on", "radiator is on",
                   "turned up", "turn it up", "on full", "full blast", "all day", "all the time",
                   "never gets warm", "never warms up", "not getting warm", "why is", "why are",
                   "why does", "why do", "why wont", "why won't", "why am i"),
              # Whether to put the heating on, and what to set it to, is the heating advice
              # row's: "my house is cold should i put the heating on" was answered with the four
              # causes, while "18C is the usual living-room setting" is the answer it can act on.
              avoid=("should i put the heating on", "should i turn the heating on",
                     "shall i put the heating on", "shall i turn the heating on",
                     "do i need to put the heating on", "do i need the heating on",
                     "is it worth putting the heating on", "worth putting the heating on",
                     "what temperature", "what should i set", "how warm should",
                     "no heating", "heating is off", "heating off", "heating not working",
                     "heating isnt working", "heating isn't working", "heating has stopped",
                     "heating stopped", "heating wont come on", "heating won't come on",
                     "heating broken", "heating is broken", "broken boiler", "boiler is broken",
                     "pressure", "gauge", "fault code", "locks out", "wont fire", "won't fire",
                     "cold at the top", "cold at the bottom", "at the top", "at the bottom",
                     "bleed", "bleeding", "radiator key", "thermostatic valve",
                     "insulation", "loft insulation", "cavity wall", "double glazing",
                     "draught", "draughts", "draft", "drafts",
                     # a person, a plate, a pet or a car is not a house
                     "i am", "im ", "i feel", "always cold", "my feet", "my foot", "my hands",
                     "my hand", "fingers", "toes", "baby", "babies", "newborn", "toddler",
                     "disabled", "elderly", "pensioner", "old", "sick", "ill",
                     "car", "cars", "van", "engine", "washing machine", "oven", "microwave",
                     "food", "reheat", "leftovers", "tea", "coffee", "bath", "shower",
                     "pool", "greenhouse", "shed", "caravan", "hot tub",
                     # money and bills are their own rows
                     "bill", "bills", "cost", "cheap", "cheaper", "cheapest", "afford",
                     "price", "quote", "tariff", "energy")),
        entry("heat-a-room", (("heat", "heating", "warm", "warmer", "warmth", "cold", "freezing",
                               "chilly", "perishing",
                               # Cold said as a picture, which is how most people say it that
                               # way: "this office is like a fridge", "its like a freezer in
                               # here", "my flat is an ice box". The same claim as "the office is
                               # cold", and every one of them was falling to the floor because a
                               # cold room is never named in the line.
                               "like a fridge", "like a freezer", "like an ice box", "ice box",
                               "icebox", "like the arctic", "colder than a fridge",
                               "like a cold store",
                               # the heating switched off is said as the thing to do without, and
                               # the boiler rows were taking "keep warm with no heating" to a
                               # thermostat fault. Naming the shape here keeps the night-in answer.
                               "no heating", "heating off", "without heating",
                               "keep warm", "keeping warm", "stay warm", "staying warm"),
                              ("room", "rooms", "one room", "house", "home", "flat", "bedroom",
                               "living room", "sitting room", "tonight",
                               # Every other room a person heats: without these "how do i heat the
                               # kitchen" was the cleaning routine (it keys on "how"), and the
                               # bathroom, the garage and the conservatory had their own rows.
                               "kitchen", "bathroom", "garage", "conservatory", "shed",
                               "hall", "hallway", "spare room", "loft", "attic", "office",
                               # the rooms nobody sits in still get asked about: "why is my
                               # cellar so cold" and "the workshop is freezing" had no answer
                               # of their own and reached the body card's thyroid test
                               "cellar", "basement", "outbuilding", "outbuildings", "workshop",
                               "porch", "caravan",
                               # The room they are in, said without naming it: "its freezing in
                               # here" is the same question about the same room, and it got
                               # "Got it. Is there anything you'd like a hand with?"
                               "in here", "in this room", "this room"),
                              # "keep warm without the heating on" asks for this answer and names
                              # the heating only to leave it out, so the entry has to say the frame
                              # itself: the matcher takes a "without" clause off the line for every
                              # entry that does not (bot/knowledge/lookup.py, _frame_masked).
                              ("without heating", "without the heating", "without central heating",
                               "heating off", "no heating", "without putting the heating on",
                               "keep warm", "keeping warm", "stay warm", "staying warm",
                               # The same question said with the room as the verb's object rather
                               # than as a condition: "how do i heat my flat cheaply" was answered
                               # with the row-with-a-partner card (its "heated" reads as "heat")
                               # and "how do i warm up the flat" with the five-minute exercise
                               # warm-up. Both name the home and ask how to warm it, which is
                               # this row's own question.
                               # not bare "warm up": it is also what you do to soup, leftovers and
                               # a cold body before a run, and on its own it is enough to reach this
                               # row ("how do i warm up leftovers" became the room card). The room
                               # is named in the phrases below, which is what makes it this question.
                               "warm the", "warm my", "warm our", "warm this", "warm a",
                               "warm this room", "warm that room", "warm up the room",
                               "warm up the house", "warm up the flat", "warm up my",
                               "warm up our",
                               # the house as the object of the verb, which is the plainest way
                               # to ask: "how do i heat the house", "how do i heat my house".
                               # The things that heat their own water (a car, a washing machine,
                               # a shower) are held out below by name.
                               "heat the", "heat my", "heat our", "heat a", "heat this",
                               "heating the", "heating my", "heating our", "heating a",
                               "cheaply", "cheaper", "cheapest", "afford")),
              "Heat the room you are sitting in and shut the door: a 1kW electric radiator warms a "
              "small room for about 25p an hour, usually less than running the whole boiler for one "
              "person, and a heated throw costs about 3p an hour. Then stop the losses, a few pounds "
              "each: a brush strip on the door, a chimney balloon, foil behind the radiator. If the "
              "central heating is on, keep the flow at 55 to 60C and heat only the rooms you use.",
              # "cold" is also an illness, and "stuck at home with a cold" is a line about a person,
              # not about a house. The noun phrase is what tells them apart.
              # "on my own" and "by myself" used to be here, and they took the most ordinary way of
              # saying the problem: "i live by myself and the flat is cold" was a nod. They are not
              # needed - a line about being lonely is answered by the loneliness row on its own
              # words, and a line about a cold flat with them in it is this row's question.
              avoid=("lonely", "loneliness", "empty", "miss him", "miss her",
                     "since he", "since she", "passed away", "died", "funeral", "boiler", "radiator",
                     "bill", "bills", "mould", "damp", "carbon monoxide",
                     # the illness, spelled with a verb or a possessive: the bare phrase "a cold"
                     # also read "how do i heat a cold room", a house question, as a person's flu
                     "have a cold", "has a cold", "had a cold", "having a cold", "ive got a cold",
                     "i ve got a cold", "got a cold", "my cold", "his cold", "her cold",
                     "with a cold", "bad cold", "down with a cold", "a cold coming", "cold coming on",
                     "cold and flu",
                     "sore throat", "sneezing", "cough", "flu", "temperature", "unwell", "sick",
                     # a house the person is trying to keep COOL is the other half of the year and
                     # the other question: "how do i keep the house cool in the heat" was told to
                     # buy an electric radiator, because it has "heat" and "house" in it.
                     "cool", "cooler", "cooling", "keep cool", "keep it cool", "stay cool",
                     "heatwave", "heat wave", "hot weather", "hot day", "hot nights",
                     # keeping the heat out of a room is the cooling row's question, and the
                     # words "heat" and "flat" are enough for this one to claim it
                     "keep the heat out", "heat out", "stop the sun", "sun heating", "block the sun",
                     "the sun coming in", "sun comes in", "sun through",
                     # Keeping warm OUT OF DOORS is a clothes question, not a heating one: "how do i
                     # keep warm cycling in winter" and "... at a football match" were both told to
                     # buy an electric radiator. The activity is what tells them apart, and the
                     # clothing notes (keep-warm-moving / keep-warm-standing) answer them.
                     "cycling", "cycle", "bike", "bicycle", "motorbike", "motorcycle",
                     "scooter", "ride", "riding", "commute", "commuting", "run", "running",
                     "jog", "jogging", "walk", "walking", "hike", "hiking", "football",
                     "rugby", "match", "watching", "touchline", "sidelines", "fishing",
                     "golf", "ski", "skiing", "camping", "festival", "outdoors", "outside",
                     "dog walk", "school run",
                     # A thing that heats its own water is not a room: "my washing machine isnt
                     # heating the water" and "no heat in my car" both came here once the home
                     # shapes were in the key, and each has its own answer.
                     "car", "cars", "van", "vehicle", "motorhome", "caravan", "washing machine",
                     "washer", "dishwasher", "tumble dryer", "dryer", "drier", "cooker",
                     "shower", "bath", "hot tub", "pool", "swimming", "greenhouse", "hot water",
                     "immersion", "water", "kettle",
                     # A person or a plate warms up too, and both have their own answer: "how do i
                     # warm up leftovers" and "how do i warm up soup" reached this row on the bare
                     # verb, and "does warming up prevent injury" wants the exercise note.
                     "leftover", "leftovers", "soup", "reheat", "reheating", "microwave",
                     "warm up before", "warming up before", "warm up prevent", "warming up prevent",
                     "before a run", "before exercise", "prevent injury", "prevent injuries",
                     # the bedroom has its own answer, and it is the more specific one: a bedroom at
                     # 16 to 18C for sleep, said there, not the sit-in-one-room answer.
                     "bedroom", "bedrooms", "bed room", "for sleep", "sleeping", "sleep in",
                     # the appliance being asked about, and not the picture of a cold room
                     ) + THE_APPLIANCE_ITSELF,
              # Two stand-downs hold here and both are wanted. A body part being warmed is the
              # compress card's question, not a room's ("heat my back or ice it" was told to buy a
              # 1kW electric radiator for the room it was sitting in). And a row or a discussion
              # that got heated is an argument, not a cold room ("things got heated in the
              # kitchen" was told to buy the same radiator).
              guard=lambda u: _a_room_being_heated(u)
              and not_the_heat_of_an_argument(u)),
        # A squeak or a rub is the hinge, the latch or a door that has dropped: the two fixes are the
        # ---------------------------------------------------------------- doors, locks, hinges
        # People describe these six by the symptom and the part, never by the fix: "the door
        # squeaks", "my key is stiff", "the handle is loose". The part and the symptom are what
        # tell them apart, so each entry keys on both and steps aside for the household ones
        # (a fridge door that will not shut, a washing-machine door that is locked, a car door).
        # "the tap in the bathroom is loose" and "my kitchen cupboard door is hanging off" were both
        # said back to the person as a note. Each is a two-minute job with a screwdriver, so the tell
        # in each line is the part that has come adrift, not the word for the room.
        entry("tap-loose",
              (("tap", "faucet", "mixer tap", "monobloc"),
               ("loose", "wobble", "wobbles", "wobbly", "moves", "moving", "swivels", "spins",
                "spinning", "swinging", "not fixed", "come away", "came away", "lifted")),
              "A tap that wobbles is held by one nut underneath: get under the sink and tighten the "
              "back nut on the threaded shank with a basin wrench or a long spanner, or the fixing "
              "plate on a monobloc. Once it is tight, check the two flexible tails have not started "
              "to weep. If the nut has pulled the thread through a thin worktop, a repair plate costs "
              "a few pounds and spreads the load.",
              avoid=("drip", "dripping", "leak", "leaking", "pressure", "hot water", "cold",
                     "scale", "limescale")),
        entry("cupboard-door-hinge",
              (("cupboard door", "cupboard doors", "cabinet door", "kitchen door", "kitchen doors",
                "hinge", "hinges", "door hanging", "door dropped"),
               ("hanging off", "hang off", "hangs off", "hanging", "loose", "dropped", "sagging",
                "sag", "came off", "come off", "falling off", "screws", "screw", "pulled out",
                "stripped", "wont close", "won't close", "rubbing")),
              "Tighten the screws holding the hinge plate first, and if they spin, take them out and "
              "pack the holes with two broken matchsticks and wood glue before driving them back in. "
              "For a door that has dropped, the two screws nearest the door edge lift it: slacken the "
              "outer ones and turn the inner ones to raise the front. Move the plate 20mm up or down "
              "only if the wood has gone."),
        entry("heating-on-by-itself",
              (("heating", "boiler", "radiators", "radiator", "central heating"),
               ("by itself", "on its own", "comes on", "come on", "came on", "turns on", "turned on",
                "random times", "middle of the night", "at night", "when i havent", "even when its off",
                "when its off",
                # The same fault the other way round: a boiler or a heating system that will not
                # stop is the same valve or programmer as one that starts on its own, and the
                # checks are the same checks. "why is my boiler always on" and "my heating wont
                # turn off" were a plumber suggestion, and "my boiler is running all the time"
                # was answered with the price of gas.
                "always on", "always hot", "always running", "on all the time",
                "running all the time", "wont turn off", "won't turn off", "wont go off",
                "won't go off", "wont switch off", "won't switch off", "wont shut off",
                "never turns off", "never goes off", "not turning off", "keeps running",
                "keeps firing", "keeps going", "stays on", "staying on", "on in the summer",
                "hot in the summer", "stuck on", "jammed on", "still on", "left on",
                "on all day", "on all night",
                "will not turn off", "will not go off", "will not switch off",
                "will not shut off", "will not stop", "doesnt turn off", "doesn't turn off",
                "doesnt go off", "doesn't go off", "never off", "never stops", "non stop")),
              "Check the programmer first: a light on ADVANCE or ON rather than AUTO is a button "
              "pressed by accident, and a room thermostat left high keeps the heating running. If "
              "the radiators heat up when the hot water is on, the diverter valve has stuck and wants "
              "replacing - about 150 to 250 pounds fitted, and worth doing before winter. A frost "
              "stat firing on a cold night is normal.",
              avoid=("not working", "broken", "cold", "no heating", "pressure", "noise", "noisy",
                     "bleed", "banging", "kettling", "thermostat setting", "how much",
                     # a bill question is about what it costs to leave the heating on, not about
                     # why it will not stop
                     "cost", "costs", "expensive", "bill", "bills", "cheaper", "save",
                     "saving", "money", "efficient", "efficiency", "how long", "every day",
                     # "is it safe to leave the boiler on all night" asked whether it is safe, not
                     # why it will not stop, and it had its own card
                     "safe", "safety", "unsafe", "dangerous", "risk", "carbon monoxide",
                     "smell gas", "yellow flame", "leave it on"),
              # "my boiler is running all the time" reached the row that says how long a machine
              # takes to do a job on the word "time", and "my heating stays on all night" reached
              # the hot-night card on "night". Neither is as specific as the valve and programmer
              # this row is about, so it wins the tie.
              bias=3),
        entry("door-rubbing", (("door", "doors", "front door", "back door", "shed door",
                                "bedroom door", "bathroom door", "internal door", "cupboard door"),
                               ("sticking", "sticks", "stuck", "rubbing", "rubs", "dragging", "drags",
                                "scrapes", "swollen", "swelling", "swelled", "warped", "wont close",
                                "won't close", "wont shut", "won't shut", "hard to close", "catching",
                                "jammed", "have to slam", "has to be slammed")),
              "A door that drags or will not shut is usually swollen from damp in winter, or has "
              "dropped on its hinges because a screw pulled out. Give the season a fortnight first, "
              "with the heating on or a dehumidifier in the room, because many free up on their own. "
              "If it has dropped, tighten the top hinge screws, or replace them with longer ones. "
              "Otherwise take a millimetre at a time off the edge where the paint has rubbed bright, "
              "and seal the bare wood afterwards so it does not take in water and swell again.",
              # Main's `squeaky-door` also keys "sticking" and "rubbing" and sits later in the file
              # with bias=1, so on a tie it took every swollen or dragging line. The damp-and-plane
              # answer is the one for those, and the bias is what makes it win; the squeak-only lines
              # still reach `squeaky-door` because no word of this entry's second key is in them.
              bias=3,
              avoid=("lock", "locks", "key", "keys", "car", "cars", "van", "fridge", "freezer",
                     "oven", "microwave", "dishwasher", "washing machine", "washer", "dryer",
                     "drawer", "drawers", "cupboard", "wardrobe", "glass", "window", "windows",
                     # a dog that will not shut up is a noise question, and "shut up" alone was
                     # enough to send "next door's dog wont shut up" to the swollen-door card
                     "dog", "dogs", "puppy", "barking", "bark", "barks", "cat", "cats", "meowing",
                     "neighbour", "neighbours", "neighbor", "neighbors", "next door", "upstairs",
                     "downstairs", "shut up",
                     # a door that will not shut is not a door that swings hard: a stiff key is
                     # the barrel card's, and "oil the hinges" is the wrong answer to it
                     "key", "keys", "lock", "locks", "keyhole", "barrel", "handle", "latch")),
        entry("door-lock-stiff", (("lock", "locks", "door lock", "barrel", "deadlock", "yale",
                                   "latch", "key", "keys", "front door",
                                   # a key that will not go into the keyhole is a dirty or worn
                                   # keyway, and "i cant get my key in the lock" fell through to
                                   # the locked-out card about spares and a locksmith
                                   "key in the lock", "key into the lock", "key in my lock",
                                   "key wont go in", "key won't go in", "key does not go in",
                                   "get my key in", "get the key in"),
                                  ("stiff", "sticky", "stuck", "sticking", "sticks", "jammed",
                                   "hard", "wont turn",
                                   "won't turn", "grinding", "tight", "difficult", "gritty",
                                   "wont go in", "won't go in", "turning",
                                   # "my front door key sticks" is the same barrel as "my lock is
                                   # stiff", and "how do i stop a door key sticking in the lock"
                                   # was reaching `change-a-lock` on "how" and "lock"
                                   "stiffen", "stiffens", "stiffened",
                                   "seizing", "seized", "grates", "grating", "rough",
                                   # a key that will not go into the keyhole is this card, not
                                   # the press-the-door card and not the composer's locked-out
                                   # line: "i cant get my key in the lock" got both
                                   "in the lock", "into the lock", "in my lock", "into my lock",
                                   "get my key in", "get the key in")),
              _door_lock_stiff,
              bias=2,
              avoid=("car", "cars", "van", "bike", "bicycle", "suitcase", "case", "padlock", "safe",
                     "lost", "lost my keys", "locked out", "locked in", "keys locked", "cut a key",
                     "laptop", "keyboard", "password", "account", "windows", "drawer", "lockbox",
                     "post box", "postbox")),
        # A key that has snapped off in the barrel is not a lock to buy and not a lock that is
        # stiff: the piece is still in there and every further turn pushes it deeper. This row
        # owns the line, and `change-a-lock` and `door-lock-stiff` pass on it.
        entry("key-broken-in-lock",
              (("key", "keys", "door key", "front door key", "spare key", "piece of key",
                "half a key", "broken key", "key blade"),
               ("snapped", "snap", "snapped off", "snapped in", "broke off", "broken off",
                "broke in", "broken in", "sheared", "twisted off", "bent", "stuck", "jammed",
                "stuck in the lock", "stuck in my lock", "jammed in", "half in", "get it out",
                "get out", "remove", "removing",
                # "how do i get a broken key out of a lock" scored 3 on the phrase and reached the
                # laptop keyboard card on "keyboard"-like "key" + "broken", so the pulling out is
                # said in the words people use for it
                "out of the lock", "out of my lock", "out of the door", "out of the barrel",
                "pull out", "pull it out", "dig out", "extract", "extracting", "out of")),
              "Stop turning it: the piece in the barrel is what the pins are holding, and every "
              "extra turn pushes it further in. Put a drop of WD-40 or graphite at the keyway, then "
              "grip whatever is proud with needle-nose pliers or thin side cutters, pull straight "
              "out rather than sideways, and jiggling the door handle while you pull helps. A short "
              "piece just inside can be walked out with the thin blade of a jigsaw or a coping saw "
              "slid alongside it. If it is in past the face of the barrel, it is a locksmith: about "
              "\u00a360 to \u00a3120 to drill and replace the cylinder, and keep the door on the "
              "latch until they come. Do not glue anything to it and do not push a second key in.",
              # a key that belongs to a car or a padlock is not this row, and a lost key is the
              # lost-keys card's
              avoid=("car", "cars", "van", "bike", "bicycle", "motorbike", "suitcase", "padlock",
                     "safe", "laptop", "keyboard", "password", "account", "phone", "lost",
                     "lost my keys", "mislaid", "locked out", "locked in", "cut a key", "spare key",
                     "cut a spare", "piano", "map", "answer", "code"),
              bias=3),
        # The keys are lost and there is nothing to open yet, so the way back in comes before any
        # searching. "lost" plus a key word is the key, and every way of being stiff stays with
        # `door-lock-stiff`, which passes on "lost" itself.
        entry("lost-house-keys",
              (("keys", "key", "keyring", "key ring", "house keys", "door key", "front door key",
                "keys to the house", "set of keys"),
               ("lost", "lose", "losing", "mislaid", "misplaced", "missing", "gone",
                "cant find", "cannot find", "can't find", "no idea where", "nowhere",
                # A key nobody has is the same evening as a key that is lost, however it is put:
                # "how do i start my car without the key" and "how do i get in without my keys"
                # are the searching-and-locksmith question, and the line says it without ever
                # using the word lost.
                "without the key", "without a key", "without my keys", "without keys",
                "without the keys", "no key", "dont have the key", "don't have the key",
                "not got the key", "havent got the key", "haven't got the key")),
              _lost_keys,
              # keys lost *inside* the house are a searching question, and the composer already has
              # the retrace-your-steps answer for those
              avoid=("stiff", "sticky", "jammed", "wont turn", "won't turn", "hard to turn",
                     "grinding", "piano", "keyboard", "laptop", "computer", "password",
                     "account", "map", "answer", "code", "locked in", "locked out",
                     "cut a key", "cut a spare", "car battery", "remote", "fob battery",
                     "in the house", "in my house", "in the flat", "in my flat", "at home",
                     "somewhere in", "in my bag", "in my pocket", "in the car", "in the office",
                     "down the back of"),
              bias=2),

        # A lock that will not turn is the stiffness row above; a lock the person wants to change,
        # fit or has broken is this one, and "how do i change the lock on my front door" was getting
        # the phone's screen-timeout setting.
        entry("change-a-lock", (("lock", "locks", "door lock", "cylinder", "euro cylinder",
                                 "barrel", "mortice", "mortise", "deadlock", "night latch", "yale"),
                                ("change", "changing", "replace", "replacing", "fit", "fitting",
                                 "new", "broken", "broke", "snapped", "put on", "install", "myself",
                                 "upgrade", "key", "keys", "how"),
                                # The phone's screen-lock setting keys "how" and "change" too, and a
                                # bare "how do i change a lock" scored one under it. The phrase is
                                # the job itself, so it carries the line.
                                ("change a lock", "change the lock", "change my lock",
                                 "change the lock", "change the locks", "replace a lock",
                                 "replace the lock", "new lock", "fit a lock", "fit a new lock",
                                 "broken lock", "lock broken", "change the barrel",
                                 "change the cylinder")),
              "Measure the old cylinder before you buy one: the length each side of the fixing screw, "
              "and whether it sits flush with the door or sticks out. Undo the retaining screw on the "
              "door edge, put the key in and turn it slightly, and the cylinder slides out; the new one "
              "goes in the same way, with the key in it. Fifteen minutes with a screwdriver, the door "
              "left open while you work, and about fifteen to thirty pounds for a kite-marked one.",
              # A lock the person wants to swap is not a door that will not open, and "how do i change
              # the lock on my front door" was reaching the swollen-door card.
              bias=2,
              avoid=("car", "cars", "van", "bike", "bicycle", "suitcase", "padlock", "safe",
                     "locked out", "locked in", "keys locked", "cut a key", "spare key", "laptop",
                     "phone", "keyboard", "password", "account", "windows", "drawer", "lockbox",
                     "post box", "postbox", "stiff", "jammed", "wont turn", "won't turn",
                     "sticking", "sticks", "stuck", "hard to turn", "gritty", "grinding",
                     "screen", "sim", "pin", "app",
                     # A lock the person cannot get through is not a lock they are buying: "i locked
                     # myself out" and "how do i open a locked door" were both told to measure the
                     # cylinder, and the phrase forms of "locked out" do not inflect.
                     # the phrase is the whole ask: "can i change a lock myself" says "lock myself"
                     # as plainly as "i locked myself out" does, so only the out-phrase stands down
                     "locked myself out", "lock myself out", "locks myself out", "locking myself out",
                     "locked out of", "lost my keys", "lost the keys", "open a locked", "locked door",
                     "wont open", "won't open",
                     # Somebody asking who to call has already decided not to do it themselves:
                     # "who do i call about a broken lock" was told to measure the old cylinder,
                     # and the who-to-call row is the answer, with the locksmith it names.
                     "who do i call", "who should i call", "who can i call", "who could i call",
                     "who do i ring", "who should i ring", "who to call", "who to ring",
                     "who do i get", "someone to call", "someone to ring", "locksmith",
                     # a key that will not turn, and above all a key that has broken off inside,
                     # is not a lock to buy: "how do i get a broken key out of a lock" was told to
                     # measure the old cylinder, and the stuck-key card below is the answer
                     "sticking", "sticks", "stuck in the lock", "stuck in my lock",
                     # "i cant get my key in the lock" was told to measure the old cylinder; a key
                     # that will not go in is the stiff keyway below, not a lock to buy
                     "get my key in", "get the key in", "cant get my key", "can't get my key",
                     "key wont go in", "key won't go in", "key does not go in", "key in",
                     "key stuck", "key snapped", "key broke", "key broke off", "broken key",
                     "snapped off", "snapped in", "broke off in", "broke in the lock",
                     "half a key", "piece of key", "jammed in the lock", "key jammed")),
        # "How do i stop locking myself out" is a habit question, not a lock to change and not a
        # phone setting: the screen-timeout row keys "stop" and "locking" and was taking it.
        entry("stop-locking-yourself-out",
              (("locked myself out", "locking myself out", "lock myself out", "locks myself out",
                "locked out again", "lock myself out again", "keys locked inside",
                "keys locked in the house", "keys locked in my flat", "keys are locked inside",
                "keep locking myself out", "always locking myself out", "keys locked in",
                "leave my keys", "left my keys", "forget my keys", "forgot my keys"),
               ("stop", "again", "keep", "keeps", "always", "how do i", "how can i", "prevent",
                "avoid", "happen", "happening", "trick", "not do it")),
              "Put the key in one place that you walk past on the way out - a hook inside the front "
              "door - and nowhere else, because the pockets, the bag and the coat are what lose it. A "
              "spare with a neighbour or family is free and saves the locksmith, and a key safe by the "
              "door (about twenty pounds, screwed on, with a code) covers the rest. If you rent, ask "
              "the landlord for a second key: yours to pay for, and almost always allowed.",
              bias=1,
              # Asking how to stop it is the habit question; "i locked myself out again" is a person
              # standing outside the door, and the composer has the way-in lines for that, so the
              # entry needs one of these words before it may answer.
              ask=("stop", "stops", "prevent", "avoid", "keep on", "keep", "keeps", "always",
                   "never again", "trick", "habit", "how do i not", "how can i not"),
              avoid=("car", "cars", "van", "vehicle", "boot", "phone", "screen", "sim", "pin",
                     "password", "account", "email", "facebook", "laptop", "change the lock",
                     "new lock", "broken lock", "lost my keys", "lost the keys", "cant find",
                     "can't find")),
        entry("door-handle-loose", (("handle", "handles", "door handle", "knob", "knobs",
                                     "door knob", "latch", "spindle", "grub screw"),
                                    ("loose", "wobbly", "wobbles", "wobble", "rattles", "rattle",
                                     "spins", "spinning", "fallen off", "fell off", "came off",
                                     "come off", "dropped")),
              "The grub screw on the neck of the handle has worked loose: there is a small screw there, "
              "sometimes under a cap you can flick off, and tightening it onto the spindle takes two "
              "minutes with a small screwdriver or an Allen key. If it keeps coming loose, put a dab of "
              "thread-lock on the spindle, or a sliver of tape. A handle that spins without opening the "
              "door has lost or snapped its spindle, and a new handle is about ten pounds.",
              avoid=("suitcase", "bag", "case", "pan", "saucepan", "frying pan", "pot", "cup", "mug",
                     "tap", "taps", "kettle", "oven", "fridge", "freezer", "drawer", "window",
                     "wheelbarrow", "lawnmower", "drill", "tool", "bike", "car", "doorbell",
                     "knife", "saw", "umbrella")),
        entry("window-painted-shut", (("window", "windows", "sash", "sash window", "casement",
                                       "upvc window", "upvc windows"),
                                      ("painted", "stuck", "seized", "jammed", "swollen",
                                       "stiff")),
              "It is paint gluing the sash to the frame: run a sharp knife, held flat, round the join "
              "between the frame and the opening sash to cut the paint film, then work a thin scraper "
              "or a wide chisel gently into the gap and ease the window open rather than forcing the "
              "handle. Once it is open, sand the paint off the meeting faces and rub a candle or "
              "silicone spray along them. Never lever against the glass.",
              bias=1,
              # "how do i paint a room with no windows" is a decorating question: "painted" plus
              # "windows" handed it here, where the answer is about a sash that will not open. The
              # painting rows own those lines, so this one stands down on what a painter says.
              avoid=("car", "cars", "van", "screen", "phone", "laptop", "computer", "software",
                     "browser", "windscreen", "shower", "clean", "cleaning", "curtain", "curtains",
                     "blind", "blinds",
                     # "how do i paint a room with no windows" is a decorating line: the window is
                     # only what the room has not got, and the paint-glued-sash answer is about a
                     # window that will not open. Main answered it with the Windows disk steps.
                     "paint a room", "painting a room", "paint the room", "painting the room",
                     "paint a wall", "paint a ceiling", "decorating", "decorate", "roller",
                     "undercoat", "emulsion", "paint the walls", "no window", "no windows",
                     "without a window", "windowless",
                     # a window frame that wants painting is a painting job, and both window-fault
                     # rows were taking it: "how do i paint a window frame" got the cut-the-paint-
                     # film answer twice over, which never mentions a brush
                     "paint a window", "painting a window", "paint my window", "paint the window",
                     "paint window", "painting the windows", "paint the windows", "repaint",
                     "painting a window frame", "paint a window frame", "brushes", "brush",
                     "paint a sash", "painting a sash", "paint the sash", "paint a casement",
                     "paint the frame")),
        entry("door-slam-wind", (("door", "doors", "front door", "back door", "porch", "gate"),
                                 # no "draught" here: a cold draught under a door is a gap with its
                                 # own answer, and this row is about a door that moves. "how do i stop
                                 # a draught from the front door" got the holder-and-closer card.
                                 ("slam", "slams", "slamming", "bangs", "banging", "bang", "rattles",
                                  "rattling", "wind", "blows")),
              "A door that slams in the wind wants a holder or a closer, not a shut window: a "
              "hook-and-eye or a door holder on the frame keeps it open, and an overhead closer set to "
              "slow the last few inches stops it banging shut. Rubber bumpers on the stop take the "
              "rattle out of the catch, and a wedge under the bottom holds a door that swings. A front "
              "door that rattles is usually the latch plate, and a wrap-around striker plate or a strip "
              "of foam behind it stops that.",
              bias=2,
              avoid=("car", "cars", "van", "garage", "cupboard", "fridge", "oven", "microwave",
                     "washing machine", "dishwasher", "drum", "tumble dryer", "doorbell", "baby",
                     "toddler", "child",
                     # a swollen door is not a windy one: it rubs, and it gets the planing answer
                     "swollen", "swelling", "swelled", "warped", "sticking", "stuck", "rubbing",
                     "drags", "dragging", "have to slam", "has to be slammed",
                     # a draught is the gap round the door, and "how do i stop a draught under a
                     # door" got the holder-and-closer answer: that is the cleaning row's, and this
                     # one keeps the slam, the bang and the rattle.
                     "draught", "draughts", "draft", "drafts", "draughty", "drafty", "cold air",
                     "cold coming", "lets in", "letting in", "coming under the door",
                     "under the door", "around the door", "round the door", "draught excluder",
                     "excluder",
                     # a finger or a toe in the door is an injury, not a door that swings:
                     # "my fingernail is black after i slammed it in the door" was answered with
                     # the holder-and-closer card, because "door" and "slammed" are its two keys
                     "my finger", "my fingers", "my thumb", "my hand", "my toe", "my foot",
                     "fingernail", "fingernails", "toenail", "toenails", "nail", "nails",
                     "black", "bruise", "bruised", "purple", "blood",
                     # someone shutting a door in a temper is not a door that moves in the wind:
                     # "he slammed the door" after a row got the holder-and-closer card, and the
                     # door in it is the person at the end of the row, not a hinge
                     "slammed the door", "slams the door", "door on me", "door in my face")),
        # same whether a person says "squeaks", "creaks" or "keeps sticking". Named things that squeak
        # and are not doors (shoes, a chair, a bike) are kept out.
        entry("door-wont-open", (("wont open", "won't open", "will not open", "wont budge",
                                  "won't budge", "cant open", "can't open", "cannot open",
                                  "stuck", "stuck shut", "jammed", "jammed shut", "locked",
                                  "locked in", "locked in my flat", "locked in my house",
                                  "locked in the house", "locked in my room", "trapped in my flat",
                                  "shut in my room", "swollen", "swelled", "warped",
                                  "cant get out", "can't get out", "wont turn", "won't turn",
                                  "wont close", "won't close",
                                  # "i cant get in my front door" is the same shut door as "my
                                  # door wont open", and it fell through to the composer's
                                  # locked-out line about spares and a locksmith
                                  "cant get in", "can't get in", "cannot get in", "wont let me in",
                                  "won't let me in", "key wont work", "key won't work"),
                                 # No bare place word here: "i cant get out of the house" is the
                                 # going-out line, and this answer must not take it. A flat or a
                                 # room only reaches this entry with a door or a lock in the line.
                                 ("door", "doors", "front door", "back door", "door lock",
                                  "the lock", "latch", "handle", "deadlock", "mortice", "yale",
                                  "shed door", "porch")),
              "Start with the lock: press the door inwards while you turn the handle, and try "
              "lifting the handle up, because plenty of doors lock that way and half a turn frees "
              "them. If the handle turns loosely and nothing clicks, the spindle inside has gone "
              "and that is a locksmith. A door swollen by damp usually frees with a firm push at "
              "shoulder height while someone turns the handle, or with a thin card slid in on the "
              "latch side; if it will not shut at all, plane a millimetre off the edge that rubs. "
              "If it is rented, ring the landlord or a locksmith who quotes on the phone - and if a "
              "child or anyone is shut in, ring 999 rather than fight the door.",
              avoid=("squeak", "squeaks", "squeaky", "squeaking", "creak", "creaks", "creaking",
                     # a key that will not go into the keyhole is the stiff keyway card's, not a
                     # door that will not open: "i cant get my key in the lock" was answered with
                     # the press-the-door-and-lift-the-handle card
                     "key in the", "key into the", "get my key", "getting my key", "keyway",
                     "key wont go", "key won't go", "wont go in", "won't go in",
                     "oil", "oiling", "hinge oil", "draught", "draughts", "draft", "paint",
                     "painting", "painted", "decorate", "decorating", "letterbox", "letter box",
                     "childproof", "child proof", "cat flap", "pet flap", "car door", "van door",
                     "garage door", "keypad", "porch light", "doorbell", "door bell", "camera",
                     "handle a", "difficult", "slam", "slamming", "bang", "bangs",
                     # an oven, a fridge or a washer door is an appliance question with its own
                     # answers, and this row's lock-and-plane advice is wrong for all of them
                     "oven", "cooker", "fridge", "freezer", "microwave", "washing machine",
                     "dishwasher", "tumble dryer", "cupboard", "wardrobe", "cabinet"),
              bias=1),
        # "the gate is hanging off", "the shed door is broken" and "the hinge on my cupboard is
        # loose" are all the same fault in different furniture: a hinge screw has pulled out of soft
        # wood. Nothing answered them (the neutral pool said "Got it"), and `door-rubbing` is the
        # damp-and-plane answer for a door that drags, not this. The fault word and the hinged thing
        # are both in the line, so the answer is the repair, not the diagnosis.
        entry("hinge-sag",
              (("hanging off", "hanging by", "hanging open", "sagging", "sag", "sags",
                "has dropped", "had dropped", "is dropping", "keeps dropping", "drooping", "loose",
                "loosened", "wobbly", "wobbling", "wobble",
                "coming off", "came off", "fallen off", "fell off", "pulled out", "ripped off",
                "blown down", "blew down", "blown off", "knocked down", "snapped", "broken",
                "breaks", "broke", "split"),
               ("gate", "gates", "garden gate", "side gate", "gate post", "shed door", "shed",
                "door", "doors", "cupboard", "cupboards", "cupboard door", "cabinet",
                "cabinet door", "wardrobe", "wardrobe door", "hinge", "hinges", "gate post",
                "gatepost")),
              "Nine times in ten a sagging gate, shed door or cupboard door is a hinge screw that has "
              "pulled out of the wood, not the hinge wearing out. Take the weight off the free "
              "corner, pack the old screw holes with glued matchsticks or a sliver of dowel and screw "
              "back in, or move the hinge 10cm along with longer screws. If the wood round the hinge "
              "is rotten or the hinge is torn, fit a new hinge onto sound timber - and if the post "
              "moves in the ground, brace or replace the post.",
              # the other door answers own their own faults (a lock, a handle, a draught, a squeak, a
              # swollen edge) and a shed or greenhouse roof is a leak, not a hinge
              ask=("hinge", "hinges", "hinged", "gate", "gates", "garden gate", "side gate",
                   "shed door", "shed", "door", "doors", "cupboard", "cabinet", "wardrobe",
                   "gate post", "gatepost"),
              avoid=("roof", "roofs", "leaking", "leak", "leaks", "glass", "glazing", "window",
                     "windows", "lock", "locks", "key", "keys", "handle", "handles", "knob",
                     "latches", "latch", "squeak", "squeaks", "squeaky", "creak", "creaks",
                     "creaking", "draught", "draughts", "draft", "paint", "painted", "paintwork",
                     "swollen", "swelling", "warped", "damp", "garage door", "car door",
                     "van door", "car", "van", "fridge", "freezer", "oven", "drawer", "drawers",
                     "cat flap", "pet flap", "letterbox", "letter box", "doorbell", "door bell",
                     # "dropped" is a fault word only on a hung thing: what people drop is a phone,
                     # keys or a purse, and "i dropped my phone in the shed" was taking this answer
                     "phone", "phones", "mobile", "wallet", "purse", "glasses", "keys", "keyring",
                     "dropped my", "dropped it", "dropped a", "dropped her", "dropped his",
                     # "fence between me and next door is broken" is about the fence: the words of
                     # "next door" are not a door of anyone's
                     "next door", "nextdoor")),
    ]
