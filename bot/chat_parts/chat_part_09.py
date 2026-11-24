"""Part 9 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import pick
from ..compose import repair
from ..compose.repair import deed_of

from ..memory import thread
from ..memory.topics import in_a_safety_thread as _safety_thread

from ..knowledge import lookup
from ..understanding import understand as understanding
from .chat_part_06 import (
    END_OF_ROPE, LOSS, OTHER_AWAKE, SYMPTOM,
)


# A mood that makes mornings hard ("i cant get out of bed most mornings"): the wake-up that
# follows is part of the same trouble, so it gets an answer that joins the two.
LOW_MOOD = re.compile(r"\b(?:can'?t|cant|struggle to|struggling to) (?:get out of bed|get up in "
                      r"the morning|face the day)\b|\bno energy\b|\bnot been sleeping\b|"
                      r"\b(?:everything|it all) (?:is )?(?:a struggle|too much)\b|"
                      r"\bfeel (?:empty|nothing|flat|low)\b|\bcan'?t be bothered\b|"
                      r"\bmost mornings\b[^.]*\b(?:dread|hard|worse)\b")


MOOD_NIGHTS = (
    "Waking early and finding the mornings this hard often come together. It is worth saying "
    "both to a GP in one go — and tonight, keep the room dark and don't watch the clock.",
    "That early waking sits on top of a low stretch, and the two feed each other. Tell a GP "
    "about both, and for tonight, get up rather than lie there watching the hours.",
)


WORRY_SOMEONE = re.compile(
    r"\b(?:worried|worry|worrying|worries|anxious|scared|frightened|freaking out|"
    r"can'?t stop thinking about)\b[^.?!]*?\b(?:about|over|for)\s+(?:my|our)\s+"
    # A pet someone is worried about is the same shape as a person: "i keep worrying about my
    # cat" is not a line about the weather, and "Noted: you keep worrying about your cat" says
    # nothing back.
    r"(?P<who>mum|mom|mam|mother|dad|father|son|daughter|child|kid|kids|baby|partner|husband|"
    r"wife|sister|brother|nan|gran|granny|grandma|grandad|grandpa|aunt|uncle|friend|"
    r"cat|dog|puppy|pup|kitten|rabbit|hamster|guinea|pony|horse|parrot|budgie)\b")


# A line that also states something to do now ("im worried about my baby she has a temperature",
# "im worried about my son he swallowed a grape") is a question for whoever can answer it, not a
# worry to talk through: the worry reply would talk past the thing that needs doing. A condition
# to live with ("she keeps forgetting things", "he was diagnosed with cancer") is not that — it
# is the worry itself, and naming the person serves it better than a neutral line does.
CARE = re.compile(r"\btemperature\b|\bfever\b|\bfell\b|\bfallen\b|\bswallowed\b|\bchoking\b|"
                  r"\bbleeding\b|\bcollapsed\b|\bunconscious\b|\bcan'?t breathe\b|"
                  r"\bbreathless\b|\bbroken\b|\bfracture\w*|\bstroke\b")


# The night has to be the person's own ("i was awake all night"), not someone else's evening:
# "she's 19 and out all night" is about the daughter, so it stays a worry about her.
NIGHT_SAID = re.compile(
    r"\b(?:up all night|up half the night|awake all night|awake half the night|no sleep|"
    r"didn'?t sleep|didnt sleep|couldn'?t sleep|"
    r"couldnt sleep|can'?t sleep|cant sleep|not slept|lay awake|lying awake|kept waking|"
    r"(?:keep|keeps|kept) waking|waking up|woke up at \d)\b")


WORRY_SOMEONE_NIGHT = (
    "A night spent worrying about your {who} is a long one, and it makes the day heavier. Say "
    "the actual worry out loud to someone today — the worst of it shrinks once it is said.",
    "Lying awake over your {who} is a hard loop to be in. Pick the one thing you can settle "
    "today — one call, one question, one visit — and let the rest wait until you have slept.",
    "That kind of waking is not your sleep at fault, it is the worry holding on. Write down the "
    "one thing about your {who} you would ask if you could, and ask it today.",
)


# The person a worry is about is named, so the follow-up question has to agree with it: "what's
# happening with them?" reads wrong about a mum. The plural ones keep "them".
WORRY_PRONOUN = {
    "mum": "her", "mom": "her", "mam": "her", "mother": "her", "daughter": "her",
    "sister": "her", "wife": "her", "nan": "her", "gran": "her", "granny": "her",
    "grandma": "her", "aunt": "her",
    "dad": "him", "father": "him", "son": "him", "brother": "him", "husband": "him",
    "grandad": "him", "grandpa": "him", "uncle": "him",
    # A pet is "them" until the person says otherwise.
    "cat": "them", "dog": "them", "puppy": "them", "pup": "them", "kitten": "them",
    "rabbit": "them", "hamster": "them", "guinea": "them", "pony": "them", "horse": "them",
    "parrot": "them", "budgie": "them",
}


WORRY_SOMEONE_DAY = (
    "Worry about your {who} follows you around all day. What's happening with {them}?",
    "That's a lot to carry around. Is it something you can do something about, or the waiting "
    "that's worst?",
    "Hard to put down when it's your {who}. Tell me what's going on.",
    "Your {who} being on your mind is not nothing. What's the worry — something that has "
    "happened, or something you are afraid might?",
)


def _worry_someone(clean, memory=None):
    """The replies for a worry about a person they love, None when it is something else, and
    "pass" when the line carries a problem that another part should answer.

    "Nerves before something big are normal" is the right answer to a nerves line and the wrong
    one to "im worried about my mum": the worry is about a person, so name them and take it
    seriously. A night that went with it is said too — a night spent worrying is its own kind.
    """
    found = WORRY_SOMEONE.search(clean)
    if not found:
        return None
    if LOSS.search(clean) or _loss_recent(memory) or END_OF_ROPE.search(clean):
        return None
    who = found.group("who")
    if SYMPTOM.search(clean) or CARE.search(clean) or OTHER_AWAKE.search(clean):
        # The worry is real but there is a problem in the line that needs answering ("im worried
        # about my baby she has a temperature"). Hand it on: and say nothing here, because the
        # generic nerves reply would read it as the person's own case of nerves.
        return "pass"
    pool = WORRY_SOMEONE_NIGHT if NIGHT_SAID.search(clean) else WORRY_SOMEONE_DAY
    them = WORRY_PRONOUN.get(who, "them")
    return tuple(reply.format(who=who, them=them) for reply in pool)


def _loss_recent(memory):
    """True when a death was mentioned in the last few turns: a bad night then is grief."""
    if not isinstance(memory, dict):
        return False
    turns = memory.get("turns") or []
    for turn in turns[-3:]:
        if LOSS.search(str(turn.get("user") or "").lower()):
            return True
    return False


def _low_mood_recent(memory):
    """True when the last few turns said the mornings are hard: the waking is part of that."""
    if not isinstance(memory, dict):
        return False
    for turn in (memory.get("turns") or [])[-3:]:
        if LOW_MOOD.search(str(turn.get("user") or "").lower()):
            return True
    return False


# --- a line about someone they love -----------------------------------------
# "she keeps forgetting where things are in the kitchen" after "my mum moved in with us last
# month" names nobody, and on main it got "Noted! What would be most useful to talk about?" - a
# line that fits any message - or, worse, a packing plan read out of the move. A friend hears
# who it is about and answers the thing that is not right. Never a question unless there is
# nothing concrete to say, never a diagnosis, and always with the person named: the store keeps
# memory["person"], so a bare "she" or "he" carries the name over (bot/memory.topics.about).
MAYBE_SOMEONE = re.compile(
    r"^(?:and |but |so |well |also |see |then |now |oh )*"
    r"(?:she|he|they)\b|\b(?:my|our)\s+(?:mum|mom|mam|mother|dad|father|son|daughter|child|"
    r"kid|baby|partner|husband|wife|sister|brother|nan|nana|gran|granny|grandma|grandad|"
    r"grandpa|aunt|uncle|cousin|friend|flatmate|neighbour|neighbor)\b")


# Something not right about them, in the words people use for it. The reading lives in the store
# (bot/memory/topics.PERSON_TROUBLE) because it outlives the turn: the reply this turn gets may
# come from another lane, and the short ask two turns later still leans on it.
# Something is not right, but it is none of the kinds above: the reply says so and asks the one
# question that matters. Only a thing they keep doing, cannot do, or have stopped doing - a bare
# "not" or "always" is far too easy to say about something ordinary.
SOMEONE_TROUBLE_ANY = re.compile(
    r"\b(?:keeps?|kept) (?:forgetting|getting|losing|falling|waking|saying|coughing|stopping|"
    r"forgetting|crying|asking|being)\b|"
    r"\b(?:wont|won'?t|cant|can'?t|refuses? to|has stopped|stopped)\b|"
    r"\bnot (?:been\s+)?(?:himself|herself|themselves|coping|eating|drinking|sleeping|"
    r"walking|right)\b|"
    # The contraction reaches the reading whole on most lines, and the understanding engine only
    # offers the expanded "has not been" reading when nothing else has claimed the line, so both
    # forms are read here: "my mum hasnt been herself at all this week" was a bare nod.
    r"\b(?:hasn'?t|hadn'?t|haven'?t)\s+been\s+(?:himself|herself|themselves|coping|eating|"
    r"drinking|sleeping|walking|right)\b|"
    r"\b(?:went|been) downhill\b|\bhas been (?:poorly|unwell|off|poorly)\b")


# "hasnt been" reaches here as "has not been" (the understanding engine expands the contraction),
# so the "been" inside the pattern is what makes "my mum hasnt been herself" a worry about her
# rather than a bare nod ("Noted: your mum hasn't been herself.") while "my mum is not herself"
# already got the careful question. The auxiliary that carries the worry is not the point.
# A diagnosis of a serious illness is news of its own: the person is not on a ward, and there is
# no first appointment to book either, so neither the hospital lines nor the GP nudge fit.
SERIOUS_DIAGNOSIS = re.compile(
    r"\b(?:diagnosed|diagnosis) (?:with|of|as having)\s+(?:cancer|a (?:brain |lung |bowel |"
    r"breast |bone )?tumou?r|leukaemia|leukemia|lymphoma|motor neurone|parkinsons?|"
    r"a terminal|something serious)\b")


# A thing that cannot be something is not something a person cannot do. "we have a barn booked" /
# "my mum is paying so it cant be too expensive" was answered "How long has that been going on
# with your mum?", which is a question about a symptom that was never mentioned: the cue is
# "cant", but its subject is the price. The same line about a sister bringing her children
# ("so it cant be too late") got "How long has that been going on with your sister?". Only a
# "cannot" with the person for its subject says what they cannot do ("my mum cant walk far",
# "she wont eat"), so a line whose every "cannot" has a thing in front of it has nothing here.
THING_BEFORE_CANNOT = re.compile(
    r"\b(?:it|it's|its|that|that's|thats|this|there|there's|theres|which|the \w+|a \w+|an \w+|any \w+)"
    r"\s+(?:probably |still |just |really |even )?(?:can'?t|cant|cannot|can not|won'?t|wont|will not)\b")


def _a_thing_cannot(clean):
    """Every "cannot" in the line is about a thing, so nothing is reported about the person."""
    return SOMEONE_TROUBLE_ANY.search(THING_BEFORE_CANNOT.sub(" ", clean)) is None


SOMEONE_REPLY = {
    "known": (
        "Since there is already a diagnosis, make this change the GP's problem rather than "
        "yours to watch: a step down like that is often something treatable, and an infection "
        "is the usual one they check for first.",
        "Ring the GP about your {who} rather than waiting for the next appointment — a change "
        "that comes on over days rather than months is often something with a fix, and worth "
        "saying today.",
    ),
    # A ward they have left: the news is good, and the reply is what a friend says to good news.
    # Kept apart from the "hospital" pool, which belongs to a ward someone is still on.
    "homeward": (
        "That's a relief — home is where most of the getting better happens. How is your {who} in "
        "themselves?",
        "Good news. Keep the first week small: short visits, early nights, and let your {who} set "
        "the pace rather than the other way round.",
        "Home, then — that is the bit that matters. The first days back are the ones to keep "
        "quiet, because everyone tries to do too much in them.",
        "Glad to hear it, and home beats a ward for getting better. Ask what to watch for in your "
        "{who}'s first fortnight, and who to ring if something changes.",
    ),
    # A serious diagnosis is not a place, so it does not borrow the ward's lines: the store reads
    # it as the hospital kind (there is care happening and the question is how they are), and this
    # is what the reply says instead of "That is a worrying place for your {who} to be" about a
    # woman diagnosed last week at home. The kind stays "hospital" in memory, so the follow-up
    # ("is that normal") keeps the ward's answer.
    "diagnosed": (
        "I'm sorry - a diagnosis like that changes the shape of a week. How is your {who} in "
        "themselves?",
        "Worrying news. What have they said about what happens next, and who is looking after "
        "your {who}'s care?",
        "That is a lot to take in, and it takes time to sink in. Has anyone walked you through "
        "the treatment yet?",
    ),
    "hospital": (
        "Sorry to hear that. How is your {who} doing?",
        "That is a worrying place for your {who} to be. What has the hospital said?",
        "Worrying, and waiting is the worst part of it. How is your {who} in themselves?",
    ),
    "memory": (
        "Losing track of things in a familiar place is worth a word with your {who}'s GP, and "
        "soon: it can be a lot of things and several of them are fixable. A note of when it "
        "started, and anything else that has changed, is what they ask for first.",
        "That is worth mentioning to a GP rather than waiting to see if it settles. Write down "
        "what you have noticed about your {who} and when it started, and take that with you — "
        "and if it gets suddenly worse, that is the same day rather than next week.",
        "Worth a GP appointment with your {who}, and take this line with you: forgetting things "
        "in a place they know well is the kind of change that gets looked at properly, and the "
        "sooner the easier it usually is.",
    ),
    "falls": (
        "A fall is worth getting looked at even when nothing hurts, and a second one is worth a "
        "GP visit: balance, eyesight and medicines are the usual causes and all three can be "
        "helped. Clear the loose rugs and put a lamp within reach of the bed in the meantime.",
        "Falls are rarely just age, and that is the good news: strength, eyesight and medication "
        "are the places to look, and a GP can start on all three. Until then, good light on the "
        "stairs and nothing to trip over on the way to the bathroom.",
    ),
    "care": (
        "Ask the staff what they notice day to day and get it written in the home's notes — they "
        "see more of your {who} than you can, and a GP takes their record seriously. Visit at "
        "different times of day so you see it for yourself too.",
        "A home keeps a daily record, so ask what is in it about your {who}: eating, sleep, and "
        "anything that has changed. That is the account a GP or the manager can act on, and it "
        "costs you one conversation at the desk.",
    ),
    # Awake all night is not a person who has withdrawn from life: sleep is the report, so the
    # reply reads the night rather than talking about low mood in later life.
    "sleep": (
        "Broken sleep is worth reading rather than enduring: pain, a new tablet, drinking later, "
        "a room that is too warm, worry — one of those is usually behind it, and the fix is "
        "different for each. If it has been weeks, or they are worn out all day, ring the GP: a "
        "blood test rules out the physical ones.",
        "A night that is nothing like their usual is a change worth having looked at, and sooner "
        "if it came on suddenly. Ring the GP this week and say when it started and what is "
        "different about the nights now.",
    ),
    "low": (
        "Going quiet and off things is worth saying out loud to a GP — it is common, it is "
        "treatable, and people often do not mention it themselves. One small thing a week that "
        "gets your {who} out, even a short walk, does more than a big plan.",
        "That kind of withdrawal is worth a GP appointment rather than a wait: low mood in later "
        "life is under-reported and it responds to help. In the meantime, keep the visits going "
        "even when they say no — company is the bit that works.",
    ),
    "ill": (
        "Get your {who} looked at rather than waiting it out, and sooner if it is getting "
        "worse — a change like that in someone you are looking after is worth a proper check.",
        "Worth a GP appointment for your {who} this week rather than next month, and keep a "
        "note of what has changed and when. If it turns sudden, that is the same day.",
    ),
}


# The next turn is usually a short ask about the same trouble: "is that normal", "what should I
# look out for", "should I go with her". It names nobody, so it is answered from the kind of
# trouble the last turn was about, kept in memory["person"]["trouble"]. Only a short ask, only
# while that trouble is the thing being talked about, and never in place of a question the
# knowledge base can answer, since this runs after those.
# The same ask arrives with age in it far more often than with "normal" alone: "is that just
# old age", "is it just her age", "is that normal for his age" are all the question above -
# how much of this is the years and how much needs looking at - and every one of them was a
# shrug on main while "is that normal" was answered from the same trouble record. The words
# that make it a cause are only read here, where a record of what is not right already exists,
# so "is that just the weather" is not this question.
SOMEONE_IS_IT_NORMAL = re.compile(
    r"^(?:and |but |so )?(?:is|was|are) (?:that|this|it) (?:normal|ok|okay|fine|serious|"
    r"bad|dangerous|common|a worry)\b|\bshould i (?:be )?worried\b|\bis that a sign\b|"
    # "when should i worry" asks the same thing as "is that normal" and was answered by the
    # generic worry pool with the question just asked: what would settle it.
    r"\bwhen (?:should|do|would) i (?:start to )?worry\b|\bhow worried should i be\b|"
    r"\b(?:is|was|are) (?:that|this|it) (?:(?:just|only|part of|down to|because of) "
    r"(?:getting |being )?(?:old age|her age|his age|their age|age|old)|(?:normal|usual|"
    r"expected) for (?:her|his|their) age)\b|\bjust (?:her|his|their) age\b|"
    r"\bat (?:her|his|their) age\b|\bold age\b")


# The age-naming half of the ask above, on its own: a line that puts the years behind the thing
# ("is that just her age") is answered from the worry the last turn reported even when the pool
# has nothing for that kind, and the plain verdict shapes ("is that bad") are left to the module
# that refuses to judge them.
SOMEONE_AGES_IT = re.compile(
    r"\b(?:is|was|are) (?:that|this|it) (?:(?:just|only|part of|down to|because of) "
    r"(?:getting |being )?(?:old age|her age|his age|their age|age|old)|(?:normal|usual|"
    r"expected) for (?:her|his|their) age)\b|\bjust (?:her|his|their) age\b|"
    r"\bat (?:her|his|their) age\b|\bold age\b")


# "And another one on Tuesday", "it happened again": the same trouble, told with a second
# example, which is exactly what the last answer asked for.
SOMEONE_MORE = re.compile(
    r"\b(?:another|again|twice|three times|second time|every (?:day|night|week|morning)|"
    r"now he|now she|hes done it|shes done it|same again)\b")


SOMEONE_NEXT_STEP = re.compile(
    r"\bwhat (?:should|can|do) i (?:be )?(?:look(?:ing)? out for|watch(?:ing)? (?:for|out) for|"
    r"expect|do(?: next)?|do now|ask(?: them| him| her| the doctor| the gp| the ward)?|"
    # "what should i ask them" is the question an admission leaves a family with, and the ward's
    # answer below is exactly the list of things to ask. It was a punt: "That's beyond what I know
    # well, sorry." Only while a carer trouble is the live topic, where the record has to exist.
    r"say(?: to them)?|bring|take with me)\b|\bshould i (?:go|come|be there) with\b|"
    r"\bwhat happens (?:now|next)\b|\bhow do i (?:help|manage|handle)\b|"
    r"\bis there anything i can do\b")


# The same question about a worry the store could not put in one of the kinds above - "my dad
# is 78 and has stopped going out" then "is that just old age" - still deserves the honest
# answer rather than a shrug: what age does, and what wants looking at whatever age says. It
# names no cause, so it is safe beside any of the pools and never replaces one.
SOMEONE_NORMAL_ANY = (
    "Some of it is age and some is not, and the difference is what changed and how fast: a "
    "slower, steadier version of the same person is the ordinary kind, and a change over days "
    "or weeks, or a stop in something they always did, is worth a GP appointment. A note of "
    "what you have seen and when is what makes that appointment useful.")


# "What should i bring him" is a question about a gift, not the next step of the hospital
# trouble. The step reading above matches a bare "bring", so it answered this line with "ask the
# ward what the plan is" while the gift table had the hospital-bag answer in the list behind it.
# A thing for a named person is the gift table's ask; the step reading keeps "what should i bring"
# with no person after it.
SOMEONE_BRING_SOMEONE = re.compile(
    r"\bwhat (?:should|shall|can|do) i (?:bring|take)\s+(?:(?:for|to)\s+)?(?:him|her|them)\b")


SOMEONE_NORMAL = {
    "memory": "Some forgetting is ordinary with age; getting lost in a room they know well is "
              "the kind that gets looked at, and a GP can tell the difference properly.",
    "falls": "One fall can be bad luck. Two, or one with no obvious cause, is not something to "
             "keep an eye on alone — balance and medication are worth a proper look.",
    "sleep": "Sleep goes in patches — a bad week after a change is common, and so is a night "
             "that is nothing like the usual. Weeks of it, or days that are wrecked by it, is "
             "worth a look rather than patience.",
    "low": "Going quiet for a few weeks after a change is common. Months of it, or losing "
           "interest in everything, deserves an appointment rather than patience.",
    "ill": "A change that comes on over days is the one to act on quickly; over months, it still "
           "wants a check rather than waiting for it to pass.",
    "known": "A step down over days is worth a call the same day; the slow changes are the ones "
             "to raise at the next appointment.",
    "hospital": "However it looks today, ask the ward what they expect next — they would rather "
                "answer a question than have you guess.",
}


# A second example of the same trouble ("she said the wrong name for the kettle yesterday") is
# not a new subject: it is the thing the first answer asked about, and the reply is to take it
# down rather than to explain it again.
SOMEONE_AGAIN = {
    "memory": "Note that one down with the date: the examples are what a GP works from, and a "
              "few of them over a few weeks say far more than one on its own.",
    "falls": "Note where and when it happened, and whether anything was different - a new "
             "tablet, a bad night, a rush to the loo. That pattern is the useful bit.",
    "sleep": "Note the nights down - when they woke, how long for, and what they had to drink or "
             "take before bed. Three nights written down says more than a month remembered.",
    "low": "Note what has changed around the same time - a move, a loss, a new tablet - and say "
           "how many days it has been like that.",
    "ill": "Keep a note of the date and what changed: three of anything in one winter is worth "
           "saying out loud to the GP.",
    "known": "Write it down as it happens, with the date: the ones that pile up are what they "
             "ask about.",
    "hospital": "Ask them, while you are there: what the operation was for, and what normal "
                "looks like afterwards.",
}


SOMEONE_NEXT = {
    "memory": "Go with your {who} and take a written note: what you have noticed, when it "
              "started, and anything that changed around then. The GP will ask for exactly that, "
              "and you will be the one who knows.",
    "falls": "Ask about balance and a medication review in the same appointment, and get the "
             "eyes checked: those three cover most of it. At home, good light on the stairs and "
             "nothing to trip over on the way to the bathroom.",
    "sleep": "Same wake-up time every day, no caffeine after early afternoon, a cool dark room, "
             "and out of bed if they are awake more than twenty minutes. If it is weeks, ask the "
             "GP to check their bloods and what they take.",
    "low": "Go along if your {who} will let you, and say the things they will not. Keep the "
           "visits and the small invitations going — they matter more than advice.",
    "ill": "Take a note of what has changed and when, and ring rather than wait for it to get "
           "worse. Sudden and getting worse is the same day.",
    "known": "Note anything that changed in the last few days — eating, drinking, sleep, a "
             "temperature — and ring the GP with it; those are the questions they ask first.",
    "hospital": "Ask the ward what the plan is and who to ring if something changes at night; "
                "write it down, because it is hard to remember later.",
}


# A small child is a different person to read: not talking much at two, or being clingy, is not
# the withdrawal from life that the low-mood reply is about.
YOUNG = re.compile(
    r"\b(?:is|only|just|nearly|almost) (?:one|two|three|four|five|[1-5])\b|"
    r"\b\d+ (?:months?|years?)\b|\bbaby|toddler|newborn\b")


# Being afraid of something is not the same as it happening: "she is worried about getting lost
# in the building" is a nervous twelve-year-old before secondary school, and the answer for a
# lost memory would frighten the person who asked it.
FEAR = re.compile(
    r"\b(?:worried|worrying|nervous|anxious|scared|afraid|frightened|terrified|dreading)"
    r"\s+(?:about|of|that)\b")


SOMEONE_ASK = (
    "How long has that been going on with your {who}?",
    "What has your {who} said about it — and how long has it been like this?",
    "Has your {who} seen anyone about it, or is that the next thing?",
)


# A check of the fact the bot just gave is this module's line, whatever else proposed: the check
# names no subject of its own, so a topic entry takes it on the topic of the chat and answers it
# with its own answer again. A hook that raises must not cost the turn, so anything unexpected
# reads as "not mine".
def _checks_the_fact(text, memory):
    try:
        return thread.checking_a_fact(text, memory) is not None
    except Exception:  # noqa: BLE001 - a hook that raises is a line this module does not claim
        return False


# A row comes with a size on it more often than not - "a massive row", "a really silly
# argument" - and the modifier was what stopped the line being read as a row at all: "me and my
# boyfriend had a massive row" got "Got it. Is there anything you'd like a hand with?". The size
# is about the row, so it is skipped over rather than allowed to hide the noun.
ROW_SIZE = (r"(?:(?:really|very|pretty|quite|totally|absolutely|such|kind of|sort of)\s+)?"
            r"(?:(?:massive|big|huge|right|proper|real|serious|silly|stupid|terrible|awful|"
            r"horrible|nasty|bitter|blazing|small|minor|tiny|daft)\s+)?")


A_ROW = re.compile(
    r"\b(?:i|we|me)\b[^.!?]{0,30}\b(?:argued|arguing|argue|rowed|had a row|falling out|"
    r"(?:had|having|got into)\s+(?:an?\s+)?" + ROW_SIZE +
    r"(?:row|argument|fight|falling[- ]out)\b|"
    # "i had a fight with my best friend" is the same turn as "i argued with her": the noun is
    # the row, not a scuffle and not a thing to look up. It still needs the person below.
    r"fight|fighting|fought|had an argument|an argument|falling out|"
    r"fell out|snapped at|shouted at|lost my temper|lost it with|not speaking|"
    r"stopped talking|said something (?:i|that i) regret)\b"
    r"|\b(?:me and|i and)\b[^.!?]{0,20}\b(?:fell out|had a row|argued)\b"
    r"|\b(?:he|she|they)(?:s|'s| is| are|re|'re)?\s+(?:not|isn'?t|aren'?t|never)\s+"
    r"(?:speaking|talking)\s+to me\b"
    r"|\bwon'?t talk to me\b")


# The row has to be with someone close for these to fit: "i argued with my boss" is a different
# turn and is left to the machinery for work trouble.
A_ROW_CLOSE = re.compile(
    r"\b(?:mum|mom|mother|dad|father|sister|brother|wife|husband|partner|boyfriend|"
    r"girlfriend|son|daughter|nan|gran|granny|grandma|grandad|grandpa|friend|mate|"
    r"flatmate|housemate|aunt|uncle|cousin|stepdad|stepmum|parents|family|"
    # a row with a child the line names as "my child" or "my kids" is the same turn as a row
    # with a son or a daughter: "i argued with my kids" had no close noun here, so the row pool
    # did not see it and the line fell to a shrug. The words are plural-safe because the row
    # regex above needs an "i" doing the rowing, so "my kids argue every morning" is untouched.
    # Only the two words the fault was in: "toddler" and "teenager" put "i lost it with my
    # toddler" and "my teenager wont talk to me" here too, and both had a better answer already
    # (the repair line, the side-by-side talk), so they stay where they were.
    r"child|children|kid|kids)\b")


# "her" and "him" where the line makes them clear, "them" otherwise: the reply has to read the
# same for a mate, a sister and a partner.
ROW_HER = re.compile(r"\b(?:mum|mom|mother|sister|wife|girlfriend|daughter|nan|gran|"
                     r"granny|grandma|aunt|stepmum|she)\b")


ROW_HIM = re.compile(r"\b(?:dad|father|brother|husband|boyfriend|son|grandad|grandpa|"
                     r"uncle|stepdad|he)\b")


# A question that names a row has its own answer somewhere ("what should i say to my sister
# after an argument"), so only a line that reports one comes here - wherever the ask sits in it.
ROW_ASK = re.compile(r"^\s*(?:what|whats|how|why|when|where|who|which|should|shall|can|could|"
                     r"do|does|did|is|are|will|would|any)\b"
                     r"|\b(?:what|how) (?:should|shall|can|could|do|does) (?:i|we)\b")


# The phrasings the knowledge base has its own row entry for. A line that says one of these is
# answered there (a clean apology in person, what to say), so the row pool stands down for it.
FALLING_OUT = re.compile(r"\b(?:fell out|fallen out|falling out|fall out|not talking"
                         r"|stopped talking|stopped speaking|made up|make up)\b")


ROW_REPLY = (
    "Rows with the people we are closest to land hardest. Say the one thing you actually want "
    "{them} to hear and leave the rest of the case: being right is rarely the part that matters.",
    "That kind of row is rarely about what it started as. If it is still raw, give it a night, "
    "then say your one true thing calmly.",
    "Most fallings-out are two people each sure of their own version. Ask {them} how it sounded "
    "from {their} side of it - it is usually not what you meant.",
    "Being at odds with someone close sits on you all day, so I would not leave it too long. "
    "One honest sentence does more than a long apology.",
    "You do not have to fix it today. Say something true rather than nothing at all, and let the "
    "rest wait until you are both calmer.",
)


def _close_nouns(text):
    """The people a line names in the words this file knows: "mum", "sister", "housemate"."""
    return {word[:4] for word in A_ROW_CLOSE.findall(str(text or "").lower())}


def _names_the_person(clean, row=None):
    """Whether a contact question says who it is about.

    "should i ring her back tonight" is this row; "should i ring the council about the bins" is
    not, and claiming it took the turn from the waste collection entry: the claim on the arbiter
    was looser than the reply, so chat got the turn with nothing to say and the composer wrapped
    the last line in "and take it from there".

    A pronoun is the row's own person, because a row is said with them in it. A named person is
    only the row's when the row was with that person: "me and my husband had a huge row" /
    "should i ring my mum" is a question about the mum, and answering it with the row about the
    husband put the wrong person in the reply.
    """
    if re.search(r"\b(?:her|him|them|she|he|they)\b", clean):
        return True
    named = _close_nouns(clean)
    if not named:
        return False
    with_them = _close_nouns((row or {}).get("text") if isinstance(row, dict) else "")
    if not with_them:
        return True
    return named <= with_them


# A row said without naming anyone is the same turn as one with a name in it: "we had a row" and
# "we had a massive row last night" were an acknowledgement and "I'm listening - say more if it
# helps", while "me and my mum had a massive row" got the pool. The pool waited for a close
# person to be named, which is the right test for "i argued with my boss" and for the landlord
# and the plumber - so the stand-down is the person named instead, and it only fires for them.
A_ROW_NOT_CLOSE = re.compile(
    r"\b(?:boss|manager|colleague|coworker|co-worker|workmate|landlord|letting agent|"
    r"neighbour|neighbor|plumber|builder|electrician|decorator|doctor|nurse|teacher|tutor|"
    r"lecturer|police|council|driver|shop|company|officer|agent|solicitor|bank|staff|"
    r"gp|dentist|vet|postman|courier|stranger|client|customer)\b")


def _a_row_person(clean):
    """Whether the row has someone the pool can speak about, named or not.

    A named close person is the pool's own, and so is a row with nobody else in it; a row with
    somebody outside that circle - a boss, a landlord, a neighbour - belongs to the machinery for
    that trouble and not to the one about being at odds with someone close."""
    if A_ROW_CLOSE.search(clean):
        return True
    return not A_ROW_NOT_CLOSE.search(clean)


def _keep_the_row(clean, memory):
    """Remember the row, so the turns after it belong to it whoever answers this one.

    "she hung up on me" and "should i ring her back tonight" are about the row and nothing else in
    the conversation says so. The row is kept from the line itself rather than from this module's
    reply, because the line can be answered by the knowledge base ("i fell out with my best mate
    has its own entry) and the turns after it are still the row."""
    if not isinstance(memory, dict):
        return None
    if not A_ROW.search(clean) or not _a_row_person(clean):
        return None
    if ROW_ASK.match(clean) or clean.rstrip().endswith("?"):
        return None
    if len(clean.split()) > 18 or LOSS.search(clean) or _safety_thread(memory):
        return None
    memory["row"] = {"them": _row_pronoun(clean), "they": _row_subject(clean),
                     "turn": len(memory.get("turns") or []), "text": clean,
                     # The falling-out rows have an entry of their own, so the turns after one
                     # go back to it rather than to the pool: "how do i put it right" after
                     # "i fell out with my best mate" wants the entry's clean apology, and the
                     # pool only has the shorter sentence about naming your part.
                     "handed_over": bool(FALLING_OUT.search(clean))}
    return memory["row"]


def observe(text, memory):
    """A row the person is in is remembered as they say it, not when this module answers it."""
    try:
        _keep_the_row(str(text or ""), memory)
    except Exception:  # noqa: BLE001, S110 - a turn never fails on a memory write
        pass


# An entry that is about the row itself is the better answer, and the pool must not stand in
# front of it: `sibling-row-adult` ("say the one thing that is actually under the argument"),
# `stop-shouting-at-kids` ("say sorry plainly, name what happened") and `fell-out-with-friend`
# all answer the row in hand. The test is the entry's own name, not its words: the family-party
# entry says "argument" in passing and is still not about the row, and "i had a really silly
# argument with my sister" needs the pool.
ROW_EVENT_ID = re.compile(
    r"(?:^|-)(?:row|rows|argu\w*|fight\w*|fought|shout\w*|yell\w*|snap\w*|temper|"
    r"sorry|apolog\w*|make-up|making-up)(?:-|$)", re.I)


ROW_FELL_OUT = "fell-out"


WANTS_AN_APOLOGY = re.compile(r"\b(?:sorry|apolog\w*)\b")


ASKS_FOR_WORDS = re.compile(
    r"\bwhat (?:should|do|can|could|would) i say\b|\bhow (?:do|should|can|could) i say\b|"
    r"\bwhat to say\b|\bhow to say\b|\bhow do i word it\b|\bhow do i put it in words\b")


def _the_base_has_an_answer(clean, memory):
    """The entry the knowledge base matched for this line, or None."""
    try:
        return lookup.find(understanding(clean, memory))
    except Exception:
        return None


# A row that says what it is about belongs to the card for that thing. "we argue about the
# housework all the time" is a question about splitting the chores, and the pool answered it
# "Rows with the people we are closest to land hardest", while the housework card - the jobs, and
# the half of them nobody counts - was there all along. The pool is for a row with no subject of
# its own, so a line that names one and no person outside the circle stands the pool down.
ROW_ABOUT = re.compile(
    r"\b(?:about|over|because of|to do with|around)\s+"
    r"(?:the |a |his |her |their |our |my )?([a-z']+)")


# The things a row is about that are people: "we had a row about her mum" is a row, not a
# question about a mother-in-law, and no card of its own answers it.
ROW_ABOUT_A_PERSON = frozenset({
    "me", "him", "her", "them", "us", "you", "it", "that", "this", "what", "nothing",
    "anything", "something", "everything", "mum", "mom", "mother", "mam", "dad", "father",
    "son", "daughter", "brother", "sister", "wife", "husband", "partner", "boyfriend",
    "girlfriend", "friend", "mate", "flatmate", "housemate", "colleague", "boss", "neighbour",
})


def _the_row_names_its_subject(clean):
    """True when the line says what the row is about and that thing is not a person."""
    for hit in ROW_ABOUT.finditer(clean):
        if hit.group(1) not in ROW_ABOUT_A_PERSON:
            return True
    return False


def _the_base_answers_the_row(clean, memory):
    """True when the entry the knowledge base matched for this line answers the row itself.

    Two shapes: the entry is about being at odds with someone (its id says row, argue, sorry), or
    the entry is the card for the thing the row is about and the line names it."""
    found = _the_base_has_an_answer(clean, memory)
    if found is None:
        return False
    ident = str(getattr(found, "id", "") or "")
    if ROW_EVENT_ID.search(ident) or ROW_FELL_OUT in ident:
        return True
    return _the_row_names_its_subject(clean)


# A word that asks something, used to see whether a line carries a question after the row in it.
_ASKS_AFTER = re.compile(r"\b(?:should|shall|can|could|what|how|why|when|where|who|which|"
                         r"is|are|do|does|did|will|would|any)\b")


def _a_row(clean, memory=None):
    """The warm replies for a row with someone close, or None.

    A row is told, not asked: what the person needs is a hand with the relationship, and the one
    thing it is not is a search question. Nothing is said when the line names no one close, when
    it asks something of its own, and when a death or an emergency is in the conversation, which
    own the turn.
    """
    said = A_ROW.search(clean)
    if not said or not _a_row_person(clean):
        return None
    if ROW_ASK.match(clean) or clean.rstrip().endswith("?"):
        return None
    # The row has to be the line, not the subject of a question carried in after it. The composer
    # re-reads a short line with the subject it leans on in front of it, so "me and my mum had a
    # massive row" / "should i ring the plumber" comes back here as one long line with a row at
    # the front, and the row pool answered a question about the plumber.
    if _ASKS_AFTER.search(clean[said.end():]):
        return None
    if len(clean.split()) > 18 or LOSS.search(clean) or _safety_thread(memory):
        return None
    them = _row_pronoun(clean)
    _keep_the_row(clean, memory)
    if _the_base_answers_the_row(clean, memory):
        return None
    they = _row_subject(clean)
    return pick(tuple(reply.format(them=them, they=they, their=_their_of(them))
                     for reply in ROW_REPLY), memory, clean)


# After a row, "should i ring her back tonight" is not a decision that is the person's alone: it
# is the same row one step on, and they are asking whether to do the thing that ends it. The
# honest-sounding "That's your call, not mine" reads as a shrug at somebody who has just told you
# about the worst day of their week, so the turn after a row is answered from the row.
ROW_CONTACT = re.compile(
    r"\b(?:ring|call|text|message|phone|facetime|go round|pop round|go over|apologise|"
    r"apologize|say sorry|make up|make it up|reach out|get in touch|speak to|talk to|"
    # Leaving it alone is the other half of the same question, and it hedged too: "should i just
    # leave it for a few days" after a row got "Not mine to decide, sorry".
    r"leave (?:it|her|him|them)|give (?:her|him|them|it) (?:some )?(?:space|time)|"
    r"wait|sit on it|sleep on it)\b")


ROW_CONTACT_ASK = re.compile(
    r"^\s*(?:should|shall|do you think|would you|is it|could)\b"
    r"|\b(?:should|shall) (?:i|we)\b|\bdo you think (?:i|we)\b|\bis it (?:better|too soon)\b"
    r"|\bor (?:not|wait|leave it)\b")


# How the answer moves the row on: one thing said, short, and not an argument won. Each line is
# about the doing of it, because that is the only part the bot can be sure of.
ROW_NEXT = (
    "Yes, and keep it short: say the one thing you would want {them} to hear, not the case for "
    "why you were right. A message is easier than a call while it is still raw.",
    "I would call rather than text, and let {them} hear your voice. One sentence about you - and "
    "if it goes to voicemail, that is not a no.",
    "Say the thing you would be glad you said in a year, not the thing you have been rehearsing. "
    "And not after a drink, however much easier that feels.",
    "Tonight is fine if you are both calmer than you were. Ring with one thing to say and let the "
    "rest wait: a row does not have to be settled in one call.",
)


# Leaving it alone is the other half of the same question and wants the opposite advice: "should i
# give her some space" answered with "say the thing you would be glad you said in a year" is a
# push where the person is asking about a pause.
ROW_SPACE = re.compile(
    r"\bleave (?:it|her|him|them)\b|\bgive (?:her|him|them|it) (?:some )?(?:space|time)\b"
    r"|\bwait\b|\bsit on it\b|\bsleep on it\b|\bnot (?:tonight|yet)\b")


# The line after a row is often not a question but what the other person said: "she said she
# needs space" and "he wants time to think" were answered "Got it - she said she needs space",
# which is the bot reading the person's own words back at them. What they asked for is the
# question, and the answer to it is the one about a pause, not about the row.
ROW_SAID_SPACE = re.compile(
    r"\b(?:he|she|they|my (?:mum|mom|mother|dad|father|sister|brother|wife|husband|partner|"
    r"boyfriend|girlfriend|friend|mate|flatmate|housemate))"
    r"(?:'s|s| is|re|'re)?\s+(?:said|says|wants|needs|asked for|asked|thinks|reckons|"
    r"told me)\b[^.!?]{0,30}\b(?:space|time|time to think|a few days|a break|breathing room|room)\b")


# "how do i put it right" says the row is still the subject without naming it, and the entries
# read the bare "it" as nothing at all: the answer was "I'd rather not guess". What puts a row
# right is the one thing, said once, so it is answered from the row.
# The how-asks that are about the row, and only those. "How do i ..." on its own is every how-to
# there is: inside three turns of a row, "how do i descale the kettle" was answered with the
# apology script, and a person upset about a row who then asks about the kettle wants the kettle.
# So the verb after "how do i" has to be one of the putting-it-right ones.
ROW_HOW = re.compile(
    r"^\s*how (?:do|can|should|would) (?:i|we)\s+(?:put (?:it|things) right|say sorry|apologi[sz]e"
    r"|make (?:it )?up|fix (?:it|this|things)|sort (?:it|this) out|make (?:things|it) better"
    r"|handle (?:it|this)|bring (?:it|things) up)\b"
    r"|\bwhat (?:do|can|could|should|would) (?:i|we) (?:do|say)\b|\bany (?:advice|ideas)\b")


ROW_HOW_REPLY = (
    "Say the one thing you would want {them} to hear, and name your part in it rather than the "
    "case for it. One sentence does more than a long apology.",
    "Keep it to what you did, not what {they} did: one specific thing, said plainly, then let "
    "{them} answer. A list of everything is a fresh row.",
    "Do it in person or on the phone rather than in writing, and lead with the apology rather "
    "than the reason for it. The reason comes after, if it is wanted at all.",
)


ROW_SPACE_REPLY = (
    "A couple of days does no harm if nobody is stewing on it - say so in one line first, so the "
    "silence is not read as the last word.",
    "Space works better with a time on it: say you will leave it until the weekend, mean it, and "
    "then come back with the one thing you want {them} to hear.",
    "A day or two is usually right. Much longer than that and it stops being space and starts "
    "being a way of not having the conversation.",
)


# A teenager who will not talk has not been quarrelled with yet. The knowledge base answers the
# line itself with the teenager card ("Stop asking what is wrong ... be around without an
# agenda"), and the card's own move is the right thing to hand back to "what do i do". What the
# row pool has for that ask is the apology script - "lead with the apology rather than the reason
# for it", "name your part in it" - which invents a quarrel and hands the person the blame for it:
#
#     my daughter is 14 and wont talk to me / she spends all evening in her room / what do i do
#       -> "Do it in person or on the phone rather than in writing, and lead with the apology ..."
#
# So only the bare ask for a move stands the pool down, and only while the chat has said nothing
# about what happened between them: "should i ring her" and "should i give him space" are the
# row's own questions and keep the row's advice, and a chat with "i shouted at her" in it is a
# quarrel in the person's own words, where the apology is what they are asking for.
A_QUIET_AT_ME = re.compile(
    r"\b(?:wont|won't|doesnt|doesn't|never|stopped|not)\s+"
    r"(?:talk|talks|talking|speak|speaks|speaking)\s+to\s+(?:me|us)\b")


A_A_CHILD = re.compile(
    r"\b(?:son|daughter|child|children|kid|kids|boy|girl|eldest|youngest|teen|teens|"
    r"teenager|teenagers)\b")


A_TEN_OR_OVER = re.compile(
    r"\b(?:teen|teens|teenager|teenagers|teenage|teenaged|adolescent|adolescents|1[0-9])\b")


A_WHAT_HAPPENED = re.compile(
    r"\b(?:argued|arguing|argue|rowed|had a row|had an argument|an argument|fight|fighting|"
    r"fought|falling out|fell out|fallen out|snapped at|shouted at|shouting|yelled|lost my "
    r"temper|lost it with|said something (?:i|that i) regret|i apologised|i said sorry|"
    r"i was wrong|my fault)\b")


A_BARE_MOVE_ASK = re.compile(
    r"^\s*(?:so\s+|and\s+|ok\s+|okay\s+)?what (?:do|can|could|should|would) (?:i|we) "
    r"(?:do|say)\b[\s.?!]*$", re.I)


def _a_teen_has_gone_quiet(text):
    """True when the line's silence is a teenager's withdrawal rather than a row to mend."""
    said = str(text or "").lower()
    if not A_QUIET_AT_ME.search(said):
        return False
    if A_WHAT_HAPPENED.search(said):
        return False
    return bool(A_A_CHILD.search(said) and A_TEN_OR_OVER.search(said))


def _a_quarrel_since(memory, turn):
    """True when the chat has said what happened between them since the row was noted."""
    rows = [t for t in (memory or {}).get("turns") or [] if isinstance(t, dict)]
    for row in rows[max(0, int(turn or 0)):]:
        if A_WHAT_HAPPENED.search(str(row.get("user") or "").lower()):
            return True
    return False


def _the_ask_in_the_line(clean):
    """The question a re-read line carries after the row it leans on, or the line itself.

    The composer re-reads a short line with the subject it leans on in front of it, so a question
    asked a turn after a row arrives here as "me and my mum had a massive row should i ring the
    plumber". The row is not what the line asks, so the ask after it is what is answered.
    """
    said = A_ROW.search(clean)
    if said:
        tail = clean[said.end():].strip()
        if tail and _ASKS_AFTER.search(tail):
            return tail
    return clean


def _a_row_next(clean, memory):
    """The reply for a line that asks what to do next about a row from a turn or two ago, or None.

    The row has to have been said out loud first (`memory["row"]`, written by `_a_row`), and the
    line has to be about reaching the person: "should i ring her back tonight" is this row, while
    "should i ring the plumber" after it is not.
    """
    clean = _the_ask_in_the_line(clean)
    row = memory.get("row") if isinstance(memory, dict) else None
    if not isinstance(row, dict) or not row.get("them"):
        return None
    turn = len(memory.get("turns") or [])
    if turn - int(row.get("turn") or 0) > 3:
        return None
    how = bool(ROW_HOW.search(clean))
    if (A_BARE_MOVE_ASK.match(clean) and _a_teen_has_gone_quiet(row.get("text") or "")
            and not _a_quarrel_since(memory, row.get("turn"))):
        # The move for a teenager's silence is the card's own ("Stop asking what is wrong ...
        # be around without an agenda"), not a script for an apology nobody asked for. Standing
        # down lets the card's step come back to the person who asked what to do.
        return None
    # What the other person asked for is about the row without being the next step of it.
    space_said = bool(ROW_SAID_SPACE.search(clean))
    if _the_base_answers_the_row(clean, memory):
        return None  # the base has an answer about this row, and it is the better one
    if how and row.get("handed_over"):
        return None  # the base answered the row itself, so its own script comes back here
    if (how and (WANTS_AN_APOLOGY.search(clean) or ASKS_FOR_WORDS.search(clean))
            and _the_base_has_an_answer(clean, memory) is not None):
        # The knowledge base has the words written out - the apology ("name what you did, say why
        # it was wrong, no but") and the message to send someone ("make it a question about them,
        # not an accusation") - and the pool's shorter sentence would stand in front of it. The
        # ask to put it right, or to sort it out, is the row's own, and stays here.
        return None
    if not how and not space_said \
            and not (ROW_CONTACT.search(clean) and ROW_CONTACT_ASK.search(clean)):
        return None
    # "how do i put it right" leans on the row for its "it", so no person has to be named; a
    # question about reaching somebody does have to say who.
    if not how and not space_said and not _names_the_person(clean, row):
        return None
    if len(clean.split()) > 14 or LOSS.search(clean) or _safety_thread(memory):
        return None
    if how:
        pool = ROW_HOW_REPLY
    elif space_said or ROW_SPACE.search(clean):
        pool = ROW_SPACE_REPLY
    else:
        pool = ROW_NEXT
    return pick(tuple(line.format(them=row["them"], they=_they_of(row),
                                  their=_their_of(row["them"])) for line in pool),
                memory, clean)


# How a row ends is part of the row, not a fact to note: "she hung up on me" two turns in was
# answered "Got it, she hung up on you", which is the bot filing the worst minute of somebody's
# evening. The ending is what the person is still sitting in, so it is answered.
ROW_ENDING = re.compile(
    r"\b(?:hung up|put the phone down|slammed (?:the door|down the phone|the phone)|walked out|stormed off|"
    r"blocked me|swore at me|shouted at me|went to bed|left the room|said nothing|"
    r"slept (?:on the sofa|in the spare room)|(?:is|isnt|isn'?t|was|wasnt|wasn'?t) (?:not )?"
    r"(?:talking|speaking) to me|hasn'?t spoken to me)\b")


ROW_ENDING_REPLY = (
    "That is the worst bit of it - being shut out leaves you with nothing to do with yourself. "
    "It usually means the night is needed, not that it is finished.",
    "That sounds like it ended at the worst moment. Nothing gets better tonight by chasing it, so "
    "leave {them} be and say your one true thing when it is calmer.",
    "A door, a silence or a walk out is a way of stopping the row, not a verdict on it. Let it "
    "settle, then say the one thing you actually wanted {them} to hear.",
)


# One ending is not the others: "he said nothing" and "shes not speaking to me" were answered
# "Hanging up is a way of stopping the row", and nobody had hung up.
ROW_HUNG_UP = re.compile(
    r"\b(?:hung up|put the phone down|slammed (?:the phone|down the phone)|blocked me|"
    r"blocked my number)\b")


ROW_ENDING_REPLY_HUNG_UP = (
    "Hanging up is a way of stopping the row, not a verdict on it. Let it settle, then say the "
    "one thing you actually wanted {them} to hear.",
)


def _a_row_ending(clean, memory):
    """The reply for the line that says how the row ended, or None.

    Only the turn or two after a row that was said out loud: on its own, "she hung up on me" is
    not enough to answer without the row behind it.
    """
    clean = _the_ask_in_the_line(clean)
    row = memory.get("row") if isinstance(memory, dict) else None
    if not isinstance(row, dict) or not row.get("them"):
        return None
    turn = len(memory.get("turns") or [])
    if turn - int(row.get("turn") or 0) > 3:
        return None
    if not ROW_ENDING.search(clean) or len(clean.split()) > 14:
        return None
    if LOSS.search(clean) or _safety_thread(memory):
        return None
    pool = ROW_ENDING_REPLY
    if ROW_HUNG_UP.search(clean):
        pool = ROW_ENDING_REPLY + ROW_ENDING_REPLY_HUNG_UP
    return pick(tuple(line.format(them=row["them"], they=_they_of(row),
                                  their=_their_of(row["them"]))
                      for line in pool), memory, clean)


def _row_pronoun(clean):
    """How the reply says the person they fell out with: hers and his where the line is clear."""
    if ROW_HER.search(clean):
        return "her"
    if ROW_HIM.search(clean):
        return "him"
    return "them"


def _their_of(them):
    """The possessive that goes with the object form the row keeps: her, his, their.

    The subject form is not enough on its own: "ask her how it sounded from where she were
    sitting" was the row's own sentence with a plural verb left in it, so the sentence is written
    with the possessive instead and the pronoun never has to agree with a verb."""
    them = str(them or "them").lower()
    return {"her": "her", "him": "his"}.get(them, "their")


def _they_of(row):
    """The subject form kept with the row, or "they" for a row recorded before it was kept."""
    return str((row or {}).get("they") or "they")


def _row_subject(clean):
    """The same person where the sentence needs a subject: "what she did", not "what her did"."""
    if ROW_HER.search(clean):
        return "she"
    if ROW_HIM.search(clean):
        return "he"
    return "they"


def _the_deed_before(memory):
    """The deed the line before this one reported, or None. The follow-up's pool follows it."""
    if not isinstance(memory, dict):
        return None
    told = [turn.get("user") for turn in (memory.get("turns") or [])[-1:] if isinstance(turn, dict)]
    return deed_of(told[0]) if told else None


