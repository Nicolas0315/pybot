"""Part 9 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import last_bot, last_user
from . import (harm, no_eyes, stepwords)

from .fallback_data import (
    FAVOURITE_GENERAL,
    FAVOURITE_WORDS,
    JUDGE_BARE_FACES,
    JUDGE_FINE,
    JUDGE_NOD_WORDS,
    JUDGE_NOT_A_GERUND,
    JUDGE_NOT_A_VERDICT,
    JUDGE_NOUN,
    JUDGE_NO_PLAN,
    JUDGE_NO_PLAN_FINE,
    JUDGE_NO_PLAN_MAD,
    JUDGE_NO_PLAN_MIND,
    JUDGE_ONLY_A_PLAN,
    JUDGE_PLAN_HAS_A_HOLE,
    JUDGE_PLAN_STOP,
    JUDGE_SANE,
    JUDGE_SELF_JUDGING,
    JUDGE_SOUNDS_FINE,
    JUDGE_WISH_ANGRY,
    JUDGE_WORTH,
    LIVE_INDOOR,
    LIVE_KINDS,
    LIVE_NEWS_REPLY,
    LIVE_ROAD_NAME,
    LIVE_SITE_THING,
    LIVE_VENUE,
    TASTES,
    YOURS,
)

from .fallback_part_01 import (
    STUCK_ON_A_PERSON, _the_person_ends_the_ask, _matchable, _has,
)
from .fallback_part_06 import (
    DISLIKE_OWN, DISLIKE_OWN_SELF,
)
from .fallback_part_08 import (
    JUDGE_PLAN_OPENING, JUDGE_SHOULD_OPENING, JUDGE_ANSWERS_FIRST, JUDGE_ACT_AT_SOMEONE, JUDGE_ASK,
    JUDGE_ASK_BARE, JUDGE_HOPED_FOR, JUDGE_NAMES_A_HOLE, MIND_WORRY, _in_a_care_thread,
)


def _the_person_they_are_stuck_on(clean):
    """The person named in "i dont know what to do about my mum", faced back at them."""
    found = STUCK_ON_A_PERSON.search(clean)
    if not found or not _the_person_ends_the_ask(found.group("rest")):
        return ""
    who = _yours(found.group("who"))
    # `_yours` faces "my" back at the person but leaves "our": "what do i do about our son" came
    # back as "our son", which is the pair's child said by the wrong one of them.
    if who.lower().startswith("our "):
        who = "your " + who[4:]
    return who


def _yours(thing):
    """The thing as the person would hear it said back to them: their `my` becomes `your`."""
    return DISLIKE_OWN.sub("your", DISLIKE_OWN_SELF.sub("yourself", thing))


# A card that opens on its own heading - "Yes: an easy hour on a bike burns roughly 300 to 400
# calories", "No: a dog left alone all day will chew" - has ruled on the question the card answers,
# not on the plan the person has put down since. The colon is how this bot's knowledge cards open,
# and reading it as a spoken "Yes," is how a plan put down for a verdict was answered with nothing:
# "i plan to cycle 100 miles with no training" / "is that daft" got the search hedge, because the
# card above it began "Yes:" and the verdict stood down as already given. A spoken ruling keeps its
# comma ("Yes, once, and make it easy to answer"), so only the heading is read here.
JUDGE_A_CARD_HEADING = re.compile(r"^\W*(?:yes|no)\s*:\s", re.IGNORECASE)


# An act against somebody, something illegal, or harm to their own body is not a plan to bless,
# whatever the words: "i want to drink a bottle of wine every night", "smoke weed every day", "lie
# on my cv", "stop paying tax" all walked through the fence the harm words had.
JUDGE_NOT_A_PLAN_TO_BLESS = re.compile(
    r"\b(?:drink|drinking|booze)\b(?:\s+\w+){0,6}?\s+"
    r"(?:every\s+(?:night|day|evening)|(?:a|one)\s+bottle|a\s+night|nightly|daily)\b"
    r"|\b(?:smoke|smoking|vape|vaping)\s+(?:weed|pot|dope|skunk|crack|heroin|coke|cocaine|speed)\b"
    r"|\b(?:weed|pot|cocaine|heroin|crack)\s+every\s+(?:day|night)\b"
    r"|\blie\s+(?:on|in)\s+(?:my|the)\s+(?:cv|resume|application|tax\s+return)\b"
    r"|\b(?:stop|stops|evade|evading|dodge|dodging)\s+paying\s+tax\b|\btax\s+evasion\b"
    r"|\bfiddle\s+(?:my\s+)?(?:tax|taxes|expenses|hours)\b"
    r"|\bclaim\s+(?:benefits|housing\s+benefit|universal\s+credit)\s+(?:i(?:'m| am)\s+not|"
    r"i\s+shouldnt|i\s+shouldn'?t)\b", re.IGNORECASE)


# What people say instead of the verb: nobody says "i want to steal", they say where from. The
# object is the tell, so the source is what this reads - work, the till, the shop - and a loan from
# a person or their own savings stays an ordinary plan.
JUDGE_TAKING_SOMETHING = re.compile(
    r"\b(?:take|taking|took|nick|nicking|pinch|pinching|borrow|borrowing|"
    r"help\s+myself\s+to|helping\s+myself\s+to)\b(?:\s+\w+){0,5}?\s+"
    r"(?:from|out\s+of)\s+(?:work|the\s+till|the\s+shop|the\s+office|the\s+company|"
    r"the\s+stockroom|the\s+warehouse|the\s+club|stock)\b", re.IGNORECASE)


# There is no ordinary plan that is lying to somebody: unlike "cheat on my diet", the person lied
# to is a person, so the words alone are the tell.
JUDGE_LYING = re.compile(r"\b(?:lie|lying|lied)\s+(?:to|about)\b", re.IGNORECASE)


# The one thing that looks like a hit and is not: "i want to smash my goals", "i want to hit my
# numbers". They are targets, and a verdict on a target is the ordinary kind.
JUDGE_A_TARGET = re.compile(
    r"\b(?:smash(?:ing)?|hit(?:ting)?|beat(?:ing)?|punch(?:ing)?|kick(?:ing)?)\s+"
    r"(?:(?:my|your|his|her|their|our)\s+)?"
    r"(?:goals?|personal\s+bests?|pbs?|records?|targets?|numbers?|deadlines?|quota|quotes?)\b",
    re.IGNORECASE)


# Taking is never a plan to bless, whatever the object: there is no version of "i want to steal
# from work" that a verdict may say is fine. What is left out is the taking that is not taking -
# "steal a few hours", "steal the show" - because those are plans like any other.
JUDGE_TAKING = re.compile(
    r"\b(?:steal|stealing|shoplift|shoplifting|rob|robbing|mug|mugging|"
    r"burgle|burgling|hack|hacking|blackmail|blackmailing|defraud|defrauding)\b"
    r"(?!\s+(?:a\s+few|time|the\s+(?:show|scene|limelight|spotlight|march|day)|"
    r"a\s+(?:march|kiss|glance|look|moment|nap|day)\b))",
    re.IGNORECASE)


# A wish against the person themselves, or one nobody could take a verdict on from here: starving
# themselves, and money at a scale that is the money entry's question and not this one's.
JUDGE_WISHES_HARM = re.compile(
    r"\b(?:stop|stopping|quit|quitting|give\s+up|giving\s+up|cut\s+out|cutting\s+out)\s+"
    r"(?:eating|food|meals)\b"
    r"|\b(?:eat|eating|ate)\s+nothing\b|\bstarve\s+myself\b|\bmake\s+myself\s+sick\b"
    r"|\bpayday\s+loan\b|\bloan\s+shark\b|\bgambl(?:e|ing)\b|\bbet\s+(?:my|our|the)\b"
    r"|\bborrow\s+(?:a\s+)?[\u00a3$\u20ac]?\d{3,}", re.IGNORECASE)


# ...unless the line names the thing being judged: "was that a bad idea" is the same ask as "was
# that stupid", and only the bare "is that bad" is the one that means somebody else's news.
JUDGE_JUDGES_A_NOUN = re.compile(
    r"\b(?:bad|terrible|awful|dreadful|wrong)\s+" + JUDGE_NOUN + r"\b", re.IGNORECASE)


# A reply above that already made the decision leaves the turn alone: the dog answer ends "If that
# sounds fine rather than like a sacrifice, get one", which is the verdict, and a second one on top
# of it is the weaker answer. The test is the last sentence, because that is where an answer puts
# what it thinks the person should do: a reply that ends on a step ("Ask when you will hear back")
# has given advice, not a verdict, and the turn is still this one's.
JUDGE_DECISION_LEAD = re.compile(r"^(?:if|unless|so|then|otherwise|either|worth)\b", re.IGNORECASE)


# A hole of the person's own body or their own medicine is not a plan to weigh: the answer there
# is the health one, and a friend does not say "that is the part to answer for" about a week off
# somebody's tablets.
JUDGE_HOLE_SAFETY = re.compile(
    r"\b(?:skip|skipping|stop|stopping|pause|pausing|come\s+off|coming\s+off)\s+"
    r"(?:my|the|your)?\s*(?:medication|meds|tablets|pills|insulin|treatment|doses?)\b"
    r"|\bmeds\b|\bmedication\b", re.IGNORECASE)


# The faces that ask for a ruling on a plan and nothing else, so the hole in the plan can be
# answered rather than deferred to an entry that has no word to match.
JUDGE_ASKING_FOR_A_CAUTION = frozenset("""stupid daft dumb silly idiotic thick bad terrible awful
    dreadful wrong good great sensible wise smart clever reasonable mad crazy insane nuts mental
    unhinged""".split())


JUDGE_JUDGEMENT = re.compile(
    r"\b(?:is|would be)\s+(?:a\s+)?(?:good|bad|fine|great|sensible|wise)\s+idea"
    r"|\bworth\s+(?:doing|it|a\s+(?:go|try))\b|\bnot\s+worth\b"
    r"|\bgo for it|\bhold off\b", re.IGNORECASE)


# The plan openings that put either a step or a place after the "to": "im going to learn
# spanish" and "im going to the gym". Every other opening of a plan ("want to", "thinking of",
# "planning to") is an infinitive, so what follows its "to" is a verb.
JUDGE_MOVING_TO = re.compile(r"\b(?:" + stepwords.MOVING_TO + r")\s*$", re.IGNORECASE)


def _the_opening_before(match):
    """The words of the line in front of the plan the opener matched: "im going to"."""
    for group in ("plan", "plan2", "plan3", "plan9"):
        if match.group(group):
            return match.string[:match.start(group)]
    return ""


def _a_gerund(word):
    """True when the word is an "-ing" form a sentence can open on ("getting", "moving")."""
    word = word.strip(".,!?;:'\"")
    return len(word) >= 5 and word.endswith("ing") and word not in JUDGE_NOT_A_GERUND


# The word that opens a noun phrase rather than a verb phrase: after "im thinking about a cat" the
# words left over are "a cat", and "wanting to a cat" is not English. The "to" is only right where
# what follows is what the person would do, so a phrase that opens on one of these takes "wanting"
# alone ("wanting a cat", "wanting more time off").
A_NOUN_PHRASE_OPENS = frozenset((
    "a", "an", "the", "my", "your", "our", "their", "his", "her", "its", "some", "any", "more",
    "less", "another", "one", "two", "three", "both", "all", "no", "nothing", "none", "it",
))


def _a_plan_said_back(phrase):
    """"wanting to quit your job", or "wanting a cat" where the words are a thing and not a step."""
    words = phrase.split()
    opening = "wanting " if words and words[0].lower() in A_NOUN_PHRASE_OPENS else "wanting to "
    return opening + _yours(phrase)


def _a_plan_phrase(said):
    """The person's plan as a phrase to say back ("wanting to ask for a pay rise"), or "".

    Nothing is made up: the words are theirs, only the opening is folded into a phrase that fits
    in front of a sentence. A plan with a clause in it ("quit my job but keep the flat") is left
    alone, because saying half of it back reads as not having listened.
    """
    text = _matchable(said)
    match = JUDGE_PLAN_OPENING.search(text)
    if match:
        words = (match.group("plan") or match.group("plan2") or match.group("plan3")
                 or match.group("plan9") or "").split()
        if not words or len(words) > 7 or any(word in JUDGE_PLAN_STOP for word in words):
            return ""
        phrase = " ".join(words)
        if not re.search(r"[a-z]", phrase) or not re.search(r"[a-z]{3}", phrase):
            return ""
        if _a_gerund(words[0]):
            return _yours(phrase)  # "getting a rescue dog" is already the shape a sentence wants
        if JUDGE_MOVING_TO.search(_the_opening_before(match)) and not stepwords.a_step(words[0]):
            # "im going to the gym", "im going to spain in may", "im going to bed early tonight":
            # the words after the "to" are where they are going, not a step, and "wanting to the
            # gym" is not a sentence. They go back behind their own "going to".
            return _yours("going to " + phrase)
        return _a_plan_said_back(phrase)
    match = JUDGE_SHOULD_OPENING.search(text)
    if match:
        words = match.group("plan").split()
        if not words or len(words) > 7 or any(word in JUDGE_PLAN_STOP for word in words):
            return ""
        if not re.search(r"[a-z]{3}", " ".join(words)):
            return ""
        return _a_plan_said_back(" ".join(words))
    return ""


# The plan is said back as the person put it, so their "my job" has to become "your job" on the
# way out: "nothing daft about wanting to quit my job" reads as the bot talking about itself.
MINE = re.compile(r"\b(my|me|myself|mine)\b", re.IGNORECASE)


def _yours(phrase):
    """The person's own phrase turned to face them: "quit my job" -> "quit your job"."""
    return MINE.sub(lambda found: YOURS.get(found.group(1).lower(), found.group(1)), phrase)


