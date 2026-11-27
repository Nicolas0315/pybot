"""Part 4 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from .normalize import KIN
from .kinds_part_01 import (
    THANKS, GREETINGS, FAREWELLS, POLITE, TERMS_OF_ADDRESS, AFFIRM, ACK,
)
from .kinds_part_02 import (
    CLAUSE_OPENERS, NOT_AFTER_THE_BOT, NOT_AUX, NOT_BEFORE_THE_BOT, SELF_ASK, SELF_FILLER,
    SELF_WORDS, _a_person_they_like, _a_thing_they_own, ASSISTANT_NAMES, PRODUCT_ASK_TAIL,
    PRODUCT_ASK_WORDS, ROBOT_WORDS,
)
from .kinds_part_03 import (
    BOT_LIFE, BOT_LIFE_FILLER, BOT_LIFE_ASK,
)


# The bot's own doings, in the words people use to ask the size of them: "how many people
# have you talked to", "how many questions do people ask you", "how many conversations have
# you had". A count of one of these is a question about what the bot does, not a sum to work
# out, so it is read as a question about the bot and the maths entry never sees it.
BOT_DOINGS = frozenset("""
talk talked talking speaks spoke spoken speaking chat chatted chatting answer answered
answering ask asked asking help helped helping heard listening sent send messages messaged
met meet meets
""".split())


# What a count of the bot's doings is a count of. "people" and "questions" are in it because
# the doing beside them is the bot's: "how many people have you talked to" counts the bot's
# chats, and "how many questions do people ask you" counts the bot's day. A count of a thing
# of the world ("how many eggs have you got", "how many people are coming to dinner") is none
# of this and keeps its reading.
BOT_COUNTED = frozenset("""
people person persons conversation conversations chat chats message messages question questions
folk folks
""".split())


COUNT_OPENERS = frozenset("so and but then also".split())


# Who the doing is done by, when it is not the bot itself. "how many questions do people ask
# you" counts the bot's day because "people" is nobody in particular; "how many questions does
# the doctor ask you" is the doctor's count, and the person is the one being asked, so it is not
# a question about the bot at all. The list is closed on purpose: a doer it does not hold is a
# third party the line named, and that line keeps its own reading.
# "have" is only a doing when what is counted is the chat itself: "how many conversations did
# you have today" is the bot's day, while "how many people have you got coming" is the person's
# dinner, and "how many eggs have you got" is the fridge. So the plain "have" needs the count to
# be a chat before it counts as something the bot did.
BOT_HAVE = frozenset("have has had having".split())


BOT_CHATS = frozenset("""
chat chats conversation conversations talk talks discussion discussions catch-up
""".split())


BOT_DOERS = frozenset("""
you u ya yourself people person folk folks anyone anybody somebody someone everybody everyone
they customers users guests strangers visitors readers
""".split())


# Words that can stand between the doer and its doing: "have you actually talked to", "did you
# ever chat". A word outside this set is the doer.
COUNT_FILLERS = frozenset("""
have has had having do does did done been being be is are was were ever already just really
also still not never once yet actually even only so far before since
""".split())


def _counts_its_own_doings(norm):
    """True when the line counts something of the bot's own life rather than working a sum out.

    "how many people have you talked to" is a question about the bot, and read as a number it
    reached the maths entry and answered a stranger with a porridge recipe. The line has to
    open on "how many/much", count a thing the bot's doings happen to (people, conversations,
    questions), say "you", and name one of those doings.
    """
    words = list(norm)
    at = 0
    while at < len(words) and words[at] in COUNT_OPENERS:
        at += 1
    if words[at:at + 2] not in (["how", "many"], ["how", "much"]):
        return False
    rest = words[at + 2:]
    if not set(rest) & BOT_COUNTED or not {"you", "u", "ya", "your", "ur"} & set(rest):
        return False
    # "had" is the doing in "how many conversations have you had": the count is the bot's day.
    # The first doing is not always the one with a doer ("messages" is a doing in "how many
    # messages have you sent"), so every doing in the line is asked about its doer.
    return any(_the_doer_is_the_bot(rest, i) for i, w in enumerate(rest)
               if w in BOT_DOINGS or w in BOT_HAVE and _a_count_of_chats(rest))


def _a_count_of_chats(rest):
    """True when what the line counts is the chat itself ("how many chats did you have today")."""
    return bool(set(rest) & BOT_CHATS)


def _the_doer_is_the_bot(rest, doing):
    """Whether the doing at `doing` is the bot's own, or nobody-in-particular's.

    "how many people have you talked to" is the bot talking, and "how many questions do people
    ask you" is the bot being asked: both count the bot's day. "how many questions does the
    doctor ask you" is the doctor asking, and the only person it is about is the one typing, so
    the memory answer would be a reply to a question nobody asked. Walking back over the
    auxiliaries and the adverbs lands on the doer, and the doer has to be the bot or a word that
    names nobody in particular.
    """
    at = doing - 1
    while at >= 0 and (rest[at] in COUNT_FILLERS or rest[at].endswith("ly")):
        at -= 1
    return at >= 0 and rest[at] in BOT_DOERS


def _asks_about_its_experience(norm):
    """True for "have you ever ..." put to the bot about a life it has not had.

    "have you ever had a day like that", "have you ever been in love", "were you ever ill": the
    thing asked about is the bot's own experience, and a program has none, so the honest answer
    is that nothing like that has happened to it. All three went to the search hedge, which asked
    the person to go and look it up as though they had asked about the world.

    What keeps this from taking turns it should not answer is the vocabulary, the same way the
    other asks about the bot's life are held: every word after the ask has to be a word of a life
    (been, had, felt, ill, love, a day) or a word that says nothing on its own. A line that names
    a thing of the world is a question about that thing and keeps its own answer - "have you ever
    eaten a jacket potato" is the potato recipe, "have you ever seen a double yolk egg" is the egg
    card, "have you ever heard of truffle oil" is a knowledge ask. A problem of theirs in the same
    breath is theirs too ("have you ever seen my boiler do this").
    """
    words = list(norm)
    if not words:
        return False
    said = " ".join(words)
    match = EXPERIENCE_ASK.match(said)
    if not match:
        return False
    rest = said[match.end():].split()
    if not rest:
        return False
    if set(rest) & THEIR_PROBLEM:
        return False
    return all(word in EXPERIENCE_WORDS or word in BOT_LIFE or word in BOT_LIFE_FILLER
               for word in rest)


# "Have you ever ..." put to the bot. The past tense only: "do you ever get tired" asks how the
# bot is now, which has its own reading and its own answer. The courtesy in front of the ask is
# allowed, and so is a leading conjunction, because people keep talking in one breath. Nothing
# that says what the line is about is allowed in front of the ask: "my nan asked have you ever
# been to spain" is a line about the nan.
EXPERIENCE_ASK = re.compile(r"""^(?:(?:and|so|but|oh|well|ok|okay|right|hey|hi|yeah|actually|
honestly|just)\s+)*(?:have|has|did|were|was)\s+(?:you|u|ya)\s+(?:ever|once)\b""",
    re.VERBOSE)


# The words a life is described with: what was done and how it felt. Nothing here names a thing
# the bot could be asked about, so a line made of these is about the bot itself.
EXPERIENCE_WORDS = frozenset("""
been be being was were had have got get went gone go going done do did seen see saw felt feel
tried try made make met meet ate eaten eat drank drunk smoked ridden rode driven drove worn wore
lived live cry cried laugh laughed hurt love loved hate hated kiss kissed miss missed win won lose
lost give gave given giving keep kept run ran swim swam cook cooked
up down through ill sick unwell happy sad tired lonely scared frightened angry upset worried
glad proud bored excited drunk lost
day days night nights week weeks month months year years time times life lived world holiday
holidays
thing things something anything nothing one ones kind sort bit lot lots
it them that this these those there before once ever really actually
myself yourself
""".split())


# A problem of theirs in the hand: the line is about the thing, and the module that knows the
# thing answers it. A "like that" after the ask is not this country - "have you ever had a day
# like that" is small talk about the day, not a fault.
THEIR_PROBLEM = frozenset("""
my our me us mine ours happen happens happened occurring seems broken broke leaking dripping noisy
""".split())


# "what's it like being you" asks what it is like to be the bot - no day, no dinner, no family -
# and the honest answer is the one that says what the bot is. Read as an ordinary question it
# reached the search hedge, which is no answer at all to a question about itself.
# The words that make "your" a question about the bot's family rather than about a thing: "were
# your parents there", "were your parents at the wedding", "are your gran and grandad coming". The
# all-words gate in `_asks_about_its_own_life` cannot carry these, because the wedding and the
# hospital name the world and would take the line out of the bot's own vocabulary - while the
# answer is the same one either way, that there is no family to have been anywhere. A kin word
# straight after "your" is enough on its own; "was your car in the garage" is not kin and keeps
# the gate.
KIN = frozenset("""family families kid kids child children son daughter mum mom mother father dad
    daddy parents parent brother brothers sister sisters sibling siblings gran grans grandma
    grandmas grandad grandads grandpa grandparents grandparent uncle uncles aunt aunts auntie
    aunties cousin cousins niece nephews relatives relative partner husband wife girlfriend
    boyfriend""".split())


# The same ask with an auxiliary or a follow-up in front of it: "do your parents live near you"
# (the ask is a life of its own, not "were your parents there"), "what about your sisters", "and
# your brother". The kin word still has to be the word straight after "your", so "do your prices
# include vat", "did your delivery arrive" and "and your car insurance" keep their own reading.
A_YOUR_KIN = re.compile(
    r"\b(?:"
    r"(?:was|were|are|is)\s+(?:your|ur|yours)\s+(?:" + "|".join(sorted(KIN)) + r")"
    r"|(?:do|does|did|have|has)\s+(?:your|ur)\s+(?:" + "|".join(sorted(KIN)) + r")"
    r")\b")


# "what about your job", "how about your dog", "and your bills": the ask about the bot's own life
# said as a follow-up, with no verb at all. Every word a life like that is described with counts
# here (not only kin), because the thing named is the bot's own - there is no job, no dog and no
# bill on this side - and the answer is the same one. It has to be "your" straight after the
# follow-up, so "what about your interview" and "how about your neighbour's dog" keep theirs.
A_YOUR_OWN_THING = re.compile(
    r"\b(?:(?:what|how)\s+about|and)\s+(?:your|ur)\s+(?:"
    + "|".join(sorted(BOT_LIFE)) + r")(?:\s+(?:too|then|either|as\s+well))?\s*[?.!]*$")


# "how many brothers have you got", "how many kids do you have": the same ask about the bot's own
# life with a count in front of it. The shape in BOT_LIFE_ASK has the person word after the verb,
# so a count in front ("how many brothers have you got") matches nothing and the line reached the
# search hedge - a search cannot say how many brothers the bot has, and the answer is none.
A_HOW_MANY_OF_THE_BOTS_OWN = re.compile(
    r"\b(?:how|what)\s+many\s+\w+(?:\s+\w+)?\s+(?:have|has|do|does)\s+(?:you|u|ya)\b")


A_WHAT_ITS_LIKE = re.compile(r"\b(?:what|whats|what's)\b.*\blike\s+being\s+(?:you|u|ya)\b")


def _asks_about_its_own_life(norm):
    """True when the line asks about the bot's own life and names nothing of the world.

    "do you have kids", "have you got a pet", "what's your job", "do you get paid": the subject
    is the bot and the thing asked about is one a program does not have, so there is nothing in
    the world to look up and a search hedge is no answer. Every word has to be a thing of that
    kind, so a line that names anything else is left alone.
    """
    words = list(norm)
    if not words or not {"you", "u", "ya", "your", "ur", "yours", "yourself"} & set(words):
        return False
    match = BOT_LIFE_ASK.match(" ".join(words))
    if not match:
        return False
    rest = " ".join(words)[match.end():].split()
    if not rest or set(rest) - BOT_LIFE - BOT_LIFE_FILLER:
        return False
    return bool(set(rest) & BOT_LIFE)


# A line can open on "and" and still be the same question ("and who made you"). The one place
# that matters is the maker question: the reply that names the bot's maker is picked by the
# phrase at the start of the line, so an opening "and" takes that answer away and leaves the
# general "what are you" one. Only that shape is held back - "and do you sleep" keeps the
# answer it had either way, and a line that opens on any other conjunction is unchanged.
JOIN_OPENERS = frozenset("and".split())


# "how old is your boy" is a question about somebody else's child, not about the bot: a person
# word after a possessive names the person the line is about, so "your boy", "my girl" and
# "your son" take the line out of the bot's own vocabulary. The bot's own words ("are you a
# boy or a girl", "how old are you") carry no possessive and are read as before.
A_PERSON_AFTER_A_POSSESSIVE = frozenset("""boy girl son daughter child kid baby man woman
    brother sister mum mom dad mother father friend wife husband partner""".split())


# "do you learn from me" is about what the bot keeps from one chat to the next, and the honest
# answer to it is the memory one ("nothing carries over"), so a line that says the bot takes
# something *from* the person is left to the module that knows. The words that ask it are small.
LEARNING_WORDS = frozenset("""learn learns learnt learned learning remember remembers
    remembered recall recalls forget forgets pick picks take takes keep keeps""".split())


# "do you have a boy or a girl" asks about a child of the person's, not about the bot's sex:
# a person word after "have a" names somebody in the family. "are you a boy" and "are you a
# girl" have no "have" and are read as the bot's own words.
A_HAVING = frozenset("""have has had having got gets getting want wants wanted expecting
    trying planning""".split())


CHILD_NOUNS = frozenset("""boy girl son daughter child kid kids baby babies twins""".split())


POSSESSIVE_WORDS = frozenset("your my our his her their".split())


MAKER_WORDS = frozenset("made make makes making created create built build built trained "
                        "programmed program designed wrote written".split())


def _the_bots_own_not(norm, i):
    """True when the "not" at this position is the bot's own negative, not a clause's.

    Three places it stands at: right after the bot ("youre not chatgpt", "are you not real",
    "you not being real is fine"), right before it because a contraction carries the not in
    front of the subject ("cant you sleep", "didnt you understand me"), and after a subject
    that came first ("you cant sleep" is "you can not sleep"). The last one is only read that
    way when nothing opens a clause of the line's own in front of it, because "what do you do
    when you cant sleep" is a question about the night and the bot in it is the person.
    """
    if i + 1 < len(norm) and norm[i + 1] in NOT_BEFORE_THE_BOT:
        return True
    if i >= 1 and norm[i - 1] in NOT_AFTER_THE_BOT:
        return True
    if (i >= 2 and norm[i - 2] in NOT_BEFORE_THE_BOT and norm[i - 1] in NOT_AUX
            and (i < 3 or norm[i - 3] not in CLAUSE_OPENERS)):
        return True
    return False


# "what did i just tell you", "what have i said about my mum", "what did i ask you": the person
# is the one who said it, and the bot is who they said it to, so the line is about the chat and
# not about the bot.
_I_SAID_IT = re.compile(
    r"^\W*(?:(?:and|but|so|ok|okay|right|now|then|wait)[,. ]+)*"
    r"(?:what|which|when|where)\b[^.?!]*?\bi\b[^.?!]*?"
    r"\b(?:said|say|told|tell|mentioned|mention|asked|ask)\b", re.I)


def _recalls_their_own_line(norm):
    """True when the line asks for something the person themselves said."""
    return bool(_I_SAID_IT.match(" ".join(str(word) for word in norm if word)))


def _self_ask(norm):
    """True when the whole line is a question about the bot and names nothing else.

    "do you have hobbies", "who made you", "what should i call you" qualify. "how do you spell
    necessary" and "what can you do with leftover rice" do not, because a word outside the
    bot's own vocabulary is in the line, so the topic keeps them.
    """
    words = set(norm)
    if not words or not words & {"you", "your", "yourself", "yours"}:
        return False
    if not words & SELF_ASK:
        return False
    if _a_person_they_like(norm) or _a_thing_they_own(norm):
        return False
    if norm and norm[0] in JOIN_OPENERS and words & MAKER_WORDS:
        return False      # "and who made you" is the maker question, not the identity one
    if any(norm[i] in POSSESSIVE_WORDS and norm[i + 1] in A_PERSON_AFTER_A_POSSESSIVE
           for i in range(len(norm) - 1)):
        return False      # "how old is your boy" is about a child, not about the bot
    if any(norm[i] in LEARNING_WORDS and norm[i + 1] == "from" for i in range(len(norm) - 1)):
        return False      # "do you learn from me" asks what the bot keeps, not what it is
    if set(norm) & A_HAVING and set(norm) & CHILD_NOUNS:
        return False      # "do you have a boy or a girl" asks about a child, not the bot
    left = words - SELF_WORDS - SELF_FILLER - {"you", "your", "yourself", "yours"}
    if "not" in words:
        # Right after the bot it is the bot's own negative ("youre not chatgpt"). Behind another
        # verb it opens a clause about something else, and that clause is the line's subject.
        if any(norm[i] == "not" and not _the_bots_own_not(norm, i)
               for i in range(1, len(norm))):
            return False
        left = left - {"not"}
    return not left


def _asks_if_the_bot_is_a_product(norm):
    """True for a yes/no ask that names an assistant product: "are you claude".

    "are you claude" asks whether there is a model under this, which is the "model" kind and not
    the "identity" one, so the answer that says there is no model keeps the turn. The same words
    as a statement ("so youre claude") say what the bot is, not what it is made of.
    """
    if len(norm) < 2 or len(norm) > PRODUCT_ASK_WORDS or norm[0] not in ("are", "is"):
        return False
    if set(norm) & ROBOT_WORDS:
        return False                      # "are you a bot", "are you real" keep the identity line
    tail = list(norm)
    while tail and tail[-1] in PRODUCT_ASK_TAIL:
        tail.pop()                        # "are you claude then", "is this really claude"
    return len(tail) > 1 and tail[-1] in ASSISTANT_NAMES


def _starts_with(words, phrases):
    bare = " ".join(words)
    return any(bare == p or bare.startswith(p + " ") for p in phrases)


# People put one interjection in front of a courtesy: "aw thanks", "oh cheers", "ahh thank you".
# The filler says nothing on its own, so the thanks is still the whole line and the reply is
# still "any time" rather than the nod the line was getting.
BEFORE_COURTESY = frozenset("aw aww ah ahh oh ohh ooh awe ha haha um umm er hmm".split())


def without_filler(norm):
    """This line with one interjection taken off the front, or the line itself."""
    if len(norm) > 1 and norm[0] in BEFORE_COURTESY:
        return norm[1:]
    return norm


# "thank you card", "thank you letter", "thanks message": the courtesy word is part of the
# name of a thing to write, and the line is about writing it, not about the bot's last answer.
COURTESY_THING = frozenset("""card cards letter letters message messages note notes mail
    email emails text texts speech poem poem story banner sign tag tags gift gifts present
    presents cake wine chocolates flowers box bag""".split())


def _a_thing_named_after_the_courtesy(norm):
    """True when the courtesy word is the first half of a thing's name: "thank you card"."""
    rest = _after_thanks(norm)
    return bool(rest) and rest[0] in COURTESY_THING


