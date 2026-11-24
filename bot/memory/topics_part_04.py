"""Part 4 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re

from . import quotes as quoted
from .topics_part_01 import (
    STOPWORDS, forms, keywords, stem, is_ack, ASK_ONLY, words, _ACTION, _VERB_WORDS, _FRAME_ASK,
)
from .topics_part_03 import (
    NOT_A_QUANTITY, SENTENCE, AMOUNT_ANSWER, JOINED_ON, CLAUSE, TIME_SPAN, DURATION, SPAN_ADJECTIVE,
    WARNING_SPAN, _clauses_of, FREQUENCY, AMOUNT, PLUS_MINUTES, RATE_BY_WEIGHT, WEIGHT_IN_GRAMS,
)


HYPOTHETICAL = re.compile(
    r"\b(?:what if|what happens if|in case|if it (?:goes|doesn't|does not|fails?|sinks?|burns?)|"
    r"supposing|suppose|what would|should i risk|(?:would|will) it" + NOT_A_QUANTITY + r")\b", re.I)


# How many turns an answer stays the thing we are on. A follow-up three lines later is still about
# the subject the answer was about; one after a whole new subject is not.
ANSWER_KEPT = 4


def remember_answer(memory, reply, keys):
    """Keep the whole answer an entry gave, with the words it is keyed on.

    A later follow-up can need a sentence the answer given at the time no longer carried, because
    a follow-up is answered with one sentence of it ("how long will it take?" needs "It's a
    20-minute job", which the steps sentence does not have). Keeping the entry's own answer means
    the words are still there for the next turn.
    """
    if not isinstance(reply, str) or not reply.strip():
        return
    record = {
        "text": reply,
        "keys": sorted(str(key) for key in (keys or ())),
    }
    memory["entry_answer"] = record
    # The last few, not just the last one: a turn in between can be about the same kind of thing
    # ("what do I wear" after an interview) and its entry is keyed on the same word, so the newest
    # answer is not always the one a follow-up is asking about.
    kept = memory.get("entry_answers")
    if not isinstance(kept, list):
        kept = []
    kept.append(record)
    memory["entry_answers"] = kept[-ANSWER_KEPT:]


def entry_answer(memory, topic_text):
    """The whole answer the entry for this topic gave, while it is still what we are on.

    The answer has to have been really given - one of the last few replies opens the way it does -
    because the arbiter may have chosen another module's reply for that turn, and quoting an
    answer the person never saw would be inventing one. It also has to be about this topic: the
    line's words share a word with the entry's key words, so a tap answer is not quoted for a
    question about a phone.
    """
    turns = memory.get("turns")
    if not isinstance(turns, list):
        return None
    kept = memory.get("entry_answers")
    if not isinstance(kept, list) or not kept:
        kept = [memory.get("entry_answer")]
    mine = {form for word in keywords(topic_text) for form in (word, stem(word))}
    best, best_score = None, 0
    for record in kept:
        if not isinstance(record, dict):
            continue
        text = str(record.get("text") or "").strip()
        if not text:
            continue
        opening = " ".join(text.lower().split()[:8])
        if not any(isinstance(turn, dict)
                   and " ".join(str(turn.get("bot") or "").lower().split()).startswith(opening)
                   for turn in turns[-ANSWER_KEPT:]):
            continue  # never really said, so it is not ours to quote
        keys = set(record.get("keys") or ())
        if not keys:
            continue
        forms = {form for key in keys for form in (key, stem(key))}
        score = len(mine & forms - STOPWORDS)
        if score and score >= best_score:
            best, best_score = text, score  # on a tie the newer answer wins
    return best


# How many turns of acknowledgement are read back over to find the answer on the table. One
# turn is the "ok thanks" and the line the bot gave back to it; two allows a "thanks" then an
# "ok", which people do send in a row.
ACKED_IN_BETWEEN = 2


def answer_in_hand(memory):
    """The bot turn that answered the subject the chat is on, reading back over acknowledgements.

    "thanks", "ok" and "cheers" say nothing about what is being talked about, so they do not end
    it: after "what can i do with mince and a tin of tomatoes" and "ok thanks", "how long does
    that take" is still the ragù's question, and the answer to draw on is the paragraph before
    the thanks rather than the bot's "Glad that helped.". Only a short run of acknowledgements is
    stepped over, so a chat that really moved on keeps its last turn as the answer it is on.
    """
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return None
    index = len(turns) - 1
    stepped = 0
    while index > 0 and stepped < ACKED_IN_BETWEEN and is_ack(turns[index].get("user")):
        index -= 1
        stepped += 1
    return turns[index]


def newest_answer(memory):
    """The answer we gave most recently, while it is still one we really gave.

    A follow-up that names nothing of its own ("how long should i leave it") is about the thing
    the last answer was about, so the newest answer is the one to draw on, even when an older
    entry's key words fit the topic better.
    """
    kept = memory.get("entry_answers")
    if not isinstance(kept, list) or not kept:
        kept = [memory.get("entry_answer")]
    turns = memory.get("turns")
    if not isinstance(turns, list):
        return None
    for record in reversed(kept):
        if not isinstance(record, dict):
            continue
        text = str(record.get("text") or "").strip()
        if not text:
            continue
        opening = " ".join(text.lower().split()[:8])
        if any(isinstance(turn, dict)
               and " ".join(str(turn.get("bot") or "").lower().split()).startswith(opening)
               for turn in turns[-ANSWER_KEPT:]):
            return text
    return None


# A sentence of the last answer that is already on the screen word for word is still the right
# answer, and giving it in the same words twice in a row is what STYLE.md rules out. So it is
# said as the repeat it is, and the wording moves on with each repeat: a person asked twice does
# not say "as I said" a second time.
REPEAT = (
    "Same as before: {reply}",
    "As I said: {reply}",
    "Same again: {reply}",
)


# The words each lead-in puts in front of the answer, so a turn that already carries one is
# still the same answer when it comes round again.
REPEAT_LEADS = (("same", "as", "before"), ("as", "i", "said"), ("same", "again"))


def _carries(said, mine):
    """Whether a bot turn is this answer word for word, with or without a repeat's lead-in."""
    if not said:
        return False
    if said == mine:
        return True
    for lead in REPEAT_LEADS:
        if said == " ".join(lead) + " " + mine:
            return True
    return False


# An acknowledgement says nothing of its own: it takes the person's detail and hands the subject
# back ("Got it - you stand all day.", "Noted: your son is coming on friday."), so an answer
# either side of it is still the answer on the screen. A short *question* ("Is it worse in the
# morning?") moves the subject on, so it is not one.
ACK = re.compile(r"^(?:got it|noted|right|ok|okay|fair enough|thanks|cheers|sure|cool"
                  r"|sounds good|no problem|not a problem|any time|you're welcome"
                  r"|understood|makes sense|good to hear|lovely to hear)\b", re.I)


# An acknowledgement is also the warm one a chat replies with when it has nothing to add ("Glad
# it helped. Say the word if there's more."). It says nothing about the subject, so it does not
# take the answer off the screen. The shape has to be closed, though: "Glad that helped, and the
# parcel came." is a warm word and then something else said, which is the chat moving on, so a
# warm line that carries a clause of its own after a comma is not an acknowledgement.
WARM_ACK = re.compile(r"\b(?:glad|pleased|happy|delighted)\b", re.I)


ACK_COURTESY = re.compile(
    r"\b(?:say the word|let me know|shout if|just ask|any ?time|good luck"
    r"|hope (?:that|it|this) (?:helps|is useful|lands))\b", re.I)


# A chat also sends a person off when a subject is finished ("Alright then — good luck with it.",
# "Enjoy it!"). That says nothing about the subject either, so an answer above it is still the
# answer on the screen: "im training for a marathon in may" / "got it, thanks" / "what am i doing
# this week" read the plan back instead of handing the programme over again.
A_CLOSE = re.compile(r"\b(?:good luck|best of luck|all the best|enjoy (?:it|the rest)|have fun"
                     r"|hope (?:it|that) goes well)\b", re.I)


# The words a close is allowed to carry besides the courtesy itself. Anything else in the line is
# a fact of its own, and then the chat has moved on.
CLOSE_FILLER = frozenset("alright ok okay right well then great lovely nice and so with it that "
                         "your the rest of day time too now very much you i me a an".split())


def _only_a_close(text):
    """True when a line does nothing but send the person off ("Alright then — good luck with it")."""
    found = A_CLOSE.search(text)
    if not found:
        return False
    rest = (text[:found.start()] + " " + text[found.end():]).split()
    for word in rest:
        word = word.strip(".,!?-\u2014\u2013\"'()").lower()
        if word and word not in CLOSE_FILLER:
            return False
    return True


SHORT_TURN = 12


def only_acknowledges(said):
    """True when a bot line only acknowledges the person's own line and adds nothing.

    A reply that adds a fact of its own after a comma ("Glad that helped, and the parcel came.")
    is the chat moving on, and the answer above it is then an old answer rather than the one on
    the screen.
    """
    text = str(said or "").strip()
    if not text or len(text.split()) > SHORT_TURN:
        return False
    if ACK.match(text):
        return True
    if _only_a_close(text):
        return True
    return bool(WARM_ACK.search(text)
                and (ACK_COURTESY.search(text) or "," not in text))


# How many turns back the answer on the screen is looked for. Two answers with only an
# acknowledgement between them are still back to back; a real turn in between is not.
LOOK_BACK = 3


def _hands_the_subject_back(said, memory):
    """Whether a turn answered a remark on the turn before rather than moving the subject on.

    "it cost a fortune" after the plan was given is a remark, not a new subject, and the answer
    above it is still the answer on the screen. The greeting writes down the replies it gave to
    remarks (`bot/memory/ack.py::_a_hand_back`), so a turn that said something else is never
    read as one: the check is the reply's own words, not its shape.
    """
    kept = memory.get("hand_backs") if isinstance(memory, dict) else None
    return isinstance(kept, list) and said in kept


# A figure in a line is a fact of its own: an age, a count, a weight.
FIGURE = re.compile(r"\b\d+(?:[.,]\d+)?\b")


# A content word that points back at what the answer has already said instead of naming a thing of
# its own. "can i get it back" after the bank answer has one content word, "back", and it named the
# money's return - so the line was read as a question of its own, the frame was withheld, and the
# person got the search hedge for a follow-up whose answer they had just read. A line that says "my
# back hurts" is still its own line, because "hurt" is a thing said about it.
#
# The words that ask for a *different* part ("and more", "what else", "same again", "another one")
# are deliberately not here: standing the frame down is what lets the reader under it pick the
# sentence the person has not had yet ("The bit of that answer worth doing first: ..."), and that
# is better than the opening said again.
POINTS_AT_THE_ANSWER = frozenset("""
back instead anyway though
""".split())


def _the_opening_of(reply):
    """The first sentence of an answer, which is the part a friend says when asked it again.

    The paragraph said again behind a lead-in is the answer printed twice: "can i get it back"
    after the bank answer came back as all 512 characters with "Same as before:" in front of
    them, and the person has the whole thing on the screen already. A sentence or two off the
    top is the same answer, said the way somebody says it a second time - and the long answer is
    still there to be read, and still comes back whole when the ask is a part of it (the readers
    below this floor answer that, before the frame is reached).

    A cut never stops inside a quotation: the words an answer hands over to say have full stops
    of their own, and half of them is a broken quote rather than a shorter answer
    (`quotes.closed`).
    """
    body = str(reply or "").strip()
    parts = quoted.sentences(body, SENTENCE)
    if len(parts) < 2:
        return body
    if len(parts[0]) >= 60:
        kept = parts[:1]
    else:
        kept = parts[:2]
    return quoted.closed(" ".join(part.strip() for part in kept), parts[len(kept):], body)


def said_again(reply, memory, line=None):
    """The reply, framed as the repeat it is when it is already on the screen, or None.

    A reply that is on the screen word for word is the right answer still, and saying it in the
    same words twice reads as a machine (STYLE.md, "Never answer the same way twice in a row").
    Framing it says what it is, and the lead-in moves on with each repeat so a person asking
    twice does not get "as I said" twice. An acknowledgement between ("Got it - you stand all
    day.") does not take the answer off the screen.

    With a line, only that line says whether this is the same ask again: a line that names
    something of its own ("am i allergic to nuts" after "my mums allergic to nuts") is a
    question of its own, even when the answer to it is the paragraph just given, and framing it
    would take the turn from a module that has something new to say about it (the store's "the
    allergy is your mum's, not yours"). A line that names nothing ("what should I do about it")
    is asking for the advice again, so the answer coming round again is framed.
    """
    from . import again as _frames  # lazy: `bot/memory/again` imports this module
    if _frames.carries_a_lead_in(reply):
        return None  # already framed: a lead-in is never stacked on another
    mine = " ".join(words(reply))
    if line is not None and pairing(line):
        return None  # a pairing question is not the same ask said twice
    if line is not None:
        from . import returned  # noqa: PLC0415 - same package, imported late to keep imports flat

        if returned.says_it_happened_again(line):
            # "my back is sore again" is news, not the same ask a second time: the trouble has come
            # back, and the modules that answer a return have the next step this paragraph cannot
            # know about ("Does it come and go, or is it there all the time?"). A request to be
            # reminded still looks like a repeat ("what was the headache thing again").
            return None
    if line is not None and (
            [word for word in keywords(line)
             if word not in ASK_ONLY and word not in POINTS_AT_THE_ANSWER]
            or FIGURE.search(str(line))):
        # A figure is something of its own too: "my son is losing weight" / "he is 9" told us the
        # age, and the whole card came back behind "Same as before:" - a person who has just said
        # something new is not asking again. `keywords` drops numbers, so the count is read here.
        return None
    turns = memory.get("turns")
    if not mine or not isinstance(turns, list):
        return None
    times = 0
    seen = 0
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            break
        if seen >= LOOK_BACK:
            break
        seen += 1
        said = words(turn.get("bot") or "")
        if _carries(" ".join(said), mine) or mine in " ".join(said):
            times += 1
            continue
        if _hands_the_subject_back(" ".join(said), memory) or only_acknowledges(turn.get("bot")):
            continue  # only an acknowledgement between ("Got it - you stand all day.")
        break
    if not times:
        return None  # not on the screen: it is a new sentence to this conversation
    short = _the_opening_of(reply)
    if short and " ".join(words(short)) != mine:
        # The whole answer is on the screen word for word. Saying it again in full is what a
        # machine does; the opening of it is what a person says when asked twice.
        reply = short
    return REPEAT[min(times, len(REPEAT)) - 1].format(reply=reply)


def _said_later_than(turn, record):
    """True when `turn` was said after `record` (both are topic records)."""
    mine = turn.get("turn") if isinstance(turn, dict) else None
    theirs = record.get("turn") if isinstance(record, dict) else None
    if not isinstance(mine, int):
        return False
    if not isinstance(theirs, int):
        return True  # a record that cannot be placed is the older one
    return mine > theirs


def _the_turn_we_lean_on(understood, memory):
    """The turn the reading says this line leans on, or None.

    The topic kept on memory is the first thing said about a subject and it keeps the words the
    subject was first said in ("im planning a veg patch"), while the last thing said about it can
    name the thing itself ("also i want tomatoes"). A follow-up leans on that last turn, and the
    reading has already worked out which turn it is.
    """
    lean = understood.get("leans_on") if isinstance(understood, dict) else None
    text = str(lean.get("text") or "") if isinstance(lean, dict) else ""
    wanted = " ".join(words(text))
    if not wanted:
        return None
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return None
    for back, turn in enumerate(reversed(turns[-8:])):
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("user") or "")
        if " ".join(words(said)) == wanted:
            return {"turn": len(turns) - 1 - back, "text": said, "words": words(said)}
    return None


