"""The rows of the home-and-DIY domain: the list from `home.py`, in a file of its own.

`home.py` went over the publisher's 1 MiB file limit (1,067,285 bytes) and the world then refused
every PR in the swarm, not only the ones that touched that file, because it looks at the clone:
`{"error": "file too large: bot/knowledge/home.py is over 1048576 bytes"}`. The list of entries
is the biggest thing in the file and it is data rather than code, so it moved here.

Nothing about the entries changed. `home.py` calls `entries()` at the end, after every helper,
table and guard this list names is defined, and puts the rows back in front of the ones it
appends itself, so `home.ENTRIES` is the same rows in the same order as before. The import is
inside the function for that reason: this module is imported by `home.py`, not the other way
round, and it has no ENTRIES of its own, so the registry does not read it as a second domain.

The rows themselves live in `bot/knowledge_parts/home_craft_rows_01` to `_10` (outside
bot/knowledge, whose domains() takes every file for a knowledge domain), about a thousand lines
each, cut at row boundaries and moved unchanged. `entries()` imports them when it is called and
joins their `rows()` in order. They take the helpers they need from this module at the top, which
is safe because they are only imported once this module is fully loaded. tests/test_home_craft_rows.py
compares every row, in order, with the list as it was before the cut.
"""

import re


_A_DEPOSIT_COMING_BACK = re.compile(
    r"\b(?:tenancy|scheme|landlord|letting agent|deposit protection|moved out|end of tenancy|"
    r"deposit back|deposit returned|deposit return|deposit paid|paid a deposit)\b")


def _a_deposit_coming_back(understood):
    """True when the deposit line is a tenancy one, not somebody saving towards a deposit."""
    read = understood if isinstance(understood, dict) else {}
    said = " ".join(str(read.get("clean") or read.get("text") or "").lower().split())
    return bool(_A_DEPOSIT_COMING_BACK.search(said))


import re

from ..understanding.topics import the_bin_is_on_a_machine
from .costs import A_AGE_OWNED

# A food named with its own smell is the food's question, and the fridge is only where it is:
# "the milk in my fridge smells off but the date is fine" was told to wash out the door seal and
# the drain hole, and "the milk in the fridge smells sour" the same. The bottle has a card of its
# own that says bin it. "The fridge smells of milk" keeps this row, because there the food comes
# after the smell and the fridge is what smells.
_FOOD_OWN_SMELL = re.compile(
    r"\b(?:milk|yoghurt|yogurt|cream|soured cream|sour cream)\b[^.?!]{0,30}?"
    r"\b(?:smells|smell|smelt|smelled|stinks|stink|gone off|went off|is off|has turned|turned|"
    r"curdled|sour)\b")


def _not_the_food_in_the_fridge(understood):
    """False when the line is a food that has turned, with the fridge named as where it is."""
    text = " ".join(str(one) for one in ((understood or {}).get("words") or ())).lower()
    if not text:
        text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    return not _FOOD_OWN_SMELL.search(text)

# "Can i service my own boiler" and "how often should the boiler be serviced" are two questions,
# and one cost-and-frequency reply answered both: the first wants to know whether the job is
# theirs, and a price never says. They are two rows rather than one row with a reply that changes
# its mind, because an entry whose reply is a function stops carrying the conversation a turn
# later: after "my boiler needs its yearly service" the age in "its 8 years old" reached the
# engineer's-price answer instead of the lifespan one.
# A fixture that has stopped is not an appliance, and the plug-and-door-switch first aid is the
# wrong first thing to try on a shower, a tap or a toilet - no appliance row names any of them.
# Until they had a row of their own these lines were answered by whatever else their words touched:
# "the hot tap stopped working" reached the bank's contactless card ("In the bank's own app there
# is usually an 'Add to Apple Pay'"), "my toilet has stopped working" the fibre answer, "my shower
# isnt working" the extractor fan (that row holds the word shower) and "the plug socket has stopped
# working" the skirting-tape row, while "the shower has stopped working", "the shower broke" and
# "the doorbell has stopped working" got only a listening line back. The fixture named in the line
# says which first check to give, so one row answers them all and no fixture needs a row of its own.
# The fault words are the ones that say the thing is not running at all: a named symptom (leaking,
# blocked, wont drain, wont flush, cold) is the row that knows that symptom, and it keeps the line.
STOPPED_ALTOGETHER = (
    "stopped working", "stops working", "stopped work", "not working", "isnt working",
    "isn't working", "doesnt work", "doesn't work", "wont work", "won't work", "no longer works",
    "broken", "broke", "broken down", "broke down", "packed in", "packed up", "gave up",
    "dead", "no power", "wont come on", "won't come on", "wont turn on", "won't turn on",
    "wont switch on", "won't switch on", "faulty", "gone wrong", "went wrong")

# Longest first, so "power shower" is the shower and not a power cut, and a fixture is found by the
# words the person typed rather than by a list of subjects: "the hot tap stopped working" has the
# subject "tap", and "my shower isnt working" the subject "shower", but a line can reach the reading
# with no subject at all and the fixture is still the thing it names. A dead socket is not here: it
# has its own row, and the paint rows that used to take it were the bug (see `decorating`).
FIXTURE_FIRST_CHECKS = (
    (("power shower", "electric shower", "shower", "showers"),
     "Start at the switch that feeds it: the pull cord or the wall switch, then the fuse in the "
     "unit, because a dead shower is usually that. If the unit lights up but no water runs, it is "
     "the solenoid valve or scale in the head, and on a mixer run the other hot taps first."),
    (("mixer tap", "monobloc", "tap", "taps", "faucet", "faucets"),
     "Look for a small screw slot on the pipe under the sink or the bath, because a tap that will "
     "not run at all is usually an isolator someone turned off or a valve that has seized. If the "
     "water comes but only trickles, unscrew the spout end and soak the aerator in vinegar."),
    (("toilet", "toilets", "loo", "cistern"),
     "Turn the isolation screw off, lift the lid and watch the cistern fill: a float arm stuck or "
     "an inlet valve furred up with scale is the usual reason the loo has stopped. A button with "
     "no resistance is the flush valve or its link, which is a cheap part."),
    # "door bell" and "door chime" are not here: a remembered key with "door" in it is handed to
    # the door group of the trade table, so the follow-up after a dead doorbell sent the person to
    # a joiner. "doorbell" alone is one word, and "chime", "chimes" and "bell push" carry the
    # lines that say it the other way round.
    (("doorbell", "doorbells", "chime", "chimes", "bell push", "bell"),
     "Start with the power to it: a wired bell has a transformer near the consumer unit, and a "
     "wireless one has a battery in the push and another in the chime. A push that is stuck, wet "
     "or corroded is the next thing."),
    (("garage door", "up and over door", "roller door", "sectional door"),
     "Use the manual release first - usually a red cord or a handle on the mechanism - so the car "
     "is not stuck in, then check the power, the remote's battery and the safety sensors at the "
     "bottom of the tracks. A door that opens a foot and stops is the travel limits or a broken "
     "spring, and a spring is not a DIY job."),
    (("heated towel rail", "towel rail", "towel radiator", "ladder rail",
      "radiator", "radiators", "rad", "rads"),
     "Bleed it, then take the head off the thermostatic valve and press the pin: one cold radiator "
     "is air or a pin stuck down. If every radiator is cold it is the boiler, the programmer or a "
     "zone valve, and one that is cold at the bottom wants a flush."),
)


