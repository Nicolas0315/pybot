"""Part 2 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
import re
from .lookup_part_01 import (
    A_GOOD_SMELL, BEFORE_OFF, FOOD_NAMED, OFF_SAID_OF_FOOD, OFF_STATE_ASKS, SMELL_VERBS,
    _BAD_IS_A_STATE, said, _BORROWING_IN_THE_LINE, string, Entry, _avoid_words, MIN_FORM, lexicon,
    WORD,
)


def food_has_gone_off(understood):
    """Whether the line says the food it names has gone off.

    "my chicken smells a bit, can i cook it", "the milk has gone sour", "is my chicken still ok
    to eat". The rows that are about something else - a smell in the room, what is in a food -
    stand down on it, and `bot/knowledge/still_ok.py` answers.
    """
    if not isinstance(understood, dict):
        return False
    text = str(understood.get("plain") or understood.get("clean") or understood.get("text")
               or "").lower()
    words = tokens(text)
    if not words or not any(word in FOOD_NAMED for word in words):
        return False
    for phrase in OFF_STATE_ASKS:
        if phrase in text:
            return True
    for pos, word in enumerate(words):
        if word not in FOOD_NAMED:
            continue
        at = pos + 1
        while at < len(words) and words[at] in BEFORE_OFF:
            at += 1
        if at >= len(words):
            continue
        said = words[at]
        # "is ham processed meat bad for you" is a diet question: "bad" said *of* the food is a
        # smell, "bad for you" is the verdict a nutrition row gives.
        if said == "bad":
            # "is ham processed meat bad" is a diet question and "bad for you" is its verdict,
            # while "the ham has gone bad" and "this ham smells bad" are the smell. The words
            # between the food and "bad" say which one it is: a state verb there makes it the
            # food's condition, and nothing there makes it the verdict the nutrition rows give.
            between = words[pos + 1:at + 1]
            if not any(word in _BAD_IS_A_STATE for word in between):
                continue
        if said in OFF_SAID_OF_FOOD:
            return True
        if said in SMELL_VERBS:
            after = words[at + 1:at + 2]
            if not after or after[0] not in A_GOOD_SMELL:
                return True
    return False


# A person, and not a thing, is what was asked off. "money off my holiday" and "money off my
# order" are discounts and stay; the relatives are the loan.
_OFF_A_PERSON = re.compile(
    r"\b(?:money|quid|pounds?|cash|tenner|fiver|ton|grand|\d+)\s+off\s+(?:of\s+)?"
    r"(?:a|an|my|our|your|his|her|their)\s+"
    r"(?:mum|mam|mammy|mother|mam|dad|father|parents?|brother|brothers|sister|sisters|"
    r"gran|granny|nan|nana|grandma|grandad|grandpa|son|daughter|child|kid|uncle|aunt|auntie|"
    r"cousin|husband|wife|partner|boyfriend|girlfriend|mate|mates|friend|friends|neighbour|"
    r"neighbours|boss|colleague|colleagues|workmate|flatmate|housemate|lodger|landlord)\b")


def a_price_not_a_loan(understood):
    """True when a price row may answer: the line is a discount and not money off a person.

    `guard=` on every entry that reads a price, so the whole lane agrees on the one rule instead
    of each row fencing its own phrases. "should i borrow money off my mum", "can i get twenty
    quid off my dad", "is it ok to borrow money off my parents" and the six other ways of saying
    it are the borrowing rows' lines, and they fall through to those rows when this says no.
    """
    said = understood if isinstance(understood, dict) else {}
    text = str(said.get("text") or said.get("clean") or "")
    if not text:
        text = " ".join(str(one) for one in (said.get("words") or ()))
    if not text:
        return True
    return not (_BORROWING_IN_THE_LINE.search(text) or _OFF_A_PERSON.search(text))


_FLAT_YOU_LIVE_IN = re.compile(
    r"\b(?:my|the|our|this|that|their|his|her|a|one)\s+"
    r"(?:tiny\s+|small\s+|little\s+|new\s+|old\s+|top\s+floor\s+|ground\s+floor\s+|"
    r"second\s+floor\s+|studio\s+)?flat\b"
    # a verb of moving, renting or buying takes the bare word as well as the determiner
    r"|\b(?:move|moves|moved|moving|rent|rents|rented|renting|let|letting|buy|buys|bought|"
    r"buying|sell|sells|selling|sold|view|viewing|sort|sorting|sorted|decorate|decorating|"
    r"refurbish|refurbishing)\s+(?:(?:a|an|the|my|our|this|that|his|her)\s+)?"
    r"(?:tiny\s+|small\s+|little\s+|new\s+|old\s+)?flat\b"
    # a verb that is also about a bake needs the determiner: "heat my flat", never "heat flat"
    r"|\b(?:heat|heating|clean|cleaning)\s+(?:a|an|the|my|our|this|that)\s+"
    r"(?:tiny\s+|small\s+|little\s+)?flat\b"
    r"|\bflats\b|\bflat\s?mates?\b|\bbedsit\b", re.IGNORECASE)


# "Heated" of people is an argument, not warmth. "my husband got heated at the table last night"
# was the hot-night card ("Cool the room rather than the bed") and "things got heated at dinner"
# the quick-dinner row, both on the word alone: a row is a different subject with its own card
# (row-escalating), and no temperature row is about it. "got heated up" is left out, because a
# radiator and a plate of food do heat up.
_THE_HEAT_OF_AN_ARGUMENT = re.compile(
    r"\b(?:got|get|gets|getting|bit|a bit|so|very|really|quite|all)\s+heated\b(?!\s+up)"
    r"|\bheated\s+(?:with|at|about|over|argument|arguments|discussion|discussions|row|rows|"
    r"debate|debates|exchange|exchanges|words|moment|moments|conversation)\b",
    re.IGNORECASE)


def not_the_heat_of_an_argument(understood):
    """True unless the line's "heated" is people or a row rather than a room or a night.

    A guard for the rows that read a temperature, so the words stay in the knowledge base: the
    reading of the line comes from the understanding engine, and this only asks whether the
    word in this line is the warmth the row is about.
    """
    if not isinstance(understood, dict):
        return True
    said = understood.get("text") or understood.get("clean") or ""
    if not said:
        said = " ".join(understood.get("words") or ())
    return not _THE_HEAT_OF_AN_ARGUMENT.search(str(said))


# --- the ask that wants the order of steps -------------------------------------------------
# "what should i do first", "what do i sort first" and "what should i pick first" ask for the
# order of the steps, and the "should i" in them is the same two words as "should i move house".
# The deciding rows read it as a decision and answer a yes/no about a thing the line never named
# as one: "moving house what should i do first" got the move-or-not answer, and the same line
# without the word "should" got the moving plan, which is the answer it wanted.
#
# The test is the object of the ask. A decision's object is the thing being decided ("should i
# move house", "should i sell the car"), and the object here is the empty verb itself - do, sort,
# pick, get - followed by a word that says the person wants an order: first, next, before.
_ORDER_OF_STEPS = re.compile(r"""
    \b what \s+ (?:should|shall|do|would|must|can) \s+ (?:i|we) \s+
       (?: do|sort|pick|choose|get|buy|wash|clean|tackle|start|book|pack|fix|handle
         | plan|change|replace|check|ask|say|look \s+ at|deal \s+ with|set \s+ up
         | make|go \s+ for|put \s+ up )
    \b .* \b (?:first|next|before|afterwards|after \s+ that) \b
