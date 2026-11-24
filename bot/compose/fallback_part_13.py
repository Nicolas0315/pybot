"""Part 13 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from . import (badnews, loss,
               trouble)
from .badnews import (reads_as_bad_news)

from .fallback_data import (
    ACKS,
    A_DAY_AHEAD,
    A_DAY_AHEAD_TENSE,
    CALL_WORDS,
    CARE_NOT_RESOLVED,
    CARE_PHRASES,
    CARE_POINTER,
    CARE_PRONOUNS,
    CARE_RESOLVED,
    CARE_WORDS,
    CRISIS_WORDS,
    EATEN_KIND,
    EATING,
    FALLBACK_MODULE,
    FIRST_PERSON,
    FORGETTING,
    GOOD_TIME_WORDS,
    GRIEVANCE,
    GRIEVANCE_HARM,
    GRIEVANCE_HARM_PHRASES,
    GRIEVANCE_HEALTH,
    GRIEVANCE_HEALTH_PHRASES,
    GRIEVANCE_IMPACT,
    GRIEVANCE_NOT_A_THING,
    GRIEVANCE_PEOPLE,
    GRIEVANCE_PHRASES,
    GRIEVANCE_PRONOUN,
    GRIEVANCE_STRAIN,
    GRIEVANCE_STRAIN_SAID,
    HOLD_AFTER,
    SORTED_AND_NO_CALL_YET,
    NOT_A_VERDICT_SUBJECT,
    NOT_THEIR_VERB,
    ONGOING_WORDS,
    OURS,
    QUESTION_OPENERS,
    STILL_HERE_AFTER,
    THANKS_AFTER,
    THANKS_WORDS,
    THE_CALL_STANDS,
    THRESHOLD_CROSSED,
    THREAD_PEOPLE,
    THREAD_TURNS,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back under the
    # same ones. The rating of a skill, the slip and the moment after it are one reading, so they
    # went together.
    SELF_BLAME_ASKS,
    EMBARRASSMENT_WORD,
    THE_GROUND_OPENS,
    DIE_OF_IT,
    GOING_TO_DIE,
    SOMEONE_ELSES_SHAME,
    A_VERDICT_ON_THE_PERSON,
    THE_MOMENT_IS_THEIRS,
    A_SLIP,
    A_SOCIAL_SLIP,
    A_SLIP_IS_NOT_A_FALL,
    IN_A_ROOM,
    LAUGHED_AT_THEM,
    A_CROWD_LAUGHED,
    A_PERSON_LAUGHED,
    LAUGHED_AT,
    EMBARRASSED,
)
from .fallback_part_02 import (
    _the_thread_is_an_animal,
)
from .fallback_part_03 import (
    HEAVY_ABOVE, SERIOUS_NEWS,
)
from .fallback_part_05 import (
    BABY_LOSS, LAUGHING, LAUGHING_AT,
)
from .fallback_part_06 import (
    HAZARD_LINE, GRIEVANCE_MINE, GRIEVANCE_MINE_THINGS, GRIEVANCE_RECUR,
)
from .fallback_part_07 import (
    RESOLVED, _feels_better, CALL_THEM_NOW, FALL_FIRST_AID, STAKES_WORDS, ALREADY_RANG,
    _someone_is_arriving, CARE_ASKS, CARE_POINTER, CARE_SEEN_ASKS, CARE_WORDS,
)
from .fallback_part_08 import (
    _in_a_care_thread,
)
from .fallback_part_12 import (
    CLAUSE_END, _red_flags_in, SENTENCE_END, _flag_events_in, _it_is_the_answer_word,
    _the_threshold_words, CARE_ROUTE_WORDS, ALREADY_OR_NOT, A_CONDITION, ABUSE_CARD,
)


def _their_own_slip(clean, memory=None):
    """Which pool an awkward moment gets: "at them" or "of their own", or None."""
    if "?" in clean:
        # A question about it is asking for something the pools below answer better, and an ask the
        # person made of the moment ("should i apologise") is help, not a story to be met warmly.
        return None
    if HEAVY_ABOVE.search(clean) or SERIOUS_NEWS.search(clean) or BABY_LOSS.search(clean):
        # A named illness or a lost pregnancy is not a clumsy minute, however quiet the room went:
        # "i told them i had cancer and everyone went quiet" is the bad-news pool's, and "that is a
        # minute you will be telling people about in a year" said to it is the worst line in the
        # file. "i had a miscarriage and everyone went quiet" is only in front of people because a
        # loss is, and "ha, we have all been there" over it is worse than saying nothing - that is
        # the grief pools' turn. The readings already exist above, so the guard asks them rather
        # than keeping a third list.
        return None
    if SELF_BLAME_ASKS.search(clean) or A_VERDICT_ON_THE_PERSON.search(clean):
        return None
    if GOING_TO_DIE.search(clean):
        return None
    if HARM_IN_A_LAUGH.search(clean) or LAUGH_STOPPED.search(clean):
        # A laugh that names harm is the safety band's, and a laugh that has stopped is the person
        # telling you something is wrong: neither is a minute to be light about.
        return None
    if isinstance(memory, dict) and _in_a_care_thread(memory):
        return None
    if A_CROWD_LAUGHED.search(clean):
        # The room, said with no "at me": "everyone in my office laughed" is not the owner of a
        # laugh the way "my boss laughed" is.
        return LAUGHED_AT
    if A_PERSON_LAUGHED.search(clean) or A_OWN_LAUGH.search(clean):
        return None
    if LAUGHED_AT_THEM.search(clean):
        return LAUGHED_AT
    if SOMEONE_ELSES_SHAME.search(clean):
        return None
    if DIE_OF_IT.search(clean) or THE_GROUND_OPENS.search(clean):
        return EMBARRASSED
    if EMBARRASSMENT_WORD.search(clean) and THE_MOMENT_IS_THEIRS.search(clean):
        return EMBARRASSED
    if A_SLIP_IS_NOT_A_FALL.search(clean):
        # A slip that ends in a body is a hurt, and the safety cards are better at it than this.
        return None
    if A_SOCIAL_SLIP.search(clean) or (A_SLIP.search(clean) and IN_A_ROOM.search(clean)):
        return EMBARRASSED
    return None


def _the_flags_still_standing(line):
    """The flag words in the line, leaving out the clauses that say it has passed.

    "the sweating has stopped but my arm hurts" is two reports: the sweat is over and the arm is
    not, so only the second one is a flag - the whole-line reading threw both away and handed the
    answer's 111 route back to somebody whose arm is the very word the answer escalates on
    (white-pigeon, #8509). A clause that reports a state in the past tense next to a settling one
    ("its stopped now but i was sweating") is the same report said twice, so its flags come out
    too. A line with no settling clause is read whole, which keeps "my arm was numb" a flag.
    """
    clauses = [c for c in CLAUSE_END.split(str(line or "").lower()) if c.strip()]
    settled = [c for c in clauses if _feels_better(c) or RESOLVED.search(c)]
    if not settled:
        return _red_flags_in(line)
    flags = set()
    for clause in clauses:
        if clause in settled or re.search(r"\b(?:was|were|had)\b", clause):
            continue
        flags |= _red_flags_in(clause)
    return flags


def _the_threshold_was_crossed(last, clean, turns):
    """True when the answer named 999 for something worse, and this line says that thing.

    Both lines are read, and that is what keeps it narrow: the answer has to have named 999 at
    all, and the flag word in this line has to be one the answer's own sentence used. "now my arm
    hurts too" after a chest answer that said "spreads to the arm or jaw" is the threshold being
    crossed; the same line after a knee answer is not, because that answer named no 999 and no arm.
    A line that says the thing is better, and a thread about an animal, keep the pools below.
    """
    said = str(last or "").lower()
    if not said or not CALL_THEM_NOW.search(said):
        return False
    line = str(clean or "")
    if _the_thread_is_an_animal(line, turns):
        return False
    if _flag_events_in(line):
        return True
    flags = _the_flags_still_standing(line)
    # The word has to be in the sentence that named the 999, not anywhere in the answer: an
    # answer that says "ring 999 if you cannot pass water" and "back pain" in another sentence is
    # not crossed by "my back is sore".
    for sentence in SENTENCE_END.split(said):
        if not CALL_THEM_NOW.search(sentence):
            continue
        if flags & _red_flags_in(sentence):
            return True
        # The sentence can carry the sign in a word of its own if-clause, and the line can say
        # that word with none of the listed ones in it - so the clause is read only for a line
        # that is not already reporting the thing better.
        if _feels_better(line) or RESOLVED.search(str(clean or "").lower()):
            continue
        for word in _the_threshold_words(sentence):
            if _it_is_the_answer_word(line, word):
                return True
    return False


# The pools whose whole point is the call: a line from one of them is a call by construction,
# whatever its wording happens to be ("Make the call now - 999 or 911 -", "The call is still the
# thing to do: 999 or 911, now."). The reader below is written for a safety or knowledge answer,
# and a phrase like "make the call now" is not one its patterns were built around.
THE_CALL_POOLS = tuple(THRESHOLD_CROSSED) + tuple(THE_CALL_STANDS)


def _it_is_this_files_call(said):
    """True when the line is one of this file's own call pools, said word for word."""
    said = " ".join(str(said or "").lower().split())
    for line in THE_CALL_POOLS:
        if said.startswith(" ".join(line.lower().split())[:40]):
            return True
    return False


def _a_newer_answer_asked_them_to_call(last, turns):
    """True when this fallback's own later line already told them to ring, so the route is stale.

    `last` is the thread's last safety answer, and the route hand-back reads the place that answer
    named - the chest-on-effort answer names 111. But the fallback can have spoken after it: "now
    my arm hurts too" is the answer's own 999 threshold, and the line after that was handed "111
    is still the one to ring" - a possible heart attack walked down to a phone call in the morning
    (close-pipe on #8509, six of twelve third lines).

    Every line of this file's own since the answer is read, not just the newest: the half of this
    thread that says "Keep the line open and follow what they tell you" is a hold on a call that
    was already asked for, so a hold must not put the stale 111 back. The walk stops at the
    answer itself and at any other module's line, because that is the thread's own last word.
    """
    for turn in reversed(turns[-THREAD_TURNS:]):
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("bot") or "")
        if not said:
            continue
        if said.strip().lower() == str(last or "").strip().lower():
            return False
        if turn.get("module") != FALLBACK_MODULE:
            return False
        if _the_answer_asked_them_to_call(said) or _it_is_this_files_call(said):
            return True
    return False


