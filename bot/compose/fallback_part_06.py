"""Part 6 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from . import (trouble)

from .fallback_data import (
    ADVICE_LENGTH,
    ADVICE_LENGTH_BARE,
    AT_IT_EXTRA,
    BECOMING,
    BECOMING_STATE,
    AT_IT_NOT,
    A_PERSON,
    DONE_NOT_A_PERSON,
    DONE_NOT_THIS,
    DONE_ONLY_A_THING,
    DONE_VERB,
    GRIEVANCE_HARM,
    GRIEVANCE_HEALTH,
    IDIOM_GLAD,
    IDIOM_SHY,
    MYSELF,
    MY_DOING,
    NOT_ENOUGH_REPLY,
    NO_DIRECTION_REPLY,
    PLAN,
    PLAN_DONE,
    QUESTION_OPENERS,
    SUMMONS_RANG,
    SUMMONS_SEEN,
    SUMMONS_WRITTEN,
)

from .fallback_part_05 import (
    AT_IT, A_TROUBLE_IN_THE_TAIL, BEEN_AT_IT, DID_AT_IT, DONE_ING, FEELING_OFF, FUTURE_TIME,
    HABIT_TIME, HARM_AFTER, HARM_ANYWHERE, HARM_NAMED, HARM_ON_ME, SPENT_TIME, TAIL_ASK,
    TAIL_GRUMBLE, TAIL_TROUBLE, TIME_SPAN, WENT_AT_IT, _a_thing_after, _tail_complains, MISHAP_FELL,
)


def _a_thing_done(clean):
    """True when the line reports a small thing the person did, which nothing else answers."""
    return _thing_done_shape(clean) is not None


def _thing_done_shape(clean):
    """Just the shape: see `_thing_done_scan`."""
    return _thing_done_scan(clean)[0]


def _thing_done_scan(clean):
    """(shape, verb) for this line, or (None, "") when it is not a thing done.

    The shape is "done" for a finished thing ("i painted the fence today") and "going" for one
    still under way ("i've been painting the fence all morning"); the verb is the one the shape
    was read from, because the pool depends on it ("how do you feel now it's finished?" fits a
    fence and not a walk).

    A question is not a report ("did you paint the fence"), and a "but" turns the line into a
    mixed one the pools for trouble and feeling answer better. So does a negative word: "i
    cleaned the kitchen but it looks the same" is a grumble, not news.
    """
    if ("?" in clean or " but " in clean or TAIL_ASK.search(clean)
            or TAIL_GRUMBLE.search(clean) or TAIL_TROUBLE.search(clean)
            or _tail_complains(clean)):
        return None, ""
    if (clean.split() or [""])[0] in QUESTION_OPENERS:
        return None, ""
    if NEGATIVE_LINE.search(clean):
        return None, ""
    # A complaint tacked onto the doing is not news: "i went to the gym and my knee is killing me"
    # wants the question about the knee, and "i did yoga and my back is worse" was not a good
    # afternoon. trouble.py already reads one, so it keeps the turn; the second gate is only for
    # the "is worse" shape, which names no harm word at all.
    if trouble.reads_as_trouble(clean, tuple(re.findall(r"[a-z']+", clean)), clean):
        return None, ""
    if HARM_AFTER.search(clean):
        return None, ""
    if HARM_NAMED.search(clean) or HARM_ON_ME.search(clean):
        return None, ""
    # A job with something wrong at the end of it is not an afternoon well spent: "im decorating
    # and the fumes are making me dizzy", "im tiling and ive run out of tiles". Neither is a
    # complaint about the job ("its a nightmare", "its taking forever"): the cheerful question
    # ("Nice one - nearly there?") reads as if the bot had not heard the rest of the line.
    if FEELING_OFF.search(clean) or A_TROUBLE_IN_THE_TAIL.search(clean):
        return None, ""
    # "ive been painting the fence all morning" is the same afternoon as "i've been painting the
    # fence all morning", and only the apostrophe was read: the shape has to be read off a line
    # with the contraction spelled out.
    text = re.sub(r"\b(?:ive|i've)\b", "i have", clean)
    text = re.sub(r"\b(?:weve|we've)\b", "we have", text)
    text = re.sub(r"\b(i|we)'d\b", r"\1 had", text)
    words = re.findall(r"[a-z']+", text)
    for i in range(len(words) - 1):
        if words[i] not in ("i", "we"):
            continue
        j = i + 1
        while j < len(words) and words[j] in ("just", "also", "finally", "only", "actually",
                                              "have", "had", "been"):
            j += 1
        if j >= len(words) or words[j] not in DONE_VERB:
            continue
        rest = words[j + 1:j + 3]
        if any(w in DONE_NOT_THIS for w in rest):
            return None, ""
        if (words[j] in DONE_ONLY_A_THING
                and any(w in DONE_NOT_A_PERSON for w in words[j + 1:j + 4])):
            return None, ""
        return "done", words[j]
    # Chat-speak drops the pronoun: "booked the hotel last night", "paid the deposit", "cancelled
    # the gym" are the same report with no "i" in it. The subject was the only thing the reading
    # wanted, so every one of them was answered as a request for instructions - "booked the hotel
    # last night" got the choose-a-hotel card, "cleaned the kitchen" the clean-a-kitchen one - or
    # with the neutral nod. Every word in DONE_VERB is a past tense, so a line that opens on one is
    # a report and not an instruction ("clean the kitchen" is the instruction, and it is not in the
    # list): that is the whole of the fence, and it is why the shape is read off the verb's form
    # rather than off a list of what a person might report.
    if words and words[0] in DONE_VERB and not HARM_ANYWHERE.search(clean):
        rest = words[1:3]
        if not any(w in DONE_NOT_THIS for w in rest):
            return "done", words[0]
    # A day's doing is not always said with the verb of the doing: "i went for a run", "i went to
    # the gym", "i did a workout", "i went swimming". Reading only DONE_VERB left every one of
    # those with "I'm listening", and "i went for a run this morning" was the only one that got a
    # question, from a different arm. The verb of going or doing says nothing on its own - "i went
    # home", "i went to the doctor", "i did the washing up" are not an afternoon's work - so the
    # object is what has to be in the list.
    went = WENT_AT_IT.search(text)
    if went:
        return "gone", "went"
    did = DID_AT_IT.search(text)
    if did:
        return "gone", "did"
    spent = SPENT_TIME.search(text)
    if spent and spent.group(1) in DONE_ING:
        return "going", spent.group(1)
    been = BEEN_AT_IT.search(text)
    if been and been.group(1) in DONE_ING and TIME_SPAN.search(text):
        return "going", been.group(1)
    at_it = AT_IT.search(text)
    if at_it and (at_it.group(1) in DONE_ING or at_it.group(1) in AT_IT_EXTRA):
        rest = text[at_it.end():]
        # "im getting fat" is a state, not a job under way: see BECOMING in fallback_data.
        if at_it.group(1) in BECOMING and (rest.split() or [""])[0] in BECOMING_STATE:
            return None, ""
        if (_a_thing_after(rest) and not HABIT_TIME.search(rest)
                and not any(word in AT_IT_NOT for word in re.findall(r"[a-z']+", rest))):
            return ("soon" if FUTURE_TIME.search(rest) else "at"), at_it.group(1)
    return None, ""


# Something sharp underfoot or in the hand. The thing named is what makes it a body line, because
# "i stepped on the scales" and "stood on the platform" are an errand.
MISHAP_UNDERFOOT = re.compile(
    r"\bi\b[^.?!]{0,20}?\b(?:stepped|stood|trod|walked|planted|knelt)\b[^.?!]{0,6}?"
    r"\b(?:on|in(?:to)?)\b[^.?!]{0,6}?"
    r"(?:a|an|some|the|broken|bits\s+of|a\s+bit\s+of|two)\s+(?:nail|nails|glass|needle|needles|"
    r"lego|thorn|thorns|screw|screws|tack|tacks|pin|pins|shard|shards|spike|spikes|drawing\s+pin|"
    r"sharp\s+thing|rusty\s+nail)\b"
    r"|\b(?:got|had)\s+(?:a\s+)?(?:bit\s+of\s+|piece\s+of\s+|shard\s+of\s+)?(?:glass|grit|"
    r"metal|a\s+nail|a\s+thorn)\s+(?:in|into)\s+my\b"
    r"|\b(?:a\s+)?(?:nail|screw|thorn|needle|splinter|bit\s+of\s+glass)\s+(?:went\s+|stuck\s+)?"
    r"(?:through|in(?:to)?)\s+my\b")


# A sense that has gone. No harm word names these, and a line about going blind in one eye is the
# last thing that can be answered "sounds alright".
SENSE_GONE = re.compile(
    r"\bmy\s+(?:vision|sight|hearing)\s+(?:has\s+|had\s+|suddenly\s+)?(?:gone|went)\b"
    r"|\b(?:went|gone|going)\s+(?:blind|deaf)\b"
    r"|\b(?:cant|cannot|can'?t)\s+see\s+(?:out\s+of|anything\s+out\s+of)\b")


MISHAP_ANYWHERE = re.compile(
    "|".join(("(?:" + MISHAP_FELL.pattern + ")",
              "(?:" + MISHAP_UNDERFOOT.pattern + ")",
              "(?:" + SENSE_GONE.pattern + ")")))


# A mishap that is over, or that never happened. "i fell off the roof last summer", "i nearly fell
# off the ladder", "my dad fell off a ladder but hes ok": the person is telling the story of a
# thing that is finished, and "how bad is it" asks about a fall that is not happening. The day
# question is the right one on those turns, so this reading steps out of the way.
MISHAP_OVER = re.compile(
    r"\b(?:last\s+(?:year|summer|winter|spring|autumn|christmas|month)|years?\s+ago|"
    r"when\s+i\s+was|as\s+a\s+(?:kid|child|teen|youngster|little\s+one)|used\s+to|"
    r"back\s+in\s+(?:the\s+)?(?:day|\d{4}|nineteen|twenty))\b"
    r"|\b(?:nearly|almost|close\s+to)\b"
    r"|\b(?:but|and|though)\s+(?:he|she|they|it|we|i)\s*(?:'?s|re|is|was|were|am)?\s*"
    r"(?:ok|okay|alright|all\s+right|fine)\b"
    # "i tripped over my words on the call": the verb is the trip, the thing is not a floor
    r"|\b(?:over|on)\s+(?:my|his|her|their|our|your|the)\s+(?:own\s+)?(?:words|tongue)\b")


def _a_mishap_to_ask_about(text):
    """A mishap that no card answered, the day question has to leave alone.

    A fall already over is not one: "i fell off the roof last summer", "i nearly fell off the
    ladder" and "my dad fell off a ladder but hes ok" are the account of a day, and the question
    about the day is right on those turns. A sense that has gone is the exception in the other
    direction - "my vision has gone in my left eye" is not a day with anything good in it, even
    though no pool asks how bad it is.
    """
    if SENSE_GONE.search(text):
        return True
    if not MISHAP_ANYWHERE.search(text):
        return False
    return not MISHAP_OVER.search(text)


def _a_mishap(clean, words):
    """True for a mishap said as an account of the day, with a question back for it.

    Only the two shapes with a landing in them ask "how bad is it": a fall and something sharp
    underfoot. A sense that has gone is the careful reading's, and asking somebody how bad their
    eyesight is when it went this morning is not the question - it is the turn above that answers
    that one.
    """
    if not clean or "?" in clean or len(words) > 24:
        return False
    if MISHAP_OVER.search(clean):
        return False
    return bool(MISHAP_FELL.search(clean) or MISHAP_UNDERFOOT.search(clean))


NEGATIVE_LINE = re.compile(
    r"\b(?:ruined|wasted|broke|broken|failed|went wrong|couldn'?t|couldnt|didn'?t|didnt|"
    r"forgot|messed|gave up|hate[sd]?|awful|terrible|useless|a waste|nobody|no one|"
    r"horrib\w*|miserab\w*|dreadful|soaked|drenched|freezing)\b")


NOT_ENOUGH = re.compile(
    rf"\b{MYSELF}\s+(?:am\s+)?(?:just\s+|still\s+|really\s+|always\s+)?(?:not|never)\s+"
    rf"(?:\w+\s+){{0,2}}(?:enough|good enough)\b"
    rf"|\bmy (?:{MY_DOING})\s+(?:is|was|isnt|isn'?t|wasnt|wasn'?t)?\s*"
    rf"(?:just\s+|never\s+|still\s+|always\s+)?(?:not\s+)?(?:good\s+)?enough\b"
    r"|\bfeel (?:like )?(?:im|i'?m|i am)?\s*(?:a )?(?:failure|fraud|useless|a waste|"
    r"letting (?:people|everyone|my family) down)"
    r"|\b(?:im|i'?m|i am)\s+(?:such\s+)?(?:a failure|a fraud|useless|a burden|a waste of space)\b"
    r"|\b(?:letting|never there for) (?:people|everyone|my family|everybody) down\b"
    r"|\bbehind (?:everyone|in life|on everything)\b"
    r"|\bwasting my (?:life|time|twenties|thirties|20s|30s)\b"
    # Keeping up is about the person only where what they are behind on is a thing to be
    # judged on. "i cant keep up with the washing" is a pile of washing, not a standard anyone
    # set for them, so the thing has to be named.
    r"|\b(?:cant|cannot|can'?t) keep up (?:at|in) (?:work|school|uni|university|college|class|"
    r"my course|my job|my studies)\b"
    r"|\b(?:cant|cannot|can'?t) keep up with (?:everything|it all|the lot|the work|everyone|"
    r"my classmates|the others)\b"
    r"|\b(?:cant|cannot|can'?t) (?:cope|do this anymore)\b")


NO_DIRECTION = re.compile(
    # Not knowing what you want is a direction question whatever follows: "i still dont know
    # what i want to do", "i dont know what i want out of work".
    r"\b(?:dont|don'?t|never)\s+know what (?:i\s+)?want\b(?=\s*(?:to do\b|with my life|"
    r"out of|from (?:life|work|mine)\b|$))"
    # Not knowing what to do is only the same thing when the line names the direction it is
    # lost in. A bare "i dont know what to do" after a broken boiler, a lost job or a landlord
    # who will not fix the heating is the ordinary way of saying the thing beat them, and the
    # nod that offers a hand is the honest reply to it.
    r"|\b(?:dont|don'?t|never)\s+know what to do\b(?=\s*(?:with my life|with myself|out of|"
    r"from (?:life|work|mine)\b|with the rest of it\b))"
    r"|\b(?:dont|don'?t|never)\s+know what (?:im|i'?m|i am) (?:doing|supposed to be doing)\b"
    r"|\bno idea what (?:im|i'?m|i am) doing\b"
    r"|\b(?:im|i'?m|i am) \d{2} and i (?:still )?(?:dont|don'?t) know\b"
    r"|\b(?:nothing|no plan|no idea) (?:feels|seems) right\b")


# The lost-at-sea line that is written as a question. `_own_feeling` refuses a question, which
# is right for "what should i do with my life", and this is the one shape where the person is
# not asking the bot anything.
LOST_QUESTION = re.compile(
    r"\bwhat (?:am i|im|i'?m) (?:even )?(?:doing|going to do|going to do with myself) with my "
    r"(?:life|time|day|week|twenties|thirties)\b")


# Another person's trouble is not the speaker's own feeling ("my mum says she isnt good enough"),
# and a question is not a statement about how things are.
NOT_SELF = re.compile(r"\b(?:he|she|they|him|her|them|his|their|my (?:mum|mom|dad|boss|son|"
                      r"daughter|partner|husband|wife|friend|sister|brother|colleague|manager))\b")


# A stated dislike with nothing under it to object to - "i hate presenting", "i cant stand
# cats", "i dont like cooking" - is a taste, not news, so every reading above stands down and
# the memory store files it: ack says the line back as "Noted: you hate presenting." That is a
# receipt for a sentence rather than a reply to it, and the coldest line in this file, and it
# ends the conversation: the person has named a thing they cannot bear and the bot has said
# nothing about it. `obstacle` answers the dislike that objects to an answer it was just given
# ("i hate exercise" after the plan); with no answer under it, the one part this file can still
# do is ask about the thing, which is what a friend does with "i hate presenting" - the thing is
# their own words and the question is about them, so it is not a stock line.
#
# The thing has to be short and one thing: "i hate my job but it pays well" is a grievance with
# two halves, and "i cant stand the way my sister talks to me" is about somebody's behaviour,
# both of which the readings above answer better than a question about the whole clause.
DISLIKE_ASKS = (
    "What is it about {thing} that gets you?",
    "Fair enough. What is it about {thing}?",
    "What is it about {thing} you don't like?",
    "{Thing} \u2014 what is it that gets you about it?",
)


DISLIKE_TOO_LONG = 6


DISLIKE_HAS_TWO_HALVES = re.compile(r"\b(?:and|but|because|so|though|although|when|if)\b", re.I)


# Words that hang off the thing rather than name it: "i hate the commute already" is a dislike of
# the commute, and asking about "the commute already" reads like a machine quoting the line.
DISLIKE_TAIL = re.compile(
    r"(?:[\s,]+(?:already|now|too|though|tho|anymore|any\s+more|at\s+the\s+moment|"
    r"right\s+now|so\s+much|that\s+much|these\s+days|all\s+the\s+time|as\s+well|anyway|"
    r"honestly|tbh|btw|lol|ha))+$", re.I)


# The thing is the person's own words, and their `my` belongs to them: "i dont like my body" was
# answered "What is it about my body that gets you?", which is the bot asking about its own body.
# The possessive turns with the question; a thing that is nobody's ("the commute") is unchanged.
DISLIKE_OWN = re.compile(r"\b(?:my|our)\b", re.I)


DISLIKE_OWN_SELF = re.compile(r"\bmyself\b", re.I)


# The same taste with the "i" left out: "not 2 keen on the new place", "not a fan of the open
# plan", "not too fussed about the colour". People drop the subject in a chat, and the store
# reads a taste from a first person verb, so the subject-less line gave nothing to object to:
# "not 2 keen on the new place" got "Got it. Is there anything you'd like a hand with?" and
# "not too keen on it" got "I'm listening - say more if it helps", while "im not keen on the new
# place" was asked about the place. The thing is the same thing and the question is the same.
DISLIKE_WITHOUT_AN_I = re.compile(
    r"^\W*(?:(?:and|but|so|oh|also|well|yeah|yep|ok|okay|right|alright|honestly)\W+)*"
    r"(?:not|n't)\s+(?:(?:really|that|too|2|very|so)\s+)?(?:(?:much|a\s+bit)\s+of\s+)?"
    r"(?:a\s+)?(?:keen|fan|fond)\s+(?:of|on|about|for)\s+(?P<thing>[^?.!]+)$", re.I)


# A pronoun is not a thing to ask about: "not a fan of it" points at what was already said, and
# the composer answers that from the thread, not from the line.
NOT_A_THING_ASKED = frozenset("""it its it's that this these those them him her you me
    everything anything something nothing""".split())


def _own_feeling(clean):
    """The pool for a statement about the speaker's own worth or direction, or None."""
    if clean.rstrip().endswith("?") or NOT_SELF.search(clean):
        return None
    if NOT_ENOUGH.search(clean):
        return NOT_ENOUGH_REPLY
    if NO_DIRECTION.search(clean):
        return NO_DIRECTION_REPLY
    return None


