"""Part 6 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from .normalize import opens_without_subject, strip_leaders
from .kinds_part_01 import (
    ALWAYS_SELF_ONLY, A_COMPARISON, A_LIMIT_ABOUT_PEOPLE, A_MONEY_SUBJECT, A_MONTH_PERIOD, A_PERIOD,
    BODY_STATE_CUES, CONFUSED_SELF_ONLY, EMOTION_WORDS, GOOD_EMOTION_NAMES, IDIOM_STATES,
    LABEL_ON_A_PERSON, NOT_A_MOOD_THERE, NOT_THE_SPEAKERS_DAY, PERIOD_CUES, SAID_AS_A_NEGATION,
    SELF_ONLY_CUES, THING_OR_PERSON_CUES, _laughed_off, NEGATIONS, PRONOUNS, QUESTION_STARTS,
    QUESTION_WORDS, SUBJECT_NEGATIONS, YESNO_STARTS, RECOMMEND, THANKS, COMPARE, OPINION,
    RECOMMEND_PHRASES, STEPS, STEPS_WORD, _asks_for_help, _turns_the_pair_down,
    two_ends_of_one_scale, ACK, FAREWELLS, GREETINGS, LAUGH, ADDRESSED_LINES, NEGATIVE, OK_WORDS,
    POSITIVE, TERMS_OF_ADDRESS, GIVEN_ADVICE, THANKS_ASK_NOUNS, THANKS_ASK_PREPS, THANKS_ASK_WORDS,
)
from .kinds_part_02 import (
    ABILITY_AT, BETTER_OFF, GETTING_WORSE, GOOD_WORD_COMPARED, GOOD_WORD_MISSING, NO_BETTER,
    _a_body_part_before, _a_period_of_their_own, _acts_on_the_speaker, _names_an_episode,
    _state_cue, _works_on_the_speaker, a_broken_heart_shape, BARE_DEFINITION, NOT_A_DEFINITION_HEAD,
    ASKS_ABOUT_A_PERSON, DEFINITION, MATH_WORDS, _has_any, SPEAKER, STATING_VERB, SAYS_HOW_THEY_ARE,
)
from .kinds_part_03 import (
    GOOD_WORD_BY_COMPARISON, _feeling_said_as_a_sound, _object_after, _said_of_the_speaker,
    _state_as_feeling, _state_of_a_person, cue_about_person, DETERMINERS,
)
from .kinds_part_04 import (
    _starts_with,
)
from .kinds_part_05 import (
    _about_bot_kind, TAIL_ASKS, TAIL_ASK_FILLER, A_FRAME_IN_FRONT, FRAME_NOT_A_SETUP,
    SETUP_CONNECTIVES, SETUP_MOST_WORDS, _says_nothing_but_the_floor, _asks_the_room, TAG_ENDINGS,
    TAG_RIGHT_NOT, _asks_the_bot, _tag_checks_a_fact, _tag_tells_a_plan, AFTER_COMPARATIVE,
    A_PERSON_AFTER, COMPARATIVE, COMPARISON, DESCRIBES, ASK_FOR_A_NAME, _asks_a_question_coming,
    _asks_for_tips,
)


def emotion_of(text):
    """The feeling the line names about a person, or None: "a mad day" is a busy one."""
    text = BETTER_OFF.sub(" ", text)
    text = NO_BETTER.sub("worse", text)
    text = GETTING_WORSE.sub(lambda match: match.group(1) + " worse", text)
    text = IDIOM_STATES.sub(" ", text)
    text = ABILITY_AT.sub(" ", text)
    for name, cues in EMOTION_WORDS.items():
        for cue in cues:
            state = _state_cue(cue)
            if state and not _state_of_a_person(text, state):
                continue
            if cue in BODY_STATE_CUES:
                if _a_body_part_before(text, cue) or _object_after(text, cue):
                    continue
            idiom = NOT_A_MOOD_THERE.get(cue)
            if idiom is not None and idiom.search(text):
                continue
            if cue in LABEL_ON_A_PERSON and _said_of_the_speaker(text, cue):
                continue
            if (cue in SELF_ONLY_CUES or cue in ALWAYS_SELF_ONLY or cue in THING_OR_PERSON_CUES
                    or cue in CONFUSED_SELF_ONLY
                    or cue in A_COMPARISON) and not _said_of_the_speaker(text, cue):
                continue
            if cue in THING_OR_PERSON_CUES and _laughed_off(text, cue):
                continue
            if (cue in PERIOD_CUES and A_PERIOD.search(text)
                    and not A_LIMIT_ABOUT_PEOPLE.search(text)
                    and (A_MONTH_PERIOD.search(text) or A_MONEY_SUBJECT.search(text))):
                continue
            if cue in SAID_AS_A_NEGATION and not denied(text, cue):
                continue
            # A good word that is ruled out is still the word the line carries: the sign comes
            # from `polarity`, and the name from here (README: "i am not happy about it" is
            # polarity -1 with emotion happy). So only a bad feeling is skipped when the line
            # denies it, because denying "sad" is not being sad.
            if name not in GOOD_EMOTION_NAMES and cue not in SAID_AS_A_NEGATION and denied(text, cue):
                continue
            if (name in GOOD_EMOTION_NAMES and GOOD_WORD_MISSING.search(text)
                    and not GOOD_WORD_COMPARED.search(text)
                    and not GOOD_WORD_BY_COMPARISON.search(text)):
                # A good word said to be missing is missed, not felt: the pool for a low is the
                # answer a friend gives to "i cant remember the last time i felt happy".
                return "sad"
            if cue_about_person(text, cue) or _names_an_episode(text, cue):
                return name
    acted = _acts_on_the_speaker(text)
    if acted:
        return acted
    if a_broken_heart_shape(text):
        return "sad"          # "my heart is broken" is the low said with the heart as the thing
    sounded = _feeling_said_as_a_sound(text)
    if sounded:
        return sounded
    # A thing doing something to the person: "work is stressing me out" names the feeling in
    # the verb, and the person it happens to is the speaker.
    worked_on = _works_on_the_speaker(text)
    if worked_on:
        return worked_on
    if _state_as_feeling(text):
        return "sad"
    # Last, and only for a line that has read as no mood at all, so nothing that already had a
    # reading can move: a day or a week the speaker had, told with a state word.
    for name, cues in EMOTION_WORDS.items():
        if name in GOOD_EMOTION_NAMES:
            continue
        for cue in cues:
            if cue in NOT_THE_SPEAKERS_DAY or cue in PERIOD_CUES:
                continue
            if denied(text, cue):
                continue
            if _a_period_of_their_own(text, cue):
                return name
    return None


def _about_bot(text, words, norm=()):
    """True when the line asks about the bot itself, not about something it was asked to do."""
    return _about_bot_kind(text, words, norm) is not None


def _asks_at_the_end(clause):
    """True when the last clause asks for the answer without a question word."""
    stripped = strip_leaders(clause) or clause
    if not stripped:
        return False
    if _opens_question(stripped):
        return True
    return bool(set(stripped) & TAIL_ASKS) and set(stripped) <= (TAIL_ASKS | TAIL_ASK_FILLER)


def the_setup(line):
    """The situation a line describes before the question it ends on, else None.

    "friends are coming for sunday lunch and one of them is vegan, what can i cook that everyone
    will eat" says the situation and then asks; the ask is what the line is about (it is
    `focus`) and the setup is what the answer has to hold to. Read whole, the situation's words
    are the ones a reply is found by, and the answer goes to the situation instead of the
    question: "my son has a football match on saturday and its freezing, what should he wear" is
    answered with the temperature a baby's room should be, because the only thing the line named
    that a card knows about is the freezing.

    Two questions in one line have no setup ("what is your name and how old are you"): the
    second is another ask, not the condition for the first.
    """
    clauses = [clause for clause in (line.get("clauses") or []) if clause]
    if len(clauses) < 2:
        return None
    ask_at = None
    for index in range(len(clauses) - 1, 0, -1):
        if _asks_at_the_end(clauses[index]):
            ask_at = index
            break
    if ask_at is None:
        return None
    before = clauses[:ask_at]
    if any(_opens_question(clause) for clause in before):
        return None
    if all(_says_nothing_but_the_floor(clause) for clause in before):
        return None
    # The situation's words are the ones a card is found by, so the courtesy or the frame in
    # front of it is not part of it: "hiya, quick one - my 14 year old wants her ears pierced" is
    # a question about the piercing, and "hiya" and "quick one" would only be noise in the search.
    setup = " ".join(" ".join(strip_leaders(clause) or clause) for clause in before)
    setup = A_FRAME_IN_FRONT.sub("", setup).strip(" ,-")
    if not setup:
        # Only the frame was there: "lol ok anyway, whats for dinner" says nothing to hold to.
        return None
    if len(setup.split()) > SETUP_MOST_WORDS:
        return None
    if FRAME_NOT_A_SETUP.match(" " + setup):
        return None
    if not set(setup.split()) - SETUP_CONNECTIVES:
        # "since, when have you been about": the words before the ask join it, they do not
        # describe anything the answer has to hold to.
        return None
    return setup


def _opens_question(clause):
    """True when a clause opens like a question ("is 8gb enough"), not like an order."""
    stripped = strip_leaders(clause) or clause
    if _asks_the_room(stripped):
        return True
    if not stripped or stripped[0] not in QUESTION_STARTS:
        return False
    if (len(stripped) > 2 and stripped[1] in NEGATIONS
            and stripped[1] not in SUBJECT_NEGATIONS
            and stripped[2] not in PRONOUNS):
        # "has not paid", "will not charge" deny a thing; "can't you come earlier" asks one
        return False
    if stripped[0] == "do" and len(stripped) > 1 and stripped[1] in QUESTION_WORDS:
        return False                      # "do what you can" is an order, not a question
    if (stripped[0] in YESNO_STARTS and len(stripped) > 1
            and _verb_form(stripped[1], stripped[0])):
        return False    # "will do", "were thinking of getting a cat": a verb, not a subject
    if len(stripped) > 1 and opens_without_subject(stripped, 0):
        return False    # "am off to bed", "were shattered", "have no idea"
    return True


def _asks_for_confirmation(norm):
    """True when the line ends by asking the other person to agree with it.

    The tag is not a question word, so the line used to read as news and got "Noted: ..."
    or "I'm listening" instead of an answer. Only the end of the line is read, and "right"
    needs a word in front that can end a statement: "im board right" is a tag, while
    "im doing everything right", "ur right" and "i cant do anything right" are not.
    """
    if len(norm) < 3 or norm[-1] not in TAG_ENDINGS:
        return False
    if (_opens_question(norm) or _asks_the_bot(norm) or _tag_tells_a_plan(norm)
            or not _tag_checks_a_fact(norm)):
        return False
    if norm[-1] == "right":
        # A word that is doing something is the complement, not a statement the tag agrees
        # with: "i keep getting the timing right", "nothing is going right", "turn right".
        # The base forms are in TAG_RIGHT_NOT; the -ing and -ed family is a rule.
        if norm[-2].endswith(("ing", "ed")):
            return False
        return norm[-2] not in TAG_RIGHT_NOT
    return len(norm) >= 4


def _wants_a_recommendation(norm, text):
    """Whether the words ask the bot to pick something out, rather than describe the speaker."""
    if set(norm) & COMPARATIVE and COMPARISON.search(" " + text + " "):
        return True                  # "which is better, tea or coffee" is picking, not reporting
    for index, word in enumerate(norm):
        if word not in COMPARATIVE:
            continue
        before = norm[index - 1] if index else ""
        after = norm[index + 1] if index + 1 < len(norm) else ""
        if after in A_PERSON_AFTER and not (
                after in ("man", "woman") and norm[index + 2:index + 3] == ["for"]):
            continue                 # "my best friend", "im the best man" name somebody
        if before not in DESCRIBES and after not in AFTER_COMPARATIVE:
            return True
    return bool(set(norm) & (RECOMMEND - COMPARATIVE))


# A thank you is said *for* something, and that something is what the bot has already given:
# "thanks for the advice", "cheers for the pointers", "thanks a lot for all your ideas". The
# advice word there is the object of "for", so it is not a request for one - but read as a
# request it turned a plain thank you into a question and the bot answered it with the search
# hedge. Only the words a gratitude "for" takes are the object, so a request of its own after
# the thanks is still an ask ("thanks, any advice for my sleep", "thanks for the tip, now how
# do i clean the oven").
GRATITUDE_OBJECT = frozenset("""a an the all any some your his her their our my that this these
    those lot lots loads much very so really again both few bit kind sort great good helpful
    useful nice lovely brilliant ever indeed awfully terribly truly too help support""".split())


# The words a thank-you uses to join one thing it is for to the next: "thanks for the help and
# the advice", "thanks for the tips, the pointers". None of them names an ask.
GRATITUDE_JOINERS = frozenset(["and", "plus", ",", "&"])


# The words that can open the thing a thank you is for but cannot carry on inside it: "thanks
# for the pointers, any suggestions for tomorrow" asks, and the comma is not even in `norm`, so
# without this the object walks over "any suggestions" and eats the ask. They are only asked
# about past the first word, so "thanks for any advice" still thanks.
GRATITUDE_ASK_AGAIN = frozenset("any some what how which more another".split())


TIP_WORDS = frozenset("tips hints pointers tip hint pointer".split())


COURTESY_WORD = frozenset(word for phrase in THANKS for word in phrase.split())


def _the_thing_a_thank_you_is_for(norm):
    """The (start, end) of the words a thank you's "for" takes, or None when it is not one.

    "thanks for the advice", "thanks a lot for the pointers", "thank you for the ideas": the
    words before the "for" are the courtesy itself and words that only measure it.
    """
    if not norm or not _starts_with(norm, THANKS):
        return None
    for at, word in enumerate(norm[:5]):
        if word != "for":
            continue
        if any(w not in COURTESY_WORD and w not in GRATITUDE_OBJECT for w in norm[:at]):
            continue                     # "thanks, any advice for my sleep": not a gratitude for
        end = at + 1
        while end < len(norm) and norm[end] in GRATITUDE_OBJECT | RECOMMEND | TIP_WORDS:
            if end > at + 1 and norm[end] in GRATITUDE_ASK_AGAIN:
                break                # "thanks for the tips any ideas for tomorrow" asks
            end += 1
        if end > at + 1:
            # The thing thanked for can be a list of them, so a joiner followed by more of the
            # same words stays inside the object. "thanks for the advice and how do i clean the
            # oven" stops at "and", because "how" is not one of those words.
            while end + 1 < len(norm) and norm[end] in GRATITUDE_JOINERS:
                run = end + 1
                while run < len(norm) and norm[run] in GRATITUDE_OBJECT | RECOMMEND | TIP_WORDS:
                    run += 1
                if run == end + 1:
                    break
                if run < len(norm) and norm[run] == "for":
                    break                # "thanks for the tips and any ideas for dinner" asks
                end = run
            return at, end
    return None


def _asks(norm, text):
    """What the line asks for, as a set of short labels."""
    thing = _the_thing_a_thank_you_is_for(norm)
    if thing:
        # A thank you is said for something, and that something names no ask of its own:
        # "thanks for the ideas" thanks the bot, where "thanks, any ideas for dinner" asks.
        # Everything outside the object still asks - "thanks for the tip, now how do i clean
        # the oven" is a question about the oven - so those words are what the labels come from.
        left = norm[:thing[0]] + norm[thing[1]:]
        return _ask_labels(left, " " + " ".join(left) + " ")
    return _ask_labels(norm, text)


# The figures in a line that are a date and not a quantity: "the 3rd of may", "3 may", "may 3",
# "on the 21st". They are taken out before a line is read for arithmetic, so a birthday is never a
# sum to work out (see `_ask_labels`).
A_DATE_FIGURE = re.compile(
    r"\b\d{1,2}(?:st|nd|rd|th)\b"
    r"|\b\d{1,2}\s+(?:of\s+)?(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b"
    r"|\b(?:january|february|march|april|may|june|july|august|september|october|november|"
    r"december)\s+\d{1,2}\b",
    re.I)


def _a_bare_definition(text):
    """True for a bare "what is X" that asks what the thing is, and False for the rest.

    The head word decides most of it (see NOT_A_DEFINITION_HEAD), and a possessive head - "what
    is peru's capital" - asks about somebody's thing rather than the meaning of a word.
    """
    found = BARE_DEFINITION.search(text)
    if not found:
        return False
    head = found.group(1).lower()
    if head.endswith(("'s", "\u2019s")) or re.search(r"\d", head):
        return False
    # The apostrophe is gone by the time the line is read, so "peru's capital" arrives as "peru s
    # capital": a lone "s" after the head is the possessive, and the line asks about a thing that
    # belongs to something rather than what a word means.
    if re.match(r"\s*s\b", text[found.end():]):
        return False
    return head not in NOT_A_DEFINITION_HEAD


def _ask_labels(norm, text):
    """The asks the line itself makes, gratitude already taken off."""
    asks = set()
    words = set(norm)
    if _asks_the_room(norm) and norm[1] in ASK_FOR_A_NAME:
        asks.add("recommend")
    if "how" in words:
        if "long" in words:
            asks.add("how_long")
        elif "much" in words or "many" in words:
            asks.add("how_much")
        elif "often" in words or "frequently" in words:
            asks.add("how_often")
        else:
            asks.add("how")
    for label in ("what", "why", "when", "where", "who", "which"):
        if label in words:
            asks.add(label)
    if _wants_a_recommendation(norm, text) or _has_any(text, RECOMMEND_PHRASES) \
            or _asks_for_tips(text, norm):
        asks.add("recommend")
    if _has_any(text, STEPS) or STEPS_WORD.search(text) or _asks_for_help(text):
        asks.add("steps")
    if _has_any(text, OPINION):
        asks.add("opinion")
    if _has_any(text, COMPARE) or words & {"vs", "versus"}:
        asks.add("compare")
    if not ASKS_ABOUT_A_PERSON.search(text) and (
            _has_any(text, DEFINITION) or _a_bare_definition(text)):
        asks.add("definition")
    # "the 3rd of may" is a date, not a sum: an ordinal, or a day of a month, names a position on
    # a calendar, and counting it as arithmetic made the birthday line ask for an amount. What is
    # left after the dates are taken out is the arithmetic in the line.
    digits = bool(re.search(r"\d", A_DATE_FIGURE.sub(" ", text)))
    if words & MATH_WORDS or "%" in text or (digits and ({"of", "each", "per", "split"} & words)):
        asks.add("maths")
    if _has_any(text, (" or ",)) and not two_ends_of_one_scale(text) \
            and not _turns_the_pair_down(text):
        asks.add("choice")
    if words & {"list", "ideas", "options", "examples", "suggest"}:
        asks.add("list")
    if words & {"write", "word", "rewrite", "draft"}:
        asks.add("write")
    if _asks_a_question_coming(norm, text):
        asks.add("question_coming")
    return sorted(asks)


# A line with no verb and no self in it that just names a thing and a place is a request for
# options, not news: "restaurants in edinburgh", "museums in rome", "things to do in lisbon with
# kids". The person is asking what to pick there. It is never a reply to the bot's last turn.
NOUN_REQUEST_MAX = 8


PLACE_WORD = frozenset("in at near around from to".split())


NOUN_REQUEST_SELF = frozenset("""i me my mine we our us myself your you it its he she they
    there here that this""".split())


VERBISH = frozenset("""is are was were am be been being have has had do does did done go goes
    going went gone plan planning planned visit visiting visited stay staying live living work
    working like love hate want need get got take took make made book booked fly flying drive
    driving rent rented see saw seen eat ate eaten drink drank cook cooked watch watched play
    played read come came coming think thought know knew say said tell told try tried start
    started stop stopped leave left move moved should would could will can may might must""".split())


# After an auxiliary a bare verb or a progressive form is the verb of the clause, not the thing
# it is about: "will do", "might do that", "were thinking of getting a cat". A subject is a
# pronoun, a determiner or a noun, so a question never puts one of these right after the
# auxiliary. Words that are as often nouns are left out ("is work busy", "is help available",
# "is cooked chicken still ok"): the -ed forms are adjectives there, and the bare ones are
# things.
BARE_VERBS = frozenset("""do give get go try keep sort call tell know feel be been have wait
    stop start find leave come put use take see say think love like want""".split())


VERB_FORMS = BARE_VERBS | frozenset(
    stem[:-1] + "ing" if stem.endswith("e") else stem + "ing"
    for stem in VERBISH - {"is", "are", "was", "were", "am", "be", "been", "being"}
    if len(stem) > 2 and stem.isalpha())


# The same verbs said of a thing rather than by the person: "the heating comes on", "it settles at
# the top", "the pump catches". A report about the thing is written that way, and the -ed and -ing
# tests miss it, so the word was read as the part of the answer the follow-up named - "its a
# banging sound when the heating comes on" after the banging card came back "Same for comes: ...",
# a lead-in about a word nobody was talking about. The tense of a verb is the same verb.
def _third_person(stem):
    if len(stem) > 2 and stem.endswith("y") and stem[-2] not in "aeiouy":
        return stem[:-1] + "ies"
    if stem.endswith(("s", "sh", "ch", "x", "z", "o")):
        return stem + "es"
    return stem + "s"


VERB_THIRD = frozenset(
    _third_person(word) for word in (VERBISH | BARE_VERBS)
    if word.isalpha() and word not in {"is", "are", "am", "be", "been", "being"})


# An -ing word after a present or a modal auxiliary is the subject of the question, not the
# clause's verb: "is cooking with gas cheaper", "will cooking it longer make it tender" and
# "is running water safe to drink" all ask something. Only a past or plural auxiliary leaves the
# person out, which is where the progressive verb shows up: "were driving up to scotland".
PAST_AUX = frozenset("""was were been had has have""".split())


def _verb_form(word, auxiliary=""):
    """True when this word is a verb here rather than a thing the question is about."""
    if word.endswith("ing") and auxiliary not in PAST_AUX:
        return False
    return word in VERB_FORMS


def noun_phrase_request(line):
    """True for a verbless line that names a thing and a place: a request for options there."""
    words = [word for word in line["norm"] if word]
    if not words or len(words) > NOUN_REQUEST_MAX or line["signals"]["question_mark"]:
        return False
    if any(word in NOUN_REQUEST_SELF for word in words):
        return False
    # An infinitive is not a verb here: "things to do in edinburgh" asks what to do there.
    if any(word in VERBISH and words[index - 1:index] != ["to"]
           for index, word in enumerate(words)):
        return False
    return len(words) >= 2 and any(word in PLACE_WORD for word in words)


# An interest the person has taken up, said in the shapes that carry no other clue: "im into
# running", "im really into baking at the moment", "ive got into yoga", "im getting into
# gardening". The knowledge base already answers the asking shape ("i want to get into running"
# gets the run-walk plan) because the word "get into" is in its key, but it cannot take the bare
# "into": "shes 30 and into running" is a detail about somebody else, not a request for a plan.
# So the reading says whose interest it is and what it is in, and a module can answer the
# person's own without widening the word.
INTEREST_HEAD = re.compile(
    r"^\W*(?:i\s*m|im|i am|i\s*ve|ive|i have|we\s*re|were|we are|i\s+got|we\s+got)\s+"
    r"(?:really\s+|so\s+|very\s+much\s+|very\s+|well\s+|quite\s+|now\s+|also\s+"
    r"|totally\s+|still\s+)?"
    r"(?:(?:getting|got|started)\s+(?:back\s+)?|back\s+)?(?:into|in to)\s+(?P<thing>[a-z' -]+?)\s*[.!]*$",
    re.I)


# The thing has to be an activity, not a person ("im into him"), a fix they are in ("im into
# debt") or a phrase that is not an activity at all ("i got into a fight", "into trouble").
INTEREST_NOT = frozenset("""not a an the this that these those some any my our his her their your
    him her them us me you it fight fights argument arguments row rows trouble debt debts
    hospital bed prison it him""".split())


# How often or when, said after the activity ("im into netball on wednesdays", "im into parkrun
# every saturday"): the day is when they do it, not part of its name, so the reply names the
# activity alone. A day that is the activity keeps its line ("im into sunday roasts" is cooking).
INTEREST_TAIL = re.compile(
    r"\s+(?:at the moment|right now|now|these days|lately|recently|a lot|lots|again"
    # "im into baking too" is into baking: the "too" belongs to the line, not to the name of
    # the thing, and a reply that says "the baking too" reads as if somebody else were baking.
    r"|too|as well|also"
    r"|on\s+(?:mon|tues|wednes|thurs|fri|satur|sun)days?"
    r"|every\s+(?:day|week|weekend|morning|evening|night|"
    r"mon|tues|wednes|thurs|fri|satur|sun)days?"
    r"|at\s+the\s+weekend|after\s+work|in\s+the\s+evenings?)$", re.I)


# "ive got into yoga" and "im getting into gardening" are somebody starting out; "im into
# running" is somebody already at it. The two want different answers - the plan for a beginner
# against the tip for the thing they do - so the reading keeps them apart (`shape`).
STARTED_OUT = re.compile(r"\b(?:got|getting|started)\s+(?:back\s+)?into\b", re.I)


# Going back to something they used to do is a taking up of its own: "i got back into chess"
# wants "what got you back into it", not "what made you start", which reads as if they never had.
BACK_INTO = re.compile(r"\bback\s+into\b", re.I)


def taking_up(line, read=None):
    """The activity the person is into, else None: `{"text", "words", "shape"}`.

    `text` is the activity as typed ("im really into baking at the moment" -> "baking"), `words`
    the same split up for matching, and `shape` is "started" for somebody beginning it ("ive got
    into yoga", "im getting into gardening") and "doing" for somebody already at it ("im into
    running").
    """
    text = str((read or {}).get("clean") or line.get("text") or "")
    # The apostrophe is dropped here only, so "i'm", "i’m" and "im" are one shape and the word
    # after "into" is read as typed.
    text = re.sub(r"['’]", "", text).strip()
    if not text or " not " in " %s " % text.lower():
        return None
    if re.match(r"\W*(?:am|is|are|was|were)\s+(?:i|we|you|they|he|she)\b", text, re.I):
        return None  # "are you into running" asks about them, not the person telling you
    match = INTEREST_HEAD.match(text)
    if not match:
        return None
    thing = INTEREST_TAIL.sub("", match.group("thing").strip(" .,!?")).strip()
    words = thing.split()
    if not words or len(words) > 4:
        return None
    if words[0] in INTEREST_NOT or (len(words) > 1 and words[1] in INTEREST_NOT):
        return None
    thing = thing.lower()
    if not thing:
        return None
    return {"text": thing, "words": words,
            "shape": "started" if STARTED_OUT.search(text) else "doing",
            "back": bool(BACK_INTO.search(text))}


# A clause that opens like a question can be the end of the sentence instead, when the clause
# before it only names the thing: "my cat, milo, is shy with visitors" says how the cat is, and
# "the boiler, which is old, keeps cutting out" says what the boiler does. The commas split the
# name of the thing off from what is said about it, and neither half is a question. A greeting
# or a "sorry" in front of a real question is not a subject, so "hi, is the shop open" and
# "sorry, where is the station" still ask, and so does "my car, is the battery dead": there the
# clause after the comma is the person's question about the car.
WH_CONTINUES = frozenset("which who whom whose that".split())


NOT_A_SUBJECT = frozenset(
    [word for phrase in GREETINGS + THANKS + FAREWELLS for word in phrase.split()]
    + list(ACK) + list(LAUGH)
    + "sorry please oh ah well right yes no yeah yep nope hmm and so but also just".split())


SUBJECT_OF_ITS_OWN = PRONOUNS | frozenset(
    """anyone someone everyone nobody anybody somebody one""".split())


def _bare_subject(clause):
    """True when a clause only names the thing: "my cat", "the boiler", "milo".

    A clause with a verb in it says something about the thing, so a question after it is the
    person's own question ("my back hurts, can i take ibuprofen").
    """
    if not clause:
        return False
    for word in clause:
        if word in VERBISH or (len(word) > 3 and word.endswith(("ed", "ing"))):
            return False
    first = clause[0]
    if first in DETERMINERS:
        return True
    return len(clause) == 1 and first not in NOT_A_SUBJECT


def _continues_the_sentence(clauses, index):
    """True when this clause only finishes the sentence the clause before it started."""
    if index < 1 or not _bare_subject(clauses[index - 1]):
        return False
    clause = clauses[index]
    if any(word in SUBJECT_OF_ITS_OWN for word in clause[1:3]):
        return False                       # "my car, does it start"
    if clause[0] in WH_CONTINUES:
        return True                        # "the boiler, which is old"
    if clause[0] not in YESNO_STARTS:
        return False
    # "my cat, milo, is shy with visitors": a name sits between the noun phrase and what is
    # said about it. Without the name there is nothing for the clause to belong to.
    return index >= 2 and _bare_subject(clauses[index - 2])


# A word that turns the feeling after it the other way: "not fine" is not fine, "not bad" is
# good. Checked a few words back, so "i am really not fine" and "im not feeling great" count.
NEGATORS = frozenset("""not no never neither nor hardly barely cannot cant dont doesnt didnt
    isnt arent wasnt werent wont wouldnt shouldnt couldnt aint nothing""".split())


# A negator turns the next feeling word and nothing else, and it reaches over the words that
# only say how much ("not really fine", "not bad at all"). Any other word in between ends it,
# because there the negator belongs to that word and not to the feeling: "i cant stop crying"
# and "i cant help feeling sad" are more of the feeling, not less, and "she shouldnt be living
# alone" is a worry, not a comfort.
NEGATION_SKIP = frozenset("""really very so too much quite pretty true honestly actually
    totally completely absolutely seriously still even at all bit little kind sort feeling
    feel felt a an the""".split())


# A feeling word the line takes back. "im not stressed", "im not in pain", "im not having a
# panic attack": the negator reaches over the words that only say how, how much or which one
# ("not really sad", "not having a panic attack", "not in any pain"), and over nothing else -
# "i cant stop crying" is still the crying. Read as the state itself, a denial was the opposite
# line: "im not stressed" got the good-news line and "im not having a panic attack" got the
# panic card.
DENY_BETWEEN = NEGATION_SKIP | frozenset("""in at on for under any more most all about much
    having had havent been being be am is are was were got get getting a an the""".split())


DENY_BEFORE = re.compile(
    r"\b(?:" + "|".join(sorted(NEGATORS)) + r")\b"
    r"(?:\s+(?:" + "|".join(sorted(DENY_BETWEEN)) + r")){0,4}\s*$", re.I)


def denied(text, cue):
    """True when this feeling word is the thing the line rules out, not the state it is in."""
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        if DENY_BEFORE.search(text[:match.start()]):
            return True
    return False


def _a_state_of_the_speaker(norm, index):
    """True when the word at `index` is said about how the speaker is: "im ok", "im not ok",
    "we are doing ok". The words in between are the verb, a negator and the amount."""
    verb = False
    back = index - 1
    while back >= 0 and index - back <= 4:
        word = norm[back]
        if word in SPEAKER:
            return verb
        if word in STATING_VERB:
            verb = True
        elif word not in NEGATORS and word not in NEGATION_SKIP:
            return False
        back -= 1
    return False


# Someone in authority wanting a word is a kind of line of its own. "my sons teacher wants a
# word", "the council have written to me", "hr want to see me on friday" are not trouble (nothing
# has gone wrong yet), not news worth congratulating and not a fact to file away; the person is
# waiting to find out what it is about, and every one of them came back as an echo of the line.
# So the reading names the shape: someone who can call you in, and what they want (a word, a
# meeting, a letter, a phone call).
SUMMONS_WHO = frozenset("""
teacher teachers head headteacher headmaster headmistress school nursery college tutor lecturer
boss manager supervisor employer hr payroll council housing landlord lettings letting agency
dwp benefits tax hmrc bank gp doctor surgery dentist hospital consultant midwife police
probation court solicitor immigration ofsted office
""".split())


# Who can call you in often takes two words.
SUMMONS_WHO_PHRASES = ("social services", "health visitor", "home office", "tax office",
                       "job centre", "jobcentre", "letting agent", "letting agents",
                       "the council", "the school", "the office", "the bank", "the head")


# What they ask for: a word with you, not a job for you. "my boss wants me to work saturday" is
# a request to the person and gets no letter-and-meeting line.
SUMMONS_SEE = ("a word", "a quick word", "to see", "to talk", "a chat", "a meeting", "to meet",
               "to discuss", "to speak", "to come in", "asked me in", "called me in",
               "for a chat", "an appointment", "to interview")


SUMMONS_WRITTEN = ("written to me", "wrote to me", "sent me a letter", "sent a letter",
                   "a letter from", "letter arrived", "letter came", "in writing")


# A letter named before the who is a summons only when it is a letter that came to the speaker.
# "i need a letter from my doctor" and "i asked for a letter from the bank" are the speaker
# asking for one, and "i sent a letter to the council last week and no reply" is their own letter
# going out: telling any of those how to answer the letter is the wrong direction.
LETTER_RECEIVED = frozenset("""got received had came come arrives arrived""".split())


LETTER_ASKED_FOR = frozenset("""need needs wanted want wants asked ask asking sent send
    sending wrote write writing expecting waiting chase chased requested requesting
    wanting""".split())


# A letter that came to somebody else is not a summons to the speaker: "my neighbour got a
# letter from the council", "my wife got a letter from the school". The possessive in front of
# the received letter names whose it is, and it is the speaker's own only when it names the
# letter itself - "i got my letter from the council" is still theirs.
LETTER_SOMEONE_ELSES = frozenset("my his her their our".split())


LETTER_ITSELF = frozenset("letter letters note email reply".split())


SUMMONS_RANG = ("rang me", "phoned me", "called me", "left a message", "rang about",
                "phoned about", "called about", "rang the house")


# A call that has already happened is not a call to make: "the bank rang me back and said it was
# fine", "the council rang me today", "my boss rang me and told me not to worry". The ring-back
# line is right for a call to return, so the words that date the call take the shape away.
SUMMONS_CALL_DONE = frozenset("""back today yesterday tonight morning afternoon evening
    earlier already just then""".split())


SUMMONS_SAID = frozenset("said says told tells explained apologised apologized asked confirmed""".split())


