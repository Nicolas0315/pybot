"""Part 13 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import fallback, pick
from ..compose.badnews import reads_like_a_symptom
from ..understanding.kinds import verdicts_a_thing
from ..compose import loss as loss_reading
from ..compose import harm as harm_reading
from ..compose import saidby as saidby_reading
from ..memory import about

from ..memory import ack
from ..memory import stuck as stuck_line
from ..memory import thread

from ..memory import meant
from ..knowledge import lookup
from ..understanding import understand as understanding
from .chat_part_01 import (
    ASKS_ALOUD, JOKE_ADVICE, JOKE_ASK, JOKE_ASKED, PICK_WORDS, RUNTIME_LIMIT, WANTS_A_THING, JOKES,
    SHORT_JOKES,
)
from .chat_part_03 import (
    _fond_of_the_bot, TIRED_PERSISTENT,
)
from .chat_part_04 import (
    REPLIES,
)
from .chat_part_05 import (
    AGAIN_ONLY, BUSY_RE, BUSY_WORK, LOOKING_FORWARD, NOT_AGAIN, PLAN_RE, PLAN_STOP, PLAN_TROUBLE,
    PLAN_WORRY, SORRY_TALK, VAGUE_WORDS, _a_care_turn, _a_forecast, _a_trip, _overloaded,
    FEELING_THING, FEELING_WANT, LEAVE_SOMEONE, SAYS_NOTHING, STOPS_TOGETHER, _name,
)
from .chat_part_06 import (
    SYMPTOM,
)
from .chat_part_07 import (
    MIGHT_BE,
)
from .chat_part_10 import (
    _stuck,
)
from .chat_part_11 import (
    _a_pick_is_in_hand, ASK_TAIL, A_DOUBT_ABOUT_IT, A_HOPELESS_THOUGHT, A_THOUGHT_ABOUT_OTHERS,
    A_THOUGHT_THAT_IS_NOT_A_THING, INTENTION, KEEPS, KEEPS_SYMPTOM, KEEP_ABOUT_SOMEONE,
    KEEP_A_BELIEF, KEEP_INTENT, MEDICINE, NEED_NOW, QUESTION, THING_SKIP, TIME_TAIL, WANT,
    _last_was_joke,
)
from .chat_part_12 import (
    _feeling, ALWAYS, ASK_KIND, A_BREAK_FROM_SOMEONE, BARE_FEELING, CHOOSING, CONTINUING, DECISION,
    DOING, INDEFINITE, INDEFINITE_SKIP, KINDLESS, LEAVE, ONE_OFF, PAIN_PART, PERSON_WORK, RELATIVE,
    STATE, TASK_ONLY, THING_REPLIES, _A_NEED_ASK, _A_PERSON_ALREADY_IN_THE_LINE,
    _PERSON_IN_THE_TAIL, _answers_knows, _in_loss, _kindless, _reply, _without_a_filler_tail,
)


def _short_talk(clean, tokens, memory):
    """A short line with something in it but no question, read by what it carries."""
    if not tokens or len(tokens) > 12 or "?" in clean:
        return None
    flat = " ".join(tokens)
    if _a_trip(flat, memory):
        return None
    if set(tokens) <= AGAIN_ONLY and "again" in tokens:
        # "not again", "oh no, not again" and "no not again" say in the words themselves that
        # the repeating is the trouble. A bare "again" does not, so it is asked: sympathy
        # assumed for good news ("i got engaged" / "again") is the bot reading a worse week
        # than the person described.
        return "again" if set(tokens) & NOT_AGAIN else "again_what"
    if flat in LOOKING_FORWARD:
        # A good thing said in the turn after bad news is the timing that is wrong, not the
        # line: the glad pool waits until the thread has room for it.
        return None if _a_care_turn(memory) else "keen"
    if SORRY_TALK.search(flat):
        return "sorry_talk"
    words = set(tokens)
    if BUSY_RE.search(flat) and words & BUSY_WORK:
        return "busy"
    # After the busy pool, so a load it already sees keeps its answer; this is the ground it
    # cannot see, where the line names the run of it and no feeling word at all.
    if _overloaded(flat, memory):
        return "overloaded"
    if "everything at once" in flat or "one thing after another" in flat:
        return "busy"
    if len(tokens) <= 8 and words <= VAGUE_WORDS and (
            "everything" in words or ("those" in words and "one" in words)
            or ("dont" in words and "know" in words)):
        # Unless the bot has just named a first step: "i want to start running", then "i dont know
        # where to start", is asking for that step, and "Sometimes it's everything at once. It can
        # stay unnamed." answers a question nobody asked. Standing down here lets the answer come
        # back as the step it already was.
        if stuck_line._the_answer_gave_a_step(memory):
            return "plan" if PLAN_RE.search(flat) and not words & PLAN_STOP else None
        return "vague"
    # The plan reading reads the line through the same strip as the feeling reader: a modal in
    # front of a feeling is the feeling, and a plan may not answer it. `flat` is built from the
    # words as typed, so without this "i think i might be exhausted from work" still matched here
    # after `_respond` had rewritten the line, and the plan pool took the turn back.
    if fallback.reads_as_a_change_of_medicine(_without_the_might(flat)):
        # A plan that changes a medicine is not a plan of the day, and it is not blessed. The
        # dose waits for the person who prescribes it, so the pool that says that answers here
        # rather than the cheerful one - it is also the reason the reading is above the trouble
        # check, because "im going to stop my inhalers now the hay fever has gone" is the same
        # decision whether or not something in the line sounds like a worry.
        return ("plan_medicine_slow" if fallback.PLAN_MEDICINE_SLOW.search(flat)
                else "plan_medicine")
    if (PLAN_RE.search(_without_the_might(flat)) and not words & PLAN_STOP
            and not PLAN_WORRY.search(flat) and not PLAN_TROUBLE.search(flat)
            and not _a_forecast(memory)):
        return "plan"
    return None


def _without_the_might(clean):
    """The line with a modal in front of a stated feeling taken off, or the line unchanged.

    The test for "is this a feeling" is the feeling reader itself, asked about the state on its
    own ("im depressed", "im low"): a word it answers is a feeling, one it passes on ("im late",
    "im fine") keeps the reading it had.
    """
    def put(match):
        state = match.group("state").lower()
        if not _feeling("im " + state):
            return match.group(0)
        return "im " + state
    with_states = MIGHT_BE.search(clean)
    return MIGHT_BE.sub(put, clean, count=1) if with_states else clean


def _asks_for_a_joke(clean, tokens, memory=None):
    """True when the line wants a joke, not a pick from the telly, the shelf or the player.

    "tell me a joke about cheese" and "say something funny" want a joke. "recommend something
    funny to watch tonight" wants a film, and a joke there drops the request, so the pick is
    left to the module that answers it (or to the fallback) instead. The medium can be the one
    the chat is already on: "im in the mood for something funny" after the films.
    """
    if (WANTS_A_THING.search(clean) and not ASKS_ALOUD.search(clean)
            and _a_pick_is_in_hand(memory)):
        return False
    if JOKE_ADVICE.search(clean):
        return False  # asked about a joke, not for one
    if SELF_JOKE.search(clean):
        return False  # "im a joke to everyone" is what they say they are, not a request
    if _fond_of_the_bot(clean):
        return False  # "you cheer me up" says what the bot already did; it is not an ask
    if JOKE_ASKED.search(clean):
        return True
    if RUNTIME_LIMIT.search(clean):
        return False  # a length belongs to a film: "something funny under two hours"
    if not JOKE_ASK.search(clean):
        return False
    return not (set(tokens) & PICK_WORDS)


# Words that say how much, how often or in what manner, not what the line is about. "i want to
# learn to cook more" names cooking; "more" is not the thing, and it is the word that reached the
# memorise-these-faster entry. The verbs are here too, because "start", "keep" and "build" are in
# the habit entries' own keys, so a line about anything at all would look like an overlap.
GENERIC_THING_WORDS = frozenset("""more better best thing things stuff a an the to of it my me
i we you want wanted need needs get gets got make makes made do does did keep keeps keeping
keep learning learn start starting started go going up down on off for with and but so
again really quite very lot bit time times""".split())


# "i keep forgetting things" named its own verb: the memorise-this-faster entry is about
# revision, and it matched on "forgetting" once the "keep" was read away. Two words are the same
# verb when they agree once the ending and the doubled consonant are off, so "forgetting",
# "forget" and "forgot" are one word and none of them can be what the line is about.
_VERB_ENDINGS = ("ing", "ed", "es", "s", "e", "en", "t")


def _verb_stem(word):
    """A word with its verb ending off, so "forgetting", "forgot" and "forget" agree."""
    word = str(word or "").lower().strip("'")
    if word.endswith("ied"):
        word = word[:-3] + "y"
    for ending in _VERB_ENDINGS:
        if len(word) > len(ending) + 2 and word.endswith(ending):
            word = word[:-len(ending)]
            break
    if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "aeiou":
        word = word[:-1]
    return word


def _answers_is_about_the_thing(text, thing, memory, verbs=()):
    """True when the knowledge base's best entry is about the thing this line named.

    The chat module's stock replies ("start with the smallest version of it", "is it the same
    every time") are about whatever the person named, so a knowledge answer about that same
    thing is the better turn: "i want to build better habits" is the habit-building tips and
    "i keep starting and stopping" is never-miss-twice.

    An entry that matched on a word which says nothing about the thing is not that answer:
    "i want to learn to cook more" reached the memorise-these-faster entry on "learn" and
    "more", and it names cooking, so the first-step reply keeps the turn.
    """
    try:
        from ..knowledge.lookup import find
        from ..understanding import understand
        # A copy of the memory: the understanding engine writes its reading of the line into
        # `memory["understood"]`, and this is a question about the knowledge base, not a second
        # reading of the turn that the rest of the pipeline should see.
        scratch = dict(memory) if isinstance(memory, dict) else {}
        entry = find(understand(text, scratch))
        if entry is None:
            return False
        said = set()
        for part in (entry.key or ()):
            for piece in (part if isinstance(part, tuple) else (part,)):
                said.update(re.findall(r"[a-z']+", str(piece).lower()))
        # A key phrase of three words or more that is in the line is the thing itself, whatever
        # its verb: "keep putting things off" is the whole of "i keep putting things off", so the
        # procrastination entry is about what was said even though "putting" is the line's verb.
        # Shorter phrases ("keep forgetting") are the shape of the line, not its subject.
        line = " " + " ".join(str(text or "").lower().split()) + " "
        for part in (entry.key or ()):
            for piece in (part if isinstance(part, tuple) else (part,)):
                piece = " ".join(str(piece).lower().split())
                if piece.count(" ") >= 2 and piece in line:
                    return True
        stems = {_verb_stem(verb) for verb in verbs if verb}
        for word in re.findall(r"[a-z']+", str(thing or "").lower()):
            if word in GENERIC_THING_WORDS or _verb_stem(word) in stems:
                continue
            if word in said or word[:-1] in said or word + "s" in said:
                return True
        return False
    except Exception:  # noqa: BLE001 - a knowledge miss must not stop the chat module
        return False


# The words a how-question is made of rather than about. What is left of the thing has to be in
# the entry's key, every word of it: an entry that answers half of it answers something else.
_HOW_STOP = frozenset("""a an the my our your his her their its some any to for of on in at with
and or but so i we you it that this these those there do does did how what where when why please
just really properly better best more most myself yourself""".split())


def _answers_has_the_how(thing, memory):
    """True when "how do i <thing>" reaches an entry whose key covers every content word of it.

    "i need to make room on my mac" is the Mac storage steps said as a want, and a plan to start
    it is a reply about the wrong thing. A near miss is not: "i need to learn to drive" reaches
    the memorise-faster entry, which names no driving, so it keeps the plan rather than an answer
    about revising.
    """
    try:
        from ..knowledge import lookup
        from ..understanding import understand
        found = lookup.find(understand("how do i " + thing))
        if found is None:
            return False
        content = {word for word in re.findall(r"[a-z']+", thing.lower())
                   if word not in _HOW_STOP and len(word) > 1}
        return bool(content) and content <= lookup.key_words(found)
    except Exception:  # noqa: BLE001 - a knowledge miss must not stop the chat module
        return False


def _fallback_has_its_own_pool(text):
    """True when the fallback already has a named pool for this line.

    A kept habit ("i keep losing my keys") is answered by a pool of real advice - give the keys
    one home, one diary for the birthdays - and a line about it must not be turned into a stock
    question about how often it happens. The pools live in the fallback, not in the knowledge
    base, so `_answers_knows` does not see them.
    """
    from ..compose import fallback as compose_fallback
    from ..compose import loss as compose_loss
    plain = " ".join(str(text or "").lower().split())
    try:
        if compose_loss.keeps_losing_thing(plain):
            return True
        for pattern in (compose_fallback.FORGET_A_DATE, compose_fallback.FORGET_A_SECRET,
                        compose_fallback.FORGETS_A_CLASH, compose_fallback.FORGETS_AGAIN):
            if pattern.search(plain):
                return True
        return compose_fallback._is_rumination(plain)
    except Exception:  # noqa: BLE001 - a fallback change must not stop the chat module
        return False


def _the_words_they_meant(clean, understood):
    """The line as the person meant it, when the understanding repaired it.

    "i want 2 go home" was answered "2 go home \u2014 fair enough. What's stopped it happening so
    far?", and "i want 2 get fit" the same: the chat table already reads a "2" after a verb as
    "to" and a spelling like "thinkin" as thinking, and this pool was cutting the thing out of
    the line as typed, so the digit and the typo were handed straight back to the person. The
    repair is the understanding's own (`plain`), not a second list here, so a digit that is a
    count keeps it: "i want 4 cats" and "i want 2 eggs" are still four cats and two eggs.
    """
    plain = understood.get("plain") if isinstance(understood, dict) else None
    plain = " ".join(str(plain or "").lower().replace("\u2019", "'").split())
    if not plain or plain == clean:
        return clean
    typed, meant = clean.split(), plain.split()
    if len(typed) != len(meant):
        return clean
    for was, is_ in zip(typed, meant):
        if was == is_:
            continue
        # A digit read as its word ("2" is "to" after a verb, "4" is "for"), or a spelling
        # repaired into the word it was reaching for ("thinkin" -> "thinking"). Anything else is
        # a different line: "whats a quick meal" becomes "what is a quick meal", which is a
        # different key for the knowledge base, and this pool must not change what answers.
        if was in ("2", "4") or was.startswith(is_) or is_.startswith(was):
            continue
        return clean
    return plain


def _their_thing(clean, tokens, memory, understood=None):
    """A reply about the thing the person named, or None when the line names nothing."""
    from ..compose import fallback as compose_fallback
    clean = _the_words_they_meant(clean, understood)
    if clean.endswith("?") or not 3 <= len(tokens) <= 16:
        return None
    if QUESTION.match(clean) or THING_SKIP.search(clean):
        return None
    if MEDICINE.search(clean):
        return None
    # A death or a real loss is not a thing to plan around: "and i keep crying at nothing" after
    # a bereavement belongs to the loss reading, which has the right reply, and so does anything
    # said in a conversation where someone died.
    if loss_reading.reads_as_loss(clean) or _in_loss(memory):
        return None
    # A want with a person on the other end of it is not a project to get on with: "i want to
    # kill my boss" was answered "Worth doing. What would you like help with first?" and "i want
    # to punch my brother" "Punch your brother - fair enough". The anger behind it is what can be
    # answered, so the harm reading says the one plain thing and asks about that.
    if harm_reading.reads_as_hurting_someone(clean):
        return harm_reading.reply_for(clean, memory)
    # The same for a quoted wish one step further down: "she texted me \"we need to talk\" and
    # nothing else" was answered "Talk\" and nothing else \u2014 fair enough. What's stopped it
    # happening so far?", which says half a quotation back with a stray quote mark in it and asks
    # about a plan nobody in the line is making.
    quoted = saidby_reading.reply_for(clean, memory)
    if quoted:
        return quoted
    # A line that puts a clock time on being somewhere ("i need to be at work for 8", "i have to
    # be at the airport for 6am") is a morning to plan, not a thing the person is failing to get
    # on with: "Be at work for 8 - fair enough. What's stopped it happening so far?" is a coach's
    # question about something somebody has been avoiding, and the answer that helps works back
    # from the time instead. The composer has that pool, so this stands down (tiny-bluebell,
    # #routing 81689).
    if compose_fallback._the_morning_has_a_clock(clean):
        return None
    # A line that asks something ("i need to do compressions, how many", "i need a new bath,
    # any tips") is an ask, not a statement about a thing: the answers module or an honest
    # "I don't know" is a better reply than a plan for the thing named.
    if ack.WANTS_ANSWER.search(clean) or ASK_TAIL.search(clean):
        return None
    # "i want to start running but my knees hurt" names a want and a snag, and the reply that is
    # already there (sympathy, then an offer) beats a plan that talks past the knees.
    if " but " in " " + clean + " ":
        return None
    # "... without burning bridges" asks how to do the thing and keep something else, and the
    # answer domain has the real answer for it, so the line passes rather than getting a plan.
    if " without " in " " + clean + " ":
        return None
    flat = clean.replace("\u2019", "'").strip(" .,!;:")
    verbs = ()
    for kind, pattern in (("intention", INTENTION), ("want", WANT), ("always", ALWAYS),
                          ("keeps", KEEPS)):
        match = pattern.search(flat)
        if not match:
            continue
        if kind == "keeps":
            # A thought whose subject is "it" or the speaker has no thing in it to plan, so the
            # plan reading stands down (see KEEP_A_BELIEF).
            said = (match.group(2) or "").strip()
            if match.group(1).lower() in KEEP_A_BELIEF and A_THOUGHT_THAT_IS_NOT_A_THING.match(said):
                if A_HOPELESS_THOUGHT.search(flat):
                    return pick(REPLIES["not_coping"], memory)
                if (A_THOUGHT_ABOUT_OTHERS.match(said)
                        or A_DOUBT_ABOUT_IT.search(said)):
                    return None
                # A fact about the day ("its friday", "its bin day") keeps the plan reading: it is
                # not a thought that keeps coming back, and the worry pool would invent one.
            if match.group(1).lower() in KEEP_INTENT:
                kind = "want"
                thing = (match.group(2) or "").strip()
            else:
                verbs = (match.group(1),)  # "forgetting" is the line's own verb, not its thing
                thing = (match.group(1) + " " + (match.group(2) or "")).strip()
        else:
            thing = match.group(1).strip()
        # A purpose clause is part of the goal, not a word to cut the thing at: "i want to
        # save up so that i can move out" is a how question for the answers module, and cutting
        # at "so" turned it into a bare "save up" plan.
        if re.search(r"\bso that\b|\bso (?:i|we) (?:can|could|will|would)\b", flat):
            return None
        thing = re.split(r"\b(?:because|but|so|though|although)\b", thing)[0].strip(" ,;:")
        thing = TIME_TAIL.sub("", thing).strip(" ,;:")
        # A want whose thing starts with a feeling word ("disappear", "give up", "hurt") is
        # the feeling's line, not a project: the same test the older intent read makes. Leaving
        # a partner is not a thing to get on with either.
        first = (thing.split() or [""])[0]
        if thing.lower() in BARE_FEELING:
            return pick(REPLIES["not_coping"], memory)
        if (first in FEELING_THING or FEELING_WANT.search(thing)
                or LEAVE_SOMEONE.search(thing)
                or thing.lower() in CONTINUING):
            return None
        # A wish for something to stop or change is not a thing to start: see `STOPS_TOGETHER`.
        # Where the subject names nothing ("it", "this", "everything"), the person is the subject
        # and the line about them is the reply; where it names the thing that is wrong ("the
        # pain", "these comments"), the turn goes to whichever module answers that thing.
        stopping = STOPS_TOGETHER.match(thing)
        if stopping:
            if " ".join(stopping.group("subject").split()).lower() in SAYS_NOTHING:
                return pick(REPLIES["not_coping"], memory)
            return None
        thing = _without_a_filler_tail(thing)
        # A second clause swallowed into the thing ("start saving i have never had a budget":
        # the normalised retry has already dropped the "but") is two statements, not one thing.
        if re.search(r"\b(?:i|i'm|im|i've|i'd|we|we're|us)\b", thing):
            return None
        words = thing.split()
        if not 1 <= len(words) <= 8:
            return None
        # Too thin to be a thing: "i want to go", "i keep trying".
        if words[0] in {"go", "be", "do", "get", "have", "try", "say", "know", "see", "it"} \
                and len(words) <= 2:
            return None
        # A thing they have not narrowed down yet ("something funny to read", "something nice
        # for dinner") asks for a pick. A plan to start it says nothing, so the reply asks
        # which kind instead.
        if LEAVE.search(clean):
            return None
        # The same for a need asked as a question: "i was burgled, do i need the police" wants
        # to know whether to ring them, not which police they usually go for.
        if kind in ("want", "need") and _A_NEED_ASK.search(clean):
            return None
        if ack.a_limit_on_the_plan(clean):
            # "we need to keep it cheap" names a limit, not a thing they want, and it was read
            # as one: "Keep it cheap - fair enough. What's stopped it happening so far?"
            return None
        # Where the knowledge base has a real answer for the line, that answer is the turn: "i
        # need something for a cold" was asked which kind of thing they wanted, and "i want
        # something funny to read" the same, while the cold's remedy and the funny book sat one
        # lookup away. The ask-which-kind reply is for the thing nobody has narrowed down yet.
        # A part of the body with something wrong with it is a problem this module already
        # has advice for: the illness pool for that part answers "what helps an earache", and
        # the frame read away is the same question, so the pool's words are the turn rather
        # than a suggestion to name one they liked.
        # The frame taken off the thing ("something for an earache" -> "an earache") is the
        # problem, and it is that problem the symptom readers and the lookup are asked about.
        problem = " ".join(w for w in words[1:] if w not in INDEFINITE_SKIP) \
            if words[0] in INDEFINITE else thing
        if words[0] in INDEFINITE and (_answers_knows(clean, memory)
                                       or ((SYMPTOM.search(problem) or PAIN_PART.search(problem)
                                            or SYMPTOM.search(thing) or PAIN_PART.search(thing))
                                           and (_answers_knows("what helps " + problem, memory)
                                                or _answers_knows("what helps " + thing, memory)))):
            return None
        # The part the problem names has its own pool of advice, and that advice is the answer:
        # "i need something for an earache" is a sore ear to help with, not a thing to name a
        # favourite of.
        if words[0] in INDEFINITE and SYMPTOM.search(problem):
            problem_read = understanding(problem, memory)
            problem_part = problem_read.get("body") if isinstance(problem_read, dict) else None
            if problem_part and "ill_" + problem_part in REPLIES:
                return _reply("ill_" + problem_part, memory, _name(memory), clean)
        # A line about a person already named in it is about them, not about picking a kind of
        # the thing wanted from them. The knowledge base keeps any line it can answer:
        # "i need some space from my mum" and "i need a day off from you" are its replies.
        someone = _PERSON_IN_THE_TAIL.search(clean)
        if someone and not _answers_knows(clean, memory):
            said = thread.your_words(thing)
            return pick(A_BREAK_FROM_SOMEONE, memory).format(
                X=said[:1].upper() + said[1:], them=someone.group("who"))
        if words[0] in INDEFINITE:
            rest = [w for w in words[1:] if w not in INDEFINITE_SKIP]
            said = thread.your_words(thing)
            return pick(ASK_KIND, memory).format(
                x=said[:1].upper() + said[1:],
                adj=rest[0] if rest else "thing")
        # A body, a medicine, a clinician or the loo is needed now, not planned.
        if kind in ("want", "need") and (set(w.lower() for w in words) & NEED_NOW):
            return None
        # An "always" is a keeps: "im always knackered" is the constant-tiredness answer's line,
        # and "im always late for work" is a routine thing the pool can talk about.
        if kind in ("keeps", "always") and KEEPS_SYMPTOM.search(thing):
            return None
        # A habit line the knowledge base answers is that answer's line: "i keep getting
        # cystitis", "i keep getting thrush" and "i keep having panic attacks" were asked
        # "is it the same every time, or does it vary?" while the entry that says what to do
        # about it sat one lookup away. A line with no entry keeps the routine reply, which is
        # what it is for: "i keep losing my keys" is a habit to fix, not a fact to look up.
        if kind in ("keeps", "always") and _answers_knows(clean, memory):
            return None
        # A keeps line the fallback has a pool for keeps that pool: "i keep losing my keys" is
        # answered with a place to keep them, and a question about how often it happens is
        # thinner than the advice the person would otherwise get.
        if kind in ("keeps", "always") and _fallback_has_its_own_pool(clean):
            return None
        # The knowledge base has an answer about this same thing: "i keep starting and stopping"
        # is never-miss-twice and "i want to build better habits" is the habit-building tips, and
        # a stock question about the trigger or the first step is thinner than either.
        if kind in ("want", "keeps", "always", "intention") \
                and _answers_is_about_the_thing(clean, thing, memory, verbs) \
                and _answers_knows(clean, memory):
            # Both halves matter: the knowledge base has to answer this line at all, and its
            # best entry has to be about the thing named. "i need a recipe for tonight" has a
            # cooking entry whose keys say recipe, but the answers module turns the line down,
            # so the "what kind of recipe" question is still the one the person gets.
            return None
        # A thing to choose ("i need a book for the train") is not a task to start, so the
        # reply is about picking it rather than taking the first step on it.
        if words[0] in {"a", "an", "some", "the", "my", "another", "one"}:
            # The head is the last word before the purpose: "a book for the train" is a book.
            # "from" is a purpose word like the rest: "a break from him" is a break, and the
            # head used to be the last word of the line, so a person already named in it was
            # read as a thing to pick a kind of ("What kind of him do you usually go for?").
            head = re.split(r"\b(?:for|on|in|at|with|to|about|from)\b",
                            " ".join(words))[0].split()[-1]
            # A person who does a job ("i need a plumber") is called, not chosen between by
            # kind, and a thing described by a clause ("a spreadsheet that adds up my spending")
            # is a how-to question, not something to pick a kind of.
            if (PERSON_WORK.search(head) or RELATIVE.search(thing)
                    or _answers_knows(clean, memory)):
                return None
            # A baby, a divorce, a loan and a pay rise are not picked between by kind, so the
            # reply that names the thing fits better than a question about which sort.
            # The job worded after the thing ("your dress taken up") is not part of the thing,
            # so it comes off before the thing is said back: "Your dress - tell me a bit more."
            from ..modules.particles import a_thing_without_its_tail
            said = a_thing_without_its_tail(thread.your_words(thing))
            label = said[:1].upper() + said[1:]
            if head.lower() in _A_PERSON_ALREADY_IN_THE_LINE:
                return None
            if _kindless(head):
                options = [option.format(x=said, X=label) for option in KINDLESS]
                return pick(options, memory)
            options = [option.format(X=label, head=head) for option in CHOOSING]
            return pick(options, memory)
        # A death is not a thing to plan around: that line belongs to the loss reading. The
        # check sits here, after the "which kind?" ask, because that reply presumes nothing
        # about the line ("i want the death star lego set" is a shopping choice).
        if ack.DEATH_WORDS.search(clean):
            return None
        # A one-off action or a state is not a thing to start and build up: "i want to cancel my
        # gym membership" and "i want to be left alone" get the ordinary reply, not a plan.
        if STATE.search(thing) or words[0] in ONE_OFF:
            return None
        # A thing the knowledge base has a real answer for is that answer, not a plan to start
        # it: "i need to make room on my mac" got "Make room on my mac - fair enough. What's
        # stopped it happening so far?" with the Mac storage steps one module away, and so did
        # "i want to write a cv", "i need to save money" and "i want to start running".
        # The knowledge base has to answer the line as it was typed as well as the rewrite: a
        # rewrite that reaches an entry the line itself never reaches would pass the turn to a
        # module with nothing to say ("i want to eat better" got the greeting's stock line).
        if _answers_has_the_how(thing, memory) and _answers_knows(clean, memory):
            return None
        pool = THING_REPLIES[kind]
        if kind == "keeps" and KEEP_ABOUT_SOMEONE.search(clean):
            pool = THING_REPLIES["keeps_someone"]
        if DECISION.search(thing) or (kind == "want" and words[0] not in DOING):
            # "Start with the smallest version" and "tell me the bit that feels hardest" both fit
            # an activity you build up. Moving in together, getting married or retiring is not
            # improved by breaking it into a smaller version, so those entries go.
            pool = tuple(option for option in pool
                         if not any(bad in option for bad in TASK_ONLY))
        if not pool:
            return None
        # The phrase is the person's own words, so a reply that says it back has to say it in the
        # second person: "comparing myself to others" is "comparing yourself to others".
        said = thread.your_words(thing)
        options = [option.format(x=said, X=said[:1].upper() + said[1:]) for option in pool]
        return pick(options, memory)
    return None


# "im a joke to everyone" is not a request for a joke, and telling a stranger one is the wrong
# answer to it: the word is there but it is what the person says they are. So the bare "joke" in
# a line only asks for one when it is not a description of the person writing it.
# The self words are the subject of the clause, not a pronoun anywhere in it: "tell me a joke"
# has "me" in it and is the plainest request there is.
SELF_JOKE = re.compile(r"\b(?:im|i am|i'm|being|made me|make me feel|i feel like|feel like|"
                       r"my life|myself)\b[^.!?]{0,24}?\bjokes?\b")


# The words a subject can never be: "about my dad dying" names the dad, not the "my", and the
# regex took the first word after "about" whatever it was, so the lead-in read "a good my one".
_NOT_A_SUBJECT = frozenset("""
    my your his her their our its the a an this that these those me him them us you it
    some any every no
