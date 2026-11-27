"""Part 4 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from . import (LINGERED_LINE)
from .badnews import (reads_as_bad_news)

from .fallback_data import (
    FORGET_A_THING,
    INVITE_ACTIVITY,
    INVITE_FILLER,
    INVITE_NEVER,
    INVITE_PRONOUN,
    NARROW_WORDS,
    NO_WORDS_ASKING,
    NO_WORDS_AT_THE_CARE,
    NO_WORDS_SOMEONE,
    NO_WORDS_STUCK,
    ONLY_FRONT,
    _ISSUER,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    THE_DAY,
    THE_DAY_AHEAD,
    _LANDED,
)
from .fallback_part_01 import (
    _matchable, _plain,
)
from .fallback_part_03 import (
    CLOSE_OWNER, NOT_THEIR_NEWS, NOT_YET_NEWS, SERIOUS_NEWS,
)


def reads_as_someone_close_is_ill(clean):
    """Whether a cleaned, lowercased line is serious news about someone the person loves.

    Only the news itself: a named serious condition, an operation, or the hospital. The pool that
    answers it asks how the person is doing, so a line that is only a cold or a rash must not
    reach it, and neither must a line where the words belong to a charity run or a hospital job.
    """
    if not clean or NOT_THEIR_NEWS.search(clean):
        return False
    if not CLOSE_OWNER.search(clean):
        return False
    serious = SERIOUS_NEWS.search(clean)
    if not serious:
        return False
    doubt = NOT_YET_NEWS.search(clean)
    if doubt and doubt.start() < serious.start():
        return False  # afraid of it, not told it: nothing has landed
    return True


# Who it is about: a person of theirs, or a person by pronoun. "I left home at sixteen" is the
# speaker's own past and gets nothing from this, and a pet is not leaving home either.
LEAVING_A_PERSON = re.compile(
    r"\b(?:my|our)\s+(?:son|daughter|boy|girl|kid|kids|children|child|eldest|youngest|"
    r"stepson|stepdaughter|mum|mom|mother|dad|father|parents|sister|brother|best\s+friend|"
    r"friend|mate|neighbour|neighbor|grandson|granddaughter|grandchild|nan|gran|aunt|uncle|"
    r"cousin|husband|wife|partner|boyfriend|girlfriend|niece|nephew)\b|"
    r"\b(?:he|she|they|the\s+kids|the\s+children|everyone)\b", re.IGNORECASE)


# Whether the leaving has already happened. The two pools above are worded for a plan - "how far
# away is it going to be?", "before they go" - and "my eldest left home last month" is not a plan:
# asking somebody whose son went a month ago how far away it is going to be reads as a bot that
# did not hear the tense. A past marker is the whole test, and it is a marker of the *leave*: "my
# daughter has been unwell" is not this, so the words were chosen for going and not for having.
THE_LEAVE_HAS_HAPPENED = re.compile(
    r"\b(?:left|moved|went|gone|flew|flown|relocated|emigrated)\b|"
    r"\b(?:has|have|had|she's|hes|he's|they've|theys|we've|was|were)\b[^.,;!?]{0,16}\b(?:left|"
    r"moved|gone|flew|flown|relocated|emigrated)\b",
    re.IGNORECASE)


# The same words in a line that wants help with it ("how do i help my daughter move out"), one
# that is asking whether they should go at all, one where the person is arriving rather than
# going, and one about a child starting school - that last has its own answer in the knowledge
# base and is not somebody leaving home.
NOT_LEAVING_ANYONE = re.compile(
    r"\bhow\s+(?:do|can|should|could|would|might|shall)\s+i\b|\bhow\s+to\b|"
    r"\bwhat\s+should\s+i\b|\bany\s+(?:tips|advice|ideas)\b|\bany\s+idea\b|"
    r"\bwhat\s+do\s+you\s+think\b|\bwhat\s+would\s+you\b|"
    r"\bmoving\s+in\s+with\b|\b(?:coming|moved|moving)\s+(?:in|back)\b|"
    r"\bstaying\s+with\s+(?:us|me)\b|\bstay(?:ing|s|ed)?\s+with\b|"
    r"\b(?:starts?|starting|started)\s+(?:school|nursery|reception|primary|year\s+one)\b",
    re.IGNORECASE)


FORGETS_AGAIN = re.compile(
    r"\b(?:i|im|ive)\b[^.?!]*\b(?:keep|keeps|always|constantly|still|never remember|"
    r"cant remember to|forget to)\b[^.?!]*\b" + FORGET_A_THING
    + r"|\b(?:i|im|ive)\s+(?:always|constantly|keep)\s+" + FORGET_A_THING
    + r"|\bi\s+never\s+remember\s+(?:to\s+\w+|my\b|the\b)")


# What keeps slipping decides the trick, so the two things that a home for an object cannot fix
# get their own lines. A date is not forgotten for want of a bowl by the door: it needs to be
# written down where the person already looks, with the reminder set while the thing is still in
# front of them. A secret is not a job to tie to a habit either - it needs somewhere that
# remembers it, so the person never has to. Both are read before the general habit line, which
# asks "which one keeps slipping?" and reads as a shrug to somebody who has just said what it is.
# A forgetting verb is what makes it a slip of memory: "im always late for appointments" has a
# date word in it and no forgetting at all, and the answer to lateness is the leaving time, not
# a diary. The "double booking" shape is the one case where the problem is the diary itself.
FORGET_A_DATE = re.compile(
    r"\b(?:i|im|ive|we|were)\b[^.?!]*\b(?:forget|forgets|forgetting|forgot|never remember|"
    r"(?:keep|keeps|kept) missing|miss|misses|missing)\b[^.?!]*\b(?:appointments?|birthdays?|"
    r"meetings?|the dentist|deadlines?|due dates?|renewals?|anniversar(?:y|ies)|plans?)\b")


# Two plans in the same hour of the same day is a diary that lives in two places, and the fix is
# to keep one.
FORGETS_A_CLASH = re.compile(
    r"\bdouble[- ]book(?:s|ed|ing)?\b|\bbooked (?:two|2) things\b|\bbook (?:two|2) (?:things|"
    r"plans)\b|\btwo (?:appointments|meetings|plans) (?:on|for|in) the same\b")


FORGET_A_SECRET = re.compile(
    r"\b(?:forget|forgets|forgetting|keep losing|lost|slips?)\b[^.?!]*\bpasswords?\b"
    r"|\bpasswords?\b[^.?!]*\b(?:keep|slip|forget)\w*\b")


# A death is not always the whole line. "my husband died in march and i dont know how to tell
# our daughter" is a person asking for the words to say to a child, and a condolence ("is there
# someone you can be with today") answers the half they did not ask about and ignores the half
# they did. The knowledge base has that answer (`explaining-death-to-a-child`), so the arbiter
# stands the sudden-loss claim down for the ask - but only when an entry has proposed something.
# The pool here is unchanged: when nothing has the words, this condolence is the right reply,
# and a bereaved parent must not be left with a nod. The reading says no in two cases: a death
# named as today ("my husband died this morning and i have to tell the kids" is a person in the
# worst hour, and the words are the next turn), and a child who is the one who died.
TELLING_A_CHILD = re.compile(
    r"\b(?:tell|telling|told|say|saying|explain|explaining|talk|talking|break it to|"
    r"break the news)\b"
    r"[^.?!]{0,32}\b(?:kid|kids|child|children|son|daughter|boy|boys|girl|girls|"
    r"grandchild|grandchildren|grandson|granddaughter|teenager|teen|toddler|little one|"
    r"niece|nephew)\b")


# The death named as today, which keeps the condolence whatever else the line asks. "died
# yesterday" is still the day itself; "died in march" is the months-back death that turns the
# line into a question about what to say.
A_DEATH_FROM_TODAY = re.compile(
    r"\b(?:today|this morning|this afternoon|this evening|tonight|last night|yesterday|"
    r"an hour ago|a moment ago|just (?:now|died|heard|found out)|hours ago)\b")


# The child is the one who died. "my son died and i have to tell my daughter" is a bereaved
# parent: the condolence is this turn and the sister who has to be told is the next one, so the
# words-for-a-child answer must not take the turn from it. The child word is the subject of the
# death here, not the person being told.
A_CHILD_DIED = re.compile(
    r"\b(?:baby|child|children|kid|kids|son|daughter|boy|girl|boys|girls|teenager|teen|"
    r"toddler|boy|girl|niece|nephew|grandson|granddaughter)\b"
    r"\s+(?:has |have |had )?(?:just )?(?:died|passed away|passed on|passed|was killed|"
    r"were killed|is dying|are dying)\b")


# The death itself, so the reading stays on the lines it is for: "how do i tell my kids im
# getting divorced" is an ask of the same shape, and it is not this one.
A_DEATH_IN_THE_LINE = re.compile(
    r"\b(?:died|dies|dying|dead|death|passed away|passed on|funeral|buried|burial|"
    r"cremation|killed)\b")


# A suicide is not the same telling: what happened is the half nobody has the words for, and the
# pools that read it are the safety lane's, so this reading leaves those lines alone
# (bot/compose/badnews.py, `SUICIDE`).
A_SUICIDE_IN_THE_LINE = re.compile(
    r"\b(?:suicide|suicidal|took (?:his|her|their) own life|killed (?:him|her|them)self|"
    r"ended (?:his|her|their) own life|overdose[sd]?|od'd)\b", re.I)


def a_fresh_death_and_the_words(clean):
    """A death said as today, with the words for a child asked for in the same line.

    `asks_what_to_tell_a_child` says no to these, because on the day itself the person is not
    asking for a procedure - but the condolence's own question ("tell me what would help today")
    is what they have just answered, so the turn is the pool above rather than either one alone.
    The child who is the one who died keeps the condolence: there is no telling to do.
    """
    text = " ".join(str(clean or "").lower().split())
    return bool(TELLING_A_CHILD.search(text)
                and A_DEATH_IN_THE_LINE.search(text)
                and A_DEATH_FROM_TODAY.search(text)
                and not A_CHILD_DIED.search(text)
                and not A_SUICIDE_IN_THE_LINE.search(text))


def asks_what_to_tell_a_child(clean):
    """Read by the arbiter: a death line whose ask is the words for a child, not a condolence.

    The reading is only ever used to give the turn to the entry that has the words, and to stand
    the sudden-loss reply down when it does, so a line it does not recognise keeps its reply
    exactly as it was.
    """
    text = " ".join(str(clean or "").lower().split())
    return bool(TELLING_A_CHILD.search(text)
                and A_DEATH_IN_THE_LINE.search(text)
                and not A_DEATH_FROM_TODAY.search(text)
                and not A_CHILD_DIED.search(text))


# Warm drinks and an early night are cold-and-flu comfort: offered for a headache at a desk or a
# bad back it reads as advice for something else, so it is only for that kind of ill.
_ILL = re.compile(r"\b(?:cold|cough|coughing|flu|throat|chest|temperature|virus|sniffles?|"
                  r"sneez\w*|head cold)\b", re.I)


# A symptom that has hung on gets the sentence for a thing that is not shifting, not "rest, warm
# drinks and an early night", which answers the first day of it. The three lines live in
# bot/compose/__init__.py so the composer and chat say the same thing.
SYMPTOM_LINGERS = LINGERED_LINE


# A lump is not a thing to wait out however recently it turned up, and it is the one symptom
# where "a pharmacist will see you quicker than a GP" is not the answer, because a lump is the
# GP's job. "A lump in my throat" is the tears idiom rather than a lump, so it is left alone.
# "a lump in my throat" is a feeling and "a lump sum" is money: the word after the lump is what
# says which, so only a lump a person has found in themselves is read here.
_LUMP = re.compile(r"\b(?:lumps?|growths?)\b"
                   r"(?!\s+in\s+(?:my|your|the)\s+throat)"
                   r"(?!\s*-?\s*sums?\b)", re.I)


# A bug you catch, as against a body part that hurts. `_ILL` decides which comfort line fits a
# line (a sore throat reads the cold's own line), and it holds `throat` and `chest` for that. But
# a throat or a chest is also the trouble question's business ("my chest is sore" wants how long
# and what makes it worse), so the guard below reads this narrower list and only a caught bug -
# a cough, a cold, flu, a virus, a temperature - keeps the advice over the trouble question.
# "cold" is the bug only when it is the thing itself: "i have a cold" is the bug, "a cold sore",
# "cold feet", "a cold room" and "cold water" are a description of something else.
_CAUGHT = re.compile(
    r"\b(?:cold(?!\s+(?:sore|sores|feet|hands|fingers|toes|air|weather|room|drink|water|days?|"
    r"morning|night|outside|shower|call))|cough|coughing|flu|virus|temperature|head cold|"
    r"sniffles?|sneez\w*)\b", re.I)


# The result itself, named by the person: the exam, the interview, the offer, the scan. A subject
# alone is not enough - "i dont think i can do this anymore" has a doubt and no result, and it is
# not waiting on anything - and neither is the bare noun "job", which is a thing you can also do
# ("i dont think i can do my job anymore"). So the result is the noun list below, or the phrase
# that reports it.
_RESULT = re.compile(
    r"\b(?:pass|passed|passes|fail|failed|fails|results?|exam|exams|test|tests|interviews?|"
    r"offers?|application|applied|audition|trial shift|probation|scan|biopsy|referral|hearing|"
    r"decision|verdict|grades?|mark|marks|"
    r"got (?:the|a) (?:job|place|part|role|offer|position)|get (?:the|a) (?:job|place|part|role)|"
    r"got in)\b", re.I)


_WAITING = re.compile(
    r"\b(?:(?:i|we) (?:find|finds) out|find out (?:next|on|tomorrow|in|at the end)|"
    r"(?:i|we) (?:hear|hearing) back|"
    r"(?:i|we|im|i'm|i am|we|were|we're|we are)\s+(?:still\s+)?"
    r"(?:havent|hasnt|haven't|hasn't|not|never)\s+heard\s+back|"
    r"(?:i|we|im|i'm|i am)\s+(?:still\s+)?(?:havent|hasnt|haven't|hasn't) heard\s+"
    r"(?:back|anything|a thing|yet|from (?:the |my |our )?" + _ISSUER + r")|"
    r"(?:i|im|i'm|i am|we|were|we're|we are)\s+(?:still\s+)?waiting\s+to hear|"
    r"(?:i|im|i'm|i am|we|were|we're|we are)\s+(?:still\s+)?waiting\s+on\s+"
    r"(?:(?:the |my |our )?(?:(?:exam |test |scan |interview |blood test )?"
    r"(?:results?|outcome|decision|news|answer|reply|offer|scan|tests?|exam|interview))|"
    r"(?:the |my |our )?" + _ISSUER + r")|"
    r"(?:i|we) (?:should|will|would) know|(?:i|we) (?:am|are|'m|'re) out of|"
    r"out of (?:my|our) hands)\b", re.I)


# A doubt about the result: not a pass, not a no, a maybe, and the news has not landed.
_DOUBT = re.compile(
    r"\b(?:dont think|do not think|didnt think|not sure|unsure|no idea|dont know|do not know|"
    r"may have|maybe|probably|might|hopefully)\b", re.I)


# ...and "i probably failed" is the person's own guess at a result they have already sat, not the
# news: the tense of the result is what says so. "i might fail" is an exam ahead and "i might have
# passed" is the same doubt pointing the other way, so both stay with the plain wait; "i might have
# failed my driving test" is a test behind them and a guess on top of it, and the reply names the
# guessing rather than sympathising with a failure that has not been reported (hearty-emu, #2663:
# "Sorry to hear that" for a line that only says "might" is a wrong answer).
_GUESSED_RESULT = re.compile(
    r"\b(?:probably|might(?:\s+have|'ve)?|maybe|think(?:ing)?|dont think|do not think|"
    r"not sure|no idea)\s+(?:failed|flunked|bombed|messed up|did badly|"
    r"did (?:rubbish|badly|terribly|awful)|(?:didnt|did not|havent|have not) (?:pass(?:ed)?|get|got)|"
    r"lost it|ruined it)\b", re.I)


# The doubt is over by the end of the line: "i dont think i could have passed but i did", "i
# didnt think id pass but i did", "i dont think i got the job but they rang". Those are a person
# enjoying the result, so there is nothing left to wait for and asking when is asking them to say
# it again. The contrast word is what makes it a resolution: "i dont think i passed" has none.
_RESOLVED = re.compile(
    r"\b(?:but|and) (?:i|we|he|she|they)\b[^.?!]*\b(?:did|do|does|passed|pass|got|made|rang|rang me)\b|"
    r"\b(?:but|and) it (?:worked|worked out|came through|came back|arrived|landed|turned out|was fine)\b|"
    r"\bturn(?:s|ed) out\b", re.I)


# The line already says when, so there is nothing to ask: it is the waiting that gets the reply.
_A_TIME = re.compile(
    r"\b(?:tomorrow|tonight|today|this (?:morning|afternoon|evening|week|weekend|month)|"
    r"next (?:week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday|term)|"
    r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"in (?:a|two|three|four|five|a few|\d+) (?:day|days|week|weeks|month|months)|fortnight|"
    r"end of the (?:week|month)|by (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"in the (?:morning|afternoon|evening)|any day now|soon|at some point)\b", re.I)


def _an_open_result(clean):
    """True when the line reports a result the person has not heard yet."""
    if _RESOLVED.search(clean):
        return False  # "but i did" - the doubt is over, so nothing is still in the post
    if _WAITING.search(clean):
        return True
    return bool(_RESULT.search(clean) and _DOUBT.search(clean))


# ...and the answer named in the same breath. "i heard back i got it" is the news, and it is the
# same news as "i got the job", so it is answered as one. "they said no" is the other way and is
# left to the pools below rather than congratulated.
_ANSWER_GOOD = re.compile(
    r"\b(?:got\s+(?:it|the\s+(?:job|place|part|role|offer|position)|in)|passed|said\s+yes|"
    r"im\s+in|offered\s+me|accepted|all\s+clear|benign|"
    r"(?:it\s+)?(?:was|is|came\s+back)\s+(?:clear|fine|nothing))\b", re.I)


_ANSWER_BAD = re.compile(
    r"\b(?:said\s+no|was\s+a\s+no|rejected|turned\s+(?:me\s+)?down|didnt\s+get|"
    r"did\s+not\s+get|unsuccessful|failed|no\s+thanks|bad\s+news|not\s+good\s+news|"
    r"was\s+bad|went\s+badly|no\s+luck|cancer|it\s+was\s+inoperable|"
    # "i got my results back and its not good" is the bad half said without the word "news": the
    # person names the answer and then says how it went, and the second half decides the reply.
    # the contraction without its apostrophe is what people actually type: "theyre terrible",
    # "theyd failed", "its not good". 's alone missed every "re" and "d", so a person who had
    # already said how it went was asked how it went.
    r"(?:it|that|they)(?:'s|'re|'d|s|re|d|\s+is|\s+are|\s+was|\s+were)?\s+(?:not\s+good|no\s+good|"
    r"not\s+great|bad|rubbish|awful|terrible))\b", re.I)


def _the_news_landed(clean):
    """'good' when the answer came back and it was good, 'landed' when it came back unread.

    The wait and the answer are the two halves of one thread, and the reply to each is different:
    a person still waiting wants to be asked when, and a person who has heard wants to say what
    was said. Until this, the second half got the nod, which reads as though the bot had stopped
    listening just as the news arrived.
    """
    if not _LANDED.search(clean):
        return None
    if _ANSWER_BAD.search(clean):
        return "bad"  # "i heard back, they said no" is not a congratulation: it is a blow
    if _ANSWER_GOOD.search(clean):
        return "good"
    return "landed"


def reads_as_a_result_line(text):
    """True when the line is a result the person is waiting on, or one they have just heard.

    Both halves are a short line with nothing in it for the store: "i got the results" is a
    person with news to tell, and "im not sure i got the place" is a person waiting. The reply
    that works is the one that asks for the rest ("What did they say?", "When do you find out?"),
    which these pools already hold. bot/memory/ack.py asks this before it says a line back,
    because "Noted: you got the results." hands the person their own words and nothing else.
    """
    clean = _plain(_matchable(text))
    if not clean:
        return False
    return bool(_the_news_landed(clean) or _an_open_result(clean) or _a_guessed_result(clean))


def _a_guessed_result(clean):
    """True for a result the person has already sat and is guessing at ("i probably failed")."""
    return bool(_GUESSED_RESULT.search(clean))


def _a_time_in_it(clean):
    """True when the line already says when the news lands."""
    return bool(_A_TIME.search(clean))


# The cost is the thing being asked of them, so a number or a price word has to be there, and so
# does somebody asking: "they want me to move in" and "my boss wants me to work weekends" are
# both asks with no money in them, and "my car insurance went up to 800" is money with nobody
# asking. A question is left alone - "should i go to the wedding" is its own ask.
A_COST = re.compile(r"£\s?\d|\b\d+\s?(?:quid|pounds?|bucks|grand|k)\b|\b(?:costs?|costing|"
                    r"expensive|afford|pricey|a\s+fortune|too\s+much)\b"
                    # "the suit hire is 200", "the dress is 500": an amount with a money verb in
                    # front of it is a price, even with no currency word after it.
                    r"|\b(?:is|are|was|were|costs?|costing|comes?|come\s+to|at|pay|paid|pays"
                    r"|spend|spent|wants?)\s+£?\s?\d{2,}\b", re.I)


SOMEBODY_ASKS = re.compile(
    r"\b(?:want(?:s|ed)?|ask(?:s|ed)?|expect(?:s|ed)?|told|tell(?:s|ing)?)\s+me\s+to\b"
    r"|\b(?:they|he|she|my\s+\w+|his|her|their)\s+want(?:s|ed)?\b"
    r"|\b(?:invited\s+me|asked\s+me|been\s+asked|asking\s+me\s+for)\b", re.I)


# The role says the ask without a verb: "im a bridesmaid and the dress is 800 quid" is a person
# being asked to pay for somebody else's day, and the line never says who asked.
A_ROLE_IN_SOMEBODY_ELSES_DAY = re.compile(
    r"\b(?:bridesmaid|maid\s+of\s+honour|best\s+man|godparent|usher|stag\s+do|stag\s+night|"
    r"hen\s+do|hen\s+party|hen\s+weekend)\b", re.I)


def _a_cost_somebody_asks(clean):
    """True for a bill somebody else has put on the person for a shared occasion."""
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text or len(text.split()) > 24:
        return False
    if not A_COST.search(text):
        return False
    if not (SOMEBODY_ASKS.search(text) or A_ROLE_IN_SOMEBODY_ELSES_DAY.search(text)):
        return False
    # Their own wedding, their own holiday: being asked to pay for a thing they are arranging is
    # a budget question, and the budget entries answer it better than this pool can.
    return not re.search(r"\bmy\s+(?:own\s+)?(?:wedding|holiday|party|trip)\b", text)


# How the day is, said as a remark. "cold today", "pouring down", "bit nippy", "its boiling in
# here", "the suns out" and "miserable day" are how people open a chat all day long, and they are
# the one remark that asks for nothing and still deserves better than the stock nod: the pool here
# answered "cold today" with "Got it. Is there anything you'd like a hand with?", "pouring down"
# with "Thanks for telling me - I'm here if you want to dig into any of that", and "bit nippy" the
# same - the sentence a person says when they have stopped listening. A remark about the weather is
# something a friend answers with the weather, so each kind of day has its own lines.
#
# The reading is the words of the day and nothing else, which is what keeps it off proper lines: a
# thing of their own in the sentence ("my tea has gone cold", "the oven is too hot", "its cold in
# here", "my hands are freezing") leaves a word the reading does not know, so it keeps whatever
# answered it before, and a question about the weather ("will it rain tomorrow") keeps the search
# or the entry that can actually answer it.
DAY_WORDS = {
    "cold": frozenset("""cold freezing chilly bitter baltic parky nippy frost frosty icy ice snow
        snowing snowy sleet slush snap frozen raw perishing taters nithered""".split()),
    "rain": frozenset("""rain raining rains rainy wet pouring drizzle drizzling drizzly showers
        shower chucking tipping pelting bucketing downpour soaked sodden damp mizzle mizzling
        lashing lash hosing drenched drenching soaking soaked-through"""
                     .split()),
    "wind": frozenset("""wind windy gale gales gusty blustery storm stormy squall blowing blow blows
        blowing""".split()),
    "hot": frozenset("""hot boiling scorching roasting sweltering baking heat heatwave muggy humid
        sticky close clammy stifling scorcher sizzling sizzler""".split()),
    # The day with nothing wrong with it, named as such: "mild one today" was answered "Noted:
    # mild one today." because no pool held the word, so the pools were read as not about the day
    # at all. Same kind as the ruling-out answer, and a line can name it either way.
    "mild": frozenset("""mild milder balmy clement""".split()),
    "fog": frozenset("""fog foggy mist misty haze hazy murk""".split()),
    "grey": frozenset("""grey gray gloomy dull overcast dark dreich dreary murky miserable grim
        cloudy horrible rotten rubbish depressing drizzly""".split()),
    "sun": frozenset("""sun suns sunny sunshine bright clear blue glorious gorgeous beautiful lovely
        nice warm pleasant""".split()),
}


# The little words a remark about the day is held together with: "its very cold out", "bit nippy
# again", "lovely and warm today". None of them says anything of its own, so a line made only of
# these and one kind of day is the remark.
DAY_GLUE = frozenset("""it its it's is are was were be been being feels feel feeling looks look
    looking very really so too quite rather bit a an the this that thats that's there here out
    outside indoors in inside above up down today tonight now still again already at last
    honestly actually just and but or oh ah well ugh eh huh huh its isn't isnt wasn't wasnt what
    such some much more most enough all day days night nights morning mornings afternoon
    afternoons evening evenings week end weather coming for of with to getting got get turned
    s gone going outside one ones not lots load loads plenty ton tons bucket buckets thick heavy
    dense meant due supposed forecast tomorrow later weekend weekends sunday monday tuesday wednesday
    thursday friday saturday next
    innit init aint ay arent aren't no never hardly even though tho anymore
    proper right dead bare bloody damn awful
    rn atm tn 2nite tmoz""".split())


# The day that met the person on the way: "i got soaked walking in", "we got drenched on the way
# home", "i got caught in the rain". The first person and the errand are how the day arrived, not
# what the line is about; take them off and the day is what is left. Without this the line opened
# on "i", which is a person doing something with their day, and got an echo of itself back.
DAY_MET_ME = re.compile(
    r"^(?:i|we|they)\s+(?:got|was|were|am|have been|ve been|waited|stood|queued|walked"
    r"|sheltered)\s+")


DAY_ON_THE_WAY = ("walking in", "walking home", "walking to work", "walking the dog",
                  "on the way home", "on the way in", "on the way to work", "on my way home",
                  "on my way in", "on the school run", "coming home", "going to work",
                  "caught in the", "caught out in the",
                  "on the platform", "at the bus stop", "at the station", "at the stop",
                  "waiting for the bus", "waiting for a bus", "waiting for the train",
                  "waiting for a train", "waiting for my bus", "waiting for my train",
                  "for a bus", "for the bus", "for a train", "for the train")


# A kind of day named to be ruled out: "not cold today", "isn't raining", "not too hot". The
# negation can be a word or two away from the day word ("not TOO hot", "not THAT cold"), so the
# words in between are skipped. Only the day words left after that are what the line says.
NEGATIONS = frozenset("""not isnt isn't arent aren't wasnt wasn't aint ain't no never hardly
    nothing""".split())


NEGATION_SOFTENERS = frozenset("that too so even very all at much really quite bit".split())


# "windy as anything", "cold as hell": the day said with the strength of it on the end. The words
# on their own say nothing, so the phrases are listed and taken off the line before it is read.
DAY_AS_ANYTHING = ("as anything", "as hell", "as can be", "as ever", "as fuck", "as all hell")


# The day said as an idiom, which names no word the pools know: "brass monkeys out there" and
# "brass monkey weather" are the cold and nothing else. It is written over with the word it
# stands for before the line is read, so the rest of the reading - the glue, the "not" in front
# of it, the day that met the person - works on it as it does on the plain word: "its not brass
# monkeys today" is the same ruling-out as "its not freezing today".
DAY_SAID_AS_A_KIND = (("brass monkeys", "freezing"), ("brass monkey", "freezing"))


# The words that put the day in the future: "its meant to be snowy tomorrow" is a forecast, and
# the answer to a forecast is the plan it changes, not the day outside now. "Storm coming" is not
# here: it is the day arriving, and the remark pools already answer it.
DAY_TO_COME = frozenset("""meant due supposed forecast tomorrow later weekend weekends sunday
    monday tuesday wednesday thursday friday saturday next""".split())


# The same said as phrases, because "going" and "to" are little words the remark is held together
# with on their own: "its going to storm tonight" is the storm on its way, not the storm now.
DAY_TO_COME_PHRASES = ("going to", "meant to", "due to", "supposed to", "forecast", "to come",
                       "on its way")


# The forecast said in the past is a forecast that has already had its day: "it was meant to be hot"
# is a complaint that it was not, and no plan of theirs waits on it.
DAY_TO_COME_PAST = ("was meant to", "were meant to", "was supposed to", "were supposed to",
                    "was due to", "were due to")


# How the day is judged rather than what it is doing. Said in the past - "today was rubbish", "the
# week was rubbish" - it is the person's day going badly, which the pools that answer the weather
# would answer as the sky.
DAY_VERDICTS = frozenset("""rubbish horrible rotten miserable grim gloomy dreary depressing dull
    dreary lovely gorgeous beautiful nice glorious pleasant dreich joyful""".split())


# What a forecast gets instead of the pools above: the day is on its way, so the reply is about the
# thing worth doing before it arrives. A good forecast is not a warning and says so.
# A line that opens on one of these is asking, not remarking: "is it cold outside" wants the
# temperature, and "what a lovely day" is a verdict on the day, not a report of it. The words
# are the ones a question turns on, and they open the question and not the remark.
DAY_ASKS = frozenset("""is are was were do does did can could will would should shall have has had
    may might how what when where why who which""".split())


# A line that opens on one of these is what the person did with the day rather than what the day
# is doing: "been out in the sun all day" is a person with sunburn coming, not a lovely afternoon.
DAY_THEIR_OWN_DAY = frozenset("""been spent spend sat stood had i im i'm ive i've we weve we're""".split())


