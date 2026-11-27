"""Part 11 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import history, last_user
from ..understanding import understand
from . import (pick, prices, quantity)
from .postcode import a_postcode_lookup

from .fallback_data import (
    A_PLACE_I_DONT_KNOW,
    BABY_FOOD_NAMES,
    BLACKED_OUT_SIGHT,
    BUYING_WORDS,
    CHILD_AT_HOME,
    CRISIS_WORDS,
    DARK_THING,
    ENDINGS,
    FILLERS,
    GIFT_WORDS,
    GROWN_UP_WORDS,
    HELP_ALREADY,
    JUDGE_NOD_WORDS,
    LIVE_DELAY_WORDS,
    LIVE_HOURS_ASK,
    LIVE_YES_NO_OPEN,
    LIVE_INDOOR,
    LIVE_JOURNEY_ENDS,
    LIVE_KINDS,
    LIVE_NOT,
    LIVE_NOT_HOURS,
    LIVE_OPEN_CLOSE,
    LIVE_PAPER_WORDS,
    LIVE_ROAD_NAME,
    LIVE_ROADS_NOT,
    LIVE_ROAD_WORDS,
    LIVE_SETTING,
    LIVE_SKY,
    LIVE_SKY_OFF,
    LIVE_SKY_WHY,
    LIVE_SOON,
    LIVE_STRONG,
    LIVE_TAKE_ASK,
    LIVE_TRAVEL_WORDS,
    LIVE_WEAR,
    LIVE_WEATHER_WORDS,
    MEDS_WORDS,
    NETWORK_WORDS,
    NOT_A_FORM,
    NO_MORE_OF,
    OUTCOME_LINES,
    OWN_PERSON,
    OWN_PLACE,
    POINTING,
    QUESTION_WORDS,
    SAFETY_WORDS,
    SELF_EATING_WORDS,
    TIPS_CLAUSE,
    TIPS_LINES,
    TIPS_OWNER,
    TIPS_UNIT,
    TIPS_VERB,
    VIEW_LEAD_IN,
    WORD_FIXES,
    _OPENING_QUESTIONS,
)

from .fallback_part_01 import (
    _DEFINITION, _matchable, _has,
)
from .fallback_part_02 import (
    HOW_TO_TELL, METHOD_OPENING, NOT_A_METHOD, _A_PRODUCT, BLACKED_OUT_A_THING, BLACKOUT_PERSON,
    _the_line_before,
)
from .fallback_part_08 import (
    LIVE_WEATHER_DAY, MY_TIME_ASK, OWN_TIME_ASK, OWN_VERB_OPEN, RECORD_CHECK, RECORD_THINGS,
    _a_bare_wear_ask, _their_own_bill, _their_own_phrase, _their_own_points, _their_own_record,
    LATER_QUESTION,
)
from .fallback_part_09 import (
    NOT_A_PLACE, PLACE_EVALUATIVE, PLACE_OPENER, TRIP_NAMED, _names_a_venue, LIVE_ANY_ACCIDENT,
    LIVE_A_BARE_WINNING, LIVE_LISTING_ASK, LIVE_NEWS_LINES, LIVE_NOT_WORLDS, LIVE_SPORT,
    _a_road_named_with_traffic, _a_trip_is_on_the_table, _the_days_news, _the_sky_and_nothing_else,
    _their_own_count, _their_own_count_fell, _their_own_thing,
)
from .fallback_part_10 import (
    _asks_for_the_move, _flat_words, _hedged_recently, _names_a_new_thing, TIPS_ANY_IDEA, TIPS_LEAD,
    TIPS_REQUEST, TIPS_SUBJECT_FOR, TIPS_SUBJECT_TAIL, TIPS_WORD, ASK_SHAPES, INDIRECT,
)


def method_ask_pool(clean, memory=None):
    """The pool for a method asked for when nothing else could answer it, else None.

    "how do i practise", "how do i start running" and "where should i hang my washing" got the
    search hedge - "I'm not sure about that one, sorry - I'd rather not guess. A quick search
    online will get you a solid answer" - which is the one answer that helps nobody: the person is
    asking how to do a thing of their own, and there is nothing to look up about it. What a friend
    says is what they have tried so far, which is also the only way the bot can help.

    The hedge is right for a question about the world, so this only takes a line nothing else
    answered, and only one that asks for a method in the person's own voice: a line with no
    "how/where/when ... i" at its front is not read here at all.
    """
    if not METHOD_OPENING.match(str(clean or "")):
        return None
    if HOW_TO_TELL.search(clean) or NOT_A_METHOD.search(clean):
        return None
    if set(re.findall(r"[a-z']+", str(clean or ""))) & _A_PRODUCT:
        return None
    if _DEFINITION.search(clean):
        return None
    # After the bot's own answer, the thing the ask is about is that answer, so asking what they
    # have tried about it is a non sequitur: the way in points at the part that did not land.
    if _answered_already(memory if isinstance(memory, dict) else {}):
        return HELP_ALREADY
    return TIPS_LINES


def _a_place_asked_about(clean, memory):
    """The pool for "is it nice" about a trip the person has just named, or None.

    Read from the person's own last substantive turn, and only when the whole ask is a judgement
    of the place: a line with anything else in it - "is it far", "how do i get there from the
    station" - is a question the answers can take, and this pool must not stand in front of them.
    Where a card does answer the town it keeps the turn, because this is claimed only for the
    ask the nod pool was answering with a sign-off. A trip to a hospital, a wedding or a doctor's
    appointment is not a place (`NOT_A_PLACE`), and neither is an evening at the cinema or the
    theatre: `is it any good` there asks about the film or the play, which the card answers, so
    the card keeps the turn.

    A price verdict on a thing you buy to get there, or to eat and sleep once you are there, is
    not a verdict on the place: "we are thinking of going to cornwall in july" then "is the train
    expensive that far" was given "No first-hand knowledge of the place, sorry. Are you going for
    the sights, the food or the peace?" - a question about a trip's own pleasures, asked of a
    fare. The trip in the thread sets the scene; the thing in the line is what is asked about,
    and a fare is a price (bot/compose/the_rule_for_it.py, FARE_PRICE_RULE).
    """
    said = _matchable(clean).rstrip(" ?.!,")
    if not said or len(said.split()) > 6:
        return None
    if not PLACE_EVALUATIVE.search(said):
        return None
    from .the_rule_for_it import A_FARE_OR_A_TICKET, PRICE_VERDICT  # the pools load later
    if A_FARE_OR_A_TICKET.search(said) and PRICE_VERDICT.search(said):
        # The fare, the flight, the hotel: a thing with a price of its own, asked about as a
        # price. The trip the thread named is only where it goes.
        return None
    if not (PLACE_OPENER.match(said) or "?" in str(clean or "")):
        return None
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(turns[-3:]):
        mentioned = _matchable(turn.get("user"))
        if not mentioned or not [word for word in mentioned.split()
                                 if word not in JUDGE_NOD_WORDS]:
            continue  # a nod in between: the trip named before it is still on the table
        if NOT_A_PLACE.search(mentioned):
            return None  # a going, not a place: the card that answers the visit keeps its turn
        return list(A_PLACE_I_DONT_KNOW) if TRIP_NAMED.search(mentioned) else None
    return None


def venue_hours(text, memory=None):
    """True when the line asks when a named place opens, closes or is open.

    The composer's own reading, published for the arbiter, so that which lines are a question
    about a venue's hours is decided beside the pools that answer them. A place has to be named
    and open or close has to be in the line, and the composer's own pool has to be the hours
    one: "what time do hospitals let visitors in" is the visiting-hours answer's (no open or
    close in it), and "how do i open a bank account" reaches a different pool.
    """
    clean = str(text or "").strip().lower()
    if not _names_a_venue(clean) or not _has(clean, LIVE_OPEN_CLOSE):
        return False
    for kind, _phrases, options in LIVE_KINDS:
        if kind == "hours":
            return _live(clean, True, memory) == options
    return False


def _live(clean, asking, memory=None):
    """The pool of honest replies for live information, or None. A line that does not read as a
    question still asks for it when it names the thing ("train times to Bristol tomorrow")."""
    # A fact belonging to one place - a car park, dogs, a takeaway, a pool - is not live
    # information, but it is not in the bot either, and the search hedge is the worst line for
    # it. It has its own reader (`bot/compose/place_facts.py`), checked before all of this.
    from . import place_facts
    place = place_facts.the_line(clean)
    if place:
        return place
    if _has(clean, LIVE_NOT):
        return None
    # A question whose answer does not change with the day is not live information, whatever
    # word in it matched a live kind: "what's the tallest building in the world" and "the biggest
    # city in the world" both reached the news note through "the world", which is a settled
    # question answered as though it were today's news. The reading says which kind it is
    # (`understood["over_time"]`, see bot/understanding/kinds.py), and only a `False` stands this
    # down - `None` keeps every line exactly as it was, and `True` is what the rest of this
    # function is for.
    understood = (memory or {}).get("understood") if isinstance(memory, dict) else None
    if isinstance(understood, dict) and understood.get("over_time") is False:
        return None
    # A fact that belongs to the person's postcode is not live information and does not need a
    # question mark ("my poll card hasnt come"). It has its own narrow reading, so it is checked
    # before the asking gate.
    lookup = a_postcode_lookup(clean)
    if lookup:
        return lookup
    # "the news" on its own is the ask with the words left out, not a report about the day: it was
    # met with the nod ("Thanks for telling me") as though the person had told the bot something.
    if clean.strip(" ?!.") in ("news", "the news", "and the news"):
        return LIVE_NEWS_LINES
    # The same ask with a few more words in it: "anything in the news", "the headlines", "news
    # about the strike". It is the shape of the line that says so, and the asking gate below
    # would drop a line with no question mark in it.
    from . import news_ask
    if news_ask.reads_as_an_ask_for_the_news(clean):
        return LIVE_NEWS_LINES
    if (not asking and not _has(clean, LIVE_STRONG)
            and not LIVE_ANY_ACCIDENT.search(clean)
            and not LIVE_A_BARE_WINNING.search(clean)
            and not _the_sky_and_nothing_else(clean)
            and not _a_road_named_with_traffic(clean)
            and not _their_own_count(clean)
            and not _their_own_count_fell(clean)):
        # "check my gift card balance", "check my order", "confirm my appointment": an ask with
        # the verb in front and no question mark, so the asking gate above would drop it and the
        # person got "Got it. Is there anything you'd like a hand with?" - the placeholder this
        # file exists to keep off their screen. The record pool answers it and nothing else here
        # can, so it is read here rather than left to the nod.
        if RECORD_CHECK.search(clean) and _their_own_phrase(clean, RECORD_THINGS):
            record = _their_own_record(clean, False)
            if record:
                return record
        return None
    # A price for something the person already has is on their own bill, so it is read before the
    # price kind, which otherwise sends them to a seller's site for a thing they have already
    # bought. Their own points balance is the same shape and the same wrong turn.
    mine = _their_own_bill(clean) or _their_own_points(clean)
    if mine:
        return mine
    for kind, phrases, options in LIVE_KINDS:
        if kind in ("site-stats", "site-stats-down"):
            # The counting words are common ones - "traffic", "visitors" - so the kind reads only
            # a line that names a thing of the person's own: their site, their shop, their
            # listing. "is there traffic near the shops" is a road question and keeps the roads
            # pool, and a line about their own numbers never reaches an app that cannot see them.
            if kind == "site-stats-down":
                if _their_own_count_fell(clean) and _their_own_thing(clean):
                    return options
                continue
            if _their_own_count(clean) and _their_own_thing(clean):
                return options
            continue
        if kind == "weather":
            # Something in the house ("the oven", "the room") makes it a setting, not a forecast.
            if _has(clean, LIVE_INDOOR) and not _has(clean, LIVE_WEATHER_WORDS):
                continue
            if (_has(clean, phrases) or LIVE_WEATHER_DAY.search(clean)
                    or (_has(clean, LIVE_SKY) and not _has(clean, LIVE_SKY_OFF)
                        and not LIVE_SKY_WHY.search(clean))
                    or (_has(clean, LIVE_WEAR)
                        and (_a_bare_wear_ask(clean) if _has(clean, LIVE_TAKE_ASK)
                             else _has(clean, LIVE_SOON))
                        and not _has(clean, LIVE_SETTING))):
                return options
            continue
        if kind == "news" and LIVE_A_BARE_WINNING.search(clean):
            continue  # "whos winning" is a score, and the reader at the end of this reads it as one
        if kind == "news" and LIVE_NOT_WORLDS.search(clean):
            continue  # their own news: the record reader answers it, not a news site
        if kind == "roads":
            if _has(clean, LIVE_ROADS_NOT):
                continue  # the road tax, a road trip, directions: not today's traffic
            if _has(clean, phrases) or (LIVE_ROAD_NAME.search(clean)
                                        and not _has(clean, LIVE_PAPER_WORDS)):
                return options
            if _has(clean, LIVE_ROAD_WORDS) and _has(clean, LIVE_DELAY_WORDS):
                return options  # "is the road to leeds closed for roadworks"
        if kind == "journey":
            # A journey line needs two ends. "how far is york from leeds" and "how long is the
            # drive to york" name one, so they get the route planner; "how far is the tennis
            # court" names only the thing, so it is the distance line instead.
            if _has(clean, phrases) and (_has(clean, LIVE_JOURNEY_ENDS)
                                         or _a_trip_is_on_the_table(memory)):
                return options
            continue
        if kind == "travel":
            if _has(clean, LIVE_ROADS_NOT):
                continue  # the road tax, a road trip, directions: not today's traffic
            if _has(clean, phrases) or (_has(clean, LIVE_TRAVEL_WORDS)
                                        and _has(clean, LIVE_DELAY_WORDS)):
                return options
            # "What time does my train leave" is live times about how they are travelling, and
            # its own subject keeps it out of the opening-hours pool above (OWN_TIME_ASK), so
            # the travel line is the one that answers it.
            if _has(clean, LIVE_TRAVEL_WORDS) and (OWN_TIME_ASK.search(clean)
                                                   or MY_TIME_ASK.search(clean)):
                return options
            continue
        if kind == "prices":
            # A rate in the line with a judgement on it ("its 45 a month, is that a lot") is a
            # question about that rate, and which reading answers it depends on one thing the line
            # itself says. A rate whose thing is *in* the line ("my mortgage is 900 a month, is
            # that normal") is judged by comparing that thing with the same thing elsewhere, which
            # is what the two readings below do, so the sum goes under them. A rate with no thing
            # in it names nothing to compare, and the sum it comes to over a year is the only
            # answer about what the person said, so it goes above them.
            rate = quantity.the_rate_they_asked_about(clean, memory)
            if rate and not quantity.the_thing_they_pay_for(clean):
                return (rate,)
            # A sum asked to be judged is not a live price: nothing is being looked up, and today's
            # figure is not what the person asked for ("is that a lot of money" after a quote).
            verdict = _a_price_wants_a_verdict(clean, memory)
            if verdict:
                return verdict
            # The ask in the many shapes people use for it, with the guards that keep it off a
            # dose, a portion, a rate to save at and a recipe (`bot/compose/prices.py`).
            before = str(last_user(memory) or "") if isinstance(memory, dict) else ""
            priced = prices.the_price_reply(clean, phrases, before.lower(), options)
            if priced:
                return priced
            if rate:
                return (rate,)
            continue
        if kind == "hours":
            if _has(clean, LIVE_NOT_HOURS):
                continue  # the sky's own times are the sky's entries' to answer
            # "when does the post office close" is the plainest way to ask this and the phrase
            # lists were written around "what time", so a named place beside open or close is
            # the same ask. It has to name the place: "when does the meeting start" and "when
            # does the flight land" are their own questions.
            if _names_a_venue(clean) and (LIVE_HOURS_ASK.search(clean)
                                           or LIVE_YES_NO_OPEN.search(clean)):
                return options
            if OWN_TIME_ASK.search(clean):
                if not (_has(clean, OWN_PLACE) or OWN_VERB_OPEN.search(clean)) or _has(clean, OWN_PERSON):
                    continue  # their own day, not a venue's hours
            # The bare phrase "what time does" is in the hours table because it is how people
            # open that question, and it took "what time does the match start" with it: a
            # kick-off is a listing, not a shop's hours.
            if _has(clean, LIVE_SPORT) and LIVE_LISTING_ASK.search(clean):
                continue
        if _has(clean, phrases):
            return options
    return _the_days_news(clean, asking) or _their_own_record(clean, asking)


def _blackout_words(clean, words, said):
    """True when the line describes a faint in words other than "blacked out".

    "everything went black and i hit the floor" and "my vision went black for a second" are the
    same thing "i blacked out" says, and they were getting a shrug, or worse, the washing card:
    a colour run reads "everything" and "went" as a load of laundry.
    """
    if _names(words, said, DARK_THING) or BLACKED_OUT_A_THING.search(clean):
        return False
    someone = bool(BLACKOUT_PERSON.search(clean))
    for shape, needs_person in BLACKED_OUT_SIGHT:
        if re.search(shape, clean):
            return someone or not needs_person
    return False


def _says_it_already(clean, words, memory):
    """True when this line only asks again what the reply just above it answered.

    A follow-up written in the person's own words ("my phone is full of photos" then "how do i
    free up space") is not a new question, and the knowledge entry reads it as the same one: what
    comes back is the opening sentence of the answer just given, word for word, so the second
    reply adds nothing at all. Plain "that's most of what I know on it - say which part is still
    unclear" is the honest reply to that, and it is the one the bot already has for a bare ask
    after an answer (HELP_ALREADY, below).

    Three things have to hold, and each of them is a way of not taking a turn that has an answer:

    * the turn just before was an answer (`_answered_already`) and not a shrug
      (`_hedged_recently`), so there is something for "it" to refer to;
    * the line is short - it has no subject of its own to ask about;
    * its content words are in that answer already: at least one of them, and half of them or
      more. A follow-up that brings a word the answer never used is a new question and keeps
      its turn.
    """
    if _asks_for_the_move(clean):
        # It asks for the move, not for the answer again, however many of its words the answer
        # above used: "my daughter is nervous about starting secondary school next week" then
        # "what can we do before the first day?" was told "that is everything I have on that one,
        # so I would only repeat myself" - about an answer that opens with what to do and carries
        # a second step after it. The step readers answer a move ask; this guard stands down.
        return False
    if not _answered_already(memory) or _hedged_recently(memory):
        return False
    if not words or len(words) > 10:
        return False
    said = set(word for word in _flat_words(_the_answer_above(memory)) if word not in POINTING)
    if not said:
        return False
    mine = [word for word in words if word not in POINTING and len(word) > 2]
    if not mine:
        return False
    # A word and its plural are the same word here: "a banging noise" and "what is causing the
    # noises" are asking about the same thing.
    missing = [word for word in mine if not (word in said or word.rstrip("s") in said
                                             or word + "s" in said)]
    here = len(mine) - len(missing)
    if not here or here * 2 < len(mine):
        return False
    # A word the answer never used is only a new question when it names a thing: "what was the
    # first thing in the box" brings "box", and "that is all I know on it" answers nothing about
    # a box. "what do i need to buy", "is 20 minutes enough" and "what do i actually say" bring a
    # verb, an adjective and an adverb, and the answer above already covers all three.
    return not any(_names_a_new_thing(word, clean) for word in missing)


def says_it_already(text, memory):
    """True when the composer's reply to this line is about the repeat, not a stock shrug.

    The arbiter asks this before the never-repeat rule: when every other module's proposal only
    says the last answer again, a line about the repeat is the only new thing on the table, and
    it is a question about the answer rather than a shrug. `is_said_it_already` then tells the
    arbiter which candidate that is, so the pools stay in one place, here.
    """
    understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = understand(text, memory)
    clean = understood.get("clean") or " ".join(str(text or "").lower().split())
    words = understood.get("words") or clean.split()
    try:
        return _says_it_already(clean, list(words), memory)
    except Exception:  # noqa: BLE001 - a reading that fails just offers no line
        return False


# "is she going to be ok" is a worry about somebody else's outcome, and no card in the knowledge
# base can answer it: nobody can say from here whether a person will recover. Main answered it
# with the search hedge - "I don't know enough to answer that honestly. A search should sort you
# out quickly" - four chats in a row ("my mum is in hospital", "my dad had a stroke", "my friend
# is having an operation tomorrow", "my wife is in hospital with pneumonia"), and a search cannot
# tell anybody whether their mother will be all right. The honest half is that no one can promise
# it, and the useful half is who does know: the staff looking after them, and what to ask while
# they are there.
#
# The line has to be the bare worry and nothing else, and about somebody other than the speaker -
# "am i going to be ok" is somebody's own fear and is left to the modules that answer for a person
# in trouble.
THE_OUTCOME_ASK = re.compile(
    r"^(?:so |and |but |ok |okay )?(?:is|are|will|do you think|does the doctor think)\b"
    r"(?=[^?]{0,44}?(?:\b(?:going to be|be) (?:ok|okay|alright|all right|fine)\b"
    r"|\b(?:make it|pull through|come through|survive|recover)\b))", re.I)


# The worry is answered about somebody the talk has already said is ill or in hospital: a card
# about a sick relative, a stay, an operation, a stroke, the ward. Without one of these the line
# is a guess about something else ("will my car be ok") and another module's answer stands.
WHO_IS_ILL = re.compile(
    r"\b(?:in hospital|in the hospital|on the ward|got admitted|been admitted|is admitted|"
    r"in icu|intensive care|stroke unit|a&e|having an operation|having surgery|"
    r"in for an operation|waiting for a bed|coming out of hospital|coming home from hospital|"
    r"had a stroke|chemo|chemotherapy|on a ventilator|in a coma|diagnosed with|"
    r"the operation|the surgery|under the knife|their scan|the scan|"
    r"pneumonia|sepsis|heart attack|collapsed)\b", re.I)


def an_outcome_asked_about_someone(text, memory):
    """The line behind "is she going to be ok", answered honestly instead of hedged.

    Only when the bare worry is the whole line and the talk has already said somebody is ill or
    in hospital, and never inside a crisis or an emergency the bot has just answered: there the
    person needs the reply they were given, not a paragraph about the ward.
    """
    if not isinstance(memory, dict):
        return None
    clean = " ".join(str(text or "").lower().split())
    if not clean or len(re.findall(r"[a-z']+", clean)) > 9:
        return None
    if not THE_OUTCOME_ASK.match(clean):
        return None
    if re.search(r"\b(?:i|me|my|we|us|our)\b", clean):
        return None      # somebody's own prognosis is not this reading's line
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)][-3:]
    if not turns:
        return None
    last = str(turns[-1].get("bot") or "")
    if last and (any(word in last.lower() for word in CRISIS_WORDS)
                 or any(word in last.lower() for word in SAFETY_WORDS)):
        return None      # an answer that named 999 or a crisis line stands
    said = " ".join([str(turn.get("user") or "") for turn in turns] + [last])
    if not WHO_IS_ILL.search(said):
        return None
    return pick(OUTCOME_LINES, memory, clean)


# The front of an answer is not always the view. A reply that opens by naming the feeling back
# ("I'm so sorry.", "Loneliness is rough.") is company, and a reply that opens with a lead-in
# ("The things that work: ...") names what follows rather than the thing itself. Both were quoted
# as the bot's own position once the view reader landed: "i had a miscarriage" / "honest view?"
# got "My view has not changed: I'm so sorry.", "im so lonely" / "honest view?" got "...:
# loneliness is rough.", and "i cant sleep" / "honest view?" got "...: the things that work."
VIEW_MIRROR = re.compile(
    r"^(?:i(?:'m| am) (?:so |really |very |truly )?sorry\b|so sorry\b|sorry\b|that sounds\b"
    r"|that(?:'s| is) (?:rough|hard|tough|awful|a hard one|a lot|a real loss|a loss)\b"
    r"|ouch\b|ugh\b|hope\b|[a-z]{3,20}(?: [a-z]{2,20}){0,3} is (?:rough|hard|tough|awful)\b)")


# The front of an answer can also be the case it is for rather than the claim itself: "If you want
# something easy and good tonight: Groundhog Day for comedy, Knives Out for a whodunnit" is a
# recommendation to two people, not a remark about wanting something easy. Quoted as the view it
# left the promise hanging in mid-air - "My view has not changed: if you want something easy and
# good tonight." - which is the half of the sentence the person did not ask about, and says
# nothing (answers' watch, budget and weather cards all open this way). A condition that opens the
# line scopes what follows, so the claim is what follows. Only the openers that cannot start a
# claim are here: "For most people the fix is the same" is a claim about most people.
VIEW_A_CASE = re.compile(
    r"^(?:if |unless |depending on|when you|when it|once you|for £|for under |for about "
    r"|for around |for between |for a budget|for \d)")


def _the_view_of(said):
    """The first part of the answer that says something, cut at a colon, or None.

    The front of an answer can be company rather than a claim (see `VIEW_MIRROR`), and it can be
    a lead-in that names what follows: "The things that work: same wake-up time every day" is
    about the wake-up time, not about the things that work. Returns the claim and whether an
    opener was skipped, because the line built from it opens differently in that case.
    """
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", said.strip()) if part.strip()]
    mirrored = False
    for part in parts:
        head, colon, tail = part.partition(":")
        if colon and tail.strip():
            # The claim is the part before the colon, and the lead-in rule swaps them round when
            # the front only names what follows ("The things that work: same wake-up time").
            words = [w.strip(",.").lower() for w in head.split()]
            # A short head names the form of what follows rather than the thing itself: "Quick:
            # tuna pasta in 15, a frittata in 20" is about the pasta and the frittata, and the
            # head alone ("Quick") is not a claim at all. Read as the head it fell through to the
            # next sentence and quoted the bot's own request back ("Same as I said: tell me what
            # is in the fridge and I will pick properly"), which answers nothing.
            if (len(words) < 7 and any(word in VIEW_LEAD_IN for word in words)) \
                    or len(words) <= 3 or VIEW_A_CASE.match(head.strip().lower()):
                head, tail = tail, head
            part = head
        part = part.strip()
        if VIEW_MIRROR.match(part.lower()):
            mirrored = True
            continue
        claim = _a_said_claim(part)
        if claim:
            return claim, mirrored
        mirrored = True
    return None, mirrored


# A sentence that asks the person for something rather than saying anything: "Tell me what is in
# the fridge", "Let me know how it goes", "Any chance you could send a photo". A question in the
# answer can be the view ("What would have to be true for the answer to be yes?"), so this is
# tested only on a sentence that is not already read as a question.
ASKS_BACK = re.compile(
    r"^(?:tell me|let me know|send me|show me|give me|any chance|could you|can you|would you|"
    r"have you got|do you have|what have you|what about you)\b")


def _a_said_claim(first):
    """One sentence read as a claim to stand behind, or None when it says nothing."""
    if not first or first.endswith(":"):
        return None
    if first.endswith("?"):
        # The bot's own question, put again: "What would have to be true for the answer to be
        # yes?" is the view when that question was the answer, and it is still the right one.
        return first if len(first.split()) >= 4 else None
    if ASKS_BACK.match(first.lower()):
        # The bot asking the person for something is not a claim to stand behind: "Tell me what is
        # in the fridge and I will pick properly" is a request, and quoting it as the view
        # ("Same as I said: tell me what is in the fridge") leaves the turn where it started.
        return None
    words = first.split()
    if len(words) > 30:
        # Long answers open with a sentence and then qualify it; the view is the part before the
        # first comma past twenty words, and never a cut through the middle of a clause.
        cut = 20
        for index in range(20, min(len(words), 44)):
            if words[index].endswith(","):
                # The comma is on the last word of the clause, so the word stays: cutting at
                # `index` alone dropped it and the line ended mid-phrase ("...on a single rate the
                # hour makes no difference at." for the dishwasher answer).
                cut = index + 1
                break
        else:
            cut = 30
        first = " ".join(words[:cut]).rstrip(",") + "."
    if len(first.split()) < 3:
        return None
    # The sentence may end at a semicolon ("... more in heat or after exercise; tea, coffee,
    # milk and food all count"), and the line built from it puts a full stop on the end, so
    # the trailing mark goes rather than sitting in front of it: "exercise;." read as a typo.
    return first.rstrip(" .;,:") + "."


# A line asking for more of the answer just given, in the three shapes people write it: "anything
# else" / "what else works" / "what about the schools". "what about you" is not one of them.
MORE_ON_THIS = re.compile(
    r"\b(?:anything|something) (?:else|more)\b|\bwhat else\b"
    r"|\bwhat else (?:can|could|might|would|will|should|do|does|works?|helps?|matters?)\b"
    r"|\bany (?:other|more) (?:way|ways|idea|ideas|option|options|thing|things|tips?)\b"
    r"|\bis there anything (?:else|more|i can do)\b"
    r"|\bcan i do anything about (?:it|that|this)\b"
    r"|\bwhat about (?:the|my|our|his|her|their|those|these|it|that)\b")


# "what about my dad", "what about the schools": the thing named after "what about" is what the
# ask is about. It is only the answer just given when the conversation has already named it.
# "my mum is in hospital" then "what about my dad" is a different person, and "that's most of what
# I know on it" would be a claim about a subject the bot never touched (@plain-orange's read).
WHAT_ABOUT = re.compile(r"\bwhat about\s+(?:the|my|our|his|her|their|those|these)\s+(.+)$")


PERSON_NAMED = re.compile(
    r"^(?:mum|mom|mam|mother|dad|father|parent|parents|sister|brother|son|daughter|gran|"
    r"grandma|grandad|granny|nana|nan|husband|wife|partner|boyfriend|girlfriend|friend|"
    r"friends|baby|boy|girl|kids?|children|child|family|aunt|uncle|cousin|niece|nephew|"
    r"neighbour|neighbor|boss|colleague|carer|vet)\b")


def asks_for_more(text, memory):
    """True when the line asks for more of the answer just given, about the same thing.

    "anything else" and "what else works" are always about the answer. A "what about <thing>"
    ask names its own subject, so it is only the same subject when the chat has already named it,
    and a person named there is a different subject however close the relation.
    """
    said = str(text or "").strip().lower()
    if not MORE_ON_THIS.search(said):
        return False
    tail = WHAT_ABOUT.search(said)
    if not tail:
        return True
    named = tail.group(1)
    if PERSON_NAMED.match(named):
        return False
    return _named_recently(named, memory)


def _named_recently(named, memory, look_back=3):
    """True when the words of the named subject are in the last few turns, either side."""
    from ..memory.topics import keywords

    wanted = set(keywords(named))
    if not wanted:
        return True
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-look_back:]
    said = " ".join(str(t.get(key) or "") for t in turns for key in ("user", "bot"))
    return bool(wanted & set(keywords(said)))


def _answered_recently(memory):
    """True when the bot answered on the turn just before this one, from any module.

    Wider than `_answered_already`, which names the knowledge base because "what have you tried
    so far" only makes no sense after a fact answer. A request for more is about whatever was
    just said, so small talk counts too ("im thinking of moving to leeds" / "what about the
    schools"). The composer's own replies do not: after a nod or a condolence there is no
    answer to have more of, and "that's most of what I know on it" would claim knowledge the
    bot never offered.

    The module name alone cannot answer it: the chat module records a greeting and a topic
    turn alike as `chat`, so "hi" then "anything else" looked like a topic and got "that's most
    of what I know on it". What was said is the signal that can be trusted, so a line the
    memory's own reading calls not-a-subject (a hello, a thank you, a question about the chat)
    leaves nothing to have more of.

    Nor is a line that offered nothing an answer to have more of, whatever module said it: the
    last line has to have told the person something. A question back is the commonest way of
    saying nothing ("im thinking of moving to leeds" was answered "Worth planning rather than
    rushing into: what would have to go right for you?", and "what about the schools" then got
    "that's most of what I know on it", about schools the bot never mentioned), and a warm
    reaction is the other ("im feeling low" / "anything else"). "Asking for more of nothing" is
    worse than the honest hedge, so those lines leave nothing to have more of.

    A one-line acknowledgement is the exception, and it is the reason the reading walks back:
    "Fair enough." is the bot taking a nod or a refusal, not a reply about something new, so it
    does not wipe the answer from the chat. "recommend a film" / "no thanks at all" / "anything
    else" is still asking about the films, and the honest end line is the reply to it. Read off
    the last line alone, that turn got the pool's stock "Thanks for telling me - I'm here if you
    want to dig into any of that", which fits any message and answers none.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    index = len(turns) - 1
    while index > 0 and _only_takes_the_answer(str(turns[index].get("bot") or "")):
        index -= 1
    last = turns[index]
    if str(last.get("module") or "") in NO_MORE_OF:
        return False
    if not _told_them_something(str(last.get("bot") or "")):
        return False
    return not history.not_a_subject(str(last.get("user") or ""))


# The bot's own one-line acknowledgement: "Fair enough.", "Got it.", "Nice one.", "Alright then -
# good luck with it." It has to be short and carry no question, because a line that asks something
# back ("Fair enough. What have you enjoyed lately?") is the bot taking the subject further.
ACK_ONLY = re.compile(
    r"^(?:fair enough|fair|got it|got that|noted|understood|right|righto|right then|ok|okay|"
    r"alright|all right|sure|fine|nice one|sounds good|no bother|no worries|no problem|"
    r"hope it works out|lovely|good|great|grand|of course|certainly)\b[^?]{0,40}$", re.I)


def _only_takes_the_answer(said):
    """True when the bot's line only acknowledged what it was told, saying nothing of its own."""
    text = " ".join(str(said or "").split())
    if not text or len(text.split()) > 8:
        return False
    return ACK_ONLY.match(text) is not None


# The ways this bot says "I heard you" back: a nod, a condolence, a cheer. They are the reply
# to the line, not facts with anything behind them, so "anything else" after one is asking for
# more of nothing.
REACTED_ONLY = re.compile(
    r"^(?:sorry to hear|sorry\.|that sounds|that'?s (?:great|good|lovely|brilliant|rough|tough|"
    r"awful|a pain|a shame|a nuisance|rotten|understandable)|good on you|nice one|nice -|well "
    r"done|love that|fair enough|got it|makes sense|noted:|thanks for telling|i'?m listening|"
    r"i hear you|that'?s a lot)", re.I)


def _told_them_something(said):
    """True when the bot's last line said something, rather than asking back or only reacting.

    Read off the line itself, because the turn records only the module that said it and the
    chat module says a nod, a question and a fact alike.
    """
    text = said.strip()
    if not text or text.endswith("?"):
        return False
    return REACTED_ONLY.match(text) is None


def _the_answer_above(memory):
    """The bot's last real answer, as "the reply above" for a bare ask or a repeat.

    An acknowledgement is not a turn of its own: "my son is 4 and wont sleep" / "he shares with
    his sister" / "any tips" put "Got it - your son shares with his sister" between the ask and
    the answer, and the ask was then answered "what have you tried so far" about the answer the
    bot had just given in full. The line that comes after a note is about the answer under it,
    not about the note: "im going to portugal in july" / "no wait, august" / "whats it like in
    august" was told "that is everything I have on that one" because the note named August, and
    nothing had been said about August at all.
    """
    from .verdict import takes_a_fact_back
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    while turns and takes_a_fact_back(turns[-1].get("bot")):
        turns.pop()
    if not turns:
        return ""
    return str(turns[-1].get("bot") or "")


def _answered_already(memory):
    """True when the bot answered on the turn just before this one.

    Only the turn straight before counts. A bare ask follows the answer it is about, and
    "that's most of what I know on it" is only honest about that answer: an answer two turns
    back belongs to a different question by then ("my landlord wont let me have a cat" / "i
    really want one though" / "is there any way round it").
    """
    from .verdict import takes_a_fact_back
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    while turns and takes_a_fact_back(turns[-1].get("bot")):
        turns.pop()
    return bool(turns) and str(turns[-1].get("module") or "") == "answers"


TIPS_SPOKEN = (
    (re.compile(r"(?<![a-z0-9])4(?![a-z0-9])"), "for"),
    (re.compile(r"(?<![a-z0-9])2(?![a-z0-9])"), "to"),
    (re.compile(r"(?<![a-z0-9])u(?![a-z0-9])"), "you"),
    (re.compile(r"(?<![a-z0-9])ur(?![a-z0-9])"), "your"),
    (re.compile(r"(?<![a-z0-9])ne(?![a-z0-9])"), "any"),
    (re.compile(r"(?<![a-z0-9])pls(?![a-z0-9])"), "please"),
)


# The words that make a digit a number rather than a stand-in for "to" / "for".
TIPS_NUMBER_TAIL = re.compile(r"\s*(?:%s)\b" % "|".join(sorted(TIPS_UNIT)))


def _tips_spoken(text):
    """The line with its chat-speak read as words, leaving a number that counts something alone."""
    words = text.split()
    for i, word in enumerate(words):
        tail = words[i + 1] if i + 1 < len(words) else ""
        if word.isdigit() and TIPS_NUMBER_TAIL.match(tail):
            continue
        for pattern, said in TIPS_SPOKEN:
            word = pattern.sub(said, word)
        words[i] = word
    return " ".join(words)


def _tips_subject(clean):
    """The thing a plea for tips is about, said back, or None when the line names no thing."""
    text = _tips_spoken(" ".join(str(clean or "").lower().split()))
    # "give me a quick dinner idea" is a request for a recommendation, not a plea for tips on a
    # subject: only "any ideas" asks the way "any tips" does.
    if not TIPS_WORD.search(text) and not TIPS_ANY_IDEA.search(text):
        return None
    found = TIPS_SUBJECT_FOR.search(" " + text)
    subject = found.group("subject") if found else TIPS_SUBJECT_TAIL.sub("", " " + text + " ")
    subject = re.sub(r"[,.!?;:].*$", "", subject.strip(" ,.!?;:"))
    subject = TIPS_LEAD.sub("", " ".join(subject.split()))
    # "i need a new bath" is a subject; "i need some advice" is not one at all.
    subject = re.sub(r"^(?:i|we)\s+(?:really\s+)?(?:need|want|would\s+like|am\s+looking\s+for)\s+",
                     "", subject)
    subject = TIPS_REQUEST.sub("", TIPS_LEAD.sub("", subject))
    subject = TIPS_LEAD.sub("", subject)
    if not subject or subject.startswith("to ") or subject in ("it", "that", "this", "some", "anything", "something",
                                  "a", "an", "the", "advice", "tips", "help"):
        return None
    kept = [word for word in subject.split() if word not in FILLERS]
    if not kept or len(kept) > 6 or len(" ".join(kept)) > 40:
        return None
    if set(kept) & TIPS_CLAUSE or kept[0] in TIPS_VERB:
        return None
    return " ".join(TIPS_OWNER.get(word, word) for word in kept)


_ASKS_DEFINITION = re.compile(r"^\s*what(?:'s|s| is| are| was| does| do)\b|\bdifference between\b"
                              r"|\bwhat does .* (?:do|mean)\b|\bmeaning of\b")


# A line that asks where a thing is is asking for a place, not for a person to ring. With the
# reading that stopped "nappy" being "snappy", "where is the nappy", "where is my nappy bag"
# and "where did i put the nappy cream" all fell into the health visitor's hand-off - an answer
# to a symptom question, for a line about a bag. The hand-off stays wherever the line names
# something wrong (an ill thing, a leak, a smell), because "where is the rash" and "where is
# the leak" are that question with a place in it.
_ASKS_WHERE = re.compile(r"\bwhere(?:'s|s| is| are| was| were| did| do| does| can i| shall i)\b")


# Arithmetic has no advisor either: "how do I work out my hourly rate from my salary" is a sum.
# "i cant do the 10am gp appt on monday" is about the diary, so no health advisor either way.
_SCHEDULING = re.compile(r"\b(appt|appointment|appointments|cancel|reschedule|rearrange|rebook|"
                         r"double booked|move it|change it)\b")


_ASKS_ARITHMETIC = re.compile(r"\b(work out|calculate|convert|how much is|how many|percent|"
                              r"percentage|hourly rate)\b")


# "How do I fix a leak under the sink" wants to do it, so naming a plumber answers nothing.
# "i got a quote for 1,500, does that sound right" wants a way to check a price, not an expert.
# The price has to be in the line. "we split the rent 60 40, is that fair" is a question
# between two people, and a boiler quote is not the reply it wants.
QUOTE_ASKS = re.compile(r"\b(quote|quoted|estimate|price|priced|cost|bill|invoice|fee|charge)\b"
                        r".*\b(sound right|sounds right|too much|too high|too dear|steep|fair|"
                        r"reasonable|about right|normal)\b")


_ASKS_DIY = re.compile(r"\b(how do i|how can i|how to)\s+(fix|mend|repair|replace|install|fit|"
                       r"unblock|bleed|reset|clean|change)\b|\bmyself\b|\bmy own\b")


# A price asked to be judged, with nothing in the line that settles it. "is 120 pounds too much to
# spend", "is 250 too much" and "does that sound about right" (after "they want 40 quid") all got
# the search hedge, which is the one reply that cannot help: no search answers "is 120 a lot" until
# you know what the 120 buys, and the line does not say. QUOTE_ASKS just above reads the same
# request when the price has a word of its own in the line ("the plumber quoted 900 to fix it, is
# that fair"). This is the shape with no way in, and the reply gives the check that decides any
# price - one other price for the same thing, or for the same job from someone else - because that
# is true of every sum and needs nothing else from here. Nothing invents a price or a range: the
# only figure said back is the one the person wrote.
PRICE_VERDICT = re.compile(
    r"\b(?:too\s+(?:much|expensive|dear|pricey|pricy)|expensive|pricey|pricy|steep|overpriced|"
    r"dear|over\s+the\s+odds|rip[- ]?off|ripped\s+off|robbed|reasonable|fair|about\s+right|"
    r"sound\s+right|sounds\s+right|worth\s+it|good\s+(?:deal|price)|a\s+lot|that\s+much|"
    r"ok|okay|daylight\s+robbery)\b")


# A sum has to be in the line or on the turn before it: "the one i like is 250 pounds" / "is that a
# lot", "the fitter wants 900" / "does that sound about right", "the quote was 1200" / "seems like a
# lot?". The turn before is the only place it is read from, and only a figure that is money there.
# Without a sum these words are a judgement of something else - "is fibre worth it", "is the
# expensive oil worth it", "it isnt worth it" - and the check below answers a question nobody asked.
# The sum as the person wrote it. A currency mark, a number with its unit, a figure in words. Only
# what is in the line, so nothing is guessed; "250 pounds" is said back as "250 pounds".
MONEY_IN_A_LINE = re.compile(
    r"(?:[\u00a3$\u20ac]\s?\d[\d,]*(?:\.\d+)?)"
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:pounds?|quid|pence|euros?|dollars?|bucks|grand|k)\b"
    r"|\b(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
    r"fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|"
    r"seventy|eighty|ninety|hundred|thousand)\s+(?:pounds?|quid|euros?|dollars?|bucks|grand)\b"
    r"|\b(?:a\s+)?(?:couple\s+of\s+|few\s+)?(?:hundred|thousand)\s+(?:pounds?|quid|euros?)\b"
    r"|\ba\s+(?:tenner|fiver|grand)\b", re.I)


