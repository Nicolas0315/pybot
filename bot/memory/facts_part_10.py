"""Part 10 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re


from .named import the_name_in
from . import taste
from .facts_part_01 import (
    ALLERGEN_PLURALS, ALLERGY, CONTRAST, DENIAL_OF, DIET_BACK, DIET_NAMES, DIET_OFF, EVERYTHING,
    NO_PETS, PETS, PET_PRONOUN, CANNOT_EAT, NOT_AN_ALLERGEN, X_ALLERGY, ANIMALS, OTHER_DIET,
    CLAUSE_EDGE, SOBER_WORDS, DAYS, MONTHS, NOT_A_NAME, NOT_A_NAME_STATE, NOT_A_NAME_THING, AGE,
    ALL_I_CAN_DO, BARE_BUDGET, BUDGET, BUDGET_ASKED, BUDGET_THOUGHT, CEILING_BUDGET, CONDITION,
    DIET_BARE, DIET_NAMED, DIET_UNDERWAY, HOME_LOOSE, INCOME, INCOME_A_YEAR, INCOME_BARE,
    INCOME_RATE, INTENDED_SPEND, MEAT, NOT_PLACES, NO_EAT_QUALIFIER, NO_MEAT, ONLY_HAVE,
    PLACE_VERBS, SPEND_BUDGET, SPEND_BUDGET_NOW, SPEND_FOR, STRETCH_BUDGET, THE_THING_MAY_COST,
    VEGETARIAN,
)
from .facts_part_02 import (
    _the_food_named, _A_WORD_FOR_A_PERSON, RELATIONS, BIRTHDAY, INFINITIVE_FRAME, MY_AGE, PLAN,
    WEIGH, WEIGH_IM, WEIGH_MY, _a_birthday_date, _a_way_of_eating_said_with_a_verb, _fact_value,
    _how_tall, _the_numbers_in_words, _weight_unit, vague_budget,
)
from .facts_part_03 import (
    JOB_WANTED, AMOUNT_CORRECTION, AMOUNT_CORRECTION_BARE, AMOUNT_WISH, CLOCK_PREFERRED,
    COPULA_SPLIT, CORRECTION, CORRECTION_BARE, CORRECTION_BARE_NO, CORRECTION_CLOCK,
    CORRECTION_DATE, CORRECTION_DATE_GOING, CORRECTION_GOING_MOVED, CORRECTION_HEDGED,
    CORRECTION_MAKE, CORRECTION_MARK, CORRECTION_NOT, CORRECTION_NOT_PAIR, CORRECTION_NOT_TO,
    CORRECTION_NUMBER_PAIR, CORRECTION_PAIR, CORRECTION_SAID, CORRECT_FROM_MARK, DENIAL_OF_A_VALUE,
    FUTURE, JOB_STOP, NOT_A_DAY, NO_THEN_A_THING_NAMED, RETRACT, _FAREWELL, _GOT_A, _GOT_TO,
    _a_day_taken_back, _a_moved_time, a_name_is_taken_back, a_value,
)
from .facts_part_04 import (
    _finish, _tidy, CHANGED_WORK, WORK_NOW, _date_change, _the_drink_they_do_not_take,
    _the_value_alone, _tidy_apart, no_tone,
)
from .facts_part_05 import (
    _allergy_items, _merge_pets, _names_a_relative, _one_of_several, _only_pet, _own_in_denial,
    _the_one_they_have, denied_before, not_had, stated_not_asked, _trim_filler,
    A_PRONOUN_NOT_A_NAME, NOT_A_PERSON_WORD, _a_person_word, CLAUSE_BREAK, OTHER_NOUNS,
    ALLERGY_STOP, _QUANTITY_WORDS, _born_place, _car, _from_place, _places,
)
from .facts_part_06 import (
    NOT_DIET, OTHER_NO_DRINK, _somebody, DIET_GROUP, DIET_STOP, CONDITION_AS_A_WORD,
    OTHER_CONDITION, OTHER_JOB, _ages_held, _other_states, _own_states,
)
from .facts_part_07 import (
    _someone_elses, subject, OTHER_JOB_AS, OTHER_JOB_NAMED, _name_after_a_title, _not_a_name,
    _the_job_phrase, _may_be_a_name, _the_person_without_a_relation, _a_relations_name, _owns,
    _pets,
)
from .facts_part_08 import (
    _a_plan_has_a_thing, _appointment, _asks_about_the_plan, _dated_plans, _name, _plan_text,
    _plan_verb,
)
from .facts_part_09 import (
    _the_person_the_pronoun_is, _the_pronoun, _a_years_pay, _is_only_the_take_back, _job_and_city,
    _other_ages, _paid_by_a_period, _people, _relation_facts, kid_count,
)


def denials(text, own=None):
    """The facts a line says the person does *not* have, in the shape extract() keeps them.

    "im not coeliac" after "im coeliac", "i'm no longer vegetarian": the store can only stop
    planning around a thing if it hears which thing is being taken back. A pet goes the same way,
    but only on possession - see `not_had`. `own` is the pets the store already holds, so a
    take-back can name the animal by the name the person gave it. A denial about somebody else
    comes back under "theirs" (a list of {"who", "allergies"}), because it takes the item off
    that person's list rather than the user's.
    """
    said = str(text or "")
    denied = {}
    # A take-back about somebody else: "he isnt allergic to nuts" one line after "my son is
    # allergic to nuts" is the same denial, and the store can only stop cooking around it if it
    # hears whose list the nuts are coming off. Kept under "theirs", which is no fact key: the
    # store takes each item off the record it holds for that person and says so.
    for match in ALLERGY.finditer(said):
        if not denied_before(said, match.start()):
            continue
        kind, who = subject(said, match.start())
        if kind != "other":
            continue
        person = _a_person(said, match.end(), who)
        items = [ALLERGEN_PLURALS.get(item, item) for item in _allergy_items(match.group(1))]
        if not person or not items:
            continue
        entry = next((seen for seen in denied.setdefault("theirs", [])
                      if _same_person(seen, person)), None)
        if entry is None:
            entry = dict(person, allergies=[])
            denied["theirs"].append(entry)
        entry["allergies"].extend(item for item in items if item not in entry["allergies"])
    for match in CONTRAST.finditer(said):
        items = _allergy_items(match.group("old"))
        for item in items:
            name = ALLERGEN_PLURALS.get(item, item)
            if name not in denied.setdefault("allergies", []):
                denied["allergies"].append(name)
    for match in DENIAL_OF.finditer(said):
        if match.group("food"):
            items = _allergy_items(re.sub(r"^allergic to\s+", "", match.group("food"), flags=re.I))
            if items:
                denied.setdefault("allergies", []).extend(
                    item for item in items if item not in denied.get("allergies", []))
            continue
        if match.group("condition"):
            denied["condition"] = match.group("condition").lower()
            continue
        if match.group("diet"):
            denied["diet"] = DIET_NAMES.get(match.group("diet").lower(), match.group("diet").lower())
    for match in DIET_OFF.finditer(said):
        plan = next((match.group(name) for name in ("plan", "off", "gone", "quit")
                     if match.group(name)), "")
        if not plan:
            continue
        plan = "-".join(plan.lower().replace("-", " ").split())
        # "im on a diet" is kept as "on a diet": the take-back has to be the value the store
        # holds, or `forget` finds nothing to take out.
        denied["diet"] = DIET_NAMES.get(plan, "on a diet" if plan.startswith("diet") else plan)
    for match in DIET_BACK.finditer(said):
        food = _the_food_named(match.group("back") or match.group("eat") or "")
        if food:
            denied["diet"] = food
    if NO_PETS.search(said):
        denied["pets"] = [EVERYTHING]
    animals = []
    others = _someone_elses(said)
    for match in PETS.finditer(said):
        if not not_had(said, match.start()):
            continue
        if any(start <= match.start() < stop for start, stop in others):
            continue  # someone else's pet is not the user's to take back
        animal = match.group(1).lower()
        if animal not in animals:
            animals.append(animal)
    if not animals:
        # "we dont have him any more": the animal is a pronoun, and the line named it earlier.
        for match in PET_PRONOUN.finditer(said):
            if not not_had(said, match.start()):
                continue
            pointed = _the_one_they_have(said, match, own)
            if not pointed and not _names_a_relative(said):
                pointed = _only_pet(own)
            for animal in pointed:
                if animal not in animals:
                    animals.append(animal)
            break
    if not animals:
        animals = _own_in_denial(said, own)
    if animals and denied.get("pets") != [EVERYTHING]:
        denied["pets"] = _merge_pets(denied.get("pets", []), _one_of_several(animals, said, own))
    return denied


def _allergies(text):
    """(the user's allergies, the others': [{"who", "allergies"}])."""
    mine, others = [], []
    for pattern in (ALLERGY, CANNOT_EAT, X_ALLERGY):
        for match in pattern.finditer(text):
            if pattern is not CANNOT_EAT and denied_before(text, match.start()):
                continue  # "im not allergic to nuts" is the opposite fact
            if pattern is X_ALLERGY and match.group(1).lower() in NOT_AN_ALLERGEN:
                continue  # "why do we get allergies" names no allergy of theirs
            items = _allergy_items(match.group(1))
            if not items:
                continue
            if pattern is X_ALLERGY:
                items = [ALLERGEN_PLURALS.get(item, item) for item in items]
            kind, who = subject(text, match.start())
            if kind != "other":
                mine.extend(item for item in items if item not in mine)
                continue
            person = _a_person(text, match.end(), who)
            if not person:
                continue  # somebody the line never names and never points at either
            entry = next((seen for seen in others if _same_person(seen, person)), None)
            if entry is None:
                entry = dict(person, allergies=[])
                others.append(entry)
            entry["allergies"].extend(item for item in items if item not in entry["allergies"])
    return mine, others


def _other_no_drink(text):
    """Who else in the line does not drink, as the person the store keeps: [{...}], or []."""
    found = []
    text = stated_not_asked(text)
    if not text:
        return found
    for match in OTHER_NO_DRINK.finditer(text):
        if NOT_DIET.search(match.group(0)):
            continue
        kind, who = subject(text, match.start("subj"))
        if kind == "":
            # "shes teetotal" is not a pronoun the clause reader knows, but it is still someone
            # else: the subject is the start of this match.
            kind, who = _somebody(match.group("subj"))
        if kind != "other" or who in ANIMALS or who in ("i", "we"):
            continue
        person = _a_person(text, match.end(), who)
        if not person:
            continue
        entry = next((seen for seen in found if _same_person(seen, person)), None)
        if entry is None:
            entry = dict(person)
            found.append(entry)
        entry.setdefault("diet", "no alcohol")
    return found


def _other_diets(text):
    """What someone else in the line eats: [{"who": "mum", "diet": "no meat"}].

    Only other people: the user's own diet is VEGETARIAN and NO_MEAT above, so "i dont eat meat"
    is still their no_meat and "she doesnt eat meat" is hers. A line that names nobody in
    particular ("they dont eat meat") keeps who "" and is still merged with the last person, the
    same way a bare "hes allergic to nuts" is.
    """
    found = []
    text = stated_not_asked(text)
    if not text:
        return found
    # "my son cant eat nuts" is his allergy, not a diet: the allergy patterns above already have
    # it, and keeping both would say the same thing back twice.
    claimed = [span for pattern in (ALLERGY, CANNOT_EAT, X_ALLERGY)
               for span in (m.span() for m in pattern.finditer(text))]
    for match in OTHER_DIET.finditer(text):
        if any(start < match.end() and match.start() < end for start, end in claimed):
            continue
        word, food = match.group("word"), match.group("food")
        free = match.group("free")
        at = match.start("word") if word else (match.start("free") if free
                                               else match.start("food"))
        kind, who = subject(text, at)
        if kind == "":
            # "shes vegan" is not a pronoun the clause reader knows, but it is still someone
            # else: the subject is the start of this match, not something before it.
            kind, who = _somebody(match.group("subj"))
        if kind != "other" or who in ANIMALS:
            continue
        if NOT_DIET.search(match.group(0)):
            continue
        if free or word:
            # The diet is kept the way the person's own diet is kept, so "my wife is gluten free"
            # and "im gluten free" are the same fact in the same words: a plan said with a
            # space is the same plan as the one said with a hyphen.
            diet = "-".join((free or word).lower().replace("-", " ").split())
        else:
            food = _trim_filler(_finish(food or ""))
            if not food or set(food.split()) & DIET_STOP:
                continue
            # "he wont eat vegetables" is a fussy eater, not a way of eating: a diet names a
            # whole food group, so the vegetable he refused at dinner is not his diet for life.
            if not set(food.split()) & DIET_GROUP:
                continue
            diet = "no " + food
        person = _a_person(text, match.end(), who)
        if not person:
            continue
        entry = next((seen for seen in found if _same_person(seen, person)), None)
        if entry is None:
            entry = dict(person)
            found.append(entry)
        entry.setdefault("diet", diet)
    # "my mate is teetotal" is that person's limit, and it is kept in the same place and the same
    # words as their diet: the store says it back as "your mate doesn't drink alcohol".
    for entry in _other_no_drink(text):
        person = next((seen for seen in found if _same_person(seen, entry)), None)
        if person is None:
            found.append(entry)
        else:
            person.setdefault("diet", entry["diet"])
    return found


def _other_conditions(text):
    """What somebody else has: [{"who": "mum", "condition": "diabetic"}].

    Only other people, and only the condition: "my son is coeliac and cant eat gluten" is his
    condition here and his allergy there, and the two are kept apart the same way a diet and an
    allergy are.
    """
    found = []
    text = stated_not_asked(text)
    if not text:
        return found
    for match in OTHER_CONDITION.finditer(text):
        if NOT_DIET.search(match.group(0)):
            # "he isnt diabetic any more" is a condition taken back, not one to keep.
            continue
        kind, who = subject(text, match.start("cond"))
        if kind == "":
            kind, who = _somebody(match.group("subj"))
        if kind != "other" or who in ANIMALS:
            continue
        cond = " ".join(match.group("cond").lower().split())
        cond = CONDITION_AS_A_WORD.get(cond, cond)
        person = _a_person(text, match.end(), who)
        if not person:
            continue
        entry = next((seen for seen in found if _same_person(seen, person)), None)
        if entry is None:
            entry = dict(person)
            found.append(entry)
        entry.setdefault("condition", cond)
    return found


def _other_jobs(text):
    """What somebody else does: [{"who": "sister", "job": "nurse"}].

    Only other people. "i'm a nurse" is the speaker's own job and stays the store's `job` fact,
    and a line about somebody with no person in it ("she's a nurse" with nobody named before
    it) keeps the pronoun, so the store can put it on the last person it heard about.
    """
    found = []
    for pattern, place_job in ((OTHER_JOB_AS, True), (OTHER_JOB, False), (OTHER_JOB_NAMED, False)):
        for match in pattern.finditer(text):
            at = match.start("job")
            kind, who = subject(text, at)
            if kind != "other":
                continue
            if JOB_WANTED.search(CLAUSE_EDGE.split(text[:at])[-1]):
                # "my brother wants to be a chef" is not his job, and neither is one he is
                # training for: only work the line says somebody does is kept.
                continue
            job = _the_job_phrase(match.group("job"), place_job)
            if not job or job in SOBER_WORDS:
                # "my mum is a teetotaller" is a limit of hers, read above, not what she does.
                continue
            person = dict(_a_person(text, at, who))
            if not person:
                continue
            said = (match.groupdict().get("name") or "").strip()
            # A word that is not a name is not one here either ("my sister in law is a nurse"
            # names a relation, not a woman called In), and a name the chat is given is kept on
            # her entry so a later line can ask about her by it.
            if (said and not _not_a_name(said, strict_ly=False)
                    and _name_after_a_title(said)
                    and said.lower() not in _A_WORD_FOR_A_PERSON):
                person["name"] = _tidy(said)
            entry = next((seen for seen in found if _same_person(seen, person)), None)
            if entry is None:
                entry = dict(person)
                found.append(entry)
            entry.setdefault("job", job)
    return found


# A name that opens a clause with the verb after it: "tom is allergic to nuts" says nothing about
# the person typing, and the fact is Tom's. Only a name that opens the clause counts - "the bag tom
# left is heavy" says nothing about anybody's allergy even where it sits in front of a verb.
NAME_THEN_THE_VERB = re.compile(
    r"^\W*(?:(?:and|but|so|then|also|oh|ok|okay|well|now|btw|hey|hi|quick)\W+)?"
    r"(?P<name>[A-Za-z][A-Za-z'\-]{1,19})\s+(?:is|was|has|had|isnt|wasnt|hasnt|cant|cannot|"
    r"doesnt|dont|didnt|never|only|gets|got|became)\b", re.I)


def _a_name_opening_the_clause(clause):
    """The name a clause opens with, or "" - "tom" in "tom is allergic to nuts"."""
    found = NAME_THEN_THE_VERB.match(clause or "")
    if not found:
        return ""
    name = found.group("name")
    low = _a_person_word(name)
    if low in NOT_A_PERSON_WORD or low in RELATIONS or low in DIET_GROUP \
            or low in A_PRONOUN_NOT_A_NAME:
        return ""
    if not (_may_be_a_name(name) and _name_after_a_title(name)):
        return ""
    return name


def _the_name_in_front(text, pos):
    """The name of the person the clause ending at pos names, or "".

    "tom is allergic to nuts" names Tom and nobody else, and "my son tom is allergic to nuts"
    names the son, who is Tom - the relation is the store's word for him, so the name is kept
    beside it rather than instead of it.
    """
    start = 0
    for match in CLAUSE_BREAK.finditer(text, 0, pos):
        start = match.end()
    clause = text[start:pos]
    who, name = _the_person_without_a_relation(clause)
    if name and not who:
        return name
    if not who:
        opening = _a_name_opening_the_clause(clause)
        if opening:
            return opening
    if who:
        # The relation is the subject; a name after it ("my son tom") is who that person is.
        found = re.search(r"\b(?:" + "|".join(sorted(OTHER_NOUNS, key=len, reverse=True))
                          + r")(?:\s+in\s+laws?)?s?\s+(?P<name>[A-Za-z][A-Za-z'\-]{1,19})\s*$",
                          clause, re.I)
        if found:
            name = found.group("name")
            low = name.lower().strip("'")
            if (low not in NOT_A_PERSON_WORD and low not in RELATIONS
                    and _may_be_a_name(name) and _name_after_a_title(name)):
                return name
    return ""


def _a_person(text, pos, who):
    """The person a fact about somebody else belongs to: {"who": "mum"}, {"name": "Tom"} or
    {"pronoun": "she"}.

    A line can point at somebody without naming them ("shes allergic to nuts", "hes vegetarian
    now"), and that person is still a person: a fact filed against nobody is an entry whose
    "who" is missing, and the next reading of the same line stumbled over it. When the line named
    one person before the pronoun, that person is who it is. {} means the line neither names
    anybody nor points at anybody.
    """
    if who:
        return {"who": who}
    # A person named and nothing else: "tom is allergic to nuts" is Tom's allergy, and there is
    # no relation word to file it under, so the entry carries the name the way "ada is 8" does.
    named = _the_name_in_front(text, pos)
    if named:
        return {"name": named}
    pronoun = _the_pronoun(text, pos)
    if not pronoun:
        return {}
    person = _the_person_the_pronoun_is(text, pos, pronoun)
    if person:
        return {"who": person}
    return {"pronoun": pronoun}


def _same_person(seen, entry):
    """Whether two readings of one line are about the same person.

    A reading that names the relation ("my son") and one that only has the pronoun ("she is 7")
    are the same person only when the line named nobody else, so a named reading matches another
    reading with that name and a pronoun reading matches the same pronoun. Merging a "she" into
    "my son" would put somebody else's birthday on the son.
    """
    who = seen.get("who") or ""
    other = entry.get("who") or ""
    if who or other:
        # Two children named in one breath ("my kids are ada 7 and sam 4") share the word in
        # front of them, so the word alone cannot tell them apart: the name is what says which
        # child an age belongs to, and two named children are never folded into one. A reading
        # with no name of its own is the same person as one that has a name - "my son is called
        # tom" then "my son is allergic to nuts" is one boy, and the name read on its own line
        # is how the allergy entry learns who he is.
        mine = str(seen.get("name") or "").lower()
        theirs = str(entry.get("name") or "").lower()
        return who == other and (not mine or not theirs or mine == theirs)
    return bool(seen.get("pronoun")) and seen.get("pronoun") == entry.get("pronoun")


# A figure said with a name and nothing else is about the person the chat knows by that name.
# "my kids are ada 7 and sam 4" and then "ada is 8" is Ada's age moved, and "no, sam is 5" is
# Sam's; without this the store kept 7 and 4 while the bot had already said "Ada is 8, good to
# know". The line names no relation, so the entry carries the name and no "who", and the store
# fills that in from the names it holds - a name the chat was never given stays nobody's.
NAME_AND_A_FIGURE = re.compile(
    r"^\W*(?:(?:no|nope|sorry|actually|wait|hold on|correction|i mean|and|but|so|oh)\W+)*"
    r"(?P<name>[A-Za-z][a-z'-]{1,19})(?:'s| is| was)\s+(?:now\s+|already\s+|actually\s+)?"
    r"(?P<age>\d{1,3})(?:\s*(?:years?|yrs?)(?:\s+old)?)?(?:\s+(?:now|already|today))?\W*$", re.I)


# The words a figure can be said with that are not names: "it is 8", "there is 8 left". The
# store also has to hold a person of that name, so this is the second of two gates, not the only
# one.
NOT_A_NAME_FIGURE = frozenset("""i you he she it we they there that this here what who which
the a an my your his her our their its mine yours hers ours theirs and but so now then just only
still really also too very time day week month year morning evening night today tomorrow
yesterday half""".split())


def _a_name_and_a_figure(text):
    """{"name": "Ada", "age": 8} for "ada is 8", "no sam is 5", "ada's 8 now" - or None.

    A whole line only, so "ada is 8 and sam is 4" is left to the relation readers and a clause
    inside a longer sentence is not taken for a fact about anybody.
    """
    match = NAME_AND_A_FIGURE.match(" ".join(str(text or "").split()))
    if not match:
        return None
    name = match.group("name")
    low = name.lower()
    if (low in NOT_A_NAME_FIGURE or low in NOT_A_NAME or low in NOT_A_NAME_THING
            or low in NOT_A_NAME_STATE
            or low in MONTHS or low in DAYS):
        return None
    age = int(match.group("age"))
    if not 0 < age <= 120:
        return None
    # The name is said back the way a name is written - "ada" is Ada - but a name the person
    # wrote with an awkward capital is left as they typed it.
    shown = name[:1].upper() + name[1:]
    return {"name": shown, "age": age}


# Where it hurts: the part of the body a line names, and the side or the place on it.
# "its on the outside of the knee", "my left shoulder is killing me", "the pain is in my lower
# back", "i hurt my ankle yesterday". A closed vocabulary, because a part of the body is not a
# word the line can invent, and a line that names one of these with nothing the matter with it
# ("my knee is fine") files nothing.
BODY_PARTS = ("knee", "knees", "back", "shoulder", "shoulders", "hip", "hips", "ankle", "ankles",
              "foot", "feet", "heel", "heels", "calf", "calves", "shin", "shins", "thigh",
              "thighs", "hamstring", "hamstrings", "wrist", "wrists", "elbow", "elbows", "hand",
              "hands", "finger", "fingers", "thumb", "neck", "head", "chest", "stomach", "tummy",
              "tooth", "teeth", "ear", "ears", "eye", "eyes", "arm", "arms", "leg", "legs", "toe",
              "toes", "jaw", "rib", "ribs", "groin", "abdomen", "spine", "tailbone", "collarbone",
              "achilles", "quad", "quads", "glute", "glutes", "arch")


BODY_PART = re.compile(r"\b(" + "|".join(BODY_PARTS) + r")\b", re.I)


BODY_HURTS = re.compile(r"\b(?:hurt|hurts|hurting|sore|ache|aches|aching|achy|pain|painful|"
                        r"injur\w*|twinge|stiff|swollen|swelling|niggle|flare[sd] up|"
                        r"killing me|playing up)\b", re.I)


BODY_LATERAL = re.compile(r"\b(left|right|both)\s+(?:(?:outer|inner|lower|upper|front|back)\s+)?"
                          r"(?:" + "|".join(BODY_PARTS) + r")\b", re.I)


BODY_PLACE = re.compile(r"\b(?:on|in|at|to|round|around)\s+(?:the|my|his|her|their|its)\s+"
                        r"(outside|inside|front|lower|upper|top|bottom|inner|outer)\b", re.I)


# The people a body part can belong to instead of them: "my mum has a sore hip", "my son hurt his
# arm", "my daughter has a sore knee" are how people talk about a parent or a child. A part with
# one of these in front of it is that person's, and a part said with "his", "her", "their" or
# "its" is not theirs at all.
SOMEONE_ELSE = re.compile(r"\b(?:my|our|the)\s+(?:(?:little|older|youngest|eldest|baby|big|"
                          r"grown[- ]up|step)\s+)?(?:son|sons|daughter|daughters|child|children|"
                          r"kid|kids|boy|boys|girl|girls|baby|babies|toddler|mum|mums|mom|mother|"
                          r"dad|dads|father|husband|wife|partner|ex|boyfriend|girlfriend|brother|"
                          r"brothers|sister|sisters|friend|friends|mate|mates|nephew|niece|cousin|"
                          r"grandma|grandad|granny|gran|nan|nanna|aunt|aunty|uncle|in-?law|"
                          r"dog|cat|puppy|kitten|patient|client|customer|colleague|boss)\b"
                          r"(?:'s|s')?", re.I)


# A part handed to another body: "my son hurt his arm". The name is its own because `NOT_THEIRS`
# above is the pet reader's ("i dont want a dog"), and a second constant of that name would take
# the first one's place for every reader loaded after this line.
A_PART_HANDED_OVER = re.compile(r"\b(?:his|her|their|its)\s+(?:\w+\s+){0,2}?(?:"
                                + "|".join(BODY_PARTS) + r")\b", re.I)


# The words that tie a part to the person typing: "my knee", "my left shoulder", "i have a sore
# knee", "i hurt my ankle". A part with none of them is a part the line is about rather than a
# report of one, and most lines like that are questions: "who has a sore hip", "does a sore knee
# need a doctor", "what helps a sore back". Filing one of those put a complaint in the person's
# mouth that they never made - the recall then said "It is your hip that you said was hurting" to
# someone who had asked who a sore hip has.
MY_OWN_PART = re.compile(r"\b(?:my|our)(?:\s+\w+){0,2}\s+$", re.I)


# A part said as the subject of the hurting word is theirs with no possessive at all: "knee
# hurts", "back is killing me", "shoulders are sore". Rare in chat, and unambiguous when it does
# happen, because nobody asks a question about a part in that word order.
THE_PART_HURTS = re.compile(r"^\s*(?:'s|s)?\s*(?:is|are|was|were|has|have|have been|has been|"
                            r"keeps)?\s*(?:killing|hurting|hurts|sore|aching|aches|ache|painful|"
                            r"stiff|swollen|playing|giving|in pain|bad|killing me)\b", re.I)


# A clause that opens with the person and then says something is the matter with a part of them:
# "i have a sore knee from running", "i hurt my ankle yesterday", "i've got a dodgy shoulder".
THE_PERSON_SAYS = re.compile(r"^(?:ok(?:ay)?[, ]+|and |so |but |well |oh |also )*"
                             r"(?:i|i'm|im|i've|ive|we|we're|were|we've|weve)\b", re.I)


# A line about a place on a part already named is about their own complaint even with no "my" in
# it: "its on the outside of the knee", "the pain is in the lower back".
A_PLACE_ON_IT = re.compile(r"^(?:it|its|it's|that|that's|this|the (?:pain|ache|hurt|soreness))\b",
                           re.I)


def _tied_to_them(part, low):
    """Whether the line ties the part to the person typing it, or only talks about parts.

    A question about a part names one with nothing that makes it theirs, and reading it as a
    complaint is the worst thing this reader can do: "who has a sore hip" filed a sore hip on the
    person who asked, and the store then answered "what did i say was hurting" with a hip they had
    never mentioned. Miss a bare "knee hurts" and nothing is lost; assert a complaint they did not
    make and the store lies to them.
    """
    before = low[:part.start()]
    after = low[part.end():]
    if MY_OWN_PART.search(before):
        return True
    if THE_PART_HURTS.match(after):
        return True
    # The clause the part sits in, so a question's own "i" does not count: "should i see someone
    # about a sore back" opens with "should", and the part is what it asks about.
    clause = re.split(r"[,;.!?]|\s+(?:and|but|so|then)\s+", before)[-1]
    if THE_PERSON_SAYS.match(clause.strip()) and BODY_HURTS.search(low):
        return True
    if A_PLACE_ON_IT.match(low) and BODY_PLACE.search(low):
        return True
    return False


def _theirs(part, low):
    """Whether the part at this place in the line is the speaker's own body.

    A part belongs to somebody else when a person word comes between them and it ("my mum has a
    sore hip", "my son's back"), and when the line hands it to another body with his, her, their
    or its ("my son hurt his arm"). Filing one of those as theirs put their mother's hip on them.
    A part the line only talks about, with no owner at all, is nobody's: it is a question.
    """
    part_at = part.start()
    owner = None
    for found in SOMEONE_ELSE.finditer(low):
        if found.start() < part_at:
            owner = found
    if owner is not None:
        between = low[owner.end():part_at]
        if not re.search(r"\b(?:my|our|i|me|mine|myself)\b", between):
            return False
    for other in A_PART_HANDED_OVER.finditer(low):
        if other.end() <= part_at + 1 and other.start() < part_at:
            return False
    return _tied_to_them(part, low)


def the_part_it_hurts(text):
    """The part of them that is sore, and where on it, or None.

    Filed as one record because it is one fact: the part, the side they gave ("left", "right",
    "both"), the place on it ("outside", "lower"), and the line as they said it, so the store can
    hand the words back instead of describing them. Read this way because nothing filed it at
    all: "its on the outside of the knee" left the store holding no fact, and eight turns later
    "and which knee was it" was answered with a hedge.
    """
    if not isinstance(text, str):
        return None
    low = " ".join(text.lower().split())
    # The first part that is their own body: "my son hurt his arm" says nothing about them, and
    # "my son has a sore arm and my knee is bad" says something about both.
    part = None
    for found in BODY_PART.finditer(low):
        if _theirs(found, low):
            part = found
            break
    if part is None:
        return None
    lateral = BODY_LATERAL.search(low)
    place = BODY_PLACE.search(low)
    if not (BODY_HURTS.search(low) or lateral or place):
        return None
    # "my knee is fine", "the back door": a part word with nothing the matter with it is not a
    # complaint, and the words that put a body word in front of another noun are not a side.
    if re.search(r"\b(?:no|not|never)\b[^.]{0,20}" + re.escape(part.group(1)) + r"\b", low):
        return None
    if not lateral and not place and re.search(r"\b" + re.escape(part.group(1)) +
                                              r"\s+(?:door|room|garden|yard|seat|window|wheel|"
                                              r"teacher|line|table|of the house)\b", low):
        return None
    held = {"part": part.group(1).lower(), "said": " ".join(text.split())}
    if lateral:
        held["side"] = lateral.group(1).lower()
    if place:
        held["place"] = place.group(1).lower()
    return held


def _extract(text, question=False):
    found = {}
    hurt = the_part_it_hurts(text)
    if hurt:
        found["hurts"] = hurt
    text = _the_numbers_in_words(text)
    diet = VEGETARIAN.search(text)
    name = _name(text)
    if name and diet and re.match(r"(?:i|we)", diet.group(1).lower()):
        # "im plant based" is how they eat, not what they are called: a way of eating that
        # starts with an ordinary word would otherwise also name them after that word.
        if diet.group(2).lower().replace("-", " ").startswith(_finish(name) + " "):
            name = None
    if name:
        found["name"] = name
    job, city, frame = _job_and_city(text, name, question)
    if not job and CHANGED_WORK.search(text):
        # "i changed jobs, im in a hospital now": the old job is gone, so the place the line
        # names as where they are now is the one to keep.
        moved = WORK_NOW.search(text)
        if moved:
            place = _finish(moved.group(3))
            if place and place not in JOB_STOP and len(place.split()) <= 3:
                # The preposition and the article are how they said where they work, so they
                # read back the same way: "you work in a hospital", never "in hospital".
                job = place
                frame = " ".join(part for part in (moved.group(1), moved.group(2)) if part)
    if job:
        found["job"] = job
        if frame:
            found["job_frame"] = frame
    car = _car(text)
    if car:
        found["car"] = car
    places, home, home_said = _places(text)
    if home is None:
        near = HOME_LOOSE.search(text)
        if near and near.group(1).split()[0].lower() not in NOT_PLACES:
            home = near.group(1)
            if home not in places:
                places.append(home)
    origin = _from_place(text)
    if origin:
        found["from"] = origin
        # A place they live in now is the one a "where do i live?" asks for, so the place they are
        # from joins the list only when nothing says where they live.
        if not home and origin not in places:
            places.append(origin)
    born = _born_place(text)
    if born:
        found["born"] = born
    for place in places:
        found.setdefault("places", []).append(place)
    if home and not city:
        city = home
        # The city is where they live, so a reply can say so rather than "you mentioned". A home
        # said with its place in front of it ("a small village near York") is kept in the words
        # they used, so the place they live is neither denied nor named as somewhere it is not.
        found["home"] = home_said or True
    if city and city not in found.get("places", []):
        found.setdefault("places", []).append(city)
    if city:
        found["city"] = city
    own = _own_states(text)
    if own:
        found.update(own)
    allergies, others = _allergies(text)
    if allergies:
        found["allergies"] = allergies
    for entry in _other_diets(text):
        known = next((seen for seen in others if _same_person(seen, entry)), None)
        if known is None:
            others.append(entry)
        else:
            known.setdefault("diet", entry["diet"])
    for entry in _other_conditions(text):
        known = next((seen for seen in others if _same_person(seen, entry)), None)
        if known is None:
            others.append(entry)
        else:
            known.setdefault("condition", entry["condition"])
    for entry in _other_jobs(text):
        known = next((seen for seen in others if _same_person(seen, entry)), None)
        if known is None:
            others.append(dict(entry))
        else:
            known.setdefault("job", entry["job"])
    for entry in _other_states(text):
        known = others[-1] if others and others[-1]["who"] == entry["who"] else None
        if known is None:
            others.append(dict(entry))
        else:
            for key, value in entry.items():
                known[key] = value
    for entry in _other_ages(text):
        known = next((seen for seen in others if _same_person(seen, entry)), None)
        if known is None:
            others.append(dict(entry))
        else:
            # A list of ages and one age are two readings of the same thing, and a lone age on
            # top of a list is the reading that saw only one of them: "i have two kids, 4 and 7"
            # was stored as "ages 4, 7" with an extra age of 7 beside it, and the chat said back
            # "Your kids are 7, 4 and 7." The fuller reading replaces the other instead.
            if entry.get("ages") or known.get("ages"):
                merged = _ages_held(known) + [age for age in _ages_held(entry)
                                              if age not in _ages_held(known)]
                held = _ages_held(entry)
                if held and len(held) >= len(_ages_held(known)):
                    merged = held
                known.pop("age", None)
                known["ages"] = merged
                if len(merged) == 1:
                    known["age"] = known.pop("ages")[0]
            else:
                known["age"] = entry["age"]
                # An age said with when it arrives is kept with those words: "my daughter is 3"
                # then "shes 5 next month" is a birthday, and an age that drops the "next month"
                # says she is 5 now, which is not what they told us.
                if entry.get("turns"):
                    known["turns"] = entry["turns"]
                else:
                    known.pop("turns", None)
            if entry.get("name") and not known.get("name"):
                known["name"] = entry["name"]
    for entry in _a_relations_name(text):
        known = next((seen for seen in others if _same_person(seen, entry)), None)
        if known is None:
            others.append(dict(entry))
        else:
            known["name"] = entry["name"]
    # The same person can be named with their name, their age or both, and the two readings are
    # merged by who they are rather than by the order they came in. A reading about "she" has no
    # "who" at all, so no step here may read the key as if every person had one.
    for entry in _relation_facts(text):
        # A line that names nobody files its fact against the pronoun instead ("shes 5 next
        # month" after "my daughter is 3"), so there is no "who" to merge by: the reader
        # crashed on the missing key and the person got "Hello!" back for a line about their
        # own child. The pronoun is the person there is to merge with, and when nobody carries
        # it the entry is kept for the store to fill in later.
        who = entry.get("who") or entry.get("pronoun") or ""
        known = None
        for seen in others:
            seen_who = seen.get("who") or seen.get("pronoun") or ""
            if (entry.get("name") and seen.get("name")
                    and str(entry["name"]).lower() != str(seen["name"]).lower()):
                # "my kids are ada 7 and sam 4" is two children, not one. A fact with no name of
                # its own still goes on the person the line already named.
                continue
            if who and (seen_who == who
                        or (not seen_who and entry.get("pronoun") and not seen.get("who"))):
                known = seen
                break
        if known is None:
            others.append(entry)
            continue
        for key, value in entry.items():
            if key in ("who", "pronoun"):
                known[key] = known.get(key) or value
            else:
                known.setdefault(key, value)
    entry = _a_name_and_a_figure(text)
    if entry:
        known = next((seen for seen in others
                      if str(seen.get("name") or "").lower() == entry["name"].lower()), None)
        if known is None:
            others.append(dict(entry))
        else:
            known["age"] = entry["age"]
            known.pop("months", None)
            known.pop("ages", None)
    if others:
        # A line that says something about a person is a line about that person: "my mums called
        # janet and shes 72" names the mum as surely as "my mum is coming round" does.
        for entry in others:
            for key in ("name", "age", "months"):
                if key in entry:
                    # A fact filed against a pronoun has no person yet: the store fills that in.
                    who = entry.get("who")
                    if who and who not in found.get("people", []):
                        found.setdefault("people", []).append(who)
                    break
        found["others"] = others
    if diet and re.match(r"(?:i|we)", diet.group(1), re.I):
        # The plain word is what people expect back, not "you're veggie".
        eating = " ".join(diet.group(2).lower().replace("-", " ").split())
        found["diet"] = DIET_NAMES.get(eating, eating)
    named = DIET_NAMED.search(text)
    if named and "diet" not in found:
        # "im on a gluten free diet" names the diet without naming a way of eating people adopt
        # as an identity, and it is the same fact: what the person will and will not eat.
        found["diet"] = " ".join(named.group(1).lower().split()).replace(" ", "-")
    underway = DIET_UNDERWAY.search(text)
    if underway and "diet" not in found:
        # "im on a diet" is a diet with no name, and "im doing keto" names one without the word
        # "diet": either way the line says how they eat, so the store keeps it.
        if underway.group("named"):
            found["diet"] = " ".join(underway.group("named").lower().split()).replace(" ", "-")
        else:
            found["diet"] = "on a diet"
    doing = _a_way_of_eating_said_with_a_verb(text)
    if doing and "diet" not in found:
        found["diet"] = doing
    bare = DIET_BARE.search(text)
    if bare and "diet" not in found:
        # "im dairy free" and "im low carb" name what the person eats without on or doing and
        # without the word "diet", and the store filed nothing, so the next ask about the diet
        # was denied to someone who had just said it.
        found["diet"] = "-".join(bare.group("bare").lower().replace("-", " ").split())
    meat = NO_MEAT.search(text)
    if meat:
        avoided = _finish(meat.group(1))
        if avoided in NO_EAT_QUALIFIER:
            # "i dont eat red meat": the first word qualifies the food, so the food comes with it,
            # and "red" on its own is not something anyone can be read back as avoiding.
            rest = _finish(text[meat.end():].split()[0]) if text[meat.end():].split() else ""
            if rest in MEAT:
                avoided = avoided + " " + rest
        # "i dont eat enough veg" and "i dont drink enough water" are a shortfall, not a way of
        # eating: filed as `diet: "no enough"` the line comes back as "You don't eat enough veg,
        # good to know - I'll plan around it", which is the complaint made into a diet.
        if avoided and avoided.lower().split()[0] not in _QUANTITY_WORDS \
                and not set(avoided.split()) & ALLERGY_STOP:
            found["diet"] = "no " + avoided
            if MEAT & set(avoided.replace(",", " ").split()):
                found["no_meat"] = True
    if not found.get("diet"):
        # The drinking half of the same fact, filed the same way, so the answers that keep food
        # off the plate keep the drink out too ("what wine goes with lamb" after "i dont drink").
        drank = _the_drink_they_do_not_take(text)
        if drank:
            found["diet"] = "no " + drank
    condition = CONDITION.search(text)
    if condition:
        found["condition"] = " ".join(condition.group(1).lower().split())
    pets = _pets(text, question)
    if pets:
        found["pets"] = pets
    owned = _owns(text)
    if owned:
        # "my car is a ford fiesta": the thing said with its make, which is what "what car do i
        # drive" asks for. One line can name two ("my car is a fiesta and my phone is a pixel").
        found["owns"] = owned
    tastes = [] if found.get("diet") else taste.read_all(text)
    if tastes:
        # "i love dogs", "not keen on fish", "not sure if i like curry": a taste of theirs, said
        # back like any other fact, and never an animal in the house (`bot/memory/taste.py`).
        # "i don't eat fish" is a diet and the diet extractor has it: a taste is what is left.
        # One line can hold two ("i like dogs but i hate cats"), and each is its own fact.
        found["tastes"] = tastes
    budget = (BUDGET.search(text) or SPEND_BUDGET.search(text) or SPEND_FOR.search(text)
              or INTENDED_SPEND.search(text) or THE_THING_MAY_COST.search(text)
              or ALL_I_CAN_DO.search(text)
              or ONLY_HAVE.search(text) or SPEND_BUDGET_NOW.search(text)
              or STRETCH_BUDGET.search(text)
              or BARE_BUDGET.search(text) or BUDGET_ASKED.search(text)
              or BUDGET_THOUGHT.search(text) or CEILING_BUDGET.search(text))
    if not budget:
        # A figure they live on is a limit like the money they have ("i only earn 1200 a month").
        # It has to be paid by a period and it must not be a rate: "i get 3 runs a week" is a
        # routine and "i earn 20 pounds an hour" is a wage rate, and neither is what a plan fits.
        money = INCOME.search(text)
        if money and not _paid_by_a_period(text, money.end()):
            money = None
        if not money:
            bare = INCOME_BARE.search(text)
            if bare and _paid_by_a_period(text, bare.end()):
                figure = bare.group(1).split()[-1]
                if sum(ch.isdigit() for ch in figure) >= 3:
                    money = bare
        if not money:
            for a_year in INCOME_A_YEAR:
                year = a_year.search(text)
                if (year and _a_years_pay(year.group(1))
                        and not text[year.end():].strip(" .,;!?-").strip()):
                    money = year
                    break
        if money and INCOME_RATE.match(text, money.end()):
            money = None
        budget = money
    if budget and subject(text, budget.start())[0] != "other":
        said_budget = " ".join(budget.group(1).split()).rstrip(".,;:")
        if budget.re is CEILING_BUDGET:
            # The refusal is the limit, said as the limit it is: "nothing over 25 pounds" and
            # "no more than 25 pounds" are the same ceiling, and the second is the one the
            # store can say back.
            said_budget = "no more than " + said_budget
        found["budget"] = said_budget
    elif not question and vague_budget(text) and subject(text, 0)[0] != "other":
        found["budget"] = vague_budget(text)
    kids = kid_count(text)
    if kids is not None:
        # A zero is a fact the store can answer with: "i dont have any kids" then "how many kids
        # do i have" was "You haven't told me how many kids you have yet", and a truthiness test
        # here dropped the one number that was said.
        found["kids"] = kids
    # "my age is 34" is the age said with its name, and people say it that way when they are
    # being clear. "i'm 34" is the shape that covers most of it.
    age = AGE.search(text) or MY_AGE.search(text)
    if age:
        found["age"] = int(age.group(1))
    # How tall, read after the age for the same reason the age reader refuses these figures: the
    # unit is what says this number is a height and not an age.
    tall = _how_tall(text)
    if tall:
        found["height"] = tall
    birthday = BIRTHDAY.search(text)
    if birthday and subject(text, birthday.start())[0] != "other":
        date = _a_birthday_date(birthday.group(1))
        if date:
            found["birthday"] = date
    weight = WEIGH.search(text) or WEIGH_IM.search(text) or WEIGH_MY.search(text)
    if weight and subject(text, weight.start())[0] != "other":
        unit = _weight_unit(weight.group(2))
        if unit:
            found["weight"] = weight.group(1) + " " + unit
            if str(found.get("age")) == weight.group(1):
                # The same figure read twice: "im 85 kilograms" is a weight, and a bare-number age
                # reader takes the 85 for an age as well, which has the bot say "you told me
                # you're 85" at the ask for their age. A line with its own age keeps it ("im 34
                # and i weigh 90 kilos" leaves both alone).
                found.pop("age", None)
    # "my sons" names the same person as "my son": _people reads the plural of every relation,
    # and a person the store knows is one the next "what is he allergic to" can be about.
    relations = _people(text)
    if relations:
        found["people"] = relations
    # A line that only moves the date of a plan they already told us about is not a new plan:
    # the plan is the one the store holds, with its date put right.
    moved = _date_change(text)
    plan = PLAN.search(text)
    if plan and _asks_about_the_plan(text, plan.start()):
        # A question about the plan is not a plan: the same words a plan is written with sit
        # inside the ask (bot/memory/facts.py, _asks_about_the_plan).
        plan = None
    if (plan and _GOT_A.search(plan.group(0)) and not FUTURE.search(text)
            and not _GOT_TO.search(text)):
        # "ive got a headache", "ive got two kids", "ive got a question about my tax": what they
        # have, not what they are going to do. The "got" form only plans when the infinitive is
        # there ("ive got to paint the fence") or when a date puts it ahead of them.
        plan = None
    if plan and re.match(r"^to\s+(?:go|leave|head off|set off|get going|dash)\b",
                          _plan_text(text, plan.end()), re.I) and _FAREWELL.search(text):
        plan = None  # "ive got to go, speak later" is a goodbye, not an arrangement
    if plan:
        plan_text = _plan_text(text, plan.end())
        words = re.sub(r"^to\s+", "", plan_text, flags=re.I).lower().split()
        while words and words[0] in ("a", "an", "the", "my", "our"):
            words.pop(0)
        first_word = words[0] if words else ""
        # "i'm going to bed" stops after "to" with a place; "i've got to call the dentist" stops
        # with the "to" still on the front, and the word after an infinitive "to" is a verb,
        # however much it looks like a place ("call", "book", "see" are in PLACE_VERBS).
        after_an_infinitive = (bool(re.match(r"to\b", plan_text, re.I))
                               or bool(INFINITIVE_FRAME.search(plan.group(0))))
        if (plan_text and not re.match(r"(?:[£$€]|\d)", plan_text)
                and first_word not in NOT_PLACES
                and (after_an_infinitive
                     or (first_word not in PLACE_VERBS and _a_plan_has_a_thing(plan_text)))):
            verb = _plan_verb(plan, plan_text)
            if verb:
                # the verb goes back in front of the thing it is about: "Saving up for a bike"
                plan_text = verb + " " + plan_text[:1].lower() + plan_text[1:]
            found["plan"] = plan_text
    if found.get("plan") and found.get("pets"):
        # "i've got two cats, milly and tom" is a pet, not a plan: the animal is the thing the
        # line is about, and a plan only reads it back as something they mean to do
        if PETS.search(found["plan"]):
            del found["plan"]
    for key in ("places", "allergies", "people"):
        if key in found:
            kept = [value for value in (_fact_value(v) for v in found[key]) if value]
            if kept:
                found[key] = kept
            else:
                del found[key]
    for entry in found.get("others") or []:
        for key in ("allergies", "places"):
            if key in entry:
                entry[key] = [value for value in (_fact_value(v) for v in entry[key]) if value]
    for key in ("budget", "diet", "city", "plan"):
        if key in found and not _fact_value(found[key]):
            del found[key]
        elif key in found:
            found[key] = _fact_value(found[key])
    if "plan" not in found:
        deed = []
        several = list(_dated_plans(text, deed))
        dated = _appointment(text) or (several[0] if several else "")
        if dated:
            found["plan"] = dated
            if len(several) > 1:
                found["plans_today"] = several
        elif deed:
            # A dated thing they have already done is not coming up, but it is theirs: the store
            # answers it with the thing itself, and only a plan is read back as ahead of them.
            found["done"] = deed[0]
    if "plan" in found and moved is None:
        found["plans"] = found.pop("plans_today", None) or found["plan"]
    if moved is not None:
        # "we moved it to july" is the plan they already gave us, said again with a new date.
        # The words of the line are not a plan of their own ("You moved it to july").
        found.pop("plan", None)
        found.pop("plans", None)
    # "i said" is read before "i meant", because "no i meant to say bristol" is caught by the
    # "meant" pattern with "to" as its value if it gets there first.
    correction = (CORRECTION_SAID.search(text) or CORRECTION.search(text)
                  or CORRECTION_PAIR.search(text) or CORRECTION_NUMBER_PAIR.search(text)
                  or _a_day_taken_back(text)
                  or _a_moved_time(text) or CORRECTION_CLOCK.search(text)
                  or CLOCK_PREFERRED.search(text)
                  or CORRECTION_MAKE.search(text))
    # "make it"/"make that" is the one shape that names no old value, and it is also the shape a
    # half sentence arrives in: "my boiler is broken / make it stop". Whether it corrects anything
    # is the store's question (it knows what the line before said), so the shape goes along.
    made = correction is not None and correction.re is CORRECTION_MAKE
    hedged = None
    if correction is None:
        dated = (CORRECTION_DATE.search(text) or CORRECTION_DATE_GOING.search(text)
                 or CORRECTION_GOING_MOVED.search(text))
        if dated is not None:
            # A date is said back with its day and its month in it, which the one-word reader
            # keeps to a single value: "sorry, its the 4th of may" is the whole date.
            found["correction"] = {"to": _tidy(" ".join(dated.group("date").split())),
                                   "from": None}
    if correction is None and "correction" not in found:
        # The date reader above already named the value, and its value is the one to keep: the
        # bare reader matches the same line with the preposition still on it ("no in july" is
        # its value "in july"), and putting that over the date moved the month into the plan's
        # place ("you're going to In july next month").
        # A hedged figure is the same move as a bare one, and the readers below cannot see it:
        # the hedge sits where the value should start, so it is read here, before them.
        hedged = None if correction is not None else CORRECTION_HEDGED.search(text)
        if hedged is not None:
            correction = hedged
        bare = None if correction is not None else CORRECTION_BARE.search(text)
        # The word that says "no thanks" can arrive behind the apology the tail strip takes
        # off ("no idea sorry"): the value is what gets compared with them, so it is the value
        # that decides, and a line that names nothing is still not a correction.
        if bare is not None and bare.group(1).lower() not in CORRECTION_BARE_NO and (
                _the_value_alone(COPULA_SPLIT.split(bare.group(1))[0]).strip().lower()
                not in CORRECTION_BARE_NO):
            correction = bare
        if correction is None:
            named = NO_THEN_A_THING_NAMED.search(text)
            if named is not None and named.group(1).lower().split()[0] not in ANIMALS:
                correction = named
    if correction is None and moved is not None:
        found["correction"] = {"to": moved, "from": None}
    if correction is None:
        amount = AMOUNT_CORRECTION.search(text) or AMOUNT_CORRECTION_BARE.search(text)
        if amount:
            before = set(re.findall(r"[a-z']+", text[:amount.start()].lower())[-4:])
            if not before & AMOUNT_WISH:
                found["correction"] = {"to": amount.group(1).strip(" .,"), "from": None}
    if correction and not _is_only_the_take_back(correction.group(1), denials(text)):
        wrong = correction.group(2) if correction.re.groups > 1 else None
        # The value stops at a verb: "no i said bristol is fine" corrects the place to Bristol and
        # says nothing about "is fine", so the copula and what follows is not part of the value.
        value = _the_value_alone(COPULA_SPLIT.split(correction.group(1))[0])
        # "no, its on thursday", "no, in bristol": the preposition in front says what kind of value
        # this is and is not part of it, but CORRECTION_BARE reads the two words together ("On
        # thursday"), so the fact in hand never matched a day again and the correction was dropped
        # without a word. A line whose value is only the preposition keeps it ("no, on"), and the
        # value has to still read as one afterwards, so the strip is tried, not forced.
        without_it = re.sub(r"^(?:on|in|at)\s+", "", value, flags=re.I).strip()
        if without_it and a_value(without_it):
            value = without_it
        # A value said with the naming word in it is a name being put right, and the naming word
        # is the frame, not the name: "no its called tim" hands over "called tim" and the cat
        # was filed as "Called tim".
        value = the_name_in(value) or value
        # A figure is a value even when the word for it is one the pointer list holds. "one" is on
        # that list because "the other one" points at something and keeps nothing, but after
        # "actually just" it is the number the person changed: "i have two kids" then "actually
        # just one" said two children back, because no value reached the count reader.
        if a_value(value) or hedged is not None:
            found["correction"] = {"to": _tidy(value),
                                   "from": _tidy_apart(wrong) if wrong else None}
            if made:
                found["correction"]["make"] = True
    if "correction" not in found:
        # "make it" can name more than the value: "make it 800 for the trip" is not a value on its
        # own, so a line the shapes above matched but could not read still has to be read for the
        # number it puts up. The amount rule is the one that knows "for the trip" and "a month"
        # leave the number as it is.
        amount = AMOUNT_CORRECTION.search(text) or AMOUNT_CORRECTION_BARE.search(text)
        if amount:
            before = set(re.findall(r"[a-z']+", text[:amount.start()].lower())[-4:])
            if not before & AMOUNT_WISH:
                found["correction"] = {"to": amount.group(1).strip(" .,"), "from": None}
    # A value taken back and the right one after it: "no, not Friday, Monday". This is read
    # before the bare take-back below, because that pattern reads the first value only and takes
    # it away - "sorry, not peanuts, tree nuts" left the person with nothing on record.
    if "correction" not in found and found.get("drop") is None:
        pair = CORRECTION_NOT_PAIR.search(text)
        if pair is not None:
            right, wrong = _tidy(pair.group(2)), _tidy(pair.group(1))
            if (a_value(right) and a_value(wrong)
                    and right.lower() not in NOT_A_DAY and wrong.lower() not in NOT_A_DAY):
                found["correction"] = {"to": right, "from": wrong}
    # A name denied with the pronoun first: "no he isn't Dave" takes a value away and puts
    # nothing in its place, and "no he isn't, it's Dan" gives the right one after it. Read by
    # CORRECTION_PAIR it was the pronoun that became the value ("no hes not dave" filed "Hes"),
    # so this shape is read on its own, and only when the line says whose value it is - a pronoun
    # sweep over every denial would turn "no it isnt" into a correction of whatever came before.
    if "correction" not in found and found.get("drop") is None:
        denial = DENIAL_OF_A_VALUE.match(text)
        if denial is not None and not a_name_is_taken_back(text):
            said, wrong = denial.group("value"), denial.group("wrong")
            if said and denial.group("says") and a_value(said):
                from_wrong = (_tidy(wrong) if wrong and a_value(wrong)
                              and wrong.lower() != said.lower() else None)
                found["correction"] = {"to": _tidy(said), "from": from_wrong}
            elif said and not denial.group("says"):
                # The only value in the line is the one being denied, so nothing is kept: what
                # the store holds is either still right or was never said here.
                pass
    # A value taken back with nothing in its place: "sorry, not peanuts" says which one goes,
    # and the store is the only thing that can take it off the list it was on. This is its own
    # `if` on purpose: it was the `elif` of the block above, so when "make it" moved in between
    # them the take-back came to belong to the wrong branch and no line took anything back.
    if "correction" not in found and found.get("drop") is None:
        paired = CORRECTION_NOT_TO.search(text)
        if paired is not None:
            # "not lisbon, porto": the value after the one taken back is what they mean instead, so
            # this is a correction and the rest of the line stays where it was.
            wrong, right = _tidy(paired.group(1)), _tidy(paired.group(2))
            # "porto instead" is the value plus the word that says it replaces the other one.
            right = re.sub(r"\s+(?:instead|then|now)\b\W*$", "", right, flags=re.I)
            if (a_value(wrong) and a_value(right) and wrong.lower() not in NOT_A_DAY
                    and right.lower() not in NOT_A_DAY and wrong.lower() != right.lower()):
                found["correction"] = {"to": right, "from": wrong}
        gone = CORRECTION_NOT.search(text)
        if gone is not None and "correction" not in found:
            value = COPULA_SPLIT.split(gone.group(1))[0]
            if a_value(value) and value.lower() not in NOT_A_DAY:
                found["drop"] = _tidy(value)
    # "take that back" states no fact of its own: it undoes the line before it, and only when the
    # line has nothing else in it, so "im allergic to peanuts, take that back" keeps the peanuts
    # going up for the correction path to read.
    if not found and RETRACT.match(str(text or "").strip()):
        found["retract"] = True
    # The tone words go last, over everything the line left behind: "my sister is called meg
    # tbh" is a sister called Meg, and "i work as a nurse haha" is a nurse. A value that was
    # nothing but tone ("haha") leaves nothing to keep.
    for key, value in list(found.items()):
        if isinstance(value, str) and value:
            kept = no_tone(value)
            if kept:
                found[key] = kept
            else:
                del found[key]
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            # A retraction hung off the end of a line is not one of the things in it: "im allergic
            # to peanuts, take that back" is the peanuts going up, not a second allergy.
            cleaned = [(item, no_tone(item)) for item in value]
            found[key] = [kept for item, kept in cleaned
                          if kept and not RETRACT.match(kept)]
            if not found[key]:
                del found[key]
    for entry in found.get("others") or []:
        for key, value in list(entry.items()):
            if key == "who":
                continue
            if isinstance(value, str) and value:
                entry[key] = no_tone(value)
            elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                entry[key] = [kept for kept in (no_tone(item) for item in value) if kept]
    if "correction" not in found and CORRECTION_MARK.search(text):
        for key in CORRECT_FROM_MARK:
            value = found.get(key)
            if isinstance(value, list):
                value = value[0] if value else None
            if isinstance(value, (int, float)):
                value = str(value)  # an age or a budget is kept as a number
            if not isinstance(value, str) or not value.strip():
                continue
            if not a_value(value):
                continue
            found["correction"] = {"to": _tidy(value), "from": None}
            break
    return found