# Someone who "has a meeting" or "has an appointment" has their own diary, not a want to see you:
# "my boss has a meeting with hr" and "the school has an appointment slot" are not summonses. So
# possession is not wanting, and the wanting verbs are the ones that name a person being called in.
SUMMONS_WANTS = ("want", "wants", "wanted", "needs", "needed", "asked", "asking",
                 "would like", "requested", "told me")


# The words that make it someone asking for you rather than you asking for them: whoever is
# wanting or writing has to be named before them. "the doctor wants to see me" is a summons,
# "i want to see a doctor" is the speaker's own plan.
SUMMONS_VERB = frozenset(SUMMONS_WANTS) | frozenset("""written wrote rang phoned called sent
    letter message""".split())


# "the letting agent still hasnt called me back" is a complaint about a call that never came.
SUMMONS_NOT = frozenset("""not hasnt havent didnt doesnt dont wont never no still yet""".split())


def _asks_for_it_rather_than_got_it(norm):
    """Whether the asking or sending word comes before the letter that arrived.

    "i asked for a letter from the bank" is the speaker asking for one, so advice on how to
    answer it is the wrong direction. But a letter that arrived can ask for something itself -
    "i got a letter from the council asking me to call" is still a letter to them, and the word
    that names the asking sits after the word that says it arrived. So the veto only reaches as
    far as the received word, the same way `_a_letter_someone_else_got` places the possessive.
    """
    arrived = next((index for index, word in enumerate(norm)
                    if word in LETTER_RECEIVED), None)
    if arrived is None:
        return False
    return any(word in LETTER_ASKED_FOR for word in norm[:arrived + 1])


