"""Part 14 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import history, reject, repeat
from . import (badnews, loss,
               trouble)
from .badnews import (reads_as_bad_news,
                      reads_like_a_symptom)

from .fallback_data import (
    ABOUT_THEM_BEFORE_COPULA,
    ADVICE_LENGTH,
    ADVICE_LENGTH_BARE,
    ADVICE_TURNS,
    AIM_FAILING,
    AIM_NEGATORS,
    A_HOW_THE_TIME_WENT,
    A_PAUSE_WORD,
    COPULA,
    ILL_AFTER,
    ILL_BEFORE,
    ILL_SAID_OF_A_BODY,
    ILL_WILL_VERBS,
    MANNERS_ONLY,
    MOOD_AFTER,
    MOOD_BEFORE,
    PREGNANCY_BLEEDING,
    QUESTION_OPENERS,
    REPORT_FILLER,
    STRETCH_OF_TIME,
    SUDDEN_LOSS,
    THANKS_ONLY,
    THANKS_WORDS,
    THANK_WORDS,
    THE_FIRST_HOUR_AND_A_CHILD,
    TREATMENT_HARM,
    TRIED_HELPED_ELSEWHERE,
    TRIED_HELPED_REPLIES,
    TRIED_IT_REPLIES,
    TRIED_NO_CHANGE_ELSEWHERE,
    TRIED_SORTED_REPLIES,
    TRIED_NO_CHANGE_REPLIES,
    TRIED_WORSE_ELSEWHERE,
    TRIED_WORSE_REPLIES,
    _SUBJECT_AFTER_AM,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    ABSENCE,
)
from .fallback_part_01 import (
    _worry_is_about_the_body,
)
from .fallback_part_03 import (
    HEAVY_ABOVE,
)
from .fallback_part_04 import (
    _hesitant_news_before,
)
from .fallback_part_05 import (
    _the_last_few_lines, baby_loss, a_heavy_news, a_heavy_verdict, _SORRY_LEAD,
)
from .fallback_part_06 import (
    ADVICE_CUE, ADVICE_LENGTH, ADVICE_LENGTH_BARE,
)
from .fallback_part_07 import (
    DONE_IT, NO_STEP, REPORT_NOW_FINE, REPORT_VERDICT_WORD, STILL_THE_TROUBLE, TRIED_HELPED,
    TRIED_IT, TRIED_NO_CHANGE, TRIED_THAT_ONLY, TRIED_THE_LOT, TRIED_WORSE, _advice_in,
    _the_words_in, AN_ANSWER_ABOUT_A_NO,
)
from .fallback_part_08 import (
    _in_a_care_thread,
)
from .fallback_part_13 import (
    _grief_thread, A_GAP_FOR_ILLNESS, A_GAP_NAMED_PERSON, A_TURN_THE_PAGE, GOT_DRAWN_AWAY,
    STEPPED_AWAY,
)


def _a_hard_week(memory):
    """True when a death or bad news of their own is in the chat in the last few turns.

    One reader for the two places that ask, because the order matters: a plan dropped in that
    week is answered gently (`DECLINED_PLAN_GENTLE`) and stays this module's line, and a plan
    dropped beside a feeling is left to the reader that answered the feeling.
    """
    return bool(_in_a_loss_thread(memory) or _a_loss_recently(memory) or _hesitant_news_before(memory))


def _a_care_thread_to_leave_alone(memory):
    """True when the bot's last answer was care, so a reaction is not news it has not heard.

    A reaction is answered by asking what happened, which is right for "oh no the boiler again" /
    "yikes" and wrong inside a bereavement: "i had a miscarriage" / "ouch" was answered with
    "Yikes. That sounds rough - what happened?" over a care reply that had just asked who is
    around them this week. The reading is the one the grief and loss pools use, so a reaction
    after a death, a loss or a crisis stays with the person instead of starting again.
    """
    if _in_a_care_thread(memory) or _in_sudden_loss_thread(memory) or _in_a_loss_thread(memory):
        return True
    return any(baby_loss(said) for said in _the_last_few_lines(memory))


def a_loss_in_the_thread(memory=None):
    """True when the news the verdict lands on is a death, a diagnosis or a baby lost.

    Only those are answered with `VERDICT_HEAVY`. The accident reading (`HARD_WEEK`) used to be in
    here too, which put a washing machine in a bereavement line: a bare "broken" matched it, so
    "my washing machine is broken" then "what a pain" got "That sounds like it has been sitting
    with you a while" (crisp-jackal on #5479). An accident's news is light enough for the light
    pools or for the answer the person already has, and `a_verdict_stands_down` still keeps a
    verdict out of a thread that is not light.
    """
    if a_heavy_verdict(memory) or a_heavy_news(memory):
        return True
    try:
        if _in_a_loss_thread(memory) or _grief_thread(memory):
            return True
    except Exception:  # noqa: BLE001 - a thread that cannot be read claims nothing
        return False
    for turn in [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)][-2:]:
        line = " ".join(str(turn.get("user") or "").lower().split())
        if not line:
            continue
        if HEAVY_ABOVE.search(line):
            return True
        try:
            if badnews.reads_as_sudden_loss(line):
                return True
        except Exception:  # noqa: BLE001 - a reading that cannot run claims nothing
            continue
    return False


def _the_gap_is_all_there_is(clean):
    """True when nothing is left of the line once the apology for the gap is taken off.

    The apology used to take the whole line even when the person had gone on to say why they
    were writing ("sorry i went to get the kids, anyway the boiler is leaking"), and the answer
    to the boiler was dropped for "No need to say sorry - I'm still here". The apology is only
    the line while every word outside it is a small word - or a word about how the stretch of
    time away went ("sorry ive been quiet, work has been mad"), which names no subject the bot
    can answer: it is the reason for the gap.
    """
    text = " ".join(str(clean or "").lower().replace("\u2019", "'").split())
    if not text:
        return False
    # The errand is the one shape that names its object partly ("sorry i went to get the kids"
    # leaves "the kids"), so it may leave one word of the line's own behind. Everything else
    # may leave none: "sorry i fell asleep at the wheel" and "sorry, i lost track of my
    # medication" name something, and that something is the line.
    errand = bool(STEPPED_AWAY.search(text))
    spare = 1 if errand else 0
    for pattern in (STEPPED_AWAY, ABSENCE, GOT_DRAWN_AWAY, _SORRY_LEAD):
        for _ in range(4):
            match = pattern.search(text)
            if not match or not match.group(0):
                break
            text = (text[:match.start()] + " " + text[match.end():]).strip()
    # A word that turns the page starts the next subject, whatever follows it: "sorry i went
    # to get the kids, anyway the boiler is leaking" is the boiler. Only when something follows
    # it - "sorry, but i got distracted" leaves the "but" behind and is still the gap.
    for match in A_TURN_THE_PAGE.finditer(text):
        if re.search(r"[a-z']", text[match.end():]):
            return False
    left = [word for word in re.findall(r"[a-z']+", text) if word not in A_PAUSE_WORD]
    rest = left[spare:]
    if not rest:
        return True
    if not any(word in A_HOW_THE_TIME_WENT or word in A_GAP_FOR_ILLNESS for word in rest):
        return False
    return len(left) <= spare + 6 and all(
        word in A_HOW_THE_TIME_WENT or word in A_GAP_FOR_ILLNESS
        or word in A_GAP_NAMED_PERSON
        for word in rest)


# The speaker's own absence, with no apology needed: "ive been quiet", "i was away". The absence
# counts only when the line names no subject of its own, which _the_gap_is_all_there_is decides.
SPEAKER_ABSENCE = re.compile(
    r"\b(?:i|ive|i've|im)\b[^.?!]{0,24}?\b(?:been|be|went|gone|was)\s+"
    r"(?:quiet|silent|away|incommunicado|off\s+my\s+phone)\b")


# The apology with no lead at all, because it came after the reason for it ("work has been mad
# so sorry for the silence"). The same words as _SORRY_LEAD without the anchor: this one is not
# the shape of the line, it is a word in it.
AN_APOLOGY_IN_THE_LINE = re.compile(r"\b(?:sorry|apolog(?:y|ies)|apologise|apologize)\b")


def reads_as_pause(clean):
    """True when the line is an apology for the conversation having paused.

    Three shapes say it: what they stepped away for ("sorry, i went to get the kids"), the
    absence itself ("sorry i went quiet", "sorry for the silence", "sorry i havent replied",
    "sorry, been busy", "sorry, my phone died"), and being drawn away ("i got distracted").
    The absence counts only behind an apology, so "my dad has gone quiet since the funeral" is
    still somebody else's line.

    Every one of them counts only while the apology is the whole line: a line that goes on to
    name something ("sorry i got distracted, the boiler is leaking") is that thing's, and the
    pause reply would take the turn from the answer to it.

    The apology does not have to come first. "work has been mad so sorry for the silence" and
    "ive been quiet because work has been mad" are the same line with the reason in front, and
    the chat module's annoyance pool took them on the word "mad" alone and told the person to
    walk it off before replying to anyone. Where the apology and the absence are both in the
    line and nothing else of its own is left, the order does not change what the line is.
    """
    text = " ".join(str(clean or "").lower().replace("\u2019", "'").split())
    if STEPPED_AWAY.search(text) or GOT_DRAWN_AWAY.search(text):
        return _the_gap_is_all_there_is(text)
    if AN_APOLOGY_IN_THE_LINE.search(text) and ABSENCE.search(text):
        return _the_gap_is_all_there_is(text)
    if SPEAKER_ABSENCE.search(text):
        return _the_gap_is_all_there_is(text)
    return False


def _came_back(clean):
    """True when the line is an apology for having stepped away for a moment."""
    return reads_as_pause(clean)


# A line that only points back at the conversation: the person picking the thread back up.
# "as i was saying", "where was i", "so anyway", "sorry, i got cut off". None of them names
# anything of its own, and nothing else reads them: the account-of-the-day pool answered them as
# though they were news ("as i was saying" -> "Sounds alright. Anything good in it?", "sorry, i
# got cut off" -> "Good to hear. What was the best bit?") and the search shrug took "where was i".
POINTS_BACK = re.compile(
    r"(?:as|like)\s+i\s+(?:was|were)\s+saying"
    r"|back\s+to\s+what\s+i\s+was\s+saying"
    r"|as\s+i\s+said"
    r"|where\s+(?:was|were)\s+(?:i|we)"
    r"|(?:got|get|getting)\s+cut\s+off|cut\s+off\s+there"
    r"|(?:i\s+)?got\s+interrupted|was\s+interrupted"
    r"|carry\s+on"
    r"|back\s+again"
    r"|any\s?way|any\s?road")


# The words that carry no subject, so a line made of these and a phrase pointing back is still
# only a line about the conversation: "right, so as i was saying" and "sorry, i got cut off".
A_POINTING_FILLER = frozenset("""
again ah already and any anyway anyroad as at back before but carry earlier er for from haha here
hmm i i'm im in in it just like me my now of off oh ok okay on right said saying so sorry that the
then there this to um up us was we well were with yeah yes you
""".split())


# What a return names the thing it is about with: "as i was saying about the car" has not said the
# thing yet, so the reply asks about it. Only these two, because a leftover after any other word is
# the rest of a sentence, not a thing.
A_THING_MARKER = frozenset("about regarding".split())


def _a_chat_behind_it(memory):
    """True when the person has already said something, so there is a thread to point back at.

    A line that points back is the whole content of the line, so it is a turn about the chat
    itself. On the first line of a chat there is no chat: the composer's own answer to "as i
    said" is "There's nothing earlier for me to go back to: this is your first line", and a
    go-ahead there would be a reply to a turn that never happened. The question is answered in
    one place, `bot/memory/history.py::an_earlier_turn`, and the arbiter asks it of every module's
    reply as well - this is the composer's own use of the same check.
    """
    return history.an_earlier_turn(memory)


def nothing_said_yet(memory):
    """True on a chat's first line; the check itself is `bot/memory/history.py::an_earlier_turn`."""
    return not history.an_earlier_turn(memory)


