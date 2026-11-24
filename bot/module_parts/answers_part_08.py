"""Part 8 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import copy
import re

from .. import memory as mem
from ..compose import goodnews
from ..knowledge import cooking, dishes, meat_in_a_card
from ..knowledge.lookup import find
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import named, narrow as length
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import keywords, recall
from ..memory import again as same_again  # the short of an answer already on the screen
from ..memory.again import AGAIN_HELP
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import keywords
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory.narrow import flat, words_of
from ..understanding import understand
from .answers_part_01 import (
    SENTENCE, _flat, _said_before_now, WORD, AGAIN,
)
from .answers_part_02 import (
    _key_words,
)
from .answers_part_03 import (
    _remember_answer, _last_answer, _same_word,
)
from .answers_part_05 import (
    A_FIGURE,
)
from .answers_part_06 import (
    _repeat_short,
)
from .answers_part_07 import (
    _a_writing_job, _asks_only_the_length,
)


def _a_limit_on_the_plan(text, memory):
    """True when the line is only a limit on the plan, which the composer answers itself.

    Read through `bot/memory/ack.py`, which owns the frames and the "is it only a limit" test, so
    the two answers for a limit cannot drift apart. A line that gives the store something of its
    own (a person, a detail, a plan) is a fact of its own and keeps the knowledge base's answer.
    """
    try:
        from ..memory import ack as _ack
    except Exception:
        return False
    try:
        return bool(_ack.a_limit_on_the_plan(text) and _ack.a_limit_reply(text, memory))
    except Exception:
        return False


# "what day did i say it was due", "what did i say the excess was": the person asks for a detail
# from one of their own earlier lines, and the word the ask turns on is not what the line is
# about - a school project "due friday" read as a late period, which is the card that answered
# "what day did i say it was due". The memory store quotes their line, so an entry that takes the
# ask on one of its words answers a question nobody asked.
THEIR_OWN_ASK = re.compile(
    r"\b(?:did|have|had)\s+i\s+(?:just\s+)?(?:say|said|tell|told|mention|mentioned)\b", re.I)


def _a_bare_thanks(understood):
    """True when the line is a thank you and nothing else.

    Read here rather than only where the lookup stands down, because the readers that draw on the
    answer just given run in front of the lookup and answer a thank you as a follow-up to it: after
    a recipe, "thats really kind thanks" was handed a second recipe. A thank you with a question
    after it is still a question, and a writing job only opens with a thank you, so both are left
    to the readers below. The kind is the reading that decides: a thanks line can still carry an
    ask word it does not ask with ("thanks, that explains the boiler" carries "explains"), and a
    thank you that really asks something is read as a question.
    """
    return (isinstance(understood, dict) and understood.get("kind") == "thanks"
            and not _a_writing_job(understood))


def _a_judgement_of_the_figure_on_the_table(text, memory):
    """True when the line is only a doubt about a figure, and the reading can answer it.

    The reading is imported here rather than at the top because it is the composer's and this
    module must keep working if it raises: a doubt this cannot read is left to the card.
    """
    try:
        from ..compose import reading as _reading
        return _reading.judges_the_figure_on_the_table(text, memory)
    except Exception:  # noqa: BLE001 - an unreadable doubt is not a reason to lose the answer
        return False


# The modules whose reply is an answer about the subject, rather than a nod at the person's line.
_AN_ANSWER = frozenset(("answers", "memory_store"))


def _the_bot_has_something_to_go_over(memory):
    """True when one of the bot's last lines explains something the ask could be pointing at.

    A line that asks what the bot meant points at the answer just given, so there has to be one.
    Very often there is not: "i got a payslip" is answered "Good to hear. What was the best bit?",
    which is the bot asking rather than answering, and standing the knowledge base down for that
    turn took away the card that answered well - "what does that mean for my pay" got "I haven't
    put anything about it into words yet" instead of the gross/net card. So the reading is asked
    only after the bot has said something to explain: the same test the store uses to decide a
    line is thick enough to hand back (`bot/memory/meant.py`), read here so the two cannot
    disagree about whether there was an answer.
    """
    from ..memory import meant as _meant
    from ..memory import repeat as _repeat
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for turn in reversed((turns or [])[-_meant.LOOK_BACK_FAR:]):
        if not isinstance(turn, dict):
            break
        said = str(turn.get("bot") or "").strip()
        if not said:
            continue
        if str(turn.get("module") or "") in _meant.NOT_TO_REPEAT:
            # An emergency or a condolence is not an explanation to point back at.
            break
        asked = str(turn.get("user") or "").strip()
        if (_repeat.HEDGE.search(said) or _meant.CONDOLENCE.match(said)
                or _meant.RECEIPT.search(said)):
            continue
        if str(turn.get("module") or "") in _AN_ANSWER or _meant._thick_enough(said, asked):
            return True
    return False


def _the_line_asks_what_this_one_meant(memory):
    """True when this turn asks what the bot's own last answer meant.

    "what do you mean", "whats that supposed to mean", "wot u mean", "wdym": the line names
    nothing of its own, so the answer is the last answer said again, which the store gives. The
    reading settles it in every spelling (`understood["asks_what_was_meant"]`, see
    `bot/understanding/kinds.py::_asks_what_was_meant`) so no list of spellings is kept here.
    """
    if not isinstance(memory, dict):
        return False
    understood = memory.get("understood")
    if not (isinstance(understood, dict) and understood.get("asks_what_was_meant")):
        return False
    return _the_bot_has_something_to_go_over(memory)


# What the answer to a question of its own is read against: the person's own facts, and nothing
# about the turn before this one. "any ideas for a cheap day out with kids near leeds" carries
# everything the entry needs, and the reading of the previous line points at the previous entry -
# with that still in the store the combined question was answered by the day-out row again.
_TURN_ONLY = ("understood", "entry_answer", "entry_answers", "frequency_answer",
              "frequency_reply", "last_answer", "topics", "topic", "return_to", "correction",
              "denial", "replies")


def _of_its_own(memory):
    """The store with the last turn's reading taken out, so a question is answered on its words."""
    own = copy.deepcopy(memory) if isinstance(memory, dict) else {}
    for key in _TURN_ONLY:
        own.pop(key, None)
    return own


