"""Part 5 of 6 of a large module, split out of `arbiter`.

Everything here is re-exported from `arbiter`, so callers import it from there as before.
"""
import re

from ..compose import fallback, fit, leaving, onscreen
from ..compose import limit as _limit
from ..memory import narrow as _narrow
from ..compose.goodnews import reads_as_a_detail_of_the_news, reads_as_the_detail_line
from .arbiter_part_01 import (
    A_CEILING, A_FIGURE, A_SUM_TO_WORK_OUT, A_WORKED_OUT, GENERIC, WORD, _says_back_one_of,
    _the_figures_they_gave, _asks_it_back, CARE_THREAD, MEMORY_MODULES, SAFETY, THREAD,
    _a_recall_from_an_earlier_turn, _already, _amends_a_detail, _explains_the_method,
    _offers_the_food, _offers_what_the_line_ruled_out, _priority, _reads_the_doubt,
    _says_only_the_line, _says_what_they_already_said, _the_advice_over_a_definition,
    _the_candidates_that_hand_the_detail_back, _the_cut_the_line_asked_for,
    _the_figure_they_asked_back, _the_food_the_line_refused, _the_kind_line_they_gave,
    _the_line_asks_for_a_doing, CHATTER, _every_real_answer_offers, _the_thing_the_line_ruled_out,
    RECALL,
)
from .arbiter_part_02 import (
    _a_check_on_the_answer, _a_leaving_said_plain, _a_repeat_to_hold, _a_shorter_said_again,
    _a_whole_line_module_spoke, _about_the_line, _announces_a_repeat, _answers_this_line,
    _asks_a_question, _asks_for_a_judgement, _carries_the_answer, _composer_reading, _content,
    _hands_the_decision_back, _hurting_reply, _is_a_generic_step, _opens_on_a_job,
    _sudden_loss_reply, _the_line_is_news, _the_name_they_gave, _declares_as_it_comes,
    _the_ask_after_the_facts, _a_sign_off, _asks, A_SUBJECT_PHRASE, A_SUBJECT_WORD,
    NOT_A_SUBJECT_WORD,
)
from .arbiter_part_03 import (
    _a_run_of, _about_the_person_the_line_names, _ack_lines, _claims_instead, _draft_index, _echoes,
    _names_what_they_said, _pause_reply, _points_back, _said_it_already, _store_correcting,
    _story_goes_on_reply, _the_ask_about_a_child, _the_candidates_that_answer_the_ask,
    _the_card_that_places_the_figure, _the_cause_asked_for, _the_date_fact, _the_move_in_hand,
    _the_next_part, _the_store_revises_the_answer, _the_words_for_the_child, _a_card_besides,
    _a_real_answer_besides, _only_a_hand_back_besides, _only_says_the_line_back,
    _the_answer_again_with_a_tail, _the_reply_is_the_report, _the_quoted_repeat,
)
from .arbiter_part_04 import (
    _carried_words, _names_the_answers_figure, _names_the_subject,
    _a_choice_the_answer_did_not_make, _a_presence_check, _about, _about_the_bot, _fit, _instead,
    _last_reply, _match, _named_topics, _only_acknowledges, _said_before, _the_answer_handed_back,
    _the_answer_written_out, _the_bots_own_taste, _the_venue_hours_turn, _the_whole_move,
    _thread_index, _verdict_reply, _a_declaring_specialist_besides, _a_fresh_answer_besides,
    _declared, _labels,
)


def _the_candidates_with_a_figure(text, memory, candidates, pool):
    """The candidates whose reply carries the figure a how-much line asks for, or the pool.

    "my car needs a service" / "how much" was answered "12 months." by the memory store, which
    had the same card's duration and not its £150 to £250, while the answers candidate had the
    price. A how-much line that asks for an amount wants a figure in a unit or a currency, so a
    candidate without one stands down when another has it. A ceiling ask is left alone, because
    "no amount is safe" is the answer and has no figure. Nothing changes when every candidate
    lacks a figure, or every one has it: the first candidate still takes the turn.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict) or understood.get("wants") != "amount":
        return pool
    line = str(text or "")
    if not re.search(r"\bhow much\b", line, re.I):
        return pool
    if A_CEILING.search(line):
        # A ceiling line is answered by a card, and a candidate that only hands the last answer
        # back under a repeat frame says nothing new: "how much is too much" after the paracetamol
        # card got "Same as before: <the card>" over the card itself. When every candidate is
        # framed, the pool is left as it was.
        plain = [index for index in pool
                 if not _limit.FRAME.match(str(candidates[index].get("reply") or "").strip())]
        return plain or pool
    money = _narrow.SIGNALS.get("money")
    figure = (money, _narrow.SIGNALS.get("amount"))
    # The person's own figure is a figure. "i pay 30 a month for my phone" / "how much do i spend
    # on my phone" is answered by the store saying the sum back ("You told me 30 on phone."), and
    # that reply carries a digit but no currency word - so on a how-much line it stood down for
    # any card with a £ in it and the person's own bill lost to the country's average. A reply
    # that names a number the person gave is about their figure, whatever unit it is written in.
    theirs = _the_figures_they_gave(memory)
    # The candidate has to be about the thing asked about as well as carry a figure: an
    # emergency-fund question was handed a business-funding card only because "£500 to
    # £25,000" is a figure. The subject words come from the line and the one it follows, and a
    # generic "should" or "about" is no subject at all.
    subject = {word for word in (set(WORD.findall(line.lower()))
                                 | _carried_words(memory))
               if len(word) >= 5 and word not in GENERIC}
    # A line that asks for the sum they gave is answered by it, and a line that asks for a sum to
    # be worked out is not. Both look the same to the reading here except for the verb, so the
    # verb decides which replies may stand on the figure alone.
    to_work_out = bool(A_SUM_TO_WORK_OUT.search(line))
    with_figure, says_it_back, bare_echo = [], [], []
    for index in pool:
        reply = str(candidates[index].get("reply") or "")
        has_figure = any(signal and signal.search(reply) for signal in figure)
        quotes = _says_back_one_of(reply, theirs)
        if not (has_figure or quotes):
            continue
        if quotes:
            # The reply names their figure, so it is about the thing asked whatever words it uses:
            # "You said 150." names none of the line's words, because they were in the line before
            # it, and the subject test would drop the one reply that answers the question. One
            # that works something out of it - "None - 10 glasses is already past the six to eight
            # glasses that answer named", "£1,100 a month more rather than the £100 you have" - is
            # kept ahead of one that only hands the figure back.
            # Money rather than any unit: "150 g of mince each" beside the number of guests is the
            # card's own arithmetic, not their figure worked out.
            new_figures = {one for one in A_FIGURE.findall(reply)} - theirs
            if new_figures and (money.search(reply) or A_WORKED_OUT.search(reply)):
                says_it_back.append(index)
            elif not new_figures and not to_work_out:
                # Only the bare saying-back stands on their figure alone. A reply that quotes it
                # and then lists its own card's numbers ("For 4, spaghetti bolognese is about
                # 150 g of mince ... 600 g") has not worked anything out, so it takes no standing
                # from the quote.
                bare_echo.append(index)
            continue
        if subject:
            said = {word for word in WORD.findall(reply.lower()) if len(word) >= 5}
            if not any(_the_same_word(word, one) for word in subject for one in said):
                continue
        with_figure.append(index)
    for best in (bare_echo, says_it_back, with_figure):
        if best and len(best) < len(pool):
            return best
    return pool


def _the_candidates_that_give_the_shape(text, memory, candidates, pool):
    """The candidates whose reply gives the shape of answer the line asked for, or the pool.

    The figure rule below was the first of these and the only one: a how-much line was owed a
    figure, and a candidate without one stood down when another had it. The same is true of every
    shape the understanding lane's reading can name - a time, a place, a person, a pick, a yes or
    a no, the steps, the reason, the meaning - and the shape is not the composer's business, so it
    is read once, in `bot/compose/fit.py`, and honoured here for all of them. "my boiler keeps
    losing pressure" / "is that normal" was answered by the memory store reading the last answer
    back under a repeat frame while the composer's verdict line was in the candidates.

    Only a candidate that *definitely* misses the shape stands down, and only for one that
    definitely gives it: where the words cannot tell, the order is left alone. `amount` keeps its
    own reading, because a figure has to be in a unit or a currency and has to be about the thing
    the line named, and that care is worth keeping.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return pool
    want = understood.get("wants")
    if not want:
        return pool
    if want == "amount":
        return _the_candidates_with_a_figure(text, memory, candidates, pool)
    if want in fit.SOFT:
        return pool
    if want == "yesno" and _names_the_answers_figure(str(candidates[pool[0]].get("reply") or ""),
                                                    memory):
        return pool
    if _a_check_on_the_answer(str(candidates[pool[0]].get("reply") or "")):
        return pool  # a check on the answer above is the shape the line asked for
    if not pool or fit.gives(str(candidates[pool[0]].get("reply") or ""), want, text) is not False:
        return pool
    # The shape is not the whole of it: on a bare doubt ("is that dangerous", four turns into a
    # boiler chat) the composer's line gives the shape and says nothing about the boiler - it asks
    # the person to say the doubt again ("Where is the worry?") - while the card already given is
    # the answer. A line that hands the question back is not the answer to it, so it does not take
    # the turn off an entry that does answer the thing, whatever shape its line gives. This is the
    # same reading as `_names_the_subject` below, applied here because this filter runs first.
    words = set(WORD.findall(str(text or "").lower()))
    subject_known = _names_the_subject(candidates[pool[0]], memory, words) if pool else True
    giving = [index for index in pool[1:]
              if fit.gives(str(candidates[index].get("reply") or ""), want, text) is True
              and (not subject_known
                   or _names_the_subject(candidates[index], memory, words)
                   or not _asks_it_back(candidates[index].get("reply")))]
    if not giving:
        return pool
    return giving + [index for index in pool if index not in giving]


