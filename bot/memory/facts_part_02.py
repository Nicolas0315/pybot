"""Part 2 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re

from ..understanding import lexicon

from .facts_part_01 import (
    AFTER_THEN, ASK_WORDS, CLAUSE_EDGE, COMING_HOME, ON_ITS_WAY_BETWEEN, NOT_THEIRS,
    NOT_THEIRS_AFTER, THEIRS_WORD, A_WISH, DIET_STOP_A_WAY_OF_EATING, DIET_WHAT, DIET_WHAT_TWO,
    DIET_DOING, DIET_QUIT, EATING_VERB, QUIT_AS_DOING, NAME_AFTER_TITLE, NOT_A_NAME, COUNTRIES,
    DAYS, JOB_WORDS, MONTHS, NOT_PLACES, NUMBER_WORDS, VAGUE_BUDGET, AFTER_A_FIGURE, AGE_IN_WORDS,
    BEFORE_A_FIGURE, NOT_YEARS_AFTER, _NUMBER_IN_WORDS, HEIGHT_BARE, HEIGHT_CM, HEIGHT_FEET,
    INCH_WORDS, AGE_UNIT, _A_TEEN_WORD, _A_TEN_WORD, _A_UNIT_WORD,
)


def _fact_value(word):
    """The thing a pattern caught, cut short where the question starts: "" when there is none.

    "what am i allergic to again" caught "again", and "nuts, what can I have?" caught "nuts,
    what can": neither is a fact. Returns the value itself otherwise.
    """
    # The value is kept exactly as it was written, separators and all: splitting on commas
    # turned "6,000 pounds" into "6 000 pounds".
    parts = re.split(r"([\s,]+)", str(word or "").strip())
    words = [parts[i] for i in range(0, len(parts), 2)]
    kept = []
    for i, value in enumerate(words):
        # "learn to swim then do a triathlon": the "do" after a joining "then" is the second
        # thing they mean to do, not the start of a question.
        if value.lower() in AFTER_THEN and i and words[i - 1].lower() == "then":
            kept.append(parts[2 * i] + (parts[2 * i + 1] if 2 * i + 1 < len(parts) else ""))
            continue
        if value.lower() in ASK_WORDS:
            # "then" mid-sentence joins two things they mean to do ("york then leeds", "learn
            # to swim then do a triathlon"), so it only ends a value when nothing follows it:
            # "my budget is 300 then" is 300.
            if value.lower() == "then" and words[i + 1:]:
                kept.append(parts[2 * i] + (parts[2 * i + 1] if 2 * i + 1 < len(parts) else ""))
                continue
            break
        kept.append(parts[2 * i] + (parts[2 * i + 1] if 2 * i + 1 < len(parts) else ""))
    out = "".join(kept).strip(" ,;:")
    if out.lower().endswith(" then"):
        out = out[:-5].rstrip(" ,;:")  # a "then" the cut left behind is not part of the fact
    return out


def _coming_home(text, start):
    """True when the animal in the line is one they are getting, not one they have."""
    window = CLAUSE_EDGE.split(text[max(0, start - 60):start])[-1]
    for cue in COMING_HOME.finditer(window):
        between = window[cue.end():]
        if not ON_ITS_WAY_BETWEEN.match(between):
            continue
        return True
    return False


def _only_wanted(text, start, end):
    """True when the animal is one they want, dislike or had once, not one they have.

    "i dont want a dog" and "i hate cats" name an animal the person does not have; "im thinking
    about getting a dog" and "i had a dog growing up" name one they may have later or had once.
    Storing either one answers "You've got a dog" to the next ask, which is the store claiming a
    pet for them, and it is also what let a take-back hand back an animal nobody mentioned.
    """
    window = CLAUSE_EDGE.split(text[max(0, start - 60):start])[-1]
    for cue in NOT_THEIRS.finditer(window):
        # "i want to train my dog" and "we are thinking about our cat" keep the animal: the
        # owner word after the want is what says it is already theirs.
        if THEIRS_WORD.search(window[cue.end():]):
            continue
        return True
    return bool(NOT_THEIRS_AFTER.match(text[end:end + 30]))


def _not_theirs(animal, text, start, end):
    """The record for an animal the person does not have, marked, and a wish marked as a wish."""
    record = {"animal": animal, "name": None, "not_theirs": True}
    if _a_wish_for(text, start):
        record["wanted"] = True
    return record


def _a_wish_for(text, start):
    """True when the animal is one they would like rather than one taken away.

    "i want a labrador", "im thinking about getting a cat" and "i might get a greyhound" all put
    no animal in the house, and none of them takes one away either. `_only_wanted` reads them
    together with "not the dog" and "forget the cat", and the modules that answer a take-back
    ("Right - no dog, then") need the two told apart.
    """
    window = CLAUSE_EDGE.split(text[max(0, start - 60):start])[-1]
    if THEIRS_WORD.search(window):
        return False
    return bool(A_WISH.search(window))


def _the_food_named(raw):
    """The food a phrase about eating names, or "" when the words are not something to eat.

    "sugar" and "red meat" are food, "work" and "the shopping" are not, and the phrase stops at
    the first filler: "dairy for a month" is the dairy. One reader for both the diet a person
    names ("im cutting out dairy") and the one they take back ("im back on dairy").
    """
    words = " ".join(str(raw or "").lower().split()).split()
    if not words:
        return ""
    two = " ".join(words[:2])
    if words[0] not in DIET_WHAT and two not in DIET_WHAT_TWO:
        return ""
    kept = []
    for word in words:
        if word in DIET_STOP_A_WAY_OF_EATING:
            break
        kept.append(word)
    return " ".join(kept)


def _a_way_of_eating_said_with_a_verb(text):
    """The way of eating a line says with a verb, as they said it, or "".

    "im cutting out dairy" -> "cutting out dairy". Only a food word behind the verb counts, so
    the shape is never read from "im off work" or "im doing the shopping".
    """
    for match in DIET_DOING.finditer(text):
        food = _the_food_named(match.group("what"))
        if not food:
            continue
        return match.group("doing").lower() + " " + food
    for match in DIET_QUIT.finditer(text):
        what = match.group("what").split()
        food = _the_food_named(" ".join(what))
        if not food and what[0] in EATING_VERB:
            # "stopped eating meat" names the meat, not the eating: the food behind the eating
            # verb is what they gave up.
            food = _the_food_named(" ".join(what[1:]))
        if not food:
            continue
        doing = match.group("doing").lower()
        return QUIT_AS_DOING.get(doing, doing) + " " + food
    return ""


def _with_title(match):
    """The name a "called"/"named" match gives, with its title kept: "Mr Whiskers", "Lady Grey"."""
    title = match.group("title")
    name = match.group("name")
    if not title:
        # A one-word name is stored exactly as it was said, as it always has been: the store is
        # not the place to change the case of what somebody called their animal.
        return name
    if name.lower() in NOT_A_NAME and name.lower() not in NAME_AFTER_TITLE:
        # The word after a title is part of the name only when it is a name word: "my cat is
        # called lady and she is 3" names the animal Lady, and "Lady And" is not a name. The
        # title alone is what the line gave, which is what the store did before titles were kept.
        return title.rstrip(".")
    # "called mr whiskers" is the same name as "called Mr Whiskers", and a two-word name is said
    # back the way a name is written.
    return (title + " " + name) if any(char.isupper() for char in title + name) else \
        " ".join(word[:1].upper() + word[1:] for word in (title + " " + name).split())


def _names_something_else(low):
    """Whether a word on its own names a thing rather than a person.

    The "im Jess" rules will read any word as a name, and the answer to "what's your name" can
    be anything at all: "london", "monday", "teacher" and "thirty" all came back as the person's
    name and then stuck ("You're Wednesday."). The lists the store already keeps decide it - the
    days, the months, the countries, a number - and the knowledge base's own city and trade
    lists for the rest, read here so a large module is only loaded when a name is being taken.
    """
    if not low:
        return True
    if (low in DAYS or low in MONTHS or low in COUNTRIES or low in NOT_PLACES
            or low in NUMBER_WORDS or low in JOB_WORDS):
        return True
    try:
        from ..knowledge import costs, travel  # noqa: PLC0415 - only when a name is on the table
        if low in travel.CITIES or low in costs.JOBS:
            return True
    except Exception:  # noqa: BLE001 - an unread list just leaves the word alone
        pass
    return False


def vague_budget(text):
    """The limit a line states with no figure in it, as the store says it back: "nothing too
    pricey" -> "not too expensive", "something cheap" -> "cheap". None when the line is not a
    limit ("the tickets were cheap" is about what they bought)."""
    match = VAGUE_BUDGET.match(text or "")
    if not match:
        return None
    said = " ".join(match.group(0).lower().split()).strip(" .,;:!")
    if "cheap" in said and said.startswith("on "):
        return "on the cheap"
    if "cheap" in said or "reasonable" in said:
        return "cheap"
    if said.startswith("budget"):
        return said
    return "not too expensive"


def _the_numbers_in_words(text):
    """The line with an age said in words written as figures, so the age readers can read it."""
    if not text or not any(word in text.lower() for word in _NUMBER_IN_WORDS):
        return text

    def figure(match):
        if not BEFORE_A_FIGURE.search(text[:match.start()]):
            return match.group(0)
        after = text[match.end():]
        if NOT_YEARS_AFTER.match(after) or not AFTER_A_FIGURE.match(after):
            return match.group(0)
        total = sum(_NUMBER_IN_WORDS.get(part, 0)
                    for part in re.split(r"[-\s]+", match.group("words").lower()))
        return str(total) if total else match.group(0)

    return AGE_IN_WORDS.sub(figure, text)


def _how_tall(text):
    """The height a line states as the words to say it back in, or "".

    Only the shapes that name a height: a bare "im 5" is not one, and the inches have to be real
    ones, so "5 foot 14" is not a reading of anything.
    """
    match = HEIGHT_CM.search(text)
    if match:
        return match.group("cm") + "cm"
    match = HEIGHT_FEET.search(text) or HEIGHT_BARE.match(text)
    if not match:
        return ""
    inches = INCH_WORDS.get((match.group("inches") or "").lower(), match.group("inches") or "")
    if inches and not inches.isdigit():
        return ""  # a word nothing counts inches in, so the line names no height
    if inches and int(inches) >= 12:
        return ""  # 14 is not inches: the figure is not a height, and 5 foot would be a guess
    return match.group("feet") + " foot" + (" " + str(int(inches)) if inches else "")


BIRTHDAY = re.compile(
    r"\bmy\s+(?:birthday|bday|dob|date of birth)\s*(?:'s|s)?\s*"
    r"(?:is|was|falls|:|=|on|in)\s+(?:on\s+)?(?:the\s+)?"
    r"([^,.;!?]{2,28})", re.I)


# The pronoun a birthday was said with, as the word the rest of the store fits to a person. The
# reader for it is with the other readers of somebody else's facts (`OTHER_BIRTHDAY`), because it
# needs the words a relation can be named by.
BIRTHDAY_PRONOUN = {"his": "he", "her": "she", "their": "they"}


# Where a date clause ends: the conjunction that starts the next person's clause ("my daughters
# birthday is in may AND MY SONS is in july"). Nothing said so, and the reader takes everything up
# to the next comma, so one date came out as "may and my sons is in jul" and the ask about the
# daughter's birthday answered with both halves in the first person.
A_DATE_CLAUSE_ENDS = re.compile(r"\s+(?:and|but|so)\s+(?=(?:my|our|his|her|their)\b)", re.I)


def _the_date_clause(date):
    """The date as far as the clause it is said in goes: "may and my sons is in july" -> "may"."""
    return A_DATE_CLAUSE_ENDS.split(str(date or ""))[0]


def _a_birthday_date(after):
    """The date words of a birthday clause, or "" when they name no date at all.

    A birthday is the one fact kept as a date, so the words after it have to look like one - a
    month or a figure - and a line that goes on about the day ("my birthday is going to be
    quiet", "my birthday is a big one this year") names no date.
    """
    date = _the_date_clause(" ".join(str(after or "").lower().split())).strip()
    date = date.rstrip(" .,;:")
    date = re.sub(r"^(?:in|on)\s+", "", date)  # "my birthday is in august" names august
    looks_like_a_date = any(word in MONTHS for word in re.split(r"[^a-z0-9]+", date)) \
        or re.search(r"\d", date)
    if not date or not looks_like_a_date:
        return ""
    if re.search(r"\b(?:to be|going|quiet|coming|soon|weekend|week|tomorrow|today)\b", date):
        return ""
    return date


# What they weigh, in the words people give it: "im 90 kilos", "i weigh 13 stone", "im 85kg".
# The unit is what tells a weight from an age ("im 34" is an age), so a bare figure is not one.
WEIGH_UNITS = {"kilo": "kilos", "kilos": "kilos", "kilogram": "kilos", "kilograms": "kilos",
               "kg": "kilos", "kgs": "kilos", "stone": "stone", "st": "stone",
               "pound": "pounds", "pounds": "pounds", "lb": "pounds", "lbs": "pounds"}


def _weight_unit(word):
    """The unit a weight was said in, however they pluralised it.

    "12 stones" is the same weight as "12 stone", and people write both; the store keeps one
    spelling for each unit, so the plural is looked up as its singular rather than listed twice.
    """
    word = str(word or "").lower()
    unit = WEIGH_UNITS.get(word)
    if unit is None and word.endswith("s"):
        unit = WEIGH_UNITS.get(word[:-1])
    return unit


# Only the present: a weight is a fact about now, so "i weighed 90 kilos last year" and "my weight
# will be 90 kilos" are not what they weigh, and storing either would have the ask say "You weigh
# 90 kilos." about a number that is not true today. A past or planned weight is left to whoever
# reads the line it is in, and the ask stays honest ("You haven't told me what you weigh.").
WEIGH = re.compile(r"\bi\s+weigh\s+(\d{2,3}(?:\.\d)?)\s*([a-z]+)\b", re.I)


WEIGH_IM = re.compile(r"\bi(?:m|'m| am)\s+(\d{2,3}(?:\.\d)?)\s*([a-z]+)\b", re.I)


# "my weight is 90 kilos" is the shape people use when they mean to be clear about it, and it is
# the same fact as "i weigh 90 kilos": read as one, or the ask that follows says they never told
# me, right after they did. The unit is what makes it a weight, as it is for the other shapes.
WEIGH_MY = re.compile(r"\bmy\s+weights?\s+(?:(?:is|are|works out at)\s+)?"
                      r"(\d{2,3}(?:\.\d)?)\s*([a-z]+)\b", re.I)


# A relation word that a noun follows is part of the noun ("my parents evening", "my mum house"):
# the line is about an evening, not the people in it. This is the handful of nouns that turn up
# there, because the word after a relation is what decides who the line is about.
COMPOUND_AFTER = frozenset("""evening wedding birthday party house home flat garden car room
meeting funeral anniversary holiday dinner tea lunch day night weekend bedtime visit health
money phone number address school work dog cat baby pram bath""".split())


# The compounds a relation can own: everything the list above has, less the one phrase that is
# an event of the school rather than a thing of the parents'.
COMPOUND_THAT_IS_THEIRS = COMPOUND_AFTER - {"evening"}


# The age said with its own name: "my age is 34", "my ages 34".
# A number with a unit after it is a measurement and not an age, the same as for anybody else:
# "my age is 68 kilos" said a weight and was filed as the age 68.
MY_AGE = re.compile(r"\bmy ages?(?:'s|\s+is|\s+just)?\s+(\d{1,2})\b"
                    r"(?!\s*(?:" + AGE_UNIT + r")\b)(?!\s*\d)", re.I)


# A word in front of a relation makes a different relation, and people say these far more often
# than the list below suggests: a stepson is not the son, and a grandson is not the son either, so
# each is kept as its own person. Built from the relations rather than listed again, so "step" and
# "grand" reach every relation a person can be. Without this the store filed "my stepmum is 40"
# under the person "stepmum" and then answered "how old is my stepmum" with a search hedge,
# because the readers on the way out were built from a narrower list than the writers.
# Only the relations that name one person: a "grandparents" or a "stepchildren" is a group the
# store keeps no age for, and reading one as a person answered "my grandparents are 80" with
# "Your grandparent is 80." - one figure for two people.
_STEP_OF = ("mum", "mom", "mother", "dad", "father", "son", "daughter", "brother", "sister")


_GRAND_OF = ("mum", "mom", "mother", "dad", "father", "son", "daughter", "child")


_BUILT_KIN = tuple(["step" + word for word in _STEP_OF]
                   + ["grand" + word for word in _GRAND_OF])


RELATIONS = ("daughter", "son", "twins", "partner", "husband", "wife", "mum", "mom", "mother",
             "dad", "father", "sister", "brother", "parents", "gran", "grandma", "grandad",
             "granny",
             "nana", "nan", "nanna", "grandmother", "grandfather", "grandpa", "aunt", "auntie",
             "aunty", "uncle", "niece",
             "nephew", "cousin", "friend", "neighbour", "neighbor", "boyfriend", "girlfriend",
             "fiance", "fiancee") + _BUILT_KIN + (
    "gran", "granddad", "stepchild")


# The relations people type short. `lexicon.CHAT` already spells them out for the understanding
# engine ("gf", "bf", "hubby", "missus", "bairn", "bubba", "m8"), and a person is the same person
# however they were said: "my gf is vegetarian" was read as the user's own diet, because the word
# "gf" named no relation to this file and the clause fell through to the "my", so the bot said
# nothing about the girlfriend and would have warned the person about a diet of their own. Read
# here, the short word is a relation everywhere this file looks for one, and it is kept as the
# full word, so "what's my girlfriend's name" still finds the name filed under "gf".
SPOKEN_RELATION = {said: full for said, full in lexicon.CHAT.items()
                   if full in RELATIONS or (full.endswith("s")
                                            and full[:-1] in RELATIONS)}


SPOKEN_RELATION = {said: (full[:-1] if full.endswith("s") and full[:-1] in RELATIONS else full)
                   for said, full in SPOKEN_RELATION.items()}


RELATIONS = RELATIONS + tuple(word for word in SPOKEN_RELATION if word not in RELATIONS)


# A person named in a line, so a bare "he died" after "my grandad was ill" is the grandad and not
# the one animal the store holds.
PEOPLE_WORD = re.compile(r"\b(?:" + "|".join(sorted(RELATIONS, key=len, reverse=True)) + r")s?\b"
                         r"|\b(?P<name>(?:my|his|her|their|our)\s+[a-z]{3,}\b)", re.I)


# "my mum is called janet", "my son is 8": the relation names which person the name or the age
# belongs to. They are theirs, not the user's, the same way "my son is allergic to nuts" is.
# A figure with a unit or a currency after it is a measurement, not how old anybody is:
# "my mum is 5 foot 4" is her height.
# The number has to end where it ends: without the bare `(?!\d)` a two-digit figure can give up a
# digit and slip past the unit, which read "my mum is 72 kilos" as age 7 and "shes 12 miles away"
# as age 1.
NOT_A_UNIT = (r"(?![\d.,]\d)(?!\d)"
              r"(?!\s*(?:foot|feet|ft|cm|centimet|inches?|inch|stone|st|kg|kilo|lbs?|lb|metres?"
              r"|meters?|miles?|mph|hours?|hrs?|mins?|minutes?|weeks?|percent|%))")


# The words a person can be to the user here: the relations, and the everyday ones people name
# in the same breath ("my nan is 81", "my flatmate is 27"). Kept local to this reader so the
# people the store keeps stay the ones RELATIONS names.
# The people in an ordinary person's life who are not family: somebody in a role, named the same
# way a relation is ("my tutor is 40", "my tutor is called mrs owens", "whats my tutors name").
# They were missing from every person list, so a name or an age said about a tutor or a childminder
# was filed nowhere and the ask about them fell to whatever card the line's other words hit. Kept
# to roles a person holds, so a word that is as often a thing (a coach, a cleaner, a trainer) stays
# out of it.
ROLE_PEOPLE = ("tutor", "childminder", "carer", "hairdresser", "barber", "instructor")


KIN = RELATIONS + (
    "nan", "gran", "granddad", "grandmother", "grandfather", "auntie", "niece", "nephew",
    "colleague", "boss", "flatmate", "housemate", "godson", "goddaughter", "manager",
    "landlord", "landlady", "lodger",
    # "my mate dave is coming over" is how half the country names a friend, and the store knew
    # nobody by it: the name was filed nowhere and "whats my mates name" was answered "I don't
    # know enough to answer that honestly". The compound words above still win, because
    # `KIN_WORDS` is taken longest first and "flatmate" is read before "mate" is tried.
    "mate") + ROLE_PEOPLE + (
    # "my girl is 7" and "my boy is 4" are how people name a child far more often than "my
    # daughter". Not a relation in RELATIONS, because that list is what the rest of the store
    # treats as a person everywhere, and a "boy" in a line is not always one.
    "girl", "boy",
    # A baby is a person the store keeps an age for, and the words people use for one are how a
    # question about them is put: "how old is the baby", "how old is our little one". They are in
    # this list so the ask names the person the age was kept under.
    "baby", "little one", "wee one")


# "my youngest is 3", "my eldest is 9": how people name one of several children, with no noun at
# all. They are a person only where no relation word follows, because "my eldest son is 8" is the
# son, and filing an "eldest" beside him makes two children of one.
# "my toddler is 18 months", "my little one is 3": a word that names one person with no
# relation after it, beside the words above. Without them the line named nobody, so the
# age was never kept, "how old is my toddler" answered a card about toddlers in general,
# and the ask back eight turns later said the chat had never been told.
ALONE_PERSON = ("youngest", "eldest", "oldest", "baby", "toddler", "newborn", "little one")


# An adjective in front of the word for a person names the same person: "my little girl is 2",
# "my eldest son is 8", "my big boy is 5". It is the commonest way people say it, and without it
# the line named nobody - the store filed nothing while the acknowledgement said "Noted: your
# eldest son is 8.", so the bot told the person it had kept the fact and then denied it a turn
# later ("You haven't told me how old your son is.").
PERSON_MODIFIER = ("little", "big", "small", "tiny", "eldest", "oldest", "youngest", "baby",
                   "middle", "older", "younger", "teenage", "grown", "first", "second", "third",
                   "fourth", "other", "poor", "darling", "littlest", "new")


MODIFIER_BEFORE = r"(?:(?:" + "|".join(PERSON_MODIFIER) + r")\s+)?"


# "in law" is the same modifier however it is typed ("my brother-in-law", "my sister in law",
# "my inlaws"), and the person it names is the in-law, not the brother: "my brother-in-law is
# called raj" filed a person called brother with no name, and the next "whats his name" was told
# "You haven't told me your brother's name." The suffix is read with the relation.
IN_LAW = r"(?:[ \t]*-?[ \t]*in[ \t]*-?[ \t]*laws?)?"


# The same phrase as a word on its own, for the readers that ask whether one word names an
# in-law ("is my brother in law a relation the store knows?").
IN_LAW_WORD = re.compile(r"^[a-z]+(?:[ \t]*-?[ \t]*in[ \t]*-?[ \t]*laws?)$", re.I)


def an_in_law(word):
    """Whether a person's word names an in-law: "brother in law", "mother-in-law", "inlaws"."""
    return bool(IN_LAW_WORD.match(str(word or "").strip()))


# The same suffix at the front of the words that follow a relation word: "brother-in-law" leaves
# "-in-law is coming" behind the match, and "sister in law" leaves " in law is coming".
IN_LAW_AFTER = re.compile(r"[ \t]*-?[ \t]*in[ \t]*-?[ \t]*laws?\b", re.I)


# Longest first: "stepmum" has to be read as one word before "mum" is tried, and the same for
# "grandson" and "son". Exported so the store asks about exactly the people it can file, which is
# what kept "my stepmum is 40" answerable but "how old is my stepmum" a shrug.
KIN_WORDS = tuple(sorted(set(KIN), key=len, reverse=True))


_RELATION_WORDS = "(?:" + "|".join(KIN_WORDS) + ")" + IN_LAW


# The word a person can be named by with no noun after it, for the readers that can tell the
# two apart: "my youngest is 3" is somebody, and the "eldest" in "my eldest son is 8" is not.
_A_PERSON = "(?:" + _RELATION_WORDS + "|" + "|".join(ALONE_PERSON) + ")"


# Every word that can be a person, and every adjective that can stand in front of one: neither is
# a name, so neither can be read as the name of the person the line just named.
_A_WORD_FOR_A_PERSON = frozenset(KIN) | frozenset(ALONE_PERSON) | frozenset(PERSON_MODIFIER)


# A title in front of a name belongs with it. "my landlord is called mr patel" was read as a
# person called "Mr", and "my mum is called mrs smith" the same, because the name was one word
# and the title is one word. The title takes the word after it, however it is punctuated.
# Longest first: "mr" would take the first two letters of "mrs" and leave the s behind.
TITLE = r"(?:professor|miss|mrs|mr|ms|dr|sir|prof|dame|lord|lady|rev|capt|sgt)\.?"


# A title on its own names nobody, so it is not a name: "my sister is called mr smith" is Mr
# Smith, and the store must never answer "Your sister is called Mr." The other readers ("my
# sister is called ...") are built from `_NAME` as well, so none of them can file the title alone
# as the name while the next one files the whole of it - which is how the store came to hold two
# people called "mr" and "Mr smith" and to answer "how old is your landlord" with "Your landlord
# is called Mr".
TITLE_WORDS = frozenset(re.findall(r"[a-z]+", TITLE))


# A title is the one thing that says whether a person is a he or a she: "my landlord is called
# mr smith" then "whats his name" is Mr Smith, and "whats her name" is not answered as his.
TITLE_GENDER = {"mr": "he", "sir": "he", "lord": "he", "mrs": "she", "ms": "she", "miss": "she",
                "lady": "she", "dame": "she"}


_NAME = (r"(?P<name>" + TITLE + r"(?:\s+[A-Za-z][A-Za-z'\-]{1,19})?"
         r"|[A-Za-z][A-Za-z'\-]{1,19})")


# The naming verb is only read as one when the line has already said it is talking about the
# person: "my mum is called janet", "my mums called janet". Without that, "called" and "named"
# are the line's own verbs and the word after them is not a name at all - "my mum called me
# yesterday" and "my sister named her baby after me" would file a person called Me and a person
# called Her, and the store would say them back.
RELATION_NAME = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r")(?:\s+is\s+|'s\s+|s\s+)"
    r"(?:called|named)\s+" + _NAME, re.I)


