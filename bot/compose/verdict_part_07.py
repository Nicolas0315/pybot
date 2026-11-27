"""Part 7 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re

from ..memory import again as again_reply
from . import pick
from .verdict_part_01 import (
    CARE,
)
from .verdict_part_02 import (
    ASKS_THEM, FIRST_ITSELF, IMPERATIVES, AGAIN, ALL_OF_IT_LINES, ALSO_LINES, ASKED_FIRST_LINES,
    A_HOW_ASK, DOING_WITH_NO_OBJECT, EMERGENCY_CALL, HOW_TO, KNOWING_DOING, LIST_STEP_LINES,
    NOTHING_LINES, OFFER_TAKEN_LINES, ONE_THING, ONE_TURN_LINES, ONE_TURN_PLAIN_LINES,
    QUESTION_BACK_LINES, REFER, SEE, SEE_ANYWAY_LINES, SEE_NONE_LINES, SEE_NOW_LINES,
    SEE_STATED_LINES, SPEAK_UP, STEP, STEP_ALREADY_FIRST_LINES, STEP_DETAIL_LINES, STEP_KEPT_LINES,
    STEP_LINES, STEP_ONE_LINES, TIPS_AGAIN,
)
from .verdict_part_03 import (
    _last_module, _flat, UNREADABLE, _first, _say, _the_news_just_before,
)
from .verdict_part_04 import (
    _is_a_question, A_STATEMENT, CONDITIONAL_OPEN, COPULA, AN_OFFER, STEP_LONG, THE_PLEA,
    _after_a_comfort_line, _already_asked_for_a_step, _an_offer_is_waiting, _echoes_the_person,
    _ends_on_a_question, _first_clause, _last_reply, _listed, _most_of_the_line,
    _the_answer_before_that, _the_line_just_given, _the_question_asked,
)
from .verdict_part_05 import (
    _doing_word, _action_count, _stated_referral, _step, _when,
)
from .verdict_part_06 import (
    reply_for,
)


def answers_the_ask(clean, memory):
    """True when there is a knowledge answer behind the ask for this composer to read.

    A bare "is that bad" has no content of its own: the answer to it is in the bot's last line,
    and that line is worth standing aside for only when it is an answer about a thing. After a
    condolence ("my dad died last week") or a mood ("i feel low") the last line is neither, this
    composer can only shrug, and a search hedge handed to someone who has just said their dad
    died is worse than the line the chat pool would have given. The gate is the same test
    reply_for makes for itself, asked from outside: the last readable turn was a knowledge answer
    and this composer has a verdict to give about it. "how do i descale the kettle" / "is that bad"
    is advice the person asked for, not a fault, and reply_for stands aside for it - so the chat
    pool keeps that turn rather than leaving a search hedge where it had a warm line.
    """
    if _last_module(memory, past_the_nod=True) != "answers":
        return False
    return reply_for(clean, memory) is not None


# A sentence of the answer is the unit a person can act on, and it is what the one-thing ask is
# handed. The cap is what keeps an answer written as one long sentence - "Most back pain is
# muscular and settles in two to six weeks, and staying active is what helps most: keep walking
# ..." - from coming back whole: past this length the step's own clause is the shorter read.
HAND_OVER_WORDS = 42


def _the_other_thing_in_the_answer(said, step, memory):
    """A sentence of the answer above that is not the step and not already on the screen, or "".

    The answer handed over a turn ago is not all one instruction: the card on vegetables opens
    with what to do and then says what makes it work ("Roasting carrots or broccoli in a little
    oil makes them sweeter, and a dip to dunk turns it into a game"). Asked for tips, a friend
    picks that second sentence out, because it is the part the person has not acted on yet. Only
    a sentence that stands on its own is picked: not the step's own sentence, not a question, not
    the warning that ends a health answer, and not something the bot has said in an earlier turn.
    """
    from ..memory.topics import RED_FLAG
    needle = " ".join(str(step or "").split()).lower().strip(" .!?,")
    mine = _flat(said)
    seen = [_flat(turn.get("bot") or "") for turn in
            ((memory.get("turns") if isinstance(memory, dict) else None) or [])
            if isinstance(turn, dict)]
    # The answer in hand is the last thing said, so the turns before it are the ones a sentence
    # from it can have been read in already.
    earlier = [heard for heard in seen[:-1] if heard and heard != mine]
    sentences = [one for one in re.split(r"(?<=[.!?]) ", str(said or ""))]
    # The step's own sentence and everything before it are what the person has already acted on
    # or read as the answer: the tips are the sentences after it. An answer whose step could not
    # be found again starts after its opening, which is the sentence a card leads with.
    starts = [i for i, one in enumerate(sentences)
              if needle and needle in one.lower().strip(" .!?,")]
    for sentence in sentences[starts[0] + 1 if starts else 1:]:
        text = " ".join(sentence.split()).strip()
        if len(text.split()) < 6 or _is_a_question(text):
            continue
        if needle and needle in text.lower():
            continue
        if RED_FLAG.match(text):
            continue
        if ASKS_THEM.match(text):
            continue  # "Tell me what is in the fridge": the answer's own question is not a tip
        if any(text.lower() in heard for heard in earlier):
            continue  # a sentence an earlier turn already said is not one more thing
        return text
    return ""


def _step_sentence(said, step):
    """The whole sentence the answer wrote the step in, or "" when it cannot be found again.

    The step itself is the first clause of that sentence ("Give them sun"), which is the right
    unit for the pools that add an order to it. A person who asks for the one thing is owed the
    instruction, not a fragment of it: "where do i start" after the tomato answer was handed back
    "Just the one, then: Give them sun." and lost the pot, the watering and the reason, none of
    which the person has read twice. So the whole sentence is quoted, and only the pools written
    for a sentence of its own hand it over.
    """
    needle = " ".join(str(step or "").split()).lower().strip(" .!?,")
    if not needle:
        return ""
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        text = " ".join(sentence.split())
        if needle and needle in text.lower():
            return text.strip(" .!?")
    return ""


def _up_to_a_break(said, step, within):
    """The longest run of the sentence that ends on one of the sentence's own breaks.

    A person who asks for the one thing is owed the instruction, and one instruction can be a
    sentence with a colon and a dash in it: "Fill a freezer bag with white vinegar - half vinegar,
    half water if the chrome worries you - tie it over the shower head so the nozzles soak for an
    hour" is one move from start to finish, and the moves after it ("then rub them with a sponge
    and poke any blocked holes with a pin") are the next thing to do, not this one. So where the
    sentence runs past what one instruction is worth (`within`), the longest piece of it that ends
    where the answer itself breaks is handed over, and the tail is left for "what else".
    """
    words = str(said or "").split()
    if len(words) <= within:
        return said
    # The framing in front of the step is not part of it: "Most back pain is muscular and settles
    # in two to six weeks, and staying active is what helps most: keep walking..." opens on a fact
    # and puts the move after the colon, so the piece starts at the move.
    opening = " ".join(words).lower().find(" ".join(str(step or "").split()).lower())
    start = len(" ".join(words)[:opening].split()) if opening > 0 else 0
    if start and start < len(words) - 1:
        said = " ".join(words[start:])
        words = said.split()
        if len(words) <= within:
            return said
    best = ""
    for found in re.finditer(r"[,;:]|\s[-\u2013\u2014]\s", str(said or "")):
        head = str(said or "")[:found.start()].strip(" ,;:-\u2013\u2014")
        if len(head.split()) <= within and len(head.split()) > len(best.split()):
            best = head
    return best or " ".join(words[:within])


def _an_instruction_sentence(said):
    """The answer's own first instruction, for an answer `_step` could not read one out of.

    Some answers write the move as a thing rather than a verb - "A dentist or a hygienist scale
    and polish first, because most yellowing is staining on the outside" - or label it before a
    colon ("The thing to do first: write down what is actually due this week"). `_step` finds
    neither, and the one-thing ask was answered "none of it is one job to start with" about an
    answer that plainly had one. Only a sentence with something imperative in it counts, so an
    answer that really is all explanation still gets the line that says so.
    """
    from ..memory.topics import RED_FLAG
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        text = " ".join(sentence.split())
        if not text or CONDITIONAL_OPEN.match(text) or RED_FLAG.match(text) or _is_a_question(text):
            continue
        if A_STATEMENT.match(text):
            continue  # "Pay is at least the apprentice minimum wage": a fact, not a move
        if _doing_word(re.findall(r"[A-Za-z'’-]+", text)[:5]) in IMPERATIVES:
            return text.strip(" .!?")
        head, colon, tail = text.partition(": ")
        if colon and tail and (_doing_word(re.findall(r"[A-Za-z'’-]+", tail)[:5])
                               in IMPERATIVES):
            return text.strip(" .!?")
        if FIRST_ITSELF.search(text) and not COPULA.match(text) and len(text.split()) >= 5:
            # "A dentist or a hygienist scale and polish first": the move is written as the thing
            # to get done, and the sentence says it is the first one. A sentence that only says
            # what the thing is ("The first day is the worst") is not a move and is left alone.
            return text.strip(" .!?")
    return ""


def _the_answer_under_a_frame(memory):
    """The answer under the last repeat frame in the chat, or "" if there is not one.

    A repeat said by the store ("Nothing separate for friday - it is the same advice: Rehearse the
    first sixty seconds out loud ...") is not a module the composer reads, so nothing was read at
    all and the step ask after it got a search hedge. The frame is the store saying this is the
    answer already on the screen, so the answer under it is the one to read - and only that: a
    turn that is not framed is left for the store to answer, exactly as before.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return ""
    last = turns[-1]
    if last.get("module") in UNREADABLE:
        return ""
    return again_reply.unframed(last.get("bot")) or ""


# The words in front of a colon that name the thing rather than say something about it: the
# article in front of a noun is dropped, and the two words after it are the subject. Anything
# past that is the verb and what follows it ("A loo seat bangs because ...").
FRONT_LEAD = frozenset(("a", "an", "the", "my", "your", "our", "their", "his", "her", "its",
                        "one"))


# A front built on one of these names no thing of its own: "That is a few pounds, not a new
# instrument" and "It is nearly always a worn washer" are about the thing already in the chat, so
# the person has read the diagnosis and the step starts at the move. A front that does name a
# thing ("A loo seat bangs because ...") is judged by whether that thing is in the chat.
FRONT_THIS = frozenset(("it", "that", "this", "they", "these", "those", "there"))


# A front that carries the trigger is not a diagnosis but the condition the move hangs on:
# "Defrost it when the ice is more than about 5mm thick: switch it off at the wall" loses the
# number that says when to bother, and the move after the colon reads as something to do now.
FRONT_WHEN = frozenset(("when", "if", "once", "unless", "whenever", "till", "until"))


FRONT_SUBJECT_WORDS = 2


def _the_front_names_what_is_in_hand(head, line, memory):
    """Whether the subject of the clause in front of a colon is the thing this chat is about.

    The words of the chat are the line itself and what the person and the bot have already said,
    because a follow-up that names the job says "how do i fix it" and not the thing: the dripping
    tap is in the first turn, not in the ask.
    """
    words = re.findall(r"[A-Za-z'’-]+", str(head or "").lower())
    if any(word in FRONT_WHEN for word in words):
        return False
    if words and words[0] in FRONT_THIS:
        return True
    subject = [word for word in words if word not in FRONT_LEAD][:FRONT_SUBJECT_WORDS]
    if not subject:
        return False
    in_hand = set(re.findall(r"[a-z'’-]+", str(line or "").lower()))
    for part in (memory or {},) if isinstance(memory, dict) else ():
        for topic in [part.get("topic")] + list(part.get("topics") or []):
            if isinstance(topic, dict):
                in_hand.update(str(word) for word in topic.get("words") or ())
        for turn in part.get("turns") or []:
            if isinstance(turn, dict):
                in_hand.update(re.findall(r"[a-z'’-]+", str(turn.get("user") or "").lower()))
    for word in subject:
        if word in in_hand:
            return True
    return False


def next_step(clean, memory):
    """A bare "what should i do" or "should i see someone", answered from the advice given."""
    flat = _flat(clean).strip(" .!?")
    bare = bool(STEP.match(flat))
    # A speak-up is about the thing in hand ("should i say something", "should i mention it"),
    # and the step the last answer gave is what they would say. A line that brings somebody new
    # is not that ask: "my knee clicks when i climb stairs" / "should i text him back" asked
    # what to do about a person nobody has introduced, and the knee answer's step came back.
    someone_new = (memory.get("understood") or {}).get("someone_new") \
        if isinstance(memory, dict) else None
    asks_step = bare or (bool(SPEAK_UP.match(flat)) and not someone_new)
    asks_who = bool(SEE.match(flat))
    # A plea for tips is read this way only when the answer above is the knowledge base's: a warm
    # chat line ("guard one evening this week that's just yours") is not a list of steps, and
    # pointing a person back at it as one would be the same fault the tips pool has.
    plea = bool(TIPS_AGAIN.match(flat) or ONE_THING.match(flat))
    # A plea for tips is not the ask for the first move, even though both want the answer above
    # read: "any tips" asks for something more than the card, and "where do i start" asks for the
    # one thing out of it. The difference decides whether the step is quoted below.
    tips = bool(TIPS_AGAIN.match(flat))
    # "how do i prepare" with the talk in hand asked the same question the answer above answered,
    # so it is a step ask and not a line for the base to fail on: the doing names no thing of its
    # own ("how do i cook rice" does, and is the knowledge base's).
    how_to = HOW_TO.match(flat)
    how_to_asked = bool(how_to) and (
        how_to.group("doing") in DOING_WITH_NO_OBJECT
        or (how_to.group("obj") and how_to.group("doing") not in KNOWING_DOING))
    if how_to_asked:
        asks_step = True
    if plea and _last_module(memory) == "answers":
        asks_step = True
    # "whats the safest way", asked one line after the answer said how: the same ask as a plea for
    # tips, and it was answered "That's beyond what I know well ... a search should sort you out".
    if A_HOW_ASK.match(flat) and _last_module(memory) == "answers":
        asks_step = True
    if not (asks_step or asks_who):
        return None
    said = _last_reply(memory, past_the_verdict=True) or _the_answer_under_a_frame(memory)
    if not said:
        return None
    if _first(said, AGAIN) is not None:
        # The answer above came back framed as the repeat it was ("Nothing separate for friday -
        # it is the same advice: Rehearse the first sixty seconds out loud ..."). The step is in
        # the answer under the lead-in, and somebody who has read it twice and asks how to
        # prepare wants that step, not a search hedge. With nothing under the frame there is no
        # step to give, and the turn is not this one's.
        said = again_reply.unframed(said)
        if not said:
            return None
    if EMERGENCY_CALL.match(said.strip()):
        # "should i call 999" after an answer that said to ring for an ambulance is the emergency
        # reader's line, not a step quoted back: the answer's own words for the first move are
        # "Ring now rather than waiting to be sure" once its colon is cut, and half of an
        # emergency instruction is worse than none of it.
        return None
    when = _when(said)
    if asks_who:
        if when:
            return _say(SEE_NOW_LINES, memory, flat, when=when)
        stated, kind = _stated_referral(said)
        if stated:
            # The answer named the point where it wants a person, so the answer is that point and
            # not this composer's own guess at one.
            pool = SEE_NOW_LINES if kind == "clause" else SEE_STATED_LINES
            return _say(pool, memory, flat, when=stated)
        if REFER.search(said):
            return pick(SEE_ANYWAY_LINES, memory, flat)
        if _first(said, CARE) is not None:
            return pick(SEE_NONE_LINES, memory, flat)
        return None
    step = _step(said)
    if not step and _ends_on_a_question(said):
        # The bot's last line was its own question, so the line above is a question and not an
        # answer, and there is no step in it. "i want to lose weight" / "i hate exercise" / "what
        # should i do first" came back with "Start with what I asked: what is the worst bit of
        # it?" - the bot asking its own question again - while the answer before it still had the
        # step the person was asking for. A friend hands over the step, so the step is taken from
        # the last line that was an answer.
        step = _step(_the_answer_before_that(memory))
    if step and _echoes_the_person(step, memory):
        step = None
    if tips:
        # A plea for tips one turn after the answer is the case where the answer still has
        # something in it: the step is the sentence they have just read, and the sentence after it
        # is news ("Roasting carrots or broccoli in a little oil makes them sweeter, and a dip to
        # dunk turns it into a game"). Only when there is no such sentence is there nothing to add.
        other = _the_other_thing_in_the_answer(said, step, memory)
        if other:
            return _say(ALSO_LINES, memory, flat, other=other)
        if not step:
            # The card above is all of it - one sentence and a question back, or a list with no
            # next thing in it - so there is nothing to add and nothing to quote. Saying that is
            # the honest reply, and the search hedge ("that's most of what I know on it") is a
            # shrug in place of it.
            return pick(STEP_KEPT_LINES, memory, flat)
    if step and (_already_asked_for_a_step(memory)
                 or _most_of_the_line(step, _the_line_just_given(memory))
                 or tips):
        # A plea for tips that the answer above cannot add to is the answer again by another word:
        # the knowledge base had its turn at it above and had nothing more to say (a card that does
        # outranks this line), so quoting its first sentence back is the whole card's opening said
        # a turn later - "Keep serving one small piece of veg next to something they already like"
        # under "any tips". The step has not changed, and saying that is the honest reply.
        # The step has already been given: the person asked for one twice running, or the answer
        # above was a single sentence and that sentence was the step itself, so quoting it hands
        # them back what they have just read. Saying it again is the one thing STYLE.md forbids,
        # and there is no second step to give because the answer had nothing else in it - so the
        # line says the step stands and adds nothing to it.
        return pick(STEP_KEPT_LINES, memory, flat)
    if not step:
        # An offer of help that the person has just taken up is not a question waiting to be
        # handed back: "What would help most right now?" then "what do i do" is the person
        # saying "this", and the pool below would answer it with a shrug. There is no step in
        # the bot's own question to quote, so this composer stands aside and lets the fallback
        # make its honest pass.
        if _an_offer_is_waiting(said):
            return None
        if bare and _ends_on_a_question(said):
            # Only a bare ask ("what now", "what should i do") is handed back. A decision ask
            # ("should i say something") names what it is about, and "nothing to do on my side"
            # denies it: after "my sister keeps borrowing my stuff" / "what have you tried
            # saying so far?", "should i say something" was answered "Nothing to do on my
            # side, honestly - whatever comes to mind about it first is the useful bit" where
            # the composer's own decide line (fallback.UNKNOWN_DECIDE, "That's your call, not
            # mine... tell me what you're weighing") had answered it. Left alone here, that line
            # answers the turn, and the question back is only for the ask that names nothing.
            # The news in the line before is the one exception, and it is checked first: "What
            # would help most right now" over "bailiffs turned up" is a question about the news,
            # and the ask that follows ("what do i do") wants an answer about the bailiffs - which
            # the entry beside this one already has. Handing the question back there took that
            # answer away and told the person there was nothing to do on my side.
            if _the_news_just_before(memory):
                return None
            asked = _the_question_asked(said)
            if asked and THE_PLEA.match(flat):
                return pick(QUESTION_BACK_LINES, memory, flat)
            if asked and _after_a_comfort_line(memory):
                return pick(QUESTION_BACK_LINES, memory, flat)
            if asked and AN_OFFER.search(asked):
                return pick(OFFER_TAKEN_LINES, memory, flat)
            if asked:
                return _say(ASKED_FIRST_LINES, memory, flat, q=asked)
            return pick(QUESTION_BACK_LINES, memory, flat)
        # "It needs nothing doing. If the noise comes with pain or swelling, treat it as pain":
        # an answer whose own advice is to do nothing still answers "what should i do", as long
        # as it says what would change the picture. With no instruction and no condition there
        # is nothing to say from it, and the fallback's own line is the honest one.
        # A plea for tips wants a move, so it is never answered with the condition alone ("Nothing
        # you need to do yet - it matters if it has gone on a month"): the answer's own list is a
        # move when it wrote one, and with neither the fallback's own line is the honest reply.
        # A bare "what should i do about it" wants a move just as much, and an answer that wrote
        # its moves after a colon is the same list: "i cant sleep" / "what should i do about it"
        # was told "Nothing you need to do yet - it matters if you're worn out all day too" over
        # "The things that work: same wake-up time every day, no caffeine after early afternoon".
        listed = _listed(said)
        if listed:
            return _say(LIST_STEP_LINES, memory, flat, step=listed)
        # "Nothing to do" is a claim about the answer, so it is only made when the answer really
        # wrote one thing or none. The back-pain answer carries four moves, but they sit inside a
        # colon and behind an "if" ("the thing that settles it is the right amount of use: keep
        # going as far as is comfortable and add two short sessions a week"), so no step was found
        # and the bare ask was answered "Nothing to do for now" - the opposite of the paragraph
        # above it. More than one action in the answer and the fallback's own line is the honest
        # reply, as it is with no condition at all.
        if when and not plea and _action_count(said) < 2:
            return pick(NOTHING_LINES, memory, flat).replace("{when}", when)
        if ONE_THING.match(flat) and _last_module(memory) == "answers":
            # The answer above may still have written a move this reader cannot cut a clause out
            # of ("A dentist or a hygienist scale and polish first", "The thing to do first: write
            # down what is actually due this week"). Where it did, that sentence is the one thing
            # and it is handed over as it stands; the line that says there is no move in it is for
            # the answer that really has none.
            move = _an_instruction_sentence(said)
            if move:
                head = move.partition(": ")[0].strip(" .;:,-")
                if ": " in move and len(head.split()) >= 8:
                    # The answer put a menu or a second choice after its colon ("... scale and
                    # polish first, because most yellowing is staining: either a professional kit
                    # or a high-street one"). The one thing asked for is the part before it.
                    move = head
                elif len(move.split()) > HAND_OVER_WORDS:
                    move = _first_clause(move).strip(" .;:,-") or move
                return _say(ONE_TURN_PLAIN_LINES, memory, flat, step=move)
            # Nothing here can name a move, and saying the ask back ("Got it - just one thing to
            # start") is the acknowledgement answering a question, so the line says the answer
            # was the whole of it and offers the part they want taken further.
            return _say(ALL_OF_IT_LINES, memory, flat)
        return None
    # A step that ends in "first" ("Do it in a short meeting first") doubles the word in a line
    # that adds its own: "Do it in a short meeting first first, then work down the list".
    if step.lower().endswith(" first"):
        step = step[: -len(" first")].rstrip()
    # A person who asked for the one thing gets the one thing, however the step is shaped.
    if ONE_THING.match(flat):
        # The person asked for one thing out of a long answer, so the answer's own sentence is
        # handed over entire. The step is only its first clause, and quoting that alone was
        # handing back "Give them sun." to somebody who asked where to start with tomatoes.
        whole = _step_sentence(said, step)
        piece = _up_to_a_break(whole, step, HAND_OVER_WORDS) if whole else ""
        if len(piece.split()) > len(step.split()):
            return _say(ONE_TURN_PLAIN_LINES, memory, flat, step=piece)
        pool = ONE_TURN_PLAIN_LINES if (": " in step or FIRST_ITSELF.search(step)) else ONE_TURN_LINES
        return _say(pool, memory, flat, step=step)
    if how_to_asked:
        # "how do i clean it", "how do i top it up": the line named the job, so the instruction is
        # the whole sentence the step sits in and not its first clause. One instruction can be
        # two moves in one sentence, and the clause stops in front of the second: the washer
        # answer's step read "Run a hot 60C or 90C service wash with a washing-machine cleaner or
        # a cup of bicarbonate of soda" and left out "and clean the filter and the detergent
        # drawer while it runs", which is half the job; the boiler's read "Top the pressure up to
        # between 1 and 1.5 bar using the filling loop" and left out "then bleed the radiators and
        # check it again the next day". A person who asked how to do the thing is owed the move
        # the answer wrote, not the part of it before the comma.
        whole = _step_sentence(said, step)
        if whole and len(whole.split()) > len(step.split()):
            step = whole
        # One answer opens on what the thing is and puts the move after a colon: "A dripping tap
        # is nearly always a worn washer or cartridge: turn the water off at the isolating valve".
        # Handing that back whole says turn one again - the person read the diagnosis in the
        # answer above and asked how to do the job, so the step starts where the move starts. A
        # front clause that is itself an instruction is kept ("Start with a plunger: then undo")
        # because the second half only makes sense with it.
        head, colon, tail = step.partition(": ")
        if (colon and tail and _doing_word(re.findall(r"[A-Za-z'’-]+", head)) not in IMPERATIVES
                and _the_front_names_what_is_in_hand(head, flat, memory)):
            # The front has to be about the thing in this chat as well as not an instruction. One
            # answer slides a list of devices into one sentence ("A loo seat bangs because the
            # rubber bumpers under it have gone hard: tighten the two bolts ..."), and a line
            # about pipes or a blind meets it on the word "bangs". Cutting the front there leaves
            # an instruction about hinges with nothing saying what it is for, and the person
            # never sees that the card picked the wrong thing. Where the front's own subject is
            # in the chat - the dripping tap, the washing machine, the boilers - the front is the
            # part they have already read and the step starts at the move.
            step = tail.strip()
    # A step that already orders itself ("Start with a plunger over the plughole", "block that
    # first") cannot take a second "first", so it gets the lines written for one.
    if FIRST_ITSELF.search(step):
        return _say(STEP_ALREADY_FIRST_LINES, memory, flat, step=step)
    if ": " in step or len(step.split()) >= STEP_LONG:
        # The answer explained the step itself, or the step is too long to take a word on the end
        # ("Track two weeks of what actually leaves the account before you change anything first"
        # lands the order on "anything"), so the line introduces it in a sentence of its own.
        return _say(STEP_DETAIL_LINES, memory, flat, step=step)
    if _action_count(said) > 1:
        pool = STEP_ALREADY_FIRST_LINES if FIRST_ITSELF.search(step) else STEP_LINES
        if how_to_asked:
            # "how do i clean it", "how do i unblock it": the ask names a doing and the thing it is
            # done to, so the reply is the answer's own first step and nothing more. The lines that
            # point at the rest of the answer ("Clip the top growth, before anything else I
            # mentioned") are for an ask about where to begin, not for one that named the job, and
            # a sentence that ends on "I mentioned" reads like a note to self.
            pool = STEP_DETAIL_LINES
        return _say(pool, memory, flat, step=step)
    return _say(STEP_ONE_LINES, memory, flat, step=step)
