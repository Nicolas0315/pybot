"""Rows 5 of 10 of `home_craft.entries()`: `paint-streaks` .. `thing-part-hurts`.

The rows are exactly as they were in `entries()`, in the same order; `entries()` joins the parts.
This module is imported from inside `entries()`, which `home.py` calls after `home_craft` is
fully loaded, so it can take the helpers it needs from `home_craft` at the top.
"""
from ..knowledge.home_craft import (
    _a_chair_and_not_a_body,
    _the_fan_stopped,
)


def rows():
    from ..knowledge.home import (
        FITTING_SHARED_STANDDOWN, LETTING, THING_PARTS, _TAKING_PAINT_OFF,
        _a_thing_owns_the_part, _fitting_repair, _paint_brush_care, _the_paper_is_in_the_line,
        entry, the_stomach_is_what_it_is_about
    )
    return [
        # The line that describes the finish rather than the job - "without streaks", "avoid roller
        # marks", "why is my paint patchy", "a smooth finish" - had no answer of its own: the walls
        # went to the shopping list, the roller marks to the search hedge, and "brush marks" to
        # brushing your teeth, because "brush" is a toothbrush word as well. The word that carries
        # the question is the fault, so the fault is the key and the paint is the fence.
        entry("paint-streaks",
              (("paint", "painting", "painted", "repaint", "emulsion", "gloss", "satin", "eggshell",
                "undercoat", "topcoat", "roller", "brush", "decorating", "decorate",
                "the walls", "wall", "walls", "woodwork"),
               ("streak", "streaks", "streaky", "streaking", "patchy", "patchiness",
                "roller marks", "roller mark", "brush marks", "brush mark", "lap marks",
                "lap mark", "lines", "smooth", "smooth finish", "even finish", "finish",
                "uneven", "blotchy", "flashing", "shiny patches", "shiny patch",
                # the denial reader drops a key made of a word inside "without", and "without
                # streaks" is the commonest way people ask for this, so the phrase carries its
                # own "without" and is passed instead
                "without streaks", "without streak", "no streaks", "not streaky",
                "without brush marks", "no brush marks", "without roller marks",
                "no roller marks", "without lap marks", "no lap marks", "without lines",
                "no lines", "not patchy", "no patches", "without patches")),
              "Streaks are an uneven coat, not a bad paint: roll in strips a roller wide and lap the "
              "last strip while it is still wet so no edge dries alone, with a light even load rather "
              "than pressing the roller dry. Brush slowly, one way, and don't go back over paint that "
              "is setting. On a wall already patchy, a second full coat cures it; touching up spots "
              "makes it worse.",
              avoid=_TAKING_PAINT_OFF + (
                     "off", "clean", "cleaning", "wipe", "scrub", "scuff", "scuffs", "fingerprint",
                     "fingerprints", "stain", "stains", "stained", "crayon", "pencil", "pen",
                     "marker", "dirty", "grease",
                     # the pieces of wood and board each have their own card, and it is a better
                     # answer to "how do i paint a door without brush marks" than this one
                     "door", "doors", "ceiling", "ceilings", "skirting", "radiator", "radiators",
                     "tiles", "cupboard", "cupboards", "kitchen unit", "kitchen units", "shed",
                     "fence", "fencing", "deck", "decking", "garden", "furniture", "wardrobe",
                     "table", "chair", "chairs", "bathroom", "wallpaper", "woodchip",
                     # nail polish is a paint that goes on a person, and "brush marks on my nails"
                     # was the nails card's line before this row touched it
                     "nails", "nail", "my nails", "toenails", "fingernails", "manicure",
                     "nail polish", "nail varnish", "polish", "pedicure")),
        # "how do i thin emulsion" and "should i water down gloss" were the search hedge: the paint
        # rows talk about coats and surfaces, and nothing said how much water or spirit to add.
        # A brush is not the wall. "How do i store paintbrushes between coats" was answered with how
        # many coats a wall wants, "what do i do with the brush between coats" went to the charity
        # clothes card, and "can i wrap the brush in cling film overnight", "how do i clean a brush
        # after emulsion" and "my paintbrush has gone hard" reached nothing at all. The tool and its
        # keeping are one question, so the brush words are the key and the keeping is the ask.
        entry("paint-brush-care",
              (("brush", "brushes", "paintbrush", "paintbrushes", "paint brush", "paint brushes",
                "brush bristles", "bristles", "bristle", "roller", "roller sleeve", "paint roller",
                "sleeve", "sleeves"),
               # `store`, `storing`, `stored` are ask words, not key words: with a keeping word in
               # the key the row looks like a shelf-life row, and `lookup._keeps_failing` stands a
               # shelf-life row down when the line says a fault keeps happening - which is exactly
               # "my brush keeps losing bristles", the shape this row exists for.
               ("between coats", "between the coats", "overnight", "over night",
                "keep", "keeps", "keeping", "kept", "clean", "cleaning", "cleaned",
                "wash", "washing", "washed", "wash out", "washing out", "rinsed", "rinse",
                "gone hard", "went hard", "hard", "stiff", "dried out", "drying out", "dry out",
                "wrap", "wrapped", "cling film", "clingfilm", "carrier bag", "plastic bag",
                "save", "saved", "reuse", "re-use", "next coat", "tomorrow", "lunchtime",
                "white spirit", "turps", "brush restorer", "soak", "soaking",
                # "how do i get paint out of a paintbrush" named the brush and a removal and no care
                # verb at all, so the row looked past it and the answer was the search hedge
                "out of", "get out", "got out", "get the paint out", "get paint out", "remove",
                "removing", "cleaned up", "clean up", "after painting", "once i have finished",
                # "how do i get oil paint off a brush" is the same wash with none of the wash words,
                # and it was the search hedge while "how do i clean a brush" was answered
                "off a brush", "off my brush", "off the brush", "off a paintbrush",
                "off my paintbrush", "out of a brush", "out of my brush", "out of the brush",
                "out of my paintbrush", "out of a paintbrush", "out of the bristles",
                "off a roller", "out of a roller", "out of the sleeve", "get it off",
                "get the paint off", "paint off",
                # a brush that sheds is the same tool with a fault, and the line usually says what
                # it does rather than what it wants: "my brush keeps losing bristles"
                "losing bristles", "loses bristles", "lose bristles", "lost bristles",
                "keeps losing", "keep losing", "losing hair", "sheds", "shedding", "shed",
                "falling", "falling out", "coming out", "keeps coming out",
                "bristles falling out", "bristles coming out", "loose bristles", "moulting",
                "falling apart", "falls apart", "coming apart", "comes apart")),
              _paint_brush_care, bias=3,
              # a brush that sheds is stated as a fact rather than asked about: "my brush keeps
              # losing bristles" is the whole question, so the fault words are ask words of their own
              ask=("how do i", "how to", "what do i do", "can i", "should i", "between coats",
                   "overnight", "store", "keeping", "keeping it", "clean", "cleaning", "wash",
                   "washing", "save", "reuse", "gone hard", "went hard", "hard", "stiff",
                   "dried", "dry", "wrap",
                   "losing", "loses", "lose", "lost", "sheds", "shedding", "shed", "moulting",
                   "falling", "coming out", "keeps coming out", "keeps losing", "keep losing",
                   "falling apart", "coming apart"),
              # a hair brush, a toothbrush and a yard brush are other questions, and so is art on a
              # canvas: the paint in this one is on a wall, a door or a skirting board.
              avoid=("hair", "my hair", "hairbrush", "hair brush", "curling", "straighteners",
                     "teeth", "toothbrush", "tooth", "gums", "makeup", "make up", "make-up",
                     "foundation", "blush", "eyebrow", "eyeliner", "nail brush", "nails",
                     "bbq", "barbecue", "grill brush", "chimney", "sweep", "yard", "broom",
                     "snow brush", "dog", "cat", "pet", "grooming", "canvas", "watercolour",
                     "watercolor", "sketch", "draw", "drawing", "brush up", "brush off",
                     "brush past", "brushed off", "paintbrush plant", "shaving brush",
                     "toilet brush", "bottle brush", "bottlebrush", "basting", "pastry brush",
                     # a blind, a curtain and a shirt sleeve are not a paintbrush, and `blind` and
                     # `sleeve` in the key were taking them: "how do i clean roller blinds" and
                     # "how do i clean a shirt sleeve stain" both had good answers before this row
                     "blind", "blinds", "curtain", "curtains", "shirt", "shirts", "jumper",
                     "jumpers", "cardigan", "fabric", "upholstery", "sofa", "settee", "carpet",
                     "carpets", "duvet", "bedding", "stain", "stains", "clothes", "clothing",
                     # "its a shiny patch on the sleeve, can i save it" is a garment that has gone
                     # shiny, and "sleeve" is a key word here because of the roller sleeve, so the
                     # shine is what stands this row down: `shiny`, `shine`, `scorch` and the
                     # garments themselves, which are `clothing.garment-shine`'s line.
                     "shiny", "shine", "shines", "shone", "shininess", "scorch", "scorched",
                     "scotch", "jacket", "jackets", "blazer", "trousers", "skirt", "skirts",
                     "seat of my trousers")),
        # Paint spilt on something soft. The row sits here, beside the brush and the tin, rather
        # than at the end of the table: an append at the very end is where every lane adds, and it
        # is the one place that conflicts with everyone.
        entry("paint-spilt-on-a-soft-thing",
              (("paint", "paints", "emulsion", "gloss", "undercoat", "primer", "varnish",
                "gloss paint", "emulsion paint", "spilt paint", "spilled paint"),
               ("carpet", "carpets", "rug", "rugs", "sofa", "sofas", "settee", "couch", "cushion",
                "cushions", "mattress", "upholstery", "armchair", "stair carpet", "spilt", "spilled",
                "spill", "knocked over", "tipped over", "out of", "remove", "get out", "blot")),
              "Blot what is still wet with kitchen paper and do not rub it, because rubbing pushes the "
              "paint into the pile. Emulsion and the water-based satins lift with cold water and a "
              "little washing-up liquid worked in with your fingertips and blotted out again; oil "
              "gloss and varnish need a cloth damped with white spirit, dabbed from the edge of the "
              "mark inwards so it does not spread. Try white spirit on a corner you cannot see first, "
              "since on a wool carpet it can lift the dye.",
              # a pot of paint on a wall, a door, a floor or a brush is somebody else's line, and so is
              # a colour that came out wrong: "my gloss came out too dark" and "the paint came out
              # darker than the sample" were sent here for the cold-water treatment because they say
              # "came out", and no splashed carpet is the complaint
              avoid=("too dark", "darker", "too strong", "too bright", "too pale", "too orange",
                     "lighten", "lighter",
                     "wall", "walls", "ceiling", "door", "doors", "radiator", "skirting", "banister",
                     "window", "frame", "floor", "floors", "floorboards", "wood", "wooden",
                     "wallpaper", "clothes", "shirt", "jeans", "jumper", "trousers", "fabric",
                     "hand", "hands", "skin", "hair", "brush", "brushes", "paintbrush",
                     "paintbrushes", "paint brush", "paint brushes", "roller", "sleeve", "tray",
                     "thin",
                     "thinning", "dilute", "colour", "what colour", "which colour", "peeling",
                     "bubbling", "drying", "how long", "coats", "two coats",
                     # "old paint tins" is what to do with the tin, which is `paint-tins`' line
                     "old paint", "leftover", "left over", "tin", "tins", "bin", "bins", "tip",
                     "household waste", "recycling", "recycle", "dispose", "disposal", "shed",
                     "garage", "store", "storing", "keeping",
                     # a car's paint is not spilt on the carpet, however the line says "get it
                     # out": "how do i get scratches out of car paint" met this row on "paint"
                     # and "out of" and was told to blot the pile. The cars row answers it.
                     "car", "cars", "van", "vans", "bodywork", "paintwork", "bumper",
                     "bonnet", "scratch", "scratches", "scratched", "scuff", "scuffs",
                     "lacquer", "alloy", "alloys", "wheel", "wheels"),
              bias=2),

        entry("paint-thin",
              (("thin", "thinning", "thinned", "water down", "watering down", "watered down",
                "dilute", "diluting", "diluted", "white spirit", "white spirit in"),
               ("paint", "painting", "emulsion", "gloss", "satin", "eggshell", "undercoat",
                "topcoat", "varnish", "primer", "matt", "matt emulsion", "oil based", "oil-based",
                "water based", "water-based")),
              "Emulsion thins with water, about one part to ten of paint; oil-based gloss thins with "
              "white spirit at much the same rate. Add it a little at a time and stir until the paint "
              "runs off the stick in a steady ribbon. A first mist coat on new plaster is thinner "
              "still, about 20 to 30 per cent water. Don't thin to stretch a tin: it covers less, and "
              "that is where streaks come from.",
              avoid=("hair", "thinning hair", "my hair", "gravy", "sauce", "soup", "blood",
                     "trees", "tree", "apples", "hedge", "hedges", "seedlings", "paint stripper",
                     "stripper", "remove", "stripping")),
        entry("paint-ceiling", (("paint", "painting", "repaint", "mist coat"),
                                ("ceiling", "ceilings", "ceiling rose", "ceiling.", "roller",
                                 "emulsion", "white", "cover", "two coats")),
              "Do the ceiling first and the walls after. Cut in round the edges with a brush and a 2cm "
              "band, then roll in strips about a metre wide with a long-handled roller, overlapping "
              "the last strip while it is still wet so the edges do not dry into lines. Work away from "
              "the window and towards the light so you can see where you have been, and roll the last "
              "metre without reloading to feather it out. Put a dust sheet down because a ceiling "
              "always drips. Matt emulsion, two coats, and a ceiling that is already white may need "
              "only one: if it is a bare or patched ceiling, thin the first coat by about a tenth as a "
              "mist coat.",
              # taking paint OFF a ceiling, a damp patch, a leak, a stain and a crack are their own jobs
              avoid=_TAKING_PAINT_OFF + ("damp", "leak", "leaking", "water", "stain", "stains",
                                         "crack", "cracked", "crumbling", "flaking", "peeling",
                                         "coming off", "coming away", "come off", "comes off",
                                         "fell off", "falling off", "blown",
                                         "mould", "mold", "asbestos", "skim", "plaster",
                                         "insulate", "loft", "bulb", "light", "fan",
                                         "smoke alarm", "dryer", "colour", "color")),
        entry("paint-door", (("paint", "painting", "repaint", "gloss"),
                             ("door", "doors", "front door", "back door", "panelled door")),
              "Take the door off and lay it flat if you can, and paint the top and bottom edges first so "
              "it still fits after. Then the panels, then the frame parts, brushing with the grain. "
              "Lightly sand between coats and give gloss about 16 hours to harden before it goes back "
              "on its hinges.",
              # taking paint OFF a door is the stripping row below, and paint on your hands after
              # painting one is the hands row: this entry was answering "how do i remove paint from a
              # door" with "take the door off and paint the top and bottom edges first", and as a
              # follow-up it repeated itself at a person with paint on their hands
              avoid=("paint a room", "painting a room", "what colour", "which colour", "colour",
                     "sticking", "stiff", "squeak", "squeaking", "lock", "key", "handle",
                     "old paint", "hands", "hand", "fingers", "skin") + _TAKING_PAINT_OFF),
        entry("paint-radiator", (("paint", "painting", "repaint"),
                                 ("radiator", "radiators", "heated towel rail")),
              "Turn the heating off and let it go cold, then brush or roller it with a water-based "
              "satin, painting in the same colour as the wall if you want it to disappear. An old "
              "cast-iron radiator wants a metal primer first. Leave it a day to dry before the heat "
              "goes back on, or the paint softens.",
              avoid=_TAKING_PAINT_OFF),
        # A floor is its own paint and had no row at all: "how do i paint the floor", "...the
        # stairs" and "...floorboards" were punts once the hobby row stood down.
        entry("paint-floor", (("paint", "painting", "repaint", "floor paint", "sand"),
                              ("floor", "floors", "floorboard", "floorboards", "floor boards",
                               "stairs", "staircase", "stair treads", "steps", "wooden floor")),
              "Sand a wooden floor back to bare wood, vacuum the dust off, then a primer and two thin "
              "coats of floor paint, keeping a wet edge so the overlaps do not show. Ordinary "
              "emulsion will scuff off in weeks, so use a paint made for floors, and leave it a full "
              "24 to 48 hours before anything walks on it - a stair run wants that on both sides of "
              "each tread.",
              bias=1,
              # a floor that squeaks, is being tiled, is laminate or has been cleaned is a
              # different job, and tiles over a floor is the tile answer's
              avoid=("squeak", "squeaks", "creak", "creaks", "clean", "cleaning", "mop", "mopping",
                     "laminate", "tile", "tiles", "tiling", "carpet", "underlay",
                     "sanding machine", "hire", "sander") + _TAKING_PAINT_OFF),

        # A concrete floor is a different job from a wooden one, and while it was a sentence in
        # the floor row it was the sentence the repeat composer picked to follow "Same for
        # floorboards", so somebody with boards was told to etch concrete and buy garage paint.
        # One subject per row: this one names itself, and the floor row keeps the boards.
        entry("paint-concrete-floor", (("paint", "painting", "repaint", "floor paint", "etch",
                                        "seal", "epoxy"),
                                       ("concrete floor", "concrete floors", "garage floor",
                                        "garage floors", "concrete slab", "concrete steps",
                                        "concrete stairs")),
              "A concrete floor wants an etch and a paint made for it, not gloss: sweep and degrease "
              "it first, let it dry, then etch it with a weak acid or a floor etch from the paint "
              "shop so the paint has something to grip. Two coats of a garage-floor paint or a "
              "two-pack epoxy, rolled in one direction, with 12 to 24 hours between them, and keep "
              "feet and tyres off it for two or three days. Fresh concrete needs a month to cure "
              "before any of it, and a damp floor needs a damp-proof coat first.",
              bias=1,
              avoid=("squeak", "squeaks", "creak", "laminate", "tile", "tiles", "tiling", "carpet",
                     "floorboard", "floorboards", "wooden floor") + _TAKING_PAINT_OFF),
        # Varnish is not paint: the floor row's key claimed it and answered with "two thin coats
        # of floor paint", which is the wrong tin for somebody asking about varnish.
        entry("varnish-floor", (("varnish", "varnishing", "re-varnish", "revarnish", "lacquer",
                                 "stain", "staining"),
                                ("floor", "floors", "floorboard", "floorboards", "floor boards",
                                 "wooden floor", "stairs", "staircase", "stair treads", "steps")),
              "Sand the boards back to bare wood, vacuum and tack the dust off, then thin the first "
              "coat of varnish as the tin says and brush it with the grain. Three coats, with a "
              "light sand and a dust-off between each, and a full 24 hours between coats. A "
              "water-based varnish dries clear and does not yellow, so it suits pale wood; an "
              "oil-based one stands up better in a hall or on stairs but darkens pine. Keep the "
              "room ventilated and leave it two or three days before anything heavy walks on it.",
              bias=1,
              avoid=("squeak", "squeaks", "creak", "laminate", "tile", "tiles", "tiling", "carpet",
                     "concrete") + _TAKING_PAINT_OFF),
        entry("paint-skirting", (("paint", "painting", "repaint", "gloss", "satin"),
                                 ("skirting", "skirting board", "skirting boards", "architrave",
                                  "door frame", "banister", "banisters",
                                  # the rest of the painted wood in a room is this same job:
                                  # "how do i paint woodwork" and "...a windowsill" were punts
                                  "woodwork", "windowsill", "windowsills", "window sill",
                                  "window sills", "picture rail", "dado rail", "handrail",
                                  # a window frame is the same painted woodwork job and was a shrug:
                                  # "how do i paint a window frame" fell between the painting rows and
                                  # the two window-fault rows, which stand down on the brush
                                  "window frame", "window frames", "sash", "sash window", "window",
                                  "windows", "casement")),
              "Sand them, wipe the dust off and run masking tape along the carpet, then brush with the "
              "grain in long strokes and a light load on the brush so it does not run onto the wall. "
              "Two thin coats beat one thick one, and satin or eggshell is easier to wipe than gloss. "
              "If you are doing the walls too, do the woodwork first.",
              # A line that names the surface and a finish and asks nothing ("its gloss on the
              # woodwork") is a detail of the question already on the table, not a fresh how-to:
              # after "how long do i leave paint before the second coat" the wait was the
              # question, and this row's how-to took the turn. The ask words are ones the key
              # does not hold, because a word the key has already used cannot answer the ask too.
              ask=("how", "what", "which", "should", "can", "best", "way", "sand", "sanding",
                   "prep", "prepare", "method", "start", "need to", "give"),
              avoid=("clean", "cleaning", "dust", "dusty", "wipe") + _TAKING_PAINT_OFF),
        # A window frame is not a skirting board and it is not a picture either: "how do i paint a
        # window frame" and "how do i paint a sash window" were both given "start with acrylics...
        # paint the same simple thing - one mug, one window - five times", which is advice for
        # learning to paint pictures. Masking the glass and opening the window before the paint
        # sets are the two things that decide whether the job went well.
        entry("paint-window", (("paint", "painting", "repaint", "gloss", "satin", "undercoat",
                                "primer"),
                               ("window", "windows", "sash", "sash window", "sash windows",
                                "casement", "casement window", "window frame", "window frames",
                                "frame", "frames", "sill", "window sill", "window sills")),
              "Mask the glass with tape, or cut in at a shallow angle with a 25mm brush and keep the "
              "brush lightly loaded so it does not run onto the pane, and paint the frame before the "
              "sliding parts. On a sash window do the staff beads and the pulley recess first, then "
              "the sashes. Run a knife round the join and open the window a crack while the paint is "
              "still soft, or it dries shut; outside wants an undercoat and two coats of gloss on a "
              "dry day.",
              # a window that will not open, is painted shut, leaks or is being replaced is a
              # fault with its own answer, and so is the picture-painting question and the blind
              # "how do i paint a room with no windows" is a room, not a window, and it was
              # answered with this row's glass and sashes - so the room, the wall and the
              # windowless phrase all stand this one down
              avoid=("room", "rooms", "wall", "walls", "ceiling", "ceilings", "bedroom",
                     "living room", "hallway", "hall", "kitchen", "bathroom", "no window",
                     "no windows", "without windows", "windowless", "no natural light",
                     "clean", "cleaning", "cleaner", "dust", "dusty", "wipe", "condensation",
                     "misted", "leak", "leaks", "leaking", "damp", "draught", "draft", "cold",
                     "broken", "cracked", "crack", "shattered", "replacement", "replace", "tint",
                     "film", "frost", "blind", "blinds", "curtain", "curtains", "shutter",
                     "shutters", "stuck", "painted shut", "wont open", "won't open", "wont close",
                     "won't close", "acrylic", "acrylics", "watercolour", "canvas", "picture",
                     "painting of", "a painting") + _TAKING_PAINT_OFF,
              bias=2),


        entry("wallpaper-hang", (("hang", "hanging", "put up", "how do i paper", "paste the",
                                  # "how do i wallpaper a wall" was the search hedge: the verb is
                                  # the noun in this job, and nothing held it
                                  "wallpaper", "wallpapering", "papering", "paper a", "paper the"),
                                 ("wallpaper", "wall paper", "lining paper", "a wall", "the wall",
                                  "wall", "walls", "ceiling", "ceilings", "room")),
              "Size the wall and let it dry, then cut each drop with an extra 5cm top and bottom, paste "
              "the paper (not the wall) and let it soak for the time the roll says, and hang the first "
              "drop plumb from a pencil line rather than from a corner. Smooth it outwards from the "
              "middle with a paper smoother, and butt the joins rather than overlapping them. A "
              "ceiling is the same paper on a bigger job: paper it before the walls, and work away "
              "from the window.",
              # "hang", "put up" and "a wall" reach every other wall job there is, so the things that
              # get hung and put up are fenced off: a picture, a mirror, a shelf, a telly and a
              # curtain rail each have their own row, and so do plastering a wall and taking paper off
              # one. Nothing here is about papering over a wall. The bare verb is not the job, so
              # the paper itself has to be in the line.
              guard=_the_paper_is_in_the_line,
              avoid=("cheap", "which", "best", "bathroom", "mould", "mold",
                     "picture", "pictures", "frame", "frames", "photo", "photos",
                     "mirror", "mirrors",
                     "shelf", "shelves", "bracket", "brackets", "tv", "television", "telly",
                     "curtain", "curtains", "rail", "pole", "blind", "blinds", "coat", "coats",
                     "coat hook", "hook", "hooks", "light", "lights", "light fitting", "radiator",
                     "door",
                     # a fixing job carries the wall as its object, so the wall itself is the word
                     # that has to hold this row off: "how do i hang a picture on a plasterboard
                     # wall" was given the papering method
                     "plasterboard", "plaster board", "stud", "studs", "rawlplug", "rawplug",
                     "hollow wall", "drill", "drilling", "fixings", "fixing",
                     # not "plastering": avoid words match on the stem, and "a plaster wall" is
                     # the whole point of the row. Paint on paper is the other direction, and
                     # "can i paint over lining paper" is its own answer.
                     "doors", "skim", "skimming", "damp", "stain", "paint", "painting", "painted",
                     "paint over", "paint on top",
                     "stripping", "remove", "removing", "off")),
        entry("paint-tiles", (("paint", "painting", "repaint"),
                              ("tile", "tiles", "tiling", "bathroom tiles", "kitchen tiles")),
              "Tiles take paint if you use a tile-specific primer and two coats of tile paint, and it "
              "holds up well on a splashback or a wall above a bath. Sand the glaze dull and clean off "
              "any grease first, or the paint peels in sheets. Not worth it on a shower floor or "
              "anywhere a foot or a scouring pad goes: re-tiling is the honest fix there.",
              avoid=("grout", "clean", "cleaning", "mould", "black", "cracked", "crack", "loose",
                     "tile a", "how do i tile", "floor") + _TAKING_PAINT_OFF),
        entry("paint-garden-wood", (("paint", "painting", "repaint", "stain", "varnish", "preserve",
                                     "preserver", "treat", "wood stain"),
                                    ("fence", "fences", "shed", "sheds", "gate", "gates", "trellis",
                                     "decking", "pergola", "garden furniture", "garden table",
                                     "garden bench", "greenhouse", "greenhouses")),
              "Wait for two dry days above about 10C and get the surface clean and bone dry before you "
              "start, because paint on damp timber peels within a season. Then two thin coats rather "
              "than one fat one: fence panels want a shed-and-fence stain, a shed or a wooden gate a "
              "preservative and a topcoat, and a metal gate a rust primer and a gloss made for metal. "
              "Brush or spray along the grain on wood.",
              bias=1,
              avoid=("garden table", "weed", "lawn", "grow") + _TAKING_PAINT_OFF),
        # The pieces people name when they mean a thing to paint. Each of these was a punt once
        # the hobby row stood down (snug-parrot on #7159: every word a fence stands down on needs
        # a row behind it), and a chair and a table are the same sanding and priming job.
        entry("paint-furniture", (("paint", "painting", "repaint", "gloss"),
                                  ("cupboard", "cupboards", "wardrobe", "table", "tables", "dresser",
                                   "chest of drawers", "sideboard", "bookcase", "shelves", "shelf",
                                   "furniture", "kitchen cabinets", "kitchen cupboard",
                                   "cabinet", "cabinets", "kitchen unit", "kitchen units",
                                   "unit", "units", "chair", "chairs", "stool", "stools",
                                   "bench", "benches", "desk", "desks", "bed", "beds",
                                   "bed frame", "cot", "cots", "crib", "cribs", "toy", "toys",
                                   "toy box", "chest", "trunk", "picture frame", "photo frame",
                                   "mirror frame", "dressing table", "bedside table", "drawers")),
              "Sand or de-gloss the surface, wipe the dust off, then a stain-blocking primer, then two "
              "thin coats of a water-based satin with a light sand between them. Take the doors and "
              "handles off if it has them, and let it harden a good 24 hours before anything goes back "
              "on: furniture paint that is rushed stays soft and sticks.",
              avoid=("clean", "cleaning", "smell", "musty", "grease", "polish", "wax", "dust",
                     "undercoat", "satin") + _TAKING_PAINT_OFF),
        # Taking paint off is the other half of the job, and it is not painting the thing: the rows
        # above take the thing painted as their key, so without this a person with old paint on a
        # door was told how to add more.
        # "why is my ceiling paint flaking" is a diagnosis, and paint-strip answered it with a heat
        # gun: the removal row keys "flaking" and "peeling" because those are how people say "get it
        # off", so a question about *why* it let go got the tool for taking it off. The two rows are
        # now told apart by the ask: a how-to remove keeps the strip, a why-it-happens gets this.
        entry("paint-flaking",
              (("flaking", "flaky", "flaking off", "flake off", "flakes off", "peeling off",
                "bubble", "bubbles", "bubble up", "bubbles up",
                "peels off", "peeled off", "peeling", "blistering", "blistered", "bubbling",
                "bubbled", "blown plaster", "coming off the wall", "coming off the ceiling",
                "coming away from the wall", "paint is flaking", "paint flaking",
                "paint is peeling", "paint peeling",
                # paint that has let go of the surface is the same question said the other way:
                # "paint coming away from the ceiling" was the painting-order card, and once that
                # card was told to stand down it had no answer at all.
                # The noun rides in the phrase. "fell off", "came off" and "coming off" on their
                # own were the whole subject, and this row's other half already holds wall,
                # walls, ceiling and bathroom, so anything that came off a wall was a paint
                # question: a mirror, a picture and a tile all got "find the reason before you
                # repaint". Said with the paint in it, every tense keeps its answer.
                "paint coming off", "paint is coming off", "paint come off",
                "paint comes off", "paint came off", "paint has come off",
                "paint coming away", "paint is coming away", "paint came away",
                "paint falling off", "paint is falling off", "paint fell off",
                "paint has fallen off"),
               ("paint", "painted", "painting", "emulsion", "gloss", "ceiling", "wall", "walls",
                "woodwork", "wood", "skirting", "door", "doors", "radiator", "plaster", "bathroom",
                "kitchen", "why", "what causes", "cause")),
              ("Find the reason before you repaint, or it comes back: feel the patch for damp (a "
               "bathroom, a kitchen or a ceiling under a cold roof is the usual one), and press the "
               "plaster - if it crunches or sounds hollow it has blown and needs cutting back to "
               "sound plaster and filling. Paint flakes off a ceiling most often because an old "
               "distemper or silk finish was painted over without a primer, or bare plaster was "
               "painted without a mist coat, so scrape back to the firm edge, sand the edge flat, "
               "and prime the bare patch before you paint. Then two coats of the same finish, and "
               "deal with the steam or the leak, because paint cannot hold on a wet wall."),
              # the same four-word score as the broad paint-room row and the soap-bubble row on
              # "why does paint bubble on a wall", so this one has to win the tie: it is the only
              # row about the paint letting go.
              bias=1,
              avoid=("remove", "removing", "removal", "strip", "stripping", "get off", "take off",
                     # paint that came off a hand, a brush or a tin is not paint that let go of a
                     # wall: the hands row and the tins row answer those.
                     "my hands", "hands", "hand", "fingers", "skin", "nails", "brush", "brushes",
                     "roller", "tin", "tins", "clothes", "carpet", "splash", "spilled", "spilt",
                     "sand off", "scrape off", "how do i get", "nail polish", "nail varnish",
                     # "old paint" is the stripper row's phrase, kept so by its own tests: "old paint
                     # is peeling on my door" is a door to take back to bare wood, not a wall to
                     # diagnose.
                     "old paint", "layers of paint", "years of paint",
                     "wallpaper", "wall paper", "skin", "hands", "brush", "nail", "nails",
                     "car", "cars", "metal", "gate", "fence", "shed", "boat", "kerb", "wheel",
                     # a tile that has come off a wall is not paint that let go of it: the tile
                     # repair row answers that, and this row read "a tile has come off the wall in
                     # my bathroom" as a paint diagnosis.
                     "tile", "tiles", "tiling", "grout")),

        entry("paint-strip", (("remove", "removing", "strip", "stripping", "get off", "take off",
                               "sand off", "sanding off", "peel", "peeling", "flaking", "flaky",
                               "old paint", "layers of paint",
                               # "how do i get paint off tiles" has no removal verb but does have the
                               # word off, and it tied with the tile-painting row without this
                               "off"),
                              ("paint", "painted", "gloss", "varnish", "emulsion", "woodwork", "wood",
                               "door", "doors", "skirting", "banister", "door frame",
                               "radiator", "tiles", "stair")),
              "Work out which paint it is first: a heat gun or a chemical stripper lifts old oil gloss "
              "in a few minutes, while a water-based paint softens under a warm damp cloth. Sandpaper "
              "alone clogs in seconds on a thick layer, so strip the bulk and sand only the last film. "
              "Test anything painted before about 1960 for lead - a kit costs a few pounds - and never "
              "sand that one.",
              # paint on skin, on a brush or on a carpet is a different job with a different answer
              avoid=("wallpaper", "wall paper", "stain", "stains", "nail polish", "nail varnish",
                     # why it let go is `paint-flaking`; this row is how to take it off
                     "why is", "why does", "why has", "why are", "what causes", "blistering",
                     "blistered", "bubbling", "bubbled", "keeps flaking", "keeps peeling",
                     "flaking off the wall", "flaking off the ceiling", "peeling off the wall",
                     "brush", "brushes", "roller", "hands", "hand", "fingers", "skin", "carpet",
                     "clothes", "shirt", "washing machine",
                     # a colour, not a job: "how do i paint a wall off white"
                     "off white", "off-white", "white", "colour",
                     # and taking a door off is how you paint one, not a stripping question:
                     # "should i take the door off to paint it" was handed the paint stripper
                     "off to paint", "to paint it", "when painting", "before painting",
                     "before you paint", "to paint the",
                     # a tin nobody is going to open is not a surface: "what do i do with old paint"
                     # and "can i put old paint in the bin" were handed the heat gun, because "old
                     # paint" is in this key and the tin row's own key needs the surface word this
                     # one has. The disposal words belong to `paint-tins`, so they stand this row
                     # down - and a surface word still wins, because "old paint on the door" carries
                     # "the door" and not one of these.
                     "what do i do", "should i do", "what should i do", "do with", "get rid",
                     "in the bin", "put it in the bin", "where do i take", "throw", "throwing",
                     "chuck", "chucking", "bin it",
                     "dispose", "household waste", "recycling centre", "leftover", "tins", "pots",
                     # a tin of paint left over is the disposal row's question, not a stripping job
                     "tin", "tins", "dispose", "disposal", "recycling centre", "tip",
                     # the row keys on "remove" and "wood", so "how do i remove a scratch from wood"
                     # came here and was told about a heat gun; a mark in the finish is not old paint
                     "scratch", "scratches", "scratched", "scratching", "scuff", "scuffs",
                     "scuffed", "mark", "marks", "marked", "dent", "dents", "dented",
                     "chip", "chips", "chipped", "ring", "rings", "water mark", "heat mark",
                     # the bare "off" in the key above is what makes this the answer to a stripping
                     # job, and it also made it the answer to every line that turns something off:
                     # "how do i turn a radiator off" and "how do i switch a radiator off for the
                     # summer" were told how to lift old gloss with a heat gun. A device switched off
                     # is not paint coming off, so the switching verbs stand this row down.
                     "turn off", "turning off", "switch off", "switching off", "shut off",
                     "shutting off", "turn it off", "turn them off", "switch it off",
                     "turn the radiator off", "turn a radiator off", "turn a rad off",
                     "turn the heating off", "turn them down"),
              # "how do i get paint off tiles" is the same job as stripping a door, and it ties with
              # the tile-painting row on score, so the removal row is the one that leans in
              bias=1,
              # A stripping job names the paint, and the paint is this row's own subject, so it is
              # not a word the reading may borrow from the turn before. Without this, "off" from one
              # turn and "door" from the next added up to a removal word and a surface, and a
              # smoke-alarm chat ("the fire alarm goes off when i have a shower" / "its right
              # outside the bathroom door") was handed the paint stripper.
              ask=(("paint", "gloss", "varnish", "woodwork", "wood", "skirting", "banister",
                    "emulsion", "undercoat", "primer", "lacquer",
                    # A person stripping a door often names the finish rather than the paint:
                    # "how do i remove the old finish off my door" was the stripper's line before
                    # the gate went on and a hedge after it. None of these words stands alone in the
                    # key, so a line that says "what finish should i use on oak" still never scores
                    # here; "strip" is deliberately not one of them, because a strip light flickers.
                    "finish", "finishes", "paintwork", "bare wood",
                    # "how do i strip a door" names the job and the surface and no paint at all, and
                    # the gate refused it: main answered it and this row was the answer. The job verbs
                    # belong with the subject words, so the line that says "strip" is a stripping job.
                    "strip", "strips", "stripping", "stripped", "sand", "sanding", "sandpaper"),)),
        entry("paint-on-hands", (("paint", "painting", "painted", "gloss", "emulsion", "varnish",
                                  "undercoat",
                                  # a wood stain on the hands is a paint on the hands, and the wood
                                  # care rows took it because "stain" is their word
                                  "wood stain", "woodstain", "wood dye", "wood stain on"),
                                 ("hands", "hand", "fingers", "skin", "nails", "fingernails",
                                  "arms", "arms and hands")),
              "Warm water and washing-up liquid takes water-based paint off skin while it is still "
              "tacky, and a soft nail brush lifts it out of the ridges. Oil gloss wants a little white "
              "spirit or baby oil on a cloth, then soap, then a moisturiser, because both dry the skin "
              "out. Keep white spirit off your face, a cut or a child, and let the last flecks wear off "
              "rather than scrubbing at them.",
              avoid=("wall", "walls", "car", "furniture", "nails painted", "paint my nails",
                     "paint your nails", "paint a", "painting a"),
              # "how do i get paint off my skin" ties with the row that stores a tin of paint,
              # and the tin won, so a person with paint on their arm was told how to keep a lid
              # tight. A part of a person in the line is this row's subject, not the tin's.
              bias=2),
        entry("red-wine-carpet", (("red wine", "wine"), ("carpet", "stain", "remove", "out", "spill")),
              "Blot it, don't rub, with kitchen paper, then pour on cold water and blot again, repeating "
              "until the water runs clear. A paste of bicarbonate of soda left on it for an hour pulls "
              "the rest out; white wine or salt are the old tricks and both work better than hot water.",
              # "can I open a bottle of red wine and leave it out" is a keeping question: a spill
              # answer needs something that the wine went on.
              ask=("carpet", "rug", "sofa", "couch", "cloth", "shirt", "dress", "tablecloth",
                   "spill", "spilt", "spilled", "stain", "stained"),
              # clothes have their own entry in the clothing domain, a sofa is the cleaning domain's
              # `wine-furniture`, and the cleaning domain's `red-wine-cloth` has the washable cloth, so
              # this one keeps carpets
              avoid=("shirt", "shirts", "dress", "dresses", "blouse", "top", "tops", "jeans", "trousers",
                     "skirt", "sweater", "jumper", "sofa", "couch", "settee", "armchair", "upholstery",
                     "chair", "cushion", "cushions", "rug", "curtain", "curtains", "tablecloth",
                     "napkin", "duvet", "pillow", "bedsheets", "linen")),
        # A carpet or a sofa stain with no substance named is the commonest version of the
        # question ("a stain on the carpet", "marks on the sofa"), and the substance entries -
        # red wine, coffee, nail polish - only answer when the line says what it was.
        # A rug that walks, slides or curls is its own small job, and every shape of it was a shrug or a
        # read-back: "how do i stop a rug from slipping", "my rug keeps sliding on the laminate", "the
        # corners of my rug wont lie flat".
        entry("rug-not-slipping",
              (("rug", "rugs", "mat", "mats", "runner", "runners", "doormat", "doormats",
                "carpet runner", "throw", "throws"),
               ("slip", "slips", "slipping", "slide", "slides", "sliding", "move", "moves", "moving",
                "shift", "shifting", "curl", "curls", "curling", "curled", "bunch", "bunching",
                "crease", "creases", "flat", "stay put", "stays put", "wont stay")),
              "Put a proper anti-slip underlay under it, the open-weave rubber sort, cut a couple of "
              "centimetres smaller than the rug, or run double-sided carpet tape along the edges: on a "
              "shiny floor the sticky corner pads do the job too. A rug that curls wants the curled end "
              "face down on the floor with something heavy on it overnight, or warmed with a hairdryer "
              "while you press it flat.",
              # cleaning a rug, a stain on it and buying one are each their own answer
              avoid=("clean", "cleaning", "wash", "washing", "shampoo", "stain", "stains", "stained",
                     "vacuum", "hoover", "smell", "smells", "smelly", "moth", "moths", "fade",
                     "faded", "colour", "color", "buy", "buying", "which", "best", "how much", "cost",
                     "price", "underlay", "new one", "shed", "sheds", "shedding", "underfloor",
                     "heating", "bath mat", "bathroom", "shower", "place mat", "placemat", "yoga",
                     "gym", "exercise", "mouse mat", "table mat", "towel", "iron", "ironing"),
              bias=1),
        entry("clean-furnishing",
              (("carpet", "carpets", "rug", "rugs", "mat", "mats", "sofa", "sofas", "couch", "settee",
                "armchair", "upholstery"),
               ("clean", "cleaning", "shampoo", "shampooing", "wash", "washing", "vacuum", "hoover",
                "dirty", "dirt", "freshen", "spring clean")),
              "Vacuum it first, then test any shampoo or foam cleaner on a hidden patch: a carpet wants a "
              "carpet shampoo worked in with a brush and rinsed, or a hired machine once or twice a year, "
              "and a sofa wants a foam cleaner and a soft brush with as little water as you can manage. "
              "Open the windows and dry it with the heating low, because anything left damp smells.",
              # a named stain, a named substance and buying or fitting one all have their own answers
              avoid=("red wine", "wine", "coffee", "tea", "cola", "juice", "nail polish", "nail varnish",
                     "blood", "paint", "oil", "petrol", "pet", "dog", "cat", "wee", "urine", "vomit",
                     "ink", "candle", "wax", "mark", "marks", "stain", "stains", "stained", "buy",
                     "buying", "which", "best", "underlay", "fitting", "fitted", "how much", "quote",
                     "leather", "suede", "new one", "cost", "price") + LETTING,
              bias=1),
        entry("carpet-stain",
              (("carpet", "carpets", "rug", "rugs", "mat", "mats"),
               ("stain", "stains", "stained", "mark", "marks", "spill", "spilled", "spillage",
                "remove", "get out", "get off", "mud", "blood")),
              "Blot, don't rub, with kitchen paper, then dab with cool water and a drop of washing-up "
              "liquid from the outside in, and blot dry with a towel; repeat until nothing more comes "
              "up. Work in small patches and never soak it, or the backing and underlay stay damp and "
              "start to smell. Grease wants neat washing-up liquid first, and a stain that survives all "
              "that is a job for a carpet cleaner.",
              # the substances have their own entries, and buying or fitting a carpet is not a stain
              avoid=("red wine", "wine", "coffee", "tea", "cola", "juice", "nail polish", "nail varnish",
                     "paint", "oil", "petrol", "pet", "dog", "cat", "wee", "urine", "vomit",
                     "ink", "candle", "wax", "turmeric", "buy", "buying", "which", "best", "underlay",
                     "fitting", "fitted", "how much", "quote", "vacuum", "hoover") + LETTING,
              bias=1),
        entry("sofa-stain",
              (("sofa", "sofas", "couch", "settee", "armchair", "upholstery", "footstool", "ottoman"),
               ("stain", "stains", "stained", "mark", "marks", "spill", "spilled", "spillage",
                "remove", "get out", "get off", "blood")),
              "Blot, don't rub, then dab with cool water and a drop of washing-up liquid from the "
              "outside in, and dry it with a towel rather than a hairdryer. Use as little water as you "
              "can, because a sofa takes days to dry and a damp one smells. A loose cover that unzips "
              "is better washed on its own; leather wants a barely damp cloth and saddle soap.",
              avoid=("coffee", "tea", "cola", "juice", "red wine", "wine", "nail polish", "nail varnish",
                     "buy", "buying", "which", "best", "new one", "replacement", "leather", "suede",
                     "how much", "cost", "price", "delivery", "second hand") + LETTING,
              bias=1),
        entry("grout-clean", (("grout", "tiles", "tile grout", "grouting"),
                              ("clean", "black", "mould", "dirty", "white", "whiten", "whitening",
                               "brighten", "yellow", "yellowed", "stained", "stain", "grimy", "grime",
                               # "seal" alone belongs to the bath and the shower more than to the
                               # joint, and with it here "how do i seal a bath round the tiles" was
                               # a grout scrub; the sealing this row means names the grout or tiles
                               "grout sealer", "sealer", "seal the grout", "sealing the grout",
                               "seal grout", "seal the tiles", "sealing the tiles", "seal tiles",
                               "seal my tiles", "sealing my tiles", "seal these tiles",
                               "scrub", "scrubbing", "brush", "steam", "steam cleaner",
                               # a room is only part of the thing, never a word of its own: on its
                               # own, "bathroom" made "how do i tile a bathroom" a grout-scrubbing
                               # answer, because "tile" alone satisfied the other half of the key
                               "bathroom grout", "shower grout", "grout in the bathroom",
                               "grout in the shower",
                               # grout that has failed is the same job as grout that is dirty, and
                               # it is the grout that is the subject here: "the grout is cracking in
                               # the corner of the shower" had no answer once the room came out of
                               # this key, because a cleaning word was all it had to offer
                               "cracking", "cracked", "cracks", "crumbling", "crumbly",
                               "missing", "falling out", "falls out", "come out", "coming out")),
              "Scrub the grout with a paste of bicarbonate of soda and water and an old toothbrush, then "
              "rinse. For black mould in the grout, use a mould spray and leave it 10 minutes. To whiten "
              "grey grout, a paste of bicarbonate and a little white vinegar left on for ten minutes "
              "lifts most of it, and an oxygen bleach (the laundry stain remover kind) left overnight "
              "takes the rest. Sealing the grout once it is dry keeps it that way for a year or two, "
              "and a grout pen is the quick fix if it is only the colour that bothers you.",
              # painting or tiling over the lot is a different job, and the tiling row owns those
              # lines. The whitening phrases are NOT here: standing this row down for "whiten tiles"
              # left the line to the tiling row, so somebody asking how to whiten a tile was told
              # how to lay one (broad-door, bronze-whistle and deft-lime all caught it). Whitening a
              # downstairs bathroom's tiles is usually the joint anyway, and this answer is the one
              # main gives.
              # and a cracked tile is the tile repair row's, not this one's: "how do i remove a
              # cracked tile" was a grout-scrubbing answer as soon as "cracked" joined this key
              avoid=("paint tiles", "paint the tiles", "cover the tiles", "tile the",
                     "cracked tile", "cracked tiles", "tile cracked", "tiles cracked",
                     "tile is cracked", "tiles are cracked", "cracked wall tile",
                     "replace a cracked tile", "remove a cracked tile")),

        # A tile that has let go of the wall, or of the floor, is a repair nobody had a card for:
        # "the tiles in my bathroom are coming loose" was a grout scrub before, and once the room
        # came out of the grout key it had no answer at all.
        entry("loose-tile",
              (("tile", "tiles", "wall tile", "wall tiles", "floor tile", "floor tiles"),
               # a tile that has let go of the wall or the floor. The words that mean the joint
               # itself are here too, because "the grout is cracking in a corner" ends in the same
               # repair, but nothing about laying, drilling, cleaning or choosing a tile is.
               ("loose", "loosening", "loosened", "coming loose", "came loose", "comes loose",
                "come off", "came off", "coming off", "falling off", "fell off", "fallen off",
                "lifting", "lifted", "hollow", "drummy", "wobbly", "popping", "popped",
                "move when i press", "moves when i press", "adrift",
                # a cracked tile comes off the same way, so it is the same job
                "cracked", "crack", "cracks", "split", "smashed", "broken tile")),
              "Tap it with the handle of a screwdriver: a hollow ring means the adhesive has let go, "
              "so the tile has to come off and go back properly rather than be patched. Score the "
              "grout round it, ease a thin scraper behind a corner and lift it out, then scrape the "
              "old adhesive off both the tile and the wall, spread flexible tile adhesive over the "
              "whole back with a notched trowel, press it home with a slight twist and tape it in "
              "place overnight before you regrout the joints.",
              # laying, drilling, cleaning, choosing and painting a tile are each another answer
              avoid=("lay", "laying", "tile a", "tiling a", "how do i tile", "start tiling",
                     "drill", "drilling", "screw", "hole", "hang", "hanging", "shelf", "mirror",
                     "clean", "cleaning", "cleaner", "grout pen", "mould", "mold", "black",
                     "whiten", "whitening", "paint", "painting", "cut", "cutting",
                     "chip", "chipped", "choose", "buy", "buying", "which", "best", "cost",
                     "price", "underfloor", "heat mat", "splashback")),
        entry("floor-scratch", (("floor", "wood", "laminate"), ("scratch", "scratched", "scuffs",
                                                                "marks")),
              "Rub a light scratch on a wooden floor with a walnut (really), or use a wax repair stick "
              "in a matching colour for deeper ones. On laminate, a scratch repair pen hides it, but "
              "only replacing the board fixes a deep gouge."),
        entry("hole-in-wall",
              (("hole", "holes", "dent", "dents", "crack", "cracks", "chunk", "gouge"),
               ("wall", "walls", "ceiling", "plaster", "plasterboard", "drywall", "skirting",
                "paper", "paint", "painted", "filler", "fill", "patch", "repair", "fix", "nail",
                "nails", "screw", "screws", "rawplug", "rawl plug")),
              "Push a bit of filler into the hole with a filling knife, leave it a little proud, and "
              "sand it flat once it is hard - two thin coats dry faster and sand better than one thick "
              "one. Anything bigger than a 50p piece, or a hole through plasterboard, wants a plasterboard "
              "patch stuck behind it and filled over before you paint. A crack wider than a couple of "
              "millimetres, or one that keeps coming back, is a builder's job rather than yours.",
              # a hole in a jumper is a darning job, and a crack in the wall is not a fabric repair
              avoid=("jeans", "jumper", "sock", "socks", "shirt", "cardigan", "knee", "tights", "garment",
                     "darn", "sew", "sewing", "stitch", "fabric", "trousers", "pocket", "coat",
                     # a cracked screen is a glass question, not a wall one
                     "phone", "screen", "mobile", "iphone", "laptop", "tablet", "tv", "telly",
                     "windscreen", "window", "glass", "car", "van",
                     "roof", "roofs", "tyre", "tyres", "tube", "inner tube", "bike", "bicycle"),
              bias=1),
        # --- the odd jobs -------------------------------------------------------
        # Small repairs and woodwork: the answers a person wants when something in the house
        # squeaks, wobbles, or will not come clean. Each one is keyed on the thing that is wrong and
        # passes on the neighbours it would otherwise steal (a floor scratch from a floor clean, a
        # wooden spoon from a wooden table).

        # `squeaky-door` in this file was the same job under a second id, and two test files wanted
        # different winners for the same line: one table now, with the sticking and rubbing cases in
        # the key, and the latch and matchstick advice in the reply.
        # The verbs come first and the fittings second, so "my gate creaks" counts two different key
        # words: with both in one part the two readings were the same word and the score was zero.
        # The fitting is the key's first half and the fault the second, so one table answers a door
        # that will not stay shut and a shelf that has snapped without either reaching the creak
        # answer or the meal table. The callable picks the part; the keys only say it is a fitting
        # with something wrong with it.
        entry("fitting-repair",
              (("oven", "cooker", "cupboard", "cupboards", "cabinet", "cabinets", "wardrobe", "unit",
                "units", "shelf", "shelves", "shelving", "drawer", "drawers", "window", "windows",
                "sash", "casement", "tap", "taps", "faucet", "mixer"),
               ("hanging off", "hangs off", "hanging", "hang", "came off", "come off", "came loose",
                "come loose", "loose", "loosely", "wobbly", "wobbles", "rocks", "snapped", "snap",
                "broken", "broke", "cracked", "fell off", "fallen off", "sagging", "sags", "dropped",
                "wont shut", "won't shut", "wont close", "won't close", "doesnt shut", "doesn't shut",
                "wont stay shut", "won't stay shut", "wont stay closed", "won't stay closed",
                "swings open", "pops open", "keeps opening", "crooked", "out of line", "wont slide",
                "won't slide", "doesnt slide", "jammed", "adjust", "fix")),
              _fitting_repair,
              # a door that creaks, sticks or needs oiling is the creak answer's, so its words come
              # out of this one; the meal table, the appliance answers and the body stay theirs too
              bias=2,
              avoid=("squeak", "squeaks", "squeaky", "squeaking", "creak", "creaks", "creaking",
                     "oil", "oiling", "rubbing", "rubs", "rattle", "rattles", "wind", "draught",
                     "draft", "sticking", "sticks",
                     "recipe", "recipes", "dinner", "lunch", "tea", "cook", "cooking", "meal", "meals",
                     "eat", "food", "fridge", "freezer", "microwave", "kettle", "dishwasher",
                     "washing machine", "tumble dryer", "dryer", "car", "van", "wheel", "wheels",
                     "pram", "pushchair", "trolley", "bike", "bicycle", "gate", "garage door",
                     "car door", "shower", "toilet", "bath", "boiler", "radiator", "my back",
                     "my knee", "my shoulder", "my neck", "my tooth", "my wrist", "my ankle",
                     "my hip",
                     # A window with glass out of it is not a fitting that came loose: "how do i
                     # fix a broken window", "is it expensive to fix a broken window" and "someone
                     # broke my window" all reached this card, which opens by saying the window is
                     # out of line rather than broken (early-badge, #4083). The break words stand
                     # this entry down in `avoid`, not only in the callable, because an entry a
                     # callable declines is still the entry the memory reads the line as being
                     # about.
                     "broken window", "window is broken", "window was broken", "broke my window",
                     "broke the window", "someone broke", "somebody broke", "smashed", "shattered",
                     "put through", "pane", "panes", "glass broke", "board up", "boarded up",
                     "expensive",
                     # "it rises then it drops in the oven" is a loaf collapsing, and `dropped` is in
                     # the key above: the bake's own rows in cooking.py answer every one of these, so
                     # anything said about the bake itself stands this card down.
                     "rise", "rises", "risen", "rising", "prove", "proves", "proved", "proving",
                     "proof", "proofed", "dough", "sourdough", "loaf", "loaves", "yeast", "sponge",
                     "batter", "souffle", "soufflé", "pastry", "croissant", "meringue", "bake",
                     "bakes", "baked", "baking") + FITTING_SHARED_STANDDOWN),
        # The noise a drawer makes is its runners rubbing, not a hinge, and there is no oil in
        # this job: grease and oil hold the dust that makes it worse. Before this entry a
        # squeaking or stiff drawer was the door answer, a rattling one was the chesty cough, and
        # "my chest of drawers is stuck" was "What have you tried so far?".
        entry("drawer-runners-rub",
              (("drawer", "drawers", "cutlery drawer", "kitchen drawer", "bedside drawer",
                "chest of drawers", "dresser drawer", "bedroom drawer"),
               ("squeak", "squeaks", "squeaky", "squeaking", "rattle", "rattles", "rattling",
                "stiff", "sticking", "sticky", "sticks", "jammed", "jamming", "jams", "grind",
                "grinds", "grinding", "dragging", "drags", "rough", "wobble", "wobbles",
                "wobbly", "loose", "hard to open", "hard to pull", "hard to push", "wont open",
                "won't open", "stuck")),
              "Rub a candle, a dry bar of soap or a little beeswax along the wooden runners or the "
              "plastic slides, and never oil or grease - those hold the dust that makes it worse. "
              "If it rattles or grinds, tighten the runner screws at the back, one turn past "
              "finger-tight. A drawer that sticks only at the end is usually the side swelling in "
              "damp weather, so sand the top edge of the drawer side lightly and it stops catching.",
              # the runners that have come away are the replace-them answer's, and a drawer with
              # something broken in it, a drawer of a fridge or a washing machine, and a chest as a
              # body part are all other jobs
              # the drawer noun is what keeps the chesty cough and the door out, so the avoid
              # list holds only the fittings and the machines: "my chest of drawers is stuck" is
              # a drawer, and a "chest" in the avoid list stood the whole entry down
              avoid=("off the runner", "off the runners", "off its runner", "come off",
                     "came off", "replace", "replacement", "new runner", "fridge", "freezer",
                     "washing machine", "dishwasher", "microwave", "oven", "lock", "locked",
                     "key", "child lock", "hinge", "hinges"),
              bias=1),
        # The window of a chat is not a window of a house: "what do you do when i shut the chat
        # window" and "when i close the browser tab" are questions about what becomes of the
        # conversation, and once the creaking-door key held "window"+"shut" they were told to oil
        # the hinges. Only the words that make the window the chat's own are here, so "why does
        # this window creak" is still the hinge answer.
        entry("door-creak",
              (("squeak", "squeaks", "squeaky", "squeaking", "creak", "creaks", "creaking",
                "sticking", "sticks", "stiff", "rubbing", "rubs", "drags", "dragging", "jammed",
                "jamming", "shut", "shuts", "closing", "hard to shut", "hard to close",
                # "how do i oil a door hinge" was the one shape of this job the key lost when the
                # two squeaky-door tables were merged: oiling is what the reply says to do, so it
                # belongs in the verbs, not only in the words of a line that is already working.
                "oil", "oils", "oiling", "oiled", "lubricate", "grease"),
               # a drawer was in this list, so "how do i stop a drawer from squeaking" was told
               # to oil the hinges and open and close the door. A drawer has runners, not hinges,
               # and the wax answer below is its own.
               ("door", "doors", "hinge", "hinges", "latch", "window", "windows",
                "cupboard door", "gate", "front door")),
              "Oil the hinges: a drop of 3-in-1 or a spray of silicone on each hinge pin, then open and "
              "close the door a few times so it works in. If it sticks or rubs rather than squeaks it "
              "has usually dropped on its top hinge, so tighten the hinge screws - loose ones let the "
              "door drop - and if they spin, push matchsticks dipped in wood glue into the holes and "
              "screw back in. Rub a candle or a dry bar of soap on the latch plate or the top edge if "
              "that is the part catching.",
              # a creaking floorboard, a creaking bed and a squeaking shoe are other answers
              # "stop" is in the key, so "how do i stop a door banging in the wind" scored here and
              # got hinge oil for a door that bangs. Banging is the latch answer's, not this one's.
              avoid=("chat window", "chat box", "chat pane", "browser", "browser window",
                     "browser tab", "this chat", "the chat", "the app window",
                     "floorboard", "floorboards", "floor", "bed", "beds", "shoe", "shoes", "brake",
                     "brakes", "kettle", "bang", "bangs", "banging", "slam", "slams", "slamming",
                     "rattle", "rattles", "rattling", "wind", "windy", "draught", "trainer",
                     "trainers", "boot", "boots", "sandal", "flip flop", "chair", "chairs", "stairs",
                     "bike", "bicycle", "car", "van", "wheel", "wheels", "trolley", "pram",
                     "pushchair", "voice", "squeaky clean", "toy", "toys", "clean", "cleaning",
                     # "grease" is in the key because greasing a hinge is this job, and it also took
                     # "how do i get grease off a kitchen door" - a cleaning question that was handed
                     # oil for the hinges. A removal phrase and a greasy surface are the cleaning
                     # ones; "how do i grease a door hinge" has neither.
                     "grimy", "sticky", "grease off", "grease from", "grease out",
                     "paint", "painted", "washing machine", "dryer", "fridge", "freezer", "oven",
                     "dishwasher",
                     # a door that will not open, or that has been forced, is a lock job or worse
                     "locked", "lock", "cannot open", "cant open", "can't open", "slammed",
                     "broke in", "burglar", "forced", "off its hinges", "fell off", "get out",
                     "trapped", "inside", "fire", "smoke", "cant get out", "can't get out",
                     # a door or gate that has dropped or come away is a loose hinge, which is
                     # `hinge-sag`'s job: oiling a joint that has pulled out of the wood only hides
                     # it, and "my gate is sagging and it wont shut" was getting this answer
                     "sagging", "sagged", "sags", "sag", "hanging off", "hanging by",
                     "come off its hinge", "came off its hinge", "off its hinge", "loose hinge",
                     "loose hinges", "wont shut", "won't shut",
                     # What comes *through* a door is not the door: junk mail, leaflets and a
                     # takeaway menu are a post question, and oiling the hinges answers none of it.
                     "mail", "junk", "junk mail", "leaflet", "leaflets", "flyer", "flyers",
                     "letter", "letters", "letterbox", "post", "postman", "delivery", "menu",
                     "cold callers", "salesman", "salesmen",
                     # A door that will not stay shut, a cupboard door hanging off and a window that
                     # will not close are a catch, a hinge screw and a sash out of line: oiling the
                     # hinges answers none of them, and `fitting-repair` has each of them.
                     "wont stay shut", "won't stay shut", "wont stay closed", "won't stay closed",
                     "swings open", "hanging off", "hangs off", "cupboard shelf", "shelf has snapped"),
              # a tie with the blister answer on "stop my door rubbing"; the fittings word settles it
              bias=1),
        entry("floorboard-creak",
              (("floorboard", "floorboards", "floor", "stairs", "stair", "step", "landing"),
               ("creak", "creaks", "creaking", "creaky", "squeak", "squeaks", "squeaking",
                "squeaky", "noisy")),
              "Find the noisy board and work talcum powder, french chalk or graphite powder into the "
              "gaps between the boards - it stops the wood rubbing on the nail. If it still creaks, "
              "screw the board down again from above instead of nailing it, and on stairs check the "
              "treads are tight.",
              avoid=("clean", "cleaning", "mop", "scratch", "scratches", "polish", "paint"),
              bias=1),
        entry("carpet-clean",
              (("carpet", "carpets", "rug", "rugs"),
               # main answers "how do i clean a carpet" from its furnishing entry, so this one is for
               # the smell and the stairs lines it leaves, not for the plain clean again
               ("smell", "smells", "smelly", "odour", "odors", "stink", "deep clean",
                "shampoo", "dirty", "stairs", "stair",
                # "what is the best way to clean a carpet" reached the stain card and was told to
                # blot a mark that does not exist. `best way` is the ask, and it is not in any other
                # carpet row's key, so the plain cleaning question comes here without taking "how do
                # i clean a carpet" or "how often should i clean my carpets" off the furnishing row.
                "best way", "steam")),
              "Vacuum it twice, slowly, then work at any mark from the outside in with a little carpet "
              "shampoo on a cloth and blot it dry - a carpet that stays damp is what starts a smell. "
              "For a whole room or a set of stairs, a hired shampoo machine is worth it once a year, and "
              "open the windows while it dries.",
              # a stain and a wooden floor are their own answers
              avoid=("red wine", "wine", "coffee", "vomit", "pet", "dog", "cat", "car", "car mat",
                     "floor", "floorboards",
                     # "my carpet smells musty" is the damp answer main already has
                     "musty", "damp"),
              bias=1),
        entry("wood-polish",
              (("table", "furniture", "sideboard", "cabinet", "chair", "desk", "dresser"),
               ("polish", "wax", "shine", "dull", "dullness", "restore", "oak", "wood", "wooden")),
              "Dust it, then work a hard wax polish or a beeswax-and-oil mix into the grain with a "
              "soft cloth, along the grain, and buff it off after ten minutes. Little and often beats "
              "a thick coat, which goes sticky and picks up dust.",
              # "get the wax OFF a table" is a removal question (cleaning's wax-table), not how to
              # polish it: this entry answered it with "work a hard wax polish into the grain"
              avoid=("floor", "floorboards", "scratch", "wobble", "wobbly", "dent", "dents",
                     "gouge", "gouges", "chip", "chipped", "stain", "stained",
                     "off", "remove", "removing", "spilled", "spilt", "spillage", "marks",
                     # painting a table is home.py's paint-furniture row, not a waxing job
                     "paint", "painting", "painted", "repaint"),
              bias=1),
        # A ring left by a wet glass, or the white bloom a hot plate leaves, is not polishing and not a
        # scratch: `wood-polish` avoids the word stain, so the commonest furniture repairs had no answer
        # of their own and the plain form of the question got "I'm not sure about that one".
        entry("wood-stain",
              (("table", "tables", "tabletop", "furniture", "sideboard", "cabinet", "desk", "dresser",
                "worktop", "wood", "wooden", "oak", "pine", "mahogany", "teak", "veneer"),
               ("stain", "stains", "stained", "water mark", "water marks", "watermark",
                "water ring", "water rings", "white ring", "white rings", "cup ring", "cup mark",
                "heat mark", "heat marks", "heat ring", "ring", "rings", "mark", "marks",
                "bloom", "milky")),
              # Every sentence names its own mark, because the composer can show one of them alone
              # when the earlier ones have been said in the same conversation.
              "A white water ring or a heat bloom lifts with mayonnaise or petroleum jelly left on "
              "overnight, or with a hairdryer held 15 cm away for a few minutes. A cloth laid over a "
              "white ring with a warm iron pressed on it for a few seconds at a time does the same job "
              "when the first try does not. A dark stain has gone into the wood and wants sanding back "
              "and re-oiling, and ink lifts with a little methylated spirit on a cloth, along the "
              "grain, before you polish the whole top so the shine matches.",
              # a scratch, a dent, a wobble and a polish are the neighbouring answers, and so are a
              # wooden floor, a car panel and a stained shirt
              avoid=("floor", "floors", "floorboard", "floorboards", "laminate", "scratch",
                     "scratches", "scratched", "scuff", "scuffs", "scuffed",
                     "dent", "dents", "gouge", "chip", "chipped", "wobble",
                     "wobbly", "loose", "car", "van", "phone", "screen", "shirt", "clothes", "clothing",
                     "carpet", "rug", "sofa", "upholstery", "wall", "paint", "gravy", "wine", "coffee",
                     "tea", "oil", "varnish", "remove the wax", "wax off",
                     # "how do i get wood stain off my hands" is paint-on-hands' line: the table
                     # card was answering it with a ring left by a glass
                     "hands", "hand", "fingers", "skin", "nails", "arms",
                     # the wood answers do not apply to a glass top: "white marks on the glass table"
                     # was told to rub mayonnaise into it, which is a trick for wood, not glass
                     "glass", "glasses", "glass table", "glass top", "glass tabletop", "marble",
                     "stone", "granite", "quartz", "slate"),
              bias=1),
        entry("wood-chip-fill",
              (("chip", "chips", "chipped", "gouge", "gouged", "chunk", "splinter", "splintered"),
               ("wood", "wooden", "woodwork", "table", "tables", "dresser", "sideboard", "desk", "oak",
                "pine", "walnut", "mahogany", "teak", "veneer", "furniture", "door", "worktop")),
              "A chipped edge or a gouge in wood is a filler job: press a two-part wood filler or a wax "
              "repair stick into it, a little proud of the surface, and sand or shave it flat once it is "
              "hard, then colour it with a touch of wax or stain. Keep the sanding to the filler - "
              "sanding the finish around it leaves a pale patch you cannot hide.",
              # the chips you eat, the chip in a tooth, and the chip in a screen are other questions
              avoid=("potato", "potatoes", "fries", "fry", "oven", "pan", "oil", "air fryer", "airfryer",
                     "fish", "supper", "takeaway", "tooth", "teeth", "filling", "dentist", "dental",
                     "phone", "screen", "glasses", "windscreen", "window", "paint", "nail", "nails",
                     "varnish", "paintwork", "car", "cars", "mug", "cup", "plate", "bowl",
                     # the wood chips you buy are burned, not filled: "what wood chips for a bbq" and
                     # "wooden chips for smoking" were a punting shrug and an acknowledgement on main
                     # before this card took them, so the fire words stand it aside
                     "bbq", "barbecue", "barbeque", "smoker", "smoking", "smoked", "smoke",
                     "wood chips", "woodchips", "chips for", "pellet", "pellets", "fire pit",
                     "chiminea", "pizza oven", "grill", "grilling", "burn", "burning"),
              # a repair in the wood is this card's even when a consumer row shares two of the words
              bias=2),
        entry("wood-dent",
              (("dent", "dents", "dinked", "gouge", "gouged"),
               ("wood", "wooden", "woodwork", "table", "dresser", "sideboard", "desk", "oak", "pine",
                "floorboard", "floor")),
              "A shallow dent in bare wood comes back up with water and heat: wet the spot, lay a damp "
              "cloth over it and press a hot iron on for a few seconds at a time, checking as you go. "
              "Once the wood has a finish on it a dent cannot be raised, so the repair is filler, sand "
              "and a matching wax or varnish.",
              # a dented car panel is bodywork, and a dented screen is glass
              avoid=("car", "cars", "van", "bumper", "wing", "bonnet", "door", "panel", "phone",
                     "screen", "fridge", "freezer", "washing machine", "drum")),
        entry("chair-wobble",
              # a desk is a table with drawers and it had no word here, so "my desk wobbles"
              # was an acknowledgement while the same line about a table got the repair
              (("chair", "chairs", "table", "tables", "desk", "desks", "stool", "bench",
                "furniture", "leg"),
               ("wobble", "wobbly", "wobbles", "loose", "rock", "rocks", "rocking", "rickety", "fix")),
              "Turn it over and find the loose joint: usually one leg has worked free of the seat. "
              "Squeeze wood glue into the joint, push it home and clamp it - a strap or a rope round "
              "all four legs works - and leave it overnight. Tighten any screws and add a bracket if "
              "the same joint keeps going.",
              ask=("wobble", "wobbly", "wobbles", "wobbling", "loose", "rock", "rocks",
                   "rocking", "rickety"),
              avoid=("chair for", "garden chair", "high chair", "wheelchair", "office chair"),
              # "loose stools for 3 days" is the same two words as a wobbly chair, and the reading
              # already knows which it is: when it reads the stomach, the chair stands aside. When
              # it reads nothing at all - "my stools are loose" - the words settle it instead, and
              # `_a_chair_and_not_a_body` holds the chair back for that one shape.
              guard=_a_chair_and_not_a_body),
        # A thing that will not sit still is its own job, and the fan had nobody to ask:
        # "my tower fan is wobbly" was an acknowledgement, "the fan wobbles when it runs" was
        # the laptop's cooling answer and "can you stop a fan from wobbling" was told that most
        # shaking is caffeine. A washer and a dryer that shake have their own cards (the transport
        # bolts and the load), so this one is the fan and the appliance with no card of its own.
        entry("a-fan-that-rocks",
              (("fan", "fans", "ceiling fan", "desk fan", "pedestal fan", "floor fan", "tower fan",
                "standing fan", "extractor fan", "heater", "fan heater", "fridge", "freezer",
                "appliance", "appliances"),
               ("wobble", "wobbles", "wobbling", "wobbly", "shakes", "shaking", "shaky", "rocks",
                "rocking", "walks", "walking", "jumps", "jumping", "vibrates", "vibrating",
                "moves about", "not level", "off balance", "uneven", "unsteady", "wonky",
                "tilts", "leaning")),
              _the_fan_stopped,
              ask=("wobble", "wobbles", "wobbling", "wobbly", "shakes", "shaking", "rocks",
                   "rocking", "walking", "jumps", "vibrates", "unsteady", "wonky", "tilts",
                   "stop it", "stop the", "why does", "fix"),
              # a person who is shaking is the shake answer's, a chair is the chair repair's, and
              # the machine with its own card (a washer, a dryer, a fridge that is not cold, a fan
              # that is noisy or grinding) keeps it
              avoid=("hands", "hand", "fingers", "arms", "voice", "feel shaky", "shaky hands",
                     # "desk" is not fenced: a desk fan is one, and the chair row wins a desk
                     # that wobbles on its own words anyway
                     "chair", "chairs", "table", "tables", "stool", "stools", "bench",
                     "sofa", "wardrobe", "door", "gate", "shelf", "shelves", "washing machine",
                     "washer", "dryer", "laptop", "computer", "pc", "phone", "car", "bike",
                     "steering", "baby", "dog", "cat", "puppy", "noise", "noisy", "rattle",
                     "rattles", "rattling", "grind", "grinding", "hum", "humming", "buzz",
                     # a fan that wobbles AND clicks is a noise question, and the noise card
                     # names the guard and the blade nut: "the fan wobbles and clicks" was
                     # answered by it before this row existed
                     "click", "clicks", "clicking", "squeak", "squeaks", "squeaking", "whine",
                     "whirr", "knock", "knocks", "knocking", "bang", "bangs", "banging",
                     "thump", "thumping", "scrape", "scraping",
                     "leak", "leaking", "smell", "smells", "not cold", "no power",
                     "how much", "cost", "electricity", "petrol"),
              bias=1),
        # A chair or a table does not only come loose; it snaps. "the table leg is broken" used to
        # reach the broken-bone answer on the word "leg", and a chair that was simply broken got an
        # echo, so a break in furniture gets the repair it needs and leaves the body table alone.
        entry("chair-broken",
              (("chair", "chairs", "table", "tables", "desk", "desks", "stool", "stools", "bench",
                "benches", "furniture", "bed", "beds", "sofa", "sofas", "couch", "couches",
                "settee", "settees", "shelf", "shelves", "cupboard", "cupboards", "drawer",
                "drawers", "wardrobe", "wardrobes"),
               ("broken", "broke", "snapped", "cracked", "split", "hurts", "hurting", "sore",
                "aching", "aches",
                # the consumer refund key carries the whole phrase "is broken", and a phrase counts
                # for more than the bare word: "my chair is broken" went to the refund ladder on it.
                # The same phrasing here is what makes the two rows weigh the same, and then the
                # bias below says a chair on its own is mended.
                "is broken", "is cracked", "is snapped", "is split", "has broken", "has snapped",
                "has cracked", "has split")),
              "Turn it over or open it up and see what has gone: a leg that has snapped wants the old "
              "glue drilled out, a wooden dowel or a longer screw and wood glue in the joint, clamped "
              "overnight. A cracked seat, back or shelf wants a bracket underneath and a screw through "
              "the split, and a split frame is usually cheaper to replace than to mend. Take the "
              "weight off it until the glue has set.",
              ask=("broken", "broke", "snapped", "cracked", "split", "hurts", "hurting", "sore",
                   "aching", "aches"),
              # a thing's own part is the thing's, and a person's part is not this entry. The
              # person's words are here because "my new chair hurts my back" is a question about
              # their back, not a broken chair.
              avoid=("chair for", "garden chair", "high chair", "wheelchair", "office chair",
                     "my leg", "my back", "my arm", "my wrist", "my ankle", "my knee", "my neck",
                     "my shoulder", "my hip", "hurts my",
                     "refund", "return", "returns", "money back", "shop", "store", "retailer",
                     "receipt", "guarantee", "warranty", "bought", "i paid", "reject",
                     "months old", "weeks old", "under a year", "still under",
                     # a chair that broke in its first week or month is a claim on whoever sold it
                     "after a week", "after a month", "after two weeks", "after 2 weeks",
                     "after a few days", "after 3 weeks", "last week", "last month",
                     # a furniture part that hurts or feels sore is loose at its joint, and
                     # `thing-part-hurts` says that: the bias above is strong enough to take the
                     # line otherwise, and "the chair back hurts" wants the tighten-it card
                     "hurt", "hurts", "hurting", "sore", "aching", "aches",
                     # "we booked a table for friday but the dishwasher broke" booked a restaurant
                     # table, not a piece of furniture, and the thing that broke is the machine
                     "booked a table", "book a table", "booking a table", "reserved a table",
                     "reserve a table", "table for two", "table for four", "table for 4",
                     "table for six", "table for 6", "restaurant", "reservation",
                     "dinner reservation"),
              # "soft stools and stomach ache" reaches this row on `stools` and `ache`
              guard=lambda understood: not the_stomach_is_what_it_is_about(understood),
              bias=4),
        # A part of a thing that hurts or feels stiff is not a part that has snapped. The body
        # tables stand down for a thing's own part, but `chair-broken` only names furniture, so
        # without this row a book's spine, a bottle's neck or a ladder's leg fell through to a
        # feeling or a question. The state the person said is the first thing to answer.
        entry("thing-part-hurts",
              (tuple(sorted(THING_PARTS)),
               ("hurt", "hurts", "hurting", "ache", "aches", "aching", "achy", "sore", "stiff",
                "pain", "pains", "painful", "twinge", "twinges", "throbbing")),
              "A part that hurts rather than has snapped is usually loose at its joint: tighten the "
              "screws or bolts, check the bracket and the glue line, and keep the weight off it until "
              "it feels firm. If it moves when you lean on it, treat it as a break - drill out the old "
              "glue, fit a wooden dowel or longer screw, and clamp it overnight.",
              # the state said is the reason for the answer, so it comes before the general
              # furniture repair when the line says "hurts" or "is sore"
              bias=3,
              # a stomach ache beside the word "stools" is the person's, not a thing's
              guard=lambda understood: (_a_thing_owns_the_part(understood)
                                        and not the_stomach_is_what_it_is_about(understood)),
              # a pipe, a wire or an appliance has its own answer, and the trade or the engineer is
              # the useful next step rather than a screwdriver
              avoid=("pipe", "pipes", "wire", "wires", "wiring", "boiler", "radiator", "radiators",
                     "drain", "drains", "tap", "taps", "socket", "sockets", "toilet", "sink",
                     "washing machine", "fridge", "freezer", "oven", "hob", "shower", "door",
                     "window", "lock", "locks")),
    ]
