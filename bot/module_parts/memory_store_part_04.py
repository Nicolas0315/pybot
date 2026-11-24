"""Part 4 of 4 of a large module, split out of `memory_store`.

Everything here is re-exported from `memory_store`, so callers import it from there as before.
"""
import copy
import re

from ..compose import pick
from ..memory import thread, user
from ..memory import decided
from ..memory import counts as how_many
from ..memory import rates as rates_reader
from ..memory.times import is_a_time_ask as _a_plain_time_ask
from ..memory import recall
from ..memory import reminded
from ..memory import told as told_about
from ..memory import whathurts as a_hurting_part
from ..memory.when import when_answer
from ..memory import repeat as repeat_the_line


from ..memory.store_lines import POINTS_BACK_NOTHING, POINTING_WORD_NOTHING, WHAT_I_SAID_NOTHING
from .memory_store_part_01 import (
    NOT_A_FACT, recall, user, _note_a_pet_that_is_new, _the_limit_they_share, _the_pets_on_record,
    POINTS_BACK_AT_IT, WHOLE_ASK, WORK_ON_IT, _a_state_that_was, _a_whole_answer_to_hand_back,
    _bare, _can_close, _folded, _the_back_this_turn, _the_budget_on_the_answer,
    _the_call_from_the_advice, _the_prep_day, _the_same_fact_about_someone, _their_own_line_ask,
    decided, rates_reader, told_about, when_answer, _how_far_along, _the_ages_of_the_children,
    _the_places_are_written_as_names, _the_store_reply, _without_the_shrug_at_the_end, pick,
    BARE_WHAT_I_DO, _the_job_was_just_said, reminded, FACT_WORDS, after, re, _about_this_chat,
    _names_its_thing, _vary, thread, RECALL_WRAPPER, _halves, _longest, _names_minutes,
    _says_something, _sentences, CHECK_FOLLOWED, _plain_line, _reads_as_the_invitation, how_many,
)
from .memory_store_part_02 import (
    _an_ask_about_someone_else, _reads_the_store, _the_clock_in_their_line,
    _the_part_that_hurts_asked, _the_plan_they_took_back, _the_take_back_about_someone,
)
from .memory_store_part_03 import (
    _observe, _a_count_from_the_date, _a_feeling_about_their_own_news, _the_figure_the_answer_names,
    _their_fact_ask, _a_word_for_the_slot, _asks_to_hear_it_again, _the_ask_behind_the_recall,
    _the_time_they_put_right, _the_ask_about_how_it_went,
)


def _a_kept_fact_read(text, memory):
    """True when the line asks back a fact they gave, in whatever words, and the store has it.

    "my budget is 300" ... "im going to rome in may" ... "whats my budget" was answered with
    the cost of a day in Rome. The ask carries no topic of its own, so the arbiter read the
    conversation's topic on it and handed the turn to the module that declares that topic. A
    recall of a fact they gave is not about the topic in the air, so the store takes it as it
    comes - the same rule a plan asked for and the line they said already have.

    The key is read by `recall.ask`, which knows the shapes and not the store, so the fact has
    to be one the store really holds: with nothing kept the line is left to the entries, which
    can answer it as advice.
    """
    if not isinstance(text, str) or not (user(memory) or {}):
        return False
    try:
        if not recall.ask(text):
            return False
        said = respond(text, copy.deepcopy(memory))
    except Exception:  # noqa: BLE001 - a hook that raises must not lose the turn
        return False
    if not said or not str(said).strip():
        return False
    return NOT_A_FACT.search(str(said)) is None


def observe(text, memory):
    """Remember what the line says, and note a second animal of a kind as the turn's news.

    Everything below writes what the line says. This wrapper is here because the one thing the
    store does with the result is not a fact but the turn: a line that leaves the store holding
    two cats called Milo and Max is a line about the two of them, and the reply should say so.
    The wording is not read - "no my other cat is called max", "no we also have a cat called max"
    and "i also have a cat called tom" all file the second cat, and all three were left to the
    greeting, which answered with the person's own line and "Got it" in front of it. A rule per
    phrasing would have covered two of the three; the store's own record covers every phrasing.
    """
    before = _the_pets_on_record(memory)
    # The readers below file pets, and the line that names an animal files one even when it is
    # putting a name right ("no the cat is called max" in a house of two cats filed a third).
    # The set the turn before held is carried so that entry can be told from a pet of its own.
    memory["_pets_before"] = before
    hurt_before = a_hurting_part.before(memory)
    try:
        _observe(text, memory)
    finally:
        memory.pop("_pets_before", None)
    a_hurting_part.after(memory, hurt_before)
    _note_a_pet_that_is_new(text, memory, before)
    try:
        _the_limit_they_share(text, memory)
    except Exception:  # noqa: BLE001 - the store never crashes a turn
        pass


