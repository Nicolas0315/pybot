"""Part 10 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews, fallback
from ..compose.badnews import reads_like_a_symptom
from ..knowledge.lookup import the_body_is_short_of_sleep
from ..understanding import topics
from ..understanding.kinds import cue_about_person
from ..compose import loss as loss_reading
from ..compose import harm as harm_reading
from ..compose import saidby as saidby_reading
from ..compose import said_about_me
from ..memory import WHO_SAID, user

from ..memory import ack, user
from ..memory.facts import JUDGEMENT_AFTER, JUDGEMENT_NOUNS

from ..knowledge import lookup
from ..understanding import understand as understanding
from .chat_part_01 import (
    SELF_COPULA, _when_not_why, ASKS_A_QUESTION, EVERYTHING_WRONG, NOT_FAIR, NOT_GREAT, OWN_HARSH,
    OWN_TRAIT, OWN_WORTH, SOCIAL_TRAIT_SETTING, _about_themselves, _asks_after, _judged_a_role,
    _letting_someone_down, _themselves_unfair, _turns_on_news,
)
from .chat_part_03 import (
    INTENSIFIERS, INTENSIFIER_PAIRS, OWN_STATES, STATE_NOUNS, FEELINGS,
)
from .chat_part_04 import (
    CANT, CANT_OPENING, ITS_BEEN, STUCK, STUCK_FIXABLE, STUCK_IDIOM, STUCK_LOSS, STUCK_OBJECT,
    STUCK_REASON, STUCK_SAFETY, STUCK_SELF, _doing_something_to_a_thing, said_loss, ROUGH_DAY,
)
from .chat_part_05 import (
    DOUBT, EVENT_OUTING, EVENT_RE, EVENT_STATE, EVENT_TIRED, FEELING_THING, FEELING_WANT,
    INTENT_CONDITION, INTENT_RE, INTENT_STOP, LEAVE_SOMEONE, NEED_FOR, NEED_RE, NEXT_ACT, NEXT_REST,
    NEXT_UP, PLAN_WORRY, QUESTION_STARTERS, WANTED, _a_trip, _answers_it, _NOTHING_MUCH_BETWEEN,
    _NOTHING_MUCH_FILLER, _tokens, NOT_MY_NIGHT, MY_NIGHT,
)
from .chat_part_06 import (
    _NOTHING_MUCH_AFTER, _NOTHING_MUCH_DO, _NOTHING_MUCH_TAIL, _nothing_much_span, BODY_FREQUENCY,
    BODY_FREQUENCY_KEPT, FREQUENCY_ONLY, NIGHT_FREQUENCY, NIGHT_FREQUENCY_KEPT, SYMPTOM, WORRY,
    END_OF_ROPE, LOSS, OTHER_AWAKE, _answers_has_the_frequency, EARLY_NIGHTS, OTHER_SLEPT,
    SORE_NIGHTS, SPEAKER_LOST,
)
from .chat_part_07 import (
    _carries_on, _owner, WEARS_OTHER_PEOPLE_OUT, _OTHER_SUBJECT, HARD_ON_THE_PERSON,
    LIFE_THING_HARD, _owned_by_a_thing, GUILT_ABOUT, HOW_I_GET_THROUGH, NOT_COPING,
    NOT_COPING_ANYWHERE, NOT_COPING_SHAPES, STRUGGLING_ABOUT_A_THING, FEAR_BEFORE,
    FIRST_PERSON_BEFORE, GOING_MAD, IDIOM_PLACE,
)
from .chat_part_08 import (
    _feel_like, FIRST_PERSON,
)
from .chat_part_09 import (
    _loss_recent, LOW_MOOD, MOOD_NIGHTS, _low_mood_recent,
)


def _judged_as_a_noun(tokens):
    """Whether the line says the person is a judgement noun, and nothing more."""
    for at, word in enumerate(tokens):
        if word not in JUDGEMENT_NOUNS:
            continue
        before = tokens[max(0, at - 4):at]
        if not any(item in SELF_COPULA for item in before):
            # "my life is a joke", "everything is a joke": the judgement said about their life
            # rather than about them, and the same thing to answer.
            if not (any(item in ("life", "everything", "it") for item in before)
                    and "is" in before):
                continue
        if not any(item in ("a", "an", "the") for item in before):
            continue
        if any(item in ("not", "never", "no") for item in before):
            continue
        after = tokens[at + 1:at + 2]
        if after and after[0] not in JUDGEMENT_AFTER:
            continue
        if _when_not_why(tokens[at + 1:]):
            continue
        return True


def _judgement(clean, tokens):
    """The pool for a line that judges the person or their luck, or None.

    A question is never one of these ("is it not fair to ask for a refund" is a question about
    something), and a long line has a subject of its own that another reader should take.
    """
    if "?" in clean or len(tokens) > 14 or (tokens and tokens[0] in ASKS_A_QUESTION):
        return None
    # A label somebody else put on the person is not the person judging themselves: "my teacher
    # says im lazy" and "my brother says im a waste of space" were answered "I doubt that's the
    # whole picture - you're being harder on yourself than you'd be on a friend", which argues with
    # the wrong person about a judgement they did not make. Being spoken to that way has its own
    # reader (bot/compose/said_about_me.py), so these pools stay out of it.
    if said_about_me.reads_as_somebody_elses_words(clean.replace("'", "")):
        return None
    # A comparison the person built themselves ("i feel like im doing everything wrong") is read
    # by `_feel_like`, which names what they compared themselves to; this pool's lines fit any
    # worth line and would answer before that reading was ever asked.
    if _feel_like(clean) not in (None, "feel_like"):
        return None
    # A judgement with a role or a noun in it comes first: "i feel like a bad dad" is the same
    # turn as "i feel like a failure", and the pool of its own is what stops the store reading it
    # back. The plain wrong words stay with the pool below, which already answered them.
    if OWN_HARSH.search(clean) and _about_themselves(tokens):
        return "own_harsh" if _judged_a_role(clean) else "own_described"
    judged = (OWN_WORTH.search(clean) or (OWN_TRAIT.search(clean)
                                          and not SOCIAL_TRAIT_SETTING.search(clean))
              or EVERYTHING_WRONG.search(clean)
              or topics.reads_as_unfit(clean) or _letting_someone_down(clean))
    # "im a fat guy what exercise should i do": the ask after the judgement is the part they can
    # act on, and comforting the whole person buries it. Asked first, because a judgement with a
    # noun in it ("im a fat guy") is exactly the shape `_judged_as_a_noun` claims.
    if not (judged and _asks_after(clean, judged)):
        if _judged_as_a_noun(tokens):
            return "not_enough"
        # "i feel stupid but i passed" is somebody's news with a shrug in it: the result is
        # what they came to say, and the warm "harder on yourself" line buries it.
        if judged and _about_themselves(tokens) and not _turns_on_news(clean):
            return "not_enough"
    if NOT_FAIR.search(clean):
        # "i wasnt fair to her" is the person owning something, not their luck being bad.
        if _themselves_unfair(tokens):
            return "own_fault"
        return "not_fair"
    if len(tokens) <= 8 and NOT_GREAT.search(clean):
        return "not_great"
    return None


def _intent(clean, tokens, memory):
    """A plan or an upcoming event, aired without a question."""
    from ..knowledge.lookup import find
    from ..compose import fallback as compose_fallback
    if not tokens or len(tokens) > 22 or "?" in clean or len(tokens) < 3:
        return None
    # A clock time somebody has to be somewhere by is a morning to plan, not an intention aired:
    # "i need to be at work for 8" was asked "Worth doing. What would you like help with first?",
    # and the composer has the pool that works back from the time (tiny-bluebell, #routing 81689).
    if compose_fallback._the_morning_has_a_clock(" ".join(tokens)):
        return None
    flat = " ".join(tokens)
    if _a_trip(flat, memory):
        return None
    # A change of dose is not an intention aired. "im going to take a double dose tonight" was
    # answered "Worth doing. What would you like help with first?" - an intention in the shape of
    # a plan, which is the one thing a prescription does not need. The plan reading below and the
    # chain both answer it with the pharmacist, so this one stands aside rather than encourage it.
    if compose_fallback.reads_as_a_change_of_medicine(flat):
        return None
    if ack.a_limit_on_the_plan(flat):
        return None  # "we need to keep it cheap" is a limit on the plan, not a plan
    words = set(tokens)
    if words & INTENT_STOP or PLAN_WORRY.search(flat):
        return None
    # A plan with a person on the other end of it is anger, not a plan: the harm reading answers
    # it earlier in the turn, and this reading must not hand it back as "Worth doing".
    if harm_reading.reads_as_hurting_someone(flat):
        return None
    # A wish inside quotation marks is somebody else's wish, not a plan of the person's: "he
    # texted \"i want to see you tonight\" and i panicked" was answered "Worth doing. What would
    # you like help with first?", which hands back the other person's plan as theirs to start.
    # The composer asks about the person holding it instead.
    quoted = saidby_reading.reply_for(flat, memory)
    if quoted:
        return quoted
    # "i want to keep going though" is answering our line about the knees, not airing a plan.
    if tokens[-1] in ("though", "tho"):
        return None
    wanted = WANTED.search(flat)
    if wanted:
        thing = wanted.group(1).strip(" .,!;:")
        first = (thing.split() or [""])[0]
        if first in FEELING_THING or FEELING_WANT.search(thing) or LEAVE_SOMEONE.search(thing):
            return None
    head = [t for t in tokens if t not in ("ok", "okay", "so", "and", "but", "also", "well")]
    if head and head[0] in QUESTION_STARTERS:
        return None  # "do i need a cable for that" is a question about the plan
    if DOUBT.search(flat):
        return None  # "i dont know if i want to stay with him" is a doubt, not a plan
    if INTENT_CONDITION.search(flat):
        return None  # a plan with a condition on it is a how-question
    # A plan line the knowledge base can answer belongs to it: "i want to hand in my notice
    # without burning bridges" is a resigning-letter question, and it sits at PRIORITY 0 there,
    # so this reading has to stand aside (@airy-radio, on the deck). What counts is whether the
    # entry answers, not whether one was found: `find` hands back `city-next` for "i want to
    # eat less sugar" (on "eat" and "i") and that entry then turns the line down because no
    # city was named, and standing aside for it left the line with a bare ack.
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict) and _answers_it(clean, understood, memory):
        return None
    # A week with no money is not a plan coming up: "i have 20 quid till friday" was read as an
    # event and asked "How ready do you feel for it?". The understanding engine has already
    # decided the line says the money has run out, and the tight-week reply is the one that
    # answers it, so this reading stands aside the same way it does for a plan the knowledge
    # base can answer.
    if isinstance(understood, dict) and understood.get("tight_on_money"):
        return None
    # A line about the kitchen is not an event coming up. "i havent got any chicken this week"
    # names a food the kitchen has not got and a week, and once the pantry stopped reading that
    # chicken as something in the house - it is what the line says is not there - this reading
    # was what answered it: "How ready do you feel for it?" What the person has told us is what
    # is in the kitchen, and the cooking answers are the ones that own it.
    from ..knowledge import cooking as cooking_kb
    if isinstance(understood, dict) and cooking_kb.negated_ingredients(understood):
        return None
    # A job on their list is not an appointment to get ready for. "i have a report to write for
    # friday" and "i've got the shed to clear out this weekend" were both asked "How ready do
    # you feel for it?" - a question about nothing, because a thing to do is not an event coming
    # up. The memory lane reads the line as the job it is, and that reading owns it.
    if ack.a_job_to_do(clean, memory):
        return None
    if EVENT_RE.search(flat):
        if (EVENT_OUTING.search(flat) or EVENT_TIRED.search(flat)
                or EVENT_STATE.search(flat)):
            return None
        return "event"
    if NEED_FOR.search(flat):
        return None  # a thing wanted for something is a request, not a plan
    if INTENT_RE.search(flat) or NEED_RE.search(flat):
        if NEXT_UP.search(flat) and not _my_night(flat):
            if NEXT_REST.search(flat) and not NEXT_ACT.search(flat):
                return "next_rest"
            if NEXT_ACT.search(flat):
                return "next_act"
            return "next_up"
        return "intent"
    return None


def _says_nothing_much(tokens, clean=""):
    """True when the line says "not much" or "nothing much" and nothing else of its own.

    The words around the phrase are the ones a spoken answer carries ("im", "yeah", "tbh"), and
    the tail after a comma or a "just" is the rest of that answer ("not much, just working").
    Anything else is a subject: a verb between "not" and "much", or a word after the phrase that
    is not one of the doings above.
    """
    said = set(tokens)
    if not (said & {"much", "notmuch", "nm", "nmu"}):
        return False
    # "how much" is a question about a quantity, not a shrug about the day: "so how much now",
    # asked after a portion was given, is the person asking for the number again, and the
    # effort answer ("Not much here either. What are you up to?") answered nothing. The words
    # around the phrase are the same either way, so the ask is what tells them apart.
    if re.search(r"\bhow\s+(?:much|many)\b", clean or ""):
        return False
    # A lone "much" is only the phrase when something makes it one: a "not" or a "nothing" in
    # the line, or a form of "do" for the person to have not been doing much of. "thanks so
    # much" and "thanks very much" are a thank-you with an adverb, and they were answered "Not
    # much here either. What are you up to?" - the same shrug the phrase earns - by the shortcut
    # below, because every word in them is a filler word.
    if "much" in said and not (said & {"not", "nothing", "notmuch", "nm", "nmu"}
                               or said & _NOTHING_MUCH_DO):
        return False
    if said <= _NOTHING_MUCH_FILLER:
        return True
    # The phrase is in the first clause: "not much, just working" says the phrase and then
    # finishes the sentence, and the comma is what tells the two halves apart.
    clause = re.split(r"[,;:]|\s-\s", clean or "", 1)[0]
    words = _tokens(clause)
    span = _nothing_much_span(words)
    if span is None:
        return False
    start, stop = span
    before, after = words[:start], words[stop:]
    # A "just" after the phrase starts the tail: what comes after it is the person finishing
    # their own sentence, so it is not read as a subject ("not much just chilling with the kids").
    for at, word in enumerate(after):
        if word in _NOTHING_MUCH_TAIL:
            after = after[:at]
            break
    if not set(after) <= (_NOTHING_MUCH_FILLER | _NOTHING_MUCH_AFTER | _NOTHING_MUCH_BETWEEN):
        return False
    if not set(before) <= (_NOTHING_MUCH_FILLER | _NOTHING_MUCH_DO):
        return False
    return True


def _frequency_of_the_last_trouble(clean, memory=None):
    """The pool for a frequency said after a trouble, or None.

    Only a line that is the frequency itself counts, and only when the turn before named a
    trouble of the person's own: their sleep, or a symptom. A death or a worry in the last few
    turns owns the frequency too ("my mum died" / "its every night" is grief, not sleep hygiene),
    and someone else's night ("my son keeps waking up") is theirs, not the person's.
    """
    frequency = FREQUENCY_ONLY.match(clean)
    if not frequency:
        return None
    often = frequency.group(1).strip()
    often = often[:1].upper() + often[1:]
    if not isinstance(memory, dict):
        return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return None
    last = turns[-1] if isinstance(turns[-1], dict) else {}
    said = " ".join(str(last.get("user") or "").lower().split())
    if not said or _loss_recent(memory) or WORRY.search(said):
        return None
    # "every day" after a broken night is not the night's frequency: the line has to name the
    # night, the morning or a thing that happens constantly for the sleep pool to answer it.
    night_phrase = bool(re.search(
        r"\b(?:night|nights|morning|mornings|nightly|all\s+(?:the\s+)?time|constantly)\b",
        often, re.I))
    night = night_phrase and _my_night(said) and not NOT_MY_NIGHT.search(said)
    body = not night and not NOT_MY_NIGHT.search(said) and (
        SYMPTOM.search(said) or reads_like_a_symptom(said))
    if not (night or body):
        return None
    # The reply already asked the length, or named the weeks it takes: say the step for now
    # instead of asking the same thing twice.
    earlier = str(last.get("bot") or "")
    kept = bool(re.search(r"\b(?:how long|how often|weeks?|months?)\b", earlier, re.I))
    pool = NIGHT_FREQUENCY_KEPT if night and kept else (
        NIGHT_FREQUENCY if night else BODY_FREQUENCY_KEPT if kept else BODY_FREQUENCY)
    return tuple(line.format(often=often) for line in pool)


def _frequency_is_the_turn(clean, memory=None):
    """True when this line is a frequency after the person's own trouble, and this module has it.

    The frequency is a line read whole: the trouble was named a turn earlier, so an entry that
    answered it can match the line's topic and hand the whole paragraph over again ("i have a
    cough" / "its every night"). The arbiter asks this module, so the next turn is this one.

    An entry that answers the frequency about the person themselves keeps its turn: the morning
    headache and the throat that is sore first thing are answers this line cannot improve on.
    """
    if END_OF_ROPE.search(clean) or OTHER_AWAKE.search(clean) or LOSS.search(clean):
        return False
    try:
        if _answers_has_the_frequency(clean, memory):
            return False
        return bool(_frequency_of_the_last_trouble(clean, memory))
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False


def after(text, reply, memory=None):
    """Note when the reply just given was the answer to a frequency line.

    The frequency reply is about the turn before it ("Every night, then ..."), not an answer of
    its own, so a bare ask on the next turn ("what do i do now") has to read past it to the
    trouble answer behind it. The composer cannot tell that from the module name alone, so this
    marks the one turn; it is replaced on every following turn.
    """
    if not isinstance(memory, dict):
        return
    try:
        clean = " ".join(str(text or "").lower().replace("\u2019", "'").split())
        pool = _frequency_of_the_last_trouble(clean, memory)
        memory["frequency_reply"] = bool(pool and str(reply or "") in pool)
        # The answer the frequency line stepped in front of, so the turn after it can be read
        # against the trouble answer rather than against "Every night, then". The cough walk
        # ends "i have a cough" / "its every night" / "can i take anything for it", and the
        # last line used to reach the search hedge though the honey answer was two turns up.
        turns = memory.get("turns")
        behind = turns[-1] if isinstance(turns, list) and turns else None
        behind = behind if isinstance(behind, dict) else {}
        memory["frequency_answer"] = (str(behind.get("bot") or "")
                                      if memory["frequency_reply"]
                                      and behind.get("module") == "answers" else "")
    except Exception:  # noqa: BLE001 - a note that fails must not cost the turn
        memory["frequency_reply"] = False
        memory["frequency_answer"] = ""


def _early_start(clean, memory=None):
    """The reply for a night the person did not get, or None when the line says something else."""
    # Someone else's night stands down only when the line does not also say the speaker lost
    # their own: "my son had a bad night so i barely slept" is two nights, and the one to console
    # is the person typing.
    ours = bool(SPEAKER_LOST.search(clean))
    if END_OF_ROPE.search(clean) or OTHER_AWAKE.search(clean):
        return None
    if OTHER_SLEPT.search(clean) and not ours:
        return None
    if LOSS.search(clean) or _loss_recent(memory) or WORRY.search(clean):
        return None
    frequency = _frequency_of_the_last_trouble(clean, memory)
    if frequency:
        return frequency
    for pattern, replies in EARLY_NIGHTS:
        if pattern.search(clean):
            if SYMPTOM.search(clean):
                return SORE_NIGHTS
            if LOW_MOOD.search(clean) or _low_mood_recent(memory):
                return MOOD_NIGHTS
            return replies
    return None


def _said_of_the_person(clean, match):
    """Whether a feeling word with no "i" in front is still said of the person.

    It has to be leaned on by an intensifier - "so tired", "really down", "a bit low" - and
    nothing the line names may take it over: "my battery is so low" is about the battery and
    "low heat" is describing the heat, so both pass the turn on instead of getting sympathy.
    """
    before = clean[:match.start()].split()
    after = clean[match.end():].split()
    owner = _owner(before)
    # "my anxiety is bad today", "my mood is low": the line already says whose state it is, with
    # a state of a person before a copula or their own "my"/"our" right in front of the word, so
    # it needs no intensifier. What follows still has to leave the word about the person.
    stated = owner in STATE_NOUNS or (bool(before) and before[-1].strip(".,!?;:").lower()
                                      in ("my", "our"))
    if after and after[0].strip(".,!?;:").lower() in STATE_NOUNS:
        return True  # "my low mood", "my low energy": the word names a state of theirs
    if stated:
        return not after or _carries_on(after[0])
    intensified = bool(before) and (before[-1] in INTENSIFIERS
                                    or " ".join(before[-2:]) in INTENSIFIER_PAIRS)
    if not intensified:
        return False
    if after and not _carries_on(after[0]):
        return False  # "low heat", "down duvet": the word is describing the thing after it
    return owner is None or owner in OWN_STATES


def _a_person_who_wears_you_out(clean, word, match):
    """True when a word of strain has another person as its subject, not the person typing."""
    if word not in WEARS_OTHER_PEOPLE_OUT:
        return False
    before = clean[:match.start()]
    if OTHER_PERSON.search(before):
        return True
    return bool(_OTHER_SUBJECT.search(before)) and not re.search(r"\b(?:i|im|i'm|we)\b", before)


def _says_how_the_person_is(clean, word, match):
    """Whether this feeling word is said about the person, not about something of theirs.

    Two things can make it theirs: the reading's own cue in front of the word is the person ("im
    shattered", "so tired", "a bit down"), or the line says the state is theirs with their own
    word for it ("my mood is low", "ive been low all week"). A thing the line names before the
    word takes it instead - "my phone battery is low again", "ok so low heat then" - unless what
    follows the word leaves it about the person after all.
    """
    if _a_person_who_wears_you_out(clean, word, match):
        # "she is so draining" is what she does to the person typing, never how she feels, and
        # the advice to give her a rest has the burden the wrong way round. The knowledge base
        # has the card for a person who drains you.
        return False
    if _owned_by_a_thing(clean, match):
        return _said_of_the_person(clean, match)
    if word in HARD_ON_THE_PERSON and LIFE_THING_HARD.search(clean[:match.start()]):
        return True  # "my job is exhausting" is them worn out by the job
    return cue_about_person(clean, word) or _said_of_the_person(clean, match)


def _not_coping(clean):
    """True when the line says, in plain words, that the person is not doing well."""
    text = " ".join(str(clean or "").split())
    if GUILT_ABOUT.search(text):
        return False
    if not (NOT_COPING.search(text) or NOT_COPING_SHAPES.search(text)
            or NOT_COPING_ANYWHERE.search(text) or _speaker_going_mad(text)
            or HOW_I_GET_THROUGH.search(text)):
        return False
    return not STRUGGLING_ABOUT_A_THING.search(text)


def _speaker_going_mad(text):
    """True when the line says the speaker themselves is going mad, in the idiom's own words."""
    for at in GOING_MAD.finditer(text):
        before = text[:at.start()]
        after = re.search(r"\b(?:at|about)\s+(.*)$", text[at.end():])
        if after and not IDIOM_PLACE.match(after.group(1)):
            # "im going mad at the state of this kitchen" is a row with the kitchen: the idiom
            # is anger there, and the not-coping pool answers a different thing.
            continue
        if after and not FEAR_BEFORE.search(before):
            # "im going crazy at work" is a full diary, not a disclosure, and the busy-day line
            # answers it. "i feel like im going crazy at work" is the disclosure, and the frame
            # in front of the idiom is what says so.
            continue
        if FIRST_PERSON_BEFORE.search(before):
            return True
    return False


