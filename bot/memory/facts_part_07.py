"""Part 7 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re

from ..understanding import breeds, lexicon, normalize

from . import taste
from .facts_part_01 import (
    A_COMMENT_ON_THE_NAME, DIED, HEDGE, PETS, PET_PRONOUN, NAME_WORD, NOT_A_NAME, NAME_AFTER_TITLE,
    NOT_NAMES, NOT_NAMES_EXTRA, PET_APPOSITIVE, NAME_PICK_ASK, PET_NAME_ASKED, NOT_A_PET_NAME,
    PET_ANIMALS, NOT_A_NAME_MIDDLE, PET_BEFORE_FACT, PET_NAME_ONLY, PET_NAME_ONLY_LOWER, PET_COUNT,
    PET_COUNT_WORDS, NOT_A_PRONOUN_NAME, NOT_THE_VERB_NAME, ALSO_HAVE, ANOTHER_ANIMAL, CLAUSE_EDGE,
    NOT_HAVE, NOT_JUST, NOT_THEIR_DETERMINER, PET_IS_NAME, PET_NAME, PET_POSSESSIVE_NAME,
    PET_PRONOUN_NAME, PET_VERB_NAME, WITHOUT_ANIMAL, _name_at, NOT_A_NAME_DESCRIBING,
)
from .facts_part_02 import (
    SPOKEN_RELATION, a_chained_person, RELATIONS, TITLE_WORDS, _A_WORD_FOR_A_PERSON, a_person_word,
    _coming_home, _not_theirs, _only_wanted, _with_title,
)
from .facts_part_03 import (
    JOB_STOP, SELF_JUDGEMENT,
)
from .facts_part_04 import (
    JOB_TAIL, JOB_TAIL_PLACE, _first_tail, _is_a_judgement_phrase, _the_role, without_the_moment,
    _a_word_not_a_name,
)
from .facts_part_05 import (
    CLAUSE_BREAK, SUBJECT, _the_person_is_in_it, A_PRONOUN_NOT_A_NAME, BARE_RELATION,
    BETWEEN_PERSON_AND_FACT, NOT_A_BARE_PERSON_AHEAD, NOT_A_PERSON_WORD, _a_person_word, _around,
    _clause, _may_be_an_animal, _only_pet, _the_one_they_have, stated_not_asked, taken_back_before,
)
from .facts_part_06 import (
    DIET_GROUP, NOT_A_NAME_MIDLINE, NOT_A_NAME_THERE, NAMES_THAT_END_LIKE_A_VERB, NOT_NAME_ENDING,
    a_titled_name, OTHER_CALLED, OTHER_NAMED_BARE, OTHER_NAMED_BEFORE_VERB, OTHER_NAMED_CAPITAL,
    OTHER_NAMED_MIDLINE, OTHER_NAME_IS, _the_name_without_a_possessive, _the_word_then_a_verb,
    names_offered, BARE_NAME, NOT_A_BARE_NAME, JOB_PHRASE,
)


def _a_name_for_the_pet(word, strict_ly=True):
    """The word a pet's name was given as, or None when the word only comments on the name."""
    low = str(word or "").lower()
    if not word or _not_a_name(word, strict_ly=strict_ly) or low in A_COMMENT_ON_THE_NAME:
        return None
    return word


def subject(text, pos):
    """Who the clause that ends at pos is about: (kind, who).

    kind is "user", "other", or "" when the line never says; who is the person named
    ("son", "husband"), or "" for a bare pronoun. "I'm allergic to nuts" is the user's,
    "my son is allergic to nuts" and "he's allergic to nuts" are not: a fact belongs to the
    person it is about, and only the first can be recalled as something the user told us
    about themselves.
    """
    start = 0
    for match in CLAUSE_BREAK.finditer(text, 0, pos):
        start = match.end()
    clause = text[start:pos]
    kind, who = "", ""
    for match in SUBJECT.finditer(clause):
        if match.group("rel"):
            kind = "other"
            who = " ".join((match.group("rel") + (match.group("inlaw") or "")).split()).lower()
            who = SPOKEN_RELATION.get(who, who)
        elif match.group("pron") or match.group("her"):
            kind, who = "other", ""
        else:
            kind, who = "user", ""
    if kind == "other" and who and _the_person_is_in_it(clause):
        # "its for me and my husband, four days": the relation is the last person the clause names,
        # so the length was filed against the husband and not kept at all - the chat then answered
        # "and how many days was it again" from its own memory of a "few days" said before. A
        # thing said about "me and my husband" is about both of them, and the person is one of
        # the two.
        kind = "user"
    if kind == "other" and who:
        # A pair of people is one person, and the clause's own words say which: "my partners mum is
        # allergic to shellfish" read the first relation as the subject and filed the allergy
        # against the partner, who is the person the line did not say it about. The pair wins only
        # when the word the clause named is the pair's first word, so "my mums car" and "my sister
        # and my mum are coeliac" are untouched.
        pair = a_chained_person(clause)
        if pair and pair.split("'s ")[0] == who:
            who = pair
    if kind == "":
        # Nobody in the clause said "my" or "i", so the person in it is the one the words name:
        # a relation word on its own ("mum is allergic to shellfish") or a name ("tom is
        # allergic to nuts"). Before this they were both read as the user, and the bot told the
        # person about somebody else's allergy as if it were their own.
        bare_who, bare_name = _the_person_without_a_relation(clause)
        if bare_who or bare_name:
            kind, who = "other", bare_who
            # A bare relation can head a pair the same way "my" can: "mum and dad are allergic to
            # nuts" is one couple in the store the way "my mum and dad" is.
            pair = a_chained_person(clause)
            if pair and pair.split("'s ")[0] == who:
                who = pair
    return kind, who


def _the_person_without_a_relation(clause):
    """(who, name) for a person the clause names without a "my": ("mum", ""), ("", "Tom")."""
    words = [word.strip(" ,.;:!?").strip("'") for word in clause.split()]
    words = [word for word in words if word]
    while words and words[0].lower() in ("and", "but", "so", "then", "also", "oh",
                                        "ok", "okay", "well", "now", "btw"):
        words.pop(0)
    while words and words[-1].lower() in BETWEEN_PERSON_AND_FACT:
        words.pop()
    if not words or len(words) > 3:
        return "", ""
    if any(word.lower() in NOT_A_BARE_PERSON_AHEAD for word in words[:-1]) \
            or words[-1].lower() in NOT_A_BARE_PERSON_AHEAD:
        return "", ""
    said = " ".join(words)
    found = BARE_RELATION.search(said)
    if found:
        who = found.group("rel") + (found.group("inlaw") or "")
        who = " ".join(who.lower().split())
        if who.endswith("s") and who[:-1] in RELATIONS:
            who = who[:-1]
        return SPOKEN_RELATION.get(who, who), ""
    if len(words) == 1:
        word = words[0]
        if _a_person_word(word) in NOT_A_PERSON_WORD or _a_person_word(word) in DIET_GROUP \
                or _a_person_word(word) in RELATIONS or _a_person_word(word) in A_PRONOUN_NOT_A_NAME:
            return "", ""
        if _may_be_a_name(word) and _name_after_a_title(word):
            return "", word
    return "", ""


def losses(text, own=None, said_before=None):
    """The animals a line says have died, in the shape extract() keeps pets.

    "my cat died last month" is not a take-back to say out loud - the loss is answered by the
    feelings side of the bot, and "Right - no cat, then." is the wrong reply to a bereavement.
    The store still has to hear it, or it hands the animal back later: "what pets do i have"
    after "my cat died" must not answer "You've got a cat called Milly."
    """
    said = str(text or "")
    if not DIED.search(said):
        return []
    animals = []
    others = _someone_elses(said)
    for match in PETS.finditer(said):
        if not DIED.search(_around(said, match.start())):
            continue
        if any(start <= match.start() < stop for start, stop in others):
            continue
        # "my mum's cat died", "the dog next door was put down": somebody else's animal. The
        # sympathy is still theirs to hear, but their own pets stay in the store.
        if _not_their_animal(said, match.start(), match.end()):
            continue
        animal = match.group(1).lower()
        if animal not in animals:
            animals.append(animal)
    if not animals:
        for match in PET_PRONOUN.finditer(said):
            # "put him to sleep" splits around the pronoun, so the clause is read whole
            # rather than only the words before it.
            if not DIED.search(_around(said, match.start())):
                continue
            pointed = _the_one_they_have(said, match, own)
            if not pointed and _may_be_an_animal(said, match, own, said_before):
                pointed = _only_pet(own)
            for animal in pointed:
                if animal not in animals:
                    animals.append(animal)
            break
    if not animals and own:
        for pet in own:
            name = str((pet or {}).get("name") or "").strip().lower()
            animal = str((pet or {}).get("animal") or "").strip().lower()
            if not animal:
                continue
            for match in DIED.finditer(said):
                if HEDGE.search(_clause(said, match.start())):
                    continue
                if name and len(name) >= 3 and re.search(r"\b" + re.escape(name) + r"\b",
                                                         said.lower()):
                    if animal not in animals:
                        animals.append(animal)
    return animals


