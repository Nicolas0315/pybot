"""Part 1 of 6 of the module, split out of `repeat`.

Everything here is re-exported from `repeat`, so callers import it from there as before.
"""
import re

from ..understanding import understand
from . import topics



# `helps` and `helped` sit beside `help` because a bare "what helps" is the same ask back as
# "what should i do" and was not read as one: a word boundary leaves "helps" behind as a word
# of its own, so the line named something of its own and every reader that asks "does this
# line name a thing" stood aside. It reached a search hedge ("im tired all the time" / "what
# helps") where `deck/a-bare-ask-that-lost-its-answer` has rows saying a person means the
# doing the answer just gave.
# The words a line can be made of and still ask nothing of its own: a way of asking for what to
# do, look for, try or do next, with no thing named.
ASK = frozenset("""
    what whats how where when which why who
    do does doing done now next then instead else anything something
    look looking start begin fix sort try use get make buy take stop
    should shall can could would will may might have has had
    i me my we you your it its that this these those there
    the a an again more better please tell say said too as well
    go going work help helps helped helping suggest recommend about at on in with
    first begin beginning step steps change advice tip tips thing things
""".split())


# A second list of ask words, kept separate because these are verbs a person asks the bot to do
# *for them* - "what should i check", "what should i ask", "what do i bring". They name nothing:
# the thing they are about is what the chat is already on, which is why "what should i check"
# after "im thinking of buying a used car" wants the answer it was just given. The object has to
# be said for the line to name something: "what should i check on a used car" is not this turn.
ASK_VERB = frozenset("""
    check checking ask asking bring bringing pick picking choose choosing spend spending
    watch watching expect expecting pack packing book booking
    first next step steps part bit
""".split())


# The verb families a line that names nothing can be written with. A follow-up that uses the same
# family as the question before it is asking for that answer again ("i want to cook something
# nice" then "what should i make"); a family the question never used is asking for something new
# ("i want to learn guitar" then "what should i buy" is about the guitar the person has yet to
# buy, not about the learning plan, so the buying entry keeps that turn).
DOINGS = (
    ("make", "makes", "made", "making", "cook", "cooks", "cooked", "cooking", "bake",
     "bakes", "baked", "baking", "prepare", "preparing", "serve", "serving"),
    ("buy", "buys", "buying", "bought", "get", "gets", "getting", "got", "pick", "picks",
     "picking", "choose", "chooses", "choosing", "chose", "shop", "shopping", "spend",
     "spending"),
    ("check", "checks", "checking", "look", "looking", "inspect", "test", "testing",
     "watch", "watching"),
    ("ask", "asks", "asking", "say", "says", "saying", "tell", "telling", "word", "words"),
    ("bring", "bringing", "take", "taking", "pack", "packing", "wear", "wearing"),
    ("try", "tries", "trying", "use", "using", "start", "starting", "begin", "beginning"),
)


# The words for asking what to do at all, with no work named: "what do i do", "and now", "what
# next". They are the shape the repeat module is for, whatever the question before them said.
WHOLE_OF_IT = frozenset("""
    do does doing done next then else now step steps first also more again
""".split())


def _doings(text):
    """The verb families a line asks its work with."""
    words = set(topics.words(text or ""))
    return {i for i, family in enumerate(DOINGS) if words & set(family)}


# Lead-ins: they carry nothing, so a line of them plus ask words still names nothing.
FILLER = frozenset("and so ok okay but well alright right then just maybe perhaps also too "
                   "good best".split())


# A time names no thing: "what should i do tonight" is the same ask as "what should i do", and the
# answer is the answer just given. It was not in the list, so the one word stood the repeat down
# and the person who asked what to do tonight about a child who will not sleep got a search hedge
# a turn after the bot had told them what to do. What the time is never a new subject: a line
# with a real one in it ("what should i cook tonight") still names something and never comes here.
TIME = frozenset("""tonight today tomorrow morning afternoon evening night later soon week
    weekdays weekend month""".split())


# A word for who does the thing is not a thing the line names: "what can i do about it myself"
# and "can i fix it myself" ask exactly what "what can i do about it" asks. The word stood the
# repeat down, so a chat that had been answered - a laptop whose fan had gone loud, with a detail
# said back in between - got "I'm not sure about that one, sorry" a turn after the answer.
SELF = frozenset("myself yourself himself herself itself oneself ourselves yourselves themselves".split())


# Lines that asked something rather than said something, so a bare question cannot be read as
# answering them.
# It has to ask for a way to do something, not for a decision: "should i buy it" and "why" are
# their own kinds of turn, and repeating an answer at them is not what they asked for.
QUESTION = re.compile(r"^\s*(?:and\s+|so\s+|ok\s+|okay\s+|but\s+|well\s+|right\s+)*"
                      r"(?:what|whats|how|where|now|next|then)\b", re.I)


# A lead that says the subject is dropped: "nvm, whats the tax deadline" after a question about
# flexible working was answered with the *second half* of that answer, because the new ask kept
# two words of it. What follows the lead is the whole of the turn, and it is read on its own.
RESET_LEAD = re.compile(
    r"^\s*(?:nvm(?:\s+(?:that|this|it))?|never\s*mind(?:\s+(?:that|this|it))?|nevermind|"
    r"forget\s+(?:it|that|this)|ignore\s+(?:it|that|this)|"
    r"scrap\s+(?:it|that|this)|anyway|anyways|new\s+question|different\s+question|"
    r"changing\s+the\s+subject|change\s+of\s+subject)\b[\s,.:;-]*", re.I)


def without_a_reset(text):
    """The line with a "forget that" lead taken off, so the new ask is read as the whole turn."""
    return RESET_LEAD.sub("", (text or "").strip(), count=1)


# "i don't know what to do" is the bare ask in the first person. It starts with "i", so the
# question lead never matched it and the person who said it - after being told what to do about a
# problem at work, or a parent in hospital - got a pool that answers nothing at all. It names no
# more than "what should i do" does.
LOSS_WORDS = frozenset("""dont know idea sure stuck really not even lost help someone
    thought anymore loss at myself""".split())


AT_A_LOSS = re.compile(
    r"^\s*(?:and\s+|so\s+|ok\s+|okay\s+|but\s+|well\s+|right\s+|honestly\s+)*"
    r"(?:i\s+)?(?:really\s+|just\s+)?(?:don'?t|dont|do not|didn'?t|didnt)\s+"
    r"(?:really\s+)?know\s+(?:what|how|where|who|which|when)\s+"
    r"(?:to\b|next\b|else\b|any\s?more\b|first\b)"
    r"|\b(?:(?:have|got)\s+)?no\s+idea\s+(?:what|how|where)\s+to\b"
    r"|\b(?:not\s+sure|stuck|at\s+a\s+loss)\s+(?:what|how|where)\s+to\b", re.I)


# The modules whose reply is an entry's answer: the knowledge base's, and the store's own when it
# hands an entry back (a repair that keeps the ask, a condition added to a choice).
ANSWER_MODULES = ("answers", "memory_store")


# How long an answer from the store has to be before it is the entry's words rather than a nod.
A_STORE_ANSWER = 120


