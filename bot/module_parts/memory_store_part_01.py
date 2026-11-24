"""Part 1 of 4 of a large module, split out of `memory_store`.

Everything here is re-exported from `memory_store`, so callers import it from there as before.
"""
import re

from ..compose import pick
from ..memory import forget, name, others, remember, remember_other, stem, user
from ..memory import ack
from ..memory import change as a_change
from ..memory.filler import without_the_end_shrug
from ..memory import facts as extract
from ..memory import hours as hours_after
from ..memory import repair as a_repair


from ..memory.store_lines import _FACT_SLOT, CONCEPTS
from ..memory.enough import enough_reply



# The reader's own tests call it through this module, and so does anything written against the
# store before the move: the three names it reaches for are kept here, pointing at the one copy.
_enough_reply = enough_reply


from ..memory.relations import (_PET_WORD, _animal_family, _canon_relation, _folded, _named_person,  # noqa: F401
                                _person_from_pronoun, _pronoun_fits)


from ..modules.memory_tables import (ASK_WITHOUT_MY, DAY_IT, DAY_THING, HOW_MANY_OF_MINE, PLAN_MINE,  # noqa: F401
                            TIME_ASKS, TIME_IT, TIME_THING, TOPIC_ASK, WHERE_PLAN)


# People ask to be reminded in their own words, and the reminder is not part of the ask:
# "remind me what I'm allergic to", "my name again?", "sorry, what was my budget". Take the
# wrapper off before matching, so one pattern in the plain form serves every phrasing. The
# chat-speak an ask arrives in ("whats", "im") is folded the same way.
# A line that asks to be reminded of something states nothing to keep. "remind me when i am
# going to rome" names Rome, and the plan reader took the name for a plan of its own, so the
# store filed "Rome" and then answered a later question from it. Only the asking words are
# listed: "remind me to ring the dentist" does state something, and it keeps being kept.
REMIND_QUESTION = re.compile(
    r"\bremind me\b[^.!?]{0,24}\b(?:what|when|where|who|whom|whose|how|which|why|if)\b|"
    r"\bremind me\b(?:[\s,]*(?:again|please))*[\s,]*$", re.I)


# "What was I making?" asks about the line they said out loud, not the newest one: a detail about
# it ("hes allergic to nuts") keeps the subject, and a statement about something else ends it.
# "What am I doing wrong?" is a question about the thing itself, not a recall: the ask has to end
# where the plan is named, so a word of complaint after it keeps the line for the module that
# answers it.
# The asks that want the list of plans rather than the line they said: "what am i planning" is
# about what is coming up, "what am i doing" is about the thing in their hands.
# The asks about what they are up to that name neither a plan nor an activity: "what am i up to?"
# is about what is coming up when the line before it said something coming up, and about the
# thing in their hands when that line said what they are doing. "what was i cooking?" is not one
# of these - it names the cooking, and the line about the cooking answers it - and neither is
# "what am i doing?", which is about the thing in their hands.
# A reply that is not a fact: the honest "you have not told me" and the guesses. The store says
# one when it has nothing to say back, so a line answered that way is not a fact of theirs.
NOT_A_FACT = re.compile(r"\bhaven't (?:told|said|mentioned|given|got)\b|\bhaven't your\b"
                        r"|\bdon't know\b|\bnot sure\b|\bnothing comes to mind\b"
                        r"|\bdidn't say\b|\bnever told\b|\bno idea\b", re.I)


def _their_own_line_ask(text, memory):
    """True on the one ask the store must win even against a topic entry: their own line back.

    "what was my plan?" is read as the topic the plan is about ("what paint should i use for a
    hallway?" then "what was my plan?" was answered by the money entry), and the store's own plan
    line is the answer.

    "what was i cooking?" is read as a cooking line, and the cooking entry answers a different
    question - a chilli recipe for a chilli they had already told us they were making, and the
    recipe's timings for "how long does that take" after it. The person asked what they said,
    not what to do. The store answers only from a line they really said, so this is said for
    exactly the asks whose answer is that line, and every other line the store proposes on is
    left to the arbiter's own rules.
    """
    try:
        low = _bare(text) or ""
        if PLAN_MINE.search(low):
            return bool((user(memory) or {}).get("plans") or (user(memory) or {}).get("plan"))
        if not ACTIVITY_ASK.search(low):
            return False
        return bool(_activity_line(memory))
    except Exception:  # noqa: BLE001 - a hook that raises must not lose the turn
        return False


# What the repaired line may fill in, and what it may not. The list used to be of keys it could
# fill, which meant every fact added later was invisible to it: "my birfday is the 3rd of may" was
# repaired to "my birthday is the 3rd of may" by the understanding engine, read as the typed line
# by the store, filed as a plan, and then denied a line later ("you haven't told me your birthday
# yet"). So it is the other way round: the repair may fill any fact, and the keys it may not are
# the ones that are not facts about the world but about what the line is doing - a plan is the
# line said back in their own words, and a take-back is read off the word as typed.
NOT_FROM_THE_REPAIR = frozenset("""plan plans drop retract correction""".split())


