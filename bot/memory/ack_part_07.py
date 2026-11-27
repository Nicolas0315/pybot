"""Part 7 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from ..compose import pick, trouble
from ..compose.badnews import reads_as_bad_news, reads_for_a_pet, reads_like_a_symptom
from ..compose.goodnews import reads_as_good_news, reads_as_settled, worry_on_the_table
from ..understanding import understand as understanding
from ..understanding.normalize import without_a_leading_exclamation
from . import there_is_a_chat
from . import opening
from . import you as say_it_back
from . import facts
from .facts import DAYS, MONTHS, a_limit_on_the_plan
from .ack_part_01 import (
    EXPLAIN_TAIL, FRAMES, PET_TAIL_MANY, PET_TAIL_ONE, _a_limit_on_the_plan, a_person_named_alone,
    a_second_person, reads_as_a_receipt, GOING_TAIL, HABIT_TAIL, HAVE_THING, NOT_A_THING,
    SOMEONE_GOOD, SOMEONE_MILESTONE_TAIL, SOMEONE_TAIL, VISIT_TAIL, WORK_FRAMES, _a_day_coming,
)
from .ack_part_02 import (
    A_LIKE_ECHO, A_LIKE_WITH_TWO_HALVES, A_PERSON_LIKED, _AN_ABILITY, _LIMIT_ONLY,
    _OPENS_WITH_AN_ASK, _a_plan_on_the_table, LIMIT_AFTER_THE_LINE, LIMIT_FRAMES, SAID_BACK_WORDS,
    _the_plan_in_hand, CONDITION_FOOD, DEATH_WORDS, GREETING, WANTS_ANSWER, FEELING, GOING,
    GOING_BAD, HABIT, OBLIGED, BUDGET_FRAMES, CONDITION_FRAMES, DRINK_FRAMES, FOOD_FRAMES,
    HEAVY_FRAMES, LIKES_FRAMES, OTHER_LIMIT_FRAMES, SPENDING_FRAMES, STILL_FRAMES, _only_a_liking,
    a_liked_thing,
)
from .ack_part_03 import (
    CORRECTED_ALONE, CORRECTED_WITH_UNIT, WHOLE_FREQUENCY, _the_bare_value, _the_line_before,
    _the_unit_is_said_twice, _without_a_unit_already_in_the_value, A_FEELING, BLEED, BODY,
    GOOD_MOOD, MEET_GREET, SELF_INTRO, WOULD_HAVE_BEEN, _a_bare_state, _a_date_on_the_thing_in_hand,
    _a_hand_back, _after_the_hello, _offers_a_chat, _repaired, has_news, pet_given_away, TROUBLE,
    CLAUSES, MOST, POLITE, STOP,
)
from .ack_part_04 import (
    _pick_ending, ANIMAL_COMING, ANIMAL_HAD_ONCE, ANIMAL_TAKEN_BACK, AS_WELL, A_BREED_BEING_CHOSEN,
    A_CHILD_IN_THE_LINE, PET_TAIL_COMING, PET_TAIL_COMING_MANY, THE_STORY_GOES_ON,
    WISH_FOR_AN_ANIMAL, _a_clock_time, _a_deadline, _a_pet_that_is_all_right,
    _a_result_is_on_the_table, _after_a_feeling, _an_animal_only_planned, _an_animal_taken_back,
    _an_animal_they_had_once, _an_animal_turned_down, _an_animal_wanted, _nothing_added_but_the_pet,
    _on_record, _only_a_wish, _the_animal_coming, _the_hours, _the_length, _the_pets_are_coming,
    _the_pets_said, _the_taken_back_animal, _the_wished_animal, the_old_one_aged, A_PET_WANTED,
    A_WANTED_ANIMAL_TAIL, _about_them,
)
from .ack_part_05 import (
    _a_loss, _a_remark_on_what_was_said, _adds_one_more_allergen, _children_said,
    _children_with_ages, _heavy, _no_subject, _plan_tails, _said_to_the_bot, _statement,
    _who_the_figure_is, nobody_around, the_job_they_had, JOB_HAS_A_DAY, JOB_TAIL, JOB_TO_DO,
    PLACED_IN_THE_PAST, _about_a_body, _repairs, _what_the_pointer_is, _a_spending_budget, _a_visit,
    _a_workplace, _about_someone_else, _about_the_family, _just_a_liking, _the_milestone,
    MONEY_ONLY, _OPENS_WITH_A_LINK, _names_nothing,
)
from .ack_part_06 import (
    _learned, MAKE_A_VALUE, VALUE_WORDS, _the_unit_before, _another_of_what_we_said,
    _bad_news_just_before, _only_the_figure, _tells_it, _strip_lead_in, HAVE_A, _spoken,
    A_COUNT_NOT_A_STATE, HAVE_GOT, KIN_POSSESSIVE, UNITS_OF_MEASURE, WHOS,
    _only_the_correction_in_front, _pick_off, _reason_off, _says_something, _tail_off, CONTRAST,
    CONTRAST_SAID_AGAIN, NOT_A_VALUE, BETWEEN_VALUES, VALUE,
)


def _a_like_of_one_thing(clean, memory=None):
    """Whether the line's whole echo is one thing the person likes."""
    echo = _echo(clean, memory)
    match = A_LIKE_ECHO.match(echo or "")
    if not match:
        return False
    thing = match.group("thing")
    if A_LIKE_WITH_TWO_HALVES.search(thing) or A_PERSON_LIKED.search(thing):
        return False
    return not any(re.search(r"\b" + re.escape(word) + r"\b", thing, re.I)
                   for word in (facts.RELATIONS or ()))