def _the_plan_on_the_table(memory):
    """The plan the person has just named, or "" when the last thing they said named none."""
    return _the_plan_and_its_line(memory)[0]


def _the_plan_is_the_last_thing_said(plan_line, memory):
    """True when nothing but a nod has been said since the plan was named.

    The plan is read from the last few turns, so a subject put down in between is read past:
    "im thinking of getting a cat" / "my knee is clicking" / "is that a good idea" is a question
    about the knee, and the pool's confident "yes, getting a cat is a reasonable thing to aim at"
    rules on the cat. The reading is right; it is the remembering that reaches back past the
    change of subject. So a verdict is given while the person has said nothing else since: a nod
    ("ok then", "right") keeps the plan, and a turn with a subject of its own ends it. A turn
    that shares a word with the plan ("i had a sugar craving" after a plan to give up sugar) is
    still about the plan, so lunch is a new subject but the craving is not.
    """
    said = [_matchable(turn.get("user")) for turn in (memory.get("turns") or [])
            if isinstance(turn, dict)]
    said = [line for line in said if line]
    about = {word for word in re.sub(r"[^a-z0-9 ]", " ", plan_line).split()
             if len(word) > 2 and word not in JUDGE_NOD_WORDS}
    for stop in range(len(said) - 1, -1, -1):
        if said[stop] == plan_line:
            break
    else:
        return True  # not read from this list at all: the reader knows more than this does
    for line in said[stop + 1:]:
        content = [word for word in re.sub(r"[^a-z0-9 ]", " ", line).split()
                   if len(word) > 2 and word not in JUDGE_NOD_WORDS]
        if not content or about & set(content):
            continue  # a nod, or a turn still about the plan
        return False
    return True