# A bare figure is a price in a short ask about spending ("is 120 too much"); it is a quantity
# anywhere a measure word says so, and those lines are turned away first.
A_BARE_FIGURE = re.compile(r"\b\d{2,}\b")


# The turn before can carry the sum with no currency word on it ("he wants 400", "they quoted 400"),
# and a verb of paying is what makes a bare figure there a price: "my sister is 40" is not one, so
# "is that a lot" after an age is left alone.
A_MONEY_VERB = re.compile(r"\b(?:want|wants|wanted|ask|asks|asked|asking|charge|charges|charged|"
                          r"charging|quote|quotes|quoted|quoting|cost|costs|costing|pay|pays|paid|"
                          r"paying|spend|spent|spending|come|comes|coming|say|says|said|tell|"
                          r"tells|told|give|gives|gave|price|priced)\b[^.?!]*?\b\d{2,}\b")


A_MEASURE = re.compile(
    r"\b(?:cups?|mugs?|glasses?|hours?|minutes?|mins?|miles?|km|kms|kilograms?|kilos?|kg|"
    r"grams?|degrees?|times?|days?|weeks?|months?|years?|cm|mm|metres?|meters?|litres?|"
    r"liters?|pints?|slices?|spoons?|teaspoons?|handfuls?|steps?|pages?|screens?|"
    r"episodes?|calories?|carbs?)\b")


