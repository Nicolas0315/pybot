"""Part 6 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import copy
import re

from ..compose import badnews, fallback
from ..compose import onscreen
from ..memory import you

from ..memory import you

from ..memory import meant
from .chat_part_01 import (
    GREET_CORE, GREET_FILLER, THANKS_CORE, THANKS_FILLER, THANKS_LOOSE, ACK_WORDS, NO_WORDS,
    BYE_FILLER, BYE_TIME, BYE_VERB,
)
from .chat_part_03 import (
    BODY_AT_THOUGHT, BODY_FEELING_SHAPE, BODY_FEELING_WORDS, BODY_PART_FEELING, BUG_NAMED,
    SYMPTOM_IN_LINE, THOUGHT_UNNAMED, POSITIVE, FEELINGS, NOT_WORDS,
)
from .chat_part_04 import (
    _the_kind_of_worry, WORRY_ABOUT_THING, WORRY_EVENT, WORRY_PERSON, WORRY_WHEN,
)
from .chat_part_05 import (
    _NOTHING_MUCH_BETWEEN, _tokens,
)


def _body_is_a_feeling(clean):
    """The feeling a body word in the line is carrying, or None when the body is the subject.

    One reading for the three places that need it: the illness pool stands down, the feeling
    pools take the line up, and the arbiter is told the line has been read whole, so a recipe or
    a stomach entry cannot win it on a word.
    """
    text = str(clean or "")
    if BUG_NAMED.search(text):
        return None
    if SYMPTOM_IN_LINE.search(text):
        # A body that is also reporting something real keeps the answer it can act on.
        return None
    if LOSS.search(text) or badnews.reads_as_someones_death(text):
        # "my dad died and i feel sick with guilt" is a bereavement, and the grief pools are
        # written for it: guilt turning up in grief is answered there, not here.
        return None
    for pattern in (BODY_FEELING_SHAPE, BODY_PART_FEELING):
        found = pattern.search(text)
        if found:
            said = (found.groupdict().get("feeling") or "").strip()
            return _the_kind_of_worry(BODY_FEELING_WORDS.get(said, "worry"), text)
    found = BODY_AT_THOUGHT.search(text)
    if found:
        pointed_at = (found.group("object") or "").strip()
        if not pointed_at or pointed_at in THOUGHT_UNNAMED:
            return _the_kind_of_worry("worry", text)
    return None


# "do" carries no subject of its own, so a line whose verb around "much" is a form of it is still
# the answer to "what are you up to" - with or without a "not": "didnt do much today",
# "havent done much today".
_NOTHING_MUCH_DO = frozenset("""do did done doing does dont didnt doesnt havent hasnt
    havent havent""".split())


# What may follow the phrase: the doings people name when they say they are not up to much. It is
# a separate list from the filler because these words are only filler after the phrase - "not
# much chilling at home" is nothing much, "not working much" is about the thing that is not
# working, and the same word in the two places must not read the same.
_NOTHING_MUCH_AFTER = frozenset("""chilling relaxing working watching hanging pottering lazy
    home at out telly tv games game music reading dinner lunch tea coffee garden""".split())


# Everything from a "just" after the phrase is how the person finished the answer, not a new
# subject: "not much just chilling", "not much, just watching telly".
_NOTHING_MUCH_TAIL = frozenset(("just", "only"))


def _nothing_much_span(words):
    """(start, stop) of the phrase in these words, or None when no phrase is there.

    "not much" and "nothing much" are spans; so is a lone "much" behind a form of "do"
    ("havent done much today"). The words inside a "not ... much" span are checked here, which
    is the whole point: "not eating much" is not this phrase.
    """
    for i, word in enumerate(words):
        if word in ("notmuch", "nm", "nmu"):
            return i, i + 1
    for opener in ("nothing", "not"):
        if opener not in words:
            continue
        start = words.index(opener)
        if "much" not in words[start + 1:]:
            continue
        stop = words.index("much", start + 1)
        if all(word in _NOTHING_MUCH_BETWEEN for word in words[start + 1:stop]):
            return start, stop + 1
        return None
    if "much" in words:
        at = words.index("much")
        if any(word in _NOTHING_MUCH_DO for word in words[:at]):
            return at, at + 1
    return None


def _the_line_on_the_screen(memory):
    """The bot's last reply, looking past the turn it is answering now."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    for turn in reversed(turns or []):
        said = turn.get("bot") if isinstance(turn, dict) else None
        if isinstance(said, str) and said.strip():
            return said.strip()
    return ""


def _thanks_that_fit(options, memory):
    """The thank-you pool that does not claim to have helped when the bot only asked.

    "im learning to drive" is answered "Worth doing. What would you like help with first?", and a
    "thank you" straight after it came back "Glad that helped." - a claim about a turn that answered
    nothing. Nothing had helped yet: the bot had asked a question, and the question is on the
    screen, so the line that says it helped is left out of the pool for that turn.
    """
    said = _the_line_on_the_screen(memory)
    if said and not said.rstrip().endswith("?"):
        return options
    left = [option for option in options if "helped" not in option]
    return left or options


# The pools that are nothing but talk about the conversation: every line of them refers to an
# earlier turn, so on the first line of a chat the whole pool is wrong and the line is answered
# from the pool that opens a chat instead. `returned` is "back again, where were we" and
# `check_in`/`check_in_name` are "hello again, still here" - all three are a greeting when there
# is nothing to come back to.
FIRST_LINE_POOL = {"returned": "greeting", "check_in": "greeting", "check_in_name": "greeting"}


def _the_part_of_day(memory):
    """Which part of the day a hello names, or None when it names none."""
    read = memory.get("understood") if isinstance(memory, dict) else None
    words = str((read or {}).get("plain") or "").lower().split() if isinstance(read, dict) else []
    for part in ("morning", "afternoon", "evening"):
        if part in words:
            return part
    return None


def _says_the_time_of_day(memory):
    """True when the hello names the part of the day: "good morning" keeps its morning.

    Read from what the understanding engine made of the line, which is set before any module
    answers. A hello that says which part of the day it is has already said something, and
    answering it with a check-in throws that away.
    """
    read = memory.get("understood") if isinstance(memory, dict) else None
    words = str((read or {}).get("plain") or "").lower().split() if isinstance(read, dict) else []
    return any(word in words for word in ("morning", "afternoon", "evening"))


def _mid_chat(memory):
    """Whether this line is somewhere in a conversation, not the first thing said.

    "Is there an earlier turn?" is asked in one place, `bot/compose/onscreen.py`, so that this
    module's pools and the arbiter's pick among the modules cannot disagree about it.
    """
    return onscreen.earlier_turn(memory)


def _just_met(memory):
    """(name, plan) from what the user said on this turn, if they have just introduced
    themselves. Welcome them once, rather than on every later line."""
    log = memory.get("facts_log")
    if not isinstance(log, list):
        return None, None
    turn, name, plan = len(memory.get("turns") or []), "", ""
    for entry in log[-6:]:
        if not isinstance(entry, dict) or entry.get("turn") != turn:
            continue
        if entry.get("key") == "name" and isinstance(entry.get("value"), str):
            name = entry["value"]
        if entry.get("key") == "plan" and isinstance(entry.get("value"), str):
            plan = entry["value"]
    return name, plan