def _after_thanks(norm):
    """The words left when a leading "thanks" is taken off, or None if it is not there."""
    for phrase in sorted(THANKS, key=len, reverse=True):
        words = phrase.split()
        if norm[:len(words)] == words:
            rest = norm[len(words):]
            if rest[:1] and rest[0] in COURTESY_THING:
                return None                     # "thank you card for a wedding present"
            return rest
    return None


def the_line_after_a_courtesy(norm):
    """The words a line goes on with after a leading "thanks", or None if it starts with one.

    A thank-you is often a wrapper round a line that still needs an answer ("thanks, my boss
    is a nightmare"), and the caller needs to see the line inside it.
    """
    return _after_thanks(without_filler(norm))


# A fault, a pain or a thing that has stopped working. After a courtesy opener one of these
# still needs an answer, so the thanks is a wrapper, not the whole line.
NEEDS_ANSWER = frozenset("""hurt hurts hurting hurt ache aches aching pain painful sore agony
    worse worst not never wont cant cannot dont doesnt didnt isnt arent wasnt weren kept
    killing killed
    keeps stopped stops broken broke breaks leaking leaks leak stuck died dead die rash
    swollen bleeding bled sick unwell slow noisy noise smells burning stings itches
    problem problems wrong stuck rubbish awful terrible worried worrying scared""".split())


