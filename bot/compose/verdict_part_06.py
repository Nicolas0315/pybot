"""Part 6 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re

from . import pick
from .verdict_part_01 import (
    CARE, REASSURE, HOW_MANY_PEOPLE, SAYS_NORMAL, CHECK_JOB_LINES, CHECK_ONCE_LINES,
    CHECK_WATCH_LINES, CHECK_WORKS_LINES, A_DECISION_ASK, A_LENGTH_IN_THE_ANSWER, A_PLAN,
    A_THINKING_ABOUT, _about_a_body, AGE_LINES, ASKS_FINE, ASKS_WRONG, A_CHECK_ASK, A_COMPARISON,
    A_FIGURE, A_FIGURE_ASK, A_HOW_TO_ASK, BARE, BOTH_LINES, CHOICE_OK_LINES, COMPARATIVE,
    CONDITION_LINES, DENIES, DO_LINES, FIGURE_LINES, GRIEF_FLOOR_LINES, HARD_NEWS_LINES, JUST_AGE,
    METHOD_DOUBT, METHOD_OK_LINES, MET_CONDITION_LINES, MET_LINES, MONEY_LINES, MONEY_TROUBLE_LINES,
    NOTHING_WARNED_LINES, NO_LINES, PERSON_CALL, PERSON_ORDINARY, SAID_YES, SYMPATHY, WHEN_ASK,
    WHEN_CALL_LINES, WHEN_LINES, WORRYING_ASK, _A_NUMBER, _a_figure_owed, _the_list_before_the_call,
    BODY_WORD, SOMEONE_ELSE,
)
from .verdict_part_02 import (
    REFER, STOP_DOING, FEELING_DOUBT_LINES, CARE_NORMAL, CARE_NORMAL_UNKNOWABLE, CARE_NOW,
    CARE_NOW_NORMAL, ORDINARY_NORMAL, ENOUGH_ASK, NAMES_A_CLINICIAN, AGAIN, ASKS_NORMAL, ASKS_OK,
    BACKSTOP_LINES, CONDITION_NORMAL, DO_NORMAL, ENOUGH_STATED_LINES, FLOOR_LINES, HELPED,
    HELPED_LINES, NEUTRAL_ASK_LINES, NOTHING_WARNED_NORMAL, NO_STATED_LINES, OK_LINES, PEOPLE_CARE,
    SEE_ANYWAY_LINES, SEE_STATED_LINES, SOON_LINES, TEST_LINES, THING_CALL, THING_ORDINARY,
    THROW_AWAY_LINES, WORRIED_ASK, YES_LINES, YES_SAID_LINES, FEELING_FAMILY,
)
from .verdict_part_03 import (
    _WORD, _flat, _last_person_line, _first, _the_line_behind, _a_punt, _last_module,
    A_CHECK_ON_A_PLAN, A_CHECK_ON_A_PLAN_LINES, OWN_PATTERN, THE_PLAN_CAN_HURT_LINES, URGENT_CALL,
    _a_doubt_about_money, _a_person_they_know, _a_thing_they_own, _a_throw_away, _about_the_person,
    _as_written, _considering, _is_a_comparison, _last_line_that_named_a_call,
    _nothing_to_be_long_about, _own_doing, _said_no, _say, _the_answer_already_warned,
    _the_last_line_was_mine, _the_person_line, _the_plan_can_hurt, _the_plan_they_brought,
    _the_worst_thing_they_said, _they_named_the_sign_themselves,
)
from .verdict_part_04 import (
    _first_positive, _last_reply, TIME_NOW, TRADE, _a_call_for_now, _a_plain_go, _care_for_now,
    _opening, _referral_about_the_thing, _said_enough, _the_call_sentence,
    _the_line_is_the_threshold, _the_person_gave_the_sign, _the_referral_sentence,
)
from .verdict_part_05 import (
    _a_how_to, _says_what_it_is, _round_robin, _a_judgement_fence, _a_mood, _a_plan_doubt,
    _about_a_death, _condition_after_care, _danger, _past_the_timescale, _referral,
    _stated_referral, _the_call_and_its_reason, _the_fence_is_their_own_line, _the_line_it_answered,
    _when, DOING,
)


# The answer above is a recommendation the person asked for ("should i text my ex", "should i go
# to the wedding"), and the doubt on top of it is about that recommendation: "is that ok". Every
# arm below is about what the person has ("i have a cough") or does ("i keep putting off my
# emails"), so a step the bot recommended reached none of them, and the chat pool closed the
# conversation - "Alright then - good luck with it" over the one answer that had given them
# something to do. The step is the answer, so it is given back with the ruling on it.
ADVICE_OK_LINES = (
    "Yes - go with that. {step}",
    "That is the right first move, and it is the one I would take: {step}",
    "Go with it. {step} If it feels wrong once you are in it, say so and we can change tack.",
)


# The line that asked for a recommendation, rather than reporting something to be judged. Read
# from the person's own words: the same answer's step over "i have a cough" is still the floor's
# question, because they did not ask for advice, they said what they had.
ASKED_FOR_A_CALL = re.compile(
    r"^\s*(?:so\s+|ok(?:ay)?\s+)?(?:should|shall|do you think|would you|what would you do|"
    r"is it (?:a good idea|ok|okay|wise|worth it|fine) to|is it wrong to|am i (?:ok|okay|right) to)\b")


def _a_job_to_do(text):
    """True when a run of words holds an instruction the person could go and do.

    Read clause by clause, because an answer often puts the job after the reason for it: "The wait
    is worse than the call nearly every time, and you can keep it short once you are through - say
    the one thing you actually want to say" is advice with its step in the second half, and
    reading only the opening of the sentence would call it a verdict. `_STEP_OPENERS` is the
    vocabulary `_an_instruction_and_nothing_else` already trusts for "this answer tells them what
    to do", so the two readings cannot drift apart.
    """
    for piece in re.split(r"[.!?;:]\s+| \u2014 | \u2013 | - ", _flat(text)):
        words = _WORD.findall(piece.strip(" ,-"))
        if words and words[0] in _STEP_OPENERS:
            return True
    return False


def _the_advice_itself(said):
    """The answer's first real sentence, when the answer holds a job to go and do.

    "Go, and give yourself an exit:" is the opening of a recommendation whose rest is a list, and
    handed back with its colon it reads as a sentence that stops dead. The words are the answer's
    own either way.

    It also has to hold a job: an answer can open on a verdict or on a shrug rather than on
    something to do, and "Yes - go with that. Not unreasonable at all." (over "should i worry") or
    "Yes - go with that. Not mine to decide, sorry." (over "should i ring in sick") tells the
    person to go and do nothing. `_a_job_to_do` is the reading for that, and where no clause of
    the answer opens on a job the arm stands aside and the line it replaced keeps the turn.
    Found by @snappy-net on #7845.
    """
    for sentence in re.split(r"(?<=[.!?]) ", " ".join(str(said or "").split())):
        clean = sentence.strip()
        if clean.endswith(":"):
            clean = clean[:-1].strip()
        if len(clean.split()) >= 4:
            if not _a_job_to_do(clean):
                return ""
            return clean if clean.endswith((".", "!", "?")) else clean + "."
    return ""


# An answer that declines to call it is not advice the person can go and do: "Not one I can call
# for you, sorry: I cannot examine anything from here" is the bot standing back, and handing it
# back as "that is the right first move" tells them to do nothing. Read from the answer's opening.
A_REFUSAL = re.compile(
    r"\b(?:i can(?:no|')?t\b|i cannot\b|beyond what i know|not one i can call|i don't know "
    r"enough|i would not want to guess|that is not something i can|not mine to decide|not mine "
    r"to say|not for me to (?:decide|say|call)|(?:that|this|it) is your call|up to you whether)\b",
    re.I)


def _an_ask_for_a_call(memory):
    """True when the person's own last line asked for a recommendation."""
    said = _flat(_last_person_line(memory)).strip()
    return bool(said) and ASKED_FOR_A_CALL.match(said) is not None


def _a_fix_with_no_warning(said):
    """True for an answer that gives a job to do and says nothing about danger either way."""
    if not said or len(said) < 80:
        return False
    if not _says_what_it_is(said):
        return False
    if _first(said, CARE) is not None or REFER.search(said) is not None:
        return False
    if _first(said, REASSURE) is not None or _first(said, STOP_DOING) is not None:
        return False
    return _a_how_to(said)


# The answer gave an instruction and nothing else: no verdict, no explanation of the thing, no
# referral. "my mate keeps cancelling on me" is answered "Say it once, about the pattern rather
# than the last time: ...", and "is that bad" on top of it came back "Alright then - good luck
# with it." - a goodbye to a fair question. So did "i got a parking ticket", "my landlord wants to
# raise the rent", "my ex keeps texting me" and "my mum keeps telling me what to do". Nothing in
# those answers can be ruled on and the pools above all need an answer that said something about
# the thing, so the doubt gets the one honest sentence there is - the doing in the answer is the
# point, not a verdict - and the question a friend asks. No line claims the thing is fine.
DIRECTED_LINES = (
    "I wouldn't call it a warning sign - the answer above is about getting it sorted, and that "
    "is the part that matters. What has you asking?",
    "Nothing in that says how serious it is. The step above is what moves it, and what would "
    "change the answer is it getting worse or going on. Where is the worry?",
    "Hard to put a scale on it. Doing the thing above is what makes the difference, so start "
    "there and tell me what is behind the question.",
)