# Phrases of the day's words that are about something else entirely: "all clear" is a test result
# and "all done" is a job finished, and the words alone cannot tell them from a clear blue sky.
DAY_NOT_THE_DAY = ("all clear", "all done", "all good", "all right", "all set", "all over",
                   "all in", "too warm", "too cold",
                   # "out cold" is a person who is unconscious, and the words around it are all
                   # words the day pools know, so "i was out cold all night" was answered with the
                   # cold day ("Bit parky, isn't it") instead of the safety reader's question
                   # about how long they were out. A night's sleep is the one form of it that
                   # carries no other word to fence it ("for two hours" and "last night" already
                   # reached the safety reader), so the phrase itself stands the day pools down.
                   "out cold", "out for the count")


# A line that opens on one of these is added to something said before it ("and heat", after "i've
# tried stretching") and not a remark about the day at all.
DAY_JOINED_ON = frozenset("and also plus then but because".split())


# Words that can be about the day and about something else just as often: "thats a bit depressing"
# after a quote is how the price feels, "its quite dark" after "the living room" is the room, and
# "grey and gloomy" needs the day named beside it before it is the weather. "so hot" and "cold
# today" hold on their own, so only these need the day named.
DAY_NEEDS_A_DAY_NAMED = frozenset("""grey gray gloomy dull dark clear blue lovely nice pleasant
    miserable depressing grim horrible rotten dreary""".split())


