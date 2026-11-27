"""Part 3 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import stuck as stuck_line
from . import (badnews, goodnews)

from .fallback_data import (
    BODY_PARTS,
    CLOSED_DOOR,
    DETAILS_IN_A_WARM_LINE,
    HEALTH_WORDS,
    HUMAN_EMPTY,
    NAMED_NEGATIVE,
    NEGATIVE,
    NOT_A_NAME,
    OCCASION,
    SOMEONE_ELSES_DAY,
    SYMPTOM_WORDS,
    _NOT_AN_OWN_THING,
    _THREAD_PEOPLE,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    BARE_PICK_LOST,
)
from .fallback_part_01 import (
    A_SUBJECT_ABOVE,
)
from .fallback_part_02 import (
    LOOKED_UP,
)


def _a_subject_above(memory):
    """True when the line before this one named something of theirs for the stuck line to be about."""
    if not isinstance(memory, dict):
        return False
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return False
    return bool(A_SUBJECT_ABOVE.search(str(turns[-1].get("user") or "").lower()))


def _thread_is_about_a_person(memory, look_back=4):
    """True when the last few things the person said named someone else."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in turns[-look_back:]:
        words = set(re.findall(r"[a-z']+", (turn.get("user") or "").lower()))
        if words & _THREAD_PEOPLE or REPAIR_PERSON.search(turn.get("user") or ""):
            return True
    return False


def _names_its_own_thing(clean):
    """True when the repair line names the thing it is about, so the thread is not the subject.

    "is it worth fixing" names nothing and belongs to the thread. "is it worth fixing the garden
    gate" names the gate, and a gate is not the person the thread was about.
    """
    match = REPAIR_DECISION.search(clean)
    if not match:
        return False
    for word in re.findall(r"[a-z']+", clean[match.end():]):
        if word in _NOT_AN_OWN_THING:
            continue
        if word in BODY_PARTS or word in HEALTH_WORDS or word in SYMPTOM_WORDS:
            continue
        if REPAIR_PERSON.search(word):
            continue
        return True
    return False


# The same evening, asked about one more step along: not whether the bot saw it, but a detail of
# it put to somebody who might have been there. "were jess and tom there", "did she like it", "who
# else was there", "was the food good" have no lookup behind them - the afternoon happened to the
# person - so the search hedge ("a quick search online will get you a solid answer") sent them to
# the internet to find out about their own day. The bot was not there, says so in as many words,
# and asks the question that gets the story (`WASNT_THERE`).
WAS_THEY_THERE = re.compile(
    r"^[^a-z]*(?:was|were)\s+(?:he|she|they|everyone|anyone|anybody|everybody|you|u)\s+"
    r"(?:there\b|at\s+\w|with\s+\w)")


WAS_A_NAMED_ONE_THERE = re.compile(
    r"^[^a-z]*(?:was|were)\s+(?P<who>[a-z][a-z'-]*)"
    r"(?:\s+and\s+(?P<also>[a-z][a-z'-]*))?\s+there\b")


# "did she like it", "did they enjoy it", "did he make it". "have" is left out on purpose: "did
# you have a good day" is small talk aimed at the bot, not a question about somebody's afternoon.
DID_THEY_GO = re.compile(
    r"^[^a-z]*(?:did|do|does)\s+(?:he|she|they|you|u)\s+"
    r"(?:like|enjoy|love|hate|go|come|make it|get there|stay|leave|arrive|say|think|"
    r"manage|turn up|show up|win|win it|lose|lose it|draw|score|play well|do well)\b")


# What an opinion of something that already happened is said with: "did you think it was good",
# "did you think the film was any good", "do you think she liked it". Without one of these after
# "do you think", the line is asking whether the bot agrees with a plan or a feeling.
# A look back at something that happened still needs something to look back at: a person who was
# there ("she liked it", "they played well") or a thing that was ("the food was ok", "my mum liked
# it"). Without one the line is about their own conduct - "do you think it was my fault", "do you
# think that was a mistake" - and the day-they-were-at reading answered it with a room the bot was
# never in.
A_THING_OR_A_PERSON = re.compile(
    r"\b(?:he|she|they|we|us|him|her|them|the|my|our|his|their)\s+\w+")


A_LOOK_BACK = re.compile(
    r"\b(?:was|wasnt|wasn't|were|werent|weren't|had|hadnt|hadn't|did|didnt|didn't|"
    r"liked|enjoyed|loved|hated|went|came|said|managed|stayed|left|arrived|won|lost|scored|"
    r"turned up|showed up|played|worked)\b")


# A detail asked of the thing rather than of a person: "was the food good", "was it busy",
# "was everything alright".
WAS_IT_ANY_GOOD = re.compile(
    r"^[^a-z]*(?:was|were)\s+(?:it|that|everything|everyone|the\s+\w+|my\s+\w+|your\s+\w+|"
    r"his\s+\w+|her\s+\w+|their\s+\w+|our\s+\w+)\s+"
    r"(?:good|nice|busy|packed|fun|loud|quiet|worth it|any good|any cop|a laugh|any fun|"
    r"alright|all right|ok|okay|terrible|awful|great)\b")


# The same detail about the people who went, named as a group: "were your parents there",
# "did the kids have fun", "were the neighbours there". The noun has to be a person in the line,
# so "were the plates there" and "was the car there" are not read as this.
PEOPLE_WHO_WENT = frozenset("""kids children child parents mum mom dad mother father family
friends friend sister brother wife husband partner boss neighbours neighbors cousins
grandparents grandmother grandfather aunt uncle colleagues classmates team group others
lot guests everyone""".split())


WENT_AND_WERE_ASKED = re.compile(
    r"^[^a-z]*(?:was|were|did)\s+(?:my|your|his|her|their|our|the)\s+(?P<noun>\w+)\s+"
    r"(?:there|about|around|have|enjoy|like|come|go|stay|leave|arrive|make it|get there|say)\b")


WHO_WAS_THERE = re.compile(
    r"^[^a-z]*(?:who\s+else|who|anyone else|anybody else)\s+"
    r"(?:was|were|went|came|turned up|showed up|there)\b")


# A question about somebody being hurt is not a question about how the day went: "did he hit you"
# is the safety pools' and never this one.
HURT_IN_THE_LINE = re.compile(
    r"\b(?:hit|hits|hurt|hurts|touch|touched|hands? on|force|forced|push|pushed|shove|shoved|"
    r"grab|grabbed|threaten|threatened|threat|abuse|abusive|shout|shouted|yell|yelled|"
    r"corner|cornered)\b")


# The words that are never a name in "were X there": determiners, pronouns and the ordinary nouns
# that sit in that slot. Both halves of "jess and tom" have to be names, so "were the plates
# there" and "was it there" are not read as people.
NOT_A_NAME = frozenset("""it that this these those there here the a an any some every no not
everything nothing something anything anyone anybody everyone everybody somebody someone
he she they you u we i him her them us me my your our their his its one ones thing things
day night week weekend time food meal party wedding dinner lunch trip holiday service drive
journey flight train bus match game film show weather traffic lunch tea supper""".split())


