"""Part 5 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from . import quotes as quoted
from .topics_part_01 import (
    ASK_ONLY, STOPWORDS, stem, words, keywords, is_ack, GREET, current, alike, ASK_CUE,
)
from .topics_part_02 import (
    _entry, _said, key_subject, subject, _thing_of,
)
from .topics_part_03 import (
    ABOUT_MOST_WORDS, ABOUT_NAMED, DEFINITE_OPEN, _ABOUT_TAIL_PRONOUN, _key_words_of,
    _the_same_answer_again, AMOUNT, FREQUENCY, RATE, SENTENCE, TIME, DURATION, LENGTH_ASK,
    SPAN_ADJECTIVE, THRESHOLD_SPAN, OWN_SIZE, WEIGHT_IN_GRAMS, RATE_BY_WEIGHT, follows_on,
    _content_words,
)
from .topics_part_04 import (
    ASKS_THEM_BACK, RED_FLAG, _opening_instruction, said_on_its_own, ADVICE_ASK,
    ADVICE_NAMES_A_THING, _pick_amount, _time_of, OPTION_ANY, PERIOD_LEAD, _asked_period,
    _duration_clauses, _in_period, _option_range, _shorten, _step_they_asked_for, time_for_amount,
    entry_answer,
)


def the_thing_the_subject_brings(understood, memory):
    """The widened reading for a line that asks about a thing of the subject, or None.

    "and what about shoes" after "i want to start running" is a question about shoes for running,
    and the knowledge base answers "shoes for running" while the line on its own reaches nothing.
    The entry has to be keyed to the thing the line named *and* to the subject, so the subject's
    own answer is never handed back as though it answered a thing it never mentioned, and a thing
    with no answer of its own ("what about socks", "what about a case") is left as it is rather
    than answered with something that is not about it.
    """
    if not isinstance(understood, dict):
        return None
    text = " ".join(str(understood.get("clean") or understood.get("text") or "").lower().split())
    # The kind of thing it names is read from the words the person typed. The reading drops the
    # article ("what about the bathroom" comes back as "bathroom"), and "a" or "the" is exactly
    # what says whether the thing is a new one of the subject's or one the chat already has. The
    # turn's own line is tried first: this is called again on a rewritten line, and the rewrite
    # has neither the opener nor the article.
    raw = " ".join(str(understood.get("text") or understood.get("clean") or "").lower().split())
    lines = [text, raw]
    for turn in [one for one in (memory.get("turns") or []) if isinstance(one, dict)][-1:]:
        typed = " ".join(str(turn.get("user") or "").lower().split())
        if typed:
            lines.insert(0, typed)
    for said_as in lines:
        found = ABOUT_NAMED.match(said_as)
        if found:
            break
    else:
        return None
    thing = _ABOUT_TAIL_PRONOUN.sub("", found.group("thing").strip()).strip()
    if not thing or len(thing.split()) > ABOUT_MOST_WORDS:
        return None
    # A thing said with "the" or "my" is one already in play - "what about the bathroom", "what
    # about my passport" - and narrowing an answer that has just been given is the detail
    # reader's turn, not this one's. Only a thing named anew is the thing the subject brings with
    # it: "a case", "shoes", "a sleeping bag".
    typed = _ABOUT_TAIL_PRONOUN.sub("", said_as[found.end():].strip())
    if DEFINITE_OPEN.match(thing) or DEFINITE_OPEN.match(typed):
        return None
    # A bare singular is one already named with its article left off ("what about bathroom" is
    # read from "what about the bathroom"), and a bare plural is a class of things ("shoes").
    kind = typed or thing
    if not re.search(r"^(?:a|an|some)\b", kind, re.I):
        last = (kind.split() or [""])[-1]
        if not (last.endswith("s") and not last.endswith("ss") and len(last) > 3):
            return None
    thing_words = [word for word in words(thing)
                   if word not in STOPWORDS and word not in ASK_ONLY and len(word) > 2]
    if not thing_words:
        return None
    record = carried_topic(memory, text)
    if record is None:
        return None
    # A thing the answer already spoke of is a narrowing of that answer, not a thing of its own:
    # "what about the bathroom" after the windows' answer is the bathroom's window, and widening
    # it read the whole paragraph out again. The two answers back are enough - an answer that
    # named the thing is the one the person is pointing at.
    spoke_of = set()
    for turn in [one for one in (memory.get("turns") or []) if isinstance(one, dict)][-2:]:
        spoke_of.update(stem(word) for word in words(str(turn.get("bot") or "")))
    if any(stem(word) in spoke_of for word in thing_words):
        return None
    subject_words = [word for word in key_subject(str(record.get("text") or ""), memory)
                     if word not in thing_words]
    if not subject_words:
        return None
    # One subject word at a time: the entry is keyed to the thing and the subject, and "shoes for
    # running start" reaches nothing at all while "shoes for running" is the answer. The first
    # word is the one the subject is about, so the order the reading gives them is the order to
    # try them in.
    for subject in subject_words:
        for candidate in (thing + " for " + subject, thing + " " + subject):
            item = _entry(candidate)
            if item is None:
                continue
            keyed = _key_words_of(item)
            named = any(word in keyed or stem(word) in keyed or _said(word, keyed)
                        for word in thing_words)
            about_the_subject = any(word in keyed or stem(word) in keyed or _said(word, keyed)
                                    for word in subject_words)
            if not (named and about_the_subject):
                continue
            # The answer has to be another answer than the one on the screen. Counting shared
            # key words was how this was first written, and the knowledge base grew: the running
            # entry and the shoes-for-running one now share five words, so the count read a real
            # answer about shoes as the running answer said again. What separates them is the
            # answer itself, so the answer already given is what is compared.
            anchor = _entry(str(record.get("text") or ""))
            if anchor is not None and item is not anchor:
                if _the_same_answer_again(item, memory):
                    continue
            return candidate
    return None


def _a_sky_ask(line):
    """True for a line asking about the weather, which needs the topic's month as much as its
    place: "whats the weather like there" after a trip in May is the May figures for Rome, and
    read without the month it is "no live weather here" instead of them. A month is dropped from
    what the topic lends only for the asks that are about somewhere, not for this one."""
    return any(word in WEATHER_WORDS for word in words(line))


def _doing_part(sentences, memory):
    """The sentence of the last answer that says what to do, as it was written, or None.

    A doing part opens with an instruction, either as the sentence is ("Rinse it until the water
    runs clear") or after the colon of the sentence that explains the cause ("A sore knee is
    usually a strain: ease off running"). A sentence that only sends them to someone else ("See a
    physio if it swells") is the doing part of last resort, so it is tried after the others. The
    bot asking them something is not a doing part at all (see `ASKS_THEM_BACK`), however
    instructively it is worded.
    """
    for allow_pointer in (False, True):
        for sentence in sentences:
            if RED_FLAG.match(sentence):
                continue
            head, sep, tail = sentence.partition(":")
            if sep and tail.strip() and _opening_instruction(tail, allow_pointer):
                said = tail.strip()
                said = said[0].upper() + said[1:]
                if not said.endswith((".", "!", "?")):
                    said += "."
                if RED_FLAG.match(said) or ASKS_THEM_BACK.search(said):
                    continue
                if not already_said(memory, said):
                    return said
            if _opening_instruction(sentence, allow_pointer) \
                    and not ASKS_THEM_BACK.search(sentence):
                if not already_said(memory, sentence):
                    return sentence
    return None


def _pick_sentence(line, understood, answer, memory, strict=False):
    """The sentence of this answer that answers this line, said on its own, or None."""
    return said_on_its_own(_the_sentence_it_answers(line, understood, answer, memory, strict))


def _the_sentence_it_answers(line, understood, answer, memory, strict=False):
    """The sentence of this answer that answers this line, or None."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    last = turns[-1] if isinstance(turns, list) and turns and isinstance(turns[-1], dict) else {}
    sentences = quoted.sentences(answer, SENTENCE)
    if not sentences:
        return None
    wanted = [stem(word) for word in keywords(line)]
    asks = set(understood.get("asks") or {})
    if "how_long" in asks:
        # "how long does it need?" wants the time, not the whole answer again: give the clause
        # with the time in it, which is the one part of it this line is asking about.
        part = _pick_duration(sentences, wanted, memory, line)
        if part:
            return part
    if re.search(r"\bhow much\b", line, re.I):
        # "how much should i take" wants the dose, and the sentence that shares its verb
        # ("Ask a pharmacist first if you take ...") is not it. Read the sentence with a figure
        # in a unit, which is the answer; if that sentence is already on the screen, give the
        # clause with the figure in it rather than the whole sentence again. "How many times a
        # week" is also an amount in the reading, but its unit is a count of times, not a figure
        # in grams or milligrams, so it is left to the readers below.
        part = _pick_amount(sentences, memory, line)
        if part:
            return part
    # An ask for the doing wants the doing, whether or not its own reading carries "steps":
    # "what helps" after a back-pain answer shares the word "helps" with the sentence, so the
    # shared-word pass below hands back the whole of what they have just read, cause and all.
    if ADVICE_ASK.search(line) and ADVICE_NAMES_A_THING.search(line) is None \
            and not _names_something_new(line, answer):
        doing = _doing_part(sentences, memory)
        if doing:
            return doing
    best, best_score = 0, 0
    for index, sentence in enumerate(sentences):
        said = [stem(word) for word in keywords(sentence)]
        score = sum(1 for word in wanted if word in said)
        if score > best_score:
            best, best_score = index, score
    if best_score:
        sentence = sentences[best]
        if not already_said(memory, sentence):
            return sentence
        # That sentence has been given already: fall through to what the ask itself wants rather
        # than let a shared word ("take the handle off" for "how long will it take?") end it.
    if strict:
        return None  # an older answer gets no say unless its words answer this line
    # No shared word: the ask itself has to say what it wants. A "how do I ..." or "what should I
    # ..." is answered by the steps, and a "how long" by the sentence with the time in it.
    if asks & {"steps", "how"}:
        first = sentences[0]
        if _names_something_new(line, answer):
            # The ask names a thing none of the last answer mentions ("how do i cancel her
            # insurance" after the pets entry condoled), so the sentence the bot opened with
            # is not an answer to it: pass instead of saying it again.
            return None
        if ADVICE_ASK.search(line) and not ADVICE_NAMES_A_THING.search(line):
            # "what should I do?" wants the doing, and the answer's first sentence is often the
            # cause ("Most back pain is muscular and settles in two to six weeks, ..."), so
            # giving it back whole says the thing they have just read and leaves out the step.
            doing = _doing_part(sentences, memory)
            if doing:
                return doing
        return None if already_said(memory, first) else first
    if "how_long" in asks:
        # A later sentence that carries a time is news, so it comes whole. The first sentence is
        # the one they have just read, so only the time in it is worth saying again, and it has
        # to be a time, not a count of people or a tin size.
        amount = AMOUNT.search(line)
        worked = _sized_reply(answer, line, memory)
        if amount and worked:
            return worked
        for sentence in sentences[1:]:
            if not (TIME.search(sentence) and not already_said(memory, sentence)):
                continue
            # "how long for a 1.5kg one" is owed the figure for 1.5kg, and the sentence about
            # resting the bird for 15 minutes is about another thing however much of a time it
            # carries. A line that names an amount takes the sentence that names it, or the
            # rate that answers any amount ("20 minutes per 500g").
            if amount and amount.group(0).replace(" ", "") not in re.sub(r"\s+", "", sentence):
                # A rate answers any amount of the same thing, so the sentence that states it is
                # the answer - as long as it is not what they have just read.
                if RATE.search(answer) and not already_said(memory, answer, turns_back=1):
                    return answer
                continue
            return sentence
        if sentences and TIME.search(sentences[0]) and not already_said(memory, sentences[0]):
            span = _time_of(sentences[0])
            if span:
                return span[0].upper() + span[1:] + "."
        # The only sentence with the time in it has been said already. The time in it is still
        # the answer to this line, so give that clause rather than the whole sentence again.
        part = _pick_duration(sentences, wanted, memory, line)
        if part:
            return part
    if "how_often" in asks:
        # "how often should i do that?" after the gutters answer is answered by it: twice a year
        # is how the answer opens, and a search hedge would be the bot not reading its own last
        # line. The repetition has to open its sentence to be that answer: an aside in the
        # middle ("repeated for 20 minutes, three times a week...") is part of a longer piece
        # of advice, and cutting it out leaves "Three times a week." where the fuller line the
        # reader already gives (the sessions, the day off) is the better answer.
        for sentence in sentences:
            found = FREQUENCY.match(sentence)
            if not found or already_said(memory, sentence):
                continue
            return _phrase(found.group(0))
    return None


def _the_option_for_the_topic(sentence, line, memory):
    """The option in this answer that names what the conversation is on, or None.

    Only for an answer that offers a time for each of several things: the figure the follow-up
    wants is the one for their thing, not the first option and not a range stitched out of two
    of them. The unit is carried from the option that says it.
    """
    text = str(sentence or "")
    found = list(OPTION_ANY.finditer(text))
    if len(found) < 2:
        return None
    topic = str((carried_topic(memory, line) or {}).get("text") or "")
    subject = set(keywords(topic))
    if not subject:
        return None
    hits, unit = [], ""
    for index, found_one in enumerate(found):
        end = found[index + 1].start() if index + 1 < len(found) else len(text)
        piece = text[found_one.start():end]
        # The next option starts at its figure, so the comma (and the "and" or "or") in front of
        # it is still on the end of this one: "5 to 10 for a steak or chops, and" is one option.
        for _ in range(2):
            piece = re.sub(r"[\s,;:]+$", "", piece)
            piece = re.sub(r"\s+(?:and|or|to)$", "", piece)
        unit = found_one.group(2) or unit
        if set(keywords(piece)) & subject:
            hits.append((found_one, piece, unit))
    if len(hits) != 1:
        return None
    found_one, piece, unit = hits[0]
    if unit and not found_one.group(2):
        # "10 to 20 minutes" and not a bare "10 to 20", which reads as a count of nothing.
        cut = found_one.end(1) - found_one.start()
        piece = piece[:cut] + " " + unit.lower() + piece[cut:]
    return piece[:1].upper() + piece[1:] + "."


def _pick_duration(sentences, wanted, memory, line=""):
    """The time in the answer this line is asking about.

    "And how long for a hard boiled one?" names the part it wants, and the sentence that has
    that part in it carries the unit with it ("6 minutes for a runny yolk, 7 for jammy, 9 to 10
    for hard boiled"), so that sentence comes whole: cut it to a clause and "9 to 10" has lost
    what it counts. When the line names nothing of its own ("how long do I need?"), the last
    time in the answer is the one for the dish being made, which is the oven step.
    """
    if LENGTH_ASK.search(line or ""):
        # Only a sentence that states a time can answer a how-long ask. Scoring every sentence
        # by shared words let the method sentence win on "take" ("how long will it take?"), and
        # the time sentence was never looked at.
        sentences = [sentence for sentence in sentences
                     if DURATION.search(sentence) or SPAN_ADJECTIVE.search(sentence)]
        if not sentences:
            return None
        # Of those, a stretch ("two to three days") answers "how long does it last", while a
        # threshold ("it lasts more than a week") answers "when should I worry". The threshold
        # used to take the question because it shares the verb, so it is looked at last.
        spans = [sentence for sentence in sentences if not THRESHOLD_SPAN.search(sentence)]
        if spans:
            sentences = spans
    wanted = set(wanted)
    best_overlap, best_index = 0, 0
    for index, sentence in enumerate(sentences):
        words = {stem(word) for word in keywords(sentence)}
        overlap = len(wanted & words)
        if overlap > best_overlap:
            best_overlap, best_index = overlap, index
    if best_overlap:
        sentence = sentences[best_index]
        period = _asked_period(line)
        if period is not None:
            # The line counts its answer in a period, and the sentence that shares a word with
            # it usually shares one that is not a time at all: "how long each day" meets "a
            # rest day between" in a running answer, and said whole that sentence has not
            # answered when the day's bit is. The time counted in that period is the answer.
            parts = [part for part in _duration_clauses(sentence)
                     if _in_period(part, period)]
            part = _step_they_asked_for(parts, wanted)
            if part:
                part = PERIOD_LEAD.sub("", part)
                if not part[:1].isupper():
                    part = part[:1].upper() + part[1:]
            return _shorten(part) if part else None
        # Already said: the part of it with the time in it is still news, the rest is not.
        if not already_said(memory, sentence):
            return sentence
        parts = [part for part in _duration_clauses(sentence)
                 if not already_said(memory, part)]
        part = _step_they_asked_for(parts, wanted)
        return _shorten(part) if part else None
    if not best_overlap:
        # "And how long?" over an answer that lists the options - "6 minutes for a runny yolk, 7
        # for jammy, 9 to 10 for hard" - has no one answer, and picking the first is a guess at
        # what they want. The range of the options is the honest answer and it is still a figure.
        choices = _option_range(sentences[0]) if sentences else ""
        if choices:
            return choices
        # Options for several different things do not make one range, and the answer is the
        # option for the thing the conversation is on: "how long should i rest a joint of beef"
        # then "and how long?" was answered "15 to 10 minutes" - the first and last figures of
        # four different joints - and then "15 to 20 minutes for a chicken", which is another
        # dish's time. The clause that names the subject is the one figure that answers it.
        part = _the_option_for_the_topic(sentences[0], line, memory) if sentences else None
        if part:
            return part
    period = _asked_period(line)
    parts = [part for sentence in sentences for part in _duration_clauses(sentence)
             if not already_said(memory, part) and _in_period(part, period)]
    part = _step_they_asked_for(parts, wanted)
    return _shorten(part) if part else None


def _already_for_this_size(line, answer):
    """True when the answer has already worked its rate out for the size this line names.

    Then the figure is in the answer for that size ("1 hour 40"), and saying the rule again
    would be longer than the answer they are owed.
    """
    asked, told = AMOUNT.search(str(line or "")), OWN_SIZE.search(str(answer or ""))
    if not asked or not told:
        return False
    grams = _in_grams(asked.group(0))
    said = _in_grams(told.group(1) + told.group(2))
    return grams is not None and grams == said


def _in_grams(text):
    """An amount in grams, or None when it is not a weight."""
    found = re.match(r"\s*(\d+(?:\.\d+)?)\s*(kg|g|lb|lbs|pound|pounds|oz|ounce|ounces)\b",
                     str(text or ""), re.I)
    if not found:
        return None
    return round(float(found.group(1)) * WEIGHT_IN_GRAMS[found.group(2).lower()], 1)


def _names_another_thing(line, answer, about=()):
    """True when the line names a word the answer is not about.

    "how long do i roast a 2kg leg of lamb" after the bird's answer carries a weight the rate
    could work out, but the lamb is not the thing the rate is for, so the figure would be
    somebody else's. A word that is only the ask ("long", "one") does not count.
    """
    said = set(stem(word) for word in keywords(answer))
    said |= set(stem(word) for word in about or ())
    for word in keywords(line):
        if AMOUNT.search(word) or word in ASK_ONLY:
            continue
        if stem(word) not in said:
            return True
    return False


def sized_reply(answer, line, memory, about=()):
    """The time this answer's own rate gives for the size this line names, or None.

    Public because the module that answers with the entry's own paragraph needs it too: the
    question "how long for 250g" reaches the roast entry by name, so the whole paragraph comes
    back before any follow-up is looked at, and the figure they asked for is inside it. `about`
    is what the entry is about, so a line naming the dish ("a 250g chicken") is not read as a
    line naming something else than the answer, which says "bird" and never "chicken".
    """
    if _names_another_thing(line, answer, about) or _already_for_this_size(line, answer):
        return None  # the rate is not for this thing, or the figure for this size is in the answer
    return _sized_reply(answer, line, memory)


def _sized_reply(answer, line, memory):
    """The time the answer's own rate gives for the amount in the line, said with the rule, or None.

    "how long for a 1.5kg one" after "20 minutes per 500g plus 20 minutes": the rule worked out
    for their size, with the rule kept behind it so nothing is hidden. Asked again in the same
    words, the same time is said another way rather than word for word.
    """
    amount = AMOUNT.search(str(line or ""))
    if not amount:
        return None
    sized = time_for_amount(answer, line)
    if not sized:
        return None
    rule = _rate_said(answer)
    if not rule:
        return None
    said = amount.group(0)
    times = _times_asked(line, memory)
    if times >= 2:
        return f"{sized.capitalize()} for {said}, the same rule: {rule}."
    if times == 1:
        return f"Still {sized} for {said}: {rule}."
    return f"About {sized} for {said}: {rule}."


def _times_asked(line, memory):
    """How many turns in a row just before this one asked this same line, word for word."""
    wanted = " ".join(str(line or "").lower().split())
    count = 0
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            break
        if " ".join(str(turn.get("user") or "").lower().split()) != wanted:
            break
        count += 1
    return count


def _rate_said(answer):
    """The sentence of an answer that states a cooking rate, without the size it worked out."""
    for sentence in SENTENCE.split(str(answer or "")):
        if not RATE_BY_WEIGHT.search(sentence):
            continue
        head = re.split(r"[,;]?\s+so\b", sentence, maxsplit=1)[0].strip(" .,;")
        head = re.sub(r"^about\s+", "", head, flags=re.I).strip(" .,;")
        return head[:1].lower() + head[1:] if head[:1].isupper() else head
    return ""


def _phrase(text):
    """A phrase of an answer said as a sentence of its own: "three times a week" -> "Three..."."""
    text = str(text or "").strip(" ,;:")
    return text[:1].upper() + text[1:] + "." if text else ""


def has_time(text):
    """True when a line or an answer carries a length of time in it ("40 to 45 minutes")."""
    return bool(TIME.search(str(text or "")))


def _worked_out_for_this_line(understood, line, answer):
    """The time an answer's own rate gives for the amount this line names, or None.

    "how long for 700g" after "20 minutes per 500g plus 20 minutes" is the same question about
    another size of the same roast: the answer works it out (time_for_amount), so it is a
    follow-up on what we are on even without an "it" or a "one" to point back with. When the
    answer carries no rate in weight (boiling an egg, roasting potatoes) nothing is worked out
    and the line is left to the subject it names.
    """
    if not isinstance(understood, dict) or "how_long" not in (understood.get("asks") or ()):
        return None
    return time_for_amount(answer, line)


# "where are you", "who are you", "what are you": the thing these name is the bot. Every word
# of them is a stopword, so they looked like a bare ask for a property of the last answer, and the
# answer just given came back with a "Same as before:" in front of it - "where are you" after a
# pot of rice re-served the rice. A question about the bot is not a question about the rice, and
# the bot's own reply (the chat module) is the one that answers it.
_ASKS_WHAT_I_AM = re.compile(
    r"^\s*(?:(?:so|ok|okay|and|but|hey|well)\s+)*"
    r"(?:where|what|who|which)\s+(?:are|r)\s+(?:you|u|ya)\b"
    r"(?:\s+(?:from|based|exactly|then|though|really|actually|now))?\s*\??\s*$")


def asks_only(understood):
    """True when the line asks for a property and names no thing of its own.

    "how long do I need?", "what temperature?", "and how much?" carry nothing but the ask. The
    thing they are about is the answer just given, so they are a question about that answer and
    not about a neighbour entry the ask happens to fit: "how long do I need?" after a tray of
    roast potatoes also reaches the boiled-potatoes entry, and boiling is not the answer to
    roast ones.

    A line made only of stopwords is this too ("what should I get for it?"), and what it wants
    is the answer just given, not a neighbour. The one exception is a request to carry on
    ("what should I do about it?"), which asks for the next step rather than a sentence of the
    last answer; `same_as_before` and `leans_on_topic` stand down for those.
    """
    if not isinstance(understood, dict) or not (understood.get("asks") or ()):
        return False
    line = understood.get("clean") or understood.get("text") or ""
    if _ASKS_WHAT_I_AM.match(str(line).lower()):
        return False
    return not [word for word in keywords(line) if word not in ASK_ONLY]


def _earlier_subject_sentence(line, understood, memory, skip, turns_back=2):
    """A sentence from the answer to an earlier subject this line still has a word in common with."""
    records = memory.get("topics")
    if not isinstance(records, list):
        return None
    mine = {stem(word) for word in keywords(line)}
    seen = 0
    for record in reversed(records):
        if not isinstance(record, dict) or record is skip:
            continue
        asked = str(record.get("text") or "")
        if not asked or already_said(memory, record.get("bot")):
            continue
        if not mine & {stem(word) for word in keywords(asked)}:
            continue
        seen += 1
        if seen > turns_back:
            return None
        answer = entry_answer(memory, asked) or str(record.get("bot") or "")
        chosen = _pick_sentence(line, understood, answer, memory, strict=True)
        if chosen:
            return chosen
    return None


def _repeats_the_question(line, asked):
    """True when this line asks what the conversation is already about, word for word."""
    wanted = [stem(word) for word in keywords(line)]
    if not wanted:
        return True
    said = [stem(word) for word in keywords(asked)]
    return sum(1 for word in wanted if word in said) >= 0.6 * len(wanted)


def already_said(memory, text, turns_back=3):
    """True when this exact wording was one of the bot's last few replies."""
    said = " ".join(str(text or "").lower().split())
    if not said:
        return True
    for turn in (memory.get("turns") or [])[-turns_back:]:
        if isinstance(turn, dict) and " ".join(str(turn.get("bot") or "").lower().split()) == said:
            return True
    return False


# The verbs and ask words that make a "how do I ..." line a request for the steps of the thing we
# are already on, rather than a question about a new thing ("how do i cancel her insurance").
STEP_ASK_WORDS = frozenset("""
how what when where which who why do does did i we you me my it this that they he she
fix sort make get work use put keep go come start stop change deal help try take set tell say
give find need want know best should can could would will shall may might
""".split())


def _names_something_new(line, answer):
    """True when the line names a thing the answer never mentions."""
    said = {stem(word) for word in keywords(answer)}
    for word in keywords(line):
        if word in STEP_ASK_WORDS or stem(word) in said:
            continue
        return True
    return False


# The words that make the next word a thing the line names for itself: "what about a leg of
# lamb", "and the radiator?".
# A line that asks the bot to fetch something is a request, not a thing of its own.
REQUEST_A_THING = re.compile(r"\b(?:find|give|send|show|get|recommend|suggest|list|write|make)"
                             r" me\b|\bdo you have\b|\bany chance\b"
                             r"|\bcan you (?:find|give|send|show|recommend|suggest|list\b)", re.I)


A_THING = frozenset("a an the my our another some this that".split())


def _named_a_fresh_thing(text, record, answer=""):
    """True when the line names a thing the topic does not have: "a leg of lamb" after a chicken.

    A word that was already in the answer just given is a detail of the subject, not a new one:
    "does the vinegar matter" and "what about the yolk" after the poached egg are about the egg.
    """
    if REQUEST_A_THING.search(str(text or "")):
        # "can you find me a recipe" asks the bot for the answer, it does not name a new subject:
        # the recipe wanted is the one for the thing the chat is already on.
        return False
    known = {stem(word) for word in (record or {}).get("words") or []}
    known |= {stem(word) for word in words(str(answer or ""))}
    said = words(str(text or ""))
    for at, word in enumerate(said[:-1]):
        if word.lower() in A_THING and stem(said[at + 1]) not in known:
            return True
    return False


# How many turns back the card a follow-up draws on can have been given.
MOVED_KEEP = 8


def _the_thing_the_chat_moved_to(whole, line, memory, keep=MOVED_KEEP):
    """The entry of the thing named after the card was given, when the chat moved to it.

    A follow-up that names nothing of its own ("how long does it last") leans on whatever the chat
    is on, and the card a follow-up draws on is the entry's answer - which can be several turns
    old. That card is the answer only while the chat is still on its subject. A statement in
    between that names a thing of its own, reaches its own entry and was answered as its own
    subject moves the chat to that thing, even though it was a statement: "we want to try for a
    baby" ... "my baby has a fever" ... "how long does it last" was handed "Have sex every two or
    three days rather than saving up.", a clause of the trying-for-a-baby card, as the answer to a
    question about a child's fever. A wrong fact is the worst reply there is.

    Only while the thing it moved to can answer the line itself: "how much should i pay a plumber"
    with a fever remark in between is still a question about the plumber, and a subject with no
    figure of the kind asked for is no better than the card the person was on.
    """
    from .narrow import SPANS, kind_of  # lazy: the store needs no reader of its own
    turns = [turn for turn in (memory.get("turns") or [])[-keep:] if isinstance(turn, dict)]
    wanted = words(str(whole or ""))[:8]
    at = None
    for index, turn in enumerate(turns):
        if words(str(turn.get("bot") or ""))[:8] == wanted:
            at = index
    if at is None:
        return None
    was = _entry(str(turns[at].get("user") or ""))
    if was is None:
        return None
    figure = SPANS.get(kind_of(line))
    if figure is None:
        return None
    for turn in reversed(turns[at + 1:]):
        said = str(turn.get("user") or "")
        if not said or words(said) == words(str(line or "")):
            continue  # the turn in hand is the one being read
        if turn.get("module") in (None, "answers"):
            continue  # the knowledge base answered it, so it was read as part of this thing
        named = _entry(said)
        if named is None or named == was:
            continue
        if figure.search(str(getattr(named, "reply", "") or "")):
            return named
    return None


def left_for_a_blank(memory, line):
    """True when the chat moved to a thing named in between and got no answer for it.

    "how do I roast a chicken" / "what about a leg of lamb?" (no entry, so a hedge) / "and how
    long should that take?" is a question about the lamb: the chicken times are a wrong answer
    rather than a helpful one, so nothing is drawn from the older subject. A line that only says
    what to do about the thing we are on ("can I fix it myself?") leaves the topic where it was.
    """
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return False
    last = turns[-1]
    if " ".join(words(str(last.get("user") or ""))) == " ".join(words(str(line or ""))):
        return False  # the turn in hand is the one being read: nothing to look past
    if last.get("module") == "answers":
        return False
    asked = str(last.get("user") or "")
    if not _a_question(asked):
        # A statement that names something is usually a detail of the thing the chat is on
        # ("one loves dinosaurs and the other loves space" is the twins' party), so it does not
        # move the chat off that thing. A question does name what it asks about.
        return False
    if not POINTS_BACK.search(str(line or "")):
        # The line has to point at the thing left blank ("and how long should that take?"). A
        # line that names nothing and points at nothing is a question about what the chat was on
        # before the remark: "how do i make bread" / "and the radiator" / "what temperature" is
        # the oven, and "how do i sharpen a knife" / "and the cat" / "what about the whetstone"
        # is the whetstone in the knife answer. Read while looking past a remark, both were
        # hedged, which is a worse answer than main's.
        return False
    # The answer on the subject is part of what the chat knows: a word in it is a detail of that
    # subject ("does the vinegar matter" and "what about the yolk" are about the poached egg),
    # so a line asking about that word does not move the chat to a thing of its own.
    record = carried_topic(memory, line)
    answer = entry_answer(memory, str((record or {}).get("text") or "")) or str(last.get("bot") or "")
    return _named_a_fresh_thing(asked, record, answer)


# A line that points back at the thing it asks about: "and how long should that take?", "how
# long does it take", "what about those". A question with none of these words and no thing of its
# own ("what temperature") is about what the chat was on before the remark in between.
POINTS_BACK = re.compile(r"\b(?:it|that|this|those|these|they|them|its)\b|\bthe one\b", re.I)


# A line that asks something: it ends on a question mark or opens with a question word. Only
# such a line says what the chat has moved to; a statement adds to what we are already on. The
# name is its own ("a question for the topic reader", not "asks") because the file already has an
# _asks, the repo's own reader that asks_after uses: a second definition of the same name silently
# takes over every earlier caller, and the two readers disagree about "and the pressure".
A_QUESTION = re.compile(r"\?\s*$|^\s*(?:and|also|or|so|but|then)\s+\S+"
                        r"|^\s*(?:what|how|which|where|when|who|why|whose|is|are|was|were|do"
                        r"|does|did|can|could|should|would|will|shall|must|have|has|had|am)\b",
                        re.I)


def _a_question(text):
    return bool(A_QUESTION.search(str(text or "")))


# A question that names no subject of its own, only what it wants to know: "what should I wear",
# "what should I do first", "where should I start". Alone it is about nothing. The advice word is
# what tells it from a question about the person's own facts ("which city did I say first",
# "what is my cat called", "what am I planning"), which is the memory's to answer, not the
# topic's: those name something of theirs and are not advice asks.
BARE_ASK = re.compile(r"\b(?:what|which|how|where|when)\b(?![^?.!]{0,40}\b(?:did|have|has)\s+i\b)"
                      r"[^?.!]{0,40}\b(?:should|shall|can|could|ought)\b"
                      r"|^\s*(?:so\s+)?(?:should|shall|can|could|must|do)\s+(?:i|we)\b", re.IGNORECASE)


BARE_WORDS = 8


def bare_question(understood, memory):
    """True for a short question with no subject of its own, after a topic it can lean on.

    "What should I wear" after "I'm going to a wedding next week" is a question about the
    wedding - the knowledge base has the wedding outfit entry and the line on its own reaches
    nothing, so it was read as a request for a search. Only a line that reaches no entry by its
    own words and only while there is a topic to lean on, so "what should I cook" said on its
    own is still the general question it is.
    """
    if not isinstance(understood, dict) or understood.get("kind") != "question":
        return False
    line = " ".join(str(understood.get("clean") or understood.get("text") or "").lower().split())
    if not line or len(line.split()) > BARE_WORDS or is_ack(line):
        return False
    if not BARE_ASK.search(line):
        return False
    if carried_topic(memory, line) is None:
        return False
    if follows_on(understood, line):
        return False  # it already points back at the topic ("how do I fix it?"): not bare
    if ASKS_ABOUT_THEMSELVES.search(line):
        return False  # the topic is not the answer: "when am i going" is in the plans memory keeps
    return _entry(line) is None


# "when am i going", "where are we staying", "what did i say": the line puts the person in the
# question as the subject of their own doings, and the answer is what they told us, not the
# knowledge base entry for the topic. Only the forms that make the person the subject (am/are/
# was/were/did) - "how do i start" and "what should i wear" carry a modal and a verb of their
# own, and those are questions about the topic.
ASKS_ABOUT_THEMSELVES = re.compile(
    r"\b(?:what|where|when|who|which|how|why)\s+(?:am|are|was|were|did)\s+(?:i|we)\b")


# A topic is the thing a follow-up is about only while the chat is still on it. One reply of
# small talk ends it, and the ask after it leans on that instead of on the topic:
# "what should i have for dinner" / "i only got mince and some spuds" / "hows it going with u" /
# "why is that" was widened with the dinner line, two turns stale, and answered with the next dish
# in the plan - a baked potato nobody had asked for, an hour after dinner.
#
# What keeps it alive: an acknowledgement or a greeting, which name nothing of their own, and any
# line that is about something ("and when did i tell you i start" is still the job). What ends it:
# a line that is small talk, because a question about the bot's day puts the chat on the bot, and
# the thing on the screen is no longer what the next ask is about.
def _still_the_topic(record, memory):
    """True when no turn since this topic's has put the chat on the bot instead."""
    if not isinstance(record, dict):
        return False
    index = record.get("turn")
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(index, int) or not isinstance(turns, list):
        return True
    from ..understanding import understand
    for turn in turns[index + 1:]:
        if not isinstance(turn, dict):
            continue
        said = " ".join(str(turn.get("user") or "").lower().split())
        if not said or is_ack(said) or said in GREET:
            continue
        if str(understand(said).get("intent") or "") == "smalltalk":
            return False
    return True


def carried_topic(memory, text):
    """The topic this line carries on from: what we were on before it, not the line itself.

    memory_store notes every line, so on a follow-up the current topic can already be this very
    line (with its words merged in). Reading it back out of memory["topics"] keeps the subject
    the follow-up left out.
    """
    line = " ".join(words(text))
    records = memory.get("topics")
    if isinstance(records, list):
        for record in reversed(records):
            if not isinstance(record, dict):
                continue
            if " ".join(words(record.get("text") or "")) != line:
                # A detail points back at the thing it is a detail of: "he is allergic to nuts"
                # is what we were on before this line, but the thing the next ask is about is
                # the cake, and the nuts' words reach nothing.
                return _thing_of(memory, record) or record
    return current(memory)


def _only_the_topics_own_words(text, record):
    """True when every content word of the line is a word the topic already carries."""
    known = [word for word in (record or {}).get("words") or [] if isinstance(word, str)]
    if not known:
        return False
    return not [word for word in _content_words(text)
                if not any(alike(word, said) for said in known)]


# A line that only names the next thing of the same ask: "and for lunch" straight after "what
# should I have for breakfast". The knowledge base has a lunch answer; it has no answer to an
# "and for" line, so the ask is carried on with the new thing in it.
NEXT_SLOT = re.compile(r"^(?:and|also|plus|then|ok|okay|so)\s+(?:what\s+)?for\s+([a-z0-9' ]{2,24})$")


ASK_SLOT = re.compile(r"\bfor\s+([a-z0-9' ]{2,24})$")


ASK_WORDS = re.compile(r"\b(?:what|which|how|where|when|who|why|should|shall|can|could|would|any)\b")


def next_slot_reading(understood, memory):
    """'and for lunch' read as the last question with lunch in it, or None.

    Only a line that says nothing but the next thing, and only when the line before it asked
    something with a "for" in it ("what should I have for breakfast"), so an "and for" line
    after news stays the plain acknowledgement it is.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    line = " ".join(str(understood.get("clean") or understood.get("text") or "").lower().split())
    slot = NEXT_SLOT.match(line)
    if slot is None or understood.get("kind") == "question":
        return None
    turns = memory.get("turns")
    previous = ""
    if isinstance(turns, list) and turns:
        previous = str((turns[-1] or {}).get("user") or "")
    asked = " ".join(previous.lower().split())
    if not asked or ASK_WORDS.search(asked) is None:
        return None
    tail = ASK_SLOT.search(asked)
    if tail is None:
        return None
    thing = slot.group(1).strip()
    if not thing or thing == tail.group(1).strip():
        return None
    reading = dict(understood)
    reading["clean"] = (asked[:tail.start()] + "for " + thing).strip()
    reading["text"] = reading["clean"]
    reading["words"] = words(reading["clean"])
    reading["kind"] = "question"
    reading["intent"] = "question"
    return reading


# A line that asks how two animals will get on names neither of them ("will they get
# on?").  With a new pet in the plan and one already in the house, the introduction
# question can be put back together from the two facts the store keeps.
TWO_PETS_ASK = re.compile(
    r"^(?:and |so |but )?(?:will (?:they|the two(?: of them)?|both(?: of them)?) (?:get on|get along|"
    r"fight|like each other|settle)"
    r"(?: (?:ok|okay|alright|fine|together))?"
    r"(?: with (?:each other|one another))?"
    r"|are they going to (?:get on|get along|fight)"
    r"|(?:can|could|will) (?:they|the two) (?:live|get) (?:together|along))"
    r"[\s?.!]*$",
    re.I)


PET_WORD = re.compile(
    r"\b(kittens?|cats?|pupp(?:y|ies)|dogs?|rabbits?|bunn(?:y|ies)|hamsters?|guinea pigs?|"
    r"ferrets?|parrots?|budgies?)\b", re.I)


PET_ONE = {
    "kittens": "kitten", "cats": "cat", "puppies": "puppy", "dogs": "dog",
    "rabbits": "rabbit", "bunnies": "bunny", "hamsters": "hamster",
    "guinea pigs": "guinea pig", "ferrets": "ferret", "parrots": "parrot",
    "budgies": "budgie",
}


PET_ARRIVING = re.compile(
    r"\b(?:getting|bringing|bringing home|joining|coming|arriving|arrives|arrive|"
    r"next (?:week|month|year)|in (?:january|february|march|april|may|june|july|august|"
    r"september|october|november|december)|soon)\b", re.I)


PET_EXISTING = re.compile(r"\b(?:already|existing|older|old|has been|have had)\b", re.I)


def _introduction_covered(new, old):
    """True when an animal introduction card answers this pair.

    `cat-second-cat` covers a new cat or kitten with an older cat; `cat-dog-intro`
    covers a cat or kitten with a dog or puppy in either direction.  A rabbit,
    hamster or bird has no introduction answer yet, and the people-introduction
    card is not a substitute.
    """
    cats = {"cat", "kitten"}
    dogs = {"dog", "puppy"}
    return ((new in cats and old == "cat")
            or (new in cats and old in dogs)
            or (new in dogs and old in cats))


def introduction_question(text, memory):
    """The full introduction question for "will they get on?" after a second pet.

    A line that asks about the two animals names neither of them, so on its own it reaches
    no knowledge entry. When the plan names a new pet - or the line that brought it in says
    it is on its way - and the store has one other pet, the line is about introducing those
    two: "how do i introduce a new kitten to my older cat". Empty when the line is not that
    ask, when the store cannot tell which two animals it means, or when no animal card
    answers that pair, so a line about a child, an unrelated "problem" or a kitten and a
    rabbit is left alone.
    """
    if not isinstance(text, str) or not isinstance(memory, dict) or not TWO_PETS_ASK.search(text):
        return ""
    known = memory.get("user")
    if not isinstance(known, dict):
        return ""
    animals = []
    for pet in known.get("pets") or ():
        animal = pet.get("animal") if isinstance(pet, dict) else None
        animal = str(animal or "").strip().lower()
        animal = PET_ONE.get(animal, animal)
        if animal and animal not in animals:
            animals.append(animal)
    if len(animals) != 2:
        return ""
    plan = known.get("plan")
    named = PET_WORD.search(plan) if isinstance(plan, str) else None
    new = ""
    if named is not None:
        new = PET_ONE.get(named.group(1).lower(), named.group(1).lower())
    else:
        # A line that says the pet is on its way is the new one even when the store did not
        # keep it as a plan: "a kitten is joining us in june".  The line that says it is
        # already here ("my old cat has been here ten years") is the one it is joining.
        arriving = []
        for fact in memory.get("facts_log") or ():
            if not isinstance(fact, dict) or fact.get("key") != "pet":
                continue
            said = str(fact.get("text") or "")
            found = PET_WORD.search(said)
            if found is None or not PET_ARRIVING.search(said) or PET_EXISTING.search(said):
                continue
            animal = PET_ONE.get(found.group(1).lower(), found.group(1).lower())
            if animal not in arriving:
                arriving.append(animal)
        if len(arriving) == 1:
            new = arriving[0]
    if not new:
        return ""
    others = [animal for animal in animals if animal != new]
    if len(others) != 1:
        return ""
    old = others[0]
    if not _introduction_covered(new, old):
        # The knowledge base has animal introductions only for a cat meeting a cat and a
        # cat meeting a dog.  A kitten and a rabbit would otherwise be sent to the card
        # that introduces two people, which is a confident answer about the wrong thing;
        # leaving the line alone lets the honest hedge answer it.
        return ""
    return "how do i introduce a new %s to my older %s" % (new, old)


# --- what the weather will be like on the trip -------------------------------------------
# A day and a month are not what a chat is about, but the place and the month of a trip are what
# a weather question is answered with, so the follow-up below reads them back out of the topic.
WEATHER_WORDS = frozenset("""
weather hot hotter cold colder warm warmer cool freezing boiling rain rains raining rainy
showers shower sunny sun sunshine cloudy cloud clouds wind windy humid humidity temperature
degrees forecast snow snowing coat coats jacket layers jumper
""".split())


MONTH_NAMES = frozenset("""january february march april may june july august september october
november december""".split())


# The grammar a line can spend on asking the weather and nothing else: "will it rain this week?"
# is about the weather, while "my weather station is broken" is about the station.
WEATHER_NOISE = frozenset("""
ok okay k so and but the a an in on at for to of it its this that these there here what whats
how will would be is was were am get getting go going we you they i me my our us week weeks
day days month months time much many like look looks outside today tomorrow tonight now then do
does did shown show get better need bring bring take maybe probably out up over all there
""".split())


# A line that says when or where it is about, and it is here and now rather than the trip: "what's
# the weather like today", "what's the weather like here", "is it raining now" are questions
# about the window the person is standing at, and the trip's month is a climate average for a
# place they are not in yet. A wrong fact is worse than the honest "I can't see a forecast".
NOW_AND_HERE = re.compile(
    r"\b(?:today|tonight|tomorrow|now|right now|outside|here|this afternoon|this evening"
    r"|this morning|at the moment|currently)\b")


# What asks a question, for a line short enough that the weather word is all it is about.
WEATHER_ASKS = re.compile(
    r"\?|^(?:is|are|do|does|will|would|can|could|should|shall)\b"
    r"|\b(?:what|whats|how|when|where|which|will|would|can|could|should|any|much|many|need)\b")


def the_weather_ask(understood):
    """True for a line that only asks about the weather, naming nothing else of its own.

    "what's the weather like", "how hot will it be", "will it rain this week" are all of them
    asks with no subject: on their own they are a question about the meaning of the words, and
    the knowledge base has no numbers to give. A line that names something else is not this.
    """
    line = str(understood.get("clean") or understood.get("text") or "")
    said = words(line)
    if not any(word in WEATHER_WORDS for word in said):
        return False
    if ASK_CUE.search(line.lower()) is None and WEATHER_ASKS.search(line.lower()) is None:
        return False
    return all(word in WEATHER_WORDS or word in WEATHER_NOISE for word in said)


def the_place_and_month(text):
    """The place and the month a line names, as the knowledge base spells them, or (None, None).

    Only the places it has climate figures for are read, so the answer that follows can always
    be given: a place it knows nothing about is left to the hedge it gets today.
    """
    low = " ".join(str(text or "").lower().split())
    if not low:
        return None, None
    from ..knowledge.travel import CITY_CLIMATE  # lazy: the store does not need the facts
    for name in sorted(CITY_CLIMATE, key=len, reverse=True):
        if re.search(r"(?<![a-z])" + re.escape(name) + r"(?![a-z])", low) is None:
            continue
        month = next((word for word in sorted(MONTH_NAMES, key=len, reverse=True)
                      if re.search(r"(?<![a-z])" + word, low)), None)
        return name, month
    return None, None
