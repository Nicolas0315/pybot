"""Part 7 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from .topics_part_01 import (
    _a_part_of_the_record, _a_place_the_line_moves, _after_an_emergency, _asks_about_the_bot,
    _back_to, _names_a_place_of_its_own, _switches, _the_record_they_came_back_to, current, find,
    is_small_talk, keywords, words, PROCEED, ASK_CUE, STOPWORDS, WHO, stem, ASK_ONLY, ASK_PART,
    STAND_IN,
)
from .topics_part_02 import (
    _about_record, _adds_a_detail, _asks, _asks_an_aspect_of_the_thing, _asks_which_kind,
    _is_a_when_or_how_often, _keep_person, _only_adds_a_person_to_the_thing, _only_details,
    _only_names_the_constraint, _resume, _the_aim_without_its_deadline,
    _the_plan_a_correction_renames, _without_switchers, is_follow_up, return_target, _entry,
    key_subject, subject, topic_text, trouble,
)
from .topics_part_03 import (
    _a_detail_of_what_we_are_on, _reaches_another_thing, _key_words_of, _names_it,
    _subject_words_to_carry,
)
from .topics_part_04 import (
    IMPERATIVE,
)
from .topics_part_05 import (
    carried_topic, PET_WORD, PET_ONE,
)
from .topics_part_06 import (
    _names_another_subject, IT_IS_PART_OF_THE_PHRASE, POINTING_WORDS, _the_entry_answers_the_ask,
    _the_entry_is_about_the_thing, _the_thing_with_a_determiner, THING_ITSELF, WHAT_IT_COSTS,
    WORTH_DECIDING, a_placeholder_pronoun, SOMETHING_IS_BROKEN, _what_they_called_theirs, BABY_OF,
    carry_the_ask, leans_on_topic, widen,
)


def _note(memory, text, kind=None):
    """Record the line as the current topic when it is about something."""
    # A line can open by saying it is changing the subject ("ok changing the subject, im planning
    # a curry tonight"). The reading has already taken that clause off, and the words left are
    # what the conversation is on from here: kept as typed, "subject" is a school word, so the
    # next line ("what should i buy") was read against a school subject the person never raised
    # and got the university entry requirements while the curry sat one turn back.
    read = memory.get("understood")
    if isinstance(read, dict):
        aim_length = _the_length_of_the_aim(read, memory)
        if aim_length is not None:
            # "how long will it take" after an aim is about the aim, and the line itself names
            # nothing: left as it came in, the reading hands every reader the deadline the aim was
            # said against ("before the holiday") as the thing the "it" points at, and the length
            # of getting fit was answered with the package-travel rules.
            memory["understood"] = aim_length
            read = aim_length
    if isinstance(read, dict) and read.get("change_of_subject"):
        kept = " ".join(str(read.get("clean") or "").split())
        if kept:
            text = kept
    _keep_person(memory, text)
    if is_small_talk(text, kind):
        return None
    if _asks_about_the_bot(read):
        # "are you a real person", "are you a robot", "do you sleep" are questions about the bot,
        # not about something of theirs, so they open no topic: on main the bot question became
        # the conversation's subject and the next "what did we talk about" answered "We were on
        # the real person", a phrase nobody said. The reading is the understanding engine's own
        # (`about_bot`), so every shape of the question is covered and a line that also says
        # something of their own is untouched.
        return None
    moved_to = _a_place_the_line_moves(text)
    if moved_to:
        # "no we changed it to devon" is the subject put right, so the chat is about Devon from
        # here: the next line that names nothing ("what should we do there", "where should we
        # stay") is read against the place they are going to now. Kept as a detail of the old
        # subject, the guide kept answering about the place they had already left.
        record = {"turn": len(memory.get("turns") or []), "text": text.strip(),
                  "words": keywords(text)}
        previous = memory.get("topic")
        if isinstance(previous, dict) and previous.get("text") == record["text"]:
            return previous
        memory["topic"] = record
        topics = memory.get("topics")
        if not isinstance(topics, list):
            topics = memory["topics"] = []
        if not topics or topics[-1].get("text") != record["text"]:
            topics.append(record)
        return record
    target = return_target(text)
    if target:
        record = find(memory, target)
        if record:
            _resume(memory, record, target, text)
            return memory["topic"]
        if not _asks(target):
            # "back to the laptop" when no laptop was ever discussed: the line is about the
            # conversation, not about a new thing, so it must not become the topic.
            return current(memory)
    # The reading in memory["understood"] knows when a line leans back on the last one
    # ("should i do the potatoes in with it?"), which is a thing a word count cannot see.
    # understand.py observes at PRIORITY 10000, so this is the reading for the current line.
    leans = isinstance(read, dict) and bool(read.get("followup"))
    if is_follow_up(text, memory) or leans:
        record = current(memory)
        if record and not _after_an_emergency(memory):
            # "my knee hurts when i run" / "how long does chicken keep in the fridge" / "it hurts
            # more in the morning": the chat moved to the chicken, and this line names a word of
            # the record it left, so it is about that record again.
            back = _the_record_they_came_back_to(text, memory, record)
            if back is not None:
                return _back_to(memory, back, text)
        if record and not _after_an_emergency(memory) \
                and (not _names_another_subject(text, record, memory)
                     or _a_part_of_the_record(read, record)):
            if not _switches(text) or _only_details(text, record):
                extra = [w for w in keywords(_without_switchers(text))
                         if w not in record.get("words", [])]
                record["words"] = (list(record.get("words") or []) + extra[:4])[:12]
                return record
    # A line that only puts a number on the subject ("we've got about 6000 pounds" after the
    # wedding, "she's 78", "its about 6 hours") is a detail about it, not a new subject: the
    # conversation stays on the wedding, and a later "what can we cut" is read against it
    # rather than against the budget line, which says nothing a kitchen or a plan can answer.
    constraint = _only_names_the_constraint(text, memory)
    if (_adds_a_detail(text, memory) or _only_adds_a_person_to_the_thing(text, current(memory))
            or constraint):
        record = current(memory)
        if record is not None and not _after_an_emergency(memory):
            if constraint:
                # The budget is kept off the subject's words as well as out of its place: the
                # words are what the next ask is looked up with, and "my budget is 5k" put
                # "budget" into the used car's words, so "what should i check" found the
                # household budget card. A constraint is not part of what the thing is.
                return record
            extra = [w for w in keywords(text) if w not in record.get("words", [])]
            record["words"] = (list(record.get("words") or []) + extra[:4])[:12]
            return record
    if _is_a_when_or_how_often(text, memory):
        record = current(memory)
        if record is not None and not _after_an_emergency(memory):
            extra = [w for w in keywords(text) if w not in record.get("words", [])]
            record["words"] = (list(record.get("words") or []) + extra[:4])[:12]
            return record
    if _asks_which_kind(text, memory):
        record = _about_record(memory)
        if record and not _after_an_emergency(memory) and not _reaches_another_thing(text, memory):
            extra = [w for w in keywords(text) if w not in record.get("words", [])]
            record["words"] = (list(record.get("words") or []) + extra[:4])[:12]
            return record
    if _asks_an_aspect_of_the_thing(text, memory):
        record = current(memory)
        # The article in "what is the food like" names a side of the thing, not a thing of its
        # own, so `_names_a_thing_of_its_own` is not asked here - it reads "the food" as a new
        # subject and that is the reading this branch exists to undo. A place of its own still
        # moves the chat ("what is the food like in naples").
        if (record is not None and not _after_an_emergency(memory)
                and not _names_a_place_of_its_own(text, record, memory)):
            extra = [w for w in keywords(text) if w not in record.get("words", [])]
            record["words"] = (list(record.get("words") or []) + extra[:4])[:12]
            return record
    kept = _the_plan_a_correction_renames(memory, text)
    if kept is not None:
        return kept
    keys = keywords(text)
    if len(keys) < 2 and len(words(text)) < 4:
        # A short line can still be the thing the conversation is on. "im so tired" has one
        # content word and three words in it, and the understanding engine reads it as being
        # about sleep; the next line ("its been going on for weeks", "what should i do about
        # it?") is read against a subject that was never written down, so the follow-up had
        # nothing to lean on and was acknowledged instead of answered. The topic id the
        # reading already found is enough to keep the conversation there.
        read = memory.get("understood")
        labels = read.get("topics") if isinstance(read, dict) else None
        labels = [str(label) for label in (labels or ()) if label]
        if not labels:
            return None
        record = {"turn": len(memory.get("turns") or []), "text": text.strip(), "words": keys,
                  "id": labels[0], "label": labels[0]}
        previous = memory.get("topic")
        if isinstance(previous, dict) and previous.get("text") == record["text"]:
            return previous
        memory["topic"] = record
        topics = memory.get("topics")
        if not isinstance(topics, list):
            topics = memory["topics"] = []
        if not topics or topics[-1].get("text") != record["text"]:
            topics.append(record)
        return record
    detail = _a_detail_of_what_we_are_on(text, memory)
    record = {"turn": len(memory.get("turns") or []), "text": text.strip(), "words": keys}
    aim = _the_aim_without_its_deadline(text)
    if aim:
        # "im trying to get fit before the holiday" is a chat about getting fit, and the deadline
        # is when they want it by. Kept whole, the only noun the chat has is the holiday, so the
        # next line - "how long will it take" - leans on the holiday and comes back with the
        # package-travel rules. The aim is the subject; the deadline is in the turns and the store
        # still has it when a line names it.
        record["text"] = aim
        record["words"] = keywords(aim)
    if detail is not None:
        # The line says something about the thing the chat is on, not about a new thing: who it
        # is for, what it is made of, what it cannot have. It stays a topic of its own - the
        # answer it reached is real, and the line is still in the turns - but it points back at
        # the thing, so the next line ("how long will it take?", "can I make it the day
        # before?") is read against the cake and not against the nuts. Read against the nuts it
        # reaches nothing and the answer already given comes back: "Same as before: <the
        # allergy answer>".
        record["of"] = str(detail.get("text") or "")
    previous = memory.get("topic")
    if isinstance(previous, dict) and previous.get("text") == record["text"]:
        return previous
    memory["topic"] = record
    topics = memory.get("topics")
    if not isinstance(topics, list):
        topics = memory["topics"] = []
    if not topics or topics[-1].get("text") != record["text"]:
        topics.append(record)
    return record


def the_pronoun_written_as_what_it_stands_for(understood, memory):
    """This line with its pronoun replaced by the thing it stands for, or None.

    "im thinking of getting a dog" / "what about a cat instead" / "how long can they be left
    alone" is a question about the cat, and the understanding engine says so - the pronoun's
    slot holds "cat" - but the line itself names no thing, so no entry answered it and the
    person got a search hedge while the cat-alone row was one entry away. Carrying the topic's
    words *after* the line ("how long can they be left alone cat instead") reaches nothing: a
    subject belongs where the pronoun was, not a word on the end.

    Every pointer the reading has filled is tried in the slot it stands in, and the entry that
    comes back has to be keyed on the thing itself, so a fill that lands on an answer about
    something else is left alone. A line that already reaches an entry keeps it: the fill is
    only for a follow-up that names nothing the knowledge base knows.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = " ".join(str(understood.get("clean") or understood.get("text") or "").split())
    if not line:
        return None
    ref = understood.get("ref") if isinstance(understood.get("ref"), dict) else None
    if not isinstance(ref, dict):
        return None
    if understood.get("kind") != "question":
        # A line that reports what somebody does ("she asks where it is") is not a question with
        # a hole in it: filling it wrote "she asks where a nan is" and the line reached the
        # borrowing-from-family entry, so a chat about presents was answered with a loan.
        return None
    if any(phrase in line.lower() for phrase in PROCEED):
        return None  # "what should i do about it" carries on from the answer
    if any(phrase in line.lower() for phrase in IT_IS_PART_OF_THE_PHRASE):
        return None  # the pronoun is the phrase's own, not a pointer at a thing
    if _entry(line) is not None:
        return None  # the line reaches an entry as it stands, so nothing is missing
    last = memory.get("last_answer") if isinstance(memory.get("last_answer"), dict) else {}
    record = carried_topic(memory, line)
    topic_entry = _entry(str((record or {}).get("text") or "")) if record else None
    topic_domain = getattr(topic_entry, "domain", None) if topic_entry is not None else None
    for word in POINTING_WORDS:
        thing = ref.get(word)
        if not isinstance(thing, str):
            continue
        thing = " ".join(thing.split())
        if not thing or thing.lower() in ("it", "that", "them", "they", "you", "me", "there"):
            continue
        if re.search(r"\b%s\b" % re.escape(thing.lower()), line.lower()):
            continue  # the thing is already in the line, so the pronoun is not standing for it
        if not re.search(r"\b%s\b" % word, line, re.IGNORECASE):
            continue
        for phrase in _the_thing_with_a_determiner(thing):
            filled = re.sub(r"\b%s\b" % word, phrase, line, count=1, flags=re.IGNORECASE)
            filled = " ".join(filled.lower().split())
            entry = _entry(filled)
            if entry is None:
                continue
            if not _the_entry_is_about_the_thing(entry, thing.split()[-1].lower()):
                continue
            if not _the_entry_answers_the_ask(entry, filled):
                continue
            if topic_domain and getattr(entry, "domain", None) != topic_domain:
                continue  # a fill that leaves the thing the chat is about is a fill into another
            if last.get("id") and entry.id == last.get("id"):
                continue  # the fill lands back on the answer they already have
            reading = dict(understood)
            reading["clean"] = filled
            reading["words"] = words(filled)
            if "norm_text" in reading:
                reading["norm_text"] = filled
            return reading
    return None