""".split())


# A joke somebody else made is what the person is telling the bot, not what they want back:
# "my sister made a joke about my weight" and "i told a joke at the wedding and it died" both got
# a pun, so the bot answered a complaint with the thing complained about. "tell me a joke" and
# "make me laugh" are the requests, and they are read as such below.
REPORTS_A_JOKE = re.compile(
    r"\b(?:made|told|cracked|sent|texted)\s+(?:me\s+|us\s+)?(?:a\s+|another\s+|some\s+)?"
    r"jokes?\b")


def _asks_outright(clean):
    """True when the line asks for a joke in so many words ("tell me a joke", "make me laugh").

    A word boundary cannot tell a request from a report: `joke` is in "my mate made a joke about
    my dad dying" as well as in "tell me a joke". This is the narrow reading, for the two places
    where a joke must not arrive unless it was asked for: a thread with a death on it, and a line
    reporting somebody else's joke.
    """
    return bool(JOKE_ASK.search(clean)) or clean.strip().startswith("joke")


def _joined_read(memory):
    """True when the line was joined onto the topic it follows before it was read here.

    The follow-up reader (`_follow_up_reading`) reads the earlier turn's words in front of the
    ask, which is how "how many lessons will i need" reaches the driving entry. Read that way,
    though, a word from a turn ago counts as a word in this line: "my mate made a joke about my
    dad dying" followed by "what would you say to him" asked for a joke, one turn after a death,
    and got a pun about a scarecrow. A joke is said to the line in front of the bot, and that
    line was already read by the call before this one.
    """
    return bool(memory.get("joined_read")) if isinstance(memory, dict) else False


def _joke(clean, tokens, memory):
    """A short, clean joke, about the subject if the user named one."""
    # "my landlord is a joke" is a verdict on the landlord, not a request for a punchline: the
    # line has the word in it, and the person is complaining. Read here rather than in the ask
    # above because it is what the line means, not what it looks like.
    if verdicts_a_thing(clean):
        return None
    if _joined_read(memory):
        return None
    asked_by_name = _asks_for_a_joke(clean, tokens, memory)
    # Somebody else's joke is the thing being told, not a request: the reply belongs to the
    # person who made it and how it landed, which is what this module's own pools answer.
    if not _asks_outright(clean) and REPORTS_A_JOKE.search(clean):
        return None
    # Nothing funny while a death is on the thread unless the person asked for a joke in so many
    # words: "make me laugh" after "my mum died" is a person asking to be cheered up and gets its
    # joke; "what would you say to him" after "my dad dying" is not a request.
    if not _asks_outright(clean) and isinstance(memory, dict) and memory.get("loss"):
        return None
    after_joke = _last_was_joke(memory) and len(tokens) <= 8 and any(
        t in {"another", "more", "next", "again", "else", "any", "got", "one"} for t in tokens)

    if not (asked_by_name or after_joke
            or ("joke" in tokens and len(tokens) <= 10
                and not (JOKE_ADVICE.search(clean) or set(tokens) & PICK_WORDS)
                and not SELF_JOKE.search(clean))):
        return None
    subject = None
    match = re.search(r"\babout\s+(?:(?:a|an|the|my|your|his|her|their|our|its)\s+)?([a-z]+)", clean)
    if match:
        subject = match.group(1).rstrip("s")
        if subject in _NOT_A_SUBJECT:
            subject = None
    words = {t.rstrip("s") for t in tokens}
    for key, joke in JOKES.items():
        if key in words or key in (subject or ""):
            return joke
    for key, joke in JOKES.items():
        if re.search(r"\b" + key + r"s?\b", clean):
            return joke
    if subject:
        return f"I don't know a good {subject} one, sorry. " + pick(SHORT_JOKES, memory)
    return pick(SHORT_JOKES, memory)


def _normalised_line(memory):
    """The line read as ordinary words, or None when that is what was typed anyway."""
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return None
    norm = understood.get("norm")
    if not isinstance(norm, list) or not norm or norm == understood.get("words"):
        return None
    return " ".join(norm)


# A length of time on its own ("its been going on for weeks") is the answer to a question the
# bot just asked about a problem, or a second turn on a problem the person already told it
# about. Acknowledging it ("Got it - it's been going on for weeks") throws away the one thing
# the person just added, so what the length means is the reply. Nothing here names a symptom:
# the same answer is right for a back, a sleep, a mood or a job.
STANDING_LINE = re.compile(
    r"^\W*(?:and\s+|well\s+|oh\s+|hmm\s+|it'?s\s+been\s+|its\s+been\s+|that'?s\s+been\s+|"
    r"i'?ve\s+been\s+|ive\s+been\s+|been\s+|i'?ve\s+had\s+it\s+|ive\s+had\s+it\s+|"
    r"it'?s\s+|its\s+|that'?s\s+)?"
    r"(?:going\s+on\s+|going\s+|like\s+(?:this|that)\s+|now\s+|"
    r"there\s+|at\s+it\s+|doing\s+it\s+|this\s+way\s+|that\s+way\s+)?(?:for\s+)?"
    r"(?:about\s+|around\s+|nearly\s+|over\s+|like\s+)?"
    r"(?:(?:\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"a\s+couple\s+of|a\s+few|several)\s+)?"
    r"(?:days?|weeks?|months?|years?|ages|a\s+long\s+time|all\s+(?:week|month|year)|"
    r"since\s+(?:yesterday|this\s+morning|last\s+night|the\s+weekend|christmas|the\s+summer|"
    r"last\s+\w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|"
    r"march|april|may|june|july|august|september|october|november|december))"
    r"(?:\s+(?:now|too|already|in\s+a\s+row))?\W*$")


# A length that names nothing yet. The reply can only ask, and it says the length back so the
# person knows the length itself was read rather than heard as a greeting.
STANDING_WHAT_REPLIES = {
    "days": ("A few days of what - has something been going on?",
             "Days of what, sorry? Tell me what has been happening and I can help.",
             "What is it that has been going on for a few days?"),
    "weeks": ("Weeks of what - has something been going on?",
              "Weeks of what, sorry? Tell me what it is and I can help.",
              "What is it that has been going on for weeks?"),
    "months": ("Months of what - what has been going on that long?",
               "What is it that has been going on for months?",
               "Months of what, sorry? What is it that has been going on?"),
    "long": ("What has been going on that long?",
             "How long of what, sorry - what is it that has been going on?",
             "Tell me what it is that has been going on all this time."),
}


# How long is long enough to matter. A few days is watch-and-see; a few weeks is the point where
# a GP is worth the trip; months and years are the point where "it's been going on for ages" has
# to be said out loud in the appointment, because it changes what gets looked at.
STANDING_REPLIES = {
    # Nothing here counts the days: the line may be "three days" or "since last night", and a
    # reply that says "a few days is" would be putting a number in their mouth.
    "days": (
        "That's still early days — keep a note of when it's worse and give it a full week before "
        "you think about a GP.",
        "That's short enough to wait on. If it's the same this time next week, that's when it's "
        "worth getting looked at.",
        "Early days on its own is common enough. What would make it worth mentioning is it still "
        "being there after a week.",
    ),
    "weeks": (
        "Weeks of it is the point where a GP is worth the trip, even if it turns out to be nothing.",
        "Two or three weeks is long enough to stop waiting it out. Say how long it's been when you "
        "book, because that's what moves it along.",
        "Weeks is where it stops being bad luck and starts being worth a proper look.",
    ),
    "months": (
        "Months is long enough that it deserves a proper look — ask for a longer appointment and "
        "say how long it's been.",
        "Months is usually where people stop mentioning it and just get on with it. Say the length "
        "out loud in the appointment and ask what can be done about it.",
        "Months of that is worth taking seriously rather than riding out.",
    ),
    "long": (
        "That long is worth a longer appointment, and saying exactly how long it's been: it changes "
        "what they look at.",
        "Years of putting up with it is a lot. Write the length down before you go in, or the "
        "appointment is over in five minutes.",
        "Carrying that for that long is tiring on its own, and it's fair to want it looked at "
        "properly now.",
    ),
}


# A machine or a thing about the house is not a body. The greeting card asks how long anything
# has been like that ("my laptop keeps crashing" -> "How long has it been like that?"), so the
# length comes back to a reply written for a back or a mood, and a broken laptop was told that
# weeks of it is the point where a GP is worth the trip. Weeks of a laptop is a repair.
A_THING_THAT_BREAKS = re.compile(
    r"\b(?:laptops?|computers?|pcs?|macbooks?|phones?|iphones?|tablets?|ipads?|printers?|"
    r"scanners?|routers?|modems?|wifi|wi-fi|broadband|internet|emails?|app|software|windows|"
    r"tv|tvs|televisions?|telly|monitors?|screens?|consoles?|playstations?|xbox|speakers?|"
    r"headphones?|keyboards?|mouses?|chargers?|batter(?:y|ies)|"
    r"cars?|vans?|bikes?|bicycles?|motorbikes?|scooters?|engines?|tyres?|tires?|"
    r"boilers?|heating|radiators?|thermostats?|washing\s+machines?|washers?|dishwashers?|"
    r"tumble\s+dryers?|dryers?|fridges?|freezers?|ovens?|cookers?|hobs?|microwaves?|"
    r"kettles?|toasters?|vacuum|hoover|mowers?|lawnmowers?|drills?|"
    r"taps?|showers?|toilets?|sinks?|drains?|pipes?|guttering|gutters?|roofs?|fences?|gates?|"
    r"doors?|locks?|windows?|garages?|sheds?|shelves|shelf|"
    r"washer|dryer|machine|device|gadget|appliance)\b", re.IGNORECASE)


# Said about a thing, a length says how long they have put up with it and how long a repair has
# been worth doing: nothing here promises a doctor, and nothing here counts the days.
STANDING_THING_REPLIES = {
    "days": (
        "Two days of it is still worth watching rather than fixing. Note when it does it, "
        "because that is the first thing anyone will ask you.",
        "A couple of days is early for a repair. If it does it again tomorrow, that is when to "
        "start asking.",
    ),
    "weeks": (
        "Two or three weeks of that is past bad luck. Back anything up that matters, then have "
        "it looked at properly rather than living with it.",
        "Weeks of it is long enough to stop waiting it out. Say how long it has been doing it "
        "when you ring, because it moves the job along.",
    ),
    "months": (
        "Months of it is worth sorting out rather than working around. Say how long it has been "
        "doing it, and ask what a repair costs before they start.",
        "Months of putting up with it usually means it is cheaper to fix it properly now than to "
        "keep patching it. Get one quote and compare what is covered.",
    ),
    "long": (
        "That long is worth a proper repair rather than another workaround.",
        "After that long, ask whether repairing it is still worth it against replacing it: say "
        "the age and what it cost before they quote.",
    ),
}


# Said about a mood rather than a body, the length points somewhere slightly different: weeks is
# the point to tell someone, and months is the point to ask for help that is already there.
STANDING_FEELING_REPLIES = {
    # Nothing here counts the days: the line may be "since last night" or "since monday", so
    # "a couple of days of it is" would put a number in their mouth that they never gave.
    "days": (
        "A rough patch like that is not a verdict. Sleep, food and daylight first, and if most "
        "days still feel like that for weeks, that is worth a GP.",
        "A mood that has only just started is not a verdict on anything. Tell one person how it "
        "actually is, and give it a few weeks and some sleep before you read anything into it.",
    ),
    "weeks": (
        "Weeks of feeling like that is worth telling someone — a GP first, and a friend who will "
        "keep asking how you are.",
        "A few weeks of it is the point to say it out loud to a GP rather than waiting for it to "
        "lift on its own.",
    ),
    "months": (
        "Months of feeling like that is the point to ask for help: a GP can refer you for talking "
        "therapy, and you don't have to explain it well to ask.",
        "Months is a long time to carry a mood on your own. Book a longer appointment, say how long "
        "it has been, and ask what is available.",
    ),
    "long": (
        "That long is worth asking for talking therapy by name — a GP can refer you, and it is "
        "there for exactly this.",
        "Years of it is not something to keep managing alone. Say how long it has been, and ask "
        "what help there is.",
    ),
}


# The bot's own questions that a length answers. If it asked one, the length is the answer to it
# and needs no second guess about what the line is about. The question is not always about the
# person themselves: "my dad has a bad cold" / "how long has your dad had it?" is asked about
# somebody they look after, and the length that comes back answers it just the same.
ASKED_HOW_LONG = re.compile(
    r"how long (?:has|have|had) (?:it|that|this) been|how long has it been|has it been going on "
    r"long|has it been like this long|how long have you|"
    # ... and the same questions asked about somebody the person looks after: "how long has your
    # dad had it?", "has your nan been like that long?", "how bad is your mum with it?" The one
    # or two words are the person ("your dad", "she", "the pain"), so an oven or a loaf cannot be
    # read as a problem the length is about.
    r"how long (?:has|have|had) (?:\w+ ){1,2}had it|has (?:\w+ ){1,2}had it long|"
    r"how long has (?:\w+ ){1,2}been like (?:that|this)|how bad is (?:\w+ ){1,2}with it|"
    r"is it easing at all", re.I)


# Tiredness said to go on is answered by the entry for constant tiredness, not the pool for a
# passing "im knackered", so `_feeling` reads it as no feeling at all (`TIRED_PERSISTENT`). The
# length that follows is still about that tiredness: "im tired all the time" / "since monday" fell
# past every subject test here and got the listening line, one turn after a real answer.
TIRED_SAID = re.compile(
    r"\b(?:tired|exhausted|knackered|shattered|wiped|sleepy|bushed|drained|worn out|no energy|"
    r"done in|zonked|pooped|dead on my feet)\b")


def _a_constant_tiredness(clean):
    """True for a tiredness the line says goes on: "im tired all the time", "always exhausted"."""
    return bool(TIRED_SAID.search(clean) and TIRED_PERSISTENT.search(clean))


def _standing(clean, memory):
    """The reply to a length of time said on its own, when it is about a problem."""
    match = STANDING_LINE.match(clean)
    if not match:
        return None
    length = " ".join(match.group(0).split())
    if re.search(r"\b(?:days?)\b", length):
        bucket = "days"
    elif re.search(r"\bweeks?\b", length):
        bucket = "weeks"
    elif re.search(r"\bmonths?\b", length):
        bucket = "months"
    elif re.search(r"\bsince\b", length) and not re.search(
            r"\b(?:year|years|christmas|summer|winter|spring|autumn|january|february|march|"
            r"april|may|june|july|august|september|october|november|december)\b", length):
        # "since monday", "since last night", "since the weekend": a day or a few at most, so it
        # is the short bucket rather than the open-ended one. "Since christmas" is not, and the
        # words for the long ones are checked first above.
        bucket = "days"
    else:
        bucket = "long"
    turns = memory.get("turns") if isinstance(memory, dict) else None
    last_bot = ""
    for turn in reversed(turns or ()):
        if isinstance(turn, dict) and turn.get("bot"):
            last_bot = str(turn.get("bot") or "")
            break
    topic = memory.get("topic") if isinstance(memory, dict) else None
    said = str(topic.get("text") or "") if isinstance(topic, dict) else ""
    # What the length is about can be one question back: "i feel low most days" / "do you think
    # i should see someone" / "its been like this for a year" is a length about the low mood, not
    # about the question the bot answered in between. Only the last two user lines are read, so
    # a feeling from earlier in the conversation cannot be revived by a length days later.
    subjects = [said] if said else []
    for turn in reversed(turns or ()):
        if isinstance(turn, dict) and turn.get("user"):
            subjects.append(str(turn.get("user") or ""))
            if len(subjects) >= 3:
                break
    about = ""
    for subject in subjects:
        if subject and (_feeling(subject) or _stuck(subject) or SYMPTOM.search(subject)
                        or reads_like_a_symptom(subject)
                        or _a_constant_tiredness(subject)):
            about = subject
            break
    # A thing that breaks is the thing the length is about even when no symptom word names it:
    # "my laptop keeps freezing" / "still the same" / "its been doing it for two weeks" is a
    # fortnight of a laptop, not a length with nothing behind it.
    if not about and A_THING_THAT_BREAKS.search(" ".join(subjects)):
        return pick(STANDING_THING_REPLIES[bucket], memory)
    if not (ASKED_HOW_LONG.search(last_bot) or about):
        # A length with nothing in the conversation it can be about: the person has not said
        # what has been going on yet, and there is no earlier turn to read it from. The line
        # itself is all there is, and the one thing a length cannot do on its own is say what
        # it is a length of, so the ask goes back with the length in it rather than a pool that
        # fits any message ("i've had it for three days" was answered "How was it, overall?").
        return pick(STANDING_WHAT_REPLIES[bucket], memory)
    if about and _feeling(about) and bucket in STANDING_FEELING_REPLIES:
        return pick(STANDING_FEELING_REPLIES[bucket], memory)
    return pick(STANDING_REPLIES[bucket], memory)


def _repaired_line(memory):
    """The line with its spelling put right, in the person's own words (`plain`)."""
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return None
    plain = understood.get("plain")
    if not isinstance(plain, str) or not plain.strip():
        return None
    return plain