def _the_route_the_answer_named(last):
    """The place the bot's own last answer told them to go, or None.

    Only where that answer named one: an answer that says "ring 999 if it becomes pressure" has
    no route to hand back, and the pools for a plain care answer stand. The gas emergency line
    holds 111 in its number, so a number is only the 111 line when it is not part of a longer one.
    """
    text = str(last or "")
    if not text:
        return None
    if re.search(r"0800\s*111\s*999", text):
        text = re.sub(r"0800\s*111\s*999", "the gas emergency line", text)
    for name, pattern in CARE_ROUTE_WORDS:
        if pattern.search(text):
            return name
    return None


def _the_answer_asked_them_to_call(last):
    """True when the bot's own last answer told the person to ring the emergency services now.

    Read from the answer and nothing else: it is the answer that says whether the bot is holding
    an emergency open or has just given first aid with a red flag in it. The number has to be
    said without a condition round it - "ring 999 if it becomes pressure" is what to watch for,
    not what to do this minute - and every sentence is read on its own, because the practical
    sentence before it ("ring 111 or your GP first thing") is where the condition ends.
    """
    for sentence in SENTENCE_END.split(str(last or "")):
        # "If you haven't already, ring 999" is a call to make now, so that one condition is
        # taken out before the rest are looked for: the others all name a threshold.
        low = ALREADY_OR_NOT.sub("already", sentence.lower())
        clauses = CLAUSE_END.split(low)
        led_by_condition = False
        for clause in clauses:
            opens_with_condition = A_CONDITION.search(clause) is not None and (
                not re.search(r"\b(?:call|ring|ringing|dial|phone|text|press|try)\b", clause))
            if CALL_THEM_NOW.search(clause):
                if A_CONDITION.search(clause) is None and not led_by_condition:
                    return True
            led_by_condition = opens_with_condition
    return False


def _raises_the_stakes(clean, last):
    """True when the person's line meets the red flag their first-aid card named.

    Only after a fall card: the same words elsewhere are not an emergency (a scratch on a blood
    thinner is a scratch), and the fall card is the one that hands over age, weight-bearing and
    a bang on the head as the point where the care line becomes 999.
    """
    return bool(STAKES_WORDS.search(clean)) and bool(FALL_FIRST_AID.search(str(last or "").lower()))


def _releasable(memory):
    """True when the thread the composer is holding can be let go by a new subject.

    Only a care answer can be. An emergency line that names the emergency services or a crisis
    line is a crisis thread, and it holds every part of itself: "my head is hurting" after an
    overdose, or a new ache while the person is still in danger, is the emergency still going,
    not a second complaint. The line that decides it is the safety answer, not this turn's, and
    it is one function so a rule about letting go of a thread cannot be written twice.
    """
    for turn in reversed([t for t in (memory.get("turns") or []) if isinstance(t, dict)][-THREAD_TURNS:]):
        if turn.get("module") == "safety":
            last = str(turn.get("bot") or "").lower()
            return not (any(word in last for word in CRISIS_WORDS)
                        or _the_answer_asked_them_to_call(last))
        if turn.get("module") != FALLBACK_MODULE:
            return False  # not this fallback's thread at all
    return True


def _is_a_hazard(last):
    """True when the emergency the bot answered is a fire, a gas leak or an alarm going off.

    Read from the bot's own last answer and nothing else: that answer says what it was about
    ("leave the building... if there is smoke", "put out any flames"), while the line now may
    name a fuel without being a hazard at all - "my gas cooker wont light" in the middle of a
    heart attack is a remark, not a fire. A person's injury is not a hazard even when a fuel is
    mentioned - "my son pulled the kettle over" is a scald, and the answer to that one is about
    cooling the skin, so the pools for a hurt person stay.
    """
    return bool(HAZARD_LINE.search(str(last or "").lower()))


def _the_safety_cards(turns):
    """The safety answers still in the thread window, newest last.

    The thread can run several turns and the safety module answers some of them itself, so the
    card is not always the last reply: the one that started the thread is what says whether this
    is a crisis line, a call to make now, or somebody being hurt.
    """
    return [str(turn.get("bot") or "").lower() for turn in list(turns or [])[-THREAD_TURNS:]
            if str(turn.get("module") or "") == "safety"]