def _the_plan_and_its_line(memory):
    """The plan, and the line that named it: "not insured" is in the line, not in the phrase."""
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(turns[-4:]):
        said = _matchable(turn.get("user"))
        if not said or not [word for word in said.split() if word not in JUDGE_NOD_WORDS]:
            continue  # a nod or an "ok then": keep looking for the line that named something
        plan = _a_plan_phrase(said)
        if plan:
            return plan, said
        if JUDGE_PLAN_OPENING.search(said) or JUDGE_SHOULD_OPENING.search(said):
            # The line named a plan this pool cannot say back in one phrase (too long, or with a
            # clause in it): it is still the plan on the table, and the caller must not ask the
            # person to name it again. So the line comes back with no phrase.
            return "", said
        # A line with something in it that is not a plan ("my sister is ill") says nothing about
        # what the plan is, and stopping here would throw away the plan named a turn earlier:
        # "im going to quit sugar" / "ok then" / "is that stupid" still has one on the table.
    return "", ""


def _the_reply_above_judged(memory, past_a_question=False):
    """True when the bot's last answer already said what the person should do about the plan.

    "im thinking of getting a rescue dog" is answered with the three questions that decide it, and
    it ends on the decision - "if that sounds fine rather than like a sacrifice, get one" - so the
    person's follow-up "is that a good idea" has already been answered, and a verdict bolted on top
    of it ("yes, that is a reasonable way to do it") is the weaker of the two. The answer to the
    pay-rise advice ends on a step ("ask when you will hear back"), which is advice and not a
    verdict, so that turn is still this one's.
    """
    said = (last_bot(memory) or "").strip()
    if not said:
        return False
    if JUDGE_A_CARD_HEADING.match(said):
        # "Yes: butter is mostly fat ..." is a card's heading, not a ruling on the plan that came
        # after it. The verdict is still this turn's to give.
        return False
    if said.endswith("?") and not past_a_question:
        # The bot asked them something ("what's the part that's under your skin?"): that question
        # is what this turn is for, and a verdict pasted over it ignores what the bot just said.
        return True
    if JUDGE_JUDGEMENT.search(said) or JUDGE_ANSWERS_FIRST.match(said):
        return True
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", said) if part.strip()]
    last = sentences[-1] if sentences else said
    return bool(len(last.split()) <= 20 and JUDGE_DECISION_LEAD.match(last))


# The line that put a place on the table: a trip going, booked or hoped for. Read from the
# person's own turn, never from the bot's, because the bot's answer names the town too.
TRIP_NAMED = re.compile(
    r"\b(?:going to|going away|off to|holiday to|holidays? in|trip to|weekend in|week in|"
    r"flying to|driving to|booked (?:a |our |the )?(?:trip|holiday|flights?|hotel|weekend)|"
    r"thinking of going|thinking about going|hoping to go|planning to go|visiting)\b", re.I)


# A trip is to a place, and half of the words that come after a verb of going are not places at
# all: "we are visiting my mum in hospital tomorrow" then "is it ok" is a question about the visit,
# "we are going to a wedding in june" then "is it nice" is a question about the wedding, and "im
# going to see the doctor about my knee" then "is it worth it" is the knee's. All three reached
# this pool on the verb of going alone and lost the card that was answering them ("However it
# looks today, ask the ward what they expect next" for the hospital visit). The place the person
# is asking about is what the trip is to, so a line carrying one of these words is not a place.
NOT_A_PLACE = re.compile(
    r"\b(?:hospital|doctors?|dentist\w*|gp|clinic|a&e|ward|surgery|appointment|scan|"
    r"results?|wedding|funeral|christening|baptism|court|work|school|nursery|college|uni|"
    r"university|gym|physio\w*|therapy|therapist|vets?|interview|meeting|party|gig|concert|"
    r"match|church|prison|jail|care home|tip|dump|shops?|supermarket|swimming|parents|"
    r"mum|dad|mother|father|sister|brother|nan|nana|grandma|grandad|gran|friend|family|"
    r"cinemas?|pictures|theatres?|theaters?|films?|movies?|screening|exhibition|"
    r"galler(?:y|ies)|musicals?|opera|ballet)\b",
    re.I)


# The whole of the ask: "is it nice", "is it any good", "was it busy", "is it worth going", and
# the same with the mark on the end. Only words of judgement, so "is it far" and "how do i get
# there" stay with whatever can answer them.
PLACE_EVALUATIVE = re.compile(
    r"\b(?:nice|good|any good|worth (?:it|going|a visit|the trip|seeing)|busy|expensive|cheap|"
    r"quiet|lively|packed|safe|warm|sunny|rainy|boring|ok|okay|family friendly)\b", re.I)


PLACE_OPENER = re.compile(r"^(?:is|was|are|were|do|does|did|would|will|any)\b", re.I)


def a_verdict_on_their_plan(clean, memory, past_a_question=False):
    """The composer's verdict on the plan the person has just put down, or None.

    The public name, for modules that have to know what this file would say before they claim the
    line. `bot/modules/chat.py` reads it: its own reply to "is that a good idea" is a hand-back
    ("the decision is yours to weigh"), and a hand-back must not take the turn from this answer,
    which rules on the plan ("Yes - getting a cat is a reasonable thing to aim at"). One reading,
    used by both, so the two cannot drift apart.
    """
    return _a_verdict_on_their_plan(clean, memory, past_a_question)