def the_thing_it_is(understood, memory):
    """A follow-up ask with a pronoun in it, read with the thing the store holds, or None.

    "what should I feed it" after "my cat is called Fish" names nothing the knowledge base can
    answer: carrying the topic's words gives "what should i feed it cat", which reaches no
    entry, so the turn fell to a search hedge with the answer one entry away. The store knows
    what the thing is, so the pronoun takes its place: "what should I feed my cat".

    Only where the filled ask reaches an entry. A pointer is worth filling when there is
    something at the other end, and a wrong subject is worse than none, so every pointer that
    does not land exactly on an entry is left for the reply that can answer it honestly.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or not ASK_CUE.search(line.lower()) or not THING_ITSELF.search(line):
        return None
    if any(phrase in line.lower() for phrase in PROCEED):
        # "what should I do about it" carries on from the answer, not from the thing.
        return None
    if WORTH_DECIDING.search(line) or a_placeholder_pronoun(line):
        return None
    if not WHAT_IT_COSTS.search(line):
        # Every other ask keeps the reader it had: the animal named on the line before, and
        # nothing guessed out of the chat's subject.
        thing = the_pet_the_line_before_named(memory)
        if not thing:
            return None
        filled = THING_ITSELF.sub(thing, line, count=1)
        if _entry(filled) is None:
            return None
        reading = dict(understood)
        reading["clean"] = " ".join(filled.lower().split())
        reading["words"] = words(reading["clean"])
        return reading
    if _entry(line) is not None:
        # The ask reaches an entry as it stands, so the pronoun is not the thing that is missing:
        # "how much will it cost to fix" is the price of the repair, not the price of whatever
        # the chat is on, and filling the pronoun in it answered a MOT with the MOT fee.
        return None
    last = memory.get("last_answer") if isinstance(memory, dict) else None
    last_id = last.get("id") if isinstance(last, dict) else None
    for thing, word in _the_things_the_pronoun_stands_for(memory, line):
        filled = THING_ITSELF.sub(thing, line, count=1)
        entry = _entry(filled)
        if entry is None:
            continue
        if not _the_entry_is_about_the_thing(entry, word):
            continue
        if not _the_entry_answers_the_ask(entry, filled):
            continue
        if last_id and entry.id == last_id:
            # The fill lands back on the answer they already have, so the pronoun is not the
            # thing that is missing: "my garden is overgrown" then "is it expensive to sort
            # out" is a new ask, and the answer they have, said again with "Same answer, and it
            # covers this" in front of it, is not the reply to it.
            continue
        reading = dict(understood)
        reading["clean"] = " ".join(filled.lower().split())
        reading["words"] = words(reading["clean"])
        return reading
    return None


def _the_things_the_pronoun_stands_for(memory, line):
    """What the pronoun in this line can stand for, the likeliest first, as (phrase, word).

    The animal named on the line before comes first, because that is what "it" means in a pet
    chat ("how often should I walk it") and it is the word they used. The chat's own subject
    comes next, because a pronoun in a chat that is not about an animal points at the subject:
    "im going to lisbon in may" then "is it expensive" is a question about Lisbon, and with only
    the animal read here the store had nothing to fill and the turn fell to a search hedge
    while "is lisbon expensive" was answered one entry away.
    """
    out = []
    pet = the_pet_the_line_before_named(memory)
    if pet:
        out.append((pet, pet.split()[-1]))
    record = carried_topic(memory, line)
    text = " ".join(str((record or {}).get("text") or "").lower().split())
    if not text or SOMETHING_IS_BROKEN.search(text):
        # A broken thing's "is it expensive" is a question about the repair, not about the thing:
        # "my washing machine is broken" then "is it expensive" is answered by the checks worth
        # doing before anyone is paid, and filling the pronoun took that turn to the cost of a
        # wash at 30C. The thing a chat is on is put in a pronoun's place when the chat is about
        # getting one or going somewhere, and a fault is left to the answer that knows it.
        return out
    said = " " + text
    mine = _what_they_called_theirs(said)
    if mine:
        # What the chat calls theirs is what the pronoun stands for, and nothing else is tried:
        # "my laptop has started making a loud fan noise" then "is it worth repairing or should i
        # replace it" is about the laptop, and filling the noise's "fan" answered a laptop
        # question with the cost of running a room fan.
        return out + [pair for pair in mine if pair not in out]
    for word in key_subject(text, memory):
        if word in words(line):
            continue                      # the line names it already, so nothing to fill
        phrase = word
        if " my " + word in said or text.startswith("my " + word):
            phrase = "my " + word
        elif " the " + word in said or text.startswith("the " + word):
            phrase = "the " + word
        if (phrase, word) not in out:
            out.append((phrase, word))
    return out


# A yes/no about what the thing in hand is like, asked with only a pronoun standing in for it:
# "is it expensive" after "i'm going to rome in may", "is that expensive" after a bike they are
# thinking of buying. The knowledge base has no entry for the pronoun and does have one for the
# filled ask ("is rome expensive" is the cost table's Rome row), so the line was answered with
# whatever answer the chat already had - "Same as before: In Rome: the Colosseum..." - or with a
# shrug ("Alright then - good luck with it.").
WHAT_IT_IS_LIKE = frozenset("""
    expensive cheap pricey costly affordable far near close long short quick slow fast easy hard
    difficult simple complicated warm hot cold wet dry busy crowded quiet noisy loud heavy light
    big small tall serious dangerous risky safe legal allowed normal common free fresh healthy
    filling fattening spicy sweet salty sour stale raw ready open tidy good bad better worse fine
