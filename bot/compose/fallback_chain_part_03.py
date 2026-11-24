"""Part 3 of 5 of the module, split out of `fallback_chain`.

Everything here is re-exported from `fallback_chain`, so callers import it from there as before.
"""

import re
from ..memory import last_bot
from ..understanding import understand
from ..understanding import kinds as understanding_kinds
from .fallback_data import (
    A_CARE_HOME, A_CARE_HOME_BRING, A_CARE_HOME_GUILT, A_CARE_HOME_MOVED, A_CARE_HOME_VISITING,
    A_SMALL_DAY, BARE_PICK_WEAR_COLD, BARE_PICK_WEAR_HOT, BARE_PICK_WEAR_WET, DISH_DETERMINER,
    DISH_PARTICIPLE,
)

# The day that went badly and the name that came from somebody: the pools those readings choose
# from. They are in the data file with the rest, and the readings that use them live here.
from .fallback_data import A_BOOKING_AHEAD, A_BOOKING_AHEAD_DATED

# What the moved rows take from fallback.py, which is fully defined by the time this
# module is imported, because fallback.py imports it from its own last line.
from .fallback_part_03 import WEATHER_COLD, WEATHER_HOT, WEATHER_WET
from .fallback_part_05 import HARM_ANYWHERE, HARM_NAMED, HARM_ON_ME
from .fallback_part_06 import NEGATIVE_LINE
from .fallback_part_10 import _in_a_pool
from .fallback_part_13 import DATE_AHEAD
from .fallback_part_15 import FOOD_TOPICS, in_a_safety_thread, reading
from .fallback import A_SMALL_DAY, DISH_DETERMINER, DISH_PARTICIPLE, last_bot, re, understand
from .fallback_chain_part_02 import (
    COUNTDOWN_AFTER_CARE, COUNTDOWN_ASK, COUNTDOWN_TO, COUNTED, _choose,
)


def _a_countdown_in_a_care_thread(memory, clean, repaired, understood):
    """The date, said plainly, in a thread where the last real answer was an emergency."""
    from ..memory.topics import in_a_safety_thread  # noqa: PLC0415 - shared reading of memory
    if not in_a_safety_thread(memory):
        return None
    said = " ".join(str(repaired or clean or "").lower().split())
    if not COUNTDOWN_ASK.search(said) or not COUNTDOWN_TO.search(said):
        return None
    from ..knowledge.maths import solve  # noqa: PLC0415 - only this branch needs the sums
    # The reading in memory was made for the previous turn, and that turn was the crisis: "i dont
    # want to live in december" has no countdown in it, so a reading of it finds none here. The
    # line itself is what is being counted to.
    reading = {"clean": said, "words": said.split(), "kind": "question"}
    # An empty memory, because the countdown is not the arithmetic the safety thread holds back:
    # this is the one sum the line is asking for.
    count = solve(said, reading, {})
    if not isinstance(count, str) or not count.strip():
        return None
    # `solve` answers a sum it will not do with a sentence of its own ("I can't see your payday
    # from here, so tell me the date it lands on"), and that is not a count. A figure at the front
    # is what makes it one, so anything else is left to the answer it already had.
    if not COUNTED.match(count.strip().lower()):
        return None
    count = count.strip().rstrip(".") + "."
    return _choose(tuple(line.format(count=count) for line in COUNTDOWN_AFTER_CARE),
                   memory, clean)


# A thing the person did that they are judging themselves for: a confession, or the first half of
# one. The cues are a verdict the person passes on themselves ("i did something stupid", "i was
# horrible", "i feel awful about it") and the deeds that carry the blame with them ("i lied", "i
# lost my temper", "i let her down"), which are the sentences a person says when they are about to
# tell you the rest. Both are first person on purpose: "he lied to me" and "my husband cheated"
# are somebody else's doing and have their own readings above.
A_REGRET_DOING = re.compile(
    r"\bi\s+(?:have\s+|had\s+)?(?:did|done|said|been|was|am|feel|felt)\s+(?:something\s+)?"
    r"(?:really\s+|so\s+|very\s+|quite\s+|a bit\s+|pretty\s+|such\s+)?"
    r"(?:stupid|dumb|thick|silly|bad|awful|terrible|horrible|horrid|wrong|mean|nasty|rude|"
    r"selfish|unfair|pathetic|useless|worthless|guilty|ashamed|judged|daft|idiotic|moronic|"
    r"embarrassing|cringe|a cow|a bitch|a jerk)\b"
    # "i did something embarrassing" is the same confession as "i did something stupid" and was
    # answered "Good to hear. What was the best bit?" - the cheer pool took it for an afternoon
    # worth asking about. "silly" stays where it was, next to a noun, because "i did a silly
    # dance" and "i made a silly joke" are things to be pleased with.
    r"|\bsomething\s+(?:a\s+bit\s+|really\s+|so\s+|very\s+|quite\s+|pretty\s+|such\s+)?"
    r"(?:daft|idiotic|moronic|cringe|awkward)\b"
    # The same thing with the adjective in front of the noun instead of behind the "something":
    # "i did a stupid thing" and "i made a daft thing of it". Only a word for a deed counts
    # there, so "i made a silly joke" and "i did a silly dance" keep their cheer.
    r"|\b(?:did|done|made|make|said)\s+a\s+(?:really\s+|so\s+|very\s+|quite\s+|right\s+|"
    r"real\s+|proper\s+|bit\s+of\s+a\s+)?(?:stupid|daft|dumb|thick|silly|idiotic|moronic|"
    r"embarrassing|cringe|awful|terrible|bad)\s+(?:thing|things|stuff|job)\b"
    r"|\bi\s+(?:have\s+|had\s+)?(?:lied|cheated|stole|shouted|lost\s+my\s+temper|"
    r"wasted|ruined|messed\s+up|screwed\s+up|cocked\s+up|botched|betrayed|snapped)\b"
    # "i cocked up at work", "i put my foot in it", "i made a pig's ear of it": the same
    # confession said with a word nothing had read, so a person who had just told the bot they
    # had made a mess of something at work was answered "Nice one. How did the rest of it go?"
    # - a cheer at a confession, which is the one reply a person does not forgive.
    r"|\b(?:cocked|balls(?:ed)?|buggered|botched)\s+(?:it|things?|that)?\s*up\b"
    r"|\bput\s+my\s+(?:foot|feet)\s+in\s+it\b"
    r"|\bmade\s+a\s+(?:pig'?s?\s+ear|hash)\s+of\b"
    r"|\bi\s+(?:have\s+|had\s+)?(?:made|make)\s+(?:a\s+|one\s+)?(?:huge\s+|big\s+|silly\s+|"
    r"stupid\s+|terrible\s+|awful\s+|bad\s+|daft\s+|dumb\s+|thick\s+)?(?:mistake|error)\b"
    # Chat-speak drops the pronoun, the way "booked the hotel last night" does: "made a stupid
    # mistake today" has the shape of an evening worth asking about and got "Nice - how did it
    # go?". Every word in this arm is a past tense, so a line that opens on one is a report of
    # something done and not an instruction.
    r"|^\s*(?:i\s+)?(?:made|did)\s+(?:a\s+|an\s+|some\s+|the\s+)?(?:\w+\s+){0,2}?"
    r"(?:mistake|error|howler|blunder)\b"
    r"|\bi\s+(?:have\s+|had\s+)?let\s+(?:him|her|them|everyone|everybody|my\s+\w+|"
    r"someone|somebody)\s+down\b"
    r"|\bi\s+(?:really\s+)?(?:regret)\b"
    # "i shouldnt have said that" is the confession; "i shouldnt have another biscuit" is the
    # next thing on the plate and nothing to do with what happened, so this arm reads the deed
    # rather than the phrase.
    r"|\bi\s+shouldnt\s+have\s+(?:said|done|told|lied|shouted|yelled|snapped|eaten|drunk|"
    r"bought|spent|sent|texted|signed|answered|opened|posted|shared|taken|stayed|called|"
    r"let|been|gone)\b"
    r"|\bi\s+should\s+not\s+have\s+(?:said|done|told|lied|shouted|yelled|snapped|eaten|drunk|"
    r"bought|spent|sent|texted|signed|answered|opened|posted|shared|taken|stayed|called|"
    r"let|been|gone)\b")