# Somebody who owes the person something: a fault a landlord, a council or a boss has been asked
# to fix is not the ordinary job the fault itself is. "my landlord wont fix the damp" / "been 3
# months now" / "is that a problem" was told "On its own, no. Everything in that answer is the
# ordinary job", because the damp card ("find the water before you treat the wall") was read as
# the answer to the question asked; the question was about somebody's duty, and three months of it
# is a tenancy problem, not a damp-repair one. The reassurance is not this composer's to give, so
# it stands aside and says nothing rather than saying the wrong thing warmly.
# Standing aside is right for the verdict and wrong for the turn: the chat pool fills the hole
# with a goodbye ("Alright then - good luck with it."), which is worse than the reassurance it
# replaced. What the person is owed is not a verdict on the damp; it is the one thing that
# changes whose problem it is, which is having it in writing with the date it started.
OWED_LINES = (
    "Then it is theirs to fix rather than yours. Put it in writing, keep a copy, and note the "
    "date it started \u2014 that is the thing that turns it from your complaint into their job.",
    "That one is their job, and the date is what makes it stick. Send it in writing, keep the "
    "reply, and say when it started: anyone who has to step in later asks for that first.",
    "Keep it in writing and keep the dates. A landlord, a council or a boss who has been told in "
    "writing is a different conversation from one who has only been told.",
)


OWED = re.compile(r"\b(?:landlord|landlady|letting agent|estate agent|council|housing "
                  r"association|housing officer|boss|manager|employer|supervisor|neighbour|"
                  r"neighbor|builder|contractor|freeholder|owner|letting|lettings)\b", re.I)


def _somebody_owes_them(memory, back=3):
    """True when one of the last few lines named somebody who owes the person a duty."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for last in turns[-back:]:
        if not isinstance(last, dict):
            continue
        line = last.get("user") or last.get("clean") or last.get("text") or ""
        if isinstance(line, str) and OWED.search(line):
            return True
    return False


def _a_reading_of_the_feeling(memory, flat):
    """The sentence for a doubt about a state the person named themselves, or None.

    Shared by both passes over the doubt: a chat line that named a feeling is answered with the
    reading for that family rather than with a question floor, and the pass after the answer
    finds the same family. The rotation is taken as it comes rather than handed to `pick`: `pick`
    seeds on the sum of the characters, and three of these pairs ("i feel low" / "is that bad",
    "i feel anxious all day" / "am i ok", "ive been feeling flat all week" / "is that weird")
    collided on one sentence. The count of turns is in the seed so the same ask twice in a row
    does not get the same sentence back.
    """
    behind = _the_line_behind(memory)
    family = _a_feeling_of_their_own(behind)
    if not family:
        return None
    seed = behind + " " + flat + " " + str(len(memory.get("turns") or []))
    return _round_robin(FEELING_DOUBT_LINES[family], seed)[0]


def _care_pool(said):
    """Which care pool a normality ask gets, by what the answer already said.

    Three readings of one answer, in the order they can be true: a card that put a time on its
    referral has already answered the doubt ("ring the vet today" is not a thing to wonder about),
    so the reply says to do it. A card that said how many people it happens to has answered
    "is it normal" itself, so the reply must not say it cannot tell. Only a card silent on both
    gets the honest "I could not call that usual or not from here".
    """
    flat = _flat(said)
    if CARE_NOW.search(flat) is not None:
        return CARE_NOW_NORMAL
    if _first_positive(flat, SAYS_NORMAL) is not None:
        # The answer has already said the thing asked about is the usual one: "The steady hum is
        # the compressor ... it is normal, and it gets louder when the room is warm". A care line
        # on top of that ("common or not, that one is worth getting looked at properly") sends a
        # person to an engineer for the ordinary hum, which is the one mistake these pools must
        # not make - it is the same reading as the `no` this pool was written to stop arguing
        # with, only louder (ample-fan, #3872). The answer's own word is the verdict, and the
        # pools that watch for change carry whatever exception its later sentences named.
        return ORDINARY_NORMAL
    if _first_positive(flat, HOW_MANY_PEOPLE) is not None:
        # The card has said how usual it is, so the one line that cannot argue with it is the one
        # that takes the commonness as the card's word: "Yes - common or not, that one is worth
        # getting looked at properly".
        return CARE_NORMAL[:1]
    if _first_positive(flat, REASSURE) is not None:
        # The card said what usually causes it ("usually means a ligament is not holding") and
        # sent them to someone: it has said enough that the honest "I could not call that usual
        # or not from here" would be arguing with it.
        return CARE_NORMAL
    return CARE_NORMAL + CARE_NORMAL_UNKNOWABLE


def _the_knowledge_has_this(clean, memory, above):
    """The knowledge base's own new answer to this line, or None.

    Read the way `safetyask` reads it: on a copy of the memory, so asking changes nothing about
    this turn. A card that cannot be read is no card.

    A card that only says the answer above again is not a new answer either, and asking the
    knowledge base does not tell the two apart: for "will that help" after the back-pain card it
    hands back that card, sometimes with the nod ("Same as before: ...") and sometimes without.
    So the test is the words - the answer above's own opening, said again - and not the nod in
    front of them. The person asking whether the method works has read that paragraph.
    """
    try:
        from .safetyask import _the_answers_have_this
    except Exception:  # noqa: BLE001 - a card that cannot be read is no card
        return None
    card = _the_answers_have_this(clean, memory)
    if not card:
        return None
    said = _flat(card)
    opening = _flat(above)[:60]
    if opening and opening in said:
        return None
    return card


def a_check_on_the_reply(reply):
    """True when a reply is this composer's answer to a check on the answer above, else False.

    Read by the arbiter: a check on the method just given is not answered by saying that method
    again, so the recall band - which repeats the paragraph - gives way to this line. The pools
    are the whole reading, because the same check is asked in many wordings.
    """
    if not reply:
        return False
    text = reply.strip()
    return any(text in {line.strip() for line in pool}
               for pool in (CHECK_WORKS_LINES, CHECK_ONCE_LINES, CHECK_WATCH_LINES,
                            CHECK_JOB_LINES))


def _an_amount_asked(flat):
    """Whether the check is about how much of a thing, which is the one kind a card can answer."""
    return bool(ENOUGH_ASK.match(flat) or re.search(r"\bhow (?:much|many)\b|\bamount\b|"
                                                    r"\benough\b", flat or ""))


def _the_last_thing_said_is_a_nod(memory):
    """Whether the bot's last turn only said the person was heard."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    last = turns[-1]
    return isinstance(last, dict) and _a_punt(last)


def _a_check_on_the_method(flat, memory):
    """"Will that work" / "will that help" / "is that enough" about the answer above, or None.

    Only an answer that is a method is what the check is about: the person is asking whether the
    thing the bot just told them to do does anything. A check on a choice the bot has no view on
    ("we are thinking about a second baby" / "will that work") keeps the line it has today - the
    answer above asked the person a question back, and no pool here can say the question works.
    """
    said = _last_reply(memory, past_the_nod=True)
    if not said or not _a_how_to(said):
        return None
    # A choice the answer put back to the person ("we're thinking about getting a rescue dog" /
    # "would that work") is not a method, whatever verbs the answer happens to use: the dog
    # answer's "get one" is the end of a test, not a step. The bot has no view on the choice, so
    # the check keeps the line it has today.
    behind = _flat(_last_person_line(memory) or "")
    if A_THINKING_ABOUT.search(behind) or A_DECISION_ASK.search(behind):
        return None
    # A plan of the person's own is not a method the bot gave, so a check on it is theirs to
    # weigh: "im going to quit my job" / "will that work" is not a doubt about advice.
    if A_PLAN.search(behind):
        return None
    # And the answer has to be the knowledge base's own method. "budget is about 30 quid" is
    # answered by the store's echo of it, and "do you think that is enough" over that echo wants
    # the sum done, not "that is the standard way": a check on an echo is a question this file
    # cannot see the subject of, so it keeps the line it has.
    if _last_module(memory) != "answers":
        return None
    if _the_last_thing_said_is_a_nod(memory):
        # A nod in between ("Got it - you're paying 60 a month") means the answer above is not the
        # last thing said, and the line the person is checking is whatever the bot is about to say
        # about their own figure, which this file cannot see: "i owe about 4000 on my credit card"
        # / "im paying 60 a month" / "is that enough" has the money line to come, and a check on
        # the card above the nod took it away.
        return None
    # A check the knowledge base answers itself is not a check on the method above: "he will eat
    # them raw though" / "is that enough" has the five-a-day card, and that card is a better
    # answer than anything this file can say about the answer before it (qptf-02 on the deck).
    # Read before the pools, and after the echo test, so a card that only repeats the answer
    # above leaves the turn here.
    if _an_amount_asked(flat) and _the_knowledge_has_this(flat, memory, said):
        # Only an amount check can be answered by a card. "is that enough" has the five-a-day card
        # behind it, and that card is the answer; "would that be worth it" over the descaling card
        # has a kettle-buying card behind it, which is about something else, so the check keeps
        # the turn.
        return None
    # A remedy pool only reads as an answer when there is a body in the question: "most people do
    # well on it" and "if it is no better in a week or two" say nothing about a price, a form, a
    # wait or a quote, and those three lines are what a check on a job used to get (snappy-net,
    # #8488). The line the person typed counts as well as the answer, because the answer to "my
    # back hurts" speaks about the habit and the line names the back.
    if not _about_a_body(behind):
        pool = CHECK_JOB_LINES
    else:
        warns = (REFER.search(said) is not None or NAMES_A_CLINICIAN.search(said) is not None
                 or _first(said.split(), STOP_DOING) is not None)
        if warns:
            pool = CHECK_WATCH_LINES
        elif A_LENGTH_IN_THE_ANSWER.search(_flat(said)):
            pool = CHECK_WORKS_LINES
        else:
            pool = CHECK_ONCE_LINES
    return pick(_round_robin(pool, flat + " " + said), memory, said)