# The same fact said with "have": "i have a son called jack", "we've got a daughter named amy".
# Every relation pattern above needs the possessive, so this shape kept the person and dropped
# the name: the bot answered "Noted: you have a son called jack." and then, asked, said "You
# haven't told me your son's name." With "have a" in front, "called" is unambiguously the naming
# verb - the line has already said the person exists - so no further guard is needed.
RELATION_HAVE_NAME = re.compile(
    r"\b(?:i|we)\s*(?:'ve|ve|have|got)(?:\s+got)?\s+"
    r"(?:an?\s+|one\s+|two\s+|three\s+)?"
    r"(?P<who>" + _RELATION_WORDS + r")s?\s+(?:called|named)\s+" + _NAME, re.I)


# "my mum's name is janet", "my brothers name is tom": the same fact said the other way round.
RELATION_POSSESSIVE_NAME = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r")(?:'s|s)?\s+name\s+(?:is\s+)?"
    + _NAME, re.I)


# "my brother tom is 12", "my friend sarah is 40": the name sits between the relation and the
# age, so one line gives the store both.
# The word between the person and the age is their name, so it is not another word for a person:
# "my eldest son is 8" is the son at eight, and read the other way it files an "eldest" beside him.
_NOT_A_PERSON_NAME = r"(?!(?:" + "|".join(sorted(_A_WORD_FOR_A_PERSON, key=len, reverse=True)) + r")\b)"


