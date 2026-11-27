"""Part 7 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""
import re
import unicodedata

from . import lexicon
from .normalize_part_01 import (
    ASK_WORDS, WANT_WORDS, RAW_WORD, _a_core_verb_typed_wrong,
)
from .normalize_part_02 import (
    DIGIT_WORDS, DROPPED_SUBJECT_AUX, REPEAT_ONCE, REPEAT_ONCE_SUBJECTS, _a_game_named_another_way,
    _parts_that_hurt, spelled,
)
from .normalize_part_03 import (
    BE_FORMS, HAVE_FORMS, MODAL_FORMS, PLURAL_SUBJECTS, THIRD_PERSON, KIN, PUNCT_BREAK,
    SENTENCE_END, THOUSANDS, THOUSANDS_SAID_WITH_A_SPACE, TOKEN, _a_contraction_typed_with_a_space,
    _a_sign_is_a_word, _a_slip_that_is_a_word, _joined_words, _one_word_food, _phrase_pass,
    a_son_not_the_sun, loose_is_lose, possessive_me, subject_missing,
)
from .normalize_part_04 import (
    _a_name_slot, _token,
)
from .normalize_part_05 import (
    _a_hello_said_short, _chat_words_said_out, _glued_said_apart, _join_chat_digits, _lookahead,
    _said_apart, _said_apart_as_one_word, _the_mrs_is_the_wife, _typed_without_spaces, _glued_words,
)
from .normalize_part_06 import (
    strip_leaders, LEADERS, _a_leading_like_is_a_filler, _a_meal_word_misspelt,
    _an_exclamation_in_front, _an_exclamation_is_not_a_thing, _an_ill_that_is_i_will, _asking,
    _clauses, _docs_doctor, _one_relation_says, _only_leaders_before, _positional_word,
    _repair_openers, _says_has, _split_ask, a_sor_bit_is_sore,
)


def _focus(clauses):
    """The clause that carries the ask: the last one that opens like a question, else the
    last one that asks for something, else the last one with something in it."""
    for clause in reversed(clauses):
        stripped = strip_leaders(clause)
        if stripped and stripped[0] in ASK_WORDS:
            return clause
    for clause in reversed(clauses):
        if any(token in WANT_WORDS for token in clause):
            return clause
    for clause in reversed(clauses):
        stripped = strip_leaders(clause)
        if stripped:
            return clause
    return clauses[-1] if clauses else []


# Letters that carry no accent mark to strip: people type them in words they know and they
# would otherwise cut the word in two ("smorrebrod", "aeble", "plain l").
LETTERS = str.maketrans({
    "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "ø": "o", "Ø": "O", "ł": "l", "Ł": "L",
    "đ": "d", "Đ": "D", "ð": "d", "Ð": "D", "þ": "th", "Þ": "TH", "ß": "ss", "ı": "i",
})


def _unaccent(text):
    """The same line with every accent mark taken off ("crème" -> "creme").

    A keyboard often cannot type the accent, and one that arrives by copy or by a foreign
    keyboard used to cut the word in two at the accent ("creme fraiche" typed with accents
    read as "cr me fra che"), so the word matched nothing and the line read as a shrug.
    NFKD splits a letter from its accent and the combining marks are dropped, for every
    script, not just the words we happen to know.
    """
    split = unicodedata.normalize("NFKD", text.translate(LETTERS))
    return "".join(char for char in split if not unicodedata.combining(char))


# "what on earth is happening" is a person asking about their own day, not a question about the
# planet: the phrase between the question word and the rest is an intensifier, and the word
# "earth" in it is not a thing the line is about. Read as a noun it was enough for the entry on
# the layers of the Earth to answer "what on earth" and "wtf" (which expands to "what on
# earth") with "a thin rocky crust, a hot slow-flowing mantle ...". The same goes for "how the
# hell do i unblock this" and "why in the world would i". Only the intensifier right after the
# question word is dropped, so "life on earth", "the biggest thing on earth" and "what on earth
# is the earth made of" keep every word they are about.
_INTENSIFIER = (r"on\s+earth|in\s+the\s+world|"
                r"the\s+(?:hell|heck|devil|blazes|dickens|fuck)")


WH_INTENSIFIER = re.compile(r"^\s*(?:" + _INTENSIFIER + r")\s*$")


WH_INTENSIFIER_LINE = re.compile(
    r"(?<![a-z'])\b(what|why|when|where|who|which|whose|how)\s+(?:" + _INTENSIFIER + r")\b",
    re.I)


WH_ANY = frozenset("what why when where who which whose how".split())


def intensifier_positions(norm):
    """Where the "on earth" / "the hell" in the line sits, as indices into `norm`.

    The noun in the phrase is not a thing the line is about, so the reading gives its place to
    the caller that keeps the words nothing answers on (`background`). Only the phrase right
    after a question word counts, so "life on earth" and "the biggest thing on earth" keep
    theirs.
    """
    positions = set()
    for index, word in enumerate(norm):
        if word not in WH_ANY:
            continue
        for size in (3, 2):
            phrase = norm[index + 1:index + 1 + size]
            if len(phrase) == size and WH_INTENSIFIER.match(" ".join(phrase)):
                positions.update(range(index + 1, index + 1 + size))
                break
    return positions


# The words of the surprise as the person typed them: "on", "earth" from "what on earth". The
# surprise is taken out of `clean` before the reading is built, so asking the reading where it
# was can only ever find the half that `clean` does not touch ("the hell", never "on earth").
_TYPED_SURPRISE = re.compile(
    r"(?<![a-z'])\b(?:what|why|when|where|who|which|whose|how|whatever|however|whoever|whenever)"
    r"\s+(?:" + _INTENSIFIER + r")", re.I)


def _the_surprise_typed(text):
    """The words of the surprise after a question word, as the line was typed.

    "what on earth is happening" and "what on earth's going on" both hand over "on" and "earth",
    with the clipped is taken off: the reading no longer holds the phrase, and a caller that
    wants to know which surprise the line used has nothing else to ask.
    """
    flat = re.sub(r"[^a-z']+", " ", text.lower().replace("\u2019", "'"))
    # "wtf" is the same surprise with the letters taken out, and the lexicon reads it as
    # "what", so the words are spelled out here before the phrase is looked for.
    flat = re.sub(r"\b(?:wtf|wth|wtaf)\b", "what on earth", flat)
    words = []
    for match in _TYPED_SURPRISE.finditer(flat):
        for word in match.group(0).split()[1:]:
            word = word[:-2] if word.endswith("'s") else word
            if word not in words:
                words.append(word)
    return words


def _without_the_intensifier(norm):
    """The reading with "on earth" / "the hell" taken out from after a question word.

    The words are not what the line is about, so every reader that matches English words gets
    the line without them: "what on earth is happening" is a question about the person's day,
    not about the planet.
    """
    out = []
    index = 0
    while index < len(norm):
        word = norm[index]
        if word in WH_ANY and index + 1 < len(norm):
            phrases = intensifier_positions(norm)
            if index + 1 in phrases:
                end = index + 1
                while end < len(norm) and end in phrases:
                    end += 1
                out.append(word)
                index = end
                continue
        out.append(word)
        index += 1
    return out


# The long word a clip doubles into, and what the line has to be about for that to be the
# meaning: "mon" is a mistyped moon in a line about the night sky, and a clipped mum anywhere
# else. "mon is coming over" and "mon and dad" are people; "the mon is bright tonight" is not.
_A_CLIP = {
    "mon": ("moon", frozenset("""moon moons full half crescent phase waxing waning eclipse
        lunar sky night tonight bright light lit shines shine rises rising stars""".split())),
}


def _a_clip_kept_only_with_its_cue(plain, norm, fixes, line):
    """The reading with a clip's repair taken back when the line names nothing it is about.

    The vowel class repairs "mon" to "moon" wherever it stands, and a line about a parent loses
    its subject to it. The repair is kept when any word of the line is a cue for the long word,
    and taken back - out of the plain line, the reading and the list of repairs - when none is.
    """
    bent = dict(fixes)
    for typed, (longer, cues) in _A_CLIP.items():
        if bent.get(typed) != longer or any(word in cues for word in line):
            continue
        fixes = [pair for pair in fixes if pair[0] != typed]
        plain = [typed if word == longer else word for word in plain]
        norm = [typed if word == longer else word for word in norm]
    return plain, norm, fixes


def _fix_auxiliaries(tokens):
    """A "bin" read as "been" gets the helper English needs: "he is been" is "he has been",
    "she been in hospital" is "she has been in hospital". Nothing else is touched: a "been"
    with a helper already ("has been", "have been") is left exactly as it is."""
    if "been" not in tokens:
        return tokens
    out = []
    for index, word in enumerate(tokens):
        if word == "been" and out:
            last = out[-1]
            if last in BE_FORMS:                      # "he is been" was a contraction of has
                out[-1] = "have" if (len(out) > 1 and out[-2] in PLURAL_SUBJECTS) else "has"
            elif last in PLURAL_SUBJECTS or last in THIRD_PERSON:
                # "how have you been" already has its helper, and a question puts the subject
                # between the two: nothing to add.
                before_it = out[-2] if len(out) > 1 else None
                if before_it not in HAVE_FORMS and before_it not in BE_FORMS \
                        and before_it not in MODAL_FORMS and before_it != "not":
                    out.append("have" if last in PLURAL_SUBJECTS else "has")
        out.append(word)
    return out


# The words people put after the thing they meant: a kiss, a "please", a laugh. None of them
# says what the line is about, and left in the line they cost the answer - "what can i put on a
# burn x", "can you help me please", "what time is it lol" all came back as the search hedge
# while the same line without the tag was answered, because every reader matches the words it
# expects and one extra word at the end is enough to miss. A line of nothing but tags keeps them
# ("x", "please", "lol" on their own), and a laugh only goes when the line already asks
# something, so "that was funny lol" is still a laugh.
TAG_WORDS = frozenset("""x xx xxx xo xxo xoxo mwah kisses""".split())


# A "please" is part of how the line is said, and the reading keeps it ("yes please" is not "yes",
# "table for 4 please" keeps its please): it only goes off a line that already asks something,
# where it is the tag on the end of the ask, not the whole of it.
TAG_PLEASE = frozenset("please pls plz pls.".split())


# The same tag said as thanks. It goes only off a line that already asks something and has
# three words of its own in front of it, so "i want to say thanks" keeps the word that is the
# whole point of the line while "can you help me thanks" is still the ask for help.
TAG_THANKS = frozenset("thanks thank cheers thx ty ta".split())


TAG_QUESTION_LEADS = frozenset("""what why how when where who which whose can could should
    would will is are do does did have has am was were may might shall""".split())


TAG_GUARD_BEFORE = frozenset("""a an the this that my your his her their our for of is are was
    were be been being with than to from called named call name letter mark spot sign cross tick
    size sized equals equal and or but not no""".split())


# A line can open by saying it is about something else: "changing subject, how do i stop my bin
# smelling", "different topic: my boiler is leaking". The announcement is about the conversation,
# not about the thing being asked, and read as words it is about something: "subject" is a school
# word, so the bin was answered with the university entry requirements and "change of subject, my
# boiler is leaking" was a school line. It comes off only when the person set it off as its own
# clause (a comma, colon or dash after it) and the line goes on to say something - "changing
# subject at a-level, is it too late" keeps it, because that subject is the thing being asked
# about, and "changing subject" on its own is the whole line.
CHANGE_OF_SUBJECT = re.compile(
    # up to two of the words people start a turn with, with or without their comma: "and changing
    # subject, ...", "so anyway, change of topic, ...", "now, on a different tack, ...".
    r"^(?:(?:and|so|but|oh|ok|okay|right|now|anyway|anyways|also|plus|well)\s*,?\s*){0,3}"
    r"(?:"
    # "changing subject", "change of topic", "changing the tack"
    r"(?:changing|change\s+of|changing\s+the)\s+(?:the\s+)?(?:subject|topic|tack)"
    # "moving on to a different subject", "on to a different topic", "onto another tack"
    r"|(?:moving\s+on\s+to|on\s+to|onto|on|to)\s+(?:a\s+)?(?:new|different|another)\s+"
    r"(?:subject|topic|tack)"
    # "moving on to something else" says the same thing without naming a subject
    r"|(?:moving\s+on\s+to|on\s+to|onto)\s+something\s+else"
    # a bare "moving on" - nobody means the walking when they put a comma after it
    r"|moving\s+on"
    # "new topic", "different subject", "another tack"
    r"|(?:a\s+)?(?:new|different|another)\s+(?:subject|topic|tack)"
    r")"
    r"\s*[,;:.\u2013\u2014-]+\s*(?=\S)")


def _change_of_subject_off(clean):
    """The line without the clause that only announces a change of subject, and whether it went."""
    seen = CHANGE_OF_SUBJECT.match(clean)
    if not seen:
        return clean, False
    rest = clean[seen.end():]
    if len(RAW_WORD.findall(rest)) < 2:
        return clean, False       # nothing after the announcement but a word or two: keep both
    return rest, True


def _without_a_tag_at_the_end(clean):
    """`clean` without the tags at its end, and the tags that came off."""
    words = str(clean or "").split()
    asks = bool(words and words[0].strip(".,!?") in TAG_QUESTION_LEADS) or "?" in clean
    dropped = []
    while len(words) > 1 and words[-1].strip(".,!?") in TAG_WORDS:
        if words[-2].strip(".,!?") in TAG_GUARD_BEFORE:
            break
        dropped.insert(0, words.pop())
    while len(words) > 1 and words[-1].strip(".,!?") in TAG_PLEASE and asks:
        dropped.insert(0, words.pop())
    while len(words) > 1 and words[-1].strip(".,!?") in lexicon.LAUGHTER and asks:
        dropped.insert(0, words.pop())
    while len(words) > 3 and words[-1].strip(".,!?") in TAG_THANKS and asks:
        dropped.insert(0, words.pop())
    return " ".join(words), dropped


# A line that asks how a word is spelt is about the spelling of it, not about the thing it names.
SPELLING_ASK = frozenset("spell spells spelling spelt spelled misspelt misspelled pronounce".split())


# The endings that make one spelling another form of the same word. A line that puts two of
# them either side of "or" is asking which spelling is right, whether or not the pair is a
# repair: "is it definately or definite" offers "definite" against the slip, and "definite" is a
# word of its own, so only the shape of the two words can tell that the line is about spelling.
SPELLING_ENDINGS = ("ly", "ness", "ing", "ed", "es", "s", "d", "e")


def _spellings_of_one_word(one, other):
    """True when these two words are spellings or forms of the same word."""
    if not one or not other:
        return False
    if one == other:
        return True
    short, longer = (one, other) if len(one) <= len(other) else (other, one)
    if len(short) < 4 or not longer.startswith(short):
        return False
    return longer[len(short):] in SPELLING_ENDINGS


# A spelling question that names letters rather than spellings: "is it definately with an a or
# an e", "is it definately with one f or two", "is neccessary one c or two", "definately with a
# double f". These are the same question as "is it definately or definitely" asked the way
# people ask it, and none of them carries a word of SPELLING_ASK, so the repair took the answer
# away: "is neccessary one c or two" was told "Two. I'd take that and not think about it again."
# A letter stands for itself only next to a count ("with one f", "one c or two") or "double",
# which is the shape that separates it from "with a cold" and "a size m".
NAMED_LETTER = re.compile(
    r"\b(?:with\s+(?:an?|one|two|three|double)\s+[a-z](?![a-z])"
    r"|(?:one|two|three|a\s+double)\s+[a-z](?![a-z])\s+or\s+(?:one|two|three|an?)\b"
    r"|double\s+[a-z](?![a-z])\b"
    r"|[a-z](?<![a-z])\s+or\s+(?:two|three)\b)")


def _names_a_letter_beside_a_slip(words, fixed):
    """True when the line names a letter a few words from a slip it repaired."""
    if not fixed:
        return False
    for at, word in enumerate(words):
        if word not in fixed:
            continue
        near = " ".join(words[max(0, at - 4):at + 5])
        if NAMED_LETTER.search(near):
            return True
    return False


# The words that come before and after a short chat form when it is being named as a letter
# rather than said as a word: "the letter u is silent", "u turn", "what u's are there", "a u-boat".
_A_SHORT_WORD_IS_NAMED_BEFORE = frozenset((
    "letter", "letters", "word", "words", "vowel", "consonant", "initial", "alphabet", "grade",
    "grade", "type", "blood", "vitamin", "plan", "shape", "u", "the",
))


_A_SHORT_WORD_IS_NAMED_AFTER = frozenset((
    "turn", "turns", "turn-", "boat", "boats", "bend", "shaped", "shape", "tube", "value", "values",
))


def _a_short_word_named(short, before, after):
    """True when a short chat form is being named, not said: "a u turn", "the letter u".

    "u" is both the chat form of "you" and a letter with its own words around it, and the two
    are told apart by what stands beside it: "do a u turn", "the letter u is silent", "a u-boat",
    "what u's do i need for the exam". Everything else is the word: "how r u", "what are u
    reading", "how do i write a thank u letter".
    """
    if before in _A_SHORT_WORD_IS_NAMED_BEFORE or after in _A_SHORT_WORD_IS_NAMED_AFTER:
        return True
    return after is not None and after.endswith("'s") and short == "u"


def _asks_the_spelling(words, fixed):
    """True when the typed spelling is what the line is asking about, so it is not put right.

    Two shapes carry it, and both name the slip as the subject:

    - the question is about spelling at all: "how do you spell recieve", "how do i spell
      embarased". The spelling answers are reached from the word as it was typed, so a repaired
      word is a word they can no longer see.
    - the line offers two spellings of one word: "is it definately or definitely", "which is
      right, seperate or separate". Only a repair with the other spelling beside it counts, so
      "im tiered or just bored" is still read as tired.
    """
    if not fixed:
        return False
    if any(word in SPELLING_ASK for word in words):
        return True
    if _names_a_letter_beside_a_slip(words, fixed):
        return True
    for at, word in enumerate(words):
        if word != "or":
            continue
        before = words[at - 1] if at else ""
        after = words[at + 1] if at + 1 < len(words) else ""
        if before in fixed and after in (fixed[before], before):
            return True
        if after in fixed and before in (fixed[after], after):
            return True
        # ... or the two words are forms of one word, so "is it definately or definite" is the
        # same question as "is it definately or definitely" and keeps the slip it asks about.
        if before in fixed and _spellings_of_one_word(fixed[before], after):
            return True
        if after in fixed and _spellings_of_one_word(fixed[after], before):
            return True
    return False


# A clause that gives the owner of the day and leaves the day itself out. "its not my birthday its
# my mums" names the day once and then says whose it is, and the second clause has nothing in front
# of a day word, so every reader that looks for a relation before the day finds none and the line
# reads as the person's own day: "Happy birthday when it comes" to somebody who has just said it is
# their mum's. The day word is put back where the person left it out, and the relation is then read
# by the readers that already work - the same line with "my mums birthday" in it is greeted right.
DAY_NAMED = re.compile(r"\b(birthday|anniversary|wedding)s?\b", re.I)


OWNER_WITHOUT_THE_DAY = re.compile(
    r"\b(?:it|its|it's|that|thats|that's)(?:\s+is)?\s+(?:not\s+)?(?:my|our)\s+([a-z]+'?s)\b",
    re.I)


# What may follow the owner and still leave the day out: the end of the clause, or when it is. A
# word that the owner owns ("its my mums fault") is the day, and is left alone.
TAIL_OF_A_DAY = frozenset("""
    tomorrow today tonight soon next this on in at already too as well then
