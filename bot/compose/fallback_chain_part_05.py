"""Part 5 of 5 of the module, split out of `fallback_chain`.

Everything here is re-exported from `fallback_chain`, so callers import it from there as before.
"""

import re
from . import handoff, remark, safetyask, trouble, why
from .fallback_data import DONE_NOT_THIS, DONE_VERB, _THING_DONE_LINES

# The day that went badly and the name that came from somebody: the pools those readings choose
# from. They are in the data file with the rest, and the readings that use them live here.

# What the moved rows take from fallback.py, which is fully defined by the time this
# module is imported, because fallback.py imports it from its own last line.
from .fallback_part_01 import _plain
from .fallback_part_02 import reads_as_if_i_saw
from .fallback_part_04 import _a_plan_on_the_table, _the_line_cancels
from .fallback_part_05 import (
    HARM_ANYWHERE, _a_declined_plan, _a_verdict_line, _the_turn_before_was_a_heavy_one,
)
from .fallback_part_06 import _thing_done_scan
from .fallback_part_09 import _a_verdict_on_their_plan
from .fallback_part_11 import _a_place_asked_about
from .fallback_part_14 import _a_hard_week, reads_as_a_report
from .fallback_part_15 import _after_safety
from .fallback import DONE_NOT_THIS, DONE_VERB, _THING_DONE_LINES, handoff, re, remark, trouble, why
from .fallback_chain_part_03 import (
    _a_dish_name, _repaired_of,
)
from .fallback_chain_part_04 import (
    reply_for,
)


def _a_report_with_no_pronoun(clean, text, memory):
    """A thing done said without the "i": "booked the hotel last night", "paid the deposit".

    The dropped pronoun is what makes this the composer's line rather than the knowledge base's.
    A card cannot tell "booked the hotel last night" from "how do i book a hotel" - both hold the
    word "hotel" and the word "book" - but a past tense in the first word is a report, and the
    whole line is then a thing done with nothing to advise. A line with its subject ("i booked the
    hotel last night") is not this: the answers module can still tell it from the how-to, and the
    composer only takes what nothing else can read.
    """
    words = re.findall(r"[a-z']+", clean)
    if not words or words[0] not in DONE_VERB:
        return False
    if HARM_ANYWHERE.search(clean):
        return False
    if any(w in DONE_NOT_THIS for w in words[1:3]):
        return False
    if _a_dish_name(clean, words, memory):
        return False
    # The composer claims the line only when its own answer for it is the thing-done pool. A
    # report the gentle pools would answer keeps the knowledge base's answer: "signed the consent
    # form for the operation" is a thing done and an operation, and "That sounds rough" is worse
    # than the how-to it replaced. Asked of the composer's own reading rather than of a word list,
    # so a pool added here is covered without a second place to keep it.
    if _thing_done_scan(clean)[0] != "done":
        return False
    try:
        reply = reply_for(text, memory)
    except Exception:  # noqa: BLE001 - a composer that cannot answer claims nothing
        return False
    return reply in _THING_DONE_LINES