# A letter that asks the person to ring them is not answered in writing: "i got a letter from the
# council asking me to call" got "Answer it in writing rather than by phone", which is the
# opposite of what the letter asked. The shape is still the letter's, but the reply they need is
# the call one.
SUMMONS_ASKS_A_CALL = re.compile(
    r"\b(?:ask|asks|asking|asked|tell|tells|telling|told|want|wants|wanting)\s+me\s+to\s+"
    r"(?:call|ring|phone|get in touch)\b")


def _summons_pool(summons, line=""):
    """The lines for a summons, by shape: a meeting, a letter, or a phone call."""
    shape = summons.get("shape") if isinstance(summons, dict) else None
    if shape == "written":
        if SUMMONS_ASKS_A_CALL.search(line):
            return SUMMONS_RANG
        return SUMMONS_WRITTEN
    if shape == "rang":
        return SUMMONS_RANG
    return SUMMONS_SEEN


# Something of the speaker's being in the way counts as impact: "parking in my space",
# "eating my food", "changing my shifts". The person themselves ("my sister", "my landlord")
# is not a thing of theirs, so "my brother always wins at chess" is still just news.
# A thing of yours only counts when the line also says it keeps happening: "someone keeps
# parking in my space" is a grumble, "i'm selling my car" and "it's me, my partner and our
# dog" are not. Without the recurrence, any possessive reads as an insult.
GRIEVANCE_RECUR = re.compile(r"\b(?:keeps?|kept|always|never|constantly|forever|again|"
                             r"every (?:day|night|morning|week|time|monday|weekend)|all the "
                             r"time|day after day|week after week)\b")


