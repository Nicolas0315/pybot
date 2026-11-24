"""Part 2 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from . import facts, named, not_a_trip
from .facts import a_limit_on_the_plan
from .ack_part_01 import (
    OCCASIONS, PLACES_WITH_THE, SHOWER,
)


# Words that turn the word after them into a thing rather than a place: an errand is "to the
# tip", a visit is "to my mum's", and neither is somewhere you have "been before".
THING_BEFORE = frozenset(("a", "an", "the", "my", "your", "his", "her", "our", "their"))


# A plan that has already happened is not a plan: "we went to spain in july" is a report and
# falls through to the ordinary reply.
PAST_PLAN = frozenset("went was were been came returned back".split())


# A trip is said with one of these verbs, a date it is coming on, and somewhere it goes. The
# three together are what make it a trip rather than an errand: "i'm going to the gym tomorrow"
# and "i'm going to see my mum this weekend" have the verb and the date, and the place is what
# tells them apart.
TRIP_VERB = re.compile(
    r"\b(?:going|gonna|off|flying|fly|flies|flew|driving|heading|travelling|traveling|sailing|"
    r"holiday|land|lands|landed|landing|arriv\w+|touch(?:es)? down|getting in|got in|get in)\b",
    re.I)


DESTINATION = re.compile(r"\b(?:to|off to|into)\s+(?:the\s+|a\s+|an\s+)?([a-z][a-z'\u2019-]*)",
                         re.I)


# Half the country says the trip by its arrival rather than its departure: "we land in lisbon on
# friday", "i arrive in rome on tuesday", "we fly into palma". Those lines have the verb and the
# date and name a place, and "to" alone threw them out - they were filed as news ("Noted: you
# land in lisbon on friday.") instead of answered about Lisbon. Only an arrival verb may take
# these prepositions: "in" after any other verb is not a destination ("im going in for a scan").
ARRIVE_VERB = re.compile(
    r"\b(?:land|lands|landed|landing|arriv\w+|touch(?:es)? down|fly|flies|flew|getting in|"
    r"got in|get in)\b", re.I)


DESTINATION_ARRIVAL = re.compile(
    r"\b(?:in|at|into)\s+(?:the\s+|a\s+|an\s+)?([a-z][a-z'\u2019-]*)", re.I)


NOT_A_TRIP = frozenset("""
    bed sleep work school college uni university gym doctor doctors dentist hospital shops shop
    town meeting interview court loo toilet hairdresser optician vet nursery see visit watch pick
    collect drop get take it that this them there here him her us me you

    appointment appointments scan scans checkup check-up clinic physio physiotherapy chiropractor
    midwife blood test tests xray x-ray hearing hearings trial trials court courts tribunal prison prisons
    jail jails cell custody remand probation solicitor lawyer

    funeral funerals burial cremation wake wakes

    be being been
    tesco asda sainsbury sainsburys morrisons lidl aldi coop co-op iceland waitrose supermarket
    office bank post
    """.split())


DATE_AHEAD = re.compile(
    r"\b(?:next|this|tomorrow|tonight|weekend|"
    r"in (?:january|february|march|april|may|june|july|august|september|october|november|"
    r"december|spring|summer|autumn|winter)|"
    r"on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"for (?:a|an|one|two|three|four|five|six|seven|eight|\d+) (?:(?:more|whole|extra) )?"
    r"(?:day|night|week|fortnight|month)s?)\b", re.I)


# The line says, in its own words, that the day is not one to look forward to: "i hate weddings",
# "im dreading it", "i cant face it", "not looking forward to it", "i dont want to go". "have
# to" and "got to" are already read as an obligation before this is reached.
DREADED_OCCASION = re.compile(
    r"\b(?:hate|hates|hated|dread|dreads|dreading|dreaded|can'?t face|cant face|"
    r"not looking forward|dont want to go|don'?t want to go|dont fancy|don'?t fancy|"
    r"cant be bothered|can'?t be bothered|a drag|boring|obligated)\b", re.I)


# A trip whose length the person has already said does not want to be asked how long it is:
# "you're going to portugal for a week in may. How long are you going for?" is the bot asking
# what it was just told.
HOW_LONG_ALREADY = re.compile(
    r"\bfor (?:a|an|one|two|three|four|five|six|seven|eight|\d+)\s*"
    r"(?:day|night|week|fortnight|month|weekend)s?\b|\bfor the weekend\b|\bfor a few days\b",
    re.I)


def reads_as_a_trip(clean):
    """"trip", "occasion" or None: a plan that is coming, told to a friend.

    A friend answers "we're going to spain in july" with something about Spain, and an occasion
    with something about the day, not with a coach's "what's the first step you're unsure
    about?". The composer asks this so a trip is not read as a project with a first step, and
    the echo asks it so it can answer the trip rather than file it. Only another person's trip
    is left alone: "my sister is going to spain in july" is not the speaker's to be asked
    about.
    """
    if not isinstance(clean, str) or not clean.strip():
        return None
    flat = " ".join(clean.lower().split())
    if not DATE_AHEAD.search(flat) or OBLIGED.search(flat):
        return None
    if set(re.findall(r"[a-z']+", flat)) & PAST_PLAN:
        return None
    if flat.startswith(("my ", "her ", "his ", "their ", "she ", "he ")):
        return None
    if not TRIP_VERB.search(flat):
        return None
    destination = DESTINATION.search(flat)
    if not destination and ARRIVE_VERB.search(flat):
        destination = DESTINATION_ARRIVAL.search(flat)
    if not destination or destination.group(1) in NOT_A_TRIP:
        return None
    # The word after "to" is not always the place: "im going to my uncles funeral next week"
    # names the funeral two words later, and "we're going to spain for work in may" says work.
    # The four words after "to" are where an appointment, a relative or a job is named, so any
    # of them being one of those ends the reading - a trip lost is a stock reply, a scan read as
    # a holiday is a wrong answer.
    after_to = re.findall(r"[a-z'’]+", flat[destination.start():])[1:5]
    if not_a_trip.not_a_destination(after_to, after_to[0] if after_to else ""):
        # The word after "to" is a doing, not a place: "im going to wait till next year" was read
        # as a trip to Wait and answered "What do you want to do while you're there?". The trip
        # reader and this echo read the same list in `not_a_trip`, so the two cannot drift.
        return None
    if set(after_to) & NOT_A_TRIP:
        return None
    if set(after_to) & OCCASIONS:
        if "shower" in after_to and not set(after_to) & SHOWER:
            return None
        # An occasion they have already said they are dreading is not one to be told they are
        # looking forward to: the words of the line are the guard, not the occasion itself.
        return "occasion_flat" if DREADED_OCCASION.search(flat) else "occasion"
    # A word that is not a place: "to the tip", "to my mum's", "to a friend's". A trip is off to
    # somewhere it can be flown to, driven to or looked forward to, and a thing with an article
    # or a possessive in front of it is neither - except for the places that keep their "the".
    head = after_to[0] if after_to else ""
    if head in THING_BEFORE or head.endswith(("'s", "’s", "s'")):
        named = after_to[1] if len(after_to) > 1 else ""
        two_word = " ".join(after_to[1:3])
        if not (head == "the" and (named in PLACES_WITH_THE or two_word in PLACES_WITH_THE)):
            return None
    if not head:
        return None
    return "trip"


# Something they do on a set day, or keep doing: "on a tuesday" is a habit, "on tuesday" is one
# particular Tuesday, and only the article tells them apart.
HABIT = re.compile(
    r"\b(?:every (?:day|week|month|morning|evening|afternoon|weekend|other day)|"
    r"every (?:mon|tues|wednes|thurs|fri|satur|sun)day|"
    r"each (?:day|week|morning)|most days|most weeks|twice a (?:day|week|month)|"
    r"once a (?:day|week|month)|on (?:a|an) (?:monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday))\b", re.I)


# Still going on, or just started, against something that is over: "i've started swimming again"
# and "i'm trying to save money" want to know how it goes, "it came out really well" does not.
GOING = re.compile(r"\b(?:i(?:'ve| have) (?:been |just )?started|i(?:'ve| have) (?:taken up|got into|signed up)|i(?:'m| am) (?:trying|getting|"
                   r"working|building|writing|learning|practising|practicing)|i(?:'ve| have) been|"
                   r"started (?:again|back)|back (?:into|at) it)\b", re.I)


# A habit someone has been landed with is not a routine to admire: "i have to top the boiler up
# every week" said back as "that's a proper routine" is the bot mistaking a chore for a hobby.
# The obligation is the line, and it keeps the stock reply.
OBLIGED = re.compile(r"\b(?:have to|has to|had to|must|got to|gotta|need to|needs to|keeps|"
                     r"kept|constantly|always|every time|end up|ends up)\b", re.I)


# Something that keeps happening to them is not a routine: "i cry every morning", "i get panic
# attacks every week", "i shout at my kids every morning" said back as "that's a habit now" is the
# coldest line the bot can say, and worse than the stock line it replaces. A feeling, a symptom or
# an outburst at someone is the line, whatever shape it has.
FEELING = re.compile(
    r"\b(?:cry|cries|cried|crying|tears|sob\w*|weep\w*|panic\w*|anxious|anxiety|depress\w*|"
    r"numb|shak\w*|nightmares?|insomnia|miserable|upset|self[- ]harm\w*|hurt(?:ing)? myself|"
    r"feel(?:s|ing)? (?:low|down|awful|rubbish|empty|worthless)|"
    r"shout\w* at|yell\w* at|scream\w* at|swear\w* at|hit(?:s|ting)? (?:my|the|him|her|them)|"
    # A body that keeps being sick is not a routine either: "i throw up every morning" was said
    # back as "that's a habit now", which is the coldest line the bot has.
    r"sick|sickness|vomit\w*|throwing up|threw up|throw up|nausea|nauseous|diarr\w*|"
    r"migraine\w*|angry|furious|rage|lash(?:ing)? out)\b", re.I)


# A tail that asks how it is going is wrong for a line that says it is going badly, and the
# complaint is answered by the modules that read it as one.
GOING_BAD = re.compile(r"\b(?:badly|not|never|can'?t|cant|won'?t|wont|too much|too many|"
                       r"stop|stopped|give up|gave up|fail\w*|struggl\w*|hard|tough|"
                       r"shattered|exhausted|knackered|late|behind|broke)\b", re.I)


# Some facts are not just a thing about them: they limit what is worth suggesting. Saying back
# "your budget is 6,000 pounds" and stopping makes the store look like a notebook; a friend says
# what they will do with it. The echo is the same either way, the ending is what changes.
# A stated budget is a limit, and the person saying it is usually about to ask for something
# inside it, so the echo ends with the first thing to do with the figure rather than stopping at
# "I'll stick to that": "my budget is 300 a month" got a receipt and nothing else.
BUDGET_FRAMES = (
    "{Thing} \u2014 I'll keep any suggestions inside it: fixed bills and food first, then savings.",
    "{Thing}, then \u2014 I'll stick to that: fixed bills and food first, then a set amount to "
    "savings.",
    "{Thing} \u2014 noted, and I'll work within it: fixed bills and food first, then savings on "
    "payday.",
)


# A budget for a thing is not a budget to live inside. "my budget is about 40 pounds" said
# during a question about a present for a dad is the money to spend on the present, and the
# living-income ending - "fixed bills and food first, then savings" - answers a household budget
# nobody asked about: the person wanted to know what to buy with forty pounds. A stated period is
# what makes it a budget to live inside ("my budget is 300 a month"); with no period, a
# conversation that was about buying a thing makes it money to spend.
PERIOD = re.compile(r"\b(?:(?:a|an|per|each|every)\s+(?:day|week|fortnight|month|year)\b"
                    r"|weekly|monthly|fortnightly|yearly|annually|a month|in a month|"
                    r"a week|in a week)\b", re.I)


# A figure for a stretch of time is money to live on whatever follows it: "i have 40 quid for the
# week", "ive got 200 pounds for the rest of the month", "i have 500 for the rest of the month".
# `PERIOD` above only sees a bare "a week" or "a month", so these went past it and the "for the"
# in them was read as naming a purchase. None of them has a thing in it at all.
A_SPAN_OF_TIME = re.compile(
    r"\bfor\s+(?:the\s+(?:rest\s+of\s+)?(?:week|fortnight|month|year|day)\b"
    r"|this\s+(?:week|month|year)\b|next\s+(?:week|month|year)\b"
    r"|last\s+(?:week|month|year)\b|the\s+rest\b"
    r"|a\s+(?:week|fortnight|month|year|day)\b|an?\s+hour\b)", re.I)


# The words above all say the purchase with a verb. A line can say it without one, by naming what
# the figure is for: "ive got 200 pounds for a new bike", "my budget for a sofa is 600". Read
# without it, those lines got the living-income ending - "fixed bills and food first, then
# savings" - for money that was never a month to live inside.
FOR_A_THING = re.compile(r"\b(?:\d[\d,.]*|a few|a couple of|about)\s*(?:pounds?|quid|euros?|"
                         r"dollars?)?\s*(?:budget\s+)?for\s+(?:a|an|the|my|our|some|new)\b"
                         r"|\bbudget\s+for\s+(?:a|an|the|my|our|some|new)\b", re.I)


BUYING = re.compile(r"\b(?:buy|buys|buying|present|presents|gift|gifts|"
                    r"shopping for|looking for a|looking for some|looking for new|"
                    r"should i get|shall i get|which one|get (?:my|him|her|them|myself)|"
                    r"spend on|worth getting|what to get|need (?:a|some|new|another)\b|"
                    # A thing being taken on is a thing being bought, whatever verb carries it:
                    # "im thinking of getting a bike", "im after a new sofa", "i want a cat",
                    # "we are getting a kitten", "im planning a holiday", "i want to redecorate
                    # the bedroom" all got the household ending ("fixed bills and food first,
                    # then savings") to a question about what to spend the money on. Only the
                    # endings change here, and only when the line names no period and the rest
                    # of the chat holds no money word, so a budget to live inside keeps its own.
                    r"getting (?:a|an|one|some|new)\b(?!\s*(?:lot|bit|break|rest|handle|hold|"
                    r"sense|grip|kick|chance|look|few|couple|little|better|worse|"
                    r"grief|telling|hearing|going|ready))|after (?:a|an|some)\b(?!\s*(?:lot|bit|"
                    r"advice|help|idea|good|thought|while|time|break|rest|sense|point))|"
                    r"want (?:a|an|some|one|to get|to buy)\b(?!\s*(?:lot|bit|break|rest|handle|"
                    r"hold|sense|grip|kick|chance|look|few|couple|little))|"
                    r"planning (?:a|an|some|my|our)\b|moving (?:into|in|to|out|house|home)\b|"
                    r"redec\w+|renovat\w+|refurbish\w*)", re.I)


# The buying words are not proof of a purchase on their own: "i need a budget plan",
# "i need some help with money" and "i am looking for a job" wear them too, and the sentence about
# bills and food is the only advice in those turns. A money word in the rest of the conversation
# keeps the living reading.
MONEY = re.compile(r"\b(?:money|loan|loans|pension|pensions|mortgage|mortgages|credit card|"
                   r"credit cards|overdraft|debt|debts|savings|insurance|benefits|"
                   r"universal credit|job|jobs|salary|wage|wages|tax|budget|budgets|plan|"
                   r"planner|finances?|rent|bills?|groceries)\b", re.I)


# A stated budget is not always a month to live inside: "I'm looking for a sofa / my budget is
# about 600" is money to spend on a thing, and the ending about fixed bills and food is an answer
# to a different question. Same fact, different ending.
SPENDING_FRAMES = (
    "{Thing} \u2014 I'll keep what I suggest inside it.",
    "{Thing} \u2014 good, and everything I suggest will be within it.",
    "{Thing} \u2014 noted, and I'll stay under that with what I recommend.",
)


FOOD_FRAMES = (
    "{Thing} \u2014 I'll keep that in mind when I suggest food.",
    "{Thing}, good to know \u2014 I'll plan around it.",
    "{Thing} \u2014 noted, and I won't suggest anything that goes against it.",
)


# A condition said out loud ("im coeliac", "im diabetic") is a fact about their body, not
# news: it is said back like any other, and one that rules out a food says what the bot will do
# with it, the way a diet does. "Noted!" for "im coeliac" is the line that could have come
# before any message at all.
# A drink is not food. "You don't drink - I'll keep that in mind when I suggest food" is wrong in
# a chat about a party or a wedding, and said back it is the line STYLE.md rules out: a stock phrase
# that fits any message. The same frame without the food does the job.
DRINK_FRAMES = (
    "{Thing} \u2014 I'll keep that in mind for anything I suggest.",
    "{Thing}, good to know \u2014 I'll plan around it.",
    "{Thing} \u2014 noted, and I won't suggest a drink that goes against it.",
)


CONDITION_FOOD = {"coeliac": "gluten", "celiac": "gluten", "gluten intolerant": "gluten",
                  "lactose intolerant": "dairy"}


CONDITION_FRAMES = (
    "{Thing} \u2014 noted, and I'll keep {food} out of anything I suggest.",
    "{Thing}, good to know \u2014 I'll plan around the {food}.",
    "{Thing} \u2014 right, so nothing with {food} in it.",
)


# A limit that belongs to somebody they named - "my mum is allergic to shellfish", "my dog is
# allergic to chicken" - is kept the same way, and it is no more news than their own: said back as
# "Noted: your mum is allergic to shellfish" it is the filing cabinet again, and the warm line
# already exists in the file for the day the store files it as theirs by mistake. Only the ending
# changes: the allergy is not the speaker's, so the bot cannot say it will keep food out of what it
# suggests for them, and it can say it will remember it for the next time it comes up.
OTHER_LIMIT_FRAMES = (
    "{Thing} \u2014 I'll keep that in mind for anything I suggest.",
    "{Thing}, good to know \u2014 I'll work around it.",
    "{Thing} \u2014 right, so that is off the table for them.",
)


# A limit on what the plan can be - "nothing too tiring", "no long walks", "my sister can't walk
# far", "we need to keep it cheap", "not too much walking" - is a constraint, not a mood and not
# a symptom. The person is saying what to leave out, and the replies that read it as one of those
# have not heard it: "Fair enough \u2014 what's going on, then?" answers a line that named no feeling,
# and "How long has that been going on with your sister?" turns a short walk into an illness to
# date. The reading of the limit is bot.memory.facts.a_limit_on_the_plan, because the store must
# not file one as a plan; what is here is what the bot does with it.
#
# The tail is chosen by what the limit is on - feet, money, or neither - and never by the words of
# the line, so it cannot be pasted onto another message.
LIMIT_FRAMES = {
    "move": (
        "{Thing} \u2014 so anything I suggest stays short and flat, with somewhere to sit.",
        "{Thing}, then. Nothing I put to you needs hours on your feet.",
        "{Thing} \u2014 noted, and I'll keep the days gentle and close to a seat.",
    ),
    "money": (
        "{Thing} \u2014 so I'll keep what I suggest to what costs nothing.",
        "{Thing}, then. Nothing that needs paying up front.",
        "{Thing} \u2014 noted, and nothing pricey in anything I put to you.",
    ),
    # The same walking limit, on a stay rather than on a day out: a guest who cannot manage the
    # stairs is a question about the bed and the bathroom, and the day-out frame ("short and flat,
    # with somewhere to sit") answers a trip they are not on. The card about hosting went round
    # three times in a row instead, because nothing here had a frame for the plan it was on.
    "move_stay": (
        "{Thing} \u2014 so it is the downstairs room or a bed moved down, a chair in the shower "
        "rather than a step over the bath, and the outings one at a time.",
        "{Thing}, then \u2014 book the bed that needs no stairs and keep the week's outings short "
        "and near a seat.",
    ),
    "other": (
        "{Thing} \u2014 noted, and I'll keep anything I suggest inside it.",
        "{Thing}, then \u2014 I'll plan around it and keep what I suggest inside it.",
    ),
}


# A plan that is somebody coming to stay, and a plan that is a trip away. The frames are written
# for one or the other, so the limit has to know which plan it has landed on.
A_STAY_PLAN = re.compile(
    r"\b(?:coming|comeing|come|comes|staying|stays|stay|stopping|to stay|visiting|visit)\b"
    r"|\b(?:we|i)(?:'re| are| am)?\s+having\s+(?:people|family|guests|my|her|his)\b", re.I)


# A trip is a place they are going, not every plan the store knows: "im trying to lose weight"
# is a plan and a day out is not what it is, and the day-out frame answers a walk nobody is on.
A_TRIP_PLAN = re.compile(
    r"\b(?:going to|off to|heading to|away to|flying to|driving to|trip to|holiday|weekend away|"
    r"going away|staying near|in (?:june|july|august|september|october|november|december|"
    r"january|february|march|april|may))\b", re.I)


A_STAY_PERSON = re.compile(
    r"\b(?:mum|mam|mom|mother|dad|father|parents|gran|grandma|grandad|granny|nana|nan|"
    r"grandpa|grandparents|sister|brother|aunt|uncle|cousin|in laws|in-laws|mother in law|"
    r"father in law|friend|friends|guest|guests|visitors|family)\b", re.I)


def _the_plan_in_hand(memory, clean=""):
    """Which plan the last few turns are on: "stay", "trip", or None.

    A limit only means something against the plan it is a limit on, and the two plans want
    different frames: a guest who cannot manage the stairs is a bed and a bathroom, while a person
    who cannot walk far on a day out is a short, flat route. Read from the line itself and the
    last few turns, so a limit said with nobody planning anything is still the pools' business.
    """
    lines = []
    if isinstance(clean, str) and clean.strip():
        lines.append(clean)
    if isinstance(memory, dict):
        for turn in reversed((memory.get("turns") or [])[-PLAN_TURNS:]):
            said = turn.get("user") if isinstance(turn, dict) else None
            if isinstance(said, str) and said.strip():
                lines.append(" ".join(said.split()))
    for said in lines:
        if A_STAY_PLAN.search(said) and A_STAY_PERSON.search(said):
            return "stay"
    for said in lines:
        if A_TRIP_PLAN.search(said) and not a_limit_on_the_plan(said):
            return "trip"
    return None


# What a line may have given the store and still be only a limit: the person it is for, or a
# detail of the thing on the table. Anything more ("her back is bad", a plan) is a fact of its own
# and keeps the reply that fact would get.
_LIMIT_ONLY = frozenset(("people", "relations", "other", "others", "relation", "detail"))


# A line that opens with an ask word is a question, whatever words it has later: "what can i cook
# on a budget" carries a budget and is still the cheap-meals question, and the knowledge base
# answers it. Only a line with nothing to ask gets the limit said back.
_OPENS_WITH_AN_ASK = re.compile(
    r"^\s*(?:what|which|how|where|when|who|why|should|shall|can|could|would|will|do|does|"
    r"did|is|are|was|were|any|anyone|anything|tell me|give me|suggest|recommend)\b", re.I)


# A stated like is not something to file and read back. "i love pizza" was answered "Noted: you
# love pizza." - the filing cabinet, on the one kind of line where the person has just told you
# what they are like and given you an opening. The dislike said out loud is answered with a
# question about the thing ("Fair enough. What is it about mushrooms?"), so the like gets the same
# shape turned round: the person's own words said back with one question about the thing. Not
# every ending asks, because a question at the end of every reply reads as an interview, and the
# thing is the whole echo rather than the bare noun, so "i love the sea" keeps its "the" and "i
# love my dog" keeps its "my" - "Sea - what is it you like about it?" is the bot talking about a
# sea in general. A like that carries a second half ("i love pizza but the price is mad") keeps
# the plain frame, because the half is a fact of its own to answer (see a_liked_thing).
LIKES_FRAMES = (
    "{Thing} \u2014 what is it you like about it?",
    "{Thing} \u2014 what is it about it that gets you?",
    "{Thing}. Good to know \u2014 what do you like best about it?",
    "{Thing} \u2014 that goes in the keep pile. I'll remember it.",
)


# A like with a second half in it ("i love pizza but the price is mad") is not one thing named,
# and the thing comes out of the store with the second half still on it: "Pizza but the price is a
# good one" is a sentence about nothing. Only a thing of a few words with nothing that joins two
# clauses gets the like's own endings; anything longer keeps the plain frame it had.
A_LIKE_OF_ONE_THING = re.compile(r"^(?!(?:.*\b(?:and|but|because|so|though|although|when|if|"
                                 r"which|that)\b)).{2,40}$", re.I)


# The endings above say "it", so the line has to name one thing the person likes and nothing else
# that could be the "it": a line with two tastes in it ("you don't like fish but you love prawns"),
# somebody else's taste ("she likes crime dramas, you like comedy"), a second clause ("you love
# cooking, you do it most nights"), a comparison ("you like food more than churches") or a choice
# ("the one you like is 650") is answered by the plain frame, which claims nothing about a thing.
# The whole echo is tested rather than the stored thing, because the echo is what the reply says.
A_LIKE_ECHO = re.compile(
    r"^(?:you|we)\s+(?:really\s+|absolutely\s+|just\s+|still\s+|also\s+|do\s+|both\s+)?"
    r"(?:love|like|adore|enjoy|prefer)\s+(?P<thing>[^,;]+)$", re.I)


A_LIKE_WITH_TWO_HALVES = re.compile(
    r"\b(?:and|but|because|so|though|although|when|if|which|that|than|too)\b", re.I)


# Somebody they like is a person, and "what is it you like about it" turns them into a thing.
A_PERSON_LIKED = re.compile(
    r"\b(?:girl|boy|man|woman|guy|bloke|lad|lass|person|someone|somebody|people|they|them|him|her"
    r"|his|hers|theirs)\b", re.I)


def _only_a_liking(found):
    """Whether the line filed a like and nothing else worth an answer of its own.

    The same guard as `_just_a_liking`, but a pet said in the like ("i love my dog") is not a
    second thing to answer: the store files the animal and then answers "Noted: you love your
    dog." A name, a job or a limit in the same line is a fact of its own and keeps its own ending.
    """
    rest = {key for key, value in (found or {}).items()
            if value and key not in ("tastes", "pets") and not key.endswith("_frame")}
    return bool((found or {}).get("tastes")) and not rest


def a_liked_thing(found):
    """The thing a stated like is about, or "" when the line filed no like.

    Only "how" of "yes" is a like: "i hate mushrooms" files the same shape with "no", and the
    dislike is answered by the composer's own question about the thing.
    """
    for entry in (found or {}).get("tastes") or []:
        if not isinstance(entry, dict) or str(entry.get("how") or "") != "yes":
            continue
        thing = " ".join(str(entry.get("thing") or "").split()).strip(" ,.:;!?")
        if (thing and "{" not in thing and "}" not in thing
                and len(thing.split()) <= 4 and A_LIKE_OF_ONE_THING.match(thing)):
            return thing
    return ""


# A limit on what a person can do needs no plan to be about: "she is 8 months pregnant and cant
# walk far" is the walking, and the plan is whatever comes next.
_AN_ABILITY = re.compile(
    r"\b(?:can'?t|cannot|can not|isn'?t able to|is not able to|not able to|only manage)\s+"
    r"(?:walk|climb|manage|stand|sit)\b"
    # The same limit said with the thing in it: "she cant do stairs" is what a person says about
    # the guest they are making a bed up for, and it has to reach the plan they are on rather than
    # be said back as a fact. The verb is fixed so an aside ("i cant do this", "cant do monday")
    # is not a limit on anything.
    r"|\b(?:can'?t|cannot|can not|isn'?t able to|is not able to|not able to|only manage)\s+"
    r"(?:do|manage|get\s+up|get\s+up\s+and\s+down|get\s+up\s+the|use|cope\s+with)\s+"
    r"(?:the\s+|a\s+|any\s+)?(?:more\s+)?(?:stairs?|steps?|hills?|walks?|walking|"
    r"climbing|standing)\b", re.I)


# How many turns back a plan still counts as the plan a limit is on. A limit said out of the blue
# is a remark about their life ("im on a budget", "im not very energetic"), and the pools that
# answer those already have the right thing to say: the knowledge base has the cheap-meal answer
# and a feeling is a feeling. A limit said while a plan is on the table is about the plan.
PLAN_TURNS = 3


# What the person wants on the plan, said while they say the limit: "i want to keep it cheap",
# "we would rather not walk too much". The want is the plan, so the limit has something to be on.
WANTS_IT = re.compile(
    r"\b(?:i|we)\s+(?:want|wanna|need|'?d like|'?d rather|would like|would rather)\s+to\b", re.I)


def _a_plan_on_the_table(memory, clean=""):
    """Whether there is a plan for the limit to be about.

    A limit is a narrowing of something. Said on its own it is a remark about their life ("im on a
    budget", "im not very energetic"), and those are answered better by the pools that read a
    budget as the cheap-meals question and a mood as a mood. It is a limit on a plan when the plan
    was said in the last few turns, was filed by the store, or is being said here in the same
    breath ("i want to keep it cheap").
    """
    if isinstance(clean, str) and WANTS_IT.search(clean):
        return True
    if not isinstance(memory, dict):
        return False
    seen = 0
    for turn in reversed(memory.get("turns") or []):
        said = turn.get("user") if isinstance(turn, dict) else None
        if not isinstance(said, str) or not said.strip():
            continue
        seen += 1
        if seen > PLAN_TURNS:
            return False
        if facts.PLAN.search(said) and not facts.a_limit_on_the_plan(said):
            return True
        if (facts.extract(said) or {}).get("plan"):
            return True
    return False


# How much of the person's own line is worth saying back. "she cant manage stairs" and "no long
# walks" name the limit itself, and naming it is what confirms the bot heard the right thing. "my
# nan is 90 and she cant do stairs" is a whole sentence: said back in front of the advice it is the
# person's own words plus the filing cabinet, and the reply is better starting with what it will
# do. The same advice, without the name.
#
# Only the limits whose reply is about what the bot will keep out of the plan (feet, money, a
# stay): a job in hand is the other way round, where naming the thing IS the answer - "i still have
# the school run to sort" has to come back saying the school run goes first - so those families
# keep their frames however long the line is.
SAID_BACK_WORDS = 7


LIMIT_AFTER_THE_LINE = {
    "move": (
        "So anything I suggest stays short and flat, with somewhere to sit.",
        "Then nothing I put to you needs hours on your feet, and there is a seat at the end of it.",
    ),
    "money": (
        "So I'll keep what I suggest to what costs nothing.",
        "Then nothing I put to you needs paying up front.",
    ),
    "move_stay": (
        "Then it is the downstairs room or a bed moved down, a chair in the shower rather than a "
        "step over the bath, and the outings one at a time.",
        "Then book the bed that needs no stairs, and keep the week's outings short and near a seat.",
    ),
}


# A separation is the same kind of news as a death: the person the lines are about has gone.
# "my wife left me", "we split up in march", "he walked out". The verb is ordinary, so "left"
# only counts with ", me" after it - "my sister left and came back" is not this - and the rest
# are phrases nobody says about anything else.
# "broke up" and "split up" are ordinary verbs - a bill is split, a band breaks up - so the
# verb has to close its clause: "we split up the bill" takes an object and is not this.
UP_CLOSED = (r"(?!\s+(?:the|a|an|it|this|that|these|those|my|his|her|their|your|our|"
             r"into|over|between)\b)")


# "left me" is the same shape: "i left me keys at home", "she left me a note", "left me to
# it" all take an object. A person who has left is what the phrase is about, so the clause
# ends there or a preposition or time follows: "left me for someone else", "left me last
# week", "left me with nothing".
LEFT_CLOSED = (r"(?=\s*(?:[,.!?;]|$|\b(?:for|after|last|in|on|at|with|when|because|so|and|"
               r"since|about|yesterday|today|tonight)\b))")


SEPARATION = re.compile(
    r"\b(?:left me|leaving me)" + LEFT_CLOSED + r"|"
    r"\b(?:walked out on|dumped me|cheated on me)\b|"
    r"\b(?:broke up|split up)" + UP_CLOSED + r"|"
    r"\bdivorce\w*\b|"
    # "he moved out" and "we separated" need who: a lodger moves out and an egg white
    # separates, and neither is a marriage ending.
    r"\b(?:he|she|they|my (?:wife|husband|partner|boyfriend|girlfriend|ex))\b[^.!?]{0,16}"
    r"\bmoved out\b|\b(?:we|my \w+ and i) separated\b")


# How many turns back a death or a separation still sets the tone. Three is about as long as
# people stay on it before a turn about something else.
HEAVY_TURNS = 3


# A hurt somebody is doing to the person, not a loss and not a marriage ending: "my son is being
# bullied at school", "he hits me", "my boss is horrible to me". A fact told in that room is not a
# form to be filed either - "Got it - he's 11" after "my son is being bullied" is the same clerk
# with a different receipt - so the room is set by the last few turns here too.
# Every phrase names a person doing it, because the words themselves are ordinary: a knee hurts
# me, the play was a hit, a film was violent, she pushed me to try again. A body part is not a
# person, and a past participle with no one in front of it is not happening now.
_NOT_A_BODY_PART = (r"(?<!\b(?:my|his|her|their|your|our)\s)(?<!\b(?:the|a)\s)"
                    r"(?<!\b(?:knee|back|leg|legs|arm|arms|head|shoulder|shoulders|neck|foot|"
                    r"feet|hip|hand|hands|stomach|tooth|teeth|ear|ears|eye|eyes|chest|ankle|"
                    r"wrist|joint|joints|muscle|muscles)\s)")


_BULLIED = re.compile(
    r"\b(?:bull(?:y|ies|ied|ying))\b|\bpick(?:s|ed|ing)?\s+on\b|\bpicked\s+on\b|"
    r"\bpicks\s+on\b|\bmean\s+to\s+(?:me|him|her|them|us|my\b)|"
    r"\bpicked\s+on\s+(?:me|him|her|them|us)\b", re.I)


# A person (the one the line names) doing the verb to someone: "he hits me", "my son hits me",
# "they shout at him at school", "she swears at the kids".
HURTS_A_PERSON = re.compile(
    r"\b(?:he|she|they|my\s+\w+|his\s+\w+|her\s+\w+|the\s+\w+)\s+"
    r"(?:(?:hit|hits|hit(?:ting)?|punch\w*|kick\w*|shov\w*|"
    r"slap\w*|smack\w*|threaten\w*)\s+"
    r"(?:me|him|her|them|us|the\s+(?:kids|children|baby|little\s+one))\b"
    # "beats me" is also how everybody says they lost: a game word after the verb means the
    # person is telling you about a match, not about harm. "my son beats me at chess" was read
    # as cruelty and answered "I'm sorry it's all coming at once", which is sorry for somebody
    # over a chess result. Bare "he beats me" keeps its reading, and the other verbs are not
    # guarded because "hit me in the face" is exactly where a place word follows them.
    r"|(?:beat|beats|beating)\s+"
    r"(?:me|him|her|them|us|the\s+(?:kids|children|baby|little\s+one))\b"
    r"(?!\s*(?:at|in|on)\s+(?:the\s+|a\s+|his\s+|her\s+|their\s+)?[a-z]))"
    r"|\b(?:shout|shouts|shouting|swear|swears|swearing|yell|yells|yelling)\s+"
    r"(?:at|at)\s+(?:me|him|her|them|us|the\s+(?:kids|children|baby|little\s+one))\b"
    r"|\b(?:is|are|was|were|being)\s+horrible\s+to\s+(?:me|him|her|them|us)\b"
    # "my husband was violent last night", "abel was violent": the violence is the whole clause,
    # so it needs a person as its subject and nothing after it that makes it a film or a match.
    r"|\b(?:he|she|they|my\s+\w+|his\s+\w+|her\s+\w+)\s+(?:was|is|were|are|"
    r"has\s+been|had\s+been|got)\s+violent\b"
    r"|\b(?:violent|violence)\s+(?:to|towards|with|at)\s+(?:me|him|her|them|us)\b"
    r"|\b(?:was|were|am|is|being|been)\s+harass\w*\s+(?:at|on|in)\b", re.I)


# "abel was violent last night": a person is the whole subject of the clause, so the line opens
# with the name - and people type names in lower case. What keeps "the match was violent" and
# "the night was violent" out is not a list of things but the word in front: a determiner means
# the subject is a thing, and a name has none.
A_NAME_WAS_VIOLENT = re.compile(
    r"^\s*(?!(?:the|a|an|it|there|this|that|these|those|my|his|her|their|your|our|we|i|you|he|"
    r"she|they)\b)[a-z][a-z'\u2019-]*\s+"
    r"(?:was|is|were|are|has\s+been|had\s+been|got)\s+violent\b", re.I)


def reads_as_cruelty(said):
    """Whether this line says somebody is doing the person harm."""
    text = " ".join(str(said or "").split())
    if not text:
        return False
    if _BULLIED.search(text) or A_NAME_WAS_VIOLENT.search(text):
        return True
    return bool(HURTS_A_PERSON.search(text))


# After a death or a separation, a fact said plainly is not a form to be filed. "She took the
# kids to her mums" answered with "noted" is colder than the general line it replaced: the
# person has just told you where his children are in the week his marriage ended, and a clerk
# says "noted". The fact still comes back - telling the bot is a choice they made - with the
# acknowledgement attached, from a pool of its own so "noted" is never one of the endings.
# These are for a fact that is theirs and ordinary, which is why they are only reached when the
# fact does not limit anything (a budget, a diet, a condition keep the ending they explain).
HEAVY_FRAMES = (
    "{Thing} \u2014 I'm sorry it's all coming at once.",
    "Got it \u2014 {thing}. That's a hard week.",
    "{Thing}. I'm sorry there's so much on your plate.",
)


# The same room, for a fact that is not one more thing landing on them: the cats, the job, the
# town. "my dad died / i have two cats" answered "You have two cats \u2014 I'm sorry it's all
# coming at once" says the cats are part of the pile, which is a claim nobody made. These keep the
# acknowledgement off the fact itself, so the warm ending is about the week and not about the cats.
STILL_FRAMES = (
    "{Thing} \u2014 got it. And I'm sorry it's a hard time.",
    "{Thing}. Noted \u2014 and I'm sorry you're having a hard week.",
    "{Thing} \u2014 I've got that. Still sorry for what you're going through.",
)


# The lead-ins people put in front of a fact: they are not part of it.
# A lead-in is the word in front of the fact and never the subject of it: "and i eat 1200" is
# "i eat 1200" with a joining word on the front, so it is said back as "you eat 1200". The long
# forms "and i" and "also i" were here, and the longest match wins, so the joining word took the
# person with it: "and i eat 1500" was said back as "Eat 1500 - noted." and "and i work at
# mcdonalds" as "Work at mcdonalds", with no "you" in either. "and" and "also" are already here
# and leave the "i" where it belongs.
LEAD_IN = ("hi", "hiya", "hello", "hey", "so", "well", "oh", "and", "also", "ok", "okay", "right",
           "because", "cos", "coz", "cause", "cuz", "because of", "cos of",
           "yeah", "yes", "actually", "anyway", "btw", "by the way", "just so you know",
           "quick one", "sorry", "haha", "lol", "oh and", "for the record",
           "one thing", "that reminds me", "thanks", "thank you", "cheers", "ta", "cool",
           "sorry one more thing", "one more thing", "one last thing", "last thing",
           "nice", "great", "yep", "yup", "mmm", "haha",
           # A hedge in front of a fact is the way somebody says it, not part of the fact:
           # "to be honest i dont like my flat" was said back as "Noted: to be honest you
           # don't like your flat", which hands the person their own shrug instead of an
           # answer. These are the words chat-speak arrives as ("tbh" and "ngl" are expanded
           # before the store sees the line) and a hedge is only ever a way in.
           "to be honest", "to be fair", "if im honest", "if i am honest", "if im being honest",
           "honestly", "tbh", "to tell the truth", "truth be told", "not going to lie",
           "not gonna lie", "ngl", "i wont lie", "i have to say", "i must admit",
           "i will say", "ill be honest", "to be truthful")


# A greeting or a self-introduction is the chat module's turn, not an echo's.
# A line with a question word in it wants an answer, not the echo: "i don't know what to get
# my dad for his 60th" said back is nonsense, however many facts it carries.
WANTS_ANSWER = re.compile(r"\b(?:what|which|how|where|whereabouts|when|who|why|whats|hows|"
                           r"whos|wheres)\b", re.I)


GREETING = re.compile(r"^\s*(?:hi|hiya|hello|hey|morning|good morning|evening|yo|howdy)\b", re.I)


# Words about dying are never said back, whatever the line means by them: "i want to die my
# hair pink" is a hair appointment, and "you want to die your hair pink" still reads badly.
DEATH_WORDS = re.compile(r"\b(?:die|died|dies|dying|death|dead|kill|killed|suicide)\b", re.I)


# The hours someone works are the shape of their week, and people say them as a fact: "i work
# nights", "my shifts are all over the place", "i get up at five for work". Said back they are
# a filing cabinet - "Noted: you work nights." - which is the coldest answer to somebody telling
# you about their life, so the reply is about the life those hours make. Each pool is its own
# kind of week, and the line has to be only that: see NOT_THE_HOURS before any of them.
ON_NIGHTS = re.compile(
    r"\b(?:(?:i|we)\s+(?:work|works|do|does|am on|are on|am doing|are doing|'m on|'re on)\s+"
    r"(?:the\s+)?night(?:s|\s+shift(?:s)?)?\b"
    r"|night shifts?\b|\bon nights\b|\bnights this week\b)", re.I)


EARLY_RISE = re.compile(
    r"\b(?:i|we)\s+(?:get up|get|start|leave|wake up|am up|are up|have to be up|'m up)"
    r"\s+(?:at|by|for)\s+(?:\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm)?|four|five|six|seven|"
    r"half (?:four|five|six))\b", re.I)


LATE_FINISH = re.compile(
    r"\b(?:i|we)\s+(?:finish|finishes|get home|am back|'m back)\s+(?:at|around|about|by)\s+"
    r"(?:\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm)?|nine|ten|eleven|twelve|half (?:nine|ten|eleven))\b",
    re.I)


LONG_SHIFT = re.compile(
    r"\b(?:\d{1,2}|twelve|ten|eleven)\s*[- ]?hour (?:shift|shifts|days?)\b"
    r"|\blong (?:days|shifts)\b|\bwork(?:ing)? long hours\b", re.I)


SHIFTS_ALL_OVER = re.compile(
    r"\b(?:my|our|the)\s+(?:shifts?|rota|hours)\s+(?:is|are|change|changes|move|moves|rotate|rotates|"
    r"all over|all over the place|everywhere|different|random|mad)\b"
    r"|\bshifts? (?:all over|all over the place|everywhere)\b"
    r"|\bwork(?:ing)? two jobs\b|\bsecond job\b", re.I)


WORK_FROM_HOME = re.compile(r"\bwork(?:ing)? from home\b|\bwork from home\b|\bwfh\b", re.I)


# The hours pools. Tonight, the body clock, the week around them: each one says something about
# the life those hours make, and none of them is a question, because a question at the end of
# every reply is the other half of the stock line.
NIGHT_TAIL = (
    "Nights turn the week upside down. The sleep in the day is never quite the same as the sleep "
    "at night, and that is the part people underrate.",
    "Nights, then. It is a different world at three in the morning, and not many people see it.",
    "Nights are hard on the body clock. Whatever makes the sleep after a shift work is worth "
    "protecting.",
)


EARLY_TAIL = (
    "That is an early start. The night before is where those mornings are won or lost.",
    "Up at that hour, the whole day is done by lunchtime. It is the evening that has to be "
    "guarded.",
    "That is a hard hour to be up, and it gets easier once the going to bed moves with it.",
)


LATE_TAIL = (
    "Finishing that late means the evening has gone by the time you are out. The wind-down is the "
    "bit worth protecting.",
    "That is a long day by the time you are home. The last hour of it is the one to keep for "
    "yourself.",
    "Home at that hour, the day turns into the next one. Best to have the food and the quiet "
    "already waiting.",
)


LONG_TAIL = (
    "Those are long days. Whatever you do for yourself has to be small enough to happen when you "
    "are wrecked.",
    "Long shifts like that leave nothing of the day. The food and the sleep are the parts that "
    "actually matter.",
    "That is a lot of hours. The days off are not a bonus, they are the half of the week that "
    "makes the rest work.",
)


SPREAD_TAIL = (
    "Shifts that move make the week hard to plan. The few fixed things - sleep, one day off, a "
    "meal at a set time - are what hold it together.",
    "A rota like that means no two weeks are the same. Worth putting the things you care about "
    "in before the rota comes out, not after.",
    "That kind of week is hard to build anything on. Whatever is regular in it is doing a lot of "
    "the work.",
)


HOME_TAIL = (
    "Working from home, the day has no edges unless you put them in. A walk at the end of it "
    "stands in for the commute.",
    "That suits a lot of people and it eats a lot of people. The bit that helps is stopping at a "
    "time rather than when the work runs out.",
    "Home all day, the work and the rest end up in the same room. A door you can shut, or a walk "
    "out of it, does more than any system.",
)


# An ask in any of the shapes people type it - "should i nap in the afternoon", "how do i stop
# waking at four", "is it worth it". The line before a line of hours is what decides whether
# those hours are a new subject or a detail added to the answer just given.
AN_ASK = re.compile(
    r"^(?:(?:and|so|but|ok|okay|well|also|plus)\s+)*(?:should|shall|can|could|do|does|did|is|are|"
    r"was|were|will|would|may|might|am|have|has|any|what|whats|which|how|hows|where|wheres|"
    r"whereabouts|when|who|whos|why)\b", re.I)


def reads_as_an_ask(line):
    """Whether this line asks something, in a shape a person types."""
    return "?" in line or bool(AN_ASK.match(str(line or "").strip()))


# A line about the hours that also carries something else is that other thing's line: a body that
# cannot sleep, a job they are sick of, a wage that does not cover it, a shift they want out of.
# Asking for tips is an ask, whatever shape it is in.
NOT_THE_HOURS = re.compile(
    r"\b(?:cant sleep|can'?t sleep|not sleeping|insomnia|exhaust\w*|knackered|shattered|"
    r"burn(?:t|ed) out|depress\w*|anxi\w*|panic|stress\w*|fed up|sick of|had enough|"
    r"hate|hates|quit|quitting|resign\w*|sacked|fired|redundant|laid off|losing my job|lost my job|"
    r"overtime|pay|paid|wage|wages|money|salary|boss|manager|colleague|interview|contract|"
    r"holiday|annual leave|tips|advice|how do i|how can i|what should|should i|help me|"
    r"pregnant|baby|kids?|child|school run|uni|college|course|exam)\b", re.I)


# A deadline said on the turn after an answer ("its tomorrow", "on friday", "in three weeks")
# is the one thing that answer did not know, and it changes what the answer is worth: it was
# written for a person with room. Said back as a receipt it uses nothing - "Got it - it's in
# three weeks." - and said back as a shrug ("I'm listening - say more if it helps") it is the
# fallback not hearing it at all. The line has to name the clock and be about the clock alone,
# and the turn before has to be a real answer rather than a hello or a hedge.
WHEN_DETAIL = re.compile(
    r"^(?:and |oh |also |so |but )?"
    r"(?:(?:its|it's|it is|thats|that's|that is|were|we're|i'm|im)\s+(?:(?:on|in)\s+)?"
    r"|(?:on|in)\s+|and\s+)"
    r"(?P<when>"
    r"tomorrow|tonight|today"
    r"|this (?:weekend|week|morning|evening|afternoon)"
    r"|next (?:week|month|weekend|year)"
    r"|monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    r"|(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"
    r"\s+(?:days?|weeks?|months?)"
    r"|a (?:few|couple of) (?:days|weeks)"
    r"|a couple of (?:days|weeks)"
    r")"
    r"(?:\s+(?:away|left|to go))?\s*[.!]*$", re.I)


# A deadline comes in four shapes and each leaves a different amount of room, so each has its
# own pool: today and tonight are already running, tomorrow has today in front of it, a figure
# counted in days is one step a day, and only a week or more is room to do the whole thing.
WHEN_TODAY = re.compile(r"\b(?:today|tonight|this (?:morning|afternoon|evening))\b", re.I)


WHEN_TOMORROW = re.compile(r"\btomorrow\b", re.I)


WHEN_DAYS = re.compile(
    r"\b(?:this (?:week|weekend)|monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    r"|a few days|a couple of days)\b", re.I)


COUNTED = re.compile(r"\b(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"
                     r"\s+(days?|weeks?|months?)\b", re.I)


COUNT = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10}


def _shape_of(when):
    """Which kind of clock this deadline is: today, tomorrow, days, or room.

    "Two days" is not "three weeks": a figure counted in days leaves a step a day, and a figure
    counted in weeks or months is room to spread the whole thing out. The pools are one per shape
    so a deadline tonight never gets a sentence written for one three weeks off.
    """
    if WHEN_TODAY.search(when):
        return "today"
    if WHEN_TOMORROW.search(when):
        return "tomorrow"
    found = COUNTED.search(when)
    if found:
        number = COUNT.get(found.group(1).lower(), found.group(1))
        unit = found.group(2).lower()
        if unit.startswith("month"):
            return "room"
        if int(number) <= (5 if unit.startswith("day") else 1):
            return "days"
        return "room"
    if WHEN_DAYS.search(when):
        return "days"
    return "room"


# What the clock leaves, said as what to do with it rather than as a claim about the answer we
# gave: the bot knows the deadline and it knows the answer was advice, and it does not know what
# that answer assumed about time. A statement either way, and never a question at the end.
WHEN_TODAY_TAIL = (
    "{When}, so the first of it happens now: a small thing done today beats a better one that "
    "waits for a quiet hour.",
    "There is no day left to work up to it in. {When} is the day, so start at the first step.",
    "{When} is already here, which makes the part of it you were saving for later today's job.",
)


WHEN_TOMORROW_TAIL = (
    "Tomorrow, so today is the working day: the first step now beats a good plan for the morning.",
    "That leaves today for it. Do the part you would least like to be doing at the last minute.",
    "Tomorrow, then. Whatever in that needs two sittings has to have the first of them today.",
)


WHEN_DAYS_TAIL = (
    "{When} is one step a day rather than all of it at once: pick the first step and give it "
    "today.",
    "{When}, so count the days and put a step in each one. The last day is for checking, not "
    "starting.",
    "{When} only fits the whole of it if each day carries a bit of it: start today, not on "
    "the last one.",
)


WHEN_ROOMY_TAIL = (
    "{When} is enough time if you spread it: one small bit a week, and the last week only "
    "checking.",
    "{When} gives you room to do it properly. Start with the part you would least like to get "
    "wrong.",
)


# A time of day said for the thing we just answered is the same detail as a deadline one step
# finer: "im worried about my interview tomorrow" / "its at 10" is not a fact to file and hand
# back. It was answered two ways, both cold - the stock line ("Thanks for telling me - I'm here if
# you want to dig into any of that") when the reading was only the bare time, and the receipt
# ("Got it - the interview is at 10") when the line named the thing, which is the person's own
# line said back. The hour is kept and the answer above is aimed at it instead.
TIME_WORD = (r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
             r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)")


# The time with its own marker - "10am", "9:30", "half nine", "ten o'clock" - is a time whichever
# word is in front of it.
CLOCK_DETAIL = re.compile(
    r"^(?:and |oh |also |so |but )?"
    r"(?:(?:its|it's|it is|thats|that's|that is|were|we're|the\s+[a-z'-]+\s+is)\s+)?"
    r"(?:at\s+|for\s+)?"
    r"(?P<when>"
    r"\d{1,2}[:.]\d{2}\s*(?:am|pm|a\.m\.|p\.m\.)?"
    r"|\d{1,2}\s*(?:am|pm|a\.m\.|p\.m\.)"
    r"|\d{1,2}\s*o'?\s?clock"
    r"|(?:half|quarter)\s+(?:(?:past|to)\s+)?" + TIME_WORD +
    # "ten to four" is a time the same way "quarter to four" is: the minutes to the hour, which
    # the pattern above only had for the half and the quarter.
    r"|(?:five|ten|twenty|twenty[- ]five)\s+to\s+" + TIME_WORD +
    r"|" + TIME_WORD + r"\s+(?:o'?\s?clock|am|pm|a\.m\.|p\.m\.|thirty|fifteen|"
    r"forty[- ]five)"
    r"|\d{1,2}\s+(?:thirty|fifteen|forty[- ]five))"
    r"\s*[.!]*$", re.I)


# "its at 10" and "at ten" have no marker of their own, so the "at" is what makes them a time:
# without it a bare figure is a count ("i have 10") and a bare word is anything at all.
CLOCK_AT = re.compile(
    r"^(?:and |oh |also |so |but )?"
    r"(?:(?:its|it's|it is|thats|that's|that is|the\s+[a-z'-]+\s+is)\s+)?"
    r"(?:at|for)\s+"
    r"(?P<when>(?:\d{1,2}[:.]\d{2}|\d{1,2}|" + TIME_WORD + r")(?:\s*(?:am|pm))?)"
    r"\s*[.!]*$", re.I)


# The clock is not a deadline: it is an hour on a day, so the answer is aimed at the hour rather
# than spread out. A person with an appointment at ten has a run-up, and the part of the answer
# that wants them sharp belongs in it.
# Morning or afternoon decides which half of the day the hour eats: a scan at half nine has the
# run-up in it, and an appointment at 2:30 has a free morning in front of it. The pools are one
# each so a ten o'clock never gets a sentence written for half past two.
CLOCK_MORNING_TAIL = (
    "{At} on the day, so be there twenty minutes early and the nerves have somewhere to sit while "
    "you wait.",
    # The hour is an adverbial, never the subject of what follows: "At ten o'clock means..." and
    # "At ten o'clock leaves..." are sentences with no subject in front of the verb. So a frame
    # that goes on to say what the hour does carries its own subject, and the hour stays in it.
    "{At}, so the day is built around it, and the bit that wants you sharp belongs before you "
    "set off rather than after.",
    "{At}, so there is enough of the morning to get ready without rushing it, which is usually the "
    "part that decides how it goes.",
)


CLOCK_AFTER_TAIL = (
    "{At}, so the morning is free for the part that needs you sharp, and nothing else has to fit "
    "round it.",
    "{At} on the day: get the other jobs done in the morning so you go into it with nothing else "
    "on your mind.",
    # Not "{At}, and the clear morning is where...": "and" after the hour leaves the clause it
    # opens without a subject, and this is the frame an afternoon hour lands on one time in three.
    "{At}, so the morning is where the part that wants a steady head goes, and the afternoon is "
    "clear for it.",
)


# The things a person sits down for at an hour, beyond the diary words the date reader already
# knows: "i need to see a dentist this week and im dreading it" names no appointment, and the
# reply to the hour after it was the receipt again.
#
# This list is the appointments, and only the appointments, because both pools it opens with talk
# about nerves and a run-up. A shift, a class, a viewing and lunch with a sister have an hour too,
# and none of them has a morning to build or a nerve to settle: those are in CLOCK_FLAT below.
CLOCK_EVENT = re.compile(
    r"\b(?:dentist|dental|optician|hygienist|doctor|gp|surgery|vet|clinic|hospital|"
    r"hearing|interview|appointment|scan|exam|test|checkup|check-up|consultant|physio|"
    r"physiotherapy|podiatrist|chiropodist|midwife|blood\s+test|presentation)\b", re.I)


# An hour on the day that nobody is nervous about: "im meeting my sister for lunch" / "its at 1"
# got "so the morning is where the part that wants a steady head goes", and a night shift at 10pm
# got told the morning was free - the opposite of the day the person has. One flat pool for these,
# with no claim about the morning and no nerves in it.
CLOCK_FLAT = re.compile(
    r"\b(?:meeting|viewing|shift|class|lesson|lecture|rehearsal|assessment|haircut|tattoo|"
    r"collection|pickup|lunch|dinner|breakfast|drinks|supper)\b", re.I)


CLOCK_FLAT_TAIL = (
    "{At}, then, and the rest of the day arranges itself round it rather than the other way round.",
    "{At} on the day, so what comes before it is short and what comes after it is free.",
    "{At}, so the day is built round it and nothing else has to be squeezed in before it.",
)


CLOCK_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
               "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
               "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
               "nineteen": 19, "twenty": 20}


def _clock_shape(when):
    """Which half of the day the hour is in: "morning" or "after".

    "At ten" is the morning, "at 2:30" is the afternoon, and "half nine" is half past nine in the
    morning - so a bare figure in the early hours is read as the afternoon, which is what a
    person means when they say an appointment is at two.
    """
    said = str(when or "").lower()
    found = re.search(r"\d{1,2}|[a-z]+", said)
    if not found:
        return "morning"
    token = found.group(0)
    hour = CLOCK_WORDS.get(token) if not token.isdigit() else int(token)
    if hour is None:
        return "morning"
    if "pm" in said or "p.m" in said:
        return "after"
    if "am" in said or "a.m" in said:
        return "morning"
    if hour <= 3:
        return "after"
    return "morning" if hour < 12 else "after"