""".split())


# "can not" is the same word as "cant": the apostrophe is off and the words are apart, and the
# reading kept them apart, so a card keyed on "cant sleep" ("i cannot sleep" reaches it) missed
# the way most people type it - "i can not sleep" fell through to a pool about bad nights. The
# knowledge entries write both spellings, so the one-word form is the one nothing loses.
CAN_NOT = re.compile(r"\bcan\s+not\b")


def _can_not_as_one_word(clean):
    """The line with a "can not" typed as two words written as the one word "cant"."""
    return CAN_NOT.sub("cant", clean)


def _the_day_left_out(text):
    """The same line with the day's name put back in the clause that only names its owner."""
    named = DAY_NAMED.search(text)
    if not named:
        return text
    day = named.group(1).lower()
    pieces = []
    last = 0
    for found in OWNER_WITHOUT_THE_DAY.finditer(text):
        if found.start() < named.end():
            continue
        tail = re.split(r"[,.;:!?]", text[found.end():], 1)[0].split()
        if any(word.lower() not in TAIL_OF_A_DAY for word in tail):
            continue
        pieces.append(text[last:found.end()])
        pieces.append(" " + day)
        last = found.end()
    if not pieces:
        return text
    pieces.append(text[last:])
    return "".join(pieces)


# The same day read the other way round: the clause that says whose day it is comes first and the
# one that says it is not the speaker's comes last. "its my sons 5th not my birthday" and "our nans
# 80th is saturday not my birthday" both got "Happy birthday when it comes" - the greeting for the
# speaker - because the day word stands in the negated clause at the end and the number that says
# whose it is is only a number. The day belongs to the person named before it, so the name goes
# back onto their number and the clause that denies it is the speaker's comes off.
A_NUMBER_OF_SOMEONES_DAY = re.compile(
    r"\b(?:my|our)\s+([a-z]+\'?s?)\s+(\d+(?:st|nd|rd|th))\b", re.I)