GRIEVANCE_MINE_THINGS = re.compile(r"\b(?:my|our)\s+([a-z']+)")


GRIEVANCE_MINE = re.compile(r"\bi (dont|don't|cant|can't|never|keep|keeps|always|wont|won't|"
                            r"refuse|refused|forget|forgot|cancel|promised)\b")


# A promise that keeps not happening: "he keeps saying next week", "she says shell come but never
# does", "the school keeps saying they will ring me back". Somebody has said something about a
# thing that has not arrived, and nothing in the grievance reader sees it - there is no impact word
# and nothing of the speaker's in the way - so every one of these went to "I'm listening" or
# "Thanks for telling me", the lines that fit any message, said to a person who has just described
# a promise that keeps moving. The reply leads with the thing the bot does know (a promise that
# moves every time is a pattern, not a date) and then names the one place that settles it: the day
# itself, asked for in writing.
#
# The words are read as reported speech and not as the speaker's own: "what should i say to my
# boss" has a person, a "say" and a "should" and none of the promise, and a deck scan caught it
# the moment the say-verb was allowed to stand on its own.
PROMISE_PEOPLE = (
    r"(?:mum|mom|mother|dad|father|parents|sister|brother|son|daughter|kid|kids|child|children|"
    r"wife|husband|partner|boyfriend|girlfriend|ex|fiance|fiancee|mate|friend|flatmate|housemate|"
    r"lodger|neighbour|neighbor|boss|manager|colleague|coworker|carer|nan|nana|grandma|grandad|"
    r"granny|aunt|uncle|cousin|stepdad|stepmum|landlord|agency|solicitor|builder|plumber|mechanic|"
    r"dealer|garage|contractor|tradesman|workman|electrician|cleaner|tutor|teacher|headteacher|"
    r"social worker|doctor|gp|dentist|nurse|therapist)")


PROMISE_OFFICES = (
    r"(?:council|school|college|university|landlord|letting agent|agent|bank|building society|"
    r"shop|store|company|employer|hr|boss|manager|surgery|gp|doctor|dentist|hospital|clinic|dwp|"
    r"jobcentre|job centre|insurance|supplier|provider|broadband|water company|housing "
    r"association|housing|department|office|service)")


# who said it, and what they said
_PROMISE_SAYS = (r"(?:say|says|said|saying|tell|tells|told|telling|swear|swears|swore|swearing|"
                 r"promise|promises|promised|promising)")


_PROMISE_KEEPS = r"(?:keeps?\s+|kept\s+|always\s+|still\s+|just\s+|only\s+)?"


PROMISE_OFFICE = re.compile(r"\b" + PROMISE_OFFICES + r"\b")


PROMISE_A_PERSON_NAMED = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:[a-z]+\s+){0,2}?" + PROMISE_PEOPLE + r"\b")


PROMISE_REPORTED = re.compile(
    r"\b(?:he|she|they|hes|shes)\s+" + _PROMISE_KEEPS + _PROMISE_SAYS + r"\b"
    r"|\b(?:my|our|his|her|their)\s+(?:[a-z]+\s+){0,2}?" + PROMISE_PEOPLE + r"\s+"
    + _PROMISE_KEEPS + _PROMISE_SAYS + r"\b"
    r"|\b" + PROMISE_OFFICES + r"\s+" + _PROMISE_KEEPS + _PROMISE_SAYS + r"\b"
    r"|\b(?:promise|promises|promised|promising|swear|swears|swore|swearing)\b")