def _keep_the_answer(text, reply, memory):
    """Keep the answer this module gives, so the next line can be about it.

    Every reader inside this module that answers from an entry records the turn itself, because
    it knows the words the entry was keyed on. The readers that answer from something else - the
    pantry table naming a dish from two foods in the line, a pick between the things the bot
    offered - gave no record at all, so "how long does that take" a turn later had nothing to
    read: "what can i do with mince and a tin of tomatoes" then "ok thanks" then "how long does
    that take" got the search hedge, while the same ask straight after the answer got "Simmer
    for at least 30 minutes". An answer is an answer whichever reader gave it, so the line's own
    words are kept with it, and a record an entry already made this turn is left as it is: it
    knows more about what the answer is about than the line does.
    """
    if not isinstance(memory, dict) or not isinstance(reply, str) or not reply.strip():
        return
    turns = memory.get("turns")
    here = len(turns) if isinstance(turns, list) else 0
    kept = memory.get("last_answer")
    if isinstance(kept, dict) and kept.get("turn") == here and kept.get("reply"):
        return
    _remember_answer(memory, None, reply, keys=keywords(text))


def _the_sentence_it_names(reply, text, memory):
    """`reply` cut to the sentence naming this line's own word, when the paragraph was said before.

    Only a paragraph the bot has already given word for word in this chat is cut: everywhere else
    the entry's own wording is the answer, and the readers above have already narrowed it where
    the line asked for a part. The word has to be one the person has not used before this turn
    ("primer" in "do i need a primer", not "paint" again), so a line that only says the subject
    once more keeps the whole paragraph.
    """
    mine = _flat(reply)
    if not mine or not isinstance(memory, dict):
        return reply
    said_before = any(isinstance(turn, dict) and _flat(turn.get("bot")) == mine
                      for turn in memory.get("turns") or [])
    if not said_before:
        return reply
    named = set(keywords(text)) - _said_before_now(text, memory)
    named &= set(words_of(reply))
    if not named:
        return reply
    parts = [sentence.strip() for sentence in SENTENCE.split(str(reply).strip())
             if sentence.strip() and named & set(words_of(sentence))]
    if not parts:
        return reply
    cut = " ".join(parts[:2])
    if len(cut.split()) < 4 or len(cut) >= len(str(reply).strip()):
        return reply
    return cut


def _fitted_to_what_they_eat(reply, text, memory):
    """The answer with the food they do not eat taken out of it, or "" when it cannot be.

    Every row in the knowledge base is written for everyone, and a row that fits the words can
    still name the food the person has just ruled out: "im vegetarian" then "what can i do with a
    swede" was "mashed with butter, alongside sausages", and "im vegan" then "what can i do with
    spinach" was "a hot pan, a knob of butter". The choosing inside the kitchen reads the diet,
    and the rows themselves do not, so the reply is read here against what the store knows the
    person eats. A word with an everyday swap is swapped ("softened in butter" is "softened in
    oil"), a row with a meat-free version of itself is served as that version, and a reply that
    still names the food they said no to is handed back as no answer at all: the row below it, or
    another module, may have one they can eat, and a shrug is a bad answer but the food they
    refused is a worse one.
    """
    if not isinstance(reply, str) or not reply.strip():
        return reply
    avoided = cooking.avoids(memory)
    # The meat a card uses as an ingredient, where the vegetarian version is one word: the gravy
    # card opens on "whisk the flour into the meat juices", and a vegetarian ten turns into a
    # chat about a roast was handed nothing rather than the gravy. See meat_in_a_card.
    reply = meat_in_a_card.swapped_out(reply, text, avoided)
    fitted = cooking.fits_the_diet(reply, avoided, text)
    if fitted is None:
        return ""
    # The person the chat is about, when that is somebody else in the store (memory["person"]
    # and memory["others"]): a long chat about packing a daughter's lunch is about her, and her
    # allergy is not the person's own (avoids() keeps those apart on purpose) but it does bind
    # the answer about her. Only ever a veto - see cooking.fitted_for_the_one_talked_about.
    fitted = cooking.fitted_for_the_one_talked_about(
        fitted, cooking.avoids_for_the_one_talked_about(memory), text)
    if fitted is None:
        return ""
    return fitted


# A dish names itself at the start of its own text ("A frittata: whisk 6 eggs", "A potato hash:
# fry diced potatoes"), and a qualifier in front of the name is not part of it.
_DISH_NAME_IN_TEXT = re.compile(r"^\s*(?:(?:one|two)[- ]pan\s+|a\s+|an\s+|the\s+)?"
                                r"([^:.,]{3,40}?)\s*:", re.I)


def _the_dish_by_name(answer, memory):
    """A reply that points at the dish ("that one") says the dish's name instead.

    "and i dont have any cheese" after a frittata was answered "Leave the cheese out of that one
    and it still works.", where "that one" names nothing a person can see: the dish was the
    subject of the answer before, and it is the one thing the sentence they now have to act on
    has to say. The plan on the table knows which dish it was, so the name goes in where the
    pointing word was.
    """
    if not isinstance(answer, str) or " that one" not in answer.lower():
        return answer
    plan = cooking.plan_recent(memory) or {}
    offered = [name for name in (plan.get("offered") or ()) if name]
    if not offered:
        return answer
    dishes = {dish["id"]: dish for dish in cooking.DISHES}
    said = _DISH_NAME_IN_TEXT.match(str((dishes.get(offered[-1]) or {}).get("text") or ""))
    name = ""
    if said and len(said.group(1).split()) <= 5:
        name = said.group(1).lower()
    if not name:
        # The plan's id for a dish is built from the foods in it, not from a name anybody has
        # read: "i have chicken and spinach" is answered "Chicken and spinach in one pan: ..."
        # while the id is chicken-spinach-cream, and naming that id gave "Leave the cheese out of
        # the chicken spinach cream and it still works." - a dish on no screen, with no cheese or
        # cream in it. A name comes off the screen, or the sentence keeps "that one".
        shown = _last_answer(memory)
        shown = shown.get("reply") if isinstance(shown, dict) else shown
        screen = _DISH_NAME_IN_TEXT.match(str(shown or ""))
        if screen and len(screen.group(1).split()) <= 5:
            name = screen.group(1).lower()
    if not name:
        return answer                    # "that one" beats a name that is nowhere on the screen
    return re.sub(r"\bthat one\b", "the " + name, answer, count=1, flags=re.I)


def _the_same_answer_again(answer, memory):
    """True when this answer says what the answer just given said, lead-in aside.

    The lead-ins are stripped first ("Same answer, and it covers this: ..."), and the two are
    compared by their openings, because the second telling is the first telling shortened rather
    than repeated word for word.
    """
    was = _flat(mem.last_bot(memory) or "")
    now = _flat(_without_lead_in(answer))
    if not was or not now:
        return False
    return now.startswith(was[:60]) or was.startswith(now[:60])