def _asked_about_the_day_they_had(clean):
    """True when the line asks a detail of something the person was at, as if the bot were there.

    "were jess and tom there", "did she like it", "who else was there", "was the food good" -
    every one of them is about a room the bot was not standing in, so there is nothing to look
    up. A line about the news, the weather, prices or a score keeps its own pools: those really
    can be searched for.
    """
    if HURT_IN_THE_LINE.search(clean) or LOOKED_UP.search(clean):
        return False
    if WAS_THEY_THERE.match(clean) or WAS_IT_ANY_GOOD.match(clean) or WHO_WAS_THERE.match(clean):
        return True
    went = DID_THEY_GO.match(clean)
    if went:
        # "do you think" is the same words in two different asks: "did you think the film was any
        # good" asks for an opinion of something that happened, and "do you think i should tell
        # her" asks whether the bot agrees with a plan. Reading the second as the first told a
        # person "I wasn't there, so I can't say - I only know what you tell me. How did it go?"
        # about their own decision, and the same thing happened to "do you think i should go to
        # the doctor", "do you think they will come" and "do you think im too old to start". So
        # "think" counts only where a look back at something that already happened is in the
        # line, and every other verb in the list ("did you like it", "were they there") is
        # already about the day itself.
        verb = clean[went.start():went.end()].rstrip()
        if verb.endswith("think"):
            # "did you think" is already in the past, so the line is a look back whatever follows
            # it ("did you think id like it"). "do you think" is the ask that could be either, and
            # only the look-back words settle it.
            if verb.startswith("do") or verb.startswith("does"):
                said = clean[went.end():]
                if not A_LOOK_BACK.search(said) or not A_THING_OR_A_PERSON.search(said):
                    return False
        return True
    if WENT_AND_WERE_ASKED.match(clean) and WENT_AND_WERE_ASKED.match(clean).group("noun") in PEOPLE_WHO_WENT:
        return True
    named = WAS_A_NAMED_ONE_THERE.match(clean)
    if not named:
        return False
    who = named.group("who")
    also = named.group("also")
    if who in NOT_A_NAME or (also and also in NOT_A_NAME):
        return False
    return True


# A bare ask to choose has no answer until it knows what for. "what should i wear" sent the
# person to a search engine, which is a shrug on a question a friend answers with one question
# back - and the same seven words with a subject ("what should i wear to a wedding") already have
# an entry of their own, so the only lines left here are the ones that name the choosing and
# nothing to choose between. "what should i do" is that shape too, and it is the widest ask in
# English: not a fact nobody has, but a person asking for a hand. The verb is the only thing the
# line gives, so the verb picks the pool; nothing here names a subject the line did not have.
# The modal is the whole difference between a person asking for a hand and a person asking for
# nothing: "what can i do" is the commonest way to say it, and it was the one wording the list
# did not hold, so it went to the search shrug while "what should i do" got the offer. "can",
# "could" and "might" are the same ask, and the verb and the tail guard still keep every line
# that names something ("what can i do about my leaking roof", "what can i get for tea") out.
BARE_PICK = re.compile(
    r"^\s*(?:(?:so|and|but|ok|okay|well|then|just|hey|hi|right|anyway|anyways|oh|hmm|yeah|"
    r"yes|alright|honestly|you\s+know)[\s,]+)*"
    r"(?:what|which)\s+(?:should|shall|do|would|can|could|might)\s+i\s+"
    r"(?P<verb>wear|put\s+on|buy|get|do|take|bring|look\s+(?:for|at)|expect|ask|sign|"
    r"order|prepare)\b"
    r"(?:\s+(?:now|today|tonight|tomorrow|instead|else|next|then))?\s*\??\s*$", re.I)


# A lost ask in a conversation that has already said what it is about ("my week has been
# rubbish" / "work is the worst bit" / "i dont know what to do about it") must not ask for the
# story again: the offer the bare pool makes ("tell me what has gone on") is a bot asking a
# person to start over, which reads worse than the placeholder it replaced. What a friend says is
# "it" - the thing already on the table - and the one question that cuts it down.
LOST_IN_A_THREAD = (
    "Then the useful question is which part of it is actually yours to move. Which part could you "
    "change this week?",
    "It usually breaks into smaller pieces once they have names. What is the smallest of them "
    "that would make tomorrow easier?",
    "You have said the whole of it already, so I will not ask again. Which bit of it would you "
    "want to have sorted by Friday?",
)


# "what should i do first" is the same ask in the question form, and it lands at a different
# door: with nothing before it the words reach the search hedge (nothing in them names a fact),
# and in a thread they are a step through advice already given. So it is read with the lost ask,
# where a thread that has advice is left alone, and not with the bare picks, which would ask a
# person who has just said what is wrong to say it all again.
BARE_PICK_LOST_FIRST = re.compile(
    r"^\s*(?:(?:so|and|but|ok|okay|well|then|just|hey|hi|right|anyway|oh|hmm|yeah|yes|alright|"
    r"honestly|tbh)[\s,]+)*"
    r"(?:what|which)\s+(?:should|shall|do|would|can|could|might)\s+i\s+do\s+"
    r"(?:first|next)\s*\??\s*$", re.I)


def _a_lost_ask(clean):
    """True for the bare "i dont know what to do" family: nothing named, a hand asked for."""
    clean = clean or ""
    return bool(BARE_PICK_LOST.match(clean) or BARE_PICK_LOST_FIRST.match(clean))


# The same ask with the first step as its object: "i dont know where to start", "no idea where
# to begin", "where do i even start". It is the widest way to ask for a hand after the bare "what
# should i do", and it names nothing at all - not the list, not the thing, not the day. Main has
# one answer for it, the size-of-the-list question ("what is the one thing that cannot slip?"),
# which needs a list the line never gave, and since the stuck reader learned to stand aside for a
# line with no list above it, the bare ask has had nothing but the placeholder ("I'm listening -
# say more if it helps"). What a friend hands over is the way to pick the first thing, which is
# the whole of what "where to start" is asking.
_START_ASK_BODY = (
    r"(?:"
    # "i dont know where to start" and the other ways of saying the not knowing.
    r"(?:i\s+)?(?:really\s+|honestly\s+|genuinely\s+|actually\s+|still\s+|simply\s+|"
    r"just\s+|even\s+)*"
    r"(?:"
    r"(?:do\s+not|don'?t|dont)\s+(?:even\s+)?know"
    r"|dunno"
    r"|(?:have|ve|got|i'?ve)\s+(?:absolutely\s+)?no\s+(?:idea|clue)"
    r"|(?:have\s+)?no\s+(?:idea|clue)"
    r"|(?:i\s+am\s+|i'?m\s+)?not\s+(?:really\s+|too\s+)?sure"
    r")\s+where\s+to\s+(?:start|begin)"
    # ...the question form, which is the same ask with a question mark on it...
    r"|(?:where|how)\s+(?:do|should|shall|can|could|would)\s+(?:i|we)\s+(?:even\s+)?"
    r"(?:start|begin)"
    # ...and the two words on their own.
    r"|where\s+to\s+(?:start|begin)"
    r")"
    # The words people put after it that add nothing the pool has to read. A subject after it
    # ("where to start with the loft", "where do i start on the cv") is not this line: that one
    # names a thing, and the thing has an answer of its own.
    r"(?:\s+(?:now|next|first|today|tonight|tomorrow|at\s+all|anymore|any\s+more|"
    r"with\s+(?:it|this|that|them)|on\s+(?:it|this|that)))?")


_START_ASK_LEAD_IN = (
    r"(?:(?:so|and|but|ok|okay|well|then|just|hey|hi|right|anyway|anyways|oh|hmm|yeah|"
    r"yes|alright|honestly|god|christ|ugh|tbh|seriously|you\s+know)[\s,]+)*"
    r"(?:(?:the\s+thing\s+is|the\s+problem\s+is|thing\s+is|truth\s+is|see|look|i\s+mean)"
    r"[\s,]+)*")


BARE_PICK_START = re.compile(
    r"^\s*" + _START_ASK_LEAD_IN + _START_ASK_BODY + r"\s*\.?\s*$", re.I)


# The same ask with a clause in front of it: "we've moved to a new place and i dont know where to
# start" is one sentence with two halves, and the half that asks for the hand is the second one.
# Only where the two are joined ("and", "but", a comma): a line that names the thing it wants to
# start on and then asks keeps its own answer, because the subject is the thing before it.
BARE_PICK_START_CLAUSE = re.compile(
    r"\b(?:and|but)\s+" + _START_ASK_LEAD_IN + _START_ASK_BODY + r"\s*\.?\s*$", re.I)