def _the_fixture_that_stopped(understood):
    """The first check for the fixture a line says has stopped, or None.

    The fault words say the thing is not running at all, and the fixture is read from the line's
    own words with the longest phrase first, so "power shower" is not a power cut and "plug
    socket" is not a plug-in appliance.
    """
    reading = understood if isinstance(understood, dict) else {}
    said = " ".join(str(one) for one in (reading.get("words") or ())).lower()
    if not said:
        said = str(reading.get("clean") or reading.get("text") or "").lower()
    if not said or not any(word in said for word in STOPPED_ALTOGETHER):
        return None
    for names, check in FIXTURE_FIRST_CHECKS:
        if any(re.search(r"\b" + re.escape(name) + r"s?\b", said) for name in names):
            return check
    return None


# Every row below answers a fixture that has stopped, so every one of them has to stay out of a
# named symptom, a fixture being bought or rented, a decorating job and a shower enclosure
# whose door or tray has gone. Shared so the rows cannot drift apart.
A_FIXTURE_IS_NOT_A_DECORATING_JOB = ("leak", "leaks", "leaking", "drip", "dripping", "blocked", "blockage",
                     "wont drain", "won't drain", "not draining", "wont flush", "won't flush",
                     "smell", "smells", "smelly", "noise", "noisy", "banging", "rattling",
                     "cold", "hot water", "pressure", "limescale", "scale", "mould", "mold",
                     "buy", "buying", "worth", "cost", "price", "cheaper", "rent", "landlord",
                     "install", "installing", "fit a new", "replace", "replacing", "replacement",
                     "paint", "painting", "tile", "tiling", "decorate", "decorating",
                     "how do i", "how to", "should i",
                     # The door, the tray and the seal are parts of the enclosure, and a broken one
                     # is a glazing or a seal question: "the shower door is broken" is not the supply
                     # and the first check for the supply is the wrong thing to tell them.
                     "shower door", "shower doors", "shower screen", "shower tray", "door seal",
                     # Which radiators are cold is the system's question, and the row that reads
                     # "cold upstairs and warm downstairs" answers it better than one radiator's
                     # first check: "the downstairs radiator is not working" keeps that answer.
                     "upstairs", "downstairs", "top floor", "first floor")

def _a_fixture_that_stopped_was_the_question(understood):
    """The first check for the fixture the line names, or None for a line that names none."""
    return _the_fixture_that_stopped(understood) is not None


def _the_stopped_fixture_entries(entry):
    """One row per fixture, not one row for the family.

    A family key is remembered as one list of words, and the next turn hands that list to the
    trade table: a shower, a tap, a doorbell and a cistern all remembered "radiator", so "my
    shower isnt working" was sent to a Gas Safe engineer. A row whose keys are its own fixture
    is remembered as that fixture, and the trade that turns up is the right one.
    """
    for _names, _check in FIXTURE_FIRST_CHECKS:
        yield entry("a-fixture-that-stopped-" + _names[0].replace(" ", "-"),
                    (_names, STOPPED_ALTOGETHER),
                    lambda memory, reading: _the_fixture_that_stopped(reading),
                    avoid=A_FIXTURE_IS_NOT_A_DECORATING_JOB,
                    # the row that names the fixture the line is about outranks a biased
                    # neighbour, and the guard keeps it to a fixture that has stopped.
                    guard=_a_fixture_that_stopped_was_the_question, bias=3)

BOILER_DIY = ("myself", "own", "diy", "legal", "allowed")

# The permission words are in every other boiler line there is: "my own boiler keeps switching
# itself off" and "is it legal to have my boiler in the loft" are a fault and a siting question,
# and one word of possession was enough for the DIY row to take both - it told them about Gas Safe
# work instead of the reset button, and it took "my own boiler is 15 years old" off the lifespan
# card. The service word is what makes the line the permission question.
SERVICE_WORDS = ("service", "services", "servicing", "serviced", "annual", "yearly", "certificate")


def _an_ask_about_servicing_my_own(understood):
    """True when the line asks whether the yearly service is theirs to do.

    The row is keyed on the permission words because "can i service my own boiler" has no other
    mark in it, so the test that tells the permission question from the fault is the service word
    itself: "can i service it myself" and "is it legal to service the boiler" carry one, and "my
    own boiler is 15 years old" does not.
    """
    words = {str(one).lower() for one in ((understood or {}).get("words") or ())}
    text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    return bool(words & set(SERVICE_WORDS)) or any(one in text for one in SERVICE_WORDS)


# The verb of travelling is a shape, not a list of phrases. Every phrase the fly row's `avoid`
# names ("fly out", "flying home", ...) was added by hand after a travel line got the cider
# vinegar, and the next wording always got through, so the shape is fenced here instead: a
# destination, a place it is done from or to, or a day. "there are flies in my house" and "a fly
# keeps landing on me" are the noun and keep the card.
_A_FLY_THAT_TRAVELS = re.compile(
    r"\b(?:fly|flys|flies|flew|flown|flying)\s+"
    r"(?:"
    # straight at a destination: "fly to spain", "fly into dublin", "fly over the alps"
    r"(?:to|into|over|via)\s+"
    r"|"
    # or it is done from, back to or with somebody: "fly out of heathrow", "fly home",
    # "fly with a baby", "fly at 6am"
    r"(?:out|back|home|abroad|from|off|at|with)\b"
    r"|"
    # or on a day, which no insect is ever on: "fly out on the 3rd of august", "fly next tuesday",
    # "fly somewhere sunny next saturday"
    r"(?:[a-z']+\s+){0,3}(?:on|next|this)\s+"
    r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend|week|month|"
    r"morning|afternoon|evening|night|\d)"
    r")")


