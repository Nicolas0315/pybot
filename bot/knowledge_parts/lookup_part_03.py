"""Part 3 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
import re
from .lookup_part_01 import (
    lexicon, said, ENDINGS, COMMON_WORDS, TIME_WORDS, PEOPLE_FEMALE, PEOPLE_MALE,
)
from .lookup_part_02 import (
    _FORMS_CACHE, _FORMS_CACHE_KEEP, IRREGULAR_PLURALS, NOT_A_BASE, NOT_A_WORD_WITH_AN_S,
    NOT_THE_DOUBLED_STEM, NOT_THE_STEM, NOT_THE_STEM_WITH_E, _CONTRACTION, _CURLY, _add, _cvc,
    _doubles_for_an_ending, _FUNCTION_WORDS, COOKING_AS_A_NAME, _MARKS,
)


def _forms(word):
    """The loose forms of a word, so eggs/egg and cooking/cook match each other.

    Two rules keep a loose form honest. A stem has to keep at least MIN_FORM letters to count
    (short stems are not words of their own: "weeing" strips to "we", and that one form made
    the cat litter entry answer "we had to put our cat down"). And a form is only handed out
    when the strip is a real ending of the word and the leftover is not a different word of its
    own: "bites" is not "bit", "cares" is not "car", "biting" is not "bit". Those reached a key
    word that has nothing to do with the line ("bit of a mad day" was answered as the
    sibling-hitting entry), and the person's real word still matches its own key, which lists
    the spelling it answers.

    The result comes from a cache and is a frozenset. The matcher asks for the same key word
    thousands of times a turn (once per entry that says it), and the forms of a word depend on
    nothing but the word, so working them out again was most of what a reply cost. A frozenset
    is returned because `find` writes the typo forms onto a line word with `|=`; on a cached set
    that would edit the copy for the rest of the conversation, on a frozenset the same line makes
    a new set.
    """
    got = _FORMS_CACHE.get(word)
    if got is not None:
        return got
    forms = _work_out_forms(word)
    frozen = frozenset(forms)
    if len(_FORMS_CACHE) >= _FORMS_CACHE_KEEP:
        _FORMS_CACHE.clear()     # a card of words, not a leak; the next turn fills it again
    _FORMS_CACHE[word] = frozen
    return frozen


def _work_out_forms(word):
    """The forms of one word, worked out from the endings and the tables (see _forms)."""
    # The understanding layer supplies the words, so the curly-apostrophe repair has to
    # happen here too, not only in tokens().
    word = word.translate(_CURLY)
    forms = {word}
    # The same word in the other spelling: "why does my bread go moldy so fast" reads as
    # "mouldy" (bot/understanding/lexicon.py, US_SPELLINGS) but the matcher had only the word
    # the person typed, so the entry keyed on "mouldy" never met the line and a mouldy loaf was
    # answered with a cooking-time entry - "Eggs are the fastest dinner there is". Nothing was
    # misspelt, so both spellings are the same word here and the reply still says the one they
    # used.
    other = lexicon.US_SPELLINGS.get(word)
    if other:
        forms.add(other)
    # A city and cities, a curry and curries: the plural is not an "s" on the end, so the
    # key word "city" never met "the best cities to visit" before. Only from six letters up:
    # "flies" would hand "fly" to the fruit flies, and "flying east" is jet lag, not a gnat.
    if word.endswith("ies") and len(word) > 5:
        forms.add(word[:-3] + "y")
    if word.endswith("y") and len(word) > 3 and word[-2] not in "aeiou":
        forms.add(word[:-1] + "ies")
    if word in IRREGULAR_PLURALS:
        # Only the real singular. The key word itself still matches a line that says it.
        forms.add(IRREGULAR_PLURALS[word])
        return forms
    # A possessive is the same thing: "my sister's birthday" is about a sister. Without this a
    # key only ever matched the plain form, so every possessive line fell through.
    # "-'s" after a pronoun or wh-word is a contraction ("what's", "it's", "there's"), not a
    # possessive: stripping it turned "What's one you'd love to see?" into the word "what", which
    # is in a few keys, and it answered a bird-feeding line in a conversation about herons.
    if word.endswith("'s") and len(word) > 3 and word not in _CONTRACTION:
        forms.add(word[:-2])
    elif word.endswith("s'") and len(word) > 3:
        # "the sisters' kitchen": the plural possessive is the plural.
        forms.add(word[:-2])
        forms.add(word[:-1])
    if len(word) > 3:
        if word.endswith("s") and not word.endswith("ss") and word not in NOT_A_WORD_WITH_AN_S:
            _add(forms, word[:-1])
        # "-es" is only a plural ending after a sibilant or an o: boxes, wishes, tomatoes. After
        # anything else the "e" belongs to the stem, and stripping both letters invents a word
        # nobody wrote: "bites" -> "bit", "notes" -> "not", "cares" -> "car", "stares" -> "star".
        # An "i" before the "-es" is the same plural: chillies, curries, berries, cookies,
        # countries. Every one of them lost its singular when the sibilant rule came in, and a
        # key on "chilli" stopped answering "the chillies are too hot". The invented forms the
        # rule exists to keep out (bites, notes, cares, stares) have a consonant there.
        if (word.endswith("es") and len(word) > 4
                and (word[-3] in "sxzi" or word[-4:-2] in ("ch", "sh") or word[-3] == "o")):
            _add(forms, word[:-2])
        if word.endswith("ed") and len(word) > 4:
            # "hated" is "hate" and a "d", not "hat", but dropping both letters handed a real word
            # to the entry all the same: a line asking "how do i knit a hat" met the two rows about
            # hating a job and was answered "Do the boring things first and most strict teachers
            # stop being a problem", "cared" handed "car" to a line about looking after a parent
            # and "moped" handed "mop". Only where the two letters less are a word of their own
            # does the e go back, and only for a word that is one: "replaced" keeps its old stem,
            # because "replac" is nothing and adding "replace" to the rows about a replaced knee
            # is what answered "how do i replace a shower head" with the washing-a-new-joint card.
            if _engine_reads(word[:-2]) and _engine_reads(word[:-1]):
                _add(forms, word[:-1])
            else:
                _add(forms, word[:-2])
            # Only a doubled consonant loses three letters: "stopped" -> "stop". Without this
            # guard "forced" also yields "for" and "started" yields "star", so a key would
            # match an ordinary word that has nothing to do with it.
            if len(word) > 5 and _doubles_for_an_ending(word[:-2]):
                _add(forms, word[:-3])
        if word.endswith("ing") and len(word) > 5:
            stem = word[:-3]
            # The stem with an "e" is a word too, and for most of these it is the one the word
            # was built from ("teething" is "teethe", "clothing" is "clothe"): that form stays.
            # "Housing" is the exception - "house" is not what it was built from, it is a
            # different noun that happens to end the same way, and a line about a house reached
            # the housing card through it.
            if word not in NOT_THE_STEM_WITH_E:
                _add(forms, stem + "e")
            # The same trap as above: "biting" is "bite", not "bit", and "caring" is "care",
            # not "car". A verb whose base really has that short shape doubles its consonant
            # before "-ing" ("stopping"), and that doubled stem is stripped below, so nothing is
            # lost by keeping the bare stem out of it.
            # A stem that ends in "y" never doubles it before "-ing" ("staying", "praying"),
            # so the bare stem is always the word: "stay" is not a short closed syllable with
            # a consonant stuck on the end, it is the word itself. Without this, `staying`
            # reached only `stay e`, and `saying`, `praying`, `worrying` lost their own word.
            if (word not in NOT_THE_STEM and stem not in NOT_A_BASE
                    and (not _cvc(stem) or (len(stem) > 2 and stem.endswith("y"))
                         or _bare_is_the_word(stem))):
                _add(forms, stem)
            # "stopping" -> "stop" and "running" -> "run", but a doubled "s" is the word's
            # own: dropping a letter from "hiss" invented "his", and any key that said hissing
            # then matched every line with "his", which is how "my dad is tired of his job"
            # reached the puncture instructions.
            if _doubles_for_an_ending(stem) and word not in NOT_THE_DOUBLED_STEM:
                _add(forms, stem[:-1])
    return forms


def _bare_is_the_word(stem):
    """Whether a short consonant-vowel-consonant stem may stand for the word that was written.

    "opening" -> "open" yes: the stem is a word the understanding engine reads and adding an
    "e" to it makes a word nobody writes. "biting" -> "bit" no: both are words, and the person
    meant "bite". "hating" -> "hat" no, for the same reason. A function word is never the base
    of a longer word. When the engine cannot read the stem at all ("stares" -> "star") it is not
    a base either, because nobody wrote it. The cost is that a word the engine does not know
    loses that one reading; the entry that answers it lists the spelling, as a key always can.
    """
    return (_engine_reads(stem) and not _engine_reads(stem + "e")
            and stem not in _FUNCTION_WORDS)


def _without_a_cooking_that_is_a_name(words):
    """The line's words with a "cooking" that names a food taken out.

    "Cooking oil" is the name of what is in the bottle, not a statement that something was
    cooked. Read as the verb it made a shelf-life question into a cooked-food one: the
    cooked-food table in bot/knowledge/cooking.py keys on "cook" and on a keeping word, so
    "how do i store cooking oil" matched it twice and the oil's own keeping row lost the line,
    while "how do i store olive oil" reached the right answer. The participle that says a food
    was cooked is "cooked", which is not a word anyone wears in a name.
    """
    kept = []
    for index, word in enumerate(words):
        following = words[index + 1] if index + 1 < len(words) else ""
        if (str(word).lower() == "cooking"
                and str(following).lower().strip(_MARKS) in COOKING_AS_A_NAME):
            continue
        kept.append(word)
    return kept


# A child named by their place in the family names no son or daughter. "my youngest is up at
# five every morning" says which child it is, and every entry that keys on a child word (early
# waking, teething, a temperature, being sick, two children rowing) passed the line over: the
# everyday word for a child does the same. "my lad has a temperature" was answered "I'm
# listening" while "my son has a temperature" got the 111 line, and "my lad wont sleep" got a
# nagging line where "my son wont sleep" got the sleep answer. Both are read the same way, in
# the same place, so every entry that keys on a child reads them without naming them: the
# person's problem was written down and not answered, and the follow-up after it had nothing to
# read from. The word the entries key on is added to the line's own words instead, so all of
# them read it the same way, and only where the place word is the subject of the line.
CHILD_BY_PLACE = re.compile(
    r"\b(?:my|our|the|his|her|their)\s+(?:youngest|eldest|oldest|little\s+one|middle\s+one|"
    r"lad|lass|kiddo|laddie|un)\b"
    # A size word between the possessive and the child does not stop it being the child, and
    # "my little lad wont sleep" was answered "Right. What have you tried so far?" where "my lad
    # wont sleep" got the sleep card: the phrase above wanted the two words side by side. The
    # size word is also what makes the plain words for a child safe to read - "my little boy" and
    # "my little man" are a child, while "my boy" on its own can be a grown man or a partner, so
    # those are left alone.
    r"|\b(?:my|our|the|his|her|their)\s+(?:little|small|wee|big|older|elder|younger|poor)\s+"
    r"(?:youngest|eldest|oldest|one|lad|lass|kiddo|laddie|un|boy|girl|man)\b",
    re.I)


# The words the phrase above is made of, which become the child word.
CHILD_PLACE_WORDS = frozenset(("youngest", "eldest", "oldest", "little", "middle"))


# The size word in "my little lad" is not the child, so it is dropped rather than read as one:
# "my child child wont sleep" still matches, but the line reads cleaner as "my child wont sleep".
CHILD_SIZE_WORDS = frozenset(("little", "small", "wee", "big", "older", "elder", "younger",
                              "poor"))


# A plain word for a child, which is only a child after a size word: "my little boy" and "my wee
# girl" are children, and "my boy" or "my girl" on their own may be a partner, so they stay out of
# EVERYDAY_CHILD.
CHILD_AFTER_A_SIZE = frozenset(("boy", "girl", "un", "man"))


# The everyday word for a child, which is the same child: "my lad has a temperature" was answered
# "I'm listening" while "my son has a temperature" got the 111 line, and "my lad wont sleep" got a
# nagging line where "my son wont sleep" got the sleep answer.
EVERYDAY_CHILD = frozenset(("lad", "lass", "kiddo", "laddie"))


# A size word makes a plain word for a child ("my little girl") safe to read, and it says nothing
# about how old the child is: a parent writes "my little girl is 12" about a twelve-year-old, and
# she was walked back to bed like a two-year-old. Eleven is where the toddler rows stop being the
# answer, and the words for a secondary school child say the same thing without a number.
# The phrase as it was before the size word was allowed: the possessive and the word for the
# child side by side. "my lad is 14" was always read as a child and then left alone by A_TEEN,
# and that path is unchanged; the size word is the new one, and it is what stands down here.
A_CHILD_WORD_BY_ITSELF = re.compile(
    r"\b(?:my|our|the|his|her|their)\s+(?:youngest|eldest|oldest|little\s+one|middle\s+one|"
    r"lad|lass|kiddo|laddie)\b", re.I)


A_CHILD_GETTING_OLDER = re.compile(
    r"\b(?:teenager|teenagers|teen|teens|teenage|teenaged|secondary\s+school|high\s?school|"
    r"senior\s+school|year\s+(?:7|8|9|10|11))\b"
    # "is 11 months" and "is 18 months" are babies, and the number alone cannot tell them apart
    # from a child of eleven, so a count in months or weeks is not an age in years.
    r"|\b(?:is|are|aged?|turned|turns|turning|now|nearly|just)\s+"
    r"(?:1[1-9]|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)\b"
    r"(?!\s*(?:months?|mths?|weeks?|mos?)\b)"
    r"|\b(?:1[1-9]|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)"
    r"\s*(?:year|yr)s?\s*old\b", re.I)


# ...unless the line names a teenager, who is not the small child these rows are for: "my lad is
# 14 and he wont get out of bed in the morning" keeps the answer "my son is 14 ..." gets, and the
# age is written without "year old" as often as with it.
A_TEEN = re.compile(
    r"\b(?:teenager|teenagers|teen|teens|teenage|teenaged)\b"
    # the age as written and as the reading spells it: "my lad is 14" reaches here as "fourteen"
    r"|\b(?:is|are|aged?|turned|turns|turning|now)\s+"
    r"(?:1[3-9]|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)\b"
    r"(?!\s*(?:week|weeks|month|months|day|days|hour|hours|stone|stones|kilos?|kg|lbs?|pounds?))",
    re.I)


# ...unless the line names what is being counted, which is the other half of every "the little
# one": "the little one of the two dogs" is a dog, and "the youngest" in a line about a husband
# is not a child either. The word is only added when nothing here says otherwise.
NOT_A_CHILD_SAID = frozenset("""dog dogs puppy puppies cat cats kitten kittens rabbit rabbits
    hamster hamsters guinea bird birds parrot parrots fish horse horses pony ponies ferret
    pet pets husband wife partner boyfriend girlfriend fiance fiancee friend friends mate mates
    boss colleague colleagues flatmate flatmates housemate housemates neighbour neighbours
    tenant tenants mum mother dad father nan nanna gran granny grandad grandpa sister brother
    aunt uncle cousin nephew niece""".split())


# "Me and my lad want to grow some veg this year" is the person and their child doing something
# together, not a question about the child. Read as a child line it reached the entry for a
# child's growth ("a child who is losing weight or not growing") and lost the grow-your-own
# answer it used to get, so a line that puts the person first names no child by itself.
# "and" is typed "n" as often as it is typed at all ("me n my little lad"), and the size word is
# what put this line inside the phrase above: "me n my little lad want to grow some veg" lost the
# grow-your-own answer to the growth card. The joiner is the whole of the test, so every way of
# typing it belongs here.
TWO_OF_US = re.compile(r"\A\s*(?:me|i|us)\s*[,&]?\s*(?:and|an|nd|n)\s+(?:my|our|mine)\b", re.I)


def _with_the_animal_in_hand(words, understood):
    """The line's words with the animal it only points at, named where the pronoun stands.

    A follow-up after a turn about a pet is about that pet: "she's been drinking a lot more
    water", "how much should he eat", "hes getting slow on walks". Nothing in those lines says
    which animal, so every entry keyed on a cat or a dog missed them and the answer for a person's
    own body took the turn - the daily figure for drinking water went to a cat, and a dog with a
    sore ear got the ear card for a person. The understanding engine has already worked out what
    the pronoun points at (`animal_in_hand`), so the animal goes where the pronoun stands: an
    entry that matches spans of positions still reads the line as it was typed.
    """
    animal = (understood or {}).get("animal_in_hand") or ""
    if not animal:
        return words
    kept = []
    for piece in words:
        low = str(piece).lower().strip(_MARKS).split("'")[0]
        kept.append(animal if low in _THE_PRONOUNS else piece)
    return kept if kept != list(words) else words


# The pronouns a follow-up points back at an animal with, as typed and without the apostrophe.
_THE_PRONOUNS = frozenset("""it its itself he him his himself hes hed she her hers herself shes
    shed they them their theirs theyre theyd this these those""".split())


def _the_animal_rules_out_that_card(item, understood):
    """True when the animal the line only points at is a word the card that took the turn avoids.

    A card carries in its avoid list the words that make it the wrong answer - the figure for a
    person's water says "cat", "dog", "puppy", "litter tray" - so a card whose avoid list holds
    the animal is a card written for somebody else and reached only because the line says "she"
    rather than "the cat".
    """
    animal = (understood or {}).get("animal_in_hand") or ""
    if not animal:
        return False
    stood_down_for = {str(word).lower() for word in getattr(item, "avoid", ()) or ()}
    return animal in stood_down_for or animal + "s" in stood_down_for


def _with_the_child_by_place(words, clean):
    """The line's words with the child it names by place or by an everyday word, when it does.

    The added word goes at the end: an entry has already matched spans of positions into this
    list (see `_frame_masked`), so nothing may move. A line that names an animal or a grown-up
    is left exactly as it came, which is also what keeps "the little one" about a dog the dog's
    question.
    """
    line = str(clean or "")
    if not CHILD_BY_PLACE.search(line) or TWO_OF_US.match(line):
        return words
    small = not A_TEEN.search(line)
    said = {str(word).lower().strip(_MARKS) for word in words}
    if said & NOT_A_CHILD_SAID:
        return words
    # The place word becomes the child word where it stands, so the line reads exactly as it
    # would had they said "my child": "my youngest has a temperature" is answered by the entry
    # "my child has a temperature" is answered by, rather than by whichever entry a spare word
    # at the end happens to favour.
    kept = []
    skipping = 0
    # The size word is what reads a plain word for a child ("my little girl"), and it says nothing
    # about how old that child is: "my little girl is 12 and wont go to bed" was a two-year-old's
    # bedtime handed to a twelve-year-old, and "my little lad is 14 and he wont get out of bed"
    # lost the answer main had. Where the size word is the only reason the phrase matched, an
    # older child stands the reading down and keeps the line it had.
    if A_CHILD_GETTING_OLDER.search(line) and not A_CHILD_WORD_BY_ITSELF.search(line):
        return words
    for at, word in enumerate(words):
        low = str(word).lower().strip(_MARKS)
        if skipping and (low == "one" or not low):
            skipping = 0
            continue
        skipping = 0
        child_word = low in CHILD_PLACE_WORDS or (small and low in EVERYDAY_CHILD)
        if low in CHILD_SIZE_WORDS:
            # "my little lad" is "my lad": the size word goes and the word after it is read as
            # the child. That word goes too when the line names a teenager, so "my little boy is
            # 14 and wont get up" stays the teenager's line instead of becoming a toddler's.
            after = next((str(word2).lower().strip(_MARKS) for word2 in words[at + 1:]
                          if str(word2).lower().strip(_MARKS)), "")
            if after in CHILD_PLACE_WORDS or after in CHILD_AFTER_A_SIZE or (
                    small and after in EVERYDAY_CHILD):
                continue
        if child_word or (small and low in CHILD_AFTER_A_SIZE
                          and at and str(words[at - 1]).lower().strip(_MARKS)
                          in CHILD_SIZE_WORDS):
            kept.append("child")
            skipping = 1 if low in ("little", "middle") else 0
            continue
        kept.append(word)
    return kept


def _one_edit(shorter, longer):
    """True when the two words are one slip apart: a letter wrong, missing, extra, or two
    neighbours swapped."""
    if shorter == longer:
        return True
    if abs(len(shorter) - len(longer)) > 1:
        return False
    if len(shorter) > len(longer):
        shorter, longer = longer, shorter
    i = 0
    while i < len(shorter) and shorter[i] == longer[i]:
        i += 1
    if len(shorter) < len(longer):
        return shorter[i:] == longer[i + 1:]        # one letter missing or extra
    rest, tail = shorter[i:], longer[i:]
    if rest[1:] == tail[1:]:
        return True                                 # one letter wrong
    return (len(rest) > 1 and rest[0] == tail[1] and rest[1] == tail[0]
            and rest[2:] == tail[2:])               # two neighbours swapped ("rubbrey")


def _stem(word):
    """The word a form belongs to, so radiator/radiators and tomato/tomatoes are one."""
    for ending in ENDINGS:
        if word.endswith(ending) and len(word) - len(ending) >= 3:
            return word[: -len(ending)]
    return word


_COMMON = frozenset(lexicon.COMMON.split()) | frozenset(lexicon.CORE.split())


# ... and the word each of them comes from, so "charging" counts as read when "charger" does.
_STEMS = frozenset(_stem(word) for word in _COMMON) | _COMMON


def _engine_reads(word):
    """True when the understanding engine already reads this word, as English or chat-speak.

    Such a word is not a typo, however close a key word looks: "park" is one letter from
    "pack", and it stays "park". The normaliser's own tables count too, so a chat form
    ("whats") is left to it. The word's family counts as well: "charging" is a form of an
    English word the engine knows a relative of ("charger"), so it is a word, not a slip
    from "changing", and a phone charging overnight stays out of the leaves fact.

    `lexicon.every_word()` is the rest of the reading's own vocabulary - the personal names, the
    topic and kind words, the parts of the body - gathered from those tables instead of listed
    again. The list this replaces was rebuilt one word at a time: "kate" was read as "kale",
    "preston" as "presto", "unfit" as "unit", "hiya" as "hoya", each found on the deck after it
    had already answered a line. A name bent into a key word is worse than a shrug, because the
    answer is confident and about another question: "enid", "elsie" and "esther" were read as
    "end", "else" and "either" ("my friend enid" got the after-a-breakup card), and "fella" and
    "bloke" as "fell" and "broke", so a line about who takes the credit at work was answered by
    the falls card for an elderly parent.

    A colour is a word too, and the engine's own tables do not carry them: "white" is one letter
    from "write", "grey" from "grow", "navy" from "naval", so wherever a row stays away from
    the nearer word the colour stood the row down - "is white ok at a christening" scored nothing
    at all because the christening card's own `avoid` holds "write", and a colour asked about a
    service with a clothes answer got a shrug.
    """
    return (word in _COMMON or word in COMMON_WORDS or word in lexicon.CHAT
            or word in lexicon.EXPAND or _stem(word) in _STEMS
            or word in lexicon.every_word() or word in COLOUR_WORDS)


# A few set phrases are plural and only plural: "the runs" is the stomach, and its singular is a
# different word altogether - "my knees have been sore since the run" is about going for one.
# `_forms` hands "runs" the singular "run" the way it hands "boxes" the singular "box", so the
# diarrhoea row answered that line with "drink water with a little salt and sugar in it". A
# phrase in here keeps every word it is written with and nothing else.
PLURAL_ONLY_PHRASES = frozenset(("the runs", "the trots"))


_WANTED_CACHE = {}


# The small words a key phrase uses to name a thing and a person does not have to type: "cold at
# the top", "look after the battery", "past the date", "park at the airport". Leaving one out
# does not say a different thing, but a key phrase has to be found whole, so the same line without
# it reached nothing at all: "radiator cold at top" got the thermostat card instead of the bleed
# answer, "past date yoghurt" and "park at airport cheaply" got a greeting, and "my phone wont
# detect sim" got a shrug while "... the sim" got the fix. Only a whole word is dropped, only from
# a phrase of two words or more, and at least two words have to be left, so no key is loosened to
# a single word or brought nearer to another phrase than it was.
_ARTICLE_WORDS = frozenset("""the a an""".split())


_ARTICLE_FORMS = frozenset().union(*(_forms(word) for word in _ARTICLE_WORDS))


_WHERE = object()


_LINE_FORMS = object()


_PHRASE_SPANS = object()


_WANTING = object()


_ASK_ABOUT_SOMEONE = object()


# The breathers people put in the middle of a phrase: "my phone just died", "the battery has
# finally gone", "the car nearly died on me". An avoid phrase is the pair of words that says what
# the line is about ("phone died"), and a word between them does not make it a different line -
# so the death-and-bills row stood down for "my phone died" and answered "my phone just died"
# with its bereavement team, which is the coldest reply in this file.
#
# Only an avoid list reads across a breather. A key phrase is the thing the row answers, and
# loosening a key would let a row answer a line it does not fit.
# "much" is gone from this list on purpose. It was read as a breather, so a fence of "how to"
# matched "how much to install a wood burner" and "how much to get a room decorated": the span
# allowed the "much" between the two words, and every price row that disowns "how to" (the fence
# that keeps a DIY answer off a price) then disowned the price question too. The person asking
# what a job costs got the method, a shopping list or a shrug. "how much" asks what it costs or
# how of it there is; it is not a softer "how", and the quantity is what the line is about. So a
# measure word is not a breather: the pair has to be about the same thing it always was.
_SAID_BETWEEN = frozenset("""
    just only nearly almost practically finally already still again now then even really
    actually suddenly completely totally literally basically quite very so too
    has have had is was were been being keeps kept
