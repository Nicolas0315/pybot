"""Part 1 of 5 of the module, split out of `fallback_chain`.

Everything here is re-exported from `fallback_chain`, so callers import it from there as before.
"""

import re
from ..understanding.body import GOING_BOTH_WAYS
from . import DOUBT, DOUBTED, turns_round
from .limit import NOTHING_THAT_LIMITS
from . import loss, no_eyes
from .fallback_data import (
    ABOUT_WORDS, BAD_STRETCH, BODY_ALSO, BODY_LEAD, BODY_PART_QUALIFIER, BODY_PART_TAIL,
    BODY_SITUATION, BODY_STATES, BODY_TAIL, CROWD, HABIT_ACT, HOUSE_VERB, NEGATORS, PERSON_WORDS,
    STRETCH_OF_TIME, YOU_SUBJECTS, _WAS,
)

# The day that went badly and the name that came from somebody: the pools those readings choose
# from. They are in the data file with the rest, and the readings that use them live here.
from .fallback_data import HABIT_PROBLEM_ACT

# What the moved rows take from fallback.py, which is fully defined by the time this
# module is imported, because fallback.py imports it from its own last line.
from .fallback_part_01 import EMERGENCY_CALL, POLICE_CALL
from .fallback_part_14 import BODY_PART, _opens_a_question
from .fallback import (
    ABOUT_WORDS, BAD_STRETCH, BODY_ALSO, BODY_LEAD, BODY_PART_QUALIFIER, BODY_PART_TAIL,
    BODY_SITUATION, BODY_STATES, BODY_TAIL, CROWD, DOUBT, DOUBTED, GOING_BOTH_WAYS, HABIT_ACT,
    HABIT_PROBLEM_ACT, HOUSE_VERB, NEGATORS, PERSON_WORDS, STRETCH_OF_TIME, YOU_SUBJECTS, _WAS,
    loss, no_eyes, re, turns_round,
)



# "i feel cold" says the same as "i am cold": a state a person feels is the state they are in,
# and the words people type for feel are "feel", "feeling" and the -in spelling that the
# normaliser already reads back to "feeling" ("i feelin cold"). Only the word in the middle of
# "i ___ cold" is read here, so "my hands feel cold" keeps its own reading, and the state word
# still has to be the whole rest of the line - "i feel cold toward him" carries a person after
# it and stays out. A standing complaint that already has a card ("i feel cold all the time")
# keeps the card, because a knowledge row answers before these pools do.
FEEL_COPULA = frozenset(("feel", "feeling"))


def _body_state(clean):
    """Which body state the whole line is ("cold", "hot", "hungry", "thirsty"), or None.

    Only a line that is the state and nothing else comes here: "im cold" is this reading, and
    "im cold water" and "im boiling eggs" are things rather than states. A question is not a
    report of one ("im cold?" is a person checking they said it), and a line with "but" in it
    is a mixed one the trouble and feeling pools answer better.
    """
    if "?" in clean or " but " in clean or " not " in clean:
        return None
    # Two of these are said as two words far more often than one: "light headed" and "bunged
    # up" (also written "light-headed" and "bunged-up"). Joined here so the state is one word
    # and the rest of the line reads the same as the single-word version.
    flat = clean.replace("light-headed", "lightheaded").replace("light headed", "lightheaded")
    flat = flat.replace("bunged-up", "bungedup").replace("bunged up", "bungedup")
    flat = flat.replace("blocked-up", "blockedup").replace("blocked up", "blockedup")
    words = [w.strip(".,!?;:") for w in flat.split()]
    words = [w for w in words if w]
    if not words or _opens_a_question(words):
        # "am i hungry", "why am i so cold" ask about the state rather than reporting it.
        return None
    for index in range(len(words) - 1):
        if words[index] not in ("im", "i'm", "am", "iam") and not (
                words[index] == "i" and (words[index + 1] == "am"
                                         or words[index + 1] in FEEL_COPULA)):
            continue
        # The state is the whole of what they said, so nothing of substance comes before it:
        # "do you think im cold" asks about the reading and "he said im cold" is reported
        # speech, and neither is a person saying how they are.
        if any(w not in BODY_LEAD for w in words[:index]):
            continue
        start = index + 2 if words[index] == "i" else index + 1
        # Hot and cold in one breath is a fever, not the weather: "im hot and cold" and "im
        # cold then hot" are one symptom going both ways, and the practical pool would tell
        # someone shivering to open a window. The temperature reading keeps those lines. The
        # shape is that reading's own, so a hot person next to a cold thing - "im hot and the
        # pool is cold" - is not read as going both ways.
        if GOING_BOTH_WAYS.search(clean):
            return None
        state, after = _state_from(" ".join(words[start:]))
        if state:
            return state
    part_state = _a_part_in_a_state(clean)
    if part_state:
        return part_state
    return None


def _a_part_in_a_state(clean):
    """Which body state the line says of a part of them, or None: "my hands are clammy".

    A nose or an ear has no answer of its own, so a cold one is the person being cold, and the
    same goes for a clammy hand or a pale face: the pools answer a state of the body, not only a
    state said with "im", so "my hands are clammy" gets the line "im clammy" gets. The state word
    can come after a qualifier ("my nose is really cold", "my hands are a bit clammy") and can be
    said twice ("my nose is freezing cold"), which is how people say it; anything else in the line
    before the state word ("my ears are red and cold") says something else is going on, and anything
    after it ("my face is pale and i feel sick") makes it more than a state, so both keep
    whatever reading they had.
    """
    part = BODY_PART.search(clean)
    if not part:
        return None
    words = [w.strip(".,!?;:") for w in part.group("rest").split()]
    words = [w for w in words if w]
    for index, word in enumerate(words):
        state = _the_state(word)
        if not state:
            if word not in BODY_PART_QUALIFIER:
                return None
            continue
        # A part being hot is the part, not the person: a hot forehead is a fever question and
        # sweaty hands are as often nerves as a warm room, so the heat pool's "open a window" is
        # not the answer to either. The states the pools read from a part are the ones a friend
        # reads the same way whichever words carry them.
        if state == "hot":
            return None
        # Everything after the state word has to be nothing, a time word, or the same thing said
        # again ("freezing cold", "cold and freezing").
        rest = [w for w in words[index + 1:] if w != "and"]
        if all(w in BODY_PART_TAIL or _the_state(w) == state for w in rest):
            return state
        return None
    return None


def _a_part_is_cold(clean):
    """The old name for the same reading, kept because the export list in fallback.py names it.

    It answered only a part being cold ("my nose is freezing"); it reads any state a pool answers
    now, so the name says less than the function does.
    """
    return _a_part_in_a_state(clean) == "cold"


def _state_from(rest):
    """(state, words after it) for the state the rest of the line names, or (None, []) ."""
    if not rest:
        return None, []
    words = [w.strip(".,!?;:") for w in rest.split()]
    for index, word in enumerate(words):
        state = _the_state(word)
        if not state:
            continue
        tail = words[index + 1:]
        # "im really very cold" and "im so cold" are the same line, so the qualifiers before
        # the state word say nothing about what follows it.
        if tail and tail[0] == "and" and len(tail) == 2 and tail[1] in BODY_ALSO:
            return state, []
        if not tail or all(w in BODY_TAIL for w in tail):
            return state, tail
        if " ".join(tail) in BODY_SITUATION:
            return state, tail
    return None, []


def _the_state(word):
    """The body-state name for this one word, or None."""
    for name, pool in BODY_STATES.items():
        if word in pool:
            return name
    return None


