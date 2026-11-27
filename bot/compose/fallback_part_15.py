"""Part 15 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import random
import re

from ..memory import history, obstacle
from ..understanding import understand
from ..understanding.topics import is_a_machine_word
from . import (draft, leaving, outlook, trouble)
from .urgent import reads_as_a_story
from .badnews import (DEATH_SAID as SAID_AS_A_DEATH,
                      reads_as_pregnancy_bleeding, reads_as_sudden_loss)

from .not_knowing import (NAMES_WHERE_TO_ASK, POINTER_HEDGE, _an_ask_with_no_subject,
                          _asks_about_this_chat, _the_lead_and_the_route)
from .fallback_data import (
    A_FREE_TIME_ASK,
    ADVICE_WORDS,
    AFRAID_AFTER,
    AFTER_RESOLVED,
    ALIVE,
    ANIMALS,
    A_THING_AHEAD,
    A_THING_BOUGHT,
    A_THING_DONE,
    A_THING_GONE,
    A_THING_ON,
    A_THING_SEEN_TO,
    ABUSE_AFTER,
    BABY_WHO,
    BODY_PARTS,
    BOUGHT_VERB,
    BURN_AFTER,
    BURN_BLISTER,
    BUYING_WORDS,
    CARE_AFTER,
    CARE_AFTER_ANIMAL,
    CARE_AFTER_ANIMAL_STILL,
    CARE_AFTER_STILL,
    CARE_BETTER,
    CARE_HERE,
    CARE_ROUTE_BACK,
    CARE_SEEN,
    CARE_SEEN_ANIMAL,
    CARE_THREAD,
    CARE_VISIT,
    CARE_VISIT_WARD,
    CARE_WORDS,
    CHILD_AT_HOME,
    CHILD_FAINT,
    CHILD_FAINT_ANSWER,
    COMPLAINT_WORDS,
    COMPLAIN_WHO,
    CRISIS_AFTER,
    CRISIS_AFTER_THEM,
    CRISIS_BETTER,
    CRISIS_BETTER_THEM,
    CRISIS_WORDS,
    DENTIST_WHO,
    DEVICE_WHO,
    DITHER_ABOUT_A_PERSON,
    DITHER_OPEN_LINES,
    EMERGENCY_AFTER,
    EMERGENCY_ANSWER,
    EMERGENCY_BETTER,
    EMERGENCY_BETTER_THEM,
    EMERGENCY_NOT_WORKED,
    EMERGENCY_WORDS,
    FAINT_COMING_ANSWER,
    FALLBACK_MODULE,
    FAVOURITE_GENERAL,
    FAVOURITE_WORDS,
    FILLING_FOODS,
    FILLING_WORDS,
    FLOPPY_WAKE,
    FORECAST_AFTER_SAFETY,
    FUEL_WORDS,
    FUME_WORDS,
    GADGET_WORDS,
    GAS_ANSWER,
    GAS_WORDS,
    GIFT_WORDS,
    GONE_VERB,
    GREETING_AFTER,
    HAZARD_AFTER,
    HEALTH_WHO,
    HEALTH_WORDS,
    HELLO_STILL_THERE,
    HELLO_WITH_YOU,
    HELPLINE_NOT_AN_AMBULANCE,
    HOLD_AFTER,
    LANGUAGE_FLUENCY,
    LAUGHING_WORDS,
    MEDS_WORDS,
    MESS_PLACES,
    MOUTH_WORDS,
    MOVE_ON_AFTER,
    MY_PICK,
    MY_PICK_ASK,
    MY_PICK_NOTE,
    NETWORK_WORDS,
    NOT_CHOSEN,
    OPINION_ASKS,
    PASSED_OUT_ANSWER,
    PASSWORD_TROUBLE,
    PAUSE,
    PEST_WHO,
    PETROL_WORDS,
    REACTION_WORDS,
    REFUSED_REPLIES,
    RESOLVED_AFTER,
    THE_CALL_STANDS_ANYWAY,
    RESOLVED_AFTER_THEM,
    SAFETY_WORDS,
    SCHOOL_TROUBLE,
    SCHOOL_WHO,
    SCHOOL_WORDS,
    SEEN_TO_VERB,
    SELF_GROUP,
    SICKNESS,
    STILL_HERE_AFTER,
    SYMPTOM_WORDS,
    TASTES,
    TASTE_GENERAL,
    TENANT_WHO,
    THANKS_AFTER,
    THANKS_WORDS,
    THE_CALL_STANDS,
    THRESHOLD_CROSSED,
    THREAD,
    THREAD_TURNS,
    TIPS_AHEAD,
    TIPS_THING,
    TIRED,
    TRADER_WORDS,
    TRADES_WHO,
    TRADE_OFF_LEAN,
    TRIED_NO_CHANGE_ELSEWHERE,
    TRIED_WORSE_ELSEWHERE,
    TROUBLE_CUES,
    UNKNOWN_WHO,
    VET_WHO,
    WHERE_SOMETHING_WRONG,
    WHO_TO_ASK,
    JOINT_WORDS,
    _ASKS_ABOUT_THE_JOINT,
    _CHOOSING_BETWEEN_TWO,
    WHY_AFTER_TASTE,
    WILD_BIRDS,
    WITH_YOU_AFTER,
    WORK_ABOUT,
    WORK_WHO,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    PASSED_OUT,
    PASSING_OUT_A_THING,
)
from .fallback_part_01 import (
    A_STRETCH_OF_TIME, _has, _somebody_to_visit,
)
from .fallback_part_02 import (
    BLACKED_OUT_A_THING, CANT_WAKE, CHOKE_BODY, CHOKE_MACHINE, CHOKE_ON_A_WORD, FAINT_COMING,
    FEED_TAIL, OVERDOSE_A_PILL, OVERDOSE_DRUG, OVERDOSE_FOOD, OVERDOSE_OF_A_TREAT, ROUTINE_WAKE,
    UNRESPONSIVE_TAIL, _the_thing_is_choking, _the_thread_is_an_animal,
)
from .fallback_part_03 import (
    _a_lost_ask, _a_start_ask,
)
from .fallback_part_06 import (
    _thing_done_scan, DISLIKE_ASKS, DISLIKE_HAS_TWO_HALVES, DISLIKE_TAIL, DISLIKE_TOO_LONG,
    DISLIKE_WITHOUT_AN_I, NOT_A_THING_ASKED, DOABLE_REPLIES, _reads_as_a_judgement, THING_SORTED,
    OUR_HEAVY_TELL,
)
from .fallback_part_07 import (
    LEAN_ASK, PICK_ADVICE, PICK_BACK, _choice_advice, _choice_pool, _is_a_choice, _capital,
    ALREADY_RANG, A_HELPLINE, BURN_ASK, BURN_BLISTER_LINE, BURN_ON_IT, BURN_THING, BURN_WORD,
    CARE_SEEN_ASKS, CARE_WORDS, MEDICAL_PLACE, MOVE_ON, NEEDS_SEEN, NOT_A_VISIT, POP_A_BARE_IT,
    RESOLVED, STILL_GOING, TRIED_NO_CHANGE, TRIED_WORSE, VISIT_ASK, _asks_about_the_advice,
    _feels_better, _no_relief, _someone_is_a_patient, _someone_is_arriving, ASKS_WHY, HYPOTHETICAL,
    OWN_NO, REFUSED, REFUSED_FAMILY, REFUSED_NOT, REFUSED_NO_OBJECT, REFUSED_PARTY,
)
from .fallback_part_08 import (
    the_pool_for_a_lost_ask, _a_bare_pick, _a_lean_only_line, _a_trade_off, _in_a_care_thread,
    _offered, _is_about_the_persons_own_life, _reads_as_why, _asks_how_are_you,
)
from .fallback_part_09 import (
    _the_person_they_are_stuck_on, _yours, FAVOURITE_WORDS, OWN_FAVOURITE, OWN_FAVOURITE_LINES,
    _their_favourite_back, _their_favourite_said,
)
from .fallback_part_10 import (
    _is_a_hedge, HEALTH_STEMS, NOT_WHAT_TO_DO_ABOUT, WHAT_TO_DO_ABOUT, WHAT_TO_DO_ABOUT_FRAMES,
    _the_thing_alone, ABOUT_THE_BOT_BORN, ABOUT_THE_BOT_CLOCK, ABOUT_THE_BOT_NAMED,
    ABOUT_THE_BOT_TALK, BOT_BORN_LINES, BOT_FEELING_NAMED_LINES, BOT_TALK_CLOCK_LINES,
    BOT_TALK_LIMIT_LINES, TIPS_SOON, _in_a_pool,
)
from .fallback_part_11 import (
    _blackout_words, _names, _tips_subject, BUYING_WORDS, GIFT_WORDS, MEDS_WORDS, NETWORK_WORDS,
    _ASKS_ARITHMETIC, _ASKS_DEFINITION, _ASKS_DIY, _ASKS_WHERE, _SCHEDULING, _a_grown_up_asks,
    _reads_as_question,
)
from .fallback_part_12 import (
    A_BACK_AGAIN, THE_THING_ITSELF_LOOKS_FINE, _ASKS_TO_LEAVE, _THE_WAY_OUT, _about_somebody_else,
    _burn_line, _goes_back_for, _keeps_thread, _reads_as_fear, _the_hazard_is_gas, _wrote_for_them,
    _an_answer_above,
)
from .fallback_part_13 import (
    _a_newer_answer_asked_them_to_call, _already_rang, _hold_pool, _is_a_hazard, _raises_the_stakes,
    _releasable, _short_ack, _somebody_is_coming, _thanks_carries_emergency,
    _the_answer_asked_them_to_call, _the_answer_was_an_abuse_card, _the_route_the_answer_named,
    _the_safety_cards, _the_threshold_was_crossed, _thread_was_closed, _grief_thread,
)
from .fallback_part_14 import (
    the_advice, THE_THREAD_KEPT, _a_report_on_the_advice, THANKS_GOOD_AGAIN, THANKS_WENT_BADLY,
    _thanks_then_said, _a_chat_behind_it, reads_as_a_return, reads_as_pause,
    _the_next_move_after_the_advice, _the_outcome_of_the_advice,
    _a_thread_about_how_somebody_treats_them, _in_a_loss_thread,
    _the_answer_above_already_says_what_to_do,
)


def _a_bad_line_above(memory):
    """True when the line before this one was a bad one by its own words.

    "its been rough and i want to cry" names no person and no thing, so neither reading above
    finds it, and the open pool's "say what you'd want if nothing was in the way" is a strange
    thing to say to somebody who has just said that. The mood of the line is the reading that
    does find it.
    """
    if not isinstance(memory, dict):
        return False
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return False
    last = str(turns[-1].get("user") or "")
    if not last.strip():
        return False
    return _mood(_words(last), last) == "negative"


def _a_question_about_the_person(clean, memory):
    """A question about the person they are stuck on, or None when no person is named.

    Read from the last place anything else answers, because the line is only this pool's when
    nothing in the knowledge or the thread can use it: "what should i do about my knee" is still
    the knee card, and a person's death in the thread is still the grief pool's.
    """
    who = _the_person_they_are_stuck_on(clean)
    if not who:
        return None
    return _choose([line.format(who=who, Who=who[:1].upper() + who[1:])
                    for line in DITHER_ABOUT_A_PERSON], memory, clean)


def _the_stretch_of_time(clean, memory):
    """A question about the free afternoon, or None when the line is not that.

    "no idea what to do with my afternoon" is somebody with an afternoon going spare, and the two
    doors it can reach - the ask for a hand with nothing named (the search hedge) and the doubt
    with two sides (the question for a person carrying too much) - are both the wrong reply. Said
    with a day or a weekend in it, the line already reaches the pool that gives the day a shape
    before either door, so this only ever sees the afternoon.
    """
    if not A_STRETCH_OF_TIME.search(clean or ""):
        return None
    return _choose(A_FREE_TIME_ASK, memory, clean)


# The topics where a filling is something you eat. A dish in the conversation makes the next
# "what filling should i use" a kitchen question, and the topic is carried, so the line itself
# does not have to say "cake" for this to hold.
FOOD_TOPICS = frozenset(("cooking", "food-and-drink"))


def the_lost_ask_reply(memory, clean, repaired=None):
    """The offer for "i dont know what to do", or None when this line is not that ask.

    One reply for one shape, from every door it can reach: as a statement it lands on the mood
    fallback, as a question on the hedge for an ask nothing can answer, and `_unknown` is that
    hedge's own door. A thread that already has advice in hand is left alone - "the boiler
    packed in" then "i dont know what to do" is the next step of that advice, and asking what
    has gone on reads as a bot that was not listening.
    """
    if the_advice(memory):
        return None
    if not (_a_lost_ask(clean) or _a_lost_ask(repaired or "")
            or _a_start_ask(clean) or _a_start_ask(repaired or "")):
        return None
    pick = the_pool_for_a_lost_ask(memory, clean if _a_start_ask(clean) else "")
    if not pick:
        return None
    return _choose(pick, memory, clean)


for _group, _words in (
        ("learn", "learn learns learning learned learnt teach taught train trained"),
        ("think", "think thinks thinking thought opinion opinions view views judgement "
                  "judgment mind brain smart clever intelligent wise understand understands "
                  "reason senses knowledge know knows decide decides deciding decided decision "
                  "decisions choose chooses choosing chosen choice choices pick picks picking "
                  "select selects sort sorts answer answers answering answered"),
        ("wrong", "mistake mistakes wrong right perfect honest"),
        ("feel", "feel feels feeling feelings emotion emotions alive living human person "
                 "people conscious consciousness aware sentient"),
        ("purpose", "exist exists existence point reason purpose"),
        ("regret", "regret regrets regretted regretting"),
        # A yes/no ask about a thing the bot plainly does, in a line with nothing else on it:
        # "can you do maths", "can you add up", "do you do sums", "can you count", "can you
        # spell". On main every one of these met the search hedge, which is the one reply that is
        # certainly wrong - the person asked the thing in front of them, not the world. Two
        # groups, because the two answers are different: figures, and words.
        ("sums", "sums sum maths math mathematics arithmetic add adds adding addition subtract "
                 "multiply divide total percentage percentages percent calculate calculation "
                 "count counting split"),
        ("spelling", "spell spells spelling spelled spelt grammar punctuation apostrophe comma "
                     "commas typo typos letters"),
        ("where", "body bodies family friends friend age old here there located program "
                  "programmed code computer machine robot ai chatbot bot")):
    for _word in _words.split():
        SELF_GROUP.setdefault(_word, _group)


def _thing_done_pool(clean):
    """The pool for a thing done, or None when the line is not one.

    Chosen by the verb and never by the noun: a thing seen to, a thing bought, a walk, and the
    rest of the made things, because the question a friend asks depends on which of those it was.
    """
    # A slip of the person's own is not a thing done. "i made a daft mistake at work" and "made a
    # stupid mistake today" have the shape of an afternoon - a past tense and something after it -
    # so the pool asked how it had gone: "What made you start on that?", "Nice - how did it go?".
    # The noun that carries the meaning is further along than the words after the verb, so the
    # thing-done reading cannot see it and the confession reader already does: `fallback_chain`
    # answers it with "That's the kind of thing that sits on you. Do you want to talk it
    # through?", and this only stands aside so that reader gets the turn. Imported here because
    # the two modules import each other at the end of the file.
    from .fallback_chain import _a_thing_they_regret
    if _a_thing_they_regret(clean):
        return None
    shape, done_verb = _thing_done_scan(clean)
    if not shape:
        return None
    if shape == "going":
        return A_THING_ON
    if shape in ("soon", "at"):
        # Not done yet: a question about how it went is a question about nothing.
        return A_THING_AHEAD
    if done_verb in GONE_VERB:
        return A_THING_GONE
    if done_verb in BOUGHT_VERB:
        if ALIVE.intersection(clean.split()):
            return None
        if NOT_CHOSEN.intersection(clean.split()):
            # A repeat prescription is not a purchase to weigh up: nobody weighs up which one to
            # go for, they are given it. "Good - was it straightforward?" is the question a
            # friend asks, and it is the same one the seen-to pool asks of a job.
            return A_THING_SEEN_TO
        return A_THING_BOUGHT
    if done_verb in SEEN_TO_VERB:
        return A_THING_SEEN_TO
    return A_THING_DONE


def the_dislike_ask(clean, memory):
    """A question about the thing the person has just said they do not like, or None."""
    thing = obstacle.the_thing(clean)
    if not thing:
        found = DISLIKE_WITHOUT_AN_I.match(" ".join(str(clean or "").split()))
        if found:
            thing = found.group("thing").strip(" ,.;:-")
            if not thing or thing.lower() in NOT_A_THING_ASKED:
                return None
            # The line is the person's own words, so a tail that only softens it ("the commute
            # already", "the open plan really") stays off the question.
            thing = DISLIKE_TAIL.sub("", thing).strip(" ,.;:-")
            if not thing or len(thing.split()) > DISLIKE_TOO_LONG:
                return None
            if DISLIKE_HAS_TWO_HALVES.search(thing):
                return None
            thing = _yours(thing)
            options = [frame.format(thing=thing, Thing=thing[:1].upper() + thing[1:])
                       for frame in DISLIKE_ASKS]
            return _choose(options, memory, clean)
    if thing:
        thing = _yours(DISLIKE_TAIL.sub("", thing).strip(" ,.;:-"))
    if not thing or len(thing.split()) > DISLIKE_TOO_LONG:
        return None
    if DISLIKE_HAS_TWO_HALVES.search(thing):
        return None
    options = [frame.format(thing=thing, Thing=thing[:1].upper() + thing[1:])
               for frame in DISLIKE_ASKS]
    return _choose(options, memory, clean)


def _a_doable(clean, memory):
    """The reply for a short "that's doable" about the advice just given, or None."""
    if not _reads_as_a_judgement(clean):
        return None
    if not the_advice(memory):
        # Nobody has been told anything to do, so there is nothing this line is judging.
        return None
    return _choose(DOABLE_REPLIES, memory, clean)


def _a_leaning_side(clean, memory):
    """The bot's own side of a trade-off the person has just put down, or None.

    "one pays more but the people are nicer in the other" / "what would you do" is a question a
    friend answers by leaning: the decide pool said "Not mine to decide, sorry", which is honest
    about what the bot knows and useless to the person who has already made the comparison.
    """
    # `PICK_ASK` does not cover "what would you do" - that is `LEAN_ASK`, the ask that only means
    # something once a trade-off is on the table - so both readings get in here, and the line then
    # has to be only the ask: "what would you do about the bike i just bought" names a subject of
    # its own and keeps its own answer.
    if not _a_bare_pick(clean) and not LEAN_ASK.search(clean):
        return None
    if not _a_lean_only_line(clean):
        return None
    if _in_a_care_thread(memory):
        return None
    side = _a_trade_off(memory)
    if not side:
        return None
    return _choose(TRADE_OFF_LEAN, memory, clean).format(side=side)


def _my_pick(clean, memory):
    """The bot's own pick, when the line asks for it and names nothing of its own."""
    offered = _offered(memory)
    if not _a_bare_pick(clean) and not (offered and PICK_BACK.match(str(clean or "").strip())):
        return None
    if _in_a_care_thread(memory):
        return None  # nothing blithe straight after a bereavement, a crisis or an emergency
    if offered:
        seed = len(memory.get("turns") or []) * 7919 + sum(ord(ch) for ch in clean)
        name, note = offered[random.Random(seed).randrange(len(offered))]
        if note:
            pool = [line.format(name=name, note=note) for line in MY_PICK_NOTE]
        else:
            pool = [line.format(name=name) for line in MY_PICK]
        return _choose(pool, memory, clean)
    if PICK_ADVICE.search(clean):
        return None
    return _choose(MY_PICK_ASK, memory, clean)