""", re.X | re.I)


def the_ask_is_the_order_of_steps(understood):
    """True when the line asks what to do first rather than whether to do a thing."""
    if not isinstance(understood, dict):
        return False
    said = understood.get("text") or understood.get("clean") or ""
    if not said:
        said = " ".join(understood.get("words") or ())
    return bool(said) and bool(_ORDER_OF_STEPS.search(str(said)))


def not_the_ask_about_the_order(understood):
    """For a row that answers a decision: an ask for the order is not a decision."""
    return not the_ask_is_the_order_of_steps(understood)


def not_the_flat_you_live_in(understood):
    """True unless the line's "flat" is the home, for a row that keys flat as a bake or a hair."""
    if not isinstance(understood, dict):
        return True
    said = understood.get("text") or understood.get("clean") or ""
    if not said:
        said = " ".join(understood.get("words") or ())
    return not _FLAT_YOU_LIVE_IN.search(str(said))


# "flat" of a thing somebody made is how it turned out, not what the ground is: "the bread came
# out flat" was answered with a canal towpath ("a flat riverside path"), and so were a cake, a
# pizza, a Yorkshire pudding and an omelette. The bake rows key their own names (bread-rise has
# "flat" in its key), so this only has to stand a walking row aside where the flat thing came out
# of an oven or a pan - either named, or read from the verb that says it turned out that way.
_A_BAKE_OR_A_PAN = re.compile(
    r"\b(?:bread|breads|loaf|loaves|cake|cakes|sponge|scones?|pastry|pastries|tarts?|buns?|"
    r"rolls?|pizza|pizzas|pancakes?|omelettes?|omelets?|yorkshires?|puddings?|meringues?|"
    r"souffles?|biscuits?|cookies?|brownies?|crumpets?|dough|naan|pittas?|pita|ciabatta|"
    r"focaccia|baguette|batter|sourdough|flatbread|chapatis?|tortillas?|waffles?|loaf tin)\b",
    re.IGNORECASE)


# The same reading without naming the food: "came out flat", "turned out flat" are about what was
# being made, unless the line is about the ground underfoot ("the path looked flat on the map").
_CAME_OUT_FLAT = re.compile(
    r"\b(?:came|come|comes|coming|turned|turns|turning|went|gone|goes|going)\s+"
    r"(?:out\s+)?(?:a\s+bit\s+|a\s+little\s+|really\s+|so\s+|rather\s+|too\s+)?flat\b",
    re.IGNORECASE)


_THE_GROUND_UNDERFOOT = re.compile(
    r"\b(?:walk|walks|walking|walked|stroll|strolls|hike|hikes|route|routes|path|paths|"
    r"towpath|trail|trails|terrain|ground|fields?|park|parks|promenade|seafront|beach|"
    r"miles?|kilometres?|outing|day out|somewhere to go|wheelchair|buggy|pram|pushchair)\b",
    re.IGNORECASE)


def not_the_flat_of_something_made(understood):
    """True unless the line's "flat" is how a thing somebody made turned out.

    A guard for the row that reads flat as the ground: "the bread came out flat" is the loaf, and
    the bake rows have their own answers for it.
    """
    if not isinstance(understood, dict):
        return True
    said = understood.get("text") or understood.get("clean") or ""
    if not said:
        said = " ".join(understood.get("words") or ())
    said = str(said)
    if not re.search(r"\bflat\b", said, re.IGNORECASE):
        return True
    if _A_BAKE_OR_A_PAN.search(said):
        return False
    if _CAME_OUT_FLAT.search(said) and not _THE_GROUND_UNDERFOOT.search(said):
        return False
    return True


# --- what a figure in years belongs to ---------------------------------------
# "my bike is a carrera, about 4 years old" got the child's inside-leg measurement, "my bike is 3
# years old and the gears slip" the same card instead of the gear adjustment, and "my phone is an
# iphone, about 3 years old" the under-two screen limit. Rows key "year old" as a sign that a
# child is in the line, which is right for a child and wrong for a machine: the figure is the age
# of the thing the person owns. No avoid word can tell the two apart, because the words are the
# same either way, so the line itself is read for which the figure belongs to.
_YEAR_OLD_FIGURE = re.compile(r"\b(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven"
                             r"|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
                             r")\s*(?:years?|yrs?)\s+old\b", re.I)


# The line says what is old: "my bike is a carrera, about 4 years old", "the boiler's 12 years old".
_A_THING_SAID_IS = re.compile(
    r"\b(?:my|our|your|his|her|their|the)\s+(?P<noun>[a-z][a-z' -]{0,40}?)\s*"
    r"(?:is|was|are|were|'s|s)\b[^.!?]{0,40}$", re.I)


# Or just names one, with the figure after it: "my bike 4 years old, is it worth a service",
# "the boiler 15 years old worth fixing". One word of the thing, because a longer window starts
# reading the article of a child's age: "is the frozen film ok for a 4 year old" is a film, not a
# figure of a thing's. A person named there is the exception and is caught before this is asked:
# "my son, 4 years old, is biting" is a child's age and stays one.
_A_THING_JUST_BEFORE = re.compile(r"\b(?:my|our|the|his|her|their)\s+[a-z][a-z']{1,14}\s*,?\s*$",
                                  re.I)


# Or points at one as the subject of the age: "its about 4 years old", "that is 4 years old",
# "they are 4 years old". The word has to carry the age, not sit in the asking: "is it normal that
# a 5 year old cant write his name" is a child, and a bare "it" in front of it is not a thing.
_A_THING_POINTED_AT = re.compile(
    r"\b(?:it|its|it's|that|this|they|these|those)\s+"
    r"(?:(?:is|was|are|were|'s|about|roughly|around|only|just|nearly|now|prob)\b[\s,]*){1,3}$",
    re.I)


# A person named near the figure: the figure is theirs, and the row is right to answer.
_PEOPLE_AGED = re.compile(
    r"\b(?:i|me|my son|my daughter|my child|my children|my kid|my kids|my boy|my girl|son"
    r"|daughter|child|children|kid|kids|boy|girl|baby|toddler|teen|teenager|he|she|him|her"
    r"|his|hers|mum|dad|mother|father|wife|husband|partner|friend|nephew|niece|grandson"
    r"|granddaughter|grandchild)\b", re.I)


def the_years_are_a_things(understood):
    """True when every figure in years on the line belongs to a thing and not to a person."""
    text = ""
    if isinstance(understood, dict):
        text = str(understood.get("text") or understood.get("clean") or "")
        if not text:
            text = " ".join(str(word) for word in (understood.get("words") or ()))
    text = " ".join(text.lower().split())
    if not text:
        return False
    figures = list(_YEAR_OLD_FIGURE.finditer(text))
    if not figures:
        return False
    for found in figures:
        window = text[max(0, found.start() - 60):found.start()]
        if _PEOPLE_AGED.search(window):
            return False
        if not (_A_THING_SAID_IS.search(window) or _A_THING_JUST_BEFORE.search(window)
                or _A_THING_POINTED_AT.search(window)):
            return False
    return True


