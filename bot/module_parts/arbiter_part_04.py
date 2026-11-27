"""Part 4 of 6 of a large module, split out of `arbiter`.

Everything here is re-exported from `arbiter`, so callers import it from there as before.
"""
import importlib

from ..compose import aboutness, fallback
from ..compose import outlook as _outlook
from .arbiter_part_01 import (
    SAFETY, _SAID_BEFORE_WORDS, _priority, _the_numbers_in, DOUBT_WORDS, WORD, RECALL,
    _asks_for_the_answer_again, CHOICE, MEMORY_MODULES, _already, MOVE_SHARE, _repeat,
    DECLARED_TOPICS, WHOLE_LINE_BAND, DECLARED_INSTEAD, LABEL_KEYS, READ,
)
from .arbiter_part_02 import (
    _content, _carries_the_answer, _names_the_thing, _asks_about_the_chat, _a_repeat_to_hold,
    NOT_A_SUBJECT, _a_question_about_the_bot, CUT_MARKS, TOKEN, WHOLE_MOVE_WORDS,
    _announces_a_repeat, _carries_on, _run_in_the_answer, _my_workings, ANSWERS_THE_NEWS,
    A_VERDICT_BACK, KEEPS_ITS_OWN_ANSWER, _about_the_news, _says_the_same_thing_again,
    _the_subject_was_answered, _in_a_careful_thread, _reads_as_a_verdict, _about_the_line,
    _the_ask_clause, _defers_to, CHITCHAT,
)
from .arbiter_part_03 import (
    _echoes, _points_back, _made_of_the_answer, _the_verdict_turn, _verdict_lines,
)


def _an_answer_it_already_gave(index, candidates, text, memory):
    """The chosen candidate, unless it is a whole answer this chat has already been given.

    The never-repeat rule lives inside `_choose`, on the path where every real module claims the
    line. A follow-up that takes one of the arbiter's other paths - the shape a line asks for, a
    verdict on the news, a claim, the knowledge base reading the line as the same question - came
    back with a paragraph the person had read three to nine turns earlier, and it was the same
    reply word for word:

        my mum fell over / ... / what do i say to her  -> the falls paragraph, five turns back
        my phone screen is cracked / ... / what should it cost to fix  -> the case paragraph
        ok back to edinburgh, whats the food like    -> the Edinburgh card, six turns back

    So the reading is asked once, after every rule has had its say (the same place and the same
    promise as `_a_past_that_is_not_there`): a reply whose words are the words of an answer this
    chat has already had, to a different question, is passed over when another real candidate is
    not one. It is passed over, never dropped - where every candidate on the table repeats, the
    repeat stands, because the answer twice is still better than a shrug (STYLE.md), and the same
    question asked again keeps its answer (`bot/memory/again.py` frames it, and `_said_before`
    leaves that turn out of the set). The safety band is never moved: an emergency answer is the
    turn whatever else is on the table.

    What takes the turn instead has to say something of its own. A nod, a receipt ("Got it - she's
    ok, just bruised"), a hedge, a pointer back ("what I said above") or another answer the chat
    has already had is not one, and neither is a line shorter than the length a whole answer
    starts at: those are the lines that would fit any message (STYLE.md), and the paragraph again
    is better than one of them. Where a band the arbiter normally stands aside for - the greeting
    band, which is where a good many of these second sentences live - offers a line that says
    something of its own, it takes the turn: "Two or three lines is plenty: what happened, what
    you want, and by when" is a better answer to "what do i say to her" than the falls paragraph
    the person read five turns ago.
    """
    if not candidates:
        return index
    try:
        if _priority(candidates[index]) >= SAFETY:
            return index
        heard = _said_before(memory, text)
        if not heard or _content(candidates[index].get("reply")) not in heard:
            return index
        last = _last_reply(memory)
        for other, candidate in enumerate(candidates):
            if other == index:
                continue
            if _priority(candidate) >= SAFETY:
                continue
            reply = candidate.get("reply")
            if _content(reply) in heard or _echoes(reply, last):
                continue
            if fallback.is_a_hedge(reply) or _points_back(reply):
                continue
            if len(_content(reply).split()) < _SAID_BEFORE_WORDS:
                # A stock line, a receipt or a nod is not a new answer: it would fit any message,
                # and the paragraph again is better than that (STYLE.md). The length is the same
                # reading the never-repeat rule uses for a whole answer - "Got it — she's ok, just
                # bruised" is the person's own words handed back, while the line beside it ("Two or
                # three lines is plenty: what happened, what you want...") says something of its
                # own. `_answers_this_line` is narrower still: it asks for an opening that is a job.
                continue
            return other
    except Exception:  # noqa: BLE001 - the arbiter must never lose a turn
        return index
    return index


def _names_the_answers_figure(reply, memory):
    """True when a reply takes up a number the answer above named.

    "i walk 10 minutes a day" got an answer that named twenty minutes, and "will that work" was
    answered "10 minutes is short of the 20 minutes that answer named." That is the yes or the no
    the person asked for - it is the comparison against the method - but the reader that looks for
    a yes or a no word cannot see one in it, so the turn went to a reply that only sounds like one.
    A reply that puts the answer's own figure back to the person is answering the check.
    """
    mine = _the_numbers_in(reply)
    return bool(mine) and bool(mine & _the_numbers_in(_last_reply(memory)))


