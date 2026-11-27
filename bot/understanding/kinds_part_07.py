"""Part 7 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from .normalize import background_clause, background_positions, strip_leaders
from .kinds_part_01 import (
    POLITE, ACK, AFFIRM, DENY, FAREWELLS, GREETINGS, LAUGH, NEGATIVE, OPINION, POSITIVE,
    QUESTION_WORDS, STEPS, THANKS, YESNO_STARTS, _asks_a_verdict, _asks_for_help, _limit_of,
    _ruled_out_of,
)
from .kinds_part_02 import (
    SPEAKER, CORRECTION, EVENT_WORDS, NEWS, _a_broken_heart_is_theirs, _a_hedged_low,
    _acts_on_the_speaker, _has_any, _somebody_elses_heart, agreement_of, small_talk_only,
)
from .kinds_part_03 import (
    _state_owner, shortage_of,
)
from .kinds_part_04 import (
    _counts_its_own_doings, _ends_with_thanks, _says_the_help_was_good, _starts_with, _thanks_only,
    farewell_only, greeting_only, without_filler,
)
from .kinds_part_05 import (
    _about_bot_kind, _agrees_to_try, _asks_about_the_bot_day, _asks_after_any, _asks_for_tips,
    _asks_it_back, _asks_the_bot, _asks_what_the_bot_is_doing, _hands_a_question_to_the_speaker,
    _short_reply, asks_how_i_am, the_manners_question,
)
from .kinds_part_06 import (
    _about_bot, _asks, _asks_back, _asks_for_confirmation, _asks_what_was_meant,
    _continues_the_sentence, _opens_question, _polarity, _thanks_still_asks, denied, emotion_of,
    says_how_they_are, summons_of,
)


# A line that only picks something out and leaves the subject to the turn before it: "the best
# time to visit", "any good places to eat", "and the cheapest way to get there". Every one of
# them is a question with its "what is" left off, and read as a statement it named nothing to
# answer and got a search hedge.
PICKING = frozenset("""best better cheapest cheaper good great nice decent place places way ways
    time times thing things option options spot spots area areas""".split())


# A "to" and a verb after it: what makes the frame an ask ("to visit", "to eat", "to get").
TO_A_VERB = re.compile(r"\bto\s+[a-z]+", re.I)


# The words that make a line say something about a subject rather than ask about one.
SAYS_WHAT_IT_IS = frozenset("""is are was were am im i'm its it's be been""".split())


# A frame with its subject left out opens on the frame itself, not on a person or a thing of the
# line's own: "the best...", "a good...", "any good...", and the "and" that introduces a follow-up.
OPENS_A_FRAME = frozenset("""the a an any some and also best better cheapest cheaper good great
    nice decent""".split())


# The words that pick one thing out of many and ask for it, whether or not the line found an
# ask word of its own: "a good place to eat", "the cheapest one to get".
PICKING_QUALITY = frozenset("best better cheapest cheaper good great nice decent".split())


def _only_the_ask(norm, asks, text):
    """True when the line is nothing but a frame asking after something the last turn named.

    "the best time to visit" is not a statement about the best time: it is the question "what
    is the best time to visit?" with the subject left out, which is how people follow up. The
    line names nobody ("i"/"we" makes it a statement about what they want), says nothing about
    a subject ("is"/"was"), and is a short frame - a thing word, a quality or an ask, and "to
    <verb>". A frame that picks one thing out is asking for a recommendation even when the ask
    words missed it: "a good place to eat" asks for one as plainly as "the best way to eat".
    """
    words = [word for word in norm if word not in POLITE]
    if not words or len(words) > 8:
        return False
    if set(words) & (SPEAKER | SAYS_WHAT_IT_IS):
        return False
    if words[0] not in OPENS_A_FRAME:
        return False  # "my mum has a good recipe to follow" is about the recipe
    if not set(words) & PICKING or not TO_A_VERB.search(str(text)):
        return False
    return bool(asks) or bool(set(words) & PICKING_QUALITY)


def classify(line):
    text = line["norm_text"]
    norm = line["norm"]
    words = set(norm)
    signals = line["signals"]

    clauses = line["clauses"]
    opens_like_question = any(_opens_question(clause) and not _continues_the_sentence(clauses, at)
                              for at, clause in enumerate(clauses))
    asks = _asks(norm, " " + text + " ")
    turned_back = _asks_it_back(norm) or _asks_about_the_bot_day(norm)
    tag = _asks_for_confirmation(norm)

    # A question is what needs answering, even when it comes after a "hi" or a "thanks":
    # "Thanks! Which one should we start with?" is a question, "Thanks, that helped" is not.
    # The ask can be later in the line and still be the point of it: "thanks, one more thing -
    # how do i clean the oven" is a question about the oven, and read as a thank you it got the
    # reply for the thanks and no oven at all. What must not count is a thanks that only
    # comments, and a comment carries an asking word of its own: "thanks, that explains the
    # boiler" finds the definition ask on "explains", and "thanks for the advice" the tips ask
    # on "advice" - neither asks the bot for anything, and read as a question the advice line
    # was sent looking for an answer to a line that thanks the bot for the last one. So an ask
    # is not enough on its own: the line has to be shaped like a question too, with a question
    # mark, a question word, or an ask frame ("thanks, any tips for a cold").
    kind = "statement"
    courtesy = without_filler(norm)
    if not norm:
        kind = "empty"
    elif (signals["question_mark"] or _opens_question(norm) or opens_like_question
          or _asks_the_bot(norm) or _asks_for_help(text) or tag or _asks_after_any(norm)
          or (asks and _starts_with(norm, THANKS)
              and (signals["question_mark"] or set(norm) & QUESTION_WORDS
                   or _thanks_still_asks(norm)))):
        kind = "question"
    elif _only_the_ask(norm, asks, text):
        # A frame asking after the subject the last turn named is a question, not a statement:
        # "whats the capital of australia" then "and the best time to visit" was read as a
        # statement about nothing, so the subject was never put back and the line got a hedge.
        # A frame that picks one thing out asks for a recommendation, and its reading says so.
        kind = "question"
        asks = sorted(set(asks) | {"recommend"})
    elif _starts_with(norm, GREETINGS) and greeting_only(norm):
        kind = "greeting"
    elif ((_starts_with(courtesy, THANKS) and _thanks_only(courtesy, clauses))
          or _says_the_help_was_good(norm)):
        kind = "thanks"
    elif _ends_with_thanks(courtesy):
        kind = "thanks"

    if turned_back:
        asks = []
    if kind != "question":
        # A question word inside the clause that says when or where is not an ask: "it started
        # this morning when i was in the garden" asks nothing, so `when` is background too.
        behind = {norm[index] for index in background_clause(norm) | background_positions(norm)}
        asks = [ask for ask in asks if ask not in behind]
    if kind == "question" and (
            (not turned_back
             and any(strip_leaders(clause)[:1] and strip_leaders(clause)[0] in YESNO_STARTS
                     for clause in line["clauses"]))
            or tag):
        asks = sorted(set(asks) | {"yesno"})
    short = len(norm) <= 3
    bare = [word for word in norm if word not in POLITE]
    # A bad feeling the line rules out is not the bad feeling: "im not stressed" is the person
    # narrowing the cause, and "im not in pain" is not pain. The good words stay as they are,
    # because a good one that is ruled out is the bad feeling ("im not happy", "not feeling
    # great"), and `_polarity` already turns it the other way.
    denied_bad = {word for word in words if word in NEGATIVE and denied(text, word)}

    intent = "statement"
    if kind == "empty":
        intent = "empty"
    elif signals["laughter"] and len(norm) <= 5:
        intent = "laugh"
    elif _starts_with(strip_leaders(norm), FAREWELLS) and farewell_only(strip_leaders(norm)):
        # The goodbye is read before the reading that looks for "you": "see you later" and
        # "ttyl" (which the lexicon writes out as "talk to you later") are the way out, and
        # "can you talk later" is not, because it does not open with the farewell. The leaders
        # are taken off first, because a goodbye is preceded by one as often as not: "ok bye
        # ttfn", "right then, good night".
        intent = "farewell"
    elif _about_bot(text, words, norm):
        intent = "about_bot"
    elif kind == "greeting":
        intent = "greeting"
    elif kind == "thanks":
        intent = "thanks"
    elif _has_any(" " + text + " ", CORRECTION) and ("meant" in words or "mean" in words):
        intent = "correction"
    elif (_asks_it_back(norm) or _asks_about_the_bot_day(norm)
          or _asks_what_the_bot_is_doing(norm) or the_manners_question(norm)
          or asks_how_i_am(norm)):
        intent = "smalltalk"
    elif agreement_of(text):
        intent = "ack"
    elif _short_reply(text) and len(norm) <= 6:
        intent = "ack"
    elif kind == "statement" and _agrees_to_try(norm):
        intent = "ack"
    elif (norm[0] in {"no", "nah", "nope", "never"} and len(norm) <= 5
          and norm[1:2] != ["one"]):
        intent = "deny"
    elif norm[0] in ACK and len(norm) <= 4:
        intent = "ack"
    elif len(bare) <= 3 and set(bare) <= AFFIRM:
        intent = "affirm"
    elif len(bare) <= 3 and set(bare) <= DENY:
        intent = "deny"
    elif len(bare) <= 3 and (set(bare) <= ACK or set(bare) <= LAUGH):
        intent = "ack"
    elif small_talk_only(norm):
        intent = "smalltalk"
    elif kind == "question":
        intent = "question"
    elif ("recommend" in asks or _asks_for_tips(text, norm) or _has_any(text, STEPS)
          or words & {"help", "need", "want"}):
        intent = "request"
    elif norm[:1] and norm[0] in {"tell", "explain", "show", "give", "write", "make"}:
        intent = "request"
    elif "i" in words and (any(w in NEGATIVE or w in POSITIVE for w in words
                                  if w not in denied_bad)
                            or says_how_they_are(norm)):
        intent = "feeling"
    elif ("i" in words or _acts_on_the_speaker(text)) and emotion_of(text):
        # "im terrified", "im petrified": the emotion reader knows the word even when the plain
        # feeling lists do not, and the speaker is the one who has it, so the same line must not
        # read as news while "im scared" reads as a feeling. A thing that acts on the speaker
        # counts the same way: "work is stressing me out" has no "i" in it, and read as news it
        # was answered with its own words back ("Money is stressing you out - noted.").
        intent = "feeling"
    elif _has_any(" " + text + " ", NEWS):
        intent = "news"
    elif {"i", "me", "my", "we", "our"} & words and (words & EVENT_WORDS or len(norm) <= 12):
        intent = "news"
    elif _has_any(text, OPINION) or (words & {"think"} and kind == "question"):
        intent = "opinion"

    state_owner = _state_owner(line["clauses"])
    limit = _limit_of(text)
    suggestion = _a_suggestion_from_someone(norm, text)
    ruled_out = _ruled_out_of(text)
    emotion = None
    if "i" in words or "im" in words or "my" in words or kind != "question":
        emotion = emotion_of(text)
    if state_owner in (None, "thing") and _somebody_elses_heart(text):
        # Somebody else's broken heart is their trouble: the pool for the person in it stands
        # aside, and the same arm keeps the heartbreak row from answering about the speaker.
        state_owner = "other"
    if emotion and state_owner in (None, "thing") and _a_broken_heart_is_theirs(text):
        # A heart is a part of a person, so `_whose_state` calls it a thing, and a thing's state
        # is not the person's mood (bot/modules/chat.py stands the sad pool down on it). A broken
        # heart is not a body fault either - the health reader has nothing to say about it - it
        # is how the person is, said the long way round, so the owner is the person.
        state_owner = "self"
    if not emotion and _a_hedged_low(line.get("clean") or text):
        # "could be better", "been better", "not so good": a low said politely, with no word of
        # mood in it for the feeling reader to find.
        emotion = "sad"
        if state_owner in (None, "thing"):
            state_owner = "self"
    polarity = _polarity(norm)
    shortage = shortage_of(text)
    if shortage and emotion is None:
        # Nothing in the line names a mood of anybody's - the only state word in it is the one a
        # supply took off ("im low on milk") - so no state is being said of the speaker either.
        state_owner = None

    return {
        "kind": kind,
        "intent": intent,
        "asks": asks,
        # True when the end of the line is a tag asking to be agreed with ("... right",
        # "... innit"), so a module can tell a confirmation from a question about the world.
        "tag": tag,
        "emotion": emotion,
        "state_owner": state_owner,
        # The thing the line says has run out ("im low on milk" is milk, "im out of tea bags" is
        # tea), or None. A shortage is not a mood, and it is not the speaker's state either, so
        # the pools that answer a feeling stand down when this is set.
        "shortage": shortage,
        "polarity": polarity,
        "short": short,
        "first_person": bool(words & {"i", "me", "my", "we", "our", "us", "myself"}),
        "asks_opinion": "opinion" in asks,
        "asks_recommendation": "recommend" in asks,
        "asks_steps": "steps" in asks,
        "help_ask": _asks_for_help(text),
        "asks_a_verdict": _asks_a_verdict(text),
        "about_bot": intent == "about_bot",
        "about_bot_kind": (_about_bot_kind(text, words, norm)
                           if intent == "about_bot" else None),
        # A "how many" asked about the bot's own doings ("how many people have you talked to"):
        # the bot has no tally to give, and the memory answer describes what it remembers rather
        # than saying there is no number, so the composer needs to know which one it is.
        "counts_the_bots_own_day": _counts_its_own_doings(norm),
        "replies_to_bot": intent in ("affirm", "deny", "ack", "laugh"),
        "agrees_to_try": _agrees_to_try(norm),
        "wants_a_quiz": _hands_a_question_to_the_speaker(norm),
        # The idiom of agreement the whole line is ("tell me about it", "you and me both"), or
        # None. It is an ack, and a warmer one than "got it": the person has just agreed with
        # something, so the reply agrees back and asks nothing of them.
        "agreement": agreement_of(text),
        # Someone who can call them in wanting a word (see SUMMONS_WHO above): the shape the
        # reply needs, because "not knowing what it is about is the worst bit" is an answer to
        # a letter or a meeting and not to a question about one.
        "summons": summons_of(norm, kind),
        # The line answers how the person is and hands the question back in the same breath
        # ("not bad, and you?", "im fine thanks, yourself"): a reply that only answers the
        # person answers half of it. See `_asks_back`.
        "asks_back": _asks_back(norm),
        # True when the whole line asks what the bot's own last answer meant ("what do you
        # mean", "what does that mean", "wot u mean", "wdym"): it names nothing of its own, so
        # no knowledge entry is its answer and the store says the last answer again. See
        # `_asks_what_was_meant`.
        "asks_what_was_meant": _asks_what_was_meant(text),
        # The thing a line that only rules something out takes away ("no horror", "no treats",
        # "without the garlic"), as a list, plus the flag the composer reads. A line that says
        # more than a limit is not one, so "no horror but the last one was good" stays its own.
        "excludes": [limit] if limit else [],
        # The things the line says it does not mean, so a reader answering it can skip their
        # words: "for a holiday not a house" is a question about a holiday.
        "ruled_out": ruled_out,
        "constraint": limit is not None,
        # Advice somebody else gave the person ("my mate said i should try it", "the doctor told
        # me to rest") as {"who", "source"}, or None. The doing in it is still to come, so a
        # reply that asks how it went is about a day that has not happened: the composer answers
        # the plan instead. See A_REPORTED_VERB.
        "suggestion": suggestion,
    }


# What a person does on a set day, or keeps doing: "every day", "twice a week", "most days",
# "on a tuesday". ("on tuesday" is one Tuesday; only the article makes it a habit.)
ROUTINE_SHAPE = re.compile(
    r"\b(?:every (?:day|week|month|morning|evening|afternoon|night|weekend|other day)|"
    r"every (?:mon|tues|wednes|thurs|fri|satur|sun)day|"
    r"each (?:day|week|morning|evening)|most (?:days|weeks|mornings|evenings)|"
    r"(?:once|twice|three times|four times|a few times) a (?:day|week|month)|"
    r"on (?:a|an) (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"at the weekend)\b", re.I)


# A routine is not a fault: "i get headaches most days" is a symptom to answer, and the card
# about it is the right reply. Nor is it a feeling ("i cry every morning") or a row, and those
# have their own readers. The words here are the ones that turn a routine into a complaint.
ROUTINE_IS_A_FAULT = re.compile(
    r"\b(?:pain|pains|\w*ache|\w*aches|aching|hurts?|hurting|sore|sick|ill|unwell|worse|worst|"
    r"worried|anxious|panic|cry|crying|cried|shout|shouting|shouted|argue|arguing|fight|"
    r"fighting|bleed|bleeding|blood|swollen|rash|fever|cough|coughing|vomit|vomiting|"
    r"dizzy|numb|sneeze|sneezing|stopped|stopping|wont stop|won't stop|leak|leaking|"
    r"broken|broke|craving|crave)\b", re.I)


# A routine they no longer keep is not a routine: "we used to talk every day" is about the past,
# and "that's a proper routine" is the wrong thing to say about it.
ROUTINE_IN_THE_PAST = re.compile(r"\b(?:used to|didn'?t use to|would (?:always |often )?\w+|"
                                 r"back then|years ago|in those days)\b", re.I)


# The person is the one doing it: "i walk the dog every day" is their routine, while "my dog
# barks at the postman every day" is the dog's behaviour, which is a question about the dog.
_ROUTINE_SUBJECT = re.compile(r"^\s*(?:and\s+|so\s+|well\s+|oh\s+)?(?:i|i(?:'m|ve|d)|we|we(?:'re|ve))\b",
                              re.I)


# The hours someone works are said as a shape of the week, and "on lates" is a shift, not a
# period that is late: "im on lates this week" was answered with the late-period card. The
# patterns need the shift word or the "on lates"/"earlies" shape, so "im late for work" and
# "my period is late" keep their own readings.
SHIFT_LATE = re.compile(
    r"\b(?:(?:i|we|im|i'm|we're|were)\s+)?(?:am|are|'m|'re|was|were)?\s*"
    r"(?:on|back on|working|work|doing|do)\s+(?:the\s+)?(?:lates|late shifts?)\b"
    r"|\bon (?:the )?lates\b|\blates (?:all|this|next|every|for)\b|\blate shifts?\b", re.I)


SHIFT_EARLY = re.compile(
    r"\b(?:(?:i|we|im|i'm|we're|were)\s+)?(?:am|are|'m|'re|was|were)?\s*"
    r"(?:on|back on|working|work|doing|do)\s+(?:the\s+)?(?:earlies|early shifts?)\b"
    r"|\bon (?:the )?earlies\b|\bearlies (?:all|this|next|every|for)\b|\bearly shifts?\b",
    re.I)


SHIFT_NIGHT = re.compile(
    r"\b(?:night shifts?|on nights|work(?:ing)? nights|nights this week)\b", re.I)


def shift_worked(text):
    """The shift pattern the line names ("late", "early", "night"), or None.

    "im on lates this week" and "im on earlies" are how half the working country says a week of
    two-till-ten or six-till-two. They are the hours of the week, not a late period: the word
    "lates" was read as "late" and reached the cycle card.
    """
    text = text if isinstance(text, str) else ""
    if SHIFT_NIGHT.search(text):
        return "night"
    if SHIFT_LATE.search(text):
        return "late"
    if SHIFT_EARLY.search(text):
        return "early"
    return None


# What somebody else says the person should do is not a day the person has had. "my mate said i
# should try that new pizza place" was answered "How was it, overall?", "i was told to rest" got
# "Good to hear. What was the best bit?" and "my sister says i would like that show" got "That
# show - fair enough. What's stopped it happening so far?": the past tense of "said" and "told",
# the short flat shape and the "i" in the reported clause read as an account of the person's own
# day, and nothing in the line has happened at all. A suggestion is a plan with somebody else's
# name on it, so the reading says who said it, and a reply about the plan is the one that fits.
A_REPORTED_VERB = re.compile(
    r"\b(?:said|says|say|told|tells|tell|reckons?|reckoned|thinks?|thought|suggests?|suggested|"
    r"recommends?|recommended|advises?|advised|insists?|insisted|keeps? (?:saying|telling me)|"
    r"wants? me to|wanted me to|nagged? me to|pushing me to|going on at me to)\b", re.I)


# The clause that holds the suggestion, and whose doing it is: the person being advised is the
# speaker ("i should", "me to rest"), so "i told him to stop" - advice given rather than
# received - is not this shape, and neither is a report of something done ("she said i was late").
A_SUGGESTED_CLAUSE = re.compile(
    r"\b(?:i|we) (?:should|shouldnt|shouldn't|ought|need|needed|have) (?:to )?"
    r"|\b(?:told|asked|tells|asks|wants?|wanted|nagged|pushing|pushed) me to\b"
    r"|\b(?:i would|id|i'd) (?:like|love|rather|be better|better off)\b", re.I)


# The passive puts the verb inside the clause instead of in front of it: "i was told to rest",
# "ive been told to slow down". The doing is still to come, so it is the same line.
A_TOLD_TO = re.compile(r"\b(?:was|were|am|im|been|be|got) told to\b", re.I)


# Advice to do nothing is not a plan to start, and the plan pools ask what the first step would
# be: "my mate said i shouldnt bother" was answered "Your mate may be onto something. What's the
# first step you could do this week?" - the opposite of what the mate said. Nor is waiting advice
# to act on. Both keep whatever reply they had.
A_NOT_A_SUGGESTION = re.compile(
    r"\b(?:shouldnt|shouldn't|should not|ought not|dont bother|don't bother|no point in|"
    r"not worth (?:it|the|bothering)|wait and see|sit tight|hold off|hang on|leave it for now|"
    r"think about it)\b", re.I)


# Who said it, in the line's own words: "my mate", "the doctor", "a friend", "my sister".
A_SAID_BY = re.compile(
    r"\b(?:my|the|a|an|our|his|her|their) (?:[\w'-]+ ){0,2}?"
    r"(?:mate|friend|mum|mom|mam|mother|dad|father|sister|brother|wife|husband|partner|son|"
    r"daughter|gran|nan|grandma|grandad|neighbour|neighbor|colleague|coworker|boss|manager|"
    r"doctor|gp|nurse|physio|physiotherapist|consultant|surgeon|midwife|dentist|pharmacist|"
    r"therapist|counsellor|counselor|trainer|coach|teacher|tutor|landlord|lads|girls|bloke|"
    r"fella|chap|someone|somebody)\b", re.I)


# Nobody in particular: "everyone says i should try yoga", "they told me to rest". The pool has
# a line for it, so the reading says the line names no one rather than leaving it to a pronoun.
A_SAID_BY_ANYONE = re.compile(r"\b(?:everyone|everybody|people|they|he|she)\b", re.I)


def _a_suggestion_from_someone(norm, text):
    """The advice somebody else gave, as {"who": "Your mate", "source": "my mate"}, or None.

    Two parts, and both are needed: a report ("said", "says", "told", "reckons", "wants me
    to", "i was told to") and a clause that is advice to the speaker ("i should", "me to rest").
    A report of a fact is somebody else's news and keeps its own reading, and a suggestion with
    no report in it ("i should try running") is the person's own plan, which the composer has.

    The name comes from the line where the line gives one, because "Your mate may be onto
    something" is a warmer reply than the same line with nobody in it. "my" becomes "Your":
    the bot is not in the family.
    """
    said = " " + " ".join(norm) + " "
    report = A_REPORTED_VERB.search(said)
    if not report:
        return None
    if not (A_SUGGESTED_CLAUSE.search(said, report.start()) or A_TOLD_TO.search(said)):
        return None
    if A_NOT_A_SUGGESTION.search(said):
        return None
    before = said[:report.start()]
    named = None
    for found in A_SAID_BY.finditer(before):
        named = found.group(0).strip()
    if named:
        words = named.split()
        if words[0] in ("my", "our"):
            words[0] = "your"
        who = " ".join(words)
    elif A_SAID_BY_ANYONE.search(before):
        who = ""
    else:
        who = ""
    return {"who": who[:1].upper() + who[1:], "source": named or ""}


def is_a_routine(line, read=None):
    """True when the line reports a routine the speaker keeps, rather than asking about one.

    "i walk the dog every day", "we eat out twice a month", "i water the plants every morning":
    the person is the one doing it, the line asks nothing, and nothing in it is a fault or a
    feeling. A card is about the thing a line names; on a routine the thing is what they do it
    to, and the routine is the news, so a module that would answer the thing stands aside and
    the habit tail says the routine back (bot/memory/ack.py::_plain).

    False for a question ("how often should i walk the dog"), for a line whose subject is
    something else ("my dog barks at the postman every day"), for a symptom ("i get headaches
    most days") and for a feeling ("i cry every morning").
    """
    read = read or {}
    if read.get("kind") not in ("statement", "news", None):
        return False
    if read.get("asks"):
        return False
    text = str(line.get("plain") or line.get("clean") or line.get("text") or "").strip()
    if not text or text.endswith("?"):
        return False
    if not _ROUTINE_SUBJECT.match(text):
        return False
    if ROUTINE_IS_A_FAULT.search(text) or ROUTINE_IN_THE_PAST.search(text):
        return False
    return bool(ROUTINE_SHAPE.search(text))


# --- the home somebody lives in now ----------------------------------------------------------
# "my mum moved into a home last month", "my nan is in a home too", "i feel guilty about not
# visiting my dad in the home". A home after "in the" or "into a" is where a person lives now,
# and every one of those lines was answered as guests arriving at the speaker's flat ("Give them
# the best bed and plan one shared outing a day") or as a move into a new one ("On the first
# night you need the bed made, toilet roll, a kettle..."), or said back as a fact ("Noted: your
# nan is in a home too shes 88"). None of them is a reply to the news.
CARE_HOME_PLACE = re.compile(
    r"\b(?:in|into|at)\s+(?:a|the)\s+(?:care\s+|nursing\s+|residential\s+)?home\b", re.I)


# Not that place: working from home is an office, a home town is where somebody grew up, and a
# home birth is neither. The article is what keeps "at home" out.
CARE_HOME_NOT = re.compile(r"\b(?:work|works|working|worked|stay|staying)\s+from\s+home\b"
                           r"|\bhome\s+(?:town|office|made|birth|baked)\b", re.I)


# The words a family uses that the relation list is not built from: "my nan is in a home too",
# "my mam moved in last month", "my mother-in-law".
CARE_HOME_KIN = frozenset("""nan nana mam mammy mate mates grannie grandaddy mother-in-law
    father-in-law sister-in-law brother-in-law son-in-law daughter-in-law""".split())


CARE_HOME_MOVED = re.compile(r"\b(?:moved|moves|moving|went|goes|gone|going|put|puts|putting"
                             r"|decided|decision|agreed|arranged|sorted)\b", re.I)


CARE_HOME_VISIT = re.compile(r"\b(?:visit|visits|visiting|visited|see|seeing|saw|"
                             r"bring|brings|bringing|brought|take her|take him|take them)\b", re.I)


CARE_HOME_GUILT = re.compile(r"\b(?:guilt|guilty|selfish|should have|shouldve|my fault|blame"
                             r"|couldnt cope|could not cope|no choice|heartbroken|awful)\b", re.I)


# A line that asks what to bring or take to somebody, with nobody and nothing named in it: "what
# should i bring her", "should i take him anything", "what can i bring". The whole sentence is
# about the person the conversation has already placed, and read word by word it is about the
# verb "bring" and nothing else - which is a customs allowance.
CARE_HOME_BRING_ASKS = re.compile(
    r"\b(?:what|anything|something|whats|should i|shall i|can i|could i|do i|did i|"
    r"is there anything)\b", re.I)


CARE_HOME_BRING_WORD = re.compile(r"\b(?:bring|brings|bringing|take|takes|taking)\b", re.I)


CARE_HOME_BRING_WHO = re.compile(r"\b(?:her|him|them|she|he|they)\b", re.I)


def a_home_carried_forward(text, earlier_lines):
    """The care home a line with no home in it is about, read from the conversation, or None.

    "my mum moved into a home last month" places somebody; "what should i bring her" two turns
    later is about that same visit, and on its own the only word in it that means anything is
    "bring" - so the answer was the customs allowance ("Coming into the UK you can bring 4 litres
    of spirits"). The line names neither a person nor a thing, so the subject is only clear from
    the turn before it: that is what this reads, and `carried` says where the reading came from.
    """
    line = re.sub(r"['\u2019]", "", str(text or "")).strip()
    if not line or a_care_home(line):
        return None
    if not (CARE_HOME_BRING_ASKS.search(line) and CARE_HOME_BRING_WORD.search(line)
            and CARE_HOME_BRING_WHO.search(line)):
        return None
    for earlier in reversed(list(earlier_lines or ())):
        read = a_care_home(earlier)
        if read:
            carried = dict(read)
            carried["shape"] = "bring"
            carried["carried"] = str(earlier)
            return carried
    return None


def a_care_home(text):
    """The person living in a care home a line is about, or None.

    `shape` says what the line is about there: "guilt" when it names the feeling, "visiting" when
    it is about going, "moved" when somebody has just gone in, and "in" for the plain statement.
    """
    from .topics import RELATIONS   # a local import: topics imports this module
    line = re.sub(r"['\u2019]", "", str(text or "")).strip()
    if not line or not CARE_HOME_PLACE.search(line) or CARE_HOME_NOT.search(line):
        return None
    lowered = line.lower()
    who, relation = "", None
    for match in re.finditer(r"\b(?:my|our|your)\s+([a-z][a-z-]*)", lowered):
        if match.group(1) in RELATIONS or match.group(1) in CARE_HOME_KIN:
            relation = match.group(1)
            who = " ".join(match.group(0).split())
            break
    if not who:
        for word in ("shes", "hes", "she", "he", "they", "theyre"):
            if re.search(r"\b%s\b" % word, lowered):
                who = word
                break
    if not who:
        return None  # "the home" with nobody named is not news about a person
    if relation in ("husband", "father", "dad", "son", "brother", "uncle", "cousin", "grandad",
                    "grandpa", "grandfather", "granddad", "partner", "boyfriend", "friend",
                    "male friend", "nephew", "stepdad", "stepfather"):
        pronoun = "he"
    elif relation in ("wife", "mother", "mum", "mom", "daughter", "sister", "aunt", "gran",
                      "granny", "grandma", "grandmother", "partner", "girlfriend", "friend",
                      "niece", "stepmum", "stepmother", "nan", "nana", "mam", "mammy",
                      "grannie", "mother-in-law", "sister-in-law", "daughter-in-law"):
        pronoun = "she"
    elif relation in ("kids", "children", "child", "parents", "friends", "mates", "mate"):
        pronoun = "they"
    elif who in ("he", "hes"):
        pronoun = "he"
    elif who in ("she", "shes"):
        pronoun = "she"
    else:
        pronoun = "they"   # the line does not say, and "they" is never wrong
    if relation in ("kids", "children", "parents", "friends"):
        pronoun = "they"
    if CARE_HOME_GUILT.search(lowered):
        shape = "guilt"
    elif CARE_HOME_VISIT.search(lowered):
        shape = "visiting"
    elif CARE_HOME_MOVED.search(lowered):
        shape = "moved"
    else:
        shape = "in"
    return {"text": " ".join(CARE_HOME_PLACE.search(line).group(0).split()),
            "who": who, "relation": relation, "pronoun": pronoun, "shape": shape}


_MONEY_NOUN = re.compile(
    r"\b(?:price[sd]?|pricing|cost[s]?|costing|charge[sd]?|fare[s]?|fee[s]?|rent|rental|"
    r"salary|salaries|wage[s]?|expensive|cheaper|cheapest|cheap|how\s+much\s+money)\b")


# A money word is not an ask for a figure. "can i withhold rent", "does paye come out of my
# wages", "is a dog expensive" and "can i pay by card at the tip" all name money and none of them
# asks what anything costs. What makes a price is the shape of the ask - how much, what does it
# cost, what is the price of, what is it worth, which is cheapest - so that is what the class is,
# and a money word on its own says nothing.
_A_PRICE_ASK = re.compile(
    r"\bhow\s+much\s+(?:is|are|was|were|will|would|does|do|did|should|can|could|might|"
    r"is\s+it|do\s+they|do\s+you|do\s+i|does\s+it)\b|"
    r"\bprice[sd]?\s+(?:of|for|on)\b|\bcost\s+of\b|"
    r"\bwhats?\s+(?:the\s+)?(?:price|cost|charge|fare|fee|rent)\b|"
    r"\bwhat\s+(?:is|are)\s+the\s+(?:price|cost|charge|fare|fee|rent)\b|"
    r"\bwhat\s+(?:does|do|will|would|should)\b[^?]{0,30}?\b(?:cost|charge)\b|"
    r"\bwhats?\s+(?:it|that|this|they|one)\s+worth\b|\bhow\s+much\s+(?:money|for)\b|"
    r"\bcheapest\b|\bdeals?\s+on\b|\bon\s+offer\b|\bdiscount(?:s|ed)?\b|"
    r"\b(?:anything|something|any|some)\s+(?:a\s+bit\s+|much\s+)?cheaper\b|"
    r"\bis\s+(?:there|that|it)\s+cheaper\b|\bcheaper\s+(?:than|option|ones?|deal)\b|"
    r"\bprice\s+match\b|"
    # A comparison of what things cost is a price question with no figure in it, and so is the
    # rate a trade charges: "is a stamp cheaper online", "whats the going rate for a plumber".
    r"\b(?:cheaper|more\s+expensive|dearer|pricier|costlier|better\s+value)\b|"
    r"\b(?:going|market|typical|average|usual|standard|ballpark)\s+"
    r"(?:rate|price|cost|fee|charge)\b")


# Who holds an office is a fact with a date on it: the answer was different last year and will be
# different again, so it is not the bot's to state from memory. "who is the prime minister" and
# "whos the ceo of twitter" are askable; "who is the queen" is not askable as a post.
_A_POST_HOLDER = re.compile(
    r"\bwho(?:s|\s+is|\s+are)?\s+(?:the\s+|our\s+)?(?:prime\s+minister|pm|president|"
    r"chancellor|home\s+secretary|first\s+minister|mayor|mp|meps?|ceo|chief\s+executive|"
    r"head\s+teacher|manager|coach|owner|chair(?:man|woman|person)?)\b"
    r"(?![^?]*\b(?:of\s+the\s+year|ever|all\s+time|alive|dead)\b)")


# How much a thing weighs or holds is a fact about the thing, whatever the words: "how much does
# a jar of coffee weigh" is a measurement, not a price.
# A person's own spending is not a figure the world holds: the bot was not there.
_A_HOW_MUCH_I_SPENT = re.compile(
    r"\bhow\s+much\s+(?:did|have|has|do)\s+(?:i|we)\s+(?:spend|spent|pay|paid|earn|earned|"
    r"save|saved)\b")


# The same holds for a figure about the person's own account, whatever verb asks it. "how much am
# i paying for my subscription" is not a price the world sets: the bot cannot see their bill, their
# subscription or their account, and the reply that answers it ("what you pay is on your own bill")
# is a better one than a price card. Only the `did i spend` shape was fenced, so `am i paying`
# fell through to the bare `how much` in `_A_COUNT` and read as a price. What makes the figure
# theirs is the person doing the paying, or a possessive on the thing billed - and neither is a
# word about time, so this is a fence and not a class of its own.
_A_MY_OWN_FIGURE = re.compile(
    r"\b(?:am|do|will|would|should|have|did|can)\s+i\s+(?:be\s+)?(?:paying|charged|billed|"
    r"spending|getting\s+charged)\b|"
    r"\bmy\s+(?:own\s+)?(?:bill|bills|subscription|subscriptions|account|card|statement|"
    r"tariff|contract|plan|direct\s+debit|standing\s+order|invoice|receipt|payslip|quota|"
    r"allowance)\b")


# A measure in, "in" or "to", a measure out is a conversion, and a conversion is arithmetic: the
# numbers do not move. "how much is 200g in cups" and "how much is 180c in fahrenheit" were read as
# prices because "how much" is the price ask and nothing said otherwise. A quantity of money on
# either side is an exchange rate, and a rate does move, so a money word keeps the line live.
_MONEY = re.compile(
    r"\b(?:dollars?|euros?|quid|cents?|yen|rupees?|pence|money|cash)\b")


_UNITS = (r"g|kg|kilos?|kilograms?|grams?|oz|ounces?|lbs?|pounds?|ml|l|millilit(?:re|er)s?|"
          r"litres?|liters?|cups?|tbsp|tsp|"
          r"tablespoons?|teaspoons?|celsius|fahrenheit|centigrade|degrees|stone|inches?|inch|"
          r"cm|mm|metres?|meters?|feet|foot|ft|miles?|km|yards?|pints?|quarts?|gallons?")


# The units that are never a thing you buy by the one - a cup of coffee and a pint of milk are
# prices. So a measure with no "of" after it is a measure, and one with "of" is what it costs.
_UNITS_BOUGHT = (r"g|kg|kilos?|kilograms?|grams?|oz|ounces?|lbs?|ml|l|millilit(?:re|er)s?|"
                 r"litres?|liters?|cups?|tbsp|tsp|"
                 r"tablespoons?|teaspoons?|celsius|fahrenheit|centigrade|degrees|stone|"
                 r"inches?|inch|cm|mm|metres?|meters?|feet|foot|ft|miles?|km|yards?")


# A number with a unit and then what it is of is an amount of a thing, and an amount of a thing
# costs money: "how much is 500 ml of paint" is a price and not a sum, even though the arithmetic
# reading hears "how much is 500".
_A_AN_AMOUNT_OF_A_THING = re.compile(
    r"\b\d+\s*(?:" + _UNITS + r")\b\s+(?:of|in)\b|"
    r"\b(?:a|an|one|two|three|half|quarter)\s+(?:" + _UNITS_BOUGHT + r")\s+of\b")


_A_A_CONVERSION = re.compile(
    r"\bhow\s+(?:much|many)\b[^?]{0,30}?\b(?:\d+)?\s*(?:" + _UNITS +
    r")\b\s+(?:in|to|into)\s+\w")


_A_HOW_MUCH_OF_A_UNIT = re.compile(
    r"\bhow\s+much\s+(?:is|are|was)\s+(?:a\s+|an\s+|one\s+)?[\d\w\s]{0,12}?\b(?:" +
    _UNITS_BOUGHT + r")\b(?!\s+of\b)")


# "what time is it" is the clock, not a place's hours.
_A_THE_CLOCK = re.compile(r"\bwhat\s+time\s+is\s+it\b|\bwhats\s+the\s+time\b")


_A_HOW_MUCH_IT_HOLDS = re.compile(
    r"\bhow\s+much\s+(?:\w+\s+){0,2}(?:does|do|is|are|will|would|should|must|can)\b"
    r"[^?]{0,60}?\b(?:weigh|weighs|hold|holds|contain|"
    r"contains|measure|measures|store|stores|sleep|sleeps|eat|eats|drink|drinks|feed|feeds|"
    r"lift|lifts|take|takes|need|needs|use|uses|burn|burns|grow|grows|train|exercise|"
    r"practise|practice|study|water|feed|give|have|put|add)\b")


# How much somebody is loved, missed or cared about is not a figure at all.
# "how much exercise is enough" asks for an amount, not for a figure.
_A_HOW_MUCH_ENOUGH = re.compile(
    r"\bhow\s+much\b[^?]{0,40}?\b(?:enough|too\s+much|too\s+little|of\s+it)\b|"
    r"\bhow\s+much\s+of\b")


_A_HOW_MUCH_IS_IN = re.compile(
    r"\bhow\s+much\s+(?:is|are)\s+(?:there\s+)?left\b|"
    r"\bhow\s+much\s+(?:is|are)\s+(?:in|left\s+in)\b|"
    r"\bhow\s+much\s+(?:\w+\s+)?in\s+(?:a|an|one|the|\d)\b|"
    r"\bhow\s+much\s+(?:\w+\s+){0,2}for\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|"
    r"ten|twenty)\b[^?]{0,20}\b(?:people|persons?|portions?|servings?|guests?|adults?|kids?)\b|"
    r"\bhow\s+much\s+(?:\w+\s+){0,2}per\s+(?:person|head|portion|serving)\b")


_A_HOW_MUCH_A_FEELING = re.compile(
    r"\bhow\s+much\s+(?:do|does|did)\s+(?:you|i|we|he|she|they)\s+(?:love|care|miss)\b")


# A sum is settled before any class is looked for: "how much is 2 plus 2" is arithmetic, and so
# is "whats 20% of 50". The reading already files some of these under `asks: maths`, and the
# digits or the sign appear in the line itself.
_A_ARITHMETIC = re.compile(
    r"\d\s*(?:\+|\*|x|/|plus|minus|times|divided\s+by|multiplied\s+by)\s*\d|"
    r"\d\s+-\s+\d|"
    r"\b(?:percent|per\s?cent)\b|\d\s*%|\bwhats\s+\d+\s*%|"
    r"\b(?:plus|minus|divided\s+by|multiplied\s+by)\s+(?:\d+|one|two|three|four|five|six|seven|"
    r"eight|nine|ten|twenty|thirty|fifty|hundred|thousand)\b")


_A_HAS_A_NUMBER = re.compile(r"\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b")


# A difference between two things is a fact about them, not about today: "whats the difference
# between weather and climate" names the sky and asks for neither today's rain nor this week's.
_A_A_DIFFERENCE = re.compile(
    r"\b(?:whats|what\s+is|what\s+was)\s+the\s+difference\b|\bdifference\s+between\b|"
    r"\bhow\s+(?:do|does)\s+\w+\s+differ\b|"
    r"\bhow\s+(?:is|are|was|were)\b[^?]{0,40}?\b(?:different|differs?|distinct)\s+"
    r"(?:from|to|than)\b")


# Asking the bot whether it saw something is a question about the bot, not a request for the news.
_A_DID_YOU_SEE = re.compile(
    r"\bdid\s+you\s+(?:see|hear|watch|read|catch|catch\s+up\s+on)\b|"
    r"\bhave\s+you\s+(?:seen|heard|watched|read)\b|\bdid\s+you\s+know\b")


# A record is a fact about the world that a superlative states, and people state it as a bare
# noun as often as they ask it: "the biggest country in the world" is a request for the answer.
_A_BARE_RECORD = re.compile(
    r"^\s*(?:(?:and|so|but|then)\s+)?(?:the|whats\s+the|what\s+is\s+the|which\s+is\s+the)?\s*"
    r"(?:biggest|largest|tallest|longest|smallest|deepest|highest|oldest|fastest|richest|"
    r"most\s+populous)\b")


# A year that has gone settles whatever is in the line: nothing about 1966 is today's version of
# anything, however live the words around it are.
_A_PAST_YEAR = re.compile(r"\b(?:back\s+)?in\s+(?:1[0-9]{3}|20[0-2][0-9])\b")


# A war that has been fought is history, however it is asked about.
_A_HISTORY_ITSELF = re.compile(
    r"\b(?:first|second|third|1st|2nd|world)\s+world\s+war\b|\bworld\s+war\s+(?:one|two|1|2|ii)\b|"
    r"\bthe\s+(?:great\s+)?war\b")


# The age of the world itself is a date and not a figure that moves.
# How hot, deep, tall or heavy a thing itself is is a measurement of that thing, and the same
# figure next year: "how hot is lava", "how hot is a scotch bonnet", "how deep is the ocean". What
# makes a line the weather is asking how it is *here and now* - "it", "outside", "today".
_A_HOW_A_THING_MEASURES = re.compile(
    r"\bhow\s+(?:hot|cold|warm|deep|tall|high|heavy|big|large|long|wide|fast|strong)\s+"
    r"(?:is|are|was|were)\s+(?!it\b|outside\b|today\b|tonight\b|this\b|the\s+weather\b)")


# A traffic light is not traffic: the lights on a road, or the label on a packet.
_A_A_TRAFFIC_LIGHT = re.compile(r"\btraffic\s+lights?\b")


# A plan about the weather is the plan, not the forecast: "what should we do about the weather
# plan", "weather permitting".
_A_A_PLAN_ABOUT_THE_WEATHER = re.compile(
    r"\b(?:the\s+)?weather\s+(?:plan|plans|permitting|dependent|depending)\b")


# What makes a line about the sky rather than about a thing: it asks how it is here and now.
_A_WEATHER_HERE = re.compile(
    r"\b(?:is|will)\s+it\s+(?:be\s+)?(?:going\s+to\s+)?(?:rain|snow|sunny|windy|hot|cold)\b|"
    r"\bhow\s+(?:hot|cold|warm|windy)\s+(?:is|will)\s+it\b|"
    r"\b(?:today|tonight|tomorrow|this\s+(?:week|weekend|morning|afternoon|evening)|"
    r"outside|right\s+now|at\s+the\s+moment)\b")


_A_HOW_OLD_IS_THE_WORLD = re.compile(
    r"\bhow\s+old\s+is\s+the\s+(?:earth|world|universe|planet|sun|moon)\b")


_MONEY_ASKED = re.compile(
    r"\bhow\s+much\s+(?:is|are|was|were|will|would|does|do)\b(?!\s+(?:too|enough|of)\b)")


# "how much for a ticket" asks the same thing without a verb.
_MONEY_FOR = re.compile(r"\bhow\s+much\s+for\b")


# A place's own times. "is it open" and "what time does it close" are the same ask, and both
# are worth checking before a person travels.
# The verb of opening has to be about a place, so a thing has to be behind it: "is tesco open
# now", "is it open", "are the shops open on sunday", "what time does the surgery close". Without
# a thing - "the heating starts", "what time do i clock in" - the verb is somebody else's
# business, so "start" and "finish" are not here at all, and a place's times are never the
# person's own diary.
# A place is named with more than one word as often as with one: the post office, the swimming pool,
# the station ticket office. The verb of opening is still the same ask, so the thing in front of it
# is looked for as a place however many words it is, and the folder that keeps the hours is the one
# that fixes them - "is the post office open" is as much a place's times as "is tesco open".
_A_PLACE_THAT_KEEPS_HOURS = re.compile(
    r"\b(?:shops?|stores?|supermarkets?|gyms?|pools?|librar(?:y|ies)|chemists?|"
    r"pharmac(?:y|ies)|surger(?:y|ies)|doctors?|dentists?|banks?|garages?|stations?|offices?|"
    r"centres?|centers?|clinics?|cafes?|pubs?|restaurants?|takeaways?|chippys?|markets?|"
    r"museums?|halls?|churches?|schools?|colleges?|tips?|dumps?|post\s+office|"
    r"leisure\s+centre|swimming\s+pool|garden\s+centre|car\s+park)\b")


# The same list, as the thing the line has to name before a day word can make a verb of opening an
# ask about hours: "is the post office open today" is the hours, "is the front door open today" is
# a door. So the day-word arms below require a place, and a door, a lid, a window, an eye or a
# fridge door is therefore never one - however the line words the day.
_A_LINE_THAT_NAMES_A_PLACE = r"(?=[^\n]*" + _A_PLACE_THAT_KEEPS_HOURS.pattern + r")"


# A place word is not enough on its own: "is the garage door open today" names a garage and asks
# about a door, so a door, a gate, a window, a lid or an eye right before the verb of opening is the
# thing that opens, and no hours. This is the fence the place word alone cannot keep.
_NOT_A_FITTING_THAT_OPENS = (r"(?![^\n]*\b(?:doors?|gates?|windows?|lids?|drawers?|eyes?|"
                            r"mouth|flaps?|valves?|caps?|tins?|jars?|boxes?)\s+"
                            r"(?:open|opens|closed|closes|shut|shuts)\b)")


# The day the ask is about. Words of now and a day of the week are what turn "open" into a question
# about hours; on their own they are not one ("the window is open").
_A_DAY_WORD = (r"(?:today|tonight|tomorrow|now|this\b|on\b|at\b|until\b|till\b|late\b|"
               r"for\s+the\s+day|,)")


# Who may use a place is not when it is open: `is the swimming pool open to non members`, `is the
# shop open to offers`, `is the cafe open for lunch`. The word after the verb of opening is the
# whole difference - "open to" and "open for" name the people or the purpose - unless what follows
# is the day itself ("open for the day", "open to the public today" is still not hours, but "open
# for the day" is), so the fence looks at the word after it.
_NOT_OPEN_TO_SOMEBODY = (r"(?![^\n]*\b(?:open|opens)\s+(?:to|for)\s+"
                         r"(?!(?:today|tonight|tomorrow|now|late|the\s+day|the\s+weekend|"
                         r"the\s+summer|christmas|easter)\b))")


_HOURS = re.compile(
    r"\bopening\s+(?:hours?|times?)\b|\bclosing\s+time\b|\blate\s+opening\b|"
    r"\bbank\s+holiday\s+hours\b|"
    r"\b(?:open|opens|closed?|closes|shuts?)\s+(?:until|till|at|on|late|early)\b|"
    + _A_LINE_THAT_NAMES_A_PLACE + _NOT_A_FITTING_THAT_OPENS + _NOT_OPEN_TO_SOMEBODY +
    r"\b(?:is|are|was|were|does|do|will)\s+(?:[\w']+\s+){0,4}?(?:open|opens)\s+"
    r"(?:today|tonight|tomorrow|now|this\s+\w+)\b|"
    + _A_LINE_THAT_NAMES_A_PLACE + _NOT_A_FITTING_THAT_OPENS + _NOT_OPEN_TO_SOMEBODY +
    r"\b(?:is|are|was|were)\s+(?:[\w']+\s+){0,3}?(?:open|opens|closed|closes|shut|shuts)\b"
    r"(?=\s*" + _A_DAY_WORD + r")|"
    + _NOT_A_FITTING_THAT_OPENS + _NOT_OPEN_TO_SOMEBODY +
    r"\b(?:is|are|was|were|does|do)\s+(?:the\s+|a\s+)?(?:\w+\s+){0,2}?"
    + _A_PLACE_THAT_KEEPS_HOURS.pattern + r"\s+(?:open|opens|closed|closes|shut|shuts)\b|"
    + _NOT_A_FITTING_THAT_OPENS + _NOT_OPEN_TO_SOMEBODY +
    _A_PLACE_THAT_KEEPS_HOURS.pattern + r"\s+(?:\w+\s+){0,2}?"
    r"(?:open|opens|closed|closes|shut|shuts)\b(?=\s*" + _A_DAY_WORD + r")|"
    + _NOT_OPEN_TO_SOMEBODY +
    r"\b(?:is|are|was|were)\s+(?:it|they|there(?:\s+anywhere)?|"
    r"(?:the|this|that|my|our|your|any)\s+\w+|"
    r"\w+)\s+open\b|"
    r"\bwhat\s+times?\s+(?:does|do|is|are|will)\b|"
    r"\b(?:when|what\s+times?)\b[^?]{0,30}?\b(?:open|opens|close|closes|closed|shut|shuts)\b")


# Today's sky, not the word for it. Rain and snow as advice ("how do i drive in snow"), as a
# cause ("why does thunder happen") or as a memory ("my wipers judder when its raining") are all
# about something else, so the sky has to be asked about: it is going to rain, the forecast, the
# weather, how hot it is today.
_WEATHER = re.compile(
    r"\bweather\b|\bforecast\b|\bumbrella\b|"
    r"\bhow\s+(?:hot|cold|warm|windy)\s+(?:is|will)\s+it\b|"
    r"\b(?:is|will)\s+it\s+(?:be\s+)?(?:going\s+to\s+)?(?:rain|snow|be\s+sunny|be\s+windy|"
    r"be\s+stormy|be\s+hot|be\s+cold)\b|"
    r"\bit\s+(?:is|will|should|might)\s+(?:be\s+)?(?:rain|snow|sunny|windy|stormy)\b|"
    r"\bheat\s?wave\b|\bcold\s+snap\b|\btemperature\s+(?:today|tomorrow|outside)\b")


# The day's news, not every word that lives in it. "score" is a credit score as often as a
# football one, "results" are exam results, and "whats going on with you" is about the bot, so a
# score has to be *the* score or a fixture, results belong to a match, and the news has to be
# asked for: the news, any news, the latest on, what happened, who won, the score.
_NEWS = re.compile(
    r"\bnews\b|\bheadlines?\b|"
    r"\b(?:whats|what\s+is|what\s+was|anything|any|the\s+latest|latest|breaking|got\s+any)\s+"
    r"(?:the\s+)?(?:news|headlines?)\b|"
    r"\b(?:latest|update[s]?)\s+(?:on|about)\b|"
    r"\b(?:news|press|newspaper)\s+stor(?:y|ies)\s+(?:on|about)\b|"
    r"\b(?:the|any|more)\s+word\s+(?:on|about)\b|"
    r"\bwhats\s+going\s+on\s+(?:in|at|with)\s+the\s+(?:world|news|country|city)\b|"
    r"\bwhats\s+(?:happened|happening)\b|\bwhat\s+(?:is|was)\s+happening\b|"
    r"\belections?\s+(?:today|tonight|this\s+(?:week|year)|results?)\b|"
    r"\bwho\s+won\b|\bwho(?:s|\s+is)\s+winning\b|\bdid\s+(?:\w+\s+){0,3}win\b|"
    r"\bhas\s+(?:\w+\s+){0,3}(?:won|finished|played)\b|"
    r"\bthe\s+score\b|\bwhats\s+the\s+score\b|\bleague\s+table\b|\bthe\s+table\b|"
    r"\bmatch\s+result\b|\b(?:the\s+)?results?\s+(?:of|from)\s+the\s+(?:match|game)\b|"
    r"\btransfers?\s+(?:news|today|latest)\b")


_AVAILABILITY = re.compile(
    r"\b(?:in\s+stock|stock\s+levels?|available|availability|unavailable|sold\s+out|"
    r"vacanc(?:y|ies)|hiring|waiting\s+list|"
    r"bookings?\s+(?:open|available|left|for)|"
    r"(?:make|get|book|check|change|cancel|move|confirm)\s+(?:a\s+|my\s+|the\s+)?booking\b|"
    r"(?:tickets?|places?|spaces?|seats?|rooms?|jobs?|appointments?)\s+(?:\w+\s+){0,2}"
    r"(?:left|going|available|free)\b)")


_TIMETABLE = re.compile(
    r"\b(?:timetables?|next\s+(?:train|bus|flight|boat|ferry|coach)|departures?|arrivals?|"
    r"delay(?:s|ed)?|roadworks?|bus\s+times?|train\s+times?|flight\s+times?|"
    r"traffic\s+(?:report|news|today|now|on\s+the)|"
    r"\bare\s+(?:the\s+)?(?:trains|buses|tubes|flights|ferries|trams)\s+running\b|"
    r"\bis\s+the\s+(?:m\d+|a\d+|motorway|road|bridge|tunnel)\s+(?:closed|open|blocked)\b|"
    r"what\s+time\s+(?:is|does)\s+the\s+(?:train|bus|flight))\b")


# A scheduled service - a train, a bus, a flight, a coach, a ferry, a tram - is not a live thing
# on its own: "how many trains are there in the uk" is a count of rolling stock and the same
# answer next year. What makes it live is being asked about *on a day or at a time*: the thing
# asked about is then the timetable and not the vehicle, whatever shape the ask has. So the two
# have to be there together, and the shape (a count, a superlative) loses to them.
# A time people say in place of the service - "the 8.15", "the 18.20" - names a train, a bus or a
# flight when a verb of going follows it ("is the 8.15 running"), and names nothing when it does
# not ("whats on the 7.30 news").
_A_SERVICE = re.compile(
    r"\b(?:trains?|buses?|bus|trams?|tubes?|underground|metro|flights?|ferry|ferries|"
    r"coach(?:es)?|platform|departures?|arrivals?)\b|"
    r"\bthe\s+\d{1,3}(?:[:.]\d{2})?(?=\s*(?:running|run|runs|leaves|leaving|departs?|"
    r"departing|due|arrives?|arriving|go|goes|going|take|takes|train|bus|flight))")


_A_DAY_OR_TIME = re.compile(
    r"\b(?:today|tonight|tomorrow|yesterday|this\s+(?:morning|afternoon|evening|weekend|week)|"
    r"next\s+(?:week|weekend)|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"weekends?|bank\s+holiday|christmas|easter)\b|\b\d{1,2}[:.]\d{2}\b|"
    r"\bo'?clock\b|\b\d{1,2}\s?(?:am|pm)\b|\bhalf\s+past\b|\bhow\s+often\b")


class _AServiceOnADay:
    """A named service and a day or a time, both of which have to be there."""

    def __init__(self, service, when):
        self.service, self.when = service, when

    def search(self, text):
        service = self.service.search(text)
        if service is None:
            return None
        when = self.when.search(text)
        if when is None:
            return None
        return service if service.start() <= when.start() else when


# A service's state is the timetable too: a train that is late, cancelled or on time, a bus on
# strike. It is the day's version of the timetable, not a fact about trains in general.
_A_SERVICE_STATE = re.compile(
    r"\b(?:trains?|buses?|bus|flights?|coach(?:es)?|ferry|ferries|trams?)\b.{0,40}?"
    r"\b(?:late|delayed|cancell?ed|on\s+time|on\s+strike|diverted|full\s+up)\b")


_SERVICE_ON_A_DAY = _AServiceOnADay(_A_SERVICE, _A_DAY_OR_TIME)


# A rate is a figure the world keeps changing under the person's feet: it is not the bot's to
# state from memory even when it is right this month.
_RATE = re.compile(
    r"\b(?:interest\s+rate[s]?|exchange\s+rate[s]?|tax\s+rate[s]?|inflation|mortgage\s+rate[s]?|"
    r"minimum\s+wage|price\s+cap|energy\s+cap|"
    r"national\s+insurance\s+(?:rate|contribution[s]?|percent|%)|stamp\s+duty|vat|"
    r"base\s+rate)\b")


_EVENT = re.compile(
    r"\b(?:whats\s+on|what\s+is\s+on|anything\s+on(?!\s+(?:a|an|the|my|your|about|for)\b)|"
    r"events?\s+on|gig\s+guide|show\s+times?|"
    r"cinema\s+times?|fixtures?|opening\s+night|when\s+is\s+the\s+\w+\s+on\b)\b")


# The order the classes are read in: the narrower class first, so "how much is the minimum
# wage" is a rate rather than a wage, and "what time does the bus leave" is a timetable rather
# than a place's hours.
# A word for freshness says the thing is today's version; it does not say the thing is not that
# thing. "what is the latest score" is the score, so the class lookup reads the line without it.
# It is dropped only here: "what is the latest iphone" is still not a definition (see _A_DEFINITION).
_A_FRESHENING = re.compile(
    r"\b(?:latest|current|newest|most\s+recent|up[\s-]to[\s-]date)\s+"
    r"(?!(?:on|about|of|in|from|at|with)\b)")


_CHANGING = (
    ("rate", _RATE),
    ("price", _A_PRICE_ASK),
    ("post", _A_POST_HOLDER),
    ("timetable", _SERVICE_ON_A_DAY),
    ("timetable", _A_SERVICE_STATE),
    ("timetable", _TIMETABLE),
    ("hours", _HOURS),
    ("weather", _WEATHER),
    ("news", _NEWS),
    ("availability", _AVAILABILITY),
    ("event", _EVENT),
)


# An explanation or a how-to is a fact about the world, not today's version of it. "how do
# weather forecasts get it wrong so often" is asking how a thing works, "how do i drive in the
# rain" how to do it, and "what causes train delays" what makes them - none of them is asking
# what the weather is doing or when the next train goes, so the live noun does not decide them.
# A line that also says *now* ("why is my train late today") is about today after all.
_A_HOW_IT_WORKS = re.compile(
    r"\bhow\s+(?:do|does|did)\b|\bwhy\s+(?:do|does|did)\b|\bwhat\s+causes?\b|"
    r"\bwhat\s+caused\b|\bhow\s+come\b")


# "when should i start", "what time do we leave" - the ask is about the person's own plan, not
# about a place's hours or a service's timetable, however the nouns around it read.
_A_MY_OWN_PLAN = re.compile(
    r"\b(?:when|what\s+time)\s+(?:(?:should|shall|do|does|can|could|will|would|must|might|"
    r"had\s+better)\s+)?(?:i|we|you)\b(?!\s+(?:open|opens|close|closes|shut|shuts|serve|"
    r"serves|trade|trades)\b)")


# What time their own appointment is, is their diary and not a place's hours: "what time is the
# funeral", "what time is my scan". A match or a fixture is still a fixture.
_A_AN_OCCASION_OF_THEIR_OWN = re.compile(
    r"\b(?:what|which)\s+time\s+(?:is|are|was|were|does|do|did|will|would)\b.{0,25}?"
    r"\b(?:funeral|wake|meeting|appointment|interview|scan|operation|procedure|checkup|"
    r"check-up|assessment|induction|shift|session|court|hearing|viewing)\b")


_A_SAYS_NOW = re.compile(
    r"\b(?:today|tonight|tomorrow|right\s+now|at\s+the\s+moment|this\s+(?:morning|"
    r"afternoon|evening|week|weekend)|currently|still)\b")


# A sealed fact, in the shapes people ask for one. Each of these is the same answer in ten
# years: a count, a record, a definition, a working, a history, a method.
_A_HOW_MANY = re.compile(r"\bhow\s+many\b")


_A_COUNT = re.compile(r"\bhow\s+many\b|\bhow\s+far\s+is\b|\bhow\s+long\s+is\b|\bhow\s+much\b")


_A_RECORD = re.compile(
    r"\bthe\s+(?:biggest|largest|tallest|oldest|youngest|longest|shortest|highest|lowest|"
    r"deepest|shallowest|fastest|slowest|smallest|richest|poorest|wealthiest|heaviest|"
    r"lightest|widest|narrowest|thinnest|strongest|busiest|rarest|commonest|most\s+common|most\s+popular|"
    r"most\s+\w+|least\s+\w+)\b")


# A definition names the thing. A word for freshness, for the best one or for the main one is not
# the thing: "what is the latest iphone" names a model that changes every year and settles nothing,
# while "what is the latest news" is the news and is settled by its own class.
_A_DEFINITION = re.compile(
    r"\bwhat\s+(?:is|are|was|were)\s+(?:(?:a|an|the)\s+)?"
    r"(?!(?:latest|newest|current|best|worst|main|right|usual|cheapest|nearest|the|a|an|it|that|this|they|these|those)\b)\w+|"
    r"\bwhat\s+does\s+\w+\s+mean\b|"
    r"\bwhat\s+is\s+the\s+meaning\b|\bwhat\s+does\s+(?:a|an|the)?\s*\w+\s+do\b")