def brings_nothing_of_its_own(text):
    """True when the line has no subject of its own, only a point back at the conversation.

    "go on", "carry on", "same as before", "as i was saying", "you told me earlier", "nothing new
    to add then", "sorry, i got cut off", "where were we": every word is a fragment of pointing
    back (`bot/memory/history.py::NO_CONTENT_WORDS`), and there is nothing in the line for a reply
    to be about. A line with any other word in it brings something of its own - "the same goes for
    the bathroom" names the bathroom, "weve booked a week in cornwall" names the week - and a
    first line that brings something is answered like any other line, even by a pool written for a
    conversation in progress ("Nice one. Is it soon, or have you got a while yet?").
    """
    return history.brings_nothing_of_its_own(text)


def assumes_an_earlier_turn(reply):
    """Whether the reply answers something the person has said earlier in this chat.

    The frames are one list (`bot/memory/history.py::ANSWERS_AN_EARLIER_TURN`) beside the ones
    that point back at the chat, and the reading is `history.a_past_that_is_not_there`: "sorry, i
    got cut off" as the first thing in a chat was answered "Good to hear. What was the best bit?",
    "as i was saying" by "Sounds alright. Anything good in it?", and "carry on" by "Thanks for
    telling me - I'm here if you want to dig into any of that." The composer's own first-line
    lines ("Go on - what about the car?", "Nothing to catch up on yet") are not frames that assume
    a turn: they name what the person just said, which is why this is a list of frames and not a
    smell test. A caller that has already established the line brings nothing of its own asks for
    the frames alone, which is what the empty line here means.
    """
    return history.a_past_that_is_not_there(reply, {}, "")


