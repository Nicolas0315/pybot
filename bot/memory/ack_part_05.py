"""Part 5 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from ..compose import loss, negated, pick
from ..compose.badnews import reads_like_a_symptom
from ..understanding import understand as understanding
from ..understanding.kinds import VERBISH
from ..understanding.topics import NUMBER_WORDS
from ..understanding.normalize import LEFT_OFF_CONTRACTION, LEADERS, opens_without_subject
from . import there_is_a_chat
from . import facts, named, topics
from .relations import _person_from_pronoun, _pronoun_fits
from .store_lines import CHILD, PERSON_GROUP
from .ack_part_01 import (
    COMING_TO_STAY, DIARY_TAIL, DIARY_THING, DIARY_TIME, DIARY_TIME_TAIL, MEETING_TAIL,
    MEETING_TIME_TAIL, OCCASIONS, OCCASION_TAIL, VISIT_TAIL_MANY, VISIT_TAIL_ONE,
    _more_than_one_coming, OCCASION_FLAT_TAIL, TRIP_TAIL, SOMEONE_MILESTONE, NOT_A_THING,
    NOT_A_VISIT, SOMEONE_COMING, WORK_PLACE,
)
from .ack_part_02 import (
    DEATH_WORDS, DATE_AHEAD, PAST_PLAN, HOW_LONG_ALREADY, reads_as_a_trip, reads_as_cruelty,
    HEAVY_FRAMES, A_SPAN_OF_TIME, BUYING, FOR_A_THING, MONEY, PERIOD, HEAVY_TURNS, SEPARATION,
)
from .ack_part_03 import (
    GROWING, REMARK_BACK, REMARK_FIGURE, REMARK_FIGURE_REPLIES, REMARK_JUDGES_THE_PRICE,
    REMARK_KINDS, REMARK_PRICE_AHEAD, REMARK_REPLIES, REMARK_TWO_SIDED, _repaired, WORD, _EMPTY,
)
from .ack_part_04 import (
    _a_price_still_to_come, OTHER_PERSON, BACK_AT_IT, GOING_HOME, GOING_HOME_TAIL, ON_THE_MEND,
    ANYBODY_AT_ALL, NOBODY_AROUND, NOBODY_AROUND_ASK, PERSON_WORDS,
)


def _a_remark_on_what_was_said(clean, memory):
    """The reply to a one-line remark about the turn before, or None when the line is not one.

    Only a short line that points back with a pronoun or a "the" and states one of the kinds
    above, and only after someone has said something for it to be about.
    """
    if not isinstance(memory, dict):
        return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return None
    body = clean.strip()
    if len(body.split()) > 9:
        return None
    if not REMARK_BACK.match(body) or "?" in body:
        return None
    if REMARK_TWO_SIDED.search(body):
        return None
    topic_text = str((memory.get("topic") or {}).get("text") or "") if isinstance(
        memory.get("topic"), dict) else ""
    for pattern, kind in REMARK_KINDS:
        if not pattern.search(body):
            continue
        if kind == "gone" and not GROWING.search(body + " " + topic_text):
            continue
        if kind == "expense" and not REMARK_JUDGES_THE_PRICE.search(body):
            # A figure on its own is not a remark about money: "it costs 400" says what the thing
            # costs, and "They never are." answers a complaint the person did not make. A line
            # that is the figure and nothing else is answered as the figure.
            if not REMARK_FIGURE.search(body):
                continue
            return pick(REMARK_FIGURE_REPLIES, memory, seed_text=body)
        options = REMARK_REPLIES[kind]
        if kind == "expense" and _a_price_still_to_come(body, topic_text):
            options = REMARK_PRICE_AHEAD
        if _asked_last(memory):
            options = tuple(one for one in options if not one.endswith("?")) or options
        return pick(options, memory, seed_text=body)
    return None


ON_THE_MEND_TAIL = (
    "Good to hear it. Recovery goes in fits and starts \u2014 a good day, then a flat one, and both "
    "are normal.",
    "That is the direction you want. Better is slower than people expect, and it counts all the "
    "same.",
    "Worth saying out loud. On the mend is the part that takes patience from everyone round them.",
)


BACK_AT_IT_TAIL = (
    "Back at it already is quick going. The first week back is the tiring one for most people.",
    "That is a good sign. Getting back to normal takes longer than people expect, and the first "
    "week of it is the hardest.",
    "Good news. Back to it \u2014 and the first week is the one to take gently.",
)


GOING_HOME_MINE = (
    "Out {soon} \u2014 good. The first days at home are the flat ones, so keep them quiet and let "
    "people bring things.",
    "That is a relief to hear. Home is where the sleep happens; the ward is not.",
)


ON_THE_MEND_MINE = (
    "Good to hear. Recovery goes in fits and starts \u2014 a good day, then a flat one, and both are "
    "normal.",
    "That is the direction you want. Better is slower than people expect, and it counts all the "
    "same.",
    "Worth saying out loud. Take the good days as they come rather than testing them.",
)


BACK_AT_IT_MINE = (
    "Back at it already is quick going. The first week back is the tiring one for most people.",
    "Good sign. Getting back to normal takes longer than people expect, so keep the first week "
    "light.",
    "Good news. Back to it \u2014 and the first week is the one to take gently.",
)


A_RELATION = frozenset("""mum mom mother dad father nan nanna granny gran grandma grandad grandpa
    son daughter kid child baby sister brother mate friend partner wife husband aunt uncle cousin
    niece nephew colleague boss neighbour neighbor lodger flatmate housemate""".split())


def _who_is_getting_better(low):
    """"them" for somebody else in the line, "me" for the speaker, "" for nobody."""
    words = set(re.findall(r"[a-z']+", low))
    if words & (OTHER_PERSON | A_RELATION):
        return "them"
    if words & frozenset(("i", "im", "ive", "me", "my", "myself")):
        return "me"
    return ""


def a_person_getting_better(clean, memory=None):
    """The pool for news that somebody is getting well, or None."""
    plain = str(clean or "").replace("\u2019", "'").replace("\u2018", "'")
    low = plain.lower()
    if not low.strip() or DEATH_WORDS.search(low):
        return None
    if not _who_is_getting_better(low):
        return None
    said = " ".join([low] + _the_words_of_the_last_two_turns(memory))
    if not re.search(r"\b(?:ill|sick|hospital|operation|op|surgery|broke|broken|stroke|chemo"
                     r"|treatment|injury|injured|fell|fall|accident|recovering|recovery|bug"
                     r"|flu|pneumonia|infection)\b", said):
        # Nothing in the chat says there was anything to get better from, so "shes better now"
        # is a line about something else entirely.
        return None
    mine = _who_is_getting_better(low) == "me"
    for pattern, theirs, ours in ((GOING_HOME, GOING_HOME_TAIL, GOING_HOME_MINE),
                                  (ON_THE_MEND, ON_THE_MEND_TAIL, ON_THE_MEND_MINE),
                                  (BACK_AT_IT, BACK_AT_IT_TAIL, BACK_AT_IT_MINE)):
        match = pattern.search(low)
        if match and not negated(low, match.group(0)):
            return _with_the_time(ours if mine else theirs, low)
    return None


def _the_words_of_the_last_two_turns(memory):
    """The person's own lines from the last two turns, lowercased, oldest first."""
    words = []
    for turn in (memory or {}).get("turns") or []:
        if isinstance(turn, dict):
            words.append(str(turn.get("user") or "").lower())
        elif isinstance(turn, str):
            words.append(turn.lower())
    return words[-2:]