HABIT_STATED = re.compile(
    # Only the person's own "i" and the "we" of a couple: another adult's habit is not theirs to
    # account for ("my husband always leaves his clothes on the floor" is a grumble about him, and
    # what is being asked here - what sets it off, what has been tried - asks the speaker to
    # explain somebody else's doing).
    r"\b(?:i|we)\s+(?:(?:always|never)\s+" + HABIT_ACT +
    r"|(?:keep|keeps|end\s+up|ends\s+up|can'?t\s+stop|cant\s+stop)\s+" + HABIT_ACT +
    r"|(?:tend|tends)\s+to\s+" + HABIT_ACT +
    # "i never get round to it" is the habit itself, said as a standing excuse.
    r"|never\s+get\s+round\s+to\b" +
    r")"
    r"|\b(?:im|i'?m)\s+always\s+" + HABIT_ACT +
    # A part of the body or the mind named with "my" is the person themselves: "my brain keeps
    # going blank" is their own pattern. Any other "my <person>" is somebody else and stops here.
    r"|\bmy\s+(?:brain|mind|memory|head|hands?|eyes?|stomach|skin|body|voice|mood|sleep|"
    r"focus|concentration|attention|nerves|anxiety|appetite|breathing|gut|bladder|jaw)\s+"
    r"(?:keeps|always|never)\s+" + HABIT_ACT, re.I)


# Being left out is not a habit to take apart: "i never get invited anywhere" is other people's
# doing, and asking what sets it off blames the person for it.
HABIT_NOT = re.compile(r"\b(?:never\s+get\s+(?:invited|asked|picked|chosen|included)|"
                       r"left\s+out|no\s+one\b|nobody\b|"
                       # "i always do this" says nothing to ask about yet - there is no "this"
                       # in the line for the bot to know, and the question reads as if it did.
                       r"\b(?:always|never)\s+do(?:es)?\s+(?:this|that|it)\b|"
                       r"\b(?:always|never)\s+late\b|"
                       # "i keep going back to him" is an on-off relationship, not a habit to
                       # take apart - what sets it off is not what the person needs to answer.
                       r"\b(?:going|go|went|running|run)\s+back\s+to\s+(?:him|her|them)\b|"
                       r"\bnever\s+(?:hear|heard|see|saw|seen|win|won)\b)", re.I)


# Said out loud, they mind it, so the doing need not be on the list: "i wish i could stop biting my
# nails", "it drives me mad".
HABIT_MIND_IT = re.compile(
    r"(?:i\s+wish|can'?t\s+stop|cant\s+stop|want\s+to\s+stop|need\s+to\s+stop|"
    r"trying\s+to\s+stop|drives\s+me\s+(?:mad|crazy|nuts|up\s+the\s+wall)|"
    r"bothers\s+me|gets\s+to\s+me|sick\s+of|fed\s+up|i\s+hate\s+that|shouldn'?t|"
    r"shouldnt|i\s+feel\s+bad|i\s+feel\s+guilty|upsets\s+me|i\s+do\s+it\s+again)", re.I)


def _habit_is_a_problem(clean):
    """Whether the repeated doing is one a person would want a hand with."""
    return bool(HABIT_PROBLEM_ACT.search(clean) or HABIT_MIND_IT.search(clean))


# "the weather is horrible today" has a bad word next to a stretch of time, but it is a claim
# about a thing out in the world rather than about how the person is: "that is a lot to hold" is
# too much for a wet afternoon. A thing named with "the" at the front of the clause is the one
# the bad word belongs to, so the stretch reading stays off it; "my week has been rough" and
# "bit of a rubbish week" keep it.
NOT_ABOUT_THEM = re.compile(r"\bthe\s+([\w']+)\s+(?:is|was|are|were|gets|looks)\s*$")


def _a_claim_about_a_thing(before):
    """True when the bad word belongs to a thing named with "the" ("the weather is ...").

    A stretch of time is the exception: "the week was rubbish" and "the day was awful" are how
    people say it went for them, so the noun after "the" has to be something other than time.
    """
    found = NOT_ABOUT_THEM.search(before + " ")
    return bool(found) and found.group(1) not in STRETCH_OF_TIME


# The verb a line opens with when it tells someone to do a job: "take ...", "put ...", "book ...",
# and the polite wrappers people put in front of it. The line has to open with it, so a question
# that merely contains one of these words ("how do i turn the heating down") is not read here.
ACT_OPENER = re.compile(
    r"^(?:please\s+|ok\s+|okay\s+|right\s+|so\s+|hi\s+|hello\s+|hey\s+|and\s+|"
    r"(?:can|could|would|will)\s+you\s+(?:please\s+)?)*"
    r"(?:take|put|get|bring|grab|turn|set|fill|switch|open|lock|wash|hoover|tidy|clean|post|"
    r"feed|walk|make|book|reserve|order|call|ring|phone|text|email|buy|pay|renew|"
    # A job asked flat, with no house word in it: "search for flights for me", "send me the
    # recipe", "sign me up for the class", "keep an eye on the oven for me". The verb alone does
    # not make them an order - "search for a cheap flight" and "pick the kids up from school" are
    # the person's own errand - so each is claimed only with the "for me" or "me a" that the
    # ACT_FOR_ME test below asks for.
    r"send|search|sign|pick|save|keep|chase|look|find)\b")


# A thing in the house or a person to ring: the object that makes the verb an act in the world
# rather than a thing to work out. "make me a shopping list" and "pay the gas bill" have neither,
# so they keep the answer their entry gives.
ACT_THING = re.compile(
    r"\b(?:rubbish|bins?|bin\s+bags?|kettle|cuppa|tea|coffee|oven|heat|heating|thermostat|"
    r"alarm|washing|laundry|dishes|door|window|windows|light|lights|lamp|water|bottle|table|"
    r"taxi|cab|appointment|doctor|dentist|gp|surgery|prescription|milk|bread|paper|"
    r"post|parcel)\b")


# Who the line is said to. A bare "put the kettle on" is said to whoever is nearest, and the bot is
# nearest to the house tasks; "get some milk", "book a table for two", "take the cat to the vet" are
# as often the person's own errand on their way past, and refusing those is worse than the nod they
# had before. So a verb that is not one of the house tasks is an order only when the line says who
# it is for or asks the bot directly.
ADDRESSED = re.compile(
    r"^(?:ok\s+|okay\s+|right\s+|so\s+|hi\s+|hello\s+|hey\s+|and\s+)*"
    r"(?:(?:can|could|would|will)\s+you\b|please\b|kindly\b)")


BOOKING_THING = re.compile(r"\b(?:table|taxi|cab|room|tickets?|flight|hotel|appointment|"
                           r"restaurant|booking)\b")


# A line that names the person as the one it is done for ("book ME a table", "call the doctor FOR
# ME") is asking the bot to be the one who does it, and that is a limit to say plainly.
# The jobs that are words, not hands: a message to send, a letter, a form to fill, a thing to
# sign. The bot does half of these, so they are not the "no hands" limit - the drafting and
# on-screen pools answer them better. "sign me up for the class" is not one of these.
A_MESSAGE_OR_A_FORM = re.compile(
    r"\b(?:text|message|email|e-mail|letter|note|reply|voicemail|form|application|document)\b"
    r"|\b(?:sign|fill)\s+(?:this|it|that|in|out)\b|\bfill\s+in\b")


# "keep me posted" is a request for news, not a job: there is nothing to fetch, and the limit
# ("nothing can be fetched, sent or signed from this end") answers an ask nobody made. The same
# words are an errand when they name the thing: "keep an eye on the oven for me".
KEEP_ME_POSTED = re.compile(
    r"\bkeep\s+me\s+(?:posted|informed|updated|in\s+the\s+(?:loop|picture)|company)\b")


ACT_FOR_ME = re.compile(r"\b(?:for me|on my behalf)\b|^\s*(?:please\s+)?(?:book|reserve|order|"
                        r"call|ring|phone|text|email|buy|pay|send|save|pick|sign|keep|search)\s+"
                        r"(?:me|us)\b")


REMIND_ME = re.compile(r"^(?:please\s+|ok\s+|okay\s+|hi\s+|hello\s+)?remind me\b")