# A plan said back to someone who has just been introduced is only worth adding when it reads
# as something they will do: "you start your new job on monday", "you're doing a roast on
# sunday". A plan kept as a bare place or a bare thing ("to leeds in june", "York in june",
# "the gym tomorrow") does not read as a sentence there - "and to leeds in june sounds like a
# good one" is not something a person would say - so the plain welcome is used instead.
PLAN_CLAUSE_OPENS = frozenset(("i", "im", "i'm", "ive", "i've", "ill", "i'll", "we", "were",
                               "we're", "weve", "we've", "well", "we'll",
                               # a plan kept as a thing reads back as one: "and a picnic for my
                               # daughter's birthday sounds like a good one".
                               "a", "an", "the", "my", "our", "his", "her", "their", "this",
                               "that"))


PLAN_THINGS_OPEN = frozenset(("a", "an", "the", "my", "our", "his", "her", "their", "this",
                              "that"))


# A plan the store keeps as a bare verb phrase ("Learn the guitar.", "Save for a car.") is not
# a noun phrase, so the welcome puts it in the -ing form: "and learning the guitar sounds like a
# good one" is a sentence, "and learn the guitar sounds like a good one" is not. These are the
# verbs a plan starts with.
PLAN_VERB_OPENS = frozenset("""learn save buy book plan start finish move visit get make cook
bake build write paint plant grow fix clean decorate prepare host throw assemble sew knit roast
boil fry grill set sort replace repair install renovate organise organize train study practise
practice sell find look run walk cycle swim read play sing dance draw travel garden dig""".split())


def _ing(word):
    """The -ing form of a plan's first verb: "learn" -> "learning", "save" -> "saving"."""
    low = word.lower()
    if low.endswith("ie"):
        return low[:-2] + "ying"
    if low.endswith("e") and not low.endswith("ee") and len(low) > 3:
        return low[:-1] + "ing"
    if len(low) <= 4 and re.fullmatch(r"[^aeiou]*[aeiou][^aeiouwxy]", low):
        return low + low[-1] + "ing"
    return low + "ing"


def _plan_clause(plan):
    """What to add to a first meeting, from the plan said on the same line, or ""."""
    text = " ".join(str(plan or "").split()).strip(" .!?,")
    first = text.split()[0].lower() if text else ""
    if not text:
        return ""
    said = re.sub(r"\b(im|ive|ill)\b", lambda m: "i'" + m.group(0)[1:], text, flags=re.I)
    said = re.sub(r"\bwere\b", "we're", said, flags=re.I)
    said = re.sub(r"\bweve\b", "we've", said, flags=re.I)
    clause = you(said)
    if clause.lower().startswith("you") and first in PLAN_CLAUSE_OPENS:
        return clause[:1].lower() + clause[1:]
    if first in PLAN_THINGS_OPEN:
        clause = clause[:1].lower() + clause[1:]
        return clause.rstrip(".!?").rstrip()
    words = clause.split()
    if first.endswith("ing") and len(first) > 4:
        # "saving up for a bike", "wedding in june": already a thing, so it is said as it is
        return clause[:1].lower() + clause[1:]
    if first in PLAN_VERB_OPENS and words:
        # "and learning the guitar sounds like a good one"
        words[0] = _ing(words[0])
        return " ".join(words)
    if first == "for":
        # a plan kept as "For a car" is money put aside: the store reads it as saving
        return "saving " + clause[:1].lower() + clause[1:]
    return ""


def _is_greeting(tokens):
    return bool(tokens) and all(t in GREET_FILLER for t in tokens) and any(t in GREET_CORE for t in tokens)


# "im good thanks", "im well thanks", "im ok thanks", "yeah im great thanks" answer "how are you":
# the thanks on the end is manners, not gratitude for anything the bot did, and `_is_thanks` fired
# on it and thanked them back ("No problem at all." to a person saying they were well). The line
# is read as the self-report it opens with, so the positive pool answers the "how are you" and the
# thanks rides along. Only a line that *says how they are* is taken out of the thanks turn: a bare
# "thanks", "thanks, that helps" and "ok thanks" keep it.
# "im good thanks for the help" is gratitude with a state word in front of it, and the thanks is
# for something the bot did: that stays the thanks turn.
THANKS_FOR = re.compile(
    r"\bfor (?:that|this|it|the|your|you|all|everything|all of it|the help|the advice)\b")


# How somebody is, said with the verb in front of the good word: "im doing alright", "im
# feeling well", "im doing ok today", "im doing really well thanks". "ANSWERS_HOW_ARE_YOU" is
# this same list of words for the line that carries a thank-you on the end; these are the lines
# without one, and the ones the conversation opens with. Only the good words are here: "im doing
# badly" and "im doing not bad" are read by the pools that already hold them.
HOW_THEY_ARE_LINE = re.compile(
    r"^\W*(?:(?:yeah|yes|oh|well|hi|hiya|hey|so|and)[, ]+)?"
    r"(?:im|i'm|i am|its|it's|ive been|i've been)\s+"
    r"(?:doing\s+|feeling\s+|been\s+|been doing\s+|doing been\s+)?"
    r"(?:pretty\s+|really\s+|very\s+|so\s+|all\s+|too\s+|quite\s+|that\s+)?"
    r"(?:good|great|fine|ok|okay|alright|well|brilliant|grand|cracking|chill|sound|content"
    r"|mint|brill)\b"
    r"(?:\s+(?:today|thanks|thank you|ta|tho|though|honestly|actually|really|now))?\W*$")


ANSWERS_HOW_ARE_YOU = re.compile(
    r"^\W*(?:(?:yeah|yes|oh|well|hi|hiya|hey)[, ]+)?"
    r"(?:im|i'm|i am|doing|all good|its all good|it's all good|not bad|not too bad)"
    r"\s+(?:doing\s+|feeling\s+|pretty\s+|really\s+|very\s+|so\s+|all\s+|too\s+)?"
    # The words for a good day that are also another thing sit here too: "im chill ta", "im sound
    # thanks" and "im mint" answer how they are the same way "im grand ta" does, so they get the
    # same reply instead of the thank-you pool's "No problem at all.".
    r"(?:good|great|fine|ok|okay|alright|well|bad|brilliant|grand|cracking|chill|sound|content"
    r"|mint|brill)\b")


# The same line the other way round: "im not good thanks", "not great thanks", "im not doing ok
# thanks". `_is_thanks` fires on it and every reader past that branch takes it for news or a plan,
# so it was answered "Alright then - good luck with it." and, without the pronoun, "Nice one." -
# a person saying they were not good was congratulated. "not bad thanks" is the exception that
# keeps the positive turn: in English that is a good week.
NOT_GOOD = re.compile(
    r"^\W*(?:(?:yeah|yes|oh|well|hi|hiya|hey)[, ]+)?"
    r"(?:im|i'm|i am|doing|it's|its|i'm doing|im doing)?\s*\bnot\s+"
    r"(?:doing\s+|feeling\s+|too\s+|really\s+|very\s+|that\s+|so\s+)?"
    r"(?:good|great|fine|ok|okay|alright|well|brilliant|grand|cracking)\b"
    r"(?=\s*(?:$|[,.;!?]|thanks\b|thank you\b|tho\b|though\b|today\b|honestly\b|really\b|"
    r"i think\b|i guess\b|right now\b|at the moment\b))", re.IGNORECASE)


