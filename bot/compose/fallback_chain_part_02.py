"""Part 2 of 5 of the module, split out of `fallback_chain`.

Everything here is re-exported from `fallback_chain`, so callers import it from there as before.
"""

import random
import re
from ..memory import ack, facts
from ..memory import stuck as stuck_line
from . import NEARLY
from .limit import a_limit_on_the_answer
from . import loss
from .badnews import reads_like_a_symptom
from .fallback_data import (
    AIM_HEADS, A_BIRTHDAY_STILL_TO_COME, A_MOOD_WITH_A_CATCH, BEHIND_ON_MONEY, FRAME_WORDS,
    IMPERATIVE, JUNK_CUES, NEGATIVE_CUES, NOTHING_AT_ALL, CONTRAST, PAST_STATE_CUES, POSITIVE_CUES,
    A_WAIT_ENDING, SOMETHING_CAME_APART, ROUTINE, ROUTINE_NOT, ROUTINE_PHRASES, ROUTINE_WORDS,
    SOMEBODY_HURT, STATE_CUES, TOO_MUCH, TOO_MUCH_PHRASES, UNKNOWN_MONEY, _DAY_WORDS,
    _NO_DAY_OF_THEIR_OWN, _START_ASK,
)

# The day that went badly and the name that came from somebody: the pools those readings choose
# from. They are in the data file with the rest, and the readings that use them live here.
from .fallback_data import HURT_EVENT

# What the moved rows take from fallback.py, which is fully defined by the time this
# module is imported, because fallback.py imports it from its own last line.
from .fallback_part_02 import _money_decision
from .fallback_part_05 import LATE_ASKS, LATE_NOT_A_TIME, LATE_NOT_IT, LATE_NOW
from .fallback_part_08 import _in_a_care_thread
from .fallback_part_11 import _reads_as_question
from .fallback_part_14 import _a_mood_word, _in_an_aim, _reads_as_illness
from .fallback_part_15 import OWN_THING, _words
from .fallback import (
    AIM_HEADS, A_BIRTHDAY_STILL_TO_COME, A_MOOD_WITH_A_CATCH, BEHIND_ON_MONEY, FRAME_WORDS,
    HURT_EVENT, IMPERATIVE, JUNK_CUES, NEARLY, NEGATIVE_CUES, PAST_STATE_CUES, POSITIVE_CUES,
    ROUTINE, ROUTINE_NOT, ROUTINE_PHRASES, ROUTINE_WORDS, SOMEBODY_HURT, STATE_CUES, TOO_MUCH,
    TOO_MUCH_PHRASES, UNKNOWN_MONEY, _DAY_WORDS, _NO_DAY_OF_THEIR_OWN, _START_ASK, ack, facts, loss,
    random, re, reads_like_a_symptom, stuck_line,
)
from .fallback_chain_part_01 import (
    HABIT_NOT, HABIT_STATED, _habit_is_a_problem, _A_BODY_WORD, _A_HARM_HAD, _A_HARM_IDIOM,
    _A_HARM_ILL, _A_HARM_ILL_NOT, _A_HARM_KNOCK, _A_HURT_BY_SOMEONE, _A_HURT_BY_SOMEONE_NOT,
    _A_HURT_DONE, _A_IN_AGONY, _A_OUT_OF_SOCKET, _A_PART_OUT, _A_PART_WENT, _A_PROGNOSIS,
    _A_PROGNOSIS_THAT_IS_NOT, _a_state_in_the_past, _a_thing_stopping_after, _cue_negated,
    _the_win_is_someone_elses, reads_as_no_pleasure,
)


def reads_as_a_flat_habit(text, understood=None):
    """Whether the composer's habit pool claims this line.

    Read by `chat` before it turns the same line into its own stock question ("Annoying. Is it
    the same every time, or does it vary?"): a habit said flatly is answered here, and the
    module above stands aside so the two readings cannot disagree about who answers. So this is
    the branch's own gate and nothing else - a recurrence and a doing, no question, and no mood
    word. A claim the reply does not keep is worse than no claim at all: `chat` would stand down
    and the echo ("Noted: you keep interrupting your sister") would answer instead.
    """
    # The line as typed, and then the line with its words put right: a word typed onto the next
    # one ("icant stop crying", "ialways leave things to the last minute") hides the doing from
    # this gate, and the reading has already split it (`understood["plain"]`). The typed line is
    # asked first, so a line that reads whole is read exactly as it was typed.
    said = [str(text or "")]
    repaired = (understood or {}).get("plain") if isinstance(understood, dict) else None
    if repaired and repaired != said[0]:
        said.append(repaired)
    for line in said:
        if _flat_habit_stated(line):
            return True
    return False


def _flat_habit_stated(raw):
    """The gate itself, for one spelling of the line."""
    clean = " ".join(raw.lower().split())
    words = clean.split()
    try:
        return bool(HABIT_STATED.search(clean) and not HABIT_NOT.search(clean)
                    and _mood(words, clean) == "neutral"
                    and not _reads_as_question(raw, words)
                    and _habit_is_a_problem(clean))
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return False


def _a_harm_said(clean):
    """True when the line reports a harm done to the person, or an illness they have.

    Read by `_mood`, so the line is a bad line and the warm pool answers it rather than the day
    pool asking how it went. A line that already says it is over ("i broke my wrist years ago")
    is still a harm they told the bot about, and the warm line fits it better than a cheer.
    """
    said = " ".join(str(clean or "").lower().split())
    if not said:
        return False
    if _A_HARM_IDIOM.search(said):
        return False
    if _A_PART_OUT.search(said):
        return True
    if _A_PROGNOSIS.search(said) and not _A_PROGNOSIS_THAT_IS_NOT.search(said):
        return True
    if _A_HURT_DONE.search(said) and _A_BODY_WORD.search(said):
        return True
    if _A_HURT_BY_SOMEONE.search(said) and not _A_HURT_BY_SOMEONE_NOT.search(said):
        return True
    if _A_HARM_ILL.search(said) and not _A_HARM_ILL_NOT.search(said):
        return True
    return bool(_A_HARM_HAD.search(said) or _A_PART_WENT.search(said)
                or _A_HARM_KNOCK.search(said) or _A_OUT_OF_SOCKET.search(said)
                or _A_IN_AGONY.search(said))


# A record broken is an achievement and an ice broken is a room warming up, but "broke" is a bad
# cue because a wrist, a phone and a boiler break: somebody who had just broken a running record was
# condoled ("Ugh, that's a lot to carry. What would make today a bit easier?"). The thing broken is
# what says which it is, so the phrases where it can only be good are read out before the cue.
_A_BREAK_THAT_IS_GOOD = re.compile(
    r"\bbroke(?:n)?\s+(?:a|the|my|our|his|her|their|new|world|personal|course|club|national)\s+"
    r"(?:\w+\s+)?(?:records?|ice|sweat|ground|habit|cycle|deadlock|stalemate|personal\s+best)\b"
    r"|\bbroke\s+even\b"
    # "i broke through" is done with something, and "i broke through the wall" is a wall: the
    # phrase only counts where nothing follows it.
    r"|\bbroke\s+through\b(?!\s+(?:the|a|an|my|our|his|her|their)\s)"
    r"|\bbreak(?:ing)?\s+a\s+record\b", re.I)


