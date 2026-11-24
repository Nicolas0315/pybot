"""Part 5 of 6 of the module, split out of `repeat`.

Everything here is re-exported from `repeat`, so callers import it from there as before.
"""
import re

from ..understanding import understand
from . import facts, topics
from .repeat_part_01 import (
    HEDGE, LOOK_BACK, ASK, ASK_VERB, CONDITION_CLAUSE, FILLER, NOT_A_MOVE, SELF, TIME,
)
from .repeat_part_02 import (
    _already_repeated, _sentences,
)
from .repeat_part_03 import (
    FIGURE_ASKS, FIGURE_SAYING, FIGURE_WORDS, NOT_ALONE, PART_ASKS, PART_STAND_INS, STILL_ASKS,
    A_MOVE_WORDS, METHOD_ASKS, NOT_A_METHOD, WHETHER_ASKS, A_QUALITY, A_QUESTION, ASK_FRAME,
    FIGURE_NOUNS, A_FIGURE, PAY_FAMILY,
)
from .repeat_part_04 import (
    _about_the_same_thing, _the_chat_is_still_on, _the_keys_of,
)


same_subject = _about_the_same_thing


def the_figure_asked(text, memory):
    """The sentence of the last answer that carries the figure this line asks for, or None.

    "how long should i leave it", a turn after the bot said "Wipe it, shake out the port, and
    leave it in a warm dry place for 24 hours", got the search hedge: the answers machinery goes
    looking for an entry keyed on this line, and the line names no thing, so nothing is found -
    while the figure asked for is in the answer already on the screen. The figure is handed back
    in the answer's own sentence, so the person gets "leave it in a warm dry place for 24 hours"
    rather than a shrug.

    Narrow on purpose: the line must ask for one kind of figure and name nothing else, the answer
    must be a knowledge answer from a turn or two ago, and the sentence handed back must carry a
    figure of the kind asked for.
    """
    if not isinstance(memory, dict):
        return None
    clean = " ".join(str(text or "").lower().split())
    if not clean:
        return None
    asked = None
    for _name, ask, figure in FIGURE_ASKS:
        if ask.search(clean):
            asked = ask, figure
            break
    if asked is None:
        return None
    ask, figure = asked
    rest = [word for word in re.findall(r"[a-z']+", ask.sub(" ", clean))
            if word not in FIGURE_WORDS and word not in FIGURE_SAYING]
    if rest:
        return None  # the line names a thing of its own: that thing has an answer
    seen_a_card = False
    for back, turn in enumerate(reversed((memory.get("turns") or [])[-LOOK_BACK:]), 1):
        if not isinstance(turn, dict):
            break
        # A knowledge answer, a turn or two back. Short answers count here, unlike in
        # `_recent_answers`: "40 to 45 minutes." is a whole answer, and it is exactly the sentence
        # a later "how long should i rest it" wants rather than the paragraph behind it.
        if turn.get("module") != "answers":
            continue
        said = str(turn.get("bot") or "").strip()
        if not said or HEDGE.search(said) or said.rstrip().endswith("?"):
            continue
        if len(said) < 50 and not figure.search(said):
            continue  # a stock line is not an answer with a figure in it
        if back > 1 and not _about_the_same_thing(str(turn.get("user") or ""), said, memory):
            continue  # the chat has moved on: an older answer is not what this line leans on
        for part in _sentences(said):
            part = part.strip().rstrip(" ;")
            if part and figure.search(part) and not _already_repeated(part, memory):
                return part[:1].upper() + part[1:] + ("" if part[-1:] in ".!?" else ".")
    return None


def answers_nothing(reply):
    """True when the reply is one of the bot's own ways of not answering this turn.

    The composer has a handful of lines for a question it cannot take on: the search hedge, the
    note that there is nothing to stand behind, "two goes at the same thing is enough", "that is
    in the answer above", "tell me what you've got so far". All of them are the right reply when
    there is nothing else to say, and all of them are the wrong reply when the card on the screen
    already says part of the answer, which is what `the_part_asked` and `what_it_knows` are for.
    """
    if not reply:
        return False
    # Taken inside the call: this module is read by the composer as it loads, and binding these
    # at the top would leave them built from a half-loaded `fallback`.
    from ..compose import fallback
    from ..compose import verdict
    if fallback._is_a_hedge(reply) or fallback._nothing_to_stand_behind(reply):
        return True
    return fallback._in_a_pool(reply, (fallback.SAME_AGAIN,
                                       fallback.HELP_ALREADY,
                                       fallback.TIPS_LINES,
                                       fallback.TIPS_THING,
                                       fallback.TRIED_NO_CHANGE_ELSEWHERE,
                                       verdict.ALL_OF_IT_LINES))


def the_advice_was_to_get_seen(memory):
    """True when the bot has already told them to be seen today - 111, A&E, a GP, a vet.

    A follow-up after that is about everything else, and the card's own sentence put in front of
    the advice again reads as the bot talking over what it just said.
    """
    from . import stuck
    return stuck.the_advice_was_to_get_seen(memory)


