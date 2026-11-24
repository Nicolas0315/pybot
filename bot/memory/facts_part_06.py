"""Part 6 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re

from ..understanding import breeds
from ..understanding.kinds import VERB_FORMS

from .facts_part_01 import (
    DAYS, MONTHS, NOT_A_NAME, NOT_A_NAME_MIDDLE, NOT_A_NAME_STATE, NOT_A_NAME_THING, ANIMALS,
    NAMES_OFFERED,
)
from .facts_part_02 import (
    _NAME, _RELATION_WORDS, TITLE, RELATIONS, _A_PERSON, SPOKEN_RELATION,
)
from .facts_part_05 import (
    ALLERGY_STOP,
)


# A number said of a person other than the user is that person's age: "my son is 7", "my mum is
# 68", "my daughter's 4". The number has to follow the person and the verb, and what follows the
# number has to be the end of what they said about them (a full stop, a comma, "and", "now") or
# the words an age is said with ("years old", "next month", "in june"). Anything else is a unit
# and the number is not an age: "my mum is 68 kilos", "my son is 8 grams", "my husband is 6 foot",
# "my daughter is 5 stone" are a weight and a height, and a closed list of units missed the ones
# nobody thought of, so the list is the words that are allowed to follow instead.
# "18 months old" is an age in months, not eighteen years, and it is still a fact the chat
# holds. Kept apart from AGE_TAIL because the answer has to say the unit. The "old" is optional:
# people write "22 months" more often than "22 months old", and the tail still has to end the
# fact, so "22 months away" is not an age.
AGE_MONTHS_TAIL = re.compile(r"^\s*months?(?:\s+old)?\b", re.I)


AGE_TAIL = re.compile(
    r"^\s*(?:$|[.,;:!?)]|\b(?:and|but|so|now|today|tomorrow|yesterday|too)\b"
    # "my daughter is 7 going on 8", "im 41 going on 42": the figure after the phrase is the age
    # coming, and it says the figure before it is an age too. Without this the line filed no age
    # at all, so the manners reader took the whole thing for the phrase "going on" and answered
    # "I'm well, thanks", and the ask a turn later said nobody had ever given an age.
    r"|\bgoing on \d{1,3}\b"
    r"|\bas well\b|\bthis year\b|\byears? old\b|\bold\b"
    r"|\bnext (?:week|month|year|spring|summer|autumn|winter|monday|tuesday|wednesday|"
    r"thursday|friday|saturday|sunday)\b|\b(?:in|on|by) [a-z]{3,9}\b)",
    re.I)


def _month_age_after(text, end):
    """True when the words after `end` are an age in months and then the end of the fact."""
    match = AGE_MONTHS_TAIL.match(text[end:])
    if not match:
        return False
    return bool(AGE_TAIL.match(text[end + match.end():]))


# An age that is still to come is said with a birthday: "she's 5 next month", "my daughter turns
# 7 in june". The person has not had that birthday yet, so the number is kept with the words that
# say when, and the reply says it back as a birthday rather than as an age they have now.
# The "who" clause says whose age it is exactly as the plain shape does, so it is read the same
# way: "my sister whos 40 next week" is a birthday still to come, the same fact as "my sister is
# 40 next week", and saying she is 40 this week would be wrong for one of the two wordings.
AGE_TO_COME = re.compile(r"\b(?:turns?|will be|is|are|'s|shes|hes|she's|he's|theyre|they're|"
                         r"who(?:['\u2019]?s)?)\s+"
                         r"(\d{1,3})\s+"
                         r"(next\s+(?:week|month|year|spring|summer|autumn|winter)|"
                         r"(?:in|on)\s+[a-z]{3,9})\b", re.I)


# A name given for someone in the family, so "what's my sister called" is a fact about the chat
# and not a search: "my sister is called meg", "my sisters called meg", "my sister's name is meg",
# "my brother dan".
OTHER_CALLED = re.compile(r"\bmy\s+(?P<who>" + _RELATION_WORDS + r")s?\s+"
                          r"(?:(?:is|was|are)\s+)?(?:called|named)\s+" + _NAME, re.I)


OTHER_NAME_IS = re.compile(r"\bmy\s+(?P<who>" + _RELATION_WORDS + r")(?:'s|s'|s)?\s+name\s+"
                           r"(?:is|was)\s+" + _NAME, re.I)


# "my brother dan" names him in passing, with no verb at all. Only the whole line is read this
# way: a word after the relation mid-line is as often a verb ("my mum coming sunday") as a name.
OTHER_NAMED_BARE = re.compile(r"^\s*my\s+(?P<who>" + _RELATION_WORDS + r")s?\s+"
                              r"(?P<name>[A-Za-z][a-z'-]{1,19})\s*[.!]?$", re.I)


# The date somebody else was born on: "my mums birthday is on the 3rd of may", "his birthday is
# the 3rd of may", "my sons birthday is the 3rd of may". The date was kept as a line of the chat
# and nothing else, so the one fact the store did not hold about that person was their birthday:
# "my son is called tom" / "his birthday is the 3rd of may" then "when is toms birthday" was
# answered "I don't have a date from you for that", which denies a date they had just given. The
# person is the relation the line names, or the pronoun, which the store folds onto the person the
# chat is about the way it does an age ("shes 78" after a line about the mum is the mum's).
OTHER_BIRTHDAY = re.compile(
    r"\b(?:(?:my|our)\s+(?P<who>" + _RELATION_WORDS + r")s?|(?P<pronoun>his|her|their))\s+"
    r"(?:birthday|bday|dob|date of birth)\s*(?:'s|s)?\s*"
    r"(?:is|was|falls|:|=|on|in)\s+(?:on\s+)?(?:the\s+)?"
    r"(?P<date>[^,.;!?]{2,28})", re.I)


# The name given in passing between the person and what is said about them: "my son tom is 7",
# "my sister meg is allergic to nuts", "my daughter lily hates mushrooms". The name stands where a
# subject stands, so the word after it has to be one that follows a subject; that is what keeps
# "my son goes to school" and "my mum always says" from naming anybody. The relation is written
# without the possessive s, because "my nans death was peaceful" and "my sons teacher wants a
# word" say which person the thing belongs to, not what they are called.
# A name typed with its capital is a name however the rest of the line goes: "my friend Sarah
# called round" gives the friend her name, and the verb list below has no word for what she did,
# so the line filed a friend with no name and "whats my friends name" denied it. Only the capital
# is the evidence - a line typed all in lower case is read by the list above, because the word
# after a relation there is as often a verb ("my mum coming sunday") as a name.
# A lower-case name is said the same way: "my friend sarah called round", "my mate dave went
# home". The verb list above is a closed set and "called" is not in it, because "called" is also
# the naming verb ("my mate is called dave"). What settles it is the word *after* the name: a
# verb there means the word before it is the person, and a line whose third word is not a verb
# ("my mum coming sunday") still says nothing.
OTHER_NAMED_BEFORE_VERB = re.compile(
    r"\bmy\s+(?P<who>" + _RELATION_WORDS + r")\s+(?P<name>[a-z][a-z'-]{1,19})\s+"
    r"(?P<verb>[A-Za-z][a-z'-]{1,19})\b")


def _the_word_then_a_verb(name, following):
    """Whether the word after a name is a verb, so the word before it is the person's name."""
    name, following = (name or "").lower(), (following or "").lower()
    if not name or not following or name in VERB_FORMS:
        return False
    if following in VERB_FORMS:
        return True
    # The past forms of the verbs a line about somebody most often carries ("called round",
    # "texted me", "moved out"), which no list holds in full.
    return len(following) > 3 and following.endswith("ed")