PROMISE_FUTURE = re.compile(
    r"\b(?:will|wont|won't|going to|gonna|next (?:week|month|weekend|time|"
    r"day|year)|tomorrow|soon|later|sometime|eventually|hell|he'll|shell|she'll|theyll|"
    r"they'll|promised|promises?|ring back|call back|get back to me|sort it|do it|"
    r"pay me back|pay it back|take the kids|in the post|by (?:noon|midnight|monday|tuesday|"
    r"wednesday|thursday|friday|saturday|sunday|the end of|christmas|new year|the weekend)|"
    r"end of the (?:week|month)|next few days|after (?:christmas|new year|the weekend))\b")


# There has to be a promise in the line and an outcome that did not arrive: the reported speech
# with a future in it ("says hell do it"), or the set phrase for one that keeps not happening
# ("but never does", "never does what he says"). Without that "she never says well done" and "my
# partner doesnt do long drives" have the shape and none of the promise.
PROMISE_BUT_NEVER = re.compile(
    r"\b(?:but|and)\s+never\s+(?:does|do|did|comes|came|happens|happened|turns up|shows up|"
    r"pays|paid|rings|rang|calls|called|sorts? it|gets round to it)\b")


PROMISE_NEVER_WHAT = re.compile(r"\bnever does what\b|\bnever follows through\b")


# A promise is the one that keeps moving, so the line needs the recurrence word as well as the
# future in it: "my mum says i should ring my aunt more" has reported speech and a "should" and is
# advice, not a promise.
# Nothing a line about a promise can say is right for a line that is really about a harm: "shes
# saying she might do it again" has the shape of a promise that keeps moving and is not one.
PROMISE_RISK = re.compile(
    r"\b(?:kill|killed|killing|suicide|suicidal|overdose|self.harm|end it|end it all|"
    r"not be here|be dead|die|dying|do it again|do something stupid|take my own life|"
    r"hurt (?:myself|himself|herself|themselves)|cut (?:myself|himself|herself|themselves))\b")


PROMISE_RECUR = re.compile(r"\b(?:keeps?|kept|always|constantly|forever|again|every time|"
                           r"still|never)\b")


# A machine saying something is not a promise: "my phone keeps saying storage full", "my printer
# keeps saying paper jam", "my tv keeps saying no signal" all have the shape of one, and the
# device answers own them.
PROMISE_NOT_A_PERSON = re.compile(
    r"\b(?:phone|laptop|printer|tv|television|boiler|app|apps|screen|router|computer|tablet|"
    r"washing machine|dishwasher|oven|car|watch|kindle|console|xbox|playstation|alexa|siri|"
    r"fridge|freezer|heating|thermostat|meter)\b")


# What is owed is a debt, not a promise: the money pools answer "he wont pay" and "he keeps saying
# hell pay me back" with the asking-for-it line, which is the one they need.
PROMISE_MONEY = re.compile(
    r"\b(?:pay|pays|paid|paying|owes|owe|owed|owing|loan|lent|borrow|borrowed|rent|bill|bills|"
    r"mortgage|wages|salary|quid|pounds|grand|deposit|invoice|refund|compensation)\b")


# "they" after an office is the office: "the school keeps saying they will ring me back" is the
# school, and only a he or a she makes the same words personal.
PROMISE_A_HE_OR_SHE = re.compile(r"\b(?:he|she|him|his|her|hes|shes)\b")


PROMISE_A_PERSON = (
    "A promise that moves every time is a pattern, not a date. Ask for the day itself, in a "
    "message, so there is something written down - which day, and put it in the calendar - and "
    "believe the answer rather than the intention. What is it they keep putting off?",
    "Stop asking whether it will happen and ask what has happened: one small thing this week, "
    "in writing. A day that slips again is the answer, and it is better to know that before you "
    "count on it. What have you been counting on?",
    "Say it once, plainly, and ask which day they mean: a promise that never gets a day is the "
    "thing worth testing, and testing it is fairer than deciding what they are like. What would "
    "change for you if it actually happened?",
)


PROMISE_AN_OFFICE = (
    "A phone-back that never comes is worth putting in writing: the reference, the day you "
    "asked, and one clear question. The complaints address on their own site is read by "
    "somebody who can answer it, and it leaves a record. What were you waiting on?",
    "Ask by email so it stops being a conversation: what was promised, who said it, and the "
    "day you want it by. That same note is the one a complaint or an ombudsman asks for, so it "
    "is worth writing once. What is the thing they keep not doing?",
    "Ring once more, quote the day they gave you, and ask for the answer in writing: a promise "
    "on the record sits in a different queue from one made on a phone call. When did they first "
    "say it?",
)


def _a_promise_that_keeps_moving(clean):
    """The reply to a promise that keeps not happening, or None."""
    reported = PROMISE_REPORTED.search(clean)
    device = PROMISE_NOT_A_PERSON.search(clean)
    if device and (reported is None or device.start() < reported.start()):
        # The machine is the one saying it: "my phone keeps saying storage full", and the device
        # answers own those. A boiler named after the promise is the thing being promised, not
        # the speaker - "my landlord keeps saying hell fix the boiler".
        return None
    if PROMISE_MONEY.search(clean) or PROMISE_RISK.search(clean):
        return None
    said = set(re.findall(r"[a-z']+", clean.replace("\u2019", "'")))
    # An office is the subject when it is named and no person is: "the hospital keeps saying they
    # will send an appointment" is a phone-back, and the word hospital there is where the
    # appointment is from rather than a body to be careful about.
    office_subject = (bool(PROMISE_OFFICE.search(clean))
                      and not PROMISE_A_HE_OR_SHE.search(clean)
                      and not PROMISE_A_PERSON_NAMED.search(clean))
    if not office_subject and (said & GRIEVANCE_HEALTH or said & GRIEVANCE_HARM):
        # A body, an illness or a harm wants the care line, never a word about a promise.
        return None
    broken = PROMISE_BUT_NEVER.search(clean)
    if not (PROMISE_NEVER_WHAT.search(clean)
            or (reported and (
                (PROMISE_RECUR.search(clean) and PROMISE_FUTURE.search(clean))
                or (broken and broken.start() > reported.end())))):
        return None
    return PROMISE_AN_OFFICE if office_subject else PROMISE_A_PERSON


# A person who has just been told what to do and says it is doable is not asking anything: they
# have decided to do it. "ok that sounds doable" was answered with "I'm listening - say more if it
# helps", which asks them to say more at the exact moment they have said the useful thing, and
# "that sounds doable, thanks" with the neutral nod, which thanks somebody for accepting a plan.
# The same reading the PLAN pool gives a next step, for the line that gives no step of its own:
# say go on, and name the one thing that makes a set of steps work - the first bit, done properly.
# It is only ever a judgement of the answer: the line has to be short, has to name no subject of
# its own, and has to come after an answer with advice in it (`the_advice`), so "the door is
# doable in a weekend" and "nothing is doable today" are left to the modules.
DOABLE = re.compile(
    r"\b(?:doable|manageable|easy\s+enough|not\s+too\s+bad|simpler\s+than\s+i\s+thought|"
    r"easier\s+than\s+i\s+thought|that\s+(?:should\s+)?work|worth\s+a\s+(?:go|try)|"
    r"i\s+(?:can|could)\s+do\s+(?:that|it))\b", re.I)


# A judgement of the answer is built out of these words and nothing else. The fence is the
# vocabulary rather than a list of things, because what must not be read is any line with a
# subject of its own in it: "the door is doable in a weekend" and "the pain is manageable" are
# about a door and a back, and the only words a judgement of the line above can use are the
# judgement, the pointer at that line ("that", "it", "sounds") and the breathers around it.
DOABLE_WORDS = frozenset("""
    doable manageable easy enough not too bad simpler easier than i thought think work works
    should worth a go try can could do that thats this its it is sounds sound seems seem looks
    possible a be
""".split())