def the_part_asked(text, memory):
    """The sentence of a card in hand that answers this follow-up, or None.

    "is the food still ok", two turns after the bot's answer about a freezer door, got "A quick
    search online will get you a solid answer": the answers machinery looks for an entry keyed on
    this line, finds none, and the card that would answer it is already on the screen. So the
    sentence of that card which says what is safe, or which step has to be done, or the step it
    says to take first, is handed back in the card's own words.

    Narrow on purpose. The ask has to be one of the three kinds above, the answer has to be a
    knowledge card from the last few turns, and the card has to be about the thing the line names
    or about the thing the chat is still on. Nothing is invented: the sentence is the bot's own.
    """
    if not isinstance(memory, dict):
        return None
    clean = " ".join(str(text or "").lower().split())
    if not clean:
        return None
    kind = None
    for name, ask, mark in PART_ASKS:
        if ask.search(clean):
            kind = name, mark
            break
    if kind is None:
        return None
    name, mark = kind
    if name == "move" and not _whether_to(clean):
        # "should i ask her", "should i text him": a card says what to do and why, never yes or
        # no, so there is no sentence of it that answers a decision about a person. The step-shaped
        # asks that a card can settle ("do i need to prick them") name a move on the thing, and
        # only those are left to the sentence below; the rest are the composer's to answer.
        return None
    asked_words = topics.words(clean)
    if name == "move":
        # The verb the ask is made with names what is being asked about, not a subject of its
        # own: "do i need to prick them" asks about pricking, and a card that never says the
        # word has nothing to hand back. So the verb right after the ask is taken out of the
        # subject, and a thing named later in the line ("do i need to move the fridge") is not.
        for _name2, ask2, _mark2 in PART_ASKS:
            if _mark2 is None:
                continue
            found = ask2.search(clean)
            if not found:
                continue
            asked_words = [word for word in asked_words
                           if word not in re.findall(r"[a-z']+", found.group(0))]
            break
    if name == "move":
        _step = _whether_to(clean)
        if not [word for word in _step.split()[2:] if word not in PART_STAND_INS][1:]:
            # The step names no thing - "should i rest", "should i wait" - so it is about the
            # person and not about anything the card is on. Nothing of the card can answer it.
            return None
    asked = [word for word in asked_words
             if len(word) > 2 and not word.isdigit() and word not in topics.STOPWORDS
             and word not in ASK and word not in ASK_VERB and word not in TIME
             and word not in FILLER and word not in SELF and word not in PART_STAND_INS]
    # A yes/no about still being able to do something with the thing ("can i still eat the ones
    # that look alright", "can i still wear these") is settled by the card only when the card says
    # that doing. The blight card says how to slow blight and never says whether the fruit is safe
    # to eat; its opening was handed back as though it answered, and the person was left with a
    # paragraph about binning leaves. The doing is in `ASK_VERB`, so it is not in `asked` at all,
    # and with nothing else named the guard below had nothing to test.
    doing = ""
    still = STILL_ASKS.match(clean)
    if still:
        doing_words = re.findall(r"[a-z']+", still.group("rest"))
        if doing_words:
            doing = _a_stem(doing_words[0])
    seen_a_card = False
    for back, turn in enumerate(reversed((memory.get("turns") or [])[-LOOK_BACK:]), 1):
        if not isinstance(turn, dict):
            break
        # A knowledge card, and only a knowledge card: the composer's own lines have no answer
        # behind them to hand back.
        if turn.get("module") != "answers":
            continue
        said = str(turn.get("bot") or "").strip()
        if not said or HEDGE.search(said) or said.rstrip().endswith("?"):
            continue
        if len(said) < 50:
            continue  # a stock line, not a card
        keys = _the_keys_of(said, memory)
        on_the_card = bool(asked) and bool(set(asked) & keys)
        if not asked and seen_a_card:
            # The line names nothing at all ("where do i start"), so the card it leans on is the
            # newest one in the chat: a card further back has been answered over since.
            continue
        seen_a_card = True
        if asked and back > 1 and not on_the_card and not _about_the_same_thing(
                str(turn.get("user") or ""), said, memory):
            continue  # the chat has moved on: an older card is not what this line leans on
        if not asked and back > 1 and not _the_chat_is_still_on(said, memory):
            # A line that names nothing of its own ("and should i put it in writing") leans on the
            # newest card only. An older one is a different subject: the card about a tired child
            # was handed back for a question about shift changes, with the NHS site on the end of
            # it. The card has to share a word with the last few lines to be the one in hand.
            continue
        for index, part in enumerate(_sentences(said)):
            part = part.strip().rstrip(" ;")
            if len(part.split()) < 4:
                continue
            if part.lower().endswith("?"):
                continue
            if NOT_ALONE.match(part):
                continue  # a sentence that only follows the one before it is not a reply
            if name == "start":
                if index > 0:
                    break  # the start is the card's opening, and nothing further down it
            else:
                if not mark.search(part):
                    continue
                if CONDITION_CLAUSE.match(part) or NOT_A_MOVE.match(part):
                    continue
            if asked and not on_the_card and not any(word in part.lower() for word in asked):
                continue
            if doing and doing not in {_a_stem(word) for word in re.findall(r"[a-z']+",
                                                                            part.lower())}:
                continue  # the card never says this doing, so nothing of it answers the line
            if _already_repeated(part, memory):
                continue
            return part[:1].upper() + part[1:] + ("" if part[-1:] in ".!?" else ".")
    return None


# The rest of an answer lives somewhere, and the subject of the chat says where. Not a fact about
# the world - a place to look, one per subject the understanding engine already names
# (`bot/understanding/topics.py`), so nothing here goes stale.
WHERE_TO_LOOK = {
    "cooking": "the packet or a cookery site",
    "food-and-drink": "the label or a cookery site",
    "health": "the NHS site or a pharmacist",
    "fitness": "a coach or the NHS site",
    "sleep": "the NHS site",
    "money": "the official page, gov.uk or your bank",
    "work": "your contract or ACAS",
    "school-and-study": "the school's own notice or the exam board",
    "science": "a textbook or the Royal Society site",
    "history": "a museum's own page",
    "geography-and-travel": "a map app or the operator's own site",
    "technology": "the maker's support page",
    "home-and-diy": "the maker's instructions or a qualified trade",
    "garden-and-plants": "the RHS site or the plant's own label",
    "pets": "your vet",
    "family-and-parenting": "your GP or the NHS site",
    "friends-and-relationships": "the person themselves",
    "shopping": "the shop's own listing",
    "cars": "the handbook or a garage",
    "entertainment": "a listings site",
    "sport": "the club or the governing body's site",
    "language-and-writing": "a dictionary",
    "feelings": "a friend who knows you, or your GP",
    "maths-and-numbers": "a calculator",
    "nature-and-weather": "the Met Office site",
}


WHERE_TO_LOOK_DEFAULT = "a search"


# The place to settle it is read off the card the person is looking at, not off the topic of the
# line that asked for it. "formula left out for 3 hours" is read as a sport topic - Formula 1 -
# so a question about reheating a baby's bottle was told to look at "the club or the governing
# body's site". The card's own words say what the chat is about, and they are on the screen, so
# they pick the place; the topic is only the fallback.
WHERE_TO_LOOK_WORDS = (
    (("baby", "formula", "bottle", "breastfeed", "nappy", "weaning"), "the NHS site or a health visitor"),
    (("boiler", "radiator", "thermostat", "bleed"), "the maker's instructions or a gas engineer"),
    (("extractor", "socket", "fuse", "appliance", "plug", "wiring"), "the maker's manual or an electrician"),
    (("oven", "roast", "bake", "boil", "fry", "pan", "saucepan", "dough", "oven's"), "the packet or a cookery site"),
    (("dose", "tablet", "antibiotic", "paracetamol", "ibuprofen", "prescription"), "a pharmacist or the leaflet in the box"),
    (("battery", "charger", "router", "app", "software", "phone"), "the maker's support page"),
    (("mortgage", "overdraft", "pension", "tax", "benefit", "allowance"), "the official page, gov.uk or your bank"),
    (("lease", "landlord", "deposit", "tenancy"), "your contract or the council's housing team"),
    # A card about a passport or a visa is a card about a rule only one office can state: "can i
    # still fly in may" was told "a map app or the operator's own site", which is where the topic of
    # the change is, not where the answer is.
    (("passport", "visa", "embassy", "renewal"), "the passport office's own site"),
    (("weed", "soil", "compost", "prune", "seedling", "plant"), "the RHS site or the plant's own label"),
    (("puppy", "kitten", "vet", "dog", "cat"), "your vet"),
    (("stitch", "sew", "hem", "zip", "fabric", "garment"), "the care label or a tailor"),
)