def _may_be_a_name(word):
    """Whether a word standing where a name stands can be one."""
    low = word.lower()
    return (_looks_like_a_name(word) and low not in NOT_A_NAME_MIDLINE
            and low not in NOT_A_NAME_THERE)


def _looks_like_a_name(word):
    """Whether a word after a relation can be their name: not a relation, not a grammar word."""
    low = word.lower()
    if a_titled_name(word):
        return True  # a title is not a name on its own, but the name after it is the name
    if low.strip(".") in TITLE_WORDS:
        return False  # "my sister is called mr smith" is Mr Smith, and Mr names nobody
    if not NAME_WORD.match(word) or low in NOT_A_NAME or low in RELATIONS:
        return False
    if is_a_contraction(low):
        return False
    if word[:1].isupper() or low in NAMES_THAT_END_LIKE_A_VERB:
        return True  # typed with a capital, the way a name is written
    return not low.endswith(NOT_NAME_ENDING)


def _name_after_a_title(name):
    """Whether a name that starts with a title is a name at all.

    A title is part of the name ("Mr Smith"), and the word after it is what makes it a name: "my
    sister is called mrs tired" names nobody, because the word after the title is one of the
    things people say about a person. A title on its own names nobody either, which is how the
    store came to answer "Your sister is called Mr".
    """
    words = str(name or "").split()
    if not words:
        return False
    title = words[0].strip(".").lower()
    if title not in TITLE_WORDS:
        return True
    if len(words) == 1:
        return False
    rest = " ".join(words[1:]).lower()
    if rest in NAME_AFTER_TITLE:
        return True  # "Dr Who"
    if rest in NOT_A_NAME or rest in NOT_NAMES or rest in NOT_NAMES_EXTRA \
            or rest in _A_WORD_FOR_A_PERSON:
        return False
    return not _not_a_name(rest, strict_ly=False)


def _a_relations_name(text):
    """[{"who": "sister", "name": "meg"}] for a name the line gives to someone in the family."""
    found = []
    text = stated_not_asked(text)
    if not text:
        return found
    without_possessive = _the_name_without_a_possessive(text)
    for pattern in (OTHER_CALLED, OTHER_NAME_IS, OTHER_NAMED_BARE):
        for match in pattern.finditer(text):
            who = a_person_word(match.group("who"))
            if who.endswith("s") and who[:-1] in RELATIONS:
                who = who[:-1]
            name = match.group("name")
            if not _looks_like_a_name(name) or not _name_after_a_title(name):
                continue
            if who in [entry["who"] for entry in found]:
                continue
            found.append({"who": who, "name": name})
    for match in OTHER_NAMED_BEFORE_VERB.finditer(text):
        who = a_person_word(match.group("who"))
        if who.endswith("s") and who[:-1] in RELATIONS:
            who = who[:-1]
        name = without_possessive.get(str(match.group("name")).lower(), match.group("name"))
        if not _the_word_then_a_verb(name, match.group("verb")):
            continue
        if not _may_be_a_name(name):
            continue
        if who in [entry["who"] for entry in found]:
            continue
        found.append({"who": who, "name": name})
    for match in OTHER_NAMED_CAPITAL.finditer(text):
        who = a_person_word(match.group("who"))
        if who.endswith("s") and who[:-1] in RELATIONS:
            who = who[:-1]
        name = without_possessive.get(str(match.group("name")).lower(), match.group("name"))
        if not _may_be_a_name(name):
            continue
        if who in [entry["who"] for entry in found]:
            continue
        found.append({"who": who, "name": name})
    for match in OTHER_NAMED_MIDLINE.finditer(text):
        who = a_person_word(match.group("who"))
        if who.endswith("s") and who[:-1] in RELATIONS:
            who = who[:-1]
        name = without_possessive.get(str(match.group("name")).lower(), match.group("name"))
        if not _may_be_a_name(name):
            continue
        if who in [entry["who"] for entry in found]:
            continue
        found.append({"who": who, "name": name})
    return found


def pet_appositive(text, start=0):
    """The name given for the animal at `start` as an aside ("a rescue dog, biscuit"), or None."""
    animals = [match.start() for match in PETS.finditer(text)]
    later = [position for position in animals if position >= start]
    limit = later[1] if len(later) > 1 else len(text)
    span = text[start:limit]
    match = PET_APPOSITIVE.search(span)
    if not match or not _names_it_aside(match, span):
        return None
    return match.group(1)


def a_name_picked(text, memory):
    """The name given as the answer to the bot's own question or list, or None.

        we got a puppy / What's its name? / biscuit
        what should i name it / For a cat: Miso, Willow or Pepper. / milo
        we got a kitten / what should we name her / pepper

    The word alone says nothing, so it is a name only when the line before it asked for one or
    offered some: anything longer than a word or two ("i dont know", "no idea") is not this, and
    nor is a word the bot never asked about. That is the whole test - the caller decides what to
    do with the name, and the answers lane stands down on it, because a person choosing a name is
    not asking about the food the word also names ("pepper").
    """
    word = bare_name(text)
    if not word:
        return None
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    last = turns[-1]
    asked = str(last.get("bot") or "")
    asked_for_one = (asked.rstrip().rstrip('"').endswith("?")
                     and bool(PET_NAME_ASKED.search(asked)))
    theirs = bool(NAME_PICK_ASK.search(str(last.get("user") or "")))
    if not (asked_for_one or theirs or names_offered(memory)):
        return None
    return word


def bare_name(text):
    """The one word a line is, when the line is nothing but that word: "biscuit", "milo".

    A word on its own says nothing; the question before it is what says it is a name, so this
    only shape-checks the line and leaves the reading to the caller.
    """
    if not isinstance(text, str):
        return None
    match = BARE_NAME.match(text.strip())
    if not match:
        return None
    word = match.group(1)
    low = word.lower()
    if is_addressing(word):
        return None
    if low in NOT_A_BARE_NAME or low in NOT_A_PET_NAME or low in PET_ANIMALS:
        return None
    if not re.search(r"[aeiouy]", low) or re.fullmatch(r"\d+", low):
        return None
    return word


# "my brother got a job as a chef", "my mum works as a teacher": the same fact said the other
# way. Only "as" is read: "my mum works in a warehouse" names where she works rather than what
# she does, and saying that back as her job would be a place handed over as a role.
OTHER_JOB_AS = re.compile(
    r"(?<!\w)(?P<subj>(?:my|our|his|her|their)\s+[a-z][a-z'\u2019-]*|he|she|they)"
    r"[^.,;!?]{0,20}?\b(?:job|work|works|working|worked)\s+as\s+(?:an?\s+)?" + JOB_PHRASE,
    re.I)


# The same fact with the person's name between the relation and the verb: "my sister emma is a
# nurse", "our son tom is a teacher". Every other reader of somebody else's fact allows the name
# ("my son jack is 6"), so the job did too little: the word after the relation was the name, the
# pattern wanted the verb, and `my sister emma is a nurse` / `what does my sister do` answered
# that the chat had never been told what she does - while the name itself was dropped as well.
OTHER_JOB_NAMED = re.compile(
    r"(?<!\w)(?P<subj>(?:my|our|his|her|their)\s+[a-z][a-z'\u2019-]*)"
    r"\s+(?P<name>[a-z][a-z'\u2019-]*)"
    r"(?:'s|\s+is|\s+was)\s+(?:a|an)\s+" + JOB_PHRASE, re.I)