# The words a row uses when the figure in years is a child's: a person named beside the age. A row
# that keys "year old" next to "child", "kid", "son" or "toddler" is asking whether there is a child
# in the line, which is why the age of a machine was answered as one. A row that keys the age next
# to a thing of its own - the fridge that is 12 years old and wants replacing - is asking about the
# thing, and must keep it.
_CHILD_WORDS = frozenset((
    "child", "childs", "children", "kid", "kids", "son", "sons", "daughter", "daughters",
    "boy", "boys", "girl", "girls", "baby", "babies", "toddler", "toddlers", "teen", "teens",
    "teenager", "teenagers", "newborn", "newborns", "stepson", "stepdaughter", "grandchild",
    "grandchildren", "grandson", "granddaughter", "nephew", "niece", "pupil", "pupils",
))


_CHILD_PHRASES = frozenset(("little one", "little boy", "little girl", "a child", "my child",
                            "the child", "our child", "my kids", "school age child"))


_A_YEARS_OLD = re.compile(r"\b(?:years?|yrs?) old\b", re.I)


def _the_age_is_a_childs(item):
    """True when a row's own key says the figure in years belongs to a child.

    Rows that answer a parent's line carry the child in their key - `bike-child-seat` has "child",
    "kid", "son", "daughter", "toddler", "boy", "girl" beside "year old" - and those rows are the
    ones that read the age of the person's own bike or handset as a child's. Rows that answer a
    thing's own line, a fridge that is 12 years old and wants replacing, name a thing and no
    person, so the same test leaves them alone.
    """
    known = _CHILDS_AGE_ROWS.get(item.id)
    if known is not None:
        return known
    words, phrases = set(), []
    stack = list(item.key or ())
    while stack:
        part = stack.pop()
        if isinstance(part, str):
            plain = part.lower().replace("'s", "s")
            words.update(plain.split())
            phrases.append(plain)
        elif isinstance(part, (tuple, list, frozenset, set)):
            stack.extend(part)
    a_person = bool(_CHILD_WORDS.intersection(words)) or any(
        phrase in _CHILD_PHRASES for phrase in phrases)
    answer = a_person and _key_says_years_old(item)
    _CHILDS_AGE_ROWS[item.id] = answer
    return answer


def _key_says_years_old(item):
    """True when any string in the row's key holds a figure in years."""
    stack = list(item.key or ())
    while stack:
        part = stack.pop()
        if isinstance(part, str):
            if _A_YEARS_OLD.search(part):
                return True
        elif isinstance(part, (tuple, list, frozenset, set)):
            stack.extend(part)
    return False


_CHILDS_AGE_ROWS = {}


# "keep an eye out for a rash" and "keep an eye on his temperature" are watching and waiting:
# the eye is the instrument of the watching, not the thing that hurts. Read as the word, it made
# every row keyed on the eye answer a question about warning signs - "what should i keep an eye
# out for with my son" was given the conjunctivitis card and "keep an eye on his temperature"
# the "Got it" shrug. The same words are one idiom in every line they appear in, so the guard
# lives here and both the eye rows use it, whatever else the line says.
#
# It is one idiom in either number, and the singular-only reading was the hole in it: people say
# "keep my eyes open", "keep your eyes peeled", "keeps his eyes on the ball", and read with
# `eye` alone none of those matched, so the plural fell through to the eye rows. "i can barely
# keep my eyes open" was answered with the conjunctivitis card - bathe it with cooled boiled
# water - when the line is a tired body and not an eye complaint at all.
_KEEPING_AN_EYE = re.compile(
    r"\b(?:keep|keeps|keeping|kept|have|has|having|had|get|gets|getting|got)\s+"
    r"(?:a|an|one|my|your|his|her|their|our|both|the)?\s*eyes?\s*"
    r"(?:out|on|peeled|open|skinned|glued|trained)\b"
    # The eye first and the watching after it: "eyes peeled", "eyes on the road".
    r"|\beyes?\s+(?:peeled|open\s+for|on\s+(?:the|him|her|them|it|that|this|what))\b"
    r"|\bturn(?:s|ed|ing)?\s+a\s+blind\s+eye\b|\beyes?\s+in\s+the\s+back\s+of\b"
    r"|\beye\s+contact\b|\beye\s+witness\b|\bprivate\s+eye\b|\beagle\s+eye\b",
    re.IGNORECASE)


def not_keeping_an_eye_on_it(understood):
    """True unless the line's "eye" is the watching rather than the thing that hurts."""
    if not isinstance(understood, dict):
        return True
    said = understood.get("text") or understood.get("clean") or ""
    if not said:
        said = " ".join(understood.get("words") or ())
    return not _KEEPING_AN_EYE.search(str(said))


# A body that is short of sleep says so without the word sleep and without any "can't": "i keep
# nodding off at my desk", "my eyes keep closing on the bus", "im falling asleep at my laptop",
# "i can barely keep my eyes open". Read as nothing about sleep, every one of those was answered by
# whatever row happened to share a word with it - the chair and the screen height for a desk, the
# 20-20-20 rule for eyes, the sleep timer of a laptop. It is one statement, so it is read once here
# and the rows that are not about it stand down (`not_a_sleepy_body`), while the tired answer is the
# one that takes the turn.
SHORT_OF_SLEEP = re.compile(
    # the verb alone is not sleep: "i keep falling over" is the falls, "i keep dropping things"
    # is the hands. Only nodding and dozing stand on their own; falling and dropping want the
    # asleep after them.
    r"\b(?:keep|keeps|keeping|kept)\s+(?:(?:nodding|dozing)\s*(?:off|asleep)?|(?:falling|dropping)\s+(?:off|asleep))\b"
    r"|\bnodd(?:ing|ed|s)?\s+off\b|\bdoz(?:e|es|ed|ing)\s+off\b"
    r"|\beyes?\s+(?:keep|keeps|are|were)?\s*(?:closing|dropping|shutting)\b"
    # "keep my eyes open" is the tiredness, unless the words say what they are being kept open
    # FOR - "keep my eyes open for a bargain" is watching for one.
    r"|\b(?:keep|keeps|keeping|kept)\s+(?:my|your|his|her|their|our|both)?\s*eyes?\s+open\b"
    r"(?!\s+for\b)"
    r"|\bf(?:all|ell)(?:ing|s)?\s+asleep\s+(?:at|in|on|during|over)\b"
    # "i can barely keep up with the rent" is the rent: the shortest form of this shape caught
    # it, and only the word after it says which one it is, so the sleep is asked for too.
    r"|\bcan\s*(?:'?t|cant|not)?\s*(?:barely|hardly)\s+(?:keep|stay)\s+"
    r"(?:(?:my|your|his|her|their|our|both)\s+)?(?:eyes?\s+open|awake|alert)\b",
    re.IGNORECASE)


# An eye that is closing because of pollen is the allergy, not a shortage of sleep: "my eyes are
# closing up with hay fever" is answered by the hay-fever reading, and called tiredness it got a
# kind word about bad nights and no mention of the thing that is actually wrong.
NOT_TIRED_AFTER_ALL = re.compile(
    r"\b(?:hay ?fever|allerg(?:y|ies|ic)|pollen|conjunctivitis|stye|sty|glued|"
    r"swollen|puffy|watering|streaming)\b", re.IGNORECASE)