# A hedge says nothing to repeat: it is what the bot says when it has no answer.
HEDGE = re.compile(r"\b(?:i'?m not sure|i don'?t know enough|that'?s beyond what i know|"
                   r"a quick search|searching for it|i'?d rather not guess|"
                   r"can'?t call that one|not mine to decide|nothing so far|"
                   r"search should sort you out|tell me what you find|"
                   r"what would be most useful|anything you'?d like a hand with)", re.I)


# How the answer comes back the second time: the same thing, minus the paragraph.
LEADS = (
    "You've got it: {said}",
    "That's the one: {said}",
    "It's what I said a moment ago: {said}",
    "Same answer: {said}",
    "From just now: {said}",
)


# One word after an answer is the ask to hear that answer again, and it is the commonest way of
# all to ask: "what?", "huh?", "sorry?", "come again?". The pool above answers an ask that took
# the answer in - "what do i do", "anything else" - with "You've got it:", which says the person
# agreed to something. On a bare ask nobody agreed to anything; they did not catch what was said:
#
#     how do i stop my pasta sticking together / what?
#       "You've got it: Stir it once as it goes in and once more a minute later ..."
#
# So a bare ask is handed the same answer under a lead that offers it again. The two words that
# are also ordinary apologies are the ask only with a question mark ("i got the job" / "sorry" is
# sympathy, not a request to repeat), and every word of the line has to be the ask.
BARE_ASK = re.compile(
    r"^(?:(?:sorry|er|erm|um|uh|oh|ah|ok|okay|and|so|but|wait|hmm|hey)\W+)*"
    r"(?P<word>huh|eh|come again|what was that|what did you say|say what|wha|hm|what|sorry|pardon)"
    r"(?:\s+(?:please|again|then|now|sorry))*\W*$", re.I)


BARE_ASK_NEEDS_A_QUESTION = frozenset("what sorry pardon".split())


SAY_AGAIN_LEADS = (
    "Again: {said}",
    "Sorry, again: {said}",
    "Said again: {said}",
)


# "what would help first", "where do i start", "whats the first thing to change": the person is
# not asking for the answer again, they are asking which part of it to do. Answering with the
# answer's opening sentence tells them the thing they already know, and answering with a search
# hedge disowns the answer given a turn ago - both are the wrong shape for this line.
# What a "that doesnt work" gets: the move past the advice, said in the answer's own words, with
# the report acknowledged rather than ignored.
TRIED_LEADS = (
    "Then it is worth going a step further: {step}",
    "If that is not shifting it, the next move is this: {step}",
    "Right - then the thing that is left is to go further: {step}",
)


# The sentence an answer closes on about who to go to when the advice alone is not enough. It is
# not the same paragraph read out again: it is the next move, and it is the answer's own words.
NEXT_STEP_EMERGENCY = re.compile(
    r"\b(?:999|911|112|a&e|accident and emergency|emergency (?:services|department|room)|"
    r"crisis line|116 123|988|samaritans)\b", re.I)


# The answer being reported on is itself the emergency route, so the step after it can only be
# that route said again. A lesser one - the "pharmacist or a doctor" that closes a pain answer -
# reads as permission to wait when it comes after "ring 999", and that is the one reply a
# frightened person must never get from this bot.
NEXT_STEP = re.compile(r"\b(?:gp|doctor|nurse|pharmacist|chemist|dentist|vet|optician|midwife|"
                       r"health visitor|111|999|911|helpline|a&e|hospital|council|"
                       r"citizens advice|plumber|electrician|engineer|gas safe|mechanic|"
                       r"locksmith|roofer|builder|technician|specialist)\b", re.I)


MOVE_ASK = re.compile(r"\b(?:help|helps|helped|helping|first|start|begin|next|step|steps|"
                      r"change|try|do|advice|tip)\b",
                      re.I)


# "Can i save it", "is it ruined", "can it be fixed": the thing is on the table from the answer
# just given, and what is asked is whether any of that answer still gets it back. It is the same
# ask as "where do i start" and wants the same thing - the answer's own first move, in its own
# words. Without it the line reached nothing: the answer was already on the screen, so the shape
# was handed a search hedge a turn after the bot had said what to do.
PUT_RIGHT = re.compile(
    r"\b(?:save|saved|salvage|salvageable|rescue|rescuable|revive|recover|redeem|fix|fixed|"
    r"repair|ruined|wasted|undo|undoable)\b", re.I)


# The words a put-right ask is made of, and the ones that name something of their own: "can i save
# it" names nothing ("it" is the thing on the table), "can i save money on my heating" names both
# a subject and a goal and is a question of its own.
# The way a put-right ask opens. It is not `QUESTION`, which reads the asks for a thing to do and
# does not carry "can", "is it" or "any chance" - the words these lines are actually made of.
PUT_RIGHT_ASK = re.compile(
    r"^\s*(?:and\s+|so\s+|ok\s+|okay\s+|but\s+|well\s+|right\s+)*"
    r"(?:can|could|can'?t|is|are|will|would|should|does|do|any|anything|is there|any chance)\b",
    re.I)


PUT_RIGHT_WORDS = frozenset("""
    save saved saving salvage salvageable rescue rescuable revive recover recoverable redeem
    fix fixed fixing repair repaired ruined waste wasted undo undoable gone dead done late still
    worth anyway any way ways chance point hope
""".split())


# "and now" is the bare ask for the next move in the same words as "what do i do": said after an
# answer about a sore knee it was handed the whole opening sentence again behind "Same answer:",
# which is the diagnosis they had just read, not the thing to do. It names no more than "what now"
# does, which is already read as an ask for the next step.
AND_NOW = re.compile(r"^\s*(?:and\s+|so\s+|ok\s+|okay\s+|right\s+)?now(?:\s+then)?[\s?.!]*$",
                     re.I)


# The lead for a put-right ask: the answer's move is still there to take, so the reply opens on
# that rather than on "start with this", which reads as a job they have not begun.
PUT_RIGHT_LEADS = (
    "Worth a go: {step}.",
    "Yes, there is something: {step}.",
    "Not too late: {step}.",
    "There is still this: {step}.",
)


# "what can i do with that" is not a move ask. It says "with that" - the thing the last
# answer was about - so it asks what the thing can be used for, and the answer is a dish or a
# use, not the first step of the instructions just given. The move rule heard the bare "do"
# and cut the dish answer to "Add the tinned tomatoes and a pinch of salt". A line that asks
# for a move on the answer says it plain ("what do i do first", "where do i start").
USE_WITH = re.compile(r"\b(?:what|anything)\s+(?:can|could|should|do|would)\s+"
                      r"(?:i|you|we)\s+do\s+with\s+(?:that|this|it|them|those)\b", re.I)


# "what else" asks for the next part of the answer in hand, not for the answer again. Said after a
# step, the whole answer read out is the paragraph they have already had twice, and the first part
# of it is the step they were just given, so the ask is answered with the part of the answer that
# comes next, and the ask after that with the part after that.
NEXT_ASK = re.compile(r"\b(?:what|anything)\s+else\b|\bwhat\s+next\b|\bnext\s+one\b|"
                      r"\bwhat\s+now\b|\bwhat\s+other\b|\band\s+then\b|\band\s+after\s+that\b|"
                      r"\bthen\s+what\b",
                      re.I)


