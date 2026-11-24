"""Part 3 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from ..understanding.kinds import NEGATIVE, POSITIVE
from .topics_part_01 import (
    words, RECENT_TURNS, _after_an_emergency, _this_line, alike, current, keywords, stem, COUNTING,
    SAME_ASK, THE_TAIL, ELIDED_ASK, ABOUT_THE_CHAT, ASK_MORE, ASK_ONLY, STAND_IN, STOPWORDS,
    TOPIC_OPENS_WITH, STAY_ASK, LIVES_THERE, TRIP_FRAME, STAY_ONLY, POINTING_WORD, A_BARE_MEASURE,
    MEASURE_WORDS, forms, DUMMY_IT, REFERRING_WORDS, ASKS_FOR_ADVICE, ASK_PART, content, PRICE_ASK,
)
from .topics_part_02 import (
    _entry, subject, _another_area, _names_a_thing_of_its_own, gist, _the_cause_words,
    _the_part_a_complaint_is_about, key_subject, topic_text, _said,
)


def _reaches_another_thing(text, memory):
    """True when the line reaches a knowledge entry that is not about the conversation's thing.

    The record's own line is a poor stand-in for the thing: "im thinking of getting a dog for
    the kids" reaches the entry about deciding a choice, not the one about dogs, so a question
    about dogs looked like a new subject next to it. The subject the store already worked out
    ("dog") is what decides: an entry that names a word of it is still that thing, and one that
    does not - the cats - is a thing of its own.
    """
    mine = _entry(text)
    if mine is None:
        return False
    thing = subject(memory)
    if not thing:
        return False
    return not _names_it(words(thing), mine)


def _a_detail_of_what_we_are_on(text, memory):
    """The record this line only says a detail about, or None when it names a thing of its own.

    "he loves chocolate but he is allergic to nuts" after a birthday cake reaches an answer of
    its own (the cake's allergy variant), so on its words alone it looks like a new subject. It
    is not: the answer it reaches is the cake's, which is why the reply was about the cake. If
    the chat moves its subject to the nuts, the next line - one that names nothing of its own,
    like "how long will it take, start to finish?" - is read against the nuts, reaches nothing,
    and gets the answer already given again: "Same as before: <the allergy answer>". The thing
    the chat is on is the cake, so a line that answers about it is a detail of it.

    "my budget is 600 pounds" after a laptop is not one: it is about the budget, and the next
    ask ("which one would you pick?") has to be read against the budget, not the laptop.
    """
    record = current(memory)
    if not isinstance(record, dict) or not record.get("text"):
        return None
    if _this_line(record, memory) or _after_an_emergency(memory):
        return None
    if _names_a_thing_of_its_own(text, record, memory):
        return None
    turn = record.get("turn")
    if isinstance(turn, int) and len(memory.get("turns") or []) - turn > RECENT_TURNS:
        return None
    thing = gist(record.get("text") or "")
    if not thing:
        return None
    widened = _entry(str(text) + " " + thing)
    if widened is None:
        return None
    # The answer the widened line reaches has to be about the thing the chat is on: "my car
    # won't start" after a birthday cake reaches the car's answer, which says nothing about a
    # cake, so the car is a subject of its own.
    keyed = _key_words_of(widened)
    thing_words = [word for word in keywords(thing) if len(word) > 2]
    if not thing_words or not any(alike(word, key) for word in thing_words for key in keyed):
        return None
    own = _entry(text)
    if (own is not None
            and not any(alike(word, key) for word in keywords(text) for key in keyed)
            and _another_area(text, record.get("text") or "")):
        # The line has an answer of its own, the answer it reaches with the thing added speaks
        # of none of the line's own words, and the two lines are read as different kinds of
        # thing: it is a subject of its own, not a detail. "im going to lisbon in may" after a
        # bedwetting line reaches the city guide, and the bedwetting answer shares no word with
        # it; kept as a detail of the bedwetting line, the next ask ("what should i see") was
        # read against that line and answered from it.
        return None
    if own is widened:
        return None  # the line reaches this answer without the thing, so it is that answer
    if own is not None and not any(alike(word, key) for word in _key_words_of(own)
                                   for key in keyed):
        return None  # a different question about the thing, not a way of answering this one
    if keeps_away(str(text) + " " + thing, record.get("text") or "", widened):
        return None
    return record


def _subject_words_to_carry(record, text, memory):
    """The topic's words a follow-up carries, with a complaint's cause left behind.

    "my back has been killing me since i moved the sofa" is a line about the back, and the
    follow-up "its sort of a dull ache on the left side" is about the back too. Its key words in
    key order are ['sofa', 'back'], so the follow-up was read as an ache of the sofa and got the
    furniture-repair card. A complaint carries the part it complains about, not the thing it
    blames for it. A line with no cause ("i pulled a muscle in my groin") carries what it always
    did, because the groin answer needs the muscle with it.
    """
    topic_text = str((record or {}).get("text") or "") if isinstance(record, dict) else ""
    subject = key_subject(topic_text, memory)
    part = _the_part_a_complaint_is_about(topic_text)
    cause = _the_cause_words(topic_text)
    if part and cause and part not in words(text) and not _the_part_a_complaint_is_about(text):
        kept = [word for word in subject if word not in cause or word == part]
        if part not in kept:
            kept.insert(0, part)
        return kept
    return subject


def _where_the_topic_lands(topic):
    """The entry the topic is about, read past the verb it happens to share with an entry's ask.

    "My sourdough keeps coming out flat" reaches the shelf-life entry, because that entry asks for
    "keep" and names a sourdough: the line has said the thing and the ask's own verb, and nothing
    more is needed for it to score. Read without that verb the line is about the loaf that comes
    out flat, and that is the entry the trouble belongs to - "keeps coming out" is how the
    trouble goes on, not a question about how long the loaf lasts. Only a word the entry itself
    asks with is dropped, and only when dropping it lands somewhere else: every other topic is
    read exactly as it was.
    """
    found = _entry(topic)
    if found is None:
        return None
    asked = set()
    for part in getattr(found, "ask", ()):
        for phrase in (part if isinstance(part, tuple) else (part,)):
            if isinstance(phrase, str):
                asked.update(words(phrase))
    if not asked:
        return found
    kept = [word for word in words(topic) if stem(word) not in asked and word not in asked]
    if len(kept) == len(words(topic)):
        return found
    other = _entry(" ".join(kept))
    if other is None or other is found:
        return found
    # The words left have to name the thing the topic is about: two of them, as everywhere else.
    if len(_key_words_of(other) & set(keywords(topic))) < 2:
        return found
    return other


def an_entry_for(text):
    """The knowledge entry a line reaches on its own, or None.

    Read by the store for the reply on screen: a line the knowledge base answered is a fact, and a
    line it did not is a nod or a reading, which is not something to confirm.
    """
    return _entry(text)


def _the_last_question(memory):
    from ..understanding import understand  # lazy: the store does not need the reading engine
    for turn in reversed([one for one in (memory.get("turns") or []) if isinstance(one, dict)]):
        said = str(turn.get("user") or "").strip()
        if "?" in said or understand(said, memory).get("asks"):
            return said
    return ""


def how_much_of_the_thing_in_hand(line, memory):
    """The last question in the chat, with this line's count of the thing in hand in it.

    "how much protein in porridge oats" / "and in a slice of bread" / "what about two slices": the
    last line only counts, so on its own it is a statement with no thing in it ("two slices" of
    what?), and the bot punted or answered a bread entry. Read as the question the chat asked,
    with the count and the thing the turn before named, it is "how much protein in two slices
    bread" - the figure the person asked for. Only a line that *only* counts takes this reading:
    a line that names its own thing is a new thing to look up, and the answers' own paths read
    those. Returns "" when the line is not that shape, or when the question thus read reaches
    nothing.
    """
    said = str(line or "").strip()
    if not SAME_ASK.match(said):
        # "i only have half a kg" counts too, but it is a statement about what they have, not a
        # follow-up asking the same question about it.
        return ""
    body = SAME_ASK.sub("", said)
    counted = words(gist(body))
    if not counted or not all(word in COUNTING or word.isdigit() for word in counted):
        return ""
    asked = _the_last_question(memory)
    if not asked:
        return ""
    head = ""
    for match in THE_TAIL.finditer(asked):
        head = asked[:match.end()]
    from ..understanding import understand  # lazy, as above
    if not head or not understand(head + " " + body, memory).get("asks"):
        return ""
    turns = [one for one in (memory.get("turns") or []) if isinstance(one, dict)]
    before = str((turns[-1] if turns else {}).get("user") or "")
    # The thing being counted is the one the turn before named ("and in a slice of bread" ->
    # bread), never a word the question already has.
    thing = [word for word in words(gist(before))
             if word not in words(head) and word not in words(said)]
    if not thing:
        return ""
    read = " ".join(words(head) + counted + thing)
    if not read or _entry(read) is None:
        return ""
    return read


def elided_ask(text):
    """True when the line asks about a thing it names with the asking left off.

    "any games" and "what about drinks" are questions, but they carry no question word of their
    own and no verb, so the understanding engine reads them as statements. Only short lines
    count: "any games for a party of ten" already asks its own question and is left alone, and
    so is a line that names a measure ("any idea how long"), which is a different ask.
    """
    said = str(text or "").lower().strip()
    if not said or len(words(said)) > 5:
        return False
    if not ELIDED_ASK.match(said):
        return False
    # "any idea how long" asks for a figure, and it is read as the ask it is already. The "how"
    # of "how about pudding" is not one of those: it is the elision itself.
    asked = re.sub(r"^(?:(?:ok|okay|so|and|also|plus|or|then|right|yeah|yes|oh|em|um)\s+)*"
                   r"(?:how|what)\s+about\s+", "", said)
    return not re.search(r"\b(?:how|when|where|why|which|who)\b", asked)


def names_nothing(text):
    """True when a line asks something and names nothing it could be about.

    'how often should I go?' and 'why is that happening?' are answered from what the last line
    was about; 'how do I cook a chicken?' names a chicken and is left alone, and a question
    about what the bot knows is not about the topic at all.
    """
    return not _content_words(text)


def _content_words(text):
    """The words of a line that could name a thing of its own, the ask words taken out.

    "how many weeks should I train" keeps only "train": a figure the line asks for is not a thing,
    and the thing here is the training.
    """
    if ABOUT_THE_CHAT.search(str(text or "").lower()):
        return []
    return [word for word in words(text)
            if word not in STOPWORDS and word not in ASK_ONLY and word not in ASK_MORE
            and word not in STAND_IN]


def _the_topic_phrase(topic):
    """The topic as the phrase a frame can take: "im buying a house" -> "buying a house"."""
    said = " ".join(str(topic or "").lower().split()).strip(" .,;:!?")
    said = TOPIC_OPENS_WITH.sub("", said).strip()
    return said if len(said.split()) >= 2 else ""


def _a_length_of_the_job(item):
    """Whether the entry is keyed to "how long ... take": the length of doing the thing.

    "how long does it take" after "im painting the kitchen" reaches the entry keyed to how long
    the paint itself lasts, and the answer it gives ("five to ten years") is a wrong fact about
    a job. A carry is only right when the entry answers the length of doing it, which its own key
    says with the asking words and "take" in the same group.
    """
    for part in getattr(item, "key", ()) or ():
        said = set()
        for phrase in (part if isinstance(part, tuple) else (part,)):
            if isinstance(phrase, str):
                said.update(words(phrase))
        if said & {"take", "takes", "taking"} and said & {"how", "long", "time"}:
            return True
    return False


def the_city_of(topic):
    """The city of the days-per-city table the topic names, or None."""
    from ..knowledge.travel import CITY_DAYS, _find_in  # lazy: the store needs no facts
    return _find_in(str(topic or "").lower(), CITY_DAYS)


def the_country_of(topic):
    """The country of the where-to-go table the topic names, or None.

    A country is a trip the same way a city is, and the length of it is answered from the cities
    its card names: "we are going to portugal in june" and then "how long should we go for" was a
    search hedge, because only the cities-per-day table was carried.
    """
    from ..knowledge.travel import WHERE_TO_GO, _find_in  # lazy: the store needs no facts
    return _find_in(str(topic or "").lower(), WHERE_TO_GO)


def asks_how_long_to_stay(line):
    """Whether the line is shaped like an ask for how long, as a stay ask is."""
    return bool(STAY_ASK.search(str(line or "").lower()))


def going_there(place, topic):
    """Whether the topic says the person is going to the place, not living in it.

    "im planning a trip to edinburgh" is a trip; "i live in edinburgh", "my sister lives in
    lisbon" and "i went to edinburgh last year" are not, and the stay length answers none of
    them - a confident "Two full days in Edinburgh" to a person who lives there is worse than
    the punt main gives.
    """
    said = str(topic or "").lower()
    for match in LIVES_THERE.finditer(said):
        # The place has to be the thing they live in, not one mentioned later in the line.
        if str(place) in said[match.end():match.end() + 40]:
            return False
    return bool(TRIP_FRAME.search(said))


def a_stay_with_the_place(line, topic):
    """The stay-length ask with the place the topic names in it, or None.

    The table is reached with the city in the line and not by the topic's words put on the end:
    "how many days planning trip" is the trip plan's own key, and its "keep one day free in the
    middle" is then read back as the answer to how long to stay ("One day.").
    """
    lowered = str(line or "").lower()
    if not STAY_ASK.search(lowered):
        return None
    if [word for word in words(lowered) if word not in STAY_ONLY]:
        return None
    from ..knowledge.travel import CITY_DAYS, _find_in  # lazy: the store needs no facts
    if _find_in(lowered, CITY_DAYS):
        return None  # the line names its own city: that is the city the ask is about
    place = the_city_of(topic) or the_country_of(topic)
    if not place or not going_there(place, topic):
        return None
    return lowered.strip().rstrip("?.!").strip() + " in " + place


def _the_ways_of_saying_it(stem_of, line, cands):
    """The follow-up with the subject carried, said the two ways it can be said.

    A follow-up that names nothing takes the topic's words with it: "how often should I go?"
    after "I want to start running" is "how often should I go running". When the line points
    back with a word of its own ("when do those go in"), the subject is what that word stands
    for, so it is put in its place rather than added after it - "when do those go in tomatoes"
    reaches no entry, and "when do tomatoes go in" is the planting one.
    """
    for cand in cands:
        carried = " ".join(cand)
        yield stem_of + " " + carried, carried
    if POINTING_WORD.search(str(line or "")):
        for cand in cands:
            carried = " ".join(cand)
            yield " ".join(POINTING_WORD.sub(carried, str(line), count=1).lower().split()), carried


# A price, a count or a length asked of a bare thing is answered by the thing the chat is on: "im
# learning to drive" and then "how much do lessons cost" is the lessons card, and the line cannot
# reach it because the word that says which lessons they are ("driving") is not on it. The topic's
# own word goes in front of the thing, and only a thing the last answer named is widened - the
# answer already said "Lessons run 25 to 40 pounds an hour", so the line is about what was on the
# table, not a guess at what they meant.
# The words that say how the person feels about a thing rather than what it is: the reading
# engine's own two sets, so a verdict it learns to hear is a verdict here too.
A_VERDICT = NEGATIVE | POSITIVE


def _the_last_answer(memory):
    """The bot's last reply, or ''."""
    turns = (memory or {}).get("turns") or ()
    for one in reversed(turns):
        said = str((one or {}).get("bot") or "")
        if said:
            return said
    return ""


def _the_topics_on_the_chat(topic=None, memory=None):
    """The topic in hand first, then the ones the chat has been on, newest first."""
    out = []
    for one in reversed((memory or {}).get("topics") or ()):
        said = str((one or {}).get("text") or "")
        if said and said not in out:
            out.append(said)
    said = str(topic or "")
    if said in out:
        out.remove(said)
    if said:
        out.insert(0, said)
    return out


def _the_thing_a_measure_is_of(line, topic=None, memory=None):
    """The bare thing a measure ask names, when the chat has an answer to be a follow-up on."""
    if not _the_last_answer(memory):
        return None
    said = str(line or "")
    if not A_BARE_MEASURE.search(said.lower()):
        return None
    on_the_chat = set()
    for one in _the_topics_on_the_chat(topic, memory):
        on_the_chat.update(keywords(_the_topic_phrase(one) or one))
    for word in keywords(said):
        if word in MEASURE_WORDS or word in on_the_chat:
            continue
        return word
    return None


def _with_the_word_before(line, word, thing):
    """The line with `word` put in front of the thing it asks about, or None."""
    said = str(line or "")
    for found in re.finditer(r"[A-Za-z']+", said):
        if stem(found.group(0).lower()) == thing:
            return (said[:found.start()] + word + " " + said[found.start():]).strip()
    return None


def _how_they_feel(word):
    """True when the word says how the person feels about the thing rather than what it is.

    A topic's entry is keyed on the whole of what they said - "hate my job" - so the words it
    lends a follow-up include the verdict. "what should i do" widened with "hate" and "job"
    reached the entry for a strict teacher, because "hate" is a word on that key too, and the
    person who said they hated their job was told what to do about a teacher. The verdict words
    are the reading engine's own two sets, so a word it learns to hear as a verdict is not a
    subject here either.
    """
    word = str(word or "")
    if not word:
        return False
    if word in A_VERDICT:
        return True
    return any(form in A_VERDICT for form in forms(word))


def _keyed_to(keyed, word):
    """Whether a key holds the word, in any of the forms it takes ("driving" for "drive")."""
    word = str(word or "")
    if word in keyed or stem(word) in keyed:
        return True
    return any(word in forms(key) for key in keyed)


def _a_measure_of_the_topic(line, topic=None, memory=None):
    """The measure ask widened with a topic word, or None.

    The chat may have moved on since the thing was on the table - "im learning to drive", then
    "my test is in march", then "how much do lessons cost" - so the topics the chat has been on
    are tried newest first. Only an entry keyed to both the topic's word and the thing counts, so
    a topic the knowledge base knows nothing about widens nothing.
    """
    thing = _the_thing_a_measure_is_of(line, topic, memory)
    if thing is None:
        return None
    said = set(words(line))
    for one in _the_topics_on_the_chat(topic, memory):
        for word in keywords(_the_topic_phrase(one) or one):
            if word in said or word in MEASURE_WORDS:
                continue
            widened = _with_the_word_before(line, word, thing)
            if not widened:
                continue
            found = _entry(widened)
            if found is None:
                continue
            keyed = _key_words_of(found)
            if thing in keyed and _keyed_to(keyed, word):
                return widened
    return None


# A bare advice ask: the person asks whether to stop, give up, carry on, cut back, rest, and the
# thing it is about is the chat's, not the line's.
ADVICE_ONLY = re.compile(
    r"^(?:so|and|but|ok|okay|well|then|hmm|erm|um|oh|ah|right|alright|just|also)?[\s,]*"
    r"(?:should|shall|can|could|do|must)\s+i\s+"
    r"(?:stop|quit|give\s+up|carry\s+on|keep\s+going|keep\s+at\s+it|cut\s+back|hold\s+off"
    r"|rest|wait|go\s+on|start|start\s+again|bother)"
    r"(?:\s+(?:now|then|for\s+now|for\s+today|today|tonight|talking|chatting|going\s+on))?"
    r"[\s.!?]*$", re.I)


def _the_ask_with_its_doing(line, topic, last_id=None):
    """The bare advice ask read with the chat's own word, or None.

    The word that carries it is the one that takes the ask somewhere new: the topic's own card
    is what the chat has just been given, so a word that only reaches that card again ("should i
    stop knee" after the sore-knee card) says nothing the person does not have. "should i stop
    running" reaches the entry about stopping, which is what they asked.
    """
    if not ADVICE_ONLY.match(str(line or "")):
        return None
    whole = _entry(str(topic or ""))
    said = words(line)
    for word in keywords(str(topic or "")):
        if word in said:
            continue
        tried = str(line or "").strip() + " " + word
        found = _entry(tried)
        if found is None or found is whole:
            continue
        if last_id and getattr(found, "id", None) == last_id:
            # The answer they already have, said again: the word that changes nothing.
            continue
        return tried
    return None


def the_advice_ask_with_its_doing(understood, memory):
    """A bare "should i stop" read as the ask about the chat's own doing, or None.

    "my knees hurt when i run" then "should i stop" is whether to stop the running, and read on
    its own the line is a question about the conversation, which is why the bot answered it
    "You're not boring me. Take as long as it needs." The chat is what says which stop it is, so
    the reading takes the chat's own word - the one that reaches an answer the person does not
    already have - and the line as typed stays what every quote is kept from.

    Only where the carried ask reaches an entry. A stop that the chat's words cannot turn into a
    question ("should i stop" after "i hate my job") is left for the reply that can answer it
    honestly, which is the one about the person.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "").strip()
    if not line:
        return None
    record = memory.get("topic")
    if not isinstance(record, dict) or not record.get("text"):
        return None
    last = memory.get("last_answer")
    last_id = last.get("id") if isinstance(last, dict) else None
    doing = _the_ask_with_its_doing(line, str(record.get("text") or ""), last_id)
    if doing is None:
        return None
    reading = dict(understood)
    reading["clean"] = " ".join(doing.lower().split())
    reading["words"] = words(reading["clean"])
    return reading


def _the_answer_covers_it(line, memory, understood=None):
    """True when the answer just given already has the step this line narrows.

    "we are painting the kitchen this weekend" / "what about the ceiling": the ceiling is part of
    the room that answer was about, and its reply is the same sentence said for the ceiling
    ("Same for the ceiling: use a mid-sheen, eggshell or bathroom paint"). A fresh search for the
    words reaches the general how-to-paint card instead, which says less than the answer they are
    quoting back. A part of the plan the answer never touched - "any games" after the food for a
    picnic - is what the situation is for, and is left to it.

    The reading is `detail`'s own, so the two cannot disagree about which lines belong to the
    answer: this is the line `detail.answer_for` will answer, and it answers it better.
    """
    if not isinstance(memory, dict) or not memory:
        return False
    from . import detail  # local: the package imports this module
    # The reading the follow-up arrives in has its articles taken out ("what about ceiling"),
    # and a detail opens on one ("what about the ceiling"), so the line as it was typed is asked
    # too: the person's own words are the ones that say which part of the answer they mean.
    asked = [str(line or "")]
    typed = str(understood.get("text") or "") if isinstance(understood, dict) else ""
    if typed and typed not in asked:
        asked.append(typed)
    asked += [put_back for put_back in (_with_the_article(one) for one in asked) if put_back]
    return any(detail.answers_the_line(one, memory) for one in asked)


# "what about ceiling" is how a line arrives once the answers' module has rewritten the bare ask:
# the article goes with the ask words. A detail opens on one ("what about the ceiling"), so the
# guard asks the words back with it in rather than missing the line it is there to protect.
ABOUT_A_BARE_THING = re.compile(
    r"^(?P<open>(?:(?:ok|okay|so|and|but|also|well|yeah|right)\s+)*(?:what|how)\s+about)\s+"
    r"(?P<thing>(?!the\b|a\b|an\b|this\b|that\b|these\b|those\b|both\b|just\b)\w+)",
    re.I)


def _with_the_article(line):
    """The line with "the" put back before a bare thing ("what about ceiling"), or None."""
    found = ABOUT_A_BARE_THING.match(str(line or ""))
    if found is None:
        return None
    said = str(line)
    return found.group("open") + " the " + said[found.start("thing"):]


# "all the time", "most of the time", "these days": a frequency the thing happens with, not a
# thing the chat is on. The words are read off the phrase, so the same words said plainly ("what
# time is it", "on the day") still count as the topic's own.
A_FREQUENCY = re.compile(
    r"\b(?:all|most|half|the\s+whole|every|each|any|much\s+of)\s+(?:of\s+)?(?:the\s+)?"
    r"(?:time|times|day|days|week|weeks|month|months|while)\b"
    r"|\bat\s+the\s+moment\b|\bthese\s+days\b", re.I)


def _only_said_as_a_frequency(topic):
    """The words of the topic it says only inside a frequency phrase, which name no thing."""
    text = str(topic or "")
    left = set(words(A_FREQUENCY.sub(" ", text)))
    return {word for word in words(text) if word not in left}


PROPERTY_ASK = re.compile(r"^\s*(?:and|so|ok|okay|also|but)?\s*[,:]?\s*(?:what|which|how)\b")


def _asks_a_property_and_nothing_else(text):
    """"what temperature", "and how hot": a line that asks a property of the thing in hand.

    A line that states one ("he has a temperature") is not this: it is a thing about him, and the
    line after it is still about that. The understanding engine asks the same question of the line
    an answer leans on, with its own word list, so that neither package imports the other.
    """
    low = str(text or "").strip().lower()
    if not PROPERTY_ASK.match(low):
        return False
    found = keywords(low)
    return bool(found) and all(word in MEASURE_WORDS for word in found)


# The last situated readings, so one turn's two asks of the same line are answered once.
_elided_situated_cache = {}


def _an_elided_ask_situated(line, topic, understood=None):
    """The line read with the situation the chat is on ("any games kid"), or None.

    The line names the part it asks about and nothing else, so the entry is chosen by the part's
    own word and the situation only says which entry of that kind is meant: a birthday picnic
    with ten children is the games answer for children, not the one for a group of adults. The
    situation is put on one word at a time, because the whole of a topic's words reach a
    neighbour as often as not ("any games ten kid coming food bring" is a hotel's details), and
    the entry found has to be named by the line itself, so the added word picks the answer and
    never becomes the subject.

    The entry also has to answer a topic the chat is about. Without that, one word of the topic
    is enough to hand over a neighbour: "any tips" about a children's picnic reached the answer
    about tipping in a restaurant.
    """
    said = words(line)
    have = set(said)
    known = [word for word in keywords(str(topic or "")) if word not in have]
    if not known:
        return None
    if not isinstance(understood, dict) or not understood:
        # Without the reading there is nothing to say which situation the line is in, and a
        # guessed situation is how "any tips" becomes the answer about tipping.
        return None
    from ..knowledge.lookup import about_the_topic  # local: the knowledge base is not a memory
    stem_of = line.strip().rstrip("?.!").strip()
    # One situation word at a time, and only the first few of them: the matcher walks the whole
    # knowledge base per try, so a topic of twelve words is not worth ten seconds of the
    # conversation's time for a line this short.
    situation = (stem_of, " ".join(known[:8]), understood.get("topic"))
    memo = _elided_situated_cache.get(situation)
    if memo is not None:
        return memo or None
    found = None
    for word in known[:8]:
        text = stem_of + " " + word
        item = _entry(text)
        if item is None or not _names_it(said, item):
            continue
        if not about_the_topic(item, understood):
            continue
        if keeps_away(text, word, item):
            continue
        found = text
        break
    if len(_elided_situated_cache) > 32:
        _elided_situated_cache.clear()
    _elided_situated_cache[situation] = found or ""
    return found


# "and what about shoes", "what about a case", "how about the passport": the thing after it is a
# thing of its own, and what is asked is that thing for the subject already on the table - "shoes
# for running" - not the subject's own answer handed back. Read with the subject's words but not
# the thing's, the line reached nothing at all ("i want to start running" / "and what about
# shoes" was a search hedge, while "shoes for running" reaches the answer about kit).
ABOUT_NAMED = re.compile(
    r"^\W*(?:(?:and|but|so|oh|also|well|yeah|yep|ok|okay|right|alright)\W+)*"
    r"(?:what|how)\s+about\s+(?P<thing>[^.?!]+?)\s*$", re.I)


# The thing said with a pronoun on the end is the same thing: "what about a bed for it" after a
# dog is a bed, and the "for it" is the subject the sentence already carries.
_ABOUT_TAIL_PRONOUN = re.compile(r"\s+(?:for|about|with)\s+(?:it|them|him|her|that|this)\s*$", re.I)


ABOUT_MOST_WORDS = 5


# "what about the bathroom", "what about my passport": a definite thing is one the chat already
# has, so it is read against the answer just given rather than as a new thing of the subject's.
DEFINITE_OPEN = re.compile(r"^(?:the|my|our|your|his|her|its|their|this|that|these|those)\b", re.I)


# How much of an answer is compared when looking for the same one again: the opening clause is
# what the person reads first, and an answer that opens on the words already on the screen is the
# same answer however it ends.
ANSWER_OPENING = 90


def _the_same_answer_again(item, memory):
    """True when the entry's answer is the answer the person already has, or opens as it does."""
    reply = " ".join(str(getattr(item, "reply", "") or "").lower().split())
    if not reply:
        return False
    opening = reply[:ANSWER_OPENING]
    for turn in [one for one in (memory.get("turns") or []) if isinstance(one, dict)][-2:]:
        said = " ".join(str(turn.get("bot") or "").lower().split())
        if said and (opening in said or said[:ANSWER_OPENING] in reply):
            return True
    return False


def follows_on(understood, text):
    """True when the understanding engine read the line as carrying on, and the line itself
    points back at something ("it", "that", "there", "he")."""
    if not isinstance(understood, dict):
        return False
    text = DUMMY_IT.sub(" ", str(text))
    points_back = any(word in REFERRING_WORDS for word in words(text))
    if not points_back:
        return False
    if understood.get("followup"):
        return True
    ref = understood.get("ref")
    return isinstance(ref, dict) and bool(ref.get("followup"))


def keeps_away(line, topic, item=None):
    """True when the entry the widened line reaches keeps itself away from a word of the topic.

    The knowledge base says which lines an entry is not about ("roast a chicken" is keyed away
    from thighs), so an entry that excludes the topic's own words is a different thing of the
    same kind: 'how long do they go in for?' after chicken thighs must not get the timings for a
    whole bird. A wrong fact is worse than none.
    """
    if item is None:
        item = _entry(line)
    avoid = getattr(item, "avoid", ()) if item is not None else ()
    said = words(topic)
    return any(_kept_away_from(phrase, said) for phrase in avoid if isinstance(phrase, str))


def _kept_away_from(phrase, said):
    """True when the entry's avoidance phrase is one the topic says.

    An avoidance phrase written as a whole question is only that question when all of it is
    there: "how much should i save" says nothing about a topic whose only word is "save", and
    read on its content word alone it refused the savings goal's own timing, so "how long will
    it take?" after "im trying to save 500 pounds for a trip to spain" got a diet answer. A
    phrase of plain words ("thighs", "cast iron") still matches on the words it names.
    """
    if not any(word in STOPWORDS for word in words(phrase)):
        return _said(phrase, said)
    wanted = [stem(word) for word in words(phrase)]
    if not wanted or not all(word in (stem(one) for one in said) for word in wanted):
        return False
    return _said(phrase, said)


def _names_it(found, item):
    """True when the line itself says a word of the entry key (not only the subject put back in).

    Widening adds the topic's subject, so a line about a two-year-old pay review can land on an
    entry keyed to offers and negotiation: it shares only the words that were added. Such an
    entry has not been named by the person, so it is not the one to answer from.

    A line that is *only* the ask - "any tips", "any advice?" - names nothing else, so the
    card keyed to that phrase is the answer it points at and still counts. The skip is for a
    line that puts the ask around a subject of its own: "any tips for a long shift" is about
    the shift, and "tips" there says how the question is put.
    """
    content = set(found) - STOPWORDS
    asked_only = not (content - (ASK_PART | ASKS_FOR_ADVICE))
    for part in getattr(item, "key", ()):
        for phrase in (part if isinstance(part, tuple) else (part,)):
            if not isinstance(phrase, str):
                continue
            named = set(words(phrase)) - STOPWORDS
            if named and not named - (ASK_PART | ASKS_FOR_ADVICE) and not asked_only:
                continue  # "how long", "any tips for": the ask, not the thing
            if _said(phrase, found):
                return True
    return False


def _key_words_of(item):
    """Every word an entry's key says it is about."""
    found = set()
    for part in getattr(item, "key", ()) if item is not None else ():
        for phrase in (part if isinstance(part, tuple) else (part,)):
            if isinstance(phrase, str):
                found.update(words(phrase))
    return found


def _names_it_as_written(found, item):
    """True when the line says a word of the entry's key as it is written, not a form of it.

    "i charge it every night" after a phone battery reaches the price of clearing a drain: the
    subject put back in the line ("... battery draining") meets `drain` through the form
    "draining", and the line's own "charge" names the price group of the same entry. A drain is
    not a thing that drains, and a price asked with no job in it is not a question about a job,
    so a price word on its own only counts when the subject is the key word itself.
    """
    for part in getattr(item, "key", ()):
        for phrase in (part if isinstance(part, tuple) else (part,)):
            if not isinstance(phrase, str) or not _said(phrase, found):
                continue
            have = {str(word).lower() for word in found}
            if any(word.lower() in have for word in words(phrase)):
                return True
    return False


def _asked_only(found, item):
    """True when the only parts of the entry key the line matches are asking words.

    "how much does a plumber charge" matches the plumber's key twice over, the job and the
    price, so it is a price question that names a job. "i charge it every night" matches the
    price group alone: the line asks for nothing and names no job, and what it is about has to
    come from the job word of the conversation, said as the entry writes it.
    """
    named = False
    for part in getattr(item, "key", ()):
        for phrase in (part if isinstance(part, tuple) else (part,)):
            if not isinstance(phrase, str) or not _said(phrase, found):
                continue
            if set(words(phrase)) <= (ASK_PART | PRICE_ASK):
                continue  # "how long", "how much", "cost": the ask, not the thing
            named = True
    return not named


def _the_step_they_report(line):
    """True when the line reports a step it has taken rather than asking about the topic.

    A report is a turn of its own, not a follow-up question: "i did ring them though, twice"
    after a benefits decision came back as "i did ring them though, twice theyve stopped
    because", and that line reached the ceramic-hob card on its "ring" and the topic's
    "stopped". What the report wants is the next turn of the thread, which is `already`'s to
    answer, so widening stands aside for it.
    """
    try:
        from . import already, repeat  # lazy: both read the store, which reads this module
        return bool(already.the_step_they_took(line) or repeat._tried(line))
    except Exception:  # noqa: BLE001 - a reading that fails just widens as it always did
        return False


# A follow-up that adds nothing but a limit on the question just answered: the time they have
# ("i only have ten minutes"), the size they have ("its a 2kg one") or being in a hurry. The
# topic's own question is asked again with the limit on it, and the knowledge base answers the
# pair: "whats a quick breakfast" with "i only have ten minutes in the morning" is the breakfast
# answer, not the ten-minute dinner entry that "ten minutes" on its own reaches.
CONSTRAINT = re.compile(
    r"\b(?:\d+|one|two|three|four|five|ten|fifteen|twenty|thirty|forty|fifty|sixty|ninety"
    r"|an hour|half an hour)\b[^.!?]{0,14}?\b(?:minutes?|mins?|hours?|hrs?)\b"
    r"|\b\d+(?:\.\d+)?\s?(?:kg|g|lb|lbs|oz|pints?|litres?|l|ml)\b"
    r"|\bin a (?:hurry|rush)\b|\bshort (?:of|on) time\b|\bno time\b"
    r"|\bnot (?:much|long) time\b", re.I)


# What a line can be made of and still be nothing but the limit: "i only have", "its a", "im in a".
CONSTRAINT_FILLER = frozenset("""a an the and but so though then just only really very about
at for in on of to be been is are was were have has had got get ive i im it its me my
that this there here now today tonight morning afternoon evening lunchtime midday night
week weeknight weekday left spare weve we you he she they one some more like most
think guess say said times""".split())


def adds_only_a_constraint(line):
    """The limit the line names, when the line is made of nothing but that limit."""
    text = str(line or "")
    match = CONSTRAINT.search(text)
    if match is None:
        return None
    rest = words(text[:match.start()] + " " + text[match.end():])
    if [word for word in rest if word not in CONSTRAINT_FILLER and not word.isdigit()]:
        return None
    return match.group(0)


def _constrains_the_ask(line, topic_text):
    """The question just answered, asked again with this line's limit on the end.

    A follow-up that only says how much time or how big the thing is is a second question about
    the same entry, so the entry is asked with the limit in it and the answer is the one for that
    limit: after the roast chicken answer, "its a 2kg one" is the 1 hour 40 the answer already
    works out, and after "whats a quick breakfast", "i only have ten minutes" keeps breakfast
    instead of reaching the ten-minute dinner entry that "ten minutes" alone finds. An entry the
    question just answered was not on is refused: a limit is not a new subject.
    """
    if adds_only_a_constraint(line) is None:
        return None
    asked = str(topic_text or "").strip()
    if not asked:
        return None
    mine = _entry(asked)
    text = asked + " " + str(line).strip()
    item = _entry(text)
    if item is None or (mine is not None and item is not mine):
        return None
    return text


SENTENCE = re.compile(r"(?<=[.!?])\s+")


# A sentence said on its own does not open with the word that joined it to the one before. The
# sentence picked out of an answer is said bare ("Then set up one meet-up with a classmate" is a
# new thing about the same subject, and framing it as a repeat would hide that), and the joining
# word only made sense in front of the sentence it followed: the child-worry answer reads "...being
# told it is nothing teaches them to hide it. Then take one small step towards whatever they are
# avoiding...", and "what can i do to help him settle" was answered with that second sentence
# whole, opening on a "Then" with no then before it. The first step of an answer is already said
# without its joining word (see `_first_step`), and so is any one sentence of it.
JOINED_ON = re.compile(r"^(?:and|then|so|but|also|now|next|plus|instead|otherwise)"
                       r"(?:\s*,\s*|\s+)", re.I)


NUMBER = re.compile(r"\d")


# A time, not just a number: "40 to 45 minutes", "1 hour 40", "20 mins". A count of people or a
# tin size is a number too, and a "how long" answered with "serves 8 to 10" is not an answer.
TIME = re.compile(r"\d[^.]{0,15}?\b(?:min\w*|hour\w*|hrs?)\b", re.I)


# The same time with the whole of it: "40 to 45 minutes", "1 hour 40", "1 hour 40 minutes".
# An amount the line names for itself: "a 1.5kg one", "4 pints", "600". A question that names one
# is owed the figure for that amount, not a time that happens to be in the next sentence.
AMOUNT = re.compile(r"\b\d+(?:\.\d+)?\s?(?:kg|g|lb|oz|pints?|litres?|l|ml|inches|inch|cm|mm)\b",
                    re.I)


# A figure in a unit an answer gives an amount in: "1 to 2 mg", "500mg", "3 pouches",
# "300 calories". The shared-word pass picks by verbs, so "how much should i take" after a
# melatonin answer chose the "take blood thinners" warning; the dose is the sentence with a
# unit in it, and this is what finds it.
AMOUNT_ANSWER = re.compile(
    # A price is a figure too: "how much is it" after the TV licence card wants "About £175 a
    # year", and the sentence holds a currency sign rather than a unit of weight or volume.
    r"(?:[\u00a3$\u20ac]\s?\d+(?:[\d,.]*)?(?:\s*(?:-|to|and|\u2013)\s*[\u00a3$\u20ac]?\s?"
    r"\d+(?:[\d,.]*)?)?"
    r"|\b\d+(?:\.\d+)?(?:\s*(?:-|to|and|\u2013)\s*\d+(?:\.\d+)?)?\s*"
    r"(?:mg|mcg|\u00b5g|g|kg|ml|l|litres?|liters?|tbsp|tsp|tablespoons?|teaspoons?|cups?|"
    r"parts?|people|slices?|tins?|oz|lbs?|pounds?|tablets?|capsules?|drops?|puffs?|sprays?|"
    r"units?|iu|kcal|calories|pouches?|sachets?|scoops?)\b)", re.I)


# A rate answers any amount of the same thing: "20 minutes per 500g" is the answer to "how long
# for a 1.5kg one" when the sentence about this size is not in the answer.
RATE = re.compile(r"\bper (?:kilo|kg|500g|pound|lb|person|head|each)\b", re.I)


# A cooking rate with the weight it is per, so a size named in a follow-up can be worked out:
# "20 minutes per 500g" is 3 times that for 1.5kg. An answer written per pound or per ounce is
# worked out in the same units it was given in.
RATE_BY_WEIGHT = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)\s+per\s+"
                            r"(\d+(?:\.\d+)?)\s*(kg|g|lb|lbs|pound|pounds|oz|ounce|ounces)\b", re.I)


