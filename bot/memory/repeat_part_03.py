"""Part 3 of 6 of the module, split out of `repeat`.

Everything here is re-exported from `repeat`, so callers import it from there as before.
"""
import re

from ..compose import pick
from ..compose.whole import a_whole_cut
from ..understanding import understand
from . import topics
from .repeat_part_01 import (
    HELP_ASK_QUESTION_FIRST, HELP_SHAPE, NAMED_AFTER_IT, ABOUT_THE_BOT, AT_A_LOSS, JUST_A_NOD,
    QUESTION, WORDS_WANTED, _names_a_thing_of_its_own, LEADS, LOST_LEADS, MOST, ASKING_THEM,
    SENTENCE, NEXT_STEP, MOVE_VERBS, _recent_answers, AGREEMENT_TAIL, AGREES_IN_A_PHRASE,
    AGREES_ON_ITS_OWN, AGREEING, BE_FORM, OPENERS, POINTING_AT, QUALIFIER,
)
from .repeat_part_02 import (
    _already_repeated, _handed_back,
)


def _a_help_ask(text):
    """True when the whole line asks for a way to help and names nothing of its own.

    Three asks that read as one: "is there anything i can do", "any way of making it easier",
    "anything that helps". None of them opens on a question word, so `QUESTION` below never
    matched them and the line went on to be answered as a new question - "any way of making it
    easier" straight after the answer about a toddler who will not settle got "That's most of what
    I know on it", and "is there anything i can do" after the answer about waking at four got the
    same shrug. The person asked for the part of the answer to do, which is what `START_ASK`
    already reads when the line is written "where do i start".

    The reading is the understanding engine's, so its fences hold here too: a negation ("there
    isnt anything i can do"), a thing named after it ("...about the mole on my back") and a line
    that states rather than asks ("anything i can do is never enough") are other turns.
    """
    line = str(text or "")
    if not HELP_SHAPE.search(line):
        return False
    if HELP_ASK_QUESTION_FIRST.search(line) and not NAMED_AFTER_IT.search(line):
        return True
    if a_more_ask(line):
        # "anything else i can do", "anything else that helps": one more thing out of the answer
        # already given, which is `MORE_ASK`'s turn and its own reader's. Read as a help ask it
        # handed the first step of the answer back instead of the next one, so a person who had
        # been given "do not check the clock, keep the light off" asked for another and heard the
        # first one again.
        return False
    return bool(understand(line).get("help_ask"))


def asks_for_the_move(text):
    """True when the line asks which part of the answer in hand to do.

    A start ask ("where do i start", "what should i do first"), a help ask ("is there anything i
    can do") and a how ask with a pronoun in it ("how do i clean it off") are the same turn, so
    every reader that answers one of them answers all three.
    """
    line = str(text or "")
    return bool(says_where_to_start(line) or HOW_IT.search(line) or _a_help_ask(line))


def names_nothing(text):
    """True when the line asks for something without naming anything of its own."""
    if JUST_A_NOD.match(text or ""):
        return False
    lost = bool(AT_A_LOSS.search(text or ""))
    help_ask = _a_help_ask(text)
    if not (QUESTION.match((text or "").strip()) or lost or help_ask):
        return False
    if ABOUT_THE_BOT.search(text or ""):
        return False
    if WORDS_WANTED.search(text or ""):
        return False
    if topics.pairing(text or ""):
        return False
    if help_ask:
        # The engine read the whole line as the ask, and its fences are the ones that know the
        # words of one ("any way", "anything that helps", "is there anything"), so no word list
        # here has to be kept in step with them.
        return True
    return bool(topics.words(text)) and not _names_a_thing_of_its_own(text)


def _a_lead_and_a_step(lead, step):
    """A lead with the step in it, and one full stop at the end.

    Every lead ends the step with its own "." ("One thing to do first: {step}."), and a step that
    already ended a sentence carries one too: "One thing to do first: Quick: tuna pasta in 15 ...
    for 30 minutes.." is the same sentence closed twice.
    """
    said = str(step or "").rstrip()
    return re.sub(r"\.{2,}$", ".", re.sub(r"\.\.\s+", ". ", lead.format(step=said, said=said)))


# A lead that counts cannot take a step that names more than one: "One thing to do first: Two
# calls free up the most cash fastest" has the lead arguing with the step. When the step opens on
# a number above one, or on a pair, that lead is dropped and another of the same kind taken.
A_COUNT_OF_MORE_THAN_ONE = re.compile(
    r"^\W*(?:two|three|four|five|six|seven|eight|nine|ten|both|a couple|a pair|a few|the two|"
    r"the three)\b", re.I)


def _the_lead_for(text, step=""):
    """Which set of leads this line gets.

    "That's the one:" and "You've got it:" say the person agreed to something. A line that says
    they do not know what to do has agreed to nothing, so it takes the leads written for it, the
    ones that just start them off. Without this, "i am thinking of leaving my husband" then "i
    dont know what to do" was handed "That's the one: Before you decide anything...", which
    answers a question nobody asked.
    """
    leads = LOST_LEADS if AT_A_LOSS.search(str(text or "")) else LEADS
    if A_COUNT_OF_MORE_THAN_ONE.match(str(step or "")):
        leads = tuple(lead for lead in leads if "one thing" not in lead.lower()) or leads
    return leads


def _content(text):
    """The words of a line that name something, in the spelling the two sides can be compared in."""
    return {w for w in topics.words(text or "") if w not in topics.STOPWORDS and len(w) > 2}


def _trouble(text):
    """True when the line is a complaint about the thing still in play, not a fact about it.

    "i cant get my kids to eat veg" is followed by "theyre 4 and 7", and "my dog ate half a bar of
    dark chocolate" by "he's a labrador, about 30 kilos": both are the person handing over what
    the bot asked for, and "Got it - they're 4 and 7" is exactly right. The advice handed back
    instead answers a complaint they did not make. So the line has to say something is still
    going wrong ("cant", "keeps", "still", "worse") before the answer's advice comes back.
    """
    return bool(TROUBLE.search(text or ""))


TROUBLE = re.compile(r"\b(?:can'?t|cant|cannot|won'?t|wont|doesn'?t|doesnt|isn'?t|isnt|"
                     r"keeps?|still|never|again|worse|worst|luck|helping|working|nothing)\b",
                     re.I)


# A thing the person says is their own ("my keys", "our boiler"). When the answer just given never
# names it, the answer is not about the thing the line is about, so there is no part of it to hand
# back: "i keep losing my keys" after a weekend-in-a-city answer was handed the doing part of that
# answer ("One that gets you out of the house - a walk you haven't done..."), which is advice for
# a day out given to somebody looking for their keys. `_trouble` alone cannot tell the two apart -
# "i keep losing my keys" is a complaint about something still going wrong, which is the shape
# that earns the hand-back when the trouble IS the thing the answer was about ("and i honestly
# cant get back off", where the line names no thing of its own).
OWNED = re.compile(r"\b(?:my|our|his|her|their)\s+([a-z]{2,})")


# A limit of somebody else's: what a person in the chat cannot have, cannot eat, or must stay away
# from. It is a fact about a person, which is the store's business, not a detail of the answer just
# given - and handing the answer's advice back for it gives the paragraph the person has just read
# and hears nothing of the limit. After the answer about making a room in a care home theirs
# (a framed photo, their own blanket, a box of their usual sweets) the line "she cant have
# chocolate" came back as that whole paragraph again, sweets and all.
SOMEONE_ELSES_LIMIT = re.compile(
    r"\b(?:he|she|they|him|her|them|mum|mom|mother|dad|father|nan|nana|gran|granny|grandma"
    r"|grandad|grandpa|son|daughter|child|kid|boy|girl|husband|wife|partner|brother|sister"
    r"|friend|baby|toddler|little one)\b[^.!?]{0,60}?"
    r"\b(?:can(?:no|')?t\s+(?:have|eat|drink|take|manage)|cant\s+(?:have|eat|drink|take|manage)"
    r"|cannot\s+(?:have|eat|drink|take)|must\s+not\s+(?:have|eat|drink|take)"
    r"|(?:does|do|did)(?:n'?t|nt|\s+not)\s+(?:eat|drink|like|touch)"
    r"|(?:is|are)(?:n'?t|\s+not)\s+allowed|allergic\s+to|intolerant\s+to|stays?\s+away\s+from"
    r"|has\s+to\s+avoid|cuts?\s+out)\b", re.I)