""".split())


# A contraction and the two words it stands for are the same words in a phrase: the
# understanding layer expands the spelling without the apostrophe ("wont" -> "will not",
# lexicon.py EXPAND), so a row keyed on "won't sleep" or "won't start" never met a line that
# wrote it out. "my 4 month old wont sleep in the cot" got the night-waking card and
# "my 4 month old will not sleep in the cot" got a bare "Noted: your 4 month old will not sleep
# in the cot"; the same for going to school, the boiler and a child who will not eat. The
# match is made here, once, rather than by listing both spellings in every key.
_ONE_SPELLING = (("won't", "will not"), ("wont", "will not"),
                 ("can't", "cannot"), ("cant", "cannot"),
                 ("shan't", "shall not"), ("dont", "do not"), ("don't", "do not"),
                 ("doesnt", "does not"), ("doesn't", "does not"),
                 ("isnt", "is not"), ("isn't", "is not"),
                 ("arent", "are not"), ("aren't", "are not"),
                 ("wasnt", "was not"), ("wasn't", "was not"),
                 ("werent", "were not"), ("weren't", "were not"),
                 ("didnt", "did not"), ("didn't", "did not"),
                 ("hasnt", "has not"), ("hasn't", "has not"),
                 ("havent", "have not"), ("haven't", "have not"),
                 ("couldnt", "could not"), ("couldn't", "could not"),
                 ("wouldnt", "would not"), ("wouldn't", "would not"),
                 ("shouldnt", "should not"), ("shouldn't", "should not"))


_ONE_SPELLING_EITHER_WAY = {}


for _short, _long in _ONE_SPELLING:
    _ONE_SPELLING_EITHER_WAY.setdefault(_short, set()).add(_long)
    _ONE_SPELLING_EITHER_WAY.setdefault(_long, set()).add(_short)


# The words of the want phrases that carry no subject: a key that matched one of these has not
# matched the thing the line is about, so the want cannot stand in for the ask. "i want to help
# but i'm exhausted too" is not a question about the difference between to and too, and an entry
# keyed on "to" must not read it as one.
WANT_FILLER = frozenset("to like of in for would feel the mood keen hoping planning thinking love "
                        "plan plans planned".split())


# A row's `ask` is almost always written in the first person - "can i", "should i", "is it ok
# to", "how do i" - because that is how the person would ask about themselves. A line asking
# the same thing about someone else said the ask and never met it: "my wife is pregnant" then
# "can she fly" reached the flying row on its own words and was turned away at the ask
# ("can i" is not in "can she fly"), so a question the row answers got a shrug; "my dad has
# arthritis" then "can he take ibuprofen" went the same way. The ask is a kind of question,
# not a person, so the pronoun in it is read as any person and every other word of it still
# has to be said.
ASK_PEOPLE = frozenset("""
he him his she her hers they them their theirs we us our ours you your yours
son daughter wife husband partner mum dad mother father child children kids baby boy girl
brother sister nan grandad grandma
""".split())


# A line that rules a state out is not about that state: "im not having a panic attack" is not
# the panic entry, and "im not in any pain" is not the pain one. Only the person saying what
# they are not in the middle of counts - the speaker, the copula and a word that carries a state
# ("not having", "not getting", "not in", "not being") - because the same shape elsewhere is a
# qualifier or a problem the entry answers: "a film thats not too long", "i dont have yeast",
# "my air con is not very cold", "the washing machine is not draining". A negator the entry's
# own key already holds ("not working", "not eating") is the key, not a denial of it.
DENY_SAID_OF = frozenset("""i im ive we were he hes she shes they theyre it its there am is are
    was were""".split())


DENIERS = frozenset("""not no dont doesnt didnt isnt arent wasnt werent aint""".split())


STATES_AFTER = frozenset("having getting being been in".split())


DENY_BETWEEN = frozenset("""really still even any more all at very too quite a an the""".split())


_FRAME_MASK = object()


# The words that turn the rest of a line into something the person wants left out: "how do i
# sleep without pills" is about sleeping, not about pills. The words after the frame still
# reach an entry that asks for the frame itself - "how do i cook without an oven" has an answer
# of its own, and "what can i use instead of butter" is a swap entry that names both things - so
# the mask is only applied to an entry whose key does not name the frame word.
ASK_FRAME = frozenset("""
    how hows what whats which who whom whose when where why
    is are was were am be been can could should would will shall may might must
    do does did doing i im get gets got getting
    """.split())


# A time word says when a thing happens, not what the line is about, and the understander already
# keeps the days, the months and the parts of the day in one place: a row that reached a line on
# one of these alone has not named the subject either. The plural is here because a key says
# "nights" as often as "night", and "bedtime" because the hour before bed is asked about by the
# name of the hour ("what should i do at bedtime") rather than by the word "night".
WHEN_WORDS = frozenset(TIME_WORDS | {word + "s" for word in TIME_WORDS} | {"bedtime"})


# A length word is how long a thing runs, not what the thing is: "how long does caffeine last",
# "how long do leftovers keep". A row whose whole reach into the line is "how long" and "last" has
# named nothing the line is about, and it answered every other line of that shape - "how long did
# the hundred years war last" got the caffeine card (the history row names the war), "how long did
# the cold war last" got the prawns. Read with the same rule as the two sets above: a row that
# also names a subject is unaffected, which is every row that answers one.
A_LENGTH_WORD = frozenset("""
    long last lasts lasted lasting keep keeps kept take takes taking time times run runs
    minute minutes hour hours day days week weeks month months year years
    """.split())


# A pronoun stands for the thing and never names it. "how long does it last" and "how long should
# they last" name no subject at all: the thing is in the turn before, and the row that answered
# was the one that also keys the pronoun - the state pension for a pair of headphones, the fridge
# for a laptop battery. A row that names the thing as well is unaffected.
A_STAND_IN = frozenset("""
    it its itself they them their theirs this that these those you your we us our
    """.split())


# A frame covers the rest of its clause and no more: "a sauce without flour and a cheap pan" is
# two things and only the first is left out. Punctuation is gone by this point, so these are
# the words a new clause starts with.
FRAME_ENDS = frozenset(("and", "but", "or", "so", "then", "when", "if", "because", "while",
                        "which", "that", "to", "for", "with", "plus", "except", "besides"))


# A "without" clause that starts with a pronoun, or with a verb whose object is a pronoun, is
# not a thing left out: it is what the thing in hand does wrong. "how do i fry eggs without them
# sticking" is a question about eggs sticking, and the fault is the subject of the answer.
# "how do i sleep without pills" leaves pills out, and the pills are not what the line is about.
# The mask still goes on (an entry that counts the clause as words outranks the subject of the
# line on plenty of other lines), and what a clause like this buys is a second look in `_best`:
# the whole line may win without its margin, but only where the rest of the line has no answer of
# its own (`_the_subjects_own_row`).
FRAME_PRONOUNS = frozenset("it its them they this that those these he she him his her".split())


# "What's the best way to clean a shower screen" is a request for a method, and "best" and
# "way" there are the asking, not the thing. A row that stays away from "best" - the soap-scum
# row does, so that "which is best, a bath or a shower" reaches the bath-or-shower card - also
# refused the commonest how-to phrasing: the screen answer, the shower answer and about 280
# other avoid lists sit behind this word. An avoid word is matched loosely wherever it appears,
# so the two words of the ask phase are blanked for the avoid test only: the rest of the line,
# and the row's own key, still read exactly as they did. "how best do i ..." is the same ask.
ASK_PHRASE_WORDS = frozenset(("best", "way", "ways"))


_ASK_PHRASE_MASK = object()


# How a person states a complaint about themselves and asks nothing: "i have tinnitus", "ive
# got heartburn", "i keep getting cystitis". The words below are the whole grammar of such a
# line; anything else in it means the line says more than the complaint, and then the entry has
# to earn the turn on two positions of its key like every other line.
REPORT_LEADS = frozenset((
    "i", "im", "ive", "am", "have", "has", "had", "got", "get", "gets", "getting", "keep",
    "keeps", "keeping", "feel", "feels", "felt", "feeling", "been", "was", "suffer", "suffering",
    "think", "thought", "reckon", "suspect", "probably", "maybe", "definitely", "sure"))


# A complaint reported about somebody else is the same line as the complaint about themselves.
# "i have head lice" was answered and "my daughter has head lice" was not - not a search hedge, a
# shrug: the person named in front of the complaint is not one of the words a report is made of,
# so the subject scored 2 and the answer that was one word away never ran. A parent writing about
# a child is the commonest way these lines arrive, and the whole family is the same shape.
REPORT_PERSON = frozenset((
    "son", "sons", "daughter", "daughters", "child", "children", "kid", "kids", "boy", "girl",
    "baby", "toddler", "little", "youngest", "eldest", "oldest", "teen", "teenager", "lad",
    "lass", "he", "she", "him", "her", "they", "them", "husband", "wife", "partner",
    "boyfriend", "girlfriend", "fiance", "fiancee", "friend", "friends", "mate", "mates",
    "mother", "mum", "mom", "father", "dad", "nan", "nana", "grandma", "grandad", "granny",
    "brother", "brothers", "sister", "sisters", "parent", "parents", "boss", "carer",
    "his", "her", "their", "our", "one"))


REPORT_FILLER = REPORT_LEADS | REPORT_PERSON | frozenset((
    "a", "an", "the", "my", "me", "really", "very", "so", "too", "just", "still", "also",
    "suddenly", "quite", "bit", "lot", "of", "with", "and", "at", "in", "on", "today", "now"))


# The words a complaint carries when it is the second time of asking: "my hay fever again",
# "eczema is back", "the asthma keeps coming back". A recurrence after the subject is the
# statement the report leads ("i have hay fever") are when the subject comes first, and without
# it a row that answers a stated complaint answered only the one word order.
HAPPENING_AGAIN = frozenset((
    "again", "back", "still", "already", "anyway", "now", "once", "twice", "more", "every",
    "year", "season", "spring", "summer", "autumn", "winter", "time", "times", "keeps", "keep",
    "kept", "coming", "come", "came", "going", "goes", "went", "on", "round", "around", "at",
    "as", "usual", "this", "same", "the", "it", "its", "is", "are", "was", "were", "has", "have",
    "had", "here", "today", "tonight", "morning", "night", "week", "month", "of", "in", "and",
    "so", "but", "though", "now", "first", "before", "like", "last"))


# The words a request to explain a thing is made of, and the words of that request that carry no
# subject of their own. "what is sepsis", "what's gout", "tell me about shingles" and "explain
# sciatica" are the same question, and the thing asked about sits behind nothing but those.
EXPLAIN_LEADS = frozenset((
    "what", "whats", "explain", "explained", "definition", "define", "meaning", "describe",
    "tell", "info", "information", "basics", "overview"))


EXPLAIN_FILLER = EXPLAIN_LEADS | frozenset((
    "s", "is", "are", "was", "does", "do", "did", "a", "an", "the", "of", "about", "on", "in",
    "for", "me", "us", "my", "mean", "means", "meant", "by", "symptom", "symptoms", "sign",
    "signs", "cause", "causes", "treatment", "exactly", "actually", "please", "and", "more"))


# A row that says how to do something on the person's own machine - sign a PDF, merge two files,
# fill in a form - is instructions for their hands. "can you fill in this form", "can you sign this
# for me" is not asking for those instructions: it is asking whether the bot can do it, and the
# honest answer is that nothing here can see the form, so the composer's reader for a thing on the
# person's side has the line. Without this, "can you fill in this form" and "help me fill in this
# form" reached the PDF-signing row and were told which menu to use.
ASKS_FOR_THE_HANDS = re.compile(
    r"\b(?:can|could|would|will|are|do)\s+(?:you|u)\b|\b(?:for|help)\s+(?:me|us)\b")


# The verbs a hand or an eye would do to a thing on their side: filling, signing, printing,
# scanning, reading. Reading is on the list because "can you read this letter from the council" is a
# person handing the bot a thing it cannot see, but it is the one verb that is also a real job for
# the knowledge base ("what does this letter mean", see `ASKS_WHAT_IT_SAYS` below), so that shape
# stands the reading down and the row keeps the line.
A_HAND_OR_EYE_DOES_IT = re.compile(
    r"\b(?:fill|fills|filling|sign|signs|signing|print|prints|printing|scan|scans|scanning|"
    r"open|opens|opening|read|reads|reading|check|checks|checking|complete|completes|"
    r"completing|translate|translates|translating|look\s+(?:at|through|over))\b")


# The same line can ask for a hand or for the meaning, and only the meaning is a job for the
# knowledge base: "can you read this letter and tell me what it means" is answered by the row that
# says what to look for in a letter, so it keeps that row. "can you read this letter from the
# council" names no question about the content and is asking the bot to see it.
ASKS_WHAT_IT_SAYS = re.compile(
    r"\b(?:what|whether|if)\b|\b(?:means?|meaning|says?|explain|explains|explaining|"
    r"understand|summar\w+|translate\w*|about\s+it)\b")


# The thing has to be one of theirs, said as theirs: "the documents i need for a passport" is a
# question about a rule and keeps its answer, and only "my form", "this pdf", "the letter" is the
# thing on their side that nothing here can see.
OWN_THING_ON_THEIR_SIDE = re.compile(
    r"\b(?:my|our|this|that|these|those|the)\s+(?:[a-z']+\s+){0,2}"
    r"(?:form|forms|pdf|pdfs|file|files|document|documents|paperwork|scan|scans|"
    r"screenshot|screenshots|photo|photos|letter|letters|invoice|invoices|contract|"
    r"application|applications|cv|questionnaire|questionnaires)\b")


THEIR_OWN_HANDS_THINGS = frozenset("""form forms pdf pdfs file files document documents paperwork
    scan scans screenshot screenshots photo photos letter letters invoice invoices contract
    application applications cv questionnaire questionnaires""".split())


# "How many eggs?" asks two different things. "how many eggs a day" asks the allowance, and it
# is the reason "how many" is in the cholesterol rows' keys; "how many eggs go in an omelette"
# asks the recipe, and "how many days do eggs keep" asks the box. The dish does not tell them
# apart - "are eggs in a cake bad for you" names the same cake and is the allowance's question -
# so the verb does: a count that "goes in" or is "put in" belongs to the dish, and a count of
# days or a keeping verb belongs to the box. Nothing about a daily allowance goes in a cake or
# keeps in a fridge.
GOES_IN = re.compile(r"\b(?:go|goes|going|went)\s+(?:in|into)\b|\bputs?\s+in\b", re.I)


# The verb is not always there: "how many eggs in a quiche" and "how many eggs for a cake" count
# into a dish with no "go in" at all. What separates the dish from the allowance is what follows
# the article - a dish or a batch is a container, and "a day", "a week" are the allowance. So a
# count into something that is not a stretch of time belongs to the dish.
COUNTED_INTO_A_THING = re.compile(
    r"\bhow many\b[^?]*\b(?:in|into|for)\s+(?:a|an|the|my|one|two|three|four|six|\d+)\s+"
    r"(?!days?\b|weeks?\b|months?\b|years?\b|mornings?\b|evenings?\b|sittings?\b|"
    r"meals?\b|servings?\b|serving\b|portion\b|portions\b|time\b)", re.I)


HOW_MANY_DAYS = re.compile(r"\bhow many (?:days|weeks|months)\b", re.I)


KEEPS_OR_STORES = re.compile(
    r"\b(?:keep|keeps|kept|keeping|store|stores|stored|storing|last|lasts|lasting|"
    r"fridge|freezer|freeze|go off|gone off)\b", re.I)


# --- "keeps" as a fault verb, not a shelf-life word -------------------------------------
#
# "How long does bread keep" and "my bread keeps coming out flat" share the word that decides
# which row answers, and the shelf-life rows win both: the storage line ("It keeps 3 days in a
# paper bag") is what somebody whose baking keeps failing was told, and the same for a roast
# chicken that comes out dry and a marble run that keeps falling over. The fault is the verb
# itself - "keeps" with another verb right after it - so the shape is what stands the keeping rows
# down, not a list of the verbs, which is every verb there is.
#
# Two shapes are the keeping question still. "My herbs keep wilting" and "my cake keeps going
# dry" are spoilage, which is what a shelf-life answer is for, so a word of rot after the verb
# keeps the keeping row in. And "coming out" is the cook reporting a result ("keeps coming out
# dry" is a roast chicken, not a mouldy one), so that shape is a fault even when the word after
# it is a spoilage word.
_KEEPING_VERB = frozenset(("keep", "keeps", "kept", "keeping"))


_RESULT_VERB = frozenset(("coming", "comes", "come", "turning", "turns", "turn"))


# The verbs of rot, in the forms people write them. Bounded on purpose: a state that is not here
# is a behaviour to fix, which is the reading the fault has.
_SPOILING = frozenset((
    "mouldy", "moldy", "mould", "mold", "moulding", "molding", "slimy", "slimy", "soggy",
    "mushy", "sour", "soured", "souring", "rancid", "stale", "wilted", "wilting", "wilt",
    "limp", "off", "bad", "rotten", "rotting", "rot", "brown", "browned", "browning",
    "discoloured", "discolored", "curdled", "curdling", "curdle", "smelly", "smelling",
    "stinking", "sprouting", "sprouted", "spotted", "furry", "fuzzy", "blue", "green",
    "shrivel", "shrivelled", "shriveling",
))


# A word that ends in -ing and is a thing rather than a verb: "it keeps the evening quiet" is
# not a fault, and a key of "keep" plus one of these is the keeping row's own line.
_ING_NOUNS = frozenset((
    "evening", "evenings", "morning", "mornings", "ceiling", "building", "feeling", "feelings",
    "meeting", "meetings", "wedding", "pudding", "stuffing", "dressing", "filling", "parking",
    "clothing", "bedding", "writing", "painting", "drawing", "reading", "heating", "lighting",
    "awning", "herring", "sterling", "seedling", "sibling", "dumpling", "spring", "springs",
    "string", "strings", "thing", "things", "ring", "rings", "king", "wing", "wings",
))


# The keeping rows themselves, found by the words they are keyed on, so a row added tomorrow is
# covered without anyone remembering to hold it out of a fault line. A keeping row holds the
# keeping word *and* one of the life words, both as alternatives of their own: "keeps" on its own
# is the word for a repeated fault as well ("my friend keeps cancelling", "he keeps interrupting
# me"), and a row that answers that complaint must keep answering it.
_KEEPING_KEY = frozenset(("keep", "keeps", "kept", "keeping"))


_LIFE_KEY = frozenset(("how long", "shelf life", "shelf-life", "store", "stores", "storing",
                       "stored", "storage", "last", "lasts", "lasted", "lasting", "fresh",
                       "fresh for", "still good", "gone off", "out of date", "use by"))


# A verb after "keeps" that says the thing comes round again rather than that it goes wrong: "why
# do i keep getting cold sores" and "i keep getting cystitis" are the subject recurring, so what is
# wanted is the cause and how to keep it off, which is the subject's own row. A keeping row that
# read these as faults stood itself down and the line got nothing ("why do i keep getting cold
# sores" got a sympathy card) or the wrong row ("why do cold sores keep coming back" reached the
# joints-in-cold-weather card on "cold" and "back"). The verbs of having a condition are enough on
# their own; "coming", "going" and "giving" are verbs of anything, so they count only with the
# word that places a recurrence ("keeps coming back", "keeps going on"). "my son keeps losing his
# jumper at school" is still a fault: what he keeps doing has the jumper as its object, so the
# row about storing a jumper has nothing to say to it. "having" is not here on purpose: "i keep
# having biscuits at about 4pm" is a habit, and the tin they keep in is not the answer to it.
_RECURRING = frozenset((
    "getting", "happening", "happens", "recurring", "returning", "flaring", "cropping"))


_RECURRING_ANYWAY = frozenset(("coming", "going", "giving"))


# The words that place a recurrence rather than a result: it comes *back*, it goes on *again*.
_RECURRING_WITH = frozenset(("back", "again", "around", "round", "on"))


# The words that only point at a thing ("the condensation", "my snoring") and so say nothing
# about it; the framed reading is right only when the entry's subject part matches the rest.
_SUBJECT_POINTS = frozenset("a an the my your our his her its it of in on at for to".split())


# A "-y" word whose stem is a different everyday word of its own, so the stem is not what the
# person meant: "are you ready" is not reading, "i'm busy" is not a bus, a "handy" shelf is not
# a hand, "a birthday party" is not a part, and "my belly" is not a bell. Everything else that
# ends this way is the same thing said as an adjective, which is what the rule below reads.
NOT_THE_ADJECTIVE = frozenset("""
    ready busy handy party army belly copy body study lady fully funny pity cosy policy every
    bully tally holy early rally holly jelly apply battery cheeky dicky factory fairy gravy
    irony kindly multiply pasty silly shiny story whisky clammy telly chilly watery shivery
    sticky