def _somebody_is_coming(turns, clean):
    """True when the person has rung, or help is with them, anywhere in the thread."""
    for turn in list(turns or [])[-THREAD_TURNS:]:
        said = str(turn.get("user") or "").lower()
        if said and (ALREADY_RANG.search(said) or _someone_is_arriving(said)):
            return True
    return bool(ALREADY_RANG.search(clean)) or bool(_someone_is_arriving(clean))


def _the_answer_was_an_abuse_card(last):
    """True when the bot's own last answer was the domestic abuse card.

    Read from the answer rather than from the line, because the line that follows an abuse card
    ("should i get out of the house") says nothing about abuse at all - the card is what makes
    this thread one where the person asking is the one in danger.
    """
    return bool(ABUSE_CARD.search(str(last or "")))


def _thread_was_closed(turns):
    """True when this fallback's last line in the thread was a close, not advice.

    "thanks, its stopped" is answered from THANKS_AFTER ("Any time. Take care — ring again if
    anything changes"), and that is the end of it: the next bare "ok" is a nod on the way out,
    not a line that needs the advice again.
    """
    for turn in reversed(turns[-THREAD_TURNS:]):
        if turn.get("module") != FALLBACK_MODULE:
            continue
        return any(str(turn.get("bot") or "").startswith(line[:24]) for line in THANKS_AFTER)
    return False


def _hold_pool(turns, clean, last, done_report=False):
    """The hold pool: one that may promise a call only when this thread already has one.

    "the operator", "the crew are on their way" and "keep the line open" are true after a 999
    call and a lie after a burn under the tap, so a care thread gets the plain hold instead
    (cobalt-panther and gray-cypress, #820).

    A done report is a third case: "i sorted it" says the person thinks the thing is handled, and
    not that anybody was rung, so a line that names an operator or a crew needs their own words to
    say somebody was (chief-umbrella and fancy-penguin, #7230).
    """
    if not _a_call_is_known(turns, clean, last):
        return STILL_HERE_AFTER
    if done_report and not (ALREADY_RANG.search(clean) or _already_rang(turns)):
        return SORTED_AND_NO_CALL_YET
    return HOLD_AFTER


# Advice to ring a number today is not a call in progress. "Ring 111 today about a home detox"
# is the same shape as "ring 999 now" as far as a number is concerned, and the difference is the
# one that matters: after the first, "ok" was answered "the crew are on their way" for a crew
# nobody had rung.
IMMEDIATE_CALL = re.compile(
    r"\b(?:ring|call|phone|dial)\s+(?:999|911|112|an\s+ambulance)\b"
    r"|\b999\s+(?:or\s+911\s+)?(?:now|straight|immediately|first)\b"
    r"|\bstraight\s+away\b|\bright\s+now\b|\bthere\s+and\s+then\b", re.I)


def _a_call_is_known(turns, clean, last):
    """True when somebody has been rung in this thread: said here, said before, or in the advice."""
    if ALREADY_RANG.search(clean) or _already_rang(turns):
        return True
    text = str(last or "")
    if not any(word in text for word in CALL_WORDS):
        return False
    # A number in the advice is only a call when the advice is to make one now. The gentle card
    # that says "ring 111 today" leaves the thread with nobody called, so the hold must not
    # promise a crew.
    if "111" in text and not IMMEDIATE_CALL.search(text):
        return False
    # A call put behind a condition is advice for a later turn, not a call in progress: after
    # "press a clean cloth on the cut ... if it soaks through, the edges gape, or they go pale or
    # dizzy, that's 999 or 911" a person saying "i did that" got "the crew are on their way" for
    # a crew nobody had rung.
    return not _the_call_is_conditional(text)


# A condition in front of the call is the whole difference between an instruction and a plan:
# "if it soaks through ... that's 999 or 911" is for the next turn, "ring 999 or 911 straight away"
# is now. Only the sentence that carries the call is read, so a condition elsewhere in the card
# does not spoil a call the card gives flatly.
CONDITIONAL_OPENING = re.compile(
    r"^\W*(?:if|unless|when|whenever|in\s+case|should|after|once|any\s*time)\b", re.I)


def _the_call_is_conditional(text):
    """True when every sentence of the answer that names a call puts it behind a condition."""
    carrying = [sentence for sentence in re.split(r"(?<=[.!?])\s+", str(text or ""))
                if any(word in sentence.lower() for word in CALL_WORDS)]
    if not carrying:
        return False
    return all(CONDITIONAL_OPENING.search(sentence.strip()) for sentence in carrying)


def _already_rang(turns):
    """True when the person said, in the last few turns, that somebody has been rung."""
    return any(ALREADY_RANG.search(str(turn.get("user") or "").lower())
               for turn in turns[-3:] if isinstance(turn, dict))


def _thanks_carries_emergency(words, clean):
    """True when a thanks also says the emergency is still going on.

    The thanks pools are a close, so they must not answer "thanks, its still soaking through".
    Any care word other than "thanks", a pronoun or a pointer ("still", "call", "there") counts,
    as does a mid-emergency ask ("is it safe to go down"); a bare "ok thanks" has none of these
    and closes. A thanks that also says it is over ("the doctor came", "the bleeding stopped",
    "its fine now") is a close, unless it also says it is still going on.
    """
    said = set(words)
    content = (said & CARE_WORDS) - THANKS_WORDS - CARE_PRONOUNS - CARE_POINTER
    if content and said & ONGOING_WORDS:
        return True
    if said & CARE_RESOLVED:
        # Only a resolved word still counts as resolved; "hasnt stopped"/"not fine" do not.
        return bool(said & CARE_NOT_RESOLVED)
    return bool(content or CARE_ASKS.search(clean) or CARE_SEEN_ASKS.search(clean)
                or any(phrase in clean for phrase in CARE_PHRASES))


# A date of ours going by is not a memory sign. "my husband keeps forgetting our anniversary"
# is a complaint about the partner, and it was read as the health word "forgetting" and answered
# with a GP and a dementia workup - a workup for a forgotten date (deck row habit-08). Only a date
# is let through: forgetting where you live, a name, the way home is the memory reading.
A_DATE_OF_OURS = re.compile(
    r"\b(?:forget(?:s|ting|ful)?|forgot)\b[^.]{0,24}?\b(?:our|my)\s+"
    r"(?:anniversary|birthdays?|dates?(?: night)?|valentine'?s|wedding day|christmas|plans?)\b")


# A worry said out loud about the person is the care line whatever else is in the line: "my husband
# keeps forgetting our anniversary, i think something is wrong" is asking about him, not about his
# manners, and the grumble pool would answer the wrong question. "not like him" and "getting worse"
# are how people say the same thing without naming a worry at all.
A_WORRY_ABOUT_THEM = re.compile(
    r"\b(?:something|summat)\s+(?:is|seems|feels)\s+(?:wrong|off|not right)\b|"
    r"\bnot (?:like|acting like) (?:him|her|them|himself|herself|themselves)\b|"
    # "shes not herself", "hes not his usual self": the person they know has changed, which is
    # the same worry as "not like him", and it turns a forgotten date back into the care line.
    r"\bnot (?:quite |really |been )?(?:himself|herself|themselves)\b|"
    r"\bnot (?:his|her|their) usual (?:self|selves)\b|"
    r"\b(?:worse|worrying)\b|\bworried about (?:him|her|them)\b|"
    r"\bshould i (?:be )?worr(?:y|ied)\b|\bdementia\b|\balzheim\w*\b|"
    r"\bconfus(?:ed|ion)\b|\bmemory\b")