def _a_verdict_on_their_plan(clean, memory, past_a_question=False):
    """The pool for "is that a stupid idea", or None when the line is not asking for a verdict."""
    # A question mark on the end is how the question is typed, not part of it. Every form of this
    # ask is anchored to the end of the line, so "is that a stupid idea?" - the way nearly everyone
    # writes it - matched nothing and got the search hedge, while the same words with no mark got
    # the verdict. The mark (and a stray full stop or comma) comes off before the line is read.
    said = _matchable(clean).rstrip(" ?.!,")
    asked = JUDGE_ASK.match(said)
    if not asked:
        bare = JUDGE_ASK_BARE.match(said)
        if not bare or not (bare.group("bare_noun")
                            or bare.group("face") in JUDGE_BARE_FACES):
            return None
        if not _the_plan_on_the_table(memory):
            # "stupid?" with nothing on the table is not a question about anything the bot can
            # see; asking what the idea is belongs to the pools that do that, not here.
            return None
        asked = bare
    if _in_a_care_thread(memory):
        return None  # nothing glib straight after a bereavement, a crisis or an emergency
    face = (asked.group("face") or asked.group("face2") or asked.group("face3") or "").lower()
    if face in JUDGE_NOT_A_VERDICT and not JUDGE_JUDGES_A_NOUN.search(said):
        return None  # "is that bad" after somebody's news, whatever plan is on the table
    plan, plan_line = _the_plan_and_its_line(memory)
    stale = bool(plan_line) and not _the_plan_is_the_last_thing_said(plan_line, memory)
    if stale:
        # They have moved on to something else, so the plan two turns back is not what this ask is
        # about. The ask is answered the way it is answered with nothing on the table - "tell me
        # the idea in a line" - rather than with a verdict on the old plan.
        plan, plan_line = "", ""
    if plan_line and (JUDGE_NAMES_A_HOLE.search(plan) or JUDGE_NAMES_A_HOLE.search(plan_line)):
        # "skip my medication for a week", "put all my savings in bitcoin", "drive with no sleep":
        # the line names the part that makes it risky, so the verdict has nothing to judge and the
        # topic's own entry - the health one, the money one - is the answer that knows what to say.
        #
        # ...which holds only where an entry can answer. The ask here is the judgement and nothing
        # else ("is that daft"), so it says no word the entry could match, and standing down leaves
        # the floor: "i plan to cycle 100 miles with no training" / "is that daft" was told "I'd
        # rather not guess, a quick search online will get you a solid answer", and "im going to
        # put all my savings in bitcoin" / "is that a stupid idea" was told the same about the
        # person's own savings. The hole is the part a friend pushes back on, so the verdict names
        # it as the part to answer for instead of blessing the plan (`JUDGE_WORTH` would say
        # "Nothing daft in wanting to put all my savings in bitcoin") - except where the hole is
        # their own medicine or their own body, which is nobody's to weigh from here.
        if JUDGE_HOLE_SAFETY.search(plan_line) or JUDGE_HOLE_SAFETY.search(plan or ""):
            return None
        if face in JUDGE_ASKING_FOR_A_CAUTION:
            return [line.format(plan=plan, Plan=plan[:1].upper() + plan[1:])
                    for line in JUDGE_PLAN_HAS_A_HOLE]
        return None
    # The wish itself, before the pool is chosen: "is that a stupid idea" after "i want to key my
    # exs car" is not a plan to weigh up, and "is that a good idea" after "i want to stop eating"
    # is not one a verdict may agree with.
    if plan or plan_line:
        wish = " ".join(part for part in (plan, plan_line) if part)
        if not JUDGE_A_TARGET.search(wish) and (JUDGE_ACT_AT_SOMEONE.search(wish)
                                             or JUDGE_TAKING.search(wish)):
            said_back = harm.reply_for(plan_line, memory) if plan_line else None
            return [said_back] if said_back else list(JUDGE_WISH_ANGRY)
        if JUDGE_WISHES_HARM.search(wish) or JUDGE_TAKING_SOMETHING.search(wish) \
                or JUDGE_LYING.search(wish) or JUDGE_NOT_A_PLAN_TO_BLESS.search(wish):
            return None
    if plan_line and not plan:
        return None  # they named a plan; asking them to say it again is the worse answer
    if plan and _the_reply_above_judged(memory, past_a_question):
        if not JUDGE_HOPED_FOR.search(_matchable(plan_line)):
            return None  # the answer above already gave a verdict on this plan; it is the better one
        # They put the plan down as a hope or an intention - "im hoping to run a half marathon",
        # "im looking to rent out my spare room" - and the answer above already went as far as it
        # can, so there is no verdict to add. The words keep the reply they had before the plan was
        # readable at all: asking which idea it is reads as not having listened, and a verdict
        # pasted over the answer above is the weaker of the two. Except where the caller has said
        # the question mark was not an answer (`past_a_question`): then the plan is still the
        # plan and the pool is still the one to give.
        plan = ""
    if not plan and asked.group("face3"):
        # "am i mad" / "am i being daft" with nothing put down is a worry about their own mind or
        # their own worth, not a plan to rule on: "i feel stupid / am i being silly" is nobody's to
        # correct from here. When the line above is itself about their mind, standing down is not
        # enough - it lands on the annoyance pool - so that one is answered here.
        if MIND_WORRY.search(_matchable(memory.get("turns", [{}])[-1].get("user", ""))):
            return JUDGE_NO_PLAN_MIND
        return JUDGE_NO_PLAN_MAD if stale else None
    if not plan:
        if face in JUDGE_SELF_JUDGING:
            return JUDGE_NO_PLAN_MAD
        if face in JUDGE_ONLY_A_PLAN:
            return JUDGE_NO_PLAN
        if face in JUDGE_SOUNDS_FINE:
            return JUDGE_NO_PLAN_FINE
        return None  # "is that bad" with nothing named is somebody else's question
    pool = JUDGE_SANE if face in ("mad", "crazy", "insane", "nuts", "mental", "unhinged") else (
        JUDGE_FINE if face in ("good", "great", "sensible", "wise", "smart", "clever",
                               "reasonable")
        else JUDGE_WORTH)
    # `Plan` is the same phrase opening a sentence: the pools are written as sentences, and
    # a template that puts it first cannot hold a lowercase word.
    return [line.format(plan=plan, Plan=plan[:1].upper() + plan[1:]) for line in pool]


# "whats my favourite food", "which is my favourite colour", "do you know my favourite film":
# the person's own favourite, not the bot's. Only the ask shape, so a line that mentions their
# favourite in passing ("what should i cook for my favourite person") is left alone. The thing
# asked about is kept: it is what the chat is searched for.
OWN_FAVOURITE = re.compile(
    r"\b(?:what|which)(?:'?s| is| was)?\s+(?:my|our)\s+(?:\w+\s+){0,2}(?:favourite|favorite)\s+(\w+)"
    r"|\b(?:do|can) you (?:remember|know)\s+(?:my|our)\s+(?:\w+\s+){0,2}"
    r"(?:favourite|favorite)\s+(\w+)")


# What the person said it was, in their own words earlier in this chat.
A_FAVOURITE_SAID = re.compile(r"\bmy (?:favourite|favorite) (\w+) (?:is|was|would be)\s+"
                              r"([^.,!?;]{1,40})")


# Said when the store has nothing to recall for it. It does not claim the person never said it:
# what they said may have been read as something other than a favourite, and asking again is right
# either way.
OWN_FAVOURITE_LINES = (
    "Remind me - which one is it?",
    "Say it again and I will keep it in mind: which one?",
    "I don't have that one. What is it?",
)


# Said back when the chat does hold it: "my favourite food is curry" then "whats my favourite
# food" is the person checking the bot was listening, and the answer is the thing they said, not
# the bot's own taste (which was what the taste table gave) and not a shrug.
THEIR_FAVOURITE_BACK = (
    "You said {value} - is that still the one?",
    "{Value}, as far as I have it. Has that changed?",
    "{Value}, you told me. Still the one?",
)


def _their_favourite_said(thing, memory):
    """What the person said their favourite <thing> was in this chat, or None."""
    if not thing:
        return None
    for turn in reversed((memory.get("turns") or [])[-12:]):
        if not isinstance(turn, dict):
            continue
        found = A_FAVOURITE_SAID.search(_matchable(turn.get("user") or ""))
        if found and found.group(1) == thing:
            value = found.group(2).strip()
            if value and " " not in value[:1]:
                return value
    return None


def _their_favourite_back(thing, value):
    """The pool above with the thing and the value the person gave filled in."""
    return tuple(line.format(value=value, Value=value[:1].upper() + value[1:])
                 for line in THEIR_FAVOURITE_BACK)


_VENUE_RE = []


def _names_a_venue(clean):
    """True when the line names one of the places in `LIVE_VENUE`, singular or plural."""
    if not _VENUE_RE:
        joined = "|".join(re.escape(word) for word in
                          sorted(LIVE_VENUE, key=len, reverse=True))
        _VENUE_RE.append(re.compile(r"(?<![a-z])(?:" + joined + r")(?:s|es)?(?![a-z])"))
    return bool(_VENUE_RE[0].search(clean))


def venue_hours_lines():
    """The composer's honest lines for a venue's opening hours."""
    for kind, _phrases, options in LIVE_KINDS:
        if kind == "hours":
            return frozenset(options)
    return frozenset()


# The day's news and results, and where the day's match is on. No card about the world can hold
# them - they change by the hour - so the honest answer says the bot cannot see them and names the
# one place that can. The ask has to be about how something went or where to find it: "the match
# wont light" is a matchstick, "how long is a match" is the rules and "how did the interview go"
# is the person's own day, so all three keep the answer they had.
LIVE_RESULT_ASK = re.compile(
    r"\b(?:who\s+won|who(?:['\u2019]?s|\s+is)\s+winning|did\s+[a-z][a-z' ]{0,20}?\s+win|"
    r"what(?:s|'s| is| was)?\s+the\s+(?:final\s+)?score|(?:any|the)\s+results?\b(?!\s+of))")