_BREAK_WORDS = frozenset(("broke", "broken", "breaking", "breaks"))


def _mood(words, clean=""):
    """'positive', 'negative' or 'neutral', from the words of a statement.

    A cue only says which way the line goes when nothing in front of it turns it round: "not
    happy" is a bad line, not a good one, and a cue that is turned round the other way ("not
    terrible") is left out rather than counted either way. Without this the cheerful pool
    congratulates someone who has just said they feel awful, which is the reply people
    remember. A cue inside an aim is not a mood at all ("i want to lose weight"), and neither is
    one behind "nearly"/"almost" ("i nearly finished it"), which is not done and not condoled.
    """
    words = tuple(words)
    # A stated dislike is a fact about their taste, not a bad day: "hate" and "can't stand" are
    # mood words too, and "that sounds rough" is an answer for something that happened to them.
    if ack.only_a_dislike(clean):
        return "neutral"
    # A limit on the answer above is not a mood: the pleasure word inside it is part of the thing
    # the person is asking to leave out (see a_limit_on_the_answer).
    if a_limit_on_the_answer(clean):
        return "neutral"
    # The pleasure gone out of everything is read before the cues, because its own words are the
    # cheerful ones: "nothing makes me happy" is the low line the pool is for, not good news.
    if reads_as_no_pleasure(clean):
        return "negative"
    good = bad = False
    if "ill" in words and _reads_as_illness(clean):
        bad = True
    # A symptom said with nothing else around it ("ive got a sore throat", "ive got a rash on my
    # arm") is already looked after by the symptom pools, and reading it as a harm here sends it to
    # the generic acknowledgement instead ("That sounds rough. If you want, I can help you think
    # through what to do next") - the line that used to say what to do. A harm that is an injury,
    # a knock, a diagnosis or a thing done to them still reads as bad.
    if not good and _a_harm_said(clean) and not reads_like_a_symptom(clean):
        bad = True
    for i, word in enumerate(words):
        if _in_an_aim(clean, word):
            continue
        # "bit of a rubbish week" is a mood and "take the rubbish out" is a chore: a word that
        # is also a thing only counts where something says what a thing was like (see JUNK_CUES).
        if word in JUNK_CUES and _a_mood_word(words, word):
            bad = True
            continue
        if word in _BREAK_WORDS and _A_BREAK_THAT_IS_GOOD.search(clean):
            # "i broke a record" is the best day of the year, and the cue would have condoled it.
            good = True
            continue
        if word not in POSITIVE_CUES and word not in NEGATIVE_CUES:
            continue
        # A cue with an everyday sense of its own is only a mood where the sentence around it
        # says so. "fired" is the one here: "i got fired" and "i was fired" are a job gone, and
        # "they fired me" the same, but "i fired a pot in the kiln yesterday" is pottery and "i
        # got fired up about the match" is the opposite of a bad day - both were answered "sorry
        # to hear that" and "that's frustrating" for a good afternoon.
        if word in A_MOOD_WITH_A_CATCH:
            before = set(words[max(0, i - 3):i])
            after = words[i + 1] if i + 1 < len(words) else ""
            if after == "up":
                # "i got fired up about the match" is keen, not a bad day: the phrase is the
                # opposite of the cue's sense, so it is the cheerful pool's, not nobody's.
                good = True
                continue
            if not (before & A_MOOD_WITH_A_CATCH[word]) and after not in ("me", "him", "her",
                                                                          "them", "us"):
                continue
        # Any of the three words before it can turn it round: "didn't get the job", "not at
        # all happy".
        window = words[max(0, i - 3):i]
        if set(window) & NEARLY:
            continue
        back = _cue_negated(words, word)
        if word in PAST_STATE_CUES and _a_state_in_the_past(words, i):
            # A state that was is not news now: "my wife was pregnant" was congratulated by the
            # bare cue in POSITIVE_CUES, and a pregnancy that is over is the last thing to be
            # cheerful about. An event in the past is still an event ("i was promoted" is news
            # they want to hear), so this reads the state words only.
            continue
        if word in POSITIVE_CUES and _a_thing_stopping_after(words, i):
            # The cue is spent: a thing that stopped is not a thing to cheer.
            continue
        if word in POSITIVE_CUES:
            # "nothing makes me happy any more" is not good news with a "not" in front of it:
            # the cue is turned round by the word saying there is none of the thing, and a
            # friend hears the complaint rather than the cue.
            if _no_such_thing_before(words, i):
                back = True
            if back:
                # "not happy" is a bad line. Not every turned word is: a result is not
                # congratulated and not condoled either - "i never finished it" is a plain fact,
                # and "that sounds rough" would be reading a feeling into it.
                if word in STATE_CUES:
                    bad = True
            elif word in A_WAIT_ENDING and SOMETHING_CAME_APART.search(clean or ""):
                # "the boiler finally died" is a wait that ended in a broken boiler, not good
                # news: the cue is about the wait, and the line says what came of it. The line
                # falls through to the readers below rather than to the negative pool, because a
                # thing that broke is a job to do more often than a loss to be condoled.
                continue
            elif _the_win_is_someone_elses(words, i):
                # Somebody else's win is not a reason to cheer them: "everyone else has got it
                # sorted and i havent" is a person saying they are behind, not a person telling
                # you good news. The cue is spent, so the line falls through to the readers
                # below it rather than to the negative pool.
                continue
            else:
                good = True
        elif not back or set(window) & AIM_HEADS:
            # A negated aim is the fear itself: "i dont want to lose the house" is not a denial
            # of the loss, it is the loss they are afraid of.
            bad = True
    if bad:
        return "negative"
    if good:
        return "positive"
    return "neutral"


def _no_such_thing_before(words, i):
    """True when the cue is the thing a word meaning none of it is said about.

    "nobody makes me feel good" puts three words between the quantity and the cue, so the
    three-word window the negators are read in is not wide enough; a contrast word starts a new
    claim and ends the search ("nobody believed i could do it but i did" is good news).
    """
    for step in range(1, 9):
        if i - step < 0:
            return False
        word = words[i - step]
        if word in CONTRAST:
            return False
        if word in NOTHING_AT_ALL or (word == "one" and i - step - 1 >= 0
                                      and words[i - step - 1] == "no"):
            return True
    return False


def _mixed_seed(text):
    """A number that changes when the line changes.

    `_choose` adds up letter values, which two lines of the same length can share: the four
    outcome pools are all about the same length, so a sum gave several threads the same sentence.
    """
    value = 7
    for char in str(text or ""):
        value = (value * 31 + ord(char)) % 1000003
    return value


# A pool line that tells the person how they feel is only drawn when the line gives a sign of
# feeling. "my mum is moving to spain in june" is a plan somebody is watching take shape, and the
# leaving pool answered it "Nobody has done anything wrong and it still hurts" - a hurt the person
# never mentioned, said with sympathy for a decision that may be half proud. The same pool's other
# lines ask instead of telling ("how far is it, and are you a phone-call pair"), so the plan keeps
# an answer either way.
#
# Only an assertion counts: a feeling word inside a question is the reply asking, not the bot
# telling - "what will you miss most?" is a fair thing to ask about a move nobody has called sad -
# so a line is dropped when one of its *statements* names a feeling.
SAYS_A_FEELING = re.compile(
    r"\b(?:hurts?|hurting|stings?|stung|miss(?:es|ed)?|dreading|dreads|sad|upset|gutted|"
    r"lonely|ach(?:e|es|ing|y)|cry(?:ing)?|broken|struggling|hate|worried|devastated)\b",
    re.IGNORECASE)


