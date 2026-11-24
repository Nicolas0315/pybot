"""Part 8 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from .filler import without_the_shrug
from .topics_part_01 import (
    words, alike, keywords, _after_an_emergency, current,
)
from .topics_part_02 import (
    _entry, _leads_a_question, _after_a_correction, _what_they_are_not_doing,
)
from .topics_part_03 import (
    _key_words_of, _constrains_the_ask, _how_they_feel, _keyed_to, _subject_words_to_carry,
    elided_ask, how_much_of_the_thing_in_hand,
)
from .topics_part_04 import (
    _said_later_than, _the_turn_we_lean_on,
)
from .topics_part_05 import (
    _still_the_topic, bare_question, carried_topic, left_for_a_blank, next_slot_reading,
    the_thing_the_subject_brings,
)
from .topics_part_06 import (
    carry_the_ask, leans_on_topic, meal_follow_up, the_period_they_ask_about,
    the_weather_of_the_trip, widen,
)
from .topics_part_07 import (
    _carrying_on, _the_length_of_the_aim, _widened, the_airport_there_is, the_animal_the_subject_is,
    the_limit_of_the_thing, the_prognosis_the_line_asks, the_pronoun_written_as_what_it_stands_for,
    the_property_of_the_thing, the_thing_it_is, _note,
)


# The gatherings people announce they are putting on. The food for one is the first thing a
# friend asks about, and the entries hold the food, not the occasion.
GATHERING_WORDS = frozenset("""barbecue bbq party picnic birthday brunch supper do
gathering get-together potluck housewarming""".split())


# A gathering that starts tonight has no day before in it, so the food-ahead entry cannot help.
TOO_SOON_TO_COOK = re.compile(r"\b(?:tonight|today|this (?:evening|afternoon)|in an hour|in a few hours|"
                              r"right now|already)\b", re.I)


# A do put on for a child or for one person is about that person: the food for a crowd is not
# what they asked, and the bot's own question ("What are they into at the moment?") is better.
FOR_SOMEBODY = re.compile(
    r"\b(?:kid|kids|child|children|toddler|teen|teens|teenager|teenagers)\b|"
    r"\b\w+[- ]year[- ]old\b|\b\d+\s*(?:st|nd|rd|th)?\s*birthday\b|"
    r"\b(?!\d+\s)(?:for|of) (?:my|his|her|our|a|an)\s+(?:mum|mom|dad|father|mother|son|daughter|"
    r"wife|husband|partner|friend|sister|brother|nan|nana|gran|granny|grandma|grandad|grandpa|"
    r"colleague|boss|niece|nephew|cousin|aunt|uncle|godson|goddaughter)\b", re.I)


PUTTING_ON = re.compile(r"\b(?:we|i)(?:'?re| are| am|'?m)?\s+"
                        r"(?:having|doing|throwing|hosting|planning|organising|organizing|"
                        r"holding|arranging)\b")


def _a_gathering_read_as_the_food(understood, line, memory):
    """"we are having a barbecue" read as the food for it, when its own words reach nothing.

    A plan announced is the thing the chat is on, and the next turns add to it ("one of my
    friends is a vegetarian", "there will be nine of us"). The first turn itself reached no
    entry, so it was answered with a listening line and the plan never started. The food for a
    gathering is what a friend offers first, and the entry that holds it is keyed on the
    gathering's own word only for a party or a picnic, so both forms are tried and only one that
    reaches an entry is used.
    """
    if not isinstance(understood, dict):
        return None
    if understood.get("kind") != "statement" or understood.get("asks"):
        return None
    said = set(words(line))
    gathering = said & GATHERING_WORDS
    if not gathering or not PUTTING_ON.search(line):
        return None
    if _entry(line) is not None:
        return None  # the words already reach an answer: leave it alone
    if TOO_SOON_TO_COOK.search(line):
        return None  # a party tonight wants ice and glasses, and the entry is about the day before
    if FOR_SOMEBODY.search(line):
        return None  # a do put on for a child or for one person is about them, and the entry is not
    for candidate in [" ".join(sorted(gathering)) + " food", "party food"]:
        if _entry(candidate) is not None:
            return candidate
    return None


def _the_whole_topic(line, record_text, memory=None):
    """The line read with the topic's own words, phrase and all, or None when that reaches nothing.

    The topic lends its words one at a time and its gist is a single word, so a phrase the
    knowledge base keys on is split and nothing matches: after "im learning to drive", "how many
    lessons will i need" was widened to "learning drive", which reaches no entry, and the person
    got the search hedge with the answer one phrase away. Reading the topic back in whole keeps
    the particle that makes the phrase ("learn to drive", "get married", "pass my test"), and it
    is only asked for when every narrower widening has reached nothing.
    """
    if not _leads_a_question(line):
        # A statement that reaches nothing is left as it came in. Reading it against the thing
        # the chat is on is what turns "it was about a dog" - said of a film - into the entry
        # about a dog that wakes in the night, on the film's "night" and the line's "dog": a
        # question that reaches nothing wants the thing put back in, a remark does not.
        return None
    best, best_score = None, -1
    for said in _the_things_the_chat_named(record_text, memory, line):
        widened = str(line) + " " + said
        reached = _entry(widened)
        if reached is None:
            continue
        last = (memory or {}).get("last_answer")
        if isinstance(last, dict) and last.get("id") == getattr(reached, "id", None):
            # What the line reaches with the topic in it is the answer already on the screen:
            # saying it again is what this widening is for, not what it should do.
            continue
        # Which thing the chat named the line should be read against is decided by the answer
        # it reaches, not by how recent the thing is: "my test is in march" on the end of "how
        # many lessons will i need" reaches the revision planner on "test", and the plan two
        # lines back reaches the driving lessons on "drive". The thing whose words the entry is
        # actually keyed on is the one the ask is about.
        if _already_answered_here(reached, memory):
            # The chat has had this answer: a widening that reads a short line back to a thing
            # the bot has already dealt with is the repeat the store spends its time avoiding,
            # not a follow-up. "fine, ill have a look at it" after the tap got the cake
            # paragraph back, because the cake was still one of the things the chat had named.
            continue
        if not _the_answer_is_about_what_the_line_names(reached, line):
            continue
        score = _how_much_of_the_thing_the_entry_uses(reached, said)
        if score > best_score:
            best, best_score = widened, score
    return best


# A content word that names the shape of the ask rather than a thing in the world. "where do i
# start" is the whole of some lines, and every second answer the bot has says "start with"; the
# same goes for "first" ("what do i do first") and "next" ("what next"). These words are not
# evidence that an answer is about what the person asked about, so they do not confirm a
# widening on their own.
ASK_SHAPE_WORDS = frozenset("""
start starts started starting begin begins beginning beginning first next thing things step
steps part parts bit bits way ways point best better good useful help advice tip tips
""".split())


def _the_answer_is_about_what_the_line_names(entry, line):
    """True when the entry's own answer talks about the thing the line asks about.

    An entry is keyed on the words people use for its subject, so an entry about moving house
    with children is keyed on "school" while its answer is about council tax, the GP and the
    meters. After "we are thinking of moving to leeds", "what are the schools like" was widened
    to reach it and got a list of admin for a different question; the search hedge it had before
    was the better reply. So the answer the widening reaches has to use one of the line's own
    words - the driving lessons answer says "lessons", the wedding budget answer says "costs" -
    and a line with no content word of its own is let through, because there is nothing to check.
    """
    asked = [word for word in keywords(line) if len(word) > 3]
    if not asked:
        return True
    named = [word for word in asked if word not in ASK_SHAPE_WORDS]
    if not named:
        # The line is the shape of a question and nothing else - "where do i start", "what do i
        # do first", "where do i begin". Its one content word is one that any answer about any
        # subject can use (the tidying card opens "Start with what is on the floor"), so being
        # named in the entry's answer is no evidence at all that the entry answers this line.
        # After "i want to go back to work after 6 years at home", "where do i start" was widened
        # onto the room-tidying entry on the word "start" and got a paragraph about cups and
        # plates where the honest hedge was the better reply. A line that names no thing cannot
        # confirm the thing the widening reached, so the widening stands down.
        return False
    said = words(str(getattr(entry, "reply", "") or ""))
    return any(alike(word, token) for word in named for token in said)


def _already_answered_here(entry, memory):
    """True when the reply the entry gives has already been said in this conversation."""
    reply = str(getattr(entry, "reply", "") or "").strip()
    if not reply:
        return False
    opening = " ".join(reply.lower().split()[:8])
    for turn in (memory or {}).get("turns") or []:
        if not isinstance(turn, dict):
            continue
        said = " ".join(str(turn.get("bot") or "").lower().split())
        if said and said.startswith(opening):
            return True
    return False


def _how_much_of_the_thing_the_entry_uses(entry, said):
    """How many of the thing's own content words the entry the widening reached is keyed on."""
    keyed = _key_words_of(entry)
    return len([word for word in keywords(said)
                if len(word) > 2 and any(alike(word, key) for key in keyed)])


def _the_things_the_chat_named(record_text, memory, line=""):
    """The things the chat has named, newest first, to read a follow-up against.

    The topic the line leans on is not always the one that can answer it. "im learning to drive"
    then "my test is in march" then "how many lessons will i need": the newest thing the chat
    named is the date, and read against the date the ask reaches nothing, but the plan two lines
    back reaches the lessons answer in full. A follow-up is read against the newest thing that
    can answer it, which is the rule the picture is worth: the chat is still on the plan.
    """
    seen = []
    texts = [str(record_text or "")]
    if _leads_a_question(line):
        # Only a question is read against an older thing. A statement that reaches nothing is
        # left as it came in: "it was about a dog" after "i cried at a film last night" read
        # against the film reaches the dog-waking-at-night entry on "dog" and "night", and the
        # person talking about a film got advice on a dog that wakes in the night.
        for record in reversed(list((memory or {}).get("topics") or [])[-4:]):
            if isinstance(record, dict):
                texts.append(str(record.get("text") or ""))
    for text in texts:
        said = " ".join(text.lower().split())
        if not said or len(said.split()) > 12:
            continue
        if " ".join(words(said)) in seen:
            continue
        seen.append(" ".join(words(said)))
        yield said


def followup_reading(understood, memory):
    """This turn's reading with the current topic's subject put back in, when the line leans
    on it: 'and if I stuff it?' after a chicken is read as being about the chicken.

    A correction is read as the topic it corrected, because memory_store has already rewritten
    the topic with what they meant: 'sorry, I meant Florence' re-asks the Florence question.
    Only lines the reading alone cannot answer are widened, so an answer that already fits is
    never replaced by a guess.
    """
    if not isinstance(understood, dict):
        return understood
    carrying_on = _carrying_on(understood, memory)
    if carrying_on is not None:
        return carrying_on
    slot = next_slot_reading(understood, memory)
    if slot is not None:
        return slot
    if _after_an_emergency(memory):
        return understood  # mid-emergency the topic starts again from the line itself
    if _after_a_correction(memory):
        return understood  # the topic they have just corrected is not the one to widen with
    aim_length = _the_length_of_the_aim(understood, memory)
    if aim_length is not None:
        return aim_length
    # The pronoun put back where it was, before anything is carried onto the end of the line:
    # "how long can they be left alone" is the cat's question, and the subject carried onto the
    # end of it reached nothing while the cat's own row was one entry away.
    filled_in = the_pronoun_written_as_what_it_stands_for(understood, memory)
    if filled_in is not None:
        return filled_in
    pointed = the_thing_it_is(understood, memory)
    if pointed is not None:
        return pointed
    # "will it go away on its own" asks how long the thing goes on, which is a row of its own: the
    # pronoun is filled with the thing and asked in the wording that row is kept in.
    prognosis = the_prognosis_the_line_asks(understood, memory)
    if prognosis is not None:
        return prognosis
    # "is it expensive" asks what the thing in hand is like, and only the pronoun says which thing
    # it is: filling it in is what reaches the entry for the cost of the trip to Rome, instead of
    # the sights answer being handed back with "Same as before" in front of it.
    property_ask = the_property_of_the_thing(understood, memory)
    if property_ask is not None:
        return property_ask
    animal = the_animal_the_subject_is(understood, memory)
    if animal is not None:
        return animal
    airport = the_airport_there_is(understood, memory)
    if airport is not None:
        return airport
    # "how much is too much" after "i drink a lot of coffee" is the same family: the thing in hand
    # is what the limit is about, and the row that answers it is keyed to the thing.
    limit_ask = the_limit_of_the_thing(understood, memory)
    if limit_ask is not None:
        return limit_ask
    # The shrugs in the middle of the line are not part of the question the topic is put back
    # into: "what can i do to help her really" widened to "... really mum arthriti", which names
    # nothing, and the answer one word away was lost.
    line = without_the_shrug(str(understood.get("clean") or understood.get("text") or ""))
    gathering = _a_gathering_read_as_the_food(understood, line, memory)
    if gathering is not None:
        # "we are having a barbecue": they are hosting and nothing in the words reaches an
        # entry, so the turn was answered "I'm listening - say more if it helps." while the
        # store holds what to feed a crowd. A gathering announced asks for the food for it.
        reading = dict(understood)
        reading["clean"] = gathering
        reading["words"] = words(gathering)
        if "norm_text" in reading:
            reading["norm_text"] = gathering
        return reading
    period = the_period_they_ask_about(understood, memory)
    if period is not None:
        reading = dict(understood)
        reading["clean"] = period
        reading["words"] = words(period)
        if "norm_text" in reading:
            reading["norm_text"] = period
        return reading
    meal = meal_follow_up(understood, memory)
    if meal is not None:
        return meal
    trip = the_weather_of_the_trip(understood, memory)
    if trip is not None:
        reading = dict(understood)
        reading["clean"] = trip
        reading["words"] = words(trip)
        if "norm_text" in reading:
            reading["norm_text"] = trip
        return reading
    record = carried_topic(memory, line)
    if record is None or left_for_a_blank(memory, line):
        # The chat has moved on to a thing named in a turn we could not answer: widening this
        # line with the older subject would answer about the wrong thing.
        return understood
    same_ask = how_much_of_the_thing_in_hand(line, memory)
    if same_ask:
        reading = dict(understood)
        reading["clean"] = same_ask
        reading["words"] = words(same_ask)
        if "norm_text" in reading:
            reading["norm_text"] = same_ask
        return reading
    brought = the_thing_the_subject_brings(understood, memory)
    if brought is not None:
        reading = dict(understood)
        reading["clean"] = brought
        reading["words"] = words(brought)
        if "norm_text" in reading:
            reading["norm_text"] = brought
        return reading
    if elided_ask(line):
        # "any games", "what about drinks": the line names the part it asks about and leaves the
        # asking off, so the understanding engine reads it as a statement and no entry is
        # reached. The chat it is in says which entry of that kind is meant - a birthday picnic
        # with ten children is the games answer for children - and the line itself still has to
        # name the thing the entry is about, so this borrows a situation rather than a subject.
        # When the situation reaches nothing the line takes the way every other follow-up takes.
        situated = carry_the_ask(line, str(record.get("text") or ""), understood, memory)
        if situated is not None:
            reading = dict(understood)
            reading["clean"] = " ".join(str(situated).lower().split())
    leaning = _the_turn_we_lean_on(understood, memory)
    if leaning is not None and _said_later_than(leaning, record):
        # The turn the line leans on is the newer thing on the table: the subject moves on
        # inside a topic ("im planning a veg patch" / "also i want tomatoes"), and the earlier
        # words widen the line to nothing. Where the newer turn widens to nothing either, the
        # topic on memory is the one the line has been answered from all along, so nothing
        # changes for it.
        newer = _widened(line, understood, leaning, memory)
        if newer is not None:
            reading = dict(understood)
            reading["clean"] = " ".join(str(newer).lower().split())
            reading["words"] = words(reading["clean"])
            if "norm_text" in reading:
                reading["norm_text"] = reading["clean"]
            return reading
    if understood.get("intent") == "correction":
        text = str((record or {}).get("text") or "")
        if not text.strip() or " ".join(words(text)) == " ".join(words(line)):
            return understood
    elif bare_question(understood, memory) and carry_the_ask(
            line, str(record.get("text") or ""), understood, memory) is None:
        # Only when the topic's own words reach no entry: "should i cut the brown bits off?"
        # names something of its own (cutting), and the plant entry answers it through the
        # topic's subject words below, so the bare path must not take the line first - read
        # with the topic's key subjects in it, it reached the tipping entry on "tips" twice
        # and the plant chat lost its answer.
        # A question that names no subject of its own is read with the topic's own words in it:
        # "what should I wear" after an interview is the interview's words with the outfit ask,
        # and which entry answers that is the answers' to decide. The record's own words only:
        # an older record's subject is a different conversation ("im getting married in june"
        # after a boiler is not a question about the boiler), so a topic with no subject words
        # of its own lends nothing and the line is left alone.
        extra = []
        not_doing = _what_they_are_not_doing(record.get("text") or "")
        for word in _subject_words_to_carry(record, line, memory):
            if word in not_doing:
                continue  # "wont listen" is not a subject to widen the line with
            if _how_they_feel(word):
                continue  # "hate" is how they feel about the job, not what the job is
            if word not in words(line) and word not in extra:
                extra.append(word)
        if not extra:
            return understood
        widened = line + " " + " ".join(extra)
        found = _entry(widened)
        if found is None:
            # The topic as they said it, question and all: "i hate my job" / "what should i do"
            # lends only "job", and "what should i do job" reaches nothing, while the whole of
            # the topic reaches the entry about hating the job. Only an entry keyed to a word the
            # topic lent counts, so a topic that widens to an entry about something else is left
            # as it came in.
            said_whole = " ".join(str(record.get("text") or "").split() + [line])
            item = _entry(said_whole)
            if item is None or not any(_keyed_to(_key_words_of(item), word) for word in extra):
                return understood
            text = said_whole
        else:
            text = widened
    elif not _still_the_topic(record, memory):
        # The chat moved off the topic on a line answered as small talk, and nothing since has
        # leaned on it: see `_still_the_topic`. The leaning path above has already been tried,
        # because a turn of small talk does not stop the chat going back to the thing it was on.
        return understood
    elif leans_on_topic(understood, memory):
        subject_words = _subject_words_to_carry(record, line, memory)
        if not subject_words or all(word in words(line) for word in subject_words):
            return understood
        text = widen(line, subject_words, str(record.get("text") or ""))
        if text is None:
            # The topic's key words did not reach an entry, but the words of the topic the
            # knowledge base knows may: "why is that happening?" after a flat sourdough.
            text = carry_the_ask(line, str(record.get("text") or ""), understood, memory)
        if text is None:
            # A line that only adds a limit to the question ("i only have ten minutes") is that
            # question asked again with the limit in it.
            text = _constrains_the_ask(line, str(record.get("text") or ""))
        if text is None:
            text = _the_whole_topic(line, str(record.get("text") or ""), memory)
        if text is None:
            return understood
    else:
        # A line that names nothing of its own ("how often should I go?") is the same kind of
        # follow-up: it is read with the topic's words, or not at all.
        text = carry_the_ask(line, str(record.get("text") or ""), understood, memory)
        if text is None:
            text = _constrains_the_ask(line, str(record.get("text") or ""))
        if text is None:
            text = _the_whole_topic(line, str(record.get("text") or ""), memory)
        if text is None:
            return understood
    reading = dict(understood)
    reading["clean"] = " ".join(str(text).lower().split())
    reading["words"] = words(reading["clean"])
    # An entry that phrases itself from the line reads `norm_text`, the line as it was typed, so
    # the subject put back in has to be there too: "it is still tough in the stalk" after
    # sprouts reached the brassica fix on its words, and the fix then read the line as it came
    # in, found no vegetable in it, and declined - so the widening bought nothing and the turn
    # went to the small talk with a reply about tiredness.
    if "norm_text" in reading:
        reading["norm_text"] = reading["clean"]
    return reading


# The words a follow-up brings to the record it stays on, as this turn put them there. The turn is
# not over when they are added - the reply is composed afterwards - so they are noted and taken
# back if that reply turns out to be a step back.
WORDS_THIS_TURN = "words_this_turn"


# The record this turn put in place, and what it is a detail of.
TURN_TOPIC = "topic_this_turn"


def note(memory, text, kind=None):
    """File the line, and note what filing it put on the record the chat is on.

    The words a line adds are what the next line is looked up with, so they are worth keeping
    ("does beer work" after the slugs is still about the slugs). But the reply to that line can be
    a step back - "I don't know enough to answer that honestly" - and then nothing about the thing
    was answered: what the turn added is taken back once the reply is known, in
    `the_step_back_takes_its_words_back`.
    """
    _the_step_back_is_undone(memory)
    before = _the_words_before_the_turn(memory)
    previous = current(memory)
    record = _note(memory, text, kind)
    _the_words_this_turn(memory, before, record, previous)
    return record


def _the_reply_to_the_turn_before(memory):
    """What the bot said last, from the history the store keeps."""
    for turn in reversed(list(memory.get("turns") or ())):
        if isinstance(turn, dict) and turn.get("bot"):
            return str(turn.get("bot") or "")
    return ""


def _the_step_back_is_undone(memory):
    """Take back the words the turn before added when its reply was a step back.

    The reply is composed after the store has filed the line, so what the turn added is noted
    then and taken back here, at the start of the next turn. The store observes before any module
    answers, so the next line is still looked up with the record as it stood when the step back
    was the answer to the line before it.
    """
    if not (WORDS_THIS_TURN in memory or TURN_TOPIC in memory):
        return None
    said = _the_reply_to_the_turn_before(memory)
    if not said:
        memory.pop(WORDS_THIS_TURN, None)
        memory.pop(TURN_TOPIC, None)
        return None
    return the_step_back_takes_its_words_back(memory, said)


def _the_words_before_the_turn(memory):
    """The words each record holds, by the words of the line it came from."""
    held = {}
    for record in _the_records(memory):
        held[str(record.get("text") or "")] = list(record.get("words") or ())
    return held


def _the_records(memory):
    for record in [memory.get("topic")] + list(memory.get("topics") or ()):
        if isinstance(record, dict):
            yield record


def _the_words_this_turn(memory, before, record, previous):
    """Note what this turn added to the record, and which record it left in place."""
    memory.pop(WORDS_THIS_TURN, None)
    memory.pop(TURN_TOPIC, None)
    if not isinstance(record, dict):
        return
    said = str(record.get("text") or "")
    added = [word for word in (record.get("words") or ()) if word not in before.get(said, ())]
    if added:
        memory[WORDS_THIS_TURN] = {"text": said, "words": added}
    # What this turn put in place, and what it is a detail of: a detail's line becomes a topic of
    # its own pointing back with "of", and a reply that steps back must leave the chat where it
    # was rather than on a question nobody answered.
    memory[TURN_TOPIC] = {"text": said, "of": str(record.get("of") or ""),
                          "was": str(previous.get("text") or "") if isinstance(previous, dict) else ""}


def _a_step_back(reply):
    """True when the reply is one of the pools that say the bot cannot answer this."""
    from ..compose import fallback  # noqa: PLC0415 - compose imports the memory package
    try:
        return bool(fallback.is_a_hedge(str(reply or "").strip()))
    except Exception:  # noqa: BLE001 - a reply is never worth a failed turn
        return False


def _the_detail_steps_back(memory, reply):
    """Put back the thing the chat was on when this turn's detail about it was only stepped back from."""
    noted = memory.pop(TURN_TOPIC, None)
    if not isinstance(noted, dict) or not _a_step_back(reply):
        return None
    back = str(noted.get("of") or "") or str(noted.get("was") or "")
    if not back or back == str(noted.get("text") or ""):
        return None
    record = current(memory)
    if not isinstance(record, dict) or str(record.get("text") or "") != str(noted.get("text") or ""):
        return None  # the turn did not leave that record in place
    older = None
    for kept in (memory.get("topics") or ()):
        if isinstance(kept, dict) and str(kept.get("text") or "") == back:
            older = kept
    if not isinstance(older, dict):
        return None
    said = dict(older)
    memory["topic"] = said
    topics = memory.get("topics")
    if isinstance(topics, list):
        topics[:] = [other for other in topics if other is not older
                     and str((other or {}).get("text") or "") != back]
        topics.append(said)
    return said


def the_step_back_takes_its_words_back(memory, reply):
    """Undo this turn's word merge when the turn stepped back, so the next line is not looked up
    with words nobody answered."""
    _the_detail_steps_back(memory, reply)
    noted = memory.pop(WORDS_THIS_TURN, None)
    if not isinstance(noted, dict) or not _a_step_back(reply):
        return None
    words = list(noted.get("words") or ())
    if not words:
        return None
    # Every record holding that line, because the store keeps copies of a record: the current one
    # and an entry in "topics" can be two dicts with the same words, and the words a turn added
    # are on both of them.
    took_back = None
    for kept in _the_records(memory):
        if str(kept.get("text") or "") != str(noted.get("text") or ""):
            continue
        kept["words"] = [word for word in (kept.get("words") or ()) if word not in words]
        took_back = kept["words"]
    return took_back
