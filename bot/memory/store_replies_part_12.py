"""Part 12 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import current, last_module, last_user, name, others, thread, user
from ..memory.places import _a_town_moved, _asked_person
from ..memory import pending
from ..memory import another as second_half
from ..memory import choice as choose
from ..memory import decided
from ..memory import company
from ..memory import spent
from ..memory import surname as family_name
from ..memory import plans
from ..memory.taste import ASKS_FOR_TASTES
from ..memory import facts as extract
from ..memory import history
from ..memory import recall
from ..memory import reminded
from ..memory import reject as turned_down
from ..memory import told as told_about
from ..memory.when import already_answer, until_answer, when_answer
from ..memory.store_lines import NOTHING_STARTED
from ..memory.enough import enough_reply
from ..memory.relations import (
    AGE_ASK, _a_list_of_names, _a_person_in_the_store, _ages_reply, _animal_family, _called,
    _canon_relation, _folded, _named_person, _person_from_pronoun, _relation_reply, _relations_of,
    _the_group_was_said, _the_group_word,
)
from ..modules.memory_tables import (
    DAY_ASKS, DAY_IT, DAY_THING, ELIDED_NOT_SURE, PLAN_ASKS, PLAN_MINE, SAID_ASK,
    SAID_AS_A_SENTENCE, TIME_ASKS, TIME_IT, TIME_THING, TOPIC_ASK, WHAT_I_SAID, WHEN_ASKS,
    WHEN_PLAN, WHEN_THING, WHEN_THING_VERB, WHERE_PLAN,
)
from .store_replies_part_01 import (
    ACTIVITY_ASK, ASKED_ALL, DIET_ASK, DIET_HOW_TO, FIRST_ASK, MORE_OF_IT, NO_RECORD, PLAN_WORDS,
    UP_TO_ASK, _a_count_ask, _bare, _retraction_this_turn, _says_more_than_the_ask,
    _the_ask_after_a_statement, _the_back_this_turn, OTHER_NAME_ASK, PRONOUN_NAME_ASK,
    _with_an_in_law, NAMED_ACTIVITY,
)
from .store_replies_part_02 import (
    _slot_words, _yes_then, PLACES_ASK, PLACE_ADVICE, PLACE_RECALLED, SELF_WORD, TALKED_ABOUT,
    THE_CHAT_ASK, THING_AGAIN, _about_the_bot_here, _an_attribute_they_gave, _summary_ask,
    _which_thing_was_it,
)
from .store_replies_part_03 import (
    _name_reply, _a_place_new_to_the_chat, _answer_the_new_one, _name_fixed_this_turn,
    _return_reply, _everyone_they_mean, _the_group, _what_the_group_is_called, _which_one_of_them,
    _who_the_pronoun_means,
)
from .store_replies_part_04 import (
    REMEMBER_IT, ASKING_AGAIN, SAID_ABOUT, WHERE_WORK, AVOID_ADVICE, BARE_WHAT_I_DO,
    A_ONE_PERSON_WORD,
)
from .store_replies_part_05 import (
    _job_reply, _places_reply, _a_name_for_the_pet, _a_part_of_the_job_never_said, _a_rate_changed,
    _after_the_yes_no_frame, _correction_this_turn, _fact_fixed_this_turn, _fact_moved_this_turn,
    _how_far_along, _their_place, _the_allergy_is_what_is_asked, _the_job_was_just_said,
)
from .store_replies_part_06 import (
    _a_pronoun_age, _age_compare, _asks_about_someone, _denial_this_turn, _other_person_reply,
    _which_comes_first,
)
from .store_replies_part_07 import (
    _kids_reply, _a_rule_on_eating, _a_thing_i_own_reply, _a_why_line_they_have_answered,
    _asks_for_a_fact, _confirmation, _limit_reply, _not_the_same_reply, _remembers_fact,
    _the_name_they_picked, _the_pick_asked_again, _vary, _what_the_pet_is_called,
    _who_is_the_name_reply,
)
from .store_replies_part_08 import (
    _age_reply, _plans_reply, _a_denial, _a_persons_birthday_reply, _names_its_thing,
    _pet_part_reply, _plan_was_corrected, _the_line_before_was_a_plan, _the_prep_day,
    _the_fact_is_kept, _a_description, _a_thing, _activity_line, _recap, _says_the_thing,
    _the_last_ask_about_the_bot, _the_making_line_they_said,
)
from .store_replies_part_09 import (
    TASTE_ASK, _about_what_they_said, _first_bot_reply, _summary_reply, _summed_up, _taste_reply,
    _tastes_said, _topics_reply,
)
from .store_replies_part_10 import (
    _a_diet_told, _a_dislike_told, _about_a_person_reply, _about_this_chat, _an_open_attribute_ask,
    _doing_again, _first_reply, _repeat_ask, _trim,
)
from .store_replies_part_11 import (
    _diet_reply, _fact_reply, _a_pregnancy_of_their_own, _a_state_that_was, _a_state_told,
    _asked_reply, _recall_reply, _repeat_reply, _said_reply, _what_i_said_about, _last_real,
    _the_line_named,
)


def _told_readers():
    """The store's own answer for each kind of fact, for `told` (bot/memory/told.py).

    "have i told you about my allergies" is the same fact as "what am i allergic to", so it is
    answered with the sentence the store already says for it: one set of sentences for one fact,
    and the two asks cannot drift apart.
    """
    return {"allergies": lambda memory: _fact_reply(memory, "allergic to"),
            "budget": lambda memory: _fact_reply(memory, "budget"),
            "diet": lambda memory: _diet_reply(memory),
            "age": lambda memory: _age_reply(memory),
            "name": lambda memory: _name_reply(memory, "my name"),
            "job": lambda memory: _job_reply(memory),
            # The plan read out whole: the told reader asks about the plan, not for a part of it.
            "plan": lambda memory: _plans_reply(memory, "what am i planning"),
            "places": lambda memory: _places_reply(memory, "where do i live"),
            "pets": _told_pet_reply,
            # A puppy is a dog and a kitten is a cat, and `told` needs the store's own reading of
            # that: the two answers must not disagree about which animal was given.
            "family": _animal_family,
            "kids": lambda memory: _kids_reply(memory, "how many kids do i have") or ""}


def _the_one_animal_with_a_name(memory):
    """What the one animal they named is called, or "" when the chat holds none or several.

    One animal and one name is not a guess: "we have a cat called max" then "hes 4 months" then
    "what is his name" asks about the only animal in the chat. Several animals leave the pronoun
    pointing at one of them, which the store cannot tell, so it says nothing.
    """
    pets = [pet for pet in (user(memory).get("pets") or [])
            if isinstance(pet, dict) and pet.get("name")]
    if len(pets) != 1:
        return ""
    animal = str(pets[0].get("animal") or "pet")
    return _fact_reply(memory, "what is my " + animal + " called")


def _told_pet_reply(memory, animal):
    """What the store says about a kind of pet, for "have i told you about the cat"."""
    pets = [pet for pet in (user(memory).get("pets") or []) if isinstance(pet, dict)
            and _animal_family(str(pet.get("animal") or "")) == animal]
    if not pets:
        return ""
    if any(pet.get("name") for pet in pets):
        return _fact_reply(memory, "what is my " + animal + " called")
    return _fact_reply(memory, "how many " + animal + "s do i have")


def _the_fact_just_asked(memory, low):
    """The fact the store answered on the turn before, said again for "do you remember it?".

    The ask carries no subject of its own, so it is about the fact the store just said - and
    only when that fact is recent (the last turn or the one before it) and the store was the
    one that said it. When there is no such fact the line is left to the other modules, so
    "do you remember it?" in a fresh chat still gets the honest answer about this chat only.
    """
    if not isinstance(memory, dict) or not REMEMBER_IT.match(str(low or "").strip()):
        return None
    asked = memory.get("asked")
    if not isinstance(asked, dict) or not asked.get("slot"):
        return None
    turns = memory.get("turns") or []
    try:
        asked_turn = int(asked.get("turn") or 0)
    except (TypeError, ValueError):
        return None
    if not turns or len(turns) - asked_turn > 2:
        return None
    if last_module(memory) != "memory_store":
        return None  # a question in between ("whats my name" / "nice one" / "remember it?")
    reply = _respond(_slot_words(str(asked["slot"]), memory), memory)
    if not reply or ELIDED_NOT_SURE.search(reply):
        return None
    return _yes_then(reply)


def _respond(text, memory):
    # "whats our plan", "what have we decided", "what do we know so far": the ask is for
    # everything the chat holds, so the answer is the list (`_summary_reply`) - not the newest
    # line, not a choice the chat never made ("You haven't picked one yet"), and not a card. It
    # goes first because the readers below each answer a question of their own: `decided` reads
    # "what have we decided" as a choice and denies a chat that made several.
    low_here = " ".join(str(text or "").lower().split())
    if _summed_up(low_here):
        # A chat that holds nothing of theirs has nothing to sum up, and the list's tail would
        # name the ask's own verb as the subject ("we've been on the decided"). The recap's own
        # "we're still at the beginning" is the honest reply to a summary of an empty chat.
        if not any(str(value or "").strip() for value in user(memory).values()):
            return _vary(NOTHING_STARTED, memory)
        return _summary_reply(memory)
    renamed = _name_fixed_this_turn(text, memory)
    if renamed:
        return renamed
    put_right = _fact_fixed_this_turn(text, memory)
    if put_right:
        return put_right
    moved = _fact_moved_this_turn(text, memory)
    if moved:
        return moved
    corrected = _correction_this_turn(text, memory)
    if corrected:
        more = _answer_the_new_one(memory, memory.get("correction"))
        if isinstance(more, str) and more.strip():
            if _a_rate_changed(text, memory):
                # The figure the person changed is what they put by each month, and the answer
                # they want is how long the goal takes at the new rate. The note about the line
                # they corrected is not news beside it ("Save 500 pounds - got it." names a sum
                # they did not touch), so the new sum is the whole turn.
                return more.strip()
            return corrected.rstrip() + " " + more.strip()
        return corrected
    denied = _denial_this_turn(text, memory)
    if denied:
        return denied
    back = _the_back_this_turn(text, memory)
    if back:
        return back
    retracted = _retraction_this_turn(text, memory)
    if retracted:
        return retracted
    # "my sister lives in perth" then "no, york": the value alone corrects the line before it,
    # and the line before it gave somebody's town, so the correction is the new town and not a
    # shrug that leaves the store saying Perth.
    moved_town = _a_town_moved(memory, text)
    if moved_town:
        return moved_town
    # A plan with something still missing is the ask they did not make: "ive got a wedding in 3
    # weeks and i still havent got an outfit" was filed as a receipt ("Noted: you've got a wedding
    # in 3 weeks and you still haven't got an outfit."), which tells a person with a wedding coming
    # nothing they did not just say. The occasion and the gap are both in the line, so the question
    # is the one the knowledge base answers about the thing that is missing.
    left_out = pending.answer(text, memory) if isinstance(text, str) else None
    if left_out:
        return left_out
    # The ask for their own family name, first name or both: "whats my surname" names a fact the
    # store keeps and the recall table reads as no fact at all, so it was answered "you've not
    # said" - or, with "last name", with their first name. Read early, because a store holding a
    # surname answered "do you know my first name" by reading the surname out, and the readers
    # after this one echo the earlier line. A how-to about a surname ("how do i change my
    # surname") names the world and is left to whoever answers those.
    named = family_name.reply_for(text, memory)
    if named:
        return named
    picked = _the_name_they_picked(text, memory)
    if picked:
        return picked
    called = _what_the_pet_is_called(text, memory)
    if called:
        return called
    picked_again = _the_pick_asked_again(text, memory)
    if picked_again:
        return picked_again
    folded = _folded(text, memory)
    low = MORE_OF_IT.sub(r"\1", _bare(folded))
    told = _a_diet_told(text, memory, low)
    if told:
        return told
    # A pregnancy, or a limit on drink, is a fact about the person they live with - the same kind
    # of thing as a diet or an age, and not something wrong that needs a careful question. The
    # line is said back with their name in it so the person knows it was taken in.
    own = _a_pregnancy_of_their_own(text, memory, low)
    if own:
        return own
    stated = _a_state_told(text, memory, low)
    if stated:
        return stated
    # The same state, said in the past: "my wife was pregnant" is not news now, and the store must
    # not congratulate it or advise on trying for a baby.
    was = _a_state_that_was(text, memory, low)
    if was:
        return was
    disliked = _a_dislike_told(text, memory)
    if disliked:
        return disliked
    # "what should I call it?" a turn after "we're getting a kitten" asks the bot for a name. A
    # name is taste, not knowledge: there is no entry to look up, and "a search should sort you
    # out" is no answer at all - it is the one thing here a friend just gives.
    named = _a_name_for_the_pet(text, memory, low)
    if named:
        return named
    # "who's older, me or my wife", "am i older than my mum", "how much older is she": two ages
    # the store was given, put side by side. The answer is arithmetic on two told facts, which
    # is the store's own business; without both of them the turn stays free for whoever can
    # answer it.
    compared = _age_compare(memory, low)
    if compared:
        return compared
    # "how far along is she" a turn after "my wife is 8 weeks pregnant": the weeks are a fact the
    # chat gave and the store kept, and no knowledge base knows them. The ask names the length,
    # not the person, so the pregnancy the store holds is the answer.
    along = _how_far_along(memory, low)
    if along:
        return along
    # "which one is first", "whose is sooner", "what comes first": two plans with a date each,
    # put in the order the calendar puts them. Like two ages, this is not knowledge about the
    # world - the store is the only place both dates are kept - and without two of them the
    # search hedge is all anyone can say, so the turn stays free.
    ordered = _which_comes_first(memory, low)
    if ordered:
        return ordered
    # "what did i decide to get", "what did we settle on", "which one did i pick": a chat that
    # weighed two things and picked one, asked for the choice it made. The topic's advice took
    # these (dog walking after "actually a dog") because the ask names the thing and not the
    # choice, so the store answers it here.
    settled = decided.answer(text, memory)
    if settled:
        return settled
    # "who is coming with me", "who am i going with": the companion they told the chat about was
    # acknowledged and then dropped, and the search shrug (or, worse, "you haven't told me your
    # name yet") is not what a friend answers.
    coming = company.answer(text, memory)
    if coming:
        return coming
    # "what's my mum's name", "how old is my son": a fact kept about someone they mentioned is
    # answered from that person, the same way "what does my mum eat" is.
    theirs = _relation_reply(memory, low)
    if theirs:
        return theirs
    # "have i told you about my sister", "did i mention the trip": a question about the chat, and
    # the store is the only part of the bot that can answer it. It says the fact, quotes the line
    # they said, or says nothing is kept - the search hedge is wrong on all three.
    # "remember when i said my knee hurt", "remember we talked about lisbon": the same thing as a
    # statement rather than an ask. The word in it is a topic too, so `answers` read the knee and
    # served the advice a second time; the store is the part that can say what was actually said,
    # so the callback is answered here and the line is claimed in `TAKES_AS_IT_COMES`. It is read
    # by the same readers as the ask, so a fact the store keeps is said the same way either side.
    called_back = told_about.callback(text, memory, facts=_told_readers(),
                                      plain=lambda asked: _respond(asked, memory),
                                      claims=lambda: bool(_about_this_chat(text, memory)))
    if called_back:
        return called_back
    remembered = told_about.answer(text, memory, facts=_told_readers(),
                                    plain=lambda asked: _respond(asked, memory),
                                    claims=lambda: bool(_about_this_chat(text, memory)))
    if remembered:
        return remembered
    if WHERE_PLAN.search(low):
        # "where are we going again", "remind me where we're going": the plan carries the place,
        # and nothing in the knowledge base knows they are going anywhere.
        asked = _plans_reply(memory, low)
        if asked:
            return asked
        gone = user(memory).get("plan_dropped")
        if isinstance(gone, str) and gone:
            # They took it back a turn or two ago, so the honest answer names that rather than the
            # empty store. What they took back is a place more often than not - "the isle of skye
            # in june" is five words and a good thing to say back - but a trip with no place in it
            # keeps the whole sentence: "we've booked two weeks in portugal in september" put the
            # line itself in the store, and "We've booked two weeks in portugal in september is
            # off, then" reads as a machine reading a note aloud. The two are told apart by shape,
            # not length: a sentence starts with who is doing it.
            if SAID_AS_A_SENTENCE.match(gone):
                return pick(["That plan is off, then \u2014 where are you going?",
                             "Right, that one is off the record \u2014 where are you headed?",
                             "Scratch that trip, then \u2014 where is it now?"], memory)
            shown = gone[:1].upper() + gone[1:]
            return pick([shown + " is off, then \u2014 where are you going?",
                         "Not " + shown + ", then. Where are you headed?",
                         "Right, " + shown + " is dropped \u2014 where is it now?"], memory)
        return None
    # "when am I moving?", "when is she due?" name a thing and not the date: the date is in the
    # line that stated it, so it comes back on its own. The helper refuses every ask it cannot
    # place, so every line can be offered it.
    # "when is my mums birthday", "when is toms birthday": the date is kept on the person
    # (bot/memory/facts.py, OTHER_BIRTHDAY), so this is memory and not a fact about the world.
    # Without it the ask was answered "I don't have a date from you for that" a turn after the
    # date had been given, which denies what the person just said.
    whose = _a_persons_birthday_reply(memory, low)
    if whose:
        return whose
    # "how many weeks till that", "how long have i got": the date is in a line they said and the
    # answer is the count from today to it. The bot had the date and gave back a hedge or the
    # statutory holiday allowance, so the count is the store's line.
    said_until = until_answer(text, memory)
    if said_until:
        return said_until
    # "where did i say we were going", "how often did i say i go": an ask about what they said, and
    # the answer is the line itself. It comes before the date reader, which took the "say" for the
    # event and answered a question about a trip with "No - that's in February."; the quotation
    # cannot be wrong the way that was, and where nothing matches it says so rather than guessing.
    from ..compose.own_facts import said_back
    the_line_back = said_back(text, memory)
    if the_line_back:
        return the_line_back
    # "did i already go", "have i been yet": the date is filed, but which side of today it is on
    # is a question of its own and "In June." does not answer it.
    said_side = already_answer(text, memory)
    if said_side:
        return said_side
    said_when = when_answer(text, memory)
    # "when's my birthday" is the one when ask the plan reader gets wrong: the birthday is a date
    # they gave once, and a plan that merely mentions one ("my sons birthday is in august") is not
    # their own birthday - reading it as the plan put someone else's date in their mouth. It is
    # kept out of every date the plan holder could answer with, the bare one included.
    a_birthday_ask = recall.ask(text) == "birthday" or recall.ask(low) == "birthday"
    if (WHEN_ASKS.search(low) or WHEN_THING.search(low) or TIME_ASKS.search(low)
            or TIME_THING.search(low) or TIME_IT.search(low) or DAY_THING.search(low)
            or DAY_IT.search(low) or DAY_ASKS.search(low) or WHEN_PLAN.search(low)
            or WHEN_THING_VERB.search(low)) and not a_birthday_ask:
        # "when do I start?" is about the plan that names that verb, when there is one, and
        # "when is the wedding?" about the plan that names that thing. A when ask about
        # something they never told us is left to whoever can answer it.
        prep = _the_prep_day(memory, low)
        if prep:
            return prep
        asked = _plans_reply(memory, low)
        if asked:
            return asked
        if said_when:
            return said_when
        if (WHEN_ASKS.search(low) or TIME_ASKS.search(low) or WHEN_THING_VERB.search(low)
                or DAY_ASKS.search(low)):
            # Nothing here knows the date, but the paragraph the person has just been given may
            # answer it itself: "how long will it take" after the countdown is its opening step.
            part = plans.follow_up(text, memory)
            if part:
                return part
            return None
    elif said_when and not a_birthday_ask:
        return said_when
    # A plan announced is the question its plan implies: "im planning a trip" files the plan and
    # answers nothing, while "how do i plan a trip" reaches the knowledge base. The fact is kept
    # either way; this only decides what the person is told (bot/memory/plans.py).
    planned = plans.answer(text, memory)
    if planned:
        # The paragraph is what the plan implies, and it is kept for the turn that asks for it
        # (observe, above): laying it out unasked answers a question nobody put, where the
        # composer has a warm word and a question for the announcement itself (sturdy-poppy,
        # #1848). So the announcement is not this module's turn.
        return None
    # The turn after that paragraph is a question about one part of the plan ("how do i pick a
    # venue", "when should i book the registrar"): the part has its own sentence in it, and the
    # paragraph again would be the same words twice (bot/memory/plans.py).
    part = plans.follow_up(text, memory)
    if part:
        return part
    if not folded:
        return None
    asked = history.asked(text, memory)
    if asked == "first":
        return _first_reply(memory)
    if asked == "first_bot":
        return _first_bot_reply(memory)
    if asked == "said_about":
        said = _what_i_said_about(memory, history.the_thing_named(text))
        if said:
            return said
    if asked == "topics":
        # A recap ask is answered with the thing we were on, not with every line they have
        # typed put in quotation marks: "what did we talk about" after "im tom and i work as a
        # bus driver" / "my knee is killing me" is about the knee.
        if _summary_ask(low) or TALKED_ABOUT.search(low):
            return _topic_reply(memory, low)
        return _topics_reply(memory)
    handed_back = choose.reply_for(text, memory)
    if handed_back:
        return handed_back
    # "is that enough" is about the amount they just gave, and the answer a turn earlier named the
    # figure to aim at, so the two numbers are read against each other.
    enough = enough_reply(text, memory)
    if enough:
        return enough
    # The other side of handing the choice back: they turn the offer down ("nah not that one",
    # "ive seen all those"). The answer is another of the things the bot itself named a turn
    # ago, or the one question that lets it pick again - never the line said back as a receipt
    # ("Got it - nah not that one"). The reading is in bot/memory/reject.py.
    another_of_them = turned_down.reply_for(text, memory)
    if another_of_them:
        return another_of_them
    # "what else can i try?" after an answer asks for the other half of that answer, not for the
    # same opening line again. The store reads it because what it hands back is its own last
    # answer, and no knowledge entry has it (bot/memory/another.py).
    other = second_half.other_option(text, memory)
    if other:
        return other
    # Going back to something said earlier is read next: the return line is about the
    # conversation, not a new subject, and the topic must move even when the reply itself is left
    # to the modules that answer questions.
    back = _return_reply(text, memory)
    if back:
        return back
    # "do you remember that i live in leeds": the person asks whether the store kept a fact and
    # says the fact. It is their own statement with a frame around it, so it is read as that
    # statement rather than as a question about the bot's memory in general.
    remembered = _remembers_fact(text, memory)
    if remembered:
        return remembered
    # "am i vegetarian?", "is my name sam?" — a yes/no question about the person, answered from
    # what they told you rather than guessed at.
    # "do i eat meat" after "im vegetarian": the rule they gave the store, asked back as a yes/no
    # about a food. It came before the confirmation reader found nothing and the turn fell to a
    # search hedge about a fact the bot had been told a turn earlier.
    ruled_out = _a_rule_on_eating(text, memory)
    if ruled_out:
        return ruled_out
    confirmed = _confirmation(text, memory)
    if confirmed:
        return confirmed
    # "do i like fish?" is a question about a taste they have already told the bot: the store
    # keeps it, so the answer is the taste and not a search hedge. A thing they have never said
    # anything about is left to the other modules.
    if ASKS_FOR_TASTES.search(low):
        liked = _tastes_said(memory)
        if liked:
            return liked
    if TASTE_ASK.search(low):
        said = _taste_reply(memory, low)
        if said:
            return said

    # The shaped reader is the safety net: when none of the store's own readers answers the line,
    # the same ask in words they have no pattern for ("do you remember my budget") is still an
    # ask about what they told you, and it is answered with the reply for that fact. It runs last
    # so a reader that quotes the line ("what did I say about the boiler?") keeps the turn.
    # "how much have i spent", "what did i spend on food": the sum of the sums they told you.
    # It comes before the chat-shaped readers because the thing the ask names is usually the
    # thing the chat is already on ("i spent 300 on food this month" then "how much did i spend
    # on food"), and the store answers that shape with whatever the topic holds - a cooking tip
    # about shopping with a list - instead of with the figure they gave it.
    spend_tally = spent.answer(text, memory) or spent.answer(folded, memory)
    if spend_tally:
        return spend_tally
    general = _general_recall(text, memory) or _general_recall(folded, memory)
    # "what does my mum eat", "is my son allergic to anything": a question about someone the user
    # told us about is answered from that person's own fact, whether or not the chat is still on
    # them, so it comes before the reading of "about this chat".
    # Their own diet is not a question about anyone else: "what's my diet" beside a diet kept
    # for their mum is still about them.
    asks_about_someone = _asks_about_someone(low, text, memory)
    if asks_about_someone:
        # The fact said before the question is context for it, so the question is what the store
        # answers - but only where the store would have answered the line as it stands. On "my
        # wife is allergic to shellfish, can she eat prawns" the answer modules say why prawns
        # are out, and the store's own reply is the thin receipt ("nothing with shellfish in it
        # - that's all I have on food for her"), so a line the store would have left alone is
        # left alone after the split too.
        told = None
        if _other_person_reply(memory, low):
            told = _other_person_reply(memory, _the_ask_after_a_statement(low, memory))
        # A miss is not a denial: when the line brings a fact with it ("is my son allergic to
        # nuts? he had a rash") the store holding nothing about the son is not the answer, and
        # the kitchen entry that can use the nuts gets the turn. What counts as the ask's own
        # words is the ask, so the telling is what is read for it.
        telling = _after_the_yes_no_frame(text) if isinstance(text, str) else ""
        if told and not (NO_RECORD.search(told) and telling
                         and _says_more_than_the_ask(telling)):
            return told
    # The line points at someone the chat never named: "she is 5 next month" then "how old is
    # she". The store keeps facts about a person, and an age about nobody is not one, so the age
    # is read back off the line that gave it, as long as the pronoun is the same one. A person
    # the chat did name, or pointed at with a relation in play ("my brother", then "how old is
    # he"), keeps the answer the store already has.
    who_asked = _named_person(low, memory)
    if not who_asked and re.search(r"\b(?:she|her|he|him)\b", low):
        who_asked = _person_from_pronoun(low, memory)
    if not who_asked and AGE_ASK.search(low):
        pointed = _a_pronoun_age(memory, low)
        if pointed:
            return pointed
    # "how old is my son", "how old are the kids": the number was given with the person, so this
    # is memory rather than a fact about the world, and it is answered before anything guesses.
    aged = _ages_reply(memory, low, folded)
    if aged:
        return aged
    # What is in their own kitchen is not a fact about the world and not one they have told us,
    # so the one thing the store can say is that it cannot see it. The places are a closed list:
    # "what have i got in the diary" is the ask about what is coming up and keeps its answer.
    place = _their_place(low)
    if place:
        return pick(["I can\u2019t see inside your " + place + ", so tell me what\u2019s in there and "
                     "I\u2019ll tell you what it will make",
                     "I\u2019ve no way of knowing what\u2019s in your " + place + ": say what\u2019s in "
                     "it and I\u2019ll find you something to cook",
                     "Nothing in your " + place + " I can see from here. Tell me what\u2019s in it and "
                     "I\u2019ll work something out"], memory).rstrip(".") + "."
    # "whats my sisters name" is the same kind of ask as "how old is my son": the name was given
    # with the person, so the store answers it, and without this it fell to the search hedge.
    counted = _kids_reply(memory, low)
    if counted:
        return counted
    called = _a_relations_name_reply(memory, low, text)
    if called:
        return called
    # "what car do i drive", "what phone have i got": the make they gave with the thing, which
    # the store keeps by the name of the thing (memory["user"]["owns"]). It runs before the
    # chat-shaped readers because "what car do i drive" is about them, not about the topic.
    owned = _a_thing_i_own_reply(memory, low)
    if owned:
        return owned
    # "what do you know about my mum", "tell me about my sister": the whole person the chat has
    # been told about, which the store holds, rather than the search hedge it used to fall to.
    about_person = _about_a_person_reply(memory, low, text)
    if about_person:
        return about_person
    # "whos meg" names the person by the name the chat was given, so it is the same kind of ask
    # read the other way round: the name is the subject and the relation is the answer.
    whom = _who_is_the_name_reply(memory, low)
    if whom:
        return whom
    # "and where does she live" and "where does jane live" are the same ask with the person
    # left to the pronoun or to the name: the chat has said where she lives, so it is answered
    # from the chat rather than left to the search hedge.
    if (_asked_person(memory, low)
            and not (PLACE_ADVICE.search(low) and not PLACE_RECALLED.search(low))):
        return _places_reply(memory, low)
    # "my son isnt" after a limit was given is that limit refused for him, and it is answered as
    # the answer it is rather than as a line about nothing.
    refused = _not_the_same_reply(memory, low)
    if refused:
        return refused
    if not _about_this_chat(text, memory) and not _a_why_line_they_have_answered(text, memory):
        # A question about them that the chat-shaped readers do not claim ("do i drive") is still
        # answered from their own line, and left to the ordinary reply when they never said it.
        # A why-line goes with it - it is about the world, and the store only keeps what they
        # said - unless the store holds the subject it names, where what they said *is* the
        # answer ("my dog is called rex" then "why do we have pets").
        return general or _about_what_they_said(text, memory)
    if re.search(r"\b(?:what|which)\b.*\bmy name\b|\bwho am i\b|^my name$|\bwhat my name\b|"
                 r"\b(?:know|remember) my name\b|\bwhat did (?:i|u|you) (?:say|tell me) my name was\b",
                 low):
        return _name_reply(memory, low)
    if re.search(r"\bmy job\b|\bmy work\b|\bwhat do i do\b|\bwhere do i work\b|"
                 r"\bwhat do i work as\b|\bwhat i (?:do|did)\b|\bfor a living\b", low) \
            or (WHERE_WORK.search(low) and not _doing_again(text, memory)):
        # "what was i saying about my job" asks for the line, not for the role: they can say
        # plenty about a job they never named, and the line said back is the answer to it.
        if _doing_again(text, memory) or (SAID_ABOUT.search(low) and _names_its_thing(low)):
            asked = _topic_reply(memory, low)
            # The store keeps the job, so a callback that found no line about it must not say
            # there is none: the fact it keeps is the answer, and it is said below.
            if asked and not _a_denial(asked):
                return asked
        # "and what do i do there", "who do i work with": a part of the job they never described,
        # so the job said back is the same sentence as the turn before it and answers nothing.
        part = _a_part_of_the_job_never_said(memory, low)
        if part:
            return part
        return _job_reply(memory, where=bool(WHERE_WORK.search(low)))
    # "where was i going with this" is a lost thread, not a place: the place ask is the one
    # that stands on its own.
    # "do you remember what I do?" asks for the job in the store's own words: the frame points
    # back at the fact, and the line ends there ("what i do about that boiler" is a request).
    if re.search(r"\b(?:remember|recall|know)\b[^.]{0,18}\bwhat i (?:do|did)\b\W*$", low):
        return _job_reply(memory)
    if (PLACES_ASK.search(low) and SELF_WORD.search(low)
            and not (PLACE_ADVICE.search(low) and not PLACE_RECALLED.search(low))):
        return _places_reply(memory, low)
    # "what cant i have" and "what did i say i don't eat" name the limit itself: the answer is
    # the limit they gave, not the answer before this one read out again ("It's what I said a
    # moment ago: Plenty: meat, fish..."), and not the line quoted back. It goes before the fact
    # questions because a limit ask is one of them and would otherwise be answered with the fact.
    if recall.ask(text) == "limit":
        limit = _limit_reply(memory, low)
        if limit:
            return limit
    # A how-to in front of "my diet" is advice, not a recall: "how do i get more veg in my
    # diet" wants an idea, and this branch used to answer that it had not been told about the
    # diet. The fact questions keep DIET_ASK.
    if (_asks_for_a_fact(low, text, memory) or (DIET_ASK.search(low) and not DIET_HOW_TO.search(low))
            or _a_count_ask(low) is not None):
        return _fact_reply(memory, low)
    if PLAN_MINE.search(low):
        return _plans_reply(memory, low)
    if FIRST_ASK.search(low):
        return _first_reply(memory)
    if _repeat_ask(text, folded):
        return _repeat_reply(memory, text)
    if SAID_ASK.search(low):
        return _said_reply(memory)
    # "remind me what i told you" with nothing named is the whole chat, not one line of it.
    if re.search(r"^what i (?:told|said)(?: you)?$|^what have i (?:told|said)(?: you)?$", low):
        # Only when the line is the ask: see the anchor note in `_recall_shapes`.
        return _summary_reply(memory)
    # "what did i tell you about me" asks for the whole picture, not one line of it: the same
    # ask in other words ("what do you know about me") is already answered as a summary, so the
    # quote-their-last-line branch below must not take it. A named thing keeps the turn:
    # "what did i say about the boiler" is still about the boiler.
    if re.search(r"\babout me\b|\bof me\b", low):
        return _summary_reply(memory)
    # The ask names the kind of detail, and the line their own words find is the answer.
    kind_said = _an_open_attribute_ask(low, memory)
    if kind_said:
        return kind_said
    if WHAT_I_SAID.search(low) or re.search(
            r"\bwhat was it i said\b|^what i (?:said|told you|mentioned)\b|"
            # "we" only when it names the thing: "remind me what we said about the boiler" is that
            # one recall, and a bare "remind me what we said" is the recap of the whole chat, which
            # `_summary_reply` answers better ("We were on Edinburgh - you asked ...").
            r"^what we (?:said|told you|mentioned)\s+(?:about|on|regarding)\b|"
            r"^anything i (?:said|told you|mentioned)\b|"
            # "i cant remember what i said" is the reminder in the speaker's own words,
            # and the forgetting in front of it is what makes it an ask.
            r"\bi (?:cant|cannot|can not|dont|do not) (?:really |quite )?remember "
            r"what i (?:said|told you|mentioned)\b|"
            r"\b(?:do|can|could|did) (?:you|u) remember what i\b", low) \
            or THING_AGAIN.match(low) or reminded.the_thing(text, memory) \
            or _which_thing_was_it(low, memory) or _an_attribute_they_gave(low):
        said = _recall_reply(memory, low, text)
        if said:
            return said
        # A place in the ask that the chat has never been on is what the ask is about: "what did
        # i say it was like in Lisbon" asks about Lisbon, and recapping the budget answers a
        # question they did not ask. The thing itself is answered by another module.
        # Only when there is something of theirs for the ask to be about: with nothing said
        # before it the store's own "we're still at the beginning" is the honest reply, and a
        # search hedge for a place they only just named is not.
        earlier = [line for line in last_user(memory, 4)
                   if " ".join(str(line or "").split()).lower()
                   != " ".join(str(text or "").split()).lower()]
        if earlier and _a_place_new_to_the_chat(memory, low):
            return general or _about_what_they_said(text, memory)
    if re.search(r"\bmy age\b|\bhow old am i\b|\bhow old did i say\b|"
                 r"\bhow old (?:i am|i was|we are|i(?:'m| am) gon(?:na|e) to be)\b", low):
        # "how old did i say she was" asks about her, and the asker's own age is not the answer
        # to it: with nothing on record for her this line read "I don't know it - you haven't
        # said", which is the person's own age being denied to a question about somebody else.
        # A person the chat knows is answered above, by their own age.
        theirs = re.search(r"\b(?:she|her)\b|\b(?:he|him)\b", low)
        if theirs and not _person_from_pronoun(low, memory):
            return ("You haven't told me how old she is." if re.search(r"\b(?:she|her)\b", low)
                    else "You haven't told me how old he is.")
        return _age_reply(memory)
    # A part of an animal they have already described, asked about with a pronoun or the word
    # for it: "how old is he", "what did i say his age was", "what breed is he". The chat holds
    # the fact, so it is the answer; left to the general readers this was the topic shrug
    # ("Still on the kids: you asked how often you should walk him"), which names the wrong
    # thing and answers a question nobody asked.
    pet = _pet_part_reply(memory, low)
    if pet:
        return pet

    if ASKED_ALL.search(low):
        return _asked_reply(memory)
    if not _about_the_bot_here(memory) and (
            THE_CHAT_ASK.search(low) or TOPIC_ASK.search(low)
            or ACTIVITY_ASK.search(low) or TALKED_ABOUT.search(low)):
        # "what am i planning" is a question about the plans we hold when we hold one; the line
        # they said it in is the fallback.
        if ACTIVITY_ASK.search(low) and (PLAN_WORDS.search(low) or _plan_was_corrected(memory)
                                         or (UP_TO_ASK.search(low)
                                             and _the_line_before_was_a_plan(memory))):
            # "what am i up to?" after "sorry, i meant porto, not lisbon" is about the plan as it
            # stands now: the line they said before the correction names the city they took back.
            asked = _plans_reply(memory, low)
            if asked:
                return asked
            # Nothing is coming up, so the plans reply has nothing to say: the ask is still a
            # plans ask ("what was i planning to do about it?") and the "nothing yet" line below
            # is the answer, not a hedge. Falling out of this branch keeps that.
        else:
            asked = _topic_reply(memory, low, again=bool(ASKING_AGAIN.search(folded)))
            if asked:
                return asked
    if _summary_ask(low):
        # "summarise our chat" asks about the conversation the same way "recap" and "what did we
        # talk about" do, so it gets the same answer: the thing we were on, not the whole of the
        # person. `_summary_reply` stays for "what do you know about me".
        return _topic_reply(memory, low)
    if re.search(r"\bwhat have i told you\b|\bwhat do you (?:know|remember) about me\b|"
                 r"\babout me\b|^what i (?:told|said)(?: you)?$|^what have i (?:told|said)(?: you)?$",
                 low):
        return _summary_reply(memory)
    if PLAN_ASKS.search(low):
        asked = _plans_reply(memory, low)
        if asked:
            return asked
    if "remember" in low and "yesterday" in low:
        return _topic_reply(memory, low)
    return general or _about_what_they_said(text, memory)


def _general_recall(text, memory):
    """A recall ask in any words (bot/memory/recall.py): "what was my name", "do you remember
    my budget?", "where do I live". The words people use for the same ask are endless, so the
    ask is read by its shape - the user plus one thing they told you - and answered with the
    reply the store already gives for that fact. Anything else is a real request: None.
    """
    low = " ".join(text.lower().split())
    # "what should i avoid": advice about the world when the store knows nothing, and the
    # allergy they told you when it does. recall.ask refuses the shape as advice on purpose (it
    # cannot see the store), so the fact answers it here, and only when the fact is what they are
    # asking about - a chat about a holiday is still a question about the sun and the roads.
    if AVOID_ADVICE.search(text) and user(memory).get("allergies") \
            and _the_allergy_is_what_is_asked(text, memory):
        # "Nothing with nuts in it" answers "what should I avoid"; the bare "you told me you're
        # allergic to nuts" repeats the fact at them and leaves the ask unanswered.
        return _limit_reply(memory, low) or _fact_reply(memory, low, "allergy")
    # "i work as a nurse" then "what do i do": the line names nothing, so on its own it is a
    # request for advice, and the knowledge base answered it with the entryways into nursing. What
    # the person means is the job they have just told you. Only right after they said it, because
    # a turn later "what do i do" is about whatever the chat has moved on to, and only when the
    # store holds a job for it to be about.
    if BARE_WHAT_I_DO.match(low) and user(memory).get("job") and _the_job_was_just_said(memory):
        return _job_reply(memory)
    # "what was i saying about my job" asks for the line they said, not for the job as a fact:
    # they can say plenty about the job ("i hate it") without ever naming what they do, and the
    # line said back is the answer. A plain "what is my job" is still the fact.
    # "how much have i spent", "what did i spend on food": the sum is kept from the lines they
    # typed, and the store read none of those lines as a budget, so the ask was answered with a
    # search hedge or a "you haven't told me a budget" that is not what they asked.
    spent_reply = spent.answer(text, memory)
    if spent_reply:
        return spent_reply
    # "how much have i got left", "can i afford a takeaway": the same sums, against the money
    # they said they had. Answered here for the same reason: it is a sum over what they typed,
    # and the answers module had the cheap week or a hedge for it.
    left_reply = spent.what_is_left(text, memory)
    if left_reply:
        return left_reply
    key = recall.ask(text)
    if not key:
        return None
    if SAID_ABOUT.search(low) and _names_its_thing(low) and not _the_fact_is_kept(key, memory):
        # "what was i saying about my job" asks for the line they said, not for the job as a
        # fact: they can say plenty about a job they never named ("i hate it"), and the store
        # holding no job does not mean the chat said nothing about it. With the fact kept, the
        # fact is the answer, and the dispatch below gives it.
        return None
    if key == "name":
        return _name_reply(memory, low)
    if key == "job":
        # "who do i work with", "and what do i do there": a part of the job they never described,
        # so the job said back answers nothing and repeats the turn before it.
        part = _a_part_of_the_job_never_said(memory, low)
        if part:
            return part
        # A where-ask reaches the job through the fact reader too ("do you know where i work"),
        # and the place is the answer when it is kept.
        return _job_reply(memory, where=bool(WHERE_WORK.search(low)))
    if key == "city":
        return _places_reply(memory, low)
    if key in ("birthday", "weight", "height"):
        return _fact_reply(memory, low, key)
    if key == "diet":
        return _diet_reply(memory, low)
    if key in ("allergy", "budget", "pet", "car"):
        return _fact_reply(memory, low, key)
    if key == "limit":
        return _limit_reply(memory, low)
    if key == "me":
        return _summary_reply(memory)
    return None


def _a_relations_name_reply(memory, low, text=""):
    """What someone in the family is called: "Your sister is called Meg."

    The name is filed with the person ("my sister is called meg", "my brother dan"), so the ask
    is answered from what the chat was told. A person the chat knows of with no name gets the
    honest "you haven't told me" rather than a search hedge: the store does know the sister.
    """
    if not isinstance(low, str):
        return None
    match = OTHER_NAME_ASK.search(low)
    who = ""
    if match:
        groups = ("who1", "who2", "who3", "who4", "who5", "who6", "who7", "who8", "who9",
                  "who10", "who11")
        who = next((match.group(group) for group in groups
                    if match.groupdict().get(group)), "")
        who = (who or "").lower()
        # "my babys name", "my toddlers name": the ask "my baby is called mia" said back. A word
        # that names one person with no relation after it ("baby", "toddler") is somebody the
        # store files, so the ask can name them, and the "s" on the end is the possessive.
        if (who.endswith("s") and (who[:-1] in extract.KIN_WORDS
                                   or who[:-1] in extract.ALONE_PERSON)):
            who = who[:-1]
        who = _with_an_in_law(who, low)
        group = _the_group(who)
        if group:
            if who in A_ONE_PERSON_WORD:
                # "what is my child called" names one person with a word that covers several,
                # which is the ask "what is my daughter called" after the same line: the store
                # holds both names and cannot say which one is meant, so it asks. Reading it as
                # the group denied the pair it had just been given, or picked one of the names.
                narrowed = _which_one_of_them(memory, who)
                if narrowed:
                    return narrowed
            # "what are my children called" asks about the several people in one word: the answer
            # is every name the store holds for that group, or the honest line about the names it
            # was never given - never the search hedge, one line after it filed both children.
            together = _what_the_group_is_called(group, memory)
            if together:
                return together
            # A line that named the group is one the store failed to file, and telling the person
            # they never told us would deny what they just said: "my kids are called tom and sam"
            # keeps the answer it had rather than being called back as a name the chat lacks.
            if _the_group_was_said(who, memory):
                return None
            # Nothing was ever said about these people, and the ask is about the asker's own
            # family: the honest line names the group, where the hedge said the bot would look
            # it up ("That's beyond what I know well ... a search will turn up better sources"
            # in answer to "what are my parents called"). The store knows what it holds.
            return _vary(["You haven't told me what your " + _the_group_word(who) + " are called.",
                          "I don't have any names for your " + _the_group_word(who) + " yet.",
                          "You've not said what your " + _the_group_word(who)
                          + " are called."], memory)
        if (who not in extract.KIN_WORDS and who not in extract.ALONE_PERSON
                and not extract.an_in_law(who)):
            return None
        # A wide kin word ("stepmum", "grandson") is only a person the chat knows of once it has
        # heard of them: an empty chat is not told "you haven't told me your stepmum's name" about
        # somebody nobody mentioned.
        if (who not in extract.RELATIONS and not extract.an_in_law(who)
                and not _a_person_in_the_store(memory, who)):
            return None
    else:
        point = PRONOUN_NAME_ASK.search(low)
        if not point:
            return None
        pronoun = next((point.group(group) for group in
                        ("pos", "sub", "obj", "pos2", "sub2", "obj2", "pos3", "pos4")
                        if point.groupdict().get(group)), "")
        if pronoun in ("their", "they", "them"):
            # "what are their names" about the children the chat has just named: the pronoun is
            # the two of them, so the answer is both names rather than the last one filed.
            together = _everyone_they_mean(memory)
            if together:
                return together
        who = _who_the_pronoun_means(low, memory, pronoun).lower()
        if not who:
            # The pronoun points at the one animal the chat has named: "i have a cat called max" /
            # "hes 4 months" / "what did i say his name was" was told it had no name for him,
            # because the age said about him a turn earlier is not a person the pronount fits.
            named_pet = _the_one_animal_with_a_name(memory)
            if named_pet:
                return named_pet
            return None
    told = others(memory)
    mine = [entry for entry in told if str(entry.get("who") or "").lower() == who]
    named = [entry for entry in mine if entry.get("name")]
    if named:
        name = _called(named[-1].get("name"))
        return _vary(["Your " + who + " is called " + name + ".",
                      name + " \u2014 your " + who + ", you told me.",
                      "You said your " + who + " is called " + name + "."], memory)
    # A pair of names said for two people ("my mum and dad are dave and sue") does not say which
    # name is whose, so the answer says what was said and asks for the one thing that settles it.
    # Guessing would file a name about their mother they never gave; denying the line would throw
    # away something they did say.
    for entry in told:
        pair = [word.strip() for word in str(entry.get("who") or "").lower().split(" and ")]
        pair_names = [str(one) for one in entry.get("names") or []]
        if ((len(pair) > 1 and who in pair) or _canon_relation(who) in _relations_of(
                entry.get("who"))) and len(pair_names) > 1:
            return ("You told me your " + str(entry["who"]) + " are "
                    + _a_list_of_names(pair_names) + " - which one is your " + who + "?")
    in_law_of_the_same = [entry for entry in told
                          if extract.an_in_law(entry.get("who"))
                          and str(entry.get("who") or "").lower().startswith(who + " in law")]
    if mine or in_law_of_the_same or who in [str(person).lower() for person in
                                             (user(memory).get("people") or [])]:
        # The person is known to the chat even with no name filed for them ("my sister had a
        # baby"), so the honest line is about the name, not about the sister. A brother in law
        # is not the brother: the chat has heard of the family, and the ask about the brother is
        # one it has nothing for - handing back the in-law's name answered for the wrong person.
        return "You haven't told me your " + who + "'s name."
    return None


def _the_fixed_fact(memory):
    """The fact a correction just fixed, as the store keeps it, or None.

    A recap quoted the correcting line itself ("you said actually make that 800") because that
    is what the last line was, while the store had already applied it. What the chat is on is
    the corrected fact, so that is what the recap says.
    """
    fixed = memory.get("correction") if isinstance(memory, dict) else None
    if not isinstance(fixed, dict):
        return None
    key = str(fixed.get("key") or "").strip()
    value = str(fixed.get("value") or "").strip()
    said = str(fixed.get("said") or "").strip()
    if not key or not value:
        return None
    if said and last_user(memory).strip().lower() != said.lower():
        return None  # an older correction: the line after it is the one we were on
    sentence = _fact_reply(memory, " ".join(_slot_words(key, memory).split()), key=key)
    sentence = str(sentence or "").strip()
    if not sentence.startswith(("Your ", "You ")):
        return None
    return sentence[:1].lower() + sentence[1:].rstrip(".")


def _topic_reply(memory, low, again=False):
    """Where we were, said back in a sentence: the thing, and what was asked about it.

    The line is never quoted: "we were on this: \"...\"" makes the person read their own
    words twice. `thread.restate` puts the last ask in the second person and fits the
    grammar, and a turn that only asks about the chat is not the thing we were on.

    `again` says the person asked for a thing they know they said ("what am i making again").
    Their own word for it comes off the line before it reaches here, so it is read from the
    line as typed and passed in.
    """
    record = current(memory)
    real = _last_real(memory)
    if real:
        record = {"text": real}
    last = last_user(memory)
    # The thing the line names decides which line is said back: "what was i saying about the
    # deposit" after a rent line is about the deposit, not about the rent. Where the thing is
    # not in any line they gave, the last line is still the honest answer to "what were we on".
    on_that_line = _the_line_named(memory, low)
    said_again = (_the_fixed_fact(memory)
                  or (thread.restate(on_that_line) if on_that_line else "")
                  or thread.last_said(memory, _about_this_chat))
    if said_again and len(said_again.split()) < 2:
        said_again = None  # "and again" is not a thing the chat was on
    if "yesterday" in low:
        said = (" In this one, you last said " + said_again + "." if said_again else "")
        return "I don't keep yesterday's chat, sorry — each conversation starts fresh for me." + said
    if _names_its_thing(low):
        # "what was i saying about pasta earlier": the thing is named, so the chat can have moved
        # on since and the last turn is not the answer to it; the line that names the thing is.
        # Nothing found about a thing the store keeps as a fact ("about my city" beside "i live
        # in leeds") is not a thing to deny, so the ordinary paths speak for it instead.
        by_name = _recall_reply(memory, low, spoken=True)
        if by_name and not _a_denial(by_name):
            return by_name
        # A miss is never a denial. The chat may have said the thing in other words - "about my
        # hours" beside "i work nights", "about music" beside "i like jazz" - and telling the
        # person the chat has nothing about it is a claim about the conversation that is false.
        # So a miss falls through to the answers this line got before the reader existed.
    named = NAMED_ACTIVITY.search(low or "")
    carried = _activity_line(memory) if ACTIVITY_ASK.search(low or "") else ""
    if not carried and named and again:
        carried = _the_making_line_they_said(memory)
    if not carried and named:
        # "what was i cooking?" after a chat about a dishwasher asks for the cooking line; the
        # topic we were on is a different thing, and naming it does not answer the ask.
        return None
    if carried:
        said_plan = _recap(carried) or ("You said: \"" + _trim(carried) + "\"")
        said_plan = said_plan.rstrip(".") + "."
        return _vary([said_plan + " Want to carry on with it?",
                      said_plan + " Where did you get to with it?",
                      said_plan], memory)
    thing = thread.about(memory, _about_this_chat)
    if not _a_thing(thing):
        thing = None
    ask = "" if on_that_line else thread.last_ask(
        memory, _about_this_chat,
        not_before=thread.topic_index(memory, _about_this_chat))
    # The subject and the ask are different halves of the same sentence, and neither quotes the
    # line: "We were on Edinburgh - you asked how many days I would give it". A recap that held
    # the subject back because the last line happened to name it too lost the topic and said
    # only "You asked how many days I would give it", which is half an answer to "remind me what
    # we've covered".
    #
    # A description the store had to give an article to ("the pressure", out of "my boiler keeps
    # losing pressure") is the one subject not worth naming again when the line already says it:
    # the reason we were on it is that it is the person's boiler, and their own words say so. A
    # line that is still on the screen names its own subject, so it is said as it is and the
    # thing cut from its words is left out.
    if thing and ask and not (_a_description(thing) and (
            _says_the_thing(said_again, thing) or _says_the_thing(ask, thing))):
        return _vary(["We were on " + thing + " — you asked " + ask + ". Want to carry on?",
                      "Still on " + thing + ": you asked " + ask + ".",
                      "The last thing we got into was " + thing + ", and you asked " + ask + "."],
                     memory)
    if ask and said_again:
        return _vary(["You said " + said_again + ". You asked " + ask + ". Want to carry on?",
                      said_again[:1].upper() + said_again[1:] + " - and you asked " + ask
                      + ". Want to carry on?"], memory)
    if ask:
        return _vary(["You asked " + ask + ". Want to carry on?",
                      "You were asking " + ask + "."], memory)
    if said_again:
        return _vary(["You said " + said_again + ". Want to carry on?",
                      "You last said " + said_again + ".",
                      "You'd told me " + said_again + "."], memory)
    if thing:
        return _vary(["We were on " + thing + ".", "Still " + thing + "."], memory)
    if record and not thread.thin(record["text"]) and thread.carries_subject(record["text"]):
        plain = thread.restate(record["text"])
        if plain and _a_thing(plain):
            return "We were on " + plain + "."
    asked_of_me = _the_last_ask_about_the_bot(memory)
    if asked_of_me:
        return _vary(["You asked " + asked_of_me + " - that is all we have been into so far. "
                      "What else is on your mind?",
                      "So far you have asked " + asked_of_me + ". Tell me something of your own "
                      "and I will keep it.",
                      "You asked " + asked_of_me + ". That is about all so far - what else are "
                      "you wondering about?"], memory)
    # Nothing but "hi", "ok", "lol" so far: there is no subject yet, and naming one would be
    # a lie. `last` is deliberately not used here — a thin line is not something to carry on.
    return _vary(NOTHING_STARTED, memory)


# The words a person puts between the frame and the verb of it: "i dont really want to talk about
# it", "id honestly rather not say", "i dont actually need to go into it". Only the intensifier is
# allowed and only one, so the frame is still the frame around it.
INTENSIFIER = r"(?:really|honestly|actually|even|ever|particularly|especially|much)"


CLOSE_SUBJECT = re.compile(
    r"\bi (?:just )?(?:want|wanna|would rather|'?d rather|need) to "
    r"(?:forget|drop|leave|skip) (?:it|that|this|all of it|all that)\b|"
    # An intensifier goes where the person puts it: "i dont REALLY want to talk about it" is the
    # same closing as "i dont want to talk about it", and it was read as an ask about how to make
    # conversation. It never changes which frame the line is in, so it sits inside every one.
    r"\bi(?:'?d|\s+would)?\s+(?:" + INTENSIFIER + r"\s+)?rather\s+not\s+"
    r"(?:say|talk about it|go into it|get into it)\b|"
    r"\bi\s+(?:do\s+not|don'?t|dont)\s+(?:" + INTENSIFIER + r"\s+)?"
    r"(?:want|wanna|need)\s+(?:" + INTENSIFIER + r"\s+)?to\s+"
    # "go into it" and "get into it" are how people say this as often as "talk about it", and both
    # were answered with a card about something else.
    r"(?:(?:talk|think|speak|hear)\s+about\s+|(?:go|get)\s+into\s+)(?:it|that|this)\b|"
    r"\bi\s+(?:can'?t|cannot|couldn'?t|won'?t|will not)\s+"
    r"(?:go|get)\s+into\s+(?:it|that|this)\b|"
    r"\b(?:can|could|would) (?:we|you) (?:just )?not (?:talk|speak) about (?:it|that|this)\b|"
    r"\b(?:let'?s|lets) not (?:talk|speak) about (?:it|that|this)\b|"
    r"\bnot (?:going to|gonna) talk about (?:it|that)\b|"
    r"\b(?:drop|forget) (?:it|that)\b|"
    # The shortest take-backs people type. "forget it" was answered with the close above and
    # "never mind" - the commonest of the lot - with the answer again: the tap card said the
    # whole dripping-tap answer twice, and "nvm" and "doesnt matter" did the same. The rest of
    # the line still has to be filler, so "never mind, how do i boil an egg" and "never mind the
    # dog" (a retraction of the animal, which facts.py reads) are not closings.
    r"\bnever\s*mind(?:\s+(?:that|this|it|then|now|anyway|about (?:it|that|this)))?\b|"
    r"\bnevermind(?:\s+(?:that|this|it|then|now|anyway))?\b|"
    r"\bnvm(?:\s+(?:that|this|it))?\b|"
    r"\b(?:it )?(?:does not|doesn'?t|didnt|didn'?t) matter\b|"
    r"\b(?:ignore|skip|scrap|scratch) (?:it|that|this)\b|"
    r"\bnot important\b|"
    r"\bforget (?:i|what i) (?:said|asked)\b|"
    r"\bno more (?:about|on) (?:it|that)\b")