# The thing that "keeps falling asleep" is not always a person. A laptop, a phone and a console
# all do it, and their own rows answer it ("It is the power setting, not a fault"); read as a
# sleepy body the power row stands down and the person is told about bad nights instead. What
# decides it is the subject the words put in front of the sleeping, so the two lists are read
# against each other up to the shape: "my laptop keeps falling asleep" is the laptop's line, and
# "i keep falling asleep at my laptop" is the person's, with the laptop after the verb.
A_DEVICE_THAT_SLEEPS = frozenset((
    "laptop", "laptops", "computer", "computers", "pc", "pcs", "mac", "macs", "macbook",
    "phone", "phones", "iphone", "android", "tablet", "tablets", "ipad", "monitor", "monitors",
    "screen", "screens", "tv", "television", "televisions", "console", "consoles", "xbox",
    "playstation", "kindle", "printer", "printers", "camera", "cameras", "watch", "fitbit",
))


# The subjects that make the sleeping a person's: the person, the body part that sleeps, and the
# child a parent is talking about ("the kids keep falling asleep at the table").
_A_PERSON_WHO_SLEEPS = frozenset((
    "i", "im", "i'm", "me", "myself", "we", "us", "ourselves", "he", "him", "himself",
    "she", "her", "herself", "they", "them", "themselves", "you", "eyes", "eye", "head",
    "body", "kid", "kids", "child", "children", "baby", "son", "daughter", "boy", "girl",
    "boy", "boys", "girls", "toddler", "lad", "lass", "teenager", "nan", "dad", "mum",
))


# The marks the words carry into this file; the line is split on spaces, so a plain strip is all
# a possessive or a comma needs.
_SLEEPY_MARKS = string.punctuation + "\u2019"


def _the_device_is_the_one_falling_asleep(said, start):
    """Whether the words in front of a sleep shape name a device rather than the person."""
    device = person = -1
    for index, word in enumerate(said[:start].split()):
        bare = word.strip(_SLEEPY_MARKS).lower()
        if bare in A_DEVICE_THAT_SLEEPS:
            device = index
        elif bare in _A_PERSON_WHO_SLEEPS:
            person = index
    return device >= 0 and device >= person


def the_body_is_short_of_sleep(understood):
    """Whether the line says the person's body is short of sleep, in the words that say it."""
    said = _the_whole_line(understood)
    if NOT_TIRED_AFTER_ALL.search(said):
        return False
    for shape in SHORT_OF_SLEEP.finditer(said):
        if not _the_device_is_the_one_falling_asleep(said, shape.start()):
            return True
    return False


def not_a_sleepy_body(understood):
    """A `guard=` test: True unless the line is a body that is short of sleep.

    For the rows that answer where somebody is sitting or what they are looking at. "i keep
    nodding off at my desk" is not a chair problem and "my eyes keep closing at the screen" is not
    eye strain, so those rows stand aside and the tired answer takes the turn.
    """
    return not the_body_is_short_of_sleep(understood)


def all_of(*guards):
    """One `guard=` test from several, true only when every one of them says the row may answer.

    A row can have more than one thing to stand aside for - the chair row already keeps out of
    place-shaped asks and now keeps out of a sleepy body too - and `entry()` takes one guard, so
    they are combined here rather than by wrapping one in a lambda at the row.
    """
    def test(understood):
        return all(bool(guard(understood)) for guard in guards if guard)
    return test


def _the_whole_line(understood):
    """The line as the person typed it, in one string, for a guard on the whole reading."""
    if not isinstance(understood, dict):
        return str(understood or "").lower()
    said = " ".join(str(understood.get(key) or "") for key in ("text", "clean"))
    if not said.strip():
        said = " ".join(understood.get("words") or ())
    return said.lower()


def entry(id, key, reply, avoid=(), bias=0, ask=(), slips=(), fault=False,
          report=False, guard=None, shape=(), explain=False, lead="", outcomes=()):
    """Build an Entry. key: words, phrases, or tuples of alternatives for one key.

    bias: a nudge when two entries fit a line equally well, for the more specific one
    (a named dish or ingredient beats a general technique). Use 1, rarely 2.
    ask: optional words or phrases that must also appear, for an entry that is only
    an answer when the line is actually asking (a factual "how many weeks in a year"
    should not fire on "I'm away for three weeks in a year", let alone on a month
    named in passing). Empty means the key alone is enough.
    slips: key words that are misspellings of another key word, not words of their own.
    A table of hard spellings has to hold "adress" next to "address", and if both count as
    words then the slip repair around them sees two near-miss neighbours in two families and
    gives up: "who do i tel about my new adress after moving" stopped reaching the address
    entry and got the shrug. A slip still matches its own entry; it is only kept out of the
    vocabulary that decides what is a word and what is a misspelling.
    report: the complaint this answer is about can be *stated* as well as asked about, so a
    line that is nothing but "i have <subject>", "ive got <subject>" or "i keep getting
    <subject>" is a request for it. Opt in only on rows where naming the complaint is the
    question (a symptom in your own body), never on a row whose subject is a thing somebody
    might own or want: "i have a dog" is not a question about looking after one.
    guard: optional `fn(understood) -> bool`; the entry answers only when it returns true.
    Use it where the reading, not a word in the line, says the key means something else.
    shape: callables given the line's words as one string, each True when the line holds a
    figure of the kind this row is about ("4%" for a phone's charge). A shape that matches is
    one signal - the same weight as a key word - so the row still needs its subject in the
    line, and a row with no shape is read exactly as before.
    lead: the sentence the row owes a line that wants one shape of answer, in the row's own words
    ("Usually, yes", "About 20 minutes"). `bot/compose/lead.py` puts it in front when the line's
    `wants` is the shape the sentence gives and the card does not already open with it; a card
    that opens with the answer, and every other shape of line, is left exactly as it is. Use it
    on a card that is written for the harder question and has the plain one to answer as well.
    explain: the row answers a named thing, so a plain request to explain it is its question:
    "what is sepsis", "tell me about gout", "explain shingles". The ask has to sit in front of
    the subject with nothing but the ask's own words between ("what is the best way to clean a
    sofa" is a request for a method, not for a sofa), and the subject counts as one signal the
    way a stated complaint does.
    """
    return Entry(id, key, reply, _avoid_words(avoid), bias, ask, slips, fault, report, guard,
                 shape, explain, lead, outcomes)


# ---------------------------------------------------------- what kinds a thing comes in
# A line that asks which families a thing comes in - "what kinds of tea are there", "what types of
# apple are there", "the different sorts of potato" - is not asking about one of them, and the rows
# that answer about one of them (brewing a cup, choosing a potato for mash) answered it or gave a
# shrug instead. The shape is the same for every subject, so it is read once here: a domain adds a
# subject as data (`kinds_entries`), and every wording below reaches it.
#
# Two parts, because the words alone cannot tell the ask from a use:
# - the kinds words, which the row needs as one of its two signals, and
# - `asks_the_kinds`, the guard that stands the row down when the line names a use as well,
#   because "what type of potato is best for mash" and "what kind of tea goes with cake" are
#   questions about the use, and the row that answers that use is the one to answer.
#
# The shape is not invented here: `bot/compose/fit.py` reads these lines as `options` and
# `bot/modules/intent.py` writes that name into `memory["understood"]["wants"]`, which is how the
# follow-up below and the rows that lean on it agree on one reading.
KINDS_WORDS = ("kinds of", "kind of", "types of", "type of", "sorts of", "sort of",
               "varieties of", "variety of", "different kinds", "different types",
               "different sorts", "different varieties")