def a_limit_reply(text, memory=None):
    """The limit said back with what the bot will do with it, or None when the line is more.

    Read before the pools a limit has already been misread by, so it has to say nothing at all
    unless the line really is only a limit: "im going to keep it cheap this month" is a month
    they have planned, not a limit to promise anything about.
    """
    if not isinstance(text, str):
        return None
    clean = " ".join(text.split())
    if not clean or "?" in clean:
        return None
    if _OPENS_WITH_AN_ASK.match(clean):
        return None
    family = a_limit_on_the_plan(clean)
    if family is None:
        return None
    if not _AN_ABILITY.search(clean) and not _a_plan_on_the_table(memory, clean):
        # Nothing is being planned, so there is no plan to keep anything out of. The line is a
        # remark, and the pools that answer remarks say something better: "im on a budget" is how
        # people ask what to cook for little money.
        return None
    found = _learned(text, memory)
    if found and not set(found) <= _LIMIT_ONLY:
        return None
    return _a_limit_reply(clean, family, memory)


def _a_limit_reply(clean, family, memory):
    """The limit said back, with what the bot will do with it."""
    body = _echo(clean) or clean
    if family == "move" and _the_plan_in_hand(memory, clean) == "stay":
        family = "move_stay"
    if len(body.split()) > SAID_BACK_WORDS:
        # A whole sentence is not a label for the limit: saying it back puts their words in front
        # of the answer, so the reply starts with what it will do with the limit instead.
        after = LIMIT_AFTER_THE_LINE.get(family)
        if after:
            return _pick_ending(after, memory)
    frames = LIMIT_FRAMES.get(family) or LIMIT_FRAMES["other"]
    return _pick_ending(frames, memory, thing=body, Thing=body[:1].upper() + body[1:])


def a_limit_for_the_plan(text, memory=None):
    """A limit on the plan in hand, or None when no plan is in hand or no frame fits it.

    Read by the chat module before it hands back the answer it already gave: a limit said about
    the plan ("shes 78 and cant do stairs" after "my mum is coming to stay") is the one thing that
    should change the answer, and the card went round three times instead. It only speaks when a
    plan of a kind the frames are written for is on the table, so a limit in a chat about a diet
    or a dripping tap keeps the reply it has.
    """
    if not isinstance(text, str):
        return None
    clean = " ".join(text.split())
    if not clean or "?" in clean or _OPENS_WITH_AN_ASK.match(clean):
        return None
    family = a_limit_on_the_plan(clean)
    if family is None:
        return None
    # A reply about the plan needs a plan from an earlier turn. On a first message there is
    # nothing to read the limit against, and the line is answered as the line it is.
    if not there_is_a_chat(memory):
        return None
    # Only a guest who is staying: a limit on a trip already has better answers below this module
    # ("my mum cant do stairs any more" after a few days away came back from the chat module with
    # "ring ahead for the ones you care about - a lift to the good floors and a loo you can get to
    # are the two questions worth asking", and a frame about a bed in the house would be worse).
    if _the_plan_in_hand(memory) != "stay":
        return None
    return _a_limit_reply(clean, family, memory)


def value_put_right(clean, memory):
    """The correction said back, or "" when the line is not one that only puts a value right.

    Two things have to hold. The line has to be the frame and a value and nothing else ("make it
    four", "change that to 10k"): "my boiler is broken" then "make it stop", and "a new sofa"
    then "make it bigger", are the rest of a sentence and stay with the modules that read it.
    And the line before has to measure something ("three *times a week*", "5k *every morning*"),
    because a figure said back with no unit is the bot claiming a value it does not hold — which
    is the one thing the store's correction refuses (see FalseFactTest in tests/test_memory.py).
    """
    match = MAKE_A_VALUE.match(clean or "")
    bare = ""
    if not match:
        bare = _the_bare_value(clean or "")
        if not bare:
            return ""
    if not _the_line_before(memory):
        return ""  # nothing said before it, so there is no value to put right
    value = " ".join((match.group("value") if match else bare).split()).strip(" .")
    if not value or len(value.split()) > 4:
        return ""
    words = [word.lower().strip(".,!?'\u2019") for word in value.split()]
    if bare:
        # A correction with no verb has to be a figure or a frequency said plainly: a bare word
        # like a month or a weekday is the rest of a sentence ("my trip is 3 days in june" then
        # "sorry, june" is not "June days in june, got it.").
        if not (re.search(r"\d", value)
                or all(word in VALUE_WORDS or word in WHOLE_FREQUENCY for word in words)):
            return ""
    elif not (re.search(r"\d", value) or all(word in VALUE_WORDS or word in DAYS
                                              or word in MONTHS or word in WHOLE_FREQUENCY
                                              for word in words)):
        return ""
    unit = _the_unit_before(memory)
    if not unit:
        # Nothing in the line before is measured in anything, so the new figure replaces no value
        # the bot can name: "im tired" then "make that 800" is not a correction of anything, and a
        # figure said back would be the bot claiming it holds a number it does not.
        return ""
    unit = _without_a_unit_already_in_the_value(value, unit)
    if _the_unit_is_said_twice(value, unit):
        # The unit of the line before would be a second measure of the same thing, so the value
        # is said back as it was given: "10 km, then."
        return pick(CORRECTED_ALONE, memory, seed_text=clean).format(
            value=value, Value=value[:1].upper() + value[1:])
    return pick(CORRECTED_WITH_UNIT, memory, seed_text=clean).format(
        value=value, Value=value[:1].upper() + value[1:], unit=unit)


