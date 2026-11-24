"""Part 16 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import last_bot
from ..understanding import understand
from . import (badnews)

from .fallback_data import (
    ANIMALS,
    BARE_PICK_AFTER_NEWS,
    BARE_PICK_BRING,
    BARE_PICK_DO,
    BARE_PICK_KIND,
    BARE_PICK_TAKE,
    BARE_PICK_WEAR,
    BARE_PICK_WEAR_COLD,
    BARE_PICK_WEAR_HOT,
    BARE_PICK_WEAR_WET,
    BARE_PICK_WHICH,
    CRISIS_WORDS,
    FAVOURITE_WORDS,
    FORECAST,
    FORECAST_AFTER_SAFETY,
    FORECAST_DURATION,
    FORECAST_PERMISSION,
    FORECAST_PERSON,
    FORECAST_PET,
    FORECAST_PET_HARM,
    FORECAST_SELF,
    FORECAST_SELF_STRUGGLING,
    FORECAST_SOMEONE_STRUGGLING,
    HEALTH_WHO,
    NOT_PEOPLE_WORDS,
    OPINION_ASKS,
    PLAIN_WORDS,
    REACTIONS_CARE,
    REACTIONS_SAID,
    TRIED_HELPED_ELSEWHERE,
    TRIED_HELPED_REPLIES,
    TRIED_IT_REPLIES,
    TRIED_NO_CHANGE_ELSEWHERE,
    TRIED_SORTED_REPLIES,
    TRIED_NO_CHANGE_REPLIES,
    TRIED_WORSE_REPLIES,
    UNKNOWN_HEALTH,
    UNKNOWN_WHO,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    NAMED_BODIES,
)
from .fallback_part_01 import (
    UNKNOWN_HOW_IT_GOES_FOR_A_HARD_TIME, UNKNOWN_HOW_IT_GOES_FOR_A_PET,
    UNKNOWN_HOW_IT_GOES_FOR_SOMEONE, UNKNOWN_HOW_LONG_IN_HOSPITAL, UNKNOWN_IF_THEY_STILL_CAN, _has,
    _matchable,
)
from .fallback_part_02 import (
    AN_ILLNESS, A_HARD_TIME, A_MEDICAL_THREAD, _the_thread_said, ASKED_ABOUT, WHETHER_IT_GOES_WELL,
    WHETHER_IT_GOES_WELL_ITSELF, WHETHER_IT_IS_THEIR_AGE, WHETHER_IT_LONGER_HAS_GOT,
    WHETHER_THEY_CAN_STILL, _a_person_in_the_thread, _a_pet_in_trouble, _A_CANDIDATE_OF_ITS_OWN,
    _BODY_TOPICS, _LEANS_ON_THE_THREAD, _thread_is_about_someone_else,
)
from .fallback_part_03 import (
    _AFTER_A_CLAUSE, BARE_PICK, BARE_PICK_NEEDS_THE_THING, OCCASION_ABOVE, THE_DAY_IS_NAMED,
    _a_subject_above, _a_trip_above, _an_occasion_above, _an_occasion_in_the_thread, _weather_above,
    HEAVY_ABOVE, WHO_FOR_IT, WHO_FOR_IT_BODY, WHO_FOR_IT_ROUTES, WHO_FOR_IT_SAID,
    WHO_FOR_IT_SAID_VOICE, WHO_NAMED_BEFORE, WHO_TO_TALK_ASK, WHO_TO_TALK_TO,
    WHO_TO_TALK_TO_A_BAD_STRETCH,
)
from .fallback_part_05 import (
    _a_verdict_line, _the_person_already_said_it,
)
from .fallback_part_07 import (
    _someone_is_a_patient,
)
from .fallback_part_08 import (
    _news_above, _is_about_the_persons_own_life, HAND_BACK, YOUR_DAY_ASK, YOUR_OWN_TIME,
    YOUR_TIME_ASK, _asks_how_are_you,
)
from .fallback_part_09 import (
    BESIDE_THEIR_OWN, FAVOURITE_WORDS, TASTE_LINES,
)
from .fallback_part_10 import (
    _hedged_recently, _thread_is_about_the_body, MEAN_WORDS, POINTERS, POINTING_ASK,
    POINTING_IDIOMS, POINTING_WORDS, _a_previous_line_named_something, _a_body_in_the_thread,
    _a_hard_patch_in_the_thread, _the_forecast_subject, _thread_said, _whose_body,
)
from .fallback_part_11 import (
    an_outcome_asked_about_someone, _answered_recently, _a_bad_stretch_above,
    _thread_has_a_health_visit,
)
from .fallback_part_12 import (
    _about, _an_answer_above, _self_line, _NOT_MANAGING, CLAUSE_END,
)
from .fallback_part_13 import (
    HARD_WEEK, _grief_thread, _hard_week_in_the_thread,
)
from .fallback_part_14 import (
    _in_a_loss_thread, _a_care_thread_to_leave_alone, AFTER_THING, ASK_WORD,
)
from .fallback_part_15 import (
    _who_for, _choose, ASK_SHAPE, in_a_safety_thread, _a_doable, _taste, _thread_answer,
    who_settles, _mood, _words, _after_advice, _a_refusal_to_answer, OWN_THING, _words_kept,
)


def _a_hard_time_and_not_a_body(memory, line=""):
    """True when the thread is about a rough patch and says nothing about a body.

    The pools that name the people treating somebody are right where there is a body to treat and
    wrong where there is not: "my mum is having a hard time" / "is she going to be ok" is about a
    spell of trouble, and nobody is treating her for it. Something in the thread that is a body,
    a bed or an illness keeps the pools, so this only stands between them and a thread of feeling.
    """
    said = _the_thread_said(memory) + " " + str(line or "")
    if A_MEDICAL_THREAD.search(said) or AN_ILLNESS.search(said):
        return False
    return bool(A_HARD_TIME.search(_the_thread_said(memory)))


def _the_pool_for_a_worry_about_them(clean, memory):
    """The pool for "is he going to be ok" and its kind, or None.

    Read from the line and the thread together, like `_thread_is_about_someone_else`: "is he going
    to be ok" names nobody, and the line before it ("my dad had a car accident", "my dog drank sea
    water") says who he is and which doctor he has. A line that names nobody and follows a thread
    that names nobody is not this ask, which keeps "will they stretch" about a pair of shoes out
    of both pools.
    """
    line = re.sub(r"[^a-z0-9' ]", " ", str(clean or "").lower())
    # The readers that already answer a follow-up like this keep their turn: `greeting` offers
    # them only to a hedge, so a pool of mine here would take the answer away from them. The ward
    # reader (`an_outcome_asked_about_someone`) says the same thing better where the thread has
    # somebody in a bed, and `the_threads_answer` owns the ask that only points at the thread.
    if an_outcome_asked_about_someone(clean, memory) or the_threads_answer(clean, memory):
        return None
    still = WHETHER_THEY_CAN_STILL.search(line)
    itself = WHETHER_IT_GOES_WELL_ITSELF.search(line) or WHETHER_IT_LONGER_HAS_GOT.search(line)
    if itself:
        # "how long has he got" after "my cat has kidney disease" is the vet's, and the animal
        # comes first here so that a pet thread is not turned away by the person-only check.
        if _a_pet_in_trouble(line, memory):
            return UNKNOWN_HOW_IT_GOES_FOR_A_PET
        if not _a_person_in_the_thread(memory):
            return None
        if not (WHETHER_IT_LONGER_HAS_GOT.search(line)
                or AN_ILLNESS.search(_the_thread_said(memory))):
            return None
    if not (still or itself or WHETHER_IT_GOES_WELL.search(line)
            or WHETHER_IT_IS_THEIR_AGE.search(line)):
        return None
    subject = ASKED_ABOUT.search(line)
    named = subject.group(0) if subject else ""
    if set(named.split()) & (ANIMALS | NOT_PEOPLE_WORDS):
        return UNKNOWN_HOW_IT_GOES_FOR_A_PET
    if not named or re.match(r"(?:he|she|they)\b", named):
        # "he" / "she" / "they" / no subject at all: the thread says who it is, and the nearest
        # line that names somebody is the one that decides which waiting room this is.
        if _a_pet_in_trouble(line, memory):
            return UNKNOWN_HOW_IT_GOES_FOR_A_PET
        if not _a_person_in_the_thread(memory):
            return None
    if still:
        return UNKNOWN_IF_THEY_STILL_CAN
    if _a_hard_time_and_not_a_body(memory, line):
        # A rough patch is not a patient: the pools below would hand them to a ward that has never
        # heard of them, and the search hedge would say nothing, so this keeps the ask and drops
        # the ward.
        return UNKNOWN_HOW_IT_GOES_FOR_A_HARD_TIME
    if _someone_is_a_patient(line, memory.get("turns") or []):
        return UNKNOWN_HOW_LONG_IN_HOSPITAL
    return UNKNOWN_HOW_IT_GOES_FOR_SOMEONE


def _the_threads_who(memory, look_back=2):
    """The person the thread's own line hands the question to, or None.

    A follow-up that points at the thread ("will that get better", "will it settle down") names
    nothing itself, so the line it points at is the only place the world is. A tooth that aches
    in cold water is the dentist's, and the follow-up about it is the dentist's too; a puppy is
    the vet's. The health hand-off is left out because the health pool says it better than one
    line about who to ring.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in reversed(turns[-look_back:]):
        said = " " + re.sub(r"[^a-z0-9']", " ", (turn.get("user") or "").lower()) + " "
        words = said.replace("'", "").split()
        if not words:
            continue
        who = _who_for(said.strip(), said, words, None)
        if who and who != HEALTH_WHO:
            return who
    return None