def _grieving(memory, clean):
    """True when this chat is still about a death, however the bot's sympathy was phrased.

    "we lost the baby in february" then "my partner wont talk about it" is a person in grief
    talking about their partner, not a report that needs a question about the partner's health.
    The bot's own sympathy line is no guide - the fallback says it as readily as the loss module.
    """
    if loss_reading.continues(memory) or badnews.reads_as_sudden_loss(clean):
        return True
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    mine = " ".join(str(clean).lower().split())
    for turn in reversed(turns):
        user = " ".join(str(turn.get("user") or "").lower().split())
        if not user or user == mine:
            continue
        said = str(turn.get("bot") or "")
        if loss_reading.reads_as_loss(user) or badnews.reads_as_sudden_loss(user):
            return True
        # The bot's own sympathy line is the other sign, and the fallback says the same thing
        # as the loss module does, so both pools count.
        return any(said in pool for pool in loss_reading.POOLS + (fallback.SUDDEN_LOSS,))
    return False


def _better_answer_exists(clean, memory):
    """True when the line has a real answer of its own, so a careful question would be worse.

    "My daughter refuses to go into school some mornings" is answered by naming the one who can
    act on it - the school office or a head of year - and "how long has that been going on with
    your daughter?" answers nothing next to it. Same for a line the knowledge base knows: the
    question is for a line nothing else can take.
    """
    try:
        if lookup.find(understanding(clean, memory)) is not None:
            return True
        return fallback.who_settles(clean, memory) is not None
    except Exception:
        return False


