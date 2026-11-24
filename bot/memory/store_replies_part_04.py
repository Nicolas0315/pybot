"""Part 4 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..memory import content, last_user, name, others
from ..memory import when as a_when
from ..memory import facts as extract
from ..memory.store_lines import COUNT_WORD, PLACE_NOT
from ..memory.relations import _every_line, _person_from_pronoun, _plural_person
from bot.memory.corrected import MONTH_ALT
from .store_replies_part_01 import (
    _RELATION, THEM,
)
from .store_replies_part_02 import (
    LOOK_BACK_ANSWER, _a_choice_from_what_was_said, _a_clock_ask, _about_the_bot_here, _turned,
)


def _kind(item):
    """A take-back is a species word or a record; either way the animal it is about."""
    return str(item.get("animal") or "") if isinstance(item, dict) else str(item)


def _a_limit_kept_for_them(low, memory):
    """True when the person the line names has a diet or a condition on record."""
    who = _someone_else_named(low, memory)
    for known in others(memory):
        if known.get("who") != who:
            continue
        return bool(known.get("condition") or known.get("diet"))
    return False


ANSWER_MODULES = frozenset(("answers", "memory_store"))


DETAIL_ASKS = (
    (re.compile(r"\bhow much\b|\bwhat did (?:it|that|it all|they) cost\b"
                r"|\bwhat(?:'s|s| is| was)? (?:the |was the )?(?:pay|price|salary)\b"), "money"),
    (re.compile(r"\bhow long (?:did|was)\b|\bhow long did (?:it|that|they)\b"),
     "time"),
    (re.compile(r"\bhow many\b|\bhow often\b"), "count"),
    (re.compile(r"\bwhere (?:is|are|was|were|did)\b|\bwhich (?:hotel|flight|one)\b"), "place"),
    (re.compile(r"\bwhat time\b|\bwhen (?:is|are|was|were|do|did)\b"), "when"),
    # "we moved house last month" / "which area", "i watched a film" / "what was it called":
    # the ask names the shape of the detail, not the thing, so it is still about their news.
    (re.compile(r"\bwhich (?:area|part|place|school|club|team|course|country|city|kind|sort|type"
                r"|one|ones)\b|\bwhat (?:kind|sort|type) of\b"), "which"),
    (re.compile(r"\bwhat (?:was|is|were) (?:it|they|that|he|she) called\b"
                r"|\bwhat(?:'s|s| is) (?:it|he|she|they) called\b|\bwhat was (?:the )?name\b"),
     "called"),
    (re.compile(r"\bhow (?:far|old|big|tall|heavy|long ago)\b"), "measure"),
    (re.compile(r"\bwhat (?:was|is|were) (?:it|that|they|he|she) (?:about|like)\b"
                r"|\bwhat(?:'s|s) it (?:about|like)\b"), "about"),
)


DETAIL_LEAN = re.compile(r"\b(?:it|that|this|they|them|those|we|you|your|he|she|him|her)\b", re.I)


BARE_MEASURE = re.compile(r"\bhow (?:much|many|long|old)\b", re.I)


# A price the answer on the screen already states. "i've got a dentist appointment" then "how
# much is that" was asked back - "You haven't said - how much is that?" - while the answer two
# lines up said "An NHS check-up is £27.40 in England." A detail already given is not a detail
# left out, and asking for it reads as if the chat had not read its own answer.
MONEY_SAID = re.compile(r"£\s?\d|\b\d[\d,.]*\s*(?:pounds?|quid|euros?|dollars?)\b", re.I)


def _the_answer_already_gives(detail, memory):
    """True when the newest answer on the screen states the detail this line asks about.

    Only the price is read. Nearly every answer states a count or a length ("four to five hours",
    "three things to check"), so a guard on those would take away ask backs that are right; a
    price is stated when it is meant, and a line asking for it has its answer already.
    """
    if detail != "money":
        return False
    said = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for turn in reversed(said[-LOOK_BACK_ANSWER:]):
        if turn.get("module") not in ANSWER_MODULES:
            continue
        reply = " ".join(str(turn.get("bot") or "").split())
        if not reply or reply.rstrip().endswith("?"):
            continue
        return bool(MONEY_SAID.search(reply))
    return False


ASK_OPENER = re.compile(
    r"\A(?:how|what|whats|when|where|which|why|who|whose|is|are|was|were|can|could|should"
    r"|shall|do|does|did|will|would|have|has|am|may|might|any|whose)\b", re.I)


HOW_LONG_IT_TAKES = re.compile(
    r"\bhow long (?:does|do|will|would|is|are|should|can|could)\b[^?]{0,25}?\b(?:take|takes|taking)\b",
    re.I)


WANTING = re.compile(r"\b(?:want|wants|wanting|need|needs|needed|hoping|hope to|planning"
                     r"|plan to|trying to|thinking of|thinking about|would like|i'd like"
                     r"|looking to|saving up|saving for)\b", re.I)


DETAIL_VERBS = frozenset("""
it that this they them those we you your he she him her is are was were did do does
have has had be been cost costs pay paid take taken took last lasted stay staying
go going went get got buy bought end give given much long many where when what time
whats salary price a an the and but so to for in on at of from with about then again
there here
""".split())


DETAIL_KNOWN = {
    "money": re.compile(r"£|\d|\bpounds?\b|\bdollars?\b|\beuros?\b|\bquid\b", re.I),
    "time": re.compile(r"\d+\s*(?:minutes?|mins?|hours?|hrs?|days?|weeks?|months?)"
                       r"|\b(?:" + COUNT_WORD + r")\s+(?:minutes?|mins?|hours?|hrs?|days?"
                       r"|weeks?|months?|years?)|\ban hour\b", re.I),
    "count": re.compile(r"\b\d+\b|\b" + COUNT_WORD + r"\b", re.I),
    "when": re.compile(r"\b\d|\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|january"
                       r"|february|march|april|may|june|july|august|september|october|november"
                       r"|december|tomorrow|tonight|next week|next month|at \d)\b", re.I),
    "place": re.compile(r"\b(?:in|to|at) [A-Z]|\bhotel\b|\bstaying (?:in|at)\b"
                        r"|\b(?:in|to|at) (?!(?:" + PLACE_NOT + r")\b)[a-z]{3,}\b"),
    "which": re.compile(r"\b(?:in|to|at|near|around) \w+|\bcalled\b|\bnamed\b", re.I),
    "called": re.compile(r"\b(?:called|named)\b", re.I),
    "measure": re.compile(r"\b\d|\bmiles?\b|\bkilomet\w+\b|\bkm\b|\bmetres?\b|\bminutes?\b"
                          r"|\bhours?\b", re.I),
}


PLACE_NARROWER = re.compile(r"\b(?:staying|sleeping|eating|hotel|hostel|accommodation|campsite"
                            r"|airport|flight|parking|venue|school|office|shop)\b", re.I)


SHAPE_WORDS = frozenset("""
area part place area school club team course country city town kind sort type one ones called
named name about like
far many much often tall heavy big old long wide
""".split())


def _detail_they_left_out(memory, low):
    """A warm ask back when the question is about a detail of what they just told us."""
    line = str(low or "").strip()
    if not line or len(line.split()) > 9:
        return None
    if _a_clock_ask(line) and not a_when.EVENT_WORD.search(str(last_user(memory) or "")):
        # "what time is it" is a question about the clock, not a detail of their news: the "it"
        # in it points at nothing the chat has said, so asking it back ("You haven't said - what
        # time is it?") tells them nothing while the clock is right there to be said. After a
        # line that names something in a diary - "i have a dentist appointment" - the time is
        # that appointment's, and the ask back is the honest answer.
        return None
    if _about_the_bot_here(memory):
        # "where are you" and "where are you from" ask the bot, not for a detail of the person's
        # own news; the chat's own identity answer is the one that speaks to them.
        return None
    if _a_choice_from_what_was_said(line, memory):
        return None
    if not re.search(r"\b(?:how|whats?|where|when|which|whos?)\b", line):
        return None
    detail = None
    for pattern, kind in DETAIL_ASKS:
        if pattern.search(line):
            detail = kind
            break
    if detail is None:
        return None
    # Nothing of its own: every other word is a function word or one of the light verbs.
    spare = [word for word in re.findall(r"[a-z']+", line)
             if word not in DETAIL_VERBS and word not in SHAPE_WORDS
             and word not in ("how", "what", "where", "when", "which", "why", "s")]
    if spare:
        return None
    # A line with no pronoun at all is the same ask in fewer words when it names the *shape* of
    # the detail - "which area", "how far", "what was it about" - but a bare "how much", "how
    # many", "how long" or "how old" is a question about the world, not about their news: after
    # "i want to save for a house" the line "how much" is asking the bot, and asking it back
    # reads as if they had asked themselves. "what's the pay" leans back on the new job the same
    # way a pronoun does, so it stays.
    if not DETAIL_LEAN.search(line) and not re.search(r"\bthe (?:pay|price|salary)\b", line):
        if detail in ("money", "count", "time") or BARE_MEASURE.search(line):
            return None
    try:
        from ..memory import named as _named
        if _named.a_faulty_thing(memory):
            # The thing on the table has stopped working, so a measure ask about it points at that
            # thing and not at a detail of their news: "my boiler is broken" / "how long does it
            # take" asks how long the repair takes, and asking the line back ("You haven't said -
            # how long does it take?") tells them nothing. The answers module reads it.
            return None
    except Exception:  # noqa: BLE001 - a reading that cannot be imported declines nothing
        pass
    previous = str(last_user(memory) or "").strip()
    if not previous or previous.endswith("?") or len(previous.split()) < 3:
        return None
    # The line before was a question, typed without its mark as often as with it: there is no news
    # in it for a detail to have been left out of, so nothing is asked back. "is it worth getting
    # a flu jab" / "how much does it cost" was answered "You didn't say what it cost - how much was
    # it?", which asks the person the question they just asked.
    if ASK_OPENER.match(previous.lower()):
        return None
    # Their own news, not a question to us: "i" or "we" or "my" in the line before.
    if not re.search(r"\b(?:i|we|my|our|me)\b|\bive\b|\bim\b", previous.lower()):
        return None
    # ... and something that happened or is the case, not a want or a plan: a want has no
    # details to have left out, it has a price tag the bot can talk about.
    if WANTING.search(previous.lower()):
        return None
    # A destination does not answer an ask about a narrower place: "we are going to portugal" then
    # "where are we staying" still wants the hotel, so the place they named is not the detail this
    # line asks about.
    known = DETAIL_KNOWN.get(detail)
    narrower = detail == "place" and PLACE_NARROWER.search(line)
    if known is not None and not narrower and known.search(previous):
        return None
    if detail == "time" and HOW_LONG_IT_TAKES.search(line):
        return None
    if _the_answer_already_gives(detail, memory):
        return None
    if detail == "money" and re.search(r"\bcost\b", line):
        return "You didn't say what it cost - how much was it?"
    ask = _turned(line)
    if not ask:
        return None
    return "You haven't said - " + ask + "?"


PART_ASK = re.compile(
    r"\b(?:what|which|who|where|when)\b[^?.!]{0,40}?\b(?:do|does|did|is|are|was|were|can)\b"
    r"|\bhow (?:much|many|old|long|big|far|often|tall|heavy)\b", re.I)


PART_MINE = re.compile(r"\b(?:my|our)\s+([a-z']+)", re.I)


PART_POINTS = re.compile(r"\b(?:it|its|he|she|they|them|their|there|his|her)\b", re.I)


RECORD_PART = re.compile(
    r"\b(?:earn|earns|earning|paid|pay|wage|wages|salary|hours|shifts?|boss|manager"
    r"|colleagues?|coworkers?|uniform|(?:do|doing|did) there|work with|working with|works with|work for"
    r"|school|nursery|childminder|called|names?|named|model|make|year|colour|color|reg"
    r"|brand|mileage|breed)\b", re.I)


PART_ADVICE = re.compile(r"\b(?:should|shall|recommend|suggest|best|better|worth|instead|advice"
                         r"|ideas?|how do i|how can i|can i|could i|would you)\b", re.I)


PART_HELP = re.compile(r"\b(?:what|how) (?:do|can|should|could|would) i do (?:about|with|for|to|next"
                       r"|now|then)\b", re.I)


PART_OF = (
    ("job", re.compile(r"\b(?:earn|earns|earning|paid|wages?|salary|shifts?|boss"
                       r"|colleagues?|coworkers?|uniform)\b")),
    ("city", re.compile(r"\b(?:live|lives|moved|grew up)\b")),
    ("pets", re.compile(r"\b(?:dogs?|cats?|pets?|puppy|kitten|rabbit|hamster)\b")),
    ("people", re.compile(r"\b(?:son|daughter|mum|dad|mother|father|sister|brother"
                          r"|partner|wife|husband|kids?|children)\b")),
    ("owns", re.compile(r"\b(?:car|bike|laptop|phone|van)\b")),
)


JOB_PART = re.compile(
    # "there" on its own is in most of the asks it is not wanted in ("what is there to see",
    # "where is there work"), so it only counts as the object of the doing: "and what do i do
    # there", "what are they like to work there".
    r"\b(?:do|doing|did|work|working|works) there\b"
    r"|\bwho (?:do|does|did) (?:i|we) (?:\w+ )?(?:with|for)\b"
    r"|\b(?:what|which) (?:are )?(?:the )?(?:hours|shifts?|pay|uniform)\b"
    r"|\bhow (?:much|many|long) (?:do|does|did) (?:i|we)\b", re.I)


DRINK_DIET = frozenset("""alcohol booze wine wines beer beers lager lagers cider spirits gin
vodka whisky whiskey rum prosecco champagne cocktails cocktail sherry brandy""".split())


REMEMBER_IT = re.compile(
    r"^(?:and |so |ok |okay |but |well )*(?:do |did )?you (?:still )?(?:remember|recall)"
    r"(?: (?:it|that|this|that one))?(?: (?:yes or no|or not|right|then))?$"
    r"|^(?:do|did) you (?:still )?(?:remember|recall) (?:it|that|this)$")


CONFIRM_FRAMES = (
    (re.compile(r"^(?:am|was) i\s+(?:not\s+)?(.+)$"), "i am "),
    (re.compile(r"^(?:do) i\s+(?:still\s+|really\s+|actually\s+)?(.+)$"), "i "),
    (re.compile(r"^(?:have) i\s+(?:got\s+|really\s+|actually\s+)?(.+)$"), "i have "),
)


YES_NO_ASK = re.compile(
    r"^\W*(?:is|are|was|were|does|did|do|can|could|has|have|had|will|would|should|may|might)\s+"
    r"(?:she|he|they|his|her|their|my|your)\b", re.I)


YES_NO_FRAME = re.compile(
    r"^\W*(?:is|are|was|were|does|did|do|can|could|has|have|had|will|would|should|may|might)\s+"
    r"[^?.!;]*[?.!;]+\s*", re.I)


TELLING_AFTER_ASK = re.compile(
    r"\b(?:he|she|they|it|we|my\s+(?:" + _RELATION + r"))\s+"
    r"(?:is|are|was|were|doesnt|does not|dont|do not|cant|cannot|wont|will not|has|have|had"
    r"|likes?|loves?|eats?|drinks?|never|always|usually|only|really|prefers?|hates?)\b", re.I)


DIET_ANY = re.compile(r"^(?:on\s+)?(?:a\s+)?diet(?:ing)?$", re.I)


DUTY_ASK = re.compile(
    r"\b(?:need|needs|needed|have|has|had) to\b|\bshould\b|\bshouldn't\b|\bmust\b|"
    r"\bgot time\b|\bworth\b|\bhow (?:often|much|long)\b|\bbetter\b")


REMEMBERING_FRAME = re.compile(
    r"^(?:(?:and|but|so|ok|okay|right|well|oh|ah|quick one|sorry|hi|hiya|hey|hello|just|also)"
    r"[\s,]+)*"
    r"(?:"
    r"(?:(?P<aux>do|did|does|can|could|would|will|have|has)\s+)?(?:you|u)\s+"
    r"(?:still\s+|even\s+)?(?P<verb>remember|recall|know|remembered|noticed)"
    r"|(?P<bare>remember|recall)\b"
    r")"
    r"(?:\s+(?:that|this|it|me|about that|about it|all that))?", re.I)


RESTATED = re.compile(r"^(?:i|im|i'm|ive|i've|id|i'd|ill|i'll|my|we|we're|weve|we've|our)"
                      r"\b", re.I)


CONFIRM_TAG = re.compile(r"[\s,]+(?:right|tho|though|yes|yeah|yep|ok|okay|lol|ha|haha|innit|"
                         r"correct)\s*$", re.I)


SAYS_SOMETHING = re.compile(
    r"\b(?:is|are|was|were|am|im|i'm|been|be|s|have|has|had|got|called|named|live|lives|"
    r"move|moved|moving|start|starts|started|work|works|eat|eats|need|needs|want|wants|like|"
    r"likes|love|loves|prefer|prefers)\b", re.I)


# Words that say how much of the food, not which food it is: "do i eat red meat" is still meat.
NOT_THE_FOOD = frozenset((
    "red", "white", "processed", "raw", "cooked", "fresh", "any", "more", "much", "some", "the",
    "a", "bit", "of", "lot", "still", "either", "anymore", "again", "now", "it", "that", "this",
    "at", "all",
))


# The ask is "do i eat meat", "do i drink alcohol": a yes/no about the rule they gave the store.
# "do i have milk" is not this ask - it is a look in the fridge - so `have` is not read here.
# The `can i eat` shape is left alone - the kitchen entries answer it with the substitutes, which
# is a better answer than the rule said back.
# The lead-in is stripped, then the ask is read: "so do i eat meat" is the same question as
# "do i eat meat", and a person who asks it that way has been mid-conversation for a while.
# "did i eat meat" is a question about the meal they had, not about the rule: the rule cannot
# answer what was on the plate last night, so the ask is the present one only.
EATING_ASK = re.compile(
    r"^\W*do\s+i\s+(?:still\s+|really\s+|actually\s+|now\s+|ever\s+)?"
    r"(?:eat|drink)\s+(.+)$", re.I)


LEAD_IN = re.compile(r"^(?:so|and|but|ok|okay|well|sorry|hey|right|quick one)[, ]+", re.I)


PUTTING_BY = re.compile(r"\b(?:save|saves|saving|saving up|put away|put by|set aside|put aside)\b",
                        re.I)


_NUMBER_WORDS = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen").split()


OWN_ASK = re.compile(
    r"^\W*(?:do|did|does|am|are|is|was|were|have|has|had|can|could)\s+(?:i|we)\b", re.I)


ASK_FILLER = frozenset("""do did does am are is was were have has had can could i we me my
know think say said tell told remember recall really still actually ever even just
much many again any anything something""".split())


NO_THING = frozenset("""you your the and for not out all any get got let put see use try buy pay
one two new old bad big top end way day now why how what who can see say ask own had his her its
our ours mine they them there here then than that this these those very too just also even still
yet ever some but nor same such with from into onto over under off ago lot bit""".split())


AVOID_ADVICE = re.compile(r"\b(?:what|which|anything)\b[^.!?]{0,24}"
                          r"\b(?:avoid|avoids|watch out for|stay away from|stay off)\b", re.I)


BARE_WHAT_I_DO = re.compile(r"^(?:so |and |but )?what (?:do|did) i (?:actually |really |even )?"
                            r"(?:do|say)(?: again)?$", re.I)


JOB_LINE_WORDS = frozenset("""i im am is was be being job jobs work works working as in at on for
with of and the a an it its s my our to here so yeah yes ok okay""".split())


AVOID_REST = re.compile(r"\b(?:avoid|avoids|watch out for|stay away from|stay off)\b(.*)$",
                        re.I | re.S)


EATING = re.compile(r"\b(?:eat|eats|eating|ate|food|foods|meal|meals|cook|cooking|cooked|recipe|"
                    r"recipes|dish|dishes|dinner|lunch|tea\b|breakfast|snack|snacks|restaurant|"
                    r"menu|takeaway|take-away|buffet|party|barbecue|bbq|gluten|dairy|nuts?|"
                    r"allerg\w*|intoleran\w*)\b", re.I)


ALLERGY_SAID = re.compile(r"\b(?:allerg\w*|intoleran\w*|coeliac|celiac)\b", re.I)


NAME_ASK = re.compile(
    r"\b(?:what|which)\s+(?:shall|should|would|could|do|can|will|might)\s+(?:i|we|you)\s+"
    r"(?:call|name)\s+(?:it|him|her|them|this|that|the\s+[\w']+)\b"
    r"|\b(?:any|some)\s+(?:good|nice|ideas?|thoughts?)?\s*(?:for\s+)?(?:a\s+)?names?\b"
    r"|\bnames?\s+(?:ideas?|suggestions?)\b"
    r"|\b(?:name|naming)\s+(?:ideas?|suggestions?)\b"
    r"|\b(?:suggest|give me|throw me|help me (?:pick|choose|find|think of)?)\s*(?:me\s+)?"
    r"(?:a\s+|some\s+)?names?\b"
    r"|\bwhat\s+(?:would|do)\s+you\s+(?:call|name)\b"
    r"|\bhelp me name\b", re.I)


POINTING = re.compile(r"\b(?:this|that|the|my|our|your|his|her|their|a|an)\s+"
                      r"(?:(?:new|little|baby|poor|first|next|wee|small|own)\s+)?"
                      r"([a-z][a-z']{1,})", re.I)


POINTING_ANY = frozenset("""pet pet's baby name names one thing it him her them pup kit
animal""".split())


POINTS_BACK_AT_IT = re.compile(
    r"\b(?:for|to|about|with|on|before|after|from|into|of|at)\s+(?:it|that|this)\b", re.I)


SETTING_OUT = re.compile(
    r"\b(?:leave|leaves|leaving|left|set off|setting off|set out|setting out|travel|travelling|"
    r"traveling|head off|heading off|go|going|get going)\b", re.I)


STUDY_PLAN = re.compile(
    r"\b(?:exam|exams|revision|revise|revising|revised|past paper|past papers|mock|mocks)\b",
    re.I)


_A_DATE_AT_THE_END = re.compile(
    r"^(?P<subject>.*?)\s+(?P<date>(?:in|on|at|next|this)\s+[a-z0-9' ]+\.?)$", re.I)


THEIR_PLACES = frozenset("fridge freezer cupboard cupboards pantry larder".split())


IN_A_PLACE = re.compile(r"\bwhat (?:have|has) (?:i|we) got (?:in|on) (?:the|my|our)\s+(\w+)")


IN_MY_PLACE = re.compile(r"\bwhat(?:'s| is|s)?\s+(?:in|on) (?:the|my|our)\s+(\w+)")


FOR_A_MEAL = re.compile(r"\bwhat (?:have|has) (?:i|we) got (?:for|in) (?:dinner|lunch|tea|supper|"
                        r"breakfast)\b|\bwhat(?:'s| is|s)\s+for (?:dinner|lunch|tea|supper)\b")


WHERE_WORK = re.compile(r"\bwhere\b[^.!?]*\bwork\b|\b(?:which|what)\s+(?:place|company|shop|"
                        r"school|hospital|office|site)\s+do\s+i\s+work\b", re.I)


WORK_CIRCUMSTANCE = frozenset("""
    part full time hours overtime nights days evenings weekends shifts days off call early late
    two three four five six seven all every a few several both