def _with_the_time(pool, low):
    """The pool with the time the line gave in it ("out next week" -> "out next week")."""
    match = re.search(r"\b(next week|this week|tomorrow|soon|on (?:monday|tuesday|wednesday"
                      r"|thursday|friday|saturday|sunday)|in a (?:few|couple of) days"
                      r"|by the weekend)\b", low)
    when = match.group(1) if match else "soon"
    return tuple(line.replace("{soon}", when) for line in pool)


# A move is the commonest cause and the one the person usually names, so it is answered as the
# move rather than as a stranger in a town with no history to it.
A_MOVE = re.compile(r"\b(?:moved|moving|move|relocat|emigrat|new (?:city|town|area|job|country))",
                    re.I)


# Two pools, because a line that names a move is answered about the move: the first months are the
# part nobody warns you about, and that is worth saying to someone in them.
ALONE_AFTER_A_MOVE = (
    "The first months somewhere new are the emptiest part of a move, and it does ease off. "
    "Whatever meets weekly near you - a class, a club, a five-a-side - fills it faster than "
    "waiting to be asked.",
    "That's the hard part of moving, and nobody warns you how long it lasts. One thing you turn "
    "up to at the same time every week is how the same faces start.",
    "Being new somewhere is lonely in a way that has nothing to do with how likeable you are. "
    "Say yes to the first small invitation that comes, even the boring one.",
)


ALONE_TAIL = (
    "That's a lonely way to spend the week, and it isn't a fault in you. One message to someone "
    "you already like does more than waiting for a night out.",
    "That's a quiet way to live. The people who get to know you are the ones you see at the same "
    "time each week, so it is worth having one of those.",
    "That's hard going. Being on your own in a place with no history to it wears thin, and the "
    "way out is nearly always the same small step: one regular thing, one person you keep saying "
    "hello to.",
)


# After a death the empty week is the grief itself, and the move pool's "fill it with something
# weekly" is far too brisk for it: this is the one thing worth saying to someone in that week.
ALONE_AFTER_A_LOSS = (
    "That's the hardest part of it, the empty week afterwards. The people who knew them are "
    "usually the ones who most want to hear from you.",
    "Being on your own after something like that is a weight of its own, and it is not something "
    "to push through. A short call to someone who knew them helps more than you'd think.",
)


def nobody_around(clean, memory):
    """The pool for a line that says, as a fact, that they have nobody, or None."""
    # The line as typed carries curly apostrophes ("don’t"), and the patterns are written the
    # plain way, so they are folded here rather than in every one of them.
    plain = str(clean or "").replace("\u2019", "'").replace("\u2018", "'")
    hit = NOBODY_AROUND.search(plain)
    if not hit or NOBODY_AROUND_ASK.search(plain) or ANYBODY_AT_ALL.search(plain):
        return None
    # A line about somebody else's empty week is not this line: "hes got no one to talk to at
    # work" wants something said about him, and the reply for the speaker would be a stranger's
    # comfort handed to the wrong person.
    if set(plain[:hit.start()].split()) & OTHER_PERSON:
        return None
    if negated(plain, hit.group(0)[:12]):
        return None  # "i dont not know anyone" - a doubled denial is not this line
    said = " ".join([plain] + [str(one or "") for one in (memory.get("turns") or [])[-2:]])
    if DEATH_WORDS.search(said):
        return ALONE_AFTER_A_LOSS
    return ALONE_AFTER_A_MOVE if A_MOVE.search(said) else ALONE_TAIL


_WORDS = re.compile(r"[a-z']+")


# A line said to the bot rather than about the person: "youre on form today", "youre off your
# game today", "you seem cheerful". The store took the second person for the first and filed it
# ("you're on form today" came back "Noted: you're on form today."), which hands somebody their
# own words with the wrong subject on them, and it kept the turn from the readers that answer
# lines aimed at the bot (bot/memory/warmth.py). Only a line that opens on the bot counts, and
# only when nothing in it is the person's own: "you were right, i do need to book it" is about
# them as well, and "my" makes it their life being talked about ("youre so patient with my mum").
_THE_BOT_AS_SUBJECT = re.compile(
    r"^\s*(?:(?:oh|aw+|ah|ha+|tbh|honestly|ok|okay|well|and|but|so|yeah)[,\s]+)*"
    r"you(?:'?re| are| were| seem| look| sound| make| keep| always| really| definitely)\b",
    re.I)


_SOMEONE_ELSE_IN_IT = re.compile(r"\b(?:i|im|i'm|i've|ive|i'd|we|we're|our|my|mine)\b", re.I)


def _said_to_the_bot(clean):
    """Whether the line opens on the bot and has nothing of the person's life in it."""
    if not _THE_BOT_AS_SUBJECT.match(clean or ""):
        return False
    return not _SOMEONE_ELSE_IN_IT.search(clean or "")


def _no_subject(clean, memory=None):
    """Whether the line opens with a helper and nothing that can be a subject: "was out all day".

    Saying the thing back needs somebody in it. People leave the subject off a short line
    ("am shattered", "was out all day", "have no idea"), and handing it back as it stands - "Got
    it - were shattered after the move" - reads worse than the stock line it replaced. The
    understanding engine already knows the shape (it puts the "i" back for its own reading),
    so this asks it instead of listing the helpers a second time.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict) and understood.get("dropped_subject"):
        return True                  # "am thinkin of jackin in me job": the "i" is the bot's
    words = [word for word in _WORDS.findall(_repaired(clean, memory).lower()) if word]
    while words and words[0] in LEADERS:
        words = words[1:]
    return bool(words) and opens_without_subject(words, 0)


def _asked_last(memory):
    """Whether the bot's last reply ended on a question, so this one must not ask another."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    last = turns[-1] if isinstance(turns[-1], dict) else {}
    return str(last.get("bot") or "").strip().endswith("?")