# The doubts that are about the thing itself rather than about what to do next. A ruling is only
# said again for one of these: "my pan caught fire" / "what now" is the next thing to do, not a
# doubt about the pan, and answering it with "the answer above still stands: it stays off" takes
# the one reply that mattered - "Stay out and ring 999" - off a fire that is still burning.
A_DOUBT_ABOUT_THE_THING = re.compile(
    r"\b(?:safe|safely|unsafe|dangerous|danger|ok|okay|fine|risky|risk|bad|wrong|worried|"
    r"worry|worrying|problem|normal|harm|harmful)\b"
    r"|\b(?:can|could|may|should) i (?:still |even )?(?:use|keep using|leave|carry on using)\b")


def reply_for(clean, memory):
    """The answer to a bare "is that bad / what should i do / should i see someone"."""
    flat = _flat(clean).strip(" .!?")
    # A check on the person's own plan, read before anything else: it is their plan, so there is
    # no verdict here to give, and the pools below would give one anyway - on a dog and a working
    # day, "is that fair" was answered "Sounds good." and, once the words were added to the bare
    # doubts, "Nothing in that sounded like a warning sign". The plan can be one line further
    # back than the line being checked (`_the_plan_they_brought`), which is the ordinary shape of
    # a plan being talked through, and only a line that says nothing else is read here: a check
    # with a subject of its own ("is that fair on my mum") is a question about that.
    # The answer above ruled the thing unsafe - it said to unplug it, switch it off at the wall,
    # stop using it, or call 999. A bare doubt after that is about the ruling, and the verdict
    # pools below cannot give it: "the plug on the kettle is scorched" is answered "Unplug it if
    # you can do it without touching anything hot...", and "is it safe" came back "Ordinary on its
    # own, yes. It stops being ordinary if there are flames or smoke in the room" - an all-clear
    # for a scorched plug, in the same breath as the answer that said not to touch it. The
    # ruling is read from the same place the safety reading reads it, so the two cannot disagree
    # about whether the bot has already said stop.
    from . import safetyask

    if (safetyask.the_bot_already_ruled(memory) and A_DOUBT_ABOUT_THE_THING.search(flat)
            and not any(word in flat for word in safetyask.A_RULING_ALREADY)):
        # A line that names the stopping itself ("should i unplug it") asks about that step, and
        # the card that names the thing answers it better than the ruling said again. The line
        # here is the bare doubt about the thing - "is it safe", "is that dangerous".
        return pick(safetyask.A_SAFETY_ALREADY_RULED, memory, flat)
    if A_CHECK_ON_A_PLAN.match(flat):
        plan = _the_plan_they_brought(memory)
        if plan:
            # The ask is which part is being weighed, and nothing is ruled on: `_a_plan_doubt`
            # answers the same line with "that is yours to decide rather than something to worry
            # about", which is right for a dog or a wedding and wrong for "i want to lie on my cv"
            # / "does that sound sensible" - there the bot would be blessing a lie by calling it
            # the person's to weigh. Asking what the doubt is works for both.
            return pick(_round_robin(A_CHECK_ON_A_PLAN_LINES, plan), memory, plan)
    # A doubt about the step just given, read before the bare doubts are read: "will that work"
    # is about the method in the answer above, and that method is the bot's own, so the honest
    # reply is the one a method gets - it is the way the bot would do it. An answer that sends
    # them to a clinician, or names a danger, stands aside: there the doubt is about the warning.
    if METHOD_DOUBT.match(flat):
        behind = _last_reply(memory, past_the_nod=True)
        # A plan or a choice in the line before is the person's own, so a doubt on it is theirs
        # to weigh: "im going to quit my job" then "will that work" is not a doubt about a method
        # the bot gave, and the method pool would be agreeing with a decision that is not ours.
        line = _the_line_behind(memory)
        written, spoken = _as_written(line)
        # The same gate "is that ok" after a how-to goes through: the ask has to be a how-to, and
        # the answer has to give the doing. A doubt on a suggestion ("what shall i get my mum")
        # or on a plan ("im going to quit my job") is the person's own to weigh, and a doubt on
        # a thing that got damaged ("my laptop got soaked in the rain") is about the thing.
        if (not behind or not _a_how_to(behind)
                or not (A_HOW_TO_ASK.search(line) or A_HOW_TO_ASK.search(written)
                        or A_HOW_TO_ASK.search(spoken))):
            # The other way round: the answer above is a method the knowledge base gave, and the
            # person is asking whether it does anything ("my back hurts" / "will that help").
            # Returning None handed it to the acknowledgement floor, which closed the
            # conversation with "Alright then - good luck with it."
            return _a_check_on_the_method(flat, memory)
        if _danger(behind) is not None:
            return None
        if REFER.search(behind) is not None or NAMES_A_CLINICIAN.search(behind) is not None:
            # The answer above sends them to a clinician ("see a GP if they keep coming back"),
            # and the doubt is about the warning rather than about the doing of it, so the method
            # pool ("that is the method I would use") must not answer it - that is the bug the
            # guard stands for. The check pool is a different reading, though: it exists to say
            # what to watch for, and a how-to with "see a GP" in it is exactly the answer a check
            # on a method was written for. So the check is read here, and only a check that reads
            # nothing (not a how-to, not the answers module's own method) stands aside as before.
            return _a_check_on_the_method(flat, memory)
        # A check on the effect ("will that help") is not the question the method pool was
        # written for ("is that ok"): "Done that way, it needs no one else: that is the method I
        # would use" says the method is the right one and never says whether it does anything,
        # which is what was asked. The check pool answers that, and picks its line by whether
        # the answer above named anything to watch for.
        checked = _a_check_on_the_method(flat, memory)
        if checked:
            return checked
        return pick(_round_robin(METHOD_OK_LINES, behind), memory, behind)
    # Whether a price is a lot, read before the bare doubts: the ask is about the figure in the
    # person's own line, and it is the one doubt that must not fall through to the body readings
    # (a figure is not a condition) or to the chat floor ("Sounds good." to a price question).
    if A_FIGURE_ASK.match(flat):
        figure_line = _the_line_behind(memory)
        figure_said = _last_reply(memory, past_the_nod=True)
        if figure_line and _a_figure_owed(figure_line) and figure_said:
            # Only a word that makes a comparison ("usual", "typical", "the going rate") is the
            # answer's own usual figure. A yearly total is a figure too, and handing that back as
            # "the answer above gives the usual one" would be the bot making one up.
            if _first(figure_said, A_COMPARISON) is not None:
                return pick(MONEY_LINES, memory, figure_said)
            if A_FIGURE.search(figure_said):
                return pick(FIGURE_LINES, memory, figure_said)
        return None
    # "is that enough" is not one of the doubts below - it asks about an amount, not about how bad
    # something is - so it matched nothing here and the acknowledgement floor took it. After "Three
    # half-hour sessions a week is enough to feel different in a month" the answer had already
    # said so, and the person asking was checking the amount: `is that enough` was answered
    # "Alright then - good luck with it." The ask is read on its own, and the answer's own
    # quantity sentence is what it is answered with.
    enough_ask = bool(ENOUGH_ASK.match(flat))
    if not BARE.match(flat) and not enough_ask:
        # A check on the method just given ("will that work") said in words the pattern above does
        # not hold ("do you think that is enough", "would that sort it") is still not a doubt
        # about the thing, and every pool below answers what is wrong with the thing. Read here
        # and go no further.
        if A_CHECK_ASK.search(flat):
            return _a_check_on_the_method(flat, memory)
        return None
    normal_ask = bool(ASKS_NORMAL.search(flat))
    ok_ask = not normal_ask and bool(ASKS_OK.search(flat))
    said = _last_reply(memory, past_the_nod=True)
    # A check on a plan that can hurt is the one doubt this file does have something to say
    # about: the plan is still theirs, but the answer cannot be "yes, it is fine". Read before
    # any of the pools below, because several of them read a plan as a thing to be weighed and
    # say so.
    plan = _the_line_behind(memory)
    family = _the_plan_can_hurt(_flat(plan))
    if family:
        warned = _the_answer_already_warned(_flat(said))
        if warned:
            return "Go with the answer above rather than around it: " + warned
        return pick(_round_robin(THE_PLAN_CAN_HURT_LINES[family], _flat(plan)), memory,
                    _flat(plan))
    # A death is not a subject this file can rule on, and the pools below would ask after it like
    # a symptom. Standing aside is not enough either: the chat pool fills the hole with "Alright
    # then - good luck with it", so the floor stays with the person instead.
    # Only over a readable line: a safety, urgent, loss or grief reply keeps its own path, and
    # `_last_module` answers "" for those.
    if _about_a_death(memory) and _last_module(memory):
        return pick(_round_robin(GRIEF_FLOOR_LINES, _the_line_it_answered(said, memory) or flat),
                    memory, flat)
    if enough_ask:
        # Read before every pool below: they all judge how bad a thing is, and an amount is not a
        # fault. Nothing to hand back means standing aside, so a "is that enough" over an answer
        # that never gave an amount keeps whatever it had.
        stated = _said_enough(said)
        if stated is None:
            # Nothing in the answer to hand back as an amount, so this is a check on the method
            # like the others: "my back hurts" / "is that enough" has the back-pain card and no
            # amount in it, and standing aside here left the acknowledgement floor to close the
            # conversation ("Alright then - good luck with it").
            # Only when the answer above is the last thing said: "i owe about 4000 on my credit
            # card" / "im paying 60 a month" / "is that enough" has the store's nod in between
            # ("Got it - you're paying 60 a month"), and the line to read is the money one the
            # greeting module is about to give, not the card above the nod.
            if _last_module(memory) == "answers":
                checked = _a_check_on_the_method(flat, memory)
                if checked:
                    return checked
            return None
        return pick(_round_robin(ENOUGH_STATED_LINES, said + " " + flat), memory,
                    said).replace("{yes}", stated)
    # A plan, a choice or a wish the person brought is theirs, and a bare doubt about it is them
    # checking that wanting it is allowed: "im going to rome" / "is that ok" was answered "Alright
    # A stand-down is not a hand-over: the answer in front is the person's own plan being
    # got, so there is nothing here to rule on and nothing below will claim it either -
    # returning nothing left the turn to the sign-off pool ("Alright then - good luck
    # with it"), which ends a conversation the person is still in.
    # A going named in the person's own line is the same shape: "we are going to skegness in
    # june" / "is that ok". The store has no card for a town, so the line comes back as an echo
    # and nothing above it is an answer to read the doubt against - the plan is still theirs and
    # the ask is still about it.
    if _considering(memory) or A_PLAN.search(_flat(_the_line_behind(memory))):
        return _a_plan_doubt(memory)
    # The worst thing said, read beside the answer above: a death or a diagnosis is not a fault,
    # so a doubt on top of one is about the person rather than about the answer, and it is read
    # the same whichever module answered it. "my dad has cancer" / "is that bad" got the
    # acknowledgement floor's "Alright then - good luck with it."
    #
    # Both halves are needed. The news is the person's own line, and the answer above has to be
    # an answer that heard it: "my phone keeps dying" and "my basil keeps dying" are how-to
    # answers, and neither of them says sorry, so the doubt about them is not a bereavement.
    worst = _the_worst_thing_they_said(memory)
    if worst and SYMPATHY.search(_flat(said)):
        # Seeded on what they brought: "is that bad" is the same seven words every time, so a
        # father's cancer, a husband's terminal cancer and a miscarriage all got one sentence.
        seed = worst + " " + flat + " " + str(len(memory.get("turns") or []))
        return _round_robin(HARD_NEWS_LINES, seed)[0]
    # A doubt over money is answered about money, and read before the answer above is read for a
    # symptom. "i cant afford to heat the house" / "is that bad" was told "That one is the ordinary
    # kind, so no. Watch it rather than worry about it: if it's still the same in a week or two ..."
    # - the sentence a cough gets, over a month that does not add up. The rent, a card, a fine and
    # a bill were all told that their thing was "to watch", which is the one thing money is not.
    # A safety answer, a death and a diagnosis all keep their own paths above this.
    money = _a_doubt_about_money(memory)
    if money and _last_module(memory, past_the_nod=True) in ("answers", "chat", "greeting",
                                                             "trouble"):
        # A figure the person gave, against the usual one the answer gave, is the comparison
        # below rather than this pool: "i owe 300 on my gas bill" / "is that bad" wants its own
        # number put beside the usual one, and the pool that names the date is for the trouble
        # that has no figure in it at all. The figure has to be a number: "the rent is late and i
        # am scared" names no amount either, and it was told "That is a figure to compare" too.
        # A digit of any shape counts, because "i owe 300 on my gas bill" is a figure with no
        # currency sign and no period beside it, which `A_FIGURE` does not catch.
        if (not _about_a_death(memory) and not _the_worst_thing_they_said(memory)
                and not (_A_NUMBER.search(money) and _is_a_comparison(said))):
            return pick(_round_robin(MONEY_TROUBLE_LINES, said or money), memory, said or money)
    # A mood or a money worry is not a body and not a fault: "i feel low" then "is that bad"
    # was told its mood was "the ordinary kind, so no", because a warm chat line was read as if
    # it were a symptom answer. The doubt path reads the knowledge base only.
    if not said or _last_module(memory, past_the_nod=True) != "answers":
        # A state the person named themselves is answered by the reading for that family, and
        # only after a chat or floor answer: after a safety answer the crisis reply is the one
        # that stands, and a body in the line is a symptom.
        reading = _a_reading_of_the_feeling(memory, flat)
        if reading:
            return reading
        # A safety answer is not read back for a step ("do the first thing I said" after "ring
        # 999" is the wrong sentence), but the verdict question about it is a different ask and
        # it has one answer: yes. Only when the answer named somebody to ring - a line that named
        # nobody has no call to point back at.
        # "i tried that and it helped" / "is that bad" is the report of a thing working, and the
        # floor read it as a symptom ("That is worth a proper look rather than a shrug").
        if HELPED.search(_flat(_last_person_line(memory))):
            return pick(_round_robin(HELPED_LINES, _flat(_last_person_line(memory))), memory,
                        _flat(_last_person_line(memory)))
        named = _last_line_that_named_a_call(memory)
        if named:
            if _a_call_for_now(named):
                # How urgent the call is, from the line's own words. A dentist, an optician or a
                # physio is somebody to see, not somebody to ring tonight, and the pools say so.
                # How urgent, from the sentence that carries the call rather than from the whole
                # answer. "a bent limb, bone through the skin or numb fingers is 999, otherwise
                # get it checked at A&E or a minor injuries unit today" is a call for today with
                # a fence around the 999; a burn answer that opens "twenty minutes under cool
                # running water ... starting straight away" is urgent about the water and names
                # nobody. Reading the whole answer for an urgent word put both of those in the
                # same pool as "ring 999 straight away".
                call = _the_call_sentence(named)
                seed = flat + " " + call
                if call and URGENT_CALL.search(call):
                    # Rotated on the answer, because "is that bad" is the same seven words every
                    # time and `pick` seeds on the sum of the characters: four different calls
                    # for today landed on one sentence word for word.
                    return pick(_round_robin(YES_SAID_LINES, call), memory, seed)
                if TRADE.search(named) is None:
                    # No time and nobody named: "a burn that blisters or is on the face, hands or
                    # joints should be seen" is a yes, and the pool that says the answer named who
                    # cannot be used over it.
                    return pick(YES_LINES[:2], memory, flat)
                return pick(SOON_LINES, memory, flat)
            # A call the line itself fenced is the condition to watch, not an order for today:
            # "see someone if it's not shifting in a few days" over "i feel dizzy" / "is that
            # bad" was "ringing is not an overreaction here, it is the whole point of it". The
            # answer already named the line to act on, so the verdict is the answer's own.
            when = _when(named)
            if when:
                return pick(CONDITION_LINES, memory, flat).replace("{when}", when)
        # "should i be worried" is the health hedge's ask, not a verdict about the bot's last
        # line: on the deck `i get out of breath singing` / `Got it. Is there anything you'd like
        # a hand with?` / `should i be worried` has the hedge's "a GP, a pharmacist or 111 will
        # tell you" on main, and the floor took that turn away from it.
        if WORRIED_ASK.match(flat):
            return None
        # A chat line, not an answer: there is nothing to read a verdict out of, and "good luck
        # with it" is what the person used to get. Two cases, because a floor may ask but it may
        # not rule: a warm line that said nothing ("I'm listening - say more if it helps") gets
        # the question and no verdict - "i have blood in my poo" was told "I wouldn't call it bad"
        # over exactly that line - while a line that already gave the practical thing ("Rest, warm
        # drinks and an early night") is an answer in substance, and the ruling rests on it.
        if _last_module(memory) in ("chat", "greeting", "trouble"):
            # A state the person named themselves is not a chat-line floor: the reading for
            # that family answers it, and every arm here would take the turn away from it
            # ("i feel really low" / "am i ok" got the question floor's "What would you like to
            # do about it, and how long has it been like that?" over the flat-stretch reading,
            # because the chat line happened to mention a walk).
            reading = _a_reading_of_the_feeling(memory, flat)
            if reading:
                return reading
            if _own_doing(memory) and _a_mood(memory):
                return pick(_round_robin(BACKSTOP_LINES, said), memory, said)
            # The step the bot recommended, doubted. Read first, because every arm below is about
            # what the person has or does and a recommendation is neither.
            step = _the_advice_itself(said)
            if step and _an_ask_for_a_call(memory) and not A_REFUSAL.search(said):
                return pick(_round_robin(ADVICE_OK_LINES, said), memory, said).replace(
                    "{step}", step)
            if _own_doing(memory) and _a_fix_with_no_warning(said):
                return pick(_round_robin(NOTHING_WARNED_LINES, said), memory, said)
            # The question floor claims nothing, so unlike the ruling pools it does not need the
            # line to be about something the person does. What they have is a fair thing to ask
            # about: "i have a cough" / "is that bad" was answered "Alright then - good luck with
            # it" over "Take it easy today - honey and lemon, and don't push through it", and
            # "i have blood in my poo" got the same shrug. What they have can also be cheerful,
            # so that floor asks without calling anything serious.
            # ...and a floor that asks how long it has been going on is for a condition, not for
            # news that went well: "i got the job" is not a thing that has been going on.
            if _own_doing(memory) and not _nothing_to_be_long_about(memory):
                return pick(_round_robin(FLOOR_LINES, said), memory, said)
            if _about_the_person(memory) and not _nothing_to_be_long_about(memory):
                return pick(_round_robin(NEUTRAL_ASK_LINES, said), memory, said)
            # A floor that turned the question back on the person - "That would get to me too. Do
            # you want to work out what to say to them, or is it more a case of letting off
            # steam?" - is a friend mid-conversation, and the doubt that comes back on top of it
            # was answered "Alright then - good luck with it." There is still nothing here to
            # rule on, so the reply says that plainly and asks for the half that decides it,
            # rather than saying goodbye to a worry.
            if _the_floor_asked_them_something(memory):
                return pick(_round_robin(ASKED_THEM_LINES, said + " " + flat), memory,
                            said + " " + flat)
        # #8025's reading, one line down: a doubt after a reply that only gave an instruction.
        return _a_plan_doubt(memory)
    # "when should i worry" asks for the condition, so the answer is the card's own condition and
    # not a yes/no verdict on the thing: over "my mum keeps forgetting things" the pools below
    # said "Yes, that one wants a proper look rather than watching it", which answers a question
    # nobody asked. Only with a readable condition in hand; otherwise the ask keeps the reading
    # it has always had.
    if WHEN_ASK.match(flat) or WORRYING_ASK.match(flat):
        when = (_when(said) or _the_list_before_the_call(said)
                or _stated_referral(said)[0])
        if when:
            return pick(WHEN_LINES, memory, flat).replace("{when}", when)
        # The answer wrote its call first and its reason after the "for", which is not a fence
        # any reader above looks for: over a cut and a cough that left the person with the search
        # hedge or a flat "yes, that one wants a proper look".
        call = _the_call_and_its_reason(said)
        if call and _they_named_the_sign_themselves(call, memory):
            # They are already at the sign, so quoting it back with "before that" is worse than
            # the reading below, which is what these lines got before this change.
            call = ""
        if call:
            return pick(WHEN_CALL_LINES, memory, flat).replace("{when}", call)
        if WORRYING_ASK.match(flat):
            return None
    # The line before was this composer's own verdict, so the person asking again gets the same
    # answer said plainly rather than a new verdict. It used to fall through to the "a fix with no
    # warning" reading, which saw the advice-in-its-own-words in "watch for that" and answered it
    # afresh.
    # It has to be this composer's line before the words are worth reading: `{Step} first.` is one
    # of the templates, and any answer that ends in that word fits it, so a card that says
    # "chemical drain cleaner is the last resort, not the first" was taken for a verdict of mine
    # and the reply to "is that serious" was "Still no." - a no the bot never said. The module is
    # the fence, and the text only decides which of my lines it was.
    if _the_last_line_was_mine(memory) and OWN_PATTERN.search(_flat(said)):
        return pick(AGAIN, memory, flat)
    if any(line.lower() in _flat(said) for line in
           NO_LINES + DO_LINES + YES_LINES + ORDINARY_NORMAL + CARE_NORMAL
           + CARE_NORMAL_UNKNOWABLE + CARE_NOW_NORMAL + DO_NORMAL):
        return pick(AGAIN, memory, flat)
    if _first(said, AGAIN) is not None:
        return None
    # A person's week is not a body (see A_PERSON_THEY_KNOW). Read before the pools below, which
    # would offer somebody's mother a doctor's look for her week.
    if _a_person_they_know(memory, said):
        if _when(said) or REFER.search(said) is not None:
            return pick(PERSON_CALL, memory, flat + " " + _the_line_behind(memory))
        return pick(PERSON_ORDINARY, memory, flat + " " + _the_line_behind(memory))
    opening = _opening(said)
    # What the answer above was about decides which words a verdict may use: a machine gets the
    # job and the trade, and only a body gets a week of watching and a proper look (see
    # A_THING_THEY_OWN). The yes-pool for a call is the same reading in the thing's words.
    thing = _a_thing_they_own(memory)
    yes_pool = THING_CALL if thing else YES_LINES
    # An answer that opens by telling them to get rid of the thing has already said how bad it
    # is, and a bare doubt on top of it is the person asking to be talked round. Read before the
    # care words: "bin it" and "isn't safe to eat" are not a job with a fix, and the pools below
    # would hand back a DIY reading of them.
    action, tested = _a_throw_away(opening)
    if action is not None:
        # Seeded on the answer: "is that bad" is the same seven words every time, so the
        # bare ask gives the chicken, the rice and the milk one identical sentence.
        # A test the person has already run is not the answer: "my milk has gone sour" said the
        # sign the rule names, so it wants the action, while "how do i know if the milk is off"
        # is the row that wants the test back.
        pool = TEST_LINES if tested and not _the_person_gave_the_sign(memory, clean) else THROW_AWAY_LINES
        # Seeded on the answer, so "is that bad" - the same seven words every time - does not
        # give the chicken, the rice and the milk one identical sentence; the person's own line
        # keeps the two chats that share one knowledge answer from matching word for word.
        return pick(pool, memory, opening + " " + _the_person_line(memory, clean)).replace("{Action}", action)
    # An answer can give the verdict in its own words and nothing else: "There is no safe number of
    # drinks before driving" is a no, and there is no referral, job, danger word or ordinary word in
    # it for the readings below to find. So "im gonna drive home after a few pints" / "is that ok"
    # fell through every arm and the acknowledgement floor took the turn with "Alright then - good
    # luck with it." over a straight no. Read before the care words, because an answer can hold a no
    # and a referral together and the no is what the person asked about.
    no_stated = _said_no(said)
    if no_stated is not None:
        return pick(_round_robin(NO_STATED_LINES, said + " " + flat), memory,
                    said).replace("{no}", no_stated)
    care = _referral(said)
    ordinary = _first_positive(opening, REASSURE)
    # A long answer puts its referral in its last sentence: the knee answer spends its opening on
    # what a giving-way knee "usually" means and ends "Ring your GP or a physio this week", and
    # reading the opening alone answered "is that bad" with "that one is the ordinary kind, so
    # no". A referral with no "if" in front of it is the answer's own judgement wherever it sits.
    anywhere = care
    # An answer that tells the person to stop doing the thing is not the answer this composer may
    # call ordinary: "grinding means the pads are down to metal: stop driving" must not come back
    # as "that one is the ordinary kind, so no", however much "usually" a later sentence about
    # the price carries. The stop is read from anywhere in the answer, so the order of the two
    # sentences cannot decide it.
    if _first(opening, STOP_DOING) is not None:
        return pick(_care_pool(said) if normal_ask else (THING_CALL if thing else YES_LINES[:2]),
                    memory, flat)
    # A condition the answer wrote out is the answer's warning for later, not its verdict now,
    # so a harm word inside that condition is not a reason to answer "yes, get it seen to":
    # "Shaking that has crept on over months, is much worse on one side ... is worth a GP
    # appointment" is handed back as that condition, not as a bare yes. The condition is read
    # first and the danger step stands aside for it; an answer with no condition in it keeps the
    # reading it has always had.
    when = _when(said)
    if when == "" and _danger(said) is not None:
        return pick(_care_pool(said) if normal_ask else (THING_CALL if thing else YES_LINES[:2]),
                    memory, flat)
    # The line that was answered decides what "is that ok" is about, and a method, a choice or a
    # plan is not the thing that is wrong. Read as a fault, "how do i cook rice" then "is that
    # ok" was told "Everything in that answer is the ordinary job", and "im going to rome" then
    # "is that ok" was told the same. A method has an answer this composer knows - it is the
    # bot's own, in the answer above - and a choice or a plan has none of this composer's to
    # give, so those go back to the warm acknowledgement.
    # People type the way they type. "wat shud i cook 2nite" is "what should i cook tonight", and a
    # reader that matches on the words as typed reads a question about a choice as no question at
    # all - the `A_PLAN` / `A_DECISION_ASK` arm never fires, and "is it ok?" was answered "That
    # answer is the fix rather than a verdict on how bad it is", which reads the previous answer as
    # a problem already handled. `_as_written` puts each word right in place, in the same order and
    # with the same punctuation, so the ask is still the person's own sentence.
    line = _the_line_behind(memory)
    written, spoken = _as_written(line)
    # Only an answer with nothing to watch in it is the bot's own method. "How do i know if my
    # ankle is broken" is a how-to, and its answer is a check with a red flag in it ("if you
    # cannot [walk on it], or it is crooked, go to a minor injuries unit or a&e today"), so
    # "is that bad" is a question about the red flag and not about the method: told "nothing in
    # it to worry about" it read as an all-clear over an answer that names a&e. So an answer that
    # sends them somewhere to have the thing looked at, or tells them to stop doing it, is read
    # by the verdict below instead, exactly as it was before this branch existed.
    warns = (REFER.search(said) is not None or NAMES_A_CLINICIAN.search(said) is not None
             or _first(opening, STOP_DOING) is not None)
    # The method came from the bot rather than from a how-to they asked: they stated a fact
    # ("i only have one oven", "my oven is fan only") and the answer above came back as the
    # method with the yes already on the front of it. A bare "is that ok" there is the person
    # checking the method, so it gets the same reading as the how-to above.
    if SAID_YES.search(_flat(said)) and _a_how_to(said) and not warns:
        return pick(_round_robin(METHOD_OK_LINES, said), memory, said)
    if ((A_HOW_TO_ASK.search(line) or A_HOW_TO_ASK.search(written)
         or A_HOW_TO_ASK.search(spoken))
            and _a_how_to(said) and not warns):
        # Seeded on the answer for the same reason the nothing-warned pool is: "is that ok" is
        # the same three words every time, so seeding on it gave the rice, the stain and the
        # radiator one identical sentence.
        return pick(_round_robin(METHOD_OK_LINES, said), memory, said)
    if A_PLAN.search(line) or A_PLAN.search(written) or A_PLAN.search(spoken):
        # The plan is theirs, so there is no verdict to give - but a sign-off is worse than
        # a question. Two of the four plans the deck holds reached the choice branch below
        # and were told their choice was a good call, which is the same overreach from the
        # other side; this arm is only the plan that has nothing below it.
        return _a_plan_doubt(memory)
    if (A_DECISION_ASK.search(line) or A_DECISION_ASK.search(written)
            or A_DECISION_ASK.search(spoken)):
        # The ask decides which way this goes. "is that ok?" after a choice asks whether the choice
        # is fine, and the answer's own suggestion makes that the composer's to give. "is that
        # bad?" asks about the thing chosen instead, and this composer has nothing to rule on for
        # it, so it stands aside as it always has.
        if ASKS_FINE.search(flat) and not ASKS_WRONG.search(flat):
            # A choice the answer made for them is the answer's own, so the honest verdict on it
            # is that it is a good call - returning nothing here left the turn to the sign-off
            # floor. Seeded on the line that was answered as well as the ask, so three different
            # choices do not all get one sentence.
            return pick(_round_robin(CHOICE_OK_LINES, line + " " + said), memory,
                        line + " " + said)
        # "should i" is also how a person asks about one thing rather than a choice: "should i get
        # my mole checked" / "is that bad" was read as a choice, and the choice arm has nothing
        # to rule on, so the doubt was handed back "Alright then — good luck with it" - over an
        # answer that had said "Get it checked by a GP within two weeks".
        #
        # Only an answer whose first sentence sends them to somebody has ruled on this for the
        # choice arm to stand aside for: there the referral is the whole answer, so the doubt
        # about it is answered by the referral itself ("Get it checked by a GP within two weeks",
        # "Ring 111 or your GP today", "Your health visitor or the 111 line will talk it
        # through"). An answer that opens with a fix and names a call later has fenced it ("most
        # coughs settle in two to three weeks ... a reason to ring the surgery"), and its own
        # condition is the verdict - the choice arm keeps standing aside rather than turning that
        # fence into "yes, get it seen to" for a chesty cough.
        opening = _opening(said)
        first_said = re.split(r"(?<=[.!?]) ", str(said or "").strip())[0]
        if (not warns or (_referral(first_said) is None
                          and NAMES_A_CLINICIAN.search(first_said) is None
                          and REFER.search(first_said) is None)):
            # Standing aside is right about the choice - the fence is not a "yes" - but the doubt
            # still has an answer here, and it is the answer's own condition. Nothing below this
            # point reads the fence, so the whole file stood aside over "i have a chesty cough that
            # wont shift" / "what should i do first" / "is that bad" and the chat floor gave the
            # cough "Sounds good."
            fenced = _condition_after_care(said, _first(str(said or "").lower(), CARE))
            if fenced:
                return pick(CONDITION_NORMAL if normal_ask else CONDITION_LINES,
                            memory, flat).replace("{when}", fenced)
            stated, kind = _stated_referral(said)
            # The same condition said as a thing rather than after an "if" ("Blood in it,
            # breathlessness or three weeks of it is a reason to ring the surgery or 111"), which
            # `_condition_after_care` cannot read. The three guards are the ones that keep an
            # answer's own "go" a go: a time in the sentence ("Ring the vet today if ..."), a
            # rider before the condition ("sooner if he is also off his food"), and a person who
            # has already had it longer than the answer's own threshold. A person whose own line
            # is the condition is asking about the condition itself, and the answer's yes stands.
            sentence = _the_referral_sentence(said)
            if (stated and kind == "noun" and not TIME_NOW.search(sentence)
                    and not COMPARATIVE.search(sentence)
                    and not _the_line_is_the_threshold(
                        stated, _the_line_it_answered(said, memory))):
                # The person already at the threshold is not told "not yet": "i have had a cough
                # for months" / what to do first / "is that bad" got the fence back, arguing with
                # its own timescale. The threshold met is the answer here, and the pools further
                # down that say so are never reached from this arm, so it is said here.
                if _past_the_timescale(said, memory):
                    return pick(_round_robin(MET_LINES, said), memory, said)
                return _say(SEE_STATED_LINES, memory, flat, when=stated)
            return None
        # A call for today is the answer, and the reply says so with the answer's own urgency: a
        # card that opens "Ring 111 today" must not come back as "get it looked at properly" with
        # the 111 gone.
        if _care_for_now(first_said):
            return pick(YES_SAID_LINES if URGENT_CALL.search(first_said) else SOON_LINES,
                        memory, flat)

        return None

    # "is that just age" is not a symptom and none of the pools below can answer it: what the
    # person wants to know is whether what they are seeing is ordinary, and the answer above has
    # already said what to watch for. Reading the referral out of that answer gives the bare "yes,
    # that one wants a proper look", which throws the answer's own hedge away.
    if JUST_AGE.search(flat):
        return pick(AGE_LINES, memory, said)
    # An amount owed is a figure against a usual one, and only an answer that gives the usual one
    # can have the comparison handed back: a money worry with a warm chat line above it has no
    # figure to compare, so it keeps the reading its own line earns.
    if _a_figure_owed(line) and (_is_a_comparison(said)):
        return pick(MONEY_LINES, memory, said)
    # The answer's own fenced condition answers the bare ask whatever the order of the two
    # readings inside it, and main pins that (`test_the_bare_asks_all_get_the_condition`). The
    # cystitis answer opens "that is usually cystitis" and ends "See a GP or pharmacy the same day
    # if it lasts over three days, comes with blood": read through the comparison below, the
    # "usually" came first and the person was told their stinging was the ordinary job, with the
    # one thing the answer named to watch for gone.
    # The cue is read from the earliest care word in the answer, fenced or not, because a referral
    # the answer fences with an "if" is not an unconditional one and `_referral` walks past it -
    # and that is exactly the sentence whose condition answers the ask ("See a GP if there's
    # blood, a high fever" is the whole verdict of the runs answer).
    care_at = _first(str(said or "").lower(), CARE)
    if care is not None and (care_at is None or care < care_at):
        care_at = care
    # The timescale the answer hedged on comes before its referral, and before its own fenced
    # condition: "if it lasts more than three weeks" over "i have had a cough for months" is a
    # fence the person is already standing past, and handing it back told them to watch a thing
    # they had already watched for months. Almost every answer with a threshold in it ends by
    # naming who to ring once that threshold is met, so the hedge is the answer and the referral
    # is only what to do about it.
    if _past_the_timescale(said, memory):
        return pick(_round_robin(MET_LINES, said), memory, said)
    if care_at is not None:
        fenced = _condition_after_care(said, care_at, memory)
        if fenced:
            # The condition is the answer's own words and it answers both doubts the same way:
            # "Ordinary on its own, yes. It stops being ordinary if you actually faint". A pool
            # written for "is it normal" only would argue with the answer over "is that bad".
            # The other way round is not true: CONDITION_LINES opens "Not the thing itself, no",
            # which over "is it normal" is the opposite of the answer it is quoting (neat-moth,
            # #3872). `pick` is seeded on the bare ask, which is the same words every time, so
            # every normality ask that reached this branch got that first line and then said the
            # thing "would stop being ordinary if ..." - a reply that argues with itself and with
            # the card, over the one ask this module exists for. The ask decides which way the
            # line leads.
            return pick(CONDITION_NORMAL if normal_ask else CONDITION_LINES,
                        memory, flat).replace("{when}", fenced)
    denies = _first(opening, DENIES)
    if care is not None and (ordinary is None or care < ordinary
                             or _a_plain_go(care, said)):
        return pick(_care_pool(said) if normal_ask else yes_pool, memory, flat)
    # A referral out of a later sentence, over an answer whose opening named the ordinary cause:
    # the knee answer ends "Ring your GP or a physio this week" and "is that bad" was told "that
    # one is the ordinary kind, so no". A denial in the opening still settles it.
    if care is not None and (ordinary is None or care < ordinary):
        return pick(YES_LINES, memory, flat)
    if denies is None and anywhere is not None and ordinary is not None:
        return pick(_care_pool(said) if normal_ask else yes_pool, memory, flat)
    if ordinary is not None:
        # A normality ask over an answer that said the ordinary thing and then named the
        # exception: the exception is the half that answers it. "usually harmless - worth getting
        # it checked if it hurts or gives way" read as a plain "the ordinary kind" tells the
        # person whose knee clicks with pain that their knee is normal. A yes/no doubt keeps the
        # answer it has always given, because there the ordinary word is the verdict to the
        # question asked ("is that bad" -> "the ordinary kind, so no", with the condition to
        # watch).
        if when and normal_ask:
            return pick(CONDITION_NORMAL, memory, flat).replace("{when}", when)
        # "my boiler makes a knocking noise" / "is it normal" was answered "...bleed the
        # radiators, check the pressure is 1 to 1.5 bar...", and the verdict came back "Yes,
        # that is the usual thing. Nothing to act on now" - over an answer whose own second half
        # is a job. Reassurance and a fix in one answer is the same reading as a fix on its own:
        # ordinary, and the fix above is the thing that settles it, so the pool for a fix carries
        # the verdict and the ordinary one stands aside (snappy-net, #3872). A harmless answer
        # keeps its own word: "White furry mould on the top of the compost is harmless: ... Scrape
        # it off ..." gives a job, and "is it bad for me" has one thing to answer, which is the
        # "harmless". Only a second half that is a job and no harmlessness claim in the answer
        # gives the fix the verdict.
        # The normality ask only. "is that bad" wants a verdict on the thing ("the ordinary kind,
        # so no"), and this pool talks about the answer rather than about the thing, which is not
        # a verdict at all: "i get a headache every afternoon" / "is that bad" came back "that
        # answer is the fix rather than a verdict on how bad it is" (apt-lime, #3872). The pool
        # below is reached by the ordinary reading that follows.
        if normal_ask and _first_positive(opening, SAYS_NORMAL) is None and _a_how_to(said):
            return pick(_round_robin(NOTHING_WARNED_NORMAL, said), memory, said)
        # "It is common at four and still common at nine ... so it is worth a GP visit whatever the
        # age": the ordinary word is not the whole answer, and "nothing to act on now" would
        # contradict the answer's own advice. The care has to be for now, though - "get it looked
        # at if it gives way" is advice for later and leaves the ordinary reading alone.
        if _care_for_now(said):
            return pick(BOTH_LINES, memory, flat)
        # An answer that names someone to see is not the answer this composer may call ordinary,
        # wherever the "usually" sits: the lump answer opens "usually a swollen gland from an
        # infection" and ends "anything hard, painless, fixed in place, or still there after three
        # weeks needs a GP, and so does a lump with night sweats or weight loss". Read on its
        # opening alone, "is that bad" was told "that one is the ordinary kind, so no" - an
        # all-clear over the answer's own referral, and the one reply a person with a lump must
        # not get. A referral the composer can put a fence on is handed back by the condition
        # pool above; one it cannot read a fence from ("needs a GP", "is a GP matter") is a visit
        # rather than a watch.
        # The referral can be the answer's judgement rather than an instruction - "Anything hard,
        # painless, fixed in place, or still there after three weeks needs a GP" - and then the
        # list in front of it is the fence, not a reason to say "ring them" about a soft lump
        # that the same answer called the ordinary sort. Read from the closing sentence only, so
        # a how-to answer's "anything left on the hob is..." is never touched.
        fence = _a_judgement_fence(said)
        if fence:
            return pick(CONDITION_LINES, memory, flat).replace("{when}", fence)
        if warns and not _when(said) and _referral_about_the_thing(said, _the_line_behind(memory)):
            return pick(SEE_ANYWAY_LINES, memory, flat)
        # The ordinary reading in the words of the thing itself, when it is a thing: the body
        # pools below watch it for a week and offer it a proper look, which over a boiler is
        # advice to leave it alone (#routing 77551).
        if thing and not normal_ask:
            return pick(THING_ORDINARY, memory, flat + " " + thing)
        return pick(ORDINARY_NORMAL if normal_ask else (OK_LINES if ok_ask else NO_LINES),
                    memory, flat)
    # The answer's own condition before the "worth doing" pool: "Shaking that has crept on over
    # months ... is worth a GP appointment" is advice for later in the answer's own words, and
    # "Sort it the way I said; if it keeps coming back, that's when it's somebody else's job"
    # drops the condition the answer took the trouble to describe.
    when = _when(said)
    if when:
        # The answer's condition has to be a condition: when it is the line the person just
        # wrote, quoting it back is a tautology, and a tautology in front of "ordinary on its
        # own, yes" reassures the person about the thing they were worried about.
        if _the_fence_is_their_own_line(said, memory):
            # When the answer also named somebody for today, that call is the answer's next step
            # and it is the one to point at: "my baby is not feeding" was met with "ring 111 or
            # your GP now", and the verdict is yes rather than a line about watching.
            if _a_call_for_now(said):
                return pick(YES_LINES, memory, flat)
            return pick(_round_robin(MET_CONDITION_LINES, said), memory, said)
        return pick(CONDITION_NORMAL if normal_ask else CONDITION_LINES,
                    memory, flat).replace("{when}", when)
    # A care word the answer fenced with an "if" is advice for later, so it is not a referral now
    # and the condition it was fenced by is the half that answers the bare ask: "Spicy food and
    # alcohol make it worse, and if you sweat buckets from one place or at night, that is worth a
    # GP visit" is the answer's condition, and "get it seen to" says the sweating is bad today.
    # This fallback is for an answer whose fence cannot be read as a condition; where it can, the
    # condition is handed back above (another lane, on main).
    if care is not None or anywhere is not None:
        return pick(DO_NORMAL if normal_ask else DO_LINES, memory, flat)
    if _first(opening, CARE) is not None:
        # A care opening that named a professional is that call, not a job to do: "get someone
        # in" is a plumber coming round, and "my son is 3 and not talking yet" was answered by
        # the answer's own "ask your health visitor or GP for a referral rather than waiting"
        # with "Do the job I described, and if it comes back after that, get someone in".
        if _first(opening, PEOPLE_CARE) is not None:
            return pick(YES_LINES, memory, flat)
        return pick(DO_NORMAL if normal_ask else DO_LINES, memory, flat)
    # The answer explained the thing and gave a fix, and said nothing about danger either way.
    # "damp in the corner of my bedroom" / "is that bad" was answered "Alright then - good luck
    # with it": the person asked whether it matters, and the bot handed back the door. What the
    # answer did say is that it is a thing to put right, so the verdict is that reading and not
    # a claim about how serious the thing is. It needs the answer to be a how-to rather than an
    # aside: a fix in it, and no referral, reassurance or stop anywhere.
    if _a_fix_with_no_warning(said):
        # Somebody who owes the person a duty changes whose problem it is, so the line says
        # what makes it theirs rather than calling the fault ordinary.
        if _somebody_owes_them(memory):
            return pick(_round_robin(OWED_LINES, said), memory, said)
        # Seeded on the answer, not on the bare ask: "is that bad" is the same seven words every
        # time, so seeding on it gave the damp, the rice and the radiator one identical sentence,
        # which is the one thing STYLE does not allow a pool to do.
        pool = NOTHING_WARNED_NORMAL if normal_ask else NOTHING_WARNED_LINES
        return pick(_round_robin(pool, said), memory, said)
    # An answer that is an instruction and nothing else, on a line that was not a how-to ask: the
    # pools above all stood aside (each needs an answer that explained the thing, named a referral
    # or gave a fix with a warning in it), and the acknowledgement floor took the turn with a
    # goodbye. Read here, at the end, so a pool that does have something to say keeps the turn.
    if _an_instruction_and_nothing_else(said, memory):
        # The answer's own closing sentence is the referral more often than not, and then there is
        # nothing to be vague about: the boiler answer ends "if it keeps dropping, stop topping it
        # up and get a heating engineer out", and "is that dangerous" four turns into that chat was
        # told "Nothing in that says how serious it is" over an answer that does say. Standing the
        # reading aside is not enough - every answer in this pool is an instruction and nothing
        # else, so the five doubt tests that need this pool went to the acknowledgement floor and
        # got a goodbye - and handing back the referral alone loses the figure the person acts on.
        # So the closing referral is the verdict, and the range the answer gave is kept with it.
        referral = _the_referral_it_closed_on(said)
        if referral:
            kept = _the_range_it_gave(said)
            said_back = referral + (f" {kept}" if kept else "")
            return pick(_round_robin(HANDED_BACK_LINES, said + " " + flat),
                        memory, said + " " + flat).replace("{referral}", said_back)
        # Seeded on the answer and the ask together: "is that bad" and "is that ok" over one answer
        # are two doubts and get two sentences, while the same ask twice gets the same answer.
        return pick(_round_robin(DIRECTED_LINES, said + " " + flat), memory, said + " " + flat)
    return None