def _the_turn_that_answered(answer, memory, keep=6):
    """The turn whose reply is `answer`, or None (the knowledge base's answers are its own words)."""
    wanted = words(answer)[:12]
    for turn in reversed((memory.get("turns") or [])[-keep:]):
        if not isinstance(turn, dict):
            continue
        if words(str(turn.get("bot") or ""))[:12] == wanted:
            return turn
    return None


# The doing word of a question is the asking, not the thing. "how do i stop it squeaking" after
# a boiler answer shares only the word "stop" with that answer's "stop topping it up", and the
# shared verb made the boiler's sentence the answer this line "belonged to", so the door just
# asked about was answered with "If it keeps dropping, there's a leak somewhere". The subject of
# a line is in its nouns; the verb is how it is asked about.
_ASKING_VERBS = frozenset(_VERB_WORDS) | frozenset(_ACTION)


def _answer_about(line, memory, keep=6):
    """The most recent earlier answer this line's own words belong to, or None.

    A follow-up that names a thing ("how long for a hard boiled one") can come after a turn on
    something else ("my tap is dripping"), and the last answer is then the wrong answer to draw
    on. Measured on the words the line brings, not on what the topic says, so a line that names
    nothing of its own is still read from the answer just given.
    """
    # The words of the ask itself ("how long should that take") belong to every answer that
    # gives a figure, so they cannot be what ties this line to an older one: "and how long
    # should that take?" after the leg of lamb matched the chicken answer on the word "takes"
    # and handed back the chicken times for the lamb.
    asking = bool(_FRAME_ASK.search(line.lower()))
    wanted = frozenset(stem(word) for word in keywords(line)
                       if word not in ASK_ONLY
                       and not (asking and stem(word) in _ASKING_VERBS))
    if not wanted:
        return None
    turns = [turn for turn in (memory.get("turns") or [])[-keep:] if isinstance(turn, dict)]
    if len(turns) < 2:
        return None
    last = str(turns[-1].get("bot") or "")
    last_score = len(wanted & frozenset(stem(w) for w in keywords(last)))
    best, best_score = None, last_score
    for turn in turns[:-1]:
        if turn.get("module") != "answers":
            continue
        said = str(turn.get("bot") or "")
        score = len(wanted & frozenset(stem(w) for w in keywords(said)))
        if score > best_score:
            best, best_score = said, score
    return best