def takes_as_it_comes(text, memory):
    """Does the composer read this whole line, whatever any topic entry matching it says?"""
    clean = " ".join(str(text or "").lower().split())
    try:
        if reads_as_a_report(text, memory):
            return True
        # A regret the composer can meet is its own turn: the entries match the nouns of a line
        # ("i regret buying this car" reached the returns card on "car" and "buy"), and no card is
        # an answer to "i regret it". Only where the composer really has the line, so the claim is
        # as narrow as the reply (bot/compose/remark.py, `regret_reply_for`).
        if remark.regret_reply_for(clean, clean.split(), memory,
                                   _repaired_of(text, memory)):
            return True
        # A thing done with the pronoun dropped is a report, and the answer cards that hold its
        # words are instructions: "booked the hotel last night" reached the choose-a-hotel card
        # because nothing said a past tense is not a request for advice.
        if _a_report_with_no_pronoun(clean, text, memory):
            return True
        if why.takes_as_it_comes(text, memory):
            return True
        if _a_verdict_line(clean, memory):
            # A line that is only a verdict on the thing before it ("what a nightmare", "nightmare")
            # names nothing to look up, so no topic entry may take it on a word of it: the sleep
            # card answered "nightmare" after a job loss with the advice for dreams.
            return True
        if safetyask.reply_for(clean, memory):
            # "is it safe to keep it on tonight" is this module's question whatever a card
            # matches on the words of it: the repeat frame and the search shrug both answered it
            # before, and neither is a reply to somebody standing next to a dripping boiler.
            return not _after_safety(memory, clean, memory.get("understood"))
        if _a_verdict_on_their_plan(clean, memory):
            # A verdict asked for on the plan already on the table: the stock nod and the search
            # shrug both offered for it, and it wants neither. See _a_verdict_on_their_plan.
            return True
        # The place on the table, asked about in three words: "is it nice" after "we are going to
        # Cornwall in August". The line holds nothing to look up - the pool is only the words of
        # judgement - and the two replies it was getting were a sign-off ("Alright then - good luck
        # with it", because a three-word line with "nice" in it read as agreement) and the search
        # hedge. See _a_place_asked_about.
        if _a_place_asked_about(clean, memory):
            return True
        # "did you see it" is a conversation, not a read of what the person just said: the store
        # answered it "Yes - you watched the final together" at PRIORITY 7000, which is a true
        # sentence and no reply at all to somebody who wants to tell you about the match.
        if reads_as_if_i_saw(text, memory):
            return True
        # A short line that answers a question this composer has just asked is the next turn of
        # the same thread, whatever a card matches on one of its words: "since the baby" after
        # "what's it like at the moment?" was answered by the new-baby card. The claim is only as
        # wide as the reply - a question, a sentence with its own verb, a fault to repair and a
        # shrug are all left to the rest of the bot (bot/compose/trouble.py,
        # `answers_a_strain_question`).
        if "?" not in str(text or "") and trouble.answers_a_strain_question(clean, memory):
            return True
        # A plan the person has had to drop is the composer's line whatever else matched the nouns
        # in it: "gonna have to cancel" reached a plan pool ("Sounds like a plan. Tell me how it
        # turns out"), which answers a cancellation as if the person were looking forward to it.
        # The reading is the same narrow one the reply is built from, so a line that only uses the
        # verb in its other sense is not claimed ("i have to cancel my gym membership" keeps its
        # entry, `DECLINE_OTHER` and the tail rule in `_a_declined_plan`).
        #
        # Not when the thing dropped is already named in the chat and the line does not say
        # "cancel": "im going to the party on saturday" / "i cant make it" wants the words to say
        # to them, which the entry about telling somebody you cannot come already writes, and
        # "we booked a table for friday" / "cant make it tonight" wants what the booking card
        # knows. The composer's "do you want to rearrange it, or let this one go?" is the nod
        # beside a real answer (`_a_plan_on_the_table`).
        if (_a_declined_plan(_plain(clean), without_a_thing=True)
                # A feeling before the decline keeps its own answer, and the claim is what stops
                # one being proposed: "i had a panic attack" / "i cant come" was "no trouble at
                # all", and holding the turn for the composer took the panic card off the table.
                # A death or bad news is the exception, because the composer answers that one
                # gently and no entry does ("my wife is in hospital" / "i cant come" would go
                # back to the visiting-times card).
                and (_a_hard_week(memory)
                     or not _the_turn_before_was_a_heavy_one(memory, _plain(clean)))
                and not (_a_plan_on_the_table(memory) and not _the_line_cancels(_plain(clean)))):
            # Not while the bot is still with somebody in an emergency: there a "i cant come" is
            # the next turn of that thread, and the careful continuation is the reply (the same
            # shape as the hand-off hook below).
            return not _after_safety(memory, clean, memory.get("understood"))
        if not handoff.takes_as_it_comes(text, memory):
            return False
        # A hand-off is this module's to answer, unless the bot has just answered an emergency:
        # there the line gets the careful continuation instead, so the arbiter must not be told
        # the composer read it as a hand-off (the same shape as the #2494 hook fix).
        return not _after_safety(memory, clean, memory.get("understood"))
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return False


TAKES_AS_IT_COMES = takes_as_it_comes