def _taste(clean, memory, was_taste, asking, repaired=""):
    """The bot's own answer to a question about its tastes, or None if it is not one.
    `was_taste` says the bot's last reply was one, so "why that one?" has something to explain.

    `repaired` is the same line with its chat-speak put right ("whats ur favourite food" ->
    "whats your favourite food"), read only when the typed line is not this shape at all: the
    repair is what makes the question about the bot, and without it the line reached the search
    hedge while the identical line with "your" spelled out got a taste.
    """
    if was_taste and _reads_as_why(clean):
        return _choose(WHY_AFTER_TASTE, memory, clean)
    # The person's own favourite, asked of the bot. The store's recall answers it when it was told
    # (PRIORITY 7000, so it keeps the turn); when it was not, the taste table answered with the
    # bot's own favourite ("whats my favourite food" -> "Roast potatoes"), which is a different
    # question, and the alternative was the search hedge, which answers nothing. Asking back is the
    # honest reply either way: it is right whether or not the person said it earlier.
    if asking and OWN_FAVOURITE.search(clean):
        found = OWN_FAVOURITE.search(clean)
        thing = found.group(1) or found.group(2) or ""
        value = _their_favourite_said(thing, memory)
        if value:
            return _choose(_their_favourite_back(thing, value), memory, clean)
        return _choose(OWN_FAVOURITE_LINES, memory, clean)
    if repaired and repaired != clean and not _has(clean, OPINION_ASKS) \
            and _has(repaired, OPINION_ASKS):
        clean = repaired
    asked = _has(clean, OPINION_ASKS)
    if asked and _is_about_the_persons_own_life(clean):
        return None  # "what do you think about my landlord refusing repairs" is advice
    if not asked and _is_a_choice(clean) and not _has(_choice_advice(clean), ADVICE_WORDS):
        # The advice words are read on the line without a *joint* question frame: "should we get a
        # pizza or a curry tonight" puts the choice to the bot, and "should" there is the frame
        # rather than a request for advice. "Should I ..." stays as it was - that one is the
        # person's own life ("should i push back or just take it", "no i mean should i quit") and
        # the pools that weigh a decision are the right answer to it.
        asked = True
    if not asked and asking and any(_has(clean, phrases) for phrases, _ in TASTES):
        asked = True  # "Is it ever OK to recline your seat?" names a taste, not a fact
    if not asked:
        return None
    if _is_about_the_persons_own_life(clean) and _has(clean, FAVOURITE_WORDS):
        # "what's my favourite food" asks what the store already holds, and the table's answer is
        # the bot's own taste: the ask was read from the thing named, not from whose taste it is.
        # Only for a line with the word favourite in it: a choice between two of the person's own
        # people ("my mum or my dad for christmas") is about their life too, and it is still the
        # choice pool's line, which is the reply it has always had.
        return None
    for phrases, options in TASTES:
        if _has(clean, phrases):
            return _choose(options, memory, clean)
    if _is_a_choice(clean):
        return _choose(_choice_pool(clean, memory), memory, clean)
    if _has(clean, FAVOURITE_WORDS):
        return _choose(FAVOURITE_GENERAL, memory, clean)
    return _choose(TASTE_GENERAL, memory, clean)