# "too much for me" is somebody overwhelmed, not a price, and "for us" is the same shape.
FOR_A_PERSON = re.compile(r"\bfor\s+(?:me|us|him|her|them|you|myself|ourselves)\b")


# A sum split between people is a fairness question between them, not a price to hold against the
# market: "we split the rent 60 40, is that fair". QUOTE_ASKS keeps the same line out, same reason.
SPLIT_BETWEEN_PEOPLE = re.compile(r"\b(?:split|splits|splitting|share|sharing|going halves|"
                                  r"pay half|pays half|pay more|pay less)\b")


# A question, not a verdict said out loud: "is 250 too much" asks, and "it isnt worth it" (a deck row
# about somebody's own life) does not, so only the ask shapes get here.
A_PRICE_ASK = re.compile(r"^(?:and\s+|so\s+|but\s+|ok\s+|okay\s+|also\s+)?(?:is|isnt|aren'?t|"
                         r"are|was|wasnt|wasn'?t|were|does|doesnt|do|did|didnt|would|wouldnt|"
                         r"should|shouldnt|could|will|that|this|too|seems?|looks?|sounds?)\b|\?")


PRICE_VERDICT_LINES = (
    "{figure} only says something next to another price: the same thing elsewhere, or the same job "
    "from someone else. Get one of those and it is easy to call.",
    "Whether {figure} is a lot depends on what the same thing goes for. One other price - another "
    "shop, or another quote for the same work - settles it.",
    "Hold {figure} against one more price for the same thing before you decide; the pair tells you "
    "more than any rule of thumb.",
)