""".split())


DISLIKE_ASK = re.compile(
    r"\?|\b(?:what|how|which|any|ideas?|recipes?|give)\b", re.I)


STOPPED_SAID = re.compile(
    r"^(?:i|we)(?:'ve|ve|\s+have|\s+had)?\s+"
    r"(?:stopped|quit|gave up|given up|packed in|came off|gone off|got off|went off)\b", re.I)


NEGATED_SAID = re.compile(
    r"\b(?:not|never|no longer|any ?more|off|without)\b|n't\b", re.I)


ANY_MORE = re.compile(r"\b(?:any ?more|anymore|no longer)\b", re.I)


A_CLAIM_OF_TELLING = re.compile(
    r"^\W*(?:and\s+|also\s+|so\s+|but\s+|ok(?:ay)?\s+|look\s+|listen\s+|hey\s+)?"
    r"(?:i|we)\s+(?:already\s+|just\s+|did\s+|have\s+|had\s+|definitely\s+)?"
    r"(?:told|tell|mentioned|mention|said|say|talked|talk|spoke)\s+(?:you|u)\b", re.I)


ASKING_ABOUT_IT = re.compile(
    r"^(?:how|what|when|where|which|who|why|do|does|did|can|could|should|would|am|are|is|have|"
    r"has|will|if)\b|\?$|\b(?:do i|should i|can i|am i|did i|have i|will i)\b", re.I)


PLANNING_IT = re.compile(
    r"\b(?:we|i|you)\s+(?:need|needs|want|wants|ought|have to|has to|should)\s+to\b|"
    r"\b(?:thinking about|planning to|going to try|might|maybe|hoping to)\b", re.I)


PLAN_DIETS = frozenset("""keto paleo atkins mediterranean low-carb slimming-world
weight-watchers intermittent-fasting whole30 whole-30 omad carnivore dukan south-beach fast-800
5:2 16:8 4:3""".split())


WAY_OF_EATING = frozenset("""vegan vegetarian veggie pescatarian flexitarian plant-based
raw gluten-free dairy-free""".split())


DIET_NEGATED = re.compile(r"^(?:not|no|never|without|off)\s+(.{2,60})$", re.I)


DIET_NOT_THEIRS = re.compile(
    r"\b(?:my|our|his|her|their)\s+[a-z]+\s+(?:is|was|are|were|has|had)\b|"
    r"\b(?:he|she|they)\b[^.?!]*\b(?:diet|keto|paleo|vegan|vegetarian)\b|"
    r"\b(?:i|we)\s+(?:was|were)\b|\bused to\b|\b(?:last|few)\s+(?:year|years|month|months)\b|"
    r"\byears?\s+ago\b|\b(?:thinking (?:about|of)|considering|might|maybe|planning to|going to try|"
    r"want to try)\b", re.I)


MEAL_WANTED = re.compile(
    r"\bwhat (?:do|should|shall|can|could|will) i (?:eat|have|cook|make|do for dinner)\b|"
    r"\bwhat'?s for (?:dinner|lunch|tea|supper|breakfast)\b|"
    r"\bwhat can we (?:eat|have|cook|make)\b|"
    r"\b(?:give|suggest|recommend) me something to eat\b", re.I)


AGE_COMPARE = re.compile(
    r"\bwho(?:'s|s| is| was)?\s+(?:the\s+)?(?:older|younger|eldest|oldest|youngest)\b|"
    # "which one is older", "which of them is younger": the same ask as a choice out of two,
    # and it fell to the search hedge the same way. The person has just been told about a pair.
    r"\bwhich(?:\s+one|\s+of\s+(?:them|those|the\s+two))?\s+(?:is\s+|was\s+)?(?:the\s+)?"
    r"(?:older|younger|eldest|oldest|youngest)\b|"
    r"\b(?:am|is|are|was|were)\b[^.!?]{0,40}\b(?:older|younger) (?:than )?\b|"
    r"\bhow (?:much|many years)\s+(?:older|younger)\b|"
    r"\b(?:older|younger) (?:than )?(?:me|him|her|them)\b", re.I)


BARE_AGE_WHO = re.compile(
    r"^\W*(?:so|and|ok|okay|but|well)?[\s,]*who(?:'s|s| is| was)?\s+(?:the\s+)?"
    r"(?:older|younger|oldest|youngest|eldest)\b[^.?!]*$", re.I)


# The same bare ask as a choice between two: "which one is older", "which of them is younger".
# The person who says this has just been told about two people and wants the two numbers put
# against each other, and it is the same question as "who is older" however it is worded.
# The gap asked for with a pronoun instead of a name: "how much older is he". It is read with
# the two people the store holds, which is the only pair the line can be about.
THE_AGE_GAP = re.compile(r"\bhow (?:much|many years)\s+(?:older|younger)\b", re.I)


WHICH_ONE_AGE_WHO = re.compile(
    r"^\W*(?:so|and|ok|okay|but|well)?[\s,]*which(?:\s+one|\s+of\s+(?:them|those|the\s+two))?"
    r"(?:'s|s| is| was)?\s+(?:the\s+)?(?:older|younger|oldest|youngest|eldest)\b[^.?!]*$", re.I)


PEOPLE_WORDS = re.compile(r"\b(?:she|her|hers|he|him|his|they|them|us|we|me|i|myself|mine)\b", re.I)


SOMEONE_ELSE = re.compile(r"\b(?:she|her|hers|he|him|his|they|them|us)\b", re.I)


WHICH_FIRST_ASK = re.compile(
    r"\b(?:which|who|whose|what)\s+(?:one\s+|ones\s+|of\s+them\s+|of\s+those\s+|of\s+the\s+two\s+)?"
    r"(?:is\s+|are\s+|comes?\s+|come\s+|happens?\s+|happen\s+|would\s+be\s+|will\s+be\s+)?"
    r"(?:up\s+)?(?:first|sooner|earliest|earlier)\b", re.I)


WHICH_FIRST_WORDS = frozenset("""which who whose what one ones of them those the two is are come
    comes happen happens would will be up first sooner earliest earlier next then so do does you
    think again now really actually please and but well hmm oh ah then just it that this both""".split())


MONTH_SAID = re.compile(
    r"\b(?:in|on|of|by|until|till|before|after|from|during|early|late|mid|next|this|that|the)\s+"
    r"(?:" + MONTH_ALT + r")\b|\b(?:" + MONTH_ALT + r")\s+\d{1,2}(?:st|nd|rd|th)?\b|"
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:" + MONTH_ALT + r")\b", re.I)


LIMIT_LIKE = re.compile(
    r"\b(?:pregnan\w*|expecting|we'?re having a baby|having a baby)\b"
    r"|\ballerg\w*|\bintoleran\w*|\bcoeliac\b|\bceliac\b|\bibs\b|\bcrohn'?s?\b"
    r"|\bdiabet\w*|\bgout\b|\breflux\b|\bhigh cholesterol\b|\bkidney\b"
    r"|\bvegan\b|\bvegetarian\b|\bpescatarian\b|\bon a diet\b|\b\w+[- ]free\b"
    r"|\b(?:can'?t|cannot|can not|don'?t|dont|do not|never|no longer|stopped|avoid\w*)\b"
    r"[^.!?]{0,24}?\b(?:eat|drink|have|haveing|having|touch|take|dairy|meat|gluten|sugar|"
    r"alcohol|salt)\b", re.I)


MORE_FOODS = frozenset("""sesame soya soy soya-bean mustard celery sulphites lupin molluscs
shellfish kiwi strawberry strawberries banana bananas pineapple tomato tomatoes chocolate
sugar caffeine msg sulphite""".split())


# A question can be asked without a question mark, and then the fact in front of it is only the
# context for it: "my sister is veggie and she's coming to dinner, what can i cook" ends on the
# ask, and the store's receipt for the fact ("Your sister is veggie.") answers something nobody
# asked while the card that answers the dinner waits behind it (hf:lewtun, #general 126189).
AN_ASK_AT_THE_END = re.compile(
    r"(?:^|[\s,;])(?:what|which|how|where|when|who|why)\b[^.!?]*$"
    r"|(?:^|[\s,])(?:can|could|should|shall|would|will|do|does|did|is|are|am)\s+"
    r"(?:i|we|you|he|she|they|it)\b[^.!?]*$", re.I)


# The composer's own way of saying it has nothing: no receipt is worth less than this.
HEDGED = re.compile(
    r"\b(?:don'?t know enough|beyond what i know|not sure about that one|"
    r"rather not guess|a (?:quick )?search\b|searching for it|look it up)\b", re.I)


A_ONE_PERSON_WORD = frozenset("""child kid baby twin parent grandchild grandparent boy girl lad
lass teenager""".split())


NOT_A_NAME = frozenset("""a an the not no still same old different changed change hard difficult
important complicated long short funny strange odd weird right wrong fine ok okay good bad""".split())


def _named_back(who, line):
    """"she doesnt eat meat" is said back as "your sister doesnt eat meat", verb and all.

    The pronoun carries its own verb when it is written as one word ("shes 32" holds "is"), so
    dropping it whole would leave "your sister 32": the verb is put back in words.
    """
    def whose(match):
        word = match.group(0).lower()
        head = "your " + who
        if word.endswith("re"):
            return head + " are"
        if word.endswith("s") and not word.endswith("ss"):
            return head + " is"
        return head

    def belonging(match):
        # "her birthday is in june" is the sister's birthday, and a bare "her" says nothing in a
        # reply that has just changed the subject back to her.
        return "your " + who + ("'" if _plural_person(who) else "'s")

    line = str(line or "")
    # A line that already names the person further on ("they said your mum is 72") is not theirs
    # to rewrite at the front: "your mum said your mum is 72" says one person twice and reads as
    # two. The words they used are said back as they were.
    if not re.search(r"\byour\s+" + re.escape(who) + r"\b", line, re.I):
        line = re.sub(r"^(?:and\s+)?(?:she|he|they)(?:'s|'re|s|re)?\b", whose, line, re.I)
        line = re.sub(r"^(?:and\s+)?(?:his|her|their)\b", belonging, line, re.I)
    return line


def _a_relation_in(line):
    """The relation a line is about, read loosely: a noun right after it is a thing of theirs.

    "my dad had a heart attack" names the dad, which the strict reader of a person misses (the
    word after "dad" is "had", so it cannot tell the person from a thing of theirs). This reading
    is only used to follow who a "she"/"he" line is about, so it can afford to be loose: a noun
    straight after the relation ("my mums car") still takes the word away from the person.
    """
    low = str(line or "").lower()
    for relation in extract.RELATIONS:
        for hit in re.finditer(r"\b" + relation + r"s?\b", low):
            rest = low[hit.end():]
            if rest.startswith("'s") or rest.startswith("s'"):
                rest = rest.split("'", 1)[1][1:]
            words = rest.split()
            if words and words[0].strip(".,!?;:") in extract.COMPOUND_AFTER:
                continue
            return relation
    return ""


def _date_written_as_a_date(value):
    """A month inside a date is written with a capital: "4 may" is said "4 May"."""
    said = str(value or "")
    for month in extract.MONTHS:
        said = re.sub(r"\b" + month + r"\b", month[:1].upper() + month[1:], said, flags=re.I)
    # A day kept as an ordinal keeps it, and a date said in a sentence needs the word that makes
    # it one: "4th may" is said "the 4th of May", never "the 4th May".
    ordinal = re.match(r"^(\d{1,2}(?:st|nd|rd|th))\s+([A-Z][a-z]+)$", said)
    if ordinal:
        said = "the %s of %s" % (ordinal.group(1), ordinal.group(2))
    return said


def _pronoun_person(text, memory):
    """Who "her"/"him"/"them" is in this line: the person last named, when the word fits them.

    "him" after only a mum was mentioned names nobody: answering with the mum's facts is a wrong
    answer, which is worse than leaving the line to whoever else can answer it. A plural person
    ("my parents") takes "them" and "they".
    """
    low = str(text or "").lower()
    if not re.search(r"\b(?:her|him|them|she|he|they)\b", low):
        return ""
    who = _person_from_pronoun(text, memory)
    if not who or _plural_person(who):
        return who
    if re.search(r"\b(?:her|she)\b", low) and who not in extract.SHE:
        return ""
    if re.search(r"\b(?:him|he)\b", low) and who not in extract.HE:
        return ""
    return who


OWNED_ASK = re.compile(
    r"\b(?:what|which)\s+(?P<a>[a-z][a-z-]*)\s+(?:do|did|does)\s+(?:i|u|you)\s+"
    r"(?:drive|ride|use|have|own)\b"
    r"|\b(?:what|which)\s+(?P<b>[a-z][a-z-]*)\s+(?:have|has)\s+(?:i|u|you)\s+"
    r"(?:got|had|have|owned|driven|ridden|used)\b"
    r"|\b(?:what|which)\s+(?P<c>[a-z][a-z-]*)\s+(?:is|was)\s+mine\b"
    r"|\b(?:what|which)\s+(?P<d>[a-z][a-z-]*)\s+am\s+i\s+"
    r"(?:driving|riding|using|in)\b"
    r"|\b(?:do|can|could|did)\s+(?:u|you)\s+(?:remember|recall|know)\s+(?:what|which)\s+"
    r"(?P<e>[a-z][a-z-]*)\s+(?:i|u|you)\s+(?:drive|ride|use|own|have)\b"
    # ...and the same ask with the frame already off it: the store reads "do you know what car i
    # drive" by its own words once the knowing frame comes away, which leaves "what car i drive".
    r"|\b(?:what|which)\s+(?P<f>[a-z][a-z-]*)\s+(?:i|u|you)\s+(?:drive|ride|use|own)\b", re.I)


def _a_that_fits(name):
    """The article a name takes: "an iPhone 13", "a Pixel", "a BMW", "an Audi".

    A name written in capitals is said letter by letter, so it takes "a" whatever its first
    letter looks like ("a BMW", "a VW"), and every other name takes the article of its sound.
    """
    first = str(name or "").split()[0] if str(name or "").split() else ""
    if len(first) > 1 and first.isupper():
        return "a"
    return "an" if first[:1].lower() in "aeiou" else "a"


def _a_list_of_clauses(clauses):
    """"Tom is 8", "Ada is 5" reads "Tom is 8 and Ada is 5", and three read with a comma."""
    said = [str(clause) for clause in clauses if str(clause)]
    if len(said) < 3:
        return " and ".join(said)
    return ", ".join(said[:-1]) + " and " + said[-1]


def _the_person_called(memory, line):
    """The person whose name the line asks about, or "".

    "my son is called ada" files the name with the son, so "what do you know about ada" has a
    person behind it even though "ada" is not a relation word. A name the chat never gave is no
    person at all, which leaves the ask to the modules that know about the world.
    """
    for match in re.finditer(r"\babout\s+([a-z][a-z'-]{1,20})\b", str(line or ""), re.I):
        word = match.group(1).lower()
        if word in extract.RELATIONS or word in extract.ALONE_PERSON:
            continue
        for entry in others(memory):
            name = str(entry.get("name") or "").strip().lower()
            if name and name == word:
                return str(entry.get("who") or "")
    return ""


def _covers(said, clauses):
    """True when one line already says the facts: a number counts as a word to be found.

    "your son is allergic to nuts" says the allergy but not the age, and the two are different
    answers, so the line is only the whole reply when every clause is in it.
    """
    seen = _tokens(said)
    return all(_tokens(clause) <= seen for clause in clauses)


def _tokens(text):
    """The words of a line to look for, with its numbers kept - content() drops them.

    The person's word is trimmed of the bare "s" it is typed with ("my mums 72"), because the
    store's own sentence uses the word without it ("your mum is 72") and the two are one fact.
    """
    words = set(content(text)) | set(re.findall(r"\d+", str(text or "")))
    return {word[:-1] if word.endswith("s") and word[:-1] in extract.RELATIONS else word
            for word in words}


def _said_everything(answer, memory):
    """True when a reply of this chat already carried every word of this one: nothing more to tell.

    Not only the last reply: "what do you know about my son" then "how old is he" then "what else
    do you know about him" asks the same person's facts a second time, and the reply that said
    them is two turns back. Any reply of the chat counts, so the person is not told the same
    sentence twice.
    """
    mine = _tokens(answer)
    if not mine:
        return False
    for turn in _every_line(memory):
        before = str(turn.get("bot") or "")
        if before and mine <= _tokens(before):
            return True
    return False


WAS_A_STATE = re.compile(
    r"\b(?:was|were|had\s+been|has\s+been|have\s+been|used\s+to\s+be)\s+"
    r"(?:still\s+|also\s+|once\s+|again\s+)?"
    r"(?:pregnant|expecting(?:\s+a\s+baby)?|breastfeeding|nursing\s+a\s+baby)\b", re.I)


PET_PART_ASK = re.compile(
    r"\b(?:his|her|its|their|my|our|the)\s+(?:age|breed)\b"
    r"|\bhow old (?:is|was) (?:he|she|it|they)\b"
    r"|\bwhat (?:breed|kind|sort|type)\b|\bwhich breed\b", re.I)


BREED_WORD = re.compile(r"\bbreed\b|\bwhat (?:kind|sort|type)\b|\bwhich breed\b", re.I)


def _a_number(value):
    """A figure the fact reader gave as text, as a number: "12" and 12 are the same age."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return value