""".split())


# --- somebody has a thing --------------------------------------------------------------
# A key that says "have" never met a line that says "has". The -s rule cannot reach it: "has" is
# three letters, and a short stem is not a word the matcher will strip to. So "my mum has a
# headache" met no key word at all beyond its subject, scored under MIN_SCORE, and was answered by
# whichever card had a word about caring for a poorly person: "That's a worry when it's someone
# you look after. Are they drinking and keeping it down?" - a question about vomiting, asked of a
# headache.
#
# Handing "have" to every "has" in every line costs more than it buys. "my phone screen has a
# green blotch" reached the rash row, whose key lists "have", and told them about a hydrocortisone
# cream; "my dog has epilepsy" was answered with lamotrigine, a neurologist and the DVLA, where the
# honest answer was to ask the vet. What the good lines have and the bad ones lack is the sense:
# somebody having a thing. So the reading is fenced by the sentence around the word - a person
# before it, and a thing after it rather than the rest of a verb.
_A_PERSON = frozenset(PEOPLE_MALE) | frozenset(PEOPLE_FEMALE) | frozenset((
    "friend", "mate", "friends", "partner", "child", "children", "kid", "kids", "baby",
    "neighbour", "neighbor", "colleague", "boss", "teacher", "someone", "somebody", "cousin",
    "person", "people", "they", "them", "we", "us", "you"))


# "has to" is a modal and "has been", "has had" and "has it" are the rest of a verb phrase: none
# of them is a thing the person has.
_NOT_A_THING_HAD = frozenset(("to", "had", "been", "being", "it", "them", "not", "no", "never",
                              "nothing", "none", "enough", "already", "yet"))


# Adverbs that turn "what do I say" into "what do I actually say" without changing what is
# asked. They are dropped only for a second read of a line that reached no entry as typed.
_FILLER = frozenset(("actually", "really", "honestly", "literally", "genuinely", "basically"))


FEELING_ABOUT = frozenset("about of with over at by".split())


# What ends the thing a feeling is about: a new clause, another person, or a word that is a time
# rather than a thing.
FEELING_ENDS = frozenset("""
    and but because so then when if that which who whom whose or also plus after before since
    till until while though although yet today tomorrow tonight now yesterday again too as
    i im ive id we they he she them us