NEXT_LEADS = (
    "Next up: {step}.",
    "The next one: {step}.",
    "Then this: {step}.",
    "After that: {step}.",
)


# The part that comes next can be the reason rather than the doing ("A sore knee is usually a
# strain or the kneecap tracking badly"), and "after that" in front of it promises a step it does
# not have: the second lead says where the line comes from and no more.
ALSO_LEADS = (
    "Also in that answer: {step}.",
    "And this: {step}.",
    "It also said this: {step}.",
    "There is this too: {step}.",
)


# A move is said in the answer's own words, as the thing to do rather than as a claim about the
# subject, so the lead has to be able to take a verb phrase.
MOVE_LEADS = (
    "Start with this: {step}.",
    "The thing to do first: {step}.",
    "I would start here: {step}.",
    "The first thing to do: {step}.",
)


# A lead and a step can say the same thing twice: "The first thing to do: Start with the room you
# walk through most" is one step said as first twice, and so is "Start with this: Start with
# run-walk". Which answers are affected is the answer's business, not the ask's - an entry whose
# step opens on its own "Start with" gets this fault on every start ask - so the rule is here: when
# the step says first itself, the lead may not say it too.
STEP_SAYS_FIRST = re.compile(r"^(?:start|begin|first)\b", re.I)


LEAD_SAYS_FIRST = re.compile(r"\b(?:start|begin|first)\b", re.I)


# What is left for those steps: they mark the one thing to do now without saying where in the
# answer it sits, because the step is already saying that. The answer's own words are what is
# being handed back, so the lead is the half that gives way.
NOW_LEADS = (
    "The one to do now: {step}.",
    "The one I would pick: {step}.",
    "Do this one: {step}.",
)


# Someone who says they do not know what to do is asking to be told one thing to do next, and the
# answer's own step is it. Said plainly, without the "same answer" framing, which reads like a
# complaint that they were not listening.
LOST_LEADS = (
    "Start with this: {step}.",
    "One thing to do first: {step}.",
    "Begin here: {step}.",
    "That's alright. Start with this: {step}.",
)


# The copula is scaffolding around the thing, never part of its name: "it was black mould" names
# the mould, and a confirmation that says "Was black mould, yes." is the scaffolding read as a word.
BE_FORM = frozenset("be been being is are was were am its it's thats that's".split())


# A pronoun points at the thing instead of naming it ("it was it", "that was low heat"), so it is
# scaffolding too - but only at the front, where it replaces the subject of the sentence.
POINTING_AT = frozenset("it that this".split())


# The words that say the person agrees and nothing more, so a line made of the answer plus these
# is the answer said back: "ok so low heat then". They come out of the confirmation.
AGREEING = frozenset("""
ok okay k right yes yeah yep yup got it good cool nice alright oh ah so then just too as well and
but actually honestly really well great perfect thanks cheers course fine sure indeed exactly
""".split())


# The words that agree on their own, as against the ones that only join a line together. "and",
# "but", "so", "then", "too", "as well" and "just" are how a person hangs a second thing onto the
# first, so a line that opens on one of them is asking about something else and is not a yes:
# "and for hard boiled", after the egg times, answers itself with "That's it: for hard boiled.",
# which the person cannot read. Only a word here makes a line an agreement.
AGREEMENT_TAIL = frozenset("""
then too well right ok okay yes yeah yep yup both is
""".split())


AGREES_ON_ITS_OWN = frozenset("""
ok okay k right yes yeah yep yup good cool nice alright great perfect thanks cheers course
fine sure indeed exactly
""".split())


# "got" and "it" are not a yes on their own: they are the commonest verb and pronoun in the
# language, and a line that carries one is usually news, not agreement - "someone else got the
# promotion", "they gave it to someone else", "i got a promotion". Both used to agree on their
# own, and the answer they were matched against came back with the verb taken out of the line:
# "someone else got the promotion" was answered "Someone else the promotion, that's the main
# thing." The set phrases are what agree, so those are matched as phrases.
AGREES_IN_A_PHRASE = re.compile(
    r"\b(?:got|get|gets|that's|thats|is|was|does|did)\s+(?:it|that|this|you)\b", re.I)


# "What should I change first" is not "what should I do first", and a lead-in that answers the
# other one reads as an answer to a question nobody asked: "The first thing I would change: Pasta
# with a sauce" answered "how do i learn to cook / what should i do first". So the lead is picked
# by the ask - one for the thing to do, one for the thing to change.
# "sort" and "try" are not change words: "what should we sort first" after a washing-machine
# answer is the thing to *deal with* first, and "Start by changing this: Run a hot 60C service
# wash" answers a question nobody asked, with a doubled verb (start by changing / run). Anything
# that means "deal with" belongs to the move leads; only change, fix, tackle and improve ask for a
# thing to change.
CHANGE_ASK = re.compile(r"\b(?:change|changed|fix|tackle|improve)\b", re.I)


# Every form has to read in front of an instruction, because the step a knowledge answer gives is
# usually one: "Change this first: Run a hot wash" keeps the ask, where "Start by changing this:
# Run a hot wash" is two verbs in a row that do not fit together.
CHANGE_LEADS = (
    "The first thing I would change: {step}.",
    "What I would change first: {step}.",
    "Change this first: {step}.",
)


# "what else can i do", "anything else i can try": the answer was on the screen and this line
# asks for one more thing out of it, so the reply is the next thing in that answer rather than
# another run at the whole paragraph or a search.
MORE_LEADS = (
    "Also from that answer: {step}.",
    "Another one from it: {step}.",
    "Worth trying as well: {step}.",
    "There is this one too: {step}.",
)


# The verbs an entry can open its instruction on that `verdict`'s list does not carry: entries
# about money say "Track two weeks of what leaves the account", the washing machine says "Run a
# hot service wash". Being off that list dropped the whole sentence and the move ask was handed
# the paragraph again ("where do i start" after "im trying to save money" -> "Same as before:").
# Kept here rather than added to `verdict`'s list so nothing outside the answer-handing-back path
# starts reading these words as an instruction.
MOVE_VERBS = (
    "track", "run", "note", "list", "lift", "simmer", "scrub", "wipe", "weigh", "sort",
    "split", "tip", "pour", "stir", "seal", "label", "spray", "blot", "trim", "tie",
    "cap", "dab", "pick", "chip", "sand", "scrape", "air", "dose", "feed", "renew", "fix",
    "swap out", "cut out", "turn off", "shut", "lock", "charge", "defrost", "descale", "dilute",
    "bring", "anchor", "aim", "count", "hold off", "leave out", "cut back", "write down",
    # The words a step opens on that are not in the composer's imperative list: an instruction is
    # read by its first word, so a verb that is missing here is a step the reader walks past.
    "undo", "unscrew", "screw", "pull", "push", "lift out", "prise", "wiggle", "dry", "brush",
    "vacuum", "mop", "dust", "sweep", "empty", "shake", "tape", "glue", "clamp", "snip",
    "preheat", "grease", "knead", "prove", "dust off", "wash out", "scrub out", "air out",
)