# The day said inside the house is the room, not the weather: "its stifling in here" is the room's
# question, and a friend answers the day outside. The words that put the remark indoors take it out
# of this reading, so the entry that knows about heating or a hot flat keeps the line.
DAY_IN_HERE = ("in here", "in this room", "in my room", "in the house", "in our house",
               "in the flat", "in my flat", "in the kitchen", "in the bedroom", "in the front room",
               "in the living room", "in the office", "in my office", "in the car", "indoors",
               "inside")


# What names the day the remark is about.
DAY_NAMED = frozenset("""out outside outdoors day days weather morning mornings afternoon evenings
    evening night nights today tonight now already week""".split())


def _the_day_described(clean):
    """The pool for a line that says what the day is like, or None.

    Only the remark itself comes here: every word of the line is either a word for how the day
    is or a little word holding the remark together. That is what keeps a line with a thing of its
    own in it ("my tea has gone cold", "the shed roof is leaking") with the reader that knows
    about the thing, and a question ("will it rain tomorrow") with the reader that can answer it.
    """
    line = " ".join(str(clean or "").lower().split())
    if not line or "?" in line:
        return None
    # "what a scorcher", "what a downpour": "what" opens a question, but "what a" opens an
    # exclamation about the day, and the words after it are the remark. Without this the line was
    # read as a question nothing here can answer, and "what a downpour" got the search hedge.
    line = re.sub(r"^what\s+an?\s+", "", line)
    if DAY_MET_ME.match(line):
        line = DAY_MET_ME.sub("", line)
        for phrase in DAY_ON_THE_WAY:
            line = re.sub(r"\b" + r"\s+".join(phrase.split()) + r"\b", " ", line)
        line = " ".join(line.split())
    for phrase in DAY_AS_ANYTHING:
        line = re.sub(r"\b" + r"\s+".join(phrase.split()) + r"\b", " ", line)
    for phrase, word in DAY_SAID_AS_A_KIND:
        line = re.sub(r"\b" + r"\s+".join(phrase.split()) + r"\b", word, line)
    line = " ".join(line.split())
    words = [word.strip(".,!;:'\u2019\"") for word in line.split()]
    words = [word for word in words if word]
    if not words or len(words) > 8:
        return None
    if words[0] in DAY_ASKS or words[0] in DAY_THEIR_OWN_DAY or words[0] in DAY_JOINED_ON:
        return None
    if any(phrase in line for phrase in DAY_NOT_THE_DAY):
        return None
    if any(phrase in line for phrase in DAY_IN_HERE):
        return None
    if not [word for word in words if word in DAY_NAMED or word in DAY_TO_COME]:
        day_words = [word for word in words
                     if any(word in pool for pool in DAY_WORDS.values())]
        if day_words and all(word in DAY_NEEDS_A_DAY_NAMED for word in day_words):
            return None
    known = DAY_GLUE.union(*DAY_WORDS.values())
    if [word for word in words if word not in known]:
        return None
    if any(phrase in line for phrase in DAY_TO_COME_PAST):
        return None
    # "its the hot one" picks one of several things out by how hot it is, and the day is not one of
    # them: a determiner and "one" after the word make it a thing among things.
    if any(words[index - 1] == "the" and words[index + 1:index + 2] in (["one"], ["ones"])
           for index, word in enumerate(words)
           if index > 0 and index + 1 < len(words)
           and any(word in pool for pool in DAY_WORDS.values())):
        return None
    day_words = [word for word in words if any(word in pool for pool in DAY_WORDS.values())]
    if ("was" in words or "were" in words) and day_words \
            and all(word in DAY_VERDICTS for word in day_words) \
            and not any(word in DAY_TO_COME for word in words):
        return None
    def ruled_out(index):
        """True when the day word at `index` is named to be ruled out, not to be reported."""
        back = index - 1
        while back >= 0 and words[back] in NEGATION_SOFTENERS:
            back -= 1
        return back >= 0 and words[back] in NEGATIONS

    best, best_count = None, 0
    ruled, ruled_count = None, 0
    for kind, pool in DAY_WORDS.items():
        # A kind word the person has just said "not" in front of is the kind they are ruling out:
        # "its raining not sunny" is a wet day and not a sunny one.
        count = sum(1 for index, word in enumerate(words)
                    if word in pool and not ruled_out(index))
        if count > best_count:
            best, best_count = kind, count
        cleared = sum(1 for index, word in enumerate(words)
                      if word in pool and ruled_out(index))
        if cleared > ruled_count:
            ruled, ruled_count = kind, cleared
    if not best:
        # Every kind of day in the line was ruled out: "not cold today", "not too hot", "isn't
        # raining". The person has said what the day is not, which is still a remark about it,
        # and the pools for the kind they named would contradict them - "not too hot today" was
        # answered "Boiling, isn't it". The mild pool agrees with the ruling and claims nothing.
        if ruled:
            return THE_DAY.get("mild")
        return None
    if any(word in DAY_TO_COME for word in words) \
            or any(phrase in line for phrase in DAY_TO_COME_PHRASES):
        # A forecast is the day that has not arrived: "meant to be nice tomorrow" got "I'm listening
        # - say more if it helps", and "snow due tomorrow" an echo of itself. The plan it changes
        # is what a friend answers, and a good forecast is worth saving the day for.
        return THE_DAY_AHEAD.get(best) or THE_DAY.get(best)
    # "it gets dark so early now" says when it is, not how it is, and the remark pools are about
    # the day being too much of something: nothing here is asked for it.
    return THE_DAY.get(best)