NOT_MY_OWN_DAY = re.compile(
    r"\s*(?:,?\s*\b(?:and\s+)?not\s+(?:my|mine)\s+"
    r"(birthday|bday|anniversary|wedding)\b)", re.I)


def _a_day_named_as_not_mine(text):
    """The same line with the day moved onto the person the clause before it named."""
    negated = NOT_MY_OWN_DAY.search(text)
    if not negated:
        return text
    day = negated.group(1).lower()
    owner = None
    for found in A_NUMBER_OF_SOMEONES_DAY.finditer(text[:negated.start()]):
        if found.group(1).lower().rstrip("s") in KIN:
            owner = found
    if owner is None:
        return text
    # Only the clause that denies the day is taken off: what follows it still says when the day
    # is ("its my daughters 3rd not my birthday on saturday" keeps the saturday).
    whole = text[:owner.end()] + " " + day + text[owner.end():negated.start()] + text[negated.end():]
    return " ".join(whole.split())


# "is it ok to eat rice thats been in the fridge 3 days" is one question: the thing has already
# been kept, and how long it has been kept is the whole point. The words that say so are the place
# it sat in and the time it sat there, and neither of them is the subject - the food is. Rows that
# answer what to cook with what is left ("leftover rice" is the fried-rice recipe), what a warm pot
# may do ("rice" and "in the fridge" is the cooling row) or what the date on a bag is worth
# ("rice" and "ok to eat" is the dry-rice row) each read one of those words as their own, so each
# was answering a keeping question. The pair is read once here and a row can stand down on it.
_KEEPING_PLACES = frozenset((
    "fridge", "fridgefreezer", "refrigerator", "freezer", "cupboard", "larder", "pantry",
    "worktop", "counter", "countertop", "out", "outside", "coolbox", "coolbag", "bag"))