def _whether_to(clean):
    """The step the line asks about, as "whether to <it>", or "".

    The step has to start with a verb of doing a thing to something, and be short: "should i take
    her tonight" and "what should i bring" are not asks about a step in hand, and "whether to
    bring" is not a sentence. Only ever a yes/no about a move on the thing the answer was about.
    """
    for shape in WHETHER_ASKS:
        found = shape.search(clean)
        if not found:
            continue
        rest = " ".join(found.group("rest").split()).strip(" .,")
        words_of_it = rest.split()
        if not words_of_it or len(words_of_it) > 5:
            continue
        if words_of_it[0] not in A_MOVE_WORDS:
            continue
        return "whether to " + rest
    for shape in METHOD_ASKS:
        found = shape.search(clean)
        if not found:
            continue
        rest = " ".join(found.group("rest").split()).strip(" .,")
        words_of_it = rest.split()
        if not words_of_it or len(words_of_it) > 5:
            continue
        if words_of_it[0] in NOT_A_METHOD:
            continue
        return "whether to use " + rest
    # A yes/no about still being able to use the thing on the screen: "can i still eat the ones
    # that look alright", "can i still wear them". The thing is a stand-in ("the ones", "them") or
    # the chat's own subject, so there is no move-word to test; the card is asked whether it covers
    # the doing, and where it does not, the reply says so in the person's own words and names the
    # one place that settles it. The clause is kept grammatical ("whether i can still eat ..."),
    # because it is said back to them in the gap line.
    found = STILL_ASKS.match(clean)
    if found:
        return ("whether " + found.group("who").lower() + " " + found.group("aux").lower()
                + " still " + " ".join(found.group("rest").split()).strip(" .,"))
    return ""


def _a_stem(word):
    """"preheat" and "preheating" are one word said in two forms.

    The gap this reads is a step the card never covered, and a card that says "about five minutes
    preheating" has covered "and how long should i preheat it". Comparing the words as typed said
    it had not, and the reply then told the person the packet knows - about the number the card in
    front of them had just given.
    """
    word = str(word or "").lower()
    for suffix in ("ing", "ings", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            word = word[: -len(suffix)]
            break
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]
    return word


def _where_the_rest_is(said, memory, turn, ask=""):
    """The one place that settles what an answer in hand does not cover, read off the answer.

    Where the rest of it lives is read off the card's own line, not the ask: "should i keep
    driving" carries no subject, and the subject of the chat is what the answer was about. The
    card's own words, and the entries it came from, go in too: a timings card for a roast says
    "20 minutes per 500g ... a 2kg bird" and names no oven at all, while the entry behind it is
    keyed on one. Without them the place came from the topic of the turn that asked for the
    figure - "how long does it take anyway" reads as maths, and the reply offered "a calculator"
    for whether to cover a chicken with foil.
    """
    card_words = " ".join(re.findall(r"[a-z']+", str(said or "").lower()))
    card_words = (card_words + " " + " ".join(sorted(_the_keys_of(said, memory)))).strip()
    for needles, place in WHERE_TO_LOOK_WORDS:
        if any(re.search(r"\b" + word + r"\b", card_words) for word in needles):
            return place
    # The topic of the turn that fetched the card is the last resort, and only counts when the ask
    # is on that same topic. A card about a dog that pulls on the lead was fetched by a turn read
    # as maths ("how long until it works"), and "does a harness work better" was told that a
    # calculator would know more than the bot - the card itself said a front-clip harness helps.
    # Where the ask is on another topic, no place is named and the line is left to whatever else
    # can answer it: a place read off the wrong turn is worse than none.
    try:
        card_read = understand(str((turn or {}).get("user") or "")) or {}
        card_topic = str(card_read.get("topic") or "")
    except Exception:
        card_topic = ""
    if ask:
        # A card fetched by a turn read as another subject says nothing about where the rest of
        # this line lives. "how long until it works" in a chat about a dog that pulls on the lead
        # reads as maths, and "does a harness work better" was told that "a calculator" would know
        # more than the bot. Where the two topics part, the honest place is the general one.
        try:
            ask_topic = str((understand(ask) or {}).get("topic") or "")
        except Exception:
            ask_topic = ""
        if card_topic and ask_topic and card_topic != ask_topic:
            return WHERE_TO_LOOK_DEFAULT
    return WHERE_TO_LOOK.get(card_topic, WHERE_TO_LOOK_DEFAULT)


