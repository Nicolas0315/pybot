"""Part 1 of 6 of a large module, split out of `arbiter`.

Everything here is re-exported from `arbiter`, so callers import it from there as before.
"""
import re

from ..compose import limit as _limit



try:  # the reading of "the next line of a hard story" and the lines it is answered with
    from ..memory import ack as _ack
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _ack = None


try:  # the one check for "does this line point back at something already said" and its reader
    from ..memory import recall as _recall
    from ..memory import repeat as _repeat
except Exception:  # noqa: BLE001 - a reader that cannot be imported just adds no rule
    _recall = _repeat = None


try:  # the reading of a death, for the rule that lifts a listening line after one
    from ..compose import loss as _loss
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _loss = None


try:  # the reading of a dream, so a dream is not a story of a death that happened
    from ..memory import dream as _dream
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _dream = None


try:  # the reading of a report that a step was already taken, and of the step it reports
    from ..memory import already as _already
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _already = None


try:  # the reading of a wish to hurt somebody, and the lines it is answered with
    from ..compose import harm as _harm
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _harm = None


try:  # whether anything was said before this line, one reading for every chat reader
    from ..memory import there_is_a_chat as _there_is_a_chat
except Exception:  # noqa: BLE001 - a reading that cannot be imported makes no claim
    _there_is_a_chat = lambda _memory: False  # noqa: E731


try:  # the shared reading of a follow-up that names nothing, and of the ask for the next move
    from ..memory import repeat as _repeat
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _repeat = None


try:  # the reading of a recall ask ("what was my target again") and the fact it names
    from ..memory import recall as _recall
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _recall = None


try:  # the one check for "does an earlier line of theirs hold what this line asks for"
    from ..memory import lineback as _lineback
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _lineback = None


try:  # the reading of the line that answers the bot's own "what's its name?"
    from ..memory import named as _naming
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _naming = None


try:  # the composer's own name for the kind of line it answers itself: one source of truth
    from ..compose.fallback import CARE_THREAD, PAUSE, THREAD
except Exception:  # noqa: BLE001 - a composer that cannot be imported has no kinds either
    THREAD, CARE_THREAD, PAUSE = "thread", "care-thread", "pause"


try:  # the composer's generic step lines, for the turn an entry already answers with a step
    from ..compose import STEP_WHEN_LOW as _STEP_WHEN_LOW
except Exception:  # noqa: BLE001 - a composer without them has no such lines to yield
    _STEP_WHEN_LOW = ()


try:  # the kitchen's own reading of a food somebody in the line will not eat
    from ..knowledge import cooking as _cooking
except Exception:  # noqa: BLE001 - a kitchen that cannot be imported just adds no rule
    _cooking = None


try:  # the composer's own reading of a thing the line rules out of the answer above
    from ..compose import ruledout as _ruledout
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _ruledout = None


try:  # whether the chat has a turn behind this one, and which replies lean on one
    from ..memory import history as _history
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _history = None


try:  # the composer's own reply to a doubt with no range behind it to judge the figure against
    from ..compose import reading as _reading
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _reading = None


# The name of the module attribute the other lanes declare, and that the arbiter itself does not:
# a module says which topics it answers with `ANSWERS = ("cooking", "food")`. The constant used to
# be called ANSWERS too, so `getattr(arbiter, "ANSWERS")` handed back the string "ANSWERS" and the
# arbiter read itself as declaring the seven letters A, E, N, R, S, S and W as topics.
DECLARED_TOPICS = "ANSWERS"


# The understanding engine's label for a line that asks to choose between named options
# ("is it worth fixing or shall i just get a new one"): see `_a_choice_the_answer_did_not_make`.
CHOICE = "choice"


# A module that answers in place of the topic entries declares `ANSWERS_INSTEAD = ("loss",
# "grief")`: it read the whole line itself and it is sure, where a topic entry only matched a
# word or a topic id of it. See `_instead`.
DECLARED_INSTEAD = "ANSWERS_INSTEAD"


DECLARED_DEFERS = "DEFERS_TO"


# A module that answers a line as it comes, whatever else proposed: it declares
# `TAKES_AS_IT_COMES = callable(text, memory) -> bool` and says yes only on the lines it read
# whole itself. See `_as_it_comes`.
DECLARED_AS_IT_COMES = "TAKES_AS_IT_COMES"


# A module that answers a line another module claims as it comes declares
# `CLAIMS_INSTEAD = callable(text, memory) -> bool`: a claim says "this line is mine, whatever
# else proposed", which is right for the lines the claimant read whole and wrong where a
# specialist has the answer the person asked for. See `_claims_instead`.
DECLARED_CLAIMS_INSTEAD = "CLAIMS_INSTEAD"


# A module that can say a line is about the conversation rather than about the world declares
# `ASKS_ABOUT_THE_CHAT(text, memory) -> bool`. The memory store has that reading already, so the
# arbiter asks it instead of keeping a second word list (see `_fit`). A module that keeps the
# same reading under a name of its own is asked through that name, so the store's gate counts
# while its file sits at the repository's size cap and cannot take the published line.
DECLARED_ABOUT_THE_CHAT = "ASKS_ABOUT_THE_CHAT"


OWN_ABOUT_THE_CHAT = "_about_this_chat"


SAFETY = 9000  # PRIORITY band that is never outvoted (see the routing lane's PRIORITY scheme)


# The top of the small-talk band: a take from underneath it is chatter giving way, a take from
# the general band and above is a module that read the line. See `_as_it_comes`.
CHATTER = 1000


RECALL = 7000  # the memory store's recall of what was said leads the turn (README, "Routing")


# A step out of the answer in hand is one clause, and built out of the answer's own words: how many
# words it may run to, and how much of it has to be the answer's words. See `_the_move_in_hand`.
MOVE_WORDS = 26


MOVE_SHARE = 0.5


