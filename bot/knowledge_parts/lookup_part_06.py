"""Part 6 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
import re
from .lookup_part_01 import (
    ASK_FRAME_IDS, MIN_SCORE, WORD_WEIGHT, _asking_with, said, guard_passes, _bounded, GRAMMAR_ONLY,
    _NOT_A_SUBJECT, lexicon,
)
from .lookup_part_02 import (
    tokens,
)
from .lookup_part_03 import (
    ASK_PHRASE_WORDS, _DEFINITION_ASK, _DEFINITION_EMPTY, _DEFINITION_POINTERS, _DEFINITION_TAIL,
    _DEFINITION_TROUBLE, _forms, _BEFORE_THE_THING, _BE_VERBS, _DEFINING_VERBS,
    _DEFINITION_ARTICLES, NAME_ALONE_DOMAINS, A_STATE_AS_A_NAME_END, A_STATE_IN_THE_PHRASE,
    NOT_A_NAME_ALONE, FOLLOW_ON_WORDS, POINTS_BACK, ASK_FRAME_WORDS, SUBSTITUTE_WORDS, _CUT_BESIDE,
    GENERAL_BODY, RETURNED_AFTER, _STILL_GOOD_ASHERS, _A_KEEP_AND_A_LENGTH, _KEEPING_WORDS,
)
from .lookup_part_04 import (
    _asks_to_explain, _bare_report, _denied, _key_names, _key_on_the_want, _misspelt_avoid,
    _only_as_a_kind, _only_the_frame, _part_match, _part_matches, _part_score, _phrase_span_between,
    _said_again, _says_removal, _the_ask_said, _unframed, _wanting, _without_ask_phrase,
    _only_the_want, _a_clause_about_the_thing,
)
from .lookup_part_05 import (
    _keeping_row, _keeps_failing_at, _says_a_shape, _the_whole_subject, _two_positions,
    _under_their_own_hands, _key_forms, _key_words, _rank, _reaching,
)


def score(item, forms, typed=None, seen=None, frame=True, framed=False):
    """The entry's score for a line, or 0 when it is not about the entry.

    Two different words of the key have to be in the line. Without that, a part like
    ("rain", ("raining", "why")) scores 4 from "it rained" alone, because raining and
    rain are loose forms of the same word; one passing mention would then answer the
    line. The same rule keeps "freeze" from a freezer fact out of a call that freezes.

    The first part is the subject and it has to be said. An entry written as
    (subject) x (what is said about it) x (how it is asked) can otherwise reach the
    total from the last two parts alone: "im thinking of getting a bike to cycle to
    work" brought "work" and "get" and was answered by the bank-holidays entry, and
    "how do i unblock a slow kitchen sink without calling a plumber" reached the
    cupboard clear-out on "kitchen" and "how do i". Both lines name a thing the entry
    never mentions.

    That only holds where the key is written that way. An entry whose key is a flat
    list of phrasings - `water-in-ear` is "water in my ear", "water is stuck in my ear",
    "swimmers ear", and twenty more, each a whole subject - has no first part to insist
    on, and reading its first phrasing as the subject took "i have swimmers ear" off
    its own answer: "Noted: you have swimmers ear." So the rule is applied to every key
    that has a group in it, which is what (subject) x (about) x (ask) looks like.

    A key that is only partly grouped still has a first part: `email-to-teacher` is
    ('teacher', 'childs', 'school', ('email', 'write', 'message')), and with the rule
    read off the first part alone it answered "how do i choose a school for my child"
    on the bare word "school" - the school was named, the email never was. So the test
    is whether any part is a group, not whether the first one is.

    framed: the line is the subject inside an advice ask ("what should i do about the
    condensation"), which spends its other words on the asking. Only for the entries in
    ASK_FRAME_IDS, whose subject is one everyday noun, the ask around it is the second signal
    and one word of the subject part is enough.
    """
    if not forms:
        return 0
    if typed and _under_their_own_hands(item, typed):
        # The row would tell them how to do it themselves; they asked whether the bot can do it.
        return 0
    masked, memo, frame_words = _unframed(forms, seen) if frame else (forms, seen, frozenset())
    if frame_words and not _key_names(frame_words, item):
        # "how do i sleep without pills" is about sleeping: the entry that answers the pills
        # (a pharmacy takes them back) must not take the line. Only the frame words, though -
        # the rest of the line still reads as it did.
        forms, seen = masked, memo
    # An explaining row reads a line that names its subject once, so it is exempt from the
    # two-position pre-filter for the same reason a stated complaint is: the ask in front of
    # the subject is the second signal, and `explained` below is what enforces it.
    # The framed reading is the exception to the two-position pre-filter for the same reason a
    # stated complaint is: the ask around the subject is the second signal, and only the
    # entries in ASK_FRAME_IDS whose subject is the whole of what the ask is about read it.
    framed_one = bool(framed and item.key and getattr(item, "id", "") in ASK_FRAME_IDS
                      and _the_whole_subject(item.key[0], forms, seen))
    if not item.report and not item.explain and not framed_one and not item.shape \
            and not _two_positions(forms, item):
        # A shape is a second signal in its own right - "4%" says a figure, and one word of a
        # dish says the dish - so a row that carries one is not dropped here for holding a
        # single position of the line. Whether the figure is really there is asked below, where
        # the shape answers, so a row whose shape does not match still scores 0.
        return 0
    if item.ask and not _the_ask_said(item.ask, forms, seen):
        if not _wanting(forms, seen) or _key_on_the_want(item, forms, seen):
            return 0
    total = 0
    covered = []
    first = ()
    removal = _says_removal(forms)
    grouped = any(isinstance(part, (tuple, list, frozenset, set))
                  for part in (item.key or ()))
    for index, part in enumerate(item.key):
        weight, words, span = _part_match(part, forms, covered, seen)
        if index == 0 and typed and len(span) == 1 and span[0] < len(typed) \
                and _asking_with(typed, span[0]):
            # The question's own modal is not the thing the line is about, so it cannot be the
            # subject the key is built on: "can i still travel" was answered by the cool-bag card,
            # whose subject group is "can" (a can of drink). The one word is dropped and the rest
            # of the line still scores, which is what keeps "can you keep it cold" on the drinks
            # row (the "cold") and "what can i do with it" on the dish the previous turn named (the
            # phrase "can i do" is two words and a phrase is not a bare modal, so it is untouched).
            # No memo here: `seen` answers per part, so the cached match would hand the modal
            # straight back. This is one part of one entry on a line that asks with a modal.
            bare = list(forms)
            bare[span[0]] = frozenset()
            weight, _, span = _part_match(part, bare, covered)
        elif (index and removal and weight > 1 and _only_the_frame(words)
              # ... but not where the subject part was itself a phrase: "how do i get out of
              # debt" names a thing of two words, and the second part could only be reached
              # through the ask ("get out", "how do i"), so the rule took the whole answer away
              # and the line scored 3 - under MIN_SCORE - while "get out of debt" answered.
              # A one-word subject is what the rule was written for ("tar" on a jacket).
              and len(first) < 2):
            # "how do i get tar off a jacket" names tar and jacket; "get" is how the person
            # asks. A later key part that the line only reaches through those words is the
            # ask, not a second thing about the entry: one of them can be an accident of how
            # the line is phrased and counts for one, and a phrase of them ("how do i", "do i")
            # is the frame itself and counts for nothing. Without that, `coat-worth` read
            # "jacket" and "get" and answered a tar mark with the coat-buying row, and
            # `paving-slab` read "paving slab" and "how do i" and answered cement on a slab
            # with the row about laying one.
            #
            # The part may also have matched a real word of the line: the second part of
            # `child-off-school` is "should i" and "child" on "should i keep my child off
            # school", and a phrase outweighs a word, so the ask won the part and the frame rule
            # then took it away, and the school question lost its own card to the kitchen. Where
            # the same part reaches a word that is not the ask, that word is what the line is
            # about and it counts at its own weight.
            # A word the earlier key part already used still counts here: "how do i tell my
            # kid off" reaches this row through "tell my kid off" (3) and its "kid" (2), but
            # "kid" is the word the first part matched, and the frame rule then took the whole
            # part away, so the line scored 3 and reached nothing while the same line without
            # "how do i" was answered. The overlap is one signal matched twice, not a second
            # thing about the entry, so it is worth what a word is worth.
            spare = [hit for hit in _part_matches(part, forms)
                     if not _only_the_frame(hit[1])]
            if spare:
                weight, words, span = spare[0]
            else:
                weight = 1 if len(words) == 1 else 0
        total += weight
        covered.extend(span)
        if index == 0:
            first = span
    if grouped and not first:
        return 0
    # A stated complaint is one signal: "i have tinnitus" names the subject and asks nothing,
    # so the entry that answers it never came within reach of the line and a chat nod ("Noted:
    # you have tinnitus") took the turn. A row that says the complaint is worth answering when
    # it is only stated counts the report itself as the second signal, which is also what lifts
    # a two-word subject ("i have hay fever" scored 3) over MIN_SCORE. The subject check above
    # is what keeps a bare "bad" - a word of the eczema row's second part - out of a knee.
    bare = bool(item.report) and (_bare_report(forms, covered, typed)
                                  or _said_again(forms, covered, typed))
    shaped = bool(item.shape) and bool(first) and _says_a_shape(item.shape, typed, forms)
    explained = bool(item.explain) and bool(first) and _asks_to_explain(forms, min(first), typed)
    if first and not explained and _only_as_a_kind(forms, first, covered, item, typed):
        # The subject of this row is the word that describes the thing asked for, and the line
        # says nothing else about it: see AS_A_KIND.
        return 0
    one_word = len(set(covered)) < 2
    if one_word and not bare and not explained:
        # The ask around a one-noun subject is its second signal, and only for the
        # entries whose subject is that kind of everyday noun (see ASK_FRAME_IDS),
        # and only where that word names one thing. The subject still has to be the
        # whole of what the ask is about: "what should i do about the damp patch" is
        # a patch.
        if not framed_one and not shaped:
            return 0
    if bare or shaped or explained:
        total += WORD_WEIGHT
    if _denied(forms, covered):
        return 0
    if not one_word and total < MIN_SCORE:
        return 0
    parts_said = _body_parts(typed) if typed else None
    ask_forms = ask_seen = None
    for word in item.avoid:
        key = word.strip().lower() if isinstance(word, str) else ""
        if key in ASK_PHRASE_WORDS:
            if ask_forms is None:
                ask_forms, ask_seen = _without_ask_phrase(forms, seen)
            if _part_score(word, ask_forms, ask_seen):
                return 0
        elif _part_score(word, forms, seen) or _phrase_span_between(forms, word, seen):
            # A fence word is read the way the line means it. "back" is a part of the body in "a
            # mole on my back" and the word that says the thing returned in "the mole in the
            # garden is back", and the garden's mole row fences "back" to keep off the skin: that
            # fence took the second line off its own answer and left it to a fitness card. The
            # reading already tells the two apart (see `_body_parts`), so a fence word that names
            # a part this line does not have is not a reason to stand the row down.
            if not _a_part_the_line_does_not_have(word, parts_said):
                return 0
    if typed and _misspelt_avoid(item, typed):
        return 0
    failing_at = _keeps_failing_at(forms, seen)
    if failing_at is not None and _keeping_row(item) and (
            not first or min(first) != failing_at + 1):
        # The row answers how long a thing keeps, and the line says the thing keeps going wrong
        # ("my bread keeps coming out flat", "my fridge keeps beeping", "my coffee keeps tasting
        # bitter"): the fault is what is wanted, not the shelf life. The one exception is a row
        # whose own words start on the word straight after the verb, because then they are what
        # the person keeps doing rather than the thing that keeps going wrong: in "i keep running
        # to the loo" the row is "running to the loo", so "keep" is only how the complaint is
        # phrased. "my son keeps losing his jumper at school" is not that - his jumper begins
        # later in the line - and neither is "my coffee keeps tasting bitter", where the row's
        # subject is the coffee before the verb.
        return 0
    return total


def _the_thing_asked_about(clean):
    """The thing a definition line asks about, as its words, or () when it is not one."""
    if not isinstance(clean, str) or not clean.strip():
        return ()
    found = _DEFINITION_ASK.match(clean.strip().lower())
    if not found:
        return ()
    thing = next((part for part in found.groups() if part), "")
    opening = (thing.split() or [""])[0].strip("'\"-")
    if opening in _DEFINITION_POINTERS:
        # "what is there to do in hastings" asks what a place has to offer, not what a word
        # means, and the battle of Hastings would answer it.
        return ()
    raw = thing.lower().replace("\u2019", "'")
    if any(word in _DEFINITION_TROUBLE for word in _words_of(raw)) \
            or any(phrase in " %s " % raw for phrase in ("going on", "up with", "up to")):
        # "what is wrong with my knee", "what is going on with my car", "what is up with my dog"
        # all ask what is the matter: a diagnosis belongs to the row that knows the thing, and a
        # card about the knee is the wrong answer to it.
        return ()
    words = []
    for word in thing.replace("\u2019", "'").split():
        word = word.strip("'\"-")
        if not word or word in _DEFINITION_EMPTY or word in _DEFINITION_TAIL:
            continue
        if len(word) < 2 and not word.isalpha():
            continue
        words.append(word)
    while words and words[-1] in _DEFINITION_TAIL:
        words.pop()
    return tuple(words[:3])


def _words_of(text):
    """The words of a phrase, lowercased and stripped of punctuation."""
    return [word.strip("'\"-?!.,;:") for word in text.split() if word.strip("'\"-?!.,;:")]


def _asks_what_it_is_for(clean):
    """True when the definition line asks what the thing is for, not what it is.

    "what is a semicolon for" is answered by what the thing does ("Use a semicolon to join two
    full sentences"), and "what is a warranty" by what the thing is ("A warranty is a bonus on
    top of your rights"). The two shapes are not interchangeable: a use is not a definition, and
    a definition is not an answer to what something is for.
    """
    if not isinstance(clean, str):
        return False
    return bool(re.search(r"\bfor\b\s*\??\s*$|\bused for\b|\bdo(?:es)? (?:it|that|this) do\b",
                          clean.strip().lower()))


# How many words may come before the thing in a defining sentence: "In the UK, a warranty is..."
# is a definition, "a cup of tea or coffee is mostly water" is not.
_SUBJECT_AT_MOST = 6


def _a_number(word):
    """True for a word with a digit in it ("4pm", "2nd", "500ml")."""
    return any(char.isdigit() for char in word)


def _the_thing_in(sentence, thing):
    """Where the whole thing is said as one phrase in the sentence, or None."""
    words = [word.lower() for word in tokens(sentence) if isinstance(word, str)]
    wanted = [_forms(word) for word in thing]
    for start in range(len(words) - len(wanted) + 1):
        run = words[start:start + len(wanted)]
        if all(_forms(word) & want for word, want in zip(run, wanted)):
            return start, words
    return None


def _the_reply_defines(reply, thing, purpose=False):
    """True when the reply's opening sentence defines the thing, so a definition ask is answered.

    Every word of the thing has to be said as one phrase: the row that answers an abnormal smear
    result says "An abnormal smear means some cells looked a little different", which names half
    of "smear test" and answers a different question, and the shower row says "the wet air stays
    in the room" about a wet room.
    Then the phrase has to be doing the defining - what it is ("A warranty is a bonus on top of
    your rights") or, when the person asked what it is for, what it does ("Use a semicolon to
    join two full sentences"). A row that merely mentions the thing while answering something
    else stays out: "Who owns a boundary fence is in the deeds" is about a fence.
    """
    if not isinstance(reply, str) or not reply.strip():
        return False
    opening = re.split(r"(?<=[.!?])\s", reply.strip(), maxsplit=1)[0]
    found = _the_thing_in(opening, thing)
    if found is None:
        return False
    if found[0] > _SUBJECT_AT_MOST:
        # A definition says what the thing is in its own opening words, so the thing has to be
        # near the front: "No, not in ordinary amounts: a cup of tea or coffee is mostly water"
        # is an answer about whether coffee dehydrates you, and it does not define coffee.
        return False
    if purpose:
        return True
    start, words = found
    if start and words[0] not in _DEFINITION_ARTICLES:
        # The phrase before the thing has to open with an article: "A short nap is worth having"
        # defines a nap, while "Ground coffee is at its best two weeks after opening" is about
        # storage and "Feet that are always cold" is about feet.
        return False
    before = words[:start]
    if any(word in _BE_VERBS for word in before):
        # A be-verb ahead of the thing means the sentence has another subject: "Feet that are
        # always cold are usually circulation" is about feet, and it does not define a cold.
        return False
    if before and (before[-1] in _BEFORE_THE_THING or _a_number(before[-1])):
        # "the top third of your CV", "a 4pm coffee", "the first cup of coffee": the thing sits
        # inside a phrase about a portion or a time, which is an example and not a definition.
        return False
    after = words[start + len(thing):start + len(thing) + 1]
    return bool(after) and after[0] in _DEFINING_VERBS


def _the_key_names_the_thing(item, thing):
    """True when one phrase of the entry's key is the thing itself, word for word.

    "what is a food bank" is the row keyed on "food bank", and the words are read the way every
    other match is read, so "will" reaches "wills" and "boundary" reaches "boundaries". A key
    that only holds the words inside a longer phrase is about that longer phrase - "boundary
    fence" is not a definition of a boundary, "sports wash" is not a sports bra - so the phrase
    has to be as long as the thing.
    """
    wanted = [_forms(word) for word in thing]
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if not isinstance(alternative, str):
                continue
            words = alternative.lower().split()
            if len(words) != len(wanted):
                continue
            if all(_forms(word) & want for word, want in zip(words, wanted)):
                return True
    return False


def _the_name_card(typed, entries, reject=None, allowed=None):
    """The entry that is *named* the line, or None.

    The entry's own name is the first alternative of the first part of its key, and only that
    counts: a card lists many ways of saying its subject, and most of them are meant to be
    reached with a second signal, not on their own. "ear infection" and "head ache" are
    alternatives of the swimmer's-ear and migraine cards, and those cards are the right answer
    to a sentence that says the rest; opened on the name alone they answered a question nobody
    asked. The card called "nappy rash" is the card for nappy rash.

    A one-word name is not enough either: "money", "sofa" and "boiler" are the objects of a
    conversation as often as they are a subject to open, and a person answering the bot own
    question meant the pizza, not the pizza card.
    """
    said = set(typed)
    found = []
    for item in entries:
        if getattr(item, "domain", None) not in NAME_ALONE_DOMAINS:
            continue
        if reject is not None and reject(item):
            continue
        if allowed is not None and getattr(item, "domain", None) not in allowed:
            continue
        key = getattr(item, "key", ()) or ()
        if not key:
            continue
        part = key[0]
        alternatives = part if isinstance(part, tuple) else (part,)
        if not alternatives or not isinstance(alternatives[0], str):
            continue
        phrase = set(alternatives[0].lower().split())
        if len(phrase) >= 2 and phrase == said:
            found.append(item)
    if not found:
        return None
    if len(found) == 1:
        return found[0]
    # Two cards can carry the same name, and one of them is usually about the name while the
    # other reaches it: the ear-infection card answers ear infections, and the swimmer's-ear
    # card lists the name among its ways of saying a wet ear after swimming. The card whose own
    # reply opens with its own name is the one that answers the name.
    def _names_itself(item):
        name = (item.key[0][0] if item.key else "")
        reply = (getattr(item, "reply", "") or "").lower()[:140]
        return 0 if isinstance(name, str) and name.lower() in reply else 1
    return min(found, key=_names_itself)


def _the_name_alone(named, entries, reject, allowed=None, understood=None, words=None,
                    use_context=False):
    """The card a line that is only the name of a thing gets, or None.

    `named` is that name's own card - the one whose own name the line spells out. The checks
    here are the ones a name has to pass before it is a name and not a sentence, and they are
    the reading's own: a state in the phrase ("gone numb"), a clause ending ("school closed"),
    a name that is one word, and a card from an area the line is not read as being about.
    """
    typed = [str(word).lower() for word in (words or ())]
    if not 2 <= len(typed) <= 4:
        return None
    if any(word in NOT_A_NAME_ALONE for word in typed):
        return None
    # "gone numb" and "feel numb" are about a body, said with the person dropped: a report, not
    # a name. A card keyed on the words of a report is a card about the words, not the thing.
    if any(word in A_STATE_IN_THE_PHRASE for word in typed):
        return None
    # A name ends in the thing. "school closed" ends in what the thing is doing, and a card that
    # lists that clause answers a question about the closed school, not about a thing named.
    if typed[-1] in A_STATE_AS_A_NAME_END:
        return None
    if named is None:
        return None
    # The name has to be the area the line is already read as being about: "nappy rash" is a
    # health line and its card is a health card, while "late again" is about nothing in
    # particular and its bare words are a remark, which small talk answers better than any
    # card. Only when the reading names a topic at all - no topic, no opinion, no pass.
    if not allowed:
        return None
    if understood is not None:
        allowed = _declared_for(allowed, understood)
    if getattr(named, "domain", None) not in allowed:
        return None
    said = set(typed)
    if len(said) != len(typed):
        return None
    return named


def _declared_for(allowed, understood):
    """The domains in `allowed` that declare one of the topics the line is about.

    `_topic_domains` keeps a domain that declares nothing, because for a search a domain with no
    opinion should not be ruled out. A card answering a bare name is a stronger claim than that,
    so the domain has to say the topic is its own.
    """
    from ..knowledge import by_topic
    judged = by_topic()
    topics = []
    if isinstance(understood, dict):
        found = understood.get("topics")
        topics = list(found) if isinstance(found, (list, tuple)) else []
        topics.append(understood.get("topic"))
    topics = [topic for topic in topics if isinstance(topic, str) and topic]
    if not topics:
        return set()
    return {name for name in allowed
            if any(topic in (judged.get(name) or ()) for topic in topics)}


def _defines(understood, forms, typed, entries, reject=None):
    """The best entry that defines the thing a definition line asks about, or None.

    Read only when every other reader gave up, so a line with an answer of its own is untouched.
    The entry has to name the thing in its key and in the first sentence of its reply, and its
    fences still hold: a "what is a wet room" line that also says the room smells is a damp
    question and keeps the damp row.
    """
    clean = understood.get("clean") if isinstance(understood, dict) else ""
    said = clean or (understood.get("text") if isinstance(understood, dict) else "") or ""
    thing = _the_thing_asked_about(said)
    if not thing:
        return None
    purpose = _asks_what_it_is_for(said)
    best = None
    best_rank = None
    for item in entries:
        if reject is not None and reject(item):
            continue
        # A guard is a test of the whole reading of the line, so it holds here too: "what is a
        # bridge" is a river crossing as often as a section of a song, and the entry that says
        # which sense it is about was being asked below anyway. A definition line names one
        # thing and asks nothing else, so it is the one reader with no second signal to lean on.
        if not guard_passes(item, understood):
            continue
        if not _the_key_names_the_thing(item, thing):
            continue
        if not _the_reply_defines(getattr(item, "reply", ""), thing, purpose):
            continue
        if any(_part_score(word, forms) for word in item.avoid):
            continue
        rank = -len(_key_forms(item))
        if best_rank is None or rank > best_rank:
            best, best_rank = item, rank
    return best


def _named_things(understood):
    """The names the line gives, which a question is about before it is about its ask words."""
    found = []
    entities = understood.get("entities") if isinstance(understood, dict) else None
    for entity in entities if isinstance(entities, list) else ():
        if not isinstance(entity, dict) or entity.get("type") not in ("place", "name", "title"):
            continue
        name = " ".join(str(entity.get("text") or "").lower().split())
        if len(name) > 2:
            found.append(name)
    return found


PLAN_WORDS = ("plan", "plans", "planning", "organise", "organize", "prepare", "preparing")


def _plans_it(item, forms):
    """True when the line asks to plan something and the entry's key is the planning word.

    "help me plan a trip to Paris" and "i want to plan a weekend in Amsterdam" name a place,
    but the question is the plan, not the place: the city guide names Paris or Amsterdam and
    would take the line on the named-thing tie-break. A key that itself says "plan" is the
    answer to a line that says plan, so it comes before the name.
    """
    if not any(_part_score(word, forms) for word in PLAN_WORDS):
        return False
    return any(word in _key_words(item) for word in PLAN_WORDS)


def _names_one(item, named):
    """True when the entry's own key names one of the things the line names."""
    for part in getattr(item, "key", ()) or ():
        for alternative in (part if isinstance(part, tuple) else (part,)):
            text = " ".join(str(alternative).lower().split())
            for name in named:
                if _bounded(str(name)).search(text):
                    return True
    return False


def _only_asking_about_it(understood, leans):
    """True when the line names nothing the line before it had not already named.

    Only the content words count: what the line adds of its own is the subject, and a line that
    adds none of its own is asking about the line before it. "what about a large one" adds
    "large", so it is not this - the earlier card answers it only when the two lines complete a
    key between them, as they do for a chicken.
    """
    earlier = set(tokens(str((leans or {}).get("clean") or (leans or {}).get("text") or "")))
    earlier.update(str(word).lower() for word in ((leans or {}).get("words") or ())
                   if isinstance(word, str))
    now = tokens(str(understood.get("clean") or understood.get("text") or ""))
    if not now:
        return False
    for word in now:
        if word in earlier or word in GRAMMAR_ONLY or word in POINTS_BACK:
            continue
        if word in FOLLOW_ON_WORDS or word.isdigit():
            continue
        return False
    return True


def names_nothing_of_its_own(understood):
    """True when the line asks about the subject of the line before it and adds no subject.

    "will it survive", "is that bad" and "what happens now" carry an ask and nothing else, so
    the only subject they can be about is the one the last answer was about. A line that adds a
    content word of its own ("what about a large one") is not this: the word it adds is what it
    is asking about.
    """
    leans = understood.get("leans_on")
    if not isinstance(leans, dict):
        return False
    return _only_asking_about_it(understood, leans)


# One reading of one line is scored once, however many times a turn asks about it. The answers
# module asks `find` for the line, then for the same line with one card family after another
# ruled out (`reject`), and each of those asked and answered every entry again: a fallback line
# on the whole 4,300-entry knowledge base walked it eight to thirty times, which was most of
# what a reply cost. What an entry scores depends on the line's words and on nothing else, so
# the answer is the same each time. The key is the reading itself, and the entries list is kept
# with it so a freed list's id cannot be reused for a different knowledge base.
_ROWS_CACHE = {}


_ROWS_KEEP = 40


# A word of the question half that more than this many entries key on is the vocabulary of
# everyday asking - "get" 949, "best" 587, "work" 566, "time" 523, "child" 211, "thing" 58 - and
# not the thing a person asked about. Below it the base treats the word as one name for one
# subject ("railcard" 4, "condensation" 10), and an entry that keys on it is answering what the
# line asked rather than what the line mentioned on the way there.
ASK_NAME_CAP = 40


# ... and the cap on the same reading of a question half that holds no rare word at all, where
# the ordinary words are all the ask has to go on. Higher, because the words it lets in are the
# ones a card keys on as its subject somewhere ("place", "live", "cost"), not the vocabulary of
# asking, which is left out below.
ASK_PLAIN_CAP = 400


def _the_names_in_the_ask(understood, every):
    """The words of the question half that the knowledge base treats as a name for something.

    People put the situation first and the question last: "i start a new job monday and the
    commute is an hour, should i get a railcard". The situation half is thick with subject words
    and the question half is thin, so the card for the commute (a house move, a season ticket)
    outscored the card for the railcard that was actually being decided. Nothing in the scan
    knew which half a matched word came from.

    `focus` is the question half, which the reading already hands over. Only the content words
    of it count, and only the ones a card keys on as a name: the ask's own words ("what",
    "should", "get") are the vocabulary of asking and every card in the base keys on some of
    them, so counting those would put the whole base on the ask.

    Only a line split into a situation and a question of its own is read this way (see
    `_two_clauses`); a line that states one thing and asks nothing keeps the reading it had.
    """
    split = _two_clauses(understood)
    if not split:
        return ()
    focus = split
    names = []
    for word in focus:
        if not isinstance(word, str):
            continue
        low = word.lower()
        if len(low) < 3 or low in _NOT_A_SUBJECT or low in ASK_FRAME_WORDS:
            continue
        if every.get(low, 0) > ASK_NAME_CAP or low in names:
            continue
        names.append(low)
    # A yes/no question about a situation is usually about that situation: "i left the chicken
    # out all night, can i still cook it" is a question about the chicken, and reading its ask
    # as the subject put a curry recipe in front of the row that says to bin it. So the ordinary
    # words of an ask are only read as its subject where the line asks what to do about it.
    plain = "yesno" not in (understood.get("asks") or ())
    if not names and plain:
        # A question half made only of common words is still the half that was asked. "how do i
        # find a place to live" has no rare noun in it, so the cap above left the ask with no
        # names at all and the row for the month in the situation - "i start a new job in
        # manchester in september" reached the garden-jobs row - won the line. With nothing else
        # to go on, the ordinary words of the ask are the ask: they are compared against a card
        # that answered the situation, and the ask's own words are left out above, so the whole
        # base cannot come in on "what" or "get".
        for word in focus:
            if not isinstance(word, str):
                continue
            low = word.lower()
            if len(low) < 3 or low in _NOT_A_SUBJECT or low in ASK_FRAME_WORDS:
                continue
            if every.get(low, 0) > ASK_PLAIN_CAP or low in names:
                continue
            names.append(low)
    return tuple(names)


def _the_ask_in_order(understood):
    """The words of the question half, in the order the person said them, or ().

    The names `_the_names_in_the_ask` hands back are single words, and a card that keys a phrase
    of two words is not reached by one of them alone: "how do i get more vitamin c" offered
    "vitamin" and the expired-medicines row, which keys on "vitamins", took the line off the row
    that keys on "vitamin c". Read as the words in order, the phrase a card keys on can be found
    for what it is (see `_the_longest_run`).
    """
    said = _two_clauses(understood)
    if not said:
        return ()
    return tuple(word for word in said if isinstance(word, str))


def _two_clauses(understood):
    """(the words of the question half, the loose forms said before it), or None.

    Only a line that puts the situation first and asks after it is read this way: the ask has to
    be there at all (`asks`), and it has to be a clause of its own, so that the words beside it
    are the situation and not the same sentence. A line that states one thing and asks nothing
    ("my nose wont stop running and i keep sneezing") has no question half to prefer, and reading
    its whole line as one put the training-injury card - which keys on "running" - in front of
    the runny nose.

    Compared as loose forms, so "stop" and "stopped" are the same word here. A word of the ask
    that the line says only earlier on means the reading is not split, and the rule stands down.
    """
    if not isinstance(understood, dict) or not understood.get("asks"):
        return None
    focus = understood.get("focus")
    clauses = [clause for clause in (understood.get("clauses") or ())
               if isinstance(clause, (list, tuple)) and clause != ["text"]]
    if not isinstance(focus, (list, tuple)) or not focus or len(clauses) < 2:
        return None
    last = {_forms(str(word)) for word in (clauses[-1] or ()) if isinstance(word, str)}
    earlier = {_forms(str(word)) for clause in clauses[:-1] for word in (clause or ())
               if isinstance(word, str)}
    # The situation has to be a clause somebody would write: "how long do i defrost a chicken
    # for" splits into "how long" and the rest, and the reading is one question, not a
    # situation and a question. Three words of situation is the least that says anything.
    longest = max((len([word for word in (clause or ()) if isinstance(word, str)])
                   for clause in clauses[:-1]), default=0)
    if not last or not earlier or longest < 4:
        return None
    for word in focus:
        if not isinstance(word, str):
            continue
        form = _forms(word)
        if form in last or form not in earlier:
            continue
        return None
    return tuple(word for word in focus if isinstance(word, str))


def _rows_key(forms, typed, named, frame, framed=False, asked=(), ask_said=()):
    """The reading of the line a scan answers, or None when it cannot be written down."""
    try:
        return (tuple(tuple(sorted(str(form) for form in group)) for group in forms),
                tuple(str(word) for word in typed or ()),
                tuple(str(one) for one in named or ()), bool(frame), bool(framed),
                tuple(str(word) for word in asked or ()),
                tuple(str(word) for word in ask_said or ()))
    except TypeError:  # a reading a test built by hand: no memo, just scan
        return None


def _line_rows(forms, typed, entries, by_domain, every, named=(), frame=True,
               stands_down=None, framed=False, ask_names=(), ask_said=()):
    """[(asked, rank, plans it, names the thing named, key parts, entry, on the ask)] reached.

    `stands_down` is a test of the whole reading, not of the entry's own key words, so the entry
    it passes over is left out of what this call returns and not out of what the line reaches:
    the scan is kept as it is and the rows are filtered on the way out.

    framed: the line is the subject inside an advice ask, which spends its other words on the
    asking (see `score`). It changes what an entry scores, so it is part of the memo key.

    ask_names: the names the question half holds (see `_the_names_in_the_ask`). They are a
    column of the row, so they are part of the memo key too.

    ask_said: the question half's words in the order they were said, which is how a card that
    keys a phrase of two of them is reached (see `_the_longest_run`). Also part of the key.
    """
    key = _rows_key(forms, typed, named, frame, framed, ask_names, ask_said)
    ranked_items = None
    if key is not None:
        got = _ROWS_CACHE.get((id(entries), key))
        if got is not None and got[0] is entries:
            ranked_items = got[1]
    if ranked_items is None:
        ranked_items = _scanned_rows(forms, typed, entries, by_domain, every, named, frame,
                                     framed, ask_names, ask_said)
        if key is not None:
            if len(_ROWS_CACHE) >= _ROWS_KEEP:
                _ROWS_CACHE.pop(next(iter(_ROWS_CACHE)))
            _ROWS_CACHE[(id(entries), key)] = (entries, ranked_items)
    if stands_down is None:
        return list(ranked_items)
    return [row for row in ranked_items if not stands_down(row[5])]


def _scanned_rows(forms, typed, entries, by_domain, every, named, frame, framed=False,
                  ask_names=(), ask_said=()):
    """Every entry the line reaches, scored: the work one reading of one line costs."""
    ranked_items = []
    ask_forms = [_forms(word) for word in ask_names]
    # The question half as the person said it, in order, so a card that keys a phrase of two
    # words can be reached by the phrase rather than by one of them (see `_the_longest_run`).
    ask_line = [_forms(word) for word in ask_said]
    # The memo is keyed by id(part), so it is only safe for parts that live on a module-level
    # entry: a part built inside a call could be freed and its id reused within the same line.
    seen = {}
    # A second memo for the question half alone, because a memo says what one part matched in one
    # reading of the line and `seen` is about the whole line.
    asked_seen = {}
    for item in _reaching(entries, forms):
        value = score(item, forms, typed, seen, frame, framed)
        if not value:
            continue
        domain = getattr(item, "domain", "") or ""
        ranked = _rank(item, forms, by_domain.get(domain) or every, seen)
        # an entry the line actually asked reaches ahead of one the want rule let in
        asked = 0 if _only_the_want(item, forms, seen) else 1
        # ...and one that answers the question half reaches ahead of one that answers the
        # situation half. A separate column on purpose: the score of the wrong card is usually
        # higher, because its half of the line is the wordy half, so a bonus inside the score
        # would have to be bigger than any score difference we can justify.
        run = _the_longest_run(item, ask_line, ask_forms, asked_seen)
        ranked_items.append((asked, ranked, _plans_it(item, forms),
                             _names_one(item, named), len(item.key), item, run))
    # The question half is about the card that accounts for the most of it. Crediting every card
    # that answers one of its words put the expired-medicines row - which keys on "vitamins" -
    # ahead of the row that keys on the phrase "vitamin c" for "how do i get more vitamin c",
    # because one loose word of the ask beat a card that answers two of them.
    longest = max((row[6] for row in ranked_items), default=0)
    if longest:
        ranked_items = [row[:6] + (1 if row[6] == longest else 0,) for row in ranked_items]
    return ranked_items


def _the_longest_run(item, ask_line, name_forms, asked_seen):
    """How many words of the question half one key part of this entry accounts for, or 0.

    A name of the question half has to be in what matched: the ask's own words ("what", "get",
    "should") are the vocabulary of asking and a card that keys one of them is not on the ask.
    Past that, the length of the run is the whole reading, because a card that keys a phrase of
    two words of the ask is more about it than one that keys a single word of it.

    The memo of matches is the caller's and holds no entry yet: `seen` in the scan is keyed by
    id(part) alone, so reusing it would hand back the matches found in the whole line, which is
    every part that reached the line at all.
    """
    wanted = set()
    for forms in name_forms:
        wanted |= forms
    best = 0
    for part in item.key or ():
        for weight, words, span in _part_matches(part, ask_line, asked_seen):
            if not weight or len(span) <= best:
                continue
            if not any(_forms(str(word)) & wanted for word in words):
                continue
            best = len(span)
    return best


def _row_order(row):
    """The order two entries compete in: asked, on the ask, score, plan, the named thing, parts."""
    return (row[0], row[6], row[1], row[2], row[3], row[4])


PLAIN_MARGIN = 3


def _plainer(plain, framed, margin=PLAIN_MARGIN):
    """True when the whole line reaches a clearly better entry than the line without its clause.

    A margin, not a straight comparison: reading the left-out thing as the subject beats the
    rest of the line by one rank point in plenty of lines where it is wrong ("how do i stop my
    baby crying without picking him up" reaches the skin-picking entry that way), and the entry
    that wins here has to win by more than that to be believed.
    """
    better = max(row[:2] for row in plain)
    other = max(row[:2] for row in framed)
    return better[0] > other[0] or better[1] >= other[1] + margin


def _the_subjects_own_row(forms, item, rows):
    """True when the whole line's fault row is the answer, not a card about a different question.

    The whole line beats the line with its "without" clause emptied by one rank point on plenty
    of lines where reading the clause as the subject is wrong, which is what the margin in
    `_plainer` is for. A clause that names a fault of the thing in hand is the question, so the
    whole line may win by that one point, but only where the rest of the line has no answer of
    its own. Two things have to hold.

    The row the whole line reaches is in the same domain as a row the rest of the line reaches:
    a clause that buys a row from another domain has changed the subject, not answered the line
    ("how do i say sorry without it sounding fake" is an apology, not a phishing warning).

    And the row the rest of the line reaches is a stand-in list rather than an answer: an entry
    whose key is what to use instead of something is not the how-to the person asked for, so the
    fault card beside it is better. "how do i fry eggs without them sticking" reached the egg
    swap ("one egg becomes 60g of yoghurt") and wanted the pan.

        how do i fry eggs without them sticking   -> egg swap (a stand-in list) / fix-sticking
        how do i cook salmon without it sticking  -> the salmon method: the answer, not a card
        how do i paint a door without it dripping -> the door how-to: not a ceiling stain card
        how do i iron a shirt without it shining  -> the shirt how-to, not the scorch card

    Measured on the deck's "without it" lines: the salmon, door, shirt and puppy lines keep the
    how-to they had, and the egg line gets the pan.
    """
    domain = getattr(item, "domain", None)
    if not domain or not _a_clause_about_the_thing(forms):
        return False
    if not any(getattr(row[5], "domain", None) == domain for row in rows):
        return False
    return _offers_a_substitute(max(rows, key=_row_order)[5])


def _offers_a_substitute(item):
    """True when this entry exists to say what can stand in for something else."""
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if isinstance(alternative, str) and set(alternative.lower().split()) & SUBSTITUTE_WORDS:
                return True
    return False


# The parts a line can name and an entry can be keyed on, as both are written: the entry keys
# use the singular and the plural of the same word, and a line may say either.
BODY_WORDS = lexicon.BODY_PARTS


# How many parts an entry's key can name and still be about one of them: "knee" and "kneecap"
# is the same joint twice, while a key listing the arm, the leg and the chest is a key for
# anywhere.
SPECIFIC_PARTS = 2


# A part that sits inside another is not a different part: new trainers rubbing the heel are
# still the entry about feet, so a keyed "foot" keeps the line that says "heel". The other
# way round is not the same thing - "my leg hurts" is not the knee - and nothing here makes the
# neck a back or the back a neck, which is what the guard is for.
PART_INSIDE = {
    "heel": "foot", "ankle": "leg", "knee": "leg", "hip": "leg",
    "thumb": "hand", "finger": "hand", "knuckle": "hand",
    "wrist": "hand", "elbow": "arm", "shoulder": "arm",
    "jaw": "head", "tooth": "head", "ear": "head", "eye": "head",
    "rib": "chest", "belly": "stomach",
}


def _inside(part, other):
    """True when this part is the other one, or a part of it."""
    seen = 0
    while part and seen < 4:
        if _forms(part) & _forms(other):
            return True
        part = PART_INSIDE.get(part, "")
        seen += 1
    return False


def _a_cut_of_meat(words, index):
    """True when the body word at `index` sits beside a cut of meat, so it names the cut."""
    near = [str(words[at]).lower() for at in (index - 2, index - 1, index + 1, index + 2)
            if 0 <= at < len(words)]
    return any(word in _CUT_BESIDE for word in near)


def _body_parts(words):
    """The body parts the line names, without a "back" that only says the thing returned."""
    parts = set()
    for index, word in enumerate(words or ()):
        word = str(word).lower()
        if word not in BODY_WORDS:
            continue
        if word == "back" and index and str(words[index - 1]).lower() in RETURNED_AFTER:
            continue
        if word in GENERAL_BODY:
            continue
        if _a_cut_of_meat(words, index):
            continue
        parts.add(word)
    return parts


def _key_body_parts(item):
    """The body parts this entry's key is written on.

    Read with the same eye as the line: a key that says "keeps coming back" names no part, and
    the entry that answers a rash which returns is still the answer to ``the rash on my knee
    keeps coming back``.
    """
    parts = set()
    for part in getattr(item, "key", ()) or ():
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if isinstance(alternative, str):
                parts |= _body_parts(alternative.lower().split())
    return parts


def _a_part_the_line_does_not_have(word, parts_said):
    """Whether this fence word names a body part the line says as something other than a part.

    Only a single word that is a part can: a fence written on a phrase ("a mole on my back", "bad
    back") says what it means, and is left alone. The word is only asked here after it was found
    in the line, so it is in the line - the question is whether it is the part.
    """
    key = str(word).strip().lower() if isinstance(word, str) else ""
    if not key or " " in key or key not in BODY_WORDS:
        return False
    return key not in (parts_said or ())


def _another_part(item, line_parts):
    """True when the entry is keyed on a body part the line does not have.

    A line that names one part is about that part: an entry keyed on a different one answers a
    question nobody asked, however well its other words fit ("pain" is in most of them). Only
    entries whose key names a part are held to it, so a row about a return ("keeps coming
    back") or a place is untouched, and a line that names no part at all is untouched too - the
    filter narrows what a body word may reach, and never widens it.

    A key that names many parts is not about one of them: `rash` lists the arm, the leg, the
    chest and the back because a rash can be on any of them, and holding it to those words took
    "the rash on my knee keeps coming back" off its own answer. Only a key written on one part,
    or a part and its other name (`sore-knee` is "knee" and "kneecap"), says what the entry is
    about. The words are compared by their loose forms, because the line says "my knees ache"
    and the key says "knee".
    """
    if not line_parts:
        return False
    parts = _key_body_parts(item)
    if not parts or len(parts) > SPECIFIC_PARTS:
        return False
    said = list(line_parts)
    # the line's part may be a part of the entry's: a heel is a foot, a thumb is a hand
    return not any(_inside(other, part) for part in parts for other in said)


_KEEPING_ANSWER = (
    " keeps ", " keep it ", " keep them ", " keeping it ", " in the fridge", " in the freezer",
    " in a sealed", " in an airtight", "bin it", "bin them", "throw it", "throw them",
    "no more than", "shelf life", "hours", "days in the", "a day in the", "day in the fridge",
    "within a day", "within the hour", "goes off", "gone off", "until the date", "use-by",
    "use by", "best before", "cold box", "cool it", "cool it fast")


def _asks_if_it_is_still_good(typed):
    """True when the line asks whether a thing is still fit to eat, drink or use."""
    if not typed:
        return False
    return bool(_STILL_GOOD_ASHERS.intersection(str(word).lower() for word in typed))


def _a_keeping_row(item):
    """True when the entry answers how long a thing keeps, where to keep it, or if it is fit."""
    reply = getattr(item, "reply", "") or ""
    if not isinstance(reply, str):
        # a reply built at the turn ("a bowl of X is ...") says what it says in `key`, and the
        # rows that keep are the ones keyed on a keeping word.
        return _a_keeping_key(item)
    if not reply:
        return False
    reply = " " + " ".join(reply.lower().split()) + " "
    return any(phrase in reply for phrase in _KEEPING_ANSWER) or bool(
        _A_KEEP_AND_A_LENGTH.search(reply))


def _a_keeping_key(item):
    """The key-word test, used only for a row whose reply is built at the turn."""
    words = set()

    def collect(part):
        if isinstance(part, str):
            words.update(part.lower().split())
        elif isinstance(part, (tuple, list, frozenset, set)):
            for inner in part:
                collect(inner)

    collect(getattr(item, "key", ()) or ())
    return bool(_KEEPING_WORDS.intersection(words))


# A colour used as a colour is one a copula or a verb of changing puts in front of you: "the sky
# was orange", "the leaves have gone brown", "it turned green". In front of a noun the colour is
# part of that thing's name and the thing is what the line is about - "green beans for dinner" is
# the beans, "orange juice" is the juice - so only this shape is read as a colour word.
A_COLOUR_USED = re.compile(
    r"\b(?:is|are|was|were|am|be|been|being|looks?|looked|seems?|seemed|got|gets|getting|goes|"
    r"going|went|gone|turn(?:s|ed|ing)?|becom(?:e|es|ing)|became|keep|keeps|kept|painted|paint|"
    r"dyed|dye|stained?)\s+(?:very\s+|really\s+|so\s+|too\s+|quite\s+|a bit\s+|a little\s+|"
    r"all\s+|still\s+|now\s+)?(?P<colour>[a-z]+)\b", re.IGNORECASE)


# A colour of something worn is the question "what should I wear to it". Every occasion row in
# the clothes domain is keyed on the wearing words (wear, outfit, clothes, put on) and on the
# occasion, because that is how the question is usually put: "what do i wear to a wedding". A
# person who names the colour instead has still asked the same thing - "is white ok for a
# wedding", "is black ok at a christening" - and without these words the wedding row lost to the
# hotel-booking row on the word "wedding", the christening row scored nothing at all and the turn
# got a shrug, and "should i wear white to a wedding" reached the rice row on "white". Three
# things are needed, and the third is what keeps it honest: a colour, a wearing word or an
# occasion people dress for, and a line that ASKS. Clothes are bought, worn and reported, so a
# colour a person mentions is usually not a question about clothes at all: "i bought a black
# dress for my mums funeral" is a loss, "she was buried in a green dress" is news, and read as an
# ask both of them got dressing instructions instead of the condolence they were owed.
#
# The ask is read the way people put it, and from the whole line rather than one word: the engine
# already says whether a line is a question, and on top of that an opener that asks, a judgement
# word the colour is being held up to (ok, alright, suitable, appropriate, "is it rude", "too
# much"), a colour offered against another ("white or navy for an interview"), or a question mark
# makes a colour the subject. A colour that is only reported has none of those.
ASKING_FIRST = frozenset("""is are am was can could should would will shall may might do does did
    what which any anything how""".split())