DOABLE_BREATHERS = frozenset("""
    ok okay alright right yeah yes yep oh ah well hmm so and but then honestly really probably
    definitely be thanks thank you ta cheers please mate
""".split())


# Never a judgement of something else: a body, a bill, a person. "the pain is manageable" is not
# the person accepting the advice, whatever else the line says.
DOABLE_NOT = re.compile(
    r"\b(?:pain|ache|hurts?|hurting|bleeding|temperature|bill|bills|debt|rent|money|pay|price|"
    r"cost|boss|mum|dad|husband|wife|partner|son|daughter|kid|kids|child|baby)\b", re.I)


DOABLE_REPLIES = (
    "Good \u2014 the first bit is the whole trick, so do that properly and see how you get on.",
    "That's the way. Shout if a step of it does not make sense once you are in it.",
    "Right. Start with the first part and tell me how it goes.",
)


# The follow-up fold in front of the line: "sounds doable" reaches the composer as "what about
# sounds doable", because the understanding engine reads a short line after an answer as the thing
# they are asking about next. The fold is not part of what the person said, so it comes off before
# the judgement is read, or every judgement would be read as a thing with a name.
DOABLE_FOLD = re.compile(r"^(?:what\s+about|how\s+about|and|also|what\s+of|then)\s+", re.I)


def _reads_as_a_judgement(text):
    """True when the line is nothing but a judgement that what was said is doable.

    No memory is looked at, so the question can be asked by a part of the bot that has no advice
    to hand (the swap reading in `bot/modules/answers.py` asks it): the answer is only whether the
    words of the line make a judgement of the line above, and `_a_doable` is what adds whether
    there was anything to judge.
    """
    clean = " ".join(str(text or "").lower().split())
    while DOABLE_FOLD.match(clean):
        clean = DOABLE_FOLD.sub("", clean, count=1).strip()
    if not clean or "?" in clean:
        return False
    words = clean.split()
    if len(words) > 8:
        return False
    if not DOABLE.search(clean) or DOABLE_NOT.search(clean):
        return False
    said = [word.strip(".,!?;:'\u2019") for word in words]
    # Something of their own is in the line, so it is a judgement of that and not of the answer:
    # "the whole shed is doable in a day".
    return all(word in DOABLE_WORDS | DOABLE_BREATHERS for word in said)


def reads_as_a_judgement(text):
    """Read by bot/modules/answers.py: is this line a judgement rather than a thing?

    The swap reading hands the answer to a thing the person named ("what about the bathroom" ->
    "The same goes for the bathroom: ..."). A judgement of the answer names no thing, and reading
    one as a thing says the judgement back as if it were one: "sounds doable" came back "The same
    goes for the sounds doable: ...". Nothing is written here, so asking costs a turn nothing.
    """
    return _reads_as_a_judgement(text)


# A person who tells the bot their next step ("ok ill book her in tomorrow", "ill try that
# tonight") is not asking for anything: they want it acknowledged. A flat "Got it" misses that,
# and the sad pool would be wrong, because a plan is not bad news.
PLAN = (
    "Good — that sounds like the right next step. Tell me how you get on.",
    "Nice one. Let me know how it goes.",
    "That sounds sensible. Shout if it does not go to plan.",
)


# A next step that changes a medicine is not a next step to bless: the pool above reads every
# "i'm going to ..." as a decision somebody has taken, and a prescription is the one kind of
# decision that waits for the person who wrote it. "im going to skip my medication for a week"
# came back "That sounds sensible. Shout if it does not go to plan.", and "im going to cut down
# my insulin" the same.
#
# The rule is about the change, not about the medicine, so it is written as two shapes and a
# window between them rather than as a list of sentences:
#
#   a verb of changing what is taken  ...  a word for what is taken
#   a word for what is taken          ...  a change in how much is taken ("an extra dose",
#                                          "two instead of one")
#
# The verb list is the ordinary English for it - stop, quit, give up, leave off, come off, cut,
# reduce, halve, double, increase, raise, lower, skip, miss, drop, ditch, bin, knock off, wean,
# taper, flush, switch, swap, change - because every one of them came up in a real line and each
# was blessed before. What keeps them safe is the second half: "cut the grass", "cut down on
# sugar", "drop the kids at school", "give up the booze", "take two weeks off work" and "change my
# mind" name nothing that is taken, so they keep their own answers. The negative lookahead keeps
# a walk past the chemist out of it: "stop at the chemist for my tablets" is a place to go, not a
# dose.
_MEDICINE_WORD = (
    r"\b(?:medication|medications|meds|medicine|medicines|tablet|tablets|pill|pills|"
    r"dose|doses|dosage|insulin|insulin injections|inhaler|inhalers|steroids|antibiotics|"
    r"antidepressants|anticoagulants|blood\s+thinners?|blood\s+pressure\s+tablets|epipen|"
    r"epipens|statins?|beta\s+blockers?|thyroxine|levothyroxine|metformin|warfarin|"
    r"prednisolone|painkillers|sleeping\s+tablets|epilepsy\s+tablets|hormones?|"
    r"prescription|prescriptions|treatment)\b")


# What a clinic does to you is not a medicine either: "my gym sessions", "three sessions with the
# physio", "my counselling sessions", "my therapy approach" are all plans, and a word for a
# session beside a verb of stopping or changing read as a dose. Nothing the caution is for is
# said as a session, so the word is out and a line that names one keeps its own answer.
# The verbs that can be followed by a place ("stop at the chemist", "drop in on mum", "cut
# through the park") get a lookahead, because a place is where the person is going, not what they
# take. The rest cannot take one, so "taper off my steroids" and "come off my antidepressants"
# are read with no lookahead in the way.
_VERB_AT_A_PLACE = (
    r"\b(?:stop|stopping|drop|dropping|cut|cutting|pop|popping|skip|skipping|miss|missing)\b"
    r"(?!\s+(?:at|by|in|on|off|for|to|past|outside)\b)")


# The change itself, said as a verb.
_CHANGE_VERB = (
    r"\b(?:quit|quitting|give\s+up|giving\s+up|leave\s+off|leaving\s+off|come\s+off|"
    r"coming\s+off|go\s+off|going\s+off|reduce|reducing|halve|halving|half|halfing|double|"
    r"doubling|increase|increasing|raise|raising|lower|lowering|ditch|ditching|bin|binning|"
    r"knock\s+off|knocking\s+off|wean|weaning|taper|tapering|flush|flushing|switch|switching|"
    r"swap|swapping|change|changing)\b")


# Splitting a tablet is the one change to a medicine with its own answer, and it is a better one:
# `science.cut-or-crush-a-tablet` says to check whether it is a modified-release tablet before
# anything is cut, and "i want to cut my pills in half to make them last" was that card on main
# and the pharmacist line here. A split is about the tablet in the person's hand, not about the
# prescription, so the caution stands down for it and the card answers.
_SPLITTING_A_TABLET = re.compile(
    r"\b(?:cut|cutting|split|splitting|break|breaking|halve|halving|half)\b[^.?!]{0,20}"
    r"\b(?:tablets?|pills?|capsules?)\b[^.?!]{0,14}\b(?:in\s+half|in\s+two|in\s+quarters?|"
    r"down\s+the\s+middle)\b"
    r"|\b(?:tablets?|pills?|capsules?)\b[^.?!]{0,14}\b(?:in\s+half|in\s+two|in\s+quarters?)\b",
    re.I)


# The change said as an amount: "an extra one", "two instead of one", "three tonight".
_AMOUNT = (
    r"\b(?:take|taking|have|having|pop|popping|swallow|swallowing)\s+(?:an?\s+)?"
    r"(?:extra|two|three|four|double|twice|\d+)\b")


PLAN_MEDICINE = re.compile(
    r"(?:" + _VERB_AT_A_PLACE + r"|" + _CHANGE_VERB + r")[^.?!]{0,40}" + _MEDICINE_WORD
    + r"|" + _MEDICINE_WORD + r"[^.?!]{0,30}" + _AMOUNT
    + r"|" + _AMOUNT + r"[^.?!]{0,40}" + _MEDICINE_WORD,
    re.I)


