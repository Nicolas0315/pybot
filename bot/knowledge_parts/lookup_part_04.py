"""Part 4 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
from .lookup_part_01 import (
    MIN_TYPO_LENGTH, PHRASE_WEIGHT, WORD_WEIGHT, said, AS_A_KIND,
)
from .lookup_part_02 import (
    _FORMS_CACHE_KEEP,
)
from .lookup_part_03 import (
    _engine_reads, _forms, _one_edit, _stem, PLURAL_ONLY_PHRASES, _WANTED_CACHE, _ARTICLE_WORDS,
    _ARTICLE_FORMS, _LINE_FORMS, _WHERE, _PHRASE_SPANS, ASK_FRAME, _SAID_BETWEEN,
    _ONE_SPELLING_EITHER_WAY, ASK_PEOPLE, _ASK_ABOUT_SOMEONE, _WANTING, WANT_FILLER, DENIERS,
    DENY_BETWEEN, DENY_SAID_OF, STATES_AFTER, A_LENGTH_WORD, A_STAND_IN, WHEN_WORDS, FRAME_PRONOUNS,
    FRAME_ENDS, _FRAME_MASK, _ASK_PHRASE_MASK, HAPPENING_AGAIN, REPORT_FILLER, REPORT_LEADS,
    REPORT_PERSON, EXPLAIN_FILLER, EXPLAIN_LEADS,
)


def _typo_forms(word, vocabulary):
    """The forms of the key word a misspelt line word is one slip away from, or nothing when
    the slip is ambiguous ("htis" could be two words, "lips" could be "lies" or "lids"), the
    word is too short to be sure, or the engine already reads the word as it is.

    Two key words of one family are one candidate, so a misspelt word still reaches an
    entry keyed on both "radiator" and "radiators"; two different families are none, so a
    slip that could be either of two meanings ("lips" for "lies" or "lids") says nothing.
    """
    if len(word) < MIN_TYPO_LENGTH or _engine_reads(word):
        return set()
    close = [other for other in vocabulary
             if other[:1] == word[:1] and abs(len(other) - len(word)) <= 1
             and _one_edit(word, other)]
    families = {_stem(other) for other in close}
    if len(families) != 1:
        return set()
    forms = set()
    for other in close:
        forms |= _forms(other)
    return forms


def _wanted(phrase):
    """The forms of each word of a key phrase, worked out once for every entry that says it."""
    got = _WANTED_CACHE.get(phrase)
    if got is None:
        if phrase.lower() in PLURAL_ONLY_PHRASES:
            got = tuple(frozenset((word,)) for word in phrase.lower().split())
        else:
            got = tuple(_forms(word) for word in phrase.lower().split())
        if len(_WANTED_CACHE) >= _FORMS_CACHE_KEEP:
            _WANTED_CACHE.clear()
        _WANTED_CACHE[phrase] = got
    return got


# A phrase only loses its article when it is long enough to still name a thing without it. "park
# at the airport" and "look after the battery" keep three words; "for a week" would fall to "for
# week", which is nearer to a phrase of some other row than to the one it came from, and a first
# try that dropped every article reordered whole families of answers - a film question reached the
# planning row, a nurse on nights reached the nursing-careers row. Three words are what a phrase
# needs to stay itself, so that is the line.
_MIN_BARE_WORDS = 3


# What such a phrase counts for. The phrase as it stands in the key is worth PHRASE_WEIGHT; the same
# phrase with its article missing is worth one less, because the person has said slightly less than
# the key says. That is what keeps the reading a tie-breaker rather than a claim: with the same
# weight, "my baby wont take bottle" reached the under-three-months row above the bottle row and
# answered a parent changing a feed with "ring 111 or your GP now". A line reaches the row it was
# about first, and only then does the article-free reading settle what is left.
BARE_WEIGHT = PHRASE_WEIGHT - 1


def _wanted_bare(phrase):
    """The forms of the phrase's words with its articles left out, or None when it has none."""
    got = _WANTED_CACHE.get(("bare", phrase), ())
    if got:
        return got[0]
    words = phrase.lower().split()
    kept = [word for word in words if word not in _ARTICLE_WORDS]
    bare = tuple(_forms(word) for word in kept) if len(kept) >= _MIN_BARE_WORDS and len(kept) < len(words) else None
    if len(_WANTED_CACHE) >= _FORMS_CACHE_KEEP:
        _WANTED_CACHE.clear()
    _WANTED_CACHE[("bare", phrase)] = (bare,)
    return bare


def _phrase_span_bare(forms, wanted, seen):
    """The span an article-free phrase covers on the line, where the line may keep its articles.

    The words of the phrase have to sit in the line in order, as they do for the phrase itself,
    and an article of the line may sit between any two of them: "how do i look after battery on my
    phone" is the same question as "how do i look after the battery on my phone". Nothing else is
    skipped, so the phrase still says what it said.
    """
    n = len(wanted)
    last = len(forms) - 1
    for start in range(len(forms)):
        if not forms[start] & wanted[0]:
            continue
        span = [start]
        here = start + 1
        for j in range(1, n):
            while here <= last and not (forms[here] & wanted[j]):
                if not forms[here] & _ARTICLE_FORMS:
                    break
                here += 1
            if here > last or not (forms[here] & wanted[j]):
                break
            span.append(here)
            here += 1
        else:
            return tuple(span)
    return ()


