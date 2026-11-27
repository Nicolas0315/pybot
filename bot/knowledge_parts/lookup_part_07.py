"""Part 7 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
import re
from .lookup_part_01 import (
    said, _DREAM, string, guard_passes, WORD, _NOT_A_SUBJECT, _NOT_A_THING, _WRAPPED, ASK_FRAME_IDS,
)
from .lookup_part_02 import (
    entry, tokens, _CURLY_ANY, _past_a_handoff, _without_a_dead_that_only_means_very,
    about_the_chat, _the_age_is_a_childs, the_years_are_a_things,
)
from .lookup_part_03 import (
    ASK_PEOPLE, _forms, _HOLDS_MONEY, _POINTS_AT_IT, _THE_THING_JUDGED, _WHERE_I_PUT,
    _WHERE_TO_KEEP, FEELING_DOMAINS, _ASK_FRAME, _FILLER, _the_animal_rules_out_that_card,
    _with_the_animal_in_hand, _with_the_child_by_place, _without_a_cooking_that_is_a_name,
    POINTS_BACK, COLOUR_WORDS, _SUBJECT_POINTS,
)
from .lookup_part_04 import (
    _frame_masked, _the_subject_it_avoids, _part_matches, A_SAYS_NOTHING,
)
from .lookup_part_05 import (
    _the_thing_the_chat_is_on, _a_thing_that_has_not_gone, _the_kept_rows, _what_is_wrong_with_them,
    _without_the_place, _feeling_occasion, _key_words, _names_a_fault, _names_a_feared_thing,
    _read_a_thing_had, _read_the_adjective, _read_typos, _speaker_is_feeling, _the_ask_on_its_own,
    _the_ask_reading, _vocabulary, _without_possessive, _without_the_ruled_out,
    _answers_a_qualification, _the_card_for_the_place_first, _the_degrees_are_a_temperature,
    _the_person_says_they_are_cold, _the_place_the_line_says_is_cold, _rank, _reaching,
)
from .lookup_part_06 import (
    _defines, _the_name_alone, _the_name_card, ASKING_FIRST, A_COLOUR_USED, _a_keeping_row,
    _another_part, _asks_if_it_is_still_good, _body_parts, _line_rows, _named_things,
    _offers_a_substitute, _plainer, _row_order, _the_ask_in_order, _the_names_in_the_ask,
    _the_subjects_own_row, _words_of, _only_asking_about_it, score,
)


def _the_subject_the_line_leans_on(understood):
    """The forms of the words the line leans on, or [] when it leans on nothing.

    The person the earlier line is about is left out. "husband", "wife" and "mum" are in the
    avoid list of nearly every card about a part of somebody else, because the speaker's own
    part is what those cards hold, and asking about that somebody is the reading this test is
    for - so a card would be ruled out for saying who the person was.
    """
    leans = understood.get("leans_on")
    if not isinstance(leans, dict):
        return []
    words = leans.get("words") if isinstance(leans.get("words"), list) else []
    return [_forms(word) for word in words
            if isinstance(word, str) and word.strip().lower() not in ASK_PEOPLE][:CONTEXT_WORDS]


def _a_price_judged_is_not_answered_here(understood, found):
    """True when the line judges a price and this entry's answer holds no price.

    "is 4 pounds a lot for a chicken" reached the card for the minutes a four-pound bird takes in
    the oven, because four pounds is also a weight, and "is £4 a lot for a pint of milk" reached
    the card about what milk does for you. Neither says anything about money, and the question is
    entirely about money.
    """
    from ..knowledge.prices import a_price_is_judged
    text = str(understood.get("clean") or understood.get("text") or "")
    if not a_price_is_judged(text):
        return False
    reply = getattr(found, "reply", None)
    if callable(reply):
        try:
            reply = reply({}, understood)
        except Exception:  # noqa: BLE001 - a card that needs the chat says nothing here
            return False
    if reply is None:
        reply = ""      # an entry that turns the line down is not answering it either
    if _HOLDS_MONEY.search(str(reply)):
        return False    # this card is about the money, so it is answering the question
    # And only when the base can say what the thing usually costs: "is 20 pounds each way cheap
    # for a train" has no fare row to hold the figure against, and the card about how to get a
    # cheap train is the better answer, so it keeps the line.
    return _a_range_for_the_thing(text, understood) is not None


def _a_range_for_the_thing(text, understood=None):
    """The answer the base gives to "how much is <the thing>", when it holds a price."""
    found = _THE_THING_JUDGED.search(str(text or "").strip().rstrip("?.!"))
    said = found.group(2).strip() if found else ""
    if said.lower() in _POINTS_AT_IT or not said:
        # No thing named: the thing the chat is on is the one the figure is being judged against.
        said = _the_thing_the_chat_is_on(understood)
    if not said:
        return None
    thing = " ".join((found.group(1) or "a ").split() + said.split()) if found else "a " + said
    for question in ("how much is %s" % thing, "how much does %s cost" % thing):
        entry = find({"clean": question, "words": question.split()})
        reply = getattr(entry, "reply", None)
        if callable(reply):
            try:
                reply = reply({}, {"clean": question, "words": question.split()})
            except Exception:  # noqa: BLE001 - a row that needs the chat answers nothing here
                continue
        if reply and _HOLDS_MONEY.search(str(reply)):
            return str(reply)
    return None


def find(understood, entries=None, reject=None, use_context=False):
    """The best Entry for this reading of a line, or None when nothing fits.

    understood: memory["understood"], with "clean" and/or "words".
    entries: an explicit list (tests); by default every domain in bot/knowledge.
    reject: a callable given an Entry; when it says True the entry is passed over and the next
    best is returned. An entry whose reply turns a line down ("how long do i cook it for" after
    mince) should not eat the turn that a lower entry can still answer.
    use_context: also search the line this one leans on, and only when the line alone reached
    nothing. Off by default, because a line that finds its own entry must be answered from its
    own words; the module that has read the conversation turns it on for a follow-up, which
    names no subject of its own ("How long in the oven?", "And if I stuff it?"), so the words
    the understanding engine hands on in `leans_on` are searched as well.

    The line is read as it was typed first, and every entry either line can reach is kept. Only
    when the typed line reaches nothing, and it is a line about somebody the person looks after,
    is it read again as the ask about that thing: "my daughter has head lice" is a question about
    head lice, and the comb is the answer - while a line that already has its card ("my baby is
    teething" is the teething card) is answered by it exactly as before.
    """
    if _DREAM is not None and _DREAM.told_as_a_dream(
            understood.get("clean") or understood.get("text") or ""):
        # A line that tells a dream is the dream, whatever it is about: "i dreamt i failed my
        # exam" was answered with what to do on results day, "i dreamt my teeth fell out" with
        # milk teeth, "i had a dream my mother died" with REM sleep. One rule here covers every
        # entry in every domain, rather than an avoid word in each row that happens to be about
        # something people dream about. The dreams module answers the scene; a question about
        # dreams in general ("why do we dream", "what do dreams mean") names no dream of the
        # person's own and reaches its entry exactly as before.
        return None
    if entries is None and _WHERE_I_PUT.search(
            " ".join(tokens(understood.get("clean") or understood.get("text") or ""))):
        # The answer is the composer's loss pool, and it is the same for every thing.
        return None
    if entries is None and _WHERE_TO_KEEP.search(
            " ".join(tokens(understood.get("clean") or understood.get("text") or ""))):
        # Where a thing is kept is a keeping row's line, whether or not that row would have won
        # the line on its own: only those rows are read, so a line that names an object and how
        # it wants it kept cannot be answered by a row about choosing one. When no keeping row
        # fits, the line is read exactly as it is on any other turn.
        kept = _the_best_entry(understood, _the_kept_rows(), reject, use_context)
        if kept is not None:
            return kept
    found = _the_best_entry(understood, entries, reject, use_context)
    if found is not None and _a_price_judged_is_not_answered_here(understood, found):
        # The line brings a figure in money and asks whether it is dear, and this card answers
        # the thing itself: what a chicken takes in the oven, what milk does for you, what the
        # flour costs to make a loaf. One card that answered its own subject is the whole shape,
        # so no card is tried again for it: the price verdict is the answer, and it is put
        # against the range the same thing sells at.
        return None
    if found is not None:
        return found
    for again in _what_is_wrong_with_them(understood):
        found = _the_best_entry(again, entries, reject, use_context)
        if found is not None:
            return found
    for again in _a_thing_that_has_not_gone(understood):
        found = _the_best_entry(again, entries, reject, use_context)
        if found is not None:
            return found
    for again in _without_the_place(understood):
        found = _the_best_entry(again, entries, reject, use_context)
        if found is not None:
            return found
    return None


def _the_best_entry(understood, entries=None, reject=None, use_context=False):
    """The best Entry for this reading of a line, or None when nothing fits."""
    if not isinstance(understood, dict):
        return None
    understood = _without_the_ruled_out(understood)
    clean = understood.get("clean") or ""
    words = understood.get("words")
    # The understanding layer splits on the curly apostrophe a phone writes, so "doesn’t"
    # arrives here as "doesn" and "t" and no key can match it. The clean text still has it,
    # so take the words from there whenever the line carries one.
    if not isinstance(words, list) or any(ch in clean for ch in _CURLY_ANY):
        words = tokens(clean)
    past = _past_a_handoff(clean)
    if past:
        # The hand-off in front of the line is not what it is about. "one more thing about the
        # boiler" reached the study entry on the words "one" and "thing".
        words = tokens(past)
    # Only the half of the surprise the line still holds: "the hell" is in the line, "on earth"
    # was taken out of it before the reading, and dropping "earth" as well lost the planet from
    # "what on earth is the earth made of".
    left = understood.get("intensifier_left")
    intensifier = understood.get("intensifier") if left is None else left
    if isinstance(intensifier, list) and intensifier:
        # "on earth" and "the hell" name nothing the line is about, so an entry keyed on one of
        # those words must not answer it - not even when the line names a subject of its own.
        # "what on earth is wrong with my boiler" is about the boiler, and the planet's layers
        # were the answer to it. Unlike `background`, this is dropped either way.
        going = {}
        for word in intensifier:
            if isinstance(word, str):
                going[word.lower()] = going.get(word.lower(), 0) + 1
        kept = []
        for word in reversed(words):
            key = word.lower() if isinstance(word, str) else ""
            # The typed word carries the possessive the reading has already taken off: "what on
            # earth's going on" hands over "on earth" and types "earth's", and the planet's
            # layers answered it because the drop compares whole words.
            stem = _without_possessive(key)
            hit = key if going.get(key) else (stem if going.get(stem) else "")
            if hit:
                going[hit] -= 1
                continue
            kept.append(word)
        words = kept[::-1]
    background = understood.get("background")
    if isinstance(background, list) and background and not understood.get("topic_own"):
        # A word that only says WHEN or WHERE it happened is not what the line is about: "it
        # started at work in the garden centre" is about whatever started, and no entry keyed
        # on "garden" answers it. Only a line that names no subject of its own is read this
        # way: a line with one keeps every word of its clause ("i was in the garden when the
        # garden flooded" still reaches the flood), and a line that carries a topic over from
        # the turn before is still answered by the words it typed.
        drop = {}
        for word in background:
            if isinstance(word, str):
                drop[word.lower()] = drop.get(word.lower(), 0) + 1
        kept = []
        for word in reversed(words):
            key = word.lower() if isinstance(word, str) else ""
            if drop.get(key):
                drop[key] -= 1
                continue
            kept.append(word)
        words = kept[::-1]
    if understood.get("kind") == "empty":
        return None
    occasion = _feeling_occasion(words)
    if occasion and not understood.get("asks") and understood.get("topic") != "pets" \
            and not _names_a_fault(occasion) and not _speaker_is_feeling(words) \
            and not _names_a_feared_thing(occasion):
        # "my son looks sad about his bike" is about the son, and the bike is the occasion: the
        # words that name it are taken out of what the knowledge base reads. An ask keeps every
        # word ("how do i stop feeling anxious about my exams" is the anxiety card), and a line
        # whose other words still reach a card keeps that card ("my back hurts and im worried
        # about work" is still the back). Four things keep every word as typed, because the
        # card is about the feeling already: the speaker's own feeling ("im scared of the
        # dentist", "im scared of flying"), a card from a domain about people ("my son is
        # scared of the dark", "worried about her rent"), a thing that is broken ("worried
        # about the washing machine leaking"), and an animal ("my dog is scared of fireworks"
        # wants the fireworks night planned).
        if entries is None:
            from ..knowledge import entries as all_entries  # the registry, to avoid an import cycle
            entries = all_entries()
        seen_in, known_words, _ = _vocabulary(entries)
        here = _best(understood, words, clean, [_forms(word) for word in words],
                     [word.lower() for word in words if isinstance(word, str)],
                     entries, seen_in, known_words, reject)
        if here is None or here.domain not in FEELING_DOMAINS:
            gone = {}
            for word in occasion:
                gone[word] = gone.get(word, 0) + 1
            kept_words = []
            for word in reversed(words):
                key = word.lower() if isinstance(word, str) else ""
                if gone.get(key):
                    gone[key] -= 1
                    continue
                kept_words.append(word)
            words = kept_words[::-1]
    original = words
    stripped = False
    if "dead" in [str(word).lower() for word in words]:
        words = _without_a_dead_that_only_means_very(words)
        stripped = len(words) != len(original)
    if "cooking" in [str(word).lower() for word in words]:
        words = _without_a_cooking_that_is_a_name(words)
        stripped = stripped or len(words) != len(original)
    words = _with_the_child_by_place(words, clean)
    if a_colour_is_worn(understood):
        # "is white ok for a wedding" is "what do i wear to a wedding" said with the colour in
        # place of the word "wear", so the line is read as saying it (see `a_colour_is_worn`).
        # The colour word itself is left out for the same reason the colour a line used as a
        # colour is left out: here it is not the name of a thing, and a row keyed on the bare
        # word ("white" the rice, "brown" the rice) would otherwise answer a question about
        # clothes - "should i wear white to a wedding" reached the brown-rice row, which keys
        # both colours alone, on a par with the wedding row and sorted above it.
        words = [word for index, word in enumerate(words)
                 if not (isinstance(word, str) and word.lower() in COLOUR_ASKED_WORDS
                         and not _a_dress_code(words, index))] + ["wear"]
    forms = [_forms(w) for w in words]
    if entries is None:
        from ..knowledge import entries as all_entries  # the registry, to avoid an import cycle
        entries = all_entries()
    by_domain, every, known = _vocabulary(entries)
    typed = [word.lower() for word in words if isinstance(word, str)]
    if about_the_chat(understood.get("text") or clean):
        return None      # "how did this chat start" is the memory store's line, not a fact
    _read_typos(typed, forms, every, known)
    _read_a_thing_had([str(word).lower() for word in words], forms)
    # An advice ask names its subject once and spends the rest of the line asking, so the subject
    # is the whole subject and is read first: "what should i do about slugs" was answered with the
    # tablespoons card, because "slug" is also how a cook says a small splash.
    wrapped = _wrapped_subject(clean, understood.get("norm_text"))
    whole = _best(understood, words, clean, forms, typed, entries, by_domain, every, reject)
    whole = _the_answer_the_colour_dragged_in(
        whole, understood, words, clean, entries, by_domain, every, reject)
    if a_colour_is_worn(understood):
        whole = _the_card_for_the_occasion_asked(
            whole, understood, words, clean, forms, typed, entries, by_domain, every, reject)
    item = None
    if wrapped:
        item = _the_ask_it_wraps(understood, wrapped, whole, entries, by_domain, every, reject)
    if item is None:
        item = whole
    # The adverbs people put between the words that matter ("what do I actually say?", "how
    # does it really work") are the person leaning in, not a subject, and no keyed phrase holds
    # one: a line that reached nothing as typed is read once more without them. Only then, so a
    # key that wants the word keeps it.
    filler = _FILLER.intersection(typed)
    kept = [word for word in words if str(word).lower() not in _FILLER] if filler else []
    bare = None
    if filler:
        bare = dict(understood)
        bare["clean"] = " ".join(str(word) for word in kept)
    if item is None and bare is not None:
        item = _best(bare, kept, bare["clean"], [_forms(word) for word in kept],
                     [word.lower() for word in kept if isinstance(word, str)],
                     entries, by_domain, every, reject)
    ask = _the_ask_on_its_own(understood)
    if ask:
        asked_for = set(word.lower() for word in ask) - _ASK_FRAME
        if item is None or not (asked_for & _key_words(item)):
            asked = _the_ask_reading(understood, ask)
            found = _best(asked, ask, asked["clean"], [_forms(word) for word in ask],
                          [word.lower() for word in ask], entries, by_domain, every, reject)
            if found is not None:
                item = found
    # Taking the "dead" out is a reading, not a deletion. "the car is dead slow to start" says
    # the car is very slow to start, and the car's own answer is keyed on the word that was
    # taken out, so with the word gone the line reaches nothing and a thing with a known fault
    # gets a shrug. A line that reaches nothing without it is read once more with it, which is
    # the same second look the filler words above get, and only then: an entry that a describing
    # word could drag in must not get in front of a line that had an answer of its own.
    if item is None and stripped:
        item = _best(understood, original, clean, [_forms(word) for word in original],
                     [word.lower() for word in original if isinstance(word, str)],
                     entries, by_domain, every, reject)
    # A line that reached nothing as typed is read once more with the thing each "-y" word
    # describes: "the garden gate is creaky", "my kettle is scaly", "my car brakes are squeaky".
    # A second look and not a wider first one, because the words are otherwise the same and an
    # entry keyed on the adjective itself has already had its turn at them ("my rice came out
    # really sticky again" is the sticky rice row, not a pan-sticking one).
    if item is None:
        described = list(forms)
        if _read_the_adjective(typed, described, every):
            item = _best(understood, words, clean, described, typed, entries, by_domain, every,
                         reject)
    # A follow-up may only search the line before it when it really leans on it: a question that
    # left its subject out, or one that points back at the thing ("is that bad", "i feed it twice
    # a day"). A statement that names its own subject does not - see `leans_on_a_subject`.
    if item is None and use_context and understood.get("leans_on") \
            and leans_on_a_subject(understood):
        item = _following_on(understood, entries, forms, typed, by_domain, every, known, reject)
        if item is None and bare is not None:
            # The phrase the follow-up is keyed on carries a filler too: "what do i actually
            # say?" after a friend line is the same ask as "what do i say?".
            item = _following_on(
                understood, entries, [_forms(word) for word in kept],
                [word.lower() for word in kept if isinstance(word, str)],
                by_domain, every, known, reject)
        # An advice ask that names a subject of its own has changed the subject, so the answer the
        # last turn was about does not stand in for it: after two turns about the lawn, "what
        # should i do about my ex" was a mowing question. The carry-over is right only when the new
        # subject is the old entry's own language ("what should i do about the smell" after a
        # fridge turns on "smell", which the fridge entry holds).
        if item is not None and wrapped and not about(item, wrapped):
            item = None
    if item is not None and _the_animal_rules_out_that_card(item, understood):
        # The card that took the turn is one the animal the line points at stands down for, so
        # the animal is the word the line is missing: "she's been drinking a lot more water"
        # after a cat reached the figure for a person's own water, and the same line with the cat
        # said is the cat's own answer. A card that holds no such word reached the line on its own
        # words and keeps the turn - after an answer about a cat hunting, "she's brought in two
        # this week" is that answer's continuation, not a fresh card that fits the animal too.
        pointed = _with_the_animal_in_hand(words, understood)
        if pointed is not words:
            better = _best(understood, pointed, clean, [_forms(word) for word in pointed],
                           [word.lower() for word in pointed if isinstance(word, str)],
                           entries, by_domain, every, reject)
            if better is not None:
                item = better
    if item is None:
        # "what is a semicolon for" is a definition, and a definition names one thing and asks
        # nothing else: it fails the two-signal rule for the row that knows the thing, and every
        # row that answers the how-to got a shrug. See `_the_thing_asked_about`.
        item = _defines(understood, forms, typed, entries, reject)
    if item is None:
        # A line that is only the name of a thing is that thing raised, and the card that
        # answers the thing said in a sentence answers it too. After the definition ask,
        # because a line that is only a name is also what a definition is and the older reader
        # keeps first claim on the lines it already answered; last of all, so a line with an
        # answer of its own keeps it.
        item = _the_name_alone(_the_name_card([str(word).lower() for word in words],
                                             entries, reject,
                                             _topic_domains(understood, entries)),
                               entries, reject, _topic_domains(understood, entries),
                               understood, words, use_context)
    return item


def leans_on_a_subject(understood):
    """True when the line leans on the subject before it, rather than saying something itself.

    A question left out its subject on purpose ("how long in the oven?"), and a line that
    points back at the thing ("is that bad", "its 3 years old") is about it. A statement that
    names its own subject is not: "i have a cat" then "i work nights" was answered with the
    cats-at-night entry, because the carried subject was searched together with the line's own
    words - "cat" plus "nights" reached an entry neither of them was about, and the person had
    only said what their job was. Nothing else about the night shift was ever said, so the reply
    answered a subject they had not raised.
    """
    if str(understood.get("kind") or "") == "question":
        return True
    if _says_how_the_speaker_handles_it(understood):
        return True
    # Read from the line as typed: the reading's own words have the pronouns taken out, and "i
    # feed it twice a day" after a sourdough is about the sourdough because of the "it".
    line = tokens(str(understood.get("clean") or understood.get("text") or ""))
    return any(word in POINTS_BACK for word in line)


# A colour being held up to a judgement, or offered against another colour, is the question even
# when the line is written without an opener the list above knows: "ok to wear cream", "would
# navy be too much", "white or navy for an interview".
A_COLOUR_ASKED = re.compile(
    r"\b(?:is|are|am|was|can|could|should|would|will|shall|may|might|do|does|did)\b[^.?!]{0,30}?"
    r"\b(?:ok|okay|alright|all right|fine|suitable|appropriate|respectful|acceptable|allowed|"
    r"rude|too much|not done|or|colour|color)\b"
    r"|\b(?:what|which|any|anything|something)\b[^.?!]{0,30}?"
    r"\b(?:wear|wearing|put on|outfit|clothes|colour|color|dress)\b"
    r"|\b(?:%s)\b[^.?!]{0,12}?\b(?:or|vs|versus)\b[^.?!]{0,12}?\b(?:%s)\b"
    % ("|".join(sorted(COLOUR_WORDS)), "|".join(sorted(COLOUR_WORDS))), re.IGNORECASE)


# The words that make a colour one of the clothes: what a person says instead of "wear".
# A person who says "what colour should i wear to the funeral" has not named a colour at all, and
# has asked the same question as the one who says "is black ok": the word "colour" stands in for
# the colour. It is kept out of COLOUR_WORDS, which decides when a colour a line *names* is the
# colour rather than the name of a thing, because "the colour was orange" says the thing was
# orange and not that something was worn.
COLOUR_ASKED_WORDS = COLOUR_WORDS | frozenset(("colour", "color", "colours", "colors"))


WEARING = frozenset("""wear wearing wore worn outfit outfits clothes clothing dressed dress dresses
    suit suits tie frock gown hat hats shirt blouse trousers shoes heels""".split())


# An occasion people dress for. A colour named against one of these is a clothes question with or
# without any other wearing word: "is black ok at a funeral". Only occasions the knowledge base
# has a clothes answer for are listed, because the list decides which card the line reaches, and
# an occasion with no card would turn an answer into a shrug - "is black ok at a cremation" is
# answered today by the card that says whether to go at all, and stays there.
OCCASION = re.compile(
    r"\b(?:weddings?|funerals?|wakes?|memorial service|christenings?|baptisms?|naming ceremony|"
    r"proms?|graduations?|black tie|cocktail|interviews?)\b", re.IGNORECASE)


# "black tie" and "white tie" name a dress code, and the code has a row of its own: "black tie
# wedding what do i wear" is the dinner-jacket answer, and it was the one line the colour rule
# broke (found by tests/test_a_dress_code_is_not_the_office.py). The colour there is the first
# word of a name, not the subject of the question, so it is neither a reason to read the line as
# a wearing question nor a word to leave out of it.
A_DRESS_CODE_AFTER = ("tie",)


def _a_dress_code(words, index):
    """True when the colour at *index* is the first word of a dress code ("black tie")."""
    return (index + 1 < len(words) and words[index] in ("black", "white")
            and str(words[index + 1]).lower() in A_DRESS_CODE_AFTER)


# The word after a colour says whether the colour is what the line is about or an adjective on a
# thing. "is white ok for a wedding" asks about white; "is a white cake ok at a christening" asks
# about the cake, and a clothes card answered it. Found by ready-fig reading pr:14043: "can i take
# my black dog to the wedding", "is red meat ok at a christening lunch" and "is a white cake ok at
# a christening" all reached a clothes card. The first three groups are the words that leave the
# colour as the subject; anything else is a noun that owns it.
AFTER_A_COLOUR_STANDS = frozenset("""
    ok okay alright fine acceptable allowed appropriate suitable good bad wrong safe rude risky
    smart casual formal warm cool nice better best right darker lighter brighter
    to for at in on with and or too not is was are were should would could can will shall must
    the a an this that there it i we they he she my our their his her
    be been being have has had do does did
    """.split())


# Something worn, read as the next word: "a white shirt", "black boots", "a grey suit". Wider than
# WEARING, because this list only decides the word *after* a colour, never whether a line asks
# about clothes at all.
WORN_AFTER_A_COLOUR = frozenset("""
    wear outfit dress dresses frock gown suit suits tie ties shirt shirts blouse top tops trousers
    pants skirt skirts jeans shorts leggings socks tights boots shoes trainers sneakers sandals
    heels flats hat hats cap jumper jumpers cardigan hoodie coat coats jacket blazer scarf gloves
    cotton linen silk wool satin lace leather denim velvet chiffon knit cashmere
    ring rings necklace bracelets earrings jewellery jewelry band watch
    """.split())


def _the_colour_is_the_whole_ask(words, index):
    """True when the colour at *index* is the subject, not the adjective of a thing.

    Read from the word after it: a verdict carries the ask on the colour ("is white ok"), a
    function word hands the ask on to what comes later ("should i wear white to a wedding"), and
    something worn or another colour makes the colour an adjective of clothes ("a white shirt",
    "black and white"). Any other noun takes the colour with it ("a white cake", "a black dog"),
    and then the line is not a question about what to wear.
    """
    if index + 1 >= len(words):
        return True          # the colour ends the line: "what about navy"
    after = index + 1
    # "a white t-shirt" is read as "t" and "shirt", and the letter is not the thing the colour is
    # an adjective of: a word of one letter is skipped for the word that carries it.
    if len(str(words[after])) == 1 and after + 1 < len(words):
        after += 1
    word = str(words[after]).lower().strip(string.punctuation)
    if not word:
        return True          # "is white ok?" - the ask ends with the colour in front of it
    return (word in AFTER_A_COLOUR_STANDS or word in WORN_AFTER_A_COLOUR
            or word in COLOUR_WORDS)


def a_colour_is_worn(understood):
    """True when the line asks about a colour of something worn, so it asks what to put on.

    Read from the line as typed, like `asks_what_to_wear`, and it takes either the line as a
    string or the reading: the reading's own words carry the conversation's topic along with
    them, and a carried topic is what made a colour question about the garden.
    """
    if isinstance(understood, str):
        understood = {"text": understood}
    if not isinstance(understood, dict):
        return False
    said = str(understood.get("text") or understood.get("clean") or "")
    if not said:
        words = understood.get("words")
        said = " ".join(str(word) for word in words) if isinstance(words, (list, tuple)) else ""
    typing = tokens(said)
    typed = set(typing)
    if not typed & COLOUR_ASKED_WORDS:
        return False
    if not any(word in COLOUR_ASKED_WORDS and not _a_dress_code(typing, index)
               and _the_colour_is_the_whole_ask(typing, index)
               for index, word in enumerate(typing)):
        # every colour in the line is half of a dress code, or the adjective of a thing the line
        # is really about ("is a white cake ok at a christening" is the cake)
        return False
    # the words in the order they were typed, because an occasion can be two words and "memorial
    # service" read out of order is neither: "is black ok at a memorial service" was the one
    # occasion in a 44-line probe that the rule did not reach.
    if not (WEARING & typed or OCCASION.search(" ".join(typing))):
        return False
    if understood.get("kind") == "question" or "?" in said:
        return True
    # The opener is the first word of the line that says something, and "so" is how a person
    # starts a question after a pause: "so is white ok for a wedding".
    first = next((word for word in tokens(said) if word != "so"), "")
    return bool(first in ASKING_FIRST) or bool(A_COLOUR_ASKED.search(said))


def _the_words_without_a_colour(clean, words):
    """The line's words with a colour it used as a colour taken out, or None when it used none."""
    said = {match.group("colour").lower() for match in A_COLOUR_USED.finditer(str(clean or ""))}
    said &= COLOUR_WORDS
    if not said:
        return None
    kept = [word for word in words if str(word).lower() not in said]
    if not kept or len(kept) == len(words):
        return None
    return kept


# The words that name nothing, so the check below looks for the line's own subject in an entry's
# key rather than for a word every key holds ("the", "a", "was" are in half the keys in the base).
_BARE_IN_A_KEY = frozenset("""a an the and or but if then than that this these those there here i
    me my mine we us our you your yours he him his she her hers it its they them their is are was
    were am be been being do does did done have has had got get gets getting go goes went gone
    going make makes made just so not no yes very really quite too much many more most some any
    all one two three last next night morning today tonight tomorrow now still also about of to in
    on at for with from by as up down out off over again ever never always thing things bit lot
    kind sort what when where which who how why""".split())


def _the_key_words(entry):
    """Every word an entry is keyed on, flattened, so a line word can be looked for in it."""
    said = set()
    for part in (getattr(entry, "key", ()) or ()):
        if isinstance(part, str):
            said.update(part.lower().split())
        else:
            for one in part:
                said.update(str(one).lower().split())
    return said


# The occasion a line names decides which of the clothes cards answers it. "is white ok at a
# funeral" and "is white ok at a wedding" reach the same two rows, and the wearing word the colour
# stands for carries the ask while the occasion carried nothing: at a funeral the reply named a
# wedding, which reads as the bot not having heard the line. The families are the words an entry
# may be keyed on, not the words a person types: "memorial service" is a funeral card.
THE_SAME_OCCASION = {
    "funeral": frozenset("funeral funerals wake wakes memorial burial cremation".split()),
    "wedding": frozenset("wedding weddings married marriage".split()),
    "christening": frozenset("christening christenings baptism baptisms naming".split()),
    "prom": frozenset(("prom", "proms")),
    "graduation": frozenset(("graduation", "graduations")),
    "interview": frozenset(("interview", "interviews")),
}


def _the_occasion_family(phrase):
    """The family a matched occasion belongs to, or "" when it has no clothes card of its own."""
    word = str(phrase or "").lower().strip()
    for family, members in THE_SAME_OCCASION.items():
        if word in members or word.startswith(family):
            return family
    return ""


def _the_occasion_words(typed):
    """The words an entry may be keyed on, for the occasion this line names itself.

    Read from the line as typed: an occasion carried over from an earlier turn is not what the
    person named this time, and a card for it would answer a question they did not ask.
    """
    said = " ".join(str(word) for word in typed if isinstance(word, str))
    found = set()
    for match in OCCASION.finditer(said):
        family = _the_occasion_family(match.group(0))
        if family:
            found |= THE_SAME_OCCASION[family]
    return found


def _the_card_for_the_occasion_asked(found, understood, words, clean, forms, typed, entries,
                                     by_domain, every, reject):
    """The clothes card for the occasion the line names, when it is not the card reached.

    Only a colour asked about what to wear gets here (see `a_colour_is_worn`), and only a clothes
    entry that is keyed on the occasion can take the turn: the line still has to reach it, so a
    row that does not fit is no answer and the line keeps the one it had.
    """
    asked = _the_occasion_words(typed)
    if not asked:
        return found
    if found is not None and (_the_key_words(found) & asked):
        return found
    for_this = [entry for entry in entries
                if str(getattr(entry, "domain", "")) == "clothing"
                and (_the_key_words(entry) & asked)]
    if not for_this:
        return found
    again = _best(understood, words, clean, forms, typed, for_this, by_domain, every, reject)
    return again if again is not None else found


def _the_answer_the_colour_dragged_in(found, understood, words, clean, entries, by_domain, every,
                                      reject):
    """The entry the line reaches once a colour it used as a colour is left out, else `found`.

    A colour word is not one of the line's subject words, so the answer that needs it is an answer
    about something else: the line is read once more without it, and that entry answers the line
    when it reaches one. Only an entry that has nothing else of the line in it is given up - an
    entry keyed on the colour and on another word the line says is about that word ("the leaves
    have gone brown" is the leaves entry, keyed on both) - and when the second read reaches
    nothing the line keeps the answer it had, so a colour the knowledge base does answer is not
    taken away from a person who asked about it.
    """
    kept = _the_words_without_a_colour(clean, words)
    if kept is None or found is None:
        return found
    others = {str(word).lower() for word in kept} - _BARE_IN_A_KEY
    if others & _the_key_words(found):
        return found
    again = _best(understood, kept, " ".join(str(word) for word in kept),
                  [_forms(word) for word in kept],
                  [word.lower() for word in kept if isinstance(word, str)],
                  entries, by_domain, every, reject)
    return again if again is not None else found


def _best(understood, words, clean, forms, typed, entries, by_domain, every, reject=None,
          framed=False):
    """The highest-ranked entry the line as typed reaches, or the one another reading reaches.

    framed: the line is the subject inside an advice ask, which spends its other words on the
    asking. Only the entries in ASK_FRAME_IDS read it that way (see `score`).
    """
    # An entry can say a test of the whole reading, not only of its key words: "the table leg is
    # cracked" reaches the dry-skin row on its words, but the part belongs to the table. The
    # guard is asked on the entries the line actually reaches, not on a copy of the whole
    # registry: `_word_index` caches by the list's identity, so a fresh list would rebuild the
    # index on every turn - most of a turn's time - for a filter that only ever excludes a few.
    line_parts = _body_parts(words)

    # A line that says a thing has already been kept a while and asks if it is still good is a
    # keeping question, whatever else its words reach (see _STILL_GOOD_ASHERS).
    kept = understood.get("kept")
    keeping_question = bool(kept) and _asks_if_it_is_still_good(typed)

    # The names the question half holds: what the person was actually asking about, as opposed to
    # the situation they described first (see `_the_names_in_the_ask`).
    ask_names = _the_names_in_the_ask(understood, every)
    ask_said = _the_ask_in_order(understood)

    # A number in front of "degrees" is a temperature, not a qualification: "a wedding in italy at
    # 35 degrees, what do i wear" was answered with the pass mark for a degree.
    degrees_are_heat = _the_degrees_are_a_temperature(understood)
    # A figure in years that belongs to a thing is not a child in the line, so no row that reads
    # the age as a child's can answer it (see the_years_are_a_things).
    aged_a_thing = the_years_are_a_things(understood)
    # The place the line says is cold, if any: a card about a person who feels the cold answers a
    # different line, and only when the line does not say how the person feels.
    cold_place = None
    if not _speaker_is_feeling(typed) and not _the_person_says_they_are_cold(typed):
        cold_place = _the_place_the_line_says_is_cold(typed)

    def rank(reading, filter_keeping):
        """The entries the line reaches, with the keeping-only rule on or off."""

        def stands_down(item):
            if not guard_passes(item, reading):
                return True
            if degrees_are_heat and _answers_a_qualification(item):
                return True
            if aged_a_thing and _the_age_is_a_childs(item):
                return True
            if filter_keeping and not _a_keeping_row(item):
                return True
            return _another_part(item, line_parts)

        named = _named_things(reading)
        reached = _line_rows(forms, typed, entries, by_domain, every, named,
                             stands_down=stands_down, framed=framed, ask_names=ask_names,
                             ask_said=ask_said)
        plain_rows = None
        if _frame_masked(forms)[1]:
            # The line has a "without" clause and two entries want it: the one that answers what
            # is asked and the one that answers the thing left out. Keep both readings: the line
            # with the clause emptied is the answer unless the whole line reaches a clearly
            # better entry ("a main for everyone without doing two dinners" is a dinner you cook
            # once, which only the whole line reaches) or a swap entry ("can i make pesto without
            # pine nuts" is the pine-nut swap, not the recipe that uses them).
            plain_rows = _line_rows(forms, typed, entries, by_domain, every, named, frame=False,
                                    stands_down=stands_down, framed=framed, ask_names=ask_names,
                                    ask_said=ask_said)
            if plain_rows:
                plain_rows.sort(key=_row_order, reverse=True)
                if (not reached or _plainer(plain_rows, reached)
                        or _offers_a_substitute(plain_rows[0][5])
                        or _the_subjects_own_row(forms, plain_rows[0][5], reached)):
                    reached = plain_rows
        return reached, plain_rows

    ranked_items, plain = rank(understood, keeping_question)
    if not ranked_items and keeping_question:
        # Nothing that answers keeping reached the line, so the keeping rule has nothing better
        # to offer and the line keeps the answer it had. The rule narrows the field; when the
        # field is empty it is put back, or a food question with no keeping row would be left
        # with no answer at all (or, worse, whatever the next module makes of it).
        ranked_items, plain = rank({k: v for k, v in understood.items() if k != "kept"}, False)
    if not ranked_items:
        return _other_reading(understood, words, clean, entries, reject)
    # A row that reached the line only through the frame (a length word, a pronoun) has not named
    # anything the line is about, and it scored 1 for it: it is not a candidate.
    ranked_items = [row for row in ranked_items if row[1] > 1]
    if not ranked_items:
        return _other_reading(understood, words, clean, entries, reject)
    # an asked entry before a wanted one; then the best score; on a tie the entry that answers a
    # line asking to plan; then the entry that names the thing the line named; then the more
    # specific key; the rest keep the registry's order. A name is the subject of the question,
    # while an ask word ("how many") is only its shape: "how many steps are there in the Eiffel
    # Tower" is about the tower, not about steps a day, but "help me plan a trip to Paris" is
    # about the plan, not about Paris.
    ranked_items.sort(key=_row_order, reverse=True)
    if cold_place is not None:
        ranked_items = _the_card_for_the_place_first(cold_place, ranked_items)
    carried = _the_subject_the_line_leans_on(understood)
    # One line can set a scene and then ask about something else: "we have a cat and a baby,
    # what should we feed the dog" sets a scene (a cat, a baby) and asks about a dog, and "got
    # a suit for the wedding, what should i wear to the interview" names a wedding and asks
    # about an interview. The reading says which thing was said in the clause that carries the
    # ask (`ask_subject`) and which one was only the scene (`setting`), so a card that is about
    # the scene and names nothing of the thing asked is answering the half of the line before
    # the comma. One rule for the whole shape, in words or not: "my mum is 80 next week and we
    # want a cake, what should i bake" names no thing in its ask, so its card is not held back.
    ask_thing = understood.get("ask_subject")
    scene = understood.get("setting")
    scene_only = (isinstance(ask_thing, str) and isinstance(scene, str)
                  and ask_thing != scene and not _says_what_is_missing(understood)
                  # A scene that names a person is a fact about them the ask leans on, not a
                  # rival thing: "my wife is vegetarian, what should i cook for dinner" is one
                  # question about dinner, and the vegetarian card is the answer to it.
                  and _is_a_person(understood, ask_thing) == _is_a_person(understood, scene))
    turned_down = set()
    # A card that answers both halves of the line is not the answer to the half that asks when a
    # card about the asked thing alone is there: "we have a cat and a baby, what should we feed
    # the dog" reached a cat-or-dog comparison ("Dogs, by a whisker") because it names the cat as
    # well as the dog, and that card outranked feeding the dog. The both-card is kept for the
    # second pass, so a line whose only answer speaks of both halves still gets it.
    for whole_line_first in (True, False):
        for _asked, _ranked, _plans, _named, _keys, item, _on_ask in ranked_items:
            if reject is not None and reject(item):
                turned_down.add(item.id)
                continue
            if _the_subject_it_avoids(item, forms, carried):
                continue
            if not scene_only:
                return item
            says_ask = about(item, ask_thing)
            says_scene = about(item, scene)
            if says_scene and not says_ask:
                continue        # an answer about the scene, not about the thing asked
            if says_scene and whole_line_first:
                continue        # about both halves; the second pass comes back for it
            return item
        turned_down.clear()
    if plain is not None:
        # Every entry the line reached with its frame clause emptied has turned it down, so the
        # answer is in the clause itself: "how do i cut an onion without crying" is about the
        # tears, and the entry that answers it is the one keyed on the words the clause carries.
        # The clause is put back and the line read once more, before any repaired reading, so a
        # person who said what they want to avoid still gets an answer that speaks of it (the
        # module that turns down an answer ignoring the clause still has the last word).
        for _asked, _ranked, _plans, _named, _keys, item, _on_ask in plain:
            if item.id in turned_down:
                continue
            if reject is not None and reject(item):
                continue
            if _the_subject_it_avoids(item, forms, carried):
                continue
            return item
    # Every entry the line as typed reached turned it down, because the conversation says the
    # line is about something else. Another reading of the same line may reach one that can
    # answer: `what shood i cook tonight` reaches the plan entry and nothing else, while the
    # tidied line reaches the dinner ideas.
    return _other_reading(understood, words, clean, entries, reject)


# The same question said for a household rather than for one person. Nearly every key in the
# knowledge base is written in the first person singular ("what should i cook", "how do i stop
# condensation", "should i get a dog"), and people say the same thing with "we", "us" and
# "our": "what should we cook this weekend" got a hedge while "what should i cook this weekend"
# got the dinner list. Reading the line once more with those words in the singular is what makes
# one key answer both. Only whole words are shifted, the contractions are read as the words they
# are ("we've" -> "i've", "we're" -> "i'm"), "were" is left alone because it is as often "we
# were" as it is "we are", and the shift is a reading of last resort, so no answer that stands
# today can change.
HOUSEHOLD_WORDS = {
    "we": "i", "us": "me", "our": "my", "ours": "mine", "ourselves": "myself",
    "weve": "ive", "we'd": "i'd", "we'll": "i'll", "we're": "i'm", "we've": "i've",
}


def _household_reading(words):
    """The same words said for one person, or None when the line says "we" nowhere."""
    shifted = [HOUSEHOLD_WORDS.get(str(word).lower(), word) for word in words]
    return shifted if shifted != list(words) else None


def _other_reading(understood, words, clean, entries, reject):
    """The same line read another way, when the line as typed reached nothing that answers.

    Two readings sit beside the words a line was typed as. `plain` is the line with the words
    that are near a key word repaired in place ("wot shud i get me mum 4 xmas", "my scrambeld
    eggs come out rubbrey"); the understanding layer's `norm` is the line with its chat forms
    and missing apostrophes put right, which reaches a key a repair cannot ("what shood i cook
    tonight" carries no `what should i cook`). Both are tried only after the line as typed has
    found nothing, or found only entries that turned it down, so an answer that stands today
    cannot change.

    A third reading is the line said for one person instead of a household, which is what the
    keys are written in (`_household_reading`). It comes last, after the two repairs, because a
    line that has a word to fix needs the fix more.
    """
    plain = understood.get("plain")
    if isinstance(plain, str) and plain and plain != clean:
        again = {key: value for key, value in understood.items() if key != "plain"}
        again["clean"] = plain
        # The repaired line is read as words of its own: `words` is a list everywhere else, and a
        # guard that asks whether a word is in it ("what is the gulf stream") cannot test None, so
        # the whole answer raised and the turn fell to the composer's hedge - "what is today's
        # date" reached no card and got the search hedge for a date the bot works out itself.
        again["words"] = [word.lower() for word in _words_of(plain)]
        found = find(again, entries, reject)
        if found is not None:
            return found
    tidied = [word for word in understood.get("norm") or [] if isinstance(word, str)]
    typed = [word.lower() for word in words if isinstance(word, str)]
    if tidied and tidied != typed and understood.get("norm"):
        again = {key: value for key, value in understood.items() if key != "plain"}
        again["clean"] = " ".join(tidied)
        again["words"] = tidied
        again["norm"] = []
        # the nested search reads the tidied line as a household one itself, so there is no
        # second reading left to do here: returning its answer keeps the shift to one pass
        return find(again, entries, reject)
    shifted = _household_reading([word for word in words if isinstance(word, str)])
    if shifted:
        again = {key: value for key, value in understood.items()
                 if key not in ("plain", "norm")}
        again["clean"] = " ".join(shifted)
        again["words"] = shifted
        return find(again, entries, reject)
    return None


CONTEXT_WORDS = 8      # how much of the earlier line is searched, at most


SPECIFIC = 3    # a key word this few entries share still says something about the line


def _says_a_key_word(item, forms, rarity=None):
    """True when the line itself names one specific key word of the entry.

    This is narrower than `_touches()`: a phrase that only meets the entry as a phrase
    ("getting on" in "he is getting on a bit") is not the line naming what the entry is
    about, while "bites" in "she says it hurts when she bites" is. The distinction is what
    keeps a comment about a dog's age from taking the dog-introduction answer, while a
    follow-up about the biting itself still gets the biting answer.
    """
    if rarity is None:
        rarity = {}
    for part in item.key:
        for _, words, _ in _part_matches(part, forms):
            if len(words) != 1:
                continue
            if any(ch.isdigit() for ch in words[0]) or rarity.get(words[0], 0) <= SPECIFIC:
                return True
    return False


def _touches(item, forms, rarity=None):
    """True when the entry is reached from the line itself by a phrase or a rare word.

    A carried word that the entry half-matches is not enough: "do I need a cable for that"
    after moving phone photos to a laptop shares only "need" with the laptop-buying entry,
    and "need" is in a dozen keys, so the entry is about something else.
    """
    if rarity is None:
        rarity = {}
    for part in item.key:
        for _, words, _ in _part_matches(part, forms):
            if words and all(word in A_SAYS_NOTHING for word in words):
                # "how long" is a phrase and it is in the line, but it says how long and names
                # nothing: it is not the line's own reach into the entry. After "my headphones
                # stopped working", "how long does it last" touched the state pension through
                # "how long" alone, while the row's other half - "stop working" - is the row
                # reading the earlier line as somebody leaving a job.
                continue
            # A figure is specific however many keys hold one: "hes 13" says which child and
            # which answer, and counting "13" as an ordinary word because the knowledge base
            # has entries for five-, eight- and ten-year-olds lost that follow-up.
            if len(words) > 1 or any(ch.isdigit() for ch in words[0]) \
                    or rarity.get(words[0], 0) <= SPECIFIC:
                return True
    return False


def _parts_across(item, carried_forms, forms):
    """True when the two lines between them complete the entry's key, one part from each.

    A key written as (the thing) x (what is asked about it) is specific as a pair, and the two
    halves can arrive a turn apart: "its a garden party" then "what do i wear as a man in his
    50s" is the party-outfit card, the occasion in the line above and the asking in this one.
    The own words alone touch that key only through "wear" and "what", which a hundred keys
    share, so the entry looked like the earlier line's business rather than the person's. It is
    the earlier line's business *and* this one's: different parts, one from each line.
    """
    own, above = set(), set()
    for index, part in enumerate(getattr(item, "key", ()) or ()):
        if _part_matches(part, forms):
            own.add(index)
        if _part_matches(part, carried_forms):
            above.add(index)
    return bool(own - above) and bool(above - own)


def key_words(item):
    """Every word the entry says it is about, singular ("cats" and "cat" count as one)."""
    found = set()
    for part in getattr(item, "key", ()) or ():
        options = (part,) if isinstance(part, str) else part
        for option in options:
            for word in str(option).lower().split():
                found.add(word.rstrip("s") or word)
    return found


def about(item, subject):
    """True when the entry is about the thing, not about a neighbour: a stew is not a steak."""
    head = (str(subject or "").split() or [""])[-1]
    head = head.rstrip("s") or head
    return bool(head) and head in key_words(item)


# The units a weight is said in, as the reading gives them: {"value": 5, "unit": "kg"}.
WEIGHT_UNITS = frozenset(("kg", "kgs", "g", "gram", "grams", "kilogram", "kilograms",
                          "kilo", "kilos", "lb", "lbs", "pound", "pounds", "oz",
                          "ounce", "ounces"))


def a_weight(understood):
    """True when the line gives a weight in kilos, grams or pounds.

    A figure with a unit of mass is what makes a line a kitchen line rather than a question
    about the thing the noun also names: "how long does a 5kg turkey take" is a bird for the
    oven, and it was two full days in Istanbul; "how long does a 5kg chicken take" was the
    lifespan of a pet. A card that answers a country, or how long an animal lives, is not
    asked with a weight in it, so it stands down and the cooking row gets the line.
    """
    for number in (understood or {}).get("numbers") or ():
        if isinstance(number, dict) and str(number.get("unit") or "").lower() in WEIGHT_UNITS:
            return True
    return False


PERSON_PRONOUNS = frozenset("he she they him them".split())


def _refers_to_the_person(understood):
    """True when the line itself speaks of the person: "he is getting on a bit"."""
    words = understood.get("norm")
    if not isinstance(words, list):
        words = str(understood.get("text") or "").lower().split()
    return any(word in PERSON_PRONOUNS for word in words)


SPEAKER_ONLY = ("i", "im", "ive", "id", "ill")


HANDLING_WORDS = ("say", "saying", "said", "tell", "telling", "answer", "answering", "agree",
                  "agreeing", "refuse", "refusing", "nod", "nodding", "smile", "smiling",
                  "laugh", "laughing", "apologise", "apologize", "explain", "explaining",
                  "ask", "asking", "keep", "keeps", "always", "never", "just", "usually")


def _says_how_the_speaker_handles_it(understood):
    """True when the line is the speaker saying how they handle the thing before it.

    "my boss keeps dumping work on me last minute" then "i never say no" is the saying-no
    question, and the line on its own names the behaviour and not the situation: the words it
    has are what the speaker does, and the situation was the line before. A statement that
    names a subject of its own ("i work nights") is not this, so the cats-at-night trap does
    not come back: nothing in it is about handling anything.
    """
    line = tokens(str(understood.get("clean") or understood.get("text") or ""))
    if not line or line[0] not in SPEAKER_ONLY:
        return False
    keys = [word for word in (understood.get("keywords") or []) if isinstance(word, str)]
    if not keys:
        return False
    return all(word in HANDLING_WORDS for word in keys)


def _following_on(understood, entries, forms, typed, by_domain, every, known=(), reject=None):
    """The entry a follow-up reaches with the subject of the line it leans on, or None.

    `reject` is honoured here too: the caller's veto is what stops an entry that declines the
    line from being offered again, so a search that ignored it would loop for ever.
    """
    leans = understood.get("leans_on")
    if not isinstance(leans, dict):
        return None
    words = leans.get("words") if isinstance(leans.get("words"), list) else []
    carried = [word for word in words if isinstance(word, str)][:CONTEXT_WORDS]
    if not carried:
        return None
    carried_forms = [_forms(word) for word in carried]
    _read_typos(carried, carried_forms, every, known)    # a misspelt earlier word too
    together = carried_forms + forms
    together_typed = carried + typed
    allowed = _topic_domains(understood, entries)
    best, best_score, best_domain = None, 0, ""
    seen = {}          # module-level parts only, for the same reason as in _best
    leans_subject = leans.get("subject")
    named_subject = leans_subject if isinstance(leans_subject, str) else ""
    for item in _reaching(entries, together):
        domain = getattr(item, "domain", "") or ""
        if allowed is not None and domain not in allowed:
            continue            # a domain that answers nothing the conversation is about
        if not score(item, together, together_typed, seen):
            continue
        if reject is not None and reject(item):
            continue
        # A guard is a test of the whole reading of the current line, and it holds here too: a
        # row that stands down for the line as typed cannot be brought back by the subject of
        # the line before it. Without this, "he asked me a question" after "she gave me a
        # question to answer" reached the quiz row through the words they share, and a
        # general-knowledge question went to somebody who was talking about someone else.
        if not guard_passes(item, understood):
            continue
        ranked = _rank(item, together, by_domain.get(domain) or every, seen)
        # The subject of the earlier line is what this line leans on, so an entry that names
        # that subject answers the pair before one that only shares its words: "my boss keeps
        # dumping work on me" then "i never say no" is the boundary lesson (the one keyed on
        # the boss), not the timing answer keyed on the work.
        if ranked and named_subject and about(item, named_subject):
            ranked += 100
        if ranked > best_score:
            best, best_score, best_domain = item, ranked, domain
    if _only_asking_about_it(understood, leans):
        # The follow-up names nothing of its own, so the row that answers it is the row the
        # person's own line reached, not whichever row the two lines together score highest.
        # Read as one text, "i feel flat all the time" and "how long do i wait before seeing
        # someone" reach `plan-followup`, and "she is staying with us for a week" and "what
        # should i have in" reach `choosing-between` - both rows from a field neither line is
        # about, both winning on a shared word. The tokens of a follow-up are all ask and point
        # words, so their contribution is noise about the subject rather than a second subject.
        # Unless the two lines complete one key between them, a part each: "i washed my wool
        # jumper hot" then "is it ruined" is one question about a felted jumper, and the row the
        # second line adds a part to answers it better than the row the first line reached on its
        # own. The lean takes the first line's row only where the follow-up adds nothing to it.
        back = _the_best_entry(leans, entries, reject, False)
        if back is not None and not (best is not None and best is not back
                                     and _parts_across(best, carried_forms, forms)):
            best, best_domain = back, getattr(back, "domain", "") or ""
    if best is not None and not _touches(best, forms, by_domain.get(best_domain) or every):
        # The earlier line alone chose it, and the line says nothing about it - unless the two
        # lines complete one key between them, a part each (see `_parts_across`), or the line
        # asks about the subject before it without naming anything of its own.
        if not _parts_across(best, carried_forms, forms) \
                and not _only_asking_about_it(understood, leans):
            return None
    # The follow-up's own words can name what the entry is about with one specific word:
    # "she says it hurts when it bites" after a wobbly tooth, and "should i raise it with her"
    # after a manager keeps cancelling their one-to-ones. That is not a neighbour of the
    # person in the earlier line, it is the thing being asked about, so it may answer below.
    # A phrase alone is not enough: "he is getting on a bit" meets the dog-introduction entry
    # only through "getting on", and the dog's age is not the introduction question.
    said = best is not None and _says_a_key_word(best, forms,
                                                  by_domain.get(best_domain) or every)
    if best is not None and not _reaches(best, carried_forms):
        return None    # the earlier line has no word of this entry: it is not the subject
    subject = leans.get("subject")
    named = isinstance(subject, str) and bool(subject)
    if best is not None and named and not about(best, subject):
        return None    # an entry about a neighbour of what the earlier line was about
    if (best is not None and named and leans.get("subject_type") == "person"
            and understood.get("kind") not in ("question", "request")
            and _refers_to_the_person(understood) and not said):
        # The follow-up is a statement about the person the earlier line named ("he is getting
        # on a bit" after "my dog is called Rex"), and its own words do not name what the entry
        # is about. An entry that shares only the person is then a neighbour of the subject,
        # not the subject: it is the dog's age, not how to introduce a puppy. A statement about
        # the speaker ("i never say no") is not about the person, and a follow-up whose own
        # words reach the entry ("she says it hurts when it bites") keeps it.
        head = set(_forms(str(subject).split()[-1]))
        other = [forms for forms in carried_forms if not (forms & head)]
        # A word of the earlier line can meet the entry as part of a phrase ("bed" in "gets out
        # of bed"), which _reaches() reads whole, so check the words too before standing down.
        words = set()
        for word in key_words(best):
            words |= _forms(word)
        if (other and not _reaches(best, other)
                and not any(forms & words for forms in other)):
            return None
    # An entry that shares only an ordinary word with the earlier line is not the earlier line's
    # subject, it is a neighbour of it: "my van wont start" and the brake-pedal entry meet on
    # "start", which is in a dozen keys, and "it clicks once and then nothing" then got a lesson
    # on brakes. When the earlier line named a thing, `about()` above has already checked this;
    # when it named nothing to lean on, the entry has to be reached by a phrase or a rare word.
    if best is not None and not named:
        if not _touches(best, carried_forms, by_domain.get(best_domain) or every):
            return None
    if best is not None and not _in_topic(best, understood):
        return None    # a fact from a different part of the knowledge base than the conversation
    return best


# A line that asks what to put on is a clothes question whatever the conversation is about.
# The chat's topic is what held the answer out: "its a garden party" then "what do i wear as a
# man in his 50s" was a gardening conversation, and the outfit cards live in a domain that
# answers shopping, so the clothes were never on the table and the person was told it was
# beyond what the bot knows. A wedding (friends-and-relationships) and a christening
# (family-and-parenting) blocked the same way.
_WEAR_ASK = re.compile(
    r"\b(?:what|which|how)\b[^.?!]{0,40}?\b(?:wear|wearing|put on|dress code)\b"
    r"|\b(?:what|which)\b[^.?!]{0,25}?\boutfit\b")


def asks_what_to_wear(understood):
    """True when the line asks what to put on, so the answer is a clothes one.

    Read from the line as typed: the reading's own words carry the topic along with it, and the
    carried words are what made the conversation about the garden rather than about the party.
    """
    said = ""
    if isinstance(understood, dict):
        said = str(understood.get("text") or understood.get("clean") or "")
        if not said:
            words = understood.get("words")
            said = " ".join(str(word) for word in words) if isinstance(words, (list, tuple)) else ""
    return bool(_WEAR_ASK.search(" ".join(tokens(said)))) or a_colour_is_worn(understood)


def _topic_domains(understood, entries=None):
    """The knowledge domains that answer a topic the line is about, or None for all of them.

    A follow-up borrows the earlier line's words, so it can otherwise land in a domain the
    conversation never touched: "what can i take for it" and "how long before i should see a
    doctor" reach the entry for asking for time off, because that entry lists "doctor" too.
    Understanding already knows what the conversation is about, so a fact from a domain that
    answers none of those topics is not the same conversation's fact.

    None means "no opinion": the line names no topic, or every domain declares nothing, and
    then every entry is a candidate. Working it out before the search also keeps a follow-up
    from scoring a thousand entries in domains the conversation never touched.
    """
    topics = []
    if isinstance(understood, dict):
        found = understood.get("topics")
        topics = list(found) if isinstance(found, (list, tuple)) else []
        topics.append(understood.get("topic"))
        leans = understood.get("leans_on")
        if isinstance(leans, dict):
            topics.append(leans.get("topic"))
    topics = [topic for topic in topics if isinstance(topic, str) and topic]
    if not topics:
        return None
    from ..knowledge import by_topic    # imported here: bot.knowledge imports this module to build entries
    judged = by_topic()
    allowed = {name for name, answered in judged.items()
               if not answered or any(topic in answered for topic in topics)}
    if entries is not None:
        allowed &= {getattr(item, "domain", "") or "" for item in entries}
    if allowed and asks_what_to_wear(understood):
        allowed.add("clothing")     # the ask is about clothes, whatever the chat is about
    return allowed if allowed else None


def _in_topic(item, understood):
    """Whether `item`'s own domain is one that answers lines about a topic of the line."""
    allowed = _topic_domains(understood)
    if allowed is None:
        return True
    return (getattr(item, "domain", "") or "") in allowed


def about_the_topic(item, understood):
    """True when the entry's domain answers a topic this reading is about.

    The same test a follow-up makes before it takes a fact: a bare ask ("what can i do") leans
    on the words of the line before it, and one of those words sits in other domains too, so
    "my kids wont listen to me" and then "what can i do" reached the music entry off the word
    "listen". A fact from a part of the knowledge base the conversation never touched is not
    the same conversation's fact.
    """
    return _in_topic(item, understood)


# The words that say something is not there: "i havent got a blender, can i still make soup" is
# not a line that sets a scene and then asks about soup - the blender it has not got is the
# condition the soup is asked under, so the answer is about blending without one.
MISSING_WORDS = re.compile(
    r"\b(?:no|not|without|havent|hasnt|hadnt|dont|doesnt|didnt|cant|cannot|isnt|arent|wasnt|"
    r"wont|lack|lacks|lacking|empty|none|nothing|ran out|run out|out of)\b")


def _is_a_person(understood, word):
    """True when the line named this word as a person rather than as a thing."""
    for ent in (understood or {}).get("entities") or ():
        if isinstance(ent, dict) and str(ent.get("text", "")).lower() == str(word).lower():
            return ent.get("type") == "person"
    return False


def _says_what_is_missing(understood):
    """True when the half of the line before the ask says something is not there.

    A clause in front of the question is usually a scene, and the ask is about the thing after
    it. But a clause that says a thing is missing is a condition on the ask, not a scene: "i
    havent got a blender, can i still make soup" asks how to make soup without one, so the card
    keyed on the blender is the answer and the thing the ask names is not what to answer about.
    """
    focus = list((understood or {}).get("focus") or ())
    for clause in (understood or {}).get("clauses") or ():
        if list(clause) == focus:
            continue
        text = " ".join(str(word) for word in clause if isinstance(word, str))
        if MISSING_WORDS.search(text):
            return True
    return False


def _reaches(item, forms):
    """True when the entry matches at least one word of the line searched for it.

    The earlier line has to be the reason the entry is on the table. When it is not, the words
    carried over are a wish rather than a subject, and the entry answers something the person
    did not say: "it clicks once and then nothing" after "my van wont start" reached the
    brake-pedal entry, which shares no word with the van at all.
    """
    for part in item.key:
        if _part_matches(part, forms):
            return True
    return False


def names_its_own_subject(item, understood):
    """True when the entry's own subject is one this line names for itself.

    The first key part of an entry is its subject (the rest are the ask, the property or the
    setting), so this asks the one question a topic test cannot: does the line say the thing the
    entry is about? "why do we get allergies" says "allergies", which is the subject of the
    allergy entry, whatever the rest of the conversation is on. A domain test on its own cannot
    see that, because an entry lives in the domain that was written for it, and the domain that
    explains allergies is not the one a chat about a pet is in.
    """
    if not isinstance(understood, dict):
        return False
    clean = understood.get("clean") or understood.get("text") or ""
    forms = [_forms(word) for word in tokens(str(clean))]
    key = getattr(item, "key", ()) or ()
    return bool(forms) and bool(key) and bool(_part_matches(key[0], forms))


def _wrapped_subject(clean, norm_text=None):
    """The subject an advice ask wraps, or None when the line is not one.

    The wrapper is looked for in the line as typed and again in its ordinary words, because
    "any tips 4 a hangover" only says "for" once the chat-speak is undone.
    """
    plain = " ".join(word for word in WORD.findall(clean or "") if word not in _FILLER)
    for text in (clean, norm_text, plain):
        text = " ".join((text or "").replace(" | ", " ").split())
        if not text:
            continue
        for pattern in _WRAPPED:
            found = pattern.match(text)
            if not found:
                continue
            subject = found.group("subject").strip(" .,!?;:")
            if subject.lower() in _NOT_A_THING:
                return None
            if not any(word not in _NOT_A_SUBJECT for word in WORD.findall(subject)):
                return None
            return subject
    return None


def _the_ask_it_wraps(understood, subject, whole, entries, by_domain, every, reject):
    """The entry the subject inside an advice ask names, or None.

    The subject read on its own is what the line is about, so it answers when it can: "what
    should i do about slugs" was the tablespoons card, because "slug" is also how a cook says a
    small splash. When the subject on its own reaches nothing, the reading adds nothing and the
    line keeps whatever the whole of it found ("my hay fever is awful this week, what actually
    works" is a line whose subject is not a thing to look up, and its answer stands).
    """
    if not subject:
        return None
    words = [word for word in tokens(subject) if word not in _SUBJECT_POINTS]
    if len(words) == 1:
        # one everyday noun, which is the only subject the ask around it can complete. The noun
        # is read without the words that framed it: "what should i put on for a wedding" wraps
        # the subject "for a wedding", and reading the phrase whole reached the hotel row keyed
        # on "for a wedding" - a block of rooms booked for one - instead of the outfit answer the
        # line had already found. A noun on its own is the thing the ask is about.
        alone = _the_subject_alone(" ".join(words), entries, by_domain, every, reject)
        if alone is not None:
            # A framed entry the whole line reached on its own words keeps the turn: "any tips
            # for snoring" is the snoring explanation, and "what should i do about the damp" is
            # the water found first. The frame is for a subject the whole line could not reach.
            if whole is not None and getattr(whole, "id", "") in ASK_FRAME_IDS:
                return None
            return alone
    if whole is not None:
        # A subject of more than one word is a line in its own right only when the whole line
        # reached nothing. Otherwise the words it was said with are part of what it means:
        # "what should i do about my cat scratching the sofa" is a cat line and the words that
        # make it one are outside the subject, so reading the subject alone lost that.
        return None
    again = {key: value for key, value in understood.items()
             if key not in ("plain", "norm", "norm_text")}
    again["clean"] = subject
    # ... and the subject's own words, never None: a guard that asks whether a word is in
    # `words` raises on None, and the whole turn loses its answer.
    again["words"] = [word.lower() for word in _words_of(subject)]
    found = find(again, entries, reject)
    if found is not None:
        return found
    return _the_subject_alone(subject, entries, by_domain, every, reject)


# A subject word a dozen entries use is a word about other things as well: "kettle" is a scaled
# one, a broken one and a cheap one, so the ask around it says nothing about which is meant.
COMMON_WORD = 12


def names_one_thing(words, every):
    """True when the words of a subject name one thing rather than a dozen.

    A word a dozen entries use is a word about other things as well: "kettle" is a scaled one, a
    broken one and the price of one, and "what can i do about my kettle" asks about whichever it
    is, so the ask around it says nothing and the line is read by its words alone. A word one or
    two entries use - slugs, limescale, snoring - names that thing, so being asked about it is
    the second signal the one word cannot give.
    """
    for word in words:
        counts = [every.get(form) or 0 for form in _forms(word)]
        if not counts or max(counts) > COMMON_WORD:
            return False
    return True


def _the_subject_alone(subject, entries, by_domain, every, reject=None):
    """The entry a one-noun subject inside an advice ask reaches, or None.

    The subject is read with the ask around it kept as a signal, which is what `framed` means:
    "what should i do about the condensation" names one thing and asks about it, so the entry
    that owns that thing answers, while every entry not listed in ASK_FRAME_IDS is still read by
    the ordinary two-word rule. A subject with more words than that is read like any other line
    and finds its answer without this.
    """
    words = tokens(subject)
    if not words:
        return None
    forms = [_forms(word) for word in words]
    typed = [word.lower() for word in words if isinstance(word, str)]
    return _best({"clean": subject, "words": None, "kind": "question"}, words, subject, forms,
                 typed, entries, by_domain, every, reject,
                 framed=names_one_thing(
                     [word for word in words if word not in _SUBJECT_POINTS], every))