def _still_about_me(clean):
    """True when the line, once the person's own name is taken out, is still about the user.

    "my mum keeps asking when im having kids and it winds me up" is the person's own annoyance
    with their mother, not a report that something is wrong with her; "my daughter wont tell me
    whats wrong" is about the two of them, not her health. The careful question ("how long has
    that been going on with your mum?") is for a line that is only about them.
    """
    return bool(FIRST_PERSON.search(WHO_SAID.sub(" ", clean)))


def _about_the_person(understood):
    """True unless the reading says the line's word of mood belongs to a thing.

    "low heat", "my phone battery is low" and "turn the heat down" name a state of an object,
    so a kind word about how someone feels would answer a question nobody asked.
    """
    return not (isinstance(understood, dict) and understood.get("state_owner") == "thing")


def _my_night(clean):
    """True when the line reports the person's own broken night, so they are short of sleep."""
    text = re.sub(r"\s+", " ", str(clean or "").lower())
    if not MY_NIGHT.search(text):
        return False
    return not NOT_MY_NIGHT.search(text)


def _stuck(clean, memory=None):
    """The kind of daily-life thing the person says they cannot do, or None.

    "i can't get out of bed in the mornings" -> "mornings"; "i can't sleep" -> "sleep";
    "i can't face going to work today" -> "work". None when the line is not a first-person
    inability, is an idiom ("can't wait"), names a thing to fix or a reason ("can't eat
    gluten", "can't work out my tax"), belongs to safety, or names a death - now or earlier
    in the conversation, which owns the turn.
    """
    if not (CANT.search(clean) or CANT_OPENING.match(clean) or ITS_BEEN.search(clean)
            or the_body_is_short_of_sleep(clean)) \
            or STUCK_SAFETY.search(clean):
        return None
    if STUCK_IDIOM.search(clean) or STUCK_REASON.search(clean) or STUCK_SELF.search(clean) \
            or _doing_something_to_a_thing(clean):
        return None
    if STUCK_FIXABLE.search(clean):
        return None
    if STUCK_LOSS.search(clean) or said_loss(memory):
        return None
    # A sleepy line names no inability, so it is answered as the tired body it is rather than
    # falling through to a row that shares a word with it.
    if the_body_is_short_of_sleep(clean) and not (CANT.search(clean) or CANT_OPENING.match(clean)
                                                 or ITS_BEEN.search(clean)):
        return "sleep"
    for name, patterns in STUCK:
        if name == "work" and STUCK_OBJECT.search(clean):
            continue
        for pattern in patterns:
            if re.search(pattern, clean):
                return name
    return None


