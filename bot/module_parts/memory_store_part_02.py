"""Part 2 of 4 of a large module, split out of `memory_store`.

Everything here is re-exported from `memory_store`, so callers import it from there as before.
"""
import re

from ..memory import forget, last_user, log, name, others, remember, user
from ..memory import facts as extract
from ..memory import whathurts as a_hurting_part


from ..memory.store_lines import NOT_RETRACTED, PET_AGE_FIX_WORDS, AGE_FIX_WORDS, NAME_FIX_WORDS
from .memory_store_part_01 import (
    _kind, _on_record_before, extract, forget, _person_from_pronoun, others, _animal_family, re,
    last_user, user, ASK_WITHOUT_MY, A_HAVE_QUESTION, CANT_HAVE, CAN_HAVE, CAN_THEY_HAVE,
    HOW_MANY_OF_MINE, NAMED_FACT_ASK, OTHER_FACT, STATES_A_LIMIT, TOPIC_ASK, _a_bare_limit_ask,
    _asks_about_someone, _bare, _folded, _other_person_reply, WHERE_PLAN, DAY_IT, DAY_THING,
    TIME_ASKS, TIME_IT, TIME_THING, _plans_reply, ASK_ABOUT_THEM, EAT_ASK, _someone_else_named,
    CORRECTS_A_NAME, CORRECTS_A_NAME_POSSESSIVE, _name_they_answered, _the_animal_of_the_pick, name,
    remember, _a_number, PET_LEAD_IN, PET_NAME_AGE, AGE_FIX, CORRECTING, _PET_WORD, PET_AGE_ANSWER,
    PREGNANCY_SAID_AGAIN, WEEKS_FIX, A_NAME_WITH_ITS_VERB, ANOTHER_ANIMAL,
)


def _forget_denied(text, memory):
    """A line that says they do not have a fact takes the old one out of the store.

    "im coeliac" and then "im not coeliac", "im allergic to peanuts and nuts" and then "im not
    allergic to nuts": the same fact being taken back. A store that keeps it goes on warning
    about, or cooking around, the thing the person has just said they are fine with.
    """
    held = (memory.get("user") or {}).get("pets") or []
    denied = extract.denials(text, held)
    # A denial about somebody else comes back under its own key and comes off that person's
    # record, not the user's: "my son is allergic to nuts" then "he isnt allergic to nuts" left
    # the nuts on his list and answered "Your son is allergic to nuts." after the line that took
    # them back.
    theirs = denied.pop("theirs", None) if isinstance(denied, dict) else None
    # A pet that died is one they no longer have, but it is not a take-back to say back to them:
    # the loss is answered warmly, and "Right - no cat, then." is the wrong reply to a death.
    # The store still hears it, or it hands the animal back later ("what pets do i have" after
    # "my cat died" must not answer "You've got a cat called Milly.").
    died = [pet for pet in _losses_taking(text, held, memory)
            if str(pet.get("animal") or "") not in
            [_kind(item) for item in (denied.get("pets") or [])]]
    # "we gave one away" out of "i have two cats" names no animal, only a number: one cat goes,
    # and the store keeps the count straight instead of answering "You've got two cats."
    given = [pet for pet in extract.given_away_one(text, held)
             if pet not in [item for item in (denied.get("pets") or []) if isinstance(item, dict)]]
    if not denied and not theirs and not died and not given:
        return None
    gone = {}
    for key, value in denied.items():
        if key == "diet":
            value = _the_diet_they_are_back_on(memory, value)
        dropped = forget(memory, key, value, "gone")
        if key == "pets":
            # The store forgets either way; only a pet they had before is worth saying back.
            dropped = _on_record_before(memory, dropped)
        if dropped:
            gone[key] = dropped
            if key == "pets" and "*" in [str(item) for item in value]:
                # "no pets" took them all: the line says that, not the last animal left.
                gone["pets_all"] = True
    if died and forget(memory, "pets", died, "died"):
        gone["pets_died"] = True
    if given and forget(memory, "pets", given, "given away"):
        # One of a set is gone, not the whole kind: "Right - no cat, then." would say they have
        # none left, so the store hears it and the turn is answered like any other.
        gone["pets_given"] = True
    for entry in theirs or []:
        taken = _off_their_list(memory, entry, text)
        if taken:
            gone.update(taken)
            break
    if not gone:
        return None
    gone["said"] = " ".join(str(text or "").lower().split())
    memory["denial"] = gone
    return gone


def _the_back_on_the_plate(text, memory):
    """A line that puts back what somebody else does not eat takes it off their record.

    "my son doesnt eat fish" then "actually he eats fish": the store kept "no fish" against him
    and went on answering "what does my son eat" with "Your son doesn't eat fish.", which is the
    opposite of the last thing the person said. A taste is the same shape - "my wife hates
    mushrooms" then "actually she loves them" puts mushrooms on her likes and off her dislikes.
    Only what is already on that person's record is lifted, so a line that describes somebody for
    the first time ("my son eats fish") is left to the modules that read it on its own.
    """
    for said in extract.their_back(text):
        who = str(said.get("who") or "").strip() or _person_from_pronoun(text, memory)
        if not who:
            continue
        for record in others(memory):
            if str(record.get("who") or "").lower() != who.lower():
                continue
            kind = said.get("kind")
            food = str(said.get("food") or "").strip()
            if food.lower() in ("them", "it", "that"):
                # "actually she loves them" names the food only by pointing at it, and there is
                # one thing on her record to point at or the line cannot be read at all.
                food = _the_one_they_are_back_on(record, kind)
            if not food:
                continue
            if kind == "diet":
                held = str(record.get("diet") or "").lower()
                if held not in ("no " + food.lower(), "no " + food.lower() + "s"):
                    continue
                # The restriction is gone and the food they do eat takes its place: the record
                # says "eats fish" so "what does my son eat" answers with it, not with a blank.
                record["diet"] = "eats " + food
            else:
                gone = [str(item) for item in (record.get("dislikes") or [])]
                if food.lower() not in [item.lower() for item in gone]:
                    continue
                record["dislikes"] = [item for item in gone if item.lower() != food.lower()]
                likes = [str(item) for item in (record.get("likes") or [])]
                if food.lower() not in [item.lower() for item in likes]:
                    likes.append(food)
                record["likes"] = likes
            memory["reversal"] = {"who": who, "food": food, "kind": kind,
                                  "said": " ".join(str(text or "").lower().split())}
            return True
    return False