def _the_figure_in(text):
    """The sum as the person wrote it, or "" when there is no money in the line."""
    found = MONEY_IN_A_LINE.search(text or "")
    return " ".join(found.group(0).split()) if found else ""


def _a_price_wants_a_verdict(clean, memory):
    """The pool for a price asked to be judged, or None for any other line.

    Only a short ask with a sum in reach: a longer line puts the thing and the sum in the same
    breath ("the plumber quoted 900 to fix it, is that fair") and the quote check and the entries
    above read those better. A line that splits a sum with somebody, judges how much of something to
    use, or says the weight of it is on them, is not a price and keeps its own reading.
    """
    said = " ".join(str(clean or "").lower().split())
    if not said or len(said.split()) > 7:
        return None
    if not A_PRICE_ASK.search(said) or not PRICE_VERDICT.search(said):
        return None
    if (FOR_A_PERSON.search(said) or SPLIT_BETWEEN_PEOPLE.search(said)
            or A_MEASURE.search(said)):
        return None
    figure = _the_figure_in(said)
    if not figure:
        bare = A_BARE_FIGURE.search(said)
        figure = bare.group(0) if bare else ""
    if not figure:
        # "the one i like is 250 pounds" / "is that a lot": the sum is the one on the turn before,
        # and only the turn before, so a figure from earlier in the chat cannot take this turn. The
        # ask does not have to point at it ("seems like a lot?", "too expensive?") because a verdict
        # word on a question is already the pointing, and the turn before has to be money itself.
        before = _the_line_before(memory)
        figure = _the_figure_in(before)
        if not figure:
            paid = A_MONEY_VERB.search(" ".join(before.split()))
            bare = A_BARE_FIGURE.search(paid.group(0)) if paid else None
            figure = bare.group(0) if bare else ""
    if not figure:
        return None
    return tuple(line.replace("{figure}", figure) for line in PRICE_VERDICT_LINES)