def _a_diary_plan(found, clean):
    """The endings an appointment or a visit wants, or None when the plan is something else.

    A plan that names a day and nothing else is either a thing in the diary - the dentist, a scan,
    an interview, a haircut - or one of their people coming to stay. Both were filed and handed
    back ("Noted: the dentist is on tuesday.", "Noted: your mum's coming on friday."), which tells
    the person nothing about the thing they have just put in their week. What is still open is the
    time, or how long the visit lasts, so that is what the ending asks. A plan with no day in the
    line ("i want to save for a house") is a project and keeps the reply it has.
    """
    if not isinstance(found, dict) or not found.get("plan"):
        return None
    said = " ".join(str(clean or "").lower().split())
    if not said or not DATE_AHEAD.search(said):
        return None
    if set(re.findall(r"[a-z']+", said)) & PAST_PLAN:
        return None
    who = None
    named = re.search(r"\b(?:my|our)\s+([a-z]+)", said)
    if named:
        # "my mums coming" and "my sister's coming" name the same person as "my mum" does, so the
        # possessive and the plural come off before the word is looked up in the relations.
        word = named.group(1)
        person = next((one for one in (word, re.sub(r"'s$", "", word), word[:-1])
                       if one in facts.RELATIONS), "")
        # Coming home is not a visit: the person is not staying with them, they live there.
        at_home = re.search(r"\b(?:coming|heading|getting|moving|flying) (?:back )?home\b", said)
        if person in facts.RELATIONS and COMING_TO_STAY.search(said) and not at_home:
            who = ("they" if _more_than_one_coming(said, named.end(), word) else
                   "she" if person in facts.SHE and person not in facts.HE else
                   "he" if person in facts.HE and person not in facts.SHE else "they")
    if who == "they":
        return VISIT_TAIL_MANY
    if who:
        return tuple(one.replace("{who}", who) for one in VISIT_TAIL_ONE)
    if DIARY_THING.search(said):
        return DIARY_TIME_TAIL if DIARY_TIME.search(said) else DIARY_TAIL
    if re.search(r"\b(?:meet|meeting|seeing)\b", said):
        return MEETING_TAIL if DIARY_TIME.search(said) else MEETING_TIME_TAIL
    if set(re.findall(r"[a-z']+", said)) & OCCASIONS:
        # A day with an occasion on it and no travelling in the line - "my sister's wedding is
        # next june" - is still a date the person is counting towards.
        return OCCASION_TAIL
    return None


def _plan_tails(found, clean, memory):
    """The endings a trip or an occasion wants, or None when the line is another kind of plan.

    Everything else the store filed as a plan - "i want to save for a house", "im going to
    start running" - is a project with a first step and keeps its own reply, which the composer
    gives it.
    """
    kind = reads_as_a_trip(clean)
    if kind == "trip":
        options = TRIP_TAIL
    elif kind == "occasion":
        options = OCCASION_TAIL
    elif kind == "occasion_flat":
        options = OCCASION_FLAT_TAIL
    else:
        options = _a_diary_plan(found, clean)
        if not options:
            return None
    if HOW_LONG_ALREADY.search(clean):
        options = tuple(one for one in options if "how long" not in one.lower()) or options
    if _asked_last(memory):
        # Two questions in a row is an interrogation: say the thing they can use instead.
        options = tuple(one for one in options if not one.endswith("?")) or options
    return options


# A body that troubles them is not a thing they own: "i have an abscess on my leg" came back
# "Noted: you have an abscess on your leg", which is the coldest reply there is. The symptoms the
# other modules answer are read by badnews.reads_like_a_symptom; a word no list has yet is caught
# by the understanding engine's own topic, so the guard is the topic rather than a longer list.
#
# A thing they had is a story, not a possession: "we had a small wedding last year" was answered
# "Noted: you had a small wedding last year", and a friend asks about the day instead.
PLACED_IN_THE_PAST = re.compile(
    r"\b(?:last (?:year|summer|winter|spring|autumn|month|week|night)|years ago|months ago|"
    r"weeks ago|back in|when i was|used to)\b", re.I)


def _about_a_body(read, memory=None):
    """Whether the line is the person's own body or health, however it words it."""
    try:
        read_it = understanding(read, memory if isinstance(memory, dict) else {})
    except Exception:  # noqa: BLE001 - a reading that fails is not a reason to echo a symptom
        return False
    return isinstance(read_it, dict) and read_it.get("topic") == "health"


# "I've got a bathroom to sort out", "i have a loft to clear out", "i have a tax return to do":
# the thing is not a possession, it is a job on their list, and saying it back - "Noted: you've got
# a bathroom to sort out" - is the filing cabinet STYLE.md rules out. The tail is chosen by the
# shape (`have` + a thing + `to` + a verb) and never by the topic word, so one pool fits a loft, a
# tax return and a bike, and the person gets a friend's question about the job rather than their
# own words back.
JOB_TO_DO = re.compile(
    r"\bto\s+(?:sort|fix|clear|clean|paint|do|tidy|finish|replace|handle|deal\s+with|"
    r"get\s+(?:rid\s+of|done|sorted)|put\s+up|take\s+down|strip|sand|wire|plumb|service|"
    r"return|file|chase|book|renew|sell|pack|prepare|plan|write|organise|organize|arrange|"
    r"fill\s+(?:in|out)|sign|complete|send\s+(?:off|back)|post\s+off|"
    r"build|assemble|learn|study|wrap|draft|collate|make|iron|wash|mow|weed|dig|tile|grout|"
    r"seal|hang|fit|install|mount|mend|sew|hem|scrub|hoover|vacuum)\b", re.I)


# The first tail asks whether the job is the weekend's, and that question is already answered when
# the line names the day: "i have a report to write for friday" was offered "is that the weekend,
# or are you fitting it in around work?" - a question the line had just said the answer to.
JOB_HAS_A_DAY = re.compile(
    r"\b(?:today|tonight|tomorrow|tmrw|this\s+(?:week|weekend|month|evening)|next\s+week|"
    r"weekend|by\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|the\s+end)|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|the\s+end\s+of\s+the\s+month)\b",
    re.I)