# What turns the same words into something else: a question about what to do (the advice pools
# answer it), a plan ("i shouldnt have another biscuit" is about to come, not a confession), and
# a line about what happens now rather than what happened.
NOT_A_REGRET = re.compile(
    r"\?|^(?:can|could|should|would|will|do|does|did|is|are|was|were|what|how|why|when|where|"
    r"who|which|any)\b|"
    r"\b(?:how\s+(?:do|can|should)|what\s+should|should\s+i|shall\s+i|do\s+i|can\s+i|"
    r"tomorrow|next\s+(?:time|week)|from\s+now\s+on|in\s+future|"
    r"want\s+to|wanna|gonna|going\s+to|i\s+will|i'?ll|plan(?:ning)?\s+to|"
    # "can my employer stop my pay if i make a mistake" is a rule about the world with the
    # person's mistake in a subordinate clause, and "if i" is the shape that hypothetical takes.
    r"(?:if|unless|whether)\s+i)\b")


# "i snapped a photo at the wedding" is the camera and "i let my hair down at the party" is the
# good time: both carry a word from the list above and neither is a thing to be sorry for.
SNAPPED_A_PHOTO = re.compile(
    r"\bsnapped\s+(?:a|another|some|two|three)\s+"
    r"(?:photo|photos|pic|pics|picture|pictures|selfie|shot|shots)\b"
    r"|\blet\s+(?:my|his|her|their|our)\s+(?:hair|guard)\s+down\b"
    r"|\blet\s+off\s+steam\b")


# A mistake with a job named after it is a problem to fix, not a confession: "i made a mistake on
# my tax return", "i messed up the booking", "i made a mistake in the recipe" want the form filled
# in again, and "you don't have to dress it up for me" is sympathy they did not ask for. The
# mistake with nobody and no job after it ("i made a mistake", "i made a mistake at work") is
# still the confession the pool is for, and so is one with a person after it ("i made a mistake
# with my mate"), because that is somebody they think they have hurt.
A_MISTAKE = re.compile(r"\b(?:mistake|error|messed\s+(?:it\s+)?up|screwed\s+(?:it\s+)?up)\b")


THE_JOB_NAMED = re.compile(
    r"\b(?:mistake|error|messed\s+(?:it\s+)?up|screwed\s+(?:it\s+)?up)\b[^.]{0,24}?"
    r"\b(?:on|in|with|at|to)?\s*(?:my|the|our|a|an)\s+([a-z]+)")


NOT_A_JOB_BUT_A_PERSON = frozenset("""
    mum mom mummy dad daddy mate mates friend friends son daughter wife husband partner fiance
    boss team kid kids child colleague workmate sister brother nana gran granny nan neighbour
    neighbor someone somebody him her them everyone everybody people lass lad girl boy man woman
""".split())


# Who did it, when the line says: the person who lied, cheated or hid money, read on its own
# because "my husband has been lying to me" never says "found out" and "turns out he cheated"
# names nobody at all.
WHO_DID_IT = re.compile(
    r"\b(?:s?he|they|my (?:partner|husband|wife|boyfriend|girlfriend|fianc\w*|ex|mate|friend|"
    r"brother|sister|son|daughter|mum|dad|mother|father|boss|landlord|flatmate|housemate))\b")


# The wrong itself, as people say it. Every one is a thing done to the person by somebody close,
# so none of them belongs to a good day out and none is another person's bad luck. A lie, a cheat
# or a theft on its own says nothing about who it was done to: "he cheated at cards", "she cheated
# in the exam", "he lied about the film times", "he cheated death" are all things people say with
# nobody wronged, and the pool would be consoling somebody for a harm nobody did. So the words
# that can be about a thing are in A_WRONG_SAID and have to be aimed, and the ones that cannot
# ("an affair", "texting his ex") are read on their own.
A_WRONG_PLAIN = re.compile(
    r"\b(?:gambl\w*|affair|seeing someone|texting (?:his|her|their) ex|"
    r"back with (?:his|her|their) ex|drinking again|on the (?:booze|drugs) again|using again|"
    r"owed? (?:me|us) money|gone behind my back|kept it from me|been unfaithful|"
    r"cheat(?:ing|ed) on (?:me|us)|slept with (?:someone|somebody|my)|sent pictures)\b")


A_WRONG_SAID = re.compile(
    r"\b(?:ly(?:ing|ed)|lied|lies|cheat\w*|hiding|hidden|hides|stole|stolen|stealing)\b")


# What makes a lie or a cheat aimed at the person rather than at a thing: it is said to them
# ("lied to me", "cheated on me"), it is about their own ("about my cooking"), or it is about
# money, which in a household is the person's own.
A_WRONG_AIMED = re.compile(
    r"\s+(?:to|at|with|on)\s+(?:me|us)\b|\babout\s+(?:\w+\s+){0,2}(?:me|my|us|our|mine|ours)\b"
    r"|\s+(?:money|his wages|her wages|the savings|the rent|the bills)\b"
    r"|\s+(?:it\s+)?from\s+(?:me|us)\b")


# A complement that names a thing the wrong was about: a score, a time, a test, an exam, a game,
# a price. Nothing here is a harm done to the person.
A_WRONG_ABOUT_A_THING = re.compile(
    r"\s+(?:to|at|in|on|over|about|with|for)\s+\S"
    r"|\s+(?:the|a|an|his|her|their|its)\s+\S")


# The news that it was found out. A lie with nothing said about what it was about is the shape
# this pool answers only when the line also says it came to light: "i found out hes been lying",
# "turns out he cheated". Without that, "hes been lying" alone has no wrong named.
FOUND_IT_OUT = re.compile(
    r"\b(?:found|find|turned|turn)\s+(?:it\s+)?out\b|\b(?:turns|turned)\s+out\b"
    r"|\b(?:just\s+)?(?:heard|learned|learnt|discovered|found)\b")


FOUND_OUT = re.compile(
    r"\b(?:found|find|turned|turn) (?:it )?out\b|\b(?:turns|turned) out\b|"
    r"\b(?:just )?(?:heard|learned|learnt|discovered|found)\b")


def _a_betrayal(clean):
    """True when the line reports that somebody close lied, cheated or hid something from them.

    "i found out hes been lying" and "turns out hes been texting his ex" are the same news, and so
    is "my husband has been lying to me", which says nothing about finding out: the reading is the
    wrong done by a person of theirs, and everything else here - the day pool, the cheer, the
    receipt that says it back - is a reply to another kind of line.
    """
    text = " ".join(str(clean or "").lower().split())
    if not text or len(text.split()) > 22:
        return False
    wrong = A_WRONG_PLAIN.search(text)
    if not wrong:
        wrong = A_WRONG_SAID.search(text)
        if not wrong:
            return False
        # A lie or a cheat about a thing is not a wrong done to the person: "he lied about the film
        # times", "she cheated in the exam", "he cheated at cards", "my son lied about his
        # homework". It is one when it is aimed at them, or when nothing says what it was about
        # and the line has just found it out.
        if not A_WRONG_AIMED.search(text):
            if A_WRONG_ABOUT_A_THING.match(text[wrong.end():]):
                return False
            if not FOUND_IT_OUT.search(text):
                return False
    if not WHO_DID_IT.search(text[:wrong.start()]) and not FOUND_OUT.search(text[:wrong.start()]):
        return False
    # A wrong aimed at somebody else is their story, not this one: "my mate lied to his boss" and
    # "she stole money from her mum" are news about other people, and the pool would be consoling
    # the person for a thing that was not done to them. The wrong has to be said of them - "to
    # me", "on me" - or said of nobody at all, which is how a lie or an affair is told.
    after = text[wrong.end():]
    if re.search(r"\b(?:to|with|from|on|at)\s+(?!me\b|us\b)"
                 r"(?:his|her|their|my|the|a|an|some)\b", after):
        return False
    if HARM_ON_ME.search(text) and not WHO_DID_IT.search(text):
        return False
    return True