def _a_letter_someone_else_got(norm, verb):
    """Whether a possessive in front of the letter names a person other than the speaker.

    "my neighbour got a letter from the council" and "my wife got a letter from the school" are
    letters to them, not to the person writing, so there is nothing for them to answer. The
    possessive has to sit before the letter word to count, and "i got my letter from the
    council" names the letter itself, so that one keeps its summons.
    """
    for index, word in enumerate(norm[:verb]):
        if word in LETTER_SOMEONE_ELSES:
            after = norm[index + 1] if index + 1 < len(norm) else ""
            if after and after not in LETTER_ITSELF:
                return True
    return False


def summons_of(norm, kind):
    """{"who", "shape"} when the line is someone wanting a word with the speaker, else None.

    `who` is the office or person who can call them in, `shape` is what they asked for:
    "see" (wants a word, a meeting), "written" (a letter) or "rang" (a phone call). A question
    is left alone: "what do i do if the council write to me" is asking for advice, not news.
    """
    if not norm or kind == "question":
        return None
    words = set(norm)
    who = None
    at = None
    for phrase in SUMMONS_WHO_PHRASES:
        if phrase in " ".join(norm):
            who = phrase
            at = norm.index(phrase.split()[0])
            break
    if who is None:
        who = next((word for word in norm if word in SUMMONS_WHO), None)
        at = norm.index(who) if who else None
    if who is None:
        return None
    # Whoever wants the word has to be named before the wanting, and it cannot be a call that
    # never came: see SUMMONS_VERB and SUMMONS_NOT.
    # The verb that carries the asking, not the "has" in front of it: the negator to look for
    # sits before "written" ("the bank hasnt written to me"), so the window has to start there.
    verb = next((index for index, word in enumerate(norm)
                 if word in SUMMONS_VERB and word not in ("has", "have")), None)
    if verb is None:
        verb = next((index for index, word in enumerate(norm) if word in SUMMONS_VERB), None)
    joined = " " + " ".join(norm) + " "
    # A letter is named before the who as often as after it ("i got a letter from the council",
    # "a letter came from the school"), and there the who follows the one word that carries the
    # asking. Only a letter may be read that way: "the council want a word" said the other way
    # round would let "i want to see the doctor" through.
    letter_first = (verb is not None and at > verb
                    and any(phrase in joined for phrase in SUMMONS_WRITTEN)
                    and any(word in LETTER_RECEIVED for word in norm)
                    and not _asks_for_it_rather_than_got_it(norm)
                    and not _a_letter_someone_else_got(norm, verb))
    if verb is None or (at > verb and not letter_first):
        return None
    if any(word in SUMMONS_NOT for word in norm[max(0, verb - 3):verb]):
        return None
    if letter_first or any(phrase in joined for phrase in SUMMONS_WRITTEN):
        return {"who": who, "shape": "written"}
    rang = next((phrase for phrase in SUMMONS_RANG if phrase in joined), None)
    if rang:
        # The words after the ring decide whether it is a call to make or one that came:
        # "school rang about my lad" is open, "the bank rang me back and said it was fine" is not.
        gap = joined.split(rang, 1)[1].split()[:3]
        if not set(gap) & SUMMONS_CALL_DONE and not set(gap) & SUMMONS_SAID:
            return {"who": who, "shape": "rang"}
    if not words & set(SUMMONS_WANTS):
        return None
    if any(phrase in joined for phrase in SUMMONS_SEE):
        return {"who": who, "shape": "see"}
    return None