RELATION_NAMED_AGE = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r")\s+"
    r"(?P<name>" + _NOT_A_PERSON_NAME + r"[A-Za-z][A-Za-z'-]{1,19})"
    r"\s+(?:is|'s|was)\s+(?P<age>\d{1,3})" + NOT_A_UNIT, re.I)


# The age given as the thing asked about rather than as a figure after the person: "my mums age is
# 68", "my sons age is 7". The word between the person and the figure is the fact being given, so
# it is that person's age; read as a name it filed "Age" against them and lost the age the line
# gave, and the store then said "Your son is called Age."
RELATION_POSSESSIVE_AGE = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r")s?'?s?\s+ages?\s+"
    r"(?:is|was|'s)\s+(?P<age>\d{1,3})" + NOT_A_UNIT, re.I)


# The age said as the birthday coming: "my son is turning 7", "my daughter is turning 5 on friday".
# The verb between the person and the figure meant nothing was kept - the store held no age, the
# present asked for next turn was a punt, and "how old is he" answered "You haven't told me".
RELATION_AGE = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r")(?:\s+is\s+|'s\s+|s\s+|\s+)?"
    r"(?:turning\s+|turns\s+)?(?P<age>\d{1,3})" + NOT_A_UNIT, re.I)


# "the eldest is 7", "the little one is 4": a child named by their place in the family takes the
# definite article as readily as a possessive. It is how the second of two children is said - "our
# youngest is 4 and the eldest is 7" - and read with the possessive only, the second age was filed
# against nobody, so the ask about that child ("how old is the eldest") fell through to the world
# and came back as advice about something else. The article says "mine" here because the place
# word is the whole of the noun phrase: "the eldest son" is the son, and that shape is left alone.
THE_PLACE_AGE = re.compile(
    r"\bthe\s+(?P<who>" + "|".join(sorted(ALONE_PERSON, key=len, reverse=True)) + r")"
    r"(?:\s+is\s+|'s\s+|s\s+)(?P<age>\d{1,3})" + NOT_A_UNIT, re.I)