def reply(text, memory):
    """A short echo of the fact they just gave, or None when this is not that kind of line."""
    if not isinstance(text, str):
        return None
    clean = " ".join(text.split())
    if not clean or "?" in clean:
        return None
    dated = _a_date_on_the_thing_in_hand(clean, memory)
    if dated:
        # "its in july" after "im going to a wedding". It comes first because nothing below asks
        # what the line is the date *of*, and the neutral line at the end of the chain fits any
        # message at all.
        return dated
    # A clock time somebody has to be somewhere by is not a fact to file: "i have a train at 7"
    # was answered "Noted: you have a train at 7.", which is the coldest version of the one thing
    # in the line worth working back from, and the composer has the pool that does that
    # (tiny-bluebell, #routing 81689). The store still keeps the line; only the saying back
    # stands aside.
    from ..compose import fallback as compose_fallback
    if compose_fallback._the_morning_has_a_clock(clean.lower()):
        return None
    # A line that takes the last thing back is not a fact to file: "forget about the whole thing"
    # was answered "Forget about the whole thing — noted.", which is the coldest line in
    # STYLE.md spent on a withdrawal - the person has just said they are done with it, and the
    # echo hands it back to them as news. The pool that answers a dismissal is the composer's
    # (bot/compose/fallback_data.py, NEVER_MIND), so the saying back stands aside and the line
    # reaches it.
    from ..compose.fallback_data import A_DISMISSAL
    if A_DISMISSAL.match(clean):
        return None
    # "i told you my interview is in june" is the fact said again with a frame around it, and the
    # store files the fact without the frame, so the note drops it too: "Noted: your interview is
    # in june.", never "Noted: you told me your interview is in june." A report of something that
    # is not a fact ("i said thanks", "i told you about the boiler") keeps its own words.
    reported = facts._reported_clause(clean)
    if reported and facts.extract(reported):
        clean = " ".join(reported.split())
        text = clean
    # Advice somebody else gave them is not a fact to file: "my mum says i should go to the
    # doctor" was said back as "Noted: your mum says you should go to the doctor", which is the
    # coldest line in STYLE.md for what is a nudge from home. Nothing in the line has happened
    # yet, so there is no fact in it to keep - the plan is the line, and bot/compose/fallback.py
    # answers it (see A_SUGGESTED there). Read off the understanding engine, not off the words,
    # so a report of something done keeps its note ("my mum says i got the job").
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict) and understood.get("suggestion"):
        return None
    # An errand asked of the bot is not a fact of theirs to say back. "we are going to lanzarote in
    # may" then "look up the flights for me" was answered "Got it — look up the flights for you.",
    # which is a receipt for something the bot has just said it cannot do - the one reply worse
    # than the honest limit. The line is read by bot/understanding/__init__.py as an errand, so the
    # store's own saying back stands aside and the composer's limit keeps the turn.
    if isinstance(understood, dict) and understood.get("errand"):
        return None
    read = _repaired(clean, memory)
    # The name in "my name is Priya" is a capital, and a capital is part of the reading, so these
    # three look at the line as typed.
    # A hello in front of a fact is the hello and the fact, and standing down on the greeting
    # lost the fact: "hi, im vegetarian" kept the diet and then answered "Hey! What would you
    # like to talk about?". The hello is taken off when the line goes on after it, so what is
    # said back is the rest of it. A line that is only a hello has nothing to say back, and
    # neither has one that goes on to give their name ("hi, i'm Sam" is the chat module's) or
    # to say what they are after ("hi, im looking for a plumber" is asking for a plumber).
    # `facts.about_themselves` is that reading, and the kind reader asks the same question of
    # the same line (`bot/understanding/kinds.py`, `greeting_only`).
    if GREETING.search(clean):
        rest = _after_the_hello(clean)
        if not rest or not facts.about_themselves(rest):
            return None
        clean = text = rest
        read = _repaired(clean, memory)
    elif MEET_GREET.search(clean) or SELF_INTRO.search(clean):
        return None
    had = the_job_they_had(clean, memory)
    if had:
        # "i was a teaching assistant before the kids": the job they had, not a day to give a
        # verdict on (see PAST_JOB). Asked here, before the day and echo paths, so the line
        # cannot be read as an event that has happened.
        return had
    # A line that names a person of theirs and nothing else is a person to ask about however it is
    # worded: "what about the little one" is the same line as "and the little one", and it was read
    # as an ask about a thing and handed a search hedge. The named-alone pattern is anchored to the
    # whole line, so a real question about a person ("what about my sons school") never gets here.
    alone = a_person_named_alone(clean, memory)
    if alone:
        return alone
    if WANTS_ANSWER.search(read) and not facts.RELATION_WHOS_AGE.search(read):
        # "idk what to get my dad" is asking, not telling. The "who" clause is the one "whos"
        # that is not an ask: "my daughter whos 9" says the same thing as "my daughter is 9",
        # and it was left with the neutral "I'm listening" while the plain wording was said
        # back. The pattern is the relation's own, so "whos coming to dinner" is still a
        # question.
        return None
    if _a_result_is_on_the_table(clean):
        # "i got the results" is a person with news, and "im not sure i got the place" is a
        # person waiting: the reply that fits asks for the rest, and bot/compose/fallback.py
        # has both ("What did they say?", "When do you find out?"). Saying the line back -
        # "Noted: you got the results." - tells them nothing they did not just say.
        return None
    limit = _a_limit_on_the_plan(read, memory)
    if limit:
        return limit
    second = a_second_person(clean, memory)
    if second:
        # "and my dads" after a birthday is the same fact for somebody new, and the date is what
        # they left out: asking for it beats "Got it - your dads."
        return second
    corrected = value_put_right(clean, memory)
    if corrected:
        # "make it four" after the gym line: the value goes back up with the unit of the line it
        # corrects, and never as a search hedge (see MAKE_A_VALUE).
        return corrected
    aged = the_old_one_aged(clean, memory)
    if aged:
        # "i need a new washing machine" / "the old one is 12 years old": the number is the only
        # new fact in the line, and a friend says what it means for the purchase (see
        # THE_OLD_ONE). The reading is only for the thing in hand - a thing named on its own ("my
        # boiler is 8 years old") has an entry of its own and keeps it.
        return aged
    if not _statement(memory):
        return None
    given = pet_given_away(clean, memory)
    if given:
        # "we had to give our dog away" is not a fact to file: it is a person telling you the
        # hardest call they have had to make about an animal (see GIVEN_AWAY).
        return given
    if trouble.reads_as_trouble(read) is not None:
        # A fault to troubleshoot is bot/compose/trouble.py's turn: a thing that is not behaving
        # gets "what's it doing", and a setback nobody has explained yet gets "what happened".
        # Either way the line is not a fact to say back. `_plain` has had this guard for the lines
        # that reach its tail; this is the same guard for the fact paths, where a complaint about
        # how something wears on them was filed as "Noted: your job is killing you."
        return None
    limit = a_limit_reply(text, memory)
    if limit is not None:
        return limit
    if _no_subject(clean, memory):
        return None  # "were shattered after the move - noted" is not a sentence anybody says
    if reads_as_bad_news(read.lower()) or _a_loss(text, memory, read):
        return None  # "our cat was put down yesterday" is not a fact to say back
    if _bad_news_just_before(read, memory):
        # "she took the kids to her mums" after "im thinking of leaving my husband".
        return pick(THE_STORY_GOES_ON, memory, read)
    if reads_like_a_symptom(read.lower()):
        return None  # "i've got a sore throat - noted" is the coldest reply there is
    if reads_as_good_news(read.lower()):
        return None  # "your sister had her baby yesterday - noted" is a filing cabinet
    if reads_as_settled(clean.lower()) and worry_on_the_table(memory):
        return None  # "hes ok now" after a bad cough is news, not a detail to say back
    if DEATH_WORDS.search(read):
        return None
    if WOULD_HAVE_BEEN.search(read) or BODY.search(read) or BLEED.search(read):
        return None  # a birthday nobody reached, or a body that hurts, is not a fact
    if A_FEELING.search(clean):
        return None  # "i want to cry" is not a plan, however the fact store reads it
    if _said_to_the_bot(clean):
        return None  # "you're on form today" is said to the bot, not a fact about the person
    if _a_bare_state(clean.lower()):
        return None  # "you're bunged up - noted" says nothing about being bunged up
    if GOOD_MOOD.search(clean) and not has_news(clean):
        # "life is good", "im in a good mood": a mood is not a detail to file and say back, and
        # the stock echo ("Got it - life is good.") is a line that fits any message. A line with
        # an event in it keeps the frames, because the event is the fact.
        return None
    alone = nobody_around(clean.lower(), memory)
    if alone:
        # Read before the fact frames: "ive got no one to talk to" is not a detail, and a reply
        # that says it back is the coldest answer to it.
        return pick(alone, memory, clean)
    deadline = _a_deadline(clean, read, memory)
    if deadline:
        return deadline
    clock = _a_clock_time(clean, read, memory)
    if clock:
        return clock
    if _after_a_feeling(clean, memory):
        # The reason for the feeling they just gave: said back with the one question that
        # follows from it, whether or not there is a fact here to file.
        thing = _echo(clean)
        if thing:
            return pick(EXPLAIN_TAIL, memory, seed_text=clean).format(
                thing=thing, Thing=thing[:1].upper() + thing[1:])
    lasting = _the_length(clean, memory)
    if lasting:
        return lasting
    hours = _the_hours(clean, read, memory)
    if hours:
        return hours
    chat = _offers_a_chat(clean, memory)
    if chat:
        return chat
    job = _a_job_to_do(clean, memory)
    if job:
        return job
    found = _learned(text, memory)
    if found and _only_a_wish(found):
        # A line that only says what animal they would like is not a fact to say back and not an
        # animal of theirs to ask about: the two pools here answered "i want a labrador" with
        # "No dog, then." and then with "A labrador - how long has it been with you?", inventing
        # a dog and then agreeing to take it away. It is an animal they would like, so it is
        # named back and asked about, which is the line the composer gives a dog they want.
        wanted = "a " + _the_wished_animal(found, clean)
        return pick(WISH_FOR_AN_ANIMAL, memory, seed_text=clean).format(
            Thing=wanted[:1].upper() + wanted[1:], thing=wanted)
    if found:
        nobody = _who_the_figure_is(found, memory, clean.lower())
        if nobody:
            # A receipt says a fact was written down. "hes 9" files nothing, because there is
            # nobody in the chat for the "he" to be, so the reply asks who instead of noting it.
            return nobody
    if found and set(found) <= {"age", "height"} and not _only_the_figure(clean):
        # An age or a height is said back when it is what the line is about. "im 29" is a fact;
        # "im 29 and everyone around me is buying houses and having babies" is a person telling
        # you where they are in life, and handing the sentence back as "Noted: you're 29 and
        # everyone around you is buying houses" is the coldest reply in the deck.
        return None
    animal_wanted = _an_animal_wanted(clean)
    if animal_wanted and not _on_record(animal_wanted, memory):
        # "my daughter is 8 and wants a hamster", "the kids want a pet": the line asks what
        # having one takes, and the store used to file the want and hand the sentence back
        # ("Noted: your daughter is 8 and wants a hamster"). Read before the take-back branch
        # because a want is usually said beside something else - an age, a name, who wants it.
        return _what_a_wanted_animal_needs(animal_wanted, clean, memory)
    coming = _the_animal_coming(found) if found else ""
    if coming:
        # "we are getting a puppy next week": the store keeps it, marked `coming`, so the
        # follow-ups still have it, and the sentence said back is the plan it is.
        return pick(ANIMAL_COMING, memory, coming).format(animal=coming)
    planned = _an_animal_only_planned(found, clean, memory)
    if planned:
        # "im thinking of getting a rescue greyhound" then "actually its a whippet": the second
        # line names a dog and nothing else, so the store filed a dog of theirs and the pet tail
        # asked how long it had been with them - inventing a dog in a house that has not got one.
        # The plan is what the chat is on (it is the topic), and the correction only says which
        # one, so the thing still open is whether they have settled on it.
        said = planned if planned.split()[0] in ("a", "an") else (
            "an " + planned if planned[:1] in "aeiou" else "a " + planned)
        return pick(A_BREED_BEING_CHOSEN, memory, clean).format(
            animal=said, Animal=said[:1].upper() + said[1:])
    if found and (_an_animal_taken_back(found) or _an_animal_turned_down(found, memory)):
        # A take-back in front of an animal ("forget the dog", "not the cat", "never mind the
        # dog") reads as a pet of theirs with nothing said about having it, and saying it back -
        # "A dog \u2014 how long has it been with you?" - invents the dog they have just taken
        # away and asks how long they have had it. When there is an animal of that kind on
        # record the store has its own line ("Right \u2014 no dog, then"), so this declines and
        # lets it answer; when there is none, the line is a person saying no dog, and the reply
        # says the same thing back rather than the stock "Got it. Is there anything you'd like a
        # hand with?".
        animal = _the_taken_back_animal(found)
        if animal and not _on_record(animal, memory):
            if _an_animal_they_had_once(clean):
                # "i had a dog growing up" is a dog they had, so "No dog, then." reads as a
                # refusal of it. What a friend says is what the memory is for.
                return pick(ANIMAL_HAD_ONCE, memory, animal).format(
                    animal=animal, Animal=animal[:1].upper() + animal[1:])
            return pick(ANIMAL_TAKEN_BACK, memory, animal).format(
                animal=animal, Animal=animal[:1].upper() + animal[1:])
        return None
    remark = _a_remark_on_what_was_said(clean, memory)
    if remark:
        # "it cost a fortune", "the slugs got them": a remark on the turn before is answered, not
        # filed and handed back. The reply is also written down as one that hands the subject
        # back, because a remark does not move the conversation on: the answer either side of it
        # is still the answer on the screen (`bot/memory/topics.py::said_again`).
        _a_hand_back(remark, memory)
        return remark
    another = _another_of_what_we_said(clean, memory)
    if another:
        # "we had another one", "my wife got one too", "we had one before": the line is a pointer
        # back and names nothing itself, so saying it back ("Got it - you had another one") tells
        # the person nothing. A friend names the thing from the chat and asks about it.
        return another
    more = _adds_one_more_allergen(text, memory)
    if not more and (memory or {}).get("understood", {}).get("routine"):
        habit = _plain(clean, memory)
        if habit:
            # The line reports a routine, and a thing inside it is what they do it to: "i walk
            # the dog every day", "i feed the cats at six". The pet tail asks how long the animal
            # has been with them - a question about an animal they told you nothing new about -
            # and the routine is the news, so the habit tail says that back instead.
            return habit
    said = None
    if not found or (not more and not _tells_it(clean, found)):
        said = _a_thing_they_have(clean, memory)
    if said:
        return _the_opening_instead(said, clean, memory) or said
    if not found or (not more and not _tells_it(clean, found)):
        # Nothing in the line to file, or a fact that cannot be said back ("my partner and i do
        # a quiz on a thursday"): a habit still gets said back, and everything else declines.
        plain = _plain(clean, memory)
        return _the_opening_instead(plain, clean, memory) or plain
    pets = found.get("pets") if isinstance(found, dict) else None
    # "my cat has kidney failure" is a line about the illness, not about having a cat: the pet
    # tail's "how long has it been with you?" asks about the wrong thing, and the vet's line
    # answers it.
    ill = not A_CHILD_IN_THE_LINE.search(clean) and reads_for_a_pet(clean.lower())
    if (pets and not more and set(found) == {"pets"} and not AS_WELL.search(clean)
            and not A_CHILD_IN_THE_LINE.search(clean) and ill):
        return None  # the vet's line answers it; this is not a line about having a pet
    if (pets and not more and set(found) == {"pets"} and not AS_WELL.search(clean)
            and not A_CHILD_IN_THE_LINE.search(clean)
            and not _nothing_added_but_the_pet(clean, pets)):
        return None  # the line says how the animal is; a question about having it is the wrong one
    if (pets and not more and set(found) == {"pets"} and not AS_WELL.search(clean)
            and not A_CHILD_IN_THE_LINE.search(clean)
            and not _a_pet_that_is_all_right(clean, pets)):
        # What they have is a pet, and the tail it deserves is the one about the pet rather than
        # the receipt it was getting: "we have two cats, milly and tom" was answered "Noted: you
        # have two cats, milly and tom". Read before the kids and the echo, because the store has
        # the animal and the name and the frames had nothing to ask about either.
        said, many = _the_pets_said(pets, clean)
        if said:
            # The thing itself, not "you have the thing": they just said they have it, and a
            # reply that opens by handing the line back is the echo this is fixing. An animal
            # the store has on its way is not one in the house yet, so the questions about
            # having it are the wrong ones: "we're getting a puppy next month" / "its a
            # labrador" was answered "A labrador. What's it like to live with?" about a dog
            # nobody has met. What a friend asks about an animal still to come is when it
            # arrives.
            if _the_pets_are_coming(pets, memory):
                pool = PET_TAIL_COMING_MANY if many else PET_TAIL_COMING
            else:
                pool = PET_TAIL_MANY if many else PET_TAIL_ONE
            return pick(pool, memory, clean).format(
                thing=said, Thing=said[:1].upper() + said[1:])
    kids = _children_with_ages(text)
    if kids:
        thing = _children_said(kids)
    elif more and list(found.get("allergies") or []) == more:
        # The line names one more thing and nothing else, so what is said back is the whole fact
        # with it in it: "Milk too" is not a sentence and "You're allergic to milk too" is.
        thing = "you're allergic to " + " and ".join(more) + " too"
    else:
        thing = _echo(clean, memory)
    if not thing:
        return None
    plan = _plan_tails(found, clean, memory)
    if plan:
        return _pick_ending(plan, memory,
                            thing=thing, Thing=thing[:1].upper() + thing[1:],
                            food=CONDITION_FOOD.get(str(found.get("condition") or "").lower(), "that"))
    frames = _frames(found, _heavy(memory), clean, memory)
    if frames is FRAMES:
        # The first line of a chat has no earlier turn for a receipt to be a detail of, so the
        # plain frames are swapped for the question a friend asks about the fact itself
        # (bot/memory/opening.py). A limit, a pet, a workplace and a plan already ask their own.
        opened = opening.the_opening(thing, clean, memory)
        if opened:
            return opened
    return _pick_ending(frames, memory,
                        thing=thing, Thing=thing[:1].upper() + thing[1:],
                        food=CONDITION_FOOD.get(str(found.get("condition") or "").lower(), "that"))