# The size an answer has already worked its rate out for ("...so a 2kg bird takes roughly 1 hour
# 40", "About 1 hour 25 for 3.5lb: ..."). Asking for that size again wants the figure, not the
# rule; asking for another size wants it worked out.
OWN_SIZE = re.compile(r"\b(?:so an?\s+|for\s+)(\d+(?:\.\d+)?)\s*"
                      r"(kg|g|lb|lbs|pound|pounds|oz|ounce|ounces)\b", re.I)


# "plus 20 minutes on top": a fixed time every size needs, before the per-weight part.
PLUS_MINUTES = re.compile(r"\bplus\s+(\d+)\s*(?:minutes?|mins?)\b", re.I)


WEIGHT_IN_GRAMS = {"g": 1.0, "kg": 1000.0, "lb": 453.59237, "lbs": 453.59237,
                   "pound": 453.59237, "pounds": 453.59237, "oz": 28.3495,
                   "ounce": 28.3495, "ounces": 28.3495}


TIME_SPAN = re.compile(r"\b\d+(?:\.\d+)?(?:\s*(?:-|to|and)\s*\d+(?:\.\d+)?)?\s*"
                       r"(?:minutes?|mins?|hours?|hrs?)(?:\s+(?:and\s+)?\d+(?:\s*(?:-|to)\s*\d+)?"
                       r"\s*(?:minutes?|mins?)?)?", re.I)


