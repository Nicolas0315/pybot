"""Part 4 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import re

from .. import memory as mem
from ..compose import lead
from ..knowledge import entries as all_entries, home
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import named
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import keywords
from ..memory import again as same_again  # the short of an answer already on the screen
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory.topics import AMOUNT
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import keywords, swap
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory.narrow import CAUSE, flat, kind_of as asked_kind, narrow, words_of
from ..understanding import understand
from .answers_part_01 import (
    SENTENCE, _flat, REFERRING,
)
from .answers_part_02 import (
    _own_thing, TIME_WORD, _key_words,
)
from .answers_part_03 import (
    ABOUT_THE_ANSWER, ASKING_FRESH, DEPENDENT_SENTENCE, DIGIT_OR_SPAN, OPTION_TIMING,
    YES_NO_ABOUT_A_THING, _last_answer, A_TRADE, CONDITIONS_THE_LINE, MOST_ACKS, OPENING_CONNECTIVE,
    SAYS_TO_GET_SOMEBODY, SOMEONE_TO_GET, WHO_ASK_WORDS, WHO_TO_CALL, _a_stock_acknowledgement,
    _the_clause_that_says_who, PROPERTY_WORDS,
)


def _the_sentence_about(text, memory):
    """The sentence of the last answer that answers a yes/no about a thing it named, or None.

    "will salt work" after the red-wine carpet answer is answered by the sentence that names
    salt; the whole paragraph again is not, and a shrug is worse than both. The guards keep it
    to a follow-up: a short line, a yes/no shape, and every word of the line but the ones about
    the answer itself already in the answer, so a line naming a new thing ("will a dehumidifier
    help") is left for the entries.
    """
    earlier = _last_answer(memory)
    if not earlier:
        return None
    reply = earlier.get("reply") or ""
    if not reply.strip() or len(text.split()) > 7:
        return None
    # A line that names a figure or a span ("its been there an hour", "for 2 days?") asks about
    # that figure, not about a thing in the answer, however few words it has: the amount readers
    # in this module work the figure out from the answer's own rule.
    if DIGIT_OR_SPAN.search(text):
        return None
    # A yes/no ("will salt work") or the bare name of the thing ("salt?", "white wine?"): both
    # ask about the answer rather than bringing a question of their own. A short question that
    # asks for the doing or the figure ("what should i do", "how long?") is asking afresh, so it
    # is not read here however few words it has.
    said_so_far = words_of(text)
    # The ask words are read off the line as typed, not off its content words: "what should i
    # say" is one content word ("say") and would pass for the bare name of a thing, and the
    # thing it would name is the advice the answer already gave - said again word for word.
    asked_fresh = ASKING_FRESH.intersection(re.findall(r"[a-z']+", flat(text)))
    if not (YES_NO_ABOUT_A_THING.search(flat(text))
            or (len(said_so_far) <= 3 and not asked_fresh)):
        return None
    said = set(words_of(reply)) | set(earlier.get("keys") or ())
    named, other = [], False
    for word in words_of(text):
        if word in ABOUT_THE_ANSWER or len(word) < 3:
            continue
        if word in said:
            named.append(word)
        else:
            other = True
    if not named or other:
        return None
    sentences = same_again.quoted.sentences(reply, SENTENCE)
    holding = [one for one in sentences if all(word in set(words_of(one)) for word in named)]
    if len(holding) != 1 or len(sentences) < 2:
        return None
    part = holding[0]
    if flat(part) == flat(reply):
        return None
    # A sentence that offers the same dish in several times over ("tuna pasta in 15, macaroni
    # cheese in 25, or a sausage traybake in 45") is a menu of options, not the answer to a line
    # that picks one of them: the thing the line names is one of the choices, and handing the
    # menu back is repeating the answer the person just chose from.
    if len(OPTION_TIMING.findall(part)) >= 2:
        return None
    # A sentence that leans on the one before it is not a reply on its own: "there is chilli as
    # well" answers "chilli?" after a spaghetti bolognese answer with a clause about somebody
    # else's dinner, and a shrug reads better than a fragment.
    if DEPENDENT_SENTENCE.match(part) or len(part) < 40:
        return None
    return _part_not_repeated(part, reply, memory)


def _the_person_to_call(text, memory):
    """The sentence of the last answer that says who to get, for a "who should I call", or None.

    Only a line that is the asking and nothing else: a word of its own ("who should i call about
    my car") names a thing the entries answer, and the sentence of an unrelated answer is a
    worse reply than leaving the turn alone.
    """
    if not WHO_TO_CALL.search(flat(text)):
        return None
    spare = [word for word in words_of(text) if word not in WHO_ASK_WORDS and len(word) > 2]
    if spare:
        return None
    # The answer on the screen is the turn before this one, read off the chat rather than off
    # `_last_answer`: that record ends with the topic, and the ask here is a new topic with none
    # of the answer's words in it, so it is exactly the case the record drops.
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    last = turns[-1]
    if last.get("module") != "answers":
        skipped = 0
        while (skipped < MOST_ACKS and len(turns) - 1 - skipped >= 0
               and _a_stock_acknowledgement(turns, skipped)):
            skipped += 1
        if not skipped or len(turns) - 1 - skipped < 0:
            return None
        last = turns[-1 - skipped]
        if last.get("module") != "answers":
            return None
    reply = str(last.get("bot") or "").strip()
    if not reply:
        return None
    sentences = [one.strip() for one in SENTENCE.split(reply) if one.strip()]
    if len(sentences) < 2:
        return None
    holding = [one for one in sentences
               if A_TRADE.intersection(re.findall(r"[a-z']+", one.lower()))]
    if not holding:
        return None
    # The sentence that both names somebody and says to get them answers the ask; a sentence
    # that only mentions a trade ("gas work is theirs by law") is the answer to another question.
    # Of those, the one that says to get somebody first ("Then get a roofer out") beats one that
    # names a person inside a condition ("If you rent, tell the landlord"), which is advice for
    # a renter rather than the answer to the ask.
    getting = [one for one in holding if SOMEONE_TO_GET.search(one)]
    pool = getting or holding
    stating = [one for one in pool if not CONDITIONS_THE_LINE.match(one)]
    pool = stating or pool
    up_front = [one for one in pool if SAYS_TO_GET_SOMEBODY.match(one)]
    # The reply has to name who to get. A sentence that mentions a trade in passing ("a brush
    # strip on the door, a chimney balloon") is not the answer to the ask, and handing back the
    # condition half of a sentence ("If it has been more than six weeks ...") answers nothing at
    # all: the clause that says to see the GP is the one that was cut off in front of it.
    ordered = up_front + [one for one in pool if one not in up_front]
    named = [one for one in ordered
             if A_TRADE.intersection(re.findall(r"[a-z']+", one.lower()))]
    if not named:
        return None
    part = named[0]
    # A sentence of a paragraph leans on the one before it ("Then get a roofer out"): said on its
    # own, the connecting word goes with the sentence it connected to.
    stripped = OPENING_CONNECTIVE.sub("", part).strip()
    if stripped != part and stripped:
        part = stripped[:1].upper() + stripped[1:]
    if len(part) < 25 or not part[:1].isupper() or DEPENDENT_SENTENCE.match(part):
        return None
    part = _the_clause_that_says_who(part)
    return _part_not_repeated(part, reply, memory)


# A line that replaces the size the answer worked from with one of its own: "make it 2kg instead",
# "do it now instead" - the ask is made again at a new size, and no thing is being substituted.
SIZE_REPLACED = re.compile(r"\b(?:instead|now|this\s+time)\b", re.I)


def _the_amount_they_named_again(text, memory):
    """The sentence of the last answer that gives the amount this line names, or None.

    "make it 2kg instead" after the timing for a 2kg bird names the size the answer has already
    worked out: there is no new figure to work out, and it is not a substitution - "instead" here
    means "instead of the size you assumed". Nothing read it that way. The size was the only
    content word left, so `_amount_asked` declined it (the answer already states 2kg) and the turn
    fell through to the context reader, which writes the line out with the last subject on it
    ("make the chicken oven 2kg instead"). The table's stand-in row is keyed on the word
    "instead", so that reading answered "Swap in pulses: red lentils for mince". The figure the
    person asked for is on the screen, so say the sentence of the answer that carries it.
    """
    earlier = _last_answer(memory)
    reply = str((earlier or {}).get("reply") or "").strip()
    if not reply:
        return None
    amounts = [one.group(0) for one in AMOUNT.finditer(text)]
    if len(amounts) != 1:
        return None  # one size or none: two is a comparison, and no size is not this line
    if not SIZE_REPLACED.search(text):
        return None  # nothing says a size is being replaced
    if not re.search(r"(?:^|[^\w])" + re.escape(amounts[0]) + r"(?:[^\w]|$)", reply, re.I):
        return None  # the answer gives another size, so the figure has to be worked out
    if swap.thing(text):
        return None  # the line names the thing to stand in for: that is a substitution
    if _own_thing(understand(text, memory)):
        return None  # the line names a thing of its own, so it is not a follow-up about a size
    sentences = [one for one in SENTENCE.split(reply) if one.strip()]
    carrying = [one for one in sentences if re.search(re.escape(amounts[0]), one, re.I)]
    if not carrying:
        return None
    # The shortest sentence that carries the size is the one written for it: the rate sentence
    # ("20 minutes per 500g plus 20") says nothing about the size asked.
    best = min(carrying, key=lambda one: len(one)).strip()
    # The size usually sits in the second half of a rate sentence - "20 minutes per 500g plus 20,
    # so a 2kg bird takes 1 hour 40" - and the opening half is the rate the person has just read.
    # A sentence said back from the front of the answer is the paragraph on the screen again as
    # far as the turn is concerned (`_short_form_of_the_last`), so the size's own clause is what
    # is said, and only when it carries the amount by itself.
    # The size is often the second half of a sentence whose first half is the rate the person has
    # just read ("a leg of lamb is 25 minutes per 500g ..., then 15 minutes resting: about 1 hour
    # 5 in total for a 2kg leg"), so the half after the last break that still carries the size is
    # what is said. A sentence said back from its own front is the paragraph on the screen again
    # as far as the turn is concerned (`_short_form_of_the_last`).
    for lead in (": ", ", so ", " so ", ", which means ", " \u2014 ", ", then ", "; "):
        cut = best.rfind(lead)
        if cut < 0:
            continue
        tail = best[cut + len(lead):].strip()
        if re.search(re.escape(amounts[0]), tail, re.I):
            best = tail
            break
    return best[:1].upper() + best[1:] if best else None


# The shapes a question about the machine takes: worth it, repair or replace, who to ring, and a
# plain yes/no ("should i get someone in"). Without one of these the line is not asking about the
# machine at all, whatever trigger words it happens to carry.
MACHINE_ASKING = re.compile(
    r"\b(?:worth|should|shall|is it|is that|would|could|can i|do i|who|whom|what|how|where|when|"
    r"why|or new|or replace|fix|fixing|repair|repairing|replace|replacing|salvage|scrap)\b")


def _the_machine_follow_up(text, reading, memory):
    """The decision about the machine the last line named, when this line names none of its own.

    "the washing machine smells of damp" then "is it worth getting someone in" is a money question
    about that washing machine, and the second line has neither the machine nor the fault in it,
    so nothing in the knowledge base could reach the repair rule and the person got "not mine to
    decide" straight after a good answer (sky-tuna, #answers). The machine and the fault are in
    the line before, so the rule reads both lines. The same goes for "is it worth fixing" and
    "shall i just replace it", which point back with a pronoun. A line that names a machine of its
    own is left alone: that is its own entry's question.
    """
    line = _flat(text)
    if home.machine_named(line):
        return None  # its own machine, so its own entry's question
    # It has to be a question. The trigger words are ordinary words, so a statement about the
    # person carrying them was read as a question about the machine: "the boiler is broken" then
    # "i work as an engineer" got the Gas Safe rule off the bare word "engineer", "the washing
    # machine is broken" then "i got a quote for a new kitchen" got the repair rule off "quote",
    # and "... then my dad looked at it and gave up" got it off "looked at" and "it" (friendly-
    # cobra, #1933). A confident answer to a question nobody asked is worse than a weak one.
    if not MACHINE_ASKING.search(line):
        return None
    asks = home.CALLING_SOMEONE.search(line) or (
        home.FOLLOWING_IT.search(line) and home.DECIDING_NOW.search(line))
    if not asks:
        return None
    earlier = home.machine_before(memory)
    if not earlier:
        return None
    # The decision is about the machine, so it is the answer to a question about the machine. A
    # line that names a part of it ("is it worth cleaning the filter") is a question about the
    # answer just given, and the sentence of that answer which speaks of the part is the answer:
    # the repair rule, which talks of quotes and new machines, says nothing about the filter.
    part = narrow(mem.last_bot(memory) or "", text)
    if part:
        return part
    reply = home.the_machine_decision(memory, earlier, line)
    return reply if isinstance(reply, str) and reply.strip() else None


# "when do i take it" after a tablet's card asks what time of day, and understanding reads the
# bare "when" as asking for a date. The date reader then cut the one date out of the card that
# answered before - "Three months.", the interval to the blood test - where the timing question
# wants the entry's own answer ("same time each day, and for most statins that is the evening").
# "What time of day should i take them" is read as `clock` already and answered by the entry, so
# this only catches the ones the reading misses: a "when"/"what time" and then a routine verb with
# the thing it is done to.
WHEN_OF_THE_DAY = re.compile(
    r"\b(?:when|what\s+time)\b[^.?!]*\b(?:take|taking|use|using|eat|eating|have|having|do|doing|"
    r"put|apply|give)\s+(?:it|them|this|these|those|one|mine|the\s+\w+)\b", re.I)


# An answer that gives a quantity by proportion rather than in figures: "use the same weight of
# butter", "half as much sugar", "twice the rice to the water".
PROPORTION = re.compile(r"\b(?:same weight|same amount|equal|half as much|twice|double\b|"
                        r"three times|two parts|one part)\b|\d", re.I)


# A clause that gives a quantity in units ("one mug of rice to one and a half mugs of water"),
# whether the number is written as a digit or as a word.
MEASURE = re.compile(r"\d|\b(?:mug|mugs|cup|cups|spoon|spoons|teaspoons?|tablespoons?"
                     r"|grams?|kilograms?|kilos?|ml|litres?|liters?|pints?|ounces?|oz"
                     r"|pounds?|handfuls?|pinch(?:es)?)\b", re.I)


# The words that can put a quantity in front of the thing it is a quantity of: "100g plain
# flour", "one and a half mugs of water", "three eggs".
_AMOUNT_BEFORE = (r"\d+(?:\.\d+)?\s*(?:g|kg|ml|cl|l|oz|lb|cm)?|one|two|three|four|five|six|"
                  r"seven|eight|nine|ten|eleven|twelve|half|quarter|dozen|mugs?|cups?|spoons?|"
                  r"teaspoons?|tablespoons?|grams?|kilograms?|kilos?|litres?|liters?|pints?|"
                  r"ounces?|pounds?|handfuls?|pinch(?:es)?")


# A quantity given by proportion rather than in figures: "use the same weight of butter".
_PROPORTION_PHRASE = (r"same weight|same amount|equal weight|equal amount|half as much|twice|"
                      r"double|three times")


def _amount_for_the_name(clause, named):
    """True when the clause ties a quantity to that very thing, not to a neighbour.

    "Weigh the eggs and use the same weight of soft butter" gives an amount for the butter, so
    "how many eggs" must not be answered with it; "three eggs fills two tins" does answer it.
    The number or unit has to sit right before the word that was asked about, or a proportion
    phrase has to lead to it a few words later.

    The words are read with their joining words in ("the same weight of soft butter"), because
    "of" and "same" are exactly what says the amount belongs to the thing after them.
    """
    text = " " + re.sub(r"[^a-z0-9. ]+", " ", str(clause).lower()) + " "
    for name in {str(one).lower() for one in named}:
        thing = re.escape(name.rstrip("s")) + r"s?"
        if re.search(r"\b(?:" + _AMOUNT_BEFORE + r")\s+(?:[a-z]+\s+){0,2}" + thing + r"\b",
                     text):
            return True
        if re.search(r"\b(?:" + _PROPORTION_PHRASE + r")\s+(?:[a-z]+\s+){0,3}" + thing
                     + r"\b", text):
            return True
    return False


# Where one clause of an answer ends and the next begins.
#
# A comma inside a number is part of the number: "About 7,000 to 8,000 steps a day" cut at its
# comma leaves "000 steps a day is where most of the benefit is", which was said back as the
# answer to "how many steps in a 5k"; "£400,000" left "000 first home in Scotland" for the
# same reason, and a boiler price cut at its comma was "800 to £3.". So a comma is a seam only
# when it is not between two digits - and it has to be written so that no wider alternative can
# match it first: a plain [:,;] character class in front of the guard swallows every comma and
# the guard never runs, which is how "000 steps a day" got through.
CLAUSE_SEAM = re.compile(r"(?:(?<=\D)[:,;]|[:,;](?=\D))|\bthen\b")


# The kind of quantity a line asks for, said in a part of an answer. Only the kinds that cannot be
# said without their own words are checked; an amount ("how much sugar") can be given by
# proportion ("the same weight of sugar"), which is the case the part reader exists for.
KIND_SAID = {
    "time": re.compile(r"\d|\b(?:an?|one|two|three|four|five|six|seven|eight|nine|ten|twelve|"
                       r"fifteen|twenty|thirty|forty|fifty|sixty|ninety|hundred)\s+"
                       r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?)\b"
                       r"|\bovernight\b|\ba few (?:hours?|days?|weeks?|months?)\b", re.I),
    "money": re.compile(r"£\s*\d|\b\d[\d,.]*\s*(?:pounds?|quid|dollars?|euros?)\b", re.I),
    "heat": re.compile(r"\d\s*(?:°|degrees?|gas mark|C\b|F\b)", re.I),
    "distance": re.compile(r"\d\s*(?:miles?|km|kilometres?|kilometers?|metres?|meters?|yards?|"
                           r"feet|foot)\b", re.I),
    "clock": re.compile(r"\b\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm|o'clock)\b|\b\d{1,2}[:.]\d{2}\b",
                        re.I),
}


# The words a clause cannot start with, because they tie it to the clause before it. A clause
# cut at a comma that begins with one of these is half a sentence, not an answer.
JOINING_WORD = re.compile(r"^\s*(?:which|that|who|whom|whose|where|because|though|although"
                          r"|whereas|while|yet|however|instead|plus|as well)\b", re.I)


def _sentence_naming_the_part(reply, text):
    """The clause of the answer that gives a quantity for the thing a follow-up asks about.

    Some answers give a quantity by proportion instead of in figures: "how do i make a cake"
    says to weigh four eggs and use the same weight of butter, sugar and flour, so "how much
    sugar" has no number to read out and the figure reader returned nothing, and the question
    got a shrug. The clause that gives it is the answer, and it is part of the answer just
    given, not a new one.

    The amount has to be for the thing that was named: a sentence that only mentions the word
    ("Caster sugar and self-raising flour.") is not an amount, and a sentence whose amount
    belongs to something else ("the same weight of soft butter" for "how many eggs") is a
    wrong answer where a shrug was right.
    """
    kind = asked_kind(text)
    if kind is None or kind in ("cause", "order"):
        return None
    # The same words the part reader counts as a thing: "how long do they go in for?" names
    # nothing ("go" is a verb), so it cannot pick a clause out of an answer by its words.
    named = set(words_of(text)) - PROPERTY_WORDS - NOT_NEW - WHERE_WORDS
    if not named:
        return None
    sentences = [one.strip() for one in SENTENCE.split(str(reply or "").strip()) if one.strip()]
    if not sentences:
        return None
    flat_reply = _flat(reply)
    for sentence in sentences:
        for clause in CLAUSE_SEAM.split(sentence):
            clause = clause.strip(" .,")
            if not clause or not named & set(words_of(clause)):
                continue
            if not _amount_for_the_name(clause, named):
                continue
            # A list split by its commas leaves fragments that say "half white vinegar": the
            # amount is there and the thing is there, but it is a piece of a list rather than a
            # sentence, and "Half white vinegar." is no answer at all. A real clause carries a
            # ratio or enough words to read as one.
            if len(clause.split()) < 4 and not re.search(r"\b(?:of|to|per)\b", clause):
                continue
            if JOINING_WORD.match(clause):
                # "..., which is about four cups of instant coffee" is the second half of a
                # sentence: said on its own it read as "Which is about four cups of instant
                # coffee." - a relative clause with no subject in it, handed over as the answer
                # to "how much coffee is too much". The sentence the clause was cut from holds
                # the figure and the thing both, so that is the part that answers.
                clause = sentence.strip().rstrip(",;: ")
                if len(clause.split()) > 40:
                    continue  # a long sentence is not a narrowing of a long answer
            elif clause[0].islower():
                clause = clause[0].upper() + clause[1:]
            part = clause + ("" if clause.endswith((".", "!", "?")) else ".")
            if _flat(part) == flat_reply:
                return None  # the whole answer, which would be the same answer twice
            return part
    return None


# A head that counts the causes instead of naming one, and a head that only says a cause exists:
# both are labels for the half after the colon. "One heavy thing is the usual cause: a duvet or a
# bath mat balls up on one side" is one sentence in the washing-machine card, and cut at its colon
# it answered "why does it do that" with "One heavy thing is the usual cause." - a label with the
# cause, which was in the half that was dropped, gone.
COUNTS_THE_CAUSES = re.compile(
    r"^\s*(?:(?:it|that|this|there)\s+(?:is|are|s)\s+)?"
    r"(?:(?:usually|often|mostly|nearly always|probably)\s+)?"
    r"(?:one|ones|a few|a couple|several|a number|a combination|a mix|many|most|some|two|three|"
    r"a lot|a range|nothing|everything)\b", re.I)


# The words a head uses to say that a cause exists, or to count one, without naming it. What is
# left when these are taken out is the subject: "Overwatering is the usual cause" keeps
# overwatering, "the usual cause" keeps nothing and names nothing.
NAMES_NO_CAUSE = frozenset("""cause causes reason reasons usual usually common commonest main
mostly often likely probably real whole only most thing things something anything everything
one ones part parts bit couple few number several combination mix lot lots many some""".split())


def _names_no_cause(head):
    """True for the head of a colon sentence that labels a cause without naming one."""
    head = str(head or "")
    if COUNTS_THE_CAUSES.match(head):
        return True
    return not (set(keywords(head)) - NAMES_NO_CAUSE)


def _cause_part(part):
    """The side of a colon sentence that gives the reason, or the whole sentence when neither
    side names a cause. A colon can open a list of causes, a step, or the advice that follows
    the reason, so the side is chosen by what it says, not by its position."""
    part = str(part or "").strip()
    if ":" not in part:
        return part
    head, tail = part.split(":", 1)
    for candidate in (head, tail):
        if candidate is head and _names_no_cause(head):
            # A head that only points at the cause is not the cause: the sentence is kept whole,
            # because the half after the colon is where the reason actually is.
            continue
        if CAUSE.search(candidate):
            candidate = candidate.strip().rstrip(",;")
            if candidate and candidate[0].islower():
                candidate = candidate[0].upper() + candidate[1:]
            return candidate + ("" if candidate.endswith((".", "!", "?")) else ".")
    return part


def _reason_again(reason, last):
    """The same reason said another way when it was just given.

    A cause answer says its subject and then the reason ("A sore knee is usually a strain...").
    Asked again, the reason on its own reads better than the whole answer, and the short form
    ("Usually a strain...") is not the same line again. The two forms alternate.
    """
    reason = str(reason or "").strip()
    match = re.match(r"^(.*?)\b(?:is|are|was|were)\s+(usually|commonly|often)\s+(.+)$",
                     reason, re.IGNORECASE)
    if match:
        short = "{} {}".format(match.group(2).capitalize(), match.group(3))
        if _flat(short) != _flat(reason):
            if _flat(reason) == _flat(last):
                return short
            if _flat(short) == _flat(last):
                return reason
    if _flat(reason) == _flat(last) and re.search(r",\s*so\b", reason, re.I):
        short = re.split(r",\s*so\b", reason, 1, flags=re.I)[0].strip().rstrip(",;")
        short += "" if short.endswith((".", "!", "?")) else "."
        if _flat(short) != _flat(reason):
            return short
    return reason


# A line asking for a measure, and a sentence that carries one. Used to keep the entry that
# answers a price or a time, instead of handing the turn to an entry that says how to fit it.
ASKS_A_MEASURE = re.compile(
    r"\b(?:how\s+(?:much|many|long|often|far|big|old)|when|what\s+time|price|cost|cheapest)\b",
    re.I)


A_MEASURE = re.compile(r"[\d\u00a3$\u20ac]|\b(?:one|two|three|four|five|six|seven|eight|nine|"
                       r"ten|twenty|thirty|forty|fifty|hundred|thousand)\b", re.I)


# A "when" that puts a condition on the time rather than asking for a span: "its sore when i sit
# down", "it clicks when i climb the stairs". The sentence of the last answer that carries a
# figure can then be its warning - "or if it is still there after eight weeks" - and handing that
# back on its own gives somebody who described a twinge the red flag instead of the advice it came
# with.
# A figure that only says how long *before* something to arrive or act is a lead time, not the
# length or the amount the line asked for: with the airport card in hand, "how long is the flight"
# was answered "45 to 60 minutes", which is when the bag drop shuts, and the flight itself is an
# hour and a quarter. The line has to be asking for a span for this to apply - "how long before i
# need to be there" is the lead time, and the same sentence answers it.
A_LEAD_TIME = re.compile(
    r"\d[\d.,]*\s*(?:to\s*\d[\d.,]*\s*)?(?:minutes?|mins?|hours?|hrs?)\s+"
    r"(?:before|ahead of)\b", re.I)


ASKS_A_SPAN = re.compile(r"\bhow\s+(?:long|many\s+(?:minutes|hours|days|weeks))\b", re.I)


WHEN_IS_A_CONDITION = re.compile(
    r"\bwhen\s+(?!'s|s\b|\?|should\b|shall\b|do\b|does\b|did\b|will\b|would\b|can\b|could\b|"
    r"is\b|are\b|was\b|were\b|am\b|must\b|to\b)\w+", re.I)


# A sentence that only sends the person to somebody else. It is part of an answer, not an answer
# on its own: the figure it carries is when to go, not the length or the amount that was asked for.
A_WARNING = re.compile(
    r"\b(?:see|speak to|talk to|ring|call|contact|visit|go to)\s+"
    r"(?:a|an|your|the|nhs|111|999)?\s*"
    r"(?:gp|doctor|dentist|midwife|health visitor|pharmacist|a&e|ae|casualty|hospital|"
    r"111|999|out of hours)\b"
    r"|\bget (?:it|them|that) (?:checked|looked at|seen)\b"
    r"|\b(?:urgent|urgently|straight away|same day|a&e|casualty)\b", re.I)


def _asked_figure(text, reply, other_reply):
    """The sentence of `reply` that carries the figure this line asks for, or "".

    Only when the entry just read has one and the other entry does not: "how much is a new one"
    is the price they have already been told, and a fitting note is not the answer to it.

    A conditional "when" asks for no figure at all: "it aches when i walk" does not want the
    warning at the end of the last answer, it wants the advice that answer opened with, and the
    warning is where the only number in it tends to sit. Skipping a sentence that only sends
    them to a doctor leaves the rest of the answer to say its piece.
    """
    if not ASKS_A_MEASURE.search(str(text or "")):
        return ""
    condition = bool(WHEN_IS_A_CONDITION.search(str(text or "")))
    if A_MEASURE.search(str(other_reply or "")):
        return ""
    for sentence in SENTENCE.split(str(reply or "").strip()):
        if not A_MEASURE.search(sentence):
            continue
        if condition and A_WARNING.search(sentence):
            continue
        return sentence.strip()
    return ""


def _the_figure(text, reply):
    """The sentence of `reply` carrying the figure this line asks for, or ""."""
    return _asked_figure(text, reply, "")


def _sentence_with(reply, part):
    """The sentence of `reply` that `part` was cut from.

    A sentence here is one a person would read as one, so a quotation is never split: the words
    an answer hands over to say carry full stops of their own, and the sentence holding them ends
    where the quote does (`same_again.quoted.sentences`)."""
    wanted = _flat(part)
    for sentence in same_again.quoted.sentences(reply, SENTENCE):
        if wanted and wanted in _flat(sentence):
            return sentence.strip()
    return ""


def _part_not_repeated(part, whole, memory):
    """The part of an answer that answers this line, said another way if it was just said.

    The same follow-up twice ("what temperature for roast potatoes", "what pressure should it
    be?") gets the same figure twice, and a reply that repeats its own last words reads as
    broken. The sentence the figure was cut from says it with its context, and the answer it
    came from says it whole: either is the same answer without the same words.
    """
    if not isinstance(part, str) or not part.strip():
        return None
    if _flat(part) != _flat(mem.last_bot(memory) or ""):
        return part.strip()
    whole = whole if isinstance(whole, str) and whole.strip() else part
    if _flat(whole) == _flat(mem.last_bot(memory) or ""):
        # The whole of it is what is already on the screen, so handing it back is the repeat this
        # guards against: no part of this answer is new to the conversation.
        return None
    sentence = _sentence_with(whole, part)
    if sentence and _flat(sentence) != _flat(part):
        return sentence
    if _flat(whole) != _flat(part):
        return whole.strip()
    return None


# A property that the line names itself, rather than the general shape of the ask. "How long will
# it take?" only asks for the total; "how long should I rest it?" names resting, and if the answer
# just given never mentions resting, another entry's time is not an answer to this line.
GENERIC_ASK = frozenset("""
long time times minute minutes hour hours day days take takes will start finish
cook cooking bake baking roast roasting boil boiling fry frying grill grilling
""".split())


# Words about *when* a job is done, not about what the job is: "how long should i cook it for
# next time" names no thing of its own, so it is a question about the answer just given however
# little of its wording it shares with it.
# "in", "into", "on" and "at" say where a thing is, not what it is: "how long do they go in
# for?" names no thing of its own.
WHERE_WORDS = frozenset("""
go goes going went gone put puts putting get gets getting set sets use uses using
in into on at for to of with it them they that this there here
""".split())


NOT_NEW = frozenset("""
next again tonight today tomorrow yesterday now soon later still just once twice another other
bit lot lots week weeks month months year years time times future onwards onward
""".split())


def _names_a_property(text):
    """True when the line names a property of its own, not just a length or a price."""
    return bool(set(keywords(text)) & (PROPERTY_WORDS - GENERIC_ASK))


# A short ask that names no thing of its own: "what should i see", "what should i do", "where
# should i eat". The words are an ask and a verb, and what it is about is only in the chat.
BARE_ASK = re.compile(r"^\s*(?:so\s+|and\s+|ok\s+|okay\s+)?"
                      r"(?:what|which|where|who|when|how)\b[^?]{0,40}"
                      r"\b(?:see|do|eat|visit|book|buy|pack|take|wear|cook|make|get|try|"
                      r"recommend|suggest|start)\b\s*[?.!]*\s*$", re.IGNORECASE)


def _with_bare_subject(text, memory):
    """A bare ask with the thing it is about on the end: "what should i see" -> "what should
    i see rome". The words the entry matches on are in the subject, so the ask carries it."""
    if not BARE_ASK.match(text):
        return text
    subject = mem.subject(memory)
    if not subject or TIME_WORD.match(subject.strip()):
        return text  # a month or a weekend is not a thing the person named
    wanted = [word.strip(".,!?;:").lower() for word in subject.split()]
    if any(word in text.lower() for word in wanted):
        return text
    return text.rstrip("?.! ") + " " + subject


def _the_things_to_try(understood, memory):
    """The things a "that" in the line could mean, newest first.

    The subject is not always the newest thing: "we are going to rome" then "we are going to
    lisbon" leaves the subject on Rome, and answering the second trip with the first trip's
    figure is a wrong answer where a hedge is not. So the thing the last turn named is tried
    first, then the thing the store resolved the pronoun to, then the subject. Each candidate
    still has to reach an entry that is about it, so a word that is nobody's subject ("going")
    finds nothing and the next one is tried.
    """
    things = []
    leans = understood.get("leans_on") if isinstance(understood, dict) else None
    if isinstance(leans, dict):
        for word in leans.get("words") or []:
            if isinstance(word, str) and len(word.strip()) > 2:
                things.append(word.strip().lower())
    ref = understood.get("ref") if isinstance(understood, dict) else None
    if isinstance(ref, dict):
        for word in ("that", "it", "this"):
            value = ref.get(word)
            if isinstance(value, str) and value.strip():
                things.append(value.strip())
                break
    if mem.subject(memory):
        things.append(mem.subject(memory))
    seen, out = set(), []
    for thing in things:
        if thing and thing not in seen:
            seen.add(thing)
            out.append(thing)
    return out


def _with_the_thing(text, thing):
    """The line with its "that"/"it" written out as the thing: "...that cost" -> "...the rome
    cost". The line itself when it has no such word."""
    words = str(text).split()
    said = [word.strip(".,!?;:").lower() for word in words]
    if not thing:
        return text
    for i, word in enumerate(said):
        if word in REFERRING:
            words[i] = "the " + thing
            return " ".join(words)
    return text


def _care_holds(text, memory):
    """True when the composer is already holding this line inside a safety thread.

    A follow-up in a first-aid chat ("should i put butter on it" after a burn) is the composer's
    turn: it has the careful continuation, and the knowledge base would have to widen the line
    with the conversation's subject to reach an entry at all ("...on the oven"), which answers a
    question nobody asked. One door, so the wording and the judgement of what still counts as the
    same thread stay in bot/compose/.
    """
    try:
        from ..compose import fallback as composer
        return bool(composer.careful(text, memory))
    except Exception:  # noqa: BLE001 - a composer that cannot answer only adds no guard
        return False


def _named_by(item, subject):
    """True when the subject names the entry, not just brushes one of its words.

    The subject put on the end of a follow-up is a gist, and a gist holds words that belong to
    other things: "keep getting security code" shares "security" with the airport scanner entry,
    which is not what the conversation is about. So the entry has to match a phrase of the
    subject, or at least two of its words.
    """
    keys = _key_words(item)
    low = " " + subject.lower() + " "
    phrases = set()
    for part in getattr(item, "key", ()) or ():
        options = (part,) if isinstance(part, str) else part
        for option in options:
            option = str(option).lower().strip()
            if " " in option and option in low:
                phrases.add(option)
    if phrases:
        return True
    # A single short key word is enough: the second key group of an entry is the ask
    # ("nervous", "what to", "bring"), and those words say how the line is put, not what it is
    # about. Two subjects words have to be there, and both of them from the subject side of the
    # entry, or "what can we do before the first day" reaches the first day at a new job.
    subject_keys = set()
    for part in (getattr(item, "key", ()) or ())[:1]:
        options = (part,) if isinstance(part, str) else part
        for option in options:
            for word in str(option).lower().split():
                subject_keys.add(word.rstrip("s") or word)
    if len(low.split()) == 1:
        # A subject of one word ("cat") can never reach the two-word rule below, and it is the
        # whole thing the chat is about: "im thinking of getting a cat" then "what about
        # holidays". One word from the entry's first key group is the most it can offer, so that
        # is the test, and the entry still has to be about the thing as well.
        return bool(subject_keys)
    found = 0
    for word in low.split():
        word = word.strip(".,!?;:").rstrip("s")
        if len(word) > 2 and word in subject_keys:
            found += 1
    return found >= 2


def _the_answer_was_about_the_subject(memory):
    """True when the thing the chat is on is also what the last answer was about.

    "and what about holidays" adds a dimension to the thing on screen, so the thing is read with
    it - but only while the answer just given was about that thing. The chat on a dog went on to
    "im going to italy in may", which the Italy entry answered, and the next line ("what about
    money") was hung on the dog and got the price of a puppy. A stored subject can lag a topic
    change by a turn; the answer that was just given does not.
    """
    subject = str(mem.subject(memory) or "").lower()
    if not subject:
        return False
    last = memory.get("entry_answer")
    keys = getattr(last, "get", lambda *_: None)("keys") if isinstance(last, dict) else None
    if not keys:
        return True
    words = {word.strip(".,!?;:").rstrip("s") for word in subject.split()}
    return bool(words & {str(key).lower().rstrip("s") for key in keys})


# A line that adds a dimension to the thing on screen instead of naming a new subject:
# "and what about holidays", "how about at night", "what if it rains". The thing said last is
# still what it is about, so the subject may be put on the end of it.
ADDING_TO_THE_SUBJECT = re.compile(
    r"^\s*(?:and\s+)?(?:what|how)\s+about\b|^\s*(?:and\s+)?what\s+if\b|"
    r"^\s*and\s+(?:for|at|on|with|in)\b", re.IGNORECASE)


# A measure of the thing in hand is not a new subject: "what about a bowl" after the protein in
# porridge is the same protein question about a bowl, and read as a new subject it reached the
# cereal-portion card instead of the figure. The earlier question's shape answers a measure;
# an actual new subject ("what about holidays") still goes the new way.
A_MEASURE_OF_THE_SUBJECT = re.compile(
    r"^\s*(?:and\s+)?(?:what|how)\s+about\s+(?:a|an|one|two|three|four|\d+)?\s*"
    r"(?:bowl(?:ful)?|cup(?:ful)?|plate(?:ful)?|mug(?:ful)?|glass(?:ful)?|servings?|portions?|"
    r"slices?|pieces?|handfuls?|spoons?|spoonfuls?|tablespoons?|teaspoons?)\b", re.IGNORECASE)


# Words that carry no subject, so a line that is only these says nothing about itself.
GENERIC = {"should", "would", "could", "how", "what", "when", "where", "which", "about", "tomorrow",
           "today", "tonight", "them", "they", "have", "need", "want", "much", "many", "does",
           "did", "will", "this", "that", "there", "then", "with", "your", "mine", "some",
           "thing", "things", "please", "thanks", "maybe", "really", "also", "just", "like"}


# "1 hour 40 minutes" is one figure, not an hour plus forty minutes: it is read as 100 minutes
# before the spans are taken, so two answers can be compared figure for figure.
_HOURS_AND_MINUTES = re.compile(
    r"\b(\d+)\s*(?:hours?|hrs?)\s*(\d+)\s*(?:minutes?|mins?)", re.I)


def _minutes_in(text):
    """Every length of time a piece of text states, in minutes, as (low, high) pairs."""
    if not isinstance(text, str) or not text:
        return []
    stated = _HOURS_AND_MINUTES.sub(
        lambda m: "%d minutes" % (int(m.group(1)) * 60 + int(m.group(2))), text)
    found = []
    for match in re.finditer(
            r"\b(\d+)(?:\s*(?:to|-|\u2013)\s*(\d+))?\s*(minutes?|mins?|hours?|hrs?)\b",
            stated, re.I):
        unit = 60 if match.group(3).lower().startswith(("h",)) else 1
        low = int(match.group(1)) * unit
        high = int(match.group(2) or match.group(1)) * unit
        found.append((low, high))
    return found


def _a_figure_apart(mine, theirs):
    """True when two answers give lengths of time that cannot both be about the same thing.

    "40 minutes" and "1 hour 40 minutes" are two answers to "how long does this take", and a
    bird cannot be both. Two answers are apart when one states a span the other's spans leave
    out: a rate and a total ("20 minutes per 500g plus 20 minutes, so a 2kg bird takes about 1
    hour 40") is apart from a short figure that is neither of them.
    """
    mine_spans = _minutes_in(mine)
    their_spans = _minutes_in(theirs)
    if not mine_spans or not their_spans:
        return False
    return any(high_other < low or high < low_other
               for low, high in mine_spans for low_other, high_other in their_spans)


def _only_a_figure(part):
    """True when the part is a sum of money and nothing else ("£800 to £1,200.")."""
    if not isinstance(part, str) or not part.strip():
        return False
    words = words_of(part)
    return bool(re.search(r"[\u00a3$\u20ac]|\bpounds?\b|\bquid\b", part)) and len(words) <= 6


FIGURE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _figures(text):
    """The numbers a line states, comma or not: "£400,000" and "400000" are one figure."""
    return {one.replace(",", "") for one in FIGURE.findall(str(text or ""))}


# The words the knowledge base keys *few* entries on: the things it knows about, as opposed to
# the words that say how a line is put ("spend", "afford", "fix") and the common words that end
# up in a key because they are part of some entry's name ("put", "one", "before", "never").
# Built once.
_NAME_WORDS = None


_NAME_DOMAINS = {}


FEW_ENTRIES = 12


# A time word says when, not what: "how long until he is house trained" names the puppy, not
# "until". `trained` and `frozen` are a state of the thing in hand, not another thing, so neither
# may stand in as the thing the line names.
WHEN_NOT_A_THING = frozenset("""
until till since while during before after within ago
""".split())


def _name_words():
    """The words that name a thing: keyed on by a handful of entries, not by the whole base.

    Asking every word any entry is keyed on is too wide to be useful - "ive never done one
    before" is four such words, and a guard that refuses a follow-up for any of them turns
    ordinary chats into a punt ("how do i give a talk at work" then "ive never done one
    before" lost its answer). A thing the base knows has a name, and a name keys a few entries:
    "fluent" keys one, "pension" five, "presentation" nine. "put" keys 74 entries and "one" 99,
    so neither is a name.
    """
    global _NAME_WORDS
    if _NAME_WORDS is None:
        counted = {}
        domains = {}
        try:
            for one in all_entries():
                field = getattr(one, "domain", None)
                for word in _key_words(one):
                    counted[word] = counted.get(word, 0) + 1
                    if field:
                        domains.setdefault(word, set()).add(field)
        except Exception:  # noqa: BLE001 - the guard is an extra, it must not stop a turn
            counted = {}
            domains = {}
        _NAME_WORDS = {word for word, seen in counted.items() if seen <= FEW_ENTRIES}
        _NAME_DOMAINS.clear()
        _NAME_DOMAINS.update({word: domains.get(word, set()) for word in _NAME_WORDS})
    return _NAME_WORDS


def _filler(word):
    """A word that says how a line is put, not what it is about: "until", "theyre", "should"."""
    if word in GENERIC or word in mem.topics.STOPWORDS or word in NOT_NEW:
        return True
    if word in PROPERTY_WORDS or word in WHEN_NOT_A_THING:
        return True
    for tail in ("re", "ve", "ll", "d", "m"):
        if word.endswith(tail) and word[:-len(tail)] in mem.topics.STOPWORDS:
            return True
    return False


def _left_out(item, text):
    """True when the line names a thing this entry never mentions.

    A follow-up is written out with the subject on the end and the entry is read from that
    rewrite, so nothing looked at the words the person actually typed: "how long until i'm
    fluent" after "i practice on the bus" became "how long until i'm fluent for the practice
    bus?" and the coach price (bus, how long) answered it. "fluent" is a word the knowledge base
    keys an entry on - the language one - and the coach entry never says it, so the widening put
    the wrong thing back. A name the base knows, that this entry does not say, is that case; the
    words that only say how a line is put, and the common words that ride along in a key, are not
    names and never block.
    """
    keys = _key_words(item)
    names = _name_words()
    for word in re.findall(r"[a-z']+", str(text or "").lower()):
        word = word.rstrip("'")
        if len(word) < 4 or _filler(word):
            continue
        bare = word.rstrip("s") or word
        if bare in keys or word in keys:
            continue
        if bare in names or word in names:
            # A name the entry's own field answers for is an aspect of the thing in hand, not
            # another thing: "house trained" after a puppy is a pets question, and a pets entry
            # is keyed on "trained", so the puppy's answer stands. "fluent" is a study word and
            # the coach entry is travel, so that one is the wrong thing being put back.
            field = getattr(item, "domain", None)
            if not any(field in _NAME_DOMAINS.get(form, ()) for form in (word, bare)):
                return True
    return False


# A line that asks how to say something to someone is about the person and the moment, not
# about the topic: "how do i raise it without sounding like i'm keeping score" after a friend
# who keeps cancelling plans is not a question about cancelling, and reading the referring word
# as the topic ("how do i raise the cancelling plans ...") handed it the how-to-cancel wording,
# which is the message the other person would send. The referring word in these shapes is what
# is said or who hears it, so the topic is not put back in for them.
#
# "how do i tell if the egg is off" is a diagnosis and not this shape, so the tell-words carry
# a guard for what follows them.
#
# The verb needs its object, the same way the fallback's wording pattern does, and the verbs are
# only the ones that mean saying something: raise, broach, word, phrase, put. "Approach" and
# "tackle" are left out on purpose - "my bike is squeaking" then "how do i approach it" is a fix
# question about the bike, and blocking the bike for it lost the chain answer. A bare "how do i
# approach my boss about a pay rise" is left to the entry that owns it.
#
# A machine "sounding like" something is the commonest way people say it is making a noise, and
# that is not a tone ask either: the tone is named by "without sounding like" and "not sounding
# like", never by the bare words.
SAY_IT = re.compile(
    r"\bhow (?:do|should|can|could|would) i (?:raise|broach|word|phrase|put)"
    r"\s+(?:it|this|that|the subject|the issue)\b"
    r"|\bhow (?:do|should|can|could|would) i (?:say|tell)\b(?!\s+(?:if|whether|the difference"
    r"|when|what))"
    r"|\bbring (?:it|this|that) up\b|\bbroach (?:it|this|that)\b"
    r"|\bwithout sounding\b|\bnot sounding\b|\bnot wanting to sound\b"
    r"|\bwithout (?:being|coming across|upsetting|offending|hurting)\b"
    r"|\bwhat (?:should|do) i say to\b",
    re.IGNORECASE)


# The words of an ask rather than of a thing: how/do/want, the articles and pronouns, laughter,
# periods of time, and the little words people hang a question on.
_ASKING_ONLY = frozenset("""how much many long far often soon old big large small hot cold warm
fast slow quick heavy light high deep thick thin wide tall low early late few more less most least
time times cost costs price worth take takes last lasts
do does did can could would should shall will may might must need needs want wants
get gets got make makes made use uses using put
i me my we our you your a an the it its that this they them there
and or but for of to in on at with from about than then too also just really very
good nice best better worse right wrong new
one ones thing things kind type sort way part bit
lol lmao haha hahaha hmm hm mmm ah oh yeah yep ok okay
today tomorrow tonight week weekend month year day night morning evening
away around back down up out over any some all
""".split())


# What makes a word in a line a thing the line is about, rather than a word that happens to be
# in it: a determiner in front of it. "is it worth getting a smart meter" says "a smart meter",
# and "how long until he is house trained" says no house at all - the house there is the front of
# "trained". One describing word is allowed in between, so "a bigger oven" and "the new boiler"
# count as named.
# The subject of a line does not need a determiner in front of it when the word is the first
# thing the line says: "is brie safe when pregnant" names brie as plainly as "is a brie safe".
# Without this the line answered in one conversation and punted in the next, because after any
# other turn the talk's subject is read against the entry and a bare name was not a name: after
# "is risotto safe to eat when pregnant" the same brie question got the search hedge, and after
# "my back hurts" it was answered. A line that opens with a word the entry is about *is* about
# it. Only one or two auxiliaries are allowed in front of it, which keeps a question that opens
# with an ask ("how long until he is house trained" names no house) out of this.
OPENS_WITH_AN_AUXILIARY = frozenset(
    "is are was were can could should do does did will would".split())


NAMING = re.compile(
    r"\b(?:a|an|the|another|my|our|your|his|her|their|this|that|these|those|one|two|three)\s+"
    # The thing named is any of the next three words, not only the last one the pattern could
    # reach: "can a gerbil have a carrot" was read as naming "a", so the gerbil's own food card
    # stood down as the answer to a talk about a horse's apples and the soup recipe took the
    # carrot. Each word in the window is tested against the entry's own subjects below.
    # A thing named at the end of the line has nothing after it to reach: "what can i do for a
    # cold" said "a cold" and the pattern wanted a word after it, so the entry that answers a
    # cold was not "named" by a line that names nothing else, and after a chat about cold rice
    # the whole turn was a shrug. The last word counts on its own.
    r"((?:[a-z-]+[\s,]+){1,3}|[a-z-]+)")


# The words a line can carry without naming anything of its own: the hand-over's courtesy and
# its pronouns. "please quiz me then" is the same ask as "quiz me".
HANDOVER_FILLER = frozenset("""
a an the some any another one more then now again please pls just
so ok okay and but also even really
""".split())


# What a person is choosing between when a taste narrows the choice: a film night, a book, a
# meal, a game. A taste about one of these is a request, because the answer is another thing of
# the same kind; a taste about a cat or a neighbour is a fact about them and nobody is choosing.
CHOICE_KINDS = frozenset("""film films movie movies series show shows programme programmes
    book books novel novels game games music song songs album albums meal meals dinner food
    recipe recipes takeaway takeaway""".split())


# A follow-up leaves its subject out, and that is what makes the rewrite safe: the thing on screen
# is put back where the "it" was. A line that names a thing of its own is not that line. "is a
# burnt toast bad for a dog" and then "is it worth getting a heat pump" became "is the burnt toast
# bad worth getting a heat pump", and the toast card answered a question about a heat pump.
#
# The word that marks the thing is the determiner in front of it: "getting a heat pump" names one,
# "fixing my old laptop" names one, and "is it worth fixing", "how long should i prove it" and
# "and if i get a new one, what should i look for" name none - they say only what to do with the
# thing already on screen, which is exactly what the rewrite is for. So a word after "a", "my" or
# "the" is a thing unless it is one of the words that only describes or counts one ("a new one",
# "the best one", "a bit").
# "its" is left out on purpose: in a chat line it is nearly always "it is" ("its 8 years old"),
# so nothing after it names a thing.
THING_AFTER = frozenset("""a an the my your our their his her this that these those another
    any some every each""".split())


# A determiner behind one of these is where the subject goes, not a thing of its own: "can i take
# it in the pool" is a question about the phone and the pool is the water it might go in, so the
# swimming kit is not the answer and the phone's own card is. "for" and "about" are left out on
# purpose: "a lot for a new one" and "what about the potatoes" both name the thing asked about.
AFTER_A_PLACE = frozenset("""in on at into inside onto unto under underneath near by through
    across behind beside below above outside around round aboard throughout within past
    toward towards via along off upon""".split())


# Words that name no thing even with a determiner in front of them: the ask itself ("no idea
# where to hold it"), a quality ("is that dangerous"), a quantity ("is 300 quid a lot"), and the
# person asking ("what do i wear as a man in his 50s"). A determiner in front of one of these says
# nothing about a new thing in the talk, so the last subject is still what the line means. Without
# the person words, the line named "a man" as its own thing, `_in_context` stepped aside, and the
# outfit question lost the occasion from the line before.
NO_THING_NAMED = frozenset("""idea ideas point points sense question questions matter deal
    problem problems chance chances clue guess guesses example examples option options choice
    choices answer answers lot lots bit bits time times while moment minute second hour day days
    week weeks month months year years difference change reason reasons dangerous risky noisy
    pricey dodgy faulty broken safe spare fortune mint bomb packet ton
    man men woman women person people guy guys lady ladies bloke child kid adult teenager""".split())


# The little verbs a determiner can sit in front of: "any ideas that wont cost a fortune", "the
# one that will last". What follows one of these is not a thing the line names.
_AUXILIARY = frozenset("""wont cant doesnt dont didnt isnt wasnt arent shouldnt wouldnt couldnt
    mustnt will would can could should may might must shall do does did have has had be been
    being is are was were am""".split())


# A line that asks how much or how many is asking about the thing already in the talk, whatever
# it says: "my boiler needs replacing" then "is 300 quid a lot for a new one" is the price of
# that boiler, and "a new one" is not a thing of its own.
ASKS_A_QUANTITY = re.compile(r"\bhow (?:much|many)\b|\bhow (?:long|far|often)\b", re.I)


DESCRIBES_ONE = frozenset("""new old another different same other else more less much many few
    lot lots best better worse easiest hardest first second last next right wrong kind sort type
    way ways thing things stuff one ones bit bits worth safe ok okay normal bad legal possible
    fine allowed hard easy too still someone something anything everything nothing everyone
    everybody nobody anybody""".split())


KEEPS = re.compile(r"\b(?:keep|keeps|keeping|fridge|freezer|freeze|lasts?)\b", re.I)


# A figure is what "how long does that keep" asks for: a number with a unit of time on it.
FIGURE = re.compile(r"\b(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|a couple of|a few)"
                    r"(?:\.\d+)?\s*(?:-|to\s+\d+\s*)?(?:hour|hours|day|days|week|weeks|month|"
                    r"months|year|years)\b", re.I)