def reads_as_a_return(clean):
    """What is left of a line that picks the thread back up: None, "" or the thing it names.

    None means the line is not a return. "" is a return with nothing of its own left in it - "as
    i was saying", "where was i", "right, so anyway" - and the composer answers it by saying go
    on. Anything else is a return that names the thing it is about, usually after "about" ("as i
    was saying about the car"): the person has not said the thing yet, so the answer asks about
    it rather than guessing.

    It counts only while the rest of the line is small words and at most a short thing, which is
    the same gate the apology above uses: "as i said, the boiler is leaking" names the boiler,
    and that is the boiler's line, not the conversation's.
    """
    text = " ".join(str(clean or "").lower().replace("\u2019", "'").split())
    if not text or not POINTS_BACK.search(text):
        return None
    left = text
    for _ in range(3):
        match = POINTS_BACK.search(left)
        if not match or not match.group(0):
            break
        left = (left[:match.start()] + " " + left[match.end():]).strip()
    tokens = [word for word in (re.sub(r"[^a-z0-9']", "", word) for word in left.split()) if word]
    marker = next((i for i, word in enumerate(tokens) if word in A_THING_MARKER), None)
    if marker is None:
        return "" if all(word in A_POINTING_FILLER for word in tokens) else None
    if not all(word in A_POINTING_FILLER for word in tokens[:marker]):
        return None
    thing = " ".join(word for word in tokens[marker + 1:] if word).strip(" ,.-\u2026")
    if not thing or len(thing.split()) > 4:
        return None
    return thing


# The words an apology for asking is made of, and nothing else: "sorry to bother you", "sorry to
# keep asking", "apologies for the silly question". A line that goes past these names something
# of its own, and that something is what the line is about.
SORRY_ASKING = re.compile(
    r"\b(?:sorry|apolog(?:y|ies)|apologise|apologize)\b"
    r"[^.?!]{0,30}?"
    r"\b(?:bother\w*|pester\w*|nagging|ask\w*|questions?|pain|nuisance|hassle|trouble\w*|"
    r"keep\s+(?:asking|going|coming|picking|on)|one\s+more|another\s+one|essay|"
    r"ramble\w*|going\s+on|dumping|moan\w*|interrupt\w*|taking\s+up)\b")


def _only_manners(clean, allowed):
    """True when every word of the line is in the allowed set, so it names nothing of its own."""
    words = re.findall(r"[a-z']+", clean.lower())
    return bool(words) and all(word in allowed for word in words)


def _sorry_for_asking(clean):
    """True when the line is an apology for asking and nothing else."""
    text = clean.lower()
    return bool(SORRY_ASKING.search(text)) and _only_manners(text, MANNERS_ONLY)


# The same manners without the apology word in front: the person checks that they are not a
# nuisance instead of apologising for it. "am i bothering you", "am i bugging you", "am i asking
# too much", "do you mind me asking", "should i stop asking", "is this a waste of your time".
# It is one social move, so it gets the one pool the apology gets. Without this the line reached
# the search shrug - "That's beyond what I know well, sorry. Searching for it will turn up better
# sources" - which searches the web for whether the bot minds being asked.
AM_I_A_NUISANCE = re.compile(
    r"(?<![a-z])(?:am|are|is)\s+(?:i|we|this|it)(?![a-z])[^.?!]{0,25}?"
    r"(?<![a-z])(?:bother\w*|bugging|annoy\w*|irritat\w*|pester\w*|in the way|too much|"
    r"a waste of|taking (?:up )?(?:too much|your)|keeping you|too many questions|"
    r"asking a lot)(?![a-z])"
    r"|(?<![a-z])(?:do|would|will|did)\s+you\s+mind(?![a-z])[^.?!]{0,25}?"
    r"(?<![a-z])(?:me asking|my asking|if i ask|i ask)(?![a-z])"
    r"|(?<![a-z])(?:should|shall|do) i (?:stop|quit) asking(?![a-z])")


# Every word such a line can be made of without naming anything of its own. "am i bothering you
# about the boiler" is the boiler's line, and this set is what keeps it out.
NUISANCE_ONLY = MANNERS_ONLY | frozenset("""
    am are is was were bugging bug annoy annoying annoyed irritating irritated irritate
    pester pestering way waste mind minding stop quit should shall if ask asking
    taking take up long much many too lot lots questions question time in way at all
    """.split())


def _am_i_a_nuisance(clean):
    """True when the line only checks whether the person is being a nuisance."""
    text = " ".join(str(clean or "").lower().split())
    return bool(AM_I_A_NUISANCE.search(text)) and _only_manners(text, NUISANCE_ONLY)


# "thanks", "thank you", "cheers", "ta" - and the word people put in front of it when they mean it
# ("ok thanks, that worked", "ah thanks"). What is left after it is the outcome.
THANKS_OPENS = re.compile(
    r"^(?:(?:ok|okay|ah|oh|right|great|brilliant|nice|lovely|perfect)\b[\s,!.]*)?"
    r"(?:thanks|thank\s+you|thankyou|thank-you|cheers|ta)\b[\s,!.]*(?P<said>.*)$")