def _the_store_readings(text, memory=None):
    """The lines this store read for certain: a read of what it keeps, the ask whose answer is a
    line they said themselves, a `when` ask it can place, and a question about what the chat
    already holds. All are answered from what the person said, so a topic the knowledge base
    declares must not take the turn.

    This is a reading, not the hook: the exported name is `TAKES_AS_IT_COMES` at the end of the
    file, and it asks this one first. A module's name is bound once, at import, so a second `def`
    of the exported name is not an addition - it is a whole new hook, and everything under the
    first one stops answering without a single test going red.

    "when is that again" after "i've got a dentist appointment on tuesday" was answered
    "Same as before: Ring practices near you and ask straight out whether they take new NHS
    patients..." - the knowledge answer that happened to be the turn before, said again behind a
    repeat lead-in. The date is in what the person said, so this is the memory store's line and
    it says so in front of it. Every ask it cannot place is left alone.

    "have we talked about food" is the same kind of line: the answers lane proposed from the word
    `food` and won before the store was asked, so the person asking the bot to remember got a
    recipe list instead.
    """
    if (_reads_the_store(text, memory) or _their_own_line_ask(text, memory)
            or _the_part_that_hurts_asked(text, memory)
            or _their_fact_ask(text, memory)
            or _a_kept_fact_read(text, memory)
            or decided.asks(text)
            or told_about.ABOUT_THE_CHAT(text, memory)
            or told_about.A_CALLBACK(text, memory)):
        return True
    if WHOLE_ASK.match(str(text or "").strip().lower()) \
            and _a_whole_answer_to_hand_back(memory, text):
        # "in full", "the whole thing", "all of it": the line names no thing of its own, so the
        # specialist rule read the chat's topic on it and handed the turn to an entry that folded
        # "the full" as a thing ("The same goes for the full: If you forget, keep a filled bottle
        # ...") instead of the answer the person asked for again. `_repeat_ask` already reads this
        # ask - it is the same `WHOLE_ASK` and the same "is there a whole answer behind it" test
        # that keeps "hi" / "in full" with the small talk - but nothing asked it from here, so the
        # store never claimed the line.
        return True
    if _a_state_that_was(text, memory, ""):
        # A pregnancy or a feeding that is over is this store's line and nobody else's: the
        # knowledge base reads the word "pregnant" and serves the trying-for-a-baby entry, and the
        # news reader congratulates a state that has passed. The store has nothing to file for it,
        # so it only says the tense back.
        return True
    if _a_feeling_about_their_own_news(text, memory):
        # A bare feeling is about the thing they said a moment ago, which is a read of this store
        # and nothing the knowledge base or the small-talk topics know about.
        return True
    if _the_plan_they_took_back(text, memory):
        # A where ask whose trip was taken back the turn before, answered by the store that knows
        # it went rather than by the paragraph that was just taken off the record.
        return True
    if _the_take_back_about_someone(text, memory):
        # "he isnt allergic to nuts" one line after "my son is allergic to nuts": the topic is
        # nuts and the line is about the chat, so the entry that knows nuts must not take it.
        return True
    if _can_close(text, memory):
        # A line that asks to leave the subject is not about the subject, so the entry that knows
        # it must not take the turn ("can we talk about something else" after a hospital line was
        # answered with a care assessment). The store knows what the subject was, so it answers.
        return True
    if _the_call_from_the_advice(text, memory):
        # A decision the answer above already settled: the line names no subject of its own, so
        # the specialist rule would read the chat's topic on it and hand the turn to that entry.
        return True
    if _asks_whether_we_followed(text, memory):
        # "did you get that" names nothing of the world, so the specialist rule read the chat's
        # topic on it and the knowledge entry that topic belongs to took the turn - the person
        # asking whether the bot had followed got a lookup. The store knows what it kept.
        return True
    if rates_reader.is_a_rate_ask(text, memory):
        # The ask for a rate this store holds: "how often do i go to the gym" after "i go twice a
        # week". The exercise entry answers from the guideline a person should keep, which is the
        # wrong answer to someone who told this store their own.
        return True
    if _a_plain_time_ask(text, memory):
        # The ask for the hour their own day runs on ("what time do i get up" after "i get up at
        # seven"). The sleep entry answers from the routine a person should keep - "work it back
        # from the morning" - which is the wrong answer to someone who told this store their own
        # hour: the line names one of the times on file and nothing of its own, so the store
        # answers it.
        return True
    if _an_ask_about_someone_else(text, memory):
        # The fact is in this store, filed under the person the line named: the knowledge base
        # has nothing about their sister's allergy.
        return True
    if _the_group_size_ask(text, memory):
        # How many the person's own group is, when this store holds the number: "how many of us"
        # after "we are four of us" was answered with the dish card the cooking topic had in hand
        # ("Quick: tuna pasta in 15, macaroni cheese in 25..."), one turn after the person had
        # said how many they were. The number is kept here, so the topic must not take the line.
        return True
    if repeat_the_line.how_long_its_been(text) and repeat_the_line.the_figure_they_gave(
            text, memory):
        # The length they gave about their own thing, asked back with the thing named: "how long
        # has my back been like this now" after "my lower back has been sore for about 3 weeks".
        # Claimed here because the carry into the card that answers a back took the turn and said
        # what keeps a back quiet, while the three weeks were in the chat.
        return True
    if _the_figure_the_answer_names(text, memory):
        # A figure ask that names no thing ("how many weeks" after the training answer) is read
        # off the answer the person just read, and `respond` says that figure. Claimed here
        # because a card the bare unit reaches answers it with a length of the wrong kind, and a
        # hook that says yes on a line `respond` answers differently would take the turn off the
        # module that should have had it.
        return True
    if _the_budget_on_the_answer(text, memory):
        # How much time there is is not a new question: it is the room the answer above has, and
        # read as a question the knowledge base took it for one - "and i only get 20 minutes"
        # after the lunch answer reached the eggs, the fastest dinner there is.
        return True
    if _the_back_this_turn(text, memory):
        # The line that puts back what somebody else does not eat is the store's own: only the
        # store knows what it lifts, and the small talk answered it with "Got it - he eats fish."
        # while the diet it lifts stayed on his record and came back on the next ask.
        return True
    if _the_same_fact_about_someone(text, memory):
        # "and my wife is too" after "im allergic to nuts" carries no subject of its own, so the
        # specialist rule read the chat's topic on it and handed the turn to the entry about that
        # diet ("same for my wife" after "im vegan" came back as the vegan amounts). The fact the
        # "too" points at is this store's, and the note it makes is kept with the reply, so the
        # store says so in front of it.
        return True
    try:
        if not isinstance(text, str) or not isinstance(memory, dict):
            return False
        line = _bare(_folded(text, memory))
        if (POINTS_BACK_AT_IT.search(line) or WORK_ON_IT.search(line)) \
                and not _the_prep_day(memory, line):
            # An ask that puts a verb on the thing ("to prep for it", "to book it") is answered by
            # the plan only when the store can name the day the work for it goes on. The plan said
            # back on its own is their own line again, and that echo was landing on the asks the
            # knowledge base has a real answer for ("when is the best time to book it" after a
            # Rome trip came back "You're going to rome in may."), so those are not claimed here.
            # "when is that again" is not this shape: the pointing word is the whole ask, not the
            # object of a verb, and the date they gave is the answer it wants.
            return False
        if _the_clock_in_their_line(text, memory):
            # "what time is my appointment" is the hour they gave, so it is not a question about
            # how to get an appointment. Read before the "when" gate because the line says
            # "what time" and that is the same ask.
            return True
        if "when" not in text.lower():
            return _a_count_from_the_date(text, memory)
        return bool(when_answer(text, memory))
    except Exception:  # noqa: BLE001 - a module that cannot claim declares nothing
        return False
        return False