def answer_about(line, memory):
    """The earlier answer this line's own words belong to, when it is not the one just given.

    A public read of `_answer_about` for the knowledge base: the part-reader cuts a part out of
    the answer just given, and a line naming words of an answer from two turns back ("and how long
    in the oven" after the cake, with a turn about the frosting in between) is asking about that
    one, not about this one.
    """
    return _answer_about(line, memory)


def _the_trip_of_theirs(text):
    """The places a line of theirs says they are going to, or an empty set.

    The store already reads a plan and the place in it ("im off to cornwall next week" is a
    plan, Cornwall is its place), so this asks it rather than guessing at the words again. A
    line with no plan of its own is not a trip: "my sister is going to rome" says where she is
    going, and the answer about her trip is still the answer to the chat's own.
    """
    from . import facts  # lazy: the store's own reader, not a second guess at the words
    found = facts.extract(text) or {}
    if not found.get("plan"):
        return set()
    return {str(place).strip().lower() for place in found.get("places") or [] if str(place).strip()}


def the_place_they_are_on(memory):
    """The place of the newest trip they have started on, or an empty set.

    The current line comes first when the store has already noted it, and the turn before it is
    read when the current line names no trip: "what should i do there" carries the trip it points
    at, and that is the trip the chat is on.
    """
    turns = [turn for turn in (memory.get("turns") or [])
             if isinstance(turn, dict) and turn.get("user")]
    # A line that put something right does not name the trip it leaves behind: "actually its
    # cornwall we go to" carries the place and no trip of its own, and the rome line before it is
    # the one the words fit best. The plan the store now holds is the trip, so it is read first.
    corrected = isinstance(memory, dict) and bool(memory.get("correction"))
    if not corrected:
        for turn in reversed(turns[-2:]):
            here = _the_trip_of_theirs(str(turn.get("user") or ""))
            if here:
                return here
    # The trip the store is holding, when the turns name none or have just been corrected: it is
    # the store's plan that says which trip the chat is on, and the answer about the place they
    # left has to be told from it.
    plan = (memory.get("user") or {}).get("plan") if isinstance(memory, dict) else None
    if isinstance(plan, str) and plan.strip():
        here = _the_trip_of_theirs("we are going to " + plan.strip())
        if here:
            return here
    return set()