def _a_city_card_asks_which_first(text, memory):
    """True when the line asks which of a city card's places comes first.

    The city rows know their own list of places, so the card they wrote answers it; imported here
    rather than at the top because this is the only place in this module that reads them.
    """
    from ..knowledge import travel as travel_cards
    return (travel_cards.asks_which_one_first(text)
            and travel_cards.a_city_card_is_in_front(_the_answer_in_front(memory)))


def _the_answer_in_front(memory):
    """The reply just given by the knowledge base, for a line asking which part of it to do.

    Only a knowledge answer of the turn just before: a greeting, a hedge or a line of another
    module has no steps in it, and reaching further back would hand over the wrong answer.
    """
    if not isinstance(memory, dict):
        return ""
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return ""
    said = turns[-1] if isinstance(turns[-1], dict) else {}
    if said.get("module") != "answers":
        return ""
    return str(said.get("bot") or "")


# A line that opens by withdrawing something is a take-back, not a question: "forget the dog",
# "scratch that", "never mind the dog", "ignore that". The memory store answers it, so no entry
# of the knowledge base should read the take-back word as the subject of the line.
TAKEN_BACK_OPENER = re.compile(
    r"^\s*(?:(?:please|ok|okay|right)\s+)?(?:forget|forgot|ignore|scratch|disregard|drop|"
    r"never\s+mind|no)\s+(?:that|this|it|the|my|our|your|a|an|about|all)\b", re.I)


# --- how long before the day ----------------------------------------------------------------
# "how long before the day should we order the cake" was answered with how long a cake keeps.
# The ask has a length in it and a thing in it, so the length card for that thing wins the
# lookup, and nothing reads the event the length hangs off: a fixed date with a job to do
# before it. That is what people ask when the date is set - a cake, the invitations, the
# airport parking, a passport - and every one of them has an answer, so the shape is read
# before the lookup rather than left to the thing's own entry.
LEAD_ASK = re.compile(
    r"\bhow\s+(?:long|far|soon)\s+(?:before|ahead\s+of)\s+(?P<event>[^.?!]{1,60}?)\s*"
    r"\b(?:should|shall|ought\s+to|do)\s+(?:i|we|you|one)\s+(?P<act>[^.?!]{0,60})"
    r"|\bhow\s+(?:long|far|soon|early)\s+in\s+advance\s+(?P<act2>[^.?!]{0,60})"
    r"|\bhow\s+early\s+(?:should|shall|do)\s+(?:i|we|you)\s+(?P<act3>[^.?!]{0,60})")


# The job the date hangs off has to be a booking or an ordering one. "how long before the flight
# do i need to be at the airport" and "how early should i get to the airport" are the length of a
# wait on the day, not a lead time, and the general answer below would be wrong for both.
# The words that say what is being booked. A row matches on any one of its words, and the earlier
# row wins, so "wedding cake" is the cake row before anything general.
LEAD_ROWS = (
    (("cake",), "Order a decorated one four to six weeks ahead: the bakery wants the number of "
                "people and the design about a month out, and the week itself it can turn round. "
                "A fruit cake is the exception: it is baked well before and fed brandy as it "
                "sits, and it only gets better."),
    (("turkey", "goose", "bird"), "Order it by the middle of December, and collect it on the 22nd "
                                  "or 23rd so it has two days in the fridge. Free-range and big "
                                  "birds go first, so the middle of the month is the real deadline."),
    (("invitation", "invite", "save"), "Six to eight weeks before the day, with the reply-by four "
                "weeks out - eight to twelve if people have to travel or fly. The venue and any "
                "rooms are the things that go a year ahead, not the cards."),
    (("passport",), "Ten weeks is the honest allowance for a standard renewal, and quicker costs "
                    "extra. Check the country you are going to as well: many want six months left "
                    "on it at the date you arrive, not the date you leave."),
    (("parking",), "Two to four weeks ahead is plenty and the price is the reason: the on-the-day "
                   "rate at an airport is several times the booked one, and the cheap car parks go "
                   "first. The date and the flight time are all they need."),
    (("hotel", "accommodation", "cottage", "campsite", "room"), "As soon as the dates are fixed. A "
                "hotel needs nothing from you but a card, and the cheap rooms are the ones that "
                "sell out first - a refundable rate booked early beats a dearer one late."),
    (("table", "restaurant"), "Two to four weeks ahead for a Friday or Saturday, and a week or two "
                              "for a weeknight. Somewhere small or famous you book when you think "
                              "of it, and a set menu also wants the numbers a few days before."),
    (("flight", "ferry", "train", "ticket", "travel"), "Six to twelve weeks ahead is the cheapest "
                "window: a flight is dearest in the last fortnight and a train is best booked the "
                "day the tickets release, about twelve weeks out. After that the price only climbs."),
    (("venue", "hall", "church", "marquee"), "A year or more for a Saturday in summer, and two "
                "years for the popular ones. The venue sets the date, so it is the first thing "
                "booked and everything else fits round it."),
    (("flower", "delivery", "bouquet", "gift", "present"), "Three to five days ahead for a delivery "
                "on a set day, and a fortnight for anything made to order or for Valentine's and "
                "Mother's Day. Same-day is a different, dearer price."),
)


LEAD_VERB = re.compile(r"\b(?:order|orders|ordering|book|books|booking|reserve|reserving|hire|"
                       r"hiring|send|sends|sending|renew|renews|renewing|apply|applying|"
                       r"arrange|arranging|sort|sorting|pay|paying|buy|buying|collect|"
                       r"collecting|pick|picking)\b")


LEAD_ANY = "Sooner than you would think: the price only goes up and the good slots go first, so " \
           "book it as soon as the date is fixed. Tell me which booking and I will be exact."


def _a_lead_time(text):
    """The answer to "how long before the day should we order it", or None.

    Read before the lookup: the thing named in the line has a length entry of its own (a cake
    keeps four days, parking is a price), and that entry answers a question about the thing
    rather than about the job to do before the date.
    """
    if not isinstance(text, str):
        return None
    found = LEAD_ASK.search(text.lower())
    if not found:
        return None
    act = " ".join(part for part in found.groups() if part)
    if not LEAD_VERB.search(act):
        return None
    words = {word.rstrip("s") for word in WORD.findall(text.lower())}
    for needles, answer in LEAD_ROWS:
        if any(needle.rstrip("s") in words for needle in needles):
            return answer
    return LEAD_ANY