def the_threads_answer(text, memory):
    """The line for a follow-up that only points at the thread, or None.

    "i cant breathe when i run for the bus" then "will that get better if i keep at it" is the
    question the person would put to their own doctor, and the plain shrug met it with "a quick
    search online will get you a solid answer": a reading list for a symptom. The line names no
    subject of its own, so the thread is the only place the world is, and the thread decides
    which honest answer fits - a body's is the GP's, a puppy's is the vet's.

    It is offered to `greeting.respond`, which asks it only of a hedge: a follow-up that already
    has an answer or a card's next step keeps it (`my wrist is sore after typing all day` then
    "will that get better on its own" is answered from the wrist card on the screen).
    """
    clean = " ".join(str(text or "").split())
    if not clean or _hedged_recently(memory):
        return None
    try:
        understood = understand(clean, memory)
    except Exception:  # noqa: BLE001 - a line the engine chokes on is not this reader's
        understood = {}
    if not _the_ask_is_the_threads(clean, understood):
        return None
    who = _the_threads_who(memory)
    if who:
        return _choose([line.format(who=who) for line in UNKNOWN_WHO], memory, clean)
    # Only the line the pronoun points at, which is the one before this: a thread that talked
    # about a headache three turns ago and a rent rise on the last turn is a money thread, and
    # "will that cover it" is not a symptom. The last line on its own is not enough, because the
    # middle turn of a health thread can name no body word at all - "my back has been hurting" /
    # "its been ages now" / "can i get anything for it over the counter" is still the back's - so
    # the thread the follow-up itself leans on counts too (`understood["leans_on"]["topic"]`, from
    # the understanding engine).
    leans = (understood.get("leans_on") or {}).get("topic")
    if leans == "health" or _thread_is_about_the_body(memory, look_back=1):
        return _choose(UNKNOWN_HEALTH, memory, clean)
    return None