# Saying you do not know something is not declining the conversation: "i dont kno" wants the same
# answer as "i dont know", "dunno", "idk" and "no idea", not "No worries - say if you change your
# mind." Expanding "dont" to "do not" once let that "not" reach the decline test first, so the
# family is read early, before the vague pool and the short talk take the line.
# "not a clue", "never sure" and "iunno" are the same family written the other ways people write
# it: the little word can sit between the negator and the noun, and "iunno" is the run-together
# spelling of "i dunno". "beats me" and "god knows" are the family said as a phrase.
DONT_KNOW = re.compile(
    r"\b(?:i (?:really |just |honestly )?(?:dont|do not|dnt|dunno) know|dunno|idk|iunno|"
    r"(?:not|no|never|isnt|is not) (?:a |any |too |so )*(?:sure|idea|clue)|"
    r"ha(?:ve|v)ent a clue|i dont have a clue|beats me|god knows)\b")


# What may be left in a line that is only saying it does not know: "i dont kno sorry", "dunno yet",
# "idk tbh", "not sure tbh mate".
DONT_KNOW_FILLER = frozenset("""
i im just really so very honestly actually dont do not know no idea sure dunno idk iunno sorry ta
thanks thank you yet right now either though tho oh well hmm um guess a clue havent havent havnt
didnt have dnt dno tbh lol mate tbf god knows beats me a any truly still even then
""".split())