# Where an instruction's verb phrase ends and its detail starts. "Run a hot 60C or 90C service
# wash with a washing-machine cleaner or a cup of bicarbonate of soda" is one sentence and 19
# words, too long to hand over as the thing to do first, and the move is the part before the
# qualifier: "run a hot 60C or 90C service wash".
# An instruction longer than this is a sentence with its detail in it, and the detail comes off at
# the qualifier. Under it the sentence is handed over whole: "put the immersion and any room
# heaters on a timer for the hours you actually use" is 16 words, complete, and better than the
# fragment a cut at 12 words left behind.
STEP_WORDS = 20


# An instruction that carries its own method or its reason after a colon is one step, and it is
# a little longer than a bare one: "start with run-walk: one minute of easy jogging, two minutes
# of walking, repeated for 20 minutes, three times a week" is the whole of what to do.
STEP_WITH_ITS_METHOD = 30


# Past this many words the detail comes off at the qualifier.
CUT_WORDS = 12


# A cut that leaves less than this is not a step, it is the start of one.
SHORT_STEP = 6


# Verbs that are not finished without what comes after them: "put the immersion and any room
# heaters" is not an instruction, it is half of one, so a sentence opening on these is handed
# over whole. The list is short on purpose - a verb that reads as a step on its own is cut.
NEEDS_COMPLEMENT = frozenset("put place set leave keep wrap cover soak spray apply dip store "
                             "hang lay pour fill seal".split())


# Where a long instruction may end: at the reason for it, or the condition on it. The instruments
# and the places stay in ("a service wash **with a washing-machine cleaner**", "**then** undo the
# trap"), because they are what makes the instruction work rather than detail about it.
QUALIFIER = re.compile(r"\b(?:because|so that|which|if|unless|before|after|until|while|when|"
                       r"once|in case|as long as|rather than)\b", re.I)


# An instruction can open on a short phrase before its verb: "Half fill the kettle with equal parts
# water and white vinegar", "Each week add a minute to the jog". A reader that wants the verb first
# passed both over - so the kettle step that says what to put in the kettle was handed over as
# "Boil it and leave it half an hour" (an empty kettle), and the running plan answered "what next"
# with only two of its three steps. The phrase stays in the step: "each week" is what makes it a
# plan.
LEADING_PHRASE = frozenset("""half quarter each every once twice three two four five one times
    day days week weeks month months year years minute minutes hour hours night nights morning
    mornings evening evenings afternoon per in on at for after before during gently slowly
    carefully lightly quickly easily really also just only about""".split())


# An article is part of a leading phrase but never its first word: "once a day take this" opens on
# one, and "the wash itself is about two hours" does not ("the wash" is a subject and its noun is
# the verb).
AN_ARTICLE = frozenset("a an the".split())


# The verb is looked for in the first this many words of the piece, so a sentence that opens on a
# proper leading phrase ("in a hard-water area do it every couple of months") is read as a sentence
# about the answer's subject rather than as a step.
LEADING_PHRASE_MAX = 3


def _the_first_instruction_in_a_long_piece(head, verbs):
    """The first instruction out of a piece too long to hand over whole, else None.

    The answer stops telling the person to do something at the comma where it moves on to what
    will happen ("...and in about eight weeks you will run 20 minutes without stopping"), so the
    words above that comma are the step. Only when they read as an instruction of their own: a
    long piece is still passed over whole when what is above the first comma is not one.
    """
    piece = str(head or "").split(",")[0].strip(" ,;:.")
    words = piece.split()
    if len(words) < SHORT_STEP:
        return None
    if words[0].lower() in verbs or _a_verb_after_a_leading_phrase(piece, verbs):
        return piece
    return None


def _a_verb_after_a_leading_phrase(head, verbs):
    """True when the instruction's verb sits just after a phrase like "each week" or "half"."""
    tokens = [word.strip(" ,-").lower() for word in str(head or "").split()]
    for at in range(1, min(LEADING_PHRASE_MAX + 1, len(tokens))):
        if tokens[at] not in verbs:
            continue
        phrase = tokens[:at]
        if phrase[0] in AN_ARTICLE:
            continue
        if all(word in LEADING_PHRASE or word in AN_ARTICLE for word in phrase):
            return True
    return False


# Words that want a noun after them. A cut in front of one of these leaves the step hanging
# mid-phrase ("keep walking and carry"), so the cut lands after the phrase instead.
OPENERS = frozenset("with in into onto inside on at by from to for of under over through".split())


# Words a step cannot end on: a cut before one of these leaves the instruction without its
# ending ("clear the vents with a can of air and check what is"), so that cut is passed over and
# the next one taken, or the sentence is handed over whole.
DANGLING = frozenset("is are was were be been being am what that which who whom whose how why "
                     "the a an of to for and or but with in on at by from as it its this these "
                     "those his her their my your our there here than then so if even when while "
                     "because unless until plus yet".split())


# A piece of a sentence ends at a colon, a comma, a dash or a semicolon - anything that can put a
# second instruction beside the first. A comma inside a number is not a piece end: "earn more than
# 10,000 pounds a year" was cut at the comma, so the step handed back as the first thing to do
# stopped at "earn more than 10" and the figure was lost ("I would start here: ... earn more than
# 10."). A thousands separator is the one comma that never opens a second instruction.
PIECE_END = re.compile(r":\s|:|(?<!\d),(?!\d)| - |;| \u2014 ")


# A step never opens on the bot asking the person for something: "Tell me the figure you are saving
# towards" is the bot's own request, and handing it back as the thing to do told the person to
# answer their own question.
NOT_A_STEP = re.compile(r"^(?:tell|let|send|give|show|ask|name)\s+(?:me|us)\b", re.I)


# A menu is not the first thing to do: "Scones take 15 minutes, flapjacks 25, a Victoria sponge 40
# and banana bread an hour, so start with whichever time you have, and ripe bananas are the reason
# to make the last one" was handed over whole as the step, and the sentence that follows it is the
# one a person wants ("Weigh everything out before you start").
A_MENU = re.compile(r"\b(?:whichever|whatever|whenever|either|any of them)\b", re.I)


SENTENCE = re.compile(r"(?<=[.!?])\s+")


LEAD_SPLIT = re.compile(r"(?<=[.!?;])\s+")


# A quotation is one unit, whatever punctuation is inside it. An answer that shows the person what
# to write has a full stop and a question mark in it, and both sentence splitters above cut there:
# "Ask early, name the dates and say who covers: "Could I take 12-16 May off? I've arranged cover
# with Priya ..."" was handed back as "Shorter: Ask early, name the dates and say who covers:
# "Could I take 12-16 May off?" - a short answer that stops inside the quotation, and a second ask
# cut the other way, starting mid-quote with the closing mark left on it. A piece whose quotes do
# not pair up is the middle of a quotation, so it is never the short form on its own.
QUOTE_PAIRS = (("\"", "\""), ("\u201c", "\u201d"))