# The medicine that causes real trouble stopped suddenly is named, because that is what makes the
# wait worth it. The ones that are usually reduced in steps over weeks are their own list, so a
# line that names none of them is not read the longest sentence in the pool.
PLAN_MEDICINE_SLOW = re.compile(
    r"\b(?:antidepressants?|steroids?|prednisolone|insulin|blood\s+pressure|blood\s+thinners?|"
    r"anticoagulants?|warfarin|epilep\w*|beta\s+blockers?|statins?|thyroxine|levothyroxine)\b",
    re.I)


PLAN_MEDICINE_REPLY = (
    "Do not change a prescribed dose on your own, even for a week: a pharmacist can tell you "
    "today, free, whether to skip it, take less, take more or come off it, and how slowly to go. "
    "If you have stopped it already and feel unwell, ring 111.",
    "Ask a pharmacist before you change a dose, skip it or come off it, even for a week: they "
    "know whether it is safe and how slowly to do it. If you have stopped it already and feel "
    "unwell, ring 111.",
)


PLAN_MEDICINE_SLOW_REPLY = (
    "Do not change a prescribed dose on your own, even for a week: a pharmacist can tell you "
    "today, free, whether to skip it, take less, take more or come off it, and how slowly to go. "
    "Antidepressants, steroids, insulin, blood pressure tablets and blood thinners are the ones "
    "that cause real trouble stopped suddenly. If you have stopped it already and feel unwell, "
    "ring 111.",
    "Ask a pharmacist before you change a dose, skip it or come off it, even for a week: they "
    "know whether it is safe and how slowly to do it, and antidepressants, steroids, insulin, "
    "blood pressure tablets and blood thinners are the ones that are usually reduced in steps "
    "over weeks. If you have stopped it already and feel unwell, ring 111.",
)


# Two things have to be true before the caution above is the right answer, and both were wrong
# when the rule was only the regex. The change has to be the person's own decision, and it has to
# be a decision rather than a question:
#
#   my gp is stopping my tablets        -> the doctor decided, so "ask a pharmacist before you
#                                          skip it" is advice about nothing
#   can i stop my medication            -> the knowledge base answers this one well ("keep taking
#                                          it until a pharmacist, nurse or GP tells you to stop"),
#                                          and a question is not a plan
#
# So the reading the pools ask is `reads_as_a_change_of_medicine`, not the regex on its own: the
# words of the rule in one place, so the three pools that cheer a plan cannot drift apart.
_A_QUALIFIED_PERSON_DOES_IT = re.compile(
    r"\b(?:my|our|the|his|her|their)?\s*\b(?:gp|doctor|dr|consultant|psychiatrist|specialist|"
    r"surgeon|nurse|pharmacist|midwife|psychologist|dietitian|anaesthetist)\b[^.?!]{0,30}"
    r"\b(?:is|are|was|were|has|have|had|keeps|kept|stopping|stopped|reducing|reduced|changing|"
    r"changed|taking|took|wants|wanted|told|said|thinks?|advised|suggested|switched|put)\b",
    re.I)


_A_QUESTION = re.compile(
    r"(?:^\s*(?:can|could|should|shall|would|will|is|are|do|does|did|am|what|how|when|where|"
    r"why|which|who)\b)|\?\s*$", re.I)


def reads_as_a_change_of_medicine(text):
    """Is this line the person's own plan to change what they take? Read by the plan pools."""
    flat = str(text or "")
    if not PLAN_MEDICINE.search(flat):
        return False
    if _SPLITTING_A_TABLET.search(flat):
        return False
    if _A_QUESTION.search(flat.strip()):
        return False
    return not _A_QUALIFIED_PERSON_DOES_IT.search(flat)


# The reply to a feeling said in the shape of a plan. Short and warm, and it asks for the story,
# because the person is telling one.
IDIOM_SHY = (
    "Ha — one of those days, then. What happened?",
    "Oh no. Go on, what happened?",
)


IDIOM_GLAD = (
    "Ha — that good? What are you waiting for?",
    "Sounds like a big one. What is it?",
)


PLAN_OPENING = re.compile(r"^(?:ok(?:ay)?|alright|right|so|well|thanks|cheers)?[\s,]*"
                          r"(?:i'?ll|ill|i will|i'?m going to|im going to|i'?m gonna|im gonna|"
                          r"gonna|going to)\s+\w+")


# The plan that has not happened yet: "i havent booked it yet" holds the words of a done thing
# and is the opposite of one.
PLAN_NOT_YET = re.compile(r"\b(?:havent|haven't|hasnt|hasn't|aint|ain't|not yet|still to|"
                          r"need to|have to|yet to)\b")


PLAN_NOT = re.compile(r"\b(?:never|not|won'?t|wont|can'?t|cant|don'?t|dont|didn'?t|didnt|"
                      r"shouldn'?t|shouldnt)\b")


# A thing the person has done with, in their own words: "i sorted it", "dealt with it", "its
# sorted now". The whole line has to be this, because "i sorted it at last" is the same report and
# "i sorted it and she still hasnt rung" is a grievance. Used in a safety thread, where the same
# words are a report on the advice (see `_after_safety`), and left to `PLAN_DONE` everywhere else.
THING_SORTED = re.compile(
    r"^(?:(?:ok|okay|alright|right|so|well|yeah|yep|yes|cool|fine|thanks|thank you|"
    r"no worries|anyway|and|but|then|all)\s+)*"
    r"(?:"
    r"(?:i|we|ive|i've|weve|we've)\s+(?:(?:have|had|got|already)\s+)?"
    r"(?:sorted|dealt with|handled|done|did|took care of)\s+"
    r"(?:it|that|this|them|things|everything)(?:\s+out)?"
    r"|(?:its|it's)\s+(?:sorted|done|handled|dealt with)(?:\s+now)?"
    r"|(?:sorted|done|handled|dealt with)\s+(?:it|that|this|them)(?:\s+out)?"
    r")"
    r"(?:\s+(?:now|thanks|thank you|already|ok|okay|alright|then))?[\s.!]*$",
    re.IGNORECASE)


# A feeling said in the shape of a plan: "im going to die of embarrassment", "i'm going to die
# laughing". PLAN_OPENING reads every "i'm going to ..." as a next step, so acking it with "Good —
# that sounds like the right next step" answers the wrong thing entirely.
PLAN_IDIOM = re.compile(
    r"\b(?:die|dying|died)\s+(?:of|from)\s+(?:embarrassment|boredom|shame|laughter|excitement|"
    r"cringe)\b"
    r"|\b(?:die|dying|died)\s+laughing\b"
    r"|\bkill(?:ing)?\s+my\s*self\s+laughing\b"
    r"|\b(?:crack(?:ing)?\s+up|wet\s+my\s*self)\b[^.?!]{0,12}\blaughing\b")


# The next step said as a decision rather than as ""i'll ..."": "i think i should ring my sister",
# "i ought to clear the garage", "i should probably call my dad". These were the nod or a receipt
# back at the person ("Noted: you should go and see your mum"), because `PLAN_OPENING` reads only
# the will-going-to shape. The should has to be the person's own next step, so the words that make
# it a verdict about how things stand - "i should be asleep" at midnight, "i should have known",
# "i should think so", "i should hope so" - are fenced off.
PLAN_DECIDED = re.compile(
    r"^(?:ok(?:ay)?|alright|right|so|well|thanks|cheers|anyway|honestly|tbh|yeah)?[\s,]*"
    r"(?:(?:i think|i reckon|i guess|i feel like|maybe|perhaps|probably)\s+)?"
    r"(?:i\s+(?:(?:really|probably|definitely|just|still|actually|honestly|so)\s+)?"
    r"(?:should|ought to|oughta|had better|better)\b|i'?d better\b|id better\b)"
    r"\s+(?!be\b|have\b|hav\b|never\b|not\b|n'?t\b|think\b|hope\b|say\b|know\b|"
    r"imagine\b|expect\b|worry\b|care\b|bother\b)"
    r"(?:probably|really|definitely|just|still|maybe|perhaps|actually|now|then)?\s*"
    r"\w+")