# How much of the answer a reply has to run to before it is the answer read out again rather than a
# part of it: three quarters of the answer's words. A step is a fraction of an answer (a fifth of
# one, in every case this rule was written for), so the two are never close.
MOVE_WHOLE = 0.75


# ...and how long the answer in hand has to be before that test says anything. A short line has a
# short re-tell: after a twenty-word "why" answer every candidate runs to three quarters of it, so
# `MOVE_WHOLE` called all three of them the answer read out again and the shortest one won - which
# was the hedge, "There is nothing to do about it until we have looked at it". Thirty words is the
# first length where three quarters of an answer is a paragraph rather than a clause.
MOVE_ANSWER_WORDS = 30


# The kinds the composer claims for "ask how the bot itself works" are published by the composer
# (`bot/compose/fallback.py: MY_WORKINGS`). The arbiter keeps no vocabulary of its own: it asks the
# composer which kinds are its workings and reads the reading. See `_about_the_bot`.
# The band of modules that read a whole line and answer it themselves (loss, grief). A turn they
# claim is theirs: the composer's own readings only fill in below them. See `_pause_reply`.
WHOLE_LINE_BAND = 2000


WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


# The key a topic record carries its label in: the understanding engine writes "id", the
# memory store writes "label" (agreed in #general) and the first store wrote "text".
LABEL_KEYS = ("id", "label", "topic", "name", "text")


# Readings already made of the conversation's stored lines, so a turn costs one at most.
READ = {}


def _a_past_that_is_not_there(index, candidates, text, memory):
    """The chosen candidate, unless it answers a chat that has not started.

    A reply that speaks about the conversation - "welcome back, where were we", "you mentioned",
    "same as before", "good to hear, what was the best bit?", "nice one, how did the rest of it
    go?" - is about turns behind this one, and on the opening line there are none. Every pool in
    the bot is written for a chat in progress, so the same fault turns up in a dozen places; the
    fault is not in the pools but in giving a reply about a life the person has not described,
    which is one question about the conversation and not one question per module. It is asked
    here, once, after every rule has had its say, and the question itself lives in one place:
    `bot/memory/history.py::an_earlier_turn`, read by
    `bot/memory/history.py::a_past_that_is_not_there`, which the composer, the store's warmth and
    this guard all call.

    The reading takes the person's line as well as the reply. A frame like "nice one" or "good to
    hear" is right on a first line that brings something of its own ("weve booked a week in
    cornwall" is well met by "Nice one. Is it soon?"), and only wrong when the line brings
    nothing - "carry on", "as i was saying", "sorry, i got cut off". So the frame counts when the
    line points back too, which is the same reading in `bot/memory/history.py`.

    The replacement is the best of what the modules offered after the leak is taken out: a take
    from a real module, never the greeting band underneath them (a greeting is not an answer to
    anything), and never out of the safety band, which does not talk about earlier turns and whose
    candidate is the turn whatever else is on the table. Where every candidate answers something
    unsaid the turn is left as it came: the composer's own answer to that is its first-line pool
    (`bot/compose/fallback_data.py::NOTHING_SAID_YET`), offered on a first line for the same
    reason, and no reply is invented here. The guard cannot raise - a guard that raises is worse
    than no guard, because the exception would take the turn with it - so everything in it is
    inside one `try`.
    """
    if _history is None or not candidates:
        return index
    try:
        def speaks_of_a_past(reply):
            return _history.a_past_that_is_not_there(reply, memory, text)

        reply = candidates[index].get("reply") if 0 <= index < len(candidates) else ""
        if not speaks_of_a_past(reply):
            return index
        if _priority(candidates[index]) >= SAFETY:
            return index
        for other, candidate in enumerate(candidates):
            if _priority(candidate) < 0:
                continue
            if not speaks_of_a_past(candidate.get("reply")):
                return other
    except Exception:  # noqa: BLE001 - the arbiter must never lose a turn
        return index
    return index


# The length at which a reply is a whole answer rather than a nod, shared with `_said_before`.
_SAID_BEFORE_WORDS = 8


# A reply that comes from what was said before this line, rather than from the world. On a line
# that asks for something said earlier, the store's answer is the answer, whatever topic the
# line's words happen to name: "what was my goal again" after "i'm trying to save 8000 for a van"
# was read as a goal-and-habits line, and a habit card lifted over the store's "You said 8000."
# The ask is read once here, so a new wording of it is answered by the store without a specialist
# rule in each module learning it.
# The modules that answer from the chat rather than from the entries: the store, the small talk, and
# the module that says an earlier line back. An entry lifting past one of these on a word of the
# line is answering a question nobody asked.
MEMORY_MODULES = frozenset(("memory_store", "chat", "greeting", "said_back"))