# A symptom or an accident, which is the other way a person says something still needs an
# answer: "thanks, i have a headache" and "thanks, i slipped in the garden" are the same shape
# as the boiler, and the ache or the fall is the news, not the sign-off. The compound aches
# (headache, toothache, backache, earache, stomach ache) come from the ending rather than a
# list, because people make new ones ("eye ache") as they type. A fall is only an accident
# with a place to fall: "i fell asleep" and "i fell for it" say nothing is wrong.
STILL_WRONG = re.compile(r"""
    \b(?:
        (?!cache\b)\w*ache | fever(?:ish)? | cough(?:ing)? | dizzy | nauseous? | vomit(?:ing)?
      | shiver(?:s|ing|y)? | chills | dehydrat\w+
      | (?:have|has|had|got|gotten|running|caught|catch|my|his|her|their|your)
        \s+(?:an?\s+)?(?:high\s+|slight\s+|bit\s+of\s+a\s+|touch\s+of\s+a\s+)?temperature
    )\b
""", re.X)


# "temperature" is the oven's just as often, and a line about the oven says nothing is wrong:
# only a person who has one is ill ("thanks, i have a temperature"), so the illness word needs
# the person word in front of it, which is what the pattern above asks for.
#
# A fall names where it happened; finding something names what was found ("i stumbled on your
# blog"), and a forgotten thing is not a fall ("it slipped my mind"). So a slip or a stumble
# counts as an accident unless the words after it name a thing found rather than a place.
FOUND = frozenset("""blog article post page site website video photo picture recipe thread
    comment question quiz idea story podcast episode book film answer deal bargain
    mind""".split())


