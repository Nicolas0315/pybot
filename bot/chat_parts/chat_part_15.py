"""Part 15 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import copy
import re

from ..compose import circumstance, doubted, negated, pick
from ..compose.badnews import reads_as_bad_news
from ..compose.goodnews import (
    reads_as_a_pass, reads_as_a_win_nobody_noticed, reads_as_a_prize_in_a_message,
)
from ..compose import loss as loss_reading
from ..compose import said_about_me

from ..memory.topics import in_a_safety_thread as _safety_thread

from ..memory import facts, meant
from ..memory.ack import A_MOVE, a_person_getting_better, nobody_around
from .chat_part_01 import (
    AGE_BEFORE_A_ROLE, COMPARED_ROLE, GROWN_IN, OUT_OF_WORK, PLACE, PLACE_NONE, PLACE_POSITION,
    PLACE_SPAN, RETIRED, RETIRED_ASKING, ROLE, ROLE_STOP, ROLE_TO_PEOPLE, ROLE_WORK,
)
from .chat_part_02 import (
    BAD_NEWS, CAME_BACK, GOOD_NEWS, JUST_DONE, JUST_STARTED, LOST_WEIGHT, MOVING, PET, STATUS, TRIP,
    WISH_LUCK, _a_job_that_went,
)
from .chat_part_04 import (
    REPLIES,
)
from .chat_part_06 import (
    MEANT_LEADS,
)
from .chat_part_07 import (
    _as_said, HEAVY_FEELINGS,
)
from .chat_part_10 import (
    after,
)
from .chat_part_11 import (
    _just_named, _name_said, _numbers, _pet_name, _place_of, _tidy, NOT_A_THING,
)
from .chat_part_12 import (
    _cheer_or_the_question, _night_out, _say, _told_a_trip, _answers_knows,
)
from .chat_part_14 import (
    _own_medical_news, ASKS_A_FIGURE, ASKS_A_PRICE, A_ASKS_WHERE, A_DOES_SOMETHING, A_NEW_CONDITION,
    A_REASSURES, A_REPEAT_FRAME, A_STATE_ASK, A_STATE_WORD, A_VERDICT, A_VERDICT_FILLER,
    A_WHEN_TO_GET_HELP,
)


def _news(clean, tokens, memory):
    """A short, warm reply to small news the user just told us, or None."""
    if clean.endswith("?") or not 1 <= len(tokens) <= 14:
        return None
    # Read before the safety gate, because the chat that makes these lines possible is the one
    # that puts a safety thread on the store: "my nan is in hospital" then "she should be out next
    # week" was answered "I'm listening - say more if it helps", and "shes back at work now" was
    # echoed back. The reader wants the line to say somebody is getting well, so nothing breezy
    # is handed to a line that is still bad news.
    better = a_person_getting_better(clean, memory)
    if better:
        return pick(list(better), memory, seed_text=clean)
    if _safety_thread(memory):
        return None
    # A question is not news however it is written. "do i have a dog" and "have i got a cat" are
    # asked without a question mark, and answering them "A dog - lovely. How old is it?" tells
    # someone they have just announced a pet they were asking about.
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict) and understood.get("kind") == "question":
        return None
    # The words this reader decides on are English words, so it reads the line as it was meant:
    # "im a faliure" and "im a burdon" are judgement nouns the same way "im a failure" is, and
    # the reading has already put the spelling right in `plain`. On the words as typed they were
    # not in ROLE_STOP, so the line was taken for a role being announced and answered
    # "Faliure - good to know. What do you like most about it?" - the chipper reply for news,
    # given to somebody saying this about themselves.
    clean = _as_said(clean, understood)
    # A death is not small news, and it is not a rejection: "i lost my dad" must not be read
    # as "i lost the job" (the BAD_NEWS patterns below take any "i lost"). That line belongs
    # to the composer's loss reading, so this module passes on it.
    if loss_reading.reads_as_loss(clean):
        return None
    # A thing mislaid is not small news either: "i lost my keys" is not "i lost the job", and
    # "give it a day before deciding anything" answers a different line. Its own reader in the
    # composer says where to look, so this module passes on it.
    if loss_reading.lost_thing_to_find(clean):
        return None
    flat = clean.replace("'", "").strip(" .,!;:")
    # Their own hospital, doctor, scan, result or diagnosis, read before the rest: the trip
    # pools refuse every one of those places, so the line otherwise reached the neutral nod.
    # It answers only the visit shapes, so a line about the world is unchanged.
    medical = _own_medical_news(flat, memory, clean)
    if medical:
        return medical
    if WISH_LUCK.search(flat):
        return _say("wish_luck", memory)
    # "im a coeliac", "im a diabetic", "im an asthmatic": a condition said out loud is a fact
    # about the body, not a role to chat about ("Coeliac - good to know. What do you like most
    # about it?"), and the memory lane says it back with what it does with it. ROLE below takes
    # any "im a <noun>", so this has to come first.
    if facts.CONDITION.search(flat):
        return None
    # Retired, before the role and the place: "im 62 and retired" is neither a role to ask a
    # work question about nor a place, and it went to the neutral nod.
    # Announced in passing, the pool is right: "im retired", "i retired in 2019". Asked about,
    # it is not: "i retired last year and feel lost", "i dont know what to do with myself now
    # im retired" and "does retirement feel strange at first" are the question every new
    # retiree brings, and "Retired - how are you filling the days?" is the wrong size for it.
    # The habits table has the shape of that year and what to rebuild, so this pool stands
    # down for any line that carries a trouble word or a question with its retirement.
    if RETIRED.search(flat) and not RETIRED_ASKING.search(flat):
        return _say("retired", memory)
    # Out of work, said plainly, or looking for it: "im between jobs" reached "I'm listening - say
    # more if it helps", which is a line that would fit any message at all.
    if OUT_OF_WORK.search(flat):
        return _say("out_of_work", memory)
    # A standing situation, not a role to chat about: "im a tenant", "im a carer", "im a single
    # parent", "im a student", "im a home owner". ROLE below takes any "im a <noun>", and the
    # job pool asks after it - "Tenant - good to know. What do you like most about it?" is the
    # last thing to ask somebody who has just said they are a tenant. The composer's own reading
    # answers these lines, so this module stands down and lets it (bot/compose/circumstance.py).
    if circumstance.reads_as_situation(flat):
        return None
    # An age in front of the job is still the job: "im 34 and a nurse" was left to the neutral
    # nod. The age is only taken off the line this reader looks at, so the store keeps it.
    # Somebody else's word for the person is not a role they hold: "my sister says im a cow" was
    # read as an "im a <noun>" and answered "Cow - good to know. What do you like most about it?",
    # and the same shape takes every label a parent or a boss uses ("im a nightmare", "im a
    # liability"). A role is what the person says of themselves, so the reading stands down when
    # the "im" is inside what somebody else said, and the judgement is left to the reader that
    # answers being spoken to that way (bot/compose/said_about_me.py).
    if said_about_me.reads_as_somebody_elses_words(flat):
        return None
    role_line = AGE_BEFORE_A_ROLE.sub("im ", flat, count=1)
    match = ROLE_WORK.search(role_line) or ROLE.search(role_line)
    if match:
        # "Nurse tbh - good to know" reads a transcript back at them: the tone words at the end
        # of what they said are not part of the job.
        phrase = facts.no_tone(match.group(1))
        if not phrase:
            return None
        words = phrase.split()
        if not (words and all(w not in ROLE_STOP for w in words)):
            return None
        # "i feel like im a burden to everyone" carries a role at the end of it and is nothing of
        # the kind: what the person compares themselves to is how they feel, and "a burden to
        # everyone" is who they think they are to other people.
        if ROLE_TO_PEOPLE.search(phrase) or (
                COMPARED_ROLE.search(flat) and match.re is ROLE):
            return None
        rest = match.group(2) if match.re.groups > 1 else None
        if rest:
            rest = _place_of(rest)
        if rest:
            phrase = f"{phrase} in {_tidy(rest)}"
            words = phrase.split()
        if len(words) <= 5 and not any(w in {"of", "with", "about", "that", "too", "and"} for w in words):
            return _say("job", memory, x=phrase, X=phrase[:1].upper() + phrase[1:])
        return None
    match = PLACE.search(clean)
    if match:
        said = match.group(1)
        # "i live in leeds not far from the station" is Leeds *and* where it is: the name answers
        # the next question about them, and the words they put with it are said back, because
        # dropping them told the person only where they live and none of what they had just said.
        # The note is read off the whole line, because the place pattern stops a few words in:
        # it says what the person said about the place, in their own words.
        note = facts.qualified_by(clean)
        place = _place_of(facts.TAKE_BACK_SPLIT.split(said, 1)[0] if note else said)
        # A date is not somewhere they have moved to (see PLACE_SPAN): "in six weeks" is when, and
        # there is nothing to say back about it, so the line keeps the plain reply.
        if place and PLACE_SPAN.match(place.strip().lower()):
            place = ""
        # "i grew up in care" is not a place they went to, so there is nothing to ask about it.
        grown = bool(GROWN_IN.search(flat)) and not facts.grown_up_in_a_place(place)
        if note and place and place.lower() not in PLACE_NONE | PLACE_POSITION and not grown:
            return _say("place_near", memory, place=_tidy(place), near=note)
        if place and place.lower() not in PLACE_NONE | PLACE_POSITION and not grown:
            # A move is not "how long have you been there": they are not there yet.
            if MOVING.search(clean):
                return _say("moving", memory, place=_tidy(place))
            return _say("place", memory, place=_tidy(place))
    if TRIP.search(flat):
        return _say("trip", memory)
    kids = facts.kid_count(flat)
    if kids:
        # "i have two kids" is a fact about people, and the number is what the line is about: the
        # store keeps it, so the reply can use it and the ask later can answer from it.
        word = facts.KID_NUMBER_WORDS.get(kids, str(kids))
        kids_word = "kid" if kids == 1 else "kids"
        ages = facts.kid_ages(flat)
        if ages and len(ages) == kids:
            # "my two kids are 4 and 7": the ages are the news as much as the count, so the reply
            # says them back instead of asking for what was just said.
            said_ages = _numbers(ages)
            return _say("kids_aged", memory, x=word + " " + kids_word + ", " + said_ages,
                        X=word[:1].upper() + word[1:] + " " + kids_word + ", " + said_ages)
        return _say("kids", memory, x=word + " " + kids_word,
                    X=word[:1].upper() + word[1:] + " " + kids_word)
    match = PET.search(flat)
    if match:
        pet = match.group(1)
        # "i got a fish bone out myself" is a bone, not a fish: a line that makes the animal the
        # modifier of another noun introduces no pet, so there is no name to ask for.
        after = facts.AFTER_ANIMAL.match(flat[match.end():match.end() + 20].lstrip())
        if not (after and after.group(0).lower() in facts.PET_COMPOUND):
            # A line that names a second, different animal is a pair, not a new pet: "i have a
            # cat and a dog" was answered "A cat - good to know. What's its name?", which drops
            # the dog and asks about half of what they said. The store keeps both and its echo
            # asks the one thing there is to ask about two animals ("do they get on?"), so this
            # reader stands down.
            if not facts.another_animal(flat, pet):
                named = _pet_name(flat, match)
                if named:
                    return _say("pet_named", memory, pet=pet, name=_name_said(named))
                return _say("pet", memory, pet=pet)
        # a compound is another line's news: let the rest of the readers have it
    # "we named him biscuit" names the pet we already know about, so answer to the name. The same
    # goes for the one-word answer to our own question: "we got a puppy" / "What's its name?" /
    # "biscuit".
    # The name can come in lower case, the way most people type: "his name is marmalade" was
    # kept by the store (the possessive in front of "name" is the whole signal there) but read
    # here only when it had a capital, so the reply was the flat "Got it" instead of the name.
    named_pet = _just_named(memory, facts.pet_name_only(flat)
                            or facts.pet_name_only(flat, lower=True)
                            or facts.bare_name(flat))
    if named_pet:
        name = _tidy(named_pet["name"])
        return _say("pet_named", memory, pet=named_pet.get("animal", "pet"),
                    name=_name_said(name))
    if LOST_WEIGHT.search(flat):
        from ..memory import goals as _goals
        planned = _goals.the_loss_that_was_the_plan(flat, memory)
        if planned:
            # "im trying to lose weight" then "i lost 2 kg" was answered with the check for weight
            # coming off by itself: "Was that on purpose, or has it been dropping on its own?"
            # The chat said a turn ago that it was the plan, so the loss is progress and the
            # figure goes back with it. Without a plan on file the check is right and stays.
            return planned
        return _say("lost_weight", memory)
    if _a_job_that_went(flat):
        return _say("lost_job", memory)
    for pattern in BAD_NEWS:
        if pattern.search(flat):
            return _say("bad_news", memory)
    # A good-news pattern is only good news when nothing turns it round: "i didn't win" matches
    # "i won" and is not news. A pass is not a word of its own - "i passed the salt" is not a
    # result - so it is asked of bot/compose/goodnews.py, which wants to know what was passed.
    # News with a silence round it - "i got the job but my sister didnt even text me" - is two
    # things at once and the second is the one that hurts, so the composer answers both halves
    # (WIN_IN_A_SILENCE in bot/compose/fallback.py) rather than congratulating half of it.
    if (not reads_as_bad_news(flat) and not reads_as_a_win_nobody_noticed(flat)
            and not reads_as_a_prize_in_a_message(flat)):
        if reads_as_a_pass(flat):
            return _cheer_or_the_question(flat, memory)
        for pattern in GOOD_NEWS:
            match = pattern.search(flat)
            if match and not negated(flat, match.group(0)) and not doubted(flat):
                return _cheer_or_the_question(flat, memory)
    if STATUS.search(flat):
        return _say("status", memory)
    if re.search(r"\bnothing (on|to watch)\b|\bnothing on (the )?(tv|telly)\b", flat):
        return _say("nothing_on", memory)
    if CAME_BACK.search(flat):
        trip = _told_a_trip(flat, memory)
        if trip:
            return trip
        return _say("came_back", memory)
    trip = _told_a_trip(flat, memory)
    if trip:
        return trip
    night = _night_out(flat, memory)
    if night:
        return night
    if JUST_STARTED.search(flat):
        return _say("just_started", memory)
    if JUST_DONE.search(flat):
        if nobody_around(flat.lower(), memory):
            # "i just moved to a new city and i dont know anyone" is about the hard part of it,
            # and "Nice. What's next?" answers the move while saying nothing to the person.
            return None
        return _say("move_done" if A_MOVE.search(flat) else "just_done", memory)
    return None


def _a_mood_pool_line(said):
    """True when a reply is one of the lines a heavy feeling is answered with.

    A mood pool answers a line that says how the person is; it is not an answer to a question
    about what to do next. "im feeling down today" / "i dont know why" / "can you help" read
    with the topic in front of it reached the sad pool and handed back "That sounds rough ...",
    which is a stock line that fits any message and answers no ask at all.
    """
    flat = _words_only(said)
    if not flat:
        return False
    for kind in HEAVY_FEELINGS:
        for line in REPLIES.get(kind) or ():
            if isinstance(line, str) and _words_only(line) == flat:
                return True
    return False


def _the_verdict_in(clean, memory):
    """The sentence of the answer already on the screen that says whether it is safe, or what to
    do about it. A yes/no follow-up - "is it safe to drive", "is it ruined", "is that too late" -
    asks for a part of the card they were just given, and the card has it in words rather than in
    a figure. A line that asks for a figure is not read here (that is `narrow`'s)."""
    asked = " ".join(str(clean or "").lower().split())
    # The line has to open on the question, the way a yes/no about the thing in hand does: "what
    # colour should i use" holds an auxiliary but is not asking for a verdict, and reading it that
    # way handed back a sentence about drying times.
    if not asked or not EVERY_YES_NO_OPEN.match(asked) or ASKS_A_FIGURE.search(asked):
        return None
    # A line that adds a thing of its own to the one on the table is a question about that thing:
    # "is it safe to drive with a broken spring" holds an auxiliary, but the spring is a second
    # fault beside the exhaust, so the exhaust card is not the answer to it. The shape is the
    # article: a noun after a preposition is a new thing ("with a broken spring", "in the cold"),
    # while the same words as the predicate of the question are the thing itself ("is it a
    # puncture", "is it the cable").
    if A_NEW_CONDITION.search(asked):
        return None
    # A line that asks where a thing can be found asks about the place, not about the thing: "is
    # it on iplayer" after a list of series was answered with the list's own sentence about how
    # gentle the programmes are, over the composer's honest "I can't see what's on iPlayer".
    if A_ASKS_WHERE.search(asked):
        return None
    last = ""
    previous = ""
    for turn in reversed(memory.get("turns") or ()):
        if isinstance(turn, dict):
            if not last and turn.get("bot"):
                last = str(turn["bot"])
            if turn.get("user"):
                previous = " ".join(str(turn["user"]).lower().split())
                break
    if not last.strip():
        return None
    # The same question again is not a follow-up, and a card about the place the ask itself
    # named has nothing in front of it to be carried from.
    if previous and (asked == previous or asked in previous):
        return None
    sentences = [" ".join(one.split()) for one in re.split(r"(?<=[.!?])\s+", last.strip())]
    # The sentence they have just read is not the answer. Handing it back word for word is what
    # this feature got wrong at first: "will it sting me" after a wasp card was handed the card's
    # own opening, "is it a disc" after a back-pain card the prognosis, "is it cancer" after a lump
    # the vet's sentence - each one a line already on the screen, so the person was told again
    # what they could see. The verdict is a sentence further in, and skipping the first of the
    # card leaves the search that answers "is it safe to drive" and "is it a puncture" untouched.
    for said in sentences[1:]:
        if len(said.split()) < 4 or not A_VERDICT.search(said):
            continue
        # The end of a card is when to get help, not the verdict: "is it ok to squeeze a boil" /
        # "should i pop this spot" was handed "See a GP the same day if the redness is spreading"
        # over the card's own "do not squeeze it", because that line holds "get it looked at".
        if A_WHEN_TO_GET_HELP.search(said):
            continue
        return said if said.endswith((".", "!", "?")) else said + "."
    # A price asked is a price asked, whatever words it uses: "is it expensive to fix" is not
    # answered by the method in the card they were given.
    if ASKS_A_PRICE.search(asked):
        return None
    # An echo of what they have already been told is not the thing's own description, and a
    # sentence from it is a repeat with extra words: "should i pay it" after "Everything about
    # the council is in what I said above" handed that line back as the answer.
    if A_REPEAT_FRAME.search(last):
        return None
    # A question about whether a thing is in a state ("is it blocked", "is it dying") is answered
    # by what the card says the thing is. "should i pay it" asks for a decision, which is not a
    # state, and no sentence of the last answer decides it.
    if not A_STATE_ASK.match(asked):
        return None
    # No verdict word in the card, but the question is answered by what the thing usually is:
    # "the shower drain is slow" / "is it blocked" is answered "A slow drain is usually a hair
    # and soap clog in the trap" - the yes is the description itself. Only a sentence that names
    # the thing the line before was about, and only from the first two, because the rest of the
    # paragraph is about other things.
    named = frozenset(word for word in re.findall(r"[a-z']{4,}", previous)
                      if word not in A_VERDICT_FILLER)
    for said in sentences[1:3]:
        if len(said.split()) < 4:
            continue
        # What the thing is, not what to do about it: the first sentence of most cards is the
        # fix, and "is it a fire risk" answered with "Stand it on a hard surface" is the same
        # miss the hedge was. Only a sentence that says what the thing usually is, or whether it
        # matters, answers a state ask.
        if A_DOES_SOMETHING.match(said) or not (A_STATE_WORD.search(said)
                                                or A_REASSURES.search(said)):
            continue
        if named.intersection(re.findall(r"[a-z']{4,}", said.lower())):
            return said if said.endswith((".", "!", "?")) else said + "."
    return None


# The modules that answer a line the bot took nothing from. The fallback hears a line as small
# talk when nothing else finds anything in it, so its name on a turn means the topic's own words
# were never understood, and there is no subject to carry a later ask into.
HEARD_NOTHING = frozenset(("greeting",))


def _nothing_was_heard(memory, topic):
    """True when the line a topic came from was answered by the fallback, so nothing was taken."""
    turns = memory.get("turns")
    records = memory.get("topics")
    if not isinstance(turns, list) or not isinstance(records, list):
        return False
    for record in reversed(records):
        if not isinstance(record, dict):
            continue
        if " ".join(str(record.get("text") or "").lower().split()) != topic:
            continue
        index = record.get("turn")
        if not isinstance(index, int) or not 0 <= index < len(turns):
            return False
        turn = turns[index] if isinstance(turns[index], dict) else {}
        return turn.get("module") in HEARD_NOTHING
    return False


TIME_ASK = re.compile(r"\bhow long\b|\bwhen did\b|\bsince when\b", re.I)


def _asks_what_they_said(said, memory):
    """A reply that asks how long it has been going on when the person has just said.

    The pools are written for a line that has not said yet, and a widened reading puts the
    person's own words back in front of the ask: "ive been like this since about march" plus
    "what should i do" is read as a fresh line, so the pool's question comes back at somebody
    who answered it last turn. `compose.trouble.DURATION` is the same reading of a duration.
    """
    if not TIME_ASK.search(str(said or "")):
        return False
    from ..compose.trouble import DURATION as _DURATION
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for turn in reversed(turns if isinstance(turns, list) else []):
        if not isinstance(turn, dict):
            continue
        line = " ".join(str(turn.get("user") or "").lower().split())
        if line and _DURATION.search(" " + line + " "):
            return True
    return False


TOPIC_WORD = re.compile(r"[a-z]+")


def _the_entrys_own_name(item):
    """The words of a knowledge entry's first key part: what that entry says it is about."""
    key = getattr(item, "key", ()) or ()
    first = key[0] if key else ""
    options = (first,) if isinstance(first, str) else tuple(first or ())
    found = set()
    for option in options:
        for word in str(option).lower().split():
            found.add(word.rstrip("s") or word)
    return found


def _about_the_topic(reading, memory, topic):
    """True unless the widened line lands on an entry that shares nothing with the topic.

    A follow-up is answered from what the *topic* is about, so the entry that answers the
    widened line has to be keyed on a word the topic itself said. Checking the keys of the
    entry rather than its text keeps this independent of every reply's wording.
    """
    from ..knowledge import lookup as _lookup
    from ..understanding import understand as _understand
    item = _lookup.find(_understand(reading, copy.deepcopy(memory)))
    if item is None:
        return True      # not a knowledge entry at all: the line's own reading answered it
    said = {word.rstrip("s") or word for word in TOPIC_WORD.findall(topic)}
    # The topic's *subject* is the thing the line is about; the rest of it says when or where
    # it happened. "i went for a swim before work" carried "how often should i go" into the
    # back-to-work-after-illness entry, because "work" is in both keys and in "before work"
    # - and the answer told a swimmer to stay off while they have a fever. So an entry the
    # topic's subject does not name is a neighbour of the topic, not the topic itself.
    read = _understand(topic, copy.deepcopy(memory))
    subject = read.get("subject")
    named = {word.rstrip("s") or word for word in TOPIC_WORD.findall(str(subject or ""))}
    if _lookup.key_words(item) & named:
        return True
    # The subject read off a plan line can be a word that only qualifies the thing: "im making a
    # birthday cake" is read as being about the birthday, while the entry that answers the length
    # after it is keyed on the cake, so the follow-up was met with a search hedge. The entry's own
    # name for the thing is the second chance, and only when the topic says that word of itself -
    # never a word the ask brought (that is how a neighbour is reached) and never one inside a
    # when-or-where phrase: "work" in "i went for a swim before work" is when it happened, and the
    # entry named "work" is about going back to work after being ill.
    # The thing, though, has to be a thing the topic *names* - one of its people or things - and
    # not any word it happens to share. "i booked the kennels for the dog" says "booked", and the
    # football card is keyed on "booked" as well, so the follow-up "what do you do about that" was
    # answered with the yellow card. "Booked" there is what the person did, not what the chat is
    # about: the kennels are.
    name = _the_entrys_own_name(item)
    things = {word.rstrip("s") or word
              for entity in (read.get("entities") or [])
              if str(entity.get("type") or "") in ("thing", "person")
              for word in TOPIC_WORD.findall(str(entity.get("text") or ""))}
    asked = {word.rstrip("s") or word for word in TOPIC_WORD.findall(reading)} - said
    return bool(name & (things - asked))


# The pools this module says when nobody else speaks: they fit any line, so they answer nothing
# that was actually asked, and a widened follow-up must not settle for one.
NOT_AN_ANSWER = ("intent", "opening", "vague", "busy")


def _says_nothing_about_the_ask(said):
    return any(said in REPLIES[kind] for kind in NOT_AN_ANSWER if kind in REPLIES)


QUESTION_OPEN = re.compile(r"^\W*(?:how|what|which|when|where|who|why)(?:'s|s)?\b")


# A yes/no ask is about the topic only when it is short: "can i freeze it" wants the cake, but
# "would a bit of kitchen roll really help" is an argument about a thing of its own ("kitchen
# roll"), and read with the salad topic in front of it the kitchen-cleaning entry answered it.
# A yes/no a short line opens on, which is the shape the carry reads as a bare ask.
YES_NO_OPEN = re.compile(r"^\W*(?:can|could|would|should)\b")


# Every auxiliary a yes/no opens on, for the verdict rule: "is it safe to drive", "is it ruined",
# "is that too late". Read there rather than in `YES_NO_OPEN`, which decides whether a line is a
# bare ask at all: "is it on iplayer" opened the carry and was answered with the list of series.
EVERY_YES_NO_OPEN = re.compile(r"^\W*(?:can|could|would|should|is|are|was|were|am|do|does|did|"
                               r"will|shall|has|have|isn't|aren't|wasn't|weren't|don't|doesn't|"
                               r"didn't|won't|shan't|can't|cannot|couldn't|wouldn't|shouldn't|"
                               r"must)\b")


YES_NO_WORDS = 5


# A suggestion wearing a question mark: "what about food", "hows about something cold" offers a
# subject of its own ("food", "cold") rather than asking about the one on the table, and read
# with that subject in front the words fight each other - the cold of a dessert offer reached
# the packing-for-a-cold-holiday entry.
OFFERING = re.compile(r"^\W*(?:what|how)s?\s+about\b")


# A line that names a thing of its own is a line of its own. "where are my glasses" after a film
# question is a search for glasses, and read with the film in front of it the cloudy-glasses entry
# answers a search with dishwashing advice: "glasses" is one of its keys. A possessive says the
# thing is the person's own ("my phone", "our car"), and a where-question says the thing it is
# looking for ("where is the remote"), so neither is the thing on the table - no answer above can
# know where it is. A thing the topic itself names is still the topic ("can i freeze the cake"
# after "im baking a cake"), so the check is made against the words of the line being carried.
OWN_THING = re.compile(r"\b(?:my|our|his|her|their)\s+([a-z]{2,})")


LOOKING_FOR = re.compile(r"^\W*where(?:'s|s| is| are| was| were)\b")


FOUND_THING = re.compile(r"\b(?:the|this|that|these|those|your)\s+([a-z]{2,})")


# A question asks about the thing it names with an article: "how much is a passport", "how much
# does a service cost", "how much is a return ticket". Those are the ask's own subject, and the
# line before them is a different one: after "i have a cat" the passport was answered with what a
# kitten costs, and after "im going to london for the weekend" a return ticket was answered with
# the airport transfer. The ask words are not a subject ("how long does it take", "how much would
# that cost"), and a thing the topic itself names is still the topic ("how long does the cake
# take" after "im baking a cake").
AN_ARTICLE = re.compile(r"\b(?:a|an|the)\s+([a-z]{2,})")


# Only a measured ask reads an article as its own subject: how much, how many, how long, how far,
# how old, where, when. "what a shame", "what a nightmare" and "whats a good thing to cook" name
# nothing to look up, and read as an ask about shame, nightmare or good they took the talk away
# from the line that needed it: the grief reply and the job reply both fell to a punt, and a
# vegetarian guest's dinner lost the whole conversation.
ASKS_ABOUT_A_THING = re.compile(
    r"^\W*(?:how\s+(?:much|many|long|far|often|old|big|heavy|tall|warm|cold|deep|high)"
    r"|where(?:'s|s)?|when(?:'s|s)?|what\s+(?:price|size|weight)\b)")


# A container is where the thing is, not the thing: "how much is in a can of coke" is the coke,
# and read as an ask about a can it lost the 35g and got the daily sugar limit instead. The line
# before it is the one that says what is in there.
# An ask for ideas about a named thing is not an ask about the thing on its own: "what can i do
# with a courgette" after "im dairy free" wants the courgette done within the talk's diet, and the
# line read alone has no talk to cook with.
ASKS_WHAT_TO_DO_WITH = re.compile(
    r"^\W*(?:what|how)(?:'s|s)?\s+(?:can|should|shall|do|could|would)\s+(?:i|we|you)\s+"
    r"(?:do|make|cook|have|eat|use)\b")


A_CONTAINER = frozenset("""can cans tin tins packet packets bottle bottles box boxes cup cups
    glass glasses mug mugs slice slices piece pieces portion portions bag bags loaf tin tub jar
    jars carton litre liter pint ounce gram grams kilo handful spoon spoons bowl plate""".split())


def _names_its_own_thing(text, topic=""):
    """True when the line names a thing of its own, which the line being carried does not name.

    "wheres my phone", "where is the remote", "my car is making a noise" are about the thing they
    name; a line that asks how long, how much or why about nothing of its own ("how long does it
    take", "how many lessons will i need") is about the topic, and keeps it.
    """
    clean = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    named = OWN_THING.findall(clean)
    if LOOKING_FOR.match(clean):
        named += [word for word in FOUND_THING.findall(clean) if word not in NOT_A_THING]
    if (not named and ASKS_ABOUT_A_THING.match(clean) and not OFFERING.match(clean)
            and not ASKS_WHAT_TO_DO_WITH.match(clean)):
        # A question's own subject, named after an article. The ask words are left out, so
        # "how long does it take" and "how much would that cost" name nothing. An ask for ideas
        # about a named food keeps the talk around it - "im dairy free" then "what can i do with
        # a courgette" wants the courgette done dairy-free, and read on its own the ask has no
        # talk to cook with, so the carry is what answers it.
        named += [word for word in AN_ARTICLE.findall(clean)
                  if word not in NOT_A_THING and word not in A_CONTAINER]
    if not named:
        return False
    said = set(re.findall(r"[a-z']+", str(topic or "").lower()))
    bare = {word.rstrip("s") for word in said}
    return not any(word in said or word.rstrip("s") in bare for word in named)


def _bare_ask(text):
    """A short question with no subject of its own: the shapes that need the topic.

    "how many lessons will i need", "why is that happening", "how much do they cost" name
    nothing the knowledge base is keyed on, and the words it is keyed on are in the line
    before. A longer line, or one offering a subject of its own, is a line of its own.
    """
    clean = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    words = clean.split()
    if len(words) > 8:
        return False
    if OFFERING.match(clean):
        return False
    if QUESTION_OPEN.match(clean):
        return True
    return bool(YES_NO_OPEN.match(clean)) and len(words) <= YES_NO_WORDS


def _words_only(text):
    """A line reduced to its words, for comparing two of them without the punctuation.

    "Top the pressure up to between 1." is the sentence the person was given in the middle of
    a longer one, and the full stop at the end of the cut kept the comparison from seeing it.
    """
    return " ".join(re.sub(r"[^0-9a-z]+", " ", str(text or "").lower()).split())


# How long a line can be and still say nothing new. "i cant come", "third time", "i cant decide"
# are the lines this stand-down is for; a line with a clause of its own is a new question.
A_SHORT_LINE = 5


# The lead a reply wears when it says itself that it is handing the last answer back. Only the
# text in front of the colon, and only a short one: a card about a bug does not open with a
# sentence of eighty words and a colon.
A_REPEAT_LEAD = re.compile(r"^[^:]{0,80}:\s*")


def _the_same_answer_again(said, memory, line=""):

    """Whether this reply is, word for word, one the bot has just given.

    Not `_said_before`, which also matches a sentence or a piece of a sentence: a card's middle
    line is reused on purpose all through a conversation, and standing down for that would take
    a good answer away. This is the whole reply, and only over the last few turns: a line that
    comes back to the same subject much later has earned the paragraph again.
    """
    # A line that asks for the last answer again is the one ask whose whole reply is that answer
    # again: "what do you mean" and "in english please" want the same sentence, and that is what
    # `bot/memory/meant.py` hands back. Handing it back is the answer to this line, not a module
    # repeating itself, so the stand-down is not for it - without this it was cleared and the
    # person got the fallback's stock line instead.
    if meant.reads_it(line):
        return False
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    # Only a short line. "i cant come" after a card says nothing the card has not answered, and a
    # repeat of it is all this module has; "and the plumber cant come till friday" names a plumber,
    # a day and a wait, and the module that reads a short line in the light of the last one made it
    # "That's a nuisance. Can it happen another time?" - a plumber's visit read as an invitation
    # turned down. The repeat is the poorer answer there and still the one on the subject.
    if len(" ".join(str(line or "").split()).split()) > A_SHORT_LINE:
        return False
    flat = _words_only(said)
    if len(flat.split()) < 12:
        return False
    # A reply that wears a lead saying it is a repeat - "Same answer: <the card again>" - is the
    # card again, and the lead is the only thing that differs. Comparing the part after the lead
    # as well makes the decision the same either way: "my mum wants me to move back home" / "i
    # cant decide" / "how do i choose" stood aside on the second turn and then came back on the
    # third with "Same answer:" in front of the card nobody had answered.
    # A line handed back under the repeat reader's own lead is the answer the person asked to
    # hear again, not the card saying itself twice: the module built it in reply to "sorry, what".
    # Read as the same answer it stood aside, and the person who had just missed a sentence got
    # the search hedge - which is the one thing this guard must never produce. "How do i clean the
    # oven glass" / "sorry, what" was the hedge on main, only because the hand-back is the opening
    # of the paragraph the guard is looking for.
    typed = str(said or "").lower()
    if any(typed.startswith(lead) for lead in MEANT_LEADS):
        return False
    readings = [flat]
    lead = A_REPEAT_LEAD.match(str(said or ""))
    if lead:
        after = _words_only(str(said)[lead.end():])
        if len(after.split()) >= 12:
            readings.append(after)
    for turn in turns[-4:]:
        bot = turn.get("bot") if isinstance(turn, dict) else None
        if not isinstance(bot, str):
            continue
        was = _words_only(bot)
        for reading in readings:
            # The whole of it, and the opening of it: a card handed back without its tail is the
            # same card to the person reading the screen, and that is how the panic answer came
            # back a second time - the first paragraph of it, and nothing else.
            if was == reading or (len(was.split()) > len(reading.split())
                                  and was.startswith(reading)):
                return True
    return False


def _said_before(said, memory):
    """Anything the bot has already said in this conversation is not an answer now.

    Whole replies and the sentences of them: the tomato entry read again with the topic in
    front came back as the first sentence of the paragraph the person had just been given.
    The punctuation is not part of it: a sentence cut short by the sentence splitter ("between
    1.") is still the sentence the person was given ("between 1 and 1.5 bar").
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    said = " ".join(str(said or "").split())
    if not said:
        return True
    flat = _words_only(said)
    if not flat:
        return True
    pieces = [_words_only(piece) for piece in re.split(r"(?<=[.!?])\s+", said)]
    pieces = [piece for piece in pieces if len(piece.split()) >= 4]
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        bot = " ".join(str(turn.get("bot") or "").split())
        if not bot:
            continue
        said_bot = _words_only(bot)
        if not said_bot:
            continue
        if flat == said_bot:
            return True
        if len(said_bot.split()) >= 4 and (flat in said_bot or said_bot in flat):
            return True
        if any(piece in said_bot for piece in pieces):
            return True
    return False


def _says_the_kind(ask, said):
    """Whether the answer carries the kind of figure the ask wanted.

    `how much do they cost` asks for a price, and the driving entry's duration line is not one:
    a confident answer to a different question is worse for the person than the hedge.
    """
    from ..memory.narrow import SPANS as _SPANS, kind_of as _kind_of
    kind = _kind_of(ask)
    if kind is None or kind not in _SPANS:
        return True
    return bool(_SPANS[kind].search(str(said or "")))


# A grumble about a person at work names a behaviour and asks for nothing: "my boss is
# nitpicking everything i do", "my manager keeps having a go at me". The knowledge base answers
# the ones that name a procedure ("my boss keeps changing the rota"), and the fallback pool
# answers the ones said as a verdict on the job ("i hate my job"), so this shape fell between
# the two into "Got it. Is there anything you'd like a hand with?".
WORK_PERSON = re.compile(
    r"\bmy\s+(?:boss|manager|line manager|supervisor|team leader|colleague|coworker|"
    r"co-worker|team)\b", re.I)


WORK_FAULT = re.compile(
    r"\b(?:is|are|was|were|keeps?|kept|has been|have been|always|still)\b[^.!?]{0,24}?"
    r"\b(?:annoying|horrible|awful|difficult|rude|dismissive|unhelpful|unfair|useless|moody|"
    r"snappy|patronising|patronizing|picky|nitpicking|nitpicky|impossible|cold|off with me|"
    r"having a go|on my back|on at me|picking on me|getting at me|watching everything|"
    r"breathing down my neck|finding fault|blaming me|undermining me|ignoring me|"
    r"leaving me out|shouting at me|talking down to me|taking the credit|taking credit)\b",
    re.I)


# The asks stay out of it: "my boss is horrible, what should i say to him" wants the advice
# line, and a question about a person at work is not a grumble to sit with.
WORK_ASK = re.compile(
    r"\?|\b(?:what|how|should|could|can|would|who)\b[^.!?]{0,24}\b(?:i|we)\b",
    re.I)


# "when i ask for help" and "where i work" are not asks, they are the time and place of the
# behaviour: "my supervisor is really dismissive when i ask for help" is the grumble itself.
# The same complaint said about the person rather than about a thing they do: "i feel invisible
# at work", "nobody notices what i do at work". The work has to be named: "i feel invisible" on
# its own is about being alone, not about a job, and it keeps the answer it has.
WORK_UNSEEN = re.compile(
    r"\b(?:feel|feeling|felt)\s+(?:so\s+|really\s+|quite\s+|a bit\s+|like\s+)?"
    r"(?:invisible|unheard|unappreciated|undervalued|ignored|taken for granted|nobody notices me|"
    r"i (?:don'?t|do not|dont) matter)\b"
    r"|\bnobody\s+(?:at work\s+)?(?:ever\s+)?(?:notices|thanks|appreciates|says anything nice "
    r"about)\b[^.!?]{0,20}\b(?:what i do|me|my work)\b",
    re.I)


WORK_CONTEXT = re.compile(
    r"\b(?:at|in)\s+(?:work|the office|the job|my job|my team|the team)\b"
    r"|\bby\s+my\s+(?:boss|manager|team|colleagues?)\b", re.I)


# "nobody notices what i do" carries a "what ... i" that reads as an ask to the pattern above, and
# it is not one: it is the thing nobody notices. The clause comes out before the ask is looked for.
WORK_RELATIVE = re.compile(r"\bwhat i (?:do|did|have done)\b|\bhow i feel\b", re.I)


WORK_GRUMBLE = (
    "That wears a person down, and it is not you being thin-skinned. Has it always been like "
    "this, or is it new?",
    "It is the small ones that grind you down more than any one big thing. What was the last one?",
    "Worth saying it once, plainly, to them rather than about them: what they did, and what you "
    "want instead.",
    "Grin and bear it is the usual advice and it is bad advice. Is there anyone at work you can "
    "say it to?",
)


# The unseen lines get their own answers, because the pool above talks about "them" and a line
# like "nobody notices what i do at work" names nobody to say it to.
WORK_UNSEEN_REPLY = (
    "That wears a person down, and it is not you being thin-skinned. Has it always been like "
    "this, or is it new?",
    "Being the one nobody notices is its own kind of tiring. Is there one person there who would "
    "hear it, if you said it plainly?",
    "Grin and bear it is the usual advice and it is bad advice. Is there anyone at work you can "
    "say it to?",
    "Worth saying once, to the person who should have noticed: what you actually did, and what "
    "you want to be different.",
)


def _work_grumble(clean, tokens, memory):
    """A complaint about a person at work, answered as the grumble it is (or None).

    Only a line that names a behaviour and asks for nothing: the ones that name a procedure
    belong to the knowledge base (`_answers_knows`), and "my boss is fine but the hours are
    awful" is a complaint about the job, which the fallback's own pool answers better.
    """
    if len(tokens) < 4 or " but " in clean or _safety_thread(memory):
        return None
    a_fault = WORK_PERSON.search(clean) and WORK_FAULT.search(clean)
    unseen = WORK_UNSEEN.search(clean) and WORK_CONTEXT.search(clean)
    if not (a_fault or unseen):
        return None
    if WORK_ASK.search(WORK_RELATIVE.sub(" ", clean)):
        return None
    if _answers_knows(clean, memory):
        return None
    return pick(WORK_UNSEEN_REPLY if unseen and not a_fault else WORK_GRUMBLE, memory, clean)


# Laughter the person is reporting, about something they watched, read or were told: "im
# cracking up at this sitcom", "i was in stitches at the stand up", "he had me in stitches",
# "crying laughing at this video", "howling at this group chat", "i nearly died laughing". The
# two laughs this file already knew are the laugh *sound* ("haha", "lol", `LAUGH_WORDS` below)
# and a laugh at the bot's own joke ("laugh" in REPLIES, which takes credit for it); this is the
# third one, where the person laughed at something of their own.
#
# Every arm needs the cue that makes it laughter: "im cracking up" on its own is somebody at
# the end of their tether (`NOT_COPING_SHAPES` says so), and only "cracking up at/over" is the
# laugh. "in bits" is the other way round: "im in bits at that clip" is laughing and "im in
# bits" is grief, so that arm needs its object too.
LAUGH_REPORT = re.compile(
    r"\bcrack(?:ing|ed|s)?\s+(?:me\s+)?up\s+(?:at|over|when|while|watching|reading)\b|"
    r"\bcrack(?:ed|s)\s+me\s+up\b|"
    r"\bin\s+stitches\b|"
    r"\bin\s+bits\s+(?:at|over|watching|reading|when)\b|"
    r"\b(?:crying|died|dying|nearly\s+died|almost\s+died|wet(?:ting)?\s+myself)\s+laughing\b|"
    r"\blaughing\s+(?:so\s+hard|hysterically|uncontrollably|my\s+head\s+off)\b|"
    r"\b(?:can'?t|cant|couldn'?t|could\s+not)\s+stop\s+laughing\b|"
    r"\blost\s+it\s+laughing\b|"
    r"\bhowl(?:ing|ed)\s+(?:at|with)\b|"
    r"\bwheez(?:ing|ed)\s+(?:with\s+laughter|laughing|at)\b")


# A laugh is shared, and that is what tells "we were all cracking up in the meeting" - a report
# of a room laughing - from "im cracking up", which is somebody at the end of their tether
# (`NOT_COPING_SHAPES`). So a group in the line makes "cracking up" the laugh with nothing after
# it, where the arms above want an object ("cracking up at this sitcom"). The tense does the rest
# of the work: a room laughing is told in the past ("were all cracking up", "everyone was
# cracking up"), and "the team is cracking up" is the team going to pieces, so the present is
# left to the not-coping reader. The pressure words are the other way round: a group cracking up
# under the strain is not a room laughing.
LAUGH_TOGETHER = re.compile(
    r"\b(?:we|us|they)\b[^.?!]{0,40}?\b(?:were|was|are|re)\s+(?:all\s+)?crack(?:ing|ed)\s+up\b|"
    r"\b(?:everyone|everybody)\b[^.?!]{0,40}?\b(?:was|were|is|are)?\s*(?:all\s+)?crack(?:ing|ed)\s+up\b|"
    r"\bthe\s+(?:whole\s+)?(?:office|team|class|family|lot|group|pub|house|household|staff|"
    r"crew|year|form)\b[^.?!]{0,40}?\b(?:were|was)\s+(?:all\s+)?crack(?:ing|ed)\s+up\b|"
    r"\bme\s+and\s+(?:my\s+)?\w+\b[^.?!]{0,30}?\b(?:were|was)\s+(?:all\s+)?crack(?:ing|ed)\s+up\b")


LAUGH_TOGETHER_NOT = re.compile(
    r"\b(?:pressure|strain|stress|weight|workload|load)\b")


# The laugh has to be the person's own. "my brother and his mates were cracking up at the park"
# is a story about other people, and their laugh is not news to answer with a warm line about
# the person's evening. "had me in stitches" carries the person in it too.
# The apostrophes are written out because a free one is not free: `we'?re` matched the word
# "were" on its own, and "the kids were in stitches at the show" became the person's own laugh.
LAUGH_MINE = re.compile(r"\b(?:i|im|i'm|ive|i've|we|we're|weve|we've|me)\b")


# Being laughed at is not laughing: "my kids were cracking up at me" is a line about being
# mocked, and "go on, what was it?" would be an answer to the wrong thing.
LAUGH_AT_ME = re.compile(r"\b(?:at|over|about)\s+(?:me|us|my\s+\w+)\b")


# A dog, a fox or the wind howls too, and "howling at the door" is not a joke either.
LAUGH_NOT_A_PERSON = re.compile(
    r"\b(?:dog|dogs|cat|cats|puppy|pup|fox|foxes|wolf|wolves|baby|babies|kid|kids|child|"
    r"toddler|bird|seagull|crow|owl|alarm|kettle|wind|siren|engine)\b")


# A funeral, a ward or a body in the line is not a laugh, whatever else is in it: "my nan is in
# bits at the funeral" is grief said with the same words as laughter.
# "died laughing" and "dying laughing" are the laugh itself, so the death words are not here:
# `reads_as_bad_news` in the body below is what reads a real death, and it knows the difference
# (bot/compose/badnews.py, `_AFTER_IT`).
LAUGH_BAD_SETTING = re.compile(
    r"\b(?:funeral|wake|burial|grave|hospital|ward|hospice|surgery|operation|ambulance|a&e|"
    r"nurse|doctor|vet|terminal|chemo|diagnosis)\b")


def _laughing_at(clean, memory=None):
    """The person saying they laughed at something, or None.

    "im cracking up at this sitcom" used to get the composer's "Thanks for telling me — I'm
    here if you want to dig into any of that", which is the coldest line the bot has for
    somebody sharing a laugh; "i was in stitches" and "he had me in stitches" got "I'm
    listening — say more if it helps"; and "im crying laughing at this video" reached the
    grief pool's "Sorry to hear that. A walk and someone to talk to usually help" because
    "crying" is a sad word. None of the three is a person in trouble.
    """
    if not isinstance(clean, str) or "?" in clean:
        return None
    together = bool(LAUGH_TOGETHER.search(clean)) and not LAUGH_TOGETHER_NOT.search(clean)
    if not LAUGH_REPORT.search(clean) and not together:
        return None
    if LAUGH_AT_ME.search(clean) or LAUGH_BAD_SETTING.search(clean):
        return None
    if not together and not LAUGH_MINE.search(clean):
        return None
    if LAUGH_NOT_A_PERSON.search(clean) and re.search(r"\bhowl", clean):
        # The animal guard is for the howling arm only: "my cat fell off the sofa and i nearly
        # died laughing" is a cat in the line and a person laughing in it too.
        return None
    if reads_as_bad_news(clean):
        return None
    if isinstance(memory, dict):
        # The laugh is not over when the report is: the next line is often the same laugh carried
        # on ("i couldnt breathe", "my sides hurt"). The number of turns is written with it, so
        # the reader below only answers the very next line and not any later "im dead".
        memory["laughed"] = len(memory.get("turns") or [])
    return "laughing"


def _the_condolence_is_the_last_thing(memory):
    """True when the turn before this nod was the condolence, or the room the nod before got.

    "mm" and "ok" answer whatever was said last. After a death they are the person taking it in,
    and the pool for a grief thread answers them with room to say more. After the egg timer they
    are a nod about eggs: a chat that moved on is not a chat about the death, and the condolence
    has to be the last thing said for the nod to be about it.
    """
    if not isinstance(memory, dict):
        return False
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    last = turns[-1]
    if str(last.get("module") or "") in ("loss", "grief"):
        return True
    if " ".join(str(last.get("bot") or "").split()) in loss_reading.AFTER_REPLIES:
        return True  # the nod before this one was already answered with room
    return bool(loss_reading.reads_as_loss(str(last.get("user") or "")))


# The same laugh, carried on in the next line. Read only when the turn before was answered by
# the laugh pool (`memory["laughed"]`), because "i couldnt breathe" on its own is a person in
# trouble and that answer must never be taken away by a laugh that happened earlier in the chat.
LAUGH_CARRIED_ON = re.compile(
    r"\b(?:couldn'?t|could\s+not|can'?t|cant)\s+(?:breathe|breathe\s+properly)\b|"
    # "stop" only ever as "stop laughing": "i cant stop" on its own is a person at the end of
    # their tether, and "i cant stop crying" is a hard night that reads as a laugh otherwise.
    r"\b(?:couldn'?t|could\s+not|can'?t|cant)\s+(?:stop\s+laughing|stop\s+it|keep\s+a\s+straight\s+face)\b|"
    r"\b(?:sides?|ribs?|face|cheeks?)\s+(?:hurt|ache|aching|are\s+sore)\b|"
    r"\bmy\s+(?:sides?|ribs?|face|cheeks?)\b|"
    r"\b(?:still|proper)\s+laughing\b|\bstill\s+going\b|"
    r"\b(?:nearly|almost)\s+choked\b|\bim\s+dead\b|\bim\s+gone\b|"
    r"\bim\s+(?:still\s+)?crying\s+(?:with|from)\s+(?:the\s+)?laugh\w*\b|"
    r"\b(?:laughed|giggled)\s+until\s+i\s+cried\b|\bcried\s+laughing\b")


# ...and the lines that are somebody having a bad time, which must never be read as a laugh.
# `reads_as_bad_news` knows grief and illness but not tears for their own sake.
LAUGH_CARRIED_ON_NOT = re.compile(
    r"\bcry(?:ing|cried)?\b|\btears\b|\bsob(?:bing|bed)?\b|\bwept\b|"
    r"\bupset\b|\bsad\b|\bscared\b|\bafraid\b|\bpanick\w*\b|\banxious\b|"
    r"\ball\s+night\b")


LAUGH_CARRIED_ON_REPLY = (
    "Ha, that good? I hope the ribs recover.",
    "That is a proper laugh when it gets your ribs.",
    "Ha - worth it. That is the kind of thing you tell people about.",
)


def _laughing_still(clean, memory):
    """The next line is the same laugh carried on, or None."""
    if not isinstance(memory, dict):
        return None
    was = memory.get("laughed")
    if not isinstance(was, int) or isinstance(was, bool):
        return None
    if len(memory.get("turns") or []) != was + 1:
        return None
    if not isinstance(clean, str) or "?" in clean or not LAUGH_CARRIED_ON.search(clean):
        return None
    if (reads_as_bad_news(clean) or LAUGH_BAD_SETTING.search(clean)
            or LAUGH_CARRIED_ON_NOT.search(clean)):
        return None
    return pick(LAUGH_CARRIED_ON_REPLY, memory, clean)


# Somebody else's opinion about the person's life is a shape and not a subject: who said it, and
# that they said the person should do something. "my sister thinks i should get a lodger" and "my
# mum thinks i should move back home" are the same line to this reading, which is why the replies
# name the person and never the suggested action: a phrase that fits "whether you ..." ("get a
# lodger") does not fit it after "be" ("be grateful for what i have"), and a reply built out of it
# read as broken English. A question is left alone ("should i get a lodger" is its own ask), and
# so is anything the suggested action makes a health matter - "my mum thinks i should get it
# checked" wants the health answer, not a line about whose decision it is.
SOMEBODY_THINKS = re.compile(
    r"\b(?:my|our|the)\s+(?P<who>[a-z]+)\s+"
    r"(?:thinks|says|reckons|insists|keeps\s+saying)\s+(?:that\s+)?"
    r"(?:i|we)\s+(?:should|ought\s+to|need\s+to|have\s+to|must)\s+(?P<named>[a-z][a-z' ]{2,70})"
    r"[.!,]*$", re.I)


EVERYONE_THINKS = re.compile(
    r"\b(?P<who>everyone|everybody|people|my\s+mates|my\s+family)\s+"
    r"(?:keeps?\s+)?(?:tells?\s+me|telling\s+me|says?)\s+(?:that\s+)?"
    r"(?:i|we)\s+(?:should|ought\s+to|need\s+to|have\s+to)\s+(?P<named>[a-z][a-z' ]{2,70})"
    r"[.!,]*$", re.I)


THEIR_OPINION_IS_A_HEALTH_MATTER = re.compile(
    r"\b(?:doctor|gp|nurse|hospital|a&e|casualty|999|111|ambulance|checked|check\s+it|scanned|"
    r"scan|tested|test|operation|surgery|tablet|tablets|medicine|meds|medication|pill|pills|"
    r"diet|weight|smoking|smoke|drink|drinking|alcohol|counselling|therapist|antidepressants)\b",
    re.I)


# None of these tells the person what to feel, explains anybody's behaviour away, or ends on a
# question they did not ask: what a friend does with a suggestion about your life is put the
# decision back in your hands.
THINKS_REPLIES = (
    "That is {who}'s idea for your life, not a decision you have made. It is your call, and no "
    "is a whole answer.",
    "Easy advice to give from outside. You are the one who would live with it, so decide it on "
    "what you want.",
    "You can hear {who} out and still not do it. What matters is what you want, not what sounds "
    "sensible to them.",
    "It is your life and your call. {who_cap} thinking it does not make it a plan.",
    "Nobody else has to live with it. Take the thought seriously if it helps and drop it if it "
    "does not - either way it is yours to decide.",
)


def _somebody_thinks_i_should(clean):
    """Who thinks what the person should do, for a line that reports somebody's opinion.

    Returns (who, named) or None. The named action is not put in the reply (see above); it is what
    tells a suggestion apart from a report, and its length is what stops a long clause being read
    as one.
    """
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text or len(text.split()) > 26:
        return None
    found = SOMEBODY_THINKS.search(text) or EVERYONE_THINKS.search(text)
    if not found:
        return None
    who = " ".join(found.group("who").split())
    named = " ".join(found.group("named").split()).strip(" .,!")
    if not named or len(named.split()) > 10:
        return None
    if THEIR_OPINION_IS_A_HEALTH_MATTER.search(text):
        return None
    return who, named