def _names_the_subject(candidate, memory, words):
    """Whether an entry may take a bare yes-or-no doubt that names no subject of its own.

    "is that bad" after "blood in my pee", "is that normal" after "my cat sleeps a lot": the
    question carries nothing but the doubt, so the subject is the line before it, and an entry
    that fits by inheriting the conversation's topic can be about something else entirely. The
    sleep entry answered a cat with "Most adults do best on seven to nine hours", the
    carbohydrate entry answered "can i freeze rice" with "Carbohydrate is not fattening in
    itself", and the repeat line answered a humming fridge with "Everything about normal is in
    what I said above". The composer's line for the doubt itself ("Yes, that is the usual thing
    - what to keep an eye on is change rather than the thing itself") was in front of every one
    of those and lost.

    So on a bare doubt the entry has to name the subject too: a word of the line the conversation
    is on, in the reply. A card that shares it (the kettling entry answering "my boiler is making
    a kettling noise", the chicken entry answering "can i freeze the leftovers") keeps its turn.
    A card that shares nothing is answering a different question and stands down.

    Only a bare doubt is held to this: a line with words of its own ("is that bad for the
    freezer", "is that normal for a 14 year old cat") names its subject itself and is read by
    the ordinary specialist rule.
    """
    if not _a_bare_yes_no(memory):
        return True
    if _carries_the_answer(candidate.get("reply"), memory):
        # The entry comes back to the answer the bot gave a turn ago, so the subject is its own
        # by construction, whatever words the two happen to share. "my calf hurts" / "is that
        # bad" is answered by the calf entry again, and its wording ("For a joint or muscle that
        # aches ... ibuprofen gel") names neither "calf" nor "hurts": a test on the topic's
        # words alone stood it down for the composer's "Nothing in that answer needs anyone yet",
        # which says less than the entry it displaced. Found in review by @smooth-lark.
        return True
    subject = _carried_words(memory) - set(words) - DOUBT_WORDS
    if not subject:
        return True
    reply = candidate.get("reply") or ""
    for word in subject:
        if len(word) < 4:
            continue
        if _names_the_thing(word, reply, _carried_words(memory) | set(words)):
            return True
    return False


def _a_bare_yes_no(memory):
    """True when the line asks yes or no and names no topic of its own ("is that normal")."""
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        return False
    if _line_topics(memory):
        return False
    return "yesno" in _labels(understood.get("asks"))


def _carried_words(memory):
    """The words of the line the conversation is on, which a bare follow-up inherits."""
    topic = memory.get("topic")
    if isinstance(topic, dict):
        labels = _labels(topic.get("words"))
        if labels:
            return labels
        text = topic.get("text")
        if isinstance(text, str) and text.strip():
            return set(WORD.findall(text.lower().strip()))
    return set()


def _fit(own, carried, memory, best_priority, reply="", claimant="", text=""):
    """The topics the specialist rule may count, and the ones it may only count weakly.

    The reading gives a turn two topic sets: the line's own (`understood["topics"]`) and the one
    the conversation is on (`understood["topic"]`, which on a follow-up is put back in). Both
    count 2 in `_match`, because on a follow-up the second is the only topic there is.

    A line that names no topic of its own is not about the topic of the conversation, though: it
    is about the conversation. "what am i doing this week" after "im writing up my thesis" was
    read as a language-and-writing line by inheritance alone, and the essay-thesis entry took
    the turn from the memory store's own answer ("You're writing up your thesis."), which is the
    answer to what was asked. So when the candidate in front sits in the recall band (README,
    "Routing": the memory store reads a line about what was said), only a specialist the line
    itself supports - its own topics, a phrase or a word it contains - may take the turn from
    it. The recall band is the only band this applies to: the safety band is answered before
    this function is reached, and the loss and grief bands already answer in place of the
    entries (`_instead`).

    The same holds for a line that asks for the answer again. Its measure word is read as a topic
    of its own - "how long did you say" is a maths-and-numbers line - but it is not a subject the
    line is about, so the conversation's topic is not counted for it either: the entry that wrote
    the answer reads the pointer as the same question and hands the whole answer back, while the
    memory store has the part the person asked for. See `_asks_for_the_answer_again`.

    And it holds for a line that asks about the conversation in some other way: a recap of the chat
    is not the topic its words name, so the module in front publishes that reading
    (the store's `_about_this_chat`) and nothing is counted against the recall band on it. See
    `_asks_about_the_chat`.
    """
    if best_priority >= RECALL:
        # Only when the recall band has the part they asked for. When its own line is the last
        # answer said again ("Again - About 20 minutes per 500g ..."), the entry's card is the
        # better of the two and keeps the turn it had.
        repeat = _asks_for_the_answer_again(memory)
        if repeat and not _echoes(reply, _last_reply(memory)):
            return set(), set()
        # A line that asks about the conversation is the recall band's, whatever topic its words
        # point at. "my boiler keeps losing pressure" then "what have i been saying about the
        # boiler" is read as a home line from the word "boiler", and the specialist rule let the
        # boiler entry answer it with its how-to instead of the store's line about what the
        # person said. "im saving for a car" then "what am i saving for" did the same with money.
        # The store's own gate reads these shapes (`_about_this_chat`), so the arbiter keeps
        # no word list: a recap is not the topic it names, and the conversation's topic does not
        # stand in for it either. A repeat ask is decided by the rule above: it is a reading of
        # the answer in hand, and on "when did you say" the card that gave the timing keeps the
        # turn rather than the store saying its own last line again.
        if not repeat and claimant and _asks_about_the_chat(claimant, text, memory):
            return set(), set()
        if not _line_topics(memory):
            return set(), carried
    return own, carried


def _line_topics(memory):
    """The topic labels the understanding engine read from this line by itself, never inherited."""
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        return set()
    return _labels(understood.get("topics"))


def _a_choice_the_answer_did_not_make(candidates, text, memory, last=""):
    """The fallback to take the turn when a choice was answered with the rest of the last reply.

    Asked only when every real candidate says the last answer again (see `_choose`). A stock line
    is no reason to drop an answer, but the rest of an answer is not an answer to a choice: "is it
    worth fixing or shall i just get a new one" after the bang on the spin got the sentence about
    the transport bolts (a slice of the answer the person had already read past), while the
    composer's own repair-or-replace pool had the line they needed. So on a line whose reading
    asks to choose between options (`understood["asks"]` holds `choice`), a fallback with words
    of its own takes the turn from a repeat.

    Only a choice ask, and only words the last reply does not already hold: the same question
    asked twice is answered by the same answer, and there the repeat is the reply.

    A shrug is not the choice made, so the two shapes of it are passed over: the hedge that says
    the bot cannot call it, and the line that only points back at the answer above. "my fridge is
    on its last legs" then "should i get it repaired or a new one" had the repair-or-replace card
    ("Repair it while a fix is well under half the price of a new one") in the candidates and was
    handed the composer's "Can't call that one for you, sorry. Say what you'd lose either way and
    I'll lay it out with you" instead, because it was the only reply in the fallback band whose
    words the answer above did not already hold. The card answers the choice; the shrug asks for
    the information again. `_choose`'s own filter drops hedges for the same reason.
    """
    understood = memory.get("understood")
    if not last or not isinstance(understood, dict):
        return None
    if CHOICE not in _labels(understood.get("asks")):
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) >= 0:
            continue
        reply = _content(candidate.get("reply"))
        if not reply or reply == last or _echoes(reply, last):
            continue
        if fallback.is_a_hedge(candidate.get("reply")) or _points_back(candidate.get("reply")):
            continue
        return index
    return None