def _the_one_they_are_back_on(record, kind):
    """The one thing on a person's record a "them" can point at, or "" when there are two.

    "my wife hates mushrooms" then "actually she loves them" is mushrooms because they are the
    only thing she does not like; with mushrooms and olives both on the list the pointing word
    says nothing, and guessing one of them would put a taste in her mouth she never gave.
    """
    if kind == "diet":
        held = str(record.get("diet") or "").strip()
        return held[3:].strip() if held.lower().startswith("no ") else ""
    gone = [str(item) for item in (record.get("dislikes") or [])]
    return gone[0] if len(gone) == 1 else ""


def _off_their_list(memory, entry, text):
    """The take-back a line makes about somebody else, taken off the record kept for them.

    "my son is allergic to nuts" then "he isnt allergic to nuts": the store files facts about
    other people under their own entry, so the denial has to find that entry and name the person
    it belongs to when it says the note back - "Nuts back on the table, then." reads as the
    speaker's own allergy, which they never mentioned.

    The note is said even when they never had it on record: "my daughter is 6" then "she isnt
    allergic to eggs" is a thing the person said about her, and the fallback's "I'm listening"
    is no answer to it.
    """
    items = [str(item) for item in (entry.get("allergies") or []) if str(item)]
    if not items:
        return None
    who = str(entry.get("who") or "") or _person_from_pronoun(text, memory)
    if not who:
        return None
    taken = []
    for record in others(memory):
        if str(record.get("who") or "") != who:
            continue
        held = [str(item) for item in (record.get("allergies") or [])]
        left = [item for item in held if item.lower() not in {one.lower() for one in items}]
        if len(left) == len(held):
            continue
        taken.extend(item for item in held if item not in left)
        record["allergies"] = left
    return {"allergies": items, "who": who}


def _the_diet_they_are_back_on(memory, value):
    """The diet as the store holds it, when the take-back names only the food.

    "im cutting out sugar" is kept as that whole phrase, and the line that takes it back can
    name nothing but the food - "im back on sugar", "im eating bread again". Matched against the
    phrase word by word, or `forget` finds nothing and the store goes on telling them to avoid
    what they eat now.
    """
    held = (memory.get("user") or {}).get("diet")
    said = " ".join(str(value or "").lower().split())
    if not isinstance(held, str) or not said:
        return value
    if said in " ".join(held.lower().split()):
        return held
    return value


def _the_last_line(memory):
    """The line just before this one, so a bare "he died" can point back at what it named.

    "i have a dog" then "he died" is the dog; "my grandad is in hospital" then "he died" is the
    grandad. Without the turn behind it a "he" says too little, and taking the only animal off the
    store on that is the worst thing this reader could do.
    """
    turns = (memory or {}).get("turns") or []
    if not turns:
        return ""
    return str((turns[-1] or {}).get("user") or "")


def _losses_taking(text, held, memory=None):
    """The animals a line about a death takes off the store, one record at a time.

    "my cat died" from someone with two cats is one of them: the store keeps the other instead of
    answering "you haven't told me about a pet yet" a turn after they grieved one. "both cats
    died" is the whole lot.
    """
    said = str(text or "").lower()
    everything = bool(extract.LOSS_ALL.search(said))
    taken = []
    before = _the_last_line(memory)
    for kind in extract.losses(text, held, before):
        same = [pet for pet in held if isinstance(pet, dict)
                and _animal_family(pet.get("animal")) == _animal_family(kind)]
        if not same:
            continue
        if everything:
            taken.extend(pet for pet in same if pet not in taken)
            continue
        named = [pet for pet in same if pet.get("name") and
                 re.search(r"\b" + re.escape(str(pet["name"]).lower()) + r"\b", said)]
        # "rex died in january" is about Rex and not about Sam: the animal they named goes.
        taken.append(named[-1] if named else same[-1])
    return taken


def _last_stated(memory):
    """The facts the line before this one put in the store."""
    said = " ".join(str(last_user(memory) or "").lower().split())
    if not said:
        return []
    kept = []
    for entry in log(memory):
        if not isinstance(entry, dict):
            continue
        if " ".join(str(entry.get("text") or "").lower().split()) != said:
            continue
        kept.append(entry)
    return kept