def respond(text, memory):
    """The store's reply, with the names in it written as the store holds them.

    A plan is quoted back in the words they typed, so a name in it came back in their spelling:
    "we r going 2 spain in may" -> "You r going 2 spain in may.". Every route out of the store
    ends here, so the names are written once, at the end.

    Then the floor under it: never the same words twice in a row. The store answers each line on
    its own terms, so two different lines can be answered by the same words - "is she vegan" and
    then "what does my mum eat" both reached the one line the store writes about a diet nobody
    gave, and the person read the same sentence twice. Whatever route the reply came by,
    `bot/memory/again.instead` frames it as the repeat it is - after the names are written, so
    the words it compares are the words on the screen.
    """
    from ..memory import again as same_again
    from ..memory import not_this
    from ..memory import trips
    text = _without_the_shrug_at_the_end(text)
    # A line that only moves a time the store already holds ("i meant seven") is answered by the
    # store: nothing else has anything to say about it, and what did say something handed the
    # person a shrug or the search hedge over a correction the store had just taken.
    put_right = _the_time_they_put_right(memory)
    if put_right:
        return put_right
    # A line that points back at what was said before, in a chat with nothing in it yet ("same as
    # before", "and the other one"): nothing below reads it, and the small-talk pools answered it
    # with a receipt of a line nobody had given. There is no before to go on, so the store says so
    # and asks for the thing itself - read here, above every reader, because on a chat that has
    # said something these lines are theirs and go on being read exactly as they were.
    pointed_at_nothing = _points_back_at_nothing(text, memory)
    if pointed_at_nothing:
        return pointed_at_nothing
    # A recall frame with nothing behind it: "what did i say about it", "what did i say i lost".
    # Read above the pointer asks, because the pointer reader read the "it" in the recall and
    # answered a request for their own words as a question about a subject.
    recall_frame = _a_recall_frame_about_nothing(text, memory)
    if recall_frame:
        return recall_frame
    # An ask whose only subject is a pointing word, in a chat with nothing behind it: "how do i
    # do it", "how long will it take", "do that again". The "it" has no thing to be yet, and the
    # turn was answered with a search hedge ("I'm not sure about that one, sorry - I'd rather not
    # guess") or a shrug ("Fair enough."), neither of which asks the one question that would let
    # the person get an answer.
    ask_about_nothing = _an_ask_about_nothing(text, memory)
    if ask_about_nothing:
        return ask_about_nothing
    # "how am i doing" with a figure for the plan in the chat is answered from that figure
    # (`bot/memory/goals.py`). Without it the line is a question about a diet in general and the
    # knowledge base's paragraph stands - and on a chat about a half stone that paragraph was an
    # arithmetic card ("Divide it by 2: half of 46 is 23..."), which answers a question nobody
    # asked. Both halves are needed: a line that is not this ask, or a chat with no figure, gets
    # Nothing from here and goes on exactly as it did.
    from ..memory import goals as _goals_progress
    going = _goals_progress.a_progress_asked(text, memory)
    if going:
        return going
    # An ask about what they said or were worried about, in a chat that has said nothing: "what was
    # it i was worried about". Read as a line about a worry it got advice about worrying ("Write
    # down what's actually at stake"), which invents a feeling nobody named.
    recall_about_nothing = _a_recall_about_nothing(text, memory)
    if recall_about_nothing:
        return recall_about_nothing
    # "what did i say her birthday was" is the direct ask with a wrapper round it, and the reader
    # that keeps that slot answers it; read as a topic instead, the last line they said about
    # anything came back as if it were the answer.
    behind = _the_ask_behind_the_recall(text)
    if behind:
        direct, attribute, possessive = behind
        answer = respond(direct, memory)
        if answer:
            return answer
        if _a_word_for_the_slot(memory, attribute):
            # They said it in a shape the slot reader does not read ("hes a labrador, 9 weeks
            # old" is an age the store never filed), so a line saying they never told me would
            # deny what they said. The store's own reply to the line as asked quotes it instead,
            # and that is the honest answer.
            behind = None
        else:
            # Nothing is filed for that slot: the honest line is that, since the reader for it
            # has just said it holds nothing, and a line about something else is not an answer.
            theirs = "your" if possessive in ("my", "our") else possessive
            return pick(["You haven't told me " + theirs + " " + attribute + ".",
                         "I don't have " + theirs + " " + attribute + " from you yet.",
                         "You haven't mentioned " + theirs + " " + attribute + " to me."], memory)
    # The ages of the children the store counts, given one at a time ("ones 7 and ones 4" after
    # "i have two kids"): the line names no group, so nothing else reads it and the store's own
    # echo said the line back while keeping nothing.
    ages_of_the_children = _the_ages_of_the_children(text, memory)
    if ages_of_the_children:
        return ages_of_the_children
    # A line that only rules a place out is not a line about that place: it is answered first,
    # because every reader below would answer about the place they had just taken back.
    ruled_out = not_this.reply_for(text, memory)
    if ruled_out:
        return ruled_out
    told_about_the_trip = trips.reply_for(text, memory)
    if told_about_the_trip:
        # A trip said plainly, or a detail added to one the conversation is on, is answered
        # about the trip: the month it is in, the people going, and how the journey goes. Read
        # here rather than inside the store's own reply so it comes before every reader below
        # that would answer the trip's subject instead.
        return told_about_the_trip
    # A length the person gave about their own life, asked back with nothing named ("how long
    # has it been" three turns after "my back has been bad for a week now", "how long have i had
    # it now" after "i started running two weeks ago"). The unit reader below reads only a line
    # that names its unit ("how many weeks"), so this shape fell past it and the answer on the
    # screen was quoted instead - a length of something else entirely. Their own words are the
    # answer while the length is in the chat.
    if repeat_the_line.A_BARE_DURATION_ASK.search(" ".join(str(text or "").lower().split())):
        theirs = repeat_the_line.the_figure_they_gave(text, memory)
        if theirs:
            return theirs
    if repeat_the_line.A_PAY_WORD.search(" ".join(str(text or "").lower().split())):
        # An ask for pay names its figure in a word the unit reader has no family for: "how much
        # is my wage" names no unit at all, and "how much do i make" names its pay in a verb the
        # keywords drop. So the wage the chat holds was read back only when the ask happened to
        # carry a unit word, and the person asking for their own pay got the budgeting card. The
        # figure they gave is the answer to any ask for it, and the reader below is where the
        # judgement words that make it a different ask are refused.
        theirs = repeat_the_line.the_figure_they_gave(text, memory)
        if theirs:
            return theirs
    if repeat_the_line.how_long_its_been(text):
        # The same ask with the thing named instead of "it" ("how long has my back been like this
        # now"): the unit reader names the back and stands down, so the store says the figure the
        # person gave, which is what the line asked for.
        theirs = repeat_the_line.the_figure_they_gave(text, memory)
        if theirs:
            return theirs
    figure = _the_figure_the_answer_names(text, memory)
    if figure:
        # The figure the answer on the screen named, on a line that asks for nothing else: said
        # back as the figure, because the sentence it is in is one the person has just read.
        return figure
    # A length ask about a pregnancy the chat holds is answered here, before the figure they gave
    # is looked for: "how many weeks am i" is a count of weeks in a line of theirs, so the reader
    # for a figure said back took it ("You said 12 weeks.") where the number they gave is the
    # length of their pregnancy and is said as one ("Twelve weeks.").
    along = _how_far_along(memory, _bare(_folded(text, memory)))
    if along:
        return along
    theirs = repeat_the_line.asked_back(text, memory)
    if theirs:
        # A recall ask about a figure of their own is answered from the line they gave it on,
        # before any entry is looked up for the thing it names. "how long am i going for" after
        # "we fly out on the 12th for 10 days" reached the departure card and answered about
        # getting to the airport two hours early, and "how many nights did i say" answered with
        # when to book flights - both while the nights and the days were in their own line. The
        # reader is narrow (bot/memory/repeat.py, `asked_back`): a recall cue, a short line, the
        # thing named in a line they said, and one figure of the kind asked for.
        return theirs
    reply = _the_store_reply(text, memory)
    if not isinstance(reply, str) or not isinstance(memory, dict):
        return reply
    reply = _the_places_are_written_as_names(reply, memory)
    # Two lines are the ones whose repeat is the point. A line that asked for the whole of the
    # answer: the reply opens "All of it:" because the person asked for that, so framing it
    # again as "Same answer, and it covers this:" takes the lead-in off and says the bot decided
    # to repeat itself - "my name is sam" / "all of it" came back as that, about a greeting.
    # And a request to hear the answer again, which is handed the words and not a note that they
    # were said before: the never-twice rule is about answering twice, not about being asked
    # twice.
    if not WHOLE_ASK.match(str(text or "").strip().lower()) \
            and not _asks_to_hear_it_again(text, memory):
        framed = same_again.instead(reply, text, memory)
        if framed:
            return framed
    return reply