# The referral said back as the verdict, when the answer closed on one. The person asked whether
# the thing matters, and the answer already says when to act and who to call, so the reply is that
# and not a line about the reply.
HANDED_BACK_LINES = (
    "That is worth acting on rather than watching: {referral}",
    "It needs sorting rather than waiting: {referral}",
    "Not one to sit on: {referral}",
)


# The range an answer gives, which is the half a person acts on and the half a bare referral
# drops: "keep it between 1 and 1.5 bar" out of the boiler answer. Read as a range of numbers with
# a unit after them, so "between 1 and 1.5 bar", "30 to 35 psi" and "between 18 and 20 degrees"
# all arrive, and a "between 2 and 3" with no unit after it does not.
_A_RANGE_OF_ITS_OWN = re.compile(
    r"\b(?:between|from) (\d+(?:\.\d+)?) (?:and|to) (\d+(?:\.\d+)?) ?([a-z]{2,10})\b", re.I)


# "Get a heating engineer out" is the way a boiler answer names the trade, and REFER reads
# see/ring/call/contact, so the act was invisible to it and the closing sentence of the boiler card
# matched nothing. The trade comes with "out", "round" or "in" after it, which is what makes it an
# act rather than a mention: "an engineer will check the pressure" is not this.
_A_REFERRAL_OUT = re.compile(
    r"\b(?:get|have|call|ring|book) (?:a |an |your |the )?"
    r"(?:(?!and\b|or\b|to\b|it\b)[a-z-]+ ){0,3}"
    r"(?:engineer|plumber|electrician|mechanic|technician|specialist|someone) ?(?:out|round|in)\b",
    re.I)