def _says_dont_know(clean, tokens):
    """True when the line does nothing but say the person does not know."""
    if not tokens or len(tokens) > 12:
        return False
    if not DONT_KNOW.search(clean):
        return False
    return set(tokens) <= DONT_KNOW_FILLER


# The way the conversation itself is going: "sorry i keep jumping about", "i keep changing the
# subject", "im going on a bit", "sorry for jumping between things". These are an apology for the
# shape of the chat, not a thing that keeps happening to the person, and the routine reply asked
# "is it the same every time, or does it vary?" of somebody who was saying sorry. What they want
# to know is that the bot still has hold of what they brought, so the answer names the things on
# the table - and it is only given when the store has two of them, because a chat with nothing in
# it yet has nothing to show for itself and the plain "ask away" is the better reply there.
# The shape of the line: a first-person "jumping about", "changing the subject", "going off on
# one", or "sorry for all the questions". The first-person frame matters, because "my family keep
# changing the subject" and "im jumping between two jobs" are about somebody else's manners and
# about work, not about the way this chat is going.
CHAT_SCATTER = re.compile(
    r"\b(?:i|im|i'm|i am|ive|i've)\b[^.!?]{0,18}\b(?:jump|jumping|jumped|hop|hopping|skip|"
    r"skipping|flit|flitting|dart|darting|bounc\w*)\b[^.!?]{0,12}\b(?:about|around|between)\b|"
    r"\b(?:jump\w*|flit\w*|skip\w*)\s+from\s+(?:one\s+)?thing\s+to\s+(?:the\s+)?"
    r"(?:next|other|another)\b|"
    r"\b(?:i|im|i'm|i am|ive|i've)\b[^.!?]{0,18}\b(?:keep\s+)?chang(?:ing|e|ed)\s+the\s+"
    r"(?:subject|topic)\b|"
    r"\b(?:i|im|i'm|i am|ive|i've)\b[^.!?]{0,18}\b(?:keep\s+)?go(?:ing|ne)?\s+off\s+on\s+one\b|"
    # "sorry for jumping between things": the apology stands in for the first person.
    r"\bsorry\b[^.!?]{0,20}\b(?:jump\w*|flit\w*|hop\w*|skip\w*)\b[^.!?]{0,12}"
    r"\b(?:about|around|between)\b")