def _the_answer_handed_back(candidates, text, memory, last):
    """The index of the store's hand-back when the line asks to hear that answer again, else None.

    An ask to hear it again is answered by the answer, so no card that read a word of the ask as a
    subject of its own may take the line first: "run that by me again" over a boiler answer was
    taken by the knowledge entry that read the word "run" as exercise, and the person got a
    heart-rate target for a run. The hand-back was in the list in every one of those turns and
    lost the turn, because the card declared the subject as it comes and the store declared
    nothing.

    Only the store's own candidate, only when its reply is the answer already on the screen, and
    never when the ask names a figure: there the number is lifted out of the answer and the card
    that holds that number keeps the turn (`tests.test_a_repeat_ask_keeps_the_recall`).
    """
    if not last or not _a_repeat_to_hold(memory, text):
        return None
    # The store's band, not the store's module: the composer hands the answer back in its own
    # words ("I said: Lower eggs into already boiling water."), and the ask is the same ask.
    band = [index for index, candidate in enumerate(candidates)
            if candidate.get("module") in MEMORY_MODULES and _priority(candidate) >= 0]
    for index in band:
        reply = _content(candidates[index].get("reply"))
        if reply and _echoes(reply, last):
            return index
    # A slice of the answer in front of the ask is the hand-back too, and the store says the whole
    # of it in the frame its own line opens on ("Same as before: ..."), so the whole answer is
    # looked for first: what the person asks to hear again is the answer, not the shorter form of
    # it another band chose to hand back.
    seen = set(_content(last).split())
    for index in band:
        reply = _content(candidates[index].get("reply"))
        if reply and _made_of_the_answer(reply, seen):
            return index
    return None


def _a_declaring_specialist_besides(candidates, index, memory, text=""):
    """True when another candidate's module declares a topic this line was read as.

    A card that repeats the answer the person already has is not a specialist that read the line.
    After "my boiler is making a noise" / "i already bled the radiators" the radiators entry
    declared heating and read the bleeding instructions out a second time, over the store's own
    line ("Then that part is out of the way: check the pressure is 1 to 1.5 bar"), and the person
    was told to do what they had just said they did. The reading of "still telling them the step
    they just took" is the store's (`already.tells_them_the_step_again`), so this file keeps no
    vocabulary of its own.
    """
    topics = _line_topics(memory) - NOT_A_SUBJECT
    if not topics:
        return False
    # A question about the bot itself is not a subject, whatever topic the reading hung on it.
    # "is what i say saved" was read as money because the person said "saved", and the savings
    # card then outranked the composer's answer to the question actually asked; "do you share what
    # i say" reached the company-shares card ("A share is a piece of a company") the same way, and
    # "can other people read my messages" the phone-trust card. No entry about the world can
    # answer what the bot does with what it is told, so there is no specialist beside this claim.
    if text and _a_question_about_the_bot(text, memory):
        return False
    for other, candidate in enumerate(candidates):
        if other == index:
            continue
        if not (set(_declared(candidate.get("module"))) & topics):
            continue
        reply = _content(candidate.get("reply"))
        if not reply:
            continue
        if _already is not None and _already.tells_them_the_step_again(reply, text, memory):
            continue
        return True
    return False


def _a_fresh_answer_besides(candidates, index, last):
    """True when a real candidate has an answer that is not the last one said again."""
    for other, candidate in enumerate(candidates):
        if other == index or _priority(candidate) < 0:
            continue
        reply = _content(candidate.get("reply"))
        if reply and reply != last and not _echoes(reply, last, announced=True):
            return True
    return False