# A question after the thanks is a new ask, not an outcome: "thanks, can you do the same for the
# shed" wants an answer about the shed, and "Glad to hear it" would step over it.
# Which way the outcome went. "Thanks, it's worse today" is somebody coming back with bad news, and
# "Good. Thanks for letting me know." is the wrong answer to it; the mood reader is no help, because
# "worse", "no better", "came back" and "still" are not mood words for a whole line - they are
# words for how a thing they tried went.
THANKS_WENT_BADLY = re.compile(
    r"\b(?:worse|worst|no\s+better|not\s+better|no\s+change|still|came\s+back|back\s+again|"
    r"hurts?|hurting|sorer?|failed|nothing|didnt|didn't|doesnt|doesn't|wont|won't|"
    r"can'?t|cant|hasnt|hasn't|"
    # The thing coming back is the commonest bad news there is, and it was read as good news:
    # "thanks, the pain is back" got "Glad to hear it - and thanks for coming back to say so."
    # "came back" and "back again" were here but not the bare return, which is how most people
    # say it. A flare and a return are the same news in other words.
    r"(?:is|are|was|were|has|have|had|its|it's|im|i'm|they're|theyre)\s+back|"
    r"(?:come|comes|coming|came)\s+back|flares?|flared|flaring|\breturned|returning|"
    r"back\s+to\s+square\s+one)\b")


# But "back" on its own is good news when it says back to how it should be: "thanks, its back to
# normal now" and "thanks, its back to how it was" are exactly what this pool is for, and the
# return shape above would turn them into trouble. Same for "still", which is in the list for
# "still the same" and not for "still keeping well".
THANKS_GOOD_AGAIN = re.compile(
    r"\bback\s+to\s+(?:normal|how\s+it\s+was|where\s+it\s+was|itself|its\s+old\s+self|"
    r"being\s+normal)\b|"
    r"\bstill\s+(?:keeping\s+|doing\s+|going\s+)?(?:good|well|fine|great|ok|okay|improving|"
    r"getting\s+better|on\s+the\s+mend|strong)\b|"
    r"\bstill\s+(?:a\s+)?bit\s+(?:sore|stiff|tired)\s+but\b")


# What the bot says to bad news that came back behind a thank-you. The thanks pools above are
# all good news, and everything below them answers a line about something the person has not
# named yet, so "thanks, its still stinging" reached the neutral pool and got "Happy to help"
# and "thanks, its worse today" got the echo ("Noted: it's worse today"). None of these lines
# claims to know what is wrong; each says sorry and hands the next detail back, which is what a
# friend does and what a card needs to answer properly.
THANKS_NO_BETTER = (
    "Sorry it hasn't settled. What's it doing now?",
    "Sorry to hear that — thanks for coming back with it.",
    "That's a nuisance. What's the worst of it now?",
    "Sorry it's no better yet. Say what's changed and I'll go again.",
    "Right, still not right. What's it doing now?",
)


THANKS_TAKES_A_QUESTION = re.compile(
    r"\b(?:can|could|would|should|will|shall|any\s+idea|what|how|why|when|where|who|"
    r"is\s+it|do\s+i|should\s+i)\b")


def _thanks_then_said(clean):
    """The outcome they came back to tell me after a thank-you, or "" when there is none."""
    match = THANKS_OPENS.match(clean.strip().rstrip(".!").strip())
    if not match:
        return ""
    said = match.group("said").strip(" .,!;:")
    if len(re.findall(r"[a-z']+", said)) < 2:
        return ""
    # A question word inside the outcome is not an ask: "thanks, its back to how it was" and
    # "thanks, its back to where it was" are the good news this pool is for, and the bare "how" and
    # "where" in them were read as a question, so the search hedge answered the report. Take the
    # outcome phrase out and read what is left, which is what decides it: "thanks, still a bit sore
    # but much better" has no question left, and "thanks, worse today, can i take more painkillers"
    # still has one.
    if THANKS_TAKES_A_QUESTION.search(THANKS_GOOD_AGAIN.sub(" ", said)):
        return ""
    return said


# "Good to know" and the rest of its family: an acknowledgement with no thank-you in it. Every
# word of it is a manners word, so `_only_manners` reads it, but there is no thanks for the
# thanks reading to find and no question in it for the hedge to answer - and the hedge is what it
# got: "good to know" was answered "I'm not sure about that one, sorry - I'd rather not guess. A
# quick search online will get you a solid answer", and "good to know thanks" the same, one word
# of thanks later. `know` is the question word that made the line into an ask, so the whole line
# has to be this shape, anchored at both ends: "how do i know if its cooked" and "do you know
# where i can get one" are asks and are not in it.
_ACKNOWLEDGES_ALONE = re.compile(
    r"^(?:(?:oh|ok|okay|right|well|ah|aye|yes|yeah|great|good|nice|cool|brilliant|lovely|"
    r"perfect|interesting|thats|that's|that|it's|its|thanks|thank\s+you|cheers|ta|"
    r"ill|i'll|i|will|do)[\s,]+)*"
    r"(?:(?:good|great|useful|handy|nice|lovely|brilliant|perfect|helpful|interesting|"
    r"reassuring|worth)\s+)?(?:to\s+know|knowing|to\s+hear|to\s+see)\b"
    r"(?:[\s,]+(?:that|it|this|then|so|now|thanks|thank\s+you|cheers|ta|mate|for\s+that))*"
    r"[\s.!]*$")


def _acknowledges_alone(clean):
    """True when the whole line is "good to know" and nothing else.

    Named apart from the thanks reading because there is no thanks in it: the reply is the same
    short one, and the reason it must not reach the hedge is different. Nobody asks the bot to
    search for anything when they say it.
    """
    return bool(_ACKNOWLEDGES_ALONE.match(" ".join(str(clean or "").lower().split())))


def _thanks_with_more(clean):
    """True when the line is thanks and nothing else, however many words it takes to say it."""
    text = clean.lower()
    if "?" in text:
        return False
    words = set(re.findall(r"[a-z']+", text))
    if not (words & THANK_WORDS):
        return False
    return _only_manners(text, THANKS_ONLY)