""".split())


# A bare pronoun names nothing to take away: "upset about it" keeps its words.
FEELING_NAMES_NOTHING = frozenset("""
    it them everything nothing anything something all
""".split())


# The domains whose cards answer a person's feeling rather than a thing: a line that reaches one
# of these keeps every word, because "my son is scared of the dark" wants the card about a
# child's fear, not a line about a dark room, and "worried about my rent" wants the rent card.
FEELING_DOMAINS = frozenset(("family", "friends", "study", "health", "sleep", "pregnancy",
                             "money", "work", "lifeadmin",
                             # A card about a thing the feeling is about is not a card about the
                             # feeling, whichever module it lives in: "worried about my knee pain"
                             # is a knee question, "my daughter is upset about her friend" wants
                             # what to say to the friend, and "worried about my flight tomorrow"
                             # wants the flight. Stripping the words that name the thing left
                             # those lines with nothing, so the modules they are filed in are
                             # listed here. This is the module name, not a list of subjects.
                             "body", "wording", "complaints", "travel", "home"))


# A broken thing is the subject of the line even when the line also says how it feels: "im
# worried about my washing machine leaking" wants the water off, not sympathy.
FEELING_FAULT_WORDS = frozenset("""
    leak leaks leaked leaking drip drips dripping burst bursts bursting broken broke breaks
    blocked blocking stopped stops smoking sparking smells smelly smell damp mould mold
    flooded flooding flood loose wobbles wobbling snapped cracked clicking noisy
