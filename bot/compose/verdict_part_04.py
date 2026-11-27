"""Part 4 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re

from . import A_STEP_ASK, why
from .verdict_part_01 import (
    A_WAIT_IN_THE_STEP, FIX_ASKED_LINES, FIX_ASKED_NOW_LINES, NOT_A_STEP_TO_WATCH,
    NOT_A_STEP_TO_WATCH_WORDS, _ASKS_ABOUT_A_STEP, _ASKS_FOR_THE_STEP, _A_FIX_WORD, CARE,
    COMPARATIVE, CONDITIONAL, CONDITIONAL_AFTER, URGENT_TIME,
)
from .verdict_part_02 import (
    REFER, STATED_ENOUGH, DECLARATIVE_REFERRAL, NAMES_A_CLINICIAN, STEP_KEPT_LINES, _own_pattern,
    STEP, HANGING,
)
from .verdict_part_03 import (
    _a_job_somewhere, _flat, _say, opens_on_a_job, RUN, _WORD, COMPOSED, OWN_PATTERN, READABLE,
    UNREADABLE, _a_punt, _a_report_line, _is_a_recap, _is_an_echo, _skip_the_derived,
    takes_a_fact_back, EMERGENCY_CALL_OPEN, EMERGENCY_ORDER, ASKING_HOW_TO_TELL, SIGN,
    _the_person_line, _first,
)


def the_fix_asked(clean, memory):
    """A line for "and does that fix the pressure too", or "" when the line is not that ask.

    Read by the chat module: the step was given a turn ago and the question is whether doing it
    is the fix. Two things have to hold, and each of them is a way of leaving the turn alone:

    * the last thing the bot said opens on a job (`opens_on_a_job`) - there is a step for "that"
      to point at, and the person has already read it;
    * the line is short and asks about fixing - a long line brings its own subject, and a line
      that asks what to do next, how long it takes or why it happens is another question that
      the answers entry or the verdict line answers better.
    """
    flat = _flat(clean)
    if not flat:
        return ""
    words = flat.split()
    if len(words) > 10:
        return ""
    if not _ASKS_ABOUT_A_STEP.search(flat) or not _A_FIX_WORD.search(flat):
        return ""
    if _ASKS_FOR_THE_STEP.match(flat):
        # "how do i fix it" asks for the step and has not been given one yet, so the answer is the
        # entry's own ("Pull the hair and soap out of the trap"), not a line about watching one.
        return ""
    last = _last_reply(memory)
    if not last or not (opens_on_a_job(last) or _a_job_somewhere(last)):
        return ""
    if str((memory.get("last_answer") or {}).get("domain") or "").lower() in NOT_A_STEP_TO_WATCH:
        return ""
    if NOT_A_STEP_TO_WATCH_WORDS.search(last):
        # An answer about a person's body, an animal or a trade is not a step the person tries
        # and watches for a few days. "my baby is not feeding" is answered with "a baby under
        # three months who stops feeding needs looking at today", and "does that fix it" was told
        # to "give it a few days", which is the one thing that answer must never say. The guard
        # reads the answer, not the chat, so a boiler in a chat about a baby is still a boiler.
        return ""
    if A_WAIT_IN_THE_STEP.search(last):
        # The step said how long it takes to know, so the line about watching it holds.
        return _say(FIX_ASKED_LINES, memory, flat)
    # No wait in the step: the answer comes when they try it, so the line asks them to look
    # straight away. "Give it a day or two" over a blocked bath trap is advice that cannot be
    # followed - the tap tells them in a minute.
    return _say(FIX_ASKED_NOW_LINES, memory, flat)


def carries_the_answer(reply, memory):
    """True when `reply` comes back to the answer the bot gave a turn ago.

    Read by the arbiter (bot/modules/arbiter.py) on a turn that asks what to do next: the
    composer's step line keeps the answer's own opening ("Keep it plain, and take it from
    there." after "Keep it plain and separate: ..."), and a hand-back keeps its first sentence,
    so both share a run of four words with it. An entry that only shares the topic shares none:
    "Five a day is 400g, and a portion is a handful" after an answer about a child refusing veg.
    Wording only, and nothing about the subject, so no entry can be read as a repeat it is not.
    """
    if _kept_step(reply):
        # The step has not changed, and the line says so instead of saying it again: "Still the
        # same move, and nothing to add to it" is about the answer above by construction, and it
        # shares none of its words because repeating them is the fault it exists to avoid. It is
        # still a line that answers from the answer, so the arbiter is told the same thing about
        # it as about a quoted step.
        return True
    said = _WORD.findall(_flat(_last_reply(memory)))
    words = _WORD.findall(_flat(reply))
    if len(said) < RUN or len(words) < RUN:
        return False
    runs = {" ".join(said[i:i + RUN]) for i in range(len(said) - RUN + 1)}
    return any(" ".join(words[i:i + RUN]) in runs for i in range(len(words) - RUN + 1))


def _last_reply(memory, past_the_nod=False, past_the_verdict=False):

    """The last answer of the bot's this turn is a follow-up to, or "" if there is not one.

    It is the bot's own last line whichever module wrote it, because the step a person asks for
    is in that line and nowhere else: "im getting headaches every afternoon" is answered by the
    composer's warm line, and "what should i do" after it used to get "a quick search online".
    A safety or urgent answer is not read back (it has already said what to do now), and
    neither is a condolence.

    My own verdict line is not a change of subject: "the boiler pressure is low" / "is that bad"
    / "is that going to get worse" is still the boiler, so the question is read from the answer
    behind the verdict rather than dropped.

    A cause handed back by another composer is the same case: "the boiler keeps making a banging
    noise" / "why is that" / "is it dangerous" is still the boiler, so the reason line is read
    past to the answer it came out of. Both are composer lines, spoken as the fallback module,
    which is why the text decides it rather than the module name.
    """
    punt_line = ""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return ""
    # A frequency line and a healing line answer the turn before them rather than this question
    # (see `_skip_the_derived`): reading one as the answer hands the condition in it back as
    # "Nothing to do for now", where the trouble answer behind it is the one to read.
    turns = _skip_the_derived(turns, memory)
    for index in range(len(turns) - 1, -1, -1):
        last = turns[index]
        before = turns[index - 1] if index else None
        if not isinstance(last, dict):
            return punt_line
        module = last.get("module")
        said = str(last.get("bot") or "")
        if module in UNREADABLE:
            return punt_line
        if module == "chat" and OWN_PATTERN.search(_flat(said)):
            continue  # this composer's own line: the answer behind it is what to read
        if _a_report_line(said):
            continue  # the composer's report on the answer: the answer behind it is what to read
        if module in COMPOSED and why.is_a_reason_line(said):
            continue  # a cause handed back is the answer above, not a new one
        if module in READABLE and takes_a_fact_back(said):
            continue  # only taking a fact back: the answer behind it is the one to read
        if A_STEP_ASK.match(_flat(last.get("user"))) and last.get("module") != "answers":
            # Asking for the first step is not a change of subject, and the answer to it is not
            # always the card quoted back: "im getting headaches every afternoon" / "what should
            # i do first" comes back as a chat line, so the quote test above does not see it, and
            # the bare doubt after it read the line "what should i do first" - which names nothing
            # - and fell through to the chat pool's "Sounds good." The answer a doubt about the
            # headache is about is the headache card, one turn further back.
            #
            # Only a step the knowledge base did not answer is stepped past. A card answers the
            # ask for a step too, sometimes with a threshold the card above did not put the same
            # way ("Try a spoonful of honey before bed ... or three weeks of it is a reason to
            # ring the surgery"), and that answer is what the doubt is about: skipping it turned
            # "Not yet. The point where it wants a person: blood in it, breathlessness or three
            # weeks of it" into the shorter condition the card above writes.
            continue
        if _a_punt(last):
            # A turn that only said the person was heard is not an answer to read. It is still
            # the last thing said, so a walk that wants the line itself takes it; a walk that
            # wants the answer a doubt is about looks past one echo, and only to the knowledge
            # answer behind it. A run of echoes is not looked past at all: a person who has said
            # two lines since the answer has moved on from it.
            if not past_the_nod or punt_line:
                return said if not past_the_nod else punt_line
            punt_line = said
            continue
        if past_the_verdict and _only_a_verdict(last.get("user")):
            # The bot's line here is a comment on the news ("Annoying. Is it a quick fix or a
            # whole thing?"), not the answer it belongs to: the answer is the turn before it, and
            # the question in the comment is conversation, not a step the person has to take
            # first. Read past it exactly as a recap is read past.
            continue
        if _is_an_echo(last):
            continue  # a line said back is not an answer: the answer behind it is what to read
        if before is not None and _is_a_recap(last, before):
            # A step quoted out of the card above is that card said shorter, not new advice.
            # "what should i do first" after the laptop answer comes back as "The thing to do
            # first: Empty the Downloads folder and the bin.", and the doubt after it ("is that
            # safe") had nothing to read, so the chat pool gave "Sounds good." - the bot
            # agreeing that a full laptop is fine. The card behind the quote is the answer.
            continue
        if module in READABLE:
            if punt_line and module != "answers":
                return punt_line
            # The answer's own capitals, because the step is quoted out of it: "Run a hot 60C
            # service wash" came back as "60c" when the reply was flattened to lower case first,
            # and a temperature is not a word to lower.
            return said
        return punt_line
    return punt_line


def _a_call_for_now(said):
    """True when this line names somebody to ring or care for now, with no "if" on it.

    "Sorry to hear it — go easy on yourself today, and see someone if it's not shifting in a few
    days" is a greeting's own line, and the referral in it is fenced: "i feel dizzy" / "is that
    bad" was told "ringing is not an overreaction here, it is the whole point of it" for a
    dizziness that is ordinary. A cue with a condition after it in its own sentence is not a call
    for now, and the verdict path carries on without it.
    """
    if _care_for_now(said):
        return True
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        found = REFER.search(sentence)
        if not found:
            # An answer can name who without a verb in front of them: a safety line says what
            # the thing needs and who it is, "That needs a real person today - your midwife, GP
            # or 111 - because sickness that stops you keeping anything down can leave you
            # dehydrated", and the bare "is that bad" after it was the fallback's "Keep an eye on
            # it and tell me if anything changes": a doubt answered at a strength the answer
            # never asked for, under a call that said today. When did the answer say to go is
            # the question, and a trade and a time in one sentence is the answer saying now -
            # unless the trade itself is fenced ("if it is still there today, see your GP").
            trade = TRADE.search(sentence)
            if trade is None:
                continue
            if LATER_CONDITION.search(sentence[:trade.start()]) is not None:
                continue
            if TIME_NOW.search(sentence) is not None:
                return True
            continue
        if not LATER_CONDITION.search(sentence[found.start():]):
            return True
        # A time in the same sentence makes the referral a today one whatever fence follows it:
        # "ring 999 or 911 straight away, and keep the container ... ; 111 gives poisons advice
        # if they seem well" is an order for now, and the "if" belongs to the poisons line, not
        # to the call. `_condition_after_care` reads a fenced referral the same way.
        if TIME_NOW.search(sentence[found.start():]):
            return True
    return False


def _the_call_sentence(said):
    """The sentence that carries the call this answer makes, or the answer itself.

    A long answer puts its fence and its call in one breath: "a bent limb, bone through the skin or
    numb fingers is 999, otherwise get it checked at A&E or a minor injuries unit today" is a call
    for today, and reading the whole answer for the emergency word made it a 999. The call is the
    first sentence whose referral is not fenced, so that sentence is what "how urgent" is read
    from.

    A sentence that opens by naming the whole answer as an emergency has already given the order
    and needs no time word to say when: "That's an emergency: ring 999 or 911 and stay on the line"
    is a call for now, and so is "Treat this as an emergency and ring 999". Without that, the
    safety lines that do not say "straight away" were read as a call for today instead, and a
    doubt about one was answered "Not an emergency by the sound of it" over an answer that had
    just said to ring 999.
    """
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        if EMERGENCY_ORDER.match(sentence) is not None:
            return sentence
        opening = EMERGENCY_CALL_OPEN.match(sentence)
        if opening is not None and LATER_CONDITION.search(sentence[opening.end():]) is None:
            return sentence
        # Only a sentence that says when is a call for now: "a cut that gapes open, is deep, or
        # keeps bleeding through the cloth needs a nurse or A&E" names a place and no time, and
        # it is the answer's condition rather than its instruction.
        if TIME_NOW.search(sentence) is None:
            continue
        found = REFER.search(sentence)
        if found is not None:
            tail = sentence[found.start():]
            if LATER_CONDITION.search(tail) is None or TIME_NOW.search(tail) is not None:
                return sentence
            continue
        trade = TRADE.search(sentence)
        if trade is None:
            continue
        if LATER_CONDITION.search(sentence[:trade.start()]) is not None:
            continue
        return sentence
    return ""


def _said_enough(said):
    """The answer's own words saying the amount is enough, or None.

    Cut at the first comma when the sentence runs long: "Three half-hour sessions a week is enough
    to feel different in a month, and you need no equipment: a walk or a jog for ten minutes to
    warm up" is one sentence, and handing the whole of it back repeats the answer the person is
    looking at. The clause that says the amount is the half that answers them.
    """
    for sentence in re.split(r"(?<=[.!?])\s+", str(said or "")):
        if STATED_ENOUGH.search(sentence) is None:
            continue
        sentence = sentence.strip().strip("\"'\u201c\u201d").strip().rstrip(".")
        if len(sentence) > 90 and "," in sentence:
            head = sentence.split(",")[0].strip()
            if len(head) > 20 and STATED_ENOUGH.search(head) is not None:
                sentence = head
        if sentence:
            return sentence + "."
    return None


def _the_person_gave_the_sign(memory, said):
    """Whether the person's own last line already said the sign the answer tests for."""
    line = _the_person_line(memory, said)
    if not line or ASKING_HOW_TO_TELL.search(line):
        return False
    return bool(SIGN.search(line))


# A referral is for later, not now, when the "if" comes after it instead of in front of it:
# "Get it looked at if it gives way, locks, or you cannot put your weight on it". _unconditional
# _care only looks backwards, and that is right for the warning branches; asking whether the
# answer offers care wholesale needs the fence read from both sides.
LATER_CONDITION = re.compile(r"\b(?:if|unless|when|once|whenever|as soon as)\b", re.I)


# Who an answer names, with no verb in front of them. `REFER` reads "see your GP" and "ring 111";
# this reads "your midwife, GP or 111" and "a real person today", which is how a safety line and
# many health answers word the same call.
TRADE = re.compile(
    r"\b(?:gp|doctor|midwife|health visitor|111|999|112|a&e|dentist|pharmacist|optician|"
    r"physio(?:therapist)?|nurse|vet|paramedic|district nurse|out of hours)\b", re.I)


def _care_for_now(said):
    """True when the answer names care that is not fenced by a condition before it or after it."""
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        found = _first(sentence, CARE)
        if found is None:
            continue
        cue = min((sentence.lower().find(word) for word in CARE if word in sentence.lower()),
                  default=-1)
        # A fence in front of the cue counts as much as one behind it. "If it locks out twice, or
        # you smell gas, stop and call a Gas Safe engineer" has its "if" before the trade, and
        # reading that as care for now made the answer's own condition (locks out twice) the wrong
        # thing to hand back.
        if (cue >= 0 and not LATER_CONDITION.search(sentence[cue:])
                and not LATER_CONDITION.search(sentence[:cue])):
            return True
    return False


def _sentence_at(text, at):
    """The sentence of `text` that the offset `at` sits in."""
    begin = 0
    for found in re.finditer(r"(?<=[.!?]) ", text):
        if found.start() >= at:
            return text[begin:found.start()]
        begin = found.end()
    return text[begin:]


def _not_fenced(said, start, end=None):
    """True when no "if ..." sits either side of this cue inside its own sentence.

    A condition can come after the cue as well as before it: "it is worth getting it checked if
    it hurts or gives way" and "see a GP if the arm is weak or numb" are both advice for a
    condition, and reading only the words in front of the cue made them a verdict now.
    """
    before = said[max(0, start - 90):start]
    if CONDITIONAL.search(before.split(".")[-1]):
        return False
    if end is not None:
        after = said[end:end + 90].split(".")[0]
        # Unless the referral itself says when to act: "ring the vet today if it has been more
        # than 24 hours" is the threshold for acting, not a condition on whether to.
        fence = CONDITIONAL_AFTER.search(after)
        if fence and not URGENT_TIME.search(said[start:end + 40]):
            # The "if" fences the cue unless the words between them make it a degree of the
            # same errand: "so ring the vet, and sooner if he is also off his food or weeing in
            # the house" is a yes, and reading its later "if" as a fence answered a dog that
            # drinks too much with "do the job I described" about its water bowl. Only a
            # comparative counts, so "get it looked at the same day if you cannot put weight on
            # it" stays the conditional second sentence it is.
            rider = after[:fence.start()]
            if not COMPARATIVE.search(rider):
                return False
    return True


NEGATED_BEFORE = re.compile(r"(?:\bnot|\bnever|\bno|n't|\bless|\bhardly|\bexcept|\bwithout)"
                      r"\s+(?:\w+\s+){0,2}$")


def _said_without_a_not(text, at, length):
    """True when the word at `at` is said plainly, not under a "not", "less" or "un-"."""
    if text[max(0, at - 2):at] == "un":
        return False
    before = text[at - 1] if at else " "
    after = text[at + length:at + length + 1]
    if before.isalnum() or after.isalnum():
        return False  # "commonest" is not "common", and "unusually" is not "usually"
    return NEGATED_BEFORE.search(text[max(0, at - 26):at]) is None


def _first_positive(text, words):
    """`_first`, but a word with a "not", "less" or "un-" in front of it is not that reading.

    "it is common at four and still common at nine, but past ten it is **less usual**" says the
    opposite of "usual" for the age in question, and "not serious in most cases" is not the same
    answer as "nothing serious". Every worry cue is read this way, so the reassuring words cannot
    be borrowed from a sentence that took them back.
    """
    text = str(text or "").lower()
    best = None
    for word in words:
        start = 0
        while True:
            at = text.find(word, start)
            if at < 0:
                break
            if _said_without_a_not(text, at, len(word)):
                if best is None or at < best:
                    best = at
                break
            start = at + 1
    return best


# How often it happens, in the person's own words: "every afternoon", "most days", "all the time".
A_FREQUENCY_SAID = re.compile(
    r"\b(?:every|most|each|all) (?:\w+ )?(?:day|days|night|nights|morning|mornings|afternoon|"
    r"afternoons|evening|evenings|week|weeks|month|months)\b|"
    r"\ball the time\b|\balways\b",
    re.I)


# The answer's fence can be a fence on how often, too: "if you get them most days".
A_FREQUENCY_ASKED = re.compile(
    r"\bmost days\b|\bmost nights\b|\bevery day\b|\bregularly\b|\bseveral times\b|"
    r"\bmore than (?:once|twice)\b|\bkeeps? (?:coming|happening|returning)\b|"
    r"\btime and again\b",
    re.I)


# "the same day" is a call for now wherever it is written, so it belongs here with "today" and
# "straight away": the toothache card says "ring a dentist the same day" in its second sentence, and
# with it missing from this reading the answer's later fence ("a swelling in your face") was taken
# for its condition and `my tooth hurts` / `is that bad` was answered with a threshold instead of
# the same-day call the answer had just made. Found in review by @steward-merry-zebra.
TIME_NOW = re.compile(r"\btoday\b|\bnow\b|\btonight\b|straight away|as soon as|"
                      r"\btomorrow\b|\bthis (?:morning|afternoon|evening)\b|\bnext few hours\b|"
                      r"\bthe same day\b(?!\s+if\b)",
                      re.I)


# A condition can run to a list of triggers ("... if it has been more than 24 hours, and straight
# away for a puppy under six months, or if there is vomiting"). A short list is repeated whole,
# because every clause of it is a sign the answer named; a long one is cut to its first clause,
# which carries the shape of it, so the line stays one sentence rather than becoming a second copy
# of the answer. The limit is where a cut stops helping: a cat answer's "she has not drunk for 24
# hours, is straining in the tray, or is hiding and off her food" is three signs and reads as one
# clause, and cutting it told the person one sign where the answer named three.
CONDITION_CLAUSE = re.compile(r", (?:and |or |then |so )?| and | or ")


def _cut_condition(when, most=22):
    when = str(when or "").strip(" ,.")
    if len(when.split()) <= most:
        return when
    when = CONDITION_CLAUSE.split(when)[0].strip(" ,.")
    return when


def _first_sentence_end(said):
    """Where the answer's first sentence ends, so a later one can be told apart from it."""
    found = re.search(r"[.!?](?:\s|$)", str(said or ""))
    return found.end() if found else len(str(said or ""))


def _told_to_act(said, at):
    """Whether the referral at `at` is the answer telling the person to do something.

    The words a referral is made in come in two shapes. One is an instruction: "ring the vet",
    "get it looked at", and the cue itself is the verb. The other only names the appointment:
    "worth a GP visit", "a job for the vet". The second shape is how an answer writes its list
    of warning signs - "Pins and needles in the fingers that wake you is worth a GP visit" - and
    that is a pointer to a different symptom, not advice about the wrist that is "usually an
    overused tendon". So it is the declarative shape that has to be in the answer's opening to
    count, and a later one is a warning rather than a referral.
    """
    said = str(said or "")
    if not DECLARATIVE_REFERRAL.match(said, at):
        return True
    return at <= _first_sentence_end(said)


GO_FROM = ("worth a gp", "gp visit", "worth a hearing test", "a referral",
           "for a referral", "worth getting looked at", "worth seeing")


def _a_plain_go(at, said):
    """True when the care cue at `at` is a recommendation, not a warning behind a condition.

    The answer that says both halves - "It is common at four and still common at nine, but past
    ten it is less usual ... so it is worth a GP visit whatever the age" - was read as the
    ordinary kind because "common" comes first, and a twelve-year-old still wetting the bed was
    told "Nothing in that sounded like a warning sign". A "worth a GP visit" is a thing to do
    whatever the age, so it answers the ask rather than the words in front of it.
    """
    said = str(said or "").lower()
    window = said[max(0, at - 24):at + 24]
    return any(word in window for word in GO_FROM)


def _opening(said):
    """The answer's first sentence or two, where its verdict and its first instruction live.

    A word searched for anywhere finds the wrong sentence as often as the right one: the gas
    bill answer carries a "usually" about tariffs three sentences in, and reading that as the
    verdict turned "is that bad" after it into "that one is the ordinary kind, so no".
    """
    parts = re.split(r"(?<=[.!?]) ", str(said or ""))
    return " ".join(parts[:2])


# A sentence that puts its own condition in front of the clinician is a referral for that case
# and not for the person reading it now: the headache answer ends "If you get them most days,
# keep a short diary ... and take it to a pharmacist or GP". Telling someone whose head hurts
# this afternoon to ring the doctor is the false alarm STYLE rules out, so a referral lifts the
# all-clear only when at least one sentence makes it plainly, with no if, when or "most days"
# in it. The lump answer's "anything hard, painless, fixed in place, or still there after three
# weeks needs a GP" has no such word in it and does lift it.
FENCED_IN_SENTENCE = re.compile(r"\b(?:if|unless|once|when|whenever|in case|most days)\b",
                                re.IGNORECASE)


# The thing's own name is the test for whether the referral is about it: the lump answer's GP is
# "so does a lump with night sweats or weight loss", and the thing in the person's line is the
# lump. An answer that names someone to see for something else is not a referral for this: the
# poinsettia entry ends "Mistletoe and holly berries are the ones to ring the vet about", and a
# rehoming answer says a rescue "asks for the vet records" - told "ring them" over either of
# those, a person with an ordinary complaint is sent to a vet for a plant they do not have.
THING_WORDS = frozenset("""about after again also always another anything around because been
before being both came cant could does doing done down during each even ever every from
getting give going good have having here just keep keeps know last like little long made make
many more most much must need needs never next only other over really right same should since
some something still such sure than that their them then there these thing things think this
those through time today tomorrow tonight under until very want wants well went were what when
where which while will with would your yours yourself""".split())


def _the_thing(line):
    """The words in the person's own line that name what they are asking about."""
    return {word for word in re.findall(r"[a-z']{4,}", _flat(line)) if word not in THING_WORDS}


def _referral_about_the_thing(said, line):
    """True when a sentence names a clinician, plainly, about the thing the person asked about."""
    thing = _the_thing(line)
    if not thing:
        return False
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        if not NAMES_A_CLINICIAN.search(sentence):
            continue
        if FENCED_IN_SENTENCE.search(sentence):
            continue
        if thing & set(re.findall(r"[a-z']{4,}", sentence.lower())):
            return True
    return False


def _echoes_the_person(step, memory):
    """Whether the "step" is only the person's own words said back to them.

    "i want to be more organised" was met with "Be more organised - fair enough. What's stopped
    it happening so far?", and the first clause of that is the wish itself: answering "what
    should i do first" with "Be more organised, and take it from there" tells nobody anything.
    A short step whose every content word is in the line the person just wrote is that echo.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    said = ""
    for turn in reversed(turns):
        if isinstance(turn, dict) and turn.get("user"):
            said = str(turn["user"])
            break
    if not said:
        return False
    from ..memory.topics import content
    want, have = set(content(step)), set(content(said))
    if not want or len(want) > 3:
        return False
    return not (want - have)


def _kept_step(reply):
    """True when `reply` is one of the lines that says the step has not changed, else False."""
    plain = _flat(reply).strip()
    return any(re.fullmatch(_own_pattern(line), plain, re.IGNORECASE)
               for line in STEP_KEPT_LINES)


def _only_a_verdict(line):
    """Whether a line the person sent was nothing but their verdict on the news above it."""
    text = _flat(line or "").strip()
    if not text:
        return False
    try:
        from .fallback import reads_as_a_verdict
    except Exception:
        return False
    try:
        return bool(reads_as_a_verdict(text))
    except Exception:
        return False


def _the_line_just_given(memory):
    """The bot's own last line, the one the person has just read. "" when there is not one."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ""
    for turn in reversed(turns):
        if isinstance(turn, dict) and turn.get("bot"):
            return str(turn["bot"])
    return ""


def _the_answer_before_that(memory):
    """The bot's line before its last one, when the last one was only a question.

    A question the bot asked is not an answer: there is no step in it to hand over, and the answer
    the person is asking about is the one before it. "" when there is not one.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ""
    seen = 0
    for turn in reversed(turns):
        if isinstance(turn, dict) and turn.get("bot"):
            seen += 1
            if seen == 2:
                return str(turn["bot"])
    return ""


def _word_runs(text, size=5):
    words = _flat(text).split()
    return {tuple(words[at:at + size]) for at in range(max(0, len(words) - size + 1))}


def _says_it_again(line, said):
    """Whether saying `line` now would hand the person a sentence they have just read.

    A five-word run in common is the whole sentence in the cases that matter ("Keep it plain and
    separate: one new food next to one they already eat"), and it cannot be a coincidence: the
    composer builds its steps out of the answer's own words, so a run that long is the answer's
    words coming back. Anything shorter is shared phrasing and is allowed.
    """
    return bool(_word_runs(line) & _word_runs(said))


def _already_asked_for_a_step(memory):
    """Whether the person's own last line was a bare step ask too."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for turn in reversed(turns):
        if isinstance(turn, dict) and turn.get("user"):
            return bool(STEP.match(_flat(turn["user"])))
    return False


def _the_referral_sentence(said):
    """The one sentence of the answer that holds its judgement, whole."""
    text = str(said or "")
    at = _first(text.lower(), CARE)
    if at is None:
        at = 0
    start = max(text.rfind(". ", 0, at), text.rfind("? ", 0, at), text.rfind("! ", 0, at))
    return re.split(r"(?<=[.!?]) ", text[start + 1:].strip())[0]


def _the_line_is_the_threshold(stated, line):
    """Whether the person's own line names the thing the answer set as its threshold.

    "A dog that will not eat for a day is worth a call to the vet" over "my dog wont eat" is the
    answer's own yes: the threshold is what they are asking about, so handing it back as "Not yet.
    The point where it wants a person: a dog that will not eat for a day" argues with the answer.
    Two content words in common is the test, because the two are written by different people
    ("wont eat" against "will not eat") and the overlap is what a reader sees.
    """
    from ..memory.topics import content
    want, have = set(content(stated)), set(content(line))
    return len(want & have) >= 2


def _most_of_the_line(step, heard):
    """Whether the step is most of what the bot said last turn, so quoting it repeats it.

    "Long one? Give yourself half an hour doing nothing before the next thing." is a whole
    answer that is one instruction, and handing it back as the step said the person's last two
    lines over again. A clause out of a longer answer is not that: the rest of the answer was
    there, so the step adds to what they read rather than replacing it.
    """
    from ..memory.topics import content
    want, have = set(content(step)), set(content(heard))
    if not want or not have:
        return False
    return len(want & have) / len(have) >= 0.8


# A word that is both a verb and a noun of the thing ("pay", "work", "change", "test", "start")
# opens an instruction ("Pay by card at the till") and a statement ("Pay is at least the apprentice
# minimum wage"), and only the rest of the sentence says which. A finite verb straight after it
# makes it a statement about the thing, and a statement is not a step to hand over: an
# apprenticeship definition handed "Pay is at least the apprentice minimum wage and more on most
# schemes" back as the one thing to start with (@blue-hedgehog, @sky-tuna, #6152).
A_STATEMENT = re.compile(r"^(?:[a-z']+\s+)(?:is|are|was|were|has|have|had|can|cannot|will|would|"
                         r"should|takes?|gives?|means?|costs?|comes?|goes?|does|did|gets?|keeps?)\b",
                         re.I)


# A step is something a person can do this afternoon. The buffer an answer works towards is the
# end of the job, not the first move: "Build towards three to six months of essential bills as
# the buffer" is where saving gets to, and read as the first thing to do it told someone with
# nothing saved to start by having three months saved. The shape of the verb is the tell - a
# target is aimed at, a step is done - so these sentences are not steps, and the reader walks
# on to the instruction the answer did give ("Track two weeks of what actually leaves the
# account").
TARGET_SHAPE = re.compile(
    r"^(?:build|work|save|grow)\s+up\b"
    r"|^(?:build|work|save|aim|get|grow|reach)\b[^.!?]{0,24}?\b(?:towards|toward|up to)\b",
    re.I)


def _listed(said):
    """The first thing on a list the answer wrote after a colon, in the answer's own words.

    "The things that work: same wake-up time every day, no caffeine after early afternoon" has
    given a move without writing one as an instruction, and a person who asks for tips wants
    that first one, not a request to say what they have tried. Only a colon list, and only its
    first item, so nothing here reads a sentence that was not written as a list.
    """
    for sentence in re.split(r"(?<=[.!?]) ", str(said or "")):
        if CONDITIONAL_OPEN.match(sentence.strip()):
            continue
        head, colon, tail = sentence.partition(": ")
        if not colon or tail.count(",") < 2:
            # Only a colon, not a dash or a semicolon: a semicolon joins two clauses of one
            # sentence ("... that turns it round; a child who also snores, wets the bed, or is
            # tired every day is worth a word with the GP"), and its second half is a sentence
            # about the child, not a list of things to do.
            continue
        if HEAD_REFUSES.search(head) or not HELPS.search(head):
            # The words in front of the colon say whether the list is a move or a cause. "The
            # things that work: same wake-up time every day" is a list of things to do;
            # "usually it is the wake-up time rather than the bedtime: a lie-in at the weekend,
            # a nap, or coffee after two" is the opposite claim, and handing its first item back
            # would tell the person to do the thing that keeps the trouble going. So is a menu
            # ("Quick: tuna pasta in 15, a frittata in 20") - a dish is what the answer offers,
            # not the first step out of it.
            continue
        for item in re.split(r",| and ", tail):
            item = " ".join(item.strip(" .:;,-").split())
            words = item.split()
            if not 3 <= len(words) <= STEP_WORDS:
                continue
            if NEGATIVE_OPEN.match(item) or CONDITIONAL_OPEN.match(item):
                # A list can open on a thing not to do ("do not check the clock, keep the light
                # off"), and the first thing to do is the item after it.
                continue
            if DESCRIBES.search(item):
                # An item that runs into a relative clause describes something ("a child who
                # also snores", "a lamp which is too bright"), and a description is not a move.
                continue
            return item
    return None


# A boundary a long step can be cut on without breaking it: "top the pressure up to between 1
# and 1.5 bar using the filling loop" is the step, and "top the pressure up to between 1 and 1.5
# bar" is still the step. Cutting at a joining word is not: "check it again the next day if"
# says half a sentence.
# " with " and " using " are not on this list, though they read like boundaries: the phrase after
# them is what the step is done with, and a step without it is not the instruction the answer
# gave ("Run a hot 60C or 90C service wash" fixes no smell; the cleaner is the point). A step
# that cannot be cut on a clause keeps its whole clause instead, up to LONG_STEP_WORDS.
TRIM = (" because ", " so it ", " so that ", " before ", " after ",
        " until ", " if ", " when ", " rather than ")


# Read only when the step is too long even with its clause kept whole.
TRIM_INSTRUMENT = (" using ", " with ")


# How long a quoted step may be. Generous on purpose: the answer wrote it, and a complete
# instruction of fourteen words beats a fragment of four ("top the pressure up to between 1 and
# 1.5 bar" is the step, "top the pressure up" is a guess at one).
# The words that weigh one thing against another, and so say what a list is not rather than
# what to do: "Change a few things you can keep doing rather than going on a diet: ...".
CONTRAST = re.compile(r"\b(?:rather than|instead of)\b", re.I)


STEP_WORDS = 16


# A step a little over the cap is still a step when every shorter reading of it drops part of the
# instruction: "Run a hot 60C or 90C service wash with a washing-machine cleaner or a cup of
# bicarbonate of soda" is nineteen words and losing the last nine leaves nothing that works.
LONG_STEP_WORDS = 24


# A step of this many words is a sentence in its own right: "first" bolted on the end of it
# lands on the wrong word, so it gets a line that says the order in a sentence of its own.
STEP_LONG = 10


# A sentence fenced with one of these is advice for later, not a step to do now: the boiler
# answer's "if it keeps dropping, there's a leak somewhere: stop topping it up" is the half a
# person must not be told to do first.
# A clause that opens on a noun and then says what it is ("water at the front is usually the
# door seal") is the answer explaining, not telling anyone to do anything, even when its first
# word is also a verb ("water" the plants).
# The punctuation counts too: "A dry, flaky scalp is usually dandruff" opens on a verb word and
# the comma after "dry" stopped the guard, so the description was handed back as the step.
COPULA = re.compile(r"^(?:[\w,'-]+\s+){0,5}(?:is|are|was|were)\b")


# The detail an answer puts after a colon is the rest of its instruction ("turn it off and keep
# it off: do not charge it") or a statement about the thing ("cut the distance ...: most running
# knee, shin and ankle pain is too much, too soon"). Only the first belongs on a step: cutting the
# second at its own comma left "most running knee" dangling off the end of it.
DETAIL_STATEMENT = re.compile(r"\b(?:is|are|was|were)\b", re.I)


CONDITIONAL_OPEN = re.compile(r"^(?:if|unless|once|when|whenever|should|in case)\b",
                            re.IGNORECASE)


# The bot talking about the conversation is not advice. "Nice one. Let me know how it goes" is
# how a chat line keeps the talk going, and a step ask read "Let me know how it goes" out of it
# and answered "Let me know how it goes, and take it from there" - the bot's own small talk handed
# back as the first thing to do, with nobody told what to do.
ABOUT_THE_TALK = re.compile(r"\b(?:let me know|keep me posted|tell me how (?:it|that) (?:goes|went)|"
                            r"how (?:it|that) goes|say more|tell me more|fair enough|"
                            r"thanks for telling me|i'?m listening|good to know|noted)\b", re.I)


def _cut_on(head, joins):
    """The longest cut of `head` before one of these joins that is still a step, or ""."""
    best = ""
    for join in joins:
        at = head.find(join)
        while at > 0:
            cut = head[:at].strip(" ,;:-")
            cut_words = cut.split()
            if (4 <= len(cut_words) <= STEP_WORDS and cut_words[-1].lower() not in HANGING
                    and len(cut) > len(best)):
                best = cut
            at = head.find(join, at + 1)
    return best


# A negative instruction is not a move: "do not check the clock first, then work down the list I
# gave you" tells a person what to stop, not what to do. Answers put the real first move in the
# clause after it ("do not check the clock, keep the light off"), so a part is read from there.
NEGATIVE_OPEN = re.compile(r"^(?:do not|don't|dont|never)\b", re.IGNORECASE)


# The words in front of a colon decide whether what follows it is a list of things to do. Only a
# claim that the items help makes a list a move; a clause naming a cause ("it is the wake-up time
# rather than the bedtime: ...") or a heading ("Quick: ...") leaves it a description.
HELPS = re.compile(
    r"\b(?:things?|ones?|bits?|steps?|changes?|habits?|moves?|tips?|fixes|tricks|what|"
    r"everything|anything|these|those|the rest)\b[^:]{0,40}?"
    r"\b(?:works?|worked|helps?|helped|matters?|counts?|do|does|did|"
    r"worth (?:a|trying|doing|a go))\b"
    r"|\b(?:do|does|did) more than\b",
    re.IGNORECASE,
)


# A clause that says what a list is not, or that what to do depends on something else, is not a
# claim that its items are the moves: "anger shown by what a person does not say: a flat 'fine',
# a sigh" is a list of examples, and "it depends on what you want to do: for nursing" is a choice.
HEAD_REFUSES = re.compile(r"\b(?:not|n't|depends|depend|differ|if|whether|unless)\b", re.IGNORECASE)


# An item carrying one of these runs into a relative clause, so it describes a thing rather than
# naming a move ("a child who also snores", "the mug which leaks").
DESCRIBES = re.compile(r"\b(?:who|whom|whose|which|that)\b", re.IGNORECASE)


def _shorten(head, words):
    """A step of more than STEP_WORDS words, cut on a joining word, or "" if it cannot be cut."""
    if len(words) <= STEP_WORDS:
        return head
    best = _cut_on(head, TRIM)
    if best:
        return best
    # Nothing can be cut off this without losing part of the instruction, so it is the step as
    # the answer wrote it - as long as it is still a sentence somebody would say out loud.
    if len(words) <= LONG_STEP_WORDS and words[-1].lower() not in HANGING:
        return head
    # The phrase the step is done with is the last thing to give up, and a step with half of it
    # still tells the person to start somewhere ("Rinse well, never mix it").
    return _cut_on(head, TRIM_INSTRUMENT)


# A comma ends the instruction unless what follows it carries the same one on: "stop driving and
# get them changed, or you will score the discs too" is a sentence with one instruction in it.
CONTINUES = re.compile(r"^\s*(?:or|but|so|yet|nor|otherwise)\b", re.IGNORECASE)


# ...and a comma that hands the same instruction on *in order* keeps both moves: "Vacuum it
# first, then mop with a barely damp mop" is one step, and reading only its first clause lost
# the mop, which is the half of the floor answer that stops the streaks. Kept apart from
# CONTINUES because of the and/then split at the end of _first_clause: once the comma is a
# continuation, that split would cut the instruction back to its first two words
# ("Wash with warm water" out of "Wash with warm water and a drop of washing-up liquid, then
# squeegee").
ORDER_CONTINUES = re.compile(r"^\s*(?:then|after\s+that|next)\b", re.IGNORECASE)


# "Between home and there" is one frame, not two instructions: cutting at its " and " left the
# step "Ask nursery to use the same words, so the rule does not change between home", which ends
# where the comparison does not. `and` inside `between ... and ...` (and inside `both ... and
# ...`) hands the same instruction on rather than starting a new one, so the split walks past it.
FRAME_AND = re.compile(r"\b(?:between|both)\b[^,;:.!?]*\band\b", re.I)


def _cut_at_a_join(part):
    """The part up to the first " and " or " then " that is not inside a between/both frame."""
    keep_until = 0
    for frame in FRAME_AND.finditer(part):
        if frame.end() > keep_until:
            keep_until = frame.end()
    for at in re.finditer(r" and | then ", part):
        if at.start() < keep_until:
            continue
        return part[:at.start()]
    return part


def _first_clause(part, and_break=True):
    """The part of an instruction up to where it stops being one instruction.

    The break is the first comma that is followed by a new instruction ("Put the child's name and
    class in the subject, say what you have noticed"), not the first " and ": cutting at " and "
    quoted "Put the child's name", a noun phrase, and the step templates then mangled it into
    "Put the child's name, before anything else on that list." A comma that hands the same
    instruction on ("stop driving and get them changed, or you will score the discs too") is not
    a break, and with none of either the whole part is the clause.
    """
    for at in (index for index, char in enumerate(part) if char == ","):
        # ...but only for the caller that wants the whole step. The one-move quote cuts at the
        # comma and that cut is the step, so letting the order through there read "Vacuum it,
        # then dab stains with cool water" as the whole step, and a person who asked for the
        # first move was told it was "still the same move, and nothing to add to it".
        if not and_break and ORDER_CONTINUES.match(part[at + 1:]):
            continue
        if not CONTINUES.match(part[at + 1:]):
            return part[:at]
    if not and_break:
        return part
    return _cut_at_a_join(part)


# A sentence that is the bot asking something rather than telling anyone to do anything. It ends
# on a question and it opens on one, or its last clause does ("Go on, what happened?"). Ending on
# a question mark alone is not enough: "Face - ask them to smile, has one side dropped? Arms -
# can they raise both and hold them out?" is a check to run, and so is a step that quotes the
# words to use ("...: "Could I do 8-4 if I asked?""). Without this, "Do you want to tell me what
# has made it like that?" is quoted as the step and comes back to the person as
# "Do you want to tell me what has made it like that?, and take it from there."
QUESTION_FRAME = re.compile(
    r"^(?:(?:so|and|but|or|ok|okay|right|well|then|now|look|listen|go on|go ahead|come on|"
    r"tell me)\b[\s,\u2014\u2013.:;-]*)*"
    r"(?:(?:do|did|does|would|will|can|could|shall|should|have|has|are|is|was|were)\s+"
    r"(?:you|i|we|they|he|she|it|there|that|this|anyone|anybody|someone)\b"
    r"|(?:what|why|how|where|who|which|whose)\b)", re.IGNORECASE)


# The bot's question that is an offer of help: "Want a hand working out the next step?", "What
# would help most right now?", "Shall I write it out for you?". A person answering that with a
# bare ask ("what do i do") is taking the offer up, so the ask is the answer to the question and
# the question is not waiting to be handed back. It was: after "Sorry to hear that. What would
# help most right now?" a person who said "what do i do" was told "Nothing to do on my side,
# honestly", which is a refusal dressed as a reply. A yes/no question ("Do you want to tell me
# what has made it like that?") is not this: a bare ask does not answer it, and the hand-back
# written for that turn is the right reply.
# An invitation to say more is an offer too: "I'm sorry. Do you want to say what has been going
# on?" then "what do i do" is the person taking it up, and the question-back pool answered that
# with "Nothing to do on my side, honestly" - a shrug after a line that had just offered to
# listen. So the shapes that ask the person to go on belong here: who they could tell, where they
# are with it, what it is like, whether they want to say. A question about a fact ("does it
# happen at night?") is not one of these and is still handed back.
OFFER_QUESTION = re.compile(
    r"\b(?:want (?:me to|a hand|me to)|would you like|shall i|can i help|may i help|"
    r"what would help|how can i help|anything (?:else )?i can do|where would you like|"
    r"do you want to (?:say|tell|talk)|where are you with|what(?:'s| is) it like|"
    r"is there (?:anyone|someone|anybody|somebody)|want to (?:say|tell|talk))\b",
    re.IGNORECASE)


def _an_offer_is_waiting(said):
    """Whether the bot's own last question was an offer the person may be taking up."""
    text = str(said or "").strip()
    if not text.endswith("?"):
        return False
    last = re.split(r"(?<=[.!?]) ", text)[-1]
    return bool(OFFER_QUESTION.search(last))


# An invitation in front of the bot's question ("Sorry. Do you want to tell me what has made it
# like that?") is how the bot offered to listen, not what it asked, and the person has already
# been asked once: naming that ask again sends them round in a circle, so the kind hand-back is
# what they get. A question that was put plainly is a thing they can answer, and that is named.
_INVITATION = re.compile(
    r"^(?:(?:do|would|will|can|could)\s+you\s+(?:want\s+to\s+"
    r"|like\s+to\s+|care\s+to\s+|mind\s+)?"
    r"(?:tell\s+me|talk\s+(?:me\s+through|about)|say|start)\s*(?:a\s+bit\s+)?(?:more\s+)?"
    r"(?:about\s+)?)", re.I)


# "what now" is the plea after bad news rather than a request for a step: a person who says it
# has run out of ideas, and being asked the bot's own question again is a dead end, so the kind
# hand-back stands. Every other bare ask ("what should i do", "what can i do about it") names the
# doing it wants, and the question the bot just put is the concrete thing to answer.
THE_PLEA = re.compile(r"^(?:and |so )?what now$", re.I)


# A question that only offers a hand is not about the thing: "Got it. Is there anything you'd like
# a hand with?" has nothing to answer, so a bare ask after it takes the offer and asks for the
# thing itself. `_an_offer_is_waiting` above names the offers the bot writes in its own voice; this
# names the pool lines, which say "anything" and "something else" instead.
AN_OFFER = re.compile(
    r"\b(?:anything\s+(?:else\s+)?(?:you.?d|i\s+can|to\s+add)|anything\s+on\s+your\s+mind"
    r"|what\s+else|something\s+else|is\s+there\s+anything)\b", re.I)


def _after_a_comfort_line(memory):
    """Whether the bot's own last line was one of its comfort lines.

    A step asked for after a comfort line already has an owner: `step_when_low`, in the module
    that said it, answers with the first step of a bad day ("something to eat, a shower, ten
    minutes outside"). The subject of that thread is how they feel, so naming the bot's own
    question back at them ("is there one thing you can check?") is the colder reply and would
    take the turn off the module that knows what to say. The sets live with the modules that
    speak them, so they are read here rather than imported at the top of this file.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return False
    said = str(turns[-1].get("bot") or "").lower()
    if not said:
        return False
    try:
        from .fallback import COMFORT_SAID
        from ..modules import chat as _chat
        lines = tuple(COMFORT_SAID) + tuple(getattr(_chat, "FEELING_SAID", ()))
    except Exception:  # a module without the set is simply not a comfort line
        return False
    return any(line and line.lower() in said for line in lines)


# The dash a gloss hangs on, and the markers a line can open with. A dash after a marker is the
# marker's own punctuation ("Right - what made you mention it?"), so what follows it is the
# question; a dash after a question is the gloss ("What's the worry - something that has
# happened?"), so what comes before it is the question.
_A_DASH = re.compile(r"^(.*?)\s+[\u2014\u2013-]\s+(.*)$")


_AN_OPENER = re.compile(
    r"^(?:so|and|but|or|ok|okay|right|well|then|now|look|listen|go on|go ahead|come on|tell me)$",
    re.IGNORECASE)


def _the_question_asked(said):
    """The bot's own last question, as the thing the person can answer, or "" if it is too long."""
    text = str(said or "").strip()
    if not text.endswith("?"):
        return ""
    last = re.split(r"(?<=[.!?]) ", text)[-1].strip()
    if not _is_a_question(last):
        return ""
    asked = last[:-1].strip(" ,;:-")
    # A question with a gloss on the end ("What's the worry - something that has happened, or
    # something you are afraid might?") is two sentences of work for the person to answer in one
    # go, so the part in front of the dash is the question that gets asked back.
    split = _A_DASH.match(asked)
    if split:
        front = split.group(1).strip(" ,;:-")
        rest = split.group(2).strip(" ,;:-")
        if _AN_OPENER.match(front) and _is_a_question(rest + "?"):
            # A line that opens on a marker puts the dash after the marker, not after a question:
            # "Right - what made you mention it?" cut in front of the dash leaves "right", which
            # is no question at all, and it was read as one ("I can be specific if you tell me
            # this much: right? Even a line is enough"). The question is the part after the
            # marker.
            front = rest
        asked = front
    if _INVITATION.match(asked):
        return ""
    if not asked or len(asked.split()) > 14:
        return ""
    words = asked.split()
    if words[0] not in ("I", "I'm", "I've", "I'd", "I'll"):
        words[0] = words[0][:1].lower() + words[0][1:]
    return " ".join(words)


def _ends_on_a_question(said):
    """Whether the bot's own last line finished on a question put to the person."""
    text = str(said or "").strip()
    if not text.endswith("?"):
        return False
    last = re.split(r"(?<=[.!?]) ", text)[-1]
    return bool(QUESTION_FRAME.match(last) or QUESTION_FRAME.match(last.rsplit(", ", 1)[-1]))


def _is_a_question(sentence):
    """Whether this sentence of a bot line is a question put to the person."""
    text = str(sentence or "").strip()
    if not text.endswith("?"):
        return False
    if QUESTION_FRAME.match(text):
        return True
    return bool(QUESTION_FRAME.match(text.rsplit(", ", 1)[-1]))
