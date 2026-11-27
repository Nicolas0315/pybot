"""Part 1 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re

from ..understanding import lexicon, normalize
from ..understanding.kinds import EMOTION_WORDS
from ..understanding.topics import STRONG, PHRASES, CONDITIONS




# A capitalised word right after "I'm" is a name ("I'm Jess"), but only when it is not one
# of the words people usually put there. The same list lets lower-case chat ("im tom") work.
NOT_NAMES = frozenset("""
a an the this that these those not no so really very quite just still also always already
only even now here there back home off out in on at up down over around about all both too
good bad great fine ok okay sure glad happy sad angry upset tired exhausted hungry thirsty bored
busy free late early lost done ready sorry afraid scared nervous worried stressed excited
confused lonely ill sick better worse old young new first second third next last single
married pregnant vegan vegetarian allergic serious interested trying looking thinking planning
coeliac celiac diabetic asthmatic epileptic anaemic anemic intolerant lactose gluten autistic
adhd menopausal perimenopausal pescatarian flexitarian veggie
going coming getting having making doing writing working learning studying cooking moving buying
playing watching reading listening talking speaking feeling letting taking giving waiting
hoping wondering asking saying telling checking shopping cleaning walking running driving
flying travelling traveling starting finishing meeting visiting staying living eating drinking
sleeping sitting standing paying spending saving booking ordering calling texting emailing
posting sharing using fixing building creating preparing practising practicing revising
training coaching organising organizing decorating painting gardening baking coming around
fine good well okay alright nearly almost definitely probably maybe perhaps honestly actually
literally seriously totally completely absolutely pretty rather kind sort bit little lot
off down out away along through until since while because though although whether
""".split())


# English makes a state out of a noun with a "y": sweat, sweaty; clam, clammy. The endings below
# cannot carry those, because "y" is the last letter of more names than any other one (emily,
# lucy, molly, kelly, daisy, holly), so no length makes the tail safe. They are listed with the
# other states instead, at the end of NOT_NAMES_EXTRA, and the list is the ones that are always
# somebody's state and never somebody's name: "im sweaty" was answered "Nice to meet you,
# Sweaty", and clammy, woozy, jittery, achey, queezy, muggy, bleary, puffy, giddy, edgy, antsy,
# twitchy, hangry, drowsy, buzzy, spacey, dopey, mopey, quivery, fidgety and sniffy were the
# same. `husky` is left out on purpose - it is a dog and a voice as well as a name.
# A lower-case word after "im" is only a name if it does not look like how people describe
# themselves: "im knackered" is a feeling, "hi im alex" is an introduction. The endings
# below are the ones English builds states and conditions with ("tired", "coeliac",
# "diabetic", "welsh", "pregnant"), each with the length a word needs before the ending
# counts more than the chance of it being a name, so "im lily" and "im eric" still work.
NAME_TAIL_MIN = {"ed": 5, "ing": 5, "ly": 6, "ous": 5, "ful": 6, "less": 6,
                 "ish": 4, "able": 6, "ible": 6, "ic": 5, "ac": 5, "ist": 6,
                 "ism": 6, "ese": 5, "ant": 6,
                 # -ive is how English makes a long condition or a mood: depressive,
                 # aggressive, sensitive, possessive. No name of six letters or more ends in it
                 # ("clive" and "steve" are five and keep their own reading), so six is safe:
                 # "im depressive" was answered "Nice to meet you, Depressive".
                 "ive": 6}


# -nt was tried and taken out again: unlike -ed or -ing it is the ending of real names as well
# ("im vincent", "im lamont"), and a name kept by mistake is worse than a state read as one. The
# states that end in it are listed in NOT_NAMES_EXTRA instead.
# The names that end like a state: "im dominic" is still an introduction, and so is "im
# isaac" (which ends in -ac like coeliac) and "im ahmed" (-ed like tired). The endings in
# NAME_TAIL_MIN carry the weight, so the names an ending would eat are listed here.
NAMES_THAT_LOOK_LIKE_STATES = frozenset("""
dominic dominick
isaac cedric frederic
ahmed mohamed muhammed jared
manish trish
kimberly
kay
""".split())


# `rich` is deliberately not here: unlike `cold` or `itchy` it is also a name people are called,
# and the cost is the wrong way round - `im rich` only ever got a silly "Nice to meet you, Rich",
# while a Rich loses his own name for the whole conversation. The state list is for words that
# cannot be both.
NOT_NAMES_EXTRA = frozenset("""
due owed english scottish welsh irish british muslim hindu sikh jew pagan mormon sober adhd ocd ptsd
trans gay straight lesbian bisexual asexual blind deaf disabled unemployed retired homeless
dyspraxic dyscalculic
# A condition somebody lives with is how they are, not who they are, and these two end in
# nothing a state is built out of, so the endings cannot catch them: "im depressive" was
# answered "Nice to meet you, Depressive", and a bare "im hypertensive" the same.
depressive hypertensive
knackered shattered starving freezing boiling skint broke aching sore stuck done outside inside
upstairs downstairs online offline asleep awake alright okay fine good great awful terrible
here there back home away out off in on over around up down away late early soon nearly almost
definitely probably maybe honestly seriously literally actually totally completely absolutely
cold hot warm wet dry cross half mid bloody soaked frozen numb dizzy queasy poorly shaky
safe unsafe itchy stiff calm restless faint bloated snotty sniffly achy crampy
tight weak sleepy dozy groggy foggy comfy cosy snug proud guilty unwell dirty clean poor
# How a person is, not who they are: "im unheard" was answered "Nice to meet you, Unheard" - the
# coldest reply there is to somebody saying they are not heard. "unseen" and "nobody" are the
# same shape ("im nobody" was a name too).
unseen unheard nobody
dead beat spent zonked pooped livid fuming miffed
content confident different important present silent decent pleasant fluent patient absent
violent brilliant distant recent constant sunburnt burnt
full empty unsure certain brave silly daft mad grumpy moody fed fedup
# How somebody says they are, in words that are also other things: "im grand" (Ireland), "im
# sound", "im chill", "im content", "im brill", "im mint". Nothing is repaired in any of them,
# so the repair rule cannot see them, and the store handed the word back as a name: "im grand"
# was answered "Nice to meet you, Grand" and every later turn called the person Grand.
grand sound chill content brill mint
# The same for a disparaging word: "im fat" and "im stupid" are how somebody says they are, and
# the store was filing them as a name ("Nice to meet you, Fat").
fat ugly stupid thick dumb
rundown offshore horny
dressed settled from with for by of to near into than as after
# A word about the spelling or the print of the name is not the name: "my name is spelt wrong on
# my payslip" was answered "Hi Spelt - open the payslip and check...", and "my name is misspelt on
# my contract" was answered "Nice to meet you, Misspelt." Every one of these is a thing said *of*
# a name, never a name people are given.
spelt spelled misspelt misspelled mispelt mispelled printed print handwritten hyphenated
capitalised capitalized typed type pronounced
# The words that close a sentence about somebody else's behaviour, which is where a name is
# least likely and the store was most confident: "my son doesnt call me anymore" was read as an
# introduction, so every later turn called the person Anymore, and the reply opened "Hi Anymore
# - a relative going quiet...". A name after "call me" is offered ("call me Dan"); a word that
# only says when or whether the calling happens is not offered at all.
anymore anyways someday sometime sometimes nowadays ever either neither soon later sooner
tomorrow tonight meanwhile afterwards afterward
# The same list, for the reviewers of this change who sent three more of exactly that shape:
# "my son wont call me again" was "Hi Again", and "call me anytime" and "call me whenever you
# like" introduced the person as Anytime and Whenever. They say when or whether, not who.
again anytime whenever always eventually already once then
""".split()) | frozenset("""
sweaty clammy woozy jittery achey queezy muggy bleary puffy giddy edgy antsy twitchy
hangry drowsy buzzy spacey dopey mopey quivery fidgety sniffy wobbly
# A body word that is also a dog's coat or a Snow White dwarf: "im husky" is a voice going and
# "im sneezy" is a cold starting, and both were answered "Nice to meet you, Husky".
husky sneezy
hungover hangover jetlagged jetlag dehydrated out
""".split())


# A word that names a feeling is how the person is, not who they are: "im mad", "im happy",
# "im grateful" are not introductions. The reading engine already lists those words, so they
# come from there rather than from a second list that would drift.
NOT_A_NAME_FEELING = frozenset(
    word for cues in EMOTION_WORDS.values() for cue in cues for word in cue.split())


# A laugh is not a name either, and it comes from the reading's one table so a form the bot has
# just learned to hear as a laugh cannot still be a person called that: "im lmfao" was met with
# "Nice to meet you, Lmfao."
NOT_A_NAME_LAUGH = frozenset(lexicon.LAUGHTER)


# A condition named by its own name is a state of a body or a mind, not who somebody is: "im
# psoriasis", "im sciatica", "im ibs", "im crohns", "im schizophrenia" all introduced the person
# as Psoriasis, Sciatica, Ibs, Crohns and Schizophrenia, and every later turn called them that.
# The body conditions are the reading engine's own table, so a condition it learns to hear is one
# the store will not file as a name. A condition of the mind is deliberately not added to that
# table: `topics.CONDITIONS` is also the health *subject* scorer, and putting "ptsd" in it made
# "my husband has ptsd from the army" / "he wont talk about it" read as an illness follow-up, so
# the card that tells you how to open a hard conversation stood down (measured by breezy-violet on
# #10914). Two tables with two jobs: the word is a name's lookalike here, and a subject there.
CONDITIONS_OF_THE_MIND = frozenset("""
    bipolar schizophrenia schizophrenic psychosis psychotic anorexic bulimic ptsd ocd adhd
    autism autistic dyspraxic dyspraxia agoraphobia agoraphobic narcolepsy narcoleptic""".split())


def _health_words():
    """The words the reading engine already uses for an illness, as whole words."""
    words = set(STRONG["health"].split())
    for phrase in PHRASES["health"]:
        words.update(phrase.split())
    words.update(CONDITIONS)
    words.update(CONDITIONS_OF_THE_MIND)
    return frozenset(words)


# A word that names how the body is is not who they are either: "im shivery" was read as an
# introduction and answered "Nice to meet you, Shivery." The reading engine already knows the
# illness words ("hoarse", "shivery", "queasy", "crampy"), so they come from there rather than
# from a third list that would drift. Nouns in that list ("doctor", "tablet", "appointment") are
# already in NOT_NAMES, so the same test can be one test.
NOT_A_NAME_ILLNESS = _health_words()


# What a person is like is not who they are called either: "im lazy" was answered "Nice to meet
# you, Lazy. What can I help with?", and the trait is the whole line. The words come from the
# reading engine's one table (`lexicon.TRAITS`), so the answer in bot/modules/chat.py and this
# refusal can never drift apart.
NOT_A_NAME_TRAIT = frozenset(lexicon.TRAITS)


# A word that says what somebody is like, written with none of the endings a state usually
# carries, was read as an introduction: "im quiet" and "im messy" were answered "Nice to meet
# you, Quiet", and so were noisy, picky, fussy, bossy, spoilt, rude, chatty, negative, tidy,
# untidy, nosy, weird, odd and loud - and "im hard work" introduced somebody called Hard. These
# are the words `_describes_them` already keeps for another person ("my dad is stubborn", "my
# sister is noisy"); nothing asked that list when the word came straight after "im". They are
# listed here rather than built from that set because the set is defined further down the file,
# and `DESCRIBING_WORDS` takes this one in so the two cannot drift apart.
NOT_A_NAME_DESCRIBING = frozenset("""quiet messy noisy picky fussy bossy stubborn rude spoilt
    chatty negative positive tidy untidy nosy weird odd loud hard""".split())


# How they are and what they are like, in one test: almost every name rule asks this question,
# and a set that is asked in six places is a set that gets forgotten in one.
# The conditions and states that carry none of the endings above and name a thing a person has
# rather than a thing they are called: "im bipolar" was answered "Nice to meet you, Bipolar",
# and every later turn called the person Bipolar. The condition endings are already covered
# (diabetic, asthmatic, dyslexic, epileptic and coeliac are all -ic, -ac or illness words), so
# this is the short list the endings miss: `bipolar` has no ending to go on, and `froze` is how
# somebody says "I am freezing" ("im froze" was an introduction too).
NOT_A_NAME_CONDITION = frozenset("""bipolar froze""".split())


NOT_A_NAME_STATE = (NOT_A_NAME_FEELING | NOT_A_NAME_ILLNESS | NOT_A_NAME_TRAIT
                    | NOT_A_NAME_DESCRIBING | NOT_A_NAME_CONDITION)


# Words people put round an introduction: "oh sorry, im jess", "jess btw", "im jess here".
# They say nothing about the person, so the clause is still an introduction with them in it.
NAME_FILLER = frozenset("""
sorry oh ah ok okay so well hey hi hello hiya morning evening afternoon good hmm um err erm anyway
btw actually also and but yeah yes yep no nah right cool thanks thank please alright howdy
first quickly just then too lol haha
""".split())


NAME_FILLER_PHRASES = ("i forgot to say", "forgot to say", "i should say", "i should have said",
                       "should have said", "by the way", "for the record", "just so you know",
                       "forgot to mention", "i did not say", "i did not mention")


# What can follow a name and leave the line an introduction rather than a sentence about
# something else: "jess here", "jess btw", "jess, nice to meet you", "jess and im 34".
NAME_FOLLOWERS = frozenset("""
here there btw way hi hey hello hiya nice to meet you u thanks thank ta cheers too also again
lol haha x xo sorry but and so just actually ok okay right good great yes yeah yep im am is was
did do your my we us how pleased glad meet meetin
""".split())


# After one of these the rest of the line says where they are or what they do, not what they
# are called: "jess from leeds", "jess at work".
NAME_PLACE_WORDS = frozenset("from in near at live living moved moving".split())


# Words that stand between "where they are" and the place itself: "jess living in leeds".
PLACE_JOIN = frozenset("in near at to from round around outside".split())


# A clause after the name that goes on about the person: "jess, live in salford with two kids",
# "tom, i work in a bakery", "sam, have two cats", "ellie and i'm 34". The line is still an
# introduction, so the name stands; the clause after it is what the person is telling us.
# A possessive ("my daughter is 6", "our cat is called Biscuit") or "I've" ("ive got two
# kids") starts a clause about the person just as "i"/"im" does, and people join an
# introduction to it with nothing but "and": "hi im dan and my daughter is 6" is the same
# introduction as "hi im dan, my daughter is 6". Without these the name was dropped and the
# bot answered "You haven't told me your name yet" to somebody who had just given it.
NAME_SAYS_ABOUT_ME = frozenset("""i i'm im ive i've live lives living work works working have
    has got like love hate prefer study studying play playing run running keep keep looking
    trying do doing need want grew raised born based married
    my our we we're we've myself""".split())


# A name is often followed by a hedge that adds nothing to who they are: "hi im meg to be
# honest", "im sam tbh". The hedge is not the start of a sentence about them, so it is taken
# off the end of the introduction before the tail is read, and the name stands.
NAME_ASIDES = ("to be honest", "to be fair", "to be truthful", "if that helps", "if im honest",
               "i think", "i suppose", "i guess", "i expect", "by the way", "for what its worth",
               "honestly", "tbh", "btw", "anyway", "though", "actually")


# The same hedges, taken off an answer to the bot's own name question rather than off the end of
# an introduction: "its sam by the way", "sam, btw", "im sam thanks". The store waits for one
# word there, so a hedge still on the line made it three and the answer went nowhere: the person
# gave the name they had just been asked for and the bot said "I'm listening - say more if it
# helps", then "You haven't told me your name yet" a turn later. A courtesy after the name is the
# same kind of word, and goes with it.
NAME_ANSWER_HEDGES = re.compile(
    r"\b(?:" + "|".join(sorted(NAME_ASIDES + ("thanks", "thank you", "ta", "cheers"),
                                 key=len, reverse=True)) + r")\b", re.I)


def without_the_hedges(text):
    """A name answer with its hedges taken off: "its sam by the way" -> "its sam".

    Only the words in `NAME_ASIDES` and a courtesy after the name are removed, so the name itself
    is handed on exactly as it was typed.
    """
    low = " ".join(str(text or "").lower().split())
    return " ".join(NAME_ANSWER_HEDGES.sub(" ", low).split()).strip(" ,.:;!?")


# The word that marks a correction sits inside the introduction as often as in front of it:
# "my name's actually Preeya", "my names honestly Dan". Only the words that say nothing about
# what follows are here, so "my name is really long" is still not somebody called Long.
NAME_MIDDLE = r"(?:(?:actually|honestly|truthfully|officially|properly|tbh)\s+)?"


# The person names themselves: "my name's Jess", "call me Dan". The word after it is a name.
ANNOUNCED_NAME_PATTERNS = (
    re.compile(r"\bmy name(?:['\u2019]s| is|s)\s+" + NAME_MIDDLE +
               r"([a-z][a-z'-]{1,19})", re.I),
    re.compile(r"\bcall me\s+" + NAME_MIDDLE + r"([a-z][a-z'-]{1,19})", re.I),
    # "I'm called Dave", "I am called Dave": the same introduction the other way round, and
    # the one people use when the name is not the first thing in the line ("hi, I'm called
    # Dave"). The word after "called" passes the same test as any other name.
    re.compile(r"\b(?:i am|i'm|im)\s+(?:called|named)\s+([a-z][a-z'-]{1,19})", re.I),
    # "Name's Dave", "the name's Dave": the line opens with it, so it is not "her name's
    # Biscuit", which names someone else's pet. The name has to end the line, or close it before
    # a courtesy ("names Dave, thanks"), because "names are hard" and "name and shame" open the
    # same way and are sentences about names, not introductions.
    re.compile(r"^\W*(?:the\s+)?names?(?:['\u2019]s)?\s+(?:is\s+)?" + NAME_MIDDLE +
               r"([a-z][a-z'-]{1,19})"
               r"(?=\s*[,.!?;:)\]]|\s*$|\s+(?:thanks|ta|cheers|btw|anyway|by the way|"
               r"nice to meet you|pleased to meet you|how are you|good to meet you)\b)", re.I),
)


# The name they answer to, as against the one on the paperwork: "i go by kit" is how somebody
# introduces themselves when the name they use is not their first one.
GOES_BY_NAME = re.compile(r"\b(?:i|we)\s+go(?:es)?\s+by\s+([a-z][a-z'-]{1,19})", re.I)


# The edges a line opens a new clause on, so a go-by said as its own thought can be read alone.
CLAUSE_SPLIT = re.compile(r"\b(?:but|and|though|although)\b|[;,.!?]")


# "I'm Jess" and "I go by Kit" are also how any number of sentences about a person start
# ("im cold", "im sat in the car", "i go by bus"), so the rest of the line has to agree.
GUESSED_NAME_PATTERNS = (
    re.compile(r"\b(?:i am|i'm|im|we are|we're)\s+([A-Z][a-z'-]{1,19})\b"),
    re.compile(r"\b(?:i am|i'm|im|we are|we're)\s+([a-z][a-z'-]{1,19})\b", re.I),
    GOES_BY_NAME,
)


# Ways of going somewhere, so "i go by bus" is not someone called Bus.
GO_BY_WAYS = frozenset("""bus car train coach tube tram plane bike foot taxi rail boat ship road
motorway""".split())


MONTHS = frozenset("""january february march april may june july august september october
november december jan feb mar apr jun jul aug sep sept oct nov dec""".split())


DAYS = frozenset("monday tuesday wednesday thursday friday saturday sunday weekend".split())


COUNTRIES = frozenset("""england scotland wales ireland britain uk america usa canada australia
new zealand france spain portugal italy germany greece turkey egypt morocco japan china korea
india pakistan thailand vietnam indonesia mexico brazil argentina peru chile colombia cuba iceland
norway sweden denmark finland netherlands belgium switzerland austria poland czech slovakia
hungary croatia serbia romania bulgaria russia ukraine israel south africa kenya nigeria ghana
philippines malaysia singapore""".split())


# Where a thing is in the house is not a place name: "im from upstairs", "i live downstairs".
NOT_POSITIONS = frozenset("""upstairs downstairs inside outside indoors outdoors here there
abroad away""".split())


NOT_PLACES = MONTHS | DAYS | NOT_NAMES | NOT_POSITIONS | frozenset("""christmas easter summer winter autumn
spring morning afternoon evening night today tomorrow yesterday home work school uni
university college hospital doctor dentist""".split())


PLACE_AFTER = re.compile(
    r"\b(?:in|to|from|near|at|visit|visiting|visited|off to|trip to|travel to|went to)\s+"
    r"([A-Z][a-z]+(?:[ -][A-Z][a-z]+)?)\b")


# Chat-speak names places in lower case: "we're going to lisbon in may".
PLACE_LOWER = re.compile(
    r"\b(?:going to|off to|flying to|fly to|travel(?:l)?ing to|trip to|holiday in|moving to|"
    r"heading to|visit(?:ing)?)\s+([a-z][a-z]{2,})\b", re.I)


# Asking words, not facts: "what am i allergic to again" names no allergy, and "what is my
# budget then" names no budget. A value that opens with one of these is the question talking.
NOT_A_FACT = frozenset("""again already actually anyway anyhow please sorry else though now
anybody anyone anything everywhere somewhere nothing something then though""".split())


# A clause that asks ("what can I have?", "where do I live?") ends the fact before it.
ASK_WORDS = NOT_A_FACT | frozenset("""what who where when why how which whether can could
should would do does did""".split())


# A verb that can follow a joining "then" inside a plan: "swim then do a triathlon".
AFTER_THEN = frozenset("""do get go be have see try take make start learn visit eat stay move
buy save write read run walk swim cook book""".split())


# "a flat in leeds", "the house near york": the home named before the place it is in.
HOME_IN = (r"(?:a|an|the|my|our|this|that)\s+(?:[a-z][a-z-]*\s+){0,2}"
           r"(?:flat|house|home|place|cottage|bungalow|farm|village|town|city|studio|area|"
           r"suburb|apartment|maisonette|caravan|boat)\s+(?:in|near|on|at|outside|round)\s+")


# Where they live is a place whatever the capitals: "i live in leeds", "we moved to preston".
# A stay is a visit and not a home ("we're staying in york for the weekend"), so the verb is
# caught on its own and _places() files the place without calling it home.
# The place they live is still the place when they name what they live in first: "we live in a
# flat in manchester", "we live in a village outside leeds". The second preposition is what makes
# the word after it a place name, so "i live in the city centre" stays a way of living.
DWELLING = (r"(?:flat|house|home|cottage|bungalow|place|caravan|boat|hostel|studio|bedsit|"
            r"village|town|hamlet)")


HOME_DWELL = re.compile(
    r"\b(?:i|we)(?:\s?'?(?:m|re|ve|s)| am| are| have| has| had)?\s+"
    r"(?:(?:just|recently|finally|already|also|now)\s+)?"
    r"(?:(?P<stay>stay|stays|staying)|(?P<planned>moving|relocating|relocate|moving house)|"
    r"(?:live|living|lives|moved|moves|moving|settled|settling|relocating|relocated|relocate|"
    r"based))\s+"
    r"(?:(?:up|back|over|out|down|away)\s+)?(?:in|to|near|outside|round)\s+"
    # A word about the dwelling sits between the article and the noun: "a rented flat in leeds",
    # "a two bed flat in leeds". It cannot be the second preposition, which is where the place
    # starts.
    r"(?:(?:a|an|the|our|my|their|his|her)\s+"
    r"(?:(?!(?:in|to|near|outside|round|at|by|with|from)\b)[a-z][a-z'-]*\s+){0,2}"
    + DWELLING + r"\s+)"
    r"(?:in|near|outside|round)\s+"
    r"(?P<place>[A-Za-z][A-Za-z'-]{1,}(?:[ -][A-Za-z][A-Za-z'-]{1,})?)\b", re.I)


HOME_PLACE = re.compile(
    # "we're living in leeds" is the usual way to say it, and chat-speak drops the apostrophe:
    # "we re living in leeds". Both are the same line.
    r"\b(?:i|we)(?:\s?'?(?:m|re|ve|s)| am| are| have| has| had)?\s+"
    # "i've just moved to bristol", "we recently settled in york": an adverb between the
    # auxiliary and the verb does not change which verb it is, and the move is still a move.
    r"(?:(?:just|recently|finally|already|also|now)\s+)?"
    r"(?:(?P<stay>stay|stays|staying)|(?P<planned>moving|relocating|relocate|moving house)|"
    r"(?:live|living|lives|"
    r"moved|moves|moving|settled|settling|relocating|relocated|relocate|based|"
    # "i rent a flat in leeds", "we bought a house near york": the same fact in the words of
    # someone who pays for the place rather than moves to it.
    r"rent|rents|renting|bought|buying))\s+"
    # "we've recently moved up to york": a particle before the preposition does not change where
    # they moved to. "i live just outside leeds" is the same line with the particle in front.
    r"(?:(?:up|back|over|out|down|away|just|right|far)\s+)?"
    # "i live in a flat in leeds", "we rent a small house near york", "i bought a house in
    # preston": the home is named first and the place it stands in comes after it, so the place
    # is the one the home is in - either after "in" or straight after the verb.
    #
    # The preposition is not optional: left optional, "i live near a school in leeds" read
    # "near" as the place and "i live close to bristol" read "close to" as one, and the store
    # then answered "You live in Near". A preposition with nothing that names a place behind it
    # says how they live, not where, so it leaves the line with no place at all.
    r"(?:(?:in|to|near|outside|round)\s+(?:" + HOME_IN + r")?|" + HOME_IN + r")"
    r"(?P<place>[A-Za-z][A-Za-z'-]{1,}(?:[ -][A-Za-z][A-Za-z'-]{1,})?)\b", re.I)


# A place name of two words is a place: "i live in new york". The words that end it are the same
# ones that end a one-word place, checked word by word in _places().
# Words that follow "i live in" without naming a place: "i live in hope", "i moved in with my
# boyfriend".
HOME_STOP = frozenset("""hope fear pain tears debt misery despair silence darkness denial poverty
sin sin sins the a an my our his her their this that these those with without for at on of two
three four five six ten twenty some any no such what which who whom when where why how much many
more less few lot lots bit town city village flat house home there here it them him me us you
case fact truth style general particular common between limbo fear
tonight today tomorrow yesterday now soon later always never usually often sometimes already still
once twice early late morning evening afternoon night weekend week month year day minute moment while
ago yet again anyway anymore then there here coming going and but so because or plus also
originally born from to into onto towards toward via until till before after about""".split())


# "to" is the one that bites a move: "i moved from leeds to bristol" kept the origin as "Leeds To",
# because the word after a place had to be a stop word to be refused and the destination's own
# preposition was not on the list. The other connectives are the same seam one phrasing over
# ("from leeds into bristol", "from india until 2019"), so the fix is the list and not the move.
# Where they are from, which is not where they live: "i live in bristol now, but im from leeds
# originally" names two places, and a later "where am i from?" asks for the second one.
# The subject and its auxiliary are read as whole words, because half of "were" is "we" and "re":
# with a bare "re" in the auxiliary list, "the parts were from ebay" says the person is from Ebay.
FROM_PLACE = re.compile(
    r"(?:^were\b|\b(?:i'm|i've|i m|i am|i have|i was|im|ive|i|we're|we've|we re|we are|we have|"
    r"we were|weve|we))\s+"
    r"(?:(?:originally\s+|born\s+)?(?:come\s+)?from|born\s+in)\s+"
    r"([a-z][a-z'-]{2,}(?:[ -][a-z][a-z'-]{1,})?)\b", re.I)


# The second from-phrase in one line often has no subject in front of it: "im from leeds,
# originally from bradford though".
FROM_MORE = re.compile(r"\boriginally\s+from\s+([a-z][a-z'-]{2,}(?:[ -][a-z][a-z'-]{1,})?)\b",
                       re.I)


# Where they are from said without the word "from": "i grew up in cork", "i was brought up in
# oslo", "we moved here from poland". The subject has to be the person, so "my mum grew up in
# kerala" is her history and not theirs.
FROM_GROWN = re.compile(
    r"\b(?:i|we)\s+(?:"
    # Where they grew up is named with a preposition, and the preposition can be a soft one:
    # "i grew up near manchester" is from Manchester, not from "Near Manchester".
    r"(?:(?:grew|grows|grow)\s+up|(?:was|were|been|being)\s+(?:brought\s+up|raised))\s+"
    r"(?:in|near|just\s+outside|outside|close\s+to|on)\s+"
    # A place named this way can be wrapped up in a phrase: "i grew up in a village near cork"
    # is Cork.
    r"(?:(?:a|an|the)\s+[a-z][a-z'-]{1,}(?:\s+[a-z][a-z'-]{1,})?\s+"
    r"(?:near|outside|close\s+to|just\s+outside|of)\s+)?"
    # Moving says where from, so the name follows "from" with no second preposition.
    r"|(?:moved|move|moves|moved over|come|came|comes)\s+(?:here|over)\s+from\s+"
    r")([a-z][a-z'-]{2,}(?:[ -][a-z][a-z'-]{1,})?)\b", re.I)


# What someone grew up in is not always a place: "i grew up in care", "i grew up in foster care",
# "i was brought up in a children's home". The place is the name of somewhere, so a common noun
# with an article in front of it ("a council estate", "the countryside") names no place either,
# and a line about it must not leave the person "from Care".
GROWN_NOT_PLACE = frozenset("""care pride poverty debt fear church faith carehomes orphanage
carehome hostel bed sit benefit benefits hospital ill health politness""".split())


GROWN_ARTICLE = frozenset("a an some such every any this that these those".split())


# A place can be wrapped in a phrase - "a village near cork", "a suburb of manchester" - and the
# name after the softer preposition is still where they grew up.
GROWN_NEAR = re.compile(
    r"\b(?:near|outside|close\s+to|just\s+outside|of)\s+([a-z][a-z'-]{2,}(?:[ -][a-z][a-z'-]{1,})?)",
    re.I)


# Words that name the first half of a two-word place: "new york", "saint malo".
PLACE_MIDDLE = frozenset("""new old saint st san santa los las la le port cape fort great little
south north east west upper lower mount lake northern southern eastern western united""".split())


# A naming word in lower case keeps the word after it, because that word is part of the name:
# "im going to sri lanka in june" was filed as Sri, and the store answered "Sri is off, then" to
# a person who had just taken back a trip to Sri Lanka. After an ordinary first word the next word
# is not part of a name at all ("going to bed early" is bed, not "Bed Early").
#
# Only a word that is a name and not an ordinary word of the language is read without a capital to
# guide it. "great", "little", "old", "upper", "lower" and "united" are adjectives first, so
# "im going to great lengths to sort this" was filed as a trip to Great Lengths - and, the whole
# point of the reader, answered "You're going to great lengths to sort this. What do you want to
# do while you're there?". "new" is kept because it names a place far more often than it opens a
# phrase in a line about going somewhere ("new york", "new orleans", "new zealand").
PLACE_NAME_FIRST = frozenset("""new saint st san santa los las la le mount lake fort cape
port sri""".split())


PLACE_LOWER_NAMED = re.compile(
    r"\b(?:going to|off to|flying to|fly to|travel(?:l)?ing to|trip to|holiday in|moving to|"
    r"heading to|visit(?:ing)?)\s+(" + "|".join(sorted(PLACE_NAME_FIRST)) + r")\s+"
    r"([a-z][a-z]{2,})\b", re.I)


def _an_everyday_word(word):
    """Whether the word is one of the language's own, so it is not part of a place's name.

    The name after a naming word is a name because it is not a word the person would have used
    on its own: "sri lanka" and "new york" are names, "great lengths" and "new job" are not.
    The plural is looked at too, because a place is not named for a heap of something: "new
    heights" is not a place and "athens" is.
    """
    low = str(word or "").lower()
    if not low:
        return True
    if low in normalize.LEXICON:
        return True
    for tail in ("es", "s"):
        if low.endswith(tail) and len(low) - len(tail) > 2 and low[:-len(tail)] in normalize.LEXICON:
            return True
    return False


# A country people type in capitals, and the article it keeps: "I live in the UK".
COUNTRY_CAPS = {"uk": "UK", "us": "US", "usa": "USA", "uae": "UAE", "states": "States"}


# A country people write with its article, and the article it keeps: "I live in the UK".
COUNTRY_ARTICLE = frozenset("""uk us usa uae netherlands philippines bahamas maldives seychelles
states""".split())


# Words that follow a travel phrase without naming a place: "going to bed", "off to work".
PLACE_VERBS = frozenset("""bed sleep work school town sleep the a an see do get have try start stop
ask tell say make take give look feel stay live move eat drink buy sell pay book plan meet call go
come home there here it that this them him her me us you we my your our their about back out over
be used buy""".split())


# The home phrase above wants the home verb straight after the subject; people also put a word
# or two between it and the place: "I have just moved to Bristol", "we've lived in York for
# years", "I live in a flat in London". This is the fallback for those, and it only ever adds a
# city the home phrase above could not read. The verb has to follow the subject, so "I want to
# live in Spain one day" and "I told you my sister lives in Leeds" are left alone.
HOME_LOOSE = re.compile(
    r"(?i:\b(?:i|we)(?:'?(?:ve|m|re|d)|\s+(?:have|has|had|am|are|was|were))?"
    r"\s+(?:now|still|just|recently|finally)?\s*"
    r"(?:liv(?:e|ing|ed)|mov(?:e|ed|ing)|settl(?:e|ed|ing)|relocat(?:e|ed|ing)|based|staying)\b)"
    r"[^.;!?]{0,30}?\b(?:in|to|at)\s+([A-Z][a-z]+(?:[ -][A-Z][a-z]+)?)\b")


# "Tokyo and Kyoto", "Rome, not Florence": a short line that names places on its own.
SHORT_LIST = re.compile(r"^\W*(?:[A-Z][a-z]+)(?:\s*(?:,|and|or)\s*[A-Z][a-z]+)+\W*$")


# A denial is the opposite of the fact it names, in the same words: "im not allergic to nuts"
# has "allergic to nuts" in it, and "im not coeliac" has the condition. The negator right in
# front of the words is what tells them apart, and getting this wrong fills the store with the
# one thing the person said they do not have.
# The negator is typed without its apostrophe as often as with it - "he isnt allergic to nuts",
# "she doesnt have one" - and the apostrophe-only reading heard no negation at all: the line
# was filed as the opposite fact, so "my son isnt allergic to nuts" was kept as an allergy of
# his and answered with the nut-free shopping lecture.
DENIAL_WORDS = re.compile(r"(?:\bnot|\bnever|\bno longer|\b(?:is|are|was|were|do|does|did|can|"
                          r"could|would|should|has|have|had|wo|ca|ai)n'?t|\baint)\s+"
                          r"(?:really\s+|actually\s+|even\s+)?(?:a\s+|an\s+|any\s+|\bat all\s+)?$", re.I)


# "im not coeliac", "i'm no longer vegetarian", "im not allergic to nuts": the fact they say
# they do not have. Kept in the shape extract() files it under, so the store can drop it.
DENIAL_OF = re.compile(
    r"\b(?:i(?:m|'m| am)|we(?:re|'re| are))\s+(?:not|never|no longer)\s+"
    r"(?:really\s+|actually\s+|even\s+)?(?:a\s+|an\s+|any\s+)?"
    r"(?:(?P<food>allergic to\s+[a-z]+(?:(?:,| and| or)\s+[a-z]+){0,3})"
    r"|(?P<condition>coeliac|celiac|diabetic|asthmatic|epileptic|anaemic|anemic|"
    r"lactose intolerant|gluten intolerant)"
    r"|(?P<diet>vegan|vegetarian|pescatarian|flexitarian|veggie|plant[- ]based))", re.I)


# A diet taken back rather than a way of eating denied: "im not on a diet any more", "im off the
# diet now", "i stopped doing keto", "ive given up the diet". DENIAL_OF only hears "im not
# vegetarian", so "im on a diet" then "im not on a diet any more" left the fact in the store and
# the next "what diet am i on" answered "You told me you're on a diet" - the line they had just
# taken back, said back to them.
# The plans people follow by name, spelled the way they type them. A plan said with on, doing
# or trying is a diet even when the word "diet" never comes, so the list is what makes "im on
# slimming world" a diet the store can say back instead of denying it a turn later. It is kept
# in one place because the take-back ("i stopped slimming world") and the named read ("im doing
# intermittent fasting") have to know the same plans.
DIET_PLANS = (r"(?:slimming world|weight watchers|intermittent fasting|whole ?30|omad|"
              r"carnivore|dukan|south beach|fast 800|5:2|16:8|4:3|"
              r"keto|paleo|atkins|low[- ]carb|mediterranean|gluten[- ]free|dairy[- ]free|"
              r"plant[- ]based|pescatarian|flexitarian|vegan|vegetarian)")


DIET_PLAN_WORD = (r"(?:(?:slimming world|weight watchers|intermittent fasting|whole ?30|omad|"
                  r"carnivore|dukan|south beach|fast 800|5:2|16:8|4:3|"
                  r"keto|paleo|atkins|low[- ]carb|mediterranean|gluten[- ]free|dairy[- ]free|"
                  r"plant[- ]based|vegan|vegetarian)|diet|dieting)")


DIET_OFF = re.compile(
    r"\b(?:i|we)\s*(?:'m|'re|m|re|am|are)\s+(?:not|no longer)\s+(?:on|doing)\s+"
    r"(?:a\s+|the\s+|an\s+)?(?P<plan>" + DIET_PLAN_WORD + r")\b"
    r"|\b(?:i|we)\s*(?:'m|'re|m|re|am|are)\s+(?:off|done with)\s+"
    r"(?:the\s+|a\s+|my\s+|that\s+)?(?P<off>" + DIET_PLAN_WORD + r")\b"
    r"|\b(?:i|we)\s+(?:came|come|came off|got|went)\s+off\s+"
    r"(?:the\s+|a\s+|my\s+)?(?P<gone>" + DIET_PLAN_WORD + r")\b"
    r"|\b(?:i|we)(?:'ve|ve|'d|d|\s+have|\s+had)?\s+"
    r"(?:stopped|quit|gave up|given up|packed in)\s+"
    r"(?:the\s+|my\s+|this\s+|on\s+)?(?:being\s+|doing\s+|eating\s+|going\s+)?"
    r"(?P<quit>" + DIET_PLAN_WORD + r")\b", re.I)


# The take-back for pets. A pet is nobody's until the line says it is theirs, so a negation is
# not enough on its own: "i dont like my cat today" has the words "dont" and "cat" in it and
# nothing lives in the house on that.
# The words that can end a statement, so "i have a cat and im not allergic to nuts" takes the
# nuts and only the nuts.
CLAUSE_EDGE = re.compile(r"[.;!?]|\b(?:and|but|so|because|though|although|which|while)\b|,", re.I)


# Possession, not feeling: have, own, keep, got, and the words that say it is gone.
NOT_HAVE = re.compile(r"\b(?:don'?t|do not|doesn'?t|doesnt|didn'?t|didnt|never|not|no longer|"
                      r"haven'?t|havent|hadn'?t|hadnt)\s+(?:have|has|had|own|owns|owned|keep|"
                      r"kept|got)\b|\b(?:have|has|had|got)\s+(?:no|not|never)\b",
                      re.I)


# The half of `NOT_HAVE` that a held animal is taken by: the negation is carried by a word that
# means having ("dont have", "never had", "no longer own"), so the animal that follows the clause
# is the thing that is gone. The other half of `NOT_HAVE` ("has never liked it") stays for the
# reader that asks whether a line brings an animal in, where the answer is no either way.
NOT_HAVE_LONGER = re.compile(
    r"\b(?:don'?t|do not|doesn'?t|doesnt|didn'?t|didnt|never|not|no longer|"
    r"haven'?t|havent|hadn'?t|hadnt)\s+(?:have|has|had|own|owns|owned|keep|"
    r"kept|got)\b", re.I)


# "he has no dog" says they have not got one, and it is a take-back. "he has never liked it",
# "she has no interest in walks" and "he has no dog friends" say what the animal is like, and
# `NOT_HAVE` read all of them as the same denial: the store took the animal off its own record
# and answered "Right - no cat, then." to somebody who had just described their cat. The line
# that takes an animal back names the animal as the thing that is gone, so the words after the
# negation are what decides, and a bare verb after it is not a possession at all.
HAVE_NONE = re.compile(
    r"\b(?:have|has|had|got)\s+(?:no|not|never)\s+"
    r"(?:(?:any|a|an|the|my|our|this|that|those|these)\b|pets?|dogs?|cats?|pupp(?:y|ies)|"
    r"kittens?|rabbits?|hamsters?|parrots?|goldfish|fish|horses?|animals?|guinea\s+pigs?|"
    r"gerbils?)\b", re.I)


# A kind word that is the first half of a compound names something else: "he has no dog friends"
# is about the friends, and the dog at the front of it stays theirs.
A_COMPOUND_AFTER = re.compile(r"\s+[a-z]+s\b", re.I)


# "without" is a take-back only when the animal itself is what follows it: "we get by without a
# car" is about the car, and "how do i help rex settle without him" is about the one that has
# gone, not the one they still have. Read as a bare "not", any "without" took the animal they
# were telling the chat about.
WITHOUT_ANIMAL = re.compile(
    r"\bwithout\s+(?:(?:a|an|any|the|my|our|his|her|their|these|those)\s+)?(?:[a-z-]+\s+)?"
    r"(?:pets?|dogs?|cats?|pupp(?:y|ies)|kittens?|rabbits?|hamsters?|parrots?|goldfish|fish|"
    r"horses?|animals?|guinea\s+pigs?|gerbils?)\b", re.I)


# A bare "not" right in front of the animal still names it: "i have a cat, not a dog".
NOT_JUST = re.compile(r"\bnot\s+(?:(?:a|an|the|any|my|our)\s+)?$", re.I)


# A take-back in front of the animal is a take-back even though nothing says "have": "forget the
# dog", "forgot the cat", and a bare "no dog" is the shortest way to say it. Such a line is not
# introducing an animal, and a store that read it as one invented a dog nobody had mentioned and
# then filed it under `pets_gone`: "forget the dog" answered "what pets do i have" with "You've
# got a cat called Tom and a dog".
#
# Only the words that take the animal away are here. "never mind the dog", "ignore the dog" and
# "drop the cat" ask the chat to move on and leave the animal where it was - reading them as a
# take-back deleted a dog the person still had and then told them "You don't have your dog Rex
# any more" - and a bare "no" is the take-back only when the animal ends the line, so the rules
# people state ("no dogs allowed in my flat") are not one. `taken_back_before` reads both.
TAKEN_BACK_BEFORE = re.compile(
    r"\b(?:forget|forgot|forgetting)\s+(?:(?:about|with)\s+)?(?:(?:a|an|the|any|my|our|that|"
    r"this|those|these)\s+)?$", re.I)


# A bare "no" or "not" in front of the animal is the shortest take-back there is, and it is only
# that when the animal is the whole line: "no dog", "no, no dog".
BARE_NO = re.compile(r"^\s*(?:(?:no|not|nope)\b[\s,.]*){1,2}(?:(?:a|an|the|any|my|our)\s+)?$",
                     re.I)


# The same "no" in front of a determiner, with no comma after it, is the person naming the animal
# they mean instead: "no a cat" is "no, a cat" typed the way people type it, and the cat is the one
# they have. Read as a take-back it answered "Right \u2014 no cat." - the opposite of the line - to
# somebody who had just said they had a dog and meant they had a cat.
NO_THEN_A_THING = re.compile(r"^\s*(?:no|nope)\b[\s,.]*(?:a|an|the|my|our|your|his|her|their)\s*$",
                             re.I)


# A phrase can take a pet with no "not" at all: "we had to give the dog away".
GIVEN_AWAY = re.compile(r"\b(?:gave|give|given|giving|took|take|taken|returned|"
                        r"rehom(?:e|es|ed|ing)|got rid of)\b[^.;!?]{0,24}?\b(?:away|up|back|"
                        r"to a (?:friend|neighbour|neighbor|rescue)|to (?:my|his|her|their))\b|"
                        r"\brehom(?:e|es|ed|ing)\b[^.;!?]*", re.I)


# "no pets" takes every animal back, with none named.
NO_PETS = re.compile(r"\b(?:no|not got any|don'?t have any|dont have any|without any|"
                     r"never had any|no longer have any)\s+pets?\b", re.I)


EVERYTHING = "*"


# A pet that died is one they no longer have, but it is not a take-back to say back to them:
# the loss is answered warmly by the feelings side, and the store only has to stop handing the
# animal back. "my cat died last month" then "what pets do i have" must not say they have a cat.
DIED = re.compile(r"\b(?:died|dead|passed (?:away|on)|put (?:\S+ ){0,3}?down|"
                  r"put (?:\S+ ){0,3}?to sleep|euthanis(?:ed|e)|euthaniz(?:ed|e)|"
                  r"have (?:him|her|it|them) put (?:down|to sleep)|"
                  r"didn'?t make it|didnt make it|no longer with us)\b", re.I)


# A pronoun pointing at the animal the line already named: "my dog is called rex, we dont have
# him any more", "we had to put her to sleep".
ANIMAL_DEATH = re.compile(r"\b(?:put (?:\S+ ){0,3}?(?:down|to sleep)|euthan\w*"
                           r"|no longer with us|didn'?t make it|had to be put)", re.I)


# "both cats died", "we lost all of them": a death said over the whole lot takes the lot. Any
# other death of a kind takes one animal, because "my cat died" from someone with two cats is one
# of them, not the two.
LOSS_ALL = re.compile(r"\b(?:both|all of them|all of the|all my|all our|every one|the pair|"
                      r"our pairs?)\b", re.I)


PET_PRONOUN = re.compile(r"\b(?P<pron>him|her|it|them|those|they|he|she)\b", re.I)


PLURAL_PRONOUN = frozenset("them those they".split())


# A line about what they think, remember or said is not a line about what is. "i dont think i
# have a cat" and "i never said i have a dog" are a doubt and a record, and taking the animal
# back on either loses something the person still has: nothing later puts a pet back.
HEDGE = re.compile(r"\b(?:don'?t|do not|didn'?t|did not|cant|can'?t|couldn'?t|could not|"
                   r"wouldn'?t|would not|might not|may not)\s+(?:think|know|remember|recall|say|"
                   r"mean|believe|reckon|suppose|guess|be sure|be certain)\b|"
                   r"\bnot sure|\bnot certain|\bno idea|\bprobably not|\bnot that i know|"
                   r"\bi doubt|\bdoubt it|\bnever said|\bnever told|\bnever mentioned|"
                   r"\bdidn'?t say|\bdidn'?t tell|\bdidn'?t mention|\bhaven'?t said|"
                   r"\bhavent said|\bhaven'?t told|\bhavent told|\bnot what i said", re.I)


ALLERGY = re.compile(r"\ballergic to ([a-z]+(?:[ ,]+(?:and )?[a-z]+){0,3})", re.I)


# The correction shape: the right thing, then the wrong one it replaces. "im allergic to soya
# not peanuts" keeps soya and takes peanuts back out of the store, because a person correcting
# an allergy must be believed - advice for an allergy they have just corrected away is the one
# kind of wrong answer that can hurt.
CONTRAST = re.compile(r"\b(?:allergic to|cant eat|can'?t eat|cannot eat|can not eat)\s+[a-z]+"
                      r"(?:(?:,| and| or)\s+[a-z]+){0,3}[\s,]+not\s+(?P<old>[a-z]+"
                      r"(?:(?:,| and| or)\s+[a-z]+){0,3})", re.I)


# The same fact said the other two ways people say it: "i cant eat nuts", "i have a dairy
# allergy". "Can't" is an allergy or an intolerance; "don't eat" below is a diet.
CANNOT_EAT = re.compile(r"\b(?:can'?t|cannot|can not)\s+(?:eat|have|drink|touch)\s+"
                        r"([a-z]+(?:[ ,]+(?:and |or )?[a-z]+){0,3})", re.I)


X_ALLERGY = re.compile(r"\b([a-z]+)\s+allerg(?:y|ies)\b", re.I)


# The word in front of "allergy" names the allergen only when it is a thing. In a question about
# allergies the word there is a verb, because the line is about how people come by them: "why do
# we get allergies", "how do you catch allergies", "can you develop an allergy". Filed as a fact,
# "get allergies" becomes an allergy called "get", and the store then says it back for the rest of
# the conversation - worse than the denial it replaces, because a denial can be forgotten and a
# fact cannot. The verbs that turn up in that one place are a closed set.
NOT_AN_ALLERGEN = frozenset("""get gets getting got gotten have has had having develop develops
developed developing catch catches caught catching treat treats treated treating prevent prevents
prevented test tests tested testing cause causes caused causing trigger triggers triggered avoid
avoids avoiding manage manages managing notice notices noticed noticing control controls
controlled risk suffer suffers suffered experience make makes made become becomes became""".split())


# "im vegetarian" is how most people type it, so the apostrophe and the "am" are optional
# and "a vegetarian" is allowed.
VEGETARIAN = re.compile(r"\b(i(?:m|'m| am)|he(?:s|'s| is)|she(?:s|'s| is)|we(?:re|'re| are))\s+"
                        r"(?:a |an )?(vegan|vegetarian|pescatarian|flexitarian|veggie|veg|"
                        r"plant[- ]based)\b", re.I)


NO_MEAT = re.compile(r"\b(?:i|we) ?(?:dont|don'?t|do not|never|no longer) eat\s+"
                     r"(?:any |any more |more )?([a-z]+(?:(?:,| or| and) "
                     # A comma joins two foods ("i dont eat fish, shellfish") or opens a new
                     # clause ("i dont eat cashews, im allergic"). The second word has to be
                     # a food, so a subject word after the comma ends the list: read as the
                     # diet, "no cashews, im" is handed back as "you don't eat cashews, im".
                     r"(?!i\b|im\b|i'm\b|ive\b|i'd\b|we\b|we're\b|and\b|but\b|so\b)[a-z]+)?)", re.I)


# Drinking is the other half of what goes on the table, and the store only kept the eating half.
# "i dont drink" filed nothing and got the stock line, "ive given up drinking" the same, and "im
# teetotal" was read as a name - "Nice to meet you, Teetotal." A thing someone does not drink is a
# diet like a thing they do not eat, and a diet is what the answers that keep food off the plate
# read. The verb with no object after it is alcohol: "i dont drink" is how people say they do not
# drink it.
DRINK = frozenset("""alcohol booze wine wines beer beers lager lagers cider spirits gin vodka
whisky whiskey rum prosecco champagne cocktails cocktail sherry brandy""".split())


NO_DRINK = re.compile(
    r"\b(?:i|we)\s+(?:really\s+|just\s+|actually\s+)?"
    r"(?:don'?t|do not|dont|never|no longer)\s+(?:really\s+|just\s+|actually\s+)?drink\b"
    # A shortfall is not a diet: "i dont drink much water" is someone who wants to drink more.
    r"(?!\s+(?:enough|much|too much|a lot|loads|that much|as much|plenty|water|it\b))"
    # "any more" and "at all" are how a thing given up is said; "at the moment" and "these days"
    # are a stretch of time and not a way of life, and a person who is off it for a while is
    # answered about refusing a drink, which is the answer that turn wants.
    r"(?:\s+(?:any\s?more|anymore|at\s+all|now))?\s*[.!]*$", re.I)


# The same said as something given up: "ive given up drinking", "i stopped drinking", "i quit",
# "im on the wagon", "im not drinking at the moment".
# What follows the verb decides whether the line is about drink: "i stopped drinking in january"
# gave up the drink, and "i stopped drinking coffee" gave up the coffee, whose answer is the
# caffeine one and would be lost if this filed a diet. So the verb has to be about the drink and
# nothing else - the sentence ends, or it goes on about when, or why.
GAVE_UP_DRINK = re.compile(
    r"\b(?:i|we)\s*(?:have|'ve|had|ve)?\s*"
    r"(?:given\s+up|gave\s+up|quit|quitted|stopped|packed\s+in|cut\s+out)\s+"
    r"(?:the\s+|my\s+|all\s+)?(?:drinking|drink|alcohol|booze)\b"
    r"(?=\s*(?:[.,;!?]|$|\s+(?:any\s?more|anymore|at\s+all|now|for\s+good|and|but|so|"
    r"because|since|when|after|before|\d+\s+(?:years?|months?|weeks?|days?)(?:\s+ago)?|"
    r"years?\s+ago|months?\s+ago|weeks?\s+ago|ago|"
    r"in\s+\w+|at\s+\w+|last\s+\w+|this\s+\w+|on\s+\w+|over\s+\w+)))", re.I)


# A drink given up by name: "i stopped drinking wine" is the same fact as "i dont drink wine", and
# only names from the drinks people give up on purpose, so "i stopped drinking coffee" is not it.
GAVE_UP_DRINK_THING = re.compile(
    r"\b(?:i|we)\s*(?:have|'ve|had|ve)?\s*"
    r"(?:given\s+up|gave\s+up|quit|quitted|stopped|packed\s+in|cut\s+out)\s+"
    r"(?:the\s+|my\s+|all\s+)?drinking\s+"
    r"(?P<thing>[a-z]+(?:\s+(?:or|and)\s+[a-z]+){0,3})", re.I)


NOT_DRINKING = re.compile(
    r"\b(?:i'?m|i\s+am|we'?re|we\s+are)\s+(?:a\s+|an\s+)?(?:"
    # "im not drinking" is alcohol and "im not drinking much water these days" is a shortfall
    # about water: what follows the verb decides which, so the quantity or the drink after it
    # takes the line back to the hydration question it was asking.
    r"not\s+drinking(?!\s+(?:enough|much|too\s+much|a\s+lot|loads|as\s+much|that\s+much|"
    r"water|anything|any\s+water|it\b|at\s+the\s+(?:moment|minute)|these\s+days|for\s+now"
    r"|this\s+(?:week|month|year)|till\b|until\b))"
    # Only the bare shape and the one that says it is for good: "im not drinking at the moment"
    # is a stretch of time, and the answer for it is how to turn a drink down.
    r"(?:\s+(?:any\s?more|anymore|now))?"
    r"|off\s+the\s+(?:booze|drink)"
    r"|on\s+the\s+wagon|teetotal(?:ler)?|tee-total|non-drinker|nondrinker)\b", re.I)


# A named drink they do not take, and only the drinks that are a choice about alcohol: water, tea
# and coffee are habits, and "i dont drink water" is a shortfall rather than a diet.
NO_DRINK_THING = re.compile(
    r"\b(?:i|we)\s+(?:really\s+|just\s+|actually\s+)?"
    r"(?:don'?t|do not|dont|never|no longer)\s+drink\s+"
    r"(?P<thing>[a-z]+(?:\s+(?:or|and)\s+[a-z]+){0,3})", re.I)


# meat words: only these make "i dont eat ..." a vegetarian, not "i dont eat dairy".
MEAT = frozenset("""meat meats beef chicken pork lamb bacon ham sausages sausage fish seafood
prawns shellfish turkey duck goose venison steak mince gelatine gelatin""".split())


ANIMALS = frozenset("""dog puppy cat kitten rabbit hamster parrot goldfish fish horse pet""".split())


# What a diet is said to be "free from". A person says it of themselves ("im dairy free") and of
# somebody else ("my mum is lactose free"), and it is the same diet either way, so the words live
# in one list and both readers use them.
FREE_FROM = r"(?:dairy|gluten|lactose|nut|egg|sugar|soya|soy|wheat|yeast)[- ]free"


DIET_FREE_WORDS = frozenset("dairy gluten lactose nut egg sugar soya soy wheat yeast"
                            .split())


# "she doesnt eat meat", "my mum is vegetarian": what someone else eats is a fact about them, so
# it is kept against that person (memory["others"]) and never becomes the user's own diet. The
# subject can come first or be named, so both "my mum doesnt eat meat" and "she is vegetarian"
# land on the mum she was just talking about.
OTHER_DIET = re.compile(
    r"(?<!\w)(?P<subj>(?:he|she|they)(?:'s|'re|s|re)?|(?:my|his|her|their|our)\s+\w+)(?!\w)"
    r"[^.,;!?]{0,24}?"
    r"(?:(?:is|are|'s|'re|s|re)?\s*(?:a |an )?(?P<free>" + FREE_FROM + r")(?!\w)"
    r"|(?:is|are|'s|'re|s|re)?\s*(?:a |an )?(?P<word>vegan|vegetarian|pescatarian|flexitarian|"
    r"veggie|gluten[ -]free|dairy[ -]free|lactose[ -]free|wheat[ -]free|sugar[ -]free|"
    r"low[ -]carb|plant[ -]based|keto|paleo|carnivore)(?!\w)"
    r"|(?:doesn'?t|does not|doesnt|don'?t|do not|dont|never|won'?t|wont|can'?t|cant)\s+"
    r"eats?\s+(?:any\s+|any more\s+|much\s+)?"
    r"(?P<food>[a-z]+(?:\s+(?:or|and)\s+[a-z]+)?))", re.I)


# The same fact turned back: "my son doesnt eat fish" then "actually he eats fish", "my wife
# hates mushrooms" then "actually she loves mushrooms". Said on its own the second line is no
# news - "he eats fish" states nothing a store has to keep - so it is read only as a correction,
# and only the store can tell whether the person has anything on record for the line to lift.
# Without this the store went on answering "what does my son eat" with "Your son doesn't eat
# fish.", which is the opposite of the last thing the person said.
THEIR_BACK = re.compile(
    r"(?<!\w)(?P<subj>(?:he|she|they)(?:'s|'re|s|re)?|(?:my|his|her|their|our)\s+\w+)(?!\w)"
    r"(?P<gap>[^.,;!?]{0,24}?)\b(?P<verb>eats|eat|likes|like|loves|love|does|do|did)\b\s+"
    r"(?:(?P<emph>eat|eats|like|likes|love|loves)\s+)?"
    r"(?:now\s+|actually\s+|really\s+)?"
    r"(?P<food>them|it|that|[a-z]+(?:\s+(?:or|and)\s+[a-z]+)?)", re.I)


# The words that make such a line a correction of what they said rather than a new sentence.
# "he eats fish" with none of them is not read at all.
A_CORRECTION = re.compile(r"\b(?:actually|no|nope|sorry|wait|oh|now|again|rather|really|"
                          r"these\s+days|after\s+all)\b", re.I)


# A negator between the person and the verb says the line keeps the restriction rather than
# lifting it: "he doesnt eat fish now" and "he wont eat fish again" are not take-backs.
A_NEGATOR_IN_BETWEEN = re.compile(r"\b(?:not|never|no\s+longer|n'?t|nt)\b|\wnt\b", re.I)


# "a nut allergy" is one nut too many when it is said back: a countable allergen is stored in
# the plural, which is how people list them ("allergic to nuts").
ALLERGEN_PLURALS = {"nut": "nuts", "peanut": "peanuts", "walnut": "walnuts",
                    "hazelnut": "hazelnuts", "cashew": "cashews", "almond": "almonds",
                    "prawn": "prawns", "egg": "eggs", "strawberry": "strawberries",
                    "kiwi": "kiwis", "berry": "berries", "sesame": "sesame", "soya": "soya"}


# A line that only names one more thing ("and milk too", "plus cheese", "i think soya as
# well") states no fact of its own: it has no verb and no subject. Read against what is already
# on record it is that same fact with one more thing in it. Nothing in the line says the thing is
# food, so the words decide: only what people name as a food or an allergen counts, and a line
# that names anything else ("and my sister too", "and work is awful too") adds nothing.
ONE_MORE_FOODS = frozenset("""
    milk dairy cheese butter cream yoghurt yogurt lactose egg eggs
    nut nuts peanut peanuts walnut walnuts hazelnut hazelnuts cashew cashews almond almonds
    pistachio pistachios pecan pecans brazil macadamia chestnut chestnuts pine
    wheat gluten flour bread pasta semolina spelt barley rye oats oat couscous noodles
    soya soy tofu sesame tahini mustard celery celeriac lupin corn maize rice potato potatoes
    fish salmon cod tuna haddock prawn prawns shellfish crab crabs lobster mussels oysters
    squid scallops clam clams anchovy anchovies sardine sardines mackerel trout
    meat chicken beef pork lamb bacon ham sausage sausages turkey duck venison gelatine
    gelatin yeast sugar honey chocolate coffee caffeine alcohol wine beer vinegar
    feta halloumi parmesan mozzarella cheddar brie ricotta paneer stilton gouda edam
    strawberry strawberries kiwi kiwis berry berries banana bananas apple apples
    pear pears peach peaches plum plums cherry cherries grape grapes melon melons
    mango mangoes pineapple avocado coconut tomato tomatoes onion onions garlic
    pepper spices spice curry chilli chili cinnamon cloves ginger mint
    sulphites sulphite sulfites sulfate sulphur sulfites msg aspartame sweetener
    preservatives colourings colouring dye colour color additives
    """.split())


# The lead-in and the tail a line uses when it is adding to what was just said. Both come off,
# again and again, so "oh and also i think maybe milk as well" is the one word "milk".
ONE_MORE_HEAD = re.compile(
    # "actually shellfish too", "sorry, sesame as well": the word that marks the line as an
    # addition is not part of the thing being added. Without "actually" the whole line was read
    # as a maybe that names nothing, so a real allergy was dropped outright.
    r"^(?:(?:it'?s|its|it is|that'?s|thats|this is|these are|those are)|and|also|plus|oh|right|but|"
    r"so|yeah|yes|then|actually|sorry|true|wait|no wait|"
    r"hold on|i think|i reckon|i suppose|maybe|probably|possibly|i think maybe)\b[\s,]*", re.I)


ONE_MORE_TAIL = re.compile(r"[\s,]*(?:\btoo\b|\bas well\b|\balso\b|\bi suppose\b)[\s.!?]*$",
                           re.I)


# A want, a dislike, a maybe, or an animal from their childhood puts no animal in the house.
# "i dont want a dog", "i hate cats", "im thinking about getting a dog" and "i had a dog growing
# up" all used to store one, so the next ask answered "You've got a dog", and a take-back on the
# line then had an animal to hand back that the person never claimed. The cue counts only in the
# same clause as the animal, and only up to the animal.
NOT_THEIRS = re.compile(r"\b(?:want|wants|wanted|need|needs|needed|fancy|fancied|"
                        r"would like|wish i|wishes|hate|hates|hated|dislike|dislikes|"
                        r"disliked|can'?t stand|cant stand|not a fan of|afraid of|scared of|"
                        r"thinking (?:about|of)|thought (?:about|of)|considering|considered|"
                        r"might|maybe|perhaps|hoping|hope to|planning (?:to|on)|plan to|"
                        r"one day|some day|someday|eventually|dream(?:ing)? of|"
                        r"looking at|shopping for|researching|used to|use to|"
                        # "shes been asking for a hamster", "im after a kitten", "the kids are
                        # desperate for a dog": a want said as an ask. Without these the animal
                        # was read as one they have, and the store answered "You've got a
                        # hamster" for a hamster the person was asking about buying.
                        r"asked for|asking for|been asking|begging for|desperate for|"
                        r"mad on|mad for|keen on|keen to get|after a|after an|"
                        r"growing up|as a kid|as a child|when i was (?:little|younger|a kid|"
                        r"a child|small))\b", re.I)


# A want in front of the animal is not a take-back: "i want a labrador" and "i might get a dog"
# name an animal the person would like, and the store has to keep it out of the house without
# also reading the line as an animal being handed back - "No dog, then." answered a wish, which
# is the bot agreeing to take away a dog nobody had. The wish is recorded beside the animal so a
# module that reads `not_theirs` can tell the two apart: bot/memory/ack declines a wish and lets
# the composer answer what they would do with one.
A_WISH = re.compile(r"\b(?:want|wants|wanted|would like|wish i|wishes|fancy|fancied|"
                    r"need|needs|needed|thinking (?:about|of)|thought (?:about|of)|considering|"
                    r"considered|might|maybe|perhaps|hoping|hope to|planning (?:to|on)|plan to|"
                    r"one day|some day|someday|eventually|dream(?:ing)? of|looking at|"
                    r"shopping for|researching|going to get|gonna get)\b", re.I)


# The same in the words that come after the animal: "i had a dog growing up", "a cat years ago".
NOT_THEIRS_AFTER = re.compile(r"^\s*(?:,?\s*(?:when i was|as a (?:kid|child)|growing up|"
                              r"years ago|back (?:then|when)|as a young|later on))\b", re.I)


# Possession is what makes the animal theirs, and it is said with an owner word: "i have a dog",
# "my dog", "our cats", "we got a puppy". A want that names no owner is only a want.
THEIRS_WORD = re.compile(r"\b(?:my|our|their|his|her|have|has|had|got|own|owns|owned|keep|"
                         r"keeps|kept|walk|walks|walked|feed|feeds|fed|bought|rescued|"
                         r"adopted|rehomed)\b", re.I)


# A pet on its way is not a pet in the house. "we are getting a puppy next week" put a puppy in
# the store, so "what pets do i have" answered "You've got a puppy" about one still with its
# mother, and the pet tail asked how long it had been with them. Only the words that buy or
# collect an animal count, and only the same clause, so "we got a puppy" (already theirs) and
# "i am getting the dog out for a walk" (a dog of theirs) are untouched.
# Only the doing, never the noun: "a rescue dog" and "a rescue greyhound" name a dog of theirs,
# and reading "rescue" as the thing they are doing took the dog out of the store, so the next
# "what should i feed him?" had no dog to answer about.
COMING_HOME = re.compile(r"\b(?:getting|adopting|rehoming|picking (?:up|out)|collecting|"
                         r"bringing home|waiting for)\b", re.I)


# Between the word and the animal, only an article or a size can stand: "getting a puppy" and
# "getting two kittens" name an animal that is coming, "getting the dog out" and "getting our
# dog used to it" name one that is already theirs.
ON_ITS_WAY_BETWEEN = re.compile(r"^\s*(?:(?:a|an|another|one|two|three|four|five|some|a "
                                r"rescue|a new|some new|my new|our new|the new|a little|"
                                r"a small|[0-9]+)\s+)*$", re.I)


# "im coeliac", "i am diabetic": a condition, kept as a fact in its own right.
CONDITION = re.compile(r"\b(?:i(?:m|'m| am)|we(?:re|'re| are))\s+(?:a |an )?"
                       r"(coeliac|celiac|diabetic|asthmatic|epileptic|anaemic|anemic|"
                       r"lactose intolerant|gluten intolerant)\b", re.I)


# The slang word is stored as the plain one, so the reply never says "you're veggie".
# Only the slang word is folded: "plant based" rules out dairy and eggs too, so it is not a
# synonym for vegetarian and is kept as it was said.
DIET_NAMES = {"veggie": "vegetarian"}


# How people describe what they eat. None of these is a name, however short the line is:
# "im veg" and "im plant based" are diets, not an introduction.
DIET_WORDS = frozenset("""vegan vegetarian veggie veg pescatarian flexitarian plant based raw
gluten-free dairy-free lactose-free nut-free egg-free sugar-free soya-free soy-free
wheat-free yeast-free keto paleo low-carb carnivore""".split())


# "im on a gluten free diet", "ive been doing the keto diet": the diet is named as a diet.
# A word about not drinking is a word about the person, not what they are called: "im teetotal"
# was read as an introduction and the bot answered "Nice to meet you, Teetotal." The diet reader
# files the same words as the drink they have given up, so the two agree about the line.
SOBER_WORDS = frozenset("teetotal teetotaller tee-total non-drinker nondrinker sober".split())


DIET_NAMED = re.compile(r"\b(?:i'm|im|i've|ive|i am|i have)\b(?:\s+been)?(?:\s+\w+){0,2}?\s+"
                        r"(?P<named>" + DIET_PLANS + r")\s+diet\b", re.I)


# "im on a diet", "ive started a diet", "im doing keto": on / doing / trying says the person
# has taken it up, so a plan named there is a diet even when the word "diet" never comes, and
# a diet with no name is still a diet. Both are what the person eats, which is what the store
# keeps; without them "im on a diet" then "do you remember my diet" denies the diet they said.
DIET_UNDERWAY = re.compile(
    r"\b(?:i(?:m|'m| am)|we(?:re|'re| are)|i(?:'ve|ve| have))\b(?:\s+been)?\s+"
    r"(?:(?:on|doing|trying|starting|started|back on|gone)\s+(?:a\s+|the\s+|an\s+)?"
    r"(?:(?P<named>" + DIET_PLANS + r")\b|(?P<diet>diet)\b)"
    r"|(?P<dieting>dieting)\b)", re.I)


# Some plans are said without on or doing and without the word "diet": "im dairy free", "im
# keto", "im low carb". The plan word after "im" is the diet there.
DIET_BARE = re.compile(
    r"\b(?:i'm|im|i am|i've been|ive been)\s+(?P<bare>" + FREE_FROM + r"|"
    r"low[- ]carb|plant[- ]based|carnivore|keto|paleo|pescatarian|flexitarian)\b", re.I)


# A way of eating said with a verb is not a plan name and is not a name without a verb either:
# "im cutting out dairy", "im off sugar", "im avoiding carbs", "im doing dry january". The
# store kept nothing from those, so the next ask about the diet was denied to somebody who had
# just said it - and a denial of something they said is the worst shape a memory has. The verb
# is kept with the food, because that is what they said: "you're cutting out dairy".
DIET_DOING = re.compile(
    r"\b(?:i'm|im|i am|i've been|ive been|i have been)\s+"
    r"(?P<doing>trying to eat less|trying to eat more|trying to cut out|"
    r"trying to give up|cutting out|cutting down on|cut back on|giving up|avoiding|"
    r"eating less|eating more|not eating|off|doing)\s+(?P<what>[a-z][a-z' -]{1,38})", re.I)


# The word after the verb has to be something to eat. "im off work tomorrow" and "im doing the
# shopping" are the same shape and are not a way of eating, so this decides, not the verb.
DIET_WHAT = frozenset("""sugar sugars carbs carbohydrate carbohydrates dairy meat meats fish
seafood gluten wheat eggs egg alcohol booze caffeine fizzy chocolate sweets bread pasta rice
potatoes protein veg vegetables fruit junk snacks takeaway takeaways processed salt fat
calories soya soy nuts junk-food processed-food fizzy-drinks red-meat white-bread
cheese milk butter coffee tea wine beer lager cider""".split())


DIET_WHAT_TWO = ("dry january", "sober october", "clean eating", "junk food",
                 "processed food", "fizzy drinks", "red meat", "white bread")


# The same way of eating said in the past: "i gave up sugar", "ive given up cheese", "i stopped
# drinking coffee", "we packed in the takeaways". The verb is the whole of what changed and the
# food behind it is what the store keeps, so the phrase is filed as the way of eating they are on
# now. Without it the store kept nothing, and the only row that answered said to take something
# back to the shop, because "gave up" is how a machine dies. Only something to eat counts, so "i
# gave up smoking" is not a diet and keeps the card its own words reach.
DIET_QUIT = re.compile(
    r"\b(?:i|we)\s*(?:have|'ve|had|ve)?\s*"
    r"(?P<doing>gave up|given up|give up|gives up|quit|quitted|stopped|packed in|cut out|"
    r"cut back on|cut down on)\s+(?:the\s+|my\s+|all\s+|our\s+)?(?P<what>[a-z][a-z' -]{1,38})",
    re.I)


# The doing word a way of eating can be said with: "stopped eating meat" is the meat, and the
# verb of the eating is not what they gave up.
EATING_VERB = frozenset("eating drinking having taking".split())


# The store says a diet back in the present ("You told me you're cutting out sugar", "no more
# cutting out sugar"), so a way of eating said in the past is filed as the same thing happening
# now. Filed as it was typed, "i gave up sugar" came back as "You told me you're gave up sugar".
QUIT_AS_DOING = {"gave up": "giving up", "given up": "giving up", "give up": "giving up",
                 "gives up": "giving up", "quit": "giving up", "quitted": "giving up",
                 "stopped": "giving up", "packed in": "giving up",
                 "cut out": "cutting out", "cut back on": "cutting down on",
                 "cut down on": "cutting down on"}


# A diet they went back on, said in the words of the food they eat again. "im cutting out sugar"
# is kept as that phrase, so "im back on sugar" names only the thing that is back: without this
# the store goes on telling them to avoid what they have just put back ("what diet am i on" ->
# "You told me you're cutting out sugar"), which is the opposite of their last line. The food
# word after the verb has to be something to eat, so "im back on monday" is not a diet returning.
DIET_BACK = re.compile(
    r"\b(?:i'm|im|i am|i've|ive|i have|i'd|we're|were|we are|we've)\s+(?:now\s+)?"
    r"back\s+on\s+(?P<back>[a-z][a-z' -]{1,38})"
    r"|\b(?:i'm|im|i am|i've|ive|i have|i'd|we're|were|we are|we've)\s+"
    r"(?:(?:back\s+to|gone\s+back\s+to|started|start|just)\s+)?(?:eating|having)\s+"
    r"(?P<eat>[a-z][a-z' -]{1,38}?)\s+again\b", re.I)


# Words that end the food in "im cutting out sugar for a bit": the fact is the sugar.
DIET_STOP_A_WAY_OF_EATING = frozenset("""for since because cos till until and but so as to
with from at in on the a an my our this that it all last next ago yesterday today years months
weeks days year month week""".split())


# The word in front of the food in "i dont eat red meat": on its own it says nothing.
NO_EAT_QUALIFIER = frozenset("red white processed raw oily fatty farmed".split())


PETS = re.compile(r"\b(dog|puppy|cat|kitten|rabbit|hamster|guinea pig|parrot|goldfish|fish|horse)"
                  r"(?:s|es)?\b", re.I)


# "two cats, milly and tom": a count, then the animals, then their names. The count is what
# says the names belong to the animals and not to something else in the line.
#
# The words between the figure and the animal describe the animal ("two big dogs", "three black
# cats"); they never open a new thing. Allowing a conjunction, a possessive or a verb there made
# a number that belongs to the person into a number of animals: "im 34 and my dog is 3" was read
# as 34 dogs, and "what pets do i have" then answered "You've got 34 dogs." So the gap stops at
# any word that starts the next thing, which also keeps "2 kids and 1 dog" a line about one dog.
NOT_A_COUNT_GAP = r"(?!(?:and|or|but|plus|with|my|our|his|her|their|the|a|an|is|are|was|were|has|have|had|then|so|because)\b)"


# An age is not a count: "a 3 year old dog" is one dog of three, not three dogs, and "my 9 week
# old dog" is not nine of them. The words between the number and the animal are what tell the two
# apart, so an age unit there cancels the count and the line goes on to answer the animal.
AGE_GAP_WORD = (r"(?!(?:year|years|yr|yrs|month|months|mth|mths|week|weeks|wk|wks|day|days|"
                r"hour|hours|minute|minutes)\b)")


PET_COUNT = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d{1,2}|"
                       r"a couple of|a pair of|couple of)\s+" + NOT_A_COUNT_GAP +
                       r"(?:" + NOT_A_COUNT_GAP + AGE_GAP_WORD + r"[a-z-]+\s+){0,2}$", re.I)


PET_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                   "seven": 7, "eight": 8, "nine": 9, "ten": 10, "a couple of": 2,
                   "a pair of": 2, "couple of": 2}


NAME_WORD = re.compile(r"^[A-Za-z][a-z'-]{1,19}$")


NOT_A_NAME = frozenset("""and or but the a an my our his her its their is are was were has have
had got both they them one all each two three four five six seven eight nine ten of to for with
called named too also as who that which name names nickname known rescued rescue puppy kitten
isnt isn't arent aren't wasnt wasn't doesnt doesn't dont don't didnt didn't cant can't wont won't
not never neither nor hardly
dog cat pets animals years
year months month old new little big small
again now then please yet already still just even never before after later soon today tonight
tomorrow yesterday ever anything something
him her it them he she they us me you there""".split())


# The words that say the animal is one more of a kind they already have: "we got another cat called
# Max", "a second dog". Without them, "my cat" is the cat the store already holds, so a line that
# gives the cat a new name is naming the same animal again and not adding one. "a new cat" counts
# because people say it about an animal they have just taken on, and the store keeps its own
# record of the count for a line that gives a number ("i have two cats").
# The marker has to be the word right before the animal ("another cat", "my other cat", "our
# second cat", "my third cat", "the new kitten"), so a phrase that only has the words further
# back is not read as a second animal: "wait a second, my cat is called Max" names one cat.
ANOTHER_ANIMAL = re.compile(
    r"\b(?:another|other|second|third|fourth|fifth|sixth|seventh|new|one more)\s+"
    r"(?:[a-z-]+\s+){0,1}$", re.I)


# The same thing said with the animal after the verb: "we also have a cat called Max", "i also got
# a dog". The marker is "also" with a verb of having right beside it, so a stray "also" elsewhere
# in the line ("also, my cat is called Max") is not a second animal, and "we also have a cat"
# beside a cat they already have is one more of them rather than the cat they have, named again.
ALSO_HAVE = re.compile(r"\b(?:also|too)\s+(?:have|has|had|got|own|owns|keep|keeps|rehomed"
                       r"|adopted|took in|rescued|named)\b"
                       r"|\b(?:have|has|had|got|own|owns|keep|keeps)\s+also\b", re.I)


# "we named the cat Biscuit", "the vet named my rabbit Bunny": the verb comes before the animal and
# the name after it, so the name is not the word next to "named". "i named my cat after my grandma"
# names the cat after somebody and gives it no name; the word after the animal is read only when it
# is a name and not a word about the animal (the lists below say which words are not names).
# "her cat" and "their dog" are somebody else's animal, so a name given to one is not the user's.
NOT_THEIR_DETERMINER = frozenset("his her their".split())


# A title in front of the name is part of the name: "my cat is called Mr Whiskers" is a cat
# called "Mr Whiskers", not a cat called "Mr", and people do name animals after titles ("Lady",
# "Prince", "Sir Purrs"). The title is only taken when a word follows it, so "my cat is called
# Prince" keeps the whole name and "called Dr" alone is still one word.
PET_TITLE = re.compile(r"(?i:(?:mrs|mr|ms|miss|mx|doctor|professor|prof|dr|captain|princess|"
                       r"prince|saint|dame|lady|lord|sir|st)\.?)")


PET_VERB_NAME = re.compile(
    r"\b(?:named|called)\s+(?:(?P<whose>the|our|my|a|an|their|his|her)\s+)?"
    r"(?:dog|puppy|cat|kitten|rabbit|hamster|parrot|goldfish|fish|horse)s?\s+"
    r"(?:(?P<title>" + PET_TITLE.pattern + r")\s+)?"
    r"(?P<name>[A-Za-z][A-Za-z'-]{1,19})\b")


# "we got a puppy and named him Rex": the animal is a pronoun by the time the name is said, and the
# pronoun is not the name. "named him" alone was read as a puppy called "Him".
PET_PRONOUN_NAME = re.compile(r"\b(?:named|called)\s+(?:him|her|it|them)\s+"
                              r"([A-Za-z][A-Za-z'-]{1,19})\b")


# Words that come after the animal in "we named the cat ..." without being the name: where the cat
# is, what it is for, and who it was named after.
NOT_THE_VERB_NAME = frozenset("""
after before because for in into out up down over round around off on at with to from by since
while and or but so then if once already now today tomorrow yesterday tonight
house home flat garden yard boat farm stable
""".split())


NOT_A_PRONOUN_NAME = frozenset("him her it them he she they us me you".split())


PET_NAME = re.compile(
    r"\b(?:called|named)\s+(?:(?P<title>" + PET_TITLE.pattern + r")\s+)?"
    r"(?P<name>[A-Z][a-z'-]+|[a-z][a-z'-]+)\b")


# A word after a title that is still part of the name even though it is in NOT_A_NAME. "Who" is
# there because a question starts with it ("who is the oldest"), but it is also a name word: a cat
# named after the doctor is "Dr Who", and without this the title is all that is kept.
NAME_AFTER_TITLE = frozenset(("who",))


def _name_at(match):
    """Where a "called" match names the animal: the title, when there is one, comes first."""
    return match.start("title") if match.group("title") else match.start("name")


# "my cat is Biscuit": a name given with no "called". Only a capitalised word, so "my dog is
# scared of men" does not become a dog called scared.
PET_IS_NAME = re.compile(r"\b(?:dog|puppy|cat|kitten|rabbit|hamster|parrot|goldfish|fish|horse)s?\s+"
                         r"(?:is|are)\s+(?:called\s+|named\s+)?(?:(?P<title>" + PET_TITLE.pattern +
                         r")s?\s+)?(?P<name>[A-Z][a-z'-]{1,20})\b")


# "the dogs name is rex", "my cats name is milo": the animal is named by the possessive in front
# of "name" and the word after it is the pet's name. The animal's own word is the whole signal, so
# the name is read in lower case too (people type "the dogs name is rex" far more often than with a
# capital), and no pet on record is needed: the line introduces the dog it names. On main the
# animal was filed and the name was dropped - "the dogs name is rex" gave a dog with no name - so
# "whats my dogs name" answered "You haven't told me a name for your dog yet" about a dog the
# line had just named.
PET_POSSESSIVE_NAME = re.compile(
    r"\b(?:the|my|our|your|his|her|its|their)\s+(?:new\s+|little\s+|old\s+|rescue\s+)?"
    r"(?:dog|puppy|cat|kitten|rabbit|hamster|parrot|goldfish|fish|horse)s?\s*(?:'s|s)?\s+"
    r"name\s*(?:'s|is|was)\s+(?:(?P<title>" + PET_TITLE.pattern + r")\s+)?"
    r"(?P<name>[A-Za-z][A-Za-z'-]{1,19})\b", re.I)


# "and her name is Biscuit", "she's called Biscuit": a name for a pet the line does not name
# again. Only her/his/its, so "my name is Nadia" never becomes a dog's name.
# "we adopted a rescue dog, biscuit", "our cat, milo, is scared of men": a name given as an aside
# after the animal, with no "called". Only a single word between commas, so "we're getting a
# kitten, next week" and "my dog has been sick twice, today" name nothing.
PET_APPOSITIVE = re.compile(
    r"\b(?:dog|puppy|cat|kitten|rabbit|hamster|parrot|goldfish|fish|horse)\b[^,.;!?]{0,24},\s*"
    r"([a-zA-Z][a-zA-Z'-]{1,20})\s*(?=$|[,.;!?]|\s+(?:is|was|and|has|needs|loves|hates|does)\b)")


# "my dog max is 4", "our cat biscuit was 12": the name sits between the animal and the fact
# the line says about it, the same way "my brother tom is 12" gives a person's name. Only one word
# is read, so "the dog next door is noisy" names nothing.
PET_BEFORE_FACT = re.compile(
    r"\b(?:dog|puppy|cat|kitten|rabbit|hamster|parrot|goldfish|fish|horse)s?\s+"
    r"(?P<name>[A-Za-z][A-Za-z'-]{1,19})\s+(?:is|was|are|were)\b")


# A word in that place that is about where the animal is, not what it is called: "the dog upstairs
# is loud" has no dog called Upstairs.
NOT_A_NAME_MIDDLE = frozenset("""
upstairs downstairs outside inside indoors outdoors away home back next front behind there here
nearby around about settled used fine
""".split())


# Words that look like a name after the comma but are not: how people talk about a pet, and when.
PET_ANIMALS = frozenset("""
dog puppy cat kitten rabbit hamster parrot goldfish fish horse dogs puppies cats kittens rabbits
hamsters parrots fish horses animal pet
""".split())


# Which kind of animal a word names, so two words for one animal ("a cat and a kitten") are one
# pet and two words for two animals ("a cat and a dog") are a pair. The plural and the young are
# the same animal: a person who says "two cats" has one kind of pet, not two.
ANIMAL_KINDS = {
    "dog": "dog", "dogs": "dog", "puppy": "dog", "puppies": "dog",
    "cat": "cat", "cats": "cat", "kitten": "cat", "kittens": "cat",
    "rabbit": "rabbit", "rabbits": "rabbit",
    "hamster": "hamster", "hamsters": "hamster",
    "parrot": "parrot", "parrots": "parrot",
    "fish": "fish", "goldfish": "fish",
    "horse": "horse", "horses": "horse",
}


def another_animal(text, animal):
    """A second, different kind of animal in the same line, or "".

    "i have a cat and a dog" names two animals, and the reply it got was "A cat - good to know.
    What's its name?", which quietly dropped the dog. Which animal a line is about is the wrong
    question when it is about two, so a reader that would answer for one of them asks this first.
    Two words for one animal are one animal: "i have two cats" and "a cat and a kitten" are not
    pairs, so the kinds are compared rather than the words.
    """
    kind = ANIMAL_KINDS.get(str(animal or "").strip().lower(), "")
    if not kind:
        return ""
    for word in re.findall(r"[a-z]+", str(text or "").lower()):
        other = ANIMAL_KINDS.get(word, "")
        if other and other != kind:
            return other
    return ""


NOT_A_PET_NAME = frozenset("""
today tomorrow yesterday tonight now soon again though although instead already still even too
also either rather which who whose what when where why how and but so or if then than there here
vet vets help advice question thing things lot lots bit one two three years year months weeks days
man men woman women boy girl child kid kids people person male female puppy dog cat kitten pet
he she they it them i we you every each some any all one ones day days week weeks month months
year years after before from with without about over under round around back away out off
""".split())


# The name is read in either case: "her name is pepper" is the same line as "her name is
# Pepper", and people type it lower-case far more often than not. What a word after "name is"
# cannot be ("not", "still", "weird") is turned down by `_not_a_name` below, so lowering the
# case does not turn ordinary words into names.
PET_NAME_ONLY = re.compile(r"\b(?:her|his|its)\s+name(?:'s| is)\s+([A-Za-z][a-z'-]{1,20})\b|"
                           r"\b(?:she|he|it)(?:'s|s)\s+(?:called|named)\s+([a-zA-Z][a-z'-]{1,20})\b|"
                           r"\b(?:we|i)(?:'ve| have)?\s+(?:named|called|call)\s+(?:him|her|it)\s+"
                           r"([a-zA-Z][a-zA-Z'-]{1,20})\b")


# The same line typed in lower case: "and her name is biscuit". People type a name without a
# capital far more often than with one, and the possessive in front of "name" is what says it is
# the animal's name, not the word after it being a name at all. Only used where a pet is already
# on record (see `pet_name_only(lower=True)`), so "his name is long" alone reads nothing.
PET_NAME_ONLY_LOWER = re.compile(
    r"\b(?:her|his|its|their)\s+names?\s+(?:'s|is|was|actually|really)\s+"
    r"([a-z][a-z'-]{1,20})\b", re.I)


# Words that follow "name is" as a comment on the name rather than as the name: "the dogs name is
# long" is a name that is hard to remember, "his name is short" the same, and none of them is a pet
# called Long. They are the words a person reaches for when the name is the thing being described,
# so the line says nothing the store can keep.
A_COMMENT_ON_THE_NAME = frozenset("""long short hard easy difficult tricky complicated silly daft
weird funny strange odd boring lovely nice horrible stupid ridiculous impossible embarrassing
forgettable unpronounceable common rare plain simple weird rubbish""".split())


# What the bot says when it asks for a pet's name, so a one-word answer can be read as the name.
PET_NAME_ASKED = re.compile(
    r"\bwhat(?:'s| is|s)? (?:its|his|her|their) name\b|"
    r"\bwhat (?:do|shall|should) (?:i|we) call (?:it|him|her|them)\b|"
    r"\bwhat(?:'s| is|s)? the name of (?:your|the)\s+(?:dog|cat|puppy|kitten|rabbit|hamster|pet)\b",
    re.I)


# What the bot says when it asks for the person's own name, or admits it does not know it:
# "can you remember my name" -> "I don't know it yet - you haven't said" is a question in all
# but the question mark, and the one word after it is the answer. Without this a bare "sam" was
# nothing at all and the store still said it had never been told.
# Every word of it is about the name. The store's other "I don't know it - you haven't said"
# lines (the age, the job, the place) are the same shape, so a pattern that read "it" instead of
# "name" made "how old am i" / "nine" file a person called Nine: the ask has to be the name's.
USER_NAME_ASKED = re.compile(
    r"\bwhat(?:'s| is|s)? your name\b|\bwhat (?:do|shall|should) i call you\b|"
    r"\bwho am i (?:speaking|talking|chatting) to\b|\bwhat are you called\b|"
    r"\bdon'?t know (?:your name|what your name is)\b|"
    r"\bdon'?t know it yet\b|\byour name (?:again|then)\b|"
    r"\bhaven'?t (?:said|told me) your name\b", re.I)


# A word said about the situation rather than a person: "its hard", "this is tough". They pass
# the shape tests, so they are listed with the other words that are not names.
NOT_A_NAME_THING = frozenset("""hard easy tough great rubbish weird strange wrong right broken
amazing lovely nice better worse possible impossible funny awful terrible horrible annoying
confusing complicated tricky simple stupid mad""".split())


# What people answer with when they read the question as "what do you do": a job says nothing
# about the person's name, and "teacher" came back as "Hi Teacher - good to meet you."
JOB_WORDS = frozenset("""teacher nurse doctor dentist engineer chef waiter waitress builder driver
farmer student accountant lawyer manager receptionist cashier soldier police mechanic hairdresser
barber baker butcher postman designer developer programmer analyst consultant researcher
scientist professor lecturer pilot cleaner decorator handyman gardener carer midwife pharmacist
vet secretary clerk apprentice volunteer""".split())


# A count is not a name: "thirty" and "nine" pass every shape test the name reader has.
NUMBER_WORDS = frozenset("""one two three four five six seven eight nine ten eleven twelve
thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty
seventy eighty ninety hundred thousand million billion dozen zero none""".split())


# "its sam", "this is sam", "the names sam": the words in front of the name are only read as
# an introduction when the bot has just asked for it, because on their own they say something
# else - "its cold" is the weather and "this is hard" is the job.
NAME_ANSWER_ANNOUNCED = re.compile(
    r"^\s*(?:it's|its|it is|this is|that'?s|the name'?s|the name is|the names|the name's|"
    r"im|i'm|i am)\s+([a-z][a-z'-]{1,19})\s*[.!]?\s*$", re.I)


# The same introduction at the end of a longer answer, when the bot has just asked for the name:
# "i havent told you, its sam by the way" is the name and nothing else after it, said after the
# apology for not having given it. Only the end of the line is read, so the name is still the last
# thing the person said, and only where the store was waiting for a name.
NAME_ANSWER_ANNOUNCED_LAST = re.compile(
    r"(?:^|\W)(?:it's|its|it is|this is|that'?s|my name'?s|my name is|call me|"
    r"im|i'm|i am)\s+([a-z][a-z'-]{1,19})\s*[.!]?\s*$", re.I)


# The bot's own list of names, as the memory store writes it: "For a cat: Miso, Willow or Pepper."
# The animal is in the line, and so is every name the person can pick from, so the patterns are
# read off the reply rather than kept in a list here: whatever was offered is what can be picked.
NAMES_OFFERED = re.compile(
    r"\bfor\s+(?:a|an|your)\s+(?P<animal>[a-z]+)\s*:\s*(?P<list>[^.]*?)\.", re.I)


# The question the list answers, said by either of them: "what should we name her" is the same
# ask as the bot's own "what's its name?", and the answer to it is a name and nothing else.
NAME_PICK_ASK = re.compile(
    r"\b(?:what|which)\s+(?:shall|should|would|could|do|can|will|might)\s+(?:i|we|you)\s+"
    # The thing being named is pointed at ("call it", "name her") or named outright: "what
    # should i name my cat" is the same question, and the answer to it is still a name.
    r"(?:call|name)\s+(?:it|him|her|them|this|that|(?:my|our|the|your)\s+"
    r"(?:[a-z]+\s+)?(?:" + "|".join(sorted(PET_ANIMALS)) + r"))\b"
    r"|\bwhat(?:'s|s| is)\s+(?:a|some)\s+good\s+name\b"
    r"|\b(?:any|some)\s+(?:name\s+)?ideas?\s+for\s+(?:a\s+)?names?\b", re.I)


# The words a figure of money is said in after the number. "6 grand" was read as a budget of 6:
# "grand" was not one of them, so the store kept the figure and dropped the word, and two turns
# later the person's own budget came back as "Your budget is 5." - a fact they gave, said back
# wrong. "grand" and "bucks" are how people say thousands and pounds out loud, so they belong in
# the same list as pounds and quid, with the word boundary kept so "5 grandkids" is a count.
BUDGET = re.compile(r"\bbudget\b[^.\d]{0,40}?((?:under |over |less than |up to )?[£$€]?\s?"
                    r"\d[\d,.]*(?:\s?(?:pounds|quid|euros?|dollars?|grand|bucks|k)\b)?)", re.I)


SPEND_BUDGET = re.compile(r"\b(?:i|we)(?:'?ve|\s+have)\s+(?:only\s+)?(?:got\s+)?"
                          r"((?:about |around |up to |under |max(?:imum)? )?[£$€]?\s?\d[\d,.]*"
                          r"(?:\s?(?:pounds|quid|euros?|dollars?|grand|bucks|k)\b)?)\s*(?:to spend|on it|budget)",
                          re.I)


# The limit said as what they mean to do with it, which is how most people say a limit out
# loud: "i want to keep it under 80 pounds", "i can only spend 80 pounds on it", "i need to
# spend under 40". None of those was filed as a budget - the only spend shapes the store knew
# wanted money they already had ("ive got 80 pounds to spend") - so six turns later a party plan
# with a stated ceiling got "You haven't told me a budget", a fact they had given and the bot had
# already answered, which is the worst kind of forgetting: it contradicts them.
#
# Two things make the figure a limit rather than a price: the person is the subject and the verb
# is what they mean to spend (want, need, can, only), and a cap word sits between the verb and
# the money (under, up to, no more than) or the money is what to spend on a named thing. A price
# they are only reporting ("the coat was under 80 pounds") has neither, and stays a remark.
_INTENT = (r"(?:want|wanna|wanted|need|needed|would like|'d like|d like|plan to|planning to|"
           r"am going|are going|hoping|have|'ve|got|can|could|will|'ll|must|should|try to|"
           r"trying to)")


_WHAT_THEY_MEAN_TO_DO = (r"(?:spend|keep (?:it|the cost|costs|the budget|the price)|come in|stay|"
                         r"be (?:under|below|within)|keep to)")


_A_CAP = (r"(?:under|below|less than|up to|no more than|not more than|at most|max(?:imum)?|"
          r"within|around|about|circa)?\s*")


_MONEY_AGAIN = (r"((?:" + _A_CAP + r")(?:[\u00a3$\u20ac]\s?\d[\d,.]*|"
                r"\d[\d,.]*\s?(?:pounds?|quid|euros?|dollars?|bucks|grand|k)\b))")


INTENDED_SPEND = re.compile(
    r"\b(?:i|we)\s+(?:only\s+)?" + _INTENT + r"\s+(?:only\s+)?(?:to\s+)?" +
    _WHAT_THEY_MEAN_TO_DO + r"\b[^.\d]{0,24}?" + _MONEY_AGAIN, re.I)


# The same limit with the thing as the subject: "it has to come in under 80 quid", "this needs to
# stay below 40 pounds". The thing is what the chat is about, and the person is still the one
# saying what it may cost.
THE_THING_MAY_COST = re.compile(
    r"\b(?:it|this|that|the whole thing)\s+(?:has to|needs to|should|must|will|can)" +
    r"\s+(?:only\s+)?(?:come in|stay|be|keep)\b[^.\d]{0,16}?" + _MONEY_AGAIN, re.I)


# "under 80 pounds is all i can do": the figure comes first and the limit is the second half.
# The money word is what makes it money, and "all i can do" is what makes it the ceiling rather
# than a price they are reporting.
ALL_I_CAN_DO = re.compile(
    r"\b" + _MONEY_AGAIN + r"\s+is\s+all\s+(?:i|we)\s+(?:can|could|have|got|afford|manage)"
    r"\s+(?:do|afford|manage|spend|stretch to|stretch|pay)\b", re.I)


# What the person can spend, said as money they have: "i've got 50 pounds for a present", "we
# only have 40 pounds for food", "i only have 30 quid". The line states no budget, but it is
# the figure their answer has to fit, and a later "make that 80" has to move it: without it the
# store has nothing to correct and the turn hedges. The verb has to be there ("i've got", "i
# have", "we had") so "i got 50 pounds for my birthday" stays money received, and "for" has to
# open a thing ("for a present", "for her party") so "for luck" is not a budget.
SPEND_FOR = re.compile(r"\b(?:i|we)(?:'?ve|'d|\s+have|\s+had)\s+(?:only\s+)?(?:got\s+|have\s+)?"
                       r"((?:about |around |up to |under |max(?:imum)? )?[£$€]?\s?\d[\d,.]*"
                       r"(?:\s?(?:pounds|quid|euros?|dollars?|grand|bucks|k)\b)?)"
                       r"\s+for\s+(?:a|an|the|my|our|his|her|their|your|another|\w+'s)\s+\w",
                       re.I)


# "i only have 30 pounds" is a budget; "i only have 30 minutes", "i only have 2 days" are not. A
# bare number after "only have" is nearly always a length of time, so the money word or the symbol
# is what makes it money - without it the store filed a budget of 30 for "i only have 30 minutes
# to cook" and then answered "whats my budget" with it.
MONEY_AMOUNT = (r"((?:(?:about |around |up to |under )?"
                r"(?:[£$€]\s?\d[\d,.]*|\d[\d,.]*\s?(?:pounds?|quid|euros?|dollars?|"
                r"bucks|grand|k)\b)))")


ONLY_HAVE = re.compile(r"\b(?:i|we)\s+only\s+(?:have|had|got)\s+" + MONEY_AMOUNT, re.I)


# The limit said again in another shape: "my budget is 500" then "ive only got 300 now". The word
# that makes it the money they have is "only", and the word that makes it now is "now" - without
# them "ive got 300 followers" is a count and "my budget was 500" is the past.
SPEND_BUDGET_NOW = re.compile(r"\b(?:i|we)(?:'ve| have)\s+only\s+(?:got\s+|have\s+)?"
                              r"((?:about |around |up to |under |max(?:imum)? )?[£$€]?\s?"
                              r"\d[\d,.]*(?:\s?(?:pounds|quid|euros?|dollars?|grand|bucks|k)\b)?)\s*"
                              r"(?:now|these days|at the moment|left)\b", re.I)


# A limit raised in another shape, with the word "budget" nowhere in it: "my budget is 500"
# then "i could stretch to 600", "we can go up to 900 at a push". The person has just told you
# the ceiling moved, so the plan, the present and the recall all have to use the new figure;
# without this the store kept 500 and "whats my budget now" handed back a limit they had
# already left behind. The figure is bare in the common case ("stretch to 600"), so a bare one
# has to end the line or be followed by the words people put after a limit - otherwise "i can
# go up to 600 followers" would file a budget of 600. The first person and the modal keep it to
# their own money: "the jeans will stretch to fit" and "can you stretch to 600" (a question to
# the bot) say nothing about what they can spend.
MONEY_FIGURE = (r"(?:[\u00a3$\u20ac]\s?\d[\d,.]*|\d[\d,.]*\s?"
                r"(?:pounds?|quid|euros?|dollars?|bucks|grand|k)\b)")


STRETCH_BUDGET = re.compile(
    r"\b(?:i|we)\s+(?:could|can|might|may|would|'d)\s+"
    r"(?:maybe\s+|probably\s+|possibly\s+)?"
    r"(?:stretch\s+(?:it\s+)?(?:up\s+)?to|go\s+up\s+to|push\s+(?:it\s+)?(?:up\s+)?to)\s+"
    r"((?:about |around |up to |maybe |just )?"
    r"(?:" + MONEY_FIGURE + r"|\d[\d,.]*(?=\s*(?:$|[.,;!?]|\bat a push\b|\bmax\b|"
    r"\btops\b|\bnow\b|\bfor\b))))", re.I)


# What comes in is the same kind of limit as what they have to spend: "i only earn 1200 a month"
# and "i only get 900 a month" are the figure any plan has to fit, and said back with the stock
# echo ("Got it - you only earn 1200 a month.") they are the filing cabinet again. Two things make
# a figure the money they live on rather than a count of something or a rate: the verb (what they
# are paid) and a period ("a month", "a year", "a week", "a fortnight"). "i get 3 runs a week" is
# a routine and "i earn 20 pounds an hour" is a rate, so neither is a budget; the period is what
# tells the count from the money and the word after the period tells the rate from it.
INCOME_PERIOD = re.compile(r"\s*(?:a|per|each|every)\s+(?:month|week|year|fortnight)\b", re.I)


# A rate, not the money they live on: "20 pounds an hour", "300 a day", "a grand a week"? no - a
# week is a period people are paid by, so it stays. An hour and a day are rates.
# The figure and its period are not always side by side: "we bring home 3000 between us a month"
# and "i take home 1800 after tax a month" put the household, or the deductions, in the gap. Only
# the words that can sit there are allowed through, so a count keeps its counting: "i get 300
# emails a week" is still a routine and not a wage.
INCOME_QUALIFIER = re.compile(
    r"(?:\s+(?:between\s+(?:us|the\s+two\s+of\s+us)|together|in\s+total|altogether|combined|"
    r"after\s+tax|after\s+taxes|after\s+deductions|after\s+national\s+insurance|after\s+ni|"
    r"after\s+stoppages|net|clear|clean|now|currently|each|both)\b){0,3}", re.I)


INCOME_RATE = re.compile(r"\s*(?:an?|per|each|every|/)\s*(?:hour|hr|day|shift|weekend)\b", re.I)


INCOME = re.compile(r"\b(?:i|we)(?:'m|m\b| am| are)?\s+(?:only\s+)?(?:"
                    r"(?:earn|make|get paid|get|bring home|take home|be on|am on)"
                    r"|(?:on))\s+"
                    r"((?:about |around |roughly |up to |just )?(?:[£$€]\s?\d[\d,.]*|"
                    r"\d[\d,.]*\s?(?:pounds?|quid|euros?|dollars?|bucks|grand|k)\b))", re.I)


INCOME_BARE = re.compile(r"\b(?:i|we)(?:'m|m\b| am| are)?\s+(?:only\s+)?(?:"
                         r"earn|make|get paid|get|bring home|take home|on)\s+"
                         r"((?:about |around |roughly |up to |just )?\d[\d,.]*)", re.I)


# A year's pay said with no period at all: "i earn 32000", "my salary is 32000", "im on 32k".
# The period is what tells money from a count ("i get 300 emails") and from a rate ("i earn 20
# pounds an hour"), so its absence is why these lines filed nothing - and why the reply to a
# statement of their pay was a stock line, while "i earn 32000 a year" got the year-to-month
# answer. What stands in for the period is the *shape* of the figure and the verb: only the verbs
# that cannot mean anything but pay are here ("get" and "make" are not, because "i get 3000
# views" and "i make 2000 cookies" are counts), and the figure has to be a year's wage rather
# than a count, which is four digits or a figure in thousands.
INCOME_A_YEAR = (
    re.compile(r"\b(?:i|we)(?:'m|m\b| am| are)?\s+(?:only\s+)?"
               r"(?:earn|earns|earned|get paid|bring home|take home|be on|am on|on)\s+"
               r"((?:about |around |roughly |up to |just )?"
               r"(?:[£$€]\s?\d[\d,.]*|\d[\d,.]*(?:\s?(?:pounds?|quid|grand|k)\b)?))", re.I),
    re.compile(r"\b(?:my|our)\s+(?:salary|wages?|pay|income)\s*(?:is|was|'s|are)?\s*"
               r"((?:about |around |roughly )?"
               r"(?:[£$€]\s?\d[\d,.]*|\d[\d,.]*(?:\s?(?:pounds?|quid|grand|k)\b)?))", re.I),
)


# A budget said with nothing around it: "under 15 pounds", "about 30", "anything under 15 pounds",
# "no more than 20 pounds", "something around 20". The figure is what the line is about, so a lead
# in is allowed but nothing else is: "anything" and "something" are people thinking out loud about
# the number, and the qualifier still has to be there ("just 25" is as likely to be minutes).
BARE_BUDGET_LEAD = (r"(?:(?:anything|anythink|something|somewhere|maybe|probably|honestly|"
                    r"i dunno|dunno|i reckon|i'd say|say|i was thinking|i'm thinking|im thinking|"
                    r"i thought|thinking|i was going to say)\s+){0,3}")


BARE_BUDGET = re.compile(r"^\W*" + BARE_BUDGET_LEAD +
                         r"((?:(?:under|below|less than|up to|around|about|max(?:imum)?|"
                         r"no more than|not more than)\s*)"
                         r"[£$€]?\s?\d[\d,.]*(?:\s?(?:pounds|quid|euros?|dollars?|grand|bucks|k)\b)?)"
                         r"(?:\s*(?:or so|ish|please|i think|i reckon))?\W*$", re.I)


# A ceiling is said as a negative as often as with "under": "nothing over 25 pounds", "not over
# 30 quid", "nothing above \u00a340". It is the same limit as "under 25 pounds" and so the same fact,
# filed as that shape ("no more than 25 pounds") because the store says a budget back as a value
# and "nothing over 25 pounds" opens on a word that ends a value (`_fact_value` cuts at
# "nothing"). The figure has to be money: without the unit "nothing over 25" is as likely to be
# minutes, and "no more than 5 a day" is a habit rather than what they can spend.
CEILING_BUDGET = re.compile(r"^\W*" + BARE_BUDGET_LEAD +
                            r"(?:nothing|not|nowt|no)\s+(?:more than|over|above|past)\s*"
                            r"([£$€]\s?\d[\d,.]*|"
                            r"\d[\d,.]*\s?(?:pounds?|quid|euros?|dollars?|bucks|k)\b)"
                            r"(?:\s*(?:or so|ish|please|i think|i reckon))?\W*$", re.I)


# A limit said without a figure: "not too expensive", "nothing too pricey", "something cheap",
# "on the cheap". It rules out what is worth suggesting as much as a figure does, so it is kept
# like a budget and said back with what the bot will do with it. The whole line has to be the
# limit: "the tickets were cheap" is about a thing they bought, not what they can spend.
# A limit asked as a question about the figure: "is 30 pound enough", "would 20 pound get
# something decent", "will 15 quid do". The money word is there and the figure is what the line
# is about, so it is the same fact as "about 20 pounds" said the other way up. Without it a gift
# chat kept the figure but lost the noun beside it and the bare number was read as a temperature.
# A figure thought out loud: "i was thinking 25 pound", "im thinking about 40 quid". The money
# word is what makes it a limit; without one the same line is a time ("i was thinking 20 minutes")
# and the store leaves it alone.
BUDGET_THOUGHT = re.compile(r"^\W*(?:i\s+was\s+|i'?m\s+|im\s+|i\s+am\s+)?thinking\s+"
                            r"(?:about\s+)?(?:around\s+)?"
                            r"(?P<figure>[\u00a3$\u20ac]?\s?\d[\d,.]*\s?(?:pounds?|quid|"
                            r"euros?|dollars?))", re.I)


BUDGET_ASKED = re.compile(r"^\W*(?:is|would|will|does|do|could|can|should)\s+"
                          r"(?P<figure>[\u00a3$\u20ac]?\s?\d[\d,.]*(?:\s?(?:pounds?|quid|euros?|"
                          r"dollars?))?)"
                          r"\s+(?:enough|do|be enough|get|buy|cover|work|be ok|be okay|be fine)\b", re.I)


VAGUE_BUDGET = re.compile(
    r"^\W*(?:(?:not|nothing|no|never)\s+(?:\w+\s+){0,2}(?:too\s+|that\s+|very\s+)?"
    r"(?:expensive|pricey|dear)|(?:something|anything|nothing)\s+(?:cheap|cheaper|reasonable)|"
    r"on\s+the\s+cheap|budget\s+(?:friendly|ish))\W*$", re.I)


MONEY = re.compile(r"([£$€]\s?\d[\d,.]*|\b\d[\d,.]*\s?(?:pounds|quid|euros?|dollars?|grand|bucks)\b)", re.I)


# An age, and only an age: "i am 6 foot 2" is a height, so a number with a unit after it is not
# one (the reader keeps to a sane range as well), and "i'm 5 11" is a height typed without its
# unit. "i'm 34 years old" is still an age, so "years" is not a unit here. A decimal ("1.75
# metres") is not one either: the 1 in it is not the number the line is about.
AGE_UNIT = (r"(?:foot|feet|ft|cm|centimetres?|centimeters?|inches?|inch|stone|st|kg|kilos?|kgs?|"
            r"pounds?|lbs?|lb|metres?|meters?|m|miles?|mph|hours?|hrs?|mins?|minutes?|weeks?|"
            r"days?|months?|percent|%)")


AGE = re.compile(r"\bi(?:m|'m| am)\s+(\d{1,2})(?![\d.,]\d)\b(?!\s*" + AGE_UNIT + r"\b)"
                 r"(?!\s*\d)", re.I)


# How tall somebody is. The age reader above already refuses a number with a unit after it ("im 5
# foot 10" was no age), and nothing else read the height, so the figure was dropped: the line got
# a listening noise and "how tall am i" was answered "I'm not sure about that one" about a height
# the person had given one line earlier. Both shapes people use are read - feet and inches as it is
# spoken, and the centimetres that go on a form - and the key is the one the correction code
# already knows, so a later "no, 5 foot 8" lands on it.
HEIGHT_FEET = re.compile(r"\b(?:i'm|i\s+am|im|my\s+height\s+is)\s+(?P<feet>\d)\s*"
                         r"(?:foot|feet|ft|')\s*(?P<inches>\d{1,2}|ten|eleven|one|two|three|"
                         r"four|five|six|seven|eight|nine)?\s*(?:\"|''|in(?:ches)?)?"
                         r"(?=\W|$)", re.I)


# The height said as a correction with nothing around it: "no, 5 foot 8". The whole line is a
# lead-in and the figure, so a recipe or an address cannot be read as one.
HEIGHT_BARE = re.compile(r"^\s*(?:(?:no|nope|sorry|wait|ah|oh|actually|make\s+it)[,.!]?\s+)*"
                         r"(?P<feet>\d)\s*(?:foot|feet|ft)\s*(?P<inches>\d{1,2})\s*\W*$", re.I)


# The inches said as a word ("5 foot ten") written as the figure. Kept under its own name: a
# second `NUMBER_WORDS` here would be the one the file has by the time a name is read, and the
# first - the count-words-no-name list above - is what the two name readers ask for. That
# shadowing is how "thirty", "forty", "dozen" and "million" came to be names: only one to eleven
# were still in the list when `reads_as_a_name` asked.
INCH_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
              "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11"}


HEIGHT_CM = re.compile(r"\b(?:i'm|i\s+am|im|my\s+height\s+is)\s+(?P<cm>1\d{2}|2[0-2]\d)\s*"
                       r"(?:cm|centimetres?|centimeters?)\b", re.I)


# An age said in words. The age readers take figures, so "my daughter is eight" was filed as a
# fact with no age in it while the ack said "Noted: your daughter is eight", and the ask one line
# later answered "you haven't told me how old your daughter is". "my gran is eighty-eight" was
# worse: the words were filed as her name, and said back as one (polite-ruler, #conversation
# 50582). Only the words in an age's place are turned into figures - after "is", "are", "was",
# "i am" and "aged", and with nothing after them but the end of the fact or the years counted -
# so "she is one of those" and "two weeks old" stay exactly as they were said.
_NUMBER_IN_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}


_A_UNIT_WORD = r"(?:one|two|three|four|five|six|seven|eight|nine)"


_A_TEEN_WORD = (r"(?:ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
                r"|nineteen)")


_A_TEN_WORD = r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"


AGE_IN_WORDS = re.compile(r"\b(?P<words>" + _A_TEN_WORD + r"(?:[-\s]" + _A_UNIT_WORD + r")?|"
                          + _A_TEEN_WORD + r"|" + _A_UNIT_WORD + r")\b", re.I)


# "hes five" and "shes seven" say an age just as plainly as "he is five" does, and the contracted
# word is the only thing between the person and the number, so it stands where "is" stands.
BEFORE_A_FIGURE = re.compile(r"(?:\b(?:is|are|was|were|aged)\s+|\bi\s+am\s+|\bim\s+|\bi'm\s+"
                            r"|\bam\s+|\b(?:he|she|they|it)(?:'s|s|'re|re)\s+)$", re.I)


AFTER_A_FIGURE = re.compile(r"\s*(?:years?\b(?:\s+old\b)?|yrs?\b(?:\s+old\b)?|yo\b)?\s*"
                            r"(?:[,.!?;:]|$|\band\b|\bbut\b|\bso\b)", re.I)


NOT_YEARS_AFTER = re.compile(r"\s*(?:weeks?|months?|days?|hours?|o.clock)\b", re.I)


# A birthday is a date, and the date is what they want back: "when's my birthday" -> "the 3rd of
# May". The asking word has to be there ("my birthday party is on saturday" is a party, not the
# date they were born), and the date has to look like one - a month or a figure - so a line that
# goes on about the day ("my birthday is going to be quiet") is not read as a date at all.
MONTHS = frozenset("""january february march april may june july august september october november
december jan feb mar apr jun jul aug sep sept oct nov dec""".split())
