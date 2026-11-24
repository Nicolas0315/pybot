"""Part 5 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re


from .filler import TAIL_OFF
from .facts_part_01 import (
    COUNTRY_ARTICLE, GROWN_ARTICLE, GROWN_NEAR, GROWN_NOT_PLACE, PLACE_MIDDLE, COUNTRY_CAPS,
    HOME_STOP, NOT_PLACES, PLACE_VERBS, _an_everyday_word, FROM_GROWN, FROM_PLACE, FROM_MORE,
    HOME_DWELL, HOME_PLACE, PLACE_AFTER, PLACE_LOWER, PLACE_LOWER_NAMED, SHORT_LIST, ONE_MORE_FOODS,
    ALLERGEN_PLURALS, ONE_MORE_HEAD, ONE_MORE_TAIL, DENIAL_WORDS, CLAUSE_EDGE, PETS, GIVEN_AWAY,
    HEDGE, NOT_HAVE_LONGER, NOT_JUST, WITHOUT_ANIMAL, A_COMPOUND_AFTER, HAVE_NONE, BARE_NO,
    NO_THEN_A_THING, TAKEN_BACK_BEFORE, A_CORRECTION, A_NEGATOR_IN_BETWEEN, THEIR_BACK,
    PLURAL_PRONOUN, ANIMAL_DEATH,
)
from .facts_part_02 import (
    RELATIONS, MODIFIER_BEFORE, PEOPLE_WORD,
)
from .facts_part_03 import (
    a_moved_time, DETERMINERS, FUTURE,
)
from .facts_part_04 import (
    MOVED_PLACE_PASSIVE, MOVED_PLACE_TO, NOT_A_PLACE_NAME, _a_date, CAR_ASKED, I_DRIVE, MEASURED,
    NOT_A_CAR, TONE_TAIL, _car_named_in_passing, _finish, TAKES_ONE_BACK,
)


def grown_up_in_a_place(phrase):
    """True when what follows "grew up in" names a place, so "care" and "a council estate" do not.

    The ack side reads the same phrase ("i grew up in care" must not come back as *Care - what's
    it like there?*), so the reading is shared rather than written twice.
    """
    return _grown_up_in_a_place(phrase, "")


def _grown_up_in_a_place(phrase, text):
    """True when what follows "grew up in" is the name of a place and not a way of growing up."""
    words = str(phrase or "").split()
    if not words:
        return False
    low = [word.lower().strip(".,!?;:'\"") for word in words]
    if any(word in GROWN_NOT_PLACE for word in low):
        return False
    near = GROWN_NEAR.search(str(phrase or ""))
    if near and _place_name(near.group(1)):
        return True
    if low[0] in GROWN_ARTICLE:
        return False
    # "i grew up in the Philippines", "we grew up in the UK": the country keeps its article.
    if low[0] == "the":
        return len(low) > 1 and low[1] in COUNTRY_ARTICLE
    return True


def a_moved_place(text):
    """The place a line moves a plan to: "no we changed it to devon" -> "Devon", else "".

    A plan's destination is put right the way its date is ("we moved it to july"), so the line is
    a correction of the plan the store already holds and not a place of its own. Whether the words
    name a place is the module's own question, asked of the same reader that reads a place said
    out loud, so "we changed it to a cottage" and "i changed it to the other one" name nothing
    here either. A question is not a change, and a date is the date reader's.
    """
    line = str(text or "")
    if not line or "?" in line:
        return ""
    for pattern in (MOVED_PLACE_TO, MOVED_PLACE_PASSIVE):
        for found in pattern.finditer(line):
            places, _home, _said = _places("we are going to " + found.group(1))
            for place in places:
                if _a_date(place) or a_moved_time(place):
                    continue
                if place.lower() in NOT_A_PLACE_NAME:
                    continue
                return place
    return ""


def place_value(phrase):
    """The place a corrected value names, or "" when the value is not a place at all.

    One word is a place ("leeds", "porto"). Two words only when the first is a naming word
    ("new york", "saint malo"): a place fact is what the last line stated, and "tree nuts" is a
    food, not a city, however much the line before was about where the person lives.
    """
    words = str(phrase or "").split()
    if len(words) > 1 and words[0].lower() not in PLACE_MIDDLE:
        return ""
    return _place_name(phrase)


def _car(text):
    """The car a line says they drive, or None when the verb is not about a car."""
    if CAR_ASKED.search(text):
        return None
    for match in I_DRIVE.finditer(text):
        phrase = _finish(match.group("what"))
        article = (match.group("art") or "").strip().lower()
        for tail in TONE_TAIL:
            if phrase.endswith(" " + tail):
                phrase = phrase[: -len(tail)].strip()
        words = phrase.split()
        # "i drive a 2015 golf": a year in front of the model is how people with an older car say
        # it, so the year is dropped and the model kept. A number on its own is a distance or an
        # amount ("i drive 200 miles a week") and names no car.
        while words and words[0].isdigit():
            words = words[1:]
        phrase = " ".join(words)
        if not words:
            continue
        if any(word in NOT_A_CAR for word in words) or words[-1] in MEASURED:
            continue
        if not article and words[-1].endswith("s"):
            # "i drive trains", "i drive lorries": what they drive for a living, not their car.
            continue
        return phrase
    return _car_named_in_passing(text)


# The naming words that are also ordinary adjectives: "new" names a place only in front of a
# word that is a name and nothing else, so "new heights" and "new job" are not places.
ADJECTIVE_NAMING = frozenset("new".split())


def _reads_as_a_plural(name_word, first):
    """Whether the word after a naming word is the plural of something, so not part of a name.

    "new heights", "old ways": the noun after an adjective that also starts place names is a heap
    of something rather than a name. The places it must not cost are the ones said in the
    singular ("new york"), which is the trade this makes: a lower-case "new orleans" is read as
    no place at all rather than as a heap of orleans.
    """
    word = str(name_word or "").lower()
    return first in ADJECTIVE_NAMING and word.endswith("s") and not word.endswith("ss")


# A word that says how something is is not the name of somewhere to go. "im going to rome in
# may" / "actually its fine" was read as a place called Fine: the store held the trip as "Fine in
# may" and "where am i going" answered "Fine." A place can be named after an ordinary word, but
# not after a comment on the thing itself.
NOT_A_PLACE_WORD = frozenset("""fine good great ok okay alright lovely rubbish awful terrible
brilliant perfect amazing wonderful horrible disgusting cancelled canceled booked sorted done
shut closed busy quiet cheap expensive pointless useless worthwhile""".split())


def _place_name(phrase):
    """The name a place phrase really names, in title case, or "".

    A two-word place ends at the first word that is not part of a name: "leeds and work in
    york" is Leeds, "preston last year" is Preston, "staying in tonight" is nothing at all.
    """
    words = str(phrase or "").replace("-", " - ").split()
    # "i live in the uk": a country keeps its article, but "the city centre" is no place, and
    # "the US" is not the pronoun HOME_STOP knows.
    the = ""
    if len(words) > 1 and words[0].lower() == "the" and words[1].lower() in COUNTRY_ARTICLE:
        the, words = "the ", words[1:]
    kept = []
    for i, word in enumerate(words):
        if the:
            kept.append(word)
            break
        low = word.lower()
        # "new york", "saint malo": a naming word that reads as an ordinary word on its own.
        if i == 0 and len(words) > 1 and low in PLACE_MIDDLE:
            # "im going to port my number": a naming word with a determiner after it is the
            # language's own word, not a place ("port my number", "new the way").
            if words[1].lower() in DETERMINERS:
                return ""
            if _an_everyday_word(words[1]) or _reads_as_a_plural(words[1], low):
                return ""  # "im moving to new job in may" is a job, not a place
            kept.append(word)
            continue
        if (low in HOME_STOP or low in NOT_PLACES or low in PLACE_VERBS or low.endswith("ly")
                or low in TAKES_ONE_BACK or low in NOT_A_PLACE_WORD or word == "-"):
            break
        kept.append(word)
    if not kept:
        return ""
    if len(kept) == 1 and kept[0].lower() in PLACE_MIDDLE:
        # A naming word on its own names nothing: "im going to port my number" is the verb, and
        # base filed it as a place called Port and then said "You're going to Port your number."
        return ""
    name = " ".join(kept)
    if len(kept) == 1 and name.lower() in COUNTRY_CAPS:
        return the + COUNTRY_CAPS[name.lower()]
    return the + " ".join(w[:1].upper() + w[1:] if w.islower() else w for w in name.split())


def _born_place(text):
    """The place they were born, when the line says it, or None.

    Only the person's own birth counts, so "my husband was born in cork" is his. A birth place is
    kept apart from where they are from: "i was born in lagos but i grew up in ibadan" is from
    Ibadan and born in Lagos, and both questions have an answer.
    """
    born = []
    for pattern in (FROM_PLACE, FROM_GROWN):
        for match in pattern.finditer(text):
            if not re.search(r"\bborn\b", match.group(0), re.I):
                continue
            name = _place_name(match.group(1))
            if name:
                born.append((match.start(), name))
    return max(born)[1] if born else None


# A move names two places: the one they went to and the one they came from. "i moved to preston
# from bolton last year" said both, and the origin was kept as nothing - the older patterns want
# the person in front of "from" ("im from leeds"), and here the subject is at the front of the
# line with the destination between it and the word. So the move verb is the cue: whatever "from"
# names after it is where they came from.
FROM_A_MOVE = re.compile(
    r"\b(?:moved|moves|moving|relocated|relocating|relocate|migrated)\b[^.;!?]{0,40}?"
    r"\bfrom\s+([A-Za-z][A-Za-z'-]{1,}(?:[ -][A-Za-z][A-Za-z'-]{1,})?)\b", re.I)


# The same move typed the other way round - origin first, destination second. "i moved from leeds
# to bristol" named Bristol as plainly as the other order names Preston, and only the origin was
# kept: "where do i live" answered "You haven't told me where you live - I know you're from Leeds."
A_MOVE_FROM_THEN_TO = re.compile(
    r"\b(?:moved|moves|moving|relocated|relocating|relocate|migrated)\s+from\s+"
    r"[A-Za-z][A-Za-z'-]{1,}(?:[ -][A-Za-z][A-Za-z'-]{1,})?\s+"
    r"(?:to|into)\s+"
    r"(?P<place>[A-Za-z][A-Za-z'-]{1,}(?:[ -][A-Za-z][A-Za-z'-]{1,})?)\b", re.I)


def _the_person_moved(before):
    """True when the clause in front of a move verb has the person themselves as its subject."""
    clause = re.split(r"[.;!?,]|\band\b|\bbut\b|\bso\b", str(before or ""))[-1]
    return bool(re.match(r"\s*(?:i|im|i'm|ive|i've|id|we|were|we're|weve|we've|we'd)\b",
                         clause, re.I))


def _from_place(text):
    """The place they say they are from, when the line says where that is.

    What they say about where they are from beats where they were born, and the last of those
    wins, because that is the one the person settled on: "im from leeds, originally from
    bradford though" is Bradford, and "i was born in lagos but i grew up in ibadan" is Ibadan.
    Only the person's own history counts, so "my mum grew up in kerala" names nothing about them.
    """
    born = []
    said = []
    for pattern in (FROM_PLACE, FROM_MORE, FROM_GROWN, FROM_A_MOVE):
        for match in pattern.finditer(text):
            if pattern is FROM_A_MOVE and not _the_person_moved(text[:match.start()]):
                # "my cousin moved to preston from bolton" is where her family is from, not
                # where they are from: the move has to be the person's own.
                continue
            phrase = match.group(1)
            if pattern is FROM_GROWN and not _grown_up_in_a_place(phrase, text):
                continue
            name = _place_name(phrase)
            if not name:
                continue
            if re.search(r"\bborn\s+in\b", match.group(0), re.I):
                born.append((match.start(), name))
            else:
                said.append((match.start(), name))
    if said:  # where they say they are from, or grew up, is the answer; being born is only a hint
        return max(said)[1]
    if not born:
        return None
    return max(born)[1]


# A home they live in beside another place is said with the home in front of it: "i live in a
# small village near york". York is the place that answered "where do i live" before, and it is
# not where they live; the village is. The home is kept in the words they said it in - "You live
# in a small village near York" reads right - so the place they gave is neither denied ("You
# haven't told me where you live") nor named as somewhere it is not ("You live in York").
A_HOME_BEFORE = re.compile(
    r"\b(?:a|an|the|my|our|their|his|her|this|that)\s+[a-z][a-z'-]*"
    r"(?:\s+[a-z][a-z'-]*){0,2}\s+(?:near|outside|round|close to|next to|by)\s+$", re.I)


def _places(text):
    """Places the line named, and the one they live in if it says where that is."""
    places = []
    home = None
    home_said = ""
    # The place named behind a dwelling is the place they live, so it is read first: "we live in a
    # flat in manchester" is Manchester and not the flat.
    for pattern in (HOME_DWELL, HOME_PLACE):
        for match in pattern.finditer(text):
            # A two-word place ends at the first word that is not part of a name: "leeds and work
            # in york" is Leeds, "preston last year" is Preston, "staying in tonight" is nothing.
            word = _place_name(match.group("place"))
            if not word:
                continue
            if not any(word.lower() == p.lower() for p in places):
                places.append(word)
            # A stay is a visit, and a move with a date still to come is not where they live yet:
            # both name a place without being home ("we're moving to york next month").
            ahead = match.group("planned") and FUTURE.search(text)
            if home is None and not match.group("stay") and not ahead:
                home = word
                # "i live in a small village near york" is a village near York, and the place is
                # what they said it with: the home is kept as "a small village near York".
                said_with = A_HOME_BEFORE.search(text[:match.start("place")])
                if said_with:
                    home_said = " ".join(said_with.group(0).split()) + " " + word
            break
        if home:
            break
    if home is None:
        for match in A_MOVE_FROM_THEN_TO.finditer(text):
            if not _the_person_moved(text[:match.start()]):
                continue
            word = _place_name(match.group("place"))
            if not word:
                continue
            if not any(word.lower() == p.lower() for p in places):
                places.append(word)
            # "we're moving from york to bristol next month" is a move still to come, so the
            # destination is a place they named and not where they live yet.
            if not FUTURE.search(text):
                home = word
            break
    for match in PLACE_AFTER.finditer(text):
        word = match.group(1)
        first = word.split()[0].lower()
        if first in NOT_PLACES or word.lower() in NOT_PLACES:
            continue
        # A capital is no proof on its own when the word is also one of the language's: "going to
        # Port my number" was filed as a place called Port, and the store then said "You're going
        # to Port your number." The same reader and the same guard as one typed in lower case.
        if first in PLACE_MIDDLE:
            pair = " ".join(text[match.start(1):].split()[:2])
            word = _place_name(pair)
            if not word:
                continue
        if word not in places:
            places.append(word)
    for match in PLACE_LOWER_NAMED.finditer(text):
        if _an_everyday_word(match.group(2)):
            continue  # "great lengths", "new heights": the second word is not part of a name
        word = _place_name(match.group(1) + " " + match.group(2))
        if word and not any(word.lower() == p.lower() for p in places):
            places.append(word)
    for match in PLACE_LOWER.finditer(text):
        word = _finish(match.group(1))
        low = word.lower()
        if not word or low in NOT_PLACES or low in PLACE_VERBS:
            continue
        if low in PLACE_MIDDLE:
            continue  # "going to port" and "off to saint" name no place until the name follows
        if word[:1].isupper() and word in places:
            continue
        # "im going to sri lanka in june" is Sri Lanka and not Sri as well: the first word of a
        # name is not a place of its own once the name is on the list.
        if any(p.lower().startswith(low + " ") for p in places):
            continue
        if not any(word.lower() == p.lower() for p in places):
            places.append(word[:1].upper() + word[1:])
    if not places and SHORT_LIST.match(text.strip()):
        for word in re.findall(r"[A-Z][a-z]+", text):
            if word.lower() not in NOT_PLACES and word not in places:
                places.append(word)
    return places, home, home_said


# How much of a thing there is, where a diet record would want which thing: see NO_MEAT below.
_QUANTITY_WORDS = frozenset("""enough much many any more less too little lots plenty loads
loads""".split())


ALLERGY_STOP = frozenset("""i we he she they it you have has had got also but so because
which and the a an my our his her their anything something everything much many most
lot food stuff no not few several some any real bad serious""".split())


# A relation or a flatmate: "my son is allergic to nuts" is a fact about the son, not the user.
OTHER_NOUNS = ("son", "daughter", "child", "children", "kid", "baby", "girl", "boy",
               "youngest", "eldest", "oldest", "husband", "wife",
               "partner",
               "boyfriend", "girlfriend", "fiance", "fiancee", "mum", "mom", "mother",
               "stepmum", "stepdad", "dad", "father", "sister", "brother", "friend",
               "mate", "colleague", "coworker", "boss", "flatmate", "housemate",
               "nephew", "niece", "grandma", "grandad", "granny", "nana", "grandpa",
               "aunt", "uncle", "cousin", "neighbour", "neighbor", "dog", "cat", "pet")


# A relation the bot already knows by name is somebody else, and this list has to know every one
# of them: "nan", "gran", "grandmother" and "grandson" are in RELATIONS and were missing here,
# so "my nan is allergic to nuts" named no relation at all and the allergy was filed as the
# user's own - the bot then warned the person about an allergy they never said they had, and the
# nan's went in the bin. The relations are added rather than retyped, so a relation added to the
# vocabulary is somebody else everywhere at once. Longest first, so "mother in law" is read as
# the two words it is before the "mother" inside it.
OTHER_NOUNS = OTHER_NOUNS + tuple(sorted((word for word in RELATIONS
                                          if word not in OTHER_NOUNS), key=len, reverse=True)) \
    + ("twin",)


CLAUSE_BREAK = re.compile(r"[.!?;]|\b(?:but|so|because|which|although|though|while)\b", re.I)


# A yes/no question puts the verb in front of the person: "is she vegan", "am i allergic to nuts",
# "do i live in leeds". The word order is the whole test - a statement never opens on the verb, so
# "my mum is vegan, is that a problem?" still says what it says.
QUESTION_OPEN = re.compile(
    r"^(?:(?:and|but|so|then|also|oh|ok|okay|well|now|hey|sorry|please|quick|hi)\s+)*"
    r"(?:is|isnt|are|arent|was|wasnt|were|werent|am|do|dont|does|doesnt|did|didnt|has|hasnt|"
    r"have|havent|had|can|cant|could|couldnt|would|wouldnt|will|wont|shall|should|shouldnt)\b",
    re.I)


# The clauses a line runs on into; a fact stated after one of these is a statement even when the
# line opened with a question ("can i eat nuts if im allergic to peanuts" states the allergy).
CLAUSE_JOIN = re.compile(r"\b(?:if|because|since|though|although|when|whenever|and|but|so)\b|[,;]",
                         re.I)


def stated_not_asked(text):
    """The part of a yes/no question that states something, or "" when it only asks.

    A question about somebody states nothing about them, and the readers below file what they
    find as a fact about that person: "is she vegan" after "my mum is called ann" filed a vegan
    diet against the mum and the store then answered the question as if it were a fact ("Your mum
    is vegan."). The ask is dropped and only the clauses that state something are read.
    """
    said = " ".join(str(text or "").strip().split())
    if not said or not QUESTION_OPEN.match(said):
        return said
    kept = [part.strip(" ,.;:!?") for part in CLAUSE_JOIN.split(said)]
    kept = [part for part in kept if part and not QUESTION_OPEN.match(part)]
    return ", ".join(kept)


# The pronoun a clause is about, read the same way `SUBJECT` reads it, for a clause that names no
# relation at all: "she is 70 next month" is somebody's birthday and the line never says whose.
PRONOUN_SUBJECT = re.compile(r"\b(?P<pron>he|she|they|him|them|hes|shes|theyre|her)\b", re.I)


# Every way a clause can name its subject; the last one before the fact is the one that owns it.
SUBJECT = re.compile(
    # The plural belongs to the whole list, not to its last word: written inside the group
    # ("...|kid|pet)s?") the "s?" only ever matched "pets", so "my sons" and "my mums" matched
    # no person at all and the clause fell through to the "my" below - the son's allergy was
    # filed as the user's own.
    r"\b(?:my|our|his|her|their|the)\s+" + MODIFIER_BEFORE + r"(?P<rel>"
    + "|".join(OTHER_NOUNS) + r")"
    # "my mother in law", "our brothers in law": the two words after the relation are part of
    # who this is. Cut to "mother", every reply said "Your mother is vegetarian" about someone
    # the person had just called their mother in law. The plural belongs to the whole phrase:
    # "my sons" and "my mums" are a person each, so the "s?" sits after the "in law".
    r"(?P<inlaw>\s+in\s+laws?)?s?\b"
    # People type the pronoun with the apostrophe left off, and "shes"/"hes" is not the
    # word "she"/"he" to a word boundary: without these the clause named no subject and the
    # fact fell to the user - "shes allergic to nuts" was filed as the user's own allergy.
    r"|\b(?P<pron>he|she|they|him|them|his|their|hes|shes|theyre|theyve)\b"
    r"|\b(?P<her>her)\b"
    r"|\b(?P<user>i'm|im|i am|i've|ive|i|me|mine|my|my own|we're|we are|we've|we|us|our)\b",
    re.I)


# The person is one of the people the clause is about: "me and my husband", "my wife and i",
# "us and the kids". The relation alone would file the thing against somebody else.
A_ME_WITH_SOMEONE = re.compile(
    r"\b(?:me|us|we|i)\b[^.!?]{0,24}\b(?:and|,|&)\b[^.!?]{0,24}\b(?:my|our)\s+\w+"
    r"|\b(?:my|our)\s+\w+[^.!?]{0,24}\b(?:and|,|&)\b[^.!?]{0,12}\b(?:me|us|i)\b", re.I)


def _the_person_is_in_it(clause):
    """Whether the clause says the thing is about the person as well as somebody else."""
    return bool(A_ME_WITH_SOMEONE.search(clause))


# The person a clause names without the "my" in front of them, or by name alone: "mum is
# allergic to shellfish" is the mum's allergy and "tom is allergic to nuts" is Tom's, and both
# were filed as the user's own, so the store told the person about an allergy they never said they
# had, and the mum's or Tom's went in the bin. The word has to be the last thing before the fact,
# which is where a subject stands, and a bare name has to be the whole clause, so a line about a
# thing ("the boiler is broken") is not read as somebody called Boiler.
BARE_RELATION = re.compile(
    r"\b(?P<rel>" + "|".join(sorted(OTHER_NOUNS, key=len, reverse=True)) + r")"
    r"(?P<inlaw>\s+in\s+laws?)?s?$", re.I)


# Words that fill the place in front of a fact without naming anybody: the softeners people open
# a line with, and the grammar words a subject is never made of.
NOT_A_PERSON_WORD = frozenset("""
and but so then also oh ok okay well now anyway actually quick just plus hey hi sorry right yeah yes
today tonight tomorrow yesterday here there this that these those it its he she they them their his
her him i im ive me my mine we us our ours you your yours who what which the a an some any no not
dont doesnt didnt is are was were be been am do does did have has had can could would should will
shall may might must of to for from in on at by with about time day week month year morning
evening night thing things something anything nothing everything someone anyone everyone nobody
help thanks please get got go going come coming done""".split())


# The words between a person and the fact said of them: "mum is", "tom has", "sarah cant". The
# clause the readers hand over ends at the fact, so what is left in front of it is the person once
# these are taken off the end.
BETWEEN_PERSON_AND_FACT = frozenset("""
is are was were be been being am has have had isnt arent wasnt werent hasnt havent hadnt
s does do did doesnt dont didnt can cant cannot could couldnt may might must shall should
shouldnt will wont would wouldnt get gets got become becomes became
""".split())


# The words in front of a person that mean the clause is not naming them the bare way: "the
# boiler is broken" has "the" in it and no person, and neither does "my son is 4".
NOT_A_BARE_PERSON_AHEAD = frozenset("""
my our his her their your its the a an this that these those some any every no each
""".split())


# A pronoun with its verb written on is not a name: "i'm allergic to nuts" is the person typing
# and "shes got a nut allergy" is the woman they were talking about, and read as names the two
# lines lost the fact and filed it on somebody called Im and somebody called Shes.
A_PRONOUN_NOT_A_NAME = frozenset("""
im ive id ill ima youve youre youd youll hes shes its itd its were weve wed well theyre theyve
theyd theyll thats whats theres heres isnt arent wasnt werent hasnt havent hadnt doesnt dont didnt
cant couldnt wouldnt shouldnt wont mustnt aint lets
""".split())


def _a_person_word(word):
    """A word the way a person says it, so "i'm", "im" and "I’m" are one word."""
    return str(word or "").strip().strip(".,!?;:\"'").lower().replace("\u2019", "'").replace("'", "")


# Words that end the sentence rather than name a thing: "I'm allergic to nuts, please don't put
# them in the pasta" is an allergy to nuts, and "remind me what I'm allergic to, please" states
# nothing at all.
# The chat-speak at the end of a line is the same set the recall drops (`filler.TAIL_OFF`, which
# is the leaf module so nothing here has to import the store). "im allergic to nuts tbh" is an
# allergy to nuts, and saying "you told me you're allergic to nuts tbh" back puts their shrug in
# the fact; "tho", "ngl" and "innit" do the same to a diet or an allergen.
FILLER_TAIL = frozenset(TAIL_OFF | frozenset("""please again then now though either too also
still yet anyway plus thanks thank sorry ok okay""".split()))


# The tail of a sentence that is about how much rather than about what: "i cant eat dairy at
# all" is dairy, and "i cant eat gluten anymore" is gluten. Two words on their own are not a thing
# anybody is allergic to.
FILLER_TAIL_PHRASES = ("at all", "any more", "anymore", "these days", "whatsoever", "at least",
                       "any longer", "no more", "for years", "since i was little")


def _trim_filler(text):
    words = text.split()
    while True:
        while words and words[-1].strip(".,!?;:'\"").lower() in FILLER_TAIL:
            words.pop()
        tail = " ".join(words[-3:]).strip(".,!?;:'\"").lower()
        cut = next((phrase for phrase in FILLER_TAIL_PHRASES
                    if tail.endswith(phrase)), None)
        if not cut:
            break
        words = " ".join(words).strip(".,!?;:'\"")[:-len(cut)].split()
    return " ".join(words)


# The ask at the end of a line names no allergy: "I'm allergic to peanuts and soya, what can I
# have?" is an allergy to peanuts and soya. A piece that starts with a question word ends the
# list, and so does the piece after it.
QUESTION_START = re.compile(r"^(?:what|which|who|how|when|where|why|can|could|should|would|"
                            r"will|shall|do|does|did|is|are|was|were|any|if)\b")


# What follows "cant eat" without naming a food: "he cant eat at all", "she cant eat much for
# breakfast", "they cant eat properly yet". The allergy reader is right that there is a limit in
# the line, but the words are not one, so nothing is filed and nothing is said back - "Your son
# can't eat at all, good to know" is a sick child answered with a diet.
NOT_A_FOOD = frozenset("""much many more anything everything nothing something all at properly
enough food stuff lot any now yet still anymore here there""".split())


# The generic noun people put after the food they mean: "i cant eat spicy food", "no fried stuff
# for me", "she cant eat dairy things". The word itself says nothing about what they cannot eat,
# so on its own it is not a food ("i cant eat food" names nothing); after a word that does say
# what, the modifier is the food and the noun is how they said it.
A_GENERIC_FOOD = frozenset("""food foods stuff things thing""".split())


def _trim_time_tail(item):
    """The food off the front of a time: "chilli after 6" is chilli, "dairy before work" dairy."""
    words = item.split()
    while len(words) > 1:
        last = words[-1].strip(".,!?;:'\"")
        if last in NOT_A_FOOD_IN_IT or last.isdigit() or last in ("the", "a", "my", "our"):
            words.pop()
        else:
            break
    return " ".join(words)


# A limit can be about when or where someone eats, and then there is no food in the line:
# "i cant eat late at night", "i cant eat before work", "i cant eat at my desk". The allergy
# reader took the words after "cant eat" for the thing, filed "late at night" as an allergy and
# said it back - "You can't eat late at night, good to know" - which is a timing question
# answered as a diet, and it took the turn from the food-timing card that answered it.
NOT_A_FOOD_IN_IT = frozenset("""at in on before after during while when whenever until till
    by from around late early night nights morning mornings afternoon evenings evening
    midnight lunchtime bedtime work school desk shift commute""".split())


def _a_modifier_before_a_generic_noun(words):
    """Whether the thing said is a word that names it plus a generic noun: "spicy food"."""
    if len(words) < 2:
        return False
    if words[-1].strip(".,!?;:'\"").lower() not in A_GENERIC_FOOD:
        return False
    return not set(words[:-1]) & ALLERGY_STOP


def _only_stop_words(item):
    """Whether every word of a piece is one the allergy reader knows is not an allergen."""
    words = item.split()
    return bool(words) and all(word in NOT_A_FOOD or word in ALLERGY_STOP for word in words)


def _allergy_items(chunk):
    """The things in "nuts and shellfish, not peanuts": ["nuts", "shellfish"].

    A "not" in the phrase is a correction, not another allergen: "im allergic to soya not
    peanuts" is soya, and the peanuts it names are the thing being taken back (see `denials`).
    """
    items = []
    chunk = re.split(r"\bnot\b|\b(?:but|so|because|which)\b", chunk)[0]
    for item in re.split(r",| and ", chunk):
        item = _trim_time_tail(_trim_filler(_finish(item)))
        if QUESTION_START.match(item.lower()):
            break
        if not item or len(item) < 2:
            continue
        if (set(item.split()) & ALLERGY_STOP
                and not _a_modifier_before_a_generic_noun(item.split())):
            # "spicy food" has the word "food" in it, which is a stop word, but the limit is the
            # spicy: the generic noun is how they said it, and the word in front is the thing.
            continue
        if item in ("it", "them", "that", "this") or item in items:
            continue
        if (set(item.split()) & NOT_A_FOOD_IN_IT
                and not set(item.split()) & ONE_MORE_FOODS):
            # "late at night" and "before work" say when, not what, so nothing is filed: the line
            # is about when they eat. A food in the piece keeps it ("i cant eat chilli after 6"),
            # because there the words around it only say when.
            continue
        if _only_stop_words(item):
            continue
        items.append(item)
    return items


# The words a line puts in front of the thing it names, which are not part of it.
ONE_MORE_DETERMINERS = frozenset("""the a an my your his her their our this that these those some""".split())


# "sorry, not peanuts" and "actually not nuts" take an item back; they do not add one. The
# negation is in front of the thing itself, so the part is skipped rather than read as the food
# "not peanuts" - which the store then kept, and "is a prawn curry ok" answered against nothing.
NOT_AN_ADDITION = frozenset("""not no dont don't didnt didn't doesnt doesn't scratch forget never
    nor without""".split())


def one_more(text):
    """The one more thing a line names and nothing else: "and milk too" -> ["milk"].

    A follow-up that adds to a fact already on record names the thing and no fact of its own:
    "im allergic to peanuts" then "and milk too", "plus cheese", "i think soya as well".
    Read on its own such a line states nothing (no verb, no subject), which is why the store
    threw it away and the bot could only echo "milk too" back. The lead-in is not part of the
    thing, and neither is the "too"; what is left has to be a food, because nothing in the line
    says what kind of fact is being added to. A line that names anything else ("and my sister
    too", "and work is awful too", "and the weather") comes back empty and states nothing.
    """
    said = " ".join(str(text or "").lower().split())
    if not said:
        return []
    typed = said
    # The lead-in and the tail come off again and again: "oh and also i think maybe milk as
    # well" is the word "milk", and "milk, as well, please" is the word "milk".
    for _ in range(6):
        before = said
        said = ONE_MORE_HEAD.sub("", said).strip(" ,")
        said = ONE_MORE_TAIL.sub("", said).strip(" ,.!?")
        if said == before:
            break
    if not said or said == typed:
        # A line that is only the thing itself ("milk") is an answer to a question, not an
        # addition to what is on record; the store keeps an answer where it asked for one.
        return []
    items = []
    for part in re.split(r",| and | or ", said):
        words = [word.strip("'\u2019") for word in part.split() if word.strip("'\u2019")]
        # A negation in front of the thing is a take-back, not an addition: "sorry, not peanuts"
        # is the peanuts off the list, and nothing else on the line is being added.
        if words and words[0].lower() in NOT_AN_ADDITION:
            continue
        # "and the milk too" is the milk: a determiner in front is how they said it, not the thing.
        while words and words[0] in ONE_MORE_DETERMINERS:
            words = words[1:]
        if not words or len(words) > 2:
            continue
        # A word in front of the food says which one ("tree nuts", "blue cheese"), so the last
        # word is the one that has to be food: "and tree nuts too" holds a thing the list can
        # take, and "and my sister too" does not.
        if words[-1] not in ONE_MORE_FOODS:
            continue
        head, last = " ".join(words[:-1]), ALLERGEN_PLURALS.get(words[-1], words[-1])
        item = (head + " " + last).strip()
        if item not in items:
            items.append(item)
    return items


# The lead-ins a person puts in front of sharing a limit: "oh me too", "yeah, im too as well".
SHARE_LEAD = r"(?:(?:oh|yeah|yes|and|haha|honestly|sorry|actually)[\s,]+)*"


# The person talking says the limit just said of somebody else is theirs too. The whole line is
# this shape and nothing else, so "me too" after a pizza is a taste (bot/modules/chat.py) and the
# store only reads it when the turn before filed a limit.
I_SHARE_IT = re.compile(
    r"^\W*" + SHARE_LEAD + r"(?:"
    r"im|i'm|i am|me|i"
    r")\s*(?:"
    r"too|also|as well|aswell|the same|same|not alone|"
    r"have (?:it|that|this|the same)(?: too| as well)?|"
    r"do too|am too|"
    # the same said with the verb the limit itself was said with: "i dont either" after "my mum
    # cant eat gluten", "i can too" after "my son can eat nuts again".
    r"dont either|don't either|cant either|can't either|couldnt either|couldn't either|"
    r"havent either|haven't either|can too|could too|do as well|am as well"
    r")\W*$", re.I)


# The same said without a subject: "same here", "so am i", "same as him".
I_SHARE_IT_SHORT = re.compile(
    r"^\W*" + SHARE_LEAD + r"(?:"
    r"same here|same for me|same for us|same|same as (?:me|him|her|them|that|my [a-z]+)|me neither|"
    # The one word that only ever agrees in a chat: "likewise" after "my husband is coeliac" is the
    # user taking the coeliac too. It is read only when the turn before filed a limit, so it stays
    # a plain "you too" after a greeting.
    r"likewise|"
    r"(?:that'?s|this is) me(?: too| as well)?|"
    # "so do i", "neither can i": the verb matches the limit the turn before filed, and the store
    # only reads the line when there was one, so any of them is a share.
    r"so (?:am|do|does|did|have|has|can|could|would) i|"
    r"neither (?:am|do|does|did|have|has|can|could) i|nor (?:am|do|have|can) i"
    r")\W*$", re.I)


# The same share said with the verb first and the relation after it: "so does my brother",
# "neither can my mum". The pronoun forms ("so can he") are not read: after "my wife cant eat
# dairy", "so can he" says the opposite of the limit, so the store keeps out of it.
SOMEONE_SHARES_IT_VERB_FIRST = re.compile(
    r"^\W*" + SHARE_LEAD + r"(?:so|neither|nor)\s+"
    r"(?:does|do|is|are|has|have|can|could|would)\s+(?:my|our)\s+(?P<who>[a-z][a-z'-]{1,14})\W*$",
    re.I)


# Somebody else shares it: "my son is too", "my wife as well", "my mum has it too".
SOMEONE_SHARES_IT = re.compile(
    r"^\W*" + SHARE_LEAD + r"(?:my|our)\s+(?P<who>[a-z][a-z'-]{1,14})\s+"
    r"(?:is|are|does|do|has|have|gets|got|wants)?\s*(?:too|also|as well|aswell|the same|same|"
    r"it too|that too|one too)\W*$", re.I)


# The same with a pronoun, which is the last person the chat named: "she is too", "he has it too".
SOMEONE_SHARES_IT_PRONOUN = re.compile(
    r"^\W*" + SHARE_LEAD + r"(?:he|she|they)\s+"
    r"(?:is|are|does|do|has|have)?\s*(?:too|also|as well|aswell|the same|same|it too|that too)\W*$",
    re.I)


# The word the reader gives back when the line shares it but names nobody: the last person named.
LAST_PERSON = "@last"


def the_limit_they_share(text):
    """"im too", "my son is too": the limit just said is theirs as well, and who "theirs" is.

    A limit said of one person is often shared by the next line, and the line says nothing on its
    own: "my son is allergic to nuts" then "im too" was answered "Glad to hear it." - a happy nod
    at an allergy, with nothing filed - and the reverse "im allergic to nuts" then "my son is too"
    was only echoed back. Both lines mean the same fact said of the other person, so they are
    read here as who the limit belongs to: the person talking ("i"), the relation they named
    ("son"), or the last person the chat named (@last).

    What the line shares is the limit on record, which is the store's question, not this one: a
    line read here that has no limit to share files nothing. Nothing else is a share, so "i love
    pizza" then "me too" stays a taste and "my son is 6" then "im too" is not an age.
    """
    said = " ".join(str(text or "").lower().split()).strip(" !.,")
    if not said or len(said.split()) > 6:
        return ""
    if I_SHARE_IT.match(said) or I_SHARE_IT_SHORT.match(said):
        return "i"
    found = SOMEONE_SHARES_IT.match(said) or SOMEONE_SHARES_IT_VERB_FIRST.match(said)
    if found:
        who = found.group("who").strip()
        # "my own too" and "my self too" name nobody else.
        return "" if who in ("own", "self") else who
    if SOMEONE_SHARES_IT_PRONOUN.match(said):
        return LAST_PERSON
    return ""


def denied_before(text, start):
    """Whether the words at `start` are said not to be true: "im not allergic to nuts"."""
    return bool(DENIAL_WORDS.search(str(text or "")[max(0, start - 40):start]))


def _clause(text, start):
    """The words before the fact at `start`, from the nearest clause edge."""
    head = text[:start]
    cut = 0
    for edge in CLAUSE_EDGE.finditer(head):
        cut = edge.end()
    return head[cut:]


def _around(text, start):
    """The whole clause the words at `start` sit in, from one edge to the next."""
    left = 0
    for edge in CLAUSE_EDGE.finditer(text[:start]):
        left = edge.end()
    right = len(text)
    edge = CLAUSE_EDGE.search(text, start)
    if edge:
        right = edge.start()
    return text[left:right]


def _own_named(text, start, own):
    """The animals the store holds whose name the line has said before `start`.

    "rex died last month" names no animal kind at all - only the name the person gave it - so
    the store's own pet list is the only thing that can hear it. A name counts only when the
    line says it, and it is matched whole, so "rex" does not fire on "rexy".
    """
    found = []
    lowered = text.lower()
    for pet in own or []:
        name = str((pet or {}).get("name") or "").strip().lower()
        animal = str((pet or {}).get("animal") or "").strip().lower()
        if not name or not animal or len(name) < 3:
            continue
        match = re.search(r"\b" + re.escape(name) + r"\b", lowered[:start])
        if match:
            found.append(animal)
    return list(dict.fromkeys(found))


def _own_in_denial(text, own):
    """The store's pets the line says are gone by name, when it named no animal kind.

    "we dont have rex any more" names no animal, only the name, so the store's own list is what
    hears it. Only a name the line puts behind a possession denial counts, and what comes back is
    that one record rather than its animal kind: "we gave fred away" from someone with Milly and
    Fred takes Fred alone, where the kind took both cats off the store.
    """
    gone = []
    for pet in own or []:
        name = str((pet or {}).get("name") or "").strip()
        animal = str((pet or {}).get("animal") or "").strip().lower()
        if not name or not animal or len(name) < 3:
            continue
        for match in re.finditer(r"\b" + re.escape(name) + r"\b", str(text or ""), re.I):
            if not_had(text, match.start()):
                if pet not in gone:
                    gone.append(dict(pet))
                break
    return gone


# A line takes one animal out of a set only when it says something happened to it: "we gave one
# away", "one of them died". "one of them is ill" and "one of them is ginger" are about a pet that
# is still in the house, so the count must not move.
ONE_TAKEN = re.compile(r"\b(?:gave|give|giving|given|gives|rehom(?:e|ed|es|ing)|took|taken|sold|"
                       r"got rid of|went to|passed (?:away|on)|died|lost|left)\b", re.I)


DIY_OF_ALL = re.compile(r"\bone\s+of\s", re.I)


ONE_OF_THEM = re.compile(r"\b(?:one|1)\s+of\s+(?:them|those|the\s+\w+s|our\s+\w+s|my\s+\w+s)\b|"
                         r"\b(?:gave|give|giving|given|rehom(?:e|ed|es|ing)|took|taken|got rid of)\b"
                         r"[^.;!?]{0,20}?\bone\b", re.I)


def given_away_one(text, own=None):
    """The one animal a line gives away without saying which, out of a set on the store.

    "i have two cats" then "we gave one away" leaves one cat, and the store used to keep the
    count at two and answer "You've got two cats." What comes back is the record to take one
    from, and only when the line names no animal of its own: "we gave the cat away" is the
    whole kind, and `denials` has it.
    """
    said = str(text or "")
    if not ONE_OF_THEM.search(said) or not ONE_TAKEN.search(said):
        return []
    kinds = {}
    for pet in own or []:
        if not isinstance(pet, dict):
            continue
        animal = str(pet.get("animal") or "").strip().lower()
        if not animal or (pet.get("count") or 1) < 2:
            continue
        kinds.setdefault(animal, pet)
    if len(kinds) != 1:
        return []
    return [dict(next(iter(kinds.values())))]


def _pointed_at(text, start, plural):
    """The animals a pronoun at `start` can be pointing at: the ones the line named first.

    "my dog is called rex and my cat is milly, we dont have them any more" names two, so a
    plural takes both and a singular takes the nearest: "we dont have him any more" is about
    the cat when the cat was the last animal named. Nothing is guessed when the line never
    named an animal at all.
    """
    named = [match.group(1).lower() for match in PETS.finditer(text[:start])]
    named = list(dict.fromkeys(named))
    if not named:
        return []
    return named if plural else named[-1:]


def not_had(text, start):
    """True when the line says the pet at `start` is not, or no longer, theirs.

    Only possession counts. "i dont have a cat" takes the cat back; "i dont like my cat today"
    and "i dont want a dog" are about how they feel about it, not about what lives in the house,
    and nothing later puts a pet back, so the narrow reading is the safe one.
    """
    clause = _clause(text, start)
    if HEDGE.search(clause):
        return False
    # `_have_none` is given the animal as well as the words before it: the shape it reads is
    # "have no dog", and the animal is the word `_clause` stops at.
    if (NOT_HAVE_LONGER.search(clause) or _have_none(clause + " " + text[start:])
            or WITHOUT_ANIMAL.search(clause)
            or NOT_JUST.search(clause) or taken_back_before(text, start)):
        return True
    return any(match.start() <= start <= match.end() for match in GIVEN_AWAY.finditer(text))


def _have_none(clause):
    """Whether the clause says the animal is not theirs, read without a bare verb deciding it.

    "i have got no dog" and "we have no pets now" name the animal as the thing that is gone, so
    they are the take-back `NOT_HAVE` takes them for. "he has never liked it" names no animal
    after the negation at all, and "he has no dog friends" names one that is not the dog: both
    are things the person is saying about the animal, and neither makes it stop being theirs.
    """
    for match in HAVE_NONE.finditer(clause):
        if A_COMPOUND_AFTER.match(clause[match.end():]):
            continue
        return True
    return False


def taken_back_before(text, start):
    """True when the words in front of the animal take it back, read with the whole line.

    "forget the dog" is a take-back - nothing says "have", so the animal is not one they have.
    "never mind the dog" and "ignore the dog" are not: they ask the chat to move on and leave
    the animal where it was, and a store that read them as a take-back deleted a dog the person
    still had. A bare "no" counts only when the animal ends the line - "no dog" - because "no
    dogs allowed in my flat" is a rule about the flat and "no dog food in the house" is about
    the food.
    """
    said = str(text or "")
    clause = _clause(said, start)
    if HEDGE.search(clause):
        return False
    if TAKEN_BACK_BEFORE.search(clause):
        return True
    animal = PETS.match(said, start)
    rest = said[animal.end():] if animal else said[start:]
    if NO_THEN_A_THING.match(clause):
        # "no a cat": the "no" is the correction talking and the animal is the one they mean.
        return False
    return bool(BARE_NO.match(clause)) and not rest.strip(" .,!?;:")


def their_back(text):
    """A line that puts back what somebody else does not eat or does not like, if it says so.

    "my son doesnt eat fish" then "actually he eats fish", "my wife hates mushrooms" then
    "actually she loves mushrooms": the second line is the person correcting the first, and the
    store went on answering "what does my son eat" with "Your son doesn't eat fish." What it
    reads is what the line says the person does now - [{"who": "son", "pronoun": "", "kind":
    "diet", "food": "fish"}] - and whether anything is on that person's record for the line to
    lift is the store's question, because "he eats fish" on its own is a sentence about the
    world that nobody asked to keep. "them"/"it"/"that" is kept as the pointing word it is: the
    store knows the one thing on that person's record it points at.
    """
    said = str(text or "")
    marked = bool(A_CORRECTION.search(said))
    found = []
    for match in THEIR_BACK.finditer(said):
        if not marked and not match.group("emph"):
            continue  # "my son eats fish" is a sentence about the world, not a correction
        if A_NEGATOR_IN_BETWEEN.search(match.group("gap") or ""):
            continue  # "he doesnt eat fish now" keeps the restriction, it does not lift it
        verb = (match.group("emph") or match.group("verb") or "").lower()
        if not verb:
            continue
        kind = "diet" if verb.startswith("eat") or verb in ("does", "do", "did") else "taste"
        food = " ".join((match.group("food") or "").lower().split())
        if not food:
            continue
        subj = " ".join((match.group("subj") or "").lower().split())
        named = subj.startswith(("my ", "his ", "her ", "their ", "our "))
        found.append({"who": subj.split()[-1] if named else "",
                      "pronoun": "" if named else subj,
                      "kind": kind, "food": food})
    return found


ALL_OF_THEM = re.compile(r"\b(?:both|all|the\s+\w+s|my\s+\w+s|our\s+\w+s)\b", re.I)


def _one_of_several(animals, said, own):
    """A kind word takes one animal when the store holds several: "we gave the cat away".

    Only the whole set is taken by a plural or by "both": "we gave the cats away", "both cats
    went to my mum". Saying "my cat" with two cats on the store that shows one cat, so one goes.

    The several can be one record with a count on it ("i have two cats" is one record, count 2)
    as well as two named records, so the count is what decides, not how many records there are:
    otherwise "we gave the cat away" left nobody with a cat and the store answered "Right - no
    cat, then." to somebody who still had one.
    """
    # "one of the cats" is one animal, so it cancels the plural reading the word itself gives.
    one_of = bool(ONE_OF_THEM.search(said))
    whole = bool(ALL_OF_THEM.search(said)
                 or re.search(r"\b(?:them|those|these)\b", said, re.I)) and not one_of
    out = []
    for animal in animals:
        if not isinstance(animal, str):
            out.append(animal)
            continue
        same = [pet for pet in (own or []) if isinstance(pet, dict)
                and str(pet.get("animal") or "").strip().lower() == animal]
        held = sum(int(pet.get("count") or 1) for pet in same)
        plural = whole or (bool(re.search(r"\b" + re.escape(animal) + r"s\b", said, re.I))
                           and not one_of)
        if held > 1 and not plural:
            out.append(dict(same[-1]))
        else:
            out.append(animal)
    return out


def _merge_pets(had, more):
    """The take-backs of one line, without saying the same one twice.

    A species word ("cat") takes every cat they have; a record takes that one animal; so the two
    kinds do not dedupe against each other and are kept apart.
    """
    out = list(had or [])
    words = {str(item).strip().lower() for item in out if not isinstance(item, dict)}
    records = [item for item in out if isinstance(item, dict)]
    for item in more or []:
        if isinstance(item, dict):
            if item not in records:
                records.append(item)
        elif str(item).strip().lower() not in words:
            words.add(str(item).strip().lower())
            out.append(item)
    return [item for item in out if not isinstance(item, dict)] and (
        [item for item in out if not isinstance(item, dict)] + records) or records


def _the_one_they_have(said, match, own):
    """The animal a bare "him"/"her" points at: one the line already named, or one the store holds.

    "rex died last month, we dont have him any more" is about Rex, and the store's own list is
    what hears a name. A plural takes them all. With nothing to point at this returns nothing;
    `_only_pet` is the fallback and the caller decides whether it is safe.
    """
    return (_pointed_at(said, match.start(), match.group("pron").lower() in PLURAL_PRONOUN)
            or _own_named(said, match.start(), own) or [])


def _only_pet(own):
    """The one animal the store holds, when it holds exactly one."""
    held = [str((pet or {}).get("animal") or "").strip().lower() for pet in (own or [])]
    held = [animal for animal in dict.fromkeys(held) if animal]
    return held if len(held) == 1 else []


def _names_a_relative(said):
    return any(re.search(r"\b" + word + r"\b", said, re.I) for word in RELATIONS)


def _may_be_an_animal(said, match, own=None, said_before=None):
    """Whether a bare "he"/"she" is the animal they keep rather than a person.

    "the vet put him to sleep" is about a pet; "my dad was ill and he died" is not, and taking a
    living pet off the store because a person died is the worst thing this reader could do. So an
    "it" is taken, and a "he"/"she" when the words around it are about putting an animal to sleep
    with no relative anywhere in the line. A plain "he died" is the animal only when the turn
    before it named an animal and no person: "i have a dog" then "he died" is the dog, where "my
    grandad was ill" then "he died" is the grandad, and a bare "he died" with no turn behind it
    says too little to take a living animal off the store.
    """
    if match.group("pron").lower() in ("it", "them", "those", "they"):
        return True
    if _names_a_relative(said) or PEOPLE_WORD.search(said):
        return False
    if ANIMAL_DEATH.search(_around(said, match.start())):
        return True
    before = str(said_before or "")
    if not before or PEOPLE_WORD.search(before) or not PETS.search(before):
        return False  # nothing points at an animal, so "he" is not one
    return bool(_only_pet(own))