def what_it_knows(text, memory):
    """What the answer in hand does know, when the follow-up asks something it never covered.

    "how do i soft boil an egg" is answered with the timings, and the follow-up "do i need to
    prick them" met "That's beyond what I know well, sorry. Searching for it will turn up better
    sources" - as if the chat had not already answered half of it. The card is still on the
    screen and the part of it that matters here is still true, so it comes back in the card's own
    words, and the bit the card does not cover is named as a gap with the one place that knows it.
    A search on its own is not a reply; this gives what the bot can, and only then points on.

    Narrow on purpose. The card has to be a knowledge card from the last few turns, the ask has
    to be a yes/no about a step, and the step has to be one the card never mentions - where the
    card does name it, the answer is already there and `the_part_asked` hands it back instead.
    """
    if not isinstance(memory, dict):
        return None
    clean = " ".join(str(text or "").lower().split()).strip(" ?!.")
    if not clean:
        return None
    whether = _whether_to(clean)
    if not whether:
        return None
    # The step, not the frame of the ask: "whether to preheat it" is about preheating, and
    # counting the word "whether" as part of it made every step read as one the card lacked.
    asked = [word for word in topics.words(" ".join(whether.split()[2:]))
             if len(word) > 2 and not word.isdigit() and word not in topics.STOPWORDS
             and word not in ASK and word not in ASK_VERB and word not in TIME
             and word not in FILLER and word not in SELF and word not in PART_STAND_INS]
    if not asked:
        return None
    seen_a_card = False
    gap = ""
    for back, turn in enumerate(reversed((memory.get("turns") or [])[-LOOK_BACK:]), 1):
        if not isinstance(turn, dict) or turn.get("module") != "answers":
            continue
        said = str(turn.get("bot") or "").strip()
        if not said or HEDGE.search(said) or said.rstrip().endswith("?"):
            continue
        if len(said) < 50:
            continue  # a stock line, not a card
        if set(asked) & _the_keys_of(said, memory):
            continue  # the card does answer this: not a gap
        on_the_card = {_a_stem(word) for word in re.findall(r"[a-z']+", said.lower())}
        named = [word for word in asked if _a_stem(word) in on_the_card]
        missing = [word for word in asked
                   if _a_stem(word) not in on_the_card and word not in A_QUALITY]
        if named and not missing:
            # The card says the step, in one form of the word or another, so there is no gap to
            # name: the sentence of it that carries the step is the answer, and no place is
            # offered for a figure the bot has just given.
            for sentence in _sentences(said):
                sentence = sentence.strip().rstrip(" ;")
                if len(sentence.split()) < 4 or sentence.lower().endswith("?"):
                    continue
                if {_a_stem(word) for word in asked} & {
                        _a_stem(word) for word in re.findall(r"[a-z']+", sentence.lower())}:
                    # The card says the step and then goes on about something else ("... with the
                    # door shut, with the shelf 10cm or so below the element"): the part that
                    # answers the ask is up to the colon, and handing the whole sentence back is
                    # the answer they have already read, which the composer sets aside.
                    head = sentence.split(":")[0] if ":" in sentence else sentence
                    if len(head.split()) < 4:
                        head = sentence
                    return head[:1].upper() + head[1:] + ("" if head[-1:] in ".!?\"" else ".")
            continue  # nothing of the card says it in a sentence of its own
        # The newest card comes first, and an older one is reached only when the newer cards do
        # not name the thing the line asks about: the answer to "how long until it works" is a cut
        # of the dog-lead card, and the sentence about the front-clip harness was in the card it
        # was cut from. The older card has to be on the subject of the chat as well.
        seen_a_card = True
        first_card = back <= 1 or not any(
            isinstance(t, dict) and t.get("module") == "answers"
            for t in (memory.get("turns") or [])[-back + 1:])
        if back > 1 and not _the_chat_is_still_on(said, memory):
            # The line itself often names nothing ("and should i put it in writing"), so the loose
            # test the rest of this module makes hands back a card the chat has nothing to do
            # with - the tired-child card, six turns into a chat about shift changes, with the NHS
            # site on the end of it. The card has to share a word with the last few lines.
            continue  # the chat has moved on
        if (back > 1 and not first_card
                and not _about_the_same_thing(str(turn.get("user") or ""), said, memory)):
            # An older card is only reached for when the chat is still on it as well: this is the
            # test every other reader of a card makes, and the newest card - the one on the
            # screen - does not have to pass it, because the subject of a fragment ("can i still
            # eat the ones that look alright") is not the subject of the card.
            continue  # the chat has moved on
        # The step has to be a step on the thing the card is about: said with a pronoun ("should
        # i cover it", "can i just use it on them") or with a word of the card's own ("should i
        # cover the chicken"). A bare move with neither - "should i rest" after an answer about
        # digging a bed - is a new question about the person, and handing back "Take one bed about
        # a metre by two" as the answer to a sore back is worse than saying it cannot call it.
        move_words = [w for w in whether.split()[2:] if w not in PART_STAND_INS]
        on_the_card = {_a_stem(word) for word in re.findall(r"[a-z']+", said.lower())}
        if not move_words[1:]:
            # "should i rest", "should i wait": the move has no object, so it is about the person
            # rather than about anything on the card. An answer about digging a bed settles nothing
            # about a sore back, and handing its step back as the reply is worse than saying so.
            continue
        part = ""
        lead = ""
        for sentence in _sentences(said):
            sentence = sentence.strip().rstrip(" ;")
            if len(sentence.split()) < 4 or sentence.lower().endswith("?"):
                # A card often opens with the whole answer in three words - "Bin it." on a bottle
                # left out too long - and dropping it because it is short leaves "a made-up bottle
                # is two hours old" as the reply to "can i just reheat it". So the short opening is
                # kept and put in front of the sentence that carries the detail.
                if not lead and sentence and not sentence.lower().endswith("?") \
                        and len(sentence.split()) >= 2 and not NOT_ALONE.match(sentence):
                    lead = sentence
                continue
            if _already_repeated(sentence, memory):
                continue
            if {_a_stem(word) for word in asked} & {
                    _a_stem(word) for word in re.findall(r"[a-z']+", sentence.lower())}:
                # The card's own sentence says the step, so there is no gap to name: "should i
                # keep driving" is answered by "Grinding means the pads are down to metal: stop
                # driving and get them changed", and telling them the rest is elsewhere would
                # talk over the answer already in hand.
                return None
            part = sentence
            break
        look = _where_the_rest_is(said, memory, turn, ask=clean)
        if not look:
            return None
        if not part:
            # The card has been read out in full already - every sentence of it is one the person
            # has just had - so there is no part of it left to hand back, and saying one again
            # would only repeat the answer. What is left of a fallback is still worth saying: the
            # step the card never covered, named, and the one place that covers it, read off the
            # card's own words. "will beer traps do anything" came to the search hedge because
            # "beer" reads as food and drink on its own; the card in hand is about slugs, and the
            # place that settles it is the garden one.
            # Held, not returned: a card further back may name the thing this one does not (the
            # answer to "how long until it works" is a cut of the dog-lead card, without the
            # sentence about the front-clip harness that the whole card has), and a card that
            # names it answers the line properly. The gap is only said once every card in reach
            # has been asked.
            gap = ("On " + whether + ", " + look + " will know more than I can - nothing I have"
                   " covers it.")
            continue
        head = part[:1].upper() + part[1:] + ("" if part[-1:] in ".!?\"" else ".")
        if lead:
            head = lead[:1].upper() + lead[1:] + " " + head
        if len(clean) % 2:
            return head + " On " + whether + ", " + look + " will know more than I can."
        return head + " That is what I can tell you; on " + whether + ", " + look + " will say."
    return gap or None


# How many turns back the thing and its figure can be. Short on purpose: a long chat has other
# numbers by now, and the person means the one from the stretch they are still in.
GAVE_LOOK_BACK = 8


# "were away for 3 nights", "were going on friday", "were off to spain": people type "we're" as
# "were", and a line that opens with it is a statement about themselves, not a question. Read as a
# question the line gave no figure at all, so "how many nights is that" after it found nothing to
# give back and the chat punted. Only the words that really ask keep it a question: "were you
# there", "were there any problems", "were we meant to book". "were there friday to monday" is a
# statement too and is left unread, because "were there" alone is a question far more often.
A_WERE_ASKS = re.compile(
    r"\A\s*were\s+(?:i|you|we|they|he|she|it|there|any|all|none|not|this|these|those|either)\b",
    re.I)


def the_plain_line(line):
    """The line with "were" read as "we are" where that is what it says, and otherwise as it is."""
    text = str(line or "")
    if A_WERE_ASKS.match(text) or not re.match(r"\A\s*were\s+\w", text, re.I):
        return text
    return re.sub(r"\A(\s*)were\b", r"\1we are", text, count=1, flags=re.I)


# What stands in front of a length that makes it a rate rather than a length: "250 a month",
# "twice a week", "£20 a day", "once a fortnight", "each month".
A_RATE_OF_TIME = re.compile(
    r"(?:\d|\u00a3|\$|\u20ac)\s*$"
    r"|\b(?:once|twice|thrice|times|per|each|every|a|an)\s*$", re.I)


# What after a length makes it a time of day rather than a length had: "20 minutes before food",
# "an hour after the dose", "two weeks after the crash". "ago" is not here: "i started two weeks
# ago" is a length they have had.
A_SCHEDULED_AFTER = re.compile(r"\s*(?:before|after|past|prior\s+to)\b", re.I)