def _shape(phrase):
    """(the words of a key phrase, its weight), worked out once for every entry that says it.

    _part_matches reads the words and the weight of every alternative of every key part it is
    asked about, and a line asks thousands of times: a phrase is a module-level constant, so
    its shape is worked out once instead of being lower-cased and split each time.
    """
    got = _SHAPE_CACHE.get(phrase)
    if got is None:
        words = tuple(phrase.lower().split())
        got = (words, PHRASE_WEIGHT if len(words) > 1 else WORD_WEIGHT)
        if len(_SHAPE_CACHE) >= _FORMS_CACHE_KEEP:
            _SHAPE_CACHE.clear()
        _SHAPE_CACHE[phrase] = got
    return got


_SHAPE_CACHE = {}


def _line_forms(forms, seen):
    """Every form any word of the line has, worked out once for the line.

    A key phrase whose words are not all here cannot be in the line, so the answer is no before
    any of the positional work: the test is one set intersection per word, in C, and most of the
    8,900 key parts of the knowledge base are not about the line in front of them.
    """
    if seen is not None:
        got = seen.get(_LINE_FORMS)
        if got is not None and got[0] is forms:
            return got[1]
    every = set()
    for word_forms in forms:
        every |= word_forms
    every = frozenset(every)
    if seen is not None:
        seen[_LINE_FORMS] = (forms, every)
    return every


def _where(forms, seen):
    """{form: the positions in the line that have it}, worked out once for the line.

    Every entry the line reaches asks _phrase_span about its own key words, and each of those
    answers is a question about the same line, so the line is read into this map once instead of
    being walked again for every word of every key. `seen` is the line's memo (see _part_matches).
    The second map is where each form first appears: a single key word only needs the earliest
    position, and that is the question a line asks thousands of times.
    """
    if seen is not None:
        got = seen.get(_WHERE)
        if got is not None and got[0] is forms:
            return got[1], got[2]
    where = {}
    for index, word_forms in enumerate(forms):
        for form in word_forms:
            at = where.get(form)
            if at is None:
                where[form] = [index]
            else:
                at.append(index)
    firsts = {form: at[0] for form, at in where.items()}
    if seen is not None:
        seen[_WHERE] = (forms, where, firsts)
    return where, firsts


def _phrase_span(forms, phrase, seen=None):
    """The positions in the line this phrase covers, or () when it is not there.

    One position for a single word, several for a phrase, so score() can tell a line
    that mentions two different key words from one that repeats the same word twice.

    The answer is kept on the line's memo by the phrase itself. The same words are key phrases
    of many entries - "how long", "how do i", "without" - and every entry the line reaches asks
    about its own copy, so the answer was worked out thousands of times a turn.
    """
    spans = None
    if seen is not None:
        got = seen.get(_PHRASE_SPANS)
        if got is not None and got[0] is forms:
            spans = got[1]
        else:
            spans = {}
            seen[_PHRASE_SPANS] = (forms, spans)
        if phrase in spans:
            return spans[phrase]
        end = _phrase_span_work(forms, phrase, seen)
        spans[phrase] = end
        return end
    return _phrase_span_work(forms, phrase, None)


_A_BREATH = 2


_ASK_FRAME_FORMS = None


def _ask_frame_forms():
    """The forms of ASK_FRAME, worked out once."""
    global _ASK_FRAME_FORMS
    if _ASK_FRAME_FORMS is None:
        _ASK_FRAME_FORMS = frozenset().union(*(_forms(word) for word in ASK_FRAME))
    return _ASK_FRAME_FORMS


def _phrase_span_between(forms, phrase, seen=None):
    """The span of an avoid phrase where a breather may sit between its words, or ().

    Two words at most may sit between any two words of the phrase, and each of them has to be a
    breather: "my phone has just died" is the same line as "my phone died", and "the phone rang
    and the cat died" is not.

    A phrase that opens on an asking word keeps its words together. The phrase is a way of asking
    there - "how do i", "how to", "what is", "is it" - and the asking words of two different
    questions sit next to each other across a line that asks one of them for a price: "how much
    to hire a breaker" has "how" and "to" with "much" between them, and every price row that
    stands down on "how to" (the whole cost table does) then refused the line, so the commonest
    way of asking what a hire costs had no answer at all. "my phone has just died" is what the
    breathers are for, and no asking phrase needs one.
    """
    if not isinstance(phrase, str):
        return ()
    wanted = _wanted(phrase)
    if not wanted:
        return ()
    if len(wanted) == 1:
        return ()
    if wanted[0] & _ask_frame_forms():
        return ()
    key = ("between", phrase)
    spans = None
    if seen is not None:
        got = seen.get(_PHRASE_SPANS)
        if got is not None and got[0] is forms:
            spans = got[1]
        else:
            spans = {}
            seen[_PHRASE_SPANS] = (forms, spans)
        if key in spans:
            return spans[key]

    def walk(at, next_word, span):
        if next_word == len(wanted):
            return tuple(span)
        gaps = 0
        while at < len(forms) and gaps <= _A_BREATH:
            if forms[at] & wanted[next_word]:
                got = walk(at + 1, next_word + 1, span + [at])
                if got:
                    return got
            if not (forms[at] & _SAID_BETWEEN):
                return ()
            gaps += 1
            at += 1
        return ()

    answer = ()
    for start in range(len(forms)):
        if forms[start] & wanted[0]:
            answer = walk(start + 1, 1, [start])
            if answer:
                break
    if spans is not None:
        spans[key] = answer
    return answer