# A thing that has already been kept somewhere, named without the place: "can i eat leftover rice
# after 3 days" is the same question as the fridge line, and says "leftover" instead of "fridge".
_KEPT_THINGS = frozenset((
    "leftover", "leftovers", "cooked", "uneaten", "spare", "rest", "remains", "opened"))


_DAY_WORDS = frozenset((
    "day", "days", "night", "nights", "week", "weeks", "month", "months"))


_KEPT_ALREADY = frozenset(("overnight", "yesterday", "since"))


_SMALL_NUMBERS = frozenset((
    "a", "an", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "couple", "few", "several", "many", "half"))


_NUMBER_SHAPE = re.compile(r"^\d{1,3}(?:st|nd|rd|th)?$")


def _a_number(word):
    """True for "3", "2nd", "two", "a few" - the number in front of the day words."""
    return bool(_NUMBER_SHAPE.match(word)) or word in _SMALL_NUMBERS


def _kept_for(flat):
    """{"place", "time"} when the line says a thing has already been kept, else None.

    The place is the word the thing sat in ("fridge", "cupboard", "out") or None when the line
    names only the thing that was kept ("leftover rice after 3 days"). The time is the phrase
    that says how long ("3 days", "overnight", "since monday"). A line with a time and no place
    and no kept thing is not this reading: "i start my new job in 3 days" is a date.
    """
    if not flat:
        return None
    time = None
    at = None
    for index, word in enumerate(flat):
        if index + 1 < len(flat) and _a_number(word) and flat[index + 1] in _DAY_WORDS:
            time, at = "%s %s" % (word, flat[index + 1]), index
            break
        if word in _KEPT_ALREADY:
            after = flat[index + 1] if index + 1 < len(flat) else ""
            time = (word + " " + after).strip() if word == "since" and after else word
            at = index
            break
    if time is None:
        return None
    place = None
    for index, word in enumerate(flat):
        if word in _KEEPING_PLACES:
            # "a bag of rice in the cupboard for 3 months" is the bag's date, and the bag is the
            # thing the line is about rather than where it was kept, so it is not this reading.
            place = word
            break
    if place is not None:
        if abs(at - index) <= 10:
            return {"place": place, "time": time}
        return None
    if _KEPT_THINGS.intersection(flat):
        return {"place": None, "time": time}
    return None


