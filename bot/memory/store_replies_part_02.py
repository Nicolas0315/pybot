"""Part 2 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import (
    content, forms, keywords, last_bot, last_module, last_user, others, recent, user,
)
from ..memory import ack
from ..memory import condition
from ..memory import facts as extract
from ..memory import resize
from ..memory.topics import STOPWORDS
from ..understanding import understand
from ..understanding.kinds import the_manners_question
from ..memory.store_lines import (
    ADVICE_MODULES, SLOT_KEY, BARE_SLOTS, WHERE_ASK, KIN, BAD_NEWS, TURNED, PART_HELD, PART_KEYS,
    KEPT_THINGS, NAMED_BY, SWAPPABLE,
)
from ..memory.relations import _called, _same_as_last
from ..modules.memory_tables import (
    ELIDED_AGAIN, ELIDED_ASK, ELIDED_NAMES, ELIDED_WORDS, MISSED_CATCH_UP,
)
from bot.memory.corrected import (
    MONTHS, RELATIVE_MONTH, _asks, _date_said, _date_word, _date_word_case,
)
from .store_replies_part_01 import (
    STOPWORDS,
)


THE_CHAT_ASK = re.compile(
    r"\bwhat (?:were|are|was) (?:we|i|you) (?:talking|chatting|saying|on) about\b|"
    # "what are you up to" is not a recap: the person is asking the bot what it is doing, and
    # the only honest answer is that there is nothing at this end. "what were you saying" and
    # "what were you on about" are still the recap - there the "you" is the chat's own last ask.
    r"\bwhat (?:were|are|was) (?:we|i) (?:on|up to)\b|"
    r"\bwhat (?:were|was) you (?:on|up to)\b|\bwhat are you on about\b|"
    r"\bwhat (?:were|was) you saying\b|"
    r"\bwhat (?:have|had|did) (?:we|you) (?:talked|spoken|chatted|covered|discussed) about\b|"
    r"\bwhat (?:were|are|was) (?:we|i|you) saying\b|"
    r"\bwhere (?:were we|are we)(?=\s*[?.!,]|\s*$)|"
    r"\bwhere did we (?:leave|get to|stop)\b|\bwhere we (?:got to|left off)\b|"
    r"\bwhat was i (?:saying|on about|telling you|mentioning)\b|\bcatch me up\b|\brecap\b|"
    + MISSED_CATCH_UP.pattern + r"|"
    r"\bwhat have i been (?:saying|telling you)\b|"
    r"\bremind me (?:what|where|how)\b|\bsum (?:up )?what we\b|"
    # One ask with the "have" in it or left out: "what we have covered" and "what we covered". The
    # "have" shape cannot be anything else, so it is read anywhere in the line; the shape without
    # it is also how a statement ends ("thats what we said"), so it is only the ask when it is the
    # whole line - which is what `_bare` leaves behind once the reminder wrapper comes off.
    r"\bwhat we (?:have|had) (?:covered|talked|discussed|done|said|been on)\b|"
    r"^(?:and |but |so |ok |okay |also |now )?what we "
    r"(?:covered|talked|discussed|done|said|been on)\b"
    r"(?=\s*(?:[?.!,]|$|again\b|so far\b|before\b|earlier\b|today\b|already\b))|"
    r"\bwhat we (?:talked|spoke|spoken|chatted|covered|discussed) about\b|"
    r"\bwhat we were (?:on|up to)\b", re.I)


def _about_the_bot_here(memory):
    """True when the understanding engine read this line as a question about the bot itself.

    "What have you been up to at the weekend", "what were you up to two days ago" ask the bot
    about its own doings and have nothing to do with what the person said, so the store must not
    read them as a recap of their line and answer "we're still at the beginning". The one ask
    about the bot the store does own is what it remembers (`about_bot_kind` is "memory").
    """
    reading = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(reading, dict):
        return False
    if the_manners_question(reading.get("norm") or []):
        # "What are you up to", "watcha doing" and "wuu2": how the bot is filling its time,
        # whichever words ask it. The engine reads the whole line, and `_about_the_bot_here` is
        # the one place that says it, because THE_CHAT_ASK below matches "what are you up to" as
        # "what were we on about" and the store answered a hello with "we're still at the
        # beginning". The ask about the bot the store does own is what it remembers.
        return True
    if not reading.get("about_bot"):
        return False
    return reading.get("about_bot_kind") != "memory"


ASK_TAIL_FILLER = frozenset("""then now again here today tonight please thanks ok okay so also
just really honestly exactly mate actually""".split())


ASK_ABOUT_JOB = re.compile(
    r"^(?:at work|for a living|for work|for a job|all day|day to day|in the week|"
    r"when i(?:'m| am) at work|in my job|at the moment|these days)$")


def _ask_about_the_job(ask):
    """Whether a "what do i do" ask has nothing after it, or only words about the work itself."""
    found = re.search(r"\bwhat do i do\b(.*)$", " ".join(str(ask or "").lower().split()))
    if not found:
        return True
    tail = " ".join(word for word in re.findall(r"[a-z']+", found.group(1))
                    if word not in ASK_TAIL_FILLER)
    return not tail or bool(ASK_ABOUT_JOB.match(tail))


def _job_just_said(memory, ask=""):
    """True when the last line the person wrote is the one that gave us their job.

    Only a line that is *about the job* counts. "i work in a warehouse" then "what do i do"
    is the job they just told us; "i'm a nurse and my back is killing me" then "what do i do"
    is a request for help, because the line carried something else with it, and that something
    else is what the ask is about.
    """
    me = user(memory) or {}
    job = me.get("job")
    line = last_user(memory) or ""
    if not job or not line:
        return False
    # The job can be a phrase ("bus driver") or a name ("mcdonalds", "co-op"), so any of its
    # words will do: the last line is the one that gave us the job when it uses one of them.
    # The name itself is checked first, because ``content`` drops a short one ("co-op").
    said = " ".join(str(job).lower().split())
    # Where they work is the job's too. The place is kept beside the role, so a line like "i work
    # at mcdonalds" names no word of the role and no word of ``WORK_WORDS``, and without this the
    # bare ask after it would be answered as though the chat had moved on from the job. A line
    # that gave us the place is a line about the job, on the same terms as one that gave the role.
    place = " ".join(str(me.get("workplace") or "").lower().split())
    if not (said in " ".join(line.lower().split()) or _job_words_seen(job, line)):
        if not (place and _the_place_said(place, line)):
            # The last line need not name the job: a line about the work itself ("i teach year 4",
            # "i mostly do spreadsheets") keeps the conversation on it, so the bare ask is still
            # about the job they told us. A line about their back is not, and answers for itself.
            return _a_work_detail(line) and _ask_about_the_job(ask)
    if not _only_the_job(line, job, place):
        return False
    # The ask has to be about the job too: "what do i do about my back" is a back question.
    return _ask_about_the_job(ask)


SELF_DO_AGAIN = re.compile(
    r"\bwhat (?:do|should|shall|can) i do again\b|"
    r"\bwhat i (?:do|did) again\b")


WORK_WORDS = frozenset("""
    work works working worked job jobs shift shifts rota office shop store school site floor
    till ward class classes year years teach teaches teaching taught lesson lessons pupil pupils
    student students manage managing manager boss team colleagues employer staff run running look looking after
    stack stacking shelf shelves serve serving customers clients patients drive driving nurse
    nursing clean cleaning cook cooking chef sort sorting stock sell selling till fix fixing
    build building repair study studying train training paperwork spreadsheets meetings meeting
    emails email calls call desk counter kitchen warehouse factory clinic hospital