def _retract_last(memory, text=""):
    """A line that takes back the last thing they said without naming it: "take that back", "scratch
    that".

    "im allergic to peanuts and shellfish" then "take that back" left the allergy on record and the
    next ask answered "You told me you're allergic to peanuts, shellfish" - a note they had just
    asked to take off. A retraction names no value, so the only thing it can be about is the line
    before it: every fact that line put in the store goes. A taste or a fact about someone else is
    left alone - those are not what "take that back" means, and losing them silently would be worse
    than keeping them.
    """
    gone, shown = [], []
    for entry in _last_stated(memory):
        key = entry.get("key")
        value = entry.get("value")
        if key == "pet":
            # The animal is taken off the record outright, not filed under `pets_gone`: that list is
            # for a pet that died or went to a new home, and answering "you don't have your dog
            # Biscuit any more" tells them about a loss they never mentioned.
            known = user(memory)
            pets = [pet for pet in (known.get("pets") or []) if pet is not value and pet != value]
            if len(pets) != len(known.get("pets") or []):
                if pets:
                    known["pets"] = pets
                else:
                    known.pop("pets", None)
                gone.append("pets")
                animal = (value or {}).get("animal") or (value or {}).get("name") or "pet"
                shown.append(str(animal))
            continue
        if key == "plans":
            known = user(memory)
            if forget(memory, "plans", [value]):
                gone.append("plans")
                shown.append(str(value))
            if known.get("plan") == value:
                known.pop("plan", None)
            continue
        if key in NOT_RETRACTED:
            continue
        dropped = forget(memory, key, value)
        if dropped:
            gone.append(key)
            shown.extend(str(item) for item in dropped
                         if not isinstance(item, dict))
    if not gone:
        return None
    if any(key in ("plans", "places") for key in gone):
        # The trip went with the plan, so the where ask names what they took back instead of an
        # empty store ("You haven't mentioned a place yet" denies the trip they just discussed).
        # As the store held it, not lower-cased: the place is a name, and "Sri Lanka is off" is
        # the trip said back where "Sri lanka" is the line read aloud.
        user(memory)["plan_dropped"] = str(shown[0])
    memory["retraction"] = {"said": " ".join(str(text or "").lower().split()),
                            "keys": gone, "shown": shown}
    return memory["retraction"]


def _reads_the_store(text, memory=None):
    """True for a line that only asks for something already kept, so it states nothing new.

    `facts` extracts what a line mentions, and an ask mentions the very thing it wants back:
    "i'm allergic to nuts" then "am i allergic to peanuts or shellfish?" used to keep both and
    answer *you're allergic to nuts, peanuts or shellfish* - a claim they never made.

    An ask about a person's allergy or a food they cannot have is the same kind of line: it
    names nothing of its own and asks for a fact the store keeps ("my son is allergic to nuts"
    then "what is he allergic to" was answered with what an allergy is, by a topic entry that
    matched the word). Said with nobody the store knows, it claims nothing.
    """
    if not isinstance(text, str):
        return False
    low = _bare(_folded(text, memory))
    if NAMED_FACT_ASK.search(low) or TOPIC_ASK.search(low) or ASK_WITHOUT_MY.search(low) \
            or HOW_MANY_OF_MINE.search(low):
        return True
    if not (OTHER_FACT.search(low) or CANT_HAVE.search(low) or CAN_HAVE.search(low)
            or CAN_THEY_HAVE.search(low)
            # "what can she not eat" and "remind me what hes allergic to" name a limit and a
            # person, and the person is a pronoun with nobody behind it, so the asks that need a
            # relation never took the line. EAT_ASK is deliberately not in this list: "and how
            # long do i need for the chicken" has an eating word in it and is the answers lane's,
            # and read as an ask that names nothing it stopped the store filing the chicken, so
            # the next turn of a roast conversation answered about hens.
            or _a_bare_limit_ask(low, memory)):
        return False
    if not _asks_about_someone(low, text, memory):
        return False
    whole = " ".join(str(text or "").lower().split())
    if STATES_A_LIMIT.search(whole) and not A_HAVE_QUESTION.search(whole):
        # The line says the limit and asks about it in one breath: "my son is 7 and has a nut
        # allergy, what is he allergic to". The fact is the line's own and keeping it is another
        # reading's job, so this one stands down. Claimed here, the store told a person who had
        # just said their son has a nut allergy that it had not been told about an allergy, and
        # the answer it took the turn from was a real one.
        return False
    said = _other_person_reply(memory or {}, low)
    # The reader only says whose fact is missing when the line does name a person it can read
    # (a relation, a name the store knows, or a "he" that points at one), so that line is the
    # store's own too: "is he allergic to anything" after three people were named was answered
    # with what to check on a label, as if "he" were the person typing.
    return bool(said)


# A line that only asks for something already kept is the store's own, whatever else proposed.
# "what were we up to?" after a Spanish lesson was answered by `answers` with the previous
# paragraph and *Same as before:* in front of it: the line carries no topic of its own, so the
# specialist rule read the conversation's topic (school-and-study) on it and handed the turn to
# the module that declares that topic. A read of the store is not about the topic it names, so
# the store says which of its own proposals this is, on the line in front of it, and the arbiter
# takes its word (bot/modules/arbiter.py, `TAKES_AS_IT_COMES`).
# Three asks the store must win even against a specialist module, and all are the arbiter's one
# hook: a read of the store ("what were we up to?") that is not about the topic it names, the ask
# whose answer is a line they said themselves ("what was i cooking?" is not a request for the
# recipe), and a `when` ask it can place - the date is in what the person said, whether they ask
# for it again ("when is that again" after a dentist appointment) or ask for the day the work for
# a plan goes on ("when is the best time to prep for it" after a work thing on friday, which the
# answers module took with the entry about revising because "best time" is in the ask).
# `_the_prep_day` says which asks of that second shape the store can really answer: with no day to
# add to the plan it has nothing to say, so an ask about the world ("when is the best time to take
# a mortgage") and an ask about a thing with an answer of its own ("when is the best time to book
# it") are left to whoever can answer them. The composition is here, after every reader, so
# neither name shadows the other.
def _the_plan_they_took_back(text, memory):
    """A where ask about a trip they have just taken back is the store's line, not a repeat.

    "im going to lisbon in may" / "take it back" / "where am i going" was answered "Same as
    before: In Lisbon: Alfama on foot and the 28 tram..." - the trip's paragraph read back to
    someone the bot had just told "Right, that place is off the record, then." The ask names no
    subject of its own, so the knowledge base leaned on the topic record for the line they had
    just retracted and the answer on the screen came back. The store is the one part that knows
    the plan went: its own answer to a where ask names what was taken back ("Lisbon is off, then
    - where are you going?"). Only a where ask, and only while the thing they took back is the
    newest thing in the store, so every other line after a take-back is read exactly as before.
    """
    if not isinstance(memory, dict):
        return False
    gone = user(memory).get("plan_dropped")
    if not isinstance(gone, str) or not gone.strip():
        return False
    low = " ".join(str(text or "").lower().split())
    return bool(WHERE_PLAN.search(low))