A_FEELING_IN_THE_LINE = re.compile(
    r"\b(?:hurts?|hurting|stings?|stung|(?:will|do|would|could)\s+miss|miss(?:es|ed)\b(?!\s+\?)|"
    r"dreading|sad|upset|gutted|lonely|ach(?:e|es|ing|y)|cry(?:ing)?|broken|struggling|hate|"
    r"worried|devastated|hard|tough|quiet|empty)\b",
    re.IGNORECASE)


def _only_what_the_line_gives(pool, clean):
    """The pool minus the lines that tell the person how they feel, unless they said it."""
    if A_FEELING_IN_THE_LINE.search(clean or ""):
        return pool
    kept = []
    for line in pool:
        asserts = False
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            if sentence.rstrip().endswith("?"):
                continue
            if SAYS_A_FEELING.search(sentence):
                asserts = True
                break
        if not asserts:
            kept.append(line)
    return tuple(kept) or pool


def _choose(options, memory, clean, seed_text=None):
    """One option, varied by the line itself and never the reply just given.

    A pool as short as NEUTRAL's three lines cannot keep the five-reply promise: once all three
    are in the window nothing is fresh, and restoring the whole pool brings back the line just
    used - "stacked up with emails" straight after "back to school", two of the same kind of
    reply in a row, which reads like the bot stopped listening. So the wide window holds while
    it can, and what is never repeated is the reply just given.
    """
    turns = memory.get("turns") or []
    recent = [t.get("bot") for t in turns[-5:] if t.get("bot")]
    fresh = [o for o in options if o not in recent]
    if not fresh:
        last = recent[-1] if recent else None
        fresh = [o for o in options if o != last] or list(options)
    if not fresh:
        # Nothing to say: a pool the conversation has emptied is not an answer, so this returns
        # None and the reading that called it stands down. `choice` on an empty list raised
        # IndexError, which took the whole composer with it - every later reading in reply_for
        # never ran, the module proposed nothing, and the turn became the runtime's "Hello!".
        return None
    if seed_text is None:
        seed = len(turns) * 7919 + sum(ord(c) for c in clean)
    else:
        seed = len(turns) * 7919 + _mixed_seed(seed_text)
    return random.Random(seed).choice(fresh)


def _a_birthday_still_to_come(clean, memory):
    """The one birthday this line gave a figure for, from the people the store now holds.

    The store keeps a birthday still to come beside the age the person is ("my mum is 72 and she
    is 73 next month" is 72 now, 73 next month), so the figure and the day are both there to say
    back. Only the entry whose number and day are in this line counts, so an age filed turns ago
    cannot take over a line about somebody else, and only one entry: two birthdays in one line is
    not one thing to name.
    """
    said = " ".join((clean or "").lower().split())
    if not said:
        return None
    met = []
    for one in memory.get("others") or []:
        if not isinstance(one, dict) or one.get("pronoun") or not one.get("who"):
            continue
        age, when = one.get("to_come"), " ".join(str(one.get("turns") or "").lower().split())
        if not isinstance(age, int) or not when:
            continue
        if str(age) not in said or when not in said:
            continue
        met.append(one)
    return met[0] if len(met) == 1 else None


def _the_birthday_said_back(birthday):
    """The pool above with the person, the figure and the day filled in."""
    who = str(birthday.get("who") or "").lower()
    if who and not who.startswith(("your ", "my ")):
        who = "your " + who
    age = str(birthday.get("to_come"))
    when = " ".join(str(birthday.get("turns") or "").split())
    said = []
    for line in A_BIRTHDAY_STILL_TO_COME:
        line = line.replace("{who}", who).replace("{age}", age).replace("{when}", when)
        said.append(line[:1].upper() + line[1:])
    return tuple(said)


# "a 3 year old", "an 8-year-old": the child's day, not the adult's.
_ROUTINE_NOT_SHAPE = re.compile(r"\b\d+\s*-?\s*year\s*-?\s*old\b")


# A named undertaking is a project, not the shape of a day: "a to do list for my wedding",
# "to do list for moving house", "where do i start with my divorce", "get organised for the
# move". Planning a thing
# wants the order of the work on that thing, which a day pool cannot give, so the pools stand
# aside where something that knows the subject can answer. The lines this leaves are ones that
# hedged before, so standing aside costs a gain and never a loss.
_UNDERTAKING = re.compile(r"\b(?:for|with|about)\s+(?:my|our|the|a|an|this|that)?\s*([a-z']+)")


def _somebody_elses_day_in_thread(memory):
    """True when the thread, not the line, belongs to somebody else's day.

    `the baby is 8 months and still not sleeping through` / `weve tried a bedtime routine`: the
    second line names nobody, so the words on the line cannot see the baby, and the method for
    an adult's day ("give it a fixed slot - what are you not getting to?") answers nothing in
    that thread. The line before it is the whole of the test, and it is read for the same words
    the line itself is read for - no module has to have answered it, because a chat line naming
    a puppy is as much a puppy thread as a knowledge line naming one.

    A death is the exception, and it is the reason this is not just a word check: `my dog died
    last night` then `help me get organised` is a person arranging their own day while grieving,
    and a dog that has died has no routine to protect.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-1:]
    for turn in turns:
        said = str(turn.get("user") or "").lower()
        if any(word in said for word in _NO_DAY_OF_THEIR_OWN) or loss.reads_as_loss(said):
            return False
        said_words = set(w.strip(".,!?;:'\"()") for w in said.split())
        if said_words & ROUTINE_NOT or _ROUTINE_NOT_SHAPE.search(said):
            return True
    return False


# The words that put a list of things on the table. A line that says "i dont know where to start"
# is asking about one only where one of these has already been said.
A_LIST_ON_THE_TABLE = re.compile(
    r"\b(?:too much|lots (?:on|of|to)|a lot (?:on|to)|so much|everything|list|lists|jobs|"
    r"things|plates|spinning|juggling|overwhelmed|swamped|drowning|stretched|spread thin|"
    r"deadlines?|behind|catch(?:ing)? up|workload)\b")


def _the_person_named_a_list(memory):
    """Whether the person's own last line or two put a list of things on the table.

    Only their lines: the bot's last reply is not evidence of a list, because the cards that are
    not about lists at all ("ring a crisis line now", "here is one about a parrot") would pass
    for one and the size-of-the-list pool would answer them.
    """
    if not isinstance(memory, dict):
        return False
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-2:]
    return any(A_LIST_ON_THE_TABLE.search(str(turn.get("user") or "").lower()) for turn in turns)


def _routine_pool(clean, words, memory=None):
    """The pool for a line about the shape of the speaker's day, or None if it is not one."""
    words = set(words)
    # A list with too much on it, asked for after the bot has just said to get seen today:
    # "my chest hurts when i run" then "i dont know where to start" was answered "the useful
    # question is what to drop", which ignores the one thing that matters and would fit any
    # message. The advice already given is the whole of today's list, and the rest keeps.
    if memory is not None and stuck_line.the_advice_was_to_get_seen(memory) and (
            any(phrase in clean for phrase in TOO_MUCH_PHRASES)
            or words & {"overwhelmed", "drowning", "swamped"}):
        return stuck_line.URGENT_ALREADY_GIVEN
    # The size of the speaker's own list is theirs whatever the list is made of: "im spread too
    # thin with work and the kids" is a list with kids in it, not a child's routine.
    if any(phrase in clean for phrase in TOO_MUCH_PHRASES if phrase not in _START_ASK):
        return TOO_MUCH
    # "im always late paying my rent" is somebody's money problem and not the shape of the day:
    # the day method would tell them what time to get up. The money pool names a free adviser and
    # asks what matters, which is the most a bot can honestly offer on another person's arrears.
    if _money_decision(clean) and words & BEHIND_ON_MONEY:
        return UNKNOWN_MONEY
    if any(word not in _DAY_WORDS for word in _UNDERTAKING.findall(clean)):
        return None
    if words & ROUTINE_NOT or _ROUTINE_NOT_SHAPE.search(clean):
        return None
    if memory is not None and _somebody_elses_day_in_thread(memory):
        return None
    if any(phrase in clean for phrase in ROUTINE_PHRASES):
        return ROUTINE
    if words & ROUTINE_WORDS:
        return TOO_MUCH if words & {"overwhelmed", "drowning", "swamped"} else ROUTINE
    if any(phrase in clean for phrase in _START_ASK):
        # "i dont know where to start" names nothing on its own: it is the stuck line, and what
        # the size-of-the-list pool has to say depends on whether there is a list. The person's
        # own line before it is the whole of the test - "i have too much on at work" then "i dont
        # know where to start" is a list to shorten, while after a crisis card, an abuse card or
        # a joke the same words got "the useful question is what to drop rather than how to fit
        # it in", which is an answer to a message nobody sent.
        return TOO_MUCH if _the_person_named_a_list(memory) else None
    return None