AN_ANIMAL = re.compile(
    r"\b(?:cat|cats|kitten|kittens|dog|dogs|puppy|puppies|pup|rabbit|bunny|hamster|gerbil|"
    r"guinea pig|parrot|budgie|bird|fish|horse|pony|ferret|tortoise|snake|lizard|pets?)\b", re.I)


A_SMALL_UNIT = re.compile(r"\b(\d{1,2})\s*(weeks?|months?)\b", re.I)


def _a_pronoun_word(text):
    """The first pronoun in the line that points at a person: "she", "he" or "they".

    The pronoun arrives with its verb joined on more often than not - "shes 4 months", "hes 7",
    "theyre twins" - and a word boundary after "she" never matches inside "shes", so the line
    read as naming nobody and the age it gave was lost.
    """
    match = re.search(r"\b(she|he|they)(?:'s|s|'re|re)?\b", str(text or "").lower())
    return match.group(1) if match else ""


def _someone_else_named(low, memory):
    """Who else the line is about, as the store files them; "" when the line names nobody.

    The person is the one the ask names ("my son", "your mum"); a bare "she"/"he" points at the
    person the last fact was about, which is the one the user just gave a fact about. A line with
    no person in it at all ("can i eat satay", after "my wife is allergic to nuts") is about the
    person typing, so it names nobody here.

    The longest name wins: "mother in law" is not her mother, and a line that says the two words
    has to reach the same person the fact was filed against.
    """
    names = [str(known.get("who") or "").strip() for known in others(memory)]
    names = [name for name in names if name] + list(extract.RELATIONS)
    # Longest first, so the two-word relation beats the word it opens with ("mother in law" and
    # not "mother"), and a relation the store already keeps by name is found as it was filed.
    # Ties are broken by where the name is in the line, then by the word itself. `set` order is
    # the hash order, so two names of the same length ("can my dad eat nuts my mum is
    # vegetarian") made the answer a coin flip between the same process runs: one run answered
    # about the mother, the next answered nothing at all.
    found = []
    # People type the apostrophe, leave it out, or use the curly one, and the store files a pair as
    # "partner's mum": a line that says "my partners mum" has to reach the person the same way the
    # reply names her, so the search is made without apostrophes on both sides.
    flat = low.replace("'", "").replace("\u2019", "")
    for name in set(names):
        match = re.search(r"\b" + re.escape(name.replace("'", "").replace("\u2019", ""))
                          + r"s?\b", flat)
        if match:
            found.append((-len(name), -match.start(), name))
    if found:
        return min(found)[2]
    if THEM.search(low):
        return _person_from_pronoun(low, memory)
    return ""