def _the_opening_instead(said, clean, memory):
    """The question about the fact, where a receipt of the line is all the reply would be.

    On the first line of a chat a receipt is the filing cabinet: nothing comes back about the
    two jobs or the six-year-old. bot/memory/opening.py asks the question a friend asks about
    the fact instead, and stands aside for every line that is not that shape."""
    if not said or not reads_as_a_receipt(said):
        return None
    thing = _echo(clean, memory)
    if not thing:
        return None
    return opening.the_opening(thing, clean, memory)


def _what_a_wanted_animal_needs(animal, clean, memory):
    """What having one of these takes, from the knowledge base, or the want's next question.

    The line already names the animal, so the entry it reaches is that animal's own. A want that
    no entry answers - "the kids want a pet", a fish nobody has named - gets the shortest honest
    thing a friend says, which is the next question, never the animal handed back.
    """
    reading = {}
    try:
        from ..knowledge import lookup  # noqa: PLC0415 - only when an animal is wanted
        reading = understanding("what do i need for a " + animal)
        found = lookup.find(reading)
    except Exception:  # noqa: BLE001 - a knowledge base that cannot answer only adds no reply
        found = None
    if found is not None:
        reply = getattr(found, "reply", None)
        try:
            reply = reply(memory, reading) if callable(reply) else reply
        except Exception:  # noqa: BLE001
            reply = ""
        if isinstance(reply, str) and reply.strip():
            return reply.strip()
    if animal == "pet":
        return pick(A_PET_WANTED, memory, seed_text=clean)
    return pick(A_WANTED_ANIMAL_TAIL, memory, seed_text=clean).format(
        animal=animal, Animal=animal[:1].upper() + animal[1:])