# "sorry for all the questions", "sorry, random questions", "ive got a hundred questions".
CHAT_SCATTER_ASKS = re.compile(
    r"\bsorry\b[^.!?]{0,24}\b(?:many|random|daft|silly|stupid|odd|lot\s+of|loads\s+of|"
    r"all\s+(?:these|the|my)|a\s+few)\b[^.!?]{0,12}\bquestions?\b|"
    r"\b(?:hundred|million|loads\s+of|lot\s+of)\s+questions?\b|"
    r"\bsorry\b[^.!?]{0,20}\b(?:to\s+)?keep\s+asking\b|"
    r"\bsorry\b[^.!?]{0,20}\basking\s+you\s+(?:so\s+much|a\s+lot|things)\b")


# Said out loud, an apology is about the chat; the same words are not, so the apology or a word
# for talking has to be in the line - unless the line names the subject it keeps changing.
CHAT_SCATTER_CTX = re.compile(
    r"\bsorry\b|\bapolog\w*\b|\bquestions?\b|\b(?:chat|conversation|talking|asking|"
    r"telling you)\b|\bsubject\b|\btopic\b|\boff on one\b")


# The mouth runs on, the head does not: "im going on" is about the talking, and "my head is all
# over the place" is the scattered-head pool's line, which says something the chat cannot. A life
# with the same shape ("im jumping between two jobs") keeps its own answer for the same reason.
CHAT_SCATTER_NOT = re.compile(
    r"\b(?:head|brain|mind|thoughts?|memory|life|sleep|shifts?|jobs?|kids?|children|mum|dad|"
    r"family|wife|husband|partner|work)\b")