def the_day_remarked(text):
    """The pool for a remark about the day as it is or as it is coming, or None.

    The same reading as `_the_day_described`, for the knowledge base, which has to stand down on
    a line the day's answer owns: an entry is reached by a word, so "windy as anything" found the
    bloating card and "cold next week" the one about a virus. A report on the day in the past is
    left to it - "it was icy this morning" in a chat about a skid is the ice explained, and the
    entry that knows about ice is the better answer - so the past tense of the remark is not here.
    """
    line = " ".join(str(text or "").lower().split())
    pool = _the_day_described(line)
    if not pool:
        return None
    if re.search(r"\b(?:was|were)\b", line):
        return None
    return pool


# A plan the person has had to drop is not a fact to file and not an appliance to troubleshoot.
# On main "i cant come" got the stock nod ("Thanks for telling me - I'm here if you want to dig
# into any of that"), "cant make it tonight" and "i cant make saturday" got "Got it. Is there
# anything you'd like a hand with?", and "i wont be able to make it" got the trouble question
# ("That's a pain. What's it doing exactly, and when did it start?"), which is the reply for a
# broken thing. What the person has said is that they are not going, so the reply is the one a
# friend gives: no trouble, and the offer of the harder half - telling whoever is expecting them.
# The reading is deliberately narrow: only the negated ability to come or make it, or the
# obligation to cancel, with nothing after it but an apology, a day, or the thing itself. Every
# other sense of those verbs is somebody else's line and stays theirs: "my cat wont come out from
# under the bed", "my heating wont come on", "i cant come up with ideas", "cant make ends meet",
# "i cant make it stop", "i cant make the bed" and "you cant come tomorrow then" (a doubt about
# the bot) are all left alone.
# "so you cant come tomorrow then" is a doubt about the bot, not a plan the person is dropping.
DECLINE_ABOUT_THE_BOT = re.compile(r"\b(?:you|u|yours)\s+(?:\w+\s+){0,2}$")