def _the_job_phrase(phrase, place_job=False):
    """A job as it is said back: "nurse", "car mechanic", "primary school teacher".

    The same cleaning the speaker's own job gets: the phrase stops where the line turns to
    something else, and a word that judges the person rather than naming a role is not a job.
    """
    cut = _first_tail(phrase, JOB_TAIL_PLACE if place_job else JOB_TAIL)
    if cut:
        phrase = phrase[:cut[0]]
    words = without_the_moment(phrase.split())
    if not words:
        return ""
    first = words[0].lower()
    if (first in JOB_STOP or first in NOT_NAMES or first in NOT_NAMES_EXTRA
            or first in SELF_JUDGEMENT or _is_a_judgement_phrase(words)):
        return ""
    if re.match(r"\d", first):
        return ""
    return _the_role(words)


def _names_before_a_fact(text):
    """The names a line puts between the animal and what it says about it.

    "my dog max is 4" and "our cat biscuit was 12" name the animal in passing, and the word
    between it and the verb is its name. A word that goes with the animal as a thing ("my dog
    food is expensive") is the thing, not the name, unless the line then says a fact about the
    animal itself ("my cat biscuit is 3").
    """
    found = []
    for match in PET_BEFORE_FACT.finditer(text):
        name = match.group("name")
        if _not_a_name(name, strict_ly=False) or name.lower() in NOT_A_NAME_MIDDLE:
            continue
        if name.lower() in PET_COMPOUND and not AFTER_A_PET.match(text[match.end("name"):]):
            continue
        found.append((match.start("name"), name))
    return found


def pet_name_only(text, lower=False):
    """The name a line gives to a pet it does not name again: "and her name is Biscuit".

    `lower` also reads the name typed without a capital ("and her name is biscuit"). It is for
    the caller that already knows there is a pet on record: there the possessive in front of
    "name" is the whole signal, and the word after it is a name until `_not_a_name` says it is
    not ("his name is long", "his name is the one i forget").
    """
    for match in PET_NAME_ONLY.finditer(text):
        name = match.group(1) or match.group(2) or match.group(3)
        name = _a_name_for_the_pet(name) if name else None
        if name:
            return name
    if lower:
        for match in PET_NAME_ONLY_LOWER.finditer(text):
            # The possessive names the animal and what follows says a name, so a word ending in
            # -ly is a name here, not the adverb the bare rule is right about: "her names
            # actually tilly" kept Tom because Tilly ends in -ly, and Kitty, Molly and Lily are
            # as ordinary a pet name as any.
            name = _a_name_for_the_pet(match.group(1), strict_ly=False)
            if name:
                return name
    return None


def _count_before(text, start):
    """"two cats", "2 dogs", "a couple of rabbits": how many, or 0 when the line does not say."""
    match = PET_COUNT.search(text[:start])
    if not match:
        return 0
    word = match.group(1).lower()
    if word.isdigit():
        return int(word)
    return PET_COUNT_WORDS.get(word, 0)


# How many names a plural animal can be followed by when the line never gave a number: the
# plural says only that there is more than one, so the list is read until the words run out.
MOST_NAMES = 6


def _names_after(rest, count, most=None):
    """The names a line lists for the animals it has just counted.

    "two cats, milly and tom" and "two cats called milly and tom" are both two cats; the count is
    what makes the list a list of names, so "two dogs, a lab and a terrier" stays nameless.

    `most` is for the line whose only count is a plural animal: "my cats are called tom, jerry and
    bub" names three, and a guess of two there drops Bub - the same wrong fact as reading one name
    off a line that lists two. So the list is read until the words run out and only the number of
    names the line really supports is kept.
    """
    if count < 2 and not most:
        return []
    target = count if count >= 2 else most
    # "my cats are called tom and jerry", "two dogs named..." - the verb can come before
    # "called", and the plural animal already said how many there are.
    match = re.match(r"\s*(?:(?:are|is|were|was)\s+)?(?:called|named)\s+", rest, re.I)
    if match:
        rest = rest[match.end():]
    else:
        match = re.match(r"\s*[,:]\s*", rest)
        if not match:
            return []
        rest = rest[match.end():]
    names = []
    for piece in re.split(r"\s*(?:,|/|&|\band\b)\s*", rest):
        piece = piece.strip().strip(".!?")
        if not piece or len(piece.split()) != 1:
            break
        if not NAME_WORD.match(piece) or piece.lower() in NOT_A_NAME:
            break
        names.append(piece)
        if len(names) == target:
            break
    if count < 2:
        return names if len(names) >= 2 else []
    return names if len(names) == count else []


# "my neighbour has a dog called Rex": the animal belongs to someone else, and reading it back as
# the user's own would put words in their mouth. "my partner and I got a dog" is still theirs.
OTHER_PET = re.compile(r"\b(?:my|our)\s+(?:[a-z]+\s+){0,2}(?:" + "|".join(RELATIONS) +
                       r")\s+(?:has|have|got|adopted|rescued|bought|owns?|keeps?|"
                       r"doesn'?t have|doesnt have|does not have|don'?t have|dont have|"
                       r"never had|no longer has|had to (?:give|rehome))\b", re.I)


# An animal that is not theirs, said with its owner in front ("my mum's cat died", "the
# neighbour's dog", "sarah's dog was put down") or with where it lives after it ("the cat next
# door", "a cat died in our street", "the dog across the road"). Read as the user's own, a death
# of somebody else's animal takes theirs off the store, and the pet ask is where a person checks
# the bot remembers an animal that is alive.
OWNER_OF = re.compile(r"\b(?:(?:my|our|his|her|their|the)\s+(?:\w+\s+){0,2}?[\w-]+"
                      r"(?:'s|s'|\u2019s))\s+(?:\w+\s+){0,2}$", re.I)


LIVES_ELSEWHERE = re.compile(r"^\s*(?:\w+\s+){0,3}?(?:next door|across the (?:road|street)|"
                             r"in (?:our|the) (?:street|road|village|block)|down the road|"
                             r"from next door|round the corner|up the road)\b", re.I)


# The same owner said without the possessive, which is how most people type it: "the neighbours
# dog", "the family cat", "their dog". A plural is enough - "the neighbours dog" is the same
# animal as "the neighbour's dog" - and the plain word is the only thing saying whose it is.
# "their" is here too: "their dog barks at my kids" is not an animal of the user's, and reading
# it as one is how the store came to answer "Right - no dog, then." a turn later.
# Only the people who are not the household: "the family dog" and "our family cat" are the
# family's own animals, the same as "our dog", so family, kids, mum and the rest are not here.
# A named person with an apostrophe ("my mum's dog", "the kids' rabbit") is read by OWNER_OF.
OTHER_PEOPLE = (r"(?:neighbou?rs?|landlords?|landlad(?:y|ies)|flatmates?|housemates?|roommates?|"
                r"friends?|mates?|colleagues?|boss(?:es)?|owners?|walkers?|someone|somebody|"
                r"anyone|anybody|nobody|people|another)")


OWNER_OF_PLAIN = re.compile(r"\b(?:their|" + OTHER_PEOPLE + r")\s+(?:[a-z]+\s+){0,2}$|"
                            # "someone else's dog", "anyone else's cat": the owner is nobody they
                            # can name, and the apostrophe goes missing as often as not.
                            r"\b(?:someone|somebody|anyone|anybody|nobody)\s+else'?s?\s+"
                            r"(?:[a-z]+\s+){0,2}$", re.I)


# An animal the line names as the person's own ("my dog", "our cat") is theirs whatever else the
# sentence says: "the vet put my dog down" is about their dog, and the vet is who did it.
# "our" is not enough on its own: "our neighbours dog" is still the neighbours' animal, so the
# word after it must not be somebody else. "my kids love our dog" is about their own dog.
OWN_ANIMAL = re.compile(r"\b(?:my|our)\s+(?!(?:" + OTHER_PEOPLE + r")\b)(?:[a-z]+\s+){0,2}$",
                        re.I)


# "we got another cat" is one more of the animals they have, not somebody else's animal: the word
# "another" is on the not-theirs list for "another family's dog" and "a dog of another", and a
# line that says whose hand took the animal on is about their own. Read as somebody else's, the
# second cat was dropped and "we got another cat called Max" left the store with one cat called
# Milo. The verb has to be there, so "i saw another cat in the garden" is still not a new pet.
OURS_ANOTHER = re.compile(r"\b(?:we|i)(?:\s+have|\s*'ve|\s*ve)?\s+(?:just\s+|also\s+)?"
                          r"(?:got|gotten|adopted|rescued|took in|taken in|bought|brought home|"
                          r"rehomed)\s+(?:another|a second|one more|a new)\b", re.I)