JOB_TAIL = (
    "{Thing} \u2014 is that the weekend, or are you fitting it in around work?",
    "{Thing}. Do you know where to start with it, or is that the hard part?",
    "{Thing} \u2014 what's the first thing that needs doing?",
    "{Thing}. Is it a bigger job than it looked?",
)


# What the person says about the job they had before. A job said in the past is the strongest
# thing in the line and the store keeps it (`facts.JOB_WAS`), but the receipt pools answered it as
# a day that has happened - "i was a teaching assistant before the kids" got "How was it,
# overall?" and "i was a nurse" got "Good to hear. What was the best bit?", which is a verdict on
# a life rather than an answer. The word that says when ("before the kids", "until 2019") is what
# makes the line a job they had rather than the job they have, so it also decides which pool.
JOB_BEFORE = re.compile(r"\bbefore\s+(?:the|my|we|i|having|that)\b|\b(?:until|till|up to)\s+\d",
                        re.I)


PAST_JOB = (
    "{X} — that is a real thing to have behind you. What has changed since then?",
    "{X} is not nothing to have behind you. Whatever comes next, you are not starting from the "
    "bottom of anything.",
    "{X}, then. You know that work from the inside, which counts for more than it looks.",
)


# The job comes out of the store without its article ("nurse", "teaching assistant"), so no line
# in these pools can put it in the middle of a sentence - "You were nurse" and "So it is
# receptionist you did before" are the kind of line that makes the bot sound like a form. The job
# opens the sentence instead, and every line starts with `{X}`.
# Nothing here says they want to go back. "i was a receptionist before i had the kids" explains a
# gap in a life; it is not a plan, and answering it with "what would have to be true for you to go
# back to it" hands somebody a decision they did not bring.
PAST_JOB_PLAIN = (
    "{X} — that is not nothing to have behind you. Do you miss it, or are you glad to be out of "
    "it?",
    "{X} is a thing you already know how to do, which is more than most people start with.",
    "{X}, then. What is it that has you thinking about it now?",
)


def the_job_they_had(clean, memory):
    """A job the person said they used to do, answered as that, or None.

    The reading is the store's own (`facts.JOB_WAS` and the job `facts.extract` keeps), so a line
    this answers is a line the store filed: a job word, said in the past, about the person and
    not about somebody else, and not a question.
    """
    if not isinstance(clean, str) or "?" in clean:
        return None
    if not facts.JOB_WAS.search(clean):
        return None
    job = " ".join(str(facts.extract(clean).get("job") or "").split())
    if not job:
        return None
    if job.split()[0].lower() in facts.WAS_NOT_A_JOB:
        return None
    pool = PAST_JOB if JOB_BEFORE.search(clean) else PAST_JOB_PLAIN
    return pick(pool, memory, seed_text=clean).format(
        x=job, X=job[:1].upper() + job[1:])


# A receipt is a claim to have kept something, and said as the first line of a chat both of these
# claim a thing the chat has never named: "hes 9" was answered "Noted: he's 9." and "we have two of
# them" was answered "Noted: you have two of them." There is no "he" in the chat for the age to
# belong to and no "them" for the two to be two of, so the note is about nobody - and for the
# second one it is false as well, because the next line, "how many do we have", is answered "You
# haven't told me about a pet yet." The age is the milder case: it is kept with no name on it, and
# "how old is he" reads back "He is 9." about a person the bot cannot call anything. What is
# missing is the person or the thing, so the reply asks for it, with the figure in it when the line
# gave one: "Who's 9?" is the question a friend asks, and "Who do you mean?" is the one a form
# asks.
WHO_THE_FIGURE_IS = (
    "Who's {figure}?",
    "{Figure} \u2014 who's that?",
)


WHO_IS_IT = (
    "Who do you mean?",
    "Who's that, then?",
    "Who are we talking about?",
)


WHAT_OF_THEM = (
    "{Count} of what?",
    "{Count} of what, sorry?",
)


WHICH_ONES = (
    "Which ones do you mean?",
    "Which one do you mean?",
)


# The words that point back and name nothing. "we have two of them" means nothing at all until
# the chat has said what they are, and a note said back from it is the bot pretending it knows.
POINTS_BACK = re.compile(r"\b(?:them|those|these|ones|it)\b", re.I)


A_COUNT_OF_THEM = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a few|a couple|\d{1,3})"
    r"\s+of\s+(?:them|those|these)\b", re.I)


# A figure with a day still to come attached to it is a birthday somebody is counting down to:
# "she is 5 next month" was answered "She is 5 next month. Plenty of time, anyway.", which is
# about the day and claims nothing about the store. The same figure with no day ("hes 9") is the
# one that was noted back as a fact nobody had kept.
A_DATE_STILL_TO_COME = re.compile(
    # "shes turning 6" is a birthday still to come with no day said for it: the word "turning" is
    # the countdown itself. Read as a plain figure it was a fact nobody had kept, so a line whose
    # whole point was the coming birthday was answered "Who's 6?".
    r"\b(?:turning|turns)\s+(?:\d{1,3}|[a-z]+)\b"
    r"|\b(?:next|this)\s+(?:week|month|year|weekend|summer|christmas|spring|autumn|winter)\b"
    r"|\b(?:in|by|until|till)\s+(?:the\s+)?(?:new\s+year|summer|christmas)\b", re.I)


def _the_chat_holds_something(memory):
    """Whether a line was said before this one, so a pointer in this line can point at it.

    The rule this serves is the operator's: a reply that leans on what was said earlier needs
    something said earlier, and on a first message there is nothing, so the line itself has to be
    answered. `memory` on a first turn is not empty - the understanding, the facts read from the
    line and the topic are all in it before anybody composes a reply - so the turns said before
    this one are the thing to ask about.
    """
    return there_is_a_chat(memory)


