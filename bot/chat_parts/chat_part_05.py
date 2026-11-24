"""Part 5 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import fallback, pick
from ..compose import leaving as leaving_reading
from ..understanding import topics
from ..understanding.kinds import ANSWERING_A_QUOTED_ASK, the_manners_question
from ..compose import stepwords
from ..memory import PERSON_TROUBLE as SOMEONE_TROUBLE
from ..memory import current, user

from ..memory import ack, current, last_user as _last_said, user

from ..memory import facts
from .chat_part_01 import (
    SMILES, TOKEN,
)
from .chat_part_02 import (
    NEWS_REPLIES,
)
from .chat_part_04 import (
    BOT_ABOUT, BOT_FEELING_ASK, BOT_MOOD_ASK, PLANS_REPLIES, SELF_ABOUT, _a_feeling_about_me,
    _about_bot_life, _as_meant, _asks_about_plans, SELF_AFTER, OPINIONS, CONTEXT_CHAT, REPLIES,
)


# "What did you do at the weekend", "what have you been doing", "where were you last night":
# the bot has no weekend and no yesterday, and that is the honest answer, in the same friendly
# register as the no-plans line for a Saturday still to come. Read as an ordinary question these
# went to the search hedge, to the weekend-plan advice, or to "we're still at the beginning" as
# if the person had said what they had been doing. The understanding engine reads the whole line
# as an ask about the bot's own doings (`about_bot_kind` is "doings"), so one pool answers it.
BOT_DOINGS = (
    "Nothing much on my side — no day of my own to spend. How has yours been?",
    "Not much: I'm here whenever you want me, which is the whole of what I do. What did you "
    "get up to?",
    "Nothing, honestly — no weekend and no evening of my own. How did yours go?",
)


# "Where have you been all day", "where were you last night", "where have you been hiding": the
# where of a bot with no time of its own. The address line is the answer to "where do you live",
# and saying "no address" to this one said nothing about the day the person was asking about.
BOT_WHEREABOUTS = (
    "Nowhere between messages - this chat is the whole of where I am. What's your day been like?",
    "No place of my own to have been: I'm here when you write and nowhere in between. How has "
    "yours gone?",
    "Nowhere, honestly - I don't go anywhere and I don't wait anywhere. How has your day been?",
)


# The same answer when the time named is still to come: "you doing anything tonight", "what are
# you up to this weekend". Every line above asks the person about a day already spent ("What did
# you get up to?"), which is the wrong way round for an evening that has not happened yet.
BOT_DOINGS_AHEAD = (
    "Nothing planned on my side — no evening of my own to spend. What about yours?",
    "Not much: I'm here whenever you want me, which is the whole of what I do. What are you up "
    "to?",
    "No plans of my own — nothing to do and nowhere to be. What have you got on?",
)


# The time words that name something still to come, and the past markers that take the same word
# back: "what have you been up to this week" is a week behind them, not ahead.
AHEAD_TIME = frozenset("tonight tomorrow later weekend weekends week weeks".split())


BEHIND_TIME = frozenset("did done been was were had yesterday last".split())


# "Have you ever been in love", "were you ever ill", "have you ever kept a pet": the same territory
# as "what did you get up to", with the whole of a life in place of the weekend. The reading is the
# doings one (kinds._asks_about_its_experience), so the pool is picked by the word "ever" rather
# than by a list of every thing a person can have done. Each line says what the bot is, because a
# bare "no" to a friendly question reads as a machine being short with them.
BOT_NEVER = (
    "Never \u2014 I'm a program, so there's no list of things I've done. What made you ask?",
    "Nothing like that, no \u2014 I'm a program, so nothing has happened to me the way it happens "
    "to you. What's been going on with you?",
    "None, no \u2014 I'm a program, so I've no past of my own to tell you about. What put that in "
    "your head?",
)


BOT_DOINGS_BARE = (
    "Not much on my side — I'm here whenever you want me. What's yours been like?",
    "Nothing much, honestly — no day of my own to spend. What did you get up to?",
)


# A stretch of time named after "been up to": "what have you been up to this week". The plain ask
# has an answer of its own higher up, so only the named stretch arrives here.
BEEN_UP_TO_SPAN = frozenset("week weeks month months year years".split())


def _a_shape_no_list_knows(words):
    """True for the two shapes of the ask ("how do you fill your time") no pattern list has."""
    if words & {"keeps", "keeping"}:
        return True
    return "been" in words and bool(words & BEEN_UP_TO_SPAN)


def _doings_pool(words):
    """The pool for how the bot fills its time, picked by whether a piece of time was named."""
    if words & AHEAD_TIME and not words & BEHIND_TIME:
        return BOT_DOINGS_AHEAD
    if words & {"weekend", "weekends", "yesterday", "night", "morning", "evening", "day", "week",
                "today", "tonight", "lately", "days"}:
        return BOT_DOINGS
    return BOT_DOINGS_BARE


# A sign-off with a time on it is still a sign-off: "see you at 5", "talk to you after work",
# "catch you on monday". The reading counts the ask about the bot's own day on the time word and
# not on what the line is doing, so "see you at 10.30 tomorrow" was read as an ask about the
# bot's evening and answered "Not much: I'm here whenever you want me" - a diary entry in place
# of a goodbye. The farewell module has these lines, so this one stands down on them.
def _a_sign_off_with_a_time(understood):
    text = str((understood or {}).get("text") or (understood or {}).get("clean") or "")
    return bool(text) and leaving_reading.reads_as_leaving(text)


def _about_bot_doings(understood):
    """The pool for "what have you been up to", or None if that is not what was asked."""
    if not isinstance(understood, dict) or understood.get("about_bot_kind") != "doings":
        return None
    if _a_sign_off_with_a_time(understood):
        return None
    words = set(understood.get("norm") or ())
    if words & {"ever", "once"}:
        # An experience asked of a program that has had none. Read here rather than in a branch of
        # its own, because the honest answer is the same one: there is nothing of its own to tell.
        return BOT_NEVER
    # "where have you been all day" asks where as well as what, and "nothing much on my side"
    # answers only half of it: the bot is not anywhere between one message and the next, which
    # is the whole of the answer to the where.
    if "where" in words:
        return BOT_WHEREABOUTS
    # One choice of pool for both shapes of the ask: `_doings_pool` is where the time word is
    # read, and it was written after this copy, so "you doing anything tonight" fell to the bare
    # pool ("What did you get up to?") while "what are you up to tonight" read it as a time.
    return _doings_pool(words)


def _about_bot(clean, understood=None, memory=None):
    # The older table answers the plain asks ("do you sleep") whatever follows them; the newer
    # one is only taken when the line stops at the bot, so "do you cook a chicken with the lid
    # on" still goes to the kitchen knowledge. A question about the bot's own life is answered
    # from the reading first, so "have you got a family" and "do you have kids" get the same
    # honest answer as "do you have a family" instead of a search hedge.
    life = _about_bot_life(understood)
    if life:
        return life
    doings = _about_bot_doings(understood)
    if doings:
        return doings
    # How the bot fills its time is one ask, in every spelling: "whatcha doing", "watcha up to
    # mate", "wuu2", "what keeps you busy". The engine reads the whole line as small talk, and
    # the pool answers it before the phrase lists below, which answered some spellings with a
    # plan of their own ("No plans. I'm around if you want to talk something through.") and the
    # composer answered others with how the bot is ("I'm well, thanks") or with advice about the
    # person's week. "what do you do" is not this ask - the engine reads it as an about-the-bot
    # question - so its capabilities card is untouched. `_a_shape_no_list_knows` keeps the older
    # fence for a caller that brings no reading.
    norms = list((understood or {}).get("norm") or ())
    if the_manners_question(norms) and (
            str((understood or {}).get("intent") or "") == "smalltalk"
            or _a_shape_no_list_knows(set(norms))):
        return _doings_pool(set(norms))
    said = _as_meant(clean, understood)
    # The name a person gave the bot is the bot's name in this chat: "call you bob" and then
    # "what are you called" is answered with Bob, not with the flat "no name of my own" that
    # would contradict the last thing the person said (`bot/memory/facts.py::bot_name`).
    named = str(((memory or {}).get("user") or {}).get("bot_name") or "").strip()
    if named and facts.BOT_NAME_ASK.search(said):
        return (named + " \u2014 the name you gave me. What can I help with?",
                "You call me " + named + ". What can I do for you?",
                "I'm " + named + ", since you named me.")
    # A quoted ask about the bot is somebody else's question: "how do i answer what are you doing
    # at the moment" is an interview, and the bot's own afternoon is the wrong answer to it. The
    # frame is the understanding's (kinds.ANSWERING_A_QUOTED_ASK), so there is one definition of
    # it, and the answers module claims the turn with the interview answer.
    quoted = bool(ANSWERING_A_QUOTED_ASK.search(said))
    for pattern, replies in BOT_ABOUT:
        if quoted and pattern is BOT_ABOUT[2][0]:
            continue
        if pattern.search(said):
            return replies
    # "any plans tonight": the same ask as "what are you up to tonight" with the verb left out,
    # read after the table above so a line that names the bot keeps the pool it already had.
    if not quoted and _asks_about_plans(said):
        return PLANS_REPLIES
    for pattern, replies in SELF_ABOUT:
        match = pattern.search(said)
        if match and _self_only(said, match):
            return replies
    # Any feeling word the person asks the bot about, not only the handful the table above names
    # one by one. "do you ever get annoyed", "do you ever feel sad", "are you ever grumpy" were
    # answered "That's beyond what I know well, sorry. Searching for it will turn up better
    # sources" - a search hedge to a question about the thing in front of them - while
    # "do you ever get angry" and "do you get lonely" were answered, because those two words
    # happened to have a pattern of their own.
    # "what are you good at" is not a question about how the bot feels: it asks what the bot can
    # do, and the composer answers it with the capability line. The feeling asks open "are you
    # ..." or "do you ever ...", where the feeling word is the whole of the question.
    if WHAT_ARE_YOU_CAN_DO.match(clean):
        return None
    match = BOT_FEELING_ASK.search(clean)
    if match and _self_only(clean, match):
        return _a_feeling_about_me(match.group("mood"))
    match = BOT_MOOD_ASK.search(clean)
    if match and _self_only(clean, match):
        return _a_feeling_about_me("moods")
    return None


# "what are you good at", "what are you best at", "what are you into": what the bot is like,
# which the composer's own readings answer. "good" and "into" are mood words to the reader here,
# so it took the line and answered a question about feelings that nobody asked.
WHAT_ARE_YOU_CAN_DO = re.compile(r"\bwhat are you\s+(?:good|best|bad|worst|into|wearing|like)\b")


def _self_only(clean, match):
    """True when the line asks about the bot and stops there, not about a thing it names.

    "do you cook?" is about the bot; "do you cook a chicken with the lid on?" is about the
    chicken and belongs to the kitchen knowledge, so anything but a filler word after the ask
    leaves the line alone.
    """
    rest = clean[match.end():].strip(" ?!.,;")
    return all(word in SELF_AFTER for word in rest.replace(",", " ").split())


def _opinion(clean, tokens, memory):
    """A brief view when the person explicitly asks what the bot thinks of something."""
    asks = re.search(r"\b(do you like|do you prefer|what do you think of|what do you think about|"
                     r"which do you prefer|what(?:'s| is) your favourite|"
                     r"what's one|which one|favourite one)\b", clean)
    if not asks or len(tokens) > 12:
        return None
    subject = clean
    for keys, reply in OPINIONS:
        if any(re.search(r"\b" + re.escape(key) + r"\b", subject) for key in keys):
            return pick(reply, memory)
    record = current(memory)
    if record and len(tokens) <= 9:
        words = set(record.get("words") or [])
        for keys, reply in OPINIONS:
            if words & set(keys):
                return pick(reply, memory)
    return None


def _context_follow_up(clean, memory):
    """A question about a worry from the last few turns: answer the question itself."""
    near = set()
    topics = memory.get("topics")
    if isinstance(topics, list):
        for record in topics[-3:]:
            if isinstance(record, dict):
                near |= set(record.get("words") or [])
    if not near:
        return None
    for keys, cues, replies in CONTEXT_CHAT:
        if not near & set(keys):
            continue
        if any(re.search(cue, clean) for cue in cues):
            return pick(replies, memory)
    return None


# "Boring" is what a film was and what somebody calls a person, and only the second reading has
# the person as its subject: "im boring" is a label somebody put on them, not their own boredom.
# The mood reader took both, so "my mum says im boring" was answered "Boredom is a good excuse for
# a walk with a podcast", which answers a complaint nobody made. The label on the person is not a
# thing that caused a feeling, so the word is owned by it and the mood pools do not see the line:
# the person's own "im boring" is answered by the self-judgement pools just above, and the same
# words said by somebody else by bot/compose/said_about_me.py.
A_LABEL_ON_THE_PERSON = re.compile(
    r"\b(?:im|i'm|i am|i\s*am)\s+"
    r"(?:so\s+|really\s+|quite\s+|a bit\s+|just\s+|getting\s+)?boring\b")


AE = {
    "tired": "tired",
    "stressed": "stressed",
    "anxious": "anxious",
    "sad": "sad",
    "lonely": "lonely",
    "bored": "bored",
    "annoyed": "annoyed",
    "happy": "happy",
}


# Short lines with content but no question: a busy week, a plan for later, an apology
# for talking too much, a bad day that will not be pinned down. They are not asks, and
# they are not "ok" either, so the stock lines fit them badly.
BUSY_RE = re.compile(r"\b(?:busy|mad|hectic|mental|crazy|slammed|non[- ]?stop|full[- ]?on|"
                     r"flat out)\b|\bone thing after another\b")


BUSY_WORK = {"work", "week", "day", "days", "month", "job", "shift", "shifts", "office",
             "deadline", "deadlines", "school", "college", "uni", "term", "kids", "house",
             "life", "everything", "weekend", "mornings"}


# Worn out by the run of things, said without a feeling word: "work has been manic", "my week has
# been chaos", "im rushed off my feet", "i cant keep up", "i havent stopped all day". Nobody in
# these lines names how they feel, so the pools of feelings never see them, and the busy pool
# above only sees the ones that put a noun beside a word it knows. The rest land on "Noted! What
# would be most useful to talk about?" - a reply that would fit any message at all.
#
# A load is read three ways: a stretch of time or a job and how it went, the person being run off
# their feet, or the pile of it getting too big. Each shape is a pattern rather than a phrase, so
# a line nobody wrote down still lands, and the words that turn it away (an ask, a turn, someone
# else's day) are guards below rather than an avoid word for each.
LOAD_THING = (r"(?:work|works|job|shift|shifts|week|weeks|weekend|month|day|days|term|year|life|"
              r"things|everything|it|staffing|rota|hours)")


LOAD_WORD = (r"(?:manic|mad|crazy|hectic|mental|chaos|chaotic|relentless|non[- ]?stop|flat out|"
             r"slammed|jam(?:med)?|full[- ]?on|busy|tough|hard|rough|a lot|too much)")


# The size of the job is not the same as the strain of it: "ive taken on a lot more" is what
# somebody says while they are building the case for a rise, and answering it with "guard one
# evening this week" loses the thread. So the thing-and-load shape below does not reach across a
# verb of taking work on, while the other shapes still do ("ive taken on a lot and cant keep up"
# is caught by that arm on its own).
LOAD_TOOK_ON = r"(?:taken|took|taking|take|takes)\s+on\b"


OVERLOAD = re.compile(
    r"\b" + LOAD_THING + r"\s*(?:has|have|had|s|is|was|were)?\s*(?:been|bin)?\s*"
    r"(?:(?!" + LOAD_TOOK_ON + r")[^.!?]){0,16}\b"
    + LOAD_WORD + r"\b"
    r"|\b(?:it'?s|its|it was|been|im|i'?m|i am|we'?re|we are)\s+[^.!?]{0,12}\b"
    r"(?:non[- ]?stop|slammed|go go go|on the go|flat out|manic|hectic|relentless)\b"
    r"|\brushed off (?:my|our) feet\b|\bcan'?t keep up\b|\bcant keep up\b"
    # The same line said with "run": "im run off my feet", "ive been run ragged this week".
    # "rushed" was here and "run" was not, so the commonest way of saying it reached nothing.
    r"|\b(?:run|runs|ran|running) off (?:my|our|your) feet\b"
    r"|\b(?:run|ran|running) (?:me )?ragged\b|\bworked off (?:my|our) feet\b"
    r"|\bcan not keep up\b|\bno let up\b|\bhavent stopped\b|\bhaven'?t stopped\b"
    r"|\b(?:a bit|a lot|too|really|so) much (?:at the moment|right now|on my plate|this week|"
    r"lately|these days|going on)\b"
    r"|\b(?:too many|so many) things (?:on|to do)\b"
    r"|\brunning on empty\b|\bshort[- ]staffed\b"
    r"|\b(?:i'?ve|i have|ive)\s+(?:had|got)\s+(?:a|one)\s+(?:lot|ton)\s+on\b"
    r"|\b(?:been|im|i'?m|i am)\s+(?:swamped|buried|snowed under)\b")


# A line that goes on to ask for something ("work has been manic, should i quit") is asking, not
# telling, and the module that can help with the thing asked answers it. A line that turns ("but
# i got a promotion") is news about something else as well, so the load is not the whole of it.
# Someone else's trouble in the same breath ("my mum is ill too") makes the line as much about
# them as about the load.
LOAD_ASK = re.compile(r"\b(?:should|shall|how do|how can|how should|what should|what can i|any tips|"
                      r"any advice|advice|tips|help me|why do|what do|can i|is it|do i|shall i)\b")


LOAD_TURNED = re.compile(r"\b(?:but|though|although|until|except)\b")


LOAD_SOMEONE_ELSE = re.compile(r"\b(?:my (?:mum|mom|mam|dad|son|daughter|wife|husband|partner|"
                                r"boyfriend|girlfriend|friend|brother|sister|nan|gran|grandma|"
                                r"grandad|kid|kids|child|children|baby|boss|mate|colleague|dog|"
                                r"cat)s?|he|she|they|them|his|her|their)\b")


LOAD_FEELS = re.compile(r"\bfeel(?:ing|s|t)?\s+(?:like\s+)?(?:crying|awful|terrible|dreadful|low|"
                        r"down|sad|rubbish|hopeless|useless|exhausted|drained|knackered|"
                        r"empty|numb|overwhelmed|anxious|worried|stressed|guilty|ashamed|"
                        r"lonely|angry|upset|ill|sick|done)\b")


PLAN_RE = re.compile(r"\b(?:i might|i may|i think ill|i think i will|im going to|i am going to|"
                     r"planning to|gonna|ill probably|might go|might have)\b")


# A plan gets "good plan"; a possible problem dressed as a plan ("I think I'll be late",
# "I'm going to be sick", "I might have left the oven on") must not. So the plan reading
# gives way to anything that sounds like trouble, and "might have" is a worry, not a plan.
PLAN_STOP = {"help", "hand", "advice", "need", "needs", "needed", "recommend", "recommendation",
             "suggest", "suggestion", "best", "cheap", "cheaper", "recipe", "fix", "how",
             "which", "what", "should", "buy", "cook", "make", "get", "worth", "better",
             "sick", "ill", "late", "hurt", "broke", "broken", "lost", "missed", "miss",
             "forgot", "forgotten", "left", "cancel", "cancelled", "worried", "worry",
             "scared", "anxious", "failed", "fail", "fired", "sacked", "debt", "owe",
             "arguing", "fight", "crying", "upset", "angry", "worse", "pain", "ache",
             "bleeding", "pregnant", "doctor", "hospital", "police", "accident", "stuck",
             "wrong", "quitting", "quit", "die", "dying",
             # a plan is something the person chooses to do; these are things that happen
             # to them and turn the same "i might" into bad news
             "lose", "losing", "afford", "able", "redundant", "bankrupt", "evicted",
             "homeless", "hungry", "rejected", "declined", "kicked", "behind", "stuck",
             "worse", "worrying", "crying", "hiding",
             # "i might be depressed" is a state said as a possibility, not a plan for the day:
             # with only the words above, "i think i might be depressed" got "Nice. Tell me how
             # it goes." and "i think i might be autistic" got a reflection. These name a state
             # a person is in; none of them is a thing they will do.
             "depressed", "depression", "depressive", "burnout", "burnt", "exhausted",
             "overwhelmed", "unwell", "poorly", "numb", "hopeless", "worthless", "useless",
             "miserable", "low", "sad", "lonely", "empty", "tired", "knackered", "shattered",
             "drained", "struggling", "stressed", "stress", "anxiety", "panic", "panicky",
             "awful", "rubbish", "terrible", "horrible", "addicted", "addiction", "unhappy",
             "despair", "grieving", "autistic", "adhd", "anorexic", "bulimic"}


# "i might not be able to pay rent" is the same shape as "i might go for a walk later", and the
# thing that tells them apart is the verb: a plan is something the person does, so a plan marker
# in front of a negation, a loss or a thing that happens to them is bad news, not a plan.
PLAN_TROUBLE = re.compile(r"\b(?:might|may|probably|likely) not\b|\bnot be able\b|"
                          r"\b(?:can't|cant|won't|wont|couldn't|cant|cannot)\b|"
                          r"\bno longer\b|\bhave to\b|\bhad better\b")


# "i might have left the oven on" is a worry; "i might have an early night" is a plan, and the
# word after "might have" says which: a determiner starts the thing they will do.
PLAN_WORRY = re.compile(r"\bthink i (?:have|ve)\b|\b(?:might|may) have (?!a\b|an\b|the\b|"
                        r"my\b|our\b|some\b|this\b)")


SORRY_TALK = re.compile(r"\b(?:sorry|apolog\w*)\b.*\b(?:rant|ranting|moan|moaning|going on|"
                        r"going off|that was (?:a lot|heavy|too much|long)|heavy|rambl\w*|"
                        r"ear|dumping|vent\w*|waffl\w*|downer)\b")


# "can i tell you something", "i want to say something", "i have something to ask you": a bid to
# speak, not a plan and not an ask with a subject in it. Nothing has been said yet, so the only
# good reply is room to talk; main answers these with a search hedge.
#
# "i have something to say" is the same bid and needed its own branch: the reading stopped calling
# it an opener (an opener is answered with a question back - "Ask away, I'm listening. What's
# going on?" - and a person who has already decided to speak wants room, not a question), and
# nothing here held "something ... to say", so the line fell through to "Noted: you have something
# to say.", which is the bot saying the line back. "nothing to say" is not held: the branch asks
# for something, somethin or a thing.
SAY_SOMETHING = re.compile(r"\b(?:say|ask (?:you|ya)|tell (?:you|ya)|show (?:you|ya)|run (?:it|"
                           r"something|this) by (?:you|ya))\b[^.?!]*\b(?:something|anything|this|"
                           r"a question|one thing|a quick question)\s*[.?!]*$|"
                           r"\b(?:something|a question|one thing)\s+to\s+(?:tell|ask)\s+"
                           r"(?:you|ya)\s*[.?!]*$|"
                           r"\b(?:have|got)\s+(?:something|somethin|a thing|one thing)\s+to\s+"
                           r"say\s*[.?!]*$|"
                           r"\b(?:have|ask|ask (?:you|ya))\s+(?:a|one)\s+(?:quick\s+)?question"
                           r"\s*[.?!]*$")


# The same words are also how somebody asks whether to speak at all: "should i say something",
# "do you think i should bring it up", "shall i text her". That is a decision they want help
# with, not a bid for the floor, so the invitation to talk stands aside - and "should i tell
# her" never reached the bid in the first place, so this keeps one ask getting one answer.
ASK_WHETHER_TO_SPEAK = re.compile(
    r"\b(?:should|shall|ought|do you think i (?:should|need to)|is it worth|would you)\b")


# A way of leaving for somewhere: what makes a line that names a place a trip rather than a
# plan. "im going to porto in june" wants Porto, not "Worth doing. What would you like help
# with first?" - the place has its own answer (a city guide, the weather there), so a plan line
# must not take the turn from it.
GO_AWAY = re.compile(r"\b(?:go|going|goes|went|off|heading|fly|flying|flew|travel\w*|trip|"
                     r"holiday|vacation|visit\w*|booked|booking)\b")


VAGUE_WORDS = {"i", "im", "its", "it", "just", "everything", "all", "of", "dunno", "idk", "know",
               "dont", "not", "sure", "one", "those", "days", "day", "kind", "sort", "where",
               "to", "start", "and", "yeah", "ok", "okay", "today", "lately", "honestly", "a",
               "bit", "lot", "loads", "stuff", "things", "thing", "really", "tbh"}


# A plan being aired, or something on the calendar: "i'm thinking of buying a used car",
# "i want to start saving", "i have a performance review tomorrow". No question is asked,
# so there is nothing to answer, but the person has just told you what is on their mind and
# a friend picks it up. The domain modules answer these too when they know the subject, and
# they outrank this; this is what the person gets when nobody else speaks.
# The small words a person drops in front of the verb without changing what they mean: "i just
# want to go home" is the same plan as "i want to go home", and "im really trying to" the same as
# "im trying to". Before this the filler broke the read, and "i just want to go home" and "i just
# want to sleep" fell to the stock "Got it. Is there anything you'd like a hand with?" while the
# plain wording got the plan reply. "Only" is left out on purpose: it is usually a limit rather
# than a softener ("i only want to spend 20 quid").
SOFTEN = (r"(?:(?:just|still|actually|probably|really|honestly|literally|kind of|sort of|"
          r"kinda|sorta) )?")


INTENT_RE = re.compile(
    r"\b(?:i " + SOFTEN + r"(?:want to|wanna|plan to|plan on|started)|"
    r"(?:im|i am) " + SOFTEN + r"(?:thinking (?:of|about)|planning (?:to|on)|going to|"
    r"trying to|looking to|hoping to|training|saving|learning|working on|preparing|"
    r"getting ready)|"
    r"i " + SOFTEN + r"have decided to|"
    r"(?:ive|i've) " + SOFTEN + r"(?:decided to|started|been trying to|been meaning to|"
    r"been thinking (?:of|about)))\b")


# A line that says what the person is doing next, not a goal they want help with: "im going to
# bed early", "im going to have a bath", "im going to work now". The plan pool asks where they
# are with it and what the first step is, which is daft for going to bed, and it was the third
# question in a row in a chat like "im tired" / "im hungry too" / "i had a long day" /
# "im going to bed early". These lines get a short, warm reply and no question.
# What the thing they are going to *is*, so the line can say the fitting thing: a bath and an early
# night are rest, a shift and the shops are not.
NEXT_REST = re.compile(
    r"\b(?:bed|sleep|nap|bath|shower|early night|lie down|sit down|read|book|film|telly|"
    r"boxset|relax\w*|unwind\w*|put my feet up|some sleep)\b")


NEXT_ACT = re.compile(
    r"\b(?:work|school|the shops?|town|church|gym|walk the dog|dinner|lunch|breakfast|tea|food|"
    r"washing|ironing|cleaning|tidy|pack|pick (?:up |the ))\b")


NEXT_UP = re.compile(
    r"\b(?:im|i am|im just|im off|i'm)\s+(?:going|off)\s+(?:to\s+|for\s+)?(?:"
    r"bed|sleep|have a bath|have a shower|take a bath|take a shower|have an early night|"
    r"get an early night|get some sleep|get ready|work|the shops|the shop|town|church|"
    r"make (?:a|some|dinner|lunch|tea|breakfast)|cook|eat|have (?:some )?(?:dinner|lunch|"
    r"breakfast|tea|food)\b|walk the dog|the gym|pick (?:up |the ))")


# A broken night is not a next-thing. "im going to bed but i keep waking up" is about the
# waking, not about going to bed, and the short warm line for going to bed is no answer to it
# (@mauve-pen found it on #1461). The report does not need a "can't": "i keep waking up", "i was
# awake half the night" and "ive been waking up at 4 every night" are all the same complaint.
MY_NIGHT = re.compile(
    r"\b(?:keep|keeps|kept) waking\b"
    r"|\bwak(?:e|es|ing) up (?:at|in the|every|most|half)\b"
    r"|\bwoke up (?:at|in the)\b"
    r"|\b(?:awake|lying awake|lay awake|up) (?:all|half|most of) the night\b"
    r"|\bno (?:night's )?sleep\b|\bbroken night\b")


# Someone else's night is not the person's: "the baby keeps waking up" and "my wife was awake
# all night" keep whatever answers them now.
NOT_MY_NIGHT = re.compile(
    r"\b(?:my|our|the|his|her|their)\s+(?:\w+\s+){0,2}"
    r"(?:baby|son|daughter|kid|kids|child|children|wife|husband|partner|mum|mom|mother|dad|"
    r"father|dog|cat|puppy|kitten|neighbou?r)s?\b"
    r"|\b(?:he|she|they)\s+(?:keeps?|kept|was|were|is|are)\b")


# "i need to sort the boiler" is a plan; "do i need a cable for that" is a question with the
# same words in it, so this one is anchored to the person at the start of the line.
# "i need a boxset for a rainy weekend" is a request for a thing, not an undertaking: the thing
# wanted is followed by what it is for, so it is left to the module that knows the subject
# (@swift-goat's find on #761; it is the same line shape here).
NEED_FOR = re.compile(r"^(?:ok |okay |so |and |but |also )?(?:i|we) (?:still )?need (?:a|an|some)\b"
                      r".*\bfor\b")


NEED_RE = re.compile(r"^(?:ok |okay |so |and |but |also )?(?:i|we) (?:still )?need (?:to|a|an|some)\b")


QUESTION_STARTERS = frozenset("""
do does did can could should would will shall is are was were am have has had how what which
where when why who whom whose any anyone anybody anything if whether ever
""".split())


DOUBT = re.compile(r"\b(?:dont|do not|didnt) know\b|\bno idea\b|\bwhether\b|"
                   r"\bif (?:i|we) (?:should|want|stay|go|leave|quit)\b|"
                   r"\bnot (?:sure|decided)\b|\b(?:unsure|undecided)\b")


# A plan with a condition on it — "i want to hand in my notice without burning bridges",
# "i want to save up so that i can move out" — is asking how, and the knowledge base has the how
# in its own words, so the bare announcement reading gives way to it.
INTENT_CONDITION = re.compile(r"\b(?:without|so that|instead of|as long as|rather than)\b")


EVENT_RE = re.compile(r"\b(?:i have|ive got|i got|im having|i am having|we have|weve got|theres)\b"
                      r"(?!.*\?)\b.*\b(?:tomorrow|tonight|this morning|this afternoon|"
                      r"this evening|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
                      r"next week|next month|next year|this week|this weekend|in a few days|"
                      r"in a couple of (?:days|weeks))\b")


INTENT_STOP = {"sick", "ill", "late", "hurt", "broke", "broken", "lost", "missed", "forgot",
               "forgotten", "left", "cancel", "cancelled", "worried", "worry", "scared",
               "anxious", "failed", "fail", "fired", "sacked", "debt", "owe", "arguing",
               "crying", "upset", "angry", "worse", "pain", "bleeding", "pregnant", "doctor",
               "hospital", "police", "accident", "die", "dying", "died", "funeral", "help",
               "advice", "recipe", "how", "which", "what", "should", "worth", "better",
               "job", "jobs", "cv", "search", "tip", "tips", "recommend", "recommendations",
               "suggest", "suggestions",
               # A plan said with a feeling attached is not a plan: "i started working from
               # home and i hate it" got "Worth doing. What would you like help with first?"
               # because "i started" is an intention. What they said is how they feel about it.
               "hate", "hates", "hating", "miserable", "dread", "dreading", "awful",
               "terrible", "horrible", "lonely", "isolated", "bored", "pointless", "stuck",
               "struggling", "exhausted", "drained", "resent"}


# The words after the marker are the thing they want to do, and that is what tells a plan from a
# feeling: "i want to start running" is a plan, "i want to cry" is not one at all, and "Worth
# doing. Where are you with it so far?" is a callous reply to the second kind.
WANTED = re.compile(r"\b(?:want|wanna|going|planning|thinking of|thinking about|trying|hoping|"
                    r"decided|plan|looking|training|saving|learning|working on|preparing|"
                    r"getting ready|meaning|started|start)\b\s+(?:to\s+|on\s+|about\s+)?(.{0,40})")


# A wish to stop a feeling is about the feeling, not a project to start: "i just want to stop
# feeling like this", "i want to not feel tired all the time", "i want to feel normal again". The
# thing starts with a word about how they feel rather than naming anything to do, and the plan
# reply ("start with the smallest version of it") is no answer to it.
FEELING_WANT = re.compile(
    r"^(?:to\s+)?(?:stop|not|never)\s+(?:\w+\s+)?(?:feeling|feel|being|hurting|crying|"
    r"worrying|like)\b|\b(?:feel|feeling)\s+(?:like|this|that|so|normal|better|good)\b")


FEELING_THING = frozenset("""
cry crying weep weeping sob sobbing scream screaming shout shouting yell yelling disappear
disappearing vanish hide hiding hurt hurting give
""".split())


# "i want to leave my husband" names a relationship, not a thing to get on with; a job, a flat or
# a club is a thing to leave, so those stay a plan.
LEAVE_SOMEONE = re.compile(r"^(?:leave|leaving|left|end|ending|break up with|divorce|divorcing|"
                           r"walk out on)\b.{0,24}\b(?:him|her|them|husband|wife|partner|"
                           r"boyfriend|girlfriend|marriage|relationship|us)\b")


# "<somebody or something> to stop": "i want it to stop", "i just want this to end", "i want the
# pain to stop", "i want these comments to stop". What the person wants is a state to change, not
# a thing to start or to pick a kind of, and the pools below can only hand the capture back as a
# label: "i want it to stop" was answered "It to stop \u2014 fair enough. What's stopped it
# happening so far?", which drops the speaker, leaves a bare verb phrase as the subject, and asks
# someone worn out by something to say what is holding their own wish up. The subject decides
# which half of the reading applies: a pronoun names nothing at all, so there is no thing here to
# be on with and the person's own state is the turn; a noun names the thing that is wrong, and
# the module that answers that thing (the pain, the noise, the comments) should have it.
STOPS_TOGETHER = re.compile(
    r"^(?P<subject>it\s+all|all\s+of\s+it|it|this|that|these|those|things|everything|nothing"
    r"|the\s+lot|life"
    r"|(?:the|my|your|his|her|their|our|this|that|these|those|all|any)\s+[a-z][a-z'-]*"
    r"(?:\s+[a-z][a-z'-]*)?)"
    r"\s+to\s+(?:stop|end|go\s+away|be\s+over|be\s+done\s+with|be\s+different|change"
    r"|get\s+better|settle|sort\s+itself\s+out|go\s+back\s+to\s+normal)\b")


# The subjects above that name nothing to act on.
SAYS_NOTHING = frozenset(("it", "it all", "all of it", "this", "that", "these", "those", "things",
                          "everything", "nothing", "the lot", "life"))


# "How ready do you feel for it?" fits an appointment, an interview, a viewing. Nothing is being
# assessed on a long drive or a night with no sleep, so those keep their own reading.
EVENT_OUTING = re.compile(r"\b(?:drive|journey|trip|flight|train|coach|ferry|commute|shift|"
                          r"night out|dinner|party|meal|shopping|sleepover)\b")


EVENT_TIRED = re.compile(r"\b(?:cant|cannot|knackered|exhausted|tired|sleep|sleeping|"
                         r"insomnia|awake)\b")


# The same goes for a state "had" at a time: "ive got a fever tonite", "i have a headache this
# afternoon" and "i have no money till friday" all name the body or the wallet, not an
# appointment, and were asked how ready they felt for it. A symptom word, or a wallet said to be
# empty, makes the have-line a state, so the reading that answers a person's own trouble takes it.
# Only a complaint is listed here: "sore" alone is a sore point, and "nothing on" is a free
# evening, and both keep the reading they had.
EVENT_STATE = re.compile(r"\b(?:fever|temperature|headache|headaches|migraine|migranes|"
                         r"toothache|earache|stomach ache|sore throat|cough|rash|infection|"
                         r"pain|ache|aching|hurts|hurting|nausea|nauseous|dizzy|swollen|"
                         r"symptoms?|skint|no money|broke)\b")


def _a_trip(flat, memory):
    """Whether the line names a place and leaves for it: the place answers, not a plan line.

    The memory store has already read the place out of this line, so a word list here would only
    duplicate its reading. A plan that names no place ("i might go for a walk later") keeps its
    plan reply.
    """
    if ack.reads_as_a_trip(flat):
        # A wedding, a gig or a week away is a day out rather than a project with a first step,
        # and the memory store answers those with the trip itself (bot/memory/ack.py).
        return True
    user = memory.get("user") if isinstance(memory, dict) else None
    places = user.get("places") if isinstance(user, dict) else None
    return bool(places) and bool(GO_AWAY.search(flat))


def _answers_it(text, understood, memory):
    """True when the knowledge base's own entry for this plan line will answer it.

    An entry that fits the words can still turn the line down because the conversation says it
    is about something else, and then its reply is empty - the same test `answers._offer` makes.
    `find` hands back `city-next` for "i want to eat less sugar" (on "eat" and "i") and that
    entry declines (no city was named), so standing aside for it left the line with a bare ack.
    """
    from ..knowledge.lookup import find
    from ..modules import answers
    try:
        found = find(understood)
        if found is not None:
            reply = answers._payload(found, memory, understood)
            if isinstance(reply, str) and reply.strip():
                return True
        # The top entry declining does not mean the knowledge base has nothing: `answers` walks on
        # to the entry the follow-up is about, so a plan line inside a conversation has to ask the
        # same reader before it takes the turn. The walk only runs when the words alone found
        # nothing that answers, so a plain plan line costs one lookup.
        item, reply = answers._offer(
            lambda reject: answers._in_context(text, memory, reject=reject), memory, understood)
    except Exception:
        return True  # a reader that cannot be asked is not a reason to take the turn from it
    return bool(item is not None and isinstance(reply, str) and reply.strip())


def _as_typed(flat, memory):
    """The line as the person typed it, joining words and all.

    Chat reads a line a second time with the words normalised, and that reading drops a word
    that turns it ("work has been manic but i got a promotion"). A guard about whether the load
    is the whole of the line has to see the word that turned it, so it reads the words the
    understanding engine kept of what was said.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    words = understood.get("words") if isinstance(understood, dict) else None
    if isinstance(words, list) and words and all(isinstance(w, str) and w for w in words):
        return " ".join(words)
    return flat


