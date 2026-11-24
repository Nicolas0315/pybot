"""Part 2 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""
import itertools
import re

from . import lexicon
from .normalize_part_01 import (
    LEXICON, SHION_WORDS, F_TYPED_FOR_TH, _one_letter_apart, VOWEL_SET, BASE, NO_SWAP_TO,
    _words_the_bot_writes, PRONOUN_BASES,
)


def _shun_variant(word):
    """The -tion people spell the way it sounds: "infecshun" -> "infection".

    English spells the /shun/ sound at the end of a word -tion, so a typed word ending in
    "shun" (or "kshun", with the k of "infection" spelled out too) is that word, and no
    ordinary word ends that way except "shun" itself. Nothing here needs the lexicon: the whole point is a word the
    lexicon does not have ("infection" is not one of its words either).
    """
    if word in LEXICON:
        return None
    # "any suggeshuns?" is the one word with an s on the end, where the s of the plural is the
    # only letter after the sound, so the singular is repaired and the s put back.
    if word.endswith("shuns") and len(word) > 7:
        singular = _shun_variant(word[:-1])
        if singular:
            return singular + "s"
        return None
    if word.endswith("kshun"):
        # "infeckshun" spells the /k/ of "infection" with a k as well: the "ks" is the c
        stem = word[:-5]
    elif word.endswith("shun"):
        stem = word[:-4]
    else:
        return None
    if len(stem) < 2 or not stem.isalpha():
        return None
    # "Cushion", "fashion" and "decision" end in the same sound and are not -tion words, so
    # the other spellings of the sound are tried first: "cushun" is a cushion, not a cution.
    # The s of "shun" is where the sound starts, so it can belong to the word as well
    # ("suggeshun" is suggest + ion), which is why the stem is tried both with and without it.
    kept = stem + "s"
    for spelled in (stem + "shion", stem + "ssion", stem + "sion", stem + "tion",
                    kept + "tion", kept + "ssion", kept + "sion", stem + "cian"):
        if spelled in LEXICON or spelled in SHION_WORDS:
            return spelled
    return stem + "tion"


def _said_with_an_f(word):
    """The "th" sound typed as an "f": "fanks" -> "thanks", "froat" -> "throat".

    A swapped sound is not a slip a one-letter repair can find - "fanks" is two letters from
    "thanks" - and it is common enough that "fanks", "fink" and "froat" arrive as whole
    lines. Only the front of the word is read this way, because that is where the sound is
    swapped, and only for a word that is not a word itself whose "th" spelling the reading
    already knows: "fan", "fat", "fro" and "fort" are real words and stay as they are, and
    "sumfink" is left to the spelling tables.
    """
    # The named spellings come first: "foughts" is not a word, but the lexicon builds it from
    # "fought" and a plural, and "thousand" and "threaten" are not in it at all.
    if word in F_TYPED_FOR_TH:
        return F_TYPED_FOR_TH[word]
    if not word.isalpha() or not word.startswith("f") or word in LEXICON:
        return None
    if len(word) < 4:
        return None
    spelled = "th" + word[1:]
    # The chat spellings count as known words here too, because the fold that reads them runs on
    # the line after this: "fey" is "they" and "feyre" is "they are" by the same table that
    # reads "feyve" as "they have".
    if spelled in LEXICON or spelled in lexicon.CHAT or spelled in lexicon.EXPAND:
        return spelled
    # The sound is swapped in a word with an ending on it too, and the ending is what the
    # lexicon holds the word without: "freatens" is "threatens", "freatened" is "threatened",
    # and a safety line that reads neither is a line about something else.
    for ending in ("s", "es", "d", "ed", "ing"):
        stem = spelled[:-len(ending)]
        if spelled.endswith(ending) and len(stem) >= 5 and stem in LEXICON:
            return spelled
    # The same sound with the g left off the end, which the reading already repairs elsewhere:
    # "finkin" -> "thinkin" -> "thinking". One retry, only for the "-in" ending, so every f
    # verb gets its -ing form without a list.
    if spelled.endswith("in") and spelled + "g" in LEXICON:
        return spelled + "g"
    return None


def _said_with_an_f_anywhere(word):
    """The same swapped sound away from the front: "wif" -> "with", "teef" -> "teeth".

    The sound is swapped in the middle and at the end of a word too, and there it costs a line
    its answer rather than only its spelling: "my teef hurt" was asked "Does it come and go, or
    is it there all the time?" while "my teeth hurt" reaches the dentist, "mouf ulcers" reached
    nothing at all, "how do i clean a baff" was a shrug, and a line said back to the person
    repeated "your birfday is the 3rd of may". Only the f is touched, so the rest of the word
    must already be the word it is meant to be: the "th" spelling has to be one the engine
    knows, and the typed word must not be a word it knows ("if", "off", "half", "loaf" and
    "shelf" stay as they are). Only an f nobody could mean as an f is read, which is why this
    runs after `fix_typo` and the letters before it.
    """
    if len(word) < 3 or not word.isalpha() or "f" not in word or word in LEXICON:
        return None
    # A doubled f is only read at the end of the word, where the whole sound is the f: "baff",
    # "mouff". Inside a word the two letters are two sounds ("offers", "coffee"), and reading
    # them as one turned "offers" into "others". A w in front of it is left alone, because
    # "wiff" and "woff" are how people spell a word that begins with "wh" ("a wiff of smoke").
    if word.endswith("ff"):
        if word.startswith("w"):
            return None
        spelled = word[:-2] + "th"
        return spelled if spelled in LEXICON else None
    for at, letter in enumerate(word):
        if letter != "f":
            continue
        spelled = word[:at] + "th" + word[at + 1:]
        if spelled in LEXICON:
            return spelled
    return None


def _near_a_part(word):
    """The part of the body a misspelt part is, or None.

    A part is a closed list, so a word with one letter typed into it or left out of it is still
    that part: "cheast" is a chest, "tomach" a stomach, "shouldr" a shoulder, "fingr" a
    finger, "nee" a knee, "hed" a head. Two parts fit the word and it is left alone, and a
    word the lexicon knows is never bent: "and" is not a hand, "year" is not an ear. The three
    letter parts are left out, because a letter in front of one of them makes an ordinary word
    the bot's list does not hold: "hear", "wear" and "tear" are each "ear" with one letter on.
    """
    if len(word) < 3 or not word.isalpha() or word in LEXICON or word in lexicon.BODY_PARTS:
        return None
    found = set()
    for part in lexicon.BODY_PARTS:
        if len(part) < 4 or abs(len(part) - len(word)) != 1:
            continue
        short, long = (word, part) if len(word) < len(part) else (part, word)
        i = 0
        while i < len(short) and short[i] == long[i]:
            i += 1
        if short[i:] == long[i + 1:]:
            found.add(part)
    return found.pop() if len(found) == 1 else None


PART_REACH = 3


# A game named by the shape of its pitch, or by the knockabout, rather than by its own name: "we
# play five a side on sunday", "anyone up for a kickabout". The game's name is the word the topic
# rule and the knowledge base match on, so a line that names the game this way named no game at all:
# "what should i eat before playing five a side" was answered with a supper pick from the fridge,
# and the same question with "football" in it with the carbs to eat an hour before. Only the reading
# is given the name: `clean` and `plain` keep the words the person typed, which is what a reply
# quotes back.
A_SIDE = frozenset("five six seven eight nine".split())


# A line that asks about the shape of the game itself, or about finding a team to play in, is not a
# line about playing today. The knowledge base has nothing about the form of the game - reading
# "how many players in five a side" as football reached the card about the professional game and
# answered "two halves of 45 minutes, with 11 a side", a confident wrong answer where the bot had
# said it did not know - and a card about picking a club to support is no answer to somebody looking
# for a team. Both shapes keep the words they typed, and so does a statement about the game's shape
# ("eleven a side is a full match"), which is why the full game is not one of the counts read here:
# it is the same game the row about watching it is about, and the line already names it.
ABOUT_THE_FORM = re.compile(r"""
    \bhow\s+many\s+(?:players?|people|a\s+side)\b
  | \bhow\s+(?:long|many\s+halves)\b[^.]{0,40}\b(?:match|game|half|halves)\b
  | \b(?:the\s+)?rules?\b
  | \boffside\b
  | \bhow\s+big\b
  | \bpitch\s+(?:size|dimensions)\b
  | \bfull\s+(?:match|game)\b