# And what to stop doing, which is the other half of a closing act: "stop topping it up".
_A_STOP = re.compile(r"\b(?:stop|don't|dont|do not) (?:[a-z]+ing|it|using it|driving|eating)\b",
                     re.I)


def _the_referral_it_closed_on(said):
    """The answer's closing sentence, when that sentence says who to get or what to stop.

    Only the closing sentence: an answer that names a professional in passing ("if it is a gas
    leak, a Gas Safe engineer needs to look at it") and then ends on a step is a how-to, and the
    pools above have it. What is left is an answer whose last word is the act.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?]) +", _flat(said)) if s.strip()]
    if not sentences:
        return ""
    last = sentences[-1]
    if len(last.split()) < 5:
        return ""
    if not (REFER.search(last) or _A_REFERRAL_OUT.search(last) or _A_STOP.search(last)
            or _first(last, STOP_DOING) is not None):
        return ""
    # The fence in front of the referral is about when to act, and the doubt comes after the
    # person has just said the situation is happening: "if it keeps dropping, stop topping it up"
    # said back to somebody who has said it drops within a day is a condition already met, and
    # handing it back verbatim asks them the question their own account answered.
    unfenced = re.sub(r"^(?:but )?(?:if|once|when|whenever) [^,]{0,70}, ", "", last, flags=re.I)
    # A stop only means something the first time it is said: by the doubt the person has already
    # been told to stop, so the half of the act that answers them is the one that names who to
    # get. Said back whole, the line is the last answer word for word, and the arbiter passes over
    # a reply that repeats the last answer - the boiler doubt came back as the whole card with
    # "Same answer, and it covers this" in front of it, a paragraph already on the screen.
    act = re.sub(r"^(?:stop|don't|dont|do not) [^,]{0,40}?,? (?:and|but) ", "", unfenced, flags=re.I)
    if len(act.split()) >= 4:
        return act
    return unfenced if len(unfenced.split()) >= 4 else last


def _the_range_it_gave(said):
    """The range the answer told the person to hold, said as a line to keep, or "".

    A referral on its own tells somebody to ring someone; the figure is what they do while they
    wait, and it is the half of the answer they act on. "between 1 and 1.5 bar" comes back as
    "Keep it between 1 and 1.5 bar in the meantime."
    """
    found = _A_RANGE_OF_ITS_OWN.search(_flat(said))
    if not found:
        return ""
    low, high, unit = found.group(1), found.group(2), found.group(3)
    if unit.lower() in ("and", "the", "for", "with"):
        return ""
    return f"Keep it between {low} and {high} {unit} in the meantime."


# The verbs an answer opens its first instruction on, for the reading below. `DOING` is the
# knowledge base's own instruction vocabulary and it already has `ask`, which is what "Ask for the
# increase in writing" opens on; `opens_on_a_job` cannot be reused here because it stands back from
# "ask for" and from "say", both deliberate where it is read (the step turn must not hand back the
# bot's own request for a subject). This reading is only ever handed an answer from the knowledge
# base, so the greeting's "say more if it helps" cannot reach it.
_STEP_OPENERS = DOING | frozenset(("say", "deal", "mention", "flag", "chase", "push", "insist"))


def _an_instruction_and_nothing_else(said, memory):
    """True when the answer only told the person what to do, on a line that stated a situation.

    A how-to the person asked for ("how do i clean the kettle") is not this: its answer is a
    method, and the pools above have it. What is left is somebody describing their week - a mate
    who keeps cancelling, a parking ticket, a rent rise - answered with the one thing to do about
    it, and a bare doubt that no pool above could rule on.
    """
    flat = _flat(said)
    if len(flat.split()) < 12:
        return False
    head = re.split(r"[:;.!?]", flat, 1)[0].strip(" ,-")
    words = _WORD.findall(head)
    if not words or words[0].lower() not in _STEP_OPENERS:
        return False
    line = _flat(_last_person_line(memory))
    if not line or A_HOW_TO_ASK.search(line):
        return False
    return True


# The answer above asked the person something instead of telling them anything, and the doubt on
# top of it has no answer to read: nothing in that reply can be ruled on, so the honest move is to
# say so and ask for the part that decides it. No line claims the thing is fine, and none of them
# repeats the question the bot just asked.
ASKED_THEM_LINES = (
    "Nothing you have told me makes it bad or fine on its own - that depends on how much it is "
    "getting to you. What is the bit that worries you most?",
    "No verdict from me on that one yet. Say what has you asking and I will tell you whether it "
    "is worth doing something about.",
    "That depends on something I have not heard yet. What is it that has you wondering?",
)


# A line with a trouble in it, for the reading below: the doubt that comes after a floor's
# question is a doubt about something that is going wrong. Without this the pool took
# "i got the job" / "Love that - well done. How are you celebrating?" / "is that ok" and answered
# it as if the job were the worry.
A_WORRY_IN_THE_LINE = re.compile(
    r"\b(?:keeps?|kept|wont|won't|refuses?|never|won't stop|hate|hates|hated|awful|horrible|"
    r"rude|nasty|unfair|upset|angry|annoyed|miserable|cry|crying|cried|stress|stressed|"
    r"worried|worry|worries|exhausted|knackered|drained|tired|hits?|hit me|shouts?|shouting|"
    r"yells?|yelling|ignores?|ignoring|off with|weird|odd|wrong|problem|falling out|fell out|"
    r"argument|arguing|argue|fights?|fighting|bully|bullied|bullying|debt|debts|skint|broke|"
    r"struggling|struggle|too much|fed up|sick of|dreading|scared|afraid|lonely|alone|"
    r"not talking|stopped talking|on top of me|getting on top|cant cope|can't cope|coping|"
    r"breaking point|drowning|shattered|rough week|bad week|a lot on|driving me|drives me|"
    r"nightmare|cant stand|can't stand|nagging|bossy|unbearable|hell|temper|disrespectful|"
    r"mean to me|picking on me|picks on me)\b",
    re.I)


# The floor's offer of help, said in the same breath as its question: both are the bot staying in
# the conversation, and neither is an answer a doubt can be read out of.
_AN_OFFER = re.compile(
    r"\b(?:if you want|if it helps|i can help|happy to help|tell me more|say more|"
    r"i'm listening|i am listening|want to talk|would you like|do you want)\b", re.I)


def _the_floor_asked_them_something(memory):
    """True when the bot's last line was a question rather than an answer to rule on."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    last = turns[-1]
    if not isinstance(last, dict):
        return False
    said = " ".join(str(last.get("bot") or "").split())
    # A question, or the offer of help that is the same move said another way: "That sounds rough.
    # If you want, I can help you think through what to do next." is a friend still in the
    # conversation, and the doubt after it was answered "Alright then - good luck with it."
    if not (said.endswith("?") or _AN_OFFER.search(said)):
        return False
    line = _flat(_the_line_behind(memory))
    # A method was asked for, so its answer is a method whoever phrased it: "how do i clean the
    # kettle" then "is that ok" is answered by the method pool, and the question at the end of
    # that answer is not the bot turning the person's own situation back on them.
    if not line or A_HOW_TO_ASK.search(line):
        return False
    return A_WORRY_IN_THE_LINE.search(line) is not None


def _a_feeling_of_their_own(line):
    """The family of state the person's own line named, or "" when it named none or a body."""
    words = [w.replace("'", "").lower() for w in re.findall(r"[A-Za-z']+", line or "")]
    if not words or len(words) > 14:
        return ""
    if words[0] not in ("i", "im", "ive", "id"):
        return ""
    if any(word in BODY_WORD for word in words) or any(word in SOMEONE_ELSE for word in words):
        return ""
    for word in words:
        if word in FEELING_FAMILY:
            return FEELING_FAMILY[word]
    return ""