def _action(clean, memory):
    """A line with a right action gets it whatever its grammar: a statement can be an emergency."""
    said = " " + re.sub(r"[^a-z0-9']", " ", clean) + " "
    words = said.replace("'", "").split()
    routine = bool(ROUTINE_WAKE.search(clean))
    # Years ago is the doctor, not the ambulance: "my dad was unconscious for a minute years ago"
    # is a story to tell a GP, and only a line that says it is still going on keeps the call.
    story = reads_as_a_story(clean)
    if CANT_WAKE.search(clean) and not _names(words, said, GADGET_WORDS) and not routine \
            and not story:
        return EMERGENCY_ANSWER
    tail_only = UNRESPONSIVE_TAIL.search(clean) and not FEED_TAIL.search(clean)
    choking_thing = CHOKE_MACHINE.search(clean) and not CHOKE_BODY.search(clean)
    if _names(words, said, EMERGENCY_WORDS) and not _names(words, said, GADGET_WORDS) \
            and not choking_thing and not tail_only and not routine and not story \
            and not (OVERDOSE_FOOD.search(clean) and not OVERDOSE_DRUG.search(clean)) \
            and not CHOKE_ON_A_WORD.search(clean) \
            and not (OVERDOSE_OF_A_TREAT.search(clean) and not OVERDOSE_A_PILL.search(clean)) \
            and not _the_thing_is_choking(clean, words):
        return EMERGENCY_ANSWER
    if _names(words, said, FLOPPY_WAKE) and _names(words, said, TIRED) \
            and not _names(words, said, GADGET_WORDS):
        return EMERGENCY_ANSWER
    if not _names(words, said, LANGUAGE_FLUENCY) and (
            _names(words, said, GAS_WORDS) or (
                _names(words, said, FUME_WORDS) and _names(words, said, FUEL_WORDS))) \
            and not _names(words, said, PETROL_WORDS):
        return GAS_ANSWER
    animal = any(word in ANIMALS or word.rstrip("s") in ANIMALS for word in words)
    # "i blacked out the windows with curtains" is a verb about a window, not a faint.
    went_under = (PASSED_OUT.search(clean) and not BLACKED_OUT_A_THING.search(clean)
                  and not PASSING_OUT_A_THING.search(clean)) \
        or _blackout_words(clean, words, said)
    if went_under and not animal and not _names(words, said, LAUGHING_WORDS):
        if _names(words, said, CHILD_FAINT):
            return _choose([CHILD_FAINT_ANSWER], memory, clean)
        if FAINT_COMING.search(clean):
            # a faint that has not happened yet: sit down first, be seen after
            return _choose([FAINT_COMING_ANSWER + "."], memory, clean)
        return _choose([PASSED_OUT_ANSWER + "."], memory, clean)
    return None


def _unknown(understood, memory, clean):
    from .fallback_pools import _unknown as _moved
    reply = _moved(understood, memory, clean)
    a_hedge = _is_a_hedge(reply)
    # "how long have we been talking" is the bot's own to answer, and on today's main it is read
    # as a date on a document instead. The bot-about reader waits behind the hedge below, so a
    # card that misreads the line kept its turn: it now runs for a line about this chat itself,
    # whatever the pools made of it, and nothing else is let past that gate.
    if a_hedge or _asks_about_this_chat(clean):
        # The pools have all had the line and what came back was the search hedge. Three things
        # the bot can do better than a hedge, in order, each of them only a hedge replaced.
        about_me = _a_question_about_the_bot(clean, memory)
        if about_me:
            # A hedge is the last thing a person asking the bot about itself should get: it is
            # the one question the bot can answer from where it stands.
            return about_me
        if not a_hedge:
            return reply
        stuck = _what_to_do_about(clean, memory)
        if stuck:
            # "what should i do about the holiday i booked in august" was offered better sources
            # for a holiday nobody else has booked. The question about the thing they named is
            # the floor under the hedge, and only the hedge.
            return stuck
        no_subject = _an_ask_with_no_subject(clean, memory)
        if no_subject:
            # "whats the first step" names nothing of its own: the kind of help it wants can be
            # given anyway, and that is more use than a tip to go and search for the answer.
            return no_subject
        # A reply that already names somebody to ask keeps its turn: the lead may only take the
        # place of a bare search tip, never of a pointer with a name in it.
        lead = (_the_lead_and_the_route(clean, memory)
                if POINTER_HEDGE.search(reply or "")
                and not NAMES_WHERE_TO_ASK.search(reply or "") else "")
        if lead:
            # A search tip on its own hands the whole question back. What can be said without the
            # answer - what settles this kind of question, and what to have in front of you - comes
            # first, and where the rest lives comes after it.
            return lead
    return reply


def _what_to_do_about(clean, memory=None):
    """The questions for a "what should i do about X" line, or ""."""
    line = " ".join(str(clean or "").split())
    found = WHAT_TO_DO_ABOUT.match(line)
    if not found:
        return ""
    thing = found.group("thing").strip(" ,.;:-")
    if not thing or NOT_WHAT_TO_DO_ABOUT.search(line):
        return ""
    words = set(re.findall(r"[a-z']+", line.lower()))
    if (words & SYMPTOM_WORDS or words & BODY_PARTS or words & HEALTH_WORDS
            or any(w.startswith(HEALTH_STEMS) for w in words)):
        # A body, a symptom or a doctor is the health readings' turn: they say who can look, and
        # a "where would you want to start with the pain" would talk over them.
        return ""
    if thing.lower().split()[0] in NOT_A_THING_ASKED:
        # "what should i do about it myself" is still a pronoun, however it is dressed.
        # "what should i do about it" points at what was just said, and the thread answers that
        # better than any stock question: a sore knee then "what should i do about it" is the
        # health reading, not a weighing. Only a thing named in the line is asked about here.
        return ""
    if len(thing.split()) > DISLIKE_TOO_LONG:
        return ""
    named = _capital(_the_thing_alone(thing))
    if not named or named.lower().split()[0] in NOT_A_THING_ASKED:
        return _choose(DITHER_OPEN_LINES, memory, clean)
    lines = tuple(frame.format(thing=named if frame.startswith("{thing}") else named.lower())
                  for frame in WHAT_TO_DO_ABOUT_FRAMES)
    return _choose(lines, memory, clean)