def _the_ask_is_the_threads(clean, understood):
    """True when the line asks something about a thing it only points at."""
    if not (ASK_SHAPE.search(clean) and _LEANS_ON_THE_THREAD.search(clean)):
        return False
    # A line that names a thing of its own is asking about that thing, not about the thread: on
    # "my knees hurt after 10 mins" then "is it my shoes", the thread is a body and this reader
    # answered it with the GP's line - "ring 111 or your surgery" - which is the one answer a
    # question about a pair of trainers must not get.
    if _A_CANDIDATE_OF_ITS_OWN.search(clean.lower()):
        return False
    return (understood or {}).get("topic") in _BODY_TOPICS


def _the_ask_clause(clean, memory=None):
    """The ask a line ends with when something sits in front of it, or "" when nothing does."""
    said = " ".join(str(clean or "").lower().split())
    if not said:
        return ""
    ask = ""
    reading = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(reading, dict):
        focus = " ".join(reading.get("focus") or []).split()
        if len(focus) >= 3 and said.endswith(" ".join(focus)) and " ".join(focus) != said:
            ask = " ".join(focus)
    if not ask:
        found = _AFTER_A_CLAUSE.search(said)
        ask = " ".join(found.group(1).split()) if found else ""
    return ask if len(ask.split()) >= 3 else ""


def _bare_pick(clean, memory=None):
    """The pool for a line that asks the bot to choose and names nothing to choose between."""
    found = BARE_PICK.match(clean)
    from_the_clause = False
    if not found:
        ask = _the_ask_clause(clean, memory)
        found = BARE_PICK.match(ask) if ask else None
        from_the_clause = found is not None
    if not found:
        return None
    if found.group(0).strip().lower().startswith("which"):
        # a choice with nothing to choose between: the things are the answer, not who it is for
        return BARE_PICK_WHICH
    verb = " ".join(found.group("verb").lower().split())
    pool = BARE_PICK_KIND.get(verb, BARE_PICK_DO)
    if from_the_clause and (OCCASION_ABOVE.search(str(clean or ""))
                            or THE_DAY_IS_NAMED.search(str(clean or ""))
                            or _an_occasion_in_the_thread(memory)):
        # The pool asks where the person is going, and the line or the thread has already said:
        # "back to the wedding, what should i wear" was asked where the day is, when the wedding
        # was the day. Asking again reads as a bot that was not listening, so a line that came to
        # the pool through its own clause stands down where the ask it carries already answers
        # the question the pool would ask.
        return None
    if from_the_clause and pool is BARE_PICK_DO:
        # "what should i do" with no object is answered by asking what has gone on, and the clause
        # in front has just said it: "i havent written a cv in ten years, what should i do" is a
        # person asking about the cv, and "tell me what has gone on" asks them to say it again.
        # The widest ask keeps its whole-line answer for a line that names nothing.
        return None
    if verb in BARE_PICK_NEEDS_THE_THING and _a_subject_above(memory):
        # the thing was named a turn ago, so this is the follow-up's turn, not the ask's
        return None
    if pool is BARE_PICK_WEAR and not _an_occasion_above(memory):
        weather = _weather_above(memory)
        if weather == "wet":
            return BARE_PICK_WEAR_WET
        if weather == "cold":
            return BARE_PICK_WEAR_COLD
        if weather == "hot":
            return BARE_PICK_WEAR_HOT
    if pool is BARE_PICK_BRING and _a_trip_above(memory):
        # the thread said where they are going, so the packing line is an answer and not a guess
        return BARE_PICK_TAKE
    if pool is BARE_PICK_DO and _news_above(memory, heavy=True):
        # "my mum died" / "what should i do" is the news, asked again: this pool has nothing true
        # to say about a death it was not told, and asking what has gone on reads as a friend who
        # was not listening. Standing down to nothing is not a fix either - the turn then went to
        # the search shrug, which is the worst line in the bot for somebody with a death or a
        # scare on their plate, so the stand-down names where it stands down to.
        return BARE_PICK_AFTER_NEWS
    return pool