_SAME_FACT_PERSON = _RELATION + "|kids|children|child|boys|girls"


SAME_FACT_ABOUT = re.compile(
    r"^(?:and |so |oh |but |ok |okay )*"
    r"(?:same for )?"
    r"(?:(?:my|our) (?P<who>" + _SAME_FACT_PERSON + r")"
    r"|(?:the )?(?P<more>" + _SAME_FACT_PERSON + r")s?)"
    r"(?: (?:is|are|does|do|has|have))?"
    r"(?: (?P<same>too|as well|also|the same|same|neither))?$", re.I)


NEGATIVE_TAIL = frozenset("""either at all as well really actually""".split())


SAME_FACT_AGAINST_PRONOUN = re.compile(
    r"^(?:and |so |oh |but |ok |okay |no,? |actually )*(?P<pron>she|he|they)"
    r"(?: is| are|'s|s)(?P<neg>nt|n't| not)\b(?P<rest>.*)$", re.I)


SAME_FACT_AGAINST = re.compile(
    r"^(?:and |so |oh |but |ok |okay )*(?:(?:my|our) (?P<who>" + _SAME_FACT_PERSON + r")"
    r"|(?P<more>" + _SAME_FACT_PERSON + r")s?) (?:is|are)"
    r"(?P<neg>nt|n't| not)\b(?P<rest>.*)$", re.I)