def about_a_place_they_left_behind(answer, memory):
    """True when the answer on the table is about a place they are no longer going to.

    "im going to rome in may", the weather in Rome, then "im off to cornwall next week": the
    next line, "what should i do there", was handed the Rome weather sentence - "Take a layer
    either way: evenings are cooler than the afternoon" - which is a fact about a city they are
    not going to, said with no sign that the trip had changed. A wrong fact is worse than none,
    so an answer that names a place they have moved off is not lent to the new trip.
    """
    here = the_place_they_are_on(memory)
    if not here:
        return False
    told = {str(place).strip().lower()
            for place in ((memory.get("user") or {}).get("places") or []) if str(place).strip()}
    left = told - here
    if not left:
        return False
    return bool(left & set(words(str(answer or ""))))


# A line that asks for the rate something is done at, and nothing else: "and how often", "how
# many times a week". Its answer is a phrase of the answer on the table, not a sentence of it.
ASKS_A_FREQUENCY = re.compile(r"\bhow (?:often|regularly|frequently)\b|\bhow many times\b", re.I)


# "what should I do about it?", "what can I do?": the person is not asking about a part of the
# answer, they are asking for the doing in it. An answer that already tells them what to do has
# that doing in one place - the instruction the sentence opens with, or the instruction after the
# colon of the sentence that explains the cause ("it is usually the washer: turn the water off").
ADVICE_ASK = re.compile(
    r"\b(?:what|anything|something|is there anything) (?:can|could|should|would|do|shall) "
    r"(?:i|we|you) (?:do|try|use)\b|\bwhat(?:'s| is) the (?:best )?(?:thing|way) to do\b|"
    r"\bwhat do i do\b|"
    # "how do I fix it", "how do I stop it hurting": the same ask written with the verb in it.
    # The answer's first sentence is usually the cause ("Most back pain is muscular and settles
    # in two to six weeks ..."), so handing that back says what they have just read and leaves
    # out the step they asked for.
    r"\bhow (?:do|can|should|could|would|might) (?:i|we) "
    r"(?:fix|sort|stop|help|ease|improve|avoid|prevent|deal with|get rid of)\b|"
    # "what helps", "what would help with that": the same ask with no "do" in it at all. The
    # answer's sentence carries both the cause and the doing ("staying active is what helps
    # most: keep walking"), so handing the sentence back whole repeats what they have just
    # read; the doing after the colon is the answer.
    r"\bwhat (?:would |could |might |will |does |do )?(?:help|helps|helped|works|worked)\b|"
    r"\bwhat (?:should|can|could|would) (?:i|we) (?:put|set|have) in place\b", re.I)


# "what can I do with leftover rice" names a thing of its own and is a question about that thing,
# not about the answer just given. "about" and "to" point back at the answer ("what can I do
# about it", "what can I do to stop it").
ADVICE_NAMES_A_THING = re.compile(
    r"\b(?:do|try|use)\s+(?:with|for|in|on)\s+"
    r"(?!(?:it|that|this|them|these|those)\b)", re.I)