""".split())


NOT_A_DETAIL = frozenset("""
    hurt hurts hurting ache aches aching pain pains ill sick unwell tired exhausted stressed
    worry worried anxious sad low fed depressed killing killed broke broken leaking wrong
    problem problems cross upset angry cry crying lost quit quitting leaving left fired sacked
    bullying bullied
    hate hates hated love loves fancy stole stealing short complaint complained warned blamed
    mistake mistakes accident incident busy rush
    today tonight tomorrow morning mornings evening evenings afternoon afternoons later soon
    every each weekly daily
""".split())


def _a_work_detail(line):
    """Whether the line is a detail of the work alone, with nothing else that wants an answer."""
    low = " ".join(str(line or "").lower().split())
    if not low.startswith(("i ", "im ", "i'm ", "we ", "we're ")):
        return False
    words = {word.strip(",.!?;:'\"()") for word in low.split()}
    words.discard("")
    if len(words) > 10 or "?" in low:
        return False
    if words & NOT_A_DETAIL:
        return False
    if not words & WORK_WORDS:
        return False
    # Every other word says something about the work or nothing at all. "i got an email from HR",
    # "i fancy my manager" and "i stole from the till" all carry a word of the work and are about
    # something else, so a bare ask after them is about that something else.
    for word in words:
        if word in WORK_WORDS or word in JOB_ONLY or word.isdigit():
            continue
        return False
    return True


def _job_words_seen(job, line):
    """Whether the line uses one of the job's words, however it ends the word."""
    mine = set(content(job))
    for word in str(job).split():
        mine |= forms(word)
    seen = set(content(line))
    return bool(mine & seen) or any(mine & forms(word) for word in seen)


JOB_ONLY = frozenset("""
    i im am a an the my me and but so oh also too now just still actually really always
    sometimes only since ago these days day days night early late full part time hour hours
    week weeks month months year years shift shifts work working works job started start new
    mostly usually lots few two three four five
    as at in for on of to do doing it that this
    changed change changes switched switching switch job jobs role career quit quits left leaving
    packed gave lost moved got get getting have had
    today tomorrow soon next monday tuesday wednesday thursday friday saturday sunday january
    february march april may june july august september october november december spring summer
    autumn winter
""".split())


def _the_place_said(place, line):
    """Whether this line is the one that told us where they work.

    The place is kept with its own little words ("in a care home", "at the co-op"), so its
    content words are what has to turn up in the line: the rest ("i work in") belongs to the
    sentence, not to the place.
    """
    words = set(content(place))
    if not words:
        # "at the co-op", "at tesco": every content word of the place is short enough that
        # ``content`` drops it, so the written words have to do, less the little ones.
        words = {word.strip(",.!?;:'\"()") for word in str(place).lower().split()}
        words -= PLACE_LITTLE
    if not words:
        return False
    said = {word.strip(",.!?;:'\"()") for word in str(line).lower().split()}
    return words <= (set(content(line)) | said)


PLACE_LITTLE = frozenset("a an the in at on of to for my our their".split())


def _only_the_job(line, job, place=""):
    """Whether the line is the job and nothing else.

    "i work at the hospital" is; "i'm a nurse and my back is killing me" is not, and the thing
    it is about instead is what a "what do i do" after it wants an answer about.

    The place they work counts as the job here: with the role and the place kept apart, a line
    that gave the place ("i work at mcdonalds") carries a word of neither the role nor the work
    vocabulary, and it is still only about the job.
    """
    # A job said with the one it replaces in the same breath - "im a teacher not a nurse" - is
    # still a line about the job, so the part that takes the old one back is cut off first.
    line = extract.TAKE_BACK_SPLIT.split(str(line), 1)[0]
    left = {word.strip(",.!?;:'\"()") for word in
            " ".join(str(line).lower().split()).split()}
    left.discard("")
    mine = set()
    for word in str(job).lower().split():
        mine.add(word)
        mine |= {form.lower() for form in forms(word)}
    mine |= {word.lower() for word in content(str(job))}
    for word in str(place or "").lower().split():
        mine.add(word)
        mine |= {form.lower() for form in forms(word)}
    mine |= {word.lower() for word in content(str(place or ""))}
    return all(word in JOB_ONLY or word in mine for word in left)


TALKED_ABOUT = re.compile(
    r"\bwhat (?:did|have|had) we (?:talk|talked|chat|chatted|speak|spoken|discuss|discussed)"
    r" about\b|\bwhat (?:did|have|had) we (?:cover|covered|discuss|discussed|talk about)\b|"
    # "talk me through what we said", "run me through what we covered": the same ask in the
    # words people use when they want the last few turns back, so it is not a hollow ack.
    r"\b(?:talk|walk|run|take) (?:me )?through (?:what|everything) (?:we|i) (?:said|covered|talked)"
    r"\b|\bwhere (?:did|have) we (?:get to|got to|left it|ended up)\b")


SUMMARY_WORD = re.compile(r"\b(?:summar\w+|sum up|recap|rundown)\b|\bsummary\b")


CHAT_WORD = re.compile(r"\b(?:chat|conversation|talk(?:ed|ing)?|we|us|it all)\b")