""".split())


# The pronoun that stands for the thing itself: "is it expensive", "are they any good", "is that
# one safe". A pronoun about a person ("is she expensive") is not this turn, and `WHO` below is
# where a chat about somebody else is kept out.
WHAT_STANDS_IN = re.compile(r"\b(?:it|its|they|them|that|this|those|these)\b", re.I)


STANDS_IN = frozenset("it its they them that this those these".split())


# The words that ask what something costs, whatever else the line says: they are asked as a money
# question, which is how the knowledge base's price rows are keyed.
MONEY = frozenset("""
    expensive cheap cheaper pricey costly affordable dear reasonable spend afford price cost costs
""".split())


# The line has to be the yes/no itself, not a longer question that happens to hold a pronoun:
# "is it expensive in june" names a month of its own and is left alone.
YES_NO = re.compile(
    r"^\s*(?:(?:and|but|so|ok|okay|then|also|now|hmm|oh)\s+|what\s+about\s+|how\s+about\s+)?"
    r"(?:is|are|was|were|will|would|do|does|did|should|can|could|any)\b", re.I)


# How a prognosis is asked of the thing in hand, word for word. The pronoun asks it and the
# words after it say what is to become of the thing rather than what it is like: "will it go away
# on its own" after a cough, "will it clear up", "will that heal", "will it last". The knowledge
# base has no row for "will cough get better" and does have one for "how long does a cough last",
# so the ask is written out in the wording that reaches the row about how long the thing goes on,
# which is the answer the person is after. The value is the phrase that row is keyed on, so
# "get" and "improve" are asked as "get better" whether the line says better or not.
PROGNOSIS = {
    "go": "go away", "goes": "go away", "going": "go away", "gone": "go away",
    "away": "go away", "clear": "clear up", "clears": "clear up", "clearing": "clear up",
    "heal": "heal", "heals": "heal", "healing": "heal", "settle": "settle",
    "settles": "settle", "last": "last", "lasts": "last", "lasting": "last",
    "get": "get better", "gets": "get better", "getting": "get better",
    "improve": "get better", "improves": "get better", "pass": "pass",
    "passes": "pass", "fade": "fade", "fades": "fade", "down": "go down",
}


def the_prognosis_the_line_asks(understood, memory):
    """A bare "will it get better / go away / clear up / heal / last", read as the prognosis of
    the thing the chat is on, or None.

    A person who has just said they have a cough asks the question a friend answers without being
    asked twice: will it go away on its own. Nothing in the line names the cough but the pronoun,
    so the reading reached no entry, and the turn was a search hedge - "That's beyond what I know
    well, sorry" - with the row that says most coughs settle in two to three weeks one lookup
    away. The same held for a cold, a verruca, a burn and a sprain, which is the shape of the ask
    rather than any one topic: the pronoun plus a word of becoming.

    Three things decide whether the row may be handed over, because the prognosis of whatever the
    pronoun last pointed at is a wrong answer, and worse than the honest hedge:

    * the thing is one word. The ask is built out of what the store keeps as the thing, and the
      store keeps a phrase when the person described something: "i planted tomatoes in pots" is
      kept as "planted tomatoe pot", and "the warranty runs out in march" as "warranty run march".
      Asked as a question, those reached the billiards card ("Cue games are won with the cue
      ball, not the pot") and the running plan ("Three runs a week is plenty to start"). A
      condition a prognosis is asked about is named in a word - a cough, a cold, a bruise.
    * the row is keyed on how long the thing goes on. The ask is written so it reaches that row,
      and the row it reaches is only the answer when its own key says so: the general card about
      the thing says what the card the person has just read says, which is how "will it go away"
      about a verruca came out as a third telling of one fact.
    * it is not the answer already on the screen.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or not YES_NO.search(line) or not WHAT_STANDS_IN.search(line):
        return None
    said = words(line)
    outcomes = [PROGNOSIS[word] for word in said if word in PROGNOSIS]
    if not outcomes:
        return None
    # A line that names something of its own has its own subject, so it is not the pronoun's
    # to take: "will the dog get better" is the dog's question, asked in full.
    left = [word for word in said
            if word not in STOPWORDS and word not in STANDS_IN and word not in PROGNOSIS
            and word not in WHAT_IT_IS_LIKE]
    if left:
        return None
    if isinstance(memory.get("person"), dict) and memory.get("person"):
        return None  # the chat is about somebody, and their pronouns are not the thing's
    thing = subject(memory)
    named = words(thing) if thing else []
    if len(named) != 1 or set(named) & WHO:
        return None
    word = named[0]
    already = _entry(topic_text(memory))
    # The words the person used, then the plainest two ways the row is kept ("how long does it
    # last"): "will it go away" about a verruca lands on the pharmacy treatment, which is the
    # answer on the screen, and the row about how long they go on is the one that answers.
    for outcome in dict.fromkeys(outcomes + ["last", "get better"]):
        for written in _the_thing_as_a_question_names_it(named):
            if outcome == "last":
                ask = "how long does " + written + " last"
            else:
                ask = "how long does " + written + " take to " + outcome
            entry = _entry(ask)
            if entry is None:
                continue
            if not _the_entry_is_about_the_thing(entry, word):
                continue
            if not _keyed_on_how_long(entry):
                continue
            if already is not None and entry.key == already.key:
                continue  # the answer on the screen already is this answer
            reading = dict(understood)
            reading["clean"] = " ".join(ask.split())
            reading["words"] = words(reading["clean"])
            if "norm_text" in reading:
                reading["norm_text"] = reading["clean"]
            return reading
    return None


# The words an entry's key is written in when the entry answers how long the thing goes on. The
# ask is written in the same words, so this is the row answering the question that was asked
# rather than a card about the thing: "how long does a cough last" is keyed on weeks and months,
# and the general warts card is keyed on "what", "how" and "treat".
HOW_LONG_KEY = frozenset([
    "how long", "last", "lasts", "lasting", "duration",
    "week", "weeks", "month", "months", "day", "days", "long",
])


def _keyed_on_how_long(entry):
    """Whether the entry the prognosis ask reached is the row about how long the thing goes on."""
    return any(phrase in group for group in getattr(entry, "key", ())
               for phrase in HOW_LONG_KEY)


def _the_thing_as_a_question_names_it(named):
    """The thing as a question of its own would name it: as it was said, then with an article.

    "i have a cough" puts "cough" in the store with no article, and the row is keyed on "how long
    does a cough last": both are tried, the words they used first.
    """
    whole = " ".join(named)
    if named[0] in ("my", "a", "an", "the", "his", "her", "our", "their", "your"):
        return [whole]
    return [whole, "a " + whole, "the " + whole]


def the_property_of_the_thing(understood, memory):
    """A bare yes/no about what the thing in hand is like, read with that thing in it, or None.

    "is it expensive" after a trip to Rome is the cost question about Rome: the store knows the
    chat is about Rome, and the knowledge base answers "is rome expensive" with the price row.
    Filling the pronoun is what turns a follow-up the bot could only repeat itself over into the
    question the person asked.

    Only where the filled ask reaches a different entry than the answer already given: when the
    pronoun's place is filled and the same entry comes back, the answer would be the one they
    have just read, which is what this is here to stop. A wrong subject is worse than none, so
    every fill that does not land on another entry is left to the reply that can answer honestly.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or not YES_NO.search(line) or not WHAT_STANDS_IN.search(line):
        return None
    said = set(words(line))
    if not said & WHAT_IT_IS_LIKE:
        return None
    # Everything the line says besides a property word and the pronoun it points with: a line that
    # names something of its own has its own subject, so it is not the pronoun's to take.
    left = [w for w in words(line)
            if w not in WHAT_IT_IS_LIKE and w not in STOPWORDS and w not in STANDS_IN]
    if left:
        return None
    if isinstance(memory.get("person"), dict) and memory.get("person"):
        return None  # the chat is about somebody, and their pronouns are not the thing's
    thing = subject(memory)
    if not thing or set(words(thing)) & WHO:
        return None
    item = None
    already = None
    looked = 0
    fallback = None
    money = bool(set(words(line)) & MONEY)
    for candidate in _fills_from_the_things(line, understood, thing, memory):
        looked += 1
        if looked > LIKE_LOOKUPS:
            # A knowledge lookup is the expensive part of a turn, and four is already more than
            # a line this short is worth: the thing the chat is about, then the words of its key.
            break
        found = _entry(candidate)
        if found is None:
            continue
        if already is None:
            already = _entry(topic_text(memory))
        if already is not None and found.key == already.key:
            continue  # the answer in hand already is this answer
        if money and not (_key_words_of(found) & MONEY):
            # "my car failed its mot on a broken spring" / "is that expensive" reaches the row
            # about what a failed MOT means, which is not what they asked: the money question is
            # answered by the row that is keyed on money (the MOT fee, the fitted price), so the
            # first row that only mentions the thing is kept as a last resort and the search goes
            # on past it.
            if fallback is None:
                fallback = (candidate, found)
            continue
        filled, item = candidate, found
        break
    if item is None and fallback is not None:
        filled, item = fallback
    if item is None:
        return None
    reading = dict(understood)
    reading["clean"] = " ".join(filled.lower().split())
    reading["words"] = words(reading["clean"])
    if "norm_text" in reading:
        reading["norm_text"] = reading["clean"]
    return reading


LIKE_LOOKUPS = 4


# A line that asks where the limit is and names nothing itself: "how much is too much", "how much
# is too much a day", "is that too much". The thing is the one the chat is on, and the knowledge
# base keeps the limit row keyed to that thing ("how much coffee is too much" is the caffeine row),
# so the ask is written out with the thing in it.
LIMIT_ASK = re.compile(
    r"\bhow (?:much|many)\b[^?.!]{0,24}?\btoo (?:much|many)\b|"
    r"\b(?:is|are|was) (?:it|that|this|they|these) too (?:much|many)\b", re.I)


# The words a limit ask may be made of and still name nothing of its own. "how much is too much a
# day" is the same ask about the same thing; "how much coffee is too much" names the coffee itself
# and is answered by the line alone, so it is not this reader's to widen.
THE_LIMIT_ITSELF = frozenset("""how much many is are was it that this they these too day days week
    weeks time of should shall i we you a an the have be can per""".split())


# The ask as the limit row is keyed: the thing first, and the words of its key beside it, so a
# thing said with its doing ("drink coffee") still reaches "how much coffee is too much".
# The last of them is the row's own name for the ask ("coffee limit"): a row about caffeine for
# babies now answers "how much coffee is too much" and "how much caffeine is too much" for anyone
# who asks, so the written-out ask alone no longer lands on the adult's limit. It is only taken
# when the row it reaches is keyed to the limit itself, so a card that says nothing about a limit
# cannot be reached this way.
THE_LIMIT = ("how much {thing} is too much", "how much {thing} a day is too much",
             "{thing} limit")


def the_limit_of_the_thing(understood, memory):
    """A bare "how much is too much" read with the thing the chat is on in it, or None.

    "i drink a lot of coffee" then "how much is too much" was answered "That's beyond what I know
    well, sorry. Searching for it will turn up better sources" - while the knowledge base has the
    caffeine row, keyed to exactly this ask once the coffee is in it. The person said no more and
    no less than "the coffee we are talking about", so the reading is the same question written
    out, and it is only taken when it lands on a row keyed to the limit words.

    Only a line that names nothing of its own is widened: "how much coffee is too much" is
    answered by the line itself, and a limit about somebody else ("how much should he have") is a
    different question and is left alone. The row it lands on has to be keyed to the limit its own
    self ("limit", "safe"), not merely to the words "too much": "i pay 45 a month for my phone and
    i barely use it" / "is that too much" is a judgement on a bill, and the row it reached there
    was the one about cutting the bill, whose paragraph answers a question nobody asked.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict) or not memory:
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or not LIMIT_ASK.search(line):
        return None
    if [word for word in words(line) if word not in THE_LIMIT_ITSELF and word not in STOPWORDS]:
        return None  # the line names its own thing, so the thing in hand is not what it asks about
    if isinstance(memory.get("person"), dict) and memory.get("person"):
        return None  # the chat is about somebody, and their limit is not theirs alone to guess at
    thing = subject(memory)
    if not thing or set(words(thing)) & WHO:
        return None
    already = _entry(topic_text(memory))
    seen = set()
    for candidate in _the_limit_written_out(line, thing, memory):
        if candidate in seen:
            continue
        seen.add(candidate)
        if len(seen) > LIKE_LOOKUPS:
            break
        found = _entry(candidate)
        if found is None:
            continue
        keyed = _key_words_of(found)
        if not (keyed & {"limit", "limits", "safe"}):
            continue  # not a row about where the limit is
        if already is not None and found.key == already.key:
            continue  # the answer in hand already is this answer
        reading = dict(understood)
        reading["clean"] = candidate
        reading["words"] = words(candidate)
        if "norm_text" in reading:
            reading["norm_text"] = candidate
        return reading
    return None