def _plain(clean, memory):
    """An echo of a line with no fact in it, with a tail that fits what kind of line it is.

    Only a plain statement about their own life gets here: fallback asks this after the symptom,
    good-news, plan and trouble questions, for a line whose mood is neutral. A line that is a
    fault to troubleshoot is left to bot/compose/trouble.py, which asks the better question."""
    body = _strip_lead_in(clean)
    if not body or trouble.reads_as_trouble(clean) is not None:
        return None
    if not _about_them(body):
        return None
    if not HABIT.search(body) and not GOING.search(body):
        return None
    if OBLIGED.search(body):
        return None
    if TROUBLE.search(body) or FEELING.search(body):
        # "i cry every morning", "i shout at my kids every morning", "i get panic attacks every
        # week": a feeling or a row is not a routine to admire, and those modules say it better.
        return None
    thing = _echo(clean, memory)
    if not thing:
        return None
    if HABIT.search(body):
        options = HABIT_TAIL
    elif GOING.search(body) and not GOING_BAD.search(body):
        options = GOING_TAIL
    else:
        return None  # anything else keeps the stock line, which is right for a line with no shape
    return pick(options, memory).format(thing=thing, Thing=thing[:1].upper() + thing[1:])


def a_job_to_do(text, memory=None):
    """A thing with something still to be done to it, as the job it is, or None.

    Every lane that has to know whether a line is a job on the person's list rather than an
    appointment to get ready for reads it here, so one gate decides it for all of them.
    """
    try:
        return _a_job_to_do(text, memory)
    except Exception:  # noqa: BLE001 - a reading that cannot be made answers nothing
        return None


