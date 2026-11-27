"""Part 10 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re

from .. import memory as mem
from ..compose import lead, with_name
from ..knowledge import pets, shopping, work
from ..knowledge.lookup import find
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import deadline, healing, named, narrow as length, prefer, repeat, when
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import hope as a_wish, matters
from ..memory import a_year_of_birth
from ..memory import doing_it
from ..memory import repeat
from ..memory import stuck as stuck_line
from ..memory import again as same_again  # the short of an answer already on the screen
from ..memory.again import AGAIN_HELP
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory import repeat
from ..memory import topics as said_topic
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import repeat, tried, more
from ..memory import returns as went_back
from ..memory import limit
from ..memory import whereabout
from ..memory import price as a_price
from ..memory import answers_about_another_creature, the_animal_the_subject_is
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory import repeat
from ..memory.narrow import SIGNALS, kind_of as asked_kind
from ..understanding import understand
from .answers_part_01 import (
    _first_step, _flat, AGAIN, ASKS_ABOUT_HOW_IT_TURNED_OUT, A_PLEA_FOR_TIPS, NOTHING_SEPARATE,
    _a_fact_about_the_person, _a_part_named_in_the_line, _answer_said, _most_of_it_said, _named_in,
    _said_before, _same_as_the_last_answer, _short_form_of_the_last, _the_part_in_the_answer,
    _the_same_answer_in_other_words, _their_own_state, WORD,
)
from .answers_part_02 import (
    _A_DURATION, _answers_a_length,
)
from .answers_part_03 import (
    _remember_answer, _the_one_to_pick,
)
from .answers_part_04 import (
    _the_sentence_about,
)
from .answers_part_05 import (
    _the_sentence_owed, _payload,
)
from .answers_part_06 import (
    _only_a_quality_name, _repeat_short, _the_detail_named,
)
from .answers_part_07 import (
    _asks_only_the_length,
)
from .answers_part_08 import (
    THEIR_OWN_ASK, _a_bare_thanks, _a_judgement_of_the_figure_on_the_table, _a_limit_on_the_plan,
    _fitted_to_what_they_eat, _keep_the_answer, _the_dish_by_name,
    _the_line_asks_what_this_one_meant, _the_sentence_it_names, _of_its_own, BARE_SAY_NO,
    TAKEN_BACK_OPENER, _A_YES_NO_ASK, _a_case_of_the_answer_in_hand, _a_city_card_asks_which_first,
    _a_lead_time, _the_answer_in_front, _the_entry_names, _the_fact_is_what_is_answered,
    _the_line_again, _the_part_is_what_answers, _the_practice_is_answered, _the_report_is_answered,
    _the_same_answer_again, _the_thing_has_got_better, _without_lead_in, _A_CLAUSE_OF_THE_ANSWER,
    _A_HOW_LONG, _names_a_repair, _the_line_already_has_its_answer, _the_plan_said,
    _ATTACHED_TO_THE_LAST_TURN, MOAN_STOP, MOAN_VERB_WORDS,
)
from .answers_part_09 import (
    _A_BARE_MEASURE, _a_complaint_answered, _a_length_ask_with_no_figure, _respond,
    _the_answer_on_the_table,
)


def respond(text, memory):
    """The knowledge base's reply, with the name the person just gave in front of it.

    A line that is only the thing again with "still" on it is not a new subject for whatever
    card its one word opens - "still cold" after "my shower is cold" is the shower, not the
    common cold - so the store's reading of it keeps the turn (`bot/memory/tried.py`).

    A line that greets the bot and says what they are doing ("hi im jess, im saving for a car")
    is answered by the entry - the substance - and the greeting is the part an entry cannot see,
    so the composer puts the name in front of the answer rather than letting a welcome take the
    turn (`bot/compose/__init__.py::with_name`).
    """
    from ..memory import not_this as _ruled_out
    from ..memory import portions as _portions
    from ..memory import size as another_size
    from ..memory import trips as _trips
    from ..memory.thread import only_the_arrival as _only_the_arrival
    from ..compose import said_about_me
    if isinstance(memory, dict):
        # The line as the person typed it, for the rows that have to tell the words of this line
        # from the earlier subject written into it: a follow-up is read with the thing the talk
        # is on put into it, so "can i freeze it" reads as "im making a chilli tonight can i
        # freeze it", and a card keyed on the added word then answers a line that never said it.
        # See `bot/knowledge/lookup.py::said_in_this_line`.
        memory["asked_now"] = text
    if _only_the_arrival(text):
        # "im back", "back from work", "we are back home": nothing in it but the arrival. A chat
        # with a bad knee in it answered the word "back" as the part, and the arbiter prefers an
        # answer to the composer's "Welcome back. Where were we?", so the person who came back
        # from the shop was told about a back that gives trouble on and off. The return is the
        # composer's line, not the knowledge base's, so this module stands down for it.
        return None
    # A remark that comes back with a frequency on it - "she says it every time i visit" after "my
    # mum says im not trying hard enough" - was answered out of the card the bot's own reply put in
    # the thread ("Agree the length before you go... two nights is plenty for most trips"), because
    # that reply said "mum" and this line says "visit". It is still about the remark, so the
    # sentence that answers a pattern takes the turn and this module stands down
    # (bot/compose/said_about_me.py, `answer_followup`).
    if said_about_me.answer_followup(text, memory):
        return None
        return None
    if _trips.THE_JOURNEY_ASK.search(text or "") and _trips.reply_for(text, memory):
        # A journey asked as a question while a trip is live is the trip's line. "how long will it
        # take to drive" after "we're going to cornwall in july" was answered here by the driving
        # entry - 45 hours of lessons, a test in six months - which is about learning to drive and
        # not about the trip. The trip reader has the reply, and the store leads the turn with it.
        # Only this shape is given up: the rest of the trip's detail questions (what to pack, what
        # to book first) are what the knowledge base is best at.
        return None
    if _the_line_asks_what_this_one_meant(memory):
        # "what do you mean" names nothing of its own: it points at the answer just given, and
        # the store says that answer again ("Just this: Top the pressure up to between 1 and 1.5
        # bar"). Read as a follow-up, the knowledge base reached the subject of the last answer
        # instead and took the word "mean" for the thing named: after "my tomato plants have
        # blight", "wot u mean" was answered "The same goes for the wot u mean: cut off and bin
        # the affected leaves" - the person's own slip said back at them as the subject - and
        # the arbiter prefers a card to the composer's line, so that is the reply they got. The
        # reading knows the shape in every spelling (`understood["asks_what_was_meant"]`), so
        # this module stands down for it rather than keeping a list of its own.
        return None
    if _a_judgement_of_the_figure_on_the_table(text, memory):
        # The line only holds a figure up ("is 2000 too much" after the price of a bike, "is that
        # expensive" after a kitchen quote): what it asks for is the comparison, which the reading
        # has already made, and this module's card says the price range over again instead of
        # answering. See `bot/compose/reading.py` (the reading) and `_doubt_and_answer`.
        return None
    if THEIR_OWN_ASK.search(text or ""):
        # A line that asks for their own words is the conversation's, not the knowledge base's.
        return None
    if repeat.A_PAY_WORD.search(" ".join(str(text or "").lower().split())) \
            and repeat.the_figure_they_gave(text, memory if isinstance(memory, dict) else {}):
        # An ask for their own pay is the store's, and the card it reached was about the shape of
        # a weekly wage rather than about this person's: "i get paid 2000 a month" then "how much
        # is my wage" was answered with the budgeting-a-weekly-wage lesson while the wage was in
        # the chat. The store says the figure, so no card is the answer to the ask.
        return None
    if (_portions.an_ask(text or "", memory) or _portions.a_count_to_fill(text or "", memory)
            or _portions.a_bare_count_to_fill(text or "", memory)):
        # "how much potato salad for a party" / "how many does that feed" is a question about the
        # answer in hand, and the store answers it from that answer. An entry that matches the
        # word "party" answers a different question (cheap party food, not how much of this one to
        # make), so the knowledge base stands down on the line rather than taking the turn.
        # The same holds for a count they change after it ("so how much for 8", "actually 6 of
        # us"): the figure is worked out from the answer's own per-head rule (bot/memory/portions.py).
        return None
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict) and understood.get("subject_unclear"):
        # The reading could not settle which thing the word means ("the bank was closed", "the
        # seal is broken"). Any entry that matches the bare word is a guess, and a confident card
        # for the other life is worse than saying which one is meant, so the knowledge base stands
        # down and the composer asks. A line with a cue is not flagged.
        return None
    if _a_bare_thanks(understood) and not (isinstance(text, str)
                                          and repeat.after_an_ack(text)):
        # A thank you and nothing else is not a follow-up to the answer it thanks. The readers
        # below answer a line that names the thing in the answer again ("thats kind thanks" after
        # a recipe was handed the recipe a second time, in other words), and a thanks that only
        # closes the turn has nothing of its own for them to answer, so the knowledge base stands
        # down and the small-talk reply takes it. A line after the ack is a line of its own and is
        # left to the readers as before ("cheers. also im skint till friday" is the money line).
        return None
    from ..compose import fallback as _the_composer
    if _the_composer.the_day_remarked(text):
        # The whole line says what the day is like ("windy as anything", "cold next week"). Nothing
        # is being asked and nothing is being looked up, and an entry is reached by a word: "wind"
        # found the bloating card, and "cold next week" found the one about a virus. The composer's
        # own reading decides, so the two cannot disagree about what the day is, and the knowledge
        # base stands down on a line the day's answer owns. A report on the day in the past is not
        # this case and stays with the entry that knows the thing.
        return None
    if _ruled_out.the_place_ruled_out(text, memory):
        # The place this module has a card for is the one they just ruled out: "we want to go to
        # italy" / "not rome" was answered with the Rome card. The line is a rejection, not a
        # mention, so the entry is no answer at all and the store's own reply takes the turn.
        return None
    try:
        if repeat.asks_what_that_costs(text, memory):
            # A line that asks what the thing on the screen costs names nothing of its own, so
            # the entry about the word in it prices its own subject: after "should i get it
            # serviced" ("a gas boiler service is usually 60 to 120 pounds"), "how much is that
            # usually" was answered with the price of a new boiler. The figure they are asking
            # about is the one in that answer, and the composer hands it back
            # (`bot/memory/repeat.py::asks_what_that_costs`), so this module stands down.
            return None
    except Exception:  # noqa: BLE001 - a reading that raises is a line this module keeps
        pass
    if mem.facts.a_name_picked(text, memory):
        # "we got a kitten" / "what should we name her" / "pepper": the word is the name they
        # chose, not a thing to look up. The store keeps it and says it back, and an entry about
        # peppers answers the word while missing the question - which is the one the bot asked.
        return None
    dog_feed = pets.the_dog_feed_follow_up(text, memory)
    if dog_feed:
        # A feeding question asked with a pronoun ("what should i feed him tomorrow") has no
        # animal word of its own, so the dog row cannot reach it; the last few turns still say
        # which animal the chat is on. It is kept as the dog row's answer, because the next line
        # ("how much of that a day") reads what this one was about from that row.
        _remember_answer(memory, pets.DOG_FEED_AMOUNT_ENTRY, dog_feed)
        return dog_feed
    # A limit that reaches an entry for the plan in hand keeps that entry. "keep it cheap" after
    # "im booking flights" is the cheap-flights answer, and an ack in its place ("I'll keep what I
    # suggest to what costs nothing") threw away the booking advice the person was asking for.
    limit = _a_limit_on_the_plan(text, memory)
    # "the cheapest quote i got is 2400" / "is that a lot": the range is in the answer this module
    # gave a turn ago, so the figure the person gave is read against it and the verdict goes in
    # place of the card said again. A price entry can be asked "is 400 too much for a roof
    # repair" - that line names its subject and is answered below - but "is that a lot" names
    # nothing, and no entry can price "that".
    judged = a_price.judged(text, memory)
    if judged:
        _keep_the_answer(text, judged, memory)
        return judged
    resized = another_size.answer_for(text, memory)
    if resized:
        # "what about a bigger one" straight after a time answer is that answer's rule asked for
        # the size they have, and the lookup reaches the entry its bare words fit: the chicken
        # rule came back as "Nothing separate for a bigger - it is the same advice: ...", which is
        # the bot quoting itself at somebody who asked a sum. Read here, before the lookup and
        # before the repeat framing, so the size line is answered by the module that knows how
        # (`bot/memory/size.py`), and a line any other reader can answer is untouched because the
        # reader passes on everything that is not a size ask about the thing above.
        _keep_the_answer(text, resized, memory)
        return resized
    if tried.a_card_is_not_the_answer(text, memory):
        # "still cold" after "my shower is cold" is the shower, and the card its one word belongs
        # to is the common cold: the thing keeps the turn, in the module that answers reports.
        return None
    reply = with_name(_the_dish_by_name(a_year_of_birth.reply(text, memory)
                                       or _answer(text, memory), memory), memory)
    # The same judgement when the figure and the thing are in one line: "is 6000 too much for a
    # new boiler" is answered with the card for a new boiler, which says what one usually costs
    # and never puts their own figure beside it. The card for the thing priced is the answer, so
    # it is the range read here, and the verdict stands in its place.
    judged = a_price.judged_with_the_card(text, reply, memory)
    if judged:
        _keep_the_answer(text, judged, memory)
        return judged
    placed = _the_question_with_the_place_on_it(text, memory, reply)
    if placed:
        _keep_the_answer(text, placed, memory)
        return placed
    if reply:
        # The rows are written for everyone, and the store knows what this person eats: a reply
        # that still names a food they said no to is handed back as no answer, so the row below
        # it - or another module - can answer with something they can eat.
        reply = _fitted_to_what_they_eat(reply, text, memory)
    if reply:
        # A paragraph read out earlier in this chat is not read out again when the line names a
        # sentence of it: "what paint do i need", "how many coats", "do i need a primer" reaches
        # the paint entry three times, and the third turn gave the same paragraph back word for
        # word two turns after the first. The sentence that names what this line names is the
        # part of it that answers, and it is new to the conversation.
        reply = _the_sentence_it_names(reply, text, memory)
    if reply:
        # A row holds one answer for every way its subject is asked about, and it is written the
        # way a screen reads it: a signpost first ("Three tests, in this order.") or the clock
        # first ("About 40 minutes start to finish. Fry 500g mince hard ..."). Neither is the
        # answer to the line read out: the sentence after the signpost is, and "how do i make
        # chilli" wants the method in its first sentence - see `bot/compose/lead.py`.
        reply = lead.answer_first(
            reply, memory.get("understood") if isinstance(memory, dict) else None, text)
    if reply:
        # The same reading for the other shapes of answer: a row holds one answer for every way
        # its subject is asked about, so the sentence that gives the time, the amount or the place
        # the line asked for is moved to the front when the card does not open on it. A declared
        # `lead` still wins, because it goes in after this - see `bot/compose/lead.py`'s `shape`.
        reply = lead.shape(reply, memory.get("understood")
                           if isinstance(memory, dict) else None, text)
    if reply:
        # The sentence the line asked for, in front, when the entry that answered declares one:
        # `entry(..., lead=("yesno", "Usually, yes"))` is the whole of that row's work, in any
        # domain, because every card is said from here - see `bot/compose/lead.py` and
        # `_the_sentence_owed`. It goes in at the last moment, after the repeat and narrowing
        # readings above, so a card the bot has already said is still read as the same card.
        reply = lead.the_sentence_owed(reply, memory.get("understood")
                                       if isinstance(memory, dict) else None,
                                       _the_sentence_owed(text, reply, memory))
    if not reply and limit:
        # "nothing too tiring" after "we are going to york next weekend" is a limit on the trip,
        # not a report of constant tiredness: the knowledge base has a fatigue entry, and it was
        # answering the trip's constraint with two weeks of sleep hygiene. Where the knowledge
        # base has nothing for the plan the limit is on, the composer answers the limit itself.
        return None
    if not reply:
        # The turn after a present list is often about the card, and a card is not a present: "my
        # nephew is 5 in june" / "what can i get them" / "and what about a card" reached the
        # present row again and had the whole list handed back behind a "Same as before" lead -
        # which the arbiter passes over as the answer already on the screen - so the turn ended on
        # a search punt. The card has an answer of its own, and it is the same answer whoever the
        # present was for, so it is said rather than the list.
        card = shopping.the_card_after_a_present(None, memory, line=text)
        if card and shopping.a_present_was_answered(memory):
            reply = card
    if not reply:
        # A line that only picks between things the bot itself just offered is answered from
        # that answer; the knowledge base has no entry for it, and the composer's search shrug is
        # a refusal of a question that was already answered one turn ago.
        reply = _the_one_to_pick(text, memory)
    # The answer is kept before the healing reader looks at it, so the care card stays the answer
    # the next line is read against: "my knee hurts" / "how long does it take to get better" /
    # "and what should i do" asked its "what should i do" of the healing line when that line was
    # the one on record, and got "Nothing to do for now."
    _keep_the_answer(text, reply, memory)
    # "how long will it take to heal" after a card about a body is answered from that card, not
    # from the entry its bare words reach: the entries keyed on healing are bones and sprains, and
    # a cut finger was told six weeks for a bone and a knee was told the two days its icing takes.
    return healing.vetted(text, memory, reply, step_of=_first_step)


def _the_question_with_the_place_on_it(text, memory, reply):
    """The last question asked again with the place this line says, answered; or "".

    "any ideas for a cheap day out with kids" is answered with the free ones, and "near leeds" is
    then the same question with a place on it: the knowledge base holds the day trips from Leeds,
    and main answered the place with "I'm listening - say more if it helps", or with the free ones
    again ("Near leeds - same answer: ..."). So the question is put back together and answered, and
    kept only when that answer is new: a hedge, the answer already on screen, or the very line the
    person's place was answered with, is nothing to hand the turn to.
    """
    question = whereabout.the_question_with_the_place(text, memory)
    if not question:
        return ""
    from ..compose import fallback as composer
    said = str((memory.get("last_answer") or {}).get("reply") or "")
    placed = with_name(_the_dish_by_name(_answer(question, _of_its_own(memory)), memory), memory)
    if not placed or placed in composer.UNKNOWN:
        return ""
    for other in (said, reply):
        if other and placed.strip() == str(other).strip():
            return ""
    # The answer is about the place and not about the answer already given, so a repeat of the
    # last answer with a place on the front of it loses: "Near leeds - same answer: ..." and
    # "Same answer, and it covers this: <the answer above>" are both the line said twice.
    flat_placed = _flat(placed)
    for other in (said, reply):
        flat_other = _flat(str(other or ""))
        if flat_other and flat_other in flat_placed:
            return ""
        if flat_other and flat_other[:60] in flat_placed:
            return ""
    return placed


def _answer(text, memory):
    """The knowledge base's reply, or the answer last given when the line is that line again."""

    if isinstance(memory, dict) and memory:
        from ..memory.when import asks_what_today_is

        if asks_what_today_is(text):
            # "what day is it" asks the calendar, and the chat around it is not part of the
            # question. Read with the thread in hand, the ask lent itself the trip on it: after
            # "we're off to portugal in august", "what day is it" got "Portugal: Lisbon three
            # full days, Porto two". The calendar row answers it with nothing else in hand, and
            # that is what it is answered with here.
            return _answer(text, {})
    if isinstance(memory, dict) and stuck_line.pool(text, memory) \
            and not repeat.answer_for(text, memory):
        # "i dont know what to do" after hard news is a request for the next step, and the stuck
        # reader has the one that fits that kind of news. It is read first, before every reader
        # below, because each of them reads a word of the line on its own: carried into the
        # knowledge base the only reachable word is the hard line's own ("i lost my job yesterday"
        # reads "lost", which is the memory-science row), and read as a plan it reached the
        # cheapest-week list. Standing aside leaves the turn to bot/memory/stuck.py, which reads
        # the class (job, money, a death, an ending) before any single word of it.
        #
        # One reader is excepted, and it is the one that answers the line already: when the reply
        # on the screen was a card with steps in it ("my boyfriend dumped me" -> "Tell two people
        # today..."), the answer to "i dont know what to do" is that reply's own first step, and a
        # neutral pool in its place throws away the specific advice for the generic one. The pool
        # is for the line after a nod, and `repeat.answer_for` says which of the two this is.
        return None
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if A_PLEA_FOR_TIPS.match(str(text or "").strip().lower()) \
            and mem.last_module(memory) == "answers":
        # "Any tips" names nothing at all, and it comes after a card of advice: it asks for more of
        # the answer in hand, and that answer is the composer's to read (the next thing in it, or
        # the plain line that the step stands). Looked up in the knowledge base the line leans on
        # the one before it and can land on a card about something else entirely - "Green
        # vegetables: broccoli or beans steamed for 4 to 5 minutes" for a child who will not eat
        # veg - because the words "any tips" are the only thing the lookup has to go on. A last
        # turn that was a note rather than a card ("Noted: you're moving flat next month.") is
        # the one case where the lookup is what answers the plea, and it is left alone.
        return None
    if isinstance(understood, dict) and understood.get("intent") == "farewell":
        # A goodbye is not a question about the words in it: after an answer about sleep, "night
        # night" reached the sleep entry through the word "night" and read the goodnight as a
        # second ask about sleep, at the moment the person was going to bed. The farewell is the
        # composer's line. The reading only calls a line a farewell when the goodbye is the whole
        # of it, so a line that says something of its own ("night feeds are killing me", "good
        # night routine for a baby") is still answered.
        return None
    if isinstance(understood, dict):
        written = named.the_best_time_to_do_it(text, understood, memory)
        if written:
            # "When is the best time to do it" after the mould on the courgette leaves points at
            # the plants, and the question about the plants is the one the knowledge base has a
            # row for. Written out, it answers; on its own the line only reaches the answer the
            # person has just had, which comes back as the mould card said again.
            said = _ask_a_rewritten_line(written, memory)
            if said and not _said_before(_without_lead_in(said), memory):
                return said
    if isinstance(memory, dict) and _the_thing_has_got_better(text, memory):
        # The same stand-down as the farewell, for a line whose words are not a new ask: the news
        # is answered by the relief pools, and this module's entry is the advice for a trouble
        # that is still there.
        return None
    if isinstance(memory, dict):
        the_moan = _the_ask_behind_a_moan(text, memory)
        if the_moan:
            # "i always get rice wrong" names the thing that comes out badly and nothing else, so
            # every reader below passes it on and the line was answered with the intake form
            # ("Got it. Is there anything you'd like a hand with?") while the card for the thing
            # was in the knowledge base all along - "how do i get rice right" gets it. The moan is
            # written out as that ask and read again; only an answer about the thing they named is
            # taken, so a loose rewrite cannot hand back a card about something else.
            return the_moan
    led = _a_lead_time(text)
    if led:
        # "how long before the day should we order the cake" is a lead time, and the cake's own
        # entry answers how long it keeps. It is read here, before the lookup, because the ask
        # names a length and a thing and every reader below would answer the length of the thing.
        return led
    if isinstance(memory, dict):
        # "i started learning guitar last month" / "my fingers hurt" / "how long should i
        # practise" was the bone-healing card, because the line was read against the complaint
        # about fingers and that card keys both "fingers" and "how long". The practicing is what
        # the ask is about and the guitar is what the chat has been on, so the ask is written out
        # with the guitar and read again. Only a rewrite that reaches an entry giving a length is
        # taken, and only when its answer is not the one already on the screen, so a line whose
        # own answer is the right one keeps the turn it had.
        #
        # The rewrite is only worth taking when it reaches a *different* entry from the one the
        # line reaches on its own. "i started running last month" / "how long should i run for"
        # reached how-often-to-run on its own, which narrows to "20 minutes." - the length asked
        # for - and the rewrite ("how long should i run for running?") reached the same entry and
        # handed back the whole training card instead. When both readings land on the same entry
        # the person has already been answered about the thing they asked about, and there is
        # nothing for this reader to add.
        own = find(understand(text))
        own_answers_the_length = False
        if own is not None:
            own_said = _payload(own, memory, understand(text))
            own_answers_the_length = bool(_answers_a_length(own, own_said)
                                          and _A_DURATION.search(str(own_said or "")))
            # The line's own answer is already a length to spend doing it - "a mile is 20 minutes
            # at a brisk walk ... half an hour a day is the number that earns most of the
            # benefit" for "i started walking every day" / "how long should i walk". A rewrite
            # reaches a card on the same practice with a figure of another kind (steps a day) or
            # the whole training plan, and neither is the length the person asked for, so the
            # line keeps the answer it had.
        for written in doing_it.written_out(text, memory):
            if own_answers_the_length:
                break
            reading = understand(written)
            reached = find(reading)
            if reached is None:
                continue
            if own is not None and reached is own:
                continue
            written_reply = _payload(reached, memory, reading)
            if not _answers_a_length(reached, written_reply):
                continue
            if _said_before(_without_lead_in(written_reply), memory):
                # The chat has had this answer already, and the ask is the same question about
                # the same practice: the part asked is what the person wants back, not the whole
                # paragraph a second time.
                short = length.narrow(written_reply, text)
                if short and not _said_before(short, memory):
                    return short
                continue
            return written_reply
    if a_wish.reading(text):
        # A hopeful aside ("fingers crossed", "with luck", "hope it works") names nothing to look
        # up, and its own words reach whatever they fit: "fingers crossed" after the condensation
        # answer got the entry on fingers going white in the cold, and "with luck" was read as a
        # detail of the answer ("The same goes for the luck: ..."). The wish is the small talk's
        # turn (`bot/memory/hope.py`, answered by `chat`), so the lookup stands aside.
        return None
    if isinstance(memory, dict) and prefer.served_already(text, memory):
        # The same taste a turn after it was answered with picks for it. Every reader below
        # would reach the same entry and hand the same list back, framed as a repeat ("Same as
        # before: *Arrival* is the smartest one ..."), because the taste is the only thing in
        # the line - and the answer last given is the last of those readers. Nothing new can
        # be said about it, so the turn goes to the small talk ("You like sci fi - noted."),
        # which is what the person got before this reader existed.
        return ""
    agreed = repeat.agreement_with_the_answer(text, memory)
    if agreed:
        # The line says the answer back ("low heat, got it" a turn after "Low heat it is."). Read
        # as a fresh question it is answered with the whole paragraph again - the paragraph the
        # person has just agreed with - so the confirmation comes first, the way the repeat
        # below does.
        return agreed
    if isinstance(text, str) and BARE_SAY_NO.search(text):
        # Nothing in the knowledge base names a situation for this ask, but the answer to
        # saying no does not need one. This is the first reader, so the answer does not depend
        # on a lookup that has nothing to match, and it still lets _the_line_again take a
        # repeat, so the line asked twice gets "Same as before" rather than the paragraph
        # again. The regex names only the bare asks - "how do i say no", "how do i refuse" -
        # so "to my boss", "to my mum" and "turn down a request" keep their own entries, and
        # "without sounding lazy" keeps the wording offer.
        return _the_line_again(text, memory) or work.SAY_NO_POLITELY
    # "make it short", "shorter", "in one line", "tldr": the person wants the answer they already
    # have with the detail taken out, and the lead of it is in memory. It comes before the lookup
    # on purpose - a line that names nothing still matches entries on its own words ("keep it
    # brief" reaches the cheese that keeps, "shorter" reaches the one that got shorter) and the
    # reply to a request for less is the answer itself, never a new entry.
    # `repeat` is imported at the top of this file: a local import here would make the name local
    # to the whole function and the agreement check above would raise before it is bound.
    shorter = repeat.shorter_for(text, memory) if isinstance(memory, dict) else None
    if shorter:
        return shorter
    dated = deadline.follow_up(text, memory) if isinstance(memory, dict) else ""
    if dated:
        # A line that is only a date is the plan said a turn ago with the date on it: "we want to
        # save 3000 pounds" / "by december" asks how the plan goes against December, and the goal
        # alone only gets the general advice. It is read that way here, before the lookup, because
        # the topic path answers a bare date with the answer already on the screen.
        answer = _ask_a_rewritten_line(dated, memory)
        if answer and _the_same_answer_again(answer, memory):
            # The date bought nothing - the entry says the same thing with it as without it - so
            # the person would hear "Same answer, and it covers this" at a line that added
            # something. The turn is then read exactly the way it was before this module.
            answer = None
        if answer:
            return answer
    # A line whose subject is a bare "he" or "she", in a chat that is on an animal, is about that
    # animal: "we got a puppy last week" then "he keeps biting the kids" was answered from the
    # entry for a child who bites at nursery, and the one after "we got a dog in the summer" came
    # back as the nod, because the pronoun is the subject of the question and nothing had put the
    # animal in its place. The store says which animal only when the reading points the pronoun at
    # one it holds and the filled line lands on an entry keyed on that animal
    # (`topics.the_animal_the_subject_is`). It is asked below, after the line itself, so a line
    # that already has an answer keeps it: "he cries when i leave the room" straight after the
    # puppy and a sleepless night is the separation answer, not the one on leaving a dog alone.
    animal = the_animal_the_subject_is(understood, memory) if isinstance(memory, dict) else None

    back_to = said_topic.the_thing_asked_again(memory, text) if isinstance(memory, dict) else ""
    if back_to:
        # "back to lisbon, what should i see" goes back to a thing and asks about it in one
        # breath. Read as it is typed the line is answered for its own words - "back" is a body
        # part - so the back-pain card answered a question about Lisbon. The store has just put
        # the thing back on the table, so the line is read with it in front of the ask.
        thing = said_topic.the_thing_went_back_to(memory)
        reached = find(understand(back_to, memory))
        if reached is not None and any(_the_entry_names(reached, word)
                                       for word in thing.split() if len(word) > 3):
            # The card the rewritten line reaches has to be the one about the thing they went
            # back to: written with the thing in front, a line about pricing a carboot reaches
            # the card on raising your freelance rate, which shares the asking and nothing else.
            answer = _ask_a_rewritten_line(back_to, memory)
            if answer:
                # The same question asked again a few turns later is worth the answer again,
                # framed as the repeat: they asked what to see in Lisbon, went on to something
                # else, and came back to it. `_said_before` would stand the reader down and hand
                # the line to the card its own words fit, which is the fault this reader is for.
                return same_again.instead(answer, text, memory) or answer
    # A line asking which part of the answer to do first is answered out of the answer in hand,
    # before the lookup. It names nothing of its own, so the lookup can reach a neighbour of that
    # answer instead: "where do i start" after "im trying to save money" reached the card on where
    # to borrow, and the person asking which step of the plan to do first got a loan. `_last_answer`
    # is no help here - a bare ask shares no word with the answer, so the run is read as ended -
    # and the line in front is all the step reader needs.
    if repeat.asks_which_part(text) and not _a_city_card_asks_which_first(text, memory):
        # A city card is a list of places to go, not a list of steps, and the card's second
        # sentence is a local habit rather than one of them: "what should we do first" after the
        # Barcelona guide came back "The thing to do first: Eat lunch at 2pm like locals." The
        # city's own row answers which of the places comes first (`city-next`), so this reader
        # stands down and the lookup has the turn.
        step = repeat.the_move(text, _the_answer_in_front(memory), memory)
        if step:
            return step
    case = _a_case_of_the_answer_in_hand(text, memory) if isinstance(memory, dict) else ""
    if case:
        # "and for a hard one" after the answer gave one of the cases: the case is written in an
        # answer above, so it is read from there rather than looked up as a question of its own.
        # Before the lookup, because the words of the line reach nothing on their own and the
        # greeting pool answered it with a nod ("For a hard one - noted.").
        return case
    if limit.reads_the_answer(text, memory):
        # The line limits the answer just given, whichever reader below would take it: this one
        # answers from that answer's steps, and the carry below would ask the knowledge base again
        # with the limit on the end of the question ("oven cleaner" reached a food answer here).
        return None
    if TAKEN_BACK_OPENER.match(str(text or "")) and "?" not in str(text or "") \
            and len(str(text or "").split()) <= 5:
        # A line that opens by withdrawing something is a take-back, not a question. The store
        # answers it ("Right - no dog, then") and the word "forget" must not reach the entry on
        # forgetting, which read "forget the dog" as a question about memory. A real ask about
        # forgetting says its question - "how do i stop forgetting things" - and is untouched.
        return None
    back_to = went_back.a_return_to_the_topic(text, memory) if isinstance(memory, dict) else ""
    if back_to:
        # "back to lisbon, what should i see" takes the chat back to a thing it has already
        # named and then asks about it. Read whole, the line reached the entry on a bad back:
        # "back" is the return, not the body part, and the thing they named never got to the
        # question. With the thing written into the ask ("what lisbon should i see") it reaches
        # the entry filed for it, which is `bot/memory/returns.py`.
        answer = _ask_a_rewritten_line(back_to, memory)
        if answer:
            if _said_before(_without_lead_in(answer), memory):
                # The return lands on the answer already on the screen: it is still the answer,
                # and it is said as the same one rather than word for word a second time.
                return went_back.as_the_same_answer(
                    answer, text, short=_repeat_short(answer, back_to))
            return answer
    again = named.a_measure_asked_again(text, memory) if isinstance(memory, dict) else ""
    if again:
        # "how long does it take to fit a new one" after the chat has been about a boiler: the
        # line names no thing, so on its own it reaches the entry that answers how long a boiler
        # is built for. Written as the question it is, it reaches the row that knows how long a
        # fitting takes. Read before the lookup, because that wrong entry does answer the line
        # as it stands and would take the turn.
        answer = _ask_a_line_of_its_own(again, memory)
        if answer and not _the_same_answer_again(answer, memory):
            return answer
    trip = named.a_part_of_the_trip(text, memory) if isinstance(memory, dict) else ""
    if trip:
        # "and where should i stay" after a trip to Rome is the question with the place written
        # in, and the card filed for that question is the one that knows: asked bare, the line
        # reached whatever the chat's newest words fit, and the day trips out of Rome answered
        # where to stay.
        answer = _ask_a_rewritten_line(trip, memory)
        if answer:
            # The same card twice in a row is not a second answer, but it is the right card:
            # "whats the food like" asked after the city card reached nothing at all and got the
            # search hedge, and said again with a lead-in it at least names Trastevere for dinner.
            # A yes/no ask about the part is not the card said again. "is three days enough" after
            # the days card asks for a verdict on the three days, and the card on the screen
            # cannot give one: saying "That was the whole of my answer on it" answers their
            # question with a remark about the bot. Where the card has already been read, the line
            # is left to the modules that hedge - the same honest reply the chat got before the
            # card - rather than handed a claim that it already had everything.
            if not _A_YES_NO_ASK.match(str(text or "").strip()):
                again_told = same_again.instead(answer, text, memory)
                if again_told:
                    return again_told
            if not _said_before(_without_lead_in(answer), memory):
                return answer
    # A plan moved to a day, rather than to a time: "im cooking chilli for 6" / "can i make it
    # friday night instead". The line names a day and a move and nothing to answer with, so the
    # turn came back as the search hedge, or as the ingredient-swap card because "instead" is how
    # a swap is asked for. Whether it can be made on Friday is whether it can be made ahead, which
    # the kitchen already answers for "can i make it the day before": the day goes out of the line
    # and "ahead of time" goes in, and the reply says the day out loud so the move is read back.
    # Only where the rewritten line answers and the answer is not the one already on the screen, so
    # a line whose subject has nothing to say about being made ahead keeps the turn it had.
    moved = when.a_plan_moved_to_a_day(text) if isinstance(memory, dict) else None
    if moved:
        answer = _ask_a_rewritten_line(moved["line"], memory)
        if answer and not _said_before(_without_lead_in(answer), memory):
            day = moved["day"]
            return day[:1].upper() + day[1:] + " works. " + answer
    if tried.reads_as_a_step_done(text, memory):
        # A step of the answer just given, said as done ("ive cleaned the filter" after "my
        # washing machine smells"): the memory lane walks the answer from there, and every reader
        # below asks the knowledge base about the words of the line instead - "filter" reached
        # the vacuum cleaner's filter, so a person with a smelly washing machine was told how to
        # clean a vacuum. The step is the answer's own, and the store has it.
        return None

    # A follow-up that names a part of the thing the person named is about that thing, even when
    # the turn before it was about a different part. "my washing machine smells" / "i clean the
    # filter" / "and the drawer every month": the drawer's owner is still the machine, and the
    # newest turn's words have lost it, so the part joined to those words reaches no entry and the
    # line fell to the pantry card that is keyed on the bare word "drawer" - a cupboard clear-out
    # as the answer to a washing machine's detergent drawer. Read before the lookup, because the
    # pantry card does answer the words of the line as it stands, and the part of the machine is
    # the thing the person asked about.
    part_owned = _the_part_of_the_thing_they_named(text, memory)
    if part_owned:
        return part_owned
    # A food or drink question whose only subject is "he" or "she" is about the animal the
    # chat is on: "my dog is 8 and a bit overweight" / "can he have cheese" reached the cooking
    # rows and came back as an omelette, and a rabbit's carrot as vegetable soup. With the
    # animal written into the line the pet rows reach it, exactly as they do when the person
    # names it themselves. A person's pronoun is left alone by `_pet_in_the_talk`.
    animal_line = pets.the_animal_follow_up_line(text, memory)
    if animal_line:
        animal_answer = _ask_a_rewritten_line(animal_line, memory)
        if animal_answer:
            return animal_answer
    answer = _respond(text, memory)
    if animal is not None and (
            not answer or answers_about_another_creature(answer, animal.get("clean") or "")):
        filled = _ask_a_rewritten_line(animal.get("clean") or "", memory)
        if filled and not _the_same_answer_again(filled, memory):
            answer = filled
    if _asks_only_the_length(text):
        # Both when the answer came back as the last paragraph again and when the lookup found
        # nothing at all: a length ask about an answer that holds no time gets the honest line.
        honest = _a_length_ask_with_no_figure(text, memory, answer or "")
        if honest:
            return honest
    measure = named.about_the_subject(text, memory) if isinstance(memory, dict) else ""
    if measure:
        # A line that only points back - "how long should it be", "how much would that cost" -
        # names nothing, so what it reaches is whatever the topic's newest words fit: after
        # "im thinking of getting a dog" / "it would be for the kids" the child bus fares, and
        # where nothing fits it, the search hedge. Written about the subject of the chat the same
        # line reaches the entry that knows it ("how much would the dog cost"), and that entry
        # takes the turn when it names the subject and the line on its own does not.
        said_about_it = _a_measure_about_the_subject(measure, text, memory, answer)
        if said_about_it:
            return said_about_it
    if answer:
        # An answer that is word for word the one the person has just had is not a second answer:
        # it happens when the line reaches the entry through the thing under discussion rather
        # than on its own ("my kitchen tap is dripping" gets the washer answer, then "i tried
        # turning it really hard and now its worse" reaches the same washer answer through the
        # tap). Said twice running, the bot is talking at the person; the short form behind a
        # lead-in is the same answer, said the way a friend says it a second time.
        if (isinstance(text, str) and _A_BARE_MEASURE.fullmatch(text)
                and re.search(r"\d", str(answer))
                and (SIGNALS["amount"].search(answer) or SIGNALS["money"].search(answer))):
            # The bare ask got the figure on the screen back. It is the same words as the answer
            # above, but the repeat frame ("Same as before: A banana is about 105 calories") is
            # a pointer at the card rather than the figure, and a how-much line is owed the
            # figure. Said plainly, it is the answer.
            return answer
        said = _answer_said(answer, memory) if _flat(answer) == _flat(mem.last_bot(memory)) else 0
        if said:
            if said >= 3:
                return AGAIN_HELP.format(reply=_repeat_short(_without_lead_in(answer), text, memory))
            return AGAIN[said - 1].format(reply=_repeat_short(_without_lead_in(answer), text, memory))
        # The short form of the answer just given, on a line that names something else, is not a
        # second answer either. "im going to lisbon in may" gives the city card, and "what about
        # the food" reaches the same card and comes back as its first sentence, so the person who
        # asked about food reads the sights again with nothing saying why. The paragraph is on the
        # screen directly above, so the turn says in one sentence where the answer is rather than
        # reading it out again behind four words of lead-in - `bot/memory/again.py` has those
        # lead-ins for the turn where the answer has not been read yet, and this is not that turn.
        short_of_it = _short_form_of_the_last(answer, memory)
        fact = bool(short_of_it) and _a_fact_about_the_person(memory)
        detail = ""
        if short_of_it and not ASKS_ABOUT_HOW_IT_TURNED_OUT.search(text):
            # A part the answer names is a part, even in a sentence ("i looked at the trams").
            # A bare word the person's own sentence happens to share with the paragraph is not:
            # `_the_detail_named` walks back over the line to the newest keyword and holds it up
            # as the part, so "i work nights" named "nights" after an answer that says "late
            # night" about a dog. So the fact test comes before that guess and after the name.
            detail = (_a_part_named_in_the_line(text, memory, short_of_it)
                      or ("" if fact else _the_detail_named(text, memory)))
        if detail:
            if _named_in(short_of_it, detail):
                # The answer names the part, so it has something to say about it, and a sentence
                # about the conversation ("Everything about insurance is in what I said above")
                # withholds the one clause that answers the line. "how much does a cat cost to
                # keep" prices insurance in passing (8 to 20 a month) and the follow-up "what
                # about insurance" was told there is no more than that - which is not true, the
                # figure is in the paragraph. The clause that names the part is the answer.
                part = _the_part_in_the_answer(short_of_it, detail)
                if part:
                    return part
            return NOTHING_SEPARATE[0].format(detail=detail)
        if fact and _only_a_quality_name(text, memory):
            # The only name in the line is a word that says what the thing is like ("a new"), and
            # that names no part of the answer: there is nothing for a lead-in to say about it and
            # the answer is already on the screen, so the repeat is answered as a repeat. Standing
            # down said "I'm not sure about that one, sorry" to a question the card answers.
            return AGAIN[0].format(reply=_repeat_short(short_of_it, text, memory))
        if fact:
            # A part the answer above does not name is not a part of it, and no paragraph is the
            # whole of a fact about themselves, so the turn goes to the parts of the bot that
            # answer a person saying something about themselves.
            return None
        if short_of_it and _their_own_state(text):
            # The same goes for a line that says where the person has got to without asking
            # anything of the thing: "i dont know why" after the low-mood card was read as the
            # part of the answer named "dont" and given a sentence of the card again, and after
            # "my 3 year old wont eat vegetables" it reached the question about why the sky is
            # blue. A line that is the person's own state is theirs.
            return None
        return answer
    carried_on = more.reply_for(text, memory) if isinstance(memory, dict) else None
    if carried_on:
        # "tell me more", "go on" - the whole line is a request to carry on, and the answer it
        # asks about is the one just given: nothing can look it up, so the reply says plainly
        # how much there is and hands the turn back with a question that can be answered.
        return carried_on
    # A report of a sore or a trouble ("i get heartburn after meals") is not a question, but a
    # friend hears one: what can I do about it. Read that way against the health answers only, so
    # "i have two kids" keeps the warmer pool, and only where the line reached nothing at all.
    if tried.might_be_a_report(text) and tried.pool_for(text, memory):
        # The line reports on the answer it followed, and the state word in it is the thing's, not
        # a new subject: "my shower is cold" then "still cold" was read as a fresh complaint and
        # answered with the common cold ("two or three days and gone in about a week"). Every
        # reader below looks the words of the line up, so the report stands the module down and
        # `chat` says the next step (`bot/memory/tried.py`).
        return None
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = understand(text, memory)
    if (understood or {}).get("kind") == "statement":
        told = _a_complaint_answered(text, understood, memory)
        if told is not None:
            return told
    carried = named.follow_up(text, memory) if isinstance(memory, dict) else ""
    from_a_taste = False
    if not carried:
        # "i like sci fi" after the film list is a request for the science fiction one, and the
        # medium it omits is in the answer just given (`bot/memory/prefer.py`).
        carried = prefer.follow_up(text, memory) if isinstance(memory, dict) else ""
        from_a_taste = bool(carried)
    if carried:
        # The line names a thing and asks nothing, and the line before it asked for
        # suggestions: "my mum is coming to stay" / "what should i cook" / "and a pudding" is
        # still that request, about a pudding. Read the ask the line carries and answer that.
        # Only when the line itself has no answer (above), so nothing that answers today moves.
        answer = _ask_a_rewritten_line(carried, memory)
        if answer and (_same_as_the_last_answer(answer, memory)
                      or _the_same_answer_in_other_words(answer, memory)):
            # A carried ask has to buy the person something they have not just had. "what else"
            # after the film list is a request for a second pick, and an entry that hands the same
            # three titles back over again has read nothing: the turn is better spent on the
            # composer's answer to the line than on the list already on the screen.
            answer = None
        if answer and from_a_taste and not prefer.about_the_medium(answer, memory):
            # "i like crime" after the film list reaches an entry with no crime films and hands
            # the same three films over again: the person hears the list they have just heard,
            # with no sign it was read. A taste that buys nothing new stands down and the small
            # talk takes the turn. So does a taste that buys something from another domain: the
            # ask is written with the medium on the end of it ("any good light books"), and an
            # entry that shares only the taste word with it (a soup for "light", a walk for
            # "walk") answers a question the person did not ask.
            answer = None
        if answer:
            return answer
    # A line that reports where the thing in hand stands ("its on 4%", "it still smells") names no
    # subject of its own, so the knowledge base cannot reach it and the turn came back as the
    # report said back at the person ("Got it — it's on 4%."). Read with the thing written in
    # ("my phone is on 4%") the same line reaches the entry that knows it. Only where the line
    # answered nothing at all and the answer is not the one already on the screen, so no turn that
    # answers today moves; the first read that answers takes the turn.
    if isinstance(memory, dict):
        for in_hand in named.reported_states(text, memory):
            reached = find(understand(in_hand, memory))
            if not _the_report_is_answered(text, reached):
                continue
            answer = _ask_a_rewritten_line(in_hand, memory)
            if answer and not _said_before(_without_lead_in(answer), memory):
                return same_again.instead(answer, text, memory) or answer
    # A fact about the person, said with no subject of its own, is the subject on the table asked
    # about with the fact on it: "pension" then "im 34 and self employed" reached nothing and the
    # turn came back as "Got it. Is there anything you'd like a hand with?". Written with the
    # subject in front ("pension im 34 and self employed") the same line reaches the entry that
    # needs both halves - the pension one for the self employed. Only an entry keyed on the fact
    # the person stated takes the turn, so a read that reaches a neighbour of the subject by a
    # word-mate ("party for a 7 year old" reaching a party card that says nothing about age) is
    # no answer and the small talk keeps the turn.
    if isinstance(memory, dict):
        for stated in named.stated_about_the_person(text, memory):
            reached = find(understand(stated, memory))
            if not _the_fact_is_what_is_answered(text, stated, reached, memory):
                continue
            answer = _ask_a_rewritten_line(stated, memory)
            if answer and _most_of_it_said(answer, memory):
                # the fact moved nothing: the same card answered, with a lead-in in front
                continue
            if answer and not _said_before(_without_lead_in(answer), memory):
                return same_again.instead(answer, text, memory) or answer
    # A practice the person keeps with the thing in hand ("i feed them every week" after tomato
    # plants) has the same shape as a report: no subject of its own, so no entry is reached and the
    # turn came back as the practice said back at the person. Written with the thing in front
    # ("tomatoes feed every week") the same line reaches the entry that knows when and how often.
    if isinstance(memory, dict):
        for practice in named.care_reports(text, memory):
            reached = find(understand(practice, memory))
            if not _the_practice_is_answered(practice, reached):
                continue
            answer = _ask_a_rewritten_line(practice, memory)
            if answer and not _said_before(_without_lead_in(answer), memory):
                return same_again.instead(answer, text, memory) or answer
    bare = named.about_it(text, memory) if isinstance(memory, dict) else ""
    if bare:
        # A bare thing after a turn about something is that thing asked about ("frosting" after
        # "im making a cake"), and the entry for it is what the person wants. The sentence of the
        # last answer that names the thing comes first: it is the same answer's own words about it.
        answer = _ask_a_rewritten_line(bare, memory)
        if answer:
            short = _the_sentence_about(text, memory) or _the_sentence_about(bare, memory)
            if short and _flat(short) != _flat(answer):
                return short
            if not _said_before(_without_lead_in(answer), memory):
                return same_again.instead(answer, text, memory) or answer
    part = named.about_the_thing(text, memory) if isinstance(memory, dict) else ""
    if part and _the_part_is_what_answers(part, memory):
        # The line names a part of the subject and asks nothing: "im going to spain" / "and its
        # population" is a question about Spain, and the knowledge base has the entry under
        # "population of spain". Only when the line on its own found nothing (above) and it does
        # not carry the ask before it, so nothing that answers today moves: the part has to
        # reach an entry of its own to take the turn.
        answer = _ask_a_rewritten_line(part, memory)
        # A part the entry answers by reading its paragraph out again is the answer they were
        # given a turn ago: "im visiting lisbon" / "and the food" reached the Lisbon card a
        # second time. The part has to be new to take the turn, so the answer on screen stands
        # and the line falls back to the follow-up paths.
        if answer and not _said_before(answer, memory):
            return answer
    person = matters.about_them(text, memory) if isinstance(memory, dict) else ""
    if person:
        # "my mum is 78 and keeps falling" / "she lives alone" is a fact about the person the
        # answer was about, and written out with her in it ("my mum lives alone") the knowledge
        # base answers it: the free care needs assessment, the pendant alarm, the key safe. The
        # store's reply to the line as typed is the receipt STYLE.md rules out ("Got it - she
        # lives alone"), with the one fact that matters left unused. Only an answer that is not
        # the one already on the screen takes the turn.
        answer = _ask_a_rewritten_line(person, memory)
        if answer and not _said_before(answer, memory):
            return answer
    # Every reader above is done and there is no answer: the line would be a search hedge, and the
    # answer already on the screen speaks to the trouble in it ("i burnt the rice" / "can i still
    # eat it"). Last, so an entry that answers the line as it stands always beats a repeat of the
    # turn above it: see _the_answer_on_the_table.
    said_on_the_table = _the_answer_on_the_table(understood, memory)
    if said_on_the_table:
        return said_on_the_table
    return _the_line_again(text, memory)


