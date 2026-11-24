"""Part 1 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from . import lexicon



NEGATIONS = lexicon.NEGATIONS


# "can't you come earlier" and "isn't it lovely" deny nothing: the negation sits in front of the
# subject, so the clause still asks. After one of these it is a tag of the question.
PRONOUNS = frozenset("i you we they he she it there that this these those one".split())


# "no", "nobody", "nothing" are what the clause is about, not a denial of the verb, so
# "is nothing working today" still asks.
SUBJECT_NEGATIONS = frozenset("no nobody none nothing neither nor".split())


# "good day", "greetings" and "salutations" are hellos people write in full and the reading
# never saw: each was answered as a statement about something ("Ha, fair enough. I'm here if
# you want a hand with anything"). They are the same hello as "hi" and nothing else, so a line
# made of one of them and a friendly tail is the hello, and a line that goes on to say something
# stays what it says ("greetings, my boiler is leaking" is the boiler).
GREETINGS = ("hi", "hello", "hey", "hiya", "morning", "good morning", "good afternoon",
             "good evening", "evening", "yo", "howdy", "good day", "greetings",
             "salutations")


FAREWELLS = ("bye", "goodbye", "see you", "see ya", "later", "night", "good night",
             "talk later", "take care", "ttyl", "gtg", "cya", "best wishes", "best regards",
             "kind regards", "warm regards",
             # The short ways out people type, and the ones that say "you" in the middle - "see
             # you later" and "talk to you later" are the same goodbye as "later", and the reading
             # that looks for "you" took them for a question about the bot. "ciao" is left out on
             # purpose: it opens a chat as often as it ends one, so it stays with the greeting.
             "ttfn", "cheerio", "laters", "adios", "night night", "nighty night",
             "ta ta", "see you later", "see you soon", "talk to you later",
             "speak later", "speak to you later", "catch you later", "bye for now")


THANKS = ("thanks", "thank you", "thx", "cheers", "ty", "ta", "much appreciated",
          "appreciate", "appreciated", "appreciate it")


QUESTION_WORDS = frozenset("what why how when where who which whose".split())


# A thanks that carries an ask is shaped like one in two ways: a question word, or an ask frame
# of its own. The frame is what people write when they thank you and then ask for advice on
# something: "thanks, any tips for a cold", "thanks, tips for a stain", "thanks, looking for a
# recipe for two". "advice on" only counts when the advice has not been given yet, so "thanks for
# the advice on my back" stays the thank you it is.
THANKS_ASK_NOUNS = frozenset("advice tip tips idea ideas suggestion suggestions".split())


THANKS_ASK_PREPS = frozenset("for on about with".split())


THANKS_ASK_WORDS = frozenset("any need needs looking".split())


GIVEN_ADVICE = frozenset("the your my our his her its their this that no".split())


QUESTION_STARTS = {"what", "why", "how", "when", "where", "who", "which", "whose", "can",
                   "could", "should", "would", "is", "are", "do", "does", "did", "will",
                   "have", "has", "am", "was", "were", "may", "might", "shall"}


# A question that opens with one of these wants a yes or a no: "can i take ibuprofen".
YESNO_STARTS = QUESTION_STARTS - {"what", "why", "how", "when", "where", "who", "which",
                                  "whose"}


# `yh`, `yhh` and `ye` are how a lot of people type "yes", and without them in this list a bare
# "yh" read as an ordinary statement and got "I'm listening - say more if it helps." - the shrug,
# not the answer a yes gets. `ye` is the oldest spelling of "you" and only survives in set
# phrases ("ye olde"), which is a trade worth making: "ye i did" and "ye it was" are answers,
# and a line that needs `ye` as "you" ("ye know what i mean") still has its other words.
AFFIRM = frozenset("yes yeah yep yup yh yhh yhhh ye sure ok okay definitely absolutely correct "
                   "right probably "
                   "maybe perhaps likely "
                   "true exactly indeed agreed fine cool great nice good perfect sounds "
                   "works deal done sweet brilliant".split())


DENY = frozenset("no nope nah never not nothing none neither".split())


ACK = frozenset("ok okay cool nice great good fine sure right got understand understood "
                "thanks aha ah oh wow really hmm hm mmm alright k gotcha you me same maybe "
                "perhaps probably likely haha hehe lol fair true".split())


LAUGH = frozenset(lexicon.LAUGHTER)


# Words of politeness that do not change what a short reply means: "yes please" is a yes.
POLITE = frozenset("please pls plz ta mate".split())


# Asking for a recommendation, an opinion, or a decision.
RECOMMEND = frozenset("recommend suggest recommendation suggestion advice idea ideas "
                      "options option pick choose best better worth".split())


# "tip" is three different things: advice asked for ("any tips for a roast"), money left for
# someone ("a 10% tip"), and what a person does ("he tips well", "tip the delivery driver").
# Only the advice reading belongs in RECOMMEND, and it needs a frame around it:
#   plural "tips"/"hints"/"pointers"  - nearly always advice, unless a subject in front makes
#                                       it a verb;
#   singular "tip"/"hint"/"pointer"   - nearly always a thing, unless something asks for some
#                                       ("any tip on painting a door").
TIPS = re.compile(r"\b(tips|hints|pointers|tip|hint|pointer)\b")


TIPS_WANTED = re.compile(r"\b(?:any|some|a few|few|got|need|needs|wanted|looking for|share|"
                         r"send|give(?: me)?)\s+(?:\w+\s+){0,2}$")


# "tips for a roast", "tips on painting", "tips for the garden" say what the advice is about.
TIPS_ABOUT = re.compile(r"\s+(?:for|on|about|when|to)\s+\w")


# a subject in front makes "tips" a verb, and an amount in front makes a tip money
TIPS_SUBJECT = re.compile(r"\b(?:i|you|we|they|he|she|it|who|that|this|people|everyone|"
                          r"nobody|someone)\s*$")


TIPS_AMOUNT = re.compile(r"(?:\d|%|\b(?:a|the)\s+\w+\s*%)\s*$")


# Asking for help without a question word in front of it: "anything i can do about it", "any way
# of making it easier", "anything that helps", "is there any way to save it". The line is a
# request for steps, but nothing in it opens like a question, so it used to read as a statement
# with nothing asked and got the stock nod. What it asks for is the same thing "what can i do"
# asks for, so it says "steps" too. A negation in front of the ask turns it back into a
# statement about there being nothing to do ("there isnt anything i can do", "i dont see any way
# to fix it"), which is a fact to answer, not a request.
HELP_ASK = re.compile(
    r"\b(?:anything|something)\s+(?:else\s+)?(?:i|we|you)\s+(?:can|could|should|might|would)\s+"
    r"(?:do|try|use|take|add|change)\b"
    r"|\b(?:anything|something)\s+(?:else\s+)?(?:that|which)\s+(?:helps|would help|might help|"
    r"will help|works)\s*[?.!]*\s*$"
    r"|\bany\s+(?:way|ways)\s+(?:of|to|round)\b"
    r"|\bis there any\s+(?:way|ways|thing)\s+(?:of|to|i|we|you|else)\b")


# What follows the ask decides it: "anything i can do is never enough" and "any way to get there is
# fine" are statements about the ask, not asks. The tail is searched, not matched at its start:
# after "any way to" comes a verb phrase ("to get there is fine"), so a check anchored at the
# match would only ever see the verb and let every statement built on the shape through.
HELP_ASK_SUBJECT = re.compile(
    r"\b(?:is|was|are|were|seems|seemed|feels|felt|sounds|sounded|helps|helped|works|worked|"
    r"suits|suited|fits|fitted|does|did|its|thats|im|youre|"
    r"(?:would|will|might|must|could|can|may) be)\b")


# "any way to put it, it hurts": the line goes on after the ask to say what it really says, so the
# ask is part of the sentence and not the whole of it. norm_text keeps a clause break as " | ", so a
# clause with two words or more after the ask means the line has its own ending already.
HELP_ASK_TAIL_CLAUSE = re.compile(r"\|\s*\w+\s+\w+")


HELP_ASK_NOT = re.compile(
    r"\b(?:no|not|isnt|isn't|wasnt|wasn't|arent|aren't|cant|can't|couldnt|couldn't|dont|don't|"
    r"doesnt|doesn't|didnt|didn't|never|nothing|without|hardly)\b")


# A line that names something of its own is asking about that thing, not for a way in: "is there
# anything i can do about the mole on my back" wants the mole answered (or an honest "I don't
# know"), not "what have you tried so far", which nobody can answer about a mole. So the ask has
# to stand alone, with no possession ("my", "our") and no "the <thing>" in the line.
HELP_ASK_OWN_SUBJECT = re.compile(
    r"\b(?:my|our|his|her|their|your|the|a|an)\s+[a-z]")


def _asks_for_help(text):
    """True when the line asks for help in a shape that does not open like a question.

    "anything i can do about it", "any way of making it easier", "anything that helps". The ask
    has to be the line's own question, so a negation before it ("there isnt anything i can do")
    or a copula after it ("anything i can do is never enough") leaves the line a statement.
    """
    if HELP_ASK_OWN_SUBJECT.search(text):
        return False
    for match in HELP_ASK.finditer(text):
        if HELP_ASK_NOT.search(text[:match.start()]):
            continue
        tail = text[match.end():]
        if HELP_ASK_SUBJECT.search(tail) or HELP_ASK_TAIL_CLAUSE.search(tail):
            continue
        return True
    return False


# A judgement asked about the thing just said, with nothing named in its place: "is that bad",
# "is that normal", "should i worry", "will it get worse". The line is a yes/no question and its
# whole content is the judgement, so the answer is in what the bot itself last said - but only a
# module that reads the previous turn can give it. Read as an ordinary short line it was an
# acknowledgement ("is that bad" got "Sounds good.", which agrees the fault is fine), so the
# reading names it for whoever can answer it.
VERDICT_ASK = re.compile(
    r"(?:and |so |but |ok |okay |also |sorry |oh |hmm )*"
    r"(?:"
    r"(?:is|was|are|were|does|do|did) (?:that|this|it)(?: all)?"
    r"(?: (?:really|actually|very|too|that|so))?"
    r"(?: (?:bad|normal|serious|dangerous|ok|okay|fine|safe|common|"
    r"a|much of a) ?"
    r"(?:problem|worry|issue|big deal)?"
    r"| (?:going to|gonna) (?:get|be) worse"
    r"| (?:going to|gonna) (?:spread|get worse))"
    r"|(?:is|was) (?:that|this|it)(?: (?:going to|gonna))? (?:get worse|getting worse|spread|serious)"
    r"|(?:is|was) (?:he|she|they) right"
    r"|(?:are|were|is|was) (?:they|these|those) (?:safe|ok|okay|fine|normal|bad|a problem|a risk|any good)"
    r"|(?:should|do|ought) i (?:be )?(?:worried|worry|worrying|bother)"
    r"|does (?:that|this|it) matter"
    r"|will (?:that|this|it) (?:get|be) (?:worse|ok|okay|fine)"
    r")"
    r"(?: then| though| honestly)?")


# The words that make a line a question about something other than what the bot just said.
QUESTION_WORD = re.compile(r"\b(?:why|when|where|how|who|whom|whose|which|what)\b")


def _asks_a_verdict(text):
    """True when the line asks for a judgement of the thing just said.

    The verdict is usually the whole line ("is that bad"), and the cap below is what keeps a line
    with a subject of its own out. But the same question is asked after the thing it is about, and
    that line carries no reading at all by the whole-line form: "my resting heart rate is 90 is
    that bad", "i left the chicken out all night is it safe", "they said two weeks is that normal"
    (48 of the deck's 60,260 turns got no shape of their own this way, and 18 more got a wrong one).
    The tail is read by the same pattern, and the cap stays on the *verdict clause* rather than on
    the line, so a short statement in front of the verdict does not hide it.
    """
    flat = re.sub(r"[^a-z0-9 ]+", " ", (text or "").lower())
    flat = re.sub(r"\s+", " ", flat).strip()
    if not flat:
        return False
    words = flat.split()
    if len(words) > 30:
        return False          # a long line is a statement with its own subject, not this ask
    if VERDICT_ASK.fullmatch(flat) is not None:
        return True
    # The verdict at the end, from any word that leaves at most seven of them: the pattern itself
    # is what says a verdict is there, so a "did" or an "is" inside the statement matches nothing.
    # The words in front must be a statement, though: "when should i worry" and "and why does it
    # matter" end on a verdict pattern word for word, and both ask a different question - a when
    # and a why - so a question word before the verdict keeps that reading.
    for start in range(1, len(words) - 1):
        if len(words) - start > 7:
            continue
        if QUESTION_WORD.search(" ".join(words[:start])):
            return False
        if VERDICT_ASK.fullmatch(" ".join(words[start:])) is not None:
            return True
    return False


# A line that only rules something out is not a new subject, it is a limit on the last answer:
# "recommend a film" / "no horror" is still a film line, and "training the lead" / "no treats"
# is still the dog. Read as a fresh line, the word after "no" becomes the topic and the bot
# answers the thing the person just ruled out (a horror list, a spaghetti bolognese).
# The shapes below are the ones people type. Each keeps the thing it rules out, so the composer
# can take it out of the answer above instead of starting again.
LIMIT_SHAPES = (
    ("no", re.compile(r"\bno\s+(?:more\s+)?([a-z][a-z' -]*?)\s*$")),
    ("nothing", re.compile(r"\bnothing\s+([a-z][a-z' -]*?)\s*$")),
    # "not spicy" is not a limit on anything, it is what the person says the food is not; the
    # word that makes it a limit is the one that turns a degree down ("not too spicy").
    ("not", re.compile(r"\bnot\s+(?:too|very|that|so|any)\s+([a-z][a-z' -]*?)\s*$")),
    # "not the sad ones" is the same limit said with the group spelled out: the plural stand-in
    # at the end says it is one of a set already on the screen, so the article in front is not
    # the person starting a sentence about a thing ("not the best" stays a verdict).
    ("not_the", re.compile(r"\bnot\s+the\s+([a-z][a-z' -]*?)\s+ones?\s*$")),
    ("without", re.compile(r"\bwithout\s+(?:the\s+|any\s+)?([a-z][a-z' -]*?)\s*$")),
    ("skip", re.compile(r"\b(?:skip|hold|drop|minus|leave out)\s+(?:the\s+|any\s+)?"
                        r"([a-z][a-z' -]*?)\s*$")),
    ("dont", re.compile(r"\bi\s+(?:dont|do not|can't|cant|can not)\s+(?:eat|drink|like|want|"
                        r"have)\s+([a-z][a-z' -]*?)\s*$")),
    ("allergic", re.compile(r"\bi\s+(?:am|m)\s+allergic\s+to\s+([a-z][a-z' -]*?)\s*$")),
)


# The softeners a person puts round a limit, front and back ("ok, no garlic please").
LIMIT_SOFT_BEFORE = re.compile(
    r"^(?:ok|okay|so|and|but|well|right|then|also|honestly|hmm|oh|ah|actually|btw)\b[\s,]*")


LIMIT_SOFT_AFTER = re.compile(
    r"[\s,]*(?:please|pls|thanks|thank you|then|though|tbh|honestly|lol|for me|this time|"
    r"at all|i guess|i suppose|to be honest|as well|instead)\s*$")


# A limit names a thing, not a sentence: three words is the most a dish, a genre or a pet food
# takes ("no more horror films"), and a verb inside it means the person is describing something.
LIMIT_ROOM = 3


# Words that fill "no ___" and "not ___" without ruling anything out: "no idea", "not sure",
# "no way", "not bad". None of them is a thing to take out of an answer, and read as one they
# would turn a shrug into a limit on the last line.
LIMIT_REFUSAL = frozenset("""idea clue way sure bad good luck doubt joke point matter rush hurry
wonder worries worry problem bother chance need thanks ta worries offence offense kidding
question answer option options choice change pain help helps well right myself yourself self
left yet though either sorry wait enough much many more less quite finished still now bake
since until after before""".split())


# A thing starts with a word that introduces something else, or continues a sentence the person
# is still writing: "nothing with subtitles", "not since breakfast" and "no, not shellfish" are
# not a thing taken away, and read as one they would empty an answer of the wrong part.
# A date or a number is not a thing to take out of an answer: "no, june" and "no, 8 kilos" are
# the person correcting what they said, and read as limits they would empty the last answer of
# the month or the figure they have just put right.
LIMIT_A_FACT = frozenset("""january february march april may june july august september october
november december monday tuesday wednesday thursday friday saturday sunday today tomorrow
yesterday morning afternoon evening night week weekend month year
one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty
hundred thousand couple few half lot""".split())


LIMIT_NOT_A_START = frozenset("""with without about for from by like not probably maybe wait sorry
enough too very much many more less just only at all and or but so then also""".split())


# A thing is named by its last word: "no checked bag", "no boiled sweets" and "no baked beans"
# all end on the thing itself. A limit whose last word is a past tense is a sentence about what
# happened - "nothing got decided", "no one asked" - and read as a thing it takes a clause out of
# the answer above: "how did the meeting go" / "nothing got decided" was answered "Right - no got
# decided, then." A state people do limit ("not too tired", "no felt tip") is not a past tense, so
# this only turns away the sentences.
PAST_ENDS = re.compile(r"^(?:[a-z]{3,}(?:ed|ought|aught)|went|got|came|said|saw|made|took|gave|"
                       r"found|lost|left|ran|broke|fell|kept|met|paid|put|sent|sat|stood|"
                       r"thought|told|won|wrote|bought|brought|caught|chose|drove|flew|forgot|"
                       r"heard|held|hit|knew|ate|drank|slept|woke|bit|spoke|spent|built|burnt|"
                       r"burned|grew|threw|been|being)$")


# The word after "nothing" has to be the thing being ruled out, and people say "nothing works",
# "nothing helps", "nothing changes" - a whole clause with the thing left out, where the word
# after "nothing" is the verb. Read as a thing, it took "works" out of the answer above:
# "my laptop is broken" / "nothing works" was answered "Nothing there was about works, so the
# answer holds." A limit always names something, so a common verb is not one - the opposite of
# PAST_ENDS above, which turns away the sentences with a past tense in them. Only the third-person
# present is listed, because a rule about the "-s" ending would throw away "no sweets",
# "no crisps" and "no horror films", which are limits.
A_THING_NOT_A_CLAIM = frozenset("""works work helps help changes happens matters seems makes does goes
comes gets stops starts fixes fits runs moves shows feels looks sounds costs needs stays keeps turns
grows hurts adds counts means bothers lives takes gives brings appeals excites suits
satisfies interests improves settles lasts ends agrees sticks sorts arrives
# The irregular pasts, which no ending rule reaches: "nothing got sorted", "nothing came of it",
# "nothing went right", "nothing did". Each of those was answered with the answer described back
# at the person - "Nothing there was about got sorted, so the answer holds" - so the verb is
# listed in the tense it is said in as well as the one the list starts in.
got came went did was were""".split())


# The same words said in another tense: "nothing helped", "nothing has worked", "nothing is
# working". The reading looks at the last word of the limit, so the ending is stripped before the
# list is asked - the two forms that are a claim are the past tense and the "-ing", and neither is
# a thing anybody limits ("no sweets" strips to "sweet", which is not on the list).
CLAIM_ENDS = ((3, "ing"), (1, "s"), (2, "ed"), (1, "d"))


# The list is written in one tense and people say these words in every tense: "nothing works",
# "nothing worked", "nothing has worked", "nothing changed". The list's own "changes" and the
# line's "changed" are the same claim, but neither is the other word, so both sides are cut back
# to a stem before the list is asked. "moved" leaves "move" and meets "moves"; the -ed cut that
# leaves "mov" is why more than one stem is tried. A doubled consonant is undone for the same
# reason: "stopped" is "stop", which is what "stops" leaves.
CLAIM_STEMS = frozenset(form[:-1] if form.endswith("s") and len(form) > 3 else form
                        for form in A_THING_NOT_A_CLAIM)


def _claim_forms(word):
    """The stems a word could be, so "changed", "changes" and "change" all answer to one."""
    forms = {word}
    for cut, _suffix in CLAIM_ENDS:
        if len(word) > cut + 2:
            forms.add(word[:-cut])
    if word.endswith("ing"):
        forms.add(word[:-3] + "e")
    for form in list(forms):
        if len(form) > 3 and form[-1] == form[-2]:
            forms.add(form[:-1])
    return {form[:-1] if form.endswith("s") and len(form) > 3 else form for form in forms}


def names_a_claim(word):
    """True when the word after "nothing" is the verb of a clause with its object left out."""
    word = str(word or "").lower()
    if word in A_THING_NOT_A_CLAIM:
        return True
    return any(form in CLAIM_STEMS for form in _claim_forms(word))


LIMIT_NOT_A_THING = frozenset("""i me my we you he she they it them us her him his hers its our
ours your yours their theirs mine whom is are was were be been
am do does did have has had can could would should will just really very too so much any some
the a an of to for in on at and or but if that this these those there here what when where who
something anything everything nothing other else matter way bit lot lots one ones thing things
to""".split())


# A thing the line says it does NOT mean is not what the line is about. "i want to save money" /
# "for a holiday not a house" got the house-left-empty card, because "house" opens that entry and
# "holiday" closes it, and the person had said the opposite of the house. The words stay in the
# line, so it can still be said back whole; only the reader that answers it skips them, the way it
# already skips an intensifier ("what on earth is wrong with my boiler" is about the boiler).
# The article is what makes it a thing being ruled out rather than a verb being denied: "i could
# not sleep" rules out no sleep and is the insomnia card, "not a house" rules out a house.
RULED_OUT = re.compile(
    r"\b(?:not\s+(?:a|an|the)|rather than\s+(?:a|an|the)?|instead of\s+(?:a|an|the)?)"
    r"\s+([a-z][a-z'’-]*(?:\s+[a-z][a-z'’-]*){0,2})", re.I)


# Words that end the thing being ruled out: what follows them is the rest of the sentence.
RULED_OUT_ENDS = frozenset("""and but or so because if when then please though although actually
really either too now tonight today anyway for with in on at to of is are was were be been do does
did have has had can could would should will""".split())


# The words a line spends on asking rather than on naming a thing. A ruling-out needs a thing to
# be a ruling-out OF: "for a holiday not a house" contrasts a house with a holiday, while
# "recommend a film" / "not a series" has nothing in front of the cue but the ask, and there the
# ruling-out is the question (a film, not a series) rather than a correction.
RULED_OUT_NO_THING = frozenset("""what about recommend recommends suggest show give find is are was
were do does did can could would should will you u ur me my i we us the a an of to for in on at
and but or so if when then there here this that these those it its be been have has had any some
please thanks ok okays just also too more most than rather instead not no yes something anything
anything""".split())


_A_CLASS_OF_THING = []


def _a_class_of_thing():
    """The words of a class a refusal can be handed back inside ("not a thriller", "not tablets")."""
    if not _A_CLASS_OF_THING:
        from ..compose.ruledout import RULED_OUT_CLASS, RULED_OUT_INSTANCES
        words = set(RULED_OUT_CLASS)
        for members in RULED_OUT_INSTANCES.values():
            words |= set(members)
        _A_CLASS_OF_THING.append(frozenset(words))
    return _A_CLASS_OF_THING[0]


# A ruling-out is only a correction when the line says it is one: the person has already said
# something and is putting it right. "i want my money back not a repair" is a question about the
# two of them together - the refund-you-choose-instead-of-a-repair card is the answer - and read
# as "i want my money back" alone it lost that card. "actually i mean for a holiday not a house"
# is putting right the house the saving answer had taken.
RULED_OUT_CORRECTION = re.compile(
    r"\b(?:actually|i mean|sorry|make that|on second thoughts?|rather|instead|no,|nope)\b", re.I)


def _ruled_out_of(text):
    """The words of a thing the line says it does not mean, for the reader to skip.

    "for a holiday not a house" hands over ["house"]; "a laptop not a tablet" hands over
    ["tablet"]. A cue with no article in front of it is a verb being denied ("i could not
    sleep"), not a thing ruled out, so nothing comes of it, and a cue with nothing in front of it
    but the ask rules nothing out: "recommend a film" / "not a series" is a question about films,
    and its reader needs the word "series" to tell one from the other.
    """
    if not text:
        return []
    gone = []
    for match in RULED_OUT.finditer(text):
        said_before = text[:match.start()]
        before = [word.strip(" .,!?;:\'\u2019").lower() for word in said_before.split()][-3:]
        if not [word for word in before if word and word not in RULED_OUT_NO_THING]:
            continue
        # A class of thing the refusal composer can hand back is left to it: "i fancy a film but
        # not a scary one" is answered inside the answer they have (the same films, not the scary
        # ones), and read as a bare "i fancy a film" it loses the films they turned down and the
        # words they gave the turn after.
        if [word for word in match.group(1).split() if word.lower() in _a_class_of_thing()]:
            continue
        # "a cheap one not a gaming one" contrasts two of the same thing, and the "one" at the
        # end is what says so: the gaming laptop is not the thing asked about, the cheap one is.
        same_thing = match.group(1).split()[-1].lower() in ("one", "ones")
        if not same_thing and not RULED_OUT_CORRECTION.search(said_before):
            continue
        for word in match.group(1).split():
            word = word.strip(" .,!?;:'\u2019\u201c\u201d")
            if not word:
                break
            if word.lower() in RULED_OUT_ENDS:
                break
            gone.append(word)
            if len(gone) >= 4:
                break
    return gone


def _limit_of(text):
    """The thing the line rules out, or None when the line says more than that.

    The whole line has to be the limit, with only the softeners people put round one. "no
    horror" is a limit; "no horror but i liked the last one" is a line of its own, and "no
    thanks" rules out nothing at all.
    """
    if not text:
        return None
    ask = " ".join(text.replace("|", " ").split()).strip(" .,!?").lower()
    for _ in range(3):
        shorter = LIMIT_SOFT_BEFORE.sub("", ask)
        if shorter != ask:
            ask = shorter
        shorter = LIMIT_SOFT_AFTER.sub("", ask).strip(" .,!?")
        if shorter != ask:
            ask = shorter
        if ask == LIMIT_SOFT_BEFORE.sub("", LIMIT_SOFT_AFTER.sub("", ask)).strip(" .,!?"):
            break
    for _name, shape in LIMIT_SHAPES:
        match = shape.search(ask)
        if match is None:
            continue
        thing = " ".join(match.group(1).split()).strip(" .,!?")
        words = thing.split()
        if len(words) > 1 and words[-1] in ("one", "ones"):
            # "no sad ones", "not the long ones": the last word stands in for the thing rather
            # than naming it, and it is on LIMIT_NOT_A_THING, so read as the thing it refused
            # the whole limit: "recommend a film" / "no sad ones" was answered with the warm
            # list and the limit unheard. "no one" is a single word and stays refused.
            thing = " ".join(words[:-1])
            words = thing.split()
        if not words or len(words) > LIMIT_ROOM:
            continue
        if any(word in LIMIT_NOT_A_THING for word in words):
            continue
        if any(word in LIMIT_REFUSAL for word in words):
            continue
        if words[0] in LIMIT_NOT_A_START:
            continue
        if PAST_ENDS.match(words[-1]):
            continue
        if ask.startswith("nothing") and names_a_claim(words[-1]):
            # Only a line that opens with "nothing": "no work" and "no costs" are limits on an
            # answer about work, and their words are on the list.
            continue
        if any(word in LIMIT_A_FACT or word.isdigit() for word in words):
            continue
        # The limit has to be the whole line: what is in front of it may be a softener only.
        before = ask[:match.start()].strip(" .,!?")
        if before and not LIMIT_SOFT_BEFORE.sub("", before + " ") == "":
            continue
        return thing
    return None


RECOMMEND_PHRASES = ("any good", "something good", "anything good", "worth watching",
                     "worth reading", "what should i watch", "what should i read",
                     "any ideas", "what would you recommend", "what do you recommend",
                     "help me choose", "help me pick", "any suggestions")


OPINION = ("what do you think", "what about you", "your favourite", "your favorite",
           "do you like", "do you prefer", "would you rather", "in your opinion",
           "what would you", "how about you")


CHOICE = (" or ", "better than", "instead of", "vs", "versus")


# Two ends of one scale about one thing are not a choice of two options. "is easter early or late
# this year" asks where the date falls, and the word "or" alone was enough to hand it the
# light-choice answer ("toss a coin and see if you are disappointed"), which is a shrug at a
# question the calendar answers. Each pair is (word, its opposite) as people type them.
OPPOSITE_PAIRS = (
    ("early", "late"), ("earlier", "later"), ("sooner", "later"), ("soon", "late"),
    ("hot", "cold"), ("warm", "cold"), ("big", "small"), ("large", "small"),
    ("long", "short"), ("high", "low"), ("good", "bad"), ("better", "worse"),
    ("wet", "dry"), ("sunny", "rainy"), ("fast", "slow"), ("quick", "slow"),
    ("cheap", "expensive"), ("busy", "quiet"), ("loud", "quiet"), ("full", "empty"),
    ("deep", "shallow"), ("heavy", "light"), ("thick", "thin"), ("wide", "narrow"),
    ("hard", "soft"), ("early", "on time"),
    # A thing is in or out, not one of two things to pick: "is the tide in or out" was read as a
    # choice and answered "Out. I wouldn't spend another minute on it". The two words sit either
    # side of one "or" about one subject, which is what this table is for.
    ("in", "out"),
)


# The words a line asking how something is starts with. Two ends of one scale are a scale only
# when the line is asking about one thing: "is easter early or late this year" wants the range,
# while "long or short hair" and "shall i have a long or short break" are two things to pick
# between, and standing the choice down there left the line with no ask at all and a shrug.
SCALE_ASK = re.compile(r"^\s*(?:is|are|was|were|will|would|should|when|what|how|which|be)\b")


def two_ends_of_one_scale(text):
    """True when the "or" in the line joins opposites rather than two things to pick between."""
    if not (SCALE_ASK.match(text) or "sooner or later" in text):
        return False
    for one, other in OPPOSITE_PAIRS:
        for first, second in ((one, other), (other, one)):
            # The two words have to sit either side of the "or" with nothing naming a thing
            # between them: "early or late" is one scale, "the early train or the late one" is
            # a choice between two trains.
            if re.search(rf"\b(?:the |a |an )?{first}\s+or\s+(?:the |a |an )?{second}\b",
                         text):
                return True
    return False


# "or" joins a choice only when the person has not already turned both sides down. "i dont want a
# dog or a cat" was read as a choice ask, and the composer answered "Cat." - a pick between the two
# things the person had just said no to - and "not pizza or curry" was quoted back as an option
# ("If you were hoping I'd say \"not pizza\", then you've decided already"). The tell is in front of
# the "or": a want, a like or a can-have that is negated, or a line that opens with the refusal.
# A choice put as a doubt ("i cant decide, pizza or curry") is untouched: the negation there is on
# deciding, not on either thing.
REFUSED_PAIR = re.compile(
    r"^\s*(?:no|not|never|without|neither)\b"
    r"|\b(?:dont|don'?t|do not|doesnt|doesn'?t|didnt|didn'?t|wont|won'?t|wouldnt|wouldn'?t|"
    r"cant|can'?t|cannot|shouldnt|shouldn'?t)\s+(?:\w+\s+){0,2}?"
    r"(?:want|wants|wanted|like|likes|love|eat|eating|have|having|drink|drinking|wear|do|doing|"
    r"need|needs|use|fancy|stand|bother|manage)\b"
    r"|\ballergic\b|\bhate\b")


def _turns_the_pair_down(text):
    """True when the thing before the "or" turns both sides down rather than asking which."""
    head = str(text or "").lower().split(" or ")[0]
    return bool(REFUSED_PAIR.search(head))


COMPARE = ("difference between", "different from", "compare", "which one", "or is it")


REQUEST = frozenset("help need want trying wanna please tell show explain give write make "
                    "how".split())


STEPS = ("how do i", "how can i", "how should i", "what should i", "step by step",
         "walk me through", "get started", "how to")


# "steps" on its own is an ask for the steps, but as a substring it is also the start of every
# step-relation: "my stepson is 21" was read as somebody asking to be walked through something,
# so a plain telling about the son came back as the search hedge. The word is matched whole.
STEPS_WORD = re.compile(r"\bsteps\b")


WRITE = ("write", "word", "phrase", "say", "message", "text to", "email to", "letter",
         "poem", "speech", "bio", "caption", "wish")


# The words for a low day that are also ordinary words for a thing, a place or a measurement:
# "an empty shelf", "the flat is cold", "a blank page", "my fingers went numb", "the kitchen is
# a mess", "moved into a new flat". They are how somebody feels only when the speaker is the
# subject - "im empty", "i feel flat", "im in a bad mood" - so these cues are read with
# `_speaker_before` as well. Words that are only ever a feeling ("miserable", "gutted") are not
# here and need no check.
# A comparison is only the speaker's state when the speaker is the one it is said of: "i feel
# worse" and "im no better" are how they are, while "the traffic is worse today", "its getting
# worse" about a leak and "it could be worse" name the state of something else. Kept apart from
# SELF_ONLY_CUES so the sad list, which is built from that tuple, does not pick "worse" up: a
# state that got worse is the body's news, and the answer for it is rest, not a walk.
A_COMPARISON = frozenset(("worse",))


SELF_ONLY_CUES = (
    "empty", "flat", "hollow", "blank", "numb",
    "rubbish", "crap", "rotten", "rough", "lousy",
    "like a failure", "like a mess", "like rubbish", "like crap", "like a burden",
    "like a fraud", "a mess",
    "in a bad mood", "in a low mood", "in a foul mood", "in a mood", "in a state",
    "in a right state", "out of sorts", "off colour", "off form",
)


# The same shape said in several words, and the phrases sit here rather than in the sad list
# because each names its own feeling: a carpet is worn thin, a credit card is at its limit, a
# branch is at breaking point. "the carpet is worn thin" and "the card is at my limit" are the
# carpet and the card; "im worn thin", "im at my wits end", "im beside myself" and "im at the
# end of my patience" are somebody's day. "im at the end of my rope" is the hopelessness list's,
# so it is left out on purpose - that one is a crisis cue, not a mood.
# The words for being lost in something are also the words for a form, a recipe and a plan being
# hard to follow: "the instructions are confusing", "there was confusion about the dates". They
# are the confused key's, and they are the speaker's own only when the speaker is the subject -
# so the check is here rather than in SELF_ONLY_CUES, which is the sad list's.
CONFUSED_SELF_ONLY = frozenset(("confused", "confusing", "confusion", "muddled", "baffled",
                                "bewildered", "puzzled"))


# A word that names what a person does to other people is a label on them, not a mood of theirs:
# "im boring" and "my mum says im boring" are somebody's verdict, and read as the person's own
# boredom the line got "Try something with your hands: a new recipe, a jigsaw, or one drawer
# tidied" - an answer to a complaint nobody made. The same word names a mood when a thing is its
# subject ("the film was boring", "work was exhausting"), which is the reading that stays.
LABEL_ON_A_PERSON = frozenset((
    "boring", "annoying", "tiring", "exhausting", "draining", "knackering", "frustrating",
    "depressing", "embarrassing",
))


THING_OR_PERSON_CUES = frozenset((
    "worn thin", "worn to a thread", "at my limit", "at breaking point",
    "at my wits end", "at my wits' end", "beside myself", "at the end of my patience",
    "reaching the end of my rope",
    # A worry is said of things as well as people - "the news is worrying", "the cough is
    # worrying me", "my mum is worrying about money" - and "worn down" is said of stairs. Read
    # as the speaker's state wherever the word appears, all of those would claim the person in
    # the line is the one who is anxious, so they are read only where the line says the state
    # is the speaker's own: "im worrying", "im stressing about money", "im worn down by the kids".
    "worrying", "stressing", "stressed out", "overthinking", "obsessing", "spiralling",
    "spiraling", "worn down",
))


# One of those phrases is also the money row's. `bot/knowledge/money.py` keys the `cant-pay`
# answer on "at my limit", and puts the period words in that row on purpose: "i'm at my limit
# every month" says the money is the month, not that somebody has had enough. A period in the
# line is what says which, so the phrase is no mood when one is there - the card or the budget
# keeps the answer it had. "im at my limit with the kids" and "im at my limit" have no period
# and stay a feeling.
# A day, a week or a month the speaker had, told with a state word in front of it: "i had a low
# day", "ive had a low few weeks", "today was a low day". The state word stands in front of the
# period and not in front of the speaker, so the speaker check below never sees a person as its
# subject and the line read as news about a thing - "Thanks for telling me" for a low day. The
# period is what makes the state the person's: a thing's own reading stays a thing ("the battery
# was low all day"), and a day that was busy is still busy ("i had a mad day").
OWN_PERIOD_NOUNS = frozenset("""day days week weeks month months year years weekend weekends
night nights morning mornings afternoon afternoons evening evenings shift shifts term""".split())


# What may stand between the state word and the period it is said of: "a low few weeks", "a low
# old week", "a low sort of day".
OWN_PERIOD_FILLER = frozenset("""a an the one few couple of real proper whole entire bit those
these sort kind old long bad""".split())


# The heads that make a period the speaker's own: the person, the day, or the part of it they
# are in. Anything else - "the battery was low all day", "his week was low" - is not their state.
OWN_PERIOD_HEADS = frozenset("""i we i've ive me today yesterday tonight""".split())


OWN_PERIOD_STOPS = frozenset("""and but because so though while if when than then that which
who whose after before since until""".split())


# A state word whose sense in front of a period is the period's own kind, not the person's: "a mad
# day" is a busy one and "a flat week" a dull one. (A separate fix reads `mad` as a thing's state
# everywhere; this list is what keeps the fallback below from inventing an anger for a busy day.)
NOT_THE_SPEAKERS_DAY = frozenset(("mad", "flat", "dead", "mental", "wild", "slow", "heavy"))


# How far back the head of the clause may be: "i had a really bad low week" names the speaker
# three words before the state, and a longer run than that is another clause.
OWN_PERIOD_REACH = 6


PERIOD_CUES = frozenset(("at my limit",))


A_PERIOD = re.compile(
    r"\b(?:every|each|this|next|last|a|per)\s+"
    r"(?:(?:single|whole|full|other|coming|past|few|one|more)\s+)*"
    r"(?:month|week|fortnight|pay ?day|paycheck|wage)\b"
    r"|\bmonthly\b|\bweekly\b|\bfortnightly\b|\bpay ?day\b")


# A period says the line is about money only when the money is named: a month is a billing cycle
# ("every single month", "with the electric every month"), a money word is what the limit is
# going on (the rent, the bill, the overdraft). A week with nothing else named is how long a
# person can keep going, so "im at my limit every single week" is somebody's week and not a
# card, and so is "im at my limit any week now", which is a point in time rather than a run of
# them ("any" is deliberately not a period word).
# A month is a billing cycle and so is a payday, but a paycheck is a word the money row does
# not yet answer: it carries "pay" and "pay cheque", and a line typed as one word would read as
# money with no card to answer it ("I'm listening"). The word is left as a period and not as a
# month, so "im at my limit every paycheck" stays the person's week, the way it does on main,
# until the row learns the joined spelling.
A_MONTH_PERIOD = re.compile(r"\b(?:month|monthly)\b|\bpay ?day\b")


A_MONEY_SUBJECT = re.compile(
    r"\b(?:rent|mortgage|bills?|electric(?:ity)?|gas|water|council tax|overdraft"
    r"|credit card|loan|debt|debts|childcare|nursery fees|fees|fuel|heating)\b")


# The limit is about a person or a day's work, not about money: "with the kids" and "at work"
# are somebody's week however long it runs.
A_LIMIT_ABOUT_PEOPLE = re.compile(
    r"\b(?:with (?:the|my|our|their|his|her|these|those)\s+"
    r"(?:kids?|children|child|family|mum|mom|dad|parents|partner|husband|wife|boss|team)"
    r"|at work|at school|at college)\b")


# "im beside myself laughing", "im beside myself with laughter": the phrase says what the
# laughing is like, not how the person is, so a cue with laughter after it is no mood at all.
LAUGHED_OFF_AFTER = re.compile(
    r"(?:with\s+|in\s+)?(?:laughter|laughing|laughs|cracking up|stitches)\b")


def _laughed_off(text, cue):
    """True when the phrase is followed by laughter: "im beside myself laughing"."""
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        if LAUGHED_OFF_AFTER.match(text[match.end():].strip()):
            return True
    return False


# The rest say "myself" or a whole clause, so they cannot be said of a thing and need no
# speaker check: "im not myself", "i dont feel like myself", "i feel nothing". The words are
# the normalised ones, because "dont" is read as "do not" before this runs.
SAD_PLAIN_CUES = (
    "dead inside", "feel nothing", "like nothing matters", "not myself", "not feeling myself",
    "not been myself", "do not feel myself", "do not feel like myself", "have not felt myself",
    "have not been myself",
)


# The words above that also describe a thing, a day or a job: "work has been awful lately", "my
# energy is low", "the windscreen is shattered", "ive spent the rent". They are somebody's state
# only when the speaker is the subject, so they carry the same check as SELF_ONLY_CUES without
# being added to the sad list.
# A mood that is also a doing or a thing: "the past tense was wrong", "the match wiped out",
# "he whacked the nail in", "the glass shattered", "i was zonked by the heat of the day".
# A fire, a sea, a pan and a bulb can rage, seethe, fume and be incandescent; only a person is
# furious about it, so the word before one of those has to be a person: "im seething" counts,
# "the sea was seething" does not.
SELF_ONLY_STATE = frozenset(
    "low awful hopeless worthless shattered wiped wasted spent "
    "tense pooped whacked zonked "
    # "im blue" is the mood; the sky, a door and a pair of jeans are the colour.
    "blue "
    "raging fuming seething incandescent".split())


# The same kind of word that a body can be as well: "my stomach is upset" is a stomach.
BODY_STATE_CUES = frozenset(("upset", "low", "awful", "rough", "rotten"))


# "flat out" is a full week and "flat broke" is no money: the idiom, not the state.
# "flat out" is a full week and "flat broke" is no money; "in a mood for pizza" is an appetite.
# Each is the idiom, not the state.
# "cheap and cheerful" is a kind of place or option, not a person's mood: "cheap and cheerful is
# fine" answered the happy pool ("That's a good feeling to carry into the rest of the day") to a
# line agreeing to a cheaper trip.
IDIOM_STATES = re.compile(r"\bflat\s+(?:out|broke)\b|\bflat as (?:a|an) \w+|"
                          r"\bcheap\s+and\s+cheerful\b|"
                          r"\bin (?:a|the) mood for\b|"
                          r"\b(?:bit of a|a bit of a|a right|a proper)\s+"
                          # "what a mad one" is left out on purpose: with nothing after it, it
                          # is the day they had, and the shell keeps that reading
                          r"(?:mad|weird|strange|funny|odd|daft|curious)\s+one\b")


# A heart breaks in a shape no single feeling word is in: "my heart is broken and i dont know
# what to do" named no feeling at all, so it was filed as news and answered "Got it. Is there
# anything you'd like a hand with?" while "im heartbroken" got the sorry-and-a-walk reply. The
# heart is the thing that is broken, in pieces, shattered, torn, aching or heavy, and the words
# between "heart" and the state are the ones people put there ("still", "completely", "so").
# A heart that is racing, pounding or fluttering is a body rather than a feeling and stays one:
# none of these shapes is how a pulse is described. "heartbreaking" is left out on purpose - it
# is said of a film or a story, which is a thing, and not of how the person is.
HEART_DEGREES = (r"(?:still|really|so|very|totally|completely|utterly|absolutely|just|all|"
                  r"now|quite|too|already|a bit|kind of|sort of)")


HEART_IN_A_STATE = re.compile(
    r"\bheart(?:s|'s)?\b"
    r"(?:\s+(?:is|was|feels|felt|seems|has|had|been))*"
    r"(?:\s+" + HEART_DEGREES + r")*"
    r"\s+(?:broken|shattered|torn|in pieces|aching|aches|breaks|heavy|breaking)\b")


# The broken heart said as an adjective, which is how most people type it: "broken hearted",
# "heart-broken", and the one word "heartbroken" that puts the same two words the other way
# round. "heartbreaking" is left out: it is said of a film or a story, not of a person.
BROKEN_HEARTED = re.compile(r"\b(?:broken[\s-]?hearted|heart[\s-]?broken)\b")


# The broken heart said as a thing rather than a state: "i have a broken heart", "i dont know
# what to do with a broken heart".
A_BROKEN_HEART = re.compile(r"\b(?:a|an|my|our|her|his|their|your)\s+broken\s+heart\b")


BROKE_A_HEART = re.compile(r"\b(?:broke|breaks|breaking|break)\s+(?:my|our|her|his|their|your)\s+heart\b")


EMOTION_WORDS = {
    "sad": ("sad", "unhappy", "miserable", "gutted", "heartbroken", "cry", "crying", "tears",
            "disappointed", "devastated", "weepy", "tearful", "homesick", "rotten", "lousy",
            "meh", "rough", "crap", "rubbish", "fed up", "numb", "blue",
            # The phrases for having had enough: "im at my wits end", "im at my limit", "im at
            # the end of my patience". They were answered "I'm listening" or "Thanks for telling
            # me". They are worn down, the way "im so fed up" is, and not the worry of "im
            # beside myself" - that one is the anxious list's.
            "at my wits end", "at my wits' end", "at my limit", "at breaking point",
            "at the end of my patience", "reaching the end of my rope",
            # The everyday words for a low day that were read as a name or a shrug: "im glum",
            # "im mopey", "im despondent", "im a bit blah".
            "glum", "mopey", "teary", "downhearted", "despondent", "blah", "bleh",
            # The plain words people use for a low day that this list was missing: "im low",
            # "im upset", "i feel awful", "i feel hopeless", "im still grieving".
            "low", "upset", "awful", "hopeless", "worthless", "grieving", "mourning",
            "despair", "despairing", "in a dark place", "emotional") \
        + SELF_ONLY_CUES + SAD_PLAIN_CUES,
    "lonely": ("lonely", "alone", "isolated", "left out"),
    "angry": ("angry", "annoyed", "furious", "cross", "irritated", "frustrated", "mad",
              "grumpy", "cheesed off",
              # "im mardy with everyone", "im snappy today", "im a bit ratty", and "im mardy"
              # is the northern word for grumpy - without these the line read as an
              # introduction and answered "Nice to meet you, Mardy".
              "cranky", "snappy", "tetchy", "ratty", "mardy",
              # The words people reach for when they are past annoyed: "im livid", "im
              # seething", "im fuming", "im raging". The lexicon already held "livid" and
              # "raging" as feelings but the reading did not, so "im seething" was answered
              # "Thanks for telling me" - the bot heard no feeling at all.
              "livid", "seething", "fuming", "raging", "seeing red", "incandescent",
              # The plain idioms for a bad temper, none of which said anything before: "im
              # brassed off", "im narked", "im miffed", "im in a strop". "hacked off" is left
              # out on purpose: hacking the dead wood off a hedge is the same two words.
              "brassed off", "narked", "miffed", "in a strop"),
    "anxious": ("anxious", "worried", "nervous", "scared", "afraid", "stressed", "stress",
                "panic", "panicking", "overwhelmed", "dreading", "bricking it",
                # "bricking" on its own is left out on purpose: it is a single word, and a
                # single word in this table has to be a feeling the lexicon holds, or a line
                # about bricking up a doorway is read as nerves. The phrases carry the idiom.
                "bricking myself", "shitting myself", "crapping myself",
                "shitting it", "crapping it", "cacking myself", "cacking it",
                "shitting bricks", "butterflies",
                "on edge", "nervous wreck", "worried sick", "freaking out", "petrified", "anxiety",
                "terrified", "panicky", "in bits", "restless",
                # "im all jittery about the scan", "im antsy", "im edgy", "im tense".
                # "im aprehensive about the results" is the same feeling one letter out.
                "jittery", "antsy", "edgy", "tense", "apprehensive",
                # "im beside myself" is the one of these that is worry, and it was read as a
                # name and answered "Nice to meet you, Beside" before this. "at the end of my
                # rope" is left out of both lists on purpose: that one is the hopelessness
                # list's, and it is a crisis cue rather than a mood.
                "beside myself",
                # The doing form of a worry, which is how most people say it: "im worrying",
                # "im stressing about money", "im overthinking a text". The list held the
                # adjective and the noun - "worried", "stress", "panic" - so these named no
                # feeling at all and were answered "I'm listening - say more if it helps" or
                # "Thanks for telling me", the two lines STYLE.md calls the worst answers there
                # are. "panicking" was already here, so the frame reads the -ing form of a
                # feeling; it was only the words that were missing. "stressed out" was in the
                # lexicon as a feeling and not in this list, so the longer way of saying
                # "stressed" was the one that said nothing.
                "worrying", "stressing", "stressed out", "overthinking", "obsessing",
                "spiralling", "spiraling"),
    "tired": ("tired", "exhausted", "knackered", "worn out", "drained", "no energy",
              "burned out", "burnt out", "shattered", "wiped out", "wiped",
              # "im zonked after the night shift", "im pooped", "im whacked", and "im
              # frazzled", which said no state at all and got a listening noise.
              "zonked", "pooped", "whacked", "frazzled",
              # Worn down rather than out of steam all at once: "im worn thin", "im worn to a
              # thread".
              # "im worn down" is the plainest way of saying it and it named no feeling, so a
              # person worn down by a month of nights got "I'm listening".
              "worn thin", "worn to a thread", "worn down",
              # "my brain is fried", "im fried": nothing left to think with.
              "fried",
              # The same thing said as what the tiredness stops them doing, or as a tank:
              # "i cant even think straight", "im running on empty", "im running on fumes",
              # "my head is mush", "i can barely keep my eyes open".
              "think straight", "running on empty", "running on fumes", "head is mush",
              "heads mush", "keep my eyes open",
              # "im dead after today", "im dead on my feet", "im dead": the way people say
              # they have nothing left. The word is also the bereavement word, so it is in
              # `ALWAYS_SELF_ONLY` below - it only counts in the "im" frame, and "my dad is
              # dead" and "my phone is dead" are not this at all.
              "dead"),
    "happy": ("happy", "glad", "delighted", "thrilled", "pleased", "excited", "proud",
              "relieved", "chuffed", "awesome", "hopeful", "cheerful"),
    "grateful": ("grateful", "thankful", "appreciate"),
    "bored": ("bored", "boring", "nothing to do"),
    # Not knowing which way is up is a feeling of its own, and the reading had no key for it:
    # "im confused", "i feel muddled" and "i dont understand" named nothing, so they were
    # answered "Thanks for telling me — I'm here if you want to dig into any of that", the line
    # the bot gives a message it has heard nothing in. It is not "stuck" (nothing is in the way)
    # and not "scattered" (the mind is holding still and going over one thing): what a confused
    # person needs is a question that makes the missing bit easy to say. "confusing", "confusion"
    # and "muddled" are also said of a form, a set of instructions and a plan, so they sit in
    # CONFUSED_SELF_ONLY as well and are the speaker's only when the speaker is the subject.
    # "i cant get my head round this" is the same state said with a picture instead of a word,
    # and it read as nothing at all: the line got "I'm listening - say more if it helps", which
    # is what the bot says when it has heard nothing in a message. The person is not tired and
    # not stuck for a fact: they cannot follow this, and the confused pool asks which part is
    # foggy, which is the question that gets them talking.
    "confused": ("confused", "confusing", "confusion", "bewildered", "baffled", "muddled",
                 "puzzled", "dont understand", "do not understand", "dont get it",
                 "do not get it", "does not make sense", "makes no sense",
                 # The picture carries its own no: "i cant get my head round this" is not the
                 # state denied, it is the state said. The negated forms are listed whole for
                 # that reason - a cue without the "cant" in it would also fire on "i get my
                 # head round it", which is a person saying they do follow it.
                 "cant get my head round", "cant get my head around", "cant get my head straight",
                 "cannot get my head round", "cannot get my head around",
                 # normalise expands "cant" to "can not" for the words list, and the reading is
                 # made on that text, so the spaced form is the one it meets most often.
                 "can not get my head round", "can not get my head around",
                 "cannot get my head straight", "can not get my head straight",
                 "cant make head nor tail", "cannot make head nor tail",
                 "can not make head nor tail",
                 # "or" is what half the people who write it type.
                 "cant make head or tail", "cannot make head or tail",
                 "can not make head or tail",
                 "struggling to understand", "struggling to follow"),
    # The morning after, and the other ways a person says they are not well today. These are
    # states, not moods, and none of them is a name: "im hungover" was read as an introduction
    # and answered "Nice to meet you, Hungover". They are their own key so that a line which
    # asks what to do ("im hungover what should i do") still reaches the hangover entry instead
    # of a mood pool, and so that a plain "im hungover" gets the water-and-rest answer.
    "unwell": ("hungover", "hung over", "hangover", "under the weather", "run down",
               # "im feeling worse", "i feel worse today", "im no better": how a person says a
               # state has got worse, which is the commonest way a bad day is told in a second
               # turn. None of it named a state - "worse" is a comparison and "better" is the
               # good one - so "i feel worse" was answered "Thanks for telling me".
               "worse",
               "run-down", "jet lagged", "jet-lagged",
               # "cream crackered" is rhyming slang for knackered, and "crackered" is what
               # people write when they shorten it: without them the line named no state at all
               # and got the stock "Thanks for telling me".
               "cream crackered", "crackered"),
    # A condition somebody has is not a name, and it is not a mood either: "im bipolar" was
    # answered "Nice to meet you, Bipolar", and the store kept the name for the rest of the chat.
    # Its own key so that a line which asks something ("im bipolar and my meds have changed")
    # keeps its own reading, and so the memory store - which builds its "not a name" list from
    # every value here - stops filing the word as a person.
    "condition": ("bipolar", "schizophrenic", "anorexic", "bulimic", "narcoleptic", "psychotic",
                  "infertile", "sterile", "paranoid", "transgender", "nonbinary", "hiv"),
}


# Words that are only a state of the speaker's, whatever else they mean. They are not in
# `SELF_ONLY_CUES`, because that set is appended to the sad list's own words, and a word here
# belongs to one feeling: "dead" is tired ("im dead after today"), not sad, and "my dad is dead"
# is a bereavement that this file must not read as a mood at all.
ALWAYS_SELF_ONLY = frozenset((
    "dead", "fried", "running on empty", "running on fumes"))


# Feelings that are said as a "not", where the not is the feeling and not a denial of it: "i cant
# think straight" is being exhausted, and `denied` reads the "cant" as the line saying it is not
# so; "i can barely keep my eyes open" is the same with "barely". The opposite way round as well:
# the cue with no not in front of it is not the feeling, so "i can think straight now" and "i can
# keep my eyes open" stay nothing at all.
SAID_AS_A_NEGATION = frozenset(("think straight", "keep my eyes open"))


# A feeling word that is also half of an idiom, with the idiom spelled out: the word is not
# the feeling there. "im dead set on going" is a plan and "im dead right" is being sure, and
# neither is being tired. A cue only needs an entry here when the words after it would
# otherwise read as somebody's state ("dead on my feet" is tired, "dead set on" is not).
NOT_A_MOOD_THERE = {
    "dead": re.compile(r"\bdead\s+(?:set|right|against|certain|last|heat|giveaway|cert|"
                       r"keen|to me|to the world)\b"
                       # "im so dead" is being in trouble, usually with a time attached ("im so
                       # dead tomorrow"), not being out of energy - "im dead" and "im dead after
                       # today" already say that.
                       r"|\bso dead\b"),
    "fried": re.compile(r"\bfried\s+(?:rice|chicken|egg|eggs|bread|onion|potatoes|tomatoes|"
                        r"fish)\b"),
    # "think straight" says how the tiredness is, unless the words give it a subject: "he cant
    # think straight" and "my boss cant think straight" are somebody else's morning, and
    # `_state_owner` would have to say whose it is for a reply to use it.
    "think straight": re.compile(r"\b(?:he|she|they|my|his|her|their|its)\b[^.|]{0,20}"
                                 r"\bthink straight\b"),
}


# The names above whose words are the good ones. Denying a good word is a complaint about it
# rather than a denial of the state ("i am not happy about it", "im not pleased"), so the name
# stays and `polarity` carries the minus.
GOOD_EMOTION_NAMES = frozenset(("happy", "grateful"))


NEGATIVE = frozenset("""sad unhappy miserable gutted heartbroken cry crying tears disappointed
devastated lonely alone angry annoyed furious frustrated mad anxious worried nervous scared
afraid stressed panic overwhelmed dreading tired exhausted knackered drained sick ill hurt
pain ache sore worse worst hate awful terrible horrible bad fail failed failing lost lose
hate rubbish useless stupid annoyed upset""".split())


POSITIVE = frozenset("""happy glad delighted thrilled pleased excited proud relieved grateful
thankful love loved lovely great good nice brilliant wonderful perfect amazing fantastic
fun funny enjoy enjoyed success succeeded won win calm relaxed fine okay""".split())


# The words a line is said *to* rather than about: "thanks love", "morning pet", "cheers duck".
# They are feeling words too, so a short line that finishes with one was read as carrying a
# feeling: "thanks love" came back with a shrug where "thanks mate" is answered "No problem at
# all.", because the thank you stopped looking like one. The word is the person being spoken
# to, so it is not a feeling, and only the last word of a line people say to somebody counts.
TERMS_OF_ADDRESS = frozenset("""love mate pet hun honey sweetheart duck ducky flower sunshine
    pal bud chick dear darling babe lass lad bella""".split())


ADDRESSED_LINES = frozenset("""thanks thank cheers ta hello hi hiya hey morning afternoon
    evening night bye goodbye yes no ok okay alright right please sorry""".split())


# "ok" is a feeling only when it is said about somebody's state ("im ok", "i am doing ok"). On
# its own it is an acknowledgement ("ok so", "ok bye") or a permission question ("is it ok to
# leave an 11 year old home alone"), and counting those as a good feeling wiped out the bad
# one in the line.
OK_WORDS = frozenset(("ok", "okay", "okey"))