def _the_whole_move(candidates, real, text, last, written=""):
    """The index of the step that keeps the answer's sentence, where another hands over a piece.

    "where do i start" after a how-to is answered by two modules at once: the composer, which
    hands back the sentence the answer wrote its step in, and the entry that wrote the answer,
    which builds "The first thing to do: <the step>" and stops the step at the answer's first
    comma. Both are made of the answer's own words, so the never-repeat rule sees nothing, and
    the specialist rule then gives the turn to the entry - half of an instruction, over the whole
    of it. And the two are the same move: the short one's words are a run of the long one's.

    So this decides one thing: where one candidate hands over a run of the answer that stops at
    the answer's own comma, and another candidate carries that same run on past the comma, the
    one that carries on takes the turn. Nothing else is read - no module name, no topic - and
    where the answer's words run out the seed rule stands, as it does everywhere else.

    A reply counts as a step only when it is made of the answer's own words (`MOVE_SHARE`, the
    same test `_the_move_in_hand` makes) and is short enough to be one (`WHOLE_MOVE_WORDS`), so a
    paragraph of the answer cannot be lifted over a step by this rule.

    A reply that says the answer over again is not a step at all, however well its opening matches
    (`_echoes`). "Same as before: <the answer>" is the entry's card for a bare follow-up, and the
    longest of those reads as a whole sentence with the writer's own comma in it, so without this
    guard the rule handed the turn to a repeat - the one thing STYLE.md forbids outright - because
    it carried the answer past its comma. Handing a sentence back is only better than handing its
    first clause over when the sentence is new.
    """
    if not last or _repeat is None or len(real) < 2:
        return None
    try:
        if not _repeat.names_nothing(text) or not _repeat.MOVE_ASK.search(str(text or "")):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return None
    # The answer as it was written: `last` is the answer with its punctuation taken out, and the
    # comma a step was cut at is a comma of the answer as the person read it.
    answer = " ".join(str(written or last).split())
    tokens = [(match.group(0), match.end()) for match in TOKEN.finditer(answer.lower())]
    if len(tokens) < 4:
        return None
    seen = {word for word, _ in tokens}

    def _halves(skip_repeats):
        """The candidates that stop at the answer's comma, and those that carry the run on."""
        cut, whole = [], []
        for index in real:
            words = _content(candidates[index].get("reply")).split()
            if not words or len(words) > WHOLE_MOVE_WORDS:
                continue
            if skip_repeats and _echoes(str(candidates[index].get("reply") or ""), last):
                continue
            if sum(1 for word in words if word in seen) / len(words) < MOVE_SHARE:
                continue
            run = _run_in_the_answer(words, tokens, answer)
            if run and answer[run[1]:run[1] + 1] in CUT_MARKS and len(tokens) - run[2] >= 2:
                cut.append((words, run[0]))
            else:
                whole.append(words)
        return cut, whole

    cut, whole = _halves(True)
    if not cut and whole:
        # Nothing here stops at the answer's comma, so there is no half-step to prefer. There is
        # still the other fault this line has: a card about a different subject. "where do i
        # really start" after the rice answer was answered by the row that builds a fence ("Set
        # the posts first: a string line between the two end posts...") - it opens on a job, so
        # the specialist rule let it take a follow-up, and it shares none of the answer's words.
        # On a line that asks for a move out of the answer in hand, the reply made of that answer
        # is the one to give: the other is about something the person was not talking about.
        absent = [index for index in real
                  if not _made_of_the_answer(candidates[index].get("reply"), seen)]
        if absent:
            for index in real:
                if _made_of_the_answer(candidates[index].get("reply"), seen):
                    return index
    if not cut or not whole:
        # Every candidate here says the answer over again, so there is no step to prefer - but
        # there is still a worse one. The entry's card for a bare follow-up announces the repeat
        # ("Same as before: <the answer>"), and the composer hands the same sentence back as the
        # one thing to do ("Just the one, then: <the answer's first sentence>"). Both quote the
        # answer; only one of them reads as a friend carrying on, and it is the one the pool put
        # first. Left to the specialist rule the entry takes the turn and the person is told the
        # answer again. This is the one case where the repeat is all there is, so the pool's own
        # order settles it rather than a guess at the words.
        repeats = [index for index in real
                   if _echoes(str(candidates[index].get("reply") or ""), last)
                   and _made_of_the_answer(candidates[index].get("reply"), seen)]
        quiet = [index for index in repeats
                 if not _announces_a_repeat(candidates[index].get("reply"))]
        # Only one shape comes here: one lane hands the answer over announcing the repeat ("Same
        # as before: <the answer>") and another hands the same sentence over as the one thing to
        # do ("Just the one, then: <the answer's first sentence>"). Both quote the answer and only
        # one of them reads as a friend carrying on, so the quiet one takes the turn - in the
        # pool's own order, so nothing else is read. Where every lane announces the repeat, or
        # where a lane has a reply that is not the answer again, the rules above stand.
        if quiet and len(quiet) < len(repeats):
            return quiet[0]
        return None
    for index in real:
        words = _content(candidates[index].get("reply")).split()
        if not words or words not in whole:
            continue
        if any(_carries_on(words, run) for _, run in cut):
            return index
    return None


def _only_acknowledges(memory):
    """True when the understanding engine reads the line as politeness and nothing else.

    "cheers", "thanks", "ta", "ok", "nice one", "makes sense": the person has finished with
    the last answer, not started a new question, so nothing it says can be about the thing the
    conversation was on. A line that names a topic of its own is not this: "thank you for the
    spinach tip" is read as thanks and about cooking, and keeps its routing unchanged.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    if _labels(understood.get("topics")):
        return False  # "thank you for the spinach tip" is thanks and about cooking: not this
    if understood.get("kind") == "thanks":
        return True
    # An acknowledgement is the understanding engine's reading of a line that answers the bot
    # rather than saying anything of its own ("ok", "nice one", "got it"), and what it is made
    # of is what tells a thank-you from a reply with an ask in it: "you pick" and "got any
    # advice" are read as acks too, and both want the conversation's topic to be answered.
    return (understood.get("intent") == "ack" and not understood.get("asks")
            and understood.get("kind") != "question")


def _a_presence_check(memory):
    """True when the understanding engine reads the line as a check that the bot is here.

    "u up?", "you there?", "still about?": the line asks whether the bot is listening, and it
    names nothing of its own, so it inherits the topic of the conversation and a module that
    answers that topic takes the turn. After "how do i unblock my sink" / "it worked", "u up?"
    got "Same as before: Start with a plunger..." - the drain card read out a second time, where
    the reply is "Still here. What's up?". A line that names a subject of its own is not this
    ("you there in that photo with the dog?" is read as a question about a photo, not a check),
    and neither is a thread the composer keeps (an emergency thread answers a "you there?" with
    its own line - that is read before this). The reading is left alone, as it is for politeness
    alone: only the topic rule is skipped, so the highest PRIORITY takes the turn.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    if _labels(understood.get("topics")):
        return False  # names a subject of its own, so it is about that subject
    if not understood.get("presence"):
        return False
    # A condolence or a crisis is a thread the line belongs to, not a topic it inherited: after
    # "my dog died yesterday" the presence check keeps the loss card that the thread has, and it
    # does not become "Still here. What's up?" in the middle of somebody's grief.
    turns = memory.get("turns")
    if isinstance(turns, list) and turns and isinstance(turns[-1], dict):
        if str(turns[-1].get("module") or "") in ("loss", "safety"):
            return False
    return True