def _the_same_word(one, other):
    """True for the same word, or a plural or a short ending of it ("service"/"services")."""
    if one == other:
        return True
    short, long = sorted((one, other), key=len)
    return len(short) >= 5 and long.startswith(short) and len(long) - len(short) <= 2


def _choose(text, memory, candidates):
    real = [index for index, candidate in enumerate(candidates) if _priority(candidate) >= 0]
    if not real:
        return 0
    last = _last_reply(memory)
    if last and _the_line_is_news(text):
        # The line reports the thing the last answer was about coming back ("my back is sore
        # again", "and the rota changed again this morning"), so it is news, and an answer under a
        # lead-in that says it is the same one misreads it: a person saying the trouble has
        # returned wants the next step, not the paragraph from a turn ago read out again. Any
        # candidate that does not announce itself as the old answer is better, a stock line
        # included. That is the reverse of the never-repeat rule below, and for the same reason: a
        # repeat is right for a bare ask to hear the answer again and wrong for a report that it
        # has happened once more. A request to be reminded ("what was the headache thing again")
        # and a question ("how do i cook rice again") are asks, not news, and
        # `returned.says_it_happened_again` is what tells the two apart.
        def _hears_the_news(index):
            # Only the announced repeat is dropped here: a candidate that shares words with the
            # last answer is the never-repeat rule's business further down, and that rule has the
            # choice between them in front of it. This is about the lead-in alone.
            return not _announces_a_repeat(candidates[index].get("reply"))

        hearing_it = [index for index in real if _hears_the_news(index)]
        if not hearing_it:
            # A fallback is in the race here, which is the one place it is: the stock line that
            # answers the news ("Does it come and go, or is it there all the time?") is a better
            # reply to "my back is sore again" than the answer from the first turn read out. Only
            # when no real candidate hears the news, so a specialist keeps its turn.
            hearing_it = [index for index in range(len(candidates)) if _hears_the_news(index)]
        if hearing_it and len(hearing_it) < len(candidates):
            real = hearing_it
    best = real[0]
    if _priority(candidates[best]) >= SAFETY:
        return best  # the safety band is answered as it comes, before the never-repeat rule
    amended = _amends_a_detail(text, memory)
    if amended:
        # A detail of their own plan is being changed, and the reply that carries the new detail is
        # the one that answers it: "actually we fly in september" was answered with the fruit-fly
        # card, because an entry matched the word "fly" inside the amendment.
        every = list(range(len(candidates)))
        handed = _the_candidates_that_hand_the_detail_back(amended, candidates, every)
        if handed[0] != best:
            # It goes into the race as well as to the front: every filter below reads `real`, and
            # the fallback is not in it, so a line promoted here and not added back is demoted
            # again by the next rule that keeps the top of the race.
            real = [handed[0]] + [index for index in real if index != handed[0]]
            best = handed[0]
    # One check, for every module: a reply that talks about the conversation needs one to have
    # happened, and this is the place every candidate passes through. It is made here as well as
    # in the pools (`bot/modules/chat.py`) because the reading is what has to be shared, not the
    # guard: another module's reply can refer to an earlier turn too, and on the first line of a
    # chat there is none. Where every candidate refers to a chat, the top one stands - a reply
    # still has to be given.
    if not onscreen.earlier_turn(memory):
        fresh = [index for index in real
                 if not onscreen.talks_about_the_conversation(candidates[index].get("reply"))]
        if fresh:
            real = fresh
            best = fresh[0]
    # A check on the answer above keeps the turn the composer gave it. The entry that scores
    # higher further down is the topic's, and a check is not about the topic but about the method
    # in the answer: "how do i descale the kettle" / "would that be worth it" was answered with
    # the kettle-buying card ("Get a 3kW one for speed"), "my laptop wont turn on" / "shall i try
    # that" with a second fault-finding card, and "how do i stop my phone battery draining" /
    # "will that help" with the same paragraph again. The composer only writes this line after
    # reading the check against the answer above, so an entry it stood aside for never gets here.
    # A reply that takes up the answer's own figure ("10 minutes is short of the 20 minutes that
    # answer named") is answering the check better and keeps the turn; see
    # `_names_the_answers_figure`.
    if _a_check_on_the_answer(candidates[best].get("reply")):
        explained = [index for index in real
                     if index != best and _explains_the_method(candidates[index].get("reply"))]
        if not explained:
            return best
        best = explained[0]
    # A line pointing back at a figure the person gave gets the reply that carries it, before any
    # of the rules below get to hand the turn to a module that read the line on its own.
    back = _the_figure_they_asked_back(candidates, real, memory, text)
    if back is not None:
        return back

    # A condolence is not the answer to a question about why a living thing is failing: the entry
    # that names the thing answers the cause that was asked for, and it is read before the claims
    # because the condolence's own module is the one that claims the line. See
    # `_the_cause_asked_for`.
    cause = _the_cause_asked_for(candidates, real, text, best)
    if cause is not None:
        return cause
    # A verdict on the news has no subject of its own, so nothing may answer it with the topic of
    # the conversation: not the same-advice path, and not an entry that owns the verdict's noun
    # ("Nightmares usually follow stress"). The composer has the line for it, so the turn is the
    # composer's, taken before the claims - except in a thread that is not a light one, where the
    # safety continuation or the grief answer stands.
    verdict = _verdict_reply(candidates, text, memory, last, clean=text, best=best)
    if verdict is not None:
        return verdict
    # Before the hand-back rule: an ask to have the answer put a plainer way is answered by the
    # candidate that explains it, not by the same words handed back. See
    # `_a_plainer_reading_of_the_same_answer`.
    plainer = _a_plainer_reading_of_the_same_answer(candidates, best, text, memory)
    if plainer is not None:
        return plainer
    handed_back = _the_answer_handed_back(candidates, text, memory, last)
    if handed_back is not None:
        return handed_back
    # A line that asks for the kind of detail an earlier line of theirs gives is answered by that
    # line rather than by nothing in particular. "what make was it again" after "its a worcester
    # bosch" was answered with the pressure advice of the turn before ("Same answer, and it covers
    # this: top the pressure up"), and "where did we get the paint again" with a card about tins;
    # both are answers to a question nobody asked.
    #
    # It is a step over the modules that do not answer the named detail - the small talk, and the
    # card that merely names a word of their line - and never over a module that says the same
    # detail in its own words: the store phrases a value better ("Your sister lives in Leeds") and
    # it is the store that holds a correction ("no, 5 foot 8"), so its answers are left alone.
    if _the_kind_line_they_gave(text, memory):
        front = candidates[real[0]].get("module")
        for index in real:
            if candidates[index].get("module") == "said_back":
                # A said_back that already leads keeps the lead: "and what time was it" had the
                # line and still lost the turn to a heating card that names a figure, because a
                # card is preferred for the shape of the ask. The person asked for their own time.
                if front in ("chat", "greeting", "answers") or index == real[0]:
                    return index
    held = _as_it_comes(text, memory, candidates, last)
    if held is not None:
        # A how-much line is owed a figure even when the claim is a recall of the card: "my car
        # needs a service" / "how much" was claimed as "12 months." while the answer's £150 to
        # £250 was in another candidate. See `_the_candidates_with_a_figure`.
        with_figure = _the_candidates_that_give_the_shape(
            text, memory, candidates, [held] + [index for index in real if index != held])
        if held not in with_figure:
            held = with_figure[0]
        elif (with_figure[0] != held
              and _the_line_asks_for_a_doing(memory)
              and _says_what_they_already_said(candidates[held].get("reply"))):
            # The claim hands back something the person has already said, and the filter has
            # already read it as missing the kind of answer the line asked for while putting one
            # that gives it in front: "i have a job interview on friday" / "what do i say when
            # they ask why i want this job" was claimed at the recall band and answered "You said
            # Friday." - the day already in their own first line - with the card that says how to
            # answer the question sitting beside it. A claim on their own words is a claim on a
            # value they already have, so it keeps the turn only when it is the answer asked for.
            held = with_figure[0]
        # A claim is the whole of the reason to take the turn, so it is only given up to a module
        # that says the line is its own answer at a higher PRIORITY: a claim from the fallback
        # band never beats a specialist that read the line, and a claim from a module above it
        # still does.
        instead = _claims_instead(text, memory, candidates, last, _priority(candidates[held]))
        if instead is not None and _offers_what_the_line_ruled_out(candidates[instead], text, memory):
            instead = None
        return held if instead is None else instead
    pool = _the_candidates_that_give_the_shape(text, memory, candidates, real)
    real = pool
    # The fact the person has just stated in the very line they are asking about is not something
    # to recall: "my sister is veggie and shes coming to dinner, what can i cook" was answered
    # "Your sister is veggie." The store claims a line for the fact in it, at the recall band,
    # while the cooking answer sits beside it at 0 - the fact was never in doubt and the ask after
    # it was. A reply made of nothing but the words the person has just used has told them nothing
    # at all, so it stands down for one that answers the ask.
    answering = _the_candidates_that_answer_the_ask(text, candidates, pool)
    if answering is not None:
        pool = answering
        real = answering
    # The candidate in front offers the very food the line refused, and another real candidate
    # does not: "im trying to eat better but i hate veg" got the balanced-meal card ("Half the
    # plate vegetables or salad"), which is the one thing the line had ruled out, while the store
    # had already answered the refusal. The refusal is read once by the kitchen, and only the
    # reply's opening sentence is checked (`_offers_the_food`), so a substitute that names the
    # food to leave it out keeps its turn. The safety band and a pool where every candidate
    # offers it are left exactly as they were.
    refused = _the_food_the_line_refused(text, memory)
    if refused:
        respecting = [index for index in pool
                      if not _offers_the_food(candidates[index].get("reply") or "", refused)]
        if respecting and len(respecting) < len(pool):
            pool = respecting
            real = respecting
    cut = _the_cut_the_line_asked_for(memory, candidates)
    if cut is not None:
        # The line ruled something out and this reply is the answer above with that thing taken out
        # of it: "Right — no walking up hills, then." and then the plan without the walking. That is
        # a repeat the person asked for, so the never-repeat rule below does not apply to it, and
        # the knowledge base's card for the word they just refused does not take the turn.
        return cut
    if last:
        # A reply that says the last answer again with a nod in front ("Same as before: ...",
        # "You've got it: ...") is not a second answer, so it is passed over whenever a real
        # candidate has something new to say. Fallbacks are not counted here: a stock line is not
        # a reason to drop an answer, and STYLE.md would rather have the answer twice than a shrug.
        # A search hedge is not something new to say. "I don't know enough to answer that
        # honestly. A search should sort you out quickly" was given the turn over the answer the
        # bot had just read out, so a bare "what helps" was met with a shrug on a subject it had
        # answered a turn before. The answer said again is better than that, so a hedge never
        # counts as the fresh candidate the repeat is passed over for.
        #
        # The same goes for a whole answer the bot already gave this person two or more turns
        # back: "when should i do that", nine turns into a chat about a boy starting secondary
        # school, was handed the walk-the-route paragraph from the first turn word for word, while
        # the composer had a line about what to ask him. Only an answer the conversation has
        # already moved past is dropped, and only when the candidate in front of it is not one:
        # a line that asks to hear it again ("what did you say") keeps it, and so does the same
        # question asked twice in a row.
        #
        # A reply that only points back at the answer above is the same shrug in better words:
        # "Everything I know on that one is in the answer above" is new wording that says where
        # the answer is. See `_points_back`.
        heard = _said_before(memory, text)
        # A cut of an answer already read is not a fresh answer: "how long do i roast a leg of
        # lamb" / "its 2 kilos" / "and how long per kilo" was given the whole card a second time
        # with its last sentence taken off. The card in this list is that shorter cut, so it says
        # nothing word for word that the whole-reply test below can catch while repeating what the
        # person has on the screen, and it beat the one line that answers the ask - "25 minutes
        # per 500g.", the composer's own cut - on the match.
        #
        # The shape has to be the cut and not a repeat with something in front of it: "is that
        # dangerous", four turns into a boiler chat, is answered by the boiler paragraph with "Same
        # answer, and it covers this:" in front, and that is the whole of the answer the person is
        # asking about (`tests.test_long.ANameIsNotGreetedAgainTest`). So the words of the
        # candidate have to sit inside an earlier answer as one run and be shorter than it - the
        # card a sentence short, or the tail of it - where a lead-in of its own takes it out.
        cut = {}
        for index in pool:
            words = _content(candidates[index].get("reply")).split()
            if len(words) < 8:
                continue
            for line in heard:
                was = line.split()
                if len(words) < len(was) and _a_run_of(was, words):
                    cut[index] = was
                    break
        fresh = [index for index in pool
                 if _content(candidates[index].get("reply")) != last
                 and not _echoes(candidates[index].get("reply"), last)
                 and not fallback.is_a_hedge(candidates[index].get("reply"))
                 and not _points_back(candidates[index].get("reply"))]
        if cut:
            held = [index for index in fresh if index not in cut]
            # The turn may only go to a line made out of the same answer's words: the composer's
            # own cut of the card in hand ("25 minutes per 500g." out of the lamb card) is a run
            # inside it, so the person still hears the answer they asked about, narrowed. A line
            # about something else is not that answer at all: "its a hybrid with a shimano
            # groupset", three turns into a chat about a second-hand bicycle, had the car-hybrid
            # paragraph waiting behind the bike price, and dropping the price handed the turn to
            # the car. When nothing is left but a different subject, the cut stays.
            if held and any(_a_run_of(cut[gone], _content(candidates[take].get("reply")).split())
                            for take in held for gone in cut):
                fresh = held
        if fresh and _content(candidates[pool[0]].get("reply")) not in heard:
            fresh = [index for index in fresh
                     if _content(candidates[index].get("reply")) not in heard] or fresh
        if (fresh and _a_repeat_to_hold(memory, text)
                and _echoes(candidates[pool[0]].get("reply"), last)):
            # A line that asks to hear the answer again is answered by that answer, so an echo of
            # it is not the same thing twice. "say that again" over the boiler answer was passed
            # over here as a repeat while the knowledge entry that read the pointer as the same
            # question said something else entirely (a podcast answer, under a boiler), and that
            # line took the turn because it was the only fresh one. The candidate in front is the
            # store's hand-back with a lead-in on it, which is the answer to a repeat ask by
            # definition, so nothing is dropped for echoing.
            #
            # Only when the hand-back is in front: a repeat that names a figure comes back as the
            # figure alone ("Again — 15 minutes"), which is not an echo of the paragraph it came
            # out of, and dropping the others there would hand the line to the card that wrote the
            # paragraph instead (tests.test_a_repeat_ask_keeps_the_recall reads that the other way
            # round on purpose: the card keeps the turn when the store has nothing but the answer
            # again). See `_fit`, which weighs the same two.
            fresh = []
        if fresh:
            pool = fresh
        else:
            if len(pool) > 1:
                # Every candidate says the last answer again, so this turn is a repeat whichever
                # one wins, and the one that repeats least is the best of them: "The thing to do
                # first: put a tall scratching post by the corner she uses" is a nod plus the one
                # step, while the knowledge entry behind it is the whole paragraph read out a
                # second time. It has to be an echo of the answer itself (so a short new answer is
                # never taken for one) and clearly shorter than the longest repeat beside it.
                shortest = min(pool, key=lambda i: len(_content(candidates[i].get("reply"))))
                longest = max(len(_content(candidates[i].get("reply"))) for i in pool)
                if (_echoes(candidates[shortest].get("reply"), last)
                        and len(_content(candidates[shortest].get("reply"))) * 3 <= longest * 2):
                    return shortest
            # Every module with a real claim on the line only says the last answer again: the
            # knowledge entry reads the follow-up as the same question and hands back the opening
            # of the answer just given, word for word. Nothing else is in the race, so the same
            # sentence twice is what the person gets - unless the composer has read the line as a
            # repeat and said so. That line is the only new thing on the table, and it is a
            # question about the answer rather than a shrug, so it takes the turn. It is the
            # composer's own reply, never a raised PRIORITY (see bot/compose/fallback.py,
            # `says_it_already`).
            # The composer's own short form of that answer is a cut of it, not a second telling,
            # so it is the one line here with something the person has not read. Read before the
            # said-it-already line, which asks whether what the cut lost is what they asked
            # about, because a bare "what?" asks for nothing the cut has to keep.
            shorter = _a_shorter_said_again(candidates, last)
            if shorter is not None:
                return shorter
            said = _said_it_already(candidates, text, memory, last)
            if said is not None:
                pool = [said]
            else:
                choice = _a_choice_the_answer_did_not_make(candidates, text, memory, last)
                if choice is not None:
                    pool = [choice]
                elif not [index for index in pool
                          if _content(candidates[index].get("reply")) == last]:
                    # Every real candidate is a slice of the last answer rather than the whole of
                    # it, and the composer has no line of its own about the repeat. A slice read
                    # back can still answer a narrower question ("and what does a major mean" is
                    # in the fail-sheet sentence word for word), so it is only given up to a
                    # fallback line that says what to do about the thing - see
                    # `_answers_this_line`. The composer's own shrug ("Got it - it goes off in two
                    # days") answers nothing, so it never takes the turn off the slice, and the
                    # whole answer said again is left alone either way.
                    unheard = [index for index, candidate in enumerate(candidates)
                               if not _echoes(candidate.get("reply"), last)
                               and _answers_this_line(candidate.get("reply"))]
                    if unheard:
                        pool = unheard
                    # Every real candidate only points back at the answer above, and a line
                    # that carries a piece of that answer is on the table. A reply that only says
                    # where the answer is has answered nothing, so the line that says something
                    # takes the turn: "how much does a boiler cost" / "how long does it take to
                    # fit" / "what about a new one" was told "Everything about a new is in what I
                    # said above - there is no more than that", while the composer had "For a new
                    # one: Fitting a new one is the long job." The reading of "a piece of the
                    # answer" is the composer's, which the arbiter already asks for elsewhere
                    # (`_carries_the_answer`), so a stock line, a hedge or a passing mention
                    # never takes a turn this way.
                    if all(_points_back(candidates[index].get("reply")) for index in pool):
                        says = [index for index in range(len(candidates))
                                if not _points_back(candidates[index].get("reply"))
                                and not fallback.is_a_hedge(candidates[index].get("reply"))
                                and _carries_the_answer(candidates[index].get("reply"), memory)]
                        if says:
                            pool = says

    # A take from the chatter band is picked on what the line was read as - a feeling, a kind of
    # day - and it says nothing of the line itself, because a stock line never can. That is right
    # where the reading was the whole of the line, and wrong where a card beside it answers the
    # thing the person actually named: the pool for a lonely week answered "my bins were left out
    # and not emptied" over the council card that says what to do about the missed collection. So
    # a chatter take that shares no word with the line stands down for a card that shares one, and
    # every line whose words the take does say is left exactly as it was.
    # A detail added to news the bot has just cheered is the news again, not a question about the
    # subject it happens to share a word with: "i passed my driving test" / "first time" got the
    # forty-five hours of lessons card, and "we won on saturday" / "2-0" got "That's 2". The pool
    # that reads the detail as news is on the table in both, and it is the one reply that answers
    # what the person actually said, so the subject card stands down for it - the reading is the
    # composer's (`bot/compose/goodnews.py: reads_as_a_detail_of_the_news`), and this only says
    # which candidate takes the turn.
    detail = _a_detail_added_to_the_news(candidates, pool, text, memory)
    if detail is not None:
        return detail
    named = _a_card_that_names_the_line(candidates, pool, text, memory)
    if named is not None:
        return named
    # A follow-up that adds a thing the answer above never covered is not answered by that answer
    # again. "how do i get a stain out of a wool jumper" / "its a coffee stain" / "also how do i
    # stop it shrinking next time" got "The thing to do first: Blot up as much as you can with
    # kitchen paper" - the first step of the stain answer read out a second time - while the entry
    # that says what to do about shrinkage ("Shrinkage is heat and agitation, so wash cool") was in
    # front of it at a lower band. The widest-reaching form of `_names_the_subject`: the added word
    # has to be in the reply, and the band rule is only set aside below the store's recall.
    added = _the_answer_that_names_what_the_line_added(candidates, pool, text, last)
    if added is not None:
        return added
    best = pool[0]
    own, carried, words, clean = _about(text, memory)
    # The same ask one turn later, in the thread of a condolence: "how do i tell a 4 year old".
    # A card that matches "a 4 year old" answers how much screen time is right, which is not the
    # question, and no knowledge entry is in the candidates to lose to.
    child_words = _the_words_for_the_child(candidates, clean, memory, last)
    if child_words is not None and not _a_whole_line_module_spoke(candidates):
        return child_words
    # A thank-you is not a question about the world. "cheers" after "what can i do with a bag
    # of frozen spinach" was answered with the spinach entry a second time: the reading hands a
    # follow-up the topic the conversation is on, so the knowledge base had "cooking" to match
    # and the small-talk candidate had nothing but its own priority. On a line the understanding
    # engine reads as politeness alone there is no topic of the line's own to match, so the topic
    # rule is skipped and the turn goes to the highest PRIORITY: the seed rule the bands are for.
    polite = _only_acknowledges(memory)
    here = _a_presence_check(memory)
    ask = _the_ask_about_a_child(candidates, clean, last)
    if ask is not None:
        return ask
    gave = _the_name_they_gave(candidates, text, memory)
    if gave is not None:
        return gave
    drafted = _draft_index(candidates, last, clean)
    if drafted is not None:
        return drafted
    # The card for the speaker's own life does not answer a how-to about somebody else.
    about_them = _about_the_person_the_line_names(candidates, pool, clean, last)
    if about_them is not None:
        return about_them
    instead = _instead(text, candidates, last, own, clean)
    if instead is not None:
        return instead
    # A line that says the person is going is not a question about its reason clause: "ill let
    # you go, dinner is burning" was answered "take it off the heat". The composer owns the
    # reading and the wording (bot/compose/leaving.py); this is only the routing decision.
    bye = _leaving_reply(candidates, own, carried, words, clean, text, memory, last)
    if bye is not None:
        return bye
    left = _a_leaving_said_plain(candidates, pool, clean, memory)
    if left is not None:
        return left
    sudden = _sudden_loss_reply(candidates, pool, clean)
    if sudden is not None:
        return sudden
    bot_answer = _about_the_bot(candidates, clean, last)
    if bot_answer is not None:
        return bot_answer
    # When a named place opens is not a fact any entry can hold, so the composer's honest line
    # answers it rather than an entry that took the line on one other word. See
    # `_the_venue_hours_turn`.
    hours = _the_venue_hours_turn(candidates, clean, last, text)
    if hours is not None:
        return hours
    # A question about the bot's own taste has no entry in the knowledge base: "do you have a
    # favourite food" was answered with a list of dishes to cook and "whats your favourite thing
    # to talk about" with advice on starting conversations. Both are good answers to the
    # questions they were written for and neither is an answer to what this person asked, so the
    # composer's taste takes the turn from a card that only matched the noun.
    own_taste = _the_bots_own_taste(candidates, clean, memory, last)
    if own_taste is not None:
        return own_taste
    corrected = _store_correcting(candidates, pool, memory, text, last)
    if corrected is not None:
        return corrected
    # The store taking its own suggestion apart when the line says what is out of it. It is the
    # only module that read the dislike, and its reply is the answer in hand with that one thing
    # gone, so no entry can answer in its place.
    revised = _the_store_revises_the_answer(candidates, pool, memory, text, last)
    if revised is not None:
        return revised
    # A bare "where do i start" asks for the one step out of the answer in hand, and the entry
    # that wrote that answer writes it again - in its other wording, at full length - when the same
    # line reaches it. That second paragraph is not a better answer than the composer's short form
    # of the answer, so the step takes the turn. See `_the_move_in_hand`.
    step = _the_move_in_hand(candidates, real, text, last)
    if step is not None and not _points_back(candidates[step].get("reply")):
        return step
    # The same ask, where no candidate re-tells the answer: two modules hand the step back and the
    # one in front stops at the answer's own comma, so half of the instruction is handed over. The
    # composer keeps the answer's sentence, and on this ask that is the reply to give.
    whole = _the_whole_move(candidates, real, text, last, _the_answer_written_out(memory))
    if whole is not None and not _points_back(candidates[whole].get("reply")):
        return whole
    # "what else" after a step asks for the next part of the same answer, and the entry that wrote
    # it answers with the whole paragraph again. The memory lane has the next part, so it takes the
    # turn. See `_the_next_part`.
    more = _the_next_part(candidates, text, last)
    if more is not None and not _points_back(candidates[more].get("reply")):
        return more
    # "when do we fly", "when is my dentist appointment": the person has already told the bot the
    # date, and a knowledge card about the subject answers a different question than the one asked.
    dated = _the_date_fact(candidates, real, text)
    if dated is not None:
        return dated
    # The next line of a hard story is not a request about its words: after "my wife left me",
    # "she packed her things last night" matched the moving entry and got a removals checklist.
    # The composer's listening line keeps the floor with them instead. Only the composer's own
    # pool can take the turn here, and only for a line that is not a question.
    hurt = _hurting_reply(candidates, pool, clean)
    if hurt is not None:
        return hurt
    story = _story_goes_on_reply(text, memory, candidates, last)
    if story is not None:
        return story
    paused = _pause_reply(candidates, pool, text, memory, last)
    if paused is not None:
        return paused
    # The line as typed, not the normalised one: the composer picks its continuation from the
    # words in front of it, and "you there?" inside a live emergency thread must get that thread's
    # line back, not whatever "you there" alone reads as. Stripping the mark cost the thread.
    kind, target = _composer_reading(text, memory)
    if not own and not carried and not words and kind not in (THREAD, CARE_THREAD):
        # Nothing in the line to match on, so the best candidate stands - unless the composer is
        # still holding a thread for it. A follow-up written entirely as a pronoun names nothing a
        # module can match ("will i feel better", "does it get better"), so this early return handed
        # a live emergency to whatever card had a candidate: an overdose was answered with the
        # grocery price card, a breathing emergency with the same one. The reading above is the
        # composer's, so the thread only keeps the turn when the composer has a line for it.
        return best
    if kind in (THREAD, CARE_THREAD):
        keeping = _thread_index(candidates, real, _named_topics(memory), target, last,
                                care_about=clean if kind == CARE_THREAD else "", memory=memory,
                                line=text)
        if keeping is not None:
            return keeping
    if polite or here:
        return pool[0]
    fit_own, fit_carried = _fit(own, carried, memory, _priority(candidates[best]),
                                 candidates[best].get("reply") or "",
                                 candidates[best].get("module") or "", text)
    best_score = _match(candidates[best].get("module"), fit_own, fit_carried, words, clean)
    # A follow-up that asks what to do next is answered from the answer the person was given a
    # turn ago, and that answer is what the composer's line carries. An entry that answers the
    # conversation's topic but none of the answer's words is a different fact, and taking the turn
    # with it reads as a change of subject: after "my son wont eat vegetables" / "what do i do",
    # "what should i do" got "Five a day is 400g, and a portion is a handful" instead of the step.
    # Only a claim on a topic the line does not name is held to this, so "and how long?" after a
    # cooking answer still belongs to the cooking entry.
    kept = _carries_the_answer(candidates[best].get("reply"), memory)
    named = _named_topics(memory)
    # A generic step from the composer is what the person gets when nothing behind it can be
    # handed on. An entry that already tells them what to do answers the same question with the
    # thing itself, so the step stands down: after "im lonely" / "what can i do" the loneliness
    # entry says "Do the inviting yourself, and make it the same thing each week", and the
    # composer's first-step line took the turn off it. Wording only, so no entry is read as a
    # repeat it is not, and a step the person asked for by name is still the composer's (the
    # rule above, before this one).
    if _is_a_generic_step(candidates[best].get("reply")):
        for index in pool[1:]:
            entry = candidates[index].get("reply")
            if entry and not _is_a_generic_step(entry) and _opens_on_a_job(entry):
                return index
    recall_from_earlier = _a_recall_from_an_earlier_turn(text, memory)
    # The closest reply to a doubt is the entry that gave the answer being doubted: it comes back
    # to its own words, so it is about the thing the person named rather than about lines of that
    # kind. A composer line that rules on a doubt says something true of every doubt of its kind
    # ("it is the sort of thing that shrinks as soon as somebody official is told about it"), which
    # is right when the entry behind it answers something else and wrong when the entry is the
    # same one again. Found in review by @smooth-lark: after "i missed a credit card payment" /
    # "is that bad" the card named the late fee, the interest and the mark on the credit file, and
    # the money pool replaced all three with the sentence the rent and the fine get.
    if _reads_the_doubt(candidates[pool[0]]):
        for index in pool[1:]:
            if _carries_the_answer(candidates[index].get("reply"), memory):
                return index
    for index in pool[1:]:
        if (recall_from_earlier
                and candidates[best].get("module") in MEMORY_MODULES):
            # The store has answered a line that asks what was said earlier. A topic entry that
            # scores on one of the line's words is answering a different question, so it does not
            # take the turn on that score alone.
            continue
        if (not _names_the_subject(candidates[index], memory, words)
                and _reads_the_doubt(candidates[pool[0]])):
            continue
        score = _match(candidates[index].get("module"), fit_own, fit_carried, words, clean)
        if score <= best_score:  # ties keep the higher PRIORITY, which comes first
            continue
        # About the line's subject, and not only about one of its words: the candidate in front
        # is about what the person said and the entry lifting past it is about something else
        # that shares a topic label with it. See `_about_the_line`.
        if (_about_the_line(candidates[best].get("reply"), words, clean)
                and not _says_only_the_line(candidates[best].get("reply"), words)
                and not _about_the_line(candidates[index].get("reply"), words, clean)):
            continue
        # A report of a step the person has just taken is not a request for that step again. After
        # "i had a row with my sister" / "i already told her sorry" the relationships entry scored
        # on the topic and answered "Name what you did, say why it was wrong ... I'm sorry": the
        # advice the person had just told the bot they had taken. The store read the line ("Good.
        # What happened when you did?"), and it is the store's reply that belongs here, so an
        # entry that still hands over that step does not take the turn on its topic alone. The
        # reading is the store's (`already.tells_them_the_step_again`), and it is only consulted
        # when the candidate in front does not repeat it as well.
        if (_already is not None
                and _already.tells_them_the_step_again(candidates[index].get("reply"), text, memory)
                and not _already.tells_them_the_step_again(candidates[best].get("reply"),
                                                           text, memory)):
            continue
        if kept and _match(candidates[index].get("module"), named, carried, words, clean) <= 0:
            entry = candidates[index].get("reply")
            if not (_carries_the_answer(entry, memory) or _opens_on_a_job(entry)):
                continue
        best, best_score = index, score
    # The person asked the bot to rule on their plan and the front of the list rules on nothing:
    # "im thinking of quitting my job" / "is that a good idea" was answered "I cannot call that one
    # for you. Tell me what matters most about quitting my job and I will help you think it
    # through", while the card under the floor had the answer the bot can give ("Yes - quitting
    # your job is worth doing. The one thing to have ready is an answer for what if it goes
    # wrong."). A hand-back is not an answer to a judgement - it is the answer to not knowing what
    # to say - so a card that names the subject of the thread takes the turn off it. Only the ask
    # itself is read here, and only a card that names the subject: an ack ("Alright then") is the
    # same shrug in shorter words, and a card about something else is not an answer either.
    # See STYLE.md, "say what you think" against "I cannot call that one for you".
    #
    # The card can be above the floor too: the judgement asked for is often one the answer in hand
    # already made, and then the module that made it hands its own sentence back - "is that fair"
    # after the answer about a dog alone all day got chat's "Sounds good." while the card beside it
    # said "What is not fair is a puppy, or ten hours with no break at all." That is the same shrug
    # in shorter words against the same answer, so the rule reads every candidate that is not the
    # front one; the safety band is left alone, because it answered already (`_choose` returns it
    # first) and a card must not pull a crisis line out from under the person.
    front = candidates[best].get("reply")
    if (_hands_the_decision_back(front)
            or (candidates[best].get("module") == "chat"
                and _content(front) in _ack_lines())) \
            and (_asks_a_question(memory) or _asks_for_a_judgement(text, memory)):
        already_read = _said_before(memory, text)
        for index in range(len(candidates)):
            if index == best or _priority(candidates[index]) >= SAFETY:
                continue
            reply = candidates[index].get("reply")
            # ...and a card that hands back an answer the person has already read is not an answer
            # to a hand-back either: "im thinking of getting a cat" then "will that work" was
            # given the whole cat card again - the card was pulled in here, past the never-repeat
            # rule, because the front line handed the decision back and the card names the cat.
            # The person had read every word of it a turn ago, so the repeat is no better than the
            # hand-back and it reads as the bot not listening. A card they have not read is
            # untouched, which is what this rule is for.
            if (_content(reply) in already_read
                    or (last and _echoes(reply, last))):
                continue
            if _names_what_they_said(reply, text, memory):
                return index
    # A report of a thing is answered by what to do about it, not by the fact that explains it:
    # see A_MY_OWN_REPORT above.
    advice = _the_advice_over_a_definition(candidates, pool, text, best)
    if advice is not None:
        return advice
    return _the_card_that_places_the_figure(candidates, best, text, memory)


