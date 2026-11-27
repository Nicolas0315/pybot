"""Rows 3 of 10 of `home_craft.entries()`: `washing-machine-smell` .. `oven-grill`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _the_leak_is_a_machines,
)


def rows():
    from ..knowledge.home import (
        JOB_GUARD, LANDLORD_JOB_FITTINGS, LANDLORD_REPAIR_LETTER, NOISE_WORDS, TAKES_THINGS,
        _a_dryer_is_not_a_washer, _a_visit_not_a_purchase, _machine_takes, _washer_sound_fault,
        entry, the_fault
    )
    return [
        entry("washing-machine-smell", ("washing machine", ("smell", "musty", "smelly", "clean",
                                                            "smells")),
              # The cause is its own short sentence after the fix, because "why" after this answer
              # is the commonest follow-up and the cause read out of the answer is what it gets: a
              # reply that only names the wash gets the shrug instead. The fix stays the first
              # sentence, so "what should it be" and "tell me more" still find it.
              "Run a hot 60C or 90C service wash with a washing-machine cleaner or a cup of "
              "bicarbonate of soda, and clean the filter and the detergent drawer while it runs. The "
              "smell lives in damp lint and detergent trapped in the seal, the drawer and the filter. "
              "The wash itself is about two hours. Leaving the door and drawer open between washes "
              "is what stops the smell coming back."),
        # Mould in the machine is its own question: the smell answer is a service wash, but the
        # mould lives in the fold of the rubber door seal, the detergent drawer and the filter, and
        # saying "run a hot wash" alone leaves the person with the same black line next month.
        # On main `ca942da` the line reached the football boot that has moulded studs instead.
        entry("washing-machine-mould",
              (("washing machine", "washer", "washing mashine", "washer dryer", "tumble",
                "laundry", "drum", "detergent drawer", "door seal"),
               # no bare "clean": "how do i clean my washing machine properly" is the service wash,
               # and this row is for the mould the wash does not lift out of the seal
               ("mould", "mold", "mouldy", "moldy", "mildew", "black mould", "black mold",
                "smells of mould", "smell of mould", "smells mouldy", "spores", "drawer",
                # not a bare "filter": a machine's filter is the hatch and the bowl, which has its
                # own row, and "how do i clean a washing machine filter" was being answered with the
                # black in the seal. A mould word carries every mould-in-the-filter line on its own.
                "detergent drawer", "seal", "door seal", "rubber",
                # not the smell words "damp" and "musty": "my washing machine smells of damp" is
                # the service wash, and the follow-up about the filter is read out of that answer
                # the plain asking shapes: they are safe here because the first part is the machine,
                # so "how do i get rid of mould" without a machine in it never reaches this row
                # not "how do i": that alone made "how do i clean my washing machine" the mould
                # answer, and the general clean is the service wash
                "get rid", "rid of", "remove", "removing", "kill", "coming back",
                "keeps coming back")),
              ("The black comes back because it lives in the fold of the rubber door seal, so that is "
               "the bit to clean: pull the seal open, wipe the fold with a cloth and a little white "
               "vinegar or a mould spray, and dry it. Then run the hottest empty wash the machine has "
               "with a machine cleaner or a cup of bicarbonate of soda, clean the detergent drawer and "
               "the filter out, and leave the door and the drawer open between washes so the drum "
               "dries. Use liquid detergent rather than powder at low temperatures and stop leaving "
               "wet washing in the drum. A seal that is black right through and slimy will not clean "
               "up: it is a cheap part and an easy swap."),
              # "how do i stop the machine smelling of damp" is the smell row, and a drum that will
              # not drain or leaks is not a mould question
              avoid=("leak", "leaking", "puddles", "wont drain", "won't drain", "not draining",
                     "wont spin", "banging", "noisy", "error code",
                     # "door seal" is in the key above, so a fridge, a freezer or an oven brought its
                     # own door seal here: "my fridge door seal is broken" was told to wipe the fold
                     # with white vinegar. A machine that is not in the key at all is not this row.
                     "fridge", "freezer", "oven", "dishwasher", "microwave", "fridge freezer",
                     # "my washing machine smells of damp" is the service wash: the smell of damp
                     # and a musty machine are the smell row's, and only the word mould is this one's
                     "damp", "musty", "damp smell", "smells of damp", "smells musty",
                     # a machine's filter has its own row and its own job: "how do i clean the
                     # filter" is not the mould in the seal, but "mould in the filter" is
                     "clean the filter", "cleaning the filter", "clean out the filter",
                     "empty the filter", "unblock the filter", "clear the filter"),

              bias=1),
        # A washer that runs the wash stone cold is a real fault and it had no card at all: the
        # line came back as a greeting once the leak row stopped taking the bare word "water",
        # and before that the drain row took it and talked about the filter. The heating half of
        # the machine is the element, the thermostat that reads the water and the relay on the
        # board, in that order of likelihood.
        entry("washing-machine-not-heating",
              (("washing machine", "washer", "washer dryer", "washing mashine", "wash cycle",
                "wash", "machine"),
               ("not heating", "isnt heating", "isn't heating", "not heat", "doesnt heat",
                "doesn't heat", "didnt heat", "didn't heat", "wont heat", "won't heat",
                "not getting hot", "isnt getting hot", "isn't getting hot", "wont get hot",
                "won't get hot", "cold wash", "stays cold", "water stays cold", "stone cold",
                "no hot water", "heat", "heating")),
              "Check the programme first: a 30C or a cold wash never heats much, and many machines "
              "have a cold-only option that stops the element coming on. If it is a hot programme and "
              "the door glass is still cold after twenty minutes, the element is the usual cause - a "
              "cheap part that an engineer swaps in half an hour - and the thermostat that reads the "
              "water or the relay on the board are the next two. A machine that heats on some "
              "programmes but not others is a board fault, not the element.",
              # a dryer that will not heat, a house with no hot water and a machine that will not
              # empty or is full of water are all different questions with their own answers
              avoid=("tumble dryer", "tumble drier", "dryer", "drier", "dishwasher", "dish washer",
                     "radiator", "radiators", "boiler", "central heating", "house", "shower",
                     "tap", "taps", "immersion", "hot tub", "not draining", "wont drain",
                     "won't drain", "blocked", "clogged", "full of water", "smells", "smelly",
                     "buy", "which", "best", "cheapest", "price", "worth it", "filter")),
        entry("washing-machine-leak",
              (("washing machine", "washer", "washer dryer", "washing mashine"),
               # "floor" alone was a leak key, so a machine that bangs and walks across the floor was
               # answered with the leak: it is the water on the floor that is the leak
               ("leak", "leaking", "leaks", "leaked", "puddle", "puddles", "water", "dripping",
                "flooding", "on the floor", "all over the floor", "under the machine",
                "underneath the machine", "under it")),
              "Stop the cycle, unplug it and turn the water off at the valve behind it, and leave it off "
              "until the leak has stopped. Water at the front is usually the door seal or the filter cap, "
              "water underneath is the pump or a loose inlet or drain hose, so check the hose "
              "connections before you call anyone. A leak from inside the machine itself is an "
              "engineer's job.",
              # a drum that will not empty, or one standing full of water, is the drain entry's line:
              # both of those hold the word "water" and this entry would otherwise take them
              guard=_the_leak_is_a_machines,
              # the laundry-sorting row keys "washing" and ranks level with this one, so water on
              # the floor beside the machine was the sorting card: the guard above is what keeps
              # this bias from reaching a line that only mentions the water
              bias=2,
              avoid=("buy", "which", "best", "cheapest", "washing machine buy",
                     "wont drain", "won't drain", "not draining", "empty", "emptying",
                     "wont empty", "won't empty", "full of water", "water in the bottom",
                     "standing water", "sitting in the bottom", "sitting in", "sitting water",
                     "holding water", "holds water", "filter", "pump")),
        # --- how much life a boiler has left ------------------------------------
        # "my boiler is 15 years old" and "the boiler is going to die on us" were both shrugs on main
        # `d310ab7`, and "how long does a boiler last" got the engineer's-call-out answer, which is
        # not the question: an age is a planning question, not a fault.
        entry("boiler-age",
              (("boiler", "boilers", "combi", "central heating"),
               ("how long", "last", "lasts", "how old", "old", "years", "15 years", "age", "die",
                "dying", "on its way out", "end of its life", "replace", "replacing", "replacement",
                "new boiler", "worth", "efficient", "efficiency", "lifespan", "life span",
                "how much longer", "keep going", "go on for")),
              ("A boiler is built for about 10 to 15 years, so at 15 it is at the end of its life even "
               "if it is working today - the useful thing now is to have the money ready rather than "
               "be without heat in January. Get it serviced, keep the service record, and start "
               "collecting two or three quotes in the quieter months, because a combi swap is roughly "
               "2,000 to 3,000 pounds fitted and it is the same job whether you are desperate or not. "
               "A modern condensing boiler is around 90 per cent efficient against 70 to 80 for an "
               "old non-condensing one, which is the part of the bill you get back; a well-kept "
               "boiler that still works does not have to be replaced on age alone, but plan for it "
               "rather than wait for the morning it dies."),
              # a fault is boiler-broken's answer, a service is its own, and the cost of a new one is
              # the quote question: an age is a planning question
              avoid=("broken", "broke", "leak", "leaking", "pressure", "no hot water", "no heating",
                     "noise", "noisy", "kettling", "error", "fault", "reset", "not firing",
                     "wont fire", "service", "serviced", "servicing", "annual", "insurance", "cover",
                     "radiator", "radiators", "thermostat", "timer", "smart",
                     # a heat pump weighed against it is the choice between the two, which is the
                     # heat-pump row's answer: this one is about how long a boiler lasts
                     "heat pump", "heat pumps", "air source", "ground source") + JOB_GUARD,
              bias=1),
        # --- how long the job takes, not how long the machine lasts --------------------------------
        # "how long does a boiler repair take" was answered with a boiler's ten to fifteen years and
        # "how long does a fridge repair take" with four days of cooked food: an appliance and a clock
        # were in the line, so a clock entry took it (urban-orange, quality). JOB_GUARD stands those
        # rows down and this one answers the question that was asked - the visit, the part, the day.
        # --- how long a new one takes to fit, which is a longer job than the repair ---------------
        # "how long does it take to fit a new boiler" was a hedge on main `b7527cf`: the repair-time
        # row is keyed on the job words a visit is asked with (repair, fix, install), and "fit" and
        # "replace" were not among them, so the line reached no row at all. The fitting is the longer
        # job of the two and it is the one people plan a day off for, so it has its own row: the swap,
        # the day, and the gas check the repair row's last sentence only mentions in passing.
        entry("swap-time",
              (("boiler", "boilers", "combi", "central heating", "fridge", "fridge freezer",
                "freezer", "washing machine", "washer dryer", "tumble dryer", "dishwasher",
                "oven", "cooker", "hob", "radiator", "radiators", "shower", "shower pump"),
               ("new", "new one", "fit", "fits", "fitting", "fitted", "swap", "swaps", "swapping",
                "replace", "replaces", "replacing", "replacement", "install", "installs",
                "installed", "installation")),
              "Fitting a new one is the long job, not the short one: an hour or two for a washing "
              "machine or a dishwasher, about an hour a radiator once the system is drained, and a "
              "boiler is the big one - usually a full day plus the gas check at the end. Ask when you "
              "book whether the price includes taking the old one away, the gas safety check and any "
              "making good, because those are the parts that turn a quote into a bigger bill.",
              ask=("how long", "long does", "how many days", "how many hours", "days", "hours",
                   "wait", "time", "take", "takes", "taking", "long will"),
              avoid=("last", "lasts", "lasting", "years", "lifespan", "how old", "cost", "costs",
                     "much", "price", "prices", "quote", "quotes", "cheap", "cheaper", "expensive",
                     "worth", "pay", "broken", "broke", "dead", "leak", "leaking", "no hot water",
                     "no heating", "pressure", "fault", "error", "not working", "stopped", "reset",
                     "noise", "noisy", "kettling", "service", "serviced", "servicing", "annual") ,
              bias=1),
        entry("repair-time",
              (("boiler", "boilers", "combi", "central heating", "fridge", "fridge freezer",
                "freezer", "washing machine", "washer dryer", "tumble dryer", "dishwasher",
                "oven", "cooker", "hob", "radiator", "radiators", "shower", "shower pump",
                "hot water", "heating", "electrics", "electrician", "plumber", "tradesman"),
               ("repair", "repairs", "repaired", "fix", "fixes", "fixed", "fixing", "install",
                "installs", "installed", "installation", "engineer", "plumber", "call out",
                "callout", "call-out", "come out", "coming out", "swap", "swapping", "job")),
              "Most jobs are done in one visit: an hour or two on site for a repair, and the wait is "
              "usually the part, so if something has to be ordered expect a few days between the "
              "first call and the fix. Ask when you book whether the price covers the first hour and "
              "whether the part is included, and get the call-out fee before anyone comes out. A "
              "boiler swap is the long one - usually a full day, plus the gas check afterwards.",
              ask=("how long", "long does", "how many days", "how many hours", "days", "hours",
                   "wait", "time", "take", "takes", "taking", "long will"),
              avoid=("service", "serviced", "servicing", "annual", "cost", "costs", "much", "price",
                     "prices", "quote", "quotes", "cheap", "cheaper", "expensive", "worth", "pay",
                     # a fault line belongs to the fault row: "my boiler is broken, how long will the
                     # repair take" wants the pressure gauge and the reset before the calendar
                     "broken", "broke", "dead", "leak", "leaking", "no hot water", "no heating",
                     "pressure", "fault", "error", "not working", "stopped", "reset", "noise",
                     "noisy", "kettling", "last", "lasts", "lasting", "years", "lifespan"),
              bias=1),
        entry("boiler-broken", ("boiler", ("broken", "break", "breaks", "broke", "dead", "not working",
                                            # the everyday ways of saying a machine has stopped, which
                                            # this row did not name: "my boiler has packed in" got
                                            # "Ugh, those are fiddly" and no help at all
                                            "packed in", "packed up", "packing in", "has packed",
                                            "given up", "gave up", "conked out", "conk out",
                                            "on the blink", "gone wrong", "playing up", "acting up",
                                            "knackered", "has died",
                                            "stopped", "repair", "repairing", "repairs", "fixing",
                                            "no hot water", "no heating", "noise", "noisy",
                                            "kettling", "reset", "not firing", "wont fire", "wont start",
                                            "wont come on", "firing", "cutting out", "cuts out",
                                            "cutting off", "locks out", "lockout", "shutting",
                                            "not responding", "thermostat", "morning", "fault",
                                            "error", "cold",
                                            # "my boiler is not heating the water" named no hot water
                                            # and no leak, so it fell through to boiler-leak on the
                                            # bare word "water" and was told to put a bowl under it
                                            "not heating", "isnt heating", "isn't heating",
                                            "heating the water", "heating water", "not hot",
                                            # a boiler that switches itself off is this answer, not
                                            # the generic appliance card
                                            "switches itself off", "switching itself off",
                                            "turns itself off", "turning itself off",
                                            "keeps switching off", "keeps turning itself off",
                                            # a boiler that is on but not heating the water
                                            "not heating", "isnt heating", "isn't heating",
                                            "not getting hot", "not warming", "heating water",
                                            "heat water",
                                            # "the boiler is on but nothing happens" is the same
                                            # no-heat morning said as an absence: the symptom is that
                                            # nothing happens, and without these two phrases the line
                                            # only had the word "boiler" to go on and fell through
                                            "nothing happens", "does nothing", "nothing at all")),
              "Check the pressure gauge (1 to 1.5 bar), the thermostat and the boiler's reset button, "
              "and make sure the programmer is on the hour you think it is; a pressure top-up or a reset "
              "fixes a lot of no-heat mornings. The checks take ten minutes. In a cold snap, the white "
              "condensate pipe outside can "
              "freeze and stop the boiler, so pour warm water along it. If it locks out twice, or you "
              "smell gas, stop and call a Gas Safe engineer: gas is not a DIY job.",
              # A quote is a price question, not a symptom: "i got a quote for 1,500 to fix the boiler,
              # does that sound right" wants a way to check a price, and the composer has a line for it.
              avoid=("landlord", "tenant", "letting agent", "rent", "deposit",
                     "quote", "quoted", "quotes", "estimate", "estimated", "invoice",
                     # a kettle in the kitchen is not a sick boiler, even straight after a boiler
                     # question: "how long does it take to boil a kettle" was this card
                     "kettle", "kettles", "boil a kettle", "tea", "coffee"),
              ask=("boiler", "heating", "hot water", "radiator", "radiators")),
        # "no heating" and "the heating isnt working" name no boiler at all, so `boiler-broken` (which
        # needs the word) stood down and a cold house got "Great - shout if you need anything else".
        # The same three-word shape as `no-hot-water`: the phrase itself is the key, and the second
        # group repeats the subject so a line with no verb in it still has two words to score on.
        entry("no-heating",
              (("no heating", "heating is off", "heating gone off", "heating has gone off",
                "heating not working", "heating isnt working", "heating isn't working",
                "heating has stopped", "heating stopped", "heating wont come on",
                "heating won't come on", "heating wont fire", "heating won't fire",
                "heating is broke", "heating broke", "radiators are cold", "radiators cold",
                "radiators not hot", "radiators wont heat", "radiators won't heat",
                # "my heating is broken" was the one plain way of saying it that this row missed,
                # and it echoed the line back. "broken" and "dead" alone are too common to key, so
                # the shapes are named whole, and the thermostat gets the same treatment because
                # "my thermostat is not working" is the same cold house with a different subject.
                "heating is broken", "heating broken down", "heating has broken down",
                "heating is dead", "heating has died", "heating is bust",
                "heating is not working", "heating not coming on", "heating is not coming on",
                "heating isnt coming on",
                "heating isn't coming on", "heating wont turn on", "heating won't turn on",
                "central heating is not working", "central heating isnt working",
                "central heating has stopped working", "central heating has packed up",
                "thermostat is not working", "thermostat not working", "thermostat is broken",
                "thermostat broken", "room thermostat is not working",
                "no heat", "heating keeps going off",
                "heating keeps cutting out", "heating cuts out", "heating keeps turning off",
                "heating comes on and off", "heating has packed up",
                # the fault told as a length of time is the commonest way to say it, and the refund
                # ladder used to take it on "broken" plus "weeks": "the heating has been broken for 3
                # weeks", "the hot water has been off for a week", "the heating has been out since
                # tuesday". The goods row stands down for "heating" and "hot water" now, so without
                # these the cold house got "tell me what it does".
                "heating has been broken", "heating has been off", "heating has been out",
                "heating has been dead", "heating has been cut off", "heating has been turned off",
                "heating is off", "heating hasnt worked", "heating hasn't worked",
                "heating has not worked", "heating hasnt been working", "heating hasn't been working",
                "heating has not been working", "heating stopped working", "heating isnt heating",
                "hot water has been off", "hot water has been out", "hot water has gone off",
                "hot water is off", "no hot water for", "no heating for", "no heating since",
                "heating has not come back on", "heating hasn't come back on"),
               # no bare house/flat/cold here: "my house is cold" and "my flat is freezing" are the
               # keep-the-house-warm-for-less answer, and a heating fault is a heating word
               ("heating", "radiator", "radiators", "boiler", "thermostat", "central heating",
                "room thermostat", "winter", "morning", "why", "fix", "check",
                # "the hot water has been off for a week" names the fault and nothing else, so the
                # second word has to be the hot water itself or the line gets an echo back instead
                # of the cold-house card. It only counts with a fault already named above.
                "hot water",
                # "what are my rights" and "what can i do" are the follow-up to a fault that has
                # dragged on, and this card is the one that says who has to put it right
                "rights", "what can i do", "who do i call", "get it sorted", "get it fixed")),
              ("Check the thermostat and the programmer first: a timer slipped to water only, a room "
               "stat turned down, or flat batteries in a wireless one are the commonest cold houses. "
               "Then look at the boiler's pressure gauge (1 to 1.5 bar cold) and top it up at the "
               "filling loop, and press reset once. In a cold snap the condensate pipe outside can "
               "freeze, so pour warm water along it. If it still will not fire, or you smell gas, "
               "that is a Gas Safe engineer."),          bias=1,
              avoid=("food", "reheat", "heatwave", "hot weather", "sun", "sunburn", "hayfever",
                     # the row keys "rights" because a fault that has dragged on is followed by
                     # "what can i do", but this card only says what to check: a line that asks
                     # about rights is the landlord's-repairs letter, which names the reasonable
                     # time and what came with the flat
                     "my rights", "what are my rights", "my legal rights", "am i entitled",
                     "heating bill", "energy bill", "bill", "cost", "price", "cheap", "tariff",
                     "quote", "insulation", "car", "cars", "van", "engine", "microwave", "oven",
                     "saucepan", "water bottle", "hot water bottle", "electric blanket",
                     "microwave",
                     # not every "heating" is a house: a car heater, a heat pad, an office, a
                     # caravan or a greenhouse has no programmer and no pressure gauge, and the
                     # thermostat-first answer would be confidently wrong for them
                     "motorhome", "camper", "caravan", "office", "workplace", "heating pad",
                     "heat pad", "underfloor", "greenhouse", "fish tank", "seat heater", "hot tub",
                     "car heater",
                     # a cold house with a baby, a disabled person or a ninety-year-old in it is not
                     # a boiler question first: the line names the person, and the answer that says
                     # "ring 111 or your health visitor today" is the better one to keep
                     "baby", "babies", "newborn", "months old", "weeks old", "toddler",
                     "disabled", "disability", "carer", "frail", "elderly", "pensioner",
                     "health visitor", "in her 80s", "in his 80s", " is 85", " is 90", " is 95",
                     "over 80", "over 85", "over 90",
                     # "do i need to turn the heating off first", after a radiator answer, is about
                     # the job in hand; the context makes the heating a subject again and this entry
                     # was taking the follow-up
                     "turn off", "turning off", "turn it off", "turning it off", "off first",
                     "bleed", "bleeding", "bleed it", "radiator key",
                     # a radiator that is cold at the top and hot at the bottom is air, and the
                     # bleed answer owns it; a line that names the boiler or its pressure is
                     # `boiler-broken`'s ("my boilar pressure has droped and the heating wont come on"
                     # was taking this answer, thermostat first, over the pressure gauge).
                     "at the top", "at the bottom", "cold at the top", "hot at the bottom",
                     "top half", "boiler", "combi", "pressure", "gauge", "locks out", "lockout",
                     "fault code",
                     # "and how often should i do that", after a bleed answer, asks a frequency this
                     # entry does not have; the context makes radiator and cold the subject again
                     "how often", "how many times")),
        # "Is it worth getting someone out" after a boiler answer is a decision about paying a
        # tradesman, and the leaning line's word ("loft") handed it to the loft-conversion price with
        # its £25,000 figure. The subject has to come from the boiler, so the ask gate holds it to the
        # lines where a boiler or its heating is already the subject; a service is a cost question and
        # belongs to the boiler-service row in costs.py.
        entry("boiler-callout", (("boiler", "heating", "hot water", "radiator", "radiators", "combi"),
                                 ("someone out", "someone in", "get someone", "call someone",
                                  "an engineer", "engineer", "callout", "call out", "tradesman",
                                  "worth getting", "worth paying", "worth a call")),

              "Yes for anything on the gas side, and the pressure gauge (1 to 1.5 bar) and the reset "
              "button are worth trying first. A Gas Safe engineer's callout is usually £60 to £120, "
              "and it is worth paying once a fault repeats rather than for a one-off reset. Note the "
              "make and model, the error code and what happens when it cuts out, because that is what "
              "turns a second visit into a first fix. If you smell gas, or water is leaking near the "
              "electrics, turn it off and call the emergency line.",
              avoid=("quote", "quoted", "estimate", "landlord", "tenant", "deposit", "how much",
                     "cost", "price", "cheapest", "install", "new boiler", "replace", "replace it",
                     "service", "serviced", "servicing", "safety check"),
              # "the boiler is making a noise, is it worth getting someone out" ties the price of a
              # new boiler on score, and the person is asking whether to pay for a visit, not for a
              # boiler, so this one is the more specific of the two.
              bias=2,
              # "worth getting" is this row's question when the line names somebody to come out or
              # something wrong; "is it worth getting a heat pump" is a purchase, not a callout.
              guard=_a_visit_not_a_purchase,
              ask=("boiler", "heating", "hot water", "radiator", "radiators", "combi")),
        entry("landlord-damp",
              (("landlord", "landlady", "letting agent", "housing association", "council", "my fault"),
               ("damp", "damp patch", "damp patches", "damp walls", "mould", "mold", "mouldy", "moldy",
                "black mould", "black mold", "mildew", "condensation")),
              "Put it in writing with photos and dates, and ask them to find the cause rather than paint "
              "over it: a coat of paint is the one repair that makes damp come back. If they will not "
              "act, your council's environmental health team can inspect damp and mould as a hazard to "
              "health and make the landlord deal with it, and Shelter or Citizens Advice will help you "
              "write the letter free. Keep paying the rent and keep copies of everything you send. A "
              "window open for ten minutes a day and a dehumidifier hold it while you wait.",
              # A disbelieving landlord is the same question: the person is asking what they can do
              # about it, not whether it is really damp.
              # A line that asks about being evicted, or about a section 21 notice, is asking about the
              # tenancy and not about the wall: it has its own answer, and this one would bury it under
              # a repair letter.
              avoid=("evict", "evicted", "evicting", "eviction", "evictions", "section 21", "section 8",
                     "s21", "revenge", "kick me out", "kick us out", "throw me out", "throw us out",
                     "get rid of me", "notice to quit"),
              bias=1),
        # A tenant who says they rent, and names no landlord, is the same question: "im renting and my
        # washing machine has been broken for 2 weeks" and "im a tenant and the boiler has been broken
        # for a week" were the appliance checks (ring the retailer) and a Citizens Advice hedge, and
        # the letter above is the answer either way. Its own wording already draws the line the person
        # needs: what came with the flat is the landlord's, what they brought is theirs.
        entry("landlord-repairs", (("landlord", "landlady", "letting agent", "tenant", "tenants",
                                   "i rent", "im renting", "i'm renting", "we rent", "renting",
                                   # The home is named as a place, and the person never says
                                   # "tenant": "the washing machine in my flat has been broken for 2
                                   # weeks", "the oven in my rented flat is broken". `faulty-goods`
                                   # stands down for these lines (its guard), so this row is what
                                   # answers them.
                                   "in my flat", "in the flat", "in our flat", "in my rented",
                                   "rented flat", "rented house", "rented home", "my rented",
                                   # "what are my rights" is in the key because a line can name the
                                   # fault and the right without a flat: "the heating has been
                                   # broken for 3 weeks, what are my rights".
                                   "the flat came with", "my rights", "what are my rights",
                                   "as a tenant", "my tenancy"),
                                   ("fix", "repair", "broken", "boiler", "refuse", "refuses", "ignore",
                                    "ignoring", "rights", "wont", "won't", "not fixing",
                                    # A fixture that came with the flat is still the landlord's, so
                                    # the appliance names are here: "i rent and the oven has been
                                    # broken for weeks" reaches the letter. Time words ("weeks",
                                    # "months") stay out - with them the follow-up "its been 3 weeks"
                                    # lost the letter with the boiler already in it.
                                    "heating", "hot water", "oven", "washing machine", "washer",
                                    "dishwasher", "fridge", "freezer", "shower", "toilet",
                                    # "does nothing" is the plainest way people say a landlord is
                                    # not fixing it, and without it the line matched no answer at
                                    # all: "my landlord does nothing about the mould" came back
                                    # "Got it. Is there anything you'd like a hand with?"
                                    "does nothing", "doesnt do anything", "doesn't do anything",
                                    "not doing anything", "isnt fixing", "isn't fixing",
                                    # Not calling back is the same failure as not fixing: "the letting
                                    # agent still hasnt called me back" reached no row at all and got
                                    # an echo of its own words back.
                                    "called back", "call back", "called me back", "hasnt called",
                                    "hasn't called", "havent called", "haven't called", "never called",
                                    "not called back", "still waiting", "chased", "chasing",
                                    "calls back", "phoned back", "not called", "no reply", "reply",
                                    "replied", "answers", "respond", "responded", "get back to me",
                                    "got back to me", "chase", "emails", "emailed", "email",
                                    "heard nothing", "ignores", "waiting", "keeps saying",
                                    "fobbed off",
                                    # The fault told as a length of time, which is how a repair that
                                    # has not happened is said: "the heating has been broken for 3
                                    # weeks", "it has not been fixed".
                                    "has been broken", "have been broken", "be been broken",
                                    "broken for", "broken since", "broken weeks",
                                    "not been fixed", "hasnt fixed", "hasn't fixed", "not fixed",
                                    "not working", "stopped working",
                                    # the duty itself, asked as a list of what they must do. Without
                                    # these, "what are my landlord's obligations" was a shrug.
                                    "responsibilities", "responsibility", "obligations",
                                    "obligation", "should fix", "has to fix", "have to fix",
                                    "must fix", "supposed to fix", "supposed to repair",
                                    "what must", "what do they have to", "what does he have to",
                                    "what does she have to")),          the_fault(
                  # The letter is quoted at the end of the answer, not its middle: a long answer is
                  # sometimes split across two turns, and a split inside a quoted letter left
                  # "Thanks, [name].\" Landlords have to do most repairs..." as a reply of its own.
                  "Landlords have to do most repairs in a reasonable time, and anything that came with "
                  "the flat counts, appliances included, while something you brought with you is "
                  "yours to fix. Put it in writing, a text or email is fine, and keep a copy: \"Hi - "
                  "I reported the {fault} on [date] and nothing has been done. Please arrange a "
                  "repair within 14 days.\" If they ignore you, your council's environmental health "
                  "team or Shelter can push it along.",
                  "Put it in writing, a text or email is fine, and keep a copy. Name what is wrong "
                  "and when it started, say what you want done and ask for a date, then keep the "
                  "messages: landlords have to do most repairs in a reasonable time, and anything that "
                  "came with the flat, appliances included, counts, while something you brought with "
                  "you is yours to fix. If they ignore you, your council's "
                  "environmental health team or Shelter can push it along."),
              # Money the landlord is holding is a tenancy question, not a repair one: the deposit
              # answer knows the protection scheme and the dispute service, this one does not.
              # A sale is not a repair either: the tenancy carries on, and that has its own answer.
              avoid=("deposit", "deposits", "selling", "sells", "sell", "sale", "sold",
                     "selling up", "on the market", "new owner", "new landlord",
                     # Damp and mould have their own answer: the letter above would tell a landlord
                     # about a boiler the person never mentioned.
                     "damp", "damp patch", "damp patches", "damp walls", "mould", "mold", "mouldy",
                     "moldy", "mildew", "condensation",
                     # "what are my rights" is in the key, and it is how every domain asks its own
                     # question: "my flight was overbooked what are my rights" was answered with a
                     # letter to a landlord about a flat the person never mentioned. The things that
                     # are not a home stand this row down, and their own answers take them.
                     "flight", "flights", "plane", "airline", "airport", "overbooked", "train",
                     "trains", "rail", "railway", "bus", "coach", "hotel", "holiday", "package",
                     "restaurant", "parcel", "delivery", "concert", "festival", "gig", "ticket",
                     "tickets", "mobile contract", "phone contract", "broadband", "insurance",
                     "sacked", "redundancy", "dismissed", "employer", "boss",
                     # the agent in the key is a letting one: a travel agent, an insurance broker
                     # and a recruiter go quiet in their own lanes
                     "travel agent", "travel agents", "holidays", "insurance broker", "recruiter",
                     "recruiters", "interview", "estate agent", "sublet", "subletting", "guest",
                     "guests")),
        # Everyone who is not being repaired asks this next, and main answered it four ways: "can i
        # withhold rent" and "can i stop paying rent" were a Citizens Advice shrug, "can i withhold
        # rent because the boiler is broken" the same shrug, "can i refuse to pay rent until its
        # fixed" the garage-labour hourly rate, "can i pay for a repair and take it off the rent" the
        # how-to-pay-for-a-big-purchase card, and "can i withhold rent until the damp is fixed" the
        # damp-treatment answer. None of them is the yes-or-no the person asked, and the wrong yes is
        # the expensive kind: stopping the rent is what gets a tenant evicted.
        entry("withhold-rent",
              (("withhold", "withholding", "withheld", "hold back", "stop paying", "stopped paying",
                "refuse to pay", "refusing to pay", "not paying", "skip the rent", "skip a payment",
                "take it off the rent", "deduct", "deduct it", "rent reduction", "reduce the rent",
                "pay less rent", "rent free", "rent strike"),
               ("rent", "landlord", "landlady", "letting agent", "tenancy", "tenant", "repair",
                "repairs", "fixed", "fix", "damp", "mould", "boiler", "heating", "hot water")),
              "Not on your own, and not by simply stopping: stopping the rent is a breach of the "
              "tenancy, and the arrears are what gets tenants evicted, whatever the state of the "
              "boiler. Keep paying and do what does work - "
              "report it in writing with dates and photos, and ask the council's environmental health "
              "team to inspect, since for a serious hazard they can order the repair. Shelter or "
              "Citizens Advice will say free whether yours is one of the rare exceptions; get that in "
              "writing before you hold back a penny.",
              # A deposit, a rent rise and a sale are their own questions, and so is a plain "how do
              # i get the landlord to repair it", which has a letter to answer it.
              avoid=("deposit", "deposits", "rent increase", "raise the rent", "raise my rent",
                     "selling", "sell", "sale", "sold", "evict", "evicted", "eviction",
                     "section 21", "section 8", "buying", "mortgage", "car", "van", "garage",
                     "hire", "student loan", "mortgage payment",
                     # A question between the people sharing a flat is not one for the landlord:
                     # "is it fair that my flatmate pays less rent because his room is smaller" was
                     # a shrug and this row would have answered it with an eviction warning.
                     "flatmate", "flatmates", "flat mate", "flat mates", "housemate", "housemates",
                     "house share", "house-share", "houseshare", "roommate", "roommates",
                     # The other direction: a lodger or a tenant who has stopped paying is the
                     # landlord's side of it, and this row only answers the tenant. "my lodger has
                     # stopped paying rent" was being told that withholding rent puts *you* in
                     # breach of the tenancy.
                     "lodger", "lodgers", "my tenant", "my tenants", "tenant", "tenants",
                     "sublet", "subtenant", "subtenant", "room to let"),
              # "how do i get the landlord to fix it" and "can my landlord put the rent up" are not
              # this question: the key word has to be about holding money back, so one of those
              # phrases has to be there.
              ask=("withhold", "withholding", "withheld", "hold back", "stop paying", "stopped paying",
                   "refuse to pay", "refusing to pay", "not paying", "skip the rent",
                   "take it off the rent", "deduct it", "rent reduction", "reduce the rent",
                   "pay less rent", "rent strike"),
              bias=1),
        # A tenant naming a fitting is asking about the tenancy, and the row that knew the word for
        # the fitting answered instead: the shower tray, the tap washer, the window frame, the lock
        # barrel, a cupboard hinge, and for the toilet the constipation card. The landlord word
        # plus one of those fittings is what makes the line this entry's, so it carries the letter
        # and stands a point above the DIY rows, which are where these lines went.
        entry("landlord-says-fix-it-yourself",
              (("landlord", "landlords", "landlady", "letting agent", "letting agents",
                "letting agency", "housing association", "my tenancy"),
               LANDLORD_JOB_FITTINGS),
              LANDLORD_REPAIR_LETTER,
              bias=3,
              # The deposit, the sale and a line about being evicted are their own questions, and a
              # landlord who will not fix it did not ask for a rent rise either.
              avoid=("deposit", "deposits", "selling", "sells", "sell", "sale", "sold", "evict",
                     "evicted", "eviction", "section 21", "notice to quit", "kick me out",
                     "throw me out", "rent increase", "raise the rent", "arrears",
                     # A hole in the glass is made safe before anybody writes a letter, tenant or
                     # not, so that card keeps the line.
                     "glass", "pane", "panes", "smashed", "shattered", "shards",
                     # the same shape `fitting-repair` uses: a window with the glass out is a hole
                     # to make safe, and the letter comes after that
                     "broken window", "window is broken", "window was broken", "broke my window",
                     "broke the window", "put through", "board up", "boarded up"),
              # A sale or a decoration question that happens to name a door is not this: the ask has
              # to be about the fault, so at least one of these words has to be in the line.
              ask=("fix", "fixed", "fixing", "repair", "repairs", "broken", "broke", "wont", "won't",
                   "will not", "refuses", "refusing", "refused", "ignores", "ignoring", "ignore",
                   "not fixing", "does nothing", "deal with", "sort out", "get it sorted")),
        entry("landlord-selling",
              (("landlord", "landlady", "letting agent"),
               ("selling", "sells", "sell", "sale", "sold", "selling up", "on the market",
                "new owner", "new landlord", "move out", "moving out", "leave", "leaving")),
              "A sale does not end your tenancy: the buyer takes the flat with you in it, your "
              "agreement carries on and your deposit stays protected. Keep paying the rent to your "
              "current landlord until they give you the new owner's details in writing, and keep the "
              "receipts. If they want you out for the sale, they still have to give you the notice "
              "your agreement and the law require - a sale is not notice - and a court order if you "
              "do not leave. Do not sign anything or hand back the keys without advice; Shelter or "
              "Citizens Advice will check the notice free.",
              # A repair, a deposit and a rent rise are their own questions. A sale that comes with
              # an eviction or a notice is this question, so those words stay out of the avoid list.
              avoid=("repair", "broken", "boiler", "damp", "mould", "deposit", "rent increase",
                     "raise the rent", "arrears", "buying", "buy", "mortgage", "house price",
                     "should i sell"),
              # A line about a landlord who wants you out is not a sale unless it says so: "leave"
              # and "move out" are in the key, so the sale word has to be present too.
              ask=("selling", "sells", "sell", "sale", "sold", "selling up", "on the market",
                   "new owner", "new landlord"),
              # A rent-arrears line also says "landlord" and "out"; a sale is the narrower subject.
              bias=2),
        # People write the machine as two words as often as one - "my dish washer smells after a
        # wash" reached nothing at all on main, while the same line with "dishwasher" answered.
        entry("dishwasher", (("dishwasher", "dishwashers", "dish washer", "dish washers"),
                             ("smell", "clean", "greasy", "filter", "cloudy", "streaks",
                              "salty", "white film", "white marks", "white spots", "film",
                              "marks")),
              "Clean the filter at the bottom, wipe round the door seal, and run an empty hot cycle "
              "with a dishwasher cleaner or a bowl of white vinegar on the top rack. The problem is "
              "usually food and grease sitting in the filter and the door seal. Check the salt and "
              "rinse aid too: running out of either makes everything come out cloudy.",
              # a pair of spectacles that came out cloudy is the glasses row's line, not the
              # machine's: "glasses" was in the key above and took it
              avoid=("my glasses", "spectacles", "specs", "frames", "lenses", "lens",
                     "prescription", "reading glasses")),

        # --- energy, heating and the boiler ------------------------------------
        entry("energy-use-up", (("energy", "electricity", "gas", "bill", "bills"),
                                 ("used more", "more than", "gone up", "doubled", "higher", "so high",
                                  "increased", "went up", "why so",
                                  # the same question opened with "why", which the size word alone
                                  # does not cover: "why is my gas bill huge" got a shrug while
                                  # "why is my electric bill so high" answered
                                  "why is my", "why has my", "why did my", "why are my",
                                  "why does my", "why is the", "why has the")),
              ("Compare the reading on the bill with the numbers on your meter first: an estimated "
               "reading, often after a supplier change, is the commonest cause of a shock bill, and "
               "sending a real reading puts it right. After that it's usually the season (heating), the "
               "immersion or a heater left on, or a fridge or freezer seal failing, so read the meter "
               "once a day for a week with everything off and see what still ticks up."),
              # the question is why the number moved; if the line asks what to do about it, main's
              # energy-bill answer is the one that helps, so the action phrasings pass
              avoid=("cut", "save", "reduce", "cheaper", "lower", "switch", "tariff", "deal",
                     "what can i do", "what do i do", "what should i do", "how can i", "how do i",
                     "spend less", "keep warm", "help",
                     "council tax", "tax", "water", "phone", "mobile", "broadband", "tv licence",
                     "licence", "rent", "insurance",
                     # a subscription bill has no meter behind it: "my sky bill has gone up" was told
                     # to read the meter once a day. The provider-price row answers it.
                     "sky", "sky tv", "sky bill", "satellite", "tv", "telly", "virgin", "virgin media",
                     "subscription", "subscriptions", "netflix", "spotify", "package",
                     "landline",
                     # "we just moved in and my girlfriend earns way more than me, how should we split
                     # the bills" is a household-income question: the `bills` key plus `more than`
                     # read it as a jump in the energy bill.
                     "split", "splitting", "split the bill", "earns", "earn", "income",
                     "salary", "wage", "wages", "50 50", "60 40", "more than me", "moved in")),
        # Reading the meter is its own job, and nothing answered it: "how do i read my gas meter" got
        # a shrug and "how do i read my electricity meter" got the physics of electric charge.
        entry("read-a-meter",
              (("gas meter", "electricity meter", "electric meter", "meter reading", "meter readings",
                "read the meter", "read my meter", "read our meter",
                # not "smart meter": main has that answer already (press A until kWh shows), and
                # the digits-a-gas-meter answer is the wrong one for a screen with a button
                "prepayment meter", "key meter", "token meter", "meter", "meters"),
               ("read", "reading", "how do i read", "how to read", "take", "taking", "submit",
                "send", "give", "which numbers", "which number", "digits", "numbers", "wrong",
                "estimated", "units", "how much")),
              "Read the black digits only and ignore anything after the decimal point or in red - those "
              "are the fractions of a unit, and a supplier only wants the whole numbers. A gas meter "
              "counts cubic metres if it says m3, or hundreds of cubic feet if it says ft3 on an older "
              "one, and the bill needs to agree which. An electricity meter may show one row of numbers, "
              "or two for day and night if you are on Economy 7: send both. Take a photo on the first of "
              "the month and send it in, because a reading you send beats an estimate.",
              # a bill that has gone up, a moving-house handover and a leaking meter are other answers
              avoid=("gone up", "so high", "higher", "expensive", "tariff", "switch", "cheaper",
                     "moving", "move out", "moving house", "landlord", "leak", "leaking", "smell",
                     "gas leak", "fault", "not working", "broken", "smart", "smart meter", "in credit",
                     "debt", "arrears", "pay", "payment", "how much do i owe", "top up", "topup"),
              ask=("read", "reading", "how", "take", "submit", "send", "which", "numbers", "digits",
                   "wrong", "units", "where"),
              # "read" and "how" are common words in this domain now that the tape and the level have
              # their own rows, and that cost this row its rarity point: "how do i read my electricity
              # meter" started reaching the smart-meter card, which is the answer for a screen with a
              # button rather than for a row of digits. The meter in the line is this row's question,
              # so it starts one point ahead.
              bias=1),
        # --- appliances and small repairs --------------------------------------
        entry("smoke-alarm-number",
              (("smoke alarm", "smoke alarms", "detector", "detectors", "fire alarm"),
               ("how many", "number", "one per", "where", "need", "needed", "fit", "fitted", "install",
                "put up", "floors", "bedroom", "bedrooms", "hallway")),
              "One on every floor, one in the hallway outside the bedrooms, and one in the room with the "
              "boiler or the open fire - the hallway one matters most, because smoke in the stairs is "
              "what cuts off the way out. Fit sealed ten-year alarms so there is no battery to "
              "remember, and check the test button on each once a month.",
              avoid=("beep", "beeping", "chirp", "chirping", "noise", "keeps going off")),

        entry("smoke-alarm-test",
              (("smoke alarm", "smoke alarms", "detector", "detectors", "fire alarm"),
               ("check", "test", "testing", "how often", "monthly", "battery", "batteries", "replace")),
              "Press the test button once a month and change the battery once a year - the easy date is "
              "when the clocks change. Vacuum the dust out of the vents twice a year, and replace the "
              "whole alarm every ten years, because the sensor ages. Fit one on every floor and one in "
              "the hallway outside the bedrooms.",
              # a chirping alarm is its own entry below; this one is the how-to-look-after-it question
              avoid=("beep", "beeping", "chirp", "chirping", "noise", "keeps going off", "smell",
                     "smoke coming", "fire started", "on fire", "burnt", "burning",
                     "how many", "number", "one per", "where should")),
        entry("smoke-alarm-beep", (("smoke alarm", "detector"), ("beep", "beeping", "chirp", "chirping",
                                                                 "noise", "keeps")),
              "A single chirp every minute or so means a low battery: change it now, don't wait. If it's "
              "a sealed ten-year alarm, replace the whole unit, and vacuum the dust out of the vents "
              "either way.",
              # An alarm that goes off while the grill is on is not a flat battery - it is a badly
              # placed sensor - and "keeps" met "smoke alarm keeps going off when i cook" here, so the
              # cooking words stand this answer down and the nuisance entry answers it instead.
              avoid=("cook", "cooking", "cooked", "toast", "toasting", "grill", "grilling",
                     "oven", "hob", "fry", "frying", "roast", "roasting", "bake", "baking",
                     "shower", "steam", "kitchen", "burning", "burnt")),
        entry("machine-takes", (TAKES_THINGS, ("how long", "take", "takes", "taking", "long", "time",
                                                "quick", "quickly")),
              _machine_takes,
              # "how long does a fridge last" is the years, and a repair is neither: this row is the
              # time the machine needs to do a job - to get cold, heat up, boil, or run a cycle.
              # "how long can i keep eggs in the fridge" reached this row on "how long" and "fridge"
              # and turned the shelf life answer down, so the keeping words stand it down before it
              # is scored at all.
              avoid=("last", "lasts", "lasting", "years", "lifespan", "life expectancy", "life span",
                     "repair", "repairing", "replace", "replacing", "broken", "not working", "fixed",
                     "engineer", "cost", "price", "electricity", "energy",
                     # the hour is the tariff row's question: "what is the cheapest time to run the
                     # washing machine" is when to put it on, not how long a cycle takes.
                     "cheapest", "cheaper", "cheap time", "best time", "what time", "off peak",
                     "off-peak", "economy 7", "tariff", "in the morning", "in the evening",
                     "during the day", "time of day",
                     "keep", "keeps", "keeping", "store", "stores", "storing", "stored", "storage",
                     "shelf life", "shelf-life", "go off", "goes off", "gone off", "still ok",
                     "still good"),
              bias=2),
        entry("fridge-not-cold",
              # "working" and a bare "not" were key words here, and a machine that has stopped working is
              # the plug-and-fuse row's question, not this one: "my fridge has stopped working" and "my
              # freezer has stopped working" were told to stand a thermometer in a glass of water. The
              # symptom this row answers has to be said - not cold, not cooling, not freezing.
              (("fridge", "freezer"), ("cold", "not cold", "not very cold", "not that cold",
                                       "wont get cold", "won't get cold", "warm", "freezing",
                                       # a seal that has gone is why a fridge stops holding its
                                       # temperature, and the paper test below is the answer
                                       "door seal", "door seals", "seal", "seals", "rubber seal",
                                                          "cool", "cooling",
                                                          "chill", "chilled", "chilling",
                                                          # "stopped cooling" outranks science.fridge,
                                                          # which keys the bare word "cool" and used
                                                          # to take the fault report as a how-it-works
                                                          # question (deck/chat-misses.jsonl).
                                                          "stopped cooling", "not cooling",
                                                          "stopped getting cold", "not getting cold")),
              "Stand a fridge thermometer in a glass of water on the middle shelf and leave it "
              "overnight: the fridge wants 3 to 5C and the freezer -18C, and the dial's numbers are not "
              "degrees. A fridge that will not reach it wants the door seals checked - close the door "
              "on a sheet of paper and see if it slides out easily - and the coils at the back dusted. "
              "Don't overfill it either, because cold air needs space to move.",
              # A fridge on the blink is this entry; "how does a fridge work" is science.fridge.
              # "how do i keep food cool without a fridge" names a fridge to say it has none, and
              # telling that person to set the fridge to 3 to 5C is no answer at all (cobalt-ivy).
              # a machine with no life in it at all is the plug fuse and the wall socket, one row
              # down from here
              avoid=("how does", "how do fridges", "how it works", "explain",
                     # the phrase, not the verb: "stopped cooling" is a key of this very row, and
                     # a bare "has stopped" stood the row down on its own symptom
                     "stopped working", "not working", "has stopped working", "have stopped working",
                     "stopped altogether", "dead",
                     "wont start", "won't start", "will not start", "not turning on", "no power",
                     "wont turn on", "won't turn on", "keeps tripping", "tripping the",
                     # a pot going into the fridge is the cooling question, not a broken fridge:
                     # "should i let the pot cool right down before it goes in the fridge" was told
                     # to stand a thermometer in a glass of water. The fridge-fault lines name the
                     # machine and no pot, so this fence costs nothing else.
                     "the pot", "a pot", "the pan", "a pan", "the stew", "a stew", "the curry",
                     "the soup", "the casserole", "leftovers", "cool it down", "let it cool",
                     "let the pot", "let the pan", "before it goes in", "before putting it",
                     "cool right down", "cool down before",
                     "without a fridge", "without a freezer", "without refrigeration", "no fridge",
                     "no freezer", "power cut", "power outage", "camping", "cool box", "coolbox",
                     "ice box", "picnic",
                     # "i have mince in the fridge and not much else" is a dinner question: the key
                     # holds "fridge" and "not", so the bare "not" of "not much else" reached the
                     # thermometer card and a person naming the one thing they had to cook was told
                     # to stand a thermometer in a glass of water. A fridge that is not cold is still
                     # this entry - none of these words is how that is said.
                     # a door that will not shut is the seal entry's, and "wont" slips to "not" here
                     "door not shut", "door not shutting", "door not close", "door not closing",
                     "door wont shut", "door wont close", "door wont stay shut", "wont stay shut",
                     "door keeps opening", "door keeps popping open", "door pops open",
                     "door swings open", "door gap",
                     # who pays for the food that went warm is the ruined-food letter in
                     # consumer.py, not the thermometer: "fridge is warm and everything inside is
                     # ruined can i claim" was told to stand a thermometer in a glass of water.
                     "claim", "claims", "refund", "money back", "compensat", "who pays", "insurance",
                     "insured", "money back",
                     "not much else", "nothing else", "nothing much", "only", "dinner", "tea",
                     "supper", "lunch", "recipe", "recipes", "what can i make", "what can i cook",
                     "what should i make", "to cook"), bias=1),
        # A cool box is how you keep food and drink cold when there is no fridge, and the entry
        # above stands these lines down on purpose ("cool box", "coolbox", "ice box" and "picnic"
        # are in its avoid): telling someone with a cool bag to stand a thermometer in the fridge
        # is no answer at all. Before this entry every one of them was a shrug -
        # "how do i keep drinks cold in a cool box" got "That's beyond what I know well" and
        # "how do i keep a cool bag cold" got "I'm not sure about that one".
        entry("cool-box-cold",
              (("cool box", "coolbox", "cooler box", "cool bag", "cooler bag", "ice box",
                "picnic bag", "picnic box", "chiller bag", "chiller box",
                "ice packs", "ice pack", "freezer blocks", "freezer block", "freezer packs",
                "freezer pack", "cool blocks", "cool pack"),
               ("cold", "cool", "keep", "keeps", "keeping", "stay", "stays", "warm", "all day",
                "picnic", "picnics", "drinks", "food", "beers", "milk", "day out", "beach", "trip",
                "car", "camping")),
              "A cool box only holds the cold you put in it. Freeze a couple of water bottles or "
              "ice packs the night before, because they do the work, and pack them around the food "
              "rather than on top. Fill the empty space with more cold drinks or a rolled-up towel: "
              "a half-empty box warms up fastest. Keep it out of the sun, out of a parked boot that "
              "gets hot, and put a towel or a folded blanket over the lid. Open it as little as you "
              "can and shut it straight after. Cold drinks and fruit keep all day like that; cooked "
              "food, milk and anything with mayonnaise is the one to throw away if it has sat warm "
              "for more than about two hours.",
              bias=1,
              # Buying one is a shopping question, and this answer would be the wrong job.
              avoid=("buy", "buying", "best", "which", "cheapest", "cheap", "price", "size",
                     "how big", "electric", "plug in", "recommend", "worth it",
                     # A cool box that smells wants washing out, not ice: "my cool box smells" is
                     # a cleaning line and the cold advice is the wrong job for it.
                     "smell", "smells", "smelly", "stinks", "mould", "mold", "dirty", "wash")),
        # How long the appliance takes to come to temperature is a clock question about the fridge,
        # not a keeping question about the food in it. "how long does a fridge take to get cold" was
        # answered with the cooked-food table ("cooked food keeps 3 to 4 days in the fridge"), and so
        # was "how long should i wait before putting food in a new fridge", because the only words
        # that reached an entry were "fridge" and "how long". The waiting words are the key here, and
        # the keeping row stands down below.
        entry("fridge-first-cold",
              (("fridge", "freezer", "fridge freezer", "refrigerator", "icebox"),
               ("get cold", "gets cold", "get colder", "getting cold", "cool down", "cools down",
                "cooling down", "get to temperature", "get down to temperature",
                "come down to temperature", "come to temperature", "reach temperature",
                "first switched on", "switched on", "switch it on", "putting food in",
                "put food in", "putting things in", "loading it", "how long before",
                "how long should i wait", "how long to wait", "wait before")),
              "A fridge comes down to temperature in about 4 hours empty and is steady at 4C after 24, "
              "so switch it on, let it run empty, then load it - a freezer wants about 24 hours to hold "
              "-18C. A thermometer in a glass of water tells you when it is ready, not the dial.",
              # A fridge that will not get cold at all is the fault card above, and a food question is
              # the keeping rows: only the clock and the waiting belong here.
              avoid=("not cold", "wont get cold", "won't get cold", "stopped getting cold",
                     "not getting cold", "not cooling", "stopped cooling", "broken"),
              # The key carries the fridge's own clock words, so "how long" is what makes the line a
              # question about time: "my new fridge is slow to get cold" is the fault card above.
              ask=("how long", "long to", "how many hours", "how much time", "how long before",
                   "how long should", "how long do i"),
              bias=1),
        entry("oven-heat-up",
              (("oven", "ovens", "fan oven", "range cooker"),
               ("heat up", "heats up", "heating up", "warm up", "warms up", "warming up",
                "preheat", "pre-heat", "preheating", "come up to temperature",
                "get to temperature", "reach temperature", "long to heat", "takes to heat")),
              "Most ovens reach 180C in 10 to 15 minutes from cold, and a fan oven is quicker than a "
              "conventional one, so a 20-minute preheat covers nearly everything. Trust an oven "
              "thermometer over the dial - they are often 10 to 20C out.",
              # the cleaning, the smell and the cooking rows all name an oven and none of them is
              # asking about the clock
              avoid=("clean", "cleaning", "self cleaning", "pyrolytic", "smell", "smells", "smoke",
                     "pizza", "chips", "roast", "bake", "baking", "cake", "air fryer",
                     # "my oven is not heating up" is the element card: a fault is not a clock
                     "not heating", "not heating up", "isnt heating", "isn't heating", "not working",
                     "wont heat", "won't heat", "stopped heating", "broken", "fault", "fuse"),
              # "how do i preheat a fan oven" is the fan-oven dial answer, not the minutes: only a
              # line that asks about time is this row's.
              ask=("how long", "long to", "how many minutes", "how much time", "how long before"),
              bias=1),
        # The job of cleaning the fridge. A smell in it is a separate entry (fridge-smell), so the
        # keys here are the cleaning words only.
        # Water in the bottom of a fridge is the drain hole at the back, and it was answered with a
        # chat echo. The freezer case shares the drain, so one row covers both.
        entry("fridge-water-inside",
              (("fridge", "freezer", "refrigerator", "fridge freezer", "salad drawer", "crisper"),
               ("water", "wet", "puddle", "pools", "pooling", "collecting", "collects", "ice", "icy",
                "dripping", "drips", "leaking", "leak", "drawer", "bottom", "inside")),
              "Water in the bottom of a fridge is nearly always the drain hole at the back: it clogs "
              "with bits of food, so push a pipe cleaner or a piece of stiff wire down it and flush "
              "warm water through. Ice on the back wall means the fridge is running too cold, so turn "
              "the dial up a notch and let it defrost. If the water keeps coming back, check the door "
              "seal by closing the door on a sheet of paper - if it slides out easily, the seal is the "
              "fault.",
              bias=1,
              avoid=("buy", "best", "which", "cheapest", "size", "smells", "smell", "not cold",
                     # "clean" is `fridge-clean`'s question: the drain keys the drawer and the
                     # bottom of the fridge, so "how do i clean the inside of the fridge" was a
                     # blocked drain hole
                     "clean", "cleaning", "cleaned", "clean out", "wipe", "wipe out", "scrub",
                     "shelves", "shelf", "racks", "spills",
                     "not freezing", "noisy", "noise", "defrost", "frost free", "on the floor",
                     "outside", "washing machine", "dishwasher", "boiler", "kettle", "toilet",
                     "hot water bottle", "ice cubes", "ice tray", "drinking",
                     # "i keep water in the fridge" says where the water lives, not that the fridge
                     # is leaking: with the kettle words above it was still sent to the drain hole,
                     # so the row stands down for the drinking water people keep.
                     "keep water", "keeps water", "keep a jug", "jug", "bottle", "bottles",
                     "water bottle", "water bottles", "keep drinks", "keep juice", "cans",
                     # a freezer that ices up is the defrost question, even when the line says ice
                     # and inside: "a layer of ice inside, is that costing me money" is that one
                     "layer of ice", "ices up", "iced up", "ice builds up", "ice build up",
                     "ice build-up",
                     # the same goes for a freezer filling up: "my freezer has ice on the walls" and
                     # "my freezer is full of ice" were sent to the fridge's drain hole, and the
                     # defrost row answers them
                     "ice on the walls", "walls of ice", "full of ice", "lots of ice",
                     "so much ice", "thick ice", "ice everywhere", "ice in the freezer",
                     "freezer has ice", "freezer with ice", "build up of ice",
                     "cost", "costs", "costing", "money", "bill", "bills",
                     "energy", "efficient", "efficiency")),
        # An oven door that is stiff or will not shut was met with a chat echo, and the front-door
        # row used to answer it with a lock and a plane.
        entry("oven-door",
              (("oven", "cooker", "range cooker", "oven door"),
               ("door", "hinge", "hinges", "stiff", "sticking", "sticks", "hard to shut",
                "hard to close", "wont shut", "won't shut", "wont close", "won't close", "not closing",
                "drops", "dropped", "spring", "loose", "rub", "rubbing", "squeak", "squeaks")),
              "An oven door that is stiff or will not shut is nearly always the hinge: open it and "
              "look at the two arms at the bottom, because a bent arm or a hinge that has dropped "
              "makes the door rub on the frame. Check nothing inside has slipped forward first - a "
              "shelf or a tray stops the door a centimetre short - and wipe the burnt grease off the "
              "hinge area. If it still will not sit shut, hinges are a cheap part for most makes: take "
              "the model number off the sticker and order a pair.",
              bias=1,
              # a tenant with a landlord who will not act wants the letter, not the hinges: the
              # tenancy phrasings stand this card down, as they do for `fitting-repair`
              avoid=("clean", "cleaning", "glass", "smell", "burning", "not heating", "temperature",
                     # a hand closed in the oven door is an injury, not a hinge that has dropped:
                     # "i shut my hand in the oven door" was the hinge card
                     "finger", "fingers", "thumb", "my hand", "hand in", "trapped", "caught",
                     "slammed", "burned", "burnt", "scalded",
                     "lock", "childlock", "child lock", "fan", "element", "pizza", "bread", "cake",
                     "how long", "how hot", "what temperature", "shelf position",
                     "landlord", "landlords", "landlady", "letting agent", "letting agency",
                     "my tenancy", "wont fix", "won't fix", "refuses to fix", "refusing to fix",
                     # a door that sticks is not a door with grease on it: "how do i get grease
                     # off the oven door" was the hinge answer, and the glass row owns the grease.
                     "grease", "greasy", "burnt", "burnt on", "food", "spill", "spilled",
                     "splatter", "splatters", "stain", "stains", "smear", "smears",
                     # A loaf that goes up and then drops in the oven has nothing to do with the
                     # door: `drops` is in the key above, and this card answered a bread fault with
                     # a hinge ("it rises then it drops in the oven"). Anything said about the bake
                     # itself stands this row down - the baking rows in cooking.py own those lines,
                     # and a door that drops is still here because none of these words is in it.
                     "rise", "rises", "risen", "rising", "prove", "proves", "proved", "proving",
                     "proof", "proofed", "dough", "sourdough", "loaf", "loaves", "yeast", "sponge",
                     "batter", "souffle", "soufflé", "pastry", "croissant", "meringue", "bake",
                     "bakes", "baked", "baking", "recipe")),
        entry("fridge-clean", (("fridge", "freezer"), ("clean", "cleaning", "cleaned", "wash", "wipe",
                                                      "shelves", "shelf", "scrub", "freshen", "hygiene")),
              "Empty it into a cool bag first, then wipe every shelf, drawer and the door seals with hot "
              "soapy water and dry them. Clear the drain hole at the back with a cotton bud and warm "
              "water, and leave a bowl of bicarbonate of soda on a shelf between cleans: it absorbs "
              "smells instead of covering them. Once or twice a year is enough if nothing has spilled."),
        # A door that will not shut is the seal, and it is the one fridge fault you can test in ten
        # seconds and often fix without a call-out. On main "the seal on my fridge door has gone" and
        # "the rubber on my freezer door is split" were a greeting, and "how do i know if my fridge
        # seal is bad" was a punt: the not-cold entry wanted a temperature complaint, so nothing
        # answered the seal itself.
        entry("fridge-seal",
              # the fridge or the freezer has to be named: "door" alone took the washing machine's
              # seal, the oven's and the car's, which are other entries and other answers
              # A door that will not shut is the same fault and the same ten-second test, and it was
              # answering as three other things: "the fridge door wont shut" got the thermometer card
              # ("wont" is one letter from "not", which keys the not-cold entry, so the slip reader read
              # a door that will not close as a fridge that is not cold), "my fridge door keeps popping
              # open" got the cooked-food keeping card, and "the freezer door wont stay shut" got the
              # power-cut card. The shapes of a door that does not shut or does not stay shut are key
              # words here, so the seal test and the hinge are what answers them.
              (("seal", "seals", "rubber", "gasket", "magnet", "magnetic strip",
                "door not shut", "door not shutting", "door not close", "door not closing",
                "door not shut properly", "door not closing properly", "door doesnt shut",
                "door doesnt close", "door does not shut", "door does not close",
                "door wont shut", "door wont close", "door wont stay shut", "door wont stay closed",
                "door keeps opening", "door keeps popping open", "door pops open", "door swings open",
                "door swings back open", "wont stay shut", "door gap", "gap round the door"),
               ("fridge", "freezer", "refrigerator")),
              "Close the door on a sheet of paper and pull it out: it should drag, and a note that "
              "slides out easily at that spot is a gap. Wipe the seal with hot soapy water and dry it, "
              "because a sticky or crumpled seal often shuts fine once it is clean, then check the door "
              "hinge has not dropped. A split or hardened seal is a part: the model number is on a "
              "sticker inside the fridge, and a new one is usually £20 to £40 and pushes into the "
              "channel by hand.",
              # the fridge without an adjective is not this: cold, cleaning and smell have their own
              # answers, and a fridge door that will not close is in house-doors, not here
              avoid=("clean", "cleaning", "smell", "smells", "smelly", "stink", "ice", "frost",
                     "defrost", "freezing", "not cold", "warm", "noise", "humming", "rattling",
                     "slam", "hinge"),
              # bias=2: a door that will not stay shut was reaching the power-cut card and the
              # cooked-food card on a tie, and both name a door without being about one
              bias=2),

        # appliance noise: the machine is working, it is just audible. A noise word alone is not a
        # fault report, so these sit apart from the smell and not-cold entries.
        entry("fridge-noise", (("fridge", "freezer", "refrigerator"),
                               ("hum", "hums", "humming", "buzz", "buzzing",
                                "rattl", "vibrat", "clunk", "gurgl", "ticking",
                                "clicking", "knock") + NOISE_WORDS),
              "The steady hum is the compressor, which switches on and off to hold the temperature: "
              "it is normal, and it gets louder when the room is warm or the door has just been shut "
              "on warm food. A rattle or a buzz is usually the fridge not sitting level, so wind the "
              "front feet down until it stands firm, and check nothing is touching the back. A clunk "
              "every few minutes, or a fridge that hums but never gets cold, is gas or the compressor "
              "and needs an engineer.",
              bias=1,
              avoid=("smell", "smells", "smelly", "stink", "stinks", "odour", "clean", "ice",
                     "frost", "defrost", "freezing", "food", "chicken")),
        # A machine that hums is working, it is just audible, and the banging answer above is about a
        # load out of balance: "why does my washing machine hum" got the tinnitus explanation, which
        # is advice for an ear, and then the spin-noise answer, which tells you to undo the tangle.
        entry("appliance-hum", (("washing machine", "washer", "dishwasher"),
                                ("hum", "hums", "humming", "whirr", "whirring", "whine", "whining",
                                 "buzz", "buzzing")),
              "A steady hum is the motor or the pump doing its job, and every machine has one. A hum "
              "that is new or louder is usually the machine standing uneven, something loose touching "
              "the case, or a filter or drain pump half blocked: level the feet, take the filter out "
              "and clean it, and check the drum or spray arm turns freely with the power off. A whine "
              "that rises with the speed is a bearing, which is a repair rather than a service.",
              bias=1,
              # the appliance's own fault is the better answer when the line names one: wet dishes,
              # a rattle, a squeal and a boiler all have an entry that knows more than this one
              avoid=("tinnitus", "my ears", "in my ears", "ringing", "hearing", "smell", "smells",
                     "buy", "replace", "best", "worst", "wet", "dirty", "not draining", "wont drain",
                     "won't drain", "squeal", "squeals", "squealing", "rattle", "rattling", "bang",
                     "bangs", "banging", "shaking", "wont spin", "won't spin", "not spinning",
                     "boiler", "radiator", "puddle", "leak", "leaking")),

        entry("washer-noise", (("washing machine", "washer", "washer dryer", "spin"),
                               ("shake", "shakes", "shaking", "bang", "bangs", "banging",
                                "rattl", "vibrat", "walk", "walks", "jump",
                                "jumps", "thump", "thumping", "screech", "squeal",
                                # the stems above are not prefixes the lookup matches, so
                                # "my washing machine rattles on the spin" had no answer at all
                                "rattle", "rattles", "rattling", "vibrate", "vibrates")
                               + NOISE_WORDS),
              "A machine that bangs or walks across the floor is almost always an uneven load: stop "
              "it, undo the tangle, and put a couple of towels in with a single heavy thing like a "
              "duvet. If it does it on every spin, take the transport bolts out of the back (they stay "
              "in on a new machine and must come out), level the feet so it cannot rock, and check it "
              "is not touching a cupboard. A screech or a burning smell means the drum bearings or the "
              "belt, which is a repair.",
              # A named fault sound belongs to the row below, which knows what that sound is: the
              # load answer does not touch a grind, a squeal or a rattle, and given the words as
              # well as this row it took the turn ("my washing machine is scraping" here, the
              # dismantled-drum answer there). "noisy", "loud" and "banging" keep this row, which
              # is the answer to them.
              avoid=("smell", "smells", "smelly", "musty", "drain", "drains", "empty", "water",
                     "filter", "buy", "replace", "worst", "best", "drum",
                     "grind", "grinds", "grinding", "scrap", "scrapes", "scraping",
                     "rumble", "rumbles", "rumbling", "roar", "roaring",
                     "screech", "screeching", "squeal", "squeals", "squealing",
                     "squeak", "squeaks", "squeaking", "rattle", "rattles", "rattling",
                     "clunk", "clunks", "clunking", "shriek", "shrieking")),

        # A washing machine had one answer for every sound it made - the load and the feet - and it
        # was a good answer to a bang and a wrong one to a grind: "my washing machine is making a
        # grinding noise" was told to untangle the washing, when a grind is something metal in the
        # drum or a bearing on its way out. "my washing machine is grinding" and "my washing machine
        # is scraping" matched nothing at all in the row above, and the scrape reached the tip.
        #
        # The sounds a machine makes when it is not the load are here, and this row is only ever
        # these: a bang, a wobble or a plain "noisy" keeps the row above, which answers the load.
        entry("washer-sound",
              (("washing machine", "washer", "washer dryer", "washer-dryer", "drum", "spin"),
               ("grind", "grinds", "grinding", "scrap", "scrapes", "scraping", "rumble", "rumbles",
                "rumbling", "roar", "roaring",
                "squeak", "squeaks", "squeaking", "squeal", "squeals", "squealing", "screech",
                "screeching", "shriek", "shrieking",
                "rattle", "rattles", "rattling", "clunk", "clunks", "clunking")),
              _washer_sound_fault,
              bias=1,
              # a dryer's drum is not a washer's, and the answer here would send someone to a kick
              # plate their machine has not got
              guard=_a_dryer_is_not_a_washer),

        # A fan oven keeps its fan going after the dial is off, and a fan that never stops sounds
        # like a fault. Left alone the line reached the baking advice about dials and gas marks,
        # which tells someone with a broken fan to drop the temperature 20C.
        entry("oven-fan-runs-on", (("oven", "cooker", "fan oven"),
                                   ("fan", "fans")),
              "A fan oven usually runs its cooling fan on after you switch off, sometimes for ten or "
              "twenty minutes, to pull the heat out of the casing: that is normal and it stops by "
              "itself. If it never stops, or starts again while the oven is cold, the thermostat or the "
              "fan switch has failed and it needs an engineer, and it is worth switching off at the "
              "wall until then.",
              bias=4,
              ask=("never", "stops", "stop", "keeps", "keeping", "runs", "running", "all the time",
                   "stays", "wont", "won't", "cold"),
              # "timing" is a loose form of "time", and it blocked "runs all the time"
              avoid=("clean", "cleaning", "gas mark", "bake", "cake", "roast", "bread", "temperature",
                     "dial", "degrees", "how long", "how hot")),

        # The glass in the door is its own job: the paste goes on the glass, not the cavity, and the
        # burnt specks come off with a blade held flat. "how do i clean the oven glass" had the
        # inside-the-oven answer and "my oven glass is dirty" had nothing.
        entry("oven-glass",
              (("oven glass", "oven door glass", "glass door", "oven window", "oven door",
                "the glass on the oven", "inside of the oven door", "door of the oven"),
               ("clean", "cleaning", "cleaned", "greasy", "grease", "dirty", "smear", "smears",
                "streak", "streaks", "marks", "scrub", "wipe", "wash", "filthy", "stained")),
              "Spread a paste of bicarbonate of soda and water on the glass, leave it twenty minutes "
              "and wipe it off with a damp cloth; burnt specks lift with a plastic scraper or a razor "
              "blade held almost flat to the glass. Keep caustic oven cleaner off the rubber seal, and "
              "wipe the inside of the door too, because most of the brown film sits between the panes.",
              # a burnt hand on the oven shelf is the safety module's line, never a cleaning one
              avoid=("hand", "hands", "finger", "fingers", "thumb", "arm", "arms", "wrist", "skin",
                     "scald", "scalded", "blister", "butter", "myself", "shelf", "shelves", "rack",
                     "racks", "stiff", "wont close", "won't close", "wont shut", "hinge", "smoke",
                     "smells", "smoking")),
        # "how do i clean the grill" got the barbecue answer: a grill in a cooker is the oven's, and
        # it is a different job from coals and a wire brush. Anything that says barbecue keeps it.
        entry("oven-grill",
              (("oven grill", "the grill", "grill pan", "grill tray", "grill plate", "grills",
                "grill"),
               ("clean", "cleaning", "cleaned", "grease", "greasy", "scrub", "soak", "wash",
                "burnt", "stuck", "filthy", "dirty")),
              "Soak the grill pan and its rack in hot water with washing-up liquid and a couple of "
              "tablespoons of bicarbonate of soda, then lift the burnt bits with a nylon scourer. "
              "The element above it is not a thing to scrub: switch it off, let it cool, and wipe it "
              "with a damp cloth, and leave the self-clean lever for the whole oven.",
              # a barbecue out in the garden is the barbecue row's question
              avoid=("barbecue", "barbecues", "barbeque", "bbq", "bbqs", "barbie", "charcoal",
                     "coals", "garden", "outdoor", "outside", "steak", "steaks", "burger",
                     "burgers", "sausage", "sausages", "kebab", "halloumi", "how long", "recipe",
                     "marinade", "temperature", "cook", "cooking", "which", "buy", "buying",
                     "dishwasher filter", "oven racks", "oven shelves"),
              ask=("clean", "cleaning", "cleaned", "grease", "greasy", "scrub", "soak", "wash",
                   "burnt", "stuck", "filthy", "dirty"),
              bias=1),
    ]