def _the_clock_in_their_line(text, memory):
    """True when the ask wants a clock or a day the person gave, and the store can place it.

    "what time is my appointment" after "i have a dentist appointment on friday at 3" was
    answered "Ring practices near you and ask straight out whether they take new NHS patients":
    the store had the hour and proposed it, but the claim that hands the store its own asks was
    gated on the word "when", so a clock ask fell to the knowledge base's entry about the same
    noun. The hour or the day is in what the person said, so the ask is the store's - and every
    such ask it cannot place (no plan naming it, nothing to read the hour off) is left alone,
    which keeps "what time do i start work" with whoever can answer it.
    """
    try:
        low = text.lower()
        if not (TIME_ASKS.search(low) or TIME_THING.search(low) or TIME_IT.search(low)
                or DAY_THING.search(low) or DAY_IT.search(low)):
            return False
        return bool(_plans_reply(memory, low))
    except Exception:  # noqa: BLE001 - a claim that cannot be read is not a claim
        return False


def _an_ask_about_someone_else(text, memory):
    """True when the line asks about a fact the store keeps for someone else.

    "i'm cooking for my mother in law on sunday" then "shes vegetarian" then "is she vegetarian"
    is an ask about the mother in law, and the diet is on record; the knowledge base reads the
    word "vegetarian" and offers a curry instead, so the store has to say the line is its own
    (`TAKES_AS_IT_COMES` below). Only a line that names or points at a person whose fact is on
    record is claimed: with nothing stored for them the ask goes to whoever can answer it.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return False
    if not ASK_ABOUT_THEM.search(text.strip()):
        return False
    keys = []
    if OTHER_FACT.search(text):
        keys.append("allergies")
    if EAT_ASK.search(text):
        keys.append("diet")
    if not keys:
        return False
    try:
        who = _someone_else_named(_bare(_folded(text, memory)), memory)
    except Exception:  # noqa: BLE001 - a line that cannot be read claims nothing
        return False
    if not who:
        return False
    for known in others(memory):
        if known.get("who") == who:
            return any(known.get(key) for key in keys)
    return False


def _the_take_back_about_someone(text, memory):
    """A line that takes a fact back off somebody else's list is the store's, not the topic's.

    "my son is allergic to nuts" then "he isnt allergic to nuts" was answered with the nut-free
    lecture from the knowledge base: the line names nuts, so `answers` read food on it and took
    the turn from the store that had just taken them off his list. The store's note is about
    what the chat keeps, not about nuts, so it says so in front of its reply.
    """
    gone = memory.get("denial") if isinstance(memory, dict) else None
    if not isinstance(gone, dict) or not gone.get("who"):
        return False
    return gone.get("said") == " ".join(str(text or "").lower().split())


def _the_part_that_hurts_asked(text, memory):
    """The ask for the part that hurts, and the side it was said with.

    "my knee hurts", then "its on the outside of the knee", then "and which knee was it" is
    answered from what the person said, so nothing that only echoes their last line can take the
    turn: `You said: "its on the outside of the knee"` says their own words again and answers
    nothing. The claim is made for every line the hurting-part reader can answer, and for no
    other.
    """
    if not isinstance(memory, dict):
        return False
    low = " ".join(str(text or "").lower().split())
    return bool(low) and bool(a_hurting_part.the_part_asked(memory, low))


def _name_the_last_pet(text, memory):
    """"we've also got a cat" then "and her name is Biscuit" is one cat with a name.

    A name given a second time is a correction when the line opens like one - "sorry, his name
    is milo" after "we have a dog called max". The store kept the first name and said it back
    ("You've got a dog called Max") while the person had already taken it back, and the same line
    with the old name on the end ("sorry, his name is milo not max") was read as not having a dog
    at all. Only the opener makes it a rename: "we have a dog called max / his name is milo" on
    its own is the same dog said twice as easily as a correction.
    """
    if not isinstance(text, str):
        return
    pets = user(memory).get("pets")
    named = pets[-1] if isinstance(pets, list) and pets and isinstance(pets[-1], dict) else {}
    # The lower-case shape is only read when there is a pet to put the name on, which is here.
    name = extract.pet_name_only(text, lower=bool(named)) or _name_they_answered(text, memory)
    if not name:
        return
    if not isinstance(pets, list) or not pets:
        # The name can come before the animal is in the store: "im getting a dog" / "what should
        # i name it" / "milo" keeps no dog yet, and the name is the one thing that turn gave.
        # The animal is the one the list or the question was about, so the pet is filed whole.
        animal = _the_animal_of_the_pick(memory)
        if not animal or animal == "pet":
            return
        remember(memory, "pets", [{"animal": animal, "name": name}], text)
        return
    last = pets[-1]
    if isinstance(last, dict) and not last.get("name"):
        last["name"] = name
        kept = {"animal": last.get("animal", "pet"), "name": name}
        if isinstance(last.get("count"), int) and last["count"] > 1:
            kept["count"] = last["count"]
        remember(memory, "pets", [kept], text)
        return
    # A correction that names the animal it is about ("no the cat is called tom") is that
    # animal's rename and nobody else's: `_fix_a_pets_name` has already moved the name on the cat,
    # and putting it on the pet said last as well renamed the dog in a house with one of each.
    if isinstance(last, dict) and str(last.get("name") or "").lower() != name.lower() \
            and (CORRECTS_A_NAME.match(text) or CORRECTS_A_NAME_POSSESSIVE.match(text)) \
            and not _names_a_pet_here(text, memory):
        # The one on record is the same animal under the name they have just taken back, so the
        # entry is renamed rather than a second one added: "we have a dog called max / sorry his
        # name is milo" is one dog, not two.
        before = str(last.get("name") or "")
        last["name"] = name
        log(memory).append({"key": "pet", "value": {"animal": last.get("animal"), "name": name},
                            "turn": len(memory.get("turns") or []), "text": text})
        # The name on record is kept beside the new one, so the next line about the pet still
        # finds it: "my dog is called rex" then "his names actually rocky" then "how old is
        # he" answered with a memory trick about names, because the dog under Rocky was a
        # different dog from the one under Rex.
        if before and before.lower() != name.lower():
            was = [str(old) for old in (last.get("was") or []) if str(old).lower() != name.lower()]
            last["was"] = was + [before]
        # The person is told which name the bot goes with rather than having their own line
        # handed back, and it is the pet's own note: the two-name shape ("Rocky, not Rex — got
        # it.") reads to the next module as a conversation about names rather than about the
        # dog, and "how old is he" then got a tip on remembering names.
        if before:
            memory["correction"] = {"key": "pet", "value": name,
                                    "animal": last.get("animal") or "pet",
                                    "said": " ".join(str(text or "").lower().split())}


def _the_animals_named(text, memory):
    """The animals of the store's pets the line names: "no the cat is called tom" names the cat."""
    low = " ".join(str(text or "").lower().split())
    here = set()
    for pet in (user(memory).get("pets") or ()):
        if not isinstance(pet, dict) or not pet.get("animal"):
            continue
        animal = str(pet["animal"]).lower()
        if re.search(r"\b" + re.escape(animal) + r"s?\b", low):
            here.add(animal)
    return here