def _the_pronoun_points_at_somebody(low, memory):
    """Whether a pronoun in this line can point at a person or an animal the chat has named.

    The store reads "she"/"he" against the people in the chat, and this asks the same reader, plus
    the two things it does not cover: an animal, which is a "he", a "she" or an "it" as far as the
    words go ("my cat has stopped eating" then "she's 12" is about the cat), and a "they", which
    is the group the chat has been naming ("something with the kids" then "theyre 6 and 9").
    """
    if _person_from_pronoun(low, memory):
        return True
    held = memory or {}
    theirs = held.get("user") if isinstance(held.get("user"), dict) else {}
    if any(isinstance(pet, dict) for pet in (theirs.get("pets") or [])):
        return True
    # A "he"/"she"/"his"/"her" points at the person the chat has already named, whether or not the
    # store has a fact about them yet. "i cant get my kid to sleep" then "hes 3" was answered
    # "Who's 3?" - the age asked whose it was two turns after the person said whose it was, and the
    # one thing the answer needed was already in the chat. The person words are read off the last
    # few turns the person typed, and a pet word counts with them ("my cat has stopped eating" then
    # "shes 12" is the cat, which is the reading the docstring above promises).
    fits = None
    if re.search(r"\b(?:she|shes|she's|her)\b", low or "", re.I):
        fits = facts.SHE
    elif re.search(r"\b(?:he|hes|he's|his)\b", low or "", re.I):
        fits = facts.HE
    if fits:
        said = " ".join(str((turn or {}).get("user") or "").lower()
                        for turn in (held.get("turns") or [])[-4:])
        for word in sorted(PERSON_WORDS.union(CHILD), key=len, reverse=True):
            if not re.search(r"\b" + word + r"\b", said):
                continue
            # The pronoun has to be one the person named can carry: "my mum is 60" then "hes 9" is
            # still a he nobody in the chat fits, and the question that asks whose age it is is
            # right. A word that names no gender ("kid", "toddler", "baby") carries either.
            if _pronoun_fits(word, fits):
                return True
    if not re.search(r"\b(?:they|theyre|they're|them|their|theirs|those|these)\b", low or "", re.I):
        return False
    words = set(re.findall(r"[a-z']+", low or ""))
    for turn in (held.get("turns") or [])[-4:]:
        words |= set(re.findall(r"[a-z']+", str((turn or {}).get("user") or "").lower()))
    for word in words:
        if word in PERSON_GROUP or word in CHILD:
            return True
    return any(str(entry.get("who") or "").strip() and not str(entry.get("who")).endswith("s")
               for entry in (held.get("others") or []) if isinstance(entry, dict))


def _somebody_was_being_hurt(memory):
    """Whether the line before this one said somebody is doing the person harm.

    "the kids at school pick on her" is a line about one person, and the store keeps nobody from
    it because she is only "her" - so the next line's "she" points at that person and at nobody
    else. This is the same room `_heavy` reads, for a line that names a figure instead of a fact.
    """
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)] \
        if isinstance(memory, dict) else []
    if not turns:
        return False
    return reads_as_cruelty(str(turns[-1].get("user") or ""))


def _who_the_figure_is(found, memory, low):
    """The question that asks who an age or a height belongs to, or None.

    Only for a reading that names nobody: "an age, of a person" with no person in it. The store
    keeps "my son is 9" against the son and drops "hes 9" when the chat holds no "he", so the
    note for the second one is about a fact nobody kept. `_person_from_pronoun` is the reader the
    store itself uses, so a chat that has the person - "my son is called tom" then "hes 9" - is
    left to the receipt it deserves.
    """
    entries = found.get("others") if isinstance(found, dict) else None
    if not entries:
        return None
    if SOMEONE_MILESTONE.search(low or "") or A_DATE_STILL_TO_COME.search(low or ""):
        # "she is 5 next month" is a milestone somebody is looking forward to, and the ending it
        # gets - "Plenty of time, anyway." - is said about the coming birthday, not a receipt for
        # a fact in the store, so it does not claim anything that was not kept.
        return None
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("who"):
            continue
        figure = entry.get("age") or entry.get("height")
        if not figure:
            continue
        if entry.get("pronoun") and _the_pronoun_points_at_somebody(low, memory):
            return None  # somebody in the chat fits the pronoun, so this is a fact about them
        if entry.get("pronoun") and _somebody_was_being_hurt(memory):
            # The chat holds no person to name because the line before named one by pronoun only:
            # "the kids at school pick on her" then "shes 7" was answered "7 - who's that?", which
            # asks the person to introduce their own child in the middle of saying what is
            # happening to her. The room says there is exactly one person this is about - the one
            # being hurt - so the age is hers and is answered as hers.
            pron = str(entry.get("pronoun") or "").strip().lower()
            said = ("%s's %s" % (pron, figure)) if isinstance(figure, int) else ""
            if said:
                return pick(HEAVY_FRAMES, memory, seed_text=low).format(
                    thing=said, Thing=said[:1].upper() + said[1:])
            return None
        if isinstance(figure, int) and figure:
            return pick(WHO_THE_FIGURE_IS, memory, seed_text=low).format(
                figure=str(figure), Figure=str(figure))
        return pick(WHO_IS_IT, memory, seed_text=low)
    return None


def _what_the_pointer_is(read, memory):
    """The question that asks what a bare "them" names, or None.

    Only while the chat holds nothing: once there are turns, "them" points at something the
    person said, and a chat that has a thing in it is not this reader's business.
    """
    if _the_chat_holds_something(memory):
        return None
    if not POINTS_BACK.search(read or ""):
        return None
    count = A_COUNT_OF_THEM.search(read or "")
    if count:
        counted = count.group(1)
        return pick(WHAT_OF_THEM, memory, seed_text=read).format(
            Count=counted[:1].upper() + counted[1:])
    return pick(WHICH_ONES, memory, seed_text=read)


# A condition they only wonder about is a question, not a fact. "i think i have diabetes" was
# said straight back - "Noted: you think you have diabetes" - which is the coldest reply there is
# and no answer at all, and "i think i have depression" came back a turn later in "what do you
# know about me". The line is asking whether it is diabetes, so it is answered: the thing is
# named, and the answer says who can actually tell them and what to take to the appointment.
A_WONDERED_CONDITION = re.compile(
    r"\bi\s+(?:think|believe|reckon|suspect|might|may)\b[^.!?,;]{0,30}?\b"
    r"(?:i(?:['\u2019]?ve|\s+have)?\s+)?(?:have|got)\s+(?P<thing>[a-z][a-z'\u2019 \-]{2,30})",
    re.I)


# The same line saying no: "i don't think i have depression" is not a worry to answer.
A_WONDER_SAID_NO = re.compile(
    r"\b(?:don'?t|do not|didn'?t|did not|never|not)\s+(?:think|believe|reckon|suspect)\b"
    r"|\bnot sure\b|\bno idea\b", re.I)