# A length they have in front of them, not a slot in the day: "i have 3 weeks till the first paper",
# "we've got two weeks until the move". The words in front of the figure say it is theirs to count.
A_HAS_THE_LENGTH = re.compile(r"\b(?:have|has|had|got|there's|there\s+are|there\s+is)\b", re.I)


# An ask that wants a name, a judgement or a conversion is not asking for a figure back, and a
# figure from the chat would answer a question they did not ask: "how much coffee is too much"
# after "i drink two coffees a day" is about coffee, not about their two, and "so 320 miles is how
# many km" is a sum. Both reached the figure reader because they share a word with the line that
# holds the number.
NOT_A_FIGURE_ASK = re.compile(
    r"\b(?:called|named|call|spell|spelt|means?|stand\s+for)\b"   # what are my dogs called
    r"|\btoo\s+(?:much|many)\b"                                    # how much coffee is too much
    r"|\benough\b|\bsafe\b|\bhealthy\b|\brecommend\b"
    r"|\b(?:is|are|was|were)\s+how\s+(?:many|much)\b"             # 320 miles is how many km
    r"|\bhow\s+do\s+i\b"
    # A total is added up, not remembered: "i spent 300 on food" and "i spent 50 on petrol", then
    # "how much have i spent" wants 350, and handing back the first figure is worse than nothing.
    # Unless the line says it is remembering: "how much did i say the flights were" is not a sum,
    # and its answer is the 300 they gave.
    r"|\bhow\s+much\s+(?:have|has|did)\s+(?:i|we|they)\b"
    r"(?!\s+(?:say|said|tell|told|mention|mentioned))"
    r"|\b(?:in total|altogether|all together|so far)\b",
    re.I)


# A plan of their own in the ask ("how long before the move should i start") still asks for the
# time they were given. It only makes an ask a question about the world when the figure wanted is
# a count or an amount: "how much coffee can i drink" after "i drink two coffees a day" is about
# coffee, and the two in the chat is not the answer.
A_PLAN_ASK = re.compile(r"\b(?:should|can|could|shall)\s+(?:i|we)\b", re.I)


# A question about the plan itself is not a question about a figure: "so whats the plan for
# cornwall then" wants the plan, and handing back the one duration in it - "You said a week." -
# answers something else. A plan is the composer's to give and no number stands in for it.
A_THE_PLAN_ASK = re.compile(
    r"\bwhat(?:'s|s|\s+is|\s+are|\s+was|\s+were)?\s+(?:the|a|our|my)\s+plan\b"
    r"|\bwhat\s+(?:do|does|should)\s+(?:i|we)\s+do\s+(?:first|next)\b", re.I)


# A duration asked back with nothing named at all: "and how long did i say its been", "how long
# have i had it now". `the_figure_asked` answers this shape out of the bot's last answer; this is
# the person's own line, which is where the two weeks came from in the first place. Only these
# wordings, because "how long do i leave it now" is the same shape and is a question about the
# world that the answer on the screen carries.
# The thing a recall ask names after the cue that asks for the figure back: "how many people did i
# say *the hall* holds" asks about the hall, and the 30 people in the chat are not the answer to
# it. The words after the cue are the rest of the person's own sentence, and only a noun phrase
# with a determiner in front of it names anything: "were coming" and "i do" continue the ask and
# name nothing.
A_THING_NAMED_AFTER_THE_CUE = re.compile(
    r"\b(?:did|do|does|was|were|am|are)\s+(?:i|we)\s+"
    r"(?:say|said|tell|told|think|want|wanted|need|needed|do|does|did)?\s*"
    r"(?:the|a|an|my|our|his|her|their|your)\s+[a-z]", re.I)


# The same for an amount: a line that names nothing and asks a figure back is answered from the
# one figure of that kind in the chat. "we need 30k for the deposit" then "how much do we need
# again" named no key the store keeps, so the figure reader answered nothing and the turn went to
# a card about deposits that said no figure at all.
A_BARE_AMOUNT_ASK = re.compile(
    # The pronoun has to end the ask: "and how much is that a year" asks for the amount turned into
    # a year, and handing the 300 back as "You said 300 now." answers a sum with the number in it.
    r"\bhow\s+much\s+(?:was|is|were|are)\s+(?:it|that|this|they|those|these)"
    r"\s*(?:again|now|then)?\s*[.?!]*\s*\Z"
    # The pronoun's verb has to be the whole ask: "how much do we need again" wants the 30k back,
    # while "how much do i need for a deposit" asks what a deposit takes and is a question about
    # the world - the 6000 they have put by is not the answer to it. A purpose or a subject after
    # the verb is what tells the two apart, so only a neutral tail may follow it.
    r"|\bhow\s+much\s+(?:did|do|does)\s+(?:i|we)\s+(?:say|need|want|have|owe|pay|spend|agree)"
    r"\s*(?:again|now|then|already|so\s+far|in\s+total|altogether|for\s+it)?\s*[.?!]*\s*\Z"
    r"|\bremind\s+me\s+how\s+much\b", re.I)


A_BARE_DURATION_ASK = re.compile(
    r"\bdid\s+i\s+(?:say|want|choose|pick)\b"
    r"|\bhow\s+long\s+(?:am|are|was|were)\s+(?:i|we)\s+"
    r"(?:going|away|out|there|staying|off)\b"
    r"|\bhow\s+long\s+have\s+i\s+had\b|\bhave\s+i\s+had\b"
    r"|\bhow\s+long\s+(?:has|have)\s+(?:it|that|this)\s+been\b"
    r"|\bhow\s+long\s+(?:was|is)\s+(?:it|that)\b", re.I)


# The same ask with the thing named instead of the pronoun: "how long has my back been like this
# now" says the back, so the bare shape above stood down and the entry for a back took the turn -
# three turns after the person had said "my lower back has been sore for about 3 weeks", the reply
# told them how to keep a back quiet instead of the three weeks. It is a construction and not a
# word list: how long + has/have + a phrase with a possessive in it + been + a tail that points
# back at the thing in hand. "how long has my chicken been in the fridge" is not one - its tail
# says where the chicken is, not that it is the same chicken the chat has been on.
A_HOW_LONG_ITS_BEEN = re.compile(
    r"\bhow\s+long\s+(?:has|have|had)\s+(?:[\w']+\s+){1,5}been\s+"
    r"(?:like\s+(?:this|that)|going\s+on|that\s+way|this\s+way|now|so\s+far)\b", re.I)


_OWNS_THE_THING = re.compile(r"\b(?:my|our|his|her|their|the)\b", re.I)


def how_long_its_been(text):
    """True when the line asks how long the person's own thing has been like this."""
    found = A_HOW_LONG_ITS_BEEN.search(" ".join(str(text or "").lower().split()))
    return bool(found and _OWNS_THE_THING.search(found.group(0)))