SUMMARY_ASK_FILLER = re.compile(
    r"\b(?:can|could|would|will|you|u|please|pls|give|me|us|a|an|the|quick|brief|short|just|"
    r"and|so|then|again|now|ok|okay|of|it|all|that|this|our|your|chat|conversation|talk|we|"
    r"so far|today|everything|sum|up|for|to|on)\b")


def _summary_ask(low):
    """True for a line that asks for a summary or a recap of this conversation.

    Two shapes count: it points at the conversation ("summarise our chat", "what did we talk
    about", "a summary of what we said"), or it is the bare ask and nothing else ("summary?",
    "give me a quick recap"). "summarise this email for me" and "summarise the news" are
    requests about something else, and answering those with the person's own facts would be a
    non-answer.
    """
    line = str(low or "")
    if TALKED_ABOUT.search(line):
        return True
    if not SUMMARY_WORD.search(line):
        return False
    if CHAT_WORD.search(line):
        return True
    return not SUMMARY_ASK_FILLER.sub(" ", SUMMARY_WORD.sub(" ", line)).split()


THING_AGAIN = re.compile(
    r"^(?:and |so |but |also )?(?:what was|whats|what is|what's) the ([a-z]{3,})(?: again)?\??$")


WHICH_WAS = re.compile(
    r"^(?:and |so |but |also |oh |ok |okay )?which ([a-z][a-z' ]{2,24}?)\s*"
    r"(?:was it|is it|was that|did i say|did i tell you)\s*[?.!]*$")


ATTRIBUTE_SAID = re.compile(
    r"^(?:and |so |but |also |oh |ok |okay )?what (?:day|date|time|size|colour|color|number|"
    r"price|cost|amount|brand|make|model|year|month) (?:did i|have i) "
    r"(?:just )?(?:say|tell you|mention)\b")


NOT_A_THING_NAMED = frozenset(('one', 'thing', 'things', 'bit', 'bits', 'part', 'parts',
                              'point', 'way', 'kind', 'sort', 'time', 'other', 'else'))


def _an_attribute_they_gave(low):
    """True for "what day did i say it was due": the ask with the attribute in front of it.

    The words after the verb are what the line is looked for by ("it was due" -> "due"), so an
    attribute ask with nothing after the verb is not this shape: "and what size did i say" has
    no word to find a line by, and the attribute words themselves ("size") are not in the line
    that gives it ("in a medium"). That one keeps the reply it had.
    """
    if not ATTRIBUTE_SAID.match(low or ""):
        return False
    after = re.search(r"\b(?:say|said|tell you|told you|mention|mentioned)\b(.*)$", low)
    return bool(after and content(after.group(1)))


ATTRIBUTE_KIND = re.compile(
    r"^(?:and |so |but |also |oh |ok |okay )?(?:what|which)\s+([a-z][a-z' ]{1,24}?)\s+"
    r"(?:did i|have i|was it i|is it i|was that i)\s+(?:just )?"
    r"(?:say|said|tell you|told you|mention|mentioned)\b")


NOT_A_KIND = frozenset(('i', 'you', 'it', 'that', 'this', 'the', 'a', 'an', 'my', 'your', 'we',
                        'they', 'he', 'she', 'was', 'is', 'much', 'many', 'long', 'often', 'else',
                        'other', 'time', 'thing', 'one', 'day', 'now', 'then', 'about'))


def _which_thing_was_it(low, memory):
    """The thing in "and which knee was it", when they named it themselves earlier in the chat.

    Only a thing they said in one of their own lines is a recall: "which knee was it" before
    anything about a knee is a question about the world, and the answer to it is not a line of
    theirs, so this hands that line on untouched.
    """
    part = WHICH_WAS.match(low or "")
    if not part:
        return None
    thing = " ".join(part.group(1).split())
    if thing in NOT_A_THING_NAMED or not content(thing):
        return None
    if not _said_word(thing, memory):
        return None
    return thing


# The phrases that say *when* rather than *what*. "my laptop fan is loud all the time now" is a
# line about the fan: the "time" in it is how long for, not a thing they told the store about.
# Read as a thing, though, it made a bare "whats the time" a recall of that line, and the store
# answered the clock with the person's own words ("You said: \"my laptop fan is loud all the
# time now\"") while the clock was right there to be said. The same shape is in "its loud all
# day", "most of the time", "at the time" and "right now", so the phrases go before the word is
# looked for, and never the other way round.
A_WHEN = re.compile(
    r"\b(?:all|most|some|any|each|every|next|last|this|that|another|half|plenty\s+of|lots\s+of|"
    r"a\s+(?:long|short|little|bit\s+of|lot\s+of)|the\s+whole|the\s+entire)\s+(?:the\s+)?time\b"
    r"|\b(?:at|in|on|before|after|by|of)\s+the\s+time\b"
    r"|\btime\s+(?:to|for)\b"
    r"|\b(?:all|most|some|any|each|every|the\s+whole|these|those)\s+"
    r"(?:day|days|night|nights|week|weeks|month|months|year|years|morning|evening|afternoon)\b"
    r"|\b(?:right|just)\s+now\b")


def _without_the_when(line):
    """The line with the phrases that say when taken out, so "all the time" is not "the time"."""
    return A_WHEN.sub(" ", line)


# "what time is it", "have you got the time": the clock, asked in the words people use for it.
# The "it" in them points at nothing the chat has said, so a detail reader that leans on a
# pointing word is reading a referent that is not there.
A_CLOCK_ASK = re.compile(
    r"^(?:and |so |but |oh |right |ok |okay |hi |hello |sorry )*"
    r"(?:(?:whats|what's|what is|whats?) the time"
    r"|what\s+time\s+is\s+it"
    r"|(?:have|has|do|did)\s+(?:you|u)\s+(?:got|have|know)\s+the\s+time"
    r"|(?:got|know)\s+the\s+time)\b")


def _a_clock_ask(line):
    """True for a line that asks what the clock says."""
    return bool(A_CLOCK_ASK.match(str(line or "").strip().lower()))


