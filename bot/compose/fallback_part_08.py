"""Part 8 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from . import (loss)
from .badnews import (reads_as_bad_news,
                      reads_as_heavy_news)

from .fallback_data import (
    BARE_PICK_AFTER_NEWS,
    BARE_PICK_DO,
    BODY_PARTS,
    CARD_VALIDITY,
    CARE_MODULES,
    CHOICE_HEALTH,
    FALLBACK_MODULE,
    HEALTH_RECORD,
    HEALTH_RECORD_LINES,
    HEALTH_WORDS,
    HEALTH_WORLD,
    HOW_ARE_YOU_ASKS,
    HOW_ARE_YOU_GOING_ON,
    HOW_ARE_YOU_GOING_ON_AFTER,
    JUDGE_ASKS_FINE,
    JUDGE_ASKS_MAD,
    JUDGE_ASKS_SLIGHT,
    JUDGE_LEAD,
    JUDGE_NOUN,
    LIVE_SOON,
    LIVE_TAKE_ALLOWED,
    LIVE_TAKE_ASK,
    LIVE_WEAR,
    MY_OWN,
    MY_OWN_DAY,
    MY_BILL_LINES,
    MY_RECORDS,
    OFFICE_RECORD_LINES,
    AT_THE_TILL,
    POINTS_LINES,
    OPINION_ASKS,
    PICK_ONLY_WORDS,
    QUIET_MODULES,
    REQUEST_CUES,
    SYMPTOM_WORDS,
    THREAD_TURNS,
    WORRY_WORDS,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    NUMBER_PLACES,
)
from .fallback_part_01 import (
    _bounded, _matchable, _nothing_but_tags, _has,
)
from .fallback_part_03 import (
    LOST_IN_A_THREAD, START_ASK, _a_start_ask, _said_what_it_is_about, HEAVY_ABOVE, WORK_NEWS,
)
from .fallback_part_07 import (
    PICK_WORD, PICK_ASK, _capital, _choice_sides, PICK_NOTE, PICK_TITLE, NOT_A_CHOICE, SIDE_BAD,
    SIDE_COPULA, SIDE_GOOD, SIDE_HAS, SIDE_IS, SIDE_ONE, SIDE_OTHER, SIDE_SUBJECT, SIDE_TAIL,
    SIDE_VERB, DESIRE, NOT_A_SIDE, OBSTACLE, TRADE_OFF, LEAN_NOT,
)


def _asks_how_are_you(clean, repaired=""):
    """True when the line's own question is how the bot is, so the manners pool fits.

    The phrase has to be the ask, not words inside a bigger question: "Hi! How's your day
    going?" asks it, and "how are you supposed to say no to your boss" does not - that one
    is a question about the boss, and "can't complain" answers nothing. So the phrase counts
    only when nothing follows it but a tag ("today", "mate") or punctuation. A greeting in
    front of it is fine. `repaired` is the same line with its wrong words put right, which
    only ever adds a reading: "hows ur day going" is the manners question as much as the
    standard spelling is."""
    forms = [_matchable(clean)]
    if repaired and _matchable(repaired) != forms[0]:
        forms.append(_matchable(repaired))
    for form in forms:
        for match in HOW_WAS_YOUR_TIME.finditer(form):
            if _nothing_but_tags(form, match.end()):
                return True
        for phrase in HOW_ARE_YOU_ASKS:
            for match in _bounded(_matchable(phrase)).finditer(form):
                if _nothing_but_tags(form, match.end()):
                    return True
        for phrase in HOW_ARE_YOU_GOING_ON:
            for match in _bounded(_matchable(phrase)).finditer(form):
                tail = form[match.end():]
                # "my daughter is 7 going on 8", "im 41 going on 42", "she is 3 going on 13": the
                # figure after the phrase is the age they are going on to, and the phrase is the
                # way an age is said, not the manners question. The tag test below reads letters
                # only, so the figure is invisible to it and the whole line was answered as small
                # talk ("I'm well, thanks. What are you up to today?").
                if re.search(r"\d", tail):
                    continue
                after = " ".join(re.findall(r"[a-z']+", tail))
                if after in HOW_ARE_YOU_GOING_ON_AFTER:
                    return True
        for pattern in (YOUR_DAY_ASK, YOUR_TIME_ASK):
            for match in pattern.finditer(form):
                if _nothing_but_tags(form, match.end()):
                    return True
    return False


def the_pool_for_a_lost_ask(memory, clean=""):
    """Which offer "i dont know what to do" gets: the news one, the thread one, or the bare one."""
    if _news_above(memory):
        return BARE_PICK_AFTER_NEWS
    if _a_start_ask(clean):
        return START_ASK
    if _said_what_it_is_about(memory):
        return LOST_IN_A_THREAD
    return BARE_PICK_DO


def _news_above(memory, heavy=False):
    """True when the line before this one said something heavy.

    A bare ask is a person asking for a hand with something they have not named. If the turn
    before named a death, a lump or somebody in intensive care, it is not that, and the pool
    that asks what has gone on reads as a friend who was not listening. A job or a bill is bad
    news of the other kind: there the ask is still half a question, so it keeps the ask pool.

    `heavy` asks the medical news alone (`badnews.reads_as_heavy_news`). A refused payment, a
    court letter, a house being sold: the person can still say a plain "what should i do" after
    those, and the ask pool is the right answer - "tell me what has gone on, even roughly" is
    what a friend says to somebody whose benefit was refused. Asking a bereaved person to tell
    the death again is the fault this pool stands down for, and that is the medical list.
    """
    if not isinstance(memory, dict):
        return False
    if _in_a_care_thread(memory):
        return True
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in turns[-2:]:
        low = " ".join(str(turn.get("user") or "").lower().split())
        if not low:
            continue
        if HEAVY_ABOVE.search(low):
            return True
        if reads_as_heavy_news(low) if heavy else (
                reads_as_bad_news(low) and not WORK_NEWS.search(low)):
            return True
        try:
            if loss.reads_as_loss(low):
                return True
        except Exception:  # noqa: BLE001 - a reading that fails is a reading not made
            pass
    return False


# The person's own records: an order, a booking, an appointment, a balance. No search answers
# these and no entry about the world can - the answer only exists with whoever holds the record,
# and the bot does not. They used to reach the search hedge ("a quick search online will get you
# a solid answer"), which sends somebody to Google to find out where their own parcel is.
# STYLE.md's example of not knowing honestly is this class, so the reply says what the bot
# cannot see and the one place the person can.
#
# The ask has to be about the state of a thing of theirs, and nothing else: "how do i return my
# order" asks what to do about it, and "what is a booking reference" asks about the world, so
# both keep the answer they had.
OWN_RECORD_NOT = re.compile(
    r"\b(?:how\s+(?:do|can|could|should|would)\s+i|how\s+to|"
    r"should\s+i|do\s+i\s+need|can\s+i|could\s+i|help\s+me|"
    r"is\s+it\s+worth|worth\s+(?:it|chasing|appealing)|how\s+long\s+does|how\s+much\s+does|"
    r"what(?:'s| is)\s+a|difference|explain|meaning|any\s+tips|advice)\b")


def _their_own_phrase(clean, things):
    """The possessive phrase naming one of the person's own things, or None."""
    for thing in things:
        pattern = MY_OWN.get(thing)
        if pattern is None:
            pattern = MY_OWN[thing] = re.compile(
                r"\b(?:my|our)\s+(?:[a-z']+\s+){0,2}" + re.escape(thing) + r"(?![a-z])")
        match = pattern.search(clean)
        if match:
            return match
    return None