# An article in front of the thing is often a thing rather than a condition ("i think i have a
# meeting at 3", "a parcel coming", "a bill"), so a phrase that takes one has to earn its place: a
# condition kind at the end of it ("an eating disorder", "a chest infection") or one of the sets
# of initials a condition is known by, which no errand ever is.
WITH_AN_ARTICLE = frozenset("a an the some any my our his her their this that these those".split())


A_CONDITION_KIND = re.compile(r"(?:disorder|syndrome|disease|infection|deficiency|condition|"
                              r"intolerance|allergy|virus|ulcer|fracture|clot|itis|concussion|"
                              r"hernia|mole|reaction|abscess|boil|polyp|stones?)$")


# The conditions that go by their initials. A short word with an odd vowel in it is no signal on
# its own - "a bill", "a cyst", "a milk" - so the ones that are initials are named, and they are
# written back in capitals because that is how they are written.
CONDITION_INITIALS = frozenset("""sti dvt uti hiv ibs ocd adhd ptsd ms me cf ibd copd gerd pnd
    tmj pcos""".split())


# Where to send them depends on what is being wondered about, because the way in is what the
# person actually needs: an assessment, a test, or a GP. A condition names its own family; none
# of this is written for one phrasing.
CONDITION_FAMILIES = (
    (re.compile(r"\b(?:depression|depressed|anxiety|ptsd|adhd|autism|autistic|bipolar|ocd|"
                r"eating|anorexi\w*|bulimi\w*|burnout|self.?harm)\b"), (
        "Whether it's {thing} isn't something I can judge from a chat - that takes a proper "
        "assessment, and the way in is a GP appointment or a self-referral to talking therapy. "
        "Say how long it has been like this and what has changed; that is where the assessment "
        "starts.",
        "I can't diagnose {thing} and a guess would be no use to you. Book a GP appointment and "
        "ask about a referral; with something like this the waiting list is the annoying part, "
        "so the useful move is to get in the queue now rather than when it gets worse.")),
    (re.compile(r"\b(?:sti|hiv|chlamydia|gonorrhoea|gonorrhea|herpes|syphilis|thrush|warts|"
                r"piles|haemorrhoids|hemorrhoids)\b"), (
        "I can't tell you from here whether it's {thing}. Get it checked: a sexual health "
        "clinic sees you without a GP referral, the test is quick and usually free, and they "
        "can treat it there too.",
        "Whether it's {thing} is a test question, not a chat one. Clinics do free, confidential "
        "testing and you can walk in without a referral - go sooner rather than later, because "
        "most of these are easy to sort once you know what it is.")),
    (None, (
        "Whether it's {thing} is a doctor's call, not something a chat can settle. Book an "
        "appointment and take a note of when it started and what has changed - that is what "
        "turns a hunch into an answer.",
        "I can't tell you whether you have {thing}, and a guess would be worse than no answer. "
        "Get it looked at - a GP or a walk-in clinic - and write down how long it has been going "
        "on first, because that is the first thing they ask.",
        "Whether it's {thing} is not something I can say from here - that needs someone who can "
        "examine you or run a test. Book it, and take three things: when it started, what has "
        "changed, and what you want out of the appointment.")),
)


def _the_route_for(thing):
    """The frames that suit the kind of condition being wondered about."""
    low = thing.lower()
    for family, frames in CONDITION_FAMILIES:
        if family is not None and family.search(low):
            return frames
    return CONDITION_FAMILIES[-1][1]


def _the_entry_names(entry, head):
    """Whether the entry that answered the line is about this thing at all.

    "i think i have an eating disorder" reached an entry about cities, so a card being in reach
    is not the same as the card being about the worry. An entry that will not say is taken at its
    word.
    """
    keys = getattr(entry, "key", ())
    if not keys:
        return True
    if head in keys:
        return True
    for word in keys:
        if len(word) > 3 and (word[:4] == head[:4] or word[:5] == head[:5]):
            return True
    return False


def _a_condition_they_wonder_about(clean, memory=None):
    """The answer to "i think i have <condition>", or "" when this is not that line.

    Only the lines nothing else can answer come here: a line the knowledge base has an entry
    for is answered from it ("i think i have gout" is answered about gout), and a symptom word
    is the bad-news or chat pool's turn ("a chest infection" keeps its own answer).
    """
    if not clean or A_WONDER_SAID_NO.search(clean):
        return ""
    match = A_WONDERED_CONDITION.search(clean)
    if not match:
        return ""
    words = " ".join(match.group("thing").lower().split()).strip("-' ").split()
    if not words:
        return ""
    article = words[0] if words[0] in WITH_AN_ARTICLE else ""
    if article:
        words = words[1:]
    if not words:
        return ""
    head = words[-1]
    if head in NOT_A_THING or head.isdigit():
        # "i think i have time", "i think i have a meeting at 3": not a condition at all.
        return ""
    if any(word in NUMBER_WORDS for word in words) or any(ch.isdigit() for ch in head):
        # "i think i have two left": a count, not a thing they have.
        return ""
    if any(word in VERBISH for word in words) and not A_CONDITION_KIND.search(head):
        # "i think i have left my keys at work", "a parcel coming": the phrase has a verb in it,
        # so it is something they did or are doing, not a condition they are wondering about.
        return ""
    initials = head in CONDITION_INITIALS
    if article and not (A_CONDITION_KIND.search(head) or initials):
        return ""
    if reads_like_a_symptom(clean.lower()):
        return ""
    entry = topics.an_entry_for(clean)
    if entry is not None and _the_entry_names(entry, head):
        # An entry already answers this line, and it knows more about the condition than a line
        # about who can tell them does.
        return ""
    phrase = " ".join([head.upper() if initials else word for word in words])
    if article:
        phrase = article + " " + phrase
    return pick(_the_route_for(phrase), memory, phrase).format(thing=phrase)


# A limit raised, said without the word "budget": "i could stretch to 600", "we can go up to
# 900 at a push" (`STRETCH_BUDGET` in bot/memory/facts.py). The raised figure is the same kind of
# money as the limit it raises, so the line it raises decides its ending: without this, a laptop
# budget of 500 and then "i could stretch to 600" got "fixed bills and food first, then
# savings", because the earlier line's word "budget" was read as the money-topic signal.
RAISED = re.compile(r"\b(?:stretch\s+(?:it\s+)?(?:up\s+)?to|go\s+up\s+to|"
                    r"push\s+(?:it\s+)?(?:up\s+)?to)\b", re.I)