# The words that follow a slip when nothing was fallen over: something was come across, or a
# thing slipped out of place, and neither of those is an accident.
SLIPPED_FROM = frozenset("across upon into through by away past".split())


FALL = frozenset("fallen fainted".split())


# Every word a fall is said with, so a line that says one can be asked what kind of fall it was:
# "i fell asleep at nine" is not an accident and "i slipped in the garden" is.
FELL_WORDS = FALL | frozenset("""fell fall falls falling tripped tripping slipped slipping
    stumbled stumbling collapsed collapse""".split())


def _a_fall(rest):
    """Did the rest of the line say somebody fell, rather than found or forgot something?"""
    for index, word in enumerate(rest):
        if word in FALL or word.startswith("collaps"):
            return True
        if word == "fell":
            after = rest[index + 1] if index + 1 < len(rest) else ""
            if after not in ("asleep", "for", "into", "in", "behind", "out"):
                return True
            continue
        if word in ("tripped", "slipped", "slipping", "stumbled", "stumbling"):
            after = rest[index + 1:index + 7]
            if after[:1] and after[0] in SLIPPED_FROM:
                continue                       # "i stumbled across a great recipe"
            if [one for one in after if one in FOUND]:
                continue                       # "i stumbled on your blog", "it slipped my mind"
            return True
    return False


# Words a greeting can carry without saying anything else: "hi there", "morning all",
# "hey, quick question", "hiya, hope you are well".
GREETING_TAIL = frozenset("""there again all folks friends everyone everybody guys you your
    mate quick question hope hopes hoping doing day today going well good thanks thank then
    too also just so how are is it things up sup life ok okay alright fine here back""".split())


# How a line gives its own name: "hi, I'm Sam", "good morning, my name is Priya".
INTRODUCES = (("my", "name", "is"), ("the", "name", "is"), ("i", "am"), ("im",),
              ("call", "me"), ("this", "is"), ("its",))


def _after_greeting(norm):
    """The words left when a leading greeting is taken off, or None if there is not one."""
    for phrase in sorted(GREETINGS, key=len, reverse=True):
        words = phrase.split()
        if norm[:len(words)] == words:
            return norm[len(words):]
    return None


def after_greeting(norm):
    """The words a line says after a leading hello, or None when it opens with none.

    For the readers that answer what a line says rather than how it opens: "hi, I'm
    vegetarian" says the diet and the hello only opens it, and a module that can answer the
    diet needs the rest of the words.
    """
    return _after_greeting(list(norm or []))


# Words that only fill out a goodbye, so a line made of them and a farewell is still just the
# goodbye: "night night", "bye everyone", "right then, good night". Nothing that names its own
# subject is here - "night feeds are killing me" is a line about the feeds, not a goodnight.
FAREWELL_TAIL = frozenset("""then ok okay right well so all everyone everybody guys folks mates
    now for to soon later tomorrow tonight night good xx xxx love hun""".split())


# "night then, thanks" is still a goodnight: the words a goodbye is said with and nothing else.
_SAID_ON_ITS_OWN = frozenset(
    [word for phrase in THANKS + FAREWELLS for word in phrase.split()])


_THANKS_WORDS = frozenset([word for phrase in THANKS for word in phrase.split()])


# A goodnight is often said with a wish for the night in front of it: "night night, sleep well".
_NIGHT_WISHES = ("sleep well", "sleep tight", "sleep good", "sweet dreams", "rest well",
                 "night night")


_WISH_WORDS = frozenset(" ".join(_NIGHT_WISHES).split())


def _after_farewell(norm):
    """The words left when a leading farewell is taken off, or None if there is not one."""
    for phrase in sorted(FAREWELLS, key=len, reverse=True):
        words = phrase.split()
        if norm[:len(words)] == words:
            return norm[len(words):]
    return None


def farewell_only(norm):
    """True when the line is a goodbye, not a goodbye wrapped round something to answer.

    A farewell word is an ordinary word in its own right - "night" is when the baby wakes,
    "later" is when something happens, "care" is what a nurse gives - so the goodbye has to be
    the whole line. "night night", "good night all" and "see you tomorrow" are goodbyes; "night
    feeds are killing me", "night shift this week", "good night routine for a baby" and "take
    care of your mum" are lines about something, and the answer belongs to what they say.
    """
    rest = _after_farewell(norm)
    if rest is None:
        return False
    if set(rest) & NEEDS_ANSWER:
        return False
    left = [word for word in rest if word not in _WISH_WORDS]
    if len(left) < len(rest) and all(word in FAREWELL_TAIL or word in POLITE for word in left):
        # "night night, sleep well" and "good night, sweet dreams" wish the night well on the way
        # out; a wish with anything else in it ("sleep well now the baby is older") is news.
        return True
    if rest and rest[0] in _THANKS_WORDS:
        # "bye, thanks for the help" says thank you on the way out, which is still the way out.
        return True
    # A goodbye is said to somebody: "bye love", "night pet", "ciao bella" and "bye duck" are
    # still the goodbye, and the name it is said to does not make it a line about them.
    return all(word in FAREWELL_TAIL or word in POLITE or word in _SAID_ON_ITS_OWN
               or word in TERMS_OF_ADDRESS for word in rest)


