"""Part 11 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import content, current, forget, keywords, last_user, name, recent, thread, user
from ..memory import change as a_change
from ..memory import condition
from ..memory import facts as extract
from ..knowledge import cooking
from ..memory import history
from ..memory import narrow
from ..memory import named as named_thing
from ..memory import recall
from ..memory import reminded
from ..memory import whathurts as a_hurting_part
from ..memory.topics import STOPWORDS
from ..memory.repeat import a_narrowing_and_its_line as _a_narrowing_and_its_line
from ..memory.store_lines import (
    PREGNANT_OWN_SAY, PREGNANT_SAY, PREGNANT_WEEKS_SAY, LIMIT_SAY, FEEDING_SAY, STATE_WAS_SAY,
    A_SHORT_ANSWER,
)
from ..memory.relations import _a, _animal_family, _called, _every_line, _person_from_pronoun
from ..modules.memory_tables import SAID_ASK
from bot.memory.corrected import _asks, _many
from .store_replies_part_01 import (
    ASKS_IT_BACK, THEIR_NAMES, _the_line_before_is_their_own_animal, DIET_FACT_ASK, OTHER_ASK,
    REMINDER_MID, DIET_ASK, DIET_HOW_TO, _a_count_ask, WHOLE_ASK, STOPWORDS, FIRST_ASK,
)
from .store_replies_part_02 import (
    _their_allergy, THING_AGAIN, _which_thing_was_it,
)
from .store_replies_part_03 import (
    _diet_words, _other_fact, _the_take_back, _count_of_a_kind,
)
from .store_replies_part_04 import (
    MEAL_WANTED, PLAN_DIETS, WAY_OF_EATING, WAS_A_STATE, ALLERGY_IN_THE_WORLD, A_HOW_TO_ASK,
    A_RECALL_WORD, ANSWER_MODULES, FIGURE_REPEAT, NOD_WORDS, THEIR_OWN_ASK, ASKS_IN_LINE,
    A_CLAIM_OF_TELLING, A_ROLE, JUDGING, PRONOUN_ASK, REFLEXIVE, A_BARE_PUT_RIGHT, A_FIGURE,
)
from .store_replies_part_05 import (
    _a_take_back_said_back, _deny, _diet_how, _a_number_word,
)
from .store_replies_part_06 import (
    _their_own_diet, _the_ask_beats_the_receipt,
)
from .store_replies_part_07 import (
    _vary, _a_pet, _a_pet_that_is_gone, _pets_together, _put_together, _was_called, car_line,
)
from .store_replies_part_08 import (
    _birthday_reply, _height_reply, _weight_reply, _adds_something, _just_a_hello, _recap,
    _about_kind, _alike, _corrects, _seen, _content_words, _the_last_ask_about_the_bot,
)
from .store_replies_part_09 import (
    _summary_reply,
)
from .store_replies_part_10 import (
    _about_this_chat, _repeat_ask, _hearing_again, _carries_something, _trim, _recall_quote,
)


def _the_names_again(folded, low, memory):
    """The names of their animals, asked back with the pronoun instead of the animal.

    "we got three kittens, pip, squeak and nibble" then "what are they called again?" is a read of
    the store, and the store holds all three names: the reply is one sentence with them in it. Only
    a line that points back ("again", "remind me") and only when a pet of theirs is named, so a
    question about the world ("i saw two birds in the garden" then "what are they called") is left
    to whoever can answer it, and a store with no pet in it never denies one they never claimed.
    """
    if not isinstance(low, str) or not low.strip():
        return ""
    # "again" is filler the ask is bare of, so the pointer back is read on the line as typed.
    if not ASKS_IT_BACK.search(str(folded or low)) or not THEIR_NAMES.search(low):
        return ""
    pets = [pet for pet in (user(memory).get("pets") or []) if isinstance(pet, dict)]
    if not pets:
        # No animal of theirs is on record, so this pronoun points at something out in the world:
        # the store says nothing rather than deny a pet they never claimed.
        return ""
    if not _the_line_before_is_their_own_animal(memory):
        # The pronoun is pointing at animals that are not theirs: "my neighbour has two cats" then
        # "what are they called again", two dogs met in the park, a sister's dogs. A store that
        # holds their own animals would answer with those names, which is the one mistake a memory
        # answer must not make.
        return ""
    # The same sentence the store gives for "what are my cats called", composed from a line that
    # names nothing: reading the ask itself lets its numbers and its nouns into the answer ("i met
    # two dogs" narrowed the list to dogs, and two names then came out as "one called Rufus and a
    # dog called Nell").
    return _fact_reply(memory, "what are my pets called", "pet")


def _diet_reply(memory, low=""):
    """How they eat, said back when they ask: "You told me you're vegetarian."

    The diet is kept on every line they say it in, so the answer is the fact and nothing else.
    A diet stored as a negation comes back with its verb ("you don't eat meat"), because "you're
    no meat" says nothing. What they cannot eat is not one key, though: "im coeliac" is a
    condition and "im allergic to nuts" is an allergy, and a question about the fact is about
    all of it - so the read says back whichever the store holds, and only when the line asks
    about the fact (a line asking for a meal keeps its meal).
    """
    # A line that reports a change to the diet, or asks for one, is not a request for the fact
    # and not a gap in it: "i want to lose a bit of weight" then "ive changed my diet" was
    # answered "You haven't told me about your diet", a denial of what they had just said.
    said = a_change.reported(low, "diet")
    if said:
        was = user(memory).get("diet")
        if said == "changed" and was:
            # The reply says what it is doing with the old value ("You were vegetarian, so I'll
            # drop that"), so the store has to do it: "im vegetarian" / "i changed my diet" /
            # "am i vegetarian" said "Yes - you're vegetarian" and "what can i cook" still picked
            # the vegetarian dish, so the bot promised a drop and went on quoting the value.
            forget(memory, "diet", [was])
            user(memory)["diet_changed"] = was
        return a_change.reply(said, "diet", was=was)
    diet = user(memory).get("diet")
    if not diet:
        if str(low or "") and not DIET_FACT_ASK.search(str(low or "")) \
                and _food_facts(memory):
            # A meal ask ("what do i eat") after they have told the store what they cannot eat is
            # a question about the food, and "You haven't told me about your diet" is a claim
            # about the person that is false when the store is holding it. What the store can say
            # about the dinner is what each meal has to leave out, so that is what it says, and
            # the kitchen picks the dish ("im allergic to nuts" then "what do i eat" was the
            # denial, and "im coeliac" then "what do i eat" was the same one a key over).
            #
            # This is asked before the fact said back, because the fact said back is a fallback
            # for lines with no meal ask and it was written when the meal rows answered this one;
            # saying "You told me you're allergic to nuts" to "what do i eat" answers nothing.
            left_out, said_so = _what_a_dinner_has_to_leave_out(memory)
            if left_out:
                return ("Nothing with " + _say_a_list(left_out) + " in it — " +
                        " and ".join(said_so) + ". Tell me what is in the fridge and I'll pick "
                        "a dinner around it.")
        kept = _food_facts(memory)
        if kept:
            # The store holds what they cannot eat, so a denial would be false whatever the
            # line's shape: "im allergic to nuts / im coeliac / what do i eat" was answered
            # "You haven't told me about your diet." Saying the fact back is the honest reply.
            return "You told me you're " + _say_a_list(kept) + "."
        if DIET_FACT_ASK.search(str(low or "")):
            kept = _food_facts(memory)
            if kept:
                return "You told me you're " + _say_a_list(kept) + "."
        who, theirs = _other_fact(memory, "diet")
        if theirs and who:
            return ("You haven't told me about yours \u2014 the diet you mentioned is your "
                    + who + "'s.")
        changed_from = user(memory).get("diet_changed")
        if changed_from and DIET_FACT_ASK.search(str(low or "")):
            # The change was said and the value it named was dropped, so the store holds nothing
            # and "You haven't told me about your diet" would deny the change they just reported.
            was = str(changed_from).strip()
            was = ("not eating " + was[3:] if was.lower().startswith("no ")
                   else "being " + _diet_words(was))
            return "You told me your diet had changed from " + was + ". What is it now?"
        take_back, gone = _the_take_back(memory, "diet")
        if gone:
            # They took a diet back, so they have said how they eat: nothing is in the store
            # because the take-back emptied it, and the honest answer is their own take-back
            # said back rather than denying the whole thing.
            return _a_take_back_said_back(take_back, gone)
        return _deny(memory, "diet", "You haven't told me about your diet.",
                     own=_their_own_diet)
    diet = str(diet)
    if MEAL_WANTED.search(str(low or "")) and not DIET_FACT_ASK.search(str(low or "")):
        # A dinner is the kitchen's to answer, and it is told about the diet on the way past. The
        # store's job on this line is only to keep what they said; saying it back answers a
        # question nobody asked, in the words they used to ask it.
        left_out, said_so = _what_a_dinner_has_to_leave_out(memory)
        if left_out:
            return ("Nothing with " + _say_a_list(left_out) + " in it \u2014 " +
                    " and ".join(said_so) + ". Tell me what is in the fridge and I'll pick a "
                    "dinner around it.")
        return None
    if diet.startswith("no "):
        return "You told me you don't " + _diet_how(diet) + " " + diet[3:] + "."
    if diet in WAY_OF_EATING:
        return "You told me you're " + _diet_words(diet) + "."
    if diet in PLAN_DIETS:
        # A plan is something they are doing, not something they are: "you're keto" is not it.
        return "You told me you're doing " + _diet_words(diet) + "."
    return "You told me you're " + diet + "."


def _a_pregnancy_of_their_own(text, memory, low):
    """The person's own pregnancy said back, with the length that dates it: "Lovely news - 12 weeks."

    A pregnancy said about themselves is the same fact as one said about their wife, and the
    store kept only the second: "im 12 weeks pregnant" was congratulated ("That's great news -
    nice one. What's next?") and then forgotten, so "how far along am i" after it got a search
    hedge, and the weeks the person had just given were nowhere.
    """
    if not isinstance(text, str) or "?" in text:
        return None
    if _about_this_chat(text, memory) or OTHER_ASK.search(low) or REMINDER_MID.search(low):
        return None
    found = extract.extract(text)
    if not found.get("pregnant"):
        return None
    if isinstance(found.get("weeks"), int):
        weeks = _a_number_word(int(found["weeks"]))
        return _vary([line.format(weeks=weeks) for line in PREGNANT_OWN_SAY], memory)
    # A length nobody said is not one to invent: the pregnancy is said back without it, and the
    # ask about how far along answers honestly that it was never given.
    return _vary(["Good to know — I'll keep the drink out of anything I suggest, and the weeks "
                  "are worth telling me if you want a meal plan that fits them.",
                  "Noted, and congratulations. Nothing alcoholic in anything I suggest; say if "
                  "you want a hand with what to cook."], memory)


def _a_state_told(text, memory, low):
    """A state of another person, said back: "Noted - your wife is pregnant..."

    The line is a fact, not a symptom, so it must not go to whoever answers a worry about someone
    ("my wife is pregnant so she cant drink" was answered "What has your wife said about it - and
    how long has it been like this?"). Only a statement is read: a question asks and changes
    nothing.
    """
    if not isinstance(text, str) or "?" in text:
        return None
    if _the_ask_beats_the_receipt(text, memory):
        # The line ends on a question the cards can answer, so the fact is only what that question
        # is about: filing it is the whole job, and the receipt is a line nobody asked to have said
        # back. "my sister is veggie ... what can i cook" gets the dinner card, not "Your sister is
        # veggie."
        return None
    if _about_this_chat(text, memory) or OTHER_ASK.search(low) or REMINDER_MID.search(low):
        return None
    found = extract.extract(text)
    if found.get("diet") or found.get("allergies") or found.get("pregnant"):
        return None  # a line about the person typing is theirs, and the modules for it are theirs
    named = [who for who in (found.get("people") or []) if isinstance(who, str)]
    for entry in found.get("others") or []:
        who = entry.get("who") or _person_from_pronoun(text, memory, named)
        if not who:
            continue
        if entry.get("pregnant") and isinstance(entry.get("weeks"), int):
            # The length is what makes the fact worth keeping: said back without it the store
            # has read the line and still sounds like it did not hear the half that dates it.
            weeks = _a_number_word(int(entry["weeks"]))
            return _vary([line.format(who=who, weeks=weeks) for line in PREGNANT_WEEKS_SAY],
                         memory)
        if entry.get("pregnant"):
            return _vary([line.format(who=who) for line in PREGNANT_SAY], memory)
        if entry.get("breastfeeding"):
            return _vary([line.format(who=who) for line in FEEDING_SAY], memory)
        if entry.get("drinks") is False:
            return _vary([line.format(who=who) for line in LIMIT_SAY], memory)
    return None


def _a_state_that_was(text, memory, low):
    """A pregnancy or a feeding that is over, acknowledged as the past thing it is.

    The line is not asked for and not planned round: a person who says "my wife was pregnant"
    has told the chat something that was true, and both readers that used to take it - the one
    that congratulates and the one that advises on trying for a baby - were reading the word and
    not the tense.
    """
    if not isinstance(text, str) or "?" in text:
        return None
    if _about_this_chat(text, memory):
        return None
    if not WAS_A_STATE.search(" ".join(str(text or "").split())):
        return None
    return _vary(list(STATE_WAS_SAY), memory)


def _fact_reply(memory, low, key=None):
    """The reply for one of their facts. key is the fact already read from the ask, so a wording
    the words do not name ("how much can I spend" is a budget) still gets the right answer."""
    # A how-to in front of the fact word is advice, not a recall of it - unless a recall word is
    # in the line, which is the ask underneath the shape.
    if low and A_HOW_TO_ASK.search(str(low)) and not A_RECALL_WORD.search(str(low)):
        return None
    known = user(memory)
    if key == "allergy" or "allerg" in low:
        if ALLERGY_IN_THE_WORLD.search(str(low or "")):
            return None
        allergies = known.get("allergies") or []
        if allergies:
            said = ", ".join(allergies)
            plain = "You told me you're allergic to " + said + "."
            # Asked twice in a row ("what am i allergic to", then "again"), the same
            # sentence twice reads like a machine, so the phrasing rotates - the way the
            # budget answer already does. The list itself is the answer either way.
            if plain in {turn.get("bot") for turn in memory.get("turns") or []}:
                return _vary(["It's " + said + " — that's what you said.",
                              "Still " + said + ".",
                              "Your allergy is " + said + "."], memory)
            return plain
        if "allergies" in known:
            # The list is still there and empty: they named one and then took it back, so the
            # answer is that nothing is on it, not that they never said anything. The one they
            # took back is still in the correction of that turn, so it can be named.
            fixed = memory.get("correction") if isinstance(memory, dict) else None
            gone = str((fixed or {}).get("value") or "").strip().lower()
            if gone and fixed.get("dropped"):
                return "Nothing on the list now — you took the " + gone + " one back."
            return "Nothing on the list now."
        who, theirs = _other_fact(memory, "allergies")
        if theirs and who:
            return _their_allergy(who, theirs)
        if theirs:
            return ("You haven't mentioned one for yourself \u2014 the allergy to "
                    + ", ".join(theirs) + " you mentioned was someone else's.")
        return _deny(memory, "allergy", "You haven't mentioned an allergy to me.")
    if key == "budget" or "budget" in low:
        budget = known.get("budget")
        if not budget:
            return _deny(memory, "budget", "You haven't told me a budget.")
        # The first answer is the plain sentence; asked again, a different phrasing, because
        # the same sentence twice in a row reads like a machine.
        plain = "Your budget is " + budget + "."
        if plain in {turn.get("bot") for turn in memory.get("turns") or []}:
            return _vary(["It's " + budget + " — that's what you told me.",
                          "You said " + budget + ".", "Still " + budget + "."], memory)
        return plain
    if key == "birthday":
        return _birthday_reply(memory)
    if key == "weight":
        return _weight_reply(memory)
    if key == "height":
        return _height_reply(memory)
    if key == "diet" or (DIET_ASK.search(low) and not DIET_HOW_TO.search(low)):
        return _diet_reply(memory, low)
    if key == "car" or recall.DRIVE_ASK.search(low):
        car = known.get("car")
        if car:
            return car_line(car)
        return pick(["You haven't told me what you drive.",
                     "I don't know your car \u2014 you haven't said."], memory)
    pets = known.get("pets") or []
    gone = [p for p in (known.get("pets_gone") or []) if isinstance(p, dict)]
    asked = None
    # "what is my dog called?" is about the dog, not the cat: read the animal they named.
    for animal, words in (("dog", "dog puppy"), ("cat", "cat kitten"),
                          ("rabbit", "rabbit bunny"), ("hamster", "hamster"),
                          ("fish", "fish goldfish"), ("horse", "horse pony"),
                          ("parrot", "parrot bird")):
        # "whats my dogs name" is the same ask as "what is my dog called": people type both.
        if re.search(r"\b(?:" + words.replace(" ", "|") + r")s?\b", low):
            # "what's my dog called?" is about the puppy too: a young animal is the same animal.
            asked = animal
            pets = [p for p in pets if _animal_family(p.get("animal")) == animal]
            gone = [p for p in gone if _animal_family(p.get("animal")) == animal]
            break
    coming_only = [p for p in pets if isinstance(p, dict) and p.get("coming")]
    if coming_only and len(coming_only) == len(pets) and not re.search(r"\b(?:called|name)\b",
                                                                     low):
        # "what pets do i have" about an animal that is on its way: the store holds it because
        # the follow-ups need it, and the sentence says it is coming rather than here.
        pieces = []
        for pet in coming_only:
            count = pet.get("count") if isinstance(pet.get("count"), int) else 1
            pieces.append(_many(count, pet.get("animal") or "pet") if count > 1 else _a_pet(pet))
        due = _put_together(pieces)
        if due:
            return "You're getting " + due + "."
    counted = _a_count_ask(low)
    if pets and counted is not None:
        # "how many cats" asks for the number, not for the list: "You've got two cats" and not
        # "two cats, Milly and Fred", which answers a question they did not ask and reads as
        # more animals than they have.
        kinds = {_animal_family(p.get("animal")) for p in pets}
        total = _count_of_a_kind(pets)
        if len(kinds) == 1 and (counted in ("any", "pet") or kinds == {counted}):
            animal = _animal_family(pets[0].get("animal"))
            if total == 1:
                # One animal, named: the number is what they asked for and the name is theirs,
                # so both survive - "You've got a dog." throws the name away.
                was = _called(pets[0].get("name"))
                if was:
                    return "You've got one " + animal + " \u2014 " + was + "."
                return "You've got " + _a(animal) + "."
            return "You've got " + _a_pet({"animal": animal, "count": total}) + "."
    if pets:
        if re.search(r"\b(?:called|name)\b", low) and not any(p.get("name") for p in pets):
            return "You haven't told me a name for your " + pets[0].get("animal", "pet") + " yet."
        together = _pets_together(pets)
        if together:
            return "You've got " + together + "."
        # "how many dogs do i have" asks for the number, so the number is the answer even when
        # the dog has a name: "two dogs" says how many, "a dog called Rex" does not.
        counted = bool(re.search(r"\bhow many\b", low))
        if counted and len(pets) == 1:
            # One animal, named: "how many dogs do i have" is still asking for the number, and
            # "You've got a dog called Biscuit" does not give it. The name is kept beside it.
            pet = pets[0]
            animal = pet.get("animal") or "pet"
            number = pet.get("count") if isinstance(pet.get("count"), int) else 1
            number = max(int(number), 1)
            many = _many(number, animal) if number > 1 else "one " + animal
            was = _called(pet.get("name"))
            return "You've got " + many + (" — " + was + "." if was else ".")
        if counted and len(pets) > 1 and len({_animal_family(p.get("animal")) for p in pets}) == 1:
            top = max([p["count"] for p in pets if isinstance(p.get("count"), int)] or [0])
            if top >= len(pets):
                # The count is the whole set: "we have two cats, milly and fred" put right with
                # "sorry, 3 cats" is three cats, not three cats and a cat called Fred.
                return "You've got " + _many(top, pets[0].get("animal") or "pet") + "."
        parts = [(_many(p["count"], p.get("animal") or "pet")
                  if counted and isinstance(p.get("count"), int) and p["count"] > 1
                  else _a_pet(p)) for p in pets]
        # An animal on its way is not one in the house: "we are getting a puppy next week" then
        # "what pets do i have" answered "You've got a puppy" about one still with its mother. The
        # animal stays in the store - "what do i need to buy first" and "will they get on" need it
        # - and this sentence is the one that says which of them are here and which are coming.
        here = [part for pet, part in zip(pets, parts) if not pet.get("coming")]
        due = [part for pet, part in zip(pets, parts) if pet.get("coming")]
        said = []
        if here:
            said.append("You've got " + _put_together(here) + ".")
        if due:
            said.append("You're getting " + _put_together(due) + ".")
        if said:
            return " ".join(said)
    if gone:
        # "what was my cat called?" asks after a death, in the past tense on purpose: the name is
        # the thing they want back, so it is the name they get.
        was_called = re.search(r"\b(?:was|were|did)\b", low) and re.search(
            r"\b(?:call|called|name|named)\b", low)
        named = [pet for pet in gone if pet.get("name")]
        if was_called and named:
            return _was_called(named)
        # A pet they told me about and then lost is not a pet they never mentioned: say what they
        # said, warmly, rather than answering "you haven't told me about a pet yet".
        return _a_pet_that_is_gone(gone)
    if asked:
        # They do have pets, just not that one: saying "you haven't told me about a pet yet"
        # about a store that holds a dog is a claim the chat can see is false.
        theirs = [_a(p.get("animal", "pet")) + (" called " + _called(p.get("name"))
                  if p.get("name") else "") for p in (known.get("pets") or [])]
        if theirs:
            return ("I don't have " + _a(asked) + " from you \u2014 " + " and ".join(theirs)
                    + " is what I have.")
    return "You haven't told me about a pet yet."


def asks_again(text, memory=None):
    """True when the whole line asks to hear the bot's last reply again.

    The store's own reading of the ask, published so the arbiter asks for it instead of keeping a
    second copy of the frame in its own file: the copy missed "pardon" and "come again", and a
    repeat that is not recognised as one is passed over as a line saying the same thing twice.
    """
    low = str(text or "").strip().lower()
    return bool(low) and _repeat_ask(low, low, memory)


def _repeat_reply(memory, text=""):
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    said = [turn for turn in turns if str(turn.get("bot") or "").strip()]
    whole = bool(WHOLE_ASK.match(str(text or "").strip().lower()))
    # A line that takes something back answered nothing, so its acknowledgement is not what the
    # person wants said again: "how long do i roast a chicken" / "forget the chicken" / "say that
    # again" handed back "Sure - Got it - forget the chicken." The answer to repeat is the last one
    # that answered something; where the take-back is all the chat has, its reply still stands.
    if said and named_thing.takes_back(said[-1].get("user")):
        answered = [turn for turn in said[:-1]
                    if not named_thing.takes_back(turn.get("user"))]
        said = answered or said
    if not said:
        return _vary(["I haven't said anything yet — you go first.",
                      "Nothing from me so far. What would you like to talk about?"], memory)
    line = str((memory.get("understood") or {}).get("text") or "")
    about = _hearing_again(said, line)
    if whole and (about is None or about.get("module") not in ANSWER_MODULES):
        # A request for the whole of it with no answer behind it: a hello, a nod, or something
        # the bot said that is not an answer. "im fine thanks" / "in full" came back framed "Same
        # answer, and it covers this: Fair enough", which promises an answer that does not exist.
        # The store has nothing to hand over, so it says nothing at all and the ordinary reply to
        # the line stands, exactly as it does on main ("Alright then - good luck with it.").
        return None
    if about is None:
        # Nothing behind the ask: no answer and nothing that carried content, only a hello or a
        # nod. "Sure - Fair enough." is the bot promising the answer again and handing back a nod.
        return _vary(["Nothing from me on that yet. What were you asking about?",
                      "I haven't given you an answer on that yet. What is it you want to know?",
                      "Nothing of mine to give back there yet - what was the question?"], memory)
    if (FIGURE_REPEAT.search(str(text or "")) and not re.search(r"\d", str(about.get("bot") or ""))
            and about.get("module") not in ANSWER_MODULES):
        # "im in a good mood" / "how long did you say": the ask names a length and the line it
        # would hand back has no length in it, so there is nothing to say again.
        return _vary(["I haven't said a length yet - what are you timing?",
                      "Nothing with a time in it from me so far. What are you looking at?"], memory)
    last = str(about.get("bot") or "")
    # Said back as it was, with only a short lead-in: a reply that already has quotes in it
    # ("Your first line was: ...") must not end up quoted twice, and asking twice must not
    # stack the lead-in ("Again — Again — ...").
    # A frame this codebase puts on a hand-back is taken off first, so asking twice does not stack
    # two of them with this module's short one in front: the answer above was "Same as before: Say
    # it once, plainly.", and the reply then read "Sure - Same as before: Say it once, plainly."
    from ..memory import again as same_again  # read here, as the two callers above do
    base = same_again.unframed(last) or last
    base = re.sub(r"^(?:sure|again|of course)\s*[—-]\s*|^here it is again:\s*", "", base,
                  flags=re.I)
    if FIGURE_REPEAT.search(str(text or "")):
        # The ask names the figure, so the figure is the answer: "18 to 20 minutes." rather than
        # the paragraph it sits in. Anything else in the ask ("how long did you say to rest it")
        # narrows to nothing, and the answer stands as it was.
        figure = narrow.narrow(str(base), str(text or ""))
        if isinstance(figure, str) and figure.strip():
            base = figure.strip()
    if about.get("module") not in ANSWER_MODULES:
        # Not an answer to give again, so nothing is promised: "Sure - Nice to meet you, Sam" is
        # the bot promising an answer and handing back a greeting. The line is said as it was.
        return base
    if WHOLE_ASK.match(str(text or "").strip().lower()):
        # The person asked for the whole of it, so the lead-in says that is what this is. The
        # answer is handed over as it was written, not cut to the part that was left out: "in
        # full" is the one ask that wants the paragraph a second time, and it says so.
        return _vary(["All of it: " + base, "Here it is in full: " + base,
                      "The whole of it, then: " + base], memory)
    return _vary(["Sure — " + base, "Again — " + base, "Here it is again: " + base, base],
                 memory)


def _what_i_said_about(memory, thing):
    """The bot's own answer about the thing they name, in a sentence, or None.

    "what did you say about chewing" after "hes chewing all the furniture" reached nothing at all
    - two of its shapes got the shrug about not knowing enough, and "remind me what you said
    about chewing" was read as a job for a body that has no hands. The answer is in the chat, so
    it is the answer: the last turn that was about the thing, said in a sentence, with the
    question that earned it named so the person knows which one is coming back.
    """
    words = {word for word in keywords(thing or "") if word not in STOPWORDS}
    if not words:
        return None
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(turns):
        if str(turn.get("module") or "") in ("safety", "urgent", "grief", "loss"):
            return None  # an emergency answer is not read out again as a quotation
        said = str(turn.get("bot") or "").strip()
        asked = str(turn.get("user") or "")
        if not said:
            continue
        # The answer matches when it *opens* on the thing: "Chewing is normal while teeth
        # change" is what was said about chewing. A word that merely turns up in the middle of a
        # paragraph is not the thing that paragraph was about.
        opening = re.split(r"(?<=[.!?])\s+", said)[0]
        in_answer = words <= {word for word in keywords(opening)}
        in_question = words <= {word for word in keywords(asked)}
        if not _carries_something(turn) or not _adds_something(said, asked):
            continue  # a nod, or the line said back, is not an answer about the thing
        if not (in_answer or in_question):
            continue
        parts = re.split(r"(?<=[.!?])\s+", said)
        sentence = parts[0].strip()
        # An opening that says little on its own ("A puppy - good to know.") takes the sentence
        # after it along, so the quotation is not a nod with the thing's name in it.
        if len({word for word in keywords(sentence)} - NOD_WORDS) <= 2 and len(parts) > 1:
            sentence = sentence + " " + parts[1].strip()
        if not sentence or len(sentence.split()) > 45:
            sentence = " ".join(sentence.split()[:45]).rstrip(",;:") + "..."
        name = " ".join((thing or "").split())
        return pick(["On " + name + ": " + sentence,
                     "I said: " + sentence,
                     "What I said about " + name + ": " + sentence], memory)
    if len(words) <= 4:
        # Nothing in the chat was about it. Saying so, and naming it, is the answer - the shrug
        # about not knowing enough told them nothing and asked nothing back.
        name = " ".join((thing or "").split())
        return pick(["I don't think we've been over " + name + " yet - what do you want to know?",
                     "We haven't got to " + name + " yet. Ask me and I'll say what I know.",
                     name[:1].upper() + name[1:] + " hasn't come up yet - ask away."], memory)
    return None


def _asked_and_answered(memory):
    """The last line they said that was about something, and the bot's own reply to it.

    Not simply the last turn: a recall said twice in a row must come back with the same answer
    both times ("what should i cook tonight" / "what did i just tell you" / "what did i just tell
    you"), and reading the previous recall out as the question and as the answer makes each reply
    longer than the last until it is all that is left of the conversation.
    """
    for seen in reversed(recent(memory, 8)):
        line = str(seen.get("user") or "")
        if line and not _about_this_chat(line):
            return line, str(seen.get("bot") or "").strip()
    return "", ""


def _said_reply(memory):
    """The person's own last line, for "what did I just say?"."""
    last = last_user(memory)
    if not last:
        return "That was your first line — there's nothing before it."
    # A recall said after a recall is about the thing the chat is on, not about the question just
    # asked: "my wife is a nurse" / "what did i just say about herpes" / "what did i tell you"
    # hands back the fact, and reading the previous question out instead ("you said: what did i
    # just say about her") is the same shrug in a friendlier voice. The store already knows which
    # of the two it filed, so the fact wins whenever there is one.
    real = _last_real(memory)
    if real and _just_a_hello(real):
        # A greeting is not a thing they told us about themselves: "hi" / "what did i just tell
        # you" was answered "You said: \"hi\"", which says nothing and sounds like a machine.
        real = ""
    if real:
        last = real
    elif _asks(last):
        # A question they asked is not something they told us either, and quoting it back is the
        # bot saying their own line at them: "whats the capital of france" / "what did i just tell
        # you". What was told is the answer they got, so that is what comes back, and how depends
        # on whether it can be read again: a short answer is the answer, and the part that gave it
        # repeats it better than the store could ("Same answer, and it covers this: Paris."), so
        # the store passes. A long explanation cannot be read out a second time, and passing it
        # left the turn to the bot-describing-itself line, which is a non-sequitur: the store names
        # the question and gives the short of its own answer instead.
        asked, mine = _asked_and_answered(memory)
        if not asked:
            # A chat that has only asked about itself so far ("where do i live") has that
            # exchange to hand back, though `_asked_and_answered` skips it as chat-about: it was
            # answered "You haven't mentioned a place yet", and passing it left the turn to the
            # search hedge. A recall after a recall is not the exchange to hand back, so those
            # lines are left to the guard above.
            for seen in reversed(recent(memory, 2)):
                line = str(seen.get("user") or "")
                if line and not SAID_ASK.search(line.lower()) and not FIRST_ASK.search(line.lower()):
                    asked, mine = line, str(seen.get("bot") or "").strip()
                    break
        again = _about_this_chat(last)
        # A question is worth handing back when it is all the chat holds: small talk ("hi" /
        # "how are you") or an ask about themselves ("where do i live") that the store had no
        # answer for. Passing it left the turn to the search hedge ("I don't know enough to
        # answer that honestly"), which says less than the exchange they just had did.
        nothing_yet = not real and (bool(history.not_a_subject(asked))
                                    or bool(THEIR_OWN_ASK.search(asked or "")))
        if mine and (nothing_yet or (not _just_a_hello(asked)
                                     and (again or len(mine.split()) > A_SHORT_ANSWER))):
            asked = _trim(asked).rstrip(" .!?")
            first = re.split(r"(?<=[.!?])\s+", mine)[0].strip()
            return _vary(["You asked: \"" + asked + "\" — I said: " + first,
                          "That one was your question: \"" + asked + "\". My answer: " + first,
                          "You asked \"" + asked + "\", and what I said was: " + first],
                         memory)
        return None
    else:
        # Nothing they told us yet, so say that rather than quote a greeting back at them.
        return _summary_reply(memory)
    fixed = memory.get("correction") if isinstance(memory, dict) else None
    fixed_words = " ".join(str((fixed or {}).get("sentence") or (fixed or {}).get("value") or "")
                           .split())
    if isinstance(fixed, dict) and fixed_words \
            and fixed.get("said") == " ".join(str(last).lower().split()):
        # Their last line was a correction of the one before it ("no, june", "make that 8"), and
        # handed back on its own it says nothing: "You said: \"no, june\"" leaves them to work
        # out what was corrected. What they said is the line with the correction in it.
        said = fixed_words.rstrip(" .!?")
        return _vary(["You said " + said + " — you put me right on it.",
                      "You said " + said + ", and that is the version I am going with.",
                      "\"" + said + "\" — your first line, put right a moment later."], memory)
    return _vary(["You said: \"" + _trim(last) + "\"",
                  "Your last line was: \"" + _trim(last) + "\"",
                  "That was: \"" + _trim(last) + "\""], memory)


def _last_real(memory):
    """The last thing the user said that was about something, not about this chat.

    A question about the chat is not what the chat was about: "what did i say the party was
    for?" must not come back as "we were on this: \"what did i say the party was for?\"".
    """
    for seen in reversed(recent(memory, 8)):
        line = seen.get("user") or ""
        if line and not _about_this_chat(line) and not _asks(line):
            return line
    return ""


def _say_back(line, memory=None):
    """Their own line said again as a sentence about them, with no quotation marks round it.

    A recap of a thing the chat has moved on from reads better as a statement than as a quote:
    "what was i saying about pasta earlier" is answered "You said like you can do pasta but
    thats it", which is the same sentence a friend would say.
    """
    said = (thread.restate(line) or _recap(line) or "").strip().rstrip(".")
    if not said:
        return _recall_quote(line, memory)
    said = said[:1].lower() + said[1:]
    return _vary(["You said " + said + ". Want to carry on?",
                  "You said " + said + "."], memory)


def _recall_reply(memory, low, text="", spoken=False):
    """The line they are asking about: "what did i say about the cake?", "and about it?".

    The thing asked about is matched by stem over the last user lines, so "the cakes" finds
    "i want to bake a cake for my daughter", and "what did i say the party was for?" finds the
    line that mentions the party. A line that only asks about the chat is skipped: otherwise
    "what did i tell you about it?" answers with an earlier question.

    Returns None when the line does not name a thing, so the caller can answer with the topic
    instead of denying something the user did say.
    """
    # "what did i say was hurting" asks about a complaint the store holds, and it holds the one
    # that stands now: quoting the first line back contradicts the store's own record after a
    # correction ("my knees..." then "my back hurts not my knees" quoted the knees).
    hurt = a_hurting_part.what_is_hurting_reply(memory, low)
    if hurt:
        return hurt
    about = re.search(r"\babout\b(.*)$", low)
    part = None if about else _which_thing_was_it(low, memory)
    if about:
        thing = about.group(1)
    elif part:
        # "and which knee was it" names the thing the detail is about, so the line to find is
        # the one that says which knee it was: the thing is the word to look for.
        thing = part
    else:
        after = re.search(r"\b(?:say|said|tell you|told you|mention)\b(.*)$", low)
        thing = after.group(1) if after else ""
    # The named-back form is said in their words, not in the normalised line: "my mum's
    # birthday" keeps its possessive when it becomes "your mum's birthday".
    mine = re.search(r"\babout\b(.*)$", text or "", re.I)
    shown = (mine.group(1) if mine else thing).strip(" ?!.,")
    thing = re.sub(r"\b(?:again|before|earlier|please|so far|up to now|until now)\b",
                   "", thing).strip(" ?!.,")
    if thing.lower() in REFLEXIVE:
        # "what did i tell you about myself" is the whole picture, not a thing they said: there
        # is no line about "myself" to find, and the denial ("You haven't said anything to me
        # about myself yet") told a person who had just given their name that they had said
        # nothing. Left to the reader for "what do you know about me".
        return None
    if not content(thing):
        # "what's the noise again?" names the thing instead of saying "about it": the word it
        # names is what to look for in their lines.
        named = THING_AGAIN.match(low)
        if named:
            thing = named.group(1)
        else:
            # The same thing named in a reminder: "what was wrong with my boiler again",
            # "remind me what the problem with the car was". The reading is the one the gate
            # uses, so a line it takes is answered here rather than by the chat's topic.
            reminded_thing = reminded.the_thing(text or low, memory)
            if reminded_thing:
                thing = reminded_thing
    # "what did i say to her?" is what they said to someone else, not to the bot: the old "what
    # did i say" branch guarded this, and so must this one.
    if re.match(r"to\s+(?!me\b|you\b)", thing):
        return None
    # "for a living" is the job said as a phrase, not a thing a line is about: "what did i say
    # i do for a living" was read by its words ("do", "living") and found "i live in leeds", so
    # the town came back as the job. The words name the kind of fact, and the fact reader
    # further down answers it in the store's own sentence ("You work as a nurse."), so this ask
    # is left to it rather than quoted from whichever line shares a word.
    if recall.LIVING.search(thing):
        return None
    words = content(thing)
    if not words or thing in ("it", "that", "this", "them", "that one"):
        real = _last_real(memory)
        if real:
            return _recall_quote(real, memory)
        record = current(memory)
        if record and record.get("text") and not _about_this_chat(record["text"]):
            return _recall_quote(record["text"], memory, asked=_asks(record["text"]))
        return pick(["You haven't told me anything about that yet.",
                     "Nothing comes to mind \u2014 you haven't said."], memory)
    # A line about the telling is not the thing told: "i told you about the damp" carries the
    # word and says nothing about the damp, so quoted back it answered "what did i say about the
    # damp" with the complaint that they had said it. It is kept apart rather than dropped: in a
    # chat where the telling is the only line about the thing, it is still what they said, and
    # with a line that states the thing it would be said beside it ("your dog or your dog died").
    hits, asked, fixed, claims = [], [], [], []
    for turn in _every_line(memory):
        line = turn.get("user") or ""
        if not line or _about_this_chat(line):
            continue
        seen = _seen(line)
        question = _asks(line)
        # A word of the ask finds the line by the kind it names as well as by the word: "what did
        # i say about my trip" is about "im going to lisbon in may", which never says "trip".
        # The kind is the shape of a plan they stated, so a line that only asks is not one: "when
        # is my trip" names the trip and states nothing, and read as the kind it comes back as
        # what they said about the holiday, when all they did was ask. The words still find it,
        # and the ask bucket quotes it as the question it is.
        if all(_alike(word, seen) or (not question and _about_kind(word, line, memory))
               for word in words):
            # "sorry, Naples not Rome" names Rome in order to replace it, so the line it
            # corrects is the one being asked about: quote that, not the correction.
            (asked if _asks(line) else fixed if _corrects(line) else
             claims if A_CLAIM_OF_TELLING.match(" ".join(line.lower().split())) else
             hits).append(line)
    if not hits and claims:
        hits = claims
    if hits:
        # A line that asks about the thing does not tell us the thing: "sorry, back to the
        # roast, what time should i start it" is the last line that mentions the roast, and
        # quoted back it looks like an answer and says nothing. Where an earlier line states it,
        # that is the line they are asking about. A chat whose only line about it is the question
        # keeps the question, because it is still true that they said it.
        stated = [line for line in hits if not ASKS_IN_LINE.search(line)]
        if stated:
            hits = stated
        # "what was i saying about pasta" is the chat going back over something it has moved on
        # from, so the line is said as a sentence; the quoting form belongs to "what did i say",
        # where the words themselves were asked for.
        if not spoken:
            put_right = _put_right_after_it(hits[-1], memory)
            if put_right:
                return put_right
            moved = _a_figure_put_right(hits[-1], memory)
            if moved:
                return moved
            narrowed = _a_narrowing_put_after(hits[-1], memory)
            if narrowed:
                return narrowed
        return _say_back(hits[-1], memory) if spoken else _recall_quote(hits[-1], memory)
    # The only line about it was a question, which they still said: "You asked: \"...\"" is
    # true where "You said" would put words in their mouth, and where a denial would be a lie.
    if asked:
        return _recall_quote(asked[-1], memory, asked=True)
    if fixed:
        return _recall_quote(fixed[-1], memory)
    # A recall ask carries its own judgement: "what did i say was wrong with my flat" asks about
    # the flat, and "wrong" is the ask's word rather than the person's. The full set of words is
    # tried first, so a line that does use the judging word still matches it; only when nothing is
    # found are those words dropped, and the rest of what was named is enough to find the line.
    naming = [word for word in words if word not in JUDGING and word not in A_ROLE]
    if naming and naming != words:
        naming_hits, naming_asked = [], []
        for turn in recent(memory, 8):
            line = turn.get("user") or ""
            if not line or _about_this_chat(line):
                continue
            seen = _seen(line)
            if all(_alike(word, seen) for word in naming):
                (naming_asked if _asks(line) else naming_hits).append(line)
        if naming_hits:
            return _recall_quote(naming_hits[-1], memory)
        if naming_asked:
            return _recall_quote(naming_asked[-1], memory, asked=True)
    # "what did i say was wrong with it": the only word left is the ask's own judgement and the
    # thing is a pronoun, so there is nothing to find and the line it asks about is the one they
    # last told me about - the subject of the chat.
    if not naming and PRONOUN_ASK.search(thing):
        real = _last_real(memory)
        # A greeting is not a thing that could be wrong: one content word is small talk, and the
        # ask gets the honest "you haven't said" instead of "you said: hello".
        if real and len(content(real)) > 1:
            return _recall_quote(real, memory)
    if not about:
        return None
    # The thing is named back in the second person: a friend says "your mum", not "my mum".
    said = re.sub(r"^my\b", "your", shown).strip()
    return pick(["You haven't said anything to me about " + said + " yet.",
                 "You haven't mentioned " + said + " \u2014 say it and I'll keep it."], memory)


def _a_figure_put_right(line, memory):
    """The quote and the figure the person put right after it, or "".

    A recall quotes the line the thing was said in, and the next line can put a figure in it
    right without naming the thing: "my rent is 1200 a month" / "sorry 1150, i got it wrong".
    Nothing in the store moves when that happens - a rent is not a fact the store keeps - so the
    quote came back as 1200 after the bot had already answered "Got it - 1150, you got it
    wrong": the chat contradicting itself one line after agreeing.

    The quoted line must hold one figure - with two in it there is no saying which one moved -
    and the correction must be the bare figure (see `A_BARE_PUT_RIGHT`), so a line about another
    thing that happens to hold a number is left alone. It must also be the line *right after* the
    quote: "my rent is 1200 a month" / "i weigh 14 stone" / "sorry 13 stone" is a weight put
    right, not the rent.
    """
    if not isinstance(memory, dict):
        return ""
    said = " ".join(str(line or "").split())
    figures = A_FIGURE.findall(said)
    if len(figures) != 1:
        return ""
    lines = [" ".join(str(turn.get("user") or "").split()) for turn in _every_line(memory)]
    places = [index for index, text in enumerate(lines) if text == said]
    if not places:
        return ""
    # Only the line right after the quote: a bare "sorry 13 stone" three lines later is about
    # whatever that line was about (a weight), not about the rent quoted, and saying the person
    # put the rent right would be putting words in their mouth.
    for after in lines[places[-1] + 1:places[-1] + 2]:
        found = A_BARE_PUT_RIGHT.match(after.strip())
        if not found:
            continue
        value = found.group("value").strip().rstrip(",")
        if not value or value == figures[0]:
            continue
        return (_recall_quote(line, memory).rstrip()
                + " \u2014 then you put it right: " + value + ".")
    return ""


def _a_narrowing_put_after(line, memory):
    """The quoted line and the narrowing the person put after it, or "".

    A recall can land on a line that narrows the one above it and says nothing on its own ("the
    ones that are open on sunday", "the cheaper ones"), and quoted alone it is their fragment with
    no thing in it. The reading of which lines those are is `repeat.a_narrowing_and_its_line`, so
    the two recall paths cannot drift apart.
    """
    if not isinstance(memory, dict):
        return ""
    pair = _a_narrowing_and_its_line(line, memory)
    if not pair:
        return ""
    before, after = pair
    return (_recall_quote(before, memory).rstrip()
            + " \u2014 then \"" + _trim(after, 80) + "\".")


def _put_right_after_it(line, memory):
    """The quoted line and the correction that followed it, or "" when there is none.

    A recall about a named thing quotes the line the thing was said in, and the person's next
    line can put that line right without naming the thing again: "the dinner is on friday" /
    "sorry, saturday". Quoting only the first line leaves the store contradicting the line it
    agreed to a turn earlier - "what did i say about my sons birthday" came back as May after
    "Got it - your son's birthday is in June". The correction the store filed is the end of the
    story, so the quote says both when the store has one for that line.
    """
    fixed = memory.get("correction") if isinstance(memory, dict) else None
    if not isinstance(fixed, dict):
        return ""
    said_back = " ".join(str(fixed.get("said") or "").lower().split())
    sentence = " ".join(str(fixed.get("sentence") or "").split()).rstrip(" .!?")
    if not (said_back and sentence):
        return ""
    lines = [" ".join(str(turn.get("user") or "").lower().split())
             for turn in _every_line(memory)]
    quoted = " ".join(str(line or "").lower().split())
    if said_back not in lines or quoted not in lines:
        return ""
    if lines.index(quoted) >= lines.index(said_back):
        return ""      # the line quoted is the correction itself, or came after it
    if not (_content_words(line) & _content_words(sentence)):
        return ""      # the correction is about something else in the chat
    tail = sentence[0].lower() + sentence[1:]
    return _recall_quote(line, memory).rstrip() + " \u2014 then you put it right: " + tail + "."


def _the_line_named(memory, low):
    """The earlier line of theirs that the thing asked about is in, or "" when none is.

    "what was i saying about the deposit" after "im saving for a deposit" and "my rent is 800"
    asks about the deposit, and saying the rent back answers a question nobody asked. A pronoun
    names no thing ("what was i saying about it"), so it names nothing to look for and the last
    line stays the answer.
    """
    about = re.search(r"\babout\s+(.*)$", low or "")
    if not about:
        return ""
    words = content(about.group(1))
    if not words:
        return ""
    for seen in reversed(recent(memory, 8)):
        line = seen.get("user") or ""
        if not line or _about_this_chat(line):
            continue
        have = set(content(line))
        if have and all(_alike(word, have) for word in words):
            return line
    return ""


def _asked_reply(memory):
    """'What did I just ask you?' — their last question, said again in their words."""
    ask = thread.last_ask(memory, _about_this_chat)
    if ask:
        return "You asked " + ask + "."
    said = thread.last_said(memory, _about_this_chat)
    if said:
        return "You didn't ask me anything — you said " + said + "."
    # A chat whose only line so far is a question about the bot ("are you a real person") has no
    # subject of theirs for either reader above, so both pass - but they did ask something, and
    # "you haven't asked me anything yet" denies the question that is still on the screen. The
    # question about the bot is said back in their own words, which is what the chat has covered.
    asked_of_me = _the_last_ask_about_the_bot(memory)
    if asked_of_me:
        return "You asked " + asked_of_me + "."
    return "You haven't asked me anything yet."


FOOD_CONDITION = frozenset(("coeliac", "celiac", "diabetic", "diabetes", "ibs",
                            "irritable bowel", "crohns", "crohn's", "lactose intolerant",
                            "fructose intolerant", "allergic"))


def _food_facts(memory):
    """The food restrictions the store holds, in the words they can be said back in."""
    mine = user(memory)
    kept = []
    allergies = mine.get("allergies")
    if isinstance(allergies, str):
        allergies = [allergies]
    if isinstance(allergies, (list, tuple)):
        for item in allergies:
            item = str(item).strip()
            if item:
                kept.append("allergic to " + item)
    condition = mine.get("condition")
    if isinstance(condition, str):
        condition = [condition]
    if isinstance(condition, (list, tuple)):
        for item in condition:
            item = str(item).strip()
            if item and item.lower() in FOOD_CONDITION:
                kept.append(item)
    return kept


def _the_food_a_condition_rules_out(condition):
    """The one food word a condition rules out ("coeliac" -> "gluten"), or "".

    The knowledge of which food a condition bans is the kitchen's, and it is already written
    there as a family (``cooking.CONDITION_BANS``); this only names that family so the store can
    say the short word people use instead of the twenty things made of it.
    """
    wanted = cooking.CONDITION_BANS.get(str(condition or "").lower().strip())
    if not wanted:
        return ""
    for name, family in cooking.FAMILIES.items():
        if set(family) == set(wanted):
            return name
    return ""


def _what_a_dinner_has_to_leave_out(memory):
    """The foods a dinner has to leave out, and the fact that rules each one out.

    The store holds two shapes of the same thing: an allergy ("you're allergic to nuts") and a
    condition ("you're coeliac"), and a meal ask after either of them must not be answered with
    "You haven't told me about your diet". Returns the words for "nothing with X in it" and the
    clauses that say why, so the sentence fits one fact or both.
    """
    mine = user(memory)
    left_out, said_so = [], []
    allergies = mine.get("allergies")
    if isinstance(allergies, str):
        allergies = [allergies]
    if isinstance(allergies, (list, tuple)):
        kept = [str(name).strip() for name in allergies if str(name).strip()]
        if kept:
            left_out.extend(kept)
            said_so.append("you're allergic to " + _all_of_them(len(kept)))
    condition = mine.get("condition")
    if isinstance(condition, str):
        condition = [condition]
    if isinstance(condition, (list, tuple)):
        for item in condition:
            named = str(item).strip()
            if not named or named.lower() not in FOOD_CONDITION:
                continue
            food = _the_food_a_condition_rules_out(named)
            said_so.append("you're " + named)
            if food and food not in left_out:
                left_out.append(food)
    return left_out, said_so


def _all_of_them(count):
    """How a person says the whole list back: one thing, two things, or three and more.

    The clause that says why a dinner leaves something out is the store's own facts read aloud, so
    it has to count what the store holds: "im allergic to nuts, shellfish and eggs" came back as
    "you're allergic to both", which is wrong for a list of three and reads as the bot having
    stopped listening at the second one.
    """
    if count == 1:
        return "them"
    if count == 2:
        return "both"
    return "all of them"


def _say_a_list(items):
    """One thing named, or several as people say them: "a, b and c"."""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return items[0] + " and " + items[1]
    return ", ".join(items[:-1]) + " and " + items[-1]