def _a_question_about_the_bot(clean, memory=None):
    """What the bot can say when the line puts a feeling or a start to the bot itself, or ""."""
    line = " ".join(str(clean or "").split())
    if not line:
        return ""
    if ABOUT_THE_BOT_CLOCK.match(line):
        return _choose(BOT_TALK_CLOCK_LINES, memory, clean)
    if ABOUT_THE_BOT_TALK.match(line):
        return _choose(BOT_TALK_LIMIT_LINES, memory, clean)
    if ABOUT_THE_BOT_BORN.match(line):
        return _choose(BOT_BORN_LINES, memory, clean)
    found = ABOUT_THE_BOT_NAMED.match(line)
    if not found:
        return ""
    raw = (found.group("thing") or found.group("thing2") or "").strip(" ,.;:-")
    if raw.lower().split()[:1] and raw.lower().split()[0] in ("your", "ur", "you", "yourself"):
        # "how do you feel about your job" is the bot's own job, and the bot has none: the
        # bot-about reader above answers it, and a frame about the person's thing would be about
        # somebody else's job.
        return ""
    thing = _the_thing_alone(raw)
    if not thing or thing.lower().split()[0] in NOT_A_THING_ASKED:
        # "how are you feeling about it" points at something of theirs the bot cannot see, and
        # naming nothing back is better than a sentence about an unnamed thing.
        return ""
    if len(thing.split()) > DISLIKE_TOO_LONG:
        return ""
    said = thing.lower()
    lines = tuple(frame.format(thing=said) for frame in BOT_FEELING_NAMED_LINES)
    return _choose(lines, memory, clean)


def _tips(memory, clean, repaired=None):
    """A reply that turns a plea for tips into the one question that makes a tip possible.

    `repaired` is the same line with its wrong words put right ("any ideaz" -> "any ideas"),
    read for the subject only when the typed line carries none: the plea is recognised in the
    spelling the person meant, so the thing it is about is the thing they meant too.
    """
    subject = _tips_subject(clean) or (_tips_subject(repaired) if repaired != clean else None)
    if not subject:
        return ""
    # A pet is the vet's line - it is a named specialist, and the question here would be a
    # guess at what is wrong with the animal. A body is not the same thing: measured, the health
    # advisor does not fire on a tips plea (`any tips for my back pain` names no symptom), so
    # that line gets the question below like any other subject.
    said = " " + re.sub(r"[^a-z0-9']", " ", str(clean or "").lower()) + " "
    if _who_for(str(clean or "").lower(), said, said.replace("'", "").split()):
        return ""
    pool = TIPS_AHEAD if TIPS_SOON.search(subject) else TIPS_THING
    return _choose(list(pool), memory, clean)


def _who_for(clean, said, words, topic=None):
    """Which person settles this line, or None. Split from the reply so a caller can ask what
    the line matches without spending a stock line on it."""
    if _ASKS_DEFINITION.search(clean) or _ASKS_ARITHMETIC.search(clean):
        return None
    diy = bool(_ASKS_DIY.search(clean))
    gift = _names(words, said, GIFT_WORDS)
    meds = _names(words, said, MEDS_WORDS)
    buying = _names(words, said, BUYING_WORDS)
    if _names(words, said, SCHOOL_WORDS) and _names(words, said, SCHOOL_TROUBLE):
        return SCHOOL_WHO
    if _names(words, said, ("password",)) and _names(words, said, PASSWORD_TROUBLE):
        return DEVICE_WHO
    if _names(words, said, COMPLAINT_WORDS) and _names(words, said, TRADER_WORDS):
        return COMPLAIN_WHO
    animal = any(word in ANIMALS or word.rstrip("s") in ANIMALS for word in words)
    if animal and _names(words, said, WILD_BIRDS) and _names(words, said, MESS_PLACES):
        animal = False  # mess to clean up, not an animal that needs a vet
    machine_mouse = is_a_machine_word(clean)
    if not animal and meds:
        return HEALTH_WHO
    if not animal and _names(words, said, FILLING_WORDS) and (
            _names(words, said, MOUTH_WORDS)
            or not (topic in FOOD_TOPICS or _names(words, said, FILLING_FOODS))):
        return DENTIST_WHO
    # "where is the nappy bag" is a lost-object question, not a symptom one, and the two health
    # hand-offs answer a symptom. The trades, the vet, the pest controller and the landlord
    # advice all keep their where-lines ("where is the boiler", "where are the mice").
    where_is_a_thing = bool(_ASKS_WHERE.search(clean)) and not _names(
        words, said, WHERE_SOMETHING_WRONG)
    for evidence, who in WHO_TO_ASK:
        if where_is_a_thing and who in (BABY_WHO, HEALTH_WHO):
            continue
        if machine_mouse and who == PEST_WHO:
            continue  # "my mouse isnt working" is a faulty mouse, not a visitor in the kitchen
        if animal and who != VET_WHO and evidence & SICKNESS:
            continue  # "my dog's cough" is the vet's, not the pharmacist's
        if animal and who == DENTIST_WHO:
            # A mouth word on a named animal is the vet's, by the same rule as a cough: "my
            # rabbit has dental problems" was sent to a human dentist because `dental` is in
            # the dentist row and no pet guard looked at it, SICKNESS having no mouth word.
            continue
        if who == HEALTH_WHO and _SCHEDULING.search(clean):
            continue  # a moved appointment is a diary question, not a symptom
        if who == HEALTH_WHO and _CHOOSING_BETWEEN_TWO.search(clean):
            # "should i bend my knees or my back" is a choice between two acts, and the
            # two-option reading further down the chain is the one that answers it. A pharmacist
            # cannot call that for somebody, and the line is not about a symptom anyway.
            continue
        if who == HEALTH_WHO and _names(words, said, JOINT_WORDS) and not (
                _names(words, said, evidence - JOINT_WORDS)
                or _ASKS_ABOUT_THE_JOINT.search(clean)):
            # A joint is a body part before it is a symptom. "my knee replacement is in march,
            # what should i pack" asks about a bag, and in a thread about lifting "should i bend
            # my knees or my back" asks which way to bend; the hand-off stays for the line that
            # asks about the joint itself.
            continue
        if diy and who in (TRADES_WHO, DEVICE_WHO):
            continue  # "how do i fix my washing machine" is a job, not a phone call
        if who == BABY_WHO and _a_grown_up_asks(clean, words, said):
            # "can i eat baby rice" is a grown-up asking about a food, not a parent asking about a
            # baby: a phone line instead of an answer is worse than a wrong card, so the hand-off
            # stands down when the only baby in the line is part of a food's name, or when the
            # line names a grown-up outright.
            continue
        if who == BABY_WHO and not _names(words, said, CHILD_AT_HOME):
            # "teething problems with the new car" is a new thing finding its feet, and the
            # word only looks like the baby's: it is the tooth-cutting word in "my baby is
            # teething". With no child named, the row has nothing to send a car to.
            continue
        if gift and who in (BABY_WHO, HEALTH_WHO):
            continue  # a present is a taste, not a symptom
        if meds and who == DEVICE_WHO:
            continue  # a pet's tablets are the vet's, not a support page
        if who == DEVICE_WHO and _names(words, said, NETWORK_WORDS):
            continue  # the wifi is not the phone: the maker's page has nothing to say about it
        if buying and who == TENANT_WHO:
            continue  # buying a home is not a tenancy question
        if who == WORK_WHO and not _names(words, said, WORK_ABOUT):
            continue  # a boss at the end of a level, or a boss who is a nightmare, is not a dispute
        if _names(words, said, evidence):
            return who
    if animal and (meds or _names(words, said, SICKNESS)):
        return VET_WHO
    return None