def greeting_only(norm):
    """True when the line is a hello, not a hello wrapped round something to answer.

    "hi", "morning all" and "hey, quick question" are greetings, and so is "hi, I'm Sam",
    which gives a name and nothing else. "hi, my boiler is leaking" is a report: the rest of
    the line decides the kind, because a hello-shaped answer to a leaking boiler is useless.
    """
    rest = _after_greeting(norm)
    if rest is None:
        return False
    if all(word in GREETING_TAIL or word in POLITE for word in rest):
        return True
    # A greeting with two words of small talk after it is still a greeting: "Morning! Finally
    # Friday." Nothing that hurts or has stopped working counts, so "hi it hurts" is not one,
    # and neither does anything that says what the person is or has ("hi, im vegetarian", "hi,
    # im diabetic", "hi, im 34"): those two words are the whole of the line, and the hello is
    # only how it opens.
    if len(rest) <= 2 and not set(rest) & NEEDS_ANSWER \
            and not _says_what_they_are(rest):
        return True
    for lead in INTRODUCES:
        if tuple(rest[:len(lead)]) != lead:
            continue
        # "hi, I'm called Sam" names the person in the same words as the store's own name
        # reading, and the naming word is not part of the name.
        tail = [word for word in rest[len(lead):] if word not in NAMING_WORDS]
        # A name is the whole of what is left, and a line that goes on to ask something is
        # not a greeting: "hi, I'm Sam, my boiler is leaking" needs the boiler answered.
        if not 1 <= len(tail) <= 2:
            return False
        # Whether the word after "I'm" is a name is the fact store's reading, because it is the
        # only reading that can tell "hi, I'm Sam" from "hi, I'm a nurse" and "hi, I'm
        # vegetarian". Counting any short tail as a name read every hello in front of what the
        # person is as a greeting, and the only answer left was "what would you like to talk
        # about?"
        return all(_a_name(word) for word in tail)
    return False


# The words a name is given with, which are not part of it: "hi, I'm called Sam".
NAMING_WORDS = frozenset(("called", "named", "name", "names"))


def _says_what_they_are(rest):
    """Whether the words after a hello say what the person is, has or does.

    A hello with a name after it is a greeting ("hi, I'm Sam"), and the same hello with a fact
    after it is a person telling you the fact ("hi, I'm vegetarian", "hi, im diabetic"): the
    words are the whole of the line in the second, and the hello is only how it opens. Which
    one it is, is the fact store's reading (`facts.about_themselves`) - the only reading that
    can tell a name from a fact about the person - and it is the same question the store asks
    before it says the fact back (`bot/memory/ack.py`). Imported here because the fact store
    reads this module.
    """
    from ..memory.facts import about_themselves
    return bool(about_themselves(" ".join(rest)))


def _a_name(word):
    """Whether a word said after "I'm" is a name: "hi, I'm Sam" against "hi, I'm a nurse"."""
    from ..memory.facts import reads_as_a_name
    return bool(reads_as_a_name(word))


# A line that says the help was good without using a thanks word: "that helps", "ok that helps",
# "that really helps", "that helped a lot", "thats helpful". The person is closing the turn on
# the answer just given, so the line is a thank-you for the same reason "thanks" is: there is
# nothing in it left to answer, and the topic the conversation is on must not pull it back to
# the entry that was just read. Only a whole line counts, so "what helps a headache" and
# "that helps my back" keep their own answer.
HELP_WAS_GOOD = frozenset((
    "that helps", "this helps",
    "that really helps", "this really helps",
    "that helps a lot", "that helps loads", "that helps so much",
    "that helped", "this helped",
    "that really helped", "this really helped",
    "that helped a lot", "that helped loads", "that helped so much",
    "thats helpful", "that is helpful", "that was helpful",
    "this is helpful", "this was helpful",
))


# The agreement in front of a praise says nothing and does not stop it being one.
BEFORE_HELP_WAS_GOOD = frozenset("ok okay yeah yep yes ah oh right cool so".split())


# The softener after the praise says nothing either: "that helps actually", "that really helps
# tbh", "that helped a lot honestly". Read without it the line said the help was good, and a
# softener is not news: it was read as a statement about nothing, and answered with the filler
# "Got it. Is there anything you'd like a hand with?" right after the person said it worked.
AFTER_HELP_WAS_GOOD = frozenset("""actually tbh honestly really though tho anyway now then
    mind cheers thanks""".split())


# A softener the chat table spells out in full: "tbh" is read as "to be honest", so the tail is
# three words rather than one and the words have to come off together.
AFTER_HELP_WAS_GOOD_SAID_OUT = ("to be honest", "to be fair", "if im honest", "if i am honest",
                                "in all honesty", "to tell the truth")


def _says_the_help_was_good(norm):
    """True when the whole line says the last answer helped, without a thanks word."""
    words = list(norm)
    while len(words) > 2 and words[0] in BEFORE_HELP_WAS_GOOD:
        words = words[1:]
    while len(words) > 2:
        said = " ".join(words)
        tail = next((phrase.split() for phrase in AFTER_HELP_WAS_GOOD_SAID_OUT
                     if said.endswith(" " + phrase)), None)
        if tail is None and words[-1] in AFTER_HELP_WAS_GOOD:
            tail = [words[-1]]
        if tail is None or len(words) - len(tail) < 2:
            break
        words = words[:-len(tail)]
    return " ".join(words) in HELP_WAS_GOOD


def _thanks_only(norm, clauses=None):
    """True when "thanks" is the whole line, not a wrapper round a problem.

    "thanks, that worked" and "thanks for staying with me" are thanks; "thanks, my boiler
    keeps losing pressure" reports a fault, and the answer belongs to the boiler, so the
    rest of the line decides the kind.
    """
    rest = _after_thanks(norm)
    if rest is None:
        return False
    if set(rest) & NEEDS_ANSWER:
        return False
    if STILL_WRONG.search(" ".join(rest)):
        return False
    if _a_clause_of_its_own(rest, clauses):
        return False
    return not _a_fall(rest)


# What a thank-you is about, so words that open with one are still part of it: "thanks, that
# worked", "thank you, this helps".
THANKS_ABOUT = frozenset("that this it they them those these which".split())


# News that things are better is a thank-you with the news on it, not a new subject: "thanks,
# i feel much better now", "thanks, the pain has gone".
BETTER = frozenset("""better best glad happy pleased relieved easier lighter improved gone
    tried try trying worked works""".split())