# The duration in an answer: "20 minutes", "1-2 hours", "half an hour". A "how long" follow-up
# after an answer that has already been given once needs the part of it with the time in it.
DURATION = re.compile(
    r"\b(?:\d+(?:\s*(?:-|–|to)\s*\d+)?|half an|an?)\s*"
    r"(?:minutes?|mins?|hours?|hrs?|seconds?|days?|weeks?)\b"
    # A span is also written in words - "it usually settles in two to three days" carries no time
    # at all to the pattern above, so a "how long" follow-up was never offered it and handed back
    # the sentence about when to see a GP instead. Days and weeks only: "a few seconds" is a
    # snippet of advice ("do short practice exits, back in a minute") and not a length either.
    r"|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a few|a couple of|"
    r"several|couple of)"
    r"(?:\s*(?:-|–|to)\s*(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten))?\s*"
    r"(?:days?|weeks?)\b", re.I)


# A length written as an adjective before its noun: "a 20-minute job", "a 10-minute walk".
# It is a duration the answer states, but DURATION above does not read it, so a "how long"
# follow-up found no clause to give and fell back to a sentence chosen by a shared word.
SPAN_ADJECTIVE = re.compile(
    r"\b\d+\s*[-\u2013]\s*(?:minute|min|hour|hr|day|week|month|year)s?\b", re.I)