def _the_fly_is_not_a_verb(understood):
    """False when the line's "fly" is the verb of travelling, which is not a fly in the house."""
    text = " ".join(str(one) for one in ((understood or {}).get("words") or ())).lower()
    if not text:
        text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    return _A_FLY_THAT_TRAVELS.search(text) is None


# A bar is a unit only when the line makes it one, the same rule the money rows use for a figure:
# "drop bars", "my bars are too low" and "should i get drop bars" are the bar you hold on a
# bicycle, and the boiler gauge was answering all three with "top the pressure up to between 1 and
# 1.5 bar". A figure beside it ("half a bar", "1.5 bar", "two bars") or a word that says what is
# being measured ("pressure", "psi", "gauge") is what makes it a reading.
_A_BAR_WITH_A_FIGURE = re.compile(
    r"\b(?:\d+(?:\.\d+)?|half|quarter|one|two|three)\s+(?:a\s+)?bars?\b")
_PRESSURE_WORDS = frozenset(("pressure", "psi", "gauge", "boiler", "boilers", "combi",
                             "radiator", "radiators", "heating", "central"))


def _a_gauge_reading(understood):
    """False for a bare "bar" that is not a measuring unit."""
    reading = understood or {}
    text = str(reading.get("clean") or reading.get("text") or "").lower()
    words = set(str(one).lower() for one in (reading.get("words") or ()))
    if words & _PRESSURE_WORDS:
        return True
    return _A_BAR_WITH_A_FIGURE.search(text) is not None


# A block-paved drive is not the patio's bed: blocks go down on sharp sand alone, no
# cement, with kiln-dried sand brushed into the joints afterwards - so the row answers
# "how much mortar for 20 square metres of block paving" with sand and a wacker plate
# rather than a 5:1 mix the job does not use. A reviewer caught this on the first head.
# A machine that will not empty is a fault, and "water" or "empty" on its own is not: the
# drain row keys both words, so a bias that lifted it over its neighbours took "how much water
# does a washing machine use", "my washing machine isnt heating the water" and "my washing
# machine smells when it drains" as well as the blocked filter it was written for. Naming the
# words that are *not* the fault is a list with no end - the litres, the heat, the smell, the
# cost, the car's screen wash - so the row asks instead for the fault itself, which is a short
# closed set: a block, a clog, a jam, water that will not go, a drain that is slow.
_WILL_NOT_EMPTY = re.compile(
    r"\b(block|blocks|blocked|blockage|blocking|clog|clogs|clogged|clogging|jam|jams|jammed|"
    r"stuff|stuffed|bunged|plugged)\b"
    r"|\b(backed|backing)\s+up\b"
    r"|\b(water\s+(is\s+)?(sitting|standing|left|stuck|pooling|pooled|trapped)|standing water|"
    r"full of water|water in the drum|water in the bottom|water inside the drum|pool of water|"
    r"water\s+(wont|won't|not)\s+(go|going|leave|leaving|drain|draining))\b"
    # the fault said as a negative about the emptying itself: "it doesnt drain", "i cant get the
    # washing machine to drain", "unable to get the water out", "stopped draining", "drains slowly"
    r"|\b(no|not|n't|cant|can\s+t|cannot|can\s*['\u2019]?\s*t|couldnt|couldn't|could not|"
    r"unable|wont|won't|wouldnt|wouldn't|doesnt|doesn't|didnt|didn't|isnt|isn't|wasnt|wasn't|"
    r"never|stopped|fail|fails|failed|failing|struggling|struggles)\b[^.]{0,45}?"
    r"\b(drain|drains|draining|drained|empty|empties|emptying|emptied|pump|pumps|pumping)\b"
    r"|\b(drain\w*|pump\w*|emptying)\b[^.]{0,18}?\b(blocked|clogged|jammed|stuck|slow|slowly|"
    r"sluggish|not working|broken)\b"
    r"|\b(slow|slowly|sluggish)\b[^.]{0,18}?\b(drain|drains|draining|empty|emptying)\b"
    r"|\b(empty|emptying|drain|draining)\s+(the|my|its|this)\s+(machine|washer|drum|water)\b"
    r"|\b(get|getting|got)\s+(the|my|its|this)\s+(water|machine|washer|drum|washing|clothes)\b"
    r"[^.]{0,22}?\b(out|to drain|to empty)\b"
    r"|\b(to\s+(get\s+it\s+)?(drain|empty))\b")


# The leak row keys the bare word "water", so "my washing machine isnt heating the water" was
# stopped, unplugged and told to turn the water off - the same trap the drain row was in. What a
# leak needs is water leaving: a leak, a puddle, a drip, a flood, or water somewhere it should
# not be. Asking for that also gives "water is coming out of the washing machine" its leak, which
# it never had: that line was the laundry-sorting card.
_WATER_LEAVING = re.compile(
    r"\b(leak|leaks|leaked|leaking|leaky|puddle|puddles|drip|drips|dripping|dribble|"
    r"flood|floods|flooded|flooding|pour|pours|pouring|seep|seeps|seeping|seeped|"
    r"spill|spills|spilling|spilt)\b"
    r"|\b(coming out|came out|running out|spilling out|working its way out|"
    r"water under|water on the|water in the bottom|water all over|underneath|"
    r"under\s+(the\s+|my\s+)?(machine|washing machine|washer|drum)|under it|"
    r"on the floor|all over the floor|wet floor|damp patch)\b")


# What a line that is about a wash says: the machine, the cycle, the load. The temperature row
# holds the bare figures "30" and "40" as key words, so any line with a figure beside a money
# word could reach it - "my phone bill is 30 a month" was the cost of a 30C wash, and it only
# showed once "month" stopped reading as a when question.
A_WASH_NAMED = frozenset((
    "wash", "washes", "washed", "washing", "laundry", "load", "loads", "cycle", "cycles",
    "machine", "washer", "tumble", "drum", "eco"))


# The figures said as a temperature, and the bare figures. "is 30 or 40 cheaper" is the row's own
# comparison and names no wash at all, so two of its temperatures in one line is the row's subject
# as much as the word wash is.
A_TEMPERATURE_SAID = re.compile(
    r"\b(?:20|30|40|60)\s*(?:c|degrees?|deg)\b"
    r"|\b(?:twenty|thirty|forty|sixty)\s+degrees?\b")
A_BARE_TEMPERATURE = re.compile(r"\b(?:20|30|40|60)\b")