# "what can i have with it" asks what to pair with the thing, not for the last answer again.
# The pairing verb and the pronoun name a relation, so the line is not a bare ask even though
# every word in it is otherwise an ask word. "what can i do about it" is not one of these: after
# the posture answer, repeating the steps is the right reply.
PAIRING = re.compile(r"\b(?:have|eat|drink|serve|pair|put|go(?:es)?)\s+(?:with|alongside)\s+"
                     r"(?:it|that|this|these|those|them)\b", re.I)


# A noun of its own before the verb is what the line is about: "what sauce goes with it" after a
# pasta answer is a sauce question, and the pasta water answer was right. "jam" and "dressing"
# are the same shape, and "what can i have with it" has no such noun.
PAIRING_OWN = re.compile(r"\b(?:sauce|gravy|dressing|dip|jam|relish|chutney|salsa|mayo|"
                         r"mayonnaise|mustard|ketchup|wine|beer)\b", re.I)


def pairing(text):
    """True when the line leans on the pairing verb alone, with no noun of its own."""
    return bool(PAIRING.search(text or "")) and not PAIRING_OWN.search(text or "")


IMPERATIVE = frozenset("""
add apply avoid ask bake bleed book buy call change check chill choose clean clear close cover cut
deal don't do drink dry ease eat fill fit freeze get give go have heat hold ice keep kill leave let
lie look lower make mix offer open peel phone pick plan prune put raise remove replace rest rid ring
rinse run say see set sit soak sort speak start stay stop swap take talk tell text think throw
tighten top try turn use wait walk wash watch wear weed wipe write
""".split())


# A sentence that only sends them to someone else is the doing part of last resort: a person who
# asks what to do wants the step they can take now, not the pointer at the end of the answer.
SENDS_YOU_ON = frozenset("""see call phone ring book ask get""".split())


# A doing part can open with when or how often it is done ("Three times a week do sit-squats",
# "each night, write it down"). The words that say when are not the doing, so the instruction is
# the first word after them.
WHEN = frozenset("""once twice three four five six seven two a an every each daily nightly morning
afternoon evening night day week month year hour minute second time times""".split())


def _doing_word(text):
    words = str(text or "").split()
    for index, word in enumerate(words):
        core = word.strip(",;:-\u2014\u2013").lower()
        if core in WHEN and index < 5:
            continue
        return core
    return ""


def _opening_instruction(sentence, allow_pointer):
    """True when the sentence opens with an instruction ("Rinse it", "Three times a week, do")."""
    first = _doing_word(sentence)
    if first not in IMPERATIVE:
        return False
    return allow_pointer or first not in SENDS_YOU_ON


# A red flag is never the doing part on its own. "Get it looked at if it gives way" said to somebody
# who has just been told to ice it reads as alarm, not as the next step they asked for; the answer
# for a line that already has ordinary steps in it is to carry on with those.
RED_FLAG = re.compile(
    r"^(?:get (?:it|that|one|them|him|her) (?:looked at|checked|seen)"
    r"|have (?:it|that|one) (?:looked at|checked)"
    r"|ring (?:111|999|911|nhs 24)|call (?:111|999|911)"
    r"|go (?:to|into) (?:a&e|a and e|the hospital|hospital|the emergency department)"
    r"|see (?:a|your|the) (?:gp|doctor|nurse|pharmacist|midwife)"
    r"|speak to (?:a|your|the) (?:gp|doctor)"
    r"|if (?:it|that|they) (?:is |are )?(?:still|gets? worse|does not settle|doesnt settle"
    r"|has not settled|had not settled|keeps? (?:on|coming)))", re.I)


# The bot's own sign-off is not a step. A card that ends by asking the person for the one word
# it needs ("Say which bit is tightest and I'll go at that one", "Tell me who it is for and I
# will write yours") opens on an instruction the way a step does, so a line that asks what to do
# next was handed the bot's offer of help back: "im a bit skint this month" / "like what do i
# do about it" got "Say which bit is tightest and I'll go at that one." and nothing else. What
# the sentence says is what the bot will do once it has their answer, which is nothing they can
# act on, so it is passed over and the step behind it is looked for.
ASKS_THEM_BACK = re.compile(
    r"\b(?:tell me|let me know|say (?:which|what|how|if|when|where|who)|send me|give me|pick one)\b"
    r"|\b(?:and|then)\s+i(?:'ll| will)\b"
    r"|\?\s*$", re.I)


def _says_it_again(part, sentence):
    """True when this part of the answer is already in that sentence, nearly word for word."""
    words = re.findall(r"[a-z']+", str(part or "").lower())
    said = re.findall(r"[a-z']+", str(sentence or "").lower())
    if not words or not said:
        return False
    head = words[:6]
    for index in range(len(said) - len(head) + 1):
        if said[index:index + len(head)] == head:
            return True
    return sum(1 for word in words if word in said) >= 0.8 * len(words)


# A line that asks for a ceiling ("how much is too much", "how much can i take") wants the
# sentence that carries the ceiling, not the single dose at the front of it. A sentence with one of
# these words is the limit answer; if the whole card has one, repeating it is better than cutting
# the figure to its first clause and leaving the "4g a day" behind.
A_CEILING_ASK = re.compile(
    r"\b(?:too much|too many|max(?:imum)?|limit|how much can i (?:take|have|drink|eat)"
    r"|how many can i (?:take|have|drink|eat)|how much is safe|how many is safe)\b", re.I)


A_CEILING_WORD = re.compile(
    r"\b(?:at most|no more than|max(?:imum)?|limit|up to|not (?:more|over)|safe|ceiling)\b",
    re.I)


_A_RATE = re.compile(
    r"\b(?:a|an|per|each|every)\s+(day|week|month|year)\b"
    r"|\b(daily|weekly|monthly|yearly|annually)\b", re.I)