def _said_word(word, memory):
    """Whether the person named this word, or one of its forms, in one of their last lines.

    A word inside a phrase that says when does not name anything: "all the time" is how long
    the fan has been loud, not something they told the store about the time of day. And a
    question they asked is not a thing they named: "what time is it" then "whats the time" is
    the same ask twice, and reading the first one as the thing the second is about handed the
    fan line back under "You said: ...". This is the rule the rest of the store already
    follows - an ask is kept as the question it was, never as the fact.
    """
    mine = forms(word)
    for turn in recent(memory, 8):
        said = str(turn.get("user") or "")
        if not said.strip() or _asks(said):
            continue
        line = _without_the_when(said)
        if not line.strip():
            continue
        if any(mine & forms(seen) for seen in content(line)):
            return True
    return False


def _elided_ask(text, memory, low=""):
    """(which fact an ask that leaves the fact out is about, whether that was a guess).

    "what did I say it was again?" after "what's my budget?" asks about the budget, and nothing
    else in the line may name a thing of its own. When no recall has been answered yet, the
    fact they mean is the one they just told me, and that is a guess: a miss on it would say
    they never said something they did, so the caller lets another module answer instead.
    """
    if not isinstance(memory, dict):
        return "", False
    line = " ".join(str(low or text or "").lower().split()).strip(" .,!?;:-")
    if not line or set(line.split()) - ELIDED_WORDS:
        return "", False
    raw = " ".join(str(text or "").lower().split())
    # The asking word is the one the folded line drops, and two of the shapes in ELIDED_ASK are
    # a recall only because of it: "what was it again" folds to "what was it", which is a question
    # about the thing and not about the conversation. So the raw line is tried as well as the
    # folded one - it is where "again" still is.
    if not (ELIDED_ASK.search(line) or ELIDED_ASK.search(raw)
            or (ELIDED_AGAIN.search(line) and "again" in raw)):
        return "", False
    turns = memory.get("turns") or []
    named = _named_slots(line)
    # The fact they just told me wins: "we have a dog called Biscuit" then "what did I call
    # him?" is about the dog, not about whatever was asked two turns ago.
    # "call" fits a pet as well as a name: "we have a dog called Biscuit" then "what did I call
    # him?" is about the dog.
    fits = named | {"name", "pets"} if {"name", "pets"} & named else named
    stated = _stated_slot(memory, turns)
    if stated and (not named or stated in fits):
        return stated, True
    # One line back: a question in between ("weve got a cat called Milo" / "is he any trouble?"
    # / "what did i call him again?") still leaves them asking about the fact they told me.
    stated = _stated_slot(memory, turns, back=2)
    if stated and (not named or stated in fits):
        return stated, True
    asked = memory.get("asked")
    if isinstance(asked, dict) and asked.get("slot"):
        try:
            asked_turn = int(asked.get("turn") or 0)
        except (TypeError, ValueError):
            asked_turn = None
        slot = str(asked["slot"])
        if asked_turn is not None and len(turns) - asked_turn <= 2 and (not named or slot in fits):
            return slot, False
    return "", False


def _named_slots(line):
    """The facts an elided ask names in its own words (empty when it names none)."""
    return {slot for slot, pattern in ELIDED_NAMES if pattern.search(str(line or ""))}


def _stated_slot(memory, turns, back=1):
    """The one fact the last thing the person said gave ("" when it gave none or several).

    Only the last line counts: "what did I call him" right after "we have a dog called Biscuit"
    is about the dog, and an allergy three lines earlier must not answer it. `back` reaches one
    line further, for a question between the fact and the ask ("weve got a rescue dog called
    Biscuit" / "what should i feed him?" / "what did i call him again?"): a line that gave no
    fact is walked past only when that line was a question, and two facts on one line still
    mean no guess at all.
    """
    user_lines = [turn for turn in list(turns or []) if isinstance(turn, dict)]
    window = list(reversed(user_lines[-max(1, int(back)):]))
    for offset, turn in enumerate(window):
        said = turn.get("user") or turn.get("text") or ""
        if not isinstance(said, str) or not said.strip():
            continue
        # One line back is for a question in between, never for any line: a line that gave a
        # fact this cannot name (a plan, a job) is not walked past, or "im allergic to nuts" /
        # "im going to spain in june" / "what did i say it was again?" would be answered with
        # the allergy rather than the plan they said last.
        if offset == 0 and int(back) > 1 and not _asks(said):
            return ""
        found = extract.extract(said, question=False)
        # `job` is left out on purpose: the job frame cannot yet say "work in a warehouse"
        # ("You told me you're a warehouse", #1123), and a quote of their line is better than a
        # broken sentence.
        kinds = [slot for key, slot in (
            ("name", "name"), ("city", "city"), ("age", "age"),
            ("budget", "budget"), ("allergies", "allergy"), ("pets", "pets")) if found.get(key)]
        if len(kinds) > 1:
            return ""
        if kinds:
            return kinds[0]
    return ""


def _remember_asked(memory, slot):
    """Keep the fact this answer was about, so the next elided ask is about the same one."""
    if not isinstance(memory, dict) or not slot:
        return
    memory["asked"] = {"slot": slot, "turn": len(memory.get("turns") or [])}


def _the_case_they_just_gave(text, memory):
    """The consequence of the last answer the short line just chose, said as the reply.

    "should i get a cat or a dog" -> "A cat is the kinder choice if you're out all day" ->
    "i work all day". The answer has already said what that means, so the reply is the choice it
    offered, with their case named - not "Got it - you work all day", which throws it away.
    """
    clean = " ".join(str(text or "").split())
    if not clean or "?" in clean:
        return None
    if _asks(clean):
        # A line that opens with an ask word is a question without the question mark, and it is
        # not a case they gave: "what did i say she is allergic to" after an answer was read as
        # one, and the reply said their own question back with the answer's tail on it.
        return None
    if last_module(memory) not in ADVICE_MODULES:
        return None
    said = str(last_bot(memory) or "").strip()
    if not said:
        return None
    consequence = condition.chosen(clean, said)
    if not consequence:
        if not condition.refused(clean, said):
            return None
        # The answer tested the number this line gives and their number fails the test, so the
        # answer's own verdict is not theirs: "is it worth fixing my old laptop" / "its 8 years
        # old" was answered "Repair it, then." by an answer that only repairs under five. Hand
        # the fact back and stop - the answer already said what it says for both cases it
        # named, and saying it again is worse than saying nothing more.
        gave = ack.said_back(clean, memory).strip(" .")
        return gave[:1].upper() + gave[1:] + "." if gave else None
    case = ack.said_back(clean, memory)
    if not case:
        return None
    body = consequence.strip(" ,;:-\u2014.")
    if not body:
        return None
    body = body[0].upper() + body[1:]
    # Their case first, then the choice the answer offered for it: saying the choice first reads
    # as a verdict out of nowhere.
    line = "%s. %s, then." % (case.strip(" .").capitalize(), body)
    if _same_as_last(line, memory):
        return None
    return line