def _a_start_ask(clean):
    """True for the bare "i dont know where to start" family: nothing named, the first step asked for."""
    clean = clean or ""
    return bool(BARE_PICK_START.match(clean) or BARE_PICK_START_CLAUSE.search(clean))


def _said_what_it_is_about(memory):
    """True when a line before this one gave a reply something to name.

    "hi" then "i dont know what to do" is a first ask with nothing behind it, and the thread pool
    would answer it with "which part of it", pointing at nothing. Three words of content in the
    last two lines is the line the pools draw.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in turns[-2:]:
        said = " ".join(str(turn.get("user") or "").lower().split())
        if len([w for w in said.split() if len(w) > 2]) >= 3:
            return True
    return False


# The first step, for the ask whose object is the first step. A line that says "where to start"
# has not given a list and has not given a thing, so no pool can name either: what it gets is the
# way to pick one thing, which is the pool the memory store's "i dont know what to do" after
# nothing at all already answers with (bot/memory/stuck.HARD). One pool, two doors, so the same
# line does not get two voices: the chat module answers the bare ask before this file sees it, and
# this is what a start-ask with a clause in front of it reaches.
START_ASK = stuck_line.HARD


# The wear pool asks and does not dress anybody: a bare "what should i wear" has not said the
# day, and a line that assumes one ("standing about, sitting on grass, a long service") answers
# a wedding nobody mentioned and walks straight past `its cold out`, which is the one thing the
# person did say. What is left is the question a friend asks first. The pool itself lives in
# `fallback_data` with the hot, cold and wet ones, and is imported above: a second definition
# here shadows that import, and `BARE_PICK_KIND` hands back the imported tuple, so the
# `pool is BARE_PICK_WEAR` tests below were comparing two different objects and the weather
# pools could never fire.
# The weather the person already told the listener decides more of it than the mirror does, and
# `its cold out / what should i wear` ignoring the cold is the reply of somebody who was not
# listening. Only a weather line counts, not a body: "i have a cold" and "i feel hot" are the
# other modules' lines, so the hot and cold ones want the it-is shape.
WEATHER_COLD = re.compile(
    r"\b(?:freezing|chilly|freezing cold|bitterly cold|snowing|snow|frost|icy)\b|"
    r"\b(?:it'?s|its|it is|very|so|really|too|dead|bloody)\s+(?:a bit\s+|quite\s+)?cold\b",
    re.I)


WEATHER_HOT = re.compile(
    r"\b(?:boiling|scorching|roasting|heatwave|muggy|humid)\b|"
    r"\b(?:it'?s|its|it is|very|so|really|too|dead|bloody)\s+(?:a bit\s+|quite\s+)?"
    r"(?:hot|warm)\b", re.I)


WEATHER_WET = re.compile(r"\b(?:raining|pouring|drizzle|drizzling|wet out|showers|storm)\b",
                         re.I)


# A heavy line before a bare ask: the person has already said the thing the ask is about.
# "what should i do" is the widest ask in English when it comes out of nothing, and after a
# death or a scare it is a request for help with what was just said - "tell me what has gone
# on" then asks a bereaved person to say the death again, and "the order of the next two
# things" is a to-do list in front of a scare. The words here are only the ones the readings
# above do not already hold (`loss.reads_as_loss` has the deaths, `reads_as_bad_news` has the
# diagnoses): a lump, a body in a hospital bed, someone very ill.
HEAVY_ABOVE = re.compile(
    r"\b(?:lump|lumps|tumou?r|cancer|leuka?emia|lymphoma|melanoma|dementia|alzheimers|"
    r"motor neurone|parkinsons|ms|chemo|chemotherapy|radiotherapy|palliative|hospice|"
    r"terminal(?:ly)?|very ill|really ill|seriously ill|dangerously ill|intensive care|"
    r"life support|stillborn|stillbirth|meningitis|sepsis)\b", re.I)


# Bad news about work or money is bad news, and it is not the news a bare ask is asking about:
# "i lost my job" then "what should i do" is somebody asking for a hand with something they have
# only half said, which is exactly what the ask pool is for. The losses of a person, a body and a
# diagnosis stand the ask down; a job does not.
WORK_NEWS = re.compile(
    r"\b(?:job|jobs|work|hours|shift|shifts|money|pay|wages|salary|contract|business|"
    r"redundant|redundancy|clients?|customers?|interview|mortgage|rent|loan|debt|"
    r"benefits?|savings?)\b", re.I)


def _weather_above(memory):
    """The weather the person named in the last two lines, as "cold", "hot", "wet" or None."""
    if not isinstance(memory, dict):
        return None
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(turns[-2:]):
        said = str(turn.get("user") or "")
        if not said:
            continue
        if WEATHER_WET.search(said):
            return "wet"
        if WEATHER_COLD.search(said):
            return "cold"
        if WEATHER_HOT.search(said):
            return "hot"
    return None


# An occasion the thread already named is the composer's own entry ("what should i wear to a
# wedding" has a real answer), so a bare ask only stays bare when the thread did not say one.
OCCASION_ABOVE = re.compile(
    r"\b(?:wedding|funeral|christening|baptism|interview|party|dinner|date|work|office|"
    r"conference|concert|festival|exam|graduation|church|meal out|night out)\b", re.I)


def _an_occasion_above(memory):
    if not isinstance(memory, dict):
        return False
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    return any(OCCASION_ABOVE.search(str(turn.get("user") or "")) for turn in turns[-2:])


# The pool asks what the day is. A line that has already said - in the clause in front of its ask -
# which day it is, or has named an occasion, has answered that question, and asking it back reads as
# a bot that was not listening: "i start at the new place on monday, what should i wear" was offered
# "tell me what the day is - work, a meal out, a long walk". Nothing is added to what the pool can
# answer here: the line stands down, and whatever it had without the pool it still has.
THE_DAY_IS_NAMED = re.compile(
    r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|"
    r"\b(?:next|this|that|the) (?:week|weekend)\b|"
    r"\b(?:tomorrow|tonight|today)\b|"
    r"\b(?:in|on|by|for|until) (?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b", re.I)


# The same occasions as `OCCASION_ABOVE`, plus the ways a thread names one without the word:
# "my sister is getting married in june" and "im going to be a bridesmaid" are a wedding, and the
# four-turn window needs them to see it. Read only by the branch below, so a word that is not here
# costs nothing but the day the pool would have asked about.
AN_OCCASION_AHEAD = re.compile(
    r"\b(?:wedding|funeral|christening|baptism|interview|party|dinner|date|work|office|"
    r"conference|concert|festival|exam|graduation|church|meal out|night out|"
    r"getting married|get married|got married|marrying|engaged|engagement|"
    r"bridesmaid|bridesmaids|best man|maid of honour)\b", re.I)


def _an_occasion_in_the_thread(memory, back=4):
    """An occasion named a few turns back, which the pool's own question would ask about again.

    `_an_occasion_above` is the two-turn window the wear pool has always used. A thread that
    opened the occasion and then talked about something else has still had it: "my sister is
    getting married in june" / "im going to be a bridesmaid" / "what should i get her" / "back to
    the wedding, what should i wear" was asked where the day is, which the conversation said
    four turns earlier.
    """
    if not isinstance(memory, dict):
        return False
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    return any(AN_OCCASION_AHEAD.search(str(turn.get("user") or "")) for turn in turns[-back:])


# A trip in the thread is the one case where the packing line is the right answer to a bare ask:
# a place, a holiday, a flight or a night away, and "im going to cornwall in july", which names
# no trip word at all. A going-to followed by a verb ("going to have a bath", "going to try
# again", "going to see my mum") or by a place down the road is not a journey.
TRIP_ABOVE = re.compile(
    r"\b(?:holiday|holidays|hols|trip|trips|away|abroad|flight|flights|flying|hotel|"
    r"camping|campsite|backpacking|weekend away|days? away|mini ?break)\b|"
    r"\b(?:go|going|went|off|flying|driving|heading)\s+(?:to\s+|off\s+to\s+)?"
    r"(?!the\b|a\b|an\b|my\b|his\b|her\b|their\b|our\b|your\b|work\b|bed\b|sleep\b|"
    r"school\b|uni\b|university\b|college\b|town\b|hospital\b|doctor\b|dentist\b|"
    r"shop\b|shops\b|toilet\b|loo\b|bath\b|shower\b|"
    r"have\b|get\b|see\b|be\b|do\b|make\b|take\b|try\b|need\b|want\b|start\b|stop\b|"
    r"give\b|put\b|keep\b|stay\b|look\b|ask\b|tell\b|say\b|ring\b|call\b|text\b|"
    r"eat\b|drink\b|cook\b|clean\b|wash\b|sort\b|finish\b|leave\b|come\b|meet\b)"
    r"[a-z]{3,}", re.I)


def _a_trip_above(memory):
    """True when the last two lines the person sent said they were going somewhere."""
    if not isinstance(memory, dict):
        return False
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    return any(TRIP_ABOVE.search(str(turn.get("user") or "")) for turn in turns[-2:])


# These verbs are missing their object, so the pool asks for it - but only when there is nothing
# on the table. "my toddler has a fever and a rash" / "what should i look for" wants the signs to
# watch for, and "looking at what - a car, a flat, a phone?" is worse there than the shrug this
# pool was built to replace. With a subject above, the turn stays with the follow-up readers.
BARE_PICK_NEEDS_THE_THING = frozenset({"look for", "look at", "expect", "ask", "sign",
                                       "order", "prepare"})


# The last line the person sent named nothing to answer: a greeting or an acknowledgement. The
# words here are the whole of a line that is not a subject, so "my son is 8" is a subject (son)
# and "ok then" is not.
THREAD_NOTHING = frozenset("""
    hi hey hello morning evening there so and but ok okay well right yeah yes yep no not im i the
    a an it that this to for of in on at is was just also thanks thank please good great fine
    alright anyway oh hmm mm me my u you your cheers ta now then today tonight