def who_settles(text, memory):
    """Which person settles this line - "the school office", "a vet" - or None.

    Split from the reply so another module can ask what the line would be answered with,
    without spending one of the composer's stock lines or moving its state.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict) or \
            str(understood.get("text") or "") != str(text or ""):
        # The reading the store is holding is the line being answered now, and asking about an
        # earlier line with it answers for the wrong line: "who do i ring about it" was read as
        # the pronoun ask, and read that way "my boiler is banging" is not a boiler at all. The
        # re-read goes through a copy so the current turn keeps its own reading.
        borrowed = dict(memory) if isinstance(memory, dict) else {}
        borrowed.pop("understood", None)
        understood = understand(text, borrowed)
    clean = understood.get("clean") or " ".join(str(text).lower().split())
    words = understood.get("words") or []
    said = " " + re.sub(r"[^a-z0-9']", " ", clean) + " "
    return _who_for(clean, said, words, understood.get("topic"))


def _advisor(memory, clean, said, words):
    """Name the person whose job settles this line, when the line names that world: a reply
    or None. The subject alone is not enough - something has to be wrong in that world."""
    topic = (memory.get("understood") or {}).get("topic") if isinstance(memory, dict) else None
    who = _who_for(clean, said, words, topic)
    if not who:
        return None
    return _choose([line.format(who=who) for line in UNKNOWN_WHO], memory, clean)


def _trouble(memory, clean, words):
    """A statement of trouble ("my landlord wont fix the damp") still deserves the person who
    can settle it. Only with a trouble cue in the line: "i paid off my mortgage" is not a
    money problem, so the plain nod stays.

    A grown-up's plain symptom is not one of those: "ive got a sore throat" wants the care line
    the composer already has (rest, warm drinks), not a queue for the GP, so that row is only
    named when the line asks something ("should i worry", "how long does it last"). A baby's
    symptom is different: "my baby has a cough" is the health visitor's, question or not.
    """
    said = " " + " ".join(words) + " "
    if not any(word.startswith(cue) for word in words for cue in TROUBLE_CUES):
        return None
    if not _reads_as_question(clean, words):
        # The topic goes through, so a line with "filling" in it and no mouth word keeps the
        # food answer when the conversation is about cooking: the same escape `_advisor` uses.
        topic = (memory.get("understood") or {}).get("topic") if isinstance(memory, dict) else None
        who = _who_for(clean, said, words, topic)
        if who == HEALTH_WHO:
            return None  # your own sore throat is a symptom to look after, not a queue to join
    return _advisor(memory, clean, said, words)


def _named_draft(memory, text, words, clean):
    """The message the bot asked for, on a line that says it is the message - or None.

    Only for "saying ...", "asking about ...", "tell them ...": those lines name what the message
    says, so the subject word in them ("skint", "the deposit") is the message's reason and not a
    new topic to answer. Everything else waits its turn further down, behind the news, the
    symptoms and the losses, so a death after an offer is still condoled.
    """
    if not draft.says_it_is_the_message(clean):
        return None
    if (_action(clean, memory) or reads_as_pregnancy_bleeding(clean)
            or reads_as_sudden_loss(clean)):
        return None
    drafted = draft.drafter(memory, text, words)
    if not drafted:
        return None
    return _choose([f'{lead} "{drafted}"' for lead in draft.LEAD_INS], memory, clean)


def _after_safety(memory, clean, understood=None):
    """A careful continuation when the bot has just answered an emergency, or None.

    A follow-up line during a fire, a crisis or a bad bleed must never be met with "search
    online" or a neutral nod: the bot stays with the person and the real help. It holds while
    the turns since the safety answer are this fallback's own and the line is still about it,
    and lets go as soon as any other module answers or the person changes the subject.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    safety = None
    # Look back past this fallback's own continuations to the turn that started the thread.
    # A thread can run for several turns ("ok", "u there?", "what happens now"), so a fixed
    # window would forget the emergency while the person is still in it; the far end is
    # capped so an emergency from ten turns ago cannot colour an ordinary line today.
    window = turns[-THREAD_TURNS:]
    for index in range(len(window) - 1, -1, -1):
        if window[index].get("module") == "safety":
            safety = window[index]
            window = window[index + 1:]
            break
    if safety is None:
        return None
    read = understood if isinstance(understood, dict) else memory.get("understood")
    if not isinstance(read, dict):
        read = understand(clean, memory)
    last = str(safety.get("bot") or "").lower()
    for turn in window:
        if turn.get("module") == FALLBACK_MODULE:
            continue
        # A line about the conversation itself ("what have we talked about?") is answered by
        # the store, and it says nothing about the emergency: the thread holds across it rather
        # than being lost by the store's answer. An entry answer that says the emergency's own
        # words back is the thread going on ("a burn blister is a sterile dressing of its own;
        # cover it loosely") and holds too. Any other module's answer ends it.
        if history.not_a_subject(str(turn.get("user") or "")):
            continue
        if _words_kept(turn.get("bot"), last) >= THE_THREAD_KEPT:
            continue
        return None
    if _reads_as_fear(read, clean) and not any(word in last for word in CRISIS_WORDS):
        # Before the thread guard: a line about the speaker's own fear is about the emergency
        # whatever topic the reader gives it ("im really scared im going to lose him"). Not in
        # a crisis thread, where the person is the one in danger and the crisis pool holds.
        return _choose(AFRAID_AFTER, memory, clean)
    words = read.get("words")
    if not isinstance(words, list):
        words = re.findall(r"[a-z0-9']+", clean)
    in_crisis = any(word in last for word in CRISIS_WORDS)
    live = in_crisis or _the_answer_asked_them_to_call(last) or _raises_the_stakes(clean, last)
    if read.get("kind") == "greeting" and not (set(words) & CARE_WORDS):
        if live:
            # A hello inside a live emergency is not a fresh morning: "Morning! How's your day
            # going?" after "my brother has hung himself" reads as if the bot had stopped
            # listening. It is still a hello, so it is not the emergency instructions again
            # either (#1369 got the line here; this answers it). In a crisis thread the person
            # is the one in danger, so the hello asks about company - the part of the safety
            # answer a greeting can carry without repeating the whole card back at them.
            return _choose(HELLO_WITH_YOU if in_crisis else HELLO_STILL_THERE, memory, clean)
        # "hiya" a few lines after a burn is a hello, not news about the burn: the care pools
        # answer it with "keep an eye on it", which reads as if the person had said nothing,
        # and ending the thread would lose the close for "thanks, its stopped" later. So the
        # hello is answered as a hello that remembers the injury.
        #
        # But a hello is read from its opening, so "hi, its still bleeding" also comes back as
        # a greeting, and "How is it today?" would drop the one thing the line is reporting.
        # Any care content after the hello makes it a line about the injury, so it goes on to
        # the thread below like any other update.
        return _choose(GREETING_AFTER, memory, clean)
    if _asks_how_are_you(clean, read.get("plain") or clean) and not _burn_line(clean):
        # The same "how are you" the small-talk pool answers with "Doing well, thanks - what
        # about you?": inside an emergency it is the person checking the bot is still there, so
        # the answer says so and hands the question back. Read with the same test the small-talk
        # pool uses (`_asks_how_are_you`), so the two cannot drift.
        return _choose(CARE_HERE, memory, clean)
    if not live and A_BACK_AGAIN.match(clean.strip()):
        # A person coming back to a thread that gave them first aid gets a hello that remembers
        # the injury, not the neutral nod. Not the emergency line either: that belongs to an
        # answer that told them to ring, and this thread's answer only named the number as a
        # red flag ("... that's 999 or 911").
        return _choose(GREETING_AFTER, memory, clean)
    if _short_ack(words) and not live and _thread_was_closed(turns):
        # The thread already said goodbye ("thanks, its stopped" -> "Any time. Take care"),
        # so a nod after it is the end of the conversation, not a reason to reopen the advice.
        return None
    if MOVE_ON.search(clean):
        # "i feel a bit better, can we talk about something else" is a person closing the thread
        # themselves, so the answer is yes and an open door, never another line of advice.
        return _choose(MOVE_ON_AFTER, memory, clean)
    if not in_crisis:
        # A question about the advice itself - how long, how cold, whether to do it again, what
        # if it does not work - is still the thread. `_keeps_thread` lets it go, because "is ten
        # minutes enough" has a subject of its own and reads as a new subject, so it is answered
        # here, before the gate, from a pool per shape. Not in a crisis: the crisis pools keep the
        # person on the line, and "how long should i hold it" is not a crisis question.
        advice = _asks_about_the_advice(clean, last)
        if advice:
            return _choose(advice, memory, clean)
    # The outcome asked about - "does it get better", "will i always feel like this" - has no
    # answer in any pool: the shape is a pronoun and a word about how it turns out, so the floor
    # guessed at it ("Say what you are asking about and I'll answer it properly rather than
    # guess") or reached for a search. It is read here, before the thread gate below, because the
    # gate reads "better" as a subject of its own and lets the emergency go. The abuse card has
    # its own pool, because "will things get better" there is about the relationship and not about
    # a symptom. See `bot/compose/outlook.py`.
    if outlook.asks_the_outlook(clean):
        # Read from every safety answer still in the thread, not from the last one: the module
        # answers a fear line itself ("I'm here. You're doing the right thing by staying with
        # them"), and that continuation names the number without the card's own words, so a
        # reading of the last reply alone took a calling-999 thread for a first-aid one and told
        # the person "it should be easing, not getting worse - give it a day".
        cards = _the_safety_cards(turns)
        in_a_crisis = any(word in card for card in cards for word in CRISIS_WORDS)
        told_to_call = any(_the_answer_asked_them_to_call(card) for card in cards)
        abuse = any(_the_answer_was_an_abuse_card(card) for card in cards)
        pool = outlook.the_pool(in_a_crisis, _somebody_is_coming(turns, clean), told_to_call,
                                abuse=abuse)
        if pool is None:
            # First aid, or a card that named an appointment: the forecast pool already answers
            # "will it get better" in a thread the bot has just answered with first aid, and that
            # line was written for exactly this talk, so the shapes it does not read get the same
            # line rather than a second voice. It works for a condition as well as an injury, which
            # "most of these settle in a day or two" does not: the card for sight that has always
            # been like that is not a burn.
            pool = [phrase.format(who="you") for phrase in FORECAST_AFTER_SAFETY]
        return _choose(pool, memory, clean)
    # From here the pools are chosen, and two of them have to know who is in danger. A crisis
    # answer about "my sister" is continued in the carer's words, not the person's own.
    them = _about_somebody_else(safety, memory)
    if _the_answer_was_an_abuse_card(last) and (_THE_WAY_OUT.search(clean)
                                                 or _ASKS_TO_LEAVE.search(clean)):
        # The abuse card names a helpline, so every pool below reads this thread as somebody's
        # suicide - and the relation in the opening line ("my husband hit me") as the person in
        # danger - so "should i get out of the house" was answered "keep your husband company
        # tonight". The person asking is the one in danger here, and the question is whether to
        # go, so it is answered about going. Before the reading below, which takes "should i go"
        # for a doubt about a symptom ("that's reason enough to have it seen today").
        return _choose(ABUSE_AFTER, memory, clean)
    if live and _a_report_on_the_advice(clean, words, False) in (
            TRIED_NO_CHANGE, TRIED_NO_CHANGE_ELSEWHERE, TRIED_WORSE, TRIED_WORSE_ELSEWHERE):
        # "it doesnt work" while the answer the person is reporting on named 999 is not a reason
        # to step down to a lesser route: it is the emergency still going, and the answer says the
        # route again. Placed before the thread gate, which reads the "work" in the line as a new
        # subject and would let the emergency go.
        if in_crisis and them:
            return _choose(_wrote_for_them(CRISIS_AFTER_THEM, them), memory, clean)
        return _choose(CRISIS_AFTER if in_crisis else EMERGENCY_NOT_WORKED, memory, clean)
    if THING_SORTED.search(clean):
        # "i sorted it" in a safety thread is the person saying they did the step, not a job
        # finished with a cheer. The plan pool took it - "Nice - glad that's sorted. Shout if it
        # comes back." - and closed an emergency two lines in, because it is a fallback pool that
        # fires after any answer (red-door, #6574). Read here, before the thread gate, which
        # reads "sorted" as a subject of its own and lets the emergency go; the hold keeps the
        # line open and never repeats the card at them.
        return _choose(CRISIS_AFTER if in_crisis
                       else _hold_pool(turns, clean, last, done_report=True),
                       memory, clean)
    if not in_crisis:
        # A bare doubt - "is that bad", "is that ok" - is read by the composer out of the answer
        # above, and on a safety line that reading knows whether the answer asked for today: "im
        # 6 weeks pregnant and cant keep anything down" is answered "that needs a real person
        # today", and the doubt after it got this file's "Keep an eye on it and tell me if
        # anything changes" - a doubt answered more softly than the answer asked for. One
        # reading, one place: the pools below are what is left when it has none.
        from . import verdict
        reading = verdict.reply_for(clean, memory)
        if reading:
            return reading
    if in_crisis and (_a_lost_ask(clean) or _a_start_ask(clean)):
        # "i keep thinking about ending it" then "i dont know where to start": the thread gate
        # below reads the asking words as a subject of their own ("the start of something" is not
        # in the answer) and let the crisis go, so the neutral pool answered a person in danger
        # with "I'm listening - say more if it helps". A person who cannot see the next step has
        # not changed the subject, and in a crisis the next thing to say is the company and the
        # number, not the shrug. Only a crisis answer: the care pools say "stay in touch with
        # them", which is about somebody else, and the person here is the patient.
        return _choose(CRISIS_AFTER, memory, clean)
    if _the_hazard_is_gas(safety.get("user")) and (
            _THE_WAY_OUT.search(clean) or _goes_back_for(clean, safety.get("user") or "")):
        # "shall i open the windows" a turn after the gas card was the fire escape, because the
        # safety answer names opening windows only in the words it was written for.
        return GAS_ANSWER
    if _the_threshold_was_crossed(last, clean, turns):
        # "now my arm hurts too" after "ring 999 or 911 straight away if it spreads to the arm or
        # jaw": the answer named what would make it an ambulance, and this line is standing on
        # it. The route hand-back and the hold pool below would both answer it with something
        # softer than the answer itself did, so the 999 the answer named is the reply.
        return _choose(THRESHOLD_CROSSED, memory, clean)
    if not _feels_better(clean) and not (
            _goes_back_for(clean, safety.get("user") or "")
            or _keeps_thread(
                read, clean, safety.get("user") or "",
                crisis=not _releasable(memory) or _raises_the_stakes(clean, last))):
        # The worst of it is passing: "i feel a bit better now" is a report on the emergency, not
        # a new subject, so it is answered below rather than let go as a change of subject.
        return None
    if (read.get("kind") == "thanks" or set(words) & THANKS_WORDS) \
            and not _thanks_carries_emergency(words, clean):
        # "ok thanks" closes the thread warmly; it is not a new statement to answer. A thanks
        # that still names the emergency ("thanks, its still soaking through") is not a close:
        # the person is telling the bot it has not stopped, so the thread has to stay open.
        return _choose(THANKS_AFTER, memory, clean)
    if _short_ack(words):
        # A bare "ok" mid-emergency is someone who heard the advice, not a new line:
        # "ring 999 if you haven't already" would be a strange thing to say twice.
        if in_crisis:
            # In a crisis thread the person is the one in danger and nobody has been called, so a
            # nod is answered with the company the crisis pool names ("Keep someone with you
            # tonight"), not with the holding line for an injury ("keep an eye on it"). It is the
            # pool an agreement already gets there, so "same" and "ok" no longer answer the same
            # crisis two ways.
            return _choose(CRISIS_AFTER, memory, clean)
        return _choose(_hold_pool(turns, clean, last), memory, clean)
    last = str(safety.get("bot") or "").lower()
    asked = read.get("kind") == "question" or "?" in clean
    if not _reads_as_fear(read, clean) and set(words) & REACTION_WORDS and any(
            str(t.get("bot") or "") in RESOLVED_AFTER for t in turns[-2:]):
        # "ok its out now" / "the ambulance is here" was the last thing said, so a reaction to it
        # gets the after-close pool: not "keep following the emergency line", and not "the crew
        # are on their way" for a crew that has already arrived. The speaker's own fear is not
        # one of those reactions: "im still scared" with the crew in the room still wants
        # company, so it falls through to the fear pool below.
        return _choose(AFTER_RESOLVED, memory, clean)
    if (not asked and RESOLVED.search(clean) and not NEEDS_SEEN.search(clean)
            and not _someone_is_arriving(clean)):
        if not them and _a_newer_answer_asked_them_to_call(last, turns) \
                and not ALREADY_RANG.search(clean):
            # "i think im fine" after this file told them to ring 999 for what they described is
            # not the end of it: the close ("That's the important bit done") is for a call that
            # was made or a crew that arrived, and neither has happened. A line that says they
            # rang keeps the close - that is the person doing the thing, not talking it down.
            return _choose(THE_CALL_STANDS_ANYWAY, memory, clean)
        # The end of it: "ok the fire is out now", "its stopped now". After the reaction-to-the-
        # close pool, so "its out but i feel shaky" is answered for the shaky and not by the close
        # a second time; before the ring branch, so "ok i rang them and hes fine now" is the close
        # and not a promise that "the crew are on their way". Help arriving is not the end of it:
        # "the crew are here", "the paramedics are here", "the ambulance is here" read as a close
        # to RESOLVED's arrival alternative, and answering them with "ring again if anything
        # changes" drops the line to the crew (cream-flag, #820). They keep the arrival pool.
        return _choose(_wrote_for_them(RESOLVED_AFTER_THEM, them) if them else RESOLVED_AFTER,
                       memory, clean)
    if ALREADY_RANG.search(clean):
        # "ok i rang them" is the person saying they did the thing, so "ring 999 if you haven't
        # already" reads as not listening.
        if A_HELPLINE.search(clean):
            # A helpline is not a dispatch: the samaritans, a crisis line and NHS 111 all talk,
            # and none of them send anybody. In a crisis thread the answer is the company the
            # person needs after telling somebody, in an ordinary one the care hold, and in a
            # thread whose last answer asked for 999 the day is not saved by ringing them.
            if any(word in last for word in CRISIS_WORDS):
                return _choose(_wrote_for_them(CRISIS_AFTER_THEM, them) if them else CRISIS_AFTER,
                               memory, clean)
            if any(word in last for word in SAFETY_WORDS):
                return _choose(HELPLINE_NOT_AN_AMBULANCE, memory, clean)
            return _choose(STILL_HERE_AFTER, memory, clean)
        if any(word in last for word in CRISIS_WORDS):
            # "ok i rang them" in a crisis thread is the crisis line, because that is the number
            # the bot gave: nobody has been sent, and "the crew are on their way" is not true.
            return _choose(_wrote_for_them(CRISIS_AFTER_THEM, them) if them else CRISIS_AFTER,
                           memory, clean)
        return _choose(HOLD_AFTER, memory, clean)
    if _reads_as_fear(read, clean) and not any(word in last for word in CRISIS_WORDS):
        # A line about the speaker's own fear gets company instead of the practical pool: it is
        # about the emergency whatever topic the reader gives it ("im really scared im going to
        # lose him"). It runs after the close and the thanks, so a fear once it is over gets
        # "the hardest part over", and not in a crisis thread, where the person is the one in
        # danger and the crisis pool holds.
        return _choose(AFRAID_AFTER, memory, clean)
    if set(words) & REACTION_WORDS:
        if any(word in last for word in CRISIS_WORDS):
            # Scared after a crisis answer is not somebody waiting for an ambulance: nobody has
            # been called, so the holding pool would promise a crew that is not coming.
            return _choose(_wrote_for_them(CRISIS_AFTER_THEM, them) if them else CRISIS_AFTER,
                           memory, clean)
        return _choose(_hold_pool(turns, clean, last), memory, clean)
    if (VISIT_ASK.search(clean) and not MEDICAL_PLACE.search(clean)
            and not NOT_A_VISIT.search(clean) and _somebody_to_visit(clean, turns)):
        # Whether to go and be with them, not whether to have the injury seen: before the injury
        # pool, because "should i go up tonight" matches the bare "go" in CARE_SEEN_ASKS.
        pool = CARE_VISIT_WARD if _someone_is_a_patient(clean, turns) else CARE_VISIT
        return _choose(pool, memory, clean)
    if CARE_SEEN_ASKS.search(clean):
        if _the_thread_is_an_animal(clean, turns):
            # A pet is not seen at a walk-in centre or in A&E: the same question about an animal is
            # the vet's, and the answer has to say so.
            return _choose(CARE_SEEN_ANIMAL, memory, clean)
        return _choose(CARE_SEEN, memory, clean)
    if _feels_better(clean):
        # Whether the thread is a crisis line or a first-aid answer, "i feel a bit better now" is
        # not answered by either pool: "ring 999 if you haven't already" reads as if the bot had
        # not heard, and so does "ring the crisis line now".
        if _no_relief(memory, last):
            # An overdose, a poisoning or an arrest is the one easing that must not be taken at
            # face value: the pool keeps the emergency line instead of sending them back to their
            # day. When the person who swallowed it is somebody else, the same instruction goes to
            # the carer about them - "get seen today" addressed to the person typing is advice for
            # a body that is not the one at risk.
            if them:
                return _choose(_wrote_for_them(EMERGENCY_BETTER_THEM, them), memory, clean)
            return _choose(EMERGENCY_BETTER, memory, clean)
        if any(w in last for w in CRISIS_WORDS):
            # "she says shes fine now" is their good hour, so the easing is the carer's: keep an
            # eye on them, ask again tomorrow.
            if them:
                return _choose(_wrote_for_them(CRISIS_BETTER_THEM, them), memory, clean)
            return _choose(CRISIS_BETTER, memory, clean)
        return _choose(CARE_BETTER, memory, clean)
    # The injury is read from the answer and from the line it answered: a sunburn is a burn
    # whether or not the safety card happens to use the word.
    opener = str(safety.get("user") or "").lower()
    if BURN_WORD.search(last) or BURN_WORD.search(opener):
        # Nothing on a burn and nothing popped: the two things people ask straight after being
        # told to cool it, and the two a knowledge entry answers wrongly ("oven", "butter").
        if BURN_BLISTER_LINE.search(clean) or POP_A_BARE_IT.search(clean):
            return _choose(BURN_BLISTER, memory, clean)
        if BURN_ON_IT.search(clean) or (BURN_THING.search(clean) and BURN_ASK.search(clean)):
            return _choose(BURN_AFTER, memory, clean)
    if them and SAID_AS_A_DEATH.search(clean):
        # The emergency was somebody else's and it is over: "my friend shot himself" and then "he
        # didnt make it", or a heart attack and then "she died". What is left is a bereavement, and
        # the loss module answers those - it answered this one on main, because no emergency card
        # had started the thread; with the card on the line before it, the emergency pool said
        # "stay in touch with them and say if anything gets worse" to somebody whose friend had
        # just died. Only when the person in danger is somebody else: after "i took too many pills",
        # "he died didnt he" is a question asked by a body that still needs the 999 hold.
        return None
    if any(word in last for word in CRISIS_WORDS):
        # In a crisis the continuation names the crisis line, and it says more about staying
        # safe tonight than "two of you is better than one" does; a person arriving is a good
        # sign, not a reason to drop the careful one (#deck row multi-042).
        return _choose(_wrote_for_them(CRISIS_AFTER_THEM, them) if them else CRISIS_AFTER,
                       memory, clean)
    if _someone_is_arriving(clean):
        # "my sister says she can come over tonight", "the ambulance is on the way"
        return _choose(WITH_YOU_AFTER, memory, clean)
    if _already_rang(turns):
        # The person said two turns ago that they rang, and "what happens now" is the line after
        # it: "ring 999 if you haven't already" tells them the bot was not listening. The hold
        # says the true thing instead - stay on the line and follow what they tell you.
        return _choose(HOLD_AFTER, memory, clean)
    if _the_answer_asked_them_to_call(last) or _raises_the_stakes(clean, last):
        # Which emergency it is decides the words: a person who is hurt is someone to stay in
        # touch with, a fire is not. The bot's own last answer says which one it was - the fire
        # answer names the smoke, the scald answer names the water - so the pools continue that
        # answer instead of guessing from the line. A follow-up that meets the card's own red
        # flag comes here too: the fall card's "cannot get up or put weight on it" said as
        # "im on blood thinners" is the emergency going on, not a line for the pharmacist.
        if _is_a_hazard(last):
            return _choose(HAZARD_AFTER, memory, clean)
        return _choose(EMERGENCY_AFTER, memory, clean)
    if _the_thread_is_an_animal(clean, turns):
        # The after-care pool names a pharmacist and a walk-in centre. An animal is not seen at
        # either of them, so the same continuation is said about the vet.
        return _choose(CARE_AFTER_ANIMAL_STILL if STILL_GOING.search(clean) else CARE_AFTER_ANIMAL,
                       memory, clean)
    if _a_newer_answer_asked_them_to_call(last, turns):
        # The care answer's route is out of date: this thread has since been told to ring, and
        # the person has not said they rang (that is answered further up), so the pool after an
        # emergency answer is the reply. Naming 111 here contradicts the bot's own last line,
        # and so does the softer hold: the number is still theirs to dial.
        return _choose(THE_CALL_STANDS, memory, clean)
    route = _the_route_the_answer_named(last)
    if route and not THE_THING_ITSELF_LOOKS_FINE.search(clean):
        # The answer named where to go and this line is about that answer: "my chest hurts when i
        # run" is answered "ring 111 or your GP first thing", so the pharmacist line that came
        # next named a different building - one that does not see a chest. A line that reports
        # the person looking well ("hes eating and playing fine") is not sent to ring again.
        return _choose(CARE_ROUTE_BACK[route], memory, clean)
    return _choose(CARE_AFTER_STILL if STILL_GOING.search(clean) else CARE_AFTER, memory, clean)


