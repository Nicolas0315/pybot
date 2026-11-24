"""Part 4 of 6 of the module, split out of `repeat`.

Everything here is re-exported from `repeat`, so callers import it from there as before.
"""
import re

from ..compose import pick
from . import history, limits, narrow, topics
from .repeat_part_01 import (
    WHOLE_OF_IT, _doings, _recent_answers, HEDGE, STEP_WITH_ITS_METHOD, CONDITION_CLAUSE,
    FIRST_THING, NOT_A_MOVE, SENTENCE, _SO_COMES_THE_STEP, _SO_DOES_NOT_ASK_SOMETHING_OF_THEM,
    _a_step_comes_after, _explains, _opening_move, ALSO_LEADS, AND_NOW, AT_A_LOSS, LOST_LEADS,
    MORE_LEADS, MOVE_ASK, NEXT_LEADS, PUT_RIGHT_LEADS, REFER_BACK, SAY_AGAIN_LEADS, USE_WITH,
    _only_echoes_between, _short, _the_answer_about_what_we_are_on, a_step_of_the_same_answer,
    asks_to_put_it_right, NEXT_STEP_EMERGENCY, TRIED_LEADS, ABOUT_THE_BOT, ASKING_THEM, ASKS,
    QUESTION, WORDS_WANTED, without_a_reset, MOVE_VERBS, NOT_A_STEP, PIECE_END, A_MENU, CUT_WORDS,
    DANGLING, NEEDS_COMPLEMENT, SHORT_STEP, STEP_WORDS, _a_verb_after_a_leading_phrase,
    _the_first_instruction_in_a_long_piece, CHANGE_ASK, CHANGE_LEADS, MOVE_LEADS, LEAD_SAYS_FIRST,
    NOW_LEADS, STEP_SAYS_FIRST,
)
from .repeat_part_02 import (
    A_LENGTH_ASK, LENGTH_BACK, _a_bare_time, _a_length_already_handed, _handed_back, _a_bare_ask,
    _a_city_guide_is_the_answer_in_front, _a_conditional_move, _a_what_to_do_answer,
    _already_repeated, _an_entry_answers_it, _another_part, _handed_back_already, _handed_back_last,
    _the_price_the_answer_gave, asks_for_more,
)
from .repeat_part_03 import (
    names_nothing, ATTEMPT, QUESTIONS_THAT_ARE_NOT_STEPS, HOW_IT, IDEAS_ONLY, QUESTION_MORE,
    WORDING, _a_lead_and_a_step, _a_step_done, _later_part, _the_lead_for, _tried, a_more_ask,
    asks_for_the_move, says_where_to_start, _next_step, _agreed, _content, _says_they_agree,
    _the_thing_they_named, ACK_OPENS, ASKING_TO_START, REJOINDER, SOMEONE_ELSES_LIMIT, _a_feeling,
    _a_thing_of_its_own, _the_advice, _the_doing, _the_step_just_given, _the_untried, _trouble,
    LIST_LEAD, NOT_A_DOING, _inside_a_bracket, A_QUESTION, NOT_A_TAIL, DECLARATIVE, _places_to_cut,
    WHAT_IT_IS, NOT_A_SUBJECT,
)


def asks_for_the_same_work(text, memory):
    """True when a line that names nothing asks for the answer the question before it got.

    This is the test a knowledge answer gives way to: a line like this has no thing of its own,
    so the entry it reaches is a neighbour of the subject rather than the question asked - but
    only when the work is the same work. A new verb is a new question and keeps its own answer.
    """
    if not names_nothing(text):
        return False
    if history.about_the_chat(text):
        # "how did we start?" names nothing and carries a verb this reader knows ("start"), and
        # the question it follows said "im trying to save 3000 pounds for a car", whose "trying"
        # is in the same verb family - so the same-work rule took a question about the chat and
        # answered it "Start with this: pick the rate your pay can carry". A line that asks what
        # was said before is never a request for the answer again: the store recaps it.
        return False
    asked = _doings(text)
    if not asked and not (set(topics.words(text or "")) & WHOLE_OF_IT):
        return False
    whole = bool(set(topics.words(text or "")) & WHOLE_OF_IT)
    for back, question, said in _recent_answers(memory):
        if back > 1 and not _about_the_same_thing(question, said, memory):
            continue
        return whole or bool(asked & _doings(question))
    return False