# A line that really asks for a length. The understanding engine labels "where do i start" as
# how_long too, and the strict duration picker must not turn a savings answer's "two weeks"
# into the answer to a question about where to begin.
LENGTH_ASK = re.compile(
    r"\bhow long\b|\bhow much time\b|\bhow many (?:minutes?|mins?|hours?|hrs?|days?|weeks?)\b"
    r"|\btime\b|\bduration\b", re.I)


# A length said as a threshold - "more than a week", "longer than three days", "at least a
# fortnight" - tells the person when to worry, not how long the thing lasts. It carries the verb
# the question used ("how long does it last" meets "it lasts more than a week"), so it used to
# win the ask on that shared word and the warning was handed over instead of the span.
THRESHOLD_SPAN = re.compile(
    r"\b(?:more than|longer than|fewer than|less than|at least|at most|over|under|beyond|up to)\s+"
    r"(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|a few|several|couple of)?\s*"
    r"(?:minutes?|mins?|hours?|hrs?|days?|weeks?|months?|fortnights?|years?)\b", re.I)


# Where a sentence can be cut into the clauses that answer different asks: "Brown the mince,
# then add the tomatoes: 20 minutes gives bolognese" carries a step and a time.
CLAUSE = re.compile(r"\s*(?:,|;|:|\u2014| - )\s*"
                    # "a week or two" is one length, so an "or" between two numbers is a span
                    # and not a clause break: splitting there left "for a week" as the answer.
                    r"|\s+or\s+(?!\d|\b(?:a|an|one|two|three|four|five|six|seven|eight|nine|"
                    r"ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|hundred|half|couple|"
                    r"several|few)\b)")