_SHE = frozenset("""mum mom mother mum-in-law wife girlfriend sister daughter aunt grandma
    grandmother granny nan nana niece fiancee""".split())


_HE = frozenset("""dad father husband boyfriend brother son uncle grandad grandfather grandpa
    nephew fiance""".split())


WHAT_ABOUT_A_FOOD = re.compile(
    r"^\W*(?:and\s+|what\s+about\s+|how\s+about\s+|ok\s+with\s+)?([a-z][a-z' -]{2,30})\s*\??$",
    re.I)


# A person named only by a pronoun, when the chat holds nobody for it to be. The pronoun is said
# back rather than replaced with "they", because the person used it and the store has heard it.
THE_PRONOUN = re.compile(r"\b(she|her|hers|he|him|his|they|them|their)\b", re.I)


# A limit asked for rather than advised about. The store was never told about the person, so the
# only true answer is that nothing is kept - but a question about the world is not that question:
# "how do i introduce allergens to my baby" and "how much notice does he have to give" are jobs for
# the knowledge base, and "what does he eat" is answered better by "you would have to ask him".
# What is left is the ask for the fact itself: an allergy or a diet named outright, or a line that
# says it is asking again ("what was she allergic to again", "what did i say she doesnt eat").
A_LIMIT_NAMED = re.compile(r"\b(?:allerg\w*|allergies|vegan|vegetarian|pescatarian|coeliac|celiac|"
                           r"intolerant|intolerance|di(?:ae)?t|avoid\w*)\b", re.I)