def _as_it_comes(text, memory, candidates, last=""):
    """The index of a candidate its module asks to be answered as it comes, else None.

    Some answers are right whatever else proposed, but only on some of the lines their module
    proposes on. A band cannot say that: it says "everything this module proposes" and the
    module's other lines then take turns they should not. The memory store is the case that
    found it: "my partner is vegetarian" then "places to eat near the old town" must be answered
    from what the person said, and the same module's diet fact must not answer "where can i take
    my dog" just because it was that high up the scale. So the module says which of its own
    proposals this is, on the line in front of it, and the arbiter takes its word.

    Read after the safety band, and before the never-repeat rule, the `ANSWERS_INSTEAD`
    declaration and the specialist fit, because "answer this as it comes" is the whole of the
    claim. A flagged reply that only repeats the bot's last turn is passed over - a module that
    says "this line is mine" still has to say something new - and so is a hook that raises, so a
    module cannot lose the turn by declaring badly.

    A hook from below the floor does not take the turn off a module above it, though. A claim is
    settled by PRIORITY everywhere else in this file (`_claims_instead`), and a module under the
    floor has no higher claim on the line than anything that actually answered it: "im worn out
    and flat this week" / "and" is answered from the store with the one thing that helps ("That
    kind of tired needs an early night, not more coffee"), and a fallback-band hook that took the
    turn said "that's as far as I can take it" over an answer nobody had been given yet. The same
    held for every other band and it was not enforced: "i keep putting off my emails" /
    "done that" gave the greeting's "How is it going with it so far?" over the next part of the
    entry. Hooks above the floor are untouched: those exist to beat the store on the lines it
    proposes on, which is the whole of the reason `answers` has one.
    """
    for index, candidate in enumerate(candidates):
        name = candidate.get("module")
        if not _declares_as_it_comes(name, text, memory):
            continue
        # ...unless the answers beside it hand back the very thing the line ruled out: "not curry,
        # something else" got the kitchen's "Quick: chickpea curry in 25, or a sweet potato curry",
        # which is the thing refused, twice, while the rule-out's own line ("That one never
        # mentions curry at all, so nothing changes. Quick: tuna pasta...") was the only answer to
        # the line in the list. A reply that offers back what the person has just ruled out has
        # not read the line, so it is not an answer the claim gives way to - not to PRIORITY, and
        # not to a declaring specialist either, which is the same card under another name.
        thing = _the_thing_the_line_ruled_out(text, memory)
        vetoed = bool(thing) and _every_real_answer_offers(thing, candidates, index)
        if _priority(candidate) < 0 and _a_real_answer_besides(candidates, last) and not vetoed:
            # A hand-back above the floor is the one case where a take from under it still has
            # the better reply - but only when the take is about what the person said
            # (`_names_what_they_said`), not when it is a pool line about something else.
            hand_back = (_only_a_hand_back_besides(candidates, last)
                         and _names_what_they_said(candidate.get("reply"), text, memory))
            # ...and the composer's answer to a report on the advice it just gave is the
            # other one: that reading is the composer's subject and not a pool line's, so a
            # module that read the line as a feeling or a mood is not an answer beside it -
            # the same reason `_a_declaring_specialist_besides` decides the rest of the
            # layer. A specialist that declares the line's topic still takes the turn.
            # ...and the status question is the one report reply that gives way: "ive tried
            # that" after the running answer is answered "Has it made any difference yet?" only
            # while there is no card beside it, because the answer's own next step is worth more
            # to a person who has just done the last one. Where nothing is beside it - the oven
            # report, the nails - the question is the whole of the answer and takes the turn.
            report = (_the_reply_is_the_report(candidate, text, memory)
                      and (fallback.a_report_that_says_something(text, memory)
                           or not _a_card_besides(candidates, index))
                      and not _a_declaring_specialist_besides(candidates, index, memory, text))
            if not (hand_back or report):
                continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        # A take says "this line is worth answering now"; a declaration says "this line is my
        # subject". A module that declares the topic the line was read as outranks a take, and
        # the bands cannot express that: "i shouted at my kids and i feel awful" had the family
        # card in the list at 0 and chat taking the turn as it comes, and raising the card's
        # band to 400 changed nothing because this layer runs above the bands.
        # The recall band is the exception, and it is a real one: "what should i cook for my
        # son" is answered from what the person said about their son's diet, not from a cooking
        # card, so a store taking that line still beats the specialist. Only a generalist's take
        # gives way. (tests.test_arbiter, the declared turn beats a higher priority specialist.)
        # ...but a card that has not read the line does not outrank it either: the conjunct
        # above is about a specialist that read the line and has the answer, and one that hands
        # back the step the person has just reported doing has read nothing. See
        # `_a_declaring_specialist_besides`, which takes the store's reading of the report.
        if (not vetoed and _priority(candidate) < CHATTER
                and _a_declaring_specialist_besides(candidates, index, memory, text)):
            continue
        # A claim says "this line is my subject", and a stock line says nothing of the subject
        # it claims: the pool for a lonely week answered "my bins were left out and not emptied"
        # ("Loneliness is rough. A weekly club or class is the quickest way to see the same faces
        # again") over the council card that answers the missed collection by name. "Left out"
        # was read as the feeling, and the take that answers that reading shares no word with the
        # line at all - the bins, the emptying, the council are all in the card beside it. A reply
        # that says nothing of the line cannot be about it, so the claim stands down where a card
        # beside it names the line's own words. Only a take from the chatter band is read this
        # way: a specialist that claims a line has read it, and the bands already settle those.
        if _priority(candidate) < CHATTER and _a_card_names_the_line(candidates, index, text,
                                                                    memory):
            continue
        # A claim on a line whose answer is the last answer under a lead ("It's what I said a
        # moment ago: <the paragraph>") is not a second answer: the same rule `_choose` applies
        # to the candidates below applies here, or a module that takes a follow-up as it comes
        # reads the paragraph back to the person while a specialist beside it has the answer to
        # the question actually asked. "my baby is not sleeping" / "what should i look out for"
        # got chat handing back the line it had just given, with the baby's own guidance in the
        # list behind it at 0. Fallbacks are not counted: a stock line is not a reason to drop an
        # answer they have not read.
        if (last and (_echoes(reply, last, announced=True)
                      or _the_answer_again_with_a_tail(reply, last))
                and _a_fresh_answer_besides(candidates, index, last)
                # ...unless the line is asking to hear that answer again: then the hand-back is
                # the answer and the fresh line beside it is about something else. "run that by
                # me again" over a boiler answer was taken by the knowledge entry that read the
                # word "run" as a subject, and the person got a heart-rate target.
                and not _a_repeat_to_hold(memory, text)):
            continue
        # A claim that only says the person's own line back is not an answer to the rest of it:
        # "my sister is veggie and shes coming to dinner, what can i cook" was answered "Your
        # sister is veggie." The store claims a line for the fact in it, at the recall band, while
        # the cooking answer sits beside it at 0. The fact was never in doubt and the ask after it
        # was, so a reply made of nothing but the line's own words gives the claim up - but only
        # where a card beside it does answer the ask, never on a line where it is the whole of
        # what the bot has to say.
        if (_the_ask_after_the_facts(text) and _only_says_the_line_back(reply, text)
                and _a_card_besides(candidates, index)):
            continue
        return index
    return None