# The ask has to be about where the record has got to. Without that test the shape catches
# phrases where the noun is doing another job - "my balance on one leg", "my order of the
# words", "my delivery of the speech", "my daughter's table manners" - and offers a parcel
# tracking page for all of them.
RECORD_STATE = re.compile(
    r"\b(?:been|yet|still|already|confirmed|approved|ready|arrived|arriving|due|processed|"
    r"done|taken|paid|debited|credited|come\s+off|"
    r"cleared|accepted|rejected|declined|dispatched|despatched|delivered|shipped|sent|sorted|"
    r"collected|out\s+for\s+delivery|"
    r"through|tracked|tracking|back|come\s+back|come\s+through|go\s+through|gone\s+through|"
    r"go\s+out|gone\s+out|went\s+out|come\s+out|on\s+(?:its|the|his|her|their)\s+way|"
    r"what(?:'s|s)?|where(?:'s|s)?|when(?:'s|s)?|what\s+time|how\s+much|how\s+many|how\s+long|status|left|"
    # The same ask handed over instead of phrased as a question: "can you check my bank
    # balance", "can you look up my order", "could you tell me my balance". Every one of those
    # reached the search hedge while "whats my balance" got the honest line, and a search cannot
    # see an account any more than this can. The verb is the ask, so the record phrase and the
    # fences above still decide whether it is about one of their own things.
    r"(?:you|u)\s+(?:check|look\s+(?:(?:it|that)\s+)?up|see|tell\s+me|confirm|look\s+at|"
    r"find\s+(?:(?:it|that)\s+)?out|give\s+me))\b")


# "my statement of work", "my order of the words": the words after the noun say which thing it
# is, so the noun is not the record the person is asking about.
RECORD_QUALIFIED = re.compile(r"\s+(?:of|that|which)\b")


# The records nobody wrote down: "is my visa approved", "has my offer been accepted", "has my
# interview been arranged". The families in `MY_RECORDS` are the things people ask about most and
# each has a line that names where it lives; a noun no table holds fell through them all and got
# the search hedge, which is the one answer that is always wrong for a thing only an office can
# see. The state is what makes it that office's: approved, accepted, arranged, issued, registered
# are not states the person's own eyes settle, which is what keeps "is my cake done", "is my
# washing still wet" and "is my dinner ready" out of here.
OFFICE_STATE = re.compile(
    r"\b(?:approved|approval|accepted|arranged|booked|scheduled|confirmed|issued|granted|"
    r"refused|rejected|declined|registered|processed|dealt\s+with|signed\s+off|finalised|"
    r"finalized|paid\s+out|put\s+through|agreed|arrived|come\s+back|sent|posted|returned)\b")


# "my visa", "my new passport", "my second interview": the possessive is what makes it theirs,
# and up to two words may sit between it and the thing.
MY_ANY_THING = re.compile(r"\b(?:my|our)\s+(?:[a-z']+\s+){0,2}([a-z]+)")


# The thing after the possessive is what the state belongs to, and a person is never a thing an
# office holds: "has my sister arrived yet", "have my parents returned", "has my son arrived at
# school" are questions only the person asking can answer, and the office line answered them with
# letters and reference numbers. The last noun is read, not the presence of a person, because "has
# my sister's visa been approved" is still the visa's state and is the office's.
_A_MY_PERSON = None


def _a_person_is_the_thing(clean):
    """True when the person is the subject of the state, not the owner of a record.

    "has my sister arrived yet" puts a person in the state; "has my sister's visa been approved"
    puts a visa in it. The word after the person decides: a state, a place or the end of the clause
    makes the person the subject, and another noun makes them the owner.
    """
    global _A_MY_PERSON
    if _A_MY_PERSON is None:
        from .loss import PEOPLE
        kinds = "|".join(sorted((re.escape(word) for word in PEOPLE), key=len, reverse=True))
        _A_MY_PERSON = re.compile(
            r"\b(?:my|our|his|her|their|the)\s+(?:" + kinds + r")(?:\'s|s\')?"
            r"(?=\s*(?:$|[,.!?;]|(?:has|have|had|is|are|was|were|did|does|do|not|never|just|now|"
            r"still|yet|already|arrived|arrive|arrives|coming|come|came|returned|returns|got|"
            r"gotten|been|being|at|home|there|back|in|out|safe|ok|alright|fine|well|on|off|to|"
            r"from|away|left|gone|late|early|waiting)\b))", re.I)
    return bool(_A_MY_PERSON.search(clean or ""))


# A thing handed over the counter, where the state was not an office's either: "have i been given
# the wrong change", "i got short changed at the shop". `MY_OWN_STATE` reads "have i been given"
# as a record and sent it to the paperwork line, and a till receipt is the answer to it.
A_TILL_ASK = re.compile(
    r"\b(?:wrong|right|short|extra|too\s+much|too\s+little|double)\s+(?:change|amount)\b|"
    r"\bshort[-\s]?changed\b|\bchange\s+back\b|"
    r"\b(?:overcharged|undercharged|charged\s+twice)\b")


# A thing the person puts in a state themselves, or one nobody can see but them: the home, the
# kitchen and the body are not offices, and an office line over them would be the same confident
# wrong answer the hedge was.
NOT_AN_OFFICE = re.compile(
    r"\b(?:cake|cakes|bread|dough|sourdough|pastry|dinner|tea|lunch|breakfast|supper|roast|"
    r"soup|sauce|stock|washing|laundry|wash|load|hair|nails|beard|leg|legs|arm|arms|back|knee|"
    r"shoulder|eyes|ears|teeth|skin|tattoo|car|cars|bike|bikes|van|boiler|heating|fence|shed|"
    r"plant|plants|garden|lawn|wall|walls|roof|paint|grout|silicone|sealant|floor|tiles|shelf|"
    r"door|window|gutter|drive|pond|allotment|chickens|hens|dog|cat|baby|nappy|sleep|diet)\b")


# "check my gift card balance", "can you check my order", "confirm my booking": the ask said with
# the verb in front, and no state word, so the record pool never saw it. An imperative "check my
# ..." is the same question as "where is my ..." and has the same answer - the record is not here,
# and this is where it lives. The line still has to name one of the record things, so "check my
# tyre pressure" and "check my spelling" are left to whatever knows them.
RECORD_CHECK = re.compile(r"\b(?:check|checking|confirm|look\s+up|track|trace)\b")


# Half of the same asks name no thing at all: the person is the subject, so there is no noun for a
# table to hold - "have i been paid yet", "am i registered", "have i been shortlisted". Every one
# is about their own record rather than the world, and every one of them had the search hedge.
MY_OWN_STATE = re.compile(
    r"\b(?:have|has)\s+i\s+been\s+(?:paid|approved|accepted|registered|booked|confirmed|"
    r"granted|refused|rejected|shortlisted|interviewed|offered|told|sent|given|taken\s+on|"
    r"picked|placed|invited|added|approved\s+for)\b|"
    r"\bam\s+i\s+(?:on\s+the\s+list|in\s+the\s+running|registered|booked\s+in|signed\s+up|"
    r"enrolled|shortlisted|selected)\b")


RECORD_THINGS = tuple(thing for _, things, _ in MY_RECORDS for thing in things)