# A hedged answer to "how are you" is the answer half the country gives, and nothing in this file
# read it: "could be better thanks" reached the search hedge ("I'd rather not guess"), "been
# better thanks" was thanked back ("You're welcome — glad that helped"), "hanging in there" and
# "mustn't grumble thanks" were echoed ("Noted.", "I'll remember that"), and "cant complain" and
# "could be worse" were met with "One of those days?" as if they had said the day was bad. The
# person chose the hedge on purpose, so there are two degrees and they take different replies: the
# understatement (not a bad day and not a good one) is taken lightly and never turned into a bad
# day, and the low hedge gets the gentle question. Each is the whole line, with the manners on the
# end ("thanks", "tbh", "i suppose") counted as part of the line rather than as its subject, which
# is what the thank-you branch below has to know before it thanks anybody back.
HEDGE_LEAD = r"(?:(?:yeah|yep|yes|oh|ah|well|honestly|tbh|still|only|just|it|its|is|was|im|i'm|" \
             r"i am|am|doing|been|a|bit|pretty|kind of|sort of|and|but|so|really|very|lately|" \
             r"today|these days)\s+)*"


HEDGE_TAIL = r"(?:[,.]?\s*(?:thanks|thank you|ta|cheers|though|tho|tbh|to be honest|" \
             r"honestly|i suppose|i guess|i think|really|at the moment|right now|today|lately|" \
             r"all things considered)\s*)*\W*$"


# Not a bad day and not a good one: the understated yes.
# The pools that ask the person how they are, or open the chat: "cant complain" after one of
# these is the small talk it looks like.
ASKED_HOW_ARE_YOU = ("howareyou", "notmuch", "greeting", "greeting_name", "meet")