def _thanks_news_went_badly(clean):
    """The outcome when a thank-you came back with bad news, or "" when it did not.

    A thank-you with something after it is the person telling the bot how the thing it answered
    went, and that something is the news. "Thanks, its still soaking through" was read as thanks
    and nothing else by the kind reader, so the thank-you pool thanked them back. The outcome is
    the line whenever it says the thing did not come right, and this is the one test both places
    ask, so they cannot disagree.
    """
    said = _thanks_then_said(clean)
    if not said or THANKS_GOOD_AGAIN.search(said):
        return ""
    if THANKS_WENT_BADLY.search(said):
        return said
    words = re.findall(r"[a-z']+", said)
    return said if _mood(words, said) == "negative" else ""


def reading(text, memory):
    """(kind, target) for a line the composer answers itself, or ("", ()) for an ordinary one.

    One place for the composer to say what it is doing with a line the rest of the app must not
    answer as small talk. `THREAD`'s target is the one continuation, as text. The arbiter asks
    this once per turn and decides only when a module keeps the turn instead; adding a third
    kind is one branch here and one there, never a second scanning loop in the router.
    """
    try:
        continuation = careful(text, memory)
    except Exception:  # noqa: BLE001 - a composer that cannot read changes no reply
        continuation = None
    if continuation:
        return (CARE_THREAD if _a_care_thread(memory) else THREAD), (continuation,)
    try:
        if leaving.reads_as_leaving(" ".join(str(text or "").lower().split())):
            return leaving.LEAVING, ()
    except Exception:  # noqa: BLE001 - a reading that fails just adds no kind
        return "", ()
    try:
        # Not inside a thread that has its own voice: after a condolence the listening line is
        # what the composer answers with ("I'm listening - say more if it helps") and a breezy
        # "No bother at all - go on" is the wrong voice for it, and inside a live crisis the
        # thread's own line is the answer.
        if (not _grief_thread(memory) and not in_a_safety_thread(memory)
                and reads_as_pause(" ".join(str(text or "").lower().split()))):
            return PAUSE, ()
        # A line that only points back at the conversation is the same kind for the arbiter's
        # purpose - no topic entry may take it back on a word of it ("where was i" was answered
        # with the search shrug, "as i was saying" with "Sounds alright") - and the wording is a
        # second pool (`RETURNED_TO_IT`), chosen in fallback_chain beside this one.
        if (not _grief_thread(memory) and not in_a_safety_thread(memory)
                and _a_chat_behind_it(memory)
                and reads_as_a_return(text) is not None):
            return PAUSE, ()
    except Exception:  # noqa: BLE001 - a reading that fails just adds no kind
        return "", ()
    return "", ()