def _plan_reported(clean, mood):
    """True when the line is the person saying what they will do next, not a trouble."""
    if mood == "negative" or PLAN_NOT.search(clean) or PLAN_IDIOM.search(clean):
        return False
    return (bool(PLAN_OPENING.match(clean)) or bool(PLAN_DECIDED.match(clean))
            or any(phrase in clean for phrase in PLAN_DONE))


# Ending a relationship, said as a plan or as news. The person has to come straight after the
# leaving word, so "leaving him a note" and "leaving my job" are not this.
RELATIONSHIP_ENDING = re.compile(
    r"\b(?:leaving|leave|left|walking out on|walk out on|walked out on|divorce|divorcing|"
    r"dump|dumping|dumped|splitting up with|split up with|broke up with|break up with|"
    r"breaking up with|ending it with|end it with|ended it with)\s+" + A_PERSON +
    # The person has to be the end of the thought: "leaving him a note", "leaving him a
    # message" and "leaving him at nursery" are about a note, a message and a nursery.
    r"(?=\s*(?:[.!?,;]|$|(?:\s+(?:for good|behind|tomorrow|tonight|next week|this week|finally|now|today))\s*(?:[.!?,;]|$)))")


# A line that holds the person's own life up against a crowd's: "everyone my age owns a house",
# "all my mates are sorted", "most people my age are married", "people my age all seem to have
# bought a flat". Every one of them is a feeling about where they stand, and none of them is good
# news: the cheer ("Brilliant. Really pleased for you.") is for a win somebody had, and the nod
# ("Got it. Is there anything you'd like a hand with?") is for a fact nobody minds about, so a
# person saying they feel behind got a stock line, and the store asked them how old the crowd was
# ("everyone my age owns a house" -> "You haven't told me how old they are.").
#
# The reading is two halves, and it needs both: a crowd, and a marker of the standing the line is
# about. A crowd on its own is a report ("everyone at work is off sick") and a marker on its own
# is the person's own life ("i still rent"), and neither is a comparison.
A_CROWD_SUBJECT = re.compile(
    r"\b(?:everyone|everybody|most people|people|folk|others|no ?one|nobody"
    r"|all (?:of )?my (?:friends|mates|siblings|cousins)|my (?:friends|mates)"
    r"|the people (?:i know|around me|at work|on my course))\b", re.I)


# What the crowd has and the person is measuring themselves against. Keep it to the things people
# actually keep score with; a verb that is about anything else ("everyone loved the cake") is not
# a comparison and must not be read as one.
A_MARKER_OF_STANDING = re.compile(
    r"\b(?:owns?|owned|owning|bought|buying|has? bought|have bought"
    r"|married|engaged|settled|sorted|got it sorted|have it sorted|has it sorted|promoted"
    r"|mortgage|kids|children|babies|pregnan\w*|ahead|better than me|more than me"
    r"|further along|further ahead|doing better"
    # The status as a thing held rather than a verb of getting it: "everyone else has a house",
    # "all my mates have got a flat". The article is what keeps a house somebody lives in ("the
    # people in the house are asleep") out of it.
    r"|(?:has|have|got|with)\s+(?:a\s+|an\s+|their own\s+|his own\s+|her own\s+)?"
    r"(?:house|flat|place|mortgage|baby|kids|children|career|job|salary|pension)\b)\b", re.I)


# A crowd that still has a parent is not the standing a person is measuring their life by: it is
# a loss in the middle of a chat, and the condolence or the gentle pool is the answer to it.
A_PARENT_STILL_THERE = re.compile(
    r"\b(?:mum|mam|mom|dad|mother|father|parents|gran|nan)\b", re.I)


# The person's own age named as the measure rather than asked for: "everyone my age", "people my
# age", "at my age". The store reads the word as an ask for the number and answers that they never
# gave it, which is the one reply that makes no sense to somebody saying everybody else is ahead.
MY_OWN_AGE = re.compile(r"\b(?:my|our) (?:own )?age\b", re.I)


# The person's own win is the whole line ("i bought a house", "we got the keys"), and a crowd in it
# is who they are telling. A comparison never has the person as its subject.
THE_PERSON_IS_THE_SUBJECT = re.compile(r"^\s*(?:i|ive|im|we|weve|were|me)\b", re.I)


# The comparison with an ask of its own on top ("everyone my age is having babies, what do i do")
# is a line for whatever answers the ask: naming the comparison back at them is not the answer to
# a question, so the reading stands down and lets the ask have the turn.
AN_ASK_ON_TOP = re.compile(
    r"\b(?:what (?:do|should|can) i do|what would you do|should i|how do i|help me|any advice"
    r"|what now|where do i start|advice)\b", re.I)


def a_comparison_of_standing(clean):
    """True when the line measures the person's life against a crowd's - the feeling of being behind.

    Published as a reading, not a pool: what follows a line like this is the same wherever it is
    met (bot/modules/memory_store.py asks it, so the age question stands down), and one name for
    the shape is what keeps the two agreeing.
    """
    line = " ".join(str(clean or "").split())
    if not line or "?" in line:
        return False
    if len(line.split()) > 14:
        return False  # a story that happens to start with a crowd is a story
    if A_PARENT_STILL_THERE.search(line) and re.search(r"\bstill\b", line, re.I):
        return False
    # A line that opens on the person and then turns to the crowd is still a comparison: "im 41
    # and everyone my age seems busy with kids" is the same feeling as "everyone my age seems busy
    # with kids". The person has to be the subject of the whole line for it to be their own news.
    comparison = line
    if THE_PERSON_IS_THE_SUBJECT.match(line):
        turned = re.split(r"(?:,|\band\b|\bbut\b)", line, maxsplit=1)
        if len(turned) < 2:
            return False
        comparison = turned[1]
        if not A_CROWD_SUBJECT.search(comparison):
            return False
    if not A_CROWD_SUBJECT.search(comparison):
        # "at my age youd think id have it sorted" names no crowd and is the same measuring all
        # the same: the age is what they are holding themselves against.
        return bool(re.search(r"\bat (?:my|our) age\b", comparison, re.I))
    if AN_ASK_ON_TOP.search(line):
        return False
    if MY_OWN_AGE.search(comparison):
        # "everyone my age ...", "at my age youd think id have it sorted": an age used as the
        # measure is the comparison itself, whatever the crowd went on to have.
        return True
    return bool(A_MARKER_OF_STANDING.search(comparison))


# What a friend says to the feeling of being behind: it is not condoled (nothing happened), not
# cheered (the crowd is not the person's win) and not filed. The comparison is named, and the
# question turns the line from the list they are on to the thing they want.
A_COMPARISON_OF_STANDING = (
    "That kind of comparison always picks the one thing you haven't got. Is it something you "
    "actually want, or is it the being behind that stings?",
    "Other people's lives look tidier from the outside than they are from the inside. What would "
    "you want to be different?",
    "It is easy to feel like the only one not there yet, and most people are a lot less sorted "
    "than they look. What would actually help you right now?",
    "That is a fair thing to feel, and the measuring is doing a lot of the work. What do you want "
    "out of it, apart from the comparison going away?",
    "There is no deadline on any of that, whatever the timeline looks like from where you are "
    "standing. What is the one piece you would want to get to?",
)


def _a_relationship_ending(clean):
    """True when the line is about leaving a person, which is neither a win nor a plan."""
    return bool(RELATIONSHIP_ENDING.search(clean))


# What our own line says when it answered a hard one: the openings of the sad, low and missing
# pools. Read by the composer because the nod has nothing in it of its own, and the thread it
# belongs to is the one the bot is already in.
OUR_HEAVY_TELL = re.compile(
    r"(?:sorry to hear|i'm so sorry|i'm really sorry|that sounds rough|that's a heavy feeling"
    r"|that's a lot to|that sounds exhausting|loneliness is rough|missing someone is the price"
    r"|it's a hard thing to carry|be kind to yourself|i'm glad you said it|you don't have to carry"
    r"|there's no rush to talk about it)")