def _said_to_somebody(norm, index):
    """True when this word closes a short line as the person it is said to.

    "thanks love", "morning pet", "cheers duck" and "night night love" end with a name for the
    person, and the line above it is one of the ones people say to somebody: a thanks, a
    greeting, a goodbye, a yes or a no. Anything else keeps its feeling word ("i love it",
    "theres no love between them", "i love").
    """
    if index != len(norm) - 1 or not 2 <= len(norm) <= 3:
        return False
    return norm[0] in ADDRESSED_LINES


# "an upset stomach" is not an upset person. `upset`, `bad` and `sick` are feelings when they
# stand on their own, and the name of what is wrong with a stomach when a stomach follows them,
# so the line is a body complaint and not a mood: the warm "what would make today a bit easier"
# line was the answer to "i have an upset stomach" while the rehydration advice sat unread.
STOMACH_WORDS = frozenset("""stomach stomachs tummy tummies belly bellies gut guts bowel bowels
    insides""".split())


# Only "upset" takes the body: "a bad stomach" and "a bad back" name how bad it is, which is a
# complaint and stays a bad line, while "upset" on its own is a mood about something else.
BODY_STATE_WORDS = frozenset("upset".split())


def _a_body_not_a_mood(norm, index):
    """True when the feeling word at `index` is naming what is wrong with the stomach."""
    forward = norm[index + 1] if index + 1 < len(norm) else None
    return forward in STOMACH_WORDS