def _advice_thread_is_about_the_body(memory):
    """True when the advice this thread is reporting on was about the person's body.

    The four pools that say "get it looked at" are for a symptom, and they read wrong after a
    pan of pasta or a boiler. The last few lines the person said decide it, because the advice
    may be the end of a thread that opened several turns earlier.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-6:]
    for turn in reversed(turns):
        line = str(turn.get("user") or "").lower()
        if line and _worry_is_about_the_body(line, line.split()):
            return True
    return False


def _a_step_word_in(words, steps):
    """Whether the line names something the answer named."""
    for word in words:
        if str(word).replace("'", "").strip(".,!?;:-\u2014") in steps:
            return True
    return False


def _a_report_on_the_advice(clean, words, about_the_body=True, the_lot_ok=False, steps=NO_STEP):
    """The pool for a report on advice just given, or None.

    Only a line that is nothing but the report counts: every word has to be one a report uses,
    so "i tried that new cafe" is a place and "it helped my mum" is about her, and both are left
    to the pools below. Apostrophes are dropped first, because "ive been doing it" is how people
    type and it is the same report.

    A word the answer itself used is a report word too: the answer's "wipe it out with a damp
    cloth" is where "i wiped it and now its worse" comes from, and no list of report words could
    have it. `steps` is what the answer said (`_the_words_in`), so the line has to be
    built from words of the advice and words a report uses, and nothing else.
    """
    if "?" in clean or len(words) > 14:
        return None
    if {str(word).strip(".,!?;:-\u2014'") for word in words} & THANKS_WORDS:
        # "thanks, that worked" is a thank-you with a report inside it, and the thanks pool says
        # the warm thing back ("Any time."). Read as a report it was answered "Good - that is the
        # end of it, then.", which is the bot closing its own advice instead of taking the thanks.
        return None
    for word in words:
        bare = str(word).replace("'", "").strip(".,!?;:-\u2014")
        if bare in REPORT_FILLER or bare in steps or bare in REPORT_VERDICT_WORD:
            continue
        return None
    # "none of that worked" holds "that worked" inside it, so the no-change report is read
    # before the one that says it is done: the reading of a report is the whole line, and a
    # line that says it did not work is not a line that says it did.
    pools = ((TRIED_NO_CHANGE, TRIED_NO_CHANGE_REPLIES, TRIED_NO_CHANGE_ELSEWHERE),
             (TRIED_WORSE, TRIED_WORSE_REPLIES, TRIED_WORSE_ELSEWHERE),
             (REPORT_NOW_FINE, TRIED_SORTED_REPLIES, TRIED_SORTED_REPLIES),
             (TRIED_HELPED, TRIED_HELPED_REPLIES, TRIED_HELPED_ELSEWHERE),
             # A "still" that has already been read as worse, sorted or helped is not this one:
             # "its still working" is the helped pool above, and only a still with no word for a
             # good outcome is the trouble that has not moved.
             (STILL_THE_TROUBLE, TRIED_NO_CHANGE_REPLIES, TRIED_NO_CHANGE_ELSEWHERE),
             (TRIED_IT, TRIED_IT_REPLIES, TRIED_IT_REPLIES),
             (TRIED_THAT_ONLY, TRIED_IT_REPLIES, TRIED_IT_REPLIES),
             (DONE_IT, TRIED_IT_REPLIES, TRIED_IT_REPLIES))
    # "ive tried everything" is the no-change outcome said about the whole of it rather than
    # about one go, so it gets the no-change wording: "Any change since you started?" asks a
    # person who has finished trying whether they have noticed anything yet ("im 34 and i still
    # bite my nails" / "ive tried everything").
    if the_lot_ok:
        pools = pools + ((TRIED_THE_LOT, TRIED_NO_CHANGE_REPLIES, TRIED_NO_CHANGE_ELSEWHERE),)
    for shape, on_the_body, elsewhere in pools:
        if shape is STILL_THE_TROUBLE and not _a_step_word_in(words, steps):
            # "still nothing" is somebody waiting on a text that has not come ("i texted him back
            # two weeks ago" / "still nothing"), not a step that did not work. A "still" report has
            # to name something the answer named, which is what a real one does: "still dripping"
            # after an answer about a dripping tap.
            continue
        if shape.search(clean):
            return on_the_body if about_the_body else elsewhere
    return None


def _the_outcome_of_the_advice(memory, clean, words):
    """The pool for a report on the advice in the last answer, or None.

    The answer has to have been a long one - that is what makes it advice a person could act on
    and report back on - and the thread must not be a loss, where "i tried that" is about the
    person who died and the outcome pools would be grotesque. Read in one place, because the
    reply and the presence of a reply have to agree: the arbiter asks the same question through
    `takes_as_it_comes` before a module that would answer the report with a stock line gets the
    turn ("its not helping" was answered "Alright then - good luck with it.").
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    last = str(turns[-1].get("bot") or "") if turns else ""
    # The check-in question ("How is it going with it so far?") is the bot's line right after
    # the advice, so a report that answers it is still a report on the advice: the cue is looked
    # for in the last few of the bot's lines, not only the one above.
    seen = [str(turn.get("bot") or "") for turn in turns[-ADVICE_TURNS:]]
    if not any(_advice_in(line) for line in seen):
        return None
    if _in_a_loss_thread(memory) or _grief_thread(memory):
        return None
    if len(last) < ADVICE_LENGTH and not ADVICE_CUE.search(last.lower()):
        # A line that is nothing but the report says what it is, and the tight word list is the
        # guard then rather than the length: "and if that doesnt work" came after a thirty-word
        # bit of the same advice, and it was answered as a fault to troubleshoot ("Ugh, those are
        # fiddly. How long has it been like that?") because the answer was three characters short
        # of the long-advice gate. A report with words of its own still needs the long answer -
        # unless the short answer names something to do (`ADVICE_CUE`), in which case it is
        # advice whatever its length, and unless the advice is one line further back behind the
        # check-in question.
        earlier = any(_advice_in(line) for line in seen[:-1])
        if not earlier and (len(words) > 6 or len(last) < ADVICE_LENGTH_BARE):
            return None
    return _a_report_on_the_advice(clean, words, _advice_thread_is_about_the_body(memory),
                                   the_lot_ok=not reject.offers_a_choice(memory),
                                   steps=_the_words_in(the_advice(memory)))


def the_advice(memory):
    """The bot's own advice this thread is reporting on, lower case, or "" when there is none."""
    for turn in reversed([t for t in (memory.get("turns") or []) if isinstance(t, dict)]
                         [-ADVICE_TURNS:]):
        reply = str(turn.get("bot") or "").lower()
        if _advice_in(reply):
            return reply
    return ""


def reads_as_a_report(text, memory):
    """Read by the arbiter: is this line a report on the advice just given?

    The same question `_the_outcome_of_the_advice` answers for the reply, published so the router
    can ask it without a second reading of the line. See `TAKES_AS_IT_COMES`.
    """
    clean = " ".join(str(text or "").lower().split())
    try:
        return bool(_the_outcome_of_the_advice(memory, clean, clean.split()))
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return False