# A feeling is not always the user's: "my wife is really tired" wants a reply about her, not
# advice to put the user's own feet up. The person named is read from the line, and the reply
# talks about them.
OTHER_PERSON = re.compile(
    r"\b(?:my|our|the)\s+(wife|mum|mom|mother|dad|father|son|daughter|husband|partner|"
    r"boyfriend|girlfriend|brother|sister|friend|mate|flatmate|boss|colleague|nan|granny|gran|"
    r"grandma|grandad|grandpa|aunt|uncle|kid|kids|child|children|baby|parents|family|"
    r"neighbours?|neighbors?)\b")


OTHER_PRONOUN = re.compile(r"^(?:he|she|they)(?:'s|s|'re|re)?\b")


# A feeling said as the verb itself, straight after the person: "he cries all the time", "she
# just sobs". The verb check below looks for an "is" or a "keeps" between the person and the
# word, and there is none when the word is the verb - so "he just cries all the time", said of a
# four-year-old, was read as the user's own tears and answered "That long is worth a proper look
# ... book the GP": a GP line said to a parent about their child.
# "he cries wolf" is not somebody crying: the words are the idiom about a false alarm, and read
# as tears it would answer a line about exaggeration with a pool about a low mood.
CRY_WOLF = re.compile(r"\bcries?\s+wolf\b|\bcrying\s+wolf\b", re.I)