def _about_the_bot(candidates, clean, last=""):
    """The index of the bot's own answer for a line that asks how it works, else None.

    "how do you learn" is a question about the bot, and the study-tips entry answered it with how
    to revise for an exam because the line has "learn" in it; "how do you know things" got the
    same paragraph. A topic entry answers the topic a line is about, and on a line about the bot
    itself the only thing it can match is the verb, so the composer's own answer is the one that
    answers the question asked (STYLE.md).

    Only the kinds the composer publishes claim this (`MY_WORKINGS`), and only from the fallback
    band: the bot's own answers for the rest ("do you have feelings") are already beaten by a
    module that has a better one, and displacing a module that read the line whole is not this
    rule's business. "wrong" is one of them because nothing has a better answer there: a chat that
    was on tomatoes answered "ok random question, do you ever make mistakes" with a tomato sauce
    recipe.
    The reading is the composer's (bot/compose/fallback.py `about_the_bot`), not a word list of
    the arbiter's.
    """
    try:
        kind = fallback.about_the_bot(clean)
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return None
    if kind not in _my_workings():
        return None
    if not candidates or not _declares_topics(candidates[0].get("module")):
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) >= 0 or _declares_topics(candidate.get("module")):
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        return index
    return None


def _the_venue_hours_turn(candidates, clean, last="", text=""):
    """The index of the composer's honest line for a venue's opening hours, else None.

    "what time does the post office on hill road close today" was answered with the
    weekend-plans card: that entry keys on "today" and a bare "what", and on a question about a
    branch's hours both are noise. "when does the post office close" was answered with the
    postage-times card, and "when do the banks open today" with how to open a bank account.
    Nobody here can know a named venue's hours, so the composer's honest line - where to find
    today's figure - is the one that answers the question asked (STYLE.md), and it takes the
    turn off an entry that matched one other word of the line.

    The reading is the composer's (bot/compose/fallback.py `venue_hours`): a place has to be
    named AND opening or closing has to be the ask, so "what time do hospitals let visitors in",
    "what time does boarding start" and "what time is my appointment today" are untouched. The
    candidate has to BE one of the composer's hours lines, from the fallback band, and it never
    repeats the last reply.
    """
    try:
        if not fallback.venue_hours(clean, None):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return None
    if not candidates or not _declares_topics(candidates[0].get("module")):
        return None
    try:
        lines = frozenset(_content(line) for line in fallback.venue_hours_lines())
    except Exception:  # noqa: BLE001 - a pool that cannot be read claims nothing
        return frozenset()
    if not lines:
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) >= 0 or _declares_topics(candidate.get("module")):
            continue
        reply = _content(candidate.get("reply"))
        if reply and reply in lines and not (last and reply == last):
            return index
    return None


def _the_bots_own_taste(candidates, clean, memory, last=""):
    """The index of the composer's taste for a line that asks what the bot likes, else None.

    The same shape as `_about_the_bot`: only a line the composer reads as a question about its
    own taste, and only where a card that declares topics is in front of it. The composer's line
    is one of its taste pools by construction (`reads_as_a_taste` checks the pool), so this rule
    never hands the turn to a shrug or a nod, and a line whose taste the composer has no reply
    for keeps whatever answered it.
    """
    if not candidates or not _declares_topics(candidates[0].get("module")):
        return None
    try:
        asked = fallback.reads_as_a_taste(clean, memory)
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return None
    if not asked:
        return None
    try:
        lines = frozenset(_content(line) for line in (getattr(fallback, "TASTE_LINES", ()) or ()))
    except Exception:  # noqa: BLE001 - a pool that cannot be read claims nothing
        return None
    if not lines:
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) >= 0 or _declares_topics(candidate.get("module")):
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        if reply in lines:
            return index
    return None