def _the_rates_in(text):
    """The periods a line or sentence puts a figure over: {"day"}, {"week", "year"}."""
    out = set()
    for found in _A_RATE.finditer(str(text or "")):
        for word in found.groups():
            if word:
                out.add(word.lower().rstrip("s"))
    for word, one in (("daily", "day"), ("weekly", "week"), ("monthly", "month"),
                      ("yearly", "year"), ("annually", "year")):
        if re.search(r"\b" + word + r"\b", str(text or ""), re.I):
            out.add(one)
    return out


def _a_rate_that_fits(line, sentence):
    """False when the line asks for a daily amount and the sentence gives a single item's.

    "how much sugar is in a can of cola" then "how much sugar should i have a day" was answered
    with the can's 35g: the figure is real, but it is not the daily amount asked for. A sentence
    with no period at all can still answer a period ask when the line is only "how much"; this
    check is for a line that names its own period.
    """
    asked = _the_rates_in(line)
    if not asked:
        return True
    given = _the_rates_in(sentence)
    return bool(asked & given) or not given


def _a_comma_that_ends_a_clause(sentence, start):
    """The first comma after `start` that is not inside a figure, or -1.

    The clause cut out of a sentence ends at a comma, but "£20,000 on a £200,000 home" has a
    thousands comma in the middle of each figure. A comma with a digit on both sides is part of
    the number, not the end of the clause.
    """
    at = sentence.find(",", start)
    while at >= 0:
        before = sentence[at - 1] if at else ""
        after = sentence[at + 1] if at + 1 < len(sentence) else ""
        if not (before.isdigit() and after.isdigit()):
            return at
        at = sentence.find(",", at + 1)
    return -1


def _pick_amount(sentences, memory, line=""):
    """The sentence of an answer that gives a figure in a unit, or the clause with it.

    "how much should i take" after a melatonin answer wants "1 to 2 mg", and the answer's
    pharmacist warning shares the verb "take" with the line while carrying no amount. The first
    sentence with a unit is the amount; when it is already on the screen word for word, the
    clause around the figure is still news. A line that asks for the ceiling ("how much is too
    much") keeps the whole sentence, because cutting at the first comma would drop the "4g a day".
    """
    screen = " ".join(words(str((memory.get("turns") or [{}])[-1].get("bot") or ""))) \
        if isinstance(memory, dict) else ""
    wants_limit = bool(A_CEILING_ASK.search(str(line or "")))
    if wants_limit:
        for sentence in sentences:
            if AMOUNT_ANSWER.search(sentence) and A_CEILING_WORD.search(sentence):
                return sentence
        for sentence in sentences:
            if AMOUNT_ANSWER.search(sentence):
                return sentence
    named = [word for word in keywords(line) if len(word) > 2 and word not in ASK_ONLY]
    for sentence in sentences:
        # A sentence of the paragraph just given is already on the screen even though the whole
        # reply is longer, so it counts as said and the clause with the figure is used instead.
        if (AMOUNT_ANSWER.search(sentence) and " ".join(words(sentence)) not in screen
                and _a_rate_that_fits(line, sentence)):
            if named and not any(word in keywords(sentence) for word in named):
                # The line names something of its own that the sentence never mentions: it is
                # asking about a different thing, not for this figure. "how much should i keep
                # for emergencies" is not the £1,000 first rung of a plan already on the screen.
                continue
            if not _the_rates_in(line) and _the_rates_in(sentence) and re.search(
                    r"\bone\b", str(line or ""), re.I):
                # "how much does one cost" asks the price of the one thing; a yearly running
                # cost is a different figure.
                continue
            return sentence
    for sentence in sentences:
        found = AMOUNT_ANSWER.search(sentence)
        if not found or not _a_rate_that_fits(line, sentence):
            continue
        if named and not any(word in keywords(sentence) for word in named):
            continue
        if not _the_rates_in(line) and _the_rates_in(sentence) and re.search(
                r"\bone\b", str(line or ""), re.I):
            continue
        before = max(sentence.rfind(":", 0, found.start()),
                     sentence.rfind(";", 0, found.start()))
        after = _a_comma_that_ends_a_clause(sentence, found.end())
        start = before + 1 if before >= 0 else 0
        end = after if after >= 0 else len(sentence)
        part = sentence[start:end].strip(" .,;:")
        if part and len(part.split()) >= 2:
            return part[:1].upper() + part[1:] + "."
        return sentence
    return None


def said_on_its_own(sentence):
    """`sentence` without the word that joined it to the sentence before, or None.

    A sentence handed to the person alone is read alone, so "Then take one small step" and "So
    keep the tin in the cupboard" open on a "then" and a "so" that have nothing in front of them.
    """
    if not isinstance(sentence, str):
        return sentence
    said = sentence.strip()
    if not said:
        return None
    joined = JOINED_ON.match(said)
    if joined:
        said = said[joined.end():]
        if said:
            said = said[:1].upper() + said[1:]
    return said or None


# The clause of a cooked answer that is about afterwards - standing, resting, cooling - carries a
# time too, and it is not the time the person asked for: "then a minute in cold water" is not how
# long an egg boils. A clause that starts "so" is the total the sentence has been working towards.
AFTERWARDS = re.compile(r"\b(?:then|rest|cool|stand|leave|sit|wait|soak|drain|cold water|"
                        r"ice|fridge|freezer|oven off|heat off)\b", re.I)


TOTAL = re.compile(r"\b(?:so|takes|total|in all|altogether)\b", re.I)


def _time_of(sentence):
    """The time in this sentence that answers "how long?": the total if it works one out, and
    otherwise the first one that is not about afterwards."""
    clauses = [clause for clause in (CLAUSE.split(str(sentence or "")) or [str(sentence or "")])
               if not _not_a_length(clause)]
    first = ""
    for clause in clauses:
        spans = list(TIME_SPAN.finditer(clause))
        if not spans:
            continue
        span = spans[-1].group(0).strip(" ,;")
        if TOTAL.search(clause):
            return span
        if not first and not AFTERWARDS.search(clause):
            first = span
    if first:
        return first
    spans = [match for clause in clauses for match in TIME_SPAN.finditer(clause)]
    return spans[-1].group(0).strip(" ,;") if spans else ""