COUNT_IN_AN_ANSWER = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|both|couple|pair)\b", re.I)


def _said_another_way(reply):
    """The same fact in a second wording, or None when there is no plain one."""
    text = str(reply or "").strip()
    match = re.match(r"^(?:Your|My) (name|job|budget) is (.+)$", text)
    if match:
        slot, value = match.group(1), match.group(2).rstrip(".")
        if slot == "budget":
            return "You said " + value + "."
        if slot == "name":
            return "I have you as " + value + "."
        if slot == "job":
            return "You told me it is " + value + "."
    match = re.match(r"^You told me you(?:'re| are) (.+)$", text)
    if match:
        return "You said you're " + match.group(1).rstrip(".") + "."
    match = re.match(r"^You've got (.+)$", text)
    if match:
        animals = match.group(1).rstrip(".")
        if animals.count("called") > 1:
            return None  # more than one name: no plain short way to say it
        named = re.search(r"\bcalled (.+)$", animals)
        if named:
            # "what's my dog called?" then "and what did I call him?" is the same name twice.
            return "Still called " + named.group(1) + "."
        if not COUNT_IN_AN_ANSWER.search(animals):
            # "You've got a cat." asked again is not "Still a cat.": with the number left off,
            # "still a cat" reads as "a cat and not a dog", which is another claim and no answer
            # to "how many". One animal has no plain second wording, so the plain one stands, as
            # it does for two names above.
            return None
        return "Still " + animals + "."
    match = re.match(r"^You (?:live|'re|are)(?: in| from)? (.+)$", text)
    if match:
        return "You said " + match.group(1).rstrip(".") + "."
    return None


def _slot_words(slot, memory=None):
    """The plain ask for a fact slot, so one set of patterns answers every ask."""
    if slot == "pets" and isinstance(memory, dict):
        pets = [p for p in (user(memory).get("pets") or []) if isinstance(p, dict)]
        animals = [str(p.get("animal") or "") for p in pets]
        if animals and animals.count(animals[-1]) == 1:
            return "what is my " + animals[-1] + " called"
    return {
        "name": "what is my name",
        "age": "how old am i",
        "job": "what is my job",
        "city": "which city do i live in",
        "budget": "what is my budget",
        "allergy": "what am i allergic to",
        "pets": "what are my pets called",
    }.get(slot, "what have i told you")


def _slot_of(low):
    """The fact a recall reply was about, from the plain ask that was answered."""
    for slot, pattern in (
            ("allergy", r"\ballerg"),
            ("car", r"\bwhat (?:do|did) i drive\b|\bcar\b"),
            ("budget", r"\bbudget"),
            ("pets", r"\b(?:dog|cat|pet)s?\b"),
            ("job", r"\bmy (?:job|work)\b|\bwhat do i do\b|\bwhere do i work\b"),
            ("city", r"\b(?:city|place|country)\b|\bwhere do i (?:live|come from)\b"),
            ("name", r"\bmy name\b|\bwho am i\b")):
        if re.search(pattern, low):
            return slot
    return ""


BARE_MINE = re.compile(
    r"^(?:and |so |ok |okay |but |well |also |what about |how about |again )*"
    r"(?:my|our)\s+([a-z][a-z' -]{0,24}?)$")


SLOT_NOUNS = {
    "name": frozenset("name".split()),
    "job": frozenset("job work".split()),
    "city": frozenset("city place town".split()),
    "budget": frozenset("budget".split()),
    "allergy": frozenset("allergy allergies allergen".split()),
    "pets": frozenset("pet pets dog dogs cat cats animal animals".split()),
    "age": frozenset("age".split()),
}


SLOT_FILLER = frozenset("""again now then please too as before though tho also still anyway
i told you said say remember""".split())


def _slot_named_in(low):
    """The fact a line that only names it asks for, from the fact's own words."""
    for slot, pattern in BARE_SLOTS:
        if re.search(pattern, str(low or "")):
            return slot
    return ""


def _slot_held(slot, memory):
    """Whether the store has a fact of theirs for this slot."""
    keys = SLOT_KEY.get(slot)
    if not keys:
        return False
    known = user(memory) or {}
    return any(known.get(key) for key in keys)


def _bare_ask_naming_a_fact(low, memory):
    """The slot a line that only names one of their facts is asking for, or ""."""
    found = BARE_MINE.match(str(low or "").strip(" .!?;,"))
    if not found:
        return ""
    words = set(found.group(1).split())
    slot = _slot_named_in("my " + found.group(1))
    if not slot or not _slot_held(slot, memory):
        return ""
    if words - SLOT_NOUNS.get(slot, frozenset()) - SLOT_FILLER:
        return ""  # the line says something about the fact, so it is not only naming it
    if slot == "pets":
        # "my cat?" is about a cat, so a store that only holds a dog has nothing to say to it -
        # the answer would be about the dog they did tell us about.
        named = words - SLOT_FILLER - {"pet", "pets", "animal", "animals"}
        held = set()
        for pet in (user(memory) or {}).get("pets") or []:
            if isinstance(pet, dict):
                held |= forms(str(pet.get("animal") or ""))
        if named and not any(forms(one) & held for one in named):
            return ""
    return slot