# "Remind me" is two lines, not one. "remind me to ring the dentist" is a job in the world the bot
# cannot do, and "remind me what i said at the beginning" is the store's own recall ask with three
# words in front of it - it was refused with "I can't do that one myself", which is a limit
# confessed over a question the memory could answer. Which one it is is not decided by the wh-word
# in it: "remind me when my dentist appointment is" and "remind me who my sister is" ask about the
# world and keep the limit, while "remind me what we said about the boiler" is the store's. So the
# store itself is asked, and the limit stands unless it can answer the ask behind the wrapper.
# The act has to be the whole line. "put the kettle on and it trips the switch" opens with the same
# verb as "put the kettle on" and then keeps going with its own subject, so it is a report about a
# fault, not an order - and "I can't do that one myself" refuses a job nobody asked for. The same
# goes for the commas ("take the rubbish out, its been there a week") and for a line that is a
# habit ("the washing machine still floods").
ACT_REPORT_TAIL = re.compile(
    r"(?:\b(?:and|but|then|so|because|till|until|when|while|whereas)\b|[,;])\s*"
    r"(?:it|they|he|she|i|we|the|my|its|this|that|there|nothing|nobody|everything|"
    r"someone|something)\b"
    r"|\b(?:still|keeps|kept|never|always|wont|cant|cannot|doesnt|didnt)\b"
    # "take the rubbish out, its been there a week": the comma is gone by the time this is read, so
    # the second half is caught by its own subject - a pronoun and what it goes on to say. An order
    # stops at the thing ("take the rubbish out", "put the oven on 200 for me"); nothing carries on
    # with "it", "they" or "we". "put the oven on its highest setting" is the possessive, which the
    # words after it do not look like a clause ("its highest"), so it stays an order.
    r"|\b(?:it'?s|its|it|they'?re|theyre|they|we'?re|we|i'?m|im|i|he'?s|she'?s|he|she|there)"
    r"\s+(?:not\s+)?(?:been|was|were|is|are|got|get|gets|went|goes|gone|split|splits|came|comes|"
    r"trips|cuts|leaks|floods|flooded|keeps|kept|stopped|broke|breaks|smells|smelt|died|works|"
    r"worked|fails|failed|\w+ing|full|empty|dirty|wet|broken|dead|stuck|blocked|loud|noisy|"
    r"cold|hot|freezing|boiling|on|off|open|shut|late|early)\b")


# Three readings that keep an instruction-shaped line out of the limit, because the person is not
# asking the bot to do the job:
#   - a choice ("take the bins out at night or morning", "put the oven on 180 or 200") is a question
#     about which, and the bot can answer that;
#   - a pronoun for the object ("put it in the oven at 200") is the speaker's own step, in the middle
#     of cooking, not an order to anyone;
#   - a temperature or a time ("on 200", "gas mark 6", "for 25 minutes") is a setting, which is how a
#     recipe step is said, not a job in the world.
ACT_CHOICE = re.compile(r"\bor\b")


ACT_OWN_STEP = re.compile(r"^\s*(?:it|them|that|this|those|these|one)\b")


ACT_SETTING = re.compile(
    r"\bgas\s+mark\s+\d+"
    r"|\b\d{2,3}\s*(?:c\b|\u00b0|degrees)"
    r"|\b(?:at|on|to)\s+\d{2,3}\b"
    r"|\b(?:for|about)\s+\d+\s*(?:mins?|minutes|hours?|hrs?)\b")


# A job asked of the bot in the polite form: "can you ring the council", "could you book me a
# table", "would you put that in my calendar". People ask a chatbot politely far more often than
# they order it about, and `_acts_for_me` read only the imperative and the objects it knew (a
# kettle, the bins, a table for two), so most polite asks reached the search hedge - the worst
# answer to "can you buy the tickets for me", because no search can buy them and the person asked
# the bot, not the internet. Three shapes are read here, each with its own line because the offer
# differs: a call needs the words before it is made, an errand needs the choosing, a date needs the
# phone's own calendar. A thing of theirs to read, print or send is a different limit with its own
# reader in this lane - it is their side of the screen, not a job in the world - and two lines for
# one shape would take the turn off each other.
POLITE_ASK = re.compile(
    r"^(?:(?:ok|okay|right|so|hi|hello|hey|and|thanks|ta|now|sorry|please)\s+)*"
    r"(?:(?:any\s+chance\s+)?(?:can|could|would|will)\s+(?:you|u)"
    r"|any\s+chance\s+(?:you|u)\s+(?:could|can|would|will))\s+(?:please\s+|possibly\s+)?"
    r"(?P<rest>[a-z0-9 ',.\-?!]+)$")


# A date put somewhere of theirs: the object is the calendar, the diary or the phone, and the verb
# has to be one that would move it there. "can you write my cv" is work the bot can do, so the
# verb alone is never enough.
ACTS_IN_A_DIARY = re.compile(
    r"\b(?:put|add|save|write|note|stick|move)\b.*\b(?:in|on|into|to)\s+(?:my|the)\s+"
    r"(?:calendar|diary|phone|notes?|list|fridge)\b")


# A call or a message to somebody. "talk through" and "speak up" are not asks to ring anyone, so
# speak and talk only count with "to" behind them.
# The act comes first in the ask ("ring the school"), so it is anchored: "can you copy the text
# from the email" has the word text as the thing, not the act, and a call is not the answer there.
ACTS_ON_A_PHONE = re.compile(
    r"^(?:just\s+|also\s+)?(?:(?:call|ring|phone|text|message|contact|chase)\b"
    r"|(?:speak|talk)\s+to\s+(?!me\b|us\b))")


# A purchase, a booking or something collected: the doing is theirs and the bot can only help
# choose. What is done to a form is not here ("can you fill in this form", "can you submit my tax
# return"): that is a thing of theirs on their own side, which has its own reader and its own offer
# (paste it in), and two lines for one shape would take the turn off each other.
ACTS_AN_ERRAND = re.compile(
    r"^(?:just\s+|also\s+)?(?:(?:book|reserve|buy|pay|purchase|renew|cancel|collect|pick\s+up|"
    r"apply|set\s+up|drop\s+off)\b|(?:get|ring|call|book|order)\s+(?:me|us)\s+(?:a|an|some)\b)")


# "Can you text me the list", "can you email me the letter": the person wants the words handed over
# in the chat, which the bot can do, so the ask is not a limit. "Call me a taxi" is the other way
# round - the article means something to be got for them, read as an errand above.
HANDS_IT_OVER_HERE = re.compile(
    r"\b(?:call|ring|phone|text|message|email|send|post|contact|chase)\s+(?:me|us)\b"
    r"(?!\s+(?:a|an|some)\b)")


# What nothing can buy or book, because it is not a thing: "can you buy me some time", "could you
# book me some rest", "can you pay attention". The object decides, not the verb.
NOT_A_THING_TO_GET = re.compile(
    r"\b(?:(?:some|a bit of|a little)\s+(?:time|rest|peace|quiet|space|slack)"
    r"|attention|my thoughts|the steps|a break|a rest|a day|a night|it a day|it a night)\b")


# What the bot can do itself: the same opener with one of these is a request it can meet ("can you
# write a message", "can you suggest a film", "can you check my spelling"), so the line keeps the
# answer it has. A reminder is in here too: the bot holds the job and the day, and the card about it
# says so better than a line about having no hands.
CAN_DO_ITSELF = re.compile(
    r"^(?:write|draft|rewrite|help|suggest|recommend|explain|remember|remind|tell|say|show|"
    r"pick\s+(?:one|which|between|the\b)|choose|plan|make|give|keep|freeze|cook|reheat|bake|"
    r"read|listen|work|sort|order(?!\s+(?:me|us)\b)|deal|spell|"
    r"check\s+(?:my\s+)?(?:spelling|grammar|writing|english|essay|answer|answers|maths|sums|"
    r"homework|work)|check\s+this|check\s+that|check\s+it)\b")


ACTS_ON_A_PHONE_LINES = (
    "I can't ring or message anyone for you - there's no phone on this end. Tell me who it is and "
    "what has to be said, and I'll help you find the words before you call.",
    "No phone here, so the call can't be mine. Give me the who and the one thing you need from "
    "them, and we'll work out what to say.",
)


ACTS_AN_ERRAND_LINES = (
    "I can't book, buy or pay for anything from here, sorry - the doing is yours. What I can do "
    "is the choosing: the options, the order to do it in and the questions to ask. Which part?",
    "Nothing in the world is mine to do - no booking, no paying. Tell me what you're after and "
    "I'll narrow it down, or work out what to check before you commit.",
)