def _a_hedge_answering_the_question(memory):
    """Whether this hedge is the answer to how-are-you rather than a way of carrying a trouble.

    "cant complain" after "how are you" is small talk, and it went unanswered on main ("One of
    those days? What's up?"). The same words after "i lost my job" or "my mum died last month"
    are how somebody carries the trouble, not an invitation to talk about the weekend: "could be
    worse" there was answered "That'll do. Anything you're looking forward to?" by the pool this
    branch feeds. So the pool takes the turn only when the hedge opens the chat or answers a
    question the bot asked about the person. Otherwise the line is left to whatever answers a
    line said in a hard week, which is where the listening replies are.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return True  # nothing said yet: the hedge is the opener, so it is how they are
    note = memory.get("said_kind")
    if not isinstance(note, dict) or note.get("turn") != len(turns) - 1:
        return False  # the last answer was not this module's, so what was asked is unknown
    return note.get("kind") in ASKED_HOW_ARE_YOU


HEDGED_OK_LINE = re.compile(
    r"^\W*" + HEDGE_LEAD +
    r"(?:can'?t complain|could be worse|mustn'?t grumble|getting there|getting by|keeping busy|"
    r"keeping going|plodding on|surviving|bearing up|fair to middling|so so|ok i suppose|"
    r"ok i guess|alright i suppose)" + HEDGE_TAIL, re.IGNORECASE)


# The hedge that asks for the gentle reply: "could be better", "been better", "hanging in there",
# "up and down". "not great" and "not brilliant" are already the denial's (`NOT_GOOD`); these are
# the spellings that denial misses.
HEDGED_LOW_LINE = re.compile(
    r"^\W*" + HEDGE_LEAD +
    r"(?:could be better|been better|hanging in there|hanging on in there|up and down|"
    r"not been great|not been brilliant|not so good|lacking in energy)" + HEDGE_TAIL,
    re.IGNORECASE)


# A negator, the words that push the denial further out ("not too good"), and then a good word:
# that is a denial of the good day, not a mild way of saying it. "not bad" is the other way round
# and stays good, because the word denied is the bad one.
DENIAL_FILLER = {"too", "so", "very", "really", "that", "all", "quite", "feeling", "doing",
                 "am", "been", "at", "the", "moment", "right", "now", "today", "honestly"}


def _denies_a_good_word(tokens):
    """True when a negator in front of a good word turns it into the low feeling the line names.

    "im not good" is not the good news "im good" is, and neither is "im not too good" - the
    intensifier in the middle is why a bare check for the word "not" in the line answered both
    with "Good to know." So the walk skips the words that only push the denial further out and
    looks at the first real word after the negator.
    """
    for index, token in enumerate(tokens):
        if token not in {"not", "never", "barely", "hardly"}:
            continue
        for word in tokens[index + 1:]:
            if word in DENIAL_FILLER:
                continue
            if word in POSITIVE:
                return True
            break
    return False


def _is_thanks(tokens):
    return bool(tokens) and any(t in THANKS_CORE for t in tokens) and all(
        t in THANKS_FILLER or t in THANKS_LOOSE or t in THANKS_CORE for t in tokens)


# A nod in front of the thank-you ("got it, thanks", "cool thanks", "right, ta") is the person
# saying they followed, not part of what the line says. Every one of those words is in ACK_WORDS
# and none of them is in the thanks word lists, so the thanks reading failed on the whole line and
# the turn fell through to the sign-off a person gets on their way out: "got it, thanks" was
# answered "Alright then — good luck with it." while "thanks", "ok thanks" and "brilliant thanks"
# were all answered "Glad that helped." The "no" words are left out: "no thanks" is a turn-down,
# and reading it as a thank-you would answer a refusal with a welcome.
A_NOD_BEFORE = frozenset(ACK_WORDS - NO_WORDS)


# The pair that makes a no firm rather than naming anything of its own.
A_FIRM_NO = ("at", "all")


def _without_the_at_all(tokens):
    """The same line with the "at all" a no is said firmly with taken out."""
    kept = []
    for token in tokens:
        if token == A_FIRM_NO[1] and kept and kept[-1] == A_FIRM_NO[0]:
            kept.pop()
            continue
        kept.append(token)
    return kept


def _without_the_nod(tokens):
    """The same line with the acknowledgements around the thank-you dropped."""
    start, end = 0, len(tokens)
    while start < end - 1 and tokens[start] in A_NOD_BEFORE and tokens[start] not in THANKS_CORE:
        start += 1
    # "thanks, got it" is the same thank-you with the nod on the other side of it.
    while end - 1 > start and tokens[end - 1] in A_NOD_BEFORE \
            and tokens[end - 1] not in THANKS_CORE:
        end -= 1
    return tokens[start:end] if (start or end != len(tokens)) else tokens


HOW_ARE_YOU = re.compile(
    r"\b(how are (you|u|ya)( doing| today| feeling)?|how r (u|you)|hows it going|"
    r"how is it going|how are things|hows things|how you doing|(?:you|u) (?:ok|okay|alright)(?!\s*(?:with|about|to|for|if|when|on|at|in)\b)|"
    # "you good?" is the same question as "you ok?", and without it the line fell to a chatty
    # pool and got "Fair enough.", which answers nothing. "good" and "fine" only carry the
    # question on their own: "you good with that", "you good to go", "you good at maths" and
    # "u good in the kitchen" ask for an answer about something, so they keep the reply they had.
    r"you (good|fine)(?!\s*(?:with|about|to|for|if|when|on|at|in)\b)|"
    r"u (good|fine)(?!\s*(?:with|about|to|for|if|when|on|at|in)\b)|"
    # The same guard on "you feeling ok": "you feeling good about the interview" and "u feeling
    # ok for tomorrow" are asks about an interview and a tomorrow, not about the bot.
    r"(you|u) feeling (ok|okay|alright|good)(?!\s*(?:with|about|to|for|if|when|on|at|in)\b)|"
    # "howz u" and "hows u" are the same question written the way people type it. The composer
    # reads them, but chat.py answers first, so without these the line reached the "I'm not sure
    # about that one" survey.
    r"howz (you|u|ya|things|life)|hows (you|u|ya)|"
    r"u (ok|okay)(?!\s*(?:with|about|to|for|if|when|on|at|in)\b)|how do you do|whats up|what is up|sup|hows life|how is life|how are ya|"
    # How-are-you said with a day in it: "hows your day been", "how was your day",
    # "hows your week been", "how have you been". These ask how the bot is, and without them
    # nothing above the floor read them as that: after any question they were answered from the
    # subject on the table - "how long do i boil an egg" then "hows your day been" got the
    # keeping card for boiled eggs, and then "how have you been" got "Same as before: Lower
    # eggs into already boiling water". A day or a week named as *yours* is the person asking
    # after the bot, so the words after it are the only thing that can make it another ask:
    # "how was your day at work" and "hows your week going to plan" are about the world.
    r"hows? (?:your|ur) (?:day|week)(?: (?:been|going|go|then))?"
    r"(?!\s*(?:(?:been|going|go|then)\s+)?(?:off|at|on|in|with|about|after|before|to)\b)|"
    r"how (?:is|was|s|has|s been) (?:your|ur) (?:day|week)(?: (?:been|going|go|then))?"
    r"(?!\s*(?:(?:been|going|go|then)\s+)?(?:off|at|on|in|with|about|after|before|to)\b)|"
    r"how (?:have|ve) (?:you|u|ya) been|how (?:you|u|ya) been)\b")


# The same words are also the start of a question about something else: "how are you meant to
# tell them", "how are you supposed to say no to your boss", "how are you going to pay for it",
# "how are you feeling about the move". A how-are-you is only about the bot while nothing that
# asks about the world follows it. "how are you going" is the Australian greeting; only
# "going to" makes it a plan.
HOW_ARE_YOU_CONTENT = ("supposed to", "meant to", "going to")


def _is_howareyou(tokens):
    if not (1 <= len(tokens) <= 7):
        return False
    line = " ".join(tokens)
    match = HOW_ARE_YOU.search(line)
    if not match:
        return False
    if _asks_about_the_make(line):
        # "how are you built", "how are you made", "how are you programmed": the words after
        # "how are you" finish a question about what the bot is made of, not about its day, and
        # the small-talk pool answered all of them with "All good here. What's keeping you busy?"
        # - a stock close for a question nobody asked. The composer already reads these lines as
        # questions about the bot's make (bot/compose/fallback.py `about_the_bot`), and the
        # greeting module has the honest answer for that reading, so this pool stands down.
        return False
    rest = line[match.end():].strip()
    # "feeling about the move" and "feeling about work" ask for an opinion on a subject, not
    # for the bot's day; "feeling today" and "feeling now" still ask about the bot.
    if match.group(0).endswith("feeling") and rest.startswith("about "):
        return False
    # "how is it going with my claim", "how's it going with the extension": something of theirs on
    # the end of a how-are-you is the thing they are asking about, and the small-talk pool answered
    # it with "All good here. What's keeping you busy?". "with all this" and "with that" are still
    # the bot's day - "how's it going with all this?" is small talk and keeps the pool.
    if re.match(r"with\s+(?:my|our|your|his|her|their|the)\s+\w", rest):
        return False
    rest_words = rest.split()
    return " ".join(rest_words[:2]) not in HOW_ARE_YOU_CONTENT


# The two readings of a line about the bot's make: the machine it is made of, and how it works.
# "feel" is not one of them - "how are you feeling" is a how-are-you with the verb said out - so
# the guard is a small set rather than every reading the composer has about the bot.
THE_MAKE = frozenset(("model", "workings"))


def _asks_about_the_make(line):
    """True when the composer reads the line as a question about what the bot is made of."""
    try:
        return fallback.about_the_bot(line) in THE_MAKE
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False


def _is_bye(tokens):
    """A goodbye, even with a short breather in front of it.

    "talk later", "catch you later" and "Ha, fair enough. Talk later!" all say the person
    is leaving. A plan to talk ("we should talk later about the boiler") is not a goodbye:
    the words that carry the plan are outside the small set a goodbye is built from.
    """
    if not tokens or not all(t in BYE_FILLER for t in tokens):
        return False
    return _leaves(tokens)


# The words a goodbye is made of, said as the whole clause ("night then", "good night").
LEAVES_ONLY = (("good", "night"), ("night", "night"), ("night",), ("later",), ("bye",),
               # Said as the whole line, these leave: "sweet dreams", "im out", "ill let you go".
               # None of them carries a going word, so the leaving has to be read from the
               # phrase itself, the same way "night" is.
               ("sweet", "dreams"), ("im", "out"), ("i", "am", "out"), ("in", "a", "bit"),
               ("let", "you", "go"), ("let", "u", "go"), ("ill", "let", "you", "go"))


# A pleasantry with a time of day describes it instead: "we had a takeaway and watched a film,
# nice night" is telling you about their evening, not walking out of the door. "good" is not one
# of the words here: "good night" is the sign-off itself, and "good night then" or "good night
# all" are still people leaving.
# Every word a goodbye is made of: the going word ("gotta", "heading", "off"), the thing it goes
# to or the time it happens ("go", "bed", "now", "soon"), and the words around them that say
# nothing ("i", "to", "then", "right"). A leaving said with the going word and a time in it is a
# goodbye only while it says nothing else: read on any word, the shape "i need ... now" took every
# ask for help that named the time it was needed, so `i need help now` and `i must eat now` were
# answered "Bye for now!" - a farewell to somebody who had just asked for a hand. A line with a
# word in it that is not one of these is about the thing it names, and the readers for that thing
# take it.
LEAVING_WORDS = frozenset({
    # the going words
    "gotta", "got", "gonna", "gunna", "have", "heading", "head", "off", "leaving", "going",
    "need", "must", "should", "go", "goes", "going", "went", "sleep", "sleeping", "bed",
    "bedtime", "out", "soon", "now", "later", "night",
    # what the leaving is said around
    "i", "im", "i'm", "am", "me", "we", "to", "be", "a", "for", "on", "in", "the",
    "then", "so", "ok", "okay", "right", "well", "just", "now", "yes", "yeah", "yep",
    "alright", "and", "all", "your", "you", "u", "take", "care", "bye", "goodbye",
    "goodnight", "cya", "cheerio", "toodles", "nightnight", "see", "talk", "speak", "catch",
})


DESCRIBES_THE_DAY = re.compile(
    r"\b(?:nice|lovely|great|fun|brilliant|long|early|late|quiet|busy|cold|warm|wet)\s+"
    r"(?:night|day|evening|morning|one|time)\b")


def _leaves(tokens):
    """True when this clause is the act of leaving, not a word that only looks like one.

    "ok, night then" and "catch you later" leave; "nice night" - said after they told you what
    they did - is a comment about their evening, and "ok, see you at the weekend" is a plan.
    """
    if not tokens:
        return False
    if tuple(tokens) in LEAVES_ONLY or tuple(tokens) == ("good", "night"):
        return True
    if any(t in {"bye", "byebye", "goodbye", "goodnight", "cya", "cheerio", "toodles",
                 "nightnight"} for t in tokens):
        return True
    if any(t in BYE_TIME for t in tokens) and any(t in BYE_VERB for t in tokens):
        return True
    if tokens[0] == "see" and any(t in {"you", "u", "ya"} for t in tokens):
        return True
    # "got the day off" is a day away from work, not the person leaving the chat: every one of
    # its words is a goodbye word, so it was answered "Bye for now!" - a farewell to somebody
    # who had just said they had the day to themselves.
    if re.search(r"\b(?:day|days|time|week|weeks|weekend|afternoon|morning|evening|night|shift"
                 r"|today|tomorrow|tonight|monday|tuesday|wednesday|thursday|friday|saturday"
                 r"|sunday)\s+off\b", " ".join(tokens)):
        return False
    going = any(t in {"gotta", "got", "gonna", "gunna", "have", "heading", "head", "off",
                      "leaving", "going", "need", "must", "should"} for t in tokens)
    # "right, i'm off" and "im off now" are goodbyes on their own; every word has to be a
    # goodbye word for this to run, so "i need time off work" and "i got off the train" stay
    # ordinary.
    away = any(t in {"go", "sleep", "bed", "now", "out", "soon", "off"} for t in tokens)
    if going and away and all(t in LEAVING_WORDS for t in tokens):
        return True
    # "in a bit", "back in a min", "see you in a sec": the time to leave and nothing else names
    # anything, so the line is a goodbye even though it carries no word for going.
    if any(t in BYE_TIME for t in tokens) and all(
            t in BYE_TIME or t in {"back", "in", "a", "see", "you", "u", "ya"} for t in tokens):
        return True
    # "night" on its own, or over to "later", is a goodbye; "nice night" is not.
    if "night" in tokens or "later" in tokens:
        return not DESCRIBES_THE_DAY.search(" ".join(tokens))
    return False


# The words that make a sign-off a night one. A goodbye at any other hour keeps the day pool:
# "cya later" is not a goodnight, and the pool it drew from used to say it was.
NIGHT_SIGNOFF = {"night", "goodnight", "nightnight", "bed", "sleep", "sleeping", "tonight"}


def _bye_kind(tokens):
    """Which goodbye pool fits this sign-off: the night one only when the line says it is night."""
    return "bye_night" if any(token in NIGHT_SIGNOFF for token in tokens) else "bye"


def _ending_bye(clean, memory):
    """The last clause is a goodbye even when the words before it are not filler.

    "right, i'm going to make a start. catch you later!" says goodbye at the end; a plan to
    talk ("we need to talk later about the boiler") is one clause and stays a plan.
    """
    if clean.endswith("?"):
        return False
    understood = memory.get("understood") if isinstance(memory, dict) else None
    clauses = understood.get("clauses") if isinstance(understood, dict) else None
    if not clauses:
        clauses = [_tokens(part) for part in re.split(r"[.!?]+", clean) if part.strip()]
    return len(clauses) > 1 and _is_bye(clauses[-1])


# A night that went wrong, told as a fact rather than a word ("ive been up since 5 with the
# baby", "i keep waking at 3am"). It is the same thing as saying "i'm knackered", so it gets the
# same kind of answer: say the hard part back, then one thing that helps.
EARLY_NIGHTS = (
    (re.compile(r"\b(?:keep|keeps|always|still) (?:waking|wake)(?: up)?(?: at| around)? \d|"
                r"wake(?:s| up)? at (?:the same|\d)|woke up at \d"),
     ("Waking at the same time every night is common and it passes. Don't watch the clock: if "
      "you're still awake after twenty minutes, get up and read something dull in low light.",
      "That clockwork wake-up is your body clock, not a fault. Keep the room cool and dark, and "
      "don't lie there fighting it — get up, then go back when you feel heavy again.")),
    (re.compile(r"\b(?:been |was )?up since \d|up since (?:the |about |half |\d)|"
                r"up at \d (?:am|o'clock)|been up since"),
     ("That's an early start, and it makes the whole day heavier. If there's anyone who can "
      "take a turn later, use them and get a proper rest.",
      "Long morning already. Get outside for ten minutes when you can — daylight is what tells "
      "your body what time it is.")),
    # A bad night is said as a fact about the sleep itself, and people name the sleep in their
    # own words: "i had a terrible sleep", "a rubbish nights sleep", "slept terribly". A
    # *night* that was rough already has its own line ("Rough one. A shower ... and an early
    # night usually resets it."), so this one is about the sleep word and the short night.
    (re.compile(r"\bup all night|awake all night|no sleep|didn'?t sleep|didn'?t get any sleep|"
                r"slept badly|bad night|sleepless|"
                r"(?:terrible|awful|rubbish|rotten|bad|poor|lousy) (?:night'?s? |nights )?sleep|"
                r"slept (?:terribly|awfully|badly|rotten|horribly|awful|terrible|rubbish|lousy)|"
                r"(?:hardly|barely)(?: any)? slept|(?:hardly|barely) any sleep|broken sleep"),
     ("Rough night, then. Coffee only covers so much — get twenty minutes flat on your back this "
      "afternoon if you can, and keep the evening quiet.",
      "That's a hard one to carry into a day. Go easy on yourself today and aim for bed an hour "
      "earlier tonight.")),
)


# The line names someone else as the one who was awake ("my baby has been up since 3am"), or it
# says the person is at the end of their rope. Both need more than sleep advice, so pass.
# The other person is named in the words parents actually use: "my little boy has been up since
# four every morning" was read as the speaker's own early start and answered with daylight
# advice about their own body clock, and "my toddler is up since 4 every day" the same, because
# only "baby", "son" and "kid" were owners here. An age between the possessive and the noun is
# the same owner ("my 3 year old has been up since 4").
OTHER_AWAKE = re.compile(
    r"\b(?:my|our|the|his|her) (?:\d+ )?(?:baby|son|daughter|kid|kids|child|children|toddler|"
    r"year[- ]olds?|"
    r"little one|little boy|little girl|littleun|littlun|newborn|grandson|"
    r"granddaughter|grandchild|twins|teenager|teen|stepson|stepdaughter|stepchild|husband|"
    r"wife|partner|mum|dad|dog|cat|"
    r"puppy|kitten|flatmate|neighbours?|neighbor)\b[^.?!]*?\b(?:up since|up all night|awake|"
    r"up from|won'?t|wont|can'?t|cant)\b"
    # "my boy" and "my girl" are a small child here only when the line says when they were up:
    # the same words say what a night cost the speaker ("my boy kept me up all night"), and that
    # is the tiredness chat answers, not the child card.
    r"|\b(?:my|our|the|his|her) (?:boy|girl|lad|lass)\b[^.?!]*?"
    r"\b(?:up since|up from|up every morning)\b"
    # A small child is named on its own just as often ("little one has been up since 4am all
    # week"), and no possessive is needed for these: they are a child in anyone's mouth.
    r"|\b(?:little one|little boy|little girl|littleun|littlun|toddler|newborn)\b[^.?!]*?"
    r"\b(?:up since|up all night|awake|up from)\b"
    # ...or the awake part is done with someone who is unwell ("up all
    # night with a sick child"): the cause is theirs, not the person's.
    r"|\b(?:been |was )?up (?:since|all night|all hours|at \d)\b[^.?!]*?"
    r"\bwith (?:a |the |my |our |his |her )?(?:sick|poorly|ill|unwell|"
    r"teething|crying|colicky|newborn)\b")


# A death in the conversation: a bad night after one is grief, not sleep hygiene, so the sleep
# reply stays out of it, in the line itself or in what they said just before.
LOSS = re.compile(r"\b(?:died|dying|death|dead|passed away|funeral|burial|cremation|bereave\w*|"
                  r"lost my (?:mum|mom|dad|father|mother|wife|husband|son|daughter|brother|"
                  r"sister|partner|baby|child)|(?:mum|mom|dad|father|mother|wife|husband|son|"
                  r"daughter|brother|sister|partner|gran|nan|grandad)\s+(?:has|have|had)\s+"
                  r"(?:just )?(?:died|passed))\b")


# The sleep that went wrong belongs to someone else ("my son had a terrible sleep and is grumpy
# today", "he slept terribly"). Consoling the speaker about another person's night is the wrong
# line whichever words carried it, so the sleep word with an owner in front of it stands down -
# and so does a person pronoun, which no one uses about themselves.
OTHER_SLEPT = re.compile(
    r"\b(?:my|our|the|his|her|their) (?:baby|son|daughter|kid|kids|child|children|husband|wife|"
    r"partner|mum|mom|dad|mother|father|brother|sister|friend|flatmate|roommate|neighbours?|"
    r"neighbor|dog|cat|puppy|kitten)\b[^.?!]*?\b(?:sleep|slept|sleeping|naps?|night)\b"
    # A pronoun before the sleep word is somebody else too: "he had a terrible sleep", "she
    # barely slept". After it ("i slept terribly and then he woke me") it is not, so only look
    # forward from the pronoun.
    r"|\b(?:he|she|they)\b[^.?!]*?\b(?:sleep|slept|sleeping|barely|hardly)\b")


# The night can be told about both people at once ("my son had a bad night so i barely slept"):
# the other person's night is the cause, and the one who lost their sleep is the speaker. The
# owner in front of the sleep word must not take the answer away from the person who is short of
# sleep, so the speaker saying they lost theirs is read before the owner is.
SPEAKER_LOST = re.compile(
    r"\bi\b[^.?!]{0,24}?\b(?:barely|hardly|didn'?t|didnt|couldn'?t|couldnt|never|not)\b"
    r"[^.?!]{0,16}?\b(?:sleep|slept|sleeping|wake|woke|slept a wink)\b"
    r"|\bi\b[^.?!]{0,12}?\b(?:was|am|been|got|kept|keep)\s+(?:up|awake)\b"
    r"|\bi\b[^.?!]{0,10}?\bslept\b"
    r"|\b(?:woke|woken|wakes) me\b")


# The reason they were awake is a symptom ("i keep waking at 3am with pain"): advice about the
# body clock talks past it, so the line goes to whoever can answer the cause instead.
# A night lost to something that hurts or keeps them up is not a body-clock problem: say the
# cause back and point at someone who can look at it, rather than handing out sleep hygiene.
SORE_NIGHTS = (
    "Being awake with something that hurts is worth mentioning to a GP or pharmacist, "
    "especially if it is the same place every night. Tonight, prop yourself up, keep the room "
    "cool and skip the clock-watching.",
    "Waking because of pain or a cough is your body asking for attention, not a bad habit. If it "
    "has gone on a few nights, get it looked at; for tonight, sit up and take the weight off it.",
)


# The ache put on a part is one word ("earache", "backache"), so the bare "ache" here only
# matches it standing alone; the compounds are named or "something for an earache" reads as no
# symptom at all.
SYMPTOM = re.compile(r"\b(?:pain|painful|ache|aches|aching|achy|hurt|hurts|hurting|cramp|cramps|"
                     r"cough|coughing|tooth|toothache|toothaches|headache|headaches|migraine|"
                     r"migraines|earache|earaches|backache|stomachache|tummyache|heartburn|"
                     r"reflux|nausea|nauseous|sick|fever|itch|itching|sore|swollen|stiff)\b")


END_OF_ROPE = re.compile(r"\b(?:can'?t|cannot) (?:do this|go on|take it|cope|keep going)\b|"
                         r"\bend(?:ing)? it\b|\bkill myself\b|\bhurt myself\b|\bwant to die\b|"
                         r"\bno point\b|\bhearing things\b|\bseeing things\b|\bnot worth it\b")


# The night was lost to something on their mind ("i didnt sleep because i was so worried about
# money", "we had a row and i couldnt sleep"). That is worry or a row to answer, not a clock to
# reset, so the sleep tips stay out of it like they do for pain and grief.
WORRY = re.compile(r"\b(?:worried|worry|worrying|worries|stress(?:ed|ful|ing)?|anxious|anxiety|"
                   r"overthink\w*|overwhelm\w*|on my mind|can'?t switch off|racing|panic(?:king)?)\b|"
                   r"\b(?:we|i|he|she|they) had a (?:row|argument|fight|falling out)\b|"
                   r"\bargued (?:with|about)\b|\bfell out with\b|\brow with\b")


# A line that gives only how often the trouble happens, after the turn that named the trouble.
# "i keep waking up at night" was followed by "its every night" and the composer echoed it back
# ("Got it - it's every night"); the frequency is the new part, so the answer should use it,
# either to ask the length it still needs or, when the last answer already asked or named that,
# to give the next step. The line has to be only the frequency: "i have a headache every day"
# names the trouble itself and keeps whatever answers it.
FREQUENCY_ONLY = re.compile(
    r"^\W*(?:(?:and|but|so|oh|well|yeah|yep|ok|okay|right|alright|no)\W+)*"
    r"(?:(?:it'?s|its|it is|that'?s|thats|there'?s|theres)\s+)?"
    r"((?:(?:every|most)(?:\s+single)?\s+(?:night|nights|morning|mornings|day|days)"
    r"|all\s+(?:the\s+)?time|nightly|daily|constantly|non ?stop))"
    r"\b(?:\s+(?:now|though|at the moment|lately|these days|still))*\W*$", re.I)


# The first reply to a broken night usually already says the GP or the weeks it takes, so the
# frequency gets the step for tonight; when nothing has been said about length, the useful turn
# is the one that asks it.
NIGHT_FREQUENCY = (
    "{often} is a lot. How long has it been like that?",
    "{often}, then. That wears you down - has it been going on long?",
    "{often}, then. Is that recent, or has it been like this for weeks?",
)


NIGHT_FREQUENCY_KEPT = (
    "{often}, then. Tonight, keep the room cool and dark, and if you are still awake after "
    "twenty minutes get up and read something dull until you feel heavy.",
    "{often}, then - keep the same getting-up time every day, even after a bad one; that is the "
    "bit that steadies it.",
    "{often}, then. Leave the phone out of reach and get ten minutes of daylight early; if it is "
    "still like this in a few weeks, go back to the GP.",
)


BODY_FREQUENCY = (
    "{often} is a lot. How long has it been going on?",
    "{often}, then - is that recent, or has it been like this a while?",
    "{often} is worth a proper look. Has it been going on for weeks?",
)


BODY_FREQUENCY_KEPT = (
    "{often}, then. That is enough to get it looked at if it keeps on, and a note of when it is "
    "worst helps.",
    "{often} is a lot. Keep a note of what sets it off and what you have tried, and take that to "
    "the GP.",
    "{often} is your body asking for a proper look. Book the GP and take a week of notes with you.",
)


# A knowledge answer that talks about a child, or about "them", is not about the person asking:
# "its every night" after their own cough reached the child-cough entry, while the morning
# headache, sore throat and sneezing entries are about the person and answer the frequency better
# than the general line here can.
_A_CHILD_OR_THEM = re.compile(
    r"\b(?:child|children|kid|kids|baby|babies|toddler|they|them|their|he|she|him|her)\b", re.I)


def _answers_has_the_frequency(clean, memory):
    """True when the knowledge base answers this frequency about the person themselves.

    The entry's own answer is better than the general frequency line: it knows it is the
    morning headache or the throat that is sore first thing. It is only stepped over when there
    is no entry, or when the entry is about somebody else (the child-cough card after an adult
    said "i have a cough"), because that one is the wrong person's answer.
    """
    if not isinstance(memory, dict):
        return False
    try:
        from ..modules import answers  # a local import: the module's own import line is shared
        guess = copy.deepcopy(memory)
        said = answers.respond(clean, guess)
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False
    if not said:
        return False
    flat = " ".join(str(said).lower().split())
    if not flat or _A_CHILD_OR_THEM.search(flat):
        return False
    # A repeat of the answer already on the screen is not the frequency's own answer: the
    # frequency line has to say something about the frequency.
    turns = memory.get("turns") or []
    before = " ".join(str((turns[-1] or {}).get("bot") or "").lower().split()) if turns else ""
    if flat.startswith("same answer") or (before and before[:60] in flat):
        return False
    return True


def _worry_kind(clean):
    """Which worry this is: about a person, about a named event, or about a thing.

    "im worried about my mum" and "im worried about money" are not the same as "im nervous
    about my driving test", and the driving-test reply ("nerves before something big are
    normal") reads as cold on either. A named event keeps "anxious"; a person gets an answer
    about them; anything else gets a worry reply that presumes nothing about a date."""
    if WORRY_EVENT.search(clean):
        return "anxious"
    if WORRY_PERSON.search(clean):
        return "worry_person"
    if WORRY_ABOUT_THING.search(clean):
        # A day in the line is a date, even when it does not name a thing that happens on it:
        # "im anxious about tomorrow" is nerves before something, and the reply that says the
        # worry has no end date on it reads as if they had not said when.
        if WORRY_WHEN.search(clean):
            return "anxious"
        return "worry"
    return "anxious"


# "not great at maths" is about a skill, not a mood, and the sad pool would be reading a feeling
# into it. What follows has to be a thing to be good at: "not great at the moment", "not great at
# work" and "not great" itself are feelings and keep their reading.
SKILL = re.compile(r"\b(?:not|never)\s+(?:very\s+|that\s+|really\s+)?"
                   r"(?:great|good|brilliant|amazing|fantastic|the best)\s+(?:at|with|in)\s+"
                   r"(?!(?:all|least|the|this|that|it|first|home|work|school|uni|university|"
                   r"college|everything|anything|life|myself)\b)[a-z]")


def _without_skills(clean):
    """The line with any "not great at <subject>" taken out, so a skill is not read as a mood."""
    return SKILL.sub(" ", clean)


# The words people use for nerves are mostly not in the table above ("bricking it", "on edge",
# "butterflies"), and the reading knows them. So its emotion is a fallback: it only counts when
# the speaker says it of themselves, which is what keeps "how do i stop my baby crying" and "a
# mad week" out of it.
EMOTION_FEELING = {"sad": "sad", "lonely": "lonely", "angry": "annoyed", "anxious": "anxious",
                   "tired": "tired", "happy": "happy", "bored": "bored", "confused": "confused",
                   # "i have a hangover" and "i think im jet lagged" name a state of the
                   # speaker's own, and the rough-day pool is the answer to it.
                   "unwell": "rough_day"}


# A panic attack is not nerves before something big: "im having a panic attack" says nothing
# about what is coming up, and the "nerves before something big are normal" line reads as though
# the person had told the bot about a date. "panic" is already in the anxious row, so the noun is
# what the reading needs. Present tense only, and only when it is the speaker's own: "my sister is
# having a panic attack" is hers, and "i had a panic attack last year" is history.
PANIC_NOW = re.compile(
    r"\b(?:i'?m|im|i am|i think i'?m|i think im|i'?ve|ive)\b[^.?!]{0,18}?"
    r"\b(?:having|getting|got|in the middle of)\b[^.?!]{0,12}?\bpanic attacks?\b"
    # The bare noun has to open the line: "she gets panic attacks now and then" is her habit, and
    # the one reading that has no subject of its own must not take it (neat-moth, on the deck).
    r"|(?:\A|\b(?:having|getting|got|in the middle of)\s+)(?:a |another )?panic attacks?"
    r"\s+(?:right now|now|at the moment)\b"
    # "im panicking about money" and "im panicking about the wedding" say what it is about, so
    # they are worry with a subject and belong to the worry pool that names it, not to a body
    # answer that would drop the subject. Only the bare verb is an attack.
    r"|\b(?:i'?m|im|i am)\s+(?:properly |really |actually |starting to )?panick(?:ing|y)\b"
    r"(?!\s+(?:about|over|because|that|at|for|since)\b)")


PANIC_SOMEONE_ELSE = re.compile(
    r"\b(?:my|his|her|their|your)\s+\w+[^.?!]{0,16}?\b(?:had|has|having|were|was|got)\b"
    r"|\b(?:he|she|they|we|you)\s+(?:is|are|was|were|had|has|have|kept|keeps|gets?|suffers?|"
    r"struggles?)\b[^.?!]{0,12}?\bpanic"
    r"|\b(?:last|past)\s+(?:year|night|week|month|summer|winter|time)\b"
    r"|\b(?:years|months|weeks|days) ago\b")


# "i was gutted", "we were shattered", "we are knackered": the state said of the person in the
# past, or of the pair of them, is the same state as "im gutted". The cue list held only the
# present first person, so "i was shattered" reached the emotion reader (emotion tired, owner
# self) and no pool: the line came back with the neutral nod, "Thanks for telling me - I'm here
# if you want to dig into any of that", to somebody who had just said they were exhausted.
SELF_CUE = re.compile(r"\b(i'm|im|i am|i was|i were|i feel|i felt|ive|i've|i have|"
                      r"we are|we were|we're|were|weve|we've|we have)\b")


# Losing the thread is said without a word for how the person is: "i dont understand", "i dont
# get it", "i cant follow it". Those are the confused pool's, and the reading already names the
# feeling, so the pool is asked for them the same way it is asked for "im confused".
LOST_THE_THREAD = re.compile(
    r"\b(?:i|we)\s+(?:just\s+|still\s+|really\s+|honestly\s+|literally\s+)?"
    r"(?:do not|dont)\s+(?:understand|get it|get this|follow|follow it)\b"
    # "i cant get my head round this" says the same thing with a picture instead of a word: the
    # reading names it confused (kinds.EMOTION_WORDS), and without this the pool was never asked.
    r"|\b(?:i|we)\s+(?:just\s+|still\s+|really\s+)?(?:cannot|cant|can not)\s+"
    r"(?:get|make)\s+(?:my|any)\s+head\s+(?:round|around|straight)\b"
    r"|\bstruggling\s+to\s+(?:understand|follow|get (?:my|it|this))\b"
    # "i cant make head nor tail of it" is the same picture with the tail in it, and "or" is what
    # half the people who write it type.
    r"|\bhead\s+(?:nor|or)\s+tail\b")


# "terrified of spiders" is nerves about a thing, not nerves before something big: the words
# the reading knows are asked the same question the table's words are.
THING_OF = re.compile(r"\bof\s+[a-z]")


# A line that is only a feeling word, with the words people put round one, is about the person
# writing it: there is nobody else "bit bored tbh" could be about. Without this the mood is
# found but the line is not counted as theirs, and a stock "Thanks for telling me" answers it.
BARE_FILLER = frozenset("""
im i'm i am i am feel feeling felt been bit a little kind of kinda sorta sort so really very
pretty quite just still totally too now today tonight again tbh tho though atm rn lol haha
honestly actually and but me that this it is
""".split())


# A courtesy word at the end of a line: "not great thanks", "knackered thanks, ta". It is the
# person being polite about answering, not the answer.
A_THANK_YOU_AT_THE_END = re.compile(
    r"(?:\s*,?\s*(?:thanks|thank you|thank|thx|ty|ta|cheers|cheerz))+\s*[.!?]*$", re.I)


# A bare "fine", "good", "not bad" is the same answer as "im fine" and "im good", which the
# positive pool already answers with "Glad to hear it." The ack pool gave them "Alright then
# \u2014 good luck with it.", a line for a plan, not for how somebody is.
# The words people answer "how are you" with. "ok", "okay", "alright" and "well" are the
# ordinary ones, and they were missing: "i feel well" got "Thanks for telling me - I'm here if
# you want to dig into any of that", which is what the bot says to bad news.
PLAIN_GOOD_WORDS = frozenset("""good great fine grand brilliant lovely perfect cool sweet""".split())


# The soft four are the ordinary answers to "how are you", but on their own they are also how a
# person takes an answer in ("ok", "alright"), so a bare one is only the answer to a question.
PLAIN_GOOD_ASKED = frozenset("""ok okay alright well""".split())


# The frame the answer comes in. With it a soft word is the answer however the last turn ended:
# "i feel ok" is how they are, not an acknowledgement of what the bot just said.
PLAIN_GOOD_FRAME = frozenset("""feel feeling felt""".split())


# "feel" and "feeling" are the frame the answer comes in, not a word of its own: "i feel fine"
# is the answer "im fine" gives, and it got a stock line instead.
PLAIN_GOOD_FILLERS = frozenset("""im i am doing so very really today still all enough too
                                  honestly actually myself feel feeling been""".split())


# A fine answer usually has a small word on the end of it, and the word is where or when or a
# courtesy, not a second thing: "all good here", "all good now", "im good thanks", "we are fine
# ta". None of these are in the fillers above, so the line failed the test, the sentence was read
# as one more thing the person had said, and a person telling the bot they were fine got
# "I'm listening - say more if it helps." or "Thanks for telling me - I'm here if you want to dig
# into any of that." The reading is still only a good word and its small words: anything that
# names a thing ("my back is good now") keeps the words that are not here and is not a fine answer.
PLAIN_GOOD_TAIL = frozenset("""here now tonight around about cheers ta thanks thank mate love
                               side on my we are yeah its""".split())


def _the_bot_just_asked_them(memory):
    """True when the last thing the bot said was a question, or when it has not spoken yet.

    A good word with a thank-you on it ("great thanks", "lovely thanks") is how people close a
    conversation after an answer: "how long do i roast a chicken" / "great thanks" is a thank-you,
    not news, so it is only folded when the bot has just asked them something to answer.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)] if memory else []
    if not turns:
        # Nothing has been asked yet, so "great thanks" as the opening line is the thank-you it
        # looks like: there is no mood to have answered.
        return False
    said = str(turns[-1].get("bot") or "").rstrip()
    return said.endswith("?")


