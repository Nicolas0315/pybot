"""Part 6 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re

from .. import memory as mem
from ..compose import lead
from ..knowledge import cooking, entries as all_entries, shopping
from ..knowledge.lookup import find
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import named
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import keywords
from ..memory import again as same_again  # the short of an answer already on the screen
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory.topics import AMOUNT, ASK_ONLY, stem
from ..understanding import kinds
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import returns as went_back
from ..memory import a_detail_of_the_thing_we_hold, keywords, swap
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory.narrow import RATE, flat, kind_of as asked_kind, narrow, the_part_asked, words_of
from ..understanding import understand
from .answers_part_01 import (
    SENTENCE, WORD, similar, _in_short, _the_sentence_asked, _without_a_lead,
    _a_restatement_of_the_answer, _all_of_it_in_the_answer, A_CORRECTION_WORD, A_JOINING_WORD,
    A_PLACE_IN_IT, A_QUALITY_WORD, BACK_POINTS, DETERMINER_BEFORE_DETAIL, FILLER_WORD, NOTHING_WORD,
    NOT_A_DETAIL, PRAISE_WORD, _ask_verb, _named_in, _named_whole, _said_before_now,
    _the_clause_s_verb, DETERMINERS, _asks_of_another_subject, _entry_words, _what_they_typed,
    _with_detail, _small_letter,
)
from .answers_part_02 import (
    _key_words, _the_answer_on_screen,
)
from .answers_part_03 import (
    ASKING_VERBS, PLACE_WORDS, PROPERTY_WORDS, SUM_TABLE, _a_property_word_names_a_thing,
    _asks_part, _last_answer,
)
from .answers_part_04 import (
    A_LEAD_TIME, KIND_SAID, NOT_NEW, WHEN_OF_THE_DAY, _a_figure_apart, _cause_part, _figures,
    _only_a_figure, _part_not_repeated, _reason_again, _sentence_naming_the_part, _sentence_with,
)
from .answers_part_05 import (
    _nothing_more_said_again, _times_the_answer_was_said, _keyed_on_the_line, _payload, GIFT_WORD,
    _a_gift_entry, _a_gift_just_answered, _asks_what_to_give, _only_a_limit, _price_limit,
    _the_interests,
)


def _the_sentence_naming(reply, text, memory=None):
    """The later sentence of the answer that carries the part the line names, or None.

    A follow-up that names a part of the thing ("it catches at the top" after the sticking door)
    reaches the same entry, and the entry has one paragraph for the whole subject: held to the
    opening, the second turn handed back the general cause - damp, or a screw pulled out - which
    the person had just read, and said nothing about the top. The card does speak to the top: a
    later sentence has the hinge to tighten. That sentence is what the person asked for, so it is
    the one said again.

    The part is read by `_the_detail_named`, so a word the person has used before in this chat is
    not a part ("how do i clean my boots" asked twice names the whole thing, not a piece of it),
    and neither is the verb of the ask or a word that names no thing. Those turns keep the
    opening, which is the answer they asked for the first time.
    """
    detail = _the_detail_named(text, memory)
    if not detail:
        return None
    sentences = [part.strip() for part in SENTENCE.split(str(reply or "")) if part.strip()]
    if len(sentences) < 2:
        return None
    word = detail.split()[-1]
    for sentence in sentences[1:]:
        # The part of the thing, so the opening is left out: said again it is already the short
        # form, and a sentence that carries the part is the one with something new in it.
        if any(similar(word, other) for other in WORD.findall(sentence.lower())):
            return sentence
    return None


def _repeat_short(reply, text, memory=None):
    """The short form of an answer given a second time: the part the line asks, or the opening.

    A sentence a row declared for the first turn's line ("No.", "Usually, yes.") belongs to that
    line, not to this one: repeated behind "Same as before:" it answers a question nobody asked
    again, and a line that wants a time would be told "No." So a declared sentence is read off
    before the answer is repeated (`_without_a_lead`).
    """
    reply = _without_a_lead(reply)
    part = _the_sentence_asked(reply, text) if asked_kind(text) else None
    return part or _the_sentence_naming(reply, text, memory) or _in_short(reply)


def _the_detail_named(text, memory=None, with_quality=False):
    """The part a follow-up names, or "" when it names nothing the answer has not already said.

    A follow-up that names a part of the answer worth its own sentence is framed as one ("Same for
    the trams: ..."). A follow-up that says the thing again in more words names no new part, and
    the frame announced the answer back at the person: after the banging card, "its a banging sound
    when the heating comes on" came back "Same for the heating: a knocking that comes at the end of
    a burn is limescale on the heat exchanger..." - a different fault, invented out of a word the
    answer had just used. If every word of the part is already in the answer above it, there is
    nothing separate being named, and the reply is found without the frame.
    """
    named = _the_part_named(text, memory, with_quality)
    if named and _a_restatement_of_the_answer(memory) and _all_of_it_in_the_answer(named, memory):
        return ""
    return named


def _the_part_named(text, memory=None, with_quality=False):
    """The word a follow-up names as the part of the thing it asks about ("the biting"), or "".

    `with_quality` reads the line the way it was read before a quality word was known to name no
    part, so the caller can see what the name would have been and answer the repeat rather than
    stand down (see `_only_a_quality_name`).

    The word is kept with the word in front of it when that is a determiner, so the lead-in reads
    "Same for the biting" rather than "Same for biting".

    Three words are not a detail, and each of them made a wrong reply:
    * the verb of the ask itself - `stop` in "how do i stop that" - because "Same for stop:" is
      not a sentence;
    * a word the person has already used in this chat - `sofa` in "what about the sofa" after "my
      cat keeps scratching the sofa" - because the answer is already about that, so there is
      nothing new to say about it and the lead-in would announce the thing itself;
    * a word that names no thing at all - `else` in "what else can i do with it" - because there is
      no part of the answer called "else" and the lead-in came out as "Nothing different for else".
    A line that only goes back to a thing ("back to lisbon", "about the boiler") names no part of
    an answer either - the word read as the part was the return itself ("Nothing separate for
    back"), which is why the guard on the shape is here rather than at each reader.
    """
    if went_back.a_bare_return(text, memory if isinstance(memory, dict) else None):
        return ""
    raw = WORD.findall(str(text or "").lower())
    if raw and all(word in ONLY_THE_ASK for word in raw):
        # A line made only of the ask to hear it again names no part of the answer. "pardon?" after
        # the red-wine answer came back "Nothing separate for pardon - it is the same advice: <the
        # paragraph>", which tells a person who missed a sentence that the bot has nothing separate
        # to say about the word "pardon". The line is the repeat ask, and the memory lane answers it
        # as one; here there is nothing to name.
        return ""
    wanted = {word for word in keywords(text)
              if len(word) > 2 and word not in ASK_ONLY and word not in NOT_A_DETAIL
              and word not in A_CORRECTION_WORD}
    if not wanted:
        return ""
    verb = _ask_verb(text)
    already = _said_before_now(text, memory)
    for index in range(len(raw) - 1, -1, -1):
        word = raw[index]
        if word in A_JOINING_WORD:
            continue
        # `keywords()` gives stems ("settle"), so the word as typed ("settles") was never found
        # and the walk went back past it to an earlier word - "until", on the line above. A plural
        # whose stem is a keyword is that keyword.
        if word not in wanted and stem(word) not in wanted:
            continue
        if (word in PRAISE_WORD or word in NOTHING_WORD or word in FILLER_WORD
                or (word in A_QUALITY_WORD and not with_quality)):
            continue
        if verb and (word == verb or word.startswith(verb) or verb.startswith(word)):
            continue
        # A verb form the person says *after* the thing is how the question about it is asked -
        # "whats the scheme thing called", "what is it used for" - so it is the asking and never
        # the part the follow-up names: the answer came back framed "Nothing different for called,
        # I'm afraid". The word in front of it decides, the way it does in `bot/memory/detail.py`:
        # behind "the" or "my" it is a noun ("the seating", "the wedding"), otherwise it is a verb.
        if raw[index - 1] not in DETERMINER_BEFORE_DETAIL and (
                word in kinds.VERBISH
                or word in kinds.VERB_THIRD
                or _the_clause_s_verb(raw, index)
                or (len(word) > 4 and word.endswith(("ed", "ing")))):
            continue
        if word in already:
            continue
        # A word with `to` after it is the verb of a habit, not a part of the answer: "he used to
        # eat them" after the refusing-veg card named `used` and told the person "There is nothing
        # separate on used - what I said above is the whole of it", which is a sentence about the
        # bot's own notes. The -ed test above misses it because `used` is four letters and the
        # test wants five, and it is not a detail beside `to` whatever its length ("went to",
        # "got to", "tried to"). The next word decides, and an earlier word still gets its turn.
        if index + 1 < len(raw) and raw[index + 1] == "to":
            continue
        behind = raw[index - 1] if index else ""
        if (word in A_PLACE_IN_IT and index + 2 < len(raw) and raw[index + 1] == "of"
                and raw[index + 2] in BACK_POINTS):
            # "the end of it", "the top of that": where in the thing already in hand, not a thing
            # of its own, so nothing new is named here. The line leans on the answer, and the
            # answer is the answer.
            return ""
        if behind in ("the", "my", "his", "her", "their", "your", "a", "this", "that"):
            return behind + " " + word
        # The determiner and the word beside it are one name even when a plain word sits between
        # them: "will she stop if i get a scratch post" is the scratch post, not "post".
        whole = _named_whole(raw, index)
        if whole:
            return whole
        # A word that is not in the keywords as it was typed is a form of one ("settles" for
        # "settle"), and on its own it is the asking, not a part of the answer: the lead-in read
        # "Nothing different for settles", which is not a sentence either. It is said back only
        # when the answer itself says it by name ("Same for the scratching: ...").
        if word not in wanted and not _named_in(mem.last_bot(memory or {}), word):
            return ""
        return word
    return ""


def _only_a_quality_name(text, memory=None):
    """Whether the part the line names is a quality word and nothing else ("a new"), or False.

    A quality word says what the thing is like and names no piece of what the answer says about
    it, so such a line names no part at all. The caller still has to know that a part *was* read
    there: a repeat of a question the answer already covers must be answered as a repeat, not
    stood down to a search hedge, and reading the line the old way says which lines those are.
    """
    named = _the_detail_named(text, memory, with_quality=True)
    if not named:
        return False
    words = [word for word in named.split() if word not in DETERMINERS]
    return bool(words) and all(word in A_QUALITY_WORD for word in words)


def _covered(text, reply, memory=None, understood=None):
    """True when the answer on the screen is about everything the line names.

    A line can reach its entry only through the words of the last turn: "how do i clean my boots"
    after the fruit-fly answer finds that answer on the word "clean", and the words of the line's
    own - the boots - are in it nowhere. Then the paragraph is not the answer to this line, so it
    is not handed back framed as a repeat of it either; nothing is said and another module speaks.
    A detail the line names ("what about the biting") is the exception: the answer having nothing
    separate for it is exactly what the lead-in is allowed to say.

    The exception is for a part of the thing the answer is about, and not for a thing of its own.
    "how much does a puppy cost" then "how much does a tattoo cost" is a price question about a
    tattoo, and reading the tattoo as a detail let the puppy's answer pass as one that covers the
    line, so the person was told "There is nothing separate on a tattoo". A line whose own subject
    is not the subject the answer is about (`_asks_of_another_subject`) names a thing, not a part.
    """
    said = set(WORD.findall(str(reply or "").lower()))
    read = understood
    if not isinstance(read, dict):
        read = (memory or {}).get("understood") if isinstance(memory, dict) else None
    typed = _what_they_typed(text, memory)
    detail = "" if _asks_of_another_subject(typed, read) else _the_detail_named(typed, memory)
    words = WORD.findall(str(text or "").lower())
    if any(word in BACK_POINTS for word in words):
        # "what is there to see" names nothing of its own: it points back at the answer on the
        # screen, and what it asks is that answer, so there is nothing here to be uncovered.
        return True
    verb = _ask_verb(text)
    entry = _entry_words(memory)
    for word in keywords(text):
        if len(word) < 3 or word in ASK_ONLY or word in detail.split():
            continue
        if verb and (word == verb or word.startswith(verb) or verb.startswith(word)):
            continue  # the asking, not a thing: "how do i clean my boots" asks how to *clean*
        if word in ASKING_VERBS:
            # "what helps" names nothing but the ask, so there is nothing in it for the answer to
            # cover: the answer on the screen is the thing it is about, and the lead-in "same
            # answer, and it covers this" is exactly what the person asked for.
            continue
        if any(similar(word, other) for other in said):
            continue
        # A word the entry that answered is keyed on is one of the things it answers, even when
        # the answer never says it: the slug row is keyed on slugs and snails and gives one
        # method for both, so "what about snails" after the slug answer was read as a line about
        # nothing the answer covered and got the shrug. The answer is about it - it is the same
        # row - so it comes back as the same advice.
        if any(similar(word, other) for other in entry):
            continue
        return False
    return True


def _a_question_about_another_thing(text, reply, understood, memory, own=None, item=None):
    """True when the line asks its own question about a thing the answer on the screen never names.

    "how much does a puppy cost" then "how much does a tattoo cost" reached the puppy's price row
    through the conversation and handed the puppy paragraph back framed as the answer to a tattoo:
    "Nothing separate for a tattoo - it is the same advice: A puppy is about 800 to 3,000 pounds".
    The line has a subject of its own - a thing, not a part of the thing in hand - and the answer
    is about another thing altogether, so it is not this line's answer however it is framed. A
    friend says what they do not know (STYLE.md prefers the honest hedge to an answer that does
    not fit), so the module stands down and the composer's own line takes the turn.

    The thing has to be named by the line, as a thing (`_the_detail_named` gives "a tattoo",
    "the passport"), and it has to be unknown to both the answer and the row that gave it. Two
    questions lean on the answer without naming anything of their own and keep it:
    - "how much should i expect to pay" after the brakes failed an MOT is the brake price; every
      word of it is asking, so it names no thing at all;
    - "how much should i budget for a van" is the money-plan card's line on the word budget, and
      a row keyed on a word the line asks by name is answering it, whether or not it says the
      line's other word.

    Only a question, too: a line that names a thing and asks nothing ("its an old oak floor")
    leans on the answer without asking anything of it, and the acknowledgement is the right reply.
    """
    if own:
        return False  # the line reached an entry on its own words: that entry is its answer
    if not isinstance(understood, dict) or understood.get("kind") != "question":
        return False
    if not isinstance(reply, str) or not reply.strip():
        return False
    typed = _what_they_typed(text, memory)
    if not _asks_of_another_subject(typed, understood):
        return False
    thing = _the_detail_named(typed, memory)
    if len(thing.split()) != 2:
        # The thing has to be named as a thing, with the word that makes it one: "a tattoo",
        # "the passport". A bare word can be the asking ("pay" in "how much should i expect to
        # pay", which is the brake price the answer on the screen already gives) and the line
        # then leans on the answer instead of naming a thing of its own.
        return False
    word = thing.split()[-1]
    if any(similar(word, other) for other in WORD.findall(reply.lower())):
        return False  # the answer names the thing
    held = set(_entry_words(memory))
    if item is not None:
        held |= _key_words(item)
    if any(similar(word, other) for other in held):
        return False  # the row that answered is keyed on the thing, so it is its answer
    named = [one for one in keywords(typed) if len(one) > 2 and one not in ASK_ONLY]
    if any(similar(one, other) for one in named for other in held):
        # The row that answered is keyed on something this line asks by name, so it is part of the
        # line's answer even when it never says the line's other word: "how much should i budget
        # for a van" is the money-plan card's line on the word budget, and the card answers it by
        # saying how to work the figure out. Only a row keyed on nothing the line names is
        # answering a different question.
        return False
    return True


def _the_detail_said_again(reply, text, memory):
    """The same answer given again for a detail named inside it, or None.

    The answer is on the screen and the entry has nothing new, so the paragraph is not printed
    twice word for word: the detail the line named is said in the lead-in, the way a friend
    answers "what about the biting" with "same for the biting - plenty of chew toys"."""
    detail = _the_detail_named(text, memory)
    if not detail:
        # No detail, but the line asks for a kind of thing the answer holds ("when could they
        # actually vote" holds the dates): the sentence that answers the ask is what a friend
        # says again, and the alternative - "That is everything I have on that one, so I would
        # only repeat myself" - shrugs at a question the card answers.
        picked = _the_sentence_asked(reply, text) if asked_kind(text) else None
        if isinstance(picked, str) and picked.strip() and flat(picked) != flat(reply):
            times = _times_the_answer_was_said(reply, memory)
            if times:
                underneath = same_again.the_same_thing_underneath(text, picked, times, memory)
                if underneath:
                    return underneath
                return same_again.AGAIN[min(times, len(same_again.AGAIN)) - 1].format(
                    reply=picked)
        return _nothing_more_said_again(reply, text, memory)
    times = _times_the_answer_was_said(reply, memory)
    if not times:
        return None
    # The detail may be said in the answer itself ("the biting" inside a paragraph about chewing):
    # then the sentence that names it is given back rather than the opening.
    short = narrow(reply, text) or ""
    if not isinstance(short, str) or not short.strip() or flat(short) == flat(reply):
        # The sentence the line asks for, not the opening: "and when could they actually vote"
        # after the women's-vote answer was handed "The campaign for women's votes split into..."
        # behind the lead-in, and the dates the person asked for were in the next sentence.
        short = _repeat_short(reply, text, memory) or reply
    return _with_detail(detail, short, times, text, memory, card=reply)


def _detail_lead_in(text, part, memory):
    """`part` with the detail the line named in front of it, when the part is already on screen."""
    detail = _the_detail_named(text, memory)
    if not detail or not isinstance(part, str) or not part.strip():
        return ""
    said = flat(part)
    times = 0
    for turn in reversed((memory.get("turns") or [])[-4:]):
        if not isinstance(turn, dict):
            break
        if said and said in flat(turn.get("bot")):
            times += 1
            continue
        break
    if not times:
        return ""
    return _with_detail(detail, part, times, text, memory, card=_the_answer_on_screen(memory))


def _the_part_said_again(part, text, understood, memory):
    """The part of the last answer, with the detail the line named in front of it when needed.

    The part asked for is usually a sentence of the answer just given, so said plainly it is the
    same sentence twice in a row - which STYLE.md says never to do. When the line named a detail
    of the animal they told us about ("what about the chewing" after the chewing answer), that
    detail is what the lead-in names."""
    if isinstance(part, str) and part.strip() and a_detail_of_the_thing_we_hold(understood, memory):
        lead = _detail_lead_in(text, part, memory)
        if lead:
            return lead
    return part


def _part_asked(text, memory):
    """The part of the last answer the line asks for, or None when it asks about something else."""
    if _a_property_word_names_a_thing(text):
        # "how long does the cold last" names the cold, so it is not a part of the answer on the
        # screen even though every word in it is a property word. The entry for the cold answers
        # it; narrowing the last answer gave "Rest, fluids... I can't say how long it will take".
        return None
    if WHEN_OF_THE_DAY.search(str(text or "")) and asked_kind(text) == "date":
        return None
    earlier = _last_answer(memory)
    if not _asks_part(text):
        # "how long should the opening be?" names a part of the answer, not a property on its
        # own. It is still about the last answer when the word it names is in that answer (or
        # in what the entry is about); a new thing ("how long does a chicken take?") is not.
        if earlier is None or asked_kind(text) is None:
            return None
        said = set(words_of(earlier.get("reply") or "")) | set(earlier.get("keys") or ())
        named = set(words_of(text)) - PROPERTY_WORDS - NOT_NEW
        if named and not named & said:
            return None
    if mem.left_for_a_blank(memory, text):
        # A turn in between named a thing of its own and got no answer ("what about a leg of
        # lamb?" after the roast chicken): this line is a question about that thing, so a part of
        # the older answer (the chicken times) is a wrong answer rather than a helpful one.
        return None
    if RATE.search(text):
        # A rate ("per kilo") is better answered by the entry that states it with its
        # qualifier than read out of a neighbouring sentence; let the lookup try.
        return None
    if not earlier:
        return None
    reply = earlier.get("reply") or ""
    if (COOK_VERB.search(text) and not KEEPS_ASK.search(text)
            and KEEPS_ANSWER.search(reply) and not COOK_VERB.search(reply)):
        # "how long do i cook it for" after "how long does cooked chicken last": the keeping
        # answer holds no cooking time, so there is no part of it to hand back, and trimming it
        # gave "3 days" as if that were how long the pan takes. The method entry for the same
        # food answers the line instead.
        return None
    if len(SUM_TABLE.findall(reply)) > 1 and asked_kind(text) == "time":
        # A table of sums ("£100 a month is 50 months, £250 a month is 20 months") is one answer:
        # trimmed to its last figure it reads "10 months" with nothing saying what for. The entry
        # that wrote the table answers the follow-up itself, with the next sums up.
        return None
    # One entry can hold a whole table of the things it answers one at a time, and then its key
    # words say nothing about which row was given: `appliance-life` keys on every appliance name,
    # so "how long does a toaster last" straight after "how long should white goods last" was read
    # as a part of that answer and cut to the sentence the table gave. When the line reaches the
    # same entry that answered, names a row of it, and that row would answer in its own words, the
    # line is a question of its own. A follow-up that names a thing of its own (`and how much
    # flour` after "2 eggs") reaches a different entry, so it is still the answer's detail.
    own_named = set(words_of(text)) - PROPERTY_WORDS - NOT_NEW
    earlier_keys = set(earlier.get("keys") or ())
    if own_named and earlier_keys:
        reading = understand(text, memory)
        same_item = [one for one in all_entries() if _key_words(one) == earlier_keys]
        if same_item and own_named & _key_words(same_item[0]):
            fresh = _payload(same_item[0], memory, reading)
            # The whole of what the entry says, not only its opening sentence: the thing the line
            # names can be in its second sentence ("and how long in the oven" after the frosting
            # answer reaches the cake's plan, whose oven time is not the sentence the follow-up
            # entry opens with). An entry that has something to say about the word the line names
            # is answering this line, and reading the last answer's part instead gives a sentence
            # about the other thing.
            if not (fresh or "").strip() or (
                    flat(fresh) != flat(reply) and own_named & set(words_of(fresh))):
                return None

    # A follow-up can name a different thing than the answer just given: "how long to bake a
    # sweet potato" after a plain one, or "how long to roast a chicken breast" after a whole
    # bird. Narrowing the last answer to its figure then gives "An hour." and "1 hour 40." for
    # a thing that takes neither, which is worse than no answer at all. When the line names a
    # thing the last answer never mentioned and reaches an entry of its own, that entry speaks.
    # Only a different *thing* counts: "in the fridge", "in the oven" and "on the hob" are where it
    # happens, not what is being cooked, and narrowing still answers those.
    named = (set(words_of(text)) - PROPERTY_WORDS - PLACE_WORDS - set(words_of(reply))
             - set(earlier.get("keys") or ()))
    reading = understand(text, memory)
    own = find(reading)
    # The line can also name what it is about in a word the last answer happened to say, and then
    # `named` is empty and nothing below looks new: "my cake cracked on top" then "why did my cake
    # sink in the middle" shares "cake" and "middle" with the crack answer and with the entry that
    # gave it, so the crack sentence was read out again for a cake that sank. What counts is not a
    # word the answer said but a word of the entry this line reaches that the earlier entry knows
    # nothing about: `cake-sink` keys on "sink" and `cake-fault` does not, so the sinking speaks.
    if own is not None and getattr(own, "id", None) != earlier.get("id"):
        theirs = _key_words(own) - set(earlier.get("keys") or ())
        hit = (set(words_of(text)) - PROPERTY_WORDS) & theirs
        # A place word is a place here too ("in the fridge", "in the oven"), so it is not a thing
        # of its own - but "sink" is a place word and a verb, and a sinking cake is the cake's.
        # The fresh entry has to be about the word and the last answer not to be: `cake-sink`
        # answers "a cake sinks when...", and no sentence of the crack answer says sink.
        if hit and not (hit & set(words_of(reply))):
            fresh = _payload(own, memory, reading)
            if (isinstance(fresh, str) and fresh.strip()
                    and hit & set(words_of(fresh))):
                return None  # the entry for what this line names answers it, not the last answer
        # The last answer can mention a thing in passing and still not be about it, and then the
        # line naming that thing is the other question: "is a cat ok with a baby" then "what
        # about the pram" was narrowed to the one sentence of the house-rules answer that says
        # pram, when the pram has an entry of its own in another part of the knowledge base
        # (plans.baby-gear). A line that asks nothing by name of a property, about a thing the
        # last answer's entry knows nothing about, and picked up by an entry from another part of
        # the knowledge base, is a change of subject rather than a part of that answer.
        if (hit and asked_kind(text) is None
                and getattr(own, "domain", "") != str(earlier.get("domain") or "")):
            fresh = _payload(own, memory, reading)
            if (isinstance(fresh, str) and fresh.strip() and flat(fresh) != flat(reply)
                    and hit & set(words_of(fresh))):
                return None
    if named:
        if own is not None and named & _key_words(own):
            if getattr(own, "id", None) != earlier.get("id"):
                return None  # a thing of its own, and the entry that answers it is about that thing
            # One entry can answer many things: a table with a row per food answers every food
            # from the same id, so "how much protein in greek yoghurt" after an egg is the same
            # entry and a different thing. When that entry has something to say about this line
            # that is not the answer on the table, the line is about its own thing: the egg's 6g
            # is a wrong fact about yoghurt. An entry with the same answer as before leaves the
            # narrowing alone, because then it really is the same subject.
            fresh = _payload(own, memory, reading)
            if isinstance(fresh, str) and fresh.strip() and flat(fresh) != flat(reply):
                return None
        elif (own is not None and getattr(own, "id", None) != earlier.get("id")
                and _keyed_on_the_line(own, text)):
            # The line reaches an entry of its own, and it is not the entry the last answer came
            # from: "how long does chicken keep in the fridge" then "how long do roast potatoes
            # keep in the fridge" narrowed the chicken answer to its opening sentence, which is a
            # confident wrong keep-time for potatoes. What the line names is not in the last
            # answer, and an entry answers the line itself, so that entry speaks. Only when it
            # has something to say that is not the answer already on the screen.
            fresh = _payload(own, memory, reading)
            if isinstance(fresh, str) and fresh.strip() and flat(fresh) != flat(reply):
                return None
        if (own is not None and getattr(own, "id", None) != earlier.get("id")
                and AMOUNT.search(text) and not AMOUNT.search(reply)
                and _keyed_on_the_line(own, text)):
            # "how long does a 2kg chicken take to roast" after an answer about breasts: the only
            # word the last answer never said is the size, and a size the answer does not state
            # is a question of its own, not a part of that answer. The entry that answers it
            # says one hour forty for a whole bird.
            return None

        # ...and the same when the line reaches an entry of its own from another part of the
        # knowledge base: "how much salt do i put in bread dough" then "how much salt should i
        # eat a day" is a person's daily limit, not the loaf's 10g, and the two questions sharing
        # the word "salt" is what used to hand back the loaf's figure. A part of an answer is
        # asked in the same subject the answer was about (a recipe's flour, a cake's temperature),
        # so a neighbour from another subject with a word of its own in the line answers instead.
        if own is not None and _keyed_on_the_line(own, text):
            mine = getattr(own, "domain", "") or ""
            theirs = str(earlier.get("domain") or "")
            if mine and theirs and mine != theirs:
                return None

    # ...and the same hand-off when the line names nothing new at all. A part is a part of the
    # answer only when it is asked in the same subject: "how do i descale my kettle" then "how
    # long does a kettle take to boil" names only the kettle, which the answer said, and "boil",
    # which is a property word, so nothing looked new and the half-hour soak time was read out
    # as the time to boil. The line reaches the kettle's boiling-time entry, and that entry is
    # about what the line says, so it answers.
    shared = (_key_words(own) & set(earlier.get("keys") or ()) & set(words_of(text))
              if own is not None else set())
    if (shared and getattr(own, "id", None) != earlier.get("id")
            and _keyed_on_the_line(own, text)):
        mine = getattr(own, "domain", "") or ""
        theirs = str(earlier.get("domain") or "")
        if mine and theirs and mine != theirs:
            fresh = _payload(own, memory, reading)
            if (isinstance(fresh, str) and fresh.strip()
                    and flat(fresh) != flat(reply)):
                return None

    # The same table entry also has to be spotted when the earlier answer's *keys* are the whole
    # table: `nutrients-in-food` keeps every food name as a key word, so "greek yoghurt" was
    # treated as a word of the last answer and the egg's figure was narrowed out of it. Only the
    # answer's own words can say whether this line names something new.
    same = own if own is not None else find(reading)
    if same is not None and getattr(same, "id", None) == earlier.get("id"):
        named = set(words_of(text)) - PROPERTY_WORDS - PLACE_WORDS - set(words_of(reply))
        # A figure the last answer never stated is the same entry asked a different question,
        # not a part of the answer: "how much lbtt on a 400000 first home" after the 200000 one
        # was answered by narrowing, which read the old price out of the old answer. An entry
        # that works a figure out from the line (a tax bill, a deposit, a rate for a size) has
        # the new figure; one that replies the same thing again leaves the narrowing alone.
        if named & _key_words(same) or _figures(text) - _figures(reply):
            fresh = _payload(same, memory, reading)
            if isinstance(fresh, str) and fresh.strip() and flat(fresh) != flat(reply):
                return None
    # The same is true of a *different* entry when the last answer's keys are a whole table:
    # `nutrients-in-food` keeps every food it can measure as a key word, so "how much protein in
    # milk" after the yoghurt figure was read as asking about yoghurt and the yoghurt sentence
    # came back instead of the milk one. The words the last answer never said are what decide
    # it: when an entry of its own has something to say about them that is not the answer on the
    # table, that entry speaks.
    other = find(understand(text, memory))
    if other is not None and getattr(other, "id", None) != earlier.get("id"):
        newly = set(words_of(text)) - PROPERTY_WORDS - PLACE_WORDS - set(words_of(reply))
        if newly & _key_words(other):
            fresh = _payload(other, memory, understand(text, memory))
            if isinstance(fresh, str) and fresh.strip() and flat(fresh) != flat(reply):
                return None
    # A conditional answer ("If nothing happens at all, try a different charger and leave it an
    # hour") is all one piece of advice: trimming it to "An hour." drops what to do first.
    if asked_kind(text) == "time" and re.search(r"\bleav(?:e|ing)\b", text):
        for sentence in re.split(r"(?<=[.!?])\s+", reply.strip()):
            if re.match(r"\s*(?:if|unless)\b", sentence, re.I) and re.search(r"\d|\ban?\b", sentence):
                return sentence.strip()
    # A line that names an amount and an answer that states a rate: the rate worked out for
    # their amount is the answer. Narrowing would hand back the figure the answer happens to
    # carry, which is for the size it was written about ("how long for a 1.5kg one" after "20
    # minutes per 500g plus 20 minutes, so a 2kg bird takes about 1 hour 40").
    sized = mem.sized_reply(reply, text, memory, set(earlier.get("keys") or ()))
    if sized:
        return sized
    # A bare figure is the whole of what narrowing can cut when the last answer stated a price:
    # "how much does it cost to charge an electric car" after the cost of a home charger came
    # back as "£800 to £1,200", which is the price of the wrong thing. If the line has an entry
    # of its own, that entry is asking about something the last answer did not price, so it
    # speaks and the figure is left alone.
    own_price = find(understand(text, memory))
    if (own_price is not None and getattr(own_price, "id", None) != earlier.get("id")
            and _only_a_figure(narrow(reply, text))):
        return None
    # A length of time is the same fault as a price, and a worse one on food. "and my oven only
    # fits one tray" answers with a traybake at 200C for 40 minutes; the next line, "how long do
    # i roast a whole chicken", was answered "40 minutes." - a raw bird, where the entry for the
    # bird states one hour forty. The sentence before only gives its figure for the thing it was
    # about, so when the entry this line reaches of its own states a different length of time,
    # that entry answers instead.
    if own_price is not None and getattr(own_price, "id", None) != earlier.get("id"):
        theirs = _key_words(own_price) - set(earlier.get("keys") or ())
        hit = set(words_of(text)) & theirs
        fresh = _payload(own_price, memory, understand(text, memory))
        if (hit and isinstance(fresh, str)
                and _a_figure_apart(narrow(reply, text), fresh)):
            return None
    # "when does it expire" after a keep answer is the same question as "how long does it keep",
    # and the subject is in the earlier answer rather than in the line: `narrow` is told what
    # that answer was about, so it looks for a document there and not in the five words of the
    # line.
    about = " ".join(str(key) for key in (earlier.get("keys") or ()))
    # A follow-up that names its unit ("how many weeks") is answered by the figure written in
    # that unit: the plain narrowing hands back the first length in the answer, and a plan names
    # several, so "how many weeks" after a training plan was answered "20 minutes." - the length
    # of the first session (see narrow.the_part_asked).
    part = the_part_asked(reply, text, about)
    if not (isinstance(part, str) and part.strip()):
        part = _sentence_naming_the_part(reply, text)
    if isinstance(part, str) and part.strip():
        # The part handed back is the whole answer to this line, so it has to state the kind of
        # quantity the line asked for. "and how long before i can play a song" after the guitar
        # cost answer was answered with "Which is most of the songs you already like." - a
        # proportion cut out of that answer for a line that asked how long, and the answer on
        # screen says no length of time about playing a song, so another turn is owed the entry.
        said = KIND_SAID.get(asked_kind(text))
        if said is not None and not said.search(part):
            part = None
        elif (asked_kind(text) == "time" and not re.search(r"\bbefore\b", text, re.I)
              and A_LEAD_TIME.search(_sentence_with(reply, part) or "")):
            # A lead time is not the length of the thing they asked about. `narrow` cuts the
            # figure out and with it the "before the flight" clause it sits in, so the sentence
            # the part came from is what says whether it is a lead time.
            part = None
    if asked_kind(text) == "cause" and isinstance(part, str) and part.strip():
        # The reason was just given: answer with the reason on its own, not the whole answer
        # again. A cause sentence can put the reason first ("A sore knee is usually...: ease
        # off") or after the step it explains ("Restart it: a full phone slows down, so...").
        return _reason_again(_cause_part(part), mem.last_bot(memory) or "")
    return _part_not_repeated(part, mem.entry_answer(memory, text) or reply, memory)


def _the_entry_reply(item, memory, reading):
    """What the entry says, without being said: the price it already names, or an empty string."""
    reply = getattr(item, "reply", None)
    try:
        said = reply(memory, reading) if callable(reply) else reply
    except Exception:  # noqa: BLE001 - an entry that cannot answer says nothing
        return ""
    return said if isinstance(said, str) else ""


def _the_present_with_a_price(text, reading, memory):
    """A present at the price the line gives, or the limit on the present just suggested.

    Only a line that is a present question with a limit on it, or a limit on a present question a
    line or two back, reads here; everything else passes, because an amount is in half the lines
    ever typed ("my budget is 30 pounds" on its own is the money answer).
    """
    money, cheaper = _price_limit(text)
    if money is None and not cheaper:
        return None
    item = _a_gift_entry(reading)
    if item is not None and "\u00a3" in _the_entry_reply(item, memory, reading):
        # An entry that already prices itself answers better than a band does: "what present for
        # a wedding, budget 60" wants the "about 50 pounds is usual" sentence, not an experience.
        return None
    only_a_limit = _only_a_limit(text)
    interests = _the_interests(text, memory, item)
    if item is None:
        if only_a_limit:
            item = _a_gift_just_answered(memory)
            if item is None:
                return None
        elif not GIFT_WORD.search(str(text or "").lower()) \
                and not (interests and _asks_what_to_give(reading)):
            # The words "gift" and "present" are how the order is usually put, and the rows that
            # price a present are reached through them: "what should i get my wife who likes
            # reading for under 100 pounds" names the person, the hobby and the limit and not
            # the noun, so the band was refused and the line fell to the love-language card,
            # which says a book and never mentions the hundred. A line the reading calls a gift
            # ask with a hobby in it is the band's question however it says it.
            return None
    if item is not None and not only_a_limit and not interests \
            and str(getattr(item, "id", "")) != "gift-generic":
        # A present for a named person, with no hobby named, is that person's row: the age picks
        # for a 7 year old, the "buy into it - secateurs for a gardener" answer for a sister. A
        # band fixes the money and forgets the person, so it says a thermos and a book to a
        # question about a child. The band answers where it is better: the limit on its own, a
        # limit as a follow-up to the present just discussed, a hobby it can price, and a line
        # that names no recipient at all.
        return None
    from ..knowledge import shopping
    if money is None:
        return shopping.present_less(interests)
    return shopping.present_within(money, interests)


# A line that asks what something costs wants a figure. It shares words with the entry about
# the thing, which answers the thing instead: "how much roughly to fix" after a noise in the
# brakes reached the entry that says when the noise happens, and a confident diagnosis is not a
# price. The entry states money when it is the answer to this line.
# A line that asks how to do something is a request, not a recall of a fact the store keeps.
_HOW_TO_SHAPES = (r"\bhow\s+(?:do|can|should|would|could|to)\b|\bhow to\b"
                # "what do i do about my budget" is the same request as "how do i budget",
                # and the recall gate above would otherwise hand it to the store. Only the
                # "about my/the" form: "what do i do for a living" is still the store's.
                r"|\bwhat\s+(?:do|can|should|shall)\s+i\s+do\s+about\s+(?:my|our|the|this|that)\b")


HOW_TO = re.compile(_HOW_TO_SHAPES)


MONEY_SAID = re.compile(
    r"£|\$|€|\bquid\b|\bpounds?\b|\bcosts?\b|\bcosting\b|\bprice[ds]?\b|\bpric(?:ey|ier)\b"
    r"|\bexpensive\b|\bcheap(?:er|est)?\b|\bfree\b|\bcharges?\b|\bfees?\b|\bpay\b"
    r"|\b\d+\s?(?:p|quid|pence)\b", re.I)


# The words that make "how much" a price rather than a quantity: an adverb, an auxiliary, a
# preposition or a pronoun, then the verb the price is for ("how much to fix it"), or nothing at
# all ("how much roughly?"). "how much rice" and "how much water" name what is measured, and an
# entry about the food is right to answer those.
PRICE_FILLER = frozenset("""
roughly approximately approx about around maybe usually normally possibly just exactly to for it
that this them those be is are was were do does did would will should can could i you we they he
she my our me us a an the
""".split())


PRICE_VERBS = frozenset("""
fix repair replace get buy hire rent install book cost costs charge pay spend make do take put
sort service deliver fit mend
""".split())


def _asks_a_price(text):
    """Whether the line asks what something costs, rather than how much of a thing there is.

    "how much roughly to fix", "how much for a service", "how much would that be" want a
    figure; "how much rice" and "how much water" want a quantity, and a recipe answers those.
    """
    low = flat(text)
    if re.search(r"\bhow much (?:does|do|is|are|will|would|should|can|could)\b.*"
                 r"\b(?:cost|pay|price|spend|budget)\b|\bwhat(?:'s| is) the price\b"
                 r"|\bhow much for\b", low):
        return True
    found = re.search(r"\bhow much\b(.*)$", low)
    if not found:
        return False
    for word in re.findall(r"[a-z']+", found.group(1)):
        if word in PRICE_FILLER:
            continue
        return word in PRICE_VERBS
    return True


def _names_what_it_wants_priced(text):
    """Whether the price question says what it is for, rather than leaving it to the chat.

    "how much does it cost to fix a dripping tap" names the tap, so the entry about the tap is
    still an answer when nothing states money. "how much roughly to fix", "how much for it" and
    "how much would that be" name nothing but the thing already said, and the entry that fits
    those words is about the thing, not about the price of it: a diagnosis of a noise in the
    brakes is not a price for repairing it.
    """
    found = re.search(r"\bhow much\b(.*)$", flat(text))
    if not found:
        return False
    for word in re.findall(r"[a-z']+", found.group(1)):
        if word in PRICE_FILLER:
            continue
        if word in PRICE_VERBS:
            continue
        return True
    return False


# The line given when the entry a follow-up reaches is the answer already on the screen. The
# answer is about the subject and not the place it was asked about - the ants advice never says
# either room - so it holds where they asked about as well: a person who asks "what about the
# bathroom" gets something useful instead of a search hedge. But the paragraph again word for word
# is the bot repeating itself, so the part of it they have not read is what comes back, under a
# lead-in that names where they asked about.
SAME_WHERE = "The same goes for {thing}: {said}"


# "in the bathroom", "at home", "on the shelf" would read "the same goes for in the bathroom": the
# place is named by the phrase, and the lead-in already has its own preposition. The same is true
# of every other preposition a detail can open on, and they are not only places: "and for cooking"
# after the camping list came back as "The same goes for the for cooking: ...", and "what about
# with kids" as "the with kids". A detail is the noun the person named, and the preposition in
# front of it is theirs, not part of its name.
LEAD_PREPOSITION = frozenset("""in at on inside into for with about to of from by without after
                                before like using around near over under between""".split())


# The most a line handed back this way can be: one line of the answer, not another paragraph.
MOST_SAME = 220


# "bathroom" on its own reads "the same goes for bathroom": the thing is named with the word
# that says which one, and a line that already has one keeps it ("my freezer", "the oven door").
DETERMINER = frozenset("the a an my our your his her its their this that these those".split())


# An elided follow-up reads a bare "again" as the thing it names - "what about again" - and
# "The same goes for the again: iron it while it is still damp" is a sentence nobody wrote. The
# line that asks for the answer a second time names no thing for the answer to be handed to.
NOT_A_THING = frozenset("again pardon sorry eh huh".split())


# Everything a line can be made of and still be only the ask to hear the answer again. The line
# reaches the detail reading folded - "pardon?" arrives as "what about pardon" - so the wrapper
# words are here beside the ask itself, and a line made of nothing else names no part of the
# answer to say it again for.
ONLY_THE_ASK = NOT_A_THING | frozenset("""
    what about again say said come then please it that this you was just now one more time
    """.split())


# The lead-in above puts the new thing in a noun slot ("the same goes for the bathroom", "the same
# goes for the snails"), which is right for a thing and wrong for a sentence. A line that opens on
# a pronoun is a sentence about the subject in hand, not the name of a new one: "hes a spaniel"
# after the lead question came back as "The same goes for the hes a spaniel: Train the lead as a
# stop-and-go game", and the same shape waits behind "its a big dog", "we have two kids" and
# "nothing too heavy". Those keep the answer and lose the frame.
CLAUSE_START = frozenset("""
he hes she shes it its i im ive ill id you youre youve we weve were they theyre theyve
that thats this these those there nothing something anything everything nobody somebody
anybody everybody
""".split())


# The answer, said again for what they told you, with no thing for the frame to name.
SAME_PLAIN = "Then the same holds: {said}"


def _same_where_they_asked(text, said):
    """The part of that answer the new thing has not been given yet, or "" for none left."""
    thing = swap.thing(text)
    if not thing:
        return ""
    # Only the words that ask for the answer again: there is no thing here to hand it to.
    if all(word in NOT_A_THING for word in re.findall(r"[a-z']+", thing.lower())):
        return ""
    # A line judging the answer as doable names no thing to hand it to either: "sounds doable"
    # came back as "The same goes for the sounds doable: ...", which is the judgement said back
    # as if the person had named a part of the job. Asked of the composer's own reading, so the
    # two cannot disagree about whether the line is about the answer or about a thing.
    from ..compose import fallback
    if fallback.reads_as_a_judgement(text):
        return ""
    # A sentence about the thing in hand is not the name of a new one, so it keeps the answer and
    # loses the "the same goes for the ..." frame: a pronoun is never how a thing is named.
    clause = bool(re.findall(r"[a-z']+", thing.lower())[:1]
                  and re.findall(r"[a-z']+", thing.lower())[0] in CLAUSE_START)
    words = thing.split()
    if len(words) > 1 and words[0].lower() in LEAD_PREPOSITION:
        words = words[1:]
    if (not clause and words[0].lower() not in DETERMINER
            and not (len(words) == 1 and words[0].endswith("ing"))):
        # "the same goes for the cooking" is one determiner too many: an activity named by its
        # gerund is the name of the thing, not a countable one of them.
        words = ["the"] + words
    thing = " ".join(words)
    # The room named in the thing, which is what a sentence about another room is read as.
    room = next((word for word in re.findall(r"[a-z']+", thing.lower())
                 if word.rstrip("s") in ROOMS), "")
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", str(said or "")) if part.strip()]
    asked = {word.rstrip("s") or word for word in re.findall(r"[a-z']+", thing.lower())}
    # The first sentence is usually the thing to do, so it is tried first: the method is what a
    # person asking about the new thing needs, and handing over only the aside is worse than a
    # hedge. "how do i get rid of slugs / what about snails" gave "Encourage birds and frogs, and
    # water in the morning" while "go out after dark with a torch" - still true of snails - went
    # unsaid.
    for part in parts:
        for piece in _the_method_in(part):
            if len(piece.split()) < 5 or len(piece) < 30 or len(piece) > MOST_SAME:
                continue
            if not _holds_where_they_asked(piece, asked):
                continue
            line = _mid_sentence(piece.rstrip(" ."))
            line = _room_they_asked_about(line, asked, room)
            if not line.endswith((".", "!", "?")):
                line += "."
            # The answer follows a colon, so its opening capital is the only thing making it a
            # sentence of its own: "The same goes for the bathroom: use a mid-sheen..." is the
            # one sentence STYLE.md asks for.
            if clause:
                return SAME_PLAIN.format(said=_small_letter(line))
            return SAME_WHERE.format(thing=thing, said=_small_letter(line))
    return ""


def _mid_sentence(part):
    """The line with its opening capital taken off, when it is only a capital because it began.

    A sentence that starts "The usual hiding places are the door seal" carries the same words in
    lower case later on, which is how this knows the first word is not a name: "Paris is the one"
    keeps its capital, because nothing later in the line says "paris".
    """
    tokens = re.findall(r"[A-Za-z']+", part)
    if len(tokens) < 2 or not part[0].isupper():
        return part
    if tokens[0].lower() in [word.lower() for word in tokens[1:]]:
        return part[0].lower() + part[1:]
    return part


# The rooms and outside places an answer can be handed to another of. A part of a house is the
# same kind of place as another part of a house: advice about a bedroom's damp holds in a bathroom,
# and advice about a fridge's door seal holds nowhere but a fridge. It is not a topic list - it is
# what tells "somewhere else in the house" from "some other thing".
ROOMS = frozenset("""room kitchen bathroom bedroom loo toilet ensuite hall hallway landing lounge
living dining garage shed garden conservatory study nursery attic loft cellar basement porch patio
balcony utility laundry cloakroom downstairs upstairs flat house home""".split())


# The places a sentence can name, for telling a line that holds anywhere from one written about
# somewhere else. Wider than ROOMS: a lawn, a path and a flowerbed are different places although
# none of them is a room.
NAMED_PLACES = ROOMS | frozenset("""lawn grass flowerbed patio path gravel drive yard plot
allotment greenhouse""".split())


def _holds_where_they_asked(part, asked):
    """Whether a sentence of the earlier answer is about the place asked about, or about none.

    "on a lawn, feed and mow it properly ... on a patio, path or gravel, hoe or flame them young"
    was handed to a flowerbed under "The same goes for the flowerbed:", which says the opposite of
    what the sentence says. A sentence that names another place is only handed over when that
    place is another of the same kind - a bedroom's advice in a bathroom.
    """
    named = {word.rstrip("s") or word
             for word in re.findall(r"[a-z']+", str(part or "").lower())} & NAMED_PLACES
    if not named or named & asked:
        return True
    return bool(named & ROOMS) and bool(asked & ROOMS)


def _the_method_in(part):
    """The sentence, and the part of it after a colon when it has one.

    A long opening sentence of an advice paragraph often carries the reason first and the thing
    to do after a colon ("Condensation comes from warm wet air hitting cold surfaces ...: use the
    extractor fan, open a window for 10 minutes a day"). The whole sentence is too long to hand
    over, and the clause after the colon is the part a person can act on.
    """
    pieces = [part]
    if ": " in part:
        pieces.append(part.split(": ", 1)[1])
    return pieces


def _room_they_asked_about(line, asked, room):
    """The line with another room in it read as the one they asked about.

    A sentence that holds anywhere in a house can still name where it was first written: the
    dehumidifier line of the condensation answer says "in a bedroom that gets it badly", and
    handed to a bathroom under "The same goes for the bathroom:" it says the opposite of what
    the lead-in claims. The room they asked about is the room in the sentence when it is the
    same kind of place, so the sentence is about the room they asked about.
    """
    if not room or not asked:
        return line
    found = {word.rstrip("s") or word
             for word in re.findall(r"[a-z']+", str(line or "").lower())} & ROOMS
    others = found - asked
    if len(others) != 1:
        return line
    other = others.pop()
    name = room.rstrip("s") or room
    return re.sub(r"\b%s(s?)\b" % re.escape(other), lambda m: name + (m.group(1) or ""),
                  line, flags=re.I)


def _a_place_of_the_same_kind(earlier, text):
    """True when the place they now ask about is another of the kind the answer was about.

    The condensation advice is about a bedroom, so it is about a bathroom too and can be handed
    over with the bathroom named. The fridge answer is about a fridge, which is not a room, so
    "what about in the garage" is a different thing and gets the honest hedge rather than a
    paragraph about door seals.
    """
    if not isinstance(earlier, dict):
        return False
    asked = {word.rstrip("s") or word
             for word in re.findall(r"[a-z']+", (swap.thing(text) or "").lower())}
    keys = {str(word).lower() for word in (earlier.get("keys") or ())}
    return bool(asked & ROOMS) and bool(keys & ROOMS)


def _a_place_they_asked(text):
    """True when the follow-up names a place with a place's own preposition.

    "and in the bathroom", "what about under the sink". A bare thing ("what about the cake",
    "and what about a turkey") is not one: the answer about a table is not the answer about a
    cake, and saying it again with the cake's name in front would be worse than a hedge.
    """
    words = (swap.thing(text) or "").split()
    return bool(words) and words[0].strip("?.!,;:").lower() in swap.PREPOSITION


def _key_terms(item):
    """Every phrase the entry is keyed on, however deeply its key is nested.

    An entry's `key` is a tuple of groups, but some entries are written with the phrases in the
    tuple itself (`('slugs', 'snails', ('keep', 'stop', ...))`), so iterating it once gives the
    letters of a phrase rather than the phrase. Walking it to the strings is what both readers
    below need.
    """
    def walk(node):
        if isinstance(node, str):
            return [node]
        try:
            children = list(node)
        except TypeError:
            return []
        out = []
        for child in children:
            out.extend(walk(child))
        return out
    return walk(getattr(item, "key", None) or ())


def _written_for(item, thing):
    """True when one of the entry's own key words is the thing, or covers it.

    The ants entry is keyed "ants" against "kitchen, bait, cupboard, sugar", and the fridge entry
    is keyed "fridge, freezer" against "smell, stink". A follow-up that changes one of those
    words ("what about the bathroom", "what about the freezer") reaches the same entry, and the
    entry was written with both of them in mind.
    """
    if item is None:
        return False
    words = set(re.findall(r"[a-z']+", str(thing or "").lower()))
    if not words:
        return False
    for term in _key_terms(item):
        own = set(re.findall(r"[a-z']+", term.lower()))
        if own and (words <= own or own <= words):
            return True
    return False


def _more_than_the_thing(item, rest):
    """True when a key of the entry also names something in the rest of the question.

    "The smell in the shed" finds the entry for shedding weight, which is keyed "shed" - one word
    shared by chance, and its answer is about eating. The sink entry reached by "and under the
    sink" after the shower is keyed "sink" and "clean", and the question was a how-do-i-clean
    one. One shared word is enough when it is the thing being asked about; a key word that the
    rest of the question also says is what tells the two apart.
    """
    if item is None:
        return False
    rest_words = set(re.findall(r"[a-z']+", str(rest or "").lower()))
    if not rest_words:
        return False
    for term in _key_terms(item):
        own = set(re.findall(r"[a-z']+", term.lower()))
        # A key term made only of question words ("how") says nothing about the subject.
        if own and own <= rest_words and not own <= swap.STOP:
            return True
    return False


def _about_the_rest_of_the_question(item, question, new):
    """True when the entry's own subject words are in the question besides the new thing.

    An entry is reached by a question about the thing the follow-up named, and its reply names
    the subject, not the room the subject is in: the ants entry answers "ants in the bathroom"
    with "wipe the trail away ... do not spray the line they are following", which never says
    either room. Reading the reply for the words of the question turned that answer down and
    left the person with a search hedge, when the answer they already have is the answer.

    The entry's own subject words say what it is about, and the rest of the question (the words
    that are not the new thing) is what the follow-up kept asking about.
    """
    key = getattr(item, "key", None) or ()
    subject = key[0] if key else ()
    if not subject:
        return False
    new_words = re.findall(r"[a-z']+", str(new or "").lower())
    if not new_words or new_words[0] not in swap.PREPOSITION:
        # Only a place is read this way. A thing swapped into a question that named none asks a
        # different question - "what should i make thats not too fiddly" / "and what about the
        # cake" reached the party-food entry that answered the turn before - and an entry about
        # the old subject is not an entry about the cake.
        return False
    asked = set(re.findall(r"[a-z']+", str(question or "").lower()))
    left = asked - set(new_words)
    for term in subject:
        words = re.findall(r"[a-z']+", str(term or "").lower())
        if words and all(word in left for word in words):
            return True
    return False


KEEPING_FROM_THE_ANSWER = "keeping-from-the-answer"


def _keeping_in_the_answer_before(memory):
    """The sentence of the answer just given that says how long the thing in hand keeps, or "".

    "i want to make stock from the chicken carcass" ends "it keeps 4 days in the fridge or 3
    months frozen". Two steps of the same job later ("how long do i simmer it", "and how long do
    i cool it for" - the second one answered with that whole sentence again) the person's "how
    long does it keep" was answered from the general cooked-food table: a card about cooked food,
    raw meat and rice, with neither the stock in it nor the 3 months. The table is the answer for
    a thing we cannot name; here the answer just given already carries the figure, and a wide card
    must not be handed over in place of it.
    """
    said = str(mem.last_bot(memory) or "").strip()
    if not said:
        return ""
    for sentence in SENTENCE.split(said):
        sentence = sentence.strip()
        if not (cooking.speaks_of_keeping(sentence) and KEEPS_A_FIGURE.search(sentence)):
            continue
        # The lead-in says what to do with it ("Strain it, cool it fast and"), not how long it
        # keeps, and the whole sentence just said reads as the bot repeating itself: the person
        # gets the keeping clause, which is what they asked for.
        keep_at = KEEPING_CLAUSE.search(sentence)
        if keep_at and keep_at.start() > 0:
            lead = sentence[:keep_at.start()].rstrip(" ,;:-")
            if lead and ("," in lead or " and" in lead.lower()):
                sentence = sentence[keep_at.start():]
                sentence = sentence[:1].upper() + sentence[1:]
        if sentence.strip() == said.strip():
            continue  # the same words again are no answer: leave it to the entry below
        return sentence.strip()
    return ""


# Where the keeping clause starts in a sentence: "Strain it, cool it fast and it keeps 4 days".
KEEPING_CLAUSE = re.compile(r"\b(?:it|they|that|this|these|those)\s+(?:keeps?|lasts?|freez(?:e|es))\b",
                            re.I)


# A keeping sentence with a length of time in it. The keeping table's own phrase ("the label's
# once-opened line beats any general rule") says nothing about how long anything keeps.
KEEPS_A_FIGURE = re.compile(
    r"\b\d+\s*(?:-|to)?\s*\d*\s*(?:day|days|week|weeks|month|months|year|years)\b"
    r"|\ba (?:day|week|month|year)\b|\bcouple of (?:days|weeks|months)\b", re.I)


# A temperature in an answer, and the number in it: "190C", "180 degrees".
DEGREES = re.compile(r"\b(\d{2,3})\s*(?:c\b|degrees)", re.I)


# A thing that has been cooked, and the words a line uses for what is left of it. The plan's
# keep fact is about leftovers, so it is only the answer when there is something cooked to have
# left over: "half a roast chicken left over" yes, "raw chicken in the fridge" no.
COOKED_THING = frozenset("""
cooked cook roast roasted bake baked fry fried grill grilled boil boiled poach poached steam
steamed leftover leftovers made reheat reheated rest rested
""".split())


def _cooked_thing(memory):
    """True when the thing the conversation is on has been cooked already."""
    return bool(set((mem.subject(memory) or "").split()) & COOKED_THING)


# A keeping answer says how long the food lasts in the fridge; it is not how long the pan
# takes. Both halves are needed before the guard fires, and neither alone is rare: "keeps" and
# "days" are in half the kitchen's answers, and "cook" is in half its questions.
COOK_VERB = re.compile(r"\b(?:cook|boil|bake|roast|fry|grill|simmer|steam|reheat|air-?fry|"
                       r"poach|braise|pressure cook)\b", re.I)


KEEPS_ANSWER = re.compile(r"\b(?:keeps?|lasts?|freezes?|fridge|freezer|cooler)\b", re.I)


KEEPS_ASK = re.compile(r"\b(?:keep|keeps|keeping|last|lasts|lasting|fridge|freezer|freeze|"
                       r"frozen|leftover|leftovers|left over|store|stored)\b", re.I)