ACTS_IN_A_DIARY_LINES = (
    "I can't put anything in your calendar - I only hold it for this chat, and it goes when the "
    "chat does. Put it in your phone with a reminder; tell me the date and I'll help you plan "
    "around it.",
    "Your calendar isn't something I can reach, sorry. Write it in your phone with a reminder, "
    "and say the day here and I'll help you get ready for it.",
)


# A clock is the one job people ask a bot for by name - "set a timer for 10 minutes", "wake me up
# at 7" - and the store's nod below answered it as if the timer were running. Nothing here can
# ring, so the limit is said in a few words and the two taps that do it are named.
ACTS_ON_A_CLOCK_LINES = (
    "No clock on this end - nothing here can ring or buzz. The timer in your phone's clock app "
    "does it in two taps; tell me what it's for and I'll help with the rest of it.",
    "I can't set a timer or an alarm, sorry - I'm only up while you are typing. Set it on your "
    "phone and tell me the job it's for; that part I can help with.",
)


# A document or a print job: the words are mine, the pressing of the button is theirs.
ACTS_ON_A_DOCUMENT_LINES = (
    "Nothing on this end can print, scan or send a file - no printer, no outbox. The print or "
    "share button on whatever you're reading this on does it; tell me what it is and I'll help "
    "with the rest.",
    "That one needs a printer or an inbox, and neither is mine. Do it on your own device, and "
    "bring me the wording or the order to send things in.",
)


# A job in the world said the way people actually type it: verb first, no "can you" in front.
# "text my mum", "book the tickets", "set a timer for 10 minutes", "save this for later" were
# all answered by the store's own acknowledgement - "Noted: text your mum", "Book the tickets -
# I'll remember that" - and a nod that reads as a job done is the worst answer of the lot: a
# person can believe the tickets are booked. The same three readings the polite form already has
# (`ACTS_ON_A_PHONE_LINES`, `ACTS_AN_ERRAND_LINES`, `ACTS_IN_A_DIARY_LINES`) answer the bare
# order, plus a clock and a document, which the polite form could not reach because "can you set
# an alarm" is an ask about how phones work.
ORDER_OPENER = re.compile(
    r"^(?:(?:ok|okay|right|so|hi|hello|hey|and|just|now|quick|quickly|please|ta|thanks)\s+)*"
    r"(?P<job>(?:text|message|whatsapp|sms|email|mail|ring|call|phone|facetime|contact|chase|book|"
    r"reserve|order|buy|purchase|renew|collect|pick\s+up|put|add|save|write|note|jot|set|wake|"
    r"alarm|print|scan|photocopy|copy|download|upload|send|forward|share)\b)(?P<tail>.*)$")


# Which of the jobs it is, read from the whole line. Each needs a thing or a place of theirs: an
# order with no object ("book it", "order one") is as likely a reply in the middle of a chat as
# an order to the bot, so the words that make it one are what count.
ORDER_A_MESSAGE = re.compile(
    r"^(?:text|message|whatsapp|sms|email|mail|ring|call|phone|facetime|contact|chase)\s+"
    r"(?:my|our|the|his|her|their|a|an|\w+'s)\s+\w+")


ORDER_A_BUY = re.compile(
    r"^(?:book|reserve|order|buy|purchase|renew|collect|pick\s+up)\s+(?:me\s+|us\s+)?"
    r"(?:a|an|the|some|two|three|four|more|my|our|another)\b")


ORDER_A_RECORD = re.compile(
    r"^(?:put|add|save|write|note|jot|stick|move)\b.*\b(?:in|on|into|to)\s+(?:my|the)\s+"
    r"(?:\w+\s+){0,2}(?:calendar|diary|phone|notes?|list|app|reminders?|fridge|whiteboard)\b"
    r"|^(?:save|keep)\s+(?:this|that|it)\b")


ORDER_A_CLOCK = re.compile(
    r"^(?:set|put)\s+(?:a|an|the|my)\s+(?:timer|alarm|countdown|reminder|stopwatch)\b"
    r"|^wake\s+me\b|^(?:set|put)\s+(?:a|an|the)\s+alarm\b|^alarm\s+me\b")


ORDER_A_DOCUMENT = re.compile(
    r"^(?:print|scan|photocopy|copy|download|upload|send|forward|share)\s+"
    r"(?:this|that|it|these|those|them|a|an|the|my|two|three)\b")


# The line goes on to report instead of ordering: "text my mum and she never answers" is about the
# mother, not an ask. The same guard `ACT_REPORT_TAIL` makes for the house tasks, kept separate so
# a tail added for one reading cannot quietly widen the other.
ORDER_A_REPORT = re.compile(
    r"\b(?:and|but|then|so|because|till|until|while)\s+"
    r"(?:it|they|he|she|i|we|the|my|its|there|nothing|nobody|everyone)\b"
    r"|\b(?:yesterday|last\s+night|last\s+week|this\s+morning|earlier|already|never|always|"
    r"every\s+day|usually|used\s+to|didnt|didn't|did|keeps|kept)\b")


# "call the doctor" on its own is a call somebody makes, and a bot that says "no phone on this
# end, tell me who it is and what has to be said" is more use than "call the doctor - noted".
# What is not a job for the bot: an emergency call (the safety card owns it) and a call about a
# thing rather than to a person ("call it a day").
ORDER_NOT_A_JOB = re.compile(
    r"\b(?:ambulance|paramedic|paramedics|999|911|112|fire\s+brigade|police|cops|101|"
    r"it\s+a\s+(?:day|night)|a\s+day|a\s+night|it\s+off|quits)\b")


def _an_order_it_cannot_do(clean):
    """The honest line for a job in the world typed as an order, or None.

    Only the shapes where the doing can only be the person's are read: a message to somebody, a
    purchase or a booking, something put in their calendar or notes, a timer, and a document. The
    offer after the limit is what makes it an answer - the words, the choosing, the order to do
    things in - so a line that is a thing to work out keeps the advice it gets elsewhere.
    """
    bare = " ".join(re.sub(r"[^a-z0-9 ']+", " ", str(clean or "").lower()).split())
    if not ORDER_OPENER.match(bare) or ORDER_A_REPORT.search(bare):
        return None
    if ORDER_NOT_A_JOB.search(bare):
        return None
    if ORDER_A_CLOCK.search(bare):
        return ACTS_ON_A_CLOCK_LINES
    if ORDER_A_RECORD.search(bare):
        return ACTS_IN_A_DIARY_LINES
    if ORDER_A_MESSAGE.search(bare):
        return ACTS_ON_A_PHONE_LINES
    if ORDER_A_BUY.search(bare):
        return ACTS_AN_ERRAND_LINES
    if ORDER_A_DOCUMENT.search(bare):
        return ACTS_ON_A_DOCUMENT_LINES
    return None


def _act_asked_of_me(clean):
    """The honest line for a job asked of the bot in the polite form, or None.

    Only the polite form is read: the imperative has `_acts_for_me` and `ACTS_FOR_ME` already,
    and its house tasks ("put the kettle on") are a different offer from these.
    """
    match = POLITE_ASK.match(" ".join(str(clean or "").lower().split()))
    if not match:
        return None
    rest = match.group("rest").strip()
    if not rest or CAN_DO_ITSELF.match(rest):
        return None
    if ACTS_IN_A_DIARY.search(rest):
        return ACTS_IN_A_DIARY_LINES
    if EMERGENCY_CALL.search(rest) or POLICE_CALL.search(rest):
        # "can you call an ambulance", "can you ring 999": the safety card owns this, and a line
        # about having no phone is the one answer that must not land on it.
        return None
    if NOT_A_THING_TO_GET.search(rest) or HANDS_IT_OVER_HERE.search(rest):
        return None
    if ACTS_AN_ERRAND.search(rest):
        return ACTS_AN_ERRAND_LINES
    if ACTS_ON_A_PHONE.search(rest):
        return ACTS_ON_A_PHONE_LINES
    return None