def _after_advice(memory, clean, words):
    """The reply for a report on the advice in the last answer, or None."""
    step = _the_next_move_after_the_advice(memory, clean, words)
    if step:
        return step
    pool = _the_outcome_of_the_advice(memory, clean, words)
    if not pool:
        return None
    # Seeded on the advice, not on the report. "i tried that and it didnt work" is the same seven
    # words in every thread, so seeding the pool on the report gave a person the same sentence
    # after a sink, a kettle and a pan of mince - STYLE.md's worst tell. The advice is what makes
    # this thread different from the next one, so it is what the wording is drawn from.
    return _choose(pool, memory, clean, seed_text=the_advice(memory) or clean)


def _a_refusal_to_answer(clean, memory, words=None):
    """The pool for a line that reports somebody else's no, or None.

    The person did what the answer said and it was turned down - by a boss, a landlord, a bank, a
    council, or the person they live with. The composer has the answer to that and the ack does
    not: said back it is "Got it - your boss said no", which is the person's own line with nothing
    added. Read in one place so the reply and the claim cannot drift apart (`reads_as_a_refusal`
    asks the same question for the arbiter).

    Narrow on purpose: no question mark, fifteen words at most, a party who can be asked again or
    an answer above for the no to be about, no no from somebody treating them, and nothing that
    reads as a fault to repair. A thread with a death or a live safety answer keeps its own line.
    """
    if "?" in str(clean or ""):
        return None
    if not REFUSED.search(clean):
        return None
    # The speaker's own no is a decision they made, not one made against them: "my son wants a
    # phone / i said no" is a parent holding a line, and telling them to ask again is the bot not
    # listening. Nobody to ask, either: "why did my boss say no" is a question about the no.
    if OWN_NO.search(clean) or ASKS_WHY.search(clean):
        return None
    # A no in the future, or in a case they are working out, is not one they were given.
    matched = REFUSED.search(clean)
    if matched and HYPOTHETICAL.search(str(clean or "")[:matched.start()]):
        return None
    words = clean.split() if words is None else words
    if len(words) > 15:
        return None
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not REFUSED_PARTY.search(clean) and not _an_answer_above(turns):
        # Nobody is named who could say yes next time, and there is no answer above this line for
        # the no to be about: "she said no" on its own is a person turned down in their own life,
        # and "ask once more what would make it a yes" is the wrong thing to say about it.
        return None
    if REFUSED_NOT.search(clean) or REFUSED_FAMILY.search(clean):
        return None
    # A written thing says no what is inside it, and nobody was refused: "the invite says no dress
    # code" came back as advice to ask again about a wedding's dress code.
    if REFUSED_NO_OBJECT.search(clean):
        return None
    # The card above was the step for a no already - "put it in writing, name what you disagree
    # with" - and the store hands that answer back. Asking once more is the weaker line after it.
    if _the_answer_above_already_says_what_to_do(turns, memory):
        return None
    # A chat about somebody's conduct is not an ask that can be trimmed: there is no smaller
    # version of "stop touching me", and the card above already gave the record and the route.
    if _a_thread_about_how_somebody_treats_them(turns):
        return None
    try:
        if trouble.reads_as_trouble(clean):
            return None
        if _in_a_loss_thread(memory) or _grief_thread(memory) or in_a_safety_thread(memory):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return None
    if turns and _in_a_pool(str(turns[-1].get("bot") or ""), (REFUSED_REPLIES,)):
        # The pool has already said this once, so saying the same thing in other wording is the
        # bot repeating itself: the second no in a thread is met by the detail it brings.
        return None
    return REFUSED_REPLIES