# The pool the reading feeds speaks to the person who dropped the plan: "no need to explain",
# "what to say to whoever is expecting you". When the thing that cannot come is somebody else -
# "the plumber cant come till friday" in a boiler chat was answered "Fair enough, no need to
# explain. Say the word if you want a hand putting it in a message" - the person has explained
# nothing and nobody is expecting them, so a plan knocked sideways by somebody else takes its own
# pool (`PLAN_KNOCKED`). Third person and a noun phrase with a determiner in it are somebody
# else; "i" and "we" are the person.
DECLINE_SOMEONE_ELSE = re.compile(
    r"(?:\b(?:the|a|an|my|our|your|his|her|their|this|that|these|those)\s+(?:\w+\s+){0,2}"
    r"|\b(?:he|she|they)\s*)$", re.I)


DECLINE_VERB = re.compile(
    r"\b(?:cant|cannot|can not|couldnt|wont|wouldnt|unable to|"
    r"not (?:going to|gonna) be able to|not able to|"
    r"not going to be able to|not gonna be able to)\s+"
    r"(?:(?:actually|really|even|possibly)\s+)*"
    r"(?:come|make|be there|attend|be able to (?:come|make it|make|be there))\b(.*)$")


DECLINE_MUST = re.compile(
    r"\b(?:have|has|had|ve got|got|going to|gonna|need|needs|will have)\s+to\s+"
    r"(?:cancel|pull out|back out|cry off|drop out)\b(.*)$")