# A thing that has got better is news, and the knowledge base is the advice for the thing still
# being there. "i have a rash on my arm" then "the rash has cleared up" reached the rash entry
# again and came back as *"Same answer, and it covers this: Most rashes are contact or heat..."* -
# the paragraph for a rash that has gone. The readers are the composer's own, because the news
# pools that answer it live there (`bot/compose/goodnews.RELIEF`), and a line is only news when
# nothing in it asks: a question mark keeps the whole module.
def _the_thing_has_got_better(text, memory):
    """Whether the line reports that the trouble has passed, so the advice would be stale.

    "the pain has gone", "my knee has healed", "im over the flu now" and "its stopped now" are
    reports on the answer above, not a second ask for it. `reads_as_recovery` reads the ones said
    about the speaker, and `reads_as_settled` the ones said about a thing or a body - that one
    needs a worry on the table, so "its stopped now" about a noise the car was making keeps its
    own answer and does not become a medical relief.
    """
    clean = " ".join(str(text or "").lower().split())
    if not clean or "?" in clean:
        return False
    got_better = goodnews.reads_as_recovery(clean) or (
        goodnews.reads_as_settled(clean) and goodnews.worry_on_the_table(memory or {}))
    # The phrase has to be the end of it: "my cough has gone green" is a cough that has changed
    # colour, and standing the chesty-cough card down for it would answer a symptom with relief.
    return bool(got_better) and goodnews.the_news_is_the_whole_of_it(clean)


# A follow-up that points at one of the cases inside the answer in hand instead of asking its own
# question: "and for a hard one", "what about the soft ones", "how about the big one". It names no
# thing the knowledge base can look up, and the case it points at is written in an answer already on
# the screen, so the words that answer it are there to be read rather than looked up again.
A_CASE_ASK = re.compile(
    r"^(?:and|or|what|how|which|then)\b[^?.]{0,40}\b(?:one|ones|other|another|"
    r"hard|soft|big|small|large|little|medium|old|young|dark|light|cheap|quick|slow)\b", re.I)


# The words that say where the ask points rather than what it points at: a part found by one of
# these is a part of the sentence, not the case the person named.
A_CASE_STOP = frozenset("""about and another any are can could for from have how i if is it
    its just like long many much my of one ones or other the then to what when which who why
    will with would you your""".split())


def _a_case_of_the_answer_in_hand(text, memory):
    """The words of an answer on the screen that cover the case this line names, or "".

    "how long do i boil an egg" gives 6 minutes for a runny yolk, 7 for jammy and 9 to 10 for hard
    boiled, and "i want it soft" gives the soft one alone - so "and for a hard one" names a case
    that is no longer in the last answer, and the bot answered it with a nod. A friend reads back
    to the answer that covered it. `bot/memory/narrow.py` cuts the clause a line asks for out of a
    paragraph, and it cuts "9 to 10 for hard boiled" out of that answer, so the case is read from
    the answers still on the screen, newest first, and only from an answer of the knowledge base.

    The part has to name what the line names - the word of the case itself - so that a figure out
    of another answer cannot be handed over for a case nobody covered. Nothing is read when the
    line is longer than a pointer ("and what about the soft boiled ones in the morning"), which is
    a line with a question of its own.
    """
    line = " ".join(str(text or "").split())
    if not line or len(line.split()) > 8:
        return ""
    if not A_CASE_ASK.match(line.lower()):
        return ""
    wanted = {word for word in WORD.findall(line.lower())
              if len(word) > 2 and word not in A_CASE_STOP}
    if not wanted:
        return ""
    answers = [str(turn.get("bot")) for turn in reversed(memory.get("turns") or ())
               if isinstance(turn, dict) and turn.get("bot") and turn.get("module") == "answers"]
    # The wider read below is for the turn after a case and no other. When the answer in hand is a
    # fragment ("9 to 10 for hard boiled."), the paragraph it came from has gone off the screen and
    # the card that answers the next case is two turns up. Straight after a whole answer the case
    # is cut out of the newest answer's own clause, and reading further back is how the list of
    # three dinners came back for "and quick" when the chat had moved on to vegetarian dishes.
    after_a_case = bool(answers) and len(answers[0].split()) <= 12
    for answer in answers[:3]:
        try:
            part = length.narrow(answer, text)
        except Exception:  # noqa: BLE001 - a part that cannot be cut is no part at all
            part = ""
        if not isinstance(part, str) or not part.strip():
            part = ""
        # Nothing was cut out of this answer: either narrow found no clause for the line, or the
        # answer is already just that clause. The second is the answer in hand after a case was
        # read - "and for a hard one" leaves the one line "9 to 10 for hard boiled." - and the card
        # before it, "A soft one is the 5 to 6 minute egg...", is the answer to "and the soft one".
        # The whole-answer rule below is there so a paragraph is never handed back; a card that is
        # one sentence with a figure in it is the case itself, and the person asked for it again.
        uncut = not part or (" ".join(part.lower().split())
                             == " ".join(answer.strip().lower().split()))
        if uncut:
            part = answer.strip() if len(answer.split()) <= 30 else ""
        if not part:
            continue
        if not re.search(r"\d", part):
            continue
        # The part is the clause around the figure ("9 to 10 for hard boiled"), never a whole
        # paragraph: "and quick" after a list of three dinners cut the whole list out of the first
        # answer, and read back a dinner they had already turned down (they are vegetarian, so the
        # whole answer was dropped as uneatable and the turn went to the small talk).
        if len(part.split()) > (30 if after_a_case else 14):
            continue
        if after_a_case and len([s for s in re.split(r"(?<=[.!?])\s+", part.strip())
                                 if s.strip()]) > 1:
            # The card two turns up can be two sentences, and the first of them is the case ("A
            # soft one is the 5 to 6 minute egg: 5 for a yolk that still runs, 6 for a set white
            # with a soft middle."). Four sentences cut out is the paragraph coming back.
            continue
        said = {word.rstrip("s") for word in WORD.findall(part.lower())}
        if not any(word.rstrip("s") in said for word in wanted):
            continue
        part = part.strip()
        if part[-1:] not in ".!?":
            # A clause cut out of the middle of a sentence comes back without its stop ("2 to 3
            # minutes a side for medium rare"), and every other reply this bot gives ends on one.
            part += "."
        return part[:1].upper() + part[1:]
    return ""


# A reply cut out of the answer on the screen is not a reply when it is only a clause of it: the
# figure a price ask pulls out of a paragraph ("£100 to £200" out of "pads are 100 to 200 and a
# front set with discs is 200 to 350"). Any longer and the part stands on its own.
_A_CLAUSE_OF_THE_ANSWER = 14