OTHER_NAMED_CAPITAL = re.compile(
    r"\bmy\s+(?P<who>" + _RELATION_WORDS + r")\s+(?P<name>[A-Z][a-z'-]{1,19})\b")


# A possessive is not part of a name, and the readers above take the whole run of letters,
# apostrophe included: "my son Tom's car is broken" was kept as a son called "Tom's", and the
# store said it out loud ("Your son is called Tom's.") where main said it had not been told.
# "my friend Sarahs birthday is in may" is the same possessive with the apostrophe left out:
# the s is the possessive when the word after it is a thing and the word after *that* is a
# copula, which is the shape a possession has, and a name that merely ends in s ("my mate James
# was late", "my son Tom saw it") never matches. The stem is the person.
OTHER_NAME_POSSESSIVE = re.compile(
    r"\bmy\s+(?P<who>" + _RELATION_WORDS + r")\s+(?P<name>[A-Z][a-z]{1,19})(?:['\u2019]s?|"
    r"s(?=\s+[a-z]{3,19}\s+(?:is|are|was|were|will|has|have|had)\b))\b")


OTHER_NAMED_MIDLINE = re.compile(
    r"\bmy\s+(?P<who>" + _RELATION_WORDS + r")\s+"
    r"(?P<name>[A-Za-z][a-z'-]{1,19})\s+"
    r"(?P<verb>is|was|are|were|has|have|had|does|did|will|can|loves|hates|likes|needs|wants|"
    r"keeps|goes|works|plays|sleeps|eats|starts|started|turns|turned|says|said|misses|cries|"
    r"refuses|comes|came|gets|got|seems|looks|feels|takes|took|makes|made|buys|bought|"
    r"tells|told|struggles|wont|won't|cant|can't|doesnt|doesn't|isnt|isn't|didnt|didn't|"
    # The verbs a line about a person most often carries after their name, including the ones a
    # bereavement line uses: "my dad john died last year" gives the name, and denying it a turn
    # later is the one thing a memory store must not do.
    r"died|dies|passed|passes|lives|lived|moved|went|grew|became|married|left|arrived|retired|"
    r"finished)\b",
    re.I)


# Words in the name's place that are never a name: modals, auxiliaries and the adverbs that sit
# between a subject and its verb ("my mum always says", "my son still wont sleep"). Named for the
# place, not for the certainty: `NOT_A_NAME_EITHER` is already the pet-and-name reader's smaller
# set further down the file, and two sets under one name means the later assignment silently
# replaces the earlier one.
NOT_A_NAME_MIDLINE = frozenset("""
will would can could shall should may might must did does do dont doesnt didnt wont cant
shall always never often sometimes usually still really just also only suddenly already quite
rather very too more most less least better worse then than soon later yet ever once twice
she he they them we you it its this that there here i me him her his hers their
""".split())


# Words that stand in a name's place without being one: the thing a person owns or has said about
# them with the possessive's dropped ("my son name is tom", "my mum birthday is saturday"), and
# the things people say in the same breath ("my dads speech is slurred"). The reader would rather
# miss a name than answer "What is your nan called?" with "Death".
NOT_A_NAME_THERE = frozenset("""
name names age birthday bday anniversary death funeral wake school teacher teachers class
homework reading exam exams job work shift shifts boss mood temper speech health weight diet
appetite sleep room bedroom car phone mobile laptop house flat garden leg legs arm arms back
head hand hands knee ankle shoulder eye eyes ear ears teeth tooth hair skin cough cold
temperature illness surgery appointment hospital care medication meds pills tablets inhaler
hearing eyesight memory bills rent money wages pension benefits passport visa wedding holiday
flight train bus ticket tickets booking order parcel present presents card
""".split())


# Endings that make a word a doing or a way of being rather than a name: "coming", "tired",
# "angrily". Nobody is called Coming.
NOT_NAME_ENDING = ("ing", "ed", "ly")


# Names that end the way a doing or a way of being does, so the ending alone does not rule them
# out: "my daughter lily is 4" is a girl called Lily, and "ted" is a man's name.
NAMES_THAT_END_LIKE_A_VERB = frozenset("""
lily holly molly polly sally kelly emily billy willy ted ned fred jed ed
""".split())


def a_titled_name(word):
    """Whether a word is a title with a name after it: "mr patel", "dr. kaur", "mrs smith"."""
    return bool(re.fullmatch(r"(?:" + TITLE + r")\s+[A-Za-z][A-Za-z'\-]{1,19}",
                             str(word or "").strip(), re.I))


def _the_name_without_a_possessive(text):
    """{"tom's": "Tom", "sarahs": "Sarah"} for the possessive runs in a line.

    The key is what the readers below capture (the name with the possessive still on it), so a
    pass that takes "Tom's" reads the same person as the naming lines do.
    """
    stems = {}
    for match in OTHER_NAME_POSSESSIVE.finditer(text):
        raw = text[match.start("name"):match.end()]
        raw = str(raw).replace("\u2019", "'").lower()
        stem = match.group("name")
        if raw and stem:
            stems[raw] = stem
    return stems


# How many children they have. "i have two kids" was filed as nothing at all, so the store could
# not answer "how many kids do i have" and the line itself got no fact read back. The number comes
# with the word for the children, because "i have two" alone is about whatever was just mentioned,
# and "a couple of" is two however it is put.
KID_COUNT = re.compile(
    r"\b(?:i|we)(?:'ve|ve|\s+have|\s+have\s+got|\s+got)\s+(?:got\s+)?"
    r"(?P<n>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"a\s+couple\s+of)\s+(?:kids?|children|child)\b"
    r"|\bmy\s+(?P<m>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    r"\s+(?:kids?|children)\b", re.I)


# The count is often the second thing in the line, after something else they have: "i've got a dog
# and two kids" kept the dog and no number of children, while the same count said first ("i've got
# two kids and a dog") was held - so the recap of the first line could not say the children at all.
# A count joined on with "and" or a comma belongs to the same person, and it is read as one.
KID_COUNT_AND = re.compile(
    r"\b(?:i|we)(?:'ve|ve|\s+have|\s+have\s+got|\s+got)\s+[^.;!?]{0,40}?(?:\band\b|,)\s*"
    r"(?P<n>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"a\s+couple\s+of)\s+(?:kids?|children|child)\b", re.I)


KID_NUMBERS = {word: number for number, word in enumerate(
    ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
     "eleven", "twelve"))}


# The same count the other way, so a reply can say "Two kids" rather than "2 kids".
KID_NUMBER_WORDS = {number: word for word, number in KID_NUMBERS.items()}


# A figure spelled as a word is the same figure. Every ages reader here matched on digits, so
# "my kids are four and seven" was no fact at all, and a line the reading spells only part way
# ("i have two kids, 4 and 7" reaches the store as "i have two kids, four and 7") gave a lone 7
# for a group of two children - an age stuck on the end of a list of ages that was already right.
# The words become digits once, before any reader looks, and "twenty one" is 21, not 20 and 1.
FIGURE_WORDS = {word: str(number) for number, word in enumerate(
    ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
     "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
     "eighteen", "nineteen", "twenty"), start=1)}