def _a_job_to_do(clean, memory=None):
    """A thing with something still to be done to it, answered as the job it is.

    "i have got a loft to clear out" is not a possession - it is a job on their list - and the
    receipt it used to get ("Noted: you've got a loft to clear out") is the filing cabinet
    STYLE.md rules out. The same gate as `_a_thing_they_have` decides it is a thing at all; then a
    verb of doing after "to" makes it a job, and the reply is the question a friend asks about a
    job. It is asked here, before the fact paths, so a line about the person's evening in front of
    it cannot change the reading.
    """
    read = _spoken(_repairs(clean, memory)) or clean
    if not JOB_TO_DO.search(read):
        return None
    match = HAVE_THING.search(read)
    if not match:
        return None
    thing = match.group(1).lower().strip("-'")
    if not thing or thing in NOT_A_THING or thing.isdigit():
        return None
    if _about_a_body(read, memory) or PLACED_IN_THE_PAST.search(read):
        return None
    if HABIT.search(read):
        return None  # "i have a lawn to mow every week" is a routine, and has its own reply
    what = _echo(clean, memory)
    if not what:
        return None
    # The bot says it in the person's own contraction: "you've got a wardrobe to put up", never
    # "you have a wardrobe to put up".
    what = HAVE_A.sub(r"\1've got a", what)
    tails = JOB_TAIL[1:] if JOB_HAS_A_DAY.search(read) else JOB_TAIL
    return pick(tails, memory, seed_text=read).format(
        thing=what, Thing=what[:1].upper() + what[1:])


