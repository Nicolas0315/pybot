"""Part 5 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from .normalize import KIN, UP_TO_LEADS, strip_leaders
from .kinds_part_01 import (
    AFFIRM, QUESTION_WORDS, TIPS, TIPS_ABOUT, TIPS_AMOUNT, TIPS_SUBJECT, TIPS_WANTED,
)
from .kinds_part_02 import (
    ABOUT_BOT, ABOUT_BOT_END, ROBOT_WORDS, _has_any, SHORT_REPLIES, GOING_ON_WHEN, DOING_FILLER,
    BEEN_SAID, BEEN_WHEN, SPENT_TIME, STILL_COMING,
)
from .kinds_part_03 import (
    ANSWERING_A_QUOTED_ASK, BOT_LIFE, KEEPING_ASK, WHILE_ASK, _asks_how_the_bot_sees_me,
    _asks_where_the_bot_is, _asks_who_this_is, _capability_question, _how_long_itself, _when_itself,
    a_stop_ask,
)
from .kinds_part_04 import (
    A_HOW_MANY_OF_THE_BOTS_OWN, A_WHAT_ITS_LIKE, A_YOUR_KIN, A_YOUR_OWN_THING,
    _asks_about_its_experience, _asks_about_its_own_life, _asks_if_the_bot_is_a_product,
    _counts_its_own_doings, _recalls_their_own_line, _self_ask, OPENING_FRAME, OPENING_MAX,
    OPENING_WORDS, _talk_opening, A_PERSON_AFTER_A_POSSESSIVE, KIN,
)


def _about_bot_kind(text, words, norm=()):
    """Which kind of about-the-bot question this is, or None.

    "memory" asks what the bot remembers, "help" what it can do, and "identity" what it is;
    "warmth" asks what it makes of the person, which is the one ask about the bot that is about
    both of them. The reply modules pick the phrasing from this, so each kind is read on the
    words that actually ask it and nothing else is pulled in.
    """
    bare = " " + text.strip() + " "
    # `text` is the line with its clauses marked ("how long | can we talk for"), so the whole
    # sentence is read from it with the marks taken out: a shape split across two clauses ("is
    # there a limit to how long | we can talk") is one question.
    flat = (text or "").replace(" | ", " ").replace("|", " ")
    if WHILE_ASK.search(flat):
        # Before the memory branch, which answers "how long have you got" with the line about
        # keeping only this conversation - a question about the bot's memory put to somebody
        # asking about its time.
        return "while"
    if KEEPING_ASK.search(flat) or a_stop_ask(flat):
        return "keeping"
    if _asks_where_the_bot_is(norm):
        return "where"
    if _asks_who_this_is(norm):
        return "identity"
    if ANSWERING_A_QUOTED_ASK.search(text or "") and not _self_ask(norm):
        return None
    if _asks_how_the_bot_sees_me(norm):
        return "warmth"
    if "remember" in words and {"you", "your"} & words:
        return "memory"
    if _capability_question(list(norm)):
        return "help"
    if _asks_if_the_bot_is_a_product(norm):
        return "model"
    if _recalls_their_own_line(norm):
        # "what did i just tell you" is the person asking for their own line back: the "you" is
        # who they told it to and the verb is theirs. Read as a self-ask it was answered with the
        # line that says what the bot is ("I'm a chatbot - here to help and chat"), which says
        # nothing to somebody asking what they had just said, and the store's recall never ran.
        return None
    if _asks_what_is_new_with_the_bot(norm):
        # "what's new with you", "anything new with you", "what's been happening with you": the
        # bot's own side of the chat in the words that name "new" rather than a verb of doing.
        return "doings"
    if _asks_what_the_bot_has_been_doing(norm):
        # "what did you do at the weekend", "where were you last night": the bot's own past,
        # which it answers plainly rather than with the search hedge or a recap of the person's
        # line. Read before the generic self-ask, which caught "what did you get up to". The
        # manners question with no past in it ("what are you up to", "wuu2") keeps its own
        # reading and its own answer.
        return "doings"
    if _asks_whether_the_bot_is_about(norm):
        return "doings"
    if _asks_how_it_spends_its_time(norm):
        # "how do you spend your time", "what do you do with your day": the same ask as "what are
        # you up to" with the verb named. Read as an ordinary question it reached the search hedge
        # ("I don't know enough to answer that honestly"), which is no answer to a friendly
        # question about the bot's own day.
        return "doings"
    if (_asks_what_the_bot_is_doing(norm) and {"you", "u", "ya"} & words
            and words & ASKS_IF_ANYTHING):
        # "you doing anything tonight", "u up to anything this weekend", "are you up to much":
        # the same ask as "what are you up to", said from the front and with the time still to
        # come, so the past-ask reader stands aside and the manners opener is not there to catch
        # it. Read as smalltalk the evening card claimed it ("Give the evening a shape") on a
        # line that asked about the bot's evening, not the person's. The `you` has to be in the
        # line: "doing anything tonight" is the person's own evening and stays where it is.
        return "doings"
    if _asks_about_its_experience(norm):
        # "have you ever been to paris": the bot's own past, asked as an experience rather than
        # as a stretch of time. Same pool with a pool of its own for the "never" answer.
        return "doings"
    if _self_ask(norm):
        return "memory" if {"remember", "recall", "forget"} & words else "identity"
    if _how_long_itself(norm) or _when_itself(norm):
        # "how long have you been going" is a question about the bot's own history, and there is
        # only ever one answer to it: nothing came before this chat. The pool that says that is
        # the memory one, so the kind is "memory" rather than a word of its own - the composer
        # would otherwise answer a question about time with its line about having no address.
        return "memory"
    if _counts_its_own_doings(norm):
        # A tally of the bot's own chats or days: there is no such number to give, and the
        # memory answer is the honest one, so it is read the same way as "what do you remember".
        return "memory"
    if A_YOUR_KIN.search(" ".join(norm)) or A_YOUR_OWN_THING.search(" ".join(norm)):
        return "life"
    if (A_HOW_MANY_OF_THE_BOTS_OWN.search(" ".join(norm))
            and set(norm) & BOT_LIFE):
        return "life"
    if A_WHAT_ITS_LIKE.search(" ".join(norm)):
        return "identity"
    if _asks_about_its_own_life(norm):
        return "life"
    if _has_any(bare, ABOUT_BOT) or text.strip().endswith(ABOUT_BOT_END):
        return "identity"
    if {"you", "your"} & words and words & ROBOT_WORDS and "are" in words:
        return "identity"
    return None


def opening_line(norm):
    """True when the line only says a question is coming, or asks for advice in general."""
    words = [word for word in norm if word]
    if not words:
        return False
    text = " ".join(words)
    if _talk_opening(text):
        return True
    if len(words) > OPENING_MAX:
        return False
    if words[0] in {"have", "do", "does", "did"}:
        return False  # "have you got a question" asks the bot, it does not offer one
    if not all(word in OPENING_WORDS for word in words):
        return False
    return bool(OPENING_FRAME.search(text))


def _short_reply(text):
    """True when the whole line is one of the set replies people give after a question."""
    for phrase in SHORT_REPLIES:
        if text == phrase or text.startswith(phrase + " "):
            return True
    return False


# Saying you will do the thing the bot just suggested is an answer to the bot, not news about
# yourself. People leave the "I" off when they type quickly ("will give it a go", "gonna try
# that", "give it a go"), and the line then has no first person in it, which is what makes it
# look like a report and earns the "I don't know enough to answer that" shrug.
COMMIT_OPEN = frozenset("""will wont would gonna going sall ill il id weve well lets let""".split())


COMMIT_TRY = frozenset("""try give go see have take""".split())


# The subject people still type ("i will try that") and the spellings that carry both the
# subject and the "will" in one word ("ill give it a go", "id try that").
COMMIT_SUBJECT = frozenset("i we".split())


COMMIT_ALONE = ("give it a go", "give it a try", "give that a go", "give that a try",
                "give it a shot", "have a go", "have a try", "give it a whirl",
                "try that", "try it", "try this")


COMMIT_ALONE_TAIL = ("let you know", "sounds like a plan")


# A hedged commitment: "might give that a go", "could do that", "nice one, might do that". The
# hedge is not a "will", so the words after it have to be the whole commitment on their own -
# a bare "have" or "go" is something else entirely ("i might have a cold", "i could go for a
# coffee"), which is why these openers do not simply join COMMIT_OPEN.
HEDGED_COMMIT = frozenset("might could may".split())


HEDGED_ALONE = COMMIT_ALONE + ("do that", "do it", "go for it", "ring them", "call them")


# Talking themselves into it: "worth a try", "cant hurt", "no harm in giving it a go". The
# phrase carries the whole agreement at the front of the line, so at most a short tail follows
# it. "no harm in trying" opened on "no" and read as a denial before this.
COMMIT_NO_HARM = ("worth a try", "worth a go", "worth trying", "worth a shot",
                  "cant hurt", "cannot hurt", "no harm in", "nothing to lose")


# The words in front of a decision the person is still making ("i suppose its worth a try",
# "maybe worth a go"): they hedge the agreement, they do not stop it being one.
HEDGE_LEAD_ONE = frozenset("maybe probably suppose guess honestly".split())


HEDGE_LEAD_TWO = ("i suppose", "i guess", "i think", "i reckon")


# The thing that is worth trying is said in front of the phrase ("it cant hurt", "that worth a
# go"), and a "cannot" is two words by the time the reading gets it.
NO_HARM_SUBJECT = frozenset("it its that this there".split())


# What a commitment never carries: a question ("will i give it a go?"), or a second person as
# the thing given to ("will give you a ring" is a plan about someone else).
COMMIT_STOP = frozenset("""you u ya your yourself yall""".split())


def _cant_for_cannot(words):
    """The line as one string, with a split "can not" written back as "cant".

    The reading takes the apostrophe out ("cant" arrives as `can not`), and the phrases that
    carry an agreement are typed with the apostrophe left out, so the two have to be joined.
    """
    joined = []
    index = 0
    while index < len(words):
        if words[index] == "can" and words[index + 1:index + 2] == ["not"]:
            joined.append("cant")
            index += 2
            continue
        joined.append(words[index])
        index += 1
    return " ".join(joined)


def _agrees_to_try(norm):
    """True when the line is the person agreeing to do what was just suggested.

    "will give it a go", "gonna try that", "ok give it a go": the subject is dropped and the
    whole line is the commitment, so the only thing it can answer is the bot's last turn.
    """
    words = [word for word in norm if word and word != "|"]
    if not words or len(words) > 9:
        return False
    if any(word in QUESTION_WORDS or word in COMMIT_STOP for word in words):
        return False
    bare = " ".join(words)
    hedged = list(words)
    while hedged:
        if hedged[0] in HEDGE_LEAD_ONE:
            hedged = hedged[1:]
        elif " ".join(hedged[:2]) in HEDGE_LEAD_TWO:
            hedged = hedged[2:]
        else:
            break
    said = _cant_for_cannot(hedged)
    if said.split()[:1] and said.split()[0] in NO_HARM_SUBJECT:
        said = " ".join(said.split()[1:])
    if 0 < len(said.split()) <= 7 and any(said == phrase or said.startswith(phrase + " ")
                                          for phrase in COMMIT_NO_HARM):
        return True
    # The phrases that carry the whole agreement on their own. "try that" is the whole line;
    # "try that new thai place on friday" names something for later, and the plan reading is
    # the one that answers it, so a phrase only takes a short tail.
    if bare in COMMIT_ALONE:
        return True
    if any(bare.startswith(phrase + " ") and len(words) <= 5 for phrase in COMMIT_ALONE):
        return True
    if any(bare == phrase or bare.startswith(phrase + " ") for phrase in COMMIT_ALONE_TAIL):
        return True
    lead = strip_leaders(words)
    if lead[:1] and lead[0] in AFFIRM:
        lead = lead[1:]                       # "yes, i will try that"
        if lead[:1] == ["one"]:
            lead = lead[1:]                   # "nice one, might do that"
    if lead[:1] and lead[0] in COMMIT_SUBJECT:
        lead = lead[1:]                       # "ok i will try that"
    if lead[:1] and lead[0] in HEDGED_COMMIT:
        rest = " ".join(lead[1:])
        return any(rest == phrase or rest.startswith(phrase + " ")
                   for phrase in HEDGED_ALONE)
    if lead[:1] and lead[0] in COMMIT_SUBJECT:
        lead = lead[1:]                       # "ok i will try that"
    # Without the "will" the line is not a commitment: "i have a sore throat" and "take vat
    # off 240" open on the same verbs and report something completely different.
    if not lead or lead[0] not in COMMIT_OPEN:
        return False
    lead = lead[1:]                           # "will try that", "gonna give it a go"
    if lead[:1] == ["to"]:
        lead = lead[1:]                       # "going to try that"
    return bool(lead) and lead[0] in COMMIT_TRY


# A line that opens by asking whoever is there ("anyone know", "does anyone have") is a
# question to the room, not a statement about anyone: "anyone know a good plumber" wants a
# recommendation, and "any1 got a spare ticket" wants one too.
ASK_THE_ROOM = frozenset("""anyone anybody somebody someone everyone everybody any1 some1
    every1 evry1 no1""".split())


# "anyone/anybody" almost always ask the room; "someone/everyone" report as often as they ask.
ASK_THE_ROOM_ANY = frozenset("""anyone anybody any1""".split())


ASK_THE_ROOM_WANTS = frozenset("""where if how what which whether why who whom whose
    a an any some""".split())


ASK_THE_ROOM_VERB = frozenset("""know knows knew got have has had recommend recommends
    suggest suggests tried try seen see use uses found find want wants need needs""".split())


def _asks_the_room(stripped):
    """True when an open collective subject asks the room for something.

    "anyone/anybody know a plumber" asks. "someone got hurt", "everyone got the memo",
    "some1 found my keys" are reports: only a question word after the verb ("some1 know
    where to get tyres") turns a someone/everyone line into a question.
    """
    if len(stripped) < 2 or stripped[0] not in ASK_THE_ROOM:
        return False
    if stripped[1] not in ASK_THE_ROOM_VERB:
        return False
    if stripped[0] in ASK_THE_ROOM_ANY:
        return True
    if stripped[1] not in ASK_FOR_A_NAME:
        return False
    return len(stripped) > 2 and stripped[2] in ASK_THE_ROOM_WANTS


# The end of a line can ask for the answer without a question word in it: "i have a wedding in
# june and i need a dress, any ideas". These are the words that make the last clause of a line
# the ask rather than a second thing said.
TAIL_ASKS = frozenset("""ideas idea thoughts thought advice tips tip suggestions suggestion
    recommendations recommendation help pointers""".split())


TAIL_ASK_FILLER = frozenset("""any some more your please a quick few""".split())


# A setup is the situation a person describes before they ask; past a couple of sentences it is
# not a setup any more but two things said, and the reply belongs to the second half anyway.
SETUP_MOST_WORDS = 45


# Clauses that only hold the line together. "thanks, what should i cook tonight" has no setup:
# the person has said nothing about their situation yet.
SETUP_NOTHING = frozenset("""thanks thank you ta cheers hi hello hey morning evening goodnight ok
    okay right so well and but oh ah hmm um yeah yes no anyway alright lol haha lmao""".split())


# Words that join a situation to the question and name nothing in it. A setup made only of these
# is not a situation: "since when have you been about" reads "since" as the setup and "when have
# you been about" as the ask, and the answer is held to a word that says nothing.
SETUP_CONNECTIVES = frozenset("""since because cos cause and but so if when while although
    though as then also plus or with for to of in on at by from that it its this these those
    there here neither nor either both too same me""".split())


# A setup that only frames the question sets nothing up: "never mind, what is the tax deadline",
# "quick question, what time does tesco close", "honestly, what do i do". The situation these
# lines ask about is not in them, and the answer must not be held to the frame.
FRAME_NOT_A_SETUP = re.compile(
    r"^(?: (?:and |but |oh |well |so |ok |okay |right |no )?"
    r"(?:never mind|nevermind|i mean|i meant|you know what i mean|i dunno|dunno"
    r"|not sure|no idea|honestly|sorry|one more thing|one thing|another thing|quick one"
    r"|back to \w+(?: \w+){0,2}"
    r"|of course|fair enough|me too|same here|no worries|anyway|just wondering"
    r"|just asking|quick question|random question|random one|hi|hey|hello|hiya"
    r"|good question)\b(?: .{0,12})?)+$")


# A frame said at the very front of a situation, inside it rather than instead of it: the
# question is still about the situation, and the words of the frame are not part of it.
A_FRAME_IN_FRONT = re.compile(
    r"^(?:(?:hi|hiya|hey|hello|morning|evening|ok|okay|right|well|also|i mean|i meant"
    r"|honestly|sorry|cheers"
    r"|thanks|thank you|no worries|quick one|quick question|random question|random one"
    r"|one more thing|another thing|just wondering|just asking|lol|haha|lmao|anyway"
    r"|bit of a random one|bit random|random one|and|but|so)(?:[\s,.-]+|$))+", re.I)


def _says_nothing_but_the_floor(clause):
    """Whether the clause is only the words that hold a conversation together.

    "thanks, what should i cook tonight" says nothing about a situation, and neither does
    "ok thanks. also, should i worry about the damp patch" - the courtesy and the "also" are the
    turn, not the situation, and the answer must not be held to them.
    """
    words = set(strip_leaders(clause) or clause)
    return not words or words <= (SETUP_NOTHING | SETUP_CONNECTIVES)


# What a bare "any tips" is made of: the ask itself, with nothing it is tips about.
TIPS_FRAME = frozenset("""any some few got get need needs needed wanted looking look for
    share send give me us please pls thanks thank you tips tip hints hint pointers pointer
    advice a an the and or to on about this that it is are do have has i u my""".split())


# A line can say a question is coming without asking it: "got a q abt me boiler", "quick
# question about my tax", "can i ask you something". Nothing has been asked yet, so no entry can
# answer it, and the labels above (which all name something wanted *in* the line) are wrong for
# it. What the person wants is room to ask, so it is its own label and the reply invites it.
# `q` and `qs` are how people type "question"; a third-person line ("she asks too many
# questions") is left alone, and a line with the question already in it ("quick q what time do
# you close") is answered rather than invited.
QUESTION_NOUNS = frozenset("q qs question questions query queries".split())


ASKING_VERBS = frozenset("ask asks asked asking".split())


ASK_ABOUT = frozenset("about abt bout re regarding on with something anything".split())


# "any" is left out on purpose: "any questions" is the speaker offering to take them, not
# saying they have one. A line that does have one says so with "got", "have", "quick" or "ask".
ASK_FRAMES = frozenset("""a an and another ask asked asking but can could daft got have has
    hey hi i ive just little may mind need one please pls quick random silly small sorry stupid
    wanna want we would will""".split())


# The verbs that make a question noun an ask that already happened: "she asked me the same
# question three times yesterday" is not a question on its way, and widening the window to the
# noun was reading it as one. "ask" itself is not here: "can i ask a quick question" is coming.
PAST_ASK = frozenset("asked told answered repeated mentioned".split())


ALREADY_ASKED = frozenset("""what why how when where who which whose whether""".split())


# The verb "ask" only says a question is coming when the bot is the one being asked: "can i ask
# about my rads", "i want to ask you something". "i will ask about the shifts", "ill ask her when
# shes back" and "can i ask my boss for a raise" are asking someone else, so nothing is coming
# here and the line is answered (or noted) for what it says.
# The wants and needs are modals here too: "i want to ask about the boiler" and "i need to ask
# about the deposit" are the person asking the bot, and the word after "ask" still has to be
# `you`, `about` or a question noun, so "i want to ask my boss for a raise" stays out.
ASK_MODALS = frozenset("can could may might want wants wanted wanna need needs needed".split())


# The auxiliaries and the adverbs do the same job as the modals here, because the "ask" is not
# always in front of its modal: "im asking about my rads", "i was asking about my rads", "just
# asking about the deposit" and "im just asking about the deposit" are all the person asking the
# bot, and the bot answering those with a shrug was the coldest thing in the conversation. The
# word after "ask" still has to be `you`, `about` or a question noun, so "i was asking her about
# the shifts" is still asking somebody else.
ASK_AUX = frozenset("""am is are was were im be been being just only still actually ever also
    always""".split())


ASK_TARGET = frozenset("you u something somethin anyone anybody".split())


# The verbs that hand the asking over: "give me a quiz question", "ask me a question", "quiz
# me", "throw me a question". The person is the one who will answer, so the question is what
# the line wants, not something it is about to say, and reading it as `question_coming` got it
# the invitation meant for the other direction ("Ask away, I'm listening" to someone who has
# just asked to be asked). Only a hand-over to the speaker counts: `me` and `us` after the verb.
# A promise keeps its reading, because the speaker is the one who will ask: "can i ask you a
# question", "i have a question for you", "let me ask you something".
HAND_OVER_VERBS = frozenset("""give gives gave send sends sent throw throws threw chuck chucks
    hit hits fire fires read reads bring brings brought pass passes offer offers ask asks quiz
    quizzes test tests""".split())


HAND_OVER_TO = frozenset("me us".split())


# What the person puts forward instead of themselves: "test my knowledge", "test our trivia",
# "quiz my brain". A possessive and one of these is the same ask as "quiz me".
HAND_OVER_MINE = frozenset("knowledge trivia quiz quizzes iq memory brain".split())


# The words that can sit in front of the hand-over and still leave the speaker as the one asking:
# a modal or a courtesy. Any other word in front of the verb is a subject of its own, and a third
# person handing the question over is somebody else's business: "she gave me a question to answer",
# "he asked me a question", "my daughter asked me a question" keep the reading they had.
HAND_OVER_LEADS = frozenset("""please pls plz kindly just maybe perhaps ok okay so and then now
    also quick quickly""".split())


HAND_OVER_MODALS = frozenset("can could will would should".split())


# The subjects a hand-over can stand behind and still be the speaker's ask: "can you quiz me" and
# "could u ask me one" put the bot's name in front of the verb. Any subject without a modal in
# front of it is somebody else doing the handing over, and that question is not on its way to
# this person at all: "she quizzed me", "my daughter asked me a question".
HAND_OVER_SUBJECTS = frozenset("you u ya".split())


def _hands_a_question_to_the_speaker(norm):
    """True when the line itself asks for a question to answer: "quiz me", "give me a question".

    The verb has to open the line, or stand behind nothing but a modal or a courtesy, so the
    person is the one doing the asking. "she quizzed me" and "he asked me a question" are a
    question that already happened to somebody, and reading them as a request to be quizzed put
    a general-knowledge question in front of a person who had said nothing of the kind.
    """
    words = [word for word in norm if word and word != "|"]
    for at, word in enumerate(words[:-1]):
        if word not in HAND_OVER_VERBS:
            continue
        handed_to = (words[at + 1] in HAND_OVER_TO
                     or (words[at + 1] in ("my", "our") and at + 2 < len(words)
                         and words[at + 2] in HAND_OVER_MINE))
        if not handed_to:
            continue
        before = words[:at]
        if not before:
            return True                                # "quiz me", "give me a question"
        modal = any(w in HAND_OVER_MODALS for w in before)
        if not all(w in HAND_OVER_LEADS or w in HAND_OVER_MODALS
                   or (modal and w in HAND_OVER_SUBJECTS) for w in before):
            continue                                   # a subject of its own: somebody else
        if modal or not any(w in HAND_OVER_SUBJECTS for w in before):
            return True                                # "can you quiz me", "please ask me one"
    return False


def _asks_a_question_coming(norm, text):
    """True when the line says a question is coming without asking it yet."""
    if not 0 < len(norm) <= 12 or "?" in text or set(norm) & ALREADY_ASKED:
        return False
    if _hands_a_question_to_the_speaker(norm):
        # "give me a quiz question" hands the asking to the bot: the question is what the line
        # wants, not something it is about to say. A third person handing one over ("she gave me
        # a question to answer") is not this person asking, so that line reads as it always did.
        return False
    if norm[0] in {"do", "does", "did", "any"}:
        # "does anyone have any questions" is asking the room, and "any questions" is
        # offering to take them: neither is the speaker saying they have one.
        return False
    if norm[0] in {"have", "has"} and len(norm) > 1 and norm[1] in {"you", "u", "anyone",
                                                                  "anybody", "any", "they"}:
        return False     # "have you got a question" asks the bot, it does not offer one
    for at, word in enumerate(norm[:5]):
        if word == "asked" and at == 1 and norm[0] in {"i", "we"}:
            continue     # "i asked about the boiler" is a past ask, not one on its way
        if set(norm[:at]) & PAST_ASK:
            continue     # "she asked me the same question three times": the ask already happened
        after = norm[at + 1] if at + 1 < len(norm) else ""
        asked_here = (word in ASKING_VERBS
                      and after in ASK_TARGET | ASK_ABOUT
                      and (at == 0  # "ask about the rota": the verb opens the line
                           or any(before in ASK_MODALS | ASK_AUX for before in norm[:at])
                           or after in ASK_TARGET))
        named = word in QUESTION_NOUNS or asked_here
        if not named:
            continue
        if at == 0 or any(before in ASK_FRAMES for before in norm[:at]):
            return True
    return False


def _asks_for_tips(text, norm=()):
    """True when a tip word here asks for advice, not a tip being left or given.

    "any tips for a roast", "tips for a job interview", "got any hints about sourdough" and
    "any tip on painting a door" ask; "a 10% tip", "he tips well", "tip the delivery driver"
    and "the tip of my knife broke" are about a thing or an action.

    A bare "any tips" with nothing in the line it is tips about is not read as an ask: the
    subject it follows in the conversation (a bad night's sleep) is what an answer needs, and
    turning the line into a request only swaps the ack for "I would rather not guess".
    """
    about = [word for word in norm if word not in TIPS_FRAME]
    for match in TIPS.finditer(text):
        before, after = text[:match.start()], text[match.end():]
        if TIPS_AMOUNT.search(before):
            continue
        if TIPS_WANTED.search(before):
            if about:
                return True
            continue
        if match.group(1) in ("tips", "hints", "pointers"):
            if TIPS_SUBJECT.search(before):
                continue
            if TIPS_ABOUT.match(after) or not after.strip(" ?.!,"):
                return True
    return False


# People ask the bot things without the auxiliary: "u think i should quit coffee", "you
# reckon i should go", "you seen this film". The subject is the bot, so the line opens like a
# statement but asks a question.
YOU_WORDS = frozenset("you u ya ur dya".split())


# Only the verbs that ask the bot for its view. A verb that takes an object ("you seen this
# film", "you saw that coming") is a remark as often as a question, so it is left alone.
ASK_VERBS = frozenset("think reckon guess recommend suggest mind".split())


# What comes after the verb decides it: "you think i should quit" asks, "you think too much"
# does not, and "you got this" is a statement of fact.
ASK_FOLLOW = frozenset("""i we us ill im id it its that this these those she he they them
there my your our their should can could will would shall is are was were do does did if
whether what when where who which why how any anything something someone""".split())


def _asks_the_bot(norm):
    """True when the line asks the bot something in the second person."""
    if len(norm) < 3:
        return False
    return (norm[0] in YOU_WORDS and norm[1] in ASK_VERBS and norm[2] in ASK_FOLLOW)


# A person drops the "is there" and the question mark: "any word on the job", "any luck with the
# boiler", "any chance of a refund" are questions about the thing after the link, and read as
# statements they got the shrug instead of an answer ("I'm listening - say more if it helps").
# The word in front is only the kind of answer wanted, never the subject.
# "news" is left out on purpose: asking for the news asks for a briefing, and the honest "I
# can't see the news from here" already answers it. Read as a question about the thing, the bot
# answered it from the small-talk pool instead ("None that I know of. What's been the best bit of
# your week?"), which is no answer to "any news on the trains".
# "progress" and "update" are left out: they ask how a thing the person has in hand is getting
# on ("any progress on the leak", "any update on my parcel"), and no card knows that, so read as
# a question the bot searched and said so - where the nod the line got before was the honest
# reply. The words here ask for something the bot can answer from what it knows.
ANY_ANSWER_WANTED = frozenset("""word words luck idea ideas chance chances
    joy sign signs hint hints intel new else""".split())


ANY_ANSWER_LINKS = frozenset("on about with from of for regarding concerning re".split())


# An ask for a list already asks, so the frame adds nothing to it: "any ideas for a cheap night
# out" is a request for suggestions, and read as a question it lost the list answer and got a
# shrug. Only the plural of a list word is here, because it is the only one of the answer words
# that asks the same thing the frame adds to the others.
ANY_ALREADY_ASKS = frozenset(("idea", "ideas"))


def after_any_link(norm):
    """The words after the link in "any news about X", or () when the line is another shape.

    The tuple is what the line is about: "any word on the job" is about the job, and read whole
    the topic was the word it was asked with. A line that only says the kind of answer wanted
    ("any luck?") has nothing after the link, so it keeps the conversation's subject, and so does
    one that puts the whole ask after it ("any idea how to stop him"): there the ask is the line
    and the thing it is about came from the turns before.
    """
    if not norm or norm[0] not in ("any", "anything"):
        return ()
    if len(norm) < 2 or norm[1] not in ANY_ANSWER_WANTED:
        return ()
    for at in range(2, len(norm)):
        if norm[at] in ANY_ANSWER_LINKS:
            return tuple(norm[at + 1:])
    return ()


def _asks_after_any(norm):
    """True for "any word on the job" and its cousins, which ask without a question mark.

    It has to name the thing after the link. "any luck" and "any ideas" on their own are
    already read as well as they can be, and a bare frame says nothing new about the line.
    """
    if not norm or len(norm) < 2 or norm[1] in ANY_ALREADY_ASKS:
        return False
    about = after_any_link(norm)
    return bool(about) and not _names_a_person(about)


def _names_a_person(words):
    """True when the tail of an "any word about X" names a person rather than a thing."""
    return any(words[at] in OWNS_A_PERSON and words[at + 1] in A_PERSON_NAMED
               for at in range(len(words) - 1))


# Asking the room for a name is asking for a recommendation: "anyone know a good plumber".
ASK_FOR_A_NAME = frozenset("""know knows knew recommend recommends suggest suggests
    found find""".split())


# "best" and "better" ask for a recommendation when they pick out one thing ("the best way",
# "a better option"). After a word that says how somebody is doing they are not asking for
# anything: "i feel better today", "im doing much better", "i want to eat better" are reports
# about the speaker, and an ask read into them makes the bot answer a statement with a hedge.
COMPARATIVE = frozenset(("best", "better"))


DESCRIBES = frozenset((
    "feel", "feels", "feeling", "felt", "do", "does", "did", "doing", "done", "get", "gets",
    "getting", "got", "look", "looks", "looking", "seem", "seems", "am", "is", "are", "was",
    "were", "be", "being", "been", "much", "any", "lot", "sleep", "sleeping", "slept", "eat",
    "eating", "ate", "cope", "coping", "manage", "managing",
))


# A comparative followed by one of these is about how somebody is: "better thanks", "better
# today". "better than" and "the best way" pick something out, so they still ask.
AFTER_COMPARATIVE = frozenset((
    "thanks", "thank", "today", "tomorrow", "yesterday", "now", "tonight", "though", "again",
    "yet", "already", "honestly", "actually", "here", "since", "after",
))


# In front of the word for a person the comparative names that person and picks nothing out: "my
# best friend is getting married in june", "im the best man", "my better half is cooking". Read
# as a request they went looking for advice nobody had offered and got the search hedge - the
# wedding line was answered "I'm not sure about that one, sorry - I'd rather not guess" - while
# the same news with "close" or "oldest" in front of it was answered properly. Only the words a
# person is called, so "the best way", "the best time" and "a better option" still ask.
A_PERSON_AFTER = frozenset("""
    friend friends friend's friends' mate mates mate's pal pals man men woman women half buddy
    bud fella lad matey mother father sister brother son daughter partner wife husband
    wishes regards
""".split())


# "any word from my sister" asks about a person, and nothing in the knowledge base knows her: as
# a question it turned a listening reply into a search punt, which is worse than what it had. A
# tail that names a person is left as it was; a service is not a person and keeps its answer
# ("any word from the vet" reaches the vet card).
A_PERSON_NAMED = (A_PERSON_AFTER_A_POSSESSIVE | KIN | A_PERSON_AFTER
                  | frozenset("""boss bosses manager managers colleague colleagues
                      neighbour neighbours neighbor neighbors teacher teachers doctor
                      doctors gp dentist dentist's""".split()))


OWNS_A_PERSON = frozenset(("my", "our", "his", "her", "your", "their", "me"))


# " or " and "better than" compare things; a bare substring is not enough, because "better
# thanks" contains "better than".
COMPARISON = re.compile(r"(?:\s+or\s+|\bbetter than\b|\binstead of\b|\bversus\b|\bvs\b)")


# "How about you", "what about yourself", "and you": the question turned back on the bot. Read
# as an ordinary question it asks for a fact the bot does not have, and gets "that's beyond what
# I know well, sorry - searching for it will turn up better sources", which is the wrong reply to
# "hbu" after the bot has asked how the day went.
ASKS_IT_BACK = ("how about you", "what about you", "how about yourself", "what about yourself",
                "and you", "and yourself", "you yourself", "what about u", "how about u",
                "how about yours", "what about yours", "and yours")


# "and" is part of the phrase itself ("and you"), so it is not stripped here.
FILLER_BEFORE = ("so", "ok", "okay", "oh", "yeah", "but", "well")


# A filler on the end of the question does not make it a new question: "how about you then".
FILLER_AFTER = ("then", "though", "now", "anyway", "huh", "eh")


# "bout" is how people write "about", but it is also a real word, so it is only read this way
# inside these two phrases, never by the normaliser.
BOUT = {"bout": "about"}


def _ask_words(norm):
    """The words of a line that may be a question turned back, fillers and "bout" removed."""
    words = [BOUT.get(word, word) for word in norm]
    while words and words[0] in FILLER_BEFORE:
        words.pop(0)
    while words and words[-1] in FILLER_AFTER:
        words.pop()
    return words


def _asks_it_back(norm):
    """True when the whole line is the question turned back on the bot."""
    return " ".join(_ask_words(norm)) in ASKS_IT_BACK


# The greetings people type without the words "how are you": "hows u" reads as "how is you",
# "hows things" as "how is things", "how you doing", "what u saying", "u ok". The small-talk
# list holds the phrases as said, and these are the same greeting with the verb or the subject
# written another way, so they are read as a shape instead of one phrase per spelling. Every
# word has to be part of the greeting - "how is life in spain" and "how are you supposed to
# defrost a turkey" name something, so they are questions and not a greeting.
GREETING_ASK_WORDS = frozenset("""
    how what whats is are was were am be been r u ya you your yours yourself yourselves the
    things everything life day days week weekend evening morning night
    going doing doin do been getting keeping saying say much
    today tonight then now lately anyway mate love friend
    all alright ok okay good fine well too so it have has having
""".split())


# The words that stand for the person being asked after: "hows things", "hows life". They are
# the subject of the greeting, so a line has to have one of these or a "you" to be one.
GREETING_ASK_SUBJECT = frozenset("""you u ya your yours yourself yourselves things everything
    life day days week weekend evening morning night""".split())


# A line that is only "u ok", "you alright", "you good" is the same greeting with the "how" left
# off. It is told apart from the short agreement "you too" by the state word, which an agreement
# does not have.
GREETING_ASK_STATE = frozenset("ok okay alright good fine well".split())


GREETING_ASK_ABOUT_SOMETHING = frozenset("with about to for if when on at in".split())


# The short shape has no "how" in it, so the person has to be named for it to be the greeting:
# "you good" and "u ok" ask after the bot, and "good morning" and "good day" are greetings that
# say nothing about how anyone is.
GREETING_ASK_SECOND_PERSON = frozenset("you u ya your yours yourself yourselves".split())


# A greeting that opens on "what" is the "what are you saying" shape and nothing else: the same
# words with a day in them ask the date ("what day is it"), and "what are you doing" asks how
# the bot fills its time, which has its own answer.
GREETING_WHAT_SAYING = frozenset("""what are is r you u ya saying say sayin then now there
    mate all""".split())


def asks_how_i_am(norm):
    """True when the whole line asks the bot how it is, however the greeting is spelled.

    This is the greeting as a shape, so it does not depend on which spelling of it a phrase
    list happens to hold: "how you been", "hows everything" and "what u saying" are the same
    question as "how are you", and the caller that answers one answers them all. A state word
    followed by "with", "about", "to" and the rest asks about something else ("you ok with
    that", "you alright to drive"), so the short shape stands down for it.
    """
    # "hows everything with you" and "how are you doing with yourself": the person adds "with
    # you" to the same greeting, so the tag is dropped rather than read as asking about a thing.
    while len(norm) > 2 and norm[-2] == "with" and norm[-1] in GREETING_ASK_SECOND_PERSON:
        norm = norm[:-2]
    if not norm or len(norm) > 8:
        return False
    words = set(norm)
    if not words & GREETING_ASK_SUBJECT:
        return False
    if norm[0] == "what":
        return words <= GREETING_WHAT_SAYING
    if norm[0] != "how":
        if len(norm) > 4 or not words & GREETING_ASK_STATE \
                or not words & GREETING_ASK_SECOND_PERSON:
            return False
        at = next(index for index, word in enumerate(norm) if word in GREETING_ASK_STATE)
        # The person comes before the state in the greeting ("u ok", "you good"); a line that
        # puts the state first and the person after it agrees with what was just said ("ok nah
        # ur right"), which is not a question about the bot.
        if not any(word in GREETING_ASK_SECOND_PERSON for word in norm[:at]):
            return False
        return not (len(norm) > at + 1 and norm[at + 1] in GREETING_ASK_ABOUT_SOMETHING)
    return words <= GREETING_ASK_WORDS


# A line that ends in one of these is asking to be told it is true, not telling news:
# "im in a union so that should help right", "nowt wrong with the boiler, its just noisy innit".
# "right" is also an adjective ("i cant do anything right", "ur right"), so it only counts
# after a word that can end a statement, never after the words that make "right" a complement.
TAG_RIGHT_NOT = frozenset("""i me my mine you your yours he him his she her hers it its we us our
    ours they them their theirs this that these those there here what who which whose
    all any anything everything something nothing none both each either neither another
    such same very quite too so just still even only also always never ever really pretty
    probably maybe perhaps definitely certainly nearly almost exactly absolutely totally
    completely obviously clearly simply possibly surely indeed actually basically honestly
    literally truly about around much many more most less least enough not no yes yeah ok
    okay right
    is are was were am be been being do does did done have has had having can could will
    would shall should may might must need ought feel feels felt look looks looked seem
    seems seemed sound sounds sounded taste tastes tasted smell smells smelled get gets got
    gotten go goes went gone keep keeps kept turn turns turned make makes made put puts set
    sets work works worked
    off on out up down in back over through round around at
    fine ok okay alright good better worse ready done sorted""".split())


TAG_ENDINGS = frozenset(("right", "innit"))


# A tag on a plan or an event is an announcement, not a claim to be checked: "my nan is coming
# sunday right" wants a warm nod, and the question path answers it with a search hedge. The
# words of a day, a time or a meal are what make it a plan; "i take one of these a day" is a
# routine, and a time after "at" ("picking me up at eight") is when something happens.
TAG_PLAN = GOING_ON_WHEN | frozenset("""day days dinner lunch breakfast tea supper later soon
    next""".split())


TAG_TIME_NUMBER = frozenset("""one two three four five six seven eight nine ten eleven twelve
    half""".split())


# A tag is a question only when the body says something the bot could check: a modal ("that
# should help", "i can get a chargeback") or a fact verb ("she gets the payment", "you said").
# News is not checkable - "i got the job right", "i passed", "my sister had the baby", "we are
# off to spain" - and those want the warm reply they already get, not a search hedge. Nor is a
# plain fact about someone's life ("she works at the hospital right", "you pay at the machine
# right"): the bot cannot check it, so a search hedge is the wrong reply there too. The verb
# has to be one that asks for a rule or a fact to be confirmed, not just any verb.
TAG_CHECKABLE = frozenset("""should shouldnt shall can cant could couldnt will wont would wouldnt
    may might must ought needs need gets said says told tells""".split())


def _tag_tells_a_plan(norm):
    """True when the body of the line before the tag is a plan or an event with a time."""
    body = norm[:-1]
    if any(word in TAG_PLAN for word in body):
        return True
    return any(word == "at" and body[index + 1] in TAG_TIME_NUMBER
               for index, word in enumerate(body[:-1]))


def _tag_checks_a_fact(norm):
    """True when the body before the tag says something the bot could confirm."""
    body = norm[:-1]
    for index, word in enumerate(body[:-1]):
        # "it should be fine innit", "we should be there by six right": a modal before "be" is
        # how something is expected to turn out, not a fact the bot can check. The question path
        # answers those with a search hedge, which is worse than the warm nod they had.
        if word in TAG_CHECKABLE and body[index + 1] == "be":
            return False
    return any(word in TAG_CHECKABLE for word in body)


# The same question with the day named: "how about your day", "what about your weekend", "was
# your day good". "your" makes the day the bot's own, so nothing in the world is being asked
# either - read as an ordinary question it goes to the knowledge base and gets "I don't know
# enough to answer that honestly". Only a day word after "your" counts, and the line has to end
# there (or on how it went), so "what about your day at the beach" is still about the beach.
BOT_DAY_WORDS = "|".join(("day", "weekend", "week", "evening", "morning", "night"))


BOT_DAY_SHAPES = tuple(re.compile(pattern.format(day=BOT_DAY_WORDS)) for pattern in (
    r"(?:how|what) about (?:your|ur) (?:{day})(?: (?:been|going|gone|so far))?",
    r"(?:how|what) about yours",
    r"and (?:your|ur) (?:{day})(?: (?:been|going|gone|so far))?",
    r"and yours",
    r"(?:how|what)(?:s|'s| is| was| are| were) (?:your|ur) (?:{day})"
    r"(?: (?:been|going|gone|good|ok|okay|fine|busy|alright|so far))?",
    r"(?:was|were|is|are|did) (?:your|ur) (?:{day})(?: (?:good|ok|okay|fine|busy|alright|nice))?",
    r"(?:did|have|had) you have a (?:good|nice|ok|okay|busy|long|lovely|great) (?:{day})",
    r"hope (?:you had|youre having|you are having) a (?:good|nice|lovely|great|ok|okay) (?:{day})",
))


def _asks_about_the_bot_day(norm):
    """True when the whole line asks the bot about its own day."""
    words = _ask_words(norm)
    if not words:
        return False
    line = " ".join(words)
    return any(shape.fullmatch(line) for shape in BOT_DAY_SHAPES)


# The indefinite a line asks about fills its time with: "you doing anything tonight", "u up to
# something this weekend". The bot's own doings read from the front, and only these words make
# it that ask - "you up to much" and "what are you up to tonight" are the manners question the
# warmth pool already answers, and the honest short answer is colder than the warm one there.
ASKS_IF_ANYTHING = frozenset("anything something nothing owt".split())


# The same ask with the verb named: "how do you spend your time", "what do you do with your day",
# "how do you fill your evenings". The person is asking what the bot's day is made of, so the
# question is read as the bot's own doings rather than left to the search hedge.
SPENDS_ITS_TIME = re.compile(
    r"\b(?:how|what)\b[^.]{0,24}?\b(?:spend|spends|spending|fill|fills|filling|use|uses)\b"
    r"[^.]{0,20}?\b(?:your|you)\b[^.]{0,16}\b(?:time|day|days|evening|evenings|hours?|"
    r"life|nights?)\b|\b(?:what do|what does)\s+you\s+do\s+(?:all\s+)?(?:day|with your|"
    r"during the|in the)\b")


def _asks_how_it_spends_its_time(norm):
    """True for "how do you spend your time" and its neighbours, in the words they are typed."""
    if not norm or len(norm) > 12:
        return False
    words = set(norm)
    if not words & {"you", "u", "ya", "your", "ur"}:
        return False
    return bool(SPENDS_ITS_TIME.search(" ".join(norm)))


# A short line asking whether the bot is about at a time: "you busy tonight", "u got much on
# tonight", "you about tomorrow", "you free this weekend". The line has the bot as its subject and
# a time, and that is the whole of it - read as nothing in particular it got the opening line
# ("I'm a chatbot - here to help and chat"), which is no answer to somebody working out whether
# there is anybody here this evening. The bot's own doings answer it, as they answer the same ask
# with an indefinite in it.
ABOUT_AT_A_TIME = frozenset("""tonight tomorrow today later weekend weekends morning afternoon
    evening night now soon week""".split())


# The words that ask it without a time: "you busy", "u free".
FREE_OR_BUSY = frozenset("busy free".split())


# A short ask about the bot itself has no first person in it: "im busy tonight" is the person's
# own evening and nothing to do with the bot.
FIRST_PERSON = frozenset("i im id ive me my mine we us our".split())


# The words that make a short line the manners question rather than this ask, kept with the arm
# that reads them so the two cannot drift.
MANNERS_WORDS = frozenset("up doing much keeps keeping".split())


def _asks_whether_the_bot_is_about(norm):
    """True for "you busy tonight" and its neighbours: the bot, a time, and nothing else."""
    if not norm or len(norm) > 6:
        return False
    words = set(norm)
    if not words & {"you", "u", "ya", "ur", "your"}:
        return False
    if words & FIRST_PERSON:
        return False
    if words & MANNERS_WORDS:
        # "what are you up to tonight" and "you up to much" are the manners question, and the warm
        # answers they have ("No plans. I'm around if you want to talk something through.") are
        # better than the bot's honest nothing.
        return False
    return bool(words & ABOUT_AT_A_TIME) or bool(words & FREE_OR_BUSY)


MANNERS_OPENERS = frozenset("what whats wats".split())


# When the same ask names a time: "what are you up to later", "what are you up to this weekend",
# "what are you doing after work tomorrow". Every other word of the line still has to be the ask
# itself, so "what are you doing at the weekend with the kids" stays a line about the kids.
WHEN_IN_THE_ASK = frozenset("""later tomorrow morning afternoon evening night weekend weekends
    week weekdays this these days coming soon next""".split())


# The spellings of "what are you" said out loud: "watcha up to", "whatcha doing". No dictionary
# has any of them, and the words after them say which is meant - "up to" and "doing" are this
# ask, "mean" is not.
SAYS_WHAT_ARE_YOU = frozenset("watcha whatcha wotcha watchu whatchu watchya whatchya".split())


# The words "what keeps you busy" is made of: the ask, the verb the other way round, the person,
# "busy", and the handful of words a person adds to the same question.
KEEPS_BUSY_SHAPE = frozenset("""what whats wats is keeps keeping you u ya busy so then mate
    today tonight now lately these days though anyway""".split())


def the_manners_question(norm):
    """True when the whole line asks how the bot is filling its time, however it is spelled.

    "what are you up to", "whatcha doing today", "watcha up to mate". The same words put any
    other way are a different ask: "u up" is whether anyone is there, and "what are you doing
    with that" is about the thing in the person's hand, so the line has to open on `what` and
    be made of nothing but the ask itself.
    """
    # A greeting in front of the ask is the same ask: "hey whatcha doing today", "hiya what are
    # you up to". Read as anything else the lead word made the opener test fail, and the ask
    # then read as a plan about the person's own week ("Pick two things and put them in the diary
    # by Friday") - black-lantern's find on this row.
    lead = 0
    while lead < len(norm) and norm[lead] in UP_TO_LEADS:
        lead += 1
    norm = norm[lead:]
    if not norm or (norm[0] not in MANNERS_OPENERS and norm[0] not in SAYS_WHAT_ARE_YOU):
        return False
    words = set(norm)
    if not {"you", "u", "ya"} & words and norm[0] not in SAYS_WHAT_ARE_YOU:
        return False
    if "been" in words and {"do", "doing"} & words:
        # "what have you been doing" is the literal past ask - the bot has no yesterday, and the
        # answer that says so is the bot's own doings, not a greeting.
        return False
    if "busy" in words and {"keeps", "keeping"} & words:
        # "what keeps you busy", "whats keeping you busy": the same ask with the verb the other
        # way round. The shape is named, because "what keeps you up at night" says "up" and is a
        # question about what worries somebody, not about how they fill the day.
        return words <= KEEPS_BUSY_SHAPE
    if not {"up", "doing", "doin", "do", "at", "been"} & words:
        return False
    if words & WHEN_IN_THE_ASK and not {"up", "doing", "doin", "at", "been"} & words:
        # "what do you do on weekends" asks what the bot is for, and the capabilities card is
        # that answer. Only the ask that names a time *and* a doing is this one: "what are you
        # up to later", "what are you doing on saturday".
        return False
    return all(word in DOING_FILLER or word in WHEN_IN_THE_ASK for word in norm)


# "What's new with you", "anything new with you", "what's going on with you", "what's been
# happening with you": the same ask as "what have you been up to" - the bot's own side of the
# chat - said with the word "new" or with "going on" instead of a verb of doing, so neither
# reader below saw it. All of them went to the search hedge ("That's beyond what I know well,
# sorry. Searching for it will turn up better sources") or to the nod, while the ask one word
# away from it ("what have you been up to") got the honest answer.
#
# The shape is closed by its own vocabulary and by the owner: the words have to be the ask, the
# "new"/"going on"/"happening" frame, and a word for the bot, with nothing named after it. That
# keeps "what's new with my car", "what's new at work", "what's new in town", "what's new with
# the world" (the news) and "what's new with the kids" out of it: every one of them names a thing
# the bot has no side of. A span of time ahead ("what's new with you tonight") is a presence
# check, and it keeps its own reading.
# "whats" is read as two words ("what is") and "whats been" as "what has been", so the two
# little verbs the fixer puts back are here beside the ask words.
NEW_ASK_WORDS = frozenset("""what whats is was has have u you ya your yours with in on going
    happening been new anything something nothing else tell me us mate pal friend hey hi hello
    so and now then lately world side day days weekend week""".split())


NEW_FRAME = frozenset("new going happening been".split())


NEW_ASK_AHEAD = frozenset("""tonight tomorrow later next saturday sunday monday tuesday
    wednesday thursday friday""".split())


def _asks_what_is_new_with_the_bot(norm):
    """True for "what's new with you" and the same ask in the words people type it in."""
    words = set(norm)
    if not words or len(norm) > 9:
        return False
    if not words & {"you", "u", "ya", "your", "yours"}:
        return False
    if not words & NEW_FRAME:
        return False
    if words & NEW_ASK_AHEAD:
        return False
    return words <= NEW_ASK_WORDS


def _asks_what_the_bot_is_doing(norm):
    """True for a line whose whole content is asking the bot how it is filling its time."""
    if not norm or len(norm) > 10:
        return False
    if not ({"doing", "do"} & set(norm) or norm[-1] in ("to", "much", "on")
            or "up" in norm):
        return False
    # "going on" also names things happening in the world, so a line that says when it is
    # asks what is on: "anything going on tonight" and "much going on this week" are about the
    # evening, not about the bot. Without a time word it is the bot's own doings.
    if {"going", "on"} <= set(norm) and set(norm) & GOING_ON_WHEN:
        return False
    if all(word in DOING_FILLER for word in norm):
        return True
    return _asks_what_the_bot_has_been_doing(norm)


def _asks_what_the_bot_has_been_doing(norm):
    """True for the same ask with the time named, as long as that time has already gone.

    "what did you do yesterday", "what were you up to at the weekend", "where were you last
    night": the bot has no yesterday and no Saturday, so the honest answer is that it has
    nothing of its own to report. Read as ordinary questions these went to the search hedge, to
    the weekend-plan advice, or to "we're still at the beginning" as if the person had said what
    they did. A day still to come is not this ask (`STILL_COMING`), and neither is a line that
    puts the past auxiliary to work on a thing: "what did you do with the leftover paint".
    """
    words = set(norm)
    if not words & {"you", "u", "ya", "your", "yours"}:
        return False
    if words & STILL_COMING:
        return False
    if not words & BEEN_SAID:
        return False
    # A day behind them and a past auxiliary are what make it the same ask as "what have you
    # been doing": "what do you do at the weekend" is a different question, and the manners
    # question in the present tense ("what are you up to", "wuu2") is a different one again.
    if not words & {"did", "done", "been", "were", "was", "had"} and not words & BEEN_WHEN:
        return False
    if ("where" in words and words & SPENT_TIME
            and words & {"have", "has", "been", "were", "was"}):
        # "where have you been all day", "where have you been hiding", "where were you last
        # night": a place question about time the bot is supposed to have spent. Read as a
        # place, the chat module's address line does not fit ("nowhere you could visit" answers
        # where it is, not where it was); read as nothing, all three went to the search hedge.
        return True
    # The english `do` has to be in the line, or the ask is about something else. Two readers
    # sent back the same two families without it: "where were you" is a question about a place
    # (the bot answers it by saying it has no address, which is the answer) and "what have you
    # been up to" is a greeting, whose warm answer is the small-talk one. "what have you been
    # doing", "what did you do yesterday" and "what did you get up to" keep the ask they had.
    if not words & {"do", "does", "did", "done", "doing"}:
        return False
    return all(word in DOING_FILLER or word in BEEN_WHEN or word in BEEN_SAID for word in norm)