def _the_store_has_the_recall(clean, memory):
    """True when the memory store has the line a "remind me ..." asks for.

    The store is asked rather than a list of words here, because only the store knows what it can
    hand back: it answers "remind me what we said about the boiler" and "remind me where we
    started", and returns nothing for "remind me who my sister is". A word list in this file would
    be a second, drifting copy of that knowledge - the first cut of this had one, and every shape
    it waved through but the store could not answer fell to a nod ("Got it. Is there anything
    you'd like a hand with?") where the limit had been the honest answer.
    """
    try:
        from ..modules import memory_store
    except Exception:  # noqa: BLE001 - no store to ask, so the limit stands
        return False
    try:
        return bool(memory_store.respond(clean, memory if isinstance(memory, dict) else {}))
    except Exception:  # noqa: BLE001 - a reading that fails leaves the line to the limit
        return False


def _acts_for_me(clean, memory=None):
    """True when the line tells the bot to do a job in the world, which it cannot do."""
    bare = " ".join(re.sub(r"[^a-z0-9 ']+", " ", str(clean or "").lower()).split())
    # "keep me posted" is the idiom, and it asks for news rather than a job.
    if KEEP_ME_POSTED.search(bare):
        return False
    # ...except the jobs it can do half of, which are words: a message, a letter, a form. "can you
    # send an email for me" is answered by the drafting invite ("tell me who it's for and what you
    # want them to do"), and "can you sign this for me" by the line that says it cannot click or
    # print and offers to walk them through the screen. Saying "no hands" over the top of those
    # throws away the one useful half, so the readers that answer them are asked here.
    #
    # Only a reader with an answer takes the line off the limit. Standing down for the word alone
    # ("text", "email", "form") left the lines no reader wants - "text me the address", "email me
    # the list", "text me when youre outside" - with the shrug the limit had replaced, which is
    # the one thing worse than the limit.
    if A_MESSAGE_OR_A_FORM.search(bare):
        if (no_eyes.writes_the_message(clean)
                or no_eyes.cannot_see_your_thing(clean)
                or no_eyes.look_at_a_body_lines(clean, bare)):
            return False
    if REMIND_ME.match(bare):
        return not _the_store_has_the_recall(clean, memory)
    opener = ACT_OPENER.match(bare)
    if not opener:
        return False
    tail = bare[opener.end():]
    if ACT_REPORT_TAIL.search(tail):
        return False  # the line goes on about something else: it reports, it does not ask
    if not ACT_FOR_ME.search(bare):
        # Not addressed to the bot at all: a choice, the speaker's own step, or a setting.
        if ACT_CHOICE.search(bare) or ACT_OWN_STEP.match(tail) or ACT_SETTING.search(bare):
            return False
    if ACT_FOR_ME.search(bare):
        return True  # "book me a table", "call the doctor for me": the bot is the one asked to act
    verb = bare.split()[0]
    if verb not in HOUSE_VERB and not ADDRESSED.match(bare):
        return False  # not said to the bot and not a house task: the person's own errand
    if verb in ("call", "ring", "phone", "text", "email", "buy", "pay", "renew"):
        # "call the doctor" on its own is as likely to be asking for advice as telling the bot to
        # ring: only the line that says who it is for is an instruction.
        return False
    if verb in ("book", "reserve", "order"):
        return bool(BOOKING_THING.search(bare))
    # Said to the bot itself ("could you put the kids to bed"), the thing does not have to be one of
    # the house's: the line is an order whatever the object is. Said flat, it does.
    return bool(ADDRESSED.match(bare) or ACT_THING.search(bare))


def _reads_as_a_bad_stretch(clean):
    """True when the line is a bad stretch of time and nothing else."""
    words = [w.strip(".,!?;:") for w in clean.split()]
    for index, word in enumerate(words):
        if word not in BAD_STRETCH:
            continue
        before = " ".join(words[max(0, index - 4):index])
        if _a_claim_about_a_thing(before):
            continue
        after = words[index + 1:]
        if after[:1] in (["few"], ["couple"]) and len(after) > 1:
            after = after[1:]
        if after and after[0] in STRETCH_OF_TIME:
            return True
        if not after and any(w in STRETCH_OF_TIME for w in before.split()):
            return True  # "my week has been rough", "the week was hard"
    return False


def _cue_negated(words, cue):
    """True when a negator stands just in front of the cue: "not finished", "not yet finished".

    Two words is the widest that stays honest. One misses "not yet sorted"; three starts
    swallowing real wins - "i cant believe i finished it" and "not bad, i finished it" are both
    good news with a negator three words away. Three is only enough when a doubt word sits
    between them: "i don't think i'm happy" is not happy, and `turns_round` tells that apart
    from the "can't believe" that is delight.
    """
    for index, word in enumerate(words):
        if word != cue:
            continue
        if any(other in NEGATORS for other in words[max(0, index - 2):index]):
            return True
        before = words[max(0, index - 3):index]
        if set(before) & DOUBTED:
            return True
        if set(before) & DOUBT and turns_round(before):
            return True
    return False


def _a_state_in_the_past(words, index):
    """True when the state word at `index` is said in the past: "my wife was pregnant"."""
    return bool(set(words[max(0, index - 3):index]) & _WAS)


def _the_win_is_someone_elses(words, index):
    """True when the good thing at `index` is a crowd's, not the person's own.

    Reads back to the nearest subject and stops at the first one: "my friend told me i should be
    proud" is still the person's own pride, because the "i" is nearer the cue than the friend.
    What counts as someone else's is a crowd - the thing a person can be measured against, "everyone
    else", "all my mates". A relation on their own is not: "my mum finally finished chemo" is news
    a person is glad of, and withholding that cheer is not what this is for.

    A crowd feeling something about the person is still the person's: "everyone is happy for us",
    "everyone's proud of me" - the words after the cue say who it is about, so they are read too.
    """
    after = words[index + 1:index + 3]
    if after and after[0] in ABOUT_WORDS and set(after[1:]) & PERSON_WORDS:
        return False
    for j in range(index - 1, max(-1, index - 7), -1):
        word = words[j]
        if word in YOU_SUBJECTS:
            return False
        if word in CROWD:
            return True
        # "all my mates are sorted", "all her friends have got sorted": a whole set of people,
        # which is the same measuring stick as "everyone else" even though each one is a friend.
        if (word in loss.PEOPLE and word.endswith("s")
                and "all" in words[max(0, j - 3):j + 1]):
            return True
    return False


# "my laptop has finally died" is not good news: "finally" is a cue on its own, so the cheerful
# pool cheered a broken laptop ("Good for you! That's really lovely news."), a car that has
# given up ("That's great news - nice one") and a knee that has given out. The cue is spent when
# the thing right after it stops, so the line falls through to the readers below it.
THINGS_THAT_STOP = frozenset((
    "died", "dead", "broke", "broken", "collapsed", "failed", "stopped", "conked",
))


THINGS_THAT_STOP_AFTER_UP = frozenset(("gave", "given", "packed", "went"))


THE_WORDS_BETWEEN = frozenset(("has", "have", "had", "is", "was", "were", "s", "just", "now"))


# A pleasure that has gone out of everything is a low line, and it is said with the word
# "nothing" in front of the cue or with the enjoyment turned round: nobody who types it is telling
# you good news. "nothing makes me happy" has "happy" in it, which is a positive cue with nothing
# in the three words before it that the cue loop reads as a negator, so the cheerful pool said
# "Good for you! That's really lovely news." to a person saying the opposite. "nothing feels fun
# any more" and "i dont enjoy anything any more" carry no cue at all and got the neutral receipt,
# which is the same shrug at the same statement in a different word order.
#
# Only the plain sense is here. "nothing to do" is a boring afternoon and "nothing works" is a
# broken printer, so both are left alone; "nothing makes me happier than the dog" is a good thing
# said with a comparison, and the cue word there is "happier", which none of these patterns reach.
# The thing that gives pleasure, in the words people use for it. Read as a shape rather than as a
# list of phrasings: the same statement arrives as "nothing makes me happy", "nothing brings me
# joy", "nothing feels worth doing", "i dont get any pleasure out of anything", "fun has gone out
# of everything" and "i feel nothing", and every one of them is a person saying the pleasure has
# gone - none of them is news to be cheered or a shrug to be filed.
PLEASURE_WORD = (r"(?:fun|funny|joy|joyful|pleasure|enjoy(?:s|ed|ing|able)?|happy|happiness|"
                 r"smile|laugh|mood|worth(?:while|\s+doing)?|interest(?:s|ed|ing)?|"
                 r"look\s+forward\s+to|content|exciting|excites?)")