LIVE_BARE_RESULTS = re.compile(r"\b(?:any|the)\s+results?\b")


# "how did the match go" is a result; "how did the meeting go" is the person's own day, and the
# news line would answer a question nobody asked. So this one counts only beside a word that says
# what was played.
LIVE_HOW_IT_WENT = re.compile(
    r"\bhow\s+did\s+(?!(?:it|that|this|things|everything|you|i)\b)"
    r"[a-z][a-z' ]{0,20}?\s+(?:go|do|get\s+on)\b")


LIVE_TABLE_ASK = re.compile(
    r"\b(?:top|bottom)\s+of\s+the\s+(?:league|table)|in\s+the\s+(?:league|table)|"
    r"still\s+in\s+the\s+cup|out\s+of\s+the\s+cup|through\s+to\s+the\s+next\s+round")


LIVE_LISTING_ASK = re.compile(
    r"\b(?:what|which)\s+channel\b|\bwhere\s+(?:can|do)\s+i\s+watch\b|"
    r"\bis\s+it\s+on\s+(?:the\s+)?(?:tv|telly|iplayer|bbc|itv|sky)\b|"
    r"\bwhat\s+time\s+(?:is\s+)?(?:kick\s*off|does\s+(?:the|it)\s+(?:start|kick\s*off))|"
    r"\bwhat\s+time\s+(?:is|does|do|will)\b[^?]{0,30}?\b(?:start|starts|kick\s*off|begin|"
    r"kick-off|coverage|highlights)\b|"
    r"\bwhen\s+(?:is|are)\s+(?:the|we|they)\s+(?:next\s+)?(?:match|game|fixture)|"
    r"\bwhen\s+do\s+(?:we|they)\s+play\b")


LIVE_WORLD_ASK = re.compile(
    r"\b(?:latest|breaking|big|any)\s+news\b|\bnews\s+(?:today|tonight|this\s+morning)\b|"
    r"\b(?:in|from)\s+the\s+(?:news|world)\b|\bheadlines?\b|\bspill\s+the\s+news\b|"
    r"\b(?:happening|going\s+on)\s+in\s+the\s+world\b|\bwhat\s+the\s+news\s+is\b")


# "in the world" is the *scope* of a question that stands still, not the day's news: "what is the
# biggest city in the world", "the tallest building in the world", "how many people live in the
# world" all named the world as the place a fact holds, and all got "I can't see the news from
# here, sorry" - a shrug at a question with a settled answer. A news word in the line still makes
# it the news ("any news from the world", "whats going on in the world"), and "in the news" is
# left alone, because that is where a story lives.
_WORLD_AS_SCOPE = re.compile(r"\b(?:in|from)\s+the\s+world\b")


_A_NEWS_WORD_BESIDE = re.compile(
    r"\b(?:news|headlines?|happening|going\s+on|latest|breaking|stories|story)\b")


def _the_scope_of_a_standing_ask(clean):
    """True when "in the world" only says where a standing fact holds, so it is not the news."""
    if not _WORLD_AS_SCOPE.search(clean):
        return False
    return not _A_NEWS_WORD_BESIDE.search(_WORLD_AS_SCOPE.sub(" ", clean))


LIVE_SPORT = ("match", "game", "score", "scores", "football", "rugby", "cricket",
              "tennis", "boxing", "league", "cup", "final", "semi", "fixtures",
              "fixture", "kick off", "kick-off", "goal", "goals", "wicket", "innings",
              "test match", "playoffs", "play offs", "f1", "formula one", "grand prix",
              "the ashes", "the table")


# Their own news, not the world's: "any news from the hospital", "did my son win", "my exam
# results". A news site cannot answer those, so they are not this reader's.
LIVE_NOT_WORLDS = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:son|daughter|kid|kids|child|children|baby|wife|husband|"
    r"partner|mum|mom|mother|dad|father|brother|sister|friend|boss|exam|scan|test|interview|"
    r"application|case|claim|order|orders|delivery|parcel|package|refund|return|booking|"
    r"reservation|offer|mortgage|tenancy|landlord|visa|passport|complaint|payslip|pension|"
    r"insurance|quote|repair|job)\b|\bexam\s+results?\b|\bthe\s+(?:exam|interview|scan|audition|"
    r"appraisal|blood\s+test|driving\s+test|meeting|appointment|case|court|hearing|audition|"
    r"presentation|visit)\b|\b(?:my|our|his|her|their)\s+(?:blood\s+test|x-?ray|scan|results?)\b|"
    r"\bresults?\s+(?:from|of|at)\s+(?:(?:the|my|our|his|her|their)\s+)?"
    r"(?:doctor|gp|surgery|"
    r"hospital|scan|test|x-?ray|clinic|consultant|nurse|school|exam|dentist|vet)\b")


LIVE_A_YEAR = re.compile(r"\b(?:19|20)\d\d\b")


# The prize they bought a ticket for is not the day's news, and the news line asks for a story
# that does not exist: "did i win the lottery" and "did my ticket win" were sent to a news site
# (fancy-hawk). The draw word decides, so "did arsenal win" keeps the reader.
LIVE_OWN_DRAW = ("lottery", "lotto", "raffle", "sweepstake", "sweepstakes", "tombola",
                 "scratchcard", "scratch card", "bingo", "jackpot", "prize", "prizes",
                 "ticket", "tickets", "the draw", "numbers come up", "my bet", "the pools",
                 "competition", "euromillions")


# "did i win", with nothing else in the line, is the same ticket.
LIVE_A_BARE_WIN = re.compile(r"\bdid\s+(?:i|we)\s+win\s*[?.!]*$")


# "whos winning" on its own is about a game and nothing else: a score is what it asks for, so it
# is a line the scores reader takes without a question mark. With a subject after it ("whos
# winning the election") it is somebody else's question and this does not fire.
# A bare "who won" is left out on purpose: after "when was the battle of waterloo" it is the same
# question again, and the scores line would answer a history question with last night's football
# (pastname-multi-01 in the deck). Only the present tense is a game and nothing else.
LIVE_A_BARE_WINNING = re.compile(r"\bwho(?:['\u2019]?s|\s+is)?\s+winning\s*[?.!]*$")


# "any accidents on the m6" is a question said without a question mark, and it names the road and
# the thing asked about: the mishap is the live figure, so the words carry the ask.
LIVE_ANY_ACCIDENT = re.compile(r"\b(?:any|an?)\s+accidents?\b|\baccidents?\s+(?:on|at)\b")


LIVE_NEWS_LINES = (LIVE_NEWS_REPLY,)


def _the_scores_line():
    """The one honest line about a score or a table, or None.

    `bot/knowledge/sport.py` already answers "who won" and "the score" when no card does, with
    `_RESULTS_REPLY`, and the bot should say one thing about a result however the question is
    put. So the line is borrowed rather than written again here (fancy-hawk). It is read at call
    time because the knowledge tables import this package while they are built.
    """
    from ..knowledge.sport import _RESULTS_REPLY
    return (_RESULTS_REPLY,)


LIVE_LISTING_LINES = (
    "No live listings here, sorry. The TV guide on the box or the channel's own app has what is "
    "on and when, and the club's page has the kick-off and which side it is on.",)


LIVE_WHICH_RESULTS = (
    "Results of what - a match, an exam, or something you are waiting to hear about?",)