def _asks_the_bot(understood):
    """True when the line asks the bot for something: an imperative, or an ask for options."""
    if set(understood.get("asks") or ()) & {"recommend", "steps", "options"}:
        return True
    norm = understood.get("norm") or []
    return bool(norm) and norm[0] in IMPERATIVE


def _words(text):
    """The words of a line the way `_mood` wants them: lowercase, no punctuation."""
    return tuple(re.findall(r"[a-z']+", str(text or "").lower()))


def _reads(pred, clean, repaired, lower=False, memory=None):
    """True when a cue reads the typed line or the same line with its words put right.

    "me n my gf r arguin a lot" is the same line as "my girlfriend and i keep arguing a lot",
    and the reading has already repaired it (bot/understanding's `plain`): the cue "arguing" is
    in what the person said even though they typed "arguin". Every pool in this file tests the
    typed line first, so a line that reads with no repair is untouched; the repaired line is
    only ever a second try, never a replacement.
    """
    def ask(text):
        return pred(text.lower() if lower else text, memory) if memory is not None else pred(
            text.lower() if lower else text)
    if ask(clean):
        return True
    if repaired and repaired != clean:
        return bool(ask(repaired))
    return False


ASK_SHAPE = re.compile(r"\b(?:should|could|can|do|does|did|is|are|was|were|will|would|shall|"
                       r"what|when|where|which|who|why|how|any)\b")


# The reading sometimes leaves the frame itself at the front of `focus` ("no i mean is that
# bad"), so it is cut off before the pointed-at words are read: answering the frame again is
# how the recursion came back with the acknowledgement instead of the verdict line.
FRAME_PREFIX = re.compile(
    r"^(?:(?:no|nah|nope|sorry|ok|okay|wait|oops|actually|oh|right|and|but),?\s+)*"
    r"(?:i\s+(?:mean|meant|said)|scratch\s+that|wait\s+no|no\s+wait|i\s+mean\s+to\s+say)\s+",
    re.I)


def _restated(understood):
    """The ask a correction points at ("no i meant <this>" -> "<this>"), or the empty string."""
    if understood.get("intent") != "correction":
        return ""
    focus = " ".join(understood.get("focus") or []).strip()
    focus = FRAME_PREFIX.sub("", focus).strip(" ,.!?")
    if len(focus.split()) < 2:
        return ""
    if all(word.lower() in FRAME_WORDS for word in focus.split()):
        return ""
    # Only an ask is answered again. The pointed-at words of a correction that swaps one named
    # thing for another ("sorry, i meant porto not lisbon", "sorry i meant my brother") are not
    # a question, and the pools below have nothing more to say about them than the line already
    # gets: answering those would put a shrug where an acknowledgement was.
    if not ASK_SHAPE.search(focus.lower()):
        return ""
    return focus


# A thing of the person's own that the line has put a mood word on: "my lawn looks sad", "my
# curtains look miserable", "our boiler is knackered". The possession is what makes the question
# the thing's own - "the weather is miserable" is a moan about the day and its answer is an
# agreement, not a fault to find.
# A thing of the person's can be said with the owner in front of it ("my lawn") or with having it
# ("i have a lawn that looks sad"): both put the thing in the line, and the reading says the state
# is the thing's either way. A body part is not this - "i have a bad back" is the person's own
# state, and the reading says so - and neither is a state the reading leaves on the speaker.
OWN_THING = re.compile(r"\b(?:my|our)\s+[a-z]"
                       r"|\b(?:i|we)\s*(?:'ve|ve|have)\s+(?:got\s+)?(?:a|an|some|two|three|four|"
                       r"a few|another)\b")


# The words that make it a *mood* on a thing rather than a quality of it: "my car looks sad" is a
# thing of the person's gone sorry, while "my pasta is tough" and "my cake is flat" are the food
# being wrong and belong to the cooking answers, not here.
A_MOOD = re.compile(r"\b(?:sad|miserable|unhappy|depressed|lonely|dejected|glum|sorry for itself|"
                    r"in the wars|seen better days)\b")


# A near miss is not a result. The pools below read the result the line names and the "almost"
# in front of it is left to `nearly`, which only says the line is not good news; nothing then
# answers it, and the day pool takes it. What a friend says is that nearly is its own kind of
# hard and asks the one thing worth asking about it. The reading is the achievement only: a
# thing that nearly went wrong ("i nearly broke my arm", "the boiler nearly died") is a fault
# or a fright and belongs to the cards that read it, so those are not here.
NEAR_MISS = re.compile(r"""
    \b(?:almost|nearly|just\s+about)\s+
    (?:
        won\b
      | beat\s+(?:him|her|them|it|everyone|the\s+\w+)
      | broke\s+(?:the|my|a)\s+(?:\w+\s+)?(?:record|pb|best|streak)\b
      | passed\b(?!\s*(?:out|away|on|wind|water|blood|a\s+stool)\b)
      | got\s+(?:the|that|my)\s+(?:job|place|part|role|promotion|record|pb)\b
      | got\s+(?:it|in|through)\b
      | made\s+it\b
      | qualified\b
      | came\s+(?:first|second|third|top)\b
      | scored\b
    )
""", re.I | re.X)