# "my brothers cat is called Max", "my mums dog": the apostrophe goes missing as often as it is
# typed, and the animal is the relation's, not the person's. `OWNER_OF` needs the apostrophe, so
# without this the brother's cat went into the store as theirs and took the name of the cat they
# do have. Only the relations who live somewhere else: "my kids cat" and "the family dog" are the
# household's own animals.
KIN_OWNER = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:brothers?|sisters?|mums?|moms?|mothers?|fathers?|dads?|"
    r"sons?|daughters?|grandmas?|grandads?|grandmothers?|grandfathers?|nans?|uncles?|aunts?|"
    r"cousins?|nephews?|nieces?|in-laws?|parents?|neighbou?rs?|flatmates?|housemates?|"
    r"friends?|step-?(?:mums?|moms?|dads?|sons?|daughters?))\b\s+(?:[a-z]+\s+){0,2}$", re.I)


def _not_their_animal(text, start, end):
    """True when the animal at this position belongs to somebody else, or to nobody."""
    before = text[max(0, start - 40):start]
    # "my brothers cat" is the same shape as "my dog", so the kin word is read first: OWN_ANIMAL
    # would take the animal for theirs on the strength of the "my".
    if KIN_OWNER.search(before):
        return True
    if OWN_ANIMAL.search(before):
        return False
    if OURS_ANOTHER.search(before):
        return False
    return bool(OWNER_OF.search(before) or OWNER_OF_PLAIN.search(before)
                or LIVES_ELSEWHERE.match(text[end:end + 40]))


def _someone_elses(text):
    """The parts of a line where the animal belongs to another person."""
    spans = []
    for match in OTHER_PET.finditer(text):
        end = re.search(r"[.!?;]", text[match.end():])
        spans.append((match.end(), match.end() + end.start() if end else len(text)))
    return spans


# "i don't eat fish", "we cook a chicken", "fish for dinner": the animal is on the plate.
FOOD_BEFORE = re.compile(r"\b(?:eat|eats|eating|ate|without|cook|cooked|cooks|cooking|buy|bought|"
                         r"roast|roasted|grilled|fried|order|ordered|serve|served|avoid|avoids|"
                         r"allergic to|instead of)\s+(?:\w+\s+){0,2}$", re.I)


FOOD_AFTER = re.compile(r"\s+(?:\w+\s+){0,2}?(?:(?:for|as)\s+(?:dinner|lunch|tea|supper|"
                        r"breakfast|christmas|a meal)|tonight|today|tomorrow|last night|"
                        r"this evening)\b", re.I)


# "my cat is called Fish": that word is a name, not a second animal.
NAME_BEFORE = re.compile(r"\b(?:called|named)\s+$", re.I)


# "i got a fish bone out myself", "the cat flap is broken": the animal is part of a compound
# noun, and the head of it is the other word, so nothing says the person keeps the animal. A
# fishbone, dog food and cat litter are all things around the house, not a pet introduced.
PET_COMPOUND = frozenset("""
bone bones food meat fingers finger pie cake cakes sandwich soup stock oil sauce
flap collar lead leash harness bed basket bowl cage hutch tank litter tray
toy toys treats treat biscuit biscuits brush shampoo hair fur vet insurance tag
door house kennel mask net bowlful piece poo mess hairball
""".split())


AFTER_ANIMAL = re.compile(r"[a-z]+")


# "my cat biscuit is 3": biscuit is a thing that goes with a cat and also a name a cat is given,
# so the compound read is only right when the line is about the thing. When the animal is
# introduced with a possessive and the word after it is what the line then says something about,
# the word is the animal's name: "my cat biscuit is 3", "my dog patch has a bad leg".
AFTER_A_PET = re.compile(
    r"\s*(?:(?:is|was)(?:n't|nt)?\s+(?:\d|a\b|an\b|so\b|really\b|very\b|getting\b|not\b)|"
    r"(?:has|had|needs|likes|hates|loves|eats|sleeps|snores|bites|chews|barks|sheds|"
    r"doesn't|doesnt|isn't|isnt)\b)", re.I)


THEIR_ANIMAL = re.compile(r"\b(?:my|our)\s+$", re.I)


# A relation that is somebody else's, not the person's: "my dad has a son" is the dad's son,
# "my sister has two sons" is two grandsons, and "my dad's son is a teacher" is a brother. Filed
# as the person's own, a relative's child answered "how many children do i have" with somebody
# else's, and the count was confidently wrong.
SOMEONE_ELSE_HAS = re.compile(
    r"\b(?:my|our)\s+(?:" + "|".join(RELATIONS) + r")(?:\s*-?\s*in\s*-?\s*laws?)?\b"
    r"(?:\s+\w+){0,2}?\s+(?:has|have|had|got)\b", re.I)


A_RELATION_OWNED = re.compile(
    # "my dad's son", "my sister's two sons", "my mother in laws son": the apostrophe is left off
    # as often as it is typed, and a count can sit between the owner and the person.
    r"\b(?:my|our)\s+(?:" + "|".join(RELATIONS) + r")\b"
    r"(?:\s*-?\s*in\s*-?\s*laws?|['\u2019]s?)"
    r"(?:\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|older|"
    r"younger|elder|eldest|youngest|first|second|third|only|own|other))*\s+$", re.I)


# The things people say are theirs and then ask about later by name. A line that names one of
# these and what it is ("my car is a ford fiesta", "my phone is an iphone 13") says something
# about the person that no other reader keeps, so "what car do i drive" was a hedge about a car
# the chat had been told the model of two turns earlier. The list is the everyday things a
# person names by make or model, not everything anybody owns: a closed list is what keeps "my
# car is old and keeps breaking down" and "my phone is on its way out" from filing a model.
OWNED = frozenset("""car phone mobile iphone laptop bike motorbike motorcycle van tablet ipad
camera tv television boiler oven fridge freezer dishwasher washing-machine tumble-dryer
hoover vacuum mower kettle""".split())


# A make or model of two words is a model: "ford fiesta", "worcester bosch". Three is the most
# anybody says in one breath ("iphone 13 pro max" is four, so the cap is four).
OWNED_VALUE = re.compile(
    # "my car is a ford fiesta", "my phone's an iphone 13", "our boiler is a worcester bosch".
    # The contraction goes with the word: nobody types "my car 's a fiesta", so an apostrophe
    # alternative written after \s+ never matches at all.
    r"\b(?:my|our)\s+(?P<thing>[a-z][a-z-]*)(?:\s+(?:is|was)|\s*'s)\s+(?:a|an|the)\s+"
    r"(?P<value>[a-z0-9][a-z0-9' .+-]{0,31})"
    # "the car i drive is a ford fiesta"
    r"|\bthe\s+(?P<thing2>[a-z][a-z-]*)\s+i\s+(?:drive|ride|use|have|own)\s+(?:is|'s)\s+"
    r"(?:a|an|the)\s+(?P<value2>[a-z0-9][a-z0-9' .+-]{0,31})"
    # "i drive a ford focus", "i ride a boardman"
    r"|\bi\s+(?P<verb>drive|ride)\s+(?:a|an|the)\s+(?P<value3>[a-z0-9][a-z0-9' .+-]{0,31})"
    # "i have a ford fiesta", "i've got an iphone 13": the line names no thing, so only a make
    # can say which thing it is - "i have a focus" stays out, as "a focus" is as likely to be
    # a focus on the week ahead.
    r"|\bi(?:'ve|\u2019ve)?\s+(?:have|got)\s+(?:a|an|the)\s+"
    r"(?P<value4>[a-z0-9][a-z0-9' .+-]{0,31})",
    re.I)


# Words that end the value: a model is a name, so the first word of another clause is not part.
OWNED_STOP = frozenset("""and but so because or plus then which that who what when where why how
if although though while also too as well""".split())