OTHER_FEELING_VERB = frozenset("""cry cries cried crying weep weeps wept weeping sob sobs
sobbed sobbing blub blubs blubbed""".split())


# "the kids", "my parents" and "they" are more than one person, so the reply cannot say "for one
# person" or "off her plate": the wording has to fit a household, not a single subject.
PLURAL_WORDS = {"kids", "children", "parents", "family", "they", "boys", "girls", "twins",
                "little ones", "grandparents", "neighbours", "neighbors"}


SHE_WORDS = {"wife", "mum", "mom", "mother", "daughter", "sister", "nan", "granny", "gran",
             "grandma", "aunt", "girlfriend", "she"}


HE_WORDS = {"dad", "father", "son", "husband", "brother", "grandad", "grandpa", "uncle",
            "boyfriend", "he"}


# A line that names a symptom or asks a question is not small talk about someone's mood: it
# belongs to the health and safety readings ("my baby is floppy", "should i worry?").
OTHER_STOP = re.compile(
    r"\b(?:floppy|limp|unresponsive|breath\w*|blue|fever|temperature|rash|sick|vomit\w*|"
    r"diarr?h\w*|pain|hurt\w*|bleed\w*|collapse\w*|seizure|fit|stroke|hospital|doctor|gp|"
    r"surgery|ambulance|infection|swell\w*|forget\w*|memory|dementia|confus\w*|dizzy|"
    r"faint\w*|chest|blood|pregnan\w*|die[ds]?|death|passed away|"
    # The cause of the tiredness, not the tiredness: "my mum is exhausted, she has cancer" is
    # not small talk about a mood, and "take something off her plate" is no answer to it.
    r"cancer|chemo\w*|radiotherap\w*|dialysis|diagnos\w*|operation|recover\w*|hospice|"
    r"terminal|palliative|parkinson\w*|tumou?r|transplant|consultant)\b")


OTHER_QUESTION = re.compile(r"\b(?:is|are|was|were|should|shall|can|could|do|does|did|will|"
                            r"would)\s+(?:i|we|you|they|he|she|it|that|this|my|the)\b")


# "my mum is exhausted what can i do" asks for the reply, not a new subject: the question at the
# end is about the writer's own next step, and every pool for somebody else is advice, so the
# question guard must not stand the feeling down and leave the line to a search hedge. Only the
# ask about the writer's action, at the end - "what should i cook" after the same feeling is a
# different subject and keeps its own answer.
_A_HELP_ASK_AT_END = re.compile(
    r"\b(?:what|how)\s+(?:can|could|should|do)\s+(?:i|we)\s+(?:do|help)\b"
    r"(?:\s+(?:about|for|with)\s+(?:it|this|that|her|him|them|us|me)"
    r"|\s+to\s+help(?:\s+(?:her|him|them|me|us))?(?:\s+out)?"
    r"|\s+(?:her|him|them|me|us)(?:\s+out)?)?\s*[.!?]*$")


# Emphasis between the verb and the feeling ("she's really low", "they're so shattered"); these
# words say how much, never who.
OTHER_ADVERB = re.compile(r"\b(?:really|very|so|quite|pretty|totally|completely|always|a bit|"
                          r"a lot|just|still|properly|proper|too|rather|extremely|incredibly|"
                          r"absolutely|constantly|getting|seems|looking|feeling)\b")


OTHER_VERB = re.compile(r"\b(?:is|are|was|were|seems?|feels?|looks?|sounds?|been|gets?|got|"
                        r"being|keeps?|has|have)\b")


# A feeling word at the end of "a <noun> ..." is the noun of that phrase, not how somebody is:
# "hes a labrador cross" is a breed of dog, and it was answered "That would wind anyone up. Is
# there anything you can do about it?" - a question about a quarrel nobody had, asked about a
# puppy. "a bit cross" and "a little cross" are the mood, so the words that measure one are not
# nouns here.
A_KIND_OF_THING = re.compile(
    r"\b(?:a|an|the)\s+(?:[a-z][a-z'-]*\s+){0,3}$", re.I)


HOW_MUCH_OF_IT = frozenset("bit little touch lot wee tad mite mood right proper terrible awful "
                           "total complete".split())


def _names_a_kind_of_thing(between, after):
    """Whether the feeling word names a kind of thing rather than naming a mood.

    Read only where the word ends the phrase and a determiner stands in front of it: "a labrador
    cross", "a cross between the two", "the cross breed". "hes a bit cross" keeps its mood,
    because "bit" is how much of it there is.
    """
    if after.strip(" .,!?;:").strip():
        return False
    words = [word.strip(".,!?;:").lower() for word in str(between or "").split()]
    words = [word for word in words if word]
    if not words:
        return False
    articles = ("a", "an", "the")
    if words[-1] in articles:
        return True  # "my dog is a cross"
    articles_at = [index for index, word in enumerate(words) if word in articles]
    if not articles_at:
        return False
    of_the_kind = words[articles_at[-1] + 1:]
    if any(word in HOW_MUCH_OF_IT for word in of_the_kind):
        return False  # "hes a bit cross": how much of the mood there is, not a kind of thing
    return bool(of_the_kind)  # "a labrador cross", "a springer spaniel cross"