""".split())


def _a_subject_above(memory):
    """True when the last line the person sent named a thing, so a bare ask is a follow-up."""
    if not isinstance(memory, dict):
        return False
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in turns[-2:]:
        said = str(turn.get("user") or "")
        if not said.strip():
            continue
        words = re.findall(r"[a-z']+", said.lower())
        if any(word.strip("'") not in THREAD_NOTHING and len(word) > 2 for word in words):
            return True
    return False


# The ask is the last thing on the line, and everything in front of it is the setting. The
# pattern above is anchored to the whole line so that a line naming its own subject keeps its own
# answer, and a subject sits in front of an ask as easily as behind it: "what should i wear to a
# wedding" has an entry of its own and never reaches here, while a clause saying what the person
# has been doing - "for the first time in years, what should i wear", "in years, what should i
# wear" - was shrugged at, though the ask in it is as bare as the seven words that get the pool.
# A friend reads the clause and then answers the ask, so the pool is tried on the whole line and,
# when the line put something in front of the ask, on the ask it ends with. Nothing new is read:
# the reading hands the ask over as `focus`, and the clause split is only worked out again when
# the caller has no reading to hand (a test, or a repaired line).
_AFTER_A_CLAUSE = re.compile(
    r"(?:[,;:]\s+|\s+(?:and|but|so|because|though|although|while|when|now)\s+)"
    r"((?:what|which|how|where|who|when)\b[^,;:?!]*)\s*\??\s*$", re.I)


# "who do i call about it", "who do i ring first", "who should i get to look at it": the person
# wants a name to take a thing to, and the thing itself was named a turn ago, so the line holds
# nothing to read. Every one of them reached the search hedge, which tells somebody to go and look
# up their own problem - the one thing a search cannot do. The thread still has two things to
# read: the line that named the trouble, and the answer the bot has just given, which usually
# names the actor ("report it to the council the same day"). Where neither names anybody the
# honest reply is the route list and one question, not a shrug.
# These patterns live in their own file: this one grew past the 1 MB a clone may carry and
# every change to it was refused. Imported here in place of their definitions.
from .fallback_words import (  # noqa: F401 - read here by the patterns below
    A_PERSON_IN_A_CRISIS,
    CRISIS_ASK,
    HUMAN_ASK,
    HUMAN_HELPS,
    HUMAN_LEAD,
    HUMAN_QUOTED,
    HUMAN_TAIL,
    NAMES_THE_BOT,
    PRIVACY_NOT_THIS,
    REFERS_BACK,
    REPAIR_DECISION,
    LEAVING_IN_THE_LINE,
    REPAIR_BARE_IT,
    REPAIR_PERSON,
    REPAIR_TARIFF,
    REPAIR_TRADE,
    REPAIR_WHAT_IT_IS_WORTH,
    REPAIR_WHETHER,
    SELF_ASK,
    A_VIEW_ASKED_FOR,
    TRUST_ASK,
    WHO_FOR_IT,
    WHO_FOR_IT_BODY,
    WHO_FOR_IT_ROUTES,
    WHO_FOR_IT_SAID,
    WHO_FOR_IT_SAID_VOICE,
    WHO_NAMED_BEFORE,
    WHO_TO_TALK_ASK,
    WHO_TO_TALK_TO,
    WHO_TO_TALK_TO_A_BAD_STRETCH,
)


def _opens_the_line(prefix):
    """True when what comes before the human/person ask is only a greeting or a question opener."""
    return bool(HUMAN_LEAD.match(prefix)) or bool(HUMAN_QUOTED.search(prefix))


# The same question asked as a request for a person to deal with: "can i speak to a real person",
# "is there a real person i can talk to", "can i talk to a human please", "get me a human",
# "i need to talk to a human", "any chance of an actual human here". `HUMAN_ASK` read only the
# three shapes where the person asks what it is talking to, and the request shapes all reached a
# shrug or a change of subject - on main "can i speak to a real person" got "I'm not sure about
# that one, sorry - I'd rather not guess. A quick search online will get you a solid answer".
#
# The words are also how a person names somebody else, so the gates are the strict ones, not
# `_asks_elsewhere`: the ask opens the line, and what follows is nothing, a "please"/"here", the
# asker ("... i can talk to") or this end of the chat ("on the other end"). A tail that names
# what they want the person for ("... about my grief", "... about my refund") is a line the
# entries and the grief module answer, and those keep it - `HUMAN_HELPS` reads "i can talk to
# about ..." as the bot being asked for a hand, which is right for "is this a real person who can
# help with my ticket" and wrong here.
HUMAN_TALK_ASK = re.compile(
    r"\b(?:can|could|may|might) i (?:please )?(?:speak|talk|chat) (?:to|with) "
    r"(?:a |an |a real |an actual |some )*(?:human being|actual human being|real human being|"
    r"human|person|real person|actual person|actual human|real human)\b|"
    r"\b(?:i )?(?:want|need|would like|wanna|have) to (?:speak|talk|chat) (?:to|with) "
    r"(?:a |an |a real |an actual )*(?:human being|actual human being|real human being|human|"
    r"person|real person|actual person|actual human|real human)\b|"
    r"\bis there (?:a |an |any )?(?:real |actual )?(?:human being|actual human being|human|"
    r"person|someone real|somebody real)\b|"
    r"\b(?:get|give) me (?:a |an )?(?:real |actual )?(?:human|human being|person)\b|"
    r"\b(?:any|got any|got a) (?:chance of )?(?:a |an )?(?:real |actual )?(?:human|human being|"
    r"person)\b|"
    r"\b(?:real|actual) (?:human|person|human being) (?:here|on here|around|available)\b")


# A tail that names the asker rather than another person: "is there a real person i can talk to",
# "someone real i could speak with", "a human being i can ask".
HUMAN_TO_ME = re.compile(
    r"^\s*(?:that |who |which )?(?:i|we) (?:can|could|may|might|would|should|will)?\s*"
    r"(?:talk|speak|chat|ask|write)\s*(?:to|with)?\s*(?:you|u)?\s*"
    r"(?:please|pls|now|first|then)?\s*[.!?]*\s*$")


# "is there a real person on the other end": the tail names this end of the chat, which is the
# question `HUMAN_ASK` already reads as its own ("real person on the other end").
HUMAN_OTHER_END = re.compile(r"^\s*(?:on|at) the other (?:end|side)\b[^a-z]*$")


def _asks_elsewhere(tail):
    """True when what comes after the human/person words asks about somebody other than us."""
    if HUMAN_HELPS.match(tail or ""):
        return False
    if HUMAN_TAIL.match(tail or ""):
        return False
    if HUMAN_OTHER_END.match(tail or ""):
        return False
    return any(word not in HUMAN_EMPTY for word in re.findall(r"[a-z]+", (tail or "").lower()))


def _asks_for_a_person_to_talk_to(clean):
    """True when the line asks for a person to deal with, and says nothing else it wants.

    The ask has to open the line (`_opens_the_line`) and what follows has to be the tail shapes
    above - nothing, "please", "here", the asker or this end of the chat. Anything a person wants
    the person *for* names a subject, and a subject is the entries' line, so this reading leaves
    it alone: "is there a real person i can talk to about my grief" is answered by the grief
    module on main and by this reading if the tail were let through.
    """
    matched = HUMAN_TALK_ASK.search(clean)
    if not matched or not _opens_the_line(clean[:matched.start()]):
        return False
    tail = clean[matched.end():]
    return bool(HUMAN_TAIL.match(tail) or HUMAN_TO_ME.match(tail)
                or HUMAN_OTHER_END.match(tail))


# An ask for a hand, with nothing said about what for: "can you help me", "i need a hand",
# "give me a hand". The whole line is the ask, so there is no subject to read and nothing to
# search for - and the shrug ("I don't know enough to answer that honestly") reads as a refusal
# to a line that only asks whether the bot will help at all. The offer asks for the detail,
# which is what a friend says.
HAND_ASK = re.compile(
    r"^(?:so |ok |okay |right |hi |hiya |hello |hey |and |please )*"
    r"(?:(?:can|could|will|would) (?:you|u) (?:please )?"
    r"(?:help(?: (?:me|us))?(?: out)?|give (?:me|us) a hand|lend (?:me|us) a hand"
    r"|do (?:me|us) a favour|advise (?:me|us)|be a hand)"
    r"|(?:i )?(?:could do with|need|want|would like) (?:(?:your|some|a bit of) )?"
    r"(?:help|a hand|advice|a bit of advice)"
    r"|(?:can|could) (?:i|we) (?:get|have|ask for) (?:(?:your|some|a little|a bit of) )?"
    r"(?:help|a hand|advice)"
    r"|help(?: me)?(?: out)?"
    r"|give me a hand"
    r")"
    r"(?: (?:with|about) (?:something|anything|a thing|stuff|it))?"
    # A time word after the ask says when the hand is needed, not what for: "i need help now",
    # "can you help me today". Left out, the ask did not match and the line went to whatever read
    # the time word - "i need help now" was answered "Bye for now!" by the leaving reader, a
    # farewell to somebody asking for a hand.
    r"(?: (?:here|please|now|today|tonight|asap|urgently|quick(?:ly)?|straight away))?"
    r"(?: (?:right )?now)?(?: please)?$")


def _asks_for_help(clean, understood=None):
    """A bare ask for a hand as the whole line, commas and all ("hi, can you help me").

    Typed the way people type it, the ask is not in plain words: "can u help me pls" is the
    commonest spelling of it on the deck and it went to the search shrug, because the pattern
    is written for ordinary words and only the reading puts them there ("u" -> "you", "pls" ->
    "please", "help me pls" -> "help me please"). So the line as typed is tried first and the
    reading's own plain text second.
    """
    lines = [clean]
    if isinstance(understood, dict):
        said = understood.get("plain")
        if isinstance(said, str) and said and said != clean:
            lines.append(said)
    for line in lines:
        bare = " ".join(re.sub(r"[^a-z0-9 ]+", " ", str(line or "").lower()).split())
        if HAND_ASK.match(bare):
            return True
    return False


# "who made you do that" asks who is behind the bot's own words. The tail after "made you" is the
# bot's own doing, so unlike every other self question there is no subject to read there: "who
# made you say that" and "what made you say that" are the same question about the same thing.
# "what made you say that" asks who is behind the words, which is the agency answer. The same shape
# with any other verb is a question about the thing the bot has no body for - "what makes you
# sneeze" was read as agency and answered "Me, in the only sense there is: I pick the words", which
# is a reply to a question nobody asked - so the verb after "you" has to be a saying or a deciding.
MADE_ASK = re.compile(r"\bwho (?:made|makes|told|tells|taught|programmed|built|wrote)\s+(?:you|u)\b"
                      r"|\bwhat (?:made|makes) (?:you|u)\s+(?:say|think|believe|decide|choose|"
                      r"pick|answer|reply|write|act|do\s+that)\b")


SELF_OPENER = re.compile(r"\b(?:where|why|how\s+long)\b")


# "what are you for" asks the same as "why are you here": a point, not a place.
# "what model are you", "which model are you running on", "what version are you", "are you an
# LLM". The subject is the machine the bot is made of, so it is a question about the bot and not a
# fact to search: "what model of car do you recommend" keeps its own answer, because the word
# after the model is "of" and not an ask about the bot.
MODEL_ASK = re.compile(
    r"\b(?:what|which)\s+(?:\w+\s+){0,2}?(?:model|version|engine|llm|ai)\s+(?:are|is|do|"
    r"did)\s+(?:you|u)\b"
    r"|\bwhat\s+(?:are|is|were)\s+(?:you|u)\s+(?:running|based|built|trained)\s+on\b"
    r"|\bare\s+(?:you|u)\s+(?:a\s+|an\s+)?(?:llm|large\s+language\s+model|"
    r"neural\s+net\w*|transformer|deep\s+learning\s+model)\b")


# How the bot works is the same honest answer as what it is made of, and it was going to the search
# hedge or to the list of things the bot can help with: "how do you work" got "Cooking, travel,
# money, work, gadgets, kids, feelings - everyday questions and plans", "do you use ai" and "whats
# inside you" got "A quick search online will get you a solid answer", and "how are you built" got
# "All good here. What's keeping you busy?". The reply the bot already has for its own make - no
# model, hand-written rules, nothing learned - answers every one of them, so they read as `model`.
# Each pattern is anchored to the end of the line or to the bot as its subject, so a line about a
# thing keeps its entry: "how do you work out a percentage", "how do you make bread" and "how do
# you work this telly" are not read here.
# "are you a bot", "are you an ai", "are you a chatbot" are not read here: that person wants yes
# or no first, and the identity answer already opens with it ("I'm a chatbot, not a person"). The
# workings answer opens on what the bot is made of, which answers a question they did not ask.
WORKINGS_ASK = re.compile(
    r"\bhow\s+(?:do|does)\s+(?:you|u)\s+(?:actually\s+|really\s+)?work"
    r"\s*(?:then|though|really|anyway|now)?\s*$"
    r"|\bhow\s+(?:are|were)\s+(?:you|u)\s+(?:built|made|programmed|put together|written)\b"
    r"|\bwhat(?:s| is)\s+(?:inside|under)\s+(?:you|your hood|the hood)\b"
    r"|\bdo\s+(?:you|u)\s+use\s+(?:ai|an ai|chatgpt|gpt|a model|an llm|llm|a neural network)\b"
    r"|\bhow\s+do\s+(?:you|u)\s+answer\s+(?:questions|these|things|that)\s*$")


# "why do you keep asking me questions", "why are you asking me that", "why so many questions": a
# remark on how the bot asks is a question about the bot, and nothing about it is on the web, so
# the search hedge ("a quick search online will get you a solid answer") is the one reply that
# cannot help. The answer needs no facts: why it asks, and that a person can tell it to stop.
ASKING_ASK = re.compile(
    # "why do you keep asking", "why are you always asking me that": the complaint in its usual
    # shape, named by "you" and the asking.
    r"\bwhy\s+(?:do|did|does|are|were|would)\s+(?:you|u)\s+"
    r"(?:keep|always|even|still)\s+(?:be\s+)?(?:ask|asking)\b"
    # "why do you ask so many questions", "why did you ask me that": the asking named with how
    # much of it there was. A line that asks about what the asking was *for* ("why do you ask for
    # my email") is a different question and keeps its own reading.
    r"|\bwhy\s+(?:do|did|does|are|were|would)\s+(?:you|u)\s+(?:ask|asking|asked)\s+"
    r"(?:me\s+)?(?:so\s+many|this\s+many|that\s+many|all\s+these|all\s+the|these|that|this)\b"
    # the bare "why do you ask", which is the whole line
    r"|\bwhy\s+(?:do|did|does)\s+(?:you|u)\s+ask\s*$"
    r"|\bwhy\s+(?:are|were)\s+(?:you|u)\s+asking(?:\s+me)?\s*(?:that|this|so\s+many)?\s*$"
    # "do you always ask this many questions": the same complaint without the "why"
    r"|\b(?:do|did)\s+(?:you|u)\s+(?:always\s+|really\s+|have\s+to\s+)?ask\s+"
    r"(?:so|this|that|these)\s+many\s+questions\b"
    r"|\bwhy\s+(?:so\s+many|all\s+these|all\s+the)\s+questions?\b"
    r"|\b(?:stop|quit|enough\s+with)\s+(?:the\s+)?(?:asking|questions)\b")


# Being trusted, and being judged. "can i trust you", "are you lying", "do you make things up"
# and "will you judge me" were answered by the search hedge - an offer to look up a fact about the
# world, made to a person asking what this thing in front of them will do with them. The honesty
# answer already exists one table away ("are you always right"); the judgement one is the privacy
# answer said warmly, because nothing is written down and nobody is grading them.
#
# Every shape names the bot as the subject, because the same words about somebody of the world are
# ordinary advice questions: "can i trust a roofer", "should i trust tripadvisor", "i dont trust
# my doctor" and "is this garage trustworthy" keep their own answers.
TRUST_ASK = re.compile(
    r"\b(?:can|could|should|shall|may)\s+(?:i|we)\s+(?:really\s+|honestly\s+|actually\s+)?"
    r"(?:trust|believe|rely\s+on)\s+(?:you|u)\b"
    r"|\bcan\s+(?:i|we)\s+(?:trust|believe)\s+what\s+(?:you|u)\s+(?:say|tell\s+me)\b"
    r"|\bare\s+(?:you|u)\s+(?:trustworthy|reliable|honest|truthful)\b"
    r"|\bwill\s+(?:you|u)\s+(?:tell|give)\s+me\s+the\s+truth\b"
    r"|\bare\s+(?:you|u)\s+telling\s+(?:me\s+)?the\s+truth\b"
    r"|\bare\s+(?:you|u)\s+lying\b"
    r"|\bdo\s+(?:you|u)\s+(?:ever\s+)?(?:lie|guess|make\s+(?:things|stuff|that|it|this|them)\s+up|"
    r"make\s+up\s+(?:things|stuff|answers|facts))\b"
    r"|\bare\s+(?:you|u)\s+(?:making|inventing)\s+(?:that|this|it|things|stuff)\s+up\b", re.I)


# Where the person stands with this chat, asked in the words people use for it. "is this between
# us" is not a promise asked for - that is "keep this between us", which the secret reading
# answers with a yes - it is the person checking, and the bot's own privacy answer is the only
# thing that can tell them. All five of these went to the search hedge, which offered to look up a
# fact about the world: "is this between us", "is this just between us", "are we private here",
# "is what i say between us" and "what happens to what i tell you".
#
# The subject is what keeps it narrow. The line has to ask about the chat ("this", "it", "we") or
# about the words ("what i say"), so "is the gap between us too big" and "what happens to my
# details if i switch supplier" are somebody's own business and keep their answers. The words arm
# names the person as the one saying them, which is why "what happens to my messages" is left to
# the privacy shapes that already read it.
BETWEEN_US_ASK = re.compile(
    # "is this between us", "is this chat just between us", "is this between us or what". The line
    # asks about the chat itself, so nothing of the world may sit between the "this" and the
    # "between us": "is this seat between us" is not this question.
    r"\b(?:is|are|was|were|will|would|does|do|can)\s+(?:this|that|it)\s+"
    r"(?:(?:chat|conversation|thread|session)\s+)?(?:just\s+|really\s+)?"
    r"between\s+(?:us|you\s+and\s+me)\b"
    # The words rather than the chat: "is what i say between us", "is everything i say between us".
    r"|\b(?:is|are)\s+(?:what|everything)\s+i\s+(?:say|tell|tell\s+you|type|write)\s+"
    r"(?:just\s+)?between\s+(?:us|you\s+and\s+me)\b"
    # "are we private here", "are we private on this" - "we" is the chat and the person together.
    r"|\bare\s+(?:we|you)\s+(?:private|confidential|anonymous)\s+(?:here|on\s+this|in\s+this)\b"
    # "is this anonymous", and the same of the chat by name.
    r"|\bis\s+(?:this|it)\s+(?:chat\s+)?anonymous\b"
    # The same check asked as what happens to the words: "what happens to what i tell you".
    r"|\bwhat\s+(?:happens|happened)\s+to\s+(?:what|everything)\s+i\s+(?:say|tell|type|write|send)\b",
    re.I)


SECRET_ASK = re.compile(
    r"\bcan\s+(?:you|u)\s+keep\s+(?:a\s+)?secret\b"
    r"|\bare\s+(?:you|u)\s+good\s+at\s+keeping\s+(?:a\s+)?secret\b"
    r"|\bcan\s+i\s+tell\s+(?:you|u)\s+(?:a\s+)?secret\b"
    r"|\bkeep\s+(?:this|it)\s+(?:between\s+(?:us|you\s+and\s+me)|to\s+yourself)\b"
    r"|\bthis\s+stays\s+between\s+(?:us|you\s+and\s+me)\b", re.I)


# A promise of silence asked for in so many words is the same ask as "can you keep a secret", and
# it was answered by whichever pool came last: the privacy lines promised silence with no exception
# ("I hold what you say only for as long as we are talking"), and "promise you wont tell my husband"
# got "Got it. Is there anything you'd like a hand with?". Both are the secret reading, which says
# yes first and then who the person should tell, so the promise is kept and the exception is said.
# The shape is a promise, an oath or an instruction about telling, and it needs the tell: "promise me
# you will ring the doctor" is a plan and keeps its own answer.
PROMISE_ASK = re.compile(
    r"\bpromise\s+(?:me\s+)?(?:that\s+)?(?:you|u)\s+(?:won'?t|wont|will\s+not|never|not)\s+"
    r"(?:tell|say|repeat|breathe|mention|share|spread)\b"
    r"|\bpromise\s+(?:me\s+)?(?:not\s+to|you'?ll\s+not|you\s+will\s+not|you\s+won'?t|you\s+wont)\s+"
    r"(?:tell|say|repeat|mention)\b"
    r"|\bswear\s+(?:me\s+)?(?:that\s+)?(?:you|u)\s+(?:won'?t|wont|will\s+not|never)\s+"
    r"(?:tell|say|repeat|mention)\b"
    r"|\b(?:you|u)\s+(?:won'?t|wont|will\s+not)\s+(?:be\s+)?(?:tell(?:ing)?|say(?:ing)?)\s+"
    r"(?:anyone|anybody|no\s+one|a\s+soul|nothing\s+to\s+anyone)\b"
    r"|(?<!\bi )(?<!\bwe )(?<!\bthey )\b(?:don'?t|do\s+not)\s+(?:go\s+telling|tell)\s+"
    r"(?:anyone|anybody|no\s+one|a\s+soul|my\s+(?:mum|mom|dad|husband|wife|partner|boss|mate|friend|"
    r"sister|brother|family|parents|doctor|girlfriend|boyfriend|other\s+half))\b"
    r"|\bjust\s+between\s+(?:us|you\s+and\s+me)\b"
    r"|\bno\s+one\s+else\s+(?:will|can|needs\s+to)\s+(?:hear|see|know)\s+(?:about\s+)?this\b", re.I)


# The person is the object of the judging: "do you judge a cake by how it looks" is an opinion
# question about cake, and the object is what tells the two apart.
JUDGING_ASK = re.compile(
    r"\b(?:will|would|are|do|did|might)\s+(?:you|u)\s+(?:going\s+to\s+)?"
    r"(?:judge|judging|judgement|judgment)(?:\s+me\b|\s+us\b|\s+my\b|\s+what\s+i\b|"
    r"\s+someone\b|[\s?!.]*$)"
    r"|\b(?:don'?t|do\s+not|please\s+don'?t|promise\s+(?:me\s+)?(?:you\s+won'?t|not\s+to)|"
    r"you\s+won'?t)\s+judge\b"
    r"|\bwill\s+(?:you|u)\s+(?:think|say)\s+i'?m\s+(?:weird|stupid|mad|dumb|thick|odd|"
    r"crazy|silly|pathetic|a\s+failure)\b", re.I)


# "what do you regret" puts the question word in front of the auxiliary, so the SELF_ASK gate below
# never sees it.
REGRET_ASK = re.compile(r"\bwhat\s+(?:do|does|would|did)\s+(?:you|u)\s+regrets?\b")


SELF_PURPOSE = re.compile(r"\bwhat (?:are|were) (?:you|u) (?:for|made for|here for)\b|"
                          r"\bwhat(?:'s| is) your (?:purpose|point)\b|\bpoint of you\b")


# "what can't you do", "what don't you know", "what are you bad at", "is there anything you
# can't do", "what are your limits". The line has to end on the ask, so a question with a subject
# in front of it keeps its own answer: "what do you do when you can't sleep" is not this, and
# "what can i do about the noise" is about the noise.
# The gap between the asking word and "can't" is where the subject sits, and it decides whose limit
# this is: "what cant you do" asks about the bot, while "they want 80 a month which i cant do" is an
# ordinary relative clause about the person's own week, and answering it with the bot's edges told a
# person with a bill they cannot pay what the program cannot look up. A first or third person in the
# gap means the limit belongs to somebody else and this reading leaves the line alone.
LIMITS_ASK = re.compile(
    r"\b(?:what|which|anything|something)\b"
    r"(?![a-z ]{0,20}\b(?:i|we|he|she|they|us|them|him|her|me)\b)[a-z ]{0,30}?"
    r"(?:\bcan'?t|\bcannot|\bcan\s+not|\bdon'?t|\bdo\s+not|\bcan\s+you\s+(?:not|n'?t))\s+"
    r"(?:you\s+)?(?:do|help|help with|answer|know|handle|understand|manage|say|cope with)"
    r"\s*(?:with|about)?[\s?!.]*$"
    r"|\b(?:what|which)\s+(?:are|is)\s+(?:it\s+)?(?:you|u)\s+"
    r"(?:bad|not good|no good|rubbish|useless|weak)\s+at[\s?!.]*$"
    r"|\bwhat\s+[a-z ]{0,20}?\byou\s+(?:bad|not good|no good|rubbish|useless)\s+at[\s?!.]*$"
    r"|\bwhat\s+are\s+your\s+(?:limits?|weak\s*spots?|weaknesses?)[\s?!.]*$")


# The person's own device or their own getting online: not a question about the bot.
OWN_DEVICE = re.compile(
    r"\b(?:my|our)\s+(?:laptop|phone|pc|computer|router|wifi|broadband|tablet|ipad|tv)\b"
    r"|\bhelp\s+me\b|\bhow\s+(?:do|can|should)\s+i\b")


# "are you online" on its own is the chat line for "are you still there": the person is checking
# the bot has not gone quiet, not asking what it can reach, and "Yep, right here - go on." is the
# answer to that. The same words with a network in them ("are you connected to the internet") are
# a question about the bot's reach and belong to the pool.
#
# What may follow the word is part of the same rule: the guard has to be as wide as the pool key,
# or one filler takes the line back out of it - "are you online now" went to the pool while "are
# you online" stayed with the chat line, which is the same question. "at all" is not filler: "are
# you online at all" is the person asking whether it can reach anything, and that is the pool.
A_BARE_ONLINE = re.compile(
    r"^\s*(?:so\s+|and\s+|ok(?:ay)?\s+|just\s+)?(?:are|is|r)\s+(?:you|u)\s+"
    r"(?:really\s+|still\s+|even\s+)?(?:online|connected|there)\s*"
    r"(?:(?:right\s+|at\s+the\s+)?now\s*|at\s+the\s+moment\s*|today\s*|tonight\s*|"
    r"then\s*|please\s*|mate\s*|though\s*)*[\s?!.]*$")


def _says_only_what_they_said(lines, clean):
    """The warm lines whose own detail the person's line carries, or the plain ones if none do.

    A congratulations is a remark about their news, and the person's line is the only thing it can
    know about them. A line naming a wait or the work behind a result is used only when their words
    say so; where every line names something, the ones that name nothing are preferred, and where
    there are none of those either the pool is left alone.
    """
    said = set(re.findall(r"[a-z']+", str(clean or "").lower()))

    def _unsupported(line):
        for phrase, support in DETAILS_IN_A_WARM_LINE:
            if phrase in line.lower():
                return not any(word in said for word in support)
        return False

    kept = [line for line in lines if not _unsupported(line)]
    # The pool's own order is kept, so a line that is sound for this person still lands on the turn
    # it always did: the only turns that move are the ones whose line had no ground under it.
    return kept or [line for line in lines if not _unsupported(line)] or list(lines)


# One of the lines above looks forward ("Happy birthday when it comes"), and that is the right
# thing to say to a day that has not arrived. Said of today it is plainly wrong - the day is here -
# so the forward-looking line stands aside when the line itself puts the occasion on today.
HAPPENING_NOW = re.compile(r"\b(?:today|tonight|this\s+(?:evening|afternoon|morning)|right\s+now)\b",
                           re.I)


# A date the line already names - "were getting married in june", "next month" - is not something
# to ask about: "how far off is it?" asks back the one thing the person just said.
DATE_GIVEN = re.compile(
    r"\b(?:in|on|next|this|at)\s+(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|"
    r"week|weekend|month|year|spring|summer|autumn|winter|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)


# A warm line about somebody else's day is a remark about their news, and the only things it can
# know are the words of the line: whose day it is, and when. Two of the lines above guessed past
# that. "Lovely. Are you seeing them for it?" said to "my daughters 7th birthday is in three
# weeks" puts the daughter in another house - the person may be with her every day - and "them" is
# three people where the line named one. Same rule as DETAILS_IN_A_WARM_LINE: a detail is said only
# when the line carries it.
#
#   1. A line that places the other person somewhere ("seeing them", "off to see", "go over") is
#      used only when the line says they are apart: away, visiting, over there, back home, at uni.
#   2. "them" is said of one person only when the line names no one: a wife is "her", a son "him".
_APART = re.compile(
    r"\b(?:away|apart|elsewhere|abroad|miles|far\s+away|over\s+there|back\s+home|visiting|"
    r"visit|stay(?:ing)?\s+with|lives?\s+(?:in|near|abroad|away)|living\s+(?:in|near|abroad|away)|"
    r"uni|university|college|the\s+other\s+side|different\s+(?:town|city|country)|"
    r"in\s+(?:london|manchester|birmingham|leeds|glasgow|edinburgh|cardiff|belfast|dublin|"
    r"paris|spain|france|italy|america|australia|canada|germany|portugal|greece|"
    r"scotland|wales|ireland|england))\b", re.I)


_PLACES_THEM = re.compile(
    r"\b(?:seeing\s+them|see\s+them|off\s+to\s+see|go\s+and\s+see|going\s+to\s+see|"
    r"visit\s+them|visiting\s+them|go\s+over|going\s+over|drive\s+(?:up|down)|"
    r"travell?ing\s+(?:to|up|down))\b", re.I)


# Who the day belongs to, in the words the line used: "her" for a wife or a daughter, "him" for a
# son or a father. A line naming both, or nobody, keeps "them".
_SHE = frozenset("""wife mum mom mother mummy daughter sister gran granny nan nana grandma
    grandmum grandmother aunt auntie niece stepmum stepmother stepdaughter motherinlaw
    sisterinlaw daughterinlaw fiancee girlfriend missus mrs""".split())


_HE = frozenset("""husband dad father daddy son brother grandad granddad grandpa granddad
    grandfather uncle nephew stepdad stepfather stepson fatherinlaw brotherinlaw soninlaw
    fiance boyfriend mr""".split())


def _the_pronoun(clean):
    """her or him for the one person the day belongs to, "" when the line names none or both."""
    words = re.findall(r"[a-z']+", str(clean or "").lower().replace("\u2019", "'"))
    she = he = False
    for word in words:
        stem = word[:-1] if word.endswith("s") and word[:-1] in (_SHE | _HE) else word
        if stem in _SHE:
            she = True
        elif stem in _HE:
            he = True
    if she and not he:
        return "her"
    if he and not she:
        return "him"
    return ""


def _occasion_pool(occasion, clean):
    """The lines for this occasion, without the ones that look forward to today's occasion."""
    if goodnews.someone_elses_occasion(clean):
        pool = SOMEONE_ELSES_DAY.get(occasion)
        if pool:
            apart = bool(_APART.search(str(clean or "")))
            kept = [line for line in pool
                    if apart or not _PLACES_THEM.search(line)]
            pronoun = _the_pronoun(clean)
            if pronoun:
                kept = [re.sub(r"\bthem\b", pronoun, line) for line in kept]
            return tuple(kept or pool)
    pool = OCCASION[occasion]
    # Each line that asks a question the line has already answered stands aside: the forward line
    # for a day that is today, the "how far off is it" line for a date the person just gave.
    drop = []
    if HAPPENING_NOW.search(clean):
        drop.append("when it comes")
    if DATE_GIVEN.search(clean):
        drop.append("how far off")
    if drop:
        pool = tuple(line for line in pool
                     if not any(phrase in line.lower() for phrase in drop)) or pool
    return pool