def _a_thing_they_have(clean, memory=None):
    """A thing they have, said back: "i have a bike" -> "Noted: you have a bike".

    Only when the line is the thing and nothing else: the thing word has to be a thing (not a
    feeling, an idea, a question or a body that hurts), and what is behind it is the rest of the
    line or nothing.
    """
    read = _spoken(_repairs(clean, memory)) or clean
    match = HAVE_THING.search(read)
    if not match:
        return None
    thing = match.group(1).lower().strip("-'")
    if not thing or thing in NOT_A_THING or thing.isdigit():
        return None
    if _about_a_body(read, memory) or PLACED_IN_THE_PAST.search(read):
        return None
    if HABIT.search(read):
        # A repeating time makes the line a routine, not a thing they have: "i have two
        # digestives with my tea every afternoon" is answered by the habit tail ("that's a
        # habit now"), and saying it back as a bare receipt - "Noted: you have two digestives
        # with my tea every afternoon" - was a regression that took the shape away from every
        # routine typed as a "have" line.
        return None
    what = _echo(clean, memory)
    if not what:
        return None
    pointer = _what_the_pointer_is(read, memory)
    if pointer:
        return pointer
    return pick(FRAMES, memory).format(thing=what, Thing=what[:1].upper() + what[1:])


def _frames(found, heavy=False, clean="", memory=None):
    """Which set of endings this fact wants: a limit is answered with what the bot does with it."""
    if found.get("budget"):
        return SPENDING_FRAMES if _a_spending_budget(clean, memory) else BUDGET_FRAMES
    condition = str(found.get("condition") or "").lower()
    if condition in CONDITION_FOOD:
        return CONDITION_FRAMES
    if found.get("diet") or found.get("allergies"):
        # "no alcohol" is a drink, and only a diet that names a drink gets the food out of the line.
        if "alcohol" in str(found.get("diet") or "").lower():
            return DRINK_FRAMES
        return FOOD_FRAMES
    if heavy and not _just_a_liking(found):
        # A death or a separation two turns back: the fact comes back, "noted" does not. Only for
        # a fact about the family the loss named - a pet or a job is not one more thing landing
        # on them, and claiming it is read as a mistake (see STILL_FRAMES).
        return HEAVY_FRAMES if _about_the_family(found) else STILL_FRAMES
    # Somebody else's limit is a limit all the same: what the person told the bot is that there is
    # a thing to cook or plan around, so it is answered with what the bot does with it.
    if any(isinstance(entry, dict) and entry.get("allergies")
           for entry in (found.get("others") or [])):
        return OTHER_LIMIT_FRAMES
    if _about_someone_else(found, clean):
        if SOMEONE_GOOD.search(str(clean or "")):
            return SOMEONE_TAIL
        if _the_milestone(clean):
            return SOMEONE_MILESTONE_TAIL
        if _a_visit(clean):
            return VISIT_TAIL
    if _a_workplace(found, heavy, memory):
        # Which ending the line gets is the line's own, so the four pools do not open every
        # conversation about a job with the same sentence: the first turn of a chat has no
        # history for bot.compose.pick to vary on, and "what's a normal day like?" for every
        # workplace line in the deck reads as a script. Same line, same reply.
        step = len(clean or "") % len(WORK_FRAMES)
        return WORK_FRAMES[step:] + WORK_FRAMES[:step]
    coming = _a_day_coming(clean)
    if coming:
        return coming
    if _only_a_liking(found) and a_liked_thing(found) and _a_like_of_one_thing(clean, memory):
        # Which ending is the line's own, the way the workplace pool rotates: the first turn of a
        # chat has no history for bot.compose.pick to vary on, and one ending for every like in
        # the deck reads as a script.
        step = len(clean or "") % len(LIKES_FRAMES)
        return LIKES_FRAMES[step:] + LIKES_FRAMES[:step]
    return FRAMES


def _echo(clean, memory=None):
    """What they said, said back and short: "my sister is called Meg" -> "your sister is called
    Meg"."""
    # "god i hate mondays" is "i hate mondays" said back, not "god you hate mondays": the
    # exclamation is the person's exasperation, not the subject of the line.
    clean = without_a_leading_exclamation(clean)
    said_it = _repairs(clean, memory)
    body = _strip_lead_in(said_it)
    if body and not _says_something(body):
        # The repair was the whole sentence and the fact is a bare value: "sorry, i mean three"
        # is "Got it - you mean three" and not "Got it - three", which is a fragment that no
        # longer says three of what. A fact with a verb of its own ("i got the second
        # interview") is said without the frame.
        kept = _strip_lead_in(said_it, keep_the_repair=True)
        if kept != body and not _only_the_correction_in_front(kept, body):
            body = kept
    if not body:
        return None
    if _names_nothing(body):
        return None
    if (_OPENS_WITH_A_LINK.match(body) and len(body.split()) <= 3
            and not MONEY_ONLY.match(body.strip(" .,!?"))):
        return None  # "for moaning": half a sentence, left to the module that answers apologies
    if len(body) <= MOST:
        said = body  # short enough to say whole, and whole is what a list ("me, my partner and
        # our dog") needs
    else:
        clauses = [clause.strip() for clause in STOP.split(body) if clause.strip()]
        said = ", ".join(clauses[:CLAUSES]) if clauses else body
    said = _cut(said).strip(" ,;:-!?.\u2014")
    said = POLITE.sub("", said).strip(" ,;:-")
    said = _tail_off(said)
    said = _contrast_off(said).strip(" ,;:-")
    said = _reason_off(said, clean).strip(" ,;:-")
    said = _pick_off(said).strip(" ,;:-")
    if not said:
        return None
    back = _tidy(KIN_POSSESSIVE.sub(r"\1's", say_it_back(_spoken(said)).strip(" ,;:-")))
    if not back:
        return None
    # "i have got a loft to clear out" came back as "you have got a loft to clear out", which is
    # not how anybody says it: the person's own contraction is kept, in the bot's wording.
    back = HAVE_GOT.sub(r"\1've got", back)
    # "i'm 2 dogs" is not a state a person is in: a count of things after "i'm" is what they
    # have, so it comes back as "you've got two dogs" and never "you're two dogs". A length of
    # time is a state ("you're two years in", "you're 5 minutes away"), so time units are left.
    counted = A_COUNT_NOT_A_STATE.match(back)
    if counted and counted.group(2).lower() not in UNITS_OF_MEASURE:
        back = "you've got " + back[counted.start(1):]
    # The clause is said back the way it is written on the page, not the way it is typed:
    # "your daughter whos 9" reads as a typo, "your daughter who's 9" reads as a sentence.
    return WHOS.sub("who's", back)


