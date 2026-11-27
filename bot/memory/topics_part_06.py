"""Part 6 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from .filler import without_the_shrug
from . import quotes as quoted
from .topics_part_01 import (
    ABOUT_ANOTHER, MEASURE_WORDS, PART_OF_THE_ONE, REFERRING, keywords, words, ABOUT_THE_CHAT,
    ASK_CUE, PROCEED, LONG_IT_TAKES, STAY_ASK, forms, stem, ASK_ONLY, MEASURED, DETAIL,
    _after_an_emergency, is_ack,
)
from .topics_part_02 import (
    _entry, _leads_a_question, _leans_back, _said, key_subject, _after_a_correction,
    opens_by_switching,
)
from .topics_part_03 import (
    _a_measure_of_the_topic, _an_elided_ask_situated, _the_answer_covers_it,
    _the_ask_with_its_doing, elided_ask, _a_length_of_the_job, _asks_a_property_and_nothing_else,
    _key_words_of, _names_it, _only_said_as_a_frequency, _the_topic_phrase, _the_ways_of_saying_it,
    _where_the_topic_lands, a_stay_with_the_place, keeps_away, names_nothing, the_city_of,
    the_country_of, _asked_only, _names_it_as_written, _the_step_they_report, SENTENCE, follows_on,
)
from .topics_part_04 import (
    _the_trip_of_theirs, ASKS_A_FREQUENCY, HYPOTHETICAL, _answer_about, _opening_instruction,
    _says_it_again, _the_turn_that_answered, about_a_place_they_left_behind, answer_in_hand,
    entry_answer, newest_answer, pairing, said_again,
)
from .topics_part_05 import (
    MONTH_NAMES, _a_sky_ask, _doing_part, _earlier_subject_sentence, _pick_sentence,
    _repeats_the_question, _the_thing_the_chat_moved_to, _worked_out_for_this_line, asks_only,
    carried_topic, left_for_a_blank, sized_reply, _only_the_topics_own_words, bare_question,
    WEATHER_ASKS, WEATHER_WORDS, the_place_and_month, the_weather_ask, NOW_AND_HERE,
)


def _names_another_subject(text, record, memory=None):
    """True when a line that leans back is really about a different thing of its own.

    "how long do i boil an egg" then "my kitchen tap is dripping and its driving me mad" reads as
    a follow-up - the "its" is enough to make it lean - and carries no switching word, so the tap
    line was merged into the egg's record: the record kept the egg's text, gained the tap's
    words, and the next question ("how do i fix it?") was answered from the egg. A line that
    reaches a knowledge entry of its own, while the record reaches a different one, is about that
    other thing, however it leans. The check is on the entries, not on the words, because
    "my oven is fan assisted" reaches nothing and is the detail about the oven it is.
    """
    if (_leads_a_question(text) and _leans_back(text, record)
            and _points_at_the_record(text, record, memory)):
        # A question that leans back is a question about the thing the chat is on, even when it
        # names another entry: "should i do the potatoes in with it" after the chicken is about
        # the chicken, and it must not become a potato topic of its own. A question that names
        # another entry and points at nothing here is its own subject, however it opens: "can i
        # freeze rice" after "how do i descale the kettle" is the rice, not the kettle, and
        # reading it as a detail of the kettle left the chat on the kettle for good, so the next
        # "is that bad" was answered from the kettle's card.
        return False
    mine = _entry(text)
    if mine is None:
        return False
    theirs = _entry(str(record.get("text") or ""))
    return theirs is not None and theirs.id != mine.id


def _points_at_the_record(text, record, memory=None):
    """True when the line points at the thing the chat is on, not merely reads as a property ask.

    A "how long" question is shaped like a property ask, and that shape alone was enough to say
    the line was about the thing in hand: "my washing machine smells" then "is it worth getting a
    smart meter" then "how long do i boil an egg" kept the washing machine as the subject, so the
    egg line was answered with the washing-machine card, two turns after the machine. A measure of
    the thing ("how long for a 2kg chicken"), a pronoun ("how long should i leave it in"), a part
    of it ("the rest", "the leftovers"), a word the record already holds, or a word from the answer
    on the screen ("how much water" after the rice, whose answer gives the ratio) is the line
    pointing at it. A property ask with none of those is a question about something else.
    """
    found = words(text)
    if a_placeholder_pronoun(text):
        # "is it worth getting an air fryer": the "it" is a hole for the thing the line names
        # after "getting", not a pointer back at the chat's subject. Read as a pointer it kept
        # the line tied to whatever came before, so after a child-and-veg line the air fryer
        # question was answered from the veg card ("Five a day is 400g"), and a smart meter
        # question was answered about the washing machine. The same words in the shape "should
        # i get an air fryer" already moved the subject; only the shape differed.
        found = [word for word in found if word != "it"]
    if any(word in REFERRING for word in found):
        return True
    if PART_OF_THE_ONE.search(" ".join(found)):
        return True
    if ABOUT_ANOTHER.search(" ".join(found)):
        return True
    mine = set(keywords(text))
    if not mine - MEASURE_WORDS:
        # "what temperature", "how long", "how much" on its own: the line asks for a detail and
        # names no thing of its own, so the detail is of the thing in hand.
        return True
    if mine & set(record.get("words") or ()):
        return True
    said = ""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if isinstance(turns, list) and turns and isinstance(turns[-1], dict):
        said = str(turns[-1].get("bot") or "")
    return bool(mine and said and mine & set(words(said)))


def carry_the_ask(line, topic, understood=None, memory=None):
    """A follow-up that names nothing takes the topic's own words with it, or None.

    'how often should I go?' after 'I want to start running' is read as 'how often should I go
    running', which the knowledge base answers. Only the words of the topic the knowledge base
    knows on their own are added, so a topic that mixes a subject with its trouble keeps both
    ('why is that happening?' after a flat sourdough is read as 'why is that happening sourdough
    flat'), and a line that names its own subject is only carried when the whole of it reaches
    an entry that the line itself named.
    """
    lowered = str(line or "").lower()
    if ABOUT_THE_CHAT.search(lowered):
        return None
    # "What should I do about it?" is a request to carry on with what the bot has already said,
    # not a fresh question about the topic's words: carrying them asks the back-pain entry again
    # and the paragraph comes back word for word. It is left to the next-step reply.
    if any(phrase in lowered for phrase in PROCEED):
        return None
    # Only an ask is carried. A line that only states something ("we have a 3 year old" after a
    # cat) names nothing either, and reading it as the topic's ask gave the cat's vet advice to
    # somebody telling the bot about their child.
    elided = elided_ask(line)
    if not ASK_CUE.search(str(line or "").lower()) and not elided:
        return None
    # The line read with the topic's own words first, and the situation only when that finds
    # nothing: the topic's words already reach the answer often enough ("im planning a kids
    # party" / "any games" is the party games), and a situated read in front of it took the
    # party games off them and handed over the board games for a group of adults. What the
    # situation may do is find an answer the topic's words cannot reach at all.
    carried = _carry_the_words(line, topic)
    if carried is not None:
        return carried
    # "should i stop", "should i give up", "should i carry on" name the advice and not the thing
    # it is about. After the card about a sore knee the line is about the running, and the bot
    # answered it "You're not boring me. Take as long as it needs" - the stop read as the talk,
    # because a follow-up is the whole line and the reader that keeps the whole line is the one
    # that decides a "should i stop" is about the conversation.
    doing = _the_ask_with_its_doing(line, topic)
    if doing is not None:
        return doing
    # A price or a count of a bare thing the answer already named is the thing with the topic's
    # word in front of it ("how much do lessons cost" after "im learning to drive").
    measured = _a_measure_of_the_topic(line, topic, memory)
    if measured is not None:
        return measured
    if elided and not _the_answer_covers_it(line, memory, understood):
        return _an_elided_ask_situated(line, topic, understood)
    return None


def _carry_the_words(line, topic):
    """The line widened with the topic's own words, or None when they reach no entry.

    The whole of the ordinary carry, and the place the topic's own words get their first say:
    only a line that reaches nothing here is read with the situation the chat is on.
    """
    # The stay-length ask below is read off the line as typed, and the name it reads it into was
    # never bound here: any chat whose topic named a city raised a NameError on the way through
    # this reader, so the carry was lost for that line and everything after it.
    lowered = str(line or "").lower()
    # "how long does it take?" is the one shape where the subject goes in the pronoun's place
    # rather than on the end of the line: "how long does it take house" reaches a different
    # entry (how long a container keeps something), and "how long does it take buying a house"
    # reaches it too. The entry still has to be keyed to the topic's own words, the same guard
    # the rest of this reader uses, so a topic the knowledge base knows nothing about carries
    # nothing.
    long_take = LONG_IT_TAKES.match(str(line or ""))
    if long_take:
        phrase = _the_topic_phrase(topic)
        tried = long_take.group("head") + " " + phrase + " take" if phrase else ""
        found = _entry(tried) if tried else None
        if found is not None and _a_length_of_the_job(found) and not keeps_away(tried, phrase, found):
            keyed = _key_words_of(found)
            carried = set(keywords(phrase))
            # Every word of the phrase has to be one the entry is keyed to, in the form it says
            # it ("learning" for the entry's "learn"), so the entry is about the whole thing the
            # chat is on and not about one word of it.
            if len(carried) >= 2 and all(word in keyed or stem(word) in keyed or forms(word) & keyed
                                         for word in carried):
                return tried
    # A stay-length ask asks how long to give the place the chat is on, and the place's own
    # answer is reached with the place in the line. The topic's words put on the end reach the
    # trip plan instead, and its advice is then read back as the answer to the length.
    lowered = str(line or "").lower()
    if (the_city_of(topic) is not None or the_country_of(topic) is not None) \
            and STAY_ASK.search(lowered):
        stay = a_stay_with_the_place(line, topic)
        if stay is not None:
            return stay
        # The chat is on a city and the line asks how long: either the line carries a subject of
        # its own ("how many days should i rest my ankle"), or the city is not a place they are
        # going ("i live in edinburgh"). Neither is answered by the trip table, and the ordinary
        # carry would put the city on the front of the line ("rome how many days should i rest
        # my ankle") and answer the ankle with a holiday. Both are left to the readers below.
        return None
    said = words(line)
    have = set(said)
    # A month or a season is a condition on their plan, not its subject - unless the plan has no
    # place in it yet: "im thinking of a holiday in october" and then "where should I go" is a
    # question about October, and dropping the month there answered with holidays in general
    # ("two things decide it: how long you have, and whether you want sun or a city").
    elsewhere = _the_trip_of_theirs(str(topic or "")) and not _a_sky_ask(line)
    # A topic that only asked a property ("what temperature") lends no word to the line after
    # it: "how long" then meant a roast chicken's timing and reached the entry keyed on a
    # temperature, which answered it with the fever card. A temperature somebody has is a thing
    # about them, so a topic that states one keeps it.
    lends_no_property = _asks_a_property_and_nothing_else(str(topic or ""))
    known = [word for word in keywords(str(topic or "")) if word not in have
             and not (lends_no_property and word in MEASURE_WORDS)
             and not (elsewhere and (word in MONTH_NAMES or word in SEASONS))]
    if not known:
        return None
    # When the topic itself reaches an entry, only the words that entry is keyed to are carried:
    # "bathroom" in "the bathroom tap has been dripping" is where the tap is, not the subject,
    # and carrying it would read "do i need to turn the water off first?" as the cleaning entry.
    # The topic is re-read only for a follow-up that names nothing of its own ("why is that
    # happening", "why", "and what can i do"): a line that brings a subject of its own is
    # answered from the anchor the topic itself reaches, so "what should i change?" after a
    # flat loaf still gets the starter's answer and only the bare why moves.
    anchor = (_where_the_topic_lands(str(topic or "")) if names_nothing(line)
              else _entry(str(topic or "")))
    if anchor is not None:
        keyed = _key_words_of(anchor)
        extra = [word for word in known
                 if word in keyed or stem(word) in keyed or _said(word, keyed)]
        frequency = _only_said_as_a_frequency(topic)
        if extra and frequency and all(word in frequency for word in extra):
            # "my laptop fan is loud all the time" reaches the "what time is it" entry through
            # "all the time", which is how often the fan is loud and not a thing the chat is on:
            # the clock lent the line nothing but a frequency, and the follow-up after any line
            # ending that way carried no subject at all ("what helps" then got the search shrug
            # where the answer was one turn back). A word said only inside a frequency phrase is
            # not the subject, so the topic is read as one that lands nowhere.
            extra = []
        if not extra:
            # The topic lands on an entry that shares none of its own words: "my laptop fan is
            # loud all the time" reaches the clock entry through "all the time", which is a
            # frequency and not what the chat is on, and the clock is keyed to nothing else in
            # it. With nothing to lend, the entry is not the topic's subject, so the topic's own
            # words are carried, exactly as for a topic that lands nowhere. Without this the
            # follow-up after any line ending "all the time" carried nothing at all and the
            # person got the search shrug where the answer was a turn back.
            anchor = None
            extra = known
    else:
        extra = known
    if not extra:
        return None
    stem_of = line.strip().rstrip("?.!").strip()
    # The whole of the topic first, then the words of it taken together: a subject said with
    # the trouble it is in ("sourdough ... flat") reaches its entry, and the words that only
    # say how long it has been going on ("keeps coming") are left out when the whole is too much.
    cands = [extra] + [[one, two] for one in extra for two in extra if one != two] \
        + [[one] for one in extra]
    text = item = borrowed = None
    for tried, carried in _the_ways_of_saying_it(stem_of, str(line or ""), cands):
        borrowed = carried
        found = _entry(tried)
        if found is None:
            continue
        # Every word carried over has to be a word the entry is keyed to: "flat" from "flat
        # tyre" is the entry's flat, but "bike" is not, so the soup-that-tastes-flat entry is
        # not the answer to "can you fix it?" after a tyre.
        keyed = _key_words_of(found)
        if not all(word in keyed or stem(word) in keyed or _said(word, keyed)
                   for word in carried.split()):
            continue
        text, item = tried, found
        break
    if item is None:
        return None
    # Only the carried words the entry is keyed to: "start running" reaches the exercise entry
    # through "running", and "start" says nothing about it.
    keyed = _key_words_of(item)
    lean = [word for word in borrowed.split()
            if word in keyed or stem(word) in keyed or _said(word, keyed)]
    if 0 < len(lean) < len(borrowed.split()):
        tried = stem_of + " " + " ".join(lean)
        found = _entry(tried)
        if found is not None:
            text, item, borrowed = tried, found, " ".join(lean)
    # A line that asks something of its own is carried only when its own words say a word the
    # entry is keyed to: the words the carry added cannot be the only thing that reached it.
    # "how often should i practise" after "i want to learn piano" names "practise", which the
    # entry is keyed to, so it is carried and answered. "right, any tips for a long shift" after
    # a knee answer is another ask, about a shift, and nothing in it names the knee, so the
    # carry put the knee into a question nobody asked. The entry the topic itself reached is not
    # exempt: it is the old subject, and this line has its own.
    #
    # A line that asks nothing is not doing that. "nah just tired" after the dinner ideas is a
    # reaction to the answer in hand, not a question about tiredness, and it stays on the topic
    # it was said in: carried, the turn belongs to the conversation; carried no longer, the
    # fatigue card answers a complaint nobody made.
    if not _names_it(said, item) and not names_nothing(line) and item is not anchor:
        return None
    # The entry has to be about the same thing as the entry the topic itself reached: two
    # words keyed alike ("running" and "jog" for a run and for how often to run). One shared
    # word is not enough - "beef" in a beef stew is not the beef in a steak, "tap" in a dripping
    # tap is not the tap in cleaning the sink - and a wrong fact is worse than none.
    if anchor is not None and item is not anchor:
        if len(_key_words_of(item) & _key_words_of(anchor)) < 2:
            return None
    elif anchor is None and len(_key_words_of(item) & set(keywords(str(topic or "")))) < 2:
        # A topic with no entry of its own is carried only to an entry keyed to two of its
        # words: a flat sourdough reaches the flat loaf, a beef stew does not become a steak.
        # A topic that names one thing has no second word to share: "also i want tomatoes" is
        # the tomato entry, and it is the whole of what that turn was about.
        if len(set(keywords(str(topic or "")))) > 1:
            return None
    # The entry is judged against the words carried over, not against every word of the topic:
    # "my sourdough keeps coming out flat" says "keeps" about the trouble, and the entry that
    # avoids "keep" (how long a loaf lasts) is still the right one to answer from.
    if keeps_away(text, borrowed, item):
        return None
    return text


def widen(line, subject_words, topic_text):
    """The line with the whole of the topic's subject on the end, when that reaches an entry.

    A follow-up names no subject of its own, so it is read together with everything the topic
    was about: 'and if I stuff it?' after a chicken is the stuffing entry, 'he's allergic to
    nuts' after a birthday cake is the nut-free cake. The subject is put back whole, never cut
    down to the word that happens to find something: a beef stew shares 'beef' with the steak
    entry, and a stew is not a steak. An entry keyed away from the topic's own words, or one
    the line itself does not name, is refused too.
    """
    if a_placeholder_pronoun(line):
        # "its freezing out isnt it" then "is it worth getting a dog": the topic's word went on
        # the end and made the card for walking a dog in the cold, about a question nobody put.
        return None
    if _the_step_they_report(line):
        return None
    topic_entry = _entry(topic_text)
    have = words(line)
    # A month or a season in the topic is a condition on their plan, not its subject: "we are
    # going to spain in june" and then "what should we do there" is a question about Spain, and
    # carrying "june" into it turned the line into "where should I go in june", which was
    # answered with "the Greek islands, the Algarve or the Baltic cities" - places they had
    # already chosen against.
    # Only when the topic already says where: with no place in it yet, the month is the whole of
    # what the follow-up is asking about ("a holiday in october" -> "where should I go").
    elsewhere = _the_trip_of_theirs(topic_text) and not _a_sky_ask(line)
    extra = [word for word in subject_words
             if word not in have and not (elsewhere and (word in MONTH_NAMES or word in SEASONS))]
    if not extra:
        return None
    text = line + " " + " ".join(extra)
    item = _entry(text)
    if item is None or item is topic_entry:
        return None
    if not _names_it(have, item):
        return None
    if _asked_only(have, item) and not _names_it_as_written(extra, item):
        return None
    if keeps_away(text, topic_text, item):
        return None
    return text


def same_as_before(understood, memory):
    """The part of the last answer that this follow-up asks about, or None.

    The knowledge base has one entry per thing, so a line that carries on about the thing we are
    already on ("how do I fix it?" after a dripping tap, "what about the rice?" after a curry
    answer) is answered from that same entry. What the person needs is the sentence of it that
    answers this line, and the shortest honest way to give it is that sentence rather than a
    search hedge. Only a follow-up gets this, only while the knowledge base is what we are on, and
    never the whole of the last answer again (the arbiter drops an exact repeat, and so does the
    bot: a reply twice in a row reads as broken). The answer to draw on is the entry's own answer
    (see entry_answer), so a follow-up still reaches a sentence that an earlier trim left out, and
    a turn in between that got no answer does not end the subject.
    """
    if not isinstance(understood, dict):
        return None
    line = understood.get("clean") or understood.get("text") or ""
    if pairing(line):
        return None  # a pairing question names a relation, not a part of the last answer
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    last = turns[-1]
    # A "thanks" between the answer and the follow-up does not change the subject, so the answer
    # this line carries on is the one before it. The reply on the screen is still `last`'s: what
    # has already been read twice in a row is judged on that, not on the older answer.
    drawn = answer_in_hand(memory) or last
    if understood.get("kind") != "question":
        return None  # a line that adds a detail wants an answer about that, not the last one again
    # "What should I do about it?" asks for the next step, not for a sentence of the last answer
    # picked by its words: that picking gives the cause sentence they have just read. The step is
    # in the answer all the same, so this line is offered the doing part of it (see `_doing_part`)
    # and nothing at all when the answer was only a cause.
    proceed = any(phrase in line.lower() for phrase in PROCEED)
    if not (leans_on_topic(understood, memory) or asks_only(understood)):
        return None  # likewise for a line that points at nothing and asks for nothing
    record = carried_topic(memory, line)
    if left_for_a_blank(memory, line):
        # A turn in between named a thing of its own and got no answer for it ("what about a leg
        # of lamb?" after the roast chicken): the chat is on that thing now, so the next "and how
        # long should that take?" is a question about the lamb, and the chicken times are a wrong
        # answer rather than a helpful one. A line that only says what to do about the thing we
        # are on ("can I fix it myself?") leaves the topic where it was.
        return None
    asked = str((record or {}).get("text") or "")
    # The answer this line's own words belong to, when an earlier turn was about the thing it
    # names: the tap answered between the eggs and "how long for a hard boiled one" are not the
    # same subject, and the egg answer is the one the line asks about.
    earlier = _answer_about(line, memory)
    # Only a line that brings nothing of its own ("how often should i go", "what can i take for
    # it") leans on a thin word match, and then the older answer has to belong to the thing on
    # the table. "how often should i go" after "i want to start running" shares "often" with the
    # shift answer two turns back ("often two to four weeks"), and the thing on the table is the
    # running - an answer about the rota is another subject's. "what can i take for it" after
    # "my back hurts" / "only when i sit down" is the back's, and the back's answer is the one
    # to draw on. A line that names a thing of its own is free to jump to another thing's answer
    # ("how long for a hard boiled one" after the tap).
    if earlier is not None and not [word for word in keywords(line) if word not in ASK_ONLY]:
        on_the_table = _entry(asked)
        answered_by = _the_turn_that_answered(earlier, memory)
        its_subject = _entry(str((answered_by or {}).get("user") or ""))
        if on_the_table is not None and its_subject is not on_the_table:
            earlier = None
    # A line that names a thing of its own is about that thing, even when it points back with
    # "it": "how long does it take to cook rice" after a boiled egg carries rice, which has its
    # own timings, and the egg's six minutes would be a wrong fact. A wrong fact is worse than
    # none, so the answer on the table is left alone and the line is read on its own.
    # The wrong fact this guards against is a figure, a heat or an amount borrowed from another
    # thing's answer; a question that asks for no measure ("should I see a doctor if it's not
    # better by Monday?") is still about the cold it does not name, and reading it alone loses
    # the warning the answer carries.
    measured = set(understood.get("asks") or ()) & MEASURED
    fresh = [word for word in keywords(line) if word not in ASK_ONLY]
    if earlier is None and measured and fresh \
            and not set(key_subject(line)) & set(key_subject(asked)):
        mine, theirs = _entry(line), _entry(asked)
        if mine is not None and theirs is not None and mine is not theirs:
            return None
    # A line that carries nothing but the ask ("and how long?", "what temperature?") cannot be
    # the same question over again: "how long do i boil an egg" then "and how long?" shares its
    # two asking words with the question before it, and the guard threw the follow-up away - the
    # one line that most needs the answer just given. An exact repeat ("how long do i boil an
    # egg" twice) carries its own words, so it keeps the guard.
    if (not asks_only(understood) and _repeats_the_question(line, asked)) \
            or HYPOTHETICAL.search(str(line)):
        return None
    # The answer we are still on: the entry's own answer while the conversation is on that
    # subject, even when a turn in between got no answer. A hedge ("that's beyond what I know")
    # does not end what we were talking about, so the next line can still be answered from it.
    whole = entry_answer(memory, asked)
    if not any(word in keywords(asked) for word in keywords(line)):
        # The line names nothing of the subject it carries on ("how long should i leave it"),
        # so "it" is whatever the last answer was about, not the older entry whose key words
        # the topic happens to fit.
        whole = newest_answer(memory) or whole
    # A card is the answer only while the chat is still on the thing it answers: a statement in
    # between that names a thing of its own and was answered as its own subject moves the chat to
    # that thing, even though it was a statement and not a question. "we want to try for a baby"
    # ... "my baby has a fever" ... "how long does it last" was handed "Have sex every two or
    # three days rather than saving up.", a clause of the trying-for-a-baby card, as the answer
    # to a question about a child's fever. A wrong fact is the worst reply there is, so a line
    # that asks for a part of what the chat holds stops drawing on a card it has moved off.
    if whole and asks_only(understood):
        moved = _the_thing_the_chat_moved_to(whole, line, memory)
        if moved is not None:
            # The thing the chat moved to answers this line itself, so its own sentence is the
            # answer: the card the chat has left is another subject's figures.
            from .narrow import narrow as _the_part
            answer = str(getattr(moved, "reply", "") or "")
            part = _the_part(answer, line)
            if part:
                # The whole sentence it stands in says more than the figure alone ("Most fevers
                # are a virus and settle in three or four days" rather than "Three or four
                # days."), and the person has not read this answer, so there is nothing to trim.
                bare = part.strip(" .").lower()
                for sentence in (one.strip() for one in SENTENCE.split(answer)):
                    if sentence and bare and bare in sentence.lower():
                        return sentence
                return part
            return None
    if drawn.get("module") != "answers" and whole is None:
        return None  # nothing was answered from the knowledge base just now: nothing to draw on
    answer = whole or str(drawn.get("bot") or "")
    # A trip they have changed moves the answer with it: the weather, the cost and what to see
    # are facts about a place, so the answer about the old place is not the answer about the new
    # one ("im going to rome in may" ... "im off to cornwall next week" ... "what should i do
    # there" was handed the Rome weather sentence).
    if about_a_place_they_left_behind(answer, memory):
        return None
    # "how long for 700g" names no thing of its own and has no "it" or "one" to point back with,
    # so it does not look like a follow-up, but it is the same question about another size of
    # what we are on. It counts only while the answer on the table works that size out from its
    # own rate: a subject with no rate in weight gives no time here, and a line that does not
    # follow on is left alone rather than answered with somebody else's figure.
    sized = _worked_out_for_this_line(understood, line, answer)
    if not (leans_on_topic(understood, memory) or asks_only(understood) or sized):
        return None  # likewise for a line that points at nothing and asks for nothing
    # A size the answer's own rate can work out is answered before the sentence scoring, because
    # the ask's weight ("500g") is also in the rate sentence ("20 minutes per 500g"), and that
    # shared word used to hand back the answer for the size the entry had already worked out:
    # "how long for 500g" after the 3kg answer said 2 hours 20 again instead of 40 minutes.
    worked = sized_reply(answer, line, memory)
    if worked:
        return worked
    # The last answer is not always the answer this line is about: a turn about the tap in
    # between must not lend the tap's sentence to a question about boiled eggs. When the line's
    # own words fit an earlier answer better than they fit the last one, that is the answer it
    # is asking again.
    if earlier and earlier != answer:
        answer = whole = earlier
        # The line asks for a part of that answer ("how long for a hard boiled one"), and the
        # answer is often one sentence with the parts inside it: hand back the clause the line
        # asks for, not the whole of a paragraph that is no longer on the last turn.
        from .narrow import narrow
        part = narrow(answer, line)
        if part:
            return part
    # A full stop inside a name is not the end of a sentence: "and *Inside No. 9* for half-hour
    # creepers" was cut at "No." and the person was handed the leftover "9* for half-hour
    # creepers." as the answer to "how long did i want it".
    sentences = quoted.sentences(answer, SENTENCE)
    if proceed:
        if _opening_instruction(sentences[0], True):
            # The answer opens with the step itself, so the next-step reply can name it ("top the
            # pressure up first, then work down the list"): nothing to add here.
            return None
        doing = _doing_part(sentences, memory)
        # The answer that already opens with the steps ("Turn the water off at the isolating valve
        # ... take the old part to a hardware shop") has its doing in that first sentence, and
        # giving it again reads as broken. Nothing is owed there: the next-step reply says to work
        # down the list, which is the honest answer to a line that adds nothing.
        if doing and not _says_it_again(doing, sentences[0]):
            return doing
        return None
    if len(sentences) < 2 and whole is None:
        return None  # one sentence, and only a sentence of it was ever said: nothing to pick
    # A follow-up that asks for a figure ("how many weeks should i train", after a plan that
    # says sixteen) is answered by that figure, not by the answer's opening sentence again.
    from .narrow import part_in_the_unit
    part = part_in_the_unit(answer, line)
    if part and " ".join(words(part)) != " ".join(words(str(last.get("bot") or ""))):
        return said_again(part, memory, line=line) or part
    # "and how often" asks for the frequency in the answer, which is a phrase of it - "three
    # times a week with a rest day between" - and a phrase is not a sentence the word scoring can
    # find, so the line went to the search hedge with the answer it wanted on the screen. The
    # answer's own reader knows how to lift that clause (see narrow._how_often).
    if ASKS_A_FREQUENCY.search(line.lower()):
        from .narrow import narrow
        part = narrow(answer, line)
        if part and words(part) != words(answer):
            return part
    chosen = _pick_sentence(line, understood, answer, memory)
    if chosen:
        # Only the answer's opening sentence is the advice coming round again: a later sentence
        # ("Then set up one meet-up with a classmate") is a new thing to say about the same
        # subject, and framing it as a repeat hides that.
        opening = quoted.sentences(str(answer or ""), SENTENCE)
        if opening and words(opening[0]) == words(chosen):
            return said_again(chosen, memory, line=line) or chosen
        return chosen
    # A turn in between can change the subject and leave this line carrying on the one before it
    # ("what do I wear" between an interview and "what do I say about why I left my last job").
    # Draw on the answer of the nearest earlier subject this line still shares a word with.
    return _earlier_subject_sentence(line, understood, memory, record)


def leans_on_topic(understood, memory):
    """True when this line carries on the current topic instead of naming its own subject."""
    if not isinstance(understood, dict):
        return False
    if _after_an_emergency(memory):
        return False  # the fire is not a subject to carry a question about
    if _after_a_correction(memory):
        return False  # the subject they have just replaced is not the one being asked about
    said = understood.get("clean") or understood.get("text") or ""
    # The shrugs in the middle of the line are not part of what it is about, but the one that
    # opens it can be the turn itself ("actually it's a funeral"), so the switch is read from the
    # line as it came in and the shrugs come out only of the rest.
    text = without_the_shrug(said)
    # "What should I do about it?" carries on from the answer, not from the topic's words: read
    # in context it reaches the same entry and the paragraph comes back word for word.
    if any(phrase in text.lower() for phrase in PROCEED):
        return False
    record = carried_topic(memory, text)
    if record is None or not text.strip() or is_ack(text):
        return False
    if opens_by_switching(said):
        return False
    # A fact or a limit about what we are already on: it leaves the subject out on purpose.
    if DETAIL.search(text):
        known = set(record.get("words") or [])
        fresh = [word for word in keywords(text) if stem(word) not in known]
        return len(fresh) <= 4 and len(words(text)) <= 14
    # Otherwise the line has to point back at the topic ("and if I stuff it?", "how long will
    # that take?"), or name nothing at all and reach an entry with the topic's words carried
    # ("how often should I go?" after running). A follow-up that names something of its own
    # ("how long in the oven?") is left as it is: it may be about a different thing of the same
    # kind, and a wrong fact is worse than none.
    if follows_on(understood, text):
        return True
    carried = carry_the_ask(text, record.get("text") or "", understood, memory)
    if carried is None:
        # Nothing the topic's words reach: the one kind of line that still leans on the topic is
        # a short question that names no subject at all ("what should I wear" after a wedding,
        # "what should I do first" after a move). Read through bare_question it reaches the
        # topic's entry; read on its own it reaches nothing.
        return bare_question(understood, memory)
    # A line that names the topic's own words is still on the topic: "how many weeks should i
    # train" after "I'm training for a half marathon" names nothing but the marathon's training,
    # and the ask is about that. "how long in the oven?" names something the topic does not
    # carry, which may be a different thing of the same kind, and is left as it is.
    return names_nothing(text) or _only_the_topics_own_words(text, record)


# The words a line can spend on naming a new period and nothing else: "and in october", "what
# about june", "how about the summer". Anything else it says is a subject of its own.
PERIOD_ONLY = frozenset("""
and or but also so in on at for about during of the a an what whats how when to it that there
weather like is will be gonna going get have we i you they month months next this coming
""".split())


SEASONS = frozenset("spring summer autumn fall winter".split())


def _the_period_in(text):
    """The period a line names, as it is spelled there, or "".

    "may" is a month and also the verb, so the word has to be standing where a period stands:
    after a preposition ("in may"), after "next"/"this", or at the end of the line. A month
    named anywhere else ("i may go to spain") is not a period.
    """
    low = " ".join(str(text or "").lower().split())
    for name in sorted(MONTH_NAMES | SEASONS, key=len, reverse=True):
        for found in re.finditer(r"(?<![a-z])" + name + r"(?![a-z])", low):
            before = low[:found.start()].split()
            after = low[found.end():].strip(" ?!.,")
            if not before or before[-1] in ("in", "next", "this", "the", "early", "late", "mid",
                                            "until", "til", "by", "for", "about", "of", "and"):
                return found.group(0)
            if name not in ("may", "march", "fall") or not after:
                return found.group(0)
    return ""


def _a_period_and_nothing_else(line):
    """True for a line that names a period and nothing else of its own."""
    said = words(line)
    if not _the_period_in(line):
        return False
    return all(word in PERIOD_ONLY or word in MONTH_NAMES or word in SEASONS for word in said)


def the_period_they_ask_about(understood, memory):
    """The question on the table asked again about a new month or season, or None.

    "whats the weather like in rome in may" then "and in october" is the same question about
    October, which the knowledge base has: asked as it came in, the month is the only subject
    and the line gets the storing turn's nod. The old period is swapped for the new one in the
    question the chat is on, so every phrasing of "and in <month>" reaches the same answer, and a
    line that brings anything else ("whats the weather like in october in cornwall") is not this.
    """
    line = str(understood.get("clean") or understood.get("text") or "")
    if not _a_period_and_nothing_else(line):
        return None
    period = _the_period_in(line)
    record = carried_topic(memory, line)
    asked = str((record or {}).get("text") or "")
    was = _the_period_in(asked)
    if was == period:
        return None      # the same period again
    if not was:
        # The question on the table names no period of its own - "whats the weather like" after
        # a trip - so the new period is the one thing missing, and the place comes from the trip
        # the chat is on: "im off to rome next week" / "whats the weather like there" / "and in
        # august" is the Rome figures for August. Only when the answer they have just read was
        # about the weather: "how much does a trip to rome cost" then "and in october" is a
        # question about money, and the climate is not the answer to it.
        if not _the_answer_was_about_the_weather(memory):
            return None
        place = _the_place_the_chat_is_on(line, memory)
        if place is None:
            return None
        return f"what is the weather like in {place} in {period}"
    if ASK_CUE.search(asked.lower()) is None and WEATHER_ASKS.search(asked.lower()) is None:
        return None      # the earlier line did not ask anything to ask again
    return _with_the_period(asked, was, period)


def _the_answer_was_about_the_weather(memory):
    """True when the last thing the bot said was about the weather."""
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("bot") or "")
        if not said.strip():
            continue
        return bool(WEATHER_WORDS & set(words(said)))
    return False


def _the_place_the_chat_is_on(line, memory):
    """The place the chat is still on, from the trip the person stated, or None.

    The newest line that names a place is the one read, so a trip said later is the trip, and a
    line with no place ends the search: the chat has moved to something the climate cannot
    answer. A trip already taken is not one to give a forecast for.
    """
    mine = " ".join(words(line))
    for said in _the_lines_said(memory):
        if " ".join(words(said)) == mine:
            continue                       # this turn is not the chat it follows on from
        if the_weather_ask({"clean": said, "text": said}):
            continue                       # the same question again: the trip behind it is the trip
        if _a_period_and_nothing_else(said):
            continue                       # yesterday's "and in october": still the same chat
        if A_TRIP_TAKEN.search(" ".join(str(said).lower().split())):
            return None                    # the figures are the right climate and the wrong tense
        place, _month = the_place_and_month(said)
        if place is not None:
            return place
        return None                        # no place in the newest thing said: nothing to fill in
    return None


def _with_the_period(asked, was, now):
    """The earlier question with its period swapped for the one this line names."""
    out = re.sub(r"(?<![a-z])" + re.escape(was) + r"(?![a-z])", now, asked, count=1)
    return " ".join(out.lower().split())


# A follow-up that names another meal is the same question about the meal it names: a dairy-free
# breakfast and then "and for lunch" was answered with the breakfast list again. Anything else the
# line says is a subject of its own, so "and for lunch i want soup" is not this.
MEAL_NAMES = frozenset("""breakfast lunch dinner supper brunch""".split())


MEAL_ONLY = frozenset("""
a an about also and anything at but can could do does eat for have how i instead is it make me
or should so something that the then there to we what whats will would you
""".split())


# A bare line that opens with one of these is a follow-up on the turn before it: "and for lunch",
# "what about dinner". A line that asks its own question ("do i have to eat breakfast") is not.
OPENS_A_FOLLOW_UP = re.compile(r"^(?:and|also|then|or|so|what about|how about|whats|same)\b", re.I)


def _the_meal_in(text):
    """The meal a line names, or ""."""
    low = " ".join(str(text or "").lower().split())
    for name in sorted(MEAL_NAMES, key=len, reverse=True):
        if re.search(r"(?<![a-z])" + name + r"(?![a-z])", low):
            return name
    return ""


def _a_meal_and_nothing_else(line):
    """True for a line that names a meal and nothing else of its own."""
    said = words(line)
    if not _the_meal_in(line):
        return False
    return all(word in MEAL_ONLY or word in MEAL_NAMES for word in said)


def the_meal_they_ask_about(understood, memory):
    """The question on the table asked again about another meal, or None.

    "what can i have for breakfast" then "and for lunch" is the same question about lunch, which
    the knowledge base answers; asked as it came in, the line names no subject of its own and
    comes back as the breakfast answer again. The meal is swapped in the question the chat is on,
    so "and for lunch", "what about dinner" and "and tea instead" all reach their own answer.
    """
    line = str(understood.get("clean") or understood.get("text") or "")
    if not _a_meal_and_nothing_else(line):
        return None
    meal = _the_meal_in(line)
    record = carried_topic(memory, line)
    asked = str((record or {}).get("text") or "")
    was = _the_meal_in(asked)
    if not was:
        # The chat is not on a meal, so there is no question to swap the meal into. A line that
        # opens a follow-up ("how do i boil an egg" then "and for lunch") is still asking about
        # the meal it names; a line that asks its own question ("do i have to eat breakfast") is
        # not this at all.
        if not OPENS_A_FOLLOW_UP.match(line):
            return None
        return "what can i have for " + meal
    if was == meal:
        return None      # the same meal again is the answer just given
    if ASK_CUE.search(asked.lower()) is None:
        return None      # the earlier line did not ask anything to ask again
    return _with_the_meal(asked, was, meal)


def meal_follow_up(understood, memory):
    """The line read again with the meal it names in it, as a reading, or None.

    The reading is built here rather than in the caller so the answer modules can use it before
    they search the earlier line: searched as it stands, "and for lunch" reaches the answer about
    the meal before it.
    """
    meal = the_meal_they_ask_about(understood, memory)
    if not meal:
        return None
    reading = dict(understood)
    reading["clean"] = meal
    reading["words"] = words(meal)
    if "norm_text" in reading:
        reading["norm_text"] = meal
    return reading


def _with_the_meal(asked, was, now):
    """The earlier question with its meal swapped for the one this line names."""
    out = re.sub(r"(?<![a-z])" + re.escape(was) + r"(?![a-z])", now, asked, count=1)
    return " ".join(out.lower().split())


def the_weather_of_the_trip(understood, memory):
    """The trip's climate question, when a weather follow-up can be answered with it, or None.

    "what's the weather like" and "how hot will it be" after "we are going to lisbon in june"
    are the Lisbon-in-June averages, which the knowledge base has; asked on their own they get
    the meaning of the word weather. The line is asked again with the trip's place and month in
    it, so every phrasing of the same question gets the same answer, and a line that names its
    own place is left alone (it already reaches the entry).
    """
    if not the_weather_ask(understood):
        return None
    line = str(understood.get("clean") or understood.get("text") or "")
    place, month = the_place_and_month(line)
    if place is not None:
        return None      # the line says where: whatever it gets today stands
    if NOW_AND_HERE.search(line.lower()):
        return None      # here and now, not the trip: the hedge is the honest answer
    place, month = the_place_and_month(_the_trip_said(line, memory))
    if place is None or month is None:
        return None      # no month, no figures: the hedge is the honest answer
    return f"what is the weather like in {place} in {month}"


# A trip that has already happened: "we went to lisbon in june", "we were in rome in may".
A_TRIP_TAKEN = re.compile(
    r"\b(?:(?:i|we|he|she|they)\s+(?:went|were|was|been|had|did|stayed|visited|flew|drove)"
    r"|got\s+back|came\s+back|back\s+from|just\s+back|returned)\b", re.I)


def _the_trip_said(line, memory):
    """The trip the chat is on, when it names a place and a month, or "".

    Only the turn the chat is actually on is read back. A weather ask is the same question asked
    again ("whats the weather like", then "will we need a coat"), so those are skipped; the first
    turn that is about something else is what the chat is on, and the figures come from it or not
    at all. A trip the chat has left - "we are going to lisbon in june", then "my boiler is
    broken" - is not the trip, and its climate is not an answer to a question about the boiler.
    """
    mine = " ".join(words(line))
    for said in _the_lines_said(memory):
        if " ".join(words(said)) == mine:
            continue                      # this turn is not the chat it is following on from
        if the_weather_ask({"clean": said, "text": said}):
            continue                      # the same question again: the ask behind it is the trip
        place, month = the_place_and_month(said)
        if place is None or month is None:
            return ""                     # the chat is on something with no figures: leave it be
        if A_TRIP_TAKEN.search(" ".join(said.lower().split())):
            # "we went to lisbon in june", "we got back from rome in may" are trips behind them:
            # the figures are the right climate and the wrong tense, and the question they are
            # followed by is what it was like, not what to pack.
            return ""
        return said
    return ""


def _the_lines_said(memory):
    """The lines the person has said, newest first."""
    if not isinstance(memory, dict):
        return []
    out = []
    for turn in reversed(memory.get("turns") or []):
        said = str((turn or {}).get("user") or "") if isinstance(turn, dict) else ""
        if said.strip():
            out.append(said)
    return out


# The pronouns that stand for the thing itself, not for a person: "what should I feed it".
THING_ITSELF = re.compile(r"\b(it|its|them|they)\b", re.I)


# Some "it"s are not pointing at anything: they are part of the phrase itself, and filling one
# writes a line nobody said. "how do i make it up to my mum" became "how do i make my mums
# birthday up to my mum" once the store had the birthday, and the party plan and the tray bake
# both took a turn about putting something right. Read before the fill, so the phrases stay whole.
IT_IS_PART_OF_THE_PHRASE = (
    "make it up", "making it up", "put it right", "make it right", "put it behind",
    "take it out on", "took it out on", "let it go", "let it lie", "get it wrong",
    "got it wrong", "getting it wrong", "said it wrong", "put it down to", "have it out with")


BABY_OF = {"puppy": "dog", "kitten": "cat"}


# An ask about what the thing costs is about getting one, not about the one they have: filling
# the pronoun turned the boiler's "how much will it cost" into the cat's feeding amount, because
# the entry for how much to feed a cat is also keyed on "much".
WHAT_IT_COSTS = re.compile(r"\b(?:cost|costs|costing|price|prices|worth|expensive|cheap|cheaper|"
                           r"pay|paid|fee|fees|insurance|bill|bills|money|afford)\b", re.I)


# "is it worth fixing" asks for a decision about the thing, not a price for it, and the readers
# that decide already answer it well: filling the pronoun there answered a washing machine with
# the cost of a wash, a laptop for uni with the repair rule, and an energy tariff with garage
# labour.
WORTH_DECIDING = re.compile(
    r"\b(?:is|would|will)\s+(?:it|that|this|they)\s+"
    r"(?:worth|better|best|cheaper|cheapest|smarter)\b[^?]*"
    r"\b(?:fix|repair|replac|restor|servic|renew|upgrad|pay|spend|buy"
    r"|keep|sell|insur|invest|switch)\w*", re.I)


# "is it worth getting a dog", "is it worth having a smart meter": the pronoun is where the line's
# own subject goes - worth, then a verb of having - so it stands for nothing the chat has said. A
# pronoun that points looks different: "is it worth paying more" after a laptop is that laptop,
# and "is it safe to drive" after a brake fault is that car.
PLACEHOLDER_PRONOUN = re.compile(
    r"\bworth\s+(?:getting|having|buying)|\bworth\s+(?:get|have|buy)\b", re.IGNORECASE)


# ... unless the line is about a new one *of the thing in hand*: "my boiler needs its yearly
# service" and then "is it worth getting a new one instead" is the boiler, and reading the worth
# as a fresh subject left the person with a shrug where the boiler rows had an answer.
A_NEW_ONE = re.compile(
    r"\b(?:new|another|bigger|smaller|different|better|second|cheaper|proper)\s+one\b"
    r"|\bone\s+instead\b|\bone\s+of\s+(?:those|them)\b", re.IGNORECASE)


def a_placeholder_pronoun(line):
    """True when the pronoun in the line is a hole for a subject of its own, not a pointer."""
    text = str(line or "")
    return bool(PLACEHOLDER_PRONOUN.search(text) and not A_NEW_ONE.search(text))


def the_ask_about_the_thing_it_points_at(understood, memory):
    """The reading with the thing a pronoun points at written in front of it, or None.

    "where should i keep it" after "im trying to save money" names nothing the knowledge base
    can answer, and the answer above it is about tracking spending rather than about where the
    money goes, so the turn fell to "that was the whole of my answer on it" with the savings
    entry one word away. The reading has already resolved the pronoun ("money"), so the ask is
    written the way the knowledge base keys it: "where should i keep my money".

    A last resort, asked only where every other reader has passed: a follow-up that a sentence
    of the answer above can answer ("what should i get for it", "how long does it need") is
    answered there and never reaches this, so the thing the store holds cannot take that
    turn. Only a thing, never a person, and never a word of the asking itself.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = " ".join(str(understood.get("clean") or understood.get("text") or "").split())
    if not line or not THING_ITSELF.search(line):
        return None
    if any(phrase in line.lower() for phrase in PROCEED):
        return None  # "what should i do about it" carries on from the answer
    if any(phrase in line.lower() for phrase in IT_IS_PART_OF_THE_PHRASE):
        return None  # the "it" is the phrase's own, not a pointer at a thing
    if WHAT_IT_COSTS.search(line):
        return None  # what it costs is about getting one, not about the one they have
    ref = understood.get("ref") if isinstance(understood.get("ref"), dict) else None
    # Only a thing. A conversation that named no thing at all resolves its pronoun to the label
    # of the topic it was read as ("language-and-writing"), and a label is not a noun phrase
    # anybody said: written into the ask it gave "how long will my language and writing take"
    # after "im trying to write a book", which the language-hours row answered with the Spanish
    # figure. `references._target` says the same in its own words - a caller that needs a noun
    # can tell the two apart - and this is that caller.
    if not isinstance(ref, dict) or ref.get("kind") != "thing":
        return None
    thing = ref.get("it") or ref.get("that")
    if not isinstance(thing, str):
        return None
    thing = " ".join(thing.split())
    if not thing or len(thing.split()) > 3 or thing in ("it", "that", "them", "they", "you", "me"):
        return None
    if thing in line.lower():
        return None  # the thing is already in the line, so nothing is pointed at
    filled = " ".join(THING_ITSELF.sub("my " + thing, line, count=1).split())
    reading = dict(understood)
    reading["clean"] = filled
    reading["words"] = words(filled)
    return reading


# The pronouns a line uses in place of a thing, and the slot the reading keeps it in.
POINTING_WORDS = ("it", "they", "them", "that", "this", "he", "she")


# A noun written into a sentence needs whatever it takes to sit there: "how long can a cat be
# left alone" is the line a person would say, and the bare "cat" reaches the same entry only by
# luck. A name takes none ("how long can Fish be left alone").
WITHOUT_A_DETERMINER = frozenset("""
    it they them that this he she i you we me my your our their his her its
    a an the some any no every each
""".split())


def _the_thing_with_a_determiner(thing):
    """The ways this thing can be written into a line, the plain one included."""
    ways = []
    first = thing.split()[0].lower()
    if first not in WITHOUT_A_DETERMINER:
        article = "an" if first[:1] in "aeiou" else "a"
        ways.extend([article + " " + thing, "the " + thing, "my " + thing])
    ways.append(thing)
    return ways


SOMETHING_IS_BROKEN = re.compile(
    r"\b(?:broke|broken|not working|stopped working|wont work|won't work|faulty|leaking|"
    r"isnt working|isn't working|packed in|given up)\b", re.I)


THEIR_OWN = re.compile(r"\b(my|the)\s+([a-z']+)", re.I)


# A word after "my" that is not a thing of theirs: a person, a part of the day, a feeling.
NOT_THEIR_OWN = frozenset("""
own self way turn go mind head opinion fault point lot bit time while moment
life day week month year today house home place
""".split())


_SMALL = frozenset("""
a an the and or but of to in on at for with is was are were be been has have had got
""".split())


def _what_they_called_theirs(text):
    """The phrases the chat calls theirs: [("my laptop", "laptop"), ("the boiler", "boiler")].

    Only a thing named as belonging to the person is read here, so a pronoun in a cost ask fills
    with what they have and not with any noun the line happened to hold. One word only, because
    "my car failed" is a thing and a verb, and "my car" is the thing.
    """
    out = []
    for lead, word in THEIR_OWN.findall(text):
        if len(word) < 3 or word in _SMALL or word in NOT_THEIR_OWN:
            continue
        pair = (lead.lower() + " " + word, word)
        if pair not in out:
            out.append(pair)
    return out[:3]


# An entry whose id says what it answers ("running-cost", "car-running-costs") is the answer to
# a question about *using* the thing, so it is only the answer when the ask names that. Filling
# the pronoun in "my dishwasher is not draining" / "is it expensive" reached the running-cost key,
# which holds sixty appliances, and answered the cost of a cycle where the person asked what a
# repair costs; a car making a noise got a yearly budget.
NAMES_THE_RUNNING = re.compile(
    r"\b(?:run|runs|running|use|uses|using|used|electricity|electric|energy|power|cycle|cycles"
    r"|hour|hours|kwh|gas|water|heating)\b", re.I)


def _the_entry_answers_the_ask(entry, line):
    """Whether what the entry is about is what the ask asked ("is it expensive to run")."""
    if str(getattr(entry, "id", "")).endswith("running-cost") or str(
            getattr(entry, "id", "")).endswith("running-costs"):
        return bool(NAMES_THE_RUNNING.search(line))
    return True


def _the_entry_is_about_the_thing(entry, word):
    """Whether the entry the filled ask landed on is keyed on the thing itself.

    An ask about what something costs used to be left alone here, because filling the pronoun
    in the boiler's "how much will it cost" reached the cat's feeding entry - both keys hold
    "much". The entry itself is the test: the trip budget entry's key names Lisbon, so
    "is lisbon expensive" is an answer about Lisbon, and a key that does not name the thing is
    an answer about something else.
    """
    return any(word in group for group in entry.key)