# A thank-you said on the way out is still a thank-you: "thanks, im off to bed", "cheers, i'm
# going to turn in". Nothing in it needs an answer.
# A thank-you that says something about the person being thanked is still a thank-you: "thanks,
# i owe you one", "thanks, you're a star".
SAYS_ABOUT_YOU = frozenset("you your yours u ya".split())


# A compliment about the thing the bot helped with is still part of the thank-you: "thanks, the
# oven temperature was perfect", "thanks, the cake was delicious". The person is closing the turn
# on a good note and there is nothing in it to answer.
PRAISING = frozenset("""perfect great brilliant lovely delicious gorgeous superb spot amazing
    excellent wonderful nice good marvellous marvelous fantastic smashing""".split())


# Praise said with a verb rather than an adjective, which is how people report back on advice
# that worked: "thanks, my son loved it", "cheers, the kids enjoyed it", "thanks, it went down
# well". The thing was good, and there is nothing left to answer.
PRAISING_VERB = frozenset("""loved love loves liked like likes enjoyed enjoy enjoys adored
    devoured demolished wolfed""".split())


# The same praise said as a phrase: "cheers, the stew went down well", "it went down a treat".
PRAISE_SAID = re.compile(r"\b(?:went|gone)\s+down\s+(?:well|a\s+treat|great|nicely)\b")


# A thing praised and then complained about in the same breath is the complaint.
TURNED_ROUND = frozenset("but though although except however".split())


# A thank-you reporting a step of the advice that the person has just done is still a
# thank-you: "thanks, i cleared the cache", "cheers, i restarted the router", "thanks, i put
# it on charge". They did what the bot said and came back to say so, and the answer to the
# turn before is the answer they wanted.
STEP_VERBS = frozenset("""cleared restarted rebooted reinstalled uninstalled deleted removed
    emptied cleaned washed rinsed changed swapped reset updated charged plugged poured soaked
    drained defrosted tried gave followed did put set""".split())


# The step verbs that take almost any object, so that the object cannot tell a step from an
# accident: "i put my back out", "i gave my notice in", "i did my back in", "i changed my mind".
STEP_ANY_OBJECT = frozenset("put set did gave changed".split())


# A step reported as having gone wrong is not a thank-you any more: "thanks, i cleared the
# cache but it is no better", "thanks, i booked the wrong day".
STEP_WRONG = frozenset("""wrong mistake error errors failed fails broken broke wont cant
    stopped worse nothing none no not still again""".split())


SIGNING_OFF = re.compile(r"""
    \b(?:i'?m|im|i\s+am|we'?re|were|we\s+are)\s+(?:off|away|going|turning\s+in|heading)\b
    | \b(?:good\s*night|goodnight|bedtime|off\s+to\s+bed|turning\s+in)\b
    | \bnothing\s+(?:else|more|left)\b | \bnothing\s+to\s+do\b
    """, re.X)


def _a_clause_of_its_own(rest, clauses=None):
    """True when the rest of a line that opens with a thank-you says something of its own.

    A thank-you at the front of a line is a wrapper round what follows it, and what follows it
    is often the point: "cheers, im skint till friday" is news about the week, and read as a
    thank-you it was answered with the answer to the turn before, all over again. The
    thank-you does hold what comes after it when that is short ("thanks, it worked"), opens
    with what the thanks is about ("thanks, that explains the boiler"), is agreement ("thanks,
    that worked a treat"), or says things are better ("thanks, i feel much better now"). A
    clause of four words or more that does none of those is the line, and the line needs an
    answer.
    """
    if not rest or rest[0] in THANKS_ABOUT:
        return False
    if _starts_with(rest, THANKS):
        return False      # "much appreciated, thanks for the tips" is two thank-yous in a row
    if len(rest) < 4:
        return False
    if _a_step_done(rest):
        # A step of the advice done and reported back is still a thank-you; one that did not
        # work is the news: "thanks, i cleared the cache but it is no better".
        return _the_step_went_wrong(rest)
    if _agrees(rest) or set(rest) & BETTER:
        return False
    if _praises_the_thing(rest):
        return False      # "thanks, the cake was delicious"
    if set(rest) & SAYS_ABOUT_YOU:
        return False      # "thanks, i owe you one", "thanks, you're a star"
    if _a_fall_that_is_not_one(rest):
        return False      # "thanks, i fell asleep at nine", "thanks, i fell for it"
    if "temperature" in rest:
        # STILL_WRONG has already ruled out a person with one, so this is the oven's: "thanks, i
        # need a higher temperature" is how the baking went, not news.
        return False
    if SIGNING_OFF.search(" ".join(rest)):
        return False
    for clause in (clauses or [])[1:]:
        if len(clause) >= 4 and clause[0] not in THANKS_ABOUT:
            return True
    return False


def _a_step_done(rest):
    """True when the rest of the line reports doing a step of the advice, and nothing went wrong.

    "thanks, i cleared the cache" and "cheers, i restarted the router" are the person saying they
    did what the bot suggested. The step is named as a thing being acted on ("the", "my", "it"),
    so a line about the person's own day keeps its own answer: "thanks, i booked a table for
    friday" is still news, and "thanks, i tried the new place on saturday" is a thing they did
    rather than a report back. A step that went wrong is the news, not the thank-you.
    """
    if len(rest) < 3 or rest[0] not in ("i", "we"):
        return False
    if rest[1] not in STEP_VERBS and not (rest[1] == "gave" and "go" in rest[2:4]):
        return False
    after = rest[2:]
    if rest[1] in ("tried", "swapped"):
        # "i tried the new place on saturday" is a thing they did, not a report back on advice.
        return after[:1] == ["it"]
    if rest[1] in STEP_ANY_OBJECT and after[:1] not in (["it"], ["the"]):
        # A step verb takes almost any object, so "the"/"my" alone made an accident read as a
        # report back: "thanks, i put my back out" is the state the person ended up in, and a
        # person whose back has gone must not be told "no problem at all". What a step acts on is
        # what the bot named ("the cache") or "it"; "my" is how a thing of the person's own gets
        # named ("restarted my router"), and no verb that takes anything keeps it.
        return False
    return "the" in after or "my" in after or after[:1] == ["it"]


def _the_step_went_wrong(rest):
    """True when a step of the advice is reported as having failed."""
    return bool(set(rest[2:]) & STEP_WRONG)


def _a_fall_that_is_not_one(rest):
    """True when the rest names a fall that is not one, so it stays part of the thank-you.

    "thanks, i fell asleep at nine" and "thanks, i fell for it" say something went well; the
    words are the ones an accident uses, and an accident is what makes the line news, so the
    rest of the line has to say what kind of fall it was. _a_fall already tells those two from
    "thanks, i slipped in the garden".
    """
    if not set(rest) & FELL_WORDS:
        return False
    return not _a_fall(rest)


