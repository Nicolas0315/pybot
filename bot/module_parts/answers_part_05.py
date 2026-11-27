"""Part 5 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re

from .. import memory as mem
from ..compose import pick
from ..knowledge import dishes, entries as all_entries, shopping
from ..knowledge.lookup import (
    EXPLAIN_FILLER, EXPLAIN_LEADS, about_the_topic, find, names_its_own_subject,
)
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import keywords
from ..memory import again as same_again  # the short of an answer already on the screen
from ..memory.again import NOTHING_MORE  # said of an answer with nothing further in it
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..understanding import kinds
from ..memory.ack import VAGUE
from ..memory.topics import current as the_topic, is_follow_up
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import keywords
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory.narrow import SIGNALS, flat, kind_of as asked_kind
from ..understanding import understand
from .answers_part_01 import (
    NO_FIGURE, NO_STEP, SPOKEN, TIMEISH, _first_step, SENTENCE, _flat, _opening, _in_short, WORD,
    _said_before,
)
from .answers_part_02 import (
    _asks_for_more, _key_words, _the_same_kind_of_thing, _refused, _own_thing, REFUSE_CHOICE,
    REFUSE_OPEN, REFUSE_WISH,
)
from .answers_part_03 import (
    PROPERTY_WORDS, _is_about, _last_answer,
)
from .answers_part_04 import (
    GENERIC, NOT_NEW, SAY_IT, _ASKING_ONLY, NAMING, OPENS_WITH_AN_AUXILIARY, HANDOVER_FILLER,
    CHOICE_KINDS, NO_THING_NAMED, AFTER_A_PLACE, ASKS_A_QUANTITY, DESCRIBES_ONE, THING_AFTER,
    _AUXILIARY, _with_bare_subject,
)


def _figure_missing(reply, text):
    """The honest short line for a figure the answer does not hold, or None.

    Only the property the line asks for counts: an answer with no time in it is no answer to
    "how long", but it is the right answer to "how do i", so this is used on the repeats and
    follow-ups that ask for one part of an answer, never on the first ask.
    """
    kind = asked_kind(text)
    if kind not in NO_FIGURE:
        return None
    if _answers_the_figure(text, reply):
        # The answer holds a figure of the kind asked ("about two hours", "£80 to £200"), so it
        # is answering the line and the short form of it is the right thing to give.
        return None
    if kind in ("time", "clock") and (SPOKEN.search(str(reply or ""))
                                       or TIMEISH.search(str(reply or ""))):
        return None
    step = _first_step(reply)
    if not step:
        return NO_FIGURE[kind] + NO_STEP
    return NO_FIGURE[kind] + step[:1].lower() + step[1:]


def _figures_changed(reply, said):
    """True when both carry figures and the answer has one the earlier line did not."""
    mine = set(NUMBER_IN_TEXT.findall(str(reply or "")))
    theirs = set(NUMBER_IN_TEXT.findall(str(said or "")))
    return bool(mine and theirs and mine - theirs)


def _same_answer(reply, said):
    """True when `said` is this answer, or the short form of it, with or without a lead-in.

    A repeated answer comes back in three shapes: the whole paragraph again, the paragraph behind
    a lead-in ("Same as before: <answer>"), or the one sentence of it a friend repeats. The
    opening alone does not cover the third: a two-part answer asked a third time is repeated as
    its second sentence first ("how much water should i drink" answers with the six-to-eight
    glasses sentence, then the tea-and-coffee one), so a count read from the opening alone saw a
    new question and started the lead-in over at the long answer."""
    mine = _flat(reply)
    theirs = _flat(said)
    if not mine or not theirs:
        return False
    if _opening(mine) in theirs:
        return not _figures_changed(reply, said)
    for sentence in SENTENCE.split(str(reply or "")):
        part = _flat(sentence)
        if len(part) > 20 and part in theirs:
            # The same sentence with a different figure in it is a different answer, not this one
            # said again: "make it 3 instead" after the timing for a 2kg bird comes back as the
            # same rule worked out for three kilos, and the sentence around the figure is word
            # for word. Counted as a repeat it was handed over behind "Nothing more on it I'm
            # afraid", which tells the person the answer has not changed when it just has.
            return not _figures_changed(reply, said)
    # A step handed out of this answer is the answer in part: "The first thing to do: Open the
    # bleed valve at the top with a radiator key." a turn after the paragraph is that answer
    # still on the screen, so the same ask again is the repeat and gets the lead-in rather than
    # starting the ladder over with the paragraph printed bare.
    for clause in str(said or "").split(":"):
        cut = _flat(clause)
        if len(cut.split()) >= 6 and cut in mine:
            return True
    return False


def _asked_again(text, reply, memory):
    """How many times this same line was asked before and given this same answer: 0 when it is
    a new question, 1 on the first repeat, 2 on the second. A count rather than a flag so the
    wording can move on with each repeat (STYLE.md, "Never answer the same way twice in a row")."""
    wanted = _flat(text)
    mine = _opening(_flat(reply))
    if not wanted or not mine:
        return 0
    count = 0
    # Only the run of turns just before this one counts. "As before" points at the last thing
    # said, so when the person asked something else in between, the question is coming back to
    # an answer two turns old and the plain answer is what they need (calm-turtle, #854).
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            break
        if _flat(turn.get("user")) != wanted:
            break
        # The answer already given, framed or not: an earlier "Same as before: <answer>" is the
        # same answer, and so is the sentence of it the repeat was shortened to, so the count
        # goes on rising and the wording can move with it.
        if not _same_answer(reply, turn.get("bot")):
            break
        count += 1
    return count


def _times_the_answer_was_said(reply, memory):
    """How many turns in a row the chat has just had this answer, counted before this one."""
    times = 0
    for turn in reversed((memory.get("turns") or [])[-4:]):
        if not isinstance(turn, dict) or not _same_answer(reply, turn.get("bot")):
            break
        times += 1
    return times


def _nothing_more_said_again(reply, text, memory):
    """The same answer for a line that names no part of it, said as nothing further, or ""."""
    if not _asks_for_more(text):
        return ""
    times = 0
    for turn in reversed((memory.get("turns") or [])[-4:]):
        if not isinstance(turn, dict) or not _same_answer(reply, turn.get("bot")):
            break
        times += 1
    if not times:
        return ""
    short = _in_short(reply) or reply
    underneath = same_again.the_same_thing_underneath(text, short, times, memory)
    if underneath:
        return underneath
    return NOTHING_MORE[min(times, len(NOTHING_MORE)) - 1].format(reply=short)


def _reaches_another_subject(text, item, memory):
    """True when the entry the line reaches is about something the conversation is not.

    A follow-up names no thing of its own, so it is answered on its bare words: "any other
    ideas" is the key word of the quick-dinners entry and of nothing else, so a chat about films
    got "Quick: tuna pasta in 15, macaroni cheese in 25". The check is on the words around the
    line - the current topic's own words and the subject's - against the entry's: when the entry
    shares none of them it is a different subject, and no wording makes that the answer.
    """
    try:
        if not is_follow_up(text, memory):
            return False
        # A line that carries a subject of its own is a new question, whatever the chat was
        # about: "what can i make with eggs" in the middle of a film chat is a cooking question
        # and the omelette is its answer. Only a line that names nothing of its own can be
        # answered from another subject, and this is the read that says which it is. Without it
        # every "what can i make with eggs/leeks/chicken/mince" was dropped as a follow-up on
        # another subject and fell through to the hedge, while the meal was in the table all along.
        if str((understand(text, {}) or {}).get("topic") or ""):
            return False
        # Nothing has been said before this line, so there is no subject it could be reaching
        # past: the store records the line as the current topic before the entry is looked up,
        # so on the first turn of a conversation "what can i make with mince" is a follow-up of
        # itself, shares no word with the dinners entry's keys ("cook" is in them and "make" is
        # not) and stood down - the person got the search hedge, while "what can i cook with
        # mince" got the recipe. A guard against answering the wrong subject has nothing to
        # protect on a first line.
        if not (memory.get("turns") if isinstance(memory, dict) else None):
            return False
        around = {str(word).lower() for word in ((the_topic(memory) or {}).get("words") or ())}
        around |= {str(word).lower() for word in keywords(mem.subject(memory) or "")}
        if not around:
            return False
        # The entry's keys carry the grammar too ("any", "something"), so both sides go
        # through keywords(): "any other ideas" shares the word "something" with the dinners
        # entry and nothing else, and that is not a subject in common.
        keys = set(keywords(" ".join(str(word) for word in _key_words(item))))
        # A placeholder is not a subject either: "something" is in the topic's words and in the
        # dinners entry's keys, and on its own it says nothing about the thing being discussed.
        around = {word for word in around if word not in VAGUE}
        keys = {word for word in keys if word not in VAGUE}
        # Two entries about the same kind of thing are not another subject. "do i need to see a
        # physio" after "my back hurts" is a question about the back, and the physio entry is a
        # body entry - but the two share no word, because the chat's words are "back" and "hurt"
        # and the entry's keys are "physio" and the ask, so the word test stood it down and the
        # person got the search shrug while the answer ("see a physio if the pain has lasted more
        # than a fortnight") was there all along. The domain is what both of them are about, so
        # the guard reads it as well as the words.
        if _the_same_kind_of_thing(item, memory, text):
            return False
        # A line asking what the entry's own word means is a new subject in so many words: "what
        # is inflation" after a back pain chat asks about inflation, and the trouble the talk was
        # on has nothing to do with it. Read as a follow-up on that, the money row was dropped for
        # a search hedge the table answers.
        if _a_definition_of_the_entry(text, item):
            return False
        return bool(keys) and not (keys & around)
    except Exception:  # noqa: BLE001 - a reading that fails just leaves the entry alone
        return False


def _keyed_on_the_line(item, text):
    """True when the entry is keyed on a word the line itself says: "wear" in "what do i wear".

    A word that only gives the shape of the ask names nothing of its own: "how long should i cook
    it for next time" was keyed on "long" and on "next" - the words of the plan entry, whose keys
    hold the length of a job and "next week" - so the line was read as a plan question from
    another subject, and the rice answer came back whole instead of its twelve minutes."""
    keys = _key_words(item)
    for word in re.findall(r"[a-z']+", str(text).lower()):
        if len(word) < 3 or word in GENERIC or word in NOT_NEW or word in PROPERTY_WORDS:
            continue
        if (word.rstrip("s") or word) in keys:
            return True
    return False


def _shares_a_word(item, subject):
    """True when the entry is keyed on a word of the subject: "save money" is about saving."""
    keys = _key_words(item)
    for word in subject.lower().split():
        word = word.strip(".,!?;:")
        if len(word) > 2 and (word.rstrip("s") or word) in keys:
            return True
    return False


# A line that asks for a figure is answered by a figure, and an entry that holds none answers a
# different question: "how much roughly to fix" after a brake that clicks reached the entry about
# the noise itself, whose answer says what to listen for and no price at all.
FIGURE_ASKS = ("money", "amount", "time", "clock", "heat", "distance", "pressure")


def _answers_the_figure(text, reply):
    """False when the line asks for a figure and the entry's answer names none of that kind.

    Only an answer that holds no figure is turned away: one that states a figure in any of the
    shapes a person writes it (£80 to £200, "20 to 30 minutes", "a couple of minutes")
    is answering the line. An entry that answers a step or a reason is asked for one, so it
    never comes here. A reply chosen later from a callable cannot be read, and is left alone.
    """
    if not isinstance(reply, str) or not reply.strip():
        return True
    kind = asked_kind(text)
    if kind not in FIGURE_ASKS:
        return True
    wanted = {kind}
    if kind in ("amount", "money"):
        # A sum of money answers "how much" whether the line asks a price or a quantity, and
        # it is written in the money shape ("£80 to £200") rather than the amount one.
        wanted.add("money")
    for one in wanted:
        pattern = SIGNALS.get(one)
        if pattern is not None and pattern.search(reply):
            return True
    return False


def _asks_how_to_say_it(text):
    """Whether the line asks how to say something rather than what the thing is."""
    return bool(SAY_IT.search(text or ""))


def _in_the_subjects_field(item, subject):
    """Whether the entry is in the same field as the thing the subject names, or has no field."""
    field = (understand(subject) if subject else {}).get("topic")
    if not field:
        return True  # nothing to go on, so nothing to rule out
    return getattr(item, "domain", None) == field


def _own_thing_words(text, memory):
    """The words in the line that name a thing of its own, not the ask or the subject on screen.

    A question is not a follow-up just because it is a question: "how much is a tv licence" after
    "what is a credit score" was read as one that had left its subject out, the credit score was
    hung on the end of it, and "how much" is a property the credit entry knows - so the licence
    question came back as the credit report, and so did a driving licence and a tip. The words
    that make it a question (how, much, should) are not the thing asked about; "tv" and "licence"
    are. A line that brings no such word ("and how much is that", "how long does it take") really
    has left its subject out and keeps the follow-up.
    """
    understood = understand(text, memory)
    subject = str(mem.subject(memory) or "").lower()
    out = []
    for word in understood.get("keywords") or []:
        low = str(word).lower()
        if low in _ASKING_ONLY or low in subject or low.isdigit() or len(low) < 3:
            continue
        out.append(low)
    return tuple(out)


def _agrees_with_its_own_field(item, reading):
    """True when the entry is in the field the line itself is read as, or in no field at all.

    An entry that carries no topic cannot disagree with the line, and the entry the line's own
    words reach is the entry for it.
    """
    if getattr(item, "topic", None) is None:
        return True
    return about_the_topic(item, reading)


def _the_field_on_the_screen(item, text, reading, memory):
    """True when the line says the entry's own subject and the entry is from the field on screen.

    The field of the answer is a fact about the talk; the topic the line is read as is a guess
    from its words, and one word can carry it into another field: "im skint this month" / "i get
    paid on friday" / "what should i cut first" was read as a question about a body because
    "cut" is a body word, so the money row that answers it was stood down as a field this talk
    never touched and the person got a shrug for the step their own conversation had set up.

    The line has to say one of the entry's own subject phrases, which is what keeps this from
    lifting an entry in over the answer the line really asks for: after "my son is being
    bullied", "how do i help with homework without fighting" says "cut first" to no card and
    keeps the homework answer, while a family card that only shares the single word "fight" with
    it is not the thing the line names.
    """
    if not isinstance(reading, dict) or reading.get("kind") != "question":
        # A statement is not a request for a card: it says where the person stands, and the
        # readers that answer a report are the ones that should take it.
        return False
    last = memory.get("last_answer") if isinstance(memory, dict) else None
    domain = str(last.get("domain") or "") if isinstance(last, dict) else ""
    if not domain or domain != str(getattr(item, "domain", "") or ""):
        return False
    if _last_turn_answered_from_the_field(memory):
        # The turn before this one already gave the field's answer, so the field is on the screen
        # and a question about it is a question about the answer they have: "is 2 hours enough
        # between connecting flights at heathrow" / "no checked bag" is answered by the connection
        # rule with the bag folded in, and the baggage card is a different question.
        return False
    return _says_a_subject_phrase(item, text)


def _last_turn_answered_from_the_field(memory):
    """True when the turn before this one was the field's answer rather than an acknowledgement.

    "im skint this month" / "i get paid on friday" / "what should i cut first" is a chat where the
    middle line only said a detail ("Got it - you get paid on friday"), and the follow-up is the
    field's own question. The connection chat is the other shape: the middle turn *was* the
    answer, so the person is adding to what they were told.
    """
    if not isinstance(memory, dict):
        return False
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return False
    last = memory.get("last_answer")
    reply = last.get("reply") if isinstance(last, dict) else last
    said = turns[-1].get("bot") if isinstance(turns[-1], dict) else None
    if not isinstance(reply, str) or not isinstance(said, str):
        return False
    return _same_answer(reply, said)


def _says_a_subject_phrase(item, text):
    """True when the line says a subject of the entry in so many words, two words or more.

    The first key part of an entry is its subject, and a phrase of it that the person wrote
    ("cut first", "where can i save") is not a pairing two unrelated lines share by accident. A
    single word is, which is why one is not enough here.
    """
    key = getattr(item, "key", ()) or ()
    if not key:
        return False
    first = key[0]
    said = " " + " ".join(re.findall(r"[a-z0-9']+", str(text or "").lower())) + " "
    for option in (first if not isinstance(first, str) else (first,)):
        phrase = " ".join(str(option).lower().split())
        if " " in phrase and (" " + phrase + " ") in said:
            return True
    return False


def _names_the_entry(text, item):
    """True when the line names the thing this entry is about, with a determiner in front of it.

    The entry's own subject words are the test, not the asks in the rest of its key
    ("worth", "get", "buy"): a person saying "a smart meter" has named the meter, and the
    entry is about the meter. This is what tells a real new subject from a word that only sits
    inside another one: the puppy talk's "house trained" names no house, so the first-home
    entry still stands down, and the washing machine talk's "a smart meter" does name one, so
    the meter's entry answers instead of "that's your call, not mine".
    """
    first = getattr(item, "key", ()) or ()
    things = first[0] if first and not isinstance(first[0], str) else ()
    heads = set()
    for option in things:
        words = str(option).lower().split()
        if words:
            heads.add(words[-1].rstrip("s") or words[-1])
    if not heads:
        return False
    for found in NAMING.finditer(" ".join(str(text or "").lower().split())):
        for word in re.findall(r"[a-z-]+", found.group(1)):
            if word.rstrip("s") in heads:
                return True
    said = " ".join(str(text or "").lower().split())
    mine = said.split()
    for _ in range(2):
        if mine and mine[0] in OPENS_WITH_AN_AUXILIARY:
            mine = mine[1:]
    for word in re.findall(r"[a-z-]+", " ".join(mine[:2])):
        if word.rstrip("s") in heads:
            return True
    return False


# How far into a line the word being explained can sit. "what is inflation" and "explain a
# dividend" put it first or second, and the far end is an ask with the longer lead-in ("what does
# a tracker mortgage actually mean"); a word deep in a line about something else is a mention.
DEFINITION_WORD_AT = 6


def _a_definition_of_the_entry(text, item):
    """True when the line asks what one of the entry's own words means ("what is inflation").

    A request to explain a word names that word as plainly as "a smart meter" names the meter,
    but it carries no determiner in front of it, so `_names_the_entry` does not see it and the
    line was read as a follow-up that names nothing of its own. After any other turn the talk's
    subject then stood the entry down - "my back hurts after sitting all day" then "what is
    inflation" got the search hedge, "who invented the telephone" then "what is apr" too - and
    the same line answered in one conversation and punted in another, which is the shape of
    mistake STYLE.md calls out. The question is a new subject, so it is that entry's question
    whatever the talk before it was on.

    The words in front of the subject have to be the ask itself ("what", "whats", "explain",
    "the meaning of"), which keeps "what is the best way to clean a sofa" off the sofa row:
    "best", "way" and "clean" are not words of a request to explain a sofa.
    """
    words = [word.strip(".,!?;:") for word in
             (" ".join(str(text or "").lower().split())).split()]
    if not words or len(words) > DEFINITION_WORD_AT + 1:
        return False
    first = getattr(item, "key", ()) or ()
    things = first[0] if first and not isinstance(first[0], str) else ()
    subject = set()
    for option in things:
        for word in str(option).lower().split():
            subject.add(word.rstrip("s") or word)
    if not subject:
        return False
    for at, word in enumerate(words):
        if (word.rstrip("s") or word) not in subject:
            continue
        before = words[:at]
        if not before or not any(one in EXPLAIN_LEADS for one in before):
            continue
        if all(one in EXPLAIN_FILLER for one in before):
            return True
    return False


def _says_the_ask_whole(text, item):
    """True when the line is nothing but one of the entry's own key phrases.

    The phrases are the entry's own wording, so a line that is exactly one of them is asking for
    this thing and cannot be a detail of whatever the chat was on before. Only phrases of two
    words or more count: a single key word is the loose match `_about_the_talk` is there to
    distrust (a puppy's "house trained" holds "house").
    """
    said = [word for word in WORD.findall(str(text or "").lower())
            if word not in HANDOVER_FILLER]
    if len(said) < 2:
        return False
    for part in getattr(item, "key", ()) or ():
        options = (part,) if isinstance(part, str) else part
        for option in options:
            phrase = [word for word in WORD.findall(str(option).lower())
                      if word not in HANDOVER_FILLER]
            if len(phrase) >= 2 and phrase == said:
                return True
    return False


def _a_why_line_that_names(item, reading):
    """True when a why-line names the subject of the entry it reached."""
    if not isinstance(reading, dict) or "why" not in (reading.get("asks") or ()):
        return False
    return names_its_own_subject(item, reading)


def _a_choice_with_one_thing_left_out(text):
    """True when the line narrows a choice ("i dont want a scary film", "i hate horror books")."""
    flat_words = set(re.findall(r"[a-z']+", " ".join(str(text or "").split()).lower()))
    if not flat_words & CHOICE_KINDS:
        return False
    return bool(_refused(text))


# The endings an adjective has and a thing does not: "is that dangerous", "is it fixable", "is
# that expensive". A word that ends this way describes the thing in the talk rather than naming
# another one, so it is no reason to drop the last subject.
_ADJECTIVE_ENDINGS = ("ous", "ful", "less", "able", "ible", "ive", "ish", "ary")


def _describes_the_thing(word):
    """True when the word describes a thing rather than naming one."""
    if word in NO_THING_NAMED:
        return True
    return any(word.endswith(ending) and len(word) > len(ending) + 2
               for ending in _ADJECTIVE_ENDINGS)


def _said_in_the_talk(memory):
    """The words of the last few turns, the bot's own included."""
    said = set()
    for turn in (memory or {}).get("turns") or []:
        if not isinstance(turn, dict):
            continue
        for side in ("user", "bot"):
            said.update(WORD.findall(str(turn.get(side) or "").lower()))
    return said


def _already_in_the_talk(word, said):
    """True when the word, its plural or a longer form of it has been said in the talk."""
    if not said:
        return False
    if word in said or word + "s" in said:
        return True
    if word.endswith("s") and word[:-1] in said:
        return True
    return any(one.startswith(word) for one in said)


def _names_its_own_thing(text, memory=None):
    """True when the line names a thing for itself rather than only what to do with the subject.

    "is it worth fixing" is the subject's own question and the rewrite answers it; "is it worth
    fixing my old laptop" names the laptop, so the last subject is not put back into it. A thing
    the talk has already named is not a new subject: after "the washing machine smells" the
    drawer it was answered about is part of the same machine, so "i think its the drawer" is
    still answered about the machine and not as a question about drawers in general.
    """
    said = _said_in_the_talk(memory) if memory is not None else set()
    if ASKS_A_QUANTITY.search(str(text or "")):
        return False
    words = re.findall(r"[a-z0-9']+", str(text or "").lower())
    for index, word in enumerate(words):
        if re.fullmatch(r"\d+(?:s|st|nd|rd|th)?", word):
            continue  # an age or a count is a quality, not a new thing
        if word in DESCRIBES_ONE or word in kinds.VERB_FORMS or word in _AUXILIARY:
            continue
        if word.endswith("e") and word[:-1] + "ing" in DESCRIBES_ONE:
            continue
        if _describes_the_thing(word):
            continue  # a quality or an amount in front of a determiner names no new thing
        if any(word in ("one", "ones") for word in words[index + 1:index + 3]):
            # "a decent one", "a really big one": the word stands in for the thing already in
            # the talk rather than naming a new one, so the last subject is still what it means.
            continue
        if _already_in_the_talk(word, said):
            continue  # a thing this talk has named is not a new subject
        before = words[max(0, index - 2):index]
        if before[-1:] and before[-1] in THING_AFTER:
            if len(before) == 2 and before[0] in AFTER_A_PLACE:
                continue  # "in the pool", "on the plane": where the subject goes, not a new thing
            return True
        # The determiner is the word before the thing ("a heat pump"), or the one before an
        # adjective ("my old laptop", "a proper coat"). The word in the middle has to be an
        # adjective: in "a lot for a new one" the middle is "lot", and "for" is not a thing.
        if (len(before) == 2 and before[0] in THING_AFTER
                and before[1] not in THING_AFTER
                and before[1] not in _AUXILIARY
                and not _describes_the_thing(before[1])):
            return True
    return False


def _the_topic_rules_it_out(item, memory):
    """True when the topic's own words are on the entry's avoid list.

    The knowledge base says which lines an entry is not about, and the topic is a line the
    person said. An entry that stands down for it cannot be the answer to a follow-up that has
    no subject of its own: nothing but the topic could have named it.
    """
    topic = mem.topics.topic_text(memory) if isinstance(memory, dict) else ""
    if not topic:
        return False
    return bool(mem.topics.keeps_away(topic, topic, item))


def _from_rewrite(fuller, text, memory, reject, added="", domain=None):
    """The entry a rewritten line reaches, when it is about the last subject and is not a repeat.

    `added` is the word the rewrite put in ("film"): an entry can be about the thing the chat is
    choosing between without carrying the subject's own word, so either one makes it the entry.
    """
    item = find(understand(fuller, memory), reject=reject)
    if item is None:
        return None
    if domain is not None and item.domain != domain:
        return None  # the word reached an entry in another field: not the thing being chosen
    if not (_is_about(item, mem.subject(memory)) or (added and _is_about(item, added))):
        return None
    own = _own_thing(understand(text, memory))
    if own and not _is_about(item, own):
        return None  # the line names its own thing: it is not about the last subject
    reply = item.reply
    if isinstance(reply, (list, tuple)) or callable(reply):
        return item  # the phrasing is chosen later; a repeated answer is caught below
    if _said_before(reply, memory):
        return None  # the same answer again is no answer
    return item


# Advice to keep something out of the fridge is for a raw food in a cupboard, never for a dish
# that has just been cooked.
_NOT_THE_FRIDGE = re.compile(
    r"\b(?:never\s+(?:in\s+)?the\s+fridge|not\s+(?:in\s+)?the\s+fridge|out\s+of\s+the\s+fridge"
    r"|room\s+temperature|dry,\s+dark|in\s+a\s+cupboard|in\s+the\s+cupboard)\b", re.I)


# A line that asks how to store or keep a food is a keeping answer in itself, so the follow-up
# "how long does that keep" asks for that same fact again, not for the general fridge table.
# Only the doing word the subject came from can say so: "how do i store bread" leaves "store
# bread", where "how long do i boil an egg" leaves no storing word at all.
STORING = frozenset("""
store stores stored storing keep keeps kept keeping
""".split())


def _asks_storing(memory):
    """True when the line before was a how-to-store (or how-to-keep-fresh) question."""
    words = (mem.subject(memory) or "").split()
    return bool(words) and words[0] in STORING


# The storing word a how-to line leaves in the subject is not part of the thing: "how do i keep
# herbs fresh" leaves the subject "keep herb fresh", so the keeping rewording read "how long does
# that keep" as already naming its subject and the follow-up got nothing. The herb is the thing.
# Only a storing word comes off: "how do i cook rice" has to keep its "cook", because cooked rice
# keeps a day and dry rice keeps months, and the cooking is what tells them apart.
def _keeping_thing(memory):
    """The thing a keeping follow-up is about, without the storing word the how-to line asked with."""
    words = (mem.subject(memory) or "").split()
    while words and (words[0] in STORING or words[0].rstrip("s") in STORING):
        words.pop(0)
    return " ".join(words)


def _the_plan_keeps(understood, memory):
    """The keeping fact a dish the conversation planned says for itself: "it keeps 3 days".

    "im making a beef stew" then "how long will it keep" is a question about that stew, and the
    plan has its own answer for it. The general cooked-food line is the answer for a dish nobody
    named, and a worse one for a dish we can name.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    words = {str(word).lower() for word in (understood.get("words") or ())}
    if dishes.ask_kind(understood) != "keep" or not words & {"it", "that", "this", "them", "they"}:
        return None
    if _own_thing(understood):
        return None  # the line names a food of its own, and that food has its own answer
    return dishes.follow_up(memory, understood)


def _in_this_conversation(reject, reading):
    """The caller's veto, and one of its own: a fact from another part of the knowledge base.

    A bare ask leans on the words of the line before it, and one of those words sits in other
    domains too: "my kids wont listen to me" and then "what can i do" reached the music entry
    off the word "listen", and the parent was offered an album. A fact the conversation never
    touched is passed over, so the search goes on to the domain it is actually about.
    """
    def veto(item):
        if not about_the_topic(item, reading):
            return True
        return bool(reject is not None and reject(item))
    return veto


def _in_bare_context(text, memory, reject=None):
    """The entry a bare ask reaches once the thing it is about is put on the end of it.

    Kept apart from `_in_context` because it hands back the reading of the written-out line:
    the entry phrases itself from that reading ("In Rome: the Colosseum ..." needs the city in
    the line), where the pronoun and property rewrites are read from the line as it came in.
    """
    if _names_its_own_thing(text, memory):
        return None
    fuller = _with_bare_subject(text, memory)
    if fuller.strip() == text.strip():
        return None
    reading = understand(fuller, memory)
    item = find(reading, reject=_in_this_conversation(reject, reading))
    if item is None or not _is_about(item, mem.subject(memory)):
        return None
    reply = getattr(item, "reply", None)
    if not (isinstance(reply, (list, tuple)) or callable(reply)):
        if _said_before(reply, memory):
            return None  # the same answer again is no answer
    return item, reading


def _reply_of(item, reading, memory):
    """What this entry would say, without keeping it, so a reply can be read before it is given."""
    reply = getattr(item, "reply", None)
    if callable(reply):
        try:
            reply = reply(memory, reading)
        except Exception:
            return ""
    elif isinstance(reply, (list, tuple)):
        reply = " ".join(one for one in reply if isinstance(one, str))
    return reply if isinstance(reply, str) else ""


A_FIGURE = re.compile(r"\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b",
                      re.I)


NUMBER_IN_TEXT = re.compile(r"\d+(?:\.\d+)?")


def _figures_of(said):
    """The numbers a sentence carries, as words a set can hold."""
    return set(NUMBER_IN_TEXT.findall(flat(said or "")))


def _new_figure(fresh, before):
    """Whether the answer has a figure the one before it did not.

    A line that adds a figure to the answer just given is worth a second answer only when the
    figure changes it: the figure they gave that was already the one used ("its 2 kilos" after
    the timing for a 2kg bird) leaves the paragraph saying what it already said.
    """
    return bool(_figures_of(fresh) - _figures_of(before))


def _adds_a_figure(text):
    """Whether the line brings a number for the thing under discussion, and asks nothing.

    A number on its own is not a line: "it says 1.8 kilos", "the gauge says 0.5", "we are six".
    An ask with a number in it ("how long for 2 kilos") is read for an entry as usual.
    """
    said = flat(text)
    if not said or "?" in said:
        return False
    return bool(A_FIGURE.search(said))


# A line that changes a figure the chat already has, rather than one that adds a figure to it: the
# sum on it replaces the sum before it, so the two are never the same question ("what if i can only
# do 100" adds a rate, "make it 150 instead" moves one).
A_PUT_RIGHT = re.compile(r"\b(?:make\s+(?:it|that|them)|instead|rather\s+than|i\s+meant|no\s+wait|"
                         r"change\s+(?:it|that|them)|put\s+(?:it|that)\s+(?:to|up|down)|"
                         r"bump\s+(?:it|that)|let'?s\s+say)\b", re.I)


def _a_figure_put_right(text):
    """True when the line moves a figure the chat already gave ("make it 150 instead")."""
    text = str(text or "")
    return bool(A_PUT_RIGHT.search(text) and re.search(r"\d", text))


def _without_the_figures(line):
    """The earlier line with its sums taken out, so only its words are handed on."""
    return " ".join(re.sub(r"[£$]?\b\d[\d,.]*\b", "", str(line or "")).split())


def _the_entry_asked_again(text, memory):
    """The entry that answered last, asked this line with its own subject still in it.

    A line that only asks for a property ("how long will that take", "what temperature?") names
    nothing of its own, so the entry is the one the last answer came from - but the entry cannot
    see the ask when the subject is missing from the line ("how long will that take" carries no
    word of a credit card). Read with the line it leans on in front, the entry answers the ask
    it has an answer for, and when it has nothing to add it says the same answer again: that is
    not a new reply, so this returns None and the rest of the module goes on as before.
    """
    record = _last_answer(memory)
    if not record:
        return None
    entry_id = record.get("id")
    if not entry_id:
        return None
    item = None
    for candidate in all_entries():
        if getattr(candidate, "id", None) == entry_id:
            item = candidate
            break
    if item is None:
        return None
    turns = memory.get("turns")
    turn = record.get("turn")
    if not isinstance(turns, list) or not isinstance(turn, int) or not 0 <= turn < len(turns):
        return None
    said = turns[turn] if isinstance(turns[turn], dict) else {}
    line = str(said.get("user") or "").strip()
    if not line:
        return None
    # The earlier line is put in front so the entry can see what the ask is about ("how long will
    # that take" carries no word of a credit card). A figure the line puts right is the one thing
    # that must not come with it: read with the rate from two turns back in front of it the entry
    # answered with both - "£2,500 at £200 a month" / "make it 150 instead" -> "£150 at £200 a
    # month is a single month at that rate", a pot nobody named made out of the rate they were
    # changing. The words still go in front, so "the car is" is still what the sum is for.
    earlier = _without_the_figures(line) if _a_figure_put_right(text) else line
    reading = understand(earlier + " " + text, memory)
    fresh = _payload(item, memory, reading)
    if not isinstance(fresh, str) or not fresh.strip():
        return None
    if flat(fresh) == flat(record.get("reply") or ""):
        return None  # the same answer again is not an answer to this line
    new_part = _the_part_a_longer_variant_adds(fresh, record.get("reply"))
    if new_part is not None:
        return new_part
    return fresh


def _the_part_a_longer_variant_adds(fresh, said):
    """What a longer variant of the answer on the screen adds to it, or None.

    The entry asked again with the line it answered still in front of it can pick a longer
    variant, and the paragraph the person has just read goes out again with a sentence stuck on
    the end: "how far should i go first" then "and how often" in a running chat came back as the
    whole training-order paragraph plus "The best order is the one you will keep doing twice a
    week." The answer is on the screen, so only the added sentences are owed here - STYLE.md
    rules out the same words twice in a row, and a friend asked a second question about the same
    answer says the part that answers it.
    """
    said = flat(said)
    mine = flat(fresh)
    if not said or not mine.startswith(said):
        return None
    rest = mine[len(said):]
    if not rest.startswith(" "):
        return None  # a word the flat form cuts in half is not the answer said again
    words = len(said.split())
    added = " ".join(str(fresh).split()[words:]).strip()
    if len(added.split()) < 3:
        return None  # a word or two on the end is the same answer, not a new part of it
    return added


def _payload(item, memory, reading):
    """The entry's reply, chosen the way the composer will choose it, or "" if it declines."""
    reply = getattr(item, "reply", None)
    if callable(reply):
        reply = reply(memory, reading)
    elif isinstance(reply, (list, tuple)):
        reply = pick(reply, memory)
    return reply if isinstance(reply, str) else ""


def _the_sentence_owed(text, reply, memory):
    """The sentence the entry behind this reply owes the line, or None when it owes none.

    The entry is the one the line's own reading reaches, and the reply has to open on that
    entry's own words: a card narrowed to one of its sentences ("Do not stop suddenly on your
    own: ..."), a card wrapped as the answer already given ("Same answer, and it covers this:
    ..."), and a reply from another row are all left as they are, because the sentence the row
    owes belongs in front of the card it belongs to.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return None
    try:
        item = find(understood)
    except Exception:  # noqa: BLE001 - a sentence is never worth a turn
        return None
    if item is None or not getattr(item, "lead", None):
        return None
    said = getattr(item, "reply", None)
    if not isinstance(said, str):
        try:
            said = _payload(item, memory, understood)
        except Exception:  # noqa: BLE001
            return None
    plain = " ".join(str(said or "").split())
    here = " ".join(str(reply or "").split())
    if not plain or not here:
        return None
    at = here.find(plain[:50])
    if at != 0:
        # the card is not what this reply says: it has been narrowed to one of its sentences, or
        # wrapped as the answer already given ("Same as before: ...", "As I said: ..."), or the
        # reply is another row's altogether. Only a reply that opens on the card gets its verdict,
        # because the sentence a row owes belongs in front of the card and not in front of a frame
        # around it: "It is not an emergency. As I said: A suddenly louder exhaust ..." answers a
        # line the person asked before with a verdict they have already been given.
        return None
    return item.lead


# A line that asks for a stand-in wants the missing thing named back: "no double cream, what can
# i use" is answered in cream's own terms ("milk with a knob of butter ... thickens much like
# cream"), and an answer that says cream is the answer, not a confident recipe about the thing
# that is not in the house. The refusal check below is for a preference ("anything but a
# horror"), so a swap line is never asked to leave the word out - and a swap line that says "no
# double cream" is read as refusing "double", the modifier, which no answer is about at all.
STAND_IN_WORDS = frozenset("""
substitute substitutes substitution swap swaps swapping replace replaces replacing replacement
""".split())


# Only the shapes that ask for a stand-in in those words: "i ran out of butter" and "i havent
# got any milk" already read as a swap and never reach the refusal check at all, so a "no double
# cream" line is the only one that needs this gate to open.
STAND_IN_PHRASES = ("what can i use", "what do i use", "what should i use", "what else can i use",
                    "what can i substitute", "in place of",
                    # The short way of asking, after a taste rather than a shortage: "i hate
                    # broccoli what can i have instead" was neither a stand-in nor a refusal the
                    # code knew, so the swap row for broccoli was handed back and the line got a
                    # search hedge.
                    "instead", "what can i have", "what could i have", "what else can i have",
                    # The other way of asking it, which needs no stand-in at all: "i dont like
                    # garlic can i leave it out" is the same swap question, and the swap row's
                    # "leave it out - nothing collapses" was handed back as a refusal answer.
                    "leave it out", "leave them out", "leave out", "skip it")


# A line that names what it wants a stand-in for is answered by that name and nothing else:
# "anything but cream, what can i use instead of milk" rules cream out and asks about milk, so
# the cream entry must keep out of it. Only the bare "no <thing>" opening, asking what to use in
# its place, is the shape where the missing thing is the subject of the line.
STAND_IN_TARGET = re.compile(r"\b(?:instead of|in place of|substitute for|swap (?:it )?for)\b",
                             re.I)


def _wants_a_stand_in(reading):
    """True when the line asks what to use in place of the thing it says it has none of."""
    if not isinstance(reading, dict):
        return False
    clean = " ".join(str(reading.get("clean") or "").split()).lower()
    if not clean or STAND_IN_TARGET.search(clean):
        return False
    asked = any(phrase in clean for phrase in STAND_IN_PHRASES)
    if not asked:
        words = reading.get("words")
        if not isinstance(words, (list, tuple)):
            words = clean.split()
        asked = any(str(word).lower() in STAND_IN_WORDS for word in words)
    if not asked:
        return False
    # "no double cream, what can i use" - the refusal is the line's own subject, so the entry
    # that says the thing back is the answer. "anything but cream" still goes through the check.
    #
    # A taste opens the line the same way a lack does: "i hate broccoli what can i have instead"
    # is the swap question put by someone who will not eat the food rather than by someone who
    # has run out of it, and the swap row that answers it was being handed back because the
    # refusal check only knew the shape a missing ingredient has.
    return bool(REFUSE_OPEN.match(clean) or REFUSE_WISH.match(clean)) \
        and not REFUSE_CHOICE.match(clean)


def _a_swap_row(item):
    """True for the table's stand-in rows, whose answer is the swapped ingredient by design.

    The gate above belongs to them and to nothing else: "no alcohol what can i drink instead"
    has the shape of a swap and is a question about alcohol, so the row that says alcohol back
    - the sleep one - has to keep its refusal. A row without the prefix simply keeps the check,
    which costs a stand-in at worst and never a confident answer about something else.
    """
    return str(getattr(item, "id", "") or "").startswith("swap-")


# --- a present with a price on it ----------------------------------------------------
# A gift question that names an amount and the same question without one are two questions: "what
# should i get my dad for his 60th, under 40 quid" has to come back with things that cost that
# much. So does the limit given as a follow-up ("what about under 40 quid", "anything cheaper"),
# which names no present word at all and used to reach the shrug. The picks themselves are data in
# shopping.py (INTEREST_GIFTS, PRESENT_BANDS), so this only reads the limit and the person.
PRICE_LIMIT = re.compile(
    r"\b(?:under|below|less than|no more than|not more than|up to|max(?:imum)?(?: of)?|"
    r"budget(?: of| is| around| about)?|spend(?: up to)?)\s*\u00a3?\s*(\d{1,4})(?:\.\d\d?)?\b",
    re.IGNORECASE)


# "nothing over 20 quid", "not over a tenner", "no more than 15 pounds": the ceiling said as a
# thing the present must not go above. Without it the amount is read ("20 quid") and the rest of the
# line is left over, so the limit is never applied and the person gets the whole price range again.
PRICE_NOT_OVER = re.compile(
    r"\b(?:nothing|not|no|nowt)\s+(?:more\s+than|over|above|past)\s*\u00a3?\s*(\d{1,4})(?:\.\d\d?)?\b",
    re.IGNORECASE)


PRICE_BARE = re.compile(r"\b(\d{1,4})(?:\.\d\d?)?\s*(?:pounds?|quid|\u00a3)\b",
                        re.IGNORECASE)


# "over 20 quid then" is the floor side of the same words, and it is not a ceiling: with `over` in
# `LIMIT_ONLY` the line reads as a limit of its own, and `PRICE_BARE` then turns "over 20 quid"
# into a ceiling of 20. The words only say a limit when nothing else in the line says which way
# the limit goes, so a floor with no negation in front of it and no "under"/"up to" beside it
# stands the reading down.
PRICE_OVER = re.compile(r"\b(?:over|above|more\s+than|past)\s*\u00a3?\s*(\d{1,4})(?:\.\d\d?)?\b",
                        re.IGNORECASE)


PRICE_WORDS = (("a tenner", 10), ("tenner", 10), ("a fiver", 5), ("fiver", 5))


CHEAPER = re.compile(r"\b(?:cheaper|more affordable|less expensive)\b", re.IGNORECASE)


# The cheapest test for "this line may hold a limit": a digit, a tenner or a fiver, or a word for
# cheaper. Every line that reaches the reader above has to pass it, so it stays a plain search.
LIMIT_SHAPE = re.compile(r"\d|\btenner\b|\bfiver\b|\bcheaper\b|affordable", re.IGNORECASE)


# What a line that *only* sets a limit is made of: the ask and the limit, nothing else. Anything
# the line names for itself (a dad, a wedding, a book) takes it out of this shape.
LIMIT_ONLY = frozenset("""
    nothing not no over above more than nowt
    what about anything something cheaper cheap please then so ok okay could we go bit a an the is
    my budget max maximum under below less than more no not up to spend pounds pound quid tenner
    fiver that this it for on do i can you any if but else maybe just around roughly sort kind of
    thing things price prices cost costs money how much will would should get buy gets go for
    """.split())


# The same interest said two ways: "garden" and "gardening" are one row of the table, and a line
# that says both does not ask for two presents.
INTEREST_ALIASES = {"garden": "gardening", "plants": "gardening", "allotment": "gardening",
                    "tackle": "fishing", "angling": "fishing", "fish": "fishing",
                    "books": "reading", "book": "reading"}


def _price_limit(text):
    """(the amount in pounds or None, whether the line asked for something cheaper)."""
    if not isinstance(text, str) or not text.strip():
        return None, False
    flat = " ".join(text.lower().split())
    cheaper = bool(CHEAPER.search(flat))
    if (PRICE_OVER.search(flat) and not PRICE_NOT_OVER.search(flat)
            and not PRICE_LIMIT.search(flat)):
        # The line says a floor and nothing that makes it a ceiling: "over 20 quid then" is a
        # present above 20 pounds, not a budget of 20.
        return None, cheaper
    match = PRICE_NOT_OVER.search(flat) or PRICE_LIMIT.search(flat) or PRICE_BARE.search(flat)
    if match:
        try:
            return int(float(match.group(1))), cheaper
        except (TypeError, ValueError):
            return None, cheaper
    for phrase, amount in PRICE_WORDS:
        if phrase in flat:
            return amount, cheaper
    return None, cheaper


# A line with a price on it is a present question when it says so, or when it is a limit on a
# present already being discussed. "my budget is 30 pounds" on its own says neither and is money.
GIFT_WORD = re.compile(r"\b(?:present|presents|gift|gifts)\b")


def _only_a_limit(text):
    """True when the line is the limit and nothing else: "what about under 40 quid"."""
    words = [word for word in WORD.findall(" ".join(str(text or "").lower().split()))
             if not word.isdigit()]
    return bool(words) and all(word in LIMIT_ONLY for word in words)


def _a_gift_entry(reading):
    """The present entry this line is about, if it is about one."""
    item = find(reading)
    return item if str(getattr(item, "id", "")).startswith("gift-") else None


def _a_gift_just_answered(memory):
    """The present entry one of the last few lines reached, while the chat is still on it."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return None
    for turn in reversed(turns[-3:]):
        said = str((turn or {}).get("user") or "") if isinstance(turn, dict) else ""
        if not said:
            continue
        item = _a_gift_entry(understand(said, memory))
        if item is not None:
            return item
    return None


def _asks_what_to_give(reading):
    """True when the line is asking what to give somebody, with a person to give it to.

    The same reading the gift rows ask before they answer (topics.gift_ask), so one rule decides
    for the rows and for the band: "get her" and "what should i buy my husband" are presents,
    "cheap running shoes under 40 pounds" and "get him tested" are not.
    """
    from ..understanding import topics as present_reading
    return present_reading.gift_ask(reading)


def _the_interests(text, memory, item):
    """The hobbies this present is for, as the table names them: said in the chat, or in the key.

    "he likes fishing and gardening" a turn before the limit is what makes "what about under 40
    quid" a question about a fisherman, so the words are read off the last few lines as well as
    off this one, and off the entry's own key when the line named the hobby in the first place.
    """
    from ..knowledge import shopping  # a local import: the module's own import line is shared
    said = []
    lines = []
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if isinstance(turns, list):
        lines = [str((turn or {}).get("user") or "") for turn in turns[-3:]
                 if isinstance(turn, dict)]
    for line in lines + [str(text or "")]:
        for word in WORD.findall(line.lower()):
            name = INTEREST_ALIASES.get(word, word)
            if name in shopping.INTEREST_GIFTS and name not in said:
                said.append(name)
    if said:
        return said
    for part in getattr(item, "key", ()) or ():
        for word in (part if isinstance(part, (list, tuple, set)) else (part,)):
            name = INTEREST_ALIASES.get(str(word).lower(), str(word).lower())
            if name in shopping.INTEREST_GIFTS and name not in said:
                said.append(name)
    return said