# A present for a new baby is a gift question, and a baby mentioned in one is not a symptom:
# "how much do you spend on a new baby present" is not the health visitor's call.
GIFT_WORDS = frozenset(("present", "presents", "gift", "gifts", "spend on", "budget for",
                        "how much do you spend", "what do you get"))


# A home to buy is not a tenancy: "im 34 and still renting, should i be buying" wants the
# buying side, and Citizens Advice's tenant line would be answering a different question.
BUYING_WORDS = frozenset(("buying", "buy a house", "buy a flat", "buy a home", "bought",
                          "purchase", "ladder", "mortgage", "own a home", "should i buy"))


# A medicine is not a device: "can i take hayfever tablets with my blood pressure pills" is the
# pharmacist's question, while "my tablet wont connect to the wifi" is the maker's.
# A router is a device you log into, so it keeps its maker's page: it is the wifi itself,
# and what runs on it, that no support page can answer for.
NETWORK_WORDS = frozenset(("wifi", "wi-fi", "internet", "broadband", "network", "connection",
                         "signal", "online"))


# A drug or a supplement is the pharmacist's, by name: "should i take vitamins" is not a reason
# to ring 111, and the counter answers it in two minutes for free. `vitamins` and the brand-free
# drug names were missing, so those lines fell to the plain shrug.
MEDS_WORDS = frozenset(("tablets", "pills", "medicine", "medication", "prescription", "dose",
                        "doses", "capsules", "antibiotics", "vaccine", "vaccination", "jab",
                        "jabs", "vitamin", "vitamins", "supplement", "supplements", "ibuprofen",
                        "paracetamol", "aspirin", "painkiller", "painkillers", "antihistamine",
                        "antihistamines", "steroid", "steroids", "insulin", "inhaler"))