def _only_doubles_a_letter(typed, mended):
    """True when the repair puts back a copy of a letter the person typed once.

    People do type one of a doubled letter ("recomend", "hapened") and the corrector puts it
    back, but the same guess is how a word becomes a different word: "mons" was read as "moons",
    "thres" as "threes" and "moning" as "mooning". A vowel put back where the line has three
    consonants in a row ("wndow", "kittn", "brdge") is a shape no English word has, so that
    repair is one the reader can be sure of; a doubled letter is a letter the person may never
    have meant, so it is left to `plain` and the word the readers match on stays as it was typed
    unless a misspelling list vouches for it.
    """
    if len(mended) != len(typed) + 1:
        return False
    return any(mended[at] == mended[at + 1] and mended[:at] + mended[at + 1:] == typed
               for at in range(len(mended) - 1))


def normalise(text):
    """{"text", "clean", "words", "plain", "norm", "norm_text", "fixes", "clauses", "focus",
    "asking", "signals"} for one line.

    "plain" is the line as it was typed with each word repaired in place - the same order, the
    same punctuation, no clause splitting - so a reader that matches on words gets the spelling
    the writer meant without losing anything else. "norm" is the fuller reading: clauses split,
    chat-speak and contractions expanded, digits read out.
    """
    text = text if isinstance(text, str) else ""
    # "isit ok to eat this" is "is it ok to eat this": a glued question opener is put right in
    # the line as typed, before the words are read, so `clean` and `words` carry the two words
    # the readers match on rather than one word no English line has. A capital is a name's, so a
    # token with an upper-case letter is never split ("Didi" is a person, not "did i").
    clean = _glued_said_apart(" ".join(_unaccent(text).split()))
    clean = _typed_without_spaces(clean)
    # "i d k" and "o m g": somebody typing with one hand puts a space between every letter, and
    # nothing read those runs, so `i d k` became "i'd k" from the two pieces "i d" and reached no
    # card at all. It goes in here, before the short spellings are repaired, because "i d" is
    # repaired into "i'd" further down and the pieces are gone by then.
    clean = _said_apart_as_one_word(clean)
    clean = _the_mrs_is_the_wife(clean)
    clean = " ".join(clean.lower().split())
    # A "can not" typed as two words is the one word "cant": the cards are keyed on the short
    # spelling ("the things that work" for sleep) and every entry writes both, so the line that
    # splits it missed all of them. It goes in before the chat-speak is spelled out, so a word
    # that stands for "can not be bothered" keeps the two words the phrase readers match on.
    clean = _can_not_as_one_word(clean)
    clean = _the_day_left_out(clean)   # "its my mums" is "its my mums birthday"
    clean = _a_day_named_as_not_mine(clean)   # "my sons 5th not my birthday" is his, not mine
    clean = THOUSANDS.sub(r"\1", clean)   # "1,500" is a number, not two numbers
    clean = THOUSANDS_SAID_WITH_A_SPACE.sub(   # "1 500" is one number too
        lambda m: m.group(1) + m.group(2).replace(" ", "").replace("\u00a0", ""), clean)
    clean = _one_word_food(clean)          # "chick peas" is the one word the kitchen knows
    clean = _a_leading_like_is_a_filler(clean)
    clean = _joined_words(clean)           # "fedup" is the two words the fed-up reader knows
    clean = _a_contraction_typed_with_a_space(clean)   # "she s 84" is "shes 84"
    clean = _an_exclamation_in_front(clean)         # "god i hate mondays" is "i hate mondays"
    clean = _an_exclamation_is_not_a_thing(clean)   # "what on earth" is "what"
    clean = _a_hello_said_short(clean)     # "gm" is "good morning", "mornin" is "morning"
    clean = _chat_words_said_out(clean)    # "wanna" is "want to" for the words a reader matches
    clean = _an_ill_that_is_i_will(clean)  # "ill go with the train" is "i will", not an illness
    clean, tags_at_the_end = _without_a_tag_at_the_end(clean)
    clean, change_of_subject = _change_of_subject_off(clean)
    # A price typed with a sign is a price, and the sign is not a word: "i have £20 until friday"
    # was read as "i have 20 until friday", so no row that matches on a money word saw the money,
    # while the same line typed as "i have 20 pound until friday" was answered about it. The
    # figure keeps the word people say in `words`, `plain` and `norm`, and `clean` stays the line
    # as it was typed, because the readers that want the sign itself ("£250 is how much a month")
    # find it there.
    clean, words = _a_meal_word_misspelt(clean, RAW_WORD.findall(clean))
    clean, words = _docs_doctor(clean, words)
    said = _a_sign_is_a_word(clean)
    words = RAW_WORD.findall(said)
    fixes = []
    norm = []
    plain = []
    fixed = {}
    subject_put_back = False
    sentence_ends = SENTENCE_END.sub(" | ", _phrase_pass(said))
    tokens = TOKEN.findall(PUNCT_BREAK.sub(" | ", sentence_ends))
    joined = _one_relation_says(
        a_son_not_the_sun(a_sor_bit_is_sore(
            loose_is_lose(possessive_me(_said_apart(_join_chat_digits(tokens)))))))
    joined, slips = _a_slip_that_is_a_word(joined)
    for typed, meant in slips.items():
        # The word meant is the word the readers get: `words` is handed to the knowledge base,
        # and `clean` keeps the line as it was typed, which is what a reply quotes.
        fixes.append((typed, meant))
        fixed[typed] = meant
    for index, word in enumerate(joined):
        before = joined[index - 1] if index else None
        after = joined[index + 1] if index + 1 < len(joined) else None

        if ((before is None or before == "|"
             or (before in LEADERS and _only_leaders_before(joined, index)))
                and word in DROPPED_SUBJECT_AUX
                and subject_missing([word] + _lookahead(joined, index), 0)):
            # "am off to bed" -> "i am off to bed". The typed word stays as it was in `plain`:
            # nothing was misspelt, the subject was left off.
            norm.extend(["i"] + _token(word, fixes, before))
            plain.append(word)
            subject_put_back = True
            continue
        after_after = joined[index + 2] if index + 2 < len(joined) else None
        before_before = joined[index - 2] if index >= 2 else None
        if _a_name_slot(before, before_before, word):
            # A name goes in as it was typed, and the plain line with it, so an echo says the
            # name back the way it was given.
            norm.append(word)
            plain.append(word)
            continue
        before_words = joined[max(0, index - 5):index]
        after_words = joined[index + 1:index + 4]
        verb = _a_core_verb_typed_wrong(word, before, after)
        if verb:
            # A verb typed with a letter out of place is the verb they typed, and the readers get
            # it: a repair is only handed on in `words` when it is recorded here, and the line as
            # typed stays the line a reply quotes.
            fixes.append((word, verb))
            fixed[word] = verb
        for spelled in ([verb] if verb else
                        _positional_word(word, before, after, after_after, before_before,
                                         before_words)):
            parts = _token(spelled, fixes, before, before_before, after,
                           before_words=before_words, after_words=after_words)
            # "i dunno" carries its own "i", and "the the" is a slip: a word a line never says
            # twice is dropped, and "very very tired" keeps both because people mean it.
            if parts and norm and parts[0] == norm[-1] and parts[0] in REPEAT_ONCE:
                parts = parts[1:]
            elif (len(parts) > 1 and norm and parts[0] == "i"
                  and parts[1] == "do" and norm[-1] in REPEAT_ONCE_SUBJECTS):
                parts = parts[1:]        # "u dunno" is "you do not know", not "you i do not know"
            if not parts:
                continue
            norm.extend(parts)
            # A repair goes into the plain line; an expansion ("don't" -> "do not", "2" -> "two")
            # does not, so the line reads as it was typed apart from the words that were wrong.
            # An American spelling is not a slip, so `plain` keeps the spelling they used.
            if len(parts) > 1 and spelled in lexicon.PLAIN_EXPANDS:
                # A chat word that is not a word at all, whose repair is two words the readers
                # match on: the plain line carries it too, or a reader that looks for the phrase
                # never sees it.
                plain.append(" ".join(parts))
            elif (len(parts) == 1 and spelled not in DIGIT_WORDS
                    and spelled not in lexicon.US_SPELLINGS):
                plain.append(parts[0])
                # Only a word the tables put right is the word the readers are given. The
                # corrector guesses at the rest - it reads "blink" as "blank" - and a guess is
                # not good enough to hand the knowledge base in place of what was typed.
                if parts[0] != spelled and (spelled in lexicon.MISSPELLINGS
                                            or spelled in lexicon.URGENT_MISSPELLINGS
                                            or (spelled in lexicon.SAID_SHORT
                                                and not _a_short_word_named(spelled,
                                                                           before, after))):
                    fixed[spelled] = parts[0]
                elif spelled != word and word in lexicon.STATES_WITHOUT_G:
                    # The g this pass put back is a repair, and the word the knowledge base is
                    # handed carries it: "how long can i go without eating, im starvin".
                    fixed[word] = spelled
                elif word == "bin" and parts[0] == "been":
                    # A "bin" the frame made into "been" is the word the knowledge base is handed,
                    # for the same reason as a spelling put right: the rows key on words, and one
                    # keyed on "bin" answers a line about a sick cat with a pet that has been in
                    # the washing machine ("cats bin sick twice 2day" got "towel him dry right
                    # through"). The noun keeps its word: "the bin needs emptying", "my dog fell
                    # in the bin" and "bin day" never get here, because the frame in front of the
                    # word is the whole of the test above.
                    fixed[word] = parts[0]
            else:
                # A chat-spelled contraction is a spelling slip, not an expansion: the plain line
                # gets "couldnt" for "cudnt", which is the spelling the modules match on. Only
                # the reading keeps the words apart ("could not").
                plain.append(lexicon.TYPED_CONTRACTIONS.get(spelled, spelled))
    norm = _fix_auxiliaries(_says_has(norm))
    # "on earth" and "the hell" are kept out of the reading and named in `intensifier`, because
    # a knowledge entry keyed on "earth" answered "what on earth is happening" with the layers
    # of the planet. They are still in `text` and `clean`, so nothing is lost from the line.
    intensifier = _the_surprise_typed(text)
    # What the line still holds is a different question: "on earth" is taken out of `clean`
    # before the reading is built, so a lookup that drops the surprise from its words must only
    # drop the half the line still has ("the hell"), or "what on earth is the earth made of"
    # loses the planet and gets a shrug.
    intensifier_left = [norm[index] for index in sorted(intensifier_positions(norm))]
    if not intensifier:
        intensifier = list(intensifier_left)
    if intensifier_left:
        norm = _without_the_intensifier(norm)
    # A misspelt part of the body is settled once, here, so the topic rule, the part the composer
    # keeps a pool of lines for, and every module that matches on words all read the same part.
    norm, words = _a_game_named_another_way(norm, words)
    norm = _parts_that_hurt(norm, fixes)
    if any(word in lexicon.PAIN_WORDS for word in norm):
        # The plain line carries the repairs the reading made, or a reader matching on words
        # never meets the part: only the words already settled above are put back.
        mended = dict(fixes)
        plain = [mended.get(word, word) for word in plain]
    # A three-letter word that is also the clip of an everyday one ("mon" for mum) is bent into
    # the longer word by the vowel class: "mon and dad" was read as "moon and dad", and a
    # clipped mum is far commoner than a mistyped moon. The moon is worth reading where the line
    # is about it, and only the line can say so, so the repair is kept only when a cue for the
    # long word stands somewhere in it.
    plain, norm, fixes = _a_clip_kept_only_with_its_cue(plain, norm, fixes, joined)
    clauses = _split_ask(_repair_openers(_clauses(norm), fixes))
    flat = [word for clause in clauses for word in clause]
    focus = _focus(clauses)
    asking = _asking(clauses, focus)
    signals = {
        "question_mark": "?" in text,
        "shout": sum(1 for w in text.split() if len(w) > 2 and w.isupper()) > 0,
        "laughter": any(lexicon.is_a_laugh(w) for w in norm + tags_at_the_end)
                    or bool(re.search(r"\b(?:ha\s*){2,}|\b(?:heh\s*){2,}", text)),
        "ellipsis": "..." in text or ".." in text,
        "exclamation": "!" in text,
        "empty": not words,
    }
    # The one line where a slip must stay a slip is the line that asks about the spelling itself:
    # "is it definately or definitely" and "how do you spell recieve" name the typed spelling as
    # the thing they want an answer about, and the spelling answers are reached from that
    # spelling. Handing the readers the repaired word instead took six such questions away.
    keep = _asks_the_spelling(words, fixed)
    # Every repair this pass made, whichever part of it made it: the token pass and the part of
    # the body settle their repairs in `fixes`, and `fixed` held only the ones a misspelling list
    # knew. A reader matching on `words` met the slip and not the word it meant ("my wndow wont
    # shut" reached the cupboard catch on "shut", never the window), so the repairs are collected
    # here once rather than in the one dict a single pass fills.
    settled = dict(fixed)
    for typed, mended_word in fixes:
        if typed != mended_word and " " not in mended_word \
                and (typed in fixed or not _only_doubles_a_letter(typed, mended_word)):
            settled.setdefault(typed, mended_word)
    return {
        "text": text,
        "clean": clean,
        # The words a line is read by are the words it meant: a spelling this pass put right is
        # the word the reader gets ("how do i cook qinuoa properly" is about quinoa). `clean`
        # keeps the line as it was typed, which is what a reply quoting the person reads.
        "words": list(words) if keep else [settled.get(word, word) for word in words],
        "plain": re.sub(r"\s*\|", ",", " ".join(plain)).strip(" ,"),
        "norm": flat,
        "norm_text": " | ".join(" ".join(clause) for clause in clauses) if clauses else "",
        "fixes": dict(fixes),
        "intensifier": intensifier,
        "intensifier_left": intensifier_left,
        "clauses": clauses,
        "focus": focus,
        # The ask as it was said, measure word and all: see `_asking`.
        "asking": asking,
        "signals": signals,
        "dropped_subject": subject_put_back,
        "change_of_subject": change_of_subject,
        "kept": _kept_for(flat),
    }