def _a_recall_from_an_earlier_turn(text, memory):
    """Whether this line asks for something said earlier, and there is an earlier turn to hold it.

    `recall.ask` reads the fact-shaped asks ("what is my name", "do you remember my budget"),
    `repeat.asked_back` reads the asks for a figure the person gave ("what was my target again"),
    and `lineback.an_earlier_turn` reads every other ask for something said earlier, including the
    ones that name the kind of detail and no past act ("and what make is the boiler" against their
    "its a worcester bosch"). All three are the memory lane's readings; this only asks whether any
    of them has an answer.
    """
    if not _there_is_a_chat(memory):
        return False
    try:
        if _recall is not None and _recall.ask(text):
            return True
    except Exception:  # noqa: BLE001 - a reading that fails is not an ask
        pass
    try:
        if _repeat is not None and _repeat.asked_back(text, memory):
            return True
    except Exception:  # noqa: BLE001 - a reading that fails is not an ask
        pass
    try:
        return bool(_lineback is not None and _lineback.an_earlier_turn(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails is not an ask
        return False


def _the_kind_line_they_gave(text, memory):
    """The earlier line of theirs that gives the kind of detail this line asks for, or None.

    Read by the memory lane (`bot/memory/kinds.py`, through `bot/memory/lineback.py`), so the
    arbiter keeps no vocabulary of its own.
    """
    if _lineback is None or not _there_is_a_chat(memory):
        return None
    try:
        return _lineback.the_kind_they_gave(text, memory)
    except Exception:  # noqa: BLE001 - a reading that fails is not a reading
        return None


def _seed(candidates):
    """The seed rule: the first real candidate, or the first fallback."""
    for index, candidate in enumerate(candidates):
        if _priority(candidate) >= 0:
            return index
    return 0


def _priority(candidate):
    priority = candidate.get("priority", 0)
    if isinstance(priority, bool) or not isinstance(priority, (int, float)):
        return 0
    return priority


# The words that can sit beside a food in a reply without offering it: "no onion then", "nut-free",
# "leave the mushrooms out", "swap the lamb for chicken". A mention with one of these near it is
# the refusal being answered, not the refused food being recommended.
_REFUSAL_UNDONE = frozenset((
    "no", "not", "without", "free", "avoid", "leave", "leaves", "leaving", "left", "out",
    "instead", "swap", "swaps", "swapped", "rather", "cant", "dont", "doesnt", "didnt",
    "refuse", "refused", "refuses", "allergic", "allergy", "intolerant", "allergen", "isnt",
    "arent", "wasnt", "wont", "cannot", "never", "none", "nothing", "off", "replace"))


# A line that says the cupboard is empty is not a person refusing to eat the food: "i dont have
# any eggs" was read as a refusal, and the answer's first move ("Eggs are the whole dish there")
# was passed over for a cooking step that had nothing to do with it. A refusal this line takes
# back ("im not allergic to nuts actually, just peanuts") is not one either.
_ALLERGY_LIFTED = re.compile(
    r"\b(?:not|isnt|arent|wasnt|werent|never)\s+(?:actually\s+)?(?:allergic|intolerant)\b"
    r"|\bno\s+(?:allerg(?:y|ies)|intolerance)\b")


def _the_food_the_line_refused(text, memory):
    """The foods the line says somebody at the table will not eat, read by the kitchen.

    The kitchen's list also names what the cupboard has run out of, and reads "not allergic" as
    an allergy, so those two shapes are left out here: neither is a reason to pass over an answer.
    """
    if _cooking is None:
        return frozenset()
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict) or not understood:
        understood = {"clean": text}
    said = str(understood.get("clean") or understood.get("text") or text or "").lower()
    if _ALLERGY_LIFTED.search(said):
        return frozenset()
    if any(phrase in said for phrase in getattr(_cooking, "SHORTAGE_WORDS", ())):
        return frozenset()
    try:
        return frozenset(_cooking.refused_foods(understood))
    except Exception:  # noqa: BLE001 - a reading that fails refuses nothing
        return frozenset()


def _offers_the_food(reply, refused):
    """True when the first sentence of the reply offers a food the line refused.

    Only the first mention of each food is read, and only the words just around it: a reply that
    opens on the refusal ("No mushrooms then: leave them out", "Egg free: ...", "nut-free") has
    answered it, while "Half the plate vegetables..." has not. The first sentence is what the
    person reads before deciding whether the answer heard them.
    """
    first = re.split(r"(?<=[.!?])\s+", str(reply or "").strip(), maxsplit=1)[0].lower()
    words = [word.replace("'", "") for word in re.findall(r"[a-z']+", first)]
    for food in refused:
        names = {food, food + "s"}
        if food.endswith("y"):
            names.add(food[:-1] + "ies")
        if food.endswith("f"):
            names.add(food[:-1] + "ves")
        for place, word in enumerate(words):
            if word not in names:
                continue
            near = words[max(0, place - 5):place + 5]
            if not any(undone in _REFUSAL_UNDONE for undone in near):
                return True
            break  # the first mention is the one the answer opens on
    return False


def _offers_what_the_line_ruled_out(candidate, text, memory):
    """True when a candidate hands back the very thing the person has just ruled out.

    "what should i cook tonight" / "not curry, something else" was answered "Quick: chickpea curry
    in 25, or a sweet potato curry if you have 30 minutes" - the thing the line refused, twice -
    because the kitchen's answer outranks the composer's claim on PRIORITY, and the rule that
    passes over a reply offering a refused *food* only runs after the claims. The rule-out reading
    already knows the thing, so it is read here once and the claim is not given up to a candidate
    that offers it. A reply that names the thing in order to leave it out ("none of that was a
    curry") is answering the refusal, and keeps the turn.
    """
    if _ruledout is None:
        return False
    try:
        thing, _kept, _opening = _ruledout._rules_out_what_i_never_said(text, memory)
    except Exception:  # noqa: BLE001 - a reading that fails offers nothing
        return False
    if not thing:
        return False
    return _offers_the_food(candidate.get("reply") or "", frozenset((thing,)))


def _the_thing_the_line_ruled_out(text, memory):
    """The thing the line rules out of the answer above it, in the person's own words, or ""."""
    if _ruledout is None:
        return ""
    try:
        thing, _kept, _opening = _ruledout._rules_out_what_i_never_said(text, memory)
    except Exception:  # noqa: BLE001 - a reading that fails rules out nothing
        return ""
    return thing or ""


def _every_real_answer_offers(thing, candidates, index):
    """True when every answer above the floor hands back the thing the line just ruled out."""
    others = [candidate for candidate in candidates
              if candidate is not candidates[index] and _priority(candidate) >= 0
              and _priority(candidate) < SAFETY
              and str(candidate.get("reply") or "").strip()]
    if not others:
        return False
    return all(_offers_the_food(candidate.get("reply") or "", frozenset((thing,)))
               for candidate in others)


# A ceiling ask ("how much is too much", "how much is safe") can be answered without a figure at
# all ("no amount is safe"), so the figure test below is not used on it.
A_CEILING = re.compile(
    r"\b(?:too much|too many|max(?:imum)?|limit|safe|how much can i (?:take|have|drink|eat)"
    r"|how many can i (?:take|have|drink|eat))\b", re.I)


# Words that name no subject: a figure candidate that shares only one of these is not about the
# thing the line asks about.
GENERIC = frozenset("""
    about after again along another anything around before being better between could doing
    during enough every first found going great happy least leave might money month months never
    other people place point right should since something still take taken their there these
    thing things think those three through times today together under until usual wanted
    where which while without would wrong year years
""".split())


def _the_cut_the_line_asked_for(memory, candidates):
    """The answer above with the thing the line ruled out taken out of it, when a module offered it.

    The composer writes that cut (`bot/compose/limit.py`), and it is the answer the line asked for.
    It reads as a repeat only because most of it is the answer already on the screen, which is what
    a limit on an answer leaves.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict) or not understood.get("constraint"):
        return None
    try:
        wanted = _limit.reply_for(understood, memory)
    except Exception:  # noqa: BLE001 - a limit that cannot be worked out is read as it was
        return None
    if not wanted:
        return None
    wanted = str(wanted).strip()
    for index, candidate in enumerate(candidates):
        if str(candidate.get("reply") or "").strip() == wanted:
            return index


# A number as a person writes it: "30", "1,250", "4.5". Only the figures the person typed are
# read this way, so the guard stays on their own words rather than on every number in the bot's.
A_FIGURE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\b")


# A line that asks for a sum to be worked out rather than a sum they gave. "how much have i got
# left", "how much more do i need", "how much short am i" are sums to do, and a reply that only
# says the figure back - their income, their bill - has not done them. Where none of these words
# is in the line the ask is for the sum on record ("how much do i spend on my phone", "how much
# was it again", "how much can i spend"), and saying it back is the answer.
# A reply that works something out of their figure: "None - 10 glasses is already past the six to
# eight glasses that answer named", "£1,100 a month more rather than the £100 you have". One that
# simply names their figure again with the numbers of its own card beside it ("For 8, chilli is
# about 150 g ... 1.2 kg of mince") has not worked anything out, so it is not kept ahead.
A_WORKED_OUT = re.compile(
    r"\b(?:none|already|past|more|less|fewer|short|left|over|under|enough|comes to|works out)\b",
    re.I)


A_SUM_TO_WORK_OUT = re.compile(
    r"\b(?:left|remaining|remain|more|less|fewer|extra|another|needed|need|short|over|under|"
    r"enough|towards|altogether|in all|total)\b", re.I)


def _the_figures_they_gave(memory):
    """The numbers in the person's own recent lines, which a reply may say back without a unit."""
    if not isinstance(memory, dict):
        return frozenset()
    said = []
    turns = memory.get("turns")
    for one in (turns if isinstance(turns, list) else [])[-8:]:
        text = one.get("user") if isinstance(one, dict) else None
        if isinstance(text, str):
            said.extend(A_FIGURE.findall(text))
    return frozenset(said)


def _says_back_one_of(reply, figures):
    """True when the reply names one of the figures the person gave, in any unit or none."""
    if not figures:
        return False
    return any(one in figures for one in A_FIGURE.findall(str(reply or "")))


# The shapes a check can read out of the reply's own words and hold a candidate to. `fit` says
# None for the rest (an opinion, a condolence), and those are left exactly as they are.
# A person amending a detail of their own plan: "actually we fly in september", "no, its the
# 14th", "sorry, its july not june". The cue is what makes it an amendment rather than a question
# about the same words - "we fly in september" on its own is a statement, and only the cue says the
# earlier detail is being changed.
_AN_AMENDMENT = re.compile(
    r"^\s*(?:actually|no|nope|sorry|oh|hang on|wait|correction|scratch that|i mean|make that)\b",
    re.I)


_MONTHS = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
    re.I)