# A line that asks is not a line that gives one back: "and how much is that a year" carries "a
# year" inside the question, and a length a person gave about their own life is the other kind of
# line. The leading "and", "but", "sorry" and the like are stripped first, so a question that
# opens softly is still a question.
A_LINE_THAT_ASKS = re.compile(
    r"\A(?:\W*(?:and|but|so|ok|okay|also|then|well|now|hmm|oh|yeah|yes|right|actually|sorry|"
    r"plus|just)\b[\s,]*)*" + A_QUESTION.pattern, re.I)


# A line that takes a figure back: "no, 45", "actually three", "make it 900". Only a correction
# that carries a figure of the same kind changes what comes back - "no pork remember" takes back
# no number, and the eight in the dinner is still the answer to "and how many people". It has to
# open the line: "no, 45", "sorry, 3 cats", "my mistake, 800", "make it
# 900". Three words in, "i want to make it to 30 countries" is a plan and not a figure taken
# back, and it was read as one because it says "make it".
A_CORRECTION = re.compile(
    r"^[\s,.\-]*(?:(?:oh|ok|okay|and|but|so|well|sorry|no|nope|actually|wait|oops|correction|"
    r"my mistake|it'?s)\b[\s,;:.-]*){1,3}"
    r"|^[\s,.\-]*(?:make\s+(?:it|that)|i\s+mean|we\s+mean|scratch\s+that|i\s+meant|"
    r"we\s+meant)\b", re.I)


# A correction word at the end of the line is the same correction: "we have two cats" then "its 3
# actually" takes the two back the way "no, 3 cats" does. The shapes above all open with the word,
# so this line was never read as a correction and the ask "how many cats do i have" answered "You
# said two cats." over a store that held three. The head has to state nothing of its own - the
# same rule the memory readers use - or "my mum is 70 actually" would put its 70 in the budget.
A_MARKER_AT_THE_END = re.compile(r"\s+(?:actually|really|honestly)\s*[.!?]*\s*$", re.I)


def _a_line_that_corrects(line):
    """Whether a line takes a figure back, whether it opens with the word or ends with it."""
    said = str(line or "")
    if A_CORRECTION.search(said):
        return True
    found = A_MARKER_AT_THE_END.search(said)
    if found is None:
        return False
    head = said[:found.start()].strip()
    if not head or len(head.split()) > 8:
        return False
    return not facts.extract(head)


# A correction says a number even when the figure reader cannot read it: "actually there are three
# of them" takes the two back and gives no figure of its own, so nothing safely comes back.
A_NUMBER_WORD = re.compile(
    r"\b(?:\d[\d,]*(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|"
    r"forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)\b", re.I)


# The words after a counted figure that join it to the rest of the sentence: "500 for the trip" is
# five hundred and not "500 for", and "300 each" keeps its each.
JOINERS = frozenset("""a an the and or but so of to in on at for with from by as then that this
    is are was were it them us you""".split())


# The words that join a figure to the rest of the sentence: a preposition, a joiner, or the reason
# the figure was corrected or explained. None of them is the figure, so none is said back with it.
FIGURE_TAIL = JOINERS | frozenset("""because cos coz cuz cause since""".split())


# A line that adds to a counted thing: "actually one more is coming", "another ones coming",
# "plus one of my mates". The count said before it is no longer the count they have, the same way
# a loss makes it out of date - and a stale count handed back as "you said 8 people" is worse
# than the card that knows nothing.
A_ONE_MORE = re.compile(r"\b(?:more|extra|other|others|fewer|less)\b", re.I)


A_GAIN = re.compile(
    r"\b(?:one|two|three|four|\d+|another)\s+(?:more|extra|other)\b"
    r"|\banother\s+(?:one|guest|person|adult|kid|child|friend|mate|of)\b"
    r"|\bplus\s+(?:one|two|three|\d+)\b|\bone\s+of\s+(?:my|our)\b", re.I)


A_GROUP_WORD = re.compile(r"\b(?:us|we|them|they|people|guests?|party)\b", re.I)


# A line that takes one of a counted thing away: "one of them died last week", "we gave the cat
# away". The count in the chat is no longer the count they have, and the store reads these itself.
A_LOSS = re.compile(
    r"\b(?:died|passed away|put (?:him|her|it|them) down|gave\b[^.?!]{0,20}\baway"
    r"|rehomed|sold|stolen|went missing|ran away|eaten|no longer|not any ?more)\b"
    r"|\bone\s+of\s+(?:them|those|these|the)\b|\bgave\s+one\b|\bone\s+(?:away|off|back)\b",
    re.I)


# A list of ages: "aged 4 and 7", "aged four and seven", "4 and 7 years old". A line shaped like
# that is naming the members of a group one by one, and the size of the group is how many members
# there are - so the first number in the list is not the count. "i have kids aged 4 and 7" asked
# "how many kids do i have" was answered "You said 4 kids."
_A_AGE = r"(?:\d[\d,]*(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"


A_LIST_OF_AGES = re.compile(
    r"\b(?:aged?|ages)\s*" + _A_AGE + r"\b\s*(?:and|&|,)\s*" + _A_AGE + r"\b"
    r"|\b" + _A_AGE + r"\b\s*(?:and|&|,)\s*" + _A_AGE
    + r"\b\s*(?:years?|yrs?)(?:\s+old)?\b",
    re.I)


def _a_list_of_ages(line):
    """Whether the line lists ages, which names the members of a group rather than its size."""
    return bool(A_LIST_OF_AGES.search(str(line or "")))


def _something_gone(lines, at, words):
    """Whether a later line says one of the counted things is gone, so the count is out of date."""
    for later in lines[at + 1:]:
        if not later:
            continue
        if A_GAIN.search(later) and A_GROUP_WORD.search(later):
            # "one more is coming" / "another of my mates is coming too": the group grew, so the
            # count given before it is not the count they have.
            return True
        if not A_LOSS.search(later):
            continue
        said = topics.keywords(later)
        if any(_the_same_word(word, other) for word in words for other in said):
            return True
        if "one" in A_LOSS.search(later).group(0).lower():
            return True   # "one of them died", "we gave one away": a count that went down
    return False


# The ask's own word for the thing counted: "how many missed calls do i have" is calls. The
# figure regex takes the words after the number as far as it can, so "5 missed calls" comes back
# as "5 missed" and "i weigh 80 kilos" as "80 kilos": the ask puts the noun back.
COUNT_ASK = re.compile(r"\bhow\s+many\s+([a-z'&-]+(?:\s+[a-z'&-]+){0,3})", re.I)


# A period word names when a thing happens, not how many of a thing there are. "how many a week
# do we have" after "we get a takeaway three times a week" was answered "You said three week." -
# the count of weeks is nothing they gave, and the sentence reads as a mistake. Where the figure on
# their line is a rate, the ask is the rate said back, and `bot/memory/rates.py` has the words for
# it (`You get a takeaway three times a week.`), so this reader steps out of the way.
PERIOD_WORD = frozenset("""hour hours day days week weeks fortnight fortnights month months
    year years night nights morning mornings evening evenings weekend weekends christmas""".split())