# A clause that offers one of several times for one of several results: "6 minutes for a runny
# yolk", "9 to 10 for hard". Two of them in one sentence and the answer asked for is the range.
OPTION = re.compile(r"^\s*(\d+(?:\.\d+)?(?:\s*(?:-|to|and)\s*\d+(?:\.\d+)?)?)"
                    r"\s*(minutes?|mins?|hours?|hrs?|seconds?|secs?)?\s+for\b", re.I)


def _option_range(sentence):
    """"6 to 10 minutes" when the sentence offers times for several results, else ""."""
    found = []
    for part in CLAUSE.split(str(sentence or "")):
        match = OPTION.match(part)
        if match:
            found.append(match)
    if len(found) < 2:
        return ""
    unit = next((match.group(2) for match in found if match.group(2)), "")
    if not unit:
        return ""
    first = found[0].group(1).split()[0]
    last = found[-1].group(1).split()[-1]
    if first == last:
        return ""
    # The options have to run the same way: the times in one answer are often for different
    # things, and the first and last of them are not the ends of one range. "15 to 20 minutes
    # for a chicken or a turkey, 10 to 20 for a joint of beef ... 5 to 10 for a steak" was read
    # as "15 to 10 minutes", which is no range at all. A span that runs backwards is not an
    # answer, and the clause for the thing they asked about is.
    try:
        if float(re.sub(r"[^0-9.]", "", last)) <= float(re.sub(r"[^0-9.]", "", first)):
            return ""
    except ValueError:
        return ""
    return f"{first} to {last} {unit.lower()}"


# An apostrophe inside a word is a contraction or a possessive ("It's", "don't", "the dog's"),
# never a quotation mark: counting every one of them made half the answers with an "It's" in
# them read as half a quotation and threw their time away.
QUOTE_MARK = re.compile(r"(?<![A-Za-z])'|'(?![A-Za-z])|\"")


def _quoted(part):
    """True when this clause is inside a quotation, so it is half of what someone says."""
    text = str(part or "")
    return len(QUOTE_MARK.findall(text)) % 2


# One option of several in an answer: "6 minutes for a runny yolk", "10 to 20 for a joint of
# beef". The unit is said once and the options after it leave it out. An option runs to the next
# figure, not to the next comma: "10 to 20 for a joint of beef, lamb or pork" is one option.
OPTION_ANY = re.compile(
    r"(\d+(?:\.\d+)?(?:\s*(?:-|to|and)\s*\d+(?:\.\d+)?)?)"
    r"\s*(minutes?|mins?|hours?|hrs?|seconds?|secs?)?\s+for\b", re.I)


# Words that place a step in time and say nothing about how long it takes: "A week out" is when
# a thing happens, not a length, and said on its own it is a fragment with no verb in it.
TIME_ONLY = frozenset("""a an one two three four five six seven eight nine ten eleven twelve
    day days week weeks month months year years out before ahead after now from to in on at the
    of""".split())


def _only_a_marker(part):
    """True for a clause that is nothing but where a step sits in time ("A week out")."""
    words = re.findall(r"[a-z0-9']+", str(part or "").lower())
    if not words:
        return True
    return all(word in TIME_ONLY or DURATION.match(word) for word in words)


def _duration_clauses(sentence):
    """Every clause of this sentence that carries a time, as sentences of their own."""
    parts = []
    for part in _clauses_of(sentence):
        part = part.strip(" .")
        if _quoted(part):
            # "Play peekaboo and do short practice exits - 'I'm going to the kitchen, back in a
            # minute' - and always come back" has a time in it, but cutting the clause out of
            # the quotation gives "Back in a minute'", which is half a script and not a length.
            continue
        if part.lower().startswith("then "):
            part = part[5:]  # "then roast for 40 minutes" reads as "Roast for 40 minutes."
        if part.lower().startswith("and "):
            part = part[4:]  # "... and it settles in two to three days" is "It settles in ..."
        if WARNING_SPAN.search(part):
            continue
        if not part or _only_a_marker(part):
            continue
        if _not_a_length(part):
            continue
        if DURATION.search(part) or SPAN_ADJECTIVE.search(part):
            parts.append(part[0].upper() + part[1:] + ".")
    return parts


def _only_a_cadence(part):
    """True when the only time in this clause is how often to do it.

    "a few times a day" is a cadence and not a length: the shoulder answer's "circle it slowly)
    a few times a day" was handed back to "how long will it last" as if it were how long the
    pain lasts, and a person plans around a length. A clause that also carries a length of its
    own ("ice it for 20 minutes, three times a day") keeps it.
    """
    return bool(FREQUENCY.search(part)) and not DURATION.search(FREQUENCY.sub(" ", part))


# "on a dry day with no rain forecast for 24 hours" says how long the weather has to hold, not
# how long the job takes: the forecast is a window the work has to fit in. With the treatment
# interval passed over as a rate, that 24 hours was the only time left and answered "how long
# will it take" to paint a shed.
A_WEATHER_WINDOW = re.compile(
    r"\b(?:forecast|rain|showers?|dry|damp|frost|wind|sunshine?|weather|mild|warm|cold)\b"
    r"[^.;:,]{0,25}\bfor\s+$", re.I)


def _a_window_in_the_weather(part):
    """True when every time in this clause is how long the weather has to hold."""
    found = sorted(list(DURATION.finditer(part)) + list(SPAN_ADJECTIVE.finditer(part)),
                   key=lambda match: match.start())
    if not found:
        return False
    for match in found:
        if not A_WEATHER_WINDOW.search(part[:match.start()]):
            return False
    return True