ASKING_AGAIN = re.compile(r"\b(?:again|remind me|did i (?:say|tell|mention)|what did i (?:say|tell|"
                          r"mention)|what i (?:said|told|mentioned))\b", re.I)


ADVICE_NOT_A_FACT = re.compile(r"\bhow\b|\bwhat should\b|\bwhat can we\b|\bwhere\b|\bwhen\b"
                               r"|\bwhy\b|\bhow much\b", re.I)


# The line that says the limit and asks about it in one breath - "my son is 7 and has a nut
# allergy, what is he allergic to" - states a fact, so it is not a line with nothing behind it:
# the fact is kept from the same line, and the store answers from what it has just been told.
# "does she have any allergies" says the same words as a statement of one and asks a question
# instead: the "have" is the question's auxiliary, not the person's. Read as a statement, the line
# kept its hedge even though it names the limit and asks nothing else.
A_HAVE_QUESTION = re.compile(r"\b(?:does|do|did)\s+\w+\s+(?:have|has|had|got)\b"
                             r"|\b(?:has|have)\s+(?:she|he|they|anyone|anybody|your)\b")


STATES_A_LIMIT = re.compile(r"\b(?:has|have|had|got)\b[^.!?]{0,24}?\ballerg\w*"
                            r"|\bis\s+allergic\b|\bare\s+allergic\b"
                            r"|\b(?:is|are|am)\s+(?:a\s+)?(?:vegan|vegetarian|coeliac|celiac)\b",
                            re.I)