def _declares_topics(module_name):
    """True when a module declares the topics it answers (README.md, "Interface")."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
    except Exception:  # noqa: BLE001 - a module that cannot be read declares nothing
        return False
    return bool(_labels(getattr(module, DECLARED_TOPICS, ())))


def _the_verdict_back(candidates, last="", memory=None):
    """The index of the module's own answer to the verdict, or None.

    Not the candidate that happens to be ranked first: the answer to the news can be ranked
    below a card that only owns a word of it, so the whole list is asked.

    The opener test (`A_VERDICT_BACK`) alone kept out a card that owns a word of the verdict - but
    it also threw away the answers that are about the news: the card for a pet that died opens
    "I'm sorry, that's one of the hardest days", which is not a verdict taken up, and gray-cypress
    found it standing down. So the answer is kept either way round: a line written for the verdict
    (the opener) or a line about the news (`_about_the_news`). An answer that says the last one
    again is neither - it is not a second answer - so the pool is free to take that turn.
    """
    for module_name in KEEPS_ITS_OWN_ANSWER + ANSWERS_THE_NEWS:
        is_a_card = module_name in ANSWERS_THE_NEWS
        for index, candidate in enumerate(candidates):
            if str(candidate.get("module") or "") != module_name:
                continue
            if _priority(candidate) < 0:
                continue
            reply = _content(candidate.get("reply"))
            if not reply:
                continue
            if last and (reply == last or _echoes(candidate.get("reply"), last)):
                continue
            if _says_the_same_thing_again(candidate.get("reply"), last):
                continue
            if not is_a_card and A_VERDICT_BACK.match(reply):
                return index
            if _about_the_news(candidate.get("reply"), memory):
                if not _the_subject_was_answered(candidate, memory):
                    return index
                continue
    return None


def _verdict_reply(candidates, text, memory, last="", clean="", best=0):
    """The index of the candidate a bare verdict on the news is answered with, else None.

    "what a hassle" after an answer about cooking is the person saying how the news sits with
    them. It has no subject of its own, so nothing may answer it with the topic the conversation
    is on: the same-advice path matched "cooking" and answered "Nothing separate for a hassle - it
    is the same advice: <the cooking answer>", which is the bot talking to itself, and any entry
    that owns the verdict's noun answered the noun ("Nightmares usually follow stress").

    Two turns keep the floor: a live emergency thread, where "thats annoying" is still that
    thread, and a line a whole-line module read for itself (grief, loss) - after "my mum died last
    week", "thats a shame" is not a light verdict, and the grief module's answer stands.
    """
    if not _reads_as_a_verdict(text, memory):
        return None
    if _priority(candidates[best]) >= WHOLE_LINE_BAND:
        return None
    if _in_a_careful_thread(clean or text, memory):
        return None
    # A module that read the line and said the verdict back in its own words keeps the turn: "i
    # cant sleep" then "thats annoying" was chat's "It is. Being cross about it for a bit is fair
    # enough.", and a tired thread's own line ("That kind of tired needs an early night") is
    # specific where the pool is general. The pool is better than a floor, a hedge or an echo -
    # not better than an answer that already answered.
    back = _the_verdict_back(candidates, last, memory)
    if back is not None:
        return back
    return _the_verdict_turn(candidates, _verdict_lines())


def _instead(text, candidates, last="", own=(), clean=""):
    """The index of a candidate whose module answers in place of the topic entries, else None.

    A topic entry matches a word or a topic id of the line, so on a line another module read as
    a whole it can answer a different question: "some days i can't get out of bed since my mum
    died" matched the gift-for-mum entry on "mum" and "get", "we had to put our cat down" matched
    litter trays on "cat", and "what do i write in a condolence card" matched a card shop. A
    module that declares `ANSWERS_INSTEAD` read the whole line and says so, so it wins the turn;
    it proposes only on the lines it is sure of, so it is not a priority to raise.

    Every candidate is looked at, not only the ones above priority 0: a module that read the
    whole line may sit in the fallback band on purpose - it proposes nowhere else, so a low
    priority is the honest place for it - and a declaration that only worked from the real band
    would make "I answer in place of the entries" a promise the arbiter then broke. Measured on
    main with no fallback-band declarer: no reply changes, so this only widens the door.

    Checked after the safety band, so a real emergency is still the safety module's turn, and
    before the specialist rule, so a topic entry cannot take the line back on a word. It also
    carries what the composer's death rule used to do on the turns after a death: the loss
    module answers "the anniversary is next week" and "i cant sleep" while the thread is still
    a bereavement, and passes a practical ask inside it ("how do i cancel her phone contract")
    to the topic entry that can answer it.

    A declaring module can also carry `DEFERS_TO`, a test on another candidate's reply, for the
    turns where an entry answers the line better than it can: the test passing lets that entry
    keep the turn (`_defers`). It is opt-in, so a module that declares nothing here is unchanged.
    """
    for index, candidate in enumerate(candidates):
        module = candidate.get("module")
        if not _declares_instead(module):
            continue
        if last and _content(candidate.get("reply")) == last:
            continue  # the never-repeat rule holds in every band
        keeps = _defers(module, candidates, skip=index, last=last, own=own, clean=clean,
                        text=text)
        if keeps is not None:
            return keeps  # the entry that already answers this line better keeps the turn
        # A line that puts one subject down and takes another up is answered on the new one: the
        # first half is the thread being left. "im fine really, anyway whats a good way to sell her
        # furniture" was answered by the grief pool's company line ("I'm here. Take your time with
        # it"), which meets the first half and leaves the question asked, while the entry had the
        # answer to it. The claim to read the whole line is only worth the turn while the reply
        # says something the new subject is about, and one shared word is enough to say the other
        # reply is the closer one, because this claim is stronger than an entry's.
        subject = aboutness.after_a_change_of_subject(text)
        if subject:
            closer = aboutness.the_better_answer(candidate.get("reply") or "", candidates, subject,
                                                 skip=index, need=1)
            if closer is not None:
                continue
        keeps = _the_entry_that_answers_the_ask(candidates, index, clean or text)
        if keeps is not None:
            return keeps  # the ask clause is the question, and that entry answers it
        return index
    return None


def _the_entry_that_answers_the_ask(candidates, skip, line):
    """The index of a reply that answers the clause the line asks in, else None.

    A module that declares `ANSWERS_INSTEAD` reads the whole line and answers the situation it
    recognises, and on a two-part line that situation is often in the clause before the question.
    "a funeral on tuesday and i need something dark" was met with a condolence, while the reply
    that says what to wear sat in the list at 7000 and named "dark": the person asked what to put
    on, not how sorry the week is. So the declaring module stands back when another reply names a
    word of the ask clause and its own reply names none of it - the closest reply to the line
    keeps the turn, which is the rule the arbiter applies everywhere else.

    Nothing here reads a wording of the module's own: a condolence on a line that asks for
    nothing ("my dad died last month") names the ask clause's words often enough to keep its turn,
    and the camel's-back case for the declaring module - "we had to put our cat down, can we bury
    him at home" - is answered by the pets entry, which is the outcome `DEFERS_TO` already had.
    """
    words = _the_ask_clause(line)
    if not words:
        return None
    for index, candidate in enumerate(candidates):
        if index == skip or _declares_instead(candidate.get("module")):
            continue
        if _priority(candidate) < 0:
            continue
        reply = candidate.get("reply")
        if not reply or not _about_the_line(reply, words):
            continue
        if _about_the_line(candidates[skip].get("reply"), words):
            return None  # both name the ask, so the module's own reading stands
        return index
    return None


def _defers(module_name, candidates, skip, last="", own=(), clean="", text=""):
    """The index of a candidate whose reply already does what the declaring module would say.

    A module can read the whole line and still meet an entry that answers it better, because
    the entry knows the topic and the module only recognises the situation: "we had to put our
    cat down yesterday" is the pets entry's line (cremation, home burial, a paw print), and the
    module's sympathy is the poorer answer. The module declares `DEFERS_TO`, a test on a reply,
    so the arbiter still reads no wording of its own: a reply that passes it keeps the turn.

    The test is called with the reply and the line (`test(reply, text)`), because the same reply
    can be right for one line and wrong for the next: the pets entry answers "we had to put our
    cat down yesterday" and is the wrong answer to "my cat died and i keep crying". A test
    written for the reply alone (`test(reply)`) is called with the reply only.
    """
    test = _defers_to(module_name)
    if test is None:
        return None
    for index, candidate in enumerate(candidates):
        if index == skip or _declares_instead(candidate.get("module")):
            continue
        if int(candidate.get("priority") or 0) < 0:
            continue  # the fallback band apologises for everything: it cannot keep a real turn
        if own and _match(candidate.get("module"), own, (), (), clean) <= 0:
            continue  # only an entry that answers the topic this line names can keep the turn
        if last and _content(candidate.get("reply")) == last:
            continue  # the entry cannot keep the turn with the reply just given
        reply = candidate.get("reply") or ""
        try:
            if test(reply, text):
                return index
        except TypeError:  # a test written for the reply alone is still a test
            try:
                if test(reply):
                    return index
            except Exception:  # noqa: BLE001 - a test that raises defers to nobody
                continue
        except Exception:  # noqa: BLE001 - a test that raises defers to nobody
            continue
    return None


def _declares_instead(module_name):
    """True when a module says it answers in place of the topic entries (README.md, "Interface")."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
    except Exception:  # noqa: BLE001 - a module that cannot be read declares nothing
        return False
    return bool(_labels(getattr(module, DECLARED_INSTEAD, ())))