# A "not" between the person and the feeling turns the sentence over: "my wife is not tired" is
# the opposite of "my wife is tired", so it gets no reply about her at all. "not" and "never"
# count only where they sit, before the feeling: "tired of not being listened to" is still tired.
OTHER_NEG = re.compile(r"\b(?:not|never|no|hardly|barely)\b|\b\w+n't\b|\b(?:isnt|arent|wasnt|"
                       r"werent|dont|doesnt|didnt|cant|couldnt|wouldnt|shouldnt|hasnt|havent|"
                       r"aint)\b")


# Replies about the other person. Pronouns only in object position ("{obj}", "{poss}") so a
# partner, a friend and "the kids" all read right.
# The line for a feeling that has no pool of its own yet. See _someone_reply: it is the floor,
# not a table, so a group added to the reading can never turn somebody else's feeling into an echo.
GENERIC_OTHER_REPLIES = (
    "That's a lot for {obj} to be carrying. What's been happening?",
    "Sounds like {subj} has something heavy on {poss} mind. Is {subj} talking about it?",
)


OTHER_REPLIES = {
    # Someone else being taken for granted: the reply says the thing back and asks what would
    # change it, rather than the general line about a person with something on their mind.
    "unappreciated": (
        "That is a slow one to watch. Is there one job {subj} could hand over this week?",
        "Being taken for granted wears anybody down. What would {subj} want noticed first?",
    ),
    "tired": (
        "Tired like that is hard to watch. Is there any chance for {obj} to rest?",
        "That's a lot of tired {target}. Worth taking something off {poss} {plate} this week.",
        "That deep tiredness usually has a cause. Worth getting it looked at if it does not lift.",
    ),
    "stressed": (
        "That sounds like a lot on {poss} {plate}. Is there anything you can lift for {obj}?",
        "Stress that runs on needs something to change, not just a rest. What's driving it?",
    ),
    # A weight coming off somebody else is worth marking, and it is not their party: "Good -
    # that's worth celebrating" was the line before relief had a group, and every word that is a
    # group of its own needs a pool here, because this table is read by the group's name.
    "relieved": (
        "That's a weight off {poss} mind. Did {subj} say what it was about?",
        "Relief like that usually follows something heavy. {Subj_has} {subj} had a rough time of it?",
        "Good - that sounds like it had been sitting on {obj} a while. What changed?",
    ),
    "anxious": (
        "That sounds rough for {obj}. Do you know what's behind it?",
        "Worry that runs on is tiring in itself. A walk together usually helps more than advice.",
    ),
    "sad": (
        "Low patches are hard to watch. Do you know what's behind it?",
        "That's a lot for {obj} to carry. Small things done together often help more than words.",
    ),
    "lonely": (
        "Loneliness is hard to watch. Is there someone nearby who could keep {obj} company?",
        "That's rough on {obj}. A visit or a phone call this week would probably mean a lot.",
    ),
    "bored": (
        "Boredom is easier to fix than most. What used to keep {obj} busy?",
        "Worth trying something new together — a walk, a class, anything with a fixed time.",
    ),
    "annoyed": (
        "That would wind anyone up. Is there anything you can do about it?",
        "Fair enough for {obj} to be cross. What happened?",
    ),
    "happy": (
        "Lovely to hear. What's made {obj} so happy?",
        "Good — that's worth celebrating.",
    ),
}


# A feeling with a cause in front of it ("scared of the dark", "anxious about the birth",
# "nervous about starting school") is about that thing, so the reply names it and asks about
# them. A free-floating worry pool would be homework for the person listening ("write down
# what's at stake"), which is the wrong job for someone worried about a child.
ABOUT_REPLIES = {
    "anxious": (
        "Nerves with a real cause in front of them are easier to talk about. What {subj_does} "
        "{subj} say the worst of it is?",
        "That's a big thing for {obj} to have in {poss} head all day. {Subj_is} {subj} talking about "
        "it?",
    ),
    "relieved": (
        "Something real came off {poss} shoulders there. What {subj_does} {subj} say about it?",
        "That's a real weight to lose. {Subj_is} {subj} talking about what {subj} went through?",
    ),
    "stressed": (
        "That's a real weight to have on {poss} {plate}. What part of it is the worst?",
        "Stress with a cause in front of it is worth naming. What {subj_does} {subj} say about "
        "it?",
    ),
    "sad": (
        "Sad about something that really happened needs room rather than fixing. {Subj_is} {subj} "
        "talking about it?",
        "That's a real thing for {obj} to be sad about. What {subj_does} {subj} say about it?",
    ),
    "annoyed": (
        "That would wind anyone up. What's the worst part of it for {obj}?",
        "Fair enough for {obj} to be cross about it. {Subj_has} {subj} said anything to them?",
    ),
    "guilty": (
        "Feeling bad about something real is not the same as being to blame. What {subj_does} "
        "{subj} say about it?",
        "That's a heavy thing for {obj} to be carrying. {Subj_is} {subj} talking about it?",
    ),
    "happy": (
        "Lovely that {subj} {subj_is} pleased about it. What happened?",
        "Good news with a reason behind it — worth hearing the whole thing.",
    ),
}


# Being tired of a thing that stays ("his job", "the commute") is not a row, so the reply asks
# about the thing rather than offering sympathy for a quarrel.
# The lead is made of the words the person used: "im fed up of this flat" got back "Tired of this
# flat is its own kind of tired", which hands them a word they did not choose. Each phrase has its
# own gerund, so the reply says "Being fed up of" to somebody who said fed up and "Being sick of"
# to somebody who said sick.
FEDUP_LEAD = {
    "fed up": "Being fed up with",
    "tired of": "Being tired of",
    "sick of": "Being sick of",
    "sick and tired of": "Being sick and tired of",
    "fed up with": "Being fed up with",
    "fed up of": "Being fed up of",
    "done with": "Being done with",
    "had enough of": "Having had enough of",
    "had it with": "Having had it with",
    # The same worn-down feeling in the words people actually use: "im browned off with my job"
    # and "im peeved about the rota" were answered "Thanks for telling me" before the fed-up
    # branch knew them.
    "browned off": "Being browned off with",
    "browned off with": "Being browned off with",
    "browned off of": "Being browned off of",
    "peeved": "Being peeved about",
    "peeved with": "Being peeved with",
    "peeved about": "Being peeved about",
    "peeved at": "Being peeved at",
}