def _the_same_words(phrase):
    """The same phrase in the other spelling, or nothing when it has no contraction in it."""
    got = _PHRASE_OTHER_SPELLINGS.get(phrase)
    if got is None:
        got = _work_out_the_same_words(phrase)
        if len(_PHRASE_OTHER_SPELLINGS) >= _OTHER_SPELLINGS_KEEP:
            _PHRASE_OTHER_SPELLINGS.clear()   # a card of phrases, refilled on the next line
        _PHRASE_OTHER_SPELLINGS[phrase] = got
    return got


_PHRASE_OTHER_SPELLINGS = {}


_OTHER_SPELLINGS_KEEP = 4000


def _work_out_the_same_words(phrase):
    words = phrase.lower().split()
    if not words:
        return ()
    out = []
    for i, word in enumerate(words):
        for other in _ONE_SPELLING_EITHER_WAY.get(word, ()):
            if " " in other:
                out.append(" ".join(words[:i] + other.split() + words[i + 1:]))
            else:
                out.append(" ".join(words[:i] + [other] + words[i + 1:]))
    if len(words) > 1:
        for i in range(len(words) - 1):
            joined = words[i] + " " + words[i + 1]
            for other in _ONE_SPELLING_EITHER_WAY.get(joined, ()):
                if " " not in other:
                    out.append(" ".join(words[:i] + [other] + words[i + 2:]))
    return tuple(out)


def _phrase_span_work(forms, phrase, seen):
    """The phrase's span on this line, with no phrase memo in front of it."""
    end = _phrase_span_spelling(forms, phrase, seen)
    if end:
        return end
    for other in _the_same_words(phrase):
        end = _phrase_span_spelling(forms, other, seen)
        if end:
            return end
    return ()


def _phrase_span_spelling(forms, phrase, seen):
    """The span of this exact spelling of the phrase."""
    wanted = _wanted(phrase)
    if not wanted:
        return ()
    n = len(wanted)
    if seen is not None:
        line = _line_forms(forms, seen)
        for word_forms in wanted:
            if not (word_forms & line):
                return ()
    if seen is None:
        # No line memo (a test calling score() on one line): walk the line itself, which is
        # what this did before the map, rather than building the map for a single question.
        if n == 1:
            for i, word_forms in enumerate(forms):
                if word_forms & wanted[0]:
                    return (i,)
            return ()
        for i in range(len(forms) - n + 1):
            if all(forms[i + j] & wanted[j] for j in range(n)):
                return tuple(range(i, i + n))
        return ()
    where, firsts = _where(forms, seen)
    if n == 1:
        # The earliest position of any form of the key word, found by letting the line's own
        # forms and the key word's forms meet in one set operation rather than one lookup each.
        if not wanted[0].isdisjoint(firsts):
            return (min(firsts[form] for form in wanted[0] if form in firsts),)
        return ()
    hits = []
    for word_forms in wanted:
        found = set()
        for form in word_forms:
            found.update(where.get(form, ()))
        if not found:
            return ()
        hits.append(found)
    # Every word of the phrase has to be in the line, in order, so only a position where the
    # first word sits can start it. Reading those in order gives the earliest span, which is
    # what walking the whole line found, without asking the other positions anything.
    for start in sorted(i for i in hits[0] if i + n <= len(forms)):
        if all(start + j in hits[j] for j in range(1, n)):
            return tuple(range(start, start + n))
    return ()


def _phrase_found(forms, phrase):
    return bool(_phrase_span(forms, phrase))


_PART_FORMS = {}


_PART_FORMS_KEEP = 20000


def _part_forms(part):
    """Every form of every word any alternative of this part says, worked out once per part."""
    got = _PART_FORMS.get(id(part))
    if got is not None and got[0] is part:
        return got[1]
    alternatives = part if isinstance(part, tuple) else (part,)
    every = None
    for alternative in alternatives:
        if not isinstance(alternative, str) or not alternative.strip():
            continue
        for word_forms in _wanted(alternative):
            if every is None:
                every = set()
            every |= word_forms
    if every is None:
        return None if not alternatives else frozenset()
    every = frozenset(every)
    if len(_PART_FORMS) >= _PART_FORMS_KEEP:
        _PART_FORMS.clear()
    _PART_FORMS[id(part)] = (part, every)
    return every