# The words a short answer can be and still be the whole of what was asked: "2 to 4 minutes.",
# "about 20 minutes", "an hour and a half".
_A_SHORT_ANSWER = 12


def _the_line_already_has_its_answer(alone, text):
    """Whether a bare length ask already got a short answer with a figure in it.

    Only a line that asks for nothing but the length, because that is the case this keeps safe: a
    microwave asked how long takes the microwave's own time out of the answer above it, and that
    figure is the answer. A measure ask about the subject - "how much would that cost" - is a
    different case: the short figure the line gets on its own is a clause cut out of an older
    answer ("£1,500 to £2,000." out of what a dog costs a year), and the written-in line reaches
    the entry that answers the cost properly. A clause on its own is not a reply, so the rewrite
    takes that turn.
    """
    if not _asks_only_the_length(text):
        return False
    said = _flat(alone or "")
    if not said or not A_FIGURE.search(said):
        return False
    return len(said.split()) <= _A_SHORT_ANSWER


# A line asking for a length of time, in any of the ways people ask it.
_A_HOW_LONG = re.compile(r"\bhow\s+long\b", re.I)


# The words an entry about getting a thing mended is keyed on: "repair-time" and the cost rows for
# a boiler, a washing machine, a phone screen. A row about the thing itself ("How long does a
# washing machine last") names none of these, which is how the two are told apart.
_A_REPAIR = re.compile(
    r"\b(?:repair|repairs|repaired|fix|fixes|fixed|fixing|install|installs|installed|"
    r"installation|engineer|plumber|electrician|callout|call-out|call out|swap|swapping|job|"
    r"visit)\b", re.I)


def _names_a_repair(entry):
    """Whether the entry is about getting the thing mended rather than about the thing itself."""
    if entry is None:
        return False
    flat = " ".join(str(group) for group in (getattr(entry, "key", ()) or ()))
    return bool(_A_REPAIR.search(flat))


def _the_entry_names(entry, word):
    """Whether the entry is keyed on the thing itself ("dog"), not only on the asking ("cost")."""
    if entry is None or not word:
        return False
    flat = " ".join(str(group) for group in (getattr(entry, "key", ()) or ())).lower()
    return bool(re.search(r"\b" + re.escape(word) + r"\w*", flat))


def _the_plan_said(memory):
    """The plan the chat is on, in the person's own words ("my sister is getting married in june")."""
    known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    return " ".join(str(known.get("plan") or "").split())


# The words of the part in a "part of <subject>" question, as the person said them: "cost" out
# of "cost of boiler".
_PART_OF = re.compile(r"^\s*(?P<part>[a-z][a-z -]{1,24}?)\s+of\s+", re.I)


def _the_part_is_what_answers(part, memory):
    """The entry a part ask reaches has to be keyed on the part, not only on the subject.

    "and the cost" after "my car is making a noise" is a price, and the entry the subject reaches
    is the diagnosis: it says nothing about a price, so the part is not answered and the turn
    falls back to the follow-up paths that were there before. "and the capital" after a trip to
    Spain reaches the entry filed for "capital of spain", which is the part's own entry, and that
    one takes the turn. A part with no entry of its own is left alone exactly as it was.
    """
    named_part = _PART_OF.match(part or "")
    if not named_part:
        return True
    wanted = {word for word in _PART_OF_WORDS.findall(named_part.group("part"))}
    if not wanted:
        return True
    item = find(understand(part, memory))
    if item is None:
        return True  # nothing is filed for it: the paths below are the only chance it has
    said = _key_words(item)
    return bool(wanted & said)


_PART_OF_WORDS = re.compile(r"[a-z]{3,}")


# A part is attached to the turn before it by a word: "and the drawer", "what about the drum",
# "the belt too", "and its population". A bare noun phrase ("the drum") and a report ("the drawer
# every month") are lines about the part in their own right, and the lookup answers those.
_ATTACHED_TO_THE_LAST_TURN = re.compile(
    r"\b(?:and|also|plus|too|what about|how about|its|it's|their|his|her)\b", re.I)


def _the_report_is_answered(text, entry):
    """The entry the report reaches has to be about the state, not only about the thing.

    A report written with its thing in ("my phone is on 4%") reaches whatever the thing and one
    other word fit, and that is not necessarily an answer: "my phone is fine now" reached a line
    about skipping breakfast, and "my battery is on 4%" reached how a battery works. The state is
    what the person said something about, so the entry has to be keyed on it too - the shape a
    figure is read as ("4%" as a charge level), or the word the person used for it ("still",
    "warm", "smells"). Where nothing is keyed on the state, the line keeps whatever answer it had.
    """
    if entry is None:
        return False
    said = " ".join(str(text or "").lower().split())
    keys = []
    for part in getattr(entry, "key", ()) or ():
        for alternative in (part if isinstance(part, (tuple, list, frozenset, set)) else (part,)):
            if isinstance(alternative, str):
                keys.extend(alternative.lower().split())
    if not keys:
        return False
    figures = re.findall(r"\d+(?:\.\d+)?\s*(?:%|percent|hours?|minutes?|days?|weeks?|litres?|"
                         r"liters?|kilos?|kg|metres?|miles?|pounds?)", said)
    if figures:
        for shape in getattr(entry, "shape", ()) or ():
            try:
                if shape(said):
                    return True
            except Exception:  # noqa: BLE001 - a shape that cannot read the line is no signal
                continue
        units = {word for figure in figures for word in re.findall(r"[a-z%]+", figure)}
        if units & set(keys):
            return True
    said_words = {word.strip(".,;:!?()") for word in said.split()}
    states = said_words & named.STATE_WORDS
    return any(any(key[:4] == state[:4] for key in keys) for state in states)


# The words that say how much of a thing there is, and nothing about which thing it is. A stated
# fact built only of these is not a fact about the thing on the table: "the hours are too much" is
# about hours, and no row keyed on "too much" is answering it.
A_DEGREE = frozenset("""too very really quite rather so such more most less least much many
                        enough plenty lots lot bit little slightly far""".split())