# What a thing is, when it is not a model: "my car is old", "my phone is broken", "the boiler is
# a nightmare". None of these says what make it is, so none of them is kept: the ask about the
# car is answered by saying it has not been told the make, never by "Your car is old".
# The makes people name a thing by, with the kind of thing each one makes and the way it is
# written. The kind does two jobs. It lets "i have an iphone 13" file a phone in a line that
# never says "phone", and it is the brake: an unknown word is no make at all, so "i drive a hard
# bargain" and "my car is a right state" file nothing, and a make of the wrong kind ("my car is
# an iphone") files nothing either. A make with no kind (Bosch, Sony, Samsung) is made by many
# things, so it is taken for whatever thing the line named.
OWNED_MAKES = {
    "ford": ("car", "Ford"), "vauxhall": ("car", "Vauxhall"), "toyota": ("car", "Toyota"),
    "volkswagen": ("car", "Volkswagen"), "vw": ("car", "VW"), "bmw": ("car", "BMW"),
    "audi": ("car", "Audi"), "nissan": ("car", "Nissan"), "honda": ("car", "Honda"),
    "kia": ("car", "Kia"), "hyundai": ("car", "Hyundai"),
    "peugeot": ("car", "Peugeot"), "renault": ("car", "Renault"),
    "citroen": ("car", "Citroen"), "skoda": ("car", "Skoda"), "volvo": ("car", "Volvo"),
    "mini": ("car", "MINI"), "fiat": ("car", "Fiat"), "tesla": ("car", "Tesla"),
    "mazda": ("car", "Mazda"), "suzuki": ("car", "Suzuki"), "jaguar": ("car", "Jaguar"),
    "seat": ("car", "SEAT"), "dacia": ("car", "Dacia"), "lexus": ("car", "Lexus"),
    "mitsubishi": ("car", "Mitsubishi"), "subaru": ("car", "Subaru"),
    "mercedes": ("car", "Mercedes"), "cupra": ("car", "Cupra"),
    "iphone": ("phone", "iPhone"), "oneplus": ("phone", "OnePlus"),
    "pixel": ("phone", "Pixel"), "samsung": ("phone", "Samsung"),
    "motorola": ("phone", "Motorola"), "nokia": ("phone", "Nokia"),
    "xiaomi": ("phone", "Xiaomi"), "redmi": ("phone", "Redmi"), "oppo": ("phone", "Oppo"),
    "huawei": ("phone", "Huawei"), "honor": ("phone", "Honor"),
    "fairphone": ("phone", "Fairphone"),
    "boardman": ("bike", "Boardman"), "carrera": ("bike", "Carrera"),
    "trek": ("bike", "Trek"), "giant": ("bike", "Giant"),
    "brompton": ("bike", "Brompton"), "specialized": ("bike", "Specialized"),
    "ridgeback": ("bike", "Ridgeback"), "voodoo": ("bike", "Voodoo"),
    "cube": ("bike", "Cube"), "scott": ("bike", "Scott"),
    "pinnacle": ("bike", "Pinnacle"), "dawes": ("bike", "Dawes"),
    "worcester": ("boiler", "Worcester"), "vaillant": ("boiler", "Vaillant"),
    "ideal": ("boiler", "Ideal"), "baxi": ("boiler", "Baxi"),
    "viessmann": ("boiler", "Viessmann"), "potterton": ("boiler", "Potterton"),
    "bosch": (None, "Bosch"), "lg": (None, "LG"), "sony": (None, "Sony"),
    "panasonic": (None, "Panasonic"), "philips": (None, "Philips"),
    "dyson": (None, "Dyson"), "hoover": (None, "Hoover"), "miele": (None, "Miele"),
    "smeg": (None, "Smeg"), "aeg": (None, "AEG"), "zanussi": (None, "Zanussi"),
    "beko": (None, "Beko"), "indesit": (None, "Indesit"), "hotpoint": (None, "Hotpoint"),
    "neff": (None, "Neff"), "siemens": (None, "Siemens"), "whirlpool": (None, "Whirlpool"),
    "candy": (None, "Candy"), "shark": (None, "Shark"), "vax": (None, "Vax"),
    "henry": (None, "Henry"), "canon": (None, "Canon"), "nikon": (None, "Nikon"),
    "fujifilm": (None, "Fujifilm"), "olympus": (None, "Olympus"), "dell": (None, "Dell"),
    "lenovo": (None, "Lenovo"), "acer": (None, "Acer"), "asus": (None, "Asus"),
    "toshiba": (None, "Toshiba"), "macbook": (None, "MacBook"), "ipad": (None, "iPad"),
    "ipod": (None, "iPod"), "apple": (None, "Apple"), "surface": (None, "Surface"),
    "razer": (None, "Razer"), "flymo": (None, "Flymo"), "mountfield": (None, "Mountfield"),
    "stihl": (None, "Stihl"), "ryobi": (None, "Ryobi"), "makita": (None, "Makita"),
    "husqvarna": (None, "Husqvarna"), "rangemaster": (None, "Rangemaster"),
    "electrolux": (None, "Electrolux"),
}


# The models people say without the make: "my car is a fiesta", "sorry its a focus". A model is
# only read for a thing the line - or the correction - already says is that kind of thing,
# because "a focus" on its own is as likely to be a focus on the week ahead.
OWNED_MODELS = {
    "fiesta": ("car", "Fiesta"), "focus": ("car", "Focus"), "golf": ("car", "Golf"),
    "corsa": ("car", "Corsa"), "astra": ("car", "Astra"), "polo": ("car", "Polo"),
    "clio": ("car", "Clio"), "micra": ("car", "Micra"), "yaris": ("car", "Yaris"),
    "qashqai": ("car", "Qashqai"), "mondeo": ("car", "Mondeo"),
    "fabia": ("car", "Fabia"), "ibiza": ("car", "Ibiza"),
    "sportage": ("car", "Sportage"), "tucson": ("car", "Tucson"),
    "civic": ("car", "Civic"), "passat": ("car", "Passat"), "octavia": ("car", "Octavia"),
    "transit": ("car", "Transit"),
}


# The kind of thing a word names, for the brake above: a van is a car in the sense that matters
# here, and a motorbike and a bike are one kind.
OWNED_KIND = {"car": "car", "van": "car", "bike": "bike", "motorbike": "bike",
              "motorcycle": "bike", "phone": "phone", "mobile": "phone", "boiler": "boiler"}


OWNED_NOT_A_MODEL = frozenset("""old new broken dead knackered leaking noisy rubbish great fine
ok okay good bad slow fast heavy light cheap expensive tiny small big rubbish fantastic brilliant
useless amazing lovely horrible awful terrible second third hand handy faulty dodgy nightmare
disaster joke mess dream beauty beast monster bargain steal ripoff wreck banger shed pain on mine
yours theirs ours its""".split())


# A line that opens with an asking word asks: "what car do i drive" is not "i drive a focus".
# Only the opening word counts, because the words that ask sit inside statements too - "is" in
# "my car is a ford fiesta", "do" in "i do like it" - and a statement read as a question files
# nothing at all.
OPENS_AN_ASK = re.compile(r"^(?:what|which|who|whom|whose|how|where|when|why|do|does|did|is|are|"
                          r"was|were|can|could|would|should|shall|will|have|has)\b", re.I)


TELLS_ABOUT = re.compile(r"^(?:my|our|the|i|we|he|she|they)\b", re.I)


def _a_question(text):
    """Whether the line asks rather than tells: "what car do i drive" is not "i drive a focus"."""
    low = str(text or "").strip()
    if OPENS_AN_ASK.match(low):
        return True
    return low.endswith("?") and not TELLS_ABOUT.match(low)


def _owns(text):
    """What the person says they have, by the name of the thing: {"car": "Ford Fiesta"}.

    Only a line that names a thing and its make or model is read - "my car is a ford fiesta",
    "i drive a ford focus", "i've got an iphone 13" - and only for the closed list of things
    people name that way. A line that asks is not a statement of one, so "what car do i drive"
    files nothing, and a word that is not a make files nothing either.
    """
    if not text or _a_question(text):
        return {}
    found = {}
    for match in OWNED_VALUE.finditer(text):
        thing = (match.group("thing") or match.group("thing2") or "").lower()
        said = (match.group("value") or match.group("value2") or match.group("value3")
                or match.group("value4") or "")
        if not thing and match.group("value4"):
            # "i have a ford fiesta" names no thing, so the make says which one it is: only a
            # make can, and a make of no one kind ("i have a bosch") says nothing at all.
            thing = _the_thing_of(match.group("value4"))
        if not thing:
            # The verb says which thing it is: "i drive" a car, "i ride" a bike.
            thing = {"drive": "car", "ride": "bike"}.get((match.group("verb") or "").lower(), "")
        thing = thing.replace("-", " ")
        if thing not in OWNED or thing in found:
            continue
        value = _the_model(said, thing)
        if value:
            found[thing] = value
    return found


