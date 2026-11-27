"""Part 9 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re

from .. import memory as mem
from ..compose import lead
from ..compose import fit as shapes
from ..compose.repair import amends_to
from ..compose import trouble as trouble_reading
from ..knowledge import cooking, dishes, entertainment, freshness, shopping
from ..knowledge.lookup import (
    about_the_chat, about_the_topic, find, leans_on_a_subject, names_nothing_of_its_own,
)
from ..knowledge.lookup import entry as lookup_entry
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import ack, named, narrow as length, onset, repeat, taste
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..knowledge.maths import solve
from ..understanding.kinds import SUMMONS_WHO
from ..memory import baking, trips
from ..memory import repeat
from ..memory import outfit
from ..memory import (followup_reading, keywords, recall, remember_answer, resize,
                     same_as_before, the_ask_about_the_thing_it_points_at)
from ..memory import again as same_again  # the short of an answer already on the screen
from ..memory.again import AGAIN_HELP
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory import repeat
from ..memory import topics as said_topic
from ..memory.topics import AMOUNT, pairing
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import repeat, tried, returned
from ..memory import limit
from ..memory import (
    followup_reading, keywords, remember_answer, resize, same_as_before, swap,
    the_thing_a_detail_belongs_to,
)
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory import repeat
from ..memory.narrow import RATE, SIGNALS, asks_a_part, flat, kind_of as asked_kind, narrow
from ..understanding import understand
from .answers_part_01 import (
    ABOUT_YOU, REFERRING, _said_before, SENTENCE, _flat, GENERIC_KEEPING, AGAIN, _carries,
    _in_short, _answer_said, _asks_of_another_subject, _opening, _the_new_part, _the_outcome_owed,
)
from .answers_part_02 import (
    _answers_a_length, _the_article, _about_subject, _key_words, _head_thing, _own_thing,
    _qualifier_rewrites, _refused, _subject_tails, _says_it_leaves_it_out, PLAN_RECALL, RECALL,
    SOMETHING_FOR_GIVEN_TO, WHEN_AM_I, _already_said, _asks_who_the_bot_is, _keeps_a_plan,
    _keyed_on_the_person, _new_thing, _off_the_topic, _only_a_size_of, _something_for,
    _the_run_said,
)
from .answers_part_03 import (
    _is_about, _last_answer, _the_figure_they_meant, _hands_back_the_refusal, _remember_answer,
    ASKING, ASKING_VERBS, BARE_GENERIC, CHOICE_ASK, PROPERTY_WORDS, _a_property_word_names_a_thing,
    _from_another_domain, _leans_on, _only_a_property, _the_dish_time, _the_one_to_pick,
)
from .answers_part_04 import (
    SIZE_REPLACED, _part_not_repeated, _with_the_thing, ADDING_TO_THE_SUBJECT, _left_out, _named_by,
    _the_answer_was_about_the_subject, _with_bare_subject, FIGURE, KEEPS, _minutes_in,
    A_MEASURE_OF_THE_SUBJECT, _asked_figure, _care_holds, _names_a_property,
    _the_amount_they_named_again, _the_figure, _the_machine_follow_up, _the_person_to_call,
    _the_sentence_about, _the_things_to_try,
)
from .answers_part_05 import (
    _payload, _answers_the_figure, _asks_how_to_say_it, _from_rewrite, _in_the_subjects_field,
    _keyed_on_the_line, _names_its_own_thing, _own_thing_words, _the_topic_rules_it_out, _reply_of,
    _a_swap_row, _wants_a_stand_in, _figure_missing, LIMIT_SHAPE, _a_choice_with_one_thing_left_out,
    _a_definition_of_the_entry, _adds_a_figure, _asked_again, _asks_storing, _in_bare_context,
    _in_this_conversation, _keeping_thing, _new_figure, _reaches_another_subject,
    _the_entry_asked_again, _the_plan_keeps,
)
from .answers_part_06 import (
    MONEY_SAID, _asks_a_price, _names_what_it_wants_priced, KEEPING_FROM_THE_ANSWER,
    _keeping_in_the_answer_before, COOK_VERB, KEEPS_ANSWER, KEEPS_ASK, HOW_TO,
    _a_place_of_the_same_kind, _a_place_they_asked, _a_question_about_another_thing,
    _about_the_rest_of_the_question, _cooked_thing, _covered, _more_than_the_thing, _part_asked,
    _repeat_short, _same_where_they_asked, _the_detail_said_again, _the_part_said_again,
    _the_present_with_a_price, _written_for,
)
from .answers_part_07 import (
    REHEAT_ASK, REHEAT_REPLY, _names_another_food, _the_food_named, COMPLAINT, _health_entries,
    _names_a_typed_word, _asks_only_the_length, CONTINUED, _a_detail_answered, _a_dish_was_offered,
    _a_figure_the_answer_has, _about_the_talk, _asks_about_their_taste, _choosing,
    _filling_in_an_emergency, _last_rewrite, _next_usable, _reword_ask, _rewritten,
    _someones_else_diet, _the_plan_answers_this, _the_plan_for, _the_plan_said_again, _tone_of,
    _usable, _without_names,
)
from .answers_part_08 import (
    _A_PERIOD, _OVEN_CHECK_WORDS, _OVEN_WORDS, _PROPERTY_WORDS, _a_bare_thanks, _a_pick_is_asked,
    _says_line, _store_keeps_the_line, _the_food_they_do_not_eat, _the_line_as_said,
)


def _written_ask_with_an_answer(text, memory):
    """The duration ask written out with the action the chat is on, when an entry answers it.

    "how long will it take" after "im learning to drive" is the driving entry's question, and
    neither the line nor the subject put back in ("how long will it take learning to drive")
    reaches it. The written-out ask is only worth taking the turn when it lands somewhere: after
    "i want to grow tomatoes" it asks "how long will it take to grow tomatoes?", no entry answers
    that, and the turn then fell to repeating the answer before it ("Same as before: Give them
    sun, a big pot...") where the person used to get an honest "that's beyond what I know well".
    None when the line is not a duration ask, or the action it names has no answer.
    """
    written = mem.written_out(text, memory)
    if not written:
        return None
    try:
        asked = understand(written, memory)
        found, found_reply = _offer(lambda reject: find(asked, reject=reject), memory, asked)
        if not _answers_a_length(found, found_reply):
            return None
    except Exception:  # noqa: BLE001 - a lookup that fails is not an answer
        return None
    return written


def _with_subject(text, memory, about=None):
    """The follow-up written out with the thing it refers to: "how long will it take?" ->
    "how long will the birthday cake take?". The line itself when it names its own subject."""
    # An ask about time is about an action before it is about a thing: "how long will it take"
    # after "i want to lose a stone" is the question the weight-loss entry answers.
    written = _written_ask_with_an_answer(text, memory)
    if written:
        return written
    words = text.split()
    if len(words) > 14:
        return text
    if ABOUT_YOU.search(text):
        return text  # "do you cook much?" is a question about the bot, not about the dish
    subject = mem.subject(memory) if about is None else about
    if not subject:
        return text
    wanted = [w.strip(".,!?;:").lower() for w in subject.split()]
    said = [w.strip(".,!?;:").lower() for w in words]
    if any(word in said for word in wanted):
        return text  # it already says what it is about
    for i, word in enumerate(said):
        if word in REFERRING:
            words[i] = _the_article(subject, memory) + subject
            return " ".join(words)
    return text


def _amount_asked(text, memory):
    """The figure for a new amount the line names, or None.

    "how long for a 1.5kg one" after the 2kg bird names an amount the last answer does not
    state: the sentence that carries the 2kg time is the wrong figure, and the rate in it ("20
    minutes per 500g plus 20") is only useful worked out. Put the subject back in and let the
    entry answer the new amount, then keep the part that answers this line ("1 hour 20"), never
    the whole paragraph again.
    """
    earlier = _last_answer(memory)
    if not earlier:
        return None
    reply = earlier.get("reply") or ""
    # A correction says the figure again and nothing else, so it names no unit: "sorry i meant
    # 1.5" after the 2kg bird, "no 1.5" after "for six". Nothing read those lines - the amount
    # reader wants a unit, and the store can only say "Thanks for telling me". The unit is the one
    # the conversation last said, so the correction becomes the same "and for <amount>" this
    # function already works out.
    corrected = _the_figure_they_meant(text, memory, reply)
    if corrected:
        # A correction is an ask in its own right: "and for 3 kilos" is a question the entry can
        # answer whether or not the last reply gave a rate to work it out from.
        text = corrected
    elif asked_kind(text) != "time" and not RATE.search(reply):
        return None  # an amount is owed a new figure only when the last answer gave a rate
    clean = lambda found: {re.sub(r"\s+", "", one.group(0).lower()) for one in found}
    amounts = [one.group(0) for one in AMOUNT.finditer(text)]
    wanted = clean(AMOUNT.finditer(text))
    if not wanted or wanted <= clean(AMOUNT.finditer(reply)):
        return None
    subject = mem.subject(memory)
    if not subject:
        return None
    # A line that replaces the size the last answer worked from ("make it 3kg instead", "do it at
    # 2kg this time") is the same ask made at a new size: the words of the replacement are a frame
    # and not a subject. Read as a subject they reach the table's stand-in row ("instead" -> the
    # mince swap) and come back with the rate it happens to carry - "make it 3kg instead" after a
    # roast chicken time was answered "20 minutes", the per-500g figure, when the total for the
    # bird is what was asked. So the ask is put back as the question, with the new size on it.
    replaced = bool(SIZE_REPLACED.search(text)) and asked_kind(text) != "time" and RATE.search(reply)
    if replaced:
        fuller = "how long for {} {}?".format(amounts[0], subject)
    else:
        fuller = _with_subject(text, memory)
        if fuller.strip() == str(text).strip():
            fuller = _about_subject(text, memory)
        if fuller.strip() == str(text).strip():
            # "and for 3kg" points back with no word of its own, so the subject is put on the end.
            fuller = str(text).rstrip("?.! ") + " for the " + subject + "?"
    reading = understand(fuller, memory)
    item = find(reading)
    if item is None or not _is_about(item, subject):
        return None
    # The subject put back can turn the line into a question about something else: after "how do
    # i keep chicken breast moist" the subject is "moist chicken breast", and a whole-bird line
    # then reads as a breast line, so "how long does a 2kg chicken take to roast" was answered
    # with the breast's 18 to 20 minutes. If the line names its own subject and that subject has
    # its own answer, this is not a follow-up about the amount at all: let the entry answer it.
    own = None if replaced else find(understand(text, memory))
    if own is not None and own is not item:
        return None
    fresh = _payload(item, memory, reading)
    # The entry answers the new amount with the rate worked out for the size it was written
    # about ("so a 2kg bird takes roughly 1 hour 40"), and narrowing picks that figure out
    # because it is the only time in the answer: "how long for 250g chicken" was answered with
    # the 2kg figure. Work the entry's own rate out for the amount they named instead.
    sized = mem.sized_reply(fresh, text, memory, _key_words(item))
    if sized:
        return sized
    part = narrow(fresh, fuller) or narrow(fresh, "how long for " + amounts[0])
    if isinstance(part, str) and part.strip() and flat(part) != flat(fresh):
        # The same size asked again gets the same figure, word for word, from a narrowed answer
        # that is one short sentence: say the sentence it was cut from instead, which carries the
        # size and the rate, and the whole answer after that.
        return _part_not_repeated(part, fresh, memory)
    return None


def _the_answer_from_thing(text, thing, memory):
    """The entry for `thing` and its reply to the line, or (None, None) when no entry answers it
    as that thing. The line is written out with the thing in place of its "that"."""
    if not thing:
        return None, None
    fuller = (_with_subject(text, memory) if thing == mem.subject(memory)
              else _with_the_thing(text, thing))
    if fuller.strip() == str(text).strip():
        return None, None
    wider = understand(fuller, memory)
    found, said = _offer(lambda reject: find(wider, reject=reject), memory, wider)
    if found is None or not _is_about(found, thing) or _said_before(said, memory):
        return None, None
    return found, said


def _in_context(text, memory, reject=None):
    """The knowledge entry a follow-up is about, by naming the thing it refers to.

    "How long will it take, start to finish?" after a birthday cake is the question "how long
    will the birthday cake take?", which the knowledge base answers. Only tried when the line
    on its own found nothing, so a full question is never rewritten, and a follow-up never
    gets the answer the bot has just given.
    """
    subject = mem.subject(memory)
    # The head of the subject is the thing it names, not its last word: "my sourdough keeps going
    # flat" is about the sourdough, and "flat" is the house word there, so reading the last word
    # alone let the first-home entry take "how long should i prove it". A subject that names no
    # thing at all keeps the old reading, because its last word is all there is.
    thing = _head_thing(subject)
    refused = _refused(text)
    if refused:
        # The line rules a thing out ("anything but a horror"). No entry about that thing is an
        # answer to it whichever rewrite reached it, unless its own reply answers around the
        # refusal ("skip horror and gore"), so the entries are searched past it.
        inner = reject
        reject = (lambda one: _hands_back_the_refusal(one, refused)
                  or (inner is not None and inner(one)))
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = understand(text, memory)
    if understood.get("intent") == "ack":
        return None  # "nice one, thx" is a thank-you, not a question about the dinner
    if _asks_how_to_say_it(text):
        return None  # see SAY_IT: the referring word here is the person or the news
    if not leans_on_a_subject(understood):
        # A statement that names its own subject is not a follow-up: "i have a dog" then "i walk
        # twice a day" was answered with the 10,000-steps entry, "im redecorating the bedroom"
        # then "i have a small budget" got a list of cheap dinners, and "my knee hurts" then "i
        # work on my feet all day" got the foot-ache one. None of those is about the thing they
        # said before; each is news about themselves, and the entry that answered was reached
        # only by putting the earlier subject back in.
        return None
    if _names_its_own_thing(text, memory):
        return None
    fuller = _with_subject(text, memory)
    if fuller.strip() == text.strip() and not _own_thing_words(text, memory):
        # The rewrite hangs the subject on the line as a property of it ("how much is a tv
        # licence for the credit score"), which is only a follow-up when the line brings no
        # thing of its own: see _own_thing_words.
        fuller = _about_subject(text, memory)
    if fuller.strip() == text.strip():
        # A bare ask ("what should I see?") points at the thing with no word at all, so the
        # thing is tried on the end of it and the entry has to be about that thing.
        fuller = _with_bare_subject(text, memory)
        # A line that only narrows the choice ("something funny but not silly", "nothing scary")
        # names no thing of its own; with the thing already being chosen put back on the end it
        # is a line the entries can read, and it reaches the narrowed entry rather than a shrug.
        for rewrite, added, domain in _qualifier_rewrites(text, memory):
            item = _from_rewrite(rewrite, text, memory, reject, added, domain)
            if item is not None:
                if _hands_back_the_refusal(item, _refused(text)):
                    continue  # the line ruled this out: an answer that ignores it is worse than none
                return item
    if (fuller.strip() == text.strip()
            and _the_answer_was_about_the_subject(memory)
            and (not _own_thing_words(text, memory) or ADDING_TO_THE_SUBJECT.match(text))):
        # Nothing to put in front of the subject, so it goes on the end, longest run first.
        # "and what about holidays" names a word of its own, but it is a word added to the thing
        # on screen rather than a new subject: "im thinking of getting a cat" then "what about
        # holidays" is the cat's holiday, and without the tail it was answered with the paid
        # holiday from work.
        skip = set()
        after_used = False
        for fuller in _subject_tails(text, memory, understand(text, memory)):
            reading = understand(fuller, memory)
            after_used = False
            while True:
                item = find(reading, reject=lambda one: one.id in skip
                            or (reject is not None and reject(one)))
                if item is None:
                    break
                skip.add(item.id)
                # The subject was put on the end, so the entry has to be keyed on one of its
                # words, be about the thing the subject names, and its answer has to be one we
                # have not just given.
                if not _named_by(item, subject):
                    continue
                if thing and not _is_about(item, thing):
                    continue
                reply = _payload(item, memory, reading)
                if not reply.strip():
                    continue
                if _said_before(reply, memory):
                    after_used = True
                    continue
                if not _answers_the_figure(text, reply):
                    # The line asks for a figure this entry never states, so the subject put on
                    # the end of it landed on an entry about something else: the next reading
                    # down is no better, and the honest hedge is what the person gets.
                    return None
                if after_used and not _keyed_on_the_line(item, text):
                    # One entry down from the best reading is only worth taking when the line
                    # itself says what it is about: "what do i wear" does, and the outfit entry
                    # is next. Without that the subject's words land on something that is not
                    # the question — "what should i feed him" after a sick dog reached the
                    # car-sickness advice that way.
                    return None
                if _left_out(item, text):
                    return None  # the line names a thing this entry never mentions
                if _the_topic_rules_it_out(item, memory):
                    # The words put on the end came from the topic, so an entry the topic itself
                    # rules out is not this chat's: "what do i need" after "im making a thai
                    # green curry tonight" was read as "what do i need thai green curry" and
                    # handed the what-to-order card, which rules itself out for "making" - the
                    # person cooking tonight was told what to order in. Same test as the one
                    # that guards the widened reading (`topics.keeps_away`), made here because
                    # this is the other way a subject gets put back into the line.
                    return None
                return item
        return None
    if not fuller or fuller.strip() == text.strip():
        return None
    # An entry about something else is passed over rather than taken, so the search goes on to
    # the entry that is about the thing - and to nothing at all if there is none.
    # "Something else" includes another part of the knowledge base: a bare ask leans on the
    # words of the line before it, and one of those words sits in other domains too, so "my
    # kids wont listen to me" and then "what can i do" reached the music entry off the word
    # "listen". A fact this talk never touched is passed over like an entry about something else.
    #
    # A subject read off the person's description also ends in the word they used for the fault
    # ("laptop keep freezing", "freezer frosting"), and the last word of that is the fault, not
    # the thing: "is it worth fixing" after a laptop was answered by the entry about how long
    # food keeps in the freezer, which is about "freezing". The thing a subject names is only a
    # guess, though (a "bathroom tap" is read as the bathroom, and the cleaning entry answers for
    # the bathroom), so both readings are tried and the subject's own words decide between them.
    reading_here = understand(fuller, memory)
    inner = reject
    want = thing or subject
    fits = lambda one: _is_about(one, want) and about_the_topic(one, reading_here)
    about = lambda one: _is_about(one, subject) and about_the_topic(one, reading_here)
    strict = (lambda one: not fits(one) or (inner is not None and inner(one)))
    loose = (lambda one: not about(one) or (inner is not None and inner(one)))
    item = find(reading_here, reject=loose)
    if item is None or not _in_the_subjects_field(item, subject):
        # The line's own reading reached an entry about another field ("a laptop that keeps
        # freezing" is not a question about the freezer), so the entry about the thing the
        # subject names is tried before that one is given.
        better = find(reading_here, reject=strict)
        if better is not None and (item is None or _in_the_subjects_field(better, subject)):
            item = better
    if item is None:
        return None
    # "what kind should I get?", "which brand?" name no thing of their own: the word that looks
    # like one is the ask itself, and the thing they ask about is the last subject.
    own = None if mem.KIND_ASK.search(text) else _own_thing(understand(text, memory))
    if own and not _is_about(item, own):
        return None  # the line names its own thing: it is not about the last subject
    if _left_out(item, text):
        return None  # the line names a thing this entry never mentions
    reply = item.reply
    if isinstance(reply, (list, tuple)) or callable(reply):
        # Handed back with the reading of the written-out line, so an entry that words itself
        # from the line names the thing: "is it worth repairing" after a freezer that has iced
        # up said "A machine is worth repairing" when the entry had the freezer in front of it.
        # When that answer is one the person has already heard, the line's own words get the
        # choice instead: "is that enough" after the child-and-veg advice came back as the same
        # advice, where the five-a-day figures were the answer to what was asked.
        held = reading_here
        if _said_before(_payload(item, memory, reading_here), memory):
            here = understand(text, memory)
            own_words = _payload(item, memory, here)
            if own_words.strip() and not _said_before(own_words, memory):
                held = here
        return item, held
    if _said_before(reply, memory):
        return None  # the same answer again is no answer
    if not _answers_the_figure(text, reply):
        return None  # the answer names no figure and the line asks for one
    return item, reading_here


def _keeping_entry(text, memory, thing=None, storing=False):
    """The entry that says how long the topic keeps, when the knowledge base has one.

    "how long does that keep" after a boiled egg is about the eggs, and the eggs have their own
    answer (a week in the fridge). Only an answer that really talks about keeping counts, so a
    recipe or a cupboard line cannot answer it.
    """
    fuller = _with_subject(text, memory, thing)
    if fuller.strip() == text.strip():
        fuller = _about_subject(text, memory)
    if fuller.strip() == text.strip():
        return None
    reading = understand(fuller, memory)
    item = find(reading)
    if item is None or not _is_about(item, mem.subject(memory)):
        return None
    reply = _reply_of(item, reading, memory)
    if not isinstance(reply, str) or not reply.strip():
        return None
    # An answer counts when it talks about keeping, or when it is the answer just given to a
    # storage question: "how do i keep herbs fresh" answers with the jar and the damp paper and
    # no figure at all, and it is still what the person asked to hear again. A recipe or a
    # cupboard line that was not the last answer never gets in this way.
    # The answer just given counts only after a how-to-store line, where it *is* the keeping
    # answer to say again. Anywhere else the previous answer may be a cooking time: after "how do
    # i roast a chicken" the roast timetable is about the chicken and was just said, and it is
    # still the wrong answer to "and how long does that last".
    said_already = bool(storing and _said_before(reply, memory))
    if not KEEPS.search(reply) and not said_already:
        return None
    # The answer has to be about keeping the thing that was cooked. After "what can i make with
    # mince and onions" the subject names both foods, and the onion entry is about raw onions in
    # a cupboard ("never the fridge") - the opposite advice to a cooked dish. A dish of two or
    # more foods is kept by the cooked-food rule, not by one ingredient's cupboard rule.
    subject = mem.subject(memory)
    if subject and len(cooking.ingredients(understand(subject, memory))) > 1:
        # A dish of two or more foods is kept by the cooked-food rule, whatever one ingredient's
        # own answer says. After "what can i make with chickpeas and spinach" the subject names
        # both foods, and the spinach entry answers for leaves in a salad drawer ("About 5 days"),
        # which is the raw ones, not the pan that just came off the hob.
        return None
    # The answer just given was this one, and it is still the answer: "how do i store potatoes"
    # then "how long does that keep" asks for the figure that is in it. Standing aside here hands
    # the line to the general fridge table, which answers a raw loaf with "keep it covered in the
    # fridge" - the opposite of the bread answer just given. So the keeping answer is said once
    # more rather than a different one being said instead - but only the part of it that answers
    # the question: "how do i store eggs" then "how long does that keep" wants "three weeks", not
    # the shelf in the door and the temperature of the fridge as well.
    if said_already:
        figures = [part.strip() for part in SENTENCE.split(reply) if FIGURE.search(part)]
        if figures:
            return " ".join(figures)
    return reply


def _offer(reader, memory, reading):
    """The first entry the reader offers whose reply stands, and that reply.

    An entry can fit the words and still turn the line down, because the conversation says the
    line is about something else: "how long do i cook it for", after a packet of mince, is a
    question about the mince. A lower entry that can answer should still get its turn rather
    than the whole turn shrugging.
    """
    text_here = reading.get("text") if isinstance(reading, dict) else ""
    names_it = _names_what_it_wants_priced(text_here)

    def price_asked(held):
        return _asks_a_price((held or {}).get("text") if isinstance(held, dict) else text_here)

    declined = set()
    refused = _refused(text_here)
    # The first entry the price filter turned down, kept in case nothing below it states money.
    fallback = None
    # The same for a line that asks for the words: the first entry whose reply says nothing to
    # say is kept for the end, so a line with no "what to say" card still gets the answer its own
    # words reached rather than a shrug.
    # Only for the line the person just sent: a reader that puts the last turn's subject back
    # into a follow-up hands back a reading whose plain words are that earlier line, and a card
    # declined there is a card declined for a question nobody has asked yet ("what can i say to
    # her" after a nervous-daughter turn stepped from the school answer to the weaning one).
    here = str((reading or {}).get("plain") or "").strip().lower()
    now = str((memory or {}).get("understood", {}).get("plain") or "").strip().lower() \
        if isinstance(memory, dict) else ""
    words_wanted = (_the_ask_is_for_words(reading)
                    if not here or not now or here == now else False)
    words_fallback = None
    # How many cards the wording rule may turn down before the answer its own words reached is
    # given after all. A line asks for the words, not for a walk through the card index: with no
    # limit, "what can i say to her" (read on the whole chat, so the subject is "my daughter")
    # stepped from the school answer past three cards to how to start a baby on solids.
    words_declines = 0
    while True:
        got = reader(lambda one: one.id in declined)
        if got is None:
            kept = fallback or words_fallback
            if kept is None:
                return None, None
            item, held = kept
            reply = _payload(item, memory, held)
            return (item, reply) if reply.strip() else (None, None)
        # A reader that wrote the line out to reach the entry hands back the reading it used,
        # because an entry can phrase itself from it ("In Rome: ..." needs "rome" in the line).
        item, held = got if isinstance(got, tuple) else (got, reading)
        if price_asked(held):
            reply = _payload(item, memory, held)
            if reply.strip() and not MONEY_SAID.search(reply):
                # The line asks for a price and this entry states none: it is answering the
                # thing, not the question. The entry below may price it. If none does, an answer
                # that is still new is better than a shrug - "how much does it cost to fix a
                # dripping tap" is answered by naming the washer, and that entry states no
                # money - but an answer the bot has already given is not, which is the noise in
                # the brakes said back a second time.
                if names_it and fallback is None and not _said_before(reply, memory):
                    fallback = (item, held)
                declined.add(item.id)
                continue
        if not (_wants_a_stand_in(reading) and _a_swap_row(item)) \
                and _hands_back_the_refusal(item, refused):
            # The line rules this thing out ("anything but a horror"), and the answer says
            # nothing about leaving it out: a confident answer about the very thing the person
            # refused is worse than a shrug, so the next entry gets the turn.
            declined.add(item.id)
            continue
        reply = _payload(item, memory, held)
        if (reply.strip() and refused
                and not (_wants_a_stand_in(reading) and _a_swap_row(item))
                and _is_about(item, refused)
                and not _says_it_leaves_it_out(reply, refused)):
            # An entry that phrases itself from the line cannot be asked about the refusal before
            # it is written, so it is asked afterwards: "i dont like sad films" reached the sad
            # films and was told "For a good cry: Manchester by the Sea...", which is the one
            # answer the line had ruled out. Only a reply that says nothing about leaving the
            # thing out is handed back, and the entry below may still answer.
            declined.add(item.id)
            continue
        if (reply.strip() and words_wanted and words_declines < 3 and held is reading
                and not _said_before(reply, memory)
                and not SAID_OUT_LOUD.search(reply)
                and not _puts_it_to_someone(reply)):
            # The line asks for the words and this card answers the thing they are about: "how do
            # i tell my flatmate to do the dishes" was answered with how to wash up, and "ordered
            # a pizza and it came freezing cold, what can i say" with how long a pizza freezes.
            # The card below it may be the one that says it; when none does, the answer here is
            # still better than a shrug, so the first of them is kept for the end. A reply that
            # already says how to put it to somebody is left alone: see `_puts_it_to_someone`.
            if words_fallback is None:
                words_fallback = (item, held)
            declined.add(item.id)
            words_declines += 1
            continue
        if reply.strip():
            return item, reply
        declined.add(item.id)


def _keeping_reader(reading, memory):
    """The reader for a line that asks how long something keeps rather than how long it cooks.

    "how long does a cooked chicken last" reached the roast timetable, and "how long does a cooked
    ham last" a shrug, though the knowledge base has an answer that says how long it keeps. The
    keeping answer is the one the line asked for, so it is looked for first; when there is none,
    the line is answered as it was before.
    """
    if not cooking.keeping_ask(reading):
        return lambda reject: find(reading, reject=reject)

    own = _own_thing(reading)

    def keeps(of, reject):
        def not_about_keeping(one):
            if reject(one):
                return True
            return not cooking.speaks_of_keeping(_payload(one, memory, of))
        return find(of, reject=not_about_keeping)

    def in_the_fridge(of):
        # "how long does a roast keep" names the keeping but not where, and the answer that holds
        # the figure is keyed on the fridge. This is the same line with the obvious place on it.
        cold = dict(of)
        cold["clean"] = (str(of.get("clean") or of.get("text") or "") + " in the fridge")
        cold["words"] = list(of.get("words") or ()) + ["in", "the", "fridge"]
        return cold

    def with_the_thing(of):
        # The thing the conversation is on goes into the line before the fridge does. "what can i
        # make with eggs" then "how long do they keep" is a question about the eggs, and the eggs
        # have their own keeping answer (three weeks on the box); the general fridge table is the
        # answer for a thing we cannot name, and a worse one for a thing we can. Only an entry
        # that speaks of keeping counts, so a recipe or a cupboard line cannot get in this way.
        said = str(of.get("text") or of.get("clean") or "")
        fuller = _with_subject(said, memory)
        if not fuller.strip() or fuller.strip() == said.strip():
            return None
        return understand(fuller, memory)

    def reader(reject):
        found = keeps(reading, reject)
        if found is None:
            thing = with_the_thing(reading)
            if thing is not None:
                found = keeps(thing, reject)
        if found is None and not own and mem.last_module(memory) == "answers":
            # The thing in hand said how long it keeps in the answer just given, and this line
            # names no food of its own: that figure is the answer, and the wide table is not.
            kept = _keeping_in_the_answer_before(memory)
            if kept:
                return lookup_entry(KEEPING_FROM_THE_ANSWER, ("keep", "keeps", "last", "lasts"),
                                    kept)
        if found is None and mem.last_module(memory) == "answers":
            # The general table answers a thing we cannot name, so there has to be a thing:
            # "that" points at the answer before, and when the turn before was not an answer
            # about anything ("hey" then "how long does that keep") there is nothing to keep.
            # The subject is no use as the test - the words of the line are the gist of it, so
            # a bare "how long does that keep" makes its own subject "keep".
            cold = keeps(in_the_fridge(reading), reject)
            # The general table is the answer for a thing we cannot name, never for a food the
            # line names: "how long does vinegar last" is not "cooked food keeps 3 to 4 days".
            # A food with an answer of its own was found above, so this is the last resort.
            if cold is not None and own and not _is_about(cold, own):
                cold = None
            found = cold
        return found or find(reading, reject=reject)

    return reader


def _a_cooking_ask_after_a_keeping_answer(understood, memory):
    """The method entry's answer to a "how long do i cook it for" after a keeping answer.

    "how long does cooked chicken last" then "how long do i cook it for" said "3 days": the
    keeping sentence was handed back as if it were a cooking time, because the follow-up names
    no food and the last answer is what the conversation is on. The keeping question and the
    cooking question are about the same food, so the line read with the food put back in ("how
    long do i cook the chicken for") reaches the entry that knows the method, and that entry
    answers. The food may have no method entry (mince, gammon), and then this says nothing.
    """
    line = str(understood.get("clean") or understood.get("text") or "")
    if not line or not COOK_VERB.search(line) or KEEPS_ASK.search(line):
        return None  # a keeping question of its own: "how long do i cook it for the fridge"
    # The keeping answer is still the one on the table after a "thanks": an acknowledgement says
    # nothing about the food, so "thanks" / "how long does it take to cook" was reading the
    # bot's "Glad that helped." and missing the keeping answer it has to stand down for.
    said = str((mem.answer_in_hand(memory) or {}).get("bot") or "")
    if not said or not KEEPS_ANSWER.search(said):
        return None  # nothing about keeping in the last answer, so not this
    # A follow-up that names a different food is a new question even when a keeping answer is on
    # the table: "how long do i reheat a pizza" after "how long does cooked chicken last" is
    # about pizza, and the entry that knows pizza answers it. Only a follow-up on the same food
    # (the pronoun, or the food named again) is this guard's business.
    subject = str(mem.subject(memory) or "").lower()
    if _names_another_food(understood, subject):
        return None
    if REHEAT_ASK.search(line):
        # Heating is a third clock, and it is the same question whatever the food is: what
        # matters is piping hot right through, not a time taken from the fridge life. The
        # keeping answers each say their own version of it in a sentence that also carries
        # keeping facts ("and eat it cold within 3 days"), so the reply is written once here
        # rather than cut out of them.
        return REHEAT_REPLY
    # The food may be named again in the follow-up ("how long do i cook pasta for", "how long do
    # i fry bacon"), and then the line itself is the reading: adding the subject would only make
    # a sentence nobody typed. When it is the pronoun that stands for the food, the line is
    # written out with the food put back in.
    food = _the_food_named(mem.subject(memory)) or None
    fuller = _with_subject(line, memory, about=food)
    if fuller.strip() == line.strip():
        fuller = _about_subject(line, memory, about=food)
    readings = [fuller, line] if fuller.strip() != line.strip() else [line]
    # The subject the memory keeps is the food as the keeping answer named it ("cooked rice"),
    # and "how long do i cook the cooked rice for" reads the keeping word as a dish of its own.
    # The method question is about the food, so the keeping adjective comes out of it.
    readings = [re.sub(r"\b(cooked|leftover|left over|roast|roasted)\s+(?=[\w' ]+\bfor\b)", "",
                       reading, count=1) for reading in readings]
    # What the line asks for is the pan's time, and a keeping entry can be reached by the same
    # words ("how long do i cook it for" landing on the rule about cooked food). A keeping answer
    # states days, not minutes, so one that states no length of time is only the fallback: the
    # answer with a time in it is the one this line wants.
    fallback = None
    for written in readings:
        reading = understand(written, memory)
        item, answer = _offer(lambda reject: find(reading, reject=reject), memory, reading)
        if item is None or not isinstance(answer, str) or not answer.strip():
            continue
        if answer.strip() == said.strip():
            continue  # the same keeping paragraph: nothing better to say about the pan
        if _minutes_in(answer):
            return answer
        fallback = fallback or answer
    return fallback


def _a_complaint_answered(text, understood, memory):
    """The help a report of a sore or a trouble did not spell out, or None.

    "i get heartburn after meals" reached nothing and got "I'm listening - say more if it
    helps", which is what a person says when they have not heard you. The line is read as the
    question a friend hears ("what can I do about heartburn"), against the health answers only.
    """
    if not COMPLAINT.search(_flat(text)):
        return None
    if trouble_reading.reads_as_trouble(_flat(text), (understood or {}).get("words")):
        # A bodily trouble the chat module already talks them through ("i get migraines" gets the
        # dark room and something for it early) is that module's turn: this reading is only for a
        # report that nothing else has a word for, so nothing it answers today moves.
        return None
    if find(understood) is not None:
        return None  # the line found its own answer: nothing to add
    again = dict(understood)
    again["clean"] = "what can i do about " + str(understood.get("clean") or _flat(text))
    # a reading of its own is words of its own: a guard that asks whether a word is in `words`
    # raises on None, and this reading would lose the answer it exists to give
    again["words"] = [word for word in re.findall(r"[a-z']+", again["clean"].lower()) if word]
    item, reply = _offer(lambda reject: find(again, entries=_health_entries(), reject=reject),
                         memory, again)
    if item is None or not isinstance(reply, str) or not reply.strip():
        return None
    if not _names_a_typed_word(item, text):
        return None
    remember_answer(memory, reply, _key_words(item))
    _remember_answer(memory, item, reply)
    return reply


def _the_figure_the_thing_we_are_on_holds(text, memory):
    """The answer the thing we are on gives this length ask, when it holds the time asked for.

    "how long will it take, start to finish?" after "im making a birthday cake" and "he is
    allergic to nuts": the answer just given is the cake's allergy variant and holds no time, so
    the honest line said the steps are not a length - but the cake the chat is on has its
    timings, and the ask read against it ("... cake") reaches them. The honest line is for a
    length ask that no entry answers, not for one whose subject is a turn back.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return ""
    wider = followup_reading(understood, memory)
    if not isinstance(wider, dict) or wider is understood:
        return ""
    if _flat(str(wider.get("clean") or "")) == _flat(str(understood.get("clean") or "")):
        return ""
    item, reply = _offer(lambda reject: find(wider, reject=reject), memory, wider)
    reply = str(reply or "").strip()
    if item is None or not reply:
        return ""
    # The entry has to hold the figure the line asks for, or the honest line is the right one.
    return "" if _figure_missing(reply, text) else reply


def _a_length_ask_with_no_figure(text, memory, answer=""):
    """The honest line for a length ask about an answer that holds no time.

    "How long will that take" after the steps for a blocked sink shares no word with the steps, so
    there is no sentence of the answer to quote: the lookup reaches nothing, and the whole
    paragraph came back behind "Same as before". The arbiter passes an echo over as soon as
    another module has anything fresh to say, and a search is fresher, so the person was told
    "I'd rather not guess" about the job in front of them. A friend says the answer holds no time
    and names the first step, so that line is built here, before the repeat is framed.
    """
    if not _asks_only_the_length(text) or mem.last_module(memory) != "answers":
        return None
    earlier = _last_answer(memory)
    last = str((earlier or {}).get("reply") or "")
    if not last.strip():
        return None
    if answer:
        opening = _flat(last)[:60]
        if not opening or opening not in _flat(answer):
            return None  # this reply is not the last answer again, so it is a different answer
    honest = _figure_missing(last, text)
    if not honest or _flat(honest) == _flat(answer):
        return None
    # The answer just given holds no time - but the thing the chat is on may: after a cake and a
    # line about the nuts, the allergy variant is the answer in front and the cake has the
    # timings. That answer beats the honest line, and it is only looked for here, where the
    # honest line would otherwise be said.
    return _the_figure_the_thing_we_are_on_holds(text, memory) or honest


# Someone who can call the person in wants a word with them: "my sons teacher wants to see me"
# is not a question about teaching, and "the doctor wants to see me" is not one about booking
# an appointment - yet the entries that know those subjects answered them, because the only
# word they shared with the line was the office itself. The chat has a pool for each shape of
# summons (a word, a letter, a phone call), so the knowledge base steps aside for a line that
# says nothing but the office and the asking. A line that says what the word is about keeps its
# answer: "... wants to see me about his reading" is the reading entry's, and "a letter from
# the council saying i owe council tax" is the council tax letter's.
OFFICE_WHO = frozenset(SUMMONS_WHO) | frozenset("""
    social services health visitor home tax job centre jobcentre letting agent the
""".split())


# The words a summons is made of - what they asked for, and the asking itself - so a line whose
# only shared words are these has been read for the office and nothing else.
OFFICE_ASKING = frozenset("""
    word words meeting meetings appointment appointments letter letters written wrote write
    writing rang ring ringing phoned phone called call calls message messages email emailed
    note notes see saw talk talks speak speaking discuss discussing chat meet come came coming
    quick asked ask asks asking want wants wanted need needs needed like would got receive
    received had saying told
""".split())


def _only_the_office(memory):
    """True when the entry this line reaches answers on the summons' office and nothing else."""
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict) or not isinstance(understood.get("summons"), dict):
        return False
    if understood.get("asks") or understood.get("kind") == "question":
        return False
    item = find(understood)
    if item is None:
        return False
    said = {str(word).lower().rstrip("s") for word in _key_words(item)}
    typed = {str(word).lower().rstrip("s") for word in (understood.get("keywords") or ())}
    shared = said & typed
    return bool(shared) and not (shared - OFFICE_WHO - OFFICE_ASKING)


def _a_food_named_of_its_own(understood, food):
    """True when the line names a food of its own that is not the food in hand.

    A keeping question is only a follow-up when the food in it is the one the store is holding.
    "how long can i keep cooked chicken in the fridge" a turn after the rice was answered is a
    question about the chicken: it names its own food, so nothing has to be put back in, and the
    chicken's own entry is the answer. Read as a bare "how long does that keep" it was put back
    together with the food the store held - "how long does cooked rice keep in the fridge" - and
    the chicken question came back with the rice paragraph behind "Same as before", which is
    the one answer nobody can use. Only a line that brings no other food leans on the one in hand.
    """
    held = set(str(food or "").lower().split())
    if not held:
        return False
    for name in cooking.ingredients(understood) or ():
        if not set(str(name).lower().split()) & held:
            return True
    return False


def _keeping_about_the_food_there(memory, understood):
    """The keeping fact for the food the chat has moved to, when a bare line asks about "it".

    "im making a cake" / "frosting" / "i burnt the rice" then "can i still eat it" is a keeping
    question about the rice, and the rice's own entry says 24 hours in the fridge. The line names
    nothing, though, so the entries never reach it: the dish follow-up answers instead from the
    last *dish* the store heard of, which here is the cake two turns back, and "3 days in a tin"
    is a keeping fact about the wrong food. Where the chat has moved to a food with no plan of its
    own, the question is put with that food in it and the entries answer - they are where the
    keeping facts live.

    Only when there is a dish for the store to answer from. With no dish in the chat, nothing
    hands out a fact about another food: "i burnt the rice" / "can i still eat it" is about the
    rice in front of them, and the answer already on the table - take it off the heat, lift the
    burnt bits out - covers it. A freshness figure is a different question about a different
    thing, and the repeat says more than the figure does - main's own "Same answer" path already
    hands that answer back, so this stands aside and lets it.
    """
    if not isinstance(memory, dict) or not isinstance(understood, dict):
        return None
    if dishes.ask_kind(understood) != "keep":
        return None
    if not dishes.dish_for(memory, understood):
        return None  # no dish to answer from: the answer on the table is the answer
    if cooking.ingredients(understood):
        # The line names a food of its own, so it is not the bare "can i still eat it" this is
        # for: the entries read it as it stands. "how do i cook rice" then "how long does chicken
        # last in the fridge" names the chicken and no "it" at all, and the food the chat is on
        # put the rice's 24 hours in place of the chicken's two days.
        return None
    food = named.the_food_it_is_about(understood, memory)
    if not food or dishes.dish_in(food):
        return None  # a food with a plan of its own is the plan's to answer
    if _a_food_named_of_its_own(understood, food):
        return None  # the line brought a food of its own: its own entry is the answer
    if not cooking.ingredients(understand(food, memory)):
        return None  # not a thing anyone keeps: a pot, a plant, a word we do not know
    asked = understand("how long does cooked " + food + " keep in the fridge", memory)
    item, reply = _offer(lambda reject: find(asked, reject=reject), memory, asked)
    if getattr(item, "id", "") in GENERIC_KEEPING:
        return None  # a fact about cooked food in general says nothing about this food
    return reply if isinstance(reply, str) and reply.strip() else None


def _the_answer_on_the_table(understood, memory):
    """The answer already on the screen, when the keeping question is about the food in it.

    "i burnt the rice" / "can i still eat it" names no food, so no entry reaches it, there is no
    dish for the store to answer from, and the turn fell through to a search hedge with a
    paragraph about the rice sitting right above it. The food the chat is on is the food the last
    answer was about, so that answer is said again - but only when it answers the *trouble* the
    person named ("burnt" is in it), never when it is how to cook the thing: after "i cooked too
    much pasta" the answer on the table is the pan and the timing, and saying it again does not
    say whether the pasta can still be eaten, so a hedge is the honest reply and a confident
    repeat is not.

    This is the last resort of `_respond`: an entry that can answer the line as it stands always
    beats a repeat of the turn above it ("i burnt the toast" / "can i still eat it" is a direct
    yes, and it must stay one).
    """
    if not isinstance(memory, dict) or not isinstance(understood, dict):
        return None
    if dishes.ask_kind(understood) != "keep":
        return None
    food = named.the_food_it_is_about(understood, memory)
    if not food or food.lower() not in str(mem.last_user(memory) or "").lower():
        return None  # the food is not the one the last answer was given about
    if _a_food_named_of_its_own(understood, food):
        return None  # the line brought a food of its own: its own entry is the answer
    turns = memory.get("turns")
    last = turns[-1] if isinstance(turns, list) and turns and isinstance(turns[-1], dict) else None
    if not last or last.get("module") != "answers":
        return None  # the line on the screen is not an answer from the knowledge base
    said_back = str(last.get("bot") or "")
    if not said_back.strip():
        return None
    trouble = (_carries(mem.last_user(memory)) - {word.lower() for word in food.split()}
               - _carries(food)) & _carries(said_back)
    if not trouble:
        return None  # the answer is not about the trouble in the line: do not say it again
    return AGAIN[0].format(reply=_in_short(said_back))


def _already_on_the_screen(reply, memory, turns=4):
    """Whether this reply is an answer the person already has, word for word."""
    mine = " ".join(str(reply or "").split()).lower()
    if not mine:
        return True
    seen = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(seen, list):
        return False
    for turn in seen[-turns:]:
        if isinstance(turn, dict):
            said = " ".join(str(turn.get("bot") or "").split()).lower()
            if said and said == mine:
                return True
    return False


# "read it again" after a verse is the verse asked for, not a lapsed reading habit: "read" and
# "again" are the lapsed-reader row's key words, so somebody who had just been given a poem was
# told to start with *Of Mice and Men*. The verse is written as a lead with lines under it, which
# is what tells it apart from every other reply here.
_READ_AGAIN = re.compile(
    r"\b(?:read|say|tell|sing)(?: it| that| this)?(?: again| once more)\b"
    r"|\bread it (?:back|to me again)\b"
    r"|\b(?:again|once more) please\b", re.I)


_VERSE_FORM_WORD = re.compile(
    r"\b(story|stories|tale|tales|poem|poems|rhyme|rhymes|rap|song|verse|limerick|haiku|"
    r"couplet|ode|sonnet)\b", re.I)


def _the_verse_said_again(text, memory):
    """The verse the last turn gave, said once more, or None when the last turn was not one.

    Only a verse counts: a lead with lines under it. A hedge, an idea or a piece of advice about
    a poem is not something to read out again, and a verse from three turns back is not what
    "read it again" points at.
    """
    if not isinstance(text, str) or not _READ_AGAIN.search(text):
        return None
    turns = [turn for turn in ((memory or {}).get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(turns):
        said = str(turn.get("bot") or "")
        if not said:
            continue
        asked = str(turn.get("user") or "")
        if not (_VERSE_FORM_WORD.search(asked) or said.startswith("Once more")) or "\n" not in said:
            return None
        said = said[said.index("\n") + 1:] if said.startswith("Once more") else said
        lead, lines = said.split("\n", 1)
        # A form that announces itself ("A limerick, then:") is not given a second lead, or the
        # person gets "Once more, then: A limerick, then: ...".
        if lead.rstrip().endswith(":"):
            return "Once more.\n" + lines
        return "Once more, then:\n" + said
    return None


# The frame a repeat reader puts in front of an answer already on the screen. A how-much line
# wants the figure, and a frame that points back at the card is not the figure said again.
_REPEAT_OPENS = re.compile(r"^(?:same as before|same answer|as i said|you've got it|you have it|"
                           r"i said|still)\b", re.I)


# The bare ways of asking for the figure again, with nothing of the subject in them. A line
# like this cannot be matched by the shared-word reader, and the answer it gets is the figure
# already on the screen; the repeat reader would frame that answer as a pointer at the card.
_A_BARE_MEASURE = re.compile(
    r"^\s*(?:(?:and|so|then|ok|okay)\s+)?how (?:much|many)"
    r"(?:\s+(?:is it|is that|does it cost|does that cost|again))?\s*[?.!]*$", re.I)


def _the_sentence_around(fragment, text):
    """The whole sentence of `text` that holds `fragment`, or "" when it does not hold it.

    "The limit for an adult is 6g of salt a day." is a cut of the card's first sentence, and the
    rest of that sentence ("about a level teaspoon, and most people eat 8g") is what a friend
    says. A figure sentence inside a longer answer is widened the same way, so the warning that
    happens to share the word "take" is not handed back as the dose.
    """
    fragment = str(fragment or "").strip()
    text = str(text or "")
    if not fragment or not text:
        return ""
    flat_fragment = " ".join(fragment.split()).rstrip(".")
    lowered = " ".join(text.split())
    where = lowered.lower().find(flat_fragment.lower())
    if where < 0:
        return ""
    start = 0
    for match in re.finditer(r"(?<=[.!?])\s+", lowered[:where]):
        start = match.end()
    end = len(lowered)
    match = re.search(r"[.!?](?=\s|$)", lowered[where + len(flat_fragment):])
    if match:
        end = where + len(flat_fragment) + match.end()
    return lowered[start:end].strip()


def _the_sentence_with_a_figure(text):
    """The first sentence of `text` that carries a figure and says what the figure is of.

    A bare "how much" after "A banana is about 105 calories (a medium one)." is the figure
    already on the screen. The shared-word reader has nothing to match and the repeat reader
    framed that sentence as "Same as before: ...", which points at the answer instead of giving
    it. The sentence itself is the answer, and it is the sentence a how-much line gets.
    """
    for sentence in SENTENCE.split(str(text or "")):
        said = sentence.strip()
        if (said and re.search(r"\d", said)
                and (SIGNALS["amount"].search(said) or SIGNALS["money"].search(said))):
            return said
    return ""


# The words themselves, as a card says them: a sentence to say, given in quotes, or a reply that
# opens on telling the person what to say. That is what the line asked for when `shapes.
# asks_for_words` is true, and a card that answers the thing instead - "Fill the sink with the
# hottest water" for how to tell a flatmate about the dishes - has neither.
SAID_OUT_LOUD = re.compile(
    r"[\"“][^\"”]{6,}[\"”]|'[^']{8,}'"
    r"|^\s*(?:say|tell|ask|put it|word it|lead with|start with|open with|write)\b"
    # A card that says which question to put is giving the person something to say, even when it
    # writes it out without quotes: "ask each trader the same question: what would bring that
    # down?" is the words to use.
    r"|\b(?:ask|say|tell|raise)\b[^.?!]{0,40}\b(?:question|questions|sentence|words|wording)\b",
    re.I)


# A reply that is about taking the matter to somebody *is* the answer to "how do i tell them":
# "how do i tell my dad to stop driving" was answered with the DVLA, his GP and a driving
# assessment - advice about this very conversation, which is what the person was asking for - and
# the wording card that took its place was a script for criticising somebody's pastry. It has to
# be said to somebody, though, or be *their* person ("your instructor"): a dentist in the last
# sentence of a card about bad breath, or the registrar in the second sentence of a card about
# wedding costs, is not what that card is about.
A_PERSON = (r"(?:gp|doctor|doctors|dentist|school|college|university|instructor|examiner|teacher"
            r"|tutor|head of year|manager|boss|employer|hr|personnel|union|careers|adviser"
            r"|advisor|consultant|council|citizens advice|solicitor|landlord|letting agent|vet"
            r"|pharmacist|midwife|health visitor|social worker|ombudsman|registrar|therapist)")


SAYING_IT_TO = re.compile(
    r"\b(?:ask|asked|asking|tell|telling|speak|speaking|talk|talking|ring|phone|call|email|write"
    r"|raise it|mention|sit down|take it|bring it up|have a word|report|complain)"
    r"\b[^.!?]{0,60}?\b" + A_PERSON
    + r"\b(?!['\u2019]s)",
    re.I)


YOUR_PERSON = re.compile(r"\byour\s+" + A_PERSON + r"\b(?!['\u2019]s)", re.I)


_TWO_SENTENCES = re.compile(r"\s*(?:[^.!?]*[.!?]){1,2}")


def _puts_it_to_someone(reply):
    """True when the reply already says how to put this to a person rather than what the thing is."""
    words = " ".join(str(reply or "").split())
    if not words:
        return False
    found = _TWO_SENTENCES.match(words)
    opening = found.group(0) if found else words
    return bool(SAYING_IT_TO.search(opening) or YOUR_PERSON.search(opening))


def _the_ask_is_for_words(reading):
    """True when this line asks what to say rather than what to do (see `compose.fit`)."""
    try:
        return shapes.asks_for_words(reading)
    except Exception:  # noqa: BLE001 - a reading this shape cannot use answers nothing here
        return False


def _respond(text, memory):
    if isinstance(text, str):
        verse = _the_verse_said_again(text, memory)
        if verse:
            return verse
    if isinstance(text, str):
        # A kind of cake, asked about after a bake was named: "im thinking of baking a cake" then
        # "what about a carrot cake" reached the carrot entry, which is a side dish, and "what
        # about lemon drizzle" reached the entry about drizzling a sauce over a joint. Written
        # out as the how-to the cake entries answer, the line keeps the bake the person is in.
        baked = baking.written_out(text, memory)
        if baked and baked != text:
            asked = understand(baked, memory)
            item, reply = _offer(lambda reject: find(asked, reject=reject), memory, asked)
            # Only a reply that answers the cake: "what about a coffee cake" right after the
            # sponge method earns "Same as before: ..." - the answer already given with a lead-in
            # on it - where the entry the line reached on its own was better.
            if item is not None and reply and not _already_on_the_screen(reply, memory):
                return reply
        # What to wear, asked after the occasion has been said: "im not sure what to wear" and
        # "and what about shoes" carry no occasion of their own, so on their own they were a
        # feeling read back and a search hedge. Written out with the thing on the table - "what
        # should i wear to a wedding" - they reach the outfit answer the entries hold.
        # The card is already on the screen and the line asks about one thing in it: "will black
        # be alright" after an answer that said black or dark colours are the thing. The sentence
        # that names it is the answer, and it is handed over as it was said.
        covered = outfit.the_sentence_answered(text, memory)
        if covered:
            return covered
        outfitted = outfit.written_out(text, memory)
        if outfitted and outfitted != text:
            asked = understand(outfitted, memory)
            item, reply = _offer(lambda reject: find(asked, reject=reject), memory, asked)
            if item is not None and reply and not _already_on_the_screen(reply, memory):
                return reply
        # One attribute of the thing on the table, asked on a line of its own: after "im making
        # bread" the person's next line is "and the oven temperature", which names no thing and
        # reached the oven repair card ("the heating element is almost always the fault"); after
        # "she wants a bike" the line "which size" reached the women's clothes chart. Written out
        # with the thing on the table, "oven temperature for bread" and "what size bike do i need"
        # are the questions the entries answer.
        attributed = said_topic.attribute_of_the_thing(text, memory)
        if attributed and attributed != text:
            asked = understand(attributed, memory)
            item, reply = _offer(lambda reject: find(asked, reject=reject), memory, asked)
            if item is not None and reply:
                if _already_on_the_screen(reply, memory):
                    # The attribute is one the answer already gave: "im roasting a chicken" was
                    # answered with the timing, and "and the timing" asks for it again. It is
                    # given again and framed as the repeat it is, rather than leaving the turn to
                    # the quantity reader, which answered a length of time with how much meat.
                    return repeat.pick(same_again.SHORT_AGAIN, memory,
                                       text).format(reply=reply)
                # An entry's sentence can open on a lower-case word ("about 1 hour 40 at 190C for
                # a 2kg joint or bird."), which is a fragment on a line of its own.
                return reply[:1].upper() + reply[1:]
    if isinstance(text, str) and trips.the_bag_beats_the_list(text, memory):
        # "what should we pack" about a trip in October is the trip's line: the store knows the
        # place and the month ("Pack light for the Lakes in October - a waterproof, something
        # warm..."), and this module's warm-week list answered a cold place with cotton tops and
        # swimwear. Every other month keeps this module's answer: high summer and the cold months
        # its lists do know, and where a place has no entry of its own the store's bag is reached
        # anyway, so standing down there only cost the answer a turn ("were going to cornwall in
        # july" lost its bag to a search hedge).
        return None
    if _only_the_office(memory):
        # The answer the entry would give is about the office rather than about the word the
        # person is waiting for, so the turn goes to the summons pool (`greeting`).
        return None
    if isinstance(text, str):
        # A verdict on the present the chat already listed is answered here, before any entry
        # reads the words of the line: "my nephew is 5 in june" / "what can i get them" / "would a
        # scooter be too much" reached the repeat reader, which said "Everything about a scooter
        # is in what I said above" - the list again, in a sentence about the chat instead of the
        # present. The row stands down unless the age is held and the thing named is a pick that
        # age's answer already offered, so every other verdict ask keeps the answer it had.
        verdict = shopping.the_verdict_on_a_present(memory, understand(text, memory))
        if verdict:
            return verdict
        # "make it longer" after a story or a poem is the verse just given with another part on
        # the end. Every reader below treats it as the verse said again ("Nothing separate for a
        # longer - it is the same advice"), as the hair-growth card, or as the search hedge, so it
        # is answered here first, on the typed line, the way the verdict on a present is.
        longer = entertainment.the_verse_longer(text, memory)
        if longer:
            return longer
        # "one more about the moon" after a poem about the moon is another poem about the moon, in
        # the form just given: the phrase names a subject and no form, so no row reads it as a
        # request and main said "Got it - one more about the moon."
        another = entertainment.the_next_verse(text, memory)
        if another:
            return another
    # A limit on a present is settled first, before anything reads the amount as something else:
    # "my budget is 30 pounds" after "a present for my sister" is the price of that present, and
    # the store reads a figure back, which is the right answer to the same line in a chat that is
    # not buying anyone a present. The gate is the cheap shape of a limit, so this costs nothing
    # on the lines that are not one.
    if isinstance(text, str) and LIMIT_SHAPE.search(text):
        priced = _the_present_with_a_price(text, understand(text, memory), memory)
        if priced:
            return priced
    if (isinstance(memory, dict) and mem.last_module(memory) == "answers"
            and isinstance(memory.get("understood"), dict)
            and mem.asks_only(memory["understood"])
            and not memory["understood"].get("change_of_subject")
            and asked_kind(text) in ("amount", "money")
            and re.search(r"\bhow much\b", str(text or ""), re.I)
            # A line that names the cost is asking about a thing, and the subject written into it
            # ("how much would the dog cost") reaches the price row. The answer last given can be
            # a sentence with the yearly cost in it, and handing that back would answer a
            # different question - the running cost of the dog for the price of getting one.
            and not re.search(r"\b(?:cost|costs|costing|price|prices|charge|charges)\b",
                              str(text or ""), re.I)):
        stated = same_as_before(memory["understood"], memory)
        # Only a sentence with a figure in it answers a how-much line. The shared-word reader
        # can hand back the steps instead ("divide the total by the weeks left" shares "week"
        # with the line), and that sentence was already read: the money readers below have the
        # figure this line wants, so leave the turn to them.
        if (stated and re.search(r"\d", str(stated))
                and flat(stated) != flat(mem.last_bot(memory) or "")
                and (SIGNALS["money"].search(stated) or SIGNALS["amount"].search(stated))):
            # The reader can hand the answer back behind a repeat lead-in ("Same answer, and it
            # covers this: ..."). A how-much line is owed the figure, not a pointer to where it is
            # on the screen, so the frame comes off before the sentence is read.
            if _REPEAT_OPENS.match(str(stated)):
                stated = _REPEAT_OPENS.sub("", str(stated)).lstrip(" :,-")
            # `same_as_before` cuts the answer to the clause that matched. When that clause is
            # inside the answer the person just read, the whole sentence around it says more and
            # is still the same answer: "The limit ... 6g of salt a day." lost the level teaspoon
            # and the 8g most people eat. The sentence is preferred to the cut, and to a repeat
            # frame, which is never the answer to a how-much line.
            whole = _the_sentence_around(stated, mem.last_bot(memory) or "")
            # Only widen when the rest of that sentence says something with a figure of its own:
            # the salt clause lost "most people eat 8g", while the water and melatonin clauses
            # already carry the figure asked for and reading more of the paragraph is the repeat
            # the arbiter passes over.
            if (whole and re.search(r"\d", whole[len(stated):])
                    and not _REPEAT_OPENS.match(whole)):
                return whole
            return stated
        # The bare ask has no words for the shared-word reader to match, so nothing came back.
        # The figure on the screen is still the answer to it: "A banana is about 105 calories"
        # after "how many calories in a banana" / "how much" is what the person is asking for,
        # and it is said plainly rather than behind a "Same as before" pointer at the card.
        same = (_the_sentence_with_a_figure(mem.last_bot(memory))
                if _A_BARE_MEASURE.fullmatch(str(text or "").strip()) else "")
        if same and not _REPEAT_OPENS.match(same):
            return same
    if _asks_who_the_bot_is(memory.get("understood"), text):
        # The bot's own identity is not a fact about the world: `greeting` answers it (who it is,
        # what it can do, where it lives). Nothing in the knowledge base is about it, and the
        # readers below that draw on the last answer - the bare ask, the dish plan, the part cut
        # out of it - all read a subjectless question as being about what was just discussed.
        return None
    if isinstance(text, str) and PLAN_RECALL.search(text) and _keeps_a_plan(memory):
        # "what was I planning?" is the plan said back, not the plan advice.
        return None
    if limit.reads_the_answer(text, memory):
        # The line limits the answer just given: the memory lane answers it from that answer's
        # steps, and re-asking the knowledge base with the limit appended is how "ants with a cat
        # in the house" reached the entry about rehoming a pet.
        return None
    if tried.might_be_a_report(text) and tried.pool_for(text, memory):
        # "i tried that and it didn't work", "still blocked": the person is reporting on the
        # answer just given, not asking for it again. Handing the same instructions over is the
        # one thing a friend never does, so the follow-up goes to `chat`, which says the next
        # step (`bot/memory/tried.py`).
        return None
    if returned.pool_for(text, memory):
        # "the smell came back after a week": the answer has not held and it already names the
        # step for that point, so re-answering the words is wrong twice over - it either repeats
        # the answer or swaps to an entry about one word of it ("i scrubbed it with bleach and it
        # came back" reached the bleach-or-vinegar comparison). `chat` says the step
        # (`bot/memory/returned.py`).
        return None
    if length.only_a_length(text) and ack.reply(text, memory):
        # "its been like that for about a week" after the answer: how long it has been going is
        # news about that answer, not a new ask and not a part of the answer to cut out. The
        # repeat machinery here reaches the same entry and says the paragraph again, which is
        # what the person has just read; the store replies with the question a length asks.
        # Passed only when the store has that reply, so a length this module does answer keeps
        # its answer.
        return None
    if mem.facts.a_name_picked(text, memory):
        # "we got a kitten" / "what should we name her" / "pepper": the word is the name they
        # chose, not a thing to look up. The store keeps it and says it back, and an entry about
        # peppers answers the word while missing the question - which is the one the bot asked.
        return None
        return None
    if about_the_chat(text):
        # "how did we start?" is a question about this chat, not about the dish on the table.
        # The memory store answers it from the turns; a fact entry answering it ("the chicken
        # takes an hour forty") is the knowledge base talking about the wrong thing.
        return None
    if taste.asks_about_a_taste(_the_line_as_said(text)):
        # "do i like curry and rice?" is a question about them, and the store keeps the answer.
        # An entry about rice answers the word, not the question: the person asked what they
        # like, and a recipe is about the food.
        return None
    if recall.ask(text) and not HOW_TO.search(_flat(text)):
        # "and where do i work", "what was my name", "what do i do for a living": the line asks
        # for one of their own facts, and the store has it. An entry answers the words it shares
        # with the question instead: "and where do i work" after a night shift reached the rota
        # and answered "the law gives you 11 hours off between shifts", which is not where they
        # work. The recall is the store's, and no fact entry is about them.
        # A how-to is a request even when it names one of their own things: "how do i live on a
        # budget" reads as a recall to ask() because live and budget are both subject words, and
        # the store has nothing to hand back for it.
        return None
    if taste.only_a_taste(_the_line_as_said(text)) and not _a_pick_is_asked(text):
        # "i like dogs but i hate cats" is a preference, not a household: an entry about
        # introducing a dog to a cat answers the two animals and the word "hate" in the line, and
        # told the person to keep their (nonexistent) pets behind a baby gate. The store says the
        # taste back, which is what the line is.
        # A diet is the one taste that is also a constraint on what to cook: "im vegetarian and i
        # dont eat dairy" was said back as "good to know", when the useful answer is a dinner
        # that is both and the labels that break it. The diet table is asked first, and a line it
        # really answers goes on to the entries.
        read = memory.get("understood") if isinstance(memory, dict) else None
        if not isinstance(read, dict):
            read = understand(text, memory)
        if not (dishes.has_a_diet_reply(memory, read)
                or dishes.has_a_dislike_reply(memory, read)
                or _a_choice_with_one_thing_left_out(text)):
            # A taste about a thing the entries answer by *choosing* is a constraint on the
            # choice, not a taste to file away: "i dont want a scary film" is asking for a film
            # without the scares, and standing down handed it to the store, which said it back
            # ("Noted: you don't want a scary film") while the gentle list sat one entry away.
            # A taste about a thing they own or meet ("i hate cats") is still the store's, which
            # is why the line has to name what is being chosen as well as what is left out.
            return None
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = understand(text, memory)
    # "will they get on?" after a new kitten and an older cat names neither animal. The
    # store knows both, so it can turn the line back into the question it is about before a
    # last-answer reader treats it as more talk about the older cat's health checks.
    introduction = mem.introduction_question(text, memory)
    if introduction:
        intro = understand(introduction, memory)
        item, reply = _offer(lambda reject: find(intro, reject=reject), memory, intro)
        if item is not None:
            return reply
    if _the_food_they_do_not_eat(text, understood):
        return None
    if _store_keeps_the_line(text, understood):
        # "my budget is 400 pounds" hands the store a value and "whats my budget" asks it for
        # one, so an entry about budgeting is answering the wrong question. The store says the
        # value back ("Your budget is 400 pounds") and the recall ("Your budget is £500"), which
        # is the reply the person wanted. Only when the slot the store reads is one of the
        # entry's own words: "im 34 and thinking of going back to uni" states an age, and the
        # answer about university is still the right one.
        return None
    if isinstance(text, str) and RECALL.search(text) and not recall.asks_for_a_word(text):
        # "What did I say my budget was again?" is a question about the conversation, and the
        # memory store answers it better than any entry: read with the topic written back in
        # ("... used car"), the knowledge base would answer the topic instead of the question.
        #
        # "What do you call a baby goat" is not that question: it wants the word the world uses
        # for a thing, and the entry that holds the word was stood down here on "what do you
        # call". The article is what tells the two apart - a recall points at what was said
        # ("what did i call my cats", "what do you call them") and a thing is named with "a" or
        # "an" - so that shape is read as the entry's ask.
        return None
    # "thanks, that helps" in the middle of a thread is a thank you, and the chat module has the
    # reply for it. Read as a follow-up it picks up the topic's words instead and answers the
    # question it was thanking us for a second time ("my cat died last night" then "thanks, that
    # helps" got the cat-sleep fact). Nothing in the knowledge base is about a bare thank you.
    #
    # A thank you with a question after it is still a question: "thanks, one more thing - how do
    # i clean the oven" reads as a question because it is shaped like one, and the oven question
    # after it is not thrown away with the thank you. A thanks line that only carries an ask word
    # it does not ask with ("thanks, that explains the boiler" carries "explains") is still a bare
    # thank you, which is the reading `_a_bare_thanks` asks for.
    if _a_bare_thanks(understood):
        # A thank-you in front of a line of its own is that line, not a thank you: "cheers. also im
        # skint till friday and theres nothing in the fridge" is the money line, "thanks. my back
        # has gone" the back one. Read whole, the thank you came first and the knowledge base
        # stood aside for it, so the turn went to the chat module's "Happy to help." and what the
        # person asked after the ack was dropped - which is how a "cheers." turns a question into
        # a shrug. The ack is cut off and the rest read as the line it is; a line that only closes
        # the turn ("thanks, that helps") has nothing after the ack, and one that agrees to try
        # something ("thanks, ill try that tonight") belongs to the chat module.
        rest = repeat.after_an_ack(text) if isinstance(text, str) else ""
        reread = understand(rest) if rest else None
        if (not isinstance(reread, dict) or reread.get("agrees_to_try")
                or reread.get("kind") in (None, "thanks", "greeting", "empty")):
            return None
        text, understood = rest, reread
    # A diet named in the middle of a meal being planned is about the dish, not a fact to say
    # back: "what should i cook" then "she doesnt eat meat" wants the vegetarian dinner. The
    # same words in a line of their own are the memory store's ("Your mum doesn't eat meat."),
    # so the plan only steps in front of it once it has answered with food.
    # "is it done" while something is in the oven asks when it is cooked, and the plan's own
    # `done` sentence says exactly that ("the juices from the thigh run clear"). The dish
    # follow-up just below answers a planned dish with the whole plan instead - "20 minutes per
    # 500g plus 20 minutes" - which is the timing said a second time: "how do i roast a chicken"
    # then "is it done" got "Same as before: About 20 minutes per 500g..." on main, while the
    # foods with no plan of their own already got their doneness sentence. The doneness ask is
    # answered from the food's own sentence first, and the plan answers the rest.
    # A line that says a food was left out on the side is a food-safety line, whatever the talk
    # before it was about: "i left the chicken out for a few hours", "can i still cook it" and
    # then "i left the mince out all night" was answered with a recipe for the mince - the dish
    # follow-up read the third line as being about the meal the talk had been on. The leaving
    # rule's own answer is the one that belongs on that line.
    left_out = freshness.says_a_food_was_left_out(text)
    if not left_out:
        # "can i still cook it" after "i left the chicken out for a few hours" is the leaving
        # question again, with the food and the hours left in the line before: the verdict is the
        # answer, and it is given before the dish follow-ups below, which read the line as being
        # about the meal and hand back a recipe for the food the bot just said to bin.
        verdict = freshness.the_still_ok_follow_up(text, memory)
        if verdict:
            return verdict
    if not left_out and dishes.ask_kind(understood or {}) == "done":
        readied = dishes.follow_up(memory, understood)
        if isinstance(readied, str) and readied.strip():
            return readied
    if not left_out and _a_dish_was_offered(memory):
        planned = cooking.follow_up(understood, memory)
        if isinstance(planned, str) and planned.strip():
            return planned
    if _someones_else_diet(text, memory, understood):
        return None  # the memory store says it back with the person's name
    if _asks_about_their_taste(text):
        # What a visitor likes or hates is kept against that person, and a dish is no answer to
        # it: "and what does she not like" after "she's vegetarian and cant stand museums" came
        # back as the meat-free dinner.
        return None
    calculated = solve(text, understood, memory)
    if isinstance(calculated, str) and calculated.strip():
        return calculated
    if _filling_in_an_emergency(understood, memory):
        # The person is talking, not asking: the modules for the person take the turn.
        return None
    # "it started when i moved house" says when the thing the bot has just answered began, and the
    # clause is the cause, not a new subject: without this, `house` is a kind of music and the
    # person is told about Daft Punk instead of about their sleep. The reading passes on every
    # line that is not an onset statement, and on a body complaint (a move that hurt their back
    # is a lifting injury).
    began = onset.reply(text, memory)
    if began:
        return began
    # "something quick please", "and no cheese either", "she doesnt eat meat": the next line
    # often only narrows the dish already on the table, which no entry and no single line of
    # the pantry can see. The plan kept in memory answers it, and passes when it cannot.
    # "i need something for a headache" asks for what helps the headache, and "something" is the
    # one word no entry is keyed on, so the pain, the burn and the cough all missed and the line
    # was read as a request for a suggestion ("Something for a headache? Tell me what you've
    # enjoyed before and I'll suggest something."). Asked as the question the tables know, the
    # problem is answered. It runs before the meal ideas because "i need something for a headache
    # fast" was a dinner: the "fast" is how soon they want help, not what they want to eat. On a
    # line with no answer of its own this changes nothing.
    helped = _something_for(text)
    if helped:
        again = understand("what helps " + helped, memory)
        other, said = _offer(lambda reject: find(again, reject=reject), memory, again)
        if other is not None and isinstance(said, str) and said.strip():
            # "can i give my baby anything for a cold" captures only "a cold", so the baby never
            # reaches the check in _something_for and the re-asked line ("what helps a cold")
            # answered the grown-up question - honey in warm water, which a baby must not have.
            # The give is what makes the person the patient, so the line's own reading is asked
            # first and kept when an entry answers it: the child-cold, the child-fever and the
            # child-cough rows own those lines, and a line the tables only know as a grown-up
            # problem ("can i give my son something for a sore throat") still gets the problem's
            # answer from the re-ask, as it did.
            given_to = SOMETHING_FOR_GIVEN_TO.search(_flat(text).lower())
            if given_to:
                own, own_said = _offer(lambda reject: find(understood, reject=reject), memory,
                                       understood)
                if (own is not None and own is not other and isinstance(own_said, str)
                        and own_said.strip() and _keyed_on_the_person(own, given_to.group(1))):
                    return own_said
            return said
    planned = (None if left_out else
               cooking.follow_up(understood, memory) or cooking.first_plan(understood, memory))
    if isinstance(planned, str) and planned.strip():
        return planned
    # A place word the line uses as a name is a name, not the city: the narrowed reading is the
    # one the rest of the turn uses, and nothing below may put the place back.
    reading = _without_names(understood)
    asked = _reword_ask(text)
    if asked is not None:
        if not asked:
            # "make it shorter" with nothing after it: the sentence is the one just handed over.
            before = _last_rewrite(memory)
            if before is None:
                return ("Paste the words you want to send and I'll soften them: who it is going "
                        "to helps too.")
            asked, tones = before
            return _rewritten(asked, tones | _tone_of(text), from_followup=True)
        return _rewritten(asked, _tone_of(text))
    # "shorter", "and friendlier" after a rewrite are about the sentence just given back.
    short_line = len(_flat(text).split()) <= 4
    if short_line and CONTINUED.search(_flat(text)):
        before = _last_rewrite(memory)
        if before is not None:
            asked, tones = before
            return _rewritten(asked, tones | _tone_of(text), from_followup=True)
    # The thing this line names for itself, if it names one: a line that opens its own subject is
    # not a follow-up about the last one.
    own = _own_thing(understood)
    # "how long do i cook it for" after "how long does cooked chicken last" is the method
    # question about the same food, not the keeping one again: the keeping answer has no
    # cooking time in it, and the part-taker below was trimming it to "3 days". The food is
    # what the conversation is on, so the line read with the food put back in reaches the
    # entry that knows the pan.
    cooked_ask = _a_cooking_ask_after_a_keeping_answer(understood, memory)
    if cooked_ask:
        return cooked_ask
    # A line that points back at the food instead of naming it ("what can i make with them",
    # "what should i do with it") has no food of its own for the pantry to work from, so it got a
    # list of quick dinners or a shrug. Read it as the earlier food plus these words, answer for
    # that food, and leave out what was just said so the follow-up is not the same words twice.
    pointed = cooking.pointed(memory, understood)
    # A side question pointed back at the dish ("what should i have with it") is that dish's own
    # side, not another dinner: the pantry read "pasta" out of a pasta bake and answered aglio e
    # olio, which is the bake over again. The plan already has the side, so hand it over here.
    if (pointed is not None and pairing(text)
            and cooking.SIDE_ASKS.search(_flat(text).lower())):
        side = cooking.side_for(memory, _flat(text))
        if side:
            return side
    if pointed is not None:
        said = tuple(text for text in (cooking.recent_replies(memory) or (mem.last_bot(memory) or "",))
                     if text)
        # A fresh dish first, then any other idea; a second way of saying the same dish beats a
        # shrug, so the food is never dropped just because everything was said once.
        picked = (cooking.dish(pointed, avoid=said)
                  or cooking.meal(pointed, avoid=said, pointed_back=True))
        if not (isinstance(picked, str) and picked.strip()) and not pointed.get("new_dish_only"):
            # Everything the table has for this food has been said already. The same dish again
            # is still better than "I'm not sure about that one" - "i have leeks" then "what can
            # i do with them" has nothing else to offer - but said flat it reads canned, so the
            # one we are going back to says so. A line that asked for a *second* idea is the one
            # case where the same dish is not an answer.
            picked = cooking.dish(pointed)
            if not (isinstance(picked, str) and picked.strip()):
                again = cooking.meal(pointed)
                if isinstance(again, str) and again.strip():
                    picked = (("The one I'd go back to: " + again[0].lower() + again[1:])
                              if again in said else again)
        if (isinstance(picked, str) and picked.strip()
                and not cooking.unusable(picked, pointed)):
            return picked
    # "Can I eat satay?" a turn after a peanut allergy is a yes or a no about peanuts, and that is
    # what they told us, not a new subject: the store answers it before any entry does, because an
    # entry about satay says how to cook it and no entry is about their allergy at all.
    suits = cooking.suits_them(understood, memory)
    if isinstance(suits, str) and suits.strip():
        return suits
    # A food somebody at the table will not eat is a limit on the dinner in the same words as an
    # allergy, and a line that names one and asks what to cook is the pantry's, before the food's
    # own card: "she wont eat cheese what can i cook" got cheese's calorie figure, and "my wife
    # wont eat bread what can i cook" the loaf's method, which is the one thing they cannot use.
    # Only where the pantry has a dinner to give: a bare "my daughter hates cheese" keeps its
    # substitute answer, because the kitchen has no dinner to suggest from it.
    without = cooking.a_dinner_without(understood, memory)
    if isinstance(without, str) and without.strip():
        return without
    # A line naming two or more things from the kitchen asks about the combination, and the
    # pantry table knows the dishes that use those things together: no entry does, because an
    # entry is keyed by one dish or one problem. One ingredient on its own is left to the
    # entries, which say more about it than a single dish can.
    named_foods = cooking.ingredients(reading)
    # Two foods are a "what can I make" question only when the line is asking for a meal: "is
    # oat milk gluten free" names oat milk and milk, and the dinner built from them answered a
    # yes or no with a bowl of porridge. A fact about the food is the entries' question.
    if len(named_foods) > 1 and not cooking.asks_a_food_fact(understood):
        # Two foods named in one line is a "what can I make" question, and it wants a meal: the
        # storage and safety entries answer a different question, so they wait until the dish and
        # the ideas have both passed ("ive got chicken and spinach in the fridge").
        cooked = (cooking.dish(understood, memory)
                  or cooking.meal(understood, memory=memory))
        # The kitchen the line describes is part of the line: a dish that needs the oven is no
        # dish at all to someone whose oven has broken ("chicken and rice and no oven").
        if isinstance(cooked, str) and cooked.strip() and not cooking.unusable(cooked, understood):
            return cooked
    # A meal idea we gave last turn states its own time, so "how long does that take" is a
    # question about our answer and the time in it is the reply. It runs before the entries,
    # because a word from the first line can win one of those instead: "i have chickpeas and
    # spinach in the cupboard" then "how long does that take" reads the cupboard, and the
    # cupboard-cleaning entry answers a question about a dinner.
    # A bare keeping question ("can i still eat it") after a line about a food of its own is
    # about that food, not about the last dish the store heard of: see the docstring.
    about_the_food = _keeping_about_the_food_there(memory, understood)
    if about_the_food:
        return about_the_food
    amount = _amount_asked(text, memory)
    if amount:
        return amount  # the figure for the amount this line names, not the one already given
    again = _the_amount_they_named_again(text, memory)
    if again:
        return again  # the size the answer already worked out, said in its own sentence
    # The same follow-up with "keep" in it wants the keeping fact, not the cooking time: twenty
    # minutes is how long the dish takes, and "how long does that keep" is a different question.
    # A food with its own keeping answer keeps it ("how long does that keep" after a boiled egg
    # wants the week an egg keeps, not the days any cooked dish does). This is tried before the
    # dish rule below, because that rule stands aside when the answer just given already carries
    # a keeping word: after "how do i store bread" the loaf's own answer is the answer, and the
    # general fridge table that would otherwise win tells people to keep a loaf in the fridge.
    if cooking.keeping_ask(understood) and _asks_storing(memory):
        specific = _keeping_entry(text, memory, _keeping_thing(memory), storing=True)
        if isinstance(specific, str) and specific.strip():
            # The storing answer is given out again when the food has no figure anywhere else,
            # and that is no use for the question asked: "how do i store bread" then "how long
            # does that keep" said the same paragraph twice, with no "3 days" in it. So when the
            # dish table knows the thing and keeps a figure for it, that figure is the answer.
            planned = _the_plan_keeps(understood, memory)
            if planned and _opening(planned) != _opening(specific):
                return planned
            return specific
    kept = cooking.keeping_followup(understood, memory)
    if isinstance(kept, str) and kept.strip():
        specific = _keeping_entry(text, memory)
        if isinstance(specific, str) and specific.strip():
            return specific
        planned = _the_plan_keeps(understood, memory)
        if planned:
            return planned
        return kept
    ours = _the_dish_time(understood, memory)
    if ours:
        return ours
    timed = cooking.timing_followup(understood, memory)
    if isinstance(timed, str) and timed.strip():
        return timed
    # A repair question about the machine the line before was about ("washing machine smells of
    # damp") is answered by that machine's own rule, before the part reader can cut a sentence
    # out of the answer just given.
    repaired = _the_machine_follow_up(text, reading, memory)
    if repaired:
        return repaired
    # An announcement that asks about cooking the dish in the same line ("im making a big
    # lasagne tonight, how long in the oven") is both things at once, and the plan is the
    # answer to both: the entry that fits the words is a category one (the pasta-bake method
    # bakes it 20 to 25 minutes at 200C, where this lasagne takes 35 to 40 at 180C). It runs
    # before the part reader, because that one reads the part out of the *previous* answer: a
    # pasta bake's 200C cut down to "200C." is not the lasagne's heat.
    if not _care_holds(text, memory):
        announced = dishes.announced_part(memory, understood)
        if announced:
            return announced
    # The part of the last answer is the answer only when the line asks about that answer. A
    # line that names a thing of its own is a new question: "can i freeze lasagne" after "can i
    # freeze cream" came back with the sentence about cream, because "freeze" was the one word
    # the two lines had in common. A line that only asks for a property ("what temperature?")
    # names no thing of its own however its words are read, so it is still about the answer.
    # A line that asks about a whole day or week asks about the period, not about the figure in
    # the answer before it: "how much sugar should i have a day" straight after a can of cola
    # came back as "A 330ml can of regular Coke has 35g of sugar." - the can's figure cut out of
    # the last answer, where the question is the daily limit and its own entry has it.
    # A follow-up that names another meal ("and for lunch") is the same question about the meal it
    # names, not a part of the answer just given: after a dairy-free breakfast it came back with
    # the breakfast list again. It is read with its own meal in it and answered as itself.
    meal = mem.meal_follow_up(understood, memory)
    if meal is not None:
        _meal_entry, _meal_reply = _offer(lambda reject: find(meal, reject=reject), memory, meal)
        if _meal_reply:
            return _meal_reply
    if _A_PERIOD.search(str(text or "")):
        asks_a_part = False
    else:
        asks_a_part = not (own and _new_thing(own, _the_run_said(memory, mem.last_bot(memory) or ""))
                           and not mem.asks_only(understood))
    if asks_a_part and named.asks_a_part_of_the_trip(text, memory):
        # A line that asks a part of the trip about the place in the chat asks its own question,
        # not for a slice of the card on the screen: after the card for a city, "how many days do
        # i need" was answered "The beach at Barceloneta for half a day." - the sentence of the
        # card that happens to hold the words "half a day", where the trip reader has the days
        # question for that place and the entry `city-stay` answers it.
        asks_a_part = False
    if asks_a_part and mem.answer_about(text, memory):
        # The line's words belong to an answer from earlier in the chat than the last one ("and
        # how long in the oven" after the cake, with a turn about the frosting in between). The
        # part it asks for is in that answer and the one just given is about the other thing, so
        # the entries answer the line rather than a part of the frosting.
        asks_a_part = False
    # A line the knowledge base answers on its own words is a question of its own, not a part of
    # the paragraph above it. "why do you want this job" after "how do i find a job" names no
    # thing with a possessive in it, so every gate above said "a follow-up", and the only word it
    # shared with the answer was "job": it was handed that answer's own sentence about jobs
    # ("Most jobs come through a person rather than a portal") where the interview row has the
    # answer to the line. The entries are asked before the part reader can cut a sentence out.
    # The line has to name a thing of its own for that: "how long does it keep" also has an entry
    # (the keeping row), and it is still a part of the answer just given - the lasagne card says
    # three months frozen where the line wants the three days the cooling answer gave.
    if asks_a_part and find(understood) is not None and understood.get("entities"):
        asks_a_part = False
    part = _part_asked(text, memory) if asks_a_part else None
    if part and cooking.keeping_ask(understood) and not FIGURE.search(part):
        # A keeping question is not a part of the answer just given when the figure in it is a
        # cooking time: "what can i make with eggs" then "how long do they last" cut the "2
        # minutes" out of the omelette recipe, which is how long it takes to cook, not how long
        # the eggs keep. The keeping answers have all been tried by now and had nothing, and a
        # sentence about days or weeks is the keeping figure the line asked for: "what can i do
        # with leftover chicken" then "how long will it last" was a shrug without it.
        part = None
    if part:
        # One part of the answer just given, not the whole answer again - with the detail the
        # line named in front of it when that part is already on the screen.
        return _the_part_said_again(part, text, understood, memory)
    again = _the_plan_said_again(understood, text, memory)
    if again:
        return again  # the same property asked again is answered again, not hedged
    earlier = _last_answer(memory)
    if (earlier and asked_kind(text) and _names_a_property(text)
            and _only_a_property(keywords(text))
            and not _a_property_word_names_a_thing(text)
            and not RATE.search(text)):
        # The line names a figure the answer just given does not have. Do not let a
        # different entry answer it with its own ("rest it" is not "roast 40 minutes").
        # A line that names a subject of its own ("what temperature for roast potatoes")
        # is a question for that entry, not this guard.
        plan = _the_plan_for(text, memory, understood)
        if plan:
            return plan  # the dish in the conversation states this part itself ("180C")
        # The figure the last answer lacks can still be the thing's own, and the line names the
        # thing only with its "that": "how much will that cost" after "we are going to rome" is
        # a question about the trip, and the trip's entry knows the cost. The words of the line
        # share nothing with the answer before it, so the key check below cannot see this; the
        # subject put back in is what reaches the entry, and the answer is the thing's own only
        # when that entry is about what the conversation is on.
        subject = mem.subject(memory)
        found, said = _the_answer_from_thing(text, subject, memory) if earlier else (None, None)
        if found is not None:
            # A thing the chat named after the subject answers instead of it: the second trip
            # is not priced with the first one's figure. A newer thing can only take the
            # answer away from the subject, never give one where the subject's entry has none
            # ("my boiler is making a noise" is not a price list).
            for thing in _the_things_to_try(understood, memory):
                if thing == subject:
                    break
                newer, newer_said = _the_answer_from_thing(text, thing, memory)
                if newer is not None:
                    return newer_said
            return said
        # It is still the same thing's question when the subject put back in reaches the entry
        # that answered last ("what temperature should the oven be?" after the cake timing), so
        # that entry may answer with the figure this line asks for.
        words = set(keywords(text))
        keys = set(earlier.get("keys") or ())
        if not words or not words <= keys:
            # The last answer's entry is not about what this line asks, but the line is still a
            # figure question about the answer just given: give the part of that answer that
            # carries the figure rather than a hedge. "i have an upset stomach" then "how long
            # does it last" reached nothing at all and was answered with a search, while the
            # answer on the screen says "it usually settles in two to three days". Only a line
            # that asks for nothing but the length takes it: one that names a thing comes back
            # here with no figure of its own, and the length before it is no fact about it.
            if not _asks_only_the_length(text):
                return None
            part = same_as_before(understood, memory)
            if part:
                return part
            # No sentence of the answer shares a word with "how long will that take" (a list of
            # steps for a blocked sink shares none), so there is nothing to quote: say that the
            # answer holds no time and give its first step, rather than hand the turn to a search.
            honest = _figure_missing(earlier.get("reply") or "", text)
            if honest:
                return honest
            return None
        fuller = _with_subject(text, memory)
        if fuller.strip() == text.strip():
            # The subject put back in ("how long will it take for the save for a house?") is not
            # this line's question when the line is a bare length ask about an action: the
            # string reaches an entry that shares a noun with it and answers something else.
            # Only an entry that answers a length may take the ask (_answers_a_length), and
            # _with_subject hands the written-out ask back only when there is one.
            fuller = text if mem.written_out(text, memory) else _about_subject(text, memory)
        same = find(understand(fuller, memory)) if fuller.strip() != text.strip() else None
        if same is None or not _is_about(same, mem.subject(memory)):
            # The ask written out with the action the chat is on takes the turn next, whatever
            # the answer before it was about: "im learning to drive" then "how long will it
            # take" is the driving entry's question, and the answer to the line before it was a
            # nudge. Only an entry that answers a length may take it (_answers_a_length).
            written = _written_ask_with_an_answer(text, memory)
            if written:
                fuller = written
            else:
                if not _asks_only_the_length(text):
                    return None
                part = same_as_before(understood, memory)
                if part:
                    return part
                honest = _figure_missing(earlier.get("reply") or "", text)
                if honest:
                    return honest
                return None
        reading = understand(fuller, memory)
    # A plan the conversation is cooking answers a follow-up about one of its parts, before the
    # entries do: "can I make it ahead" after "I'm cooking a pasta bake for eight people" is about
    # that bake, and the eight fits the party-hosting entry, which advises on a menu instead.
    # "keep" is here only when the line points back at the dish ("can i keep it in the fridge",
    # "how long will it keep"). One that names the food - "how long can i keep cooked chicken in
    # the fridge" - is a keeping fact, and the entry that knows it says more (raw 1 to 2 days,
    # cooked 3, go by the date on the pack) than the plan's one sentence does.
    PLAN_FIRST = ("ahead", "fill", "sides")
    kind = dishes.ask_kind(understood)
    words = {str(word).lower() for word in (understood.get("words") or ())}
    if kind == "keep" and words & {"it", "that", "this", "them", "they"}:
        # The plan's keep fact is what is left of a cooked dish, so it answers only when the
        # answer we are on was about cooking, or the thing the conversation is on has been
        # cooked. "raw chicken in the fridge" then "how long will it keep" was told the
        # leftovers keep 3 days, a day too long for raw meat, when the raw chicken answer
        # (1 to 2 days) is the one that belongs.
        if _the_plan_answers_this(memory) or _cooked_thing(memory):
            PLAN_FIRST += ("keep",)
    if (kind == "temp" and _the_plan_answers_this(memory) and _says_line(text, _OVEN_WORDS)
            and not _says_line(text, _OVEN_CHECK_WORDS)):
        # "what temperature should the oven be" in a cake chat asks for the cake's own figure
        # ("180C, or 160C in a fan oven"), and the oven-runs-hot card was taking it: setting the
        # oven is not a question about the oven being wrong. The line has to name the oven, so
        # "what temperature should the chicken be" keeps the internal 75C it asks for, and a
        # line about checking the heat keeps the card.
        PLAN_FIRST += ("temp",)
        # `own` here is the property the line asks for, not an entry, and it being set sent the
        # line to the card while the dish's figure was waiting.
        if own and str(own).lower() in _PROPERTY_WORDS:
            own = None
    if not own and kind in PLAN_FIRST and not _care_holds(text, memory):
        plan = dishes.follow_up(memory, understood)
        if plan:
            return plan
    # A detail about the thing in hand is answered about that thing or not at all, on every
    # reading of it below: the line alone, the line with its figure changed, the line read with
    # the topic beside it. One entry from another domain means the answer is to a different
    # question that happens to share the detail's words.
    off_topic = _off_the_topic(understood, memory)

    def _guard(reject):
        # The fence goes up when the chat's answer has a domain to be off, or when the line says
        # what the thing IS (a colour): both mean the line is about the thing in hand and an entry
        # from elsewhere is answering a question that shares its words. A detail that only says
        # what was done to it ("i painted it last year") names no subject of its own, so the entry
        # reached through the chat's own domain is the answer to it, which is what the bot gave
        # before the colour work and still does.
        if not off_topic[1] and not off_topic[2]:
            return reject
        return lambda one: reject(one) or _from_another_domain(one, off_topic)

    keeping = _keeping_reader(reading, memory)
    item, reply = _offer(lambda reject: keeping(_guard(reject)), memory, reading)
    if item is not None and item.id == KEEPING_FROM_THE_ANSWER:
        # The figure the answer just gave, handed back as it stands: the subject has drifted to
        # the last thing asked about ("cool", after "and how long do i cool it for"), so the
        # guards below would read the line against that word instead of against the answer.
        return reply
    if not own and (understood or {}).get("kind") == "statement":
        # A detail that narrows the trouble ("it's worse when I lie down", "it's sore when I
        # kneel") is still about the answer on the screen, and that answer usually holds the part
        # of it that speaks to the detail. Read as words it reaches the same entry again, whose
        # answer has just been given, so it is answered here before the repeat is dropped and the
        # turn goes to the chat.
        detail = _a_detail_answered(text, memory)
        if detail is not None:
            return detail
        # A figure the answer already speaks of is that answer's own sentence, not a shrug: "im
        # 34 and i want to run a 10k" then "i can do 5k now" was answered "I'm listening — say
        # more if it helps" while the answer on the screen said "If you can run 5k comfortably
        # now, eight to ten weeks is a realistic build."
        figure = _a_figure_the_answer_has(text, memory)
        if figure is not None:
            return figure
    if not own:
        # An ask that names only a detail of the thing the store holds is about that thing: after
        # "we got a puppy called Biscuit", "how do I stop the chewing" reaches the answer about
        # chewing a pen at a desk on its own words, and the puppy's own entry only when the kind
        # the store holds is read beside it. The memory decides that reading, and it is kept only
        # when it reaches an entry of its own - never the one the line alone already had.
        beside = the_thing_a_detail_belongs_to(understood, memory)
        if beside is not None:
            # The entry the stored kind and the detail were read together for is the only one
            # those words vouch for. When that entry is turned down, the next best card from the
            # same words is one the line itself never named, and it must not take the turn:
            # "my rabbit bites me when i pick him up" then "how long should i boil an egg" read
            # the egg line with the rabbit beside it, the cooking entry was refused, and the
            # rabbit's heat card answered a question about boiling an egg.
            vouched = find(beside)
            other, said = _offer(_keeping_reader(beside, memory), memory, beside)
            if (other is not None and vouched is not None
                    and getattr(other, "key", None) != getattr(vouched, "key", None)):
                other, said = None, ""
            if other is not None:
                if _said_before(said, memory) or _already_said(said, memory):
                    # The entry the detail belongs to has already answered - reaching it with the
                    # thing's kind read beside the line, or on the line's own words - and one
                    # detail of it is all this line names ("what about the chewing" after the
                    # chewing answer). The paragraph would come back word for word, so the detail
                    # is named in the lead-in and the part of it that answers is given instead.
                    again = _the_detail_said_again(said, text, memory)
                    if again:
                        remember_answer(memory, said, _key_words(other))
                        _remember_answer(memory, other, said)
                        return again
                if getattr(other, "id", None) != getattr(item, "id", None):
                    item, reply, reading = other, said, beside
    if item is not None and not own:
        # A follow-up names no thing of its own, so an entry about something else can take it on
        # its bare words: "and how long should i rest it" after a sore knee reaches the rest day
        # advice, and the knee never gets the line. The thing the conversation is on is what the
        # line is about, so the entry about that thing is taken instead - and only when it is
        # about that thing, so a line the other entry answers better is left alone.
        head = _head_thing(mem.subject(memory))
        # A line that names a food of its own is about that food, not the one on the table: "how
        # long do i reheat a pizza" after a chicken keeping answer was read with chicken put back
        # in and got the roast chicken's 20 minutes per 500g, where its own words reach the pizza
        # entry. The context entry only takes a line that names nothing but a property.
        other_food = _names_another_food(understood, str(mem.subject(memory) or "").lower())
        # A line asking what a word means is about that word, not about the talk: read with the
        # back pain of the turn before it, "what is an overdraft" took the lifting advice, and
        # "what is a recession" after a leap year took the leap year. The definition stands.
        defined = _a_definition_of_the_entry(text, item)
        if head and not other_food and not defined and not _is_about(item, head):
            other, said = _offer(lambda reject: _in_context(text, memory, reject=_guard(reject)),
                                 memory, reading)
            if other is not None:
                item, reply = other, said
    if item is not None and not own and not _about_the_talk(item, text, memory, reading):
        item, reply = None, None
    follow_up = False
    if item is None:
        # A follow-up that only changes a figure ("what about a 3kg one" after "how long do i
        # cook a 2kg chicken for") is the same question with the new figure in it. Read with the
        # earlier line's figure swapped out it reaches the entry the first line did, and the
        # entry works the new figure out from its own rule ("20 minutes per 500g plus 20").
        resized = resize.rewritten(text, memory)
        if resized:
            again = understand(resized, memory)
            # A headcount is worked out rather than looked up: "how much rice for 4 people" is
            # answered by the portion table ("75 g each, so 300 g for four") with no entry
            # behind it, so the corrected line has to be worked out the same way before an
            # entry is asked for it - the rice entry says 75 g a head and nothing about the
            # table of three, which is the number the person just changed.
            calculated = solve(resized, again, memory)
            if (isinstance(calculated, str) and calculated.strip()
                    and flat(calculated) != flat(mem.last_bot(memory) or "")):
                return calculated
            item, reply = _offer(lambda reject: find(again, reject=_guard(reject)), memory, again)
            if item is not None:
                # Not a follow-up in the repeat sense: the figure is new, so the answer is a new
                # one even though the entry and its rule are the same.
                reading, own = again, _own_thing(again)
        if item is None:
            if (ADDING_TO_THE_SUBJECT.match(text)
                    and not A_MEASURE_OF_THE_SUBJECT.match(text)
                    and _the_answer_was_about_the_subject(memory)):
                # "and what about holidays" adds a dimension to the thing on screen rather than
                # naming a new subject, so the thing is read with it before the earlier
                # question's shape is put back round it. Without this the long cat chat - "what
                # do i need", "how much does it cost", "what about holidays" - read the line as
                # "how much holidays", which is the paid holiday from work.
                other, said = _offer(
                    lambda reject: _in_context(text, memory, reject=_guard(reject)),
                    memory, reading)
                if other is not None:
                    item, reply = other, said
        if item is None:
            # A follow-up that only names a new thing ("what about a dessert") has no ask in it,
            # so no entry fits it on its own. Read as the earlier question with that thing in
            # place of the old one it reaches the entry the first line did - but only when the answer that
            # comes back is about the new thing, so a crumble answers a dessert question and the
            # dinner answer is never handed over as if it were.
            # The reading this has always used - the earlier question's word that its answer took
            # up - comes last, so an ordinary follow-up is read exactly as it always was. A repair
            # gets the other readings too: it says the earlier line had the wrong thing in it, and
            # that thing is not always the word the earlier answer took up. "how long does a
            # chicken take to roast" is answered with "20 minutes per 500g plus 20", which takes up
            # "take" and never says chicken, so "i meant a turkey" was read as "how long does a
            # chicken turkey to roast", reached nothing, and the person got "I'm listening - say
            # more if it helps" where the question in full gets the turkey's time. Worse, "how
            # long does chicken last in the fridge" takes up "fridge", so "i meant beef" swapped
            # the fridge and kept the chicken.
            older = swap.rewritten(text, memory)
            readings = swap.candidates(text, memory) if swap.is_repair(text) else []
            if older and all(read[0] != older[0] for read in readings):
                readings.append(older)
            if not readings and older:
                readings = [older]
            handed = None
            for swapped in readings:
                again = understand(swapped[0], memory)
                other, said = _offer(lambda reject: find(again, reject=_guard(reject)), memory, again)
                # An answer that is the paragraph already on the screen is turned down by
                # `names` (saying it again is not an answer about the new thing). It is the
                # answer, though, when the entry it came from is keyed for the word the follow-up
                # replaced: "what about the freezer" after the smell in the fridge reaches the
                # fridge entry, which is keyed for freezers too, and "what about the bathroom"
                # after ants in the kitchen reaches the ants entry, keyed on the kitchen.
                same_answer = (_already_said(said, memory)
                               and _written_for(other, swapped[1]))
                # An entry is about its subject and its answers do not always name it: the sink
                # entry says "rinse it after every wash-up" and never the word sink, so "and
                # under the sink" after the shower was turned down and the person got their own
                # words back ("Got it - under the sink"). An entry keyed for the new thing is
                # about it, whatever words its answer happens to use.
                thing = swap.thing(text)
                thing_words = set(re.findall(r"[a-z']+", str(thing or "").lower()))
                rest = " ".join(word for word in swapped[0].split()
                                if set(re.findall(r"[a-z']+", word.lower())) - thing_words)
                kept = _written_for(other, thing) and _more_than_the_thing(other, rest)
                if other is not None and (same_answer or kept
                                          or swap.names(swapped[1], said, text, memory,
                                                        question=swapped[0])
                                          or _about_the_rest_of_the_question(
                                              other, swapped[0], swap.thing(text))):
                    # That answer may be the one already on the screen, word for word: the entry
                    # is about the subject, so the same lines answer both rooms. Handing the
                    # paragraph back again is the bot repeating itself, so the rest of it comes.
                    if same_answer or _already_said(said, memory):
                        # Handing the paragraph back again is the bot repeating itself, so the
                        # part of it they have not read is what comes.
                        said = _same_where_they_asked(text, said) or said
                    item, reply, reading = other, said, again
                    handed = (other, said, again)
                    break
            if handed is None and _a_place_they_asked(text) and _a_place_of_the_same_kind(
                    earlier, text):
                # A place that no entry answers is still the place the answer they have was
                # asked about: "how do i stop condensation / and in the bathroom" reached the
                # bathroom's cleaning routine, whose answer is about a different job, and the
                # person was left with a search hedge while the advice about air and warmth
                # was one line above. What holds where they asked about is handed back, once,
                # under a lead-in that names it - and only the part they have not read.
                parting = _same_where_they_asked(text, mem.last_bot(memory) or "")
                if parting:
                    return parting

        if item is None:
            # A follow-up that only names a person ("what about my dad", "and something for my
            # brother") is the same question about somebody else: asked in full - "what should i
            # get my dad for his birthday" - it reaches an entry, while on its own it is a bare
            # ask and the person got the search hedge. The answer has to be about the new person,
            # which is checked by the old one not being in it and it not being the answer just
            # given said again.
            about_someone = swap.rewritten_person(text, memory)
            if about_someone:
                again = understand(about_someone[0], memory)
                other, said = _offer(lambda reject: find(again, reject=reject), memory, again)
                if other is not None and swap.names_person(about_someone[1], said, text,
                                                           mem.last_bot(memory)):
                    item, reply, reading = other, said, again
    # A follow-up about a part of a dinner plan is the plan's to answer, not the entry the line
    # reaches when it is read back with the dish put in: "how long should it be in the oven"
    # after "I'm cooking a pasta bake" reached the announcement and said the time again.
    PLAN_KINDS = ("fill", "sides", "done", "keep", "fix")
    care = item is None and _care_holds(text, memory)
    if item is None and not care:
        if dishes.ask_kind(understood) in PLAN_KINDS:
            # "And what should I put in it?" asks about a part of the plan, and the line as it
            # came in names no dish: read back with the dish put in ("I'm making a beef stew")
            # it reaches the announcement entry, which says the time it already said. The plan
            # answers the part, so it goes first.
            plan = dishes.follow_up(memory, understood)
            if plan:
                return plan
        if mem.asks_only(understood) and mem.last_module(memory) == "answers":
            # A line that only asks for a property ("how long?", "what temperature?") is a
            # question about what we are already talking about, not about a neighbour entry the
            # ask happens to fit: read with a subject put back in, "how long do I need?" also
            # reaches the boiled-potatoes entry after a tray of roast ones.
            # "how long do i cook it for" after "how long does cooked chicken last" is the
            # method question about the same food, not the keeping one again, and the keeping
            # answer has no cooking time to take out of it.
            cooked = _a_cooking_ask_after_a_keeping_answer(understood, memory)
            if cooked:
                return cooked
            # A line that names a food of its own is not asking about the one in the answer we
            # just gave: "how long do i reheat a pizza" after a chicken answer was handed the
            # chicken's figure out of that answer ("2 hours"), where the entry that knows pizza
            # has the 12 to 15 minutes. The bare asks ("how long?", "how long does it take")
            # name nothing, so they still take the figure out of the last answer.
            other_food = _names_another_food(understood, str(mem.subject(memory) or "").lower())
            if mem.has_time(mem.last_bot(memory)) and not other_food:
                said = same_as_before(understood, memory)
                if said and said != mem.last_bot(memory):
                    return said  # take the figure out of the answer we just gave
            # The answer just given has no figure for the property asked, and the entry that
            # gave it often has one: the same entry, asked with the line it leans on in front,
            # is the ask in its own words ("how long will that take" after the credit-card
            # answer is the payoff-length answer). Without this the line is read for an entry
            # of its own and a neighbour answers it - the travel-money entry, off the word
            # "take", told them what to carry abroad instead of what the debt takes.
            again = _the_entry_asked_again(text, memory)
            if again:
                return again
        if not care and mem.last_module(memory) == "answers" and _adds_a_figure(text):
            # The lines that add a figure to the answer just given - "it says 1.8 kilos" after the
            # per-kilo time, "we are 6" after the table for four - carry no ask and name no entry,
            # so the greeting echoed them back ("Got it - it says 1.8 kilos.") and the figure did
            # nothing. The entry that answered last is the one that knows what the figure means,
            # asked again with the line it leans on in front. Only when the figure is new to the
            # answer: "its 2 kilos" after the timing for a 2kg bird repeats the figure they were
            # just given, and a paragraph read out again is not an answer.
            again = _the_entry_asked_again(text, memory)
            if again and _new_figure(again, mem.last_bot(memory)):
                return again
            # The last answer had no figure in it ("180C, or 160C in a fan oven"), so the dish
            # plan is where the answer is: the plan says the whole thing in one sentence.
            if _the_plan_answers_this(memory) and not pairing(text):
                plan = dishes.follow_up(memory, understood)
                if plan:
                    # "what temperature?" asked twice is the same line in different words, so
                    # the count is of turns that already carried this sentence, not of turns
                    # that typed it: the answer comes whole with the same lead-in a repeated
                    # answer gets.
                    said = 0 if pairing(text) else _answer_said(plan, memory)
                    if said >= 3:
                        return AGAIN_HELP.format(reply=plan)
                    if said:
                        return AGAIN[said - 1].format(reply=_repeat_short(plan, text, memory))
                    return plan
        follow_up = True
        if WHEN_AM_I.search(text):
            # "when am i going" is a question about what they told us, not about the topic: read
            # with the topic put back in ("when am i going lisbon may") it reaches the trip entry
            # again and hands back the paragraph they just read. The plans memory answers it.
            return None
        # Nothing for the line on its own: a follow-up is about the last thing said, so the
        # earlier line it leans on is searched too (memory["understood"]["leans_on"]), with the
        # guards in lookup keeping a neighbour's entry out. Only after the line alone found
        # nothing, so an answer that fits stands.
        # A follow-up that names a food of its own is about that food: "how long do i reheat a
        # pizza" after a chicken answer was read with chicken added to it and got the roast
        # chicken's 20 minutes per 500g, where the line on its own reaches the pizza entry.
        # A follow-up that names another meal ("and for lunch") is the same question about the
        # meal it names, so it is read with its own meal in it before the earlier line is
        # searched: searched as it stands, the dairy-free breakfast and then "and for lunch" was
        # answered with the breakfast list again.
        meal = mem.meal_follow_up(understood, memory)
        if meal is not None:
            reading = meal
        other_food = _names_another_food(understood, str(mem.subject(memory) or "").lower())
        own_thing = _names_its_own_thing(text, memory)
        item, reply = _offer(
            lambda reject: find(reading, reject=_guard(reject),
                                use_context=not other_food and not own_thing),
            memory, reading)
        if item is not None:
            # A follow-up that asks how the subject turns out is answered by the row that
            # answered the line before it: "will it be alright" after the phone went in the sink,
            # "will it survive" after the laptop got coffee in it. The row has an answer of its
            # own for the ask when it declares one, and giving that is the whole turn - the card
            # itself has already been read out, and saying it again is the paragraph the person
            # is looking at. Without this the turn gave up and pointed at a search, over a
            # subject the bot had answered a turn before.
            owed = _the_outcome_owed(item, text)
            if owed and (_said_before(reply, memory)
                         or names_nothing_of_its_own(reading)):
                return owed
        if item is not None and _said_before(reply, memory):
            # The entry the line reaches with the topic behind it is the one that gave the answer
            # already on the screen: what the line asks is a part of it the store can ask for, out
            # loud, in the words the row is kept in. "i have a cough" then "will it go away on its
            # own" is the cough's own row about how long it lasts, and the store holds that
            # reading - the cheap answer here read out the cough answer a second time, and the
            # turn after it was a search hedge.
            wider = mem.followup_reading(understood, memory)
            if isinstance(wider, dict) and wider is not understood:
                wider_item, wider_reply = _offer(
                    lambda reject: find(wider, reject=_guard(reject)), memory, wider)
                if wider_item is not None and wider_item.key != item.key:
                    reading, item, reply = wider, wider_item, wider_reply
        if item is not None and not _about_the_talk(item, text, memory, reading):
            # The best entry is from a field this line is not about, and the field is against it
            # rather than the words: "should i tip a hotel cleaner" reaches the money table, and
            # the line is read as a travel one, so the money row is turned down and the turn went
            # to a shrug while the travel row for the same question sat one place below it. Ask
            # again with the domain as part of the refusal, so the next best entry gets the turn
            # a wrong-field entry took from it.
            item, reply = _offer(
                lambda reject: find(reading,
                                    reject=_in_this_conversation(_guard(reject), reading),
                                    use_context=not other_food and not own_thing),
                memory, reading)
        if item is None:
            item, reply = _offer(lambda reject: _in_context(text, memory, reject=_guard(reject)),
                                 memory, reading)

            # A question that picks between things and names nothing to pick for ("what should i
            # see?", "what could i get her?") is answered about the thing under discussion.
            chosen = _choosing(text, memory)
            if chosen is not None:
                reading, item, reply = chosen
    if item is None:
        # A short ask naming no thing of its own ("what should I see?", after a city) is about
        # the thing the conversation is on, so the thing is tried on the end of it.
        item, reply = _offer(lambda reject: _in_bare_context(text, memory, reject=_guard(reject)),
                             memory, reading)
        follow_up = item is not None
    # Whether the line is a bare ask of the thing the chat is on ("how much is a new one"), which
    # wants the figure even when the entry's whole answer has been read already. Bound here
    # because the repeat check further down reads it on the path where `care` is set and the
    # block below never runs; read unbound, the raise is swallowed by the runtime and the turn
    # goes to another module with nothing red to show for it.
    bare = False
    if item is None and not care:
        # A follow-up names no subject of its own ("and if I stuff it?", "he's allergic to
        # nuts") and a correction names the wrong one; read it with the topic's subject put
        # back in, but only when the line alone reaches no entry, so a fit answer stands.
        wider = followup_reading(understood, memory)
        if wider is not understood:
            reading = wider
            item, reply = _offer(lambda reject: find(reading, reject=_guard(reject)), memory, reading)
            bare = mem.bare_question(understood, memory)
            if item is not None and bare:
                # A line that asks for a price or a time wants the figure even when the entry's
                # whole answer has been read already: "how much is a new one" after the battery
                # answer is the seventy to a hundred and fifty pounds.
                #
                # What this does NOT do, and an earlier head of this PR did, is hand the turn to
                # the next entry that fits when the topic's own entry has nothing new. It read
                # "my daughter is nervous about starting secondary school" / "what can we do
                # before the first day" as the school-admissions entry, whose advice is to apply
                # by 31 October - a different question, months too late for a child about to
                # start, where the entry the chat was already on answers it. Stepping off an
                # entry by subject is not something the keys can be trusted with; the sentence
                # the line asks for, when the entry has one, is picked out below.
                figure = _asked_figure(text, reply, None)
                if figure:
                    reply = figure
            # A line that names its own subject is not a follow-up, however much it leans on the
            # last topic: putting the subject back in may add the thing the topic was about, it
            # may not replace the thing this line is about.
            if item is not None and own and not _is_about(item, own):
                item, reply, reading = None, None, understood
            # The entry has to be about what the line is about. One ask is already known to be:
            # the store writes a line that says nothing but a pronoun out loud with the thing in
            # it ("will it go away" after "i have a cough" becomes "how long does a cough take to
            # go away"), and it only does that when the row it lands on is about that thing, so
            # there is nothing here for the line to be checked against - its own words are "will
            # it go away", which name nothing. Judged on those words alone, every such turn was
            # turned down here and went to a search hedge with the right row found. Everything
            # else is judged on its own words, as before: a line that names something ("and no
            # oven") must not be carried off to another subject by the topic.
            written_out = (understood is not reading
                           and mem.topics.the_prognosis_the_line_asks(understood, memory) is not None)
            if (item is not None and not written_out and not _leans_on(understood, item, memory)
                    and understood.get("kind") == "question"):
                # The topic fits the shape of the ask but not what the line is about: "what
                # should I say on the first day" is not a question about clothes. Leave the turn
                # to another module rather than read the last answer back a sentence at a time.
                # Only a question can be carried off this way: a statement that carries the same
                # thing on ("its been like that for a week" after the fridge-noise answer) is
                # read with the topic exactly as before, and repeating the answer is right.
                # A "who should i call" is that case and the answer on the screen settles it:
                # the topic fits the shape of the ask, and the entry it reaches is the wrong one.
                someone = _the_person_to_call(text, memory)
                if someone:
                    return someone
                return None
            follow_up = item is not None
    if item is None and not care:
        # A bare duration ask written out with the action the chat is on: "im learning to drive"
        # then "how long will it take" is the driving entry's question, and neither the line nor
        # the subject put back in ("how long will it take learning to drive") reaches it. Only
        # the ask about time, and only when the chat is on something you do, so a line that names
        # its own thing is untouched.
        written = _written_ask_with_an_answer(text, memory)
        if written:
            asked = understand(written, memory)
            item, reply = _offer(lambda reject: find(asked, reject=reject), memory, asked)
            if item is not None and not _is_about(item, mem.subject(memory)):
                item, reply = None, None
            if item is not None and not _answers_a_length(item, reply):
                # The entry found shares a noun with the action but answers another question
                # ("moving house" reaching "how much deposit"): a hedge beats a figure about a
                # different thing, and what is on the screen can still answer the length.
                item, reply = None, None
            if item is not None:
                reading, follow_up = asked, True
    if item is None and not care and mem.written_out(text, memory) \
            and not same_as_before(understood, memory):
        # The line asks how long something the person does takes, and no entry answers that
        # ("i want to grow tomatoes" then "how long will it take"). Nothing here knows the
        # length, and the answer on the screen is how to grow them: the turn is left to say it
        # does not know, rather than repeat the answer with "Same as before" in front of it.
        # The answer on the screen does settle it when it carries the length itself ("i want to
        # lose a stone" then "how long will it take" is answered by its own "losing about 0.5
        # to 1kg a week is the rate that stays off"), so only an answer with no such part is
        # left alone here.
        return None
    if item is None:
        # The sentence of the last answer about the thing this line names: "will salt work" after
        # the carpet answer reaches no entry however it is read, and the sentence holding salt
        # answers it. A yes/no whose thing has an entry of its own ("should i take ibuprofen"
        # after "my back hurts") is answered by that entry above and never arrives here.
        about = _the_sentence_about(text, memory)
        if about:
            return about
        # "who should i call" after the answer about the thing that broke names nobody itself:
        # the person the answer already names is the reply.
        someone = _the_person_to_call(text, memory)
        if someone:
            return someone
        # The line is about the very thing the last answer was about, and the knowledge base has
        # one entry per thing: give the part of that answer this line asks for.
        # A use-it-up question is about the food it names, not about the dish on the hob: the
        # slice of the last answer the words point at ("medium heat on the hob") is not what
        # was asked, and it stops the pantry table building the ragu the mince is for. A question
        # read with the topic is the other exception: every sentence of that answer has been
        # said, so the part it would give is a repeat.
        use_up = any(phrase in text.lower() for phrase in dishes.USE_UP_PHRASES)
        followed = None if (use_up or bare) else same_as_before(understood, memory)
        if isinstance(followed, str) and followed.strip() and not _new_thing(own, followed):
            # The part comes back from the answer just given, and the line named a detail of the
            # animal they told us about: said plainly it is the same sentence twice in a row
            # ("what about the chewing" after the chewing answer), so the detail is named.
            return _the_part_said_again(followed, text, understood, memory)
        # A dish they are only thinking of ("i was thinking of a satay") is a yes or no about
        # their allergy, and no entry is about that: it is about the dish. Last, though, because
        # an entry that already answers them with a dish they can have ("i fancy a chicken
        # curry" -> chickpea curry) is the better answer, and a check would take its turn.
        thinking = cooking.considered(understood, memory)
        if thinking:
            return thinking
        # No entry is about this line by name, but a line naming what is in the kitchen ("eggs
        # and spinach, what can I make?") is still answerable: the pantry table builds a meal
        # from the ingredients named rather than from a keyword. It passes on anything that is
        # a timing, a safety question or a why, and on a follow-up that names no food itself.
        # "how do i make it up to my mum" is a table to the kitchen's words alone - "make", "up
        # to", and a person after it - and the tray bake for a crowd is no answer to a person
        # asking how to put something right. The composer's repair is that turn, so the pantry
        # is not shown this line (bot/compose/repair.py, amends_to).
        meal = None if amends_to(text) else cooking.meal(understood, text=text, memory=memory)
        if isinstance(meal, str) and meal.strip() and not cooking.unusable(meal, understood):
            return meal
        # Every reader above has passed, and the line points back at a thing the store holds:
        # "where should i keep it" after "im trying to save money" asks about the money, and
        # "where should i keep my money" is the entry. It is asked here rather than earlier so a
        # turn a sentence of the answer above can answer keeps that answer.
        pointed = the_ask_about_the_thing_it_points_at(understood, memory)
        if pointed is not None:
            item, reply = _offer(lambda reject: find(pointed, reject=reject), memory, pointed)
            if item is not None and isinstance(reply, str) and reply.strip():
                return reply
        # Nothing the knowledge base has fits this kitchen: say what can be cooked in the one it
        # has ("my oven is broken, what can i make for dinner" had no answer at all).
        return cooking.without(understood)
    if getattr(item, "fault", False):
        # A fault card is about the appliance; the line may still be asking what to eat without
        # it. "my oven is broken what can i cook" fits the plug-check card on the words, and the
        # dinner is the question, so the kitchen plan answers before the card does.
        kitchen = cooking.without(reading)
        if isinstance(kitchen, str) and kitchen.strip():
            return kitchen
    if not _usable(item, reading, memory):
        # The entry answers the words but not the kitchen: take the best entry that needs
        # nothing the line has not got ("no oven" once reached the roast-chicken timings).
        kitchen = cooking.without(reading)
        # "my oven is broken what can i cook" is a cooking question with a repair answer in the
        # table: the kitchen plan answers the part of the line that is a question, and it is
        # better than the plug-check card, which is for the appliance and not for dinner.
        if isinstance(kitchen, str) and kitchen.strip():
            return kitchen
        item = _next_usable(item, reading, memory)
        if item is None:
            return kitchen
        reply = _payload(item, memory, reading)
        # The entry that needs nothing the line has not got can still have no reply at all for
        # this line ("can i bake a cake with no oven" landed on the planning entry, which only
        # answers an announcement). The kitchen answer is better than a shrug, and it is the
        # answer to the part of the line that is a question.
        if not (isinstance(reply, str) and reply.strip()) and isinstance(kitchen, str):
            if kitchen.strip():
                return kitchen
    if isinstance(reply, str) and reply.strip():
        if not own and _reaches_another_subject(text, item, memory):
            # The entry the line reaches is about something the conversation is not. "any other
            # ideas" after a chat about what to watch asked for another film and got the
            # fifteen-minute dinners ("Quick: tuna pasta in 15, macaroni cheese in 25") because
            # "ideas" is in that entry's keys and the line names nothing of its own. A wrong
            # subject is worse than a shrug, so the entry stands down here, after every reader
            # has had its chance: a topic-anchored read of the same line shares the topic's words
            # and is never dropped.
            return None
        said = (_answer_said(reply, memory)
                if mem.asks_only(understood) and not pairing(text) else 0)
        # A line that names only a size ("how long for 250g") reaches the entry by name, so the
        # whole paragraph comes back before any follow-up is looked at - and the figure they
        # asked for is workable from the rate inside it. Only for a line about this entry and
        # nothing else, so "how long do i roast a 2kg leg of lamb" is not given the bird's rate.
        if (not own or _is_about(item, own)) and _only_a_size_of(item, text):
            sized = mem.sized_reply(reply, text, memory, _key_words(item))
            if sized:
                remember_answer(memory, reply, _key_words(item))
                return sized
        # A bare ask repeats the answer it is about ("what temperature?" after "what temperature
        # for a cake") without repeating the line, so it is counted by the sentence we gave and
        # not only by the line that asked for it. A question that says its own subject again
        # ("how long do I boil eggs for") is asking afresh and gets the plain answer.
        if not said and not follow_up and _said_before(reply, memory):
            # The line reaches the same entry on its own words, so the whole paragraph would be
            # said again word for word: give the part of it this line asks for instead.
            part = narrow(reply, text)
            if isinstance(part, str) and part.strip() and flat(part) != flat(reply):
                part = _part_not_repeated(part, reply, memory)
                if part:
                    # The sentence was said on the last turn as part of the same paragraph, so it
                    # comes back with the detail the line named in front of it: a sentence word
                    # for word twice in a row is the repeat STYLE.md says never to give.
                    again = _the_detail_said_again(reply, text, memory)
                    if again:
                        return again
                    return part
        # "which one?" is not the same line asked again: the answer they want is the one part of
        # the last answer that decides between the things, not the whole paragraph back with a
        # "Same as before" in front of it. Read it before the repeat framing takes the turn, and
        # only for a line that is one of the bare choice asks (`_the_one_to_pick` declines on
        # everything else: a comparison, a line with nothing being chosen before it, an answer
        # with nothing shorter to give).
        if CHOICE_ASK.match(" ".join(str(text or "").lower().split())):
            picked = _the_one_to_pick(text, memory)
            if picked:
                return picked
        same_line = _asked_again(text, reply, memory)
        # A line that names a food of its own is not asking for a part of the last answer: "how
        # long do i reheat a pizza" after a chicken keeping answer was cut down to that answer's
        # "2 hours", where the pizza entry had just found the 12 to 15 minutes.
        # A timing ask about an action the chat is on ("i want to grow tomatoes" then "how long
        # will it take") is not a part of the last answer: the answer on the screen is how to
        # grow them, and framing it "Same as before" is the bot's worst habit, not a length. When
        # the ask written out reaches no entry, the turn has nothing to say about the length and
        # is left to say so.
        if (not own and not same_line and _said_before(reply, memory)
                and not _names_another_food(understood, str(mem.subject(memory) or "").lower())
                and (not mem.written_out(text, memory) or same_as_before(understood, memory))):
            # The answer is on the screen but this line is not the same line: it leans on the
            # last answer for its subject ("what can we do before the first day", "anything to
            # do before it starts"). That is a follow-up asking for a part of the answer, and
            # framing it "Same as before" and cutting it to its opening sentence drops the very
            # sentence it asks about - the classmate line was right there in the answer. Whether
            # `follow_up` was read for the line does not matter here: the line names no thing of
            # its own, so what it is about is what we just said.
            part = same_as_before(understood, memory)
            if (isinstance(part, str) and part.strip()
                    and flat(part) != flat(mem.last_bot(memory) or "")):
                return part
        if said and mem.written_out(text, memory) and not same_as_before(understood, memory):
            # A timing ask about an action the chat is on ("i want to grow tomatoes", then "how
            # long will it take") read as a bare ask for a figure. No entry knows how long that
            # takes, and the answer on the screen is how to grow them: it is not that answer
            # said again, so it is neither framed as a repeat nor cut to its opening sentence.
            # The turn is left to say it does not know.
            return None
        asked = max(same_line, said)
        if asked and _said_before(reply, memory):
            # "Where do i start", "what should i do first" a turn after this answer: they are not
            # asking for the paragraph again, they are asking which part of it to do. The step is
            # already in the answer, so it is handed over in the answer's own words.
            move = repeat.the_move(text, reply, memory)
            if move:
                return move
            # The same line again, reaching the same answer: say it again with the lead-in a
            # repeat gets, rather than hand the turn over. The entry has nothing new, but the
            # person asked the same thing, and a shrug is the one answer a repeated question
            # must not get.
            if asked >= 3:
                return AGAIN_HELP.format(reply=reply)
            honest = _figure_missing(reply, text)
            if honest:
                return honest
            return AGAIN[asked - 1].format(reply=_repeat_short(reply, text, memory))
        # A bare ask names nothing of its own ("what am i doing this week", "how do i do it"), so
        # the answer coming round again is that same answer asked for again and is framed as the
        # repeat it is - even with an acknowledgement between. A line that names its own thing is
        # a question of its own and is left to the module that has something new about it.
        framed = mem.said_again(reply, memory, line=None if said_topic.names_nothing(text) else text)
        if framed:
            # Nothing smaller to give and the paragraph is already on the screen, so it comes
            # back as the repeat it is rather than printed twice word for word.
            return framed
        added = _the_new_part(reply, memory) if follow_up and _said_before(reply, memory) else None
        if added:
            # The entry says what it said before and then the sentence this line asks for: that
            # sentence is the answer, and the rest is a paragraph already on the screen.
            remember_answer(memory, reply, _key_words(item))
            _remember_answer(memory, item, reply)
            return added
        if follow_up and _said_before(reply, memory):
            # The entry has nothing new for this follow-up: give the part of the last answer
            # that fits, or let another module speak rather than say it twice. A line asking
            # for a price or a time gets the sentence that carries one: "how much is a new one"
            # is the figure they were told a turn ago, not a note on how to fit it. A choosing
            # question is worth one more try first: what the context reached is often the entry
            # that answered the line before ("interview-prep" for "what should i wear"), and the
            # outfit the line is really asking about is a different entry nothing has said yet.
            if _a_question_about_another_thing(text, reply, understood, memory, own, item):
                # A figure cut out of the answer on the screen is not this line's figure when the
                # line asks about a thing of its own that the answer never mentions: "how much
                # does a puppy cost" then "how much does a tattoo cost" was handed the puppy's
                # price as the price of a tattoo. A friend says what they do not know instead.
                return None
            figure = _the_figure(text, reply)
            if figure:
                return figure
            chosen = _choosing(text, memory)
            if chosen is not None and not _said_before(chosen[2], memory):
                return chosen[2]
            same = same_as_before(understood, memory)
            if same:
                return same
            # The entry the line reaches has nothing new, but the person asked a yes/no about a
            # thing it named ("does a plunger help" after the sink answer): the sentence of that
            # answer holding the thing is exactly what they asked for, and a shrug is not.
            sentence = _the_sentence_about(text, memory)
            if sentence:
                return sentence
            # The follow-up points back at the answer itself and the words it brings name no
            # thing to cut a sentence by: "what should i see there", after the city was already
            # described. The reply is on the screen, so it comes back framed as the repeat it is
            # rather than as a search hedge - a person who asks again gets their answer again.
            # Only a question: a detail they add ("its an old oak floor") leans on the last answer
            # without asking anything of it, and the acknowledgement it gets is the right reply.
            # And only for a line the answer is about: "how do i clean my boots" after "how do i
            # get rid of fruit flies" reached the fruit-fly answer on the word "clean" and came
            # back as "Same as before: Put a little cider vinegar..." for a line about boots. The
            # sentence about the thing, above, is the one thing worth handing back to a line that
            # names a thing the answer never mentions.
            # A line that names nothing of its own but the ask ("what helps" after the
            # shower-drain answer) is asking the same question about the same thing, and the
            # answer says how: nothing in it has to say the word "help" for the framing to be
            # right. Cut to the sentence with the move in it, so the person gets the step rather
            # than the paragraph they have already read.
            if (isinstance(understood, dict) and understood.get("kind") == "question"
                    and _covered(text, reply, memory, understood)
                    and not _asks_of_another_subject(text, understood)):
                # A yes/no ask is not the same ask again: "my back is sore" then "will it stop"
                # wants a yes or a no, and "Same answer, and it covers this" in front of the
                # paragraph is not one. Only an ask that names nothing and asks nothing to be
                # decided - "what helps", "what should i do" - is the question the answer on the
                # screen already answers.
                bare_ask = (not mem.topics.YES_NO.search(str(understood.get("clean") or ""))
                            and not [word for word in mem.content(str(understood.get("clean") or ""))
                                     if word not in ASKING and word not in BARE_GENERIC
                                     and word not in ASKING_VERBS and word not in PROPERTY_WORDS])
                if (bare_ask and isinstance(understood, dict)
                        and understood.get("kind") == "question"
                        and not _asks_of_another_subject(text, understood)):
                    return (same_again.instead(reply, text, memory)
                            or mem.said_again(reply, memory, line=text))
                return mem.said_again(reply, memory, line=text)
            # Nothing in the last answer matched this line's words, and a turn before it got no
            # answer at all, so the usual part-picking has nothing to hand over: "how do i clean
            # it off" after a burnt pan came back as "I'm not sure about that one - a quick
            # search". The answer still says how, so the step in it is given in its own words
            # rather than a hedge about a subject we have already answered.
            return repeat.the_move(text, reply, memory)
        if not asked and follow_up and _already_said(reply, memory):
            # The same answer, word for word, is still on the screen: say the part of it this
            # line asks for, or let another module speak rather than repeat it. Only a line that
            # had to lean on the last answer counts: a question asked again by name reaches its
            # entry on its own, and answering it twice is right. A bare ask is counted above,
            # so it is answered again with the lead-in a repeat gets rather than declined.
            figure = _the_figure(text, reply)
            if figure:
                return figure
            same = same_as_before(understood, memory)
            if same:
                return same
            if (isinstance(understood, dict) and understood.get("kind") == "question"
                    and not _asks_of_another_subject(text, understood)):
                return mem.said_again(reply, memory, line=text)
            return repeat.the_move(text, reply, memory)
        if asked >= 3:
            return AGAIN_HELP.format(reply=reply)
        if asked:
            honest = _figure_missing(reply, text)
            if honest:
                return honest
            return AGAIN[asked - 1].format(reply=_repeat_short(reply, text, memory))
        if not own and _said_before(reply, memory) and _covered(text, reply, memory, understood):
            # Nothing else narrowed it and the paragraph is word for word what the last turn said:
            # the line is a follow-up on the answer already given ("what about the chewing" after
            # the chewing answer), so the part it asks about comes back with the detail named
            # rather than the same paragraph twice. STYLE.md, "Never answer the same way twice in
            # a row", and a repeat printed twice reads as a machine.
            again = _the_detail_said_again(reply, text, memory)
            if again:
                return again
            framed = mem.said_again(reply, memory)
            if framed:
                return framed
        if _a_question_about_another_thing(text, reply, understood, memory, own, item):
            # The answer on the screen is about the thing the chat was on, and this line asks its
            # own question about a thing of its own that the answer never mentions: it is not this
            # line's answer, neither framed as a repeat nor said plainly.
            return None
        # Keep the answer whole: a later follow-up may need a sentence of it that this turn is
        # about to be trimmed to, or that a trimmed answer no longer carries.
        remember_answer(memory, reply, _key_words(item))
        _remember_answer(memory, item, reply)
        # The paragraph is already on the screen word for word, and this line named something of
        # its own, so no lead-in applies to it above and the entry has nothing new: say the short
        # of it rather than print it twice (bot/memory/again).
        return same_again.instead(reply, text, memory) or reply
    return None