# Written to fit a result of theirs whoever had it: "i almost won", "we nearly won the quiz" and
# "my daughter nearly won her race" are all the same near miss, so none of the four says "you".
NEAR_MISS_REPLY = (
    "So close. Was there a last bit that got away, or was it lost earlier than that?",
    "Almost is its own kind of annoying, being right there. What happened at the end?",
    "Ugh, that is the hardest way to miss something. Will there be another go at it?",
    "That is a hard one to sit with, because nearly is not the same as not good enough. What "
    "would have made the difference?",
)


def _a_near_miss(clean):
    """Whether the line is a result they almost had ("i almost got the job", "i nearly won")."""
    return bool(NEAR_MISS.search(str(clean or "")))


def _a_things_state(memory, clean):
    """Whether the state the line names belongs to a thing of the person's, not to the person.

    "my lawn looks sad" is a report about a lawn; "im sad" is a person's own state, "my mum is sad"
    is somebody else's, and "the weather is grim" is the day rather than a thing that can be seen
    to. The shared reading in memory already says whose the state is (state_owner), so the composer
    asks it rather than re-reading the line.
    """
    understood = (memory or {}).get("understood") or {}
    text = str(clean or "").lower()
    return (understood.get("state_owner") == "thing"
            and bool(OWN_THING.search(text)) and bool(A_MOOD.search(text)))


# The openers a correction is said with ("sorry,", "actually,", "no wait"). Taken from the reader
# that files a corrected fact, so this and that agree on what a correction looks like.
_A_CORRECTION = re.compile(facts.CORRECTION_LEAD, re.I)


# A line that opens by taking something back. The two pools already here cover the withdrawal
# ("never mind", "forget it" - NEVER_MIND) and the apology ("sorry" on its own - SORRY_ON_ITS_OWN),
# but not the correction: "no it was my idea not the kids" after the bot asked which of the party
# games the children had picked, "no the quiet is the best bit of it" after an answer about the
# noise. Both reached the search hedge - "I don't know enough to answer that honestly. A search
# should sort you out quickly" - which tells a person setting the record straight to go and look
# it up, and the party line also reached the kids' games card, because "party" was still in it.
# A correction is a reply to this end of the chat, not a question about the world, so nothing in
# it is a subject to look up. The opener is read strictly: an apologetic "sorry", an "oh" and a
# plain "actually" are how people open all sorts of lines, and only the retracting words count.
TAKING_SOMETHING_BACK = re.compile(
    r"^\s*(?:(?:ok|okay|right|so)\s*[,.]?\s*)?"
    # "no one at work likes me" and "no body tells me anything" open on "no" and are the
    # sentence, so "one" and "body" are not read as the thing being put right.
    r"(?!no\s+(?:one|body)\b)"
    r"(?:no|nope|wait|hold\s+on|hang\s+on|scratch\s+(?:that|it)|forget\s+(?:it|that)|"
    r"my\s+mistake|i\s+(?:got|had)\s+(?:that|it|this)\s+wrong|i\s+made\s+a\s+mistake|"
    r"i'?m\s+wrong|(?:sorry\s*,?\s*)?i\s+(?:mean|meant))\b", re.I)


# What makes the remainder a thing said rather than a noun phrase attached to "no": a verb ("no it
# was my idea"), or the thing itself behind its article ("no the blue one", "no the quiet is the
# best bit of it"). "no onions in it" and "no heating since friday" have neither - they are
# somebody saying what they have not got, which is the sentence and keeps its answer.
SAYS_A_THING = re.compile(
    r"\b(?:is|are|was|were|am|be|been|being|do|does|did|done|have|has|had|can|could|will|would|"
    r"shall|should|must|might|may|its|it's|thats|that's|hes|he's|shes|she's|theyre|they're|"
    r"we're|youre|you're|im|i'm|ive|i've)\b|\w+ed\b", re.I)


THE_THING_ITSELF = re.compile(r"^(?:the|these|those|this|that)\b", re.I)


# What comes after the opener and turns it back into a question: "no what about the other one",
# "no can i do it tomorrow". The ask is the line's, and the pools above answer it.
ASKS_AFTER_THE_OPENER = re.compile(
    r"^\s*(?:what|how|why|when|where|who|which|can|could|should|would|will|do|does|did|is|are|"
    r"was|were|have|has|any)\b", re.I)


# "ok so", "no no", "wait - sorry": an opener stacked on another, which the same line often has.
THE_OPENER = re.compile(r"^\s*(?:(?:ok|okay|right|so|no|nope|wait|ah|oh|sorry)\s*[,.]?\s*)+", re.I)