def _amends_a_detail(text, memory):
    """The months a line amends, or an empty set when the line is not an amendment.

    "actually we fly in september" four turns into a Spain chat: the answers module matched the
    word "fly" to the fruit-fly entry - the insect - and that card took the turn off the composer's
    line, which had the month they had just corrected. A knowledge entry that matched a word inside
    an amendment is about something else.
    """
    said = str(text or "").strip()
    if not said or not _AN_AMENDMENT.search(said):
        return set()
    months = {month.lower() for month in _MONTHS.findall(said)}
    return months if len(months) == 1 and memory.get("turns") else set()


def _the_candidates_that_hand_the_detail_back(months, candidates, pool):
    """The candidates whose reply says the month the line just amended, best first, or the pool.

    Where more than one reply names it, the words cannot say which one is the answer, so the order
    is left alone. Where none does, the amendment was not about the month and the reading was
    wrong - the fruit-fly card on "actually we fly in september" is a knowledge entry that matched
    the word "fly" inside the amendment, and the reply that says September is the one that heard it.
    """
    holding = [index for index in pool
               if months & {month.lower() for month in _MONTHS.findall(
                   str(candidates[index].get("reply") or ""))}]
    if len(holding) != 1:
        return pool
    return holding + [index for index in pool if index != holding[0]]


def _asks_it_back(reply):
    """True when a reply ends by asking the person something, so it picks the turn up again.

    "Nothing in that says how serious it is. ... Where is the worry?" has the shape of a yes or a
    no and says nothing about the boiler: the question at the end asks the person to say the
    doubt again. "Yes, that is how it is normally handled. What would matter is a change in it."
    answers, and keeps its turn.
    """
    said = str(reply or "").strip()
    if not said:
        return False
    last = said.replace("\n", " ").rstrip()
    cut = max(last.rfind(". "), last.rfind("! "), last.rfind("? "))
    return "?" in (last[cut + 2:] if cut >= 0 else last)


# The kinds of answer that are a doing rather than a value: the steps, the options, the pick, the
# advice. A recall of something the person already said is never one of these - it answers a
# question about a value they gave ("what did i say my budget was", "did i say when we were going")
# and nothing else.
DOING_WANTS = frozenset(("steps", "options", "pick", "advice", "howto"))