FIGURE_PAIR = re.compile(r"\btwenty[\s-]+(one|two|three|four|five|six|seven|eight|nine)\b",
                         re.I)


FIGURE_WORD = re.compile(r"\b(?:" + "|".join(sorted(FIGURE_WORDS, key=len, reverse=True))
                         + r")\b", re.I)


def figures_as_digits(text):
    """The line with every figure it spells as a word written as a digit instead."""
    if not isinstance(text, str) or not text:
        return ""
    text = FIGURE_PAIR.sub(
        lambda match: str(20 + int(FIGURE_WORDS[match.group(1).lower()])), text)
    return FIGURE_WORD.sub(lambda match: FIGURE_WORDS[match.group(0).lower()], text)


# Their own children, so a count followed by where those children are ("in my class", "in year
# four") is a class the person teaches.
# The ages said with the children: "my two kids are 4 and 7", "i have two kids aged 4 and 7".
# The count alone is a fact and the ages are another one, so a reply that has them should use
# them rather than ask for the ages the person has just given.
KID_AGES = re.compile(
    r"\b(?:kids?|children|child)\b[^.!?]{0,24}?\b(?:are|aged?|of)\s+"
    r"(?P<ages>\d{1,2}(?:\s*(?:,|and)\s*\d{1,2})+)", re.I)


# The same list with no verb in it: "i have two kids, 4 and 7" gives the ages after a comma, and
# the reply that asked "How old are they?" asked for what the person had just written down.
KID_AGES_AFTER_A_COMMA = re.compile(
    r"\b(?:kids?|children)\b\s*[,:;-]\s*(?P<ages>\d{1,2}(?:\s*(?:,|and)\s*\d{1,2})+)", re.I)


# The ages of the children the store already counts, handed out one at a time on the next line:
# "i have two kids" then "ones 7 and ones 4". No group word is in the second line, so none of the
# readers above match it, the store kept nothing, and the bot said the line back ("Got it - ones 7
# and ones 4."); "what do you know about my kids" then answered that it did not know. The same line
# is the plain answer to the question the count was met with ("how old are they?").
ONES_BY_ONE = re.compile(
    r"\bones?\b|\bthe\s+(?:other|older|younger|little|big|small|eldest|youngest)\s+one\b", re.I)


# What such a line may say besides the ages: the words that hand them out, and nothing that names
# another thing ("i have 2 dogs and 4 cats" is not two children).
AGES_ONLY_WORD = frozenset("""and or is are s the other older younger little big small eldest
youngest of them both now too yeah oh well ok okay right so but theyre they there its it aged old
then
years year yrs yo nearly almost just turned about""".split())


def the_ones_are_given_one_at_a_time(text):
    """Whether the line hands the ages out one by one ("ones 7 and ones 4", "the older one is 7")."""
    if not isinstance(text, str):
        return False
    return bool(ONES_BY_ONE.search(" ".join(text.lower().replace("'", "").split())))


def ages_said_one_by_one(text, count):
    """The ages a line gives a group the store counts, or [] when it gives anything else."""
    if not isinstance(text, str) or not isinstance(count, int) or count < 2:
        return []
    flat = " ".join(text.lower().replace("'", "").split())
    if not flat or len(flat.split()) > 12:
        return []
    flat = figures_as_digits(ONES_BY_ONE.sub(" & ", flat))
    ages = []
    for word in re.split(r"[^a-z0-9]+", flat):
        if not word:
            continue
        if word.isdigit():
            age = int(word)
            if not 0 < age <= 120:
                return []
            ages.append(age)
        elif word not in AGES_ONLY_WORD:
            return []
    return ages if len(ages) == count else []


KID_ELSEWHERE = re.compile(
    r"^\s*(?:in|at)\s+(?:my|the|our|a|this|that)\s*(?:class|classes|classroom|school|nursery|"
    r"club|group|team|unit|year)\b|^\s*in\s+year\b|^\s*in\s+(?:reception|year)\b", re.I)


# A question about the number is not a statement of it: "do i have two kids" asks.
KID_ASKING = re.compile(r"^\W*(?:do|did|does|have|has|how|are|is|was|were|can|could|would)\b",
                        re.I)


# A number of zero is still a number. "i dont have any kids" said nothing to the store at all,
# so "how many kids do i have" answered "You haven't told me how many kids you have yet" to a
# person who had just said they have none. The words are the ordinary ways of saying none: a
# negated have, a plain "no kids", and the count said as zero.
KID_NONE = re.compile(
    r"\b(?:i|we)(?:'ve|ve)?\s+(?:do\s+not|dont|don't|did\s+not|didnt|didn't|have\s+not|"
    r"havent|haven't|has\s+not|hasnt|hasn't)\s+(?:got\s+)?(?:have\s+)?(?:any\s+|a\s+)?"
    r"(?:kids?|children|child)\b"
    r"|\b(?:i|we)(?:'ve|ve|\s+have|\s+have\s+got|\s+got)\s+no\s+(?:kids?|children)\b"
    r"|\bno\s+(?:kids?|children)\b"
    r"|\b(?:i|we)(?:'ve|ve|\s+have|\s+have\s+got|\s+got)\s+(?:zero|0)\s+(?:kids?|children)\b",
    re.I)


# A zero that is not a zero: "i dont have any kids yet" is somebody trying, "i dont have kids at
# home" is a house with grown children in it, and "i dont have kids anymore" with them gone says
# nothing about how many there are. None of them is a count to say back.
KID_NONE_NOT_AFTER_ALL = re.compile(
    r"\b(?:yet|anymore|any\s+more|with\s+me|at\s+home|living\s+at\s+home|but|instead)\b", re.I)