# A baby is somebody people give an age for with no relation word in the line: "my baby is 4
# months old", "the baby is 18 months". The readers above need a word like "son" or "daughter",
# so the age was filed nowhere and the store said a turn later that it had never been told.
BABY_AGE = re.compile(
    r"\b(?:my|our|the)\s+(?:(?P<who>baby)|(?P<little>little\s+one|wee\s+one)|newborn|tot)"
    r"\s+(?:is|'s|was|are)\s+"
    r"(?P<age>\d{1,3})(?![\d.,]\d)(?!\d)\s*(?P<unit>months?|years?)\b"
    r"(?!\s*(?:away|ago|later|early|behind|off))", re.I)


# The age as the name of the baby: "our 7 month old", "my 18 month old is crawling". The figure
# sits inside the phrase that names the person, so no reader above - all of which want "is" after
# the person - found it, and the age the line gave away was filed nowhere.
MONTH_OLD_BABY = re.compile(
    r"\b(?:my|our|the)\s+(?P<age>\d{1,2})(?![\d.,]\d)(?!\d)\s*(?:months?)\s+old\b"
    r"(?!\s*(?:away|ago|later|early|behind|off))"
    # The phrase has to name a person, and "old" is what a thing is too: "our 7 month old labrador
    # needs walks", "my 6 month old phone keeps dying", "our 9 month old puppy is chewing". So the
    # phrase must end the clause or be followed by a verb or a word for the person - never by
    # another noun, which is the thing being described.
    r"(?=\s*(?:[,.;!?]|$|\s+(?:is|was|are|were|has|have|had|keeps|needs|wakes|sleeps|who|that|and|"
    r"but|eats|walks|loves|will|can|does|did|goes|cries|feeds|naps|sits|crawls|started|still|now|"
    r"baby|boy|girl|son|daughter|child|little one|wee one)\b))", re.I)