def _leaving_reply(candidates, own, carried, words, clean, text, memory, last=""):
    """The index of the sign-off for a line that says the person is going, or None.

    A goodbye is the one line no topic entry owns, and every topic entry can win it on a word of
    the reason behind it: "ill let you go, dinner is burning" matched cooking, "better go and
    get the washing in" got the search shrug, "got to go, the kids are up" got a nod. The
    reading and the wording are the composer's (bot/compose/leaving.py); the arbiter only keeps
    the turn where it belongs. A leave inside a safety thread is still that thread, so the
    careful continuation keeps it.
    """
    # The line as typed: the composer's reading needs the punctuation that separates the leave
    # from the reason ("ill let you go, dinner is burning"), and `clean` has already lost it.
    typed = " ".join(str(text or "").lower().split())
    try:
        if not leaving.reads_as_leaving(typed):
            return None
        said = {_content(line) for line in leaving.lines()}
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    try:
        if _composer_reading(text, memory)[0] == THREAD:
            return None
    except Exception:  # noqa: BLE001 - no thread reading, no thread to keep
        return None
    # The small-talk module first: a goodbye is its line, and it has its own wording for one.
    # Chat wins this on its own reply rather than on the composer's, so a chat that read the line
    # keeps it and this rule only fills in where nothing did.
    small_talk = _labels(("small-talk",))
    try:
        # Only the leave with a reason in front of it can be answered by the reason: a bare leave
        # ("im off to work now") is a plan as much as a goodbye, and small talk's next-thing line
        # is the better reply to it.
        reasoned = leaving.pool(typed) is leaving.REASON_POOL
    except Exception:  # noqa: BLE001 - no reading of the reason, no reason to be stricter
        reasoned = False
    for index, candidate in enumerate(candidates):
        # ... but only a sign-off. A sign-off asks nothing, and small talk also answers the
        # reason behind the leave with a question ("thanks, i need to go, the kids are up" got
        # "Go, the kids are up - fair enough. What's stopped it happening so far?"); it also
        # answers the reason without one ("talk later, the baby is crying" got "That's a lot for
        # them to carry."). Neither is a goodbye, so where the leave has a reason the composer's
        # vocabulary decides whether the reply in front of it is one.
        if _declared(candidate.get("module")) & small_talk and not _asks(candidate.get("reply")) \
                and (not reasoned or _a_sign_off(candidate.get("reply"))):
            return index
    spare = None
    for index, candidate in enumerate(candidates):
        said_back = _content(candidate.get("reply"))
        if said_back in said:
            if not last or said_back != last:
                return index
            spare = index if spare is None else spare
    if spare is not None:
        return spare
    # No sign-off among the candidates: the first reply that is not about a topic still beats
    # one that matched a word of the reason clause.
    for index, candidate in enumerate(candidates):
        if _priority(candidate) < 0:
            continue
        if _match(candidate.get("module"), own, carried, words, clean) <= 0:
            return index
    return None