def _the_line_asks_for_a_doing(memory):
    understood = (memory or {}).get("understood") if isinstance(memory, dict) else None
    want = understood.get("wants") if isinstance(understood, dict) else None
    return want in DOING_WANTS


# A reply that hands back something the person has already said: the store's recall ("You said
# Friday."), the attribute the store restates ("You told me your budget is 100 pounds."), and the
# second time the same value comes back ("Still 40 a month."). What they already know is not the
# answer to a question about what to do next. Only the opening is read, because a recall says who
# said it before it says what.
SAID_BACK = re.compile(r"^(?:you said|you told me|you mentioned|as you said|still )\b", re.I)


def _says_what_they_already_said(reply):
    return bool(SAID_BACK.match(str(reply or "").strip()))


_NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                 "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15,
                 "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
                 "hundred": 100, "thousand": 1000}


_FIGURES = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?\b|\b(?:" + "|".join(sorted(_NUMBER_WORDS, key=len,
                                                             reverse=True)) + r")\b")


def _the_numbers_in(line):
    """The numbers a line names, digits and words counting the same."""
    said = set()
    for word in _FIGURES.findall(str(line or "").lower()):
        if word in _NUMBER_WORDS:
            said.add(float(_NUMBER_WORDS[word]))
            continue
        try:
            said.add(float(word.replace(",", "")))
        except ValueError:
            continue
    return said


def _explains_the_method(reply):
    """True when a reply says why a thing works, which is the better answer to a check on it.

    "im trying to stop biting my nails" / "i chew gum instead" / "does that actually work" was
    answered "A bitter-tasting polish from the pharmacy works because it makes you aware of the
    bite", and that is the method explained rather than the method agreed with - a person asking
    whether a thing works is served by the reason as well as by the yes. Only that shape stands
    aside; a card that sells something else ("Get a 3kW one for speed") does not.
    """
    flat = str(reply or "").lower()
    return " because " in flat and "work" in flat


def _the_figure_they_asked_back(candidates, real, memory, text):
    """The candidate that gives back the figure the line asked for, or None.

    "Is there an earlier turn?" is answered once per turn, before any module runs
    (`memory["understood"]["looks_back"]`, read by bot/memory/recall.py), and this is that answer
    used as one rule instead of a check inside each module: a line pointing back at a figure of
    the person's own gets the reply that carries the figure. Without it a module that never looks
    back answers with a figure of its own: "the flight is 4 hours" then "how many hours was the
    flight" was "Two hours.", and the same shape took "how many nights is that" after "im going
    for 5 nights" to a date card.

    Only a figure is enforced here, and only when the store holds one: a look-back whose thing has
    no figure to carry ("back to the boiler") is left to the modules, and a candidate that already
    says the figure keeps its place in the order.
    """
    if _repeat is None or _recall is None:
        return None
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict) or not understood.get("looks_back"):
        return None
    try:
        figure = _repeat.the_figure_they_gave(text, memory)
    except Exception:  # noqa: BLE001 - a reader that cannot answer adds no rule
        return None
    if not figure:
        return None
    # The highest-priority candidate that carries the figure takes the turn, whether or not it is
    # the one in front: the figure is theirs, and a module that read the line on its own gets the
    # turn back only when no candidate carries it at all.
    for index in real:
        if _repeat.carries_the_figure(figure, candidates[index].get("reply") or ""):
            return index
    return None


# "i have a chest infection" is a statement about the person, and what it asks for is what to do
# about it, not what a chest infection is. The fact that explains the thing answered it instead -
# "Pneumonia is an infection deep in the lungs that fills the air sacs with fluid ..." - because a
# named subject and a definition are a real answer to any line that names it, and the advice about
# the very same thing ("A chest infection that brings breathlessness, a fever or a cough with mucky
# stuff in it is worth getting looked at") was beside it in the pool with no word in front of it
# from the line that the definition did not have.
#
# A definition is the broad reply about the thing; advice about the thing the person has is the
# close one, so on a report the definition stands behind it. Three things keep this small:
#   * it only reads a line that reports and asks nothing ("i have gout", not "what is gout" and
#     not "i have gout how long does it last", and not "do i have gout");
#   * the definition is only moved for a reply that is about the same thing - it names the words
#     the report names - so a condition nothing advises about keeps its definition;
#   * a nod is not advice: "Noted: you have diabetes." names the word and says nothing, so it does
#     not take the turn off the fact that explains it.
A_MY_OWN_REPORT = re.compile(
    r"\b(?:i|ive|i've|we|weve|we've)\s+(?:have|has|had|got|gotten)\b", re.I)


A_REPORT_ASKS = re.compile(
    r"\?|\b(?:what|whats|why|how|when|where|which|who|is|are|was|do|does|did|can|could|should"
    r"|would|will|tell|explain|mean|means|contagious|infectious|symptom|symptoms|sign|signs"
    r"|treat|treated|treatment|long|last|lasts|serious|dangerous|fatal|cause|causes|recover"
    r"|spread|catch|test|tests|vaccine|diet|food|foods|cure|help|worried|worry|advice|tips"
    r"|avoid|prevent|dose|better|worse|normal|common|painful)\b", re.I)


# "Gout is ...", "A cataract is ...", "Type 2 diabetes is ...", but not "It is ..." or "There is".
A_DEFINITION = re.compile(
    r"^\s*(?!(?:it|there|that|this|these|those|he|she|they|you|we|i|here|what)\b)"
    r"(?:a\s+|an\s+|the\s+|type\s+\d+\s+)?[\w'-]+(?:\s+[\w'-]+){0,3}\s+(?:is|are)\s+\S",
    re.I)


# A nod back at the person, not an answer: "Noted: you have diabetes.", "Got it.",
A_REPORT_NOD = re.compile(
    r"^\s*(?:noted|got it|okay|ok\b|right|sure|nice one|i'm listening|im listening|"
    r"that sounds|thanks|cheers)\b", re.I)