# The name `bot/compose/fit.py` gives the ask for a menu of kinds, which `bot/modules/intent.py`
# writes into `memory["understood"]["wants"]`. Spelled here rather than imported: `bot.compose`
# imports `bot.memory`, which imports `bot.knowledge`, so an import here would close a circle at
# load time.
KINDS_SHAPE = "options"


# The words a follow-up opens on. They name no subject of their own, so pairing them with the
# subject is what says "this line is about that thing" - the same shape as ASK_ABOUT above.
KINDS_FOLLOW_UP_WORDS = ("and", "what", "how", "about", "same", "also", "then", "so")


# The words that make the line a question about a use rather than about which ones there are. "for"
# is the plainest of them, and no kinds question needs it: "what kinds of tea are there for a cold"
# is a cold question, and the row that answers colds has more to say than the list of teas.
# A line that asks the bot what it likes or does ("what kind of coffee do you like", "what sort of
# tea do you drink", "what types of coffee can you make") carries a subject and a kinds word like
# every ask above, and is still a question to the bot: the bot's own answer is the one to give, and
# the families of coffee answer a different question. The second person is what says so.
KINDS_ASKS_ME = re.compile(
    r"\b(?:do|does|would|will|did|can|could|are|were)\s+(?:you|u)\s+"
    r"(?:like|love|prefer|drink|eat|use|having|have|think|recommend|choose|watch|read|make|"
    r"order|rate|enjoy)\b")


# A line that says how things are instead of asking about them. The kinds words alone do not say
# which: "there are so many kinds of tea" carries them exactly as "the different types of potato"
# does, and the understanding lane reads both as a statement, so `kind` cannot separate them and
# neither can the kinds word. What separates them is a predicate, and a noun phrase has none: a
# subject with a copula, an auxiliary or a common doing-verb after it is the person telling the
# bot something ("there are so many kinds of tea", "we tried three different types of rice last
# week", "they stock three sorts of rice"), where the right answer is the mirror ack and not the
# families. Only the words arm needs this fence: a question has `wants == "options"`, which is the
# other arm, and a follow-up leans on that shape.
# A predicate does not make a line a statement if it is the verb of asking. "i want to know the
# types of tea", "i would like to see the different sorts of milk", "i am after a list of the kinds
# of honey" are questions with the question word left out, and the families are the answer. These
# are the verbs that want something said, and they are a short closed list: everything else with a
# subject and a verb is the person telling the bot how things are.
KINDS_ASKS_WITH_A_VERB = re.compile(
    r"\b(?:want|wants|wanted|wanna|would like|like to|need|needs|needed|wonder|wondering|"
    r"wondered|ask|asked|know|knowing|learn|find out|show|show me|tell|tell me|curious|"
    r"after|looking for|interested|thinking of|choose|choosing|pick|picking|decide|deciding|"
    r"recommend)\b")


KINDS_SAYS_HOW_IT_IS = re.compile(
    r"\b(?:i|we|you|they|he|she|it|there|people|everyone|someone|nobody|this|that|these|those|"
    r"the|my|our|his|her|their)\b(?:\s+\w+){0,3}\s+"
    r"(?:is|are|was|were|am|has|have|had|do|does|did|can|could|will|would|should|tried|try|tries|"
    r"bought|buy|buys|made|make|makes|ate|eat|eats|cooked|cooks|keep|keeps|stock|stocks|sell|"
    r"sells|sold|use|uses|used|prefer|prefers|like|likes|liked|love| loves|love|loved|hate|"
    r"hates|hated|grow|grows|grew|got|get|gets|need|needs|want|wants)\b")


KINDS_NAMED_A_USE = re.compile(
    r"\b(?:for|best|better|good|right|make|makes|making|bake|baking|cook|cooking|roast|roasting|"
    r"boil|boiling|mash|fry|frying|chips|salad|soup|sauce|crumble|pie|cakes?|bread|jam|chutney|"
    r"keep|keeps|keeping|store|storing|freeze|frozen|buy|buying|cheap|cheapest|substitute|"
    r"instead|replace|swap|goes|go|with|worth|healthy|"
    # An occasion or a destination is a use too: "what sort of wine should i bring to dinner" was
    # answered with the red, white and rose taxonomy when the person was choosing a bottle to take,
    # and the pairing row already answers that. Which families exist is a question about the thing;
    # "bring it to dinner", "take it to a party" is a question about which one to take there.
    r"bring|brings|take|takes|serve|serves|serving|dinner|lunch|supper|party|picnic|barbecue|"
    r"bbq|wedding|christmas|birthday|gift|present|occasion|hosting)\b")


def asks_the_kinds(understood):
    """True when the line asks which families a thing comes in.

    Two ways a line asks it, and both are the same shape:

    - in its own words, with a kinds word and no use named ("what kinds of tea are there",
      "the different types of potato", "what sort of apple is there");
    - leaning on the kinds question before it, which carries no kinds word of its own ("and
      rice", "what about apples"). The shape is kept in `memory["understood"]["wants"]` by
      bot/modules/intent.py, so no phrase list has to guess at it here.

    One reading, used two ways: a kinds row answers on it, and the table that answers the next step
    of a meal stands down on it (the dish follow-up answered "what types of potato are there" with
    a recipe, because the turn before it had named a food).
    """
    if not isinstance(understood, dict):
        return False
    # The line as it was typed, not the reading of it: a two-line reading carries the words of the
    # turn before ("what kinds of milk are there for coffee" then "which is easier to froth"), and
    # a row that answered on those words would answer the wrong question.
    said = str(understood.get("clean") or understood.get("text") or "")
    if said and KINDS_ASKS_ME.search(said):
        return False
    if said and not KINDS_NAMED_A_USE.search(said):
        words = " %s " % " ".join(said.lower().replace("[", " ").replace("]", " ")
                                  .replace(",", " ").replace("'", " ").split())
        # The words arm answers a noun phrase. A line that predicates something about the thing
        # is the person saying it, not asking it, and the mirror ack is the answer to that.
        lowered = " ".join(said.lower().split())
        says_it = (understood.get("intent") == "news"
                   or (understood.get("kind") != "question"
                       and not KINDS_ASKS_WITH_A_VERB.search(lowered)
                       and KINDS_SAYS_HOW_IT_IS.search(lowered)))
        if not says_it and any(kind in words for kind in KINDS_WORDS):
            return True
    # The same ask carried by a follow-up that names no kinds of its own ("and coffee", "what
    # about wine"). The shape on the turn before is what makes it one, and no phrase list has to
    # guess at it here.
    return (understood.get("wants") == KINDS_SHAPE
            and not KINDS_NAMED_A_USE.search(said)
            and not set(understood.get("asks") or ()) - {"what", "yesno"})