# The count said back about the group in hand: "actually there are three of them", "we have
# three altogether". People correct a number this way, with no word for the people in the line at
# all, so `kid_count` finds no "kids" to read and the store kept the old number: "i have two kids"
# then "actually there are three of them" still answered "You've got two children." The group is
# whatever the turn before was about, which is the store's question, not the reader's.
COUNT_OF_THEM = re.compile(
    r"\b(?:there are|there're|there is|theres|there's|that's|thats|we have|we've got|we got|we"
    r" have got)\s+(?P<n>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    r"\s+(?:of them|altogether|in total|in all)\b", re.I)


# A line that goes on to say where they are is about that place, not a correction of the count:
# "there are three of them at school" is not how anybody says "I have three children".
COUNT_OF_THEM_ELSEWHERE = re.compile(
    r"^\s*(?:at|in|on|down|up|over|for|from|who|here|there|with|left|still|near|around|about|"
    r"already|so|but)\b", re.I)


# The words that say the group in hand is the children: the count has nothing else to say which
# people it is about.
CHILDREN_WORDS = ("kid", "kids", "child", "children", "boy", "boys", "girl", "girls", "son",
                  "sons", "daughter", "daughters", "twin", "twins")


def count_of_the_people(text, memory):
    """"there are three of them" -> 3, while the group in hand is the children.

    The count in front of the word ("my three kids") is `kid_count`'s to read. This is the same
    fact said the other way round - the number, then "of them" - and it needs the store to say
    which people it counts: the group the turn before was about, or the children the store holds.
    "my cats are called milo, tom and otis" then "there are three of them" counts cats, and a
    number about cats is not a number of children.
    """
    if not isinstance(text, str) or KID_ASKING.match(text):
        return None
    match = COUNT_OF_THEM.search(text)
    if not match:
        return None
    said = match.group("n").lower()
    number = int(said) if said.isdigit() else KID_NUMBERS.get(said)
    if not number or not 1 < number <= 12:
        return None
    if COUNT_OF_THEM_ELSEWHERE.match(text[match.end():]):
        return None
    if not _the_group_in_hand_is_the_children(memory):
        return None
    return number


def _the_group_in_hand_is_the_children(memory):
    """Whether the children are what the chat was last on, so a bare count is theirs."""
    user_record = (memory or {}).get("user")
    turns = (memory or {}).get("turns")
    said = ""
    if isinstance(turns, list):
        last = next((turn for turn in reversed(turns) if isinstance(turn, dict)), None)
        said = " ".join(str((last or {}).get("user") or "").lower().split())
    words = set(re.split(r"[^a-z']+", said))
    if words & set(CHILDREN_WORDS):
        return True
    if isinstance(user_record, dict) and user_record.get("kids"):
        # The children are on file and the turn before named another group of people ("my cats"):
        # then the cats are what the count is about.
        others = set(words) & {"cats", "cat", "dogs", "dog", "pets", "pet", "fish", "birds"}
        return not others
    return False


# The children said as one group: "my kids are 4 and 7", "i have two children aged 4 and 7",
# "my kid is 5". They are not in RELATIONS, which names one person at a time, because a line
# about children usually gives more than one age in the same breath and the ages belong together:
# "how old are my kids" is one of the commonest things a person asks a chat that has been
# listening, and a confident "you haven't told me" straight after they did is worse than no answer.
# The count above uses its own ages reader (KID_AGES/kid_ages, which needs "are" or "aged"); this
# is the one the store files, because it also reads the ages said after a comma and keeps them in
# the order the person gave them.
KIDS = ("kids", "children", "child", "kid")


# The words a group of children can be said under. "my boys" and "my sons" are two children the
# same way "my kids" is, and the word is kept as the person each of them belongs under.
KID_GROUP = tuple(KIDS) + ("sons", "daughters", "boys", "girls")


# A child named one at a time is said with the singular word - "my daughter is 6 and my son is
# 9" - so a line that gives children their own ages is read with these as well as the group
# words above. The plural is here too: "my sons are 6 and 9" is the same line.
KID_ONE_BY_ONE = ("son", "daughter", "sons", "daughters", "child", "children", "kid",
                  "kids", "boy", "girl", "boys", "girls", "baby", "twins", "twin")


# "my kids are 4 and 7", "my children are 4, 7 and 9"
#
# Two words in front of the group were read as not the group at all. A count is the number of
# them, not part of who they are - "my two girls are 6 and 9" names the same two girls "my girls
# are 6 and 9" does - and "our" is the same possessive as "my": "our two boys are 6 and 9" and
# "our 2 girls are 6 and 9" were answered with a receipt ("Thanks for telling me") and the store
# kept nothing, so "how old are they" a turn later had no ages to read.
A_COUNTED_GROUP = (r"\b(?P<whose>my|our)\s+"
                   r"(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
                   r"|\d{1,2})\s+)?")


KID_AGES_ARE = re.compile(A_COUNTED_GROUP + r"(?P<who>" + "|".join(KIDS) + r")\s+(?:are|is)\s+"
                          r"(?:both\s+)?(?:aged?\s+)?(?P<ages>\d{1,3}"
                          r"(?:\s*(?:,|and)\s*\d{1,3})*)", re.I)


# The same ages said under any of the words a group of children go by: "my boys are 9 and 6" is
# the line "my kids are 9 and 6" in another word, and the ask can be in either.
KID_GROUP_AGES_ARE = re.compile(A_COUNTED_GROUP + r"(?P<who>" + "|".join(KID_GROUP) + r")\s+"
                               r"(?:are|is)\s+(?:both\s+)?(?:aged?\s+)?"
                               r"(?P<ages>\d{1,3}(?:\s*(?:,|and)\s*\d{1,3})*)", re.I)


# "i have two kids, 4 and 7", "i've got three children aged 2, 4 and 7": the count in front of
# the word is the number of them, not an age, so the ages are read after the word.
KID_COUNT_AGES = re.compile(
    r"\b(?:i|we)(?:\s+have|'ve|ve)(?:\s+got)?\s+(?:\w+\s+)?(?P<who>kids|children)\b"
    r"(?:[^.\d]{0,14})(?P<ages>\d{1,3}(?:\s*(?:,|and)\s*\d{1,3})*)", re.I)


# The same ages in a line that counts the children without the word "my" in front of them: "we
# are 2 adults and 2 kids aged 6 and 9" is two children and their two ages, and the store kept
# nothing at all, so the very next "how old are they" said they had never told.
KID_ADULTS_AGES = re.compile(
    r"\b(?:kids?|children|child)\b(?:[^.\d]{0,14})?(?:aged?|of|are)\s+"
    r"(?P<ages>\d{1,3}(?:\s*(?:,|and)\s*\d{1,3})+)", re.I)


# A number that says where the group sits rather than what age each of them is: "two kids under
# 5" is not "two kids aged 5".
KID_AGES_NOT = re.compile(r"\b(?:under|over|above|below|nearly|almost|about|round|around)\s*$", re.I)


# The children named with their ages in one breath: "my kids are ada 7 and sam 4", "my children
# are ada, 7, and sam, 4". Each child is their own person, with their own name and their own age,
# so "how old is ada" and "how old are my kids" are both answerable from the line. The group word
# in front is what says these are their children, and it is kept as the person each one of them
# belongs under.
KID_NAME_AGES = re.compile(r"\bmy\s+(?P<who>" + "|".join(KID_GROUP) + r")\s+(?:are|is)\s+(?P<rest>"
                           r"[a-z][a-z'-]{1,19}\s+\d{1,3}(?:\s*(?:,|and)\s*"
                           r"[a-z][a-z'-]{1,19}\s+\d{1,3})*)\b", re.I)


KID_NAME_AGE = re.compile(r"(?P<name>[a-z][a-z'-]{1,19})\s+(?P<age>\d{1,3})", re.I)


# A figure the line says after the names it has already paired up. The line reaches this reader
# with its numbers spelled out ("my kids are ada 7 and four"), so a digit alone is not enough to
# see the second child: pairing "ada 7" on its own invents one child and quietly drops the other.
FIGURE_AFTER = re.compile(r"\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven"
                          r"|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
                          r"|nineteen|twenty)\b", re.I)


# The words that say where a figure sits rather than whose it is: "my kids are nearly 5 and 7"
# is not two children called Nearly and 7, and "my children are under 5" is not a child called
# Under. `KID_AGES_NOT` already stops the plain ages reader taking the figure; a name taken from
# one of these words is worse than the shrug, because it invents a person and drops the other
# child.
NOT_A_NAME_HEDGE = frozenset("""nearly almost about around round under over above below
roughly approximately approx somewhere only just both all each every either neither
aged age ages yrs year years old""".split())


def _kids_named_with_ages(text):
    """[{"who", "name", "age"}] for the children given with a name and an age, or []."""
    found = []
    who_word = "|".join(RELATIONS)
    for match in KID_NAME_AGES.finditer(text):
        rest = match.group("rest")
        if KID_AGES_NOT.search(text[:match.start("rest")]):
            continue  # "my kids are nearly 5 and 7" gives a figure for the group, not a name
        pairs = list(KID_NAME_AGE.finditer(rest))
        if not pairs:
            continue
        if len(re.findall(r"\d{1,3}", rest)) != len(pairs) or FIGURE_AFTER.search(text[match.end():]):
            # One age of the run was given without a name ("my kids are ada 7 and 4"), so the
            # line is not a person per figure: the reader matches the named part and would stop
            # before the bare one. Pairing "ada 7" alone invents a child and drops the 4, so the
            # line is left to the readers that were there before.
            continue
        for pair in pairs:
            name, age = pair.group("name"), int(pair.group("age"))
            low = name.lower()
            if (low in NOT_A_NAME or low in KIDS or low in NOT_A_NAME_HEDGE
                    or low in NOT_A_NAME_MIDDLE or low in NOT_A_NAME_THING
                    or low in NOT_A_NAME_STATE
                    or low in MONTHS or low in DAYS or not 0 <= age <= 120):
                continue
            if age <= 2 and not name[:1].isalpha():
                continue
            found.append({"who": match.group("who").lower(), "name": name,
                          "age": age})
    return found


def _the_same_person(one, other):
    """Whether two readings of the people in a line are about the same person.

    Two children named in one breath ("my kids are ada 7 and sam 4") share the word in front of
    them, so the word alone is not enough to tell them apart: the name is what says which child
    the age belongs to, and two named children are never folded into one.
    """
    if (one.get("who") or "") != (other.get("who") or ""):
        return False
    return str(one.get("name") or "").lower() == str(other.get("name") or "").lower()


# A state of a person they live with that changes what you would suggest for them: a pregnancy,
# or an alcohol-free limit. It is a fact about that person, like a diet or an age, so it is kept
# against them and never read as something wrong with the person typing ("my wife is pregnant so
# she cant drink" was answered "What has your wife said about it - and how long has it been like
# this?"). Only a relation-named person ("my wife", "my daughter"), never "i".
_STATE_WHO = lambda: r"\bmy\s+(?P<who>" + "|".join(sorted(RELATIONS, key=len, reverse=True)) + r")"


# The length comes before the word as often as not: "my wife is 8 weeks pregnant" is the common
# way a pregnancy is said, and read only as "is pregnant" it kept nothing at all - the store had
# no pregnancy for her, so the turn after it ("she feels sick in the mornings") was answered by a
# card that opened "Morning sickness that is not pregnancy is usually...". The weeks are part of
# the same fact: they are kept with it, because they date nothing and are only true of now.
OTHER_STATE = re.compile(
    _STATE_WHO() + r"\s*(?P<tense>'s|is|are|was|were)\s+"
    r"(?:(?P<weeks>\d{1,2})\s*(?:weeks?|wks?)\s+)?"
    r"(?P<state>pregnant|expecting|breastfeeding|nursing a baby)\b", re.I)


# The words that mean the pregnancy, and the words that do not. A woman who is breastfeeding was
# kept as pregnant and answered "your wife being pregnant is worth knowing": the state is the
# word they said, and a state the store did not hear is a fact it must not put on anyone.
PREGNANCY_STATES = ("pregnant", "expecting")


OTHER_LIMIT = re.compile(
    _STATE_WHO() + r"\s*(?:can'?t|cannot|doesn'?t|does not|won'?t|will not|isn'?t)"
    r"\s+(?:really\s+)?(?:drink|drinks)\b"
    # "my son cant drink milk" is about the milk, not about alcohol: the limit ends where the
    # line does, or goes on with a word that is about drinking and nothing else.
    r"(?=\s*(?:$|[.,;!?]|alcohol\b|at all\b|any ?more\b|anymore\b|either\b|though\b|"
    r"these days\b|now\b|when\b))", re.I)


# The person's own state, said about themselves: "im 12 weeks pregnant", "i'm expecting a baby".
# The store kept this state only for somebody else, so the person's own news was congratulated and
# forgotten, and "how far along am i" after it got a search hedge. The subject is the person, so
# the fact is filed against them (`memory["user"]`) rather than against a relation.
OWN_STATE = re.compile(
    # The pronoun has to open the clause: "i thought i was pregnant" is a thought about a maybe,
    # and the "i was pregnant" inside it is not news.
    r"(?:^|[.;,!?]\s*|\b(?:and|but|so|because|although|though)\s+)"
    r"(?:i|im|i'm|i’m|ive|i've)\s+(?:am\s+|was\s+|feel\s+|think\s+i\s*m\s+)?"
    # "not" and "no longer" take the state back out: "im not pregnant" says the opposite.
    r"(?!not\b|no longer\b|never\b|wasnt\b|wasn't\b)"
    r"(?:(?P<weeks>\d{1,2})\s*(?:weeks?|wks?)\s+)?"
    r"(?P<state>pregnant|expecting)\b", re.I)


# A pregnancy nobody put a length on is still the state, and the length is only true of now.
OWN_PREGNANCY_WEEKS_MAX = 45


def _own_states(text):
    """{"pregnant": True, "weeks": 12} for the person themselves, or {}.

    A length said with the state is part of the same fact, exactly as it is for "my wife is 8
    weeks pregnant": the weeks date nothing, they are only true of now, so a past tense keeps
    nothing at all.
    """
    # "im eight weeks pregnant" is the same fact as "im 8 weeks pregnant": most people spell a
    # small number out, and the length was lost while the state was kept, so "how far along am i"
    # after it was a search hedge about a chat that had said the answer.
    for match in OWN_STATE.finditer(figures_as_digits(text)):
        said = match.group(0).lower()
        if re.search(r"\b(?:was|were|thought|maybe|might|may|hope|hoping|could)\b", said):
            continue
        found = {"pregnant": True}
        weeks = match.group("weeks")
        if weeks is not None and 1 <= int(weeks) <= OWN_PREGNANCY_WEEKS_MAX:
            found["weeks"] = int(weeks)
        return found
    return {}


def _other_states(text):
    """[{"who", "pregnant"|"breastfeeding": True}] and [{"who", "drinks": False}] for these people.

    A question is not a fact: "is my wife pregnant?" asks, and only a line that says it stores it.
    Nor is a thing that was: "my wife was pregnant" is not a state she is in now, so a past tense
    keeps nothing (said back in the present it told a woman whose child had arrived that a drink
    was off the table because she was pregnant).
    """
    found = []
    for match in OTHER_STATE.finditer(text):
        if match.group("tense").lower() in ("was", "were"):
            continue
        who = " ".join(match.group("who").lower().split())
        state = match.group("state").lower()
        if state in PREGNANCY_STATES:
            entry = {"who": who, "pregnant": True}
            weeks = match.groupdict().get("weeks")
            if weeks and 1 <= int(weeks) <= 45:
                entry["weeks"] = int(weeks)
            found.append(entry)
        else:
            found.append({"who": who, "breastfeeding": True})
    for match in OTHER_LIMIT.finditer(text):
        who = " ".join(match.group("who").lower().split())
        found.append({"who": who, "drinks": False})
    return found


# The child given as "a 4 year old": the age comes with no age word in front of it and, often,
# no relation either ("i have a 4 year old and a 7 year old"). Read as digits above, the phrase
# is the same as "aged 4", and the children it counts are the children the chat knows about.
YEAR_OLD = re.compile(r"\b(?P<age>\d{1,3})\s*(?:years?|yrs?)[- ]old\b", re.I)


# "when i was a 4 year old" is the person's own age, not their child's.
OWN_AGE_BEFORE_IT = re.compile(r"\b(?:i|we)\s+(?:was|were|am|had been)\s*(?:a|an)?\s*$", re.I)


# An animal is aged in years too, and "our dog is a 4 year old" is about the dog.
YEAR_OLD_ANIMAL = re.compile(r"\b(?:" + "|".join(sorted(ANIMALS)) + r")\b", re.I)


# A thing is aged in years as well, and it is not a child: "my laptop is really slow" / "its
# about 5 years old" was read as a five year old child, and the turn after it asked the person
# how old they were. The subject of the age is the word before it, so a thing named there (or the
# pronoun for one) means the number is the thing's age, not a child's.
THING_AGED = re.compile(
    r"\b(?:it|its|it's|that|thats|that's|this|these|those|there|hes|he's|shes|she's|theyre|"
    r"they're|mine|ours|yours|theirs)\b[^.!?]{0,12}$", re.I)


# A person pointed at is a person, and the years after them are theirs: "he is 8 years old" says
# what "hes 8" says, and neither line says there are any children. Read as a count of children,
# the store answered "One kid, eight - noted." to a person who had just said how old their nephew
# was, and the count then stood as a fact about the family. The pronoun's own entry keeps the
# age, so nothing is lost by standing down here.
A_PERSON_AGED = re.compile(
    r"\b(?:he|she|they|hes|she's|he's|shes|theyre|they're)\b[^.!?]{0,12}$", re.I)


NAMED_THING_AGED = re.compile(
    # A figure belongs in the noun because the reading spells figures as digits before this runs:
    # "the old one is 12 years old" arrives as "the old 1 is 12 years old", and a noun class of
    # letters alone could not see the thing that is aged. The age was then filed as a twelve year
    # old child, and the store said "One kid, twelve - what are they into?" to a person who had
    # just said how old their washing machine was. Any numbered thing is the same ("my machine 2
    # is 8 years old"), so the noun takes a figure wherever it falls.
    r"\b(?:my|our|your|his|her|their|the)\s+(?P<noun>[a-z' 0-9]{1,30}?)\s*"
    r"(?:is|was|are|were|s|'s)\b[^.!?]{0,12}$", re.I)


# A thing is aged in years without a be-form too: "a dell about 4 years old", "the sofa, about 6
# years old". The determiner and the thing are there; only the word "is" is missing. Without this
# the age went in as a child's - "a dell about 4 years old" was answered "One kid, four. What are
# they into at the moment?" in a chat about a laptop fan, and "the sofa, about 6 years old" the
# same. So when a determiner names a thing and only a be-form or a qualifier ("about", "roughly",
# "around", "nearly", "only", "just") sits between that name and the age, the age is the thing's -
# unless the name is a person word, which is what the check below is for. A determiner with nothing
# after it names no thing ("i have a 4 year old and a 7 year old"), so it is left alone.
THING_AGED_QUALIFIED = re.compile(
    r"\b(?:a|an|the|my|our|your|his|her|their)\s+(?P<noun>[a-z'][a-z'0-9]*)(?:\s*,)?\s*"
    r"(?:(?:is|was|are|were|s|'s)\s*)?(?:(?:,\s*)?(?:about|roughly|around|nearly|only|just)\s*)?$",
    re.I)


# "the youngest about 4 years old" is one of the children, not a thing that is 4 years old.
PERSON_ELSEWHERE = frozenset("""youngest oldest eldest younger older middle first second third
last little big small""".split())


# The words a line uses for the children themselves: a noun here is a person ("my kids are 4 and
# 7 years old") and the age is one of theirs.
PEOPLE_AGED = frozenset(KID_GROUP) | frozenset("""kid child children boy boys girl girls son
sons daughter daughters twin twins baby babies toddler toddlers lad lads lass lasses""".split())


# "my 5 year old laptop" ages the laptop, not a child: the word just after the age says what the
# age belongs to.
AFTER_YEAR_OLD = re.compile(r"^\s+(?P<word>[a-z']{2,})\b", re.I)


AFTER_YEAR_OLD_OKAY = frozenset("""and or but who which that whose now today next in at on
with too as when so already nearly exactly almost about boy girl kid child son daughter lad
lass twins baby toddler to from""".split())


# A child is under eighteen, so a grown-up's age is not a count of children when the line does
# not say whose age it is.
CHILD_AGE_UNDER = 18


# "my boys are 4 and 7 years old" says the years once, at the end of the list, so the figure the
# reader sees is the last one of a list the reader for the named group has already read whole.
LIST_BEFORE_IT = re.compile(r"\d{1,3}\s*(?:,|and|, and)\s*$", re.I)


# The rest of a list of ages after the first one: "my brothers are 20 and 24".
A_LIST_OF_AGES = re.compile(r"(?P<ages>\d{1,3}(?:\s*(?:,|and|, and)\s*\d{1,3})+)\b", re.I)


GROUP_NAMED = re.compile(r"\b(?:" + "|".join(KID_GROUP) + r")\b", re.I)


# The thing an age belongs to is often a clause away from the number: "it's a front loader,
# about five years old" put the whole of "a front loader," between the pronoun and the years, so
# the two guards above (which reach 12 characters back) sailed past it and the store filed a
# five-year-old child. On the same chat the store then answered "how many kids do i have" with
# "You've got one kid." about a child nobody had. So the subject is read back to the last thing
# the line named, and a line with no people word in it at all cannot be counting children.
THING_NAMED_BACK = re.compile(
    r"\b(?:it|its|it's|that|thats|that's|this|these|those|there|they|theyre|they're)\b"
    r"|\b(?:my|our|your|his|her|their|the)\s+(?P<noun>[a-z' ]{1,30}?)\s*"
    r"(?:is|was|are|were|s|'s)\b", re.I)


PEOPLE_NAMED_ANYWHERE = re.compile(r"\b(?:" + "|".join(sorted(PEOPLE_AGED)) + r")\b", re.I)


# How far back the subject of an age is worth looking for: one short clause and the thing it
# named ("my old washing machine, a front loader, about five years old").
SUBJECT_REACH = 80


# The nouns an age in years is said of, and the "is" that puts the age after them, with the
# appositive people really use in between: "my washing machine is a front loader, about 4 years
# old". The window is wide because the words between the thing and the figure are the point of
# the sentence - a make, a model or a type - and the reader that can only see twelve characters
# past the "is" filed a four year old child for a four year old washing machine, and the turn
# after asked the person about the kid.
_A_THING_SAID_IS = re.compile(
    r"\b(?:my|our|your|his|her|their|the)\s+(?P<noun>[a-z' 0-9]{1,30}?)\s*"
    r"(?:is|was|are|were|s|'s)\b[^.!?]{0,40}$", re.I)


# The same, said with a pronoun: "its a front loader, about 4 years old", "thats a band new one,
# two years old". No noun is named, so the pronoun is the subject and whatever it points at is
# the thing, because a person is named rather than pointed at when their age is given.
_A_THING_POINTED_AT = re.compile(
    r"\b(?:it|its|it's|that|thats|that's|this|these|those|there|theyre|they're|mine|ours)\b"
    r"[^.!?]{0,40}$", re.I)


def _the_years_are_a_things(text):
    """Whether every age in years on the line belongs to a thing rather than to a child.

    A line can age a person and a thing together ("my son is 4 and the dog is 6 years old"), and
    one thing aged on it is not enough to drop the children the line counts - so every figure has
    to be a thing's before the reading stands down.
    """
    figures = list(YEAR_OLD.finditer(text))
    if not figures:
        return False
    for match in figures:
        before = text[max(0, match.start() - 80):match.start()]
        words = re.findall(r"[a-z']+", before.lower())
        if PEOPLE_AGED.intersection(words):
            return False
        named = _A_THING_SAID_IS.search(before)
        if named and named.group("noun").split()[-1].lower() not in PEOPLE_AGED:
            continue
        if _A_THING_POINTED_AT.search(before):
            continue
        return False
    return True


def _children_by_year_old(text):
    """The children a line counts in years: {"who": "kids", "ages": [...]}, or None."""
    if not YEAR_OLD.search(text):
        return None
    if _the_years_are_a_things(text):
        return None
    if (not GROUP_NAMED.search(text)
            and re.search(r"\bmy\s+" + _A_PERSON + r"\b", text, re.I)):
        # "my daughter is a 4 year old" names one child, and the reader for the people the line
        # names keeps her age; filing the same number against the children as a group would say
        # "your kids is 4" about a child the line had a name for.
        return None
    group_named = bool(GROUP_NAMED.search(text))
    if group_named and len(YEAR_OLD.findall(text)) > 1:
        # "my boys are 4 and 7 years old" says the years once at the end of the list, and the
        # reader for the group the line named has already read both ages; reading the last one
        # again would put a second, smaller answer about the children on top of it.
        return None
    ages = []
    for match in YEAR_OLD.finditer(text):
        age = int(match.group("age"))
        if not 0 <= age <= 120:
            continue
        if OWN_AGE_BEFORE_IT.search(text[:match.start()]):
            continue
        if not group_named and A_PERSON_AGED.search(
                text[max(0, match.start() - 40):match.start()]):
            # "he is 8 years old" is somebody's age, said the way "hes 8" says it, and the
            # reader for the pronoun keeps it. Counting a child here put a kid in the store the
            # person never mentioned.
            continue
        if YEAR_OLD_ANIMAL is not None and YEAR_OLD_ANIMAL.search(
                text[max(0, match.start() - 24):match.start()]):
            continue
        before = text[max(0, match.start() - 40):match.start()]
        if breeds.BREED_RE.search(before):
            # A breed is the animal it is, and an animal is aged in years: "hes a lurcher, about
            # two years old" is the dog's age. Read as a child it put a kid in the store the
            # person never mentioned - the turn after answered "One kid, two - good to know. Tell
            # me about them.", and the next ask about the dog came back with the children's food.
            continue
        if not PEOPLE_NAMED_ANYWHERE.search(text):
            # Nothing in the line is a person, so the number cannot be a child's age: it is the
            # age of whatever the line was about. "how old is it" is the next question, not "how
            # many kids do you have". This is the same fault the breed guard above fixes for an
            # animal, for every other thing: a machine's age is a whole clause from its name
            # ("it's a front loader, about five years old"), further than the guards under this
            # line can see.
            nearest = None
            for found in THING_NAMED_BACK.finditer(
                    text[max(0, match.start() - SUBJECT_REACH):match.start()]):
                nearest = found
            noun = (nearest.groupdict().get("noun") or "").split() if nearest else []
            if nearest is not None and (not noun or noun[-1].lower() not in PEOPLE_AGED):
                continue
        if group_named and LIST_BEFORE_IT.search(before):
            continue
        if THING_AGED.search(before):
            continue
        qualified = THING_AGED_QUALIFIED.search(before)
        if qualified:
            thing = qualified.group("noun").lower()
            if thing not in PEOPLE_AGED and thing not in PERSON_ELSEWHERE:
                continue
        named = NAMED_THING_AGED.search(before)
        # The thing can be named in more than one word ("my washing machine is 8 years old"), so
        # the noun that is aged is the last word of the phrase in front of the be-form.
        if named and named.group("noun").split()[-1].lower() not in PEOPLE_AGED:
            continue
        after = AFTER_YEAR_OLD.match(text[match.end():])
        if after and not group_named and after.group("word").lower() not in AFTER_YEAR_OLD_OKAY:
            continue
        if age >= CHILD_AGE_UNDER and not group_named:
            continue
        ages.append(age)
    if not ages:
        return None
    return {"who": "kids", "ages": ages} if len(ages) > 1 else {"who": "kids", "age": ages[0]}


def _ages_held(entry):
    """Every age an entry holds, the list and the lone one together, in the order given."""
    held = [age for age in entry.get("ages") or [] if isinstance(age, int)]
    if isinstance(entry.get("age"), int) and entry["age"] not in held:
        held.append(entry["age"])
    return held


def _keep_the_ages(found, entry):
    """Add a reading about a group of children, or fold it into the group already read.

    Two readings of one line of the same children are the same fact however they were worded
    ("my kids are 4 and 7" and "my kids are 4 and 7 years old"), and the fuller reading wins.
    A lone age beside a list is the reading that saw one figure of the list, which is what put
    "7" on the end of "4 and 7" and made the chat answer "Your kids are 7, 4 and 7."
    """
    who = entry.get("who")
    known = next((one for one in found if one.get("who") == who), None)
    if known is None:
        found.append(dict(entry))
        return
    said, held = _ages_held(entry), _ages_held(known)
    if held and said and len(held) >= len(said) and set(said) <= set(held):
        return  # the group already read says everything this reading does
    known.pop("age", None)
    known["ages"] = said if len(said) > 1 else held + [age for age in said if age not in held]
    if len(known["ages"]) == 1:
        known["age"] = known.pop("ages")[0]


def _relation_before(text, pos):
    """The relation the line named most recently before `pos`, or "" for none."""
    who = ""
    for match in re.finditer(r"\bmy\s+(" + "|".join(RELATIONS) + r")\b", text[:pos], re.I):
        who = match.group(1).lower()
    return who


BARE_NAME = re.compile(r"^[\W_]*([a-zA-Z][a-zA-Z'-]{1,19})[\W_]*$")


NOT_A_BARE_NAME = frozenset("""
yes yea yeah yep no nope nah ok okay k fine good great thanks thank ta cheers please
hi hello hey bye later maybe sure right true false nothing none neither dunno
sorry sure why what when where who how which it that this there here them him her
""".split())


def names_offered(memory):
    """The names the bot itself put in front of them on the turn before, and what they are for.

    "what should i name it" is answered with three names, and the next line is one of them or a
    name of their own. That turn is a choice, not a fact to look up, so the list is read back
    out of the bot's own reply instead of being written down twice.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    match = NAMES_OFFERED.search(str(turns[-1].get("bot") or ""))
    if not match:
        return None
    names = re.findall(r"[A-Za-z][a-z'-]{1,20}", match.group("list"))
    names = [word for word in names if word.lower() not in ("or", "and")]
    if len(names) < 2:
        return None
    return {"animal": match.group("animal").lower(), "names": names}


# "shes not vegetarian", "he used to be vegan", "she said she eats meat": the line is not a
# statement that this is how they eat now, so nothing is kept.
NOT_DIET = re.compile(r"\b(?:never|no longer|used to|isnt|isn'?t|arent|aren'?t|said|says|"
                      r"asked|wondered|whether)\b|"
                      # "she's not vegetarian", "he was not vegan": the "not" belongs to the state,
                      # and a bare "does not eat dairy" is the diet itself.
                      r"\b(?:is|are|was|were|(?:he|she|it|they|we|i)(?:'s|s|'re|re)?)\s+not\b",
                      re.I)


# Things that say nothing about what a person eats: "he doesnt eat much", "she doesnt eat
# anything green". A food name has to survive these to be kept.
DIET_STOP = ALLERGY_STOP | frozenset("""much many more anything everything nothing something
food stuff lot any""".split())


def foods_ruled_out(found):
    """Every food a line rules out, for the person or for somebody they named, or [].

    A diet is kept as "no fish", an allergy as "fish", and a line can rule out several ("my son
    cant eat fish and nuts"). The dictionary is what `extract` already returned, so the caller
    does not read the line twice. A limit on a food is the only kind a reply can be built on: the
    words after "cant eat" that name no food are already kept out by `_only_stop_words`.
    """
    if not isinstance(found, dict):
        return []
    foods = []
    match = re.match(r"^\s*no\s+([a-z][a-z ]{1,20}?)\s*$", str(found.get("diet") or ""), re.I)
    if match:
        foods.append(match.group(1))
    # The speaker's own limit, which is kept as an allergy whatever way it was said: "i cant eat
    # chilli" files the chilli, and a reader that only looks at a diet and at other people finds
    # no limit in the line and answers it as nothing (a filler, or a dish with chilli in it).
    mine = found.get("allergies") or ()
    if not isinstance(mine, (list, tuple)):
        mine = [mine]
    foods.extend(str(food).strip() for food in mine if str(food).strip())
    for entry in found.get("others") or ():
        if not isinstance(entry, dict):
            continue
        match = re.match(r"^\s*no\s+([a-z][a-z ]{1,20}?)\s*$",
                         str(entry.get("diet") or ""), re.I)
        if match:
            foods.append(match.group(1))
        allergies = entry.get("allergies") or ()
        if not isinstance(allergies, (list, tuple)):
            allergies = [allergies]
        foods.extend(str(food).strip() for food in allergies if str(food).strip())
    return foods


# The food groups a diet is about: "she doesnt eat dairy" is how she eats, "he wont eat
# vegetables" is a Tuesday at the dinner table.
DIET_GROUP = frozenset("""meat meats fish dairy gluten wheat eggs egg sugar carbs seafood
shellfish pork beef chicken lamb alcohol nuts soya soy""".split())


# A word about not drinking is a limit like a diet, and one said of somebody else is kept against
# that person the same way: "my mate is teetotal" filed nobody, so "what can he have at the do" had
# nothing to answer with. The verb ("my dad doesnt drink") is already read as that person's
# `drinks: False` and is left to it.
OTHER_NO_DRINK = re.compile(
    r"(?<!\w)(?P<subj>(?:my|our|his|her|their)\s+[a-z]+|he|she|they)(?!\w)"
    r"[^.,;!?]{0,24}?"
    r"(?:(?:is|are|'s|'re|s|re)\s+(?:a\s+|an\s+)?"
    r"(?P<word>teetotal(?:ler|lers)?|tee-?total(?:ler|lers)?|non-?drinker|nondrinker)(?!\w))",
    re.I)


def _somebody(subject_text):
    """Who a subject phrase names: ("other", "mum") for "my mum", ("other", "") for "shes"."""
    named = re.match(r"(?:my|his|her|their|our)\s+(\w+)", subject_text or "", re.I)
    if named:
        word = named.group(1).lower()
        return "other", SPOKEN_RELATION.get(word, word)
    return "other", ""


# A condition said of somebody else, which the store keeps against that person the same way it
# keeps their allergy or their diet. "my son is coeliac" was only the word "son" and a line in
# the greeting, so the next turn - "what can he eat" - had nothing to answer with and the turn
# after it forgot the boy could not have gluten. The speaker's own conditions are CONDITION
# above; nothing here is ever kept as the user's.
# Both ways people say it: what they are ("my mum is diabetic") and what they have ("my dad has
# diabetes"). The clause has to end after the word, so "my mum has a diabetes appointment on
# tuesday" is an appointment and not a condition - the words after it are what carry the news.
# "high blood pressure" and "crohns" are kept as said: they name no single food, but they are
# what the person has, and a follow-up ask can still be answered honestly with them.
OTHER_CONDITION = re.compile(
    r"(?<!\w)(?P<subj>(?:my|our|his|her|their)\s+[a-z][a-z'\u2019-]*(?:\s+in\s+laws?)?|he|she|they)(?!\w)"
    r"(?:'s|'re|\s+is|\s+are|\s+was|\s+were|s|\s+has|\s+have|\s+got|"
    r"\s+suffers?\s+from|\s+suffering\s+from)\s+(?:a\s+|an\s+)?"
    r"(?P<cond>coeliac|celiac|diabetic|asthmatic|epileptic|anaemic|anemic|"
    r"lactose\s+intolerant|gluten\s+intolerant|"
    r"diabetes|asthma|epilepsy|anaemia|anemia|arthritis|crohn'?s|colitis|ibs|"
    r"high\s+blood\s+pressure|high\s+cholesterol|coeliacs?\s+disease)\b"
    r"(?=\s*(?:[,.;!?]|$|\s+(?:and|but|so|because|which|too|as\s+well|now|since|at\s+the\s+moment)\b))",
    re.I)


# A condition said as what they have is kept as the word for what they are: the reply says "your
# mum is diabetic", which is the same fact in the words the rest of the bot knows it by.
CONDITION_AS_A_WORD = {"diabetes": "diabetic", "asthma": "asthmatic",
                       "epilepsy": "epileptic", "anaemia": "anaemic",
                       "anemia": "anaemic", "anemic": "anaemic", "celiac": "coeliac",
                       "crohns": "crohn's", "crohn": "crohn's",
                       "coeliac disease": "coeliac", "celiac disease": "coeliac",
                       "coeliacs disease": "coeliac"}


# What somebody else in the chat does all day, which the store keeps against that person the way
# it keeps their age or their diet. "my sister is a nurse" then "what does my sister do" was a
# search hedge about somebody the chat had been told about a turn before, because every job
# reader here is about the speaker's own work.
# A role is a phrase of ordinary words and it stops where the line turns to something else: a
# connective, a place or a clause. Read as one greedy run, "my mum is a nurse and my dad is a
# builder" named the mum's job as "nurse and my dad is a builder" and never saw the dad at all.
JOB_PHRASE = (r"(?P<job>[a-z][a-z'\u2019-]*"
              r"(?:\s+(?!(?:and|but|so|because|who|that|which|in|at|for|on|with|from|near)\b)"
              r"[a-z][a-z'\u2019-]*){0,3})")


OTHER_JOB = re.compile(
    r"(?<!\w)(?P<subj>(?:my|our|his|her|their)\s+[a-z][a-z'\u2019-]*|he|she|they)"
    r"(?:'s|'re|\s+is|\s+are|\s+was|\s+were|s)\s+(?:a|an)\s+" + JOB_PHRASE, re.I)