def _a_wash_is_named(understood):
    """True when the line is about a wash, which is the subject this row is about.

    A temperature is only the subject of a line that is already about washing: a bill, a battery
    and a bus fare are all said with one figure, and each of them is another question. So the row
    answers a line that names the wash, a line that says a figure as a temperature ("30c",
    "thirty degrees"), or a line that compares two of its temperatures, which is the row's own
    question however it is typed.
    """
    text = " ".join(str(one) for one in ((understood or {}).get("words") or ())).lower()
    if not text:
        text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    words = text.replace(",", " ").split()
    if any(word in A_WASH_NAMED for word in words):
        return True
    if A_TEMPERATURE_SAID.search(text):
        return True
    return len(set(A_BARE_TEMPERATURE.findall(text))) > 1


def _it_is_water_leaving(understood):
    """True when the line has water somewhere it should not be, which is what this row answers."""
    text = " ".join(str(one) for one in ((understood or {}).get("words") or ())).lower()
    if not text:
        text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    return bool(_WATER_LEAVING.search(text))


# The word "washer" is the machine to nearly everyone, and it is also the little rubber ring in a
# tap and the ring under a bolt. The rows that answer the machine read the bare word, which is
# right: on the deck almost every line that says "washer" means the appliance. What they must not
# do is answer a line that names the other one, so a plumbing or fixing word stands them down.
# "what size washer do i need for a 15mm tap" was told how many kilos a drum holds.
_A_WASHER = frozenset(("washer", "washers", "washing machine", "washer dryer"))
_ANOTHER_KIND_OF_WASHER = frozenset((
    "tap", "taps", "faucet", "faucets", "mixer", "monobloc", "ball valve", "ballcock",
    "bolt", "bolts", "nut", "nuts", "screw", "screws", "rawlplug", "rawlplugs", "anchor",
    "anchors", "rivet", "rivets", "dowel", "dowels", "valve", "valves",
    "radiator", "radiators", "banjo"))
_THE_MACHINE_ITSELF = frozenset(("washing machine", "washer dryer", "tumble dryer", "dryer",
                                 "drum", "laundry", "clothes"))


# A person who says they have already changed the washer is not asking how to change one: "my
# kitchen tap was dripping so i changed the washer" was answered with the washing machine's leak
# card, and the tap card would be nearly as wrong. What is left to do is the seat or the cartridge.
_A_WASHER_ALREADY_CHANGED = re.compile(
    r"\b(?:changed|change|replaced|replacing|swapped|swapping|new)\b[^.?!]{0,20}\bwasher\b"
    r"|\bwasher\b[^.?!]{0,20}\b(?:changed|replaced|swapped|done)\b", re.I)
_THE_NEXT_TAP_STEP = (
    "Then it is the seat rather than the washer. Take the head off again and look at the brass "
    "ring the washer presses on: if it is pitted or scored it can be re-ground with a seat tool, "
    "and if the tap turns a quarter turn it has a ceramic cartridge instead, which is replaced "
    "whole and matched by the maker's name stamped on the tap. A cartridge is a ten-minute swap "
    "and stops it for good; until then, turn the water off at the isolating valve when you leave "
    "the house.")
_THE_DRIPPING_TAP = (
    "A dripping tap is nearly always a worn washer or cartridge: turn the water off at the "
    "isolating valve under the sink, take the handle off, and take the old part to a hardware "
    "shop to match it. It's a 20-minute job and saves a lot of water.")


def _a_dripping_tap(memory, understood):
    """The washer is the answer, unless they have already changed it: then it is the seat."""
    said = str((understood or {}).get("clean") or (understood or {}).get("text") or "")
    if _A_WASHER_ALREADY_CHANGED.search(said):
        return _THE_NEXT_TAP_STEP
    return _THE_DRIPPING_TAP


def _not_a_washer_of_another_kind(understood):
    """False for a washer that is a tap's or a bolt's, which no machine row can answer."""
    words = set((understood or {}).get("words") or ())
    if not (_A_WASHER & words):
        return True
    if _THE_MACHINE_ITSELF & words:
        return True
    return not (_ANOTHER_KIND_OF_WASHER & words)


# A report that the washing has been done is a follow-up, not a question about which washer it is:
# "ive changed the washer" is asking what to do next, and this card is the first thing it must not
# get. The past forms are here as words because the key matches word forms, not words.
_A_WASHER_DONE = re.compile(
    r"\b(?:already|changed|changing|replaced|replacing|swapped|swapping|fitted|fitting|"
    r"sorted|done|did|tried|trying)\b", re.I)


def _a_washer_with_no_other_subject(understood):
    """True when "washer" is the whole subject of the line, so the answer has to hold both senses."""
    words = set((understood or {}).get("words") or ())
    if not (_A_WASHER & words):
        return False
    if _THE_MACHINE_ITSELF & words or _ANOTHER_KIND_OF_WASHER & words:
        return False
    said = str((understood or {}).get("clean") or (understood or {}).get("text") or "")
    return not _A_WASHER_DONE.search(said)


_WASHER_TWO_THINGS = (
    "Two things in a house are called a washer. The ring inside a tap costs pennies: turn the "
    "water off at the isolating valve, take the tap apart and take the old ring to a hardware "
    "shop to match - half an inch fits most taps, three quarters the older big bath taps. If it "
    "is the machine, the fix depends on what it is doing: water on the floor is usually the door "
    "seal or a hose, clothes that come out wet is the spin, and no heat is the element. All three "
    "are cheap parts, so a machine with a sound drum is worth repairing rather than replacing.")
# The same word in a chat that has already been about a tap is not two things at all: the person
# who says "i have a washer and a spanner" beside a dripping tap has the part in their hand and
# wants the next step, and telling them about the machine would be answering nobody.
_THE_TAP_WASHER = (
    "Good - then you have what you need. Turn the water off at the isolating valve under the sink "
    "or the small screw on the pipe, take the handle off and unscrew the head, then pick the old "
    "washer out with a small screwdriver. Match it at a hardware shop: half an inch fits most "
    "taps, three quarters the older big bath taps. A smear of silicone grease on the new one and "
    "it goes back the same way, and the spanner is for the big nut under the handle.")
_A_TAP_TALK = re.compile(r"\b(?:tap|taps|faucet|dripping|drip|drips|spout|cistern)\b", re.I)


