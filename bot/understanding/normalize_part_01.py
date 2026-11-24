"""Part 1 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""
import re

from . import lexicon



# One word, and a measure stays one word: "1.5kg", "20%", "1,500" and "don't" are each a
# single token, so a weight is never read as "one" and "5kg".
# A short name with a number in it is one word too, because that is what it is to the person
# who typed it: "p60", "p45", "a1", "m25", "s21", "b12", "t4". Split into "p" and "60" the
# name is lost, so a knowledge entry keyed on it never matches and a question about it reads
# as a question about a number.
_MEASURE = (r"[0-9]+(?:[.,][0-9]+)*[a-z%]*"
            r"|[a-z]{1,3}[0-9]+(?:[a-z]{1,3}[0-9]*)*(?![a-z0-9])"
            r"|[a-z]+(?:'[a-z]+)*")


WORD = re.compile(_MEASURE)


# The chat words `_chat_words_said_out` spells out in `clean`: what people type, and the phrase
# a reader has to see to answer it.
SAID_OUT = {word: lexicon.CHAT[word]
            for word in lexicon.PLAIN_EXPANDS | lexicon.PLAIN_ONE_WORD
            if word in lexicon.CHAT and word not in lexicon.EXPAND}


# The chat spellings whose meaning is one ordinary word, and which are not a word themselves, are
# spelled out in `clean` too: a reader matching on the line as it was typed never met "tomorrow"
# in "is it gna rain tmoz", so the one line in eight that is typed this way reached a reader that
# was written for the words the person meant. The letters are kept as typed ("grade c", "vitamin
# c", "plan b") - the positional readers own those - and so are the spellings that are an
# ordinary word with a sense of their own: "the cause of the leak" is not "because of the leak",
# and "cos" is a lettuce. "owt" is kept because the reading already tells its two senses apart by
# the word after it - "is owt else wrong" is anything, "owt the door" is out - and folding it
# first turned "anything wrong with my car" into "out wrong with my car". Three more were measured
# and taken back out: "wif" is as often a wife as it is with ("my wif is due in july" was read as
# "your with is due"), "wtf" opening a line is an exclamation and not a question ("wtf is going on"
# stopped being "Really? Tell me what happened" and became the how-are-you reply), and a "pressie"
# for a named person is a gift for them, where "present" and "cheap" together reach the whip-round
# row ("wots a good cheap pressie for a 60 yr old woman" got the tenner-for-a-colleague answer).
CHAT_KEPT_AS_TYPED = frozenset("""
    u ur urs yr yrs urself y r n k b c d v x ar av sed prob cause cos tho owt
    wif wtf pressie pressies prezzie prezzies prezzy
    """.split())


CHAT_AS_ONE_WORD = {word: meaning for word, meaning in lexicon.CHAT.items()
                    if " " not in meaning and word not in CHAT_KEPT_AS_TYPED
                    and word not in SAID_OUT}


SAID_OUT.update(CHAT_AS_ONE_WORD)


RAW_WORD = re.compile(_MEASURE)


# What a repaired word may become: the emergency words themselves, plus the gerunds the case
# patterns read ("havin chest pains" is "having chest pains").
URGENT_WORDS = frozenset(lexicon.URGENT_MISSPELLINGS.values()) | frozenset(("having",))


_ANY_WORD = re.compile(r"[a-z]+(?:'[a-z]+)*", re.IGNORECASE)


# A clipped family word after a possessive, with the two words that follow it, so the guard
# that reads a thing of that name ("my ds wont charge", "my dd bra") still applies.
CLIPPED_FAMILY = re.compile(
    r"\b(?P<owner>my|our|his|her|their)\s+(?P<word>dd|ds|dh|mil|fil|sil|bil|oh|lo)\b"
    r"(?P<rest>(?:\s+[a-z']+){0,2})", re.IGNORECASE)


def _doubles_its_last_letter(word):
    """"get" gives "getting" and "throb" gives "throbbing": a one-beat word that ends in a
    consonant after a single vowel writes that consonant twice before -ing and -ed.

    Only the last syllable matters to English, and this has no way to hear the stress, so it
    asks for a word of one beat - "visit" and "open" are left alone, and so are words that end
    in a letter English never doubles ("fix", "play", "snow").
    """
    if len(word) < 3 or not word.isalpha():
        return False
    if word[-3] in "aeiou" or word[-2] not in "aeiou" or word[-1] in "aeiouwxy":
        return False
    return len(re.findall(r"[aeiou]+", word)) == 1


VOWEL_SET = frozenset("aeiou")


# A y does the work of an i in the words people misspell ("worryed" is "worried"), so the
# reader that hears one letter swapped for another has to count it as a vowel.
VOWEL_SET_OR_Y = VOWEL_SET | frozenset("y")


def _drops_a_final_e(word):
    """True for a word that loses its last e before an ending: "move" is "moving", "moved".

    Every word that ends in a silent e drops it before -ed and -er, so "agree" is "agreed",
    "free" is "freed", "eye" is "eyed" and "dye" is "dyed"; a word ending in "ee" keeps both
    letters only before -ing. That is the one ending the letter before the e is the whole
    question for ("seeing", "agreeing", "freeing"), and it is named in _keeps_its_e_before_ing:
    there is no rule in English that hears it.
    """
    return word.endswith("e") and len(word) > 2


def _keeps_its_e_before_ing(word):
    """True for a word whose "ee", "ye" or "oe" keeps both letters before -ing."""
    return len(word) > 2 and word.endswith(("ee", "ye", "oe"))


def _ing_form(word):
    """The -ing form of a word that ends in an e: "moving", "agreeing", "eyeing"."""
    return word + "ing" if _keeps_its_e_before_ing(word) else word[:-1] + "ing"


def _inflections(word):
    """The everyday forms of a word, so 'likes' and 'jeans' are not 'typos'."""
    out = set()
    if len(word) < 3 or not word.isalpha():
        return out
    # A y after a consonant is an i in every ending: "worry" is "worried", never "worryed", and
    # "worrys" is not a word either. Generating those forms put "worryed", "tryed", "copyed" and
    # "studys" in the lexicon, and a word the lexicon holds is a word the fixers may not touch -
    # so "im still worryed about it" could not be read as the feeling, and the person who typed
    # it got "Thanks for telling me" where the line as spelt right gets the worry answer.
    y_for_i = word.endswith("y") and word[-2] not in VOWEL_SET
    out.add(word + "ly")
    if not y_for_i:
        out.add(word + "s")
    if _doubles_its_last_letter(word):
        # "getting", "throbbing": the doubled form is the word, so the undoubled one is not.
        out.update((word + word[-1] + "ing", word + word[-1] + "ed", word + word[-1] + "er"))
    elif _drops_a_final_e(word):
        # "move" is "moving", not "moveing": the e goes before an ending that opens with a
        # vowel, and it was being written both ways, which put "moveing" in the lexicon as a
        # word of its own. It goes before -ed and -er either way ("agreed", "freed", "dyed"),
        # which is why only the -ing form asks about the letter before the e.
        out.update((_ing_form(word), word[:-1] + "ed", word[:-1] + "er"))
    else:
        out.add(word + "ing")
        if not y_for_i:
            out.update((word + "ed", word + "er"))
    if word.endswith("e"):
        out.update((word[:-1] + "ing", word[:-1] + "ed"))
    if word.endswith("y"):
        out.update((word[:-1] + "ies", word[:-1] + "ied", word[:-1] + "ier"))
    if word.endswith("s"):
        out.add(word[:-1])
    return out


_BASE = (
    lexicon.COMMON.split() + lexicon.CORE.split()
    + " ".join(lexicon.CHAT.values()).split()
    + " ".join(lexicon.EXPAND.values()).split()
    + " ".join(lexicon.MISSPELLINGS.values()).split()
    + " ".join(lexicon.REAL_WORDS).split()
)


BASE = frozenset(_BASE)


LEXICON = BASE | frozenset(f for word in _BASE for f in _inflections(word))


COMMON_RANK = {word: i for i, word in enumerate(lexicon.CORE.split() + lexicon.COMMON.split())}


# "me" where a possessive is meant, in the one shape the pass below cannot see.
#
# `possessive_me` already repairs most of British chat-speak's possessive "me" - "me sister is
# coming at the weekend", "wher me phone", "me car wont start", "me head is banging" - and it
# knows the words that make "me" the object instead ("she told me mum died" told me that Mum
# died, "give me car keys back" is the keys). Two shapes fall outside it:
#
#   "it does me head in"   "head" is not a kin word, so the idiom that ends in "in" - do someone's
#                          head in - was read as the pronoun and the line as an acknowledgement.
#   "doin me ed in"        the "h" is clipped, so the word after "me" is not a word at all and
#   "doin me ead in"       the repair stops at "me ead" -> "my ead".
#
# So this pass carries only those two, and asks the same question the other one asks: is the thing
# the end of the phrase? "me head in" and "me ed ..." close the phrase, "me head office" and
# "me ed office" do not, and nothing here touches a line `possessive_me` already reads.
# What may follow a "me" this file thinks is a possessive: a verb, a preposition, a joiner, an
# adverb, punctuation or the end of the line. A thing can go on naming a thing ("head office",
# "car keys"), and there the "me" is somebody's object, so that word is not in the list.
ME_FOR_MY_CLOSES = frozenset("""
    is are was were am be been being isnt arent wasnt werent aint
    has have had having got gets getting get
    will wont would could should can cant cannot must might may shall
    do does did doing done dont doesnt didnt
    hurts hurt hurting aches ache aching bangs bang banging throb throbs throbbing kills kill
    feels feel feeling looks look looking smells smell smelling sounds sound sounding seems seem
    needs need wants want keeps keep kept goes go going went comes come coming came broke broken
    breaks break stopped stops started starts works worked died dies dying
    in on out off up down at to for with from by about over under around through into onto
    and or but so because as than then
    not no never still too also just again now today tomorrow yesterday tonight anymore
    all both every any some