def _a_thing_of_its_own(line, said):
    """True when the line names a thing as its own that the answer does not mention."""
    named = set(OWNED.findall(str(line or "").lower()))
    if not named:
        return False
    words = set(re.findall(r"[a-z']+", str(said or "").lower()))
    stems = {w.rstrip("s") for w in words}
    return not any(word in words or word.rstrip("s") in stems for word in named)


# A thank-you in front of the line, with the rest of it after a full stop: "cheers. also im skint
# till friday", "thanks. my boiler has packed in". The ack closes the turn the answer belonged
# to, so what follows it opens a new one - it is not a detail on the answer just given. Handed
# back, the person who thanked the bot for the washing-machine fix and then said they were skint
# got the washing-machine fix word for word, which is the thing STYLE.md says never to do twice
# in the same words. Only a courtesy word counts: "ok" and "right" in front of a detail ("ok and
# i honestly cant get back off") are still the same turn being carried on.
ACK_OPENS = re.compile(
    r"^\s*(?:ok(?:ay)?\s+)?(?:thanks|thank you|thankyou|thank u|thx|ty|ta|cheers|cheerz|"
    r"much appreciated|appreciated)\b[^.!?]{0,20}[.!?]+\s*\S", re.I)


# The same ack with a comma after it ("thanks, my back has gone") or at the end of a courtest
# phrase: whatever separates the thank-you from the rest of the line.
ACK_AND_REST = re.compile(
    r"^\s*(?:ok(?:ay)?\s+|right\s+|ah\s+|oh\s+|aw\s+)?"
    r"(?:thanks|thank you|thankyou|thank u|thx|ty|ta|cheers|cheerz|much appreciated|appreciated)"
    r"(?:\s+(?:so|very|much|a lot|again|loads|tonnes))?"
    r"[^a-z0-9]{0,20}"
    r"(?P<rest>[a-z0-9].*)$", re.I | re.S)


def after_an_ack(text):
    """The rest of a line that opens with a thank-you, or "" when it opens with anything else.

    "cheers. also im skint till friday and theres nothing in the fridge" is a thank-you and then
    a line about money; "thanks, that helps" is the thank-you and nothing else. The callers use
    this to read what comes after the courtesy: the knowledge base answers it, and a line that
    only closes the turn has nothing there to answer.
    """
    match = ACK_AND_REST.match(str(text or "").strip())
    if not match:
        return ""
    rest = match.group("rest").strip(" ,.!?;:-\u2014")
    # "thanks love, the boiler is still not firing": the name is said to the bot, not part of the
    # line, so it comes off with the thank-you.
    rest = re.sub(r"^(?:mate|love|pet|hun|hunny|duck|sunshine|chief|fella|sweetheart)\b[,!.]*\s*",
                  "", rest, flags=re.I)
    # A rest that opens with "for" is what the thanks is for, not a line of its own: "thanks for
    # explaining", "thanks for the boiler advice". Read as the line it would be a fragment the
    # knowledge base answers with the advice just given all over again.
    if re.match(r"for\b", rest, re.I):
        return ""
    # What is left has to say something. "thanks, that helps" and "thanks, thats great" are the
    # thank-you and nothing else: read on their own they are words about the answer just given, and
    # the knowledge base would hand back the same paragraph - the red-wine answer said twice
    # because the person said thanks for it.
    named = [word for word in topics.words(rest) if word not in CLOSES_THE_TURN]
    return rest if len(named) >= 2 else ""


# The words a line says thank-you with, and the words a line agrees about it with. What is left
# after they come off is what the person is actually asking about.
CLOSES_THE_TURN = frozenset("""that this it helps helped helping help works worked work working
    does did will would good great fine perfect nice handy useful brilliant lovely amazing awesome
    fantastic ok okay much loads lot lots again everything all so very really too just then now
    know noted needed needs glad cheers thanks please mate love pet
    thats kind kindest thoughtful generous sweet of you""".split())


# A line about the thing going round in their head is about how they are, not a detail of the
# doing: after "ask for a specific figure, with the reason attached" a person says "i keep going
# over it in my head at 2am", and the same sentence handed back word for word answers the pay rise
# and not the 2am. The shapes are the ones people use for trouble that will not leave them alone -
# the head, the mind, being awake - and none of them points at anything in an answer to do.
BROODING = re.compile(
    r"\b(?:"
    r"(?:going|goes|went)\s+(?:over|round|around)\b|"
    r"round\s+in\s+(?:my|our)\s+(?:head|mind)|\bin\s+my\s+head\b|\bon\s+my\s+mind\b|"
    r"(?:cant|can'?t|cannot|keep|keeps|kept)\s+(?:stop\s+)?thinking\b|"
    r"think(?:ing)?\s+about\s+it\b|\bthoughts?\s+(?:racing|going)\b|"
    r"my\s+mind\s+(?:is\s+)?(?:racing|going|spinning)"
    r")", re.I)


def _a_feeling(text):
    """True when the line is about how they are, not about the thing the answer was about.

    "i lost my job last week" is answered with what to check in the offer, and the next line,
    "i cant stop crying", is not a question about the offer: handing back "ask for it in writing
    and don't sign it on the day" reads as if nobody had heard the crying. The feeling words are
    the ones the fallback already reads a bad week by, so the two cannot drift apart. A line about
    the trouble following them about (BROODING) is how they are too, even with no feeling word in
    it: "i keep going over it in my head at 2am" is the part of the evening the answer never
    spoke to.
    """
    from ..compose.fallback import NEGATIVE_CUES

    if BROODING.search(text or ""):
        return True
    return bool(set(topics.words(text or "")) & NEGATIVE_CUES)


def _the_doing(sentence):
    """The doing part of a sentence: what follows a short label, and cut to a length that is a
    reply rather than a paragraph.

    "The fix is what you do in those minutes: do not check the clock, keep the light off, and if
    you are properly awake after about twenty minutes get up and sit somewhere dim ..." is advice
    with a label in front of it; on its own the label says nothing about the sleeping, so the part
    after the colon is what the person gets, with its first letter raised because it now opens
    the reply.
    """
    head, sep, rest = str(sentence).strip().partition(":")
    # A label in front of the advice is dropped ("The fix is what you do in those minutes: ..."),
    # but a sentence that itself opens on a doing is an instruction, not a label: "Check the salt
    # and rinse aid too: running out of either makes everything come out cloudy" is the check, and
    # the part after the colon only says why. Handing back the reason would answer a person who
    # asked for the next step with something to do nothing about.
    if sep and not _opens_a_doing(head) and len(head.split()) <= 12 and len(rest.strip()) >= 20:
        whole = rest.strip()
        whole = whole[0].upper() + whole[1:]
    else:
        whole = str(sentence).strip()
    whole = a_whole_cut(whole, MOST)
    last = whole.rstrip("'\"\u2019\u201d")
    return whole + "." if whole and not last.endswith((".", "!", "?")) else whole


def _the_advice(said):
    """The sentence of an answer that tells them what to do, or None when it tells them nothing.

    "The fix is what you do in those minutes: do not check the clock, keep the light off, and if
    you are properly awake after about twenty minutes get up ..." is the most of an instruction in
    that answer, and it is the part a person who says "i cant get back off" can use. A sentence of
    explanation ("Waking in the night is normal") has nothing to do in it, so it is never picked.
    """
    from ..compose.verdict import IMPERATIVES  # the verbs an instruction can open on

    best, most = "", 1
    for part in [p.strip() for p in SENTENCE.split(str(said).strip()) if p.strip()]:
        if topics.RED_FLAG.match(part) or ASKING_THEM.search(part):
            continue
        words = [w.strip(" ,;:.") for w in part.lower().split()]
        count = sum(1 for w in words if w in IMPERATIVES)
        count += 1 if re.search(r"\bdo not\b|\bdon'?t\b", part, re.I) else 0
        if count > most:
            best, most = part, count
    return best


def _next_step(said):
    """The sentence an answer ends on about who to go to, when the advice alone is not enough."""
    sentences = [s.strip() for s in SENTENCE.split(str(said or "")) if s.strip()]
    for sentence in reversed(sentences[1:]):
        if NEXT_STEP.search(sentence):
            return sentence
    return ""