A_CONTENT_WORD = re.compile(r"[a-z][a-z'-]{2,}")


REPORT_STOP = frozenset("""i im i'm ive i've we we've weve me my mine myself have has had got gotten
    the a an and or but so that this it its it's of to in on at for with from about really very
    quite just now today again too also still some any been being am is are was were do does did
    not no yes feel feeling felt think thinks thought lot bit sort kind thing things""".split())


def _the_words_the_report_names(text):
    """The content words of a report line - the thing the person says they have."""
    said = " ".join(str(text or "").lower().split())
    return tuple(word for word in A_CONTENT_WORD.findall(said) if word not in REPORT_STOP)


def _a_report_and_no_ask(text):
    """True when the line only reports that the person has something."""
    said = " ".join(str(text or "").lower().split())
    return bool(A_MY_OWN_REPORT.search(said)) and not A_REPORT_ASKS.search(said)


def _is_advice_about(reply, words):
    """True when the reply answers the report: about its thing, and not a definition or a nod."""
    said = " ".join(str(reply or "").split())
    if not said or A_REPORT_NOD.match(said) or A_DEFINITION.match(said):
        return False
    if len(said.split()) < 10:
        return False
    low = " " + re.sub(r"[^a-z0-9' ]+", " ", said.lower()) + " "
    # One word of the thing is enough: the advice for a chest infection says "a chesty cough with
    # a fever ...", and it is about exactly that report. The reply still has to be a real answer.
    return any(" " + word in low for word in set(words))


def _how_much_it_names(reply, words):
    """How many of the report's words the reply names - how close it is to what was said."""
    low = " " + re.sub(r"[^a-z0-9' ]+", " ", str(reply or "").lower()) + " "
    return sum(1 for word in set(words) if " " + word in low)


def _the_advice_over_a_definition(candidates, pool, text, chosen):
    """The candidate that advises about the thing the line reports, when the turn went to a fact.

    Reads only the pool of real answers, only when the reply that won is the definition of the
    thing the line reports, and only when another candidate answers that same thing. Returns None
    for every other line, so nothing else changes.
    """
    if len(pool) < 2 or not _a_report_and_no_ask(text):
        return None
    words = _the_words_the_report_names(text)
    if not words:
        return None
    won = candidates[chosen].get("reply") or ""
    low = " " + re.sub(r"[^a-z0-9' ]+", " ", str(won).lower()) + " "
    if not A_DEFINITION.match(won) or not any(" " + word in low for word in words):
        return None
    # The close reply is the one that names as much of the report as the definition does, and more
    # where it can. One shared word is not enough on its own - "a cough" is in the definition of a
    # fever too - so a reply that names less of what the person said stays where it is, and on a
    # tie the card that is about that thing (`answers`) is preferred to a line about the thread
    # (`chat`), which reads a word of the report and answers the shape of it rather than the thing.
    # The definition naming more of the report than the advice does is not a reason to keep it: the
    # care line for a chest infection says "a chesty cough with a fever ..." and names the thing
    # without ever saying "infection", and it is still the answer the person needs. So any reply that
    # is about the report is a candidate, and the ranking only decides which one.
    best_index, best_score, best_chat = None, 0, True
    for index in pool:
        if index == chosen:
            continue
        reply = candidates[index].get("reply")
        if not _is_advice_about(reply, words):
            continue
        score = _how_much_it_names(reply, words)
        is_chat = str(candidates[index].get("module") or "") == "chat"
        if score > best_score or (score == best_score
                                  and (best_index is None or (best_chat and not is_chat))):
            best_index, best_score, best_chat = index, score, is_chat
    return best_index


LONG_ENOUGH = 4


def _places_the_figure(reply):
    """True when the reply puts a number on the thing: a range, a price, a total.

    A card that answers a doubt about a figure names a figure of its own ("usually £60 to £120 a
    month", "the going rate is 30 to 45 pounds"). One that names the thing and no number has not
    placed the figure either, so it does not take the turn off the hand-back.
    """
    said = str(reply or "")
    if not re.search(r"\d", said):
        return False
    return bool(re.search(r"[£$\u20ac]|\b(?:a|an|per|pounds?|quid|dollars?|euros?)\b", said))


LETTERS = re.compile(r"[a-z]+")


def _says_only_the_line(reply, words):
    """Whether a reply is the line handed back, in its own words or nearly.

    The guard above asks whether the candidate in front names the subject, and an echo names it
    by construction: it is built out of the person's own words. So "she wont eat fish what can i
    cook" gave the echo "They don't eat fish." the protection and held back the dish that
    follows it, because a recipe names potatoes and eggs and never names the fish the person
    turned down. What the guard is for is an answer about something else that shares a topic
    label - the sleep card answering a school meeting - so a reply that says nothing beyond the
    line itself is not the answer the guard is there to keep.

    The test is the share of the reply's own words that the line already has: an echo is all of
    them, and an answer that carries anything new is not.
    """
    # Letters only: "don't" is the line's word too, and a contraction is not something the reply
    # brought with it.
    said = [word for word in LETTERS.findall(str(reply or "").lower()) if len(word) >= LONG_ENOUGH]
    if not said:
        return False
    had = set(word for word in (words or ()) if len(word) >= LONG_ENOUGH)
    if not had:
        return False
    fresh = [word for word in said
             if not any(word.startswith(one) or one.startswith(word) for one in had)]
    if len(said) > 8:  # a long reply carries something of its own somewhere
        return False
    return len(fresh) * 2 <= len(said)


# The words that end the opening noun phrase of a reply: the copula and the auxiliaries. Everything
# before the first of them is what the reply is about ("A blood test", "Your boiler's pressure").
FIRST_VERB = frozenset("is are was were will can could should may might must does do did has have "
                       "had".split())