# The same question handed back: "not bad, and you?", "im fine thanks, yourself".
BACK_AT = frozenset("you yourself u urself ya".split())


# "and you" and "about you"; not "to you" or "of you", which are the object of the line's own
# verb ("i miss talking to you", "thinking of you").
BACK_JOIN = frozenset("and about".split())


# "what about you", "how about you": the question coming back on its own.
BACK_ASKING = frozenset(("what", "how"))


# "me and you" and "you and me" are one subject, not a question back.
BACK_NOT_A_SUBJECT = frozenset("me us him her them i we my our your".split())


# What people put in front of the "yourself" they are handing back: how they are and the thanks
# that goes with it. No verb is in here, so "i love you" keeps its own reply, and "thank" is out
# because "thank you" is a thank-you on its own.
BACK_AFTER = frozenset("""thanks cheers ta ok okay alright fine good great well grand sound
    chill brill mint content lovely nice brilliant wonderful perfect amazing fantastic happy glad
    relaxed calm not bad tired rough meh shattered knackered wrecked awful terrible so very
    really doing feeling mate man
    complain same always
    working work busy off home out just finishing finishing up sorted done""".split())


def _asks_what_was_meant(text):
    """True when the whole line asks what the bot's own last answer meant.

    "what do you mean", "what does that mean", "how do you mean it" and the half a dozen ways
    people type the same question ("wot u mean", "wdym", "whatcha mean", "whaddya mean by
    that") name nothing of their own: they point at the line just given. The knowledge base read
    them as a follow-up on the subject of the last answer and took the word "mean" for the thing
    named, so after "my tomato plants have blight" the person got "The same goes for the wot u
    mean: cut off and bin the affected leaves" - their own slip said back at them as the thing
    being asked about, and the composer's own reply ("Just this: Brown-black patches ...") was
    the right one all along.

    The spellings are read in one place already, by the reply that answers this question
    (`bot/memory/meant.py::MEAN`), so this borrows that rule rather than keeping a second list
    that falls behind it. A thing named after "mean" is not this reading: "what does the boiler
    pressure mean", "what does it mean to be a good friend" and "what does mean reversion mean"
    are questions about a thing, and their card keeps the turn.
    """
    asked = str(text or "").strip()
    if not asked:
        return False
    from ..memory import meant

    return bool(meant.MEAN.match(asked))