def _the_thing_of(value):
    """The thing a make belongs to: "i have a ford fiesta" names a car without saying so."""
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'+-]*", str(value or ""))
    family = (OWNED_MAKES.get(words[0].lower()) or (None, ""))[0] if words else None
    return {"car": "car", "phone": "phone", "bike": "bike", "boiler": "boiler"}.get(family, "")


def _the_model(value, thing=""):
    """The make and model out of what followed the article, or "" when it is not one.

    "a ford fiesta and a bike rack" is a Fiesta: the value stops at the word that starts the next
    clause. "old" and "broken" are what the thing is like, not what it is, and a word that is no
    make or model is nothing either - "a right state" and "a hard bargain" file nothing, which is
    what stops the store answering "You drive a Hard Bargain."
    """
    words = []
    for word in re.findall(r"[A-Za-z0-9][A-Za-z0-9'+-]*", str(value or "")):
        if word.lower() in OWNED_STOP or len(words) == 4:
            break
        words.append(word)
    words = without_the_moment(words)  # "a corsa now" is a Corsa, not a "Corsa Now"
    if not words:
        return ""
    first = words[0].lower()
    if first in OWNED_NOT_A_MODEL:
        return ""
    kind = OWNED_KIND.get(str(thing or "").lower(), "")
    make = OWNED_MAKES.get(first)
    if make:
        # A make of the wrong kind is not this thing's make: "my car is an iphone".
        if kind and make[0] and make[0] != kind:
            return ""
        return _spell_the_model(words)
    model = OWNED_MODELS.get(first)
    # A model is only read for a thing the line already named as that kind of thing.
    if not model or not kind or model[0] != kind:
        return ""
    return _spell_the_model(words)


def _spell_the_model(words):
    """The value written the way a name is: "ford fiesta" -> "Ford Fiesta", "bmw" -> "BMW"."""
    spelled = []
    for word in words:
        known = OWNED_MAKES.get(word.lower()) or OWNED_MODELS.get(word.lower())
        spelled.append(known[1] if known else word[:1].upper() + word[1:])
    return " ".join(spelled)


def _a_name_given_by_the_verb(word):
    """True when the word after "we named the cat ..." is the name and not the rest of a sentence.

    A name is a word the line gives the animal: "after my grandma" is who it was named *after*,
    "in for dinner" is where it was called, and "him" is the animal itself.
    """
    word = str(word or "").strip()
    low = word.lower()
    if low in NOT_A_NAME or low in NOT_THE_VERB_NAME or low in NOT_A_PRONOUN_NAME:
        return False
    return bool(NAME_WORD.match(word))


# A puppy is a dog and a kitten is a cat. The pet reader keeps the word the person used - people
# say "my puppy is a spaniel" far more often than "my dog is a spaniel" - so the breed's kind and
# the animal's own word were compared as different animals and one pet was filed as two: "You've
# got a puppy and a spaniel. Do they get on?" about the one animal they had just described.
GROWN_UP = {"puppy": "dog", "pup": "dog", "kitten": "cat", "kitty": "cat"}


def _the_same_animal(one, other):
    """Whether two names for a kind of animal are the same animal."""
    return GROWN_UP.get(one, one) == GROWN_UP.get(other, other)


def _with_the_breed(pet, breed):
    """The record, with the breed the line named kept beside the kind of animal it is.

    The store compares one pet with another by `animal` ("my dog" and "my greyhound" are the same
    dog), so the kind is what goes there; the breed is what lets a reply say the word they used.
    """
    if breed:
        pet["breed"] = breed
    return pet