# The words that carry no subject of their own, so they are not what a reply is about.
CARRIES_NO_SUBJECT = frozenset("""a an the and or but if of to in on at for with from by as it
its this that these those i me my we us our you your he she they them their not no yes so then than
just also very really quite some any all about there here out up down over under more most much
less""".split())


def _the_same_plain_word(one, other):
    """One word said the same way twice: the same letters, or the same word inflected.

    A shared pair of letters is not a shared word - "care" is not "car", "spinach" is not
    "spin", "bloody" is not "blood" - but the same word in another form still names the same
    thing, and a reply that says "toothache" for a line about a tooth is about that tooth
    (@deft-apricot in review: the toothache card stopped counting for "my tooth hurts when i
    drink tea").

    So the ending may carry an inflection - the plural spelled either way (`s`, `es`, `ies`),
    the possessive (`'s`, `s'`) - or `ache`, which is how English makes a hurt into a compound
    and the only such ending a card here is written with ("toothache"). Anything else is a
    different word: a suffix that makes a new name (`er`, `y`, `ch`, `ach`) is never read as
    the same thing.

    Named apart from `_the_same_word` further down this file, which is the older reader of a
    word's forms (`_the_forms_of`) and is the one bound at import time. Two `def`s of one name
    leave only the later bound, so the earlier one silently never runs.
    """
    if one == other:
        return True
    for word, token in ((one, other), (other, one)):
        if not word or not token:
            continue
        if token.startswith(word) and token[len(word):] in INFLECTED_ENDS:
            return True
        if word.endswith("y") and token == word[:-1] + "ies":
            return True          # berry / berries
        if word.endswith(("'s", "s'")) and token == word[:-2]:
            return True          # boiler's / boiler
        if word.endswith("s") and not word.endswith("ss") and token == word[:-1]:
            return True          # boilers / boiler
    return False


# The endings that inflect one word rather than make another: the plural either way, the
# possessive, and the one compound ending the cards are written with ("toothache" is the
# tooth's ache). "care", "catch", "spinach" and "boiler" are new names, so no ending here
# reaches them.
INFLECTED_ENDS = frozenset(("s", "es", "'s", "s'", "ache"))


# The words a bare doubt is made of: they sit in the reply ("that is the usual thing") and in
# the line the doubt inherits, and they name no subject, so they are not what the entry has to
# share.
DOUBT_WORDS = frozenset("bad normal okay fine good safe right wrong better worse serious worry "
                        "worried thing things that this it is be to a an the for of".split())


def _reads_the_doubt(candidate):
    """True when the reply in front of the entry is the composer's own ruling on the doubt.

    A bare doubt ("is that bad", "is that normal") is answered by the composer's line for it, so
    an entry that only inherits the conversation's topic stands down (`_names_the_subject`). That
    trade is only worth making when the line in front actually rules on the doubt: "is that
    normal" after "my cat sleeps a lot" gets "Yes, that is the usual thing - what to keep an eye
    on is change rather than the thing itself", which reads the doubt, where the entry it
    displaced was the human sleep card.

    Three reviewers measured what happens when the front is something else, and every one of them
    named the same fix:

    - a nod or a farewell. "Alright then - good luck with it." after "im allergic to shellfish /
      is that bad" (@grand-gopher), and "Sounds good." after "i owe about 4000 on my credit card /
      im paying 60 a month / is that enough".
    - a hand-back or a search hedge. "I cannot call that one for you" after "im thinking of
      getting a rescue dog / is that a good idea" displaced the entry that answered (@smooth-lark).
    - a note about the answer. "Nothing in that answer needs anyone yet" after "my calf hurts / is
      that bad" took the turn off the aching-joint card (@smooth-lark).
    - a floor, which asks how long and rules on nothing. "How long has it been going on?" after "i
      take ibuprofen most days / is that ok" took the turn off the dose card (@grand-gopher,
      @neat-moth).
    - a card about something else. "why does my cat scratch its ears / should i clean her ears"
      stood the earwax card down for a cat-scratch-wound card, which is a vocabulary gap rather
      than a reading (@smooth-lark's warning).

    So the test is positive rather than a list of shapes to exclude: the pools in
    bot/compose/verdict.py that rule on a doubt are named there (`RULED_BY_THE_COMPOSER`,
    `rules_on_the_doubt`), and anything else leaves the entry its turn. One rule here instead of
    five negative ones, and a pool that gains a ruling line needs no change in the arbiter.
    """
    try:
        from ..compose import fallback as composer, verdict as opinions
        said = candidate.get("reply")
        return opinions.rules_on_the_doubt(said) or composer.is_said_it_already(said)
    except Exception:  # noqa: BLE001 - a composer that cannot answer leaves the entry its turn
        return False


# A line that asks for the answer again points at what the bot said and names nothing else.
POINTS_BACK = re.compile(
    r"\b(?:did|do|does|were|was|have|had)\s+(?:you|u)\s+(?:say|said|tell|told|mention)\b"
    r"|\b(?:you|u)\s+(?:said|say|told|mentioned)\b|\bagain\b"
    # The same ask with another verb, which is how people say it when the answer was long: "explain
    # that", "go over it", "run that by me", "the last part". Each names nothing of its own - the
    # object is the last thing said, not a subject - so the frame below leaves no word behind.
    r"|\b(?:explain|talk me through|walk me through)\s+(?:it|that|this|those|them)\b"
    r"|\bgo\s+(?:over|through)\s+(?:it|that|this)\b"
    r"|\brun\s+(?:it|that|this)\s+by\s+me\b"
    r"|\bthe\s+(?:last|final)\s+(?:bit|part)\b"
    r"|\b(?:once|one)\s+more\b|\bone\s+more\s+time\b"
    r"|\b(?:i|you)\s+(?:lost|lose)\s+(?:you|me)\b")