# "what does that mean for my mortgage": the meaning is being applied to a thing of theirs. The
# thing is the question when it has just been talked about ("... for my pay" after a payslip),
# and it is a question of its own when it has not - see
# `bot/understanding/__init__.py::_the_meaning_is_applied_to_what_was_said`.
MEANT_APPLIED_TO = re.compile(r"\bfor\s+(?:my|our)\s+([a-z'\u2019-]+)", re.I)


def _asks_back(norm):
    """True when the line ends by handing the question back to the bot.

    "not bad, and you?", "im fine thanks, yourself", "good thanks, u?" answer how the person is
    and ask the bot the same thing in one breath. The reading called the whole line news about
    them, so the reply said neither how the bot was nor took the question: "im fine thanks,
    yourself" was answered "Thanks for telling me - I'm here if you want to dig into any of
    that", which answers neither half.

    Only the end of the line counts, and the "you" has to be a question rather than the object
    of the line's own verb: "i love you", "is it ok with you", "i miss talking to you",
    "thanks, youre alright you" and "i saw your mum and you" are none of them questions back.
    """
    words = [word for word in norm if word]
    if len(words) < 2 or words[-1] not in BACK_AT:
        return False
    # "and you?", "what about you", "how about you": the question back is the whole line, with
    # nothing about the person in front of it.
    if (len(words) == 2 and words[0] in BACK_JOIN) or \
            (len(words) == 3 and words[0] in BACK_ASKING and words[1] in BACK_JOIN):
        return True
    # "me and you" is one subject, not a question back.
    if len(words) > 2 and words[-3] in BACK_NOT_A_SUBJECT:
        return False
    # "thanks, youre alright you": the last "you" is a reprise of the one in front of it.
    if any(word in BACK_AT or word in {"youre", "your"} for word in words[:-1]):
        return False
    if words[-2] == "about" and not any(word in BACK_ASKING for word in words[:-2]):
        # "im worried about you", "im sad about you", "im confused about you": the "you" is
        # what the feeling is about, not the question handed back. An asking word anywhere in
        # front of it makes it a question back ("im skint, what about you"), and the join list
        # cannot tell the two apart on its own: the emotion in front of the "about" made every
        # worried-about-you line read as "im fine, thanks for asking after me".
        return False
    if words[-2] in BACK_JOIN:
        # "not bad, and you?": something has to be said about how they are in front of the join,
        # in the sign the line carries or in a feeling word of its own ("im fed up, and you",
        # which carries no sign either way), or in a word that says how they are without a sign
        # at all: "thanks, and you?", "cheers, and you", "same as always, and you". The reprise
        # guard above has already turned away the lines whose "you" is not a question, so the
        # words in front of the join here are about the person. "i saw your mum and you" keeps
        # what it had because of the "your".
        return (_polarity(norm) != 0 or emotion_of(" ".join(words)) is not None
                or any(word in BACK_AFTER for word in words[:-2]))
    # "im fine, you?" and "thanks, yourself": no joining word, so the word in front has to be
    # one of the words for how they are. "i love you" ends the same way and is not on offer.
    return words[-2] in BACK_AFTER