# The name given without the naming verb: "my mum is sue", "my son is tom". A word after "is" is
# an adjective far more often than a name ("my mum is tired", "my brother is older"), so the word
# has to look like a name and not like the state it would otherwise be - see `_bare_name`.
RELATION_BARE_NAME = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r")(?:\s+is\s+|'s\s+|s\s+)"
    r"(?P<name>[A-Za-z][A-Za-z'-]{1,19})\b", re.I)


# Two people given one after the other: "my mum and dad are dave and sue". The line names two
# people and two names and no more, so the pair is kept whole rather than split by guesswork.
RELATION_PAIR_NAMES = re.compile(
    r"\b(?:my|our)\s+(?P<who1>" + _RELATION_WORDS + r")\s+and\s+(?P<who2>" + _RELATION_WORDS
    + r")\s+(?:are|were)\s+(?P<name1>[A-Za-z][A-Za-z'-]{1,19})\s+and\s+"
    r"(?P<name2>[A-Za-z][A-Za-z'-]{1,19})\b", re.I)


# A group given its names in one breath: "my kids are called jack and emma", "my son and
# daughter are called jack and emma". The pair reader above takes the line with no naming verb
# ("my mum and dad are dave and sue"), and a group word ("kids", "children") is not a relation
# at all, so this line was answered "Got it" and the two names were never kept.
GROUP_NAMED_NAMES = re.compile(
    r"\b(?:my|our)\s+(?P<who>" + _RELATION_WORDS + r"|kids?|children)"
    r"(?:\s+and\s+(?P<who2>" + _RELATION_WORDS + r"))?\s+(?:are|were)\s+(?:called|named)\s+"
    r"(?P<rest>[A-Za-z][A-Za-z'-]{1,19}(?:\s*(?:,|and)\s*[A-Za-z][A-Za-z'-]{1,19}){1,3})\b",
    re.I)


# The same pair shape with an age on each: "my kids are ada 7 and sam 4". A group of people is
# the only relation this reads, because one person is never two name-and-age pairs.
GROUP_NAMED_AGES = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<who>" + _A_PERSON + r"|kids?|children|child)\s+(?:are|were)\s+"
    r"(?P<rest>[a-z][a-z'-]{1,19}\s+\d{1,3}(?:\s*(?:,|and)\s*[a-z][a-z'-]{1,19}\s+\d{1,3}){1,3})",
    re.I)


# The person named with a clause about them: "its for my daughter whos 9", "my son, who is 7,
# starts school in september". The "who" belongs to the person named before it, so the number
# after it is their age exactly as "my daughter is 9" is: without this the age was dropped and
# "how old is my daughter" said she had never told.
RELATION_WHOS_AGE = re.compile(
    r"\b(?:my|our)\s+(?P<who>" + _RELATION_WORDS + r")\s*,?\s+who(?:['\u2019]?s)?\s+"
    r"(?:is\s+)?(?P<age>\d{1,3})\b" + NOT_A_UNIT, re.I)


# A relation of a relation: "my partner's mum is 68", "my sisters husband is 41", "my mums friend
# julie is 70". The person is the pair, not the first word, and the store filed it as neither: the
# line was read as two people with no age, so the reply said "Noted: your partner's mum is 68." and
# then, asked, "You haven't told me how old your partner is" - the wrong person's age. The pair is
# kept as one person, in the words the line used ("partner's mum"), and the ask that names the same
# pair finds it.
CHAINED_RELATION_AGE = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<first>" + _A_PERSON + r")"
    r"(?:'s|\u2019s|s)\s+(?P<second>" + _A_PERSON + r")"
    r"(?:\s+(?P<name>(?!(?:is|was|'s)\b)[A-Za-z][A-Za-z'-]{1,19}))?"
    r"\s*(?:'s|\u2019s|is|was)\s+(?P<age>\d{1,3})" + NOT_A_UNIT, re.I)


# The same pair named by an ask rather than given an age: "how old is my partner's mum", "and my
# sisters husband?". The pair is the person, so the age filed against "partner's mum" is found by
# the question that names her the same way.
CHAINED_PERSON = re.compile(
    r"\b(?:my|our)\s+" + MODIFIER_BEFORE + r"(?P<first>" + _A_PERSON + r")"
    r"(?:'s|\u2019s|s)\s+(?P<second>" + _A_PERSON + r")\b", re.I)


def a_chained_person(text):
    """"partner's mum" for "my partners mum", or "" when the line names no pair of people."""
    found = CHAINED_PERSON.search(str(text or ""))
    if not found:
        return ""
    first = re.sub(r"(?:'s|\u2019s|s)$", "", found.group("first").lower())
    return first + "'s " + found.group("second").lower()


# "my mum is called janet and she is 72": after the relation is named, a pronoun is that person.
# "they" is here too: "theyre 12" is somebody's age said the way people type it, and the reply is
# the same kind of reply as "shes 12".
# The figure of a pronoun's age as people write it: a digit, or the word for it, with the way an
# approximate age is said in front ("hes about five years old", "shes nearly seven"). "hes five"
# was read as nothing at all while "hes 5" was read as the son's age, so a person who spelled the
# number out - which is most people, most of the time - was told "You haven't told me how old your
# son is" about a line that had just said it.
# The words that put an age in the future rather than now: "next month", "in june", "on friday".
# Written once so a reader that keeps the age they have now can stand aside for the one that keeps
# a birthday, instead of taking the figure and losing the day it was said with.
AGE_TO_COME_TAIL = (r"(?!\s+(?:next\s+(?:week|month|year|spring|summer|autumn|winter)|"
                    r"(?:in|on)\s+[a-z]{3,9})\b)")


# How the person feels about it is a thing they told you, and it outranks the figure:
# "shes turning 40 and she hates being the centre of attention" is a line about a sister, and
# reading the 40 as a fact to file turned a warm reply into a receipt for it. This is a check
# rather than part of the pattern below because it only applies to an age said with the word
# that says it is coming: "shes 70 and she hates fuss" is a fact with an aside, and the aside
# has always been echoed back to the person, which is the reply that line wants.
HOW_THEY_FEEL = re.compile(r"\b(?:hate|hates|hated|hating|love|loves|loved|likes?|liked"
                           r"|wants?|wanted|prefers?|dreads?|shy|embarrassed|nervous"
                           r"|excited|proud|rather)\b", re.I)