# What follows the verb decides it: a day or a time, the thing itself ("to the party"), or nothing.
# A line that is asking something is not a plan being dropped: "how do i tell my friend i cant
# come to her wedding" wants the wording, and "i need to cancel my dentist appointment" is a job
# with an entry of its own.
DECLINE_ASK = re.compile(
    r"^(?:how|what|when|where|which|who|why|should|could|would|do|does|did|is|are|will|any)\b")


DECLINE_TIME = re.compile(
    r"\b(?:tonight|today|tomorrow|this (?:evening|afternoon|morning|weekend|week|time|one)|"
    r"next (?:week|weekend|month|time)|"
    r"(?:mon|tues|wednes|thurs|fri|satur|sun)day|weekend|yesterday|on (?:the )?"
    r"(?:mon|tues|wednes|thurs|fri|satur|sun)day|after all)\b")


# The occasion itself, named: "cant make the wedding", "cant make parents evening". A noun that
# is an occasion is the plan; the other senses of the verb are already caught by `DECLINE_OTHER`.
DECLINE_OCCASION = re.compile(
    r"\b(?:wedding|party|funeral|meeting|interview|appointment|class|lesson|match|game|gig|"
    r"exam|shift|christening|baptism|birthday|service|rehearsal|practice|session|course|"
    r"event|evening|morning|afternoon|night|parents|school|one)\b")


# "cant come on the 14th": a date is a plan, and it is read before the "come on" sense below.
DECLINE_DATE = re.compile(r"\b(?:on|at|by)\s+(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?\b")


# The same verbs in every other sense: nothing here is a plan being dropped.
DECLINE_OTHER = re.compile(
    r"^(?:up|out|on|down|off|back|home|round|across|along to|into|to terms|near|"
    r"ends meet|sense|sure|do(?:ne)?|the most|a (?:difference|decision|start|point|mess|fuss|"
    r"cake|list|move|change)|money|dinner|tea|breakfast|lunch|supper|the bed|my bed|the tea|"
    # "i cant come to the phone" / "to the door" is not a plan being dropped: nobody is
    # expecting them anywhere, they are saying they cannot pick up.
    r"to the (?:phone|landline|door|doorstep)|the phone|the door|"
    r"it (?:work|stop|go|better|worse|through|happen|home|out|up|down|right|snow|rain|fit|run))\b")


# A phrasal "come on" / "come out" is a thing or somebody else, not the person dropping a plan:
# "the heating wont come on", "the stain wont come out", "she cant come on saturday". Their own
# line with a day after it - "i cant come on saturday", "cant come on monday" - is the plan, and
# the bare "on" in `DECLINE_OTHER` was refusing it.
DECLINE_OTHER_SUBJECT = re.compile(
    r"^(?:my|the|our|your|its|it|his|her|their|this|that|these|those|"
    r"he|she|they|dad|mum|mom|brother|sister|son|daughter|kids?)\b")


# "i cant be there for him" is being available to somebody, not dropping an invitation, and "do
# you want to rearrange it, or let this one go?" about a birth is the worst line in the file.
DECLINE_BE_THERE = re.compile(r"\bbe\s+there$")


# The apology comes off the end too: "i cant come sorry", "cant make it im afraid".
DECLINE_AFTER = re.compile(
    r"(?:[\s,]*(?:sorry|im sorry|so sorry|apologies|im afraid|afraid|unfortunately|"
    r"i think|i dont think|this time|this week))+$")


BODY_SAYS_WHY_PHRASE = re.compile(
    r"\bthrowing\s+up\b|\bvomit\w*\b|\bstomach\s+(?:bug|upset)\b|\bd&v\b|"
    r"\bunder\s+the\s+weather\b|\bcoming\s+down\s+with\b|\bcan'?t\s+keep\s+\w+\s+down\b")


BABY_ON_THE_WAY = re.compile(
    r"\b(?:baby|babies|bump|pregnan\w*)\b[^.!?]{0,26}\b(?:due|coming|arriv\w+|induct\w+|"
    r"c-section|overdue|weeks)\b|"
    r"\b(?:contractions?|waters|midwife|health visitor|nursery)\b|"
    r"\b\d{1,2}\s*weeks?\s+(?:gone|pregnant|along)\b")


# The particle that belongs to the verb, so that it is not read as the body: "i cant come back on
# saturday" is a day, and the "back" in it is not the person's.
VERB_PARTICLE = re.compile(r"^\s*(?:in|into|back|out|up|round|along|over|down|home|here|there)\b")


# The thing the person was going to, named in an earlier turn: "im going to the party on
# saturday" then "i cant make it". The bare decline is the composer's own line only while the
# thing dropped is not in the chat, because a reply about the thing - the words to say to them,
# what a booking costs - is the answer once it is.
PLAN_ON_THE_TABLE = re.compile(
    r"\b(?:party|wedding|dinner|restaurant|table|booking|booked|reservation|appointment|"
    r"meeting|interview|gig|concert|cinema|drinks|lunch|brunch|barbecue|bbq|christening|"
    r"funeral|birthday|hen do|stag do|leaving do|catch up|get together|trip|holiday|flight)\b",
    re.I)


# The act of dropping the plan, which is the composer's own line wherever it is said: "gonna have
# to cancel" after the booking was named still wants the one sentence ready, not the booking card's
# "Nice one - tell me how it goes."
LINE_CANCELS = re.compile(r"\b(?:cancel\w*|call(?:ing)? (?:it )?off|called off|drop(?:ping)? out|"
                          r"pull(?:ing)? out|opt(?:ing)? out|back(?:ing)? out)\b", re.I)


def _the_line_cancels(line):
    """True when the line is the person dropping the plan, not only saying they cannot come."""
    return bool(LINE_CANCELS.search(str(line or "")))