def _pets(text, question=False):
    """The animals a line introduces, with the names it gives them.

    A question names no pet: "what is my dog called?" asks, and storing a second, nameless "dog"
    from it would make the recall read "dog and dog". A question gives no name either: the
    lowercase "again" in "what's my dog called again?" is not a name.
    """
    theirs = _someone_elses(text)
    names = [(_name_at(match), _with_title(match)) for match in PET_NAME.finditer(text)]
    names += [(_name_at(match), _with_title(match)) for match in PET_VERB_NAME.finditer(text)
              if _a_name_given_by_the_verb(match.group("name"))
              and (match.group("whose") or "").lower() not in NOT_THEIR_DETERMINER]
    names += [(match.start(1), match.group(1)) for match in PET_PRONOUN_NAME.finditer(text)
              if _a_name_given_by_the_verb(match.group(1))]
    names += [found for found in _names_before_a_fact(text)
              if found[1] not in [name for _, name in names]]
    names += [(_name_at(match), _with_title(match)) for match in PET_IS_NAME.finditer(text)
              if _with_title(match) not in [name for _, name in names]]
    names += [(match.start("name"), _with_title(match))
              for match in PET_POSSESSIVE_NAME.finditer(text)
              if _a_name_for_the_pet(match.group("name"), strict_ly=False)
              and _with_title(match) not in [name for _, name in names]]
    names += [(match.start(1), match.group(1)) for match in PET_APPOSITIVE.finditer(text)
              if _names_it_aside(match, text)]
    # "called again" in "what's my dog called again?" names no pet: a name is a word of its own,
    # not the grammar of the ask
    names = [(position, name) for position, name in names if name.lower() not in NOT_A_NAME]
    names.sort()
    if question:
        names = [(position, name) for position, name in names if name[:1].isupper()]
    # A name belongs to the animal it follows and comes before the next one: "a dog and a cat
    # called Tom" names the cat, not the dog. Another person's pet is not the user's: "my
    # neighbour has a dog called Rex" says nothing about what the user has.
    # The name just given is not another animal: "my cat is called Fish" names one cat, and
    # reading "Fish" as a second one left the cat unnamed, so "what is my cat called" answered
    # "you haven't told me a name for your cat yet" about a cat the line had just named.
    named_at = {position for position, _ in names}
    animals = [[match.start(), match.end(), match.group(1).lower(), ""]
               for match in PETS.finditer(text)
               if not any(start <= match.start() < stop for start, stop in theirs)
               and match.start() not in named_at]
    # A breed is the animal it is. "we got a rescue greyhound last week" told the store nothing,
    # so "what pets do i have" answered "You haven't told me about a pet yet" about a dog the
    # person had just described, and "my labrador is 4" lost the age for the same reason: the
    # pet reader only knew the animal's own word. The breed is kept beside the kind, so the
    # store compares `animal` with `animal` as it always did and can still say the word they used.
    one_of_the_group = set()  # starts where the breed named one animal of a group
    for match in breeds.BREED_RE.finditer(text):
        if any(start <= match.start() < stop for start, stop in theirs):
            continue
        if match.start() in named_at:
            continue
        breed = breeds.the_breed_named(match.group(0))
        kind = breeds.BREED_KIND.get(breed, "")
        if not kind:
            continue
        # The word has to be said as an animal: "im husky" is a voice, and the store filed a dog
        # for it and answered "A husky - is it good company?" about the person.
        if not breeds.a_frame_before(text, match.start()):
            continue
        # "the greyhound bus is late", "greyhound racing on saturday": the breed names something
        # else here, and the word after it is what says so.
        after = re.match(r"[\s-]*([a-z]+)", text[match.end():match.end() + 24])
        if after and after.group(1).lower() in breeds.NOT_A_CREATURE_NEXT:
            continue
        # A breed said beside the animal's own word is the same animal: "my cat, a tabby, is 3",
        # "my dog is called miss and she is a spaniel" and "we have two dogs, a lab and a terrier"
        # each describe one pet, and reading the breed as a second animal left the store holding
        # two records and the reply counting two where the person had said one.
        beside = [entry for entry in animals if _the_same_animal(entry[2], kind)
                  and abs(entry[0] - match.start()) <= 40]
        if beside:
            closest = min(beside, key=lambda entry: abs(entry[0] - match.start()))
            # A breed beside a group is the breed of one of them, not of the group: "we have two
            # dogs, a lab and a terrier" was kept as two terriers, and the reply said "Two
            # terriers. Who's in charge?" about a lab and a terrier. The breed stays on the
            # record - the words were said, and the ack reads them to see the line added nothing
            # else - but it is marked as one of the group, so what is said back is the kind:
            # "two dogs". A breed said as the group itself ("we have two greyhounds") is not
            # marked, so the word they used is still the word said back.
            if not closest[3]:
                closest[3] = breed
                if _count_before(text, closest[0]) > 1:
                    one_of_the_group.add(closest[0])
            continue
        animals.append([match.start(), match.end(), kind, breed])
    animals.sort()
    pets = []
    # One animal in the line is the only one a description and a figure can both be about:
    # "we have two dogs, 3 and 5" gives two ages in one clause (`_names_after`), not one.
    one_animal = len(animals) == 1
    for index, (start, end, animal, breed) in enumerate(animals):
        limit = animals[index + 1][0] if index + 1 < len(animals) else len(text)
        # "we got another cat called Max" beside a cat they already have is a second cat; the same
        # words without "another" are the cat they have, named again. Read here rather than in the
        # store, which sees only the animal and the name; bot/memory/remember decides with it.
        before = text[max(0, start - 60):start]
        second = bool(ANOTHER_ANIMAL.search(before) or ALSO_HAVE.search(before))
        # "i don't eat fish", "we had chicken for dinner": the animal is on the plate, not in the
        # house, so it is a diet and not a pet.
        if FOOD_BEFORE.search(text[max(0, start - 30):start]):
            continue
        # "i love dogs", "not keen on rabbit": a taste, not a pet ("we love our dog" is both, and
        # taste.said_about keeps the pet there because the possessive says which animal it is).
        if taste.said_about(text, start):
            continue
        if FOOD_AFTER.match(text[end:end + 30]):
            continue
        # The head of the phrase is the word after the animal, not the animal: "a fish bone"
        # is a bone, so the line says nothing about a pet. Two shapes hide here. "a fish bone",
        # "the dog bowl" is not a pet at all. "my dog food is expensive", "my cat litter costs a
        # fortune" is a pet, said through a thing of theirs: the compound is not the pet's name,
        # but the animal is still theirs, so it is kept and left unnamed rather than dropped.
        after = re.match(r"\s*([a-z]+)(.{0,40})", text[end:], re.S)
        compound_they_have = False
        if after and after.group(1).lower() in PET_COMPOUND:
            named = (THEIR_ANIMAL.search(text[max(0, start - 12):start])
                     and AFTER_A_PET.match(after.group(2)))
            if not named:
                if not THEIR_ANIMAL.search(text[max(0, start - 12):start]):
                    continue
                compound_they_have = True
        if NAME_BEFORE.search(text[max(0, start - 12):start]):
            continue
        # An animal they want, dislike or had once is not an animal they have, and a line that
        # says they have not got one adds nothing: "i dont have a cat" used to store a cat and
        # then take it back, so "what pets do i have" answered "you don't have your cat any more".
        # The record still goes out, marked, so the line can be said back to them ("Noted: you
        # don't want a dog"): bot/memory/remember keeps only the ones that are theirs.
        if _not_their_animal(text, start, end):
            # "my mum's cat is called Tom" tells us about a cat the person does not have.
            pets.append(_with_the_breed(_not_theirs(animal, text, start, end), breed))
            continue
        clause = CLAUSE_EDGE.split(text[max(0, start - 60):start])[-1]
        if (_only_wanted(text, start, end)
                or NOT_HAVE.search(clause)
                or WITHOUT_ANIMAL.search(clause)
                # "not the dog" is the same take-back as "i don't have a dog": reading it as a
                # pet left the store holding a dog the line had just taken back, and a second
                # reader then filed that dog under `pets_gone` as a loss they never had.
                or NOT_JUST.search(clause)
                # "forget the dog", "no dog": a take-back names the animal, so the line is not
                # introducing it.
                or taken_back_before(text, start)):
            pets.append(_with_the_breed(_not_theirs(animal, text, start, end), breed))
            continue
        # An animal on its way is not one in the house: "we are getting a puppy next week" is a
        # plan, and the store claiming the puppy answered "You've got a puppy" about one still
        # with its mother. It is read as theirs and marked, because the follow-ups need it ("what
        # do i need to buy first", "will they get on") and only the sentence said back changes.
        coming = _coming_home(text, start)
        count = _count_before(text, start)
        # "my cats are called tom and jerry" is two cats and two names: the plural animal is the
        # only thing that says there is more than one, and without it the second name was dropped
        # and "what are my cats called" answered "you've got a cat called tom". It says nothing
        # about how many, so the list is read for as many names as the line gives.
        plural = count < 2 and text[start:end].lower().endswith("s")
        listed = _names_after(text[end:limit], count, most=MOST_NAMES if plural else None)
        if compound_they_have:
            # "my dog food is expensive": the compound is a thing of theirs, not a name.
            listed = []
        if question:
            listed = [name for name in listed if name[:1].isupper()]
        if listed:
            pets.extend(_with_the_breed({"animal": animal, "name": name,
                                         **({"coming": True} if coming else {})}, breed)
                        for name in listed)
            for name in listed:
                if name in names:
                    names.remove(name)
            continue
        name = None
        for position, candidate in list(names):
            if end <= position < limit:
                name = candidate
                names.remove((position, candidate))
                break
        if question and not name:
            # A word after the animal in commas introduced the animal, even when the word is not
            # a name: "our dog, mate, is 4" has told us there is a dog, and dropping it makes the
            # next turn answer "what's my dog called?" with "you haven't told me about a pet".
            if PET_APPOSITIVE.search(text[start:limit]) is None:
                continue
        if not name and count > 0:
            # "i have two cats" names no animal one at a time, so the number is the only thing
            # that says how many there are. Without it "one of them died" empties the house, and
            # "we have two cats" then "sorry, 1 cat" cannot move the count down to one either:
            # a number the line really gave for that animal is kept, even when it is one.
            pet = {"animal": animal, "name": name, "count": count}
        else:
            pet = {"animal": animal, "name": name}
        if coming:
            pet["coming"] = True
        # "my dog is 5", "my dog max is 4": how old the animal is is a fact of theirs like any
        # other, so it is kept with the animal and a later "how old is max" has an answer.
        age = _pet_age(text[end:limit])
        if not age and one_animal and not pet.get("count"):
            # The figure said after what the animal is: "hes a labrador, 9", "my dog is a
            # spaniel and hes 11", "she is a tabby, 3 years". The breed line is the animal's
            # own record, and the figure that follows it belongs to the same animal - without
            # this it was filed against nobody and "what did i tell you his age was" said the
            # chat had never been told, about an age it had just been given.
            age = _pet_age_tail(text[end:limit])
        if age:
            pet["age"] = age[0]
            if age[1]:
                pet["unit"] = age[1]
        if second:
            pet["another"] = True
        if breed and start in one_of_the_group:
            pet["breed_of_one"] = True
        pets.append(_with_the_breed(pet, breed))
    return pets


# The figure a line gives for an animal right after saying what it is: "hes a labrador, 9",
# "my cat is a tabby and she is 3". The comma or the "and" is what makes it the same animal's
# age: a figure set off on its own is a new clause and could be anybody's.
PET_AGE_TAIL = re.compile(
    r"^\s*(?:is\s+(?:a|an)\s+[A-Za-z][A-Za-z'-]{1,19}\s*)?(?:,|\band\b)\s*"
    r"(?:(?:hes|shes|its|theyre|he's|she's|it's|they're|he is|she is|it is|they are)\s+)?"
    r"(?:aged?\s+)?(?P<age>\d{1,2})(?![\d.,]\d)"
    r"(?!\s*(?:kg|kilo\w*|lbs?|pounds?|stone|st|cm|inches?|inch|metres?|meters?|miles?|km|mph|"
    r"hours?|hrs?|mins?|minutes?|percent|%))"
    r"\s*(?P<unit>years?|yrs?|months?|weeks?)?\b", re.I)


def _pet_age_tail(after):
    """The age said after the animal's own description, or None: "hes a labrador, 9".

    Read only where the line gave one animal (`one_animal` in `_pets`), because with two a
    figure cannot say which one it is. `unit` is kept the way `_pet_age` keeps it, so "shes a
    tabby, 6 months" is a kitten and not a six-year-old cat.
    """
    match = PET_AGE_TAIL.match(str(after or ""))
    if not match:
        return None
    age = int(match.group("age"))
    if not 0 < age <= 40:
        return None
    unit = str(match.group("unit") or "").lower()
    return age, ("months" if unit.startswith("month")
                 else "weeks" if unit.startswith("week") else "")