_AN_AGE_IN_WORDS = ("(?:" + _A_TEN_WORD + r"(?:[-\s]" + _A_UNIT_WORD + r")?|"
                    + _A_TEEN_WORD + "|" + _A_UNIT_WORD + ")")


PRONOUN_AGE = re.compile(r"\b(?P<who>she|he|they)(?:'s|s|re|'re)?(?:\s+(?:is|are))?"
                         r"(?:\s+(?:about|around|nearly|almost|roughly|maybe|probably|just|only"
                         r"|now|already|still))*\s+"
                         # The word that says the age is coming, which the relation readers have
                         # always taken: "my daughter is turning 6" was read and "shes turning 6"
                         # was not, so the age the chat had just been given was filed nowhere and
                         # the next ask was a punt. Same words, same reading, whoever they are
                         # said of.
                         r"(?P<come>turning\s+|turns\s+|will\s+be\s+|is\s+going\s+to\s+be\s+)?"
                         r"(?P<age>\d{1,3}|" + _AN_AGE_IN_WORDS + r")" + NOT_A_UNIT
                         # A birthday still to come is `AGE_TO_COME`'s: "hes turning 9 in june"
                         # is the age he is not yet, and reading it here as the age he is now
                         # replaced the 8 the chat had been told with the 9.
                         + AGE_TO_COME_TAIL, re.I)


def a_stated_number(word):
    """The number a person wrote as a word or a digit, or None when it says no number at all."""
    said = str(word or "").strip().lower()
    if not said:
        return None
    if said.isdigit():
        return int(said)
    total = sum(_NUMBER_IN_WORDS.get(part, 0) for part in re.split(r"[-\s]+", said))
    return total or None


def a_person_word(word):
    """A person's word said plainly: "brother in law" and "brother-in-law" are one person.

    The store keeps one entry per person, and the pronoun that fits her is one word: "my
    brother-in-law" and "my brother in law" are the same brother in law, said two ways.
    """
    plain = " ".join(re.sub(r"[ \t]*-[ \t]*", " ", str(word or "").strip().lower()).split())
    # "my mother in laws name" is the same person as "my mother in law": the plural of the
    # suffix is how the possessive gets typed, and one person is filed under one word.
    return re.sub(r"\bin laws$", "in law", plain)


def _the_person(found, who, name=""):
    """The entry for one person, when the word for the relation can be more than one of them.

    "my son jack is 6 and my son sam is 9" is two sons, so the word "son" alone does not say
    which of them an age belongs to: the name in the clause does. A fact with no name of its own
    ("he is 9", "my son is 9") still goes on the person the chat just named, so an entry with no
    name is a match for anything.
    """
    who = a_person_word(who)
    for one in found:
        if one.get("who") != who:
            continue
        if name and one.get("name") and str(one["name"]).lower() != str(name).lower():
            continue
        return one
    return None


# Who a bare "she" or "he" most likely is, so "my mum is coming sunday" then "she doesnt eat
# meat" is the mum's diet and not a stray fact about nobody. The person a relation names is
# spelled the way the store files them ("brother in law", no hyphen).
_SHE_SAID = frozenset("""mum mom mother daughter sister wife grandma granny nana nan grandmother aunt
niece girlfriend fiancee partner friend neighbour neighbor colleague girl boss manager landlord
landlady cousin flatmate housemate roommate lodger mate""".split())


_HE_SAID = frozenset("""dad father son brother husband grandpa grandad grandfather uncle nephew
boyfriend fiance partner friend neighbour neighbor colleague boy boss manager landlord landlady
cousin flatmate housemate roommate lodger mate""".split())


def _kin_pronoun(word):
    """The relation inside a step- or grand-word, so the pronoun it takes can be read from it."""
    for prefix in ("step", "grand"):
        if word.startswith(prefix) and word[len(prefix):] in _SHE_SAID | _HE_SAID:
            return word[len(prefix):]
    return word


# A word in front of a relation does not change whose pronoun it takes: a stepmum is a she and a
# grandson is a he. Without this a person the store can file could not be pointed at with "she"
# or "he", so "my stepmum is 40" then "how old is she" found no mother.
# An in-law is the relation they are an in-law of, said with the suffix: "my sister-in-law"
# and "my sister in law" are one person, and a pronoun has to be able to point at her.
SHE = (_SHE_SAID | frozenset(word for word in _BUILT_KIN if _kin_pronoun(word) in _SHE_SAID)
       | frozenset(("gran", "sister in law", "mother in law", "daughter in law",
                    "sister in laws", "mother in laws")))


HE = (_HE_SAID | frozenset(word for word in _BUILT_KIN if _kin_pronoun(word) in _HE_SAID)
      | frozenset(("brother in law", "father in law", "son in law",
                   "brother in laws", "father in laws")))


def _sided(word):
    """The pronoun a word for a person names from inside it: "she", "he", or "" for neither.

    Read from the word rather than listed again: a goddaughter is a daughter and a nanna a nan, so
    the relation a longer word is built from decides it, where the words written out by hand above
    only ever knew the ones somebody had thought of. A word that names no gender of its own gets
    nothing, because these sets are also what a reply reads to say "her" or "him": a stepchild
    given both would be called "her" by a bot that should have said "them".
    """
    inside = _kin_pronoun(word)
    for gendered in sorted(_SHE_SAID | _HE_SAID, key=len, reverse=True):
        if inside.startswith(gendered) or inside.endswith(gendered):
            return "she" if gendered in _SHE_SAID else "he"
    return ""


# A person the store can file is a person a pronoun can point at. The two lists above were written
# by hand, so a word the store files and neither list holds could be told about and never referred
# to: "my auntie is a hairdresser" then "what does she do" found nobody and fell to a search hedge,
# where the same two lines about a sister were answered, and "my nanna is 71" then "how old is she"
# asked the search instead of saying 71. Every word whose own relation has a pronoun takes it now,
# so a relation added to the list of people is pointed at without a second list to remember.
_UNPOINTED = frozenset(word for word in KIN if word not in SHE and word not in HE)


SHE = SHE | frozenset(word for word in _UNPOINTED if _sided(word) == "she")


HE = HE | frozenset(word for word in _UNPOINTED if _sided(word) == "he")