def _a_plan_on_the_table(memory):
    """True when one of the last few turns names the thing the person is now dropping.

    Only an earlier line of theirs counts, and only the shape of a plan: a thing they were going
    to ("the party on saturday", "we booked a table for friday"). A chat with no such word in it
    leaves the bare decline to this composer, which is where it does its best work.
    """
    history = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-3:]
    for turn in history:
        said = str(turn.get("user") or "")
        if said and PLAN_ON_THE_TABLE.search(said):
            return True
    return False


def _hesitant_news_before(memory, turns=3):
    """True when one of the last few things the person said was bad news of their own.

    A death in the chat is asked separately (`_in_a_loss_thread`), and this is the rest of it:
    "my wife left me", "i lost my job", "my mum is in hospital". The reader is the composer's own
    (`badnews.reads_as_bad_news`), so the register is right for the news the rest of the bot
    already greets that way, and a plan dropped in that week is answered in it.
    """
    history = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-turns:]
    for turn in history:
        said = str(turn.get("user") or "").lower()
        if said and reads_as_bad_news(said):
            return True
    return False


# Not knowing what to say to somebody is its own ask, and NEUTRAL is the wrong answer to it: "I'm
# listening - say more if it helps" and "Got it. Is there anything you'd like a hand with?" both
# answer as if the person had said nothing, when what they said is that the words will not come.
# The written things have their own entries (a card, a note, a letter, an email) and a death, a
# harm or a loss has its own module, all of them ahead of this file, so what reaches here is a
# person with a conversation to have: the useful reply is one true sentence to open with.
NO_WORDS = re.compile(
    r"\b(?:dont|don't|do not|never|can'?t|cannot|cant)\s+"
    r"(?:ever\s+|really\s+|quite\s+|honestly\s+|know\s+)*what\s+to\s+"
    r"(?:say|tell|text|write to)\b"
    # The same thing said the other way round: the words will not come, without "what to say".
    r"|\b(?:can'?t|cannot|cant|lost|stuck)\s+(?:for|find)\s+"
    # The adjective is part of how people say it ("the right words", "the first words"), and
    # "ive lost my words" is the same line with no find in it.
    r"(?:(?:the|my|his|her|their|any)\s+)?(?:(?:right|first|proper|good)\s+)?words\b|"
    r"\b(?:lost|losing|at a loss for)\s+(?:my|the|his|her|their)\s+words\b|"
    r"\b(?:lost|struggling|struggle)\s+for\s+words\b", re.I)


# The things whose words are already known: a card, a note, a letter, an email, a speech. Those
# have entries of their own and reach this file only when they should not be answered here.
NO_WORDS_NOT = re.compile(
    r"\b(?:card|cards|note|notes|letter|letters|email|emails|speech|toast|eulogy|"
    r"write|writing|written|funeral|death|died|dying|passed away|cancer|hospice|"
    r"miscarriage|stillborn|divorce|wedding|birthday)\b", re.I)


# A talk with somebody named is opened for them, and a talk with a boss, a manager or a landlord
# is opened by saying what the person is asking for: the same "what to say" is two different
# sentences depending on who it is.
NO_WORDS_TO = re.compile(r"\b(?:to|for|about|with|tell|text|txt|ring|call|phone|message)\s+"
                         r"(?:him|her|them|his|their|my|our|the|a)\b", re.I)


# The person can be named without a preposition in front of them: "when she cries", "about my dad",
# "i cant find the words for him". A third-person pronoun anywhere is somebody to talk to, so it
# goes to the same pool - except "my"/"our", which is the speaker's own words, not a person.
NO_WORDS_SHE = re.compile(r"\b(?:him|her|his|hers|them|their|theirs|she|he|they)\b", re.I)


# A doctor, a dentist or a vet is not a heart-to-heart: those are appointments about a trouble, so
# the useful sentence is what to bring up first, not a line about having been thinking it over.
# A group is not the one person an opening line is written for: "to a group of people" and "to an
# audience" would be told to ask how they are today. Nothing here fits that, so it stands down.
NO_WORDS_CROWD = re.compile(r"\b(?:group|audience|crowd|panel|committee|everyone|whole class|"
                            r"room full|assembly|people)\b", re.I)


NO_WORDS_ONE = re.compile(r"\b(?:him|her|his|hers|she|he)\b", re.I)


NO_WORDS_CARE = re.compile(r"\b(?:doctor|doctors|gp|dentist|nurse|consultant|surgeon|specialist|"
                           r"vet|midwife|health visitor|optician|pharmacist|physio|"
                           r"physiotherapist|therapist|counsellor)\b", re.I)


NO_WORDS_ASK = re.compile(r"\b(?:boss|manager|hr|employer|landlord|landlady|client|customer|"
                          r"team|staff|colleague|interview|appraisal|review|landlord)\b", re.I)


def _no_words(clean):
    """The pool for a line that cannot find the words, or None."""
    if not NO_WORDS.search(clean) or NO_WORDS_NOT.search(clean):
        return None
    if NO_WORDS_ASK.search(clean):
        return NO_WORDS_ASKING
    if NO_WORDS_CARE.search(clean):
        return NO_WORDS_AT_THE_CARE
    if NO_WORDS_TO.search(clean) or NO_WORDS_SHE.search(clean):
        if NO_WORDS_CROWD.search(clean) and not NO_WORDS_ONE.search(clean):
            return None
        return NO_WORDS_SOMEONE
    return NO_WORDS_STUCK


# The talk that is the whole invitation: "fancy a chat", "shall we have a natter", "catch up".
INVITE_TALK = re.compile(r"\b(?:chat|talk|natter|chinwag|catch\s*up|a\s+word|gossip)\b", re.I)


# The opener, and the words people start a line with before it ("so", "hey", "right", "just").
INVITE_OPENER = re.compile(
    r"^(?:(?:so|ok|okay|right|well|hey|hi|oi|and|but|oh|ah|anyway|then|now|er|um|hmm|listen|"
    r"quick|just|actually)\s+)*"
    r"(?:(?:do|would|d)\s+(?:you|u)|(?:are|r)\s+(?:you|u)|you|maybe)?\s*"
    r"(?:fancy|want|like|up\s+for|coming|come|join\s+me|walk\s+with\s+me|"
    r"shall\s+we|should\s+we)\b(.*)$", re.I)


# "walk with me" and "join me" are the whole invitation, and "come with me" / "come along" too: the
# company is the ask, so no thing has to follow.
INVITE_COMPANY = re.compile(
    r"^(?:(?:so|ok|okay|right|well|hey|oi|and|but|oh|ah|anyway|then|now|just)\s+)*"
    r"(?:(?:do|would|d)\s+(?:you|u)\s+|(?:are|r)\s+(?:you|u)\s+|you\s+)?"
    r"(?:(?:come|walk|sit)\s+(?:with|along)\b(?:\s*(?:me|us))?|join\s+me\b|"
    r"(?:fancy|want)\s+(?:to\s+)?(?:com(?:e|ing)|tag(?:ging)?)\s+along\b)", re.I)


# The same openers with a question about the world after them are not invitations: "do you want to
# know how it works", "do you want me to ring them", "do you want a lift home".
INVITE_NOT_A_DOING = re.compile(
    r"^(?:know|hear|ask|tell|say|explain|check|bet|guess|see|read|talking|think|be|become|stay|"
    r"leave|go home|try|start|stop|help|mean|happen|me\b|hand|lift|ride|anything|something|"
    r"nothing|a go|a look|a word)\b")


# A tail that only says when, or asks about a time, is arranging rather than inviting.
INVITE_WHEN = re.compile(r"^(?:when|if|whether|whenever|unless)\b")


