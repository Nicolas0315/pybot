"""Part 2 of 6 of the module, split out of `repeat`.

Everything here is re-exported from `repeat`, so callers import it from there as before.
"""
import re

from ..compose import pick
from . import narrow, topics
from .repeat_part_01 import (
    CONDITION_CLAUSE, NOT_A_MOVE, SENTENCE, _explains, _opens_an_instruction, NEXT_ASK, ASKING_THEM,
    MOST, ASK, ASK_VERB, FILLER, HEDGE, LOOK_BACK_FOR_LESS, QUOTE_PAIRS, BARE_ASK,
    BARE_ASK_NEEDS_A_QUESTION,
)


# A condition that puts the decision on them - "if that sounds fine", "if you can live with
# that", "if you are happy with it" - is the choice itself, not a moment the step waits for.
_A_JUDGEMENT = re.compile(
    r"^\s*(?:when|once|if|as soon as|next time)\b[^,]{0,60}?\b(?:sounds?|feels?|you'?re happy|"
    r"you are happy|you can live with|you'?re ok(?:ay)? with|you are ok(?:ay)? with)\b", re.I)


def _a_conditional_move(said):
    """The answer's step that comes wrapped in its own condition, kept whole, or None.

    An answer often puts the step behind the moment to do it: "When you're ready, ask for one
    line of feedback", "Once it has cooled, press it flat". `_a_move` reads that condition and
    stops, because a step for later is not the step to do first - which is right for "what
    should i do first" and wrong for the person who says they do not know what to do at all:
    there, the conditional step is the one thing the answer has to give them, and repeating the
    answer's opening sentence ("That's disappointing, especially after an interview") says
    nothing they can do. The condition is kept, so the step is not handed over as if it were
    for now.
    """
    parts = [p.strip() for p in SENTENCE.split(str(said).strip()) if p.strip()]
    for part in parts:
        if topics.RED_FLAG.match(part) or NOT_A_MOVE.match(part):
            continue  # a warning or a referral is not a step, whatever it is wrapped in
        match = CONDITION_CLAUSE.match(part)
        if not match:
            continue
        # The dash-clause after a step is why it is done, and a bracket after it is the aside
        # that says the same in different words ("ask for one line of feedback (was there
        # anything I could strengthen?)"): neither is more of the step, and both made a short
        # step too long to be handed back.
        step = re.split(r"\s+[-\u2014]\s+|\s+\(", part.strip())[0].strip(" ,.;:")
        # The condition runs to its comma - "When you're ready, ..." - and the step is what
        # follows it; without a comma the whole clause is one word ("Once cooked, ...") and the
        # step starts after it.
        after = step.split(",", 1)
        rest = (after[1] if len(after) > 1 else step[match.end():]).strip(" ,")
        if not 3 <= len(rest.split()) <= 14:
            continue  # a two-word step is a shrug, not the thing to do
        if not _opens_an_instruction(rest):
            continue  # the condition leads into a fact, not an instruction
        if _A_JUDGEMENT.match(step):
            # "If that sounds fine rather than like a sacrifice, get one" weighs their life up
            # and its step is the decision itself: handed back alone it tells a person at a loss
            # to make up their mind, which is the thing they said they cannot do.
            continue
        if not 4 <= len(step.split()) <= 24:
            continue
        if _explains(step):
            continue
        return step[0].lower() + step[1:]
    return None


def asks_for_more(text):
    """Whether the line asks for the next part of the answer in hand, and says nothing else.

    "what else", "anything else", "and after that" - four words at most, because a line that says
    what it is about ("what else can i do about my nails") has a subject of its own for the
    entries to match. `names_nothing` reads "anything else" as naming something, so this ask needs
    a reading of its own.
    """
    if len(re.findall(r"[a-z']+", str(text or "").lower())) > 4:
        return False
    return bool(NEXT_ASK.search(str(text or "")))


def a_hand_back(said, memory):
    """Whether this bot line was handed back out of an earlier answer rather than being one.

    A step is a clause of the answer it came from, so a turn that holds one is not the answer: what
    to do with "what else" after it is the answer behind it, which `_handed_back` kept. Read off
    what was handed back rather than off a list of lead-ins, so a frame added later is one of these
    too.
    """
    wanted = str(said or "").strip().lower()[:60]
    if not wanted:
        return False
    return any(wanted in str(line or "").lower() for line in (memory.get("repeated") or []))