def kinds_entries(rows):
    """Build the `what kinds of X are there` answers for one domain.

    `rows` is data: (the line's subject words, the subject for the row's id, the answer). The
    answer opens on the families, because that is what was asked. The shape is the guard, not a
    word in the key, so a follow-up that carries the shape ("and rice") reaches the same row, and a
    line that names a use ("what type of potato is best for mash") reaches the row that answers the
    use instead.
    """
    out = []
    for subjects, name, answer in rows:
        # The ask as it is worded: a kinds word and the subject.
        out.append(entry("kinds-of-%s" % name, (KINDS_WORDS, subjects), answer,
                         guard=asks_the_kinds, bias=2))
        # The same row for a line that carries the shape and no kinds word ("and rice", "what
        # about apples"): the words that make it a follow-up, and the subject. The guard is the
        # same, and it is what keeps this row off every other line: it answers only when the shape
        # was asked, which a follow-up has in `memory["understood"]["wants"]`.
        out.append(entry("kinds-of-%s-told" % name, (KINDS_FOLLOW_UP_WORDS, subjects), answer,
                         guard=asks_the_kinds, bias=2))
    return out


# The "-'s" words that are contractions of "is" or "has", never a possessive.
_CONTRACTION = frozenset((
    "it's", "what's", "that's", "there's", "here's", "he's", "she's", "who's", "where's",
    "when's", "why's", "how's", "let's", "this's", "one's", "everyone's", "someone's",
    "nothing's", "everything's", "nobody's",
))


# Plurals that are not made by adding "s": the singular ends in -f or -fe instead. Stripping
# the "s" from these gives a different word that people use all day - "leave" from "leaves",
# "lif" from "lives" - so a key of "leaves" was answered by "leave my phone charging".
IRREGULAR_PLURALS = {
    "leaves": "leaf", "loaves": "loaf", "sheaves": "sheaf", "thieves": "thief",
    "wolves": "wolf", "shelves": "shelf", "selves": "self", "elves": "elf",
    "halves": "half", "calves": "calf", "scarves": "scarf", "wharves": "wharf",
    "hooves": "hoof", "knives": "knife", "wives": "wife", "lives": "life",
}


# A curly apostrophe is what a phone writes by default, so "isn’t eating" has to read as
# the same line as "isn't eating". Without this the word split in two ("isn", "t") and a key
# holding "isnt eating" could never match.
_CURLY = str.maketrans({"’": "'", "‘": "'", "ʼ": "'"})


_CURLY_ANY = ("’", "‘", "ʼ")


def _doubles_for_an_ending(stem):
    """True when the final doubled consonant of a stem comes from the ending, not from the word.

    "stopp" in "stopping" and "runn" in "running" are one letter short of the word, so the
    doubled "p" and "n" go and "stop"/"run" can still meet a key. "hiss", "add" and "egg"
    already are words: dropping a letter invents a different one - "hissing" was handing "his"
    to every key that said hissing, so "my dad is tired of his job" reached the puncture
    instructions, and "passed" handed "pas". A doubled "s" is always the word's own, and the
    doubling an ending makes always sits on a consonant after a vowel ("stop", "run", "plan").
    """
    if len(stem) < 4 or stem[-1] != stem[-2] or stem[-1] in "aeiou" or stem[-1] == "s":
        return False
    # a doubled "l" is a spelling variant, not a doubled consonant of the inflection:
    # "misfuelled" is "misfuel" and "travelled" is "travel", whatever comes before it
    if stem[-1] == "l":
        return True
    # a vowel then a consonant in front of the pair: "st-o-pp", "r-u-nn", "pl-a-nn". The "u"
    # of "qu" is a consonant here: "quitting" is "quit", not "quitt" left alone.
    if stem[-3] not in "aeiou":
        return False
    return _is_consonant(stem, len(stem) - 4)


def _is_consonant(word, index):
    """True for the letter at index, reading the "u" of "qu" as the consonant it sounds."""
    if index < 0:
        return False
    letter = word[index]
    if letter not in "aeiou":
        return True
    return letter == "u" and index > 0 and word[index - 1] == "q"


_FORMS_CACHE = {}


# How many words the card holds before it is cleared. A reply asks for about 10,000 of them and
# a whole conversation adds a handful at a time: six long deck conversations, 48 turns between
# them, left the card at 10,013 with 104,749 questions already answered from it. So 50,000 is
# five times what a real conversation reaches, and it is what stops a very long one from holding
# a frozenset for every word it has ever seen.
_FORMS_CACHE_KEEP = 50000


# A few "-ing" words are not their stem with an ending on it. "teething" is "teethe", and the
# "teeth" a matcher finds at the front of it is the plural noun of a different word: the card
# for caring for teeth answered "teething problems with the new puppy" with brushing steps, and
# the dentist entry answered "teething problems with the new car" with how to register with a
# practice. Only the bare stem is held back; "teething" and "teethe" still read.
# "Sugaring" is the same shape: the "sugar" at the front of it is the sweetener. The hair-removal
# card keys on "sugaring", so its "sugar" form was on that card too, and the card's own "how do i"
# topic word was the second signal it needed: "how do i cut down on sugar" and "best way to cut
# down on sugar" were answered with the shave. The card keeps "sugaring", "how to do sugaring at
# home" included; it loses only the bare stem.
# "Stuffing" is the same and the commonest of them all: "stuff" is how people say things they
# have not named ("can i make it with stuff from a corner shop", "how do i sell stuff on ebay"),
# so the stuffing recipe answered a corner-shop question with sage and onion. The row already
# stands down for the selling words; the plain "stuff" is the same slip and cannot be listed as a
# key word, because a key word is a word the line is about.
# "Evening" is the same shape and the most expensive of them: the "even" at the front of it is
# one of the commonest words in English ("even when i use it", "even though"), so a key on
# "evening" answered every line with an "even" in it. The phone-battery card never got its turn:
# "my phone keeps going flat even when i barely use it" was the bedtime-scrolling answer, and
# "my phone keeps going flat when i barely use it" was right, which is what a stray "even" costs.
NOT_THE_STEM = frozenset(("teething", "sugaring", "evening", "stuffing",
                          # "Skirting" is the same shape once more, and it cost a whole question:
                          # the "skirt" at the front of it is a cut of beef as far as the matcher
                          # could tell, so "how do i dust skirting boards" was a plain steak
                          # question - salt, acid, slice across the grain - and the skirting-board
                          # card, which keys on "skirting", never got its turn on "how do i hem a
                          # skirt" either. Only the bare stem is held back; "skirting" still reads.
                          "skirting",
                          # "Outing" is the same shape, and "out" is one of the commonest words
                          # there is: the walking row keys on "outing", so the "out" of "my
                          # sourdough keeps coming out flat" was that row's own subject, and a
                          # flat loaf was answered with a canal towpath - three separate lines
                          # ("the bread keeps coming out flat", "the loaf came out flat again").
                          # The row keeps "outing" and "outings"; it loses only the bare stem.
                          "outing",
                          # The same shape, found by auditing every "-ing" key word in the
                          # registry against the words the engine reads: each of these is a noun
                          # of its own whose stem is a *different* everyday noun, so the stem is
                          # never the row's meaning. "Weathering is rock being broken up where it
                          # sits" answered "what will the weather be like" - every wording of it,
                          # in Cornwall or anywhere else - because the weather row's key word
                          # handed the matcher "weather". "A letter from the council" reached the
                          # lettering card, and "boarding" is a plane as often as it is boards.
                          # The word itself still reads; only the bare stem is held back.
                          "weathering", "lettering", "wording", "boarding", "footing", "decking",
                          "clothing", "housing", "marketing", "banking", "accounting"))