def _the_name_it_had(animal, said, memory):
    """The name the store had for this animal before the line that named it again."""
    for entry in reversed(log(memory) or ()):
        value = entry.get("value") if isinstance(entry, dict) else None
        if not isinstance(value, dict):
            continue
        if str(value.get("animal") or "").lower() != animal:
            continue
        name = str(value.get("name") or "")
        if name and name.lower() != str(said or "").lower():
            return name
    return ""


def _names_a_pet_here(text, memory):
    """Whether the line names an animal the store keeps a pet of ("the cat", "the dogs")."""
    low = " ".join(str(text or "").lower().split())
    for pet in (user(memory).get("pets") or ()):
        if not isinstance(pet, dict) or not pet.get("animal"):
            continue
        if re.search(r"\b" + re.escape(str(pet["animal"]).lower()) + r"s?\b", low):
            return True
    return False


def _the_figure_said(match):
    """The age a reader's own regex caught, as a number, whether it was digits or a word."""
    said = str(match.group("age") or "").strip().lower()
    if not said:
        return None
    value = _a_number(extract.FIGURE_WORDS.get(said, said))
    return value if isinstance(value, int) else None


def _without_a_lead_in(text):
    """The line with the lead-ins people open a short sentence with taken off."""
    said = str(text or "").strip()
    for _ in range(4):
        shorter = PET_LEAD_IN.sub("", said, count=1)
        if shorter == said:
            break
        said = shorter.strip()
    return said


def _put_a_pets_age(pet, age, unit, text):
    """Store an age on one animal, or None when it already says exactly that."""
    if pet.get("age") == age and str(pet.get("unit") or "") == unit:
        return None
    pet["age"] = age
    pet.pop("unit", None)
    if unit:
        pet["unit"] = unit
    return {"key": "pet", "value": dict(pet), "text": text}


def _age_the_named_pet(text, memory):
    """"my dog is called fred" then "fred is 5" is an age for the dog, not a fact about nobody.

    The line names no animal at all, only the name the store has for one, so the store is what
    says whose age it is. Without this the 5 went nowhere and "how old is fred" had no answer.
    """
    if not isinstance(text, str):
        return None
    low = _without_a_lead_in(text).lower()
    match = PET_NAME_AGE.match(low)
    if not match:
        return None
    age = _the_figure_said(match)
    if not 0 < age <= 30:
        return None
    unit = "months" if str(match.group("unit") or "").lower().startswith("month") else ""
    said = low.strip().split()[0].strip(".,!?") if low.strip() else ""
    pets = user(memory).get("pets")
    if not isinstance(pets, list):
        return None
    for pet in reversed(pets):
        if not isinstance(pet, dict) or str(pet.get("name") or "").lower() != said:
            continue
        return _put_a_pets_age(pet, age, unit, text)
    return None


def _fix_a_pets_age(text, memory):
    """"my dog is 5" then "sorry he is 6": the correction goes on the animal it corrects.

    The line names no animal - it names a pronoun and a figure - and the store already has one
    age for the animal the chat is on, so that is the age the figure replaces. Read the same way
    a person's corrected age is read (`_fix_a_persons_age`): only a short line, only with a
    correction word in it, and only when there is an age stored to replace, because a
    correction replaces a fact rather than being the first one said.

    Without this the store kept the old figure and the bot said it as fact: "my dog is 5" /
    "sorry he is 6" / "how old is my dog" answered "Your dog is 5." after the person had said 6.
    """
    said = " ".join(str(text or "").lower().split())
    low = _without_a_lead_in(said)
    # The correction word is one of the lead-ins, so it has to be read off the line as it was
    # said, before the lead-in comes off.
    if not low or len(low.split()) > PET_AGE_FIX_WORDS or not CORRECTING.search(said):
        return None
    if _PET_WORD.search(low):
        return None  # "my dog is 6" names the animal and is a fact of its own
    match = AGE_FIX.search(low)
    if not match:
        return None
    age = _the_figure_said(match)
    if not 0 < age <= 30:
        return None
    who = _person_from_pronoun(low, memory)
    if who and any(str(known.get("who") or "") == who and "age" in known
                   for known in others(memory)):
        # "my dog is 5" / "my son is 7" / "actually hes 8": the pronoun points at a person, and
        # a person's corrected age is read by `_fix_a_persons_age`. It is one figure, not both.
        return None
    unit = "months" if re.search(r"\bmonths?\b", low) else ""
    aged = [pet for pet in (user(memory).get("pets") or [])
            if isinstance(pet, dict) and pet.get("age") is not None]
    if len(aged) != 1:
        # Two animals with ages and no animal named: the pronoun is the only thing to go on, and
        # "they are 6" is not a correction of either of them.
        return None
    return _put_a_pets_age(aged[0], age, unit, text)