""".split())


# The words the topics name a thing by, kept by length so a slip is one scan of the words the
# right length. `topics` fills this at import: it reads this module, so the list cannot come the
# other way round, and the repair below needs it (see `_a_thing_a_letter_short`).
THING_WORDS_BY_LENGTH = {}


# The same vocabulary flat, for the question "does the reading already know this word".
THING_WORDS = set()


def learn_thing_words(words):
    """Keep the vocabulary the topics answer for, so a thing typed a letter short is read."""
    for word in words:
        if isinstance(word, str) and word.isalpha() and len(word) > 2:
            THING_WORDS.add(word)
            THING_WORDS_BY_LENGTH.setdefault(len(word), set()).add(word)


# Phrases that must be recognised before the words are looked at separately. Longest first.
PHRASES = sorted(
    {k: v for k, v in lexicon.CHAT.items() if " " in k or "/" in k or "&" in k}.items()
    | {k: v for k, v in lexicon.MISSPELLINGS.items() if " " in k}.items(),
    key=lambda item: -len(item[0]),
)


# Words a clause can start with that mean "new thought, same conversation".
BREAKS = frozenset(
    "anyway anyways btw actually instead otherwise also plus so but then oh ok okay right now "
    "still however meanwhile finally".split()
)


PRONOUN_BASES = frozenset(
    "i it that this there here he she we they who what where how when why everyone somebody "
    "someone nobody everybody one".split()
)


ASK_WORDS = frozenset(
    "what why how when where who which whose can could should would is are do does did will "
    "have has shall may might am was were".split()
)


WANT_WORDS = frozenset(
    "want need like looking help recommend suggest advice idea ideas tip tips know wonder "
    "thinking plan trying".split()
)


# An ask can hide in the middle of a run-on line: "my back hurts can i take ibuprofen",
# "im knackered all the time what could be wrong". These are the pieces that open one.
WH_WORDS = frozenset("what why when where who which whose".split())


AUX_WORDS = frozenset(
    "is are was were am do does did can could should would will shall have has may might".split()
)


# The be-forms: in front of a person they link a clause ("the thing is i do not know").
BE_WORDS = frozenset("is are was were am".split())


SUBJECT_WORDS = frozenset("i we you they he she".split())


HOW_DEGREE = frozenset(
    "long much many often old far big soon hot cold tall early late heavy deep".split()
)


# A clause opening with one of these is already being asked, not asking again.
NO_ASK_AFTER = frozenset("that if whether what why when where who which whose how".split())


# The only words that can come between a question word and its verb ("what time should i
# come", "how much does it cost", "which one should i buy"). Any other word there is a
# subject, and a question word in front of a subject is a relative clause: "the man who
# called was rude" and "the film which i saw" are statements, not questions.
ASK_NOUNS = frozenset("""time day date week month year kind sort type colour color size
amount number temperature age price reason way one ones much many long often far""".split())


# A reporting verb or a thought in front of the question word makes it what is being talked
# about, not what is being asked: "i know what to do", "she said why she left".
REPORTING = frozenset("""know knows knew known tell tells told say says said ask asks asked
wonder wondered wondering remember remembered forget forgot decide decided sure idea clue
mean means meant matter matters question doubt explain explains argue argued arguing
disagree disagreed discuss discussed debate debated talk talked mention mentioned
consider considered""".split())


# The same when a nominal and a copula come first ("that is what i meant", "the question is
# when to start"). The reporting verbs above already cover "we argued about who should pay".
COPULAS = frozenset("is are was were am be been being".split())


NOMINAL_BEFORE_COPULA = frozenset("""this that it there here all exactly precisely just
question thing problem point issue doubt reason answer part bit main only also still really
actually probably""".split())


# A determiner, then a noun, then "who/which/whose" is a relative clause that names the thing
# rather than asking: "a present for my mum who is in hospital", "the man who called was
# rude". These are the words that can open that nominal.
DETERMINERS = frozenset("""a an the my your his her our their its this that these those
some any no every each another anyone everyone someone nobody people ones""".split())


RELATIVE = frozenset("who which whose".split())


# "who should i see", "which do i pick": the relative word is followed by an auxiliary and a
# subject, so it is an inverted question about the thing named before it, not a clause about it.
RELATIVE_ASKS = frozenset("could can should would will shall do does did".split())


FREQUENT = frozenset((lexicon.CORE + " " + lexicon.COMMON).split()[:420])


AEIOU = frozenset("aeiou")


VOWELS = "aeiou"


def _double_variants(word):
    """Words one doubled-letter change away ("recomend" -> "recommend", "untill" -> "until")."""
    out = set()
    for i, char in enumerate(word):
        if char in VOWELS + "y":
            continue
        if i + 1 < len(word) and word[i + 1] == char:
            out.add(word[:i] + word[i + 1:])          # un-double: untill -> until
        else:
            out.add(word[:i] + char + word[i:])        # double: recomend -> recommend
    return out


def _a_doubled_letter_typed_once(word):
    """Words made by writing one of this word's letters twice: "wek" -> "week".

    The vowel is left out of `_double_variants` because most of the time it is the consonant
    that doubles ("recomend"), and a doubled vowel is rarer still - but "wek", "kep" and "cok"
    are the same slip, and a vowel is what the writer left one of.
    """
    out = set()
    for i, char in enumerate(word):
        if char.isalpha():
            out.add(word[:i] + char + word[i:])
    return out


def _three_of_a_letter(word):
    """Whether one letter runs three times together, which no English word does.

    The lexicon works a word's endings out, so a word that already ends in the letter an
    ending opens with comes back with three of them: "tell" + "ly" is "tellly", "full" + "ly"
    is "fullly". Nobody types those, so three together is the mark of a word the endings made
    rather than a word, and a spelling is never bent towards one.
    """
    return any(word[at] == word[at + 1] == word[at + 2] for at in range(len(word) - 2))


def _doubled_letter_words(word):
    """The words a doubled letter would make of this one, and that the lexicon knows.

    Only for a word the lexicon does not have: an ending of a word is a word of its own
    ("planed" is not "planned"), and the lexicon's "mattres" is a plural rule run backwards
    off "mattress", so a candidate that is a word only because a word ending in -ss lost an s
    is not a word at all. That guard is what stops "matres" being read as "mattres".
    """
    if word in LEXICON:
        return []
    return [w for w in _a_doubled_letter_typed_once(word)
            if (w in BASE or (w in LEXICON and w + "s" not in BASE))
            and not _three_of_a_letter(w)]


def _ie_variants(word):
    """Words one ie/ei swap away ("recieve" -> "receive")."""
    out = set()
    for pair, other in (("ie", "ei"), ("ei", "ie")):
        start = word.find(pair)
        while start != -1:
            out.add(word[:start] + other + word[start + 2:])
            start = word.find(pair, start + 1)
    return out


# An s in front of one of these is how English words do begin ("street", "sprint", "shrug"),
# so a run of consonants that opens with one of these pairs is a shape of its own and nothing
# is missing from it.
S_CLUSTERS = "tpskmlnwhqc"


def _missing_vowel(word):
    """The words a vowel left out of the middle of a long word would make: "daughtr" ->
    "daughter", "brthday" -> "birthday", "bicycl" -> "bicycle".

    A vowel is the letter people leave out of the middle of a word they are typing fast, and
    none of the repairs the reader already has can put one back. The new vowel has to sit in a
    cluster of three or more consonants ("daughtr" has "ghtr", "brthday" has "brth"), because
    that is the shape English does not have and the vowel is the sound that is missing from it.
    Two consonants are every sound a word needs ("martin", "statin", "toast") and a cluster
    that opens with an s is English of its own ("street", "sprint"), so a vowel is never put
    there; that is what keeps a name a name and a drug a drug.

    Only a word of five letters or more is tried, and only one the lexicon does not know, so a
    real word is never touched: below five there is no room left for a misspelt word to be told
    from a real one ("thnks" is "thanks"; "thnk" is a keystroke and a word). The caller keeps
    the repair only when exactly one word of the lexicon fits.
    """
    if len(word) < 5 or word in LEXICON:
        return ()
    out = set()
    for i in range(1, len(word) + 1):
        start = i
        while start > 0 and word[start - 1] not in VOWELS:
            start -= 1
        end = i
        while end < len(word) and word[end] not in VOWELS:
            end += 1
        cluster = word[start:end]
        if len(cluster) < 3 or (cluster[0] == "s" and cluster[1] in S_CLUSTERS):
            continue
        for vowel in VOWELS:
            candidate = word[:i] + vowel + word[i:]
            if candidate in BASE:
                out.add(candidate)
    return out


def _extra_vowel(word):
    """The words a vowel typed next to another vowel would make: "radiatior" -> "radiator".

    People adding a vowel where two already meet ("ie", "ei", "io", "ue") is the one extra
    letter worth undoing: "radiatior", "cookeing". Only a long word is tried, because the
    short ones this would bend are words in their own right ("seing" is one letter from "sing",
    "seizing" from "sizing"), the last letter is never taken, because it is what makes
    "breathe" a verb and "breath" a noun, and only an e or an i is removed, which is what
    people insert. The caller keeps only the candidates the lexicon knows, and only when
    exactly one fits.
    """
    if len(word) < 8:
        return ()
    out = set()
    for i, char in enumerate(word):
        if char not in "ei" or i + 1 == len(word):
            continue
        before = word[i - 1] if i else ""
        after = word[i + 1]
        if before in VOWELS or after in VOWELS:
            out.add(word[:i] + word[i + 1:])
    return out


_A_WORDS = frozenset("cola tuna mocha salsa karma pasta data area idea".split())


def _a_said_for_an_ending(word):
    """The words an -er, -or, -ar or -ow said as a would make: "propa" -> "proper", "winda" -> "window".

    A last syllable nobody stresses comes out as an a when people write the way they talk
    ("propa", "showa", "brotha", "plumba", "docta", "simila", "winda", "narra"), and none of
    those is a word, so the lexicon can say what was meant: "my winda wont shut" was read as a
    line about nothing while the word spelled right gets the window answer. Only a word of four
    letters or more that ends in an a after a consonant is tried, so a real word ending in an a
    ("sofa", "pizza", "idea") never reaches the guess - it is in the lexicon and fix_typo stops
    there - and the few real words that are not are held below.
    """
    if word in _A_WORDS:
        # A real word that happens to end in an a: "cola" is a drink, not a colour.
        return ()
    if word.endswith("as") and len(word) >= 5:
        # "the windas wont shut" is the same guess with the plural still on it.
        stem, plural = word[:-2], "s"
    elif word.endswith("a") and len(word) >= 4:
        stem, plural = word[:-1], ""
    else:
        return ()
    if stem[-1:] in VOWELS:
        return ()
    return tuple(stem + ending + plural for ending in ("er", "or", "ar", "ow"))


def _dropped_letter(word):
    """The words a missing w would make: "kno" -> "know", "thro" -> "throw", "shado" -> "shadow".

    Only a w is put back. It is the letter people leave out of a word and never hear missing
    ("know", "throw", "shadow", "answer"), so the repair cannot turn a real word into another
    one the way a general dropped letter can; the caller keeps only the candidates the lexicon
    knows, which is what makes "kno" safe.

    A word with a w already in it keeps one: "the windo wont shut" was read as a word the reader
    did not know, so the window that will not shut was answered "Right. What have you tried so
    far?" instead of the card. The w people leave off the end is the same w wherever the other
    one sits, and the candidate still has to be a word of the lexicon, so the guard is on the
    letter the repair would add rather than on the word ("window", "willow").
    """
    if len(word) < 3 or word.endswith("w"):
        return ()
    return (word + "w",)


def _an_ing_said_as_n(word):
    """The -ing form typed with the i and the g both gone: "gettn" -> "getting".

    A word ending in three letters that are all consonants and the last of them an n is an -ing
    with nothing left of the ending but the n: "forgettn", "gettn", "sittn", "chattn". The shape
    is what makes it safe - no English word ends that way, because a syllable needs a vowel - so
    a word that has one in its last three letters ("basin", "satin", "salmon") is left alone
    even when it is not in the lexicon, and one the lexicon holds is never reached at all.

    The verb under it may double its last letter ("get" -> "getting", "sit" -> "sitting"), so
    both spellings are tried and the caller keeps the one the lexicon knows.
    """
    if (len(word) < 5 or not word.endswith("n") or word in LEXICON
            or word in lexicon.COMMON_NAMES):
        return None
    if any(char in VOWELS for char in word[-3:-1]):
        return None
    stem = word[:-1]
    forms = [stem + "ing"]
    if len(stem) > 1 and stem[-1] == stem[-2]:
        forms.append(stem[:-1] + stem[-1] + "ing")
    known = {form for form in forms if form in LEXICON}
    if len(known) == 1:
        return known.pop()
    return None


def _a_leading_h(word):
    """The word an h put back on the front would make: "eadache" -> "headache", "eart" -> "heart".

    An h at the front of a word is the letter people say and never hear, so it is the one that
    goes missing when somebody types the way they talk: "iv got a bad eadache", "my eart is
    racing", "the ouse is freezing", "i need an ospital". Only the front is tried, only a word
    that opens on a vowel, and the caller keeps only candidates the lexicon knows - which is what
    makes it safe: "eadache" is one letter from "earache" as well, and that repair reached the
    earache card, so the h is the shorter path to the word the line is about. A word the lexicon
    holds never arrives here ("edge", "and", "am" are words), and a word of three letters is
    left alone because "ed" and "ed" are not a slip of anything the bot should answer with.
    """
    if len(word) < 4 or word[:1] not in "aeiou":
        return ()
    if word.endswith("s") and word[:-1] in BASE:
        # A plural is a word of the deck's own: "18 year olds" is not "18 year holds", and it
        # is the one line of the whole deck this repair would otherwise reach.
        return ()
    return ("h" + word,)


# The few real words that keep the e before -ing: dyeing a dress is not dying, and singeing
# hair is not singing. Each one sits exactly where the repair below would put it, so they are
# named rather than left to the candidate count.
E_KEPT_WORDS = frozenset({"dyeing", "singeing", "tingeing", "swingeing"})


def _e_kept_before_ing(word):
    """The word an e kept before -ing would make: "moveing" -> "moving", "takeing" -> "taking".

    A verb that ends in an e drops it before the ending, and a fast typist writes it anyway.
    Only this ending is tried, because it is the one where the letter before the e decides
    whether the e stays ("seeing", "freeing", "canoeing" all keep it) and that is a rule the
    reader cannot hear - so the candidate has to be a word the lexicon knows and it has to be
    the only one. The four real words that do keep the e are named above.
    """
    if len(word) < 6 or not word.endswith("eing") or word in E_KEPT_WORDS:
        return ()
    shorter = word[:-4] + "ing"
    return (shorter,) if shorter in LEXICON else ()


def _swapped_pair(word):
    """The words swapping two letters typed the wrong way round would make, or ().

    "collasped" is "collapsed" with the p and the s the wrong way round, and that is how a word
    comes out when two keys are hit in the wrong order. Only a long word is tried, and the caller
    keeps the candidates the vocabulary knows and only one of them: "trail"/"trial" and
    "form"/"from" are both real words, so they never reach here, and a word with two fittings is
    left alone. Five letters is the floor, the same as the vowel reader's: "hpone" is "phone",
    and a word the bot's own answers write is not a slip at all.
    """
    if len(word) < 5 or _a_word_the_bot_writes(word):
        return ()
    out = set()
    for at in range(len(word) - 1):
        pair = word[at:at + 2]
        # Two consonants typed the wrong way round ("collasped"): a vowel in the pair is how a
        # real word becomes a different real word ("overdoes" is not "overdose", "form" is not
        # "from"), and those stay with the curated tables.
        if len(pair) < 2 or pair[0] == pair[1]:
            continue
        if pair[0] in VOWELS or pair[1] in VOWELS:
            continue
        out.add(word[:at] + word[at + 1] + word[at] + word[at + 2:])
    return out


def _two_letters_the_wrong_way_round(word):
    """The words swapping two letters typed the wrong way round would make, vowels included:
    "brithday" -> "birthday", "cra" -> "car", "aeg" -> "age", "paekd" is not one.

    This is the same slip `_swapped_pair` reads, without its two limits: that one wants a long
    word and two consonants, because in a real word a vowel pair is how one word becomes
    another ("form" is not "from", "trail" is not "trial"). Neither limit is needed when the
    typed word is not a word at all, which is what this is for: a person typing fast puts two
    keys down in the wrong order, and half the time one of them is a vowel ("brithday",
    "taht", "hte", "aeg"). Everything the lexicon holds is left alone, and the caller keeps the
    repair only when exactly one word fits, so a slip with two readings ("cra" is one swap from
    "car" and from "arc") is left as it was typed.
    """
    if len(word) < 5 or word in LEXICON or _a_word_the_bot_writes(word):
        return ()
    out = set()
    for at in range(len(word) - 1):
        pair = word[at:at + 2]
        if pair[0] == pair[1]:
            continue
        # A pair with two consonants is `_swapped_pair`'s job ("collasped"), and a pair with two
        # vowels is a slip the curated map has ("recieve"). One vowel and one consonant is the
        # shape left over: "brithday" for "birthday", "caesr" for "caesar", "cehst" for "chest".
        if (pair[0] in VOWELS) == (pair[1] in VOWELS):
            continue
        made = word[:at] + pair[1] + pair[0] + word[at + 2:]
        if made not in NO_SWAP_TO:
            out.add(made)
    return out


# Words a swapped pair may not be repaired to. "hagned" is one swap from "hanged" and from
# nothing else the bot reads, and a person who writes it almost always means "hung": the repair
# would not fix the line, it would put a confident wrong word in the bot's mouth ("hagned my
# washing out" became "hanged my washing out"), which is worse than the slip it started with.
NO_SWAP_TO = frozenset(("hanged",))


_A_WORD_THE_BOT_WRITES = None


def _words_the_bot_writes():
    """Every word the knowledge base's own keys and answers use, worked out once.

    The guard on a swapped pair is "only read a word the reader does not know as a word", and
    LEXICON cannot answer that on its own: it is the base words and the forms made from them, not
    a dictionary, so "stain", "order", "paper", "spilt" and "matters" are not in it and each is
    one swap from a word it does hold ("satin", "roder", "apper", "split", "mattres"). Read that
    way, the reader bent 138 of the deck's own lines.

    The knowledge base cannot make that mistake: its keys and answers are written by the bot, so
    every word in them is well spelled by construction - the same reasoning `tools/typo_scan.py`
    gives for scanning them. Asking it is a lazy import because the answer modules import it
    anyway, and the result is held: one build a process, about a second, and nothing after that.
    """
    global _A_WORD_THE_BOT_WRITES
    if _A_WORD_THE_BOT_WRITES is None:
        words = set()
        try:
            from bot.knowledge import entries as knowledge_entries
            from bot.knowledge import lookup as knowledge_lookup
            for entry in knowledge_entries():
                for field in ("reply", "ask", "key", "id", "domain"):
                    value = getattr(entry, field, "")
                    for text in (value if isinstance(value, (list, tuple, set)) else [value]):
                        if isinstance(text, str):
                            words.update(knowledge_lookup.tokens(text))
            _, _, known = knowledge_lookup._vocabulary(knowledge_entries())
            words.update(word for word in known if isinstance(word, str))
        except Exception:                     # the reading must stand up on its own
            pass
        _A_WORD_THE_BOT_WRITES = frozenset(
            word.lower() for word in words if word.isalpha())
    return _A_WORD_THE_BOT_WRITES


def _a_word_the_bot_writes(word):
    """Whether the knowledge base writes this word as it stands, so it is not a slip."""
    if word in lexicon.TYPED_WORDS or word in lexicon.COMMON_NAMES:
        return True
    return word in _words_the_bot_writes()


def _bones(word):
    """The consonants of a word, in order: "collapsed" and "collpsd" are both "cllpsd"."""
    return "".join(char for char in word if char not in VOWELS)


def _longest_consonant_run(word):
    """The longest stretch of letters in a word with no vowel in it.

    A vowel typed past closes a gap and leaves a run behind - "collpsd" has "psd", "bleedng"
    has "dng" - and an ordinary word hardly ever has three consonants in a row. That is what
    tells a typo from a word: "balding" and "sizing" are only two ("ld", "ng"), and they are
    words, so they must not be read as "bleeding" and "seizing" (the same bones).
    """
    run = best = 0
    for char in word:
        if char in VOWELS or char == "y":
            run = 0
        else:
            run += 1
            if run > best:
                best = run
    return best


URGENT_BONES = {}


def _an_emergency_word_left_out(word):
    """The emergency word this is with its vowels typed past, or None.

    A frightened person types fast, and the vowels are what goes: "my mum collpsd". A letter
    left out is the one typo the engine does not otherwise guess at, because a word one letter
    short of another is usually the other word - but here the only words consulted are the
    emergency vocabulary itself (lexicon.URGENT_MISSPELLINGS' values), and only when exactly
    one of them has the same consonants in the same order. "cllpsd" is "collapsed" and nothing
    else; a word whose bones fit two of them is left for the curated table.

    The word also has to look like a vowel was left out: three consonants in a row. Without
    that guard the same bones bend ordinary words into emergencies - "balding" is "bleeding"
    and "sizing" is "seizing" - and a person talking about their hair got the bleeding card.
    """
    if len(word) < 6 or word in LEXICON or _longest_consonant_run(word) < 3:
        return None
    if not URGENT_BONES:
        for known in URGENT_WORDS:
            URGENT_BONES.setdefault(_bones(known), []).append(known)
    found = [known for known in URGENT_BONES.get(_bones(word), ()) if len(known) > len(word)]
    return found[0] if len(found) == 1 else None


# The words a name comes after: "my brother is called crispin". A word there is a name, and a
# name is not a slip. A bare "call" is not one of them, because "call mi later" is a pronoun
# with the letters left out, not somebody's name.
NAME_FRAMES = frozenset("called named".split())


# The chat-speak word that is also a name. "kay" is typed for "ok" ("kay thanks") and it is
# also a name, and where a name goes the name is the reading that matters. Read as "ok", every
# line that gave a name came back wrong: "call me ok", "i go by ok", "my names ok", and "im not
# kay" - a person saying which name is not theirs - earned "Sorry to hear that. A walk and
# someone to talk to usually help more than sitting with it", the answer to feeling low.
CHAT_NAMES = frozenset(word for word in lexicon.CHAT if word in lexicon.COMMON_NAMES)


# The words a name follows when the line is about what somebody is called: the verbs that
# introduce one, the pronouns that carry it for a person who has just said it ("what shall i
# call you" - "call me kay"), and "i am", which is how a name is given.
NAME_ROLL = frozenset("""names name named go goes going by im am i'm""".split())


# The verbs a name is given after: "call me kay", "call u kay". Only these take the pronoun that
# carries a name, because "text me kay" is "text me, ok?" - the tag at the end of an ask, not a
# name - and the ask that the bot cannot send a text is the answer the line wants.
NAME_CALLS = frozenset("""call calls called calling callin name names named""".split())


def _dropped_g(word):
    """The -g people leave off a typed word: "doin" -> "doing", "mornin" -> "morning".

    Only when the word is not one the lexicon knows and the form with the g is, so a real
    word is never changed. The lexicon is missing ordinary -in words ("satin", "raisin"), so
    those are named in lexicon.REAL_IN: "a satin dress" must not read as "a sating dress".
    """
    if (len(word) < 4 or not word.endswith("in") or word in LEXICON
            or word in lexicon.REAL_IN or word in lexicon.COMMON_NAMES):
        return None
    longer = word + "g"
    if longer in LEXICON:
        return longer
    # "movein" is "moving": the g is not the only letter missing, because the e goes as well.
    stem = word[:-2]
    if _drops_a_final_e(stem) and len(stem) > 2:
        dropped = _ing_form(stem)
        if dropped in LEXICON:
            return dropped
    # A verb that doubles its last letter, written with one or with two: "getin" and "gettin"
    # are both "getting". The doubled spelling has to be proved a word, so the lexicon has to
    # carry it - which is what _inflections writes for a word of one beat. The verb under it
    # has to be a word too: "stalin" is one letter from a doubled -ing and "stal" is nothing,
    # so the name stays a name ("who was stalin" read as "who was stalling" and lost its
    # answer once the words a line is read by carried the repair).
    stem = word[:-2]
    if len(stem) > 3 and stem[-1] == stem[-2]:
        stem = stem[:-1]
    if _doubles_its_last_letter(stem) and (stem in BASE or stem in LEXICON):
        doubled = stem + stem[-1] + "ing"
        if doubled in LEXICON:
            return doubled
    return None


# The ones the quantifier is built on: "anyfing", "sumfing", "evryfing", "nuffing". The
# whole class is these four words and the spellings of their first half, so the repair is a
# closed list of stems rather than a guess at what a stopped th might have been. Nothing else
# in English ends in "fing" except words the lexicon already holds ("stuffing", "proofing").
STOPPED_TH_STEMS = {
    "any": "anything", "eny": "anything", "ani": "anything",
    "some": "something", "sum": "something", "som": "something", "sumn": "something",
    "every": "everything", "evry": "everything", "evrey": "everything",
    "nuf": "nothing", "nuff": "nothing", "nof": "nothing", "noff": "nothing",
    "nut": "nothing", "nuth": "nothing", "not": "nothing", "no": "nothing",
}


def _stopped_th(word):
    """The -thing word a stopped th is said as: "anyfing" -> "anything", "nuffing" -> "nothing".

    Th-stopping ("thing" said as "fing") is regular in several of the accents people type in,
    so it is a spelling a reader has to expect: "anyfing i can do at lunch" was read as nothing
    in particular and answered with the stock line about a hard day. Only a word the lexicon
    does not hold is touched, and only the four -thing words are reachable, so a line about
    "stuffing" or "waterproofing" is left alone.

    The same accents drop the g and the th: "nuffin", "anyfink" and "sumfin" are the same word
    typed three ways, and people write all three, so the ending is not just "fing". The stem
    still has to be one of the handful people write, which is what keeps "muffin", "puffins",
    "griffins" and "thinking" out: no real word is built from one of these stems.
    """
    if len(word) < 5 or word in LEXICON:
        return None
    for suffix in ("fings", "fing", "finks", "fink", "fins", "fin"):
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            break
    else:
        return None
    plural = suffix.endswith("s")
    found = STOPPED_TH_STEMS.get(stem)
    return found + "s" if found and plural else found


# The common words with the /shun/ sound that are not spelt -tion, so "fashun" is a fashion
# and not a fation. Anything outside this list is a -tion word, which is the overwhelming
# majority of the sound in English. The -ssion, -sion and -cian words are here because the
# repair has to tell them apart from the -tion ones: "mishun" is a mission and not a mition.
SHION_WORDS = frozenset("""
cushion fashion passion mission session version decision occasion discussion permission
television conclusion explosion confusion illusion vision revision division provision
suggestion tension expression compassion impression profession possession aggression
admission commission expansion extension pension mansion excursion invasion collision
emission transmission procession succession confession depression digression obsession
recession concession progression exclusion inclusion seclusion precision derision
magician musician electrician politician technician physician statistician optician
beautician mathematician paediatrician dietician clinician""".split())


# The th sound typed as an f in a word too short for the rule below: the little words, which
# carry a line whatever else is in it. Each f spelling here is not a word of its own, so reading
# one cannot take a word away from the person.
F_TYPED_FOR_TH = {
    "fe": "the", "fis": "this", "fey": "they", "fem": "them", "fere": "there",
    "fing": "thing", "fings": "things", "fird": "third",
    "fousand": "thousand", "fousands": "thousands",
    "freat": "threat", "freaten": "threaten", "freatens": "threatens",
    "freatened": "threatened", "freatening": "threatening",
}


# A word for a person or a thing, typed as the little word that sounds like it. "wif" is
# "with" in "going wif my mum", but in the place a person's name goes it is the wife: "my wif
# is due in july" was said back as "your with is due in july". Read where the line is read, not
# here - the chat table below owns "wif" and "wiff" for every other place.
A_THING_TYPED_AS_A_LITTLE_WORD = {
    "wif": "wife",
    "wiff": "wife",
}


# The words that fill the place a person or a thing goes. "a" is not one of them: "a wiff of
# smoke" is the wh word, and a thing of the person's is always "my", "our", "the" or a name.
A_THING_GOES_AFTER = frozenset("the".split())


def _short_double(word):
    """A short word typed with a doubled letter: "hii" -> "hi", "okk" -> "ok", "byee" -> "bye".

    Words under four letters used to be left alone, and they are where most of the one-word
    replies live. Only an un-doubled form that is a frequent word is taken, and only for a
    word the lexicon does not know, so "all" and "off" are never touched.
    """
    if len(word) < 3 or word in LEXICON:
        return None
    variants = _double_variants(word)
    if word[-1] == word[-2]:
        variants.add(word[:-1])              # a vowel too: "hii" -> "hi", "noo" -> "no"
    keep = [variant for variant in variants
            if variant in LEXICON and variant in FREQUENT]
    keep.sort(key=lambda variant: COMMON_RANK.get(variant, 10 ** 6))
    return keep[0] if keep else None


def _one_letter_apart(word, other):
    """True when `word` is `other` with one letter added, left out, swapped round or replaced
    by another vowel: the shapes people type at speed ("knackerd", "exausted", "nerveus")."""
    if abs(len(word) - len(other)) > 1:
        return False
    if len(word) == len(other):
        differ = [i for i in range(len(word)) if word[i] != other[i]]
        if len(differ) == 1:
            i = differ[0]
            return word[i] in VOWEL_SET_OR_Y and other[i] in VOWEL_SET_OR_Y
        if len(differ) == 2:
            i, j = differ
            return j == i + 1 and word[i] == other[j] and word[j] == other[i]
        return False
    short, long = (word, other) if len(word) < len(other) else (other, word)
    i = 0
    while i < len(short) and short[i] == long[i]:
        i += 1
    if i == len(short):
        # A letter on the end of a whole word is how a word grows, not how a typo looks:
        # "scare" + "d" is "scared" and "guilt" + "y" is "guilty", so "dont scare me" and
        # "guilt tripping me" would become feelings they are not. Only a letter inside counts.
        return False
    if short[i:] != long[i + 1:]:
        return False
    if word is long:
        # A letter typed into a word only makes it a stretch when it is a vowel: people hold a
        # vowel, and they drop or swap letters, but a consonant typed into a feeling word is
        # usually another word altogether - "gland" is not "glad", "strain" is not "train".
        return long[i] in VOWEL_SET
    return True


# The everyday verbs a line puts straight after its subject, as people say them. A closed list,
# so a letter out of place in one of them has one reading, and nothing else in the language is
# one edit from it.
CORE_VERBS = frozenset("""take get give make have go do say see know think want need feel look
    come wake walk work eat drink buy pay keep leave sleep live start stop try help tell ask
    call find bring wear watch read cook clean wash sit stand run drive ride""".split())


# The particles a verb of a line takes straight after it ("wake up", "get off", "give in"): where
# one stands, the word before it is the verb, and a vowel out of place in that word is read.
AFTER_A_VERB = frozenset("up off out in on back over down away".split())


# Where the verb of a line stands: right after its subject ("i tke the bus to work", "we gte
# home at 6", "they wke up early"). A subject is what says the word after it is the verb and not
# a name or a thing. "to" and "and" were tried as places as well and were taken back out: they
# put a repaired verb into a line that read fine without it, and "i wake up and mak coffee" moved
# off the coffee card and onto the buffet one.
BEFORE_A_VERB = frozenset("i we they you he she".split())


def _one_letter_wrong(word, other):
    """True when one letter added, left out, swapped with its neighbour or typed for another
    makes `other` out of `word`.

    `_one_letter_apart` says the same thing for feelings and parts, with two limits that are
    right there and wrong here: a letter typed *into* a word only counts when it is a vowel,
    and a letter typed *for* another only when both are vowels. Those limits keep "gland" from
    being "glad"; next to a closed list of the commonest verbs there is nothing to confuse it
    with, so any letter counts.
    """
    if abs(len(word) - len(other)) > 1:
        return False
    if len(word) == len(other):
        differ = [i for i in range(len(word)) if word[i] != other[i]]
        if len(differ) == 1:
            return True
        if len(differ) == 2:
            i, j = differ
            return j == i + 1 and word[i] == other[j] and word[j] == other[i]
        return False
    short, long = (word, other) if len(word) < len(other) else (other, word)
    i = 0
    while i < len(short) and short[i] == long[i]:
        i += 1
    return short[i:] == long[i + 1:]


def _a_word_the_reading_knows(word):
    """Whether the topics' vocabulary or the lexicon already holds this word or a form of it.

    "seeding" is not in the lexicon as it stands, and the bot does not write it, so a repair
    read it as "seedling" - a word bent into a different word, in a line about a lawn. The
    word, its stem and its everyday endings are asked, because the lexicon holds base words
    and the topics hold the names of things ("seed" is a seed, "seeds" and "seeded" are forms
    of it).
    """
    if _known_word(word):
        return True
    return any(_known_word(stem) for stem in _stems_of(word))


def _known_word(word):
    """Whether one word is held by the lexicon or by the topics' vocabulary."""
    return word in LEXICON or word in THING_WORDS


def _stems_of(word):
    """The words `word` could be an everyday ending of."""
    stems = set()
    if word.endswith("ing") and len(word) > 5:
        stems.update((word[:-3], word[:-3] + "e"))
    if word.endswith("ed") and len(word) > 4:
        stems.update((word[:-2], word[:-1]))
    if word.endswith("es") and len(word) > 5:
        stems.add(word[:-2])
    if word.endswith("s") and len(word) > 4:
        stems.add(word[:-1])
    return stems


def _a_thing_a_letter_short(word):
    """The thing `word` is one letter short of, or None when none or two fit.

    The same reading as `_a_core_verb_typed_wrong`, with the topics' own vocabulary as the
    closed list: a letter left out of a thing's name is the commonest slip in a line about a
    thing ("my fidge is broken", "my frige is making a noise", "how do i check my raiator"),
    and next to a list of things there is little to confuse it with. Eight household and garden
    words typed a letter short reached no card on main: "my fidge is broken" got "That would
    bother me too. Tell me what it does", "how do i clean my frige" and "how do i clean my
    caret" got the search shrug, "my biler is broken" got "Right. What have you tried so far?",
    "how do i check my raiator" and "how often should i water my grss" got "I don't know enough
    to answer that honestly", and "my feezer is frosting up" got "I'm listening — say more if it
    helps."

    The caller has already refused a real word and a name, so what is left is a word nothing
    knows. Two things one letter away still say nothing ("roter" is a router and a roster),
    which is the tie rule everywhere else.

    The letter put back is one left out of the middle, never one on either end: a letter on the
    end of a whole word is how a word grows, not how a typo looks. "repeat that step by step"
    was read as "steps" and the follow-up that repeats the last answer fell to the search
    shrug, and "wols" was read as "wools" - both a word of its own bent into a longer one.
    "step" is not in the lexicon as it stands, so the guard against a real word did not catch
    it; keeping the first and last letter does, and none of the repairs above loses one.

    A word the reading knows somewhere else is not a word missing a letter. The lexicon is a
    curated subset and not a dictionary, so the guard against a real word let 63 of the deck's
    own 9,580 words through as "slips": "on fire" became "on fibre" and lost the 999 answer,
    "we have mice" became a bolognese, "my bother", "the plans", "it moves" and "the tables"
    were bent as well. Every one of them is a word the bot writes in its own answers, or a form
    of one the topics name ("seeding" is a seed), so the reading asks both before it bends
    anything - the same guard `_a_core_verb_typed_wrong` has always had.
    """
    if len(word) < 4:
        return None
    if _a_word_the_bot_writes(word) or _a_word_the_reading_knows(word):
        return None
    fits = [w for w in THING_WORDS_BY_LENGTH.get(len(word) + 1, ())
            if w[0] == word[0] and w[-1] == word[-1] and _one_letter_wrong(word, w)]
    return fits[0] if len(fits) == 1 else None


def _a_core_verb_typed_wrong(word, before, after=None):
    """The everyday verb `word` is one letter away from, right after a subject, or None.

    "i tke the bus to work" was answered "I'm listening", "i gte home at 6" and "i hav a shower
    then work" the same, "i mak dinner at 7" nothing at all; "i wek up at 6 every morning" came
    back as "You week up at 6 every morning", because the corrector had a spelling to guess at
    and this word has a reading from where it sits. The word being read is not in the lexicon
    and is not a name, and one letter out of place in "take", "get", "have" or "make" is that
    word: nothing else in the language is one edit from exactly one of them.
    """
    if not word.isalpha() or len(word) < 3 or len(word) > 7:
        return None
    if before not in BEFORE_A_VERB:
        return None
    if word in LEXICON or word in lexicon.COMMON_NAMES or word in _words_the_bot_writes():
        return None
    found = {verb for verb in CORE_VERBS if _one_letter_wrong(word, verb)}
    if word.endswith("d"):
        # A d at the end of the word is the d of an ending, not a letter typed where another
        # one belongs: "askd" is "asked" with the e left out and "wantd" is "wanted". Cutting
        # the d off is a slip the corrector already knows ("_missing_e"), and reading it here
        # as the verb with its last letter gone turned "she askd me to leave" into "she ask".
        found.discard(word[:-1])
    if not found and after in AFTER_A_VERB:
        # A vowel typed wrong is the same slip as a letter out of place, and it is the one the
        # corrector cannot see: "i wek up at 6 every morning" came back as "You week up at 6
        # every morning", because "wek" is one letter from the noun "week" while the verb it was
        # meant to be has its consonants and its vowels wrong ("wake"). Right after a subject,
        # and with the particle the verb takes after it ("up", "off", "out"), the consonants are
        # what is left of the word: only a core verb whose consonants are these, and which is no
        # more than one letter longer, is read. The particle is what keeps "i wak to work" as it
        # was typed, where the word could have been "walk" and a reading of "wake" is a guess.
        found = {verb for verb in CORE_VERBS if _its_vowels_typed_wrong(word, verb)}
    if len(found) == 1:
        return found.pop()
    return None


def _its_vowels_typed_wrong(word, other):
    """True when `other` is `word` with a vowel (or a whole syllable) typed wrong."""
    if word == other or word[0] != other[0] or not other.startswith(word[0]):
        return False
    if abs(len(word) - len(other)) > 1:
        return False
    consonants = "".join(letter for letter in word if letter not in "aeiou")
    return consonants and consonants == "".join(letter for letter in other if letter not in "aeiou")