# A word that ends in "s" whose shorter form is a different word, which no key means to meet.
# "ages" is how long it has been - "i havent cooked in ages", "its been ages since i went out" -
# and the "age" inside it is the noun for growing old, so the ageing fact answered a person who
# had not cooked for months with what happens to cells, and any row keying "age" beside "when"
# or "how old" answered them as well. Every other plural still strips: this is a list of the
# words where the strip invents a meaning, not of plurals in general.
NOT_A_WORD_WITH_AN_S = frozenset(("ages",))


# The "-ing" words whose stem plus an "e" is another everyday noun rather than the word they
# were built from. "Housing" is not "house" with an ending on it: one is what the council
# builds and the other is the thing you live in, and only one of them is this row's subject.
NOT_THE_STEM_WITH_E = frozenset(("housing",))


# The same shape as NOT_THE_STEM, but for a whole class of word rather than one at a time: a
# particle is never the base of the "-ing" word in front of it. "Outing" is a trip out, and
# "out" is not what it means, but the bare stem went onto it because the stem is not a short
# consonant-vowel-consonant shape and the only other test for it was `_bare_is_the_word`, which
# holds a list of 85 of the commonest words and "out" is not one of them. So "out" was a form
# of the easy-walk card's "outing", and it is one of the commonest words in an everyday line:
# "the cake came out flat" carried the card's own "flat" and its "out", which is the two
# signals every entry needs, and a bake that sank was answered with a canal towpath. The same
# stem reaches a phone that keeps "going" flat, a hinge that came "off", and anything a person
# says came "up".
# The verbs are left out on purpose: "go" and "work" are inside the same kind of word as
# "going" and "working", so a key on "go" has to answer a line that says "going", and the
# damage above is done by the particles, which are never the thing a sentence is about.
NOT_A_BASE = frozenset(
    "about above across after against along among around at before behind below beneath "
    "beside besides between beyond by down for from in into near of off on onto out over "
    "past since through till to toward towards under until up upon with within without".split())


# A few "-ing" words are not a verb with its ending on it, so the doubled stem is a different
# noun rather than the base they were built from. "Bedding" is the linen; "bed" is the
# furniture, or the plot in the garden. Keys that say "bedding" (bot/knowledge/cleaning.py,
# clothing.py, cars.py, the drying-outside card in home_craft.py) therefore matched every line
# with "bed" in it, and on main `7652cff82` the line of washing answered the sleep questions:
#   "my son is 14 and wont get out of bed"       -> A dry, breezy day dries a normal load...
#   "how do i get out of bed in the morning"    -> the same
#   "he keeps getting out of bed"               -> the same
#   "how often should i change my bed sheets"   -> Cover tender plants when frost is forecast
#   "how do i protect my flower beds from frost" -> A dry, breezy day dries a normal load...
# Only the doubled stem is held back, so a line that says "bedding" still reaches every one of
# those cards.
NOT_THE_DOUBLED_STEM = frozenset(("bedding",))


def _add(forms, form):
    """Keep a derived form only when it is long enough to be a word in its own right."""
    if len(form) >= MIN_FORM:
        forms.add(form)


# A question about this chat is the memory store's turn, never a fact's. The understanding layer
# carries the words of the last few lines along with the new one, so "how did we start?" after a
# chat about saving read as "how do I start saving" and a knowledge entry answered it. The check
# runs on the words the person typed, not on those the memory adds.
_CHAT_PHRASES = (
    r"how did we (?:start|begin|get started|meet)"
    r"|how did (?:this|our|the) (?:chat|conversation) (?:start|begin|go)"
    r"|(?:start|beginning) of (?:this|our|the) (?:chat|conversation)"
    r"|what did (?:i|we) (?:say|ask|tell you) (?:first|at the start|at the beginning)"
    r"|what was (?:the first thing|my first (?:question|line|message))"
    r"|first (?:thing|question|line|message) (?:i|we) (?:asked|said|sent)(?: you| him| her)?"
    r"|do you (?:remember|recall) what (?:i|we) (?:said|asked|told)(?: you)?(?: first)?"
    r"|what have we (?:talked|spoken) about"
    r"|what did we talk about"
)


# Only the chat's own words may follow: "how did we start?" is about the chat, and "how did we
# start saving for a house" is about the house.
_CHAT_TAIL = (r"(?:\s+(?:out|then|here|it|this|that|chat|conversation|talking|off|again|"
              r"everything))*\s*")


_ABOUT_THE_CHAT = re.compile(r"(?:^|\s)(?:" + _CHAT_PHRASES + r")" + _CHAT_TAIL + r"$")


def about_the_chat(own_line):
    """True when the line asks about this conversation rather than about the world.

    This runs on the words the person typed ("text"), not on the reading's words: a follow-up is
    re-read with the memory's topic words added ("how did this chat start save car"), and those
    are exactly what made a fact answer a question about the chat.
    """
    return bool(_ABOUT_THE_CHAT.search(" ".join(tokens(str(own_line or "")))))


# Words that carry grammar rather than meaning: a longer word never has one of these as its base.
_FUNCTION_WORDS = frozenset(lexicon.CORE.split())


def _cvc(stem):
    """Whether a short stem is consonant-vowel-consonant: "bit", "car", "hat", "hop".

    A short word of that shape after stripping "-ing" is nearly always a different word of its
    own ("bit" for "biting", "car" for "caring") rather than the base of the word that was
    written, so it needs a second look before it is handed out. Longer stems are left alone:
    "gardening" is "garden", and its last three letters being consonant-vowel-consonant says
    nothing.
    """
    if not 3 <= len(stem) <= 4:
        return False
    vowels = "aeiou"
    return stem[-1] not in vowels and stem[-2] in vowels and stem[-3] not in vowels


def tokens(text):
    """The loose words of a line, lower case, for matching against keys."""
    return WORD.findall(text.translate(_CURLY).lower())


# The throat-clearing in front of a hand-off: "and", "oh", "so", "sorry," before "one more thing".
_THROAT = re.compile(
    r"^(?:(?:and|oh|ooh|ok|okay|so|but|right|ah|er|um|umm|hmm|sorry|also|just|plus|hey|ta|"
    r"anyway|anyways|then|actually|well)\b[\s,:-]*)+")


# What carries a line from the hand-off to what it is about, and goes with it: "one more thing
# about the boiler" is a line about the boiler, and so is "the other thing is my back hurts".
# Only punctuation or one of these makes the lead-in an announcement: "the last thing i need is
# another bill" is one sentence and every word of it counts.
_BRIDGES = tuple(lexicon.HANDOFF_BRIDGES) + ("is", "was")


_BRIDGE = re.compile(r"^\s*(?:" + "|".join(re.escape(one) for one in
                                            sorted(_BRIDGES, key=len, reverse=True))
                     + r")\b[\s,.:;\-\u2013\u2014]*")


_PUNCTUATION = re.compile(r"^\s*[,.:;\-\u2013\u2014]+[\s,.:;\-\u2013\u2014]*")