def _age_said_of_the_only_animal(text, memory):
    """"i have a greyhound called sid" then "hes 6": the figure is that animal's age.

    `_age_they_answered` reads a bare figure only when the bot asked for one, so a figure the
    person volunteers ("hes 6", "shes 12 now") went nowhere and "how old is sid" answered that
    they had never said. It is only read when the line before it named an animal or the one the
    store knows by name, and when the chat holds one animal - with two, "hes 6" says nothing
    about which one.
    """
    said = " ".join(str(text or "").lower().split())
    if not said or len(said.split()) > 5:
        return None
    previous = " ".join(str(last_user(memory) or "").lower().split())
    pets = [pet for pet in (user(memory).get("pets") or []) if isinstance(pet, dict)]
    if len(pets) == 1:
        pet = pets[0]
    else:
        # With more than one animal, the one the line before named is the one the pronoun is:
        # "rufus is a terrier" then "hes two" is Rufus's age, and Nell's is not known. Any other
        # line before it leaves the pronoun pointing at nobody in particular.
        named = [one for one in pets
                 if len(str(one.get("name") or "").strip()) > 2
                 and re.search(r"\b" + re.escape(str(one["name"]).strip().lower()) + r"\b",
                               previous)]
        if len(named) != 1:
            return None
        pet = named[0]
    if int(pet.get("count") or 1) > 1:
        # "i have two cats" is one record for two animals, so a pronoun and a figure do not say
        # which of them it is.
        return None
    name = str(pet.get("name") or "").strip().lower()
    called = [str(pet.get(word) or "").strip().lower() for word in ("animal", "breed")]
    if not (_PET_WORD.search(previous)
            or (len(name) > 2 and name in previous)
            or any(len(word) > 2 and word in previous for word in called)):
        return None
    if not re.search(r"\b(?:he|she|it|they)(?:'s|s|\s+is|\s+are)?\b", said):
        # A figure with no pronoun is someone else's unless the bot asked for it: the line has to
        # say whose age it is.
        return None
    match = PET_AGE_ANSWER.match(said)
    if not match:
        return None
    age = _the_figure_said(match)
    if not 0 < age <= 30:
        return None
    if _person_from_pronoun(said, memory):
        # "hes 8" after "my son has a dog" is the son, and a person's age is not the animal's.
        return None
    unit = str(match.group("unit") or "").lower()
    unit = "months" if unit.startswith("month") else ("weeks" if unit.startswith("week") else "")
    return _put_a_pets_age(pet, age, unit, text)


def _age_they_answered(text, memory):
    """The bot asked how old their animal was, so the figure in this line is that animal's age:

        i have a dog / You haven't told me how old your dog is. / hes 3

    A bare age names nobody, so it is read only when the reply before it asked, the same way a
    bare name is only read when the bot asked for one.
    """
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    asked = str(turns[-1].get("bot") or "")
    if "how old" not in asked.lower():
        return None
    pets = [pet for pet in (user(memory).get("pets") or []) if isinstance(pet, dict)]
    if not pets:
        return None
    # Only an animal was asked about: a figure given after "how old is your daughter" is not the
    # dog's age, so the question has to name an animal, or a name the store has for one.
    names = [str(pet.get("name") or "").strip().lower() for pet in pets]
    if not (_PET_WORD.search(asked) or any(
            name and re.search(r"\b" + re.escape(name) + r"\b", asked.lower()) for name in names)):
        return None
    match = PET_AGE_ANSWER.match(str(text or ""))
    if not match:
        return None
    age = _the_figure_said(match)
    if not 0 < age <= 30:
        return None
    unit = str(match.group("unit") or "").lower()
    unit = "months" if unit.startswith("month") else ("weeks" if unit.startswith("week") else "")
    for pet in reversed(pets):
        if pet.get("age") == age and str(pet.get("unit") or "") == unit:
            return None
        pet["age"] = age
        pet.pop("unit", None)
        if unit:
            pet["unit"] = unit
        # The store took a figure the person gave to the bot's own question, so the reply says it
        # back ("Noted: your cat is 4.") rather than a line that would fit any message at all.
        memory["pet_age"] = dict(pet)
        return {"key": "pet", "value": dict(pet), "text": text}
    return None


def _their_name_answered(text, memory):
    """The person's own name, given as the answer to the bot's own question:

        can you remember my name / I don't know it yet - you haven't said / sam
        can you remember my name / I don't know it yet - you haven't said / its sam

    A word on its own says nothing, so it is read as a name only when the reply right before it
    asked for one, and only when no name is on record yet ("sam" to a bot that already has the
    name is something else). "its" in front of the word is only an introduction there.
    """
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    if user(memory).get("name"):
        return None
    asked = str(turns[-1].get("bot") or "")
    if memory.get("asked_for") != "name" or not extract.USER_NAME_ASKED.search(asked):
        return None
    # The hedge comes off first: "its sam by the way" and "sam, btw" are the one word the store
    # waits for with three more around it, and read whole they were nothing at all.
    answered = extract.without_the_hedges(text)
    match = extract.NAME_ANSWER_ANNOUNCED.match(answered)
    if match:
        return extract.reads_as_a_name(match.group(1))
    last = extract.NAME_ANSWER_ANNOUNCED_LAST.search(answered)
    if last:
        # "i havent told you, its sam": the name is still the last thing said, after the apology
        # for not having given it, and the store was waiting for exactly this.
        return extract.reads_as_a_name(last.group(1))
    return extract.reads_as_a_name(answered)