def _the_days_news(clean, asking):
    """The honest line for the day's news, a result or a listing, or None.

    "how did the match go" and "any news today" want the place the answer lives, not a guess; a
    line about the person's own news, a year in the line (history) or a contest that is not played
    keeps whatever answer it had.
    """
    if (LIVE_A_YEAR.search(clean) or LIVE_NOT_WORLDS.search(clean)
            or _has(clean, LIVE_OWN_DRAW) or LIVE_A_BARE_WIN.search(clean)):
        return None
    played = _has(clean, LIVE_SPORT)
    if LIVE_LISTING_ASK.search(clean) and played:
        return LIVE_LISTING_LINES
    if LIVE_TABLE_ASK.search(clean) and played:
        return _the_scores_line()
    if (LIVE_RESULT_ASK.search(clean)
            or (played and LIVE_HOW_IT_WENT.search(clean))):
        if LIVE_A_BARE_WINNING.search(clean):
            # "whos winning" is the score, not a story to read: a news site is the one place that
            # will not have it (vivid-feather).
            return _the_scores_line()
        if played:
            return _the_scores_line()
        # "did arsenal win" names a team by its own name, and "did labour win" a party: with no
        # word here that says what was played, the news line is the one that covers both.
        if LIVE_BARE_RESULTS.search(clean):
            return LIVE_WHICH_RESULTS
        return LIVE_NEWS_LINES
    if played and LIVE_TABLE_ASK.search(clean):
        return _the_scores_line()
    if LIVE_WORLD_ASK.search(clean) and not _the_scope_of_a_standing_ask(clean):
        return LIVE_NEWS_LINES
    return None


# The limit said plainly, for a line that asks whether the bot can look anything up and names
# nothing to look up. A yes/no about the bot deserves a yes/no, then the offer, then nothing else:
# the alternative was "I'm not sure about that one, sorry" plus a search suggestion, which is the
# bot hedging about itself.
CANNOT_ANYTHING = (
    "No - nothing live from this end: no searching, no pages, no today's figures. What were you "
    "after? I'll tell you what I know, and where to look the rest up.",
    "That's right, I can't look anything up. What I've got is what I know and whatever you tell "
    "me. What did you want checked?",
    "No, sorry - no browsing and nothing live. Say what it is and I'll do what I can with it, and "
    "name the place that has the rest.",
)


# Agreeing that the bot cannot do something. The line is a yes/no about the bot, not news and
# not a fact to file: "so you cant check the weather for me" said straight after the bot had
# said it had nothing live, and "you cant see my calendar can you". The last kind has no verb
# in it at all ("so no live news then"), so a bare "so no ... live/today" counts as well.
BOT_CANNOT = re.compile(
    r"\b(?:you|u|ya)\s*(?:cant|can't|cannot|can not|couldnt|couldn't|dont|don't|doesnt|"
    r"doesn't|wont|won't|arent|aren't|isnt|isn't)\b", re.I)


BOT_CANNOT_DO = re.compile(
    r"\b(?:check|look|see|tell|know|find|search|access|view|pull|get|open|connect|browse|"
    r"read|show|say|able|online)\b", re.I)


# Saying it cannot look something up is a claim about what the bot is for, so a line with nothing
# named in it ("you cant check anything can you") gets the whole limit said plainly.
BOT_CANNOT_LOOK = re.compile(
    r"\b(?:check|look|search|browse|online|internet|connect|open|view|access|find)\b", re.I)


# "you cant check anything can you" asks the whole question; "you cant open a jar with that" has the
# same words and is about a jar. Only a line that names nothing to look up and asks the bot about
# itself gets the plain limit.
CANNOT_ANYTHING_ASK = re.compile(
    r"\b(?:anything|any|whatever|at all|a thing|one thing|nothing)\b|"
    r"\b(?:can|could|do|does|are|will) (?:you|u)\b", re.I)


SO_NOTHING_LIVE = re.compile(
    r"\bso (?:no live (?:anything|news|weather|prices|times|scores)|nothing live|"
    r"no (?:news|weather|prices) (?:then|today|either))\b", re.I)


# The same denial, about one of the person's own records rather than anything live: "you cant see
# my calendar can you", "you cant read my emails either". There is no live pool for a calendar and
# no state word to make it an ask ("what's on my calendar" is a different line), so the answer is
# the limit itself plus the one thing the person can do about it. The record noun has to be there,
# or the arm would take "you cant see me can you", which is a joke with an answer of its own.
CANNOT_READ_YOURS = re.compile(
    r"\b(?:see|read|access|open|view|look (?:at|in)|check)\b[^.?!]{0,14}\b"
    r"(?:my|our|the)\s+(?:calendar|diary|inbox|emails?|mail|files?|folders?|notes?|photos?|"
    r"pictures?|messages?|texts?|documents?|screen|spreadsheets?)\b", re.I)


# A denial about the bot's eyes with nothing named in it: "you cant see anything can you", "you
# cant read anything". The words are the no-eyes reader's own ("see", "read"), so this is the same
# limit it says about a photo or a file, said once with nothing to point at. The line has to end at
# the bare thing or at a small asking tail, or it would take "you cant see anything in this light",
# which is about the light.
CANNOT_SEE_ANYTHING = re.compile(
    r"\b(?:see|read|look at)\b[^.?!]{0,12}\b(?:anything|nothing|a thing|any of it|any of them)\b"
    r"(?:\s+(?:at all|can you|could you|right|then|either|though|really|now))*[.?!]*\s*$", re.I)


CANNOT_SEE_ANYTHING_LINES = (
    "No, nothing on your side is visible to me - no pages, no photos, no files. I only get the "
    "words you type, and that is enough for most things: tell me what is in it.",
    "That's right, I can't see anything of yours. Type out the bit that matters and I'll work "
    "with it from there.",
)


CANNOT_YOUR_OWN = (
    "No, I can't see your diary from here - no calendar, no bookings, nothing of yours. Tell me "
    "what is in it and I'll work with that.",
    "Nothing of yours is in front of me, so no. Read out the lines that matter and I can help with "
    "what they say.",
    "I can't see your calendar or your plans, sorry - I only know what you tell me here. Give me "
    "the part that matters and it is as good as me having it.",
)


def _what_no_eyes_already_says(clean):
    """The line no_eyes already has for a named thing of theirs, or None.

    A screen, a photo, a file and an inbox each have their own honest line in `no_eyes`, and they
    are better than a general one about calendars: "you cant see my screen can you" wants the
    words-are-all-I-get line, not a list of records. Read here so the two cannot drift, the same
    way the body tables are read from this file.
    """
    for family, things in no_eyes.SEEING_FAMILIES.items():
        if re.search(r"\b(?:" + "|".join(re.escape(thing) for thing in things) + r")\b", clean):
            return no_eyes.CANNOT_SEE.get(family)
    return None


def _a_no_from_the_bot(clean):
    """True when the line only asks the bot to confirm it cannot do something."""
    text = clean or ""
    if SO_NOTHING_LIVE.search(text):
        return True
    return bool(BOT_CANNOT.search(text) and BOT_CANNOT_DO.search(text))


# The bare thing named inside a denial is not an ask the live pools recognise on their own:
# "trains" is not "train times", and "the news" on a line with no question in it never got as far
# as the pool. Only a denial takes this reading, so an ordinary chat about trains is untouched.
CANNOT_THINGS = (
    ("travel", ("train", "trains", "bus", "buses", "tube", "tram", "flight", "flights",
                "traffic", "motorway")),
    ("news", ("news", "headline", "headlines", "the score", "scores")),
    ("prices", ("price", "prices", "the cost", "costs", "exchange rate", "the rate")),
)


def _the_live_thing_named(clean):
    """The live pool for the bare thing a denial names, or None."""
    for kind, words in CANNOT_THINGS:
        if _has(clean, words):
            for name, _phrases, options in LIVE_KINDS:
                if name == kind:
                    return options
    return None


def _the_bot_says_it_cannot(clean):
    """True when the line is about what the bot cannot do, with nothing in it to look up."""
    return bool(BOT_CANNOT.search(clean or "") and BOT_CANNOT_LOOK.search(clean or ""))