""".split())


# A fear the person speaking has is a question about the thing feared: "im scared of the dentist"
# wants the dentist card, "im scared of flying" the one about flying. The same words about someone
# else are the occasion of their feeling: "my son is worried about football practice" does not
# want a page about practice. So when the line has the speaker's own feeling, every word stays.
FEELING_SPEAKER = frozenset(("i", "im", "ive", "i'm", "i've", "id", "me", "myself"))


# Some things are not the occasion of a feeling but the thing itself: people are frightened of a
# short list of things as a class, and the card about that thing is the answer. "my son is scared
# of the dentist" wants the dentist card, not sympathy, and "im scared of flying" the one about
# the first flight - while "my son is worried about football practice" is a boy's afternoon.
FEARED_THINGS = frozenset("""
    dentist dentists dentistry dental flying plane planes flight flights needles needle
    injections injection jab jabs spiders spider snakes snake heights height lifts lift
    escalators dark thunder lightning storms storm blood vomit sick wasps bees mice rats
    clowns hospitals hospital doctors doctor dentists surgery operation operations
    presentations public presentations interviews interview exams exam tests test motorways
    motorway driving flying ferries tunnels enclosed spaces crowds dentists darkness
    water swimming swim pool pools
""".split())


# A thing that has been put down and cannot be found is not a fact about the thing. "where did i
# put the nappy cream" was answered with which barrier cream to buy and "where is my nappy bag"
# with what to pack in one, and the right reply to both is somewhere to look. That answer does
# not depend on what the thing is, so no row can be better at it than another: the whole base
# stands down and the composer's loss reading takes the line. Only the asking, not the naming: a
# row that says where a thing is kept ("where do i keep my passport") is answering a different
# line and is untouched.
_WHERE_I_PUT = re.compile(r"\bwhere\s+(?:did|have|has|had)\s+i\s+(?:put|leave)\b")


# A line that asks *where* a thing is kept is the keeping row's question, and a row that helps
# choose one is not the answer: "where should i keep my winter jumpers" was answered with which
# fibre to buy, and "where should i keep my duvet in summer" with the tog ladder. The frame is the
# word "where" and not the word "keep", because "keep" also means "which jumper keeps me warm" -
# a buying question, which must stay one.
_WHERE_TO_KEEP = re.compile(
    r"\bwhere\s+(?:should|shall|do|can|could|would|will|might|am\s+i\s+to)?\s*(?:to\s+)?"
    r"(?:i\s+|we\s+|you\s+)?(?:keep|store|stow|put\s+away|pack\s+away)\b")


# What a row's key says when it is the keeping of a thing rather than the choosing of one.
_KEPT_SOMEWHERE = frozenset("""
keep keeps keeping kept store stores stored storing storage stow stows stowed stowing
away loft wardrobe moth moths cedar
""".split())


# A price card can only answer a line that judges a price if it is holding a price. The general
# test of the line lives with the price rows (`prices.a_price_is_judged`); this is the half about
# the answer, and it sits in the one place every card is chosen, so a card written next year is
# covered without remembering to consult anything.
_HOLDS_MONEY = re.compile(r"\u00a3\s?\d|\b\d+(?:\.\d+)?\s?(?:p|pence|pounds?|quid)\b|"
                          r"\b\d+\.\d{2}\b|\bpounds?\b")


# The thing after "for" in a line judging a price: "is 4 pounds a lot for a chicken" names the
# chicken, and the base is asked what a chicken costs.
_THE_THING_JUDGED = re.compile(r"\bfor\s+((?:a|an|the|my|our|this|that|these|those)\s+)?"
                               r"([a-z][a-z' ]{1,40})$", re.I)


# A word that points at the thing instead of naming it. "is 4 pounds a lot for one", asked while a
# chicken is on the table, is about the chicken.
_POINTS_AT_IT = frozenset("""
    one ones it that this these those them they him her he she the thing things that one this one