def _a_measure_about_the_subject(measure, text, memory, alone=""):
    """The answer to a measure ask that points back, asked about the subject of the chat.

    "how much would that cost" after "im thinking of getting a dog" is a question about the dog,
    and the entry that answers it ("pet-cost") is only reached when the subject is in the line. The
    line on its own, with nothing of its own to match, reaches the entry the topic's newest words
    fit ("it would be for the kids" gave the child bus fares) or nothing at all, which is the
    search hedge. Three things have to hold before it takes the turn:

    - the entry the written-in line reaches names the subject, not only the asking;
    - the entry the line on its own reaches does not name the subject (so nothing that answers
      today moves);
    - where the subject alone is not enough, the plan the chat is on goes in as well: "how long
      should the speech be" names no occasion, and "my sister is getting married in june" does.
    """
    # A bare "how much" whose answer already carries a figure is answered: the rewritten line
    # ("how much drink") reaches a clause without one ("Drink a few mouthfuls every 15-20 minutes")
    # and the repeat reader framed that as the answer. The figure on the screen is the answer, and
    # only a figure the line did not get sends the ask through the rewrite.
    if (alone and re.fullmatch(r"\s*how (?:much|many)\s*[?.!]*", str(text or ""), re.I)
            and asked_kind(text) == "amount"
            and SIGNALS["amount"].search(str(alone))):
        return ""
    word = named.subject_word(memory)
    if not word:
        return ""
    if named.a_newer_thing(memory, word):
        # The line before the ask named something they need, so the ask is about that and the
        # subject the chat opened with is stale: "it needs a new spring" / "how much would that
        # cost" is the price of the spring, not the price of the MOT test.
        return ""
    # The thing on the table has stopped working, so the measure asked about it is the repair's:
    # "my boiler is broken" / "how long will it take" wants the visit, not the boiler's ten to
    # fifteen years, and the entry that knows it is filed under the boiler and the repair. Asked
    # first, and only where an entry about getting the thing mended names the thing, so a fault the
    # knowledge base has nothing for falls through to the paths that were there before.
    reached = None
    faulty = named.a_faulty_thing(memory)
    if faulty and not _A_HOW_LONG.search(measure):
        # Only a length ask moves. "how much will that cost" about a broken thing is answered well
        # by the rows that were already answering it (a repair is £60 to £120, a phone screen £60 to
        # £120), and the repair's *time* row is no answer to a price: the price of a cooker's repair
        # reached the car repair row, said how long a garage keeps a car, and the figure they asked
        # for never came.
        faulty = False
    if faulty:
        # The phrase naming the thing, not the one word of it: "the washing machine" reaches the
        # washing machine's repair row where "the machine" reaches the row about how long a wash
        # cycle runs. `named.the_thing` is the subject with the words for how it is taken out.
        thing = named.the_thing(memory)
        phrased = measure
        if thing and word and ("the " + word) in measure and thing != word:
            phrased = measure.replace("the " + word, "the " + thing, 1)
        asked_lines = [phrased.replace("the " + thing, "the " + thing + " repair", 1)
                       if thing and ("the " + thing) in phrased else phrased + " repair",
                       phrased + " repair"]
        if thing:
            # The row about a repair is only reached by a line that says how long a repair takes
            # and not how long a cycle runs: "how many days for a washing machine repair" is that
            # line, where "how long will the washing machine repair take" is the cycle's.
            asked_lines.append("how many days for a " + thing + " repair")
        for said in asked_lines:
            asked = find(understand(said, memory))
            if not (asked is not None and _the_entry_names(asked, word)
                    and _names_a_repair(asked)):
                continue
            told = _ask_a_rewritten_line(said, memory)
            if not told or _flat(told) == _flat(alone):
                # The row that answers the written line is the thing's own row again ("Six years."
                # for a cooker whatever the wording), so this candidate buys nothing: the ask has
                # to bring the repair's answer, not the same one under a different sentence.
                continue
            measure, reached = said, asked
            break
    if reached is None:
        reached = find(understand(measure, memory))
    if faulty and _A_HOW_LONG.search(measure) and not _names_a_repair(reached):
        # A broken thing asked how long is not asking how long the thing lasts: without an entry
        # that names the repair, the life of it ("Six years.") would be handed over as the answer
        # to getting it mended, and the paths below were giving nothing better. Stand down instead.
        return ""
    if reached is None or not _the_entry_names(reached, word):
        if named.is_a_progress_ask(text) and named.a_figure_on_the_doing(memory, word):
            # A progress ask about a doing the plan put a figure on is already the whole question:
            # "how long until im good at running" answers how long it takes to be able to run one,
            # and putting the plan on the end adds its figure, which reaches the row for how long a
            # 5k takes to *run*. A plan with no figure in it ("i started running") is a different
            # case, and there the plan's words are what find the timeline.
            told = _ask_a_rewritten_line(measure, memory)
            if told:
                return told
        plan = _the_plan_said(memory)
        if not plan:
            return ""
        measure = measure + " " + plan
        reached = find(understand(measure, memory))
    if reached is None or not _the_entry_names(reached, word):
        return ""
    if _the_entry_names(find(understand(text, memory)), word) and not (
            faulty and _names_a_repair(reached)):
        # The line on its own reached an entry that names the thing, which is the case this keeps
        # safe - except on a fault, where the entry it reaches is the life of the thing ("Six
        # years." for a fridge that has stopped) and the repair row is the answer that was asked
        # for.
        return ""
    if alone and word in _flat(alone):
        # The answer the line gets on its own already talks about the subject: it is about the
        # right thing and only the wording differs. "im learning spanish" / "how long until im
        # good at it" is answered with the Spanish hours, and the written-in line reached the
        # language row that says "Spanish, French or Italian" instead, which is the same answer
        # with less of the person in it.
        return ""
    answer = _ask_a_rewritten_line(measure, memory)
    if not answer:
        return ""
    if _the_line_already_has_its_answer(alone, text) and not (
            faulty and _names_a_repair(reached)):
        # A fault is the exception: "my washing machine has stopped" / "how long will it take" got
        # the life of the machine ("Six years."), and that short figure is the answer to a question
        # nobody asked. Where an entry about the repair names the thing, the repair's clock is the
        # answer and it takes the turn.
        # In a chat about reheating rice, "how long in the microwave" is answered with the rice's
        # own time by the cooking path, which is not an entry the line reaches: the figure they
        # asked for is already on the way. The rewrite is for a line that got the appliance's
        # lifespan or the search hedge, so a short answer with a figure in it is kept as it is.
        return ""
    if same_again.unframed(answer):
        # The written-in line reached an answer that is already on the screen: the rewrite found
        # nothing the line on its own did not have, and a repeat lead-in in front of the same
        # paragraph ("Nothing separate for the oven - it is the same advice: 30 to 40 minutes")
        # reads worse than the figure the line gets on its own. Only a rewrite that brings a new
        # answer takes the turn.
        return ""
    # An ask the answer already covers pulls a clause out of the paragraph on the screen, and a
    # clause on its own is not a reply: "the price" after the price of a brake job gave
    # "£100 to £200.", which is the pads alone out of a sentence that went on to say the job with
    # discs is 200 to 350. The whole of that sentence, framed as the answer already given, is
    # what a friend says.
    last_said = _flat((mem.last_bot(memory) or ""))
    whole_amount = (asked_kind(text) == "amount"
                    and SIGNALS["amount"].search(str(answer or "")) is not None)
    if (last_said and _flat(answer) in last_said
            and len(_flat(answer).split()) < _A_CLAUSE_OF_THE_ANSWER and not whole_amount):
        return same_again.instead(str(mem.last_bot(memory) or ""), text, memory) or ""
    # The same answer twice in a row is not a second answer: "how many words is that" after the
    # length of the speech gets the length again, framed as the repeat it is.
    again_said = same_again.instead(answer, text, memory)
    if again_said and not whole_amount:
        return again_said
    if _said_before(_without_lead_in(answer), memory):
        return ""
    return answer