# The figure a line gives for an animal's age: "is 5", "max was 12", "is 3 years old". A figure
# with a weight or a length after it is a measurement ("my dog is 5 kilos"), not an age, and the
# words before the verb are at most the name the line gave the animal.
PET_AGE = re.compile(
    r"^\s*(?:[A-Za-z][A-Za-z'-]{1,19}\s+)?(?:is|was|are|were)\s+(?P<age>\d{1,2})"
    r"(?![\d.,]\d)"
    r"(?!\s*(?:kg|kilo\w*|lbs?|pounds?|stone|st|cm|inches?|inch|metres?|meters?|miles?|km|mph|"
    r"hours?|hrs?|mins?|minutes?|percent|%))"
    r"\s*(?P<unit>years?|yrs?|months?|weeks?)?\b", re.I)


# The same fact said with no verb at all: "hes a labrador, 9 weeks old", "a kitten, 12 weeks".
# The figure is still the animal's age, and without it "how old is the puppy" had nothing to
# answer from although the person had just said how old it was. A unit word is required here,
# because a bare number after the animal ("two cats, one dog") is a count, not an age.
PET_AGE_BARE = re.compile(
    r"^\s*[,;:]?\s*(?:aged\s+)?(?P<age>\d{1,2})\s*(?P<unit>years?|yrs?|months?|weeks?)"
    r"(?:\s*old)?\b", re.I)


def _pet_age(rest):
    """How old the animal is, when the words right after it say so, or None.

    A kitten or a puppy is often given in months, so the unit is kept: "4 months" is an age of
    four months, and reading it as four years says something about the animal that is not true.
    """
    match = PET_AGE.match(rest) or PET_AGE_BARE.match(rest)
    if not match:
        return None
    age = int(match.group("age"))
    if not 0 < age <= 30:
        return None
    unit = (match.group("unit") or "").lower()
    if unit.startswith("month"):
        unit = "months"
    elif unit.startswith("week"):
        unit = "weeks"
    else:
        unit = ""
    return age, unit


# Words people use to address the person they are talking to, not to name an animal: "i got a
# dog, mate" names the dog nothing. The list leaves out the words people do give pets (buddy,
# honey, chief), so a name still lands.
ADDRESSING = frozenset("""
mate matey mates pal fella feller fellas chum cocker bruv bro brother sis sister
love lovey duck ducks petal hun hon dear dearie sunshine lad lass guys folks friend
son daughter dad mum mam mom missus mister sir madam flower
""".split())


def is_addressing(word):
    """Whether a word is how someone addresses a person ("mate", "love"), not a pet's name."""
    return isinstance(word, str) and word.lower() in ADDRESSING


def _names_it_aside(match, text):
    """Whether the word after the animal in commas names it.

    A word that is not a name at all does not ("our dog, mate, is 4"), but one the person wrote
    with a capital and then carried the sentence on with does: "our cat, Flower, is old" is a cat
    called Flower, while "i got a dog, Mate" ends the line and is someone being friendly.
    """
    word = match.group(1)
    if not _not_a_name(word):
        return True
    return word[:1].isupper() and bool(re.search(r"[A-Za-z]", text[match.end():]))


# The words that stand where a name can stand and are certainly not one: "my mum called me
# yesterday", "my sister named her baby after me", "my son is called after his dad".
NOT_A_NAME_EITHER = frozenset((
    "me", "her", "him", "us", "them", "you", "my", "your", "his", "hers", "its", "it", "this",
    "that", "these", "those", "who", "what", "which", "someone", "somebody", "anyone", "anybody",
    "everyone", "everybody", "nobody", "something", "anything", "nothing", "after", "for", "by",
    "with", "from", "up", "out", "back", "there", "here", "then", "not", "never", "still",
    "also", "too", "either", "both", "all",
))


# A describing word is not a name: "my mum is amazing" is a compliment, and "Your mum is called
# Amazing" puts a word in the person's mouth. The test is the shape of the word rather than a
# list of every adjective - the endings no name carries (-ing, -ous, -ful, -less, -ness, -able,
# -ible, -ity, -tion, -sion) plus -ed, which only Fred, Ned, Ted, Ed and Jed keep - because a
# person's name is the one word in the line that nothing else in the language explains.
DESCRIBING_ENDS = ("ing", "ous", "ful", "less", "ness", "able", "ible", "ity", "ation",
                   "ition", "sion")


# The everyday describing words with no ending to go on: "my dad is stubborn", "my sister is
# overweight". Words ending in -y are here rather than in the endings above, because Daisy, Lucy
# and Poppy are names and a -y means nothing on its own.
# A relationship and a shape, and the two comparisons: "im taken" is a relationship rather
# than an introduction, and "im best at maths" answered "Nice to meet you, Best" too.
DESCRIBING_WORDS = frozenset("""
clever stubborn overweight underweight thin tall short fat skinny slim lazy happy sad funny angry
hungry thirsty pretty ugly smelly messy noisy silly busy cheeky grumpy sleepy cranky dizzy clumsy
greedy greedy wealthy healthy rocky risky shaky steep bumpy itchy sweaty queasy tipsy
nosey spoiled bratty mardy stroppy sulky clingy fit unfit taken best worst
""".split()) | NOT_A_NAME_DESCRIBING


# -ed is an adjective's ending too, and these are the names it would otherwise swallow.
ED_NAMES = frozenset("fred ed ned ted jed".split())


# The words a line says *about* a name rather than a name: "my daughters name" ends in the word
# itself, and filed as one the bot tells the person their daughter is called Name. Nothing in
# the line names anybody.
NOT_A_NAME_WORD = frozenset("""name names nickname called known ages age""".split())


# Every word the understanding lane keeps as ordinary English, so the store can tell a word with
# a job in the sentence ("its complicated", "its the plumber") from a word that only has the job
# of being somebody's name. Read once, because it is asked on every correction of a name.
COMMON_WORDS = frozenset(lexicon.COMMON.split()) | frozenset(lexicon.CORE_WORDS) | lexicon.A_STATE


# The endings a describing word wears and a name rarely does: "complicated", "amazing", "real".
NOT_A_NAME_ENDINGS = ("ed", "ing", "ous", "ful", "less", "ish", "able", "ible", "ive", "est", "ly",
                      "al", "ic")


# A contraction typed without its apostrophe ("isnt", "arent", "didnt"): the stem is a verb the
# lexicon knows, which is what tells it apart from a name that happens to end in the same letters.
NEGATED_VERB = re.compile(r"^(?P<stem>[a-z]{2,})n['\u2019]?t$")


def is_a_contraction(word):
    """Whether a word is a verb with its "not" written on: "isnt", "arent", "didnt".

    "my son isnt" filed a person called Isnt beside the son - "whats my sons name" answered "Your
    son is called Isnt." - because the word after the relation is read as the name it gives. A
    verb with its "not" written on is one of the things that word can never be.
    """
    low = str(word or "").strip().strip(".,!?;:'\"").lower().replace("\u2019", "'")
    match = NEGATED_VERB.match(low)
    if not match:
        return False
    stem = match.group("stem")
    return stem in normalize.LEXICON or stem + "e" in normalize.LEXICON


def _not_a_name(word, strict_ly=True):
    """Whether a word after the comma is one of the things people say about a pet, not a name.

    A word ending in -ly is an adverb far more often than a name ("our dog, friendly, is 4"), so
    it is turned down. That rule is only safe where the line gives no other sign that the word is
    a name: in "my daughter Emily is 6" the relation and the verb in front of it already say so,
    and Emily, Molly, Kelly and Lily are names. `strict_ly=False` is for those shaped lines.
    """
    low = word.lower()
    if is_addressing(word) or low in NOT_A_PET_NAME or low in NOT_NAMES or low in NOT_NAMES_EXTRA:
        return True
    if low in NOT_A_NAME_EITHER:
        return True  # a pronoun or a preposition is never somebody's name, whatever it follows
    if low in PET_ANIMALS or not re.search(r"[aeiouy]", low):
        return True
    if strict_ly and low.endswith("ly") and len(low) > 4:
        return True
    if _a_word_not_a_name(low):
        # "her name is blonde": a hair colour, a number written out or a state is how somebody
        # is, not what they are called, and every reader of a name asks this guard.
        return True
    return bool(re.fullmatch(r"\d+", low))