# The short form is a sentence or two, never a paragraph read out twice.
MOST = 240


LEAD_IN = 45


# The answer went unanswered for a turn or two at most.
LOOK_BACK = 3


# A request for less answered two or three times leaves hand-backs behind it, and those are
# skipped when looking for the answer: the window is wide enough to reach back past them to the
# answer they came from, so a fourth ask says there is nothing left instead of "nothing to cut".
LOOK_BACK_FOR_LESS = 6


# A line that opens on an auxiliary is asking something ("and is rice or pasta worse for me"),
# and a question about the thing in play has modules of its own: what was handed back to it was a
# sentence about packed lunches. The repeat's own QUESTION only knows the wh-words, because
# "what do i do" is the one it answers.
ASKS = re.compile(r"^\s*(?:and\s+|so\s+|ok(?:ay)?\s+|but\s+|well\s+|right\s+|also\s+)*"
                  r"(?:is|are|was|were|do|does|did|can|could|should|shall|would|will|"
                  r"have|has|had|am|may|might|must|any|anything|anyone)\b", re.I)


# A sentence where the bot asks the person something is not advice: "he cant stand coriander" was
# handed back "Tell me what is in the fridge and I will pick properly", which is the bot's own
# request said a second time.
ASKING_THEM = re.compile(r"\btell me\b|\blet me know\b|\bwhat(?:'s| is| have you)\b|"
                         r"\bsay which\b|\bwhat about\b", re.I)


# The bot has already said "that is the first step, work down the list" or "what I said above is
# the plan". Saying the answer again after that is the third time, and the chat has been pointed
# back once already. The composer's pointer says the rest of its answer follows from the step in
# its own words ("Ease off running first. The rest of what I said follows from that"), so the
# shapes it writes count here too, or the same paragraph comes back a third time.
REFER_BACK = re.compile(r"\b(?:the list i gave you|what i said (?:above|a moment ago)|"
                        r"down the list|first, then|i said (?:just )?now|same answer|"
                        r"you'?ve got it|that'?s the one|from just now|my answer above|"
                        r"the rest of what i said|the other things i said|first move|"
                        r"follows from (?:that|it)|comes after it)\b", re.I)


# A line that says "you" is asking about the bot itself ("what can you help with"), and the
# answer to that is never the thing the bot was just talking about.
ABOUT_THE_BOT = re.compile(r"\b(?:you|your|you'?re|u|ur)\b", re.I)


# "what should i say" asks for words to use, not for the steps again: the composer has a
# helper that puts the thing in words ("keep it to two sentences: what happened, then what you
# want"), and a repeat of the pay-rise advice takes the turn from it.
WORDS_WANTED = re.compile(r"\b(?:say|tell|write|phrase|word(?:ed|s)?|put\s+it|email|text|message|"
                          r"reply|respond|explain|ask\s+for|apologise)\b", re.I)


# A turn that added a detail to what we were already on, and got its own words back, has not
# moved the chat on. "we want to grow some veg this year" / "we only have a small patio" is the
# same thing twice, and the echo ("Got it - you only have a small patio") is the bot holding the
# detail, not answering it: "what should we start with" after that is still the first question.
# These are the words an echo puts round a line, so what is left of the two is what the person
# actually said.
ECHO_FRAME = frozenset("""got not right ok okay yes noted good to know remember that thats
    ill i you your youre its it and the a an of in on at for with so then anything like hand
    question theres there here me my""".split())


STALL = re.compile(r"\b(?:say more if it helps|go on|keep going|tell me the rest|"
                   r"i'?m with you|i'?m listening|i'?m here if you want|anything you'?d like a "
                   r"hand with|i'?ll remember that|noted|good to know|i'?ve got that|"
                   r"i'?ll keep that in mind)\b", re.I)