def says_how_they_are(norm):
    """True when the line says how the speaker is with a word that is also another thing.

    "im grand", "im sound thanks", "im chill": the reading has to see a feeling there, or the
    line reads as news and the bot answers a bare "im chill" with "Say more if it helps".
    "the sound of the boiler" and "the content of the email" are the other thing, so the word
    only counts when it is said about the person.
    """
    return any(word in SAYS_HOW_THEY_ARE and _a_state_of_the_speaker(norm, index)
               for index, word in enumerate(norm))


# A thing said to be a joke, a nightmare, a shambles. The noun is a verdict on the thing, not a
# request: "my landlord is a joke" is a person with a problem, and it was answered with a punchline
# because the line had the word "joke" in it and nothing said the word was the verdict. "it was a
# joke" is left alone - the subject is a pronoun, so the person is saying they were kidding.
VERDICT_NOUNS = frozenset("""joke nightmare disaster shambles mess farce ripoff con
    circus zoo mockery sham travesty letdown disappointment pain drag headache minefield
    slog waste fiasco scandal pantomime horror""".split())


COPULAS = frozenset("is are was were am be being been becomes became".split())


# The words that can sit between the copula and the verdict and only say how much: "a complete
# joke", "a total shambles", "a bit of a nightmare" (read from the verdict back to the copula).
VERDICT_FILLER = frozenset("""a an the total complete absolute utter right proper real massive
    huge bloody bit of on one big fat""".split())