def a_date_of_ours_forgotten(clean):
    """True when the line is somebody forgetting a date of ours - an anniversary, a birthday.

    Read by `chat` before it answers a person's trouble as a memory sign: a forgotten date is a
    complaint about the partner, and the grievance pool here is the reply for it, not a GP. A worry
    in the same line is the person asking about them, so the care line keeps that one.
    """
    said = " ".join(str(clean or "").lower().split())
    return bool(A_DATE_OF_OURS.search(said)) and not A_WORRY_ABOUT_THEM.search(said)


def _impact_said(clean):
    """The words of what somebody did, where the somebody is the one doing them."""
    tokens = re.findall(r"[a-z']+", clean)
    found = set()
    for position, token in enumerate(tokens):
        if token not in GRIEVANCE_IMPACT:
            continue
        before = tokens[max(0, position - 2):position]
        if before and before[-1] in NOT_THEIR_VERB:
            continue
        if any(word in FIRST_PERSON for word in before):
            continue
        # Forgetting is only about the two of them when it is a date of ours that went by:
        # "my boyfriend forgot our anniversary" is the complaint, "my friend forgot his keys"
        # is just what happened to him.
        if token in FORGETTING and not (set(tokens[position + 1:position + 4]) & OURS):
            continue
        # "eats all the biscuits" is the complaint; "eats meat", "eats fish on fridays" is a
        # diet, and the person is talking about what to cook rather than about their manners.
        if token in EATING and tokens[position + 1:position + 2] and \
                tokens[position + 1] in EATEN_KIND:
            continue
        found.add(token)
    return found


def _grief_thread(memory):
    """True when the last thing the bot said about this was a condolence.

    "we lost the baby in february" then "my partner wont talk about it": the partner is part of
    the grief, so the line keeps the thread rather than treating it as somebody's bad manners.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in reversed(turns[-THREAD_TURNS:]):
        line = str(turn.get("bot") or "")
        if not line:
            continue
        return any(line.startswith(reply[:30]) for reply in loss.LOSS_REPLIES)
    return False


def _grievance_thread(memory):
    """True when the last thing the bot said about this was the offer to talk it over.

    "my friend drains me" then "she rings me every night as well": the second line names the
    person only as "she", and the reader wants a person word ("my sister") or something of theirs
    in the way, so the follow-up fell through to "Thanks for telling me - I'm here if you want to
    dig into any of that" - the line that fits any message, said to somebody who is still
    complaining about the same person.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in reversed(turns[-THREAD_TURNS:]):
        line = str(turn.get("bot") or "")
        if not line:
            continue
        return any(line.startswith(reply[:30]) for reply in GRIEVANCE)
    return False


def _someone_else_minding(clean, words, after=False):
    """True when the line is about what another person keeps doing, and the person minds it.

    The person has to be in the line as somebody else ("my sister", "the landlord", "someone")
    and the line has to say it keeps happening ("keeps", "always", "never", "again", "without
    asking"). Asked only about the person's own line, never about the bot: "you never listen"
    is a complaint about the bot and gets a different reply.
    """
    said = {w for w in words if w.isalpha() or "'" in w}
    # "she is so draining", "he is really exhausting", "they are tiring": a pronoun in front of
    # the word for the wear is already the person, and the wear is in the word itself. Without
    # this the first line of a complaint that names somebody only as "she" fell to the line that
    # fits any message - "Thanks for telling me - I'm here if you want to dig into any of that" -
    # when the person had just said that somebody tires them out.
    a_person_pronoun = bool(GRIEVANCE_PRONOUN.search(clean))
    if said & GRIEVANCE_PEOPLE:
        if not ({"my", "our", "the"} & said):
            return False
    elif not (after and said & THREAD_PEOPLE) and not a_person_pronoun:
        # A follow-up in the same thread names the person only as "she" or "he": it is still the
        # same row, so the person comes from the turn before rather than from this line.
        return False
    # "he never says thank you for anything" is about him, not about the bot: "thank you" is the
    # only "you" in the line and it is the phrase, so it is taken out before the test.
    spare = clean.replace("thank you", "thanks").replace("thank u", "thanks")
    if " you " in " " + spare + " ":
        return False  # "you never listen" is a complaint about the bot, not about them
    if said & GRIEVANCE_HEALTH or said & GRIEVANCE_HARM:
        # A body, an illness or a harm wants a care line, not a word with them - except where the
        # health word is the forgetting of a date of ours, which is the grievance itself.
        if not (a_date_of_ours_forgotten(clean) and not said & GRIEVANCE_HARM):
            return False
    if any(phrase in clean for phrase in GRIEVANCE_HARM_PHRASES):
        return False
    if any(phrase in clean for phrase in GRIEVANCE_HEALTH_PHRASES):
        return False
    if _impact_said(clean) - set(GRIEVANCE_MINE.findall(clean)):
        return True
    if GRIEVANCE_RECUR.search(clean):
        # In a thread that is already about them, the "again" is enough. The exception is the
        # person turning it on themselves - "i never say anything to her" is their own silence,
        # not the other one's manners, and the offer to work out what to say would talk past it.
        if after and not GRIEVANCE_MINE.search(clean):
            return True
        if any(word not in GRIEVANCE_PEOPLE and word not in GRIEVANCE_NOT_A_THING
               for word in GRIEVANCE_MINE_THINGS.findall(clean)):
            return True
    if any(phrase in clean for phrase in GRIEVANCE_PHRASES):
        return True
    if any(phrase in clean for phrase in GRIEVANCE_STRAIN):
        return True
    return bool(GRIEVANCE_STRAIN_SAID.search(clean))


def _short_ack(words):
    """True for a bare "ok", "right", "got it" — a nod, not a new subject."""
    return len(words) <= 2 and bool(set(words) & ACKS)


# The subject a good time is had by: a group, or the event itself. A person on their own saying
# "i had a lovely day" is left to the ordinary pools, because that line is about them and the
# good news and feeling replies know what to do with it.
GOOD_TIME_SUBJECT = re.compile(
    r"\b(?:everyone|everybody|all of them|"
    # An event belongs to somebody as often as it is "the" event: "my sister's wedding was lovely"
    # and "the kids' match was great" are the same good half of a chat as "the wedding was lovely",
    # and the possessive in front of the word kept them out of it - they reached the pool that
    # answers nothing ("Thanks for telling me - I'm here if you want to dig into any of that") and,
    # on the first of them, "I'm listening - say more if it helps".
    r"(?:the|my|our|his|her|their|your|\w+'s?)"
    r"(?:\s+\w+){0,2}\s+"
    r"(?:party|wedding|meal|trip|holiday|gig|match|game|concert|night|day|weekend|evening|"
    r"dinner|barbecue|bbq|bash|hen|stag))\b")


GOOD_TIME_OURS = re.compile(
    r"\bwe (?:had|have had) (?:a |such a )?(?:great|lovely|brilliant|good|amazing|wonderful|"
    r"fantastic|smashing)\b")