def _a_chat_to_correct(memory):
    """Whether the bot has said anything this chat for a line to be putting right."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for turn in turns or ():
        if isinstance(turn, dict) and str(turn.get("bot") or "").strip():
            return True
    return False


def _takes_something_back(clean, memory=None):
    """True when the line opens by correcting something and is not then asking a question.

    "no it was my idea not the kids" is the person putting the bot right about who had the idea.
    Three things keep it to that. The chat has to be under way, because a correction is a reply to
    something said here and "no onions in it" as the opening line is somebody telling the bot what
    they are cooking. The line must not go on to ask anything ("no what about the other one"). And
    the rest of it has to say a thing rather than name one: a verb, or the thing behind its own
    article. A correction with nothing on the end of it ("no", "no that's not it") is the
    withdrawal pool's, and "no heating since friday" is the sentence.
    """
    text = " ".join(str(clean or "").split())
    if not text or "?" in text or not TAKING_SOMETHING_BACK.match(text):
        return False
    if not _a_chat_to_correct(memory):
        return False
    body = THE_OPENER.sub("", text, count=1).strip(" ,.;:-")
    if body and TAKING_SOMETHING_BACK.match(body):
        body = THE_OPENER.sub("", TAKING_SOMETHING_BACK.sub("", body, count=1), count=1)
    if len(body.split()) < 2 or ASKS_AFTER_THE_OPENER.match(body):
        return False
    return bool(SAYS_A_THING.search(body) or THE_THING_ITSELF.match(body))


def _a_lateness_report(clean, normalised=""):
    """The speaker's own lateness, stated and not asked about - the one line the pool is for.

    Read off the typed line first, then off the reading's `norm_text` when that found nothing:
    chat-speak is written the way people type it, and the reader has already put it back into
    words (`gona` -> "going to", `bot/understanding/normalize.py`). "im gona be late for work"
    is the same report as "im gonna be late for work", and the pool that read only the typed
    words answered a person rushing out of the door with the neutral nod.
    """
    if "?" in clean or len(clean.split()) > 12:
        return False
    if LATE_ASKS.search(clean) or LATE_NOT_A_TIME.search(clean):
        return False
    if _mood(_words(clean), clean) != "neutral":
        return False
    read = clean
    hit = LATE_NOW.search(read)
    if hit is None and normalised:
        # `norm_text` keeps a clause break as " | ", which no word pattern reaches across.
        read = " ".join(normalised.replace(" | ", " ").split())
        hit = LATE_NOW.search(read)
    if hit is None:
        return False
    between = hit.group(1) or ""
    if LATE_NOT_IT.search(between):
        return False
    # "im behind with my sleep" is a body short of rest, not work left undone, and "what has
    # held you up" is the wrong question for it. `loss.SELF_NOUNS` is the censused list of the
    # words for a part of somebody's own life rather than a thing in the world, so a "behind"
    # that hangs on one of them stands down and the floor answers as it did before. Only "behind":
    # a late-for-work line is about a place and keeps its pool.
    if (hit.group(0) or "").endswith("behind"):
        after = read[hit.end():]
        if any(word in loss.SELF_NOUNS for word in re.findall(r"[a-z']+", after)):
            return False
    return True


# A person the line can hurt: "my son", "our neighbour", "her mum". Never the speaker - "my back
# is killing me" is their own body, with its own answers - and never an animal, because "my dog
# was attacked by a wasp" is the dog's problem and none of these lines is right for it.
HURT_SOMEBODY = re.compile(
    r"\b(?:my|our|his|her|their|the)\s+(?:son|daughter|boy|girl|child|kid|baby|mum|mom|mother|"
    r"dad|father|brother|sister|husband|wife|partner|boyfriend|girlfriend|friend|mate|"
    r"neighbour|neighbor|grandad|granddad|grandma|gran|nan|nana|uncle|aunt|auntie|cousin|"
    r"colleague|flatmate|housemate|carer|teacher|boss|fella|lass|lad|family)\b")


# The end of the news: "my nan slipped in the bath but she's ok", "nothing broken, just bruised".
# The pool asks how somebody is, and the person has already said it.
HURT_BUT_FINE = re.compile(
    r"\bbut\s+(?:he|she|they|hes|shes|theys|it)(?:'s|\s+is|\s+was|\s+seems)?\s*"
    r"(?:ok|okay|alright|fine|good|bruised|home)\b"
    r"|\b(?:he|she|they)(?:'s|\s+is|\s+seems)\s+(?:ok|okay|alright|fine)\b"
    r"|\bnothing\s+(?:broken|serious|bad)\b|\bnot\s+(?:too\s+bad|serious)\b"
    r"|\bonly\s+(?:a\s+)?(?:bruise|scrape|scratch|graze)\b")


# A fall about laughing is not a fall: "my dad collapsed laughing" and "my son fell about" were
# getting "Is your dad alright?".
HURT_FIGURE = re.compile(
    r"\b(?:collapsed|fell|fall|falls)\b[^.!?]{0,12}?\b(?:laughing|about|over\s+laughing|ill|"
    r"sick\s+with\s+laughter)\b"
    r"|\b(?:fell|fallen)\s+(?:out|for|in\s+love|asleep)\b"
    r"|\b(?:knocked|blown)\s+(?:out|away)\b(?!\s+by\s+(?:a|the)\s+\w+\s*(?:car|bus))")


# The person is the one who was hit: "my brother attacked me", "my husband hit me". Asking how
# the brother is doing, when the brother is the one who did it, is the wrong person entirely -
# that belongs to whoever reads abuse, not here.
HURT_ON_THE_SPEAKER = re.compile(
    r"\b(?:attacked|hit|punched|stabbed|kicked|pushed|thrown|strangled|bitten|bit|beat|beaten|"
    r"burned|burnt|hurt|injured|raped)\s+me\b")


HURT_DEATH = re.compile(
    r"\b(?:died|dead|death|dying|passed\s+away|killed|kills?|funeral|buried|suicide|"
    r"took\s+(?:his|her|their)\s+own\s+life)\b")


def _somebody_hurt(clean, memory, understood):
    """The reply to a line that says somebody the person loves has been hurt, or None."""
    if understood.get("asks"):
        return None     # "what do i do if my son gets hurt" is a question about the future
    if _in_a_care_thread(memory):
        return None     # a death or a crisis is already on the table, and that is not this
    found = HURT_SOMEBODY.search(clean)
    if not found:
        return None
    if HURT_DEATH.search(clean):
        return None     # a death is the loss module's, and it says it far better
    if not HURT_EVENT.search(clean):
        return None
    if HURT_ON_THE_SPEAKER.search(clean):
        return None
    if HURT_BUT_FINE.search(clean):
        return None     # "my nan slipped in the bath but she's ok" is the whole of the news
    if HURT_FIGURE.search(clean):
        return None     # "my dad collapsed laughing" is not a fall
    # The words are the person's, so they face the person: "my son" comes back as "your son".
    who = re.sub(r"^(?:my|our)\b", "your", found.group(0))
    return _choose(tuple(line.format(who=who) for line in SOMEBODY_HURT), memory, clean)


# A day of the person's own that was low, rough or long. The floor answered it with the stock nod
# ("Got it. Is there anything you'd like a hand with?", "Thanks for telling me"), which is a line
# that could have come before any message at all: nobody says "i had a low day" to be filed, they
# say it to be met. The chat module has a pool for "i had a bad day" but its words for a feeling
# are read as a mood the person is in, and "a low day" names a thing - a day - so chat's own guard
# (a "low" that names a thing is a dial, not a mood) leaves the line to the floor. The reading here
# is the day, not the adjective: "<a low word> day/week/month" with the person as its owner.
LOW_DAY = re.compile(
    r"\b(?:low|rough|bad|rubbish|crap|hard|tough|awful|terrible|dreadful|long|heavy|rotten|flat)"
    r"\s+(?:old\s+)?(?:day|week|month|morning|afternoon|evening|night|shift)\b")


# The day is the speaker's: "i had a ...", "ive had a ...", "today was a ...", or the bare "low day
# today" a person types when there is nothing else to say about it.
LOW_DAY_MINE = re.compile(
    r"^(?:so |and |but |ok |okay |well |god |ugh |honestly |anyway |yeah |yeh |hmm )*"
    r"(?:i\s+(?:had|have|'ve|ve)\b|ive\b|i\s*'?m\s+having\b|i\s+am\s+having\b"
    r"|we\s+(?:had|have|'ve|ve)\b|weve\b"
    r"|(?:kind\s+of\s+|sort\s+of\s+|bit\s+of\s+|such\s+an?\s+)?a\b"
    r"|(?:today|yesterday|this\s+(?:morning|afternoon|evening|week))\s+(?:was|has\s+been|is)\b"
    r"|really\b|such\s+an?\b|what\s+an?\b"
    # the bare line a person types when the day is the whole of it: "low day today", "bad day at
    # work". It still has to name a day rather than an adjective on its own.
    r"|(?:low|rough|bad|rubbish|crap|hard|tough|awful|terrible|dreadful|long|heavy|rotten|flat)"
    r"\s+(?:old\s+)?(?:day|week|month|morning|afternoon|evening|night|shift)\b)")


# Somebody else's bad day is not the person's, and neither is a thing's: "my mum had a rough week"
# and "the shop had a bad day" are about that person and that shop.
LOW_DAY_NOT_MINE = re.compile(
    r"\b(?:he|she|they|it)\s+(?:had|has|was|is)\b"
    r"|\b(?:my|his|her|their|your)\s+(?!day\b|week\b|month\b|morning\b|night\b|evening\b)\w+"
    r"\s+(?:had|has|was|is)\b"
    r"|\bthe\s+\w+\s+had\b")


def _a_low_day(clean, understood):
    """True when the line says one of the person's own days went badly, and nothing else."""
    if (understood or {}).get("kind") == "question":
        return False
    if LOW_DAY_NOT_MINE.search(clean):
        return False
    # A day that went badly and then a thing that made it so ("i had a low day, my car broke") is
    # the named thing's turn: the pools for bad news already ask about it, and a general question
    # about the day is the weaker reply.
    if "," in clean or " because " in clean or " cos " in clean:
        return False
    return bool(LOW_DAY.search(clean)) and bool(LOW_DAY_MINE.match(clean))


