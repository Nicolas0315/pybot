"""Part 12 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re
import string

from ..understanding.kinds import (the_manners_question)
from . import (trouble)

from .fallback_data import (
    ABOUT,
    ABOUT_ITSELF_KINDS,
    ABOUT_SELF,
    AGREEMENTS,
    ASKING_WORDS,
    CARE_HURTS,
    CARE_INJURY,
    CARE_NOT_RESOLVED,
    CARE_PHRASES,
    CARE_POINTER,
    CARE_PRONOUNS,
    CARE_RESOLVED,
    CARE_WORDS,
    GENERIC_WORDS,
    HAZARD_WORDS,
    HELP_TOPIC,
    HELP_TOPIC_ANY,
    IDENTITY,
    MEMORY,
    MODEL_NAMED_WORDS,
    PICKS_A_MECHANISM,
    REACTION_WORDS,
    SELF_FILLER,
    SELF_GROUP,
    TIGHT_MONEY,
    TIGHT_MONEY_MORE,
    WORRY_FILLER,
    WORRY_WORDS,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    NOT_WHAT_I_SAID,
    ONLINE_ASK,
    PRIVACY_ASK,
    PRIVACY_SHAPES,
)
from .fallback_part_02 import (
    SELF_WORDS,
)
from .fallback_part_03 import (
    ASKING_ASK, A_BARE_ONLINE, BETWEEN_US_ASK, HUMAN_ASK, JUDGING_ASK, LIMITS_ASK, OWN_DEVICE,
    PRIVACY_NOT_THIS, PROMISE_ASK, SECRET_ASK, TRUST_ASK, WORKINGS_ASK, _asks_elsewhere,
    _asks_for_a_person_to_talk_to, _asks_for_help, _opens_the_line, A_VIEW_ASKED_FOR, MADE_ASK,
    MODEL_ASK, NAMES_THE_BOT, REFERS_BACK, REGRET_ASK, SELF_ASK, SELF_OPENER, SELF_PURPOSE,
)
from .fallback_part_06 import (
    SOMEBODY_HURT_ME, A_PERSON_OF_THEIRS, A_PRONOUN_FOR_SOMEBODY, HE, SELF_IN_DANGER, SHE,
)
from .fallback_part_07 import (
    HELP_TOPIC_ASK, FORGETTING_ASK, CLOTHES_ASK, GOOD_AT_ASK, HELP_ELSE, LIKE_ASK, RECALL_TAIL,
    WHAT_ARE_YOU, WHAT_ARE_YOU_NOUN, _free_tail, _the_answers_take_it, _the_store_takes_it,
    BURN_ASK, BURN_BLISTER_LINE, BURN_ON_IT, BURN_THING, BURN_WORD, POP_A_BARE_IT, CARE_POINTER,
    ALREADY_RANG, CARE_ASKS, CARE_HURTS, CARE_SEEN_ASKS, CARE_WORDS, HOUSE_FAULT, STILL_HERE,
    _POINTER_OWN_OBJECT, _someone_is_arriving, ABOUT_THE_SPEAKER, FRIGHTENED, NOT_FRIGHTENED,
)


def _help_topic(clean, understood):
    """A capability ask with a topic gets a line inside that topic, or None.

    "what can you help me cook tonight" is not a request for the list of every domain; the
    engine has already read cooking, so the reply stays there and asks the next question.
    A bare "what can you do" has no topic and keeps the ABOUT help pool.
    """
    if not isinstance(understood, dict) or not HELP_TOPIC_ASK.search(clean):
        return None
    # Only a topic the line names itself: a bare "what can you help with" inherits the last
    # topic from the conversation, and answering it inside that topic would be a guess.
    topic = understood.get("topic_own")
    if not topic or topic in ("about-the-bot", "small-talk", "opinions"):
        return None
    return HELP_TOPIC.get(topic) or HELP_TOPIC_ANY


def reads_as_about_itself(text, memory=None):
    """True when the line is a question about the bot itself, for the arbiter's use.

    A topic entry matches a word or a topic id, so "are you connected to the internet" reached
    the guest-wifi card and "what model do you run" reached the search hedge: the line is about
    the bot, and no entry about the world can answer it. The module that carries this file
    declares `TAKES_AS_IT_COMES` with this, so on these lines the composer's own line takes the
    turn whatever else proposed - and every one of the readings is narrow, so an ordinary
    question that happens to use the same words ("can you think of a name for my cat", "how do
    i connect to the internet") is not claimed.
    """
    clean = _self_line(text)
    # "do you forget things", "did you forget what i said": the bot is the one who might forget, and
    # the memory answer is the one to give. The reading of the question is `FORGETTING_ASK`, the same
    # one that answers it, so a line read here always has the bot's own answer behind it.
    return (_about(clean, None) in ABOUT_ITSELF_KINDS
            or bool(FORGETTING_ASK.search(clean)))


# A question inside the line is still the line's question. "Im skint does that mean i get
# universal credit" is somebody asking about benefits, and "im skint is there any help" is the
# same ask, but the reading's own fence (`kind == question` in bot/understanding/topics.py) sees
# a statement with a question clause hanging off it and lets both through - so the claim answered
# a benefits question with "Right before payday is the hardest bit of the month. What have you got
# in the cupboard?". Any question shape anywhere in the line keeps the turn where it was.
QUESTION_CLAUSE = re.compile(
    r"\b(?:does|do|did|can|could|should|would|will|shall|is|are|was|were|have|has|am)\s+"
    r"(?:there|that|this|it|i|you|we|they|he|she|any|my|me|the)\b"
    r"|\b(?:what|where|who|which|when|how)\s+(?:can|could|should|do|does|did|is|are|would|will|"
    r"am|to|if|about|much|many|long|often)\b")


# What is short is a thing with its own entry. "im skint and i cant afford my electric" is
# answered by the payment-plan card, "im skint and my gas bill is huge" by the warm-home one and
# "im skint and i owe my mate 200" by "say it before they have to ask" - every one of them the
# answer that person needs. The week's own line says what to do about a week with nothing left in
# it, and it is only for the lines that say nothing but that: a line naming a bill, the rent or a
# debt hands the turn back to the entry that knows the thing.
A_THING_THAT_IS_SHORT = re.compile(
    r"\b(?:bill|bills|electric|electricity|leccy|gas|water|council\s+tax|rent|mortgage|"
    r"broadband|wifi|wi-fi|phone\s+bill|arrears|owe|owed|owes|debt|debts|loan|overdraft|"
    r"credit\s+card|store\s+card|direct\s+debit|instal?lment)\b")


def reads_as_a_tight_week(text, memory=None):
    """True when the line only says the money has run out, for the arbiter's use.

    README says the reply to that line is about the tight week, not about saving, and this file
    has it (`TIGHT_MONEY`). A money entry reads a word of the same line ("skint", "no money
    left") and answers a saving question instead - freeing cash over months to somebody asking
    how to get to Friday - so it takes the turn from the composer at PRIORITY 0. The reading is
    the understanding engine's own, and it is narrow: a question is left alone ("what can i cook
    till payday") and so is a line long enough to be about something else, so the composer only
    claims the lines that are nothing but the week being long.
    """
    # The reading is the line's own, so it is made here and not taken from memory: the engine
    # carries the subject of the conversation across turns, so `memory["understood"]` still says
    # the money has run out on the bare continuation after it, and a "go on" a moment after a
    # tight week was answered with the closing line ("Thanks for telling me - I'm here if you want
    # to dig into any of that") instead of the answer's own next step.
    context = dict(memory or {})
    context.pop("understood", None)
    try:
        from ..understanding import understand
        understood = understand(text, context)
    except Exception:  # noqa: BLE001 - a reading that cannot be made claims nothing
        return False
    if not isinstance(understood, dict) or not understood.get("tight_on_money"):
        return False
    try:
        from ..understanding import topics
        if not topics.tight_on_money(understood.get("norm"), understood.get("kind")):
            return False
    except Exception:  # noqa: BLE001 - without the second reading the line is left alone
        return False
    if QUESTION_CLAUSE.search(_self_line(text)):
        return False
    if A_THING_THAT_IS_SHORT.search(_self_line(text)):
        return False
    # A bare "go on" a moment later is somebody asking the bot to keep talking, not the week said
    # again: the pool's line ends by asking what is left and how long till the money comes, and
    # answering the ask with the closing line is worse than saying the answer again. The line is
    # left to the answer path, which has the money in it and hands back the ask it ended on.
    try:
        from ..memory.more import asks_for_more
        if asks_for_more(text):
            return False
    except Exception:  # noqa: BLE001 - a continuation that cannot be read keeps the pool
        pass
    # The composer's own line for it is chosen before the reaction and the flat pools, so this is
    # the same reply the person gets on the phrasings no money entry reads.
    return True


# "and" on its own is the shortest way of saying go on, and the pool that answers a flat ack
# said "Alright then - good luck with it" to it, which ends the conversation the person is trying
# to keep going.
BARE_AND = re.compile(r"^(?:and|and then|and\?|then|so|ok and|and so)[\s.?!,]*$", re.IGNORECASE)


def a_continuation_of_the_tight_week(memory, text):
    """True when a bare "go on" follows the composer's own tight-week line."""
    if not BARE_AND.match(text or ""):
        try:
            from ..memory.more import asks_for_more
        except Exception:  # noqa: BLE001 - a continuation that cannot be read is no continuation
            return False
        if not asks_for_more(text):
            return False
    turns = (memory or {}).get("turns") or []
    if not turns or not isinstance(turns[-1], dict):
        return False
    # The line the bot just said has to be the pool's own, which is what makes this the same
    # subject: a "go on" after anything else is the answer path's turn.
    # The pool's own line or the continuation already given: a second "go on" is the same week
    # still, and the picker never says the same line twice.
    return str(turns[-1].get("bot") or "").strip() in TIGHT_MONEY + TIGHT_MONEY_MORE


# The plainest way of saying it: `_mood` holds "struggling" and the loss reading holds "i cant
# stop crying", but "im not coping" and "i cant cope anymore" are in neither, and a cheerful day
# line after one of them is the bot changing the subject to itself (sure-umbrella on #6004).
_NOT_MANAGING = re.compile(
    r"\b(?:i|im|i'm|i am|we|we're|were)\b[^.]{0,14}\b(?:not coping|cope any ?more|"
    r"can'?t cope|keep going|take any ?more|falling apart|falling to pieces|breakdown|"
    r"breaking point|not managing|cant manage|can'?t manage|do this any ?more)\b")


def _an_answer_above(memory):
    """True when the bot's last line was the knowledge module's answer to a question.

    The same test `bot/memory/repeat.py` makes before it will say an answer again: the turn came
    from `answers`, and it is a line long enough to be an answer and not a question back. A nod,
    a hello or the composer's own closing line is not one - "i went to a party tonight" is
    answered "Thanks for telling me - I'm here if you want to dig into any of that", and the chat
    module's reply to the question after it is better than this pool's.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    last = turns[-1] if isinstance(turns[-1], dict) else {}
    said = str(last.get("bot") or "").strip()
    return (last.get("module") == "answers" and len(said) >= 50
            and not said.rstrip().endswith("?"))


def _a_repair_already_spoken_of(memory):
    """True when the bot's last line already said what a repair would involve.

    "my glasses broke" / "can it be repaired" was answered by the knowledge card with the optician
    and the price of a frame repair; a generic "ask a repair shop for a quote" then talks over an
    answer that had the thing in front of it. A card about a symptom is not that answer - the
    boiler's pressure gauge says nothing about whether it can be mended - so the test is on the
    words of that line, not on the module alone.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    last = turns[-1] if isinstance(turns[-1], dict) else {}
    if last.get("module") != "answers":
        return False
    said = str(last.get("bot") or "").lower()
    return bool(re.search(r"\b(?:repair|repairs|repaired|repairing|mend\w*|fix\w*|"
                          r"replace\w*|replacement|part|parts|quote|quoted|engineer|"
                          r"optician|servic\w+)\b", said))


# The words people put in front of a question when they are changing the subject: "ok random
# question, do you ever make mistakes". They say the person knows the line is a turn away from
# what the chat was on, and every phrase list below is anchored at the start of the line, so a
# lead-in that was kept turned a question about the bot into a card for the last thing talked
# about (a tomato chat answered it with a tomato sauce). These are lead-ins and nothing else: the
# words that carry a subject ("my tomatoes", "the roast") are not on the list, and dropping one
# cannot make a line about the world into a line about the bot.
LEAD_IN = re.compile(
    r"^(?:(?:ok|okay|okey|kk|right|so|ah|oh|ohh|well|anyway|anyways|and|but|now|hmm+|er+|um+|uh+|hey|"
    r"sorry|quick question|random question|stupid question|silly question|daft question|"
    r"this is (?:a bit |a |totally )?random|bit of a random one|a random one|unrelated|"
    r"off topic|just wondering|i was wondering|wondering|can i ask|may i ask|"
    r"just out of curiosity|out of curiosity|by the way|btw)\b[\s,:.!?-]*){1,4}")


def _self_line(text):
    """The line as these readings see it: lowercase, no apostrophes, single spaces, no lead-in."""
    clean = " ".join(str(text or "").lower().replace("\u2019", "'").replace("'", "").split())
    return LEAD_IN.sub("", clean) or clean


def _a_tally_of_its_own_day(understood):
    """True when the line counts the bot's own doings rather than asking what it remembers.

    The reading makes the distinction once (`counts_the_bots_own_day`), so the composer does not
    have to read the line again: the answers lane and this pool ask the same question.
    """
    return bool(isinstance(understood, dict) and understood.get("counts_the_bots_own_day"))


# Chat-speak, spelled out for the phrase tables only. "r u a robot" and "are u a bot" are the
# same question as "are you a robot", and the engine expands a leading "u" or "ur" but not one in
# the middle of a line, so the identity, memory and capability phrases were only ever matched on
# the spelled-out line: "r u a robot" fell through to the search punt while "are you a robot" got
# the answer. One expansion here covers every phrase in those tables, so no table grows a
# chat-speak row of its own. It is not applied to the line anywhere else: a "u" that means the
# letter, or a word that merely ends in one, is only rewritten for this comparison.
_SPELLED_SHORT = (
    (re.compile(r"(?<![a-z])(?:r u|ru|r you|are u|am u)(?![a-z])"), "are you"),
    (re.compile(r"(?<![a-z])u(?![a-z])"), "you"),
    (re.compile(r"(?<![a-z])ur(?![a-z])"), "your"),
    (re.compile(r"(?<![a-z])u r(?![a-z])"), "you are"),
    (re.compile(r"(?<![a-z])wat(?![a-z])"), "what"),
    (re.compile(r"(?<![a-z])wot(?![a-z])"), "what"),
)


def _spelled_out(clean):
    """The line with chat-speak spelled out, for the phrase tables in this file."""
    out = clean
    for pattern, word in _SPELLED_SHORT:
        out = pattern.sub(word, out)
    return out


def _about(clean, understood=None):
    """Which about-the-bot question this is, or None.

    The reading says which kind the line is, so "what can you do with leftover rice" is not
    answered as a question about the bot: the engine sees what follows the question and calls
    it about the rice. The phrase lists stay as a floor for lines the engine does not label.

    The lead-in goes first (`_self_line`, `LEAD_IN`): every list below is anchored at the start of
    the line, so "ok random question, do you ever make mistakes" was read as a line with no ask
    in it at all, and a tomato chat answered it with a tomato sauce recipe.
    """
    clean = _self_line(clean)
    # What the bot does with what it is told. First, because no other reading has a kind for it and
    # the two that answered instead were a card matching "keep" and the search hedge. The line is
    # read with the bot's own pronouns (`_self_line`), so "who can see this chat" and "can anyone
    # see what i say" are the same ask.
    _self = _self_line(clean)
    if (PRIVACY_ASK.search(_self) or PRIVACY_SHAPES.search(_self)
            or BETWEEN_US_ASK.search(_self)) \
            and not NOT_WHAT_I_SAID.search(_self):
        return "privacy"
    # After privacy: "can you keep a secret" and "will you judge me" are the same promise from a
    # shyer angle, but they ask for honesty rather than for a record, and the privacy pool talks
    # about logs where these want a plain yes or no.
    if TRUST_ASK.search(_self):
        return "trust"
    if SECRET_ASK.search(_self) or PROMISE_ASK.search(_self):
        return "secret"
    if JUDGING_ASK.search(_self):
        return "judging"
    # Before the phrase lists: "what are you" sits inside "what are you bad at", and the list
    # would answer the wrong question. Both readings are anchored to the end of the line, so
    # neither can take a line that goes on to ask about something else.
    # What the bot does with what it is told, and whether it can be trusted: no card answered
    # either, so a search hedge went where the bot itself is the only thing that knows. The food
    # and medicine words hold both reads off, since "is this safe to eat" is about the thing in
    # their hand and has an answer of its own.
    # The same fence the branch above applies: "is this private healthcare worth it" matches
    # `PRIVACY_ASK` on the "is this private" shape, and `NOT_WHAT_I_SAID` is the reading of
    # "private" as the kind of thing ("private school", "private rented", "keep my receipts").
    # Without it here the second branch answered the question nobody asked.
    if PRIVACY_ASK.search(clean) and not PRIVACY_NOT_THIS.search(clean) \
            and not NOT_WHAT_I_SAID.search(clean):
        return "privacy"
    if TRUST_ASK.search(clean) and not PRIVACY_NOT_THIS.search(clean):
        return "trust"
    if LIMITS_ASK.search(_self_line(clean)):
        return "limits"
    if ONLINE_ASK.search(_self_line(clean)) and not OWN_DEVICE.search(_self_line(clean)) \
            and not A_BARE_ONLINE.search(clean):
        return "online"
    if the_manners_question([word.strip(string.punctuation)
                             for word in _self_line(clean).split()]):
        # "what are you up to" holds "what are you" and is not the identity card: the whole line
        # asks how the bot is filling its time, which the engine reads as small talk. Both
        # readings below are substring tests, so they would answer a hello with "I'm a chatbot -
        # here to help and chat" and stand the chat pool's own answer down (`hello`).
        if understood is not None and (understood.get("intent") or "") != "smalltalk":
            # The ask is on the line but the engine did not take it as the doings question:
            # "what do you do" is what the bot is for, and standing the capabilities card down
            # for it left the search punt answering (black-lantern, #6380). A reading is what
            # tells the two apart, so without one the answer stays the small-talk one.
            return "help"
        return None
    spelled = _spelled_out(clean)
    if WHAT_ARE_YOU.search(clean) or WHAT_ARE_YOU.search(spelled):
        return "identity"
    # A verb after "what are you" stands the identity card down only when the knowledge module
    # answers the line. Both callers run the same test (`_about(clean, reading)` from the
    # composer, `_about(clean)` from the routing lane), so one line is read one way.
    if re.search(r"\bwhat are you\b", spelled) and not _the_answers_take_it(clean):
        if WHAT_ARE_YOU_NOUN.search(clean):
            return "identity"
        if GOOD_AT_ASK.search(clean):
            return "help"
        if CLOTHES_ASK.search(clean):
            return "clothes"
        if LIKE_ASK.search(clean):
            return "identity"
        return "self_doing"
    # Before the engine's kind and before the help reading: "how do you work" is a question about
    # the bot's make, and both of those were reading it as something else - the engine labels it an
    # about-the-bot question of the "what can you do" kind, and the capability list answered it.
    if WORKINGS_ASK.search(clean):
        return "workings"
    # Before the phrase lists and before the engine's kind: a complaint about the bot's own asking
    # is not a question about the subject it was asking about, and the answer is about the bot.
    if ASKING_ASK.search(_self):
        return "asking"
    for phrase in IDENTITY:
        if phrase in clean or phrase in spelled:
            return "identity"
    if FORGETTING_ASK.search(clean):
        return "memory"
    for phrase in MEMORY:
        if phrase in clean or phrase in spelled:
            if RECALL_TAIL.search(clean) and _the_store_takes_it(clean):
                return None
            return "memory"
    if isinstance(understood, dict):
        kind = understood.get("about_bot_kind")
        if kind in ABOUT or kind in ABOUT_SELF:
            return kind
    # "am i talking to a human", "is this a real person": the same question as "are you a
    # human", asked about the other end of the chat rather than to it.
    asked = HUMAN_ASK.search(clean)
    if asked and _opens_the_line(clean[:asked.start()]) \
            and not _asks_elsewhere(clean[asked.end():]):
        return "identity"
    if _asks_for_a_person_to_talk_to(clean):
        return "identity"
    matched = HELP_ELSE.search(clean)
    if matched and _free_tail(matched.group(1) or matched.group(2)):
        return "help"
    # "can you help me" is an ask to the bot with nothing else on the line: there is no subject
    # to understand and nothing to search for, so the honest answer is what it is for, not the
    # shrug. A chore or a topic after it ("can you help me end this email", "can you help me with
    # my cv") is a line about that thing, so this only reads the ask on its own.
    if _asks_for_help(clean, understood):
        return "hand"
    return _the_bot_itself(clean)


# The model's name in the line is the bot's own make, not a fact about the world: "is this
# chatgpt", "which version of gpt are you", "are you claude". MODEL_ASK above reads the shape
# ("what model are you"), and these say the same thing with the name in a different place, so the
# search hedge answered them as if a search could settle what the bot is made of. Read only in a
# short line: "is this chatgpt good for essays" is about the essays, and "what model is this" can
# be a follow-up about a car.
MODEL_NAMED = re.compile(
    r"\b(?:what|which)\s+(?:version|model|kind|type|sort)\s+of\s+(?:gpt|chatgpt|ai|llm|model|"
    r"chatbot|bot|openai)\s+(?:are|is)\s+(?:you|u|this|it)\b|"
    r"\b(?:is|are)\s+(?:this|that|it|you|u)\s+(?:a\s+|an\s+|really\s+)?(?:chatgpt|gpt[-\s]?\d*|"
    r"openai|claude|gemini|bard|llama|copilot|an?\s+(?:ai|llm|chatbot|bot))"
    r"\s*(?:then|really|though|now|huh|yeah|or not)?\s*$")


def _names_the_make(clean):
    """Whether the line names what the bot is made of, in a line short enough to be only that."""
    said = re.findall(r"[a-z0-9']+", str(clean or "").lower())
    return len(said) <= MODEL_NAMED_WORDS and bool(MODEL_NAMED.search(" ".join(said)))


def about_the_bot(clean):
    """The composer's reading of the line as a question about the bot itself, or None.

    The kinds are the ones `_about_itself` already returns ("learn", "think", "feel", "purpose",
    "where", "agency", "model"). The routing lane reads it in bot/modules/arbiter.py, so the two
    lanes share one reading of "this is about you" rather than each keeping a list of words.

    """
    return _the_bot_itself(clean)


# A doubt about a capacity is the same question as the capacity, asked the other way round:
# "so you cant learn then", "you cant remember things can you", "so you dont do sums then". On
# main the first and the third got "I'm listening - say more if it helps", which answers neither
# half, while "can you learn" got the honest paragraph about nothing carrying over - the person
# was checking that paragraph, not changing the subject. What makes the re-reading safe is that
# it only rewrites the wrapper: the opners people put in front, the "then"/"though" on the end,
# the tag question, and the negated auxiliary, and then hands the rest to the same reading. A line
# that names something of its own ("you cant learn this song for me", "so you cant come
# tomorrow then") comes out of `_about_itself` with a word it does not know and is not claimed.
DOUBT_OPENER = re.compile(r"^(?:so|and|but|oh|ok|okay|well|right|actually|honestly)\s+")


DOUBT_TAIL = re.compile(
    r"(?:\s+(?:then|though|really|at all|any more|anymore|these days))+$"
    r"|\s+(?:can|could|do|does|are|will|would)\s+(?:you|u)$")


DOUBT_NOT = re.compile(
    r"\b(?:you|u(?:r)?)\s+(?:just\s+|only\s+|actually\s+|really\s+|still\s+)?"
    r"(?:can ?t|cant|cannot|can not|could ?nt|couldn ?t|don ?t|dont|do not|does ?nt|doesn ?t|"
    r"won ?t|wont|will not|never)\s+")


# "youre not a person then", "you are not a real person are you": the doubt is about what the bot
# is rather than what it can do, so the auxiliary goes back the other way round.
DOUBT_NOT_BE = re.compile(r"\b(?:youre|you are)\s+(?:not|n ?t)\s+")


def _a_doubt_about_the_bot(clean):
    """Which question about the bot this doubt is asking, or None."""
    line = clean
    for _ in range(3):
        stripped = DOUBT_OPENER.sub("", line)
        if stripped == line:
            break
        line = stripped
    line = DOUBT_TAIL.sub("", line)
    asked = None
    notted = DOUBT_NOT.search(line)
    if notted:
        asked = "can you " + line[notted.end():].strip()
    else:
        notted = DOUBT_NOT_BE.search(line)
        if notted:
            asked = "are you " + line[notted.end():].strip()
    if not asked or asked.endswith(("you", "you can", "you are")):
        return None
    return _about(asked, None)


def _the_bot_itself(clean):
    """The bots-own-kind reading, with the doubt shape read as the question it is asking."""
    clean = _self_line(clean)
    return _about_itself(clean) or _a_doubt_about_the_bot(clean)


# "how do you decide" asks how the bot works; "which do you pick" asks it to choose between the
# person's options and has a cheerful answer of its own ("I'm easy on it — it's not a hill I'd
# argue from"). The words are shared, the ask is what tells them apart, so only a "how" line is
# read as a question about the workings.
# "What do you know about me" carries the bot's own word for knowing, and it is the store's line to
# answer ("So far I know you said you cannot swim; your dad has cancer"), not a question about the
# bot's nature: read as one it got "there's nobody home; ask me something and see what you get".
# A line that asks what it knows or keeps of the person is therefore left alone here.
ABOUT_THE_PERSON = re.compile(
    r"\babout (?:me|us|my|our)\b|\bknow (?:about|of) (?:me|us|my)\b"
    r"|\bremember (?:me|my|what i|what we|anything|things)\b|\bwhat have you (?:kept|remembered)\b",
    re.I)


def _about_itself(clean):
    """Which question about the bot's own nature this is, or None.

    Nothing on the line but the bot and a word for a mind or a machine is a question about the
    bot; the same shape with something else on the end is about that thing, so "can you think
    of a name for my cat" and "can you learn this song for me" are not answered here.
    """
    if REFERS_BACK.search(clean) and not NAMES_THE_BOT.search(clean):
        # A follow-up about what the bot said, not about what the bot is. The exception is the
        # line that points back and names what the bot might be: "did you say you were human"
        # and "did you say you were an ai" are the one thing this bot can always answer, and
        # standing aside sent them to "searching will turn up better sources than I can offer".
        return None
    # The words of the line with the punctuation taken off: `SELF_WORDS` is a list of plain words,
    # so "can you learn things?" and "do you have opinions?" were read as sentences with one word
    # in them that the bot does not know ("things?", "opinions?") and fell through to the search
    # hedge, while the same questions without the mark got their answer. People type the mark.
    said = [word.strip("?!.,;:\"'()") for word in clean.split()]
    if REGRET_ASK.search(clean):
        return "regret"
    if SELF_PURPOSE.search(clean):
        return "purpose"
    if MADE_ASK.search(clean):
        return "agency"
    if MODEL_ASK.search(clean) or _names_the_make(clean) or WORKINGS_ASK.search(clean):
        return "model"
    if LIMITS_ASK.search(_self_line(clean)):
        return "limits"
    if ONLINE_ASK.search(_self_line(clean)) and not OWN_DEVICE.search(_self_line(clean)) \
            and not A_BARE_ONLINE.search(clean):
        return "online"
    if not SELF_ASK.search(clean):
        return None
    # "do you think that was a mistake" asks for a view of the thing that happened, and it was
    # answered as a question about the bot's own mind ("there's no mind behind it, just rules
    # doing their job") because the words left after the fillers - "think", "mistake" - are both
    # on the self list. The clause's own subject settles it: a "you" straight after the verb is
    # still the bot being asked about ("do you think you are clever", "can you think for
    # yourself"), and any other subject is the thing the view is wanted on.
    view = A_VIEW_ASKED_FOR.match(clean)
    if view and not re.match(
            r"\s*(?:you|u|youre|you're|ur|yourself|for\s+yourself|about\s+yourself|"
            r"by\s+yourself|on\s+your\s+own)\b", view.group(1)):
        return None
    if ABOUT_THE_PERSON.search(clean):
        return None  # "what do you know about me" is the store's to answer, not the bot's nature
    # The bot's own pronouns are not one of the words it is asked about, and "youre" is as much
    # one as "you": "do you think youre clever" was left with nothing but the ask words and fell
    # past this reading to the search hedge, while "do you think you are clever" was answered.
    rest = [w for w in said
            if w not in SELF_FILLER and w not in ("you", "u", "youre", "you're", "ur")]
    if not rest:
        # "where are you", "do you have a family": nothing but the bot and an opener, so it asks
        # where it is in the world. "why are you here" is the same shape and a different
        # question — its point, not its address — so it keeps a reply of its own.
        if re.search(r"\bwhy\b", clean):
            return "purpose"
        return "where" if SELF_OPENER.search(clean) else None
    if any(w not in SELF_WORDS for w in rest):
        return None
    for word in rest:
        if word in PICKS_A_MECHANISM and not re.search(r"\bhow\b", clean):
            continue
        group = SELF_GROUP.get(word)
        if group == "where" and word in ("here", "there") and re.search(r"\bwhy\b", clean):
            return "purpose"  # "why are you here" asks the point, not the address
        if group:
            return group
    return None


def _burn_line(clean, thread=""):
    """True for a line inside a burn thread that is about the burn: what to put on it, or the
    blister. A bare "cream"/"ice" only counts when the line is a question, because a shopping
    list and a bowl of ice cream are not questions about a burn.

    A bare "it" is the blister when the thread is a burn: "can i pop it" names nothing, and
    letting it go hands the person a search hedge."""
    if BURN_BLISTER_LINE.search(clean) or BURN_ON_IT.search(clean):
        return True
    if POP_A_BARE_IT.search(clean) and (BURN_WORD.search(str(thread or "").lower())
                                        or BURN_WORD.search(clean)):
        return True
    return bool(BURN_THING.search(clean) and BURN_ASK.search(clean))


# The way out of the emergency is not a new subject, even when it names its own place. A person
# in a fire thread asking "should i get out of the house", or in a burn thread asking "can i open
# a window", is asking how to be safer, and main answered the fire one with the shrug ("Not mine
# to decide, sorry"): "house" has a topic of its own, so the thread gate ended the emergency
# before the pointer rule could keep it.
# The domestic abuse card is the one safety answer that names a helpline for a danger that is a
# person at home, and this file reads a helpline as a suicide crisis ("116 123", "the crisis
# line"). So the card is recognised by its own words, and the thread it opens is answered as the
# person's own danger rather than as somebody else's.
ABUSE_CARD = re.compile(r"\b(?:domestic\s+)?abuse\s+(?:helpline|charity|service|line)\b", re.I)


# The question an abuse thread is actually asked: whether to leave. It is not the way out of a
# building ("should i get out of the house" is), so it needs its own reading, and a bare "should
# i leave" was answered "Not mine to decide, sorry" to a person who had just been hit.
_ASKS_TO_LEAVE = re.compile(
    r"\b(?:should|shall|can|could|do|must)\s+(?:i|we)\s+(?:just\s+)?"
    # "should i leave the washing up" is the washing up, not a person: only leaving with nothing
    # after it, or with a person after it, is the question.
    r"(?:leave|go|stay|come\s+back|go\s+back|walk\s+out|get\s+out|move\s+out|run)\b"
    r"(?!\s+(?:the|my|your|a|an|it|this|that)\b)"
    # "should i call the police" is the same question in the same thread, and the pool's answer
    # is the right one for it: go when it is safe to, and 999 if you cannot get to the door.
    r"|\b(?:should|shall|can|could|do|must)\s+(?:i|we)\s+(?:call|ring|phone|dial)\s+"
    r"(?:the\s+)?(?:police|cops|999|911|an?\s+ambulance)\b", re.I)


_THE_WAY_OUT = re.compile(
    # Getting out of the place the emergency is in is the way out.
    r"\b(?:get|gets|getting|got|come|comes|coming|clear|clearing|climb|climbing|stagger\w*)\s+"
    r"out\s+of\s+(?:a|an|the|my|our|his|her|their)?\s*"
    r"(?:house|home|flat|building|block|room|car|van|vehicle|bed|bath|bathroom|kitchen|lift|"
    r"elevator|road|water)\b"
    # ...and so is asking whether to stay put, move, or let some air in.
    r"|(?:\b(?:should|shall|do|can|could)\s+(?:i|we)\b"
    r"|\bis\s+it\s+(?:safe|ok|okay|alright|best|wise)\b"
    r"|\bwould\s+it\s+be\s+(?:better|safer|ok|okay)\b"
    r")[^.?!]{0,20}\b(?:go|going|get|leave|leaving|stay|staying|move|moving|open|opening|"
    r"close|closing|shut|shutting|ventilate)\b[^.?!]{0,20}\b(?:outside|outdoors|upstairs|"
    r"downstairs|up\s+stairs|down\s+stairs|home|house|flat|building|room|away|clear|"
    r"fresh\s+air|window|windows|door|garden|corridor|landing|down|up|"
    r"out\b(?!\s+of)|back\s+in|back\s+inside|in\s+there)\b"
    # Staying put is the same question and it names no place of its own: "should i stay where i
    # am" was answered "That's your call, not mine", to a person who has just been told to get
    # out. The second half is what makes it the waiting rather than a plan: where they are, put,
    # here, inside, or waiting for the help to come.
    r"|\b(?:should|shall|do|can|could|must)\s+(?:i|we)\s+(?:just\s+)?(?:stay|wait|sit|hold)\b"
    r"[^.?!]{0,20}\b(?:where\s+(?:i|we)\s+am|where\s+(?:i|we)\s+are|put\b|here|inside|"
    r"in\s+the\s+(?:house|flat|room|car|building)|for\s+(?:help|the\s+(?:ambulance|fire|"
    r"paramedics|doctor)|them|someone))\b",
    re.I)


_HAZARD_WORD = re.compile(
    r"\b(?:" + "|".join(sorted(re.escape(w) for w in HAZARD_WORDS)) + r")\b", re.I)


# Nothing inside is worth going back in for, and people ask it without naming the place: "can i
# get my passport" a turn after the fire card was answered with the passport service, and "should
# i go and get the dog" with nothing about the fire at all. Only inside a hazard thread - a person
# asking "can i get my prescription" after a cut is asking about the chemist, and that is a new
# subject, so the hazard has to be the line this thread was opened with.
_FETCH_FROM_INSIDE = re.compile(
    r"\b(?:can|could|should|shall|do|may)\s+(?:i|we)\s+(?:just\s+|quickly\s+)?"
    r"(?:go\s+(?:and\s+|to\s+)?)?"
    r"(?:back\s+in|get|grab|fetch|collect|save|rescue|nip\s+in|run\s+in)\b[^.?!]{0,30}"
    r"\b(?:my|our|the|his|her|their)\s+\w+", re.I)


# Gas is not smoke, and the way out of it is not the way out of a fire: the windows open and the
# boiler goes off before anyone leaves. The way-out arm above would otherwise hand a gas thread the
# fire escape ("get to a room with a window, shut the door") - good advice with a fire behind the
# door, and the wrong advice with a leak. The hazard has to be the line the thread opened on, and a
# fire thread is never a gas thread however the boiler is fuelled.
_GAS_WORD = re.compile(r"\b(?:gas|gases|fumes?|carbon\s+monoxide|flue)\b", re.I)


_FIRE_WORD = re.compile(r"\b(?:fires?|flames?|smoke|smoking|ablaze|burning|burnt)\b", re.I)


def _the_hazard_is_gas(line):
    """True when the emergency this thread opened on is a leak rather than a fire."""
    said = str(line or "")
    return bool(_GAS_WORD.search(said)) and not _FIRE_WORD.search(said)


def _goes_back_for(clean, thread=""):
    """True when the line asks to fetch something out of the place a hazard is burning in."""
    if not (_HAZARD_WORD.search(clean) or _HAZARD_WORD.search(str(thread or ""))):
        return False
    return bool(_FETCH_FROM_INSIDE.search(clean))


def _names_a_new_part(words, clean, thread):
    """True when the line complains about a part of the body this thread never mentioned.

    "my back is stiff" a turn after a burn is a second complaint, said with a word the care
    vocabulary already knows: whoever answers that part should get it, or the person who has
    moved on to their back is told to keep an eye on the burn. Two things keep the thread,
    because both are the same complaint still going on: a part the thread already named ("my
    hand is still sore"), and a pointer back to it ("its still sore", "call them back"). A new
    part said without a pain word ("spreading to my arm") is not a complaint of its own either.
    """
    part = words & trouble.BODY_PART
    if not part or not trouble.reads_as_trouble(clean, words):
        return False
    if words & (CARE_POINTER | CARE_PRONOUNS):
        return False
    seen = set(re.findall(r"[a-z0-9']+", str(thread or "").lower()))
    return not (part & seen)


def _keeps_thread(understood, clean, thread="", crisis=False):
    """True when the line is still about the emergency, rather than a new subject.

    A person mid-emergency says "it's still soaking through" or "is it safe to go down the
    stairs"; a person who has moved on says "what should i cook tonight". The second kind must
    not get emergency advice, so a new subject ends the thread, while short replies, check-ins
    and the questions people ask inside one keep it.
    """
    norm = understood.get("norm")
    if isinstance(norm, (list, tuple)):
        words = set(norm)
    else:
        words = set(re.findall(r"[a-z0-9']+", str(norm or clean)))
    if not crisis and _names_a_new_part(words, clean, thread):
        # A second complaint about another part of the body, in a care thread, is a new subject
        # and goes to whoever answers that part; it outranks the care words it is said with.
        return False
    if _ASKS_TO_LEAVE.search(clean) and SOMEBODY_HURT_ME.search(str(thread or "")):
        # "should i leave" after "my wife hits me" is the question of that thread, and "leave"
        # reads as a subject of its own, so the gate ended the emergency before the abuse card
        # could answer it (the shrug, "Not mine to decide, sorry"). The thread's own line is
        # what makes this the same question, so it is read here.
        return True
    if _THE_WAY_OUT.search(clean):
        # "Should i get out of the house", "can i open a window": how to be safer is still the
        # emergency, whatever place it names. This one comes before every other answer, because
        # the shrug on a fire card ("Not mine to decide, sorry") is the worst reply in the file.
        return True
    if words & CARE_HURTS:
        return True
    if not crisis and not (words & CARE_INJURY) and HOUSE_FAULT.search(clean):
        # A fault about the house itself ("the oven door doesnt shut properly", "the boiler is
        # broken") is a different subject from the one being treated, even though "door" and
        # "floor" are in the care vocabulary. A live emergency is not a different subject: "the
        # window wont open" in a thread where someone is bleeding badly is how they get out, so
        # the emergency line keeps the turn (cream-flag, #routing).
        return False
    if (words & CARE_WORDS) - CARE_POINTER or CARE_ASKS.search(clean):
        return True
    own = understood.get("topic_own")
    if words & CARE_RESOLVED and words & CARE_NOT_RESOLVED and own in (None, "feelings", "health"):
        # "it hasnt stopped", "i dont feel better": a negated resolution is not a resolution,
        # and it is still the emergency. A new subject of its own still ends the thread.
        return True
    if words & REACTION_WORDS:
        return True
    if words & CARE_POINTER and not understood.get("topic_own") \
            and not _POINTER_OWN_OBJECT.search(clean):
        # A pointer word keeps the thread only when it is pointing at the emergency. "How do i get
        # out of a parking ticket" has an "out" in it, and the pointer rule answered it with the
        # 999 line in a heart-attack thread instead of the parking answer it gets on its own.
        return True
    if any(phrase in clean for phrase in CARE_PHRASES) or CARE_SEEN_ASKS.search(clean):
        return True
    if _someone_is_arriving(clean):
        # "my sister says she can come over tonight" is news about the emergency, not a new
        # subject, and it is answered as such below rather than with the generic advice.
        return True
    if ALREADY_RANG.search(clean):
        # "i phoned samaritans", "i called the crisis line", "i rang the doctor": the person is
        # saying what they did about the emergency, and the answer below depends on which number
        # it was (`A_HELPLINE`). Letting the line go here gave the turn to the last pool in the
        # composer, so "i want to kill myself" / "i phoned samaritans" was answered "Sounds
        # alright. Anything good in it?" - a cheer at somebody who had just rung a crisis line.
        return True
    if _burn_line(clean, thread):
        # "should i put butter on it", "can i pop the blister": still the burn, not a new subject.
        return True
    if understood.get("presence") or STILL_HERE.search(clean):
        # "can you hear me" during a fire is about the emergency, not a new subject.
        return True
    if understood.get("kind") == "thanks":
        # A short thanks closes the thread warmly; a thanks with a new ask does not.
        return len(words) <= 5
    if crisis and words & trouble.BODY_PART:
        # A crisis keeps every part of itself: "my head is hurting" while the person is in
        # danger is the emergency still going, not a second complaint. Skipping the new-part
        # rule above is not enough, because such a line can fail this function for the ordinary
        # reason of having a subject of its own. Only a body part needs this: a feeling
        # ("i feel angry") is still a change of subject, in a crisis or not.
        return True
    if understood.get("kind") == "question" or "?" in clean:
        # "what happens now", "how long will it take": a question with nothing but generic
        # words is still about the emergency, while one that brings a subject of its own
        # ("what time does tesco close", "what should i cook tonight") ends the thread.
        keywords = understood.get("keywords") or []
        return all(str(word).lower() in GENERIC_WORDS for word in keywords)
    if len(words) <= 2 and words & AGREEMENTS:
        # "same", "ditto", "likewise": a nod that agrees with the line before it and names
        # nothing. The last resort below reads a word of more than three letters as a subject of
        # its own, so it ended the emergency on "same" (four letters) and sent "i feel like i
        # want to die" / "same" to the fallback's "Ha, fair enough", and "same here" to "Great -
        # shout if you need anything else" (safety lane, #routing). "ok" and "yeah" were never
        # caught because they are too short to count as a subject, so this puts the agreements
        # back beside them.
        return True
    if not understood.get("topic_own"):
        # No subject of its own is not the same thing as the emergency going on. "i keep
        # falling asleep in the afternoon" two turns after a fall is a subject the reader gave
        # no topic to, and this last resort kept the thread for it, so the composer answered
        # "ring 999 or 911 now" over the sleep entry that fitted the line (see
        # `deck/care-thread.jsonl`). The last resort now asks whether the line names anything
        # the thread has not: a line made of asking words ("i dont know what to do") names
        # nothing and keeps the emergency, and one that names its own subject is a new subject,
        # whichever part of the bot should have given it a topic.
        mine = {w for w in words if len(w) > 3 and w not in ASKING_WORDS}
        thread_words = set(re.findall(r"[a-z0-9']+", str(thread or "").lower()))
        return bool(mine & thread_words) or not mine
    return False


def _reads_as_fear(understood, clean):
    """True when the line is the speaker's own fear, not a practical question about the incident.

    "i'm scared", "i can't stop shaking", "i'm terrified". A question ("should i call an
    ambulance", "how do i change the dressing") keeps the practical pool: fear words in an ask
    are about the incident, and that is where the real instructions belong. "Worried" and
    "nervous" are not in the pool: "i'm worried about her appointment on tuesday" wants the
    practical continuation, and so does anything that says the fear is off ("im not scared").
    """
    if understood.get("kind") == "question" or "?" in clean:
        return False
    if CARE_ASKS.search(clean):
        return False
    if not ABOUT_THE_SPEAKER.search(clean):
        return False
    if NOT_FRIGHTENED.search(clean):
        return False
    if FRIGHTENED.search(clean):
        return True
    return _only_a_worry(clean)


def _only_a_worry(clean):
    """True when the whole line is the speaker's worry and nothing else."""
    if re.search(r"\babout\b", clean):
        return False
    words = re.findall(r"[a-z']+", clean)
    if not words or len(words) > 6:
        return False
    if not WORRY_WORDS & set(words):
        return False
    return all(word in WORRY_FILLER or word in WORRY_WORDS for word in words)


# Coming back to a thread rather than starting one: "im back", "still here", "hiya". Only the
# shapes that are all of the line, so "back on sugar" is the diet it says and "hi, its still
# bleeding" is the report it is.
A_BACK_AGAIN = re.compile(
    r"^(?:(?:im|i'm|i am)\s+)?(?:back|here|still here)(?:\s+(?:again|now|too))?[.!]*$|"
    r"^(?:hi|hiya|hello|hey)(?:\s+[a-z']+){0,2}[.!]*$")


def _about_somebody_else(safety, memory):
    """The words for the person in danger when the crisis was about somebody else, else None.

    Returns the parts every line of CRISIS_AFTER_THEM needs - the relation as the person said it
    ("your sister"), and the pronouns and the verb that go with it - or None when the thread is
    the speaker's own crisis, which is what CRISIS_AFTER is written for.

    The line that decides is the safety turn's own user line, and nothing later: "now shes
    talking about it again" is a follow-up whose subject is only in the earlier line. When that
    line names nobody ("shes talking about suicide" after "my wife has been low for months"),
    the last few lines of the chat are read instead, so the relation is still the person's own
    words rather than a guess from the pronoun.
    """
    opener = str((safety or {}).get("user") or "")
    if SELF_IN_DANGER.search(opener):
        return None
    if SOMEBODY_HURT_ME.search(opener):
        # "my husband hit me": she is the one in danger, not him, so this is the speaker's own
        # crisis and the carer's words would be said to the wrong person.
        return None
    found = A_PERSON_OF_THEIRS.search(opener)
    if found is None:
        # Only a pronoun sends this looking backwards: "shes talking about suicide" with the
        # person named a turn earlier. A line with neither a relation nor a pronoun ("im scared",
        # "i dont know what to do") belongs to the person typing, and an old "my mum" from
        # another corner of the chat must not turn it into a carer's line.
        if not A_PRONOUN_FOR_SOMEBODY.search(opener):
            return None
        try:
            turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
        except AttributeError:
            return None
        for turn in reversed(turns[-4:]):
            said = str(turn.get("user") or "")
            if said == opener or SELF_IN_DANGER.search(said):
                continue
            found = A_PERSON_OF_THEIRS.search(said)
            if found is not None:
                break
    if found is None:
        return None
    word = re.sub(r"\s+", " ", found.group("who").strip().lower())
    if word in SHE:
        forms = {"subject": "she", "object": "her", "possessive": "her", "be": "is"}
    elif word in HE:
        forms = {"subject": "he", "object": "him", "possessive": "his", "be": "is"}
    else:
        forms = {"subject": "they", "object": "them", "possessive": "their", "be": "are"}
    forms["who"] = "your " + word
    return forms


def _wrote_for_them(pool, forms):
    """One pool's lines, filled with the words for the person they are about."""
    return tuple(line.format(who=forms["who"], subj=forms["subject"], obj=forms["object"],
                             poss=forms["possessive"], be=forms["be"]) for line in pool)


# A number named as a threshold is not a call to make now. The chest-on-effort answer ends "Ring
# 999 or 911 straight away if it becomes pressure, spreads to the arm or jaw, or comes with
# breathlessness or sweating", and the person's next line ("is that normal", "what should i do")
# was handed "ring 999 or 911 now" as if the bot had told them to ring in the first place - a
# harder instruction than the answer it followed, which had said 111 or the GP today. The rule is
# the one @ivory-orange gave on #safety: an emergency answer tells them to ring now, a warning
# names the number as a threshold. "If you haven't already, ring 999" is still a call to make:
# the condition there is only about whether the phone is already in their hand.
A_CONDITION = re.compile(r"\b(?:if|unless|when|whenever|once|in case|as soon as)\b", re.I)


ALREADY_OR_NOT = re.compile(r"\bif\s+(?:you\s+)?(?:have\s?n[o']?t|havent|not)\b", re.I)


SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")


# A call is judged clause by clause, because one answer can hold both kinds: the gas card says
# "Ring 0800 111 999 (UK) or 911 from outside, and 999 straight away if anyone feels ill" - the
# first call stands on its own and only the second is a threshold.
CLAUSE_END = re.compile(r"[,;:]\s+|\s+(?:and|but|so|then|or)\s+")


# The route a care answer names, in the order that picks the most specific one: a gas emergency
# number is not the 111 line (it holds the digits), and a vet is not a GP.
CARE_ROUTE_WORDS = (
    ("vet", re.compile(r"\b(?:the\s+)?vets?\b", re.I)),
    ("dentist", re.compile(r"\bdentist\w*\b|\bdental\b", re.I)),
    ("pharmacist", re.compile(r"\bpharmac(?:ist|y)\b|\bchemist\b", re.I)),
    ("walk-in", re.compile(r"\bwalk[- ]in\b|\burgent care\b", re.I)),
    ("111", re.compile(r"(?<!\d)111(?!\d)|\bnhs 111\b", re.I)),
    ("gp", re.compile(r"\b(?:gp|g\.p\.|doctor|surgery|practice nurse)\b", re.I)),
)


# The person's own reassurance about somebody: a child who is eating and playing, a patient who
# seems themselves. The answer above already said what to do, so saying it again harder reads as
# not having heard the good bit.
THE_THING_ITSELF_LOOKS_FINE = re.compile(
    r"\b(?:eating|drinking|playing|running about|running around|chatting|talking|sleeping well|"
    r"seems (?:fine|himself|herself|themselves|ok|okay|alright|bright)|looks (?:fine|well|ok|"
    r"okay|alright|better)|perky|bright as|back to (?:normal|himself|herself))\b", re.I)


# The words an answer uses when it names 999 as a threshold: "Ring 999 or 911 straight away if it
# becomes pressure, spreads to the arm or jaw, or comes with breathlessness or sweating." A line
# that says one of those words back is standing on the threshold the answer named, and the route
# that answer named first (111, the GP) is not the reply to it - that hands the person a phone call
# for the very moment the answer itself called an ambulance for.
RED_FLAG_SHARED = re.compile(
    r"\b(?:arm|arms|jaw|neck|shoulder|shoulders|back|chest|sweat\w*|clammy|breathless\w*|"
    r"breath|breathing|lip|lips|grey|gray|blue|faint\w*|passed\s+out|collaps\w*|rest|resting|"
    r"sitting|speech|slurr\w*|numb(?:ness|ed|ing|s)?|drow\w*|floppy|seizure|fits?|vomit\w*|blood|pale|"
    r"dizz\w*)\b", re.I)


def _red_flags_in(line):
    """The flag words in the line, leaving out the ones the line itself says are gone.

    "im not sweating any more" and "the sweating has stopped" are a person reporting the relief,
    and telling them to ring 999 for it is the bot not listening. Read word by word, though,
    because the rest of the line can still carry one: "no longer sweating but my arm hurts" has
    an arm that is worth the call.
    """
    low = " ".join(str(line or "").lower().split())
    flags = set()
    for match in RED_FLAG_SHARED.finditer(low):
        before = low[:match.start()].split()[-4:]
        after = low[match.end():].split()[:4]
        if any(word in ("not", "no", "never", "isnt", "arent", "havent", "hasnt", "dont", "didnt")
               for word in before):
            continue
        if "stopped" in after or ("any" in after and "more" in after) or \
                ("no" in after and ("more" in after or "longer" in after)):
            continue
        flags.add(_flag_stem(match.group()))
    return flags


# The signs that are an emergency on their own, whatever the answer happened to list: a faint, a
# collapse, cold and clammy skin, speech that has gone. The answer's own sentence is the right
# vocabulary for the words that are only a flag in context (an arm, a back, dizzy), but not for
# these: "i passed out this morning" after a chest-on-effort answer was handed the answer's 111
# route back, because that answer's 999 sentence never said "passed out" (white-pigeon, #8509).
RED_FLAG_EVENTS = re.compile(
    r"\b(?:passed\s+out|passing\s+out|fainted|fainting|collaps\w*|unconscious|knocked\s+out|"
    r"clammy|slurr\w*|floppy|seizures?|convuls\w*|drooling|not\s+waking|cant\s+wake|"
    r"couldnt\s+wake|could\s+not\s+wake|wont\s+wake)\b", re.I)


def _flag_events_in(line):
    """The signs in the line that are an emergency by themselves, leaving out the denied ones."""
    low = " ".join(str(line or "").lower().split())
    found = set()
    for match in RED_FLAG_EVENTS.finditer(low):
        before = low[:match.start()].split()[-4:]
        if any(word in ("not", "no", "never", "isnt", "arent", "havent", "hasnt", "dont",
                        "didnt", "wasnt", "without") for word in before):
            continue
        found.add(_flag_stem(match.group().split()[0]))
    return found


# The answer can name its threshold in a word this file's flag list has no entry for. The
# chest-on-effort answer ends "Ring 999 or 911 straight away if it becomes pressure, spreads to
# the arm or jaw", and "it feels like pressure now" was answered with the neutral nod: the flag
# list carries an arm, a jaw, a chest and breathlessness, but not pressure, which is the word the
# answer itself puts first. So the clause after the answer's own if is read for the signs it
# names, instead of growing the list one card at a time. The line has to say the word as a
# feeling of their own ("it feels like pressure now", "the pressure is back"), which keeps an
# ordinary "im under pressure at work" a turn later from being a heart attack.
THRESHOLD_CLAUSE = re.compile(r"\b(?:if|when|whenever|once)\b\s+(.{3,140})", re.I)


# The words of that clause that are the instruction rather than the sign: the call itself, the
# number, when it is wanted by, and the joining words.
THRESHOLD_NOT_A_SIGN = frozenset("""
the a an and or of to in on at for with without if it its this that your you yours they them
their he she his her is are was were be been being do does did done have has had can could would
should will shall may might must not no dont cant wont also too very really just only even still
more most less least than then there here any anything something everything nothing someone
somebody anyone anybody what when where which who how why get gets getting go goes going went come
comes coming make makes making take takes taking please sorry help helps helped need needs needed
want wants wanted like likes tell tells told say says said see sees look looks try tries tried
thing things way ways time times day days moment minute hour about after before again once twice
first last next other another same own such because so but however though always never sometimes
often soon later early late today tonight tomorrow morning afternoon evening night emergency
emergencies ambulance hospital doctor gp nurse care service services team advice line risk danger
sign signs symptom symptoms feeling feel feels felt seem seems seemed become becomes became
becoming much many lot lots bit little kind sort sure give gives given keep keeps watch watching
worse bad good well hard suddenly sudden started starts start stopped stops happen happens lasted
ring rings ringing call calls calling called phone number numbers nhs straight away right now
immediately urgent quickly twice back gone around through even
alright fine okay normal better best settled eased easing quiet
four five six seven eight nine ten eleven twelve thirteen fourteen fifteen twenty thirty forty
fifty sixty hundred thousand minutes hours weeks days months years month week year day
""".split())


# A sign said as a feeling of their own, or a thing come back: what a person says about a symptom
# they are having, as opposed to the word turning up in ordinary talk.
A_FEELING_OF = ("feels like {w}", "feel like {w}", "feeling like {w}", "felt like {w}",
                "feels {w}", "feel {w}", "feeling {w}", "like {w}", "{w} now", "{w} again",
                "{w} too", "{w} back", "{w} is back", "{w} coming on", "in my {w}", "on my {w}",
                "my {w}", "some {w}")


def _the_threshold_words(sentence):
    """The signs the answer names in its own if-clause, without the ending that varies."""
    low = " ".join(str(sentence or "").lower().split())
    words = set()
    for match in THRESHOLD_CLAUSE.finditer(low):
        if match.group(0).lstrip().lower().startswith("even if"):
            continue  # "get a medical check today even if you feel alright" is no threshold
        for word in re.findall(r"[a-z']+", match.group(1)):
            if len(word) < 4 or word in THRESHOLD_NOT_A_SIGN:
                continue
            words.add(_flag_stem(word))
    return words


def _it_is_the_answer_word(line, word):
    """True when the line says the answer's own sign as a feeling of theirs."""
    low = " ".join(str(line or "").lower().split())
    if not re.search(r"\b" + re.escape(word) + r"\w*\b", low):
        return False
    for shape in A_FEELING_OF:
        said = r"(?:the\s+|a\s+|some\s+)?" + re.escape(word) + r"\w*"
        if re.search(r"\b" + shape.replace("{w}", said) + r"\b", low):
            return True
    return False


def _flag_stem(word):
    """The word without the ending that makes "sweaty" and "sweating" the same flag."""
    for tail in ("ing", "ness", "ed", "y", "s"):
        if word.endswith(tail) and len(word) - len(tail) >= 4:
            word = word[:-len(tail)]
    return word


def _an_answer_above(turns):
    """Did the bot answer above this line, so that the no is how that answer went?

    An ack is four or five words ("Got it — the landlord said no" is longer, but the bot's own
    answers run to full sentences); an answer is a thing somebody can go and try.
    """
    bot = str((turns[-1].get("bot") if turns else "") or "")
    return len(bot.split()) >= 8


# A thing the line brings in right after the shared word: "blood out of a shirt" is a laundry
# question, not another line about the nose that bled, and so is "blood stains out of cotton"
# with no article at all. The preposition is what makes it a new object, so the article is
# optional: a plain ask ("can i pop the blister") has no preposition in front of the noun.
CLAUSE_END = re.compile(r"[;,.?!]|\b(?:and|but|then|so|because|while|which|who)\b")