def _the_part_of_the_thing_they_named(text, memory):
    """The answer about a part of the thing the person named, or "".

    A part follows the chat's subject for as long as the chat is about it, and the newest turn's
    words are not always that subject: after "my washing machine smells" / "i clean the filter"
    the reading joins "and the drawer every month" to "clean filter", which is no entry at all,
    and the line falls to whatever is keyed on "drawer" alone. The machine is what the person
    named, so the part is joined to that, and only an entry that is keyed on the part (the drawer
    card, not the machine's smell card read out again) and an answer the person has not already
    had takes the turn.
    """
    if not isinstance(memory, dict):
        return ""
    owner = named.the_thing_named(memory)
    if not owner:
        return ""
    part = named.about_the_thing(text, memory, owner=owner)
    on_its_own = named.about_the_thing(text, memory)
    if not part or not on_its_own or part == on_its_own:
        # No part at all, or the line is not a part follow-up. A bare "the drum" after "my
        # washing machine is noisy" is a line about the drum on its own, and the lookup already
        # answers it; "the drawer every month" is a report, and the line's own subject. Only a
        # part attached to the turn before it ("and the drawer", "what about the drum", "the
        # belt too") is asked about the thing the person named.
        return ""
    if not _ATTACHED_TO_THE_LAST_TURN.search(text):
        return ""
    if _the_part_is_what_answers(on_its_own, memory):
        # The reading from the newest turn's words does reach an entry of the part's own, so the
        # answer already on the table is that entry's and this reader has nothing to add. Only a
        # part the newest turn's words lose is written under the thing the person named.
        return ""
    if not _the_part_is_what_answers(part, memory):
        return ""
    filled = _ask_a_rewritten_line(part, memory)
    if not filled or _said_before(filled, memory):
        return ""
    return filled


