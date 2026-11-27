"""Rows 9 of 10 of `home_craft.entries()`: `fence-post-depth` .. `furniture-upstairs`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    A_AGE_OWNED,
    BOILER_DIY,
    _a_deposit_coming_back,
    _an_ask_about_servicing_my_own,
    _hair_dryer,
    _not_a_washer_of_another_kind,
    the_bin_is_on_a_machine,
)


def rows():
    from ..knowledge.home import (
        NOT_A_FENCE_JOB, _DIY_AVOID, _not_a_size_of_a_home, _diy, _dryer_heat,
        _furniture_upstairs, _a_person_not_a_hob, _hob_heat, _iron_fault, _washer_price, entry
    )
    from ..knowledge.lookup import RING_AS_A_CALL
    return [
        # "how deep should fence posts go" and "ive buried the posts about two foot down, is that deep
        # enough" reached nothing at all: the repair, treating and height rows each answer a fence
        # line, and none of them says how deep the hole is. The line usually has no fault word in it,
        # because nothing has gone wrong yet, so the depth ask is the row's own key.
        entry("fence-post-depth",
              (("how deep", "deep enough", "deep should", "deep do", "deep to", "deep for",
                "depth", "how far down", "how far in", "foot down", "feet down", "two foot",
                "2 foot", "two feet", "2 feet", "three foot", "3 foot", "three feet",
                "buried", "in the ground", "into the ground", "how much of"),
               ("fence post", "fence posts", "gate post", "gatepost", "pergola post",
                "deck post", "deck posts", "posts", "post", "fence", "fencing", "pergola")),
              "About a third of the post in the ground: 600mm (two foot) under a standard 1.8m panel, "
              "and 750 to 900mm on an exposed, windy corner or in sandy soil. Two foot is enough if "
              "the hole is about 250 to 300mm across and set in Postcrete or a 3:1 ballast and cement "
              "mix, with the concrete sloping away from the post so water runs off - check it plumb "
              "before the mix goes off, because a post only 300 to 400mm down leans within a winter.",
              # the depth words are the ask as well as the subject: a line about a post with no depth
              # in it belongs to the repair, treating or height row
              ask=("how deep", "deep enough", "deep should", "deep do", "deep to", "deep for",
                   "depth", "how far down", "how far in", "foot down", "feet down", "buried",
                   "in the ground", "into the ground", "how much of"),
              bias=1,
              avoid=NOT_A_FENCE_JOB + (
                     "post office", "post a letter", "parcel", "delivery", "mail",
                     "letter", "blog", "job", "position", "apply", "applying", "instagram",
                     "facebook", "comment", "review", "how tall", "how high", "planning",
                     "max height", "boundary", "who owns", "whose", "who pays", "my neighbour",
                     "my neighbor", "cost", "costs", "price", "prices", "quote", "cheapest",
                     "treat", "treating", "stain", "staining", "paint", "painting",
                     "preserver", "creosote", "blew down", "blown down", "fell down",
                     "repair", "replace", "rotten", "rotted", "wobbly", "loose", "leaning",
                     "hanging", "plant", "plants", "bulb", "bulbs", "seed", "seeds",
                     "grave", "graves", "coffin", "ashes",
                     # old posts taken to the tip are rubbish, not a hole to get right
                     "the tip", "to the tip", "tip run", "rubbish", "skip", "landfill", "dispose",
                     "disposing", "instead of", "dumping", "get rid")),
        # The other half of a new fence: the depth row above answers "how deep", and the lines about
        # putting the post in the hole at all were reaching the repair answers. "how do i set a fence
        # post straight" and "should i put gravel in the bottom of a fence post hole" were both told
        # that "a panel that came out in the wind is usually a post that has moved", and "how much
        # postcrete do i need per fence post" was quoted the price of a fence.
        entry("fence-post-set",
              (("set a fence post", "set the post", "set a post", "set a new post",
                "set", "setting", "put up", "putting up", "install", "installing", "erect",
                "erecting", "fit", "fitting", "concrete", "concreting", "concreted",
                "concrete a fence post", "concrete it in", "concrete the post",
                "postcrete", "cement", "dig", "digging", "hole", "gravel", "ballast",
                "put gravel", "gravel in the bottom", "gravel in the hole", "bottom of the hole",
                "plumb", "straight", "level", "brace", "bracing", "how many bags",
                "how much postcrete", "how much concrete", "help it stand"),
               ("fence post", "fence posts", "gate post", "gatepost", "deck post", "posts",
                "post", "fence", "fencing", "panel", "panels")),
              "Dig the hole 250 to 300mm across and two foot (600mm) deep, stand the post on about "
              "50mm of gravel so the cut end never sits in water, and get it plumb on two faces with "
              "a spirit level before anything goes in. One 20kg bag of Postcrete does one post: pour "
              "it dry around the post, water it as the bag says, brace the post and leave it a day "
              "before a panel goes on. A 100mm square or 75mm round post is right for a 1.8m panel; "
              "in soft soil, or on a windy corner, go deeper rather than wider.",
              bias=1,
              avoid=NOT_A_FENCE_JOB + (
                     "post office", "post a letter", "parcel", "delivery", "mail", "letter",
                     "blog", "job", "position", "apply", "applying", "instagram", "facebook",
                     # "the neighbour put up a fence and i dont like it" is a boundary row's line
                     "neighbour", "neighbor", "next door",
                     # a lamp post, a sign post and a post box are other things with "post" in them:
                     # "how do i fit a lamp post in the garden" was a hedge on main and got the fence
                     # post's hole here until these were named
                     "lamp post", "lamppost", "lamp", "post box", "postbox", "goal post",
                     "goalpost", "sign post", "signpost", "postcard", "postcard", "postcode",
                     "post code", "carrier", "courier",
                     "comment", "review", "how tall", "how high", "planning", "boundary",
                     # the limit said as a measurement is the height row's: "can i put up a fence 2
                     # metres high" is not a hole to dig
                     "metres high", "metre high", "metres tall", "metre tall", "feet high",
                     "foot high", "2 metres", "2m high", "six foot", "height limit",
                     "who owns", "whose", "who pays", "my neighbour", "my neighbor", "cost",
                     "costs", "price", "prices", "quote", "cheapest", "treat", "treating",
                     "stain", "staining", "paint", "painting", "preserver", "creosote",
                     "blew down", "blown down", "fell down", "repair", "replace", "rotten",
                     "rotted", "rot", "rotting", "wobbly", "loose", "leaning", "sagging",
                     "plant", "plants", "bulb", "bulbs", "ashes",
                     "the tip", "to the tip", "rubbish", "skip", "instead of", "get rid",
                     "how far apart", "spacing", "spaced", "centres", "centers",
                     "how deep", "depth", "deep enough", "foot down", "feet down")),
        # How far apart, which the hole and the depth say nothing about: the answer is the centres.
        entry("fence-post-spacing",
              (("how far apart", "how far between", "spacing", "spaced", "centres", "centers",
                "distance between", "how many posts", "how many panels", "how wide"),
               ("fence post", "fence posts", "posts", "post", "fence", "fencing", "panel",
                "panels", "gate post", "gate")),
              "Fence posts go 1.8m apart, centre to centre, for a standard 1.8m (6ft) panel, and 2.4m "
              "for a 2.4m panel - a gravel board and a panel are sold to that width, so measure the "
              "panel before you dig. On a slope, keep the tops level and let the bottom of each panel "
              "follow the ground, stepped one post at a time rather than raked.",
              bias=1,
              avoid=NOT_A_FENCE_JOB + (
                     "post office", "post a letter", "parcel", "delivery", "mail", "letter",
                     "lamp post", "lamppost", "lamp", "post box", "postbox", "goal post",
                     "goalpost", "sign post", "signpost", "postcard", "postcode", "post code",
                     "blog", "job", "position", "apply", "cost", "costs", "price", "quote",
                     "treat", "treating", "stain", "paint", "painting", "how tall", "how high",
                     "planning", "boundary", "who owns", "whose", "how deep", "depth",
                     "deep enough", "how far down", "buried", "in the ground", "repair",
                     "replace", "rotten", "rotted", "wobbly", "loose", "leaning")),
        # "how thick should a fence post be" and "what size fence post do i need" both came back
        # with the panel-repair answer, because the only thing the fence rows had for a post was
        # something going wrong with one. The size is a fact about a post, not about a repair.
        entry("fence-post-size",
              (("how thick", "how big", "what size", "which size", "what width", "how wide",
                "whats the best fence post", "best fence post", "best post", "what post",
                "which post", "what sort of post", "what kind of post", "what timber",
                "4 inch", "four inch", "3 inch", "three inch", "100mm", "75mm", "125mm",
                "square or round", "round or square", "concrete or wooden post"),
               ("fence post", "fence posts", "gate post", "gatepost", "deck post", "posts",
                "post", "fence", "fencing", "panel", "panels", "gate")),
              "A 100mm (4 inch) square post carries a 1.8m panel, and 75mm round is enough for a "
              "light closeboard fence; a gate wants a 125 to 150mm post of its own, not a panel post "
              "with a gate hung on it. Buy posts marked for ground contact (UC4) rather than plain "
              "treated timber, because a post rots at the soil line, and on an exposed corner a "
              "concrete post outlasts wood.",
              bias=1,
              avoid=NOT_A_FENCE_JOB + (
                     "post office", "post a letter", "parcel", "delivery", "mail", "letter",
                     "lamp post", "lamppost", "lamp", "post box", "postbox", "goal post",
                     "goalpost", "sign post", "signpost", "postcard", "postcode", "post code",
                     "blog", "job", "position", "apply", "applying", "cost", "costs", "price",
                     "prices", "quote", "how many do i need", "how far apart", "spacing",
                     "how deep", "depth", "deep enough", "how far down", "buried",
                     "in the ground", "dig", "digging", "hole", "concrete in", "postcrete",
                     "repair", "replace", "fix", "rotten", "rotted", "wobbly", "loose",
                     "leaning", "blew", "blown", "fell", "fallen", "treat", "treating",
                     "stain", "paint", "painting", "how tall", "how high", "planning",
                     "boundary", "who owns", "whose", "my neighbour", "my neighbor")),
        # "how do i paint a fence" was turned down honestly. The answer is a day's work with one
        # method, and the fence it is asked about is usually the one the row above has just mended.
        entry("fence-paint",
              (("fence", "fences", "fence panels", "shed", "garden gate"),
               ("paint", "painting", "paint it", "stain", "staining", "treat", "treating",
                "treatment", "creosote", "preserver", "preservative", "protect", "weatherproof")),
              "Clean it and let it dry: paint on a dirty or damp fence flakes within a year. Brush or "
              "spray a water-based fence stain rather than a film-forming paint, two coats on a dry day "
              "above 10C, keeping the bottom of the panel clear of the soil. A shed wants an oil or "
              "wood preserver, not a fence stain.",
              avoid=("neighbour", "neighbor", "boundary", "cost", "how much", "blew down", "rotted",
                     "fallen", "leaning", "replace")),
        entry("fence-windproof",
              (("stop my fence blowing down", "fence keeps blowing down", "fence blowing down again",
                "blown down every", "windproof", "wind proof", "keep the fence up"),
               ("fence", "fences", "garden", "wind", "storm", "gale", "again", "strong")),
              "A solid fence is a sail, so the wind pulls on the posts rather than passing through: "
              "slatted panels, or a gap under the gravel board, let it through. Set the posts 600mm "
              "into the ground in concrete, keep the panel out of the soil, and brace the end posts. A "
              "trellis strip along the top takes most of the load off a windy corner."),
        # "my patio slabs are loose" had the "I'm listening" line: a rocking slab is a bedding
        # question with a method, and it is the same answer for paving, setts and a step.
        entry("patio-slab-loose",
              (("patio slab", "patio slabs", "paving slab", "paving slabs", "slab", "slabs",
                "paving", "patio", "paving stones"),
               ("loose", "wobble", "wobbles", "wobbly", "rocking", "rocks", "sunken", "sunk",
                "cracked", "moved", "lift", "relay", "re-lay", "dip", "uneven")),
              "Lift the slab, scrape off the old bedding and re-bed it on 30 to 40mm of 5:1 sharp sand "
              "and cement, tapping it level with its neighbours with a rubber mallet and checking with "
              "a straight edge. A slab that rocks after rain is usually a hollow bed or ants. Point the "
              "joints with dry sand and cement, not soil, and leave it a day."),
        # The mix for a paving bed had no row of its own: "how much sand and cement do i need to lay
        # a patio" was "I don't know enough to answer that honestly", "what mix do i use to lay patio
        # slabs" was the same shrug, "how much mortar do i need for a patio" was the gravel volume
        # sum (a bag of sand read as a tonne of gravel) and "how much sand and cement per square
        # metre of paving" was the area formula. A bagged mix is not a volume of fill, so the
        # quantities are per square metre of bed here and per brick and block next door: same sum,
        # different sums to know.
        entry("bricklaying-mortar",
              (("mortar", "mortar mix", "sand and cement", "building sand and cement",
                "cement", "cement mix", "cement and sand", "what mix", "what ratio", "mix ratio",
                "mix do i use", "mix should i use", "how much sand", "how much cement",
                "how many bags of sand", "how many bags of cement", "bags of sand",
                "bags of cement", "5 to 1", "5:1", "4 to 1", "4:1"),
               ("brick", "bricks", "bricklaying", "brickwork", "block", "blocks", "blockwork",
                "breeze block", "breezeblock", "cinder block", "wall", "walls", "garden wall",
                "render", "rendering", "pointing", "repointing", "re-point", "point the",
                "screed", "floor", "slab of concrete", "concrete base", "footing", "footings")),
              "Bricklaying mortar is 5:1 building sand to cement, or 4:1 for a wall that takes the "
              "weather, mixed soft and buttery rather than wet. A 25kg bag of cement with five bags of "
              "building sand lays roughly 150 bricks or 40 blocks, so measure the wall first - a 10m "
              "single-skin wall 1m high is about 600 bricks. Pointing and rendering are both a 4:1 "
              "mix, and a footing or a small concrete base is 6 parts ballast to 1 of cement.",
              avoid=("cost", "costs", "price", "prices", "cheap", "cheapest", "expensive",
                     "how much is", "how much does", "how much would", "quote", "quotes",
                     "which", "what type", "what sort", "best type", "what colour", "what color",
                     "how many bricks", "how many blocks", "many square metres",
                     "how do i lay", "how to lay", "clean", "cleaner", "stain", "stains",
                     "algae", "moss", "seal", "sealer", "paint", "render crack", "cracked",
                     "patio", "paving", "paving slab", "paving slabs", "flag", "flags",
                     "flagstone", "flagstones", "setts", "joints", "paving joints",
                     "mixer", "hire", "borrow", "wheelbarrow", "shovel", "board",
                     "how long", "how deep", "how thick", "depth", "thickness", "cure", "dry",
                     "damp", "damp proof", "insulation", "cavity", "lintel", "planning",
                     # as above: a set mix that has to come off is a cleaning row's line
                     "get off", "getting off", "off a", "off the", "off my", "off bricks",
                     "off the wall", "off walls", "remove", "removing", "removal", "scrub",
                     "scrubbing", "pressure washer", "jet wash", "stubborn"),
              bias=1),
        # Blocks are not the patio's bed: a block-paved drive or patio goes down on sharp sand
        # alone, compacted, with kiln-dried sand brushed into the joints - no cement in the bed at
        # all. On main "how much mortar for 20 square metres of block paving" was the patio's
        # price card and "how much sharp sand and cement for a block paved drive" was the slab
        # bed, which is the wrong mix for the job by 5 parts sand to 1.
        entry("block-paving-bed",
              (("block paving", "block paved", "block paver", "block pavers", "paving blocks",
                "driveway blocks", "setts", "block paving drive", "paved drive", "paving the drive"),
               ("sand", "cement", "mortar", "mix", "much", "need", "how much", "how many",
                "bed", "bedding", "joint", "joints", "brush in", "kiln dried", "kiln-dried",
                "how deep", "depth", "wacker", "compact")),
              "Blocks are not bedded on sand and cement: they go down on 30 to 40mm of sharp sand "
              "alone, compacted with a wacker plate, and the joints are brushed full of kiln-dried "
              "sand afterwards, so there is no cement to measure at all. For 20 square metres "
              "reckon on about a tonne of sharp sand for the bed and two or three 25kg bags of "
              "kiln-dried sand for the joints, plus an edge restraint on every open side, which is "
              "the part that stops the blocks spreading.",
              # a price, the laying method, a slab, a cleaning job and a wall are other rows
              avoid=("cost", "costs", "price", "prices", "cheap", "cheapest", "expensive",
                     "how much is", "how much does", "how much would", "quote", "quotes",
                     "which", "what type", "what sort", "best type", "what colour", "what color",
                     "how do i lay", "how to lay", "laying", "lay the blocks", "do i lay",
                     "clean", "cleaner", "stain", "stains", "algae", "moss", "weeds", "weed",
                     "seal", "sealer", "slippery", "oil", "paint", "get off", "getting off",
                     "off a", "off the", "off my", "remove", "removing", "removal", "scrub",
                     "patio slab", "paving slab", "paving slabs", "flag", "flags", "flagstone",
                     "wall", "walls", "brick", "bricks", "brickwork", "render", "rendering",
                     "screed", "floor", "concrete base", "footing", "footings", "mixer", "hire"),
              bias=3),
        entry("too-much-rubbish",
              (("bin", "bins", "rubbish", "trash", "garbage", "wheelie", "wheelie bin", "bin bag",
                "bin bags", "recycling", "waste"),
               ("always", "overflowing", "overfull", "too much", "every week", "each week", "full",
                "loads", "so much", "less", "reduce", "cut down", "keep filling")),
              "Most of it is air and packaging: flatten cartons, crush cans and squash bottles with the "
              "lid off, and the same bag holds twice as much. Put a smaller bin by the counter and take "
              "it out every night rather than waiting for the big one to fill, and keep a caddy beside "
              "it for peelings, which is often a third of the weight. Then buy the biggest pack you will "
              "actually use, loose veg instead of trays, and one refill bottle instead of a new one. If "
              "the wheelie bin is full by day five, half of what is in it belongs in the recycling.",
              avoid=("smell", "smells", "smelly", "stink", "stinks", "bin day", "collection",
                     "collected", "council", "where do i take", "tip",
                     "dump", "neighbour", "neighbor", "next door", "compost", "garden", "food caddy",
                     "seagull", "fox", "rat", "mouse", "mice", "broke", "broken", "lid", "lock",
                     "when is", "what day",
                     # "waste" is this row's noun for rubbish, but it is also a verb, and the
                     # thing it is done to decides who answers: "i waste so much money every
                     # month" and "i am wasting so much gas" were both the flatten-the-cartons
                     # answer, because the key holds "waste" and the other half holds "so much".
                     # The object of the verb stands this row down: money is money.py's
                     # question, the fuels are the energy bill's, and food is the food-waste row's.
                     "money", "wages", "cash", "salary", "payday", "food", "groceries",
                     "time", "water", "electricity", "energy", "gas", "fuel", "petrol",
                     "paint", "wood", "ink", "data", "battery", "heat")),
        # "the bin needs emptying" was answered "right-click the Recycle Bin on the desktop": the
        # word `bin` was the whole reading, and the bin in that sentence is the one under the sink.
        # The technology table reads the machine words out of a line before either row answers, and
        # its row stands down on exactly this reading, so this is the everyday bin's answer.
        entry("empty-the-kitchen-bin",
              (("bin", "bins", "wheelie bin", "kitchen bin", "bin bag", "bin bags", "bin liner",
                "rubbish", "trash"),
               ("empty", "emptied", "emptying", "needs emptying", "need emptying",
                "needs taking out", "need taking out", "wants taking out", "clear", "clearing",
                "cleared", "empty it")),
              "Tie the bag at the top and take it straight out to the wheelie bin: a tied bag left "
              "by the door still smells, and the bin is what wants emptying, not the kitchen. While "
              "it is empty, wipe the inside with hot soapy water and a splash of bleach, let it dry, "
              "then fit the liner before anything goes back in - that once-a-week wipe is what keeps "
              "the flies off in summer. A bag that split on the way out wants a rinse in the garden "
              "rather than a scrub, and the wheelie bin gets the same wash twice a year.",
              guard=lambda read: not the_bin_is_on_a_machine(read),
              # The rows that own the bin's other questions keep them: the bins going out, a letter
              # to the council, a missed collection, a bin too small for the kitchen, and the bin on
              # a computer. A chore said as done or handed over ("i put the bins out") is a line to
              # agree with, not a method to explain, so it is fenced too.
              avoid=("row", "rows", "argument", "argue", "arguing", "flatmate", "housemate",
                     "landlord", "neighbour", "neighbors", "council", "collected", "collection",
                     "missed", "write", "letter", "report", "small bin", "tiny", "too small",
                     "put the bins out", "put the bin out", "put them out", "put it out",
                     "i emptied", "ive emptied", "i took the", "ive taken", "already emptied",
                     "already done", "did it")),
        # The visit length is the answer a how-long line asks for, and the service row above answers
        # with the yearly interval and the price: "how long does a boiler service take" got "once a
        # year, £60 to £120", which is the right topic and the wrong shape.
        entry("boiler-service-duration",
              (("boiler", "boilers", "combi", "gas boiler"),
               # The clock asks, not a list of sentences: "how long does it take to service a
               # boiler", "how long to get the boiler serviced" and "how long will the service
               # take" were all reading past the sentence list above to the yearly-interval
               # row, which is the right topic and the wrong shape. The service words have to
               # be in the line too, so a boiler's life and a boiler's price are not this row.
               ("how long", "how many hours", "how much time", "long does", "long will",
                "how long to", "length of")),
              "About an hour for a straightforward boiler, and up to ninety minutes if it is the "
              "first service in a while or the engineer has to check the flue and the safety "
              "devices. It is a set of checks rather than a strip-down: they run the boiler, test "
              "the flue and the gas pressure, clean what they can reach, and leave you the service "
              "record. Book it for late summer if you can, because the wait is longer once the cold "
              "weather starts.",
              # A boiler's life, its price, its yearly interval and a new one going in are all
              # other rows: this one is the length of the visit.
              avoid=("cost", "price", "much", "worth", "worthwhile", "often", "annual", "yearly",
                     "new", "install", "installation", "replace", "fit", "fits", "fitted",
                     "fitting", "life", "lifespan", "good for",
                     "how many years", "years", "bleed", "pressure", "broken", "fault",
                     # a repair has its own row, with the engineer's visit length in it
                     "repair", "repairs", "repairing", "fix", "fixes", "fixing",
                     # a boiler that is doing something is a fault the talk is on, not a visit
                     # to book: "my boiler is making a noise" then "how long will it take" was
                     # told the length of a service
                     "noise", "noisy", "banging", "rumbling", "knocking", "whistling", "hissing",
                     "leak", "leaks", "leaking", "hot water", "not heating")
              # "how long have i had the boiler now" is the age of the boiler, not the length of
              # the visit, so the possession shape stands this row down too.
              + A_AGE_OWNED,
              # "how long does a boiler service last" is the visit and "how long does a boiler
              # last" is its life, so the row asks for the service word as well as the clock:
              # without it, dropping "last" from the avoid list would take the lifespan line.
              ask=("service", "services", "serviced", "servicing"),
              bias=3),

        entry("boiler-service",
              ("boiler", ("service", "servicing", "serviced", "annual", "yearly", "every year",
                          "certificate", "cost", "much", "price", "landlord")),
              "Once a year, yes: a gas boiler service is usually \u00a360 to \u00a3120 depending on "
              "where you are. It keeps the warranty valid, catches a failing part before it strands "
              "you in winter, and landlords are legally required to have one. Book it in late "
              "summer, when engineers are quiet and the price is lower.",
              avoid=("new", "install", "installation", "replace", "replacement", "buy"),
              ask=("service", "servicing", "serviced", "annual", "yearly", "certificate", "cost",
                   "much", "price", "often")),

        # "can i service my own boiler" and "is it legal to service the boiler" are the same job
        # asked as permission, and a price never answers it: the gas side is Gas Safe work, and
        # what is left for the person is the bit around it.
        entry("boiler-service-diy",
              (("boiler", "boilers", "combi", "gas boiler"),
               BOILER_DIY + ("can i service", "service my own", "service it myself",
                             "service the boiler myself", "legal to service")),
              ("Not the service itself: it means opening the case and checking the gas side, and "
               "a gas boiler is Gas Safe work by law, so the annual service is an engineer's job "
               "at about \u00a360 to \u00a3120. Yours is the bit around it: keep the pressure "
               "at 1 to 1.5 bar, keep the flue and the vents clear, bleed the radiators - and the "
               "warranty usually needs the engineer's service anyway."),
              # a price or an interval with no "own" or "legal" in it is the yearly-service row's
              avoid=("new boiler", "install", "buy"),
              bias=4,
              ask=BOILER_DIY + ("service", "servicing", "serviced", "annual", "yearly"),
              guard=_an_ask_about_servicing_my_own),

        # The stain and the money word together, and never one without the other: with only "stain" it
        # is a cleaning question, and with only "letting agent" it is the agent asking about the boiler.
        entry("damage-deduction",
              (("stain", "stains", "stained", "mark", "marks", "damage", "damaged", "scuff", "scuffs",
                "burn", "burns", "chip", "chips"),
               ("letting agent", "landlord", "landlords", "deduct", "deducted", "deducting", "deduction",
                "deductions", "withheld", "withhold", "withholding", "wear and tear", "deposit",
                "refund", "end of tenancy")),
              ("Ask in writing for an itemised list of what was taken and why, and say which deductions "
               "you disagree with. Fair wear and tear - a carpet going thin where you walk, a worktop "
               "faded by sunlight - is not chargeable; a burn or a paint mark is. If the deposit went "
               "into a protection scheme, use its free dispute service rather than arguing with the "
               "agent, and keep the photos from the day you moved in."),
              bias=1),

        entry("deposit-back", (("deposit", "deposits", "deposit scheme", "tenancy deposit",
                                "holding deposit", "security deposit", "damage deposit",
                                "deposit protection", "deposit protection scheme"),
                               ("back", "returned", "return", "not", "unfair", "withheld", "landlord",
                                "landlords", "claim", "getting", "move out", "moved out",
                                "moving out", "end of tenancy", "tenancy", "renting", "rented",
                                "letting agent", "deductions", "deducted", "deducting",
                                # "can i get my money back from a deposit scheme" asks for the
                                # money without the word back, so the money is the second half
                                "money", "money back", "get it", "how do i get")),
              ("Ask in writing for an itemised list of what was taken and why, and say which of the "
               "deductions you disagree with. If your deposit was in a protection scheme, use its free "
               "dispute service rather than arguing with the landlord; you can also raise it with the "
               "council. Photos from the day you moved in are the evidence that wins this."),
              # the scheme's own letter is rent-deposit's question ("a deposit protection
              # scheme says i owe money" was the itemised list), so the things that letter says
              # keep this row off it
              avoid=("flat", "house", "saving", "save", "rent", "buy", "first home",
                     "says i owe", "they say i owe", "say i owe", "owe money", "i owe"),
              # a scheme, a tenancy and a landlord are all this row's words, so when they are
              # there the row answers over the booking deposit and the chargeback
              bias=3),

        # How much laundry a drum takes: a size question, which the fault rows below cannot answer.
        entry("washing-machine-size",
              (("washing machine", "washer", "washer dryer", "tumble dryer", "dryer", "drum",
                "drum size",
                # the figure on the box is the other way people name the thing: "is 7kg enough
                # for two people" has no word for the machine in it at all
                "7kg", "8kg", "9kg", "10kg", "11kg", "12kg"),
               ("size", "sizes", "sized", "capacity", "kg", "kgs", "kilo", "kilos", "kilogram",
                "kilograms", "litre", "litres", "liter", "liters", "big", "bigger", "biggest",
                "big enough", "how big", "what size", "how many kg", "how much can", "enough",
                # choosing between two: "9kg or 10kg washing machine" is the same size question
                "or 7kg", "or 8kg", "or 9kg", "or 10kg", "or 11kg", "or 12kg")),
              "Roughly: 7kg for one or two people, 8kg for three, 9kg for four and 10 to 12kg if you "
              "wash duvets and bedding in it. The figure is the dry weight of a full load, so a 9kg "
              "drum is not gentler, it just holds more; a bigger one costs more to run per wash but "
              "you run it less often. Measure the gap and the doorway first, because depth is what "
              "usually rules a machine out, and match the dryer to the washer or slightly bigger "
              "than it.",
              # a machine that will not spin, or one that has packed in, is a fault and not a size
              avoid=("wont spin", "won't spin", "not spinning", "no spin", "wont turn", "won't turn",
                     "spin cycle", "soaking", "soaking wet", "still wet", "dripping", "wringing",
                     "wont drain", "won't drain", "packed in", "broke", "broken", "faulty",
                     "leaking", "smell", "smells", "smelly", "noise", "noisy", "banging", "hot",
                     "overheating", "not heating", "wont heat", "won't heat", "wont start",
                     "won't start", "error", "door", "locked", "buy", "buying", "worth it",
                     "cheap", "cheapest", "best", "which one", "recommend",
                     # a weight in kilos is only a laundry size when the line is about laundry:
                     # "is a 2kg joint enough for six" is the roast, and a bag of compost is a bag
                     "turkey", "chicken", "lamb", "beef", "pork", "joint", "roast", "compost",
                     "potatoes", "spuds", "dumbbell", "dumbbells", "barbell", "weights",
                     "suitcase", "luggage", "package", "parcel", "barbecue", "bbq"),
              # The other thing a washer is: a tap washer, a bolt's washer. "what size washer do i
              # need for a 15mm tap" is a size question, so it matched "size" and "washer" and
              # was told how many kilos a drum holds. Plumbing and fixing words stand this row
              # down unless the line also names the machine.
              guard=_not_a_washer_of_another_kind),
        # "how long does a tenancy deposit scheme take to return" was answered with the card about
        # arguing with deductions, which is the other deposit question: this one wants the number
        # of days, and where that number comes from.
        entry("deposit-return-days",
              (("deposit", "tenancy deposit", "deposit scheme", "protection scheme",
                "deposit protection"),
               ("how long", "how many days", "how many weeks", "how soon", "take", "takes",
                "wait", "waiting", "when")),
              ("Ten days is the rule: the deposit has to come back within ten days of the day you "
               "and the landlord agree the amount, and interest can come with it. If you have not "
               "agreed, the landlord has to return the undisputed part within those ten days and "
               "put in a claim for the rest, and a disputed amount goes to the protection scheme, "
               "whose free dispute service usually decides within 28 days. So ask the scheme which "
               "one holds your money, and chase the agent in writing, because the deadline is "
               "counted from the agreement and not from the day you moved out."),
              bias=2,
              # "back to the deposit, how long will it take" is a saver asking how long the
              # saving takes, not a tenant waiting for money back, so the line has to name the
              # tenancy, the scheme or the landlord: see _a_deposit_coming_back.
              guard=_a_deposit_coming_back,
              avoid=("save", "saving", "savings", "put away", "towards", "a month",
                     "each month", "per month", "afford", "first home", "first time",
                     "house", "flat", "moving", "move", "mortgage", "buy", "rent",
                     "renting", "damage", "damaged", "unfair", "withheld", "deduct",
                     "deductions", "cleaning", "checkout", "inspection")),

        # --- a machine that will not spin, a hoover with no pull, a pilot light ---
        entry("washing-machine-spin",
              (("washing machine", "washer", "washer dryer",
                # People describe the fault by what comes out of it rather than by the machine: "the
                # clothes come out soaking wet" never says washer at all, and both words below are
                # only this question when the outcome words beside them say "out of a wash".
                "clothes", "washing", "wash load", "laundry"),
               ("wont spin", "won't spin", "not spinning", "no spin", "wont turn", "won't turn",
                # the same fault in the present tense people actually type: "the washing machine
                # isnt spinning" reached the listening turn, and "the drum isnt turning" too,
                # because only the "not"/"won't" forms were keyed here.
                "isnt spinning", "isn t spinning", "aint spinning", "isnt turning",
                "isn t turning", "isnt going round", "drum isnt turning", "drum not turning",
                "drum", "spin cycle", "spin only", "to spin", "get it to spin",
                "clothes are wet", "clothes come out wet", "soaking", "soaking wet",
                # the outcome said a dozen other ways: still wet, wrung out by hand instead, dripping
                # in the basket, and the machine that "leaves" them wet rather than not spinning
                "wringing wet", "wringing", "still wet after", "still wet when", "sopping",
                "sopping wet",
                "dripping wet", "come out wet", "comes out wet", "come out soaking",
                "comes out soaking", "come out dripping", "comes out dripping", "come out wringing",
                "comes out wringing", "wet after the wash", "wet after a wash",
                "wet after washing", "wet after wash", "come out still wet",
                "comes out still wet", "leaves the clothes wet", "leaves clothes wet",
                "leaves them wet", "leaves it wet",
                # "my washing machine is leaving the clothes soaking" is the same outcome said
                # as it happens, and the leaving form is how people put it
                "leaving the clothes", "leaving clothes", "leaving them", "leaving it",
                "leaving my clothes", "left the clothes", "left clothes",
                # A machine that stops mid-cycle is not this row's question: the door latch and
                # the blocked drain are the answer to it, and this key's "stopped halfway" phrases
                # only took it away from that row once the bias below put this one in front.
                )),
              "One heavy thing is the usual cause: a duvet or a bath mat balls up on one side and the "
              "machine refuses to spin, so shake it flat and run a spin only cycle. Still soaked? Clear "
              "the filter behind the kick plate, because a machine that can't drain won't spin. On an "
              "older machine the belt can slip off, which is a cheap part.",
              # a drum that will not turn is a spin fault; a door that will not open is the door entry,
              # a smell is its own entry, and a squeak or a bang under "spins" is the noise question
              # A drum with a *size* is a capacity question, not a fault: "what size drum for a
              # washing machine", "does a bigger drum wash better" and "washing machine drum size
              # for duvets" were all told a duvet had balled up on one side, because the word
              # "drum" is the only thing in them the row knew. The capacity row below answers them.
              avoid=("buy", "which", "best", "door", "doors", "locked", "lock", "wont open",
                     "size", "sizes", "sized", "drum size", "capacity", "kg", "kgs", "kilo",
                     "kilos", "kilogram", "kilograms", "litre", "litres", "liter", "liters",
                     "big", "bigger", "biggest", "big enough", "how big", "how many kg",
                     "7kg", "8kg", "9kg", "10kg", "11kg", "12kg", "how much can",
                     "won't open", "smell", "smells", "smelly", "musty", "leak", "leaking",
                     "noise", "noisy", "loud", "squeak", "squeaks", "squeaking", "squeal",
                     "squeals", "squealing", "grind", "grinds", "grinding", "bang", "bangs",
                     "banging", "rattle", "rattles", "rattling", "knock", "knocks", "knocking",
                     "whine", "whining",
                     # a load hung out in the rain, or a wet room, is not a spin fault: the outcome
                     # words only count when the line is about what the machine did
                     "rain", "rained", "raining", "rainy", "weather", "storm", "puddle", "puddles",
                     "leak", "leaks", "leaking", "wet room", "wet wipes", "wet wipe",
                     "marks", "mark", "stains", "stain", "black marks", "dark marks", "streaks",
                     # a drum that is hot or overheating is the machine-hot row in home.py, not a
                     # spin fault: "the drum of my washer is hot" is not a duvet balled on one side
                     "hot", "warm", "overheating", "overheated", "burning",
                     "smell of burning",
                     # water that will not leave the drum is the filter and the drain, which is a
                     # different check from a load that came out too wet, and its own card answers
                     # it: this row took "water is sitting in the drum of my washing machine" as
                     # soon as the bias below was raised
                     "sitting", "standing", "sitting water", "standing water", "water sitting",
                     "water standing", "wont drain", "won't drain", "not draining", "didnt drain",
                     "didn't drain", "wont empty", "won't empty", "not emptying"),
              # The outcome lines are this row's own question and `dry-inside` was answering them
              # with a drying rack: it keys on the same wet words and carried the same score with
              # bias 2, so "the clothes come out soaking wet" was told how to hang a load. Two
              # points puts the machine's own fault back in front of it, which is what
              # tests/test_a_wet_load_is_not_a_mark.py has been asserting all along.
              bias=2),

        # A dryer that will not heat, or takes three goes to dry a towel, is one fault with one
        # cause in most homes: the air cannot get through or the heat is not being asked for. There
        # was no entry for it at all, so "i cant get my dryer to heat up" fell through to the chat
        # module ("That would bother me too") and "my dryer takes ages to dry" was answered
        # "Is there anything you'd like a hand with?".
        # A hob that is slow, and a ring that has stopped, had no answer: "my hob is slow to heat",
        # "the hob takes ages to warm up" and "the ring takes ages to heat up" were all a "Got it",
        # and "one ring on my hob doesnt work" was "Ugh, those are fiddly". The hob is a different
        # appliance from the oven and the checks are different again on gas, induction and ceramic.
        # A hob ring that has gone is a part you buy, not an appliance you replace, and the price
        # question had no row: "how much is a new hob ring" fell to the composer's live-prices
        # hedge ("I can't look up live prices"), and a solid plate is a tenner. The row is the
        # price of the part only; cleaning one and fitting a gas one stay where they were.
        entry("hob-scratch",
              (("hob", "hobs", "ceramic hob", "induction hob", "cooker top", "cooker plate",
                "hotplate", "electric hob", "gas hob"),
               # "marks" is the burnt-on cleaning question ("my hob has burnt on marks"), so
               # only the words that name damage are here.
               ("scratch", "scratches", "scratched", "scuff", "scuffs", "scuffed", "gouge",
                "gouged", "chipped", "chip")),
              ("Nine times in ten the mark that looks like a scratch is metal, sugar or limescale "
               "burnt onto the glass: scrape the cold hob with a hob scraper held almost flat, then "
               "rub ceramic hob cleaner over it with a cloth, and it comes away. A real scratch - "
               "you feel it catch a fingernail - cannot be polished out of a glass top, so a fine "
               "one is something to live with and a deep one means a new top, which on a built-in "
               "hob is often most of the price of a new one. Never use an abrasive powder or a "
               "scouring pad; they make more of them."),
              # the surfaces that are sanded or repaired rather than scraped: a wooden floor, a
              # worktop, a car, a phone screen, a bath and a pair of glasses all have their own
              # answer, and each of them would otherwise land here on the word "scratched".
              avoid=("floor", "floors", "wood", "laminate", "worktop", "worktops", "table",
                     "tables", "furniture", "desk", "door", "doors", "car", "cars", "van",
                     "windscreen", "screen", "phone", "mobile", "glasses", "spectacles", "watch",
                     "bath", "bathroom", "sink", "shower", "wall", "walls", "paint", "painted",
                     "leather", "sofa", "shoe", "shoes", "boot", "boots", "cd", "dvd", "vinyl",
                     "record", "records", "lens", "camera", "clean", "cleaning", "grease",
                     "burnt on", "burnt", "burned", "burning", "baked on", "limescale",
                     "buy", "best", "which", "worth", "cost", "price", "cheap", "cheapest")),
        entry("hob-ring-price",
              (("hob ring", "hob rings", "ring", "rings", "burner", "burners", "burner cap",
                "solid plate", "hotplate", "element", "cooker ring", "gas ring"),
               ("cost", "costs", "much", "price", "prices", "buy", "replace", "replacement", "new",
                "cheap", "cheapest", "spare", "spares", "part", "parts", "fit")),
              ("About £10 to £25 for a solid plate or a gas burner cap, and £25 to £50 for an "
               "induction zone's part, so it is worth fixing rather than replacing the cooker. Buy "
               "by the cooker's model number rather than by eye - the same size ring is not always "
               "the same fitting. An electric one is usually two screws and a spade connector; a "
               "gas ring has to be fitted by a Gas Safe engineer."),
              bias=1,
              # a ring you wear, a phone ringing, a ring round the bath and a ring-marked hob are
              # other entries' lines
              avoid=("clean", "cleaning", "grease", "stain", "stains", "scrub", "phone", "mobile",
                     "ringtone", "engagement", "wedding", "gold", "silver", "diamond", "jewellery",
                     # a budget question about the rings you wear is the jewellery row's, and
                     # "how much should we spend on rings" was reaching this one on the tie
                     "spend", "spent", "spending", "budget", "afford", "salary", "propose",
                     "proposal", "carat",
                     # "what ring should i buy" is a ring you wear, and the bare noun in the key
                     # plus "buy" in the ask was enough to answer it with a burner cap
                     "what ring", "which ring", "ring should", "rings should", "pick a ring",
                     "rings cost", "ring cost", "much do rings", "much are rings", "ring prices",
                     "choose a ring", "ring shopping", "wear", "wearing", "worn", "rings to wear",
                     "necklace", "earring", "bracelet", "tarnish", "finger", "ear", "ears",
                     # "burner" is a wood burner and a log burner as well as a gas ring, and
                     # "how much does a wood burner cost" and "how much to install a log burner"
                     # were both answered with the price of a hob ring
                     "wood burner", "woodburner", "wood burning", "woodburning", "log burner",
                     "logburner", "multi fuel", "multifuel", "stove", "stoves", "chimney",
                     "flue", "fireplace", "solid fuel",
                     "bath", "bathtub", "sink", "onion", "calamari", "pineapple", "doorbell",
                     "door bell", "curtain", "smoke", "ow", "hurt", "swollen", "sting")),
        # "how do i fit a wood burner" was answered with the price of a hob ring, and with the stove
        # words held out of that row it became "That's beyond what I know well" - which is worse
        # than a wrong price only because it is honest. Nothing had the fitting itself, and it is
        # the one part of a wood burner a person cannot just get on with: the flue and the chimney
        # have to be signed off.
        entry("fitting-a-wood-burner",
              (("wood burner", "woodburner", "wood burning", "woodburning", "wood stove",
                "log burner", "logburner", "log burning", "multi fuel", "multifuel",
                "solid fuel", "stove", "stoves", "fireplace", "flue", "chimney"),
               # the *fitting* words, not "how do i": "how do i light my log burner" and
               # "how do i stop a chimney banging" both name a stove and ask how, and each has
               # its own card - a bare "how do i" in this group took both of them.
               ("fit", "fits", "fitting", "fitted", "install", "installing", "installation",
                "put in", "putting in", "need", "needed", "regulations", "regs",
                "regulation", "building control", "hetas", "legal", "allowed", "sign off",
                "hearth", "clearance", "distance", "ventilation", "liner", "lining", "line it",
                "what size", "how big", "position", "where can i put", "too close")),
              ("Get it signed off rather than doing the flue yourself: a Hetas-registered installer, "
               "or a fitter whose work building control inspects, is what the regs ask for, and an "
               "unsigned stove is a problem when you sell the house as well as a fire risk. Size "
               "the stove to the room - roughly 1kW for every 14 cubic metres, and no more, because "
               "a big stove turned right down smokes and soots the flue. It needs a non-combustible "
               "hearth (12mm of slate or stone is the usual, and 300mm in front of the door), the "
               "flue swept and lined if the chimney is old, and a carbon monoxide alarm in the same "
               "room, which the law has required for a solid-fuel stove since 2022. In a smoke "
               "control area the stove must be DEFRA-exempt, so check that before you buy it."),
              # what one costs and what one saves is the price and running-cost card's line
              avoid=("how much", "much does", "much is", "cost", "costs", "price", "prices",
                     "cheap", "cheapest", "expensive", "worth it", "save", "saving", "savings",
                     "bill", "quote", "budget",
                     # a dirty stove door, a smoky one and a rusted one are the stove's own jobs
                     "clean", "cleaning", "cleaner", "glass", "soot", "sooty", "smoke", "smoky",
                     "dirty", "sweep", "sweeping", "swept", "paint", "painting", "repaint",
                     "rust", "rusty", "not drawing", "wont light", "won't light", "keeps going out",
                     # lighting it is its own card, and a chimney that bangs is a bird or soot
                     "light", "lighting", "light it", "banging", "bang", "noise", "noisy",
                     "bird", "birds", "damper", "stop the", "smell"),
              # the DIY sheet claims "can i install my own ..." with one key word and one ask,
              # and it is right about a tap washer rather than a flue that has to be signed off
              bias=3),
        entry("hob-heat",
              (("hob", "hobs", "ring", "rings", "burner", "burners", "hotplate", "hotplates",
                "cooker plate", "cooker top", "induction", "ceramic hob", "gas ring", "gas hob",
                "electric hob", "solid plate"),
               ("slow", "slower", "slowly", "ages", "forever", "long", "longer", "takes", "taking",
                "heats", "heating", "heat up", "warms", "warming", "warm up", "not heating",
                "isnt heating", "isn't heating", "wont heat", "won't heat", "not hot", "cold",
                "not working", "doesnt work", "doesn't work", "stopped working", "stopped",
                "dead", "gone", "weak", "barely", "packed up", "stopped heating", "one ring",
                # a ring that will not light at all is the same fault as one that will not heat,
                # and "the hob wont light" was "That would bother me too" on its own
                "wont light", "won't light", "wont ignite", "won't ignite", "wont spark",
                "won't spark", "not lighting", "doesnt light", "doesn't light", "clicks but",
                "no flame", "wont stay lit", "won't stay lit", "goes out", "keeps going out")),
              _hob_heat,
              # a dirty hob is a cleaning job, a pan that will not heat on induction is the pan's own
              # question when the line names the pan, and buying or choosing one is a shopping answer
              avoid=("clean", "cleaning", "grease", "greasy", "burnt on", "stain", "stains", "scrub",
                     # A gym, a job and a hospital all have an induction, and only the kitchen one
                     # is a hob: "what should i take to a gym induction" was the ceramic element
                     # ("check the pan before the hob"). None of these words is in this row's key,
                     # and the fitness row answers the gym line.
                     "gym", "gyms", "new job", "first day", "at work", "the office", "staff",
                     "orientation", "hospital", "ward", "antenatal", "new starter", "volunteer",
                     "shiny", "oven", "grill", "microwave", "kettle", "wood burner", "log burner",
                     "buy", "best", "which", "worth", "cost", "price", "cheap", "cheapest",
                     "how do i use", "setting", "simmer", "boil", "wok", "season", "seasoning",
                     "pressure cooker", "slow cooker", "air fryer", "boiler", "pilot",
                     "pilot light", "candle", "candles", "fire", "fireplace", "barbecue", "bbq",
                     # A phone rings and a hob has rings, and "ring"/"rings" is in this key, so
                     # "how do i stop my phone ringing at night" was the ceramic-element answer.
                     # Anything about a phone means the ring in the line is the sound.
                     # The words are the phone's own and never a hob's: "ringing" and "rang" fold
                     # onto "ring", so they would take every hob line with them.
                     "phone", "phones", "mobile", "mobiles", "ringtone", "voicemail", "landline",
                     "missed call", "missed calls",
                     # The same worry one step further out: "how do i stop my ears ringing" and "the
                     # ringing in my ears wont stop" were the ceramic-element answer, because a ring
                     # that will not heat and an ear that will not stop are the same two words. The
                     # tinnitus row holds the ear words below, so any of them means the line is about
                     # a person and not a hob. "ringing" and "rang" still cannot go here - they fold
                     # onto "ring", and they would take every hob line with them.
                     "ear", "ears", "tinnitus", "hearing", "my ears", "in my ears", "in my ear",
                     "ringing in my ears", "ringing in the ears",
                     # and a ring you wear is not a hob ring either: "my ring has gone green" was
                     # this answer, and green is the tarnish on silver, not an element going out
                     "gold", "silver", "jewellery", "jewelry", "necklace", "bracelet", "earring",
                     "earrings", "engagement ring", "wedding band", "diamond", "tarnish",
                     "tarnished", "green", "gone green", "finger green", "clean my ring",
                     # a ring that has gone dull or wants a polish is a jeweller's job as well
                     "dull", "dulled", "polish", "polishing",
                     # and the verb: "i need to ring in tomorrow" was the ceramic element,
                     # because the ring a line is asked about can be a phone call and the two
                     # words it took to say so were not in this list. See `RING_AS_A_CALL`.
                     ) + RING_AS_A_CALL,
              bias=1, guard=_a_person_not_a_hob),
        # An iron that spits water or leaves marks is the commonest thing that goes wrong with one,
        # and it had no answer at all: "my iron spits water" was "Thanks for telling me" and "my iron
        # is leaking water" was "That would bother me too".
        entry("iron-fault",
              (("iron", "irons", "steam iron", "steam generator", "soleplate"),
               ("spits", "spitting", "spit", "spat", "spits out", "spitting out", "spitting water",
                "drips", "dripping", "drips water", "leaks", "leaking", "leaky", "water",
                "wet patches", "wet patch", "marks", "white marks", "brown marks", "streaks",
                "spraying water", "sprays water", "water on the clothes", "damp clothes",
                # a soleplate that stays cold is the other half of the same question
                "wont heat", "won't heat", "wont heat up", "won't heat up", "not heating",
                "isnt heating", "isn't heating", "no heat", "stopped heating", "cold", "dead",
                "wont get hot", "won't get hot", "not hot", "wont turn on", "won't turn on",
                "wont switch on", "won't switch on")),
              _iron_fault,
              # ironing a garment, a scorch on fabric, the crease and the fold, and buying one are
              # other entries: this one is only the iron misbehaving with its own water
              avoid=("crease", "creases", "ironing board",
                     "scorch", "scorched", "burn", "burnt", "buy", "best", "which", "worth",
                     "cost", "price", "cheap", "travel iron", "hair", "hair straighteners",
                     "curling", "fabric", "shiny", "clothes are",
                     # "wont heat" and "won't heat" were in this row's own key group and in
                     # this avoid list at the same time, so the row stood itself down for the
                     # half of its question about a soleplate that stays cold: "the iron wont
                     # heat up" was a shrug while "my iron isnt heating up" was answered. An
                     # avoid word is read through its forms and stands the whole row down, so a
                     # key word of the same row can never be one.
                     "cord", "plug", "fuse", "water tank", "limescale in the kettle"),
              bias=1),

        entry("dryer-not-heating",
              (("tumble dryer", "tumble drier", "dryer", "drier", "tumbler", "washer dryer"),
               ("not heating", "isnt heating", "isn't heating", "no heat", "wont heat", "won't heat",
                "heat up", "heating up", "cold", "takes ages", "takes forever", "not drying",
                "wont dry", "won't dry", "doesn't dry", "doesnt dry", "still wet", "still damp",
                "clothes are damp", "clothes are wet", "long time to dry",
                # "my tumble dryer takes two goes" and "my clothes come out damp after two cycles"
                # are the same slow-drying question, and they were a "Got it" for want of "goes"
                # and "cycles" here.
                "two goes", "two cycles", "goes", "go", "cycles", "cycle", "come out damp",
                "comes out damp", "still damp after", "damp after", "takes two",
                "leaves the clothes damp", "leaves clothes damp", "leaves them damp",
                "clothes damp", "clothes still wet", "clothes are still wet",
                # a slow dryer is the same question as a cold one, and the "taking" forms were the
                # fuse-and-wall-switch card instead: "how do i stop my tumble dryer taking three
                # hours" was answered with the checks for a machine that will not start at all.
                "taking ages", "taking so long", "takes so long", "taking hours", "takes hours",
                "taking three hours", "taking two hours", "taking a long time", "takes a long time",
                "hours to dry", "long to dry", "slow to dry", "drying slowly")),
    _dryer_heat,
              # a dryer that will not turn, or that squeals, is the noise and drum question; a
              # blocked vent in a rented flat is the damp one; and the running cost is its own entry
              avoid=("buy", "which", "best", "worth", "cost", "cheap", "cheapest", "running",
                     "noise", "noisy", "loud", "squeak", "squeaks", "squeaking", "bang", "bangs",
                     "banging", "rattle", "rattles", "grind", "grinds", "grinding", "smell",
                     "smells", "smelly", "fire", "fires", "lint fire", "condensation", "mould",
                     "mold", "damp walls", "hair dryer", "hairdryer")),

        # A drum that will not turn is the same machine with a different part at fault, and the heat
        # answer leads somewhere the person cannot check. The belt slipping off is the usual cause and
        # it is cheap to put right, so it is said first.
        # A dryer that smells of burning is a lint fire waiting to happen, and the answer it got was
        # to simmer a pan of vinegar. Nothing else in the kitchen keys the smell of a dryer, so it
        # fell to the general odour entry, which is advice for a room.
        # A dryer that smells musty or damp is the machine's own trapped moisture, and the only
        # smell row it had was the burning one, so "the heat pump dryer smells" and "my dryer
        # smells musty" were a shrug and "the tumble dryer smells musty" was the washing
        # machine's service wash. The fix is the fluff and the condenser, which is where the
        # water sits.
        entry("dryer-smells",
              (("tumble dryer", "tumble drier", "dryer", "drier", "tumbler", "washer dryer",
                "heat pump dryer", "heat pump drier", "heat pump tumble dryer", "vented dryer",
                "condenser dryer"),
               ("smells", "smell", "smelly", "stinks", "stink", "stinking", "musty", "fusty",
                "damp smell", "damp", "mouldy", "moldy", "mildew", "sour", "whiff", "reek",
                "reeking", "pongs", "pong", "funky", "off smell", "smells off")),
              "Nearly always the fluff and the water: empty the fluff filter and wash it, pull the "
              "condenser out and rinse it under the tap if the machine has one, and tip out the "
              "water tank or check the drain hose. On a heat pump or condenser dryer the smell is "
              "usually the condenser left damp, so run a rinse cycle and leave the door and the "
              "drawer open afterwards. A vented dryer wants the vent hose cleared and the outside "
              "flap checked, and once a year wipe the drum and the seal with a hot damp cloth.",
              # a burning smell is the fire card's, and the ones that are not the machine -
              # cooking, the room, a drain, the fridge - are their own rows' questions.
              avoid=("burning", "burnt", "scorched", "singed", "smoking", "fire", "smells hot",
                     "smells really hot", "too hot", "oven", "kitchen", "room", "fridge",
                     "freezer", "washing machine", "dishwasher", "sink", "drain", "drains",
                     "bin", "bins", "cooker", "hob", "microwave", "hair dryer", "hairdryer",
                     "takes ages", "not drying", "still wet", "not heating", "not working",
                     "buy", "worth", "cost", "running")),

        # "do heat pump dryers need a vent" was answered with the buying advice ("worth it if you
        # would use it three times a week"), which is a different question, and the vent question
        # is the one that decides where the machine can go. It is a fixed fact per kind of dryer,
        # so it is keyed by the kind and the word for the duct.
        # A hair dryer is not a tumble dryer, and once the radiator row stopped taking every
        # "not heating up" the line fell to a shrug: "my hair dryer is not heating up" had been
        # told about a thermostatic valve head, which is the wrong machine as well as the wrong
        # part. The grille is the first thing to check and it is a different job from a dryer's
        # fluff filter, so it is its own row.
        entry("hair-dryer-not-hot",
              (("hair dryer", "hairdryer", "hair drier", "blow dryer", "blowdryer"),
               ("not heating", "isnt heating", "isn't heating", "not heating up", "no heat",
                "no heat coming out", "blowing cold", "blows cold", "cold air", "cold",
                "stopped heating", "wont heat", "won't heat", "wont heat up", "won't heat up",
                "not hot", "isnt hot", "isn't hot", "wont get hot", "won't get hot",
                "keeps cutting out", "cuts out", "cut out", "stopped working", "dead",
                "takes ages", "smells hot", "buzzing")),
              _hair_dryer,
              # how long one lasts, whether to buy one and styling a head of hair are other rows'
              avoid=("buy", "buys", "buying", "best", "which", "worth", "cost", "price", "cheap",
                     "how long", "last", "lasts", "lasting", "curlers", "straighteners",
                     "straightener", "diffuser", "brush", "bristles", "dry my hair", "dry hair",
                     "hairdryer brush", "styling", "frizz", "curly", "curls")),

        entry("dryer-vent",
              (("tumble dryer", "tumble drier", "dryer", "drier", "tumbler", "washer dryer",
                "heat pump dryer", "heat pump drier", "heat pump tumble dryer", "vented dryer",
                "condenser dryer"),
               ("vent", "vents", "vented", "venting", "ventilation", "hose", "hoses", "duct",
                "ducting", "flue", "out of the window", "outdoors", "outside wall", "wall vent",
                "needs a vent", "need a vent", "need venting", "no vent", "without a vent",
                "tumble dryer vent", "dryer vent",
                # a heat pump dryer makes water instead of steam, and "where does the water go
                # in a heat pump dryer" named the water rather than the vent, so it fell to the
                # slow-drying row. The tank and the hose are this row's answer.
                "where does the water go", "where does the water", "water go",
                "water tank", "empty the water", "condenser water", "the water goes")),
              "A heat pump or condenser dryer needs no outside vent at all - the water goes into a "
              "tank you empty, or down a hose to the drain - so it can sit in a cupboard or a "
              "bedroom. Only a vented dryer needs the duct, and then it wants the hose out through "
              "a wall vent or an open window with no kinks and no crushed section behind the "
              "machine; a short straight run to outside is the whole job. Never duct one into a "
              "loft or a chimney: that puts the damp and the lint back into the house, and fluff "
              "round a hot duct is a fire.",
              # a dryer that is not heating, not turning, smelling, cutting out or being chosen in
              # a shop is another row's; this one is only where the air and the water go.
              avoid=("not heating", "isnt heating", "isn't heating", "not drying", "takes ages",
                     "still wet", "still damp", "smells", "smell", "burning", "fire", "sparks",
                     "wont turn", "won't turn", "not spinning", "cuts out", "stopped working",
                     "buy", "best", "which", "worth", "cost", "cheap", "running cost",
                     "hair dryer", "hairdryer", "condensation", "mould", "mold", "damp walls")),

        entry("dryer-smells-of-burning",
              (("tumble dryer", "tumble drier", "dryer", "drier", "tumbler", "washer dryer"),
               ("burning smell", "smells of burning", "smells like burning", "smell of burning",
                "smells burnt", "smells scorched", "smells singed", "smells hot", "burning",
                "scorching", "smoking")),
              "Stop it and unplug it, and do not run another load until you have looked: a dryer fire "
              "starts with lint round the heater or a vent hose full of fluff, and the smell is the "
              "warning. Empty the fluff filter and clear the hose. Still there after that? Get an "
              "engineer out, and never leave a dryer running while you are out.",
              avoid=("buy", "which", "best", "worth", "cost", "running", "noise", "noisy", "heating",
                     "not heating", "takes ages", "hair dryer", "hairdryer", "oven", "room", "kitchen",
                     "fridge", "freezer", "washing machine", "damp", "mould", "mold")),

        entry("dryer-drum-not-turning",
              (("tumble dryer", "tumble drier", "dryer", "drier", "tumbler", "washer dryer"),
               ("wont turn", "won't turn", "not turning", "isnt turning", "isn't turning",
                "drum isnt turning", "drum not turning", "drum wont turn", "drum not moving",
                "wont spin", "won't spin", "not spinning", "no spin", "drum dead")),
              "The belt has almost certainly slipped off or snapped: it is a rubber band round the drum "
              "and the motor pulley, a few pounds, reached through the back panel with a screwdriver. "
              "Turns by hand but not under power? Belt or door switch. Will not turn by hand either? "
              "Something is jammed or the bearings have gone, which usually means a new machine.",
              # the heat, the noise, the running cost and the buying question all have answers of
              # their own, and a dryer that smells of burning is a fire question, not a belt.
              avoid=("buy", "which", "best", "worth", "cost", "cheap", "running", "noise",
                     "noisy", "loud", "squeak", "squeaks", "squeaking", "bang", "bangs",
                     "banging", "rattle", "rattles", "grind", "grinds", "grinding", "smell",
                     "smells", "smelly", "fire", "fires", "heating", "heat up", "not heating",
                     "takes ages", "still wet", "still damp", "hair dryer", "hairdryer")),

        entry("vacuum-suction",
              (("vacuum", "vacuum cleaner", "hoover", "henry", "dyson", "vax"),
               ("suction", "lost suction", "no suction", "not picking up", "wont pick up",
                "won't pick up", "not sucking", "weak", "blocked", "clogged", "full",
                # "picking up" is the way most people say it, and "picking" is the only word that
                # says which part of the air path has failed: "my hoover isnt picking anything up"
                # reached nothing at all, and "the hoover wont pick anything up" was read as the
                # hand habit of picking. The vacuum noun in the first group is what keeps the hand
                # habit out, and `which`/`buy` below keep the shopping question out.
                "picking", "pick", "picked", "picks", "picking up", "pick up", "picks up",
                # "how do i unblock a hoover" is the same air path said the other way round, and it
                # reached nothing at all: unblock is not a form of blocked, and the appliance alone
                # is one word of key
                "unblock", "unblocking", "clearing", "bunged", "bunged up", "jammed", "stuck",
                # "how do i unclog a hoover" reached nothing: unclog is not a form of clogged, and
                # "how do i fix the hoover" named no air word at all. Both are this one job.
                "unclog", "unclogging", "clogging", "fix", "fixing", "stopped picking up")),
              "Follow the air path: take the hose off both ends and drop a coin through it, shake the bag "
              "or empty the bin, wash the filter (most are washable, and it has to be bone dry before it "
              "goes back) and cut the hair off the brush bar. A blocked hose, a full bag or a matted "
              "filter is the answer nearly every time, and all three are free to fix.",
              # A named vacuum with "fix" in the line is this job, not the machine-stopped card's
              # first checks: "how do i fix the hoover" was answered "check the plug fuse ... then
              # ring the retailer", which is consumer law for a machine that will not start. The
              # one point of lift only wins against the cards that also match a vacuum, and the
              # power words below hand a vacuum that really has stopped dead back to them.
              bias=2,
              # "help me pick a hoover" is the shopping question with the fault entry's words in it
              avoid=("buy", "which", "best", "cheapest", "worth", "cordless",
                     # a vacuum that will not start at all is the machine card, not the air path
                     "wont turn on", "won't turn on", "wont switch on", "wont start", "wont come on",
                     "no power", "dead", "fuse", "stopped dead", "smell", "burning",
                     # a robot vacuum that gets stuck is the brushes, the wheels and the map, not the
                     # air path, and the answer here would be the wrong list of things to check
                     "robot",
                     "choose", "choosing", "recommend", "recommendation", "shop", "shopping",
                     "help me pick", "pick a", "pick the", "picking a", "pick one", "pick out")),

        # A toaster that browns one side of the bread is not the pops-early fault: one element has
        # gone or the bread is sitting proud, and either way the timer is fine. It reached the
        # meal rows ("what to have on toast") because "toasts" and "one side" are both food words.
        entry("toaster-one-side",
              (("toaster", "toast", "sandwich toaster"),
               ("one side", "one side only", "only one side", "one end", "uneven", "unevenly",
                "patchy", "halfway", "one half", "half cooked", "not browning")),
              "One side not browning means the element on that side has gone, or the wire that feeds "
              "it: unplug it, and if you look in while it is cold and one element never glows while "
              "the others do, that is the fault. On an ordinary toaster that is a new toaster, not a "
              "repair. If it browns at one END instead, the bread is sitting proud of the slots and "
              "the elements are fine.",
              avoid=("buy", "best", "which", "cheapest", "worth", "recipe", "recipes", "idea",
                     "ideas", "dinner", "lunch", "breakfast", "sandwich", "topping", "toppings")),

        entry("pilot-light",
              (("pilot light", "pilot", "pilot flame"),
               ("going out", "goes out", "gone out", "wont stay lit", "won't stay lit", "keeps going",
                "blows out", "not staying", "wont light", "won't light", "wont stay on",
                "won't stay on", "flame")),
              "Hold the knob in for twenty seconds after the flame catches, then let it go: a pilot that "
              "won't hold is nearly always the thermocouple, a small part a Gas Safe engineer swaps in "
              "ten minutes. A draught or a dirty jet does it too, and both mean taking the case off, so "
              "that is their job as well. If you smell gas, turn it off at the meter, open the windows "
              "and ring the gas emergency line on 0800 111 999.",
              avoid=("buy", "best", "cost", "price")),

        # "can i fix it myself" is asked after a fault far more often than it is typed as a whole
        # question, and it went two ways and neither helped: alone it reached nothing and the person
        # got "I don't know enough to answer that honestly", and in a thread it collected the repair
        # rule ("worth repairing while the quote is under half the price of a new one"), which is a
        # different question. The do-it-yourself words are one key part and the job the other, so the
        # job may come from this line or from the one it leans on; the ask gate is what keeps it off
        # a report ("i fixed it myself this time"), because a report is not a question about whether
        # to have a go. `myself` and `my own` are in half the language - a haircut, a tax return,
        # being on your own - so the avoid list names the things that are not house repairs.
        entry("fix-it-myself",
              (("myself", "my own", "diy", "have a go", "having a go", "have a bash",
                "give it a go", "giving it a go", "by myself", "on my own"),
               ("fix", "fixing", "fixed", "repair", "repairing", "mend", "mending", "install",
                "installing", "fit it", "fitting", "replace", "replacing", "unblock",
                "unblocking", "do it", "go at it", "at it", "sort it", "sort that",
                "take it apart", "take apart", "plumb", "plumbing",
                "wire", "wiring", "rewire", "rewiring", "electric", "electrics", "bleed", "service",
                "seal", "belt",
                # "washer" is the appliance in one line and the little rubber disc in another: a tap
                # washer is a five-minute job, and reading it as the machine loses the question.
                "tap washer", "tap washers", "washer", "part")),
              _diy,
              ask=("can i", "can we", "could i", "should i", "should we", "shall i", "is it worth",
                   "worth", "easy", "easier", "hard", "difficult", "safe", "able to", "dare",
                   "do i need", "possible", "any point"),
              avoid=_DIY_AVOID,
              # "is it easy to replace a tap washer myself" names two things a rule can be keyed on
              # (a tap, a washer) and the rule that owns them is repair-or-replace, which answers a
              # machine that failed, not a person asking whether to have a go. A line that says
              # "myself" is asking the do-it-yourself question, so this entry leans over a job rule.
              bias=2),

        entry("tradesperson-check",
              (("tradesperson", "tradesman", "plumber", "electrician", "builder", "roofer",
                "gas engineer", "handyman", "boiler engineer",
                # the same ask about the other trades people hire: "how do i find a good decorator"
                # was a search hedge while the plumber in the line was answered
                "decorator", "decorators", "painter", "painters", "plasterer", "plasterers",
                "tiler", "tilers", "joiner", "joiners", "carpenter", "carpenters", "glazier",
                # not "window fitter": the fitness card reads "fitter" as someone getting fit
                "locksmith", "gardener", "gardeners", "landscaper", "fencer", "chimney sweep",
                "roof tiler", "bricklayer",
                # "how do i check if a company is legit" was a shrug: the question is the one a
                # person asks about a plumber, so the trade names are not the only door into it.
                # "website", "shop", "garage" and "dealer" are left out on purpose - a fake website,
                # an online shop and a used car each have a row of their own that knows more.
                "company", "companies", "firm", "business", "supplier", "installer",
                "installation company", "contractor", "contractors", "man with a van",
                "removals", "tradesperson", "tradespeople"),
               ("check", "reputable", "trust", "trustworthy", "cowboy", "avoid", "rip off",
                "rip-off", "how do i know", "vet", "choose", "find a good", "insurance", "quote",
                # "how do i find a reliable tradesperson" wanted the word "good" in the line
                "reliable", "careful", "decent", "honest", "find a", "find someone", "who can",
                "good one", "good company", "good firm", "pick a", "picking a",
                # "how do i spot a cowboy builder" is the same question as "how do i avoid" one, and
                # it went to a complaint entry: spotting one is how to pick one.
                "spot a", "how do i spot", "how to spot", "spotting",
                # the same ask about a company rather than a trade
                "legit", "legitimate", "genuine", "registered", "look up", "look them up", "verify",
                "vetted", "references")),
              "Start with Companies House, which is free: search the name or the number on their quote "
              "and you can see whether the company exists, when it was formed and whether the "
              "registered address is a real place rather than a mail drop - a limited company has to "
              "put its number and registered address on its website and its invoices. Then the trade "
              "checks: a written quote rather than a verbal one, proof of insurance, and for gas, oil "
              "or electrical work the registration number you can check yourself on the Gas Safe, "
              "OFTEC or NICEIC register. A neighbour who has used them beats any review site, and pay "
              "by card rather than bank transfer so there is a chargeback if it goes wrong. Never pay "
              "the whole price up front - a deposit for materials is normal, the rest when it is done.",
              # a line that complains is the complaint answer's, and so is a line about your rights:
              # "we got ripped off by a roofer" is money and small claims, not how to pick one.
              avoid=("cheap", "cheapest", "cost", "how much", "price", "hourly", "emergency",
                     "no hot water", "leak", "leaking", "broken",
                     "rip off", "ripped off", "ripping off", "overcharged", "refund",
                     "small claims", "trading standards", "botched", "bad job", "rubbish job",
                     "took my money", "never came back", "complain", "complaint", "guarantee",
                     "warranty", "rights", "did a runner",
                     # a link, a login or an email is the phishing rows' line: "is this website a
                     # scam" and "is an online shop with no reviews safe" both had a better answer
                     # before this entry learned the word "website", so the door stays shut
                     "website", "websites", "online shop", "link", "click", "clicked", "login",
                     "password", "email", "text message", "phishing", "invoice for", "paypal",
                     "bank details", "account details")),

        # Nobody in this tree answered the kit question: "what should i have in a first aid kit" fell to
        # "I don't know enough to answer that honestly". The list is the ordinary one a pharmacist would
        # give, and it is on the house rather than a symptom, so the safety module keeps the injuries.
        entry("first-aid-kit",
              (("first aid kit", "first aid box", "first aid", "medical kit", "first-aid kit",
                "medicine cupboard", "medicine cabinet", "medicine box", "first aid supplies"),
               ("have", "need", "keep", "put", "got", "get", "buy", "stock", "include", "contents",
                "what", "at home", "for the car", "should")),
              ("A home kit is a box you can use one-handed in the dark: plasters in a few sizes, sterile "
               "gauze and tape, a crepe bandage, small scissors, tweezers, disposable gloves, a "
               "thermometer, and children's paracetamol with the dose worked out by weight. Add an ice "
               "pack, antiseptic cream and the 111 number, then check it once a year and replace "
               "anything past its date."),
              # An injury is the safety module's line, not a shopping list: the kit entry is only for
              # the question about what a kit holds.
              avoid=("burn", "burns", "burnt", "scald", "scalded", "cut", "cuts", "bleeding", "bled",
                     "nosebleed", "sprain", "sprained", "choking", "choked", "swallowed", "overdose",
                     "rash", "fever", "temperature", "allergic", "anaphylaxis", "seizure", "fit",
                     # a course or a certificate is a different question from a box of plasters
                     "course", "training", "certificate", "qualification")),

        # What to do with paint is asked at the shed door, and the answer is a legal one: liquid paint
        # is not household waste, so it has to be dried out or taken to the tip.
        entry("paint-smell-curing", (("paint", "painting", "repainted", "paintwork", "gloss", "emulsion",
                                "undercoat"),
                               ("smell", "smells", "smelling", "smelly", "smells of", "smelt",
                                "fumes", "fume", "stink", "stinks", "lingering")),
              "Keep the windows open and let it cure: water-based paint stops smelling within a day or "
              "two, and oil-based gloss takes a week or so to stop off-gassing. A bowl of water with a "
              "chopped onion in the room overnight, or a dish of bicarbonate of soda, takes the edge "
              "off. Don't mask it with candles. If it is still strong after a week, the paint may be "
              "old or the room under-ventilated.",
              bias=1,
              avoid=("tin", "tins", "leftover", "dispose", "bin", "recycle", "tip", "gas",
                     "carbon monoxide", "burning", "smoke")),
        entry("paint-tins",
              (("paint", "paint tin", "paint tins", "tins of paint", "paint pot", "paint pots",
                "leftover paint", "old paint",
                # a tin that is drying out is kept, not thrown away, and the phrases are how that
                # question arrives: "dried out" alone is the tip
                "drying out in the tin", "dries out in the tin", "dried out in the tin",
                "drying out in the can", "gone hard in the tin", "skinned over", "a skin on"),
               # "tips" must not match "the tip": "any tips for painting a small room" is the painting
               # entry, and the forms of the bare word "tip" catch it
               ("old", "leftover", "dispose", "get rid", "throw", "bin", "recycle", "the tip",
                "to the tip", "recycling centre", "tins", "pots", "half a tin", "dried out", "store",
                "keep", "what do i do")),
              "A tin of paint has to dry out before it can go anywhere. Stir sand, sawdust or cat "
              "litter into it, leave the lid off somewhere safe until it is hard, then take it to the "
              "household waste recycling centre, where nearly every site takes paint. To keep a "
              "part-used tin, wipe the rim, press the lid down with a block of wood and store it upside "
              "down so no skin forms. A few inches left is worth offering on Freecycle.",
              # "how do i get rid of the smell of paint" was answered with "dry the tin out": the
              # smell of a room is paint-smell, and only a leftover tin is this row's business.
              avoid=("wall", "walls", "ceiling", "woodwork", "paint the", "repaint", "colour",
                     "nail polish", "spray", "smell", "smells", "smelling", "smelly", "smells of",
                     "fumes", "fume", "stink", "stinks",
                     # "keep" and "store" are how a leftover tin is asked about, and they took "how do
                     # i keep my paint from drying too fast" with them: keeping a paint workable while
                     # you use it is paint-drying-fast's question, and this card is about a tin that
                     # is finished with
                     "drying too fast", "drying too quickly", "dries too fast", "dry too fast",
                     "from drying", "keeps drying", "before it dries", "going off the brush",
                     "wet edge", "open time", "workable")),

        # A second-hand machine is a price question, so the numbers come first and the checks second.
        entry("second-hand-washer",
              (("washing machine", "washer", "tumble dryer", "dishwasher"),
               # the second-hand words carry this one: "what's the best washing machine to buy" is the
               # shopping domain, and a bare "buy" or "worth" would take it
               ("second hand", "second-hand", "used", "refurbished", "reconditioned", "cheap",
                "cheaper", "fair price", "how much", "private sale", "facebook", "gumtree",
                "gum tree", "dealer", "nearly new")),
              _washer_price,
              # A machine being priced is not a machine being cleaned: "how much bleach in the
              # washing machine" was answered with what a second-hand one costs, and a mouldy door
              # seal is the mould answer's question, not this one's.
              avoid=("bleach", "mould", "mold", "mildew",
                     "fix", "repair", "broken", "leaking", "error", "wont spin", "won't spin",
                     "not draining", "smells", "install", "plumbing in")),
        # Furniture up a stairwell is a measuring and lifting question, and the answer that saves the
        # wall (and a back) is the tape measure, not muscle.
        entry("furniture-upstairs",
              (("wardrobe", "chest of drawers", "sideboard", "bookcase", "bookshelf", "sofa",
                "couch", "settee", "armchair", "table", "bed frame", "divan", "furniture", "dresser",
                # a mattress is the classic thing that will not turn the corner, and it was a shrug
                "mattress", "bed"),
               ("upstairs", "up the stairs", "stairwell", "landing", "narrow stairs", "on my own",
                "by myself", "get it up", "move it up", "carry it up", "one person", "two people",
                "up a floor", "second floor", "top floor",
                # Getting the thing into the new place in the first place is the same measuring and
                # lifting job, and the plainest way of asking it names no stairwell at all: "how do
                # i move a sofa" and "how do i move my sofa to my new flat" were both a shrug. The
                # moving words are the second part of the key, so the furniture word still has to be
                # there and "how do i move house" stays with the moving-day plan.
                "move", "moving", "moved", "new flat", "new house", "downstairs", "front door",
                "through the door", "doorway", "doorways", "van", "hire", "hiring", "removals",
                "removal", "too big", "wont fit", "won't fit", "get it to", "get it in")),
              _furniture_upstairs, bias=2,
              # "can i get a sofa up the stairs on my own" was answered by the making-friends row,
              # which keys "on my own" too and outscored this one; the bias settles it, and the two
              # key groups here still have to match, so a lonely line is never this answer.
              avoid=("assemble", "flat pack", "build", "ikea", "squeak", "hinge", "slide", "rail",
                     "mirror", "sell", "buy", "choose", "paint",
                     # A move that names a price is the van-hire row's question, and that row opens
                     # with the numbers; the measuring answer is for the person who has the van.
                     "cheap", "cheaper", "cheapest", "cheaply", "cost", "costs", "price",
                     "how much", "man with a van", "hire a van",
                     # A move that has already hurt somebody is the body's answer: "my backs been
                     # killing me since i moved the sofa" was told to measure the stairwell.
                     "my back", "my backs", "bad back", "sore back", "killing me", "back hurts",
                     "pulled my back", "hurt my back", "done my back", "in agony"),
              # A house's size is not a bed being carried: "its a 3 bed with a garden", said in a
              # chat about moving, reached this row because "bed" is a key and the carried line
              # about the move met the second group. Only a line that is describing the home
              # stands the row down - a carried thing keeps the measuring card, so "a 4 bed
              # mattress", "a 2 bed settee" and "moving a bed into a 3 bedroom house" still fit.
              guard=_not_a_size_of_a_home),
    ]