# The card's own two states are not the balance: a line asking whether it still works wants the
# expiry date, and a line saying it is worth something wants a resale answer.
CARD_VALIDITY_ASK = re.compile(
    r"\b(?:valid|expire|expires|expired|expiry|run\s+out|runs\s+out|ran\s+out|"
    r"out\s+of\s+date|still\s+(?:use|work|spend|spent)|still\s+good)\b")


# "How much is on my card", "what's left on my debit card": the bare word card asks about the
# balance on it, and the pool below only knows the named ones (gift card, voucher, store card).
# The state words keep it off "my card was declined" and "how much is my card worth", which are
# the bank's answer and a resale question, not a balance.
CARD_BALANCE_ASK = re.compile(r"\b(?:how\s+much|balance|left|remaining|still\s+on)\b")


CARD_NOT_A_BALANCE = re.compile(r"\b(?:worth|value|declined|refused|cloned|stolen|blocked|"
                                r"cancel|replace|expire|expires|expired)\b")


MY_CARD_ROW = next((options for name, things, options in MY_RECORDS if name == "card"), None)


# Two of the families answer a line that names no thing of its own: wages are the money row's, and
# a yes or a no about being picked is the application row's.
MY_MONEY_ROW = next((options for name, things, options in MY_RECORDS if name == "money"), None)


MY_APPLICATION_ROW = next((options for name, things, options in MY_RECORDS
                           if name == "application"), None)


# A points, stamps or voucher balance is the person's own and only the scheme holds it. The name
# of the scheme is what makes it theirs: "how many points do i have" on its own is a quiz, a
# driving licence or a game, and those keep whatever answers them, so the line has to say
# loyalty, a named scheme, "my points" or stamps on a card. "How do loyalty points work" is the
# same reader, because where they collect and when they expire is the answer either way.
POINTS_SCHEME = re.compile(
    r"\b(?:loyalty\s+(?:points?|cards?|scheme)|nectar|clubcard|club\s?card|avios|airmiles|"
    r"reward\s+(?:points?|cards?|scheme)|store\s+points?|points\s+cards?|"
    r"(?:my|our)\s+points|(?:my|our)\s+stamps|stamps?\s+on\s+(?:my|the)\s+card|"
    r"points\s+(?:balance|total))\b", re.I)


# The balance question, the expiry question and the how-does-it-work question are one answer:
# where the figures are, when they go, and what the rate makes them worth.
POINTS_ASK = re.compile(
    r"\b(?:how\s+many|how\s+much|how\s+do|how\s+does|how\s+can|what(?:'s|\s+is)?|do|does|did|"
    r"are|is|when|where|worth|expire|expires|expired|expiring|left|balance|collect|collected|"
    r"redeem|redeemed|spend|spent)\b", re.I)


POINTS_NOT = re.compile(
    r"\b(?:licence|license|driving|car|insurance|court|ban|visa|school|university|"
    r"course|grade|exam|game|match|score|league|rugby|football|quiz|test)\b", re.I)


# A thing the person already pays for, asked about its price: not a market price (the "prices"
# live kind answered "how much is my gym membership" with "the seller's site will have today's
# figure", which is a stranger's price for a thing they do not sell) and not a quote for a new one
# (that is @hearty-dog's pool). The thing has to be one a bill covers, and it has to be theirs.
MY_BILL_THING = re.compile(
    r"\b(?:memberships?|subscriptions?|subs|plan|tariff|contract|deal|package|"
    r"season\s+ticket|direct\s+debit|standing\s+order)\b", re.I)


MY_BILL_MINE = re.compile(
    r"\b(?:my|our|the)\s+(?:[a-z]+\s+){0,2}?(?:memberships?|subscriptions?|subs|plan|tariff|"
    r"contract|deal|package|season\s+ticket)\b", re.I)


MY_BILL_ASK = re.compile(
    r"\b(?:how\s+much|what(?:'s|\s+is)?\s+(?:i|we)\s+paying?|what\s+do\s+(?:i|we)\s+pay|"
    r"cost|costs|costing|charge|charged|charging|price|paying|per\s+month|a\s+month|"
    r"a\s+year|over\s+the\s+year|too\s+much|cheaper|worth\s+it|stop\s+paying|cancel)\b", re.I)


# A quote for something new, and a bill that belongs to the house rather than to a contract, are
# not this: "how much is a gym membership" is a price to compare, "how much is my council tax" is
# the council's own band and their own page.
MY_BILL_NOT = re.compile(
    r"\b(?:a\s+gym|join|joining|sign\s+up|new|compare|comparison|cheapest|switch|switching|"
    r"council\s+tax|water|electric|gas|energy|broadband|insurance|mortgage|rent|"
    r"mobile\s+phone|sim\s+only|iphone|phone\s+contract)\b", re.I)


def _their_own_bill(clean):
    """The honest line for the price of something the person already pays for, or None."""
    if not MY_BILL_MINE.search(clean) or not MY_BILL_THING.search(clean):
        return None
    if not MY_BILL_ASK.search(clean) or MY_BILL_NOT.search(clean):
        return None
    return MY_BILL_LINES


def _their_own_points(clean):
    """The honest line for a points or stamps balance, or None."""
    if not POINTS_SCHEME.search(clean) or POINTS_NOT.search(clean):
        return None
    if not POINTS_ASK.search(clean):
        return None
    return POINTS_LINES


CARD_RECORD_THINGS = ("gift card", "gift cards", "voucher", "vouchers", "prepaid card",
                      "store card", "loyalty card", "loyalty points", "card")


def _an_office_record(clean, asking):
    """The honest line for a record only an office can see, or None.

    Two shapes reach here. A thing of the person's own that no family names, put into a state
    only an institution can put it in - "is my visa approved", "has my offer been accepted" - and
    the same ask with the person as the subject and no thing to hold at all: "have i been paid
    yet", "am i registered", "have i been shortlisted". Both were met with the search hedge, and
    no search can see a visa either.

    The state word is what makes it an office's, and the homes and bodies that also have one are
    in `NOT_AN_OFFICE`: "is my cake done" and "is my washing still wet" keep their own answers,
    and the person can settle those themselves.
    """
    if not asking or NOT_AN_OFFICE.search(clean):
        return None
    if A_TILL_ASK.search(clean):
        return AT_THE_TILL
    if _a_person_is_the_thing(clean):
        return None
    if OFFICE_STATE.search(clean) and MY_ANY_THING.search(clean):
        return OFFICE_RECORD_LINES
    if MY_OWN_STATE.search(clean):
        if _has(clean, ("paid", "pay", "wages", "salary", "money", "expenses")):
            if MY_MONEY_ROW is not None:
                return MY_MONEY_ROW
        if MY_APPLICATION_ROW is not None:
            return MY_APPLICATION_ROW
    return None