# "Nothing … the pleasure" with nothing in front of it: "nothing makes me happy", "nothing feels
# fun", "nothing lifts my mood", "there is nothing i enjoy". A comparison is the opposite statement
# and is left alone ("nothing makes me happier than the dog", "nothing beats a curry"), so a word
# that turns the pleasure into a comparison stands the reading down.
NOTHING_AND_A_PLEASURE = re.compile(
    r"\bnothing\b[^.?]{0,28}?\b" + PLEASURE_WORD + r"\b")


A_COMPARISON = re.compile(r"\b(?:than|beats?|more\s+than|as\s+much\s+as)\b")


# The other half of the same sentence: a negator in front of the pleasure and everything as its
# object - "i dont get any pleasure out of anything", "i never enjoy anything", "no joy from
# anything", "i stopped enjoying things". The object is what makes it about their life rather than
# their taste: "i dont enjoy horror films" is a fact about films and keeps the turn.
NOTHING_NEGATED = re.compile(
    r"\b(?:no|not|never|dont|don'?t|doesnt|doesn'?t|cant|can'?t|cannot|stopped|without)\b"
    r"[^.?]{0,24}?\b" + PLEASURE_WORD + r"\b[^.?]{0,20}?"
    r"\b(?:anything|nothing|much|things|life|it|myself|any\s?more|anymore|at\s+all)\b")


# "fun has gone out of everything" is the same statement said from the other end.
PLEASURE_GONE_OUT = re.compile(
    r"\b(?:fun|joy|pleasure|interest|point|enjoyment)\b\s+(?:has|have|had)\s+"
    r"(?:gone|gone\s+right|all\s+gone)\s+out\s+of\b")


# The shortest way it is said at all, plus the pleasure named after the verb ("enjoying nothing")
# and the plain "nothing feels good" - which is not "nothing is good on telly", so the verb stays
# the thing that makes it a statement about them.
FEELING_NOTHING = re.compile(
    r"\bfeel(?:s|ing)?\s+nothing\b|\bnothing\s+matters\b"
    r"|\bnothing\s+(?:makes\s+me\s+)?feels?\s+(?:good|right|nice|better)\b"
    r"|\b(?:enjoy|enjoying|enjoyed)\s+nothing\b")


# Two shapes built from the same words that are not this statement at all, both found by the
# deck and both answered better by what came before this reading.
#
# A limit on the answer above ("nothing with a laugh track though", "no subtitles") is not a
# statement about their life: the pleasure word inside it belongs to the thing they are asking to
# leave out. `limit.NOTHING_THAT_LIMITS` and `limit.a_limit_on_the_answer` are the one reading of
# that shape, shared with the module that takes things out of an answer.
#
# A pleasure about one named thing: "i got the promotion and i don't feel happy about it" is a
# person asking whether that is odd, not a person saying the pleasure has gone out of everything,
# and the promotion answer is what they need. The reading wants everything as the object, so a
# pleasure tied to "it", "that" or a named thing stands it down.
PLEASURE_ABOUT_ONE_THING = re.compile(
    r"\b(?:happy|glad|pleased|excited|thrilled|proud)\s+about\s+"
    r"(?:it|that|this|them|him|her|the\b|my\b|his\b|her\b|their\b|our\b)")


def reads_as_no_pleasure(clean):
    """True when the line is a person saying the pleasure has gone out of everything."""
    text = " ".join(str(clean or "").lower().split())
    if not text:
        return False
    # "nothing feels better than this" and "nothing makes me happier than the dog" are the good
    # thing said with a comparison, which is the opposite statement in the same words.
    if A_COMPARISON.search(text):
        return False
    if NOTHING_THAT_LIMITS.search(text) or PLEASURE_ABOUT_ONE_THING.search(text):
        return False
    if FEELING_NOTHING.search(text) or PLEASURE_GONE_OUT.search(text):
        return True
    if NOTHING_AND_A_PLEASURE.search(text):
        return True
    return bool(NOTHING_NEGATED.search(text))


# A question about the bot's own body or abilities is the one ask that is always answerable, and it
# was reaching the search hedge: "can you drive" and "can you feel pain" were told that "a quick
# search online will get you a solid answer", which no page can give, because the subject is this
# program. The answer is the same for every verb in the list - a program has no body, no senses and
# no car keys - so the pool says that once and stays true, and then offers the half it can do.
ABOUT_THE_BOT_LINES = (
    "Nothing to do it with, I'm afraid: I'm a program, so no body, no senses and no car keys. Ask "
    "me the thing you would ask a friend and I will take that half of it on.",
    "No, and I would rather say so than guess. I am a program in a chat window, so what I can do "
    "is read, remember this conversation and think the question through with you.",
    "Not at all - there is no body here. If it is something you are wondering about, ask it "
    "anyway: plenty of that I can still help with.",
)


# The shape is the whole line, because the subject is the bot. "Can you smell gas" is their
# kitchen, "can you feel the baby moving" is a pregnancy and "can you drive me to the airport" is
# a lift, so a verb with a thing of theirs after it is not this question: only a bare sense or
# body verb, optionally with a word like "pain" or "anything" that names nothing of theirs.
ABOUT_THE_BOT = re.compile(
    r"^(?:can|could)\s+(?:you|u)\s+(?:actually\s+|even\s+|really\s+|still\s+)?"
    r"(?:drive|smell|taste|feel|see|hear|touch|breathe|eat|drink|swim|run|walk|dance|sing|laugh"
    r"|cry|shiver|sweat|blink|wave|hold|hug|kick|jump|climb|fly)\b"
    r"(?:\s+(?:anything|something|things?|pain|cold|the\s+sun|a\s+car|at\s+all|either|yet|though))?"
    r"\s*(?:please|then)?\s*\?*\s*$", re.I)


def reads_as_a_question_about_the_bot(clean):
    """True for "can you drive", "can you feel pain": the whole line, about this program."""
    text = " ".join(str(clean or "").lower().split())
    return bool(text) and bool(ABOUT_THE_BOT.match(text))


# What is said to a person whose pleasure has gone out of everything, once the readings have had
# their turn. The gentle pool is what this file says to a low line, and one of its lines offers
# films, a series and a book that "leave you better than they found you" - which is the one reply
# that does not help somebody who has just said nothing gives them any pleasure: it answers a flat
# fortnight with the telly. The line here says what the flatness is worth doing about, names the
# one small concrete thing that tends to help, and asks the question that puts the person's own
# week back in it, so the turn is never just sympathy.
PLEASURE_GONE_LINES = (
    "That flatness is a miserable thing to carry, and it is not laziness or a mood to be talked "
    "out of. More than a couple of weeks of it is worth saying to a GP, and until then the "
    "smallest thing that helps is one thing you used to like, put back in this week on a day you "
    "pick. What did you look forward to a year ago?",
    "I'm sorry - when nothing gives pleasure the days go flat and everything takes effort, and "
    "waiting for it to lift is the one thing that does not work. Tell one person, and put one "
    "small piece of what you used to enjoy back on the calendar this week; if it has been weeks, "
    "say it to a GP. What did you like doing before this started?",
    "That is worth taking seriously rather than shaking off: nothing giving pleasure for weeks is "
    "something a GP wants to hear about, and it is not a failing to say so. Until then the "
    "things to try are small and concrete - one walk, one person, one thing you used to look "
    "forward to, this week. Which of those feels least impossible?",
)