def _a_thing_they_regret(clean):
    """True when the line tells the bot about something the person did and is sorry for."""
    text = " ".join(str(clean or "").lower().split())
    if not text or len(text.split()) > 20:
        return False
    if not A_REGRET_DOING.search(text):
        return False
    if NOT_A_REGRET.search(text) or SNAPPED_A_PHOTO.search(text):
        return False
    job = THE_JOB_NAMED.search(text) if A_MISTAKE.search(text) else None
    if job and job.group(1) not in NOT_A_JOB_BUT_A_PERSON:
        return False
    if HARM_NAMED.search(text) or HARM_ON_ME.search(text):
        return False
    return True


# The day it happened on: a marker of a time already gone.
DAY_PAST = re.compile(
    r"\b(?:today|tonight|last night|yesterday|this morning|this afternoon|this evening|"
    r"at the weekend|over the weekend|this weekend|last weekend|all day|all morning|"
    r"the other day|earlier)\b")


# Whose day it was: the person's own, or the plain "it" of "work was ok today".
A_DAY_SUBJECT = re.compile(
    r"\b(?:i|i'm|im|ive|i've|we|we're|weve|we've|my|our|it|work|school|the weather|the day)\b")


# A past tense, read off the form of the word rather than off a list of what a person might
# mention: every one of these is a thing that has already happened, and a line that reaches this
# far has already been read for trouble, a fault, a plan and a body.
PAST_DOING = re.compile(
    r"\b(?:had|got|saw|was|were|went|did|made|took|met|ate|drank|bought|brought|read|played|"
    r"watched|walked|cooked|cleaned|painted|cut|sorted|finished|started|spent|sat|ran|came|left|"
    r"gave|found|booked|visited|helped|learned|learnt|worked|slept|drove|caught|wore|won|felt|"
    r"heard|told|said|sold|paid|sent|kept|put|let|set|fell|held|stood|thought|knew|began|broke|"
    r"spoke|rang|sang|wrote|built|swam|saw|ran)"
    # A word ending in "ed" is a doing, unless it is a thing or a colour: "the skin around it is
    # hot and red" is a symptom, and "red" read as a past doing made the small-day pool answer an
    # infected cut with "Sounds alright. Anything good in it?". The three words excluded here are
    # nouns, so the past doings of three letters - fed, led, wed, bled - are still readings of a
    # day, which cutting the word down to `\w{2,}ed` also dropped.
    r"\b|\b(?:(?!red\b|bed\b|shed\b|"
    # The words that end in "ed" and are not a thing that happened. "i need help with my
    # daughters birthday" was read as an account of a day - "need" is the only verb in it and it
    # ends in "ed" - and answered "Nice one. How did the rest of it go?"; a need is a thing they
    # want now, not a day behind them, and neither is a feed, a bleed or a speed.
    r"need\b|feed\b|bleed\b|speed\b|weed\b|seed\b|breed\b|proceed\b|succeed\b|exceed\b|"
    r"indeed\b|hundred\b|greed\b|creed\b)\w+ed)\b")


# A symptom said as a state rather than as an ache: skin hot or red, a wound weeping, a joint
# swollen. The symptom words the body reader knows are aches and pains, so these lines reached a
# reading of the day instead.
A_SYMPTOM_PHRASE = re.compile(
    r"\b(?:hot|warm)\s+(?:and\s+)?(?:red|redder|swollen|tender|puffy|angry)\b"
    r"|\bred(?:ness)?\s+(?:and\s+)?(?:hot|warm|spreading|swollen|tender|angry|streaky)\b"
    r"|\bhot to (?:the )?touch\b|\bweeping\b|\boozing\b|\boozed\b|\bpus\b"
    r"|\bswollen (?:and|or) (?:red|hot|tender)\b", re.I)


# Not a day that happened: a plan, a want, or a day still to come.
NOT_A_DAY_DONE = re.compile(
    r"\b(?:tomorrow|next (?:week|weekend|month|year|monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday)|gonna|going to|i will|i'll|ill|want to|wanna|plan to|planning to|"
    r"should i|shall i|can i|could i|do i|did i|have i|am i|are we|named|renamed)\b")


def _a_care_home_line(understood, memory):
    """The reply to somebody living in a care home, or None."""
    care = (understood or {}).get("care_home") if isinstance(understood, dict) else None
    if not isinstance(care, dict):
        return None
    pronoun = str(care.get("pronoun") or "they")
    several = pronoun == "they"
    words = {"they": pronoun, "them": "them", "their": "their",
             "is": "are" if several else "is"}
    shape = str(care.get("shape") or "")
    if shape == "bring":
        pool = A_CARE_HOME_BRING
    elif shape == "guilt":
        pool = A_CARE_HOME_GUILT
    elif shape == "visiting":
        pool = A_CARE_HOME_VISITING
    elif shape == "moved":
        pool = A_CARE_HOME_MOVED
    else:
        pool = A_CARE_HOME
    return _choose(tuple(line.format(**words) for line in pool), memory,
                   str(care.get("who") or ""))


# A thing they have is not a day they had. "ive got a mortgage" is the store's filing - "Noted:
# you've got a mortgage." - and "got" is a past doing, so the receipt was swapped for the day
# pool's question: "ive got a car" was answered "How was it, overall?", "ive got a boiler" "Nice
# one. How did the rest of it go?" and "ive got a dishwasher" "Sounds alright. Anything good in
# it?", while the same line with "i have" got "Noted: you have a car." Nobody asks how a thing
# they own went. Only the auxiliary form counts: "i got a haircut" and "we got burgled" are days,
# and "ive got to go" is a leave, which is answered above.
HAVE_GOT_A_THING = re.compile(
    r"\b(?:i|we)(?:['\u2019]?ve|['\u2019]?d|\s+have)\s+"
    r"(?:only\s+|just\s+|still\s+|already\s+|now\s+)?(?:got|gotten)\b(?!\s+to\b)", re.I)


# The person measured against other people. The cue is a crowd - "everyone else", "all my
# mates", "the only one", "people my age" - and the thing being measured is a milestone or a
# place in the order: a house, kids, a wedding, a career, "sorted", "settled", "behind", "ahead".
# Both halves are needed: a crowd on its own is "everyone is coming round tonight" and a
# milestone on its own is "i finally bought a flat".
A_CROWD = re.compile(
    r"\b(?:everyone|everybody|everyone'?s|everybody'?s|other people|others|the only one|only one|"
    r"nobody else|no one else|no-one else|"
    r"(?:everyone|everybody|people|friends|mates)\s+(?:i know|around me|my age|else|at work|"
    r"from school|from uni|from work|these days)|"
    r"all (?:of )?my (?:mates|friends|family|cousins|brothers|sisters|colleagues|workmates)|"
    r"people my age|people of my age|my age)\b")


# A place in the order, or a milestone that is the thing people are placed by. "behind" and
# "ahead" are the words a person uses for the scoreboard, so they carry the reading with any
# crowd in front of them.
A_MILESTONE = re.compile(
    r"\b(?:behind|ahead of|sorted|sorted out|settled|milestone|milestones|"
    r"bought|buying|own(?:s|ed)? a|house|houses|flat|mortgage|babies|baby|kids|children|"
    r"married|wedding|engaged|pregnan\w*|career|promotion|their lives|getting on with it|"
    r"moved on|all sorted)\b")


# Not this reading: a line that asks something (its answer is not a reassurance), a line where
# the crowd is doing something to the person ("everyone at school hates me" is a care line and
# the harm readers above it own it), a crowd celebrating the person's own news ("everyone is
# happy for us", "my sister had a baby and everyone is delighted"), and a plan or an event the
# crowd is part of ("all my mates are coming round").
NOT_A_CROWD_AHEAD = re.compile(
    r"\b(?:hate|hates|hated|bully|bullied|bullying|picks? on|picked on|leaves? me out|"
    r"left me out|laughs? at|laughed at|ignores? me|ignored me|mean to me|rumours?|gossip|"
    r"happy for (?:us|me)|proud of me|delighted for|congratulat\w*|well done|"
    r"coming round|coming over|round tonight|tonight|tomorrow|next week|next month|next year|"
    r"this weekend|party|gonna|going to|we'?re all|we are all|shall we|should we|any tips|"
    r"how do i|what should|am i|"
    # "im the only one doing anything round the house" is the work the person does for a
    # household, not a place in the order against other people, and it is the grievance readers
    # above that own it.
    r"only one (?:who|doing|that|bothered))\b")


