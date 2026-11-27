"""Rows 1 of 10 of `home_craft.entries()`: `stair-gate` .. `water-shutoff`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _a_dripping_tap,
    _a_washer_two_things,
    _a_washer_with_no_other_subject,
)


def rows():
    from ..knowledge.home import (
        JOB_GUARD, NOT_A_TRADE_WORDS, _a_mark_that_is_live, _broken_window, _going_to_the_loo,
        _mould, _pipes, _the_black_is_not_a_body, _pressure_weak, _roof_leak, _water_off, entry,
        the_trade_to_call
    )
    return [
        # A stair gate had no card at all: "how do i fit a stair gate" and "do i need a stair
        # gate" were both "I don't know enough to answer that honestly", and "how do i fit a stair
        # gate round the newel post" was the rounding rule, because "round" is the maths verb
        # there. The one thing that matters is which way it is fixed.
        entry(
            "stair-gate",
        (("stair gate", "stair gates", "stairgate", "stairgates", "baby gate", "baby gates",
          "safety gate", "safety gates", "child gate", "child gates", "pressure gate"),
         ("fit", "fits", "fitting", "fitted", "install", "installing", "put up", "putting up",
          "fix", "fixing", "mount", "mounting", "buy", "need", "which", "best", "top", "bottom",
          "stairs", "staircase", "newel", "banister", "bannister", "wall", "doorway", "toddler",
          "baby", "measure", "measuring", "remove", "take down")),
        "At the top of the stairs use a screw-fixed gate, never a pressure-fit one: a pressure gate "
        "grips between two surfaces and a determined toddler can push it out of the opening, and the "
        "top of the stairs is the one place that matters. A pressure gate is fine in a doorway or at "
        "the bottom of the stairs, where it needs no drilling, but check it by hand every week or so "
        "as the pads work loose. Measure the opening at its widest and buy a gate whose stated range "
        "covers it, and add a banister or newel-post adaptor, or an extension, when one side is a "
        "post rather than a flat wall. Look for a gate to BS EN 1930, at least 73cm high, with a door "
        "that swings away from the stairs, and no bottom bar across a step because it is a trip.",
        ask=("how", "what", "which", "do i need", "should i", "best", "fit", "install", "buy"),
        avoid=("dog", "dogs", "puppy", "cat", "cats", "pet", "pets", "rabbit", "chicken",
               "chickens", "hens", "goat", "garden", "driveway", "field", "fence", "gate post",
               "gatepost", "wooden gate", "front gate", "back gate", "side gate", "airport",
               "departure", "boarding", "flight", "concierge", "number", "digits", "decimal"),
        bias=2),

        # --- who to call --------------------------------------------------------
        # The trade is the answer, so it is the first thing said. The keys are the asking and the
        # reply is worked out from the thing named, because one row per trade would let the wrong
        # trade answer a line that names two ("a leaking roof" is a roofer, not a plumber).
        # A trade quotes a price for the job, so there is nothing to tip on top of it. The tip table
        # is money's, and a line naming a trade is read as a home question ("plumber" is what the
        # home-and-diy topic is about), so the answer has to live here to be reached at all: the
        # money row was turned down on the topic and "how much do you tip a plumber" fell through to
        # the careers entry about getting into the trades.
        entry("a-trade-is-not-tipped",
              (("tip", "tips", "tipping", "tipped", "gratuity"),
               ("plumber", "electrician", "builder", "decorator", "joiner", "carpenter", "plasterer",
                "tiler", "mechanic", "fitter", "engineer", "gas engineer", "boiler man", "handyman",
                "roofer", "scaffolder", "tradesman", "workman")),
              "No: a plumber, an electrician or a builder quotes a price for the job, and that price "
              "is the whole of it. A tip is not expected and can read as odd, so the thing worth "
              "doing instead is offering a tea and paying on time.",
              # What the trade costs is the price card's question, not this one: a tip word is what
              # makes this row an answer, so the two never meet.
              avoid=("how much does", "how much is", "cost", "costs", "charge", "charges",
                     "quote", "hourly", "day rate"),
              # "how much do you tip a plumber" is this row asked with a price in front of it, and
              # the careers entry (what the trades pay, what you need to get in) fits the same words:
              # the tip row is the one the line is asking.
              bias=4),

        entry("who-to-call",
              (("who", "who to", "which engineer", "which tradesman", "what kind of engineer",
                "anyone i can call", "someone to call",
                "who do i call", "who should i call", "who do i ring", "who should i ring",
                "who do i get"),
               ("call", "ring", "get", "get in", "tradesman", "engineer", "come out", "phone",
                "fix")),
              the_trade_to_call,
              # the reply is the trade, so the line has to be asking for one and naming something a
              # trade owns: where it names a person or an organisation instead, that line has its
              # own answer and this row must not stand in front of it
              avoid=NOT_A_TRADE_WORDS),

        # --- lighting a fire ----------------------------------------------------
        # `the living room is cold` then `how do i start the fire in the wood burner` was the search
        # hedge: `cleaning.py` names the wood burner in its hob entry's `avoid=` so the "wipe a hob"
        # answer does not take the line, and then nothing offered anything at all. Lighting a fire is
        # a job with an order to it, so it gets the steps a careful neighbour would give, and the one
        # thing that turns a stove into a chimney fire is said out loud.
        entry("lighting-a-fire",
              (("wood burner", "woodburner", "wood burning stove", "woodburning stove",
                "log burner", "logburner", "log fire", "open fire", "wood stove", "wood fire",
                "multifuel stove", "multi fuel stove", "fireplace", "woodburner stove",
                "coal fire", "stove"),
               # the asking: lighting it, keeping it in, and what it does when it is wrong. The
               # noun above is what makes a line about a stove at all, so this group holds the verbs
               # and nothing else - bare "log", "wood" and "coal" here made "how much is a log
               # burner", which is a price, a fire, and a bare "how do i" / "how to" every line in
               # the deck carries shifts what is rare and takes other answers' turns.
               ("light", "lighting", "lit", "start", "starting", "kindle", "kindling",
                "get it going", "get going", "get the fire going", "fire going", "light the fire",
                "start the fire", "going out", "goes out", "gone out", "keeps going out",
                "wont light", "won't light", "wont stay in", "smokes", "smoking", "smoulders",
                "damper", "air control", "vent", "going", "get it lit", "burner going",
                "stove going", "fire lit",
                "lay a fire", "lay the fire", "lay it")),
              "Open the air control fully, clear the grate but leave an inch of ash, and lay eight or "
              "ten sticks of kindling in a loose criss-cross with a firelighter or a twist of "
              "newspaper in the middle. Light it low down and leave the door on the latch rather than "
              "shut, so air can get in, and wait until the kindling is properly caught before you add "
              "one or two split logs - a big log laid on a small flame is how a fire goes out. Once "
              "the fire is going and the glass has cleared, shut the door and close the air down to "
              "about a finger's width; that is what stops it burning through a load in an hour. If it "
              "smokes into the room on a cold day the flue is cold, so hold a lit twist of newspaper "
              "up near the throat of the stove for a minute first. Dry wood and a swept flue are the "
              "two things that keep it easy: fit a carbon monoxide alarm in the same room, have the "
              "chimney swept once a year, and never use petrol, meths or barbecue fluid to start it, "
              "because a sooted flue is what turns a stove into a chimney fire.",
              bias=1,
              # a sweep, an installation, a price and the alarm are each their own answer, and a
              # bonfire or a fire pit is not a stove in a room
              avoid=("sweep", "sweeps", "sweeping", "swept", "chimney sweep", "flue liner",
                     "install", "installation", "fitter", "buy", "best one", "which one", "cost",
                     "price", "cheap", "worth it", "how much", "how many", "broken", "not working",
                     "wont work", "no heat",
                     "smoke alarm", "carbon monoxide", "alarm going off", "chimney fire",
                     "caught fire", "on fire", "bonfire", "fire pit", "garden fire", "barbecue",
                     "bbq", "grill", "charcoal", "smoker", "pizza oven", "candle", "hob", "pilot",
                     "boiler", "oven",
                     # a gas fire has no grate, no kindling and no damper: it is a pilot, an
                     # ignition and, if there is a smell of gas, a safety line. "my gas stove wont
                     # light" was given the wood-burner steps, which is a confident answer to a
                     # different appliance - and gas is the one thing in the house nobody should
                     # be told to take apart.
                     "gas", "gas stove", "gas fire", "gas fireplace", "gas hob", "ignition",
                     "clicking", "spark", "electric", "electric fire",
                     "outdoor", "allotment", "campfire", "stove top", "cook on", "cooking",
                     "glass", "paint", "rust", "door seal", "rope seal", "replace the")),

        # --- damp, mould, condensation -----------------------------------------
        # A bare "black" made this the answer to every line with the word in it: "i dropped something
        # on my toe and the nail has gone black" came back as scrub it with mould spray. Black is only
        # mould when it says what it is on, so the phrase is the key and the bare word is gone.
        # "should i use bleach on mould" and "does bleach kill mould" were a "Not mine to decide" and
        # a search hedge: the answer below names no surface, so the mould entry's second group - the
        # rooms and the places - never matched it. What people want is the short verdict, on what it
        # works and what it only paints over.
        entry("bleach-on-mould", (("bleach", "bleach solution", "thin bleach", "milton",
                                   "mould spray", "vinegar"),
                                  ("mould", "mold", "mildew", "kill", "kills", "killing", "dying")),
              # The first sentence has to be the verdict, and it is the one a repeated question gets
              # back (a repeat is answered with the sentence that shares most with the line, shortest
              # on a tie), so it carries bleach, mould, kill and "on" - the words the line uses.
              "Yes: vinegar is the gentler of the two and bleach at about one part to four of water is "
              "the stronger, and either kills the mould it reaches on tiles, grout, glass and the "
              "sealant round a bath - gloves on, window open, never mixed with another cleaner. On "
              "plaster, paint, wood or fabric neither does more than lift the colour, because it "
              "cannot get at mould that has grown in, so those want a mould spray, or the sealant cut "
              "out and replaced. And it is the damp that brings it back, so that is the part to fix.",
              # Bleach on a stain, on fabric, in a wash or down a drain is another entry's question, and
              # so is the mould that has gone into food. A ceiling, a wall or a bit of skirting belongs
              # to the mould entry, which finds the water the mould is living on - the right answer for
              # plaster and paint, and one whose first sentence is about the room, not a tile.
              # "whites" alone kept the bleach-it-whiter lines out, but the form table folds "white"
              # into it, so "does white vinegar kill mould" was zeroed by its own avoid and fell to a
              # shrug. Held as the phrases a person uses for the laundry instead.
              avoid=("stain", "stains", "my whites", "the whites", "in with the whites",
                     "white wash", "colors", "colours",
                     "towels", "washing machine", "in the wash",
                     "drain", "sink", "bin", "bread", "cheese", "food", "jam", "the fridge",
                     "nail", "toe", "finger",
                     "ceiling", "ceilings", "wall", "walls", "wardrobe", "skirting",
                     "behind the", "under the window")),
        entry("mould-bathroom", (("mould", "mold", "mildew", "mouldy", "moldy",
                                  "black mould", "black mold", "black spots", "black patch",
                                  "black patches", "black marks", "black staining", "black on the",
                                  # "the sealant has gone black" names no mould at all: the colour is
                                  # the complaint. Safe to key now that the second group is a surface,
                                  # so a nail that went black cannot reach it.
                                  "gone black", "going black", "turned black", "turning black",
                                  "black in the corner", "black behind the", "black round the",
                                  "black around the",
                                  # "how do i stop my bathroom going mouldy" is the plainest way to
                                  # ask about the wall, and it tied with the bathroom cleaning order
                                  # at two words each, so the cleaning won. The shape people use -
                                  # going, gone, gets, keeps getting - is the mould itself.
                                  "going mouldy", "going moldy", "gone mouldy", "gone moldy",
                                  "gets mouldy", "gets moldy", "getting mouldy", "getting moldy",
                                  "keeps going mouldy", "keeps getting mouldy", "mouldy again",
                                  "moldy again"),
                                 # "my shower has gone mouldy" is this answer, and so is the sealant
                                 # round it: the words below are the surfaces, not the food that molds.
                                 # The bare colour word used to sit here and stood in for a surface too,
                                 # so "black mould in the bedroom" matched on black+black while the room
                                 # named nothing at all; the rooms and the "is it dangerous" ask are
                                 # here now, which is what that word was doing by accident.
                                 ("bathroom", "ceiling", "ceilings", "wall", "walls", "wallpaper",
                                  "remove", "get rid", "stop", "shower", "showers", "shower cubicle",
                                  "sealant", "silicone", "grouting", "tile", "tiles", "window",
                                  "windows", "window frame", "frame", "windowsill", "corner",
                                  "corners", "bedroom", "bedrooms", "kitchen", "hall", "hallway",
                                  "loft", "attic", "cupboard", "wardrobe", "skirting", "paint",
                                  "dangerous", "harmful", "unhealthy", "bad for", "smell", "smells",
                                  "smelly", "damp", "flat", "house", "home", "room", "rooms",
                                  # The follow-up people send after the first wipe-down names no
                                  # surface and asks nothing but "and it is here again": the entry's
                                  # rooms and places never matched it, so it fell to a shrug. These
                                  # are the words a returning patch uses, and the answer already ends
                                  # on them - "if it keeps returning in the same place, that patch is
                                  # a damp problem, not dirt".
                                  "keeps coming back", "keep coming back", "comes back",
                                  "coming back", "keeps returning", "keeps coming",
                                  # "my laptop screen is mouldy" names no wall at all: the device is
                                  # the subject, and the words below let it reach the entry. What the
                                  # answer says is decided in _mould, where a device gets the gentler
                                  # wipe and its own warning about the damp behind it.
                                  "screen", "screens", "monitor", "monitors", "laptop", "laptops",
                                  "phone", "phones", "handset", "keyboard", "keyboards", "headset",
                                  "headsets", "headphones", "earbuds", "earphones", "airpods",
                                  "gasket", "gaskets", "door seal",
                                  "returns", "returning", "again", "spreading", "spread",
                                  "getting worse", "getting bigger", "keeps growing",
                                  # The colour belongs here, not in the key: a line needs a mould
                                  # word to get as far as this group, so "black mould" is mould plus
                                  # black - the plainest way people name it - while a nail that went
                                  # black names no mould at all and never reaches this entry.
                                  "black",
                                  # "mould behind the tv" says mould and a place and no surface, and
                                  # it is the plainest wall question of the lot: the place is the
                                  # surface, named by a preposition. Safe for the same reason the
                                  # colour is - the first group still has to name mould.
                                  "behind", "behind the", "above the", "under the", "underneath",
                                  "under it", "next to", "beside", "around the", "along the",
                                  "behind it", "above it",
                                  # the ask with no surface in it: "what can i do about the mould"
                                  # names no room, so it scored on the mould word alone, fell just
                                  # short and went to the boot with moulded studs. The act of asking
                                  # is enough of a second word here because the first group is already
                                  # a mould word, so none of these can carry a line on its own.
                                  "do about the mould", "do about mould", "deal with the mould",
                                  "deal with mould", "about the mould", "about mould",
                                  "with the mould", "of the mould", "the mould problem",
                                  "handle mould", "sort out mould", "the mould keeps")),
              _mould,
              # "gone black" and "turned black" are how people name mould without the word, and
              # they are how they name a bruise too: `my ankle is sprained` then `its turned black`
              # was told to wipe it with a mould spray. A line naming a body part or a bruise with
              # no mould word and nothing in the house is the body's question.
              guard=_the_black_is_not_a_body,
              # mould on food is a keeping question, not a wall to scrub, and a knock that left a
              # nail or a finger black is body's question. The fruits and vegetables below go black
              # on their own: "how do i stop my avocado going black" was taken by "going black" plus
              # "stop" and told to wipe it with a mould spray.
              avoid=("bread", "food", "cheese", "jam", "fruit", "veg", "vegetables", "milk", "meat",
                     "leftovers", "the fridge", "a fridge",
                     "nail", "nails", "finger", "thumb", "toe", "banged", "slammed", "bruised",
                     "dropped", "knocked", "hit it",
                     "avocado", "avocados", "guacamole", "apple", "apples", "banana", "bananas",
                     "pear", "pears", "potato", "potatoes", "aubergine", "aubergines",
                     # "black on the" is the plainest way to name mould on a wall, and it also reads
                     # "everything went black on the bus": a person's sight going is not a wall, and
                     # the faint it is belongs to the 111 answer, not to a mould spray.
                     "went black", "went dark", "vision", "sight",
                     # A plant that has gone black is the garden's, and the garden rows name the rot
                     # or the fungus: "why are my tomatoes going black at the bottom" matched "going
                     # black" and "bottom" here and was told to wipe it with a mould spray.
                     "tomato", "tomatoes", "tomato plant", "rose", "roses", "plant", "plants",
                     "leaves", "leaf", "blossom end", "courgette", "courgettes", "cucumber",
                     "cucumbers", "seedling", "seedlings", "cutting", "cuttings", "greenhouse",
                     # "my laptop screen keeps going black" was answered with a mould spray, because
                     # "going black" is in the key and a screen names no surface the key knows. The
                     # device words are handled where the line can be read: _mould stands down when a
                     # screen is named and no wall, window or room is, which keeps "the wall behind my
                     # monitor has gone black" as mould. The charger words below are never a wall.
                     "charger", "charging", "windows update", "reboot", "battery",
                     # The grout has its own card, and it already covers the mould in it ("for black
                     # mould in the grout, use a mould spray... sealing the grout keeps it that way").
                     # "the grout in my shower has gone blak, how do i cleen it" reached this entry the
                     # moment the slip was repaired to "black", and was told to run the fan with no
                     # word about grout at all.
                     "grout", "grouting",
                     # A tenant whose landlord will not deal with the mould is asking about the
                     # landlord, not about the scrub: "my landlord wont deal with the mould" and "my
                     # landlord is ignoring me about the mould" both got this wipe because the ask
                     # phrase names the mould, and the repair-letter answer is the one they need.
                     # So the words that make a mould line a tenancy line keep this entry out of it.
                     # Only the phrasings the repair answer can actually take are here: a bare
                     # "landlord" also reads "the mould keeps coming back and my landlord does
                     # nothing", which the repair entry does not match, and standing this one down
                     # there left the line with nothing but "I'm listening".
                     "landlord wont", "landlord won't", "landlords wont", "landlords won't",
                     "landlord refuses", "landlord refused", "landlord is refusing",
                     "landlord ignores", "landlord is ignoring", "landlord not fixing",
                     "landlord hasnt fixed", "landlord hasn't fixed", "landlord does nothing",
                     "letting agent wont", "letting agent won't", "letting agent ignores",
                     "withhold rent", "withholding rent", "rent arrears", "tenancy", "deposit",
                     "housing officer",
                     # A line asking what the law says, or whether it is legal, is a question about
                     # the landlord's duty: the scrub answers a question nobody asked, and main's
                     # hedge is the better of the two until a rights card takes it.
                     "the law", "law say", "law says", "legal", "legally", "am i allowed",
                     "is it legal", "obliged", "duty to")),
        # "Is it damp or is it condensation?" names both and asks for the difference, so neither
        # answer below fired and the line got "a plumber will spot it in minutes" (or, for "rising
        # damp or condensation", "either works, so take the one that's less fuss"). The difference is
        # what people actually want, and there is a test anyone can do at home in three days.
        entry("damp-or-condensation",
              (("damp", "damp patch", "damp wall", "damp walls", "rising damp"),
               ("condensation", "or condensation", "condensation or", "difference between",
                "which one", "what kind")),
              "Condensation is water out of the air landing on a cold surface: the windows and the outer "
              "corners are wet in the morning, it clears when the room is aired, and it comes back on "
              "cold days. A leak is a patch that grows and stays wet whatever the weather, and rising "
              "damp only runs along the bottom metre of a wall, usually with a tide mark. To tell them "
              "apart, dry a patch with a hairdryer, tape a square of cling film over it tight and leave "
              "it three days: water on the room side of the film is condensation, a wall still wet "
              "behind it is water coming through.",
              # A wet cloth, a damp cake and a damp tent are not a wall.
              avoid=("cloth", "cloths", "dishcloth", "washing", "laundry", "clothes", "towel",
                     "towels", "cake", "bread", "tent", "shed")),
        entry("condensation", (("condensation", "damp", "walls are wet", "wet walls", "walls get wet",
                                "windows are wet", "wet windows",
                                # The same complaint with the time of day in the middle of it: "the
                                # walls in my bedroom are wet in the morning" has every word but
                                # never them next to each other, so it fell to the listening reply.
                                "wet in the morning", "wet every morning", "wet each morning",
                                "wet in the mornings",
                                # the way people describe it out loud
                                "steaming up", "steamed up", "steamy", "condensating", "condensing",
                                "misting up", "misted up", "wet inside", "running with water",
                                # "fog" is the other word for it, and it reached no row that answers
                                # the inside of an ordinary window: "how do i stop my windows fogging
                                # up in winter", "my windows fog up in the morning" and "how do i stop
                                # windows fogging up" were all punts. Only the phrases are here and not
                                # the bare "fogging", so a line that names no pane still scores higher
                                # here than at the sealed-unit row.
                                "fogging up", "fogged up", "fog up", "fogs up",
                                "foggy windows", "windows fog", "window fog",
                                # The same water, frozen: "how do i stop frost on my windows" was a
                                # punt, and frost on the inside of a pane is condensation with the
                                # heating off, so it is this row's advice, not a weather forecast.
                                "frost on the windows", "frost on my windows", "frost on windows",
                                "frost on the inside", "frost inside", "frosty windows",
                                "frosted up", "windows are frosted", "windows frosted",
                                "ice on the inside", "ice on the windows", "ice inside the windows",
                                "ice on my windows"),
                               ("window", "windows", "walls", "wall", "bedroom", "stop", "inside",
                                "wet", "winter", "misty", "glass", "running down",
                                # the same water in a room that has no window named in the line:
                                # "my loft has condensation" and "the cupboard smells damp" fell
                                # to the listening reply, because the row wanted a pane or a wall
                                # and got only the word for the water.
                                # Only the places a pane or a wall is never named for: "room",
                                # "flat" and "ceiling" are in the damp-proofing and leak rows'
                                # lines ("how do i dry out a damp room" is the find-the-water
                                # answer) and adding them here took those turns.
                                "loft", "attic", "garage", "shed", "landing", "hall",
                                "hallway", "basement")),
              "Condensation comes from warm wet air hitting cold surfaces, so ventilate and keep the "
              "place a bit warmer: use the extractor fan, open a window for 10 minutes a day, dry "
              "clothes outside or in a vented dryer, and leave the heating on low rather than off and "
              "on. A dehumidifier helps in a bedroom that gets it badly.",
              # a house that mists up, not the things people look through: spectacles, a car and a
              # pan of boiling water are all different questions; a mirror has its own anti-fog trick
              avoid=("glasses", "spectacles", "goggles", "car", "cars", "van", "windscreen",
                     "motorbike", "helmet", "pot", "pan", "saucepan", "kettle", "cooker",
                     "mirror", "mirrors",
                     # A patch that climbs a wall is water coming through, not air landing on a cold
                     # surface: "the damp is spreading up the wall" was the mist-up answer because
                     # "wall" is one of the surfaces below and it scored on the same two words.
                     "spreading up", "spreading across", "up the wall", "up the walls",
                     # a sealed unit that fogs between the panes has lost its seal and the glass row
                     # below answers it: this entry is the room side of the glass
                     # "glazing" on its own is not here: the matcher reads it as the same stem as
                     # "glazed", so a bare "glazed" in the avoid shut out every single-glazed
                     # window - "how do i stop condensation on a single glazed window" was a punt
                     # while the same line with a plain "window" got the answer. The double-glazed
                     # phrases below still fence the units, and a line that says glazing without
                     # them has a failing seal word ("misted", "blown") and is the unit row's.
                     "double glazing", "double glazed", "double-glazed", "window pane",
                     "panes", "the pane", "between the panes", "sealed unit")),
        # A sealed double-glazed unit that mists up between the panes is not condensation on the
        # glass: the seal has gone and the argon and the desiccant with it. "my double glazing has
        # misted up inside" was answered with open a window and dry your washing, which cannot fix
        # it, and "what do i do about misted double glazing" was a shrug.
        entry("misted-double-glazing",
              # A bare "window" is here because a unit is usually described by the window it is in
              # ("the glass in my window is cloudy", "my window has misted up on the inside"). The
              # fog words are not bare, though: "fog" on its own means the inside of an ordinary
              # window as often as a blown unit, and "windows fogging up" and "why do my windows fog
              # up" were both told the seal had gone. Only the fog that is tied to the inside or the
              # space between the panes is this row's.
              (("misted", "misting", "misty", "mist", "misted up", "fogged up inside",
                "fogging up inside", "fogged up between", "fogging between",
                "condensation between", "cloudy", "gone cloudy", "hazy", "blown", "seal has failed",
                "seal failed", "seals have failed", "water between the panes", "wet between",
                "inside the glass", "inside the pane", "inside the panes"),
               ("double glazing", "double glazed", "double-glazed", "glazing", "window pane",
                "window panes", "the pane", "panes", "unit", "units", "window", "windows",
                "conservatory", "door", "doors", "sealed unit")),
              ("That is a failed seal, not condensation: the unit has taken in damp and the "
               "desiccant inside it is full, so no amount of ventilating, heating or a dehumidifier "
               "will clear it. The glass unit is replaced, not repaired - a glazier measures the unit "
               "and swaps it, and the frame and the handles stay, which is why it is a much smaller "
               "job than new windows, usually £80-£200 a pane fitted depending on size and glass. "
               "Some firms now drill and dry a misted unit in place for less; it works on a mild "
               "case, but a unit that has been cloudy for years is a swap. If the mist is on the room "
               "side of the glass and wipes off, that is ordinary condensation and the ventilating "
               "answer is the right one - check with a dry cloth first."),
              # a car windscreen, a bathroom mirror and a pair of spectacles are other rows, and so
              # is the condensation that wipes off the inside of an ordinary window
              # "glasses" is not in this list on purpose: the avoid words are matched loosely, so
              # "glasses" also catches "glass", and every line about the glass mists up. The
              # spectacles row does not need it here either - a pair of glasses naming no window
              # never reaches this entry.
              avoid=("spectacles", "goggles", "windscreen", "car", "cars", "van",
                     "motorbike", "helmet", "mirror", "mirrors", "kettle", "saucepan",
                     "steam", "shower", "bathroom",
                     # a window that fogs while the pans are on is steam on the glass, not a failed
                     # seal: "the windows fog up when i cook" was told the unit had taken in damp
                     "cook", "cooking", "cooked", "kitchen", "boiling", "boil", "pan", "pans",
                     "casserole", "oven", "washing", "drying clothes",
                     # A window that mists up every morning, or asking how to stop it, is the
                     # condensation question however the line is worded: "how do i stop my windows
                     # misting up" and "my bedroom window is always misted up" are not a quote for
                     # a new unit. The failed-seal answer is for mist that will not wipe off, so the
                     # words for the everyday job send those lines back to it.
                     "stop", "stops", "stopping", "prevent", "preventing", "wipe", "wipes",
                     "wiping", "morning", "mornings", "every morning", "always", "every day",
                     "every night", "each morning",
                     # the glass has to be a unit for this to be a failed seal: a single pane, a
                     # skylight and a car are other rows, and "my glasses mist up" is the
                     # spectacles one
                     "single glazed", "single glazing", "skylight", "velux"),
              bias=1),
        # A bare "how do i deal with damp" names no surface and no smell, so neither answer above
        # matched it and the line fell to the "someone qualified will spot it" fallback. Damp is a
        # cause to find, not a person to call, and the first move is the same whatever the room.
        entry("damp",
              (("damp", "damp patch", "damp patches", "damp wall", "damp walls", "damp corner",
                "damp in", "damp problem", "rising damp", "damp proof", "damp course"),
               ("deal", "get rid", "stop", "cure", "fix", "treat", "sort", "coming back", "keeps",
                "why", "how", "cause", "room", "house", "flat", "hallway", "corner", "wall",
                # "do i have rising damp", "what is rising damp", "is it serious": the same hunt for
                # the water answers all of them, and they reached the plumber fallback before.
                "have", "got", "real", "signs", "sign", "what", "mean", "means", "look", "looks",
                "like", "serious", "worry", "worried",
                # A bare "rising damp" names the subject and asks about it in two words, so the same
                # phrase in both parts is what lets the topic reach its own answer.
                "rising damp",
                # "my damp patch is getting bigger" asked the one thing this answer is for - has the
                # water found a way through - and got a shrug, because a patch that grows named none
                # of the verbs above.
                "getting worse", "getting bigger", "bigger", "growing", "spreading", "spread",
                "keeps coming back", "coming back", "returns", "returning")),
              # 110 words was more than twice the bar, and this is the answer for every damp room, so
              # it says the same thing in two moves: find the water, then dry it out.
              "Find the water before you treat the wall: a leaking gutter or downpipe, an overflow "
              "running, ground above the damp course, or a slow leak near the patch. Feel whether the "
              "wall is wet high up (a leak) or only at the bottom (rising damp). Warm it and ventilate "
              "it while you look, don't paint over it, and in a rented flat ask the landlord in "
              "writing.",
              # The cloth, the laundry and the cooking are all "damp" somewhere else, and a room that
              # is damp in winter, or wet round the windows, is the condensation answer below rather
              # than a gutter to go looking for.
              # The furniture is the smell entry's line: a wardrobe or a cupboard that smells damp is
              # about airing it and finding the cold wall behind it, and this answer's gutter, damp
              # course and survey are the outside of a house.
              avoid=("cloth", "cloths", "dishcloth", "washing", "laundry", "clothes", "towel",
                     "towels", "cake", "bread", "tent", "shed",
                     "condensation", "winter", "window", "windows", "bedroom", "steam",
                     "wardrobe", "wardrobes", "cupboard", "cupboards", "drawer", "drawers",
                     "closet", "suitcase", "mattress", "bedding", "sofa", "settee", "armchair",
                     # A car is the car's own diagnosis: "how do i get rid of a damp smell in the
                     # car" got the gutter hunt, and a wet carpet and a pollen filter are not a
                     # leaking gutter. A smell inside a room's own walls is not held out here: a
                     # damp-smelling room is this answer's line, and it is two moves long.
                     "car", "van", "boot", "camper")),
        # The place the smell is in is the key, not a bare "room": "how do i get rid of a musty smell
        # in a room" and "how do i stop my wardrobe smelling" both had an answer already waiting, and
        # the first was taken by the hotel-complaint row because "room" alone was the only word it
        # needed. The car keeps its own smell diagnosis: "my car smells damp" is a wet carpet and a
        # pollen filter, not a cold outside wall.
        # The key is the smell said with the damp: "damp" or "musty" in one group, the smell or the
        # place in the other. It is deliberately not widened to a bare "smell": a key of "smell" beside
        # any place word made this row the answer to "the garage smells" (the place-smell row's own
        # line), "my car smells of wet dog", "how do i make my house smell nice" and "the carpet smells
        # of wee" - four answers it took from rows that know the subject better.
        entry("damp-smell", (("damp", "musty", "mustiness", "mildew", "dampness", "damp and musty",
                              "musty and damp", "musty smell"),
                             ("smell", "smells", "smelling", "smelly", "whiff", "reek", "stinks",
                              "room", "house", "flat", "home", "bedroom", "living room", "spare room",
                              "sitting room", "dining room", "box room", "utility room", "en suite",
                              "wet room", "shower room", "wash room",
                              "loft", "attic", "basement", "cellar", "hallway", "landing", "stairs",
                              "wardrobe", "cupboard", "closet", "drawer", "mattress", "sofa", "settee",
                              "armchair", "carpet", "rug", "garage", "shed")),
              "A musty smell is usually damp rather than dirt: check for a leak or a cold outside wall, "
              "air the room properly and dry it out before covering anything up. Don't paint over damp "
              "patch, because it comes straight back.",
              # a room somebody is paying for is a complaint, not a damp job, and the avoid words
              # below say so by name. This row used bias=2 to outrank the hotel rows, and with the
              # key made narrower that bias only took "the room smells damp" off the hotel answer
              # the main deck expects, so it is gone.
              # a car, a towel and a machine each smell for their own reasons and have their own answers
              avoid=("hotel", "hotels", "hotel room", "guest house", "guesthouse", "bed and breakfast",
                     "b and b", "airbnb", "holiday let", "villa", "cottage", "reception",
                     "check in", "check out", "booking", "the room we booked",
                     "washing", "laundry", "clothes", "shirt", "shirts", "sheets", "towel", "towels",
                     "machine", "dryer", "car", "van", "boot", "fridge", "freezer", "oven", "bin",
                     "bins", "dustbin", "dishwasher", "sink", "drain", "plughole",
                     # every other smell has a subject of its own, and a bare "smell" in this key
                     # would take it: smoke, a pet, cooking, a shoe, a baby and a fuel each have
                     # their own answer, and a musty room is what is left.
                     "shoe", "shoes", "trainer", "trainers", "boots", "dog", "dogs", "cat", "cats",
                     "pet", "pets", "puppy", "puppies", "kitten", "kittens", "urine", "pee", "poo",
                     "sick", "vomit", "smoke", "smoking", "cigarette", "cigarettes", "cigar",
                     "fire", "burnt", "burning", "paint", "painting", "cooking", "curry", "fish",
                     "food", "garlic", "onion", "baby", "nappy", "nappies", "milk", "diesel",
                     "petrol", "exhaust", "fuel", "gas", "sewage", "chemical", "formaldehyde",
                     # what is *on* a soft thing is the soft-thing row's ("the carpet smells of
                     # wee" is the enzyme cleaner), but the soft things themselves are not stood down
                     # here: khaki-key measured that a musty sofa, rug or bathroom then reached no
                     # answer at all, because `soft-thing-smell` stands down for "musty" as well. So
                     # a musty soft thing keeps this answer as its fallback and only the smell that
                     # has a neighbour behind it stands this row down.
                     "wee", "wet patch",
                     # a wet room is the condensation rows' question, and a mould patch is the mould
                     # spray's: naming either is not asking what a musty room needs. The bathroom is
                     # not here - "musty smell in the bathroom" is a musty room, and the fixture
                     # words below are the ones with cards of their own.
                     "shower", "tiles", "grout", "toilet", "loo", "condensation",
                     "mould", "mold", "mouldy", "moldy", "damp patch", "rising damp",
                     "damp course", "landlord", "council", "letting agent", "environmental health",
                     # and the opposite question - making a room smell nicer - was the ventilate
                     # card before this row took it: "how do i make my house smell nice"
                     "nice", "nicer", "good", "better", "fresh", "fresher", "lovely", "pleasant",
                     "smell nice", "smells nice", "smell good", "smells good", "smell fresh",
                     "smells fresh", "smell better", "smells better", "smell lovely")),
        entry("roof-leak",
              # water arriving through the roof or the loft is the one home job where the next hour
              # matters, so it gets its own entry: the ceiling patch above is about a stain that may
              # be weeks old, and this is about the rain that is coming in now.
              (("roof", "roofs", "loft", "attic", "ceiling", "tiles", "slates", "roof tiles",
                "flat roof", "roof space", "chimney", "light fitting", "ceiling light", "lights",
                "landing", "hallway"),
               ("leaking", "leak", "leaks", "coming in", "coming through", "pouring", "dripping",
                "water", "rain", "raining", "wet", "soaked", "damp coming", "buckets",
                "go up", "get up", "getting up there", "get on the roof", "climb", "ladder", "safe",
                "storm", "blew off", "blown off", "missing tiles", "damaged", "tarp", "tarpaulin",
                # a ceiling that is bulging or sagging is water that is already there and heavy:
                # that is a stay-out-of-the-room answer, not the stain one
                "bulging", "sagging", "bowed", "belly")),
              _roof_leak,
              avoid=("boiler", "radiator", "washing machine", "dishwasher", "tap", "taps", "faucet",
                     "toilet", "sink", "shower", "bath", "overflow", "drain", "drains", "gutter",
                     "gutters", "downpipe", "window", "windows", "condensation", "mould", "mold",
                     "musty", "car", "van", "boat", "tent", "sofa", "roof box", "moss", "caravan",
                     # "tiles" and "damaged" are too thin on their own: a damaged bathroom tile or a
                     # kitchen floor is a tiling job, not rain coming in
                     "bathroom", "kitchen", "wall", "walls", "floor", "floors", "grout",
                     "grouting",
                     # A stain is history, not rain that is coming in now: "water stain on the
                     # ceiling" was told to cut the power and get a roofer out the same day, which is
                     # the answer for a live leak. The mark a leak left keeps damp-patch-ceiling,
                     # which says to find where it comes in; the drip keeps this one.
                     "dried", "drying out", "old"),
              guard=_a_mark_that_is_live),
        entry("damp-patch-ceiling",
              # the ceiling first: "damp" on its own is the condensation answer, and a patch that
              # spreads on a ceiling is water coming through, not warm air meeting a cold wall
              (("ceiling", "ceilings", "plaster", "paint", "skirting"),
               ("damp", "patch", "wet", "brown", "yellow", "stain", "stains", "dripping", "peeling",
                "water coming", "coming through", "blistering",
                # a dried "water mark" on a ceiling is the same old patch, and it had no row at all
                "mark", "marks", "water mark", "water marks")),
              "A brown or yellow patch on a ceiling is water, and the first job is to find where it "
              "comes in rather than paint over it. Look at what is above: a bathroom or a radiator "
              "pipe means a leak at the sealant, the trap or the joint, and an outside wall or the "
              "roof means it only grows after rain, so note whether it does. Press it with a finger - "
              "soft, crumbly plaster or a slow drip means it is live and worth turning the water off; "
              "a hard dry ring that has not moved in weeks is an old stain, which you seal with a "
              "stain block and then paint. Photograph it with the date and tell the landlord or your "
              "insurer in writing, because a patch painted over with no record is one you cannot "
              "claim for.",
              avoid=("mould", "mold", "mildew", "smell", "musty", "condensation", "window", "windows",
                     "steam", "damp proof", "rising damp", "basement", "cellar floor",
                     # a stained or painted fence is the fence's question: "should i paint or stain
                     # my fence" was told about a brown patch on a ceiling
                     "fence", "fences", "shed", "decking", "gate", "patio")),

        # --- broken glass ------------------------------------------------------
        # "a pane of glass got broken" was answered "Rotten luck.", "my window pane is cracked"
        # was "Got it. Is there anything you'd like a hand with?" and both "can i replace a broken
        # window pane myself" and "how much does it cost to replace a window pane" got the shrug,
        # so a broken window had no answer at all on main `a2dbea5`.
        entry("broken-window",
              # The window or the glass in it is one group, and what is wrong with it is the other, so
              # "a pane of glass got broken", "my window pane is cracked" and "the glass in my front
              # door is cracked" are all one question. A break word has to be there: "my window glass
              # is streaky" and "how do i stop the draught" are other answers.
              (("window", "windows", "pane", "panes", "pane of glass", "glass", "double glazed",
                "sealed unit", "glazing"),
               ("broken", "broke", "broken glass", "cracked", "crack", "cracks", "cracking", "smashed",
                "shattered", "shatters", "came out", "come out", "fell out", "blown", "gone",
                "replace", "replacing", "repair", "repairing", "fix", "fixing", "cost", "costs",
                "how much", "myself", "diy", "glazier", "board up", "make safe", "what do i do",
                "who do i call", "quote", "reglaze", "reseal", "putty")),
              _broken_window,
              # A car windscreen, a drinking glass, a mirror, a phone screen, the oven door and a pair
              # of spectacles are all their own question and none of them is a window: "my car
              # windscreen is scratched" must not get a glazier's quote, and "my glasses broke" is the
              # optician's answer.
              # A window word has to be there as well, because "glass" on its own is usually
              # something you drink out of or eat off: "how much sugar is in a glass of apple juice",
              # "how much caffeine in a glass of coke" and "what should i do with a cracked glass"
              # all took a glazier's quote (sleek-skunk, #3207).
              ask=("window", "windows", "pane", "panes", "double glazed", "double-glazing",
                   "sealed unit", "glazing", "front door", "back door", "patio door", "sash",
                   "window frame", "french door"),
              avoid=("windscreen", "windshield", "car", "cars", "van", "drinking glass",
                     # what is in the glass, and what a cracked one in the hand wants
                     "juice", "sugar", "caffeine", "calorie", "calories", "coke", "cola", "wine",
                     "beer", "water", "milk", "drink", "drinking", "drank", "pint", "whisky",
                     "whiskey", "gin", "vodka", "tea", "coffee", "glass of", "tumbler", "mug",
                     "wrap it", "bin it", "cut myself", "in my hand", "in the sink", "washer",
                     # "glasses" cannot go here: it is a loose form of "glass", so "a pane of glass"
                     # read as a pair of spectacles and the entry scored nothing at all.
                     "spectacles", "optician", "mirror", "phone", "screen", "shower screen", "shower",
                     "oven", "hob", "cooker", "stove", "log burner", "splashback", "picture",
                     "tv", "telly", "watch", "table", "fish tank", "aquarium", "shelf", "cupboard",
                     # the window that is not broken
                     "draught", "draft", "condensation", "steam", "mould", "mold", "streaky",
                     # A pane that has gone cloudy has lost its seal, not its glass: "what do i do
                     # about misted double glazing" was told to sweep up the glass and tape a bin
                     # bag over the hole. The unit row owns the seal words.
                     "misted", "misting", "misty", "mist", "cloudy", "hazy", "fogged", "fogging",
                     "smear", "smears", "clean", "cleaning", "paint", "painting", "handle", "hinge",
                     "catch", "lock", "latch", "blind", "curtain", "insulation", "double glazing quote",
                     "how much do double glazing", "windows are wet",
                     # and the window that is jammed rather than broken: "how do i fix a sticking
                     # window" carried "window" + "fix" and was answered with a glazier's quote for a
                     # smashed pane, which is the row below
                     "sticking", "sticks", "stuck", "jammed", "jams", "painted shut", "swollen",
                     "swelled", "hard to open", "hard to close", "wont open", "won't open",
                     "wont shut", "won't shut", "wont close", "won't close", "rubs", "dragging"),
              bias=1),
        # --- drains and water ---------------------------------------------------
        # "how much to fix a blocked sink" reached the brick-quantity row, because the car row had
        # stood down on "sink" and "blocked" and the bricks were keyed by "block": a blocked sink
        # is the plunger and the trap, so this row takes the tie.
        # "clog" is the other word for the same fault, and it was the one nobody had: "how do i
        # unclog a sink" was answered with the wipe-the-bowl card, "my sink is clogged" with a
        # nod ("Right. What have you tried so far?"), and "how do i clear a clogged drain" with
        # the once-a-week maintenance card. All three are the plunger and the trap.
        entry("sink-blocked", ("sink", ("blocked", "blockage", "slow", "draining", "drain", "water",
                                         "unblock", "unblocking", "plunger",
                                         "clog", "clogs", "clogged", "clogging", "clogged up",
                                         "unclog", "unclogging", "unclogged")),
              "Start with a plunger over the plughole with a little water in the bowl, then undo the "
              "trap underneath (bucket first) and pull the gunk out. A kettle of hot water with a "
              "spoonful of bicarbonate and vinegar clears the rest; chemical drain cleaner is the last "
              "resort, not the first.",
              # Water that has arrived is a leak, and water that will not leave is a blockage: the
              # same sink and the same word for water, opposite jobs. "theres water under the sink"
              # and "water under the kitchen sink" were both told to reach for the plunger, which
              # fixes nothing on a floor that is wet.
              avoid=("under the sink", "under my sink", "behind the sink", "underneath",
                     "under the unit", "under the cupboard",
                     "wet patch", "damp patch", "puddle", "puddles", "leak", "leaks", "leaking",
                     "dripping", "flood", "flooded", "soaked", "ceiling"),
              bias=1),
        # "loo" and "bog" are the same toilet, and "my loo is blocked" was only a warm
        # acknowledgement because "toilet" was the only name in the key.
        entry("toilet-blocked", (("toilet", "loo", "bog"), ("blocked", "blockage", "unblock", "flush",
                                                           "overflow", "overflowing", "plunger",
                                                           # "how do i unclog a toilet" was read
                                                           # as a blocked bowel and answered with
                                                           # fibre and a walk, which is the wrong
                                                           # end of the same word
                                                           "clog", "clogs", "clogged", "clogging",
                                                           "clogged up", "unclog", "unclogging",
                                                           "unclogged")),
              "Use a plunger with a good seal, and pour a bucket of water in from waist height rather "
              "than flushing again. If the water is rising, turn off the stopcock or lift the ball "
              "valve so it can't overflow, and never pour chemical cleaner into a blocked toilet.",
              bias=2,
              # a cistern that keeps filling after a flush is the running-toilet entry, not a blockage
              avoid=("wont stop", "won't stop", "keeps running", "stop running", "running", "runs",
                     "keeps filling", "trickling", "trickle", "hissing", "keeps topping",
                     "after flushing",
                     # "how much water does a toilet use per flush" is the litres question, and the
                     # bare word "flush" in this key was answering it with a plunger: water-use has
                     # the figure, so an amount of water stands this row down.
                     "how much water", "much water", "litres", "litre", "water use", "per flush",
                     # "after flushing" is the running-cistern tell, above; a bare "flush" stays
                     # here, because a blockage said with a flush is still a blockage - "can i
                     # flush a blocked toilet" and "a nappy has been flushed down the toilet" are
                     # both a plunger job, and standing this row down for the may-it-go question
                     # left them with a nod and no advice. The other sense is settled on the other
                     # row instead: the what-may-go-down list outranks this one on a thing flushed.
                     )),
        # "how do i stop X banging" was a haircut when X was a shutter or a loo seat, a cleaning card
        # when X was a blind, and a shrug when X was a chimney. A rattle is one job with one method,
        # so it is one row: find the part with play in it, then take the play out.
        entry("rattle-stop",
              (("shutter", "shutters", "blind", "blinds", "loo seat", "toilet seat", "window",
                "windows", "pipe", "pipes", "chimney", "flue", "gate", "gates", "fence", "fences",
                "panel", "panels", "vent", "grille"),
               ("banging", "bang", "bangs", "rattling", "rattle", "rattles", "clattering", "knocking",
                "flapping", "vibrating", "buzzing", "humming", "noisy", "noise")),
              "A bang is a part with play in it, so press and shake each end to find what moves before "
              "you buy anything. A loo seat bangs because the rubber bumpers under it have gone hard: "
              "tighten the two bolts through the hinges and fit new bumpers, which cost a couple of "
              "pounds. A blind bangs on the wall or the window when the bottom rail has nothing to "
              "rest against, so shorten the pull cord onto a cleat. A shutter or a gate in the wind "
              "wants a hook and eye or a magnetic catch holding it open. Banging in a chimney is birds "
              "or a flue that has no cowl on top, a banging pipe is water hammer, which wants the "
              "clips tightened and a clip or two more, and a fence or a gate that rattles in the "
              "wind wants the post fixing or a second bolt through the hinge.",
              # the cleaning, the bleeding, the sweeping and the draught answers are their own rows
              avoid=("clean", "cleaning", "wash", "washing", "dust", "dusty", "mould", "damp",
                     "bleed", "bleeding", "cold", "boiler", "sweep", "sweeping",
                     "draught", "draft", "slam", "slamming", "shut", "open", "broken", "cracked",
                     "won't close", "wont close")),
        # A rail is the fitting a household puts up themselves and asks about most, and nothing
        # answered it: "how do i put up a curtain rail" was a punt, while the curtain rows in the
        # cleaning table are about washing one.
        entry("curtain-rail",
              (("curtain rail", "curtain pole", "curtain rod", "curtain track", "rail", "pole"),
               ("put up", "hang", "hanging", "fit", "fitting", "fitted", "install", "fix",
                "how high", "what height", "drill", "bracket", "brackets", "level",
                # A rail that has already come down is the same two fixing points as a rail going
                # up, and it was answered with "A pencil rubber takes most scuffs off a matt
                # emulsion" (the wall-mark card, through "wall" + "off") and with "Blot, do not
                # rub" (a stain card, through "pulled out"). The words a person uses for the rail
                # coming away are the question.
                "coming off", "came off", "come off", "keeps coming off", "coming away",
                "came away", "pulled out", "pulling out", "ripped out", "torn out", "fallen",
                "fell", "fell down", "falling down", "came down", "come down", "sagging",
                "dropping", "loose", "wobbly", "won't stay", "wont stay", "not holding",
                "what fixing", "what fixings", "rawl plug", "rawlplug", "hollow wall")),
              "Mark both ends before you drill: the rail sits 10 to 15cm above the window recess and "
              "15 to 20cm past each side, so the curtains clear the glass, and check it with a spirit "
              "level because a rail two people can see is crooked. Fix into masonry or a timber stud "
              "rather than the plasterboard alone - a rail hangs all its weight on two points and "
              "pulls downwards - so find the studs with a magnet dragged along the wall, which sticks "
              "at the screw heads, or drill and use a masonry plug. Hang the curtains on the rail "
              "before it goes up, and use the last eyelet at each end.",
              # ironing or washing a curtain, a shower curtain and a rail for a towel or a coat are
              # other answers. "fallen"/"fell"/"came down" used to be fenced here too, on the guess
              # that a rail that came down was somebody else's card; it was nobody's, and the two
              # lines that say it were told how to rub a scuff off emulsion and how to blot a stain.
              avoid=("iron", "wash", "washing", "clean", "shower",
                     "broken", "tv", "television", "picture", "shelf", "coat", "towel")),
        # A window curtain that will not slide is its own job: the rod, the rings and the gliders, not
        # the liner in a shower. `shower-curtain-clinging` is the shower's row, and the two sit next to
        # each other because people use one word for both.
        entry("curtains-drag",
              (("curtain", "curtains"),
               ("sticking", "sticks", "stick", "dragging", "drag", "stiff", "jerky", "scraping",
                "wont slide", "won t slide", "wont pull", "won t pull", "hard to pull",
                "hard to open", "hard to close", "squeaking", "squeak")),
              "Rub the rod with a candle end or furniture wax, or spray it with silicone, and the rings "
              "will run again: the squeak is the rod and the ring, not the fabric. Plastic gliders go "
              "chalky and grip after a few years, so replace them, and check the brackets are not "
              "sagging in the middle, which pinches the two curtains against each other. A track gets "
              "the same treatment plus a vacuum along the slot, because fluff in the runners does most "
              "of the sticking.",
              avoid=("shower", "bath", "liner", "iron", "ironing", "wash", "washing", "clean",
                     "cleaning", "mould", "mold", "fade", "fading", "blackout", "put up", "hang",
                     "hanging", "fit", "fitting", "fallen", "fell", "came down", "buy", "length",
                     "shorten", "hem", "sew", "sewing", "blinds"),
              # the shower row beside it holds "curtain sticks" as a phrase and a bias, so a bare
              # "my curtains sticking" reached the shower first; a window curtain on a rod is the
              # commoner reading of the bare plural, so this row is the tie-break
              bias=2),
        # "leaky" is the adjective people use and it is not a form of "leak", so "how do i fix a
        # leaky tap" scored 2 on the tap alone and went to the hedge.
        entry("tap-drip", (("tap", "faucet"), ("drip", "drips", "dripping", "leak", "leaks", "leaky",
                                              "leaking", "washer")),
              _a_dripping_tap),
        # A bare "do i need a new washer" has two subjects and no way to tell them apart, so the
        # answer to both is short: the ring in a tap, or the machine. Every row that owns one of
        # them reads its own words beside the washer, and this one only the washer alone.
        entry("a-washer-two-things",
              (("washer", "washers"),
               ("new", "need", "needs", "replace", "replacing", "change", "changing", "fit",
                "fits", "size", "what size", "which size", "right size",
                # telling you they have one is the same question with half the answer given
                "have", "has", "got", "ive", "i've", "bought", "buy", "buying", "should",
                "which")),
              _a_washer_two_things,
              guard=_a_washer_with_no_other_subject,
              bias=-1),
        # The cistern that never stops filling is the most common plumbing fault in a house, and
        # main answered it with "Got it. Is there anything you'd like a hand with?". The tell is
        # where the water goes, so the answer asks the person to take the lid off and look.
        entry("toilet-running",
              # "the flush button is stuck" names no toilet at all, and the cistern's own parts
              # are the subject when the part is what has gone wrong
              # the words people use for it, in one place: "the lav keeps running" reached
              # nothing, and a toilet is a loo, a lav and a wc before it is ever a cistern
              (("toilet", "loo", "loos", "lav", "lavatory", "wc", "bog", "cistern", "pan",
                "flush button", "flush", "flushes",
                "ball valve", "ballcock", "fill valve", "flush valve", "float valve", "float"),
               ("running", "runs", "keeps running", "wont stop", "wont stop running", "stop running",
                "keeps filling", "filling", "trickling", "trickle", "constantly", "all the time",
                "hissing", "keeps topping", "stuck", "jammed", "wont go down", "wont push",
                "broken", "gone", "seized", "worn")),
              "Turn the water off at the isolation valve under the cistern, take the lid off and "
              "watch where it goes. Trickling down the back of the pan means the flush valve is not "
              "seating: feel the rubber seal for grit, and a new flapper is a couple of pounds and "
              "clips straight on. Water into the overflow or up the side means the fill valve is too "
              "high or its float has gone, so screw the level down and replace the valve if that does "
              "not stop it. A button that stays down or does nothing is the button or the syphon "
              "under it, and those are a few pounds at a hardware shop and clip in without any "
              "plumbing.",
              avoid=("blocked", "blockage", "overflowing", "smell", "clean", "cleaning", "stain",
                     "limescale ring", "brush",
                     # the hot flush is a symptom and the sweats are another card entirely
                     "hot flush", "hot flushes", "flushes at night", "sweats", "menopause",
                     "perimenopause",
                     # "i need the loo all the time" is a symptom, not a cistern: the body's line is
                     # health's uti card, so the loo that is needed rather than running is not here
                     "need the loo", "need a loo", "needing the loo", "need to loo",
                     "need the toilet", "needing the toilet", "keep needing",
                     ),
              # ... and the going half of it: "i keep running to the loo" has both words of this
              # row's key in it, and it is the runs, not the flush valve
              guard=_going_to_the_loo),
        # A toilet that leaks is not the cistern that will not stop filling: the tell is where the
        # water comes out, so this asks for that. It was reaching the constipation answer in health.py,
        # because "toilet" and "fix" were both in its key.
        entry("toilet-leak",
              (("toilet", "loo", "loos", "lav", "lavatory", "wc", "cistern", "pan", "bog"),
               ("leak", "leaks", "leaking", "leaky", "drip", "drips", "dripping", "pool", "puddle",
                "puddles", "floor", "seal", "seals", "joint", "joints", "fix", "repair", "water",
                "wet")),
              "Where the water shows tells you which seal has gone. Water on the floor at the base "
              "means the wax or rubber seal between the pan and the soil pipe - the pan has to come "
              "up, so an hour of a plumber's time. A trickle from under the cistern is the inlet "
              "connection or the coupling washer, a quarter turn with a spanner. Water in the bowl "
              "that will not stop is the flush valve. Turn the water off at the isolation valve "
              "beside the cistern first, dry everything, and watch again - and if you rent, tell the "
              "landlord in writing rather than taking the pan off yourself.",
              # a question about the colour or the smell of the water is not a leak
              avoid=("blocked", "blockage", "unblock", "plunger", "smell", "smells", "smelly", "clean",
                     "cleaning", "stain", "stains", "limescale", "brush", "brown", "brownish", "rusty",
                     "yellow", "yellowish", "green", "cloudy", "murky", "discoloured", "black",
                     "colour", "color", "taste", "tastes", "drink", "drinking", "constipated",
                     "constipation")),
        entry("tap-pressure-low",
              (("tap", "taps", "faucet", "shower", "showers", "shower head", "water"),
               ("low pressure", "no pressure", "pressure is low", "pressure has dropped", "weak",
                "weedy", "trickle", "trickling", "barely", "hardly", "dribble", "slow flow",
                # "the shower pressure is rubbish" and "the pressure is poor" are the same
                # complaint without the word low, and they were the shrug: the key wanted
                # "low pressure" and "pressure is low", never the bare noun beside a rating.
                "pressure", "rubbish", "poor", "useless", "hardly any", "no force")),
              _pressure_weak,
              # the gauge on a boiler has its own answer, and a car tyre is not a tap
              avoid=("boiler pressure", "boiler", "radiator", "tyre", "car", "blood", "oil pressure",
                     "pressure washer", "gas",
                     # drinking is not plumbing: the first arm carries the word "water", and with
                     # "barely" and "weak" in the second, "i drink barely any water" and "i hardly
                     # drink any water" were told to unscrew the aerator on the tap. A water bill
                     # and a watering can are other questions too.
                     "drink", "drinking", "drank", "thirsty", "hydrate", "hydrated", "dehydrated",
                     "bill", "bills", "water the", "cuppa", "brew")),
        # A tap that gives no water had no row at all: "the tap is not working", "the kitchen
        # tap doesnt work" and "the bathroom tap is not working" were the shrug, and before the
        # fence on `card-on-a-phone` they were told to check the phone's screen and its case. The
        # row is the tap itself, so a shower, a loo and a machine keep their own answers.
        entry("tap-no-water",
              # "water" belongs with the thing and not with the fault: the scorer wants two
              # signals from two key groups, and with water on the fault side a line that says
              # "the tap has no water" is one group twice - which is why it was a shrug.
              (("tap", "taps", "faucet", "faucets", "mixer tap", "kitchen tap", "bathroom tap",
                "hot tap", "cold tap", "the water", "water supply", "water"),
               ("not working", "doesnt work", "doesn't work", "stopped working", "no water", "none coming", "nothing comes out", "nothing coming", "wont run",
                "won't run", "wont come on", "wont turn on", "won't turn on", "cant turn on",
                "no flow", "stopped", "stops", "spits", "sputters", "splutters", "airlock",
                "dry", "dry tap", "barely", "suddenly")),
              "If it is one tap and the rest of the house runs, it is that tap's own supply: the "
              "isolation valve on the pipe under the sink is a slot-head screw, and a half turn the "
              "other way is the usual answer. With the valve open, unscrew the spout aerator and "
              "soak it in vinegar - a scaled-up aerator stops a tap dead. If every tap is dry, it is "
              "the stopcock where the mains comes in, or the supply itself, so check the water "
              "company's postcode status before you pay anyone. A tap that runs and then stops is an "
              "airlock: hold your palm over the spout and open it fully for a few seconds, or "
              "back-fill it with a jug from another tap. And if the pipe is in a cold wall in "
              "freezing weather, warm it gently with a hairdryer - never a blowtorch - with the tap "
              "left open.",
              # the other tap rows answer their own complaint, and a shower, a loo, a machine and a
              # boiler are separate faults with separate answers
              avoid=("drip", "drips", "dripping", "leak", "leaks", "leaking", "washer",
                     "pressure", "low pressure", "weak", "trickle", "limescale", "scale",
                     "shower", "showers", "loo", "toilet", "cistern", "boiler", "radiator",
                     "radiators", "washing machine", "dishwasher", "immersion", "cylinder",
                     "hot water", "cold water", "drink", "drinking", "water bill", "meter",
                     # "watering" is not here: the avoid list matches stems, so it also
                     # matched "water" and a dry tap was a shrug all over again
                     "outside tap", "garden tap", "hosepipe", "hose",
                     # "the tap to pay doesnt work" is the phone, not the plumbing: the phrase
                     # names the payment before it names the tap
                     "tap to pay", "tap and pay", "to pay", "apple pay", "google pay",
                     "contactless", "card machine", "phone", "wallet", "debit card",
                     "credit card", "bank card",
                     # a tap that is dry is this row; what the water in it is like is the water
                     # rows' question, and every one of those says "tap water" - safe, cloudy,
                     # hard, where it comes from, why it smells - so the phrase alone separates
                     # them, and the tap has to name a fault to reach this row at all
                     "tap water")),
        entry("limescale", (("kettle", "limescale", "scale", "tap", "shower head", "showerhead"),
                            ("descale", "clean", "white", "fur", "build", "rid", "remove",
                             "blocked", "blocking",
                             # "clogged" is how a scaled-up head or tap is described, and it was in
                             # no part of this row: "the shower head is clogged with limescale" was
                             # a shrug
                             "clogged", "clogging", "spray", "holes", "weak",
                             # the remedy is asked for as an ask, and none of the words above is
                             # in "what can i do about limescale": the row was not reached at all
                             # (the water softener's fault row keys "still limescale", so the bare
                             # word named two rows and the one-word retry withheld it), and the
                             # everyday remedy line went to a search hedge (#6283). A remedy row
                             # answers "what can i do about X" in its own right.
                             "what can i do", "do about", "what can i use", "anything for",
                             "anything to", "how do i stop", "how to stop", "keeps coming",
                             "coming back", "comes back", "get it off", "get rid of it",
                             # the same ask in the other words people use for it: main keys the
                             # first list, and these are what was missing from it
                             "what do i do", "what should i do", "deal with", "get rid",
                             "anything i can do", "do about it", "cope with")),
              "Soak the scaled part in half water, half white vinegar, or a spoonful of citric acid in "
              "water: boil it in the kettle and leave it an hour, or tie a bag of it round a shower "
              "head or tap for an hour. Rinse twice afterwards, and do it again whenever it furs up.",
              # The ask words above are general, so they pair with any subject this row carries,
              # and the tap is one: "what can i do about my dripping tap" and "... leaking tap"
              # got a vinegar soak for a worn washer (#7242 review). Dripping, leaking, a washer
              # and the water-pressure words are the plumbing rows' whatever else the line says.
              # The kettle has its own rows and they say more, so it stands down for those too.
              avoid=("drip", "drips", "dripping", "dripped", "leak", "leaks", "leaking", "leaked",
                     "washer", "washers", "cartridge", "cartridges", "plumber", "valve",
                     "no hot water", "water pressure", "blocked drain", "drains",
                     "kettle", "kettles", "boiler", "boilers", "steam iron", "washing machine",
                     "dishwasher", "coffee machine",
                     # "scale" means scale insects in a garden, and "what can i do about the
                     # scale on my plants" was a vinegar soak for them (@steward-maroon-mink,
                     # #7242). Anything growing stands this row down.
                     "plant", "plants", "garden", "gardening", "insects", "aphids", "leaves",
                     "leaf", "soil", "compost", "lawn", "houseplant", "houseplants",
                     "orchid", "orchids", "fern", "fern fronds")),
        # "why does my kettle get limescale" and "my kettle is scaled up" are asks about the cause,
        # and no key carried "why" or "get", so they were answered with a shrug. This entry is keyed
        # on the scale itself rather than on the remedy, so the cause leads and the descale follows.
        # The kettle has its own answer now (descale-kettle, #820), so it is left out of here: this
        # is the cause for the rest of the scale in a house - taps, the shower head, an iron, stains.
        entry("limescale-why", (("limescale", "scale", "scaled", "scaling", "fur",
                                 "furred", "furry", "white stuff", "white marks", "chalky marks",
                                 "chalky", "hard water",
                                 # the sentence people actually write: "my water is hard and
                                 # leaves marks" had no row at all, because "hard water" is not in it
                                 "water is hard", "water hard", "water is so hard",
                                 "water is very hard", "water tastes hard",
                                # the tap wording without the scale word: "hard water stains on the
                                # taps" is the same question, and the cleaning row hands it on
                                "hard water stain", "hard water stains"),
                                ("tap", "taps", "shower", "shower head", "showerhead",
                                 "iron", "steam iron", "washing machine", "dishwasher", "water",
                                 # "how do i prevent limescale" asks how to keep it away, and the
                                 # remedy card only says how to soak it off; this row ends with
                                 # the filter jug and the scale reducer that cut down how often
                                 # it comes back. "stop" is not here: the remedy card already
                                 # answers "how do i stop limescale".
                                 "prevent")),
              ("Hard water is the reason: it carries dissolved calcium and magnesium, and they are "
               "left behind as a chalky scale whenever the water boils away or dries on a surface. "
               "Soak the scaled part in half water, half white vinegar, or a spoonful of citric acid "
               "in water - boil it in the kettle and leave it an hour, or tie a bag of it round a "
               "shower head or tap for an hour - then rinse twice. A filter jug or a scale reducer "
               "cuts down how often it comes back."),
              # "kettling" is a form of "kettle" as far as the matcher is concerned, so naming it
              # here turned the kettle lines off; the boiler's own entry wins on specificity.
              # Water on hair is a different question with a different answer (a chelating shampoo),
              # and scale on a kettle says nothing about it, so the hair lines keep whatever they had.
              # A question about whether the hardness is bad for a person is not a question about
              # the scale: "is hard water bad for you" was this row's descaling recipe, and the
              # health half is `drinks.hard-water`.
              avoid=("kettle", "kettles", "boiler", "heating", "radiator", "radiators", "fish", "skin",
                     "weigh", "weight", "muscle", "diet", "recipe", "flour", "sugar",
                     "hair", "shampoo", "conditioner", "scalp",
                     "bad for you", "bad for me", "good for you", "safe to drink", "is it safe",
                     "harmful", "dangerous", "kidney", "kidneys", "drink it", "drinking",
                     "health", "healthy", "formula", "baby", "babies", "softener")),
        # Brown marks in a bathroom are iron, not the calcium the scale answer is about, and the leak
        # answer had them until the leak row stood down for the rust words: "how do i get rid of rust
        # stains off the shower" was told to look for a damp patch under the tray. Iron stains are
        # lifted by the same acid and made permanent by the same bleach, so they get their own row
        # rather than a sentence the white-scale lines would have to carry too. The kitchen tools keep
        # their own rust answer, and a rusty bike, nail or gate is none of these words.
        entry("rust-marks",
              (("rust", "rusty", "rusted", "rust stain", "rust stains", "rust marks"),
               # the surfaces the iron sits on, and no word for the wash: "my washing machine has
               # rust marks" is the drum and the seal, and "rust stains on my white shirt" is a stain
               # on a garment. A reviewer found the bathroom card taking both.
               # "tiles" is spelled by "tile" through the word forms, and the bare plural here scored
               # the same point as the grout row on "how do i clean the grout between my tiles"
               # "tile" and "grout" are not here: a key word is counted for rarity across every
               # row, and naming them in this surface group made "grout" common enough that the
               # grout answer lost "how do i whiten grout in the shower" to the leak row. Rust on a
               # joint is still reached by "shower" or "bathroom" in the same line.
               ("shower", "bath", "sink", "basin", "toilet", "glass",
                "screen", "bathroom", "plughole", "plug hole", "patio", "paving", "paving slabs",
                "drive")),
              ("Brown marks are iron rather than the calcium of scale, from a steel screw or fitting, "
               "a chip in the enamel, or iron in the water, and the acid that lifts scale lifts rust "
               "too: white vinegar or a citric acid paste, left ten minutes and rinsed. Never bleach, "
               "because it sets rust into the surface, and never wire wool, which leaves specks of "
               "steel behind to rust again. If it keeps coming back, find the steel that stays wet - "
               "a screw, a shower rose, the frame of the screen - and dry it or replace it."),
              # a rusty baking tray, a rusty bike and a rusty gate are other answers
              avoid=("tray", "trays", "tin", "tins", "knife", "knives", "cutlery", "pan", "pans",
                     "bike", "bicycle", "chain", "car", "van", "gate", "nail", "nails", "screwdriver",
                     "tools", "tool", "garden furniture", "barbecue", "bbq",
                     "washing machine", "washer", "drum", "seal", "laundry", "clothes", "shirt",
                     "shirts", "fabric", "whites", "white shirt")),

        # How long a kettle takes is a different question from what is wrong with one, and nothing
        # answered it: "how long does a kettle take to boil" was a shrug, and "why does my kettle
        # take so long" a shrug too. Two entries, because the first wants a number and the second
        # wants a cause, and the words that belong to the descale and running-cost answers are in
        # both avoids so those lines keep the answer they had.
        entry("kettle-boil-time",
              (("kettle", "kettles"),
               ("how long", "long does", "minutes", "take", "takes", "time", "quick",
                "quickly", "fast", "how many")),
              "About 45 seconds for one mug and around 3 minutes for a full 1.7-litre kettle in a 3kW "
              "one, so boiling only what you are going to drink is both quicker and cheaper. A 2kW "
              "kettle takes roughly half as long again.",
              ask=("how long", "minutes", "take", "takes", "time", "quick", "quickly", "fast",
                   "how many"),
              # "kettling" is a loose form of "kettle" to the matcher (see limescale-why), so the
              # boiler's noise word cannot be named here; "boiler" and "noise" are enough.
              # a kettle's *life* is the appliance-life row: "how long does a kettle last" says
              # "how long" and names a kettle, so without these words this row took it and answered
              # with boiling times. "last" in the sense of duration of boiling ("how long does it
              # last once boiled") has no kettle word, so nothing good is lost here.
              avoid=("last", "lasts", "lasting", "lifespan", "life span", "life expectancy", "years",
                     "descale", "descaleing", "limescale", "scale", "scaled", "fur", "furred",
                     "noise", "noisy", "boiler", "heating", "cost", "costs",
                     "pence", "electricity", "energy", "bill", "cheaper", "leak", "leaking",
                     "broken", "not working", "switch", "element", "fill", "capacity",
                     # how long one lasts, and whether to replace it, is the appliance-life
                     # question rather than a filling one. Main already stands "last" and "years"
                     # down here; the branch's extra words are merged in beside them.
                     "lifetime", "life", "replace", "replacement", "new kettle", "worth it",
                     "how long do they", "how long should", "keep going", "buy") + JOB_GUARD,
              # the "how many minutes" cooking follow-up entry scores the same as this one on the
              # line, and it won the tie: a named appliance outranks it.
              bias=2),
        # A kettle that smells is a different fault from one that is slow: "why does my kettle smell"
        # was a hedge and "my kettle smells of plastic" reached the burning-brakes answer.
        entry("kettle-smell",
              (("kettle", "kettles", "boiled water", "water in the kettle"),
               ("smell", "smells", "smelly", "smelling", "stink", "stinks", "odour", "odor",
                "taste", "tastes", "tasting", "musty", "earthy", "metallic", "plastic",
                "chemical", "fusty")),
              "A smell from a kettle is nearly always scale or water left standing in it: fill it "
              "with equal parts water and white vinegar, boil it, leave it half an hour, then boil "
              "fresh water and tip it away twice. A new kettle's plastic smell fades after a few "
              "boils; a musty one means water has sat in it, so empty it each night. If the taste "
              "still comes through, filter the water.",
              # the timings, the scaling noise, the electricity and the descale method are their own
              # answers, and a boiling-water burn is a safety question
              avoid=("how long", "minutes", "cost", "costs", "electricity", "bill", "noise",
                     "noisy", "boiler", "burn", "burnt", "scald", "spilled", "spilt",
                     "descale", "limescale", "scale", "fur", "leak", "leaking"),
              bias=2),
        entry("kettle-slow",
              (("kettle", "kettles"),
               ("slow", "slowly", "slower", "taking so long", "takes so long", "takes ages",
                "taking ages", "forever", "why")),
              "The element has to heat through limescale before it reaches the water, so a badly "
              "scaled kettle can take twice as long - vinegar or citric acid brings it back to speed. "
              "Past that, a full kettle takes longer than a mugful, a 2kW kettle is about half the "
              "speed of a 3kW one, and very cold water is slower than water that has stood.",
              ask=("why", "slow", "slowly", "slower", "long", "ages", "forever", "takes"),
              avoid=("boiler", "noise", "noisy", "bang", "banging", "rumbling",
                     "broken", "not working", "switch", "element", "cost", "costs", "cheaper",
                     "energy", "bill", "descale", "descaleing", "limescale", "scaled", "scale",
                     "removing", "rid of", "fur", "furred", "furry", "white stuff", "chalky",
                     # a smell and a taste are not speed: "why does my kettle smell" was taking
                     # this answer about limescale slowing it down
                     "smell", "smells", "smelly", "smelling", "stink", "stinks", "odour", "odor",
                     "taste", "tastes", "tasting", "funny", "metallic", "plastic"),
              # A cause word in the line beats the how-long entry, which would otherwise take
              # "why does my kettle take so long" for the 3-minute answer.
              bias=3),
        # A frozen pipe is a job on the pipe, not on the boiler or the heating, and "freezing" is
        # the weather word in "it's freezing out": the pipe has to be named for this answer.
        entry("pipes-freezing", (("pipe", "pipes", "plumbing", "stopcock"),
                                 ("freeze", "frozen", "freezing", "froze", "freeze up",
                                  "froze up", "frozen solid", "thaw", "burst", "lagging",
                                  "lag", "split", "stop tap", "stop valve", "water off")),
              _pipes,
              avoid=("boiler", "radiator", "central heating", "car", "windscreen", "screen wash",
                     "freezer", "food", "vegetable", "veg", "meat", "bread", "cake", "bake",
                     "baking", "shoulder", "fingers", "hands", "feet", "paddling pool")),
        # "how do i drain the pipes" and "where is my stopcock" were the plumber shrug, and the two
        # travel entries took the water-off lines, so this entry names the job rather than the subject:
        # the stopcock, the valve and the words for switching it off. "Water" alone is not a key here -
        # that is the tap-water question and it belongs to travel.
        entry("water-shutoff",
              (("stopcock", "stop tap", "stop valve", "isolating valve", "water main", "mains water",
                "water supply", "water off", "shut the water", "shutting the water",
                "shut off the water", "shutting off the water", "turn the water", "turning the water",
                "turn off the water", "turning off the water", "switch the water off",
                "drain the pipes", "draining the pipes", "drain the system", "draining the system",
                "isolate the water", "stop the water",
                # A bare "keeps running" or "wont stop running" names no subject at all, and one of
                # them was the whole first part of this key, so "my nose keeps running" and "my tap
                # keeps running" reached the stopcock on the verb alone. The supply is named instead,
                # and the verb only counts when the water is the thing that runs: the nose, the tap,
                # the toilet and the cistern all keep their own running lines.
                "water keeps running", "water keeps coming", "water wont stop", "water won't stop",
                "water wont stop running", "water won't stop running", "water is running",
                "water runs", "water running", "running water", "pipes keep running"),
               ("where", "find", "locate", "how", "turn", "turning", "shut", "shutting", "off",
                "on", "drain", "draining", "wont", "won't", "keeps", "still", "stop", "running",
                "leaking", "flood", "flooded", "valve", "mains", "supply", "house", "flat",
                "kitchen", "sink")),
              _water_off,
              bias=3,
              # Drinking it, it not being safe, the water in a boiler and the water in a pool are all
              # different questions, and a fish tank and a garden water butt have their own. A loo that
              # will not stop filling, a dripping tap and a dripping shower are each a washer or a
              # valve, and "the toilet wont stop running" was the complaint this entry would otherwise
              # read as a burst pipe. "Abroad" and "holiday" are not avoided: the key needs the
              # stopcock or the words for turning the water off, which a drinking-water question never
              # has, so "how do i shut the water off before a holiday" is this answer and
              # "is the water safe abroad" stays with travel.
              avoid=("drink", "drinking", "safe to drink", "taste", "tastes", "brown", "smelly",
                     "boiler", "radiator", "heating", "filtr", "filter", "softener", "limescale",
                     # "rinse the rice until the water runs clear" is a cooking instruction, and
                     # the key's "water runs" phrase took it while the rice-rinse row in the
                     # cooking table that answers it lost by one point. Whatever the line is
                     # rinsing is the word that says which water it is, so the food and the verb
                     # name their own rows.
                     "rinse", "rinsing", "rinsed", "rice", "pasta", "lentils", "quinoa",
                     "chickpeas", "beans", "noodles", "spinach", "greens",
                     # "our hot water runs out quickly" is the cylinder emptying, not the stopcock:
                     # the key's "water runs" phrase took it on bias, and the answer was where the
                     # mains tap is. The hot water rows below take it.
                     "hot water", "hot tap", "hot taps", "immersion", "cylinder",
                     # a water heater or an immersion has its own valve or switch, so the mains
                     # stopcock is the wrong tap for it
                     "heater", "immersion", "cylinder", "hot water tank",
                     "pool", "swimming", "paddling", "fish tank", "aquarium", "water butt", "garden",
                     "plants", "lawn",
                     # "keeps running" is the tap that will not stop, but a phone or an app that
                     # "keeps running" has nothing to do with the mains: "i keep running out of
                     # storage on my phone" got the stopcock on main.
                     "phone", "phones", "app", "apps", "storage", "memory", "battery", "laptop",
                     "computer", "tablet", "printer", "software", "update", "download", "wifi",
                     # holding the water back is this entry; letting it go slowly is the trap
                     # under the plug hole: "how do i stop the water draining slowly out of the
                     # sink" was sent to the stopcock, and the answer was which way to turn it.
                     "draining", "drains", "drain", "drainage", "plughole", "plug hole",
                     "u bend", "blocked", "unblock",
                     "internet", "screen", "data", "background",
                     "toilet", "toilets", "loo", "loo", "cistern", "ballcock", "flush", "flushing",
                     "dripping", "drips", "drip", "shower", "bath", "bathroom")),
    ]