def _not_a_length(part):
    """True when the time in this clause is not how long the job takes.

    Two shapes say a different thing with a time: how often to do it ("treat it every two or
    three years") and how long the weather has to hold ("on a dry day with no rain forecast for
    24 hours"). Both were handed back as the length of the job, so "how long will it take" to
    paint a shed was answered "Two or three years." and then "24 hours." A person plans around a
    length, so a clause that says neither is passed over.
    """
    return _only_a_cadence(part) or _a_window_in_the_weather(part)


def _duration_clause(sentence):
    """The first clause of this sentence that carries the time in it."""
    parts = _duration_clauses(sentence)
    return parts[0] if parts else None


def _shorten(part):
    """A long clause with a time in it comes back as the time itself.

    The time is the answer only when it ends the clause, which is the shape of an answer about a
    length of time: "roast it for 40 minutes" is 40 minutes. A time in the middle of a sentence
    is saying something else - "one lesson a week is what makes the rest stick" is a cadence, and
    cutting it to "a week." leaves a fragment that answers nothing.
    """
    text = str(part or "")
    if len(text.split()) > 9:
        found = DURATION.search(text)
        if found and not text[found.end():].strip(" .,;:!?"):
            # The time ends the clause but not the reply: it is cut out of the middle of the
            # answer's sentence, so it starts a sentence of its own and says so.
            span = found.group(0).strip(" .")
            return span[:1].upper() + span[1:] + "."
    return part


# The period a line counts in: "how long each day", "how many hours a week". A figure counted in
# a bigger unit than the one asked for is a different figure ("a week" is not how long each day),
# and said on its own it is not an answer at all.
PERIODS = {"minute": 0, "second": 0, "hour": 1, "day": 2, "week": 3, "month": 4, "year": 5}


PERIOD_ASK = re.compile(r"\b(?:a|an|each|every|per|one)\s+"
                        r"(seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b", re.I)


# A clause that carries its time behind a verb says the doing, not the length: "repeated for 20
# minutes" to "how long each day" is 20 minutes. Only used for a period ask, where the figure
# itself is what was asked for; "boil for 10 minutes" is left as it is, because the doing is the
# only thing that says what the 10 minutes are for.
PERIOD_LEAD = re.compile(r"^(?:[a-z]+ed|takes?|lasts?|runs?)\s+(?:for|about|around|roughly)?\s*",
                         re.I)


def _asked_period(line):
    """The unit a line counts in ("how long each day" -> 2), or None when it names no period."""
    found = PERIOD_ASK.search(str(line or ""))
    if found is None:
        return None
    unit = found.group(1).lower().rstrip("s")
    return PERIODS.get(unit)


# A length of time counted on its own: a digit, or a number spelled out. The bare article is not
# one - "give each topic a day" carries a unit and no figure, and handed back as an answer it says
# "a day", which is nothing.
FIGURED = re.compile(
    r"\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|"
    r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|couple|few|several|dozen|half|quarter)\b",
    re.I)


def _in_period(part, period):
    """True when the time in this part is counted in the period the line asked for.

    A smaller unit answers a bigger period ("half an hour a week" answers "how long each week"),
    a bigger one does not: "a week" is not how long each day. A part with a unit and no figure is
    not a length of time at all, so it is never the answer to a "how long"."""
    if period is None:
        return True
    if not FIGURED.search(str(part or "")):
        return False
    found = DURATION.search(str(part or ""))
    if found is None:
        return False
    counted = found.group(0).lower()
    for name, rank in PERIODS.items():
        if name in counted:
            return rank <= period
    return False


def _step_they_asked_for(parts, wanted):
    """The last time in the answer that is not a step afterwards, unless they asked for that.

    "6 minutes for a runny yolk ... then a minute in cold water" ends on the cold water, and the
    cold water is not how long an egg boils; the same answer said to "how long should I rest it"
    is exactly the resting clause, so a clause they named is never dropped.
    """
    kept = [part for part in parts
            if not AFTERWARDS.search(part) or set(keywords(part)) & set(wanted)]
    if kept:
        return kept[-1]
    return parts[-1] if parts else None


def _time_in_words(minutes):
    """80 -> "1 hour 20", 50 -> "50 minutes". Rounded to five, the way a recipe talks."""
    minutes = int(round(minutes / 5.0)) * 5
    hours, rest = divmod(minutes, 60)
    if not hours:
        return f"{rest} minutes"
    hours_text = f"{hours} hour" + ("" if hours == 1 else "s")
    return f"{hours_text} {rest}" if rest else hours_text


def time_for_amount(answer, line):
    """The time an answer's own rate gives for the amount a follow-up names, or None.

    "20 minutes per 500g plus 20 minutes" is a rule that answers any weight, and someone who
    asks "how long for a 1.5kg one" wants the time for their bird, not the rule to work out
    themselves. Only a rate with a weight in it is worked out, only for an amount in the same
    kind of unit, and only for a total that a roast could plausibly take, so a rate that is
    not a cooking time is left alone.
    """
    amount = AMOUNT.search(str(line or ""))
    rate = RATE_BY_WEIGHT.search(str(answer or ""))
    if not amount or not rate:
        return None
    each, per, unit = rate.groups()
    said_unit = re.sub(r"[\d.\s]", "", amount.group(0)).lower()
    if said_unit not in WEIGHT_IN_GRAMS or unit.lower() not in WEIGHT_IN_GRAMS:
        return None
    want = float(re.sub(r"[^\d.]", "", amount.group(0))) * WEIGHT_IN_GRAMS[said_unit]
    base = float(per) * WEIGHT_IN_GRAMS[unit.lower()]
    if base <= 0 or want <= 0:
        return None
    total = float(each) * want / base
    extra = PLUS_MINUTES.search(str(answer))
    if extra:
        total += float(extra.group(1))
    if not 5 <= total <= 12 * 60:
        return None
    return _time_in_words(total)