# The frame that makes a milestone a comparison rather than news: the person is behind it, the
# only one without it, or set against a whole set of people. Without one of these the line is
# somebody else's news ("my sister had a baby and everyone is delighted") or a plan.
CROWD_ORDER = re.compile(
    r"\b(?:behind|ahead of|sorted|settled|caught up|only one|but me|"
    r"all (?:of )?my (?:mates|friends|family|cousins|brothers|sisters|colleagues|workmates)|"
    r"around me|my age|people my age|"
    r"(?:and )?i(?:'?m| am)? (?:havent|haven't|have not|aint|ain't|am not|dont|do not)|"
    r"i'?m not|im not|and i'?m still|still not|without)\b")


# A scoreboard is not an answer: each line names the comparison and hands the person their own
# question back, without guessing at the milestone they are missing.
A_CROWD_AHEAD = (
    "That comparison lands on nearly everybody, and it is not a fair one: you are seeing their "
    "headline and your own whole week. What would you actually like for yourself?",
    "The people who look sorted are mostly just further into their own thing. What is the next "
    "bit you would choose for yourself, if nobody were watching?",
    "It is worth pulling those two apart: which of those things do you actually want, and which "
    "do you only want because they have it?",
    "Everyone's timetable is their own and yours is not late, it is just not the same one. What "
    "would a good year look like for you?",
    "Nobody posts the part where it is going badly. What is the bit of your own you would want "
    "to change first?",
    "That is the comparison that makes everybody feel behind, and it has never once had the "
    "full picture. What would you want to be true for yourself a year from now?",
)


def _the_crowd_is_ahead(clean):
    """True for a line that measures the person against other people.

    A short line, no question in it, a crowd in it, a milestone in it, and the frame that makes
    the milestone a comparison (see CROWD_ORDER). The exclusions are the crowds that are not a
    measuring stick: one doing something to the person, one cheering their news, and one that is
    a plan for the evening.
    """
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text or len(text.split()) > 16:
        return False
    if not A_CROWD.search(text) or not A_MILESTONE.search(text):
        return False
    if not CROWD_ORDER.search(text):
        return False
    return not NOT_A_CROWD_AHEAD.search(text)


# A line that means the day went badly, as the understanding reads it. "work was mad today" and
# "today was mad" are the mood words the engine already files as anger, and they are the commonest
# way a hard day is said without a word like "rough" in it.
A_HARD_DAY_MOOD = ("angry", "sad", "tired", "worried", "stressed", "upset")


def _an_emotion(clean):
    """The emotion the understanding engine reads in a line, or None."""
    try:
        return understanding_kinds.emotion_of(clean) or None
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return None