def _part_matches(part, forms, seen=None):
    """Every matching alternative of one key part: [(weight, its words, its span), ...].

    `seen` is this line's memo, a dict from the part's id to the answer. score() asks a part
    about the line and _rank() asks the same part again, and the answer does not depend on
    anything else, so the second question is not asked. The part belongs to a module-level
    entry, so it outlives the call and its id cannot be reused inside it.
    """
    if seen is not None:
        got = seen.get(id(part))
        if got is not None:
            return got
    every = _part_forms(part)
    if every is not None and not (every & _line_forms(forms, seen)):
        # not one word of any alternative is in the line, so no alternative can match, and the
        # answer needs no reading of the line: one set intersection instead of a phrase search
        # per alternative. The line reaches 700 entries and asks about 3 parts of each, so most
        # of what a scan used to do was this test, one alternative at a time.
        if seen is not None:
            seen[id(part)] = []
        return []
    alternatives = part if isinstance(part, tuple) else (part,)
    found = []
    for alternative in alternatives:
        if not isinstance(alternative, str) or not alternative.strip():
            continue
        span = _phrase_span(forms, alternative, seen)
        bare_hit = False
        if not span:
            bare = _wanted_bare(alternative)
            if bare is not None:
                span = _phrase_span_bare(forms, bare, seen)
                bare_hit = bool(span)
        if span:
            words, weight = _shape(alternative)
            if bare_hit and weight > BARE_WEIGHT:
                weight = BARE_WEIGHT
            found.append((weight, words, span))
    found.sort(key=lambda hit: (hit[0], not _only_the_frame(hit[1])), reverse=True)
    if seen is not None:
        seen[id(part)] = found
    return found


def _part_match(part, forms, covered=(), seen=None):
    """The best matching alternative of one key part: (weight, its words, its span).

    An alternative that says something new about the line beats one that reuses a word
    already counted by another part, so ("rain", ("raining", "why")) scores on "why does
    it rain" from the "why", not from a second reading of "rain".
    """
    found = _part_matches(part, forms, seen)
    if not found:
        return (0, (), ())
    for weight, words, span in found:
        if not covered or not set(span) <= set(covered):
            return (weight, words, span)
    return found[0]


def _part_score(part, forms, seen=None):
    return _part_match(part, forms, seen=seen)[0]


def _own_words(item):
    """The single words this entry's own key already names, from its phrases as well.

    "self employed" is one key phrase, and "employed" inside it is a word the entry has
    already claimed: a row that keys it cannot then stay away from "employee" because the
    line says "self employed". `_misspelt_avoid` uses this to tell a slip from a subject.
    """
    words = set()
    for part in item.key or ():
        if isinstance(part, str):           # a part may be one phrase, not a list of them
            part = (part,)
        for key in part:
            if not isinstance(key, str):
                continue
            for word in key.strip().lower().split():
                if len(word) >= MIN_TYPO_LENGTH:
                    words.add(word)
    return words


def _misspelt_avoid(item, typed, own=None):
    """True when a line word is one slip from a word this entry stays away from.

    The forms of a repaired word already reach the avoid list, but a slip that two key
    words could explain ("brest" is "breast" or "best") is never used to read a line, and
    must still not be answered as the entry that disowns that word ("how long do i cook a
    chiken brest" is not a whole-bird question).

    A word the entry's own key names is not a slip, whatever the avoid list says: "self
    employed" is in start-a-business's key, "employee" is in its avoid, and "employed" was
    read as a slip of "employee", so "im thinking of going self employed" and "should i go
    self employed" were both refused by the one row that answers them.
    """
    if own is None:
        own = _own_words(item)
    for word in item.avoid:
        if not isinstance(word, str):       # an Entry built by hand, not through entry()
            continue
        key = word.strip().lower()
        if len(key) < MIN_TYPO_LENGTH or " " in key:
            continue
        for typed_word in typed or ():
            if typed_word in own:           # the entry's own subject, not a slip
                continue
            # a real word is never a slip of the avoid word: "does" is not "dogs", and the
            # sauce that does not need dog food still needs its seasoning answer
            if typed_word in own:
                continue
            if (len(typed_word) >= MIN_TYPO_LENGTH and not _engine_reads(typed_word)
                    and typed_word[:1] == key[:1] and _one_edit(typed_word, key)):
                return True
    return False