def _a_repair_is_open(memory):
    """True when the turns just said are one repair, with the asks in the middle of it.

    The walk itself is the repair reading's (bot/compose/repair.py::a_repair_is_open), because
    the knowledge base needs it as well: the card for a small child who is late talking answers
    "hes not speaking to me" the day after an apology, and it has to stand down for the repair.
    """
    return repair.a_repair_is_open(memory)


# What a person can and cannot do is a fact about them, not a complaint. After a "what could i do
# with her on a sunday" a line like "she cant walk far" is the shape of the plan, so it is the
# answer to a plan the planner still owes, not a report to ask how long it has been going on.
LIMIT = re.compile(r"\bcan'?t\b|\bcant\b|\bisn'?t able\b|\bnot able\b|\bonly manage\b")


PLAN_ASK = re.compile(
    r"\bwhat (?:could|can|should|shall) (?:i|we) do\b|\bwhat would you do\b|"
    r"\bwhere (?:could|can|should) (?:i|we) (?:go|take)\b|\bany ideas\b")


def _after_a_plan(memory, clean):
    """True when the chat is about a plan, so a limit on it is part of the plan.

    The plan can be the question just asked ("what could i do with her") or the plan already on
    the table ("we are going to york next weekend"): "my sister cant walk far" after either is a
    limit on the trip, not a health report to date. A plan from further back is a different
    conversation, so only the last couple of turns count.
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    mine = " ".join(str(clean).lower().split())
    for turn in reversed(turns):
        said = " ".join(str(turn.get("user") or "").lower().split())
        if not said or said == mine:
            continue
        if PLAN_ASK.search(said):
            return True
        break
    # The plan the store holds, if it was said a turn or two ago: "we are going to york next
    # weekend" leaves a plan in the store, and the limit that follows it belongs to that plan.
    log = (memory or {}).get("facts_log")
    if isinstance(log, list):
        newest = len(turns)
        for entry in reversed(log):
            if not isinstance(entry, dict):
                continue
            if entry.get("key") not in ("plan", "plans"):
                continue
            try:
                when = int(entry.get("turn"))
            except (TypeError, ValueError):
                return False
            return newest - when <= 3
    return False