def _later_part(tried, said):
    """The part of one answer that comes after the step the line says it has tried."""
    def shared(part, words):
        return sum(1 for w in _content(part)
                   if any(w == v or (len(w) >= 5 and len(v) >= 5 and w[:5] == v[:5])
                          for v in words))

    parts = [p.strip() for p in SENTENCE.split(str(said).strip()) if p.strip()]
    tried_words = _content(tried)
    best_i, most = -1, 0
    for i, part in enumerate(parts):
        count = shared(part, tried_words)
        if count > most:
            best_i, most = i, count
    if best_i >= 0:
        # The tried step is in the answer: the sentence right after it is the next step, not
        # whatever later sentence happens to share the fewest words (that can be another part of
        # the answer, such as the patio paragraph after the lawn one).
        later = []
        for part in parts[best_i + 1:]:
            if topics.RED_FLAG.match(part) or ASKING_THEM.search(part):
                continue
            if shared(part, tried_words) >= most:
                continue
            doing = _the_doing(part)
            if len(doing) >= 25:
                later.append(doing)
        # Not every later sentence is a step. An answer often puts how long the step takes
        # between the step and the next one ("... clean the filter and the detergent drawer
        # while it runs. The wash itself is about two hours. Leaving the door and drawer open
        # between washes is what stops the smell coming back"), and handing back the timing
        # reads as advice given to someone who asked for the next move. The sentence that opens
        # on a doing is the step; the timing is skipped, and the first qualifying sentence is
        # still the answer when none of them opens on one.
        for doing in later:
            if _opens_a_doing(doing):
                return doing
        return later[0] if later else ""
    # The step is not named in the answer ("ive tried bleach" against a drain answer that says
    # chemical cleaner): the last sentence is the part they have not heard yet.
    best = ""
    for part in parts[1:]:
        if topics.RED_FLAG.match(part) or ASKING_THEM.search(part):
            continue
        doing = _the_doing(part)
        if len(doing) >= 25:
            best = doing
    return best


def _opens_a_doing(sentence):
    """Whether a sentence opens on a doing rather than on its subject.

    "Leaving the door and drawer open between washes is what stops the smell coming back" opens
    on the habit to keep, and "The wash itself is about two hours" opens on the wash: the first
    is something to do, the second is how long the thing they just did takes. The test is the
    first word - an instruction's verb, or the "-ing" form of one, which is how an answer says a
    step that is a habit rather than a one-off.
    """
    from ..compose.verdict import IMPERATIVES

    words = str(sentence).strip(" .,:;").split()
    if not words:
        return False
    first = words[0].lower().strip(".,;:")
    if first in IMPERATIVES or first in MOVE_VERBS:
        return True
    if first.endswith("ing") and len(first) > 4:
        stem = first[:-3]
        bare = [stem, stem + "e"]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            bare.append(stem[:-1])
        return any(candidate in IMPERATIVES for candidate in bare)
    return False


def _the_untried(tried, memory):
    """The later part of the last answer that is not the step they have just tried.

    "my sourdough is flat" / "i tried the starter and it still flopped" used to stand down to a
    filler, but the answer's last sentence is the next diagnosis, not the step they tried. The
    same is true of "ive tried the filter and the drawer": the answer's later sentence - leave the
    door open - is what is left to do. Only a later sentence qualifies: a one-sentence answer has
    no next step to hand back.
    """
    for back, _question, said in _recent_answers(memory):
        if back != 1:
            return None
        best = _later_part(tried, said)
        if best and not _already_repeated(best, memory):
            return _handed_back(memory, best)
    return None


# A line that says the step has already been done is not picking the step out of the answer: it
# is telling the bot the advice did not work. Handing the same step back reads as if nobody had
# listened ("ive tried a hot wash already" got the service-wash sentence again), so the answer
# hands back its later step instead; only the line that asks nothing new stands down.
TRIED = re.compile(r"\b(?:i|we|he|she|they)\s+(?:already\s+)?(?:tried|done)\b|"
                   r"\b(?:i(?:'ve|ve| have)|we(?:'ve|ve| have)|he(?:'s|s| has)|"
                   r"she(?:'s|s| has)|they(?:'ve|ve| have))\s+(?:already\s+)?"
                   r"(?:tried|done|had)\b|\balready\s+(?:tried|done|had)\b|"
                   r"\b(?:tried|done)\s+(?:that|it|this)\b", re.I)


# Only a negation of the attempt itself ("i haven't tried", "never done") keeps the advice.
# A later "it did not work" is the reason to say it was tried, not a claim that it was not.
NOT_TRIED = re.compile(r"\b(?:not|never|havent|hasnt|didnt|haven't|hasn't|didn't)\s+"
                       r"(?:\w+\s+){0,2}(?:tried|done|had)\b", re.I)


# A line that says the step was tried and then asks about another part of the same answer is
# still a follow-up ("ive done the vinegar, how long should i leave the citric acid"). The
# stand-down is only for the line that asks nothing new.
QUESTION_MORE = re.compile(r"\b(?:how|what|when|why|which|should)\b", re.I)


def _tried(text):
    """True when the line says the advice has already been carried out, not that it failed."""
    return bool(TRIED.search(text or "")) and not NOT_TRIED.search(text or "")


def _says_they_agree(clean):
    """Whether the line carries a word that agrees: "ok so low heat then", "low heat, got it".

    A line that happens to sit inside one sentence of the answer word for word is not always an
    agreement: "the washer is old" after the dripping tap answer is the person telling the bot
    something, and saying it back ("Yes - the washer is old.") is the bot parroting them. What
    makes a line an agreement is the word in it that agrees - ok, so, then, got it, right - so
    that is what is asked for.
    """
    words = [word.strip(".,!;:\"'").lower() for word in clean.split()]
    if any(word in AGREES_ON_ITS_OWN for word in words):
        return True
    if AGREES_IN_A_PHRASE.search(clean):
        return True
    # A joining word on its own is not a yes, and the line it starts is often another item
    # altogether ("and for hard boiled", "and a root canal"). The word a person puts after a
    # thing they are agreeing with is the yes: "so low heat then", "low heat as well".
    return len(words) <= 8 and bool(words) and words[-1] in AGREEMENT_TAIL


def _the_thing_they_named(clean, part):
    """The words of the line that are the answer's own, in the person's order: "low heat".

    "ok so low heat then" is the answer's sentence with an agreement round it, and the thing the
    person said is the part of it they named. The agreement words come out, so the reply names the
    thing rather than repeating the agreement back at them. Every other word stays as they said
    it, including one with no stem of its own ("same time every day"), because the line has
    already been matched against the answer and those are the words they chose.
    """
    kept = []
    for word in clean.split():
        bare = word.strip(".,!;:\"'").lower()
        if not bare or bare in AGREEING:
            continue
        # The line has already been matched against the answer, so the words left are the ones
        # the person named: a word with no stem of its own ("same", "every") is still theirs to
        # say back. Only the agreement comes out.
        kept.append(word.strip(".,!;:\"'"))
    # A thing said with the copula in front of it is still the thing: "it was black mould" after
    # the grout answer named the mould, and the confirmation came out as "Was black mould, yes."
    # - the copula capitalised into the reply as if it were part of the name.
    while len(kept) > 1 and kept[0].lower() in BE_FORM | POINTING_AT:
        kept = kept[1:]
    if not kept or len(kept) > 4 or kept[0].lower() in BE_FORM | POINTING_AT:
        return ""
    # A line that opens on a preposition is a detail of the answer rather than a thing it named
    # ("it was in a big pot" after the repotting advice), so there is nothing to say back: the
    # confirmation of it ("In a big pot, yes.") tells the person nothing they did not just say.
    if kept[0].lower() in OPENERS:
        return ""
    return " ".join(kept)


def _agreed(named, memory):
    """The confirmation of a thing the person said back: "Low heat, yes."

    Every line names the thing, so the pool cannot be read out to anybody else, and the answer
    just given is never one of them.
    """
    low = named[:1].lower() + named[1:]
    up = named[:1].upper() + named[1:]
    return pick([up + ", yes.",
                 "Yes \u2014 " + low + ".",
                 up + " it is.",
                 "That's it: " + low + ".",
                 up + ", that's the main thing."], memory, named)