# "Sick with worry" is a figure of speech, and the only illness in it is the word "sick".
# Read as a symptom it earns "rest, warm drinks and an early night" for a person who is
# frightened about an exam, and "keep them home with drinks in small sips" for a child who is
# worried about school - advice for a bug nobody has. The feeling after "with" is what the word
# is doing, so the phrase is read as the feeling it stands for and the line goes on to the pool
# that answers feelings: "worried about my exam", "nervous", "guilty". A bug named in the same
# line ("sick with a bug going round", "sick with the flu") is not a feeling and keeps its illness.
# The word carrying the symptom is not always "sick": "im nauseous with worry", "shaking with
# nerves" and "ill with guilt" are the same figure of speech, and read as the body they begin
# with they earn the stomach-bug answer for a person who is frightened.
SICK_AS_FEELING = re.compile(
    r"\b(?:sick|ill|unwell|nauseous|nauseated|queasy|shaking|shaky|trembling|dizzy)"
    r"\s+(?:(?:with|from)\s+)?"
    r"(worry|worrying|worried|stress|stress(?:ed)?\s+out|fear|fright|frightened|panic\w*|"
    r"nerves|nervous|anxious|anxiety|guilt\w*|grief|shame|ashamed|dread\w*|anger|rage|"
    r"jealousy|it\s+all)\b",
    re.I)