""".split())


# Where a thing is, on the body, is not what the line is about: "the mole on my arm is sore",
# "my mole on my back has grown", "the lump on my neck is bigger". No card is keyed on the place,
# so the words spent on it stood the card down and the line reached nothing - "the mole on my arm
# is sore" got "I'd rather not guess. A quick search online ..." while "my mole is sore" got the
# two-week card. The same re-read as the two readers above: the line without the place is the ask
# about the thing it named. Only a part of the body, so "the leak in my kitchen" and "the price of
# a pint in my local" keep every word of what they said.
_A_PLACE_ON_THEM = re.compile(
    r"(?:,?\s*(?:on|in|under|near|around|behind|above|below|beside|by|at|just (?:above|below|"
    r"under|behind|over|beside|next to))\s*(?:the\s+)?(?:my|his|her|their|our|your|its|this|"
    r"that)?\s*(?:left|right|inner|outer|lower|upper|front|back of the|top of the|side of the)?"
    r"\s*([a-z]+))\b", re.I)


# A thing reported as not gone is a thing still there, and it is the commonest way people say a
# symptom has not shifted: "the cough has not gone", "the rash hasnt gone", "my knee hasnt got any
# better". Cards are keyed on the ask ("still there", "wont go", "how do i treat"), so the report
# reached nothing and the person got a nod. The clause saying it has not gone is the news, not the
# subject, so the rest of the line is read again as the ask about the thing it named.
_NOT_GONE = re.compile(
    r"\b(?:has|have|had|is|are|was|were|does|did)?\s*(?:not|n't|never)\s+"
    r"(?:gone|gone away|shifted|cleared|cleared up|eased|settled|improved|any better|got any better|"
    r"got better|better)\b|\bno better\b|\bwont\s+go\b|\bwon't\s+go\b|\bwould\s+not\s+go\b",
    re.I)


_SUBJECT_LEAD = re.compile(r"^(?:and|but|so|well|ok|okay|hi|hello|um|er)\b[,\s]*", re.I)


_POSSESSIVE = re.compile(r"^(?:the|my|his|her|their|our|your|a|an|this|that|these|those)\s+", re.I)


# The words a line spends on the refusal itself: with these and the ruled-out thing gone there is
# no subject left in the line for a card to be about.
_OF_THE_RULE_OUT = dict.fromkeys("""not a an the rather than instead of and but or please really
actually just so though although is are was were be been do does did""".split(), True)


# "degrees" is a measure of heat in "35 degrees" and a qualification in "a 2:1 degree".
_THE_DEGREE_WORDS = frozenset("degree degrees".split())


_THE_HEAT_OF_THE_DAY = frozenset("""
    hot cold warm cool heat heating temperature weather forecast oven fan oven thermometer summer
    winter sunny degrees