# A good day is the same good time said about one person, and it is how most people report one:
# "i had a really good day today", "great day today", "best day ever". The greeting words are the
# reason this is not just an adjective and a day - "good morning", "good night" and "have a good
# day" are hello and goodbye, and a warm question about the best of it is the wrong reply to
# either. So the line has to say it happened to them ("i had...") or say how the day went
# ("today was..."), and never just name it.
GOOD_DAY_OURS = re.compile(
    # A good day had by somebody the person knows is a good day too: "the kids had a lovely time"
    # and "my mum had a good day" were answered with the neutral pool, the line a person gives when
    # they were not listening. The subject is the person or the group, so the same words that say
    # "i had" say "the kids had".
    r"^(?:(?:i|we|ive|i've|weve|we've|(?:my|our|the|his|her|their)(?:\s+\w+'s)?"
    r"(?:\s+\w+){0,2})\s+)?(?:had|have had|ve had|has been having|am having|"
    r"are having)\s+(?:a\s+|such a\s+|a really\s+|a proper\s+|a pretty\s+)?"
    r"(?:really\s+|properly\s+|pretty\s+|so\s+|such\s+|super\s+)?"
    r"(?:good|great|lovely|nice|brilliant|amazing|wonderful|lush|smashing|fantastic)\s+"
    # The list is the times a good day is said with, and the things people do with one: "i had a
    # lovely walk today" and "we had a nice lunch" are the same good half of a chat, and the
    # thing is what the pools' question can be about.
    r"(?:day|week|weekend|evening|afternoon|morning|night|shift|time|walk|swim|run|ride|"
    r"cycle|lunch|dinner|meal|picnic|bath|shower|breakfast|coffee|nap|sleep|lie in|read)\b")


# "great day today" and "good day at work" drop the "i had" altogether. These are anchored at the
# start of the line, which is what keeps "have a good day" (a goodbye) and "good morning" (a
# hello) out of it, and they leave out "good" and "nice" for the same reason.
GOOD_DAY_BARE = re.compile(
    r"^(?:what |such |a )?(?:really |so |pretty |proper |quite )?"
    r"(?:great|lovely|brilliant|amazing|wonderful|fantastic|lush|smashing|perfect)\s+"
    r"(?:day|week|weekend|evening|afternoon|morning|night|shift)\b")


GOOD_DAY_WENT = re.compile(
    r"\b(?:today|yesterday|the day|the week|the weekend|last night|this (?:morning|afternoon|"
    r"evening)|my day|my week|my weekend)\s+(?:was|has been|went|'s been)\s+(?:a\s+)?"
    r"(?:really\s+|so\s+|proper\s+|pretty\s+|such\s+|quite\s+)?"
    r"(?:good|great|lovely|nice|brilliant|amazing|wonderful|fine|alright|lush|fantastic)\b"
    r"|\bbest\s+(?:day|week|weekend|evening|night)\b")


# The same good time said with "it" for a subject: "it was great", "it was such a nice day",
# "it was a lovely evening", "it was great fun". Every one of these was answered with the neutral
# pool ("Thanks for telling me - I'm here if you want to dig into any of that") or with an echo,
# because the good-time gate wanted a subject it could name: a day, a group, or the person. "it"
# is a subject too, and the thing it stands for is whatever the two of them were just on.
#
# The words after the good word are what keep this off the lines that only look alike. "it was a
# good idea", "it was nice of her", "it was great news" and "it was nice to meet you" all carry a
# good word and a subject, and none of them is a good time had by anything: the tail is a short
# list of the things a good time can be, or nothing at all.
GOOD_TIME_IT = re.compile(
    r"^(?:it|that|this)\s+(?:was|were|has been|s been|turned out)\s+"
    r"(?:(?:a|an|such a|such)\s+)?"
    r"(?:(?:really|so|pretty|proper|properly|quite|absolutely|dead|very)\s+)?"
    r"(?:good|great|lovely|nice|brilliant|amazing|wonderful|fantastic|lush|smashing)\b"
    r"(?:\s+(?:fun|time|day|night|evening|weekend|week|meal|trip|holiday|break|wedding|party|"
    r"gig|show|film|game|match|outing|afternoon|morning|christmas|birthday|dinner|lunch|"
    r"barbecue|do|out|away|all|overall|actually|though|thanks|in the end)\b)*\s*$")


# A verdict on a thing, said with nothing asked: "it was dead good actually", "its dead good
# actually", "the film was lovely". The subject is a thing of theirs or an "it/that/this", never
# a person ("my mum was great" is about her, and the family and feeling pools know what to do
# with those), and the good word ends the line, so a mixed verdict ("it was good but the ending
# dragged") keeps its own reply. "its" is "it is" written without the apostrophe, so the copula
# is optional: the intensifier or the good word is what carries the sense either way.
GOOD_VERDICT = re.compile(r"""
    ^\W*(?P<subject>(?:it|its|it\'s|that|thats|that\'s|this|the\s+\w+|my\s+\w+|our\s+\w+)
         (?:\s+(?:was|is|were|are|has\s+been|\'s\s+been))?)\s+
    (?:really\s+|so\s+|proper\s+|pretty\s+|dead\s+|quite\s+|absolutely\s+|well\s+)*
    (?:good|great|lovely|nice|brilliant|amazing|wonderful|lush|smashing|fantastic|superb|
        class|fun)\b
    (?:\s+(?:actually|honestly|tbh|though|to\s+be\s+fair))?\W*$
""", re.X | re.I)


# The turns a good word can follow without being a good time: an accident, a body in trouble, a
# pet put to sleep. `badnews` reads the news a friend meets gently; these are the plain words for
# the same week that it leaves to other readers.
HARD_WEEK = re.compile(r"\b(?:fall|fell|fallen|tripped|collapsed|collapse|seizure|stroke|"
                       r"overdose|accident|crash|crashed|put down|passed away|in hospital|"
                       r"operation|surgery|stitches|broken|broke (?:my|his|her|their))\b")


def _hard_week_in_the_thread(memory):
    """True when the thread still holds a death or an accident the bot was gentle about.

    A list of ceremony words is a net with holes in it (sure-umbrella on #3594: "a list always
    leaves one out"), so the reading stands down on the shape that matters instead - a recent
    turn that was a death, an accident, or a line a friend would answer gently. "my mum had a
    fall" a turn before "the paramedics were brilliant" is the same hard week as a funeral: the
    good word is about how they were, not about a good time.
    """
    if not memory:
        return False
    if loss._loss_is_the_thread(memory):
        return True
    for earlier in [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(earlier.get("user") or "").lower().split())
        if line and (reads_as_bad_news(line) or badnews.reads_as_sudden_loss(line)
                     or HARD_WEEK.search(line)):
            return True
    return False


def _a_verdict(clean, memory=None):
    """True when the line is a good verdict on a thing, with nothing asked and nothing after it.

    The thing has to be something you can have a good time with: a person is not (the family and
    feeling pools have better lines for them) and neither is a place of care or a funeral, where
    the same words describe how a hard week went rather than how nice it was. In a bereavement
    nothing on the line is a night out either: "the flowers were lovely" and "the service was
    lovely" are about the day, and the reading stands down for the whole thread rather than for a
    list of its words (emerald-carpet on #3594: the loss card kept the eulogy by luck, because
    only a subject the reader catches would have taken it).
    """
    if _hard_week_in_the_thread(memory):
        return False
    found = GOOD_VERDICT.search(clean)
    if not found:
        return False
    said = found.group("subject").lower().split()
    head = said[1] if len(said) > 1 else said[0]
    if head in GRIEVANCE_PEOPLE or head in trouble.OTHERS:
        return False
    if head in NOT_A_VERDICT_SUBJECT:
        return False
    return True