def _the_limit_written_out(line, thing, memory):
    """The ask with the thing in it, the thing's own name before the doing word beside it.

    The store keeps the gist of the line that put the thing in hand there, so "i drink a lot of
    coffee" leaves "drink coffee": the limit row is keyed to the coffee, not to the drinking, and
    a single word of the gist that is not a verb is the thing's own name.
    """
    whole = " ".join(str(thing or "").split())
    named = [word for word in whole.split() if not _a_doing_word(word)]
    parts = named + [whole] + [word for word in whole.split() if word not in named]
    try:
        key = key_subject(line, memory)
    except Exception:
        key = []
    for word in key or ():
        if isinstance(word, str) and word.strip() and word.strip() not in parts:
            parts.append(word.strip())
    for one in parts:
        for said in THE_LIMIT:
            yield said.format(thing=one)


def _a_doing_word(word):
    """True for a word that says what is done rather than what it is done to ("drink", "put")."""
    from ..understanding import kinds  # local: the reading's own lists, not a second guess
    return word in kinds.VERB_FORMS or word in kinds.VERBISH


def _fills_from_the_things(line, understood, thing, memory):
    """Every ask the line means, the gist of the thing first and then the words of its key.

    The store's word for the thing in hand is the gist of the line that put it there - "car failed
    mot broken", "washing machine making bang" - and the price entries are keyed on the short
    noun: "how much does a car failed mot broken cost" is nothing, and "how much does mot cost"
    is the MOT fee. `key_subject` is the entry's own subject, so it is the second thing to write
    the ask with.
    """
    seen = set()
    things = [thing]
    try:
        key = key_subject(str(understood.get("clean") or understood.get("text") or ""), memory)
    except Exception:
        key = []
    for word in key or ():
        if isinstance(word, str) and word.strip():
            things.append(word)
    for one in things:
        for ask in _fills(line, one):
            if ask not in seen:
                seen.add(ask)
                yield ask