# Being turned away from work - "nobody will interview me", "i cant even get an interview now im
# 50" - is not bad news to be gentle about and it is not small talk either. The gentle pool's "ugh,
# that's a lot to carry" is wrong for it, and the stock nod ("got it, is there anything you'd like
# a hand with?") is colder than saying nothing. These name the door and ask the one question worth
# asking, so the person can go on.
CLOSED_DOOR = (
    "That's a hard thing to keep going back to. What sort of work are you after?",
    "Applying and hearing nothing wears a person down, and it is not about what you are worth. "
    "How long has this been going on?",
    "A door that keeps closing is exhausting. What have you been trying for?",
    "It's a rough time to be looking. What is the job you are chasing?",
)


NEGATIVE = (
    "That sounds rough. If you want, I can help you think through what to do next.",
    "Ugh, that's a lot to carry. What would make today a bit easier?",
    "I'm sorry — that's frustrating. Want a hand working out the next step?",
    "Sorry to hear that. What would help most right now?",
)


# The same pool with the word for a setback taken out, for the news that has a name in it: a dad
# with parkinsons, a daughter taken into care, a roof that has to go. "That's frustrating" is what a
# friend says about a form or a bus, and applied to a person it is the smallest of the four lines -
# the other three say the same thing without judging how big it is. The order is kept, so the
# wording still varies with the line.
NAMED_NEGATIVE = tuple(line for line in NEGATIVE if "frustrating" not in line)