# What those words look like in a line, with a boundary so "fired" and "gasp" are not them.
HAZARD_LINE = re.compile(r"\b(?:fires?|smoke|flames?|gas|fumes?|carbon monoxide|flue|"
                         r"fire brigade|fire service)\b")


# The same easing after a first-aid answer: nobody is bleeding any more, so the care pools (an
# eye on something that is still going on, or a trip to a&e) would not fit.
# Feeling better is not the same as being out of danger. With an overdose, a poisoning or a
# cardiac arrest a person can feel fine for hours while the harm is still going on, so the easing
# keeps the emergency line rather than sending them back to their day: chief-umbrella's three
# shapes ("i took an overdose" / "i feel a bit better now" was *"keep an eye on it today"*).
NO_RELIEF = re.compile(
    r"\b(?:overdos\w*|poison\w*|swallow\w*|paracetamol|ibuprofen|bleach|antifreeze|"
    r"carbon monoxide|pills|tablets|capsules|stopped breathing|not breathing|isnt breathing|"
    r"no pulse|cpr|cardiac|arrest|unconscious|unresponsive|collaps\w*|hanging|hung|"
    r"electrocut\w*|electric shock)\b")


# Who the person in danger is. A good share of the crisis lines in the deck are about somebody
# else - "my sister took an overdose last year", "my dad overdosed in march" - and the safety
# answer gets those right by speaking about "them". The continuation did not: the pools above
# are written for the person typing ("keep someone with you tonight", "stay with the person you
# told"), so "now shes talking about it again" got "Keep someone with you tonight, and ring back
# if it gets heavier - they'd rather hear from you". That is advice for a body that is not the
# one at risk, and it tells the carer to ring about themselves in the worst hour of their week.
#
# So each continuation asks one question first: is the person in this thread somebody else? It is
# read from the line that started the thread - the safety turn's own user line - so the relation
# and the gender are the person's own words ("your sister", "your dad"), and a "she" in the
# follow-up never has to be guessed. A line that names both - "i told my mum i want to die" - is
# answered as the speaker's own, because that is the mistake that has to stay safe.
SHE = frozenset((
    "sister", "mum", "mummy", "mother", "mam", "nan", "nanna", "gran", "granny",
    "grandma", "daughter", "wife", "girlfriend", "aunt", "auntie", "niece", "stepmum",
    "stepdaughter", "stepsister",
))


HE = frozenset((
    "dad", "daddy", "father", "son", "husband", "boyfriend", "brother", "nephew",
    "uncle", "grandad", "grandpa", "granddad", "stepdad", "stepson", "stepbrother",
))


# "my sister", "our eldest daughter", "my best mate". The relation is what the reply uses, and
# for the people a person looks after without a gender ("my friend", "my partner") the plural
# words below carry it, so nothing is assumed.
A_PERSON_OF_THEIRS = re.compile(
    r"\b(?:my|our)\s+(?:poor\s+|little\s+|eldest\s+|youngest\s+|old\s+|older\s+|elderly\s+|"
    r"grown\s*up\s+|best\s+|close\s+|work\s+|foster\s+|step\s*)*(?P<who>"
    r"sister|mum|mummy|mother|mam|nan|nanna|gran|granny|grandma|daughter|wife|girlfriend|"
    r"aunt|auntie|niece|dad|daddy|father|son|husband|boyfriend|brother|nephew|uncle|"
    r"grandad|grandpa|granddad|stepmum|stepdad|stepson|stepdaughter|partner|other\s+half|"
    r"friend|mate|flatmate|housemate|roommate|cousin|neighbour|colleague|child|kid|baby)\b",
    re.I)


# The speaker in danger: then it is their own crisis whatever else the line names. "me" is not
# here on purpose - "my friend told me she wants to die" would read as the speaker's own.
SELF_IN_DANGER = re.compile(
    r"\b(?:(?:i|ive|im|id)\b[^.?!]{0,24}?\b(?:took|swallow|overdos|od'd|cut|hurt|harm|"
    r"kill|suicid|die|dying|dead|end\s+it|hang|hung|jump|pills|tablets|starving|starve)|"
    r"myself\b|\bmy\s+own\s+(?:life|body|head))", re.I)


# Somebody hurt the speaker: "my husband hit me". The relation named in that line is the person
# who did it, not a person in danger, so the carer's pools (which ask the person to look after
# "your husband" tonight) have no business in this thread - the speaker is the one who needs
# looking after. Same rule as SELF_IN_DANGER, read from the other end of the sentence.
SOMEBODY_HURT_ME = re.compile(
    r"\b(?:hit|hits|hitting|beat|beats|beating|punch(?:ed|es|ing)?|kick(?:ed|s|ing)?|"
    r"slap(?:ped|s|ping)?|push(?:ed|es|ing)?|shov(?:ed|es|ing)|grab(?:bed|s|bing)?|"
    r"drag(?:ged|s|ging)?|strangl(?:ed|es|ing)|chok(?:ed|es|ing)|threaten(?:ed|s|ing)?|"
    r"abus(?:e|es|ed|ing)|assault(?:ed|s|ing)?|rap(?:e|ed|es|ing)|grope[sd]?|"
    r"burn(?:ed|t|s)|scald(?:ed|s|ing)|hurt|hurts|hurting|harm(?:ed|s)|attacked|"
    r"lock(?:ed|s)\s+(?:me|us)\s+(?:in|out))\s+(?:me|us)\b", re.I)


# A pronoun that carries somebody other than the speaker ("shes talking about it"), which is the
# one thing that sends the reading above back through the chat for the person it means.
A_PRONOUN_FOR_SOMEBODY = re.compile(
    r"\b(?:he|she|they|him|her|his|their|hes|shes|theyd|theyll|theyre|they've)\b", re.I)


# The advice was a page of it, and this line is the report on it. "i tried that and it helped a
# bit" told the bot which part worked and got a stock line that would fit any message ("Got it.
# Is there anything you'd like a hand with?"); "ive been doing it for a week now" got their own
# sentence back. A friend answers the outcome, not the report, so there are four of them: it
# worked, it has not moved yet, it made things worse, and "I am doing it" with no verdict.
# Only a line that is nothing but the report is read this way - "i tried that new cafe" is a
# place, not a report on the last answer - and only right after an answer that gave the person
# something to do, so it can never take a turn from a subject of the person's own.
ADVICE_LENGTH = 180


# The same question for a line that is nothing but the report ("it doesnt work", "none of that
# worked"): the answer behind it only has to be long enough to have been advice at all.
ADVICE_LENGTH_BARE = 120


# A warm care line is advice too, and a short one is a whole answer: "go easy on yourself today,
# and see someone if it's not shifting in a few days" is something to do and to report back on,
# and at a hundred characters it never got past the length gate - so "no change" after it was
# answered as a remark about anything at all ("Right - anything else on your mind?"). Length is
# still one way to say "this was advice"; the other is a cue that names something to do. A line
# that only makes conversation ("Hi! What's on your mind?", "You're welcome - shout if anything
# else comes up") has none of these, so a report after one is still a remark.
ADVICE_CUE = re.compile(
    r"\b(?:go easy|take it easy|take it steady|rest|see someone|see (?:your|a) (?:gp|doctor)|"
    r"get it looked at|looked at|worth (?:a|an|seeing|asking|ringing|going|getting|trying)|"
    r"say so to (?:a|your) (?:gp|doctor)|talk to (?:a|your) (?:gp|doctor)|"
    r"tell (?:a|your) (?:gp|doctor|pharmacist)|ask (?:a|your) (?:gp|doctor|pharmacist)|"
    r"ring (?:your|the|us|back|111|999|nhs)|phone (?:your|the|111|999)|make an appointment|"
    r"book (?:an?|your|it)|carry on|keep (?:going|doing|it|walking|an eye|taking|using)|"
    r"try (?:a|an|the|it|this|that|putting|going|starting|taking|walking|keeping)|"
    r"start with|stop (?:it|there|and|doing)|"
    r"leave it (?:off|alone|a)|check (?:the|it|your|whether|that)|top (?:it|the) up|"
    r"apply|cover it|elevate|keep it|write (?:it|down|a|the)|make a note|note down|"
    r"ask (?:for|about|your|the|whether|what)|change one thing)\b")