def said_back(clean, memory=None):
    """Their line in the bot's own words, short: "i work all day" -> "you work all day".

    The same reading the echo reply is built from, for a module that wants to name what the
    person said inside a sentence of its own rather than hand it back on its own."""
    return _echo(clean, memory)


def _contrast_off(said):
    """`said` without the wrong value it replaced: "my budget is 400 a month not 300" -> "my
    budget is 400 a month".

    Only a value is taken off. "my sister is not coming" and "my son is not well" carry the same
    shape and are whole facts, so the cut needs a value on one side of the "not": the number or
    the day it corrects, on either side of it.
    """
    again = CONTRAST_SAID_AGAIN.match(str(said or "").strip())
    if again and _a_value(again.group("old")):
        return "%s %s" % (again.group("thing"), again.group("new"))
    match = CONTRAST.search(said or "")
    if not match:
        return said
    old = [word for word in re.split(r"\s+", match.group("old").strip(" .,;:-")) if word]
    if old and old[0].lower() in ("the", "a", "an"):
        old = old[1:]  # "not the 5th" corrects a day, and the article is not the value
    if not old or not re.search(r"[a-z0-9]", old[0], re.I):
        return said
    kept = [word for word in re.split(r"\s+", said[:match.start()].strip(" .,;:-")) if word]
    if old[0].lower() in NOT_A_VALUE:
        return said
    if not (_a_value(old[0]) or (kept and _a_value(kept[-1]))):
        return said
    restated = _the_value_put_right(said, match)
    if restated:
        return restated
    return said[:match.start()]


def _the_value_put_right(said, match):
    """The line with the value a restated correction puts right, or "" for any other shape.

    A correction can put the old value in the middle of the line rather than at its end: "hes not
    4 hes 5", "my son is not 4 hes 5". The cut above leaves only what stands in front of the
    "not", so the person was told "Got it \u2014 he's." and "Got it \u2014 your son is." - the
    bot handing back the first half of their sentence with the fact gone. The value the line is
    corrected to is the last one in the clause, and what is in front of it names the subject
    without naming a value, so the line goes back together with that value on the end.
    """
    head = " ".join(str(said or "")[:match.start()].split()).strip(" ,;:-—")
    if not head:
        return ""
    if any(_a_value(word) for word in re.split(r"\s+", head)):
        return ""  # the value on this side is the one said back, as it was before
    words = [word for word in re.split(r"\s+", match.group("old").strip(" .,;:-")) if word]
    if len(words) < 3:
        return ""  # one value in the clause: the ordinary cut is the whole of it
    second = next((at for at in range(1, len(words)) if _a_value(words[at])), None)
    if second is None:
        return ""
    between = [word.lower().strip(".,!?'\u2019") for word in words[1:second]]
    if not between or any(word not in BETWEEN_VALUES for word in between):
        return ""
    return head + " " + " ".join(words[second:])


def _a_value(word):
    """Whether this word is a value a correction can replace ("300", "june", "£40")."""
    low = str(word or "").strip(" .,;:!?\u2019'").lower()
    if not low:
        return False
    if VALUE.match(low):
        return True
    return low in DAYS or low in MONTHS


def _cut(said):
    """`said` down to MOST characters at a word boundary, so an echo stays an echo."""
    if len(said) <= MOST:
        return said
    kept = said[:MOST].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return kept if " " in kept else said[:MOST]


# Words that carry a capital only because they started the person's sentence. Saying the detail
# back puts it after "Got it - " ("Got it - just you, four nights"), where a capital reads like a
# mistake, so these come down; a name ("Tokyo", "September") keeps the capital they gave it.
FIRST_WORD = frozenset((
    "he", "he's", "he'll", "she", "she's", "she'll", "it", "it's", "it'll", "they", "they're",
    "they'll", "they've", "we", "we're", "we'll", "we've", "our", "there's", "there'll",
    "the", "this", "that", "these", "those", "a", "an", "my", "his", "her", "its", "just",
    "not", "no", "and", "but", "so", "also", "then", "now", "still", "only", "even", "both",
    "all", "every", "at", "in", "on", "for", "after", "about", "around", "one", "two", "three",
    "four", "five", "six", "seven", "eight", "nine", "ten", "half", "someone", "something",
    "nothing", "theres", "theyll",
))


def _tidy(text):
    """`text` as one sentence piece: the second person in lower case, and nothing else
    changed, so a proper name ("Tokyo") keeps the capital the person gave it."""
    words = text.split()
    out = []
    for index, word in enumerate(words):
        low = word.lower()
        if low in ("you", "your", "you're", "you've", "we", "our", "yourself"):
            word = low  # you() keeps the capital of "I", which only belongs at the start
        elif index == 0 and low in FIRST_WORD:
            word = low  # a capital only because it started their sentence
        out.append(word)
    return " ".join(out)