# A step said in the past tense is a step tried. "i topped it up yesterday", "i did the hot wash",
# "i changed the washer already" report the same news as "ive tried topping it up": the advice did
# not work, and handing it back - or asking "what made you start on that?" - reads as if nobody
# had listened. The gate is the act, not the word (TRIED above only knows the words tried, done
# and had): the past tense has to name a step the answer just gave, so a past tense about anything
# else ("i paid the bill", "i walked to work") is still the person's own news.
DONE = re.compile(
    r"\b(?:i|we|he|she|they)\s+(?:(?:have|had|already|just|finally|now|then|since)\s+)*"
    r"(?P<verb>[a-z]+)\b", re.I)


# The past forms that are not spelled with -ed.
IRREGULAR_PAST = {
    "did": "do", "done": "do", "made": "make", "took": "take", "given": "give", "got": "get",
    "left": "leave", "kept": "keep", "cut": "cut", "put": "put", "set": "set", "ran": "run",
    "bled": "bleed", "hung": "hang", "wore": "wear", "fed": "feed", "found": "find",
    "built": "build", "sent": "send", "spent": "spend", "threw": "throw", "dug": "dig",
    "held": "hold", "lit": "light", "swept": "sweep", "bought": "buy", "caught": "catch",
    "taught": "teach", "told": "tell", "sold": "sell", "froze": "freeze", "drew": "draw",
    "shut": "shut", "spread": "spread", "paid": "pay", "struck": "strike", "shook": "shake",
}


NO_LONGER_TO_DO = frozenset("""not never no havent hasnt didnt doesnt dont wont cant
    haven't hasn't didn't doesn't don't won't can't""".split())


def _the_stems(word):
    """The base verbs an -ed form could have come from ("topped" -> top, "dried" -> dry)."""
    word = str(word or "").lower()
    out = set()
    if word.endswith("ied") and len(word) > 4:
        out.add(word[:-3] + "y")
    if word.endswith("ed"):
        base = word[:-2]
        out.add(base)
        out.add(base + "e")
        if len(base) > 2 and base[-1] == base[-2]:
            out.add(base[:-1])
    elif word.endswith("d") and len(word) > 3:
        out.add(word[:-1])
    return out


def _the_act(word):
    """The step a word names in the past tense, if it is one an instruction can open on."""
    from ..compose.verdict import IMPERATIVES  # the verbs the base says a step with

    base = IRREGULAR_PAST.get(word)
    if base and (base == "do" or base in IMPERATIVES):
        return base
    for stem in _the_stems(word):
        if stem in IMPERATIVES:
            return stem
    return None


# A word that stands in for the answer's thing rather than naming another one: "i topped it up"
# is the boiler, "i bled them" the radiators. The object of a past tense that is one of these
# says nothing new, so the act alone is enough.
STANDS_IN = frozenset("it them that this one ones those these there".split())


# Where the object of a past-tense verb ends: a preposition opens the rest of the line ("i topped
# it up for the second time"), and a time word or a joining word is not the thing done.
OBJECT_END = frozenset("""for to in on at with by from into onto and but then so because when
    while before after again twice once already yesterday today tonight now later still
    earlier this morning evening week month year""".split())


def _the_object(clean, at):
    """The thing a past tense was done to, as words to find in the answer; None if it says none.

    "i topped up my phone" is the phone and not the boiler, "i bled my knee" is the knee and not
    the radiators, so what follows the verb has to be read or the act alone hands back the next
    step of a job the person never did. A pronoun is not a new thing ("i topped it up"), so it
    says nothing and the act is left to decide.
    """
    tail = []
    for word in str(clean or "")[at:].lower().replace(",", " ").split():
        bare = word.strip(" .;:!?()[]\"")
        if not bare or bare in OBJECT_END:
            break
        if bare in STANDS_IN:
            return None
        tail.append(bare)
    said = frozenset(word for word in tail if len(word) > 2 and word not in topics.STOPWORDS)
    return said or None


def _the_steps_done(text):
    """The steps a line reports having done: the act, and the thing it was done to if it names one."""
    acts = set()
    clean = str(text or "")
    for match in DONE.finditer(clean):
        before = clean[:match.start()].lower().split()[-3:]
        if any(w.strip(" ,.;:!?'") in NO_LONGER_TO_DO for w in before):
            continue  # "i havent cleaned the filter" is the step still to do
        act = _the_act(match.group("verb").lower())
        if act:
            acts.add((act, _the_object(clean, match.end())))
    return acts


def _the_answer_gives(said, act):
    """Whether the answer just given is the one that named the step."""
    for word in str(said or "").lower().replace("'", "").split():
        word = word.strip(" ,.;:!?()[]\"")
        if word == act or act in _the_stems(word):
            return True
    return False


def _a_step_done(text, said):
    """True when the line reports doing a step of the answer just given.

    The step is the answer's, not the word list's: "i changed the washer already" is a step when
    the answer said "take the old part to a hardware shop" and not when the chat is about
    something else. A step named by its object rather than its verb ("i did the hot wash") counts
    too, and only for the empty verb - "do" is not a step any answer says, so the word that has to
    be in the answer is the thing done.
    """
    acts = _the_steps_done(text)
    if not acts or not said:
        return False
    given = _content(said)
    for act, thing in acts:
        # "i did the hot wash" names its step by the thing done - "do" is not a verb any answer
        # uses, so the object is the only way in.
        by_object = act == "do"
        if not by_object and not _the_answer_gives(said, act):
            continue
        if thing is None:
            # A pronoun or no object ("i topped it up", "i bled them"): the answer's thing, by
            # the act alone. A bare "i did it" names nothing, so it is not the step.
            if not by_object:
                return True
            continue
        # The act has to be of the answer's thing as well as in its words: "i topped up my
        # phone" after the boiler answer is not the boiler topped up, and handing back the next
        # boiler step tells the person to stop doing something they never did.
        if thing & given:
            return True
    return False


def _the_step_just_given(text, memory):
    """True when the line reports doing a step of the answer one turn back."""
    for back, _question, said in _recent_answers(memory):
        return back == 1 and _a_step_done(text, said)
    return False


# The words that make a line a rejoinder to the answer above rather than a report of its own: the
# person is defending or adding to what they already do ("i do that too", "i go to bed at the same
# time every night though", "but i already walk the dog").
REJOINDER = re.compile(r"\b(?:though|although|already|but|anyway|still|mind you|to be fair)\b",
                       re.I)


# The same rules for another reader of that turn (bot/memory/more.py): an ask to carry on needs
# the answer the bot just gave, the same guard that the chat has not moved on, and the same
# memory of what has already been handed back. Exposed rather than copied, so the two readers
# cannot drift apart on what counts as an answer or what counts as said twice.
recent_answers = _recent_answers


said_recently = _already_repeated


# A line that names a stall and asks to get going. It is an ask for a step, not a detail of the
# answer just given, so `carried_on` leaves it to the readers that know one: "she is 8 and keeps
# putting it off" after a project answer was handed the sentence about the marking, which is the
# problem already on the screen.
#
# Only a stall about somebody else: "she is 8 and keeps putting it off", "he doesnt know how to
# start". A stall about the person's own plan is a detail of that plan - "how do i boil an egg" /
# "i keep putting it off" wants the cooling step, and "i want to start running" / "i cant get
# started" wants the walk-jog - so a first-person stall keeps the detail reader.
_A_STALL = (r"(?:keeps? putting (?:it |things )?off|puts? (?:it |things )?off"
            r"|putting (?:it |things )?off|keeps? avoiding (?:it|them|this)"
            r"|does not know (?:how|where) to start"
            r"|doesn[\u2019']?t know (?:how|where) to start|not sure (?:how|where) to start"
            r"|can[\u2019']?t get started|cannot get started|has not started|hasn[\u2019']?t started"
            r"|not even started|leaves? it to the last minute|hates? starting)")


ASKING_TO_START = re.compile(
    r"(?:\b(?:he|she|they)\b|\bthe (?:kids?|children)\b"
    r"|\bmy (?:son|daughter|child|kid|boy|girl|mum|mom|dad|father|mother|partner|husband|wife"
    r"|brother|sister|friend|nephew|niece|grandson|granddaughter)\b)"
    r"[^.!?]{0,30}?\b" + _A_STALL + r"\b", re.I)