def _the_chat_is_about_a_tap(memory, understood):
    """True when the last turn or two named a tap and nothing named the machine."""
    turns = (memory or {}).get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    said_now = str((understood or {}).get("text") or (understood or {}).get("clean") or "")
    said_now = said_now.strip().lower()
    seen = 0
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            continue
        text = str(turn.get("user") or "").strip().lower()
        if not text or text == said_now:
            continue
        if _THE_MACHINE_ITSELF & set(text.split()):
            return False
        if _A_TAP_TALK.search(text):
            return True
        seen += 1
        if seen >= 2:
            break
    return False


def _a_washer_two_things(memory, understood):
    """The washer that a chat has already identified, or the two senses when it has not."""
    if _the_chat_is_about_a_tap(memory, understood):
        return _THE_TAP_WASHER
    return _WASHER_TWO_THINGS


def _the_leak_is_a_machines(understood):
    """The leak row's guard, plus the other sense of "washer": a tap's, not the machine's."""
    return _it_is_water_leaving(understood) and _not_a_washer_of_another_kind(understood)


def _a_machine_that_will_not_empty(understood):
    """True when the line names a machine that will not empty, which is what this row answers.

    The appliance or the drum is in the key already; this is the fault half, so a question that
    only mentions the water - how much it uses, how hot it gets, what it smells of - stands the
    row aside and keeps its own answer.
    """
    text = " ".join(str(one) for one in ((understood or {}).get("words") or ())).lower()
    if not text:
        text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    return bool(_WILL_NOT_EMPTY.search(text))


def _the_bed_for_paving_or_blocks(memory, reading):
    line = (reading.get("clean") or reading.get("text") or "").lower()
    words = set(reading.get("words") or ())
    if words & {"block", "blocks", "setts", "pavers"} or any(
            phrase in line for phrase in ("block paving", "block paved", "block paver",
                                          "block paving drive", "paved drive",
                                          "paving the drive")):
        return ("Blocks are not bedded on a sand-and-cement mix: they go down on 30 to 40mm "
                "of sharp sand alone, compacted with a wacker plate, and the joints are "
                "brushed full of kiln-dried sand afterwards - so there is no cement to "
                "measure. For 20 square metres reckon on about one tonne of sharp sand for "
                "the bed and two or three 25kg bags of kiln-dried sand for the joints, plus "
                "an edge restraint on any open side, which is what stops the blocks "
                "spreading.")
    return ("Patio slabs go on a full bed of 5:1 sharp sand and cement, 30 to 40mm thick, "
            "never on five dabs: a 25kg bag of cement with five 25kg bags of sharp sand "
            "beds about 2 to 2.5 square metres, so a 20 square metre patio wants nine or "
            "ten bags of cement and two bulk bags of sand. The mix should be crumbly-damp "
            "- squeeze a ball and no water runs - and the joints are pointed afterwards "
            "with a 4:1 mix, not the bed mix.")
# A stool is a chair and a stool is what a person passes, and the reading does not always settle
# which: "my stools are loose" came in with no body part, no own output and no health topic at
# all, so the chair row answered a stomach complaint with the wood glue. When the reading says
# nothing, the words still do: a line that says the looseness of what a body passes, and says
# nothing about a piece of furniture, is the body's.
# The plural is the gut's and the singular is the chair's: "my stool is loose" is the leg, and
# the reading and `tests.test_loose_stools_are_the_stomach` already settle that, while "my stools
# are loose" is one person and the part of them the plural names. "poo" and "bowels" are never
# furniture, so they count in either number.
_LOOSE_STOOL = re.compile(
    r"\b(?:stools|poos?|faeces|feces|bowels?)\b[^.?!]{0,24}?"
    # "bowels" is already plural, so "loose" is the whole of the shape here
    r"\b(?:loose|runny|watery|soft|sloppy)\b"
    r"|\b(?:loose|runny|watery|sloppy)\s+(?:stools|poos?|faeces|feces)\b", re.I)
# Anything that says the line is about a chair or a table instead: the fixing words are in here,
# so "the loose leg on my stool" stays with the glue even though it says loose and stool.
_FURNITURE_WORDS = re.compile(
    r"\b(?:chair|chairs|table|tables|bench|benches|desk|desks|leg|legs|glue|screw|screws|"
    r"tighten|joint|joints|wood|wooden|seat|furniture|varnish|paint|repair|fix|wobbl\w*|"
    r"rock\w*|rickety)\b", re.I)


def _a_chair_and_not_a_body(understood):
    """False when the line is the looseness of what a body passes, rather than a wobbly chair."""
    from .body import the_stomach_is_what_it_is_about

    understood = understood if isinstance(understood, dict) else {}
    if the_stomach_is_what_it_is_about(understood):
        return False
    text = str(understood.get("clean") or understood.get("text") or "").lower()
    if _LOOSE_STOOL.search(text) and not _FURNITURE_WORDS.search(text):
        return False
    return True


def _the_fan_stopped(memory, understood):
    """The answer for the fan that will not sit still, or for a plain appliance that rocks."""
    text = str((understood or {}).get("clean") or (understood or {}).get("text") or "").lower()
    if re.search(r"\b(?:fan|fans|blade|blades)\b", text):
        return ("A fan that rocks is usually the base or a bent blade: tighten the nut under the "
                "base, then take the blade off and sight along it, because one blade out of line "
                "is the whole wobble and a new blade is a few pounds. Stand it on a hard, level "
                "floor rather than a rug, and wind out the feet if it has them.")
    return ("A wobble is a loose base or an uneven floor rather than a fault: wind the feet out "
            "until it sits flat on all of them, tighten what holds the base to the body, and take "
            "it off a rug or a soft board, which is what most of them are standing on. If it is "
            "still rocking it wants shimming on one corner.")


# "and the kitchen stuff" is what a person says when the packing is already the chat: the phrase
# names the room with "stuff" and has no verb in it, so on its own it asks nothing. Asked first
# thing in a chat it was a whole plan for the boxes ("Leave the kitchen to the second-to-last
# day..."), answering a house move nobody had mentioned. "stuff" and "the rest" stay keys, but
# only for a line that has a packing word of its own or that is taking up a chat already about
# moving.
_PACKING_VERB = frozenset((
    "pack", "packs", "packing", "packed", "box", "boxes", "boxed", "boxing", "packup"))


def _the_kitchen_stuff_is_a_take_up(understood):
    """The bare "kitchen stuff" line answers only when it takes up a line before it."""
    reading = understood or {}
    said = str(reading.get("clean") or reading.get("text") or "").lower()
    if set(re.findall(r"[a-z]+", said)) & _PACKING_VERB:
        return True
    return bool(reading.get("followup"))