def TAKES_AS_IT_COMES(text, memory=None):
    """Claim every line the store can answer - the bare "what do i do" included.

    The arbiter reads one `TAKES_AS_IT_COMES` per module and the last `def` in the file is the one
    it reads, so a hook written above this one is not read at all: its line goes unclaimed, and the
    specialist rule hands it to whatever entry the topic fits. That is what happened to the store's
    own readings for a while ("my son is 5" then "is my son 5", "he isnt allergic to nuts", a plan
    asked about by "when"), which is why every reading now has a private name and is asked from
    here, at the end of the file, rather than from a hook of its own.

    The job ask is the last reading: the bare "what do i do" said right after the person gave their
    job is the fact, whatever else read. The line names nothing, so the understanding engine hands
    it the topic of the turn before, and a knowledge entry for that trade answers it: an answer
    about the entryways into nursing, given to someone who already is one and only asked what they
    do. The store's reading is the one that answers what they asked, and it wins the turn on this
    line alone. False everywhere else - a turn later the same words ask about whatever the chat has
    moved on to.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return False
    if memory.get("moved_to_who") == " ".join(text.lower().split()):
        # "sorry i meant my daughter is a nurse": the fact moved from one person to another, and
        # the store said which. An entry that reads the word "sorry" answers it as a request for
        # the apology script, so the store's line takes the turn on this line alone.
        return True
    if _the_store_readings(text, memory):
        # Every reading the store had before this one lives in `_the_store_readings`, and it is
        # asked from here because this is the only `def` of the exported name: a second one above
        # would replace this hook at import and every reading under it would stop answering.
        return True
    if told_about.A_CALLBACK(text, memory):
        # "remember when i said my knee hurt": the store is the part that can say what was
        # actually said, and an entry that reads the word in it ("knee") would serve the advice
        # again. This hook is the one the arbiter reads - the store has an older definition
        # above, which no longer runs - so the claim is made here.
        return True
    if _the_ask_about_how_it_went(text, memory):
        # The thing they did today and the ask about how it went: only they can say how it went,
        # so the store answers by asking them. An entry about the thing would answer the question
        # nobody asked - "interview" is a word in the line, not what the line is about.
        return True
    if _a_callback_that_names_its_thing(text, memory):
        # "my boiler keeps losing pressure", then "what have i been saying about the boiler": the
        # line is about the conversation and the store's line answers it. The reading still gives
        # it a topic - a boiler is home-and-diy - so the specialist rule lifted the boiler entry
        # over the recall band, and the person who asked what they had said was told how to set
        # the flow temperature on the dial. "my kitchen tap drips" then "what have i been saying
        # about the kitchen" got a traybake the same way.
        #
        # Only the store's own gate for "this line is about the conversation", and only with the
        # thing named after "about": "what were we on about" and "what was i saying" name nothing,
        # and "when should i get the boiler serviced" names a boiler without being about the chat.
        return True
    if reminded.about_a_thing_they_said(text, memory):
        # "my boiler keeps losing pressure", then "what was wrong with my boiler again": the
        # past tense and the "again" make it a reminder about the line they said, and read as a
        # question about the world it was a fault to diagnose - the boiler entry answered it
        # with the flow temperature, a turn after the person had told us what was wrong.
        # The reading is `bot/memory/reminded.py`, and it is the same one the store's gate for
        # "this line is about the chat" uses, so the two cannot disagree.
        return True
    if not BARE_WHAT_I_DO.match(_bare(_folded(text, memory) or text)):
        return False
    return bool(user(memory).get("job")) and _the_job_was_just_said(memory)


def _a_fact_word(low):
    """True when the thing a callback names is one of the facts the store keeps."""
    after = re.search(r"\babout\b\s+(.+)$", low or "")
    words = set(re.findall(r"[a-z]+", (after.group(1) if after else "").lower()))
    return bool(words & FACT_WORDS)


def _a_callback_that_names_its_thing(text, memory):
    """True when the line asks about the conversation and names the thing it asks about.

    "what have i been saying about the boiler" is a recap by name (`_about_this_chat`, the reading
    the store answers with) and the name is what makes it about that thing rather than the chat as
    a whole (`_names_its_thing`). Both, because either on its own is too wide for a claim: a line
    that names nothing is the chat's own topic, and a line that names a boiler is not a recap
    unless the store read it as one.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return False
    try:
        low = " ".join(text.lower().split())
        return bool(_names_its_thing(low) and _about_this_chat(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False


def _points_back_at_nothing(text, memory):
    """The store's answer to a pointer with nothing behind it, or None when it is not that line.

    "same as before" as the first thing in a chat is not a request the store can answer from what
    it holds, and it is not small talk either: it is the person picking up a conversation that is
    not there. Saying that plainly is the answer, and it is the same answer NOTHING_STARTED gives
    to "what have we talked about" - so a chat that opens this way gets a line that names the
    missing thing and asks for it, not a welcome and not a receipt.
    """
    if not thread.points_back(text) or not thread.nothing_said(memory):
        return None
    return _vary(POINTS_BACK_NOTHING, memory)


def _a_recall_about_nothing(text, memory):
    """The store's answer to "what was it i was worried about" with nothing said, or None.

    The line names no slot and no fact: it asks the chat to give back something that was never
    put in it. The readers below all want a thing to look for, so none of them reads it, and it
    fell through to the chatter band as a line about a worry.
    """
    if not thread.asks_what_i_said(text) or not thread.nothing_said(memory):
        return None
    return _vary(WHAT_I_SAID_NOTHING, memory)


# The same ask for their own words in shapes the wrapper does not reach: an order ("tell me what
# i said"), a yes/no recall ("did i say anything about it"), a frame whose subject is named as a
# thing ("what was the thing i said"), and a reminder of something that is not there ("remind me
# what that was"). Each is the ask for their own words and each named no slot, so no reader below
# read it: the turn went to the search hedge or to the pool for an ask about a thing.
A_RECALL_IN_ANOTHER_SHAPE = re.compile(
    r"^(?:and|so|but|also|again|ok|okay|well)?\s*(?:"
    r"tell\s+me\s+what\s+(?:i|we)\s+(?:said|say|told\s+(?:you|u)|tell\s+(?:you|u)|mentioned?)\b"
    r"|(?:did|do)\s+(?:i|we)\s+(?:say|tell\s+(?:you|u)|told\s+(?:you|u)|mentioned?)\s+"
    r"(?:anything|something|much)\b"
    r"|what\s+(?:was|were)\s+(?:the\s+thing|that\s+thing|that)\s+(?:that\s+)?"
    r"(?:i|we)\s+(?:said|told\s+(?:you|u)|mentioned?)\b"
    r"|remind\s+me\s+what\s+(?:that|it|this|those|they)\s+(?:was|were|is|are)\b"
    r")", re.I)


# What may follow such an ask and still name nothing of its own: the pointer, the words that stand
# for a thing nobody has named ("anything", "something", "the thing"), the little words, and the
# auxiliaries. A word outside these is a thing ("about the boiler"), and that line has a reader of
# its own that names the thing back ("You haven't mentioned the boiler").
RECALL_NAMES_NOTHING = frozenset("""it that this them those these one ones there anything something
much thing things about of on in at to for from with the a an was were is are be been being
i we you u he she they me us my our his her their said say told tell mention mentioned mentioning
and or so but also again then just really actually exactly then""".split())


def _names_nothing_in_a_recall(rest):
    """True when what follows a recall ask names no thing of its own."""
    words = re.findall(r"[a-z]+", str(rest or "").lower().replace("'", ""))
    return not [word for word in words if word not in RECALL_NAMES_NOTHING]


def _a_recall_frame_about_nothing(text, memory):
    """The store's answer to "what did i say about it" with nothing said, or None.

    The recall frame - "what did i say", "what did i say about that", "what did i say i lost" -
    is the ask for their own words, and it is that whatever the frame is filled with. The "it"
    or the "that" inside it is not a thing the chat could name: the person is asking what they
    themselves said, so there is nothing to give them, and saying that is the answer.

    Read before the pointer asks, because the pointer reader looked at the same "it" and answered
    a request for the chat's own words as if the person had asked a question about a subject
    ("Nothing said yet for that to be: tell me the thing itself..."). A rule-out, not a new pool:
    it hands back the same WHAT_I_SAID_NOTHING line the feelings recall gets.
    """
    if not thread.nothing_said(memory):
        return None
    low = " ".join(str(text or "").lower().replace("'", "").split()).strip(" .!?,")
    wrapped_low = " ".join(str(text or "").lower().split()).strip(" .!?,")
    # The shapes of the ask that no slot reader reaches, kept to the ones that name no thing: a
    # line that does name one ("did i say anything about the boiler") has a reader below that says
    # the thing back, which is the better answer.
    another = A_RECALL_IN_ANOTHER_SHAPE.match(wrapped_low)
    if another and _names_nothing_in_a_recall(wrapped_low[another.end():]):
        return _vary(WHAT_I_SAID_NOTHING, memory)
    wrapped = RECALL_WRAPPER.match(wrapped_low)
    if not wrapped:
        return None
    # Only where what the frame is filled with is a pointer and nothing else: "about it", "about
    # that". A person or a thing named inside the frame ("what did i say her birthday was", "how
    # old did i say he was") is a slot one of the readers below keeps, and those answer with the
    # slot that is empty, which is a better line than this one.
    rest = wrapped.group("rest")
    if not thread.POINTING_WORD.search(rest) or len(re.findall(r"[a-z]+", rest)) > 2:
        return None
    return _vary(WHAT_I_SAID_NOTHING, memory)


def _an_ask_about_nothing(text, memory):
    """The store's answer to an ask about nothing at all, or None when it is not that line.

    "how do i do it" as the first line of a chat names one thing - the "it" - and the chat holds
    nothing it can be. Nothing below reads the line: no fact is asked for, no plan is stated, so
    the turn went to a search hedge over a question the person could be helped with in one line.
    The same goes for "do that again" and "is it worth it". The answer says the thing is missing
    and asks for it, which is what a friend does with a question whose subject they never heard.
    """
    if not thread.points_at_a_word_alone(text) or not thread.nothing_said(memory):
        return None
    # A line that is nothing but pointing words ("what does that mean", "how does that work") is
    # already read by the composer, which asks for the thing itself in its own words. Two pools
    # answering one shape is two voices for the same turn, so the composer keeps that one and
    # this reading is only for the pointer asks its word list does not reach.
    from ..compose import fallback
    if fallback._points_at_nothing(text, memory):
        return None
    return _vary(POINTING_WORD_NOTHING, memory)


def _the_last_ask_about_the_bot(memory):
    """The last thing they asked about the bot, as a sentence, when that is all they have said.

    A chat that opens "are you a real person" and then asks what we have talked about has nothing
    of theirs to go back over - but "nothing yet" is not true either, because they asked something.
    The question is said back in their own words ("whether I am a real person") as the one thing
    the chat has covered, which is what a friend would say.
    """
    for text, reading in reversed(list(thread.user_lines(memory))):
        if not (isinstance(reading, dict) and reading.get("about_bot")):
            return None
        asked = thread.restate(text)
        if asked:
            return asked
    return None


def _fits(answer, room):
    """The move of an answer whose own length is the largest one that still fits `room`.

    The largest that fits, not the shortest: somebody with 20 minutes wants the twenty-minute way
    of doing it, not the two-minute half of a paragraph that is about something else.
    """
    best, best_seconds = None, -1
    names = _names_minutes(answer)
    for sentence in _sentences(answer):
        for part in _halves(sentence):
            took = _longest(part, bare=names)
            if took is None or took > room or not _says_something(part):
                continue
            if took > best_seconds:
                best, best_seconds = part, took
    return best


def _asks_whether_we_followed(text, memory):
    """True when the whole line asks whether the last thing they said was taken in."""
    if not isinstance(text, str):
        return False
    low = _plain_line(_folded(text, memory) if isinstance(memory, dict) else text)
    if not low:
        return False
    if low.endswith("?") :
        low = low[:-1].strip()
    # The same words asked about the world: "did you see it" after "we watched the final
    # together" asks whether the bot was at the match, not whether it took the line in, and
    # reading their own evening back to them ("Yes — you watched the final together") is a true
    # sentence and no answer at all. The composer already reads that line as the invitation it
    # is, so the store stands down exactly where the composer answers (bot/compose/fallback.py,
    # `reads_as_if_i_saw`) and every other check keeps this reading.
    if _reads_as_the_invitation(low, memory):
        return False
    return bool(CHECK_FOLLOWED.match(low))


def _the_group_size_ask(text, memory):
    """Whether this is a question about how many the person's own group is, and the number is kept.

    The ask has to be about the group itself - "how many of us", "how many people are there",
    "how big is my family" - and never about how many are going somewhere ("how many of us are
    going to the park"), which `counts.GROUP_ASK` already tells apart. Nothing is claimed unless
    the store actually holds a size, so a "how many people" with nothing said before it keeps
    whatever answer the line has of its own.
    """
    low = str(text or "").lower()
    # The ask may name the group ("how many of us") or point back at the number with nothing else
    # said ("how many was it", "how many again"): both are the size this store is holding, and the
    # bare one was otherwise handed to the answers module, which read "how many was it" as a
    # figure off the last card.
    # "how many people is it for" is not in here: the roast card answers it with the rate a
    # table of that size needs, and the number said back is a poorer answer to the same ask.
    if not (how_many.GROUP_ASK.search(low) or how_many.BARE_COUNT_ASK.search(low)):
        return False
    return bool(how_many.answer(text, memory))