def _praises_the_thing(rest):
    """True when what follows the thank-you is a compliment about a thing, not news of its own.

    "thanks, the oven temperature was perfect" and "thanks, the cake was delicious" praise the
    thing the bot helped with and need no answer, so the thank-you still holds the line. Praise
    said of the speaker ("thanks, im good now") is a thank-you too. A thing praised and then
    complained about in the same breath is the complaint: "the meal was good but the service was
    slow".
    """
    if not (set(rest) & (PRAISING | PRAISING_VERB) or PRAISE_SAID.search(" ".join(rest))):
        return False
    return not set(rest) & TURNED_ROUND


# The words people put in front of a "thanks" as they answer the bot: "pretty good thanks",
# "that helps a lot thanks", "not bad ta". A line ending in thanks counts as thanks when
# everything before it is one of these, so a line that also reports something keeps its kind
# ("the flat is freezing thanks" is still news about the flat).
AGREE_TAIL = frozenset("""it that this these those all so much very quite a an lot bit really
    pretty good great fine nice cool ok okay lovely brilliant magic perfect spot better best
    well helps helped works worked working doing do does is was been am are you your not no
    too to and now enough still same here there just also then
    love loved loving like liked liking righto alright ace grand decent pleased glad happy
    kind kindest thoughtful generous sweet
    one ones of""".split()) | AFFIRM


# "not bad" and "not too bad" are agreement; "bad" on its own is not, so it only counts
# in a line that also says "not".
AGREE_AFTER_NOT = frozenset("bad half wrong shabby".split())


# After "not", these words are skipped before the word that decides: "not too bad thanks",
# "not that good thanks".
NOT_FILLER = frozenset("too that so very much all quite a an to even really feeling".split())


# The noise a person writes in front of a thank you. It says nothing about the line, and it is
# not an agreement either: "oh thanks" is a thank you with a sound in front of it, where
# "sounds good thanks" is an answer. Read as an agreement, "oh thanks" and "ah thanks" were
# answered "Fair enough." - a shrug at the offer - instead of "No problem at all.".
THANKS_NOISE = frozenset("oh ah aha aah ahh ohh ooh aw aww mm mmm".split())


# The name a short line is said to, at the end of it: "thanks love", "thanks pet", "cheers
# duck", "morning hen". It names the person being spoken to, not a feeling and not a thing the
# line is about, so the line is the thank you (or the hello) with a name after it. Read as a
# word of its own, "love" made "thanks love" a good feeling, and the thank you behind it was
# answered "Fair enough.".
ADDRESSED = frozenset("""love mate pet hun duck sunshine hen flower chuck dear pal buddy
    babes shug lovey""".split())


def _agrees(rest):
    """Whether every word before the thanks is agreement, so the thanks is the whole answer.

    "not" is the hard part: "not bad thanks" agrees, and "still not working thanks" does not,
    because the person has just told you their thing is still broken. So what follows "not" is
    the word that decides.
    """
    if "not" not in rest:
        return all(word in AGREE_TAIL for word in rest)
    after = rest[rest.index("not") + 1:]
    while after and after[0] in NOT_FILLER:
        after = after[1:]
    if not (after and after[0] in AGREE_AFTER_NOT):
        return False
    return all(word in AGREE_TAIL or word in AGREE_AFTER_NOT for word in after)


def _ends_with_thanks(norm):
    """True when a short line ends in thanks: "pretty good thanks", "brilliant thanks".

    People answer the bot and thank it in one breath, and the tail is the whole point of the
    line: "loving it thanks" is thanks, not news.
    """
    # A name at the end is the person the line is said to, not part of what it says, so the
    # thank you is looked for in front of it: "thanks pet", "oh thanks love".
    said_to = len(norm)
    while said_to and norm[said_to - 1] in ADDRESSED:
        said_to -= 1
    line = norm[:said_to]
    named = said_to < len(norm)
    for phrase in sorted(THANKS, key=len, reverse=True):
        words = phrase.split()
        if len(line) > len(words) and line[-len(words):] == words:
            # The noise in front of a thank you is not part of it either, and a line with
            # nothing else in it is the thank you itself: "oh thanks", "mm thanks".
            rest = [word for word in line[:-len(words)] if word not in THANKS_NOISE]
            if not rest:
                return True
            if len(rest) > 6:
                continue
            if set(rest) <= (AFFIRM | ACK) and not named:
                continue      # "sounds good thanks" is already an answer: leave it an ack
            if rest[:1] and rest[0] in {"no", "nope", "nah", "never", "naw"}:
                continue      # "no thanks" is a refusal, and the refusal is the point
            if not _agrees(rest):
                continue      # "still not working thanks" is a fault, not a thank-you
            return True
    return False


# A line that says a question is coming, or asks for help without saying what with: "can i ask
# you something", "i have a question", "i need some advice", "can you help me with something".
# Nothing in it can be answered yet, so it is not a question about the world; the reply is to
# invite them to go on. Every word has to be part of the frame, so "can i ask you something
# about my boiler" stays a boiler question.
OPENING_FRAME = re.compile(r"""
    \b(?:can|could|may|might)\s+i\s+ask\s+(?:you\s+)?(?:something|somethin|a\s+question|one\s+thing|advice|for\s+advice|your\s+advice)\b
  | \b(?:i|ive)?\s*(?:have|got|has)\s+(?:a\s+|one\s+|quick\s+)?question\b
  | \bquick\s+question\b
  | \b(?:i|we)\s+(?:need|want|would\s+like|could\s+use)\s+(?:(?:some|a\s+bit\s+of)\s+)?(?:your\s+)?advice\b
  | \b(?:can|could|would|will)\s+you\s+help\s+me\s+(?:with\s+something|with\s+a\s+thing|with\s+one\s+thing|out\s+with\s+something)\b
  | \bmind\s+if\s+i\s+ask\s+(?:you\s+)?(?:something|a\s+question)\b
  | \bi\s+(?:want|need)\s+to\s+ask\s+you\s+(?:something|a\s+question)\b
""", re.X)


OPENING_WORDS = frozenset("""can could may might i ask you something somethin a one thing
    question quick have got has ive we need want would like use some bit of for your advice
    help me with out will to if mind is it""".split())


OPENING_MAX = 9


# The other thing people say before they say anything: they want to talk, or to get something
# off their chest. It is the same reading as a question that is coming - nothing in it can be
# answered yet, so the reply is to make it easy to go on - and the same guard: the whole line
# has to be the frame, so "i need to talk to my sister" and "i want to vent about work" keep
# the person and the subject they name.
# The talk words people use for the same ask. "vent" and "rant" are the loud ones; a whinge, a
# grumble and an offload are the same request to be listened to, and they were answered as
# questions about the world ("What kind of whinge do you usually go for?").
TALK_ASK_VERBS = r"(?:vent|rant|moan|whinge|grumble|offload|unload)"