# The subject the line names: the thing after "my", "the", "your" - the bins in "my bins were
# left out and not emptied", the washing in "my washing was left out in the rain". A line about a
# feeling names no such thing ("i feel lonely at work"), which is the difference between a stock
# take answering a reading of the line and a card answering the thing in it.
def _the_subject_words(text):
    """The words the line says its subject with - what follows a determiner, else an empty set."""
    words = set()
    for phrase in A_SUBJECT_PHRASE.findall(str(text or "").lower()):
        words.update(word for word in A_SUBJECT_WORD.findall(phrase)
                     if word not in NOT_A_SUBJECT_WORD)
    return words


def _the_lines_own_words(text, memory):
    """The words of the line that say what it is about, else an empty set."""
    understood = memory.get("understood") if isinstance(memory, dict) else None
    words = _the_subject_words(text)
    if isinstance(understood, dict) and understood:
        subject = understood.get("subject")
        if isinstance(subject, str) and subject:
            words.update(A_SUBJECT_WORD.findall(subject.lower()))
        words.update(word for word in _the_subject_words(subject or "")
                     if word not in NOT_A_SUBJECT_WORD)
    return {word for word in words if word not in NOT_A_SUBJECT_WORD}


def _the_forms_of(word):
    """The word and the endings English puts on it - "bins", "bin", "emptied", "emptying"."""
    forms = {word}
    if word.endswith("s") and len(word) > 3:
        forms.add(word[:-1])
        if word.endswith("es") and len(word) > 4:
            forms.add(word[:-2])
    if word.endswith("ed") and len(word) > 4:
        forms.update((word[:-2], word[:-1]))
    if word.endswith("ing") and len(word) > 5:
        forms.update((word[:-3], word[:-3] + "e"))
    return {form for form in forms if len(form) >= 3}