# Looking forward said as a want rather than as news. The news-to-come reader keys on the thing
# (a wedding, a baby, a move, a holiday), so a weekend, a Friday, a night out or a person seen
# again went past it to the floor. Only the looking-forward phrase counts, and only when the line
# does not turn it into dread: "i cant wait for this week to end", "cant wait to get out of here"
# and "not looking forward to monday" are a bad week, not a thing to look forward to, and the
# trouble and mood pools answer them.
LOOKING_FORWARD = re.compile(
    r"\b(?:cant|cannot|can not|can't)\s+wait\b"
    r"|\b(?:really |so |properly |very )?(?:am |im |i'm )?looking forward to\b"
    r"|\broll on\b"
    r"|\bcount(?:ing)? down (?:the days )?(?:to|till|until|til)\b"
    r"|\b(?:only|just)\s+\d+\s+(?:days?|weeks?|sleeps?)\s+(?:to go|till|until|til)\b"
    r"|\bnot long (?:now )?(?:till|until|before)\b"
    r"|\b(?:excited|buzzing|chuffed) (?:about|for|to)\b", re.I)


# "Cant wait" is an eagerness only when what follows is worth waiting for. The other sense is
# being at home when somebody turns up: "cant wait in for an engineer", "cant wait around for a
# delivery", "i cant wait until friday for the boiler man". "and i have to be at work at 7 so
# cant wait in for an engineer" was answered "That's worth looking forward to. Tell me how it
# goes.", and "cant wait around for a delivery, i work days" was cheered the same way. The words
# after the wait are the test, so every wording of that sense goes with them, and a line that
# looks forward in another way as well ("i cant wait in all day but i cant wait to see her") keeps
# its eagerness.
A_CANT_WAIT = re.compile(r"\b(?:cant|cannot|can not|can't)\s+wait\b", re.I)


# The stay-at-home sense on its own: waiting in, around, about, at home.
A_WAITING_IN = re.compile(r"\s+(?:in|around|about|at\s+home|indoors)\b", re.I)


# And the same sense said with the person it is for, when the line also says the day is not
# theirs to give: "i have to be at work at 7 so cant wait in for an engineer" is the plain one,
# "i work days so i cant wait until friday for the boiler man" is the same wait. Without a
# working day in the line, "i cant wait for the plumber to come and fix the heating" stays the
# eagerness it reads as, because a cold house is worth waiting for.
A_WAITING_FOR_A_TURN_UP = re.compile(
    r"\s+(?:for|till|until|til|on)\s+(?:[\w']+\s+){0,4}?"
    r"(?:engineer|plumber|electrician|gas\s+man|boiler\s+man|repair\s+man|delivery|deliveries|"
    r"parcel|parcels|courier|post|postman|installer|technician|builder|roofer|scaffolder|council|"
    r"nurse|carer|vet|someone|anyone|somebody|it\s+to\s+(?:be\s+)?(?:fixed|repaired|arrive|come|"
    r"turn\s+up)|them\s+to\s+(?:come|arrive|turn\s+up))\b", re.I)


A_WORKING_DAY = re.compile(
    r"\b(?:have\s+to\s+be\s+(?:at|in)\s+work|have\s+to\s+work|ive\s+got\s+to\s+work|"
    r"im\s+at\s+work|i'm\s+at\s+work|i\s+work\b|im\s+working|i'm\s+working|on\s+shift|"
    r"working\s+days?|no\s+time\s+off|not\s+free|only\s+free|day\s+off)\b", re.I)


# What turns a want-to-come into a dread: the thing coming is an end, or the line says it is not
# looked forward to.
NOT_LOOKED_FORWARD_TO = re.compile(
    r"\b(?:to (?:end|finish|be over|be done with|stop)|over with|get (?:it|this) over)\b"
    r"|\b(?:to )?(?:get out|leave|quit|resign|escape|be done|go home)\b"
    r"|\b(?:not|never)\s+(?:really\s+|at all\s+)?looking forward to\b"
    r"|\bdread(?:ing)?\b|\bnot (?:to )?(?:the )?end\b"
    r"", re.I)


# A wait for the end of a life is not a wait for something to come, and it is not a stretch the
# person wants behind them either. "i cant wait to die" was answered "That's worth looking
# forward to. Tell me how it goes." - the worst sentence this bot can hand a person - and the
# pool for wanting a bad stretch over ("Fair enough. What's making it drag?") is not much better.
# "i cant wait to be out of pain" and "i cant wait to see my dad again", said about a parent who
# has died, read the same way. The safety and loss readings catch the phrasings that name a
# method ("i want to die", "i wish i was dead"); these name none, so both cheer pools stand
# aside and the flat reply the store has is better than either.
A_WAIT_FOR_A_LIFE_TO_END = re.compile(
    r"\b(?:to|till|until|til)\s+(?:i\s+)?(?:die|be dead|be gone|be with (?:him|her|them)|"
    r"not wake up|stop (?:hurting|being here)|be out of (?:this )?pain|be at peace)\b"
    r"|\b(?:die|dying|dead|death|suicide|kill myself|end it all|no reason to live)\b"
    r"|\bsee (?:my |our )?(?:mum|mom|mother|dad|father|son|daughter|wife|husband|gran|nan|"
    r"grandad|grandma|grandpa|brother|sister|baby|child) again\b", re.I)


DREADING = re.compile(
    r"\bdread(?:ing|s)?\b|\bnot (?:really |at all )?looking forward to\b"
    r"|\bcant face\b|\bcan't face\b|\bthe thought of\b[^.?!]{0,40}\bmakes me\b", re.I)


# What a dread line has to be left to: something that is really wrong is the trouble, feeling or
# safety pools' line, not a light question.
NOT_A_MILD_DREAD = re.compile(
    r"\bdread (?:to|what(?:ever)? it) (?:think|hear)\b|\bdread to think\b|"
    r"\b(?:suicide|kill myself|end my life|self[- ]harm|hit me|hurts? me|abuse[sd]?|"
    r"died|dying|death|funeral|cancer|hospital|diagnos\w*)\b", re.I)


def _dreading(clean):
    """True for a mild thing coming that the person is not looking forward to."""
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text or len(text.split()) > 20:
        return False
    if not DREADING.search(text) or NOT_A_MILD_DREAD.search(text):
        return False
    return True


def _wants_it_over(clean):
    """True when the thing being waited for is the end of a bad stretch."""
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text or A_WAIT_FOR_A_LIFE_TO_END.search(text):
        return False
    return bool(LOOKING_FORWARD.search(text) and NOT_LOOKED_FORWARD_TO.search(text))


# A thing with a date on it in the person's own future, said flat: "my holiday is next week",
# "im off on holiday in two days", "my exam is on monday", "my sister is visiting next week", "i
# have a hospital appointment tomorrow". The nod files these back ("Noted: your holiday is next
# week"), which is the restatement STYLE.md rules out and answers nothing at all: something is
# ahead of them, and the useful reply is about that. Split by tone, because a holiday and a
# hospital appointment do not want the same question.
DATE_AHEAD = re.compile(
    r"\b(?:tomorrow|tonight|next (?:week|month|year|weekend)|this (?:weekend|afternoon|evening)|"
    r"(?:on )?(?:mon|tues|wednes|thurs|fri|satur|sun)day|next (?:mon|tues|wednes|thurs|fri|satur|"
    r"sun)day|in (?:\d+|a few|a couple of|two|three|four) (?:days?|weeks?|months?)|"
    r"in the morning|the week after|not long now)\b", re.I)