# A line that asks which part of the answer to do, narrowly: "where do i start", "what should i
# do first", "how do i begin". The wider MOVE_ASK above also catches a plain repeat ("how long
# do i boil them" has the word "do" in it), which wants the answer again, not a step.
# The ask, not the word: "how did we start the fire in the wood burner" is a question about
# something they did, and reading it as "where do i start" handed the step of an unrelated answer
# over. The order that follows is what makes it this ask.
START_ASK = re.compile(r"\b(?:where|how)\s+(?:do|does|should|shall|can|could|would|might|to)\s+"
                       r"(?:(?:i|we|you)\s+)?(?:start|begin)(?:ed|ing)?\b|"
                       r"\bhow do (?:i|we) get (?:started|going)\b|"
                       r"\b(?:do|try|change|fix|sort|put|write|tackle|get)\s+first\b|"
                       r"\bfirst (?:thing|step|move)\b|\bnext step\b", re.I)


# A start/begin that names what it starts is the line's own question, not a lean on the answer in
# hand: "how do i start running" is about running, and the knowledge base has the row for it, but
# read as "where do i start" it was handed the first step of whatever the turn before had said
# (@ochre-mango, #answers). The ask ends at the start, or points back with a pronoun ("start it",
# "start with this") or a word that adds nothing to start ("start again", "start small").
STARTING_WHAT = re.compile(
    r"\b(?:where|how)\s+(?:do|does|should|shall|can|could|would|might|to)\s+"
    r"(?:(?:i|we|you)\s+)?(?:start|begin)(?:ed|ing)?\s+([a-z']+)(?:\s+([a-z']+))?", re.I)


# The words after start/begin that point back at the answer rather than naming a thing to start.
STARTING_BACK = frozenset("""
it this that them these those one again over now today here then though please anyway
small slowly simple easy gently early off out up
""".split())


STARTING_AT = frozenset(("with", "on", "about"))


# "start out" and "start off" name nothing on their own, so the ask reads as the bare one - but
# only when nothing follows them: "how do i start out in gardening" starts out *in gardening*, and
# "how do i start out on my own" in a business. Read as the bare ask, a person trying a few
# hobbies in a row was answered from the answer before it ("start out in running", then "start out
# in gardening" told to jog), and "start out in the morning" was handed the card from the line
# before (@clever-latch, #answers). A preposition after it asks for the word after that one, the
# same way the bare ask looks past "with" and "on"; anything else after it is the thing started.
STARTING_OUT = re.compile(
    r"\b(?:start|begin)(?:ed|ing)?\s+(?:out|off)\s+([a-z']+)(?:\s+([a-z']+))?", re.I)


STARTING_INTO = frozenset(("in", "into", "at", "for", "as"))


def _starting_out_names_a_thing(line):
    """True when what is started out *into* is in the line: "start out in gardening"."""
    found = STARTING_OUT.search(line)
    if found is None:
        return False
    first, second = found.group(1), found.group(2) or ""
    if first in STARTING_INTO or first in STARTING_AT:
        return bool(second) and second not in STARTING_BACK
    return first not in STARTING_BACK


def says_where_to_start(text):
    """START_ASK for a line that asks which part of the answer to do first, and names no starting.

    "Where do i start", "how do i begin with it" and "what should i do first" lean on the answer
    in hand. "How do i start running", "how do i start saving", "how do i start learning guitar"
    and "how do i start out in gardening" name a thing of their own and are answered by the entry
    for it.
    """
    line = str(text or "")
    if not START_ASK.search(line):
        return False
    if _starting_out_names_a_thing(line):
        return False
    found = STARTING_WHAT.search(line)
    if found is None:
        # A start ask leans on the answer in hand only when the line names nothing of its own:
        # "where do i start" and "what should i try first" do, while "my laptop keeps dropping
        # the wifi in the back room, what should i try first" names a laptop and a wifi, and it
        # was handed the first step of the sleep answer given the turn before. A line with a
        # context clause in it is a question about that context, whatever it asks at the end.
        return len(_names_a_thing_of_its_own(line)) < 2
    first, second = found.group(1), found.group(2) or ""
    if first in STARTING_AT:
        return not second or second in STARTING_BACK
    return first in STARTING_BACK


# "what else can i do", "anything else i can try", "and what else": one more thing out of the
# answer just given. A line with a thing of its own in it keeps its own answer, so this is only
# read where the answer is what the line leans on.
MORE_ASK = re.compile(r"\bwhat else (?:can|could|should|would) (?:i|we)\b|"
                      r"\bwhat else (?:is there|works|helped|helps|do i do)\b|"
                      r"\banything else (?:i|we) (?:can|could|should) (?:do|try)\b|"
                      r"\bis there anything else\b|"
                      # "what else could it be" asks for another explanation of the trouble, not
                      # for another thing to do, so the step of the last answer is not the reply.
                      r"\b(?:and )?what else\b(?!\s+(?:could|would|might|is|are|was|were)\s+it\b)",
                      re.I)


# "any ideas", "what do you suggest", "what would you pick", "any other suggestions": the same ask
# as "what else", in the words people use when they want an option rather than another thing to do.
# They name nothing of their own, so no entry can answer them, and until this reading they fell to
# the plain hedge ("That's most of what I know on it", "A search should sort you out quickly") a
# turn after the subject had been answered in full - the aimless turn a friend never gives.
# The whole line has to be the ask: "any ideas for a day out with the kids" names a subject of its
# own, and the entries for it answer from its own words.
IDEAS_ASK = (r"anything (?:else|more|other)|"
             r"(?:any|some) (?:other |more |different )?"
             r"(?:ideas?|suggestions?|thoughts?|recommendations?|options?|tips?)|"
             r"what (?:do|would|can|should) you (?:suggest|recommend|pick|choose|go for|advise)|"
             r"what would you (?:pick|choose|go for|do)|"
             r"your (?:ideas|suggestions|thoughts|recommendations)|"
             r"ideas|suggestions")


IDEAS_ONLY = re.compile(
    r"^\W*(?:(?:and|so|ok|okay|right|well|alright|then|but)\b[\s,]+)*(?:" + IDEAS_ASK + r")" +
    r"\W*(?:[\s,]+(?:then|please|now|tho|though|thanks|ta))?\W*$", re.I)


def a_more_ask(text):
    """Whether the line asks for the next part of the answer in hand, said either way."""
    said = str(text or "")
    return bool(MORE_ASK.search(said) or IDEAS_ONLY.match(said))


# The same ask written with the doing in it: "how do i clean it off", "how do i get rid of the
# smell", "how do i fix it". The pronoun is what makes it the answer's own business; a line that
# names a thing of its own ("how do i clean a cast iron pan") has its own entry and its own answer.
# "how do i word it", "how do i say no", "how do i explain it": a line about the saying, not
# about the doing. The step of the last answer is not the answer to it - there is a module that
# puts the words together - so the move steps aside and leaves the turn to it.
# "Bring it up", "raise it", "mention it" are the same ask: they name no words and no doing, so
# they are listed beside the verbs that say the saying outright. Only a pointed-back object counts
# ("raise the money" is a doing), which keeps the reading narrow.
WORDING = re.compile(r"\bhow (?:do|can|should|could|would|might) (?:i|we)\s+(?:"
                     r"(?:word|write|say|phrase|put|explain|draft|reply|tell|ask|answer)\b"
                     r"|(?:bring|raise|mention|broach|approach)\s+"
                     r"(?:it|that|this|them|the (?:subject|issue|matter|problem))\b"
                     r")", re.I)


HOW_IT = re.compile(r"\bhow (?:do|can|should|could|would|might|shall) (?:i|we)\s+"
                    r"(?:[a-z']+\s+){0,3}(?:it|that|this|them|these|those)\b", re.I)


def _places_to_cut(head):
    """Where a long instruction could end: at a qualifier, or at a bracket that explains it.

    A qualifier that is the last word leaves nothing to cut, and one that is followed by a
    preposition ("put a bowl under it and turn the water off at the stopcock") is the second half
    of the phrase rather than its end, so both are passed over.
    """
    spots = []
    for found in QUALIFIER.finditer(head):
        after = head[found.end():].strip().split()
        if not after:
            continue
        if after[0].lower() in OPENERS:
            continue
        spots.append(found.start())
    for index, char in enumerate(head):
        if char == "(" and ")" in head[index:]:
            spots.append(index)
    return sorted(set(spots))


def _inside_a_bracket(text, at):
    """Whether the character at `at` sits inside a bracket that has not closed by then."""
    return text.count("(", 0, at) > text.count(")", 0, at)