def _the_same_word(said, word):
    """True when `said` is a form of `word` - "bin" for "bins", "empty" for "emptied"."""
    return said in _the_forms_of(word)


def _names_a_word_of(a_reply, words):
    """True when the reply says one of `words` as a word of its own, not merely a sound of it."""
    said = A_SUBJECT_WORD.findall(_content(a_reply))
    return any(_the_same_word(one, word) for one in said for word in words)


def _a_card_names_the_line(candidates, index, text, memory):
    """True when another real candidate names the line's own words and this one names none.

    A stock line can never name the thing the person said - it does not know it - so a take that
    shares no word with the line is the one case where a card beside it answers more of the line
    than the take does. Every line whose words the take does say is left alone, as is every line
    with no card beside it: this passes over a candidate, it never chooses one, and no PRIORITY is
    read or changed anywhere.
    """
    words = _the_lines_own_words(text, memory)
    if not words:
        return False
    if _names_a_word_of(candidates[index].get("reply"), words):
        return False
    for other, other_candidate in enumerate(candidates):
        if other == index or _priority(other_candidate) < 0:
            continue
        if _names_a_word_of(other_candidate.get("reply"), words):
            return True
    return False


def _a_detail_added_to_the_news(candidates, pool, text, memory):
    """The index of the composer's line for a detail added to news the bot has just cheered.

    Read only on the turn after a cheer this bot gave (`goodnews.the_reply_just_cheered`), and only
    for a short line with nothing asked in it: which go it was ("first time", "third go") or the
    score ("2-0"). Nothing in those names a subject, so every card in the list that matched the
    conversation's topic is answering a question nobody asked - the driving-test one, the "That's
    2" arithmetic - and the pool that takes the detail as news is the answer. It never picks a
    fallback and reads no PRIORITY: only a line of `goodnews`'s own pool takes the turn.
    """
    if not reads_as_a_detail_of_the_news(text, memory):
        return None
    for index in pool:
        if _priority(candidates[index]) < 0:
            continue
        if reads_as_the_detail_line(candidates[index].get("reply")):
            return index
    return None