def _fix_a_persons_age(text, memory):
    """Put a corrected age on the person the pronoun points at.

    "my son is 7" then "actually hes 8" leaves the store saying 7 while the bot has already said
    "Got it - he's 8.", so the person thinks the correction landed. The line names no relation,
    so who it is about comes from the pronoun, and the age it replaces has to be one the store
    already has.
    """
    low = " ".join(str(text or "").lower().split())
    if not low or len(low.split()) > AGE_FIX_WORDS or not CORRECTING.search(low):
        return None
    match = AGE_FIX.search(low)
    if not match:
        return None
    age = _the_figure_said(match)
    if not 0 <= age <= 120:
        return None
    who = _person_from_pronoun(low, memory)
    if not who:
        return None
    for known in others(memory):
        if known.get("who") == who and "age" in known:
            known["age"] = age
            known.pop("turns", None)
            log(memory).append({"key": "other", "value": dict(known),
                                "turn": len(memory.get("turns") or []), "text": text})
            return known
    return None


def _fix_the_weeks_of_a_pregnancy(text, memory):
    """Move the length the store holds to the one this line gives, for the person it points at."""
    low = " ".join(str(text or "").lower().split())
    if not low or len(low.split()) > 8:
        return None
    match = WEEKS_FIX.search(low)
    if not match:
        return None
    # A line that states the pregnancy again ("my wife is 12 weeks pregnant") is read by the
    # extractor, which files the new length itself; this is for the line that only moves it.
    if PREGNANCY_SAID_AGAIN.search(low):
        return None
    weeks = int(match.group("weeks"))
    if not 1 <= weeks <= 45:
        return None
    if not (CORRECTING.search(low) or re.search(r"\b(?:now|today)\b", low)):
        return None
    # The subject of the line decides whose length it moves, exactly as it does for a line that
    # states the pregnancy: "im 14 weeks now" is theirs, "she's 10 weeks now" is hers, and a chat
    # that has both on file must not move the wrong one.
    said_mine = re.search(r"\b(?:im|i'm|i am|i)\b", low)
    said_theirs = re.search(r"\b(?:my|our|she|he|they|her|his|their|hers)\b", low)
    own = user(memory) or {}
    if said_mine and not said_theirs and own.get("pregnant"):
        # A line about the person themselves: "im 14 weeks now", "actually im 16 weeks". Their own
        # pregnancy is kept on them, not in `others`, so nothing moved it: the bot agreed ("got it
        # - you're 14 weeks now") while "how far along am i" still answered 12.
        remember(memory, "weeks", weeks, text)
        return dict(own, weeks=weeks)
    who = _person_from_pronoun(low, memory)
    if not who:
        return None
    for known in others(memory):
        if known.get("who") == who and known.get("pregnant") and "weeks" in known:
            known["weeks"] = weeks
            known.pop("turns", None)
            log(memory).append({"key": "other", "value": dict(known),
                                "turn": len(memory.get("turns") or []), "text": text})
            return known
    return None