# A list item that is a fact about the world rather than a thing to do is not a step: "the rent is
# due on friday" says how things are, and "same wake-up time every day" says what to do.
# What the words before a colon say the list is: a list of things that work or things to do is the
# answer's instructions, a list of things to learn or of objects is not.
LIST_LEAD = re.compile(r"\b(?:works?|working|helps?|helped|things to do|to do|steps?|rules?|"
                       r"habits?|ways?|tips?|start|begin|try|keep|stick to|do these|do this)\b",
                       re.I)


# A lead that says what the tail is rather than how to do it announces a list of things, and a
# list of things is not the method: "learn four things and the rest follows: pasta with a sauce,
# an omelette, a tray of roasted vegetables" names dishes to try, and handing the first of them over
# as the step ("learn four things and the rest follows: pasta with a sauce") answers nothing.
NOT_A_TAIL = re.compile(r"\b(?:things|rest|following|list|these|those|steps|rules|ways|tips|"
                        r"habits|ideas|examples|reasons)\b", re.I)


NOT_A_DOING = re.compile(r"\b(?:you|your|i|we|they|he|she|it|its|their)\b|"
                         r"\b(?:is|are|was|were|has|have|had|means|meant)\b", re.I)


# A tail that opens on one of these is the questions themselves: "ask the ward three things
# today: who is in charge of their care, what the plan is, and what has to happen next".
A_QUESTION = re.compile(r"^\s*(?:who|what|which|when|where|why|how|whether)\b", re.I)


# A word that is both a verb and a noun of the thing ("pay", "work", "change", "test", "start")
# opens an instruction ("Pay by card at the till") and a statement ("Pay is at least the apprentice
# minimum wage"), and only the sentence says which. A finite verb straight after it makes the
# sentence a statement about the thing, and a statement is not a step to hand back: an
# apprenticeship definition handed its "Pay is at least the apprentice minimum wage and more on
# most schemes" over as the first thing to do (@blue-hedgehog, @sky-tuna, #6152).
DECLARATIVE = re.compile(r"^(?:[a-z']+\s+)(?:is|are|was|were|has|have|had|can|cannot|will|would|"
                         r"should|takes?|gives?|means?|costs?|comes?|goes?|does|did|gets?|keeps?)\b",
                         re.I)


# The sentences that ask rather than tell: an interrogative never opens a step ("do the theory
# test early" is one and starts with a verb, so verbs stay out of this), and "tell me what you
# last enjoyed" is the bot asking a question with the question mark left off.
QUESTIONS_THAT_ARE_NOT_STEPS = re.compile(
    r"^(?:what|which|how|when|where|who|why|tell me|let me know)\b", re.I)


# "what is a mortgage", "what does a mortgage mean", "whats a mortgage": the line asks what the
# thing is, not what to do about it, so the answer it gets is a definition. A definition has no
# work in it at all - which is why a how-to question after one can only be a new question about
# the same subject, never the answer said again under a lead.
WHAT_IT_IS = re.compile(r"^\s*(?:what(?:'s|s| is| are| does| do| did)\b|"
                        r"tell me (?:about|what)\b|define\b|meaning of\b)", re.I)


# A line that says the person has already had a go: the move must not be the thing they had a go
# at. "tried" is here as well as in `tried`'s own patterns because those read the bare "i tried
# that", and the line that matters names what it tried.
ATTEMPT = re.compile(r"\b(?:tried|trying|already|gave it|had a go|no luck|used)\b", re.I)


# The figures a follow-up can ask for, and the figure in the answer that answers each one. The
# words are the ask itself; the second pattern is what the answer has to contain for that ask to
# be answered from it.
FIGURE_ASKS = (
    ("time", re.compile(
        r"\bhow\s+(?:long|soon|quick(?:ly)?|longer)\b"
        r"|\bhow\s+many\s+(?:seconds?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?|nights?)\b"
        r"|\bwhat\s+(?:time|timing)\b", re.I),
     re.compile(
        r"\b(?:\d+(?:\.\d+)?|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
        r"fifteen|twenty|thirty|forty|forty-five|fifty|sixty|ninety)\s*(?:\w+\s+to\s+)?"
        r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|wks?|months?|years?|nights?)\b",
        re.I)),
    ("heat", re.compile(r"\bhow\s+(?:hot|warm)\b|\bwhat\s+(?:temperature|heat|gas\s+mark)\b", re.I),
     re.compile(r"\b(?:\d{2,3}\s*(?:°|degrees?|c\b|celsius|f\b|fahrenheit)|gas\s+mark\s+\d|"
                r"mark\s+\d\b)", re.I)),
    ("amount", re.compile(r"\bhow\s+(?:much|many)\b", re.I),
     re.compile(r"(?:£\s?\d|\b\d+\s*(?:g|kg|grams?|ml|l|litres?|pints?|cups?|tbsp|tsp|oz|ounces?)\b)",
                re.I)),
    ("often", re.compile(r"\bhow\s+often\b|\bhow\s+many\s+times\b", re.I),
     re.compile(r"\b(?:once|twice|three\s+times|\d+\s+times)\b[^.?!]{0,25}"
                r"\b(?:a|per|every)\s+(?:day|week|month|year|night)\b", re.I)),
)


# The words a line that asks for a figure and nothing else is made of: the ask, the pronoun that
# points at the thing already on the screen, and the verb the figure belongs to. A line that names
# anything more ("how long should i cook the rice", "how much do i need for the deposit") has an
# answer of its own and is left to it.
FIGURE_WORDS = frozenset("""
    how long soon quickly quick longer much many often hot warm what time timing temperature heat
    gas mark should shall can could would will may might must do does did is are was were am
    i we you they he she it its that this these those them there and so ok okay but then again
    also just really leave left need use take cook bake keep wait soak boil simmer rest run
    sit stand stay lie hang dry cool warm heat set settle marinate marinade prove rise chill
    exercise give put apply wear change replace before after for in on at to it too much
    before afterwards after that
""".split())


# A verb of saying something does not name the thing that would have an answer of its own:
# "how long do i wait before asking", "how long should i wait before telling her" and "how long
# before i say something" all ask for the wait in the answer just given. The word the question
# ends on used to stand in the way - "asking" was read as a thing of its own - so the sentence
# with the figure in it was never handed back. A line that does name the thing ("before asking
# for a refund", "before telling my boss") keeps its own answer, because that word is not here.
FIGURE_SAYING = frozenset("""
    ask asking say saying tell telling mention mentioning bring bringing raise raising
    broach broaching approach approaching him her them
""".split())


# Not every follow-up asks for a figure. "is the food still ok" after a card on a freezer door,
# "do i need to prick them" after one on jacket potatoes, "where do i start" after one on sorting
# out money: each names the thing in a word the card itself never has to use ("food", "them"),
# and each reached the search hedge, which tells a person to go and look up the thing the bot has
# just told them about. What the card has is a sentence of the kind asked for, and none of these
# asks needs a figure for it to be handed back.
STILL_SAFE = re.compile(
    r"\bstill\s+(?:ok|okay|good|fine|safe|edible|alright)\b|\bis\s+(?:it|that|this)\s+"
    r"(?:safe|alright|fine|ok|okay|good)\b|\bcan\s+i\s+still\b|\bsafe\s+(?:to|for)\b",
    re.I)


SAID_SAFE = re.compile(
    r"\b(?:safe|fine|okay|ok|keep|keeps|kept|bin|binned|binning|throw|thrown|eat|eaten|edible|"
    r"cooked|refreeze|put\s+back|nothing\s+needs|no\s+need)\b", re.I)


DO_I_NEED_TO = re.compile(
    r"\bdo\s+i\s+(?:need|have)\s+to\b|\bhave\s+i\s+got\s+to\b|\bshould\s+i\b|"
    r"\bam\s+i\s+meant\s+to\b|\bdo\s+you\s+have\s+to\b", re.I)


A_MOVE = re.compile(
    r"\b(?:prick|cut|turn|stir|cover|leave|put|add|check|wash|rinse|soak|rest|shake|score|"
    r"season|test|wait|ask|keep|write|print|sign|ring|call|book|take|use|give|hold|open|close|"
    r"run|cook|bake|boil|simmer|freeze|defrost|empty|clean|wipe|change|replace)\b", re.I)