""".split())


# The words a person asks with when the ask is a clause of its own: "..., what do i wear".
_THE_WH_WORDS = frozenset("what whats why how when where which who whose whom".split())


# The words an ask shares with every ask of its shape: the question word, the helper and the
# person. A card that answers the ask matches a word of it that is not one of these - "what should
# i bake" is answered by a card that holds "bake", and the card about why a craving comes holds
# only "what", so it is the setting clause's words that took the line.
_ASK_FRAME = frozenset("""
    what whats why how when where which who whose whom do does did should shall can could will
    would may might must i me my we our us you your the a an is are was were be been being to
    for of in on at it that this these those there here and or but if so then also just
""".split())


# A place a person lives is not the person. "flat" is a home in "my flat is freezing" and a mood in
# "i feel flat"; "cold" is the radiators in "the flat is cold" and a symptom in "im always cold".
_PLACES_PEOPLE_LIVE_IN = frozenset("""
    flat house home room rooms kitchen bedroom bathroom lounge hall hallway office classroom
    conservatory garage shed caravan cabin attic loft basement studio cottage
""".split())


_COLD_WORDS = frozenset("cold freezing frozen chilly baltic perishing".split())


# The words that sit between the place and the cold, kept to the few a person types: "the flat is
# so cold", "my room is freezing", "the kitchen was really cold all weekend".
_BETWEEN_A_PLACE_AND_ITS_COLD = frozenset("""
    is was are were get gets got been be feels feel really very so too absolutely
    bit little always still
""".split())


_HOW_A_PERSON_IS_COLD = frozenset("""
    shiver shivers shivering shivery chilled freezing numb goosebumps
""".split())


_SAYS_OF_THEMSELVES = frozenset("i im ive id iam me myself".split())


# "what is a semicolon for" and "what is a deductible" name one thing and ask nothing else. That
# is a definition, and a definition is the commonest way a person asks about a word. The rows are
# written for the asks around a thing ("how do i use a semicolon", "is a warranty worth it"), and
# a definition line covers one position of such a key, so it fails the two-signal rule and the
# person got "I'm not sure about that one" about a thing the knowledge base already answers.
# These are the shapes of the definition ask; the thing is the rest.
_DEFINITION_ASK = re.compile(
    r"^\s*(?:so\s+|ok\s+|okay\s+|and\s+|but\s+)?"
    r"(?:"
    r"what\s*(?:'s|\u2019s|s)?\s+(?:is|are|was|were)\s+(?P<thing>[^?.!,;:]{1,60}?)"
    r"|what\s*(?:'s|\u2019s|s)\s+(?P<thing2>[^?.!,;:]{1,60}?)"
    r"|what\s+(?:does|do)\s+(?P<thing3>[^?.!,;:]{1,60}?)\s+mean"
    r"|define\s+(?P<thing4>[^?.!,;:]{1,60}?)"
    r")\s*(?:\?)?\s*$", re.I)


# The words of the ask that are not the thing asked about, including the tail a person puts after
# it ("what is a semicolon for", "what is an isa exactly", "whats an isa please").
_DEFINITION_TAIL = frozenset("""
    for mean means meant exactly then again please called thats it its in simple terms
    supposed to do stand stands actually really even anyway though
""".split())


# Words too empty to be the thing asked about, so "what is it" and "what is that" stay a punt.
# A thing that opens with one of these is pointing at something said a turn ago, or asking what
# there is to do somewhere, and no key names it.
_DEFINITION_POINTERS = frozenset("""
    there it that this these those he she they we you i someone anyone somebody nobody
""".split())


# A trouble word in the thing means the line is a diagnosis, not a definition: "what is wrong with
# my knee" asks what is the matter, and the row that knows about knees says where the saddle goes.
# None of these can be part of the name of a thing somebody wants defined, so the line is left to
# the readers that answer a problem.
_DEFINITION_TROUBLE = frozenset("""
    wrong matter happening pain painful hurts hurt hurting ache aches aching smell smells smelling
    leak leaks leaking noisy noise broken stuck faulty fix
""".split()) | {"going on", "up with", "up to"}


_DEFINITION_EMPTY = frozenset("""
    a an the my your our their his her its some any this that these those of in on at to and or
    for with from about it that this there here one ones thing things stuff kind sort type
    what which who whom whose how why when where right best good
    going happening wrong up on around next
""".split())


# The verbs a definition of a thing runs on: "A warranty is a bonus on top of your rights",
# "Food banks give a few days of free food". A thing the opening sentence only mentions on the way
# to something else is not being defined by it.
_DEFINING_VERBS = frozenset("""
    is are was were means mean refers gives give costs cost covers cover keeps keep works work
    helps help makes make takes take needs need holds hold comes come runs run lets let stops stop
    protects protect lets replaces replace counts count serves serve
""".split())


# The verbs that make a sentence say what something is, and the words that show a thing is
# only part of a phrase about something else.
_BE_VERBS = frozenset("is are was were".split())


_DEFINITION_ARTICLES = frozenset("a an the".split())


_BEFORE_THE_THING = frozenset("""
    of in on with at from your my our their its his her
    cup mug glass slice piece bit bowl plate packet tin can bottle spoon teaspoon tablespoon
    handful pinch taste sip bite