# One feeling word back for every phrase the person used, because the pools read the adjective
# ("worried about a person" and "worried about a thing" are different pools) and not the noun.
_FEELING_WORD = {
    "worry": "worried", "worrying": "worried", "worried": "worried", "stress": "stressed",
    "stressed out": "stressed", "stressed": "stressed", "fear": "frightened",
    "fright": "frightened", "frightened": "frightened", "panic": "panicky",
    "panicking": "panicky", "panicky": "panicky", "nerve": "nervous", "nerves": "nervous",
    "nervous": "nervous", "anxious": "anxious", "anxiety": "anxious", "guilt": "guilty",
    "guilty": "guilty", "grief": "grieving", "shame": "ashamed", "ashamed": "ashamed",
    "dread": "dreading", "dreading": "dreading", "anger": "angry", "rage": "angry",
    "jealousy": "jealous", "it all": "overwhelmed",
}


# "worried sick", "scared sick", "bored sick" put the feeling in front: the word after it is
# the feeling, and "sick of" there is the same figure of speech, not an illness.
FEELING_BEFORE_SICK = re.compile(
    r"\b(?:worried|scared|frightened|terrified|bored|stressed|anxious)\s+sick\b", re.I)


def _the_feeling_word(match):
    said = " ".join(match.group(1).lower().split())
    return _FEELING_WORD.get(said, "upset")


def without_the_figure_of_speech(clean):
    """`clean` with "sick with worry" read as the feeling it stands for, for the body readers."""
    clean = FEELING_BEFORE_SICK.sub(lambda m: m.group(0).split()[0], str(clean or ""))
    return SICK_AS_FEELING.sub(_the_feeling_word, clean)


# "sugar" is two things: what goes in the tea and what the body runs on. The rest of the line says
# which, and only one of them is a health line: "my sugar was low last night" is a hypo, and it
# was read as the kitchen ("I'm listening - say more if it helps", or "cut the sugar you drink"
# for "my sugar keeps dropping at night"), while the same line with "blood" in it got the answer.
# A word of the level after "my sugar" is what says the body is meant, so that is what the whole
# engine reads, and a line that says "add", "a cup" or "brown" still means the bag in the cupboard.
SUGAR_LEVEL = frozenset("""low high dropped drop drops dropping crashed crash crashes crashing
    dipped dip dips dipped levels level reading readings rises rose rising spike spiked spiking
    fell falls falling down up""".split())


# "rose" is the one level word that is a thing as well: "my sugar rose collapsed" is the icing
# flower on a cake. It counts as a level only where it is the verb of the reading - followed by
# "to", "from", "after" and the like, or by nothing at all ("my sugar rose") - and not where a
# noun follows it.
SUGAR_AFTER_ROSE = frozenset("""to from after again overnight during before since sharply
    steadily quickly suddenly a bit so very high low all above around past 6 7 8 9""".split())