def _the_fact_is_what_is_answered(text, stated, entry, memory=None):
    """The entry a stated fact reaches has to be keyed on the fact, and on the subject too.

    Written with the subject in front, the line can reach any row that shares a single word with
    it, and that is not an answer: "lawn i work shifts" reached the stop-smoking card, "phone i
    work shifts" the stain one and "bike we rent" the rent-or-buy-a-house one. The entry that
    holds both halves of what the person said is the one that needs them - the pension card for
    the self employed, the bike card for a child - so the fact has to be in the key and so does
    the subject. A word is compared by its first four letters, because a key holds one form of a
    word ("years") and the line another ("year").
    """
    if entry is None:
        return False
    # The rewrite must not slip past the row's own standing-down words: the child-weight card
    # says "i want to lose" is not about a child, and the fact on its own ("i have two kids")
    # no longer holds that phrase, so writing the subject in front of it read a parent's own
    # wish as a question about their children.
    # What the whole exchange said, not only this line: the card that stands down on "i want to
    # lose" is held down by the first turn, and the fact said on its own no longer holds it.
    low = " ".join(str(text or "").lower().split())
    try:
        said = [str(turn.get("user") or "").lower() for turn in (memory or {}).get("turns", ())[-3:]]
    except (AttributeError, TypeError):
        said = []
    low = " ".join(said + [low])
    for hold in getattr(entry, "avoid", ()) or ():
        if isinstance(hold, str) and hold and hold.lower() in low:
            return False
    keys = []
    for part in getattr(entry, "key", ()) or ():
        for alternative in (part if isinstance(part, (tuple, list, frozenset, set)) else (part,)):
            if isinstance(alternative, str):
                keys.append(" ".join(alternative.lower().split()))
    if not keys:
        return False

    def tells(word):
        # The whole word, in the key's own phrase: comparing by opening letters was how "patchy"
        # met the nicotine patch in the stop-smoking card, and "shifts" the word "shift".
        return any(re.search(r"\b" + re.escape(word) + r"(?:s|es)?\b", key) for key in keys)

    said = [word for word in re.findall(r"[a-z0-9']+", str(text or "").lower())
            if len(word) > 2 and word not in named.FACT_FILLER
            and word not in named.JOINING]
    # A degree says how much of a thing, not which thing: "my sister says i should quit my job"
    # then "yeah she thinks the hours are too much" wrote the sister in front of the line, the
    # gift-budget row took "sister" as its subject and "too much" as the fact, and a person
    # talking about their shifts was asked what a present should cost. The fact has to name
    # something the row is about, so a fact made only of degrees is no fact to put in front.
    told = [word for word in said if tells(word)]
    if not told or all(word in A_DEGREE for word in told):
        return False
    subject = str(stated or "").lower().split()
    subject = subject[0] if subject else ""
    return bool(said) and tells(subject)


def _the_entry_key_words(entry):
    """Every word an entry is keyed on, in one flat list."""
    keys = []
    for part in getattr(entry, "key", ()) or ():
        for alternative in (part if isinstance(part, (tuple, list, frozenset, set)) else (part,)):
            if isinstance(alternative, str):
                keys.extend(alternative.lower().split())
    return keys


def _the_practice_is_answered(practice, entry):
    """The entry the practice reaches has to be about the practice and about the thing.

    A line written with its thing in front ("tomatoes feed every week") reaches whatever the thing
    and one other word fit, and an entry that only says what the thing is is no answer to what the
    person does to it: "tomatoes feed every week" reaching the sowing answer would tell them when
    to sow a plant they already have. The practice is what they said something about, so the entry
    has to be keyed on the care verb too ("feed", "water").

    It has to be keyed on the thing as well, and that is the half that is easy to lose. The person
    said the practice about *their* plant or *their* dog, and an entry that shares only the verb is
    some other question about the same word: "chillies feed every two weeks" met the meal plan,
    because chillies are a dinner, and "dog walk twice a day" met the step count, because walking
    is how the steps are counted. Both are fluent answers about something else, so both are worse
    than the plain "Got it" they replace. The thing is the words in front of the verb in the
    rewrite, which is the shape `named.care_reports` writes.
    """
    if entry is None:
        return False
    words = re.split(r"[^a-z]+", " ".join(str(practice or "").lower().split()))
    verbs = [word for word in words if word in named.CARE_VERBS]
    if not verbs:
        return False
    at = words.index(verbs[0])
    thing = [word for word in words[:at] if len(word) > 2]
    keys = _the_entry_key_words(entry)
    if not keys or not thing:
        return False
    same = any(_same_word(key, word) for key in keys for word in thing)
    if not same:
        return False
    return any(_same_word(key, verb) for key in keys for verb in verbs)


_A_YES_NO_ASK = re.compile(
    r"^(?:is|are|was|were|would|will|do|does|did|can|could|should|shall|have|has)\b", re.I)


# The words a thing named in a moan is made of, as the stems the answer is searched with.
MOAN_STOP = frozenset("""a an the my our your his her their its me i we you it that this these
those and or of to for in on at with from by up down out about right wrong""".split())


MOAN_VERB_WORDS = frozenset("get do make cook pick find manage".split())


# A period the line asks about: a day, a week, a month. "how much sugar should i have a day"
# is a question about the day, so a figure cut out of the previous answer is not its answer.
_A_PERIOD = re.compile(
    r"\b(?:a|per|each|every|one)\s+(?:day|week|month)\b|\b(?:daily|weekly|monthly)\b", re.I)


# The bare ask for the words to refuse: "how do i say no", "how can i say no without feeling
# awful". The refusal entries are keyed on the situation (a boss, a client, a mum, a request),
# so the ask that names no situation reached the search hedge even though the same answer fits.
# This is the last reader in _answer, after every entry and every follow-up, so an answer that
# knows the situation keeps the turn. It is deliberately narrow: only the ask itself, or the ask
# with a feeling to avoid, because "how do i say no without sounding lazy" is the wording module's
# offer to draft it, and a language question ("how do i say no in sign language") is not advice.
BARE_SAY_NO = re.compile(
    r"^(?:how\s+(?:do|can|could|should)\s+i\s+"
    r"(?:say\s+no|refuse|turn\s+(?:something|it|that)\s+down)"
    r"|what\s+do\s+i\s+say\s+when\s+i\s+say\s+no)"
    r"(?:\s+without\s+feeling\b[^.!?,;:]*)?\s*[.!?]*\s*$", re.I)


def _turns_on_this_line(text, memory):
    """How many turns in a row, just before this one, asked the same line."""
    wanted = _flat(text)
    if not wanted:
        return 0
    count = 0
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            break
        if _flat(turn.get("user")) != wanted:
            break
        count += 1
    return count