# A word that points back at the thing the chat is on, in a line that is a detail on it.
_ON_THE_JOB = re.compile(r"\b(?:it|its|it's|that|that's|this|them|they|those|these)\b", re.I)


# The words that make a line about the run of the person's week rather than about the job.
_THE_RUN_OF_IT = re.compile(r"\b(?:work|works|job|shift|shifts|week|weeks|weekend|month|day|days|"
                            r"term|year|life|things|everything|staffing|rota|hours)\b", re.I)


def _a_detail_on_the_job(flat, memory):
    """Whether the line adds a detail to a job the knowledge base is already answering.

    "my kitchen tap is dripping and it wont stop" is answered with the washer and the isolating
    valve; "i tried turning it really hard and now its worse lol" is that same tap. Read as the
    strain of the person's week it matched OVERLOAD on "it ... hard" and got "a run like that
    wears you down - pick the one thing you can drop", which is about them and not about the tap.
    A hard thing in the line is the job being hard, not the week: the run of it is what OVERLOAD
    is for, and it needs a word for the run ("this week", "at the moment", "everything").
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not turns or not isinstance(turns[-1], dict) or turns[-1].get("module") != "answers":
        return False
    understood = memory.get("understood") if isinstance(memory, dict) else None
    leans = understood.get("leans_on") if isinstance(understood, dict) else None
    if not isinstance(leans, dict) or not str(leans.get("text") or "").strip():
        return False
    if not _ON_THE_JOB.search(flat):
        return False
    # A pronoun is the only thing the load can point at; a week or a shift named in the line is
    # the person's week, whatever else the chat is on.
    return not _THE_RUN_OF_IT.search(flat)


# A figure with a period is a price, and the judgement after it is the question about that
# price. "its 45 a month, is that a lot" matched OVERLOAD's first alternative on "month ... a
# lot" and was answered "a run like that wears you down before you notice. Pick the one thing
# you can drop this week" - advice about a strain nobody mentioned, to somebody asking whether
# forty-five pounds a month was dear. The two readings share the word "lot" and nothing else.
# Only money stands the reading down ("5 miles a day" is a rate and can be a load), and only
# with a judgement on it, so "45 a month for the gym and i cant keep up" still keeps the run.
A_RATE_OF_MONEY = re.compile(
    r"(?:[£$€]\s*\d[\d,.]*|\b\d[\d,.]*\s*(?:pounds?|quid|euros?|dollars?|grand|k)?)\s*"
    r"(?:a|an|per|each|every)\s+(?:month|week|year|day|fortnight)\b", re.I)


A_JUDGEMENT_ON_A_FIGURE = re.compile(
    r"\b(?:is|isnt|isn'?t|was|wasnt|wasn'?t)\s+(?:that|this|it)\s+(?:about\s+|really\s+|"
    r"actually\s+)?(?:a lot|too much|too dear|expensive|cheap|good value|worth it|about right|"
    r"normal|fair|steep|reasonable|pricey|dear)\b", re.I)


def _overloaded(flat, memory):
    """The run of things, when it is all the line says and it asks for nothing."""
    if not OVERLOAD.search(flat):
        return False
    if A_RATE_OF_MONEY.search(flat) and A_JUDGEMENT_ON_A_FIGURE.search(flat):
        return False
    said = _as_typed(flat, memory)
    if LOAD_ASK.search(said) or LOAD_TURNED.search(said) or LOAD_SOMEONE_ELSE.search(said):
        return False
    if _a_detail_on_the_job(flat, memory):
        return False
    return not LOAD_FEELS.search(said)


# A judgement asked about the thing in the thread rather than named: "is that a good idea",
# "would that work", "is it worth it". The thing itself is in the line before, and the pools they
# used to land on ("good luck with it", "Fair enough.") answer nothing that was asked.
JUDGED = re.compile(
    r"^(?:and |so |but |ok |okay |well )*(?:is|was|would|will|could) "
    r"(?:that|this|it) (?:really |actually |even )?"
    r"(?:a (?:good|bad|daft|silly|smart|sensible|wise|right|wrong|clever) "
    r"(?:thing|idea|move|call|plan|choice|buy|option)(?: to do)?|"
    r"the (?:right|wrong|sensible|wise|smart) (?:thing|move|call|choice)(?: to do)?|"
    r"worth it|worth (?:doing|getting|a go|trying)|sensible|wise|a mistake|a waste of money|"
    r"going to work|work|going to help|going to be (?:ok|okay|fine))"
    r"(?: then| though| do you think| in your opinion| or not| to do)?\??$")


# The words that say they are thinking about the thing rather than naming it. Taken off the topic
# so the reply can name the thing in the words it was said in: "im thinking of getting a cat" is
# about "getting a cat", and "im considering moving to leeds" about "moving to leeds".
_CONSIDERING = re.compile(
    r"^(?:(?:ok|okay|so|well|and|and also)[\s,]+)?"
    r"(?:(?:i'?m|im|i am|we'?re|we are|i'?ve|i have|i|we)\s+)?(?:been\s+|still\s+|also\s+)?"
    r"(?:thinking (?:of|about)|considering|looking (?:at|into|for|round at)|weighing up|"
    r"toying with|fancy(?:ing)?|after|into)(?:\s+|$)")


# The same said with "to": "i want to learn the guitar" is about learning the guitar, so the verb
# after the "to" is put in the -ing form the rest of the sentence uses.
# "off to bed" and "out to the shops" are the same movement as "going to", and they used to be
# said back whole: "Whether im off to bed soon is the right move" is the person's own sentence
# inside the bot's, subject and all.
_CONSIDERING_TO = re.compile(
    r"^(?:(?:ok|okay|so|well|and|and also)[\s,]+)?"
    r"(?:(?:i'?m|im|i am|we'?re|we are|i'?ve|i have|i|we)\s+)?(?:been\s+|still\s+|also\s+)?"
    r"(?:thinking (?:of|about) going to|planning to|thinking to|hoping to|want(?:ing)? to|"
    r"wanted to|'?d like to|would like to|keen to|tempted to|trying to|going to|gonna|off to|"
    r"out to|away to|heading to|about to)(?:\s+|$)")


def _judged(clean, memory):
    """The honest answer to "is that a good idea", naming the thing in the thread, or None.

    "is that a good idea" after "im thinking of getting a cat" is not an acknowledgement and not
    a fact to look up: it is the person asking the bot to call a decision that is theirs. The
    line said what the thing is, so it is said back ("Whether getting a cat is the right move is
    yours to weigh") rather than answered with a line that would fit any message at all.
    """
    if not JUDGED.match(clean):
        return None
    # The composer can rule on the plan the person has just put down, and a verdict answers the
    # question this hand-back only declines ("I cannot call that one for you"). So the hand-back
    # stands down where the composer has a verdict for the same line, and keeps the lines the
    # composer will not weigh: a plan to harm someone, a wish, a body, a bare "is that bad".
    # "im thinking of getting a cat" / "is that a good idea" was the hand-back against
    # "Yes, it makes sense - getting a cat is a reasonable thing to aim at."
    try:
        if fallback.a_verdict_on_their_plan(clean, memory):
            return None
    except Exception:
        pass
    thing = _judged_thing(clean, memory)
    if thing:
        options = [option.format(thing=thing, Thing=thing[:1].upper() + thing[1:])
                   for option in NEWS_REPLIES["judged"]]
    else:
        options = list(NEWS_REPLIES["judged_bare"])
    return pick(options, memory, clean)


# A phrase with a verb of its own in it is a statement about something, not the thing being
# weighed: "my boiler is 20 years old" would be said back as "Whether my boiler is 20 years old is
# a good idea". Only a thing, or a thing being done, can go in that sentence.
_STATEMENT = re.compile(
    r"\b(?:is|are|was|were|am|has|have|had|do|does|did|will|would|can|could|should|shall|"
    r"might|must|i|we|you|he|she|they|that|this)\b"
    # The contracted ones are how people type a subject: "im off to bed soon" said back as the
    # thing read "Whether im off to bed soon is the right move is yours to weigh".
    r"|\b(?:im|i'?m|ive|i'?ve|we'?re|hes|he'?s|shes|she'?s|they'?re|dont|doesnt|didnt|"
    r"can'?t|wont|isnt|aren'?t|wasnt|wouldnt|couldnt)\b")


# A plan typed as the doing of it: "im leaving my job", "we're buying a house". Only an -ing
# word starts it, because a state is not a plan ("im shattered", "im not sure about the cat") and
# a state is not a thing to weigh.
_BARE_DOING = re.compile(
    r"^(?:i'?m|im|i am|we'?re|we are)\s+(?P<doing>[a-z]{3,}ing)\b(?P<rest>.*)$")


def _judged_thing(clean, memory):
    """The thing the thread is about, in the words it was said in: "getting a cat", "a second baby".

    The line itself is never the thing: the store has already noted this line as the topic, so
    read back it would answer "is that a good idea" with "is that a good idea is your call"."""
    record = current(memory)
    said = " ".join(str(record.get("text") or "").split()) if isinstance(record, dict) else ""
    said = said.strip(" .!?,")
    if not said or said.lower() == clean.lower():
        return ""
    to_form = bool(_CONSIDERING_TO.match(said))
    said = _CONSIDERING_TO.sub("", said) if to_form else _CONSIDERING.sub("", said)
    if to_form:
        # "to learn spanish" is a step and "to the gym" is a place, and a place folded into an
        # -ing word is not English: "going to the gym" said back was "Theing gym". The composer's
        # reading knows which is which, so the phrase is said back the way it fits a sentence.
        said = stepwords.said_after_a_to(said)
    doing = _BARE_DOING.match(said)
    if doing:
        # A plan typed as the doing of it: "im leaving my job", "we're moving to leeds". There is
        # no considering phrase for the strips above to take, and the pronoun and the tense are
        # the telling rather than the thing weighed, so the doing is what the reply names. It is
        # already an -ing phrase, so nothing is folded: "leaving my job" goes back as it stands
        # (able-paper, #routing 179). Without this the line's own "im" was read as the statement
        # a thing cannot be, and "is that a good idea" was answered "Tell me what matters most"
        # with the job gone out of it.
        said = (doing.group("doing") + doing.group("rest")).strip(" .,!?:;")
    # A time or a place after a comma is not the thing: "im thinking of a new kitchen, maybe in
    # the spring" is about the kitchen.
    said = re.split(r"[,;]|\b(?:because|but|so|though|although)\b", said)[0].strip(" .,!?:;")
    words = said.split()
    if not 2 <= len(words) <= 6 or _STATEMENT.search(said):
        return ""
    return said


# A line that is only the news that it happened once more: "again", "not again", "oh no not
# again". The word is the whole reading, so it is read only when nothing else is in the line.
AGAIN_ONLY = frozenset("again not oh no and over yet it on this time really".split())


# The words that make an "again" the bad kind on their own.
NOT_AGAIN = frozenset("not no oh".split())


# A how-to asked and answered, which is what makes a bare "again" a request for the steps back
# rather than the news that it happened once more.
HOW_TO_ASKED = re.compile(r"\bhow (?:do|can|should|would|could) (?:i|you|we)\b|\bhow to\b",
                          re.IGNORECASE)


# Said before the answer handed back, so a person who asked for it hears that the bot knows it is
# the same answer and not a new one.
THE_STEPS_AGAIN = ("Again — ", "Here it is again: ", "Same as before: ")


# The whole line looking forward to something. "can't wait" is read as an idiom by the
# understanding engine (so "i can't wait to get to sleep" is not an inability), and the short
# line that follows a plan is the person saying they are glad about it.
LOOKING_FORWARD = frozenset((
    "cant wait", "cannot wait", "cant wait for it", "cant wait to go", "cant wait for this",
    "looking forward to it", "looking forward to that", "so excited", "im so excited",
    "really excited", "counting down", "cant wait now",
))


def _the_steps_again(memory):
    """The answer just given, said again, for a bare "again" after a how-to.

    "how do i bleed a radiator" / "again" is the person asking for the steps back: the answer is
    on their screen a moment ago and the word is the whole request. Handing them the news pool's
    "Again — that's hard going." read the repeat ask as a bad week, which is worse than the flat
    nod it replaced, because it reads as not having listened at all.
    """
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return None
    last = turns[-1]
    asked = str(last.get("user") or "")
    answer = str(last.get("bot") or "").strip()
    # A nod is not an answer: after "how do i descale the kettle" / "ok" a "again" is not the
    # steps, and handing back "Sounds good." would be handing back nothing.
    if not HOW_TO_ASKED.search(asked) or len(answer.split()) < 8:
        return None
    return pick(THE_STEPS_AGAIN, memory) + answer


def _a_care_turn(memory):
    """True when the turn before this one was care, so a glad line is the wrong timing in it.

    "my mum is in hospital" / "cant wait" is not a person looking forward to something: the
    answer before it was the ward and the questions to ask, and cheering over that is the bot
    reading the wrong thread. The hospital is said in the person's own line, and the loss modules
    say it in their own name, so both are checked.
    """
    last = _last_said(memory)
    if last and any(pattern.search(last.lower()) for _, pattern in SOMEONE_TROUBLE):
        return True
    return fallback._in_a_care_thread(memory)


def _a_forecast(memory):
    """True when the line the pools are reading is a question about the weather.

    "is it gonna rain" is a forecast, not a plan: the "going to" in it is the ordinary future,
    and the plan pool answered it "Nice. Tell me how it goes." - a well-wish for a trip nobody
    described - while the weather line ("I can't check the forecast from here, sorry") sat one
    candidate below it, at the fallback's priority. The reading already says the line is about
    the weather and is a question (`bot/understanding/`: `topic` and `kind`), so the plan pool
    stands down and the line is answered as the weather question it is. A line that says what
    the weather will do without asking ("gonna rain later i think") is a statement and keeps
    the answer it had.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    if str(understood.get("topic") or "") != "nature-and-weather":
        return False
    return str(understood.get("kind") or "") == "question"


# The pools that comfort and ask rather than advise, so a step asked for after one of them is
# the person taking up the offer rather than a repeat of advice already given: the shared
# helper in bot/compose/ gives the first step of a bad day when it sees one of these lines.
FEELING_POOLS = ("sad", "tired", "stressed", "ill", "anxious", "worry", "worry_person",
                 "missing", "guilty", "lonely", "rough_day", "stuck", "not_coping",
                 "bad_day", "venting")


# Bad news is not on that list, though it looks like it should be: the lost-job and bad-news
# lines all give an instruction of their own ("get the reason and the pay in writing", "ask for
# feedback if you can"), so a step of a bad day is not the follow-on - "i lost my job today"
# then "what should i do" was answered "something to eat, a shower, ten minutes outside", which
# is the wrong first thing after a job. The ask after bad news belongs to the news.
#
# The two that carry no instruction are on it: every not_coping and bad_day line ends on a
# question about the person's own day, so "im falling apart" then "what do i do" has nothing of
# its own to hand on - and what the person got instead was the question-back line, "Nothing to
# do on my side, honestly - whatever comes to mind about it first is the useful bit", said to
# somebody who had just said they were falling apart. The smallest step of a bad day is the
# follow-on, exactly as it is after the sad pool.
FEELING_SAID = frozenset(
    [text for name in FEELING_POOLS for text in REPLIES[name] if isinstance(text, str)])


def _tokens(text):
    text = text.lower().replace("’", "'")
    for smile, word in SMILES.items():
        text = text.replace(smile, word)
    text = text.replace("'", "")
    return [t for t in TOKEN.findall(text) if t]


def _name(memory):
    facts = memory.get("user")
    if isinstance(facts, dict):
        name = facts.get("name")
        if isinstance(name, str) and name:
            return name[:1].upper() + name[1:]
    return None


def _the_lost_thread_asked(memory, kind):
    """Note that the lost-thread question was asked, for the turn after it.

    Written where the reply is chosen, so it lands in this module's copy of the memory and only
    survives when this module's reply is the one the person got (see _the_weight_said).
    """
    if kind != "confused" or not isinstance(memory, dict):
        return
    turns = memory.get("turns")
    memory["lost_thread"] = {"turn": len(turns) if isinstance(turns, list) else 0}


# Two pool lines ask about the person's life rather than answering them, so they need the person
# to have said what it is: "anything nice planned to go with it?" is a good reply to "i'm excited
# for the weekend" and a nonsense one to "i'm proud of myself", and "nerves before something big"
# invents a date the person never mentioned ("i feel a bit anxious"). Everything else in those
# pools reads as a reply whatever the line says, so this is the shortest list that can be wrong.
AHEAD = re.compile(
    r"\b(?:tomorrow|tonight|this (?:weekend|evening|afternoon|morning|week|month)"
    r"|next (?:week|month|weekend|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"|weekend|holiday|holidays|trip|away|party|wedding|birthday|christmas|new year|exam|exams"
    r"|test|interview|results?|match|game|flight|moving|graduation|show|gig|appointment"
    r"|driving test|scan|check-?up|first day|performance|audition|presentation)\b", re.I)


NEEDS_AHEAD = (
    "Love that. Anything nice planned to go with it?",
    "Nerves before something big are normal. Slow breaths for a minute genuinely help.",
)


# Being pleased with yourself is not the same as having good news, and it has no plan in it.
# A line that rules the pride out ("im not proud of what i did", "nothing to be proud of") is the
# other way round: it is regret, and being told "and so you should be" would be the bot
# congratulating someone for the thing they feel bad about.
NOT_PROUD = re.compile(r"\b(?:not|never|hardly|nothing|no)\b[^.?!]{0,20}?\bproud\b", re.I)


PROUD_OF_MYSELF = re.compile(
    r"\b(?:i'?m|im|i am|i\s+feel|feeling|felt|so|really|quite|proper)\b[^.?!]{0,24}?\bproud\b"
    r"|\bproud of (?:myself|what i|that i|how i|it)\b", re.I)


# Pride in someone else is not the person's own doing: "im so proud of you" is praise of the bot
# and "im proud of my daughter" is hers, so "whatever it took, you did that" answers neither.
PROUD_OF_ANOTHER = re.compile(
    r"\bproud of (?:you|u|ya|her|him|them|his|hers|their|my|our|the|this|that)\b", re.I)


# A celebration is the one thing the bot should never do in a thread where someone died. "my mum
# died last night" then "great" got "That's great news! Make the most of it.", and "lol" got "Ha!
# Glad you liked it." - the cheer pools read the ack and none of them read the room. The good
# news is still good news, so these warm to it instead of celebrating in it, and none of them
# pretends the death was not said.
#
# The read is compose/loss's, not a word list: "my phone died", "the battery died on my car" and
# "my house plant died" are jokes and gadget news, and they keep their laugh. "my dog had to be
# put down" is a death, and it gets the same flat warmth as a person's.
CHEER_IN_LOSS = (
    "I'm glad there's something good in the week - it's been a heavy one for you.",
    "Good to hear it. You've had a lot to carry lately.",
    "That's good to hear, and I'm still sorry about your loss.",
    "Glad of that. How are you doing in yourself, with everything else?",
)


# The pools that celebrate, including the laugh, since a laugh in a bereaved thread reads the
# same way as "that's great news!": "lol" after a death is not the bot's joke landing.
CHEER_KINDS = frozenset(("happy", "laugh", "lol", "good_news"))


# "not much" is how a person answers "what are you up to", and it is a noun phrase: the words
# around it are the ones a spoken answer carries ("im", "just", "yeah"), never a verb. "im not
# eating much" and "im not sleeping much" are lines about eating and sleeping, and they were
# answered "Same as ever — helping, chatting. How's your day going?" because the two words
# "not" and "much" appeared in a short line. A verb between them is the line's subject.
_NOTHING_MUCH_FILLER = frozenset("""not much nothing nm nmu notmuch im i m am just yeah yeh yep
    so well oh hi hey hello really like its it is a bit going on happening here there today now
    thanks ta lol though either atm still you u and about what how yourself to say report
    else lately honestly tbh tbf mate m8 bud pal me us hbu wbu innit haha happened""".split())


# The words that may stand between "not" and "much". An adverb says nothing of its own, and so
# does "do": it is the stand-in verb, so "im not doing much" and "havent done much today" are the
# same answer as the bare phrase. Any other word there is the line's subject: "im not eating
# much" is about eating, "im not sleeping much" about sleeping.
_NOTHING_MUCH_BETWEEN = frozenset("""really very so that too even actually quite just
    do did done doing does""".split())