# The word that makes a question one about a favourite rather than about a choice between two
# things on the table.
FAVOURITE_WORDS = ("favourite", "favorite")


def _taste_lines():
    """The taste lines that may take a favourite question off a card (see `reads_as_a_taste`).

    Only the entries asked for with the word favourite, and the honest "no favourite" pool. The
    choice pools are left out on purpose: "do you like dogs" is answered better by the chat
    module's own line than by the taste shrug ("No strong view on that one, honestly"), and "what
    do you like watching" better by the viewing picks than by the same shrug, so neither is a line
    to claim a turn with.
    """
    lines = set(FAVOURITE_GENERAL)
    for phrases, options in TASTES:
        if any("favourite" in phrase or "favorite" in phrase for phrase in phrases):
            lines.update(options)
    return frozenset(lines)


TASTE_LINES = _taste_lines()


# A line that puts the bot's favourite beside the person's own ("whats your favourite season? i
# cant decide mine") is a two-way question, and the entry that answers both halves is the better
# reply: the taste alone drops the half they brought to it.
BESIDE_THEIR_OWN = re.compile(r"\b(?:mine|can'?t decide|cant choose|not sure which)\b")


# The words that put a trip on the table: "we are driving down to cornwall", "we're flying to
# portugal in may". A follow-up that refers to "the drive" or "the trip" with no ends of its own
# is about that one.
TRIP_ON_TABLE = re.compile(
    r"\b(?:driving|drive|travelling|traveling|heading|going|off|flying|cycling|walking|"
    r"getting the (?:train|bus|coach|ferry)|trip|journey)\b[^.?!]{0,24}?\b(?:to|in ?to)\b")


def _a_trip_is_on_the_table(memory):
    """True when the ends of the trip are already in the chat.

    "how long would the drive be" names no ends by itself, but after "we are driving down to
    cornwall in august" they are known, so the route line is the one to give rather than the
    short question that asks which two places.
    """
    if not isinstance(memory, dict):
        return False
    for step in (1, 2):
        try:
            said = str(last_user(memory, step) or "").lower()
        except TypeError:
            said = str(last_user(memory) or "").lower() if step == 1 else ""
        if said and TRIP_ON_TABLE.search(said):
            return True
    return False


# A line that is the sky and nothing else is an ask with the words left out: "the weather today",
# "weather tomorrow", "weather outside", "rain this weekend". None of those has a question in it and
# none has a word of LIVE_STRONG, so the asking gate dropped them and the person got the nod ("I'm
# listening - say more if it helps") as though they had told the bot something, which is the worst
# answer to a question. This is a whole-line shape, not a keyword: every word has to be a sky word,
# a piece of time or the frame of a question, so "cold weather running tips" is still a question
# about running, "i like the rain" is still the person's own remark, and "the oven is too hot" is
# still the oven. The nouns carry it, so "weather" alone is an ask and "nice one" is not.
LIVE_SKY_NOUNS = frozenset(
    "weather wether weathr forecast forcast rain raining snowy snow sun sunny shine frosty frost "
    "icy ice foggy fog windy wind sleet hail stormy storm thunder drizzle cloudy overcast "
    "muggy humid misty mist".split())


LIVE_SKY_WORDS = LIVE_SKY_NOUNS | frozenset(
    "a an and the like is it what whats how hows will would be going gonna this next on at in "
    "for today tonight tomorrow morning afternoon evening night weekend weekends week weeks day "
    "days now later outside out there any much could might should please tell me know".split())


# A place is not a keyword to keep out of the shape above: "weather in manchester tomorrow" is the
# same ask as "weather tomorrow" with the place said out loud, and the old test dropped it for the
# one word that was not a sky word or a piece of time. So after a preposition the line may name
# where - one or two words of it - and still be the ask. Two, because "the weather in the peak
# district" is a place and three words in a row is usually a subject.
LIVE_SKY_PLACE = frozenset("in at near around for of".split())


def _the_sky_and_nothing_else(clean):
    """True when every word of the line is the sky, a piece of time, the shape of the ask, or the
    place the person is asking about."""
    words = [word.strip("'") for word in re.findall(r"[a-z']+", clean)]
    if not words or not _has(clean, LIVE_SKY_NOUNS):
        return False
    unknown = 0
    after_place = False
    for word in words:
        if word in LIVE_SKY_PLACE:
            after_place, unknown = True, 0
            continue
        if word in LIVE_SKY_WORDS:
            continue
        # "the weather in the oven" is the oven: an indoor thing after a preposition is the
        # thing, not the place, and the reading above answers the thing.
        if not after_place or word in LIVE_INDOOR:
            return False
        unknown += 1
        if unknown > 2:
            return False
    return True


# The words for traffic on a road, read with a road's name: "any jams on the a1 north" carries no
# ask and none of the strong live words ("any traffic" is one, "any jams" is not), so the asking
# gate dropped it and the person got the nod - "I'm listening - say more if it helps" - to a
# question about their drive this morning.
ROAD_TRAFFIC_WORDS = frozenset("""
    jam jams traffic busy closed closure closures shut roadworks accident accidents
    delay delays delayed diversion diversions queue queues queuing
""".split())


# A line that tells you what already happened on a road is not asking what the roads are doing.
# "i got stuck in a jam on the a1 this morning" is a person's morning, and "the m6 was closed last
# night" is news about their evening: the note about how a jam clears where "Rotten luck" belonged
# reads as a lecture. The same fault as the one above, one tense over, so the reader has to know
# whether the line is an ask at all.
# A report is not one phrase: it is a time already past, or a verdict on a day already had. "the
# m25 was shut last night" carries the time, but "the traffic was awful on the m25" carries only
# the verdict, and "my morning was a nightmare" only the mood - and both of those were still read
# as asks about right now. So the verb's own tense is read too: "was awful", "was a nightmare",
# "took ages" and "sat in traffic" are things that have happened, while "is the m6 shut" and
# "was the m6 shut" keep their ask (the asking gate and LIVE_STRONG hold those), and "was it busy"
# is still a question because the order is inverted.
A_REPORT_OF_WHAT_HAPPENED = re.compile(
    r"\b(?:yesterday|last night|this morning|earlier|we sat|i sat|got stuck|was closed|were bad|"
    r"there were|there was|it took us|took me|sat in|stuck for|queued for|took ages|"
    r"took forever|took hours|missed the (?:train|bus|ferry|flight)|"
    r"(?:was|were) (?:awful|terrible|horrendous|grim|hell|murder|chaos|a mess|a joke|a nightmare|"
    r"bad|shut|rammed|chocka|packed)|(?:awful|terrible|horrendous|grim) (?:this morning|earlier|"
    r"yesterday|last night))\b")


def _a_road_named_with_traffic(clean):
    """True when the line names a road and asks what the traffic on it is doing."""
    if not LIVE_ROAD_NAME.search(clean):
        return False
    if A_REPORT_OF_WHAT_HAPPENED.search(clean):
        return False
    return bool(set(clean.split()) & ROAD_TRAFFIC_WORDS)


THEIR_OWN_COUNT_WORDS = ("traffic", "footfall", "foot traffic", "visitors", "hits",
                         "analytics", "viewers", "stats")


# The ask, when the question mark is missing: "how much web traffic does my site get", "where do i
# see my footfall", "is my shop up or down this month".
A_COUNT_ASKED = re.compile(
    r"\b(?:how\s+(?:many|much|often)|whats?\s+(?:my|the)|what\s+is\s+my|where\s+(?:do|can)\s+i\s+"
    r"(?:see|find|check)|is\s+my\b.*\b(?:up|down)|how\s+is\s+my)\b")