def _the_answer_above_already_says_what_to_do(turns, memory):
    """Did the card answer above already say what to do when the answer comes back no?

    A deposit card that says "ask in writing for an itemised list, and use the protection scheme"
    is the reply to the landlord saying no as well as to the question, and the store hands it back
    ("Same answer, and it covers this: ..."). Only an entry answer counts: advice that was the
    composer's own has no card behind it to come back with.
    """
    if not turns:
        return False
    if not (memory.get("entry_answer") or memory.get("entry_answers")):
        return False
    return bool(AN_ANSWER_ABOUT_A_NO.search(str(turns[-1].get("bot") or "")))


def _a_thread_about_how_somebody_treats_them(turns):
    """Whether the chat is on somebody's conduct rather than on a request for something.

    "im being bullied at work" and "my manager keeps touching me" are things done to the person,
    and what the no means there is that the move is a record and a route, not a smaller ask. The
    words are the composer's own grievance vocabulary (`GRIEVANCE_HARM`), read over the person's
    own lines, so a new harm word reaches this guard and the grievance pool together.
    """
    for turn in turns[-4:]:
        said = set(re.findall(r"[a-z']+", str(turn.get("user") or "").lower()))
        if TREATMENT_HARM & said:
            return True
    return False


def _the_next_move_after_the_advice(memory, clean, words):
    """The step the answer itself named, for a report that the advice did not work, or None.

    "Then stop doing more of the same and change one thing instead" is advice to change, told to
    somebody who has just changed and reported back. When the answer ends on who to go to if the
    advice is not enough ("ask a GP", "call a Gas Safe engineer"), that sentence is the next move
    and the only thing left to say. bot/memory/repeat owns the reading of what was said, so the
    sentence comes from there; with no step to give, the pools below stand as they are.

    The length gate the outcome pools use is not applied here: an answer of thirty words that ends
    on a next step is still advice with a next step, and it is the sentence that matters.
    """
    pool = _a_report_on_the_advice(clean, words, _advice_thread_is_about_the_body(memory),
                                   the_lot_ok=not reject.offers_a_choice(memory),
                                   steps=_the_words_in(the_advice(memory)))
    if pool not in (TRIED_NO_CHANGE, TRIED_NO_CHANGE_ELSEWHERE):
        return None  # "it helped" or "it made it worse" is answered by the outcome itself
    if _in_a_loss_thread(memory) or _grief_thread(memory):
        return None
    try:
        return repeat.the_next_move(memory, clean) or None
    except Exception:  # noqa: BLE001 - a memory layer that cannot answer adds nothing
        return None


AFTER_THING = re.compile(r"\s+(?:out\s+of|out|off|from|in|into|on|onto|over|under|"
                         r"with|about)\s+(?:(?:a|an|the|some|another)\s+)?(\w+)")


ASK_WORD = re.compile(r"\b(?:can|could|should|shall|do|does|did|is|are|will|would|may|"
                      r"might|what|whats|how|hows|when|where|why|which|am|ok|okay)\b")


# How much of the thread's answer an intervening reply has to say back to be the thread going on
# rather than the end of it. Three is what the burn's own entry keeps ("burn", "blister",
# "cover"), and what an answer about another subject does not: a line about a shoe rubbing a
# blister shares "blister" and nothing else.
THE_THREAD_KEPT = 3


def _in_a_loss_thread(memory):
    """True when one of the last few things said was about a death.

    Grief is not a body that mends. `im over it now` two turns after `my dad died in march` is
    the same loss said again, and "take it gently for a day or two and let it stick" answers it
    with advice for a bad back.
    """
    for turn in [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-4:]:
        said = str(turn.get("user") or "").strip()
        if said and loss.reads_as_loss(said.lower()):
            return True
    return False


# A nod after a bereavement is still the same conversation, and the stock nod pool opens with a
# closing line for a chat about a dripping tap. The two words either side of it are enough to
# know: the bot's own condolence, or the person's own news.
#
# "funeral", "passed away", "sorry for your loss" can only be about a person. "dead" and "died"
# cannot: a laptop dies and an engine dies, and a nod after either is not a bereavement, so those
# words need somebody in the line with them.
LOSS_IN_TURN_CLEAR = re.compile(
    r"\b(?:funeral|buried|burial|cremat\w*|grief|grieving|bereave\w*|widow\w*|condolence\w*|"
    r"sorry for your loss|passed away)\b")


LOSS_IN_TURN_ANYBODY = re.compile(r"\b(?:died|dying|death|deaths|dead|lost (?:my|her|his|our))\b")


# The people who die are open-ended and the things that die are a short closed list, so an unknown
# subject is read as a person: "sandra died last week" is a condolence and "my tv died" is not.
LOSS_A_THING = re.compile(
    r"\b(?:laptop|phone|mobile|engine|battery|car|van|plant|plants|machine|washing machine|"
    r"tv|telly|fridge|freezer|boiler|dishwasher|dryer|oven|router|computer|pc|printer|hoover|"
    r"vacuum|watch|clock|bike|mower|heating|bulb|lights?|screen|console|kettle|toaster|"
    r"microwave|cooker|radiator|immersion|shower|pump|drone|drones|lawnmower|lawn mower|moped|"
    r"scooter|motorbike|tablet|ipad|wifi|wi-fi|internet|broadband|signal|connection|speaker|"
    r"headphones|earbuds|camera|torch|iron|drill|radio|music|party|battery|charger|"
    r"satnav|gps|tumble dryer|hot water|plug|fuse|switch)\b")


LOSS_IT_DIED = re.compile(r"\bit(?:'s| is| has| had)?\s+(?:just\s+)?(?:died|dead|dying|gone)\b")


# "lost" is the same word for a person and for a job, a set of keys or a house, and the thing that
# is lost is what says which: a job is a hard week and a bereavement is not one.
LOSS_A_LOST_THING = re.compile(
    r"\blost (?:my|our|his|her|their|the) (?:job|jobs|work|shift|hours|keys|key|wallet|purse|"
    r"passport|ticket|tickets|money|savings|deposit|house|home|flat|bag|card|cards|licence|"
    r"license|id|fob|bus pass|phone|mobile)\b")


LOSS_SOMEBODY = re.compile(
    r"\b(?:mum|mom|mam|mother|dad|father|nan|nana|gran|granny|grandma|grandad|grandpa|"
    r"grandmother|grandfather|sister|brother|wife|husband|partner|son|daughter|baby|child|"
    r"children|uncle|aunt|auntie|cousin|friend|mate|neighbour|neighbor|fiance\w*|boyfriend|"
    r"girlfriend|he|she|him|her|his|hers|they|them|person|people|someone|somebody|man|woman|"
    r"lady|lad|boy|girl|pet|dog|cat|puppy|kitten)\b")