A_RATE_IN_THE_FIGURE = re.compile(
    r"\b(?:once|twice|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+times?\b"
    r"|\bevery\s+(?:\w+\s+)?(?:hour|day|week|fortnight|month|year|morning|evening|night|weekend)\b",
    re.I)


# A figure written as a word and the same figure written as a digit, so "for eight" in an ask and
# "8 people" in a line are read as one number rather than two.
THE_SAME_NUMBER = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "fifteen": "15",
    "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60",
    "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000",
}


A_PLURAL_ONLY_NOUN = frozenset("""people children men women feet teeth""".split())


def _the_ask_gave_that_figure(number, clean):
    """Whether the ask itself names the figure the reading found.

    A number in the ask - "for 8", "how many for 10 people" - is the ask's own quantity, so it is
    not a figure the person gave earlier and saying it back claims a recall that did not happen.
    """
    number = str(number or "").strip().lower()
    if not number:
        return False
    first = number.split()[0]
    looked = {first, THE_SAME_NUMBER.get(first, first)}
    for other in A_NUMBER_WORD.findall(clean):
        if other == first or THE_SAME_NUMBER.get(other, other) in looked:
            return True
        if other[:1].isalpha() and first[:1].isalpha() and _the_same_word(first, other):
            return True
    return False


def _a_count_of_one_with_a_plural(number, noun):
    """Whether a count of one is about to be said with a noun in the plural: "one people"."""
    if str(number).strip().lower() not in ("1", "one", "a", "single"):
        return False
    word = (noun.split() or [""])[-1].lower()
    if not word:
        return False
    return word in A_PLURAL_ONLY_NOUN or word.endswith("s")


def _the_thing_counted(clean, said):
    """The ask's word for the thing counted, with the figure's own modifier when it has one."""
    match = COUNT_ASK.search(clean)
    if not match:
        return ""
    phrase = match.group(1).split()
    words = [word for word in phrase
             if word not in topics.STOPWORDS and word not in ASK_FRAME
             and word not in FIGURE_NOUNS]
    if not words:
        return ""
    tail = said.split()[-1].lower()
    # "two flat tyres" / "5 missed calls": the ask says the modifier in front of the noun, so the
    # whole pair is the thing, and "two tyres" would drop a word the person said.
    for one, other in zip(phrase, phrase[1:]):
        if other in words and _the_same_word(one, tail):
            return one + " " + other
    for word in words:
        if _the_same_word(word, tail):
            return word
    return words[-1]


def _figures_in(line):
    """The figures a line gives, as (kind, the words used, the number, whether it counted).

    A figure that belongs to somebody else is not one they gave: "my mum has three brothers" is
    the mother's count, and "how many brothers do i have" must not be answered with it. The
    subject of the clause is read by the store's own reader (`facts.subject`), so a relation, a
    pronoun or a name is somebody else everywhere at once.
    """
    text = str(line or "")
    if not text or "?" in text or A_QUESTION.match(text):
        return []
    out = []
    for match in A_FIGURE.finditer(text):
        if match.group("time") and A_RATE_OF_TIME.search(text[:match.start()]):
            # "im putting by 250 a month", "twice a week", "£20 a day": a rate, not a length. The
            # article form above reads the "a month" in it, and a later "how many months is that
            # again" - the sum the chat worked out - was answered "You said a month.".
            continue
        if (match.group("time") and A_SCHEDULED_AFTER.match(text[match.end():])
                and not A_HAS_THE_LENGTH.search(text[:match.start()])):
            # "i take the tablets 20 minutes before food" is when to take them, not a length they
            # have had: "how long have i had it now" answered "You said 20 minutes." But "i have 3
            # weeks till the first paper" is a length they have, and the count is theirs.
            continue
        said = " ".join(match.group(0).split()).rstrip(" ,.;:")
        if not said:
            continue
        if match.group("count") and A_ONE_MORE.match(" ".join(said.split()[1:])):
            # "actually one more is coming so theres 10 of us now": a count word with "more",
            # "extra" or "other" after it is how many were added, not how many there are. Read as
            # a count it answered "how many people is it for again" with "One people".
            continue
        try:
            whose, _who = facts.subject(text, match.start())
        except Exception:  # noqa: BLE001 - a reading that cannot run keeps the figure theirs
            whose = ""
        if whose == "other":
            continue
        counted = match.group("count") is not None
        kind = "time" if match.group("time") else "amount"
        if match.group("share"):
            # Said back whole and never as a count: "You said 10 per cent." A share is the figure
            # the person gave, and every way of writing one reads the same.
            digits = re.match(r"\s*([\d][\d,]*(?:\.\d+)?)", match.group(0))
            number = digits.group(1) if digits else said
            out.append((kind, number + " per cent", number, False))
            continue
        if counted and said.lower().endswith(" per"):
            # "3 per box" is three of them: "per" joins a count to what it is counted in, so it
            # comes off with the rest of the tail rather than being said back as part of it.
            said = said[:-4].rstrip(" ,.;:")
        # The words a figure is joined to the rest of the sentence by are not part of it: "500
        # for the trip" is five hundred, not "500 for", and a figure given with the reason it
        # changed - "actually i mean 75 because i lost some" - is 75, not "75 because". Both
        # shapes were handed back whole ("You said 75 because."), so the tail comes off every
        # figure and not only a count.
        words = said.split()
        while len(words) > 1 and words[-1].lower() in FIGURE_TAIL:
            words.pop()
        # The punctuation is the sentence's, not the figure's: "actually my brother cant come so
        # 5, and theres a dog" is read as the count "5, and", and the comma stayed on the number -
        # "You said 5,." and "5, - that's what you told me." both said it back with a comma that
        # belongs to the sentence. A comma is part of the number only when there are digits on
        # both sides of it ("£1,500"), so any other one ends the figure: "its 2, not 3" is 2.
        said = re.split(r"(?<!\d),|,(?!\d)", " ".join(words))[0]
        said = said.rstrip(" ,.;:")
        number = (said.split()[0] if counted else said).rstrip(" ,.;:")
        if not number:
            continue
        out.append((kind, said, number, counted))
    return out


# Money paid for a thing is not the thing. "we paid 2000 for the venue" gives a figure for what
# the venue cost, and "what did i say the venue was" asks what the venue *is* - the name of the
# place, which that line never gave. The figure was handed over anyway ("You said 2000."), so the
# person asking what the venue was got its price. An ask for the money carries its own word for
# it ("how much did i say the venue was", "what did i say i paid for the venue"), and then the
# figure is the answer.
_MONEY_PAID_FOR = re.compile(
    r"\b(?:paid|pay|pays|spent|spend|cost|costs|charged|gave|give|offered|quoted|put|set)\b"
    r"[^.?!]{0,25}?[\u00a3$\u20ac]?\s?\d[\d.,]*[^.?!]{0,25}?\b(?:for|on|towards)\b", re.I)


