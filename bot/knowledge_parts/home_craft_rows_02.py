"""Rows 2 of 10 of `home_craft.entries()`: `water-less` .. `washing-outside`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _a_gauge_reading,
    _not_a_drying_inside_question,
    _the_explainer_keeps_the_explainer,
)


def rows():
    from ..knowledge.home import (
        MACHINE_SOUNDS, NOISE_WORDS, _boiler_noise, _the_boiler_is_not_the_fault,
        _heating_goes_cold, _heat_pump_answer, _not_a_machine_that_has_gone, _radiator_not_hot,
        entry
    )
    return [
        # Using less of it. The house is full of answers about water going where it should not - a
        # tap dripping, a loo running, a stopcock, a boiler - and none about using less of it, so
        # "how do i use less water" and "how do i save water at home" had no answer at all once the
        # dry-eye row stopped taking them on the word "water". The two that matter are the shower and
        # the dripping tap, and both are a washer or a timer rather than a new bathroom, so the card
        # leads with those and gives the free habits after them.
        entry("water-less",
              (("use less water", "using less water", "uses less water", "save water", "saving water",
                "water saving", "reduce water", "reduce my water", "reduce our water",
                "cut water use", "cut my water use", "cut our water use", "wasting water",
                "waste water", "water waste", "water use", "water usage", "using so much water",
                # the saving put as waste rather than as saving: "how do i waste less water" had
                # no phrase of its own here, and the bare "waste" in the sink-trap row's key sent
                # it to a bowl under the trap
                "waste less water", "wasting less water", "waste less water at home",
                "use so much water", "less water at home", "save on water"),
               # the ask words, and what the household is: a line naming a shower or a garden already
               # has its own card, so neither is here
               ("how", "ways", "tips", "help", "stop", "much", "home", "house", "household",
                "family", "flat", "ours", "we use", "reduce", "cut", "save", "saving", "less")),
              "A shower of five minutes rather than ten saves about 40 litres a time, and a dripping "
              "tap wastes around 5,500 litres a year - both are a washer or a shorter timer, not a new "
              "bathroom. After those, run the washing machine and the dishwasher only when they are "
              "full (a half load uses nearly the same water as a full one), put a water butt on the "
              "downpipe for the garden instead of a hose, and drop a cistern bag in an old loo, which "
              "saves a litre or two a flush. A water meter is free to have fitted in most of the UK "
              "and usually cuts a bill for one or two people, though a big family can pay more on one.",
              # drinking it, a garden that needs watering, and the water going somewhere it should not
              # are all other answers, and so is a cooking instruction: "use a little less water than
              # the packet says" is the rice, not the meter.
              # "watering" is not in this list even though the garden rows own it: the matcher
              # folds it onto the bare "water", so an avoid word of it denies every line that says
              # "save water" at all.
              avoid=("drink", "drinking", "thirsty", "thirst", "safe to drink", "plants", "plant",
                     "lawn", "water the", "water my", "water butt", "rain barrel",
                     "sprinkler", "irrigation", "hose", "pool", "swimming", "fish tank", "aquarium",
                     # the garden has its own watering card, and it answers "how do i use less water
                     # in the garden" better than a card about the meter does
                     "garden", "gardening", "allotment", "flowerbed", "flower bed", "hanging basket",
                     # and a bath against a shower is the `bath-or-shower` card, which reads "uses
                     # less water" as its own ask: that row sits later in this list, so without the
                     # fence the comparison would come to the household card instead
                     "a bath or a shower", "bath or a shower", "bath or shower", "a shower or a bath",
                     "shower or a bath", "shower or bath", "bathtub", "a bath", "hot bath",
                     "leak", "leaking", "burst", "flood", "flooded", "blocked", "drain", "drains",
                     "boiler", "radiator", "hot water", "softener", "hard water", "limescale",
                     "rice", "pasta", "dough", "bread", "pastry", "baking", "cake", "sauce", "stock",
                     "simmer", "boil", "boiling", "kettle", "recipe", "cook", "cooking", "pan",
                     "washer", "dripping", "drip", "drips", "eye", "eyes",
                     # How much a thing uses against how much a household can save are two
                     # questions. "does a dishwasher use less water than washing up" holds the
                     # phrase "use less water" that this row is keyed on, so it came to the
                     # household card and was told about five-minute showers; the litres table
                     # (water-use, in home.py) answers it with the figures for both sides. The
                     # row is still the answer for the household with no machine named in it.
                     "dishwasher", "dishwashers", "washing machine", "washing machines",
                     "washer", "washers", "tumble dryer", "tumble drier", "toilet", "toilets",
                     "flush", "flushes", "cistern", "shower", "showers", "a shower of",
                     "bathtub", "hose", "hosepipe")),

        # The gas is turned off somewhere else from the water, and it is the one of the three that is
        # also a call to the emergency line, so it gets its own card rather than a corner of the water
        # one: "how do i turn off the gas supply" met a search hedge, and "where is the gas meter"
        # should say where the lever is, not where the meter is.
        entry("gas-shut-off",
              (("gas", "gas meter", "gas supply", "gas valve", "meter box", "gas pipe",
                # the water stopcock row keys "shut off valve" on its own, and "where is the gas
                # shut off valve" was answered with a brass tap under the sink: the gas phrase is
                # this row's, and the water row stands down on it below
                "gas shut off valve", "gas shutoff valve", "gas stop valve", "gas stopcock"),
               # The intent words, and the phrases that name the job. The words that ride along with
               # the thing ("meter", "emergency", "smell", "leak") are not here: "gas meter" is the
               # whole first part, so a clicking or beeping meter reached the shut-off card, which is
               # the wrong subject and buries the "what is it doing" answer the person can use.
               ("turn off", "turn it off", "turning off", "shut off", "shutting off", "isolate",
                "switch off", "turn", "off", "where", "valve", "handle", "emergency switch",
                "leaking gas", "smell gas", "smelling gas", "stop the gas")),
              "The gas shut-off is the lever on the pipe beside the meter, usually in a box outside "
              "or under the stairs: a quarter turn so the lever sits across the pipe rather than "
              "along it turns the gas off. If you can smell gas, do not touch a switch, a light or a "
              "phone indoors - open the windows, get everyone out and ring the gas emergency line "
              "from outside: 0800 111 999 in England, Scotland and Wales, 0800 002 001 in Northern "
              "Ireland, 911 in the US. Only a Gas Safe engineer turns it back on.",
              # Turning it back on is a different job and a different person's: it is the Gas Safe
              # engineer's. A bare "how" in the ask part was enough to win "how do i turn the gas back
              # on", so the ways of asking to put it on are named here instead.
              avoid=("bill", "bills", "price", "tariff", "cheaper", "cost", "usage", "boiler",
                     "cooker", "hob", "oven", "fire", "fireplace", "cylinder", "bottle", "bbq",
                     "barbecue", "car", "central heating", "supplier", "reading", "standing charge",
                     "back on", "turn on", "turning on", "turned on", "switch on", "switching on",
                     "gas on", "gas back on", "turn the gas on", "turning the gas on",
                     "relight", "re-light", "pilot light", "pilot",
                     # "where do i find a gas safe engineer" is a question about the trade, not
                     # about the meter: the find-a-tradesman row answers it, and the word "gas"
                     # plus "where" was enough to hand it the lever card instead
                     "gas safe", "gas safety", "find a", "find me a")),
        entry("boiler-pressure", ("boiler", ("pressure", "low", "drop", "dropped", "bar", "gauge")),
              # "why" after this answer is asked all the time, so the cause is its own sentence
              # after the topping up: the first sentence stays the gauge reading, which is what
              # "what pressure should it be" and "what should i do about it" are answered from.
              "Top the pressure up to between 1 and 1.5 bar using the filling loop, then bleed the "
              "radiators and check it again the next day. The pressure falls because water is escaping "
              "somewhere: a radiator valve, a joint, or the pressure relief pipe outside. If it keeps "
              "dropping, stop topping it up and get a heating engineer out.",
              # "what happens now" after that answer is the engineer, and saying it as its own
              # line adds the one thing the card leaves out: how often it has dropped is what
              # tells the engineer where to look.
              outcomes=(("next",
                         "Get a heating engineer out and tell them how often it has dropped since "
                         "you topped it up: a system that loses pressure twice is losing water at a "
                         "valve, a joint or the relief pipe, and each top-up only hides it."),)),
        # The gauge is the sealed system's, and it is not always called a boiler: "the radiator is
        # down on pressure", "my heating pressure has dropped" and "the heating is down to half a
        # bar" are all the same gauge. The pressure word comes first here so a radiator word in
        # the line cannot make the answer about the radiator - that is the valve card's, and "and
        # how do i bleed a radiator" after this answer must stay the bleed card.
        entry("heating-pressure", (("pressure", "bar", "psi", "gauge"),
                                   ("down", "low", "lowest", "dropped", "drop", "dropping", "half",
                                    "zero", "under", "below", "fallen", "falling", "topped",
                                    "top up", "topping up", "filling loop", "what should",
                                    # "how do i sort the pressure out" is this card, not the bleed
                                    # one: the bleed answer only lets air out. The bleed row names
                                    # that phrasing in its own avoid list, so this row has to take
                                    # it or the line punts.
                                    "sort", "sorts", "sort it out", "sort out",
                                    # the same repair ask written with "fix", which the bleed row
                                    # gives up in its own avoid list ("does that fix" is its
                                    # question, "how do i fix" is this one)
                                    "fix", "fix it", "fixes it", "how do i fix")),
              "Top the pressure up to between 1 and 1.5 bar using the filling loop, then bleed the "
              "radiators and check it again the next day. The pressure falls because water is escaping "
              "somewhere: a radiator valve, a joint, or the pressure relief pipe outside. If it keeps "
              "dropping, stop topping it up and get a heating engineer out.",
              # "i feel under pressure at work" is the same three words as a gauge question and
              # nothing to do with a boiler: the human sense stands this row down.
              # A line that says "boiler" is `boiler-pressure`'s, and that row is the one the
              # follow-up machinery knows: stealing "my boiler pressure keeps dropping" for a
              # card with the same words but a new id turned the next turn's "Same as before"
              # into an echo ("Got it - you have to top it up every week").
              # A bare "bar" is the bar on a bicycle as often as it is a pressure: the guard above
              # is the unit test, so "drop bars" and "my bars are too low" are not gauge lines.
              guard=_a_gauge_reading,
              avoid=("under pressure", "feel the pressure", "feeling the pressure",
                     "peer pressure", "stressed", "stress", "anxious", "anxiety",
                     "pressure at work", "pressure at school",
                     # a line that asks whether a bleed fixes the gauge is the bleed row's:
                     # "Bleeding does not put pressure back in" is the half of the answer that
                     # says why not. With "sort" in this row's key too, "will bleeding them sort
                     # the pressure" came here and lost it. A report that the radiators were bled
                     # and the gauge is still low is the topping-up question, so the fence is the
                     # question and not the word.
                     "will bleeding", "would bleeding", "does bleeding", "do i bleed",
                     "will bleeding them", "bleeding fix", "bleeding sort", "bleeding help",
                     "bleed them", "bleeding the radiators fix",
                     # A gauge that is too high is the opposite job, and a topping-up answer to it
                     # tells someone to put more water into a system that is already over pressure.
                     # The words are the bleed row's list, so both rows of the pair agree on what
                     # a high gauge is.
                     "too high", "high", "higher", "over 2", "over 3", "above 2", "above 3",
                     "rising", "climbing", "2 bar", "2.5 bar", "3 bar", "overpressure",
                     "boiler", "boilers", "combi")),
        entry("bleed-and-pressure", (("pressure", "bar", "gauge", "top up", "top it up"),
                                    ("fix", "fixes", "cure", "cures", "sort", "sorts",
                                     "does that", "will that", "would that", "that fix",
                                     # "does bleeding help the pressure" and "will bleeding do
                                     # anything" ask the same yes/no as "does it fix it", and the
                                     # row passed them, so both were a search hedge. They are
                                     # written as phrases and not as bare "help"/"work", because
                                     # a bare one takes every other sense of the word: "how do i
                                     # help without pressure", from a parent asking about SATs,
                                     # took this row on "help" and got the boiler paragraph.
                                     "help the pressure", "helps the pressure",
                                     "help the gauge", "helps the gauge", "worth it")),
              "Bleeding does not put pressure back in - it lets air out, and it can drop the "
              "gauge a little. Top it up at the filling loop to 1 to 1.5 bar with the system "
              "cold, then check it the next day; if it is low again there is a leak somewhere "
              "and that is an engineer's job.",
              # The same unit test as `heating-pressure`: "my bars are too low" reached this row
              # on "bar" alone and was told about bleeding a radiator.
              guard=_a_gauge_reading,
              # A gauge that is too high is the opposite job and a topping-up answer is the
              # wrong move to hand someone: "the pressure is too high" took this row on "high"
              # being nowhere and "too" being here.
              # What the repair costs is the money card's question, not this one. The row needs a
              # cross-question word to fire at all ("would that", "that fix", "same"), and the
              # boiler is still in memory from the turn before, so "what would that cost to fix"
              # was read as a cross-question and the person asking the price was told how
              # bleeding works and never got a figure. The price words stand the row down.
              #
              # They are the price words and not "how much": an avoid phrase is read loosely, so
              # "how much" as one stood this row down for "how much would that be", which already
              # reached the boiler figures on main, and the turn came back a hedge - a worse
              # answer for a case this change is not about.
              #
              # The feelings sense of the word is the other stand-down, and it is the one a
              # reviewer caught: "how do i help without pressure" is a parent asking about SATs
              # (deck row qmis-year6-01) and it came here on a bare "help" that took every sense
              # of the word. The bare word is gone from the key; these name the sense. "no
              # pressure" and "pressure on" are deliberately not here - "there is no pressure in
              # the boiler" and "the pressure on the gauge" are gauge lines.
              avoid=("too high", "high", "higher", "over 2", "over 3", "above 2", "above 3",
                     "rising", "climbing", "2 bar", "2.5 bar", "3 bar", "overpressure",
                     "under pressure", "peer pressure", "pressure at work", "pressure at school",
                     # "how do i sort the pressure out" and "my boiler pressure is low, how do i
                     # sort it" are repair asks, and the cue is the how-do-i frame, not the verb
                     # "sort": the bleed row owns "does that sort the pressure". The frame is what
                     # separates them, so the frame is the fence.
                     "how do i sort", "how to sort", "how can i sort", "how do you sort",
                     "how do i fix", "how to fix", "how do i top", "what do i do about the pressure",
                     "without pressure", "putting pressure", "pressure myself", "pressure from",
                     "pressure her", "pressure him", "pressure them", "sats", "exams", "revision",
                     "blood pressure", "tyre", "tyres", "tire", "tires",
                     "cost", "costs", "costing", "price", "prices", "priced", "quote", "quotes",
                     "quoted", "charge", "charges", "£")),
        # The noise is in the heating as often as in the boiler: "my heating is making a clanking
        # noise" named no boiler at all and got a shrug, though the answer is the same one. The
        # row is still keyed on a sound, so "how much does heating cost" never reaches it. "hot
        # water" and "the heating" are deliberately not subjects: a two-word phrase also scores
        # its own words, so "only when the hot water comes on" cleared the minimum on the phrase
        # alone and pulled the follow-up into this row.
        # The sounds come from the shared list in wording.py, because this row's own list named
        # some forms of each sound and not others: the answer has a paragraph for a tick or a click
        # ("pipes expanding as they heat"), and "my boiler clicks a lot" and "the boiler is
        # clicking" reached nothing but the greeting, while "the boiler wont stop clicking" got in
        # through "clicking" being spelled out on another row. One list for every row that answers
        # a noise means the next appliance inherits the forms too.
        entry("boiler-noise", (("boiler", "heating", "central heating", "heat pump"),
                               MACHINE_SOUNDS + NOISE_WORDS),
              _boiler_noise),
        # A kettling boiler is a different fault with a different first move: limescale on the heat
        # exchanger, not air. Naming it is the whole question, so it gets its own answer rather than
        # the banging one with a postscript.
        # "combi" is a boiler by another name, and a line that says it is a heating line: "our
        # combi is kettling and the pressure is fine" reached nothing at all, because the row's
        # other half wanted the word "boiler".
        entry("boiler-kettling", (("kettling", "kettle", "kettles", "limescale", "scale", "descale",
                                   "sludge"),
                                  ("boiler", "boilers", "combi", "heating", "central heating",
                                   "hot water", "radiator", "radiators")),
              ("Kettling - a noise like a kettle boiling as it fires - is limescale on the heat "
               "exchanger, not air in the pipes, so bleeding the radiators will not stop it. Get a "
               "heating engineer to power-flush or descale the system and fit a scale reducer or a "
               "magnetic filter; turn the boiler flow temperature down a notch meanwhile, because "
               "kettling gets worse the hotter it runs."),
              # "a noise like a kettle boiling" ties with the banging answer on words, and this is the
              # more specific fault: the line named the sound.
              # A kettle in a line about how long the water takes is the thing in the kitchen: "how
              # long does it take to boil a kettle" was answered with kettling on the boiler.
              avoid=("how long", "how many minutes", "minutes to boil", "take to boil",
                     "does it take", "tea", "coffee", "cup of"),
              bias=1),
        entry("radiator-noise", ("radiator", ("noise", "noisy", "banging", "clicking", "gurgling",
                                              "ticking", "loud")),
              ("Ticking and clicking is the pipes expanding as they heat, which is normal and stops "
               "once the system is warm. Banging or gurgling means air or trapped water: bleed the "
               "radiators and check the boiler pressure sits between 1 and 1.5 bar.")),
        # "bled" and "bledding" are what people type for bleed: a one-letter verb that is also a
        # real word ("bled", "cold") never comes back from the typo reader, so it is listed here.
        # A heated towel rail is a radiator with a bleed valve at the top, and people call it a rail
        # rather than a radiator, so "how do i bleed a towel rail" reached nothing at all.
        # The heating and the hot water "keep going cold" is a shape the fault rows did not read: on
        # main "the heating keeps going cold" got "Got it - is there anything you'd like a hand
        # with?" and "my hot water keeps going cold" was packed for a picnic. The words that matter
        # are the thing that went cold and the verb shape, so this row keys on both and the radiator
        # keeps its bleed and sludge answers.
        entry("heating-goes-cold",
              (("heating", "the heating", "my heating", "our heating", "central heating",
                "hot water", "my hot water", "hot tap", "hot taps", "boiler",
                "immersion", "hot water cylinder", "cylinder", "hot bath", "bath water"),
               ("keeps going cold", "keeps running cold", "keeps coming out cold",
                "goes cold", "going cold", "runs cold", "running cold", "comes out cold",
                "cold after", "goes cold after", "cools down", "keeps cooling", "hot then cold",
                "comes on then goes off", "hot and cold", "lukewarm", "never really hot")),
              _heating_goes_cold,
              bias=2,
              # a radiator that is cold is the bleed and sludge rows' question, and a bill is not a
              # fault at all
              avoid=("radiator", "radiators", "rads", "bill", "bills", "cheaper", "cost", "save",
                     "tariff", "insulation", "energy", "kettle", "shower", "washing machine",
                     "dishwasher", "drink", "drinks", "beer", "wine", "milk", "oven", "microwave",
                     "hob", "air fryer", "toaster", "iron", "food", "bath water")),
        entry("radiator-bleed", (("radiator", "towel rail", "towel radiator", "heated towel rail",
                                  "ladder rail", "ladder radiator", "chrome rail"),
                                 ("bleed", "bled", "bleeding", "bledding", "cold",
                                  "bottom", "noise", "hot",
                                  # the shape of the fault said as a phrase, because a towel in the
                                  # line otherwise reads as washing
                                  "cold at the top", "hot at the bottom", "warm at the top",
                                  "cold at the top of the radiator")),
              "Radiators that are hot at the bottom and cold at the top have air in them: open the bleed "
              "valve at the top with a radiator key, a quarter turn at a time, with a cloth under it, "
              "until water trickles out steadily. Two minutes a radiator is all it takes, and a whole "
              "house takes ten to fifteen minutes. Then check the boiler pressure and top it up if it's "
              "below 1 bar.",
              # A radiator that is hot at the top and cold at the bottom is the other fault (see
              # radiator-cold-bottom), and the bleed answer is the wrong one for it.
              # A line that names the boiler is the boiler's, not the radiator's: "my boiler is
              # banging and the radiators are cold at the top" is about the boiler, and the banging
              # and pressure rows answer it and tell the person to bleed the radiators themselves.
              # Only the words that name the boiler are held out - "pressure" and "pump" are not
              # boiler words (the banging card says a pump set too fast), and holding them out took
              # the bleed card away from "radiator cold at the top and the pressure is low".
              avoid=("cold at the bottom", "cold at the botto", "cold bottom", "hot at the top",
                     "warm at the top", "cold along the bottom", "filling loop",
                     # the same fault said as a denial: "hot at the bottom" is in this row's key,
                     # so "the radiator is not hot at the bottom" (a sludge radiator, cold along
                     # the bottom) read as the air one and was told to bleed it
                     "not hot at the bottom", "not warm at the bottom", "not getting hot at the "
                     "bottom", "isnt hot at the bottom", "isn't hot at the bottom",
                     "lukewarm at the bottom", "cool at the bottom"),
              # #6487 held out the bare word "boiler", which is not the same as the boiler being
              # the fault: people name the boiler to say it is *not* the problem, and then the
              # bleed card is the answer they need. "boiler pressure is fine, radiator cold at the
              # top" was told to top the pressure up through the filling loop, and "my boiler
              # pressure is ok, the radiator is still cold at the top" got the cold-and-flu card.
              # Only a boiler named with something wrong with it stands this row down.
              guard=_the_boiler_is_not_the_fault),
        # The next thing people ask after the bleed card is about the key: "which key do i need",
        # "ok so i bleed them with a key?", "does it need a special key". The bleed row's answer
        # names a radiator key and stops there, and the follow-up was answered "Everything about a
        # key is in what I said above" - a sentence about the conversation rather than about the
        # key you buy. One row for the tool, and the radiator has to be in the line or in the last
        # turn, so a door key or a keyboard keeps its own answer.
        entry("radiator-bleed-key",
              (("radiator key", "bleed key", "bleeding key", "key for the radiator",
                "key for a radiator", "radiator valve key", "special key", "little key", "small key",
                "key", "keys"),
               ("radiator", "radiators", "rad", "rads", "bleed", "bled", "bleeding", "bleed them",
                "bleed it", "valve", "valves", "towel rail")),
              "Yes - a radiator bleed key: a little square or half-moon spanner, about two or three "
              "pounds from a hardware shop or a big supermarket, and a cloth under the valve to catch "
              "the drips. Some newer valves take a small flat screwdriver instead, so look at the slot "
              "before you buy. A quarter turn is enough, and you stop when water runs steadily rather "
              "than hissing air.",
              # a door key, a keyboard, a bike lock and a car key are other questions, and the
              # radiator's own fault cards are the hardware answer, not the tool
              avoid=("door", "doors", "front door", "back door", "lock", "locks", "lockout", "locked",
                     "snapped", "snap", "lost my keys", "lost the key", "spare key", "keyboard",
                     "keyboards", "keypad", "keyring", "key fob", "fob", "car key", "bike lock",
                     "padlock", "ignition", "remote", "opener", "cylinder lock", "euro cylinder",
                     "cold at the bottom", "hot at the top", "sludge", "noise", "banging",
                     "pressure", "thermostat", "trv")),
        # The mirror image of a radiator with air in it: hot at the top, cold at the bottom means the
        # bottom of the radiator is full of sludge, so there is nothing to bleed. Main answered it
        # with the bleed card, which tells someone to open a valve that will not help.
        entry("radiator-cold-bottom",
              ("radiator", ("cold at the bottom", "cold along the bottom", "cold bottom",
                            "hot at the top", "warm at the top", "bottom is cold",
                            "bottom stays cold", "half cold", "never gets hot",
                            # the same thing said as a denial: "my radiator is not getting hot at
                            # the bottom" was a listening reply, because a state word cannot be
                            # keyed and the negation has to be spelled out
                            "not getting hot at the bottom", "not hot at the bottom",
                            "not warm at the bottom", "wont get hot at the bottom",
                            "won't get hot at the bottom", "doesnt get hot at the bottom",
                            "doesn't get hot at the bottom", "getting hot at the bottom",
                            "lukewarm at the bottom", "cool at the bottom",
                            "cold at the bottom of", "cold along the bottom of")),
              "Hot at the top and cold at the bottom is sludge sitting in the radiator, not air, so "
              "bleeding it will not help: the water cannot get round the bottom. Ask a heating engineer "
              "to power-flush the system or add a chemical cleaner, and have a magnetic filter fitted "
              "so it does not come back. Turning the other radiators off to push water through the cold "
              "one is a five-minute test that shows whether it is sludge or a stuck valve."),
        # A radiator that will not heat up at all: the key is the fault phrase rather than the state
        # word, because the denial reader rules a state word out ("is not getting hot" is not a hot
        # radiator) and a key of "radiator" alone scores 0. See RADIATOR_WHOLE_HOUSE above for the two
        # first moves.
        entry("radiator-not-hot",
              (("radiator", "radiators", "rad", "rads", "central heating", "the heating",
                "heating"),
               ("upstairs", "downstairs", "landing", "first floor", "ground floor",
                "not getting", "not warming", "not heating", "isnt getting", "isn't getting",
                "arent getting", "aren't getting", "isnt warming", "isn't warming", "isnt heating",
                "isn't heating", "wont heat", "won't heat", "wont warm", "won't warm",
                "not hot", "not warm", "stays cold", "staying cold", "still cold", "still not hot",
                # "radiator is cold" bare is not here, because a cold radiator with nothing else
                # said is the bleed question and that row keeps it; "in" is what marks the one that
                # named where it is cold
                "radiator is cold in", "rad is cold in",
                # "the radiator in my bedroom is cold" names where the radiator is rather than
                # where the cold is, so it needed its own shape
                "radiator in my", "radiator in the", "rad in my", "rad in the",
                "never gets hot", "never gets warm", "never warms", "cold radiator",
                "one radiator is cold", "rads are cold", "radiators are cold",
                "thermostat is stuck", "thermostat stuck", "valve is stuck", "valve stuck",
                "trv stuck", "stuck on")),
              _radiator_not_hot,
              # It ties the bleed row at 5 words of rank on "bled ... still cold" (radiator + still
              # cold), and a tie is file order, so the bias is what gives the fault card the turn the
              # line is about: someone who has already bled a radiator is not told to bleed it again.
              bias=2,
              # a radiator that is hot at the top and cold at the bottom is the sludge card, and the
              # bill question about the heating is not a fault at all
              avoid=("at the top", "at the bottom", "cold at the top", "hot at the bottom",
                     "top half", "bottom half", "bill", "bills", "cheaper", "cost", "save",
                     "tariff", "insulation", "bleed a radiator", "how do i bleed", "bleed valve",
                     "radiator key",
                     # a heating word is also a hot-water word: "the hot water is not heating up" is
                     # the cylinder or the immersion, not a radiator, and this card talked about
                     # valves and radiators to someone whose hot taps had gone cold
                     "hot water", "shower", "immersion", "cylinder", "hot tap", "hot taps",
                     "tank", "no hot",
                     # and every other thing in a house that heats or warms: the oven, the boiler
                     # and the water were all told about a radiator pin, since "heating" is the
                     # verb in "my oven isnt heating up" as much as the noun in "my heating"
                     "boiler", "oven", "water", "hob", "washing machine", "dishwasher",
                     "tumble dryer", "towel rail", "airing cupboard",
                     # and the small appliances, for the same reason: "heating" is the verb in
                     # "my microwave isnt heating" as much as it is the noun in "my heating", and
                     # a person with a cold microwave was told to take a thermostatic valve head
                     # off a radiator
                     "microwave", "microwaves", "kettle", "kettles", "toaster", "toasters",
                     "iron", "air fryer", "airfryer", "air-fryer", "coffee machine",
                     "washer dryer", "deep fat fryer", "slow cooker", "pressure cooker",
                     # a tumble dryer, a heat pump dryer and a hair dryer heat too, and "my dryer
                     # isnt heating up" and "my heat pump dryer is not heating up" were both told
                     # to take a thermostatic valve head off a radiator. The machine that will
                     # not heat is its own card, and the dryer is the one this row kept missing:
                     # only "tumble dryer" and "washer dryer" were named, and most people type
                     # "my dryer".
                     "dryer", "dryers", "drier", "driers", "tumbler", "heat pump dryer",
                     "heat pump drier", "heat-pump dryer", "hair dryer", "hairdryer",
                     # a garden heap heats up too, and "why is my compost not heating up" was
                     # told to take a thermostatic valve head off a radiator, because "heating"
                     # is the verb in "my compost isnt heating up" as much as the noun in "my
                     # heating"
                     "compost", "composts", "heap", "heaps", "pile", "piles", "allotment",
                     "garden", "gardening", "manure", "muck")),
        # "i have no hot water" names no boiler and boiler-broken needs the word, so the commonest
        # way of saying it got "Got it - is there anything you'd like a hand with?". The line is
        # often three words with no verb phrase at all, so the second group repeats the subject: a
        # key that scores on the phrase alone still needs a second word from the line to answer.
        entry("no-hot-water",
              (("no hot water", "hot water gone", "hot water has gone", "hot water not working",
                "hot water isnt working", "hot water isn't working", "hot water is not working",
                "hot water has stopped", "hot water stopped", "hot water has stopped working",
                "hot water comes and goes", "hot water is cold", "hot water is off",
                "hot water is lukewarm", "only cold water", "no hot water anywhere",
                "no heating and no hot water",
                # "we keep running out of hot water" is the same fault said as a habit, and it had
                # no row of its own: "runs" is a form of "running" and "water" sat in the place part
                # of the holiday row, so a house with no hot water was told to eat where it is busy.
                # The phrase is keyed here, not the bare "running", which is what a nose and a
                # deadline both say.
                "running out of hot water", "run out of hot water", "ran out of hot water",
                "runs out of hot water", "running out of hot water in the mornings",
                "hot water runs out", "hot water runs out fast", "hot water running out",
                # and the ask from the other side: "how do i get hot water back" names no fault at
                # all, so it reached no row and got a punt
                "get hot water back", "hot water back", "hot water working again",
                # and the same habit with the words the other way round
                "keeps running out of hot water", "hot water keeps running out",
                # The supply that is there and cold is the same fault said as a verb, and it had no
                # row at all: "my hot water is not heating up" and "the water isn't getting hot" got
                # a bare nod, because every key above is the water being *absent*. The phrase has to
                # carry the water, or "my microwave is not heating up" and "my food is not hot" would
                # land on a plumber.
                "hot water is not heating up", "hot water isn't heating up",
                "hot water isnt heating up", "hot water not heating up",
                "hot water is not heating", "hot water isn't heating",
                "hot water is not getting hot", "hot water isn't getting hot",
                "hot water isnt getting hot", "hot water not getting hot",
                "hot water is not hot", "hot water isn't hot", "hot water is never hot",
                "hot water is not hot enough", "hot water won't heat up", "hot water wont heat up",
                "hot water won't get hot", "hot water wont get hot",
                "water is not heating up", "water isn't heating up", "water isnt heating up",
                "water not heating up", "water is not heating", "water isn't heating",
                "water is not getting hot", "water isn't getting hot", "water isnt getting hot",
                "water won't heat up", "water wont heat up", "water is not warming up",
                "water isn't warming up", "hot water is not warming up",
                # "not hot enough" says the same fault as an amount rather than as a state, and
                # the hydration row took "water not hot enough" for it
                "water not hot enough", "water is not hot enough", "water isn't hot enough",
                "water isnt hot enough", "the water is not hot enough",
                "water is never hot enough", "why is my water not hot enough",
                "hot water is not hot enough for a bath",
                # the tap named instead of the supply: "the water from the hot tap is not hot" was a
                # shrug too, and it is the same question about the same tank
                "hot tap is not hot", "hot tap isn't hot", "hot tap is cold",
                "hot tap water is cold", "water from the hot tap is not hot",
                "water from the hot tap is cold", "water from the hot tap runs cold",
                # The hyperbaton shapes: every phrase above puts "is" between the water and the
                # temperature, so "why is my hot water cold" - the plainest way to ask - matched
                # none of them and was answered by the science card about why water is wet. The
                # copula is the "why is" at the front, so these carry the words without it.
                "why is my hot water cold", "why is the hot water cold",
                "why is our hot water cold", "why is hot water cold",
                "why is my hot water not hot", "why is the hot water not hot",
                "why is my hot water warm", "why is my hot water lukewarm",
                "why is my hot water tepid", "hot water comes out cold",
                "water comes out of the hot tap cold", "cold water comes out of the hot tap",
                # the water with no "hot" in it: a person with cold taps asks this way, and the
                # science card answered it. The pool, the sea and the glass are fenced out below.
                "why is my water cold", "why is the water cold", "why is my tap water cold",
                "why is the tap water cold", "my tap water is cold", "the tap water is cold",
                "why is my cold water warm", "why is the cold water warm",
                "cold tap runs warm", "cold water is warm", "cold tap is warm",
                # heating on, radiators hot, taps still cold - the same cylinder or diverter,
                # asked by naming the heating
                "why is the heating not warming the water", "heating is not warming the water",
                "not warming the water", "heating works but the water",
                "radiators are hot but the water", "radiators hot but no hot water"),
               ("hot water", "water", "tap", "taps", "shower", "bath", "kitchen", "bathroom",
                "flat", "house", "home", "heating", "morning", "mornings", "why", "fix", "check")),
              ("Start at the programmer: it is usually on a timer that has slipped, or on 'water "
               "only' when you wanted heating too. A combi with no hot water but working heating is "
               "nearly always low pressure or a stuck diverter valve, so look at the gauge (1 to 1.5 "
               "bar cold) and try the reset. If there is a hot water cylinder, look for the immersion "
               "switch and the thermostat on the side, and check the little header tank has water in "
               "it. Anything inside a gas boiler, or gas you can smell, is a Gas Safe engineer."),
              # a line with no hot water and a word about heat ties with the hot-weather card, which
              # then wins on key order; the plumbing answer is the one that helps
              bias=1,
              avoid=("boiler", "boilers", "gas", "cylinder", "immersion", "pressure", "gauge",
                     "error code", "flame", "pilot", "condensate", "gas safe",
                     # a hot water *bottle* and a hot water tap abroad are other questions
                     "bottle", "abroad", "hotel", "camping", "kettle",
                     # "why is my water cold" is a tap or a tank, not a pool, a sea or a glass
                     "pool", "pools", "swimming pool", "swim", "sea", "beach", "lake", "river",
                     "glass of", "glass", "drinking", "ice", "ice cube", "cubes", "freezer",
                     "fridge", "cool box", "cooler", "flask", "gym", "hot tub", "jacuzzi",
                     # A shower that goes cold after a few minutes is `shower-goes-cold`'s question:
                     # this answer is about a supply that is not there at all, so the halfway-through
                     # shapes stand this row down and "no hot water at all" does not.
                     "after one shower", "after a shower", "after two showers", "after a few minutes",
                     "halfway through", "half way through", "mid shower", "mid-shower", "goes cold",
                     "turns cold", "runs cold")),
        # A heat pump is the question people ask twice: what is it doing, and is it worth it. The
        # mechanics come first for "how does it work", and the verdict for "is it worth it".
        # A cold shower with hot taps elsewhere is the shower itself; no-hot-water above owns the
        # whole house, so that entry keeps its lines and this one never takes them.
        entry("shower-cold",
              (("shower", "showers", "power shower", "electric shower", "mixer shower", "shower head",
                # The bare nouns scored 2 against a floor of 4, so "why is my shower cold" was
                # answered by the science card about water being wet rather than by this one. The
                # question shapes carry it over the floor.
                "shower is cold", "shower is not hot", "shower is lukewarm", "shower isnt hot",
                "shower isn't hot", "shower runs cold", "shower running cold",
                "shower goes lukewarm", "why is my shower cold", "why is the shower cold",
                "why is my shower not hot"),
               ("cold", "cool", "lukewarm", "not hot", "warm", "temperature", "running cold",
                "runs cold", "cold water")),
              "If the shower runs cold but the hot taps elsewhere are fine, it is the shower: an "
              "electric shower usually wants the pull cord or a tripped switch in the consumer unit "
              "checked, and a mixer shower is often a stuck thermostatic cartridge, which frees up if "
              "you take the head off and work the temperature knob from cold to hot a few times. If "
              "the hot taps are cold too, the fault is the boiler or the cylinder rather than the "
              "shower.",
              bias=1,
              avoid=("blocked", "drain", "smell", "mould", "clean", "limescale", "buy", "best",
                     "which", "cheapest", "install", "bathroom", "tile", "leak", "boiler", "curtain",
                     "screen", "tray", "no hot water", "hot water", "house", "anywhere", "heating",
                     # A shower that comes hot and then goes cold is the hot water running out, not
                     # the shower giving up: shower-goes-cold already answers it from the boiler side,
                     # and that answer is the better one. These phrases are the words of that question.
                     "goes cold", "going cold", "gone cold", "went cold", "keeps going cold",
                     "kept going cold", "turns cold", "turned cold", "hot then cold",
                     "warm then cold", "cold after a few minutes", "after a few minutes",
                     "cold quickly", "cuts out",
                     # A cold shower somebody chooses is not a fault, and it was a shrug on main:
                     # "is a cold shower good for you" wants a fact, not a plumber. The bare "cold"
                     # in the key means any cold shower reads as a broken one, so the practice words
                     # stand this entry down and the honest shrug comes back.
                     "a cold shower", "cold showers", "cold shower good", "cold shower bad",
                     "have a cold shower", "having a cold shower", "take a cold shower",
                     "taking a cold shower", "cold shower after", "cold shower every",
                     "cold shower in the morning", "cold water therapy", "cold plunge", "ice bath",
                     "sauna", "contrast shower", "bracing")),
        # The dial, as opposed to the fault: "how hot should hot water be" and "how do i make my
        # hot water hotter" were a search hedge, and they are the one question about a cylinder
        # that has a number for an answer. Asking about the setting is not asking why the water
        # is cold, so "why is my hot water cold" stays with no-hot-water above.
        entry("hot-water-temperature",
              (("hot water temperature", "temperature of the hot water", "hot water be",
                "hot water hotter", "make the water hotter", "make my hot water hotter",
                "turn up the hot water", "turn up my hot water", "turn the hot water up",
                "hot water thermostat", "cylinder thermostat", "hot water setting",
                "how hot should hot water", "how hot should the hot water",
                "how hot should my water", "what temperature should the hot water",
                "what temperature should my hot water", "what should the hot water be set to",
                "how hot should the water be", "hot water too hot", "hot water is too hot"),
               ("hot", "hotter", "temperature", "setting", "thermostat", "turn up", "dial",
                "degrees", "how hot", "what", "should", "celsius", "too hot", "scald")),
              "Sixty degrees on the cylinder thermostat is the number to aim for. A stored "
              "cylinder is held at 60 to 65C because below about 50C the bacteria behind "
              "Legionnaires' disease can multiply in the tank, and a thermostatic mixing valve on "
              "the outlet then brings it down to about 48C at the tap so nobody scalds. A combi "
              "has no tank, so set its hot water to 50 to 55C - hotter only burns gas and scales "
              "the plate heat exchanger faster. If the water comes out warm rather than cold, the "
              "setting is the thing to raise; if it starts hot and cools, the setting is fine and "
              "the fault is flow rate or a scaled exchanger.",
              # the cooking temperatures, the baby's bath, the washing machine and the greenhouse
              # are other questions with their own numbers
              avoid=("oven", "chicken", "meat", "pork", "turkey", "beef", "lamb", "sausages",
                     "roast", "bake", "bread", "dough", "sourdough", "yeast", "yoghurt", "yogurt",
                     "baby", "babies", "bath for the baby", "bottle", "formula", "breast milk",
                     "milk", "washing machine", "wash", "washing", "radiator", "radiators",
                     "heating", "kettle", "hot tub", "jacuzzi", "pool", "swimming", "thermometer",
                     "fever", "temperature of my child", "child", "children", "greenhouse",
                     "propagator", "germinate", "seeds", "compost", "room", "bedroom", "bed"),
              bias=1),
        # The other side of the same fault: a cold tap that runs warm. "why is the cold tap warm"
        # was a "a plumber will spot it in minutes", "my cold water runs warm" was the stopcock
        # card and "cold water comes out warm" was a bare nod, because no row owns a cold supply
        # that is hot.
        entry("cold-tap-warm",
              (("cold tap", "cold taps", "cold water", "the cold water", "cold supply",
                "cold water is warm", "cold water runs warm", "cold water comes out warm",
                "cold water goes warm", "cold water is hot", "cold tap is warm",
                "cold tap runs warm", "cold tap is hot", "why is my cold tap warm",
                "why is the cold tap warm", "why is my cold water warm",
                "why is the cold water warm", "why is my cold water hot"),
               ("warm", "hot", "warmish", "lukewarm", "tepid", "not cold", "warm up", "warms up",
                "comes out", "runs", "why", "heating up", "boiling")),
              "A cold tap that runs warm is nearly always warm water getting into the cold pipe: a "
              "mixer tap or shower cartridge letting by, or a non-return valve that has failed, and "
              "in a house with a hot water cylinder a faulty mixing valve does the same. Feel the "
              "pipe under the sink - if it turns cold after a minute or two it is just the pipe run "
              "sitting warm in a cupboard, which is harmless; if it stays warm, have the check valve "
              "or cartridge replaced. If it is only the one tap, that tap is the culprit; if it is "
              "every cold tap, look at the cylinder, the mixing valve or the shared supply.",
              # the shower has its own card, and the rest of these are other questions entirely
              avoid=("shower", "showers", "pool", "swimming", "sea", "beach", "lake", "river",
                     "glass", "drink", "drinking", "bottle", "flask", "kettle", "hot water bottle",
                     "ice", "freezer", "fridge", "cooler", "hot tub", "jacuzzi", "radiator",
                     "radiators", "heating", "boiler", "overflow", "leak", "dripping",
                     "tap is dripping", "no hot water", "hot water", "hot tap", "hot taps",
                     "bath water", "washing"),
              bias=3),
        entry("heat-pump",
              (("heat pump", "heat pumps", "air source", "ground source", "heat pump work",
                "heat pump works", "what is a heat pump", "how do heat pumps work"),
               ("work", "works", "working", "how", "what", "explain", "worth", "idea", "good",
                "cost", "costs", "running", "cheaper", "replace", "boiler", "install", "noise",
                "loud", "cold", "any")),
              _heat_pump_answer,
              # a heat pump dryer, a heat pump dehumidifier or a heat pump hot water tank is
              # that appliance's question, and "is a heat pump dryer any good" was answered here
              # with how the refrigerant works.
              guard=_the_explainer_keeps_the_explainer,
              avoid=("car", "engine", "air conditioning", "fridge", "freezer", "microwave",
                     "washing machine", "dishwasher", "shower pump", "pool")),
        entry("batteries-in-the-bin",
              (("batteries", "battery", "old batteries", "used batteries", "aa", "aaa", "button cell",
                "lithium", "vape", "vapes", "disposable vape", "e-bike battery", "phone battery"),
               # "rubbish" is a verdict as often as it is a bin: "my phone battery is rubbish" was
               # answered with the recycling card, so only the bin sense of the word counts here
               ("bin", "bins", "the rubbish", "rubbish bin", "in the rubbish", "trash",
                "throw", "throw away", "throwing", "dispose",
                "disposal", "recycle", "recycling", "kerbside", "where do i put", "get rid",
                # the rest of the ways people say "I want this gone": the rubbish domain's own RID
                # list has them all and this row had five, so "what do i do with old batteries" and
                # "where do i take old batteries" came back as a shrug while "how do i get rid of
                # old batteries" answered properly.
                "do with", "where do i take", "where can i take", "drop off", "chuck", "toss",
                "the tip", "to the tip", "recycling centre", "scrap")),
              ("Not the bin: batteries are a fire risk in a lorry and in the tip. Most supermarkets and "
               "every council recycling centre have a battery box by the door, and button cells and "
               "lithium ones go in those too, with the ends taped. Vapes, e-bike and scooter batteries "
               "and power banks are the ones that actually start fires, so take them to a shop that "
               "sells them or to the tip, never the kitchen bin."),
              avoid=("car battery", "car", "laptop wont charge", "phone wont charge", "remote",
                     "smoke alarm", "hearing aid", "flat battery")),
        # "where is my stopcock" and "how do i turn the water off" were both punts, and they are the
        # two questions every other plumbing answer assumes have already been answered. The telling
        # words are stopcock/stop tap/stop valve, and the water-off shapes, which stand on their own.
        entry("stopcock", (("stopcock", "stop cock", "stop tap", "stop valve", "shut off valve",
                            "shutoff valve", "water valve", "mains valve", "isolation valve",
                            "water main", "mains water", "water meter", "turn the water off",
                            "turn off the water", "turn the water back on", "shut the water off"),
                           ("where", "find", "located", "how", "what", "turn", "shut", "off", "water",
                            "under the sink", "outside", "emergency", "leak", "leaking")),
              "It is usually under the kitchen sink where the cold main comes up, or in a box near the "
              "boundary outside, and it is a brass tap that closes clockwise: turn it a quarter turn at "
              "a time, run the cold tap to check it has stopped, and turn it back anti-clockwise "
              "afterwards. If it is seized, don't force it with a wrench - a rounded stopcock means "
              "turning the water off at the road, which is the water company's job.",
              # "water meter" is a key word here because the meter sits by the stopcock, and that
              # made every question with the phrase in it ask where the thing is: "is a water meter
              # cheaper", "will a water meter save me money" and "how much does a water meter save"
              # got its location, and a leaking meter got it too. Only the where-is-it shapes are
              # this row's; the money shapes are the water-bill row's.
              avoid=("worth", "worth it", "cheaper", "save", "saves", "saving", "expensive", "cost",
                     "costs", "how much", "should i", "should we", "leak", "leaks", "leaking",
                     # the same money shapes said as an ask for a view: "would you recommend a water
                     # meter" and "do you recommend a water meter" carry the buying words the row
                     # below answers with, and this one answered them with where the stopcock is.
                     # A recommendation is never a where-is-it question, so it stands the row down.
                     "recommend", "recommended", "recommendation", "recommendations",
                     "any point in", "any point to", "waste of money", "worth having",
                     "leaked", "drip", "dripping", "broken", "faulty", "frozen", "read my meter",
                     "meter reading", "smart meter",
                     # the gas has its own lever and its own card, and "where is the gas shut off
                     # valve" was the water stopcock answer for want of these
                     "gas shut off", "gas shutoff", "gas valve", "gas stop", "gas meter",
                     "gas supply", "gas pipe", "gas leak", "smell gas",
                     # "how do i get a water meter" is the meter question, not where the meter is:
                     # the location answer named the sink and said nothing about asking the company
                     "get a water meter", "get a meter", "getting a meter", "have a meter fitted",
                     "fit a meter", "fit a water meter", "install a meter", "free meter",
                     "switch to a meter", "ask for a meter", "water meter save",
                     # a heater, an immersion or a hot water tank has its own valve and its own
                     # answer, and "turn off the water heater" reached this row on the words
                     # "turn off the water" plus "how"
                     "water heater", "water heaters", "immersion", "immersion heater",
                     "hot water tank", "hot water cylinder", "water tank", "heater", "heaters",
                     "cylinder", "hot water"),
              bias=1),
        # Turning a radiator off is not a fault: it is the summer job, the spare room nobody heats,
        # and the radiator that is too hot to sit next to. Nothing on main answered it - the line
        # reached `paint-strip` (bare "off" plus the word radiator) or a plumber punt.
        entry("radiator-off",
              (("radiator", "radiators", "rad", "rads", "trv", "thermostatic valve",
                "radiator valve", "towel rail"),
               ("turn off", "turning off", "switch off", "switching off", "shut off",
                "shutting off", "turn it off", "switch it off", "turn them off",
                # "how do i turn down a radiator" and "my radiator is too hot" are main's own lines -
                # the numbered head, down a notch or two - and turning a radiator DOWN is not turning
                # it off, nor is a room that is too warm asking for the frost setting. The bare
                # "turn down" forms and the "too hot" shape are therefore not in this key at all, and
                # both lines keep the answer they had.
                "off for the summer",
                "off for summer", "off in the summer", "not using that room", "spare room",
                # "how do i turn a radiator off" has no "turn off" in it, because the thing is in
                # the middle: the noun and its off are the phrase people actually type
                "radiator off", "radiators off", "rad off", "rads off",
                "turn a radiator off", "turn the radiator off", "turn my radiator off",
                "switch a radiator off", "switch the radiator off", "shut a radiator off",
                "turn both radiators off")),
              "Turn the thermostatic head on the radiator down to 0 or to the snowflake, which is "
              "frost protection rather than fully off, and leave it there: that closes the valve "
              "against the room and the radiator goes cold the next time the heating runs. If it has "
              "an old wheel valve instead of a numbered head, turn it clockwise until it stops - the "
              "same valve a plumber would close - and turn both ends if you are taking the radiator "
              "off the wall. Don't shut the valves on a radiator in a room that gets damp or near "
              "freezing, because that is the one that needs the frost setting.",
              bias=1,
              # a leak, a cold radiator and a noisy one are faults with their own first move, and
              # paint is the stripping row's
              avoid=("leak", "leaking", "leaked", "drip", "dripping", "puddle", "bleed", "bled",
                     "cold", "noise", "noisy", "banging", "gurgling", "paint", "painting",
                     "strip", "removing", "bill", "bills", "save", "cheaper", "cost", "boiler",
                     "how long", "radiator key", "hot water")),
        entry("radiator-leak",
              (("radiator", "radiators", "rad valve", "trv", "thermostatic valve", "towel rail",
                # the valve is the part that leaks, and "how do i fix a leaky radiator valve" scored
                # nothing at all: "valve" was only reachable as "rad valve" or "trv"
                "valve", "valves", "lockshield", "bleed valve"),
               ("leak", "leaks", "leaking", "leaked", "leaky", "drip", "dripping", "weeping",
                "water", "puddle", "wet", "rusted", "rusty", "seeping")),
              "Turn both radiator valves off and put a towel and a bowl under it, then see whether the "
              "water comes from the valve nut or the radiator itself: a drip at the nut often stops "
              "with a quarter turn of a spanner on the gland, while water from the panel or a rusty "
              "seam means the radiator has gone and wants replacing. Don't overtighten a joint that is "
              "held by plastic pipe, and if the water is coming through the ceiling, turn the heating "
              "off and ring a plumber today.",
              bias=1,
              avoid=("buy", "best", "which", "cheapest", "size", "how many", "bleed", "bled", "cold",
                     "bottom", "noise", "banging", "boiler", "landlord", "tenant",
                     # "where is the valve on the hot water tank" was told to turn both radiator
                     # valves off: a tank's valve is not a radiator's
                     "water heater", "immersion", "immersion heater", "hot water tank",
                     "hot water cylinder", "water tank", "cylinder", "tank",
                     # radiators that heat up whenever the hot water runs are a stuck valve, not a
                     # leak: the word "water" was enough to make this the answer to that line
                     "hot water is on", "hot water comes on", "comes on when", "by itself")),
        entry("outside-drain", (("outside", "gully", "yard", "driveway", "pavement", "garden"),
                                ("drain", "blocked", "smell", "overflowing", "flooding")),
              ("Lift the drain cover and clear the gully of leaves and silt with gloves and a trowel, "
               "then flush it with a bucket of water. If it's still slow or smells after that, or it's "
               "the main sewer, ring your water company: blocked public sewers are usually their job and "
               "free to clear.")),
        # "sink" is in part one because the trap under a kitchen sink is where the hair and the fat
        # go; part two keeps it off the cleaning question ("how do i clean the sink").
        # A pair of scissors that will not cut is not the kitchen-cleaning routine, which was what
        # "how do i sharpen kitchen scissors" got from the word "kitchen" plus "how". A serrated
        # kitchen pair cannot be honed on a steel at all, which is why this has its own answer.
        entry("sharpening-scissors",
              # kitchen scissors only: a pair of garden shears is cut differently, and the answer
              # below is about the serrated edge a kitchen pair has
              (("scissors", "scissor", "kitchen scissors", "paper scissors", "safety scissors"),
               ("sharpen", "sharpening", "sharpened", "blunt", "dull", "wont cut", "won't cut",
                "doesnt cut", "doesn't cut", "dont cut", "don't cut", "not cutting", "cut properly",
                "jamming", "sticks", "tight")),
              "Look at the edge first: a serrated kitchen pair cannot be sharpened at all, and a "
              "smooth pair is done with a fine diamond file or a small whetstone, five or six light "
              "strokes along the bevelled side only, at the angle the bevel already has, then wipe the "
              "burr off with the flat of the stone. A stiff screw is usually the pivot, not the blade: "
              "a drop of oil and a quarter turn on the nut frees it. If the two blades no longer meet "
              "along their length, a repair shop re-grinds them for a few pounds, which is cheaper "
              "than a good new pair.",
              # garden tools are not a kitchen pair: shears, secateurs and hedge trimmers are in the
              # avoid list so "how do i sharpen garden shears" keeps its own answer
              avoid=("hair", "haircut", "cut my hair", "cut my own hair", "fringe", "topiary",
                     "hedge", "hedges", "lawn", "garden", "shears", "secateurs", "burglar",
                     "run with")),

        # A pool in the garden is emptied on purpose, and "how do i drain a paddling pool" was the
        # hair-in-the-trap card: "pool" and "pooling" are loose forms, and the row above read the
        # word without the thing it belongs to.
        entry("paddling-pool",
              # no "kids pool": "kids" is a key word of moving-with-kids and one more row using it in
              # this domain costs that row the rarity bonus it was getting ("how do i tell my kids
              # we're moving house" fell from moving-with-kids to screen-time)
              (("paddling pool", "paddling pools", "inflatable pool",
                "blow up pool", "blow-up pool", "paddling"),
               ("empty", "emptying", "emptied", "drain", "draining", "get rid", "tip", "tip out",
                "pour away", "water", "clean", "cleaning", "clean out", "store", "storing",
                "put away", "chlorine", "chlorinated", "how often", "change the water", "fill",
                "filling", "fill up")),
              "A paddling pool holds 300 to 800 litres, so buckets are the hard way: pull the drain plug "
              "if it has one, or lift one side and let it run into a drain or a big bucket, or hook a "
              "short hose over the lowest edge and syphon it out. Water that has only had children in "
              "it can go on the flower beds rather than the lawn, but water with chlorine or soap in it "
              "should go down a drain, since it scorches grass. Scrub the inside with hot soapy water, "
              "rinse, dry it in the sun and store it folded and dry, because a pool put away wet comes "
              "out black and slimy next summer.",
              # a swimming pool and a hotel pool are other questions, and a pool table is not water
              avoid=("swimming pool", "hotel", "lido", "leisure centre", "pool table", "pool cue",
                     "gene pool", "pool car", "football pool", "car pool")),
        # A hot tub is emptied and refilled on a schedule, and none of that was anywhere: "how do i
        # drain my hot tub" got the kettle-and-bicarbonate drain cleaner, "how often should i change
        # the water in a hot tub" got the garden's watering row, and "how do i clean my hot tub" got
        # the wash-temperature rule for a duvet. The tub is its own thing to keep, so it is its own
        # row: the water change is a schedule, and the way to empty it is a hose to a drain because
        # the chlorine kills the grass.
        entry("hot-tub-care",
              (("hot tub", "hot tubs", "hottub", "jacuzzi", "spa bath"),
               ("empty", "emptying", "emptied", "drain", "draining", "drained", "pump out",
                "pump it out", "siphon", "syphon", "change the water", "changing the water",
                "how often", "clean", "cleaning", "cleaned", "clean out", "flush", "flush out",
                "water out", "get the water out", "wont drain", "won't drain", "not draining",
                # the whole phrase, because "water" alone is the drinking-water rows' and "change" is
                # the bedding's: "how often should i change the water in a hot tub" was a hydration
                # answer about a long run
                "change the water in a hot tub", "change the water in my hot tub",
                "change the water in the hot tub", "change the hot tub water",
                "empty the hot tub", "drain the hot tub")),
              "Change the water every three to four months, or after about thirty uses, whichever "
              "comes first: a 4 to 6 person tub holds 1,000 to 1,500 litres, so check the level weekly "
              "with the hose and the chemicals, and do a full change when the water stops holding "
              "chlorine. To empty, hook a hose on the drain valve at the bottom into a drain, or drop a "
              "sump pump in, because a tub of chlorinated water kills the lawn and burns a border. "
              "Then flush the pipes with a line cleaner, wipe the shell with bicarbonate of soda rather "
              "than a detergent, and refill through the filter.",
              # a bath, a paddling pool and a swimming pool are other answers, and the heat questions
              # about a tub (how hot, is it safe, can a pregnant person use one) are not this one
              avoid=("bath", "baths", "bathtub", "shower", "paddling pool", "swimming pool",
                     "too hot", "how hot", "temperature", "pregnant", "pregnancy", "safe",
                     "safety", "heat rash", "warms up", "warm up time", "electrics", "electric",
                     "buying", "buy a", "worth it", "cost to run", "running cost", "cheap to run",
                     "cover", "lid", "steps", "chemcial", "chlorine level")),
        # "how do i empty a water butt" was a money row about a plan that went wrong, "how do i empty
        # my pond" was no answer at all, and "how do i empty a swimming pool" was told to start with
        # twenty minutes of lengths. All three are the same job - getting a lot of still water out of
        # something in the garden - and the sizes are what decide how, so one row answers all three.
        entry("empty-a-big-container",
              # no bare "pool": "pool" is the swimming pool's, the paddling pool's, the pool table's
              # and a puddle's, and the paddling pool row beside this one keys its own words
              # no bare "water tank": a loft tank, a header tank and a caravan tank are three other
              # jobs, and the garden water is what this row knows
              (("water butt", "water butts", "rain barrel", "rain butt",
                "pond", "ponds", "garden pond", "wildlife pond", "swimming pool", "swimming pools"),
               ("empty", "emptying", "emptied", "drain", "draining", "drained", "get the water out",
                "water out", "tip out", "tip it", "pump out", "pump it out", "siphon", "syphon",
                "get rid of the water", "hose out", "flush out",
                # the whole ask, because the butt's own row (how big a one to buy) keys the two words
                # and reads "empty a water butt" as a question about sizes
                "empty a water butt", "empty the water butt", "empty my water butt",
                "drain a water butt", "drain the water butt", "empty a pond", "empty the pond",
                "empty my pond", "drain a pond", "drain my pond", "empty a swimming pool",
                "empty the swimming pool", "empty my swimming pool", "drain a swimming pool")),
              "Run it to a bed or a drain, never the road, and let the size decide how: a water butt "
              "goes out of the tap at the bottom onto a hose, and a barrel with no tap is tipped on "
              "its side or syphoned with a hose kept full of water. A pond is emptied in autumn, not "
              "spring, when frogs and newts are in it: net the fish into buckets of pond water, keep "
              "the filter media wet in that water, and put the plants in a tray, because it goes back "
              "within a day. A swimming pool is "
              "20,000 litres or more, so it is a hired pump and a drain or a tanker, never the garden "
              "hose, and never the road drain without asking the council first.",
              # water in a garden is the watering row's, the pool for swimming is the stroke row's,
              # and a fish tank indoors is the tank's own answer
              avoid=("watering can", "irrigation", "sprinkler", "hose pipe ban", "fill", "filling",
                     "fill it", "install", "installing", "fit a", "fitting a", "diverter",
                     # no bare "swim" or "swimming" here: "a swimming pool" is the subject, and the
                     # stroke words below are what tell the two apart
                     "lengths", "lanes", "front crawl", "backstroke", "breaststroke", "lessons",
                     "learnt to swim", "learn to swim", "swim for fitness", "times a week",
                     "pool table", "pool cue", "hotel", "lido", "leisure centre", "gene pool",
                     "car pool", "fish tank", "aquarium", "toilet", "cistern", "radiator",
                     "boiler", "central heating", "header tank", "oil tank", "septic tank",
                     # a tank in a van or a boat is drained for the winter, and that is its own
                     # job: the caravan, the motorhome and the boat are named so this garden row
                     # does not answer them with a water butt
                     "caravan", "motorhome", "camper", "boat", "yacht", "narrowboat", "canal",
                     "van", "campervan")),
        entry("drain-blocked", (("drain", "shower", "shower tray", "bath", "plughole", "plug hole",
                                "sink", "basin", "handbasin", "washbasin", "tub", "bathtub"),
                                ("blocked", "blockage", "slow",
                                 # "why is my bath draining so slowly" reached the eat-slowly row,
                                 # because "drains slowly" is a phrase and nothing matched
                                 # "draining ... slowly": the verb and the adverb are own words
                                 "slowly", "draining", "drains", "drain", "clogged", "clog",
                                 # the rest of the clog family, which is how most people say it:
                                 # what main did not have was the verb and its -ed and -ing forms
                                 "clogs", "clogging", "clogged up", "unclog", "unclogging",
                                 "unclogged",
                                 # "why does my bath take so long to drain" and "the sink takes
                                 # ages to drain" are the same slow waste pipe, said with a time
                                 "so long to drain", "long to drain", "takes ages",
                                 "taking ages", "takes ages to drain", "ages to drain",
                                 "smells", "smell", "clear", "unblock",
                                 # a fixture that is choked is blocked, not breathing: "my bath is
                                 # choked" and "the shower is choked" are the hair-in-the-trap fault
                                 "choked", "choking", "chokes",
                                 "backed up", "not draining", "won't drain", "wont drain",
                                 "isnt draining", "isn't draining", "doesnt drain", "doesn't drain",
                                 # a tray of standing water is the same hair-in-the-trap fault as a
                                 # slow drain, and "the shower tray keeps filling with water" was an
                                 # echo because none of the words above are in it
                                 "fills with water", "filling with water", "fills up", "filling up",
                                 "keeps filling", "keeps filling with water", "water sits",
                                 "sits in the", "pooling", "pools", "puddle in", "wont empty",
                                 "won't empty", "not emptying", "goes down slowly",
                                 "drains slowly", "slow to drain", "standing water",
                                # hair is what blocks a plug hole, and saying so is the way most
                                # people describe the job ("how do i get hair out of the plughole")
                                "hair", "hairs",
                                # "what can i put down a smelly drain" named no action the second
                                # group knew, so it fell to the tiredness entry on "drained"
                                "smelly", "stinks", "stink", "put down", "pour down",
                                "drain cleaner", "through the drain", "down the drain")),
              ("Pull the hair and soap out of the trap first (a bent wire or tweezers does it), then "
               "pour a kettle of hot water down with a spoonful of bicarbonate of soda and vinegar; a "
               "plunger over the plughole clears the rest. Skip the chemical cleaner until last, and "
               "fill the trap with a hair collector so it does not come back. The reason is hair, "
               "soap and grease caught in the trap and the bend."),
              # a cistern that will not stop filling, or a tank, is another answer: "keeps filling"
              # belongs to this entry only when the water is going the wrong way, down a waste
              avoid=("outside", "gully", "driveway", "street", "pavement", "machine",
                     "washing machine", "dishwasher", "dryer", "washer", "freezer", "fridge",
                     "toilet", "toilets", "cistern", "ball valve", "ballcock", "tank", "loft",
                     "boiler", "radiator", "radiators", "central heating", "header tank",
                     # "pooling" is a loose form of "pool", so a pool emptied on purpose reached the
                     # hair-in-the-trap card: "how do i drain a paddling pool" wanted the plug or a
                     # hose and a bucket, and nothing here knows that
                     "paddling pool", "swimming pool", "hot tub", "water butt", "garden pond")),
        # Clearing a drain is one question; what may go down it is another, and every "can i put
        # oil down the drain" was answered with the trap and the plunger. The question words are in
        # the key because the fault words are not: a blocked drain is the row above, and this one
        # only ever speaks for a line that asks whether something may go down.
        entry("down-the-drain",
              (("down the drain", "down the sink", "down the plughole", "down the plug hole",
                "down the toilet", "down our drain", "down my drain", "into the drain",
                "into the sink", "flush", "flushed", "flushing", "down the loo"),
               ("can i", "could i", "should i", "is it ok", "is it okay", "ok to", "okay to",
                "safe", "safe to", "allowed", "what can i", "what should i", "what shouldnt i",
                "what should not", "anything", "never", "not to", "which things", "what things")),
              "Four things never go down a drain: fat, oil and grease (they cool, set and make "
              "fatbergs), wet wipes even the ones marked flushable, anything that swells or sets - "
              "rice, pasta, potatoes, flour, eggshells and pastry scraps go down soft and pack hard "
              "a metre along - and paint, thinner and the chemicals that go with them. Fat goes into "
              "a jar or the bin, wipes and grounds into the bin, rice and peelings into the food "
              "waste with a sieve in the plug for the last rinse. A toilet takes the three Ps and "
              "nothing else: pee, poo and paper. Soapy water, tea, milk and small crumbs are fine.",
              # a drain already blocked is the row above, and a machine or a tank is another
              avoid=("blocked", "blockage", "backed up", "wont drain", "won't drain",
                     "not draining", "smells", "smelly", "clear", "unblock", "plunger",
                     "washing machine", "dishwasher", "dryer", "machine", "boiler", "radiator",
                     "freezer", "fridge", "oil out", "pour old", "old oil", "recycle",
                     # bleach and coffee grounds have a card of their own that says more than a
                     # list can: the bleach one names the chlorine gas, and grounds are worth
                     # composting. "anything chemical" in the reply above would deny the bleach
                     # card's "a capful a week is fine", so the list stands down for both.
                     # "coffee ground" and not "coffee": a bare "coffee" fenced the list for
                     # "can i put coffee down the drain" as well, and that line has no card of its
                     # own, so it was left to the blocked-drain plunger.
                     "bleach", "bleaches", "caustic", "coffee ground", "used coffee",
                     "spent coffee", "coffee grouts",
                     # a cistern that will not stop is a fault, not a thing going down: "what
                     # should i do about the toilet flushing all night" got the list of things
                     # that never go down a drain, and the running-toilet row has the valve.
                     "keeps flushing", "constantly", "all night", "all day", "wont stop",
                     "won't stop", "keeps running", "running", "dripping",
                     # the fat in a roasting tin has a card that says how to get rid of it -
                     # wipe it out with kitchen paper while the pan is warm - and the list took
                     # that line away from it
                     "roasting tin", "roasting tray", "roasting pan", "baking tray",
                     "kitchen paper", "wipe the fat", "fat from the"),
              # a thing asked about before it goes down ("can i flush wet wipes down the toilet")
              # is this list, and the toilet row keys the same "flush": this row is the specific
              # one of the two, so it outranks the plunger rather than the plunger being stood down
              bias=3),
        # A cycle that takes hours is the most common thing people ask about a washer after a fault,
        # and it was the honest hedge. The length of a cycle is a fact, not a fault, and the reason it
        # runs long is the same on every machine.
        entry("wash-cycle-time",
              (("washing machine", "washer", "washing", "wash"),
               ("how long", "take so long", "takes so long", "so long", "hours", "an hour",
                "cycle", "cycle time", "wash cycle", "washing cycle", "long cycle", "eco",
                "quick wash", "30 minute", "15 minute", "how many minutes", "duration",
                "length of a cycle", "normal wash", "cotton wash", "eco wash", "express wash",
                "spin", "spin cycle", "rinse cycle", "drain cycle", "programme", "program")),
              "Most cycles are two to three hours on eco and about an hour on a normal 40C cotton "
              "wash, and nothing is wrong: eco runs the drum slowly and heats the water slowly so it "
              "uses less electricity, which is why the eco label says 3 hours plus. The quick washes "
              "are 15 to 30 minutes and are meant for a small, lightly worn load. A cycle that runs "
              "longer than the dial says is usually a cold fill taking ages, a blocked filter, or "
              "extra rinses switched on, so check the filter and the rinse setting before calling "
              "anyone.",
              # "wash" and "cycle" are both ordinary words elsewhere: a wash of a car, a cycle ride
              # to work ("how long does a wash cycle take" was the exercise-after-illness answer).
              # The machine words are what the line has to carry.
              avoid=("dishwasher", "tumble dryer", "dryer", "oven", "last", "lasts", "lasting",
                     "lifespan", "life span", "life expectancy", "replace", "often",
                     "car", "cars", "van", "bike", "bicycle", "motorbike", "dog", "dogs", "pet",
                     "hair", "hands", "face", "dishes", "windows", "walk", "run", "running",
                     "swim", "swimming", "gym", "exercise", "ill", "sick", "cold", "flu",
                     "cycle to work", "cycle ride", "bike ride", "ride to work",
                     # a pan being cooled so it can be washed is not a wash cycle: "how long should i
                     # cool a pan before washing" matched "washing" and "how long" and got the drum
                     "pan", "pans", "wok", "skillet", "saucepan", "pots", "cookware",
                     "washing up", "wash the pan", "before washing",
                     # a repair is a job on the machine, not a wash it runs: "how long does a
                     # washing machine repair take" was the eco cycle times, and the repair clock
                     # - one visit, an hour or two on site, the wait is the part - is the answer
                     # it wanted. The machine and the repair have to be said together: a bare
                     # "a repair" after a fault is the fault row's, which is a separate question
                     "washing machine repair", "washer repair", "machine repair",
                     "repair man", "repairman", "engineer", "call out", "callout",
                     "spare part", "spare parts",
                     # how long the washing takes to DRY is the drying question, not the cycle:
                     # "how long does washing take to dry indoors" was answered with the eco
                     # cycle times, which is a different length of time
                     "to dry", "dry indoors", "dry inside", "drying indoors", "drying inside",
                     "to dry it", "hang out", "hanging out", "on the line", "air dry"),
              ask=("how long", "so long", "hours", "cycle", "take", "takes", "duration"),
              # a machine that stopped part way through is a fault, and its own rows have the
              # door latch and the drain: "my washing machine stopped mid cycle" was answered
              # "most cycles are two to three hours ... and nothing is wrong", which reads like a
              # diagnosis and is not one. The guard is home.py's, so every symptom added to the
              # fault words there stands this row down too.
              guard=_not_a_machine_that_has_gone,
              bias=4),
        # "can i hang washing out today" was the length of a wash cycle, because "washing" and
        # "today" are both in that row's reach and the machine was never mentioned. Hanging it out
        # is a different question with a different answer, and it is the one a washday starts with.
        entry("washing-outside",
              # Not the bare word "bedding": `lookup._forms` un-doubles it to "bed" the way
              # "running" gives "run", so a bed in the line satisfied it and "get out of bed" was
              # answered with the drying weather. Saying it with an article or a possessive is the
              # whole fix - "the bedding", "my bedding", "bedding dry" is the thing that hangs out
              # and never the bed - and the bare word has to go with it or the row loses its own
              # question: "i want to get the bedding dry outside today" then "what time should i
              # put it out" was answered indoors, on a deck row (`intent-putting-out-when`) that
              # main had right. Not "whites" either, for the same reason in the other direction:
              # `_forms("whites")` holds "white", so "my hands go numb and white in the cold"
              # matched on the colour and the weather words finished the row. "the whites" alone
              # then lost the commonest way people say it - "my whites" was named in this comment
              # and not in the key, so "can i put my whites on the line" got a punt - so the
              # possessive forms and two-word ones ("whites dry", "whites out") are in the key
              # beside it. None can be the colour: each carries a word the colour is never said
              # with, and "my hands go numb and white" says none of them.
              (("washing", "washing line", "laundry", "clothes", "wash", "the whites",
                "my whites", "our whites", "whites dry", "whites out", "sheets",
                "towels", "the bedding", "my bedding", "bedding dry"),
               ("hang", "hanging", "out", "outside", "line", "dry", "drying", "dried", "today",
                "tomorrow", "outside today", "put out", "airing", "airer", "weather", "rain",
                "raining", "wind", "windy", "sun", "sunny", "frost", "cold", "winter", "summer",
                "dryer", "tumble")),
              "A dry, breezy day dries a normal load outside in two to four hours, and a cold sunny "
              "day with wind is nearly as good as a warm one, so 8C and breezy beats 20C and still. "
              "Rain, fog and damp evening air put the water back, so bring it in before dusk. In "
              "winter, spin it an extra five minutes, then dry it indoors on an airer with a window "
              "open a crack: the water has to go somewhere, and an open window is cheaper than the "
              "heating.",
              # A spot on one thing is not a load to dry: "how do i get a stain out of a white
              # shirt", "how do i get blood out of a white shirt" and "how do i get red wine out
              # of a white shirt" all reached this row, because "whites" folds to "white" and the
              # line has an "out" in it, and were told the weather for a washday. The stain rows
              # answer those, and the words below are the ones a spot is said with.
              avoid=("stain", "stains", "stained", "staining", "spot", "spots", "marked",
                     "blood", "grass", "red wine", "wine", "coffee", "tea", "ink", "mud",
                     "vomit", "sick", "bleach", "bleached", "yellow", "yellowed", "sweat",
                     "grease", "oil", "curry", "tomato", "chocolate", "pen", "marker",
                     "out of a white", "out of my white", "out of the white", "out of whites",
                     # a fault, a smell, a leak or a cycle length is the machine's question, and
                     # the machine row answers it better than the weather
                     "washing machine", "washer", "not spinning", "wont spin", "won't spin",
                     "smell", "smells", "smelly", "musty", "mould", "mold", "leak", "leaking",
                     "drain", "filter", "cycle", "programme", "program", "eco wash", "spin speed",
                     "broken", "repair", "error code", "fault",
                     # "out" is one of this row's key words, so a load that came out of the
                     # machine wet was answered with the weather, and so was a stain asked as
                     # "how do i get the oil out of clothes". A wet load is the machine's
                     # question; a stain has its own card. The words that say so stand this
                     # row down, and the guard reads a line like "dry clothes without a tumble
                     # dryer" as it was typed.
                     "come out", "comes out", "came out", "coming out", "get out", "got out",
                     "getting out", "remove", "removing", "dirty", "smell out",
                     # A stain is a spot-clean question about one thing, not a question about the
                     # weather: "how do i get sweat stains out of a white shirt" was answered with
                     # "a dry, breezy day dries a normal load outside in two to four hours", because
                     # "whites" and "out" are both in this row's keys and the stain row's own words
                     # scored lower. The stain rows in clothing.py own these lines.
                     "stain", "stains", "stained", "sweat", "sweaty", "ink", "blood", "grass",
                     "grease", "oil", "sauce", "coffee", "tea stain", "wine", "mud", "makeup",
                     "deodorant", "bleach mark"),
              guard=_not_a_drying_inside_question,
              bias=3),
    ]