# The heat pump explainer is for the machine in the garden, and the words for the ones in the
# house were what carried a dryer question into it: "is a heat pump dryer any good" was told how a
# heat pump moves heat, and "how do i fix my heat pump tumble dryer" would have been too. A use
# word beside a question about the appliance - what it costs, whether it is any good, a fault - is
# the appliance's row, and this explainer keeps the lines that ask what a heat pump is or how it
# works.
_HEAT_PUMP_USE = ("dryer", "drier", "tumble dryer", "tumble drier", "dehumidifier", "radiator",
                  "radiators", "hot water tank", "cylinder", "shower", "pool", "swimming pool",
                  "air conditioning", "hot tub", "underfloor", "boiler")
_HEAT_PUMP_ASK = ("fix", "fixing", "repair", "repairing", "not working", "broken", "fault",
                  "faulty", "any good", "worth", "worth it", "cost", "costs", "price", "cheap",
                  "cheaper", "run", "running", "buy", "buying", "recommend", "noise", "noisy",
                  "loud", "install", "installed", "installation", "smell", "smells",
                  "efficient", "good")


def _the_explainer_keeps_the_explainer(understood):
    """False when the line is about a heat pump appliance, not about what a heat pump is."""
    text = " " + (understood.get("clean") or understood.get("text") or "").lower() + " "
    if not any(word in text for word in _HEAT_PUMP_USE):
        return True
    return not any(word in text for word in _HEAT_PUMP_ASK)


def _hair_dryer(memory, reading):
    """The grille for a dryer that blows cold, the flex for one that is dead.

    A hair dryer that runs but never warms and one that will not start are two faults with two
    first checks, and the same line shapes carry both ("stopped working", "keeps cutting out").
    STYLE asks for the thing to do first in the first sentence, so the answer is chosen by what
    the person said the machine is doing.
    """
    words = set(str(one).lower() for one in (reading.get("words") or ()))
    dead = {"dead", "stopped", "stop", "wont", "won't", "wont.", "turn", "turns", "start",
            "starts", "switch", "switches", "power", "fuse", "buzzing", "buzzes", "nothing"}
    if words & dead:
        return ("A hair dryer that is completely dead is nearly always the plug or the flex, not "
                "the element: try another socket, check the fuse in the plug, and look at the "
                "point where the flex meets the handle, because a cable that is wound up every "
                "day is what breaks. If a fresh fuse blows again, stop using it - that is a short "
                "in the element, and a new dryer is cheaper than the repair.")
    return ("Check the air intake first: a hair dryer that blows cold usually has the grille at "
            "the back furred up with hair and fluff, and the thermal cut-out trips before the "
            "element ever fails. Unplug it, pull the hair off the grille and out of the vent, let "
            "it cool for ten minutes and try it again on the high setting. If it still runs cold "
            "it is the element or the cut-out, and on a cheap dryer that is a new one rather than "
            "a repair - do not open the case, the element is a live part.")


def _to_a_figure(value):
    """A figure a person would say out loud: 4.46 -> 4.5, 2.0 -> 2, 1 -> 1.

    "a wall 6 ft long and 8 ft high" is 4.46 square metres, and a card whose own numbers are
    "10 to 12" reads as a measurement taken in a laboratory rather than a wall. One decimal is
    as fine as the sums behind it go, and the trailing zero goes.
    """
    return round(float(value), 1)


def _counted(value, unit):
    """The figure with its noun agreed with it: "1 litre", "About 2.5 litres", "1 square metre"."""
    return "%g %s" % (value, unit if _to_a_figure(value) == 1 else unit + "s")


PAINT_WITH_NO_SIZE = (
    "One litre of emulsion covers about 10 to 12 square metres, and you need two coats, so "
    "count the wall area and double it: add the walls up as perimeter times ceiling height "
    "(a 4m by 4m room with 2.4m ceilings is about 38 square metres), take off roughly 1.7 "
    "square metres for a door and 1.2 for a window, and that room wants about 7 litres - two "
    "5 litre tins, or a 10 to leave some for touching up. Ceilings and a second colour are "
    "extra, and a dark colour over a light wall often takes three coats.")


def _paint_for_the_room(memory, understood):
    """The litres for the wall or room in the line, or the method when the line has no size.

    The size the person gave is the answer's raw material: a wall 6 metres long and 2.5 high is
    15 square metres, and 15 square metres at two coats and 10 to 12 to the litre is about 3
    litres. Handing back a worked example of a different room answers the method, not the
    question. A room said as two sides is painted round its walls, so the perimeter times the
    ceiling height is the area - the height the line names, or 2.4m. A line with no size in it
    keeps the method, which is the only thing that can be said without one.
    """
    from .home import _wall_area
    area, ceiling, what = _wall_area(understood, memory)
    if not area:
        return PAINT_WITH_NO_SIZE
    # Rounded up to the next half litre, never down: a person who buys 2.5 litres for a wall
    # that wants 2.7 is one coat short, and the tin sizes are 2.5, 5 and 10 anyway.
    litres = max(1.0, int(area * 2 / 11.0 * 2 + 0.999) / 2.0)
    area = _to_a_figure(area)
    coats = "%g" % _to_a_figure(area * 2)
    if what == "ceiling":
        count = ("A ceiling that size is %s, two coats makes %s, and a litre of "
                 "emulsion covers 10 to 12." % (_counted(area, "square metre"), coats))
    elif ceiling is None:
        count = ("That's %s, two coats makes %s, and a litre of emulsion "
                 "covers 10 to 12." % (_counted(area, "square metre"), coats))
    else:
        count = ("A room that size is %s round and %s to the ceiling, so about %s of wall, and "
                 "two coats makes %s."
                 % (_counted(_to_a_figure(area / ceiling), "metre"), _counted(ceiling, "metre"),
                    _counted(area, "square metre"), coats))
    # A door and a window are a room's business: a single wall of 7 square metres has neither, and
    # the subtraction only muddles the figure it was just given.
    if what == "ceiling":
        tail = ("Give the walls their own sum, and go a coat further when a white ceiling is "
                "going over a colour rather than over white.")
    elif ceiling is None:
        tail = ("Allow a third coat when a dark colour goes over a light one, and give the ceiling "
                "and any second colour their own sum.")
    else:
        tail = ("Take off roughly 1.7 square metres for a door and 1.2 for a window if they are in "
                "it, allow a third coat when a dark colour goes over a light one, and give the "
                "ceiling and any second colour their own sum.")
    return "About %s: %s %s" % (_counted(litres, "litre"), count, tail)