def _their_own_record(clean, asking):
    """The honest line for one of the person's own records, or None."""
    # Half of what a person asks about their own life names no record at all: the person is the
    # subject of the verb and there is no noun to hold on to - "what did i do last tuesday",
    # "where did i go last weekend", "what did i buy on saturday". Nothing in any knowledge entry
    # has it, no search answers it, and the hedge sent the person to Google to find out about
    # their own week. It is read before the record test below, which needs a possessive noun these
    # lines do not have, and it is read whether or not the line is an ask, because "i went to
    # asda on saturday" is the same history.
    said = _their_own_week(clean)
    if said:
        return said
    # A points or stamps balance is the person's own record even when the line names no
    # possessive: "how many loyalty points do i have" has no "my ..." for the rows below to hold.
    said = _their_own_points(clean)
    if said:
        return said
    checking = bool(RECORD_CHECK.search(clean)) and bool(_their_own_phrase(clean, RECORD_THINGS))
    # A card's expiry is its own question with its own answer, and it can be said as a statement
    # ("my loyalty card has expired") as well as an ask, so it is read before the asking gate.
    validity = bool(CARD_VALIDITY_ASK.search(clean)) and bool(
        _their_own_phrase(clean, CARD_RECORD_THINGS))
    if not (asking or checking or validity) or OWN_RECORD_NOT.search(clean):
        return None
    if validity:
        return CARD_VALIDITY
    if not (RECORD_STATE.search(clean) or checking):
        # A state only an office can see, on a thing no table names: "has my interview been
        # arranged" holds no word the gate above knows, and the search hedge is the one answer
        # that is always wrong for a thing only an office can look up.
        return _an_office_record(clean, asking)
    # A card with money on it is the card's row even when the ask is written with a balance word:
    # "check my gift card balance" matched the money row first ("my gift card balance"), and the
    # reply was about a bank account the person had not mentioned.
    rows = MY_RECORDS
    if _their_own_phrase(clean, CARD_RECORD_THINGS):
        rows = sorted(MY_RECORDS, key=lambda row: row[0] != "card")
    for name, things, options in rows:
        phrase = _their_own_phrase(clean, things)
        if phrase and not RECORD_QUALIFIED.match(clean, phrase.end()):
            return options
    if (MY_CARD_ROW is not None and CARD_BALANCE_ASK.search(clean)
            and not CARD_NOT_A_BALANCE.search(clean)
            and _their_own_phrase(clean, ("card",))):
        return MY_CARD_ROW
    phrase = _their_own_phrase(clean, HEALTH_RECORD)
    if phrase and not RECORD_QUALIFIED.match(clean, phrase.end()):
        if _has(clean, HEALTH_WORLD):
            return HEALTH_RECORD_LINES
    # The named families are read first and keep their own lines - a booking is in a confirmation,
    # a balance in the bank's app - and only a thing no table holds comes to the office line.
    return _an_office_record(clean, asking)


# The person's own day, said with a day behind it: "what did i do yesterday", "where did i go last
# weekend", "what did i buy on saturday". The day is what makes it their own history rather than a
# question about the world - "what did i do wrong" is about the thing in hand and keeps its own
# answer - and the doing has to be one of the ordinary ones a diary holds: shoulders, schools and
# shifts are in the record entries already. What they said in this chat is the memory store's
# ("what did i say yesterday"), so saying and telling are not here.
A_DAY_AGO = re.compile(
    r"\b(?:yesterday|last night|last (?:week|weekend|month|(?:mon|tues|wednes|thurs|fri|satur|"
    r"sun)day)|on (?:mon|tues|wednes|thurs|fri|satur|sun)day|this (?:morning|afternoon|evening)|"
    r"the weekend|earlier today)\b")


MY_OWN_DOING = re.compile(
    r"(?:^|\b(?:what|where|who|when|which|how much|how many)\b[^?]{0,40}?)"
    r"\b(?:did|have|had)\s+(?:i|we)\s+(?:already\s+|actually\s+|just\s+|even\s+)?"
    r"(?:do|done|go|gone|see|seen|visit|visited|buy|bought|spend|spent|eat|eaten|drink|drunk|"
    r"work|worked|book|booked|order|ordered|pay|paid|take|taken|get|got|watch|watched|meet|met)\b")


MY_OWN_DAY_LINES = (
    "I haven't got your diary, sorry - I only know what you tell me here. Your phone's calendar or "
    "the photos from that day will usually bring it back.",
    "Nothing of yours to look at from this end. The calendar, the photos and the emails from that "
    "day are where it is - tell me what you find and I'll help with the rest of it.",
)


# A medicine ask has a day behind it and the same "did i take" doing, but the person who knows is
# not the calendar: "have i taken my pills this morning", "did i take my tablets this morning",
# "have i taken my antibiotics this morning" were answered with the diary line, and "the photos
# from that day" is no help for whether a tablet was swallowed. The health entries already answer
# these by naming the pharmacist and the GP, so the reader stands down for any line that names the
# medicine, and the answer the person had before is the one they get.
NOT_ABOUT_THEIR_DAY = re.compile(
    r"\b(?:pill|pills|tablet|tablets|medicine|medicines|medication|medications|meds|"
    r"antibiotic|antibiotics|inhaler|insulin|dose|doses|injection|injections|jab|jabs|"
    r"painkiller|painkillers|paracetamol|ibuprofen|steroid|steroids|epipen|"
    r"vitamin|vitamins|supplement|supplements|prescription|prescriptions|drops|patch|patches)\b")


def _their_own_week(clean):
    """The honest line for what the person did on a day gone by, or None.

    The fact is not in any entry about the world and a search does not know it either, so the
    reply says in a few words what the bot cannot see and names the one place the person can:
    the calendar, the photos and the emails of that day. A line about the thing in hand rather
    than their history ("what did i do wrong") has no day in it and keeps its own answer.
    """
    said = " ".join(str(clean or "").lower().split())
    if not said:
        return None
    if NOT_ABOUT_THEIR_DAY.search(said):
        return None
    if A_DAY_AGO.search(said) and MY_OWN_DOING.search(said):
        return MY_OWN_DAY_LINES
    return None


# A phone number is a live fact like an opening time: it changes, and a wrong one is worse than
# no answer at all, because the person dials it. So a line that wants the number of a place gets
# the one place that number lives for that kind of place, never digits. It reads only the ask
# shaped "the number for ..." / "what's the number" / "how do i ring ...", so a report ("the
# bank's number was engaged all morning") and a number of the person's own ("my account number")
# are left alone, and a place nobody here knows ("the number for 111") stays with the pool that
# does know it.
NUMBER_WANTED = re.compile(
    r"\b(?:the|a|their|its|his|her)\s+(?:[a-z']+\s+){0,2}number\b|"
    r"\bnumber (?:for|to (?:ring|call|phone))\b|\b(?:phone |telephone |contact )number of\b|"
    r"\b(?:whats|what's|wats|wots) (?:the )?(?:phone |telephone )?number\b|"
    r"\bhow do i (?:ring|phone|call)\b|\b(?:need|want|looking for) (?:the )?(?:phone )?number\b|"
    r"\bcontact (?:details|number)\b|\blook up the number\b|\bgive me the number\b|"
    r"\bnumber to (?:ring|call|phone)\b|\bwhat number (?:do|should) i (?:ring|call)\b")


# A number that was engaged, wrong or unanswered is being reported, not asked for: "the council
# number was engaged all morning" is a complaint, and the honest line about where a number lives
# answers a question nobody asked.
# "The number of council houses" counts them: the counting sense of "number of" is not a phone
# number unless the line says phone.
NUMBER_OF = re.compile(r"\bnumber of\b")


NUMBER_OF_PHONE = re.compile(r"\b(?:phone|telephone|contact|mobile)\s+number of\b")


NUMBER_REPORT = re.compile(
    r"\bnumber (?:was|is|kept|keeps|has been|had been|never|didnt|didn't|rang|rung|went)\b|"
    r"\b(?:i|we|she|he|they)\s+(?:rang|rung|phoned|called|tried)\s+"
    r"(?:the\s+|my\s+|her\s+|his\s+|their\s+|our\s+)?(?:[a-z']+\s+){0,2}number\b")