def _a_care_thread(memory):
    """True when the safety answer this thread continues was first aid, not a crisis line."""
    answer = _thread_answer(memory)
    if not answer:
        return False
    return not any(word in answer for word in CRISIS_WORDS)


def in_a_safety_thread(memory):
    """True when the bot's last word in this stretch was a safety answer.

    Read by the arbiter: an apology for the pause inside a live crisis keeps the thread's own
    line ("I'm listening - say more if it helps"), where the light "No bother at all - go on"
    is the wrong voice for a person who has just said something that frightened them.
    """
    return bool(_thread_answer(memory))


def _thread_answer(memory):
    """The bot's safety answer this thread continues, lower case, or "" when there is none.

    A thread holds across the composer's own continuations and across an entry answer that is
    still about the emergency - the burn's own blister line after "should i pop the blister" -
    because that entry is the thread going on, and losing the thread there took the next line
    off it: "can i put cream on it" was answered from the measles entry once the burn's answer
    was no longer in hand. Any answer that says nothing of the emergency ends it.
    """
    window = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-THREAD_TURNS:]
    answer = ""
    for index in range(len(window) - 1, -1, -1):
        if window[index].get("module") == "safety":
            answer = str(window[index].get("bot") or "").lower()
            window = window[index + 1:]
            break
        if window[index].get("module") == FALLBACK_MODULE:
            continue
    if not answer:
        return ""
    for turn in window:
        if turn.get("module") == FALLBACK_MODULE:
            continue
        if _words_kept(turn.get("bot"), answer) >= THE_THREAD_KEPT:
            continue
        return ""
    return answer


OWN_THING = re.compile(r"\b(?:my|our|his|her|their)\s+(\w+)")


def _words_kept(reply, answer):
    """How many of an answer's own words a reply says back, or 0.

    The count behind `how_much_of_the_answer_kept`, and the test for whether a reply is still
    about the thread's thing: an entry answer that says three of the emergency's words back is
    following the thread ("a burn blister is a sterile dressing of its own; cover it loosely"),
    where one about another subject says none of them ("leave the shoes off for short
    stretches"). Reading it here keeps one number for both questions.
    """
    said = set(_words(str(answer or "").lower()))
    return len({word for word in _words(str(reply or "").lower())
                if len(word) >= 5 and word in said})


def careful(text, memory):
    """The careful continuation a line inside a safety thread gets, or None.

    `reply_for` gives it too, but a light module may propose a reply to the same line and win
    on PRIORITY ("im scared" twice in a row deserves the thread, not a reframe about worry).
    The arbiter reads this to keep the thread (bot/modules/arbiter.py), so the wording and the
    judgement of what still counts as the same thread live here, in the composer.
    """
    understood = memory.get("understood")
    clean = " ".join(str(text or "").lower().split())
    return _after_safety(memory, clean, understood if isinstance(understood, dict) else None)


# The words that make a nod a nod after a hard line rather than after anything else. The mood
# reader already knows which way a line goes, and a line it reads as negative is a line the person
# was not making small talk on. This is only asked when the nod has nothing of its own, so a
# "mm" after "the boiler is fixed" is still left to the cheerful pool.
def _the_last_line_was_heavy(memory):
    """True when the last exchange was a hard thing, not small talk.

    Either side says it: the person's line read as a low one, or the answer we gave was one of the
    heavy pools ("Sorry to hear that", "That's a lot to be holding in"). The second is needed
    because the mood reader does not know every word - "im gutted" and "i want to cry" read
    neutral - and our own line is the plainest evidence of which thread we are in.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    last = turns[-1]
    said = str(last.get("user") or "").strip()
    if said:
        words = _words(said.lower())
        if words and _mood(words, said.lower()) == "negative":
            return True
    return bool(OUR_HEAVY_TELL.search(str(last.get("bot") or "").lower()))


# The rest of this module's rows live in fallback_chain.py, so this file stays under the publisher's
# 1 MiB limit. They are imported here, at the end, where everything they use above is
# already defined. New rows belong in that file too, or this one grows back over the limit.
from .fallback_chain_part_01 import (
    ACTS_AN_ERRAND, ACTS_AN_ERRAND_LINES, ACTS_IN_A_DIARY, ACTS_IN_A_DIARY_LINES, ACTS_ON_A_PHONE,
    ACTS_ON_A_PHONE_LINES, ACT_CHOICE, ACT_FOR_ME, ACT_OPENER, ACT_OWN_STEP, ACT_REPORT_TAIL,
    ACT_SETTING, ACT_THING, ADDRESSED, BOOKING_THING, CAN_DO_ITSELF, HABIT_MIND_IT, HABIT_NOT,
    HABIT_STATED, HANDS_IT_OVER_HERE, NOT_ABOUT_THEM, NOT_A_THING_TO_GET, POLITE_ASK, REMIND_ME,
    _a_claim_about_a_thing, _a_part_is_cold, _a_state_in_the_past, _act_asked_of_me, _acts_for_me,
    _body_state, _cue_negated, _habit_is_a_problem, _reads_as_a_bad_stretch, _state_from,
    _the_state, _the_store_has_the_recall, _the_win_is_someone_elses, _a_part_in_a_state,
)
from .fallback_chain_part_02 import (
    ASK_SHAPE, AT_THE_CLOCK, A_CLOCK, A_LENGTH, A_LIST_ON_THE_TABLE, A_MOOD, A_TIME_SAID,
    CLOCK_ABOUT_THE_JOB, CLOCK_ASKED, CLOCK_NOT_THIS, CLOCK_SHAPE, CLOCK_SOMEONE_ELSE,
    CLOCK_THE_DEPARTURE, FRAME_PREFIX, HURT_BUT_FINE, HURT_DEATH, HURT_FIGURE, HURT_ON_THE_SPEAKER,
    HURT_SOMEBODY, LOW_DAY, LOW_DAY_MINE, LOW_DAY_NOT_MINE, OPTION_ON_THE_TABLE, OWN_THING,
    _A_CORRECTION, _ROUTINE_NOT_SHAPE, _UNDERTAKING, _a_birthday_still_to_come, _a_lateness_report,
    _a_low_day, _a_things_state, _asks_the_bot, _choose, _flat_habit_stated, _loves_people,
    _loves_someone, _mixed_seed, _mood, _options_already_up, _reads, _reads_value, _restated,
    _routine_pool, _somebody_elses_day_in_thread, _somebody_hurt, _the_birthday_said_back,
    _the_clock_pool, _the_morning_has_a_clock, _the_person_named_a_list, _the_time_said, _words,
    reads_as_a_flat_habit,
)
from .fallback_chain_part_03 import (
    AN_ATTEMPT_AT_SOMEONE, A_BAD_THING_NAMED, A_BARE_MODIFIER, A_CHILDHOOD_MEMORY, A_CROWD,
    A_CROWD_AHEAD, A_DAY_SUBJECT, A_DAY_WENT_WRONG, A_HAND_OUT, A_MILESTONE, A_MISTAKE,
    A_REGRET_DOING, A_SYMPTOM_PHRASE, A_VISIT, BAD_DAY_ANYWAY, CROWD_ORDER, DAY_PAST, FOOD_TOPICS,
    NOT_A_CROWD_AHEAD, NOT_A_DAY_DONE, NOT_A_DAY_SAID, NOT_A_JOB_BUT_A_PERSON, NOT_A_REGRET,
    PAST_DOING, SNAPPED_A_PHOTO, SOMEONE_ELSE_NAMED, THEIR_OWN_DOING, THE_JOB_NAMED, _AN_ASKING,
    _AN_ATTEMPT_COUNT, _A_BODY_UNWELL, _A_DETAIL_OPENING, _A_NEGATIVE_AUXILIARY, _A_SYMPATHY,
    _a_care_home_line, _a_day_of_someone_else, _a_detail_about_what_was_said, _a_dish_name,
    _a_thing_got_ahead, _a_thing_happened, _a_thing_they_regret, _just_asked_about_the_day,
    _repaired_of, _the_crowd_is_ahead,
)
from .fallback_chain_part_04 import (
    _a_day_told_instead_of_the_receipt, _a_small_day, _answers_the_correction, _reply_for,
    reply_for,
)
from .fallback_chain_part_05 import (
    TAKES_AS_IT_COMES, _a_report_with_no_pronoun, takes_as_it_comes,
)