def _a_spending_budget(clean, memory):
    """Whether a stated budget is money to spend on a thing rather than a month to live inside.

    Asked once, where the budget frame is chosen, so every way of stating a budget gets the same
    reading: the period decides it when the line names one, and otherwise the conversation does.
    """
    if PERIOD.search(clean or "") or A_SPAN_OF_TIME.search(clean or ""):
        return False
    # A line that says what they mean to spend is about a thing, not about a month to live inside:
    # "i only want to spend 200 pounds" arrived with the living ending - "fixed bills and food
    # first, then savings" - in a chat that had just asked what a good bike costs. The period is
    # what makes it a month to live on, and that is checked first, so "i want to keep it to 300 a
    # month" keeps the living reading.
    if (facts.INTENDED_SPEND.search(clean or "") or facts.THE_THING_MAY_COST.search(clean or "")
            or facts.ALL_I_CAN_DO.search(clean or "")):
        return True
    if FOR_A_THING.search(clean or ""):
        # The line names what the money is for, so it is money to spend on that thing.
        return True
    recent = [clean or ""]
    for turn in (memory.get("turns") or [])[-3:] if isinstance(memory, dict) else []:
        if isinstance(turn, dict):
            recent.append(str(turn.get("user") or ""))
    for topic in (memory.get("topics") or [])[-2:] if isinstance(memory, dict) else []:
        if isinstance(topic, dict):
            recent.append(str(topic.get("text") or ""))
    said = (clean or "").strip().lower()
    others = [line for line in recent if line.strip().lower() != said]
    if RAISED.search(clean or ""):
        for line in others:
            if FOR_A_THING.search(line) or BUYING.search(line):
                return True
            if PERIOD.search(line) or A_SPAN_OF_TIME.search(line):
                return False
    if MONEY.search(" ".join(others).lower()):
        return False
    return bool(BUYING.search(" ".join(recent).lower()))


# The person told about by the line: "my mums birthday is next week" files nothing, and it is
# still their mum's news rather than theirs.
THEIRS = re.compile(
    r"\b(?:my|our)\s+(?:mum|mom|mam|mother|dad|father|son|daughter|sister|brother|wife"
    r"|husband|partner|aunt|uncle|gran|granny|grandma|grandad|grandpa|nan|cousin|niece|nephew"
    r"|mate|mates|friend|neighbour|neighbor|colleague|boss|stepson|stepdaughter|stepdad|stepmum"
    r"|boyfriend|girlfriend|fiance|fiancee)(?:'?s)?\b", re.I)


def _about_someone_else(found, clean=""):
    """Whether the line's fact is about a person of theirs rather than about the person typing.

    A win of their own is answered by the composer's own good-news pools (`reads_as_good_news`
    declines it here), so only somebody else's is read: their son, their mum, their neighbour.
    """
    for key in ("people", "others", "kids", "relations"):
        if (found or {}).get(key):
            return True
    return bool(THEIRS.search(str(clean or "")))


def _a_visit(clean):
    """Whether the line is a visit announced, rather than a lift or a question.

    A question is not news ("when is my sister coming" asks the bot what it cannot know), and the
    errand on the way past is not a visit ("my mum is coming to pick me up").
    """
    said = str(clean or "")
    if not said.strip() or said.rstrip().endswith("?") or NOT_A_VISIT.search(said):
        return False
    if re.match(r"\s*(?:when|what|how|why|where|who|is|are|does|do|will|did)\b", said, re.I):
        return False
    return bool(SOMEONE_COMING.search(said))


def _the_milestone(clean):
    """A round birthday or an anniversary of somebody else's, which is not the same as an age.

    "my son is 9" is a fact to keep; "my mum is 70 next week" is a thing people make something
    of, and "my son got a prize at school" is news rather than a milestone.
    """
    return bool(SOMEONE_MILESTONE.search(str(clean or "")))


def _a_workplace(found, heavy=False, memory=None):
    """Whether the line told the bot where the person works, and nothing else.

    Only the place the work is in: the store keeps it beside the job ("in a warehouse", "at
    tesco"), so those words are the tell. A line that files something else as well - an age, a
    pet, a place they live - keeps the plain frames, because the thing said back is then two
    facts and a workplace ending answers only one of them. A hard week two turns back keeps its
    own endings as well: there the apology is the reply, whatever was filed.
    """
    if heavy or not isinstance(found, dict) or not found.get("job"):
        return False
    rest = [key for key, value in found.items()
            if value and key != "job" and not key.endswith("_frame")]
    if rest:
        return False
    frame = ""
    if isinstance(memory, dict):
        known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
        frame = str(known.get("job_frame") or "").strip().lower()
    return bool(frame) and frame.split()[0] in WORK_PLACE


# The keys of facts.extract() that name a person of theirs: the family a death leaves behind.
FAMILY = ("people", "others", "kids", "relations")


def _about_the_family(found):
    """Whether the fact filed is about a person of theirs rather than a pet, a job or a taste.

    "my son is 9" after a death is the family the death named, and the apology belongs on it.
    "i have two cats" and "i work in a shop" are the person telling you about their life, and the
    apology there says the cats are part of the pile.
    """
    return any((found or {}).get(key) for key in FAMILY)


def _just_a_liking(found):
    """Whether the only thing this line filed is a taste, which is not something that lands.

    "i love pasta" two turns after a death was answered "You love pasta — I'm sorry it's all coming
    at once", which reads as a mistake: a liking is not one more thing on a person's plate, and it
    is not what the room of a hard week changes. Anything else in the line (an age, a pet, a job)
    can be that, and keeps the heavy ending.
    """
    rest = {key for key, value in (found or {}).items()
            if value and key != "tastes" and not key.endswith("_frame")}
    return bool((found or {}).get("tastes")) and not rest


def _heavy(memory):
    """Whether the last few turns hold a death, a separation or harm somebody is doing.

    Only the recent turns: a funeral six turns ago has been answered, and a fact told now is
    not still being said through it. A line that is itself a loss or bad news is guarded where
    it arrives, so this is only about the room the next fact is said in.
    """
    for turn in (memory.get("turns") or [])[-HEAVY_TURNS:]:
        if not isinstance(turn, dict):
            continue
        said = " ".join(str(turn.get("user") or "").split())
        if not said:
            continue
        if loss.reads_as_loss(said) or SEPARATION.search(said.lower()) or reads_as_cruelty(said):
            return True
    return False


def _statement(memory):
    """Whether the understanding engine read the line as telling the bot something."""
    understood = memory.get("understood")
    kind = understood.get("kind") if isinstance(understood, dict) else None
    if isinstance(kind, str) and kind:
        return kind in ("statement", "tell", "news")
    return True