def _nothing_but_acknowledgements(back, memory):
    """Nothing has answered since that answer: only acknowledgements of the person's own line.

    "my back hurts" -> the answer, "ive tried stretching" -> "Got it - you've tried stretching",
    "what else can i do": the answer is still the last thing said about it, so a follow-up that
    names nothing of its own is about that answer. A real answer in between (cooking, money)
    means the chat has moved and the older paragraph is not what the line leans on.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if back <= 1 or back > len(turns):
        return True
    for turn in turns[len(turns) - back + 1:]:
        if turn.get("module") == "answers":
            return False
        line = str(turn.get("user") or "")
        if len(line.split()) > 6 and not ATTEMPT.search(line):
            return False
    return True


def _about_the_same_thing(asked, said, memory):
    """The answer belongs to what the chat is still on, not to a subject that has moved."""
    # A line the bot had no answer to does not move the chat on. "i eat takeaway three times a
    # week" was met with "Got it. Is there anything you'd like a hand with?", and the ask for the
    # first move after it is still about the answer two turns back - the bot never answered the
    # detail, so it cannot have left the subject. Without this the ask went to nobody and the
    # person who had just been told what to do about their tiredness got a search hedge.
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if turns and HEDGE.search(str(turns[-1].get("bot") or "")):
        return True
    subject = [w for w in topics.words(topics.subject(memory) or "")
               if w not in topics.STOPWORDS]
    if not subject:
        return True
    # An answer that does not use one word of the line it answered is not an answer about that
    # line, whatever subject that line was on: the knowledge base reached a cheap-food answer for
    # "were redoing our bathroom on a budget", and two turns later the ask for what to spend on
    # first was handed a food step under "I would start here", out of an answer made of rice and
    # lentils. The older turn's own question is about its own subject by construction, so it is
    # the answer's words that decide this, not the question's.
    theirs = {w for w in topics.words(asked) if len(w) > 2 and w not in topics.STOPWORDS}
    mine = {w for w in topics.words(said) if len(w) > 2 and w not in topics.STOPWORDS}
    # The entries behind the answer count as the answer's words. A card written for the person's
    # own words never says them back: "i have slugs everywhere" is answered with "Go out after dark
    # with a torch and pick them off ... copper tape round pots", where slugs are only "them", so
    # the answer looked like one that had nothing to do with the line it answered, and the chat
    # was declared to have moved on after one turn. The entry behind it is keyed on slugs, and the
    # ask that follows is still about that card.
    mine = mine | {w for w in _the_keys_of(said, memory) if len(w) > 2}
    if theirs and not (mine & theirs):
        return False
    broken = set(topics.words(asked)) | set(topics.words(said))
    if broken & set(subject):
        return True
    # A line that reports having a go at the answer ("ive tried stretching") is a line about that
    # answer, even though the word it reports is the word the chat is now on. Without this the
    # attempt in between hid the answer and the next ask got a search instead of the next step.
    mine = {w for w in topics.words(said) if len(w) > 2 and w not in topics.STOPWORDS}
    for turn in (memory.get("turns") or [])[-3:]:
        if not isinstance(turn, dict):
            continue
        line = str(turn.get("user") or "")
        if not ATTEMPT.search(line):
            continue
        if len(mine & {w for w in topics.words(line) if len(w) > 2}) >= 2:
            return True
    return False


def _the_chat_is_still_on(said_before, memory):
    """Whether the thing the chat is on now is still the thing this older answer was about.

    `_about_the_same_thing` asks an older answer whether it is about the line it answered, and a
    knowledge answer is about its own question by construction, so that reading cannot see a
    subject that came in between. "ive started running three times a week" / "i want to lose a
    stone" / "how long will it take" was answered "20 to 30 minutes" - the length of the runs,
    from the answer two turns back - because the only thing the reader compared was the running
    question with the running answer. The line the chat is on says which thing the person is
    asking about now, so a figure said about something else is not handed back.
    """
    topic = memory.get("topic") if isinstance(memory, dict) else None
    now = {w for w in topics.words(str((topic or {}).get("text") or ""))
           if len(w) > 2 and w not in topics.STOPWORDS}
    if not now:
        return True
    then = {w for w in topics.words(said_before) if len(w) > 2 and w not in topics.STOPWORDS}
    return bool(then & now)


def _a_question(said):
    """Whether the sentence asks rather than tells.

    The bot's own question is not a step: a wish to write a book is answered with "tell me what
    you last enjoyed and I'll narrow it down", and handing that back as "Start with this: Tell me
    what you last enjoyed" is the bot asking the person its own question as if it were advice.
    A step never opens on an interrogative, and "do the theory test early" starts on a verb, so
    verbs are not in the list.
    """
    text = str(said or "").strip()
    if text.endswith("?"):
        return True
    return bool(QUESTIONS_THAT_ARE_NOT_STEPS.match(text))


def _a_move(said, questions_are_steps=False):
    """The move in the answer, when it is a move and not the answer with a lead on it.

    A move is one thing to do: "Stop the cycle and turn the water off". `_a_move_in` reads the
    answer for the sentence that says what to do, and on an answer whose opening sentence says
    what to do and how, all season and at what pace, it hands back thirty-five words of it. Said
    under a lead ("That's the one: start where you can already run 5km comfortably and build up
    over about sixteen weeks: three runs a week (one long, two short and easy)...") that is the
    answer again with two words in front of it, and the ask that gets it is the one the answer
    already answered. Past a step's length there is no one thing to do, so this reader stands
    down and the answer comes back as the repeat it is.
    """
    move = _a_move_in(said, questions_are_steps=questions_are_steps)
    if move and len(move.split()) > STEP_WITH_ITS_METHOD:
        return None
    return move


def _a_move_in(said, questions_are_steps=False):
    """The sentence of the answer that tells them what to do, or None.

    `questions_are_steps` is for the reader that hands back what still stands of an answer the
    person has just ruled part of out (`bot/memory/obstacle.py`): the bot's own question is part
    of what stands ("Then skip black pepper - the rest of it stands: tell me what is in the fridge
    and I will pick properly"), where as the first thing to do it is the bot asking itself.

    A knowledge answer either opens with what to do ("Stop the cycle, unplug it and turn the
    water off") or opens with what is true and ends with what to do ("Most bad posture is the
    chair and the sitting still: set the screen so the top of it is at eye level"). The opening
    sentence wins when it is an instruction: it is the first step, and the step is what was asked
    for. Only when the answer opens on a fact is the last instruction the move.
    """
    parts = [p.strip() for p in SENTENCE.split(str(said).strip()) if p.strip()]
    if parts:
        opening = _opening_move(parts[0])
        if opening and (questions_are_steps or not _a_question(opening)):
            return opening
    for part in reversed(parts):
        # A red flag is not a move. A health answer ends with the warning ("Get it looked at if it
        # gives way"), so walking the sentences backwards found the warning first, and a person
        # who has just been told to ice it was met with the A&E sentence alone. The skip is the
        # one `topics` uses for the same reason, so the two paths cannot drift.
        if topics.RED_FLAG.match(part):
            continue
        named = FIRST_THING.match(part)
        if named:
            move = named.group("move").strip(" ,;:")
            if (2 <= len(move.split()) <= 20 and not topics.RED_FLAG.match(move)
                    and (questions_are_steps or not _a_question(move))):
                return move[0].lower() + move[1:]
        head = _opening_move(part)
        if (head and not CONDITION_CLAUSE.match(head) and not NOT_A_MOVE.match(head)
                and (questions_are_steps or not _a_question(head))):
            return head

        if _explains(part) and not _a_step_comes_after(part):
            # The sentence explains how something is, and every clause of it is part of the
            # explanation: a verb-shaped first word in one of them is that clause's subject, not
            # a move ("water goes in at the mouth" is not something to do). The one exception is
            # the conclusion: a sentence that ends "..., so clear the vents" explains nothing
            # after its "so", it tells them what to do.
            continue

        for piece in [part] + part.split(":"):
            # A step is often the second clause of a sentence whose first clause names where to do
            # it: "On a Mac: ... Storage, click the bar and let it finish scanning ... Empty the
            # Bin, clear the Downloads folder". Walking only the first clause of each sentence
            # found no move in a reply made of them, so "what should i delete first" after the
            # storage answer had nothing to hand back.
            from ..compose.verdict import IMPERATIVES  # the verbs an instruction can open on
            # A comma between two digits is a thousands separator, not a clause: "Aim for 10%
            # of the price: £20,000 on a £200,000 home" was cut at the comma inside the number,
            # and the step handed back said "Aim for 10% of the price: £20" - a wrong figure
            # under a lead that presents it as the answer's own words.
            clauses = re.split(r"(?<!\d),(?!\d)| - |;| \u2014 |\. ", piece)
            conditional = False
            # How deep inside a bracket the last clause left the sentence. A comma inside
            # brackets is not a clause boundary: "(weather, air traffic control, a security
            # alert)" was cut at its commas and "air traffic control" was handed back as the
            # step, and "wash cool (30C, or 20C for anything with stretch)" was cut to "wash cool
            # (30C". A clause that opens inside a bracket is part of the aside, not a step.
            in_a_bracket = 0
            for clause in clauses:
                head = clause.strip(" .:;")
                if not head:
                    continue
                opened_inside = in_a_bracket > 0
                in_a_bracket = max(0, in_a_bracket + head.count("(") - head.count(")"))
                if opened_inside:
                    continue
                # "... so clear the vents" is the first clause that starts on the step, and the
                # joining word is not part of it. A conclusion is delimited by the sentence's own
                # comma, so it is a whole step however long the explanation in front of it was.
                a_conclusion = bool(_SO_COMES_THE_STEP.match(head))
                head = _SO_COMES_THE_STEP.sub("", head)
                if not head:
                    continue
                if head.count("(") != head.count(")"):
                    # The other half of the same bracket: the clause after the aside ends on a
                    # ")" and what is left reads as a step when it is the tail of one.
                    continue
                if a_conclusion and _SO_DOES_NOT_ASK_SOMETHING_OF_THEM.match(head):
                    continue
                if CONDITION_CLAUSE.match(head):
                    # The rest of this sentence is what to do in that case, not now.
                    conditional = True
                    continue
                if conditional:
                    continue
                if topics.RED_FLAG.match(head):
                    continue
                if NOT_A_MOVE.match(head):
                    # A referral ends a health answer; it is not the first thing to do.
                    continue
                words = head.split()
                if not 2 <= len(words) <= (STEP_WITH_ITS_METHOD if a_conclusion else 14):
                    continue
                if words[0].lower() not in IMPERATIVES:
                    continue
                if not questions_are_steps and _a_question(head):
                    # "tell me what you last enjoyed and I'll narrow it down" is the bot's own
                    # question: "tell" is an instruction and the sentence is not one.
                    continue
                break
            else:
                continue
            # "Start with run-walk: one minute of easy jogging" already leads; a lead in front of
            # it says start twice, so that sentence is the answer's opening, not a move.
            if re.match(r"(?:start|begin) with\b", head, re.I) and ":" in part:
                continue
            return head[0].lower() + head[1:]

    return None


def _the_time_an_earlier_answer_gave(text, memory):
    """The length an answer further back gave, when the line asks for one and the last one does
    not hold it.

    "i want to run a 5k" ("Three runs a week gets most people to 5k in about eight weeks") /
    "im 45 and havent run since school" ("Come back at about half of what you used to do ...") /
    "how long to train" was met with "That's beyond what I know well, sorry", a search hedge,
    while "eight weeks" sat in the chat two turns back. The answer in hand is the wrong place to
    look: it is about how hard to come back, not how long, and narrowing it gives no length.
    """
    said_line = str(text or "")
    if not A_LENGTH_ASK.search(said_line) or narrow.kind_of(said_line) != "time":
        return None
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if len(turns) < 2:
        return None
    # The answer in hand is the normal place for this: when it can be narrowed to the length, the
    # readers below hand that part back and this one keeps out of it.
    last = str(turns[-1].get("bot") or "")
    if last and _a_bare_time(narrow.narrow(last, said_line)):
        return None
    for back, asked, said in _recent_answers(memory):
        # Two answers back is the case people have: a detour, then the ask. An answer from six
        # turns back is likely a different plan that happens to share a word.
        if back < 2 or back > LENGTH_BACK or not narrow.SPANS["time"].search(said):
            continue
        if not _about_the_same_thing(asked, said, memory):
            continue
        # A length from an older answer is only this line's length when the chat is still on the
        # thing that answer was about: "ive started running three times a week" / "i want to lose
        # a stone" / "how long will it take" was given "20 to 30 minutes", the length of the runs,
        # because the older answer is about its own question by construction and nothing asked
        # whether the subject in between had changed the thing being measured.
        if not _the_chat_is_still_on(asked + " " + said, memory):
            continue
        part = _a_bare_time(narrow.narrow(said, said_line))
        if part and not _a_length_already_handed(part, memory):
            return _handed_back(memory, part)
    return None


def answer_for(text, memory):
    """The answer they just asked for again, or None when this is not that turn."""
    from ..compose import limit as limit_line  # noqa: PLC0415 - no import cycle at load
    # The card in front is a city's places, and which of them comes first is the city row's own
    # question: this reader would hand back a sentence of the card that reads like a first step.
    if asks_for_the_move(text) and isinstance(memory, dict) \
            and _a_city_guide_is_the_answer_in_front(memory):
        from ..knowledge import travel  # noqa: PLC0415
        if travel.asks_which_one_first(text):
            return None
    # "anything else" is an ask for the next part only where there is a part to give, so it is
    # let past `names_nothing` for the shape below and not for every arm of this function.
    more = asks_for_more(text) and _handed_back_last(memory)
    # The free time just planned is the thing "with it" points at, and the answer to it is the
    # plan again: see `_a_what_to_do_answer`.
    if USE_WITH.search(str(text or "")) and not _a_what_to_do_answer(memory):
        return None
    if WORDING.search(str(text or "")):
        return None  # a line about how to say it is not a line about the last answer
    # The length asked for, when the answer that gave it is further back than the last one: see
    # `_the_time_an_earlier_answer_gave`.
    time_said = _the_time_an_earlier_answer_gave(text, memory)
    if time_said:
        return time_said
    # The price the answer on the screen gave, when the line asks what that costs without naming
    # anything of its own: see `_the_price_the_answer_gave`.
    price_said = _the_price_the_answer_gave(text, memory)
    if price_said:
        return price_said
    # The asks that name nothing of their own and still want the answer in hand: "anything else",
    # "where do i start", "how do i clean it off". Each is read out below by its own reader.
    put_right = asks_to_put_it_right(text)
    if not (names_nothing(text) or a_step_of_the_same_answer(text)) and not (
            more or says_where_to_start(text) or HOW_IT.search(str(text or ""))
            or a_more_ask(text) or put_right):
        return None
    # An ask for an idea is answered by the entries when an entry has an idea of its own to give:
    # "he'll eat pasta and cheese and not much else" / "any ideas" is another dish, and the step
    # this reader hands back is a clause of the dish already given ("Make a quick sauce with a
    # knob of butter"). Where every entry has is the same answer said again, the step is the one
    # thing on the screen the person has not read.
    if IDEAS_ONLY.match(str(text or "")) and _an_entry_answers_it(text, memory):
        return None
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    # The line that asks which part to do first is the one ask that a pointer back has not
    # already answered: "i keep burning the bottom of my pans" / "what am i doing wrong" (the
    # answer again, under a lead) / "how do i clean it off" wants the first clause of that
    # answer and has never had it, so the pointer guard leaves this ask alone.
    which_part = asks_for_the_move(text)
    if turns and not which_part and REFER_BACK.search(str(turns[-1].get("bot") or "")):
        return None
    # A turn that said the answer again with something taken out of it is not a turn after a new
    # answer: the answer behind it is still the one on the table, so an ask for the move after it
    # is answered from the whole answer, not from a fragment of the restatement. "my dog pulls on
    # the lead" / "no treats" / "how do i stop it" was handed "Same answer: Stand still until it
    # slackens" - the step with nothing round it - instead of the training answer it came from.
    if turns and limit_line.restates_the_answer(str(turns[-1].get("bot") or "")):
        return None
    tried = str(turns[-1].get("user") or "") if turns else ""
    wanted = narrow.kind_of(text)
    for back, asked, said in _the_answer_about_what_we_are_on(memory, _recent_answers(memory)):
        # The turn just before this one is the answer they are asking for; anything older is only
        # that answer if the chat has not moved on since. Adding a detail to the same thing and
        # having it said back is not moving on, so the answer behind it still stands: "we want to
        # grow some veg" / "we only have a small patio" / "what should we start with". An
        # acknowledgement of the person's own line is not the chat moving either.
        if (back > 1 and not _about_the_same_thing(asked, said, memory)
                and not _only_echoes_between(memory, back)
                and not _nothing_but_acknowledgements(back, memory)):
            continue
        if _a_new_work(text, asked):
            # "what is an apprenticeship" / "how do i get one": the line carries "get", a doing
            # the answer in hand never used, so this is a new question about the same subject and
            # the knowledge base answers it ("apply to them like jobs, because that is what they
            # are"). Handing the answer back gave the pay line under "Start with this" instead
            # (@blue-hedgehog, @sky-tuna, #6152). A line that asks back at the answer names no
            # doing of its own ("how do i do that", "where do i start") and is untouched.
            return None
        if wanted is not None and not narrow.carries(said, wanted):
            # A line can name nothing and still ask for a particular kind of fact: "how much
            # should i spend" after "im after a new kettle, mine leaks" names no thing, and the
            # answer it would be handed back says what has perished in the kettle and nothing at
            # all about money. Handing the paragraph back is what a person hears as not being
            # listened to - they asked a price and got the fault again. A figure the answer does
            # not carry is not the answer again, so this answer is not the one to give back.
            continue
        nothing_more = False
        if more:
            # Only after a step out of this answer: an answer that was read out in full has its
            # next part taken by the knowledge base's own reader, and the ask there is not the
            # same one. This branch is for the ask that comes after a *short form* of the answer,
            # where that reader is left holding a fragment and re-tells the paragraph instead.
            part, doing = _another_part(said, memory)
            if part:
                leads = NEXT_LEADS if doing else ALSO_LEADS
                return _handed_back(
                    memory, pick(leads, memory, text).format(step=part[:1].upper() + part[1:]))
        if (tried and not QUESTION_MORE.search(tried)
                and (_tried(tried) or _a_step_done(tried, said))):
            later = _later_part(tried, said)
            if later:
                short = _short(later)
                # The later step was already handed back once. On an explicit "what else" that is
                # still the only step left, so saying it under a lead beats the search shrug.
                return _handed_back(memory, _a_lead_and_a_step(
                    _a_lead_for(_the_lead_for(text, short), short, memory, text), short))
            if not a_more_ask(text):
                continue
            # "my back hurts" / "ive tried stretching" / "what else can i do": they named the part
            # they have tried and the rest of this answer is what they are asking for, so the
            # readers below get the answer. Main skipped it here because nothing below used to
            # read a "what else"; with that reader in place, skipping it is the search hedge.
        if a_more_ask(text):
            step = _the_next_step(said, memory)
            if step:
                _wording = step[:1].upper() + step[1:]
                return _handed_back(memory, pick(MORE_LEADS, memory, text).format(step=_wording))
            # "and what else" with no second step to hand over: the paragraph again is not one
            # more thing, so this reader steps aside - the step readers below get the line, and
            # past them an ask for more is not a repeat at all, so the whole answer under a
            # lead-in ("From just now: If you want something easy and good tonight: ...") is the
            # one reply this function must not write. `nothing_more` keeps it from the lead-in at
            # the end, which is where "what can i watch tonight" / "what else" was coming back
            # read out in full.
            nothing_more = True
        if asks_for_the_move(text):
            # "Where do i start" asks which part of the answer to do first, so it is read forwards
            # and the first instruction given, whatever verb it uses. The general reader below
            # walks backwards looking for a step, which gave the third step of a sleep answer.
            step = _the_first_step(said)
            if step and not _handed_back_already(step, memory) \
                    and not _they_say_they_tried(step, memory):
                _wording = step[:1].upper() + step[1:]
                return _handed_back(memory, _a_lead_and_a_step(
                    _a_lead_for(_leads_for(text), _wording, memory, text), _wording))
        if MOVE_ASK.search(text) or put_right or AND_NOW.match(text or ""):
            step = _a_move(said)
            if step is None and AT_A_LOSS.search(text or ""):
                # Nothing to do first, because every step in the answer waits on a moment: the
                # person at a loss is given that step with its moment, not the answer again.
                step = _a_conditional_move(said)
            if step and not _already_repeated(step, memory) \
                    and not _they_say_they_tried(step, memory):
                # Every lead ends on a colon or a full stop, so the step opens a sentence there
                # and takes a capital: "The thing to do first: Stop the cycle." An answer's own
                # wording is kept otherwise - this is the one letter formatting needs.
                said = step[:1].upper() + step[1:]
                if put_right:
                    # "can i fix it" carries no change word but CHANGE_ASK's "fix" would take the
                    # lead meant for what to change, so this ask gets its own.
                    leads = PUT_RIGHT_LEADS
                else:
                    leads = LOST_LEADS if AT_A_LOSS.search(text or "") else _leads_for(text)
                return _handed_back(memory, _a_lead_and_a_step(
                    _a_lead_for(leads, said, memory, text), said))
            # The step has already been handed back once, so this ask is the third time. The
            # composer's pointer at the rest of the answer is the best line when it has one to
            # point at ("Ease off running first. The rest of what I said follows from that"), so
            # the step is offered again rather than the turn stood down from: standing down here
            # left the turns whose answer the composer had no line for with a search hedge, which
            # is worse than the instructions they already have. The arbiter still prefers the
            # composer's line where there is one.
            if step:
                _wording = step[:1].upper() + step[1:]
                return _handed_back(memory, _a_lead_and_a_step(
                    _a_lead_for(_the_lead_for(text, step), _wording, memory, text), _wording))
        if more and not a_more_ask(text):
            # A bare "anything else" with nothing left of the answer to hand over. The paragraph
            # again is not one more thing, so this module stands down and the composer's own line
            # answers it ("That's the lot I have on that one. Tell me which bit isn't landing").
            return None
        if nothing_more:
            # An ask for more with nothing more in this answer is not the answer again: standing
            # down lets the composer's end line say the plain thing, and lets a knowledge entry
            # with a second wording answer the ask itself.
            return None
        short = _short(said)
        if short and not _already_repeated(short, memory):
            leads = SAY_AGAIN_LEADS if _a_bare_ask(text) else _the_lead_for(text, short)
            return _handed_back(memory, _a_lead_and_a_step(
                _a_lead_for(leads, short, memory, text), short))
    return None


def the_next_move(memory, text=""):
    """The step after advice the person says did not work, in the answer's own words, or "".

    A report on the advice is answered by the composer, and its pools say "change one thing
    instead" - advice to change, which the person in front of it has already done. When the answer
    itself ends on who to go to if the advice is not enough ("ask a GP", "call a Gas Safe
    engineer"), that sentence is the next move and it is the one thing left to say. Nothing is
    invented here: it is the answer's own closing sentence, said once (a step already repeated
    gets "" and the composer's own line stands).
    """
    for back, asked, said in _recent_answers(memory):
        if back > 1 and not _about_the_same_thing(asked, said, memory):
            continue
        if NEXT_STEP_EMERGENCY.search(said):
            # Nothing is handed back from an emergency answer, and nothing older is reached past
            # it: the composer's own emergency line is the only next move that is true.
            return ""
        step = _next_step(said)
        if step and not _already_repeated(step, memory):
            step = step[:1].upper() + step[1:]
            return pick(TRIED_LEADS, memory, text or "").format(step=step)
        return ""
    return ""


def agreement_with_the_answer(text, memory):
    """The confirmation of a thing the person has just said back, or "" for every other line.

    "ok so low heat then" is answered by `carried_on`, but a second agreement - "low heat, got
    it", a turn later - is answered before that: the answer it agrees with is now two turns back,
    the lookup reads the named thing as the thing to answer about, and the whole paragraph comes
    out again, which is the answer the person has just agreed with. The answer modules call this
    first, the way they call `asks_for_the_same_work`, so the confirmation is what they get.
    """
    clean = (text or "").strip()
    if (not clean or clean.endswith("?") or QUESTION.match(clean) or ASKS.match(clean)
            or len(clean.split()) > 20):
        return ""
    if ABOUT_THE_BOT.search(clean) or WORDS_WANTED.search(clean):
        return ""
    asked = _content(clean)
    if len(asked) < 2:
        return ""
    for back, question, said in _recent_answers(memory):
        if back > 1 and not _about_the_same_thing(question, said, memory):
            continue
        best, shared = "", 0
        for part in [p.strip() for p in SENTENCE.split(said) if p.strip()]:
            if topics.RED_FLAG.match(part) or ASKING_THEM.search(part):
                continue
            count = len(asked & _content(part))
            if count > shared:
                best, shared = part, count
        if shared < len(asked) or not _says_they_agree(clean):
            continue
        named_thing = _the_thing_they_named(clean, best)
        if named_thing:
            return _agreed(named_thing, memory)
    return ""


def carried_on(text, memory):
    """The reply to a line that picks up a detail of the answer just given, or None.

    "ive been waking up at 4 every night" is answered with the advice - the clock, the light, get
    up after twenty minutes. The next line, "and i honestly cant get back off", names the detail
    they mean and says nothing the answer does not already cover, so the honest reply is the part
    of that answer that speaks to it. What it got was "Thanks for telling me - I'm here if you
    want to dig into any of that", which would fit any message anybody ever sent.

    The rule is narrow on purpose:
    * the line has to name at least two things of its own, and they have to be in one sentence of
      the answer, so a line about something else never comes here;
    * it is a statement, not a question - a question has the modules of its own;
    * only the answer just given counts, or, a turn older, one the chat is still on;
    * a part already handed back once is not handed back again.
    """
    # A reset lead is taken off only when what follows it is a question of its own: "nvm, whats
    # the tax deadline" asks something new, and the old answer must not be searched for it. A
    # detail that refines the old subject ("nvm, i mean the carpet" after a stain) is not a new
    # question, and the answer is what tells the carpet from the stain, so the lead is left on.
    clean = (text or "").strip()
    asked_after = without_a_reset(clean)
    if QUESTION.match(asked_after) or ASKS.match(asked_after):
        clean = asked_after
    if (not clean or clean.endswith("?") or QUESTION.match(clean) or ASKS.match(clean)
            or len(clean.split()) > 20):
        return None
    if ABOUT_THE_BOT.search(clean) or WORDS_WANTED.search(clean):
        return None
    if ASKING_TO_START.search(clean):
        # The line names the stall and asks for the first move: "my daughter has a project about
        # the water cycle" / "she is 8 and keeps putting it off". A sentence of the answer can
        # share the words ("a project is marked on...") without telling them how to begin, and
        # handing that back is the answer they already have. The chat and knowledge readers have
        # a first move for this, so the detail reader stands aside.
        return None
    if ACK_OPENS.match(clean):
        return None  # a thank-you ends the turn: what follows it is a new ask, not this answer
    if limits.names_a_limit(clean):
        # "she cant walk far" is a fact about the person's mum, not a detail of the answer on the
        # screen: the hosting answer says nothing about walking, and handing its first sentence
        # back read the same sentence twice. The composer has a reply for a limit of its own
        # ("She can't walk far - so anything I suggest stays short and flat, with somewhere to
        # sit."), and the limit has to reach it.
        return None
    if not QUESTION_MORE.search(clean) and (_tried(clean) or _the_step_just_given(clean, memory)):
        return _the_untried(clean, memory)
    if isinstance(memory, dict) and (memory.get("understood") or {}).get("routine") \
            and not REJOINDER.search(clean):
        # A routine the person reports names its own subject and says something whole about it:
        # "im trying to lose a stone" / "i walk the dog every day" was handed the diet answer back
        # because a sentence of it happens to say "walk" and "day", and the person's own line went
        # unanswered. The habit tail answers it (bot/memory/ack.py::_plain).
        #
        # A rejoinder is the other case: "i go to bed at the same time every night though" is the
        # person saying the step already given is the one they take, and the answer to it is that
        # step again, so a line that argues with the answer keeps the reader.
        return None
    asked = _content(clean)
    if len(asked) < 2:
        return None
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    # The line that asks which part to do first is the one ask that a pointer back has not
    # already answered: "i keep burning the bottom of my pans" / "what am i doing wrong" (the
    # answer again, under a lead) / "how do i clean it off" wants the first clause of that
    # answer and has never had it, so the pointer guard leaves this ask alone.
    which_part = asks_for_the_move(text)
    if turns and not which_part and REFER_BACK.search(str(turns[-1].get("bot") or "")):
        return None
    for back, question, said in _recent_answers(memory):
        if back > 1 and not _about_the_same_thing(question, said, memory):
            continue
        best, shared = "", 0
        for part in [p.strip() for p in SENTENCE.split(said) if p.strip()]:
            if topics.RED_FLAG.match(part) or ASKING_THEM.search(part):
                continue
            count = len(asked & _content(part))
            if count > shared:
                best, shared = part, count
        if shared < 2:
            # The line names something the answer does not put in words ("and i honestly cant
            # get back off" against "do not check the clock, keep the light off, and if you are
            # properly awake ..."), so there is no sentence to match on. The chat is still on the
            # thing the answer was about, and what a friend does then is say the doing part of it
            # again, which is the sentence with the most telling-them-what-to-do in it.
            best = (_the_advice(said) if back == 1 and _trouble(clean) and not _a_feeling(clean)
                    and not _a_thing_of_its_own(clean, said)
                    and not SOMEONE_ELSES_LIMIT.search(clean) else "")
            if not best:
                continue
        elif shared >= len(asked) and _says_they_agree(clean):
            # Every word of the line is in that one sentence: the person has just said the answer
            # back, as people agree - "ok so low heat then" after "cook them low and slow".
            # Handing the same sentence back is the bot talking to itself: they agreed, they did
            # not ask again. The reply is the confirmation, which is the thing they named and
            # nothing else, so it also cannot be a line that would fit any message.
            named = _the_thing_they_named(clean, best)
            if named:
                return _agreed(named, memory)
        doing = _the_doing(best)
        if len(doing) < 25 or _already_repeated(doing, memory):
            continue
        # No lead in: "do not check the clock, keep the light off, ..." answers the line in its
        # first words, and a stock "that is the bit that counts" in front of it says nothing the
        # person did not already know.
        return _handed_back(memory, doing)
    return None


def _a_list_item(part):
    """The first item of a list the answer gives after a colon, when no item opens on a verb.

    "The things that work: same wake-up time every day, no caffeine after early afternoon, a cool
    dark room" is three things to do and not one of them opens on a verb, so a reader that wants
    the verb first found nothing in it and went on to the next sentence - "ask a GP", which is the
    last resort at the end of the answer, not the first thing to do.
    """
    if ":" not in part:
        return ""
    lead = part.split(":")[0]
    if not LIST_LEAD.search(lead):
        # "Learn four things and the rest follows: pasta with a sauce, an omelette": the list is a
        # set of things the answer names, not the things to do, and its first item is a dish. The
        # sentence that says what to do with them is the one after it.
        return ""
    items = [p.strip(" .:;") for p in _pieces(part)][1:]
    items = [p for p in items if p]
    if len(items) < 2:
        return ""
    first = items[0]
    words = first.split()
    if not 3 <= len(words) <= 8:
        return ""
    if NOT_A_DOING.search(first) or topics.RED_FLAG.match(first) or NOT_A_STEP.match(first):
        return ""
    # An item with a verb of its own is read by the verb path above; one that has a verb but does
    # not open on it is a fact about the thing ("most run classes for complete beginners"), not a
    # thing to do.
    from ..compose.verdict import IMPERATIVES

    verbs = set(IMPERATIVES) | set(MOVE_VERBS)
    if any(word.strip(".,!?;:'\"").lower() in verbs for word in words):
        return ""
    return first


def _pieces(part):
    """The instructions of one sentence, split at its colons and commas.

    Nothing is split inside a bracket: "turn the boiler off at the wall switch (not at the fuse
    board, you want the pump to run on for a minute first)" is one instruction with its reason in
    brackets, and splitting at that comma handed over half of it, bracket still open.
    """
    marks = [f for f in PIECE_END.finditer(part) if not _inside_a_bracket(part, f.start())]
    out, start, listed = [], 0, False
    for index, found in enumerate(marks):
        if found.group().strip() == "," and not listed:
            # A comma only splits an instruction when what follows it is one of its own: the
            # clause has to open on a verb, once the connector in front of it is off ("then lift
            # the burnt layer", "and check what your contract says"). "Pick one wake-up time and
            # keep it every day for two weeks, weekends included" and "Check the labels on
            # chocolate, muesli, pesto and satay, and anything marked may contain nuts" carry on
            # the same instruction - a detail and a last item in a list - and cutting there threw
            # away the very words that make the step work.
            end = marks[index + 1].start() if index + 1 < len(marks) else len(part)
            after = part[found.end():end].strip(" ,;:.")
            after = re.sub(r"^(?:and|then|but|also|so|next|plus)\s+", "", after, flags=re.I)
            if not _opens_on_a_verb(after):
                continue
        if found.group().strip() == ":" and not listed:
            keeps, at = _the_colon_tail_kept(part, marks, index, start, found)
            if keeps is None:
                # The head says what the tail is ("learn four things and the rest follows: pasta
                # with a sauce, an omelette"): a lead-in and the list it leads are not an
                # instruction, and the head on its own says nothing to do.
                start, listed = len(part), True
                continue
            if keeps:
                # The colon does not end the instruction: what follows it is the method it is
                # done by or the reason it is worth doing, and the step is the whole of it.
                if at is None:
                    continue
                out.append(keeps)
                start = at
                listed = True
                continue
        out.append(part[start:found.start()])
        start = found.end()
        listed = listed or found.group().strip() == ":"
    out.append(part[start:])
    return out


def _the_tail_asks_a_question(part, marks, index, found):
    """True when what follows the colon is the questions to put, not a list of things to try."""
    end = marks[index + 1].start() if index + 1 < len(marks) else len(part)
    return bool(A_QUESTION.match(part[found.end():end].strip(" ,;.")))


def _the_colon_tail_kept(part, marks, index, start, found):
    """The instruction with its colon tail, when the tail belongs to it rather than to a list.

    "Open a lifetime ISA and put a monthly standing order into it: that adds 25%", "start with
    run-walk: one minute of easy jogging, two minutes of walking", "pick one wake-up time for two
    weeks, weekends included: the morning light is what sets the clock" - the words before the
    colon are the whole of the instruction and the colon gives its method or its reason, so
    cutting there handed over a headline with the part that makes it work gone ("Split your time
    in three.").

    A colon after a noun phrase still opens a list, and a list is read item by item: "the things
    that work: same wake-up time every day, no caffeine" has no verb in front of its colon, so
    this leaves it alone. Returns (the piece to hand over, where the next piece starts) - the
    piece is "" when the colon splits as before, None when the head only announces a list of
    things, and the offset is None when the whole of the sentence after it belongs to this
    instruction.
    """
    head = part[start:found.start()].strip(" ,;")
    if not _opens_on_a_verb(head):
        return "", None
    if NOT_A_TAIL.search(head) and not _the_tail_asks_a_question(part, marks, index, found):
        # A verb phrase that only announces what the tail is: "learn four things and the rest
        # follows: pasta with a sauce, an omelette" leads a list of things to try, and neither
        # the lead nor its list is a thing to do. Unless the tail is the questions themselves:
        # "ask the ward three things today: who is in charge of their care, what the plan is"
        # names what to ask, and asking it is the step.
        return None, None
    tail = part[found.end():]
    if len((head + ": " + tail).split()) <= STEP_WITH_ITS_METHOD:
        return head + ": " + tail.rstrip(" ,;"), None
    # The tail is longer than a step with its method: the step is the instruction and the first
    # item of the tail, and the rest of the list is what a further ask gets.
    for later in marks[index + 1:]:
        if later.group().strip() not in (",", ";"):
            continue
        first = part[found.end():later.start()].strip(" ,;")
        if not first:
            continue
        piece = head + ": " + first
        if len(piece.split()) <= STEP_WITH_ITS_METHOD:
            return piece, later.end()
        return "", None
    return "", None


def _opens_on_a_verb(text):
    """Whether this clause starts on a verb, which is what makes it an instruction of its own."""
    from ..compose.verdict import IMPERATIVES

    words = text.strip(" .,:;").split()
    if not words:
        return False
    return words[0].lower() in IMPERATIVES or words[0].lower() in MOVE_VERBS


def _the_steps(said):
    """Every instruction in the answer, in the order the answer gives them.

    `_the_first_step` wants the first one; a "what else can i do" wants the first one that is not
    the thing the person has just said did not work, so both read the answer through this.
    """
    from ..compose.verdict import IMPERATIVES

    verbs = frozenset(IMPERATIVES) | frozenset(MOVE_VERBS)
    for part in [p.strip() for p in SENTENCE.split(str(said).strip()) if p.strip()]:
        if topics.RED_FLAG.match(part):
            continue
        # "If you get them most days, keep a short diary of sleep for two weeks": what to do about
        # a pattern, not the first thing to do for the headache the person has this afternoon, so
        # the whole sentence is passed over the way `_a_move` passes it. A condition that is the
        # answer's only instruction still leaves this reader nothing, which is right: the line is
        # then answered by the move reader, which reads the same condition the same way.
        if CONDITION_CLAUSE.match(part):
            continue
        found = []
        for piece in _pieces(part):
            head = piece.strip(" .:;")
            # "Keep walking, and put a hot water bottle on it at night": the second instruction of
            # an answer starts with the connector, and a reader that wants the verb first skipped
            # it whole and found nothing else.
            head = re.sub(r"^(?:and|then|but|also|so|next|plus)\s+", "", head, flags=re.I)
            if not head or topics.RED_FLAG.match(head) or NOT_A_STEP.match(head):
                continue
            if A_MENU.search(head):
                continue
            if DECLARATIVE.match(head):
                continue  # a statement about the thing, not something to do
            # A question is not a step, even the bot's own: "i want to write a book" then "i dont
            # know where to start" was handed "Start with this: Tell me what you last enjoyed and
            # I'll narrow it down." - the answer's own question read back as the thing to do.
            if head.endswith("?") or QUESTIONS_THAT_ARE_NOT_STEPS.match(head):
                continue
            words = head.split()
            # A step that carries its method after a colon is already the whole of it, and the
            # words of the method ("before you change anything: the subscriptions you forgot")
            # read as qualifiers that are not there. `_the_colon_tail_kept` has cut it to size.
            if ":" in head:
                limit, cut_words = STEP_WITH_ITS_METHOD, STEP_WITH_ITS_METHOD
            else:
                limit, cut_words = STEP_WORDS, CUT_WORDS
            if len(words) > cut_words and words[0].lower() not in NEEDS_COMPLEMENT:
                # The verb phrase is the step and the qualifier after it is detail. Without the
                # cut a long instruction was skipped whole and the ask got the paragraph instead.
                # A qualifier that is the second half of a phrasal verb ("carry on with normal
                # activity") is not where the step ends, so the cut waits for the next one, and
                # a cut that would leave too little goes uncut: a sentence handed over whole
                # still reads, a sentence cut mid-phrase does not ("put the immersion and any
                # room heaters").
                cut = None
                for at in _places_to_cut(head):
                    if _inside_a_bracket(head, at):
                        # "turn the boiler off at the wall switch (not at the fuse board...)": the
                        # words in the bracket are the reason for the step, and a cut there hands
                        # over "turn the boiler off at the wall switch (not".
                        continue
                    left = head[:at].strip(" ,;:.").split()
                    if len(left) < SHORT_STEP:
                        continue
                    if left[-1].lower() in DANGLING:
                        # "clear the vents with a can of air and check what is": the cut landed
                        # past the ending of the clause, so this is not where the step ends.
                        continue
                    cut = at
                    break
                if cut:
                    head = head[:cut].strip(" ,;:.")
                    words = head.split()
            if not 3 <= len(words) <= limit:
                # A piece too long to hand over whole still opens on one instruction: "Each week
                # add a minute to the jog and take one off the walk, and in about eight weeks you
                # will run 20 minutes without stopping" promises and instructs in one sentence,
                # and the reader passed the whole thing over - so a "what next" through the
                # running plan skipped the week-on-week bit the plan is made of.
                first_half = _the_first_instruction_in_a_long_piece(head, verbs)
                if first_half is None:
                    continue
                head, words = first_half, first_half.split()
            if words[0].lower() not in verbs \
                    and not _a_verb_after_a_leading_phrase(head, verbs):
                continue
            # "The thing to do first: fix the wake-up time first" says first twice.
            trimmed = re.sub(r"\s+(?:first|next)$", "", head, flags=re.I)
            # ...but "first" is sometimes part of the phrase rather than a word said twice:
            # "keep them apart behind a baby gate at first, feed each one on their own side of it"
            # was handed over as "The first thing to do: Keep them apart behind a baby gate at." -
            # a step that stops mid-phrase and reads as a typo. Only a bare "first" at the end of
            # a step is the repeated word, so the trim is kept only when the step still ends on
            # something a sentence can end on.
            if trimmed.split() and trimmed.split()[-1].lower() not in DANGLING:
                head = trimmed
            found.append(head[0].lower() + head[1:])
        for step in found:
            yield step
        if not found:
            item = _a_list_item(part)
            if item:
                yield item[0].lower() + item[1:]


def _the_next_step(said, memory):
    """One thing out of the answer past the first, which they have not already had or tried.

    "ive tried stretching" then "what else can i do" is a person two things into a list, and the
    next item is the whole reply: handing back the stretch they just told us did nothing, or the
    paragraph they are working through, is not.

    The first instruction is skipped: the whole answer was handed over a turn ago, so "what else"
    asks for what comes after it, and giving the opening sentence back with "there is this one
    too" in front of it is the same thing said again with a new label.
    """
    steps = list(_the_steps(said))
    for step in steps[1:]:
        if topics.RED_FLAG.match(step):
            # A health answer ends with the warning ("See a GP if it is no better in a fortnight"),
            # and handing that over as "one more thing you can do" makes the person's afternoon
            # worse, not better. The same skip `_a_move` makes, for the same reason.
            continue
        if _already_repeated(step, memory) or _they_say_they_tried(step, memory):
            continue
        return step
    return None


def _the_first_step(said):
    """The first thing to do in the answer, read more generously than `_a_move`.

    The move reader above is tuned for a line that asks back at the answer generally, so it only
    takes a verb phrase it recognises and only when the phrase is short. A "where do i start" is
    a narrower ask, and the entries answer it with verbs that list does not have ("track two
    weeks of what leaves the account", "run a hot service wash"), so this one takes those verbs
    and cuts a long instruction at its qualifier: the verb phrase is the step, the rest is detail.
    """
    # Forwards, not backwards as `_a_move` reads it: a "where do i start" wants the first thing
    # to do, and an answer that opens with a fact still gives its steps in order after it.
    for step in _the_steps(said):
        return step
    return None


def _a_new_work(text, asked):
    """True when a how-to question follows a definition of the same thing.

    "what is an apprenticeship" then "how do i get one": the definition answered what the thing
    is, and the person now asks how to get one, which its own entry answers ("apply to them like
    jobs, because that is what they are"). Handed the definition back they got its first fact as
    if it were a step: "Start with this: Pay is at least the apprentice minimum wage"
    (@blue-hedgehog, @sky-tuna, #6152). A line that only asks back at the answer ("how do i use
    it", "how do i do that", "where do i start") names no doing of its own, and "can i save it"
    is answered from the answer by its own reader, so neither comes here.
    """
    line = str(text or "")
    if asks_to_put_it_right(line) or HOW_IT.search(line):
        return False
    if not WHAT_IT_IS.match(str(asked or "")):
        return False
    return bool(_doings(line))


def asks_which_part(text):
    """Whether the line asks which part of the answer to do first, and names no doing of its own.

    "Where do i start", "what should i do first", "where should i begin with this": the whole of
    the line is the ask, so it is answered from the answer in hand and never by a fresh lookup.
    "How do i clean it" is not this: it names a doing ("clean") that may be a question of its own
    and a neighbouring entry answers it well, so the lookup keeps that line and this reader stays
    out of it.
    """
    line = str(text or "")
    if not line.strip() or WORDING.search(line):
        return False
    return bool(asks_for_the_move(line)) and not HOW_IT.search(line)


def _leads_for(text):
    """The lead-ins that answer this ask: the thing to do, or the thing to change."""
    return CHANGE_LEADS if CHANGE_ASK.search(text or "") else MOVE_LEADS


def _a_lead_for(leads, step, memory, text):
    """One lead out of `leads`, and never one that says what the step's first word says.

    Every lead in these pools marks the step as the first thing, which is the whole point of it -
    except when the step opens on its own "Start with": then the reply says start twice, and to
    somebody who asked where to start that reads like a machine that did not hear the question.
    Only the lead can give way, because the step is the answer's own wording and trimming it is
    how a step stops being the answer's. A placeholder is not a word of the lead, so it comes out
    before the lead is read.
    """
    if STEP_SAYS_FIRST.search(str(step or "").strip()):
        leads = tuple(lead for lead in leads
                      if not LEAD_SAYS_FIRST.search(re.sub(r"\{[a-z_]+\}", " ", lead)))
        leads = leads or NOW_LEADS
    return pick(leads, memory, text)


def the_move(text, said, memory):
    """The first step of the answer just given, when the line is asking which part to do.

    "Where do i start" a turn after the answer has already been on the screen is not a request
    for the paragraph again: the knowledge base reaches the same entry and frames it "Same as
    before: <the whole of it>", which tells a person who has just read it nothing. The step is
    already in the answer, so it is handed over in the answer's own words.
    """
    if not isinstance(said, str) or not said.strip():
        return None
    if not asks_for_the_move(text):
        return None
    if WORDING.search(str(text or "")):
        return None
    if re.search(r"\bhow (?:long|much|many|often|far|hot|soon)\b", str(text or ""), re.I):
        return None  # a figure is asked for, not the first step
    step = _the_first_step(said)
    if not step or _already_repeated(step, memory):
        return None
    if not isinstance(memory, dict):
        return None
    if _they_say_they_tried(step, memory):
        # "ive tried a hot wash already" then "what else can i do": the first step of the answer
        # is the thing they just said did not work, and handing it back is the one reply a friend
        # never gives. The tried pools have the next step; this one steps aside for them.
        return None
    _wording = step[:1].upper() + step[1:]
    return _handed_back(memory, _a_lead_and_a_step(
        _a_lead_for(_leads_for(text), _wording, memory, text), _wording))


def _they_say_they_tried(step, memory):
    """True when a line just before this one reports having done this very thing.

    The report does not have to be the bare "i tried that" the tried pools read: "ive tried a hot
    wash already" names the thing it tried, and that is exactly the one the move must not hand
    back.
    """
    mine = {word for word in re.findall(r"[a-z']+", step.lower()) if len(word) > 2}
    if not mine:
        return False
    for turn in (memory.get("turns") or [])[-3:]:
        if not isinstance(turn, dict):
            continue
        line = str(turn.get("user") or "").lower()
        if not ATTEMPT.search(line):
            continue
        said = {word for word in re.findall(r"[a-z']+", line) if len(word) > 2}
        shared = mine & said
        # One long word that is the same word is enough ("ive tried walking" against "keep
        # walking and carry on"): the person named the very thing, and handing it back is the
        # reply that reads as not listening.
        if len(shared) >= 2 or any(len(word) >= 5 for word in shared):
            return True
    return False


def _the_keys_of(said, memory):
    """The words the entry behind an answer was keyed on, or an empty set.

    `memory["entry_answers"]` keeps the keys of every card this chat was given, and a follow-up
    can be about the card without using a word of the card's own sentences: "where do i start"
    after a card on sorting out money says nothing about money, and the card's keys do.
    """
    head = " ".join(str(said or "").split())[:60]
    for record in (memory or {}).get("entry_answers") or ():
        if not isinstance(record, dict):
            continue
        text = " ".join(str(record.get("text") or "").split())
        if text and text[:60] == head:
            return {str(key).lower() for key in (record.get("keys") or ())}
    return set()


def _the_chat_is_still_on(said, memory):
    """True when the card is the one the chat is still on, not just one it passed through.

    Two things make a card the one in hand. Its words (and the words it is keyed on, because a
    card written for the person's own line never says them back - "slugs" becomes "them") touch
    the line just given, or they touch the reply just given, which is how a card stays in hand
    when the bot has been handing parts of it back. A card four turns back that shares a word with
    one of the lines in between is a different thing: the child-sleep card came back for a
    question about putting a shift change in writing, because "my kid is 6" was still in the last
    three lines. The reply just given there was "Say the one thing that matters first", which is
    about nothing in that card, and the line just given was about writing it down.
    """
    words = set(re.findall(r"[a-z']+", str(said or "").lower()))
    words |= {word for word in _the_keys_of(said, memory) if len(word) > 2}
    words = {word for word in words
             if len(word) > 2 and word not in topics.STOPWORDS and word not in NOT_A_SUBJECT}
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    last = turns[-1]
    for side in ("bot", "user"):
        here = {word for word in re.findall(r"[a-z']+", str(last.get(side) or "").lower())
                if len(word) > 2 and word not in topics.STOPWORDS
                and word not in NOT_A_SUBJECT}
        if words & here:
            return True
    return False