def _fills(line, thing):
    """The asks the line means, written out with the thing in it, best first.

    "is it expensive" about a banging boiler is the question a person asks before ringing an
    engineer: what will this cost. Written as "is boiler expensive" the price rows come second
    to the running-cost ones, because both rows are keyed on the machine and the dear word; the
    money phrasing reaches the fitted-price row the question is about. So a money word is asked
    as a money question, and everything else keeps the yes/no the person typed.

    Two asks at most: a knowledge lookup is the expensive part of this, and the second wording
    is only there for the rows the first one misses.
    """
    whole = " ".join(str(thing).split())
    said = WHAT_STANDS_IN.sub(whole, line, count=1)
    if set(words(line)) & MONEY:
        return ["how much does " + whole + " cost", "is " + whole + " expensive"]
    return [said]


# A line whose subject is a bare "he" or "she": the pronoun, with the filler that can come
# before it, is the thing to put the animal in place of. A written-out contraction ("he's
# scared of the car", "shes 12") is left alone: the pronoun is not a word of its own there, and
# putting the animal in front of the tense would write "my dog 's scared of the car".
HE_OR_SHE_OPENS = re.compile(
    r"^(?P<lead>(?:and |so |but |well |ok |okay |also )?)(?P<pron>he|she)\b(?!')", re.I)