# Every other word a repeat ask can be made of. The words left over are the line's own subject,
# and a line with one of those is a new ask that happens to point back: "when can i play football
# again" is about the football, and "how old is she again" is about the age.
REPEAT_FRAME = frozenset("""
    a again already an and earlier before bit bits but by did do does exactly explain explained
    final for go going had has have how is it just last long lose lost many me mention mentioned
    more much now of okay once one over part parts please ran run said say sayd so sorry tell that
    the them then there this through to told u us walk talk walked talked was were what when which you
""".split())


# Filled on first use from this file's frame and the store's repeat words (see `_the_repeat_frame`).
_FRAME = None


THE_ANSWER_BANDS = frozenset(("answers", "memory_store"))


def _an_answer_behind_the_ask(memory):
    """Whether the last thing the bot said is an answer, so a repeat ask has one to hand back.

    A repeat ask is the answer again, and this file holds the turn for it. Where the bot's last
    line was a nod - "that thing you said about the boiler", "sorry i lost it", "can you say it
    again" - there is no answer to say again: the store hands back "Ugh, that's a lot to carry."
    and the arbiter, told the line is a repeat, passes over the card that did read it. Saying a
    nod twice answers nothing, so a nod is not an answer behind the ask.
    """
    if not isinstance(memory, dict):
        return False
    turns = [one for one in (memory.get("turns") or []) if isinstance(one, dict)]
    said = [one for one in turns if str(one.get("bot") or "").strip()]
    if not said:
        return False
    return said[-1].get("module") in THE_ANSWER_BANDS


def _asks_for_the_answer_again(memory, text=""):
    """Whether the whole line is a pointer back at what the bot said, with no subject of its own.

    The measure words are read as a topic of their own: "how long did you say" and "when did you
    say" after a sprained ankle came back as maths-and-numbers lines, so the specialist rule let
    the ankle card repeat its whole answer while the memory store's length line - the answer to
    what was actually asked - sat behind it. A line made only of the pointer and the measure names
    no topic of its own: it is about the conversation, and the recall band answers it.
    """
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        return False
    text = str(text or understood.get("clean") or understood.get("text") or "").lower()
    if _repeat is not None and _repeat.asks_for_less(text):
        # An ask for less is an ask for the answer in shorter words, not for the same answer
        # again: "explain it simply" over the rice answer wants "Briefly: one mug of rice to one
        # and a half mugs of water...", not the whole paragraph the person just said was too
        # much. The store's shorter form and the composer's shortener keep the turn; handing back
        # the full answer here would answer the opposite of what was asked.
        return False
    if _the_store_reads_a_repeat(text, memory):
        # The store's own reading, and the only one that knows the words people use when the answer
        # went past them: it answers "i dont understand", "im confused" and "i dont have a clue
        # myself" with the answer again, and none of them is made of the pointer words this file
        # keeps.
        return True
    if _the_store_reads_an_explain_again_ask(text):
        # The store reads the whole line as its own ask for the last reply again: it has checked
        # that every word of it is a word of the ask, against the one list of them. There is
        # nothing left here to decide, and a second frame below can only lose a word it has not
        # heard of ("pardon", "come again").
        return True
    if not POINTS_BACK.search(text):
        return False
    frame = _the_repeat_frame()
    return not [word for word in re.findall(r"[a-z']+", text) if word not in frame]


def _the_repeat_frame():
    """The words a repeat ask is made of: this file's, and every word the store reads one with.

    The frame here was a second copy of the store's repeat words, and it drifted the way a second
    copy does: "pardon" and "come" were repeat words in the store and not in this frame, so the
    line was left with a subject of its own and "pardon" over the boiler answer was read as a new
    line rather than the ask to hear that answer again. One source for the words and one for the
    reading (see `_the_store_reads_a_repeat`) is the general form: a word the store accepts in an
    ask is a word this file does not count as a subject.
    """
    global _FRAME
    if _FRAME is None:
        frame = set(REPEAT_FRAME)
        try:
            from ..modules import memory_store as store
        except Exception:
            store = None
        frame |= set(getattr(store, "REPEAT_WORDS", ()) or ())
        _FRAME = frame
    return _FRAME


def _the_store_reads_a_repeat(text, memory):
    """Whether the store read the whole line as an ask for its last reply again.

    The store owns this reading: it is what decides whether its own reply is the hand-back, and it
    knows every way people write the ask. The frame in this file is the second copy of it, and a
    second copy drifts: "pardon" and "come again" are read as the hand-back's ask by the store -
    both are in its repeat words - and were not matched here, so over the boiler answer "pardon"
    was passed over as an echo and the podcast card from two turns back took the turn. Asking the
    store rather than reading the line twice is the general form of the fix: any ask the store
    answers with its hand-back is a repeat here too.
    """
    try:
        from ..modules import memory_store as store
    except Exception:
        return False
    reader = getattr(store, "asks_again", None)
    if reader is None:
        return False
    try:
        return bool(reader(text, memory))
    except Exception:
        return False


def _the_store_reads_an_explain_again_ask(text):
    """Whether the store read the line as "I did not understand that, say it again".

    `bot/memory/meant.py` is the one reading of the ask to have the last turn put another way: it
    answers "i dont understand", "im confused" and "i dont follow" with the answer again under a
    lead-in, and it does not read "i understand" as one, which a word list would. The arbiter's
    repeat frame is the pointer words ("again", "pardon", "come again") and none of these lines is
    made of them, so a card that shares a word with "understand" took the turn off the hand-back:
    over the boiled-egg answer, "i dont understand" got the warm-flannel card and over the boiler
    answer it got the forgetting entry.
    """
    try:
        from ..memory import meant
    except Exception:  # noqa: BLE001 - a memory lane that cannot be read reads no ask
        return False
    line = str(text or "").strip().lower()
    if not line:
        return False
    for name in ("MEAN", "REPEAT"):
        reader = getattr(meant, name, None)
        try:
            if reader is not None and reader.match(line):
                return True
        except Exception:  # noqa: BLE001 - a reading that fails reads no ask
            continue
    return False