# A number they already hold is not one to ring for: "whats my reference number" and "my policy
# number" belong to the record pools, and a bank's "customer number" is not a phone.
NUMBER_NOT = ("reference number", "order number", "account number", "policy number",
              "national insurance", "registration number", "ni number", "case number",
              "invoice number", "membership number", "customer number", "flight number",
              "bus number", "train number", "house number", "serial number", "pin number",
              "tracking number", "claim number")


NUMBER_PLACE_PATTERNS = {}


def _names_place(clean, places):
    """True when the line names one of these places, plural or not ("the councils number")."""
    for place in places:
        pattern = NUMBER_PLACE_PATTERNS.get(place)
        if pattern is None:
            pattern = NUMBER_PLACE_PATTERNS[place] = re.compile(
                r"\b" + re.escape(place) + r"(?:s|es)?\b")
        if pattern.search(clean):
            return True
    return False


def _their_contact_number(clean, asking):
    """The honest line for the phone number of a place the person wants to ring, or None.

    `asking` is not consulted: the shape in NUMBER_WANTED is what tells a want from a report.
    """
    if not NUMBER_WANTED.search(clean) or _has(clean, NUMBER_NOT):
        return None
    if NUMBER_REPORT.search(clean):
        return None
    if NUMBER_OF.search(clean) and not NUMBER_OF_PHONE.search(clean):
        return None
    for places, options in NUMBER_PLACES:
        if _names_place(clean, places):
            return options
    return None


# Their own shift, which is on a rota nobody here can see. "What time do i start work tomorrow"
# and "am i working on saturday" are not questions about the world: the answer is a rota, on the
# person's side of the screen, written by somebody the bot cannot ring - so the search hedge is
# the worst of both, and describing how rotas work (the entry that answers "my shift got
# switched") is a paragraph about somebody else's rota.
MY_DAY_ASK = re.compile(
    r"(?<![a-z])(?:what time|when|which time|what hours)(?: (?:do|does|am|are|will|should))? i "
    r"(?:start|finish|begin|leave|get in|get off|clock in|clock off|be in|be on|in|on)(?![a-z])"
    r"|(?<![a-z])(?:am|will) i (?:be )?(?:working|in work|in today|in tomorrow|on shift|"
    r"on a shift|on the rota)(?![a-z])")


# The words that can sit around it without making it about something else: which day, and the
# work itself. "what time do i finish work" is this reading, "what time do i finish the essay"
# and "what time do i start the roast" are not.
MY_DAY_SAID = frozenset("""
work works working job shift shifts rota hours office site shop store school placement
today tomorrow tonight now this next the a an on at in for till until from to and or but so
then also please just know wondering do does did dont don't not never any idea anyone anybody
you your me i my actually usually normally roughly about quick question one more supposed meant
ever again morning mornings afternoon evening evenings night nights early late earlies lates days
week weekend monday tuesday wednesday thursday friday saturday sunday day
start starts finish finishes begin clock off experience induction
""".split())


# Named out loud, the timetable is somebody else's to keep: a school's office, a course, a
# surgery's appointment. They have their own line, and it is not this one.
MY_DAY_NOT = re.compile(
    r"\b(?:school run|college|uni|university|course|class|lesson|exam|appointment|nurse|doctor|"
    r"dentist|hospital|physio|clinic|chemist|pharmacy|hair|barber|gym|football|training|"
    r"the match|the kids?|the children|pick(?:ing)? up|drop(?:ping)? off|"
    r"tablets?|medicine|medication)\b", re.I)


def _their_own_day(clean):
    """The honest line for their own shift, or None.

    Last resort only: it is asked where the bot has nothing else, so a line the knowledge has a
    card for keeps it.
    """
    match = MY_DAY_ASK.search(clean)
    if not match or MY_DAY_NOT.search(clean):
        return None
    if not (_has(clean, ("work", "works", "working", "job", "shift", "shifts", "rota", "hours"))
            or re.search(r"\bclock(?:ed|s)? (?:in|off|on)\b", clean)):
        return None
    rest = clean[:match.start()] + " " + clean[match.end():]
    for word in re.findall(r"[a-z']+", rest):
        if word not in MY_DAY_SAID:
            return None
    return MY_OWN_DAY


# "What time do the shops open" asks when a place opens; "what time do i start work" and "what
# time does my shift start" ask about the person's own day. The honest line about opening hours
# answers a question nobody asked there, so a time ask whose subject is the speaker - a
# first-person subject, or a possessive of their own - is not about a venue. One sentence found
# it: "what time do i take my tablets" was answered "I can't check today's opening hours, sorry."
OWN_TIME_ASK = re.compile(
    r"(?<![a-z])what time (?:do|does|did|will|would|should|can|could|shall) "
    r"(?:i|we|my|our)(?![a-z])")


# "What time is my train" asks the same thing with a different verb and no bad habit behind it,
# so the travel pool reads it too.
MY_TIME_ASK = re.compile(r"(?<![a-z])what time (?:is|are|was|were) (?:my|our)(?![a-z])")


OWN_VERB_OPEN = re.compile(r"(?<![a-z])(?:i|we) (?:open|close|shut)(?![a-z])")


def _a_bare_wear_ask(clean):
    """True when a take/wear ask is the whole of the line and nothing else is attached."""
    text = clean
    for phrase in sorted(LIVE_TAKE_ASK, key=len, reverse=True):
        text = text.replace(phrase, " ")
    for word in tuple(LIVE_WEAR) + tuple(LIVE_SOON):
        text = text.replace(word, " ")
    for word in re.findall(r"[a-z']+", text):
        if word not in LIVE_TAKE_ALLOWED:
            return False
    return True


# "Is it going to rain on saturday" names no weather word the list above holds, only a day.
# The words are the sky's own, so "hot tomorrow", "frost tonight" and "icy on saturday" reach the
# note the way "cold tonight" already did; "nice", "dull" and "grey" only count beside a day,
# because on their own they are a verdict on anything.
LIVE_WEATHER_DAY = re.compile(
    r"\b(?:rain|raining|rainy|snow|snowing|sunny|sun|windy|warm|cold|hot|icy|frost|frosty|"
    r"fog|foggy|misty|muggy|humid|cloudy|overcast|chilly|freezing|storm|stormy|thundery|hail|"
    r"showers?|drizzle|drizzling|nice|dull|grey|gray)\b[^.!?]{0,28}?"
    r"\b(?:today|tonight|tomorrow|this week|next week|weekend|saturday|sunday|monday|tuesday|"
    r"wednesday|thursday|friday)\b", re.I)


# The same question, asked about a piece of time: "how was your day", "how did your evening
# go", "how's your week been". A time word is what makes it the bot's own day and nothing
# else in the world, so "how did your meeting go" is still its own question.
HOW_WAS_YOUR_TIME = re.compile(
    r"(?<![a-z])hows? (?:is |was |are |were |did |has |have )?(?:your|you) "
    r"(?:day|days|week|weeks|weekend|evening|morning|afternoon|night|shift|holiday|break|time)"
    r"(?![a-z])")