def _fix_a_pets_name(text, memory):
    """A pet's name put right in the sentence moves the name on the pet.

    "my cat is called milo" then "no hes called max": the person correction path needs a pointer
    to a relation and a name that is a spelling of the old one, and a pet is neither, so the store
    kept Milo and the next ask answered Milo. The pet is the animal the line names, or else the
    pet the turn before was about.
    """
    from ..memory import rename as pet_rename  # the rename frame: see bot/memory/rename.py
    low = " ".join(str(text or "").lower().split())
    moves = pet_rename.moves(low)
    if not low or len(low.split()) > NAME_FIX_WORDS or not (CORRECTING.search(low) or moves):
        return None
    match = A_NAME_WITH_ITS_VERB.search(low)
    # A correction says the name with its verb ("no hes called max"); a rename says it at the end
    # of the line, with the verb about the animal in front ("we renamed him max").
    raw = ""
    if match:
        raw = match.group("name") or ""
    elif moves:
        raw = pet_rename.the_name_a_line_moved_on(
            low, user(memory).get("pets"), bool(extract.PETS.search(low)))
    if not raw:
        return None
    said = extract._finish(raw)
    if not said or extract._not_a_name(raw, strict_ly=False):
        return None
    pets = [pet for pet in (user(memory).get("pets") or ()) if isinstance(pet, dict)]
    named = [pet for pet in pets if pet.get("name")]
    target = None
    # The line that names the animal it is about ("no the cat is called tom") has already been
    # carried out by the facts reader: the store keeps one pet an animal, so filing "a cat called
    # tom" replaced the cat called milo. Nothing is left to move, and going on to look for a pet
    # anyway found the pet said last - the dog, in a house with one of each - and renamed that.
    if _names_a_pet_here(text, memory):
        if _another_animal_is_named(text):
            # "no my other cat is called max", "no we also have a cat called max": the word says
            # the name belongs beside the pet already there, so nothing is put right.
            return None
        for animal in sorted(_the_animals_named(text, memory)):
            kept = _pets_of(animal, pets)
            if not kept:
                continue
            filed = [pet for pet in kept if _a_pet_new_this_line(pet, memory)]
            older = [pet for pet in kept if not _a_pet_new_this_line(pet, memory)]
            if older:
                # The line that names the animal files the name it says ("no the cat is called
                # max" filed a cat called max), so that entry is the line's own echo. In a house
                # of one the facts reader files it over the cat already there and nothing is
                # left to move; in a house of two the cat it was filed beside is still there and
                # the name belongs on that one - the cat said last. Either way the entry the
                # line added is not a pet of its own.
                target = older[-1]
                if str(target.get("name") or "").lower() != said.lower():
                    target["name"] = said[:1].upper() + said[1:]
                    target.pop("turns", None)
                    was = _the_name_it_had(animal, said, memory)
                    if was and not (isinstance(memory.get("correction"), dict)
                                    and memory["correction"].get("said") == low):
                        memory["correction"] = {"key": "pet", "value": target["name"],
                                                "wrong": was[:1].upper() + was[1:],
                                                "animal": animal, "said": low, "text": text}
                for pet in filed:
                    if pet is not target and pet in (user(memory).get("pets") or ()):
                        user(memory)["pets"].remove(pet)
                return None
            for pet in filed:
                # A pet given its first name: the facts reader filed it as the line said it
                # ("max"), and a name on a pet is read back the way a name is written.
                pet["name"] = said[:1].upper() + said[1:]
                was = _the_name_it_had(animal, said, memory)
                if was and not (isinstance(memory.get("correction"), dict)
                                and memory["correction"].get("said") == low):
                    memory["correction"] = {"key": "pet", "value": pet["name"],
                                            "wrong": was[:1].upper() + was[1:],
                                            "animal": animal, "said": low, "text": text}
            return None
    if _another_animal_is_named(text):
        # "no my other cat is called max" names a second cat, not a name taken back: the store
        # keeps one pet an animal, so the facts reader files the new one and this line adds it.
        return None
    here = [pet for pet in pets
            if pet.get("animal")
            and re.search(r"\b" + re.escape(str(pet["animal"]).lower()) + r"s?\b", low)]
    # The line that renames also names the animal ("no the cat is called tom"), so the facts
    # reader has already filed a second cat of the new name: that entry is this line's echo, not
    # a pet of its own, and counting it would leave two cats matching the word "cat" and send the
    # correction on to the pet said last - the dog, in a house with one of each.
    here = [pet for pet in here if str(pet.get("name") or "").lower() != said.lower()]
    if len(here) == 1:
        target = here[0]
    else:
        for key in ("name", "animal"):
            found = [pet for pet in named if _the_turn_before_said(pet.get(key), memory)]
            if found:
                # The line says "he", and in "i have two cats called milo and tom" the he is
                # the one said last, so the pet named last in the same line is the one the
                # correction is about. A house of one pet is unaffected.
                target = found[-1]
                break
    if target is None:
        return None
    before = str(target.get("name") or "")
    if before.lower() == said.lower():
        # The name said again is the name already on file: nothing was put right.
        return None
    target["name"] = said[:1].upper() + said[1:]
    target.pop("turns", None)
    # The correction is the turn's news, said with the store's own correction note ("Max, not
    # Milo — got it."), unless the line already left one of its own.
    kept_note = memory.get("correction")
    if not (isinstance(kept_note, dict) and kept_note.get("said") == low):
        memory["correction"] = {"key": "pet", "value": target["name"],
                                "wrong": before[:1].upper() + before[1:],
                                "animal": str(target.get("animal") or "pet"),
                                "said": low, "text": text}
    # The line that renames also names a pet ("no, my cat is called max"), so the facts reader
    # has just filed a second cat of that name beside the one being renamed. One cat a person
    # names once: the renamed entry is the whole of what that line says.
    animal = str(target.get("animal") or "").lower()
    for other in list(pets):
        if other is target:
            continue
        if (str(other.get("animal") or "").lower() == animal
                and str(other.get("name") or "").lower() == said.lower()):
            pets.remove(other)
    user(memory)["pets"] = pets
    # The store keeps every pet it had: a rename is one animal under a new name, not the whole
    # household. Writing the renamed pet back on its own dropped the others - "i have two cats
    # called milo and tom" then "no hes called max" left one cat, and the count answer was
    # "You've got one cat" against two lines of what the person told us.
    log(memory).append({"key": "pet", "value": dict(target),
                        "turn": len(memory.get("turns") or []), "text": text})
    return target


def _pets_of(animal, pets):
    """The pets of one animal in the store's list, in the order the store keeps them."""
    return [pet for pet in pets if isinstance(pet, dict)
            and str(pet.get("animal") or "").strip().lower() == animal]


def _a_pet_new_this_line(pet, memory):
    """Whether this pet entry was filed by the line being read.

    The store before the line was read is carried in the memory for the length of the turn
    (`_pets_before`), so an entry that was not there before is the line's own: it is the name
    the line said, filed beside the pets it was filed with, and not a pet of its own.
    """
    held = memory.get("_pets_before") if isinstance(memory, dict) else None
    if not isinstance(held, set) or not isinstance(pet, dict):
        return False
    return (str(pet.get("animal") or "").strip().lower(),
            str(pet.get("name") or "").strip().lower()) not in held


def _another_animal_is_named(text):
    """Whether the line says the name belongs to another animal, not the one on record."""
    return bool(ANOTHER_ANIMAL.search(" ".join(str(text or "").lower().split())))


def _two_of_the_animal_are_kept(pets, animal):
    """Whether the store holds more than one pet of this animal.

    When it does, a name filed against that animal was filed beside the pet already there. A
    rename leaves one entry (the rename drops the echo the same line filed), so two entries of
    the animal said with the new name is the store keeping both, not one name put right.
    """
    kept = [pet for pet in pets if isinstance(pet, dict)
            and str(pet.get("animal") or "").lower() == animal]
    return len(kept) > 1


def _the_turn_before_said(word, memory):
    """Whether the line before this one said this word about the pet in question."""
    turns = memory.get("turns")
    if not word or not isinstance(turns, list) or not turns:
        return False
    last = next((turn for turn in reversed(turns) if isinstance(turn, dict)), None)
    said = " ".join(str((last or {}).get("user") or "").lower().split())
    if not said:
        return False
    return bool(re.search(r"\b" + re.escape(str(word).lower()) + r"s?\b", said))