FEDUP_REPLIES = (
    "{lead} {thing} is its own kind of tired. What's the worst part of it for {obj}?",
    # {obj} rather than "a person": the same pool answers for somebody else ("my husband is fed
    # up with the commute"), but when it is the person writing it has to speak to them.
    "{lead} {thing} wears {obj} down more than a late night does. What would have to change?",
    "What is it about {thing} that has worn {obj} out?",
)


# A thing that is itself a state ("fed up of being ill") reads badly after "being ... of", so the
# only template that does not put the lead in front of it answers a gerund.
FEDUP_GERUND_SAFE = ("What is it about {thing} that has worn {obj} out?",)


# What they are tired of when it is not a thing but the whole of it: their life, living, trying.
# These are not a thing to ask after ("What is it about living that has worn you out?"), and the
# crisis band has its own words for some of them, so the branch that asks about the thing named
# stays out of the way and the low-mood pool answers instead.
FED_UP_WHOLE_OF_IT = re.compile(
    r"\b(?:with|of)\s+(?:(?:my|your|our|his|her|their)\s+)?"
    r"(?:life|living|alive|being alive|existing|trying|everything|anything|it all|the lot|"
    r"the world|feeling|feel|how i feel)\b")


def _recent_plural(memory):
    """True when the last few lines named more than one person, so a bare "they" has one."""
    turns = (memory or {}).get("turns")
    if not isinstance(turns, list):
        return False
    said = " ".join(str(turn.get("user", "")).lower() for turn in turns[-3:]
                    if isinstance(turn, dict))
    if not said:
        return False
    if any(word in said.split() for word in PLURAL_WORDS):
        return True
    return bool(JOINED_PERSON.search(said))


def _pronouns(word):
    """(her, her, False), (him, his, False) or (them, their, True): whose feeling it is.

    The flag is plural, because "the kids are exhausted" needs "off their plates", not "for one
    person, off her plate"."""
    word = word.lower()
    if word in PLURAL_WORDS:
        return "them", "their", True
    if word in SHE_WORDS:
        return "her", "her", False
    if word in HE_WORDS:
        return "him", "his", False
    return "them", "their", True


# A person whose night went wrong is tired, and saying so is the answer: "my son slept badly"
# and "the neighbours had a bad night" are about them, and read as nothing they were echoed back
# ("Noted: your son slept badly"). The sleep words are the tiredness, so the tired pool answers
# it, worded for the person the line named.
OTHER_BAD_NIGHT = re.compile(
    r"\b(?:slept (?:badly|terribly|awfully|rotten|horribly|awful|terrible|rubbish|lousy|poorly)|"
    r"(?:hardly|barely|didn'?t|didnt|couldn'?t|no) (?:any )?(?:slept|sleep)|"
    r"up all night|awake all night|"
    r"(?:bad|terrible|awful|rubbish|rotten|rough|poor|lousy|restless|broken|sleepless) nights?|"
    r"nights sleep)\b")


def _other_feeling(clean, memory=None):
    """(feeling, person) when the line is about how someone else feels, else None.

    "my wife is really tired" and "she's been low" are about her, so the reply must not tell
    the user to rest. The self check keeps "my mum is in hospital and i'm worried" as the
    user's own worry."""
    # "sick of the noise" is being fed up, not ill, so it must not trip the symptom guard.
    body = re.sub(r"\b(?:sick of|tired of|fed up with|fed up of|done with|had enough of|"
                  r"had it with)\s+[^.!?]*$", "", clean)
    asked = _A_HELP_ASK_AT_END.sub("", clean).strip()
    if clean.endswith("?") and asked == clean:
        return None
    if OTHER_STOP.search(body) or OTHER_QUESTION.search(asked):
        return None
    if CRY_WOLF.search(clean):
        return None  # "he cries wolf" is an idiom about a false alarm, not tears
    # "she's shattered" carries its verb inside the contraction, so there is no separate word
    # before the feeling and the usual verb check would miss it.
    be_verb = False
    match = OTHER_PERSON.search(clean)
    if match:
        word, start = match.group(1), match.end()
    else:
        match = OTHER_PRONOUN.match(clean)
        if not match:
            return None
        pronoun = match.group(0)
        word, start = pronoun.split("'")[0].rstrip("s"), match.end()
        if word.lower() in ("they", "them", "their", "we", "us", "you"):
            # "they are tired" names nobody, so there is no one to answer about unless the last
            # few lines did: the neutral line is the better reply until then.
            if not _recent_plural(memory):
                return None
        be_verb = re.search(r"(?:'s|'re|s|re)$", pronoun) is not None and len(pronoun) > 2
    rest = clean[start:]
    # "my boss is angry with me" and "my mum is worried about me" are about the user too:
    # the feeling points back at them, so the ordinary reading is the right one. "my wife is
    # tired of me" is the same: it is news about the relationship, not about her mood, and
    # siding with her ("fair enough for her to be cross") is the last thing the user needs.
    if re.search(r"\b(?:with|at|about|of|by)\s+(?:me|us)\b", rest):
        return None
    # "my friend is lonely since she moved": a pronoun later in the line settles who it is.
    if word.lower() not in SHE_WORDS and word.lower() not in HE_WORDS:
        if re.search(r"\b(she|her|hers)\b", rest):
            word = "she"
        elif re.search(r"\b(he|him|his)\b", rest):
            word = "he"
    # The other ways of saying "tired of a thing": "sick of the noise", "done with the commute",
    # "had enough of it". They are not in the feeling table because they say nothing about
    # health, so they are read here, with the thing they name.
    fed = re.search(r"\b(?:sick of|done with|had enough of|had it with)\b\s*(.*)$", rest)
    if fed:
        thing = _the_thing(fed.group(1))
        pronouns = _pronouns(word)
        if thing and _thing_that_stays(thing):
            return "fedup", *pronouns, thing
        return "annoyed", *pronouns
    # A night that went wrong is the other person's tiredness, said in their own words.
    if OTHER_BAD_NIGHT.search(rest):
        return ("tired",) + _pronouns(word)
    for name, words in FEELINGS:
        for feeling in words:
            hit = re.search(r"\b" + re.escape(feeling) + r"\b", rest)
            if not hit:
                continue
            between = rest[:hit.start()]
            if _names_a_kind_of_thing(between, rest[hit.start() + len(feeling):]):
                continue
            glue = OTHER_ADVERB.sub("", between).strip()
            # "she's really low": the contraction is the verb, the rest is only emphasis. And the
            # feeling can be the verb itself ("he just cries"), which is the one shape with no
            # "is" to find.
            their_verb = not glue and not be_verb and feeling in OTHER_FEELING_VERB
            if not (their_verb or OTHER_VERB.search(between) or (be_verb and not glue)):
                continue
            # A mood word that runs straight on into another word is describing that word,
            # not saying how somebody feels: "he explained why he was late but it was a
            # rubbish excuse" is about the excuse, and the kind word for it ("low patches are
            # hard to watch") answered a feeling nobody had. The reading's own rule decides
            # whether a word is a feeling or a description, so the two sides cannot drift.
            # The crying verbs are the one exception: the person is the subject and the word is
            # the verb they do ("he weeps most nights", "he sobs down the phone"), so there is no
            # noun it could be describing.
            if not their_verb and not cue_about_person(clean, feeling):
                continue
            # A word of strain said of a person is what that person does to the person typing,
            # never how they feel: "my sister is exhausting" was answered "That's a lot of tired
            # for one person to be carrying. Worth taking something off her plate", which has the
            # burden the wrong way round. The state words ("exhausted", "worn out", "drained")
            # still come here: "she is exhausted" is her state, not the effect she has.
            if feeling in WEARS_OTHER_PEOPLE_OUT:
                continue
            if re.search(r"\b(?:i'm|im|i am|i feel|i've|i have|me|my)\b", between):
                return None
            # "my wife is not tired", "she isnt tired": the word between the person and the
            # feeling says it is the other way round, so there is nothing to answer about.
            if OTHER_NEG.search(between):
                continue
            after = rest[hit.start():]
            # A feeling said *with* a person is how the two of them are, not a free-floating
            # annoyance: "she is browned off with me" is the relationship question ("You seem a
            # bit off with me - have I done something?"), and the fed-up pool's "what's the
            # worst part of it" throws that answer away. Let the row that answers the
            # relationship have the line.
            if re.match(r"\b" + re.escape(feeling) +
                        r"\s+with\s+(?:me|us|him|her|them)\b", after):
                return None
            # A feeling with a thing after it is about that thing: "tired of his job" is fed up
            # with the job, "scared of the dark" is afraid of the dark, "anxious about the
            # birth" is worried about the birth. Each gets its own reply, about them and about
            # the thing, rather than a free-floating pool that tells the listener what to do.
            caused = re.match(r"\b" + re.escape(feeling) + r"\s+(?:of|about|with)\s+(.+)$", after)
            if caused:
                thing = _the_thing(caused.group(1))
                if feeling in ("tired", "bored", "sick", "worn out", "done in", "fed up",
                               "browned off", "peeved"):
                    pronouns = _pronouns(word)
                    if thing and _thing_that_stays(thing):
                        return "fedup", *pronouns, thing
                    return ("bored" if feeling == "bored" else "annoyed"), *pronouns
                if name in ABOUT_REPLIES:
                    return name + "_about", *_pronouns(word), thing
                continue
            if feeling == "low" and re.search(r"\blow\s+(?:on|in)\b", after):
                continue
            # "im spent up this month" is money, not tiredness, and main noted it as the fact it
            # is: the advice about an early night is for the other sense.
            if feeling == "spent" and re.search(r"\bspent\s+(?:up|all|it|my|the|every)\b", after):
                continue
            # "my brother and his wife are exhausted" is two people, so the reply cannot say
            # "one person" or "his plate": an "and" joining another person makes it plural.
            joined = clean[:start + hit.start()]
            if JOINED_PERSON.search(joined):
                return name, "them", "their", True
            return name, *_pronouns(word)
    # "my wife had a rough day" is tiredness about her too; the rough-day reply must not tell
    # the user to have a shower and an early night.
    if ROUGH_DAY.search(rest) and not re.search(r"\b(?:i'm|im|i am|i feel|i've|i had)\b", rest):
        return "tired", *_pronouns(word)
    return None