def _a_loss_in(text):
    """True when the line is about somebody dying, not about a thing that stopped working."""
    text = (text or "").lower()
    if LOSS_IN_TURN_CLEAR.search(text):
        return True
    if not LOSS_IN_TURN_ANYBODY.search(text):
        return False
    # the thing that was lost beats the person who lost it: "my dad lost his job" is a bad week
    # and "i lost my dad" is not, and only the object of "lost" tells them apart.
    if LOSS_A_LOST_THING.search(text):
        return False
    # a person word in the line beats any thing word: a man who came off his bike and died is a
    # bereavement, and only a line with nobody in it can be a machine that stopped.
    if LOSS_SOMEBODY.search(text):
        return True
    if LOSS_IT_DIED.search(text) or LOSS_A_THING.search(text):
        return False
    return True


# "dead" on its own is a British intensifier as often as it is a death - "dead funny", "dead on
# my feet", "dead tired", "dead good", "drop dead", "im dead" when they are worn out - and a
# line whose only death word is "dead" is where every one of those idioms lives. The loss module
# already reads them all (`reads_as_loss` knows the laughing and the worn-out lines), so its
# answer is the one that counts there. A line that says "died", "death" or "funeral" is read on
# its own words: "he died" and "sandra died last week" carry no idiom in them.
DEAD_AND_NOTHING_ELSE = re.compile(r"\bdead\b")


DIED_OR_DEATH = re.compile(r"\b(?:died|dying|dies|death|deaths|lost (?:my|her|his|our))\b")


def _dead_is_the_only_death_word(said):
    """True when the only death word in the line is "dead", where the idioms live."""
    return bool(DEAD_AND_NOTHING_ELSE.search(said)) and not DIED_OR_DEATH.search(said)


LOSS_OWN_WORDS = tuple(loss.LOSS_REPLIES) + tuple(loss.AFTER_REPLIES)


def _we_condoled(line):
    """True when the bot's own line was a condolence from the loss pools.

    Read on the opening of the line, because a reply is the pool's sentence and sometimes a
    question after it, and the sentence is what says which thread we are in.
    """
    line = (line or "").strip()
    return bool(line) and any(line.startswith(reply[:30]) for reply in LOSS_OWN_WORDS)


# A machine stops without anybody dying, and "my laptop died" is a repair rather than a loss:
# the nod after the advice is neither a condolence nor a win. Main's own reading already tells the
# two apart (`_a_loss_in`), so a death word that is not a loss is a thing that stopped.
def _a_thing_stopped(clean):
    """True when a thing stopped working rather than a person or a pet dying."""
    return bool(LOSS_IN_TURN_ANYBODY.search(clean or "")) and not _a_loss_in(clean)


def _last_turn(memory):
    """The last turn of the chat, or an empty one."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    return turns[-1] if turns else {}


def _the_last_line_was_bad_news(memory):
    """True when the last thing the person said was bad news about their own life.

    "my mum has cancer", "my dad is in hospital", "i got made redundant": a nod to that is the
    person taking it in, and the reply is room to say more rather than a nod back.
    """
    said = str((_last_turn(memory) or {}).get("user") or "")
    return bool(said) and reads_as_bad_news(said.lower())


def _the_last_line_was_a_fault(memory):
    """True when the last thing the person said was a thing or a body of theirs going wrong.

    "my knee is sore when i run", "my boiler keeps cutting out", "my laptop died": everyday
    trouble rather than heavy news, and the nod after it was congratulated just the same.
    """
    said = str((_last_turn(memory) or {}).get("user") or "")
    if not said:
        return False
    clean = said.lower()
    if reads_like_a_symptom(clean):
        return True
    return bool(trouble.reads_as_trouble(clean) or _a_thing_stopped(clean))


def _a_loss_recently(memory):
    """True when the last thing said, either way, was a death or a funeral.

    The bot's own condolence line counts even when it names no death word ("There's no rush to
    talk about it"): that is the thread the person is in, and the nod belongs to it.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    last = turns[-1]
    said = str(last.get("user") or "").strip().lower()
    if said and (not _dead_is_the_only_death_word(said) or loss.reads_as_loss(said)):
        if _a_loss_in(said):
            return True
    # the condolence after the condolence: "the funeral was yesterday" is answered, then "i feel
    # empty" is answered with room to talk, and the nod after that belongs to the death and not
    # to a fresh chat. Neither of our lines has to name the death for the thread to be that one.
    ours = str(last.get("bot") or "")
    if _we_condoled(ours):
        return True
    # the bot's own words are not the person's: an answer about a machine "that has stopped
    # dead" is not a bereavement, so only a word that can only be about a person is read there.
    both = " ".join(str(last.get(k) or "") for k in ("user", "bot")).lower()
    return bool(LOSS_IN_TURN_CLEAR.search(both))