def only_said_it_back(line, said):
    """Whether the reply only says the person's own line back, so nothing has been answered.

    The words of the line that name something, less the ones a frame is built from, are nearly
    all in the reply: that is the line said back with a frame around it, which files a statement
    and answers nobody. It is here rather than in `_an_echo` because two readers need it and they
    must agree: the repeat guard below reads it a turn at a time, and the composer's want reader
    (`bot/compose/remark.py`, `a_want_said_back`) uses it to tell a receipt from an answer -
    "Got it — your son wants a tattoo." and "Your son is 16 and wants a motorbike. That explains
    it — no wonder it sits on you." are the same shape, and the shape is what decides it, not the
    frame either one happens to use.
    """
    said = str(said or "").strip()
    if not said:
        return False
    low = said.lower()
    spoken = [w for w in topics.words(str(line or ""))
              if w not in topics.STOPWORDS and w not in ECHO_FRAME and len(w) > 1]
    if not spoken:
        return False
    kept = sum(1 for w in spoken if w in low)
    return len(spoken) >= 2 and kept >= max(2, (len(spoken) * 3) // 4)


def _an_echo(turn):
    """The bot only said the person's own line back, or stalled, so nothing has been answered."""
    said = str(turn.get("bot") or "").strip()
    if only_said_it_back(turn.get("user") or "", said):
        return True
    return bool(said) and bool(STALL.search(said.lower()))


def _names_no_topic(turn):
    """The line was a detail, not a subject of its own: "we only have a small patio" is about the
    garden we are already on, while "my mother in law is coming on sunday" is a new thing."""
    line = str(turn.get("user") or "")
    if not line.strip():
        return False
    try:
        return not (understand(line, None).get("topics") or [])
    except Exception:
        return False


def _only_echoes_between(memory, back):
    """Whether every turn after an answer `back` turns ago was a detail said back, and no more.

    Both halves matter: the bot has to have only echoed the line or stalled, and the line has to
    have named no subject of its own. "we only have a small patio" after the veg answer is the
    same question again, but "my mother in law is coming on sunday" is a new thing, and the roast
    timing is not the answer to it.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    between = turns[len(turns) - back + 1:] if back > 1 else []
    return bool(between) and all(_an_echo(turn) and _names_no_topic(turn) for turn in between)


# "ok then", "alright then", "right then" is a nod that closes the turn, not a bare ask. The
# `then` made it read as "then what?", so the whole answer came back under a lead - "You've got
# it: Take paracetamol or ibuprofen at the dose on the pack and ring a dentist the same day" - to
# somebody who had just said ok. The other thirteen acks ("ok", "right", "cheers", "got it") all
# get a short close, and `then` is the only thing that separated this one from them.
JUST_A_NOD = re.compile(
    r"^\s*(?:ok|okay|alright|all right|right|fine|good|great|cool|cheers|ta|thanks|nice)"
    r"(?:\s+(?:then|thanks|cheers|mate|ok|okay|so))*[\s.,!?]*$", re.I)


# The shape of a bare ask for a way to help that has no question word to be read by: "is there
# anything i can do", "any way of making it easier", "anything that helps", "something that would
# help". The understanding engine reads these (`help_ask`, with the fences that keep a line naming
# a thing of its own out - "is there anything i can do about the mole on my back" is not one), and
# the gate below keeps that reading to the lines that could be one. "something" is the same ask
# said with the other word, and the gate was the only thing that knew only one of them: the engine
# had read "something that would help" as a help ask all along, and the gate turned it away, so a
# person who asked it after an answer got the answers module reading a search for it instead.
HELP_SHAPE = re.compile(
    r"\b(?:any\s?way|anything|something\s+(?:that|which|to)|is there|are there)\b", re.I)


# The same ask with the question in front. The understanding engine's reader knows one word order,
# "anything i can do"; "can i do anything about it" puts the question first and names nothing, and
# read as a statement it got the composer's shrug ("That's most of what I know on it") straight
# after a full answer about the rent - while the same line written "is there anything i can do" was
# handed the answer's own first step. Only the word order is missing, so it is read here, with the
# engine's own fence kept: a thing named after the ask ("...about the mole on my back") is not a
# bare ask for a way in.
HELP_ASK_QUESTION_FIRST = re.compile(
    r"\b(?:can|could|should|shall)\s+(?:i|we)\s+do\s+(?:anything|something)\b"
    r"|\bis\s+there\s+(?:anything|something)\s+(?:i|we)\s+"
    r"(?:can|could|should|might|would)\s+do\b", re.I)


NAMED_AFTER_IT = re.compile(r"\b(?:my|our|his|her|their|your|the|a|an)\s+[a-z]")


# "what do you think i should do first" asks for the move in the answer in hand and names nothing
# of its own; "think" is what the person wants done with the answer, not a subject. Everything
# else outside the ask's own frame is a thing named.
NOT_A_THING = frozenset((
    "think", "reckon", "want", "suppose", "guess", "even", "actually", "back", "again", "one",
    "ones", "thing", "things", "stuff", "lot", "bit", "kind", "sort", "way", "ways", "time",
    "times", "people", "anyone", "someone", "everything", "anything", "something", "nothing"))


def _names_a_thing_of_its_own(text):
    """The content words of the line that name something, in the ask's own frame left out.

    This is the reading behind `names_nothing`, kept separate because the start asks need the
    same test without the fences around it: "my laptop keeps dropping the wifi in the back room,
    what should i try first" names a laptop, a wifi and a back room, so it is a question about
    those and not a question about the answer just given.
    """
    lost = bool(AT_A_LOSS.search(text or ""))
    said = ASK | ASK_VERB | TIME | FILLER | NOT_A_THING
    if lost:
        said = said | LOSS_WORDS
    return [word for word in topics.words(text or "")
            if len(word) > 2 and word not in said and word not in SELF
            and not word.isdigit() and word not in topics.STOPWORDS]


# A step verb acts on the answer just given rather than naming a subject of its own: "what should
# i delete first" is about the answer on the screen, and the answer's own move is the reply.
# A move a sentence only makes under a condition is not the first thing to do now: "If you get
# them most days, keep a short diary of sleep" is what to do about a pattern, not about the
# headache the person has this afternoon.
CONDITION_CLAUSE = re.compile(r"^\s*(?:if|unless|when|whenever|once|in case|should|as long as)\b",
                              re.I)


# A referral is not a move either: "ask a GP: they can check your bloods" ends a health answer and
# was handed back as the first thing to do for the trouble the person named that turn.
NOT_A_MOVE = re.compile(
    r"^(?:ask|ring|call|see|phone|speak to|talk to|book|visit|check)\b[^.!?]{0,30}\b"
    r"(?:gp|doctor|doctors|dentist|nurse|pharmacist|chemist|optician|vets?|hospital|ae|"
    r"a&e|plumber|electrician|engineer|specialist)\b", re.I)


STEP_VERBS = frozenset("delete remove clear keep pick choose check replace".split())


# The words that make a line ask which of several steps comes before the others.
ORDER = re.compile(r"\b(?:first|next|then|before|after that)\b", re.I)


def asks_to_put_it_right(text):
    """True when the line asks whether the thing on the table can still be put right.

    "can i save it", "is it ruined", "can it be fixed": the thing is the one the answer just
    gave, so nothing about the line is new - it is a question about that answer, and the answer's
    own first move is what it wants. A line that names a subject or a goal of its own ("can i save
    money on my heating", "can i fix my bike") is a question of its own and keeps it.
    """
    line = str(text or "").strip()
    if not PUT_RIGHT.search(line) or not PUT_RIGHT_ASK.match(line):
        return False
    if topics.pairing(line) or ABOUT_THE_BOT.search(line):
        return False
    words = [w for w in topics.words(line) if w not in ASK and w not in FILLER
             and not w.isdigit() and w not in SELF and w not in PUT_RIGHT_WORDS
             and w not in topics.STOPWORDS]
    return not words


def a_step_of_the_same_answer(text):
    """True when the line asks which of the answer's own steps to do first.

    "what should i delete first" after the Mac storage answer carries one content word, and that
    word ("delete") acts on the answer rather than naming a subject of its own, so the answer on
    the screen still answers it. A line that names a thing ("how do i delete a file") is a
    question of its own and keeps it.
    """
    if not ORDER.search(text or "") or not MOVE_ASK.search(text or ""):
        return False
    if topics.pairing(text or "") or ABOUT_THE_BOT.search(text or ""):
        return False
    words = [w for w in topics.words(text) if w not in ASK and w not in FILLER
             and not w.isdigit() and w not in topics.STOPWORDS]
    return bool(words) and set(words) <= STEP_VERBS


def _recent_answers(memory):
    """The bot's own answers in the recent past, newest first, each with the line it answered and
    how many turns ago it was (1 is the turn just before this one)."""
    out = []
    seen_a_card = False
    for back, turn in enumerate(reversed((memory.get("turns") or [])[-LOOK_BACK:]), 1):
        if not isinstance(turn, dict):
            break
        # Only an answer is worth saying again. A stock line, an echo of their own words, a
        # refusal or an emergency reply is not: "what would you do" after "Thanks for telling
        # me - I'm here if you want to dig into any of that" must not be handed that line back.
        if turn.get("module") not in ANSWER_MODULES:
            continue
        said = str(turn.get("bot") or "").strip()
        if not said or HEDGE.search(said) or len(said) < 50:
            continue
        # The store answers some lines with an entry's own words - a swap that keeps the ask, a
        # condition added to a choice - and those are answers to hand back. Its own short lines
        # ("Got it - the front room.") are not, so the length is what tells the two apart: without
        # this, the paragraph after a corrected line was invisible and a follow-up was handed the
        # answer from two turns back instead of the one just given.
        if len(said) < A_STORE_ANSWER and turn.get("module") != "answers":
            continue
        # The bot asking a question is not an answer to hand back: "what would you do?" after
        # "is there one thing that would help?" wants an answer, not the question again.
        if said.rstrip().endswith("?") or QUESTION.match(said):
            continue
        # A trip they have changed moves the answer with it: the weather, the cost and what to
        # see are facts about a place, so an answer about Rome is not the answer to a question
        # about Cornwall ("im off to cornwall next week" / "what should i do there" was handed
        # the Rome weather sentence).
        if topics.about_a_place_they_left_behind(said, memory):
            continue
        out.append((back, str(turn.get("user") or ""), said))
    return out


def _the_answer_about_what_we_are_on(memory, recent):
    """The recent answers that can be handed back, newest first, with the topic in hand first.

    The newest answer is the answer to a follow-up that names nothing of its own, which is right
    while the chat is still on it. Going back to an earlier topic is the case where it is not:
    the conversation is on the boiler again, and the newest answer is about the school places the
    line between them brought up. The store has already made the returned topic current, so an
    answer about some *other* subject is not the answer in hand, and the answer to the topic we
    are on is the one to draw on:

        my boiler keeps losing pressure
        my daughter is 6 and starts school in september
        anyway back to the boiler      -> "Back to the boiler, then. What did you want to know
                                          about it?"
        what should i do first         -> "The thing to do first: Apply through your council by
                                          15 January ..."   (the school places)

    Only answers about the topic in hand are offered when the newest one is about something else;
    when the newest answer *is* about the topic in hand the list is left exactly as it was, so
    every other chat reads as before. The order of the answers about the topic in hand is kept,
    so the newest of those is still tried first, and the guards in `answer_for` still decide
    whether it may be handed back at all.
    """
    here = topics.current(memory)
    # The topic's own words carry what the lines since have added to it ("should i switch" adds
    # `switch` to the broadband), so they are read with the keywords of the line that opened it.
    # Without them the answer to a follow-up that used the topic's own word was not recognised as
    # being about it, and an older answer took its place: "my broadband is 45 a month is that a
    # lot" / "should i switch" (the cancel steps) / "how do i cancel it" was handed the verdict on
    # the £45 instead of the steps to cancel.
    mine = {word for word in topics.keywords(str((here or {}).get("text") or ""))}
    mine |= {str(word).lower() for word in ((here or {}).get("words") or ())}
    if not recent or not mine:
        return recent
    # The newest answer is the answer in hand when it is about the topic, and an answer is what
    # the bot said, not only what the person said: "my broadband is 45 a month is that a lot" /
    # "should i switch" gets the cancel steps, and the "how do i cancel it" after it belongs to
    # that answer even though the line between them never said "broadband". Without the bot's own
    # words, the answer about the person's *line* two turns back wins over the answer about the
    # thing they are asking about now.
    if mine & set(topics.keywords(recent[0][1])) or mine & set(topics.keywords(recent[0][2])):
        return recent
    about_it = [item for item in recent if mine & set(topics.keywords(item[1]))]
    return about_it or recent


def _short(said):
    """The answer the way a friend repeats it: its first sentence, or two when the first is only
    a lead-in, and never more than MOST characters."""
    parts = [p.strip() for p in SENTENCE.split(said.strip()) if p.strip()]
    if not parts:
        return ""
    short = parts[0]
    if len(short) < LEAD_IN and len(parts) > 1:
        short = short + " " + parts[1]
    if len(short) > MOST:
        short = short[:MOST].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return short


# A knowledge answer sometimes says which of its own pieces is the move: "Half an hour earlier to
# bed, and the same wake-up time every day, is the first thing to change". The sentence names the
# move itself, so the part in front of the "is" is the thing to hand back, in their own words.
FIRST_THING = re.compile(
    r"^(?P<move>.{4,120}?)\s+is\s+(?:the|your|my)\s+(?:first thing|thing to do first|"
    r"best first (?:step|move)|first (?:step|move)|best (?:step|move)|place to start|"
    r"one thing|fix|change|main thing|thing that helps|bit that helps|part that matters)", re.I)


# The prepositions that follow a noun and never an instruction: "water at the front" is about
# water, though `water` is a verb in the list, and handing that back says the diagnosis is the
# step to take. A heading that weighs one way of doing it against another is not the move itself: the thing it
# is weighing in favour of is what follows the colon ("Test yourself instead of rereading: cover
# the page, say or write what you remember").
_WEIGHS_ONE_AGAINST = re.compile(r"\s(?:rather than|instead of)\s", re.I)


# The prepositions that follow a noun and never an instruction: "water at the front" is about
# water, though `water` is a verb in the list, and handing that back says the diagnosis is the
# step to take. "Stop the cycle", "check the hose", "turn it off" are the shape of an instruction.
_AFTER_A_NOUN = frozenset("at in on from of for to with by near under behind over into about".split())


# A sentence that opens on a subject pronoun and runs on is saying how something is, and no
# clause of it is an instruction. The tell is the subject in front of the verb: an instruction has
# none, so a verb-shaped word that has one is the sentence's subject ("water goes in at the mouth"
# is a statement, and "water" is what you do to a plant).
_SUBJECT_OPEN = re.compile(r"^(?:they|it|it's|its|he|he's|she|she's|this|that|that's|these|those"
                           r"|there|there's|we|we're)\b", re.I)


# What a heading in front of a colon may be. Longer than this is a sentence, not a heading.
_EXPLANATION_WORDS = 5


def _explains(sentence):
    """True for a sentence that says how something is, so holds no step of its own."""
    text = str(sentence or "").strip()
    if not _SUBJECT_OPEN.match(text):
        return False
    head = re.split(r":|,|;| - | \u2014 ", text, 1)[0]
    return len(head.split()) > _EXPLANATION_WORDS


def _a_step_comes_after(part):
    """Whether the sentence that explains a fault ends on the step ("..., so clear the vents").

    `_explains` caps a description at its first clause and treats the rest of the sentence as more
    description. A sentence that closes on "so <verb>" is different: everything after the "so" is
    what to do, and skipping it lost the step of answers like "It is cooling itself because it is
    hot, so clear the vents with a can of air".
    """
    text = str(part or "")
    for match in _SO_THE_STEP_FOLLOWS.finditer(text):
        if _opens_an_instruction(text[match.end():]):
            return True
    return False


def _opens_an_instruction(text):
    """Whether a piece of an answer opens on a verb an instruction can open on."""
    from ..compose.verdict import IMPERATIVES

    words = text.strip(" ,.:;").split()
    # "Blot, don't rub" is the same instruction as "Blot": the comma belongs to the sentence, not
    # to the word.
    return bool(words) and words[0].lower().strip(" ,.;:") in IMPERATIVES


# A step cut at its own ", then" must not end on one of these: "ask once, plainly, and" is half a
# sentence, and the half it lost was the instruction.
_HANGS = frozenset("and or but then with to of the a an in on at for is are that this".split())


# What follows the comma in "Blot, don't rub": the answer going on with the same instruction by
# saying what not to do. A negation is an instruction even though it opens on a word that is not
# a verb in the list.
_NEGATES = re.compile(r"^(?:do not|don't|dont|never|avoid)\b", re.I)


# The step often comes as the conclusion of the sentence that explains the fault: "It is cooling
# itself because it is hot, so clear the vents with a can of air". The joining word holds the
# sentence together and is not part of the step, but it is where the step starts, so a reader that
# only opens on a verb walked past it and handed the cause back instead of what to do.
_SO_COMES_THE_STEP = re.compile(r"^(?:and\s+|but\s+)?so\b[,\s]+", re.I)


# The same word in the middle of the sentence, after the part that explains it.
_SO_THE_STEP_FOLLOWS = re.compile(r"[,;]\s*(?:and\s+)?so\b[,\s]+", re.I)


# "so do holidays" is not an instruction: it is agreement with what the sentence just said
# ("Days and months take a capital - so do holidays"). `do` is a verb an instruction can open on
# and the words after it are the subject of the agreement, so the two are told apart by what comes
# after the verb: an instruction names what to do ("do that first", "do the washing", "do both").
_SO_DOES_NOT_ASK_SOMETHING_OF_THEM = re.compile(
    r"^do(?:es)?\b(?!\s+(?:it|that|this|these|those|them|the|a|an|your|my|his|her|their|our|both"
    r"|one|all|more|less|as|so)\b)", re.I)


def _opening_move(part):
    """The instruction a sentence opens with, in the answer's own words, or None.

    Only the start of the sentence counts: an instruction opens on its verb, and a word further
    in is the thing it is about: "Stop the cycle, unplug it and turn the water off" opens on the
    instruction, and "Water at the front is usually the door seal" is about water, though `water`
    is also a verb in the list. A sentence that opens on a fact and then says what to do ("A
    dripping tap is nearly always a worn washer: turn the water off at the valve") hands back what
    follows its colon, and the whole of it, because the steps are the answer.

    A sentence that leads with the plan ("Start with run-walk: one minute of easy jogging") hands
    back what follows its colon too: the lead is the verb, and reading the lead as the move would
    hand back "start with run-walk" and say start twice.
    """
    from ..compose.verdict import IMPERATIVES  # the verbs an instruction can open on

    # A step is often wrapped in one long sentence: "Pack what you use least first - books, spare
    # bedding, the cupboard under the stairs - and keep a 'first night' box out of the van: kettle,
    # mugs, chargers, loo roll, bedding and a change of clothes" is 37 words and it is one step.
    # Handed back whole it is a paragraph said aloud, and the asides are the reason it took two
    # goes to say: the piece before the first dash is the step, and it is read first when it is
    # itself a short sentence. A dash inside a longer instruction ("Stop the cycle, unplug it and
    # turn the water off - the fuse stays live") costs nothing, because the lead is the step.
    lead = re.split(r"\s+[-\u2014]\s+", str(part).strip())[0]
    if lead.strip() and lead.strip() != str(part).strip() and len(lead.split()) <= 12:
        found = _opening_move(lead)
        if found:
            return found

    leads_with_the_plan = bool(re.match(r"(?:start|begin) with\b", part.strip(), re.I))
    pieces = [part] + part.split(":")
    # A sentence that opens on a subject pronoun and runs on is explaining something, so what
    # follows its colon is the rest of the explanation and not a step: "They take oxygen out of
    # the water instead of the air: water goes in at the mouth, passes over the gills" is how a
    # fish breathes, and its tail read on its own is the instruction "Water goes in at the
    # mouth" - what a person asking what to do about a goldfish lying on the bottom of the tank
    # was told to do. A short piece in front of the colon is still a heading ("That's the one:
    # split your time in three"), so the cap keeps those.
    explaining = _explains(part)
    for index, piece in enumerate(pieces):
        if index and explaining:
            continue
        head = _SO_COMES_THE_STEP.sub("", piece.strip(" ,.:;"))
        if topics.RED_FLAG.match(head):
            continue  # a warning is not a move, and handing it back alone scares the person
        words = head.split()
        if not 3 <= len(words) <= 40:
            continue
        # "Blot, don't rub, then dab a little hand sanitiser" is one instruction whose verb the
        # comma sticks to, and reading the word with its comma in it missed the verb and walked
        # on to the next sentence, so "what should i do first" was answered with the second thing
        # in the answer ("rinse with cold water and wash") rather than the first. The comma only
        # comes off when what follows it is another instruction, so a list of nouns that happens
        # to open on a verb word keeps its guard: "Sleep, water and an antihistamine" is one
        # thing among others, not the step.
        first = words[0].lower().strip(" ,.;:")
        if first != words[0].lower() and not _opens_an_instruction(" ".join(words[1:])) \
                and not _NEGATES.match(" ".join(words[1:])):
            # A comma comes off the verb only when the answer goes on with another instruction
            # ("Blot, don't rub"): "water, squash and milk all count" and "dry, gritty eyes are
            # usually the tear film" also open on a word the verb list holds, and reading those
            # as the step handed back a list and a description.
            continue
        if first not in IMPERATIVES:
            # The verb of a "start with X: <steps>" sentence is its lead, so the steps after its
            # colon are instructions even though they open on a measure ("one minute of easy
            # jogging") rather than on a verb.
            if not (leads_with_the_plan and index > 1):
                continue
        elif words[1].lower().strip(" ,.;:") in _AFTER_A_NOUN:
            continue  # "water at the front": a noun the imperative list happens to hold
        elif re.match(r"(?:start|begin) with\b", head, re.I) and ":" in part:
            continue  # the lead itself; what it leads to is the next piece
        elif (_WEIGHS_ONE_AGAINST.search(head) and index + 1 < len(pieces)
              and _opens_an_instruction(pieces[index + 1])):
            # "Test yourself instead of rereading: cover the page" weighs one way against
            # another, so it is a heading and not the move; what follows the colon is. The
            # contrast has to be the whole of the heading for that to hold: in "keep walking ...
            # rather than taking to your bed, and take paracetamol" the contrast is inside the
            # instruction, and the instruction is what is handed back.
            continue
        # "book a GP appointment rather than keep taking painkillers" is one instruction with a
        # contrast on the end; the step is what is in front of the "rather than", and handing the
        # contrast back reads as two steps run together.
        head = re.split(r"\s+rather than\b", head)[0].strip(" ,;:-")
        if len(head.split()) < 2 or topics.RED_FLAG.match(head):
            continue
        # The sentence may carry the step and then the rest of the routine after a ", then " or a
        # semicolon ("Blot, don't rub, then dab a little hand sanitiser into the mark with a cotton
        # bud and blot again"). Sentence splitting cannot see that boundary, so the first step is
        # handed back on its own and the rest of the routine is left where it is - a friend says
        # the first thing once.
        if ":" not in head and ", then " in head:
            # One step and then the next: "Blot, don't rub, then dab a little hand sanitiser into
            # the mark with a cotton bud and blot again" hands back two moves in one line, and a
            # person asked for the first. Only a short lead is cut, and only before ", then": a
            # colon holds the instruction it introduces ("check the obvious one first: signal,
            # then mobile data off for ten seconds" lost the part that fixes it when it was cut
            # there), and a semicolon joins two statements as often as two steps ("water doesn't
            # help; a little sugar and lemon balances the chilli" is not a step when its first
            # half is read alone).
            shorter = head.split(", then ")[0].strip(" ,;:-")
            if (3 <= len(shorter.split()) <= 8 and _opens_an_instruction(shorter)
                    and shorter.split()[-1].lower() not in _HANGS):
                head = shorter
        return head[0].lower() + head[1:]
    return None