def _ask_a_line_of_its_own(line, memory):
    """The answer to a line asked with nothing on the table, as if it were the first thing said.

    The line here is one the person did not type - it is their own line written out ("how long
    does it take to fit a new one" asked as "how long does it take to fit a new boiler"). Read
    with the chat's topic still in memory it reaches the entry the topic is on (how long a boiler
    is built for) rather than the one its own words fit (how long a fitting takes), so the topic
    the bot remembers is left out and the entry that answers the words is asked.
    """
    spoke = {key: value for key, value in memory.items()
             if key not in ("topic", "topics", "entry_answer", "entry_answers", "last_answer")}
    return _ask_a_rewritten_line(line, spoke)


def _the_ask_behind_a_moan(text, memory):
    """The answer to the how-to ask behind "i always get rice wrong", or "".

    The frame says the thing they do comes out badly, and the thing named is what they want to do
    properly, so the ask behind it is the how-to about that thing. It is only taken when its
    answer is about the thing the person named: read loosely, "how do i get the kids to bed
    right" reaches the frost card, and a card about the wrong thing is worse than the line that
    asked for help.
    """
    written = doing_it.the_ask_behind_a_moan(text)
    if not written:
        return ""
    said = _ask_a_rewritten_line(written, memory)
    if not said:
        return ""
    thing = written[len("how do i "):].rsplit(" right?", 1)[0]
    # The thing's own name is the last word of it that is not grammar ("the rice", "my hours",
    # "the timing"), and that is the word the answer has to have in it. A share of any words is
    # not enough: "how do i get the tax return right" reaches the trading-allowance card, which
    # says "tax" and is not about a return at all.
    named = [word for word in WORD.findall(thing.lower())
             if len(word) > 2 and word not in MOAN_STOP and word not in MOAN_VERB_WORDS]
    if not named:
        return ""
    head = said_topic.stem(named[-1])
    answered = {said_topic.stem(word) for word in WORD.findall(said.lower())}
    if head not in answered:
        return ""
    if _said_before(_without_lead_in(said), memory):
        return ""
    return said