# A want is an ask. "i want to make a cake" and "i fancy making a curry" ask for the recipe as
# plainly as "how do i make a cake" does, and an entry that already keys the dish and the verb
# knows the line is about making one. Without this the ask guard below throws the line away, and
# the turn goes to a chat question ("Make a cake - fair enough. What's stopped it happening so
# far?") where the recipe belongs. The words are the ones that turn a thing into a request; a
# bare "i want cake" still reaches nothing, because the entry's own key needs the verb too.
WANTING = ("want to", "wants to", "wanted to", "wanting to", "would like to",
           "would love to", "feel like making", "feel like doing", "feel like baking",
           "feel like cooking", "fancy making", "fancy doing", "fancy baking",
           "fancy cooking", "fancied making", "fancied doing", "thinking of", "planning to",
           "keen to", "hoping to", "in the mood for",
           # A need is a want. "i need to sort the garage" asks for the how as plainly as "i want
           # to sort the garage" does, and without these words the line reached no entry at all:
           # nine of twenty-eight typed "i need to sort X" lines were answered by the chat module
           # with a plan to start the job ("Then start with the smallest version of it") where the
           # base has a card for it. The entry still has to key the verb and the thing, so a need
           # the base knows nothing about reaches nothing, as before.
           "need to", "needs to", "needing to", "have to", "has to", "got to", "gotta")


# A want to *know* is a question, not a want of the thing: "i want to know how long to boil an
# egg" asks about the times, and the entry that keys them carries a keeping `ask` for exactly
# that line. Reading the want as the ask would hand it the boiled-egg keeping row instead.
WANT_KNOWING = ("want to know", "wants to know", "wanted to know", "wanting to know",
                "would like to know", "want to find out", "want to check", "want to ask",
                "want to learn", "like to find out", "need to know", "needs to know",
                "need to find out", "need to check", "need to ask", "need to learn")


ASK_PERSON_PRONOUNS = ("he", "she", "they", "we", "you")


ASK_PERSON_POSSESSIVES = ("his", "her", "their", "our", "your")


def _about_someone_else(phrase):
    """The ask phrase said about someone other than the speaker, or () when it cannot be."""
    words = phrase.split()
    if not any(word.lower() in ("i", "me", "my") for word in words):
        return ()
    out = []
    for person in ASK_PERSON_PRONOUNS:
        out.append(" ".join(person if word.lower() in ("i", "me") else word for word in words))
    for person in ASK_PERSON_POSSESSIVES:
        out.append(" ".join(person if word.lower() == "my" else word for word in words))
    return tuple(out)


def _said_about_someone(ask, forms, seen=None):
    """True when one of the entry's asks is said about a person other than the speaker."""
    line = _line_forms(forms, seen)
    if not any(word in line for word in ASK_PEOPLE):
        return False        # no person in the line, so nothing here changes
    for part in ask or ():
        # The ask parts belong to module-level entries, so the id is the part and the answer is
        # the same whichever entry asks: kept on the line's memo like every other part answer.
        if seen is not None:
            got = seen.get((_ASK_ABOUT_SOMEONE, id(part)))
            if got is not None and got[0] is forms:
                if got[1]:
                    return True
                continue
        said = False
        for phrase in ((part,) if isinstance(part, str) else part):
            if not isinstance(phrase, str):
                continue
            for variant in _about_someone_else(phrase):
                if _phrase_span(forms, variant, seen):
                    said = True
                    break
            if said:
                break
        if seen is not None:
            seen[(_ASK_ABOUT_SOMEONE, id(part))] = (forms, said)
        if said:
            return True
    return False


def _ask_about_someone_only(ask, forms, seen=None):
    """True when the entry's ask is met only by its somebody-else reading.

    The line asked the row's question, and it asked it about a person rather than about the
    speaker: no phrase of the ask is said as written.
    """
    if not ask:
        return False
    if any(_part_score(part, forms, seen) for part in ask):
        return False
    return _said_about_someone(ask, forms, seen)


def _the_subject_it_avoids(item, forms, carried, seen=None):
    """True when the row asks about someone else on the very subject its own avoid list rules out.

    "my mums got a chest infection" then "should she see a doctor": the ask is the see-somebody
    row's, said about her instead of about the speaker, and that row's avoid list names a chest,
    a cough, the flu and a mum - all words of the line this one leans on, so the row stands down
    when the speaker asks it about themselves. Reached through the somebody-else reading the test
    was never made, and two to six weeks was said of a chest infection.

    The earlier line is read for the avoid list only when the ask is met through that reading and
    not through a phrase of the entry's own, so a line the entry reaches as typed never turns on
    this.
    """
    if not carried:
        return False
    if not _ask_about_someone_only(item.ask, forms, seen):
        return False
    memo = {}
    for word in item.avoid:
        if isinstance(word, str) and word.strip() and _part_score(word, carried, memo):
            import os, sys
            return True
    return False


def _the_ask_said(ask, forms, seen=None):
    """True when the line asks what the entry's `ask` says, about the speaker or someone else."""
    if not ask:
        return True
    if any(_part_score(part, forms, seen) for part in ask):
        return True
    return _said_about_someone(ask, forms, seen)


