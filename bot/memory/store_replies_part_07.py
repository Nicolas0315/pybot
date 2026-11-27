"""Part 7 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import random
import re
from ..compose import pick
from ..memory import name, others, recent, thread, user
from ..memory import ack
from ..memory import condition
from ..memory import facts as extract
from ..memory import recall
from ..memory.topics import subject as topic_subject
from ..memory.store_lines import (
    CHILD_RELATIONS, RESTATED_KEYS, CHILD_RELATIONS, CAR_CAPS, NUMBER_WORDS, _SUBJECT_KEYS,
    CONCEPTS,
)
from ..memory.relations import (
    PET_ASK, _a, _a_list_of_names, _animal_family, _called, _canon_relation, _folded, _in_the_group,
    _one_age, _relations_of, _same_as_last, _the_group_names_typed, _tidy_name,
)
from ..modules.memory_tables import ASK_WITHOUT_MY
from .store_replies_part_01 import (
    NAME_PICKED_AGAIN, PET_NAME_AGAIN, PET_NAME_SETTLED, _the_animal_of_the_pick,
    _name_they_answered, _offered_here, NOT_THE_SAME, _the_limit_the_last_line_gave, FOOD_ASK,
    NAME_ASK_TAIL, WHO_IS_NAME_ASK, _kids_ask, CHILDREN_ABOUT,
)
from .store_replies_part_02 import (
    A_DAY, A_PERSON_IN_TROUBLE, COMING_UP, FEELING_ALONE, OPENS_ON_THE_SENTENCE, TREATMENT,
    WHO_IS_IN_TROUBLE, _again, _is_a_question, _said_back_already, _the_thing_before_the_feelings,
    _same, _someone_said_back, A_CONDITION_RULES_OUT, A_DIET_RULES_OUT, FOOD_CATEGORIES, _names,
    _their_allergy,
)
from .store_replies_part_03 import (
    _other_fact, _diet_food, _said_list, _is_are, _object_pronoun,
)
from .store_replies_part_04 import (
    EATING_ASK, LEAD_IN, DUTY_ASK, OWNED_ASK, _a_that_fits, _a_list_of_clauses, BREED_WORD,
    CAR_DESCRIBED, NO_CAP, A_BIRTHDAY_PLAN, A_RELATIONS_BIRTHDAY, ADVICE_ASK,
)
from .store_replies_part_05 import (
    _diet_how, _job_said, _restated, _said_matches, _the_food_named, _statement, _a_number_word,
)
from .store_replies_part_06 import (
    _a_food, _said_a_limit,
)


def _the_pick_asked_again(text, memory):
    """The name the store holds, when the ask is the choosing said with "pick" or "settle".

    "im getting a dog / what should i call it / pepper / so what did i pick" was answered
    "You haven't picked one yet", which is false twice over: the name was said, and the store has
    it. The choice reader answers this shape for a plan it watched being made, and a name is not
    a plan, so the turn is answered from the pet instead.

    A bare "what did i pick" is only this ask while the chat is still on the pet and the name is
    among the last lines: a chat with a cat called Mango that has since been talking about a
    holiday is asking about the holiday, and there the choice reader's answer stands.
    """
    low = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if not low or not NAME_PICKED_AGAIN.search(low):
        return None
    if re.search(r"\b(?:" + "|".join(extract.RELATIONS) + r")\b", low):
        return None
    named = [pet for pet in (user(memory).get("pets") or [])
             if isinstance(pet, dict) and pet.get("name")]
    if not named:
        return None
    pet = named[-1]
    name = str(pet.get("name") or "")
    animal = str(pet.get("animal") or "pet")
    if "name" not in low:
        # Without the word "name" in it, a bare "what did i pick" is only about the pet while the
        # chat is still on the pet: the subject is the animal (or the name itself) and one of the
        # last three lines was the name on its own. A chat with a cat called Mango that has since
        # moved on to "we were thinking italy or spain" is asking about the trip, and the choice
        # reader's own answer stands there.
        subject = str(topic_subject(memory) or "").lower().split()
        if not subject or (animal.lower() not in subject and name.lower() not in subject):
            return None
        turns = memory.get("turns") if isinstance(memory, dict) else None
        recent = [str((one or {}).get("user") or "")
                  for one in (turns[-3:] if isinstance(turns, list) else [])]
        said = [(extract.bare_name(line) or "").lower() for line in recent]
        if not name or name.lower() not in said:
            return None
    return _vary((
        _called(name) + " \u2014 that is the one you picked for your " + animal + ".",
        "You went for " + _called(name) + ". I have it written down.",
        _called(name) + ". That is your " + animal + "'s name.",
    ), memory)


def _what_the_pet_is_called(text, memory):
    """The name the store holds for the animal the line points at: "Milo — you settled on that."

    Only when the line is that ask and no person in it: "what's his name" after "my brother came
    round" is about the brother, and the relations reader owns those.
    """
    low = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if not low or not (PET_NAME_AGAIN.search(low) or PET_NAME_SETTLED.search(low)):
        return None
    if re.search(r"\b(?:" + "|".join(extract.RELATIONS) + r")\b", low):
        return None
    named = [pet for pet in (user(memory).get("pets") or [])
             if isinstance(pet, dict) and pet.get("name")]
    if not named:
        # The animal is in play and has no name yet: the honest line is about the name, the way
        # the store already answers "what's my dog called". A line with no animal anywhere near
        # it ("what's his name" after a brother came round) is left to the relations reader.
        if PET_NAME_SETTLED.search(low):
            return None  # no name yet, so the naming question still wants names
        animal = _the_animal_of_the_pick(memory)
        if not animal or animal == "pet":
            return None
        return "You haven't told me a name for your " + animal + " yet."
    pet = named[-1]
    name = _called(str(pet.get("name")))
    animal = str(pet.get("animal") or "pet")
    return _vary((
        name + " \u2014 that is what you settled on for your " + animal + ".",
        "Your " + animal + " is called " + name + ".",
        name + ". I have that one written down.",
    ), memory)


def _the_name_they_picked(text, memory):
    """The name the person settled on, said back: "Pepper it is. I'll remember that for your cat."

    A name is the one thing a naming answer gives that no entry can, so the turn that gives it is
    answered rather than echoed ("Got it - her name is pepper") or given the stock line
    ("Thanks for telling me"). The name is already in the store by the time any module answers,
    because `observe` runs first, so the reply is built from what was kept and not from the line.
    """
    said = extract.pet_name_only(text)
    if not said and _offered_here(memory):
        # Only the list this module put in front of them is this module's turn: a bare word after
        # the bot has *asked* for the name ("we got a puppy" / "A puppy - good to know. What's its
        # name?" / "biscuit") is answered where that question was written, and the warmer line
        # there ("A puppy called Biscuit - lovely. How's Biscuit settling in?") stands.
        said = _name_they_answered(text, memory)
    if not said:
        return None
    pet = None
    for one in reversed(user(memory).get("pets") or []):
        if isinstance(one, dict) and str(one.get("name") or "").lower() == said.lower():
            pet = one
            break
    if pet is None:
        return None
    name = _called(str(pet.get("name") or said))
    animal = str(pet.get("animal") or "pet")
    return _vary((
        name + " it is. I'll remember that for your " + animal + ".",
        name + " \u2014 good choice, and easy to shout across a park.",
        "Right, " + name + ". That is the one from here on.",
    ), memory)


def _not_the_same_reply(memory, low):
    """The limit refused for somebody, acknowledged, and nothing filed."""
    if not isinstance(low, str):
        return None
    match = NOT_THE_SAME.match(" ".join(low.split()))
    if not match:
        return None
    who = _canon_relation(extract.a_person_word(match.group("who")))
    if who not in extract._A_WORD_FOR_A_PERSON:
        return None
    if not _the_limit_the_last_line_gave(memory):
        return None
    said = "your " + who
    return _vary(["Got it \u2014 " + said + " isn't.",
                  "Good to know \u2014 " + said + " isn't, then.",
                  "Right, so it's not " + said + " \u2014 noted."], memory)


def _a_feeling_about_what_they_said(memory, low):
    """The thing they just told us, said back, when the whole line is how they feel about it."""
    match = FEELING_ALONE.match(str(low or "").strip().rstrip("!.,"))
    if not match:
        return None
    previous = _the_thing_before_the_feelings(memory)
    if not previous or len(previous.split()) < 4:
        return None
    if _is_a_question(previous):
        return None
    if TREATMENT.search(previous):
        return None
    if not re.search(r"\b(?:i|we|my|our|me)\b|\bim\b|\bive\b", previous.lower()):
        return None
    trouble = A_PERSON_IN_TROUBLE.search(previous)
    if not (COMING_UP.search(previous) or trouble):
        return None
    if trouble:
        # The person is named in the reply itself, so the news is not read back on top of them:
        # "Scared for your dad is one of the heaviest things to carry" is a friend's line, and
        # "Your dad is in hospital. ..." in front of it is the machine reading their own news.
        who = WHO_IS_IN_TROUBLE.search(previous)
        if who:
            # A body already said stays out: two fears in a row about the same person should not
            # read as one line twice.
            recent = " ".join(str(t.get("bot") or "") for t in (memory.get("turns") or [])[-5:]
                              if isinstance(t, dict))
            # The person's own word for them wins over what the kin word usually means: "im
            # scared for him" about a friend is a him, and the reply must not say "them".
            said_for = re.search(r"\b(?:for|about)\s+(him|her|them)\b", str(low or ""), re.I)
            again = _again(who.group(1))
            if said_for:
                theirs = said_for.group(1).lower()
                # ... but only where the kin word cannot tell. "my brother is in hospital / im
                # scared for her" is two people in one sentence - "frightened for your brother
                # does not make you any less help to her" - and the word that names the person
                # in the line before is the one the reply is about, so a kin word that already
                # says which it is keeps its own word and their pronoun is the slip.
                if again == "them" or theirs == again:
                    again = theirs
            said_bodies = [body.format(who="your " + who.group(1).lower(), again=again)
                           for body in (
                "That is a lot to be carrying, and being frightened for {who} does not make you "
                "any less help to {again}.",
                "It is all right to be frightened for {who}. You do not have to be the calm one "
                "all the time.",
                "Scared for {who} is one of the heaviest things to carry, and you are allowed to "
                "say so.",
                "Being frightened for {who} is the honest reaction, and saying it out loud once "
                "usually takes some of the weight off.",
            )]
            fresh = [body for body in said_bodies if body not in recent] or said_bodies
            # A seed off the person as well as the turn, so two chats about two different
            # people do not open with the same sentence.
            seed = len(memory.get("turns") or []) + sum(map(ord, who.group(1)))
            return random.Random(seed).choice(fresh)
    said = thread.restate(previous)
    if not said or len(said.split()) < 3:
        return None
    said = said[0].upper() + said[1:]
    feeling = match.group(1).lower()
    if feeling in ("worried", "anxious"):
        bodies = ["That is a fair thing to have on your mind, and most of it is the not-knowing.",
                  "Worrying about it makes sense. Is there one thing you could check that would "
                  "settle it?",
                  "That kind of worry is tiring to carry, and saying the worst version out loud "
                  "usually shrinks it.",
                  "Worry about something coming up is the mind rehearsing it. Is there one thing "
                  "you could check that would settle it?"]
    elif A_DAY.search(previous):
        bodies = ["Nerves before something like that are normal, and it is usually worse in the "
                  "days before than on the day.",
                  "Of course you are - most of it is the not-knowing. What is the first thing that "
                  "happens?",
                  "That is a fair thing to be nervous about. Tell me the part of it that keeps "
                  "coming back.",
                  "That is a nervous-making thing to have coming, and it says nothing bad about "
                  "how ready you are.",
                  "Nerves are usually worse in the days before than on the day. What is the first "
                  "thing that happens?"]
    else:
        bodies = ["That is a fair thing to be nervous about, and it is all right to say so.",
                  "Nerves about it make sense, and naming the worst version out loud usually "
                  "shrinks it.",
                  "That is a lot to be carrying around. Is there one part of it you could start "
                  "on?",
                  "Saying the thing you dread out loud is usually the worst part of it, and the "
                  "rest is smaller than it looks.",
                  "Most of the nerves is the not-knowing. What is the part that keeps coming "
                  "back?"]
    # The bot may have just said the thing itself ("Noted: you are going to spain in june"), and
    # reading their own news back to them twice is the machine talking. The body carries the
    # reply on its own; the sentence is only there when it is new.
    # A body that was already said stays out even when the sentence in front of it was not the
    # same: two feels in a row should not read as one line with a different lead.
    recent = " ".join(str(t.get("bot") or "") for t in (memory.get("turns") or [])[-5:]
                      if isinstance(t, dict))
    body = _vary([b for b in bodies if b[:40] not in recent] or bodies, memory)
    if any(_said_back_already(str(turn.get("bot") or ""), said)
           for turn in (memory.get("turns") or [])[-2:] if isinstance(turn, dict)):
        # The sentence is left off because the bot has just said the news ("Noted: you have a
        # scan at the hospital on friday"), so any body that opens by pointing at a sentence
        # which is not there has nothing to point at: "Of course you are" answers a "scared"
        # nobody said, and "That is a nervous-making thing" names a thing with no antecedent.
        standing = [b for b in bodies if not OPENS_ON_THE_SENTENCE.match(b)]
        return _vary([b for b in standing if b[:40] not in recent] or standing or bodies, memory)
    return said + ". " + body


def _clause(key, value, known=None):
    """The fact said the way a friend would say it back: "you're vegetarian"."""
    if key == "name":
        return "you're " + str(value)
    if key == "age":
        return "you're " + str(value)
    if key == "job":
        # A job told with a place preposition is a place ("you work at the hospital"), so the
        # frame stored with it says it back, not "you're a hospital".
        known = known if isinstance(known, dict) else {}
        frame = str(known.get("job_frame") or "").strip()
        if frame and _same(value, known.get("job")):
            said = _job_said({"job": str(value), "job_frame": frame})
            return said[:1].lower() + said[1:]
        return "you're " + _a(str(value))
    if key == "city":
        return "you live in " + str(value)
    if key == "car":
        return "you drive " + str(value)
    if key == "from":
        return "you're from " + str(value)
    if key == "allergies":
        return "you're allergic to " + ", ".join(value)
    if key == "budget":
        return "your budget is " + str(value)
    if key == "diet":
        diet = str(value)
        return ("you don't " + _diet_how(diet) + " " + diet[3:] if diet.startswith("no ")
                else "you're " + diet)
    if key == "pets":
        pets = value if isinstance(value, list) else [value]
        parts = [_a_pet(p) for p in pets]
        return "you've got " + " and ".join(parts)
    return ""


def _remembers_fact(text, memory):
    """Yes or no to "do you remember that i ...", from the fact they told the store.

    A fact the store holds is confirmed in its own words ("Yes - you're vegetarian."), and one
    stated the other way round is put right gently ("You told me you live in Leeds."). A
    statement the store keeps nothing about is left to the other modules: this reader answers
    only what it holds.
    """
    said = _restated(_folded(text, memory), text)
    if not said:
        return None
    found = extract.extract(said) or {}
    known = user(memory)
    yes, no = [], []
    for key in RESTATED_KEYS:
        value = found.get(key)
        if not value:
            continue
        stored = known.get(key)
        if not stored:
            continue
        if key == "pets":
            value = [p for p in value if isinstance(p, dict) and (p.get("name") or p.get("animal"))]
            if not value:
                continue
            value = value[0]
        matches = _said_matches(key, value, stored)
        said_back = _clause(key, stored, known)
        if not said_back:
            continue
        if matches:
            yes.append(said_back)
        elif matches is not None:
            no.append(said_back)
    if yes:
        fact = yes[0]
        return pick(["Yes \u2014 " + fact + ".",
                     fact[:1].upper() + fact[1:] + " \u2014 I have that.",
                     "That's right \u2014 " + fact + "."], memory)
    if no:
        fact = no[0]
        return pick(["You told me " + fact + ".", "Not quite \u2014 " + fact + "."], memory)
    # A frame around a fact the store has just been told is not a question it can answer yes or
    # no to: the keys above are the person's own facts, and their sister's name is not one of
    # them. Saying nothing left the line to the about-the-bot reader, which answered a person who
    # had just given the name with "there's nothing on your sister". What the frame asks for is
    # the store holding it, so the fact it now holds is said back.
    kept = _someone_said_back(said, memory)
    if kept:
        return kept
    return None


def _the_rule_that_rules_it_out(known, category):
    """The rule they gave the store that takes this food off the table, said back, or ""."""
    diet = " ".join(str(known.get("diet") or "").lower().split())
    taken = list(A_DIET_RULES_OUT.get(diet) or ())
    if known.get("no_meat") and "meat" not in taken:
        taken.append("meat")
    if category in taken:
        if diet:
            return "No \u2014 " + _clause("diet", known.get("diet")) + "."
        return "No \u2014 you don't eat meat."
    for allergy in known.get("allergies") or []:
        said = str(allergy).lower()
        if any(said == one or said.rstrip("s") == one.rstrip("s")
               for one in dict(FOOD_CATEGORIES)[category]):
            return "No \u2014 " + _clause("allergies", known.get("allergies")) + "."
    for condition in known.get("condition") or []:
        word = " ".join(str(condition).lower().split())
        if category in (A_CONDITION_RULES_OUT.get(word) or ()):
            return "No \u2014 you've told me you're " + word + ", so " + category + " is out."
    return ""


def _a_rule_on_eating(text, memory):
    """A yes/no about eating or drinking a food, answered from the rule the store keeps.

    "im vegetarian" / "do i eat meat" was answered "I'm not sure about that one, sorry" - a
    search hedge about something the person had just told the bot - because the confirmation
    reader looks for a fact of the same shape ("i eat meat") and what the store was told is the
    rule. Only a rule that takes the food off the table is answered: a food their rule allows is
    read by the kitchen entries, which know the substitutes, and a food no rule mentions is left
    to them as well.
    """
    line = " ".join(str(text or "").lower().split())
    match = EATING_ASK.match(LEAD_IN.sub("", line))
    if not match:
        return None
    category = _the_food_named(match.group(1).strip(" ?!."))
    if not category:
        return None
    known = user(memory)
    if not isinstance(known, dict):
        return None
    rule = _the_rule_that_rules_it_out(known, category)
    return rule or None


def _confirmation(text, memory):
    """Answer a yes/no question about something they told you, from what they told you."""
    statement = _statement(text)
    if not statement:
        return None
    if DUTY_ASK.search(statement):
        return None
    # "am i not allergic to nuts?" asks for the opposite yes or no.
    inverted = bool(re.search(r"\b(?:not|n't)\b", " ".join(text.lower().split())))
    found = extract.extract(statement)
    if not found:
        return None
    known = user(memory)
    yes, no, elsewhere = [], [], []
    for key, value in found.items():
        if key not in ("name", "age", "job", "city", "from", "diet", "budget", "allergies",
                       "pets"):
            continue
        stored = known.get(key)
        # A pet is read as a list even for one animal, and only a named one is an assertion.
        if key == "pets":
            value = [p for p in value if p.get("name") or p.get("animal")]
            if not value:
                continue
            value = value[0]
        # Only a fact the store actually holds is confirmed or denied: without it "am i right?"
        # would be read as a job ("i am right") and answered "No — you're ...".
        if not stored:
            # A fact they gave about someone else, asked about themselves: "my mums allergic to
            # nuts" then "am i allergic to nuts" is a no, and the honest answer says whose it is
            # rather than leaving the line to the general answer about allergies.
            theirs_who, theirs = _other_fact(memory, key)
            if theirs_who and theirs:
                elsewhere.append((key, theirs_who, theirs))
            continue
        matches = _said_matches(key, value, stored)
        if matches is None:
            continue
        if matches:
            yes.append(_clause(key, stored or value, known))
        elif _names(key, " ".join(text.lower().split())):
            said_back = _clause(key, stored if stored else value, known)
            if said_back:
                no.append(said_back)
    if inverted:
        yes, no = no, yes
    if not yes and not no:
        for key, who, theirs in elsewhere:
            if key == "allergies":
                return _their_allergy(who, theirs)
        return None
    if no and not yes:
        # "do i live in york or leeds?" is an either/or, so the answer is just the fact.
        if re.search(r"\bor\b", " ".join(text.lower().split())):
            return no[0][:1].upper() + no[0][1:] + "."
        return pick(["No — " + no[0] + ".", "Not quite — " + no[0] + "."], memory)
    said = "; ".join(yes[:2]) if yes else ""
    if no and yes:
        return pick(["Yes on one thing, no on another: " + said + ", but " + no[0] + ".",
                     "Partly — " + said + ", though " + no[0] + "."], memory)
    return pick(["Yes — " + said + ".", "That's right — " + said + ".",
                 "Yes, you told me — " + said + "."], memory)


def _limit_reply(memory, low=""):
    """What they can't have, said back: "what can't i eat", "what should i avoid", "what am i
    not allowed to eat". The ask names no subject of its own, so the answer is the limits they
    gave - an allergy, a diet, a condition - and nothing else about them."""
    known = user(memory)
    allergies = [str(a) for a in (known.get("allergies") or []) if str(a).strip()]
    conditions = known.get("condition") or []
    if isinstance(conditions, str):
        conditions = [conditions]
    conditions = [str(c) for c in conditions if str(c).strip()]
    diet = str(known.get("diet") or "").strip()
    # What they can't have is a list of food, so only a food can be said back as one. "im allergic
    # to penicillin" is a fact about medicine, and "nothing with penicillin in it" is a claim about
    # their dinner they never made; the store says nothing and the turn is left to the hedge it
    # would have had before.
    foods = [allergy for allergy in allergies if _a_food(allergy)]
    if not foods and not conditions and not diet:
        # Nothing is stored, so there is no limit to say back. When the line names food it is
        # still the limit ask and gets an honest answer; "what should I avoid" with no food word
        # in it is a question about whatever the conversation is on ("I want to paint my
        # kitchen"), and asking what to keep out of their food answers a question nobody asked.
        if not FOOD_ASK.search(low):
            return None
        # Unless they did tell us something a moment ago: "im pregnant" and "my son is allergic
        # to nuts" are not kept as limits, and "you haven't told me anything you can't have" flatly
        # denies the turn before. The honest line is only for a chat that said nothing at all.
        if _said_a_limit(memory):
            return None
        return ("You haven't told me anything you can't have. Say what to keep out of your food "
                "and I'll stick to it.")
    # Every limit the store keeps is about food, so it is said as the food it rules out: "what
    # can't i have" and "what should i avoid" are the same ask as "what can't i eat".
    clauses = []
    if foods:
        clauses.append("nothing with " + _said_list(foods) + " in it \u2014 you're allergic to "
                       + ("them" if len(foods) > 1 or foods[0].endswith("s") else "it"))
    if conditions:
        # A condition that rules a food out is said as the food, the way the bot answers it when
        # they first say it: "nothing with gluten in it - you're coeliac".
        ruled = [ack.CONDITION_FOOD.get(condition.lower()) for condition in conditions]
        if ruled and all(ruled):
            clauses.append("nothing with " + _said_list(ruled) + " in it \u2014 you're "
                           + _said_list(conditions))
        else:
            clauses.append("you're " + _said_list(conditions))
    if diet:
        ruled = _diet_food(diet)
        # "no meat" is already the food, so the label it would be said back with is the food too:
        # "nothing with meat in it - you're no meat" reads as a broken sentence. That shape keeps
        # the wording it had.
        if ruled and all(ruled) and not diet.lower().startswith("no "):
            # A diet is a list of food, so it is said the way an allergy is: the food first, the
            # reason after. "you're vegetarian" alone names no food at all.
            clauses.append("nothing with " + _said_list(ruled) + " in it \u2014 you're " + diet)
        else:
            clauses.append("you don't " + _diet_how(diet) + " " + diet[3:] if diet.startswith("no ") else
                           "you're " + diet)
    said = clauses[0]
    if len(clauses) == 2:
        said += ", and " + clauses[1]
    elif len(clauses) > 2:
        said += ", " + ", ".join(clauses[1:-1]) + ", and " + clauses[-1]
    said = said[:1].upper() + said[1:] + "."
    if _same_as_last(said, memory):
        # Asked again in the words of the ask ("what can't i have" after "what should i avoid"),
        # the same sentence twice in a row reads like a machine, and the turn would go to
        # whichever module says something else: the limit is still the answer, said afresh.
        said = _vary(["Still this: " + said[0].lower() + said[1:],
                      "That hasn't changed: " + said[0].lower() + said[1:],
                      "Same answer: " + said[0].lower() + said[1:]], memory)
    return said


def _who_is_the_name_reply(memory, low):
    """The person a name they gave belongs to: "Meg is your sister."

    A name is filed on the person (`others[...]["name"]`), so a line that asks about the name by
    itself is asking about someone the chat already knows. Only a name already filed is claimed:
    "who is the queen" and "whos bob" keep the reply they had. A relation the person was filed
    under is compared through the same concept table the recalls use, so "is meg my mum" after
    "my mother is called meg" is a yes and not a no.
    """
    if not isinstance(low, str):
        return None
    match = WHO_IS_NAME_ASK.search(low)
    if not match:
        return None
    parts = match.groupdict()
    said = (parts.get("name1") or parts.get("name2") or parts.get("name3")
            or parts.get("name4") or "").strip().lower()
    asked_who = (parts.get("who3") or parts.get("who4") or "").strip().lower()
    if asked_who.endswith("s") and asked_who[:-1] in extract.RELATIONS:
        asked_who = asked_who[:-1]
    if not said:
        return None
    if parts.get("name1") or parts.get("name2"):
        # Only the name on its own asks about the chat: "who is meg" is about the Meg they told me
        # about, and "who is meg on eastenders" is about a programme, which is a search, not a
        # claim. A made-up answer to a real question is worse than the hedge it replaces.
        group = "name1" if parts.get("name1") else "name2"
        tail = low[match.end(group):].strip(" \t?.,!;:'\"")
        if tail and not set(tail.split()) <= NAME_ASK_TAIL:
            return None
    for entry in reversed(others(memory) or []):
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name") or "").strip()
        who = str(entry.get("who") or "").strip().lower()
        if not name or not who or name.lower() != said:
            continue
        proper = _tidy_name(name)
        if asked_who:
            same = CONCEPTS.get(asked_who, asked_who) == CONCEPTS.get(who, who)
            if same:
                return _vary(["Yes - " + proper + " is your " + who + ".",
                              "That's right: " + proper + " is your " + who + "."], memory)
            return "No - " + proper + " is your " + who + "."
        return _vary([proper + " is your " + who + ".",
                      proper + " \u2014 your " + who + ", you told me.",
                      "That's " + proper + ", your " + who + "."], memory)
    for entry in reversed(others(memory) or []):
        # A group given whole ("my kids are called jack and emma") files both names on the one
        # entry and no name on either person, so the name on its own was read as somebody the
        # store had never heard of: "who is jack" two turns after both names were given. The
        # line said which people, not which one of them, so the answer says that and no more.
        if not isinstance(entry, dict):
            continue
        names = [str(one).strip() for one in (entry.get("names") or []) if str(one).strip()]
        who = str(entry.get("who") or "").strip().lower()
        if len(names) < 2 or not who or not any(one.lower() == said for one in names):
            continue
        proper = _tidy_name(next(one for one in names if one.lower() == said))
        if asked_who:
            same = CONCEPTS.get(asked_who, asked_who) in _relations_of(who)
            if same:
                return _vary(["Yes - " + proper + " is one of your " + who + ".",
                              "That's right: " + proper + " is among your " + who + "."],
                             memory)
            return proper + " is one of your " + who + ", not your " + asked_who + "."
        return _vary([proper + " is one of your " + who + " - you told me your " + who
                      + " are " + _a_list_of_names(names) + ".",
                      "One of your " + who + ": you said your " + who + " are "
                      + _a_list_of_names(names) + "."], memory)
    # The same thing for an animal: "i have a cat called tom" files the name on the pet, so
    # "whos tom" is a question about the chat and not about the world.
    for pet in (user(memory).get("pets") or []):
        if not isinstance(pet, dict):
            continue
        name = str(pet.get("name") or "").strip()
        if not name or name.lower() != said:
            continue
        proper = _tidy_name(name)
        animal = str(pet.get("animal") or "pet").strip().lower()
        if asked_who:
            same = CONCEPTS.get(asked_who, asked_who) == CONCEPTS.get(animal, animal)
            if same:
                return _vary(["Yes - " + proper + " is your " + animal + ".",
                              "That's right - " + proper + " is your " + animal + "."],
                             memory)
            return proper + " is your " + animal + ", not your " + asked_who + "."
        return _vary([proper + " is your " + animal + ".",
                      "That's " + proper + ", your " + animal + "."], memory)
    return None


def _kids_reply(memory, low):
    """How many children they have, said back: "You've got two kids."

    The number came with the children ("i have two kids"), so the ask is answered from the chat
    rather than hedged, and the line says the number they gave and nothing else.
    """
    if not _kids_ask(low):
        return None
    held = user(memory).get("kids")
    if isinstance(held, int) and held == 0 and not isinstance(held, bool):
        # A person who said they have none has answered the question: "i dont have any kids" then
        # "how many kids do i have" was told "You haven't told me how many kids you have yet".
        return _vary(["You told me you don't have any kids.",
                      "None \u2014 you said you don't have any.",
                      "You said you haven't got any kids."], memory)
    if held is None:
        # A child named without an age ("my son is four" said in words) is in `people` and not in
        # `others`, and it is still a child they have told us about.
        named = [entry for entry in (others(memory) or [])
                 if isinstance(entry, dict) and str(entry.get("who") or "").lower()
                 in CHILD_RELATIONS]
        if not named:
            named = [{"who": who} for who in (user(memory).get("people") or [])
                     if str(who).lower() in CHILD_RELATIONS]
        if named:
            who = str(named[0].get("who") or "child").lower()
            return _vary(["You've mentioned your " + who
                          + " \u2014 how many have you got altogether?",
                          "I know about your " + who + ", but not a number. How many have you "
                          "got in all?"], memory)
        # Their own children, not something to look up: the honest answer is that they have not
        # said, rather than a hedge about searching online for their own life.
        return _vary(["You haven't told me how many kids you have yet.",
                      "I don't have a number from you \u2014 how many have you got?",
                      "You haven't said how many children you've got."], memory)
    count = int(held)
    if count == 1:
        return _vary(["You've got one kid.", "One kid, as you told me.",
                      "You said you've got one kid."], memory)
    word = NUMBER_WORDS.get(count, str(count))
    kids = "children" if count == 2 else "kids"
    return _vary(["You've got " + word + " " + kids + ".",
                  word.capitalize() + " " + kids + " \u2014 that's what you told me.",
                  "You said you've got " + word + " " + kids + "."], memory)


def _a_thing_i_own_reply(memory, low):
    """The make of a thing they said was theirs: "your car is a Ford Fiesta".

    Only a thing the store was told the make of is given one. "my car is old" says nothing about
    the make, so the ask is answered by saying the make was never said rather than by guessing,
    and a thing the person never mentioned at all keeps the ordinary answer.
    """
    held = user(memory).get("owns")
    if not isinstance(held, dict) or not held:
        held = {}
    for match in OWNED_ASK.finditer(low):
        thing = next((word for word in match.groups() if word), "")
        thing = thing.replace("-", " ")
        if not thing:
            continue
        name = held.get(thing) or held.get(thing.rstrip("s"))
        if thing == "car" and not name:
            # "i drive an old fiesta" then "what car have i got": the fact reader holds the car
            # and this reader asks first, so without the fallback the store filed the car and
            # denied it in the next breath ("you haven't told me the make of your car").
            name = user(memory).get("car") or ""
        if thing == "car" and name:
            # One fact, one shape: a model is capitalised however the car was filed.
            return car_line(name)
        said = {"bike": ("You ride ", "Your bike is "),
                "motorbike": ("You ride ", "Your motorbike is ")}.get(thing)
        if name:
            article = _a_that_fits(name)
            if said:
                return pick([said[0] + article + " " + name + ".",
                             said[1] + article + " " + name + "."], memory)
            if thing == "phone":
                return pick(["Your phone is " + article + " " + name + ".",
                             "You've got " + article + " " + name + "."], memory)
            return pick(["Your " + thing + " is " + article + " " + name + ".",
                         "You told me your " + thing + " is " + article + " " + name + "."],
                        memory)
        if thing in extract.OWNED:
            # They asked about a thing nobody has mentioned the make of. Saying so is the honest
            # answer and it is not a denial: whatever they told me about the car is still true.
            return pick(["You haven't told me the make of your " + thing,
                         "You've not said what your " + thing + " is"], memory) + "."
    return None


def _about_the_children_reply(memory, low):
    """What the chat holds about the children as a group: "tell me about my kids".

    Every other ask in this family names one relation ("my mum", "my sister") and the store files
    one person under it. Children are the exception: "my kids are tom 8 and ada 5" files two
    people against the same word, so the ask about them reached no person at all and fell to the
    search hedge three turns after both names were given. The answer is the children the chat
    holds, each with the age or name it was told - and when only the count was given, the count.
    """
    if not CHILDREN_ABOUT.search(str(low or "")):
        return None
    kept = [entry for entry in others(memory) if isinstance(entry, dict)
            and _in_the_group(entry.get("who"), CHILD_RELATIONS)]
    clauses = []
    for entry in kept[:4]:
        name = _called(str(entry.get("name") or "")) if entry.get("name") else ""
        names = [str(one) for one in (entry.get("names") or []) if str(one).strip()]
        if len(names) > 1:
            # "my kids are called tom and ada" is one fact about several children, and the names
            # are the whole of it: without this branch the reply said the chat held nothing two
            # turns after the names were typed.
            clauses.append("your " + str(entry.get("who") or "children") + " are called "
                           + _a_list_of_names([_called(one) for one in names]))
        elif entry.get("ages"):
            # A group given its ages as a list - "my kids are 4 and 7" - is one fact about the
            # children, and the store kept it as a list. Read only as a single age, the group had
            # no clause at all and the answer was "You've told me you have two kids, and nothing
            # more about them yet" a turn after the ages were typed.
            ages = [age for age in entry["ages"] if isinstance(age, int)]
            who = str(entry.get("who") or "children")
            said = (", ".join(str(age) for age in ages[:-1]) + " and " + str(ages[-1])
                    if len(ages) > 1 else str(ages[0]))
            clauses.append("your " + who + _is_are(who) + said)
        elif entry.get("months") and not entry.get("age"):
            # A baby's age was given in months, and is said back in months.
            clauses.append((name or ("your " + str(entry.get("who") or "child")))
                           + " is " + str(entry["months"]) + " months old")
        elif entry.get("age") or entry.get("turns"):
            clauses.append(_one_age(str(entry.get("who") or "child"), entry.get("age"),
                                    str(entry.get("turns") or ""), entry.get("to_come"),
                                    held=name).strip().rstrip("."))
        elif name:
            clauses.append("your " + str(entry.get("who") or "child") + " is called " + name)
    # A clause that begins "Your son" is folded into the sentence and takes a small letter; a
    # clause that begins with a name keeps it, because Tom is spelled with a capital.
    clauses = [clause[0].lower() + clause[1:] if clause.startswith("Your ") else clause
               for clause in clauses]
    if not clauses:
        # A name given for the group in words the name readers did not file ("i have two kids"
        # then "they are called tom and ada") is still in the chat, and the group reply reads it
        # where "what are my kids called" reads it, so it never denies a name one turn later.
        typed = _the_group_names_typed("kids", memory) or _the_group_names_typed("children", memory)
        if typed:
            clauses = ["your kids are called " + _a_list_of_names([_called(one) for one in typed])]
    if not clauses:
        counted = (memory.get("user") or {}).get("kids")
        if isinstance(counted, int) and counted:
            return _vary(["You've told me you have " + _a_number_word(counted) + " "
                          + ("kid" if counted == 1 else "kids")
                          + ", and nothing more about them yet.",
                          "Just the count: " + _a_number_word(counted) + " kids, with no name or "
                          "age yet."], memory)
        return None
    # One child is "him" or "her", and a reply that says "them" about a single daughter reads as
    # a reply about somebody else. The word for the relation already knows: the pronoun follows
    # it, the way it does in every other reply the store writes.
    one = (str(kept[0].get("who") or "") if len(kept) == 1 else "")
    about = _object_pronoun(one) if one else "them"
    if len(clauses) == 1:
        # The same ask twice may not say the same sentence twice, so there is a second way to say
        # what is held. Neither says the chat holds nothing else: the clause is the fact, and
        # "and nothing else about them yet" behind the only fact there is reads as a denial.
        first = "You've told me " + clauses[0] + "."
        second = clauses[0][:1].upper() + clauses[0][1:] + " - that's all I've got on " \
            + about + "."
        return _vary([first, second], memory)
    facts = _a_list_of_clauses(clauses)
    # The reply may open with the facts themselves ("your son is 6 and ..."), and a sentence
    # starts with a capital.
    answer = _vary([facts + " - that's what I've got on " + about + ".",
                    "That's everything I have on " + about + ": " + facts + "."], memory)
    return answer[:1].upper() + answer[1:]


def _pet_breed_reply(memory, low):
    """The breed the chat was told, for "what breed is he", or None.

    Only when the line is about an animal the chat holds a breed for: one it names ("max"), the
    family it names ("my dog"), or a pronoun, which means the one the chat has just been on.
    "what kind of dog should i get" names no animal of theirs and is a question about the world.
    """
    if not BREED_WORD.search(low):
        return None
    pets = [pet for pet in (user(memory).get("pets") or [])
            if isinstance(pet, dict) and str(pet.get("breed") or "").strip()
            and not pet.get("not_theirs")]
    if not pets:
        return None
    asked = []
    family = ""
    animal = PET_ASK.search(low)
    if animal:
        family = _animal_family(animal.group(1))
    if family:
        asked = [pet for pet in pets if _animal_family(pet.get("animal")) == family]
    if not asked:
        for pet in pets:
            name = str(pet.get("name") or "").strip()
            if len(name) > 2 and re.search(r"\b" + re.escape(name.lower()) + r"\b", low):
                asked.append(pet)
    if not asked and re.search(r"\b(?:she|he|it|they|his|her|its|their)\b", low):
        asked = [pets[-1]]
    if not asked:
        return None
    pet = asked[-1]
    breed = str(pet.get("breed") or "").strip()
    name = str(pet.get("name") or "").strip()
    if not name:
        # "hes a labrador" gave the animal no name, so the breed is the only word the chat has
        # for it: "your labrador is a labrador" is the store saying its own word back.
        return _vary(["A " + breed + " - that is what you said.",
                      "You said a " + breed + ".",
                      "A " + breed + "."], memory)
    name = _tidy_name(name)
    return _vary([name + " is a " + breed + ".",
                  "You told me " + name + " is a " + breed + ".",
                  "A " + breed + ", that one."], memory)


def car_line(car):
    """The car said back, in one shape wherever it is asked for.

    The same fact was said two ways: the fact reader capitalised a model ("You drive a Corsa")
    and said a description as it came, while the thing-they-own reader said everything as it
    came - so "i drive a ford focus" came back lowercase from one reader and "a Corsa" from the
    other. The rule is the one a person uses reading it out: a model is a name and takes its
    capital, two words are both names ("a Ford Focus"), a describing word is not a name ("an old
    fiesta"), and a fuel or a body is not one either ("a diesel").
    """
    said = " ".join(str(car or "").split())
    if not said:
        return ""
    words = said.split()
    if any(word.lower() in CAR_DESCRIBED for word in words):
        return "You drive " + _a(said) + "."
    if len(words) == 1 and said.lower() in NO_CAP:
        return "You drive " + _a(said) + "."
    shown = " ".join(CAR_CAPS.get(word.lower(),
                                  word[:1].upper() + word[1:] if word.islower() else word)
                     for word in words)
    return "You drive " + _a(shown) + "."


def _birthday_in_words(memory):
    """A birthday they gave in words rather than as a date: "my birthday is tomorrow".

    A relative day is not a date the store can keep - next week "tomorrow" is wrong - so the line
    stays the plan it was read as. The summary already says "your birthday is tomorrow", so the
    ask has to say the same thing back: "you haven't told me" in the same conversation is the bot
    contradicting itself. Only their own birthday is read here, never one said of someone else.
    """
    for plan in reversed(user(memory).get("plans") or []):
        said = str(plan)
        match = extract.BIRTHDAY.search(said) or A_BIRTHDAY_PLAN.search(said)
        if not match or extract.subject(said, match.start())[0] == "other":
            continue
        if A_RELATIONS_BIRTHDAY.search(said):
            # "my sons birthday is tomorrow" is held as the plan "sons birthday tomorrow", and the
            # relation in front of it is what says whose date it is.
            continue
        words = " ".join(match.group(1).lower().split()).rstrip(" .,;:")
        words = re.sub(r"^(?:in|on)\s+", "", words)
        if words:
            return words
    return ""


def _the_same_relative(one, other):
    """Whether two words are the same person's relation: "mum" and "mums" are one mum."""
    one = str(one or "").lower()
    other = str(other or "").lower()
    if not one or not other:
        return False
    if one == other:
        return True
    return (other.endswith("s") and one == other[:-1]) or (one.endswith("s") and one[:-1] == other)


def _was_called(named):
    """The name of a pet that is gone: "Your cat was called Milly."."""
    if len(named) == 1:
        return ("Your " + str(named[0].get("animal") or "pet") + " was called "
                + _called(named[0].get("name")) + ".")
    parts = [str(pet.get("animal") or "pet") + " " + _called(pet.get("name")) for pet in named]
    return "You called them " + ", ".join(parts[:-1]) + " and " + parts[-1] + "."


def _a_pet_that_is_gone(gone):
    """A pet they no longer have, said back the way they told me: died, or gone elsewhere."""
    def one(pet):
        animal = str(pet.get("animal") or "pet")
        name = _called(pet.get("name"))
        return animal + " " + name if name else animal

    shown = [one(pet) for pet in gone]
    if len(shown) > 2:
        which = "any pets"
    elif len(shown) == 2:
        which = "your " + shown[0] + " or your " + shown[1]
    else:
        which = "your " + shown[0]
    if all(pet.get("gone") == "died" for pet in gone):
        return "I'm sorry \u2014 you told me " + which + " died."
    if not any(pet.get("gone") == "died" for pet in gone):
        return "You told me you don't have " + which + " any more."
    told_died = ["your " + shown[index] for index, pet in enumerate(gone)
                 if pet.get("gone") == "died"]
    return ("I'm sorry \u2014 you told me "
            + (" or ".join(told_died) if len(told_died) > 1 else told_died[0]) + " died.")


def _put_together(parts):
    """The pieces of a pet sentence as one phrase: "a dog", "a dog and a cat", "a, b and c"."""
    parts = [part for part in parts if part]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def _pets_together(pets):
    """Two or more of the same animal, each named: "two cats called Tom and Jerry", or None.

    Said one at a time they read like a list a machine wrote - "a cat called Tom and a cat called
    Jerry" - and the animal is the same both times, so it is said once with both names after it.
    """
    animals = [(p.get("animal") or "pet") for p in pets]
    if len(pets) < 2 or len(set(animals)) != 1:
        return None
    if not all(not p.get("count") for p in pets):
        return None
    named = [p for p in pets if p.get("name")]
    nameless = [p for p in pets if not p.get("name")]
    if not named:
        return None
    animal = animals[0]
    many = animal if animal.endswith(("fish", "sheep", "deer")) else animal + "s"
    count = len(pets)
    names = [_called(p.get("name")) for p in named]
    if len(nameless) == 1:
        # A second animal they have not named yet is not said as "a cat and a cat called Max",
        # which is two animals described one at a time and reads as a list a machine wrote. It is
        # the whole set said once, with the one name they gave and the gap beside it: "i have a
        # cat" then "my other cat is called Max" is "two cats - Max and one you haven't named".
        return (NUMBER_WORDS.get(count, str(count)) + " " + many + " \u2014 "
                + _put_together(names + ["one you haven't named"]))
    if len(nameless) > 1:
        return None
    return (NUMBER_WORDS.get(count, str(count)) + " " + many + " called "
            + ", ".join(names[:-1]) + " and " + names[-1])


def _a_pet(pet):
    """"a cat", "a cat called Milly", "two cats": a number they gave is said back as a number."""
    # The breed they named comes first: "we got a rescue greyhound" is said back as a greyhound.
    animal = str(pet.get("breed") or pet.get("animal") or "pet")
    count = pet.get("count") or 1
    if pet.get("name"):
        try:
            many = int(count) > 1
        except (TypeError, ValueError):
            many = False
        if many:
            # "i have 2 cats" then "and her name is biscuit" is two cats with one name between
            # them, and "a cat called Biscuit" answers it as one animal: the number they gave
            # stays in the reply.
            plural = animal if animal.endswith(("fish", "sheep", "deer")) else animal + "s"
            return (NUMBER_WORDS.get(int(count), str(count)) + " " + plural + ", one called "
                    + _called(pet.get("name")))
        return _a(animal) + " called " + _called(pet.get("name"))
    if int(count) > 1:
        many = animal if animal.endswith(("fish", "sheep", "deer")) else animal + "s"
        return NUMBER_WORDS.get(int(count), str(count)) + " " + many
    return _a(animal)


def _a_why_line_they_have_answered(text, memory):
    """A why-line the store can answer, because it holds the subject the line names."""
    low = " ".join(str(text or "").lower().split())
    return bool(re.search(r"\bwhy\b", low)) and _holds_the_subject(memory, text)


def _holds_the_subject(memory, text):
    """Whether the store has the thing a why-line names, so it can say what they said.

    The subject is read the way every other fact ask reads it, and then looked for where the
    store keeps it: nothing filed means nothing to say, and "you haven't told me" is not an
    answer to a question about the world.
    """
    key = recall.ask(text, why=True)
    if not key:
        return False
    known = user(memory) or {}
    held = known.get(_SUBJECT_KEYS.get(key, key))
    if key == "limit":
        return bool(held or known.get("diet") or known.get("limits"))
    return bool(held)


def _asks_for_a_fact(low, text="", memory=None):
    """True when the line asks for one of their own facts, in the words they use for it.

    "my dog", "allergic", "my budget" are the plain forms; "what pets do I have?" and "do I have
    any allergies?" the same asks without the word my. A line that asks what they said about
    something ("what did I say about the dog?") is a read of the chat, not a fact recall, and
    belongs to the store's own quote.
    """
    if re.search(r"\bmy (?:dog|cat|pet)s?\b", low) and ADVICE_ASK.search(low):
        return False
    # "why do I have allergies", "why do we have pets": the store has no cause to give, so a
    # why-ask is not a read of it - it was answered "You haven't mentioned an allergy to me."
    # over a line that never asked what they had said. The one exception is the subject they
    # have just said: "my dog is called rex" then "why do we have pets" is "You've got a dog
    # called Rex.", which is a warm and right answer, and a search hedge for it loses what
    # they told you (black-lantern on #4437). So the store speaks when it holds the subject
    # and stays quiet when it would only be saying it holds nothing.
    if re.search(r"\bwhy\b", low):
        return _holds_the_subject(memory, text)
    if re.search(r"\bmy (?:dog|cat|pet)s?\b|\ballerg\w*\b|\bmy budget\b", low):
        return True
    if re.search(r"\bwhat (?:did|have) i\b", low):
        return False
    return bool(ASK_WITHOUT_MY.search(low))


def _vary(options, memory):
    """pick(), but over the whole reply: a lead-in and a body put together can repeat a line
    the bot said, even when the pieces on their own do not."""
    turns = memory.get("turns") or []
    recent = {t.get("bot") for t in turns[-5:]}
    fresh = [o for o in options if o not in recent] or list(options)
    return random.Random(len(turns)).choice(fresh)
