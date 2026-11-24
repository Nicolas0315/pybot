"""Part 2 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from ..understanding import lexicon
from .topics_part_01 import (
    NOT_DOING, STOPWORDS, stem, AIM_FRAME, A_DEADLINE, words, KIND_ASK, ASPECT_IS_A_PRONOUN,
    ASPECT_OF_IT, WHO, OWN_THING, _names_a_place_of_its_own, ABOUT_THE_PERSON, JOINS_THE_THING,
    PRONOUN_PERSON, MEASURE, ABOUT_ANOTHER, PART_OF_THE_ONE, PROPERTY, REFERRING, keywords,
    RETURN_ASKS, SWITCHERS, _LEADS_IN, ACKS, CORRECTION_NOISE, DETAIL_WORDS, A_THING_ON_ITS_WAY,
    FRESH_NAMES, NAMES_THE_THING, _after_an_emergency, current, SHORTHAND, NAMED_THING,
    RECENT_TURNS, WHEN_OR_AMOUNT, CONSTRAINT_IS, ON_A_BUDGET, FRESH_WORDS, MY_THING_IS, WHO_SAID,
    A_BARE_PRONOUN_SUBJECT, A_QUESTION_THEY_ASK, WHO_SAID_THIRD, about, A_CHILDS_PERSON,
    A_GROWN_AGE, A_JOB_AT, A_WORRY_AFTER, CHANGE, FALLS_FINE, FELL_OUT, PERSON_TROUBLE,
    REPEATED_SAID, SOMETHING_WRONG, YOUNG_PERSON, CORRECTION_LINE, WH_WORD_WITHOUT_ITS_APOSTROPHE,
    CASUAL_LEAD, CASUAL_OPEN, RETURN_LEAD, HELPER_ASKS, ING_VERBS, MODALS, VERB_PHRASE_AFTER,
    CASUAL_VERB, RETURN_TIME, _the_answer_on_the_return, CONTINUATION_START, GREET, LEAD_ACKS,
    _switches, _this_line, is_ack, context, _CONSIDERING, _HANDOFF_THROAT, _A_FIGURE, _DATE_FILLER,
    _DATE_OCCASIONS, _TIME_WORDS, _the_people, _MAKING_A_THING, ASK_ONLY, _BUYING_A_STATE,
    _CORRECTION_LEAD, _FRAME_ASK, _LEAD, _LEAD_QUESTION, _PHRASAL_RE, _RELATION, _WISH_RE,
    _WITHOUT_CLAUSE, _HOME_SPACES, _ROOM_LIMIT, ACTION, ACTION_AFTER, PERSON_LEAD, forms,
    DURATION_ASK, DURATION_WORDS, ATTRIBUTE_WORDS, A_STATE, NOT_A_THING, ONE_ATTRIBUTE,
    CAUSE_OF_THE_COMPLAINT, ASK_PART, find,
)


def _what_they_are_not_doing(text):
    """The words a line puts after a negation: "wont listen" gives {"listen"}."""
    out = set()
    for found in NOT_DOING.finditer(" ".join(str(text or "").lower().split())):
        word = found.group(1)
        if word and word not in STOPWORDS and len(word) >= 3:
            out.add(stem(word))
    return out


def _the_aim_without_its_deadline(text):
    """The aim a line states, without the deadline clause it is said against, or "".

    Empty for every line that is not an aim, and for an aim that names no deadline: the words of a
    line that has no later thing in it are already the thing it is about.
    """
    line = " ".join(str(text or "").strip().split())
    match = AIM_FRAME.match(line)
    if not match:
        return ""
    rest = line[match.end():]
    cut = A_DEADLINE.search(rest)
    if not cut:
        return ""
    aim = re.sub(r"^\s*to\s+", "", rest[:cut.start()], flags=re.I).strip(" .,;:-")
    words = aim.split()
    if not 1 <= len(words) <= 8 or not re.search(r"[a-z]{3}", aim, re.I):
        return ""
    return aim[0].upper() + aim[1:] if aim[:1].islower() else aim


def _asks_which_kind(text, memory):
    """True when the line asks which kind of the thing in hand, naming no thing of its own.

    "what breed is good with young children" after "im thinking of getting a dog for the kids"
    is a dog question: "what breed" is the word for the choice between dogs, not a thing of its
    own. Read as a subject of its own, the topic became "breed good young children", and the
    next line - "how much exercise does it need" - was answered from that instead of from the
    dog. Only a conversation that already has a subject folds the line into it: with nothing on
    the table the line is all there is, so it keeps its own record.
    """
    if not KIND_ASK.search(" ".join(str(text or "").lower().split())):
        return False
    return bool(subject(memory))


def _asks_an_aspect_of_the_thing(text, memory):
    """True when the line asks about a side of the thing the chat is on, naming nothing of its own.

    Only read inside a conversation that already has a subject, and never when the line brings a
    thing or a person of its own: "what is the food like in naples" moves the chat to Naples, and
    "how are the kids" is not an aspect of anything. The words of the aspect join the record's
    words, which is what the pronoun asks ("what spices go in it") already do, so the next ask is
    looked up with the thing still in it.
    """
    if not ASPECT_OF_IT.search(" ".join(str(text or "").lower().split())):
        return False
    if person(text):
        return False
    if any(word in ASPECT_IS_A_PRONOUN for word in words(text)):
        return False
    # "how are the kids" is not a side of anything: a person is a subject of their own, in the
    # plural too, and the store reads people by the same list everywhere else.
    if any(stem(word) in WHO for word in words(text)):
        return False
    return bool(subject(memory))


def _names_a_thing_of_its_own(text, record, memory=None):
    """True when the line turns the chat to a thing of its own ("my budget", "the kitchen")."""
    known = set(record.get("words") or [])
    for found in OWN_THING.finditer(" " + " ".join(words(text)) + " "):
        word = stem(found.group(1))
        if word in WHO or word in known:
            continue
        return True
    return _names_a_place_of_its_own(text, record, memory)


def _only_adds_a_person_to_the_thing(text, record):
    """True when the line adds a person to the thing the chat is on, rather than a subject.

    "my sister is coming too" after "im going to rome in june", and "he loves dinosaurs" after
    "my son is 7": the line names no thing a knowledge entry can answer, so it cannot be what the
    next one leans on. Kept as a topic of its own it became exactly that, and the ask after it -
    "what should i see?", "how long will it take?" - was read against a sister or a dinosaur,
    reached nothing, and the answer that was on the screen one turn earlier (the trip's
    sightseeing, the sponge's timings) turned into a search hedge. The person is part of the
    thing: their words join the thing's, and the chat stays on it.

    Two shapes count, both narrow: a person who joins the thing ("too", "as well", "coming",
    "with me"), and something said of the person the thing already names ("he loves ...", "she
    is into ...", a pronoun, with the record naming the person). A line that names a thing of
    its own is left to be a subject of its own, so "my budget is 600 pounds" after a laptop and
    "my car won't start" after a cake still move the chat.
    """
    if not isinstance(record, dict) or not record.get("text"):
        return False
    line = " ".join(words(text))
    if not line or len(line.split()) > 14:
        return False
    if _entry(text) is not None:
        # The line reaches an answer of its own (the cake's allergy variant, say): that answer is
        # about the thing, so the record stays a topic of its own that points back at it.
        return False
    named = person(text)
    theirs = person(record.get("text") or "")
    if named is None and theirs is None:
        return False
    if JOINS_THE_THING.search(line) and named is not None:
        return True
    return (ABOUT_THE_PERSON.search(line) is not None and theirs is not None
            and PRONOUN_PERSON.search(line) is not None)


def _another_area(text, said):
    """True when the two lines are read as different kinds of thing (bedwetting, Lisbon).

    A detail can well be in another area from the thing it is a detail of - "he is allergic to
    nuts" after a birthday cake is food about a cake - so this never refuses a detail on its
    own; it is the third check beside the line's own answer and the words that answer speaks.
    """
    if not said:
        return False
    from ..understanding import understand  # noqa: PLC0415 - understanding imports this package
    there = (understand(said, {}) or {}).get("topic_own")
    mine = (understand(text, {}) or {}).get("topic_own")
    if mine in MEASURE:
        return False  # "and how many days in kyoto" is a count of the trip, not another subject
    return bool(there and mine and there != mine)


def _leans_back(text, record):
    """True when the line points at the thing the chat is on: "with it", a measure of it, or a
    word the subject already has.

    A how-long or what-temperature question names no subject of its own ("how long for a 2kg
    chicken" after a roast), so the measure is what says it is still the same thing.
    """
    found = words(text)
    if any(word in REFERRING for word in found):
        return True
    if PROPERTY.search(" ".join(found)):
        return True
    if PART_OF_THE_ONE.search(" ".join(found)):
        return True
    if ABOUT_ANOTHER.search(" ".join(found)):
        return True
    return bool(set(keywords(text)) & set(record.get("words") or ()))


def _leads_a_question(text):
    """True when the line opens a question: "how long for a 2kg chicken", "should i ...?"."""
    found = words(text)
    return "?" in text or (bool(found) and found[0] in RETURN_ASKS)


def opens_by_switching(text):
    """True when the line opens by turning to another subject ("actually it's a funeral").

    A switch word in the middle of a line is not a switch: "what can i actually do to help her" is
    a follow-up about the thing on the table, "can i use oil instead of butter" asks about the
    butter, and "i might be sad, actually" is a feeling said again. Read as a turn away, that
    follow-up was left with no reading at all - "actually" is a word the person talks with, not a
    subject - and the answer about the arthritis sat one word away while the turn went to a search
    hedge. Only a line that says the turning first is turning.
    """
    low = _LEADS_IN.sub("", " ".join(words(text)))
    return any(low.startswith(switcher) for switcher in SWITCHERS)


def _without_switchers(text):
    """The line with the words that announce or excuse a correction taken out, so they are not
    content: "actually" and "sorry" say a correction is coming, not what it is."""
    parts = [part for switcher in SWITCHERS for part in switcher.split()]
    return " ".join(word for word in words(text)
                    if word not in parts and word not in CORRECTION_NOISE and word not in ACKS)


def _only_details(text, record):
    """True when everything a correction brings is a detail of the subject, not a new subject.

    "I'm going to a wedding in july" then "actually it's in august" is still the wedding, and
    the next line that names nothing ("what should I wear to that?") has to keep leaning on it.
    "Actually it's a funeral" replaces the occasion, so that line starts a new record instead.
    """
    have = set(record.get("words") or [])
    fresh = [key for key in keywords(_without_switchers(text)) if key not in have]
    return all(key in DETAIL_WORDS for key in fresh)


def _the_plan_a_correction_renames(memory, text):
    """The record the line corrects, when it names a different thing inside a plan of theirs.

    Returns None when the line is not a bare naming after a plan to get something, so every other
    correction is left to the rules that read it as a subject of its own.
    """
    record = current(memory)
    if not isinstance(record, dict) or _after_an_emergency(memory):
        return None
    if not NAMES_THE_THING.match(" ".join(str(text or "").lower().split())):
        return None
    if not A_THING_ON_ITS_WAY.search(str(record.get("text") or "")):
        return None
    extra = [key for key in keywords(text) if key not in (record.get("words") or ())]
    if not extra:
        return None
    # The plan keeps its words and gains the new name: the next line leans on the plan ("how much
    # exercise does it need" is the dog's question), and the name they have just said is in the
    # record it leans on.
    record["words"] = (list(record.get("words") or []) + extra[:FRESH_NAMES])[:12]
    return record


def _is_a_quantity(reading):
    """True when the numbers in the line carry a measure: "6000 pounds", "6 hours", "3k".

    A count of things is not one - "i have two cats" names the cats, it does not put a number
    on the last subject - so a bare count is left to name its own topic.
    """
    for number in reading.get("numbers") or []:
        if not isinstance(number, dict):
            continue
        if number.get("unit"):
            return True
        if SHORTHAND.match(str(number.get("text") or "").strip()):
            return True
    return False


def _is_a_when_or_how_often(text, memory):
    """True when the line only adds a when or a how-often to what the chat is already on."""
    read = memory.get("understood")
    if not isinstance(read, dict) or read.get("kind") != "statement":
        return False
    found = words(text)
    if not found or len(found) > 8:
        return False
    if WHEN_OR_AMOUNT.search(" ".join(found)) is None:
        return False
    if NAMED_THING.search(" " + " ".join(found) + " "):
        return False
    if len(keywords(text)) > 4:
        return False
    if _entry(text) is not None:
        return False  # it reaches an answer of its own, so it is a subject
    record = current(memory)
    if record is None:
        return False
    turn = record.get("turn")
    if isinstance(turn, int) and len(memory.get("turns") or []) - turn > RECENT_TURNS:
        return False
    return True


def _only_names_the_constraint(text, memory):
    """True when the line puts a number on a constraint of the thing in hand, and nothing else.

    It has to carry a measure ("my budget is 5k", "my budget is 5000 pounds"), because a budget
    with no figure in it ("my budget is tight") is a feeling about the money and not a quantity
    for the thing - and the line has to have something in hand to be about.
    """
    read = memory.get("understood")
    if not isinstance(read, dict) or read.get("kind") != "statement":
        return False
    said = " ".join(words(text))
    on_a_budget = ON_A_BUDGET.match(said) is not None
    if CONSTRAINT_IS.match(said) is None and not on_a_budget:
        return False
    if on_a_budget:
        # "about 300 each" is read as a maths ask rather than a quantity, so the figure is counted
        # in the line: a budget with no figure in it ("we're on a budget") is a feeling about the
        # money and says nothing about the trip.
        if not re.search(r"\d", said):
            return False
    elif not _is_a_quantity(read):
        return False
    record = current(memory)
    if record is None:
        return False
    turn = record.get("turn")
    if isinstance(turn, int) and len(memory.get("turns") or []) - turn > RECENT_TURNS:
        return False
    return True


def _adds_a_detail(text, memory):
    """True when the line only says a how-much about what the conversation is already on.

    It has to be a plain statement (a question is its own ask), it has to carry a measure (a
    price, a time, a distance), and it may bring at most a couple of words the subject does
    not already have: "we've got about 6000 pounds" after the wedding, "i can do about 3k at
    the moment" after the 10k. A line that names its own thing is not a detail of the last
    subject, so "my car is a 2015 fiesta" and "i have two cats" still start their own.
    """
    read = memory.get("understood")
    if not isinstance(read, dict) or read.get("kind") != "statement":
        return False
    if not _is_a_quantity(read):
        return False
    record = current(memory)
    if record is None:
        return False
    turn = record.get("turn")
    if isinstance(turn, int) and len(memory.get("turns") or []) - turn > RECENT_TURNS:
        return False
    named = MY_THING_IS.match(" ".join(words(text)) + " ")
    if named and stem(named.group(1)) not in (record.get("words") or []):
        return False
    numeric = set()
    for number in read.get("numbers") or []:
        if isinstance(number, dict):
            numeric.update(stem(word) for word in words(number.get("text") or ""))
    known = set(record.get("words") or [])
    fresh = [w for w in keywords(text) if w not in known and w not in numeric]
    return len(fresh) <= FRESH_WORDS


def person(text):
    """The person this speaker names ("my mum" -> "mum"), or None when it names nobody."""
    found = WHO_SAID.search(" ".join(words(text)))
    return found.group(1) if found else None


def _named_inside_a_question(text):
    """Whether this line's pronoun subject is asking a question that names somebody else."""
    line = " ".join(words(str(text or "").lower().replace("\u2019", "'")))
    if not A_BARE_PRONOUN_SUBJECT.search(line):
        return False
    return bool(A_QUESTION_THEY_ASK.search(line))


def person_named(text, memory=None):
    """The person the line is about: the speaker's own, or a third one when nobody is tracked.

    "my wife has dementia" then "she keeps asking for her mum" is still about the wife, so
    `her mum` names nobody new while someone is tracked. With nothing tracked, the same line
    still names the person being asked for.
    """
    who = person(text)
    if who:
        if about(memory) is not None and _named_inside_a_question(text):
            # "he keeps asking where my nan is" is still about the person the chat is on (and the
            # nan is the one being asked after), so the subject does not change on that line.
            return None
        return who
    if about(memory) is not None:
        return None
    found = WHO_SAID_THIRD.search(" ".join(words(text)))
    return found.group(1) if found else None


def trouble(text):
    """Which kind of trouble this line reports about the person it is about, or None."""
    low = " ".join(str(text).lower().replace("\u2019", "'").split())
    if A_JOB_AT.search(low) and not SOMETHING_WRONG.search(low):
        # Where somebody earns a living is not a trouble: "he works at the hospital" got "Sorry to
        # hear that. How is your dad doing?" because "at the hospital" is the words for a ward,
        # and the kinds below only made it worse once that one stood down ("Get your dad looked
        # at"). A line that says where the work is needs something actually wrong with it to be a
        # trouble at all.
        return None
    for kind, pattern in PERSON_TROUBLE:
        if not pattern.search(low):
            continue
        if kind == "known" and not CHANGE.search(low):
            continue  # a diagnosis on its own is not a change to tell the GP about
        if kind == "memory" and REPEATED_SAID.search(low) \
                and A_CHILDS_PERSON.search(low) and not A_GROWN_AGE.search(low):
            continue  # a child's favourite story, not a memory change
        if kind == "homeward" and A_WORRY_AFTER.search(low):
            # "my dad is out of hospital but he is still very weak" is a worry with good news in
            # front of it: the line's point is the weakness, and the ward question is the closer
            # reply. The kinds below keep that line.
            continue
        if kind == "falls" and (YOUNG_PERSON.search(low) or FALLS_FINE.search(low)
                                or FELL_OUT.search(low)):
            # a child who got straight back up has not had the fall this is about, and neither
            # has anybody who was only telling you they had fallen out with someone
            continue
        return kind
    return None


def _keep_person(memory, text):
    """Record the person this line is about, and keep the last one when the line says "she".

    The kind of trouble the line reports is kept with them, so the short ask two turns later ("is
    that normal", "what should i look out for") has something to lean on whatever answered the
    turn it arrived in.
    """
    turn = len(memory.get("turns") or [])
    who = person_named(text, memory)
    kind = trouble(text)
    if who:
        kept = about(memory) or {}
        if kept.get("who") != who or kept.get("said") != text.strip():
            memory["person"] = {"who": who, "said": text.strip(), "turn": turn}
        record = memory["person"]
    else:
        record = about(memory)
        if record is not None:
            record["turn"] = turn  # they are still the person being talked about
    if record is not None and kind:
        if record.get("trouble") != kind:
            record["trouble_turn"] = turn  # this line is the first to say it
        record["trouble"] = kind
    return record


def _after_a_correction(memory):
    """True when the line before this one corrected something, so nothing here is carried.

    "I need tips for my first half marathon" / "sorry, it's a 10k, not a half" / "how many weeks
    do I need to train?" is a question about the 10k. The topic record still reads "half
    marathon" - a correction replaces the subject rather than starting a new one - so carrying
    its words answers the half-marathon question to someone who has just said 10k. A correction
    ends the carry for one turn: the next line that names nothing is read on its own, which is
    where it would have been without the topic to lean on.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return False
    said = turns[-1].get("user")
    if not isinstance(said, str) or not said.strip():
        return False
    return bool(CORRECTION_LINE.search(" ".join(said.lower().split())))


def _the_apostrophe_back(low):
    """`whats good to see` read as `what is good to see`, so the ask word is a word again."""
    return WH_WORD_WITHOUT_ITS_APOSTROPHE.sub(r"\1 is", low)


def return_target(text):
    """What a line like "ok back to the boiler" or "anyway, the laptop" names, or ""."""
    low = _the_apostrophe_back(" ".join(words(text)))
    found = RETURN_LEAD.match(low)
    if found:
        rest = low[found.end():].strip(" ,.?!")
        return _the_thing(rest)
    casual = CASUAL_LEAD.match(low)
    if not casual:
        return ""
    target = low[casual.end():].strip(" ,.?!")
    parts = target.split()
    if not parts or parts[0] not in CASUAL_OPEN:
        return ""
    return _the_thing(target)


def _a_question_after_the_thing(rest, split):
    """Whether the words from `split` on are a question about the thing rather than its verb."""
    parts = rest.split()
    if split >= len(parts) or parts[split] not in HELPER_ASKS:
        return True
    after = parts[split + 1].strip(".,!?;:") if split + 1 < len(parts) else ""
    if not after:
        return True
    if parts[split] in MODALS and (after in ING_VERBS or after.endswith("ed")):
        return True
    return not (after in VERB_PHRASE_AFTER or after in ING_VERBS or after.endswith("ed"))


def _the_thing(rest):
    """"the laptop, which would you get?" names the laptop; "work tomorrow" names nothing."""
    asked = re.search(r"[,?!;]|\b(?:" + "|".join(sorted(RETURN_ASKS)) + r")\b", rest)
    head = rest[:asked.start()] if asked else rest
    if asked and not _a_question_after_the_thing(rest, len(head.split())):
        return ""
    parts = head.split()
    while parts and (parts[-1] in CASUAL_OPEN or parts[-1] in STOPWORDS):
        parts.pop()
    if not parts or len(parts) > 3:
        return ""
    if any(part in CASUAL_VERB or part in RETURN_TIME for part in parts):
        return ""
    return " ".join(parts)


def _asks(text):
    if "?" in text:
        return True
    return any(word in RETURN_ASKS for word in text.split())


def asks_after(line, thing):
    """Does the line ask something *after* the thing it went back to?

    The sentence people use to go back can carry a question word before the thing: "as I was
    saying, Rome" has "was" in it, and read as a whole line that looked like a question, so the
    return reply stepped aside and the greeting said "As you was saying, Rome - noted." What
    matters is what comes after the thing: "as I was saying, Rome" asks nothing, while "back to
    the laptop, which would you get?" and "coming back to the boiler, is it worth servicing?"
    do, and the answer modules take those lines.
    """
    low = _the_apostrophe_back(" ".join(words(line)))
    named = " ".join(words(thing))
    at = low.find(named) if named else -1
    if at >= 0:
        low = low[at + len(named):]
    return _asks(low)


def _resume(memory, record, target, line=""):
    """Make the earlier topic current again, and note the turn so a reply can greet the return."""
    said = dict(record)
    # The thing the person just named is the best word for what the conversation is about now:
    # "back to saving" makes the subject "saving", not a gist of the longer line they first
    # said it in, so a follow-up ("how much do I need to put by each month?") still reaches the
    # entry that word matches.
    said["subject"] = " ".join(words(target)) if target else said.get("subject") or ""
    memory["topic"] = said
    # The list of topics is what a follow-up is read against ("how much do I need to put by each
    # month?" after going back to the saving plan), so the topic gone back to is the newest entry
    # in it too: left where it was, the line read against the subject in between and got a hedge.
    topics = memory.get("topics")
    if not isinstance(topics, list):
        topics = memory["topics"] = []
    topics[:] = [other for other in topics if other is not record
                 and (other.get("text") or "") != (said.get("text") or "")]
    topics.append(said)
    memory["return_to"] = said.get("text") or target
    memory["returned"] = {"text": said.get("text") or target, "asked": target,
                          "asks": asks_after(line, target),
                          "turn": len(memory.get("turns") or [])}
    _the_answer_on_the_return(memory, said)
    return said


def is_follow_up(text, memory):
    """True when a line leans on the current topic: 'how long will it take?', 'and if I...'."""
    record = current(memory)
    if not record:
        return False
    # A record made from this very line is not the thing before it. The topic is written before
    # the modules run, so on a first line `current(memory)` is the line itself: "what can i make
    # with mince" then looks like a follow-up on "mince", nothing about the entry shares those
    # words, and the answer the line has is thrown away as a different subject.
    if _this_line(record, memory):
        return False
    clean = " ".join(words(text))
    if not clean or is_ack(text) or clean in GREET:
        return False
    rest = [word for word in words(text)]
    while rest and rest[0] in LEAD_ACKS:
        rest = rest[1:]
    if rest:
        clean = " ".join(rest)
    low = clean
    if _switches(clean):
        return False
    found = words(text)
    if len(found) > 16:
        return False
    topic_words = set(record.get("words") or [])
    fresh = [k for k in keywords(text) if k not in topic_words]
    if KIND_ASK.search(low) and len(found) <= 10:
        return True
    if found[0] in CONTINUATION_START:
        if len(fresh) <= 2 and len(found) <= 8:
            return True
        if PROPERTY.search(low) and len(fresh) <= 3 and len(found) <= 10:
            return True
    if any(word in REFERRING for word in found) and len(fresh) <= 3:
        return True
    return len(fresh) <= 1 and len(found) <= 8


def expand(text, memory):
    """The line plus the topic it follows, e.g. 'how long will it take? (earlier: ...)'."""
    record = current(memory)
    if record and is_follow_up(text, memory):
        earlier = context(memory) or [record["text"]]
        return text + " (earlier: " + " / ".join(earlier) + ")"
    return text


_MAX_SUBJECT = 4


def _strip_considering(source):
    """The line without the words that only say they are thinking of getting the thing."""
    while True:
        stripped = _CONSIDERING.sub("", source)
        if stripped == source:
            return source
        source = stripped


def _only_a_handoff(head):
    """Whether a clause only announces that something is coming: "one more thing", "quick one".

    The hand-off phrases are the reading engine's own list, so a phrase added there is read here
    too (bot/understanding/lexicon.py, `HANDOFF_LEADS`). A clause that goes on to name something
    of its own is not an announcement: "the last thing i need is another bill" is about the bill.
    """
    text = " ".join(str(head or "").lower().split()).strip(" ,.;:!?-")
    text = _HANDOFF_THROAT.sub("", text).strip(" ,.;:!?-")
    for lead in sorted(lexicon.HANDOFF_LEADS, key=len, reverse=True):
        if text == lead or (text.startswith(lead) and not keywords(text[len(lead):])):
            return True
    return False


def _a_word_of_a_date(word):
    """Whether a content word can be part of a date and nothing else: "saturday", "next",
    "christmas", "son".

    The forms are compared as well as the words, because `keywords` stems what it keeps:
    "christmas" comes back as "christma".
    """
    forms_ = (word, stem(word))
    return (any(form in _DATE_OCCASIONS for form in forms_)
            or any(form in _TIME_WORDS for form in forms_)
            or word in _DATE_FILLER
            or any(form in _A_FIGURE for form in forms_)
            or any(form in _the_people() for form in forms_))


def _only_a_date(clause):
    """Whether a clause only says when a day is: "my son's birthday is next saturday".

    Every content word has to be one of the day, a word of the date, a figure or a person: a
    clause that says anything else ("my knee hurts", "my mum is 78 and keeps falling") is about
    that thing, and the person in it is what the line is about.
    """
    kept = keywords(clause)
    if not kept or not any(stem(word) in _DATE_OCCASIONS for word in kept):
        return False
    return all(_a_word_of_a_date(word) for word in kept)


def _the_thing_after_a_date(text):
    """The clause that names the thing a dated line is about, or "".

    "my son's birthday is next saturday and i want to bake him a cake" led with the date, so the
    subject came back as "son birthday": the chat was on nothing to bake, the allergy line after
    it attached to no thing, and "how long will that take?" was carried as "how long will son
    birthday take", which no entry answers. The thing they are making is the subject.

    A comma is the same break as an "and" here: "my sons birthday is next saturday, im doing a
    cake" is one dated line with one thing being made.
    """
    parts = re.split(r"\b(?:and|but)\b|[,;]", text, maxsplit=1)
    if len(parts) < 2:
        return ""
    head, tail = parts
    if not _only_a_date(head) or not keywords(tail):
        return ""
    return tail if _MAKING_A_THING.search(tail) else ""


def gist(text):
    """The short noun phrase a line is really about: "birthday cake", "kitchen tap", "turkey".

    "A birthday cake for my son, 8, this weekend." is about the birthday cake; "Cook a turkey
    for Christmas." is about the turkey; "the tap in the kitchen keeps dripping" is about the
    tap in the kitchen. It keeps the words that carry the meaning and drops the rest.
    """
    source = " ".join(str(text or "").lower().split())
    source = _CORRECTION_LEAD.sub("", source)
    # "never mind, how do i boil an egg" is about the egg: the words that announce a new subject
    # are the switch, not the subject.
    for switcher in sorted(SWITCHERS, key=len, reverse=True):
        if source.startswith(switcher):
            source = source[len(switcher):].lstrip(" ,.!-")
            break
    # A clause that only dates the day is the date of the thing, not the thing: what they are
    # making after the "and" is what the chat is on.
    dated = _the_thing_after_a_date(source)
    if dated:
        source = dated
    # A verb with its particle comes off before the "for" split as well: "i cant cope with the
    # noise" was split at its own "with" and the subject came back as "cant cope".
    source = " ".join(_PHRASAL_RE.sub(" ", source).split())
    source = _RELATION.split(source)[0]
    whole = source
    if _FRAME_ASK.search(source):
        # the clause emptied, and the line kept as it was when the clause is all there is
        trimmed = _WITHOUT_CLAUSE.sub("", source).strip(" ,.;:!?")
        if trimmed and keywords(trimmed):
            source = trimmed
    # The words that say they are deciding come off first, before the "for" split: "i'm in the
    # market for a sofa" would otherwise be split at its own "for" and be about "the market".
    source = _strip_considering(source)
    # "thinking of getting a dog", "trying to lose a stone": the wishing and the doing are how
    # the thing is reached, not the thing. Only the front is dropped, so "my driving" stays.
    # "getting" and "buying" only open such a phrase when a determiner follows: the same words
    # are a state ("we're getting married next year"), and stripping "getting" from it leaves
    # "married", a word that fits half the knowledge base.
    buying = bool(_BUYING_A_STATE.match(source))
    wished = False
    for _ in range(3 if not buying else 0):
        stripped = _WISH_RE.sub("", source)
        if stripped == source or not stripped.strip(" ,.;:!?"):
            break
        source = stripped
        wished = True
    before_split = source
    # The purpose after a sum is a better subject than the sum: see _A_FIGURE below.
    segments = re.split(r"\b(?:for|tonight|today|tomorrow|yesterday|this|next)\b", source)
    source = segments[0]
    if not wished and not buying:
        source = _LEAD.sub("", source.strip(" ,.;:!?"))
        # A question left over as a subject keeps its question word: "whats the weather like" is
        # about the weather, not about "what weather", and a follow-up that puts the subject back
        # on the end of itself ("what should i wear" + "what weather") is not a line anything
        # answers.
        while True:
            trimmed = _LEAD_QUESTION.sub("", source)
            if trimmed == source or not trimmed.strip():
                break
            source = trimmed
    source = _strip_considering(source)
    # A comma opens a clause about the thing, not another thing: "i'm after a new phone, mine is
    # four years old" is about the phone, and "mine four years old" is not part of its name.
    # Unless the clause before it is only an announcement: "one more thing, my car failed its mot
    # on a tyre" is about the car, and read as the announcement it was about nothing at all -
    # empty, so `_about_record` skipped the record and the conversation kept the subject it had
    # two turns before, which is how a question about the MOT was answered about back pain.
    head, _, after_handoff = source.partition(",")
    source = after_handoff if after_handoff.strip() and _only_a_handoff(head) else \
        re.split(r"[,;]", source)[0]
    kept = [word for word in keywords(source) if word not in ASK_ONLY]
    while kept and kept[-1] in _TIME_WORDS:
        kept.pop()
    if kept and all(word in _A_FIGURE for word in kept):
        # A sum and its unit are the figure, not the thing: "im trying to save 500 pounds for a
        # trip to spain" is about the trip, and read as "pound" the follow-up "how long will it
        # take?" became a question about losing weight, the one entry keyed on pounds. What the
        # money is for is the subject, so the purpose after the "for" is read instead.
        for part in segments[1:]:
            later = [word for word in keywords(part)
                     if word not in ASK_ONLY and word not in _TIME_WORDS]
            if later and not all(word in _A_FIGURE for word in later):
                kept = later
                break
    if not kept and wished:
        # "im trying to save 3000 for a trip to iceland next summer" loses everything it has to
        # the time split, because what is left before it is a figure. A figure is a poor subject
        # but an empty one is worse: the follow-up has nothing to be about at all. So the whole
        # line, minus the times and the ask, is the last word.
        for source in (before_split, whole):
            kept = [word for word in keywords(source)
                    if word not in ASK_ONLY and word not in _TIME_WORDS]
            if kept:
                break
    if not kept:
        return ""
    return " ".join(kept[:_MAX_SUBJECT])


def _room_limit(text):
    """The home space a line only says the size of, or "" when it says more than that.

    "my flat is small" -> "my flat", "the kitchen is really tiny" -> "the kitchen",
    "my kitchen is tiny and the oven is broken" -> "" (the line names something else too),
    "the garden is small" -> "" (a place with room in it, but not a space inside the home).
    """
    words_ = " ".join(str(text or "").lower().split())
    found = _ROOM_LIMIT.match(words_)
    if not found:
        return ""
    head = found.group("head").strip(" ,.;:!?-")
    if not head:
        return ""
    return head if head.split()[-1] in _HOME_SPACES else ""


def _thing_of(memory, record):
    """The record a detail line points back at, or None.

    A line that only says a detail of the thing the chat is on ("he is allergic to nuts" after
    a birthday cake) is still a topic: the answer it reached is about the cake, and the line
    itself is in the turns. But ask a follow-up of it - "how long will it take, start to
    finish?" - and the words it lends are the nuts, which reach nothing, so the answer already
    given comes back with "Same as before" in front of it. The record carries the thing it was
    a detail of, and that is the subject a follow-up leans on.
    """
    if not isinstance(record, dict):
        return None
    back = str(record.get("of") or "")
    if not back:
        return None
    for other in reversed(memory.get("topics") or []):
        if isinstance(other, dict) and str(other.get("text") or "") == back:
            return other
    return None


def _about_record(memory):
    """The last topic that names something, rather than only saying how much room there is.

    When every topic so far is a size line there is nothing to fold back into, so the record is
    read as it always was: "my kitchen is tiny" is about the kitchen tiny, and a follow-up after
    it is answered the way it was before this rule.
    """
    records = memory.get("topics")
    if not isinstance(records, list):
        return current(memory) or {}
    for record in reversed(records):
        if not isinstance(record, dict) or _room_limit(record.get("text")):
            continue
        if _names_nothing(record):
            # A line that only leans on what is on the table ("and how long will it take", "lol")
            # is not what the conversation is about: the record before it is. Read as the subject,
            # the follow-up's own two words ("long take") gave every reader that asks the subject
            # nothing at all, and the ask about the boiler reached no boiler.
            continue
        return record
    return current(memory) or {}


def _names_nothing(record):
    """Whether a topic record says nothing of its own about what is being talked about."""
    if " ".join(str(record.get("subject") or "").split()):
        return False
    return not gist(record.get("text") or "")


def subject(memory):
    """What the conversation is about now, as a noun phrase other modules can use.

    The plan the person gave if there is one ("birthday cake"), otherwise the gist of the
    current topic ("xmas dinner"). Empty when the conversation has no subject yet.
    """
    known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    record = _about_record(memory)
    # A detail of the thing we are on is about the thing: "he is allergic to nuts" after a
    # birthday cake leaves the cake as the subject, so the next line ("how long will it take?")
    # is the cake's question and not the nuts'.
    thing = _thing_of(memory, record)
    if thing is not None:
        record = thing
    # A return names its topic ("back to saving"), and that word is what the line after it is
    # about, so it outranks the gist of the longer line the topic first came from.
    now = " ".join(str(record.get("subject") or "").split()) or gist(record.get("text") or
                                                                    topic_text(memory))
    planned = gist(known.get("plan") or "")
    if planned and now and planned in now:
        return planned  # the plan names the thing better than the line it came from
    return now or planned


def topic_text(memory):
    record = current(memory)
    return record["text"] if record else ""


MAX_ACTION = 6       # "lose a stone", not the whole sentence the person said it in


def _the_action_word(line):
    """The first word of the line that is the person's own action, and its base form.

    "im thinking of getting a rescue dog" opens on "getting": the ask about time is about the
    dog, and "get a rescue dog" is the phrase the answer is indexed by. Looking at every word,
    not only the ones after "to", is what finds it - "i want to lose a stone" puts the action
    after "to", "im learning to drive" puts it first.
    """
    for index, word in enumerate(line):
        found = forms(word) & ACTION
        if not found:
            continue
        before = line[:index]
        if before and before[-1] in ACTION_AFTER:
            pass  # "the best way to learn spanish" is the person's own doing
        elif any(word not in PERSON_LEAD for word in before):
            continue  # "my boiler is making a noise" is about the boiler
        # The base form is the one the list has; "getting" is "get", "learning" "learn".
        return index, sorted(found, key=len)[0]
    return None, None


def action(memory):
    """The action the conversation is on ("lose a stone", "learn spanish"), or "".

    A topic that is a thing rather than an action ("my boiler is making a noise") has none, so
    the caller names the thing its own way.
    """
    said = " ".join(words(topic_text(memory)))
    if not said:
        return ""
    line = said.split()
    index, base = _the_action_word(line)
    if index is None:
        return ""
    # "lose a stone and eat better" is one action, not two: what follows is another ask.
    tail = " ".join(line[index:])
    tail = re.split(r"\b(?:and|but|because|so|then|when|if|before|after)\b", tail)[0]
    words_of_the_action = tail.split()[:MAX_ACTION]
    words_of_the_action[0] = base
    return " ".join(words_of_the_action).strip()


def written_out(text, memory):
    """A bare duration ask written out with the action in it.

    "how long will it take?" after "i want to lose a stone" -> "how long will it take to lose a
    stone?", the question the knowledge base has an entry for. None when the line is not a bare
    duration ask, or the conversation is on a thing rather than an action, so the caller keeps
    its own way of naming what the answer is about.
    """
    low = " ".join(words(text))
    if not low or not DURATION_ASK.search(low):
        return None
    if any(word not in DURATION_WORDS for word in low.split()):
        return None
    done = action(memory)
    if not done:
        return None
    said = " ".join(str(text).split()).rstrip("?.! ")
    return said + " to " + done + "?"


def _named_a_thing(line):
    """Whether a line named a thing at all, rather than an attribute of one or a state of one."""
    thing = gist(line)
    if not thing or thing in NOT_A_THING:
        return ""
    if all(word in ATTRIBUTE_WORDS for word in thing.split()):
        # "and the oven temperature" / "which size": an attribute line names no thing of its own,
        # so the thing is whatever the chat was on before it ("sofa", not "size").
        return ""
    if thing.split()[-1] in A_STATE:
        return ""
    return thing


def _the_thing_on_the_table(memory):
    """The thing the last few lines named, as few words ("bread", "bike"), or ""."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ""
    for turn in list(reversed(turns))[:4]:
        line = str((turn or {}).get("user") or "") if isinstance(turn, dict) else ""
        thing = _named_a_thing(line)
        if thing:
            return thing
    return ""


def attribute_of_the_thing(text, memory):
    """A line that asks one attribute of the thing on the table, written out with the thing.

    None when the line is not only an attribute, or the chat has no thing to put in it, so the
    caller keeps the answer it would have given.
    """
    low = " ".join(words(text))
    if not low or len(low.split()) > 5:
        return None
    if any(word not in ATTRIBUTE_WORDS for word in low.split()):
        return None
    frame = None
    for pattern, said in ONE_ATTRIBUTE:
        if pattern.search(low):
            frame = said
            break
    if frame is None:
        return None
    thing = _the_thing_on_the_table(memory)
    if not thing:
        return None
    return frame.format(thing=thing)


def key_subject(text, memory=None):
    """The key words of the entry a line is about, in the fewest words.

    It is the part of a knowledge entry's key that the line actually used, so a long question
    comes back as its subject: 'how long do I cook a 2kg chicken?' -> ['chicken'], 'any tips for
    Rome in July?' -> ['rome']. Knowing just the subject is what lets a follow-up ('and if I
    stuff it?') be read as being about the chicken and not about its cooking time. When the
    line on its own reaches no entry, the earlier topics in memory are tried, so a follow-up of
    a follow-up still finds the thing they were talking about.
    """
    if memory is not None:
        # The thing a detail points back at is what the line after it is about: the words of
        # "he is allergic to nuts" reach the cake's allergy entry, and a follow-up ("and if I
        # leave the nuts out?") keyed on "nuts" reaches nothing.
        for record in reversed(memory.get("topics") or []):
            if not isinstance(record, dict) or str(record.get("text") or "") != str(text):
                continue
            if _this_line(record, memory):
                break  # the line on the table now is read on its own words
            thing = _thing_of(memory, record)
            if thing is not None:
                found = _key_subject(str(thing.get("text") or ""))
                if found:
                    return found
            break
    found = _key_subject(text)
    if found:
        return found
    if memory is not None:
        for record in reversed(memory.get("topics") or []):
            text_ = record.get("text") if isinstance(record, dict) else None
            found = _key_subject(str(text_ or ""))
            if found:
                return found
    return keywords(text)[:3]


def _the_part_a_complaint_is_about(text):
    """The body part a line complains about, or None.

    Lazy, because the store keeps no facts of its own: the part table is the knowledge base's.
    """
    from ..knowledge.body import the_part_that_hurts
    return the_part_that_hurts(text)


def _the_cause_words(text):
    """The words after the cause in a complaint, or an empty set when it names none."""
    found = CAUSE_OF_THE_COMPLAINT.search(str(text or "").lower())
    if not found:
        return set()
    return set(words(str(text or "").lower()[found.end():]))


def _key_subject(text):
    """The key words of the entry a line reaches, in key order, or None when it reaches none.

    Every part of the key the line used comes back, not just the first, so a dripping tap gives
    'tap' and 'dripping': a follow-up needs both to reach the same entry again. A part made of
    asking words ("how long", "time") is left out: it is the ask, not the subject.
    """
    found = words(text)
    item = _entry(text)
    if item is None:
        return None
    out = []
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if not isinstance(alternative, str) or not _said(alternative, found):
                continue
            part_words = words(alternative)
            if not ASK_PART.intersection(part_words):
                out.extend(part_words)
            break
    return out or None


def _said(phrase, found):
    """True when the words of a phrase are in the line, folded so eggs/egg still match.

    The words are taken in the order the line said them, because a key phrase is two words said
    in that order ("urine infection", "blood in the urine", "litter tray"). A caller that hands
    over a set has already thrown the order away, and a set is read in whatever order the hash
    seed happened to give it: the same line was answered from the cat's urine-infection entry
    under one seed and from the human one under another, because the two words of the phrase
    landed beside each other in one run and not the other. So an unordered bag is read as what it
    is - every word of the phrase said somewhere in the line - and the answer is the same under
    every seed. Callers that have the line in hand pass its words in order and get the tighter
    reading.
    """
    wanted = [stem(word) for word in words(phrase) if word not in STOPWORDS]
    if not wanted:
        return False
    if isinstance(found, (set, frozenset)):
        return all(word in {stem(one) for one in found} for word in wanted)
    have = [stem(word) for word in found]
    n = len(wanted)
    return any(have[i:i + n] == wanted for i in range(len(have) - n + 1))


def _entry(text):
    """The knowledge entry a line reaches, or None (the knowledge base is read, not changed)."""
    from ..knowledge.lookup import find  # lazy: the store does not need the facts
    return find({"clean": str(text), "words": words(text)})