PLACES_ASK = re.compile(
    r"\b(?:which|what) (?:city|place|country|town)\b"
    # The words people use for a place without naming a city: "what area do i live in", "what
    # part of the country do i live in". These are only a place ask when the line goes on to ask
    # about the person, so "what area of my flat needs painting" is not one.
    r"|\b(?:which|what) (?:area|suburb|neighbourhood|neighborhood|county|village|"
    r"part of (?:the|this) country) (?:of (?:the|this) (?:country|city|town) )?"
    r"(?:do|does|did|am|was|are|were) (?:i|we)\b"
    r"|\b" + WHERE_ASK + r" (?:am|was) i (?:going|from|living)\b(?! with\b)|"
    r"\bmy hometown\b|\b" + WHERE_ASK + r" am i from originally\b|"
    r"\b" + WHERE_ASK + r" (?:was|were) (?:i|we) born\b|\b" + WHERE_ASK + r" are (?:i|we) from\b|"
    r"\b" + WHERE_ASK + r" do (?:i|we) (?:live|come from)\b|\b" + WHERE_ASK + r" are we "
    r"(?:living|based)\b|"
    r"\b" + WHERE_ASK + r" (?:do|does) my \w+ (?:live|come from)\b|"
    r"\b" + WHERE_ASK + r" is my \w+ (?:living|based)\b|"
    # Where they grew up is a place ask, whether it is said with "from" or with the growing up:
    # "where did i grow up" is answered by the place the line gave ("i grew up in dublin"), which
    # the extractor files as where they are from.
    r"\bwhere (?:did|do|does) (?:i|we) (?:grow|grew|grown) up\b|"
    r"\bwhere (?:was|were) (?:i|we) (?:raised|brought up|brung up)\b|"
    r"\bwhere did (?:i|we) (?:live|grow up) (?:before|originally|as a kid|as a child|growing up)\b|"
    # The move said as a move: "where did i move from" asks the same fact as "where am i from",
    # and it was answered with a search hedge. It is asked this way after "i moved to preston
    # last year" - the line names only the destination, so the origin is the question.
    r"\bwhere (?:did|do|does) (?:i|we) (?:move|moved) (?:here |over |away )?from\b|"
    # And the move named with the destination in the question: "which town did i move from".
    r"\b(?:which|what) (?:city|town|place|county|country) did (?:i|we) move (?:from|away from)\b")


SELF_WORD = re.compile(r"\b(?:i|i'm|im|i've|ive|i'd|id|me|my|mine|we|we're|us|our|ours)\b")


PLACE_ADVICE = re.compile(
    r"\b(?:should|shall|recommend\w*|worth|visit\w*)\b"
    r"|\bbest (?:place|city|country|town|part)\b")


PLACE_RECALLED = re.compile(
    r"\b(?:did i (?:say|tell|mention)|i (?:said|mentioned|told)|remember|again)\b")


GROWN_UP_ASK = re.compile(
    r"\b(?:grow|grew|grown) up\b|\b(?:raised|brought up|brung up)\b"
    r"|\bwhere (?:i|we) (?:lived|was living|were living)\b")


FEELING_ALONE = re.compile(
    r"^(?:and |but |so |also |honestly |yeah |yes |god |oh |well |still |im |i'm |i am |i feel"
    r"|i just feel |feel |im just |im getting |getting |a bit |really |very |quite |so )*"
    r"(scared|nervous|worried|anxious|terrified|petrified|frightened|panicking|dreading|dreading it)"
    r"(?: (?:about it|of it|about that|about this|about the whole thing|now|today|already"
    r"|honestly|a lot|so much|quite a lot|tbh|tbf|again|about it now"
    r"|for (?:him|her|them|it|us|you)))?$", re.I)