def _wanting(forms, seen=None):
    """True when the line asks for the thing as a want rather than as a question.

    Read from the line, so the line's memo keeps it: this is asked once for every entry whose
    ask the line did not say, and the answer does not depend on the entry.
    """
    if seen is not None:
        got = seen.get(_WANTING)
        if got is not None and got[0] is forms:
            return got[1]
    if _part_score(WANT_KNOWING, forms, seen) > 0:
        answer = False
    else:
        answer = _part_score(WANTING, forms, seen) > 0
    if seen is not None:
        seen[_WANTING] = (forms, answer)
    return answer


def _only_the_want(item, forms, seen=None):
    """True when the want rule, and not the entry's own ask, is why this entry reached the line.

    The want rule is a reading of an entry the line names but does not ask about: "i want to make
    a cake" names the cake and the making, so the recipe's ask ("how long", "how do i") does not
    have to be said. It is not a licence for an entry whose own ask is about something the line
    never mentions: "i want to lose weight" reached the cycling entry this way, because its key
    holds "weight" and "lose" and only its ask ("bike", "cycle", "pedals") says it is about riding
    a bike, so the line got the calories-in-an-hour answer instead of the losing-weight one. An
    entry whose ask the line does say is a better fit than one let in by the want alone, so the
    two are ranked apart.
    """
    return not _the_ask_said(item.ask, forms, seen) if item.ask else False


def _key_on_the_want(item, forms, seen=None):
    """True when a key word this line matched is one of the want phrase's filler words."""
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if not isinstance(alternative, str):
                continue
            if set(alternative.lower().split()) & WANT_FILLER and _part_score(
                    alternative, forms, seen):
                return True
    return False


def _denier_inside(covered, forms, index):
    """True when a denier between the subject and this word is inside the phrase that matched.

    A key phrase can carry its own "not": "not getting any interviews" is what the entry asks
    for, and "im not getting any interviews" is the same line with a subject in front of it.
    Reading the key's own not as the speaker ruling the state out answered both of those with a
    shrug, because the subject "im" made "getting" the state after it.
    """
    back = 2
    while back <= 4 and index - back >= 0:
        at = index - back
        if at not in covered:
            return False      # the matched phrase stops before the denier
        if forms[at] & DENIERS:
            return True
        back += 1
    return False


def _denied(forms, covered):
    """True when the speaker rules out the state a key word names."""
    for index in covered:
        if index - 1 in covered and forms[index - 1] & DENIERS:
            continue          # "not working" is the entry's own key, not a denial of it
        if _denier_inside(covered, forms, index):
            continue          # "not getting any interviews" is the entry's key as well
        back = 1
        while back <= 4 and index - back >= 0:
            before = forms[index - back]
            if before & DENIERS:
                subject = index - back - 1
                if subject < 0 or not forms[subject] & DENY_SAID_OF:
                    break
                between = forms[index - back + 1:index]
                if any(word & STATES_AFTER for word in between) and all(
                        word & (STATES_AFTER | DENY_BETWEEN) for word in between):
                    return True
                break
            if not before & DENY_BETWEEN and not before & STATES_AFTER:
                break
            back += 1
    return False


# The four sets above together: a word here says how a thing is asked, when it happens, how long
# it runs, or which thing is meant. None of them names anything, so a phrase made only of these is
# not the line's own reach into an entry.
A_SAYS_NOTHING = ASK_FRAME | WHEN_WORDS | A_LENGTH_WORD | A_STAND_IN


def _only_the_frame(words):
    """True when every word of a matched key part is one the line is wrapped in, not about."""
    return bool(words) and all(word in ASK_FRAME for word in words)


_TAKE_OFF = None


def _says_removal(forms):
    """True when the line says something is to be taken off something else."""
    global _TAKE_OFF
    if _TAKE_OFF is None:
        _TAKE_OFF = (_forms("off"), _forms("out"), _forms("of"))
    off, out, of = _TAKE_OFF
    for index, word in enumerate(forms):
        if not word:
            continue
        if word & off:
            return True
        if out and of and index + 1 < len(forms) and word & out and forms[index + 1] & of:
            return True
    return False


FRAME_WORDS = ("without",)


_FRAME_PRONOUN_FORMS = None


def _frame_pronoun_forms():
    """The forms of the pronouns above, worked out once."""
    global _FRAME_PRONOUN_FORMS
    if _FRAME_PRONOUN_FORMS is None:
        got = frozenset()
        for word in FRAME_PRONOUNS:
            got |= _forms(word)
        _FRAME_PRONOUN_FORMS = got
    return _FRAME_PRONOUN_FORMS


def _the_subjects_own_clause(here):
    """True when the words at `here` say what the thing in hand does, not what is left out."""
    if not here or not here[0]:
        return False
    mine = _frame_pronoun_forms()
    if here[0] & mine:
        return True
    # "without drying it out", "without scratching them": the gerund's object is the thing.
    if not any(str(form).endswith("ing") for form in here[0]):
        return False
    return any(word and word & mine for word in here[1:3])


