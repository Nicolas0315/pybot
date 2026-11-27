"""Part 4 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from ..compose import pick
from ..compose.badnews import reads_as_bad_news, reads_like_a_symptom
from ..understanding import understand as understanding
from ..understanding.kinds import SHIFT_EARLY, SHIFT_LATE
from . import facts, hours as hours_after, named, narrow, taste, topics
from .ack_part_01 import (
    AN_AIM, A_FEELING_ABOUT_IT,
)
from .ack_part_02 import (
    DEATH_WORDS, NOT_THE_HOURS, WANTS_ANSWER, reads_as_an_ask, WHEN_DAYS_TAIL, WHEN_DETAIL,
    WHEN_ROOMY_TAIL, WHEN_TODAY_TAIL, WHEN_TOMORROW_TAIL, _shape_of, CLOCK_EVENT, CLOCK_FLAT,
    TIME_WORD, CLOCK_AFTER_TAIL, CLOCK_AT, CLOCK_DETAIL, CLOCK_FLAT_TAIL, CLOCK_MORNING_TAIL,
    _clock_shape, EARLY_RISE, EARLY_TAIL, HOME_TAIL, LATE_FINISH, LATE_TAIL, LONG_SHIFT, LONG_TAIL,
    NIGHT_TAIL, ON_NIGHTS, SHIFTS_ALL_OVER, SPREAD_TAIL, WORK_FROM_HOME,
)
from .ack_part_03 import (
    REMARK_ALREADY_PAID, REMARK_STILL_TO_COME, A_FEELING, BLEED, _tells_them_what_to_do,
)


def _a_price_still_to_come(body, topic_text):
    """Whether an expense remark is about a price nobody has paid yet.

    "it cost a fortune" and "the flights are expensive" are the same kind of remark and want
    different endings: the first is money already spent, which is why the question that follows
    is whether it was worth it, and the second is a bill still to come, where that question asks
    about a thing that has not happened. The plan on the table decides it - a line in the past
    ("redid", "cost me", "last year") is behind them, and a plan still to happen ("going to",
    "in august", "next month") is not - and with nothing to say either way it counts as still to
    come, because asking someone whether an unbooked trip was worth it reads as the bot not
    having listened.
    """
    said = " ".join(part for part in (body or "", topic_text or "") if part)
    if REMARK_STILL_TO_COME.search(said):
        return True
    return not REMARK_ALREADY_PAID.search(said)


def _a_result_is_on_the_table(clean):
    """Whether this line is a result the person is waiting on or has just heard.

    Asked of bot/compose/fallback.py, which owns the two readings and the two replies, and
    imported here rather than at the top of the file because that file imports this one.
    """
    from ..compose import fallback
    return fallback.reads_as_a_result_line(clean)


# A hole in a frame: {Thing}, {thing}, {food}. What is left after the first one is the ending, and
# that is the part a person hears twice.
_HOLE = re.compile(r"\{[^}]*\}")


# The letters and digits of a line, so "I'm sorry it's all coming" and "I am sorry; it is all
# coming" compare as one ending.
_NOT_WORDS = re.compile(r"[^a-z0-9]+")


def _ending_of(frame):
    """The words a frame adds after the thing said back: the part that repeats between turns."""
    parts = _HOLE.split(frame)
    return " ".join(_NOT_WORDS.sub(" ", parts[1].lower()).split()) if len(parts) > 1 else ""


def _pick_ending(frames, memory, **fields):
    """One of the endings, never the one the reply before it ended with.

    The store says a different thing back each turn - "Your son is 9", then "Your daughter is
    4" - so bot.compose.pick cannot see the repeat: the whole line differs and the ending is the
    same twice running, which reads as a script even though the sentence does not. Facts follow
    facts, so this is where it happens most: "my son is 9 / my daughter is 4" came back as two
    "I'm sorry it's all coming at once" in a row.
    """
    turns = memory.get("turns") or []
    last = ""
    if turns and isinstance(turns[-1], dict):
        last = " ".join(_NOT_WORDS.sub(" ", str(turns[-1].get("bot") or "").lower()).split())
    fresh = [frame for frame in frames if not (_ending_of(frame) and _ending_of(frame) in last)]
    return pick(fresh or list(frames), memory).format(**fields)


# The people a line can be about when it explains a feeling: "he is only 6", "my son is 6".
PERSON_WORDS = frozenset(facts.RELATIONS) | frozenset((
    "kids", "children", "child", "baby", "toddler", "twins", "them", "they", "he", "she",
    "him", "her", "us", "we", "both"))


# An age said on its own is a fact about the person, not the reason for how they feel. "i lost my
# job last week" then "im 52" came back "You're 52 \u2014 so that is the part behind it. What has
# been hardest about it?", which makes the person's age the cause of the redundancy. The age has
# its own plain reading in this file ("you're 52", FACTS above), and the reason-reading is not for
# it; the same is true of a name handed over after bad news.
# The reason marker people put in front of the clause that explains how they are: "im low" then
# "because the kids are hard work". The marker says what the clause is for, so the reading does
# not have to guess it from the turn before, and it is not part of the thing said back - with it,
# the reply reads "Because the kids are hard work \u2014 noted.", which is the receipt of a reason.
A_REASON_MARKER = re.compile(
    r"^(?:(?:and|but|well|so|see)\s+)?(?:because|cos|coz|cause|cuz)\b(?:\s+of\b)?[\s,:]*", re.I)


# A turn that says nothing about how they are, said between the feeling and its reason: "im low"
# then "dont know why" then "because the kids are hard work". The feeling the reason belongs to
# is one turn further back, so the reading looks there rather than giving up on the turn.
NO_REASON = re.compile(
    r"^(?:(?:i\s+)?(?:dont|do not|dunno|havent a clue|no idea|not sure)\b"
    r"(?:\s+(?:really\s+)?(?:know\b\s*)?(?:why)?)?|no reason|not a clue)\s*[.!]*$", re.I)


# A bare thing is not a clause: "her job" and "only the kids" are lifted out of the line and put
# back into a sentence with the state they are the reason for (bot/memory/cause.py's expand),
# which says them in the bot's own words ("your job", not "her job"). A clause of its own ("the
# kids are hard work") has no expansion, so this reading answers it itself - and only a clause is
# worth looking a turn back for, because a bare thing after "dont know why" is still the thing
# the expansion knows how to say.
A_CLAUSE_OF_ITS_OWN = re.compile(
    r"\b(?:is|are|was|were|isnt|arent|wasnt|werent|gets?|got|makes?|made|keeps?|kept|feels?|felt"
    r"|never|always|doesnt|dont|didnt|wont|cant|couldnt|has|have|had|am|been|being|takes?|took"
    r"|wears?|wore|drives?|drove|works?|worked|goes|went|gives?|gave)\b", re.I)


AN_AGE_ALONE = re.compile(
    r"^(?:i'?m|im|i am|ive|i've|i just turned|i turned)\s+(\d{1,3})"
    r"(?:\s*(?:years?|yrs?)(?:\s+old)?)?(?:\s+(?:now|this year))?\s*[.!]?$", re.I)


def _after_a_feeling(clean, memory):
    """Whether this line is the reason for a feeling they said on the turn before.

    The reading of the line before is asked for again here rather than kept: memory["understood"]
    is this turn's reading, the modules answer in any order, and a marker written by one module
    would be lost with its copy when another one's reply is the one the user got. A feeling is
    the engine's own reading (intent "feeling", negative), so "my boss said my reports are late"
    is news and not one.

    The line has to be a short statement about the person or the people in it: a fact about the
    world ("my car is broken") keeps its ordinary echo, and a question has its own answer.
    """
    if AN_AGE_ALONE.match(str(clean or "").strip()):
        # An age is not a reason for anything here: it is what the person is, and the reply that
        # makes it "the part behind it" hands them their own age as the cause of their trouble.
        return False
    if not isinstance(memory, dict):
        return False
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return False
    index = len(turns) - 1
    last = turns[index]
    said = last.get("user") if isinstance(last, dict) else None
    if not isinstance(said, str) or not said.strip():
        return False
    if NO_REASON.match(said.strip()) and A_CLAUSE_OF_ITS_OWN.search(str(clean or "")):
        # "im low" then "dont know why": the turn that says nothing about how they are is not
        # the feeling this reason belongs to. It was answered "dont know why - noted" or with a
        # warm line of its own, and the reason they give next is still for the feeling one turn
        # back, so the reading looks there rather than dropping the reason.
        index -= 1
        if index < 0:
            return False
        back = turns[index]
        said = back.get("user") if isinstance(back, dict) else None
        if not isinstance(said, str) or not said.strip():
            return False
    read = understanding(said)
    if read.get("emotion") == "confused":
        # Losing the thread is not a mood the next line explains: after "i dont get it" the next
        # line is the part they did not follow, and "That is a lot to carry on top of how you
        # feel" is about a feeling nobody named.
        return False
    if AN_AIM.search(said):
        # An aim, not a mood: what follows it is progress and not the reason for it. A feeling now
        # is the exception, because that is the case the reason-reading exists for - somebody who
        # has just said what they are working at and then says they want to give up gets answered
        # warmly, not handed their own line back.
        now = understanding(clean)
        if not (now.get("intent") == "feeling" and (now.get("polarity") or 0) < 0) \
                and not A_FEELING_ABOUT_IT.search(clean):
            return False
    if read.get("intent") != "feeling" or (read.get("polarity") or 0) > 0:
        # "im fine" is a feeling too, and nothing follows from it.
        if not _a_heavy_reply_just_before(memory, index):
            return False
    words = clean.split()
    if not words or len(words) > 12:
        return False
    first = words[0].lower().strip(",;:!")
    if first in ("i", "im", "i'm", "ive", "i've", "we", "we're", "were"):
        return True
    return bool(PERSON_WORDS & {word.lower().strip(",;:!") for word in words})


def _a_heavy_reply_just_before(memory, index):
    """Whether the reply they got on turn `index` was about something heavy they are carrying.

    bot/modules/chat.py notes the pool it answered from when that pool is one of the heavy ones
    (its HEAVY_FEELINGS), and the note survives only if that module's reply is the one the person
    got. The engine's own reading is asked first and this is the second reading, because the
    engine files some heavy lines as news: "i miss my mum" is read as news, and the line after it
    ("she lives in spain") was answered "Got it - she lives in spain", which drops the missing.
    """
    if not isinstance(memory, dict):
        return False
    note = memory.get("heavy_reply")
    if not isinstance(note, dict):
        return False
    return note.get("turn") == index


# Who a line can be about when it is not about the person typing: the subject that carries a
# story on ("she took the kids to her mums", "he wont answer my calls", "they have gone to his
# mums"). A line that opens on "my" or "i" is the person's own life, and a fact about it is a
# fact even in a hard week ("my sister is called Meg" after "my wife left me" is still news the
# bot should hold). So the guard below asks for this, not for a pronoun anywhere in the line.
# What the bot says when it declines to file the line: the next line of a hard story is answered
# by keeping the floor with them, not by handing the turn on. Declining alone was the first shape
# of this rule, and it turned "she packed her things last night" after "my wife left me" into a
# removals checklist - the answers module saw the packing and offered "pack what you use least
# first". So this branch answers. The lines are short and they ask nothing, because the person is
# already telling it and a question at the end of every turn is the thing STYLE.md warns about.
THE_STORY_GOES_ON = (
    "I'm listening \u2014 say more if it helps.",
    "Go on. I'm here.",
    "That sounds like a lot to be in the middle of. Tell me the rest.",
    "I'm with you. Keep going if you want to.",
)


THIRD_PERSON = re.compile(r"^(?:he|she|they|him|her|his|their|them|hes|shes|theyre|theyd|"
                          r"theyll|she'd|he'd|she'll|he'll)\b", re.I)


# How long it has been going is the news, and the question that follows from it is the reply.
# How long it has been going is the news, and the question that follows from it is the reply.
# Rubbing the length in ("Got it - it's been like that for a week") tells the person what they
# said; a friend asks the one thing nobody has asked yet, in the person's own measure of it.
# None of these assumes the thing in hand is a trouble: the line read here says what somebody is
# doing as often as what is wrong ("im learning spanish" / "ive been doing it for 3 months"), and
# "long enough to stop waiting for it to pass" or "worth getting someone in" is not true of a
# language. What a length asks is whether it has moved, so that is all any of them ask.
LENGTH_TAIL = (
    "{length} of it \u2014 has anything changed in that time?",
    "{length} of it. How are you finding it now?",
    "{length} of it already. Is it going the way you want it to?",
    "{length} of it \u2014 and has anything you have tried made a difference?",
)


# The same when the line dates it instead of counting it: "since monday".
SINCE_TAIL = (
    "Since {when} \u2014 has anything changed in that time?",
    "Since {when}. How are you finding it now?",
    "Since {when}. Is it going the way you want it to?",
    "Since {when} \u2014 and has anything you have tried made a difference?",
)


# A measure that already carries its own amount needs no "of it": "Over a week of it" is the
# only shape that reads, so these leads are kept and the rest ("for", "about", "the last") are
# dropped, leaving "A week of it".
LENGTH_KEEPS = frozenset(("nearly", "almost", "over", "going on"))


# A thing being replaced has an age, and the age is the only new fact in the line. "the old one
# is 12 years old" is the thing in hand plus a number of years, and nothing else: the subject is a
# pronoun for the thing, not a name for it, so the entries for named things never see this line.
# The number is read as a digit or as the word people type: "the old one is twelve years old" is
# the same line as "the old one is 12 years old", and read as a digit only it fell through to the
# echo - "Got it - the old one is twelve years old." - which is their own line back.
THE_OLD_ONE = re.compile(
    r"^\W*(?:the|my|our)\s+(?:old|current|existing|present)?\s*one"
    r"(?:\s+(?:i|we)\s+(?:have|'ve|ve|got|use|used))?"
    r"\s+(?:is|was|'s|s)\s+(?P<n>\d{1,2}|[a-z]{3,9})\s*(?:years?|yrs?)(?:\s+old)?\W*$", re.I)


# The turn before it is about getting or replacing one. "new" is the word people use for the one
# they are going to buy, and "getting a" is how they say it out loud.
REPLACING = re.compile(
    r"\b(?:new|getting|get|got|bought|buy|buying|replace|replacing|upgrade|upgrading|"
    r"order|ordering|shopping for|looking at|need a|needs a|want a|after a)\b", re.I)


# Every frame uses the number, and none of them assumes the thing broke: "i need a new one" is
# as often an upgrade as a failure. The first asks the one thing a friend asks next.
OLD_ONE_TAIL = (
    "{n} years on the old one \u2014 it has done its share. What are you after this time?",
    "{n} years is a good run out of one, so you are not replacing it early.",
    "{n} years \u2014 that is a fair innings, and it has earned the swap.",
)


def the_old_one_aged(clean, memory):
    """The reply to a line giving the age of the thing they are replacing, or None.

    "i need a new washing machine" then "the old one is 12 years old" was read as a child of
    twelve and answered "One kid, twelve - noted.", and once that was put right the line fell
    through to the composer's echo - "Got it - the old one is 12 years old." The age is what the
    purchase is measured against, so the reply says what the number means for it.

    Two things have to hold. The line has to be the thing in hand and its age, and nothing else:
    a thing named for itself ("my boiler is 8 years old") is a question about that thing and has
    an entry of its own. And the turn before has to be about getting or replacing one, because
    an age on its own is not a purchase: "my car is 12 years old" after a line about the children
    stays with whatever reads the car.
    """
    if not isinstance(clean, str):
        return None
    found = THE_OLD_ONE.match(clean)
    if not found or len(clean.split()) > 9:
        return None
    said_age = found.group("n").lower()
    if said_age.isdigit():
        age = int(said_age)
    else:
        spoken = facts.WORD_NUMBERS.get(said_age)
        if not isinstance(spoken, int):
            return None
        age = spoken
    if not 5 <= age <= 40:
        return None  # "two years old" is a bad run, not a good one
    turns = memory.get("turns") if isinstance(memory, dict) else None
    said = [str(turn.get("user") or "") for turn in (turns or []) if isinstance(turn, dict)]
    if not said or not REPLACING.search(said[-1]):
        return None
    if A_FEELING.search(clean) or DEATH_WORDS.search(clean) or BLEED.search(clean):
        return None
    return pick(OLD_ONE_TAIL, memory, seed_text=clean).format(n=age)


def _the_length(clean, memory):
    """The reply to a line that says only how long the thing has been going, or None.

    Said a turn after the bot answered that thing, this is the person telling the answer how
    long it has had: "its been like that for a week" is not a detail to file and hand back, and
    handing it back is what the fridge conversation came out as. The length belongs with the
    answer, so this only reads the line when the last turn was an answer - a length said cold is
    its own subject and keeps its own reply. A body that hurts, a loss and a feeling are somebody
    else's turn even said this short.
    """
    if not narrow.only_a_length(clean):
        return None
    from . import tried

    if not tried.after_an_answer(memory):
        return None
    if reads_like_a_symptom(clean.lower()) or reads_as_bad_news(clean.lower()):
        return None
    if A_FEELING.search(clean) or DEATH_WORDS.search(clean):
        return None
    found = narrow.A_LENGTH.search(clean)
    lead = found.group("lead").lower()
    amount = found.group("amount")
    unit = found.group("unit").lower()
    if lead == "since":
        # A weekday is a name and keeps its capital; "since yesterday" is a word like any other.
        when = unit[0].upper() + unit[1:] if unit in narrow.LENGTH_NAMED_DAYS else unit
        return pick(SINCE_TAIL, memory, seed_text=clean).format(when=when)
    # "for months" has no amount of its own, and "a months" is not a sentence: the plural unit is
    # the measure on its own.
    length = "%s %s" % (amount, unit) if amount else unit
    if lead in LENGTH_KEEPS:
        length = "%s %s" % (lead, length)
    return pick(LENGTH_TAIL, memory, seed_text=clean).format(
        length=length[0].upper() + length[1:])


def _the_hours(clean, read, memory):
    """The reply to a line about the hours they work, or None.

    "i work nights" is a fact about their week, and the store filed it: "Noted: you work
    nights." is a clerk with a form, not a friend. The reply is about the life those hours make
    - the body clock, the week that moves, the day with no edges - and it is chosen by which of
    those the line says, never by the words of a topic, so it cannot be pasted onto another
    line. Only a line that is only that: a body that will not sleep, a job they are sick of, a
    wage, a rota they want out of and any ask are all somebody else's turn, and a loss thread
    keeps its own quiet.
    """
    if "?" in clean or WANTS_ANSWER.search(read):
        return None
    if NOT_THE_HOURS.search(read):
        return None
    if DEATH_WORDS.search(read) or A_FEELING.search(clean) or BLEED.search(read):
        return None
    if reads_like_a_symptom(read.lower()) or reads_as_bad_news(read.lower()):
        return None
    # A death in the last few turns is not a chat about the rota, whatever the company gives
    # them: the loss modules answer those turns and this one stays out of the way.
    turns = [one for one in (memory.get("turns") or []) if isinstance(one, dict)]
    recent = " ".join(str(one.get("user") or "") for one in turns[-3:])
    if recent and DEATH_WORDS.search(recent):
        return None
    last_ask = str(turns[-1].get("user") or "") if turns else ""
    if turns and turns[-1].get("module") == "answers" and reads_as_an_ask(last_ask):
        # The line is a detail added to the answer just given ("should i nap in the afternoon" /
        # "i work from home"): the thing on the table is the answer, and saying it back with
        # that answer under it beats a pool that starts a new subject of its own. The ask in the
        # line before it is what makes it a detail - hours said cold are their own subject.
        return None
    family, pool = _hours_family(read)
    if pool is None:
        return None
    # The store keeps the job whichever way the turn goes, so the hours are still there to be
    # asked about later; only the reply is this one's. The kind of week is kept for the turn
    # after it, because the next line is usually "does that get easier" (bot/memory/hours.py).
    hours_after.note(memory, family)
    return pick(pool, memory, clean)


def _a_deadline(clean, read, memory):
    """The reply to a line that only says when the thing we just answered has to happen.

    "its tomorrow" and "its in three weeks" are the person telling us the answer we just gave has
    a clock on it. The answer is aimed at the clock rather than said again: a deadline a day off
    is cut down to its first step, and one weeks off is spread out. Only after a real answer - a
    line from the answers module long enough to be advice - because a deadline has nothing to
    change when the turn before it was a hello or a hedge, and never in a loss thread, where the
    clock is not the thing that matters.
    """
    found = WHEN_DETAIL.search(clean)
    if not found:
        return None
    if len(clean.split()) > 7:
        return None
    turns = [one for one in (memory.get("turns") or []) if isinstance(one, dict)]
    if not turns:
        return None
    last = turns[-1]
    said = str(last.get("bot") or "")
    if last.get("module") != "answers" or len(said.split()) < 18:
        return None
    if not _tells_them_what_to_do(said):
        return None  # a list of facts has no first step, and a deadline has nothing to change
    recent = said + " " + " ".join(str(one.get("user") or "") for one in turns[-3:])
    if DEATH_WORDS.search(recent) or BLEED.search(recent) or A_FEELING.search(clean):
        return None
    when = found.group("when").strip()
    pools = {"today": WHEN_TODAY_TAIL, "tomorrow": WHEN_TOMORROW_TAIL, "days": WHEN_DAYS_TAIL}
    pool = pools.get(_shape_of(when), WHEN_ROOMY_TAIL)
    return pick(pool, memory, clean).format(when=when, When=when[:1].upper() + when[1:])


def _an_hour_on_the_day(text):
    """Which pool an hour on the day belongs to: "nerves" for an appointment, "flat" for a shift.

    "i have a night shift tomorrow" / "its at 10pm" is an hour on the day too, and a night shift at
    ten is spent asleep in the morning: the appointment pools, which all say what the morning is
    for, say the opposite of that person's day. The flat pool says only that the day fits round
    the hour, which is true of a shift, a class, a viewing and lunch with a sister.
    """
    if not isinstance(text, str) or not text:
        return None
    if CLOCK_EVENT.search(text):
        return "nerves"
    if CLOCK_FLAT.search(text):
        return "flat"
    from . import when as clock  # noqa: PLC0415 - same package, kept local for the import order

    return "nerves" if clock.EVENT_WORD.search(text) else None


# "the total is at 40" has the same shape as "the appointment is at 2:30", and only the noun tells
# them apart: a quantity on a total, a bid, a count, a level or a price is not an hour, and those
# lines used to get "At 40, so the morning is free...".
THE_NOUN_IS_AT = re.compile(r"\bthe\s+(?P<noun>[a-z'-]+)\s+is\s+(?:at|for)\s+", re.I)


# A figure carrying its own marker is a time whatever noun is in front of it.
A_MARKED_HOUR = re.compile(
    r"\d{1,2}\s*(?:am|pm|a\.m\.|p\.m\.)|\d{1,2}[:.]\d{2}|o'?\s?clock|"
    r"\b(?:half|quarter)\b|\b" + TIME_WORD + r"\b", re.I)


def _the_figure_is_an_hour(when):
    """True when the figure is an hour at all: "40" is a quantity, and a clock stops at 24."""
    head = re.match(r"\s*(\d{1,2})(?!\d)", when)
    if not head:
        return True  # a spelled hour ("half nine", "ten o'clock") is a time
    return 1 <= int(head.group(1)) <= 24


def _a_clock_time(clean, read, memory):
    """The reply to a line that only gives the hour the thing we just answered is at, or None.

    "its at 10" and "the interview is at 10" say when the answer above has to happen, and the
    answer is aimed at the hour instead of being said back. Only after a real answer that tells
    them what to do, and only when the conversation already names something that goes in a diary
    (an interview, an appointment, a scan, a flight): the same words after advice about the roses
    ("its at 10") are not an appointment, and the store has nothing to build a morning around.
    """
    if len(clean.split()) > 8:
        return None
    found = CLOCK_DETAIL.search(clean) or CLOCK_AT.search(clean)
    if not found:
        return None
    from . import when as clock  # noqa: PLC0415 - same package, kept local for the import order

    turns = [one for one in (memory.get("turns") or []) if isinstance(one, dict)]
    if not turns:
        return None
    last = turns[-1]
    said = str(last.get("bot") or "")
    module = last.get("module")
    theirs = " ".join(str(one.get("user") or "") for one in turns[-3:])
    if module == "greeting" and not len(said.split()) < 5:
        # The composer's own acknowledgment is a whole turn too: "im going for a scan next week"
        # is answered "Noted: you're going for a scan next week.", and the hour after it is the
        # hour of that scan. It counts when either side names the thing that goes in a diary:
        # the acknowledgment used to hand the words back, and the small talk now answers the
        # same line with "How are you feeling about it?", which names nothing at all.
        if not (_an_hour_on_the_day(said) or _an_hour_on_the_day(theirs)):
            return None
    elif module not in ("answers", "chat", "memory_store") or len(said.split()) < 5:
        return None
    # What they said, not what the answer said: "i want to learn spanish" is answered with advice
    # that says "start", and a start is not an appointment at seven.
    kind = _an_hour_on_the_day(theirs)
    if not kind:
        return None
    # The emergency guard reads the person's own words and this line, never the answer above: a
    # dentist card that mentions gums that bleed was enough to drop the hour of the appointment,
    # and the hour is exactly what the person gave.
    recent = said + " " + theirs
    if DEATH_WORDS.search(theirs) or BLEED.search(clean) or A_FEELING.search(clean):
        return None
    when = found.group("when").strip()
    if not _the_figure_is_an_hour(when):
        return None
    named = THE_NOUN_IS_AT.search(clean)
    if named and not A_MARKED_HOUR.search(when) and not _an_hour_on_the_day(named.group("noun")):
        # "the appointment is at 2:30" is the hour of the thing; "the total is at 40" is a figure
        # on a total, and the noun is what tells them apart.
        return None
    at = "At " + when
    if kind == "flat":
        pool = CLOCK_FLAT_TAIL
    else:
        pool = CLOCK_AFTER_TAIL if _clock_shape(when) == "after" else CLOCK_MORNING_TAIL
    return pick(pool, memory, clean).format(At=at[:1].upper() + at[1:], When=when[:1].upper()
                                            + when[1:], when=when)


def _hours_family(read):
    """Which kind of week the line names, and the pool that answers it.

    Six shapes people put their hours in, and the reply has to be about the one they said: a
    night shift has a body clock to it, an early start has a night before, working from home has
    no edges at all.
    """
    if ON_NIGHTS.search(read):
        return "nights", NIGHT_TAIL
    # "on lates"/"on earlies" are the shift pattern itself, not a finish time: the late and early
    # tails already say the right thing about a week of two-till-ten or six-till-two.
    if SHIFT_LATE.search(read):
        return "late", LATE_TAIL
    if SHIFT_EARLY.search(read):
        return "early", EARLY_TAIL
    if EARLY_RISE.search(read):
        return "early", EARLY_TAIL
    if LATE_FINISH.search(read):
        return "late", LATE_TAIL
    if LONG_SHIFT.search(read):
        return "long", LONG_TAIL
    if SHIFTS_ALL_OVER.search(read):
        return "spread", SPREAD_TAIL
    if WORK_FROM_HOME.search(read):
        return "home", HOME_TAIL
    return None, None


# "i have two cats as well" adds to what the bot already has, and the fact frames say so ("as
# well"); the pet tail would drop that, so a line that adds keeps the frame it had.
AS_WELL = re.compile(r"\b(?:as\s+well|too|also|another)\b", re.I)


# A child in the line is a second fact, and the kids tail is the one that answers it: "i have two
# kids n a dog called rex" is not a line about a dog. The store keeps the count under a key the
# fact frames own, so the line itself is what is read here.
A_CHILD_IN_THE_LINE = re.compile(
    r"\b(?:kid|kids|child|children|son|sons|daughter|daughters|baby|babies|toddler)\b", re.I)


# What a line can add about the pet it names and still be news of the pet: the name, the count,
# the age, and the breed. The pet tail asks how long the animal has been with them, which is the
# question for a pet arriving - it is the wrong question for a line that says how the animal
# *is*. The store can only keep the animal out of "my pug is snoring a lot", "my whippet is
# shivering" and "my mongrel is fine", so set(found) == {"pets"} held for all three and the tail
# asked "is it good company?" at somebody describing a symptom. The shape after the animal word
# is the test rather than a list of symptoms, so the next unlisted one is covered too: a name, a
# count, an age or a breed keeps the tail, and anything else after "is/are/has/got" is how the
# animal is.
PET_ADDED = re.compile(
    r"\A\s*,?\s*(?:"
    r"(?:(?:is|are|was|were)\s+)?(?:called|named)\b[\w' ]*"           # "is called biscuit"
    r"|(?:is|are|was|were)\s+(?:\d\w*|one|two|three|four|five|six|seven|eight|nine|ten"
    r"|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty"
    r"|thirty|forty|fifty)\b(?:\s*(?:years?|months?|weeks?|days?)\s*old|\s+old)?\s*\Z"
    r"|(?:is|are)\s+(?:a|an|another)\s+[\w' ]{1,20}\Z"               # "is a rescue"
    r"|,\s*\w[\w' ]*"                                                 # "two cats, milly and tom"
    r"|(?:and|with|plus|,)\s+(?:a|an|another|one|\d+)?\s*[\w' ]{1,24}\Z"  # "and a dog"
    r"|\Z"                                                             # "we got a pug"
    r")", re.I)


# The words that say the animal is all right are not a symptom: "my dog is fine now thanks" is the
# person saying the animal came through, and the store has always said that back without the
# "thanks". A line like that is a fact to echo, so it neither stands aside for an answer (which is
# what "my pug is snoring a lot" needs) nor takes the tail that asks how long the pet has been with
# them.
PET_ALL_RIGHT = re.compile(
    r"\b(?:is|are|was|were|'s)\s+(?:(?:doing|feeling)\s+)?(?:fine|ok|okay|better|well|healthy|"
    r"alright|all\s+right|great)\b", re.I)


def _a_pet_that_is_all_right(clean, kept):
    """Whether the line says the animal is fine, rather than how it is ill.

    Read after the animal word, so "my dog is fine" counts and "my dog is being sick" does not.
    """
    text = str(clean or "")
    for pet in kept or []:
        if not isinstance(pet, dict):
            continue
        word = str(pet.get("breed") or pet.get("animal") or "").strip().lower()
        if not word:
            continue
        found = re.search(r"\b" + re.escape(word) + r"s?\b", text, re.I)
        if found and PET_ALL_RIGHT.search(text[found.end():]):
            return True
    return False


# A name reaches the line from both sides. "my cat is called Biscuit" puts it after the animal
# and PET_ADDED reads it; "we named the cat Biscuit" and "i called my dog Rex" put it in front,
# and the words after the animal are the name and nothing else, so the whole line stood down
# and the person got "Thanks for telling me" for introducing their animal. The introducing verb
# has to sit right before the animal word: "i called the vet about my cat snoring" is not this,
# and the rest of that line is how the animal is anyway.
INTRODUCED_BEFORE = re.compile(
    r"\b(?:named|called)\s+(?:the|my|our|a|an|his|her|their|its)?\s*\Z", re.I)


# ...and the name is the only thing after the animal. "they called my dog a nuisance" has the
# verb in front too, and "a nuisance" is how somebody treated the animal, not what it is called.
A_NAME_AFTER = re.compile(r"\s*,?\s*[a-z][\w'-]*[.!]?\Z", re.I)


def _nothing_added_but_the_pet(clean, kept):
    """Whether the words after the animal add nothing but its name, count, age or breed.

    The animal word is the one the person used ("pug", not the store's "dog"), so a breed is
    found in the line as they said it. A line that never repeats the animal ("we got one") keeps
    the tail: the store reached an animal, and only the words beside it could say otherwise.
    """
    text = str(clean or "")
    for pet in kept or []:
        if not isinstance(pet, dict):
            continue
        word = str(pet.get("breed") or pet.get("animal") or "").strip().lower()
        if not word:
            continue
        found = re.search(r"\b" + re.escape(word) + r"s?\b", text, re.I)
        if not found:
            continue
        if PET_ALL_RIGHT.search(text[found.end():]):
            continue  # "my dog is fine now": a fact, and the echo below says it back
        if (INTRODUCED_BEFORE.search(text[:found.start()])
                and A_NAME_AFTER.match(text[found.end():])):
            continue  # "we named the cat Biscuit": the name is in front of the animal
        if not PET_ADDED.match(text[found.end():]):
            return False
    return True


# "i have lots of fish" is a number the store does not keep, and "You have a fish" is a smaller
# family than the person has. The vague quantities keep the echo.
A_VAGUE_MANY = re.compile(r"\b(?:lots|loads|plenty|several|many|a\s+few|some)\b\s*(?:of\s+)?",
                          re.I)


# What a person says to "forget the dog" when there was never a dog: the same words back, short.
ANIMAL_TAKEN_BACK = (
    "No {animal}, then.",
    "Fair enough \u2014 no {animal}.",
    "Right \u2014 no {animal}.",
)


# A want is not a take-back. "she wants a puppy", "my son would like a rabbit", "the kids have
# been asking for a hamster" and "im after a kitten" all read as a pet that is not theirs - true,
# and no use as a reply - and the take-back pool said them back as a refusal.
A_WANTED_ANIMAL = re.compile(
    r"\b(?:want|wants|wanted|wanting|would\s+like|'d\s+like|would\s+love|fancy|"
    r"fancied|i'?d\s+love|id\s+love|after|asked\s+for|"
    r"asking\s+for|been\s+asking|begging\s+for|dream(?:s|ing)?\s+of|keen\s+on|"
    r"desperate\s+for|mad\s+(?:on|for)|hoping\s+(?:for|to\s+get)|"
    r"(?:thinking|thought|talking)\s+(?:of|about)\s+getting|going\s+to\s+get)\b", re.I)


# The same words turned down: "she doesn't want a puppy", "not keen on a dog".
A_WANT_TURNED_DOWN = re.compile(
    r"\b(?:don'?t|dont|doesn'?t|doesnt|didn'?t|didnt|won'?t|wont|not|never|no\s+longer)\b"
    r"[^.!?;]{0,16}\b(?:want|wants|wanted|like|keen|after|ask(?:ed|ing))\b", re.I)


# An animal they had and do not have now: "i had a dog growing up", "we used to have a cat".
A_HAD_AN_ANIMAL = re.compile(
    r"\b(?:had|used\s+to\s+have|use\s+to\s+have|grew\s+up\s+with)\b", re.I)


# What a friend says to "i had a dog growing up": the animal is a memory, so the question is the
# one a memory invites, not a refusal.
ANIMAL_HAD_ONCE = (
    "A {animal} growing up, then \u2014 would you have another?",
    "You had a {animal} before. Do you think you would again?",
    "A {animal} when you were younger, then. What do you miss about it?",
)


# "the kids want a pet" names no animal, so the reply is the question a friend asks first.
A_PET_WANTED = (
    "Which animal are they after \u2014 a dog, a cat, something small?",
    "What have they got in mind? A pet is a long commitment and the answer changes with the animal.",
)


# A want no entry answers: the next question a friend asks about getting one.
A_WANTED_ANIMAL_TAIL = (
    "A {animal}, then \u2014 what is putting you off getting one?",
    "So you are thinking about a {animal}. Who would look after it in the day?",
    "A {animal} is a long commitment. How soon were you thinking?",
)


def _a_wanted_animal(clean):
    """True when the line asks for an animal rather than turning one down or remembering one."""
    low = str(clean or "")
    if A_WANT_TURNED_DOWN.search(low):
        return False
    return bool(A_WANTED_ANIMAL.search(low))


def _an_animal_wanted(clean):
    """The animal a line wants, or "".

    Read from the line and not from the store, because the want is often the only thing the store
    does not keep: "my son would like a rabbit" filed the son and dropped the rabbit.
    """
    low = str(clean or "")
    if not _a_wanted_animal(low):
        return ""
    for match in facts.PETS.finditer(low):
        return match.group(1).lower()
    # "the kids want a pet" names no animal at all, and the answer to that is the question which
    # one; facts.PETS is the list of animals named, so the plain word is read here.
    if PET_WORD.search(low):
        return "pet"
    return ""


def _an_animal_they_had_once(clean):
    """True when the line is an animal the person used to have, not one they are asking for."""
    low = str(clean or "")
    if _a_wanted_animal(low):
        return False
    return bool(A_HAD_AN_ANIMAL.search(low))


PET_WORD = re.compile(r"\b(?:pet|pets)\b", re.I)


# An animal on its way: "we are getting a puppy next week", "we are adopting a cat". The
# store keeps it, marked `coming`, so a later "what pets do i have" answers with what is
# here and the follow-ups still have the puppy to talk about.
ANIMAL_COMING = (
    "A {animal} on the way, then \u2014 is everything ready for it?",
    "A {animal} coming home. Have you picked a name yet?",
    "A {animal} to look forward to.",
)


# An animal on its way, not one in the house. The store marks it `coming` ("we're getting a
# puppy next month") and the follow-up that names the breed ("its a labrador") reaches the pet
# tail, whose questions - how long has it been with you, what's it like to live with, is it good
# company - are all about an animal the person has met. A friend asks the one thing that is still
# open: when it turns up.
PET_TAIL_COMING = (
    "{Thing} \u2014 when does it arrive?",
    "{Thing}. Not long now.",
    "{Thing} \u2014 the waiting is the worst part.",
)


PET_TAIL_COMING_MANY = (
    "{Thing} \u2014 when do they arrive?",
    "{Thing}. Two at once, that's a houseful.",
    "{Thing}. Not long now.",
)


def _the_pets_are_coming(pets, memory):
    """Whether the animals this line names are ones the store already has on their way.

    Read from the store and not the line: the line that says the animal is coming has its own
    reply (`ANIMAL_COMING`), and this is for the lines after it, which name the animal again
    without saying it is on its way. A puppy is a dog, so the kinds are compared rather than the
    words.
    """
    coming = set()
    for pet in ((memory or {}).get("user") or {}).get("pets") or []:
        if isinstance(pet, dict) and pet.get("coming"):
            kind = facts.ANIMAL_KINDS.get(str(pet.get("animal") or "").strip().lower(), "")
            if kind:
                coming.add(kind)
    if not coming:
        return False
    for pet in pets or []:
        if not isinstance(pet, dict):
            continue
        if pet.get("name") or (pet.get("count") or 0) > 1 or not pet.get("breed"):
            # A named animal, or more than one of them, is not the one on its way: "my dog is
            # called rex" after an announced puppy is the dog they have, and answering it with
            # the coming pool asks when Rex arrives. Only an animal the line names with nothing
            # of its own - the breed on the one coming - is read as that animal. The breed is the
            # shape the store fills in on an animal already on its way, so it is the shape this
            # reply is for: `my dog is 3` names an animal they have, and "the waiting is the
            # worst part" is about nobody.
            continue
        kind = facts.ANIMAL_KINDS.get(str(pet.get("animal") or "").strip().lower(), "")
        if kind in coming:
            return True
    return False


def _the_animal_coming(found):
    """The animal word of an animal the line says is on its way, or ""."""
    for pet in (found or {}).get("pets") or []:
        if isinstance(pet, dict) and pet.get("coming"):
            animal = str(pet.get("animal") or "").strip().lower()
            if animal:
                return animal
    return ""


def _the_taken_back_animal(found):
    """The animal word the take-back names, or ""."""
    for pet in (found or {}).get("pets") or []:
        if isinstance(pet, dict) and pet.get("not_theirs"):
            animal = str(pet.get("animal") or "").strip().lower()
            if animal:
                return animal
    return ""


def _an_animal_turned_down(found, memory):
    """True when the line is a "no" on an animal they do not have.

    "i dont want a dog" files a dog that is not theirs and, beside it, a taste of "no" on the
    dog, so the take-back reading saw a second fact in the line and declined. What answered the
    refusal was the composer, holding the answer above: "Nothing there was a dog, so the answer
    holds. A bed, two bowls, a crate or pen, a collar and lead..." - the whole dog kit handed
    back to a person who has just said no to it. A taste of "no" on the same animal is the
    refusal said in the store's own words, not another thing in the line, and an animal they do
    have keeps the store's own line.
    """
    if not isinstance(found, dict):
        return False
    pets = [pet for pet in (found.get("pets") or []) if isinstance(pet, dict)]
    if not pets or not all(pet.get("not_theirs") for pet in pets):
        return False
    if set(found) - {"pets", "tastes"}:
        return False
    animal = _the_taken_back_animal(found)
    if not animal or _on_record(animal, memory):
        return False
    named = {str(pet.get(field) or "").strip().lower()
             for pet in pets for field in ("animal", "breed")}
    named.discard("")
    tastes = [taste for taste in (found.get("tastes") or []) if isinstance(taste, dict)]
    return bool(tastes) and all(str(taste.get("thing") or "").strip().lower() in named
                                for taste in tastes)


def _on_record(animal, memory):
    """True when the store holds an animal of that kind as one of theirs."""
    user = (memory or {}).get("user") if isinstance(memory, dict) else None
    pets = (user or {}).get("pets") if isinstance(user, dict) else None
    for pet in pets or []:
        if isinstance(pet, dict) and str(pet.get("animal") or "").strip().lower() == animal:
            return True
    return False


# The animal they would like, said back: the breed is the word they used, so "i want a labrador"
# is answered about a labrador and not about a dog. The pools are the composer's line for an
# animal somebody wants ("A dog? Where are you up to with it?"), said here because the echo is
# the module that has the animal in hand and the composer has already declined the line.
WISH_FOR_AN_ANIMAL = (
    "{Thing}? Where are you up to with it?",
    "{Thing} - what's drawing you to one?",
    "{Thing}. What would you have to sort out first?",
)


# The animal is named again with a different breed, inside a plan to get one: "im thinking of
# getting a rescue greyhound" / "actually its a whippet". No question about having it can be
# asked, because there is nothing in the house yet; what is open is whether the choice is made.
A_BREED_BEING_CHOSEN = (
    "{Animal} \u2014 are you settled on that one?",
    "{Animal}, then. What made you pick that one?",
    "{Animal} \u2014 have you met one before?",
)


def _an_animal_only_planned(found, clean, memory):
    """The animal word a line renames inside a plan to get one, or "".

    Both halves are asked of the store and the subject rather than of the wording: the line gives
    one animal and no flag on it, the correction is a bare naming, and the chat is on a plan to
    get something. A line that is not a correction, or a chat that is on anything else, is left
    to the pet tail and to every other rule.
    """
    pets = [pet for pet in ((found or {}).get("pets") or []) if isinstance(pet, dict)]
    if len(pets) != 1:
        return ""
    pet = pets[0]
    if pet.get("wanted") or pet.get("coming") or pet.get("not_theirs"):
        return ""  # the store says what the animal is, and the pools above answer it
    if not topics.NAMES_THE_THING.match(" ".join(str(clean or "").lower().split())):
        return ""
    record = memory.get("topic") if isinstance(memory, dict) else None
    plan = str(record.get("text") or "") if isinstance(record, dict) else ""
    if not plan or plan.strip().lower() == str(clean or "").strip().lower():
        return ""
    if not topics.A_THING_ON_ITS_WAY.search(plan):
        return ""
    return str(pet.get("breed") or pet.get("animal") or "").strip().lower()


def _the_wished_animal(found, clean=""):
    """The animal the line wishes for, as they named it - the breed if they gave one."""
    for pet in (found or {}).get("pets") or []:
        if isinstance(pet, dict) and pet.get("wanted"):
            said = str(pet.get("breed") or pet.get("animal") or "").strip().lower()
            if said:
                return said
    words = [word for word in str(clean or "").split() if word.isalpha()]
    return words[-1] if words else "one"


def _only_a_wish(found):
    """True when everything the line gave the store is an animal the person would like."""
    if not isinstance(found, dict) or set(found) - {"pets"}:
        return False
    pets = [pet for pet in (found.get("pets") or []) if isinstance(pet, dict)]
    return bool(pets) and all(pet.get("wanted") for pet in pets)


def _an_animal_taken_back(found):
    """True when the only thing the line gave the store is an animal being taken back.

    A wish is not a take-back. "i want a labrador" and "i might get a dog" name an animal the
    person would like, and answering "No dog, then." agreed to take away a dog nobody had, and
    said no to a line that was asking about one. The store marks the two apart (`wanted`), so a
    wished-for animal declines here and the composer answers what they would do with one.
    """
    if not isinstance(found, dict) or set(found) - {"pets"}:
        return False
    pets = [pet for pet in (found.get("pets") or []) if isinstance(pet, dict)]
    if any(pet.get("wanted") for pet in pets):
        return False
    return bool(pets) and all(pet.get("not_theirs") for pet in pets)


def _the_pets_said(kept, clean=""):
    """The pets the store kept, as a person would say them: "two cats and a dog, Milly and Tom".

    The store has one entry per animal, with the count and the name beside it, so the numbers and
    the names are both there; what was missing is the sentence a friend would make of them. Two
    cats and a dog is not "two dogs", which is what counting the entries says.
    """
    number = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
              8: "eight", 9: "nine", 10: "ten"}
    groups = []
    for pet in kept or []:
        if not isinstance(pet, dict):
            continue
        # The store keeps the kind of animal and, beside it, the breed the person named: "we got
        # a rescue greyhound" is said back as a greyhound, not as a dog, because that is the word
        # they used. Two dogs of different breeds are two groups, which is right: "a greyhound
        # and a labrador" is what they have, not "two dogs".
        try:
            count = int(pet.get("count") or 1)
        except (TypeError, ValueError):
            count = 1
        # A breed named beside a group is the breed of one of them, so the group is said by its
        # kind: "we have two dogs, a lab and a terrier" is two dogs, not two terriers.
        breed_word = "" if pet.get("breed_of_one") else str(pet.get("breed") or "")
        animal = str(breed_word or pet.get("animal") or "").strip().lower()
        if not animal:
            continue
        for group in groups:
            if group[0] == animal:
                group[1] += count
                break
        else:
            groups.append([animal, count])
    if not groups:
        return "", False
    if len(groups) == 1 and groups[0][1] == 1 and A_VAGUE_MANY.search(str(clean or "")):
        return "", False
    parts = []
    for animal, count in groups:
        if count == 1:
            parts.append(("an " if animal[:1] in "aeiou" else "a ") + animal)
        else:
            word = animal if animal.endswith("s") else animal + "s"
            parts.append(f"{number.get(count, str(count))} {word}")
    said = ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]
    names = [n[:1].upper() + n[1:]
             for n in (str(pet.get("name") or "").strip() for pet in kept
                       if isinstance(pet, dict)) if n]
    if len(names) == 1:
        said += f" called {names[0]}"
    elif names:
        said += ", " + ", ".join(names[:-1]) + f" and {names[-1]}"
    many = sum(count for _, count in groups) > 1
    return said, many


def _about_them(body):
    """Whether the line is about their own life rather than the world or someone else's.

    The shape it matched is what makes it specific (HABIT or GOING), so the subject is enough
    here: "i do legs on a tuesday" and "i'm trying to save money" have no state word in them."""
    first = body.split()[0].lower().strip(",;:") if body.split() else ""
    return first in ("i", "i'm", "im", "i've", "ive", "i'd", "we", "we're", "were", "my", "our")


# "i dont know anyone here" is loneliness said as a fact, and the fact readers had nothing for it:
# the fallback answered "Got it. Is there anything you'd like a hand with?" - a shrug at the one
# line a lonely person is most likely to write. It is not a detail to file and say back either, so
# it is read before the fact frames and answered as the feeling it is.
NOBODY_AROUND = re.compile(
    r"\bi\s+(?:don'?t|do not)\s+(?:really\s+|even\s+|actually\s+)?know\s+"
    r"(?:anyone|anybody|a soul|any ?one else|a single person|one person)\b"
    r"|\bi\s*'?ve\s+(?:got|gotten)\s+no\s*(?:one|body|friends|mates)\b"
    r"|\bi\s+have\s+no\s*(?:one|body|friends|mates)\b"
    r"|\bno ?(?:one|body)\s+to\s+(?:talk|chat|go out|spend|turn)\b",
    re.I)


# The line asking who could help with something ("i dont know anyone who can look at the boiler")
# is a request for a recommendation, not a line about being alone.
NOBODY_AROUND_ASK = re.compile(r"\b(?:who|that)\s+(?:can|could|would|will|to)\b", re.I)


# "i know lots of people", "i do know someone": the same shape with the sense turned round.
ANYBODY_AT_ALL = re.compile(
    r"\b(?:know|knows)\s+(?:lots|plenty|loads|a few|some|quite a few|lots of|plenty of)\b",
    re.I)


OTHER_PERSON = frozenset("""he she they his her their hes shes theyve him them him/her""".split())


# News about somebody else that is going the right way. "my nan is in hospital" then "she should be
# out next week" was answered "I'm listening - say more if it helps", which tells the person
# nothing about the news they just gave, and "shes back at work now" was echoed back at them. The
# three shapes are different news, so each has its own pool: coming home, on the mend, back at it.
GOING_HOME = re.compile(
    r"\b(?:should|might|will|hopefully|due|going|expected|allowed)\s+(?:to\s+)?(?:be\s+)?"
    r"(?:out|home|discharged|released)\b"
    r"|\b(?:out|home|discharged|released)\s+(?:of\s+(?:hospital|there)\s+)?"
    r"(?:next week|this week|tomorrow|soon|on (?:monday|tuesday|wednesday|thursday|friday|saturday"
    r"|sunday)|in a (?:few|couple of) days|by the weekend)\b"
    r"|\bcoming home\b|\bout of hospital\b", re.I)


ON_THE_MEND = re.compile(
    r"\b(?:doing|getting|feeling|looking)\s+(?:a lot |much |a bit |so much |a little )?better\b"
    r"|\bon the mend\b|\bon the up\b|\bturned (?:a|the) corner\b|\bout of (?:the )?danger\b"
    r"|\bpicking up\b|\bback to (?:her|his|their) old self\b|\bwell on the way\b", re.I)


BACK_AT_IT = re.compile(
    r"\bback (?:at work|to work|in work|at school|on (?:her|his|their) feet|to (?:normal|it|"
    r"herself|himself|themselves|training|the gym|uni|university))\b"
    r"|\bup and about\b|\bwalking (?:again|now)\b|\bwell enough to\b", re.I)


GOING_HOME_TAIL = (
    "Out {soon} \u2014 that is the news you want. The first days at home are usually the flat ones, "
    "so keep them quiet.",
    "That is a relief. Coming home is the milestone; the tiredness tends to last a few weeks past "
    "it.",
    "Good to hear. Home beats any ward for sleeping, even with the stairs in the way.",
)