# A limit on what a plan can be - "nothing too tiring", "no long walks", "my sister cant walk
# far", "we need to keep it cheap" - is a constraint, not a plan and not a feeling: the person is
# saying what to leave out. The plan reader below files "keep it cheap" as a plan (it came back as
# "You are going to Keep it cheap next weekend") and the correction reader takes "no long walks"
# as one, so the line is read here first and neither is kept from it.
A_LIMIT = re.compile(
    r"\b(?:nothing|no|not|never|nowt)\s+(?:too\s+|very\s+|much\s+|any\s+)?"
    r"(?P<move>tiring|strenuous|energetic|demanding|exhausting|exhaustive|walking|walk|walks|"
    r"long walks?|hikes?|hiking|hills?|stairs?|standing|climbing|lifting)\b"
    r"|\b(?:can'?t|cannot|can not|isn'?t able to|is not able to|not able to|only manage)\s+"
    r"(?:walk|climb|manage)\s+(?:far|long|much)\b"
    # "she cant do stairs" and "she cant get up the stairs" are the same limit as "she cant walk
    # far", said with the thing rather than with the walking. The verb is what stands between
    # "can't" and the limit, so it is the verb that is allowed to be there, not any word: "i cant
    # do this" and "i cant do monday" name no limit. Airing this here rather than in the abilities
    # reader means the plan and the mood both read it, and "i cant do stairs" on its own is a
    # remark about their knee, which the pools that answer a body already own.
    r"|\b(?:can'?t|cannot|can not|isn'?t able to|is not able to|not able to|only manage)\s+"
    r"(do|manage|get\s+up|get\s+up\s+and\s+down|get\s+up\s+the|use|cope\s+with)\s+"
    r"(?:the\s+|a\s+|any\s+)?(?:more\s+)?(?:stairs?|steps?|hills?|walks?|walking|"
    r"climbing|standing)\b"
    # "i cant stand long" is the standing, and "i cant stand much more of this" is a feeling:
    # the word after "stand" decides, so "much" is not allowed on its own.
    r"|\b(?:can'?t|cannot|can not|isn'?t able to|is not able to|not able to|only manage)\s+"
    r"(?:stand|sit)\s+(?:for\s+)?(?:long|far)\b"
    r"|\b(?:keep (?:it|the cost|costs) (?:cheap|low|small)|on a (?:tight )?budget)\b"
    r"|\b(?:nothing|no|not)\s+(?:too\s+)?(?:expensive|pricey|fancy)\b", re.I)


# A plan the person has committed to ("im going to", "we are booking"), as opposed to one they
# say they want or need: "im going to keep it cheap this month" is a month planned, while "we need
# to keep it cheap" is only the limit.
COMMITS_TO = re.compile(
    r"\b(?:going to|planning to|off to|about to|booking|booked|saving up|i(?:'?ve| have) booked)\b",
    re.I)


# What the limit is on, which is what decides what the reply does with it: the money, or the rest.
MONEY_LIMIT = re.compile(r"\b(?:cheap|budget|expensive|pricey|fancy|cost|costs|money|low)\b", re.I)


def _own_body_is_the_trouble(clean):
    """True when the line is the speaker's own body complaining, read by the pool that owns it.

    `bot/compose/badnews.py` already has the reading ("my knee hurts", "i have a bad back", and
    not "she has a bad chest"), so it is asked rather than a second list kept here. Imported
    inside the call because badnews is a composer module and the store is read before it exists.
    """
    try:
        from ..compose.badnews import reads_like_a_symptom
    except Exception:
        return False
    try:
        return bool(reads_like_a_symptom(clean))
    except Exception:
        return False


def a_limit_on_the_plan(text):
    """The limit a line puts on a plan - the feet, the money, or some other thing to avoid.

    "nothing too tiring", "no long walks", "my sister cant walk far", "we need to keep it
    cheap": the person is saying what to leave out of the plan, never how they are. The reading
    is here because the plan reader would otherwise file one as a plan, and the mood readers ask
    it too, so it has to be one reading both can ask. None when the line puts no limit on anything.
    """
    if not isinstance(text, str):
        return None
    clean = " ".join(text.lower().split())
    if not clean or "?" in clean:
        return None
    match = A_LIMIT.search(clean)
    if match is None:
        return None
    if _own_body_is_the_trouble(clean):
        # A limit whose reason is the person's own body is a symptom with a consequence, and the
        # answer they need is the one for the back or the knee: "my back is bad so no long walks"
        # came back as "Nothing I put to you needs hours on your feet", which tells them nothing
        # about the back they just mentioned. A body that is somebody else's is still a limit -
        # "my sister cant walk far" is what a carer is saying about the trip.
        return None
    hit = match.group(0)
    if match.group("move") or re.search(
            r"\b(?:walk|stand|sit|climb|climbing|manage|stairs?|steps?|hills?|walking|standing)\b",
            hit):
        # "my sister cant walk far" is a limit on the walking too, and "she cant do stairs" is
        # the same limit said with the thing rather than with the walking.
        return "move"
    return "money" if MONEY_LIMIT.search(hit) else "other"


# a plan or intention: the line says what the user is going to do
PLAN = re.compile(r"\b(?:(?:i(?:'m| am)|we(?:'re| are)|im|were)\s+(?:going to|planning|thinking of|off to|"
                  r"about to|hoping to|trying to|aiming to|aim to|meaning to|learning to|"
                  r"working on|writing|training|moving|"
                  r"buying|looking for|starting|organising|organizing|preparing|building|making|"
                  r"booking|saving|decorating|redecorating|painting|renovating|tiling|plastering|"
                  r"sorting|packing|cleaning|planting|digging|sewing|knitting|baking|cooking)(?: up| out| around| through)?|"
                  r"i want to|i need to|we want to|"
                  # "ive" is how a plan gets typed without the apostrophe, and it is a plan all
                  # the same: "ive got to paint the fence this weekend".
                  r"we need to|i(?:'?ve| have) got|i(?:'?ve| have) just got)\b", re.I)


PARTICLES = frozenset("""up out around through off""".split())


# A particle belongs to the verb, not to the plan: "i'm saving up for a bike" is saving, up, then
# for a bike. Without a place for it the line read as no plan at all and the person got the stock
# line back; PLAN takes it and the plan keeps it.
# The frames that are always followed by a verb rather than a place, so the word after them is
# the doing: "i'm aiming to get fit" is a plan about getting fit, and "get" opens it as a verb
# even though "get" is a place word in "i'm going to get the bus". Without this the aim was read
# as a destination and dropped, and the aim's own follow-up ("how long will it take") then had no
# subject but the deadline the aim named.
INFINITIVE_FRAME = re.compile(r"\b(?:trying|aiming|hoping|planning|meaning|learning|want|need)"
                              r"\s+to\s*$", re.I)


# The words people put in front of a plan verb: "i'm saving", "we are moving", "i want to save".
PERSON_OPEN = re.compile(r"^(?:i(?:'m| am)|we(?:'re| are)|im|were|i want to|i need to|we want to|"
                         r"we need to|i(?:'ve| have) got|i(?:'ve| have) just got)\s+", re.I)


# A plan whose rest opens with a preposition has lost its verb: "for a bike" says what the money
# is for, and reads back as "You're planning to for a bike". The verb is the plan there.
PREPOSITIONS = frozenset("for to in on at with about into by from".split())


# And an object that only points at something is no object at all: "saving up for it" and
# "saving up for the one i saw" name nothing to keep, and said back they tell the person nothing
# about their own week.
POINTING = frozenset("""it them that this these those one ones nobody nothing anything
something everything anyone someone none""".split())


# A date written the way people write dates: a day and a month next to each other, with or
# without the ordinal ("14 march", "3 june", "the 4th of may"). The two readers below both want
# it, and neither knew it: the plan reader took "on friday" and "in august" but not "on 3 june",
# so "my driving test is on 14 march" kept nothing at all, and the appointment reader wanted a
# clock, so "the scan is on 3 june" was a thing with no date on it.
MONTH_NAMES = (r"(?:january|february|march|april|may|june|july|august|september|october|november|"
               r"december)")


# Grouped, because it is dropped into two longer patterns: without the bracket the last way of
# writing a date would escape the word in front of it ("on" a date, "june 3" anywhere at all).
DAY_AND_MONTH = ("(?:" + r"\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?" + MONTH_NAMES +
                 r"|(?:the\s+)?\d{1,2}(?:st|nd|rd|th)\s+of\s+" + MONTH_NAMES +
                 r"|" + MONTH_NAMES + r"\s+\d{1,2}(?:st|nd|rd|th)?" + ")")