def _a_loss(text, memory, clean):
    """Whether bot/compose/loss.py reads a death or a grief in the line: that is its turn."""
    understood = memory.get("understood")
    topics = understood.get("topics") if isinstance(understood, dict) else None
    return loss.reply_for(text, memory, clean, topics) is not None


def _children_with_ages(text):
    """The children a line names with an age: "my kids are ada 7 and sam 4"."""
    reader = getattr(facts, "_kids_named_with_ages", None)
    try:
        return reader(text) if reader else []
    except Exception:
        return []


def _children_said(kids):
    """The children said back by name and age: "Ada is 7 and Sam is 4"."""
    parts = []
    for kid in kids[:4]:
        name = str(kid.get("name") or "")
        if not name:
            continue
        parts.append(name[:1].upper() + name[1:] + " is " + str(kid.get("age")))
    return " and ".join(parts)


def _adds_one_more_allergen(text, memory):
    """The allergy a line adds to the ones on record, or []: "and milk too" after peanuts.

    Only an allergy the person already gave is added to: a food word on its own says nothing
    about what it is being added to, and guessing "milk" into an allergy for someone who has
    not said they are allergic to anything is the one mistake worth never making.
    """
    if not isinstance(memory, dict):
        return []
    known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    held = known.get("allergies") or []
    if not isinstance(held, list) or not held:
        return []
    # The thing may already be in the list: the store files it on this same turn, before the
    # reply is chosen, so "and milk too" is read here against a list that already has the milk
    # in it. What is said back is the fact either way.
    return facts.one_more(text)


# The frame a repair puts round the thing it puts in place ("sorry i mean", "make that",
# "no, i meant to say"). What follows it is the thing itself, and a thing that is only a figure
# says nothing once the frame is taken off.
REPAIR_FRAME = re.compile(
    r"^\s*(?:(?:no|nope|sorry|apologies|actually|wait|hold\s+on|oops|and|so|oh|right|ok|okay)"
    r"\b[\s,]*)*(?:i\s+(?:mean|meant)(?:\s+to\s+say)?|make\s+that|you\s+mean)\b[\s,]*", re.I)


def _words(text):
    """The words of `text` that carry meaning: no articles, no auxiliaries, lower case."""
    out = []
    for word in WORD.findall(str(text or "").lower()):
        if word in _EMPTY:
            continue
        out.append(word)
    return out


# Words that name nothing on their own. "just everything at once" and "more of the same" are
# how they feel, not a fact to keep, and "everything at once — noted" is the coldest thing the
# store can say to someone having a bad day.
VAGUE = frozenset("""everything anything something nothing all stuff things thing lot lots
    bit bits more less much many one ones again once anyway same usual normal worse better
    else other others""".split())


def _names_nothing(body):
    """True when the words left are only filler and vague ones, so there is nothing to say back."""
    named = [word for word in _words(body) if word not in VAGUE]
    return not named


# A line that is only a preposition phrase after its lead-in is a fragment, not a thing:
# "sorry for moaning" loses "sorry" to the lead-in and leaves "for moaning", which said back
# reads "for moaning - noted" and answers the apology with a filing cabinet.
_OPENS_WITH_A_LINK = re.compile(r"^(?:for|about|to|of|with|in|on|at|over|into|like|as)\b", re.I)


# A budget said with nothing around it opens with one of those words ("about 30 pounds", "about
# 20 quid") and is still the whole fact, not half a sentence: the store keeps it, so it is said
# back. Money is what makes it whole, so a symbol or a money word has to be there.
MONEY_ONLY = re.compile(
    r"^(?:(?:about|around|under|below|less than|up to|max(?:imum)?|no more than|not more than)\s*)?"
    r"(?:[£$€]\s?\d[\d,.]*(?:\s?(?:k|pounds?|quid|euros?|dollars?|bucks))?"
    r"|\d[\d,.]*\s?(?:pounds?|quid|euros?|dollars?|bucks|k)\b)$", re.I)


def _repairs(clean, memory):
    """The line with the understanding engine's own corrections in it.

    A friend does not say your typo back. "my dog is geting old" was answered "your dog is geting
    old", and "im alergic" came back spelled the same way; the engine had already repaired both
    words for its own reading, and the echo only used its chat-speak table (SHORT), which is a
    different list. So the echo takes every word the engine repaired, in place, and keeps the
    words it left alone - a hyphen, a digit or a name is what they typed.

    A contraction typed without its apostrophe is one word where the reading has two: "were going
    to spain in may" reads as "we are going to spain in may", and the echo knows neither line, so
    it never got said back at all. The engine keeps that table (`LEFT_OFF_CONTRACTION`), so the
    count of words comes from it rather than from a second list here, and only the words it adds
    are allowed to appear where the person typed one.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    plain = understood.get("plain") if isinstance(understood, dict) else None
    if not isinstance(plain, str) or not plain.strip():
        return clean
    typed, fixed = clean.split(), plain.split()
    if not typed:
        return clean
    pairs, was_at, now_at = [], 0, 0
    while was_at < len(typed) and now_at < len(fixed):
        words = LEFT_OFF_CONTRACTION.get(typed[was_at].lower())
        if words and fixed[now_at:now_at + len(words)] == list(words):
            pairs.append((typed[was_at], " ".join(words)))
            now_at += len(words)
        elif (typed[was_at].lower() == fixed[now_at].lower()
              or (typed[was_at].isalpha()
                  and fixed[now_at].replace("'", "").replace("\u2019", "").isalpha())):
            pairs.append((typed[was_at], fixed[now_at]))
            now_at += 1
        else:
            return clean
        was_at += 1
    if was_at != len(typed) or now_at != len(fixed):
        return clean
    words = []
    for was, now in pairs:
        # A repair is a word for a word, and it changes the letters, not the case: the engine
        # lowercases the line for its own reading, and "Meg" is still "Meg". "co-op" read as
        # "co op" and "2" read as "two" are that same bookkeeping - not something to hand back
        # differently from how it was typed. A repair may carry an apostrophe, which is a
        # spelling ("ur" is read and said back as "you're"), so the apostrophe is not a word,
        # and a contraction typed flat is read as two words ("were" is "we are"), which is.
        if (was != now and was.isalpha()
                and (now.replace("'", "").replace("\u2019", "").isalpha() or " " in now)
                and was.lower() != now.lower()):
            words.append(now[:1].upper() + now[1:] if was[:1].isupper() else now)
        else:
            words.append(was)
    return " ".join(words)