def _ask_a_rewritten_line(line, memory):
    """The answer to a line the person did not type, read with their own reading replaced.

    The shape of answer the turn asked for is carried onto the fresh reading: the reading of the
    rewrite never passes through `bot/modules/intent.py`, which is what writes `wants`, so a module
    underneath saw a line that asked for nothing. "and for 3kg" after a chicken time lost its
    time, and the second "what should i cook tonight" in a chat lost its pick.
    """
    was = memory.get("understood")
    want = was.get("wants") if isinstance(was, dict) else None
    try:
        fresh = understand(line, memory)
        if want and isinstance(fresh, dict):
            fresh["wants"] = want
        memory["understood"] = fresh
        return _respond(line, memory)
    finally:
        if was is None:
            memory.pop("understood", None)
        else:
            memory["understood"] = was


from ..memory import again as _never_twice  # noqa: F401, E402 - applied once the module is defined


# Whatever this module answers, the last thing that happens to it is the earlier-turn
# check (bot/memory/again.replied): `answers` alone served a card again on 59 deck turns.
respond = _never_twice.replied(respond)


from ..memory import paragraph  # noqa: F401, E402 - the floor is applied once the module is defined


# And the floor under all of it: a paragraph the chat has *had* is not printed again in the same
# words. `again.replied` above frames a repeat of the answer just given; this one frames a card
# that comes back several turns later, after a turn about something else, which no reader sees.
respond = paragraph.then_framed(respond)