# The pools whose words mean the day went well. A thank-you on the end of one of these is how a
# conversation closes, so it is read as a mood only when the bot has just asked them something.
GOOD_POOLS = frozenset({"happy"})


def _a_thank_you_taken_off(clean, memory=None):
    """The line with a courtesy word at the end taken off, when what is left is a mood.

    "not great thanks" is a person answering how they are, and the "thanks" is courtesy. Read
    whole, the line was a thank-you, so the bot said "Alright then \u2014 good luck with it." to
    someone who had just said things were not great. The courtesy word comes off, and only when
    the words left are a mood the pools already answer: "ok thanks", "thanks for that" and a
    question with a thank-you on the end keep their own replies.
    """
    folded = A_THANK_YOU_AT_THE_END.sub("", clean).strip(" ,.!?")
    if not folded or folded == clean or len(folded.split()) > 4:
        return ""
    padded = " " + folded + " "
    for pool, words in FEELINGS:
        for word in words:
            if " " + word + " " in padded:
                # "great thanks" and "lovely thanks" after an answer are a close, not news: the
                # good half of the mood list is only read when the bot has just asked them
                # something. "not great thanks" is still a bad day, so the rest of the list folds
                # wherever it lands.
                if pool in GOOD_POOLS and not _the_bot_just_asked_them(memory):
                    return ""
                return folded
    if _a_plain_good_answer(folded, memory):
        return folded if _the_bot_just_asked_them(memory) else ""
    return ""