# The line has to be about the person's own thing, not a general remark with a day in it
# ("sundays are lovely" is not a plan).
DATE_AHEAD_OWN = re.compile(
    r"\b(?:my|our|im|i'm|i am|we are|we're|ive|i've|i have|i start|i go|i get|im off|i'm off)\b"
    r"|\bthe (?:wedding|holiday|trip|exam|interview|test|party|scan|operation|appointment|"
    r"viewing|hearing|move)\b", re.I)


# A thing that is ahead and good, and a thing that is ahead and tense. Without one of these the
# line is left to the rest of the chain.
AHEAD_NICE = re.compile(
    r"\b(?:holiday|holidays|trip|break|week off|visit|visiting|visitor|party|wedding|christening|"
    r"concert|gig|festival|night out|day out|meal|dinner|lunch|housewarming|camping|abroad|"
    r"flight|date|seeing|meeting up|reunion|graduation|barbecue|bbq|staying|going away|getaway|"
    r"off to|away for)\b", re.I)


AHEAD_TENSE = re.compile(
    r"\b(?:exam|exams|test|interview|scan|operation|surgery|appointment|hospital|dentist|doctor|"
    r"assessment|presentation|results|deadline|inspection|audit|court|hearing|tribunal|"
    r"check-?up|treatment|procedure|settlement|viewing|inspection|review|appraisal|"
    r"one-to-one|back to work|back at work|back to school|term starts|jab|jabs|vaccine|"
    r"vaccination|injection|booster|blood test)\b", re.I)


# Whatever else is in the line, these are somebody else's to answer: a death, a funeral, a
# diagnosis or abuse is not a plan, and the loss, safety and trouble pools come first anyway.
NOT_A_PLAN = re.compile(
    r"\b(?:died|dying|death|funeral|buried|cremation|hospice|terminal|cancer|chemotherapy|"
    r"hit me|hurt me|abuse[sd]?|miscarriage|stillborn|passed away|suicide|kill myself)\b", re.I)


def _a_day_ahead(clean):
    """Return the pool for a dated thing ahead of the person, or None.

    Read only when the line is a statement about their own thing and the thing is either good or
    tense. Anything else keeps whatever reply it had - this is here to stand in for the nod, not
    to answer everything with a date in it.
    """
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return None
    if not DATE_AHEAD.search(text) or not DATE_AHEAD_OWN.search(text):
        return None
    if NOT_A_PLAN.search(text):
        return None
    if AHEAD_TENSE.search(text):
        return A_DAY_AHEAD_TENSE
    if AHEAD_NICE.search(text):
        return A_DAY_AHEAD
    return None


def _the_wait_is_for_someone_to_turn_up(text):
    """True when the only looking forward in the line is a "cant wait" that means being at home.

    Read on what follows the wait, and only when every "cant wait" in the line is that sense and
    no other shape in the line is looking forward, so a mixed line keeps its eagerness.
    """
    hits = list(A_CANT_WAIT.finditer(text))
    if not hits:
        return False
    left = text
    for hit in hits:
        left = left[:hit.start()] + " " + left[hit.end():]
    if LOOKING_FORWARD.search(left):
        return False
    working = bool(A_WORKING_DAY.search(text))
    for hit in hits:
        after = text[hit.end():]
        if A_WAITING_IN.match(after):
            continue
        if working and A_WAITING_FOR_A_TURN_UP.search(after):
            continue
        return False
    return True


def _looking_forward(clean):
    """True when the line is looking forward to something still to come."""
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return False
    if not LOOKING_FORWARD.search(text) or A_WAIT_FOR_A_LIFE_TO_END.search(text):
        return False
    if _the_wait_is_for_someone_to_turn_up(text):
        return False
    return not NOT_LOOKED_FORWARD_TO.search(text)


def _a_good_time(clean, memory=None):
    """True when the line reports a good time had by a group or by an event.

    A question is not a report ("was the wedding good"), and a "but" turns the line into a mixed
    one that the pools for trouble and feeling answer better. The positive word has to be there,
    so "the trip was cancelled" and "everyone there was awful" are left alone.
    """
    if "?" in clean or " but " in clean or " until " in clean:
        return False
    # The good-day shapes are anchored and name what happened ("i had", "today was", "great day
    # today"), so they are read before the question openers: "had a good day at work" opens with
    # a word from that list and is not a question, while "did you have a good day" still starts
    # with the "did" and stays out.
    if (GOOD_DAY_OURS.search(clean) or GOOD_DAY_WENT.search(clean)
            or GOOD_DAY_BARE.search(clean) or GOOD_TIME_IT.match(clean)):
        return True
    if _a_verdict(clean, memory):
        return True
    if (clean.split() or [""])[0] in QUESTION_OPENERS:
        return False
    if GOOD_TIME_OURS.search(clean):
        return True
    if not GOOD_TIME_SUBJECT.search(clean):
        return False
    return bool(set(re.findall(r"[a-z]+", clean)) & GOOD_TIME_WORDS)


# A film that was hilarious is a film, and the recommender has something to say about it ("For
# laughs: *What We Do in the Shadows*..."). The laugh pool would take the line first and hand back
# a question about it, which is a worse answer to somebody who has just named a film: they are
# telling the bot what they watched, and the bot knows some. "the show", "the book" and "the gig"
# are not in here - the recommender keys on film and movie, and for the rest the laugh is the
# better reply.
A_FILM = re.compile(r"\b(?:film|films|movie|movies|cinema|netflix)\b", re.I)


# A laugh that names harm is not a good day, even as hyperbole. "i laughed so hard i nearly killed
# myself" reads as a suicide line to every other pool in this file, and cheering it ("Ha - that
# good?") is the one reply nobody wants; the deck carries it under safety. The harm word is what
# makes it, not the death word: "i nearly died laughing" and "i laughed so hard i nearly died" are
# both a joke about the laughing, and they stay a laugh.
HARM_IN_A_LAUGH = re.compile(
    r"\b(?:kill(?:ed|ing|s)? myself|end(?:ed|ing)? my life|want(?:ed|s|ing)? to die|"
    r"suicid\w*|self[- ]harm\w*|overdos\w*|took (?:some |a load of )?pills?)\b", re.I)


# A laugh that has stopped is the opposite of a good day, and it is the one place where laughing
# back does harm: "my mum hasnt laughed in weeks", "nothing makes me laugh any more", "i dont
# laugh much these days" are a person telling the bot something is wrong, and LAUGHING matches the
# word in every one of them. Measured by chief-umbrella on 44 probe lines: this stands down the ten
# that are about not laughing and keeps every gain ("she made me laugh", "it had me in stitches",
# "i nearly died laughing"). It also stands down "nothing is funny any more" and "funny that the
# bus never came", which other tests already guard, so nothing is lost there. The cost is
# "i have never laughed so hard", where the honest reply is a nod rather than a cheer.
LAUGH_STOPPED = re.compile(
    r"\b(?:any ?more|any ?longer|these days|lately|never|hardly|used to|stopped|"
    r"in (?:weeks|months|years)|remember the last time)\b", re.I)


# Two shapes that are not a story, so "what set it off?" has nothing to be about: how somebody's
# laugh sounds ("she has a lovely laugh") and a general liking for laughing ("i love a good
# laugh"). Both are warm lines about laughing, not a report of one, and the pool's question is the
# wrong reply to them.
A_LAUGH_ITSELF = re.compile(
    r"\b(?:has|have|had|got)\s+(?:a|such a|the)\s+(?:very\s+|really\s+|proper\s+)?"
    r"(?:lovely|nice|great|good|infectious|loud|big|brilliant|wonderful|happy|silly)\s+laugh\b"
    r"|\bi\s+(?:love|like|adore|enjoy)\b[^.?!]{0,20}\b(?:a|good|a good|nothing better than a)"
    r"\s+laugh\b"
    r"|\bnothing (?:beats|better than) a good laugh\b", re.I)