# A bracketed aside is not a clause. Its commas belong to the aside, so a cut at one leaves half
# a bracket: the shoulder answer's "the pendulum swing (lean forward, let the arm hang, circle it
# slowly) a few times a day" came back to "how long will it last" as "Circle it slowly) a few
# times a day." - a fragment with a stray bracket in it. The aside's own commas are shielded from
# the split and put back after it, so a time that lives inside the brackets still counts.
ASIDE = re.compile(r"\([^()]*\)")


SHIELD = "\x00"


def _clauses_of(sentence):
    """The clauses of a sentence, with a bracketed aside kept whole."""
    shielded = ASIDE.sub(lambda found: found.group(0).replace(",", SHIELD), str(sentence or ""))
    return [piece.replace(SHIELD, ",") for piece in CLAUSE.split(shielded)]


# A time in the tail of a warning list - "see a physio if the pain is sharp, that leg swells up
# after every run, or it is still there in two weeks" - is the point at which to worry, not the
# length they asked for. The split on " or " hands it back as a clause of its own, and said on
# its own it is a fragment: "how long will that take" was answered "Or it is still there in two
# weeks."
WARNING_SPAN = re.compile(
    r"\b(?:still there|still not|still the same|not better|no better|not gone|not settled|"
    r"not cleared|gets? worse|getting worse|keeps? (?:on|coming)|comes? back|bleeds?"
    r"|is a reason to|ring (?:the )?(?:surgery|gp|doctor|nhs|111|999)"
    r"|(?:ring|call|see|contact|speak to) (?:a |the |your )?(?:gp|doctor|nurse|pharmacist|"
    r"surgery|111|999|a&e|hospital))\b",
    re.I)