def _without_lead_in(answer):
    """The answer with a repeat lead-in taken off, so a third repeat does not stack them."""
    for frame in AGAIN + (AGAIN_HELP,):
        head = frame.split("{reply}")[0]
        if answer.startswith(head):
            return answer[len(head):].strip()
    # Every other repeat frame in the codebase is a lead-in too, and they live in
    # `bot/memory/again` ("Same answer, and it covers this: ...", "Nothing separate for the biting
    # - it is the same advice: ..."). Not knowing them stacked a second lead-in in front of the
    # first: "Same as before: Same answer, and it covers this: Wash the bin with hot soapy water".
    return same_again.unframed(answer) or answer


# A line that asks whether to make a call is not answered by saying the trouble's steps again:
# "should i see someone" after a cough is the composer's referral to give, and it has the answer
# in hand. The words are the call itself, not the ask around it ("what should i do" is a step).
A_CALL_ASK = frozenset("""see seeing ring call contact phone gp doctor surgery nurse hospital
    dentist vet 111 999""".split())


def _the_line_again(text, memory):
    """The answer just given, said again with the lead-in a repeat gets, or None.

    This is the last thing the knowledge base does: when nothing in it answers the line the
    second time, the answer the person has already been given is still the answer, and a shrug
    is the one reply a repeated question must not get - "im making a cake" then "frosting" twice
    gave the frosting recipe and then "Thanks for telling me - I'm here if you want to dig into
    any of that". Only an answer of ours is repeated, so a repeated "no" or "thanks" is left to
    the small talk, and a line asking about a step already taken ("i tried that") keeps its
    next step from `chat`.
    """
    if not isinstance(memory, dict):
        return None
    if memory.get("frequency_reply"):
        # The turn before the frequency reply is the trouble answer, and a line that leans on the
        # trouble without naming anything of its own ("can i take anything for it") can reach the
        # search hedge because the frequency line, not an answer, is now the last thing said. The
        # answer behind it is still the answer, so the part the line asks is said again. A line
        # with something of its own keeps the normal lookup, and a referral ask is left to the
        # composer, which outranks this module.
        behind = str(memory.get("frequency_answer") or "").strip()
        read = memory.get("understood")
        if (behind and isinstance(read, dict) and read.get("followup")
                and not read.get("change_of_subject") and not read.get("subject")
                and "recommend" not in (read.get("asks") or ())
                and not (A_CALL_ASK & set(read.get("words") or ()))):
            # A line asking for a judgement ("is it worth seeing someone") is left to the
            # composer, which has the answer's referral and is the better reply; only a line
            # asking for a step or a thing gets the part of the answer it asks for.
            return AGAIN[0].format(reply=_repeat_short(behind, text, memory))
    if mem.last_module(memory) != "answers":
        return None
    said = _turns_on_this_line(text, memory)
    answer = _without_lead_in(str(mem.last_bot(memory) or "").strip())
    if not said or not answer:
        return None
    if said >= 3:
        return AGAIN_HELP.format(reply=answer)
    return AGAIN[said - 1].format(reply=_repeat_short(answer, text, memory))


# The words a line says around a topic without naming anything: "my budget", "the budget",
# "our spending". Only these are stripped when asking whether a line is nothing but the store's
# own slot, and only "my"/"our"/"i" make it the person's rather than the topic's.
# The lead-ins and joining words people put in front of the slot, so "and my budget?" and
# "so my budget then" are the same line as "my budget".
_FRAME = frozenset("my our i the a an is was be been it its of on about and but so also then "
                   "now ok okay right well again too".split())


_MINE = frozenset("my our i me mine ours".split())


# The store's own fact keys ("budget", "name", "pet", ...): a line that is nothing but one of
# these is a mention of the slot, not a question about the topic.
_SLOT_KEYS = frozenset(key for key, _ in recall.SUBJECTS)


# The slots whose store reply is a limit the bot then works inside ("Your budget is 400 pounds,
# then - I'll stick to that"), and the entries that would otherwise take the line. A job or a
# city is not a limit at all: "i work in a warehouse on the night shift" keeps the night-shift
# answer, which says more than "Noted: you work in a warehouse on the night shift". Of the
# money entries, only the general ones stand down, because a figure the store has read back is
# still the figure the split entry splits. An entry with a purpose of its own keeps the line -
# "my food budget is 60 a week" is food-bill's, "my wedding budget is 5000" is wedding-budget's,
# and both say something about the figure that a receipt cannot.
_STORED_VALUE = {"budget": frozenset(("budget-how", "budget-split", "budget-rule"))}


# A how-to is not a request for a stored value: "how do i budget" and "what do i do about my
# budget" ask what to do, and the entry is the answer to that.
_HOW_TO = re.compile(r"\b(?:how|help|make|sort|fix|plan|start|do)\b")


# A value is stated rather than planned: "my budget is 400 pounds" hands over a figure, while
# "i set myself a budget of 200" and "my budget of 200" keep the worksheet on main and still do.
_COPULA = frozenset("is are was were s".split())


def _stated_with_copula(text, value):
    """Whether the value is given with "is"/"was" in front of it, not with "of" or a verb.

    "my budget is 400 pounds" and "my food budget is 60 a week" hand over a figure; "i set
    myself a budget of 200" and "my budget of 200" are plans, and on main they keep the
    worksheet, which is what a person asking how to budget wants.
    """
    words = _flat(text).split()
    value_words = _flat(str(value)).split()
    if not words or not value_words:
        return False
    for start in range(len(words) - len(value_words) + 1):
        if words[start:start + len(value_words)] == value_words:
            return start > 0 and words[start - 1] in _COPULA
    return False


def _nothing_but_the_slot(said, value_words, about):
    """Whether the line, with the value taken out, is no more than the slot's own word.

    "my budget of 200" is the same line as "my budget is 200" and main reads it back, while
    "i set myself a budget of 200" has words of its own ("set", "myself") and keeps the
    worksheet there. So the copula is not the whole test; this is the other half of it.
    """
    rest = list(said)
    for word in value_words:
        if word in rest:
            rest.remove(word)
    left = [word for word in rest if word not in _FRAME]
    return bool(left) and all(word in about for word in left)


# The knowledge that answers with food: a line saying what someone does not eat is a diet, and
# the useful reply is a dinner they can eat or the swap for the thing they cannot. Every other
# domain reads a food named after "doesnt eat" as the thing that has stopped being eaten - a pet
# off its food, a child refusing meals - which is a different line about a different subject.
_COOKING_DOMAIN = frozenset(("cooking", "dishes", "meals", "food", "drink", "drinks"))