# A price or an amount of the stuff says the line is about the shopping, not about a meter: "my
# sugar went up in price", "my sugar dropped in price", "went up a pound", "down to one bag". It
# says that beside any level word, not only "up" and "down", because a price is not a reading
# whichever way it is said to have moved. And it has to sit where the level word would be followed
# by a linking word or a number, so "my sugar is up a bit", "up a lot" and "up the other day" -
# which are how people say how far the reading moved - keep it.
#
# "nothing" is deliberately not here. It is not a price: a diabetic whose sugar is "down to
# nothing" is describing the meter, and that line is a low that gets the emergency answer
# (polite-ruler, #4222). The shopping's "nothing left" is covered by the shop words around it.
SUGAR_PRICE = frozenset("""price prices cost costs pound pounds lb lbs kilo kilos bag bags packet
    packets tin tins gram grams spoon spoons teaspoon teaspoons""".split())


# Five words of tail, so "down to one bag" and "levels are down to a tin" are both in view.
# A price written in figures: "90p", "50p", "£2", "£1.50". The pence and the pound sign are what
# make it a price rather than a meter reading.
SUGAR_PRICE_SHAPE = re.compile(r"^(?:[£$€]|\d+(?:\.\d+)?p(?:ence)?$)", re.I)


# The tail takes a currency sign as well: "down to £1.50" is the price, and a tail that stopped at
# the sign read the "down" and called it a meter reading.
SUGAR_FIRST_PERSON = re.compile(
    r"\b(my|his|her|their|your)\s+sugar\b((?:\s+[a-z0-9'£$€]+){0,5})", re.I)


# A part of the body is not only said to hurt. People say how badly it is going in the words of
# a bad day instead - "my back is a joke today", "my knees are a nightmare", "my ankle is a
# mess", "my back is terrible" - and every reader that knows the part waits for a word of pain
# it never sees, so those lines fell through to "I'm sorry - that's frustrating" while "my back
# hurts" got the answer. The body readers already agree on what a word of pain is
# (`lexicon.PAIN_WORDS`) and on the parts (`lexicon.BODY_PARTS`), so the saying is read once
# here as the plain complaint it stands for, before anything reads the line.
#
# Only a part the person owns, with a be-word between it and the saying: "the back of the house
# is a mess" is the house, because "back" is followed by "of" rather than by the be-word, and a
# thing that is not a part of the body ("my sleep is a mess", "my hair is a nightmare") keeps
# the reading it has, which the knowledge base already answers.
BAD_SAYING = (r"(?:an?\s+|such\s+an?\s+|one\s+big\s+"
              r"|an?\s+(?:complete|right|total|proper|real|absolute|utter|bit\s+of\s+a|bloody)\s+)?"
              r"(?:joke|nightmare|mess|disaster|wreck|state|shambles|agony|torture|car\s+crash|"
              r"pain\s+in\s+the\s+(?:arse|bum|butt|neck|back))")


# The same thing said with one word. "sore" and "bad" are already words of pain; these are the
# rest of the ways a person says it, and none of them is ever about anything but being unwell
# when a part of the body is the subject.
BAD_WORD = (r"(?:terrible|awful|rubbish|crap|horrible|dreadful|brutal|shocking|knackered|shot|"
            r"agony|unbearable|wrecked|ruined|buggered|done\s+in)")


PART_THAT_IS_BAD = re.compile(
    r"\b(my|his|her|their|our|your)\s+("
    + "|".join(sorted(lexicon.BODY_PARTS, key=len, reverse=True))
    + r")\s+(?P<link>is|are|was|were|has\s+been|have\s+been|feels?|feels?\s+like)\s+(?:"
    + BAD_SAYING + "|" + BAD_WORD + r")\b", re.I)


# A part is said in the plural for both of its own ("my knees", "my feet"), and the verb follows
# what was typed: "my knees hurt", "my feet hurt". Two of those plurals do not end in an s.
THE_ODD_PLURALS = frozenset("feet teeth calves".split())


def _the_part_that_is_bad(match):
    part = match.group(2).lower()
    plural = part.endswith("s") or part in THE_ODD_PLURALS
    link = " ".join(str(match.group("link") or "").lower().split())
    if link in ("has been", "have been"):
        # "my back has been a nightmare for weeks" is a complaint that has gone on, and
        # "my back hurts for weeks" is not English: the tense the person used is kept, because
        # the memory keeps this line and says it back to them.
        verb = "have been hurting" if plural else "has been hurting"
        return "%s %s %s" % (match.group(1), match.group(2), verb)
    verb = "hurt" if plural else "hurts"
    return "%s %s %s" % (match.group(1), match.group(2), verb)


def _the_part_that_hurts(clean):
    """`clean` with "my back is a joke" said as "my back hurts", for the health readers."""
    return PART_THAT_IS_BAD.sub(_the_part_that_is_bad, str(clean or ""))


def _the_sugar_that_is_blood(clean):
    """`clean` with "my sugar was low" said as "my blood sugar was low", for the health readers."""
    def rewrite(match):
        tail = [word.strip(".,!?").lower() for word in match.group(2).split()]
        # A price is not a reading even when it is written in figures: "my sugar dropped to 90p",
        # "down to £1.50". Only the pence and the pound sign say so - a bare number is a meter
        # reading, which is why "my sugar is 3.9" and "dropped to 3.1" keep the blood.
        if any(SUGAR_PRICE_SHAPE.match(word) for word in tail):
            return match.group(0)
        # A number is a reading on a meter, not a spoonful: "my sugar is 3.9", "went down to 3.1".
        if any(word[:1].isdigit() for word in tail):
            return "%s blood sugar%s" % (match.group(1), match.group(2))
        near = tail[:3]
        level = [word for word in near if word in SUGAR_LEVEL]
        if level == ["rose"]:
            following = tail[tail.index("rose") + 1:]
            if following and following[0] not in SUGAR_AFTER_ROSE \
                    and not following[0][:1].isdigit():
                level = []  # "my sugar rose collapsed" is a flower, not a reading
        if level:
            for at, word in enumerate(tail):
                if word in SUGAR_LEVEL and SUGAR_PRICE & set(tail[at + 1:at + 4]):
                    return match.group(0)  # "my sugar dropped in price" is the shopping
            return "%s blood sugar%s" % (match.group(1), match.group(2))
        return match.group(0)
    return SUGAR_FIRST_PERSON.sub(rewrite, str(clean or ""))


def glued_words(token, after=None):
    """The words a glued token stands for, or None - the name a module reads.

    The reading splits these tokens for its own line, and a module that reads the line another
    way (the safety module does, in `safety._norm`) reads the same table rather than keeping one
    of its own: "whatsthe point" is the crisis line "whats the point" is, and "iwant to die" is
    "i want to die".
    """
    return _glued_words(token, after)