def _a_thing_stopping_after(words, i):
    """True when the words after a cue name that thing stopping ("has finally died")."""
    after = list(words[i + 1:i + 5])
    while after and after[0] in THE_WORDS_BETWEEN:
        after.pop(0)
    if not after:
        return False
    if after[0] in THINGS_THAT_STOP:
        return True
    if after[0] in THINGS_THAT_STOP_AFTER_UP and len(after) > 1 and after[1] in ("up", "in",
                                                                               "out"):
        # "gave up smoking" is a thing given up, so the cue stands; "has given up" on its own,
        # "given out", "packed in" and "gave up on me" are the thing stopping.
        return len(after) == 2 or after[2] in ("on", "it", "them", "me", "him", "her", "us")
    return False


# A harm the person reports is a bad line however it is worded, and the day pool used to cheer it:
# "i dislocated my shoulder" was answered "Nice one. How did the rest of it go?", "my back went last
# week" "Good to hear. What was the best bit?", "i got a concussion playing football" "How was it,
# overall?" and "i have covid" "Noted: you have covid." Every one of those is a past-tense account
# with no mood cue in it, so `_mood` read it as neutral and the small-day pool took the turn.
#
# The two shapes are the ones people say it in: the person as the doer of a hurt ("i broke my
# wrist", "i cracked a rib", "i dislocated my shoulder") and the person as the one it happened to
# ("i got a concussion", "i have covid", "i had a miscarriage"). A hurt with no owner is not this
# ("my car broke down", "the boiler broke"), and neither is a thing that is not the body - the
# owner words are what keep "i broke my phone" the phone card's, which answers it anyway.
_A_HURT_DONE = re.compile(
    r"\b(?:i|we)\s+(?:just\s+|nearly\s+|think\s+i\s+)?(?:have\s+|had\s+|ve\s+)?"
    r"(?:broke|broken|fractured|cracked|dislocated|sprained|tore|torn|snapped|slipped|"
    r"hurt|injured|done)\b", re.I)


# The part has to be in the line for it to be a hurt done to the person: the same verb is a
# phone, a car and a boiler in other lines, and every one of those has a card of its own that
# answers it. A body word is the whole test, so "i broke my wrist", "i cracked a rib" and "i
# dislocated my kneecap" are this and "i broke my phone" is the phone card's.
_A_BODY_WORD = re.compile(
    r"\b(?:back|knees?|legs?|feet|foot|ankles?|hips?|arms?|elbows?|wrists?|hands?|fingers?|"
    r"thumbs?|shoulders?|ribs?|neck|toes?|heels?|shins?|calves|calf|thighs?|collarbone|"
    r"jaw|nose|eyes?|head|spine|disc|kneecap|ligaments?|muscles?|tendons?|bones?|"
    r"teeth|tooth|nail|shoulder blade|lip|lips|cheek|cheeks|chin|ears?|eyebrow|"
    r"forehead|scalp)\b", re.I)


# The illness and the diagnosis, which are said with "have", "had" or "got". Only the words that
# are no everyday thing: "i had a fall" is a hurt done, "i had a fit" is a seizure, and "i had a
# stroke" is not a stroke of luck - but a line that says which one it was is left to the cards.
_A_HARM_HAD = re.compile(
    # "i've had stitches" is the same report as "i had stitches", so the contracted subject is
    # read as well as the spaced one. Without it the shorthand got "How was it, overall?".
    r"\b(?:(?:i|we)\s+(?:(?:have|had|has)\s+been\s+)?(?:have|had|got|caught|was given|were given|"
    r"been given|been told|was diagnosed with|diagnosed with)|"
    r"(?:i've|we've|ive|weve)\s+(?:had|got|been given|been diagnosed with))"
    r"\s+(?:to have\s+|to get\s+)?"
    # "i got four stitches in my chin" is the same report as "i got stitches", and the count in
    # front of them is what the first draft could not read: it was answered "Nice one. How did the
    # rest of it go?".
    r"(?:a|an|the|my|some|a few|a couple of|two|three|four|five|six|seven|eight|nine|ten|\d+)?\s*"
    r"(?:concussion|concussions|stitches?|staples?|whiplash|pneumonia|sepsis|septicaemia|meningitis|"
    r"covid|coronavirus|shingles|glandular fever|miscarriage|stillbirth|seizure|seizures|"
    r"stroke|heart attack|blood clot|pulmonary embolism|breakdown|relapse|"
    r"chemo|chemotherapy|radiotherapy)\b", re.I)


# The illness half of the same report is a rule, not a list of the ones that came up. A person
# says what they have with "have", "had", "got" or "caught" and then names it, and the naming is
# what makes it an illness: a head word ("infection", "bug", "flu", "cold", "temperature"), or a
# word that only illness names end in ("bronchitis", "norovirus", "pleurisy", "chickenpox"). The
# first draft listed covid, shingles and pneumonia, so "i had the flu", "i had the norovirus",
# "i had a uti" and "i had bronchitis" were all still cheered ("Nice one. How did the rest of it
# go?") - the same bug in the same shape, one noun over.
_A_ILLNESS_WORD = (
    r"(?:[a-z]+\s+){0,2}?"
    r"(?:infections?|bugs?|virus(?:es)?|flu|influenza|fever|colds?|cough|temperature|"
    r"poisoning|disease|illness|ailment|condition|attack|migraines?|seizures?|"
    r"sore throat|sickness|nausea|diarrhoea|diarrhea|rash|abscess|cyst|ulcer|thrush|"
    r"gout|shingles|covid|coronavirus|malaria|tuberculosis|hepatitis|uti|dvt|copd|ibs|mrsa|"
    r"strep|\w+(?:itis|osis|aemia|emia|iasis|pox|virus))"
)


_A_HARM_ILL = re.compile(
    # "i have been diagnosed with sepsis" is how a lot of people say a diagnosis, and the "been"
    # in the middle put it back on the day pool: the auxiliary is read with or without it.
    r"\b(?:(?:i|we)\s+(?:(?:have|had|has)\s+been\s+)?(?:have|had|got|caught|was given|were given|"
    r"been given|been told|was diagnosed with|diagnosed with)|"
    r"(?:i've|we've|ive|weve)\s+(?:had|got|been given|been diagnosed with|"
    r"caught))"
    r"\s+(?:to have\s+|to get\s+)?"
    r"(?:a|an|the|my|some|a few|a couple of|two|three|four|five|six|seven|eight|nine|ten|\d+)?\s*"
    + _A_ILLNESS_WORD + r"\b", re.I)


# The same words where they are not an illness at all: a cold drink is a drink, a bug in the code
# is a program, and a temperature or a condition can be the setting of a thing.
_A_HARM_ILL_NOT = re.compile(
    r"\b(?:cold (?:one|beer|drink|water|shower|bath|snap|call|weather|night|morning|day|"
    r"evening|outside|front|shoulder|hands|feet)|"
    r"bugs? (?:in|on) (?:my |the )?(?:code|computer|laptop|phone|app|program|software|system)|"
    r"virus (?:on|in) (?:my |the )?(?:computer|laptop|phone)|"
    r"temperature (?:setting|gauge|dial|outside|gauge)|"
    r"sickness (?:policy|pay|record|note)|"
    r"in (?:good|no|great|perfect|top) condition|condition of (?:the|my) (?:car|house|road)|"
    r"attack of (?:the )?(?:nerves|conscience)|"
    r"fever pitch|cabin fever|spring fever)\b", re.I)


# The same words in a phrase that is not a harm: "i had a stroke of luck" is a good day and "i
# broke the ice at the meeting" is a small one. This keeps *this* reader off them - what a person
# gets for those lines is another reader's answer, and it is not the warm pool this change adds.
# A harm is a thing that happens to a body, and these say so in words that only look
# like one.
_A_HARM_IDIOM = re.compile(
    r"\b(?:stroke of (?:luck|genius|good luck|the brush)|brush ?stroke|stroke of a pen|"
    r"broke the ice|broke the news|broke even|broke the bank|broke a record|broke the rules|"
    r"broke a promise|broke the silence|cracked a joke|cracked a smile|cracked on|"
    r"cracked a window|slipped my mind|slipped away|tore a strip off|torn between)\b", re.I)