# A follow-up about the airport that never says the word. "im flying to dublin next week" then
# "how early do i need to be there" reached no entry at all - "there" is not a place - and every
# widening with the topic's own words reached the *destination* entry instead (Dublin's sights),
# so the arrival answer was never given and the turn went to the composer's honest hedge. The
# flight in the topic is the only place "there" can be, so the line is read with the airport in it.
ASKS_HOW_EARLY_THERE = re.compile(
    r"\b(?:how early|how long before|what time (?:should|do|shall|must) i|"
    r"when (?:should|do|shall|must) i)\b", re.I)


A_FLIGHT_IN_THE_TOPIC = re.compile(
    r"\b(?:flight|flights|flying|fly|airport|terminals?|departure|departing|plane|boarding)\b",
    re.I)


THE_AIRPORT = "at the airport"


def the_airport_there_is(understood, memory):
    """A question about how early to be there, in a chat about a flight, read as the airport.

    Only when the line asks about the time and the pronoun is all the place it names: a line that
    names where ("how early should i be at the airport") is already answered from its own words,
    and one that asks about anything else ("how long does it take to get there") is a different
    question. The filled line also has to reach an entry of its own, and not the one in hand, so
    this can only add an answer where the line had none.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or "there" not in words(line) or not ASKS_HOW_EARLY_THERE.search(line):
        return None
    trip = topic_text(memory)
    if not trip or not A_FLIGHT_IN_THE_TOPIC.search(trip):
        return None
    filled = re.sub(r"\bthere\b", THE_AIRPORT, line, count=1, flags=re.I)
    if filled == line:
        return None
    found = _entry(filled)
    if found is None:
        return None
    already = _entry(trip)
    if already is not None and found.key == already.key:
        return None  # the answer in hand is this answer
    reading = dict(understood)
    reading["clean"] = " ".join(filled.lower().split())
    reading["words"] = words(reading["clean"])
    if "norm_text" in reading:
        reading["norm_text"] = reading["clean"]
    return reading


def the_animal_the_subject_is(understood, memory):
    """A line whose subject is a bare "he"/"she", read with the animal the chat is on, or None.

    "we got a puppy last week" then "he keeps biting the kids" is the puppy biting: the pronoun
    was read as the animal (the understanding engine points it there, because the store holds a
    puppy and no person), but nothing put it back into the question, so the line reached the
    entry for a child who bites at nursery and the person got advice about a toddler. Read with
    the animal it is "my puppy keeps biting the kids", which is the answer they asked for.

    Only when the reading itself points the pronoun at an animal the store holds, and only when
    the filled line lands on an entry that names that animal: a person the chat is on ("my son
    is 8" then "he keeps biting the kids") points the pronoun at the son, so the line is left
    alone, and an animal with nothing to say about the trouble buys nothing either.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or PET_WORD.search(line):
        return None  # the line names the animal already, so its own reading is the answer
    opens = HE_OR_SHE_OPENS.match(line)
    if opens is None:
        return None
    ref = understood.get("ref") if isinstance(understood.get("ref"), dict) else {}
    who = str(ref.get("he") or ref.get("she") or "")
    if not who or not PET_WORD.search(who):
        # Who "he" is has to be an animal for the store to put one in the line. A person
        # ("my husband is 40") is not this reader's business.
        return None
    thing = the_pet_the_line_before_named(memory) or _called(who)
    filled = opens.group("lead") + thing + " " + line[opens.end():].lstrip()
    item = _entry(filled)
    if item is None:
        return None
    if item is _entry(line):
        return None  # the same answer, so the reading that reached it is already right
    kind = thing.split()[-1].lower().rstrip("s")
    keyed = _key_words_of(item)
    if kind not in keyed and kind not in {stem(word) for word in keyed}:
        return None  # an entry about something other than the animal they keep
    reading = dict(understood)
    reading["clean"] = " ".join(filled.lower().split())
    reading["words"] = words(reading["clean"])
    return reading


# An answer about a child, which is not an answer about the animal in the chat. The words are
# the ones that only make sense for a person: "put the child down", "a teething baby", "back to
# nursery". A pet answer can mention children ("keep him away from the kids") and still be the
# pet's answer, so this is only ever asked together with the wider question below, which wants
# the filled line to reach an entry keyed on the animal.
CHILD_CARE = re.compile(
    r"\b(?:child|children|baby|babies|toddler|toddlers|kid|kids|nursery|nappy|nappies|cot|"
    r"pushchair|highchair|breastfeed\w*|childminder|schoolchild)\b", re.I)


def _the_kind_of_animal(text):
    """The animal a line or an answer names, as the family word: a puppy is a dog."""
    found = set()
    for word in PET_WORD.findall(str(text or "")):
        word = PET_ONE.get(word.lower(), word.lower()).rstrip("s")
        found.add(BABY_OF.get(word, word))
    return found


def answers_about_another_creature(answer, what_the_line_is):
    """True when the answer in hand is about a person or another animal than the one the chat is on.

    "we got a puppy last week" then "he keeps biting the kids" gets the entry for a child who
    bites at nursery: the advice is real and tells the person to put their child down, which is
    nothing to do with a puppy. The same line read with the puppy reaches the puppy's own entry,
    and that one is the answer. The question is only ever asked when the filled line already
    reaches an entry keyed on the animal (`the_animal_the_subject_is`), so what is left to
    decide is whether the answer in hand fits the animal at all.

    A line whose own answer is about the animal in the chat keeps it: after "i cant sleep since
    we got the puppy", "he cries when i leave the room" is answered from the entry for a baby's
    separation anxiety, and that advice - short practice exits, always coming back - is the
    right answer for a puppy too, so it is not thrown away for the one on leaving a dog alone.
    """
    said = " ".join(str(answer or "").split()[:60])
    if not said:
        return False
    if CHILD_CARE.search(said):
        return True
    kind = _the_kind_of_animal(what_the_line_is)
    named = _the_kind_of_animal(said)
    return bool(named) and not (kind & named)


def _called(who):
    """"my dog" from the animal the reading points at, which the reading may already say "my" in."""
    who = " ".join(str(who or "").strip().lower().split())
    if not who:
        return ""
    return who if who.split()[0] in {"my", "our", "the", "a"} else "my " + who


def _the_pet_the_turns_before_named(memory, back=3):
    """"my puppy" when the puppy was named a turn or two before, else "".

    "and the biting" three lines into a puppy chat names no animal at all, so the pronoun rule's
    one turn is too short and the newest animal the person named is what the line is about. Only
    a few turns back: a pet named before a change of subject is not what a bare detail ask means
    now, and a line with an animal of its own never comes here.
    """
    thing = the_pet_the_line_before_named(memory)
    if thing:
        return thing
    turns = memory.get("turns") if isinstance(memory.get("turns"), list) else []
    user = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    lines = []
    for turn in reversed(turns):
        said = turn.get("user") if isinstance(turn, dict) else None
        if isinstance(said, str) and said.strip():
            lines.append(said)
        if len(lines) > back:
            break
    for line in lines[1:back + 1]:
        # The same reading the one-turn rule does, on an earlier line of the chat.
        found = the_pet_the_line_before_named({"turns": [{"user": line}], "user": user})
        if found:
            return found
    return ""


def a_detail_of_the_thing_we_hold(understood, memory):
    """"the chewing" when that is a detail of the animal the store holds, and nothing else.

    The same reading `the_thing_a_detail_belongs_to` makes, without asking which entry the filled
    ask lands on: it says the line is about a detail of the animal they told us about, which is
    what tells an answer already given that the detail is what the line is asking about."""
    return bool(_the_kind_the_line_leaves_out(understood, memory))


def _the_kind_the_line_leaves_out(understood, memory):
    """(line, kind) when the line names a detail and leaves out the animal the store holds."""
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line or not ASK_CUE.search(line.lower()):
        return None
    # The line names the animal itself, so its own reading is the one to answer from.
    if PET_WORD.search(line) or any(phrase in line.lower() for phrase in PROCEED):
        return None
    thing = _the_pet_the_turns_before_named(memory)
    if not thing:
        return None
    kind = thing.split()[-1]
    if kind in words(line):
        return None
    return line, kind


def the_thing_a_detail_belongs_to(understood, memory):
    """The ask read with the kind of thing the store holds, when the ask names only a detail.

    "we got a puppy called Biscuit" then "how do I stop the chewing" names the trouble and not
    the animal, and on its own "the chewing" reaches the answer about chewing a pen at a desk -
    a confident answer about the wrong thing. The store knows what the thing is, so its kind is
    put beside the detail: "how do I stop the chewing puppy" reaches the puppy's own entry. The
    same holds for a cat, a dog or a rabbit called anything at all, because the kind is read from
    the store and never from the line.

    Only where the filled ask lands exactly on an entry keyed to the kind the line has not
    named, so a line that names its own subject ("how do I stop the slugs" after a puppy) and a
    detail that belongs to nothing the store holds are both left to the reading they already
    have.
    """
    found = _the_kind_the_line_leaves_out(understood, memory)
    if not found:
        return None
    line, kind = found
    filled = line + " " + kind
    item = _entry(filled)
    if item is None:
        return None
    # The entry has to be the one the kind and the detail are both part of: "chew" is what the
    # line asks about and "puppy" is what the store holds. An entry that only the detail reaches
    # is the one the line already had, and one that only the kind reaches has not been asked.
    keyed = _key_words_of(item)
    if kind not in keyed and stem(kind) not in keyed:
        return None
    # What the line says about the trouble, in the words that name it: the ask ("how do I") and
    # the verb that carries it ("stop", "get rid of") are how the question is put and not what it
    # is about, and an entry can be reached on one of those alone. A cat with a chewing ask
    # reaches the cat-keeping-out-of-the-garden entry through its own "stop", and its advice is
    # about soil rather than about a cat that chews. So the trouble has to be named by the line.
    said = [word for word in words(line)
            if word not in ASK_PART and word not in ASK_ONLY and word not in STAND_IN
            and word not in STOPWORDS]
    trouble = [word for word in said if word not in IMPERATIVE]
    if not _names_it(trouble or said, item):
        return None
    reading = dict(understood)
    reading["clean"] = " ".join(filled.lower().split())
    reading["words"] = words(reading["clean"])
    return reading


def the_pet_the_line_before_named(memory):
    """"my cat" when the line before named a pet the store holds, else "".

    The thing a pronoun points at is what the line before it named: "how often should I walk it"
    straight after "I have a dog". A pet mentioned ten turns ago is not what "it" means now -
    "my boiler is broken" then "how much will it cost" is about the boiler, and filing the cat
    into that line would answer a different question.
    """
    turns = memory.get("turns") if isinstance(memory.get("turns"), list) else []
    before = ""
    for turn in reversed(turns):
        said = turn.get("user") if isinstance(turn, dict) else None
        if isinstance(said, str) and said.strip():
            before = said
            break
    if not before:
        return ""
    # The word they used, not the family it belongs to: "what should I feed my kitten" is the
    # kitten's answer, and filling "my cat" in its place would give the adult cat's.
    named = {}
    for word in PET_WORD.findall(before):
        word = PET_ONE.get(word.lower(), word.lower())
        named.setdefault(BABY_OF.get(word, word), word)
    user = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    # A breed is the animal it is. "we are getting a rescue greyhound next week" names no word
    # PET_WORD knows, so "how much exercise does it need" had nothing to point at and the ask fell
    # to the search hedge while the store held the dog. The animal's own word is the one an entry
    # is keyed on, so that is what goes in the line; a breed said as something else ("the
    # greyhound bus") is not an animal and `a_frame_before` is what knows the difference.
    # A puppy in the store is a dog too, and the puppy's own entry is the one that answers a puppy
    # question: "we just got a puppy" / "hes a labrador, 9 weeks old" / "how much should i be
    # feeding him" got the adult dog's 2% guide once the breed filled the line, where the word
    # they used - the puppy - reached the four-small-meals answer. So a kind the store holds as a
    # baby is left to the baby word.
    babies = set()
    for pet in user.get("pets") or []:
        if not isinstance(pet, dict):
            continue
        kind = str(pet.get("animal") or "").strip().lower().rstrip("s")
        if kind in BABY_OF:
            babies.add(BABY_OF[kind])
    from ..understanding import breeds as _breeds
    for match in _breeds.BREED_RE.finditer(before):
        if not _breeds.a_frame_before(before, match.start()):
            continue
        kind = _breeds.the_kind_of(match.group(0))
        if kind and kind not in babies:
            named.setdefault(kind, kind)
    if not named:
        return ""
    for pet in reversed(user.get("pets") or []):
        if not isinstance(pet, dict):
            continue
        kind = pet.get("animal")
        if not isinstance(kind, str) or not kind.strip():
            continue
        kind = BABY_OF.get(kind.strip().lower().rstrip("s"), kind.strip().lower().rstrip("s"))
        if kind in named:
            return "my " + named[kind]
    return ""


# "How do I keep it up?" is the question of carrying on with the thing in hand, and those words
# are the whole of the ask: after "im learning spanish" the line names no subject for the
# knowledge base to reach, so the search hedge is the reply, and after an answer it is handed the
# answer it has already had ("Same as before: ..."). Said as the question it is, the entry that
# holds the answer - keep it small and scheduled, track the days you show up - is reached.
KEEP_IT_UP = re.compile(
    r"\bhow\s+(?:do|can|should|would|could)\s+i\s+"
    r"(?:keep\s+(?:it|this|that)\s*(?:up|going|on)?|"
    r"keep\s+(?:going|on|at\s+it)|"
    r"keep\s+on\s+(?:with\s+)?(?:it|this|that)|"
    r"stick\s+(?:with|at|to)\s+(?:it|this|that)|"
    r"stay\s+(?:with|at)\s+(?:it|this|that))\b", re.I)


# The words the ask becomes. "stay motivated" is what the answer to carrying on is keyed to, and
# nothing else about the ask is changed.
STAYING_WITH_IT = "how do i stay motivated"


# The topic in hand has to be something they are learning or practising - "im learning spanish",
# "i started learning spanish last week", "im playing the piano", "im writing a novel". Only then
# is "how do i keep it up" a question about carrying that on: after "my kitchen tap is dripping"
# the same words name nothing the bot can answer, and the honest hedge is the reply rather than
# advice about keeping a habit. A plan with its own steps ("im doing couch to 5k", "im trying to
# save money") is left out on purpose: its entry already answers a question about keeping going
# with the part of the plan that says so, and the general advice would be a worse reply there.
# The ask is the same whether the thing was started years ago, last week or not yet: "i started
# learning spanish last week" and "i want to learn spanish" are the topic being kept up, and
# reading only "im learning" left both of them with the previous answer handed back clipped.
AN_ACTIVITY = re.compile(
    r"\b(?:i'?m|i am|i'?ve been|i have been|i'?m still|i am still|"
    r"i'?ve started|i have started|i started|i began|i'?ve begun|i have begun|"
    r"i want to|i'?d like to|i'?m trying to|i am trying to|i'?ve been trying to)\s+"
    r"(?:learning|studying|practising|practicing|reading|writing|playing)\b|"
    r"\b(?:i'?m|i am|i'?ve been|i have been|i'?m still|i am still|i started|i'?ve started|"
    r"i began|i want to|i'?d like to|i'?m trying to|i am trying to)\s+"
    r"(?:learn|study|practise|practice|read|write|play)\b", re.I)


def _carrying_on(understood, memory):
    """The bare "how do i keep it up" as the carrying-on question, or None.

    Only when the topic in hand is an activity, and only for the ask that says nothing else: the
    reading is handed back with the question in place of those words and nothing else changed, so
    the sentence has one subject - carrying on - and the knowledge base answers it.
    """
    line = str(understood.get("clean") or understood.get("text") or "")
    found = KEEP_IT_UP.search(line)
    if not found:
        return None
    record = carried_topic(memory, line) or {}
    text = str(record.get("text") or "")
    if not text.strip() or not AN_ACTIVITY.search(text):
        return None
    text = (line[:found.start()] + STAYING_WITH_IT + line[found.end():]).strip()
    reading = dict(understood)
    reading["clean"] = " ".join(text.lower().split())
    reading["words"] = words(reading["clean"])
    if "norm_text" in reading:
        reading["norm_text"] = reading["clean"]
    return reading


# A whole line that takes something off the thing in hand and says nothing else: "no cheese
# though", "without the sauce", "skip the onions please". The thing it names is what is gone.
LIMIT_LINE = re.compile(
    r"^\s*(?:oh\s+|and\s+|also\s+)?(?:no|nope|not|without|skip|minus|except|but\s+no)\b"
    r"\s+(?P<thing>[a-z']{3,20}(?:\s+[a-z']{3,20}){0,2}?)"
    r"\s*(?:though|tho|then|please|for\s+me|thanks|sorry)?\s*[.!]*\s*$", re.I)


def _what_the_turn_took_away(record, memory):
    """The things a turn took off the thing in hand: "no cheese though" gives {"cheese"}.

    A limit is not a subject. The turn after one was widened with the thing that had just been
    taken away - "and how long does that take" after a frittata and "no cheese though" was read
    as how long the cheese takes - which reaches nothing, so the dish's own time, one entry away
    and already on the screen, was lost.
    """
    if not isinstance(record, dict):
        return set()
    said = " ".join(str(record.get("text") or record.get("user") or "").lower().split())
    found = LIMIT_LINE.match(said)
    if not found:
        return set()
    taken = set()
    for word in found.group("thing").split():
        if word in STOPWORDS or len(word) < 3:
            continue
        taken.add(stem(word))
    return taken


def _widened(line, understood, record, memory):
    """This line read with the record's subject put back in, or None when that reaches nothing."""
    from .when import asks_what_today_is

    if asks_what_today_is(line):
        # "what day is it" asks the calendar, and no subject of the chat goes into it: widened with
        # the trip in hand it read "what day is the portugal trip", and the Portugal card answered
        # a question about today. The calendar answers it where the calendar is read.
        return None
    if not isinstance(record, dict):
        return None
    topic_text = str(record.get("text") or "")
    if not topic_text.strip():
        return None
    taken = _what_the_turn_took_away(record, memory)
    if leans_on_topic(understood, memory):
        subject_words = _subject_words_to_carry(record, line, memory)
        if taken:
            subject_words = [word for word in subject_words
                             if stem(str(word).lower()) not in taken]
        if not subject_words or all(word in words(line) for word in subject_words):
            return None
        text = widen(line, subject_words, topic_text)
        if text is not None:
            return text
        # The topic's key words did not reach an entry, but the words of the topic the
        # knowledge base knows may: "why is that happening?" after a flat sourdough.
        return carry_the_ask(line, topic_text)
    # A line that names nothing of its own ("how often should I go?") is the same kind of
    # follow-up: it is read with the topic's words, or not at all.
    return carry_the_ask(line, topic_text)


def _the_length_of_the_aim(understood, memory):
    """This turn read as the length of the aim the chat is on, when it asks only a length.

    "im trying to get fit before the holiday" / "how long will it take": the line names nothing of
    its own, so the "it" is filled in from the topic - and the only noun the chat has is the
    deadline, so the length of getting fit is answered with the package-travel rules. The aim on
    the line before is what the length is about; `bot/memory/named.py` writes that question out
    ("how long does it take to get fit") and keeps it only where an entry answers a length, so a
    line that reaches nothing is still answered by whatever reaches it.
    """
    line = str(understood.get("clean") or understood.get("text") or "")
    if not line:
        return None
    try:
        from . import named

        asked = named.a_goal_measured(line, memory)
    except Exception:  # noqa: BLE001 - a reading that fails leaves the line as it was
        return None
    if not asked:
        return None
    reading = dict(understood)
    reading["clean"] = asked
    reading["words"] = words(asked)
    if "norm_text" in reading:
        reading["norm_text"] = asked
    return reading