def a_verdict_stands_down(memory=None):
    """True when this thread is one a light verdict must not answer.

    A verdict is a light turn, and three threads are not light: a live emergency ("my husband hit
    me" then "thats annoying" is still that thread - the bot's continuation is the turn), a
    bereavement or a hard week ("my mum died last week" then "thats a shame" is not a light
    verdict, and the shame pool asked "What went wrong?"), and a thread the bot has already been
    careful about. The reading stands down for the whole thread rather than for a list of its
    words, the same way `_a_verdict` does for a good verdict in a hard week.
    """
    if not memory:
        return False
    try:
        if in_a_safety_thread(memory) or _in_a_loss_thread(memory) or _grief_thread(memory):
            return True
    except Exception:  # noqa: BLE001 - a thread that cannot be read claims nothing
        return False
    # An accident, an operation, a body in trouble a turn ago: the same hard week `_a_verdict`
    # stands down for, minus the general bad news. A line of bad news (an eviction, a sacking) is
    # a light verdict's proper place - "Annoying, that. Is it sorted?" is the reply to it - while
    # a death or a fall is not.
    # A diagnosis and a baby lost are the same hard week as a death, and a list of accidents does
    # not hold them: "i have cancer" then "what a nightmare" was answered with "Annoying. Is it a
    # quick fix or a whole thing?", and "my wife is having a miscarriage right now" then "thats a
    # shame" with "Gutted for you. Do you want to talk it through?". The readings exist
    # (`HEAVY_ABOVE` holds the diagnoses, `badnews.reads_as_sudden_loss` the baby and the suicide)
    # and a job or a rent rise is in neither, so an eviction keeps its verdict.
    for turn in [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if not line:
            continue
        if HARD_WEEK.search(line) or HEAVY_ABOVE.search(line):
            return True
        try:
            if badnews.reads_as_sudden_loss(line):
                return True
        except Exception:  # noqa: BLE001 - a reading that cannot run claims nothing
            continue
    return False


def reaction_line(text, memory=None):
    """The composer's own line for a verdict on the thing before it, or None.

    The whole line is the verdict, so the reply is the reaction back. A topic entry can still
    take the turn on a word of it - the knowledge base's advice for dreams answered a bare
    "nightmare" - and where that happens the loss is the entry's to avoid; this says what the
    composer would have said on the line, so the fault can be measured turn by turn.
    """
    memory = memory if isinstance(memory, dict) else {}
    clean = " ".join(str(text or "").lower().split())
    pool = _a_verdict_line(clean, memory)
    if not pool:
        return None
    if _a_care_thread_to_leave_alone(memory):
        pool = REACTIONS_CARE
    elif _the_person_already_said_it(memory):
        pool = REACTIONS_SAID.get(pool, pool)
    return _choose(pool, memory, clean)


def a_doable(text, memory):
    """Read by bot/modules/greeting.py: is this line a judgement of the answer just given?

    The fallback module's own floor asks `_a_doable` too, and the greeting module asks this one
    *before* `bot/memory/detail.py`, because a short line with a copula in it is a detail to that
    reading - "sounds doable" came back "The same goes for the sounds doable: ...". One reading
    with two askers, so the two cannot disagree about whose turn a line is.
    """
    clean = " ".join(str(text or "").lower().split())
    return _a_doable(clean, memory)


def reads_as_a_taste(text, memory=None):
    """True when the line asks what the bot itself likes and the composer answers it as a taste.

    The arbiter reads this so a question about the bot's own taste is not answered by a card about
    the thing it names: "do you have a favourite food" reached the what-to-cook entry and came back
    with a list of dishes, and "whats your favourite show" with tonight's viewing picks. Those are
    good answers to "what should I cook" and "what should I watch"; neither is an answer to a
    question about the bot. Only the lines its own pools answer count, so a taste the composer has
    no line for keeps whatever else matched it.
    """
    clean = _matchable(text)
    if not clean:
        return False
    if not _has(clean, OPINION_ASKS):
        # The same question with its chat-speak put right ("whats ur favourite show"), which is how
        # the reading answers it too: the repair is what makes the line the taste question.
        try:
            clean = _matchable((understand(text, memory if isinstance(memory, dict) else {})
                                or {}).get("plain") or "")
        except Exception:  # noqa: BLE001 - a reading that fails claims nothing
            return False
        if not clean or not _has(clean, OPINION_ASKS):
            return False
    if _is_about_the_persons_own_life(clean):
        return False
    if BESIDE_THEIR_OWN.search(clean):
        return False
    if not _has(clean, FAVOURITE_WORDS):
        # A taste asked without the word favourite is left to the entry that answers it: "what do
        # you think is the best season of the year" has a card that says more than the taste, and
        # the card is the better reply there.
        return False
    try:
        reply = _taste(clean, memory if isinstance(memory, dict) else {}, False, False, "")
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False
    return bool(reply) and reply in TASTE_LINES


def _points_at_nothing(clean, memory, repaired=""):
    """True when the line is only a pointer and there is nothing in the chat for it to be."""
    for line in (clean, repaired):
        said = re.sub(r"[^a-z0-9' ]", " ", str(line or "").lower())
        words = said.replace("'", "").split()
        if not words or len(words) > 6:
            continue
        if not set(words) <= POINTING_WORDS:
            continue
        points = set(words) & POINTERS
        asks = set(words) & MEAN_WORDS
        if not points and not asks and " ".join(words) not in POINTING_IDIOMS:
            # No finger and no ask about the words: "how are you" is not pointing at anything.
            continue
        if not set(words) & POINTING_ASK and not asks:
            continue
        if ("you" in words or "u" in words) and not asks:
            # "what about you" is the hand-back, and the manners pool has already read it.
            continue
        return _nothing_to_point_at(memory)
    return False


def _nothing_to_point_at(memory):
    """True when the chat has said nothing the pointer could be about.

    An answer above the line gives "that" its subject, and the pools before this one have
    already read it. A question back is the other thing a pointer can be about - "what do you
    mean" after the bot's own question is about the question, and the repeat reader in
    `bot/compose/why.py` is the one that says it again (`said_again`). Neither is this pool's
    turn. A thread about a body or a bereavement keeps its own voice: "whats that" after "my
    chest hurts" is not a person reading a letter.
    """
    if not isinstance(memory, dict) or not memory:
        return True
    if in_a_safety_thread(memory) or _grief_thread(memory) or _thread_is_about_the_body(memory):
        return False
    if _answered_recently(memory):
        return False
    if _a_previous_line_named_something(memory):
        # The chat has a subject of its own ("i watched a film for two hours"), so "how long was
        # it" has something to be: the pools that read the thread keep the turn. The reading of
        # the gist is the memory's own (`bot/memory/topics.py`), not a second word list here.
        return False
    if "?" in (last_bot(memory) or ""):
        return False
    return True


def _forecast_pool(clean, repaired, memory):
    """The pool for a line asking how something will turn out, or None when it is not one."""
    line = next((said for said in (clean, repaired)
                 if said and FORECAST.search(said)), "")
    if not line or FORECAST_PERMISSION.search(line) or FORECAST_DURATION.search(line):
        return None
    if _in_a_loss_thread(memory) or _grief_thread(memory):
        # "my dad died in march" then "will i be ok": grief is not a body that mends, and the
        # condolence pools keep that thread.
        return None
    kind, who = _the_forecast_subject(line, memory)
    if in_a_safety_thread(memory):
        return [phrase.format(who=who or "you") for phrase in FORECAST_AFTER_SAFETY]
    if kind == "pet":
        if not (_a_body_in_the_thread(memory) or FORECAST_PET_HARM.search(_thread_said(memory))):
            # "my cat keeps scratching the sofa" / "ive tried a spray" / "will it stop" is a
            # habit, not a body, and the vet is not who answers it: only a pet that has eaten
            # something, been hit or gone lame keeps the vet's line.
            return None
        return [phrase.format(who=who) for phrase in FORECAST_PET]
    if kind == "person":
        if an_outcome_asked_about_someone(clean, memory):
            # The composer already reads this one for a person who is ill or in hospital
            # (`OUTCOME_LINES`, kept for the greeting module), and its lines were written for
            # exactly this talk: standing aside leaves them in place rather than swapping one
            # good answer about the ward for another.
            return None
        if _a_body_in_the_thread(memory):
            return [phrase.format(who=who) for phrase in FORECAST_PERSON]
        if _a_hard_patch_in_the_thread(line, memory):
            # "my sister is really struggling" then "will she be ok" is not a question about a
            # body, and "whoever is treating her" is the wrong frame for a hard patch: what can
            # be said is what the person asking can do, and who steps in if it gets darker.
            later = globals().get("_a_hard_time_and_not_a_body")
            if later and later(memory, line):
                # A reader written for exactly this shape landed later (#9034) and keeps the hard
                # patch apart from a patient itself; its lines are in the same voice, so it gets
                # the turn and this stands aside rather than answering the same line twice.
                return None
            return [phrase.format(who=who) for phrase in FORECAST_SOMEONE_STRUGGLING]
        # Anything else about a person is a guess about a life - "will she be ok on her own"
        # about an 84 year old who lives alone - and the store has nothing to say on it.
        return None
    if kind == "self":
        recent = [str(turn.get("user") or "").lower()
                  for turn in ((memory or {}).get("turns") or []) if isinstance(turn, dict)][-3:]
        if _the_threads_who(memory):
            # A thread that already hands the question to somebody of its own - a tooth out, a
            # filling gone, a puppy that will not eat - keeps that hand-off: "a dentist is the
            # one to see" answers "will it heal alright" better than a line about the GP, and it
            # is the answer main already gave.
            return None
        if _whose_body(clean, recent[-1:]) != "mine" and (
                _a_hard_patch_in_the_thread(line, memory) or _thread_is_about_someone_else(memory)):
            # "i lost my job on friday" then "will i be ok", or a father in an accident and
            # "will i be ok": neither is a body of theirs that mends. The answer is about the
            # week the person is in, not about a GP's prognosis.
            return list(FORECAST_SELF_STRUGGLING)
        return list(FORECAST_SELF)
    return None


def _in_a_crisis_thread(memory):
    """True when the bot's own last word in this stretch named a crisis line.

    `in_a_safety_thread` is true for any safety answer, and most of those are ordinary comfort:
    "my mum says im lazy" gets one, and offering a person at Samaritans on the next line - with
    999 behind it - treats a bad week as an emergency. The line meant here is the one where the
    bot has already said a crisis line out loud (`CRISIS_WORDS`), because that is the thread the
    person is already in.
    """
    answer = _thread_answer(memory)
    return bool(answer) and any(word in answer for word in CRISIS_WORDS)


def _who_for_the_thread(memory, clean, understood=None):
    """The person to take a bare "who do i call about it" to, or a reply asking what it is.

    Read only in `_unknown`, so a line with a subject of its own never gets here and the looser
    reading costs nothing: what it replaces is the shrug. Three rungs, in the order of how much
    they know about this person: the trouble they named a turn ago (the same reading that names a
    person for a line that says it outright), then the actor the bot's own answer named a moment
    ago ("report it to the council"). With neither, the honest reply is the route list for a call
    and the talk-to lines for a person to talk to, plus the one question that would settle it.
    """
    # The line as typed, not as the reading resolved it: "who do i ring about it" comes out of
    # the reading as "who do i ring about my dog", because the engine has already put the
    # pronoun back to the thing named a turn ago. The ask is the same ask, and this reader
    # wants it in the shape the person used, where the thread is visibly not named.
    typed = str((understood or {}).get("text") or "") if isinstance(understood, dict) else ""
    line = typed or clean or ""
    # A person to talk to is read before a person to ring, because the two overlap on "talk to"
    # and only one of them is a service: "who can i talk to" is somebody to listen, and it must
    # not come back with a list of desks. A line that names its own subject keeps the call
    # reading, since "who do i talk to about my landlord" is a question about a desk.
    a_voice = bool(WHO_TO_TALK_ASK.search(line)) and not re.search(
        r"\babout\s+(?!it\b|that\b|this\b|them\b)\w|"
        r"\b(?:talk|speak|chat)\s+(?:to|with)\s+(?:the|a|an|my|your|his|her|their)\b", line)
    a_call = bool(WHO_FOR_IT.match(line)) if not a_voice else False
    if not (a_call or a_voice):
        return None
    # The actor the bot's own last answer named comes first: "my landlord says its my fault" was
    # answered "ask the council's environmental health team to step in", so "who can i talk to"
    # next is a question about that answer, and standing on it is what a friend does. The wider
    # reading below is what to fall back to when the answer named nobody.
    answer = str(last_bot(memory) or "").lower()
    if answer:
        for word, name in NAMED_BODIES:
            if re.search(r"\b" + re.escape(word) + r"\b", answer):
                shapes = WHO_FOR_IT_SAID_VOICE if a_voice else WHO_NAMED_BEFORE
                return [shape.format(who=name) for shape in shapes]
    # Not just the line above: "my boiler is banging" then "is it dangerous?" then "who do i call"
    # leaves a middle turn with no trouble in it at all, and the person is still in the boiler
    # thread. Three lines is the stretch the reading itself keeps for a follow-up.
    for said in reversed([str(t.get("user") or "") for t in
                          [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-3:]
                          if isinstance(t, dict)]):
        if not said:
            continue
        try:
            who = who_settles(said, memory)
        except Exception:  # noqa: BLE001 - a reading that fails just offers the next rung
            who = None
        if who:
            shapes = WHO_FOR_IT_SAID_VOICE if a_voice else WHO_FOR_IT_SAID
            return [shape.format(who=who) for shape in shapes]
    # "im scared about the scan" then "who do i ring": the route list under this names money, a
    # repair and a form, and none of them is a body. What a person does about a body is have it
    # looked at, which is a name and an hour, not a list of trades.
    if a_call and (_thread_is_about_the_body(memory) or _thread_has_a_health_visit(memory)):
        return list(WHO_FOR_IT_BODY)
    if a_call:
        return list(WHO_FOR_IT_ROUTES)
    return list(WHO_TO_TALK_TO_A_BAD_STRETCH if _a_bad_stretch_above(memory) else WHO_TO_TALK_TO)


def reads_as_small_talk(text, memory=None):
    """True when the line is the manners question about the bot's own day, for the arbiter's use.

    "Hows your day going anyway" and "what have you been up to today" come after an answer as
    often as they open a chat, and every follow-up reader in the bot reads a question with no
    subject of its own as a question about the thing on the table: after the egg answer, "hows
    your day been" got the sentence about keeping boiled eggs in the fridge. The line is about
    the bot, though, and the pool that says how its day went is the answer to it, so the module
    that carries this file declares `TAKES_AS_IT_COMES` with this and the composer's line takes
    the turn. Safety is read before this claim, so a small talk line in a live emergency still
    gets the emergency reply.

    Only the manners question itself is claimed, and only where the pool has a line for it: a
    line the reading cannot see ("how about your day") is left to the chat module, which answers
    it better than a shrug. A line that goes on to name anything ("are you having a baby", "what
    are you doing about the damp") is not claimed.
    """
    clean = _self_line(text)
    if _about(clean, None):
        return False
    # The pool is cheerful, and the turn above may be a hard one: "i feel awful today" then "hows
    # your day been" is the bot changing the subject to itself, and "my mum has cancer" then "and
    # you" is worse. A module that read the whole thread answers those with the low line, so the
    # claim stands down for the whole hard week and not for a list of its words (spare-leopard on
    # #6004: `module == "answers"` is not a test of a hard turn, because the knowledge module
    # answers plenty of them).
    if _a_low_turn_above(memory):
        return False
    # The hand-back asked with nothing else in it is the same question: "what about you",
    # "and you", "yourself" after an answer are the person passing the question over, and the
    # pool that says how the bot's day went is the reply. Read before the phrase lists because
    # these lines carry no "how are you" for them to find.
    if HAND_BACK.match(clean):
        # A hand-back means something only where there is something to hand back from. As the
        # first thing typed there is nothing passed over, and the chat module's warmer "I'm well,
        # thanks for asking. How is your day going?" is the better opening; the fault this claim
        # answers - the follow-up readers taking the line as a question about the thing on the
        # table - only happens after a turn.
        return bool((memory or {}).get("turns") if isinstance(memory, dict) else None)
    # The claim is only worth making where the pool has a line: a line the manners reading
    # cannot see ("how about your day") is answered by the chat module with a better one, so it
    # is left alone rather than handed to a module that would shrug at it.
    if not _asks_how_are_you(clean):
        return False
    # The plain "how are you" and "hows it going" are answered by the chat module with the same
    # manners pool, so they are left to it: what this claims is the shapes it reads as a
    # question about the last thing said. `YOUR_DAY_ASK` is the widest of them and the one the
    # claim cannot leave out: it puts a verb between the person and the day ("are you having a
    # good day", "did you have a good day then"), and a line the phrase list has no entry for is
    # read by the knowledge module as a question about the thing above - after the egg answer,
    # "are you having a good day" got the paragraph about cholesterol.
    if YOUR_DAY_ASK.search(clean) and not (YOUR_OWN_TIME.search(clean)
                                          or YOUR_TIME_ASK.search(clean)):
        # The verb shape is claimed only where the fault is: after an answer. That is where the
        # knowledge module reads it as a question about the thing above, and where the chat
        # module never gets the turn. After something the person has just said, chat answers it
        # better than the pool does ("i went to a party tonight" / "did you have a good day" ->
        # "No days like that on my side, so nothing to report - how was yours?").
        return _an_answer_above(memory)
    return bool(YOUR_OWN_TIME.search(clean) or YOUR_TIME_ASK.search(clean))


def _a_low_turn_above(memory):
    """True when the last turn or two were heavy, so the cheerful pool must not take the turn.

    A hard week is the first reading (`_hard_week_in_the_thread`, which covers a death, an
    accident and a gentler word list), and the second is the engine's own sign on the person's
    line: "i feel awful today" and "i have a lump and im scared" are a low the word lists do not
    carry, and the module that reads the whole thread answers them with the low line until this
    claim stands out of the way (spare-leopard on #6004).
    """
    if not isinstance(memory, dict):
        return False
    if (_hard_week_in_the_thread(memory) or _in_a_loss_thread(memory)
            or _grief_thread(memory) or _news_above(memory)):
        return True
    for earlier in [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(earlier.get("user") or "").lower().split())
        if not line:
            continue
        # The two readings the rest of the composer already has for a heavy line: the engine's
        # sign, and the mood the pools read a word like "struggling" or "awful" by. "im really
        # struggling at the moment" is polarity 0 to the engine and negative to `_mood`, and the
        # turn after it was the cheerful pool until both were read here (sure-umbrella on
        # #6004). A diagnosis named of somebody close is neither: `_news_above` holds those,
        # with the readings of a death and a care thread.
        read = understand(line, {})
        if isinstance(read.get("polarity"), int) and read["polarity"] < 0:
            return True
        if _mood(_words(line), line) == "negative" or _NOT_MANAGING.search(line):
            return True
    return False


def the_report_reply(text, memory):
    """The reply this composer makes to a report on the advice just given, or None.

    Read by the arbiter, so that a report on the advice keeps the turn the composer's reading of
    the line earned it: the module that proposes the reply sits under the floor (the composer
    only fills the floor), and a pool line from a module above it would otherwise stand it down.
    The same call on the same thread gives the same words - `_choose` seeds on the advice and the
    thread - so the arbiter can compare what was proposed with what the report's answer is,
    without a second copy of the reading or of the wording.
    """
    clean = " ".join(str(text or "").lower().split())
    try:
        return _after_advice(memory, clean, clean.split())
    except Exception:  # noqa: BLE001 - a reading that fails offers no reply
        return None


def a_report_that_says_something(text, memory):
    """Does the composer answer a report on the advice with something other than a status question?

    The pool that asks "How is it going with it so far?" is the lightest of the report replies,
    and it is the one case where the composer should not take the turn off a module above it: "ok
    done that" after the energy bill entry is answered with the next part of that entry ("Ask your
    supplier in writing for the standing charge and unit rate ... cheapest tariff"), and asking
    the person how it is going instead is the same fault as a goodbye. A report that is answered
    with an outcome - worse, no change, sorted - does say something, and keeps the turn.
    """
    reply = the_report_reply(text, memory)
    return bool(reply) and reply not in TRIED_IT_REPLIES


def reads_as_a_refusal(text, memory):
    """Read by the arbiter: is this line somebody else's no, which the composer answers?"""
    clean = " ".join(str(text or "").lower().split())
    try:
        return bool(_a_refusal_to_answer(clean, memory, clean.split()))
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return False


def asks_about_the_last_answer(line, last, own=()):
    """True when the line asks about something the bot's last answer named.

    It has to be an ask: "can i pop the blister" after the scald answer is a question about the
    burn, while "chest pain again" is the person saying the same thing and the health entry
    answers it. And only a word long enough to be a subject counts ("blister", "nosebleed"), so
    an ordinary follow-up cannot match on a common word and take a topic entry's turn.

    The used word also has to be the thing the line is about. A first-aid answer is a paragraph,
    so it shares some word with almost anything: "my running shoes give me blisters what do i do"
    after a scald shares "blisters", "water" and "running" with the burn answer, and both of the
    lines below are about something else the person has just brought in. Three readings keep
    those with their entry:

    - the line names other subjects as well (`own`, the topics its own words point at). "my water
      bill is huge" is money and "my running shoes" is fitness, so a line carrying more than its
      one subject has moved on to a new thing and its entry has the better claim.
    - the line says "my <something>" that is not the shared word ("should i take ibuprofen for my
      headache" after a nosebleed is about the headache).
    - the line puts the shared word in front of a thing of its own ("how do i get blood out of a
      shirt" after a nosebleed is a laundry question, and the stain is in the shirt, not in the
      nose; "blood stains out of cotton" is the same line without the article).

    smooth-lark found the last one at the head of this rule: `blood` is named by the nosebleed
    answer, one subject, no "my <thing>", so every test above passed while the laundry entry lost
    its turn to a care continuation that said nothing about the shirt.
    """
    if not line or not last:
        return False
    text = str(line).lower()
    if "?" not in text and not ASK_WORD.search(text):
        return False
    if len(set(own)) > 1:
        return False
    named = set(OWN_THING.findall(text))
    for word in _words(text):
        if len(word) < 5 or word in PLAIN_WORDS:
            continue
        if word not in last:
            continue
        if named and word not in named:
            # The line says "my <something else>", so it is not about the thing just answered.
            return False
        for said in re.finditer(r"\b" + re.escape(word) + r"\b", text):
            # The rest of the clause, not the whole line: a new object in a later clause is
            # another question, and the clause it sits in already reads as an ask.
            clause = CLAUSE_END.split(text[said.end():], 1)[0]
            brought_in = AFTER_THING.search(clause)
            if not brought_in:
                continue
            thing = brought_in.group(1)
            if len(thing) >= 4 and thing not in PLAIN_WORDS and thing not in last:
                # "blood out of a shirt": the thing the line is really about is the shirt.
                return False
        return True
    return False


def asks_about_a_care_answer(line, last, memory, own=()):
    """True when the line asks about something the care thread has named, else False.

    `asks_about_the_last_answer` reads one reply, and inside a care thread that reply is a pool
    line: after a scald and "should i cover it" the bot's last word was "Don't put anything on a
    burn - not butter, not cream, not ice. Twenty minutes under cool running water, then a loose
    clean dressing", which never says "blister". So "can i pop the blister" shared nothing with
    it and the blister-plaster entry (padded plaster, short stretches in the shoes) took the
    turn over the burn's own answer - and once that entry had the turn the thread was over, so
    the next line ("how long will it take") was answered by the measles entry's infectious
    period. The answer that opened the thread is the one that names the thing - "a burn that
    blisters or is on the face, hands or joints should be seen" - so both are read, and only
    the care thread's own answer is added: an ordinary conversation is unchanged.
    """
    if asks_about_the_last_answer(line, last, own):
        return True
    answer = _thread_answer(memory or {})
    if not answer or answer == str(last or "").lower():
        return False
    return asks_about_the_last_answer(line, answer, own)


def how_much_of_the_answer_kept(reply, memory):
    """How many of the care thread's own answer words a reply says back, or 0.

    Inside a care thread the person asks about the thing the bot has just answered, and two
    candidates can both be on topic: the composer's continuation, which is drawn from the
    thread's pool, and an entry that matched one word of the line. Which one continues the
    conversation is not a matter of priority - it is a matter of whether the reply is about the
    same thing:

        i burnt my hand on the oven / its a blister now / should i cover it / can i pop the blister
          answers:  "Don't pop it: cover the blister with a padded blister plaster and wear the
                     shoes for short stretches"                     (ten of the burn's words: 3)
          greeting: "Don't pop it. A blister is a sterile dressing of its own; cover it loosely
                     and let it settle"                            (ten of the burn's words: 10)
        ... / should i cover the blister
          answers:  "Cover it with a clean non-fluffy dressing and leave it alone: don't pop it"
                                                                     (3 - and it is the answer)
          greeting: "Keep an eye on it and tell me if anything changes"  (0)

    So the count separates the shoe answer (another person's blister) from the burn's own, and
    it keeps the good entry answer where the composer's pool line says nothing about it. It is a
    reading, not a decision: the arbiter is the one that chooses.
    """
    answer = _thread_answer(memory or {})
    if not answer:
        return 0
    return _words_kept(reply, answer)


# Every line this composer says as an outcome of the advice it gave. Kept together so a reader of
# the bot's own last line can tell the composer's report from an answer: the second question in a
# thread ("is that bad") is about the answer, and the report spoken over it is not the answer.
REPORT_REPLY_LINES = frozenset(
    tuple(TRIED_WORSE_REPLIES) + tuple(TRIED_NO_CHANGE_REPLIES) + tuple(TRIED_NO_CHANGE_ELSEWHERE)
    + tuple(TRIED_HELPED_REPLIES) + tuple(TRIED_HELPED_ELSEWHERE) + tuple(TRIED_IT_REPLIES)
    + tuple(TRIED_SORTED_REPLIES)
)


def is_a_report_reply(said):
    """Whether the bot's own line was one of this composer's readings of a report on its advice.

    The report lines are spoken by whichever module proposes them - `greeting` under the floor, or
    `chat` - so the text decides it rather than the module name, the way `verdict` already reads
    its own verdict lines.
    """
    line = " ".join(str(said or "").lower().replace("\u2019", "'").split())
    return bool(line) and line in _REPORT_LINES_FLAT


def _flat_pools():
    return frozenset(" ".join(str(line).lower().replace("\u2019", "'").split())
                     for line in REPORT_REPLY_LINES)


_REPORT_LINES_FLAT = _flat_pools()