def _a_clause_about_the_thing(forms):
    """True when one of the line's frame clauses is about the thing in hand, not a thing left out.

    "how do i roll out pastry without it cracking" has one; "how do i sleep without pills" and
    "can i make pesto without pine nuts" have none, and nothing about them changes.
    """
    starts, _end_forms = _frame_starts()
    for index, here in enumerate(forms):
        if not here:
            continue
        for first_forms, words in starts:
            if not here & first_forms:
                continue
            span = forms[index:index + len(words)]
            if len(span) == len(words) and all(
                    word and word & _forms(wanted) for word, wanted in zip(span, words)):
                after = index + len(words)
                if _the_subjects_own_clause(forms[after:after + 3]):
                    return True
    return False


def _frame_starts():
    """[(the first word's forms, the phrase, how many words it is)], worked out once."""
    global _FRAME_STARTS
    if _FRAME_STARTS is None:
        starts = []
        for phrase in FRAME_WORDS:
            words = phrase.split()
            starts.append((_forms(words[0]), tuple(words)))
        end_forms = frozenset()
        for word in FRAME_ENDS:
            end_forms |= _forms(word)
        _FRAME_STARTS = (starts, end_forms)
    return _FRAME_STARTS


_FRAME_STARTS = None


def _frame_masked(forms):
    """The line with its frame clauses emptied, and the frame words it uses.

    Positions stay in place - a span is a tuple of positions into this list, so emptying a
    position rather than removing it keeps every span an entry has already matched valid.
    """
    starts, end_forms = _frame_starts()
    found = set()
    dead = set()
    index = 0
    while index < len(forms):
        here = forms[index]
        hit = None
        if here:
            for first_forms, words in starts:
                if not here & first_forms:
                    continue
                span = forms[index:index + len(words)]
                if len(span) == len(words) and all(
                        word and word & _forms(wanted) for word, wanted in zip(span, words)):
                    hit = words[0]
                    index += len(words) - 1
                    break
        if hit is None:
            index += 1
            continue
        found.add(hit)
        index += 1
        while index < len(forms):
            if forms[index] and forms[index] & end_forms:
                break
            dead.add(index)
            index += 1
    if not found:
        return forms, frozenset()
    return [frozenset() if at in dead else word for at, word in enumerate(forms)], frozenset(found)


def _key_names(frame_words, item):
    """True when this entry's key asks for the frame word itself."""
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if isinstance(alternative, str) and set(alternative.lower().split()) & frame_words:
                return True
    return False


def _unframed(forms, seen):
    """(the forms to read, the memo to read them with, the frame words the line uses).

    An entry that names the frame keeps the whole line. The others read the masked line with a
    memo of its own: the per-part memo is keyed by the part alone, so the same part asked about
    two different readings of one line would answer the first reading twice.
    """
    if seen is not None:
        got = seen.get(_FRAME_MASK)
        if got is not None and got[0] is forms:
            return got[1], got[2], got[3]
    masked, frame_words = _frame_masked(forms)
    memo = seen if masked is forms else {}
    if seen is not None:
        seen[_FRAME_MASK] = (forms, masked, memo, frame_words)
    return masked, memo, frame_words


def _without_ask_phrase(forms, seen):
    """(the forms to read an avoid word against, the memo to read them with).

    The line with "best way", "best ways" or "how best" blanked, so a row that disowns "best"
    or "way" is not stood down by the asking itself. A memo of its own, for the same reason
    `_unframed` keeps one: the part memo is keyed by the part alone.
    """
    span = ()
    for phrase in ("best way", "best ways", "how best"):
        span = _phrase_span(forms, phrase, seen)
        if span:
            break
    if not span:
        return forms, seen
    if seen is not None:
        got = seen.get(_ASK_PHRASE_MASK)
        if got is not None and got[0] is forms:
            return got[1], got[2]
    masked = list(forms)
    for at in span:
        masked[at] = frozenset()
    masked = tuple(masked)
    memo = {} if seen is not None else None
    if seen is not None:
        seen[_ASK_PHRASE_MASK] = (forms, masked, memo)
    return masked, memo


def _said_again(forms, covered, typed=None):
    """True when the words after the entry's subject are only the news that it has come back.

    "hay fever again", "eczema is back" and "my asthma keeps coming back" state the complaint
    and ask nothing, the same way "i have hay fever" does, and the order of the two is the only
    difference: a report in front of the subject is `_bare_report`'s, and one behind it is this.
    Only a row that has taken `report=True` asks this, so the list is the whole of the freedom
    it gives: nothing in it can name a thing the line is asking about.
    """
    if not covered:
        return False
    if isinstance(typed, (list, tuple)) and len(typed) == len(forms):
        words = [str(word).lower() for word in typed]
    else:
        words = []
        for group in forms:
            forms_of_word = sorted(str(form).lower() for form in group) if group else []
            words.append(forms_of_word[0] if forms_of_word else "")
    last = max(covered)
    after = words[last + 1:]
    if not after:
        return False
    return all(word in HAPPENING_AGAIN or word in REPORT_FILLER for word in after)