""", re.VERBOSE | re.IGNORECASE)


FINDING_A_TEAM = re.compile(r"""
    \b(?:join|joining|find|finding|looking\s+for|sign\s+up\s+(?:for|to)|get\s+into)\b
  | \bteams?\b[^.]{0,24}\b(?:in|near|around|local)\b
  | \b(?:clubs?|leagues?)\b
""", re.VERBOSE | re.IGNORECASE)


def _a_game_named_another_way(norm, words):
    """(`norm`, `words`) with a game named by its shape read as the game's own name.

    "five a side" is a small football match and nothing else is said that way, and one word stands
    in its place so the game sits where the person put it - in their setting clause or in their ask
    - instead of being bolted onto the end of the line. The knockabout is the same game named by the
    thing you do with the ball. The game's name goes into `words` as well, because that is the list
    the knowledge base is matched on; `clean` and `plain` keep the words the person typed, which is
    what a reply quotes back.

    A line about the make-up of the game, or about finding a team, names the game without asking
    anything about playing it, so it keeps the words it typed (see `ABOUT_THE_FORM`). So does a
    line whose subject is a part of the body that hurts: "i play five a side twice a week and my
    groin is sore" has a groin answer of its own, and naming the game put a football-injury card's
    clarifying question ahead of it - the person's part is the subject, and the game is only where
    they use it.
    """
    flat = " ".join(norm)
    if ABOUT_THE_FORM.search(flat) or FINDING_A_TEAM.search(flat):
        return norm, words
    if (any(word in lexicon.BODY_PARTS for word in words)
            and any(word in lexicon.PAIN_WORDS for word in words)):
        return norm, words
    out = []
    read = []
    index = 0
    while index < len(norm):
        if (norm[index] in A_SIDE and index + 2 < len(norm)
                and norm[index + 1] == "a" and norm[index + 2] == "side"):
            out.append("football")
            read.append("football")
            index += 3
            continue
        if norm[index] == "kickabout" or (norm[index] == "kick"
                                          and norm[index + 1:index + 2] == ["about"]):
            out.append("football")
            read.append("football")
            index += 1 if norm[index] == "kickabout" else 2
            continue
        out.append(norm[index])
        index += 1
    if not read or "football" in words:
        return out, words
    return out, list(words) + ["football"]


def _parts_that_hurt(words, fixes):
    """The line with every misspelt part of the body read as that part, repairs kept in `fixes`.

    Only where the line puts the word where a part goes: right beside a word of pain ("my
    cheast hurts", "a sore stomack", "my shouldr has been aching"), or straight after "my" or
    "our" with a word of pain close behind. The place is what tells a part of the body from an
    ordinary word a letter away from one, and the bot's word list does not hold every ordinary
    word ("hear", "wear", "tear" are each a letter from "ear"; "gear" and "chip" are a letter
    from "ear" and "hip"), so the word is never repaired on the letters alone. The words looked
    for are the two the topic rule needs (`topics.BODY` and `topics.HURTS`), so the repair and
    the rule cannot disagree.
    """
    pain = [at for at, word in enumerate(words) if word in lexicon.PAIN_WORDS]
    if not pain:
        return words
    out = []
    for at, word in enumerate(words):
        part = _near_a_part(word)
        beside = at - 1 in pain or at + 1 in pain
        mine = words[at - 1:at] in (["my"], ["our"]) and any(
            abs(other - at) <= PART_REACH for other in pain)
        if part and (beside or mine):
            fixes.append((word, part))
            out.append(part)
        else:
            out.append(word)
    return out


# The verbs that put somebody in a state: "i got so exausted", "that made me exausted", "work
# left me exausted", "it keeps me busy". A feeling is what these lead to, so the words after one
# are a state's place - but only with the person said ("made me") or a measure word between ("i
# got so"), because "i got nappy rash" is a rash (clear-weasel, #5358).
CAUSES_A_STATE = frozenset("""got get gets getting gotten make makes made making left leave leaves
    leaving kept keep keeps keeping felt feels feel feeling found find finds find made became
    become becomes turned turns turn drove driven drive drives""".split())


# The people a state is said about when something was done to them: "made me exausted".
OBJECT_PRONOUN = frozenset("""me us him her them you u u's myself yourself himself herself
    ourselves themselves""".split())


# A state is measured with phrases as well as words: "im a bit nackered", "im a little
# exausted", "im kind of knackered", "im a tad tired". These are the function words those
# phrases are made of - a closed class, like the determiners and the prepositions - so they are
# only taken in the first person, where a bare noun cannot stand ("it is a nappy" is a thing and
# stays one).
PHRASE_MEASURES = frozenset("""a an the bit little lot lots tad touch wee kind sort of out much
    many far way right that this these those enough half twice few some more most less least
    loads bunch ton tons hell heck mega extra damn damned fricking freaking""".split())


# When a state was: "i was exausted yesterday", "i was nackered last night", "we were miserabl all
# week". A state reads the same with one of these after it as with nothing at all, and without
# them a slip with a letter missing ("exausted", "nackered") was not repaired in a line that said
# when it was - 28 of the 882 slips the understanding lane measured (#5358, tall-moth) - while a
# slip of a letter in the wrong order ("knackerd") was, because that repair does not ask the frame.
# Only the words that say when, because a state is in the past as often as it is now, and every
# one of them also ends the sentence ("i was exausted last night" says no less than "i was
# exausted"). None of them makes a thing into a state: "what is nappy rash yesterday" is nothing
# anyone writes, and the thing words this repair must leave alone are words with a noun after
# them.
TIMES_A_STATE = frozenset("""yesterday last this week weekend morning mornings night nights
    evening evenings afternoon afternoons ago monday tuesday wednesday thursday friday saturday
    sunday january february march april june july august september october november december""".split())


# What comes after a state to say when it was, but comes after a thing just as easily ("nappy
# after nappy", "nappy before bed"), so it is only a state's ending where the line already says a
# state - after a be-form with somebody in front of it, or after a verb that puts somebody in one.
AFTER_A_TIME = frozenset("""all after before until till during while once then later earlier
    afterwards""".split())


def _a_letter_typed_twice(word):
    """The feeling a word is when one of its letters was typed twice, or None.

    "im saad", "im maad", "im loow", "im shyy", "im lonelyy": the letter that came out twice is
    one letter too many, and the word without it is a feeling. The one-edit reader in
    `_one_letter_apart` refuses these on purpose - a letter typed into a word only counts when it
    is a vowel, and a four letter word needs its feeling to be longer than it is, because a word
    that short is as often a name - and the doubled letter is not always a vowel ("lonelyy").
    Nothing is lost by reading the one slip on its own terms: the word being read is not in the
    lexicon, and the word without the doubled letter is a feeling and not a name.
    """
    if len(word) < 4 or word in lexicon.COMMON_NAMES:
        return None
    for place in range(len(word) - 1):
        if word[place] != word[place + 1]:
            continue
        shorter = word[:place] + word[place + 1:]
        if shorter in lexicon.FEELINGS:
            return shorter
    return None


# The shapes a line introduces a person in, where a word one letter short of a feeling is that
# person's name: "hi, im saad", "im saad from egypt", "saad here", "im saad (34)", "nice to
# meet you im saad". A doubled letter is the same evidence for a name as for a typo - "Saad" is
# an ordinary name - so the introduction is asked first and the doubled letter is left alone
# there. Being told "Sorry to hear that" for saying your own name is worse than the typo reaching
# the shrug, and it is permanent: the reply is stock and the person cannot tell why it happened.
INTRODUCING_A_PERSON = frozenset("""
    hi hello hey heya hiya hii hiii yo howdy greetings morning afternoon evening sup meet
""".split())


# What follows the name of the person being introduced: "saad here", "im saad from egypt".
INTRODUCING_AFTER = frozenset("here from".split())


def _an_introduction(before, before_before, after, before_words=None, after_words=None):
    """True when this word is the name a line introduces rather than a state it states.

    The five shapes are the ones a person gives their name in, and none of them is a shape a
    feeling comes in: a greeting in front of it, "this is X", an "X here" or "X from <place>"
    tail, an age after it, or a word at the front of the line that the verb after it has as its
    subject ("saad is my brother"): a state is what a line says about somebody, not what it
    says about a word.
    """
    for word in (before_words or ()):
        if word in INTRODUCING_A_PERSON:
            return True
    if after in INTRODUCING_AFTER:
        return True
    if before == "is" and before_before in ("this", "that"):
        return True
    if after == "is" and before in (None, "|"):
        # A word that opens the line and has a verb after it is the subject of that verb.
        return True
    # An age after the name, in either the shape people type it: "im saad and im 34", "im saad
    # (34)". The words after the word are only looked at where one of the two links allows it.
    if after in ("and", "|") or (after or "").isdigit():
        for word in list(after_words or ())[:3]:
            if word.isdigit():
                return True
    return False


# The states a person can be in, which are a closed list of their own: hungry and cold are
# ordinary words the lexicon holds as words, so they are not on the feeling list, and a slip of
# one of them was read as nothing at all - "im hongry" was answered "Nice to meet you, Hongry".
# Only the states said of a person are here, and only in the form the pools answer, so a slip of
# any of them reaches the word it is a slip of.
STATES_OF_A_PERSON = frozenset("""hungry thirsty starving famished peckish sleepy tired
    exhausted shattered knackered drained dizzy queasy nauseous bunged freezing frozen cold
    hot warm boiling sweaty bored lonely miserable""".split())


def _a_letter_wrong_in_a_state(word):
    """The one state word `word` is a letter away from, or None.

    This is a whole-letter test, not the vowel-only one `_a_slip_of_a_state` makes, and it is
    only asked where the line itself says the word is how the person is: a letter typed wrong
    is the ordinary slip of a state word ("hungy", "thisty", "colde"), and the state list is
    the closed one, so nothing else in the language is a letter from one of them. The word has
    to be the last word of the clause as well, because "been staring at a screen all day" is a
    letter from "starving" and is not about hunger at all.
    """
    # Only the states of a person, and only a word of five letters or more: a name is a letter
    # from a feeling far more often than a state is, and "im cory" is not "im cry".
    if len(word) < 5 or word in LEXICON or word in lexicon.COMMON_NAMES:
        return None
    found = {state for state in STATES_OF_A_PERSON
             if state[:1] == word[:1] and _a_letter_apart(word, state)}
    if len(found) == 1:
        return found.pop()
    return None


def _a_letter_apart(word, other):
    """True when one letter added, left out, doubled or swapped round makes the other word.

    This is the feeling rule's own test (`_one_letter_apart`) with the consonant let in: people
    do type "hungy" for hungry and "thisty" for thirsty, a consonant left out in the middle,
    and "dizzzy" with one letter doubled. A letter on the front or the end of a whole word is
    still not a slip, which is what keeps "im busy" out of it.
    """
    if _one_letter_apart(word, other):
        return True
    if abs(len(word) - len(other)) != 1:
        return False
    short, long = (word, other) if len(word) < len(other) else (other, word)
    return any(short == long[:i] + long[i + 1:] for i in range(1, len(long)))


def _a_consonant_left_out_of_an_ing_word(word, feeling):
    """True when the only difference is a consonant missing from a word ending in "-ing".

    A vowel is what people leave out of an "-ing" word when the keys are under the fingers
    ("starvng", "annoyng", "depresing"), so a vowel is the whole of the slip the frame and the
    closed feeling list were built to catch. A consonant left out of an "-ing" word is an
    ordinary verb underneath instead, and the feeling on the list is another word: "staring" is
    "stare" with "-ing" on it and only the "v" of "starving" makes it a state, so "been staring
    at a screen all day" was read as "been starving at a screen all day". The frame cannot see
    the difference - "ive been exausted" and "ive been staring" stand in the same place - so the
    letter is what decides.
    """
    if not word.endswith("ing") or len(feeling) != len(word) + 1:
        return False
    i = 0
    while i < len(word) and word[i] == feeling[i]:
        i += 1
    return word[i:] == feeling[i + 1:] and feeling[i] not in VOWEL_SET


def the_feeling_two_letters_are_gone_from(word):
    """The feeling a long word has lost two letters of, or None: "stessd" is "stressed".

    Its own function because the name store has to ask the same question: "im stessd" was read
    as a state and answered "Hi Stessd", and the name was kept for the rest of the chat
    ("whats my name" then said Stessd). A word this long has room for two letters, and the slip
    is always the same shape - letters left out, never swapped - so the test is that the typed
    word is the feeling with one or two letters taken out, first letter kept. Two candidates and
    a common name are refused: "im sarah" and "im katie" are people, not a state.
    """
    if not isinstance(word, str):
        return None
    low = word.strip().lower()
    if len(low) < 6 or low in lexicon.COMMON_NAMES:
        return None
    found = sorted(feeling for feeling in lexicon.FEELINGS if _two_letters_out(low, feeling))
    return found[0] if len(found) == 1 else None


def _two_letters_out(word, feeling):
    """`word` is `feeling` with one or two letters taken out of it, and nothing else changed."""
    if len(feeling) - len(word) not in (1, 2) or word[:1] != feeling[:1]:
        return False
    if _one_letter_apart(word, feeling):
        return False
    rest = iter(feeling)
    return all(letter in rest for letter in word)


def _feeling_without_its_ending(word):
    """"confuse" is "confused": a feeling typed with its ending left off, or None.

    "im confuse", "im annoy", "im bore" and "im excit" are how people type when the ending of
    the word they mean does not come out, and they are words already ("confuse" is a verb), so
    the misspelling fixer may not touch them - but next to "im" they are the feeling. The same
    slip costs the last letter of "nervous", "anxious" and "miserable" ("im nervou", "im anxio",
    "im miserabl"), and it can cost the whole of a longer ending - a whole "-ing", "-l" or
    "-ty": "im gratefu", "im guil", "im awfu", "im anxie", "im dread", "im mourn" and
    "im emotiona" were each answered "Nice to meet you, Gratefu". Only the closed feeling list
    is consulted, and only the endings a feeling word takes, so a name is still a name
    ("im matt", "im justin", "im anna").
    """
    if len(word) < 3 or not word.isalpha():
        return None
    known = lexicon.FEELINGS | lexicon.A_STATE
    # A word that already is the state is not a state with its ending missing: "i am hurt" is
    # hurt, not "hurting", and "cry" is cry, not "crying". The short endings never needed this
    # because no feeling is another feeling with two letters on the end.
    if word in known:
        return None
    for ending in ("ed", "d", "y", "s", "us", "e", "g", "ing", "l", "ty"):
        if word + ending in known:
            return word + ending
    return None


def _a_vowel_left_out_of_a_state(word):
    """The state a short word had a vowel left out of, or None: "spnt" is "spent", "bet" is "beat".

    Only a vowel that was never typed, never a letter changed: a short word with one letter
    changed is usually another word and often somebody's name ("sid" is not "sad"), and no name
    people are given is a state with a vowel missing - the one that looked like it, "don" for
    "done", is on the common names list and is left alone. A word the lexicon knows keeps its
    own meaning ("bat" is not "beat").
    """
    if not 3 <= len(word) < 5 or not word.isalpha():
        return None
    if word in LEXICON or word in lexicon.COMMON_NAMES:
        return None
    found = sorted(state for state in lexicon.FEELINGS | lexicon.A_STATE
                   if len(state) == len(word) + 1 and word in _one_vowel_less(state))
    return found[0] if len(found) == 1 else None


def _one_vowel_less(word):
    """Every way of leaving one vowel out of the word, as a set."""
    return {word[:at] + word[at + 1:] for at, letter in enumerate(word)
            if letter in VOWEL_SET and 0 < at < len(word) - 1}


def reads_as_a_sound(word):
    """True when the word is the sound of a feeling ("board" is bored), not its spelling.

    A module that files a bare word as a name asks this as well, because "im board" is how
    somebody says they are bored, not what they are called. It is a separate question from
    `reads_as_a_feeling`, which is about the word as it is spelt, and it is the caller with the
    whole line in front of it that decides: "my name is board" names a person.
    """
    if not isinstance(word, str):
        return False
    low = word.strip().strip(".,!?;:'\"()").lower()
    if not low or not low.isalpha():
        return False
    from . import kinds
    return kinds.feeling_by_sound(low) is not None


def spelled(word):
    """What the engine's own tables read this one token as, or [] when only a guess would.

    ``repaired_tokens`` also carries the fixer's guesses, and those need the "says more than
    the word did" guard: a cut is not evidence ("ann" collapses to "an", and "an" is not a
    reason to doubt somebody's name). A curated entry is evidence on its own - the table
    says what the word stands for - so "hungrey" is "hungry" even though that is one letter
    shorter, and a module that holds its own list of words asks this rather than re-reading
    the tables.
    """
    if not isinstance(word, str):
        return []
    low = word.strip().strip(".,!?;:'\"()").lower()
    if not low:
        return []
    for table in (lexicon.CHAT, lexicon.EXPAND, lexicon.US_SPELLINGS,
                  lexicon.MISSPELLINGS, lexicon.URGENT_MISSPELLINGS):
        if low in table:
            return table[low].split()
    return []


def _unsays_the_word(word, variant):
    """True when the only change is an un-doubled consonant in front of -ing, -ed, -er, -est.

    Both spellings are English words and they say different things: "hopping" is not "hoping",
    "taping" is not "tapping", "planed" is not "planned". Which one the person meant is nowhere
    in the letters, so the doubled letter in front of an ending is left as it was typed rather
    than guessed at - "island hopping in greece" was read as "island hoping".
    """
    if len(variant) >= len(word):
        return False
    ending = next((end for end in ("ing", "est", "ed", "er") if variant.endswith(end)), "")
    if not ending:
        return False
    stem = variant[:-len(ending)]
    if len(stem) < 2:
        return False
    doubled = stem + stem[-1]
    return word == doubled + ending


def _a_word_of_the_bots(word):
    """Whether this is a word to repair *towards*: the lexicon, or a word the bot's own base writes.

    The repair vocabulary used to be the lexicon alone, so a slip in a word only the bot's cards
    use was left as typed. "rouitne" and "chloesterol" are one swapped pair from "routine" and
    "cholesterol" - both of them things the bot has a card about, and neither of them an everyday
    English word - so nothing was repaired, and the line was read as a word about nothing: the card
    missed, or the slip was said back to the person ("Same for the drippign"). The words the bot
    writes in its own keys and answers are spelled by construction (that is what
    `_words_the_bot_writes` is for), so a slip one letter from one of them is a slip of that word.
    """
    if word in NO_SWAP_TO:
        # A word the bot never puts in place of a slip, whichever class found it: "hagned my
        # washing out" is somebody's washing, not a hanging.
        return False
    return word in BASE or word in _words_the_bot_writes()


OPENERS = frozenset(lexicon.OPENERS.split())


WH_OPENERS = frozenset("what why when where who which whose how".split())


def _slip(word, opener):
    """How `word` is one letter away from `opener`: "missing", "extra" or None.

    A letter swapped for a different one is not counted: in a word this short a swap says
    nothing ("who" and "why" are both one swap from "whn"), while a letter added or left out
    is the shape people type at speed.
    """
    if word == opener or word[:1] != opener[:1] or abs(len(word) - len(opener)) != 1:
        return None
    short, long = (word, opener) if len(word) < len(opener) else (opener, word)
    i = 0
    while i < len(short) and short[i] == long[i]:
        i += 1
    if short[i:] != long[i + 1:]:
        return None
    return "missing" if short is word else "extra"


def fix_opener(word):
    """The opener word `word` is one letter away from, or None when none or two fit.

    Openers of two letters are only reached by un-doubling a letter ("hii" -> "hi"), because
    one letter means too little in a word that short. `normalise` only asks about a word
    nothing else knows, and only where a clause begins.
    """
    if not word.isalpha() or len(word) < 2:
        return None
    doubled = len(word) > 2 and word[-1] == word[-2]
    # Two letters are only worth a repair when they are the bones of a question word: "hw" and
    # "wy" say "how" and "why", while "ha" says nothing about being "has".
    short = len(word) == 2
    fits = []
    for opener in OPENERS:
        shape = _slip(word, opener)
        if not shape:
            continue
        if short and opener not in WH_OPENERS:
            continue
        # A letter typed twice ("heyy" -> "hey") is the only extra letter worth reading as a
        # slip: any other extra letter is usually a real word of its own, and one of those at
        # the start of a line turns a statement into a question ("hash" is not "has", "ways"
        # is not "was", "mary" is not "may", "wars" is not "was", "halve" is not "have").
        if shape == "extra" and not doubled:
            continue
        fits.append((opener, shape))
    # Several openers can be one letter away ("weres" is "were" plus one and "wheres" less
    # one). The end of a word is the part people get right, so a fit that keeps it wins; a
    # last letter typed twice ("heyy") is settled the same way.
    for test in (lambda opener: opener[-1] == word[-1],
                 lambda opener: doubled and opener[-1] == word[-2]):
        if len(fits) > 1:
            kept = [f for f in fits if test(f[0])]
            fits = kept if len(kept) == 1 else fits
        if len(fits) == 1:
            break
    return fits[0][0] if len(fits) == 1 else None


def _plain_word(word):
    """True when this is a real word the engine knows, not something it only guessed at.

    The lexicon also holds the ordinary endings of real words ("worries", "weres"), which is
    what a typo must still be allowed to reach: "weres the best place to park" is "where is",
    and only a word that is real on its own is left alone.
    """
    return word in BASE or word in lexicon.CHAT or word in lexicon.MISSPELLINGS \
        or word in lexicon.EXPAND


def _four_spells_for(word):
    """A leading 4 inside a word is "for": "4get", "4got", "4getting", "4give", "4ever".

    People write the first syllable of a word with the digit, and the word then means
    nothing to any reader: "i keep 4getting things" came back as an echo of the line where
    "i keep forgetting things" answers. Only a 4 in front of a word the engine already knows
    is spelled out, so "i have 4 cats" and "a table for 4" are untouched, and "4tunate"
    stays as typed because "tunate" is not a word. One 4 per word is all people write
    ("4give", never "4give4"), so the rest must be letters. The words this happens to put
    the "for" in front of a g or a vowel ("forget", "forgot", "forgive", "forever"), which is
    what keeps "4night" and "4ward" from being spelled into a word that does not exist.
    """
    if len(word) < 4 or not word.startswith("4") or not word[1:].isalpha():
        return None
    rest = word[1:]
    if rest[0] not in "aeioug":
        return None
    if rest in BASE or rest in lexicon.CHAT or rest in lexicon.MISSPELLINGS or rest in LEXICON:
        return "for" + rest
    return None


def _collapse(word):
    """'sooo' -> 'so', 'pleeease' -> 'please'; a variant that is a real word, else None.

    A word stretched in two places still lands: settling every run at once would take
    "heellooo" to "helo" and throw it away, so the runs are tried in every combination.
    """
    if not re.search(r"(.)\1\1", word):
        return None
    runs = list(re.finditer(r"(.)\1+", word))
    if len(runs) > 3:
        return None
    # Every stretched letter settled at once, in every combination: "heellooo" only reads as
    # "hello" when the e and the o come back to one but the l stays doubled.
    choices = [range(1, min(3, len(match.group(0))) + 1) for match in runs]
    for lengths in itertools.product(*choices):
        variant = word
        for match, length in reversed(list(zip(runs, lengths))):
            variant = variant[:match.start()] + match.group(1) * length + variant[match.end():]
        if variant != word and variant in LEXICON:
            return variant
    return None


def _apostrophe(word):
    """Expand or settle one token that has an apostrophe."""
    if "'" not in word:
        return None
    base, _, rest = word.partition("'")
    if rest == "t" and word.endswith("n't"):
        stem = word[:-3]
        if stem == "ca":
            return ["can", "not"]
        if stem == "wo":
            return ["will", "not"]
        if stem == "sha":
            return ["shall", "not"]
        if stem == "ai":
            return ["is", "not"]
        return [stem, "not"] if stem else None
    if rest == "m":
        return [base, "am"]
    if rest == "re":
        return [base, "are"]
    if rest == "ve":
        return [base, "have"]
    if rest == "ll":
        return [base, "will"]
    if rest == "d":
        return [base, "would"] if base in PRONOUN_BASES else [base]
    if rest == "s":
        if base in PRONOUN_BASES:
            return [base, "is"]
        # A chat word or a misspelling carrying its apostrophe-s is that word and "is", not the
        # bare word: "wot's wrong with my boiler" was read as "wot" alone, so the s the person
        # typed went missing and the line reached the tradesman answer where "what is wrong with
        # my boiler" gets the boiler one. The base goes through the same tables an
        # apostrophe-free token goes through, and only when its repair is one word.
        read = (lexicon.CHAT.get(base) or lexicon.MISSPELLINGS.get(base)
                or lexicon.URGENT_MISSPELLINGS.get(base) or "")
        if read and " " not in read:
            return [read, "is"]
        return [base]
    return None


DIGIT_WORDS = dict(zip("0123456789",
                       "zero one two three four five six seven eight nine".split()))


DIGIT_WORDS.update({str(n): w for n, w in zip(
    range(10, 21),
    "ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen "
    "twenty".split())})


# People type "2" for "to" as often as for "two", and "4" for "for". The next word says
# which reading fits: "2 the shop" and "2 cook" are "to", "2 eggs" is "two", "me 2" is
# "too", "4 lunch" is "for" and "4 eggs" is "four". The number is what people mean most of
# the time, so it is the reading the digit keeps unless the next word asks for another one:
# "i have 4 cats", "meet me at 4", "party of 4" and "4 pm" are all counts.
BEFORE_WORD = frozenset("""the a an my your his her their our its this that these those
me you him us them it""".split())


BEFORE_VERB = frozenset("""go get do make see eat cook buy book call ask tell say try keep
put wear bring take watch read start stop pay save sleep work clean fix check learn study
write send order pick choose plan join find leave stay drink wash boil roast give show help
move sort turn cut fill set talk chat walk run live meet visit play listen wait come sit
stand hold pour chop stir fry bake serve mix add remove park drive catch post share print
sign email text speak change cancel return swap replace freeze heat store wrap pack load
grill steam reheat defrost tidy paint build grow plant have know""".split())


# "4" is "for" only in front of one of these: a determiner or a pronoun ("4 the kids",
# "4 my back") or a thing people do something for ("4 lunch", "4 later", "4 free").
FOR_A = frozenset("""the a an my your his her their our its this that these those
me you him us them one two three""".split())


FOR_OBJECT = frozenset("""lunch dinner tea breakfast supper brunch now later tonight
tomorrow today free once example sure good real ages fun sale keeps christmas weekend
everyone everybody nothing starters afters dessert pudding coffee cake
milk bread butter cheese sugar flour rice pasta petrol diesel fuel wine beer juice""".split())


# "4 lunch" at the start of a line is still "for lunch"; "4 tomorrow please" is four people,
# so only the food words are read that way with nothing in front of them.
FOR_MEAL = frozenset("""lunch dinner tea breakfast supper brunch starters afters dessert
pudding cake""".split())


# "for" cannot follow a be-verb, so "we are 4 today" is four today, not "for today".
BE_VERBS = frozenset("am is are was were".split())


# "2" is "too" in front of an adjective the way people say it: "2 much salt", "2 late".
TOO_A = frozenset("""much many late early soon long often hard fast big small hot cold
tired busy expensive cheap old young loud noisy sweet salty spicy easy quick heavy light
slow warm dark bright strong weak soft loud""".split())


# "2" at the end of a clause is "too" when the line already said who (or what) it is about:
# "me 2", "love it 2". After anything else it is the number: "see you at 2", "a table for 2".
TOO_AFTER = frozenset("me you us him her them i we they it".split())


# A "2" at the end of a line after one of these is "to", not "too" and not the number: "what u
# up 2" and "i will get back 2" are the same "to" as "what u up to", and read as "two" they
# reached nothing at all. "in" and "on" are left out on purpose: "im in 2" is "i'm in too".
TO_AFTER = frozenset("up down over back out round through along".split())


# A negation in front of the "2" is what makes the next word an adjective being graded rather
# than a thing being counted: "not 2 bad" and "not 2 keen" are "too", while "2 bad eggs" and
# "not 2 minutes away" are numbers. The words here are the ones a person grades that TOO_A does
# not already hold; the negation is the whole of the safety, so "2 bad eggs" is untouched.
A_NEGATION_BEFORE = frozenset("not".split())


TOO_A_GRADED = TOO_A | frozenset("""bad shabby keen happy far sure worried good pleased glad
    proud cross upset annoyed safe well fun useful handy honest bright""".split())


# A digit next to one of these is a number, not a word that sounds like it: "4 x 5" is four
# times five, and "take 2 a day" is two a day.
OPERATORS = frozenset("x * / + - plus minus times divided squared".split())


COUNTS = frozenset("a an per each".split())


# A number counts something: a plural ("4 eggs", "4 ways"), a unit ("4 months", "4 o'clock",
# "4 quid") or a word that is not a thing at all ("the 4 of us", "at 4 pm", "4 and 7", "grade 4
# in gcse maths"). In front of anything else the "4" is not counting, so it is "for": "tips 4
# sleep", "time 4 bed", "reasons 4 leaving", "advice 4 new mums", "stuck 4 childcare". Reading
# those as counts is why "any tips 4 sleep" went off as "any tips four sleep" and reached
# nothing at all.
COUNT_UNITS = frozenset("""year month week day hour minute second mile miles kilometre kilo
gram litre pint cup quid pound euro dollar pence percent point star item person people child
children man men woman women foot feet grand ton bob
yr yrs mth wks wk hr hrs min mins sec secs km cm mm kg g mg ml cl lb lbs oz ft yds yd
tsp tbsp
pack slice seat piece wheel toaster suite star speed door
january february march april may june july august september october november december
jan feb mar apr jun jul aug sep sept oct nov dec""".split())


# A number in front of one of these is a count when another noun follows it: "a 4 bed house",
# "a 3 door car". "ready 4 bed" is still "for", so the word itself never counts on its own.
COMPOUND_HEADS = frozenset("bed class bay birth seat".split())


COMPOUND_TAILS = frozenset("""house flat home room rooms car cars van cottage bungalow
door doors window windows drive suite garden""".split())


# Written after a digit, these are not things, so the digit is counting: "at 4 pm", "4 o'clock",
# "the 4 of us", "4 and 7". A clock time is the one a person types most, so its spellings are all
# here: "4pm", "4 pm", "4 o'clock", "4 o clock".
NOT_COUNTED_AFTER = frozenset("""and or but so in on at of to by as is was were for with from
about than per each every a an the my your his her their our its this that these those
more fewer less most other others another few out tomorrow today tonight now later soon twice please
am pm oclock o'clock o’clock""".split())


# A number in front of a noun that is itself followed by a noun is counting the first one: "a 4
# bedroom house", "a 4 seater car", "a 4 course meal", "a 4 poster bed". The tail is what says
# so, which keeps the purpose reading where the noun ends the line - "tips 4 sleep", "time 4
# bed", "stuck 4 childcare" - and where what follows is a time or a rate - "4 work tomorrow".
# The head of a compound says how big the thing is ("4 seater", "4 bedroom"), so an adjective
# is not one: "advice 4 new mums" is advice for them, not four new mums. And the tail has to be
# the noun the compound names, not a clause starting up again ("time 4 bed i reckon").
NOT_A_COMPOUND_HEAD = frozenset("""new old small big cheap little large lovely nice good bad
first second third last next own same whole different other another
i me you him her us them he she we they it""".split())


NOT_A_COMPOUND_TAIL = frozenset("""i we they he she it you me us them there thats that's
and or but so if when because though anyway""".split())


def _counts_a_compound(head, tail):
    """Whether a number `head tail` counts the head rather than meaning "for" it."""
    if not head or not tail or head == "|" or tail == "|":
        return False
    if head.isdigit() or tail.isdigit():
        return False
    if head in NOT_COUNTED_AFTER or tail in NOT_COUNTED_AFTER:
        return False
    if head in NOT_A_COMPOUND_HEAD or tail in NOT_A_COMPOUND_TAIL:
        return False
    if head.endswith("ing") or tail.endswith("ing"):
        return False
    return True


# Written after one of these, a number is the label of a thing rather than a purpose: a school
# year, a class, a question. "year 4 homework" is year four's homework and "class 4 teacher"
# teaches class 4, so nothing that follows can turn the number into "for". These are the words a
# number can be *in* or *on* and that are not a thing anybody asks for - you are in year 4, on
# question 4 - which is what separates them from a word that only happens to come before a digit
# ("time 4 bed", "tips 4 sleep", "stuck 4 childcare").
#
# A table, a room, a bus, a seat and a team are the other way round: they are things people ask
# for, so "table 4 two" is a booking for two and "room 4 the night" is a room for the night. Those
# stayed out of the list, because the digit after them is the purpose and the food answer needs it.
A_LABEL_BEFORE = frozenset("""year years class classes grade grades form forms level levels stage
stages part parts section sections page pages question questions chapter chapters episode episodes
lesson lessons unit units term terms step steps""".split())


# A number after one of these is how many of a thing is taken or used: "take 4 paracetamol",
# "i took 4 ibuprofen", "add 4 potatoes". "need" and "want" are not here, because "i need 4
# childcare" is the purpose and not a count.
NUMBERS_BEFORE = frozenset("""take took takes taking ate eaten eat drink drank drinks
buy bought buys get got gets use used uses add added adds gave give gives
a an the my your his her their our another first last only just""".split())


def _counts_a_thing(word):
    """Whether a number in front of this word is counting something."""
    if not word or word == "|":
        return True
    word = (word.split() or ["|"])[0]
    if word.isdigit() or word in COUNT_UNITS or word in NOT_COUNTED_AFTER:
        return True
    return len(word) > 2 and word.endswith("s") and not word.endswith(("ss", "us", "is"))


REPEAT_ONCE = frozenset("""i you we they he she it me my the a an to and of in is am are
was were do does not at on for""".split())


REPEAT_ONCE_SUBJECTS = frozenset("i you we they he she it u".split())


def _once_only(tokens):
    """Drop a word typed twice in a row when it is one a line never says twice.

    "i dunno" expands to "i i do not know" because the chat spelling carries its own "i", and
    "the the" and "to to" are the same kind of slip. An adjective or a word like "very" is kept,
    because people mean it twice.
    """
    out = []
    for token in tokens:
        if out and token == out[-1] and token in REPEAT_ONCE:
            continue
        out.append(token)
    return out


# Chat-speak drops the subject: "am off to bed" is "i am off to bed", "was thinking of quitting"
# is "i was thinking of quitting". A yes/no question turns the subject round instead ("am i too
# late", "was the film good", "have you got a minute"), so the subject is missing exactly when
# nothing that could be one follows the auxiliary. Putting the "i" back makes the rest of the
# engine read the line the way it reads "im off to bed", which is what the person meant: without
# it, "am off to bed" was read as a question and handed to the "I don't know, try a search" hedge.
AUX_OPENS = frozenset("am is are was were have has had been".split())


# The ones where the dropped subject is the person typing: "am off to bed", "was thinking of
# quitting", "have no idea". ("were shattered", "are knackered" and "has gone quiet" drop a "we"
# or a "he" that cannot be put back safely, so the reading is fixed for those, the words are not.)
DROPPED_SUBJECT_AUX = frozenset("am was have".split())


_SUBJECTS = frozenset("""i you we they he she it there that this these those one anyone someone
    everyone nobody nothing none who which what""".split())


# Words that are only ever a predicate after an auxiliary: "am off to bed", "am knackered",
# "was well worth it". Nothing that can name a thing goes in here, and "there" and the subject
# negations stay out: "is there anything for a cold" and "is nobody home" are questions.
_PREDICATE_ONLY = frozenset("""going gonna off out away back home up down well knackered
    shattered exhausted drained starving fine alright okay ok rubbish great late here""".split())


# A state of the person is a whole predicate on its own, so "am", "was" and "were" in front of one
# have lost their subject: "were hungry", "was shattered all week", "am freezing". The list is the
# states a person can be in where the feeling is what the line is about - hungry, skint, soaked -
# and not a thing the state word also names ("were down to the last tenner" is a shortage, and a
# determiner after "was" keeps it a question: "was the film good").
_A_STATE_OF_THE_PERSON = frozenset("""hungry thirsty starving famished peckish busy rushed
    freezing frozen broke skint brassic sleepy
    dizzy tired shattered knackered exhausted drained ill unwell poorly sick lousy rough
    down low fed up miserable sad happy chuffed pleased livid fuming cross annoyed upset gutted
    relieved worried anxious nervous scared frightened stressed""".split())


_SUBJECTLESS_AUX = frozenset("am was were".split())


# The words people put in front of a state and nowhere else: "were both tired", "am so relieved".
# A determiner is not one of them, so "was that ok" and "was the film good" still ask.
_STATE_FILLER = frozenset("""both so really very totally absolutely properly too all quite still
    always just completely dead kind of a bit""".split())


# What may come after the state and leave it the whole predicate. The state is the last thing said
# about the person, so what follows it is the end of the clause, an intensifier, a preposition that
# starts the reason or the time ("were tired after", "am so busy at the moment"), a determiner, a
# time word, or a joining word. A plain noun after it means the state was the first half of a
# compound and the line asks about a thing: "was sick leave ok" and "was happy hour good" were
# being read as a person saying how they feel, which was confidently wrong where the line before
# only hedged.
_STATE_TAIL = frozenset("""at in on for after before by since till until from about with around
    over through during the a an this that these those my your his her their our
    last next today tonight tomorrow yesterday week weekend morning afternoon evening night
    month year day now then again still too also already anymore lately recently though but and
    so because when while if all every up out off sick stiff rotten
    to be been being had got go going""".split())


# The auxiliaries that cannot take an "-ing" word for a subject, so one after them means the
# person was left off the front of the line.
_SUBJECTLESS_ONLY = frozenset("am was".split())


# A negation after "have" is not a subject either ("have no idea", "have nothing to wear").
_HAVE_NEGATIONS = frozenset("no none nothing".split())


# Nor is a participle: "have got a bad head", "have had a rough week" are the person saying what
# they have, with the "i" left off the front, and reading them as questions cost the health answer
# and got a search hedge instead. "have got a minute" is the one that really is the ask, so a
# request word after the thing keeps the line a question.
_HAVE_PARTICIPLES = frozenset("got had been seen made taken spent".split())


_HAVE_THING = frozenset("a an the my our his her their your some this that".split())


_HAVE_ASKING = frozenset("minute moment sec second mo chance word".split())


# What can follow a participle and leave it as the verb: "was thinking **of** quitting", "was
# making tea **and**". A determiner or a noun after the participle means the participle was naming
# a thing instead: "is cooked chicken still ok" and "is cracking your knuckles bad" ask, so they
# are left alone.
_AFTER_PARTICIPLE = frozenset("""of to for in on at with about from by up out off over through
    into onto and but so or because if when while then that than as not never ever too also
    just""".split())


def _opener_is(word):
    """'wots'/'whatz'/'whyz' -> ['what', 'is'] / ['why', 'is'], or None.

    People run the "s" of "is" onto the question word and often spell the question word as
    they say it: "wots the best way", "whyz my boiler losing pressure". Neither half is a
    typo the other readers can find - "wots" is not one letter from an opener, and it is
    not in the spelling tables - so the line reads as news and gets a "noted" back. The
    stem is read the way the chat table reads it ("wot" -> "what"), and only a question
    word is ever completed this way.
    """
    if len(word) < 4 or word[-1] not in "sz":
        return None
    stem = word[:-1]
    if stem in WH_OPENERS:
        return [stem, "is"]
    spelled = (lexicon.CHAT.get(stem) or lexicon.EXPAND.get(stem)
               or lexicon.MISSPELLINGS.get(stem) or "").split()
    if len(spelled) == 1 and spelled[0] in WH_OPENERS:
        return [spelled[0], "is"]
    return None


# "cause" is both the chat spelling of "because" and an ordinary verb and noun: "i dont want to
# cause trouble", "it could cause problems", "what is the cause of the fire". The chat table
# answered `cause` with "because" wherever it stood, so those became "because trouble" and "the
# because of the fire". A repair belongs in the position that means it, so "because" is read only
# where the line goes on with a subject or an auxiliary - the shape that follows "because" - and
# the verb and noun keep their word.
CAUSE_A_SUBJECT_FOLLOWS = frozenset("""i im ive id ill you youre youve we were weve they theyre
    theyve he hes she shes it its that thats this these those there theres my your our his her
    their if when whenever while since as so and but or not never no nobody nothing everyone
    everybody someone something anyone anything am is are was were do does did dont doesnt did
    didnt cant cannot couldnt wont wouldnt shouldnt isnt wasnt arent hasnt havent hadnt u ur ya""".split())


# What can follow "the" and make it a clause rather than the noun's article: "cause the bus was
# late" is because the bus was late, while "cause the problem" is the verb with its object.
CAUSE_A_CLAUSE_VERB = frozenset("""is was were are am has had have will would can could did does
    do dont doesnt didnt wont cant cannot isnt wasnt arent hasnt hadnt""".split())