# A knock that took the person off something, a joint that came out of its socket and a week in
# agony are the same report in other words: "i got knocked off my bike" was asked how it went
# ("How was it, overall?"), "my shoulder came out of its socket" the same, and "i have been in
# agony all week" was said back ("Noted: you have been in agony all week."). None of them names an
# illness or a part, so the hurt words above miss them.
_A_HARM_KNOCK = re.compile(
    r"\b(?:knocked|thrown|shoved|swiped|swept)\s+off\s+(?:my|our|his|her|their|the|a)\b"
    r"|\bhit\s+by\s+a\s+(?:car|van|lorry|truck|bus|taxi|bike|motorbike|cyclist)\b", re.I)


_A_OUT_OF_SOCKET = re.compile(
    r"\bcame out of (?:its|the|my) socket\b|\bout of (?:its|the) socket\b"
    # a joint that came out and went back in is said without the socket, and "my shoulder came out
    # again" was answered "Good to hear. What was the best bit?" - the part is what makes it a
    # report, so a car that "came out" and a tooth that "came out" keep their own answers.
    r"|\b(?:my|our|his|her|their|the)\s+(?:shoulders?|knees?|kneecap|hips?|elbows?|jaw|"
    r"ankles?|fingers?|thumbs?|wrist|toe)\s+(?:came|comes|went|goes|popped|pops) out\b",
    re.I)


_A_IN_AGONY = re.compile(r"\bin (?:absolute |sheer |real )?agony\b", re.I)


# A part that "went" is the way people say a back or a knee gave out: "my back went last week" is
# the same report as "my back went", and the day pool asked how the week went.
_A_PART_WENT = re.compile(
    r"\bmy\s+(?:back|knee|knees|leg|arm|shoulder|hip|ankle|neck)\s+(?:just\s+|suddenly\s+)?"
    r"(?:went|gone|gave way|gives way)\b", re.I)


# A hurt somebody else did to the person is the same report in the other direction, and the day pool
# cheered it: "he held a knife to my throat" was answered "Good to hear. What was the best bit?" and
# "his friend spat at me" "Noted: his friend spat at you." The person is the object here, not the
# doer, and the safety cards catch most of the family ("my ex hit me", "he punched me in the face"
# are all cards) - this is the floor's backstop for the ones they miss, so the worst it can do is
# answer with the warm line instead of a cheer.
#
# Who can do it is a shape, not a list of relatives: he, she, they, someone, somebody, a man, and
# any "my/his/her/their/our <person>". What they do is a hurt with the person as its object.
_A_SOMEONE = (
    r"(?:he|she|they|someone|somebody|anyone|"
    r"(?:a|the)\s+(?:man|woman|lad|bloke|chap|guy|girl|boy|teen|carer|nurse|neighbour|neighbor)|"
    r"(?:my|his|her|their|our)\s+\w+)")


_A_HURT_BY_SOMEONE = re.compile(
    # someone hits, kicks, slaps, punches, bites or burns the person
    r"\b" + _A_SOMEONE + r"\s+(?:\w+\s+){0,2}?"
    r"(?:hit|punch(?:ed|es|ing)?|kick(?:ed|s|ing)?|slapp?(?:ed|ing)|smack(?:ed|ing)?|"
    r"beat|beats|beating|beaten|headbutt(?:ed)?|bit|bites|burn(?:ed|t|s)|"
    r"chok(?:ed|ing)|strangl(?:ed|ing)|stabbed|stabs|raped|molested|groped|"
    r"dragg?(?:ed|ing)|whipp?(?:ed|ing)|belt(?:ed|ing))\s+(?:me|us)\b"
    # the same with a part of them named: "he punched me in the face", "my ex grabbed my arm"
    r"|\b" + _A_SOMEONE + r"\s+(?:\w+\s+){0,2}?"
    r"(?:hit|punched|kicked|slapped|grabbed|pinched|twisted|yanked|wrenched|bit|bitten)\s+my\s+\w+"
    # a push or a shove with a place in it, because "she pushed me to apply" is not a hurt
    r"|\b" + _A_SOMEONE + r"\s+(?:\w+\s+){0,2}?(?:push(?:ed|es|ing)?|shov(?:ed|es|ing)?)\s+"
    r"(?:me|us)\s+(?:down|into|against|over|off|up|to the)\b"
    # a thing thrown at the person, or spit
    r"|\b" + _A_SOMEONE + r"\s+(?:\w+\s+){0,2}?(?:threw|throws|tossed|spat|spits?)\b"
    r"[^.?!]{0,25}?\bat\s+(?:me|us)\b"
    # a weapon held or pointed at the person
    r"|\b(?:held|holds|holding|put|puts|pointed|pointing|pressed|had|pulled)\s+"
    r"(?:a|an|the|his|her|their)\s+(?:knife|gun|blade|scissors|hammer|bat|belt|bottle|"
    r"glass|razor|needle|pillow|cushion)\s+(?:to|at|against)\s+(?:my|her|his|our)\s+\w+",
    re.I)


# The same words where nobody was hurt: "he hit me up" is a message, "he hit on me" is flirting,
# "she kicked me out" is a flat, "he beat me to it" is being quicker, and a boss who "pushed me
# into applying" is a boss.
_A_HURT_BY_SOMEONE_NOT = re.compile(
    r"\b(?:hit me up\b|hit on me\b|kicked me out\b|beat me (?:at|in|to)\b|"
    r"bit my head off\b|grabbed my (?:attention|eye)\b|"
    r"pushed (?:me|us) into \w+ing\b|"
    r"burn(?:ed|t) me (?:out|a copy|a cd)\b)", re.I)


# A part taken out is the same kind of report and the word alone is not, because "i have a sweet
# tooth" is not a harm. It was answered "Sounds alright. Anything good in it?", and "i had my
# appendix out last week" was answered "Nice one. How did the rest of it go?" - the same flat
# report in another part.
_A_PART_OUT = re.compile(
    # the verb is droppable, because people say "my appendix out last week" and "my tooth out on
    # friday": the part and what happened to it are the report, and the verb in front is optional.
    r"\b(?:(?:had|have|having|needed|need|getting|got)\s+)?(?:to have\s+|to get\s+)?"
    r"(?:a|an|my|two|some|the)\s+(?:tooth|teeth|wisdom tooth|wisdom teeth|molars?|"
    r"appendix|tonsils?|adenoids|gallbladder|gall bladder|kidney stone|cataract|"
    r"splinter|ingrown nail|nail)\s+"
    r"(?:out|removed|taken out|pulled|drained)\b", re.I)


# A number of months is a prognosis when it is what a person has been given or what they have
# left: "i've been given six months" was answered "You've been given six months, how long have you
# been at it?", which is the worst reply in this file. The money and notice shapes say the same
# number for something that ends rather than a life, so they are read out first.
_A_PROGNOSIS = re.compile(
    r"\b(?:been given|given|been told (?:i (?:have|'ve|have got|got)|there (?:is|are))|"
    r"told i (?:have|'ve|have got|got))\s+(?:about\s+|only\s+|maybe\s+|perhaps\s+)?"
    r"(?:a|two|three|four|five|six|nine|ten|twelve|eighteen|a few|a couple of)\s+"
    r"(?:more\s+)?(?:days|weeks|months|years)\b"
    r"|\b(?:two|three|four|five|six|nine|ten|twelve|eighteen|a few|a couple of)\s+"
    r"(?:more\s+)?(?:weeks|months|years)\s+(?:left|to live|at most|maybe)\b"
    r"|\b(?:terminal(?:ly)? (?:ill|illness|cancer)|palliative care|in a hospice|"
    r"end of life care)\b", re.I)


# The same words for a thing that ends, not a life: a payment plan, a notice period, a sentence.
_A_PROGNOSIS_THAT_IS_NOT = re.compile(
    r"\b(?:to pay|to repay|to clear|to save|to appeal|to file|to finish|to complete|"
    r"notice|sentence|probation|tenancy|contract|lease|to build|to train|to study|"
    r"to sell|to deliver|warranty|guarantee|to get out of)\b", re.I)