def _with_repaired(found, text, memory, kind):
    """The facts the understanding engine's own repairs make plain.

    The store read the line as it was typed, so a word the engine had already repaired hid the
    fact from it: "im alergic to peanuts" filed nothing at all, and "im alergic to peanits" filed
    a food called "peanits". The repaired line is read as well, and a fact is taken from it only
    where the typed line gave nothing for that key - so this can add what a typo hid, and cannot
    overwrite what they actually said.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    plain = understood.get("plain") if isinstance(understood, dict) else None
    if not isinstance(plain, str) or not plain.strip():
        return found
    if plain == " ".join(str(text).split()):
        return found  # nothing was repaired, so there is nothing new to read
    more = extract.extract(plain, question=(kind == "question")) or {}
    for key, value in more.items():
        if key not in NOT_FROM_THE_REPAIR and not found.get(key) and value:
            found[key] = value
    # A list of facts about other people is not one fact. The typed line can name the person and
    # one thing about them while the repair is what makes the other plain: "my mums 70 n she
    # loves gardning" reads the hobby as typed, and the age only once it is repaired. Taking the
    # repaired list only when the typed one was empty threw the age away because the hobby was
    # there, so the person is merged key by key instead.
    if found.get("others") and more.get("others"):
        for entry in more["others"]:
            if not isinstance(entry, dict) or not entry.get("who"):
                continue
            known = next((one for one in found["others"]
                          if isinstance(one, dict) and one.get("who") == entry["who"]), None)
            if known is None:
                found["others"].append(dict(entry))
                continue
            for key, value in entry.items():
                if key != "who" and not known.get(key):
                    known[key] = value
    return found


# The words that make a place word a common noun instead: "a bath and an early night" is a bath,
# and a person who lives in Bath does not want it handed back as the city.
NOT_A_NAME_BEFORE = re.compile(r"(?:\b(?:a|an|the|some|another|his|her|their|our|your|my)\s+)$",
                               re.I)


# One word deep is not enough to tell the city of Bath from a hot one. Bath, Reading, Nice, Sale,
# Deal and Wells are all answers to "where do you live", so the town comes back in store replies
# that are about something else: "You're planning a hot Bath tonight", "Everything is on Sale",
# "Start Reading for twenty minutes". Only the place that reads as a place is written - where a
# name is normally said: after a preposition or a travel word, with the number in chat-speak
# ("going 2 spain") allowed between, or where a name is at the front of a sentence.
THE_PLACE_IS_NAMED = re.compile(
    r"(?:^|[.!?;:]\s+|\n|\b(?:to|in|into|from|at|near|of|around|through|toward|towards|via|"
    r"going|coming|off|back|flying|travelling|traveling|moving|heading|headed|staying|visiting|"
    r"visit|bound|left)\s*(?:\d+|two|three|four|five|six|seven|eight|nine|ten)?\s*)$", re.I)


def _the_places_are_written_as_names(reply, memory):
    """A place the store holds is written the way the store holds it.

    A plan is kept and quoted in the words they typed, which is right for the plan and wrong for
    the name in it: "we r going 2 spain in may" came back as "You r going 2 spain in may.", and
    "im going to lisbon in may" as "You're going to lisbon in may." The line that named the place
    told the store the name ("Spain", "Lisbon"), so the reply is written with it. Only a place the
    store is holding is touched, and a determiner in front of the word says it is a common noun,
    not a place: "You're planning a bath and an early night" is not the city of Bath.
    """
    known = user(memory)
    if not isinstance(known, dict) or not isinstance(reply, str) or not reply.strip():
        return reply
    names = [name for name in (known.get("places") or []) if isinstance(name, str) and name.strip()]
    city = known.get("city")
    if isinstance(city, str) and city.strip() and city not in names:
        names.append(city)
    if not names:
        return reply
    out = reply
    for name in names:
        pattern = re.compile(r"(?<![\w'])" + re.escape(name) + r"(?![\w'])", re.I)

        def swap(match, name=name):
            before = match.string[max(0, match.start() - 28):match.start()]
            if NOT_A_NAME_BEFORE.search(before):
                return match.group(0)
            if not THE_PLACE_IS_NAMED.search(before):
                return match.group(0)
            return name

        out = pattern.sub(swap, out)
    return out


def note_the_hours(text, memory):
    """Keep the kind of week the line names, for the follow-up on the next turn.

    The reading is bot/memory/ack.py's (`_hours_family`), so the six shapes are written down in
    one place: a night shift, an early start, a late finish, long shifts, a rota that moves, and
    working from home. Asked here rather than in the reply, because the hours are often answered
    by a knowledge entry that never reaches the ack module, and the following line - "does that
    get easier", "i never know when to stop" - is the same follow-up however it was answered.
    """
    if not isinstance(text, str) or not text.strip():
        return
    # The week has to be theirs. "my son wakes at five" is his morning, and "i work nights, my
    # back is killing me" is a line about the back: the understanding engine reads that one as
    # health and the son's morning as family, while the lines this is for read work, or read no
    # topic at all ("i start at six so im up at five").
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict):
        topic = understood.get("topic")
        if topic and topic != "work":
            return
    try:
        from ..memory import ack
        family, _pool = ack._hours_family(text.lower())
    except Exception:  # a reading that cannot run must not cost the store the turn
        return
    if family:
        hours_after.note(memory, family)


def _a_detail_does_not_replace_the_job(found, memory):
    """A line that only says when or where they work keeps the job they already gave.

    "im a nurse" then "i work nights" put "nights" in the store as their job and dropped the
    nurse, so "and my job?" answered "You work nights" and the one fact they had given was gone.
    A shift is a detail of the work, and a detail does not take the place of the fact.

    The same for where they work: "im a teacher" then "i work in a school" said back "You work in
    a school" and the teacher was gone, so "what do you know about me" lost the role altogether.
    A place is a detail beside the role, and the summary now says both.
    """
    if "job" not in found:
        return found
    held = (user(memory) or {}).get("job")
    held_frame = str((user(memory) or {}).get("job_frame") or "")
    said = found.get("job")
    if not held or not said or str(held) == str(said):
        return found
    said_frame = str(found.get("job_frame") or "")
    said_weight = extract.work_weight(said, said_frame)
    if said_weight < extract.work_weight(held, held_frame):
        kept = dict(found)
        kept.pop("job", None)
        # The frame belongs to the job it was said with: keeping "work" beside the nurse they
        # already told us would say "you work nurse".
        kept.pop("job_frame", None)
        # It is still something they told us, so it is kept as what it is - when or where they
        # work, beside the job - rather than thrown away: memory then says both ("you're a
        # nurse; you work nights", "you're a teacher; you work in a school") instead of one of
        # the two going missing.
        if said_weight == 2:
            kept["workplace"] = (said_frame + " " + str(said)).strip()
        else:
            kept["shift"] = said
        return kept
    if extract.is_a_place_of_work(held_frame) and found.get("job_frame") is None:
        # The role is said second: "i work in a school" then "im a teacher". The school stays
        # beside it as where they work, rather than being overwritten by the role.
        if not (user(memory) or {}).get("workplace"):
            found["workplace"] = (held_frame + " " + str(held)).strip()
    if "job_frame" not in found:
        # A role said on its own is "you're a nurse", never "you work nurse": the frame belongs to
        # the line it was said with ("i work nights"), and left in the store it carries over.
        (user(memory) or {}).pop("job_frame", None)
    return found


# The words a question opens with. A line that opens with one of them, or carries a question mark,
# is an ask, and an ask is where a shrug on the end is dropped.
ASK_OPENERS = frozenset("""what whats which when where who whose why how hows
do does did is are was were am can could should would will shall have has had
any anyone anything""".split())


def _without_the_shrug_at_the_end(text):
    """The line without the chat-speak hung on the end of it, when that leaves words behind.

    `bot/memory/filler` holds the shrugs people put on the end of a line, and everything the store
    says back reads a line through it. What the store *files* did not, so the shrug became part of
    the thing told: "how old is my son by the way" reached no reader at all and was answered with
    the search hedge, and "when do we go to cornwall by the way" filed a place called "cornwall
    bies the way" and said it back: "You go to cornwall bies the way in August."
    """
    said = " ".join(str(text or "").split())
    words = said.lower().strip(" .,!;:").split()
    if "?" not in said and not (words and words[0] in ASK_OPENERS):
        # The shrug is dropped from an ask, and from an ask only. "i meant 43 actually" is a
        # correction, and the word on the end of it is part of how it reads: with the shrug gone
        # the correction went to the greeting and the line "43 - got it, 43 it is" was lost.
        return said
    clean = without_the_end_shrug(said)
    return clean if clean and clean != said else said


def after(text, reply, memory):
    """Keep a correction the chat was given, whichever module gave the reply to it.

    "how long does a chicken take to roast" / "i meant a turkey" reads right on the turn that says
    it - the turkey row answers the correction by itself - and the chat was still on the chicken:
    asked "what about a duck" the next line reached no row at all and got a search hedge. Whether
    the bookkeeping happened used to depend on which module won the turn, because each module
    replies to its own copy of the memory and only the winner's copy is kept. The correction is
    the chat's, not the reply's, so it happens here, once, after the reply has been chosen.
    """
    try:
        a_repair.keep_the_correction(text, memory)
    except Exception:  # noqa: BLE001 - the store never crashes a turn
        pass


# The ages in words, for saying a group of children back the way the store says them elsewhere
# ("Two kids, four and six").
AGES_IN_WORDS = {int(number): word for word, number in extract.FIGURE_WORDS.items()}


def _the_ages_of_the_children(text, memory):
    """The reply for the ages of the children the store counts, given one at a time, or "".

    "i have two kids" then "ones 7 and ones 4": the second line names no group word, so every
    reader for a group passes it on, the store kept nothing, and the composer handed the line back
    ("Got it - ones 7 and ones 4."). The ages are the answer to "how old are they?", so they are
    kept and said as ages. A bare list of figures is read only when the line before counted the
    children, because "7 and 4" on its own could be anything.
    """
    if not isinstance(memory, dict):
        return ""
    held = user(memory).get("kids")
    if not isinstance(held, int) or held < 2:
        return ""
    # Ages already on the group are a correction, and `matters.a_corrected_age` reads those: a
    # second full list here would overwrite the ages one at a time.
    if any(len(entry.get("ages") or ()) > 1
           for entry in others(memory) if isinstance(entry, dict)):
        return ""
    ages = extract.ages_said_one_by_one(text, held)
    if not ages:
        return ""
    if not (extract.the_ones_are_given_one_at_a_time(text) or _the_count_was_the_line_before(memory)):
        return ""
    remember_other(memory, {"who": "kids", "ages": ages}, text)
    # Said in the order the person gave them: "ones 7 and ones 4" is seven and four, and the store
    # keeps that order everywhere else.
    words = [AGES_IN_WORDS.get(age, str(age)) for age in ages]
    said = ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 2 else " and ".join(words)
    return pick(["{} — got it.".format(said[:1].upper() + said[1:]),
                 "Got it — {}.".format(said),
                 "{}.".format(said[:1].upper() + said[1:])], memory)


def _the_count_was_the_line_before(memory):
    """Whether the line before this one counted the children, so a bare list of ages is theirs."""
    said = str((memory.get("topic") or {}).get("text") or "")
    return bool(re.search(r"\b(?:kids?|children|child)\b", said, re.I))


def _the_pets_on_record(memory):
    """The (animal, name) pairs the store holds, for comparing one turn with the next."""
    held = set()
    if not isinstance(memory, dict):
        return held
    for pet in user(memory).get("pets") or ():
        if not isinstance(pet, dict):
            continue
        held.add((str(pet.get("animal") or "").strip().lower(),
                  str(pet.get("name") or "").strip().lower()))
    return held


def _note_a_pet_that_is_new(text, memory, before):
    """A line that leaves two of an animal on record is answered as a line about the two.

    Nothing is read out of the words: the store is compared with itself, so a phrasing nobody
    wrote a rule for is answered the same as the ones people type most. A first pet is left
    alone - bot/memory/ack.py already answers the line that gives one ("A cat called Milo.
    What's it like to live with?") - and so is a rename, which leaves one animal behind.
    """
    if not isinstance(memory, dict):
        return None
    held = memory.get("correction")
    if isinstance(held, dict) and held.get("said") == " ".join(str(text or "").lower().split()):
        return None  # the line has already been read as a correction, and that is its answer
    added = _the_pets_on_record(memory) - before
    pets = [pet for pet in (user(memory).get("pets") or ()) if isinstance(pet, dict)]
    for animal, name in sorted(added):
        if not animal or not name:
            continue
        same = [pet for pet in pets
                if str(pet.get("animal") or "").strip().lower() == animal and pet.get("name")]
        if len(same) < 2:
            continue
        memory["correction"] = {"key": "pets_more", "value": name, "animal": animal,
                                "said": " ".join(str(text or "").lower().split()),
                                "text": text}
        return memory["correction"]
    return None


def _a_trip_booked_named(text, memory):
    """A trip that is already booked is a trip the chat is on, and the store keeps it.

    "we booked a cottage in cornwall for august" was answered about Cornwall and then kept
    nothing: "where are we going" said "You haven't said - where are you going?", and a correction
    after it had no plan to land on. The place is filed, and the plan in the shape the other trips
    are kept in ("Cornwall in August"), unless the store is already on that plan.
    """
    from ..memory import trips
    place, when = trips.the_trip_they_booked(text)
    if not place:
        return
    known = user(memory)
    if not isinstance(known, dict):
        return
    place = place[:1].upper() + place[1:]
    plan = " ".join(f"{place} in {when}".split()) if when else place
    places = [str(one) for one in known.get("places") or [] if str(one).strip()]
    if place.lower() not in {one.lower() for one in places}:
        remember(memory, "places", place, text)
    if str(known.get("plan") or "").strip().lower() != plan.lower():
        # The plan is the last thing the line states, the way a trip said as a plan keeps it, so a
        # correction after the booking moves the trip rather than the place on its own.
        remember(memory, "plan", plan, text)
        remember(memory, "plans", plan, text)


def _this_line_put_something_right(memory, text):
    """Whether this very line is the correction one of the readers has just applied."""
    said = " ".join(str(text or "").lower().split())
    if not said:
        return False
    for key in ("correction", "name_fixed"):
        kept = memory.get(key)
        if isinstance(kept, dict) and said == " ".join(str(kept.get("said") or "").split()):
            return True
    return False


def _on_record_before(memory, records):
    """The animals an earlier line put on record, out of the ones this line has just taken back.

    A take-back only says itself when there was something to take back. "i dont have a rabbit"
    from someone who has a cat is a thing they never had, and "Right \u2014 no rabbit, then."
    answers a line they did not say; the ordinary answer to it is the one they get.
    """
    said = " ".join(str((turn or {}).get("user") or "").lower()
                    for turn in (memory.get("turns") or []) if isinstance(turn, dict))
    words = {stem(word) for word in re.findall(r"[a-z']+", said)}
    kept = []
    for record in records or []:
        if not isinstance(record, dict):
            continue
        for word in (record.get("animal"), record.get("name")):
            if word and stem(str(word).lower()) in words:
                kept.append(record)
                break
    return kept


# An ask that names one of their own facts and wants it back: "what are my cats called",
# "and where do i work", "what was my budget again". The fact is named as theirs, with the
# copula or the first-person ask around it, and nothing else in between: "how do i budget" and
# "why do we get allergies" are questions about the world and the store has nothing to say to
# them, while "what should i do about my job" is advice, not a read of the store.
NAMED_FACT_ASK = re.compile(
    r"\bwhat(?:'s|s| is| are| was| were)?\s+my\s+" + _FACT_SLOT + r"\b|"
    r"\bwhat\s+(?:is|are|was|were)\s+my\s+" + _FACT_SLOT + r"\b|"
    r"\bwhere do i (?:work|live|come from)\b(?=\s*(?:[?.!,;:]|$)|\s+(?:now|again|then|at|from|"
    r"these|days|properly|though|honestly|anymore|either|oh|wait|sorry|hmm|actually|um|right|"
    r"please|thanks)\b)|\bwhat do i work as\b|\bwho am i\b|"
    r"\bhow old am i\b|\bwhat do i do for a living\b", re.IGNORECASE)


# An ask about someone else, put as a question: "is she vegetarian", "does she eat meat", "what
# does my mother in law eat", "what is she allergic to". The line has to open as a question or ask
# what they eat; "what can i cook for my vegetarian mother in law" is a request for a dish, and the
# word vegetarian in it is not the person's diet being asked about.
ASK_ABOUT_THEM = re.compile(
    r"^\W*(?:is|are|does|do|did|was|were|can|could|has|have|will)\b|"
    r"\bwhat (?:does|do|did|can|could|is|are|was|were) "
    r"(?:he|she|they|your|my|his|her|their)\b|"
    r"\bwhat(?:'s|s| is| are)\s+(?:my|his|her|their|he|she|they)\b", re.I)


# "what is my mum allergic to?" carries the word the allergy entry knows, and the entry answered
# with what an allergy is - the one thing the person did not ask - while the store held "your mum
# is allergic to shellfish". The line is a read of a fact the store keeps about a person, so the
# store takes it; a line that asks for advice instead ("can he eat cake", "what should my son
# eat") is still the entry's, and so is a question about allergies in general.
PERSON_ADVICE_ASK = re.compile(
    r"^\W*(?:can|could|should|shall|would|will|may|might|is it (?:ok|okay|fine|safe)|"
    r"what can|what could|what should|how (?:do|can|should)|any (?:tips|ideas|advice|"
    r"suggestions|ways))\b", re.I)


# "sorry, his name is milo", "no, its luna", "actually his name is milo not max": the opener is
# what says the name on record is the wrong one.
CORRECTS_A_NAME = re.compile(r"^\W*(?:(?:no|nope|sorry|actually|oops|wait|hold on|correction)"
                             r"[,.]?\s+)", re.I)


# The correcting word inside the possessive instead of in front of it: "his names actually rocky"
# is "his name's actually rocky" typed without the apostrophe, and it opens with no "no"/"sorry",
# so the rename above never saw it and the store kept Rex while the reply handed the line back.
CORRECTS_A_NAME_POSSESSIVE = re.compile(
    r"^\W*(?:his|her|its|their)\s+names?\s+(?:actually|really)\s+", re.I)


# "fred is 5", "biscuit was 12", "milly is 3 years old": a line that names no animal, only the
# name the store has for one, and gives a figure for it.
# An age is typed as a figure or as a word, and people type "hes two" as often as "hes 2": the
# two are the same figure, so every age reader below takes either. Without the words, an age said
# out loud went nowhere and the store answered "how old is your dog" with "You haven't told me"
# about the age it had just been given.
AGE_IN_WORDS = "|".join(sorted(extract.FIGURE_WORDS, key=len, reverse=True))


PET_NAME_AGE = re.compile(r"^\W*(?:[a-z][a-z'-]{2,20})\s+(?:is|was|are|were)\s+"
                          r"(?P<age>\d{1,2}|" + AGE_IN_WORDS + r")(?![\d.,]\d)(?!\s+of\b)"
                          r"(?!\s*(?:kg|kilo\w*|lbs?|pounds?|stone|st|cm|metres?|meters?|"
                          r"miles?|hours?|mins?|minutes?|percent|%))"
                          r"\s*(?P<unit>months?|weeks?)?\b", re.I)


# A lead-in in front of a name is not part of it: "and fred is 5", "sorry, actually fred is 6".
# People start a short line with one of these, and the name reader took the lead-in for the name.
PET_LEAD_IN = re.compile(r"^(?:and|also|oh|but|well|yeah|yes|no|sorry|actually|ok|okay|right|"
                         r"wait|god|hang on)\b[\s,]*", re.I)


# The bot has asked how old the animal is and this line is the figure, with or without the
# pronoun: "hes 3", "she's 4", "3".
PET_AGE_ANSWER = re.compile(r"^\W*(?:(?:he|she|it|they)(?:'s|s|\s+is|\s+are|\s+is\s+now)?\s+)?"
                            r"(?P<age>\d{1,2}|" + AGE_IN_WORDS + r")\s*"
                            r"(?P<unit>years?|months?|weeks?)?\s*(?:old)?\W*$", re.I)


# A number on its own after a line about someone else, the way "no, 8" corrects "my son is 7".
from bot.memory.corrected import (  # moved out whole: see bot/memory/corrected.py.py  # noqa: F401
    AMOUNT,
    ANY_NUMBER,
    ASK_START,
    AT_TIME,
    A_DAY_BEFORE_A_MONTH,
    A_DAY_SAID_LONG,
    A_UNIT_SAID,
    BARE_HOUR,
    BARE_NEW_COUNT,
    CORRECTABLE,
    COUNT_SAID,
    CURRENCY,
    DATE_DAY,
    DATE_PHRASE,
    DAY_WORD,
    MADE_OF_A_VALUE,
    MONTHS,
    MONTH_ALT,
    MONTH_WORD,
    MONTH_WORDS,
    NAMING_VERB,
    NOT_A_FACT_OF_THEIRS,
    NO_SUBJECT_OF_ITS_OWN,
    NUMBER_DIGITS,
    NUMBER_VALUE,
    NUMBER_WORD,
    OTHER_BARE_NUMBER,
    RELATIVE_MONTH,
    STILL_THE_SAME_PERSON,
    _a_bare_hour,
    _a_birthday_for_somebody,
    _a_birthday_on_the_last_line,
    _a_count,
    _a_day_in_the_kind,
    _a_day_written_the_way_the_store_writes_it,
    _a_name_for_a_person,
    _a_name_the_store_keeps,
    _a_new_name_was_said,
    _a_relative_line,
    _a_relative_month,
    _a_spelling_of,
    _a_word_of_a_name,
    _an_amount_on_the_measure,
    _apply_correction,
    _asks,
    _birthday_words,
    _carries,
    _clock_key,
    _correct_a_persons_name,
    _correct_birthday,
    _correct_clock,
    _correct_count,
    _correct_date,
    _correct_fact,
    _correct_number,
    _correct_other,
    _correct_plan,
    _correct_the_count_on_the_table,
    _correct_their_birthday,
    _correct_when,
    _count_said,
    _date_in_plan,
    _date_said,
    _date_word,
    _date_word_case,
    _denies_and_names,
    _drop_wrong,
    _fact_naming,
    _keep_unit,
    _kind_of_value,
    _letters_apart,
    _make_corrects,
    _many,
    _measured_the_same,
    _names_a_half_of_the_day,
    _number_belongs_to_that_age,
    _number_in,
    _plan_saying,
    _plan_the_line_named,
    _plan_told_line,
    _stated_families,
    _stated_last,
    _stated_plan,
    _swap_in,
    _the_line_is_about_that_birthday,
    _the_person_the_plan_is_about,
    _the_plan_before,
    _the_plan_on_the_table,
    _the_topic_with_the_new_clock,
    _the_unit,
    _what_took_its_place,
    _without_the_naming_verb,
)


from bot.memory.store_replies import (A_HAVE_QUESTION, _a_bare_limit_ask, ACTIVITY_ASK,  # noqa: F401
                                      ANSWER_MODULES, ASK_WITHOUT_MY, BARE_WHAT_I_DO, CANT_HAVE,
                                      CAN_HAVE, CAN_THEY_HAVE, CAN_THEY_HAVE_A_FOOD,
                                      CHECK_FOLLOWED, DAY_IT, DAY_THING, EAT_ASK, FIRST_ASK,
                                      MONTHS, NO_RECORD, OTHER_FACT, PLAN_MINE, POINTS_BACK_AT_IT,
                                      THEM, TIME_ASKS, TIME_IT, TIME_THING, TOPIC_ASK, WHERE_PLAN,
                                      WHOLE_ASK, YES_NO_ASK, _RELATION,
                                      _a_feeling_about_what_they_said, _a_limit_kept_for_them,
                                      _a_number, _a_state_that_was, _a_thing,
                                      _a_whole_answer_to_hand_back, _about_the_bot_here,
                                      _about_this_chat, _activity_line, _after_the_yes_no_frame,
                                      _animal_family, _asks, _asks_about_someone, _bare,
                                      _behind_a_remembering_frame, _can_close, _canon_relation,
                                      _diet_reply, _folded, _halves, _how_far_along, _kind,
                                      _longest, _name_they_answered, _named_person,
                                      _names_its_thing, _names_minutes, _names_the_thing,
                                      _other_person_reply, _person_from_pronoun, _plain_line,
                                      _plans_reply, _reads_as_the_invitation, _repeat_ask,
                                      _says_something, _says_the_verb, _sentences,
                                      _someone_else_named, _statement, _the_animal_of_the_pick,
                                      _the_back_this_turn, _the_budget_on_the_answer,
                                      _the_call_from_the_advice, _the_job_was_just_said,
                                      _the_limit_the_last_line_gave, _the_limit_they_share,
                                      _the_person_still_in_hand, _the_prep_day, STATES_A_LIMIT,
                                      _the_same_fact_about_someone, _the_store_reply, _told_phrase,
                                      _vary, ack, company, content, current, decided, enough_reply,
                                      extract, family_name, forget, guest, how_many, last_user,
                                      name, note, others, pick, plans, rates_reader, re, recall,
                                      recent, remember, remember_other, reminded, stem, thread,
                                      told_about, units, until_answer, user, when_answer,
                                      REPEAT_WORDS, asks_again)


# A correction of someone else's age carries the number with a pronoun: "my son is 7" then
# "actually hes 8". That line states no fact of its own, so it is read against the person the
# pronoun points at, and only when that person already has an age stored: a correction replaces
# a fact, it is not the first one said. A long line is not a correction of anything, it is a new
# sentence that happens to hold a number.
AGE_FIX = re.compile(r"\b(?:he|she|they)(?:'s|s| is| are| was)\s+(?:now\s+)?"
                     r"(?P<age>\d{1,3}|" + AGE_IN_WORDS + r")\b(?!\s+of\b)",
                     re.I)


# "i meant" belongs here with "i mean": both say the value being given replaces one already given,
# and the word boundary after "mean" meant "i meant he is 8" matched neither - the correction was
# applied by the others path below and then answered as if it were news.
CORRECTING = re.compile(r"\b(?:actually|no|nope|sorry|wait|i mean|i meant|make it|makes it)\b",
                        re.I)


# How long a pregnancy has run goes up as the chat goes on, and the line that moves it names
# nobody: "my wife is 8 weeks pregnant" then "shes 10 weeks now" was answered "Got it - she's 10
# weeks now." while the store still held 8, so the ask after it said "Eight weeks." - the bot
# told the person the correction landed and then contradicted itself. The same shape as an age
# put right: the pronoun says who, and only a pregnancy already on record has a length to move.
WEEKS_FIX = re.compile(r"\b(?P<weeks>\d{1,2})\s*(?:weeks?|wks?)\b", re.I)


PREGNANCY_SAID_AGAIN = re.compile(r"\b(?:pregnant|expecting)\b", re.I)


# A correction of someone else's name carries it with a pronoun: "my sister is called meg" then
# "actually she's called maggie". The store kept meg, so the bot said "Got it - she's called
# maggie." and then answered "what's my sister called" with "Your sister is called Meg." - it
# told the person that the correction landed and then contradicted itself. The pronoun says who
# it is about, and a name is only replaced when that person already has one: this is the second
# name said, not the first.
# "her names actually hannah" is the same line with the apostrophe typed out, and it reached
# nobody: the possessive shape asked for "name is" exactly, so the store kept Anna while the
# reply handed the line back ("Her names actually hannah, good to know"). A name said after the
# word that opens a correction belongs to the person the possessive points at.
NAME_FIX = re.compile(
    r"\b(?:(?:he|she|they)(?:'s|s| is| was)?\s+(?:actually\s+|really\s+)?(?:called|named)"
    r"|(?:his|her|their)\s+names?\s+(?:is|was|actually|really))\s+"
    r"(?P<name>[a-z][a-z'\u2019-]{1,19})\b", re.I)


NAME_NOT_A_NAME = frozenset("""not called named now really also still a an the""".split())


# A name put right without the word "called" in it: "my daughter is called amy" then "no sorry,
# she is rosie". The plain "is" is also how a person says everything else about somebody ("she is
# tired", "she is 8", "she is a nurse"), so the word after it is only read as a name when it is
# not one of the words everybody uses. Rosie is a name; tired and nurse are not.
A_NAME_AFTER_A_PRONOUN = re.compile(
    r"\b(?:he|she|they)(?:'s|s| is| was)\s+(?P<name>[a-z][a-z'\u2019-]{1,19})\s*[,.!]?$", re.I)


# A pet's name given with its verb, for the correction that moves it: "no hes called max".
A_NAME_WITH_ITS_VERB = re.compile(r"\b(?:called|named)\s+(?P<name>[A-Za-z][A-Za-z'-]{1,19})\b",
                                  re.I)


# A name said for another animal of the same kind: "no my other cat is called max", "no we also
# have a cat called max". The word says the name belongs to a different animal, so it is a second
# pet rather than the name on the one in hand put right.
ANOTHER_ANIMAL = re.compile(r"\b(?:other|second|another|also|third)\b", re.I)


# A make said again in the words people use for it: "sorry its a focus", "actually its a 3 series".
# The line names no thing of its own, so the thing is the one the chat was last told the make of -
# the same way a corrected age goes on the person the last age went on.
CORRECTS_A_MAKE = re.compile(
    r"\b(?:sorry|actually|no|i mean|make that|or)?[\s,]*(?:its|it's|it is)\s+"
    r"(?:actually\s+|really\s+|just\s+)?(?:a|an|the)\s+(?P<value>[a-z0-9][a-z0-9' .+-]{0,31})$",
    re.I)


# A name given again for a person the store already holds, with no correcting word in the line:
# "my son is called jack" then "hes called jake". `_fix_a_persons_name` above wants a correction
# ("no she isnt, shes called dana"), so the plain form reached nobody and the store kept Jack while
# the reply said "He's called jake, good to know".
NAME_GIVEN = re.compile(
    r"\b(?:he|she|they)(?:'s|s| is| was)?\s+(?:called|named)\s+(?P<name>[a-z][a-z'\-]{1,19})\b"
    r"|\b(?:his|her|their)\s+name(?:'s|\s+is)\s+(?P<name2>[a-z][a-z'\-]{1,19})\b", re.I)


# A name given for a person ends the line: "hes called jake". The word after "called" in a longer
# line is usually not a name at all - "hes called in sick today" is a man phoning work, and reading
# it as one answered the next ask "Your son is called In".
NOT_A_NAME_AFTER_CALLED = frozenset("""
in out off up down back away over round around about on at by for with without into onto
sick ill late busy tired poorly bad good home here there now soon again today tonight
tomorrow yesterday it them him her me us you one ones the a an
""".split())


# The digits of a value, so "£500" and "500" are the same number. The unit that may follow is
# taken only when it is a unit on its own: "90 kilos" is 90, not "90 k", and "90k" is still 90.
NUMBER = re.compile(r"[£$€]?\d+(?:[.,]\d+)?(?:\s?(?:pounds|quid|euros?|dollars?|k))?(?![a-z])")


# A correction does not always wear a marker. Once a wrong value has been said, "its Preeya not
# Priya" and "not Priya, Preeya" name both values with no "no" and no "sorry" in front, and
# they left the store alone: the old value stayed, the line was filed as a fact, and "what do you
# know about me" answered with both names. The shape alone is not enough to tell a correction
# from a statement - "its raining not sunny" has the same shape - so the reading is done here,
# where the store is, and only counts when the value it takes back is one it already holds.
PAIR_WITHOUT_A_MARKER = (
    re.compile(r"^\W*(?:(?:ok|okay|oh|well|so|and|hmm)[,. ]+)*"
               r"(?:(?:it'?s|its|that'?s|thats)\s+)?"
               r"(?P<to>[a-z0-9][a-z0-9'-]{0,19})\s*,?\s+not\s+"
               r"(?P<wrong>[a-z0-9][a-z0-9'-]{0,19})[.!]?\s*$", re.I),
    re.compile(r"^\W*(?:(?:ok|okay|oh|well|so|and|hmm)[,. ]+)*"
               r"not\s+(?P<wrong>[a-z0-9][a-z0-9'-]{0,19})\s*[,\u2013\u2014;-]\s*"
               r"(?:(?:it'?s|its|that'?s)\s+)?(?P<to>[a-z0-9][a-z0-9'-]{0,19})[.!]?\s*$",
               re.I),
    # "i'm not 42, i'm 43" and "it's not florence it's rome": the same pair with the copula said
    # twice, which is how most people put a figure or a name about themselves right. The half that
    # is taken back comes first here, so the groups are the other way round from the shapes above.
    re.compile(r"^\W*(?:(?:ok|okay|oh|well|so|and|hmm|sorry|actually|no|nope)[,. ]+)*"
               r"(?:i'?m|i am|im|it'?s|its|it is|that'?s|thats|we'?re|we are)\s+not\s+"
               r"(?P<wrong>[a-z0-9][a-z0-9'.\-]{0,19})"
               r"[\s,;.!-]*(?:but\s+)?"
               r"(?:i'?m|i am|im|it'?s|its|it is|that'?s|thats|we'?re|we are)\s+"
               r"(?P<to>[a-z0-9][a-z0-9'.\-]{0,19})[.!]?\s*$", re.I),
)


# A word that can sit in either half of that shape and mean nothing as a value.
NOT_A_NEW_VALUE = frozenset("""a an the me you it that this these those my your his her our their
thanks thank sure fair right wrong now then today tomorrow yesterday fine bad good great sorry
please yes yeah no not ok okay yet even both all much many one two three too so there here what
why how who when where true false""".split())


# "my son is too" is the limit the line before just gave, said again about somebody else. The
# line names a person and agrees with what was said and nothing more, so nothing carried the
# allergy across: the son was filed with no limit at all, and every later ask about him was
# answered as if the allergy were only theirs.
TOO_AS_WELL = re.compile(
    r"^(?:(?:and|also|but|plus)\s+)?(?:my|our)\s+(?P<who>[a-z]+(?:[ -]in[ -]law)?)\s+"
    r"(?P<agree>is\s+as\s+well|is\s+too|as\s+well|also|too)$", re.I)


# The word that stands for the person again later in the same reply: "frightened for your mum ...
# any less help to her". A reply that says "them" about one woman is the machine talking, so the
# kin word decides, and the ones that can be either ("friend", "partner", "child") take "them".
OTHER_NOUNS = frozenset("""friend mate partner baby child kid children kids cousin parent parents""".split())


FIGURE_ASK = re.compile(
    r"^\W*(?:(?:and|but|so|ok|okay|right|then|oh|well)\W+)*"
    r"how\s+(?P<asked>many|much|long|far)\b(?P<rest>.*)$", re.I)


# What may stand around the unit on such a line without naming a thing: "how many weeks then",
# "how long do you reckon". A content word that is not a unit ("how long should i rest it") means
# the line is asking about a thing, and that thing has an answer of its own.
FIGURE_FILLER = frozenset("""a an the it its that this them those there here then now again
    roughly exactly approximately about around all told overall altogether total more less much
    many long do does did will would should can could you i we they he she reckon think suppose
    guess say again please for of in at on to be have has had is are was were and but so if
    when after before time times per each""".split())


# What may follow the unit and still leave it the noun of the figure. "eight to ten weeks is a
# realistic build" is a figure; "the 5 to 6 minute egg" is a length used as an adjective, and a
# card that says it is not answering "how many minutes".
FIGURE_AFTER = frozenset("""is are was were and or a an the in for of to on at by after before
    now then so but if when that from with without each every per of till until into about
    to around roughly or while than which where""".split())


# A length that belongs to an action rather than to what the answer is about: "ice it for 20
# minutes at a time with a cloth round it for the first two days" is how long to ice it, not how
# long a knee takes to heal, and "two days" there is not the answer to "how long". A figure whose
# own clause says when or how often it is done is a duration of the doing, and it is handed back
# as a confident number where the honest reply is that the length is not in the answer.
ACTION_DURATION = re.compile(
    r"\bat a time\b|\bfor the first\b|\bfor the next\b|\bin a row\b|\beach time\b"
    r"|\bthe (?:first|next|last|coming|following|remaining|final)\b"
    r"|\b(?:once|twice|three times|a few times) a day\b|\ba day or two\b|\bper session\b",
    re.I)


# An amount that belongs to a step rather than to what the answer is about: "raise the standing
# order by 10 pounds whenever a bill or a habit goes" states 10 pounds as the size of a move, and
# the clause says when it is made. A bare "how much" after the same answer was handed "10 pounds."
# where the answer's own figure is "10 to 20 per cent of what you take home" - so a figure whose
# clause says when or if it happens is a step's amount, the money analogue of ACTION_DURATION.
ACTION_AMOUNT = re.compile(
    r"\b(?:whenever|when|if|once|each time|any time|every time|in case|unless)\b", re.I)


# An amount, with the sign in front of the number or the word for it after it, and a range read
# whole: "£50 to £120" is one amount and is handed back as it was said.
A_MONEY_FIGURE = re.compile(
    r"(?:£|\$|€)\s*\d[\d,]*(?:\.\d+)?(?:\s*(?:to|-|or)\s*(?:£|\$|€)?\s*\d[\d,]*(?:\.\d+)?)?"
    r"|(?<![\d.,])\d[\d,]*(?:\.\d+)?(?:\s*(?:to|-|or)\s*\d[\d,]*(?:\.\d+)?)?\s*"
    r"(?:pounds?|quid|dollars?|euros?|pence)\b", re.I)


# A share of what they take home answers "how much" when the answer states no sum of money, and it
# is what the saving answer's own figure is: "pick an amount you will not miss, 10 to 20 per cent of
# what you take home" is the amount, and reading only pounds in it left the line with the one sum
# the answer states as an example of a step ("raise the standing order by 10 pounds whenever a bill
# or a habit goes") or with nothing at all.
A_PERCENT_FIGURE = re.compile(
    r"(?<![\d.,])\d[\d,]*(?:\.\d+)?(?:\s*(?:to|-|or)\s*\d[\d,]*(?:\.\d+)?)?\s*"
    r"(?:per\s?cent|percent|%)", re.I)


# A second figure of the same kind said without the unit, as a list: "6 minutes for a runny yolk,
# 7 for jammy, 9 to 10 for hard boiled". The card is answering this ask already.
LISTED_FIGURE = re.compile(r"(?:,|;)\s*\d+(?:\s*(?:to|-|or)\s*\d+)?\s+for\b", re.I)


# A "how much a month" line asks for an amount per month, and the answer to it is a table of
# rates: "For £4,000: £100 a month is 40 months, £250 a month is 16 months". Reading one figure
# out of that table gave "4 months." to the person who asked what to put by each month - the
# figure there is how long the saving takes, not the amount, and the saving answer owns the line.
A_RATE_ASK = re.compile(
    r"how\s+much\b[^.?!]*\b(?:a|per|each|every)\s+(?:day|week|month|year)\b", re.I)


A_RATE_STATED = re.compile(
    r"(?:£|\bgbp\s*)?\d[\d,.]*\s*(?:pounds?\s+)?(?:a|per|each|every)\s+"
    r"(?:day|week|month|year)\b", re.I)


# The words that say a statement is the first one put right, rather than news said once: "sorry, i
# meant my son is 8", "i meant 8". Only these lines are answered here - a correction said the
# other way ("no he is 9", "actually hes 8") is already said back by the same receipt that
# answers a plain statement about someone, and it needs nothing from this reader.
SAID_AGAIN = re.compile(r"\bi\s+(?:mean|meant)(?:\s+to\s+say)?\b", re.I)


# "sorry" opens two readings at once: the correction, "my son is 7" then "sorry he is 9", and the
# message that apologises to somebody. The apology card took the turn and the person who had just
# put their son's age right was told how to word an apology to him. A line that says sorry and
# puts a fact right is a correction, so it is answered with the fact, like "i meant" below.
SORRY_OPENS_A_CORRECTION = re.compile(r"\b(?:sorry|soz)\b", re.I)


# A recall ask about a slot of a person or a thing is the direct ask with a wrapper around it:
# "what did i say her birthday was" is "when is her birthday", "how old did i say she was" is
# "how old is she", "what did i say his name was" is "what is his name". The reader that owns the
# slot answers the direct ask, so the wrapper needs no reader of its own - and read as a topic
# instead, the last line they said about anything came back as if it were the answer ("what did
# i say his name was" was answered with the line about their knee).
RECALL_WRAPPER = re.compile(
    r"^\s*(?:and\s+|so\s+|but\s+|also\s+|again\s+)?"
    r"(?P<word>what|when|how\s+old)\s+(?:did|do)\s+(?:i|we)\s+"
    r"(?:say|call|tell\s+(?:you|u)|told\s+(?:you|u)|mention)\s+(?P<rest>.+?)\s*\??\s*$", re.I)


# The slot the ask is about, and the question word that asks it directly. A word not in this
# table is not a slot the store keeps against a person, and the line is left to the recall paths.
RECALL_SLOTS = (
    (re.compile(r"\b(?:names?|called)\b", re.I), "what", "name"),
    (re.compile(r"\b(?:birthday|bday|dob|date\s+of\s+birth)\b", re.I), "when", "birthday"),
    (re.compile(r"\b(?:ages?)\b", re.I), "how old", "age"),
    (re.compile(r"\b(?:budget|salary|wage|rent|target|savings?)\b", re.I), "what", None),
    (re.compile(r"\b(?:address|postcode|number|time|date)\b", re.I), "what", None),
)


RECALL_POSSESSIVE = re.compile(r"^\s*(?P<poss>my|our|his|her|their)\b", re.I)


# A slot said on its own, straight after the possessive: "his name", "her birthday", "my budget".
# Anything else ("my dog called") is a thing whose slot the store reads with its own readers.
RECALL_SLOTS_BY_POSSESSIVE = re.compile(
    r"^\s*(?:my|our|his|her|their)\s+(?P<attribute>names?|birthday|bday|dob|ages?|"
    r"budget|salary|wage|societys?|address|postcode)\??\s*$", re.I)


# A slot said in the chat in words of its own: an age is a figure, a name is "called", a
# birthday is a month or the word itself. It only matters when the slot's reader found nothing:
# then the fact may still have been said in a shape the reader does not read, and the store must
# not answer that they never told it.
SLOT_WORDS = {
    "age": re.compile(r"\b\d|\b(?:age|aged|old)\b", re.I),
    "name": re.compile(r"\b(?:name|called|named|calls)\b", re.I),
    "birthday": re.compile(r"\b(?:birthday|bday|dob|january|february|march|april|may|june|july|"
                           r"august|september|october|november|december)\b", re.I),
}


# Setting out is not prep, and nobody asking when to leave wants the day to do the work on:
# "i have an interview on thursday" then "when is the best time to leave for it" was answered
# with "Wednesday is the day for the prep". The verb sits in the tail the ask points back from,
# just before the "for it", so it is read there rather than anywhere in the line.
# A verb put on the thing they just said: "to book it", "to renew it", "to prep for it". The
# knowledge base often has a real answer for those, so the store only claims one when it can add
# the day the work goes on. A pointing word that follows no verb ("when is that again") is the
# whole ask, and the date they gave is exactly what it wants back.
WORK_ON_IT = re.compile(r"\b[a-z]{3,}\s+it\b", re.I)


def _diet_reply(memory, low=""):
    """How they eat, said back when they ask: "You told me you're vegetarian."

    The diet is kept on every line they say it in, so the answer is the fact and nothing else.
    A diet stored as a negation comes back with its verb ("you don't eat meat"), because "you're
    no meat" says nothing. What they cannot eat is not one key, though: "im coeliac" is a
    condition and "im allergic to nuts" is an allergy, and a question about the fact is about
    all of it - so the read says back whichever the store holds, and only when the line asks
    about the fact (a line asking for a meal keeps its meal).
    """
    # A line that reports a change to the diet, or asks for one, is not a request for the fact
    # and not a gap in it: "i want to lose a bit of weight" then "ive changed my diet" was
    # answered "You haven't told me about your diet", a denial of what they had just said.
    said = a_change.reported(low, "diet")
    if said:
        was = user(memory).get("diet")
        if said == "changed" and was:
            # The reply says what it is doing with the old value ("You were vegetarian, so I'll
            # drop that"), so the store has to do it: "im vegetarian" / "i changed my diet" /
            # "am i vegetarian" said "Yes - you're vegetarian" and "what can i cook" still picked
            # the vegetarian dish, so the bot promised a drop and went on quoting the value.
            forget(memory, "diet", [was])
            user(memory)["diet_changed"] = was
        return a_change.reply(said, "diet", was=was)
    diet = user(memory).get("diet")
    if not diet:
        if str(low or "") and not DIET_FACT_ASK.search(str(low or "")) \
                and _food_facts(memory):
            # A meal ask ("what do i eat") after they have told the store what they cannot eat is
            # a question about the food, and "You haven't told me about your diet" is a claim
            # about the person that is false when the store is holding it. What the store can say
            # about the dinner is what each meal has to leave out, so that is what it says, and
            # the kitchen picks the dish ("im allergic to nuts" then "what do i eat" was the
            # denial, and "im coeliac" then "what do i eat" was the same one a key over).
            #
            # This is asked before the fact said back, because the fact said back is a fallback
            # for lines with no meal ask and it was written when the meal rows answered this one;
            # saying "You told me you're allergic to nuts" to "what do i eat" answers nothing.
            left_out, said_so = _what_a_dinner_has_to_leave_out(memory)
            if left_out:
                return ("Nothing with " + _say_a_list(left_out) + " in it — " +
                        " and ".join(said_so) + ". Tell me what is in the fridge and I'll pick "
                        "a dinner around it.")
        kept = _food_facts(memory)
        if kept:
            # The store holds what they cannot eat, so a denial would be false whatever the
            # line's shape: "im allergic to nuts / im coeliac / what do i eat" was answered
            # "You haven't told me about your diet." Saying the fact back is the honest reply.
            return "You told me you're " + _say_a_list(kept) + "."
        if DIET_FACT_ASK.search(str(low or "")):
            kept = _food_facts(memory)
            if kept:
                return "You told me you're " + _say_a_list(kept) + "."
        who, theirs = _other_fact(memory, "diet")
        if theirs and who:
            return ("You haven't told me about yours \u2014 the diet you mentioned is your "
                    + who + "'s.")
        changed_from = user(memory).get("diet_changed")
        if changed_from and DIET_FACT_ASK.search(str(low or "")):
            # The change was said and the value it named was dropped, so the store holds nothing
            # and "You haven't told me about your diet" would deny the change they just reported.
            was = str(changed_from).strip()
            was = ("not eating " + was[3:] if was.lower().startswith("no ")
                   else "being " + _diet_words(was))
            return "You told me your diet had changed from " + was + ". What is it now?"
        take_back, gone = _the_take_back(memory, "diet")
        if gone:
            # They took a diet back, so they have said how they eat: nothing is in the store
            # because the take-back emptied it, and the honest answer is their own take-back
            # said back rather than denying the whole thing.
            return _a_take_back_said_back(take_back, gone)
        # A denial is a reply about the chat, so it needs a line that asks about the chat: "what do
        # i eat" is somebody asking for a dinner who never mentioned a diet, and the kitchen has a
        # meal to suggest. The stand-down below reads the same ask where a diet is held; this is
        # the path with nothing held, and the phone answered it with a claim about the person.
        if MEAL_WANTED.search(str(low or "")) and not DIET_FACT_ASK.search(str(low or "")):
            return None
        return _deny(memory, "diet", "You haven't told me about your diet.",
                     own=_their_own_diet)
    diet = str(diet)
    if MEAL_WANTED.search(str(low or "")) and not DIET_FACT_ASK.search(str(low or "")):
        # A dinner is the kitchen's to answer, and it is told about the diet on the way past. The
        # store's job on this line is only to keep what they said; saying it back answers a
        # question nobody asked, in the words they used to ask it.
        left_out, said_so = _what_a_dinner_has_to_leave_out(memory)
        if left_out:
            return ("Nothing with " + _say_a_list(left_out) + " in it \u2014 " +
                    " and ".join(said_so) + ". Tell me what is in the fridge and I'll pick a "
                    "dinner around it.")
        return None
    if diet.startswith("no "):
        return "You told me you don't " + _diet_how(diet) + " " + diet[3:] + "."
    if diet in WAY_OF_EATING:
        return "You told me you're " + _diet_words(diet) + "."
    if diet in PLAN_DIETS:
        # A plan is something they are doing, not something they are: "you're keto" is not it.
        return "You told me you're doing " + _diet_words(diet) + "."
    return "You told me you're " + diet + "."


# The words people use for the facts the store keeps, so a callback that names one of them can
# tell "they never mentioned it" from "I could not find the line, but the fact is kept".
FACT_WORDS = frozenset((
    "name", "called", "age", "old", "job", "work", "works", "working", "city", "town", "live",
    "lives", "living", "moved", "moving", "from", "diet", "dieting", "eating", "food", "budget",
    "money", "afford", "allergy", "allergies", "allergic", "pet", "pets", "dog", "cat", "height",
    "tall"))


for _concept, _words in (
        ("mother", "mum mom mummy ma mam mother mumma"),
        ("father", "dad daddy pa papa father"),
        ("parent", "parent parents folks"),
        ("child", "kid kids child children baby toddler"),
        ("dog", "dog puppy pup dogs"),
        ("cat", "cat kitten kitty cats"),
        ("pet", "pet pets"),
        ("car", "car vehicle motor"),
        ("home", "home house flat apartment place"),
        ("party", "party birthday bday celebration bash"),
        ("job", "job work career"),
        ("food", "food dinner tea meal supper"),
        ("money", "money budget cash savings"),
        ("diet", "diet vegetarian vegan pescatarian"),
        ("doctor", "doctor gp surgery hospital"),
        # The things people tell a friend about, said with a second set of words: a wedding is
        # "getting married", revision is "an exam in may", the gym is "getting fitter", cigarettes
        # are "stopping smoking". Without them the recall told a person who had just said they
        # were getting married "You haven't said anything to me about the wedding yet."
        ("wedding", "wedding weddings married marry marriage engaged engagement bride groom "
                    "fiance fiancee honeymoon"),
        ("holiday", "holiday holidays vacation trip trips break abroad travelling travel"),
        ("exam", "exam exams revision revise revising coursework dissertation thesis mock"),
        ("gym", "gym gyms fitter fitness exercise exercising workout workouts jogging running"),
        ("smoking", "smoking smoke smoker cigarettes cigarette fags vaping vape nicotine")):
    for _word in _words.split():
        CONCEPTS[_word] = _concept


# Going somewhere is a holiday, and the line says the country rather than the word: "im going to
# spain in june" is what "what did i say about my holiday" is asking about.
for _country in extract.COUNTRIES:
    CONCEPTS.setdefault(_country.lower(), "holiday")