# An apology is only the line when it is all the line. The follow-up reading puts the last thing
# said in front of a bare question ("sorry i keep going off on one" + "what would you do?"), and
# answering that with "no need to apologise" answers the apology and drops the question. So a
# line that carries a real question of its own after the apology is that question.
CHAT_SCATTER_LEFTOVER = frozenset("""
    the and you your for that this with just its it it's not all any have has had was were are
    sorry apologise apologize apologising asking ask asked told tell said say here there then than
    about around between things thing something anything much very really lot loads few some
    questions question today tonight now again still too so but
    """.split())


def _only_the_apology(clean, match):
    """True when the apology match leaves no question of its own behind it."""
    rest = clean[match.end():] if match else clean
    words = [word for word in re.findall(r"[a-z']+", rest) if len(word) > 2]
    return len([word for word in words if word not in CHAT_SCATTER_LEFTOVER]) < 2


CHAT_SCATTER_REPLIES = (
    "Jump about as much as you like - I'm holding {list}. Where do you want to pick up?",
    "No need to apologise, it's your chat. Still on the table: {list}.",
    "Ask in any order you like. I have {list}, so nothing is lost.",
)


# One thing on the table, or nothing the store can name: the same warmth without a list, because
# a list of one ("I'm holding the guitar") claims more than the chat holds.
CHAT_SCATTER_ALONE = (
    "Jump about as much as you like - I'm keeping the thread, not marking you on it.",
    "No need to apologise. Jump between them as you like and I'll keep track.",
    "That's what I'm here for - carry on in any order.",
)