# What makes the news serious rather than a cold. A named condition, an operation, or the hospital
# itself: a cold, a temperature and a rash are the carer's line (`CARING`) and stay there. A death
# and a suicide are not here - they are heavier news with pools of their own - and neither is a
# seizure happening now, which is the safety module's.
SERIOUS_NEWS = re.compile(
    r"\b(?:heart attack|cardiac|stroke|blood clot|aneurysm|"
    r"cancer|tumou?rs?|leuka?emia|lymphoma|melanoma|chemo(?:therapy)?|radiotherapy|"
    r"dialysis|transplant|bypass|sepsis|septica?emia|pneumonia|meningitis|"
    r"intensive care|high dependency|life support|resuscitat\w+|"
    r"operation|surgery|amputat\w+|"
    r"admitted|in hospital|into hospital|hospital (?:last|this) (?:night|week|morning)|"
    r"collapsed|collapse|seizures?|convulsions?|"
    r"diagnosed|diagnosis|terminal|palliative|hospice)\b", re.I)


# Whose news it is, and it has to be someone close: "i had a heart attack" is the person's own
# body and the symptom line's, and "my dog had a heart attack" is the vet's.
CLOSE_OWNER = re.compile(r"\b(?:my|our)\s+(?:" + badnews.KIN + r")\b", re.I)