def _in_sudden_loss_thread(memory):
    """True when the bot's own last line was its reply to a sudden loss."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    last = str(turns[-1].get("bot") or "")
    return bool(last) and any(last in pool for pool in
                              (SUDDEN_LOSS, PREGNANCY_BLEEDING, THE_FIRST_HOUR_AND_A_CHILD))


def _reads_as_illness(clean):
    """True when the word "ill" in the line means sickness rather than "I'll"."""
    words = [w.strip(".,!?;:'\"") for w in clean.split()]
    for n, word in enumerate(words):
        if word.strip(".,!?;:'\"") != "ill":
            continue
        before = words[n - 1] if n else ""
        if before in ILL_SAID_OF_A_BODY:
            return True
        # "so ill be on 34k", "and ill be there by eight": the verb after it is the tell, and it
        # beats a degree word in front, because a body is never ill *be* something.
        if n + 1 < len(words) and words[n + 1].strip(".,!?;:'\"") in ILL_WILL_VERBS:
            continue
        if n and before in ILL_BEFORE:
            return True
        if n == len(words) - 1 or words[n + 1] in ILL_AFTER:
            return True
    return False


# A cue word that is the thing the person wants to do is not a mood: "i want to lose weight"
# is an aim, and "Sorry to hear that" answers a feeling nobody expressed. Only an aim with
# nothing else wrong in the line counts, so "im trying to lose weight but the scales wont
# move" stays a frustration. A negated aim ("i dont want to lose the house") is the fear
# itself, so it stays too.
AIM_BEFORE = re.compile(
    r"(?:\b(?:want|wants|wanting|trying|try|need|needs|plan|planning|hoping|hope|help|helps"
    r"|starting|started)\s+(?:to\s+|me\s+to\s+)?"
    r"|\b(?:how\s+do\s+i|how\s+can\s+i|how\s+to|best\s+way\s+to|ways\s+to|tips\s+to"
    r"|tips\s+for|any\s+advice\s+on)\s+)$"
)


def _in_an_aim(clean, word):
    """True when every use of this word is the thing the person is setting out to do."""
    if " but " in clean or " though " in clean or " although " in clean:
        return False
    hits = list(re.finditer(r"\b%s\b" % re.escape(word), clean))
    if not hits:
        return False
    for match in hits:
        before = clean[:match.start()]
        if not AIM_BEFORE.search(before):
            return False
        if {w.strip(".,!?") for w in before.split()[-3:]} & AIM_NEGATORS:
            return False
        after = match.end()
        if {w.strip(".,!?") for w in clean[after:].split()} & AIM_FAILING:
            return False  # the aim is not going well, so it is a trouble after all
    return True


def _a_mood_word(words, word):
    """True when a word that is also a thing is describing something rather than naming it."""
    for index, said in enumerate(words):
        if said != word:
            continue
        before = words[index - 1] if index else ""
        after = words[index + 1] if index + 1 < len(words) else ""
        if before in COPULA:
            # "the food was crap" and "this phone is rubbish" are the thing's fault, not a weight
            # the person is carrying; "i feel rubbish" and "the week was rubbish" are theirs.
            subject = words[:index - 1]
            last = subject[-1] if subject else ""
            if (last in ABOUT_THEM_BEFORE_COPULA or set(subject) & STRETCH_OF_TIME
                    or not subject or (len(subject) == 1 and last in ("it", "this", "today"))):
                return True
            continue
        if before in MOOD_BEFORE or after in MOOD_AFTER:
            return True
    return False


# Going over the same thing and getting nowhere, which people say far more often than they say
# what it is: "i keep going over it in my head", "its been on my mind all week", "i cant stop
# replaying what i said", "on repeat since friday". The line has no subject a module can pick up,
# so without this it is either said back word for word or met with "noted". What a friend does is
# name the loop and ask the one thing it keeps coming back to, so that is the whole reply.
RUMINATION = re.compile(
    r"\b(?:keep|keeps|kept|can'?t|cant|cannot|stop|stopped)\s+(?:thinking|replaying|reliving|"
    r"dwelling|worrying)\b"
    r"|\b(?:go|going|think|thinking)\s+(?:over|through|round|around)\s+(?:it|that|this|him|her|"
    r"them|what)\b"
    r"|\b(?:on my mind|in my head|over and over|again and again|round in circles|on repeat|"
    r"switch off|can'?t shake|can not shake)\b")


# A line with a thing in it that a module knows ("i keep thinking about my mortgage", "i keep
# going over the numbers for the new car") is that thing said again, not a loop to be named: the
# loop wording would take the turn off the module that could actually answer it.
WITH_A_SUBJECT = re.compile(
    r"\b(?:my|our|his|her|their|the)\s+(?:\w+\s+)?(?:mortgage|loan|debt|rent|money|budget|"
    r"bills?|job|boss|car|boiler|washing machine|fridge|damp|landlord|surgery|doctor|gp|"
    r"appointment|wedding|interview|cv|exam|test|results?|numbers|figures|son|daughter|kids?|"
    r"child|baby|mum|mom|dad|husband|wife|partner|dog|cat|puppy|kitten)\b")


# The same shape holds a want, and there the loop line is wrong in the other direction: "i keep
# thinking about getting a dog" is looking forward to something, and "that kind of thing does not
# let go on its own" hands a happy plan sympathy for a worry they do not have (speedy-dolphin's
# read). A word of wanting says so, and so does the gerund of getting or going after the loop's
# own "about": naming the thing you are going to do is anticipation, not a thing going round.
A_WANT = re.compile(
    r"\b(?:want|wants|wanted|wanting|wanna|hope|hopes|hoping|hoped|plan|plans|planning|planned"
    r"|saving up|saving for|dreaming of|thinking of|looking forward to|working towards?)\b"
    r"|\b(?:thinking|thought|dreaming|dreamt|going|go)\s+(?:(?:about|of|over)\s+)?"
    r"(?:getting|buying|booking|adopting|starting|trying|learning|making|building|moving)\b"
    # "i keep thinking about a holiday" is one they have not had yet; a worry attaches to
    # something definite ("the interview", "my mortgage", "what i said"), which is the same
    # reading WITH_A_SUBJECT already gives the line.
    r"|\b(?:thinking|thought|dreaming|dreamt)\s+(?:about|of)\s+(?:a|an|some|another)\s+\w+")


def _is_rumination(clean):
    """True when the line is the loop itself rather than something a reply could answer."""
    if WITH_A_SUBJECT.search(clean) or A_WANT.search(clean):
        return False
    return bool(RUMINATION.search(clean))


# The same line said with a part of the person as its subject: "my nose is cold", "my ears are
# freezing", "my hands are clammy", "my face is pale". A state said of a part of me is a state of
# me - the same cold sweat and the same pallor whether the person says "im clammy" or "my hands
# are clammy" - and the pools are written to answer either ("Is it just your hands, or all
# over?"). Only a part that has no answer of its own comes here: a hand or a foot being cold is
# circulation, and the answers entry says so better ("warm the whole body, not just the hands"),
# and "my head is hot" is a fever question, so those keep their own readings. Nothing above this
# in the chain has refused the line already, which is what keeps the part's own card first.
BODY_PART = re.compile(
    r"\b(?:my|our)\s+(?:nose|ears?|face|cheeks?|skin|hands?|lips?|forehead|arms?|back)\s+"
    r"(?:are|r|is|feels?|looks?|go|goes)\s+(?P<rest>.+)$")


def _opens_a_question(words):
    """True when the line opens like a question rather than a report of a state.

    "am" is the one opener that is also the person with their subject left off - "am hungry", "am
    freezing" - and it only asks when the pronoun is back in the line ("am i hungry"). Read as a
    question, those lines got the neutral nod: "am hungry" was "I'm listening - say more if it
    helps" where "im hungry" has its answer. Every other opener ("why", "is", "was") asks
    whatever follows it, so it is left as it was.
    """
    if words[0] not in QUESTION_OPENERS:
        return False
    if words[0] != "am":
        return True
    return len(words) > 1 and words[1] in _SUBJECT_AFTER_AM