# What the ask may say after the verb and still be the whole line: "can i vent about it",
# "can i talk about this" ("can i talk about it" was read as the speech-therapy question),
# "can i have a moan here", "i need to talk first".
TALK_TAIL_WORDS = (r"(?:\s+(?:a\s+bit|a\s+minute|a\s+sec|a\s+moment|one\s+thing|"
                   r"for\s+a\s+minute|for\s+a\s+bit|about\s+something|about\s+it|"
                   r"about\s+this|to\s+you|to\s+someone|on\s+you|here|first))*")


# How a person asks leave to do any of it: the permission ask, with the person in it.
TALK_ASK_OPENERS = (r"(?:(?:can|could|may)\s+(?:i|we)|do\s+you\s+mind\s+if\s+i|"
                    r"would\s+you\s+mind\s+if\s+i|is\s+it\s+ok\s+if\s+i|"
                    r"is\s+it\s+okay\s+if\s+i)")


TALK_OPENING = re.compile("|".join((
    # "i just want to vent", "im going to vent", "we need a moan"
    r"(?:i\s+|we\s+)?(?:just\s+|really\s+|honestly\s+|properly\s+)?(?:am\s+|are\s+)?"
    r"(?:(?:want|wanna|need|have|got|gotta|planning|going|gonna)\s+)?(?:to\s+)?"
    + TALK_ASK_VERBS + TALK_TAIL_WORDS,
    # "can i rant", "could we have a moan"
    r"(?:can|could|may)\s+(?:i|we)\s+(?:just\s+)?(?:have\s+a\s+)?" + TALK_ASK_VERBS
    + TALK_TAIL_WORDS,
    # "im going to have a proper rant", "i need a rant", "a quick moan"
    r"(?:i\s+|we\s+)?(?:just\s+)?(?:am\s+|are\s+)?(?:going\s+to\s+|gonna\s+)?"
    r"(?:(?:want|wanna|need|have|got|gotta)\s+(?:to\s+)?)?(?:have\s+)?a\s+"
    r"(?:proper\s+|good\s+|quick\s+|little\s+)?(?:vent|rant|moan|whinge|grumble)"
    + TALK_TAIL_WORDS,
    # "i need to get something off my chest", "can i get this off my chest"
    r"(?:i\s+)?(?:just\s+)?(?:(?:want|wanna|need|have|got|gotta)\s+(?:to\s+)?"
    r"|(?:can|could|may)\s+i\s+|let\s+me\s+)(?:get\s+)?"
    r"(?:something|somethin|this|it)\s+off\s+my\s+chest",
    # "i need to talk", "i want to talk to you about something", "we should talk"
    r"(?:i\s+|we\s+)?(?:just\s+|really\s+)?(?:am\s+|are\s+)?"
    r"(?:(?:want|wanna|need|have|got|gotta|going)\s+(?:to\s+)?"
    r"|(?:can|could|may)\s+(?:i|we)\s+)"
    r"talk" + TALK_TAIL_WORDS,
    # "i need someone to talk to"
    r"(?:i\s+)?(?:need|want|would\s+like)\s+"
    r"(?:someone|somebody|anyone|anybody)\s+to\s+talk\s+to",
    # "can i have a word", "i need a word"
    #
    # Saying something is coming is not the same as asking for room to say it, and the lines
    # below are left to the card that already answers them well: "i have something to tell you"
    # and "can i tell you something" get "Of course. Take your time.", and "got something on my
    # mind" gets "Going round it that many times is exhausting. Say it out to me - what keeps
    # coming back?". Read as an opener, all three got "Ask away, I'm listening. What's going
    # on?" instead, which asks a question in the same breath as giving room - the one thing a
    # person about to say something hard does not need. They are also the lines where the
    # person has already decided to speak, so there is nothing to make easier.
    r"(?:can|could|may)\s+i\s+(?:have\s+a\s+word)",
    r"(?:i\s+)?(?:need|want)\s+a\s+word",
    # Asking for the bot's ear is the same ask with the same answer - "can i run something by
    # you" was a search hedge, "can i get a second opinion" said it would rather not guess -
    # and each phrase holds "you", so it cannot be about anything else.
    TALK_ASK_OPENERS + r"\s+"
    r"(?:run|bounce|try|talk\s+through)\s+"
    r"(?:something|somethin|this|that|it|an?\s+idea|one\s+thing|a\s+couple\s+of\s+things|"
    r"a\s+few\s+things|some\s+ideas?)\s+(?:by|past|off)\s+you" + TALK_TAIL_WORDS,
    TALK_ASK_OPENERS + r"\s+"
    r"(?:pick\s+your\s+brains?|bend\s+your\s+ear)" + TALK_TAIL_WORDS,
    TALK_ASK_OPENERS + r"\s+"
    r"(?:tell\s+you\s+what\s+happened|share\s+(?:something|this|it)\s+with\s+you|"
    r"have\s+a\s+second\s+opinion|get\s+a\s+second\s+opinion)" + TALK_TAIL_WORDS,
)))


# The line can be wrapped in a word that says nothing but that they are starting ("right, im
# going to vent", "ok so i need to get this off my chest") and end in one that only softens it
# ("... tbh", "... if that's ok"). Either side is taken off before the frame is matched, so the
# frame itself stays the whole line and a subject named in it is still a subject.
TALK_HEAD = frozenset("""right ok okay so look well honestly listen alright now then""".split())


TALK_TAIL = (("to", "be", "honest"), ("if", "that", "is", "ok"), ("if", "thats", "ok"),
             ("now",), ("please",), ("then",), ("thanks",), ("right",), ("actually",),
             ("quickly",), ("quick",), ("mate",))


def _talk_opening(text):
    """True when the whole line asks for room to talk, with nothing named yet in it."""
    words = text.split()
    changed = True
    while words and changed:
        changed = False
        if words[0] in TALK_HEAD:
            words, changed = words[1:], True
        for tail in TALK_TAIL:
            if len(words) > len(tail) + 1 and tuple(words[-len(tail):]) == tail:
                words, changed = words[:-len(tail)], True
                break
    return bool(words) and bool(TALK_OPENING.fullmatch(" ".join(words)))


def talk_frame(norm):
    """True when the whole line asks for room to talk and names nothing in it.

    `opening_line` uses this, and so does the reading: the frame is the whole line, so a word
    inside it ("run", "brain", "share") is not a subject, and an answer that matched one of them
    ("can i run something by you" found the fitness entry) is not an answer to this line.
    """
    text = " ".join(word for word in norm if word)
    return bool(text) and _talk_opening(text)