# The same words in a line that is not about them falling ill: a sponsored run for a cancer
# charity, a nurse and a hospital shift, a documentary. The owner word is in all of these.
NOT_THEIR_NEWS = re.compile(
    r"\b(?:sponsor\w*|fundrais\w*|raising|raise money|awareness|charity|marathon|"
    r"race for life|donat\w*|nurses?|nursing|(?:works?|working) (?:at|in|for)|shift)\b", re.I)


# A fear is not news. "i think my mum has cancer", "maybe my mum has cancer", "my mum might have
# cancer" report nothing that has been diagnosed - the person is telling you what they are afraid
# of, and a pool that opens "that is frightening news about someone close" hands them a diagnosis
# nobody has given. The hedge only counts before the condition word: "my dad had a heart attack
# and i keep thinking it could happen again" reports the news first and wonders afterwards, so it
# is still news and still this pool's.
NOT_YET_NEWS = re.compile(
    r"\b(?:i think|i thought|might|could have|maybe|may have|suspect\w*|probably|possibly|"
    r"what if|is it possible|worried (?:it|that|he|she|they)|terrified (?:it|that)|"
    r"scared (?:it|that)|afraid (?:it|that)|waiting (?:on|for) (?:the )?results)\b", re.I)


# The thread is not in the past yet: "my wife is having a miscarriage right now" is not a grief
# line to be asked about, it is a thing happening while they type.
HAPPENING_NOW = re.compile(
    r"\b(?:right\s+now|just\s+now|as\s+we\s+speak|this\s+minute|right\s+this\s+minute|"
    r"happening\s+now|is\s+having\s+it|are\s+having\s+it|still\s+going\s+on|"
    r"in\s+the\s+next\s+hour|on\s+my\s+way\s+to\s+the\s+hospital)\b")