def _bare_report(forms, covered, typed=None):
    """True when the line reports the entry's subject about themselves and asks nothing.

    "i have tinnitus" and "ive got hay fever that keeps coming back" both start with the report
    and then name the subject: what comes before the subject is only the report ("i", "have",
    "got", "think"), so the person is telling you about themselves and the entry is the answer.
    A line that puts anything else before the subject is asking or telling something else -
    "do i have hayfever" carries its question word in front, "my hayfever is bad" names the
    subject first - and keeps the two-position rule like every other line.
    """
    if not covered:
        return False
    if isinstance(typed, (list, tuple)) and len(typed) == len(forms):
        words = [str(word).lower() for word in typed]
    else:
        words = []
        for group in forms:
            forms_of_word = sorted(str(form).lower() for form in group) if group else []
            words.append(forms_of_word[0] if forms_of_word else "")
    first = min(covered)
    lead = False
    person = False
    for index in range(first):
        word = words[index]
        if word in REPORT_LEADS:
            lead = True
            continue
        if word in REPORT_PERSON:
            person = True
            continue
        if word in REPORT_FILLER:
            continue
        return False
    # the complaint about a child or a partner needs the verb that says it is theirs ("my son has
    # head lice"), because the person alone in front of the subject is not a report of it
    if person and not lead:
        return False
    return lead


def _asks_to_explain(forms, start, typed=None):
    """True when the words in front of the entry's subject are a request to explain it.

    The subject is `start`, the first word of the part of the key that was matched; everything
    before it has to be one of the ask's own words. "what is sepsis" and "what are the symptoms
    of shingles" pass; "what is the best way to clean a sofa" does not, because "best", "way",
    "clean" are not words of a request to explain the sofa, and the row that names a sofa is not
    the row the line wants.
    """
    if not start or start > 12:
        return False
    if isinstance(typed, (list, tuple)) and len(typed) == len(forms):
        words = [str(word).lower() for word in typed]
    else:
        words = []
        for group in forms:
            forms_of_word = sorted(str(form).lower() for form in group) if group else []
            words.append(forms_of_word[0] if forms_of_word else "")
    lead = False
    for index in range(start):
        word = words[index]
        if word in EXPLAIN_LEADS:
            lead = True
            continue
        if word in EXPLAIN_FILLER:
            continue
        return False
    # "tell me about it" names no thing, and "what is it" is the follow-up question: the thing
    # asked about has to be a word of its own, which the caller has already found in its key.
    return lead


def _only_as_a_kind(forms, span, covered, item, typed=None):
    """True when the entry's subject is only ever said as a description of something else.

    "something light", "anything sweet" - the word is an adjective where it stands, and a row
    that names it as the subject of its own has nothing to answer. The row that explains light
    was the answer to "what should i watch tonight, something light" and to "whats on tonight,
    something light".

    A single word is the whole of the shape. The description is one word and the row reads that
    one word as its subject; a key phrase of several words is a clause the row reads for itself,
    and the pronoun in front of it is the subject of that clause, which names the thing the row
    is about ("everything tastes of metal", "nothing wakes my baby").

    A row whose subject is a qualifier it was built for keeps the line, and so does one whose
    other words are the ask itself: "light" is the subject group of the light-dinner row, so
    "something light for lunch" is exactly its question, and the mood row asks "something" of
    its own. What tells the rows apart is whether anything beside the subject is a word this row
    answers with: the definition rows have nothing but their own ask words there ("what"), the
    others have "lunch", or the "something" their key names.

    Read on the words the person typed, and on the forms otherwise, exactly as
    `_asks_to_explain` does, so a reading built without `typed` still matches.
    """
    if len(span) != 1:
        # One word is the whole of a description: "something light", "anything sweet". A key
        # phrase of several words next to the pronoun is the row's reading of the clause
        # instead, and the pronoun is that clause's subject, not a word in front of a
        # description: "everything tastes of metal" and "nothing wakes my baby" both name a
        # taste and a waking, and their rows answer them.
        return False
    start = min(span)
    if start < 1:
        return False
    if isinstance(typed, (list, tuple)) and len(typed) == len(forms):
        words = [str(word).lower() for word in typed]
    else:
        words = []
        for group in forms:
            forms_of_word = sorted(str(form).lower() for form in group) if group else []
            words.append(forms_of_word[0] if forms_of_word else "")
    if start - 1 >= len(words):
        return False
    if words[start - 1] not in AS_A_KIND:
        return False
    asked = set()
    for part in (item.ask or ()):
        for alternative in ((part,) if isinstance(part, str) else part):
            for word in str(alternative).lower().split():
                asked.add(word)
                asked |= {str(form).lower() for form in _forms(word)}
    said = set()
    for index in covered:
        if index in span or index >= len(words):
            continue
        said.add(words[index])
    said.discard("")
    # Nothing said beside the subject is what the line is about, only the asking and the words
    # the row asks with: nothing of this row's own is in the line, so the subject was a
    # description.
    return all(word in asked or word in EXPLAIN_FILLER for word in said)