# An apology for asking is not an apology for hopping about: they said sorry for the number of
# questions, and a line about "jumping about" answers a charge they did not make. So the two
# shapes keep their own pools, chosen by which one the line is, and both name what is held.
CHAT_ASKING_REPLIES = (
    "No need to apologise, it's your chat. Still on the table: {list}.",
    "Ask in any order you like. I have {list}, so nothing is lost.",
    "Ask as many as you like - I'm holding {list}, and nothing is lost.",
)


CHAT_ASKING_ALONE = (
    "No need to apologise - asking is what I'm here for.",
    "Ask as many as you like, whenever you like.",
    "None of that needs an apology. Ask away.",
)


def _chat_scatter(clean, memory):
    """A reply to an apology for how the chat is going, naming what the chat is holding.

    Returns None when the line is not that, and None too when the chat is empty: a scatter
    apology on turn one of a chat has nothing to show for itself, and the "ask away" replies
    already there are the better answer.
    """
    shape = CHAT_SCATTER.search(clean)
    asks = CHAT_SCATTER_ASKS.search(clean)
    if not (shape or asks):
        return None
    if CHAT_SCATTER_NOT.search(clean) or not CHAT_SCATTER_CTX.search(clean):
        return None
    if not _only_the_apology(clean, shape or asks):
        return None
    # Which of the two apologies this is: hopping about between things, or asking a lot. The
    # pools are drawn from the one they said, so nothing answers a charge they did not make.
    if shape:
        with_a_list, alone = CHAT_SCATTER_REPLIES, CHAT_SCATTER_ALONE
    else:
        with_a_list, alone = CHAT_ASKING_REPLIES, CHAT_ASKING_ALONE
    held = thread.on_the_table(memory)
    if len(held) >= 2:
        said = thread.in_a_list(held)
        return pick([option.format(list=said) for option in with_a_list], memory)
    if held or shape:
        return pick(list(alone), memory)
    return None
