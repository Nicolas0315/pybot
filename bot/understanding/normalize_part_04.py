"""Part 4 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""

from . import lexicon
from .normalize_part_01 import (
    CLIPPED_FAMILY, URGENT_WORDS, _ANY_WORD, BE_WORDS, CHAT_NAMES, LEXICON, NAME_CALLS, NAME_FRAMES,
    NAME_ROLL, A_THING_GOES_AFTER, A_THING_TYPED_AS_A_LITTLE_WORD, VOWELS, _one_letter_apart, BASE,
    COMMON_RANK, _a_leading_h, _a_said_for_an_ending, _a_thing_a_letter_short,
    _an_emergency_word_left_out, _an_ing_said_as_n, _double_variants, _doubled_letter_words,
    _dropped_g, _dropped_letter, _e_kept_before_ing, _extra_vowel, _ie_variants, _missing_vowel,
    _short_double, _stopped_th, _swapped_pair, _two_letters_the_wrong_way_round,
    _words_the_bot_writes,
)
from .normalize_part_02 import (
    CAUSES_A_STATE, OBJECT_PRONOUN, AFTER_A_TIME, TIMES_A_STATE, PHRASE_MEASURES,
    _a_consonant_left_out_of_an_ing_word, _a_letter_typed_twice, _an_introduction,
    the_feeling_two_letters_are_gone_from, _a_word_of_the_bots, _shun_variant, _unsays_the_word,
    DIGIT_WORDS, _apostrophe, _collapse, _four_spells_for, _opener_is, _said_with_an_f,
    _said_with_an_f_anywhere, spelled,
)
from .normalize_part_03 import (
    KIN, PERSON_WORDS, NOT_A_THING, _ache_for_aike, _cause_in_place_is_the_verb, _z_for_s,
    BEEN_WORDS, IN_NOUNS, BE_FORMS, HAVE_FORMS, MODAL_FORMS, PERSON_PREPS, THIRD_PERSON,
)


def respell_urgent(text):
    """The line as typed, with only a misspelt emergency word put right and nothing else moved.

    The reading has `norm_text`, but that splits clauses and drops the punctuation, and the
    safety module matches apostrophes ("can't breathe") and one line, so it cannot read it.
    This keeps the line as it was typed, word for word, and only puts back a word from the
    curated emergency table: "my son swalowed a coin" -> "my son swallowed a coin". Nothing
    else in the line is touched, so a module that reads it sees exactly what it read before
    for every line that is not an emergency with a misspelt word in it.

    The one other thing put back is a family word clipped to its initials, because that is a
    word the reading knows and the module cannot: "my dd fell off the slide" was answered with
    the falls answer for an older person, and "my daughter fell off the slide" gets the two
    questions a child's fall needs. The clipped word is only read after a possessive, and only
    when the word after it does not make it a thing of that name ("my ds wont charge" is still
    the console), which is the same guard the reading puts on it.
    """
    if not isinstance(text, str) or not text:
        return ""
    fixes = lexicon.URGENT_MISSPELLINGS

    def put(match):
        word = match.group(0)
        fix = fixes.get(word.lower())
        if not fix:
            # A left-off final g is a typo class the reader already trusts ("havin", "chokin"),
            # but here it has to land on the emergency words to be worth touching: "havin chest
            # pains" is the same emergency as "having chest pains".
            guessed = fix_typo(word.lower())
            return guessed if guessed in URGENT_WORDS else word
        keep = word[:1].isupper()
        # Keep the writer's capital: "Swalowed a coin" starts a sentence.
        return fix.capitalize() if keep else fix

    return CLIPPED_FAMILY.sub(_family_put_back, _ANY_WORD.sub(put, text))


def _family_put_back(match):
    """The clipped family word read as the word it stands for, or the match left as it was."""
    rest = (match.group("rest") or "").split()
    after = rest[0].lower() if rest else None
    after_after = rest[1].lower() if len(rest) > 1 else None
    family = _family_short(match.group("word").lower(), match.group("owner").lower(),
                           after, after_after)
    if not family:
        return match.group(0)
    return match.group("owner") + " " + " ".join(family) + (match.group("rest") or "")


def _a_name_slot(before, before_before, word):
    """True when this word stands where a name goes, so a spelling repair may not touch it.

    The lexicon makes an "-ing" out of every word it holds, so "crispin" is one letter from
    "crisping" and "justin" from "justing": the left-off-g repair read both as verbs, and the
    line came back as "Noted: your brother is called crisping" and "Your cousin justing is
    coming - noted". The store had the name right both times (`others` holds "crispin" and
    "justin"); it is the echo of the repaired line that was wrong.

    Two frames are named, and nothing else: the word after "called"/"named"/"name is", where any
    name may stand, and a known name right beside the person it belongs to ("my cousin justin").
    Only a known name is held back in the second frame, because a verb sits there too: "how do i
    stop me baby wakin up at night" and "my sister sed she would come" are both the repair
    working, and the repair stands.
    """
    if not word.isalpha() or len(word) < 2 or word in LEXICON:
        return False
    if before in NAME_FRAMES:
        return True
    if before in BE_WORDS and before_before == "name":
        return True
    if word in CHAT_NAMES and (before in NAME_ROLL
                               or (before in ("me", "you", "u") and before_before in NAME_CALLS)
                               or (before == "not"
                                   and before_before in BE_WORDS | {"im", "i"})):
        # "call me kay", "i go by kay", "my names kay", "im not kay": the s on "names" and the
        # "not" after "im" are left where they are and the next word is a name, so the chat table
        # may not read it as "ok".
        return True
    return (word in lexicon.COMMON_NAMES
            and before in KIN and before_before in POSSESSIVES)


def _a_thing_where_a_thing_goes(word, before):
    """The person or thing a little word stands for in the place one goes, or None.

    "my wif" and "the wif" are the wife typed without the last letter. This has to be asked
    before the chat table, which answers `wif` with "with" wherever it appears.
    """
    if before not in POSSESSIVES and before not in A_THING_GOES_AFTER:
        return None
    thing = A_THING_TYPED_AS_A_LITTLE_WORD.get(word)
    return thing if thing in LEXICON else None


def _missing_e(word):
    """The "-ed" people type as "-d": "askd" -> "asked", "wantd" -> "wanted", "movd" -> "moved".

    A bare d is how no English word ends after a k, t, v, p, s, m, f or g, so the letter before
    it is the sign the e was dropped; after a vowel, a l, an n or an r it is how plenty of words
    end ("road", "old", "mend", "bird"), and there the repair could only bend a real word, so
    those are left to the curated MISSPELLINGS map. The form with the e also has to be one the
    lexicon knows, which is what keeps "tird" from becoming anything but "tired".
    """
    if len(word) < 4 or not word.endswith("d") or word in LEXICON:
        return None
    if word.endswith("yd"):
        # A word ending in a consonant and y takes "-ied": "worryd" -> "worried", never
        # "worryed". After a vowel the y is part of the sound ("playd"), so it is left alone.
        if word[-3] in VOWELS or word[-3] == "y":
            return None
        longer = word[:-2] + "ied"
        return longer if longer in LEXICON else None
    if word[-2] not in MISSING_E_AFTER:
        return None
    longer = word[:-1] + "ed"
    return longer if longer in LEXICON else None


def _where_a_state_stands(before, before_before, after, before_words=None):
    """True when the words around this one are where a feeling can be said.

    The first person is the whole of the evidence ("im knackerd", "im so exausted", "i feel
    awsome"), and for somebody else it is the be-form and what follows it: "he is worrid about
    money" is a state, "what is nappy rash" is a rash.

    Every measure word between the two is stepped back over, not one of them: "im absolutely
    exausted", "im literally exausted", "im so so exausted" and "im really very exausted" are
    the same state as "im exausted" (lilac-cherry, #5358). Walking back is what keeps the frame
    off the word list, so the next temper word nobody has thought of yet ("im utterly flabbered")
    still reads as a state.
    """
    words = [word for word in (before_words if before_words is not None
                               else (before_before, before)) if word is not None]
    if words and words[-1] in DETERMINER_IN_FRONT:
        # "work left me exausted" arrives with the "me" already repaired to "my", and there the
        # "my" is the person the state was done to. A thing is only named when nothing earlier
        # in the line was done to anybody.
        done_to = (words[-1] in POSSESSIVE_IN_FRONT
                   and any(word in CAUSES_A_STATE for word in words))
        if not done_to:
            return False
    end = len(words) - 1
    back = end
    while back >= 0 and _measures_a_state(words[back]):
        back -= 1
    if back < 0:
        # Nothing but measure words in front of it ("so exausted", "a bit nackered"), or nothing
        # at all because the word opens the line ("exausted", "exausted from work", "worrid about
        # money"): a state is what a line opens with or what a bare "so" leads to, but only where
        # a state is what the line is about, because "nappy bag" and "nappy cream" are things.
        return _opens_a_state(after)
    stands = words[back]
    if stands in BE_BEFORE_A_STATE:
        return True
    if stands in THIRD_PERSON_BE:
        return _ends_a_state(after, opening=not (back >= 1 and (words[back - 1] in PERSON_WORDS
                                                               or words[back - 1] in OBJECT_PRONOUN)))
    # "i got so exausted", "that made me exausted", "work left me exausted": a verb that says
    # something was done to somebody puts them in a state, either with the person said ("made me",
    # "left me") or without ("i got so exausted"). Without the person, the word right after the
    # verb has to be a measure word or the state has to end the clause, so "i got nappy rash" is a
    # rash and "we got nappy" is not English anyway.
    if stands in CAUSES_A_STATE:
        return back < end or _ends_a_state(after)
    if stands in OBJECT_PRONOUN and back >= 1 and words[back - 1] in CAUSES_A_STATE:
        return True
    # "work left me exausted" is typed with "me" and the possessive repair reads it as "my"
    # before this point, so the same evidence arrives as "my". Kept only where the state ends the
    # clause, because "she got my nappy bag" is a bag.
    if stands == "my" and back >= 1 and words[back - 1] in CAUSES_A_STATE:
        return _ends_a_state(after)
    # A measure phrase is two words or more ("a bit", "a little", "kind of", "a tad"), so walk
    # back over those as well - but only to a first person be-form, because in the third person
    # the same words carry a thing ("it is a nappy" is a nappy) and that is the word this repair
    # must never touch.
    wide = back
    while wide >= 0 and _measures_a_state(words[wide], wide=True):
        wide -= 1
    if wide < back and wide >= 0 and words[wide] in BE_BEFORE_A_STATE:
        return True
    # A measure phrase taken all the way back to the start of the line is the same case as a bare
    # measure word: "a bit nackered", "kind of nackered", "a little exausted" with no "im" in
    # front of them at all (gentle-chair, plucky-pomelo, #5358).
    if wide < back and wide < 0:
        return _opens_a_state(after)
    return False


def _ends_a_state(after, opening=False):
    """True when what follows a state is where a state can end: nothing, a function word, a time.

    `opening` is for the word that opens a line: there is nothing in front of it to say a state is
    what the line is about, so a word that a thing can be followed by ("nappy after nappy") is not
    taken as the end of one.
    """
    if after is None or after == "|" or after in AFTER_A_STATE:
        return True
    if opening:
        return False
    return (after in TIMES_A_STATE or after in AFTER_A_TIME
            or after in A_STATE_THEN_A_TIME)


def _opens_a_state(after):
    """True when what follows a word that opens a line is a state rather than a thing.

    A state that opens a line is the whole of what they said ("exausted", "exausted from work",
    "worrid about money", "nackered all the time"), so it is repaired; a word that opens a line
    and is followed by a thing is part of that thing, so it is not ("nappy cream", "nappy rash",
    "nappy change", "nappy bag", "nappy bin"). Only the word right after it decides, and every
    function word - a preposition, a joiner, a time word, a determiner - says the line is about a
    state, so the list of things does not have to be written down.

    A word that says when is not one of those, because a thing is followed by one as easily as a
    state is: "nappy yesterday" is a nappy, and the line would have to say a state some other way
    ("i was nackered yesterday") before the word is read as one.
    """
    return _ends_a_state(after, opening=True) or after in NOT_A_THING


def _a_measure_spelt_wrong(word):
    """True when this is a measure word spelt wrong ("completey exausted", "absolutley terified").

    The measure words are ordinary words, so a slip in one of them is repaired anywhere; this is
    only about the frame, which cannot see that the word in front of a state is still a measure
    word with a letter missing. Only words long enough to be no other word with one letter
    different, so "realy" and "completly" count and "to" and "so" do not.

    The closed list is not the whole story, because the "-ly" is what says a word measures a state
    (`_measures_a_state`) and the words in the list above are the ones people say, not the ones
    they type. A slip that breaks the ending is then in neither: `absolutley`, `extremley`,
    `genuinly` and `realy` are none of them one letter from a word of the list, and none of them
    ends in "ly" any more, so `im absolutley terified` lost the feeling the spelled line keeps.

    The ending itself is what gets typed wrong, and it is typed wrong in one of two ways: the "l"
    and the "y" of "-ly" in the wrong order ("absolutley", "extremley") or a doubled "l" typed
    once ("totaly", "realy"). Both leave a word ending in "y" with a single "l" among its last
    three letters, which no other long word has - "safety", "memory", "quality", "mouldy",
    "floppy", "turkey" all end in a letter that is not the "l" of the ending, and the short words
    that do ("barley", "parsley", "trolley") are shorter than an adverb of that shape. The adverb
    itself is often not in the vocabulary at all ("absolutely", "extremely" are made by an ending
    rule rather than written down, and their stem is not either), so it is the shape of the ending
    that is read, and no list of adverbs is asked for and none is kept.
    """
    if not (len(word) >= 6 and word.isalpha()):
        return False
    if any(_one_letter_apart(word, measure) for measure in AMOUNT_BEFORE_A_STATE):
        return True
    if word.endswith(("aly", "lye", "yl")):
        return True
    # "The l and the y in the wrong order" also catches the words that end in "ley" of their own
    # ("barley", "parsley", "trolley"), and those are six or seven letters where an adverb of that
    # shape ("absolutely", "extremely") is nine or more.
    return len(word) >= 9 and word.endswith("ley")


def _measures_a_state(word, wide=False):
    """True when this word only says how much or how, not what.

    The measure words are a closed list of the ones people type ("so", "very", "not", "dead",
    "proper"), and any word made into an adverb with "-ly": "im absolutely exausted", "im
    literally exausted", "im utterly exausted" are the same state as "im exausted", and a list
    of intensifiers is a list somebody has to keep adding to (lilac-cherry, #5358). The "-ly"
    is what says the word is about the state rather than a thing, so "im genuinely exausted"
    reads without anybody naming "genuinely" here.
    """
    if wide and word in PHRASE_MEASURES:
        return True
    return (word in AMOUNT_BEFORE_A_STATE or word in BARE_TO
            or (len(word) >= 5 and word.endswith("ly")) or _a_measure_spelt_wrong(word))


def _near_a_feeling(word, before=None, before_before=None, after=None, alone=False,
                    before_words=None, after_words=None):
    """The feeling a misspelt feeling word names, or None.

    A feeling word is a closed list, so one letter out is still that feeling: "knackerd" is
    "knackered", "shatterd" is "shattered", "worrid" is "worried", "exausted" is
    "exhausted". This is the class a general spell-fixer has to refuse, because next to an
    ordinary word the shortest edit is another ordinary word; next to a feeling word there is
    nothing to confuse it with. A word that could be two feelings is left alone.

    Only where a state can stand: after a be-form, with at most one measure word between ("im so
    exausted", "she was knackerd", "i feel awsome"). Every other feeling repair in this file is
    framed like that and this one was not, so a real word the lexicon does not hold became the
    feeling anywhere in the line: "how do i change a nappy" was read as "snappy" (four deck
    lines, and the question reached the pool for a short temper), "my nappy bag is heavy" as
    "snappy bag". The frame is the second guard, after the lexicon.
    """
    if not alone and not _where_a_state_stands(before, before_before, after, before_words):
        return None
    # A word somebody uses as it stands is not a feeling with a slip in it, however close it
    # sits: "i scored a goal today" was read as "scared" and answered "I'm sorry - that's
    # frustrating", and "this place is sacred" was the same, because the state frame was right
    # and the word was one letter from the feeling. `lexicon.NOT_A_FEELING` names those words,
    # and the true slips ("exausted", "nerveus") still repair.
    if len(word) < 4 or word in LEXICON or word in lexicon.NOT_A_FEELING:
        return None
    # One letter typed twice is one letter too many, whatever the letter is, and whatever the
    # length of the word: "im saad" and "im loow" were four letter words the length rule below
    # refuses, and "im lonelyy" a consonant the vowel rule above refuses.
    twice = _a_letter_typed_twice(word)
    if twice and not _an_introduction(before, before_before, after, before_words, after_words):
        return twice
    # The short states are where a letter left out costs the answer, and they were refused here
    # by length: "im emty" and "im angy" were each answered "Nice to meet you, Emty" and
    # "Nice to meet you, Angy", while "im empty" and "im angry" get the real answer. A four
    # letter word is the shape of a name as well, so the list of names is asked first, and the
    # feeling has to be one letter longer than the word - a letter left out, never swapped in.
    if len(word) == 4:
        # A four letter word starts a phrase as often as it is a state, and only the word right
        # after it is looked at: "im tied up at work" is busy, not tired, and "im bred to run" is
        # about a dog. So a word this short is repaired only where nothing follows it.
        if after is not None and after != "|":
            return None
        if word in lexicon.COMMON_NAMES:
            return None
    # "-cious" and "-xious" are the same sound and the same slip ("ancious" is "anxious").
    # The rest of the word has to be a feeling already, so this reaches the closed list only.
    if word.endswith("cious") and word[:-5] + "xious" in lexicon.FEELINGS:
        return word[:-5] + "xious"
    # The same sound with a t heard in it: "anctious" is "anxious".
    if word.endswith("ctious") and word[:-6] + "xious" in lexicon.FEELINGS:
        return word[:-6] + "xious"

    found = sorted(feeling for feeling in lexicon.FEELINGS
                   if _one_letter_apart(word, feeling)
                   and (len(word) >= 5 or len(feeling) == len(word) + 1)
                   and not _a_consonant_left_out_of_an_ing_word(word, feeling))
    if len(found) == 1:
        return found.pop()
    # Two letters gone is the next class out, and it is the common one once the word is long:
    # "im stessd" is "stressed", "im exasted" is "exhausted", "im depresd" is "depressed". A word
    # this long has room for two letters, and the slip is always the same shape - letters left
    # out, never swapped - so the test is that the typed word is the feeling with one or two
    # letters taken out, first letter kept. Swaps and two candidates are refused, and so is a
    # name: "im stessd" is a state, "im sarah" and "im katie" are people.
    if after in (None, "|") and _the_state_is_the_whole_frame(before, before_before,
                                                              before_words):
        return the_feeling_two_letters_are_gone_from(word)
    return None


def _the_state_is_the_whole_frame(before, before_before, before_words=None):
    """True when nothing but the person or the be-form stands in front of the state.

    Two letters out is a long enough slip for two different words to be that close, and a state
    said of a thing is where the two meet: "my phone screen is cracked" is a screen, "cracked"
    being "crackered" by two letters. So this repair only reaches a line whose subject is the
    person - "im stessd", "im so stessd", "she was stessd" - and stands down the moment a thing is
    named in front of the be-form ("my phone screen is cracked", "the table leg is cracked").
    """
    words = [word for word in (before_words if before_words is not None
                               else (before_before, before)) if word]
    back = len(words) - 1
    while back >= 0 and _measures_a_state(words[back]):
        back -= 1
    return back == 0


def fix_typo(word):
    """A high-confidence correction for a word that is not in the lexicon, or None.

    Only typo classes that do not collide with ordinary words are used: a doubled or
    un-doubled letter ("recomend", "untill"), an ie/ei swap ("recieve"), a left-off final
    g ("mornin") and a dropped w ("kno"). A confident wrong correction is worse than none, so one-letter
    substitutions and transpositions are left to the curated MISSPELLINGS map: with a
    lexicon this size, "three" would otherwise become "there". A test keeps that honest: a
    real word is never bent into the word the bot answers with ("stairs" is not "stars",
    "swelling" is not "spelling").
    """
    if not word.isalpha():
        return None
    if word in BASE:
        # A word the lexicon holds is a word of its own, whatever it looks like: "travelled"
        # and "traveled" are both right, and each was being read as a slip of the other.
        return None
    if word in lexicon.TYPED_WORDS:
        # A word the deck and the bot's own prose use as it stands is a word, even when it is
        # one letter from another one's doubled spelling: "bled", "wed", "telly", "lager",
        # "thee". The whole deck reads 23 turns differently without this guard, and every one
        # of them is a word bent into a wrong one.
        return None
    if word in _words_the_bot_writes():
        # A word the bot's own base writes is spelled right by construction, so it is a word of
        # its own: "stain", "order", "spilt" and "matters" are not slips of "satin", "roder",
        # "split" and "mattres". The same guard already keeps a swapped pair from reading one as
        # the other; it belongs on every class now that the bot's words are repair targets too.
        return None
    if word in lexicon.NOT_A_FEELING:
        # An everyday word one letter from a feeling is not that feeling typed with a slip, and
        # the two-letters-the-wrong-way-round reader does not know it: "sacred" is one swap from
        # "scared", so "this place is sacred" was read as a line about being frightened and
        # answered "a lot to carry". A word on this list is left as it was typed.
        return None
    if word in lexicon.COMMON_NAMES:
        # A first name is a word, to the person who has it, and nothing in the line says it is
        # a typo: "matt is my son" was noted as "mat", "ann is my sister" as "an", and the
        # repair reached the doubled letter of one and the doubled letter of the other's name.
        # The sentence a person writes about someone they know is the one thing the bot must
        # not get wrong, so a name the list holds is left as it was typed.
        return None
    shunned = _shun_variant(word)
    if shunned:
        return shunned
    stopped = _stopped_th(word)
    if stopped:
        return stopped
    short = _short_double(word)
    if short:
        return short
    doubled_once = _doubled_letter_words(word)
    if len(word) == 3 and doubled_once:
        # A three-letter word is not too short for this slip - "i need a wek off work", "im
        # trying to kep calm" - but a short word is bent only towards one of the words people
        # use most, so "cok" is a cook and nothing stranger is guessed.
        best = sorted(doubled_once, key=lambda w: COMMON_RANK.get(w, 10 ** 6))[0]
        if COMMON_RANK.get(best, 10 ** 6) < 2000:
            return best
    if len(word) < 4:
        return None
    a_thing = _a_thing_a_letter_short(word)
    if a_thing:
        return a_thing
    # A doubled letter in front of an ending is left as it was typed: the un-doubled spelling
    # says something else ("hopping" is not "hoping", "planed" is not "planned"), and which one
    # the person meant is nowhere in the letters.
    candidates = [w for w in _double_variants(word)
                  if _a_word_of_the_bots(w) and not _unsays_the_word(word, w)]
    candidates += doubled_once
    candidates += [w for w in _ie_variants(word) if _a_word_of_the_bots(w)]
    dropped = _dropped_g(word)
    if dropped:
        candidates.append(dropped)
    said_as_n = _an_ing_said_as_n(word)
    if said_as_n:
        candidates.append(said_as_n)
    candidates += [w for w in _dropped_letter(word) if _a_word_of_the_bots(w)]
    candidates += [w for w in _a_leading_h(word) if _a_word_of_the_bots(w)]
    candidates += [w for w in _extra_vowel(word) if _a_word_of_the_bots(w)]
    candidates += [w for w in _missing_vowel(word) if _a_word_of_the_bots(w)]
    # A plural is an everyday form of a word rather than a word, so "the windas" is kept when
    # the lexicon knows "windows". The singular stays a base word: letting everyday forms in
    # made "winder" (of "wind") tie with "window", and a tie is no guess at all.
    candidates += [w for w in _a_said_for_an_ending(word)
                   if w in BASE or (w.endswith("s") and w in LEXICON)]
    # A long word two letters the wrong way round is the emergency vocabulary first ("collasped"
    # is "collapsed") and the ordinary one after it, and the caller still keeps only one answer.
    candidates += [w for w in _swapped_pair(word) if _a_word_of_the_bots(w) or w in URGENT_WORDS]
    candidates += [w for w in _two_letters_the_wrong_way_round(word) if _a_word_of_the_bots(w)]
    flat_ed = _missing_e(word)
    if flat_ed:
        candidates.append(flat_ed)
    candidates += [w for w in _e_kept_before_ing(word) if w in LEXICON]
    left_out = _an_emergency_word_left_out(word)
    if left_out:
        candidates.append(left_out)
    # A letter the word does not say, and a letter typed twice.
    #
    # The t of "often", "listen", "fasten", "castle" and "whistle" is not said, so it is the
    # letter people leave out of the word. It goes back where those words have it: straight
    # before "en" or "le" and straight after a consonant. A general letter put anywhere turns
    # ordinary words into other ones ("pond" is one letter from "pound", "bush" from "brush", and
    # both are words a line is about), and with a vowel in front of the ending it would make
    # "tile" into "title".
    def _a_silent_t_put_back(typed):
        for ending in ("en", "le"):
            if typed.endswith(ending) and len(typed) > len(ending) + 1:
                if typed[-len(ending) - 1] in VOWELS:
                    continue
                yield typed[:-len(ending)] + "t" + ending

    candidates += [w for w in _a_silent_t_put_back(word) if w in BASE or w in LEXICON]
    # The doubling rule above fences every doubled pair off, because "taping" is not "tapping" -
    # but the fence belongs on a word that *is* a word as typed. "watter" is nothing, so "water"
    # loses nothing, and the line that had it keeps its card. The fence is only ever loosened for
    # a typed word the lexicon does not hold, so nothing that means something is bent.
    typed_is_a_word = word in BASE
    candidates += [w for w in _double_variants(word)
                   if w in BASE and not (typed_is_a_word and _unsays_the_word(word, w))]
    words = sorted(set(candidates), key=lambda w: COMMON_RANK.get(w, 10 ** 6))
    if not words:
        return None
    if len(words) == 1:
        return words[0]
    if COMMON_RANK.get(words[0], 10 ** 6) < 120 and COMMON_RANK.get(words[1], 10 ** 6) > 900:
        return words[0]
    return None


def _token(word, fixes, before=None, before_before=None, after=None, alone=False,
           before_words=None, after_words=None):
    """Normalise one lower-case token to zero or more ordinary words.

    `before` is the word it follows, for the few repairs that depend on where a word sits.
    """
    if word == "cause" and _cause_in_place_is_the_verb(before, after, after_words):
        return [word]
    if before is not None:
        # The chat table turns "wif" into "with" wherever it stands; in the place a person
        # goes the same letters are the wife.
        thing = _a_thing_where_a_thing_goes(word, before)
        if thing:
            fixes.append((word, thing))
            return [thing]
    if word in DIGIT_WORDS:
        return [DIGIT_WORDS[word]]
    if word in lexicon.CHAT:
        return lexicon.CHAT[word].split()
    if word in lexicon.EXPAND:
        return lexicon.EXPAND[word].split()
    if word in lexicon.US_SPELLINGS:
        # The same word in the American spelling: the reading, the topics and the knowledge base
        # all know the British one, and the line was not misspelt, so this is not a repair - the
        # plain line keeps the spelling the person used.
        return [lexicon.US_SPELLINGS[word]]
    if word in lexicon.MISSPELLINGS:
        return lexicon.MISSPELLINGS[word].split()
    if word in lexicon.URGENT_MISSPELLINGS:
        fixes.append((word, lexicon.URGENT_MISSPELLINGS[word]))
        return [lexicon.URGENT_MISSPELLINGS[word]]
    if "'" in word:
        expanded = _apostrophe(word)
        if expanded:
            return expanded
    for_spelled = _four_spells_for(word)
    if for_spelled:
        fixes.append((word, for_spelled))
        return [for_spelled]
    collapsed = _collapse(word)
    if collapsed:
        fixes.append((word, collapsed))
        return [collapsed]
    if word in LEXICON or not word.isalpha() or len(word) < 2:
        return [word]
    opened = _opener_is(word)
    if opened:
        fixes.append((word, opened[0]))
        return opened
    pluraled = _z_for_s(word)
    if pluraled:
        fixes.append((word, pluraled))
        return [pluraled]
    ached = _ache_for_aike(word)
    if ached:
        fixes.append((word, ached))
        return [ached]
    corrected = fix_typo(word)
    if corrected:
        fixes.append((word, corrected))
        return [corrected]
    fronted = _said_with_an_f(word)
    if fronted:
        fixes.append((word, fronted))
        return [fronted]
    swapped_inside = _said_with_an_f_anywhere(word)
    if swapped_inside:
        fixes.append((word, swapped_inside))
        return [swapped_inside]
    feeling = _near_a_feeling(word, before, before_before, after, alone, before_words,
                              after_words)
    if feeling:
        fixes.append((word, feeling))
        return [feeling]
    return [word]


def _the_thing_has_been(word):
    """Whether the word after a "bin" is what a thing that has been somewhere says next."""
    plain = _plain_chat(word) if word else ""
    if not plain:
        return False
    if plain in BEEN_WORDS or plain.endswith(("ing", "ed")):
        return True
    # The word `in` itself ends in "in", so "<possessive> <thing> bin in <place>" - "my green
    # bin in the corner", "my washing bin in the corner" - was read as a thing that has *been*
    # somewhere, and both lines lost their own answer. The bare word is not a dropped g.
    return plain != "in" and plain.endswith("in") and plain not in IN_NOUNS


def _is_person(word):
    """True when this token names the person a "bin" belongs to: "mums", "hes", "my dad"."""
    if not word:
        return False
    bare = word.replace("'", "").replace("\u2019", "")
    if bare in PERSON_WORDS or bare.rstrip("s") in PERSON_WORDS:
        return True
    plain = _plain_chat(word)
    if plain in PERSON_WORDS:
        return True
    spelled = (lexicon.CHAT.get(word) or lexicon.EXPAND.get(word) or "").split()
    return bool(spelled) and spelled[0] in PERSON_WORDS


def _plain_chat(word):
    """The first word a chat spelling stands for: "shud" -> "should", "ive" -> "i"."""
    if not word:
        return ""
    spelled = lexicon.CHAT.get(word) or lexicon.EXPAND.get(word) or word
    return spelled.split()[0]


def _spells_a_helper(word):
    """True when the token in front is a helper or a "to" once its chat spelling is undone.

    "b" is the quick way of writing "be" ("gona b late", "ill b there", "will b fine"), but it
    is a letter people also name ("plan b", "vitamin b", "b side"), so it only becomes a verb
    where a verb has to be: after a helper, a form of have or be, "to", or "not".
    """
    if not word or word == "|":
        return False
    spelled = (lexicon.CHAT.get(word) or lexicon.EXPAND.get(word) or word).split()
    if not spelled:
        return False
    last = spelled[-1]
    return (last in MODAL_FORMS or last in BE_FORMS or last in HAVE_FORMS
            or last in ("to", "not"))


def _is_be(word):
    """True when the token in front is a form of "be", chat spelling or contraction included."""
    if not word:
        return False
    if word in BE_FORMS:
        return True
    spelled = lexicon.CHAT.get(word) or lexicon.EXPAND.get(word)
    return bool(spelled) and spelled.split()[-1] in BE_FORMS


# The past participles a modal helper takes, so "could of gone" is repaired and "could of" on
# its own is not: a line that names the spelling it is asking about is a question about words.
IRREGULAR_PARTICIPLES = frozenset("""
    been gone done had seen said made taken given told known written eaten drunk spoken broken
    chosen driven fallen flown forgotten got gotten hidden held kept left lost met paid put read
    run come become begun brought bought caught fought found heard meant sent shown slept spent
    stood taught thought understood won worn
""".split())


def _is_participle(word):
    """Whether this word is the verb a modal helper's "of" is standing in for "have" before."""
    if not word or word in ("|",) or word == "or":
        return False
    plain = _plain_chat(word)
    if plain.endswith("ed") or plain in IRREGULAR_PARTICIPLES:
        return True
    return False


# "my mums got a chest infection", "my dads on his own", "my nans still not well": the
# possessive written without its apostrophe and the helper dropped with it. Read word by word the
# family word looks like a plural, so the line loses the person and an answer that needs one never
# comes. Only kin a person has one of: "my kids got chickenpox" and "my brothers coming over" are
# two people as often as one, and turning them singular would put the wrong person in the line.
KIN_SINGULAR = {
    "mums": "mum", "mams": "mam", "moms": "mom", "dads": "dad",
    "husbands": "husband", "wives": "wife", "partners": "partner",
    "nans": "nan", "grans": "gran", "grandmas": "grandma", "grandads": "grandad",
    "mothers": "mother", "fathers": "father",
    "boyfriends": "boyfriend", "girlfriends": "girlfriend",
}


# What a person is doing or is: the shapes that need a helper in front of them. "got" and "had"
# take "has"; everything else takes "is". A word that is not here is left alone, which keeps a
# real possessive out of it: "my mums car", "my mums pills" are things belonging to somebody.
KIN_HAS = frozenset("got had been gone".split())


KIN_IS = frozenset("""
    on in at off out away here back home due around
    pregnant engaged married divorced retired widowed ill sick poorly unwell upset fine ok okay
    worried tired late early better worse mad angry happy sad lonely dead alive well drunk hungover
    coming going staying moving working getting having being doing feeling expecting visiting
    arriving leaving starting recovering struggling coping waiting looking planning hoping trying
    applying retraining babysitting sitting standing living travelling traveling
    """.split())


# A short filler can sit between the person and what they are doing: "my dads just retired".
KIN_FILLERS = frozenset("just still always now already recently never not really very so quite"
                        .split())


# A word in "the person is doing ___" is the start of a verb phrase, not a thing the person owns.
# The -ing words in KIN_IS are nouns too, and "my mums living room" is a room: only a following
# word that can come after a verb earns the helper. Kept to the function words and the handful of
# adverbs that sit right after one, because a miss costs nothing (the line keeps what it typed)
# and a false positive puts "is" in the middle of a noun.
CAN_FOLLOW_A_VERB = frozenset("""
    a an the this that these those my his her their our your its
    in on at to from with about for of into onto over under up down out off back home
    away around round through across along behind past near
    me him her them us it you
    and but or so because when while if then than
    today tonight tomorrow now again soon later already still just always never ever not
    late early hard well badly properly slowly quickly together alone anymore
    fine ok okay alright better worse
""".split())


def _a_gerund_reads_as_a_verb(word, after_after):
    """True when "-ing" is what the person is doing rather than the first half of a noun.

    "my dads working late" and "my mums coming to stay" are verb phrases; "my mums living room is
    tiny", "my dads sitting room needs painting" and "my mums waiting list is long" are things
    that belong to them, and an "is" in front reads as nonsense.
    """
    if not isinstance(word, str) or not word.endswith("ing") or len(word) < 5:
        return True
    if after_after in (None, "", "|"):
        return True                             # "my mums cooking" - nothing after it
    return after_after in CAN_FOLLOW_A_VERB


def _kin_needs_a_helper(token, before, after, opens_the_clause, after_after=None):
    """The family word a dropped-apostrophe possessive stands for, with its helper.

    "my mums got a chest infection" is "my mum has got a chest infection", and "my dads on his
    own" is "my dad is on his own". Only where the possessive opens the clause or follows a
    leader ("and my dads on his own"), and only in front of a word that needs a helper, so a noun
    coming next keeps the possessive as it was typed ("my mums car").
    """
    if not opens_the_clause or before != "my":
        return None
    if token not in KIN_SINGULAR:
        return None
    if after in KIN_HAS:
        return [KIN_SINGULAR[token], "has"]
    if after in KIN_IS or after == "not" or (after or "").isdigit():
        if after in KIN_IS and not _a_gerund_reads_as_a_verb(after, after_after):
            return None                        # "my mums living room", "my dads sitting room"
        return [KIN_SINGULAR[token], "is"]      # "my mums not eating", "my mums 82"
    if after in KIN_FILLERS and (after_after in KIN_IS or after_after in KIN_HAS
                                 or after_after == "not"):
        return [KIN_SINGULAR[token],
                "has" if after_after in KIN_HAS else "is"]
    return None


# The family people clip to initials in a quick message, and the one they call their partner.
# Only after a possessive: "my mil", "her oh". A bare "oh" is the word people start a line with.
FAMILY_SHRT = {
    "mil": ("mother", "in", "law"), "fil": ("father", "in", "law"),
    "sil": ("sister", "in", "law"), "bil": ("brother", "in", "law"),
    "oh": ("other", "half"), "lo": ("little", "one"),
    "dd": ("daughter",), "ds": ("son",), "dh": ("husband",),
}


# Two of those initials are also a thing somebody owns, so the word after says which one it is:
# "my ds" is the console when it is broken, charging or a game ("my ds wont charge"), and "my
# dd" is a bra size or a due date when it is in front of a size or a month ("my dd bra", "my dd
# is june", "my dd is in june"). Those keep their letters: the mistake the other way is a
# partner's own possession read back as a member of the family, which is worse than a line left
# as it was typed.
SHRT_THINGS = {
    "ds": frozenset("""broken broke charging charge charger battery screen console game games
        lite dead working works""".split()),
    "dd": frozenset("""bra cup size in january february march april may june july august
        september october november december""".split()),
}


POSSESSIVES = frozenset("my your his her our their ur me mums dads sons daughters".split())


def _family_short(token, before, after, after_after):
    """The family word a clipped initial stands for, or None to keep the letters.

    "my oh", "her mil" and "my dh" are the partner and the in-laws, and the expansion is what
    lets every entry that keys on "husband" or "daughter" answer a line typed in a hurry: "my
    dd wont sleep" was read as the person not sleeping and answered "Annoying. Is it every
    time". Only after a possessive, and only for an initial that cannot be the thing of that
    name in the line ("my ds wont charge" is a console, "my dd is in june" a due date).
    """
    if token not in FAMILY_SHRT or not _is_possessive(before):
        return None
    things = SHRT_THINGS.get(token)
    if things and (after in things or after_after in things):
        return None
    return list(FAMILY_SHRT[token])


# A count of time after the "been" a "bin" stands for: "thats bin 3 wks", "its bin months".
PERIOD_COUNTS = frozenset("""week weeks month months year years hour hours minute minutes""".split())


# A unit clipped to its first letters, which is only the unit after a count: "4 yr old",
# "2 hrs sleep", "ten mins". It cannot be spelled out everywhere - "yr" is how people type
# "your" ("yr welcome") and "hr" is the department ("should i go to hr about my manager"),
# so the count in front is what makes the reading safe. The plural forms never mean anything
# else, so they are in the chat table; these are the ones that need the word in front.
CLIPPED_UNITS = {"yr": ("year", "years"), "hr": ("hour", "hours"),
                 "min": ("minute", "minutes"), "sec": ("second", "seconds")}


# A thing named by its first letters: "how do i bleed a rad", "the rad in my bedroom is cold".
# The full word is what the questions and the pools are written in, so a line read as "rad"
# names nothing and gets "I don't know enough to answer that honestly", while the radiator
# answer sits two words away. A clipped word is only the thing when it is used as one: a word
# about a thing after it ("my rads are noisy", "the rad is cold"), or a determiner in front of
# it at the end of the line ("bleed a rad"). "thats rad mate", "pretty rad" and "a rad new
# bike" are how somebody rates something, and they are left alone. "Mic" is not here: it is a
# microphone to almost everyone who types it, and the one line that wants the microwave
# ("how do i clean the mic") is not worth answering a call about a kitchen appliance.
CLIPPED_THINGS = {"rad": ("radiator", "radiators"), "rads": ("radiator", "radiators")}


# After the clipped thing: what people say about a thing that is not working.
THING_AFTER = frozenset("""is are was were wont wont keeps keep needs need broke broken leaking leaky
    cold hot noisy warm blocked bleed bleeding clean cleaning fix fixed valve valves
    died dies dead stopped stopping working works faulty glitchy tinny quiet sounds sound
    cuts cutting muted mute drops dropped plug plugged cable battery""".split())


# A joining word after it: "i tried to bleed the rad but no water came out", "the rad and the
# pipes". Only after a determiner, because "pretty rad but expensive" is how somebody rates a
# thing and the word after it is still the rating.
THING_JOIN = frozenset("and but so though although because when if then".split())


# "the rad in my bedroom is cold": a place is named after it, and the thing in front is a
# determiner ("thats rad in a way" is still a rating).
THING_PLACE_AFTER = frozenset("in on at".split())


THING_DETERMINER = frozenset("""a an the my our your his her their its both each every no any
    this these those""".split())


THING_PLACE_WORDS = frozenset("""a an the my our your his her their its this these those that""".split())


# In front of it, at the end of the line: "bleed a rad", "fix the leaky rad".
THING_SUBJECT = frozenset("""a an the my our your his her their its this these those both
    each every no any leaky leaking cold hot noisy warm blocked old spare""".split())


A_COUNT = frozenset("""one two three four five six seven eight nine ten eleven twelve
    thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty
    sixty ninety a an couple few several hundred thousand million""".split())


def _counts_a_period(word):
    """Whether this word is a length of time, so "thats bin 3 wks" is "that has been 3 weeks"."""
    return _plain_chat(word or "") in PERIOD_COUNTS


def _is_a_count(word):
    """Whether this word is how many, so the clipped unit after it is the unit."""
    plain = _plain_chat(word or "")
    return plain.isdigit() or plain in A_COUNT


# A period written short after one of these is one of them, not many: "nxt yr", "this yr",
# "last yr", "per yr". The word in front is what makes it safe, because on its own "yr" is how
# people type "your" ("yr welcome"), and "that" and "my" are left out for the same reason -
# "is that yr coat" is a coat, not a year.
A_PARTS_OF_A_PERIOD = frozenset("""next last this every each per past coming previous
    whole""".split())


# "hr" is a word of its own as well as an hour: the HR department, the HR team. A period word in
# front of it ("this hr", "past hr") is an hour when the line is about time and the department when
# the line is about work, and the word *after* the "hr" is what tells the two apart, so both have
# to be read together: "this hr department is useless" is not "this hour department".
HR_IS_THE_DEPARTMENT_AFTER = frozenset("""department departments team teams policy policies
    advice manager managers meeting meetings issue issues people rep reps email emailed staff
    director directors""".split())


def _hr_is_the_department(after):
    """True when the word after "hr" says it is the department and not an hour."""
    return _plain_chat(after or "") in HR_IS_THE_DEPARTMENT_AFTER


def _says_one(word):
    """Whether this word in front of a length of time makes it one: "next yr", "a 3 hr flight"."""
    plain = _plain_chat(word or "")
    return plain in ("1", "a", "an", "one") or plain in A_PARTS_OF_A_PERIOD


# A unit written in its short form and put in front of a noun is one word with it: "a 3 hr
# flight", "a 20 min walk", "a 10 sec clip". The writer typed the singular, and the noun after
# it says the unit is qualifying the noun rather than being the thing counted. Every other word
# after the unit leaves it the head of the count: "4 hr", "3 hrs at the clinic", "2 hrs sleep",
# "4 yr old".
NOT_BEFORE_A_NOUN = frozenset("""a an the my your his her our their its this that these
    of in at on to for from with per and or so but then than ago later old olds off out up
    down back over about around by as if sleep nap rest wait left more less most least
    now today tonight tomorrow yesterday""".split())


def _is_a_thing_here(before, after, after_after=None):
    """Whether the clipped word beside this one is the thing it stands for.

    "my rads are noisy" and "the rad is cold" say something about it; "bleed a rad" ends with it
    after a determiner. "thats rad mate", "pretty rad" and "a rad new bike" are how somebody
    rates something, so the word after them is not one of the things said about a thing.
    """
    # The word after has to be said about a thing as it was typed: "isnt" is read as "is" by the
    # rest of the reader, and "thats pretty rad isnt it" is a rating, not a radiator.
    said_after = (after or "").lower().strip("|")
    if said_after in THING_AFTER:
        return True
    if said_after in THING_JOIN:
        return _plain_chat(before or "") in THING_SUBJECT
    if said_after in THING_PLACE_AFTER:
        if _plain_chat(before or "") not in THING_DETERMINER:
            return False
        return (after_after or "").lower().strip("|") in THING_PLACE_WORDS
    return not said_after and _plain_chat(before or "") in THING_SUBJECT


def _clipped_thing(token):
    """The full word for a clipped thing, plural when the line says so."""
    one, many = CLIPPED_THINGS[token]
    return many if token.endswith("s") else one


def _is_before_a_noun(token, after):
    """Whether the clipped unit in front of this word is qualifying a noun: "a 3 hr flight"."""
    if token.endswith("s") or not after or after == "|":
        return False
    return _plain_chat(after) not in NOT_BEFORE_A_NOUN


def _is_said_of_a_person(word):
    """Whether this word is what somebody has been: a verb with its ending on, or a state.

    "my mums bin in hospital" is a "bin" that is the "been" it sounds like, and so is "my cats
    bin sick" and "bin thinkin bout it". A bare noun is not: "the bin day", "a bin lorry".
    """
    if not word or word in ("|",) or word in PERSON_PREPS:
        return False
    plain = _plain_chat(word)
    if len(plain) > 3 and (plain.endswith("ing") or plain.endswith("ed")
                           or plain.endswith("in")):
        return True
    return plain in IRREGULAR_PARTICIPLES or plain in BEEN_WORDS


def _is_possessive(word):
    """True when the token in front owns what comes next: "my", "her", "your mums"."""
    if not word:
        return False
    bare = word.replace("'", "").replace("\u2019", "")
    return bare in POSSESSIVES


# What can follow a feeling said about yourself: nothing, or where and when. A noun after it
# ("im board games") means the word was not a feeling.
# The words that may come after a feeling: a place or a time it holds for, so "im board work" is
# "i'm bored work(ing)". "the" is not one of them: "im board the train" is *on board the train* and
# "im tried the gym" is the past tense, so a "the" after the feeling turned both into feelings.
A_FEELING_CAN_BE_FOLLOWED = frozenset("""at in on with about of today tonight now again lately
    atm tbh so as all time work home stiff shit""".split())


# The words people put between "i am" and a feeling: "im so board", "im still board".
BEFORE_A_FEELING = frozenset("""so really very well still always constantly dead proper
    pretty totally completely""".split())


def _sounds_like_a_feeling(token, before, after, before_before=None):
    """The feeling this word sounds like, in the place a feeling goes, or None.

    "im board" is "i'm bored" and "im tried" is "i'm tired". Both words are ordinary ones, so
    nothing repairs them anywhere else; the position is what makes the reading safe.
    """
    if before in BEFORE_A_FEELING:
        before = before_before
    if before not in FIRST_PERSON_BE or token not in lexicon.SOUNDS_LIKE_A_FEELING:
        return None
    if after and after not in A_FEELING_CAN_BE_FOLLOWED:
        return None
    return lexicon.SOUNDS_LIKE_A_FEELING[token]


# How people write "ain't": the apostrophe is left out, put in, or typed as a stray one.
AINT_FORMS = frozenset(("aint", "ain't", "aint'", "a'int", "ai'nt", "aint,"))


# A subject that takes "has": "she aint been", "it aint done".
HAS_SUBJECT = THIRD_PERSON | frozenset("this that there everyone somebody someone nobody".split())


AINT_PLURAL = frozenset("you we they ye these those".split())


# The letters no English word ends in before a bare d, so a d after one is a left-off e.
MISSING_E_AFTER = frozenset("ktvpsmfgxzcjq")


# Past forms people leave as the participle in speech: "we aint spoke in a year", "he aint
# broke it". They only ever help choose the expansion of "ain't", so nothing else moves.
PAST_AS_PARTICIPLE = frozenset("""spoke broke woke drank wrote rang sang began swam took gave
    ate fell forgot stole drove rode wore chose froze ran came grew knew threw flew drew""".split())


# "hv" is the fastest way to write "have" ("i hv 2 kids", "hv u got a min"), and it is also
# what a parent calls the health visitor ("ring the hv about her sleep"). Where a verb has to
# be it is the verb: after the person or a helper ("i hv", "shld hv"), in front of the person
# of a question ("hv u", "how many hv u got") and in front of "to" ("hv to go"). After a
# determiner or a possessive the only thing it names is the person - "the hv", "my hv", and
# "ask the hv to weigh him" - and that is the reading the chat table gives it.
HV_SUBJECTS = frozenset("i we you they u ye".split())


HV_HELPERS = MODAL_FORMS | frozenset("to do does did not".split())


# The first person of "to be", the one place a bare stem is how somebody feels ("im annoy") or
# a feeling typed as another word ("im board"). Only the first person is here: "is"/"was" are
# how a thing is described ("the boiler is years old", "everybody was lovely"), where the same
# letters are the word they are.
FIRST_PERSON_BE = frozenset(("im", "i'm", "i’m", "am", "m"))


# How much of it there is sits between the two and changes nothing: "im still confus", "im so
# bore", "im really annoy", "im not confuse" are the same feeling as "im confuse". These are
# only the words that measure or temper a state, and they carry the same evidence for a word
# whose last letter came off: "im so nervou", "im really miserabl", "im well tire". A word that
# names anything keeps its own reading ("im in bore water" is not a feeling, and "im at bored"
# is not a shape of English).
AMOUNT_BEFORE_A_STATE = frozenset("""just only still so really very pretty quite too not never
    always often all sometimes ever constantly honestly actually kinda rather super totally
    completely proper propper dead well awful bloody terribly""".split())


# Where a state can stand: the first person be-form a feeling is said about, and the forms people
# type for it ("im", "i'm", "am", "i been", "i feel", "i feels"). Only first person, because
# "is" and "was" carry a thing as often as a state ("what is nappy rash"), and `_near_a_feeling`
# repairs a one-letter slip of a feeling only here, with any number of measure words between the
# two (`AMOUNT_BEFORE_A_STATE`), so "im knackerd", "im so exausted" and "im absolutely exausted"
# are repaired and a nappy is a nappy.
BE_BEFORE_A_STATE = frozenset("""im i'm i\u2019m m am i been being feel feels feeling feelin felt""".split())


# A state said about somebody else ("he is worrid about money", "she was knackerd") is repaired
# too, but only where a state can stand: at the end of the clause or in front of a word like
# "about". In front of anything else the word is part of a thing, not a state - "what is nappy
# rash" is a rash, and a nappy is a nappy - so the be-form on its own is not enough.
THIRD_PERSON_BE = frozenset("""is are was were r re hes he's shes she's its it's theyre they're
    youre you're ure we're seems seem looks look""".split())


# "to" typed for "too" is one of the measure words a state is said with ("im to exausted").
BARE_TO = frozenset(("to", "two", "2"))


# A determiner in front of a word says the line is naming a thing, not saying how somebody is.
# "the nappy" and "a nappy" are nappies, and the feeling repair made them "snappy", so a person
# who had said nothing about themselves was answered "I'm sorry - that's frustrating." "that"
# is deliberately not here - "im that knackered" is how people say "so knackered" - and neither
# is a phrase measure, so "a bit nackered" still reads as the state it is.
DETERMINER_IN_FRONT = frozenset("""
a an the every each no another this these those some any
my your his her its our their
""".split())


# The possessives among them are also how "me" arrives: the repair that turns "me sister" into
# "my sister" is done before this point, so "work left me exausted" reaches here as "work left my
# exausted" and the "my" is the person the state was done to, not a thing being named.
POSSESSIVE_IN_FRONT = frozenset("my your his her its our their".split())


AFTER_A_STATE = frozenset("""about of at with by for from since because and but so that today
    tonight now lately again too enough when as than in on to not all these days these days""".split())


# What a state said about somebody else may be followed by, over and above `AFTER_A_STATE`: the
# time it held for, and the word that says it did not pass. "she was exausted after work",
# "he was knackerd last week", "they were exausted already". These are the rest of the sentence,
# not a thing the state is part of, so the repair holds in front of them exactly as it holds in
# front of nothing at all. Kept apart from `AFTER_A_STATE` because that list also answers where a
# word that opens a line stands, and a line that opens on a state has no time word in front of it.
A_STATE_THEN_A_TIME = frozenset("""after before yesterday tomorrow already last earlier later
    soon still early late ever during while whenever yet until till whole every""".split())