def _shares_a_stem(one, other):
    """True when two words are the same word with an ending on - "shrink", "shrinking",
    "shrinkage". Five letters is the shortest run that does not join "there" to "these"."""
    return len(one) >= 5 and len(other) >= 5 and one[:5] == other[:5]


NOT_A_NEW_WORD = frozenset("""
thanks thank sorry please pardon cheers again alright okay ok right really maybe perhaps actually
still even ever always whole little another other thing things lot stuff first next then step steps
""".split())


def _the_word_the_line_added(text, last):
    """The longest word the line has that the answer above does not, else "".

    "also how do i stop it shrinking next time" adds "shrinking" to an answer about blotting a
    coffee stain. The longest one is the one that names the new subject: the short words of a
    follow-up ("next", "time", "stop") are also words of a hundred other replies, so a reply that
    says one of them is not a reply about what was added.
    """
    said = WORD.findall(str(last or "").lower())
    words = [word for word in A_SUBJECT_WORD.findall(str(text or "").lower())
             if len(word) >= 5 and word not in NOT_A_SUBJECT_WORD
             and word not in NOT_A_NEW_WORD]
    fresh = [word for word in words
             if not any(_shares_a_stem(word, one) for one in said)]
    return max(fresh, key=len) if fresh else ""


def _says_nothing_new(reply, last):
    """True when every word of substance in the reply is already in the answer above.

    "The thing to do first: Blot up as much as you can with kitchen paper" is the answer above with
    a lead-in ("first" is not a word of substance), so the person has read it a turn ago and it
    cannot be the answer to what they have just added. A fresh line says something of its own, and
    one word of its own is enough: on "my son is 2" / "he isnt talking yet" / "should i worry" the
    take "Yes - it is worth acting on rather than sitting on. Asking costs very little" is not a
    repeat of the speech answer, so it keeps the turn.
    """
    said = set(WORD.findall(_content(last)))
    glue = NOT_A_SUBJECT_WORD | NOT_A_NEW_WORD
    loose = [word for word in WORD.findall(_content(reply))
             if len(word) >= 4 and word not in glue]
    fresh = [word for word in loose
             if word not in said and not any(_shares_a_stem(word, one) for one in said)]
    return len(fresh) <= 1