WHERE_TO_START = re.compile(
    r"\bwhere\s+(?:do|should|would|can|shall)\s+i\s+(?:really\s+|even\s+)?(?:start|begin)\b"
    r"|\bwhere\s+to\s+start\b|\bwhat\s+(?:do|should)\s+i\s+(?:do|try)\s+first\b"
    r"|\bhow\s+do\s+i\s+(?:start|begin|get\s+going)\b|\bwhere\s+do\s+i\s+(?:go|look)\b",
    re.I)


# The kinds of sentence a card can hand back when no figure is asked for: the ask, and the mark
# that says the card has the sentence. `None` means the card's own opening, which is the first
# step of what it tells the person to do.
PART_ASKS = (
    # "When does it wear off" and "how long does it last" are the same ask about the same figure,
    # and so is "when will the numbness go": the card in hand usually states it outright ("wears
    # off after an hour to three hours", "keeps 24 hours in the fridge"), so all of them are read
    # here rather than only the first shape. "How long" is the commonest way of asking it and was
    # missing, which left "how long does the numbness last" with the search hedge.
    ("time", re.compile(r"\bwhen\s+(?:does|do|will|would|should|can|is|are)\b|"
                        r"\bhow\s+(?:soon|long)\b|\bhow\s+(?:much\s+)?longer\b", re.I), FIGURE_ASKS[0][2]),
    ("start", WHERE_TO_START, None),
    ("safe", STILL_SAFE, SAID_SAFE),
    ("move", DO_I_NEED_TO, A_MOVE),
)


# The words that stand in for the thing the chat is on rather than naming a new one. "Is the food
# still ok" after a card about a freezer door names the topic of the card in a general word, and
# the card is free to answer it. A word that names a thing the card does not have ("manchester",
# in "how long does it take to get to manchester" after a card on marinades) is not one of these,
# and a card that never says it cannot answer for it.
PART_STAND_INS = frozenset("""
    food foods stuff thing things bit bits part parts piece pieces kit gear item items
    water drink milk meat rest lot lots everything anything something nothing else
    job work house home place places one plant plants garden washing clothes
""".split())


# A sentence that only follows another one is not a reply: "Then put the phone down and let the
# answer come or not." was handed back to "should i ask her", where it reads as an instruction to
# stop asking. A part of a card has to stand up on its own.
NOT_ALONE = re.compile(r"^(?:then|after that|afterwards?|next|also|and|but|or|so|instead|"
                       r"either|once|while|because|which|that|this|it|they|them|he|she)\b", re.I)


PART_OPENS = frozenset("""
    then afterwards next also and but or so instead either once while because which
""".split())


# The ask whose gap this reading can name: a yes/no about doing a step - "do i need to prick
# them", "should i prick the shell", "am i meant to score the fat". The rest of the line becomes
# "whether to ..." and reads as the one thing the card in hand never said.
A_MOVE_WORDS = frozenset("""
    prick cut score slash stab turn stir cover uncover leave put add check wash rinse soak scrub use try
    rest shake season salt test taste wait keep freeze defrost empty clean wipe change replace
    trim peel chop slice mix whisk knead roll fill drain squeeze press
    bleed flush prime seal grease oil sand paint varnish glue screw tighten loosen unplug plug
    switch reset restart reboot charge update install download back defrost refrigerate reheat
    tin jar bottle label marinate brine gut bone stuff ice chill cool warm heat preheat blind
    line flour dust glaze baste carve prove rise fold beat cream sieve sift blend mash grate zest
    juice deseed core hull soak de-ice descale unblock plunge rod hoover vacuum mop dust sweep
    water feed prune repot stake tie mulch mow scarify aerate
""".split())


WHETHER_ASKS = (
    re.compile(r"\b(?:do|did)\s+i\s+(?:need|have|got)\s+(?:to\s+)?(?P<rest>[^?!]+)", re.I),
    re.compile(r"\bshould\s+i\s+(?:be\s+|just\s+|still\s+)?(?P<rest>[^?!]+)", re.I),
    re.compile(r"\bam\s+i\s+(?:meant|supposed)\s+(?:to\s+)?(?P<rest>[^?!]+)", re.I),
    # Permission, which is the same question about the same step: "can i just use bleach" after
    # the card on moths, "is it ok to put it in the wash" after the card on a stain. The card
    # never says yes or no, so what comes back is the card's own sentence and the one place that
    # settles it - never an invented yes.
    re.compile(r"\bcan\s+i\s+(?:just|still|safely|even)?\s*(?P<rest>[^?!]+)", re.I),
    re.compile(r"\bis\s+it\s+(?:ok|okay|safe|alright|fine)\s+to\s+(?P<rest>[^?!]+)", re.I),
)


# A yes/no about a method rather than a step of the card's own: "will beer traps do anything"
# after the card on slugs, "does vinegar work on weeds", "would a dehumidifier help", "is a fan
# enough". The card never covered that method, and the reply used to be "I'm not sure about that
# one - a quick search online will get you a solid answer", which throws away the card still on
# the screen. What the card does cover comes back, and only then the one place with the rest.
METHOD_ASKS = (
    re.compile(r"\b(?:will|would|does|do|did|is|are|can|could)\s+(?P<rest>[^?!]{3,40}?)\s+"
               r"(?:work|works|help|helps|do\s+anything|do\s+it|do\s+the\s+job|"
               r"(?:be\s+)?enough|(?:be\s+)?any\s+good|be\s+ok\b|be\s+okay|"
               r"be\s+worth\s+(?:it|doing))\b[^?!]*", re.I),
)


# The words that name no method at all: "will it work", "would that help". A pronoun leans on
# something the bot cannot see, and the card in hand may already be that something.
NOT_A_METHOD = frozenset("""
    it that this they those these there he she i we you one ones
""".split())


# Words that say how well something works rather than what is being asked about. "does a harness
# work better" asks about the harness, and a card that says "A front-clip harness or head halter
# helps while he learns" answers it; the "work better" is the frame of the question. Left in, they
# made every such ask a gap the card had to fill word for word, and the card in hand was passed
# over for a place that knows nothing of it.
A_QUALITY = frozenset("""
    work works worked working better best help helps helped worth enough good fine okay ok
    safe still anymore actually really even than
""".split())


# A yes/no about still being able to do something with the thing in hand. Unlike the two families
# above, there is no step named ("the ones", "them"), so the clause itself is what the card is
# asked about.
STILL_ASKS = re.compile(
    r"^(?:(?:and|but|so|or)\s+)?"
    r"(?P<aux>can|could|may|should|would)\s+(?P<who>i|we)\s+still\s+(?P<rest>[a-z].*)$", re.I)


# The frame words of a reply, not its subject. "Count the sleep first" and "Say the one thing that
# matters first, then the rest" share "first" and nothing else, and on that one word the card about
# a child's sleep counted as still on a chat about putting a shift change in writing.
NOT_A_SUBJECT = frozenset("""
    first thing things one ones rest bit part way ways sort kind lot next still even actually
    really everything anything something nothing else another
""".split())


# The figures a person gives about their own life, asked back late in the chat. "i need 20 grand"
# on the second turn and "what was my deposit target again" eight turns later reached the
# knowledge machinery, which looks for an entry keyed on "deposit target", found none, and
# answered with the search hedge - while the figure was in the chat the whole time. The same
# with "and how many people" after "a roast on sunday for 8 people", "how long have i got until
# the move" after "we're moving house in 6 weeks", and "and how many bedrooms" after "its a 3 bed
# with a garden".
#
# `the_figure_asked` above answers an ask that names nothing at all, out of the bot's last answer.
# This is its other half: the ask names the thing the figure is for, and the figure is one the
# person gave themselves a few turns up. The shape is narrow, so a question about the world is
# never answered with a number out of the chat:
#   * the line has to ask for the figure back ("what was my ... again", "what did i say ...",
#     "how many/long/much ...") and be short;
#   * it has to name the thing the figure is for, and at least half of what it names has to be in
#     a line the person said - so "how many people live in london" does not take the eight from
#     the dinner, which is the one word it shares with it;
#   * the figure has to sit in that line or the two lines after it, so a number given for
#     something else in the same chat is not handed over;
#   * where the ask says which kind of figure it wants ("how many" against "how long"), only that
#     kind comes back, and a line with two different kinds on it hands nothing back at all.
GAVE_ASKS = re.compile(
    r"\bwhat(?:'s|s|\s+(?:was|were|is|are))\s+(?:my|our|the)\b"  # what was / what's my target
    r"|\bwhat\s+did\s+(?:i|we)\s+(?:say|tell)\b"            # what did i say i need
    r"|\bhow\s+(?:long|much|many|often|soon)\b"             # and how many people
    r"|\bwhat\s+was\s+it\s+(?:i|we)\b"                      # what was it i wanted
    # Pay asked for without "how much" in it: "what do i earn", "whats my wage". The word for the
    # pay is in the ask, so a figure given for something else in the chat is not its answer.
    # A word about when may stand between "my" and the pay: "whats my current salary" is the same
    # ask as "whats my salary", and it named nothing at all because the pay word was not the next
    # one. Not "monthly" or "gross": those name a different figure from the one they gave.
    r"|\bwhat(?:'s|s|\s+is|\s+are|\s+do|\s+does|\s+did)\s+(?:i|we|my|our)\s+"
    r"(?:(?:current|exact|actual)\s+)?"
    r"(?:earn|earns|earning|make|makes|paid|pay|pays|wage|wages|salary|salaries|income)\b", re.I)