def _declared(module_name):
    """The topics a module declares (README.md, "Interface"), or () when it declares none."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
    except Exception:  # noqa: BLE001 - a module that cannot be read declares nothing
        return ()
    return _labels(getattr(module, DECLARED_TOPICS, ()))


def _named_topics(memory):
    """The topics the line itself names, not the one the reading infers from the kind of line.

    `understood["topics"]` is what the words in front of the bot point at ("my hand is still
    sore" -> health); `understood["topic"]` also carries the fallback the reader uses for a kind
    of line ("hiya" -> small-talk). A module keeps its turn inside an emergency because the
    person asked about its subject, so only the first counts: a bare greeting is not asking
    chat about small talk, and on a live crisis thread it was getting "Morning! How's your day
    going?" while the composer was still answering it.
    """
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        return set()
    return _labels(understood.get("topics")) - CHITCHAT


def _thread_index(candidates, real, own, target, last, care_about="", memory=None, line=""):
    """The composer's continuation for a safety thread, or None.

    After the bot has answered an emergency, the next line ("im scared") is not small talk: it
    is the same thread, and a light module proposing a reframe would win it on PRIORITY. The
    composer already has a continuation for exactly that line, so the routing decision is to
    give the turn to the module the composer answers through - `fallback.FALLBACK_MODULE`,
    the one module whose whole reply is the composer's - and to nothing else. The wording
    stays in bot/compose/ for the composer lane to own.

    Matching the *module* rather than the text is what makes the thread hold: the composer
    draws its continuation from a pool, and the draw the arbiter makes and the draw the
    module makes are two calls, so a text match only holds while both pick the same line. On
    the ones where they differed ("you there?" after "my dad is having chest pain"), chat's
    "Yep, I'm here" took a live emergency thread - the flaky red in `test_chat`.

    A module that declares the line's own topic is answering the question asked, so it keeps
    its turn even inside the thread (a health entry quoted back mid-emergency).

    The one exception is a follow-up about the very thing the bot has just answered, in a
    first-aid thread: "can i pop the blister" after the scald answer names a word the clothing
    entry claims, and that entry's answer ("break new shoes in slowly") is for a different
    person with a different blister. The composer's continuation is the burn's own line, so it
    keeps the thread. It takes both halves to say so: the thread must be a care thread (a
    crisis answer's next question is often about something else), and the line must name
    something the last answer named - a new question in the thread still goes to its entry.
    """
    text = target[0] if target else ""
    if not _content(text):
        return None
    # The line asks about the thing the thread has answered. The thread's answer is read as well
    # as the last reply, because inside a care thread the last reply is a pool line: "Don't put
    # anything on a burn - not butter, not cream, not ice. Twenty minutes under cool running
    # water, then a loose clean dressing" never says "blister", and "can i pop the blister" was
    # answered by the blister-plaster entry (shoes) instead of the burn's own line.
    asks = fallback.asks_about_a_care_answer(care_about, last, memory, own)
    # A follow-up that points at the thread instead of naming a subject ("does it get better",
    # "will i be ok") names no topic of its own, whatever label the understanding engine infers
    # for it - and that label is what let a module take a live emergency off the composer: an
    # overdose answered with "Compare the price per kilo or per 100g on the shelf label", a
    # breathing emergency with the price card too. A pronoun line belongs to the thread it points
    # at, so the topic exception below does not apply to it. The reading is the composer's
    # (`bot/compose/outlook.py`), and only the lines with no subject of their own are affected.
    # Read from the line the person typed, not from `target`, which is the composer's own
    # continuation and would read as pointing at itself.
    pointed_at = _outlook.points_at_the_thread(line or text)
    if (not pointed_at and any(own and _labels(_answered(candidates[index].get("module"))) & own
                               for index in real) and not asks):
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) < 0 and candidate.get("module") == fallback.FALLBACK_MODULE:
            reply = _content(candidate.get("reply"))
            if not reply or reply == last:
                return None  # nothing to say, or the same line again
            if asks:
                # Both candidates can be on topic, and priority does not say which one continues
                # the conversation. The reply that says more of the answer in hand does: the
                # burn's own line shares ten of its words, the shoe answer ("a padded blister
                # plaster and wear the shoes for short stretches") shares three, while for
                # "should i cover the blister" it is the entry's "cover it with a clean
                # non-fluffy dressing" that carries the answer and the pool line that carries
                # none of it. So the entry keeps the turn where it is the answer, and the
                # composer keeps it where the entry is about another thing. See
                # `fallback.how_much_of_the_answer_kept`.
                mine = fallback.how_much_of_the_answer_kept(candidate.get("reply"), memory)
                for other in real:
                    closer = fallback.how_much_of_the_answer_kept(
                        candidates[other].get("reply"), memory)
                    if closer > mine:
                        return other
            return index  # the composer's continuation for this thread
    return None


def _the_answer_written_out(memory):
    """The last answer as the person read it: punctuation and case kept."""
    turns = memory.get("turns")
    if isinstance(turns, list) and turns and isinstance(turns[-1], dict):
        return str(turns[-1].get("bot") or "")
    return ""


def _last_reply(memory):
    turns = memory.get("turns")
    if isinstance(turns, list) and turns and isinstance(turns[-1], dict):
        return _content(turns[-1].get("bot"))
    return ""


def _said_before(memory, text):
    """Whole answers the bot has already given this person, as `_content` strings.

    Only answers of two or three sentences count (`at least eight words`): a short "Got it." is
    a thing a friend says twice and no repeat, and it is never the whole of a real answer. The
    turn being answered is not in `memory["turns"]` yet, so this is the conversation so far.

    A turn whose question is this line word for word is left out: the same question asked again
    is answered again, in the wording the repeat frame gives it (`bot/memory/again.py`), and
    that rule is what tells the person where the answer went. So this is only the answers to
    other questions, which have no business coming back here.
    """
    said = set()
    turns = memory.get("turns")
    if not isinstance(turns, list):
        return said
    asked = _content(text)
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        if asked and _content(turn.get("user")) == asked:
            continue
        reply = _content(turn.get("bot"))
        if len(reply.split()) >= _SAID_BEFORE_WORDS:
            said.add(reply)
    return said


def _about(text, memory):
    """What this turn is about: (the topic the reading gives it, the topic only a stored record
    names, the line's words, the whole line), all lower case.

    The first set is the understanding engine's reading of this turn, `understood["topics"]`
    (the line by itself) and `["topic"]` (the line plus what a follow-up inherits from the
    conversation), and both count 2: they are one reading, and the engine has already decided
    how much a follow-up leans on the line before. So on a follow-up the conversation's topic
    ties with the line's own, and PRIORITY settles it - whether that is the right rule is
    written down in the routing lane plan, not decided here. Only a record that names a topic
    outright (`memory["topic"] = {"label": "cooking"}`, the shape the memory lane agreed) is
    the weaker signal, at 1.
    """
    understood = memory.get("understood")
    own = set()
    words = set()
    if isinstance(understood, dict):
        own |= _labels(understood.get("topics"))
        own |= _labels(understood.get("topic"))
        for word in _strings(understood.get("words")):
            words.update(WORD.findall(word.lower()))
    carried = _labels(memory.get("topic")) - own
    clean = " ".join(WORD.findall(str(text).lower()))
    words.update(clean.split())
    return own, carried, words, clean


def _strings(value):
    """The strings in value, one level deep (a list, a tuple, a set, or one string)."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set, frozenset)):
        return [item for item in value if isinstance(item, str)]
    return []


def _label(value):
    """One topic label, canonical: lower case words joined by spaces, so "small-talk",
    "Small talk" and "small_talk" are the same topic."""
    return " ".join(WORD.findall(str(value).lower()))


def _labels(value):
    """The topic labels in a value the understanding engine or the conversation wrote: a label,
    a list of labels, one of the records a lane writes (`{"id": ...}` from the understanding
    engine, `{"label": ...}` or `{"text": ...}` from the memory store), or a mapping of topic
    -> score. Anything else, including a whole memory dict, adds nothing.

    A record is read from its label key only. The other keys of a record describe it ("turn",
    "kind", "words") and are not labels, so reading them would make every specialist miss
    the topic and the specialist rule silent."""
    found = set()
    if isinstance(value, str):
        found.add(_label(value))
    elif isinstance(value, dict):
        found |= _stored(value)
        for key in LABEL_KEYS:
            if isinstance(value.get(key), str):
                found.add(_label(value[key]))
                break
        else:
            if "topics" in value:
                found |= _labels(value.get("topics"))
            elif value and all(not isinstance(item, (dict, list, tuple))
                               for item in value.values()):
                for key in value:  # a mapping of topic -> score
                    if isinstance(key, str) and key not in LABEL_KEYS:
                        found.add(_label(key))
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            found |= _labels(item)
    found.discard("")
    return found


def _stored(record):
    """The topic of the line the conversation is on, when a record only keeps the line itself
    (`{"turn", "text", "words"}`, the shape the memory store writes). The stored line is read
    with the understanding engine, the same reader the current line gets, so a follow-up ("and
    how long?") is about what the earlier line was about and the specialist rule still fires.
    """
    text = record.get("text") if isinstance(record.get("text"), str) else ""
    if not text.strip():
        text = " ".join(_strings(record.get("words")))
    return _read_topic(text)


def _read_topic(text):
    """The topic id the understanding engine gives for a line, or nothing when it gives none."""
    key = " ".join(WORD.findall(str(text or "").lower()))
    if not key:
        return set()
    found = READ.get(key)
    if found is None:
        try:
            from ..understanding import topics as understood
            from ..understanding.normalize import normalise
            read = normalise(key)
            topic, score = understood.detect_topic(read, None, understood.detect_entities(read))
            found = {_label(topic)} if topic and score >= 2 else set()
        except Exception:  # noqa: BLE001 - a reader that fails adds no topic
            found = set()
        READ[key] = found
    return set(found)


def _answered(module_name):
    """The topic labels a module declares it answers. Declared per module, so it is read from
    the module itself (README.md, "Interface")."""
    try:
        module = importlib.import_module("." + str(module_name), 'bot.modules')
    except Exception:  # noqa: BLE001 - a module that cannot be read declares nothing
        return set()
    return _labels(getattr(module, DECLARED_TOPICS, ()))


def _match(module_name, own, carried, words, clean):
    """How well a module's declared topics fit this turn: 2 for a topic id the reading gives
    this turn (the line, or on a follow-up the conversation it is still on), 1 for one only a
    stored record names, 1 for a declared phrase or word the line contains. 0 when it declares
    nothing that fits, so a generalist keeps its PRIORITY over a specialist of some other
    topic."""
    score = 0
    padded = " " + clean + " "
    for label in _answered(module_name):
        if label in own:
            score += 2
        elif label in carried:
            score += 1
        elif " " in label:
            if " " + label + " " in padded:
                score += 1
        elif label in words:
            score += 1
    return score