def _the_food_they_do_not_eat(text, understood):
    """Whether the line only states a food somebody does not eat, and the entry is not about food.

    "my son doesnt eat fish" is the son's diet: the store says it back, and the pet answer - test
    the water, it is nearly always ammonia - is about a fish that has stopped feeding. The same
    line worded as a limit on the person - "my son cant eat fish", "my wife cannot eat gluten" -
    is the same fact, and the store keeps it as their allergy. A line that asks something as well
    keeps its answer ("my son doesnt eat fish, what can i cook"), and so does any domain that
    answers with food, because a dinner round a diet is the better reply than the fact said back:
    "my son doesnt eat meat" still gets the vegetarian dinner and "my son doesnt eat eggs" the
    egg-free swap.
    """
    if not isinstance(text, str) or _HOW_TO.search(_flat(text)):
        return False
    reading = understood if isinstance(understood, dict) else {}
    if reading.get("asks") or reading.get("kind") == "question":
        return False
    stated = mem.facts.extract(text, question=False)
    if not mem.facts.foods_ruled_out(stated):
        return False
    item = find(understood)
    return item is not None and item.domain not in _COOKING_DOMAIN


def _store_keeps_the_line(text, understood):
    """True when the line hands the store a value the entry is about, or asks for one back.

    A person who says "my budget is 400 pounds" is telling the bot something, and a person who
    says "whats my budget" is asking the bot what it kept. Both are the store's turns, and an
    entry about budgeting that answers either one is a how-to for a question they did not ask.
    The entry still answers every line that is a question about budgeting itself ("my budget is
    a mess", "help me with my budget", "how do i make a budget"), because those state no value
    and ask for none.

    The comparison is against the entry's own key words, so a statement about something else
    keeps its answer: "im 34 and thinking of going back to uni" states an age, no entry about
    university is about age, and the answer is unchanged. A value has to be a part of the line
    rather than the line itself, because "i want to plan meals for the week" is filed as a plan
    and the plan is what the meal-plan entry is there to answer.
    """
    if not isinstance(text, str):
        return False
    item = find(understood)
    if item is None:
        return False
    about = _key_words(item)
    if not about:
        return False
    reading = understood if isinstance(understood, dict) else {}
    if reading.get("kind") == "statement":
        stated = mem.facts.extract(text, question=False)
        said = _flat(text).split()
        if isinstance(stated, dict):
            for slot, value in stated.items():
                words = _flat(str(value)).split()
                if item.id not in _STORED_VALUE.get(slot, ()):
                    continue
                if words and words != said and len(words) < len(said) \
                        and (_stated_with_copula(text, value)
                             or _nothing_but_the_slot(said, words, about)):
                    return True
    asked = recall.ask(text)
    if asked and not _HOW_TO.search(_flat(text)):
        return asked in about
    # "my budget", and its like: nothing but the person's own topic, with no ask and no value.
    # That is still the store's, not the entry's: it answered it before this change ("You haven't
    # told me a budget."), and now that "my" is an ask word the entry would take it. The line has
    # to name the slot in the store's own words and say nothing else that the entry is about, so
    # "my budget is a mess" and "i want to sort my budget out" keep the how-to.
    said = [word for word in _flat(text).split() if word not in _FRAME]
    if not said or not all(word in about for word in said):
        return False
    if not any(word in _MINE for word in _flat(text).split()):
        return False
    # ... and the words left have to be the slot's own name, so "my budget plan" still wants the
    # plan: only "budget", "name", "pet" and the rest of the store's keys stand down here.
    return all(word in _SLOT_KEYS for word in said)


# A line that asks what the oven should be set to is asking for a figure, and the oven-runs-hot
# card is about an oven that is wrong. These words keep that card for the question it answers.
_OVEN_CHECK_WORDS = ("check", "checking", "thermometer", "accurate", "runs hot", "running hot",
                     "too hot", "overheat", "overheats", "gone wrong", "be wrong",
                     # an oven with a fault is a fault question, whatever setting is asked for
                     "not heating", "not heat", "wont heat", "won't heat", "cold", "not working",
                     "broken", "fault", "smell", "smoke", "stays on", "stay on", "won't turn off",
                     "wont turn off", "keeps running", "noisy", "noise", "loud", "rattl",
                     "grinding", "squeak", "bulb", "element", "door", "seal", "hinge", "light")


# Only the oven and the fan oven: the figure in a plan is the *oven* figure, and an air fryer,
# a grill or a slow cooker is a different appliance with its own answer.
_OVEN_WORDS = ("oven", "fan oven")


_PROPERTY_WORDS = ("temperature", "temp", "heat", "degrees", "gas", "gas mark", "how hot")


def _says_line(text, words):
    """True when any phrase in `words` is in the line."""
    return any(phrase in text for phrase in words)


# A taste in a line that also asks what to watch, read or listen to is a constraint on the pick,
# not a preference to file away: "what film should i watch if i like sci fi" says what they like
# and asks for the next thing, and read as a bare taste it went to the store, which said it back
# (or to the search hedge), while the film card sat one row away. The frame is narrow on purpose:
# only the three tables that really do pick by taste have one, because the bare "recommend" and
# "what should i do" frames let a card answer a line that named its taste for a reason, and a
# card that is about the wrong thing is worse than the honest "I don't know that one".
PICK_FRAME = re.compile(
    r"\b(?:what|which)\b[^?.!]{0,30}?\b(?:should|could|can|shall|would|do|might)\s+"
    r"(?:i|we|you)\s+(?:watch|read|listen\b|stream|binge)\b"
    r"|\b(?:recommend|suggest)\b[^?.!]{0,40}?\b(?:to watch|to read|to listen|podcast|podcasts|"
    r"film|films|movie|movies|book|books|album|albums|show|shows|series)\b",
    re.I)


def _a_pick_is_asked(text):
    """Whether the line asks what to watch, read or listen to, so a taste is a constraint."""
    return bool(PICK_FRAME.search(str(text or "")))


def _the_line_as_said(text):
    """The line with a filler it opens with taken off, as the understanding engine read it.

    People open a line with "like" the way they open it with "so" or "well", and the word is a
    real one, so a reader that matches it as typed takes "like my back hurts" for a taste of
    theirs ("i like...") and hands the turn to the store. The engine drops the filler and keeps
    the rest, so the readers that go by a phrase ask the line as it was said.
    """
    if not isinstance(text, str):
        return text
    from ..understanding.normalize import _a_leading_like_is_a_filler
    return _a_leading_like_is_a_filler(" ".join(text.lower().split()))