def _a_grown_up_asks(clean, words, said):
    """True when the baby in the line is a food's name or the line is about a grown-up.

    "can adults have baby rice" says the person outright. "can i eat baby food" names no child
    except inside the food's own name, so the food names come out first and the rest of the line
    is asked again for a child - "my baby wont eat baby food" keeps its baby, and "is baby food ok
    for a 7 month old" is a parent because the age is still there.
    """
    if _names(words, said, GROWN_UP_WORDS):
        return True
    left = " %s " % clean
    dropped = False
    for name in BABY_FOOD_NAMES:
        if " %s " % name in left:
            left = left.replace(" %s " % name, " ")
            dropped = True
    if not dropped or not _names(words, said, SELF_EATING_WORDS):
        return False
    return not _names(set(left.split()), left, CHILD_AT_HOME)


# The words that make a thread a body thread even when nothing is wrong yet: a scan, a result, a
# clinic. `_thread_is_about_the_body` reads symptoms and parts, and "im scared about the scan" has
# neither, so the reader would have offered the list of trades to somebody waiting on a result.
HEALTH_VISIT_WORDS = frozenset("""
    scan scans mri ct xray x-ray ultrasound biopsy results result consultant clinic appointment
    appointments operation surgery transplant chemo radiotherapy dialysis test tests screening
    ward hospital
""".split())