""".split())


# --- a line that is only the name of a thing --------------------------------------------------
# "nappy rash", "cradle cap", "heat rash": a person naming what is wrong, with no verb and no
# ask, is asking about it. The card keyed on the name was never reached, because a key wants a
# second signal as well as the subject - so bare "nappy rash" got the health visitor line. A name
# on its own is the whole ask, and only a card whose subject group the line spells out exactly
# will do: nothing is guessed from one word of a two-word name.
NAME_ALONE_DOMAINS = frozenset('''family health body babyfood pregnancy'''.split())


# The words that make a line more than a name: a question, a pointing back, or the speaker in it
# ("i think nappy rash" is a sentence).
NOT_A_NAME_ALONE = frozenset('''what why how when where which who whom whose is are was were
    am do does did can could should would will shall may might i im ive id you your u my mine
    me we our us it its that this these those there they them he she him her his hers the a an
    and or but if so then than about for with on in at to of from not no yes ok okay thanks
    please help huh'''.split())


# A name is a thing. The phrase a person types when they drop themselves out of the sentence is
# not: "gone numb", "went numb", "feel numb" and "burning up" are things said about a body, and a
# bare "gone numb" answered with the cauda-equina warning told somebody to ring 999 about a foot
# that had gone to sleep. A state verb in the phrase means the line is a report, not a name.
# A word a name does not end in: "school closed" and "back open" are clauses about a thing, and
# the card that lists the clause is answering the clause.
A_STATE_AS_A_NAME_END = frozenset('''closed shut blocked swollen broken numb off blocked'''.split())


A_STATE_IN_THE_PHRASE = frozenset('''feel feels feeling felt gone went go goes going get gets
    getting got gotten been being be keep keeps keeping kept start starts started starting
    burn burns burning'''.split())


# The words that point back at the thing already said: a line carrying one of these is about
# that thing whatever else it says ("its 3 years old" after a cat).
POINTS_BACK = frozenset("""it its it's that this these those there them they he she him her""".split())


# A follow-up whose own words are all asking or pointing adds no subject of its own: "will it be
# alright", "what happens now", "is that bad", "how long do i wait". Such a line is about the
# subject before it, which is why it leans, and the entry the earlier line reached is its answer
# even though the line touches none of the entry's own words. The gate above was refusing exactly
# those: "will it be alright" after "i dropped my phone in the sink" left the phone-in-water card
# unread and the person got "that's beyond what I know well, sorry", and the deck has the same
# shape for a boiler losing pressure, a flat mood, a tax return and a house guest.
FOLLOW_ON_WORDS = frozenset("""
about actually alright anyway bad better change good happen happens idea instead mean means meant
now okay otherwise question really safe suppose then thing think true wait worse wrong
common dangerous fine fix fixed happening happened knackered normal repair repaired ruined ruin
salvage salvaged save saved serious survive survived survives worrying worried worth next
""".split())


# The words every card in the base may key on because they are how a line asks rather than what
# it asks about. A short list on purpose: the frequency cap above already keeps most of them out.
ASK_FRAME_WORDS = frozenset("""
    what when where which who why how should could would can will shall may might must
    is are was were be been being am do does did done doing have has had having
    get gets got getting need needs want wants like likes make makes made take takes
    go goes going put give gives tell say says know think use uses try tries
    good best better bad worse right wrong sure possible worth
    """.split())


# The words an entry's key uses when the entry is there to name what can go in place of something
# else. A line that leaves an ingredient out ("can i make pesto without pine nuts") wants that
# entry, not the entry that answers the dish with the ingredient still in it.
SUBSTITUTE_WORDS = frozenset(("substitute", "substitutes", "substitution", "instead", "swap",
                              "alternative", "alternatives", "replace", "replacement"))


# The words a "back" says nothing about the body after: the thing came back, or somebody went
# back to something. "my knee pain is back again" is the knee, "my hip pain is back" is the hip,
# and "I'm going back to study at 38" is a course - but each of them reached the back entry and
# answered "Most back pain is muscular and settles in two to six weeks", a part the person never
# named. A verb in front is what tells the two apart: the back that is a part has no verb there
# ("my back", "lower back pain"), while every return and every going back is "<verb> back".
RETURNED_AFTER = frozenset("""
    is are was were be been am
    im i'm youre you're hes he's shes she's theyre they're were we're
    come comes came coming
    go goes going went gone
    get gets getting got gotten
    walk walks walking walked
    drive drives driving drove driven
    fly flies flying flew flown
    run runs running ran
    head heads heading headed
    move moves moving moved
    travel travels travelling traveled
    carry carries carrying carried
    bring brings bringing brought
    take takes taking took taken
    send sends sending sent
    call calls calling called
    write writes writing wrote written
    put puts putting
    hand hands handing handed
    pay pays paying paid
    give gives giving gave given
    kick kicks kicking kicked
    sit sits sitting sat
    lie lies lying lay lain
    step steps stepping stepped
    look looks looking looked
    turn turns turning turned
    think thinks thinking thought
    bounce bounces bouncing bounced
""".split())


# Parts that are everywhere: a rash on the knee is still the skin entry, and a keyed "skin" is
# not a different part from the one the line names.
GENERAL_BODY = frozenset(("skin", "muscle", "muscles"))


# A body word beside a cut of meat is the joint on the board, not a part of a person: "how long
# should i rest a leg of lamb" is the roast and not a leg, and "pork shoulder" is the cut. The
# rows keyed on a cut that is also a part ("shoulder", "ribs") were standing down for every line
# that named a body part, which is how the resting question reached no meat row at all.
_CUT_BESIDE = frozenset((
    "lamb", "beef", "pork", "chicken", "turkey", "duck", "goose", "gammon", "veal", "venison",
    "meat", "steak", "joint", "roast", "roasting", "brisket", "mince", "sausage", "sausages",
    "ham", "bacon", "chops", "chop", "fillet", "breast", "thigh", "drumstick", "wing"))


# A thing that has already been kept somewhere and a question about whether it is still good is
# one question, and it is a keeping question: "is it ok to eat rice thats been in the fridge 3
# days", "can i eat leftover rice after 3 days", "cooked pasta in the fridge 5 days ok". The
# reading says so (`understood["kept"]`: the place it sat in and how long), and the rows that
# answer something else read one of the same words as their own - the fried-rice recipe takes
# "leftover rice", the warm-pot row takes "rice" and "in the fridge", the date-on-the-bag row
# takes "rice" and "ok to eat", and the chicken-nutrition row takes "chicken" and "eat". On main
# each of them answered that question. So when the line says a thing has been kept a while and
# asks if it is still good, only the rows that answer keeping are left to answer it.
_STILL_GOOD_ASHERS = frozenset((
    "ok", "okay", "safe", "eat", "eats", "eating", "drink", "use", "still", "good", "gone",
    "off", "bin", "throw", "edible", "risky"))


# The words a keeping row is keyed on. A row whose key holds one of them answers how long a thing
# lasts, what to do with it once it has lasted, or whether it is still fit to eat.
# What a keeping answer says, in the row's own words. A key word will not do: `babyfood-cheese` is
# keyed partly on keeping ("how long can i keep cheese for a baby") and answered a grown-up's
# "can i eat cheese thats been in the fridge for a month" with a weaning verdict the moment the
# appliance row stood down. The answer itself is the surest sign of the question it answers - it
# says how long the thing keeps, where to keep it, or to bin it - so that is what is read.
# The words a keeping row that builds its reply is keyed on.
_KEEPING_WORDS = frozenset((
    "keep", "keeps", "kept", "keeping", "last", "lasts", "store", "stored", "storage", "freeze",
    "frozen", "reheat", "reheated", "mouldy", "sour", "slimy", "stale", "gone", "date", "bin",
    "throw", "overnight", "left"))


# A keeping answer gives a length, and the commonest way it gives one is the plural verb: "Raw
# eggs keep about three weeks past the date on the box", "Carrots keep for weeks in the fridge".
# The phrase list above can only hold " keeps " and " keep it ", so a card that said "keep about"
# was not a keeping row at all: on a line saying how long a thing had been kept and asking if it
# was still good, `keep-eggs` stood down while a plan follow-up that turned the line down took it,
# and "is it ok to eat eggs thats been in the fridge 4 days" was the search hedge. Read the verb
# and the length it gives instead of the phrase.
_A_KEEP_AND_A_LENGTH = re.compile(
    r"\bkeep(?:s)?\s+(?:about|for|up to|until|till|roughly|around|no more than|"
    r"a day|a week|a fortnight|a month|a year|"
    r"two|three|four|five|six|seven|eight|ten|twelve|\d)")


# A word can name a colour and a thing at once - "orange" a fruit, "green" a vegetable, "brown" a
# way of cooking, "plum" a fruit - and an entry keyed on the thing is reachable from a line that
# only used the colour. "the sky was orange last night" was answered with the citrus keeping card,
# "Keep them a week or two in the bowl and a month in the fridge", because "orange" was the whole
# of what the line and that entry had in common. A shared word is not a subject, so a colour the
# line used as a colour is not one of the line's subject words.
COLOUR_WORDS = frozenset("""red orange yellow green blue indigo violet purple pink brown black white
    grey gray beige cream tan navy gold golden silver amber turquoise lilac mauve crimson scarlet
    burgundy maroon olive khaki teal cyan magenta peach coral rust blonde fair plum cherry lemon
    lime salmon rose chestnut copper ochre ebony ivory pearl""".split())