# What happened, rather than what they want to know: "my shop had footfall all day", "my website
# had 200 visitors yesterday", "traffic to my etsy shop is down". A busy day is a thing to say
# something about, and a figure they already have is theirs, so "it lives in your analytics" is
# pointing away with nothing given - the same fault as a report of a road.
THEIR_OWN_COUNT_HAPPENED = re.compile(
    r"\b(?:had|has|got|fell|dropped|went|rose|doubled|halved|visited|bought|sold|shipped)\b")


THEIR_OWN_COUNT_REPORT = re.compile(
    r"\b(?:yesterday|last\s+(?:night|week|month|year)|this\s+(?:morning|week|month)|all\s+day|"
    r"so\s+far|today|down|up)\b")


def _their_own_count(clean):
    """True when the line asks for a number of the person's own with the question left off.

    "how much web traffic does my site get" and "where do i see my footfall" are asks, and the
    asking gate would drop them to the nod because the verb is not in front. The number is in
    their own analytics, so it is read here and answered by the site-stats note rather than by
    the nod.

    A line that says how the day went, or names the figure they already have, is not asking where
    the figure lives: "my shop had footfall all day" wants a word about the day, not a note
    pointing at the analytics page.
    """
    if not _has(clean, LIVE_SITE_THING) or not _has(clean, THEIR_OWN_COUNT_WORDS):
        return False
    if A_COUNT_ASKED.search(clean):
        return True
    return not (THEIR_OWN_COUNT_HAPPENED.search(clean)
                or THEIR_OWN_COUNT_REPORT.search(clean))


# A fall, said rather than asked: "traffic to my etsy shop is down", "visitors dropped last
# month", "sales have gone quiet". It reports their own numbers and asks nothing, so the asking
# gate would turn it into a nod and the site-stats note would send them to a page without saying
# anything first. A fall has ordinary explanations, and those come before the page.
A_COUNT_FELL = re.compile(
    r"\b(?:down|fell|falling|dropped|dropping|slowed|slowing|stalled|quiet|quietened|"
    r"nose\s?dived|collapsed|stopped|lower|fewer|half|dead|gone\s+quiet|went\s+quiet)\b")


def _their_own_thing(clean):
    """True when the number is one of theirs: their site, their shop, their till."""
    return _has(clean, ("my", "our", "mine", "the shop", "the site")) or bool(
        A_COUNT_ASKED.search(clean))


def _their_own_count_fell(clean):
    """True when the line reports a fall in a number of the person's own, and asks nothing."""
    if A_COUNT_ASKED.search(clean):
        return False
    return (_has(clean, LIVE_SITE_THING)
            and _has(clean, THEIR_OWN_COUNT_WORDS + ("sales", "orders"))
            and bool(A_COUNT_FELL.search(clean)))


# Word orders that are a question wherever they sit in the line. They are inversions a
# statement rarely uses ("who should i see", "should i go", "any advice"), so they do not
# turn "I saw what he did" into a question.
# A line that asks for words, not facts ("what should i say when i ring the plumber",
# "help me word a text to my landlord") wants a shape to say it in, not a search result.
# Two ways to be sure: it asks for wording outright, or it asks what to say and names who to
# or how you will say it. "What should I say on the first day?" is neither, and neither is
# "What should I ask the seller?" - those are questions about the thing, not the wording.
WORDING_ASKS = re.compile(
    r"\b(help (me )?(to )?(word|phrase|say)|word (a|an|the|this|that)|word it|phrase it|"
    r"how do i (word|phrase|say)|"
    r"put (it|this|that) in(to)? (a|an|words)|what to write)\b")


WORDING_SAYS = re.compile(r"\bwhat (should|do|can) i say\b")


# "what should i ask the plumber" is the same ask, with the expert already in the line.
WORDING_ASKS_WHO = re.compile(r"\bwhat (should|do|can) i (say|ask|tell)\b")


# "how do i tell my mum", "what do i tell my son about his dad", "how do i tell my husband i
# want a divorce": the same ask as "what should i say to my boss", said with tell. The `if` and
# `whether` forms are a different question - "how do i tell if my cat is ill" is asking for a
# sign, not for words - so they are kept out.
# The people a person actually has to break news to are usually named in the plural or as a
# group: the kids, the family, the team, everyone. "how do i tell my kids" was answered with a
# shape to say it in and an offer to draft it, while "how do i tell the kids", "how do i tell the
# children", "how do i tell the family", "how do i tell everyone", "how do i tell the twins" and
# "how do i tell the grandparents" all got the search hedge - the bot telling somebody to look up
# how to talk to their own children. The two groups are the household and the room, and both word
# orders below use them.
A_GROUP_OF_PEOPLE = (
    r"kids|children|child|family|families|team|staff|neighbours?|neighbors?|in[-\s]?laws|"
    r"grandparents|grandchildren|grandkids|twins|siblings|relatives|parents|friends|"
    r"colleagues|boys|girls|lads|folks|guys")


A_WHOLE_ROOM = r"everyone|everybody|anyone|anybody|someone|somebody"


WORDING_TELL = re.compile(
    r"\bhow\s+(?:do|should|can|could|would|might)\s+i\s+tell\s+"
    r"(?!\w*\s+(?:if|whether)\b)"
    r"(?:(?:my|his|her|their|our|your)\b"
    # a bare "the" took any noun: "how do i tell the time on this clock", "how do i tell the
    # twins apart", "how do i tell the sex of my kitten" all became wording asks, and four of
    # them had a better answer before (honey-bat). "The doctor", "the vet", "the landlord" are
    # people you have a conversation with, and they stay.
    r"|the\s+(?:doctor|gp|nurse|vet|police|landlord|boss|manager|bank|school|council|teacher|"
    r"colleague|midwife|consultant|dentist)\b"
    # A group after "the" cannot be the "how do i tell the time on this clock" shape the bare
    # article took, and where the line really is a comparison ("how do i tell the boys from the
    # girls", "how do i tell the twins apart") the "from" and "apart" guards below keep it out.
    r"|the\s+(?:" + A_GROUP_OF_PEOPLE + r")\b(?!\s+from\b)"
    r"|him|her|them|people|" + A_WHOLE_ROOM + r")\b"
    r"|\bwhat\s+(?:do|should|can|could)\s+i\s+tell\s+"
    r"(?:my|his|her|their|our|your|him|her|them|" + A_WHOLE_ROOM + r"|"
    r"the\s+(?:" + A_GROUP_OF_PEOPLE + r"))\b(?!\s+(?:if|whether)\b)")


# "how do i tell the difference between a cold and flu", "how do i tell the twins apart": the
# line is asking for a sign or a comparison, not for words, whatever follows "tell".
# The ask for words is said two ways, and the second one is what people who are stuck actually
# type: "how do i tell my boss" and "idk how to tell my boss". Nobody reports a doubt and then
# writes it out in full - the doubt is the first thing out of them, and every one of those lines
# reached the search hedge while the same ask in the other word order got a shape and an offer.
#
# So the line is read in both orders: "how to X" is read as "how do i X" and "what to X" as
# "what should i X", and the three patterns above answer whichever one the person used. That is
# what brings in the whole family, not just `tell`: "idk how to say it to her", "idk what to say
# to my landlord", "idk how to break it to my parents".
#
# Two guards, both of them measured:
# - The doubt has to be in front. "how to tell my baby is hungry" and "how to tell if my baby is
#   teething" are asking what to look for, not for words. They have no doubt in front of them and
#   keep their own answers.
# - Heavy news stands it down: "my daughter died and i dont know how to tell my son" is grief with
#   a question inside it, and the wording branch returns before the grief pools.
A_DOUBT_IN_FRONT = re.compile(
    r"\b(?:idk|i\s+dont\s+know|i\s+do\s+not\s+know|i\s+dunno|dunno|no\s+idea|"
    r"i\s*ve\s+no\s+idea|i\s+have\s+no\s+idea|not\s+sure|i'?m\s+not\s+sure)\b")