WALLPAPER_WITH_NO_SIZE = (
    "Count drops, not floor: divide the room's perimeter by the 52cm width of a standard roll and "
    "round up (a 4m by 4m room is 16m round, so 31 drops), then divide a roll's 10m by the ceiling "
    "height plus the pattern repeat to see how many drops each gives - usually three - and 31 drops "
    "is about 11 rolls. Buy one extra for a mistake and matching, and keep the batch number the "
    "same on every roll.")


def _wallpaper_for_the_room(memory, understood):
    """The rolls for the room in the line, or the method when the line has no size.

    A room said as two sides is papered round its walls, so the wall area already worked out for
    paint is the starting point: the perimeter is that area divided by the ceiling height, a
    standard roll is 52cm wide, and a 10m roll gives four drops of a plain paper at a 2.4m ceiling
    and three of a paper with a big repeat. A single wall has no perimeter to read the drops from,
    so it keeps the method, which is also what a line with no size gets.
    """
    from .home import _wall_area, _wall_width_and_height
    area, ceiling, what = _wall_area(understood, memory)
    if not area:
        return WALLPAPER_WITH_NO_SIZE
    if what == "wall":
        # A wall with a size in the line is drops along its own width, not a room's perimeter
        # read off an area: "how much wallpaper for a wall 1m by 1m" is one drop of a 52cm roll,
        # and the card's own example is a room, which is what it keeps teaching.
        width, height = _wall_width_and_height(understood, memory)
        if not width or not height:
            return WALLPAPER_WITH_NO_SIZE
        across = int(-(-width / 0.52 // 1))
        plain = max(1, int(10 // height))
        patterned = max(1, int(10 // (height + 0.3)))
        plain_rolls = int(-(-across / plain // 1))
        patterned_rolls = int(-(-across / patterned // 1))
        return ("About %s: a wall %s wide and %s high takes %s at the 52cm width of a standard "
                "roll, and a 10m roll gives %s of a plain paper or %s of one with a big repeat - "
                "so %s plain and %s patterned. Buy one extra for a mistake and matching, and keep "
                "the same batch number on every roll."
                % (_counted(plain_rolls, "roll"), _counted(_to_a_figure(width), "metre"),
                   _counted(_to_a_figure(height), "metre"), _counted(across, "drop"),
                   _counted(plain, "drop"), _counted(patterned, "drop"),
                   _counted(plain_rolls, "roll"), _counted(patterned_rolls, "roll")))
    if what != "room" or not ceiling:
        return WALLPAPER_WITH_NO_SIZE
    round_the_room = area / ceiling
    drops = int(-(-round_the_room / 0.52 // 1))
    plain = max(1, int(10 // ceiling))
    patterned = max(1, int(10 // (ceiling + 0.3)))
    rolls_plain = int(-(-drops / plain // 1))
    rolls_patterned = int(-(-drops / patterned // 1))
    return ("About %d rolls: a room that size is %g metres round and %g metres to the ceiling, so "
            "%d drops at the 52cm width of a standard roll, and a 10m roll gives %d drops of a "
            "plain paper or %d of one with a big repeat - so %d rolls plain and %d patterned. Buy "
            "one extra for a mistake and matching, and keep the same batch number on every roll."
            % (rolls_plain, round_the_room, ceiling, drops, plain, patterned,
               rolls_plain, rolls_patterned))


# A nail in a wall is two jobs: putting one in, and getting an old one out. The two lines share
# every noun they use ("nail", "wall", "picture"), so the row below reads the verb and answers
# the job that was asked for, the way the hair-dryer row reads the fault.
_A_NAIL_COMES_OUT = ("remove", "removing", "removed", "out", "puller", "pincers", "pull",
                     "pulling", "pulled", "old", "stuck", "left", "loose", "snapped", "broke",
                     "broken", "half")


def _a_nail_in_the_wall(memory, reading):
    """How to get an old nail out of a wall, or how to put a new one in so it holds."""
    words = set(str(one).lower() for one in (reading.get("words") or ()))
    if words & set(_A_NAIL_COMES_OUT):
        return ("Grip the head with pincers and slide a scrap of wood under them so the plaster "
                "does not crush, then ease it out with a slight twist rather than levering "
                "against the wall. A nail that turns but will not come has lost its grip: punch "
                "it below the surface with another nail, fill the dent with filler, sand it flat "
                "and touch up the paint.")
    return ("Tap it in at a slight downward angle so the weight hangs on the wall instead of "
            "pulling the head out, and put it into something solid - a stud, found by tapping, "
            "or brick under the plaster. On plasterboard with nothing behind it a bare nail or "
            "a picture hook pulls out: use a plasterboard plug or a self-drilling fixing, and "
            "keep the load light.")


# A nail into wood is two questions: how not to split the board, and what size to buy. The same
# line shapes carry both ("what nail for ...", "how do i stop ... splitting"), so the row reads
# which one was asked, the way the nail-in-a-wall row reads putting in from taking out.
_A_SIZE_ASK = ("size", "sizes", "what size", "which size", "what length", "how long", "how big", "how thick", "which nail",
               "what nail", "what nails", "how many mm", "mm", "gauge", "best nail", "should i use")
_A_SPLIT_ASK = ("split", "splits", "splitting", "crack", "cracks", "cracking", "splinter",
                "splinters", "splintering", "snapped")


def _the_wood_and_the_nail(memory, reading):
    """What size of nail to buy, or how to drive one without splitting the board."""
    words = set(str(one).lower() for one in (reading.get("words") or ()))
    said = " " + " ".join(str(one).lower() for one in (reading.get("words") or ())) + " "
    # the asks are phrases ("what size", "how long"), and `words` holds one word each, so the
    # joined line is what the phrase list is read against
    if (any(ask in said for ask in _A_SIZE_ASK)) and not (words & set(_A_SPLIT_ASK)):
        return ("Size the nail to the job, not to the room: 40mm to 50mm lost-head or oval nails "
                "for skirting and architrave, 50mm to 65mm for a floorboard, 30mm for a 6mm "
                "batten, and thin panel pins for beading and a back panel. As a rule the nail "
                "wants to be about two and a half times as long as the piece it is holding, and "
                "the top third of it has to bite into something solid behind.")
    return ("Drill a pilot hole first, about three quarters as wide as the nail, and keep it at "
            "least 25mm in from the end of the board, because that is where a split starts. "
            "Blunt the point by tapping it once on a hard surface so it cuts the grain instead "
            "of wedging it apart, and clamp a scrap of wood behind the far face when the board "
            "is thin. A split that has already opened wants wood glue worked into it and a "
            "clamp overnight, not another nail.")


# The move-and-a-child card answers one question: how to tell a child about the move. Its key
# carries the feeling words ("upset", "worried", "nervous", "sad", "cope") because a child's feeling
# is often the whole line - "my son is upset about moving" - and with them the card answered the
# person who had moved themselves: "im sad after moving house", "i feel sad about moving house",
# "im worried about moving house" and "we are moving and i feel nervous" all got "Tell them as soon
# as it is certain ... which room is theirs". A feeling in the speaker's own line is not a question
# about telling a child, so the card is a guard rather than a longer avoid list: an avoid phrase only
# covers the wordings someone thought of, and every new feeling word would need another one.
_A_CHILD_IN_A_MOVE = re.compile(
    r"\b(?:kid|kids|child|children|son|sons|daughter|daughters|teenager|teenagers|teen|teens|"
    r"toddler|toddlers|baby|babies|boy|boys|girl|girls|schoolchild|schoolchildren|"
    r"stepson|stepdaughter|stepchildren|little one|little ones|the youngest|the eldest)\b")

# "how do i tell them we are moving" names no child and is still this card's question, so a line
# that asks for the words to say passes too. It is the telling that makes the audience the children,
# not the noun: "how do i tell my mum i'm moving out" is answered by family.py and never reaches
# this row, because "move out" is in the avoid list below.
_A_TELLING_THE_LINE_ASKS_FOR = re.compile(
    r"\b(?:tell|tells|telling|told|explain|explains|explaining|explained|break the news|"
    r"let them know|lets them know|prepare them|preparing them|reassure|reassuring)\b")


def _a_child_or_a_telling(understood):
    """True when the line names a child, or asks for the words to say about the move.

    Used as the `guard` by the moving-with-kids row. Without it the row's feeling words answer the
    person who moved: "im sad after moving house" was told how to tell a child, and so was
    "i feel sad about moving house" and "im worried about moving house". A line with nobody to tell
    in it is not that question.
    """
    said = understood if isinstance(understood, dict) else {}
    text = " ".join(str(said.get("norm_text") or said.get("plain") or said.get("text") or "")
                    .lower().split())
    return bool(_A_CHILD_IN_A_MOVE.search(text) or _A_TELLING_THE_LINE_ASKS_FOR.search(text))
# The outside-drying row answers the weather, and a line that says inside, a bathroom, a
# radiator, a rack or a tumble dryer wants the drying-indoors answer instead. Those words cannot
# be an avoid list: a line with a "without" clause is read twice, and on the reading with the
# clause emptied the words are gone - "how do i dry clothes without a tumble dryer" reached the
# outside row on "dry" and "clothes" alone, once the ironing card had turned the same line down.
# The guard reads the line as it was typed, so the clause's words are still there.
_DRY_IT_INDOORS = (
    "inside", "indoors", "indoor", "in the house", "in the flat", "bathroom", "radiator",
    "airer", "rack", "maiden", "tumble dryer", "tumble drier", "tumbledryer", "dryer",
    "drier", "dehumidifier", "no garden", "no line", "nowhere to hang", "condensation",
)
_DRYING_WORD = re.compile(r"\bdry(?:ing|s|er|d)?\b|\bhang(?:ing)?\b|\bwashing\b|\blaundry\b",
                          re.I)
# A line that names the weather is the outside row's own question even when it says inside:
# "should i bring the washing inside before the rain" is a forecast question, not a rack one.
_THE_WEATHER = re.compile(
    r"\b(?:rain|rains|raining|rainy|showers?|forecast|wind|winds|windy|sun|sunny|sunshine|"
    r"weather|frost|frosty|drizzle|damp|fog|line|outside|out there|today|tomorrow|dry out)\b",
    re.I)


# A load of washing, named. A room being damp is not a load: "how do i dry out a damp room"
# is the damp card's question, and naming a room only says where the washing is.
_A_LOAD_NAMED = re.compile(
    r"\b(?:washing|laundry|clothes|clothing|load|jeans|trousers|shirts|sheets|bedding|"
    r"towels?|duvets?|jumpers?|coats?|jackets?|wool|knitwear|uniform|school uniform)\b", re.I)
# The rooms a person dries a load in. A flat with one room and no garden is the whole reason
# the line is asked: "how do i dry clothes in a damp flat" was told "a dry, breezy day dries a
# normal load outside in two to four hours", which is no help to somebody with no outside.
_A_ROOM = re.compile(
    r"\b(?:room|rooms|bedroom|kitchen|bathroom|cellar|loft|hallway|hall|utility|"
    r"flat|house|home|studio|caravan)\b", re.I)
# "damp" is a room and a day at once, so a named room tells us which one it is here.
_WEATHER_NOT_A_ROOM = re.compile(
    r"\b(?:rain|rains|raining|rainy|showers?|forecast|wind|winds|windy|sun|sunny|sunshine|"
    r"weather|frost|frosty|drizzle|fog|line|outside|out there|today|tomorrow)\b", re.I)


def _not_a_drying_inside_question(understood):
    """False when the line is about drying the washing indoors rather than in the weather."""
    text = " " + str(understood.get("clean") or understood.get("text") or "").lower() + " "
    if not _DRYING_WORD.search(text):
        return True
    if _A_LOAD_NAMED.search(text) and _A_ROOM.search(text):
        # the load and the room are both named: the rack's answer, unless the weather is the
        # question ("should i bring the washing inside before the rain")
        return bool(_WEATHER_NOT_A_ROOM.search(text))
    if not any(word in text for word in _DRY_IT_INDOORS):
        return True
    return bool(_THE_WEATHER.search(text))


def entries():
    """The rows `home.py` builds its list from, in their original order."""
    from ..knowledge_parts import (
        home_craft_rows_01,
        home_craft_rows_02,
        home_craft_rows_03,
        home_craft_rows_04,
        home_craft_rows_05,
        home_craft_rows_06,
        home_craft_rows_07,
        home_craft_rows_08,
        home_craft_rows_09,
        home_craft_rows_10,
    )

    return [
        *home_craft_rows_01.rows(),
        *home_craft_rows_02.rows(),
        *home_craft_rows_03.rows(),
        *home_craft_rows_04.rows(),
        *home_craft_rows_05.rows(),
        *home_craft_rows_06.rows(),
        *home_craft_rows_07.rows(),
        *home_craft_rows_08.rows(),
        *home_craft_rows_09.rows(),
        *home_craft_rows_10.rows(),
    ]