# A laugh in the room is not the person's laugh. "i fell over and everyone laughed", "i made a
# fool of myself and they laughed" and "i tripped and they all laughed" were all answered "Ha -
# that good? Tell me the best bit.", which joins in with a laugh that was at the person: it is the
# same fault the "laughed at" list catches, said without the "at". A room word as the subject of
# the laugh is that, unless the line also has the person's own laugh in it - "my friends and i
# laughed for hours" keeps the pool, and so does "the kids made me laugh".
A_ROOMS_LAUGH = re.compile(
    r"\b(?:everyone|everybody|they|all of them|the (?:others|rest|group|kids|class|crowd|family)|"
    r"my (?:mates|friends|sisters?|brothers?|mum|dad|husband|wife|partner|boyfriend|girlfriend|"
    r"boss|colleagues|coworkers|workmates|family))\b(?:\s+[\w']+){0,3}\s+"
    r"(?:laughed|laugh|laughing|giggled|giggling)\b", re.I)


A_OWN_LAUGH = re.compile(
    r"\b(?:i|we|me|us)\b(?:\s+[\w']+){0,2}\s+"
    r"(?:laughed|laugh|laughing|giggl(?:ed|ing)|in stitches|creased up)\b|"
    r"\b(?:made|makes|make|had) me laugh\b", re.I)


def _something_funny(clean, memory=None):
    """True when the line says something was funny and nothing in it says a problem.

    A question is not a report ("was that funny"), a "but" turns it into a mixed line the pools
    for trouble and feeling answer better, and being laughed at is not a good day.
    """
    if "?" in clean or " but " in clean:
        return False
    if LAUGHING_AT.search(clean):
        return False
    if A_FILM.search(clean):
        return False
    if HARM_IN_A_LAUGH.search(clean):
        return False
    if LAUGH_STOPPED.search(clean):
        return False
    if A_LAUGH_ITSELF.search(clean):
        return False
    if A_ROOMS_LAUGH.search(clean) and not A_OWN_LAUGH.search(clean):
        return False
    if isinstance(memory, dict) and _in_a_care_thread(memory):
        # "my father died on tuesday" then "we laughed about it afterwards" is the memory of a
        # funeral, not a good day: the care thread's own reply is right and a cheer is not.
        return False
    return bool(LAUGHING.search(clean))


# An apology for stepping away is easy to mistake for an apology about a fault. Only the absence
# after the "sorry" makes it this shape, and what they went to do has to be a small errand, so
# "sorry i crashed the car" and "sorry for your loss" keep their own replies.
# A mistake is not an absence: "sorry i went to the wrong house" is the person telling me something
# went wrong, so "i went" only counts when what follows is the errand or the place they were away
# from. gray-palm measured the loose version taking "sorry i went to the wrong house" and answering
# "No bother at all - go on." to a line that had news in it.
STEPPED_AWAY = re.compile(
    r"\b(?:sorry|apologies)\b[^.?!]{0,30}\b(?:i went (?:to (?:get|grab|pick|fetch|answer|"
    r"check|put|sort|deal|make|do)\b|for\b|away\b|out\b|off\b)|i had to go\b|"
    r"to get (?:the|my|some)\b|to pick (?:up )?(?:the|my)\b|for a (?:min|minute|sec|second|"
    r"bit|moment)\b|i'?ve been away|i was gone)\b"
    r"|\b(?:sorry|apologies) (?:i|for) (?:disappeared|vanishing|going quiet|being away)\b"
    r"|\b(?:sorry|apologies)\b[^.?!]{0,40}\b(?:i was (?:away|asleep|out|busy|driving|"
    r"in a meeting|on a call|at (?:work|school|uni))|slow (?:reply|response)|late (?:reply|"
    r"response)|the delay)\b"
    r"|\b(?:sorry|apologies) (?:i|that i) (?:missed|didn'?t (?:see|get)) (?:your|that) "
    r"(?:message|reply|text)\b"
    # The wait itself is the same apology as the silence, and it was the one shape that missed
    # the pool: "sorry for the wait" and "sorry i took so long" got the stock nod, and "sorry im
    # late replying" got advice on writing the email. These words are about the answer taking a
    # while, so they say nothing about being late for anybody.
    r"|\b(?:sorry|apologies)\b[^.?!]{0,30}\b(?:for the wait|the wait|kept you waiting|"
    r"took (?:me )?(?:so|a while)|took so long|late replying)\b")


# The errand is not the only way to be drawn away: the person was distracted, waylaid, pulled
# away or sidetracked, and "Noted: you got distracted." is what the store filed it as. This
# shape needs no apology in front, because "i got distracted" in the middle of a chat is the
# whole content of the line too, and the pool below is what a friend answers it with.
GOT_DRAWN_AWAY = re.compile(
    r"\b(?:got|get|was|been)\s+(?:a\s+(?:bit|little)\s+|a bit\s+|totally\s+|completely\s+)?"
    r"(?:distracted|waylaid|sidetracked|side-tracked|pulled\s+away|dragged\s+away|"
    r"called\s+away|taken\s+away)\b"
    r"(?:\s+(?:by|with)\s+(?:a|the|some|my|an)?\s*[a-z']{2,12})?"
    r"|\b(?:got|get|was|were|been)\s+(?:talking|chatting)\s+to"
    r"(?:\s+(?:a|the|some|my|his|her|our)\s+[a-z']{2,12})?"
    r"|\b(?:got|get)\s+caught\s+up\s+with(?:\s+(?:a|the|some|my|an)\s*[a-z']{2,12})?")


# The words that turn the page: whatever follows one of these is the next subject, not the
# reason for the gap.
A_TURN_THE_PAGE = re.compile(
    r"\b(?:anyway|anyways|but|oh|also|by\s+the\s+way|while\s+i'?m\s+here|"
    r"quick\s+question|separate\s+thing|other\s+thing)\b")


# A stretch away because of an illness is the same reason for the gap, and it names nothing the
# bot can answer on its own: "sorry for the silence, i had the flu" was answered "Sounds alright.
# Anything good in it?" - a line about a film nobody mentioned, to somebody explaining a fortnight
# of silence. The same for the reason arriving as a person: "sorry i went quiet, my mum was ill"
# is an apology, not a confession to be coached.
A_GAP_FOR_ILLNESS = frozenset("""
    flu cold covid bug virus infection ill sick unwell poorly worse hospital operation surgery
    migraines migraine headache bereavement funeral grieving grief depressed depression anxiety
    burnout recovery recovering recovered injury injured broken sprained test scan results
    doctor doctors gp a&e sleep sleepless insomnia
""".split())


# The reason can be a person: "sorry i went quiet, my mum was ill" is the gap and an ill relative,
# not a confession to be coached through ("Name what you did, say why it was wrong"). A person
# named beside a reason is part of the reason, so the words that name one may be left over - but
# only with a reason word beside them, never on their own.
A_GAP_NAMED_PERSON = frozenset("""
    mum mom mother mum's dad father dad's sister brother gran grandad grandma grandpa nan nana
    son daughter wife husband partner boyfriend girlfriend fiance fiancee kids children child
    baby family friend mate aunt uncle cousin mother-in-law father-in-law in-laws
""".split())
