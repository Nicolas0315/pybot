"""Part 5 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""
import re

from . import lexicon
from .normalize_part_01 import (
    LEXICON, SAID_OUT,
)
from .normalize_part_02 import (
    STATES_OF_A_PERSON, _a_letter_wrong_in_a_state, _a_vowel_left_out_of_a_state,
    _feeling_without_its_ending, A_LABEL_BEFORE, A_NEGATION_BEFORE, BEFORE_VERB, BEFORE_WORD,
    BE_VERBS, COMPOUND_HEADS, COMPOUND_TAILS, COUNTS, FOR_A, FOR_MEAL, FOR_OBJECT, NUMBERS_BEFORE,
    OPERATORS, TOO_A, TOO_AFTER, TOO_A_GRADED, TO_AFTER, _counts_a_compound, _counts_a_thing,
    spelled, _apostrophe,
)
from .normalize_part_03 import (
    A_PERIOD_FOLLOWS, DEMONSTRATIVE, MOTION_BEFORE,
)
from .normalize_part_04 import (
    _token, _is_possessive, _plain_chat,
)


def reads_as_a_feeling(word):
    """True when this word is a feeling word, or a slip of one the engine repairs.

    The reading already lowers a misspelt feeling to that feeling, so a module that takes a
    bare word for a name has to ask the same question, or a person typing one word about
    themselves is welcomed by name: "im knackerd" was answered "Nice to meet you, Knackerd".
    A name that the one-edit fixer would bend is still a name ("im matt", "im justin"), and so
    is a word that only looks like a state.
    """
    if not isinstance(word, str):
        return False
    low = word.strip().strip(".,!?;:'\"()").lower()
    if not low or not low.isalpha():
        return False
    if _feeling_without_its_ending(low) or _a_letter_wrong_in_a_state(low):
        # A state word with a letter typed wrong is how they are, not what they are called.
        # This one is asked without the line in front of it, so only the words that are a letter
        # from a state and nothing else are taken: "im hungy" is not a name, "im shy" is.
        return True
    if low in lexicon.SOUNDS_LIKE_A_FEELING:
        return True
    if any(word in lexicon.FEELINGS or word in lexicon.A_STATE
           or word in STATES_OF_A_PERSON
           for word in _token(low, [], alone=True)):
        return True
    # The "-d" dropped off a feeling: "im confuse" is "im confused", "im annoye" is "im annoyed".
    # The letter is put back on the word as typed, not on the repaired one, so a name the fixer
    # bends is left alone ("ann" becomes "an", and "and" is on the feeling list).
    if low + "d" in lexicon.FEELINGS | lexicon.A_STATE:
        return True
    # A short state with a vowel left out of it is still how they are: "im spnt" is spent,
    # "im bet" is beat, "im wrn" is worn, "im wepy" is weepy. `_near_a_feeling` refuses a word
    # this short on purpose, so the repair never happens, but the name reader has to know the
    # word is a state or it welcomes the person by it: "im spnt" and "im bet" were answered
    # "Nice to meet you, Spnt" and "Nice to meet you, Bet".
    if _a_vowel_left_out_of_a_state(low):
        return True
    return False


def repaired_tokens(word):
    """What the engine reads this one token as, alone: "gd" is "good", "y" is "why".

    A module holding its own list of words that cannot be a name asks this rather than the
    private table, so "im gd" is caught by the same lists that hold "im good".
    """
    if not isinstance(word, str):
        return []
    low = word.strip().strip(".,!?;:'\"()").lower()
    if not low:
        return []
    return list(_token(low, [], alone=True))


def _digit_word(token, before, after, after_after=None):
    """The word "2" or "4" stands for where it sits, or None to keep it a number.

    The next word says which reading fits: "2 the shop" and "2 cook" are "to", "2 eggs" is
    "two", "me 2" is "too", "4 lunch" is "for" and "4 eggs" is "four". The number is what
    people mean most of the time, so it is the reading the digit keeps unless the next word
    asks for another one: "i have 4 cats", "meet me at 4", "party of 4", "4 pm" and
    "we are 4 today" are all counts.
    """
    if token not in ("2", "4"):
        return None
    if (after or "").lower() in ("yr", "yrs"):
        # "a 2 yr old" counts years, and the chat table would otherwise read the `yr` as "your"
        # and turn the number into "to".
        return "two" if token == "2" else "four"
    before = before or "|"
    # The words either side are read the way the chat table reads them ("/dont/" is "do not"),
    # and the word nearest the digit is the one that decides: the last of the one before it and
    # the first of the one after it.
    spelled = lexicon.CHAT.get(before) or lexicon.EXPAND.get(before) or before
    spoken_before = (spelled.split() or ["|"])[-1]     # "dont" -> "not", the word before the digit
    after = lexicon.CHAT.get(after, after) if after else "|"
    after = (after.split() or ["|"])[0]
    number = "two" if token == "2" else "four"
    if after in OPERATORS or before in OPERATORS:
        return number
    if after in COUNTS and (before in BEFORE_VERB or before in TOO_AFTER or before == "|"):
        tail = lexicon.CHAT.get(after_after, after_after) if after_after else "|"
        tail = (tail.split() or ["|"])[0]
        if tail in A_PERIOD_FOLLOWS or tail == "|":
            return number      # "take 2 a day" is two, and "4 a week" is four
        return "for"           # "what can i do 4 a sore throat": a thing, not a rate
    if spoken_before in A_LABEL_BEFORE and not after.isdigit():
        return number          # "year 4 homework", "class 4 teacher", "table 4 tomorrow"
    if token == "2" and before in MOTION_BEFORE and after not in A_PERIOD_FOLLOWS:
        return "to"             # "going 2 spain" and "off 2 bed", but "going 2 weeks" is two
    if after in DEMONSTRATIVE:
        after_after = lexicon.CHAT.get(after_after, after_after) if after_after else "|"
        after_after = (after_after.split() or ["|"])[0]
        if after_after in A_PERIOD_FOLLOWS:
            return number      # "i did 4 this week" counts days, it is not "for this week"
    if token == "2":
        if before in TO_AFTER and (after == "|" or after in UP_TO_TAGS):
            return "to"             # "what u up 2", "back 2 mate"
        if after == "|":
            return "too" if before in TOO_AFTER else number
        if after in TOO_A:
            return "too"
        if after in BEFORE_WORD or after in BEFORE_VERB:
            return "to"
        if after in TOO_A_GRADED and spoken_before in A_NEGATION_BEFORE:
            return "too"        # "not 2 bad", "not 2 keen", "not 2 minutes" stays a count
        return number
    if before in BE_VERBS:
        return number
    if after in FOR_A:
        return "for"
    if after in FOR_OBJECT and (before != "|" or after in FOR_MEAL):
        return "for"
    if after.isdigit() and not before.isdigit():
        return "for"          # "waited 4 20 mins": a count is never written twice
    if after_after is not None:
        head = after
        tail = lexicon.CHAT.get(after_after, after_after) if after_after else "|"
        tail = (tail.split() or ["|"])[0]
        if head in COMPOUND_HEADS and tail in COMPOUND_TAILS:
            return number     # "a 4 bed house" counts the beds, "ready 4 bed" is for bed
    if before in NUMBERS_BEFORE and not _counts_a_thing(after):
        return number         # "take 4 paracetamol" is four tablets, not four for
    if after_after is not None:
        tail = lexicon.CHAT.get(after_after, after_after) if after_after else "|"
        tail = (tail.split() or ["|"])[0]
        if _counts_a_compound(after, tail):
            return number     # "a 4 bedroom house", "a 4 course meal", "a 4 seater car"
    if not _counts_a_thing(after):
        return "for"          # "tips 4 sleep", "time 4 bed", "stuck 4 childcare"
    return number


def _lookahead(words, index, n=3):
    """The next few tokens as the reading will have them ("thinkin" -> "thinking").

    A line typed in a hurry leaves the subject off and misspells the word after it: "am thinkin
    of jackin in me job". Whether the subject is missing depends on the word the reader will see,
    not the one that was typed.
    """
    out = []
    for word in words[index + 1:index + 1 + n]:
        if word == "|":
            break
        out.append(_token(word, [])[0] if _token(word, []) else word)
    return out


# "were" at the front of a line is "we are" only in front of a word that says how you are or what
# you are doing: a state ("were shattered", "were gutted", "were broke this month"), an -ing verb
# ("were thinking of getting a cat", "were driving up to scotland") or a word that leads to one
# ("were so tired", "were all gutted", "were not happy"). The state words are spelled out here
# rather than taken from `lexicon.FEELINGS`, because that list is for a typo of a feeling and this
# is a closed list of what can follow "were" for "we are".
_WERE_STATE = frozenset("""gutted shattered exhausted knackered tired worried stressed anxious
    frightened scared annoyed angry furious upset sad unhappy miserable depressed lonely bored
    happy glad pleased proud relieved grateful shattered wiped drained bushed sleepy sick ill
    unwell poorly broke skint done fine ok okay stuck sorted lost ready low""".split())


# A word that can only be the start of "we are": nobody asks a question with these after "were".
_WERE_ARE = frozenset("gonna gunna".split())


# The -ing words that are what a person is doing rather than a thing: "were getting a cat",
# "were camping near oban". A thing that ends in -ing ("were wedding photos allowed", "were
# parking available") is not here, and keeps its "were".
_WERE_DOING = frozenset("""thinking having going coming driving flying travelling traveling
    staying doing getting making taking working playing visiting eating cooking watching
    planning trying looking waiting hoping wondering moving camping hiking jogging running
    walking cycling swimming skiing sailing fishing gardening studying revising rehearsing
    baking painting decorating renovating unpacking babysitting feeling jogging""".split())


# The list above is the doings people write most, and it is closed, so every other doing kept its
# "were" and the line was read as a question about a thing: "were selling the flat", "were
# adopting a dog", "were fighting a lot" and "were arguing all the time" were all answered "I
# don't know enough to answer that honestly. A search should sort you out." The word after the
# doing is what separates the two shapes. A doing takes a determiner, a particle or a preposition
# after it ("selling the flat", "breaking up", "arguing all the time", "struggling with money"),
# and a thing that merely ends in -ing takes a noun ("wedding photos", "morning people") or an
# adjective ("parking available"), and that is a question about the thing. So any doing the engine
# knows, with one of these after it, is "we are"; a noun or an adjective there keeps the "were".
_AFTER_A_DOING = frozenset("""a an the my your our their his her its this that these those some
    any no every each another all both just still quite really very too so not up out off away
    back over down around together apart through in on at to with for from about into onto by of
    and or but because while when if i you we they he she it me us them him there here""".split())


# The words that come between "were" and the state: "were so tired", "were all gutted", "were
# not happy", "were gonna be late". The word after one of these decides it.
# The prepositions that open a place or a state after "we are": "were in york", "were near
# bristol", "were at my mums", "were up in scotland", "were on the train". At the front of a
# clause there is no subject in front of the "were", so the past tense of the plural cannot be
# what was meant, and the only other reading - a question about a thing ("were dogs allowed",
# "were parking available") - needs a noun after it, not a preposition. These lines kept their
# "were" and reached the search hedge ("were in york" was answered "I don't know enough to
# answer that honestly. A search should sort you out quickly"), while the same line with the
# apostrophe was read: "we're in york" got the acknowledgement, "we're at my mums" was noted.
_WERE_PLACE = frozenset("in at near up down out over round around on inside outside".split())


# What says the past tense was meant after all: "were in york last week" is about a week that
# has gone, and reading it as "we are in york last week" is a line nobody says. A time word
# right after the preposition keeps the "were".
_WERE_IN_THE_PAST = frozenset("""last yesterday then earlier previously ago once before
    afterwards that those""".split())


# Who a lead-in word can stand in front of in a question: "were both of them there", "were
# all of us late". These keep the "were", because the question is about who was there.
_AFTER_A_LEAD_IN_SUBJECT = frozenset("""i you we they he she it them us him her me of""".split())


_WERE_LEAD_IN = frozenset("""so not too very really all both just still quite pretty always
    never literally definitely probably already almost nearly gonna gunna about""".split())


# The finite verbs a line starts with when it starts with "were" for "where": "were is my
# wallet", "were do i put it", "were have you been".
_A_QUESTION_VERB = frozenset("""is are was were am do does did can could would should will
    shall may might must has have had""".split())


def _were_for_another_word(before, after, after_after=None):
    """What "were" at the front of a line stands for, or None to keep it as it was typed.

    The front of a line is where a question puts "were" too, so the word after it decides which
    word was meant. In front of a finite verb it can only be "where" ("were is my wallet", "were
    do i put it", "were have you been"), because that word is the verb and not a subject. In
    front of a state or a doing it is "we are" with the apostrophe left off ("were shattered",
    "were thinking of getting a cat"), and a lead-in word is looked through for the same thing
    ("were so tired", "were all gutted", "were not happy"). Every other word keeps the "were" it
    was typed with, because a question about a thing is asked the same way: "were dogs allowed",
    "were parking available", "were the kids ok", "were you at the party".

    "Were" further into the line is the past tense of the plural ("they were late", "so were
    gutted") and is never touched: only the front of a line, or the front of a clause.
    """
    if before not in (None, "|"):
        return None
    if after in (None, "|"):
        return None
    if after in _A_QUESTION_VERB:
        return ["where"]
    if after in _WERE_STATE or after in _WERE_DOING or after in _WERE_ARE:
        return ["we", "are"]
    if after in _WERE_LEAD_IN:
        if after_after in _WERE_STATE or after_after in _WERE_DOING:
            return ["we", "are"]
        if after_after is not None and _a_doing(after_after):
            return ["we", "are"]
        if after_after in _AFTER_A_LEAD_IN_SUBJECT:
            # "were both of them there", "were all of us late": a lead-in word in front of
            # who was there is a question about them, and the plain contraction would read
            # "we are both of them there". The word is kept, which is what was typed.
            return ["were"]
        return None
    if _a_doing(after) and (after_after is None or after_after in _AFTER_A_DOING):
        return ["we", "are"]
    if after in _WERE_PLACE and after_after not in _WERE_IN_THE_PAST:
        return ["we", "are"]
    return None


def _a_doing(word):
    """Whether a word ending in -ing is a doing rather than a thing: "breaking", "selling".

    Only a word the engine knows is read this way, and the g may be left off the way people type
    it ("were goin out tonight"). What follows decides which of the two it is; this says only
    that the word itself could be the doing.
    """
    if not word:
        return False
    bare = word.replace("'", "")
    if bare.endswith("ing"):
        return bare in LEXICON or bare[:-3] in LEXICON
    if bare.endswith("in") and len(bare) >= 6:
        return bare in LEXICON or bare[:-2] in LEXICON
    return False


# "what you up to" typed as a number: the question people open a message with, and nothing else.
# The same letters also name a code, a password or a username ("the wifi code is wu2", "my mate
# text me wuu2"), so the word is read where the line opens with it and left as it was typed
# anywhere else - a code keeps its answer and the question still gets one.
UP_TO_SPELLINGS = frozenset("wuu2 wu2 wyu2 wuut".split())


# The openers people type for "what are you": "watcha up to", "whatcha doing", "wotcha been up
# to". No dictionary has any of them, and the word after says which ask it is - "up to", "doing"
# and "been" are the bot's own time, and "mean" ("whatcha mean") is not - so only those repair.
# Read as written they named no ask at all: "watcha up to" got the listening line and "whatcha
# doing today" was said back to the person as news.
WHAT_ARE_YOU_SPELLINGS = frozenset("watcha whatcha wotcha watchu whatchu watchya whatchya".split())


WHAT_ARE_YOU_AFTER = frozenset("up doing doin do been".split())


# The words that turn a typed "c" into "see": the person it is addressed to, and nothing else.
LETTER_C_IS_SEE = frozenset("u ya you yeah yah".split())


UP_TO_LEADS = frozenset("""so ok okay oh ah and but well just hi hey hiya hello right then now
    anyway""".split())


# What may follow the spelling and leave it the whole question: the words people put around it
# ("wuu2 mate", "wuu2 lol", "wuu2, you ok" - the comma starts another clause), and nothing else.
UP_TO_TAGS = frozenset("""mate hun love pet duck sunshine hen flower chuck dear pal buddy friend
    guys folks all both then though now lol haha ha x xo xx""".split())


# A question opener typed onto the word after it: "isit ok to eat this", "doyou think i should",
# "shouldi take it". People glue the two words when they type quickly, and the line then has no
# opener the reading knows, so it is read as a statement and answered with the stock "is there
# anything you'd like a hand with". The two lists are closed so a real word can never be split.
GLUED_LEFT = frozenset("is do does did can could would will should have are was were am "
                       "what whats where wheres when why how hows who whos".split())


GLUED_RIGHT = frozenset("it that this there they you i we he she your my "
                        "much long many the can should do does is are will would could did".split())


GLUED_COLLAPSE = {"itthere": ["there"]}


# A name typed lower case can wear a question opener as its first letters: "dodo" is a bird,
# "isis" is a cat and "didi" is a person. Two shapes give them away, and each is worth more than
# the lines it costs, because the split turns a piece of news into a question about nothing.
GLUED_DO = frozenset("do does did".split())


GLUED_AFTER_A_DO = frozenset("is are was were am will would can could should shall may might "
                             "must wont wouldnt cant couldnt shouldnt mustnt shant mightnt".split())


def _a_doubtful_split(pieces, after=None):
    """True when the words a glued token would be cut into are a name rather than a question.

    "dodo wont eat" is "do do wont eat" and "isis is my cat" is "is is is my cat": a question
    never says its first two words the same, so a split that does is a name. "didi is coming
    round" is "did i is coming round": no do-form is followed by a be-form or a modal, so the
    opener there is a name too. A pet or a person typed lower case keeps its line as the news
    it was.
    """
    if len(pieces) > 1 and pieces[0] == pieces[1]:
        return True
    return (pieces[0] in GLUED_DO and isinstance(after, str)
            and after in GLUED_AFTER_A_DO)


# "i" typed onto the word after it, which is the same slip the question openers have and costs
# more: every distress frame a person types starts with "i", and a glued one reads as no frame at
# all - "idont want to be here", "icant go on" and "iwant to die" were each "I'm listening - say
# more if it helps" while the spaced line got the crisis card. Only a word that can follow "i" is
# in the list, and a token already in the lexicon is never split, so "ill", "ive", "iron" and
# "island" keep their meaning.
I_GLUED = frozenset("""dont cant wont didnt doesnt havent havnt couldnt shouldnt wouldnt isnt
    wasnt want feel need know think hope wish hate love miss just also really always never got
    went have had will would should could might must am was did saw live work been told said
    tried lost quit moved found bought sold left met heard broke failed cried slept woke rang
    asked felt started stopped changed forgot paid spent took gave kept began ran walked drove
    ate drank won hired retired dumped applied booked cancelled emailed phoned texted replied
    agreed signed decided hated loved missed needed wanted hoped knew thought""".split())


# The same slip with somebody else in front of the word: "wedont have any money", "youdont
# understand", "shedoesnt ring back". A word that can follow "i" can follow these, so the table is
# the same one; only the pronoun is new.
# "it" is left out on purpose: "itisnt working" and "itdoesnt matter" are fragments a reader can do
# nothing with, and the split only made them shorter ("Fair enough" to "itisnt working"). The
# speaker's own pronouns are the ones that carry a frame.
# "u" is the chat form of "you" and it is typed onto the word beside it the same way: "udont
# understand", "ucant come", "uknow what i mean". Only a token that is not a word of its own is
# looked at and the rest of it has to be a word that follows "i", so "under", "until", "usual"
# and "upset" keep their meaning.
A_PRONOUN_GLUED = ("u", "i", "we", "you", "they", "he", "she")


# The two halves of "i am" said as one word, typed onto the word after them: "imso tired",
# "imstill awake", "imdone with today", "ivegiven up". The pronoun table above reads "i" plus a
# verb, and "im" is not a pronoun, so the whole token stayed as it was: "imdone with today" was
# answered "Noted: imdone with today." - the line read back with a word no one writes - and
# "imstill awake" lost the advice "i am still awake" gets. Only the words a person really types
# after "im" and "ive" are listed, so "image", "impact", "import", "imogen" and "ivory" stay
# whole words.
A_PRONOUN_STATE = {
    "im": frozenset("""not so sorry still done going glad happy sad fine ok okay afraid worried
        tired starving hungry thirsty freezing boiling home back here sure just really trying
        working off out up sick lost confused angry upset lonely scared nervous bored at on in
        sitting lying waiting
        struggling stressed fed exhausted overwhelmed anxious depressed panicking hopeless
        worthless gutted furious annoyed irritated shattered unwell ill hurt aching shaky dizzy
        sleepless restless moody numb broke skint stuck busy late""".split()),
    "ive": frozenset("""given got been had never just tried lost done seen told said finished
        started stopped found made taken read heard watched eaten bought moved left paid spent
        decided noticed asked called checked waited worked lived known thought wanted needed
        felt learned kept written broken forgotten
        only already finally recently lately quit joined applied booked sent posted texted
        emailed ordered become grown gained""".split()),
}


_PLACES_SAID_WHOLE = [None]


def _a_place_said_whole(bare):
    """True when the whole token is a place the bot knows, so it is not a pronoun and a verb.

    "iran is in the news" is a country, and only by accident "i" + "ran"; the same is true of any
    country whose name happens to start with a pronoun. The list is the bot's own, so a verb added
    to `I_GLUED` later cannot take a country with it, and a name from `COMMON_NAMES` is refused the
    same way.
    """
    if bare in lexicon.COMMON_NAMES:
        return True
    places = _PLACES_SAID_WHOLE[0]
    if places is None:
        try:
            from bot.knowledge.geography import COUNTRIES
            places = frozenset(COUNTRIES)
        except Exception:
            places = frozenset()
        _PLACES_SAID_WHOLE[0] = places
    return bare in places


def _a_pronoun_said_together(token):
    """The pronoun and the word it is typed onto, or None.

    The apostrophe is kept, because that is how the person typed it and the readers already know
    "can't" and "don't": "ican't go on" is "i can't go on", which is the crisis line, while the
    glued token was no line at all.
    """
    bare = token.replace("'", "").replace("\u2019", "")
    if _a_place_said_whole(bare):
        return None
    for who, after in A_PRONOUN_STATE.items():
        if bare.startswith(who) and bare[len(who):] in after:
            return [who, bare[len(who):]]         # "imso", "imdone", "ivegiven"
    for who in A_PRONOUN_GLUED:
        if bare.startswith(who) and len(bare) > len(who) and bare[len(who):] in I_GLUED:
            return [who, token[len(who):]
                    if token.startswith(who) else bare[len(who):]]
    return None


def _a_state_typed_onto_im(token):
    """The state typed onto the "im", or None: "imsad" is "im sad", "imexhausted" is tired.

    The token has to be one no reader knows (the guard in `_glued_words`), so "image", "impact",
    "import", "improve", "imagine" and "immune" keep their meaning: each of them is a word. What
    is left over after the "im" has to be a state the reading already knows, which is why
    "improv" and "impressed" are left alone here and read elsewhere.
    """
    if len(token) < 4 or not token.startswith("im") or not token.islower():
        return None
    rest = token[2:]
    if rest in lexicon.STATES_SAID_ONTO_IM:
        return ["im", rest]
    return None


def _glued_words(token, after=None):
    """The two words a glued opener stands for, or None when the token is a word of its own.

    Only a token that is not in the lexicon at all is a candidate, which is what keeps "island",
    "issue", "washer", "dinner" and "cannon" whole: each of them is already a word, and a word
    keeps its meaning. The split is tried left to right by the length of the opener, so the
    longest opener that fits wins ("doesit" before "do" + "seit"). `after` is the next word of
    the line, which is what tells a name's split from a question's (_a_doubtful_split).
    """
    if len(token) < 4 or token in LEXICON or not token.islower():
        return None
    said_together = _a_pronoun_said_together(token)
    if said_together:
        return said_together                      # "idont", "icant", "ican't", "wedont"
    a_state = _a_state_typed_onto_im(token)
    if a_state:
        return a_state                            # "imsad", "imlonely", "imsuicidal"
    half, odd = divmod(len(token), 2)
    if not odd and token[:half] == token[half:]:
        # A name is often one half written twice ("didi", "dodo", "coco", "isis", "nana"), and no
        # question opener is: "didi from work rang" is news whatever word follows it, which the
        # be-form fence alone cannot tell, because a friend is followed by "from", "said" or
        # "and" at least as often as by "is".
        return None
    for cut in (6, 5, 4, 3, 2):
        if token[:cut] not in GLUED_LEFT:
            continue
        rest = token[cut:]
        if rest in GLUED_RIGHT:
            pieces = [token[:cut], rest]
            return None if _a_doubtful_split(pieces, after) else pieces
        if rest in GLUED_COLLAPSE:
            # "isitthere anything i can do" is "is there anything i can do": the `it` is a slip
            # and reading all three words keeps a word the line does not need.
            return [token[:cut]] + GLUED_COLLAPSE[rest]
        for second in (5, 4, 3, 2):
            # "isitthere" is three words, not two, and it is still one question.
            if rest[:second] in GLUED_RIGHT and rest[second:] in GLUED_RIGHT:
                pieces = [token[:cut], rest[:second], rest[second:]]
                return None if _a_doubtful_split(pieces, after) else pieces
    return None


# "the mrs" is the wife. It is how half the country says it, and the word on its own is a
# title, so it cannot go in the chat table with "missus": "Mrs Smith next door" is a neighbour
# and turning that into "wife Smith" would lose a name. The frame decides it - "the mrs", "my
# mrs", "our mrs" is a wife, and a mrs with a capital word after it is a title. The chat table
# already reads "missus" as "wife", so "me and the missus are arguing about money" reached the
# money-between-partners card while "me and the mrs are arguing about money" got "Sorry to hear
# that. What would help most right now?" - one word apart.
MRS_IS_THE_WIFE = re.compile(r"\b(the|my|our|his|her)\s+([Mm]rs)\b\.?(?!\s+[A-Z])")


def _the_mrs_is_the_wife(text):
    """A wife said as "the mrs", left alone where "mrs" is a title in front of a name."""
    return MRS_IS_THE_WIFE.sub(r"\1 wife", text)


# The words a person can already have written in front of an abbreviation that carries its own
# subject: "i dunno" is "i" and "i do not know", and the line would read "i i do not know".
_SUBJECT_SAID = frozenset(("i", "we", "you", "they", "he", "she", "it", "people", "folk",
                           "u", "ya", "yous", "everyone", "everybody", "somebody", "nobody"))


def _chat_words_said_out(clean):
    """A chat word spelled out in the line the readers match on.

    "i dont know what i wanna do" is the same statement as "i dont know what i want to do", and
    the readers that answer it are written on the words the person meant. The reading already
    spells these out (`norm`), but a reader matching on `clean` - the line as it was typed -
    never met the phrase, so the same line typed two ways got two different replies. Only the
    words in `lexicon.PLAIN_EXPANDS` are spelled out: a word that is not a word at all, whose
    repair is the phrase a reader is looking for. A contraction stays as it was typed ("dont" is
    how people write "do not", and the patterns are written on it), and so does a word whose
    spelling is somebody's name.
    """
    if not clean:
        return clean
    out = []
    for word in clean.split():
        spelled = SAID_OUT.get(word)
        # An abbreviation can carry its own subject: "dunno" is "i do not know", and after the
        # person has already written "i" the line would read "i i do not know what to do".
        before = SAID_OUT.get(out[-1].lower(), out[-1].lower()).split() if out else []
        if spelled and before and before[-1] in _SUBJECT_SAID and spelled.startswith(("i ", "I ")):
            spelled = spelled.split(" ", 1)[1]
        out.append(spelled or word)
    return " ".join(out)


# A hello typed as its initials or with the tail of the word bitten off: "gm", "gm all",
# "gmorning", "mornin", "evenin", "gday", "top of the morning". None of these is a word the
# reading knows, so no reader saw a hello in it at all: "gm" and "gm all" - the shape a group
# chat uses every morning - were answered with the flat "Thanks for telling me - I'm here if you
# want to dig into any of that", and so was "mornin". They are put back into the words people
# mean, so the greeting kind and the morning pool can see them.
#
# Only at the front of the line: "gm" is how a cook writes a gram, so "200 gm of butter" and
# "500gm flour" keep their weight. A hello with something after it is filler, like "hi" or "oh":
# "gm, boiler is leaking" is read as "boiler is leaking", because the words of the hello are not
# words the boiler answer matches and putting them in the line would bend what it says.
HELLO_SAID_SHORT = (
    ("top of the morning", "good morning"),
    ("g morning", "good morning"),
    ("gmorning", "good morning"),
    ("g'morning", "good morning"),
    ("gm", "good morning"),
    ("gday", "good day"),
    ("g'day", "good day"),
    ("mornin'", "morning"),
    ("mornin", "morning"),
    ("evenin'", "evening"),
    ("evenin", "evening"),
)


# The words a hello is said to: "gm all", "mornin everyone", "top of the morning to you". They go
# when the hello is taken off the front, or the line left is "all, any tips for a cold".
HELLO_TAIL = frozenset("all everyone everybody guys folks friends there you mate to".split())


def _a_hello_said_short(clean):
    """The line with a hello typed as initials, or with its tail bitten off, read as a hello."""
    if not clean:
        return clean
    for typed, meant in HELLO_SAID_SHORT:
        if clean == typed:
            return meant
        if not (clean.startswith(typed + " ") or clean.startswith(typed + ",")
                or clean.startswith(typed + "!")):
            continue
        words = clean[len(typed):].strip(" ,!.").split()
        while words and words[0].strip(",.!") in HELLO_TAIL:
            words.pop(0)
        rest = " ".join(words).strip(" ,!.")
        return rest or meant
    return clean


def _glued_said_apart(clean):
    """The line with every glued question opener put back into the words it stands for.

    A shortened opener is spelled out on the way: "whatsthe best way" is "what is the best way",
    not "whats the best way", because the modules read the words of the line and "whats" means
    nothing to them, while "what is" is the same two words the spaced line carries.
    """
    out = []
    words = clean.split()
    for index, token in enumerate(words):
        pieces = _glued_words(token, words[index + 1] if index + 1 < len(words) else None)
        if pieces:
            spread = lexicon.CHAT.get(pieces[0])
            if spread and " " in spread:
                pieces = spread.split() + pieces[1:]
        out.extend(pieces if pieces else [token])
    return " ".join(out)


# A whole line, or a whole sentence of it, typed with the spaces left out: "whatshouldido",
# "howdoicookrice", "mysonisill", "imsotired", "cantgetoutofbed". A phone keyboard's swipe gives
# a run like this and so does a hurried thumb, and every one of them was answered with the stock
# "Got it. Is there anything you'd like a hand with?", because no word in the run is a word the
# reading knows. "isit ok to eat this" is the same fault with one opener in front, and
# `_glued_words` above puts that right; this is the same idea for a run of three words or ten.
#
# Two things keep a real word whole. A run is only split when it opens the way a line opens - on
# a question word, on the speaker ("i", "im", "idk") or on a possessive ("my", "our") - and the
# words it is split into are words of the lexicon, so a run only ever becomes words somebody
# typed: "document" is not "do cu meant" and "whatsapp" is not "what is app", because "cu" and
# "sapp" are not words. "cupcakes", "toothache", "pushchair", "houseplant", "lunchtime",
# "behaviour", "fortnight", "bearings", "hibernate" and "presentation" open on nothing a line
# opens on, so none of them is touched at all.
RUN_ON_OPENERS = frozenset("what how why when where who which whats hows wheres whos "
                           "nothing nobody everything everyone something someone "
                           "can cant could couldnt should shouldnt would wouldnt will wont "
                           "do dont does doesnt did didnt is are was were shall".split())


RUN_ON_SELF = frozenset("i im ive id ill idk idunno cant dont didnt doesnt wont isnt arent".split())


RUN_ON_MINE = frozenset("my your his her our their".split())


# The words a run is split into: the lexicon alone, so a split is words of English and never a
# piece of a longer word ("cu", "sapp", "cument"), plus the two single letters a line has and the
# spellings people type for them ("im", "cant", "dont") which are only the words with a letter
# dropped. A run says who it is about - "what should i do", "my back hurts", "can you help me",
# "nothing is working" - so one of the pieces has to be a word for a person or a thing.
RUN_ON_WORDS = LEXICON | frozenset("""a i im ive id ill idk idunno dunno cant dont didnt
    doesnt wont isnt arent wasnt werent wouldnt couldnt shouldnt""".split())


RUN_ON_PEOPLE = frozenset("""i im ive id ill me my we us our you your he him his she her it its
    they them their there this that these those nothing nobody everything everyone something
    someone anyone no one""".split())


# How long a run has to be to be read as a clause rather than as a word. "myanmar" is "my an
# mar" to a split, and "my" is a word people open a line on, so a run of seven letters is left
# alone; "mymumisill" and "mybackhurts" are ten and eleven and are read.
RUN_ON_SELF_LONGEST = 9


# A run is split into two words or more, and the shortest a run can be is eight letters: "island",
# "insure", "inherit" and "instead" all open on "is" or "in" and are six or seven letters, so a
# shorter run is read as one word and left alone.
RUN_ON_SHORTEST = 8


# A run that ends on one of these is a word that begins with an opener: "whatever", "whenever",
# "whoever", "however" and "wherever" are one word each, and "how" and "ever" are not two.
RUN_ON_LAST_PIECES = frozenset("ever ether soever".split())


def _said_run_on(token):
    """The words a line typed without spaces is made of, or None when the token is not one."""
    if not token.isalpha():
        return None
    token = token.lower()
    if len(token) < RUN_ON_SHORTEST:
        return None
    if token in LEXICON:
        return None
    best = {0: ()}
    for start in range(len(token)):
        pieces = best.get(start)
        if pieces is None:
            continue
        for end in range(len(token), start, -1):
            piece = token[start:end]
            if piece not in RUN_ON_WORDS:
                continue
            here = pieces + (piece,)
            there = best.get(end)
            if there is None or len(here) < len(there):
                best[end] = here
    split = best.get(len(token))
    if not split or len(split) < 2:
        return None
    if split[-1] in RUN_ON_LAST_PIECES:
        return None
    if sum(1 for piece in split if len(piece) == 1) > 1:
        return None
    if split[0] in RUN_ON_SELF or split[0] in RUN_ON_MINE:
        if len(token) < RUN_ON_SELF_LONGEST or len(split) < 3:
            return None
        return list(split)
    if split[0] in RUN_ON_OPENERS:
        if not any(piece in RUN_ON_PEOPLE for piece in split):
            return None
        return list(split)
    return None


def _a_run_and_what_surrounds_it(token):
    """A token as (what comes before the letters, the letters, what comes after them).

    The letters of a run are the letters wherever a phone put a capital or a person put a
    question mark: "WhatShouldIDo" and "whatshouldido?" are the same five words as
    "whatshouldido", and all three were answered with a line that says nothing.
    """
    start = 0
    while start < len(token) and not token[start].isalpha():
        start += 1
    end = len(token)
    while end > start and not token[end - 1].isalpha():
        end -= 1
    return token[:start], token[start:end], token[end:]


def _typed_without_spaces(clean):
    """The line with any run of words typed as one long word put back into its words."""
    out = []
    for token in clean.split():
        before, letters, after = _a_run_and_what_surrounds_it(token)
        pieces = _said_run_on(letters)
        if pieces:
            spread = lexicon.CHAT.get(pieces[0])
            if spread and " " in spread:
                pieces = spread.split() + pieces[1:]
            out.extend(pieces)
            if after:
                out[-1] = out[-1] + after
            if before:
                out[0] = before + out[0]
        else:
            out.append(token)
    return " ".join(out)


# A contraction typed with a space where its apostrophe belongs: "i m 34", "i ve got a cat",
# "i ll do it tomorrow", "we re going", "i don t know", "can t breathe", "they d love it".
# The apostrophe is the only mark that was left out, so the two pieces are one word and every
# reader below is looking for that one word: on main "i m 34" kept no age, "i ve got a cat" was
# read as a line with a bare "m" and "ve" in it, "i ll do it tomorrow" was echoed back as "you ll
# do it tomorrow", and "i don t know" was the shrug every reader gives a line it cannot parse.
# The pairs are not written out by hand, because the engine already knows both spellings: the
# apostrophe-free ones are the contraction table, and the apostrophe ones are a pronoun and its
# tail. The one-letter rule is what makes a space-split contraction: something like "we re" is
# the contraction because no line puts a bare "re" after "we" for any other reason, and "so me"
# is left alone because neither piece is a letter on its own.
APOSTROPHE_TAILS = frozenset("m re ve ll d s".split())


# What a tail can follow. "this" and "one" are left out: "one s" and "this s" say nothing as
# contractions, and the possessive "one's" is not the "one is" the engine would read.
APOSTROPHE_BASES = frozenset("""i you we they he she it that there here what who where when
    why how let everyone everybody someone somebody nobody""".split())


# "i s" is left out: nobody writes "i's" for "i is", so a bare "s" after "i" is a letter, not
# a contraction.
APOSTROPHE_NOT = frozenset([("i", "s")])


def _the_said_apart_forms():
    """({pieces: the word}, one pattern) for the contractions that can be typed as two words.

    Every way of splitting the known contraction spellings into two or three pieces, kept only
    where one piece is a single letter, so the pattern can never claim two ordinary words.
    """
    forms = {}
    for joined in tuple(lexicon.EXPAND) + tuple(lexicon.TYPED_CONTRACTIONS):
        if not joined.isalpha() or not 2 <= len(joined) <= 10:
            continue
        for pieces in _the_ways_a_word_is_typed_apart(joined):
            forms.setdefault(pieces, joined)
    for base in APOSTROPHE_BASES:
        for tail in APOSTROPHE_TAILS:
            if (base, tail) in APOSTROPHE_NOT:
                continue
            one = base + "'" + tail
            if _apostrophe(one):
                forms.setdefault((base, tail), one)
    return forms


def _the_ways_a_word_is_typed_apart(joined):
    """The ways this one word arrives as two or three tokens: "dont" is "don t" or "d ont"."""
    ways = []
    for cut in range(1, len(joined)):
        first, rest = joined[:cut], joined[cut:]
        if len(first) == 1 or len(rest) == 1:
            ways.append((first, rest))
    for first_cut in range(1, len(joined) - 1):
        for second_cut in range(first_cut + 1, len(joined)):
            pieces = (joined[:first_cut], joined[first_cut:second_cut], joined[second_cut:])
            if 1 in (len(piece) for piece in pieces):
                ways.append(pieces)
    return ways


SAID_APART_FORMS = _the_said_apart_forms()


SAID_APART = re.compile(
    r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(
        r"\s+".join(pieces) for pieces in sorted(SAID_APART_FORMS,
                                                  key=lambda pieces: -sum(len(p) for p in pieces))))


# A determiner in front of a bare letter is a name or a badge, not a contraction: "my i d is in
# my bag" is an identity card, and joining it into "my i'd" answers a line about paperwork with a
# line about what somebody would do.
A_LETTER_AFTER = frozenset("""my your his her their our the a an this that these those no any
    every each another some""".split())


def _said_apart(tokens):
    """The contractions typed with a space in place of the apostrophe, put back together."""
    if len(tokens) < 2:
        return tokens
    said = " ".join(tokens)
    if not SAID_APART.search(said):
        return tokens

    def put_together(match):
        before = said[:match.start()].split()
        if before and before[-1] in A_LETTER_AFTER:
            return match.group(0)
        return SAID_APART_FORMS[tuple(match.group(0).split())]

    return SAID_APART.sub(put_together, said).split()


def said_apart(line):
    """The line with a contraction typed as two words put back together: "she s" -> "she's".

    A module that matches English words rather than the engine's reading calls this so that the
    one word people typed as two arrives as one, the same shape the reading has.
    """
    line = str(line or "")
    words = line.split()
    if len(words) < 2:
        return line
    return " ".join(_said_apart(words))


# The names of the notes, so a line about the sound of music keeps its "mi": "do re mi fa sol la".
SOLFEGE = frozenset("do re mi fa sol la ti so".split())


# What "mi" is followed by when it is "me" and not "my": a line that puts somebody alongside
# the speaker ("mi and my friend went out", "mi n the dog", "mi too"). A possessive needs a
# thing to own straight after it, so these words rule "my" out.
MI_IS_ME_AFTER = frozenset("and n or nor & too either neither also".split())


# And what it is followed by in "call mi later", "send mi the link", "give mi a min": a word
# that cannot open a thing to own, so "my" has nothing to stand on. "back" and "first" are
# left out on purpose - "my back hurts", "my first day" are possessives. "know" ("let mi know
# when u land") and "alone" ("leave mi alone for a bit") are here for the same reason: neither
# one is a thing, so "my know" and "my alone" are not sentences.
MI_IS_ME_BEFORE = frozenset("""the a an this that these those later soon now again what how why
    when where if to in on at up out over please pls plz today tomorrow tonight then also
    though anyway know alone""".split())


# A word in front of "mi" that no possessive can follow: "the mi band is cheap", "a mi band",
# "this mi phone". A name is what is left, so the "mi" stays as it was typed.
MI_IS_A_NAME_AFTER = frozenset("the a an this that these those another".split())


# "text mi back", "ring mi back later tonight": the "back" is the second half of the verb
# ("text back", "ring back"), and the word in front is what says so. On its own "mi back" is a
# body: "mi back is playing up", "mi back hurts" keep "my back".
MI_BACK_VERBS = frozenset("""text ring call phone send pass get give pay email message pm
    whatsapp reply write leave take bring hand poke shout""".split())


# "ill" is "i will" in "ill go with the train", "ill take the train", "ill catch the eight
# o'clock": the word after it is a verb that needs a subject, and the line is somebody picking
# between two things. Left as it was typed, the health entry that holds "ill" and "train" claims
# it - "Use the neck rule: a runny nose, sneezing or a mild sore throat above the neck is fine
# for easy exercise" as the answer to a choice of trains. Only these three verbs, and only with
# the clause at its head, so the health lines keep their illness ("im ill", "i feel ill", "my nan
# is very ill", "still ill and i want to run") and the leaving idioms keep their words ("ill let
# you go", "ill leave you to it", "ill get going", "ill book her in tomorrow"). "get" is out
# because "ill get going" is the leaving line, and the -ing forms are out because none of them
# was ever the misfire.
ILL_GOES_ON = frozenset("go take catch".split())


# The parts a person has one of. "my backs playing up", "my heads banging", "my tummys been
# off since friday": the s on the part is the possessive 's typed without its apostrophe, or
# the plural habit, and there is still only one of them. A plural part ("my knees", "my hands")
# is not in this list, so nothing that really is plural is touched.
ONE_OF_A_KIND = frozenset("""back head neck chest stomach tummy belly throat nose waist spine
    forehead tongue heart pelvis gullet""".split())


# What follows the part when the s was a possessive: the word says what the one part is doing,
# and a plural would need "are" or "were", which are left out so "our backs are aching" keeps
# its backs.
ONE_PART_AFTER = frozenset("""is was has been s keeps kept does did will would going playing
    killing hurting aching throbbing banging pounding killing""".split())


def _one_of_the_parts(token, before, after):
    """The part a typed s on one of a kind stands for: "my backs" -> "my back", or None.

    Only after a possessive, and only when the word behind it says what the one part is doing,
    so a real plural keeps its s: "my knees have been playing up" and "our backs are aching" are
    untouched, and "my backs playing up" is read as the back it is.
    """
    if not token.endswith("s") or len(token) < 4 or token[:-1] not in ONE_OF_A_KIND:
        return None
    if not _is_possessive(before):
        return None
    # An -ing word says what the part is doing; "playin" is one before the g is put back.
    if after in ONE_PART_AFTER or (after or "").endswith(("ing", "in")):
        return token[:-1]
    return None


# "veggies" is a plate of vegetables after a cooking word ("roast veggies", "steamed veggies",
# "leftover veggies") and a person after a verb of being ("3 are veggies", "the kids are
# veggies"): the word in front tells the two apart, and the diet reading is the one the answer
# tables need. Kept short on purpose - a token that is not here leaves the line as typed.
VEGGIES_AFTER = frozenset("""roast roasted roasting grilled grilling steamed steaming fried frying
    stir braised baked charred sauteed saute boiled raw leftover leftovers fresh frozen chopped
    diced sliced seasonal mixed cook cooked cooking eat eating ate""".split())


# The words "wers" is the verb "wears" after: a person doing the wearing. Anywhere else it is
# the question "where is", which is what a line that opens with it or leads into it asks.
WEARS_AFTER = frozenset("""i you u we they he she it people everyone somebody anybody
mum mums dad dads mam mother father sister brother son daughter wife husband nan gran
grandma grandad granparents mates kids children boy girl lad lass""".split())


# The words that make a typed "sum" the arithmetic noun rather than "some" with its o left out.
# A determiner in front of it is one ("do a sum", "the sum of 5 and 3"), and so is the name of a
# lump of money or the word describing it ("the lump sum", "a tidy sum", "a large sum") - the two
# words people use for a payout, and the only place the reader of a line says "sum" for money.
SUM_THE_NOUN = frozenset("""a an the my your his her our their its this that these those another
    each every no any do did does doing done work worked works add added adds total totals
    lump round large small tidy princely big hefty cash whole same missing""".split())


# The words that keep a typed "sum" the word "sum" when they follow it: "sum up", "sum it up",
# "to sum things up" is the verb, and "sum total" is the noun. The word in front cannot say this -
# a verb has no determiner in front of it, and "to", "let me" and "can you" look like the noun's
# lead-ins - so the word after it is what decides.
SUM_STAYS_AFTER = frozenset("up it things that this them total".split())


def _sum_word(before, after=None):
    """The word a typed "sum" stands for, from the words around it.

    "sum" is "some" with the o left out, and it is also the arithmetic noun and the verb of
    adding up, and the maths reading was winning everywhere: "i gotta loose sum weight b4 the
    weddin" was read as a line about numbers, so the topic was maths-and-numbers and the "loose"
    in front of it was not repaired to "lose". A determiner or the name of a lump of money in
    front is the noun; "up", "it", "things" or a demonstrative behind is the verb ("to sum up",
    "let me sum it up", "sum up what happened"); anything else is "some" ("i need sum help with
    my cv", "can i get sum milk", "sum of us are going").
    """
    spelled = _plain_chat(before) if before not in (None, "|") else ""
    if spelled in SUM_THE_NOUN:
        return ["sum"]
    behind = _plain_chat(after) if after not in (None, "|") else ""
    if behind in SUM_STAYS_AFTER:
        return ["sum"]
    if spelled in ("in", "to") and behind not in SUM_STAYS_AFTER:
        # "in sum, the day was good" and "to sum up" are the only two of these people type; the
        # first is the noun, and the second was already sent to the verb by the word behind it.
        return ["sum"]
    return ["some"]


# "ur" is two words typed as one, and which one it is is decided by the word after it, because
# only one of the two can stand there. A possessive takes a thing ("ur mum rang", "ur bike is
# outside", "ur washing machine is leaking"), and "you are" takes an article, a word of degree
# or the word for what somebody is doing ("ur a star", "ur so funny", "ur the best", "ur going
# to love this"). Read as "your" every time, "ur so funny" was answered "Thanks for telling me",
# "ur the best" went to the search hedge and "ur going to love this" was echoed back as
# "Noted: your going to love this".
YOU_ARE_AFTER = frozenset("""a an the such so too very really quite bloody proper
    going gonna joking kidding being not""".split())


def _join_chat_digits(tokens):
    """A chat word typed in pieces stays one word: "any1", "l8r", "2nite", and "i d k".

    The tokeniser keeps a measure together ("5kg", "1.5kg") but splits a letter run from a
    digit run, so the digit spelling of a chat word arrives in two or three pieces ("l" + "8r",
    "2" + "nite") and never reaches the chat table. Pieces are joined only into a word the
    lexicon knows, so an ordinary digit pair ("i have 4 cats", "a table for 2") is left alone,
    and a measure ("1.5kg", "20mg") is one token already and never a candidate.

    Somebody typing with one hand writes the same chat word with a space between every letter:
    "i d k", "o m g", "n e 1". Nothing read those runs, so `i d k` came out as "i'd k" and the
    line reached no card at all. Three or four one-character pieces that spell a chat word are
    joined the same way, and a run that spells nothing the lexicon knows ("c a t", "i have 4
    cats") is left exactly as typed.
    """
    joined = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        following = tokens[index + 1] if index + 1 < len(tokens) else None
        if (following is not None
                and (following[:1].isdigit() or token.isdigit())
                and (token + following in lexicon.CHAT
                     or token + following in lexicon.MISSPELLINGS)):
            joined.append(token + following)
            index += 2
            continue
        spelt = _said_apart_as_one(tokens, index)
        if spelt is not None:
            joined.append(spelt[0])
            index = spelt[1]
            continue
        joined.append(token)
        index += 1
    return joined


# A run of three or four one-character pieces that spells one chat word, in the line as typed.
_SPACED_RUN = re.compile(r"(?<![\w'])([a-z0-9](?:[ \t]+[a-z0-9]){2,3})(?![\w'])", re.IGNORECASE)


def _said_apart_as_one_word(clean):
    """Join "i d k" into "idk", and only when the run spells a word the lexicon knows.

    Longest first, so "n e 1" is read as "ne1" and not as a shorter piece of it. Two pieces are
    deliberately left alone: "i m", "didn t" and "c section" are read by the tables that expect
    them, and joining them here would take those lines away from those readers.
    """
    if not _SPACED_RUN.search(clean):
        return clean

    def join(match):
        # The run may be longer than the chat word in it: "b t w i was late" is "btw" and the
        # start of the next clause, so the longest piece that spells a word wins and the rest of
        # the run is put back exactly as typed.
        pieces = match.group(1).split()
        for length in range(len(pieces), 2, -1):
            word = "".join(pieces[:length]).lower()
            if word in lexicon.CHAT or word in lexicon.MISSPELLINGS:
                return " ".join([word] + pieces[length:])
        return match.group(0)

    return _SPACED_RUN.sub(join, clean)


# "i d k" and "o m g": three or four single characters in a row that spell one chat word.
# "i d k" and "o m g": three or four single characters in a row that spell one chat word.
_SPACED_PIECE = re.compile(r"^[a-z0-9]$")


def _said_apart_as_one(tokens, start):
    """The chat word at this position and the index after it, or None.

    Longest first, so "n e 1" is "ne1" and never a shorter piece of it, and never more than four
    pieces, because five one-character words in a row is a spelling and not a chat word.
    """
    if not _SPACED_PIECE.match(tokens[start]):
        return None
    for length in (4, 3):
        pieces = tokens[start:start + length]
        if len(pieces) < length or not all(_SPACED_PIECE.match(piece) for piece in pieces):
            continue
        word = "".join(pieces)
        if word in lexicon.CHAT or word in lexicon.MISSPELLINGS:
            return word, start + length
    return None