# The manners question in the shapes the phrase list cannot see, because a verb comes between
# the second person and the day: "what have you been doing", "are you having a good day", "did
# you have a nice weekend". The second person is what makes it the bot's own day - "im having a
# good day" is the person's and stays theirs - and the time word at the end is what the line is
# about, so a line with anything else after it ("are you having a baby") is not this question.
YOUR_DAY_ASK = re.compile(
    r"\b(?:are|were|have|had|did|do|does)\s+(?:you|u)\s+(?:been\s+)?"
    r"(?:having|had|have)\s+(?:a\s+|an\s+)?(?:good|nice|great|lovely|ok|okay|quiet|crap|bad)?\s*"
    r"(?:day|days|weekend|evening|night|morning|afternoon)\b")


# A day, week or evening with the bot's possessive in front of it is the bot's own time and
# always was the manners question: "hows your day going anyway", "whats your day been like".
# The three above read the verb; this reads the noun, which no other subject can own.
YOUR_OWN_TIME = re.compile(
    r"(?<![a-z])(?:your|you)\s+(?:day|days|week|weeks|weekend|evening|morning|afternoon|night)"
    r"(?![a-z])")


# "what have you been doing", "what u been up to": the ask is about the bot's own time, and
# nothing else can follow it but a tag.
# The shortest way of asking it back: "what about you", "and you?", "yourself?" one turn after an
# answer. Every follow-up reader in the bot reads it as a question about the thing on the table -
# after the egg answer, "what about you" got the egg answer again - so the composer claims it with
# the same manners pool. A line that names anything after the hand-back ("what about your meeting",
# "what about you and your sister") is not this.
HAND_BACK = re.compile(
    r"^(?:(?:and|so|ok|okay|but|right|then)\s+)?"
    r"(?:(?:what|how)\s+about\s+(?:you|ya|u|yourself|your\s+(?:day|week|weekend|evening|one))"
    r"|any(?:thing)?\s+new\s+with\s+you"
    r"|yourself"
    # "and you?", "and yourself?", "so you?": the connector in front is what makes a bare
    # pronoun a hand-back rather than a one-word answer.
    r"|(?:and|so|ok|okay|but|right|then)\s+(?:you|ya|u|yourself))\??"
    r"(?:\s+(?:today|then|anyway|though|so|now|lately|honestly|mate))?$")


YOUR_TIME_ASK = re.compile(
    r"\b(?:what|whats)\s+(?:have|has|ve)\s+(?:you|u)\s+been\s+(?:up\s+to|doing|at)\b"
    r"|\b(?:you|u)\s+been\s+(?:up\s+to|doing)\b")


# A question word that opens a later clause ("ok cool. one more thing, how do i ask for a
# raise") asks a question just as much as one that opens the line. A bare auxiliary is not
# enough: "we also have a 4 year old" and "and can't get back to sleep" are statements.
LATER_QUESTION = re.compile(
    r"(?:^|[,.!?;\u2013\u2014-]\s*|"
    r"\b(?:and|but|so|then|also|ok|okay|cool|right|btw|anyway|quick|thing)\s+)"
    r"(?:what|whats|wats|wat|wot|why|whys|how|hows|when|whens|where|wheres|who|whos|which"
    r"|can (?:i|you|we|it) \w+|could (?:i|you|we) \w+|should i \w+|would (?:i|you) \w+"
    r"|do (?:i|you|we) \w+|does (?:it|that|this) \w+|is (?:it|that|this|there) \w+"
    r"|are (?:there|you|we) \w+)\b",
    re.IGNORECASE)


def _asks_for_something(text):
    """True when the line is more than a greeting: it wants an answer."""
    lower = text.lower()
    return any(cue in lower for cue in REQUEST_CUES)


def _reads_as_why(clean):
    """True for a follow-up that asks for the reason behind the taste just given."""
    return clean.startswith("why") or "why that" in clean or "how come" in clean \
        or "what makes you say" in clean


# "What do you think about my landlord refusing repairs?" asks for advice about the speaker's
# own life, not what the bot likes: a glib "I don't mind either way" there is worse than an
# honest hedge, so the taste pools stay out of it.
OWN_LIFE = re.compile(r"\b(?:my|our|his|her|their)\b")


def _is_about_the_persons_own_life(clean):
    """True when the opinion asked for is about the speaker's situation, not about a thing."""
    return bool(OWN_LIFE.search(clean))


def _in_a_care_thread(memory):
    """True when the bot's last answer, reading past its own continuations, was care.

    A pick is not the reply to a bereavement or a crisis: "my mum died last month" / "what would
    you pick" asking for the list invites one where nothing blithe belongs, and "i want to kill
    myself" / "which would you pick" reads as asking which way out. The walk goes on past this
    fallback's own lines, because a grief thread is often several of them in a row.
    """
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(turns[-THREAD_TURNS:]):
        module = turn.get("module")
        if module in CARE_MODULES:
            return True
        if module not in QUIET_MODULES:
            return False
    return False


def _a_lean_only_line(clean):
    """True when the line is only the ask, so the trade-off is what it is about."""
    return not [word for word in PICK_WORD.findall(clean) if word not in PICK_ONLY_WORDS]


def _a_bare_pick(clean):
    """True when the line asks for the bot's own pick and names nothing of its own."""
    if not PICK_ASK.search(clean):
        return False
    if " or " in clean:
        # "cats or dogs, which would you pick" puts the choice in the line itself: that is the
        # taste pools' question, and they have real answers for it.
        return False
    if _has(clean, OPINION_ASKS):
        # "which do you prefer", "what do you think of it": a taste with no options on the table
        # is the taste pools' question, and "No strong view on that one, honestly" is a better
        # answer than a pick of something that is not there.
        return False
    return not [word for word in PICK_WORD.findall(clean) if word not in PICK_ONLY_WORDS]


def _the_side_taken(reply, sides):
    """The side of `sides` the bot's own reply went to, or None when it named neither.

    "cats or dogs" is answered from the knowledge base with "Dogs, by a whisker: daft,
    straightforward and pleased to see you. A cat is the kinder choice if you're out all day",
    and "which would you get" must not then say "I'd go *Cats*": a pick that argues with the
    bot's own last line is worse than no pick at all. The first side the reply puts in front of
    the person is the one it went to, whether it opens on it ("Chinese.") or names it as the
    thing to do first ("Quick: chickpea curry in 25, or a potato curry").
    """
    said = str(reply or "").lower()
    best = None
    for side in sides or ():
        found = re.search(r"\b" + re.escape(side.lower()) + r"", said)
        if found and (best is None or found.start() < best[0]):
            best = (found.start(), side)
    return best[1] if best else None


def _picked_a_side(reply, sides):
    """True when the bot's reply to that choice went to one of the two things in `sides`: the
    choice is still on the table for "which would you get?".

    A fallback line usually offers nothing ("that's beyond what I know well, sorry"), and reading
    an offer out of it would pick an option the bot never named. A light choice answered with a
    side is the exception: "Chinese. I'd take that and not think about it again" is the option.
    """
    return _the_side_taken(reply, sides) is not None