# The mood words that make "who can i talk to" a person asking who could take some of it. Only
# the person's own state: "worried" is here and "low" is not, because "the car is low on oil" and
# "im low on milk" are the same word doing another job, and this fence decides whether the GP is
# named at all.
A_ROUGH_STRETCH = re.compile(
    r"\b(?:sad|lonely|alone|crying|cry|cried|tears?|grief|grieving|mourning|bereft|depressed|"
    r"depressing|miserable|unhappy|hopeless|worthless|anxious|anxiety|panic(?:king)?|scared|"
    r"afraid|terrified|worried|worry|worries|worrying|struggling|struggle|coping|"
    r"breaking point|burnt out|burned out|drained|overwhelmed|numb|empty|"
    r"cant cope|cannot cope|can't cope|hate myself|no one cares|nobody cares)\b")


# "who can i talk to" after a line about a funeral, a diagnosis or a death is the same ask, and
# the word is a noun rather than a feeling.
A_HARD_THING_HAPPENED = re.compile(
    r"\b(?:funeral|died|death|dying|passed away|diagnos\w*|cancer|tumour|tumor|terminally|"
    r"miscarriage|stillborn|divorce|separated|left me|walked out|sacked|redundant|"
    r"evicted|homeless|hospital|icu|intensive care|hospice)\b")