def _a_plain_good_answer(clean, memory=None):
    """A line that is only a good word (and maybe a "not bad") is the answer "im fine" gives."""
    if "?" in clean:
        return False
    if re.search(r"\bnot (?:too |half |so )?bad\b", clean):
        return True
    words = [w.strip(".,!?;:") for w in clean.split() if w.strip(".,!?;:")]
    if not words or len(words) > 7:
        return False
    if not any(word in PLAIN_GOOD_WORDS or word in PLAIN_GOOD_ASKED for word in words):
        return False
    if not all(word in PLAIN_GOOD_WORDS or word in PLAIN_GOOD_ASKED
               or word in PLAIN_GOOD_FILLERS or word in PLAIN_GOOD_TAIL for word in words):
        return False
    # "ok" and "okay" on their own are how somebody takes an answer in: after "my dad died in
    # march" / "how long do i boil an egg" the next line "ok" was answered "Glad to hear it.",
    # which is the bot being pleased about the death. A soft word is only the answer to a
    # question, so the bot has to have just asked one - unless the person put it in a feeling
    # frame ("i feel ok"), which no acknowledgement of the bot's last line ever is. Without
    # either, the line is read the way it was before the soft words were known at all, so
    # "ok cool" stays the nod it is.
    soft = any(word in PLAIN_GOOD_ASKED for word in words)
    if soft and not (set(words) & PLAIN_GOOD_FRAME) and not _the_bot_just_asked_them(memory):
        return all(word in PLAIN_GOOD_WORDS or word in PLAIN_GOOD_FILLERS for word in words)
    return True


# The words the repeat reader puts in front of a line it hands back, so a reply that hands one
# back can be told from the reader saying there is nothing of its own to go back over.
MEANT_LEADS = tuple(sorted(lead.split("{", 1)[0].strip().lower()
                           for lead in meant.REPEAT_LEADS + meant.LEADS))


def _bare_feeling(clean):
    """The feeling a line made only of a feeling word and fillers names, or None."""
    rest = [word.strip(".,!?;:") for word in clean.split()]
    rest = [word for word in rest if word and word not in BARE_FILLER]
    if not rest or len(rest) > 2 or set(rest) & NOT_WORDS:
        return None
    for name, words in FEELINGS:
        if all(word in words for word in rest):
            return name
    return None