def _offered(memory):
    """The options the bot offered for what the conversation is on, as (name, note) pairs.

    Only a reply that was not the fallback's own: a nod offers nothing to choose between, and
    two options at least, because one thing is not a choice. The offer also has to be the one
    for the subject the chat is on: walk back over the turns that only nod or only ask again
    ("ok", "what would you suggest"), and read the reply to the last line that named something.
    A turn where the person moved on ("the kids want a takeaway tonight") ends the walk, so a
    film offered three turns ago is never picked for a takeaway.
    """
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            continue
        said = PICK_WORD.findall(str(turn.get("user") or "").lower())
        if not said or not [word for word in said if word not in PICK_ONLY_WORDS]:
            continue  # a nod or the same ask again: keep looking for the line it is about
        if turn.get("module") == FALLBACK_MODULE and not _picked_a_side(
                str(turn.get("bot") or ""), _choice_sides(" ".join(said))):
            return []
        found = _titles(str(turn.get("bot") or ""))
        if len(found) >= 2:
            return found
        # The bot's reply need not have offered the options in italics: "chinese or indian
        # tonight" was answered by a pick, and "which would you get?" then wants that pick made
        # again rather than "depends what we're choosing between" - the choice is right there in
        # the line the person has just said.
        sides = _choice_sides(" ".join(said))
        if not sides:
            return []
        # The bot's own answer may have gone to one side already, and the pick says the same one
        # rather than arguing with the line above it.
        taken = _the_side_taken(str(turn.get("bot") or ""), sides)
        if taken:
            return [(_capital(taken), "")]
        # A side read from the person's line goes into a reply mid-sentence ("I'd go *Indian*,
        # out of those"), so it keeps the capital it would have had as a name.
        return [(_capital(side), "") for side in sides]
    return []


def _titles(said):
    """The options a reply offered, as (name, note) pairs."""
    found = []
    for match in PICK_TITLE.finditer(said):
        name = " ".join(match.group(1).split())
        if not name or len(name.split()) > 8 or not name.strip("."):
            continue
        if len(name.split()) == 1 and name[:1].islower() and not any(c.isdigit() for c in name):
            # A word in italics is as often the word being talked about ("nothing rhymes with
            # *purple*") as it is an option: a single lowercase word is not a thing to pick.
            continue
        note = PICK_NOTE.match(said[match.end():match.end() + 90])
        note = " ".join(note.group(1).split()) if note else ""
        if note and re.search(r"\b(?:you|your|i|we|me|us)\b", note):
            # "if you'd rather think" is about the person, not a description to say back.
            note = ""
        found.append((name, note))
    return found


def _names_in(said):
    """The words of a line that name something, with the plumbing and the ask taken out."""
    return {word for word in PICK_WORD.findall(said.lower()) if word not in PICK_ONLY_WORDS}


def _a_named_side(after):
    """The side after the "but" as the thing to pick, or "" when it is not one.

    "the other has better brakes" -> "the one with better brakes"; "further from work" -> "the
    one further from work"; "the people are nicer in the other" -> "the one where the people are
    nicer". A verdict ("i hate it", "the neighbours are awful") is not a side at all, and neither
    is a phrase that comes out of these shapes half-built: nothing is said rather than something
    wrong.
    """
    text = " ".join(str(after or "").split()).strip(" ,.;:")
    text = SIDE_TAIL.sub("", text).strip(" ,.;:")
    # The side has to name an advantage, or there is no second option to name: "my mum is here"
    # and "the pay is less" are a fact and a comparison, not a thing to pick. A side that also
    # reads as a cost ("cheaper but further out") is left alone rather than half-read.
    if not text or NOT_A_CHOICE.search(text) or SIDE_BAD.search(text):
        return ""
    if not SIDE_GOOD.search(text):
        return ""
    # "the other has better brakes" is about the other of the two, and the thing to name is what
    # it has.
    text = SIDE_OTHER.sub("", text).strip(" ,")
    if re.match(r"^(?:is|are|was|were)\s+", text, re.I):
        text = "that " + text
    first = re.match(r"^(?:i|we|im|i'm)\b", text, re.I)
    has = SIDE_HAS.match(text)
    if has:
        return "the one with " + has.group(1).strip(" ,.")
    is_ = SIDE_IS.match(text)
    if is_:
        return "the one that is " + is_.group(1).strip(" ,.")
    if first:
        # "i keep thinking about the art one" is the person's own leaning, not a side to name:
        # handing it back as "the one I keep thinking about" only repeats their sentence.
        return ""
    one = SIDE_ONE.match(text)
    if one and SIDE_GOOD.search(one.group(2)):
        # "the art one sounds more fun" names the thing itself, which is the best label there is.
        return one.group(1)
    if SIDE_SUBJECT.match(text) and SIDE_COPULA.search(text):
        return "the one where " + text
    if re.match(r"^(?:more|fewer|less|better|cheaper|bigger|newer|nicer)\b", text, re.I):
        return "the one with " + text
    if SIDE_VERB.search(text) and not SIDE_SUBJECT.match(text):
        return "the one that " + text
    if not SIDE_SUBJECT.match(text):
        return "the one " + text
    return ""


def _a_trade_off(memory):
    """The side the person put after their "but", named as a thing to pick, or ""

    Only the most recent line of theirs that says something: a nod or the same ask again is
    walked past, and a line that names no trade-off ends the walk, so a "but" from four turns
    ago cannot answer a question about something else.
    """
    pointed = []
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            continue
        said = " ".join(str(turn.get("user") or "").split())
        found = PICK_WORD.findall(said.lower())
        if not found or not [word for word in found if word not in PICK_ONLY_WORDS]:
            continue
        match = TRADE_OFF.search(said)
        if not match:
            if len(said.split()) <= 3 and not said.endswith("?"):
                # "the bikes", "the jobs": a two-word pointer back at the thing they have just
                # put down is not a new subject, so it is walked past - but only when it names
                # something in the trade-off it reaches ("the boiler" does not).
                pointed.append(said)
                continue
            return ()
        before = match.group(1).strip(" ,.")
        after = match.group(2).strip(" ,.")
        if (len(before.split()) < 2 or len(after.split()) < 2
                or NOT_A_SIDE.search(after) or DESIRE.search(before)
                or OBSTACLE.search(after)):
            return ()
        if _is_a_body_or_care_trade_off(said):
            return ()
        named = _a_named_side(after)
        if not named:
            return ()
        names = _names_in(said)
        if [line for line in pointed if not _names_in(line) & names]:
            return ()  # the short line was a subject of its own, not a pointer at this
        return named
    return ()


def _is_a_body_or_care_trade_off(said):
    """True when the trade-off is about their health, their mood or somebody in care.

    The health sets are the bot's own reading of a body, and they are read here for the same
    reason: a side taken on "the pain is worse at night but i dont want to bother the doctor" is
    a side taken on going to the doctor, which is nobody's pick to make.
    """
    words = set(re.findall(r"[a-z']+", said.lower()))
    if words & (BODY_PARTS | SYMPTOM_WORDS | HEALTH_WORDS | CHOICE_HEALTH | WORRY_WORDS):
        return True
    return bool(LEAN_NOT.search(said))


# The ask on its own, with nothing else in the line: the moment it names a subject of its own
# ("is that a bad idea for a birthday") it is a question about that subject, not a verdict asked
# for on the plan already on the table.
JUDGE_ASK = re.compile(
    r"(?:^|\b(?:ok|okay|so|and|but|hmm|well|wait|honestly|seriously)\b )"
    r"(?:is|was|would|will)\s+(?:that|this|it)\s+(?:be\s+)?(?:such\s+)?(?:a\s+|an\s+)?"
    r"(?P<face>" + JUDGE_ASKS_SLIGHT + r"|" + JUDGE_ASKS_FINE + r"|" + JUDGE_ASKS_MAD + r")"
    r"(?:\s+" + JUDGE_NOUN + r")?"
    r"(?:\s+(?:or\s+not|then|though|tho|or\s+what|at\s+all))?"
    r"$"
    r"|(?:^|\b(?:ok|okay|so|and|but|hmm|well)\b )does\s+(?:that|this|it)\s+"
    r"(?:sound|seem|look)\s+(?:like\s+)?(?:a\s+|an\s+)?"
    r"(?P<face2>" + JUDGE_ASKS_SLIGHT + r"|" + JUDGE_ASKS_FINE + r"|" + JUDGE_ASKS_MAD + r")"
    r"(?:\s+" + JUDGE_NOUN + r")?$"
    r"|(?:^|\b(?:ok|okay|so|and|but|hmm|well)\b )am\s+i\s+(?:being\s+)?"
    r"(?P<face3>" + JUDGE_ASKS_MAD + r"|" + JUDGE_ASKS_SLIGHT + r")$")