# The same words inside a question: "remind me what hes allergic to" is folded to "what he is
# allergic to", which has "is allergic" in it and states nothing. Only a line without an
# interrogative in front of the verb is telling the store something.
A_ASK_FRAME = re.compile(r"\b(?:what|which|who|tell me|remind me|if|whether|wonder|know)\b"
                         r"[^.!?]{0,24}?\b(?:is|are|was|were|has|have|does|do|can)\b", re.I)


A_MEAL_WORD = re.compile(r"\b(?:cook|cooking|cooked|recipe|recipes|meal|meals|dinner|tea|lunch|"
                         r"breakfast|snack|menu|shop|shopping|bake|baking)\b", re.I)


A_BIRTHDAY_PLAN = re.compile(r"\b(?:birthday|bday|dob|date of birth)\s+(?:is\s+|was\s+|on\s+|in\s+)?"
                             r"([^,.;!?]{2,28})", re.I)


_A_RELATION = ("(?:" + "|".join(sorted(extract.RELATIONS, key=len, reverse=True)) + r")"
               + extract.IN_LAW)


A_RELATIONS_BIRTHDAY = re.compile(
    r"\b" + _A_RELATION + r"(?:'s|s)?\s+"
    r"(?:birthday|bday|dob|date of birth)\b", re.I)


NO_CAP = frozenset(("diesel", "petrol", "hybrid", "electric", "estate", "hatchback", "saloon",
                    "coupe", "convertible", "automatic", "manual", "classic"))


CAR_DESCRIBED = frozenset("""old new used secondhand second-hand little small big cheap tidy rusty
yellow red blue white black silver grey gray green other spare reliable""".split())


WHOSE_BIRTHDAY = re.compile(
    r"\b(?:when|what\s+date)(?:'s|s)?\s+(?:is|was|are)?\s*(?:it\s+)?"
    r"(?:(?:my|our)\s+(?P<who>" + _A_RELATION + r")s?"
    r"|(?P<pronoun>his|her)"
    r"|(?P<name>[a-z][a-z'\u2019-]+)(?:'s|s))\s*"
    r"(?:birthday|bday|dob|date\s+of\s+birth)\b", re.I)


ALLERGY_IN_THE_WORLD = re.compile(r"\bwhy\s+(?:do|does|did|would|are|is|can)\b|"
                                  r"\bwhat\s+causes?\b|\bhow\s+common\b|"
                                  r"\bwhat\s+are\s+allergies\b", re.I)


# A how-to at the front of a line is a request for advice, not a recall of a fact: "how do i
# budget" was read as the budget fact and answered "You haven't told me a budget." to a person
# asking how to make one, when the knowledge answer for budgeting was there to give. The diet
# branch has kept this guard (`DIET_HOW_TO`) since the same bug in front of "my diet"; the other
# facts needed it too. The frame has to be at the front, because a fact question can carry the
# same words later on ("whats my budget", "how much can i spend").
#
# The frame is a how-to of *doing* the thing. A question of how much, how many or how long is a
# quantity ask that happens to start with "how", not a how-to: "how much do i spend" after "my
# budget is 200 a month" wants the 200 back, so the quantity words are not a frame at all.
A_HOW_TO_ASK = re.compile(r"^\s*(?:so|and|ok|okay|hi|hello)?[, ]*\s*"
                          r"(?:how (?:do|can|could|should|would|might|to)\b|"
                          r"ways? to\b|any (?:tips|advice|ideas|suggestions|ways)\b|"
                          r"tips for\b|help me\b|what can i do\b|what should i do\b)", re.I)


# ...unless they are asking to be reminded of the figure they gave: "how do i know my budget
# again" is a recall with a how-to shape, and the how-to answer ("write down what comes in each
# month") is advice about budgeting, not their number. The recall word decides - and "know" is
# one of them, because "how do i know my weight" is a how-to of knowing, which is a recall, while
# "how do i lose weight" is a how-to of doing and stays advice.
A_RECALL_WORD = re.compile(r"\bagain\b|\bremind me\b|\bdid i (?:say|tell|mention)\b|"
                           r"\bwhat did i say\b|\bdo you remember\b|\byou know my\b|"
                           r"\bwhat was my\b|\bwhats my\b|\bwhat's my\b|\bknow\b", re.I)


ADVICE_ASK = re.compile(
    r"\bdo i (?:need|have) to\b|\bshould i\b|\bhow (?:often|much|long|many)\b|"
    r"\bwhen (?:should|do|can|must) i\b|\bcan i\b|\bis it (?:ok|okay|fine|safe)\b|"
    r"\bwhat (?:should|can|could) i (?:do|feed|give|use|buy|get)\b|\bhow (?:do|can) i\b")


FIGURE_REPEAT = re.compile(
    r"\b(?:how long|how many|how often|how soon|what time|what temperature|"
    r"which temperature|what setting|how hot|when)\b")


ANSWER_MODULES = frozenset(("answers", "loss", "grief", "safety", "urgent"))


NOD_WORDS = frozenset("""thanks ta thx ty thank you cheers much so very really that this helps
                         helped for the lot got it ok okay k kk great nice brilliant awesome
                         perfect lovely cool fair enough right alright indeed yes yeah yep
                         sure fine good ah oh""".split())


HELLO_FILLER = frozenset("""there all everyone everybody both you folks guys again friend
friends mate team""".split())


THEIR_OWN_ASK = re.compile(r"\b(?:i|me|my|mine|we|our|ours)\b", re.I)