# The people a person might say they love, and the shapes of the whole line. It is anchored at
# both ends because "i love my mums cooking" and "i love my best friend" already have their own
# answers, and "i dont love my mum" / "i love my mum but" are not this line. Two people get a
# plural pool of their own, because "what do you two do together?" is wrong for "mum and dad".
# One person, named or not: family, a partner, and the words people actually use for them.
# `kids`, `family` and `parents` are plural on their own and go to the plural pool; a list of
# names is always one word short, so the group words are here rather than left to be added later.
LOVE_ONE = (r"(?:mum|mom|mam|mother|dad|father|nan|nana|gran|granny|grandma|grandad|grandpa|"
            r"sister|brother|son|daughter|kid|child|wife|husband|partner|girlfriend|boyfriend|"
            r"fiance|fiancee|fiancé|fiancée|stepmum|stepmom|stepdad|stepson|stepdaughter|"
            r"mother[- ]in[- ]law|father[- ]in[- ]law|son[- ]in[- ]law|daughter[- ]in[- ]law)")


LOVE_GROUP = (r"(?:kids|children|family|families|parents|grandparents|grandkids|"
              r"grandchildren|siblings|brothers|sisters|boys|girls|aunts|aunties|uncles|"
              r"cousins|nieces|nephews|stepchildren|stepkids|in[- ]laws|friends|mates)")


LOVE_PERSON = r"(?:" + LOVE_ONE + r"|" + LOVE_GROUP + r")"


LOVE_OPENER = (r"^(?:oh |aw+ |ah |ha+ |lol |tbh |honestly |ok |okay |well |and |but |so )*"
               r"(?:i|we)(?: really| just| absolutely| so| still| do| totally| truly)?"
               r" love (?:my|our) ")


LOVE_TAIL = (r"(?: (?:so much|lots|loads|to bits|to pieces|more than anything|really|tbh|"
             r"honestly|though|tho|too|also))*[.!]*$")


LOVES_SOMEONE = re.compile(LOVE_OPENER + LOVE_ONE + LOVE_TAIL)


LOVES_A_GROUP = re.compile(LOVE_OPENER + LOVE_GROUP + LOVE_TAIL)


LOVES_PEOPLE = re.compile(
    LOVE_OPENER + LOVE_PERSON
    + r"(?: (?:and|&|n) (?:my |our |the )?" + LOVE_PERSON + r")+" + LOVE_TAIL)


# A clause after the person is how people type as they think: "i love my nan she is 88", "i love
# my mum and the kids". The line still starts with the love and names no other thing, so it is the
# same affection; a "but" or "though" is an objection with its own answer and stays out.
LOVE_START = re.compile(LOVE_OPENER + LOVE_PERSON + r"(?:[ ,'-]+[a-z0-9][^?.!]{0,60})?[.!]*$")


def _loves_people(clean):
    """How many of their own people the whole line says they love: 0, 1 or 2 (two or more)."""
    if "?" in (clean or ""):
        return 0
    text = (clean or "").strip()
    if " but " in " " + text + " " or " though " in " " + text + " ":
        return 0
    if LOVES_A_GROUP.match(text) or LOVES_PEOPLE.match(text):
        return 2
    if LOVES_SOMEONE.match(text):
        return 1
    # "i love my mum and dads cooking" is a thing of theirs, not a second person: a possessive
    # after the person is the thing they do or own, and it keeps its own reader.
    if LOVE_START.match(text) and not re.search(
            r"\b(?:mum|mom|dad|nan|gran|sister|brother|kid|child|parent|family)'?s\b"
            r"|\band (?:my|our|his|her|their)\b", text):
        return 1
    return 0


def _loves_someone(clean):
    """True when the whole line is the person saying they love someone of their own."""
    return bool(_loves_people(clean))


# A line that puts a clock time on being somewhere is a morning to plan, not a goal the person is
# failing at: "i need to be at work for 8" was answered "Be at work for 8 - fair enough. What's
# stopped it happening so far?", which is a coach's line about something somebody has been
# avoiding, and it drops the only part of the answer that helps - when to leave and how long the
# journey is (tiny-bluebell, #routing 81689). "Noted: you have a train at 7." and "I'm listening -
# say more if it helps." are the same fault from the other end: a deadline is the one thing in the
# line that can be worked back from, the way the airport entry already answers "what time should i
# leave for the airport" with "be there by 4am - work back from that".
A_CLOCK = (
    r"(?:\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm)|"
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(?:am|pm)|"
    r"(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*o'?clock|"
    r"half\s+(?:one|two|three|four|five|six|seven|eight|nine|ten))")


# The clock time itself, with the little word it hangs off. A bare number needs one ("for 8"), and
# "8am" does not.
A_TIME_SAID = re.compile(
    # The minutes come first, so a time given to the minute is quoted as it was said: "7.45"
    # matched the bare \d{1,2} arm of A_CLOCK on its own and the reply worked back from "7",
    # which is not what the person has to be there by (grand-gopher on #7924).
    r"\b(?:at|by|for|before|around|about|until|till|from)\s+"
    r"(\d{1,2}[:.]\d{2}\s*(?:am|pm)?|" + A_CLOCK + r"|\d{1,2}|"
    r"one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b",
    re.I)


# A time in front of the thing that leaves - "i have to catch the 7.15 train", "the 6am flight
# goes from terminal two" - has no little word in front of it, so A_TIME_SAID misses it. It is
# the same morning as the other shapes and worth the same answer.
CLOCK_THE_DEPARTURE = re.compile(
    r"\bthe\s+(\d{1,2}[:.]\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm)|half\s+past\s+"
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve))\s+"
    r"(?:train|flight|bus|coach|ferry|boat|tram|tube|plane)\b", re.I)


# The shapes that make a clock time a deadline: somebody has to be somewhere, a train leaves, a
# shift starts, an alarm goes off. A clock time on its own is not enough - "i have 8 eggs" and
# "i watched it for 8 hours" are about a number, not a morning.
CLOCK_SHAPE = re.compile(
    r"\b(?:need|needs|needed|have|has|had|got|must|ought)\s+(?:to\s+)?"
    r"(?:be|get|leave|head|go|catch|make)\b"
    # A journey or a shift that has a time on it. An interview, an exam and a match are left out
    # on purpose: those are occasions the bot already answers as occasions ("Good luck with it"),
    # and "my interview is at 3pm" is a fact to keep rather than a morning to plan.
    r"|\b(?:train|flight|bus|coach|ferry|boat|taxi|shift|meeting|work|check-?in)\s+"
    r"(?:is|are|starts?|leaves?|departs?|takes?\s+off|begins?|kicks?\s+off)?\b"
    r"|\b(?:be|get|wake)\s+up\b|\bset\s+(?:the|my|an)\s+alarm\b")