def _an_invitation(clean):
    """'talk', 'go' or None: which invitation this line is, if it is one."""
    line = " ".join(re.sub(r"[^a-z0-9 ']+", " ", str(clean or "").lower()).split())
    if not line or len(line.split()) < 2:
        return None
    if set(line.split()) & INVITE_NEVER:
        return None
    if INVITE_COMPANY.match(line):
        return "talk" if INVITE_TALK.search(line) else "go"
    found = INVITE_OPENER.match(line)
    if not found:
        return None
    tail = [w for w in found.group(1).split() if w not in INVITE_FILLER]
    if not tail:
        # "do you fancy a coffee tonight" is the same invitation once the time is off it.
        tail = [w for w in found.group(1).split()
                if w not in ("tonight", "today", "tomorrow", "later", "now", "soon", "after")]
    said = " ".join(tail)
    if not tail or INVITE_NOT_A_DOING.match(said) or INVITE_WHEN.match(said):
        return None
    if all(w in INVITE_PRONOUN for w in tail):
        return None
    if not set(tail) & INVITE_ACTIVITY and not INVITE_TALK.search(line):
        return None
    return "talk" if INVITE_TALK.search(line) else "go"


ONLY_FAR = re.compile(
    ONLY_FRONT + r"(?:(?:somewhere|something|some place|a place|a bit|a little|much|quite|really|"
    r"fairly|more|less|not|too|this|that|thats|that's|which is|its|it's|is)\s+)*"
    r"(?:far|near|nearby|nearer|close|closer|local|walkable|in the area|round the corner)"
    r"(?:\s+(?:away|out|by|enough|either|though|from here|to home|from the \w+))?$", re.I)


ONLY_PRICE = re.compile(
    ONLY_FRONT + r"(?:(?:a bit|much|more|a little|something|somewhere|the|ones?)\s+)*"
    r"(?:cheaper|cheap|pricier|dearer|not too (?:expensive|dear|pricey|much)|budget|affordable|"
    r"free|nothing (?:too )?(?:pricey|dear)|"
    r"(?:under|below|less than|no more than|max|maximum|up to|about|around)\s+"
    r"[\u00a3$\u20ac]?\d+\s*(?:pounds?|quid|grand|k|thousand|dollars?|euros?)?"
    r"(?:\s*(?:or so|ish|max|tops))?|"
    r"[\u00a3$\u20ac]?\d+\s*(?:pounds?|quid|grand|max|or so|ish))$", re.I)


ONLY_TIME = re.compile(
    ONLY_FRONT + r"(?:(?:a bit|much|more|a little|something|somewhere|the|ones?)\s+)*"
    r"(?:quick|quickly|quicker|fast|faster|soon|sooner|later|earlier|not long|no time|"
    r"not too long|in a (?:bit|minute|hour|day|week)|in an? \w+|"
    r"an? (?:hour|minute|day|week|moment|min)|(?:under|below|less than) an? (?:hour|minute|day|week|moment|min)|"
    r"(?:under|below|less than|no more than|max|maximum|up to|about|around|in)\s+"
    r"\d+\s*(?:mins?|minutes?|hours?|hrs?)|"
    r"\d+\s*(?:mins?|minutes?|hours?|hrs?)(?:\s*(?:or so|max|tops))?)$", re.I)


ONLY_EFFORT = re.compile(
    ONLY_FRONT + r"(?:(?:a bit|much|more|a little|something|somewhere|the|ones?)\s+)*"
    r"(?:easy|easier|simple|simpler|no fuss|not much fuss|low effort|minimal effort|"
    r"not too much (?:work|effort|faff)|no faff|quick and easy|nothing (?:fiddly|complicated))$",
    re.I)


ONLY_SIZE = re.compile(
    ONLY_FRONT + r"(?:(?:a bit|much|more|a little|something|somewhere|the|ones?)\s+)*"
    r"(?:small|smaller|big|bigger|tiny|compact|roomy|not too (?:big|small|large)|"
    r"on the small side|on the big side)$", re.I)


NARROW_AXES = (("time", ONLY_TIME), ("price", ONLY_PRICE), ("far", ONLY_FAR),
               ("effort", ONLY_EFFORT), ("size", ONLY_SIZE))


# The pools above ask for the bound. That is the right question when the line only says which way to
# cut - "not too far", "cheaper", "quicker" - and the wrong one when the line already carries it:
# "under 20 minutes" after "tuna pasta in 15, a frittata in 20" was answered "How many minutes have
# you got?", and "about 300 pounds" after the October destinations was answered "Cheaper, then.
# What's your limit?" - which asks for a figure the person just gave and asserts a preference they
# never said. A bound in the line is the person answering the question already, so the reply says it
# back and points it at the things on the screen.
BOUND_SAID = re.compile(
    r"\b(?:under|below|less than|no more than|not more than|at most|max|maximum|up to|within|"
    r"about|around|roughly|only)\s+(?:\d|a\b|an\b|one|two|three|five|ten|twenty|thirty|forty|"
    r"fifty|sixty|ninety|a hundred|half)"
    r"|\b\d|\bhalf an hour\b|\ban hour\b|\ba tenner\b|\ba fiver\b|\ba couple of hours\b",
    re.I)


def the_bound_said(clean):
    """The bound the line itself names, said back the way they said it, or ""."""
    line = " ".join(str(clean or "").strip().split())
    found = BOUND_SAID.search(line)
    if not found:
        return ""
    rest = line[found.start():]
    rest = re.sub(r"[^\w\s£$€.,-]", " ", rest).strip(" .,")
    words = rest.split()
    return " ".join(words[:5]).rstrip(" .,")


def reads_as_a_narrowing(clean):
    """The axis this line narrows on, or "" when it is not only a constraint.

    Only a line that is the constraint and nothing else comes here: "not too far" and "under 20
    minutes" are this, and "is it cheaper in june" and "the car is cheap but it needs work" name a
    subject of their own and keep the readers that can answer those.

    Two limits in one line - "cheap and not too far", "not too far and cheap", "under 20 minutes and
    easy" - are read by `the_limits_said`, which puts the part that carries a bound first: a line
    joined by "and" matched neither pattern and was said back ("Got it - cheap and not too far"),
    which gives the person nothing to answer and does not cut the answer above either. This returns
    the first axis of that reading, which is the one the reply starts with.
    """
    limits = the_limits_said(clean)
    return limits[0][0] if limits else ""


# The words that join two limits into one line. A line with a part that is not a limit ("cheap and
# cheerful", "something not too far from the station") is not only a limit, and keeps whatever the
# composers after this one make of it.
NARROW_JOIN = re.compile(r"\s*(?:,|&|\band\b|\bplus\b)\s*", re.I)


def the_limits_said(clean):
    """The limits a line of joined limits names, in the order a reply should try them.

    "cheap and not too far" and "under 500 pounds and not too far" are one line with two limits in
    it, and the reply has to pick one to ask about. The part that carries a bound comes first: the
    person has already answered the question that part asks - "under 500 pounds" - so saying it
    back and pointing it at the things on the screen is the most the reply can do. The other parts
    follow, the last said first, because the limit said last is the one the next answer has to
    meet. The parts are tried in that order against the answer above, and the first one the answer
    can be cut on is the one the reply asks about: "under 500 pounds each and not too far" after
    four destinations that quote no prices is a distance to cut, not a price.

    Returns [(axis, part), ...] and nothing when the line is not only limits - a line with a part
    that is not one ("cheap and cheerful", "something not too far from the station") keeps
    whatever the composers after this one make of it.
    """
    line = " ".join(str(clean or "").strip().split())
    if not line or line.rstrip().endswith("?") or len(line.split()) > NARROW_WORDS:
        return []
    parts = [part for part in NARROW_JOIN.split(line) if part]
    if not parts:
        return []
    axes = [_one_axis(part) for part in parts]
    if not all(axes):
        return []
    with_bound = [(axis, part) for axis, part in zip(axes, parts) if the_bound_said(part)]
    without = [(axis, part) for axis, part in zip(axes, parts) if not the_bound_said(part)]
    return with_bound[::-1] + without[::-1]


def _one_axis(line):
    """The one axis a piece of a line narrows on, or ""."""
    for axis, pattern in NARROW_AXES:
        if pattern.match(line):
            return axis
    return ""
