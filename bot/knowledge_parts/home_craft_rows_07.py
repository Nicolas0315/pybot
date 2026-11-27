"""Rows 7 of 10 of `home_craft.entries()`: `fence-panel` .. `how-often-to-defrost`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _a_child_or_a_telling,
    _the_kitchen_stuff_is_a_take_up,
)


def rows():
    from ..knowledge.home import (
        APPLIANCE_DOOR_WORDS, BODY_WORDS, COST_WORDS, FIRST_NIGHT_BOX, JOB_GUARD, LIFE_ASK,
        LIFE_GUARD, LIFE_NAMES, NOT_A_FENCE_JOB, RUNNING_WORDS, _a_fence_is_named, _lifespan,
        _running, entry, the_stomach_is_what_it_is_about
    )
    THE_APPLIANCE_ITSELF = (
        "my fridge", "the fridge", "our fridge", "fridge is", "fridge not", "fridge too",
        "fridge door", "fridge keeps", "in the fridge", "fridge cold",
        "my freezer", "the freezer", "our freezer", "freezer is", "freezer not", "freezer cold",
        "in the freezer", "freezer door",
        "my oven", "the oven", "our oven", "oven is", "oven not", "oven too", "oven on",
        "in the oven", "oven door", "fan oven", "oven cold",
    )
    return [
        # A fence is not a hinge: "fence panel blew down" and "the back fence is broken" were both
        # getting the gate-hinge answer, and the how-to lines got a shrug. The fault and the fence
        # part are both in the line, so the answer is the repair. Height, ownership and treating are
        # three other questions about the same object, so each has its own row.
        entry("fence-panel",
              (("blew down", "blown down", "blew out", "blown out", "came off", "come off",
                "came out", "come out", "fell out", "fallen out", "fell down", "fallen down",
                "knocked down", "knocked out", "loose", "loosened", "wobbly", "wobbling",
                "broken", "broke", "snapped", "split", "damaged", "rotten", "rotted",
                "repair", "fix", "mend", "replace", "put back", "falling out",
                "keeps falling", "keeps coming", "blew over", "blown over", "fell over",
                "fallen over", "blowing down", "blowing over", "blow down", "blow over",
                "blew off", "blown off"),
               ("fence panel", "fence panels", "panels", "panel of fence", "panel of the fence",
                "fence", "fencing", "fence boards", "fence board", "feather edge", "closeboard",
                "gravel board", "gravel boards", "arris rail", "fence rail", "picket fence",
                "trellis")),
              "A blown-down panel is usually the panel, not the posts: lift it back between the posts "
              "and screw it to the rails through the post, two 65mm galvanised screws per rail, "
              "rather than just slotting it in - or fit a new panel of the same width. If boards have "
              "come off, feather-edge boards go back on with galvanised nails, each overlapping the "
              "last by about 25mm, and check the gravel board the panel sits on first, because a "
              "rotted one lets the whole panel drop. If panels keep going in wind, leave a 25mm gap "
              "under the panel so the wind passes through instead of pushing.",
              ask=("fence", "fencing", "fence panel", "fence panels", "panel", "panels",
                   "gravel board", "feather edge", "closeboard", "picket", "trellis"),
              # a fence key word here is a fence, so a repair word settles it; the bare "fence"
              # key is shared with the height and ownership rows and a tie went to the wrong one
              bias=1,
              # height, ownership and treating are the other three fence questions, and the cost of
              # one is in costs.py - none of them wants the repair method
              avoid=NOT_A_FENCE_JOB + ("how tall", "how high", "tall can", "high can", "maximum height",
                     "max height", "height limit", "planning", "planning permission",
                     "boundary", "who owns", "whose", "who is responsible", "who pays",
                     "who has to pay", "deeds", "title plan", "my neighbour", "my neighbor",
                     "neighbour says", "neighbor says", "neighbours fence", "neighbor's fence",
                     "neighbour's fence", "neighbours fence", "how much", "cost", "costs",
                     "price", "prices", "quote", "cheapest", "treat", "treating", "treatment",
                     "stain", "staining", "paint", "painting", "painted", "preserver",
                     "preservative", "creosote", "fence spray", "spray",
                     # A panel that keeps going is a question about why, not about this panel: the
                     # windproof row answers it. Without these, "how do i stop my fence blowing
                     # down" and "keeps blowing down" came here and the windproof row could never
                     # win the line it exists for.
                     "stop my fence blowing", "stop the fence blowing", "stop it blowing",
                     "stop blowing down", "keeps blowing down", "keeps blowing over",
                     "blowing down again", "windproof", "wind proof", "keep the fence up",
                     # a prevention question, not a repair one: "how do i stop my fence rotting" is
                     # the treating row, and a bare "rot"/"rotting" is not in this row's key, so it
                     # loses on covered words without an avoid - which would also stand this row
                     # down for "the gravel board has rotted and the panel has dropped", the line
                     # its own answer names the gravel board in
                     "stop my fence rotting", "stop it rotting", "stop the fence rotting",
                     "prevent rot", "rotting again")),
        entry("fence-post",
              (("rotted", "rotten", "rot", "rotting", "wobbly", "wobbling", "leaning",
                "leaned", "loose", "loosened", "sinking", "sunk", "moves", "moving",
                "rocking", "broke", "broken", "snapped", "replace", "repair", "fix",
                "strengthen", "concrete"),
               ("fence post", "fence posts", "gate post", "gatepost", "fence", "fencing",
                "post", "posts")),
              "A post that has rotted or gone loose at the bottom wants replacing, not bracing: dig it "
              "out and set a new 100mm post 600mm into the ground, prop it plumb, and fill the hole "
              "with Postcrete poured dry and watered. If only the bottom has gone, cut the post off "
              "above the rot and bolt a galvanised repair spur onto the sound timber. Line the new "
              "post up with its neighbour before the concrete sets, and stand it on a gravel board or "
              "a slate so the base is not sitting in wet soil.",
              ask=("fence post", "fence posts", "gate post", "gatepost", "fence", "fencing",
                   "post", "posts"),
              bias=1,
              avoid=NOT_A_FENCE_JOB + ("post office", "post a letter", "letter", "parcel", "delivery", "mail",
                     "blog", "logged", "job", "position", "applying", "apply", "instagram",
                     "facebook", "tiktok", "photo", "photos", "comment", "review", "how tall",
                     "how high", "planning", "boundary", "who owns", "whose", "how much",
                     "cost", "costs", "price", "quote", "treat", "treating", "stain",
                     "staining", "paint", "painting", "preserver", "creosote")),
        entry("fence-treat",
              (("treat", "treating", "treatment", "stain", "staining", "paint", "painting",
                "painted", "preserver", "preservative", "creosote", "weatherproof",
                "waterproof", "protect", "protecting", "seal", "sealing", "varnish",
                "oil it", "last", "how often", "how long",
                # "how do i stop my fence rotting" and "the fence is rotting" are treating
                # questions - the rot the treatment prevents, or the board to replace
                "rot", "rotting", "rown", "gone soft", "soggy"),
               ("fence", "fencing", "fence panels", "fence panel", "feather edge", "closeboard",
                "gravel board", "trellis", "shed")),
              "Treat bare fence timber every two or three years, on a dry day with no rain forecast "
              "for 24 hours, and brush it on along the grain rather than flooding it. A water-based "
              "shed-and-fence preserver is fine for most fences and dries in a couple of hours; a "
              "solvent one soaks deeper but smells for days. Do the bottom edge of the boards and the "
              "cut ends, which is where the water gets in, and replace a rotted gravel board instead "
              "of treating it. A stain sinks in and does not peel, which is why it beats paint on a "
              "fence.",
              ask=("fence", "fencing", "fence panel", "fence panels", "trellis", "shed",
                   "feather edge", "closeboard", "gravel board"),
              # a fence that is rotting with no post named is the treating question, and the post
              # row reads "rot" too; naming a post still outranks this on covered words
              bias=2,
              avoid=NOT_A_FENCE_JOB + ("how tall", "how high", "planning", "boundary", "who owns", "whose",
                     "how much", "cost", "costs", "price", "quote", "blew down", "blown down",
                     "blew out", "blown out", "came off", "fell down", "fell out", "rotted post",
                     "fence post", "gate post", "paint a room", "paint the room", "painting a room",
                     "decorating", "wall", "walls", "door", "doors",
                     # a panel that has dropped is the panel answer, which names the rotted gravel
                     # board under it: treating is the question when the timber is still up
                     "gravel board", "dropped", "dropping", "sagging", "fallen", "fell out")),
        entry("fence-height",
              (("how tall", "how high", "tall can", "high can", "tallest", "highest",
                "maximum height", "max height", "height limit", "planning permission",
                "planning", "can i build", "can i put", "can i put up", "put up a fence",
                "put a fence up", "allowed", "legal",
                # the limit said as a measurement: "can i put up a fence 2 metres high" was the
                # build card, and once the build row stood down on the height words it was the
                # post hole. The number is this row's own signal.
                "metres high", "metre high", "metres tall", "metre tall", "feet high",
                "foot high", "2 metres", "2m high", "six foot"),
               # a hedge has its own law (the high-hedges rules), so it is not this row's
               ("fence", "fencing", "fence panels", "fence panel", "wall", "garden wall")),
              "In England and Wales a fence or a garden wall can be 2 metres high without planning "
              "permission, or 1 metre where it is next to a road, footpath or driveway; conservation areas, listed "
              "buildings and some new estates have stricter rules, so ring the council's planning "
              "desk before going higher. On a boundary you also want the neighbour's agreement, "
              "because a fence over 2 metres can be complained about as a nuisance even where the "
              "height itself is allowed.",
              ask=("fence", "fencing", "fence panel", "fence panels", "wall", "garden wall"),
              avoid=NOT_A_FENCE_JOB + ("how much", "cost", "costs", "price", "quote", "blew down", "blown down",
                     "blew out", "blown out", "came off", "fell down", "repair", "fix", "replace",
                     "treat", "treating", "stain", "staining", "paint", "painting", "preserver",
                     "creosote", "rotten", "rotted", "wobbly", "loose", "boundary fence is",
                     "who owns", "whose", "who pays", "who has to pay", "deeds",
                     # A count is the quantity rows' question, whatever height came with it:
                     # "how many blocks for a garden wall 6 metres long and 1 metre high" was
                     # answered with the 2 metre planning limit.
                     "how many blocks", "how many bricks", "how many slabs", "how many tiles",
                     "how many panels", "how many posts", "how many boards", "how many sheets",
                     "how many bags", "how many rolls", "how many metres of")),
        # "what is a gravel board for" was a shrug: the board is the part of a fence that keeps the
        # panel out of the wet, and nobody knows what it is until they have had to replace one.
        entry("fence-gravel-board",
              (("gravel board", "gravel boards", "gravelboard", "gravelboards", "gravel boarding",
                "gravelboard height", "gravel boards keep"),
               ("what", "whats", "why", "for", "need", "use", "useful", "high", "height",
                "ground", "panel", "panels", "post", "posts", "fence", "fences", "sit", "sits",
                "fit", "fitted", "rot", "replace")),
              "A gravel board is the timber along the bottom of the run, and its job is to hold the "
              "panel up out of the wet ground so the bottom rail does not rot: it sits on the soil or "
              "in a slotted concrete board, with the panel fixed above it. Set the top of a timber "
              "board about 25mm above the ground and leave the panel 50mm clear of it, so air gets "
              "between the two. A slotted concrete gravel board lets you slide a rotten board out "
              "without taking the panel down.",
              bias=1,
              avoid=NOT_A_FENCE_JOB + (
                     "how much", "cost", "costs", "price", "quote", "how many", "how long",
                     "who owns", "whose", "deeds", "planning", "how tall", "how high can",
                     "how deep", "depth", "postcrete", "how far apart", "spacing", "how thick",
                     "put up", "build", "install", "treat", "treating", "stain", "paint",
                     "painting", "blew", "blown", "fell", "fallen", "leaning", "wobbly")),
        # "how do i put up a fence", "how do i build a fence" and "where do i start with a new
        # fence" are the build question, and "put up a fence" was in the owner's key: the deeds
        # answer came back for a person who wanted to know where to dig.
        entry("fence-build",
              (("how do i put up a fence", "how to put up a fence", "how do i put up my fence",
                "put up a fence myself", "put a fence up myself", "how do i build a fence",
                "how to build a fence", "how do i fence", "fence my garden", "fencing my garden",
                "how do i fence off",
                # "where do i start" and "how long does it take to build" on their own are not a
                # fence: the bare phrase answered "where do i start with my essay" and the plain
                # "where do i start" with the posts and the string line. The subject has to be in
                # the line, and the whole phrase is what carries it.
                "where do i start with a fence", "where do i start on a fence",
                "where do i start with my fence", "where do i start on my fence",
                "where do i start with the fence", "where do i start on the fence",
                "where do i start with the fencing", "where do i start with fencing",
                "where do i begin with a fence", "where do i begin with my fence",
                "where do i begin with the fence", "where to start with a fence",
                "where to start with my fence", "where do i start with a new fence",
                "where do i start with fence panels",
                # the subject can sit before the where-phrase instead of after it: "i want to put up
                # a fence where do i start" and "i want to build a fence where do i start" have no
                # "how do i" and no "where do i start with", so the where-phrase fence words above
                # missed them and the build card was the plan reply. The verb and the fence are
                # enough, wherever they sit in the line.
                "build a fence", "build my fence", "build the fence", "building a fence",
                "put up a fence", "putting up a fence", "put a fence up", "putting a fence up",
                "erect a fence", "install a fence", "installing a fence", "new fence",
                "want a fence", "put in a fence", "putting in a fence",
                "how long does it take to put up a fence", "how long to put up a fence",
                "how long does it take to build a fence", "how long does building a fence take",
                "what do i need to put up",
                "what do i need for a fence", "can i put up a fence", "can i build a fence",
                "can i put a fence up", "how do i install a fence", "how do i erect a fence",
                "how do i put a fence up", "do it myself", "is it hard to put up a fence",
                "is it hard to build a fence", "is it easy to put up a fence",
                "hard to put up a fence"),
               ("fence", "fences", "fencing", "garden", "panel", "panels", "closeboard",
                "boundary", "posts"),
               # a build line is asked as "how do i", "how long" or "can i": the ask itself is the
               # third part, which is what lifts these over the treating and height rows that share
               # the word "fence" and tied with the whole-fence answer at five
               # "where do i" and "where to" were here and every "where do i start with my
               # garden" matched them on the word garden alone: a bare where-phrase is not a
               # fence, so the fence phrases above carry that half now.
               ("how do i", "how to", "how long", "how much time", "can i", "what do i",
                "is it hard", "is it easy")),
              "Set the posts first: a string line between the two end posts keeps the run straight, "
              "then each post goes 600mm deep and 1.8m apart in concrete, braced for a day. The gravel "
              "boards go on next and the panels screw through their rails into the posts, one post's "
              "worth at a time. Two people with an auger do 20 metres in a weekend; on a boundary, "
              "check the deeds and the 2 metre rule before you dig.",
              bias=1,
              guard=_a_fence_is_named,
              avoid=NOT_A_FENCE_JOB + (
                     "how much", "cost", "costs", "price", "quote", "who owns", "whose", "deeds",
                     "planning permission", "treat", "treating", "stain", "paint", "painting",
                     "how tall", "how high", "blew", "blown", "fell", "fallen", "repair", "replace",
                     "rotten", "rotted", "wobbly", "loose", "leaning", "came off", "panel has",
                     # the post questions have their own rows, and this one only knows the run
                     # a neighbour putting one up is the boundary question, not the build
                     "my neighbour", "my neighbor", "neighbour", "neighbor", "next door",
                     "fence post", "fence posts", "gate post", "post hole", "posts go",
                     # the height limit is the height row's: "can i put up a fence 2 metres high"
                     # was the build card once "put up a fence" was in the key above
                     "metres high", "metre high", "metres tall", "metre tall", "feet high",
                     "foot high", "planning permission", "permission", "allowed", "legal",
                     "how deep", "depth", "how far apart", "spacing", "how thick", "what size",
                     "postcrete", "concrete a post", "concrete it in", "bags of")),
        entry("fence-owner",
              (("who owns", "whose", "who is responsible", "who pays", "who has to pay",
                "who should pay", "my neighbour", "my neighbor", "neighbour says", "neighbor says",
                "neighbours fence", "neighbor's fence", "neighbour's fence", "neighbours fence",
                "next door say", "boundary", "deeds", "title plan", "t mark", "shared fence",
                "pay half", "half the cost", "have to pay", "split the cost", "go halves",
                "shared boundary",
                "took the fence down", "removed the fence", "replaced the fence", "put up a fence"),
               ("fence", "fencing", "fence panels", "fence panel", "boundary fence", "wall")),
              "Who owns a boundary fence is in the deeds, not in who mows the grass: the title plan "
              "marks the owner's side with a T, and where there is no mark it is usually shared, each "
              "side looking after the fence on their own side. Almost no property has to have a fence "
              "at all, so a neighbour taking down one that is theirs is usually within their rights. "
              "If it is theirs you cannot paint it, fix your side of it or hang anything on it without "
              "asking, and if it is shared the fair split is half the cost each.",
              ask=("fence", "fencing", "fence panel", "fence panels", "boundary fence", "hedge",
                   "wall"),
              # "do i have to pay half the fence" is the ownership question, and cost-fence would
              # otherwise answer it with a price per metre
              bias=1,
              avoid=NOT_A_FENCE_JOB + ("how much", "cost", "costs", "price", "quote", "blew down", "blown down",
                     "blew out", "blown out", "came off", "fell down", "repair", "fix it",
                     "replace", "treat", "treating", "stain", "staining", "paint it", "painting",
                     "preserver", "creosote", "rotten", "rotted", "wobbly", "loose",
                     "how tall", "how high", "tall can", "high can", "planning",
                     # the height limit can be said in metres or feet, and "can i put up a fence 2
                     # metres high" was the deeds answer for want of a number
                     "metres high", "metre high", "metres tall", "metre tall", "feet high",
                     "foot high", "ft high", "m high", "2m", "6ft", "planning permission",
                     "can i put up a fence", "can i build a fence", "am i allowed",
                     # the build question ("where do I dig, what order") is the fence-build row's;
                     # these keep the deeds answer for who owns, who pays and who took it down
                     "how do i put up", "how to put up", "how do i build", "how to build",
                     "how do i fence", "fence my garden", "where do i start",
                     "how long does it take", "how long to put up", "what do i need to put up",
                          "put up a fence myself", "put a fence up myself", "erect a fence",
                     "install a fence", "do it myself", "how do i begin", "where do i begin",
                     # "my neighbour's fence is blocking my light" and "his wall is too high" ask
                     # what can be done about it, which is the council route, not the deeds
                     "blocking my light", "blocks my light", "blocking the light", "blocks the light",
                     "my light", "too tall", "too high", "overhanging", "overhangs", "branches")),
        # Light and overhanging branches are the neighbour question people actually have, and it is
        # not a fence: a hedge, a tree or a fence that blocks the light has its own route (the council
        # under the high-hedges rules), and cutting back what overhangs is a right with conditions.
        entry("neighbour-hedge-light",
              (("too tall", "too high", "blocking my light", "blocks my light", "blocking the "
                "light", "blocks the light", "blocking light", "blocks light", "block my light",
                "no light", "my light", "overhanging", "overhangs", "hanging over", "hangs over",
                "branches over", "branch over", "trees over",
                # not a bare "cut back": "the hedge needs cutting back" is the pruning question, and
                # the dispute reading needs a neighbour, a height or the light in the line
                "cut back over my", "cut over my", "cut my branches", "cut back my branches",
                # the commonest shape of the question names the branches and not the position:
                # "can i cut branches off my neighbours tree" was a search hedge
                "cut branches", "cut a branch", "cut back branches", "cut the branches",
                "cut back the branches", "trim branches", "trim the branches", "branches off",
                # not "hedge is": it is a fragment, not a boundary phrase, and it made every line
                # that says what the hedge is like ("my hedge is looking sorry for itself") a
                # neighbour dispute. The boundary reading needs a neighbour, a height or the light.
                "high hedge", "hedges", "complaining about", "complain about",
                "hedge too tall", "hedge too high"),
               ("hedge", "hedges", "tree", "trees", "branches", "branch", "fence", "fencing",
                "wall", "neighbour", "neighbours", "neighbour's", "neighbors", "next door",
                "next-door")),
              "A hedge or a wall that shuts out the light is the council's job, not a court's: if it "
              "is an evergreen hedge over 2 metres and it blocks your light, you can complain to the "
              "council under the high-hedges rules, but only after you have written to the neighbour "
              "and kept a copy, and there is a fee of a few hundred pounds. Branches that overhang "
              "your side you can cut back to the boundary without asking, though you must offer the "
              "cuttings back and you cannot lean into their garden to do it, and you must not cut a "
              "tree under a tree preservation order or in a conservation area without checking with "
              "the council first. Right to light through an old window is a separate legal claim and "
              "a solicitor's job.",
              ask=("hedge", "hedges", "tree", "trees", "branches", "branch", "fence", "fencing",
                   "wall"),
              avoid=NOT_A_FENCE_JOB + ("how much", "cost", "costs", "price", "quote", "blew down", "blown down",
                     "blew out", "blown out", "repair", "fix", "replace", "treat", "treating",
                     "stain", "staining", "paint", "painting", "creosote", "rotten", "rotted",
                     "wobbly", "loose", "how tall can", "how high can", "planning permission for",
                     "who owns", "whose", "deeds", "fell down", "died", "dead", "dying", "diseased",
                     "looks dead", "brown", "not growing", "bare patch",
                     # a plant in a bad way is the hedge-care answer, not the council's: the state
                     # of the hedge is the subject and there is no dispute in the line
                     "patchy", "yellow", "yellowing", "yellowed", "gone brown", "brown at the base",
                     "brown at the bottom", "bare at the bottom", "bare at the base", "thin",
                     "sparse", "gaps", "gap", "looking sorry", "sorry for itself", "looks ill",
                     "looks bad", "looks sad", "bald", "shrubs", "shrub", "feed", "feeding",
                     "fertiliser", "fertilizer", "compost", "mulch", "watering", "water it",
                     "poison", "fruit", "apple", "pear", "plum", "cherry tree", "prune",
                     "pruning", "plant a tree", "plant a hedge", "how do i trim")),
        # "trapped in my job" is a feeling, so the lock is what counts here, not the place.
        entry("locked-in-a-room", (("locked in", "locked inside", "shut in", "stuck inside"),
                                   ("flat", "house", "home", "room", "bedroom", "bathroom",
                                    "toilet", "garage", "shed", "cellar", "loft", "hallway")),
              "If a child is shut in, ring 999 straight away and stay on the line. Otherwise get a "
              "window open and shout to a neighbour, or ring someone who has a spare key - "
              "someone is nearly always in. If nobody is, the landlord or letting agent first, then "
              "a locksmith who quotes on the phone; a stuck lock is worth one firm push with the "
              "handle held up before you pay anyone. If there is fire, smoke or someone unwell, "
              "ring 999 and say you are locked in.",
              bias=1),
        entry("draughts", (("draught", "drafts", "draughts", "cold air", "under the door",
                            "under the front door", "gap under"),
                           ("door", "window", "cold", "stop", "keep", "front")),
              "Stick a brush strip or foam seal round the doors and windows, and put a weighted "
              "draught excluder at the bottom of the front door. A chimney balloon and a letterbox "
              "flap are cheap and stop the worst of it; seal up the gaps before spending money on "
              "heating."),

        entry("door-banging", (("door", "doors", "gate"),
                               ("banging", "bangs", "bang", "slamming", "slams", "slam", "rattling",
                                "rattles", "rattle", "wind", "windy", "shutting", "swinging")),
              "A door that bangs is a latch that isn't holding or a gap that lets the wind push it: "
              "check the strike plate first — a card's thickness of movement is enough, and moving it "
              "2mm further in with a chisel or a file fixes most of them. If it still swings, a hook "
              "and eye or a magnetic catch holds it open or shut, and a foam strip on the stop takes "
              "the noise out.",
              # "a cupboard door" and "the kitchen door" bang too, but not from the wind: the
              # strike plate answer is about a room door in a draught, so a cabinet that will not
              # stay shut goes to whatever cabinet entry fits, and never to the wind.
              # A car door that is frozen shut is a different job with a different answer, and the
              # key word "shutting" alone was enough to take it: cars.py has that entry.
              avoid=("frozen", "freezing", "froze", "iced", "ice", "frost", "car door", "car doors",
                     "stuck shut",
                     "paint", "painting", "sticking", "creaking", "hinge", "hinges", "lock", "key",
                     "keys", "handle", "front door lock", "burglar", "shed", "garage door",
                     "cupboard", "cupboards", "cabinet", "cabinets", "wardrobe", "wardrobes",
                     "kitchen", "kitchen door", "drawer", "drawers",
                     # the door of an appliance is never the door in the wind
                     ) + APPLIANCE_DOOR_WORDS + (

                     # a finger caught in a door is the black-nail answer, not a latch: the nail is
                     # the subject and "slammed" only says how it happened
                     "nail", "nails", "fingernail", "fingernails", "toenail", "toenails", "finger",
                     "fingers", "thumb", "toe", "toes", "hand", "jammed",
                     # a person shutting a door in a temper is the end of a row, and the latch
                     # answer was given to "he slammed the door" two turns after one
                     "slammed the door", "slams the door", "door on me", "door in my face")),

        # --- moving in ----------------------------------------------------------

        # A move that has not happened yet and is about too much stuff is a packing plan, not a
        # question about what the van costs. The clutter words here are chosen so they cannot
        # reshuffle the rest of the base: lookup._rank gives a bonus to a key word only one entry
        # uses, and "stuff" (used only by chicken-stuffed) turned "And if I stuff it?" into the
        # plain chicken answer when I first keyed this with it.
        # The first group is the phrase people say, not the bare verb: "keep moving" and "lifting
        # boxes" are a bad back, and "moving" alone is in every line about a new job, a new city or
        # a new phone. "pack" and "moving house" are the words that only appear in a move.
        # An office, a shop or a studio is a move too: the boxes and the kettle for the first night
        # are the same job, so the workplace phrases are keys and only the bare verb stays out.
        entry("moving-pack", (("move house", "moving house", "moving home", "move home",
                               "moving flat", "move flat", "moving out", "move out",
                               "moving in", "move in", "for moving", "before moving",
                               "moving office", "move office", "moving offices", "move offices",
                               "office move", "moving the office", "moving shop", "moving studio",
                               # "too much stuff to move" names the move after the stuff, with no
                               # "moving" in it: the infinitive is the phrase, and the second key
                               # group still has to be about the load, so "i want to move" passes.
                               "to move", "to be moved", "to move house",
                               "pack", "packing", "packed", "unpack", "unpacking"),
                              ("too much", "so much", "lots", "loads", "plenty", "things",
                               "boxes", "clutter")),
              "Pack what you use least first - books, spare bedding, the cupboard under the stairs - "
              "and keep a 'first night' box out of the van: kettle, mugs, chargers, loo roll, bedding "
              "and a change of clothes. Label boxes by room, do one room an evening for the last "
              "three weeks, and get rid of anything you have not touched in a year rather than "
              "paying to move it.",
              avoid=BODY_WORDS),

        entry("moving-cheap", (("move", "moving", "moved", "removals", "man with a van"),
                               ("cheap", "cheaper", "cheapest", "cheaply", "cost", "costly",
                                "price", "prices", "pricey", "expensive", "budget", "hire", "van",
                                "money", "save", "afford")),
              ("For one sofa and a bed, hire a man with a van for a couple of hours or borrow a van and "
               "two friends; book the van for the whole morning rather than by the hour. Measure the "
               "doorways and the stairwell first, because a sofa that doesn't fit costs you the day."),
              # "house", "flat" and "moving" alone are everyday words: without these avoids the van
              # advice answered "how do I tell my kids we're moving house", "how do I register with a
              # doctor after moving house" and "do I need to tell the council when I move out".
              avoid=("stressed", "stress", "worried", "nervous", "anxious", "sad", "upset", "feeling",
                     "kids", "children", "child", "tell", "doctor", "gp", "dentist", "council",
                     "council tax", "school", "care home", "piano", "landlord", "deposit", "tenancy",
                     "register")),
        entry("moving-admin",
              (("move", "moving", "moved", "moving house", "moving flat", "new address", "new house",
                "new flat", "move house", "move out"),
               ("council", "council tax", "doctor", "gp", "dentist", "school", "register", "utilities",
                "redirect", "meter", "tenancy", "admin", "paperwork", "notify", "need to do",
                "tell", "what do i need", "checklist")),
              ("Do the paper trail in one afternoon: tell the council tax office for the old and the "
               "new address, register with a GP near the new place and ask for your notes to move with "
               "you, and read the meters on the day you leave and arrive. Set up a Royal Mail redirect "
               "for three months, because it catches the accounts you forget, and take photos of the "
               "meters as proof."),
              # "moved" and "move" are in every line about a new phone, a new city or a new job, so
              # this entry only answers when the line names the paperwork as well.
              # "what do i need to buy first" is the first-night box, not the paper trail
              avoid=("buy", "first night", "sofa", "van", "cheap", "cost", "price", "hire", "removal",
                     "phone", "laptop",
                     # telling the landlord is the notice letter, not the paper trail: "when
                     # should i tell my landlord im moving out" got the GP-and-meters list
                     "tell my landlord", "tell the landlord", "my landlord", "the landlord",
                     "landlord", "landlady", "letting agent", "notice period", "give notice",
                     "who do i tell about my new address", "who do i tell about my address",
                     "who do i tell about my new adress", "who do i tell about my new place",
                     # "change the name on my council tax bill after my husband moved out" is the bill,
                     # not the move: the name and the discount are the question, and the paper-trail
                     # list buries them.
                     "change the name", "name on", "in my name", "not on the bill",
                     "computer", "city", "job", "office", "desk", "company", "files", "apps",
                     "contacts", "care home", "piano", "abroad", "country", "kids", "kid",
                     "children", "child", "son", "daughter", "explain", "upset",
                     # a rescheduled appointment is not a house move: "the doctor appointment got
                     # moved" matched "moved" and "doctor", so the paper-trail list came back
                     "appointment", "appointments", "rescheduled", "postponed",
                     "brought forward", "cancelled", "canceled", "moved to", "moved it",
                     # a moved shift is not a moved house: "my boss moved my shifts again and i
                     # cant do the school run" matched "moved" and "school" and got the
                     # paper-trail list, where the rota card is the answer. Work words stand
                     # this entry down.
                     "shift", "shifts", "rota", "boss", "manager", "overtime")),
        # "how do I pack for a house move" was a shrug and "no idea where to begin the packing" got
        # the weekend-away list, because packing-weekend names a weekend and packing. This is the
        # move's own packing: what to put in first, what goes in the first-night box, what to get rid
        # of rather than pay to move. moving-pack already answers the clutter lines ("too much stuff")
        # and a bare date is news, so this one asks for the packing itself.
        # The bare verb is not a key here either: "keep moving" with "boxes" is a bad back, so the
        # first group is the phrases that only appear in a move.
        entry("moving-packing-plan",
              (("move house", "moving house", "moving flat", "move flat", "house move", "moving home",
                "move home", "moving out", "moving in", "removals", "before moving", "when moving",
                "after moving", "moving office", "move office", "moving offices", "move offices",
                "office move", "moving the office", "moving shop", "moving studio",
                # "pack for a move" is the planning question and names the move without a noun after
                # it, so the article forms are keys too. They carry no meaning alone, and the second
                # group still has to be about packing, so "its your move" passes.
                "for a move", "a house move", "the move", "for the move"),
               ("packing", "pack", "packed", "boxes", "box", "declutter", "unpack")),
              # The fuller plan wins a line that fits both: "how do i pack boxes for moving house" is
              # the planning question, not the short "too much stuff" answer.
              bias=1,
              reply=("Start with one room and one deadline: pack the things you use least first, label every "
               "box by room and keep one box for the first night - bedding, toilet roll, kettle, mugs, "
               "chargers, a torch and any medication. Anything you have not used in a year, sell, "
               "donate or bin it now rather than paying to move it; a bag a day from the back of a "
               "cupboard gets rid of most of it. Book the van for the whole morning rather than by the "
               "hour, and measure the doorways and stairwell before the day. As a guide, a one-bed "
               "flat is about twenty boxes and a couple of weekends of packing; a three-bed house is "
               "two or three times that."),
              # "where do I even start" and "how do I plan" belong to plans.move-house-plan, and a
              # feeling about a move is not a packing question.
              avoid=("council", "council tax", "doctor", "gp", "dentist", "register", "tenancy",
                     "deposit", "landlord", "kids", "children", "child", "son", "daughter",
                     "piano", "abroad", "country", "city", "job", "phone", "laptop", "computer",
                     "contacts", "apps", "care home", "pet", "cat", "dog", "trip", "holiday",
                     "flight", "hotel", "camping", "suitcase", "weekend away",
                     "start", "started", "starting", "plan", "planning", "organise", "organize",
                     "organised", "sorted", "checklist", "advice", "break up", "breakup",
                     "girlfriend", "boyfriend", "ex", "stressed", "stress", "worried", "nervous",
                     "anxious", "sad", "upset", "feeling", "overwhelmed", "exhausted", "dreading",
                     "manager", "boss", "meeting",
                     # crockery named in the line wants the box-by-box answer, not the plan:
                     # "how do i pack glasses for a house move" is about the glasses
                     "glasses", "plates", "mugs", "crockery", "glassware", "china", "bowls")
              + BODY_WORDS),
        # The packing lines that never say "move": "how long does it take to pack a 1 bed flat", "any
        # tips for packing a house". moving-packing-plan keys on the move, so these fell to a hedge.
        # Packing plus a home is the same question, and the trip lines (suitcase, holiday, weekend
        # away) stay with the travel packing entries.
        entry("packing-time",
              (("pack", "packing", "packed", "boxes"),
               ("flat", "house", "home", "1 bed", "one bed", "2 bed", "two bed",
                "how long", "how many boxes", "bedsit", "moving day")),
              ("Pack what you use least first and give it a date: a one-bed flat is about twenty boxes "
               "and two weekends if you do it evenings and one weekend if you take a day off; a "
               "three-bed house is two or three times that. Every box labelled by the room it goes to, "
               "one first-night box kept out of the van, and anything you have not used in a year "
               "goes to the charity shop rather than into a box."),
              # A statement about packing ("i'm packing up my flat next week") is news and the chat
              # module acks it, so the advice only comes when the line asks something.
              ask=("how long", "how many", "tips", "advice", "how much", "best way", "how do i",
                   "where do i", "what do i need", "should i"),
              avoid=("suitcase", "holiday", "trip", "flight", "airport", "camping", "abroad",
                     "weekend away", "hand luggage", "carry on", "school bag", "nappy bag",
                     "council", "council tax", "doctor", "gp", "dentist", "register", "tenancy",
                     "deposit", "landlord", "kids", "children", "child", "piano", "van", "cost",
                     "price", "cheap", "removal", "stressed", "stress", "worried", "nervous",
                     "anxious", "sad", "upset", "feeling", "overwhelmed", "dreading",
                     # "flat pack" folds to "flat" + "pack", so building a wardrobe got the
                     # moving-boxes answer: the furniture words are not a house being packed
                     "flat pack", "flat-pack", "furniture", "assemble", "assembling",
                     "wardrobe", "sofa", "mattress", "bookcase", "bed frame", "dining table",
                     # a line that names the breakables wants packing-breakables, not a plan
                     "glasses", "plates", "mugs", "crockery", "glassware", "china", "bowls",
                     "wine glasses", "tumblers", "ornaments", "vases")
              + BODY_WORDS),
        # "how do i pack plates so they dont break" got the weekend-away list, because a box of
        # plates is a packing question and the travel entry also keys on "break". The breakables are
        # the one part of packing with a right answer, so they get their own.
        entry("packing-breakables",
              (("pack", "packing", "packed", "wrap", "wrapping", "box up", "boxes", "box"),
               ("plates", "glasses", "crockery", "mugs", "dishes", "bowls", "china", "fragile",
                "wine glasses", "ornaments", "vases", "picture frames", "mirrors", "tumblers")),
              ("Wrap each plate in paper or a tea towel and stand it on its edge in the box, like "
               "records in a crate, never stacked flat: that is what stops them cracking. A crumpled "
               "paper or towel cushion in the bottom and on top, small boxes that one person can lift, "
               "and FRAGILE written on the sides. Glasses and mugs go upright with paper pushed inside, "
               "a mug handle never takes the weight, and wine glasses travel best one inside a sock. A mirror "
               "or a framed picture travels standing on its edge too, with card on the corners and "
               "tape across the glass in an X so a crack stays put."),
              # A statement ("i'm packing the plates tonight") is news, and a broken plate is not a
              # packing question: the advice only comes when the line asks how.
              ask=("how", "what", "tips", "advice", "best way", "should i", "so they dont break",
                   "so they don't break", "wont break", "won't break", "without breaking",
                   "not break", "safely"),
              # A trip is a suitcase, not a box: "what should i pack for a weekend away with my
              # glasses" was the travel list, and it should stay the travel list.
              avoid=("spectacles", "contact lenses", "contact lens", "lenses", "prescription",
                     "glasses prescription", "eyes", "sight",
                     "weekend", "weekend away", "trip", "holiday", "holidays", "abroad", "flight",
                     "hotel", "suitcase", "carry on", "hand luggage", "days")),
        # The kitchen is the room nobody knows where to start with, and the packing entries had
        # no line for it: "how do i pack the kitchen" was the cleaning routine (the room plus the
        # bare "how"), and in a move chat "and the kitchen stuff" was three quotes and a payment
        # schedule from the renovation plan. Crockery and glasses keep packing-breakables.
        entry("packing-a-kitchen",
              (("kitchen", "kitchens", "kitchen stuff", "kitchen things", "kitchen cupboards",
                "kitchen drawers", "cupboards in the kitchen"),
               # the packing words are the whole key on this side: a looser group ("how",
               # "start", "first", "what about") let the carried words of a move chat pull this
               # card onto "only in the kitchen", "what about the ceiling" and "theyre melamine".
               ("pack", "packs", "packing", "packed", "box", "boxes", "box up", "pack up",
                "packing up",
                # the room named with "stuff" is the kitchen in a move chat: "and the kitchen
                # stuff" after a packing question is what has to go in the boxes, and it was
                # three quotes and a payment schedule from the renovation plan. Shopping for a
                # kitchen is fenced below, and so are the words that name a job instead.
                # "things" is not a key: "what new thing should i try in the kitchen" is a
                # cooking question and the boxes answered it.
                "stuff", "the rest")),
              ("Leave the kitchen to the second-to-last day, because it is the room you still "
               "need, and keep one box open until the morning: kettle, two mugs, tea, a tea towel, "
               "washing-up liquid, a sharp knife, a tin opener and a corkscrew. Do it one cupboard "
               "at a time and set a box down on the counter as you empty it, so nothing gets "
               "carried across the room; plates and glasses go on edge in small boxes with a towel "
               "round them, never stacked flat. Anything out of date or never used goes in the bin "
               "bag rather than the van, the fridge wants emptied, defrosted and dried out a day "
               "before, and it travels upright. Write KITCHEN - OPEN FIRST on the boxes you will "
               "want that night, and put the food and the cleaning stuff in their own two boxes so "
               "you are not hunting for the bin bags."),
              # a kitchen being cleaned, planned, fitted or painted is another row's line, and so
              # is shopping for one: only the packing words reach this one.
              guard=_the_kitchen_stuff_is_a_take_up,
              avoid=("unpack", "unpacking", "unpacked",
                     "clean", "cleaning", "cleaned", "grease", "greasy", "smell", "smells",
                     "oven", "fridge", "freezer", "hob", "cooker", "microwave", "bin", "dishwasher",
                     "leak", "tap", "taps", "mould", "limescale", "floor", "floors", "wall", "walls",
                     "paint", "painting", "decorate", "plan", "planning", "design", "layout",
                     "fit", "fitted", "fitting", "install", "installing", "renovate", "refurb",
                     "quote", "quotes", "builder", "extension", "buy", "buying", "shop", "shopping",
                     "cheap", "cheapest", "price", "prices", "cost", "where can i get",
                     "plates", "glasses", "crockery", "china", "bowls", "mugs", "wine glasses")),
        entry("moving-with-kids",
              (("move", "moving", "moved", "moving house", "house move", "new house", "new home"),
               ("kids", "kid", "children", "child", "son", "daughter", "teenager", "toddler",
                # a baby is a child, and "moving house with a baby" reached nothing at all
                # because the word for the smallest one was not in the group
                "baby", "babies",
                "tell", "explain", "upset", "worried", "nervous", "sad", "cope", "settle")),
              ("Tell them as soon as it is certain, and keep it concrete: which room is theirs, where "
               "the school or nursery is, and what stays the same. Let them pack a box of their own "
               "things and choose the paint or the posters, because control is what they are missing. "
               "Say goodbye to the old place properly on the last day, and expect a wobble a few weeks "
               "in, when the novelty wears off and they miss their friends."),
              # A child who is leaving home is not a household packing up: "my daughter wants to
              # move out" was told "tell them as soon as it is certain... which room is theirs",
              # and "my son has moved out and i am bereft" the same. family.py answers the leaving.
              # A feeling in the speaker's own line is not a question about telling a child, and
              # that is a guard rather than more avoid words: see `_a_child_or_a_telling`.
              guard=_a_child_or_a_telling,
              avoid=("council", "council tax", "gp", "doctor", "dentist", "register", "piano",
                     "van", "cheap", "cost", "price", "abroad", "country", "care home",
                     "move out", "left home", "has left", "wants to move",
                     # the same care home without the word "care": "my mum moved into a home
                     # last month" was told to put a kettle and toilet roll in a box.
                     "a home", "the home", "nursing home", "residential home", "home too")),
        # A piano is the one thing that a hired van and two friends ruins, and its move has its own
        # answer rather than the sofa-and-bed line.
        entry("piano-move",
              (("piano",), ("move", "moving", "moved", "cost", "hire", "removers", "stairs",
                            "upstairs", "quote")),
              ("Hire a piano remover rather than a general removal firm: it takes two people who know "
               "the handholds, a proper trolley and straps, and a knocked soundboard is a repair bill. "
               "Keep it upright and never on its side, take the legs off an upright only if the maker's "
               "instructions say so, and let it settle in the new room for a few weeks before it is "
               "tuned. Stairs and narrow turns are what make a quote go up, so send a photo of the "
               "route when you ask for one."),
              avoid=("learn", "lessons", "practise", "practice", "tune", "buy", "worth", "grade")),
        entry("first-night", (("first night", "moving in", "moving into", "new flat", "first flat"),
                              # "what should i keep out for the first night" asks for this box in
                              # the words of someone standing in a hallway of boxes, and "should"
                              # alone is not the ask: it was the car's night-driving row on that
                              # line, and it pulled the box onto "what should i sort out first"
                              # in the middle of a should-we-move chat. The words below say the
                              # keeping-out, which is what the question is.
                              ("need", "do", "before", "buy", "keep out", "keep aside",
                               "keep back", "put aside", "put by", "pack last", "open first",
                               "have ready", "ready", "get ready")),
              FIRST_NIGHT_BOX,
              # Getting the furniture in is a different job from the first night in it: "how do I move
              # my sofa to my new flat" is a stairs-and-doorways question, and the kettle-and-toilet-roll
              # box cannot help with it. These words send that line to the honest hedge instead, which
              # is what main gives for "how do I move a sofa".
              avoid=("stressed", "stress", "worried", "nervous", "anxious", "sad", "upset", "feeling",
                     "sofa", "couch", "settee", "bed", "mattress", "wardrobe", "table", "chairs",
                     "fridge", "freezer", "piano", "van", "removals", "removal", "hire", "hiring",
                     "stairs", "upstairs", "doorways", "doors", "carry", "carrying", "lifting",
                     "move my", "moving my", "shift my")),
        entry("just-moved-in",
              # "just moved" and nothing looser: "we're moving into our first flat on Saturday" is
              # news - the chat module acks it and the first-night question comes as its own turn -
              # and the loose forms of "moving" and "moved" are the same word, so only the word
              # people say once they are in stays here. It is the same paragraph as first-night, not
              # a second copy of it, so the two cannot drift apart.
              # "we moved in last week" is the same arrival as "we just moved in": people say it in
              # the past tense with no "just", so the verb carries it and the time words below say
              # the move has already happened.
              (("just moved", "moved in", "moved into"),
               ("new flat", "new house", "new home", "new place", "first flat", "our own place",
                "moved in", "moved into", "last week", "last weekend", "last month", "this week",
                "this month")),
              FIRST_NIGHT_BOX,
              # "just moved into a care home, i feel guilty" is about the guilt, and the paperwork
              # lines are moving-admin's: this entry is only the arrival itself.
              # A tie with the paperwork list used to go to the paperwork: the arrival is the
              # question, so it wins the tie.
              bias=1,
              avoid=("guilty", "care home", "nursing home", "a home", "the home", "home too",
                     "residential home", "stressed", "stress", "worried",
                     "nervous", "anxious", "sad", "upset", "feeling", "kids", "children", "child",
                     "council", "council tax", "doctor", "gp", "dentist", "school", "landlord",
                     "deposit", "tenancy", "address", "register", "job", "city", "country", "abroad",
                     # an arrival that already has a problem is that problem's question
                     "damp", "mould", "mold", "leak", "piano", "boiler", "heating", "hot water",
                     "radiator", "broken", "repair", "washing machine", "fridge", "noise", "noisy",
                     "neighbour", "neighbours", "cold",
                     # a move still to come, or one made with someone, is news and a chat, not the
                     # list of what to put in the box tonight
                     "tomorrow", "next week", "next month", "on saturday", "on sunday",
                     "with my", "boyfriend", "girlfriend", "partner", "husband", "wife", "parents",
                     "flatmate", "housemate", "together"),
              # "my bowels havent moved in 4 days" carries `moved in` and was told to buy toilet roll
              # and photograph the meters: a bowel that has not moved is the stomach's line, and the
              # reading says so (see `the_stomach_is_what_it_is_about`)
              guard=lambda understood: not the_stomach_is_what_it_is_about(understood)),
        # --- a home in hot weather ---------------------------------------------
        # Keeping the heat out of a room is one job and sleeping in it is another, so they sit apart
        # from fan-vs-aircon (which is a cost question) and from nature.heatwave (which is the public
        # health line: drink water, check on neighbours). The appliances, pets and people with their
        # own answers are avoided, because a fridge that is not cool and a baby in the heat are not
        # this entry's question.
        entry("keep-room-cool",
              (("house", "home", "flat", "room", "bedroom", "living room", "kitchen", "windows",
                "heatwave", "heat wave", "heat", "summer", "sun", "indoors", "inside", "upstairs",
                "downstairs",
                # The room they are standing in, said without naming it, and the workplace, which
                # is the same question about the same four walls: "its boiling in this office" was
                # a shrug until "office" was here, and "its like a sauna in here" with it.
                "office", "in here", "in this room", "this room", "this place", "my place",
                "our place"),
               ("cool", "cooler", "cooling", "cool down", "keep cool", "hot", "boiling", "stuffy",
                "stifling", "roasting", "shade", "sun", "keep the sun out", "windows",
                # "the flat gets baking in summer" is a home in a heatwave: without "baking" the
                # line reached the flat-bake card, and once that stands down it gets a shrug.
                "baking", "baking hot", "an oven",
                # Heat is a picture as often as it is a word: "its like a sauna in here", "my
                # bedroom is like an oven", "its stifling in here" and "im roasting in here" all
                # fell to the floor because a room is never named in them. The picture is the
                # same claim as "the room is too hot", so the row reads it as one.
                "sauna", "like a sauna", "like an oven", "like a greenhouse", "like a furnace",
                "sweltering", "melting", "boiling hot", "hot as an oven", "stifling hot",
                "a furnace", "furnace",
                # Keeping the heat out is the same job asked from the other side, and it was
                # read as a question about turning the heating ON: "how do i keep the heat out
                # in summer" got the 18C living-room setting and "how do i stop the sun heating
                # my flat" got the electric radiator.
                "keep the heat out", "heat out", "stop the sun", "sun heating", "block the sun",
                "the sun coming in", "sun comes in", "sun through")),
              ("Shut the windows and pull the curtains on the sunny side in the morning, then open "
               "everything wide once it is cooler outside than in, usually after 9pm. A fan in an open "
               "window pulling air through the flat beats one blowing at you. Keep the oven off and "
               "cook early, and put a bowl of water out if the air is dry."),
              # "heating" is not avoided: "heat" is one of its forms, so it would take every
              # heatwave line with it. Only the switched-on phrase goes.
              avoid=THE_APPLIANCE_ITSELF + ("hob", "boiler", "radiator", "heating on",
                     "radiators", "washing machine", "tumble dryer", "laptop", "computer", "pc",
                     "phone", "tablet", "car", "engine", "dog", "cat", "puppy", "kitten", "baby",
                     "babies", "toddler", "pregnant", "fan cheaper", "cheaper", "cost",
                     "electricity", "bill", "keep warm", "keep the house warm", "draught",
                     "draughts", "drink", "beer", "wine", "food", "milk", "leftovers",
                     # "i moved into a new flat and theres no hot water" is a boiler question
                     "hot water", "no water", "cold water", "shower", "bath", "immersion",
                     "heating on", "thermostat",
                     # a room with no window is its own answer, not the heatwave one
                     "no window", "no windows", "without a window", "windowless",
                     # building work on a window is not a way to keep a room cool
                     "bigger", "bigger window", "enlarge", "enlarging", "widen", "widening",
                     "larger", "new window", "window fitter", "glazier")),
        # A room with no window is asked about for the same two things every time - it is dark, and
        # the air sits still - and it was getting the keep-cool answer, because "room" is in that
        # row's key and "window" in its second group.
        entry("room-no-window",
              (("room", "bedroom", "living room", "kitchen", "hallway", "office", "study", "flat",
                "cellar", "basement"),
               ("no window", "no windows", "without a window", "without windows", "windowless",
                "no natural light", "no light", "get light", "air", "ventilation", "ventilate",
                "airflow", "stuffy", "damp")),
              ("Light it in layers and move the air with a fan. One bright lamp in each corner beats a "
               "single ceiling light, an LED around 4000K reads closest to daylight, and a mirror or "
               "pale wall opposite the door bounces it about. For the air, prop the door open with a "
               "fan pulling air through to another room, or run a small dehumidifier: a windowless "
               "room goes damp before it goes stuffy."),
              avoid=("mould", "mold", "mildew", "condensation", "cool", "cooler", "hot", "heatwave",
                     "heat", "radiator", "boiler", "heating", "paint", "curtain",
                     "curtains", "blind", "blinds", "bigger", "enlarge", "widen", "door", "lock",
                     # a room that smells is the damp answer: "my basement smells damp" is not a
                     # question about lamps and airflow, though it carries the word damp
                     "smell", "smells", "smelling", "smelly", "musty", "whiff", "reek", "stinks")),
        # "my living room needs a bigger window" is not a cleaning or a cooling line: it is building
        # work, and the answer is who does it and what it needs before anyone quotes.
        entry("window-bigger",
              (("window", "windows", "window opening"),
               ("bigger", "enlarge", "enlarging", "enlarged", "widen", "widening", "larger",
                "more light", "knock through", "new window", "replace the window",
                "replacement window", "big window")),
              ("Widening a window opening is a builder's job, not a window fitter's: taking out "
               "brickwork under a new lintel is structural, where a swap of the same size is a fitter's "
               "morning. Ask a builder to price it, and a structural engineer if the wall carries the "
               "floor above; in a flat or a conservation area you may need permission too. Cheaper "
               "first: a mirror opposite the window and paler walls."),
              avoid=("curtain", "curtains", "blind", "blinds", "draught", "drafts", "draft",
                     "measure", "measuring", "clean", "cleaner", "cleaning", "wash", "replace the "
                     "glass", "cracked", "broken", "stuck", "leaking", "condensation", "no window")),
        # A window painted shut, an old sash that will not budge and a frame swollen after rain are
        # one question - the window will not open - and nothing answered it: the door row wants a
        # door, so these lines fell to "say more".
        entry("window-wont-open",
              (("window", "windows", "sash window", "sash", "casement", "frame", "upvc"),
               # "sticking" and "hard to open" are how the same fault is described when nothing has
               # jammed yet: "how do i fix a sticking window" scored here on nothing and got a
               # glazier's quote for broken glass, and then a door-hinge card for a creaking door.
               ("wont open", "won't open", "will not open", "cant open", "can't open", "cannot open",
                # "painted shut" and "painted over", but not a bare "painted": painting a window is
                # the painting rows' line, and "how do i paint a sash window" was a sash fault
                "painted shut", "painted over", "stuck", "stuck shut", "jammed", "seized",
                "swollen", "swelled", "warped", "budge", "wont move", "won't move", "wont shut",
                "won't shut", "wont close", "won't close", "sticking", "sticks", "doesnt close",
                "doesn't close", "hard to open", "hard to close", "hard to shut", "easier to open",
                "rubs", "dragging", "stiff")),
              ("Run a knife round the join first, because paint gluing the frame to the sill is the "
               "usual cause: score the line all the way round, then press on the frame and lift the "
               "handle. If it is a sash, check the cords - a snapped cord drops the weights and the "
               "window wedges. A tap with the heel of your hand and a dry bar of soap on the runners "
               "frees most of the rest."),
              avoid=("door", "doors", "windscreen", "car", "clean", "cleaning", "cleaner", "wash",
                     "condensation", "draught", "draft", "drafts", "leaking", "leak", "cost", "price",
                     "replace", "double glazing", "curtain", "curtains", "blind", "blinds", "bigger",
                     "widen", "enlarge", "no window", "no windows", "storage",
                     # and painting a window frame is the painting rows' line, not a sash fault's
                     "paint a window", "painting a window", "paint my window", "paint the window",
                     "paint window", "painting the windows", "paint the windows", "repaint",
                     "painting a window frame", "paint a window frame", "brushes", "brush"),
              # the creaking-door row keys "sticking" and "window" both, so a window that sticks ties
              # it and loses on registry order: a window is this row's, and the hinge card is not.
              bias=2),
        entry("sleep-hot-night",
              (("sleep", "sleeping", "slept", "bed", "bedroom", "night"),
               ("hot", "heat", "heatwave", "heat wave", "warm", "sweating", "sticky", "sweaty",
                "cool", "cooler", "cooling", "cool down", "too hot")),
              ("Cool the room before you get in, not after: windows open and a fan on for half an hour, "
               "then a lukewarm shower and dry off properly. Cotton sheets, one light layer rather "
               "than a duvet, and a damp flannel on your neck or feet. Sweating is how your body dumps "
               "heat, so give it moving air instead of covering up."),
              avoid=("baby", "babies", "toddler", "child", "children", "dog", "cat", "puppy",
                     "kitten", "pregnant", "fridge", "freezer", "boiler", "radiator", "heating on",
                     "laptop", "phone", "computer", "car", "mattress", "buy", "best", "which",
                     "wake up", "waking", "woke", "nap", "nightmare", "dream", "snore",
                     "snoring", "teeth", "grind"),
              # "cool cool. anyway im off to bed" is chit-chat that happens to hold a "cool"
              # and a "bed", so this needs a real ask as well as the heat word.
              ask=("how", "what", "tips", "tip", "advice", "should", "can i", "can you", "help",
                   "too hot", "cant", "can't", "cannot", "struggling", "keep", "cool down")),
        # Half of the "my bed is uncomfortable" lines want a fix for tonight, not a shopping trip,
        # and they used to land on shopping.mattress-buy (which answers "what should i buy") or on
        # nothing at all. The comfort words are the keys and the buying words are in the avoid, so
        # "which mattress should i buy" still gets the buying answer.
        # A lumpy pillow is its own answer: "my pillow is lumpy" was reaching the mattress row on
        # "lumpy" and being told to price up a topper, which is not what a lumpy pillow wants.
        entry("lumpy-pillow",
              # `duvet` and `duvets` were here with bias=2 on the row, so "my duvet is lumpy" and "how
              # do i fluff up a lumpy duvet" got the pillow card, whose first move is "unzip it" -
              # advice for a pillowcase and not for a duvet. A duvet is `cleaning.bedding-life`'s
              # question, and its card has the tumble-on-low-with-dryer-balls answer already.
              (("pillow", "pillows", "pillowcase", "pillow case", "filling"),
               ("lumpy", "lumps", "bunched", "bunched up", "flat", "too flat", "saggy", "sags",
                "gone flat", "worn out", "old", "replace", "uncomfortable")),
              "A lumpy pillow has usually just bunched its filling: unzip it, pull the filling apart "
              "with your hands, shake it down to the corners and bash it flat. If it still lumps, or "
              "it folds in half and stays folded when you lay it on your arm, the filling has gone "
              "and a new one is the fix - hollowfibre costs about £10 to £25 and a pillow over two "
              "years old is usually past it. A duvet that has gone lumpy is the same job, and a wash "
              "on a hot cycle with two tennis balls in the tumble dryer evens the filling out again.",
              bias=2,
              # the bed under the pillow, the way to sleep and the state of the person are their own
              # answers; a hotel, a baby and a shop are other rows too
              avoid=("mattress", "mattresses", "topper", "bed frame", "sprung", "squeak", "hot",
                     "wash", "washing", "dryer", "smell", "smelly",
                     "sweat", "sweaty", "insomnia", "wake up", "waking up", "cant sleep",
                     "hotel", "baby", "babies", "toddler", "cot", "pram", "buy", "which",
                     "should i get", "look for", "best")),
        entry("bed-uncomfortable",
              (("bed", "beds", "mattress", "mattresses", "bedding"),
               ("uncomfortable", "too soft", "too hard", "too firm", "sagging", "sags",
                "sag", "dip", "dipped", "hurts", "hurt", "sore back", "stiff back", "wake up sore",
                "waking up sore", "bad back", "not comfortable", "kill my back", "kills my back",
                "topper", "springs")),
              ("Try a mattress topper before a new mattress. A 5cm memory-foam or latex one costs about "
               "£40 to £100 and softens a firm bed or fills the dip in a soft one. If the mattress is "
               "over eight years old, sagging in the middle or you can feel the springs, it is the "
               "mattress and a topper only postpones it. A slipped pillow under your knees takes the "
               "strain off a sore lower back, and a too-soft bed is worth trying with a board under it "
               "first."),
              # buying questions, cleaning and a hot night are other entries' business.
              # "can i fix it without buying a new one" is the fix question, so the buying words are
              # the phrases that ask what to buy, not the bare verb: bare "buy" also matched "buying"
              # and swallowed this entry's own deck line.
              avoid=("should i buy", "should i get", "to buy", "buy a new mattress", "buy a mattress",
                     "buy a new bed", "new mattress", "new bed", "cost", "price", "how much", "cheap", "cheaper",
                     "budget", "which", "choose", "choosing", "best", "shop", "deal", "sale",
                     # "what should i look for in a mattress" asks what to look for, whatever else
                     # the line says about a bad back: that is the buying answer.
                     "look for", "looking for", "recommend", "recommendation", "worth it", "review",
                     # a sore back is the back's own answer: "my bed is killing my back" asks what
                     # to do about the back first, and the bed card is only the bed half of it
                     "back pain", "my back hurts", "killing my back", "bad back pain",
                     "clean", "cleaning", "stain", "stains", "wash", "washing", "bedbugs", "bed bugs",
                     "hot", "heat", "sweating", "sweaty", "wet", "wee", "accident", "hotel",
                     "breakfast", "holiday", "baby", "babies", "toddler", "child", "my son",
                     "my daughter", "my dog", "the dog", "my cat", "the cat", "sick", "vomit",
                     "hospital", "care home")),
        entry("fan-vs-aircon",
              (("fan", "aircon", "air con", "air conditioning", "air conditioner"),
               ("cheaper", "cheap", "cost", "run", "running", "expensive", "electricity", "worth")),
              "A fan costs a penny or two an hour; a portable air conditioner is more like 30 to 50p, "
              "and a fitted one more again. A fan only cools you, not the room, so put it in front of "
              "an open window at night with another window open across the room. A bowl of ice in front "
              "of a fan helps in dry heat, not in humidity.",
              avoid=("laptop", "computer", "pc", "console", "playstation", "xbox", "car", "engine",
                     "oven", "extractor", "boiler", "server"),
              ask=("cheaper", "cheap", "cost", "expensive", "electricity", "air con", "aircon",
                   "air conditioning", "hot", "cool", "cooling", "heatwave", "summer", "worth")),
        # "Is it cheaper to run the dishwasher or wash by hand": any two things in RUNNING are
        # compared from that one table, and one thing named on its own gets its figure.
        # "how long do washing machines last": the lifespan table above, one row per appliance.
        # "years" on its own is not a key: "my tumble dryer is 9 years old" is the age said as
        # context for a fault, and it was claiming the lifespan answer.
        entry("appliance-life", (LIFE_NAMES, LIFE_ASK),
              _lifespan, ask=LIFE_ASK,
              # "what is the life expectancy of a tumble dryer" ties with explains.explain-tumble-dryer
              # at six: the machine and the ask score the same for both, and a tie goes to the earlier
              # entry, which is the mechanism. How long it lasts is this row's question and the
              # mechanism is not an answer to it, so the tie is broken here rather than by standing
              # every explanation down on the word "lifespan", which would leave a solar panel - not
              # in this table - with nothing. Four, because every explanation carries its own bias and
              # a rarity bonus for a name only it uses ("tumble", "dryer"): the tumble dryer's
              # explanation ranks 9 against this row's 8 at three and 6 at two, so three ties and the
              # registry order hands the line to the explanation. The other appliance-life row used to
              # carry this bias and win the tie; with the duplicate gone, it is this row's job.
              # A pan cooling before the washing-up is not a pan at the end of its life: "how long
              # should i cool a pan before washing" matched "frying pan" and "how long" here as well
              # as on the wash cycle.
              # "worth" on its own is the buying question ("is it worth it"), but it is also half
              # of "is it worth replacing", which is this row's own question: the bare word vetoed
              # the most common way people ask it, so only the buying sense is fenced now.
              avoid=LIFE_GUARD + JOB_GUARD + ("broken", "quote", "worth it", "worth buying",
                                              "worth the money", "worth paying", "cool", "cooling",
                                              "cool it", "cool the pan", "before washing",
                                              "washing it", "wash the pan", "before i wash"), bias=4),
        # "When should I replace my mattress" belongs to the years table above - it has the age
        # and the rule that says when the thing is finished - but its key is the lifespan
        # phrasing, so the replace question fell to shopping's mattress-buy and was told what to
        # look for in a shop. One row for the thing people ask this about: the name plus the
        # replace words, and the buying, cleaning and turning rows keep their own lines.
        entry("bedding-finished", (("mattress", "mattresses"),
                                   ("replace", "replacing", "replacement", "replaced",
                                    "when to replace", "time to replace", "new one",
                                    "need a new", "need a new one")),
              _lifespan, bias=2,
              # a purchase is shopping's, and a stain, a wash or a turn is the rows above
              avoid=("buy", "buying", "bought", "cost", "costs", "price", "prices", "cheap",
                     "cheaper", "budget", "spend", "shop", "shops", "store", "topper",
                     "protector", "clean", "cleaning", "wash", "washing", "stain", "stains",
                     "smell", "smells", "turn", "turning", "flip", "flipping", "rotate",
                     "rotating", "cover", "covers", "sheet", "sheets", "pillow", "pillows",
                     "duvet", "duvets",
                     # "i need a new mattress, how do i choose" was this row's lifespan answer,
                     # because "need a new" is its own ask and the pick was left in the words.
                     # Chosen is shopping's question (mattress-buy), and it reads the line for
                     # which one, so this row stands down for the choosing words.
                     "choose", "choosing", "chose", "pick", "picking", "which one",
                     "what should i look for", "how do i choose", "help me choose"),
              ask=("replace", "replacing", "replacement", "replaced", "when to", "new")),
        entry("running-cost", (RUNNING_WORDS, COST_WORDS), _running,
              avoid=("broken", "break", "repair", "install", "frost", "iced", "ice", "defrost",
                     # a repair is priced by the engineer, not by the unit of electricity: "how much
                     # does it cost to fix a washing machine" got the pence-per-cycle figure.
                     "fix", "fixing", "fixed", "mend", "mending", "engineer", "call out", "spare",
                     "won't", "wont", "doesn't", "doesnt", "does not", "stopped", "spin", "hair",
                     "smell", "smells", "leak", "noise", "noisy", "not working", "cold", "filter",
                     "clean", "car", "engine", "laptop", "phone", "tablet", "pc", "console",
                     "playstation", "xbox", "extractor", "buy", "buying", "getting",
                     # a service or a repair is a price, not a bill
                     "service", "servicing", "serviced", "repair",
                     # a thing swapped for another thing is priced fitted, not by the unit of
                     # electricity: "is replacing a bath with a shower expensive" got the pence
                     # for five minutes of hot water. The same holds for any swap - a boiler, a
                     # window, a shower - so it is one rule here rather than a word in each row.
                     "replace", "replaces", "replacing", "replaced", "replacement",
                     "swap", "swaps", "swap out", "swapping", "swapped", "rip out",
                     "ripping out", "fit a", "fitting a", "fitted a",
                     "get one", "worth getting", "cups", "water for", "fill", "best", "new",
                     # which one to buy is a shopping question: "what is a good cheap slow cooker"
                     # took "cheap" as the cost word and was told the pence per hour, when the
                     # buying row has the £30-against-£100 answer. "cost" and "cheaper" keep their
                     # own lines ("how much does it cost to run a slow cooker").
                     "good", "a good", "good cheap", "good and cheap", "recommend", "recommended",
                     "worth", "worth it", "which one", "which one to", "should i buy",
                     "should i get", "what to buy", "to buy",
                     # a fan against air con is a cooling question, and that entry has the tips
                     "air con", "aircon", "air conditioning", "air conditioner",
                     # the hour is the tariff row's question, not pence per cycle: "what is the
                     # cheapest time to put the washing machine on" was priced as a cycle instead.
                     "what time", "cheapest time", "time of day", "off peak", "off-peak",
                     "in the morning", "in the evening", "during the day",
                     # "is it cheaper to leave the heating on all day" is a habit question, not an
                     # hourly figure, and `heating-all-day` has the timer and the 18C setting.
                     # "leave on" does not catch "leave the heating on", because the thing being
                     # left sits between the two words, so the heating's own phrases are named too.
                     "leave on", "leaving on", "left on", "all day", "all the time", "overnight",
                     "leave the heating on", "leaving the heating on", "left the heating on",
                     "keep the heating on", "keeping the heating on", "heating on all day",
                     "heating on all the time", "heating on low", "heating on at night",
                     "timer", "timed", "thermostat", "flow temperature",
                     # a bath is also a city, a bath bomb and a bath mat, and a shower is weather
                     "hotel", "hotels", "bath bomb", "bath bombs", "bath mat", "bath mats",
                     "bath towel", "bath towels", "bird bath", "swim", "swimming", "baby", "babies",
                     "dog", "dogs", "cat", "cats"),
              ask=COST_WORDS, bias=2),
        entry("freezer-defrost",
              # a fridge that has iced up is the same defrost question: the drain-hole row stands
              # down on `ice on the walls` / `full of ice` now, so the fridge words have to be here
              # or the line falls through to a shrug
              (("freezer", "freezer drawer", "icebox", "fridge", "fridges", "refrigerator"),
               ("defrost", "defrosting", "ice", "icing", "iced", "frost", "frosting", "froze",
                "frozen", "icy", "thick", "needs")),
              "Defrost it when the ice is more than about 5mm thick: switch it off at the wall, move "
              "the food into a cool box, and leave bowls of hot water inside with the door shut. Budget "
              "two to three hours, or overnight leave it with the door open and towels down. Never "
              "chip at the ice with a knife, because a pierced pipe writes the freezer off. The "
              "reason is moist air getting in every time the door opens.",
              # "how do i stop my freezer frosting up" ties with the first aid for a machine that will
              # not start, which takes the word "stop": the ice is the subject of the line, so this
              # card goes first
              # "do you need to keep rice in the fridge" is a keeping question: "needs" matched
              # `needs`, and the food the line was about went out of it, so the answer was how to
              # defrost a freezer. A food *named* in the line stands this row down - named, not
              # the words `food` and `leftovers`, which turn up in the defrost questions themselves
              # ("why is there ice on the food in my freezer", "is my food ruined") and took the
              # ice away from the card that is about the ice.
              avoid=("rice", "pasta", "bread", "milk", "meat", "chicken", "eggs", "butter",
                     "cheese"),
              bias=2),

        # A freezer that needs defrosting is the row above. This is the other question: a fridge that
        # ices up when it is meant to look after itself, which is a fault with a cause. "my fridge is
        # icing up" was "Noted: your fridge is icing up" and "how do i stop my fridge icing up" was
        # the dead-appliance answer, so both shapes had nothing.
        entry("fridge-frost",
              (("fridge", "fridge freezer", "ice box", "freezer box", "freezer compartment"),
               ("frost", "frosts", "frosting", "frosted", "icing", "icing up", "ices up", "iced up",
                "ice", "icy", "ice building up", "build up of ice", "frozen up", "freezing up",
                "thick ice", "snow", "back wall", "back of the fridge", "icicles")),
              "Ice in a fridge that is meant to look after itself comes from one of three things: a "
              "door seal that no longer grips (shut a strip of paper in the door and pull - it should "
              "drag), the drain hole at the back of the fridge blocked so the water freezes there, or "
              "food pushed against the back wall. Fix the seal and clear the drain and the ice stops "
              "coming back. Get rid of what is there by defrosting it properly with the door open "
              "overnight, and never chip at it with a knife.",
              # the defrost row above, the water-in-the-bottom row, the smell and clean rows, and a
              # dead appliance are all other answers
              avoid=("defrost", "defrosting", "not cold", "warm", "noise", "noisy", "smell", "smells",
                     "clean", "cleaning", "repair", "replace", "buy", "cost", "broken", "dead",
                     "leaking", "drain hole", "water", "freezer", "chest freezer", "freezer drawer",
                     "temperature", "setting", "worth"),
              # the water-in-the-bottom row holds the drain hole, and it answered "ice on the back wall
              # of my fridge" first; the cause here is the same fault, so this one leans in
              bias=2),


        # "its a frost free one" and "how often should i defrost it" are the two follow-ups to the
        # defrost answer, and neither names the freezer, so neither reached it. The first was the
        # defrost instructions said back with "For a frost free one, the same:" in front of them,
        # which is the wrong way round - a frost-free freezer does its own defrosting, and one that
        # ices up has a seal or a vent letting warm air in. The second was the refreezing-the-food
        # rule, because the bare word "defrost" is enough for that row. Two rows, because they are
        # two different questions: whether to defrost at all, and how often.
        entry("frost-free-freezer",
              (("frost free", "frost-free", "frostfree", "no frost", "auto defrost", "auto-defrost",
                "self defrosting", "never needs defrosting"),
               ("freezer", "freezers", "icebox", "fridge freezer", "frost", "frosts", "frosting",
                "frosting up", "frosts up", "ice", "ices", "icing", "iced", "one", "it", "that",
                "needs", "defrost", "defrosting")),
              "A frost-free freezer never needs defrosting by hand: it clears its own frost, so ice "
              "building up means the door seal has gone or the vent behind it is blocked. Check the "
              "gasket all round the door with a sheet of paper (it should grip), and a new seal is a "
              "cheap fix.",
              # the buying question is `worth-an-appliance`'s: this row is about the ice in a machine
              # somebody already has
              avoid=("buy", "buying", "worth", "cheaper", "cheapest", "best", "which", "recommend"),
              bias=1),
        entry("how-often-to-defrost",
              # The machine's own defrosting, said any of the ways people say it. The food's
              # defrosting is another row, and the freezer words in the second part are what keep
              # these apart: a bare "needs defrosting" on its own does not reach this row.
              (("defrost a freezer", "defrosting a freezer", "best way to defrost", "way to defrost",
                "should i defrost it", "shall i defrost it", "do i defrost it", "needs defrosting",
                "needs a defrost", "needs defrosting out", "how often should i defrost",
                "how often do i defrost", "how often to defrost", "when should i defrost",
                "defrost the freezer", "defrost my freezer", "defrost it now"),
               ("freezer", "freezers", "icebox", "fridge freezer", "ice", "icing", "frosting",
                "how often", "often", "how many times", "once a year", "twice a year", "yearly",
                "frequency", "every few months")),
              "At about 5mm of ice, switch it off at the wall and move the food into a cool box: "
              "budget two to three hours, or overnight with bowls of hot water inside and the door "
              "shut."
              " Most freezers need this once or twice a year. Never chip at the ice, because a "
              "knife can pierce a pipe and write the freezer off, and a frost-free one never needs "
              "it at all, so ice in one means the door seal has gone.",
              # defrosting the food, not the machine: the thigh, the chicken and the loaf keep their
              # own answers, and so does the fridge's thawing method
              avoid=("chicken", "meat", "mince", "turkey", "fish", "prawns", "sausages", "beef",
                     "pork", "lamb", "bread", "pastry", "cake", "food", "the food", "from frozen",
                     "thaw", "thawing", "thawed", "for dinner", "before cooking", "cook it"),
              # "my freezer needs defrosting shall i do it now" reached the take on whether a freezer
              # is worth buying, which names the same machine and the word "need": the take ties this
              # row even with one point of nudge, so it takes two
              bias=2),
    ]