def _just_asked_about_the_day(memory):
    """True when the bot's own last line was already the question about the day.

    "we had a takeaway last night" / "it was nice not cooking" was asked how it went twice, which
    reads as not listening to the answer. The bot's last line is the test, so the second turn is
    left to the rest of the chain.
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    return _in_a_pool(str(turns[-1].get("bot") or ""), (A_SMALL_DAY,))


# A line with a "not" in it is a doubt or a complaint, not an account of the day: "my brother is
# not cut out for the army" was read as a day out and got "Nice one. How did the rest of it go?".
# A negative auxiliary, spelled with the apostrophe a phone or a quick typist leaves out: the
# optional character is what "isnt" and "isn't" and "isn’t" have in common, so neither spelling
# needs its own arm and a curly one from a phone keyboard is not a miss.
_A_NEGATIVE_AUXILIARY = ("not|never|no|isn['’]?t|aren['’]?t|don['’]?t|didn['’]?t|"
                         "wasn['’]?t|weren['’]?t|can['’]?t|couldn['’]?t|"
                         "won['’]?t|hardly|cannot|haven['’]?t|hasn['’]?t|"
                         "hadn['’]?t|wouldn['’]?t|shouldn['’]?t|mustn['’]?t|"
                         "needn['’]?t|ain['’]?t|daren['’]?t|shan['’]?t|"
                         "oughtn['’]?t")


# Every auxiliary says the same thing, so the list carries them all rather than the ones that
# happened to turn up: "i havent got any cheese" and "i havent got round to it" were read as an
# afternoon's work and got "How was it, overall?", because "havent" is not the word "not".
NOT_A_DAY_SAID = re.compile(r"\b(?:" + _A_NEGATIVE_AUXILIARY + r")\b")


# The news is that somebody close did something to them: lying, cheating, hiding money, an affair.
# Read on the finding-out as well as on the deed, because that is how people say it ("i found out
# hes been lying", "turns out he cheated", "i just heard shes been seeing someone else"), and the
# deed word has to be there for the finding-out to count: "i found out im pregnant" and "i found
# out hes been promoted" are news of another kind and keep their reading.
_A_TELLING_OF_WRONG = (
    r"ly(?:ing|ed)|lies|lie\b|cheat\w*|hiding|hidden|stole|stealing|steals|gambl\w*|"
    r"affair|seeing someone|texting (?:his|her|their) ex|back with (?:his|her|their) ex|"
    r"drinking again|on the (?:booze|drugs) again|using again|owed? (?:me|us) money|"
    r"borrowed money|spent (?:it|the|our|my) .{0,20}money|gone behind my back")


A_BETRAYAL_FOUND_OUT = re.compile(
    r"\b(?:i |we )?(?:just |only |now )?(?:found|find|findin[g]|turned|turn) (?:it )?out\b"
    r"[^.!?]{0,45}\b(?:" + _A_TELLING_OF_WRONG + r")\b"
    r"|\b(?:turns|turned) out\b[^.!?]{0,45}\b(?:" + _A_TELLING_OF_WRONG + r")\b"
    r"|\b(?:i )?(?:just )?(?:heard|learned|learnt|discovered)\b[^.!?]{0,40}"
    r"\b(?:s?he|they|my \w+) (?:has been|had been|was|were|is|cheated|lied|stole)\b")


# A report of an attempt at somebody is the follow-up to a trouble, not a small account of the
# day. "my neighbour keeps parking over my drive" / "i asked him nicely twice" was answered
# "Sounds alright. Anything good in it?" once #6500 added the account-of-the-day pool: "asked"
# matched the past tense, "i" is a day subject and the line is short, so a person whose complaint
# had just gone nowhere was congratulated. "i asked him nicely", "i told him twice" after a
# landlord and "i chased them again" went the same way. What separates the two is who the doing
# was aimed at: a named person with news ("i told my mum the news") is still a small day, so it
# is the pronoun object, or a count of how many times it was tried, that stands this down.
_AN_ASKING = (r"asked|told|texted|messaged|phoned|rang|called|emailed|chased|reminded|warned|"
              r"complained|spoke|talked|written|wrote")


_AN_ATTEMPT_COUNT = (r"twice|three times|four times|five times|repeatedly|again|once more|"
                     r"for the (?:second|third|fourth|fifth) time")


AN_ATTEMPT_AT_SOMEONE = re.compile(
    r"\b(?:" + _AN_ASKING + r")(?: to)?\s+(?:him|her|them|us)\b"
    r"|\b(?:" + _AN_ASKING + r")\b(?:\s+\w+){0,4}?\s+(?:" + _AN_ATTEMPT_COUNT + r")\b")


# Whose day it was decides whether the pools' question fits. The four lines ask how it went, which
# is the right question for the person's own day and the wrong one for a thing that happened to
# somebody else: "my dad left when i was 5" was answered "Good to hear. What was the best bit?",
# "my mate got killed on call of duty" "Sounds alright. Anything good in it?", and "my marriage
# ended last year" the same. A memory from childhood is not a day that has just happened either.
SOMEONE_ELSE_NAMED = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:mum|mam|mom|mother|dad|father|son|daughter|wife|husband|"
    r"partner|boyfriend|girlfriend|brother|sister|mate|friend|boss|marriage|relationship|"
    r"nan|nana|gran|granny|grandad|grandma|uncle|aunt|cousin|neighbour|neighbor|child|kid|baby|"
    r"mother-in-law|father-in-law|in-laws|"
    # An ex is somebody, and the day is theirs: "my ex moved out" was answered "Good to hear.
    # What was the best bit?" - a cheer for a person leaving - because the day pool read it as a
    # flat account of the person's own afternoon. The cards that own a separation name "wife",
    # "partner" and "flatmate", so this line had no reading above it at all.
    r"ex|ex-wife|ex-husband|ex-partner|ex-boyfriend|ex-girlfriend|"
    r"flatmate|housemate|roommate|landlord|stepson|stepdaughter|stepmum|stepdad)\b"
    r"|\b(?:someone|somebody|a man|a woman|a bloke|a lad)\b")


A_CHILDHOOD_MEMORY = re.compile(
    r"\bwhen i was (?:\d+|little|young|a kid|a child|at school|small)\b")


# The person as the doer, which is what makes the day theirs: "i told my mum the news" and "i saw
# my sister at the weekend" are days, and the pool is what keeps the second off a receipt.
THEIR_OWN_DOING = re.compile(r"\b(?:i|im|i'm|ive|i've|we|we're|weve|we've)\b")


# A visit is the person's own day even when the other person is the one who came: "my nan came
# round for tea" was answered "How was it, overall?", and the guard below must not turn that into
# a receipt ("Noted: your nan came round for tea.").
A_VISIT = re.compile(
    # "coming over" is the commonest way a visit is said, and it was missing: "my ex is coming
    # over tonight" was read as somebody else's day and stood the day question down.
    r"\b(?:came (?:round|over|by|in)|come (?:round|over)|coming (?:round|over|by)|"
    r"popped (?:round|in|over)|"
    r"stopped by|visiting|visited|rang|phoned|called|texted|facetimed|stayed over)\b")


def _a_day_of_someone_else(text):
    """True when the day belongs to somebody else, or to a childhood that is not this day.

    One predication is enough: whoever comes first in the line is the one the day is about, so
    "my husband cornered me" is his doing and "i told my mum" is hers, and a line that names no
    speaker at all ("my marriage ended", "someone drove into the back of my car") is not an
    account of the person's own day.
    """
    if A_CHILDHOOD_MEMORY.search(text):
        return True
    who = SOMEONE_ELSE_NAMED.search(text)
    if not who:
        return False
    if A_VISIT.search(text):
        return False
    mine = THEIR_OWN_DOING.search(text)
    return mine is None or who.start() < mine.start()


# Something has to have happened in the line for "how did it go" to be about it. "i asked again"
# is a follow-up about the line above, not a day, and once the complaint above it stopped taking
# the pool's line this one took it instead: "Good to hear. What was the best bit?". The subject
# and the past tense are taken out first, and what is left has to name a thing or a time.
A_BARE_MODIFIER = frozenset(
    "a an the again already too as well anyway now so just really instead back then still yet "
    "before either though even also all of it in on at to my me myself i we our for with".split())


def _a_thing_happened(text):
    """True when the line holds a thing or a time, not only a verb and a modifier."""
    doing = PAST_DOING.search(text)
    rest = text if doing is None else text[:doing.start()] + " " + text[doing.end():]
    return bool([word for word in rest.split()
                 if len(word) > 2 and word not in A_BARE_MODIFIER])


# "i got an audition", "i got tickets for the match", "i got a viewing for a flat": a thing secured
# for a day that has not happened yet. The past tense of "got" made it a small day done, so every
# one of them was asked how it went - "How did the rest of it go?", "Anything good in it?", "How was
# it, overall?" - about something still to come. Nobody knows how it went, and the question a friend
# asks is when it is.
#
# The list is the things a person secures a place in, and it stops short of the ones that come with
# a date already in the line (`DATE_AHEAD` reads those) and of a thing that is tense rather than
# good: a scan, a test or an appointment is somebody else's pool, and "i got the job" is done.
A_THING_GOT_AHEAD = re.compile(
    r"\b(?:i|we)(?:'?ve| have)?\s+(?:just\s+|finally\s+)?"
    r"(?:got|booked|secured|bagged|landed|sorted)\s+(?:myself\s+|us\s+)?"
    r"(?:a|an|the|my|our|two|three|four|some|another|front row|cheap)?\s*"
    r"(?:audition|tickets?|viewing|viewings|booking|slot|reservations?|table booked)\b")


# A day already gone takes the past tense where it belongs: "i got a viewing yesterday" happened,
# and the line says so. A parking ticket is not a place in anything, and a bus or a train ticket is
# a purchase rather than a date.
GOT_AHEAD_GONE = re.compile(
    r"\b(?:yesterday|last (?:night|week|month|year|saturday|sunday|monday|tuesday|wednesday|"
    r"thursday|friday)|this morning|earlier|the other day|on (?:mon|tues|wednes|thurs|fri|satur|"
    r"sun)day)\b", re.I)


A_MONTH = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november|"
    r"december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|weekend after next|"
    r"the \d+(?:st|nd|rd|th))\b", re.I)


GOT_AHEAD_NOT_A_DATE = re.compile(
    r"\b(?:parking|speeding|penalty|fine|fined|clamped|bus|train|plane|coach|tube|ferry|tram|"
    r"lottery|raffle|on the way)\b", re.I)


def _a_thing_got_ahead(clean):
    """The pool for a place secured in something still to come, or None."""
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return None
    if not A_THING_GOT_AHEAD.search(text):
        return None
    if GOT_AHEAD_GONE.search(text) or GOT_AHEAD_NOT_A_DATE.search(text):
        return None
    if A_MONTH.search(text) or DATE_AHEAD.search(text):
        # The date is on the line already ("i got tickets to see them in june"), so asking when it
        # is would ask for the thing just said.
        return A_BOOKING_AHEAD_DATED
    return A_BOOKING_AHEAD


# ------------------------------------------------ a problem stated and nothing else
#
# A person who says they have a problem has asked for a hand and said nothing else. Every one of
# these lines fell to a pool that could have answered any message at all: "i have a problem" and
# "ok i have a problem" got the intake form, "i have an issue" got "I'm listening - say more if it
# helps", "problem" on its own got "Thanks for telling me", and the shapes with a past tense in
# them ("i got a problem", "i have a problem i need help with") were read as a small day and asked
# about cheerfully. The offer is the one the other bare asks already get, and it is the honest
# reply: yes, and the bot needs the thing before it can help.
#
# The line has to be the whole line. "i have a problem at work" and "i have a problem with my
# neighbour" name the thing, and the reply that asks what it is would lose what they just said;
# those keep their own readings, as does anything with a verb after it ("i have trouble sleeping").
PROBLEM_STATED = re.compile(
    r"^(?:so |ok |okay |right |and |hi |hiya |hello |hey |um |er |honestly |well |but )*"
    r"(?:(?:i|we)(?:'?ve|'?m| have| am| got|'?ve got)\s+|there (?:is|'?s) |theres |its |"
    r"it'?s )?"
    r"(?:a |an |one )?"
    # "a bit of a problem", "a small problem", "quite a problem": the size is part of saying it,
    # not the thing itself, so it does not stop the offer.
    r"(?:(?:bit of a|small|big|massive|real|proper|slight|little|serious|tiny|huge|nasty|"
    r"right|bit of|wee|awkward) )?"
    r"(?:problem|issue|trouble)"
    r"(?: (?:here|really|actually|now|again|too|i (?:need|could do with) (?:some )?help(?: with)?|"
    r"that i (?:need|could do with) (?:some )?help(?: with)?|i (?:need|could do with) "
    r"(?:some )?advice))?$")


# The same offer for the other half of the same line: something is up and the person has not said
# what. "something is wrong" got the intake form, "theres something wrong" and "something is
# bothering me" got "I'm listening - say more if it helps", and "something happened" got "Thanks
# for telling me - I'm here if you want to dig into any of that".
SOMETHING_UP = re.compile(
    r"^(?:so |ok |okay |right |and |hi |hello |hey |um |er |honestly |well |but )*"
    r"(?:"
    # "something is wrong", "theres something up", "something really is not right"
    r"(?:there (?:is|'?s) |theres )?"
    r"(?:(?:something|somethings|sommat|summat)(?: really| bad| weird| odd| serious| not right)?"
    r"(?:'?s)? )?"
    r"(?:is |was |keeps )?"
    r"(?:wrong|up|not right|off|the matter)"
    # "something happened", "something's gone wrong", "something has come up"
    r"|(?:something|somethings|sommat|summat)\s+(?:has |had |just )?"
    r"(?:happened|gone wrong|come up)"
    # "something is bothering me"
    r"|(?:something|somethings|sommat|summat)\s+(?:is |was |keeps )?"
    r"(?:bothering|worrying|upsetting|bugging|nagging)\s+me"
    r")"
    # The line has to end there. "something is wrong with my car" names the thing, and the offer
    # would lose it; a time or a place after it ("something happened at work yesterday") still says
    # nothing about what it was, so those are allowed.
    r"(?: (?:here|today|yesterday|tonight|last night|this morning|this week|at work|at home|"
    r"again|right now|at the moment)){0,2}$")


def _a_problem_stated(clean, repaired=None):
    """True when the line is a statement of a problem and nothing else.

    Both the line as typed and the reading's repaired text are tried, for the same reason
    `_asks_for_help` tries both: the reader puts the words back ("i hav a problem" -> "i have a
    problem", "ive got a problm" -> "i've got a problem"), and the patterns are written for
    ordinary words.
    """
    for line in (clean, repaired):
        bare = " ".join(re.sub(r"[^a-z0-9 ]+", " ", str(line or "").lower()).split())
        if bare and (PROBLEM_STATED.match(bare) or SOMETHING_UP.match(bare)):
            return True
    return False


# A line can ask what to put on and still name the day: "office has gone casual but the clients are
# in suits, what do i wear", "climbing for the first time saturday, what should i wear". The wear
# pool is written for the ask on its own (`BARE_PICK` wants the whole line to be the ask), no
# clothes row answers those occasions, and nothing else reads a clothes question - so the person
# got the search hedge, "I'd rather not guess. A quick search online will get you a solid answer",
# for the one kind of question this file can still say something true about.
# "put on" is deliberately not here: "what should i put on" is a moss killer on the lawn and a cream
# on a cold sore far more often than it is clothes, and answering those with a layer you can take
# off is the confident wrong frame this pool exists to avoid. Only the words that can only be
# clothes are in it.
WEAR_ASK = re.compile(
    r"\b(?:what|which|how)\b[^.?!]{0,40}?\b(?:wear|wearing|dress code|outfits?)\b", re.I)


# The rule that decides it, then the one question that narrows it: not a fact to look up, and not
# a guess about the occasion either. Each line leads with what is true of any day (the weather,
# how long you are on your feet, how the room is dressed) before it asks.
WEAR_WHEN_NOTHING_ANSWERS = (
    "Clothes come down to the weather and how long you are standing about: a layer you can take "
    "off, and shoes you can spend the day in. Is it indoors or out?",
    "Go off the room rather than the label - one notch up from what most people there will have "
    "on, and a layer to shed if you are the only one dressed up. Cold where you are?",
    "Dress for the coldest hour of it and the longest you will be on your feet: shoes decide "
    "more of a day than people expect. Are you inside or out?",
)


# "i have nothing to wear" is the same kind of line one step further from an ask: nothing in the
# tables answers it - it names no occasion - and it reached the echo ("Thanks for telling me - I'm
# here if you want to dig into any of that"), which is the reply that would fit any message at
# all. It is a clothes line and it is nearly always about the choice rather than the wardrobe, so
# the rule and the one question are the honest reply here too.
NOTHING_TO_WEAR = re.compile(
    r"\b(?:nothin|nothing|nowt)\b\s+(?:at all\s+)?to\s+(?:wear|put on)\b|"
    r"\b(?:nothin|nothing|nowt)\s+fits\b", re.I)


NOTHING_TO_WEAR_REPLIES = (
    "Nothing to wear usually means nothing you fancy - pick the one thing you feel good in and "
    "build the rest round it. What is the day?",
    "Everyone has nothing to wear the night before. Is it work, a meal out, or a long walk?",
    "Then wear the one you always skip and keep everything else plain. What is it for?",
)


def _says_there_is_nothing_to_wear(clean, repaired=None, text=None):
    """True when the line says there is nothing to put on, with no occasion named in the tables."""
    for line in (clean, repaired, text):
        said = " ".join(str(line or "").lower().split())
        if said and NOTHING_TO_WEAR.search(said):
            return True
    return False


def _a_wear_ask_about_a_day(clean, repaired=None, text=None):
    """True when the line asks what to put on and has a day to put it on for.

    The ask has to be part of a longer line, because the ask on its own is `_bare_pick`'s and
    already has its pool; this is the line that says the occasion first and asks after.

    All three readings are tried: `clean` is the line with the filler taken out and the ask read
    off it, so "im going to a do at the golf club and i have no idea what to wear" arrives here
    as the occasion alone and the ask in `understood["ask"]`, and only `text` still has both.
    """
    for line in (clean, repaired, text):
        said = " ".join(str(line or "").lower().split())
        if not said or not WEAR_ASK.search(said):
            continue
        rest = WEAR_ASK.sub(" ", said, count=1)
        if re.findall(r"[a-z']{2,}", rest):
            return True
    return False


# The weather as a number: "40 degree heat", "35 degrees", "minus 5". The pools above read the
# weather by the word for it ("it is boiling"), which is how a person says it when they are
# standing in it, and a line that says the figure instead ("what to wear in 40 degree heat") has
# no word in it at all, so it took the general pool and heard "dress for the coldest part of the
# day" in a heatwave. A figure needs the word degrees or a unit beside it, because "40" alone is
# an age, a run, or a bill.
HOT_FIGURE = re.compile(
    r"\b(?:\d{2})\s*(?:degrees?|°|c\b)|\b(?:minus|below)\s+(?:\d{1,2}|zero)\b|"
    r"\b(?:heat|heatwave|warm spell)\b", re.I)


# The sun said as a consequence rather than a temperature: "i burn in ten minutes" is a clothes
# line about heat, and answering it with layers for the cold is a confident wrong guess. A beach is
# the same day said another way.
WEATHER_SUN = re.compile(
    r"\b(?:sunburn\w*|sunbathe?\w*|sunny|sun cream|sunscreen|factor\s*(?:15|20|30|50)|"
    r"beach|blazing|scorching sun)\b|\bburn(?:s|t)? in (?:\w+ )?minutes?\b", re.I)


COLD_FIGURE = re.compile(
    r"\b(?:freezing|frost|snow|sleet|chilly|bitter(?:ly)?)\b|"
    r"\b(?:minus|below)\s+(?:\d{1,2}|zero)\b", re.I)


def _the_wear_pool_for_the_line(clean, repaired=None, text=None):
    """The wear pool that fits the weather the line itself named, or the general one."""
    said = " ".join(" ".join(str(line or "").lower().split())
                    for line in (clean, repaired, text))
    if WEATHER_WET.search(said):
        return BARE_PICK_WEAR_WET
    if COLD_FIGURE.search(said) or WEATHER_COLD.search(said):
        return BARE_PICK_WEAR_COLD
    if HOT_FIGURE.search(said) or WEATHER_HOT.search(said) or WEATHER_SUN.search(said):
        return BARE_PICK_WEAR_HOT
    return WEAR_WHEN_NOTHING_ANSWERS


# A thing named as bad is not a flat account of a day, whatever the rest of the line looks like.
# "i got some bad news" was answered "Nice one. How did the rest of it go?" and "i got some good
# news" is the only line of that pair the pool is for. The word in front of the noun is what
# decides, so the shape is the modifier and the thing; "not bad" never reaches here, and a thing
# that is bad in a way worth naming ("a bad back", "the bad knee") is not in this list because it
# is a body part and the pools above have their own reading of it.
A_BAD_THING_NAMED = re.compile(
    r"\b(?:bad|sad|awful|terrible|dreadful|grim|rotten|lousy|horrible|horrid|rubbish|tough)\s+"
    r"(?:news|tidings)\b")


# Somebody asking for help is asking for it now, not reporting a day: "i asked for help" got
# "Sounds alright. Anything good in it?". The pool is for what happened, so it stands aside and
# the pools below are free to answer the ask.
A_HAND_OUT = re.compile(
    r"\b(?:asked|ask|asking|looked|looking|reached|reaching)\s+(?:for|out for)\s+"
    r"(?:help|support|a hand|some help)\b")


# A day with a thing gone wrong in it is not a day to ask about cheerfully, and the words for
# the things that go wrong are their own list: a crash, a burglary, a theft. "we got burgled last
# night" was answered "Sounds alright. Anything good in it?", "someone nicked my bike last week"
# "Good to hear. What was the best bit?" and "my car got keyed at the weekend" "Nice one. How did
# the rest of it go?" - the pool for a flat account of a day cannot tell a good afternoon from a
# burglary by the shape of the line, so it is the nouns that have to stop it.
# Nothing here is a word that is also said of something good: "crashed out" is an early night,
# "smashed it" and "smashed my pb" are a job well done, and "flooded with" is orders coming in,
# so the phrases are written out rather than left as bare verbs.
# The nouns above only cover the mishaps somebody has already named for us, and the same day is
# told as the verb far more often ("i got pickpocketed on the bus", "my dog ran off yesterday",
# "i chipped a tooth eating a toffee", "my phone cracked yesterday", each congratulated). The
# reading of a thing done to the person or to a thing of theirs is the remark module's setback,
# so it is asked for there rather than written out twice.
A_DAY_WENT_WRONG = re.compile(
    r"\b(?:burgl\w*|broken into|broke into|break-in|break in|robbed|robbery|mugged|mugging|"
    r"stolen|stole|theft|shoplifted|nicked|pinched|keyed|vandalised|vandalized|scratched the car|"
    r"written off|wrote it off|wrote the car off|caught fire|went on fire|on fire|burst pipe|"
    r"water damage|smoke damage|gone missing|went missing|disappeared|vanished|"
    r"crash|car crash|had a prang|a prang|in a smash|was rear-ended|rear-ended|hit by a car|"
    r"fell off|come off my bike|came off my bike|fell down the stairs)"
    r"\b|\bcrash(?:ed)?\b(?!\s+out)\b|\bflood(?:ed)?\b(?!\s+with)\b")


# "it was yesterday", "that was in march", "it was lifting the shopping": the subject is a
# pronoun standing in for the line before, so the line says nothing about a day of its own. Only
# a pronoun that has something to point at counts - on its own, with nothing before it, there is
# no "it" to be a detail about, and the line is left to the reading it would have had.
# A reply that opened on sympathy is the bot's own reading that something bad was said, which is
# the reading a detail added to it must not be congratulated.
_A_SYMPATHY = re.compile(r"\b(?:sorry|condolences|sad news|real loss)\b")


# A body that was ill is a trouble the reading above does not name: "my son was ill all week" is
# not a wrong day or a harm, and "ill" is too common to add to the day list.
_A_BODY_UNWELL = re.compile(r"\b(?:ill|illness|unwell|poorly|sick|infection)\b")


_A_DETAIL_OPENING = re.compile(r"^(?:it|that|this|there)\s+(?:was|were|is|had|happened)\b")


# A line that points back at the person's own earlier words is a correction to what is already on
# the table, not a new account of a day: "and i said it only started since may" was congratulated
# ("Good to hear. What was the best bit?") on the turn after an answer that ended in a question.
# The pronoun in the clause is what makes it a back-reference - "i said no to the offer" is a day
# with a decision in it, and keeps the pool.
A_LOOKING_BACK = re.compile(
    r"^(?:and\s+|but\s+|so\s+|well\s+)?(?:like\s+|as\s+)?i\s+(?:already\s+|did\s+)?"
    r"(?:said|told\s+you|mention\w*)\b"
    r"[^.!?]{0,50}?\b(?:it|that|this)\s+(?:only\s+|just\s+|actually\s+|never\s+)?"
    r"(?:was|were|is|had|started|began)\b",
    re.I,
)


def _a_detail_about_what_was_said(text, memory):
    """True for a clause that only adds to the line before it: "it was yesterday".

    The pleasantry this stands down is the answer to a question about a day, so it is kept when
    the bot has just asked one: "how was it, overall?" then "it was ok" is the answer, not a
    detail. What makes the line a detail is that the answer before it was advice or sympathy -
    the bot was talking about the ankle, not asking about the day.
    """
    if not _A_DETAIL_OPENING.match(text):
        return False
    turns = [turn for turn in ((memory or {}).get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return False
    last_bot = str(turns[-1].get("bot") or "")
    if _in_a_pool(last_bot, (A_SMALL_DAY,)):
        return False
    # What went before has to be a trouble, because a detail about a good thing ("i finished a
    # book last week" / "it was a thriller, set in norway") is the pleasantry's own line and
    # "got it - it was a thriller, set in norway" is worse than asking how it went. The trouble is
    # read off the line before and off the bot's own answer to it: a body part or a harm word, a
    # failure, a day that went wrong, or a reply that opened on sympathy for a death.
    if _A_SYMPATHY.search(last_bot.lower()):
        return True
    before = " ".join(str(turns[-1].get("user") or "").lower().split())
    return any(reading.search(before)
               for reading in (HARM_ANYWHERE, NEGATIVE_LINE, BAD_DAY_ANYWAY,
                              A_DAY_WENT_WRONG, _A_BODY_UNWELL))


# Being treated badly by another person is not a small account of the day to ask about warmly.
# "my son is being called names" was answered "Good to hear. What was the best bit?" and "i got
# called names at work" "How was it, overall?": the line is a subject, a past tense and a day, so
# the shape fits the pool, and only the words say that something was done to the person rather
# than by them. Every phrase here names who it was done to, because the same verbs the other way
# round are ordinary ("they called me a taxi", "we laughed at the film", "i teased my brother
# about his hair").
SOMEONE_DONE_WRONG = re.compile(
    r"\b(?:called (?:me|him|her|them|us) names|"
    r"call (?:me|him|her|them|us) names|"
    r"called names|name[- ]calling|called (?:me|him|her|them|us) a \w+ name|"
    r"got called names|got called (?:a |an |the )?(?:\w+ )?names?\b|"
    r"(?:was|were|is|are|being) called (?:a |an |the )?(?:\w+ )?names?\b|"
    r"teased (?:me|him|her|them|us)|teasing (?:me|him|her|them|us)|"
    r"bullied|bullying|bullies|"
    r"picked on|picking on|picked last|picking (?:me|him|her|them) last|"
    r"left (?:me|him|her|them|us) out|leaving (?:me|him|her|them|us) out|"
    r"laughed at (?:me|him|her|them|us)|laughing at (?:me|him|her|them|us)|"
    r"made fun of (?:me|him|her|them|us)|making fun of (?:me|him|her|them|us)|"
    r"mean to (?:me|him|her|them|us)|nasty to (?:me|him|her|them|us)|"
    r"horrible to (?:me|him|her|them|us)|"
    r"(?:would|wouldnt|wouldn't|wont|won't|didnt|didn't) let (?:me|him|her|them) play|"
    r"nobody (?:will|would|wants to) play with|"
    r"snatched (?:it|the \w+) (?:off|from) (?:me|him|her|them))\b")


# What makes an account of the day something to ask about rather than to answer: the day went
# wrong in a way that has no reading of its own above.
BAD_DAY_ANYWAY = re.compile(
    r"\b(?:hospital|a&e|ambulance|fell over|a fall|funeral|died|death|test results|biopsy|"
    # A thing that fell on the person, said with the speaker as the subject: "i had a car crash
    # last year" and "we had a flood in the kitchen" are not a day to ask how the best bit was.
    r"crash|crashed|accident|collision|flood|flooded|burst pipe|fire|burgled|robbed|stolen|"
    r"wrote off|killed|killing|(?:massive|big|huge|proper|right|awful|terrible) row|"
    r"row (?:about|over|with)|"
    r"chemo|miscarriage|evicted|lost my job|sacked|fight|row with|panic|anxiety attack|ticket|"
    # The drug that starts when the treatment stops is not a day to ask about cheerfully either:
    # "they put my dad on morphine" was answered "Nice one. How did the rest of it go?" and
    # "they started my mum on morphine" "How was it, overall?". The reading is in the loss
    # composer (`says_the_last_drug`), and this list is the fence under it, for the shapes it
    # does not read.
    r"morphine|diamorphine|midazolam|syringe driver|palliative|end of life|hospice|terminal|"
    r"clamped|fined|argued|argument|shouted|cried|upset|worried|worries|sick|threw up|migraine|"
    r"rained|soaked|drenched|wet through|late for|missed my|missed the|clinic|dentist|surgery|"
    r"wrong|mistake|messed up|screwed up|"
    r"waited|waiting|queued|queue|on hold|hung around|hung about|two hours|three hours|"
    r"four hours|an hour|all night|"
    r"headache|aching|exhausted|shattered|knackered|gutted|a row|an argument|strange|grim|"
    r"full on|fell flat|meh|"
    # The ride they came off, the thing they smashed, the wing mirror someone took off: a mishap
    # is a day that went wrong even when the line has no word for harm in it.
    r"came\s+off|smashed|smash|flooded|flooding|"
    r"stacked\s+it\b|stacked\s+(?:my|the|his|her|their)\s+"
    r"(?:bike|motorbike|moped|scooter|motorcycle|car|van|horse)\b|"
    r"wrecked|dented|chipped|snapped\s+(?:at|my|the|his|her|their)\b|"
    # A thing of theirs that stopped working, burned, or came apart in front of them: no word
    # here is a word for harm, so the line has the shape of a day and nothing in the mood reads
    # it - "my toast went up in flames" was answered "Nice one. How did the rest of it go?" and
    # "the website collapsed when we launched" "How was it, overall?".
    r"went up in flames|caught fire|blew up|blew a fuse|went bang|collapsed|fell apart|"
    r"packed in|conked out|stopped working|wouldnt start|wouldn't start|broke down|leaking|"
    # Something that was meant to come back well and came back worse, and something of theirs
    # shut: "the mortgage valuation came back 5k under our offer" was congratulated, and the
    # park at the end of a road being closed is a nuisance rather than a day to ask the best bit
    # of. "i closed the shop" is a day's work and keeps the cheer, which is why the verb has to
    # be the one the thing itself carries.
    r"came back (?:short|lower|worse)|under (?:our|the) (?:offer|asking)|over budget|"
    r"went over budget|(?:is|are|was|were) (?:still )?closed|"
    # Somebody telling the person off rather than the person telling a story: the same shape as
    # the haircut, so only these words separate them. ("it kicked off" is the same news and is
    # read a step earlier, in `A_DAY_SAID_BADLY`, because it wants the sympathetic question and
    # not the neutral one.)
    r"told\s+[^,.;!?]{0,25}?\boff\b|had a go at me|had a right go|"
    # A penalty put on the thing they parked, and a body or an animal that came a cropper in a
    # way that names no harm: "they put a boot on my car", "my cat fell in the paddling pool",
    # "i was short of breath earlier". "fell in love" is the one phrase the middle one would
    # take by mistake, and it is excluded by name.
    r"boot on (?:my|the|our) (?:car|van|motor|bike)\b|fell in (?!love)|"
    r"choked(?!\s+up)|short of breath|"
    # A thing marked or spoiled rather than broken ("my kettle is blackened on the bottom"), and a
    # mistake they made at work ("i keep slipping up at work and im confused"): neither names any
    # harm, and both were congratulated.
    r"blackened|burnt|burned|scorched|stained|rusted|scratched|slipping up|slipped up|"
    r"messed up|mucking up|mucked up|"
    r"knocked\s+over|tipped\s+over)\b")


FOOD_TOPICS = frozenset(("cooking", "food-and-drink"))


def _a_dish_name(clean, words, memory):
    """Is this line the name of a dish rather than a report of something done?

    Asked of the understanding engine's own reading, not of a word list: a line it read as
    cooking or food-and-drink is a subject the knowledge base answers, and "packed lunch for a
    vegan" is a question about lunch however it opens.
    """
    if len(words) < 2 or words[0] not in DISH_PARTICIPLE:
        return False
    if words[1] in DISH_DETERMINER:
        return False
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    topics = set(understood.get("topics") or ())
    if isinstance(understood.get("topic"), str):
        topics.add(understood["topic"])
    return bool(topics & FOOD_TOPICS)


# The arbiter reads this before the never-repeat fallback (README.md, "Interface"). Three kinds
# of line have no words of their own to match, and only the composer reads them: a line that is
# nothing but a report on the advice just given ("its not helping", "no change yet", "i did what
# you said"), a bare "why" after a substantive answer (bot/compose/why.py), and a bare hand-off -
# "one more thing", "quick one" - which announces something and has not said it yet
# (bot/compose/handoff.py). A line that says it did what was said and got nowhere is the most
# useful thing a person can say in an advice thread, and the chat module otherwise answers it with
# the line back or a stock "Alright then - good luck with it."
def _repaired_of(text, memory):
    """The line with its chat-speak put right, as the reading made it, or "" for none.

    The reading is the arbiter's own (`memory["understood"]`) when it is this turn's, so the
    router asks for no second reading of the line; a reading that fails claims no repair.
    """
    try:
        read = memory.get("understood")
        if isinstance(read, dict) and read.get("plain"):
            return str(read["plain"])
        read = understand(text, memory)
        return str((read or {}).get("plain") or "")
    except Exception:  # noqa: BLE001 - no repair, and the typed line still reads
        return ""


# A name is not an afternoon's work: "my kids are called jack and emma" and "my mother-in-law is
# called june" opened with a subject and a past tense and were asked how the day went ("Nice one.
# How did the rest of it go?").
A_NAME_IS_NOT_A_DAY = re.compile(r"\b(?:is|are|was|were)\s+(?:called|named)\b")


# The name reader in remark.py has a line for one of them - "my sister is called rose" -> "Rose —
# noted with care. What does she make of it?" - but the collective shapes (kids, parents, the
# in-laws) and a person word with an adjective in front ("my new boss") are not in its patterns.
# Standing the cheer down alone put those on the store's read-back ("Noted: your kids are called
# jack and emma."), which is the restatement STYLE.md opens with, so the names are said back the
# way a person would say them and one question about the people is asked: with nothing known
# about them, that is the whole of the warm reply available.
A_NAMES_TOLD = re.compile(
    r"\bmy\s+(?:(?:new|old|little|big|eldest|youngest|middle|first|second|step|ex|late)\s+)?"
    r"(?P<person>[a-z][a-z'-]{1,20})\s+(?:is|are|was|were)\s+(?:called|named)\s+"
    r"(?P<names>[a-z][a-z'-]{0,20}(?:\s*(?:,|and|\s)\s*[a-z][a-z'-]{0,20}){0,3})"
    # A name with something said after it ("my mum is called janet and shes 72", "my sister is
    # called rose and she lives in leeds"): the figure or the place is the name reader's own line
    # where it reads the shape, and where it does not the name is still the whole of what this
    # pool needs - the receipt that would otherwise be said back says less than the name does.
    r"(?:\s+(?:and|,)?\s*(?:she|he|they|it)s?\b[^.!?]{0,80})?\s*$")


# A name the whole household answers to ("we are called the smiths", "they were called the
# williams"): there is no person word to take a pronoun from, so the question is about the name.
A_NAME_A_HOUSEHOLD_TAKES = re.compile(
    r"\b(?:we|they)\s+(?:are|were)\s+(?:called|named)\s+"
    r"(?P<names>[a-z][a-z'-]{0,20}(?:\s*(?:,|and|\s)\s*[a-z][a-z'-]{0,20}){0,3})\s*$")


# A word after "called" that names nobody: "my son is called after me", "my car is called it".
NOT_A_NAME_WORD = frozenset((
    "the", "a", "an", "it", "its", "that", "this", "him", "her", "them", "me", "after",
    "something", "nothing", "whatever", "what", "which", "who", "but", "and",
    "she", "hes", "he", "they", "we", "us", "his", "hers", "theirs", "is", "was", "were",
))