ASKS_IN_LINE = re.compile(r"[,;:\u2013\u2014-]\s*(?:what|whats|why|how|hows|when|where|wheres|who|"
                          r"which|whose|can|could|should|would|do|does|did|is|are|was|were|will|"
                          r"shall|have|has)\b", re.I)


CORRECTS = re.compile(r"\b(?:rather than|instead of|scratch that|or rather)\b|"
                      r"\bi (?:meant|mean)\b|\bnot\s+(?:the\s+)?\w+\s*[.!]?$", re.I)


SAID_ABOUT = re.compile(
    r"\bwhat (?:was|were|am|are) (?:i|we) (?:saying|talking|chatting|on)\b[^.?!]*\babout\b",
    re.I)


DENIAL = re.compile(
    r"\bhaven't said anything\b|\bhaven't mentioned\b|\bnothing comes to mind\b", re.I)


REFLEXIVE = frozenset(("myself", "yourself", "ourselves", "themselves"))


JUDGING = frozenset((
    "wrong", "bad", "good", "best", "worst", "right", "nice", "like", "dislike", "much", "many",
    "long", "often", "soon", "far", "big", "small", "else", "other", "another", "next", "first",
    "last", "again", "exactly", "actually", "really", "truly"))


A_ROLE = frozenset((
    "guest", "guests", "person", "people", "someone", "somebody", "man", "woman", "guy",
    "bloke", "lad", "friend", "colleague", "member", "kid", "child", "children", "folk"))


PRONOUN_ASK = re.compile(r"\b(?:it|its|that|this|them|those)\b")


TAGS = (
    ("holiday", re.compile(r"\b(?:going|gone|flew|flying|off|travell?ing|travel)\s+to\s+"
                          r"(?!the\b|a\b|an\b|my\b|our\b|his\b|her\b|their\b|work\b)"
                          r"|\babroad\b|\bholiday\b", re.I)),
)


A_PROGRAMME_IS_ON = re.compile(
    r"\b(?:is|was|are|were)\s+(?:on|back on)\s+(?:tonight|now|tv|telly|later|this evening|"
    r"last night|tomorrow|at \d|bbc|itv|channel|netflix|prime)\b", re.I)


PERSON_STANDS = re.compile(
    r"(?:^\s*|[,.;:!?)—]|\b(?:is|are|was|were|has|have|had|does|do|did|can|could|will|would|"
    r"shall|should|might|must|needs?|needed|wants?|wanted|says?|said|said|called|rang|phoned|"
    r"texted|loves?|likes?|hates?|came|comes?|coming|went|goes|going|got|gets|getting|thinks?|"
    r"thought|knows?|knew|feels?|felt|feeling|worried|ill|unwell|poorly|sick|poor|well|fine|"
    r"who|that|which|and|too|as|again|now)\b|$)", re.I)


KINDS = (
    ("trip", frozenset("trip trips holiday holidays vacation getaway break travel journey flight"
                        " abroad".split())),
    ("job", frozenset("job jobs work career shift shifts employment".split())),
    # What they eat is said in the food itself, never in the word: nobody says "my food is
    # vegetarian", they say "im vegetarian" or "i dont eat meat", and the ask "what did i say
    # about food" was answered "You haven't said anything to me about food yet." one line later.
    ("food", frozenset("food foods diet meals meal dinner tea supper lunch breakfast eating"
                       " cooking".split())),
    # Where they live is a kind of its own, and a move says it as well as the word does: "we live
    # in leeds" then "we moved to york last year" is one fact in two lines, and the ask "what did
    # i say about where i live" quoted "we live in leeds" - the home they had just left - because
    # only the first line uses the word "live". The newest line of the kind is the one the chat is
    # on, and the store already keeps the city the last one named.
    ("home", frozenset("live lives living home house city town address moved move moves"
                       " moving".split())),
)


SAYS_A_TRIP = re.compile(r"\b(?:holidays?|vacation|getaway|abroad|trips?|travell?ing|flight|flying|"
                         r"cruise|week away)\b", re.I)


NOT_A_PLACE_IN = frozenset("""bed pain limbo prison hospital hospice traction tears denial
hiding isolation quarantine plaster shock mourning""".split())


SAYS_A_STAY = re.compile(
    r"\b(?:a |the )?(?:few |couple of |two |three |four |five )?(?:days?|nights?|weeks?|weekend)"
    r"\s+(?:away\s+)?in\s+(?:(?:the|a|an)\s+)?(?P<place>[a-z]{3,})", re.I)


SAYS_A_JOB = re.compile(r"\b(?:job|jobs|work|working|career|shift|shifts|office|employ\w*|"
                        r"promotion|interview|colleagues?)\b", re.I)


SAYS_FOOD = re.compile(
    r"\b(?:eat|eats|eating|eaten|ate|drink|drinks|drinking|drank)\b|"
    r"\b(?:vegetarian|vegan|pescatarian|diet|allerg\w+|intoleran\w+|gluten|dairy|sugar|meat|"
    r"fish|carbs?|keto|fasting|booze|alcohol)\b|"
    r"\b(?:cook|cooks|cooking|cooked|bake|baking|roast|recipe)\b", re.I)


def _kind(thing):
    """The kind of thing an ask names, or "" when the word is a thing of its own."""
    for kind, words in KINDS:
        if thing in words:
            return kind
    return ""


# The echo of a line that was itself a telling: "you told me about your mum". A frame on top of it
# says the telling twice, and the echo already carries who told whom.
TELLING_ALREADY = re.compile(r"^you (?:told me|said to me|mentioned to me)\b")


A_BARE_PUT_RIGHT = re.compile(
    r"^\s*(?:sorry|no|nah|actually|oh|wait|hang on|hold on|i mean|my mistake|silly me|"
    r"correction)[\s,]*"
    r"(?:(?:its|it's|it was|make that|make it|i mean|should be|thats|that is)\s+)?"
    r"(?:about\s+|only\s+|just\s+)?"
    r"(?P<value>\d[\d,]*(?:\.\d+)?"
    r"(?:\s+and\s+(?:an?\s+)?(?:half|quarter))?)"
    r"(?:\s*(?:%|percent|per\s?cent|pounds?|quid|grand|k|stone|kg|miles?|mph|hours?|"
    r"minutes?|mins?|a\s+(?:month|week|year|day|night|person|guest|head))s?)?"
    r"\s*(?:[,!.]|\b(?:sorry|thanks|actually|i got it wrong|got it wrong|my mistake|silly me|"
    r"i think|i mean|then|right)\b)*\s*$", re.I)


A_FIGURE = re.compile(r"(?<![\w.,£$])(\d[\d,]*(?:\.\d+)?)")


# "Again" is the licence to cross a turn that changed the subject: the person is pointing at
# something they know they said, so an aside in between is not the chat moving on.
ASKING_AGAIN = re.compile(r"\bagain\b|\bremind me\b", re.I)


THING_POINTER = frozenset(
    "the a an my your our their his her its it this that of on in at for to with about".split())


SMALL_TALK_ONLY = frozenset("""hi hello hey morning afternoon evening night thanks thank cheers
bye goodbye ok okay cool nice great good fine yeah yes no nah lol haha hmm well anyway
brilliant lovely""".split())


SUMMARY_FILLER = frozenset("""you your yours i me my mine and so but it its it's is was are were
be been am do did does have has had to of in on at for with that this these those the a an
too also just really very quite still now then there here""".split())


NAME_SAID = re.compile(r"\b(?:called|named|name(?:'s)? is|goes by)\s+([A-Za-z][\w'\u2019-]*)", re.I)


NOT_A_NAME = frozenset("""a an the that this it him her them me you us someone something
somebody anyone anybody everyone nobody""".split())