# The same verdict as an adjective: "my landlord is useless" is the complaint "my landlord is a
# joke" makes, and it read as no feeling at all, so the line got "Got it. Is there anything you'd
# like a hand with?" and the person had to say it again. Only the verdicts are here. The state of
# a thing ("broken", "dead", "knackered", "stuck") has its own how-to-fix answer and keeps it, and
# "awful"/"terrible" already carry a feeling that the pools they reach are built for.
VERDICT_ADJECTIVES = frozenset("""useless pointless hopeless rubbish crap shit shite garbage
    trash pathetic""".split())


# A pronoun subject is the person talking about what they said or did, not a thing they are
# complaining about: "it was a joke", "that was a disaster" (a burnt cake, not a complaint).
PRONOUN_SUBJECT = frozenset("it that this there he she they we i you".split())


# A subject that asks names nothing: "what is a joke", "who is a nightmare" are questions about
# the words, and read as a verdict they lose their answer ("what is a joke" told one, and stopped).
ASKING_SUBJECT = frozenset("""what which who whom whose how why when where whatever whoever
    whichever whenever wherever""".split())


# A period of time said to be rubbish is a report of a mood rather than a thing to be put right:
# "the week was rubbish" already gets the question that helps ("what has made it like that"), and
# taking it as a verdict loses that question.
NOT_A_THING = frozenset("""week weekend day month year morning evening night afternoon term
    shift holiday trip time""".split())


def a_bad_verdict(norm, index):
    """True when the word at `index` is a verdict on a thing named before it: "my job is a joke"."""
    if index >= len(norm) or (norm[index] not in VERDICT_NOUNS
                             and norm[index] not in VERDICT_ADJECTIVES):
        return False
    back = index - 1
    while back >= 0 and norm[back] in VERDICT_FILLER:
        back -= 1          # "a complete joke", "a bit of a nightmare"
    if back < 0 or norm[back] not in COPULAS:
        return False
    subject = back - 1
    if (subject < 0 or norm[subject] in PRONOUN_SUBJECT or norm[subject] in ASKING_SUBJECT
            or norm[subject] in COPULAS or norm[subject] in NOT_A_THING):
        return False
    return True


def verdicts_a_thing(clean):
    """True when the line calls something a joke, a nightmare, a shambles.

    Read by the module that hands out jokes, and by the composer: "my landlord is a joke" has the
    word in it and is a person with a problem, and a punchline under it is the bot not reading the
    line at all. The sentence is tidied the way the reading tidies it, so "the trains are a total
    joke" counts.
    """
    text = " ".join(str(clean or "").lower().replace("\u2019", "'").replace("'", "").split())
    norm = [word for word in (re.sub(r"[^a-z0-9]+", "", part) for part in text.split()) if word]
    return any(a_bad_verdict(norm, index) for index in range(len(norm)))


def _polarity(norm):
    """-1, 0 or 1 for the feeling the line carries, with a negation turning it the other way.

    "im not fine", "not feeling great" and "im not ok" carry a bad feeling even though every
    feeling word in them is a good one, and "not bad" carries a good one. A line with words
    both ways ("tired but happy") stays 0.

    A negator turns the next feeling word only, so "i cant stop crying" and "i cant help
    feeling sad" stay bad: there the negated verb is not about the feeling. "ok" counts only
    as somebody's state ("im ok"), because on its own it is an acknowledgement or a question
    about permission.
    ''worry'' is left out on purpose: "should i worry about my knee" is a question about
    whether to worry, not a line with a bad feeling in it.
    """
    score = 0
    negated = False
    for index, word in enumerate(norm):
        if word in NEGATORS:
            negated = True
            continue
        if word in TERMS_OF_ADDRESS and _said_to_somebody(norm, index):
            negated = False
            continue
        if word in OK_WORDS or word in SAYS_HOW_THEY_ARE:
            feeling = 1 if _a_state_of_the_speaker(norm, index) else None
        elif word in POSITIVE:
            feeling = 1
        elif word in NEGATIVE:
            feeling = (-1 if word not in BODY_STATE_WORDS or not _a_body_not_a_mood(norm, index)
                       else None)
        elif a_bad_verdict(norm, index):
            # "my landlord is a joke" carries the complaint whatever the word is worth elsewhere
            # in the line: the noun is what they think of the thing they named.
            feeling = -1
        else:
            feeling = None
        if feeling is None:
            if word not in NEGATION_SKIP:
                negated = False
            continue
        score += -feeling if negated else feeling
        negated = False
    return (score > 0) - (score < 0)


def _thanks_still_asks(norm):
    """True when a thanks is followed by an ask that has no question word of its own.

    A person who thanks the bot and then asks for advice on something often writes no question
    word at all: "thanks, any tips for a cold". The advice word is the ask there, while in
    "thanks for the advice" the same word is only what they are thanking the bot for.
    """
    words = list(norm)
    for index, word in enumerate(words):
        if word not in THANKS_ASK_WORDS:
            continue
        back = words[index - 1] if index else ""
        if back in GIVEN_ADVICE:
            continue            # "thanks, no need": a comment, not an ask
        return True
    for index, word in enumerate(words):
        if word not in THANKS_ASK_NOUNS:
            continue
        back = words[index - 1] if index else ""
        if back in GIVEN_ADVICE:
            continue            # "for the advice on my back": the advice was already given
        if (index + 2 < len(words) and words[index + 1] in THANKS_ASK_PREPS
                and words[index + 2].isalpha()):
            return True
    return False