def _a_bad_stretch_above(memory, look_back=3):
    """True when the last few things the person said were about a bad stretch of their own.

    "who can i talk to" is the same line in a painting thread and in a lonely one, and the reply
    that fits the second ("the GP is not only for a body") is a cold, wrong answer to the first -
    it tells somebody looking for a class that the bot thinks they are ill. So the GP line is only
    offered when a turn or two before this one was about a mood, a funeral or a diagnosis.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-look_back:]
    for turn in turns:
        said = str(turn.get("user") or "").lower()
        if not said:
            continue
        if A_ROUGH_STRETCH.search(said) or A_HARD_THING_HAPPENED.search(said):
            return True
    return False


def _thread_has_a_health_visit(memory, look_back=3):
    """True when the last few things the person said were about a visit or a result coming."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-look_back:]
    for turn in turns:
        words = set(re.findall(r"[a-z'-]+", str(turn.get("user") or "").lower()))
        if words & HEALTH_VISIT_WORDS:
            return True
    return False


def _is_a_form(word, evidence_word):
    """True when `word` is `evidence_word` with a grammatical ending on it.

    "boilers", "coughing", "itched", "itchy", "eviction" are forms of their word. "pesto",
    "toothbrush", "rasher" and "example" are different words that start the same way, and a
    doubled consonant before the ending is still an ending ("resetting", "vomitting").
    """
    tail = word[len(evidence_word):]
    if not tail:
        return True
    if word in NOT_A_FORM:
        return False
    if tail in ENDINGS:
        return True
    return (len(tail) > 1 and tail[0] == evidence_word[-1] and tail[1:] in ENDINGS)


def _names(words, said, evidence):
    """True when the line uses one of these words: whole, a phrase, or a longer form of it
    ("coughing", "boilers", "landlords"). A short word has to match whole, so "taxi" is not
    "tax" and "hr" is not "hrm"; and a longer word only counts when the extra letters are an
    ending, so a toothbrush is not a tooth and pesto is not a pest."""
    for word in evidence:
        if " " in word:
            if word in said:
                return True
        elif any(w == word or (len(word) >= 4 and w.startswith(word)
                               and _is_a_form(w, word)) for w in words):
            return True
    return False


def _reads_as_question(text, words):
    """True when the line asks something, even if the understanding engine called it a
    statement (a question mark mid-line, a typo for a question word: "whats", "wats", or a
    question word that opens a later clause)."""
    if "?" in text:
        return True
    plain = [w.replace("'", "") for w in words]
    if plain and WORD_FIXES.get(plain[0], plain[0]) in QUESTION_WORDS:
        return True
    # A question word after a preposition is not an ask: "we argued about who should pay for
    # dinner" and "im worried about what to say" are telling me something, so the question
    # words inside those clauses are dropped before the late-question test.
    joined = INDIRECT.sub(" ", " " + " ".join(plain) + " ")
    later = INDIRECT.sub(" ", text.lower())
    # A question word can also come later in the line: "my gums are bleeding who should i
    # see" is a question without a question mark or a question word first. LATER_QUESTION
    # covers the question words and modal shapes; ASK_SHAPES adds the asks that carry no
    # question word at all ("any tips", "is it worth fixing").
    return bool(LATER_QUESTION.search(later) or ASK_SHAPES.search(joined))


def _reads_as_a_question_when_repaired(text):
    """The opening shape of the repaired line: a question word first, or an inversion.

    "hw much sleep do kids need" and "wdyt about leeds" are questions whose first word the
    person shortened, and the repair puts the question word back. This is the second reading,
    so it is deliberately the narrow half of `_reads_as_question`: a question word that only
    arrives later in the line is not enough, because "dont know why" repairs to "do not know
    why" and the late "why" would turn a follow-up into a search hedge.
    """
    plain = [word.replace("'", "") for word in str(text or "").split()]
    if plain and WORD_FIXES.get(plain[0], plain[0]) in _OPENING_QUESTIONS:
        return True
    return bool(ASK_SHAPES.search(" " + " ".join(plain) + " "))