# The connector between a feeling and the thing in front of it, and the thing itself: "tired of
# his job" is the job, "anxious about the birth" is the birth. Only words people really say
# after it, and short, so a whole clause is never read as the thing.
def _the_thing(phrase):
    """The thing after "of" / "about", on its own: "his job", "the birth", "starting school"."""
    phrase = " ".join(str(phrase or "").split()).strip(" .,!?;:")
    phrase = re.split(r"\b(?:because|but|so|and|since|when|after|before|which|that)\b",
                      phrase)[0].strip()
    words = phrase.split()
    if not words or len(words) > 5:
        return ""
    return phrase


# A thing that stays ("his job", "the commute") is something to talk about; a person or a moment
# ("me", "it", "that") is the old cross reply. Only a determiner in front marks the first kind.
# "my brother and his wife", "my mum and dad", "me and my wife": a second person joined on by
# "and" means the feeling belongs to two people, however the first one is introduced.
JOINED_PERSON = re.compile(
    r"\band\s+(?:(?:his|her|their|my|our)\s+)?(?:wife|husband|partner|brother|sister|son|"
    r"daughter|mum|mom|mother|dad|father|kids?|children|parents?|family|friend|mate|boyfriend|"
    r"girlfriend)\b")


THING_THAT_STAYS = re.compile(r"^(?:my|his|her|their|our|the|this|that|these|those)\b")


def _thing_that_stays(thing):
    return bool(THING_THAT_STAYS.match(thing or ""))


# The thing a tired-of line names, in the person's own words: "fed up with my job", "sick of the
# noise", "done with the commute", "fed up of being ill". It stops at the end of that clause, so
# "fed up of my job and i want to quit" keeps the job as the thing.
FED_UP_THING = re.compile(
    r"\b(?:done with|fed up with|fed up of|browned off with|browned off of|browned off|"
    r"peeved with|peeved about|peeved at|sick of|sick and tired of|tired of|had enough of|"
    r"had it with)\s+([^,.;!?]*)")


# The thing is a noun phrase, so it ends where the next clause begins: "im tired of my job i want
# to leave" is about the job, and quoting the rest back ("your job i want to leave", and a man's
# "he never calls me" said back as "he never calls you") is not a sentence.
# A wh-word opens the next clause, so it ends the thing as surely as "and" does: "im tired of my
# job what should i do" was handed back as "Being tired of your job what should i do wears you
# down more than a late night does", which is the person's question said back as if it were a
# noun. "sick of how they treat me" already stopped at "they"; stopping at "how" leaves nothing,
# which is the honest answer (the thing is a clause, not a thing to ask about).
FED_UP_STOPS = re.compile(
    r"\b(?:and|but|so|because|cos|coz|cause|when|whenever|if|while|then|though|tho)\b"
    r"|\b(?:what|why|how|who|which|whether)\b"
    r"|\b(?:i|im|i'm|ive|i've|he|she|they|we|hes|shes|theyll|were)\b")


# A thing said with no owner in front of it is still the thing: "sick of waiting", "fed up of
# being ill", "done with the commute". A pronoun is not: "sick of it" and "fed up of everything"
# name nothing this reply could ask about.
FED_UP_BARE = re.compile(r"^(?:being\s+)?[a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,2}$")