def _names_the_word(a_reply, word):
    """True when the reply says the word, endings and all - "Shrinkage" for "shrinking"."""
    return any(_shares_a_stem(said, word) for said in WORD.findall(_content(a_reply)))


def _the_answer_that_names_what_the_line_added(candidates, pool, text, last):
    """The index of the reply that answers what the line has just added, where the one in front
    does not name it at all.

    A reply that repeats the answer above is not a reply to the part of the line that answer never
    covered, however high its band: this passes over a take that leaves the added word out of its
    own words, for a real candidate beside it that says it. Only what the line adds is read, and
    only against the answer immediately above, so an answer that already covered the word keeps
    its turn and a line with nothing new in it is untouched. The store's recall is left alone - a
    hand-back that misses the added word is the memory lane's, not this rule's - and no PRIORITY is
    read or changed.
    """
    if len(pool) < 2 or not last:
        return None
    added = _the_word_the_line_added(text, last)
    if not added:
        return None
    if not _says_nothing_new(candidates[pool[0]].get("reply"), last):
        return None
    if _names_the_word(candidates[pool[0]].get("reply"), added):
        return None
    if _priority(candidates[pool[0]]) >= RECALL:
        return None
    for index in pool[1:]:
        if _priority(candidates[index]) < 0:
            continue
        if _names_the_word(candidates[index].get("reply"), added):
            return index
    return None


def _a_card_that_names_the_line(candidates, pool, text, memory):
    """The index of a card that names the line where the chosen take names nothing of it.

    Read off the reading's own keywords, so a reply that shares one of them is about the line by
    the same reading that says what the line is about. Only a take below the chatter band is
    passed over, and only for a real candidate beside it: this never picks a fallback, and no
    PRIORITY is read or changed.
    """
    if len(pool) < 2 or _priority(candidates[pool[0]]) >= CHATTER:
        return None
    # A line that asks for something said earlier is answered from the chat, as the store and the
    # said-back lines are: a card that names a word of it ("and what make is the boiler" against
    # the flow-temperature card) is answering a question about the world that nobody asked.
    if (candidates[pool[0]].get("module") in MEMORY_MODULES
            and _a_recall_from_an_earlier_turn(text, memory)):
        return None
    words = _the_lines_own_words(text, memory)
    if not words or _names_a_word_of(candidates[pool[0]].get("reply"), words):
        return None
    for index in pool[1:]:
        if _priority(candidates[index]) < 0:
            continue
        if _names_a_word_of(candidates[index].get("reply"), words):
            return index
    return None


# A line that asks for the answer again in words that can be followed ("can you explain that
# again", "in plain english?", "i dont understand") is not a line that asks to hear the same words
# again, and those are two different turns. The memory lane reads a bare "explain that again" as
# the ask to have the answer handed back, and hands it back under a lead ("Sure — {said}"), at
# MEMORY 7000 the store's band: on `my boiler is making a noise` the whole boiler answer came back
# word for word twice, while the candidate beside it that did the explaining ("A burner heats
# water and a pump sends it round the radiators; the water comes back cooler and is heated
# again") sat at 0 and was never given. "What does that mean" already reached that card; the three
# wordings that say it plainer did not.
#
# The rule reads the all-repeat case the never-repeat rules already read in one place: where the
# turn has an announced repeat in front and a candidate that says something the person has not
# read, about the same subject, the candidate that says something new wins. It never deletes the
# repeat: when every other candidate is the same answer again, a stock line, a hedge or a points
# back ("You typed: ..."), the repeat stands, because a person who asks again must be given an
# answer. No PRIORITY is read from or written to: the band the store's repeat sits in is where it
# stays; this chooses among the candidates the turn already has.
A_PLAINER_ASK = re.compile(
    r"\b(?:explain(?:\s+(?:that|it|this))?|in plain (?:english|words)|plainer|plainly|"
    r"simpler|more simply|put (?:it|that) (?:another way|in other words)|in other words|"
    r"what (?:do you|does that) mean|i (?:don'?t|do not|didn'?t) (?:understand|get it|follow))",
    re.I)


# The words an ask to have the answer put plainer can be made of and still be nothing but the ask.
# They are function words and the verbs of the ask itself, never a thing: "can you explain that
# again" and "in plain english please" are all of them, "explain how a combi boiler works" leaves
# "combi", "boiler" and "works" standing, and that line wants the thing explained, not the last
# answer worded differently.
PLAIN_ASK_FILLER = frozenset("""
a again and another ask can could did do does doing dont don't english explain explained explaining
follow following for get got how i in it just mean means meant me more not now of or plain plainer
plainly please put right say saying simpler simply so sorry that the then there this to understand
understandit want was way what word words would you your
""".split())


def _a_line_asking_for_plainer_words(text):
    """True when the line is only the ask to have the last answer put a plainer way.

    The whole line has to be the ask: the words around the ask phrase are read, and one word of
    the person's own - a thing, a skill, a part - means the line wants that thing, so it is left
    alone. "explain the bit about the pressure" is a question about the pressure.
    """
    clean = _content(text)
    if not clean or not A_PLAINER_ASK.search(clean):
        return False
    rest = A_PLAINER_ASK.sub(" ", clean)
    return not [word for word in A_SUBJECT_WORD.findall(rest.lower())
                if word not in PLAIN_ASK_FILLER]


def _says_the_answer_again(reply, last):
    """True when the reply is the previous answer, with a lead in front of it or without one."""
    if not reply or not last:
        return False
    said = _content(reply)
    if said and said == _content(last):
        return True
    if _the_quoted_repeat(reply) is not None:
        return True
    return bool(_echoes(reply, last, announced=True))


def _a_plainer_reading_of_the_same_answer(candidates, best, text, memory):
    """The candidate that explains the last answer, where the turn in hand is the answer again."""
    if not _a_line_asking_for_plainer_words(text):
        return None
    last = _last_reply(memory)
    if not last or not _says_the_answer_again(candidates[best].get("reply"), last):
        return None
    about = _the_subject_words(last)
    if not about:
        return None
    order = sorted(range(len(candidates)), key=lambda index: -_priority(candidates[index]))
    for index in order:
        if index == best or _priority(candidates[index]) < 0:
            continue
        reply = candidates[index].get("reply")
        if not reply or _says_the_answer_again(reply, last):
            continue
        if fallback.is_a_hedge(reply) or _points_back(reply):
            continue
        if _names_a_word_of(reply, about):
            return index
    return None