# The same ask with nothing to point at: the plan is on the table from the line before, so the
# whole line is the verdict word. It only counts where a plan is already named (see
# `_a_verdict_on_their_plan`): an adjective with nothing on the table is not a question.
JUDGE_ASK_BARE = re.compile(
    r"^(?:(?:ok|okay|so|and|but|hmm|well|honestly|seriously)\s+)?"
    r"(?:(?:does|would|is|was)\s+(?:that|this|it)\s+)?"
    r"(?:(?:sound|seem|look)\s+(?:like\s+)?)?"
    r"(?:(?:a|an)\s+)?"
    r"(?P<face>" + JUDGE_ASKS_SLIGHT + r"|" + JUDGE_ASKS_FINE + r"|" + JUDGE_ASKS_MAD + r")"
    r"(?:\s+(?P<bare_noun>" + JUDGE_NOUN + r"))?$")


JUDGE_PLAN_OPENING = re.compile(
    JUDGE_LEAD +
    r"(?:im|i am|i)\s+(?:going to|gonna|off to|out to|away to|heading to|heading off to"
    r"|planning to|planning on|thinking of|thinking about"
    r"|about to|want to|wanna|might|will|intend to|intending to|decided to|have decided to"
    r"|plan to|hoping to|hope to|looking to|keen to|aiming to|thinking i(?:d| would) like to"
    r"|think i(?:ll| will)|reckon i(?:ll| will))\s+(?P<plan>\S.{1,58})$"
    r"|" + JUDGE_LEAD +
    r"i\s+(?:have\s+)?decided\s+(?:to|i(?:'ll| will))\s+(?P<plan9>\S.{1,58})$"
    r"|" + JUDGE_LEAD +
    r"(?:my|the)\s+plan\s+is\s+to\s+(?P<plan2>\S.{1,58})$"
    # An age in front of it does not stop it being a plan: "im 40 and want to change career".
    r"|" + JUDGE_LEAD +
    r"(?:im|i am)\s+(?:nearly\s+|about\s+)?\d{2}\s*,?\s+and\s+(?:want|need|plan)\s+to\s+"
    r"(?P<plan3>\S.{1,58})$")


# What the person asked instead of said: "should i get a credit card" is a plan with a question
# mark on it, and the verdict line names it the same way.
JUDGE_SHOULD_OPENING = re.compile(
    JUDGE_LEAD +
    r"(?:should\s+(?:i|we)|(?:i|we)\s+(?:should|ought to))\s+(?P<plan>\S.{1,58})$")


# The openings that are a hope or an intention rather than a plan put down as one: "im hoping to run
# a half marathon", "im looking to rent out my spare room". A plan said this way is still the plan
# on the table - the composer was asking "say the idea in a line" after the person had said it in
# one - but the verdict after it is only this turn's when there is one to give.
JUDGE_HOPED_FOR = re.compile(
    r"\b(?:hoping|hope|looking|keen|aiming|intending|planning on)\b"
    r"|\bthinking i(?:d| would) like to\b", re.IGNORECASE)


# "Is that wise?" with nothing on the table is a judgement asked for in a line of its own, and it
# can be given without knowing the plan: what a friend says is that the test is the way out. Only
# the words that only ever mean "is the plan sound" - "is that good" and "is that great" are just
# as often about a bit of news, and after "my chicken is still pink" the food answer is the one.
# "am i mad" after a line that is itself about their own mind - hearing things, being watched,
# memory going - is not a plan question and not self-doubt about a choice. Standing down sends it
# to the annoyance pool ("Say it out loud to whoever caused it"), so this arm keeps it and says the
# two things that are true: nothing here reads as mad, and this is a GP's call, not a stranger's.
MIND_WORRY = re.compile(
    r"\b(?:hear(?:ing)?\s+(?:noises?|voices?|things|stuff)|see(?:ing)?\s+things|"
    r"watching\s+me|following\s+me|remember(?:ing)?\s+(?:anything|things)|"
    r"losing\s+(?:my\s+mind|it|my\s+memory)|forgetting\s+everything|going\s+mad)\b",
    re.IGNORECASE)


# A plan that names its own limit is not one a verdict can bless from here, however it is said:
# the hole is in the words.
JUDGE_NAMES_A_HOLE = re.compile(
    r"\bno\b|\bnothing\b|\ball\s+(?:my|our|your|the)\b|\bwithout\b|\bnot\s+\w+|\bnever\b"
    r"|\b(?:skip|skipping|stop|stopping|pause|pausing|come off|coming off)\s+(?:my|the|your)?\s*"
    r"(?:medication|meds|tablets|pills|insulin|treatment|doses?)\b", re.IGNORECASE)


# A wish can name an act, and no verdict can bless an act it would have to talk somebody out of.
# "i want to key my exs car" was answered "Nothing wrong with wanting to key my exs car." and "i
# want to stop eating" got "Yes, that is a reasonable way to do it". The hole in those is in what
# the wish is *for*, not in how they would do it, so it is read on the wish's own words: an act
# against a person or their things gets the answer the anger gets, and a wish against themselves
# or their money stands down to the topic that knows what to say about it.
JUDGE_ACT_AT_SOMEONE = re.compile(
    r"\b(?:key|keying|scratch|scratching|slash|slashing|smash|smashing|torch|torching|"
    r"vandalise|vandalize|vandalising|spike|spiking|drug|drugging|"
    r"hit|hitting|punch|punching|kick|kicking|strangle|strangling|choke|choking|stab|stabbing|"
    r"shoot|shooting|kill|killing|poison|poisoning|harm|harming|hurt|hurting|"
    r"slap|slapping|smack|smacking|thump|thumping)\s+(?:\w+\s+){0,3}?"
    r"(?:him|her|them|"
    r"(?:my|his|her|their|your|our|somebody's|someone's)\s+(?:\w+))", re.IGNORECASE)


# An answer that opens with the answer - "Yes, once, and make it easy to answer...", "No, not with
# the state of that roof" - has already ruled on the plan, and a verdict pasted over it is the
# weaker reply: "im going to text him back / am i being stupid" wants that advice, not a blessing.
# "Once" was in this list and it was the wrong word for it: an answer that opens on "once" almost
# always opens on a condition, not on a ruling - "Once you can run for an hour without stopping, a
# half marathon takes twelve to sixteen weeks" has not said yes or no to anything, so the verdict
# after it is still this turn's. "Yes, once, and make it easy to answer" is caught by the "yes".
JUDGE_ANSWERS_FIRST = re.compile(
    r"^\W*(?:yes|no|nope|not|don'?t|never|definitely|probably|only)\b", re.IGNORECASE)