def _handed_back_last(memory):
    """Whether the bot's last turn was a short form handed back out of an earlier answer."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    return a_hand_back(turns[-1].get("bot"), memory)


def _another_part(said, memory):
    """The next part of the answer in hand and whether it says what to do, else ("", False).

    The answer is walked in order, so "what else" after a step gets the part after the step rather
    than the step again or the whole paragraph. A red flag is not a next step ("Get it looked at
    if it gives way" is what to do in an emergency, not the next thing to try) and neither is a
    sentence that asks the person for something, so both are skipped. A sentence that tells them
    to do something wins over one that only explains, because "what else" asks for the next move -
    but an answer of nothing but explanation still has more in it, so the first part is the
    fallback and the caller says which of the two it got.
    """
    spare = ""
    for part in (p.strip() for p in SENTENCE.split(str(said).strip())):
        part = part.rstrip(" .")
        if len(part.split()) < 4 or len(part) > MOST:
            continue
        if topics.RED_FLAG.match(part) or ASKING_THEM.search(part):
            continue
        if _already_repeated(part, memory):
            continue
        # The lead already says where the part comes from, so a part that opens on a connective
        # reads as one said twice: "After that: Then ask for a specific figure" is "then" twice.
        part = re.sub(r"^(?:and\s+|but\s+|so\s+|then\s+|after\s+that,?\s+|next,?\s+)", "",
                      part, flags=re.I)
        part = re.sub(r"^then\s+", "", part, flags=re.I)
        if len(part) > 110:
            # A sentence that carries its examples in a list after a colon says what to do before
            # it: "Notice the moment you start, and give that hand something else to do: a ring to
            # twist, a pen, a stress ball." The next part is the doing, not the shopping list.
            head = part.split(": ")[0].strip(" ,;")
            if len(head.split()) >= 4:
                # The list under the colon may be further along than the lead-in. The answer gives
                # "Change a few things you can keep doing rather than going on a diet: fill half
                # the plate with vegetables, put protein in every meal ...", and once the first
                # clause of that list has been handed over, the next part is the clause after it -
                # not the lead-in again ("After that: Change a few things you can keep doing rather
                # than going on a diet"), which is a heading read out as a step.
                under = [one.strip(" ,;:") for one in re.split(r",\s+", part.split(": ", 1)[1])]
                under = [one for one in under if one]
                if under and _already_repeated(under[0], memory):
                    for clause in under[1:]:
                        if _says_what_to_do(clause) and not _already_repeated(clause, memory):
                            return clause, True
                    continue
                part = head
                # The cut is taken after the "said already" test above, and the head on its own is
                # the part that was handed back a turn ago: "Fix the wake-up time first" came back
                # as "After that: Fix the wake-up time first." on a "what else", the same
                # instruction twice in a row. What the head contains has been said too.
                if _already_repeated(part, memory):
                    continue
        if _says_what_to_do(part):
            return part, True
        if not spare:
            spare = part
    # An explanatory part is offered only when it was not on the screen already: the answer in hand
    # was read in full a turn ago, so handing its opening sentence back as "one more thing" is the
    # paragraph again with a label in front of it ("my knee hurts" / "what should i do first" /
    # "anything else" -> "There is this too: A sore knee is usually a strain"). Where the doing
    # parts are all spent, the honest "that's the lot I have" is the reply.
    if spare and not _said_in_a_turn(spare, memory):
        return (spare, False)
    return ("", False)


def _said_in_a_turn(short, memory):
    """Whether these words are already in a reply the bot gave, whichever turn it was."""
    said = str(short or "").strip()[:60].lower()
    if not said:
        return False
    for turn in memory.get("turns") or []:
        if isinstance(turn, dict) and said in str(turn.get("bot") or "").lower():
            return True
    return False


def _says_what_to_do(part):
    """True when the sentence tells them to do something rather than saying how things are."""
    from ..compose.verdict import IMPERATIVES  # the verbs an instruction can open on

    words = [w.strip(" ,;:.") for w in str(part).lower().split()]
    orders = bool(re.search(r"\bdo not\b|\bdon'?t\b", str(part), re.I))
    at = next((index for index, word in enumerate(words) if word in IMPERATIVES), None)
    if at is None:
        return orders
    # A verb that comes after the sentence has said how things are is not the doing asked for:
    # "Losing about 0.5 to 1kg a week is the rate that stays off, and the plan that works is the
    # one you would still follow in a year" was handed to a "what else" as the next thing to do,
    # because "follow" is on the list. The copula in front of it makes the sentence a statement
    # about the thing, and a statement is the spare, not the move.
    if any(word in ("is", "are", "was", "were", "means", "sounds") for word in words[:at]):
        return orders
    return True


# The leads that say the line after them was given in this chat already. They are true only when
# it was. An answer is reached again by a line it does not fit ("what should we spend it on first"
# got a cheap-food answer out of a bathroom chat, "what if she just wont start" a caffeine one out
# of a homework chat), and framing that as "It's what I said a moment ago: ..." tells the person
# they already have an answer they never got - worse than a punt, because it is a claim about
# their own conversation that is not true. Where the claim does not hold, the sentence is still
# the best thing to give: it is just given plainly, with nothing said about when it was said.
CLAIMS_IT_WAS_SAID = (
    "it's what i said a moment ago",
    "you've got it",
    "that's the one",
    "same answer",
    "from just now",
    "said again",
    "sorry, again",
    "as i said",
    "again",
)


def _said_in_the_chat(said, memory):
    """True when the chat has already read this wording.

    Checked the way a friend would: the opening of the line, whitespace flattened, against the
    bot's own turns. A short form is a cut of an answer rather than a copy of one, so the opening
    is what has to be found, not the whole line.
    """
    opening = " ".join(" ".join(str(said or "").lower().replace("...", " ").split()).split()[:10])
    if not opening:
        return False
    for turn in memory.get("turns") or []:
        if isinstance(turn, dict) and opening in " ".join(str(turn.get("bot") or "").lower().split()):
            return True
    return False


def _claims_what_it_never_said(reply, memory):
    """The line, with its claim to have said this before taken off when the claim does not hold."""
    line = str(reply or "").strip()
    low = line.lower()
    for head in CLAIMS_IT_WAS_SAID:
        if not low.startswith(head):
            continue
        rest = line[len(head):].lstrip(" :-,\u2014").strip()
        if rest and not _said_in_the_chat(rest, memory):
            return rest[:1].upper() + rest[1:]
        return line
    return line


def _handed_back(memory, reply):
    """Keep the line handed back, so the next bare ask sees it as already said.

    A short form of an answer is not a copy of it (a move is one clause of it), so counting the
    earlier answers alone would let the same clause come back a third time: the turn that handed
    it back has to count as having said it.
    """
    reply = _claims_what_it_never_said(reply, memory)
    kept = memory.get("repeated")
    if not isinstance(kept, list):
        kept = memory["repeated"] = []
    kept.append(reply)
    del kept[:-8]
    return reply


_FRAME_HEADS = []


def _frame_heads():
    """Every lead-in this module can put in front of a line, as the text it opens on.

    Read off the templates rather than listed again, so a pool added later - here or below this
    point in the file - is framed like the rest, and a frame can never be stacked on a frame the
    test does not know about. Found on first use, when the whole module has been read.
    """
    if _FRAME_HEADS:
        return _FRAME_HEADS[0]
    heads = set()
    for value in list(globals().values()):
        if not isinstance(value, (tuple, list)):
            continue
        for item in value:
            if not isinstance(item, str):
                continue
            # A template is a line with a slot in it: "Shorter: {short}". A bare "{short}" is
            # the answer itself and opens on nothing, so it frames nothing.
            head = item.split("{", 1)[0].strip()
            if "{" in item and head:
                heads.add(head.lower())
    _FRAME_HEADS.append(tuple(sorted(heads, key=len, reverse=True)))
    return _FRAME_HEADS[0]


def framed(said):
    """True when this line already has one of this module's hand-back frames on it.

    "i dont follow" after a line that repeat had framed came back as "I said: It's what I said a
    moment ago: ..." - a frame stacked on a frame - because the module that answers "what did you
    mean" only knew its own leads. A line that has already been handed back under a lead is the
    answer's second telling, and framing it again says the same thing a third time.
    """
    line = (said or "").strip().lower()
    return bool(line) and line.startswith(_frame_heads())


def handed_back(memory, reply):
    """The public form of `_handed_back`: a line the bot gave with a lead on it is kept.

    Every module that hands a line over under a frame records it here, so nothing frames it again:
    a frame on a frame is the bot saying the same thing a third time.
    """
    return _handed_back(memory, reply)


def _already_repeated(short, memory):
    """Saying the same paragraph a third time reads worse than moving on: once the answer has
    come back once, another "what now" wants the next step, not the same line again."""
    said = short.strip()[:60].lower()
    if not said:
        return False
    seen = 0
    for turn in memory.get("turns") or []:
        if not isinstance(turn, dict):
            continue
        # Case does not decide whether a sentence has been said: a move is handed back with its
        # first letter lowered, and it is still the same sentence on the screen.
        if said in str(turn.get("bot") or "").lower():
            seen += 1
    # A line handed back a turn ago counts as said: a move is one clause of an answer, so it is
    # not found in the answer it came from.
    for line in memory.get("repeated") or []:
        if said in str(line or "").lower():
            seen += 1
    return seen >= 2


def _handed_back_already(step, memory):
    """True when this very step has already been handed back as the reply, not merely said.

    `_already_repeated` asks whether the words are on the screen, and a step is one clause of the
    answer it comes from, so the answer itself counts as one telling. That is right for a step
    handed back a turn ago; it is wrong for the ask that comes after a paragraph, where the words
    are there and the step never was: "i keep burning the bottom of my pans" / "what am i doing
    wrong" (the answer again, framed) / "how do i clean it off" was answered with a search hedge,
    because the first clause of the pan answer had now been "said" twice and the step once never.
    """
    said = step.strip()[:60].lower()
    if not said:
        return False
    for turn in memory.get("turns") or []:
        if not isinstance(turn, dict):
            continue
        reply = str(turn.get("bot") or "").strip().lower()
        if not reply or said not in reply:
            continue
        # The reply has to be the step rather than a paragraph that carries it: a step is at
        # least a third of the line it is handed back as, and a sentence of a long answer is not.
        if len(said) * 3 >= len(reply):
            return True
    for line in memory.get("repeated") or []:
        if said in str(line or "").lower():
            return True
    return False


# "make it short", "shorter please", "in one line", "tldr": the person is not asking a new
# question, they are asking for the answer they already have with the detail taken out. It names
# nothing of its own, so it is answered from the last answer's own lead - no lookup, and no hedge
# a turn after the bot has just answered properly.
LESS = re.compile(
    r"\b(?:make (?:it|that)|keep it|be|say it|put it|give it to me|give me it)\s+"
    r"(?:a bit |a lot |really |much |nice and )?"
    r"(?:short|shorter|brief|briefer|quick|quicker|snappy|concise)\b"
    r"|\b(?:short|shorter|brief|briefly|concisely)\s+please\b"
    r"|\b(?:shorter|tldr|tl;?dr|summarise|summarize|sum it up|sum up|short version|"
    r"cut it down|cut to the chase|get to the point|skip the detail|less detail|"
    r"in (?:a|one) (?:sentence|line)|one line|just the (?:gist|answer|short version))\b"
    # Asking for the same answer in words they can use is the same request as asking for it
    # shorter, and it is how most people word it: "make it simpler", "in plain english",
    # "explain it like im 5", "no jargon please". None of these asks anything new, and the words
    # gate in `asks_for_less` still holds, so a line that names something of its own keeps its own
    # reading: "can you make a simpler cake" and "how do i make my essay shorter" are not this.
    r"|\b(?:simpl(?:e|er|ify|ified)|in plain (?:english|terms|words)|plain english|"
    r"(?:in )?simple (?:english|terms|words)|no jargon|jargon[- ]free|layman'?s? ?terms?|"
    r"explain (?:it|that)(?: (?:all )?(?:again|to me))? (?:simply|in english|in simple words)|"
    r"put it (?:simply|plainly|in plain (?:english|words))|dumb (?:it|that)? ?down|"
    r"plainly\b|like (?:i'?m|im|i am) (?:5|five))\b",
    re.I)


# The words an ask for less is made of. Anything else in the line names something, and a line that
# names something is its own question: "how do i make my essay shorter" is not this turn.
LESS_WORDS = frozenset("""make made it that keep be say put give me a bit lot really much
    nice short shorter brief briefer briefly quick quicker snappy concise please tldr tl dr
    summarise summarize sum gist answer version cut chase point skip detail details less
    sentence line one just and so ok okay right then now again too long word words
    more fewer condensed simple simpler simply simplify simplified plain english terms words
    jargon free layman laymans explain plainly like im i'm five 5 dumb dumbed easy easier wordy""".split())


# A lead handed back as the short form is the same answer, so it says so and then gets out of the
# way. The bare lead is one of the shapes: "Shorter: ..." on every turn would be a stock line.
LESS_LEADS = (
    "{short}",
    "Shorter: {short}",
    "In short: {short}",
    "Briefly: {short}",
)


# An answer the knowledge base writes can carry a lead of its own, and it is short because of it:
# "Quick: tuna pasta in 15, a frittata in 20, or a salmon traybake if you have 30 minutes." Handing
# that back under this module's lead stacks two promises in front of one answer - "Briefly: Quick:
# tuna pasta in 15 ..." - which is a longer reply than the one it replaced, not a shorter one. The
# label is the answer's, and it says the same thing the lead would, so the lead steps out of the
# way. It is only a label when it is a few words and ends at a colon: "Ask early, name the dates
# and say who covers:" is the opening of an answer, not a name for it.
OWN_LEAD = re.compile(r"^[^:!?.\n]{1,45}:\s")


OWN_LEAD_WORDS = 5


def _a_lead_of_its_own(short):
    """True when the short form already opens with a label of its own ("Quick: ...")."""
    match = OWN_LEAD.match(str(short or ""))
    return bool(match) and len(match.group(0).split()) <= OWN_LEAD_WORDS


# "shorter but keep the timings", "one line, but don't leave out the water ratio": the person
# asks for less and says what the less has to keep. Read as a fresh line it reached the entry for
# softening a message somebody sends ("Softer, same point: \"But keep the timings.\"").
KEEP_CLAUSE = re.compile(
    r"\b(?:but\s+)?(?:keep|keep\s+in|leave\s+in|don'?t\s+(?:leave\s+out|drop|lose)|without\s+"
    r"(?:losing|dropping)|making\s+sure\s+(?:to\s+)?(?:keep|say))\s+(?P<what>.+)$", re.I)


# The requirement is honoured by handing back the sentence that carries it, so a word of it has to
# be a word of the answer, or the answer has to be about numbers at all ("keep the timings" is in
# the minutes, not in the word).
FIGURES = re.compile(r"\b(?:timings?|times?|numbers?|figures?|ratios?|amounts?|quantit(?:y|ies)|"
                     r"temperatures?|degrees?|weights?|measures?|proportions?)\b", re.I)


DIGIT = re.compile(r"[0-9]")


def _kept_clause(text):
    """The words a shorter version has to keep, or "" when the line names none."""
    match = KEEP_CLAUSE.search(" ".join(str(text or "").split()))
    return match.group("what").strip(" .!?,") if match else ""


# "how do i make it shorter" asks how to do something to a thing of theirs - an essay, a wait, a
# queue - and the thing is in what they said the turn before, not in the words of the ask. The
# person who wants less of the answer tells us: "make it shorter", "can you make it shorter". A
# question in this shape that names nothing still names its own verb, so it is not this turn.
HOW_TO = re.compile(
    r"\bhow\b(?:\s+\w+){0,3}\s+(?:do|can|should|would|could|might|shall)\s+(?:i|we|you)\b",
    re.I)


# Words that ask for fewer words on their own, without any of the phrasings `LESS` knows: a person
# who has just been given a paragraph and types "briefly" or "short" has asked for the short version,
# and `LESS` only knew "briefly please" and "make it short". The line still has to be made of
# nothing but these and filler, so a line that names something is never this turn.
BREVITY_WORDS = frozenset("""brief briefly short shorter concise concisely tldr gist sentence
    condensed summarise summarize sum version line""".split())


def asks_for_less(text):
    """True when the whole line, bar what it says to keep, is a request for a shorter answer."""
    clean = " ".join(str(text or "").split())
    if not clean:
        return False
    if HOW_TO.search(clean):
        return False
    asked = KEEP_CLAUSE.sub("", clean) if KEEP_CLAUSE.search(clean) else clean
    said = topics.words(asked)
    left = [w for w in said
            if w not in LESS_WORDS and w not in FILLER and w not in ASK
            and w not in ASK_VERB and w not in topics.STOPWORDS]
    if left:
        return False
    # "briefly", "short", "condensed" on their own: every word of the line is already an ask for
    # less, so one of the words that promises it is the whole of the reason to read it that way.
    if not (LESS.search(clean) or any(w in BREVITY_WORDS for w in said)):
        return False
    # The word has to be what the line is about, not a word in front of a thing it describes: "a
    # short book" asks for a book, and "short hair" is a haircut. Both read as an ask for less
    # until this line, because "book" is a verb the ask lists know and "hair" is a word the
    # topic lists drop - so the last word of the line that is not filler decides.
    settled = [w for w in (said or topics.words(clean))
               if w not in FILLER and w not in topics.STOPWORDS]
    return bool(settled) and (settled[-1] in LESS_WORDS or settled[-1] in BREVITY_WORDS)


# The answer was already one sentence, so there is nothing to take out: say so and give it back
# rather than answering a request for less with "I don't know enough to answer that".
# A request for less that says what it has to keep is answered with the sentence that keeps it.
KEEPING = (
    "Keeping {keep}: {short}",
    "With {keep} in: {short}",
)


ALREADY_SHORT = (
    "That's about as short as it gets: {short}",
    "That is the short version: {short}",
)


# Asked for a short version of a short answer they have already had in pieces: there is nothing
# left to hand back, and reading the answer out again is the one thing a shorter answer is not.
NO_SHORTER_STILL = (
    "That is the short version - there is nothing left in it to take out.",
    "Nothing left to cut: every part of that answer you have now had on its own.",
)


# A request for less on the first turn of a chat names nothing to cut down. The search hedge is
# the wrong answer to it: there is nothing to look up, and "I don't know enough to answer that"
# reads as a refusal to a person who only asked for a shorter one.
NOTHING_TO_CUT = (
    "Nothing to cut down yet - ask me something and I'll keep it short.",
    "Nothing in hand to shorten - ask away and I'll keep it brief.",
)


# Asked twice, the lead is not shorter than the answer any more, so the line is the one sentence
# of it that carries the most: the figure, the step, the condition.
JUST_THIS = (
    "Just this: {short}",
    "The one thing in it: {short}",
)


# A line that opens a chat has nothing in it to cut down, and handing back less of "Hi, good to
# meet you" answers nothing - and the composer speaks as the fallback module, so the greeting's own
# lines carry that module's name too. The one line of the greeting that is an answer is a draft
# handed over inside its own quotation marks ("Here's something you could send: ..."), so the name
# is skipped only when the line holds no draft, and `_the_quotation` is what reads the draft.
WELCOMES = "greeting"


def _recent_lines(memory):
    """The bot's own recent lines that said something, newest first, with how many turns ago.

    Wider than `_recent_answers`: a request for less is about whatever the bot just said, and the
    line can be the small-talk answer as easily as a knowledge one ("i feel a bit low" / "make it
    short"). A greeting, a hedge, a question back and a line too short to have any detail in it
    are all still left out. The count is of lines that said something, not of turns: after two
    hand-backs the answer they came from is still the line in hand, and counting the hand-backs
    would put it out of reach of a third request for less.
    """
    out = []
    for turn in reversed((memory.get("turns") or [])[-LOOK_BACK_FOR_LESS:]):
        if not isinstance(turn, dict):
            break
        said = str(turn.get("bot") or "").strip()
        if not said or HEDGE.search(said):
            continue
        if turn.get("module") == WELCOMES and not _the_quotation(said):
            continue  # a hello has nothing to shorten; a draft it handed over does
        if said in (memory.get("repeated") or []):
            continue  # our own hand-back: saying it again under another lead-in stacks them
        if len(said.split()) < 6 or said.rstrip().endswith("?"):
            # A short answer is still the answer: "About 500 g of chicken each." is what a
            # request for less gets handed back with "that is as short as it gets", and skipping
            # it left the line answered with "nothing to cut down yet" a turn after an answer.
            continue
        out.append((len(out) + 1, said))
    return out


# A sentence ends on its full stop, question mark or semicolon, and the closing quote mark after
# one belongs to it: "week." is the end of the sentence, not a mark inside the next one.
SENTENCE_END = re.compile(r"([.!?;][\"\u201d]?)\s+")


def _sentences(said):
    """The sentences of a line, split only where the line is not inside a quotation.

    A quotation is one unit: an answer that shows the person what to write has a question mark in
    it, and splitting there cut the message in half - "Shorter: Ask early, name the dates and say
    who covers: "Could I take 12-16 May off?" is a short answer that stops inside the sentence it
    is quoting, and the next request cut the other way, starting mid-quote with the closing mark
    left on it. So a boundary only counts once the quotes before it pair up.
    """
    text = str(said or "").strip()
    out, last = [], 0
    for end in SENTENCE_END.finditer(text):
        piece = text[last:end.end()].rstrip()
        if _unbalanced(piece):
            continue
        if piece.strip():
            out.append(piece.strip())
        last = end.end()
    tail = text[last:].strip()
    if tail:
        out.append(tail)
    return out


def _most_condensed(said, memory=None):
    """The one sentence of the answer that carries the most, for a second request for less.

    A sentence already handed back is left out: after "Shorter: <the lead>", the sentence that
    carries the rest of the answer is the one thing they have not read twice, and handing back
    the lead again under a second lead-in is the one thing that makes a short answer longer.
    """
    parts = [p.strip().strip(",;:") for p in _sentences(str(said).strip())]
    parts = [p for p in parts if 4 <= len(p.split()) <= 30 and not topics.RED_FLAG.match(p)]
    parts = [p for p in parts if not _already_repeated(p, memory or {})]
    if not parts:
        # An answer written in long sentences gets its shortest one anyway: a second request for
        # less inside a 31-word sentence is still a request, and the alternative is handing the
        # whole paragraph back under a lead that promises it is short.
        long_parts = [p.strip().strip(",;:") for p in _sentences(str(said).strip())]
        long_parts = [p for p in long_parts if 4 <= len(p.split()) <= 45
                      and not topics.RED_FLAG.match(p)]
        long_parts = [p for p in long_parts if not _already_repeated(p, memory or {})]
        if long_parts:
            return min(long_parts, key=lambda p: len(p.split()))
    if not parts:
        return ""
    return min(parts, key=lambda p: len(p.split()))


# A lead that is still a paragraph is not a shorter answer: "in one line" answered with forty
# words and "Briefly:" in front of them keeps the promise in the wrong direction. The cap is
# generous on purpose - a first sentence of twenty-odd words is a real short answer - so only a
# lead nobody would call short is cut down.
SHORT_ENOUGH = 26


CLAUSE_SPLIT = re.compile(r"(?<=[,;])\s+")


# A clause that ends on one of these was cut off mid-thought: "staying active is what helps most
# and" is not a sentence, and a short answer that stops in the wrong place is worse than a longer
# answer that finishes.
CUT_MID_SENTENCE = frozenset("""and but so or because which that while with rather than to of the
    a an in on for if when as also then it its your my their there""".split())


def _short_enough(cut):
    """The answer's shorter read, trimmed to something a person would call short.

    A short lead is handed back as it is. A long one is cut at its own colon first - the place an
    answer often offers its own summary ("... and staying active is what helps most: keep walking
    ...") - and then at the last clause boundary inside the cap, never ending on a word that
    leaves the sentence hanging.
    """
    cut = str(cut or "").strip()
    if len(cut.split()) <= SHORT_ENOUGH:
        return _ended(cut)
    head = _read_up_to_the_colon(cut)
    if len(head.split()) <= SHORT_ENOUGH:
        return _ended(head)
    parts = [p.strip() for p in CLAUSE_SPLIT.split(head) if p.strip()]
    out = ""
    for part in parts:
        together = (out + " " + part).strip()
        if out and len(together.split()) > SHORT_ENOUGH:
            break
        out = together
    words = out.rstrip(",;").split()
    while words and words[-1].lower().strip(",;") in CUT_MID_SENTENCE:
        words = words[:-1]
    out = " ".join(words).rstrip(",;")
    if len(out.split()) < 6:
        return _ended(head)
    return _ended(out)


def _ended(cut):
    """A short answer cut out of a sentence still ends like a sentence.

    A cut that ends on a quotation needs no full stop of its own when the quoted sentence already
    has one: `... nothing is due that week."" is finished, and a stop after the closing mark says it
    twice.
    """
    cut = str(cut or "").strip().rstrip(",;:")
    if cut[-1:] in ".!?":
        return cut
    if cut[-1:] in "\"\u201d" and cut[-2:-1] in ".!?":
        return cut
    return cut + "."


def _unbalanced(piece):
    """True when a piece opens a quotation it does not close, so it is the middle of one.

    A straight quote is its own mark, so an odd number of them is a quotation left open; the curly
    pair is counted against itself.
    """
    said = str(piece or "")
    for opens, closes in QUOTE_PAIRS:
        if opens == closes:
            if said.count(opens) % 2:
                return True
        elif said.count(opens) != said.count(closes):
            return True
    return False


def _the_quotation(said):
    """The draft the answer handed over inside its own quotation marks, or "".

    "Here's something you could send: \"Hi, basically I want Friday off. Thanks.\"" is a draft with
    a lead in front of it, and asking for less of a message asks for the message: cutting the
    lead leaves the whole draft with a shorter introduction, which is not a short version of it.
    """
    said = str(said or "")
    for opens, closes in QUOTE_PAIRS:
        at = said.find(opens)
        while at != -1:
            end = said.find(closes, at + len(opens))
            if end != -1:
                quote = said[at + len(opens):end].strip()
                # The quote has to be most of the answer: a message to send is the quotation with
                # the bot's own lead in front of it, while advice often carries a quoted example
                # ("Ask in person with one specific thing (\"I get the formula but I can't do the
                # last question\")") and handing that back as "Just this:" is advice cut to the
                # example, which answers nothing.
                if len(quote.split()) >= 4 and len(quote.split()) * 2 >= len(said.split()):
                    return quote
            at = said.find(opens, at + len(opens))
    return ""


def _closing_the_quote(cut, said):
    """The cut, carried on to the end of the quotation it stops inside.

    A short answer may stop inside a quotation as long as it stops after it: "... say who covers:
    \"Could I take 12-16 May off? I've arranged cover with Priya.\"" reads as a whole. When the
    answer has no end for the quotation the cut is left as it is - that is the module below
    saying nothing it can shorten, not a line to invent the rest of.
    """
    cut = str(cut or "").strip()
    whole = str(said or "").strip()
    if not cut or not _unbalanced(cut) or cut not in whole:
        return cut
    rest = whole[whole.index(cut) + len(cut):]
    for end in re.finditer(r"[.!?][\"\u201d]?", rest):
        longer = (cut + rest[:end.end()]).strip()
        if not _unbalanced(longer):
            return longer
    return cut


def _read_up_to_the_colon(said):
    """The sentence, or the part of it before its own colon when that is a shorter read of it."""
    head = str(said).partition(":")[0]
    if head != str(said) and 8 <= len(head.split()) < len(str(said).split()):
        return head.strip()
    return str(said)


def _keeps(said, what):
    """The sentence of the answer that carries what the person said the short version has to keep.

    A word of the requirement first ("the water ratio" is the sentence with the mugs of water in
    it), then the figures when the requirement is about numbers ("keep the timings" is in the
    minutes, and no sentence of the answer has the word "timings" in it). Empty when the answer
    has neither, and then the lead is the short version as before.
    """
    parts = [p.strip() for p in SENTENCE.split(str(said).strip()) if p.strip()]
    words = set(topics.words(what)) - set(topics.STOPWORDS) - {"timings", "timing", "numbers",
                                                               "figures", "details"}
    named = [p for p in parts if words & set(topics.words(p))]
    if named:
        return max(named, key=len)
    if FIGURES.search(what):
        counted = [p for p in parts if DIGIT.search(p)]
        if counted:
            return counted[0]
    return ""


def shorter_for(text, memory):
    """The last answer's own lead, or None when this is not a request for less.

    Three shapes, one per ask, because the second request cannot be answered with the sentence
    the first one just gave: the lead of the answer, then the single sentence of it that carries
    the most, and then the honest "that is the short version". A request for less never changes
    the subject and never looks anything up.
    """
    if not isinstance(memory, dict) or not asks_for_less(text):
        return None
    said_any = ""
    for back, said in _recent_lines(memory):
        if back > 2:
            break
        # A semicolon is where the answer already offered a shorter read of itself ("...; a
        # pressure top-up or a reset usually sorts it"), so the lead can end there too.
        parts = [p.strip().strip(";") for p in _sentences(said)]
        said_any = said_any or said
        lead = parts[0] if len(parts) > 1 else ""
        if lead and len(lead.split()) < 8 and len(parts) > 1:
            lead = parts[1]  # "Sorry to hear that." on its own is not the answer, it is the door
        # An answer written as one long sentence still offers a shorter read of itself at its own
        # colon: "Most back pain is muscular and settles in two to six weeks, and staying active
        # is what helps most: keep walking ...". "Briefly:" in front of all of it is not a shorter
        # answer, it is the answer with a promise in front.
        if not lead:
            lead = _read_up_to_the_colon(str(said)).strip()
        kept = _kept_clause(text)
        if kept:
            # What they said to keep is the short version they asked for: nothing else is.
            carry = _keeps(said, kept)
            if carry:
                return _handed_back(memory, pick(KEEPING, memory, text).format(
                    keep=kept, short=carry))
        # A draft handed over in quotation marks is the thing to give back shorter, and it is
        # already the whole of what to send: the lead in front of it is the bot talking.
        quote = _the_quotation(said)
        if quote and quote.strip() != str(said).strip() \
                and not _already_repeated(quote, memory):
            return _handed_back(memory, pick(JUST_THIS, memory, text).format(short=quote))
        for pool, cut in ((LESS_LEADS, lead),
                          (JUST_THIS, _most_condensed(said, memory))):
            cut = _closing_the_quote(_short_enough(cut), said)
            if not cut or _unbalanced(cut):
                continue
            if cut.strip().lower() == said.strip().lower():
                continue
            if _already_repeated(cut, memory):
                continue
            line = pick(pool, memory, text)
            if line != "{short}" and _a_lead_of_its_own(cut):
                line = "{short}"
            return _handed_back(memory, line.format(short=cut))
    if not said_any:
        return _handed_back(memory, pick(NOTHING_TO_CUT, memory, text))
    if said_any:
        # It is already one sentence: there is nothing to take out, and saying so is a better
        # answer than the search hedge a turn after the bot answered properly.
        one = _most_condensed(said_any, memory)
        if one:
            return _handed_back(memory, pick(ALREADY_SHORT, memory, text).format(
                short=_ended(one)))
        # Every sentence of it has now been read out as the short version, so quoting it again -
        # whole, under a lead that promises it is short - makes the reply longer than the answer
        # it was asked to cut. What is left to say is that there is nothing left.
        return _handed_back(memory, pick(NO_SHORTER_STILL, memory, text))
    return None


# The ask for a length, and the shape of the part of an answer that gives one: "Eight weeks.",
# "about two hours", "3 minutes". A part that is nothing but one of these has everything asked for.
A_LENGTH_ASK = re.compile(r"\bhow\s+long\b|\bhow\s+many\s+(?:days|weeks|months|hours|minutes)\b",
                          re.I)


A_BARE_TIME = re.compile(
    r"^\s*(?:about|around|roughly|usually|at least|up to|only|just|no more than)?\s*"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|"
    r"thirty|forty|fifty|sixty|ninety|half an?|an?)\s*"
    r"(?:to\s+\w+\s*)?"
    r"(?:minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?)\b", re.I)


def _a_bare_time(part):
    """The part of an answer when it is nothing but the length asked for, else None."""
    if not isinstance(part, str):
        return None
    part = " ".join(part.split()).strip()
    if not part or len(part.split()) > 6 or not A_BARE_TIME.match(part):
        return None
    return part[0].upper() + part[1:]


# How far back an earlier answer is looked in for a length: the answer in hand is turn 1 and the
# detour before it, which is the shape people use.
LENGTH_BACK = 3


# A line that asks what something costs and points at it rather than naming it: "how much is that",
# "what does that cost". The ask word plus a pointer is the whole line - a line that names its own
# thing ("how much is a new boiler") is a question of its own and is left to the module that knows
# about boilers.
A_PRICE_ASK = re.compile(
    r"\bhow\s+much\b|\bhow\s+expensive\b|\bwhat\s+(?:does|do|would|will|did)\s+(?:that|it|this)\s+cost"
    r"|\bwhat\s+(?:is|was)\s+the\s+price\b", re.I)


# The pointer the line uses instead of naming the thing, and the words an ask about a price is
# made of. Anything else in the line is a thing of its own and keeps the ask for the module that
# knows about that thing.
POINTING_BACK = frozenset("that this it those these they them ones one".split())


PRICE_WORDS = frozenset("""
how much many expensive price priced cost costs costing cheap cheaper cheapest usually typical
normally roughly about approximately altogether total altogether pay paying spend spends by for
at a an the per each and so then do does did would will is was are were be be a lot really
here there again any more of on in to get got buy buying round roughly average range
""".split())


def _names_no_thing_of_its_own(text):
    """Whether the line asks about a price without naming what the price is for."""
    words = topics.words(text or "")
    if not words or not any(word in POINTING_BACK for word in words):
        return False
    return all(word in POINTING_BACK or word in PRICE_WORDS or word in topics.STOPWORDS
               for word in words)


def _the_price_the_answer_gave(text, memory):
    """The price the answer in hand stated, when the line asks what that costs, else None.

    "the boiler is old" / "should i get it serviced" ("Once a year, yes: a gas boiler service is
    usually 60 to 120 pounds ...") / "how much is that usually" was answered with the price of a
    new boiler, because the module that knows about boilers took the question and the answer on
    the screen already said the figure. An ask that points at the last answer rather than naming
    its own thing is a question about that answer, and an answer that states one price has
    nothing to choose between: that price is what it says it costs.

    Two prices are two different things ("a patch is 150 to 400, a whole roof 3,000") and the one
    the person means is not known, so an answer with two is left alone.
    """
    part = _the_price_in_hand(text, memory)
    if not part:
        return None
    if _a_length_already_handed(part, memory):
        return None
    return _handed_back(memory, part)


def asks_what_that_costs(text, memory):
    """Whether the line asks the price of the thing the answer in hand has just priced.

    The turn is this reading's in the same way a check of a fact is: the line names nothing of
    its own, so every entry about the word in it ("how much is that usually" after a boiler
    service) answers the ask by pricing its own subject instead of the figure on the screen.
    """
    return bool(_the_price_in_hand(text, memory))


def _the_price_in_hand(text, memory):
    """The bare price the answer in hand gave, when the line asks what that costs, else None."""
    line = str(text or "")
    if not A_PRICE_ASK.search(line) or narrow.kind_of(line) != "money":
        return None
    if not _names_no_thing_of_its_own(line):
        return None
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return None
    last = str(turns[-1].get("bot") or "")
    if not last:
        return None
    found = {" ".join(hit.group(0).lower().split())
             for hit in narrow.SPANS["money"].finditer(last)}
    if len(found) != 1:
        return None
    part = narrow.narrow(last, line)
    if not part or not narrow.SPANS["money"].search(part):
        return None
    part = " ".join(part.split())
    if len(part.split()) > 8:
        return None
    if not part.endswith((".", "!", "?")):
        part += "."
    return part[0].upper() + part[1:]


def _a_length_already_handed(part, memory):
    """True when this length has been handed back already in this chat.

    Once "Eight weeks." has answered "how long to train", the next length ask in the same chat is
    about a different length: "and how long to recover" was given the same "Eight weeks." - the
    time to reach 5k, handed over as the time to recover from a run, which is a confident wrong
    number where a hedge is honest. A length is spent once it has been handed over.
    """
    kept = memory.get("repeated")
    if not isinstance(kept, list):
        return False
    flat = " ".join(str(part).lower().split()).strip(" .")
    return any(flat == " ".join(str(said).lower().split()).strip(" .") for said in kept)


def _a_what_to_do_answer(memory):
    """True when the answer in hand is itself the answer to "what should i do": a plan, or the
    free time to fill.

    "What can i do with that" is a use ask - a dish, or a purpose for the thing the last answer
    was about - and repeating that answer under a lead is wrong for it. But the pronoun can point
    at the free time that was just planned: "got the day off" / "no plans yet though" / "what
    should i do with it" asks the same thing as "what should i do now", and it reached a search
    hedge. Only the answer in hand's own keys decide it: a recipe's keys name its ingredients and
    a plan's name the event or the free block, in the plans domain's own words.
    """
    from ..knowledge.plans import FREE_TIME  # noqa: PLC0415 - read only when a line asks with
    if not isinstance(memory, dict):
        return False
    answer = memory.get("entry_answer")
    if not isinstance(answer, dict):
        return False
    # Only the words that are the free time itself, or the plan of it. The whole of FREE_TIME is
    # no good here: it holds "long weekend", and "long" is a key of the answer about a journey
    # with children, so "what should we do with them" about the kids was answered with the first
    # clause of the travel answer.
    blocks = {"plan", "plans", "planning", "weekend", "weekends", "bored", "dayoff"}
    for one in FREE_TIME:
        words = [word for word in str(one).lower().split() if len(word) > 3]
        if words and all(word in blocks for word in words):
            blocks.update(words)
    return bool({str(key).lower() for key in (answer.get("keys") or ())} & blocks)


def _a_city_guide_is_the_answer_in_front(memory):
    """True when the reply on the screen is a city's list of places to go.

    A city card is a list of places, not a list of steps, so "what should we do first" after it
    asks which of those places comes first - and the city row answers that itself. Read as a step
    of the card it came back "The thing to do first: Eat lunch at 2pm like locals", which is a
    habit, not the first place. The travel cards are imported here rather than at the top because
    they are the only thing in this module that reads them, and `answers` asks the same question
    of the same helpers (see `_a_city_card_asks_which_first`).
    """
    from ..knowledge import travel  # noqa: PLC0415 - no import cycle at load
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    return travel.a_city_card_is_in_front(turns[-1].get("bot"))


_AN_ENTRY_IS_LOOKING = [False]


def _an_entry_answers_it(text, memory):
    """Whether the knowledge base has an idea of its own for this ask, rather than the answer again.

    The entries are asked the way the turn asks them - their own `respond`, on a copy of the
    memory so a probe claims nothing - and a reply that restates the answer in hand (`Same answer,
    and it covers this: ...`, `Nothing separate for suggest - it is the same advice: ...`) is not
    an idea, so it leaves the line to this reader. A reply with something new in it is the better
    answer by a long way, and this reader steps aside for it.

    The lookup is guarded against coming back into itself: `respond` asks this module whether the
    line is a repeat of the answer, and without the guard that question would return here.
    """
    if _AN_ENTRY_IS_LOOKING[0]:
        return False
    _AN_ENTRY_IS_LOOKING[0] = True
    try:
        from ..modules import answers as entries  # noqa: PLC0415 - no import cycle at load
        reply = entries.respond(str(text or ""), dict(memory or {}))
    except Exception:  # noqa: BLE001 - a lookup that fails claims no turn
        return False
    finally:
        _AN_ENTRY_IS_LOOKING[0] = False
    said = _words(reply)
    if not said:
        return False
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)] if isinstance(
        memory, dict) else []
    opening = " ".join(_words(turns[-1].get("bot") if turns else "")[:8])
    if opening and opening in " ".join(said):
        return False  # the entry is the answer in hand, said again
    return True


def _words(text):
    """The words of a line, lowercased, in order: enough to see one line inside another."""
    return re.findall(r"[a-z']+", str(text or "").lower())


def _a_bare_ask(text):
    """True when the whole line is one word asking to hear the last answer again."""
    match = BARE_ASK.match(str(text or "").strip())
    if not match:
        return False
    # "sorry" and "pardon" are the ask only as a question: "sorry" on its own is what a person
    # says to bad news, and the answer to that is not the paragraph above it.
    if match.group("word").lower() in BARE_ASK_NEEDS_A_QUESTION and "?" not in str(text or ""):
        return False
    return True


handed_back = _handed_back