_AN_AMOUNT_WANTED = re.compile(
    r"\bhow\s+(?:much|many)\b|\bcost\b|\bcosts\b|\bprice\b|\bpaid\b|\bpay\b"
    r"|\bspent\b|\bspend\b|\bbudget\b|\bfee\b|\btotal\b|\bworth\b", re.I)


def _money_paid_for_a_thing(clean, line):
    """True when the line's figure is money spent on a thing, and the ask wants the thing itself."""
    if _AN_AMOUNT_WANTED.search(clean):
        return False
    return bool(_MONEY_PAID_FOR.search(line))


def _one_figure(found, kind):
    """The figure of the kind asked for, or () when the line holds none or holds two kinds."""
    if not found:
        return ()
    if kind:
        found = [one for one in found if one[0] == kind]
    elif len({one[0] for one in found}) > 1:
        return ()   # a length of time and an amount on one line: which one is not known
    return found[0] if found else ()


def _a_bare_count(figure):
    """Whether a figure is the number on its own, with nothing saying what it counts.

    The span line is written for a figure a person gave in their own words with its unit -
    "\u00a3250 a month - that's what you told me" - and with no unit in it the line reads as a
    template cut short. A count said back is just the count: "You said 5."
    """
    words = str(figure or "").split()
    return len(words) == 1 and bool(A_NUMBER_WORD.fullmatch(words[0]))


def _the_same_word(one, other):
    """Whether two words are the same thing said twice: "move" and "moving", "bed" and "bedrooms"."""
    first, second = topics.stem(one), topics.stem(other)
    if first == second:
        return True
    if topics.forms(first) & topics.forms(second):
        # The same verb with an ending on and off: "how much was i *putting* away" asks about the
        # line that said "i *put* 400 a month away", and "putting" and "put" share no prefix. The
        # short forms are the ones the prefix rule below cannot reach, so they are matched as a
        # family (topics.forms), which is how the rest of the store reads a word family.
        return True
    # A room counted by its name and by its rooms: "its a 3 bed", "how many bedrooms". The short
    # word is too short for the prefix rule below, and it is the shape people use for a house.
    for shorter, longer in ((first, second), (second, first)):
        if longer.endswith("room") and longer[:-4] == shorter:
            return True
    if first in PAY_FAMILY and second in PAY_FAMILY:
        # Pay said as a wage on one line and as being paid on another: the same money, so the ask
        # under either word is answered by the figure given under the other.
        return True
    return (len(first) >= 4 and len(second) >= 4
            and (first.startswith(second) or second.startswith(first)))


def _the_corrected(lines, at, kind, found):
    """The figure a later line takes back to, or the one it was given, or () when it is unsure.

    "my budget is 500" / "make it 900" / "what is my budget": the last figure they said for the
    thing is the one they mean. A correction with no figure in it ("no pork remember") takes
    nothing back, so the figure stands.
    """
    for later in lines[at + 1:]:
        if not later or not _a_line_that_corrects(later) or A_LINE_THAT_ASKS.search(later):
            continue    # "and how much is that a year" opens like a correction and asks a question
        got = _one_figure(_figures_in(later), kind)
        if got:
            found = got
        elif A_NUMBER_WORD.search(later) and kind != "time":
            # A number was taken back and the new one cannot be read: say nothing. A length is
            # the one kind where a bare number is not a length at all - "its a 3 bed with a
            # garden" opens like a correction and carries the 3 of the bedrooms, and reading it
            # as a new length took back the six weeks the person gave about the move.
            return ()
    return found


# A recall ask points back with the person's own words: "what did i tell you", "did i say".
A_TOLD_BACK = re.compile(
    r"\b(?:did\s+i\s+(?:say|tell|mention)|what\s+did\s+i\s+(?:say|tell)"
    r"|what\s+was\s+it\s+i\s+(?:said|told)|how\s+(?:long|many|much)\s+did\s+i\s+(?:say|tell))\b",
    re.I)


# Words that frame a recall ask and never name the thing a length is about. "sorry" and "going"
# get there from the apology shape, and both would otherwise count as the thing asked about.
NOT_A_THING_ASKED = frozenset((
    "sorry", "apologise", "apologize", "going", "told", "tell", "said", "say", "mention",
    "remember", "again", "asked", "ask"))


def _the_length_they_mean(clean, lines, spoken=()):
    """The length a recall ask points at, in the person's own words, or "".

    Two lengths in a chat is normally a question of which, so the thing the ask names decides:
    "how long did i tell you the headaches been going on" picks the line about the headache even
    when the person also said a root canal was a month ago. With nothing named to go on, the one
    length they gave anywhere is the answer, and a corrected one is read as corrected. Anything
    still unclear is left to the module that knows the thing, so this says "" rather than guess.

    `spoken` is what the bot itself said in the same window. A word of the ask that no line of
    theirs carries is not always a new thing: "sorry, how long did i tell you it has been sore"
    after "i hurt my shoulder about a week ago" was left unanswered because the person's line says
    "hurt" and the ask says "sore", a word only the replies had used. When every word the ask adds
    to the cue is a word the chat has already used, the ask is naming nothing new and the one length
    in the chat is the one they mean - while "how long did i say the shop was open" still names a
    thing the chat has never mentioned, and is still left alone.
    """
    wanted = [word for word in topics.keywords(clean)
              if word not in ASK_FRAME and word not in NOT_A_THING_ASKED]
    if wanted and spoken:
        theirs = [other for line in lines for other in topics.keywords(line)]
        heard = [other for line in spoken for other in topics.keywords(line)]
        new = [word for word in wanted
               if not any(_the_same_word(word, other) for other in theirs)]
        if new and all(any(_the_same_word(word, other) for other in heard) for word in new):
            wanted = []
    named, anywhere = [], []
    for back, line in enumerate(lines):
        if A_LINE_THAT_ASKS.search(line):
            continue    # a question the person asked is not a length the person gave
        figures = [one for one in _figures_in(line) if one[0] == "time"]
        if not figures:
            continue
        anywhere.append((back, figures))
        words = topics.keywords(line)
        if any(_the_same_word(word, other) for word in wanted for other in words):
            named.append((back, figures))
    # When the ask names something, only a line that names it counts: "how long did i say the shop
    # was open" is not answered with the length of the commute just because that is the only length
    # in the chat. With nothing named, the one length they gave anywhere is the answer.
    for pool in ((named,) if wanted else (named, anywhere)):
        if not pool:
            continue
        distinct = {one[1].lower() for _back, figures in pool for one in figures}
        if len(distinct) == 1:
            back, figures = pool[-1]
            # "my back has hurt for two weeks" / "actually its been three weeks" - the later line
            # is the one they mean, and it names neither the back nor anything else.
            later = _the_corrected(lines, back, "time", figures[-1])
            return (later or figures[-1])[1]
        if A_CORRECTION.search(lines[pool[-1][0]]):
            return pool[-1][1][-1][1]
    return ""