COMING_UP = re.compile(
    r"\b(?:tomorrow|tonight|later today|this (?:morning|afternoon|evening|week|weekend|month)"
    r"|next (?:week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend)"
    r"|on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"|at the weekend|in (?:january|february|march|april|may|june|july|august|september|october"
    r"|november|december)|soon|in a (?:few|couple of) (?:days|weeks))\b", re.I)


A_DAY = re.compile(
    r"\b(?:tomorrow|tonight|later today|this (?:morning|afternoon|evening|weekend)"
    r"|next (?:week|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend)"
    r"|on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|at the weekend)\b", re.I)


def _is_a_question(previous):
    if previous.rstrip().endswith("?"):
        return True
    try:
        return understand(previous).get("kind") == "question"
    except Exception:  # noqa: BLE001 - an unreadable line is not this rule's business
        return True


TREATMENT = re.compile(
    r"\b(?:chemo|chemotherapy|radiotherapy|radiation therapy|dialysis|biopsy|palliative|hospice"
    r"|terminally ill)\b", re.I)


A_PERSON_IN_TROUBLE = re.compile(
    r"\b(?:my|our)\s+(?:" + KIN + r")\b(?:'s|s)?[^.?!]*?\b(?:" + BAD_NEWS + r")\b", re.I)


WHO_IS_IN_TROUBLE = re.compile(r"\b(?:my|our)\s+((?:" + KIN + r"))\b", re.I)


SHE = frozenset("""mum mom mother daughter wife sister gran granny nan nana grandma grandmother
                   aunt niece stepdaughter""".split())


HE = frozenset("""dad father son husband brother grandad grandpa grandfather uncle nephew
                  stepson""".split())


def _again(who):
    """The word for the person in the rest of the reply: "her", "him" or "them"."""
    word = str(who or "").lower()
    if word in SHE:
        return "her"
    if word in HE:
        return "him"
    return "them"


def _the_thing_before_the_feelings(memory):
    """The last line they said that was not itself a bare feeling.

    "im nervous", "im scared", "im terrified" in a row are all about the one thing said before
    them, so each of them looks past the feelings in between. Reading the feelings as news would
    make the second and third fall back to the general worry line.
    """
    seen = 0
    for turn in reversed((memory.get("turns") or [])[-6:]):
        if not isinstance(turn, dict):
            break
        line = str(turn.get("user") or "").strip()
        if not line:
            continue
        if FEELING_ALONE.match(line.lower().rstrip("!.,")):
            continue
        seen += 1
        if seen > 1:
            # Only the nearest real thing they said is the subject: two feelings about two
            # different things belong to the nearest one.
            break
        return line
    return ""


OPENS_ON_THE_SENTENCE = re.compile(
    r"^(?:of course|of course you are|that\b|this\b|those\b|these\b|such\b"
    r"|(?:nerves|worry|worrying|fear|stress|panic) about it\b)", re.I)


def _said_back_already(reply, said):
    """True when a bot line already carried this sentence's own subjects.

    The last two lines, not one: `im so nervous` / `im scared` / `im terrified` about the same
    test gives a body with no sentence in front of it on the second, so the third looked at
    the line just above, saw a body, and read the test back a second time.
    """
    words = {w for w in keywords(said) if len(w) > 3}
    if not words:
        return False
    return len(words & {w for w in keywords(reply) if len(w) > 3}) >= max(2, len(words) - 1)


def _the_bot_name(memory, low):
    """The name they gave the bot, said back when they ask for it, or None.

    Nothing here without a name on file: a chat where the person never named the bot keeps the
    reply it already had ("I don't have one - pick something if it helps").
    """
    known = str(user(memory).get("bot_name") or "").strip()
    if not known or not extract.BOT_NAME_ASK.search(low):
        return None
    return pick(["You call me " + known + ".", known + " \u2014 you named me that.",
                 "I'm " + known + ", since you named me."], memory)


LOOK_BACK_ANSWER = 3


def _turned(question):
    words = str(question or "").rstrip(" ?!.").split()
    said = " ".join(TURNED.get(word.lower(), word) for word in words)
    # The understanding writes "what is the pay" out in full; said back to them it reads stiff.
    for long_form, short in (("what is the", "what's the"), ("what is it", "what is it"),
                             ("it is", "it's"), ("you are", "you're"),
                             ("where is the", "where's the")):
        said = re.sub(r"\b" + long_form + r"\b", short, said)
    return said


def _a_choice_from_what_was_said(line, memory):
    """"which one?" after a recommendation, when the last answer has a pick in it.

    A bare "which one" is the one ask back that is not warm here: the person is asking us to
    choose between the things we just recommended, and the answer is a part of that answer, not
    a request to say which one they mean. It declines unless the answer really does have a pick
    to give, so a "which one" with nothing behind it keeps the ask back it had before.
    """
    try:
        from ..modules.answers import CHOICE_ASK, _the_one_to_pick
    except Exception:  # noqa: BLE001 - a reading that cannot be imported declines nothing
        return False
    clean = " ".join(str(line or "").lower().split())
    if not CHOICE_ASK.match(clean):
        return False
    try:
        return bool(_the_one_to_pick(clean, memory))
    except Exception:  # noqa: BLE001 - a pick that cannot be made declines nothing
        return False


def _holds_nothing(known):
    return not any(known.get(key) for key in PART_KEYS)


def _a_thing_it_keeps(memory, mine):
    """The rows of the store a possessive names, or None when the chat has been told nothing."""
    known = user(memory)
    if _holds_nothing(known):
        return None
    key = PART_HELD.get(str(mine or "").lower())
    if key is None:
        return None
    if key == "people":
        return key if (known.get("people") or known.get("others")
                       or known.get("kids")) else None
    if key == "city":
        return key if (known.get("city") or known.get("home")
                       or known.get("places")) else None
    return key if known.get(key) else None


def _a_kept_thing_behind(memory):
    """True when the nearest thing they said about themselves is a fact the store keeps.

    The line this reader answers leans back on that fact ("there" after "i work at a cafe" is
    the job, "it" after "i drive a ford" is the car), so which fact was said decides whether the
    store can be asked about a part of it.
    """
    from bot.memory import facts as kept

    for turn in reversed(recent(memory, 5)):
        said = str(turn.get("user") or "").strip()
        if not said or said.endswith("?"):
            continue
        if not re.search(r"\b(?:i|we|my|our|im|ive)\b", said.lower()):
            continue
        try:
            found = kept.extract(said)
        except Exception:  # noqa: BLE001 - a line that cannot be read keeps the old answer
            return False
        if not isinstance(found, dict):
            return False
        if any(found.get(key) for key in KEPT_THINGS):
            return True
    return False


def _yes_then(reply):
    """The fact with a yes in front of it, "you" still lower case after the dash."""
    text = str(reply or "").strip()
    if re.match(r"^(?:You|Your|It)\b", text):
        text = text[:1].lower() + text[1:]
    return "Yes \u2014 " + text


def _same(left, right):
    return " ".join(str(left).lower().split()) == " ".join(str(right).lower().split())


def _their_allergy(who, theirs):
    """Someone else's allergy, said back with whose it is: a no about the person asked about."""
    return ("You haven't told me one \u2014 the allergy to " + ", ".join(theirs)
            + " is your " + who + "'s, not yours.")


def _names(key, text):
    pattern = NAMED_BY.get(key)
    return bool(pattern) and bool(re.search(pattern, text))


def _someone_said_back(said, memory):
    """The fact about someone else that the framed statement just gave, said back."""
    words = " ".join(str(said or "").lower().split())
    if not words:
        return None
    found = extract.extract(said) or {}
    said_about = [other for other in (found.get("others") or []) if isinstance(other, dict)]
    for entry in others(memory):
        if not isinstance(entry, dict):
            continue
        who = str(entry.get("who") or "").strip().lower()
        if not who or not re.search(r"\b" + re.escape(who) + r"\b", words):
            continue
        if "name" in entry:
            called = _called(str(entry.get("name") or "").strip())
            if called:
                return "Your " + who + " is called " + called + "."
            continue
        # A figure said about someone in the frame is said back the same way, so the receipt is
        # not "there's nothing on your son" about the age just filed against him: "can you
        # remember my son is 7" is "Your son is 7."
        age = entry.get("age")
        if age in (None, "", [], {}):
            continue
        given = [other.get("age") for other in said_about
                 if str(other.get("who") or "").lower() == who]
        if str(age) in [str(one) for one in given]:
            return "Your " + who + " is " + str(age) + "."
    return None


# A category of food, and the words people use for it. Only a category is read: "do i eat
# halloumi" is a question about a food and the kitchen entries answer it, while "do i eat meat"
# is a question about the rule they gave the store.
FOOD_CATEGORIES = (
    ("meat", ("meat", "chicken", "beef", "pork", "lamb", "bacon", "ham", "sausage", "sausages",
              "steak", "mince", "turkey", "burger", "burgers", "veal", "venison")),
    ("fish", ("fish", "salmon", "tuna", "prawn", "prawns", "shellfish", "cod")),
    ("dairy", ("dairy", "milk", "cheese", "butter", "cream", "yoghurt", "yogurt")),
    ("eggs", ("egg", "eggs")),
    ("gluten", ("gluten", "wheat", "bread", "pasta", "flour")),
    ("nuts", ("nut", "nuts", "peanut", "peanuts")),
    ("alcohol", ("alcohol", "beer", "wine", "booze", "spirits", "cider")),
)


# What each rule the store keeps takes off the table. The diet is its own words ("vegetarian",
# "no alcohol"), an allergy names the food, and a condition names what it rules out: the reader
# asks this table instead of guessing from the words of the line.
A_DIET_RULES_OUT = {
    "vegetarian": ("meat",),
    "vegan": ("meat", "fish", "dairy", "eggs"),
    "pescatarian": ("meat",),
    "no meat": ("meat",),
    "no dairy": ("dairy",),
    "dairy free": ("dairy",),
    "dairy-free": ("dairy",),
    "gluten free": ("gluten",),
    "gluten-free": ("gluten",),
    "no alcohol": ("alcohol",),
}


A_CONDITION_RULES_OUT = {
    "coeliac": ("gluten",),
    "celiac": ("gluten",),
    "coeliac disease": ("gluten",),
    "lactose intolerant": ("dairy",),
}


def _old_values(memory, told):
    """The words of the line before the correction that a correction could have swapped out.

    The plan is kept as the phrase the person used ("Portugal in june"), so its words are the
    candidates: a month or a day is a value of the fact and is said back by the note alone
    ("make that july"), and the filler words are not values at all.
    """
    out = []
    entries = memory.get("facts_log")
    if not isinstance(entries, list):
        return out
    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        if " ".join(str(entry.get("text") or "").lower().split()) != told.lower():
            continue
        if entry.get("key") not in SWAPPABLE:
            continue
        for word in re.split(r"[\s,]+", str(entry.get("value") or "")):
            low = word.lower().strip("'-.!?")
            if (len(low) > 2 and low not in MONTHS and low not in extract.DAYS
                    and low not in STOPWORDS and low not in out
                    and re.search(r"\b" + re.escape(low) + r"\b", told, re.I)):
                out.append(low)
    return out


def _a_figure(word):
    """True when the value is a number rather than a word of the sentence ("100", "2k", "1,500")."""
    return bool(re.fullmatch(r"\d[\d,]*(?:\.\d+)?\s*(?:k|grand|thousand|pounds?|quid)?",
                             str(word or "").strip(), re.I))


def _swapped_lines(memory, fixed):
    """The lines the person would have said if they had said it right the first time."""
    if not isinstance(fixed, dict):
        return []
    if fixed.get("dropped"):
        # Nothing took the value's place, so there is no line they "would have said" and nothing
        # to answer about it: the note that it is gone is the whole of this turn.
        return []
    value = str(fixed.get("value") or "").strip()
    said = last_user(memory, 3) or []
    if isinstance(said, str):
        said = [said]
    # The correction line itself is the newest turn on some paths and not yet recorded on
    # others, so the line before it is the newest one that is not the correction.
    mine = " ".join(str(fixed.get("said") or "").lower().split())
    said = [x for x in said if " ".join(str(x).lower().split()) != mine]
    told = " ".join(str(said[-1] if said else "").split())
    if not value or not told:
        return []
    out = []
    moved = _the_time_that_moved(told, fixed, value)
    if moved:
        # The time is the one value in the sentence that cannot be added beside the old one -
        # "im going to lisbon in June in may" is still a line about May - so the corrected
        # sentence is the only one they could have said.
        return [moved]
    olds = _old_values(memory, told)
    if _a_figure(fixed.get("from")) and _a_figure(value):
        # The thing corrected is the figure in the line and the new thing is a figure too, so the
        # figure is what moves. Swapping a *word* of it instead leaves the old number standing
        # beside the new one - "i want to save 200 a month" / "actually make it 100" gave "i want
        # to Save 100 a month 200 a month" - and that line reads as two rates with a sum between
        # them: answers took the 200 as the goal and said "£200 at £100 a month is 2 months."
        olds = [old for old in olds if _a_figure(old)]
    out.extend(re.sub(r"\b" + re.escape(old) + r"\b", value, told, count=1, flags=re.I)
               for old in olds)
    # A figure of the line before, changed rather than a word of it ("make it 75 instead" after
    # "i can put away 50 a month"): the line they would have said is that one with the new figure
    # in it, and it is what the answer to their correction is about (bot/memory/resize.py).
    resized = resize.rewritten(str(fixed.get("said") or ""), memory)
    if resized:
        out.append(resized)
    out = [line for index, line in enumerate(out) if line not in out[:index]]
    if _a_figure(fixed.get("from")) and re.search(r"\d", value):
        # A line that still carries the figure the person replaced has not been corrected at all,
        # and read as the line they "would have said" it names both figures: "i want to Save 100
        # a month 200 a month" is two rates with a sum between them, which is how a corrected
        # amount became the goal of £200 nobody had named.
        gone = re.compile(r"\b" + re.escape(str(fixed["from"]).replace(",", "")) + r"\b")
        out = [line for line in out if not gone.search(line.replace(",", ""))]
    return out


def _the_time_that_moved(told, fixed, value):
    """The line they would have said, when what they corrected is the month or the day in it.

    "i'm going to lisbon in may" and "sorry, june" keeps Lisbon and moves the time, so the line
    they would have said is the one before with June where May was. The generic swap takes the
    words of the stored phrase instead, and on a plan kept as "Lisbon in June" that put both
    months in one line - "i'm going to Lisbon in June in may" - which the answers then read as
    May, so a June trip was given the May advice.
    """
    wrong = str(fixed.get("from") or "").strip()
    relative = RELATIVE_MONTH.fullmatch(wrong) if wrong else None
    if relative is not None:
        # The date taken back was said in relative words, so the month they name now is what
        # goes in its place: "im going to rome next month" and "no in july" is the line they
        # would have said. Put the value in whole instead and the plan gathers both dates
        # ("rome in July next month"), which the answers then read as next month.
        day, month = _date_said(str(fixed.get("value") or "").lower())
        if not month or not re.search(r"\b" + re.escape(wrong) + r"\b", told, re.I):
            return None
        said = _date_word_case(month)
        said = ("on the {day} of {said}".format(day=day, said=said) if day else "in " + said)
        return re.sub(r"\b" + re.escape(wrong) + r"\b", said, told, count=1, flags=re.I)
    was, now = _date_word(wrong), _date_word(value)
    if not was or not now or was.lower() == now.lower():
        return None
    # Only within one family: a month moves for a month and a day for a day. "on monday" and
    # "make that june" are two different things said about a fact, not one value moving.
    if (was.lower() in MONTHS) != (now.lower() in MONTHS):
        return None
    if not re.search(r"\b" + re.escape(wrong) + r"\b", told, re.I):
        return None
    return re.sub(r"\b" + re.escape(wrong) + r"\b", now, told, count=1, flags=re.I)