# How often, which is a different question from how long: "three times a week" is not a
# duration, and a "how often should i go" answered with "3 months" answers nothing. Only a
# phrase that carries the repetition itself, so "a couple of times" and "every other day"
# come whole and "20 minutes" never looks like one.
FREQUENCY = re.compile(
    r"\b(?:once|twice)\s*(?:a|per|every)\s*(?:day|week|month|year|fortnight|weekend|morning|"
    r"evening|night)\b|"
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|a couple of|a few)\s*times?"
    r"\s*(?:a|per|every)\s*(?:day|week|month|year|fortnight|weekend|morning|evening|night)\b|"
    r"\bevery\s+(?:other\s+)?(?:day|week|month|morning|evening|night|year)\b|"
    # A counted interval is how often too: "treat bare fence timber every two or three years" is
    # a cadence, and the sentence was the only one with a time in it, so "how long will it take"
    # to paint a shed was answered "Two or three years." The same shape covers "every couple of
    # days" and "every 2 weeks".
    r"\bevery\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twelve|couple of|"
    r"few|several|a couple of|a few)(?:\s*(?:-|to|or)\s*(?:\d+|one|two|three|four|five|six|"
    r"seven|eight|nine|ten|twelve))?\s+(?:days?|weeks?|months?|years?|nights?|mornings?|"
    r"evenings?)\b|"
    r"\b(?:daily|weekly|nightly|monthly)\b",
    re.I)


# A line about something that has not happened, or might not: repeating the last answer does not
# answer it ("what if the cake sinks?" is not the cake recipe again). A question about a quantity
# or a duration is not one of those: "how long will it take?" asks for the time, so "will it
# take" must not be read the same way as "will it work?".
NOT_A_QUANTITY = r"(?!\s+(?:take|last|need|cook|roast|bake|boil|keep|stay|be done|finish|work out))"