# The words that only frame the ask, so they never count as the thing the figure is for. It is
# FIGURE_WORDS plus the ones this shape is built from - the remembering, the pointing back, and
# the words that hold an ask together.
ASK_FRAME = FIGURE_WORDS | frozenset("""
    said say says saying tell told telling mention mentioned remember remembers remember forgot
    recall earlier before after since again exactly actually probably guess think know my our
    the a an i we you it its thing things one ones number figure what whats which was were is are did
    do does have has had got left until till by about story now been
""".split())


# One figure, said the way people say it: money with its sign or its word, a length of time with
# its unit, and a count with the thing counted ("8 people", "3 bed", "40 boxes"). The count is
# last, so "20 grand" is money and "6 weeks" is a length of time before either is read as a count.
A_FIGURE = re.compile(
    r"(?P<money>£\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:k|grand|thousand|m)\b)?"
    r"|\b(?<![\d.])\d[\d,]*(?:\.\d+)?\s?(?:grand|k|quid|pounds?|dollars?|euros?|bucks)\b)"
    r"|(?P<time>\b(?<![\d.])\d[\d,]*(?:\.\d+)?\s*"
    r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|wks?|months?|years?|nights?)\b"
    r"|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+"
    r"(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?|nights?)\b"
    # "ive had it for a week", "about a month now", "a couple of days": people give a length
    # with an article far more often than with a number word, and "for a week now" was not a
    # figure at all, so a later "how long have i had it" found nothing to give back.
    r"|\b(?:about\s+|around\s+|nearly\s+|over\s+|under\s+)?(?:a|an)\s+"
    r"(?:second|minute|hour|day|week|month|year|night)\b"
    r"|\b(?:a\s+)?(?:couple\s+of|few|couple)\s+"
    r"(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?|nights?)\b"
    r"|\bhalf\s+an?\s+(?:hour|day|week|month)\b)"
    # A share is a figure of its own, read whole: "the deposit is 10 per cent of 180 thousand" was
    # read as the count "10 per" and "what was the deposit again" answered "You said 10 per.",
    # with the rest of their words dropped. "20 percent" was already one figure; "20%" was none.
    r"|(?P<share>\b(?<![\d.])\d[\d,]*(?:\.\d+)?\s?(?:%|per\s?cent\b|percent\b))"
    r"|(?P<count>\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"(?<![\d.])\d[\d,]*(?:\.\d+)?)\s+[a-z][a-z-]{2,}\b)"
    # a bare figure is an amount when the ask asks how much: "i also owe 2000 on a credit card"
    r"|(?P<amount>\b(?<![\d.])\d[\d,]{2,}\b)", re.I)


# The nouns that name the kind of figure rather than the thing it is for. "what was my deposit
# target again" is looked up by "deposit", not by "target": the ask says what it wants back, and
# the word for that is in the ask and in no line the person said.
# What a person is paid, said any of the ways there are. The figure is the same money whichever
# word is used for it, and only the word changed between the two lines: "i get paid 2000 a month"
# then "how much do i earn" got the search hedge, while "i earn 2000 a month" answered "You said
# 2000", and "my salary is 30000 a year" then "how much do i earn" the same. The words are stems,
# because "wages" and "earning" arrive with their endings on.
PAY_FAMILY = frozenset("""earn earning earned pay paid pays payslip wage salary income make making
made takehome""".split())


# A word that names pay, whether as the thing asked about or as the verb in the ask: "how much do
# i make" names the pay as plainly as "how much do i earn" and arrived naming nothing at all,
# because "make" is a stopword the keywords drop.
A_PAY_WORD = re.compile(
    r"\b(?:earn|earns|earning|earnings|pay|pays|paid|wage|wages|salary|salaries|income|"
    r"make|makes|making|made)\b", re.I)


# Pay asked for as a bare verb at the end of the ask: "how much do i make" wants the figure, and
# "what do i make of this" does not, so only the ask that stops there is read as an ask about pay.
A_PAY_VERB_AT_THE_END = re.compile(r"\b(?:make|makes|earn|earns|paid|pay)\s*[.?!]*\s*$", re.I)


# Pay asked about for a view rather than for the figure: "whats my pay like", "is my wage fair".
# The figure is theirs and it is true, and it is still not what they asked.
# Pay said as two words no keyword joins: "i take home 1800 a month" is the wage, and the store
# read "take home" as the shops - "how much do i earn" after it got the duty-free card.
A_TAKE_HOME = re.compile(r"\btak(?:e|es|en|ing)\s+home\b", re.I)


# "im on 2000 a month" is a wage said with no word of the family in it, like "take home".
A_IM_ON_A_FIGURE = re.compile(
    r"\b(?:i'?m|i am|we'?re|we are)\s+on\s+(?:about\s+|roughly\s+|around\s+)?"
    r"[\u00a3$£]?\s*\d", re.I)


A_PAY_JUDGEMENT = re.compile(
    r"\b(?:like|worth|enough|fair|reasonable|normal|average|typical|good|bad|ok|okay|"
    r"competitive)\b", re.I)


# A word about when, not about what: "whats my current salary" and "how much do i earn currently"
# add nothing the wage did not say, and they arrived naming a word in no line, so the pay ask was
# refused as a qualifier it is not. Only the pay asks drop these, because a qualifier anywhere else
# can be the whole question.
PAY_WHEN_WORDS = frozenset("""current currently presently now moment latest today exact exactly
    actual precisely roughly""".split())


# What kind of figure an ask wants, not which one: a length of time, and the words that point at
# their own trip with it. "days" in an ask is the unit the answer will be in, never the thing the
# figure was given for, so a bare one of these is not a thing for the ask to have named.
A_MEASURE_WORD = frozenset("""
    day days night nights week weeks weekend weekends month months year years hour hours minute
    minutes morning mornings afternoon afternoons evening evenings time times while""".split())


A_DOING_WORD = frozenset("""going away off there gone staying travelled traveled travelling
    traveling returning back doing""".split())


FIGURE_NOUNS = frozenset("""target amount total figure count number budget price cost age date
    sum score""".split())


# The words that name a goal and nothing else. An ask whose only content word is one of these
# names no thing for the figure, so the thing is the goal they set: "what was my target again"
# after "i'm trying to save 8000 for a van" is the 8000. The figure is read from the line that
# states the goal, not from a rate they put by, which is how they get there and not the target.
GOAL_NOUNS = frozenset("target goal aim objective ambition".split())


A_GOAL_LINE = re.compile(
    r"\b(?:save|saving|saved|need|needs|needed|want|wants|wanted|aim|aiming|goal|target|"
    r"objective|ambition|trying|try|plan|planning|afford)\b", re.I)


# A rate is how they reach the goal, not the goal: "i can put by 250 a month" is not the target
# when the line before it said "i'm trying to save 8000 for a van".
A_RATE_LINE = re.compile(
    r"\b\d[\d,.]*\s*(?:a|an|per|each|every)\s+"
    r"(?:day|week|month|year|fortnight)\b"
    r"|\b(?:a|per|each|every)\s+(?:day|week|month|year|fortnight)\b", re.I)


# A line that asks is not a figure given: "how many roast potatoes do i need for 8" has an eight
# in it, and it is the number they are waiting for, not one they gave.
A_QUESTION = re.compile(
    r"\W*(?:how|what|which|when|where|who|why|do|did|does|can|could|should|would|will|shall|"
    r"is|are|was|were|have|has)\b", re.I)