# A correction names the value that was wrong, and the old one too when it is handy: "sorry, I
# meant Florence, not Rome", "no I mean Bristol", "sorry, Bristol not Leeds", "no, Bristol".
# "mean" and "meant" are the same move, and people drop the "I" as often as not.
# "make that" is the same move only when it is the move the line makes: at the front, after at
# most a word or two that opens a correction ("ok", "actually", "sorry", "no"). In the middle of
# a sentence it is ordinary English - "we make that recipe a lot", "i make that mistake" - and
# reading it as a correction put "Recipe a lot in june" in the plan and dropped the trip.
# A correction usually comes with the reason it changed: "sorry, i meant 900 because the boiler
# went", "no, bristol, since i moved for work". The reason names no value, so it is said around
# the value like the apology words are; left on it, the value read as "900 because the boiler
# went", which is not a value any reader here takes, so the 1500 stayed on record.
CORRECTION_WHY = r"\s*,?\s*(?:because|cos|coz|cuz|'cause|since)\b[^.!?]*"


# "sorry, Bristol not Leeds": the two values side by side, with no verb to say which is which.
# Either value can be two words ("tree nuts", "hard boiled"), and people put "it's" in front of
# the pair: "sorry, it's tree nuts not peanuts" is one correction, not a statement. A date or a
# count arrives this way as often as a name does ("sorry, the 12th not the 5th"), so a digit is a
# value too and the "the" in front of it is part of the way it is said.
# "rather than" and "instead of" take a value back in the same shape, and people say them
# without a subject: "im an accountant" / "actually an engineer rather than an accountant" was
# left with the accountant, because the pair reader knew only "not" as the word between the two
# values.
TAKES_BACK_THE_VALUE = r"(?:not|rather\s+than|instead\s+of)"


# A time that has been moved is the same correction in the words people use for it: "i got it
# moved to thursday" after "my interview is on tuesday" is Tuesday being taken back, and the
# store has the plan to put Thursday in. The thing that moved is one they have already told us
# about, so the shape needs a pointing object ("got it moved", "changed it to") or a passive
# with the thing as its subject ("it's been moved") - without one, "we moved to preston" is a
# new address and not a correction of anything.
MOVED_VERB = (r"(?:moved|changed|pushed|shifted|switched|bumped|rescheduled|rearranged|"
              r"brought|put|shoved|dragged)")


MOVED_TO = r"\s*(?:back|forward|ahead|earlier|later|round|on)?\s*(?:to|until|till|for)\s+"


# A clock time, as a plan says it: "2pm", "8.30", "20:30", "7 o'clock", "noon". A plan can
# have its clock put right the way it has its day put right - "the meeting is at 10am" then
# "make it 2pm" - and the two were not read the same way. A figure inside a plan was replaced by
# word boundary (`\b10\b`), which does not find the 10 in "10am", so the store answered "Meeting
# at 10am - got it" over a plan it had not changed; and "sorry, its at 8pm" was not read as a
# correction at all. The clock is read on its own so both have somewhere to go.
CLOCK_SAID = (r"(?:\d{1,2}(?:[:.][0-5]\d)?\s*(?:am|pm|a\.m\.|p\.m\.)"
              r"|(?:[01]?\d|2[0-3]):[0-5]\d"
              r"|\d{1,2}\s*o'?\s*clock"
              r"|noon|midday|midnight)")


# A date as a moved plan names it: a month or a weekday on its own, "the 4th", "the 4th of june",
# "12 june". One fragment so every shape that carries a moved date accepts the same dates.
A_DATE_VALUE = (r"((?:the\s+)?\d{1,2}(?:st|nd|rd|th)?(?:\s+of\s+(?:the\s+)?[a-z]{3,10})?"
                r"|(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?\s+[a-z]{3,10}"
                r"|the\s+[a-z]{3,10}"
                r"|[a-z]{3,10})")


# The words a person puts after the value they are putting right: "sorry, the 5th actually",
# "no, june then", "make it july, i think". The marker in front is what says the line is a
# correction, and people say a second one after the value as often as before it. It stopped the
# value being read at all, so the correction turn moved nothing and the ask after it gave the old
# date back ("my sons birthday is on 4 june" / "its the 5th actually" still said 4 June), and
# `a_date_put_right` said yes while `the_date_put_right` found no date in the line.
AFTER_THE_VALUE = (r"(?:\s+(?:actually|instead|then|though|sorry|please|i\s+think|"
                   r"i\s+reckon|if\s+thats\s+ok|if\s+that'?s\s+ok))*\s*[.!]?\s*$")


# The person taking back the name they gave the bot: "im not kay", "my names not kay", "thats
# not my name", "dont call me kay". None of these names anybody new, so the store kept the old
# name and went on using it - the next turn called them by the name they had just said was wrong
# - and the reply had nothing of its own at all ("I'm listening - say more if it helps", "Got it
# - that's not your name").
#
# Every shape here denies the name rather than giving one, and the word is read only against the
# name on record: "im not hungry" and "im not sure" are the commonest openings of any line, and
# a denial of the name cannot be about a word the person never gave. "dont call me kay" is the
# same denial said as an instruction, and it is why the naming word is listed on its own: the
# line is not a phone call to be refused.
# A name said in a denial is a whole name as often as one word: "im not kay smith" takes back
# the name the store holds, and reading only the first word left the line with nothing at all.
_A_SAID_NAME = r"[a-z][a-z'\-]{1,19}(?:\s+[a-z][a-z'\-]{1,19})?"


def _the_same_name(left, right):
    """Whether a word names the same person as a name on record: "kay" is "Kay Smith"."""
    said = " ".join(str(left or "").lower().replace(".", " ").split())
    known = " ".join(str(right or "").lower().replace(".", " ").split())
    if not said or not known:
        return False
    return said == known or said in known.split() or known in said.split()


# "no, Bristol": a bare value after a "no" that starts the line, once the line before it said a
# fact. Only a value on its own counts, so "no, i'm tired" is not a correction. A figure comes with
# what it is counted in ("sorry, 88 kilos"), because that is how a weight, a height or a price is
# said back, and the unit is what tells the weight from the age.
# People stack the words that announce a correction: "no sorry croatia", "oh no, bristol",
# "sorry no, soya", "no wait 600". One word was all this read, so "no sorry croatia" was not a
# correction and the value went into the store with the idiom still on the front of it. "ok" only
# opens a correction in front of one of those words: "ok wait 600" takes something back and
# "ok 600" is an answer, so it leads without carrying the value on its own.
# People also stall before they correct: "no wait, Leeds", "hold on, Porto", "sorry, hang on,
# June". The stall says nothing about the value, so it is an opener like the "no" it follows.
# A value can be two words: the thing people correct to is often not one ("tree nuts", "new
# york", "hard boiled"), and the clause guards below still refuse a phrase that is a sentence
# ("no, i'm tired" opens with "i'm").
CORRECTION_STALL = r"(?:hold\s+on|hold\s+up|hang\s+on)"


# A stock apology or an acknowledgement is not a value: "sorry, my mistake", "sorry, my bad",
# "sorry, thank you". A possessive opens a phrase that names something of the person's ("my
# mistake", "my bus") and not a new value for the fact the line before stated, and with the value
# widened to two words it was read as one ("sorry, my mistake" made the city "My").
NOT_A_VALUE_START = (r"(?!\s*(?:my|your|his|her|our|their|its|thank|thanks|cheers|please"
                     r"|and|but|so|not|nothing|never|no|ok|okay|right|yes|yeah|why|what|how)\b)")


# The hedges belong in the run too: "hmm sorry croatia", "well actually 800" and "um no bristol"
# announce a correction in the same breath as the words above, and a run of them is still one run.
CORRECTION_HEDGE = r"(?:hmm|um+|erm+|well)"