# A length hanging off the same little word is not a clock: "for 8 hours", "for 6 months",
# "for 8 people" are quantities, and "i was at work for 8 hours" is the day that has happened.
A_LENGTH = re.compile(
    r"^\s*(?:hours?|hrs?|minutes?|mins?|days?|weeks?|months?|years?|miles?|km|kms|"
    r"people|quid|pounds|kilos?|kg|st[o]?ne|times|of\s+them|more|less)\b")


# Over, or somebody else's, or a question: the four shapes that are not a morning of theirs.
CLOCK_NOT_THIS = re.compile(
    r"\b(?:was|were|been|missed|lost|yesterday|last\s+night|this\s+morning|cancelled|"
    r"canceled|used\s+to|usually|always|every\s+day)\b")


CLOCK_ASKED = re.compile(
    r"^\s*(?:what|when|how|which|why|who|should|shall|can|could|would|do|does|did|is|are|"
    r"was|were|have|has|any|is\s+it)\b")


# Somebody else's morning is answered where that person is answered: "my mum has to be at the
# hospital for 9" is the worry about her, not a journey to plan.
# A line that describes the job is about the job, not about this morning: "im a bus driver and i
# start at five in the morning" is context for the early shifts, and the sleep answer is the one
# that helps, so the clock time in it is not a deadline to work back from.
CLOCK_ABOUT_THE_JOB = re.compile(
    r"\b(?:im|i'm|i am)\s+an?\b|\bi\s+work\s+as\b|\bmy\s+job\b|\bmy\s+shift\s+pattern\b")


CLOCK_SOMEONE_ELSE = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:mum|mom|mam|mother|dad|father|wife|husband|partner|"
    r"boyfriend|girlfriend|son|daughter|child|kid|brother|sister|nan|nana|gran|granny|"
    r"grandma|grandad|grandpa|aunt|uncle|cousin|niece|nephew|friend|mate|neighbour|neighbor|"
    r"colleague|boss)\b")


# The reply works back from the time: what the journey is, what has to happen before they go, and
# the leaving time rather than the arriving one.
AT_THE_CLOCK = (
    "Work it back from {at}: the journey, then getting ready, then ten minutes spare. What is "
    "the trip like at that hour?",
    "{At} gives you a time to work back from. How long does the journey take from yours?",
    "Count backwards from {at} and set the alarm by the time you have to walk out. What has to "
    "happen before you get out of the door?",
    "The leaving time is the thing to fix for {at}, not the arriving one. How long does it take "
    "from yours?",
    "{At} is a timetable rather than a rush, as long as the leaving time is right. Where are you "
    "travelling from?",
)


def _the_clock_pool(at):
    """The pool with the time worked into the lines, so the reply names it back."""
    at = (at or "").strip()
    if not at:
        return AT_THE_CLOCK
    return tuple(line.format(at=at, At=at[:1].upper() + at[1:]) for line in AT_THE_CLOCK)


def _the_time_said(clean):
    """The clock time in the line, as the person said it, with its match.

    A time said with the little word in front of it ("by 7.45", "for 6am") and a time said in
    front of the thing that leaves ("catch the 7.15 train") are the same morning, and both have
    to be quoted back the way they were given, minutes and all.
    """
    return A_TIME_SAID.search(clean) or CLOCK_THE_DEPARTURE.search(clean)


def _the_morning_has_a_clock(clean):
    """True when the line puts a clock time on somebody having to be somewhere."""
    if "?" in clean or CLOCK_ASKED.match(clean):
        return False
    if CLOCK_NOT_THIS.search(clean) or CLOCK_SOMEONE_ELSE.search(clean):
        return False
    if CLOCK_ABOUT_THE_JOB.search(clean):
        return False
    said = _the_time_said(clean)
    if not said:
        return False
    if A_LENGTH.match(clean[said.end():]):
        return False
    return bool(CLOCK_SHAPE.search(clean) or said.re is CLOCK_THE_DEPARTURE)


# The alternatives can already be on the table when the person hands the choice back: a dinner
# the bot listed two lines up, or a choice the person named themselves ("i could go to the gym or
# go for a swim" / "you pick"). Where memory's `prefer` can pick it never gets this far, so asking
# "what are they?" here is asking for what was just said - a friend picks, or says what it turns
# on. The pool stands down and the ordinary answer for the line takes the turn, which is what the
# person got before this pool existed. Found by brown-pomelo, merry-wheel and violet-pine on the
# review of #7538, each on their own comparison.
OPTION_ON_THE_TABLE = re.compile(r"\b(?:or|either)\b")


def _options_already_up(memory):
    """True when the things to choose between were named in the last turn or two."""
    if not isinstance(memory, dict):
        return False
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-2:]
    for turn in turns:
        said = str(turn.get("bot") or "")
        asked = str(turn.get("user") or "")
        if len(OPTION_ON_THE_TABLE.findall(said.lower())) or " or " in asked.lower():
            return True
    return False


def _reads_value(pred, clean, repaired, memory=None):
    """The pool a cue picks out of the typed line, or out of the same line with its words put
    right, or None.

    `_reads` is the same idea for a cue that only says yes or no. The pools that pick a reply out
    of a line need the pool itself back, and they were handed the typed line alone: "im ment to be
    goin to a weddin nxt week" was answered "I'm listening - say more if it helps" while the same
    line spelled properly got "Something to look forward to, then", because "next week" is a
    spelling the reading puts right and the pool never saw the mended line. As in `_reads`, the
    typed line is asked first, so a line that needs no repair is untouched.
    """
    found = pred(clean) if memory is None else pred(clean, memory)
    if found or not repaired or repaired == clean:
        return found
    return pred(repaired) if memory is None else pred(repaired, memory)


# A countdown is the one sum that still belongs in a care thread. "i dont want to live in
# december" then "how long till december" is somebody asking how long they have to hold on, and
# the arithmetic card stands down there on purpose (maths.solve asks in_a_safety_thread first,
# because a figure said out loud mid-emergency is the person still in it and not a sum to work
# out). What was left was the search hedge - "searching for it will turn up better sources than I
# can offer" - which is the worst thing this bot can say to that question. The date is worked out
# with the crisis taken out of the way, and the line keeps the person company while it says it.
COUNTDOWN_ASK = re.compile(
    r"(?<![a-z])(?:how long|how many (?:days|weeks|months|sleeps|more days)|how much longer|"
    r"how far away)(?![a-z])")


COUNTDOWN_TO = re.compile(r"(?<![a-z])(?:till|til|until|before|away|to go)(?![a-z])")


COUNTDOWN_AFTER_CARE = (
    "{count} That is a while to be counting towards, and you don't have to get through it on "
    "your own - what is tonight like?",
    "{count} If there is something about that date you are counting towards, say what it is and "
    "we'll take it a day at a time.",
    "{count} A long stretch of days is hard to carry on your own. Who knows how you are doing "
    "tonight?",
)


# The shape a count starts with. A sentence from `solve` that refuses the sum ("I can't see a
# calendar from here, so tell me the date") has numbers later in it, so where the figure sits
# decides it rather than whether there is one at all.
COUNTED = re.compile(
    r"^(?:that's |that is |it's |its )?(?:about |around |just |nearly |only |almost |another )?"
    r"(?:\d|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
    r"fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|a hundred)")