def _past_a_handoff(clean):
    """The line after a hand-off at its front, or None when it does not open with one.

    "one more thing about the boiler" and "quick question, how do i descale a kettle" announce a
    question and then ask it. The announcement is not what the line is about: nothing in "one
    more thing" should be matched against a key, or an entry keyed on "one" and "thing" answers a
    line that was about the boiler. Only a hand-off that is followed by what it announces is
    dropped, so a bare "one more thing" keeps every word it typed and is answered by whoever
    reads the line itself (bot/compose/handoff.py).
    """
    text = _THROAT.sub("", " ".join(str(clean or "").lower().split()))
    for lead in sorted(lexicon.HANDOFF_LEADS, key=len, reverse=True):
        if not text.startswith(lead):
            continue
        rest = text[len(lead):]
        after = None
        punctuation = _PUNCTUATION.match(rest)
        if punctuation:
            after = rest[punctuation.end():]
        else:
            bridge = _BRIDGE.match(rest)
            if bridge:
                after = rest[bridge.end():]
        if after is None:
            continue  # "the last thing i need is another bill" is one sentence
        bridge = _BRIDGE.match(after)  # "one more thing, about the boiler"
        if bridge:
            after = after[bridge.end():]
        return after.strip(" ,.:;\t\u2013\u2014") or None
    return None


# A line about somebody the person looks after, and what is wrong with them: "my daughter has
# head lice", "our baby's got conjunctivitis", "my son caught chickenpox". The person is not asking
# about the child, they are asking what to do about the thing - and the card that answers it is
# keyed on the thing ("head lice", "conjunctivitis"), never on the child. Read as typed the line
# reached no entry, so the composer's line for a carer answered it: "Being the one looking after
# them is its own kind of tiring. What have you noticed so far?" while "Wet-comb the whole head
# with a fine-tooth lice comb..." was one word away.
CARER_FRAME = re.compile(
    r"^\s*(?:my|our|the)\s+(?:poor\s+|little\s+|eldest\s+|youngest\s+|old\s+|new\s+)?"
    r"(?:son|sons|daughter|daughters|child|children|kid|kids|baby|boy|girl|toddler|teen|"
    r"teenager|mum|mam|mom|mother|dad|father|wife|husband|partner|boyfriend|girlfriend|"
    r"sister|brother|niece|nephew|grandson|granddaughter|grandchild|grandchildren|"
    r"friend|mate)\s*(?:'s|s')?\s+"
    r"(?:has|have|had|got|caught|come down with|came down with|is|are|was|were|"
    r"keeps getting|came out in|is covered in|has come out in)\s+"
    r"(?:(?:an?|the|some)\s+)*", re.I)


# What makes the thing wrong with somebody an illness rather than an event: a part of the body
# (`lexicon.BODY_PARTS`), the everyday symptom, or a condition with a name. "my son has a birthday
# next week" and "my wife has a job interview" are not this, and reading them as an ask about the
# thing answered a party and an interview with a card about the thing named in them.
AN_ILLNESS = re.compile(r"\b(?:" + "|".join(sorted(lexicon.BODY_PARTS)) + r"|" + "|".join("""
ill unwell poorly sick sickness bug bugs virus infection infected cold flu fever temperature
cough coughing sneeze sneezing wheeze wheezing breath breathing rash itchy itching itch spot
spots lump lumps sore pain painful ache aching hurt hurts injury injured wound cut gash burn
scald scab bruise bruised swelling swollen stiff sprain strain break broken fracture
dislocated dizzy fainting faint vomit vomiting diarrhoea diarrhea constipation dehydrated
dehydration allergy allergic reaction hives eczema psoriasis asthma croup colic teething
chickenpox measles mumps rubella tonsillitis thrush nits lice worms threadworms ringworm
verruca verrucas wart warts boil boils abscess stye conjunctivitis earache toothache headache
migraine migraines pneumonia bronchitis covid shingles gout sciatica arthritis cystitis uti
scabies impetigo meningitis quinsy coldsore epilepsy seizure
seizures dementia alzheimers diabetes anaemia thyroid tumour leukaemia cancer stroke
""".split()) + r")(?:s|es)?\b", re.I)


def _past_the_carer(clean):
    """The thing wrong with the person they look after, or None when the line is not that shape.

    "my daughter has head lice" is a question about head lice; whoever types it wants the comb and
    the conditioner, not a word about how hard caring is. Only the words that name the child and
    the having are dropped, so a line that also says what they want - "my son has chickenpox and
    wont eat" - is read on its own remaining words like any other line. A state of somebody's life
    is not an illness and is left to the reader that knows it (`AN_ILLNESS`).
    """
    text = " ".join(str(clean or "").lower().split())
    found = CARER_FRAME.match(text)
    if not found:
        return None
    left = text[found.end():].strip(" ,.:;\t")
    words = [word.strip(_MARKS) for word in left.split() if word.strip(_MARKS)]
    if not words:
        return None
    # The thing named is the head of the phrase, so an illness word at the end of it is the thing
    # ("a bad back", "sore throat", "head lice"), and a short phrase may name it first ("a rash that
    # doesnt fade"). An illness word anywhere in a long phrase is not the thing: "my brother was
    # hanging back at the party" has "back" in it and is a party.
    if AN_ILLNESS.fullmatch(words[-1]) or (
            len(words) <= 3 and any(AN_ILLNESS.fullmatch(word) for word in words)):
        return left
    return None


# "the pub was dead quiet last night": before a describing word, "dead" says how it felt. It is
# not a symptom ("my hand has gone dead" is one), so it is not a word to match a key against -
# the numb-hands entry keyed on it answered the pub with carpal tunnel syndrome. The words after
# it stay, so a line about being tired is still about being tired. The composer reads the same
# word the same way (bot/compose/trouble.py, DEAD_AS_VERY_AFTER).
DEAD_AS_VERY_AFTER = frozenset((
    "quiet", "tired", "easy", "good", "bad", "cheap", "slow", "boring", "cheerful", "glad",
    "lucky", "proud", "keen", "jealous", "happy", "sure", "tricky", "hard", "funny", "rude",
    "straight", "wrong", "serious", "certain", "ahead", "silent", "knackered", "shattered",
    # the same idiom with the describing word after "and": "it was dead easy and dead quick" is
    # two ways of saying the same easy, so the second word has its own description in front
    # "dead" before a describing word says how much, and the composer's trouble panel was reading
    # it as a broken thing: "my trainers are dead comfy" -> "Annoying. Is it every time, or only
    # now and then?", "my new bed is dead comfortable" -> "Right. What have you tried so far?",
    # "the sofa is dead soft" -> the same panel. The adjectives people actually put it in front of:
    "comfy", "comfortable", "soft", "cosy", "cozy", "warm", "cold", "nice", "sweet", "pretty",
    "smooth", "strong", "fussy", "broke", "skint", "fun", "obvious", "scary", "gentle", "relaxed",
    "bright", "dark", "loud", "chuffed", "mint", "annoying", "embarrassing",
    "quick", "fast", "clean", "simple", "smart", "friendly", "heavy",
))


def _without_a_dead_that_only_means_very(words):
    """The line's words with a "dead" that describes the next word taken out."""
    kept = []
    for index, word in enumerate(words):
        following = words[index + 1] if index + 1 < len(words) else ""
        if (str(word).lower() == "dead"
                and str(following).lower().strip(_MARKS) in DEAD_AS_VERY_AFTER):
            continue
        kept.append(word)
    return kept


_MARKS = string.punctuation + "\u2019"


# The food nouns that make a "cooking" in front of them part of a name: "cooking oil" and
# "cooking apples" are things in a cupboard, not food that has been cooked.
COOKING_AS_A_NAME = frozenset(("oil", "oils", "apple", "apples", "chocolate", "bacon", "fat",
                               "sauce", "wine", "salt", "cream", "onions", "onion", "ham"))
