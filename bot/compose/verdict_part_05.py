"""Part 5 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re

from . import pick
from .verdict_part_01 import (
    CALLS_FOR, IS_A_NUMBER, _the_person_for, A_PLAN, CARE, COMPARATIVE, _a_thing_stopped,
)
from .verdict_part_02 import (
    A_PLAN_DOUBT_LINES, REFER, DECLARATIVE_REFERRAL, HANGING, IMPERATIVES, SPLIT, THEN_OPEN,
    _is_an_explanation, WHEN, NAMES_A_CLINICIAN, DANGER, NEGATED, AFTER,
)
from .verdict_part_03 import (
    _flat, _the_line_behind, _the_plan_they_brought, _words,
)
from .verdict_part_04 import (
    _sentence_at, _not_fenced, A_FREQUENCY_ASKED, A_FREQUENCY_SAID, TIME_NOW, _cut_condition,
    _the_call_sentence, _first_sentence_end, _told_to_act, A_STATEMENT, NEGATIVE_OPEN,
    ABOUT_THE_TALK, CONDITIONAL_OPEN, CONTRAST, COPULA, DETAIL_STATEMENT, STEP_WORDS, TARGET_SHAPE,
    _first_clause, _is_a_question, _shorten,
)


def _the_call_and_its_reason(said):
    """The answer's own "see a GP for X" and "X is 111 today", said as one clause, or "".

    Only for the "when should i worry" ask, which wants the answer's condition and never a
    verdict on the thing. Two at most: a card listing more than two calls has written a
    paragraph, and half of a paragraph read back is worse than the pool.
    """
    found = []
    for m in CALLS_FOR.finditer(str(said or "")):
        sign = _no_hanging_end(m.group("list").strip(" ,;:-"))
        if not 2 <= len(sign.split()) <= 20:
            continue
        found.append((m.start(), sign, _the_person_for(m.group("who"), m.group("quick"))))
    for m in IS_A_NUMBER.finditer(str(said or "")):
        sign = _no_hanging_end(m.group("when").strip(" ,;:-"))
        if not 2 <= len(sign.split()) <= 20:
            continue
        found.append((m.start(), sign, _the_person_for(m.group("who"), m.group("quick"))))
    # In the card's own order, so the first two calls it makes are the two the line carries.
    said_signs = []
    for _, sign, who in sorted(found):
        if any(sign in other for other in said_signs):
            continue
        said_signs = [s for s in said_signs if s not in sign]
        said_signs.append("%s (%s)" % (sign, who) if who else sign)
        if len(said_signs) == 2:
            break
    if not said_signs:
        return ""
    # The second sign is a second line of the card, so the two are joined with a semicolon rather
    # than an "or": "spreading redness or pus (a GP the same day); a fever or feeling shivery
    # (111 today)" keeps each sign with the call it belongs to.
    clause = "; ".join(said_signs)
    return clause[0].lower() + clause[1:] if clause[:1].isupper() else clause


def _a_plan_doubt(memory):
    """The line for a bare doubt that follows the person's own plan, or None.

    A plan is theirs, so this composer has no verdict to give and stands aside - which used to
    mean returning nothing, and the turn then landed on the acknowledgement pool: "im going to
    rome" / "is that ok", "i want to book a holiday" / "is that ok" and "we're thinking of getting
    a rescue greyhound" / "is that ok" were all answered "Alright then - good luck with it". A
    sign-off says the conversation is over, and what the person is checking is that wanting it is
    allowed. Nothing is ruled on about the plan; the ask is for the part being weighed.
    """
    said = _flat(_the_line_behind(memory))
    if not said or not A_PLAN.search(said):
        # The plan is often one line back rather than the last one: "im thinking of getting a dog"
        # / "but i work all day" / "is that fair". The detail is the person's own thought about
        # the plan, so the plan is still what the check is about.
        said = _the_plan_they_brought(memory)
    if not said:
        return None
    return pick(_round_robin(A_PLAN_DOUBT_LINES, said), memory, said)


def _behind_a_description(said, at):
    """True when the care cue at `at` is the referral a described condition hangs on.

    "Shaking that has crept on over months ... is worth a GP appointment" is the same advice for
    later that an "if" makes it, written as a relative clause instead: the care word comes after
    the condition rather than in front of it, so reading only backwards called it a verdict now.
    """
    sentence = _sentence_at(said, at)
    if len(sentence) <= len(said) - at - 1 and not sentence.endswith((".", "!", "?")):
        sentence = sentence + "."
    described = _a_described_condition(sentence)
    if not described:
        return False
    marker = None
    for found in re.finditer(r"\b(?:that|which|who)\s+", sentence, re.I):
        marker = found
    if marker is None or not sentence[:marker.start()].strip():
        return False
    cue = sentence.lower().find(said[at:at + 12].lower()) if at < len(said) else -1
    return cue > marker.start()


def _unconditional_care(said):
    """The first care cue that is not fenced off by an "if ..." or a description in front of it.

    The words a referral is made in are not all in CARE: an answer offers "get looked at" and
    "Ring your GP or a physio", and a physio, a dentist and a vet are the same kind of referral
    as a doctor. REFER is read here too, so the referral counts however it is worded.
    """
    said = str(said or "").lower()
    best = None
    for word in CARE:
        start = said.find(word)
        while start >= 0:
            # The condition can be written as a description of the thing rather than as an
            # "if": "Shaking that has crept on over months ... is worth a GP appointment" answers
            # a bare "is that bad" with the condition, not with "yes". Main's `_behind_a_description`
            # reads that same shape and is kept here rather than a second reader for it.
            if (_not_fenced(said, start, start + len(word))
                    and not _behind_a_description(said, start)):
                if best is None or start < best:
                    best = start
                break
            start = said.find(word, start + 1)
    for match in REFER.finditer(said):
        if not _not_fenced(said, match.start(), match.end()):
            continue
        if best is None or match.start() < best:
            best = match.start()
        break
    return best


def _the_fence_is_met(fence, said, memory):
    """Whether the person's own line already says the words the answer's fence is written in."""
    if not isinstance(memory, dict):
        return False
    line = (_the_line_it_answered(said, memory) or "").lower()
    if not line:
        turns = memory.get("turns") or []
        line = str((turns[-1] or {}).get("user") or "").lower() if turns else ""
    if not line:
        return False
    said = {word.rstrip("s") for word in re.findall(r"[a-z']{4,}", line)}
    for word in re.findall(r"[a-z']{4,}", str(fence or "").lower()):
        if word.rstrip("s") in said:
            return True
    return False


def _a_frequency_already_said(fence, said, memory):
    """Whether the person has already said how often it happens, so the answer's condition is met.

    `im getting headaches every afternoon` / `what should i do first` / `is that bad` is the person
    the headache card fences: "if you get them most days" is their "every afternoon" in the card's
    words. The doubt's own line says only "is that bad", so no words of the fence are in front of
    it and reading the fence as the answer's condition told them the headache was ordinary on its
    own, over their own line that it happens every afternoon. Found in review by @loyal-brush.

    Both halves are needed: the fence has to be about how often, and the person has to have said
    how often, so a chat whose answer fences on something else is untouched by a stray "every day"
    about the bins.
    """
    if not isinstance(memory, dict) or not A_FREQUENCY_ASKED.search(str(fence or "")):
        return False
    # The frequency has to be about the same thing: a chat whose "every day" is the bins going out
    # has said nothing about how often the headache comes. So the line that said how often must
    # share a word with the line the answer was answering - and when it is that line, it does.
    answered = _the_line_it_answered(said, memory)
    subject = {word.rstrip("s") for word in re.findall(r"[a-z']{4,}", answered)}
    for turn in memory.get("turns") or []:
        line = str((turn or {}).get("user") or "").lower()
        if not A_FREQUENCY_SAID.search(line):
            continue
        if not subject:
            return True
        words = {word.rstrip("s") for word in re.findall(r"[a-z']{4,}", line)}
        if words & subject:
            return True
    return False


def _condition_after_care(said, care_at, memory=None):
    """The answer's own condition, when it sits after the referral in that same sentence.

    "Get up in two stages, drink enough water, and see a doctor if you actually faint or it
    happens most times you stand" has a referral in it, so the bare "is that bad" after it was
    answered "Yes, that one wants a proper look rather than watching it" - a claim the answer
    itself had just contradicted, since the standing up is ordinary and the faint is the thing
    to watch. A referral with the answer's own "if" after it is not a verdict now: it is the
    condition the answer named, and that condition is the answer to the bare ask.
    """
    if care_at is None or care_at < 0:
        return ""
    sentence = re.split(r"(?<=[.!?]) ", str(said or "")[care_at:])[0]
    fence = re.search(r"\b(?:if|unless|once|when) \w", sentence, re.I)
    if not fence:
        # An answer whose referral is fenced in a later sentence is not a call for today either:
        # "water, a dark quiet room and paracetamol usually do more than anything you can buy ...
        # If you get them most days ... take it to a pharmacist or GP" was answered "Yes, that one
        # wants a proper look", over a card that had just said the ordinary headache settles. The
        # fence is the answer's own condition wherever it is written, so the same reading applies
        # to it - unless the answer also makes a call for now, which outranks its condition.
        if _the_call_sentence(said):
            return ""
        # The person being already past a timescale the answer set is a sharper reading than the
        # condition is: "my knee has clicked for three weeks" wants "you are already past it", not
        # "it stops being ordinary if it is no better after six weeks". That arm reads the
        # answer's hedge with the person's own span, so it keeps the turn.
        if memory is not None and _past_the_timescale(said, memory):
            return ""
        later = _when(said)
        if later and _a_frequency_already_said(later, said, memory):
            # A fence on how often is met by the person's own "every afternoon": the threshold they
            # have already described is not a thing to watch for.
            return ""
        if later and _the_fence_is_met(later, said, memory):
            # A fence the person's own line already meets is not a condition on whether to act,
            # it is a threshold they have passed: "i sweat a lot at night" against the card's
            # "if you sweat buckets from one place or at night" is a yes, and reading it as the
            # answer's condition would tell them "ordinary on its own" in the same breath as
            # naming the thing they just said they have.
            return ""
        return _cut_condition(later) if later else ""
    # A referral that names a time is not waiting on anything: "ring the vet today if it has been
    # more than 24 hours" is a yes today, and reading it as a condition would soften advice that
    # was never soft. Only a fence with no time in it is the answer's own condition.
    if TIME_NOW.search(sentence):
        return ""
    # A condition that comes after the answer has already said go is a degree of the same errand,
    # not a fence on whether to: "so ring the vet, and sooner if he is also off his food or
    # weeing in the house" is a yes, and reading its later "if" as the answer's own condition
    # told the person their dog was "ordinary on its own" over an answer that said ring the vet.
    if COMPARATIVE.search(sentence[:fence.start()]):
        return ""
    return _cut_condition(_when(said))


def _referral(said):
    """The answer's own referral, from its first sentence or from a later one that tells them to act.

    The knee answer's referral is its last sentence, and reading only the opening answered the
    knee with "that one is the ordinary kind, so no". A later sentence that only states some
    OTHER symptom is worth a visit is a warning about that symptom, not advice about this one,
    so a referral out of the first sentence has to be an instruction.
    """
    care = _unconditional_care(said)
    if care is None:
        # A referral stated rather than told: "anything hard, painless, fixed in place, or still
        # there after three weeks needs a GP" is the answer's own judgement about the thing the
        # person asked about, and the person asking "is that bad" about a lump they found is
        # asking whether theirs is that one. It carries its own fence, so it is read anywhere but
        # only when no "if" or "when" sits beside it: "see a GP if it is still there in three
        # weeks" stays a condition, not a yes.
        stated = DECLARATIVE_REFERRAL.search(str(said or ""))
        if stated is not None and _not_fenced(said, stated.start(), stated.end()):
            return stated.start()
        return None
    if care <= _first_sentence_end(said):
        return care
    return care if _told_to_act(said, care) else None


def _step(said):
    """The first thing the answer told them to do, in the answer's own words."""
    # A negative instruction is not a move: "do not check the clock first, then work down the list
    # I gave you" tells a person what to stop, and the answer's next instruction is the one to
    # hand back ("keep the wake-up time the same, and go easy on late coffee").
    found = [one for one in _steps(said) if not NEGATIVE_OPEN.match(one)]
    found = [one for one in found if not A_STATEMENT.match(one)]
    return found[0] if found else None


def _steps(said):
    """Every step the answer gave, in the answer's own words, in the order it gave them."""
    # A red flag is not a step, and a health answer ends with one: "Get one checked the same day
    # if it comes on like a thunderclap" was handed back as the thing to do today, on its own,
    # to somebody who had just been told the ordinary steps. The pattern is the one `topics` uses
    # for its own path, imported here rather than copied so the two cannot drift.
    from ..memory.topics import RED_FLAG
    found = []
    parts = []
    for at_sentence, sentence in enumerate(re.split(r"(?<=[.!?]) ", str(said or ""))):
        if (CONDITIONAL_OPEN.match(sentence.strip()) or RED_FLAG.match(sentence.strip())
                or _is_a_question(sentence) or _is_an_explanation(sentence)):
            continue
        # An answer that opens on "Then" is giving its first move, not its second: the word is
        # how the thought was put down, and no step is being continued because there is nothing
        # before it. Read as written it was not a step at all - "Then start with the smallest
        # version of it, not the whole thing" was invisible to this reader, so "what should i do
        # first" after it fell through to handing the bot's own question back ("Nothing to do on
        # my side, honestly"). Only the answer's own opening is trimmed: a "then" later in the
        # answer joins two moves, and cutting it there would hand back the second one.
        opened = THEN_OPEN.sub("", sentence.strip()) if not at_sentence else sentence
        if opened is not sentence:
            sentence = opened[:1].upper() + opened[1:]
            if not sentence:
                continue
        raw = SPLIT.split(sentence)
        kept = []
        for at, chunk in enumerate(raw):
            if at % 2 or not chunk.strip():
                continue
            kept.append((chunk.strip(), raw[at - 1] if kept else ""))
        if (len(kept) > 1 and CONTRAST.search(kept[0][0])
                and _doing_word(kept[1][0].split()) in IMPERATIVES):
            # A clause that weighs one thing against another in front of a colon is a heading for
            # the list, not the first thing to do: "Change a few things you can keep doing rather
            # than going on a diet: fill half the plate with vegetables" gave back "Change a few
            # things you can keep doing rather than going on a diet first, then work down the
            # list", where the order lands on the comparison instead of on the step. The
            # instruction is the one after the colon. A plain clause in front of a colon is not
            # dropped ("Turn it off and keep it off: do not charge it" is the first thing to do),
            # so only the contrast is the tell.
            kept = kept[1:]
        if len(kept) > 1 and _doing_word(kept[0][0].split()) not in IMPERATIVES:
            # "That's the one: split your time in three", "Cheapest fix: bleed the radiators":
            # the piece in front of the colon is the answer naming its own line, not the
            # instruction, and it is dropped the same way.
            kept = kept[1:]
        if len(kept) > 1 and all(sep == ": " for _, sep in kept[1:]):
            # The colon is the answer explaining its own instruction, and the explanation is the
            # part a friend would say ("turn it off and keep it off: do not charge it"), so the
            # instruction is read whole with the explanation still on it. The pieces stay on the
            # list as well, because a later ask wants the one after the first. A dash is not an
            # explanation ("keep the room cool and dark - get up" says two things), so it is left
            # as it is written.
            parts.append((": ".join(text for text, _ in kept), True))
        parts.extend((text, False) for text, _ in kept)
    for part, spread in parts:
        if RED_FLAG.match(part):
            continue
        part = re.sub(r"\([^)]*\)|\S*\.(?:com|co\.uk|org|net|gov)\S*", " ", part)
        part = " ".join(part.strip(" .:;,-").split())
        if not part:
            continue
        words = part.split()
        if _doing_word(words) not in IMPERATIVES or COPULA.match(part):
            continue
        if TARGET_SHAPE.match(part):
            continue
        if ABOUT_THE_TALK.search(part):
            continue
        # The first clause, but "and" between two numbers is a range and not a new clause
        # ("top the pressure up to between 1 and 1.5 bar" keeps its second half that way).
        protected = re.sub(r"(?<=\d) and (?=[\d.])", " \x00 ", part)
        if spread:
            # The instruction the answer opened with and the detail it gave for it are one move:
            # "Find what starts it and block that first: a curtain over the window he watches" is
            # the step, and cutting it at its own " and " left "Find what starts it", half an
            # instruction, with the half that says how to do it thrown away.
            opening, _, detail = protected.partition(": ")
            opening = _first_clause(opening, and_break=False).replace("\x00", "and")
            opening = opening.strip(" .:;,-")
            detail = detail.replace("\x00", "and").strip(" .:;,-")
            if DETAIL_STATEMENT.search(detail):
                # "Cut the distance and the speed for a week or two: most running knee, shin and
                # ankle pain is too much, too soon" - the colon hands on a statement about the
                # thing rather than the rest of the instruction, and cutting it at its own comma
                # left "most running knee" dangling off the step. The step is the instruction
                # before the colon; the explanation is not something to tell anybody to do.
                detail = ""
            else:
                detail = _first_clause(detail).strip(" .:;,-")
            head = "%s: %s" % (opening, detail) if detail else opening
            if len(head.split()) > STEP_WORDS and "," in detail:
                detail = detail.split(",")[0].strip(" .:;,-")
                head = "%s: %s" % (opening, detail) if detail else opening
            if len(head.split()) > STEP_WORDS:
                # Longer than a step anybody says out loud: the instruction on its own is the
                # step, and the explanation is left behind rather than cut in half.
                head = _shorten(opening, opening.split()) or opening
        else:
            clause = _first_clause(protected).replace("\x00", "and").strip(" .:;,-")
            head = _shorten(clause, clause.split()) if len(clause.split()) >= 3 else ""
            if not head:
                # A first clause too short to quote ("Blot") is no reason to quote the whole part
                # with its own order still in it: "Blot, don't rub, with kitchen paper, then dab"
                # arrived as "Blot, don't rub, with kitchen paper, then dab", the order said twice
                # and the last item left hanging without its verb. Cutting at the answer's own
                # "then" keeps the one step it wrote.
                trimmed = re.split(r",? then ", part)[0]
                head = _shorten(trimmed, trimmed.split()) if len(trimmed.split()) >= 2 else ""
            if not head:
                head = _shorten(part, words)
        if not head:
            # The answer's next instruction could not be quoted whole. Walking on past it quotes
            # the conditional half instead ("stop topping it up first"), so the list stops here -
            # but a step found before it stands: "Turn it off and keep it off" was read cleanly
            # and "wipe it, shake out the port gently and leave it somewhere warm and airy for at
            # least 24 hours" was not, and returning nothing threw the good first move away.
            return found
        words = head.split()
        if not words or words[-1] in HANGING or head in found:
            continue
        # The verb of a sentence is capitalised and the list is not: "Ask once, plainly ..."
        # is the same instruction as "ask once", and reading it case-sensitively threw away
        # every answer that opens with its step instead of burying it after a colon. The verb
        # is the first word that is not one of the when words in front of it, so "three times
        # a week do sit-to-stands" still counts.
        if _doing_word(words) not in IMPERATIVES:
            continue
        found.append(head)
    return found


def _doing_word(words):
    """The first word that is not one of the when words in front of a step."""
    # A part that opens on an article is a noun phrase saying what the thing is ("A dry mouth
    # usually means mouth breathing"), not an instruction, however verb-shaped the word after
    # the article looks. Nobody writes a step as "a ...".
    if words and words[0].strip("*_`(\"'[]").lower() in ("a", "an", "the"):
        return ""
    for index, word in enumerate(words[:5]):
        core = word.strip(",;:-\u2014\u2013").lower()
        if core in WHEN:
            continue
        return core
    return ""


def _action_count(said):
    """How many things the answer told them to do, so a "list" is only promised when there is
    one. A clause counts when it opens with a verb, which is how the answers write a step
    ("put a bowl under it", "ease off hills", "take paracetamol")."""
    # A question is not one of the things the answer told them to do, so it does not make the
    # answer a "list" ("Sorry. Do you want to tell me what has made it like that?").
    said = " ".join(s for s in re.split(r"(?<=[.!?]) ", str(said or ""))
                    if not _is_a_question(s))
    total = 0
    for part in re.split(",| and | then |\\. |; |: | - | — | – ", said):
        words = part.strip(" .:;,-()").split()
        if words and _doing_word(words) in IMPERATIVES:
            total += 1
    return total


def _no_hanging_end(when):
    """The condition with any trailing join, comma or half-list taken off its end."""
    text = str(when or "").strip(" ,;:")
    while True:
        shorter = re.sub(r"(?:^|[ ,]+)(?:and|or|but|then|so|also|plus)$", "", text).strip(" ,;:")
        if shorter == text or not shorter:
            break
        text = shorter
    return text


# A red flag is written as a description as often as it is written with an "if": "Shaking that
# has crept on over months, is much worse on one side, or comes with a slow walk or stiff arm is
# worth a GP appointment". There is no "if" anywhere in that sentence, so `_when` found nothing,
# and a bare "is that bad" on top of it was "Alright then - good luck with it". The relative
# clause is what the answer puts the referral on, so it is the answer's condition in exactly the
# way an "if" is. The verbs are the ones a red flag is written with, so a description that is not
# a condition ("the noise that it makes is normal, but see a plumber") is not read as one.
CONDITION_VERBS = frozenset((
    "comes", "come", "gets", "get", "turns", "turned", "starts", "started", "goes", "went",
    "spreads", "spread", "wakes", "woke", "lasts", "lasted", "keeps", "kept", "has", "have",
    "develops", "developed", "bleeds", "bled", "swells", "swelled", "is", "are", "was", "were",
    "hurts", "stops", "stopped", "changes", "changed", "moves", "moved", "suddenly",
))


# A described condition that ends on one of these was cut in the wrong place: those words are
# the subject of the half-sentence that is left, not the end of a condition ("... is true, or
# you").
CONDITION_HANGING = frozenset("""
you i he she we they it or and but so if when with of the a an is are was were been t
""".split())


# The verb the referral itself is made of ("... passing water is a GP matter"): the condition
# ends where that verb begins. A verb in the middle of a list is part of the condition, not the
# end of it - "has crept on over months, is much worse on one side" - so the cut is the last one
# whose remainder is short and free of commas ("worth a", "a", "looking at today:"). When no verb
# qualifies, the clause cannot be separated safely ("a finger that ... behind a ring needs the
# ring cut off, so go to A&E") and nothing is handed back.
REFER_VERB = re.compile(
    r"\b(?:is|are|was|were|needs|needed|means|wants|should|must|will\s+need)\b", re.I)


# A tail that restates the referral in the answer's own words is not part of the condition, and
# handing it back reads as a second sentence bolted on: "if you sweat buckets from one place or
# at night, that is worth a GP visit, so that is what to watch".
RESTATED = re.compile(r",\s*(?:that|this|which|it)\s+(?:is|means|needs|wants|should)\b", re.I)


# The words a referral is hung on when the answer writes its condition as a description instead of
# an "if": "Shaking that has crept on over months ... is worth a GP appointment".
RELATIVE = re.compile(r"\b(?:that|which|who)\s+", re.I)


def _described_clause(sentence):
    """The condition a sentence writes as a description: (from, to, its words), or None.

    "Shaking that has crept on over months, is much worse on one side ... is worth a GP
    appointment" hangs its referral on the clause that follows "that", and so does "one that is
    also dull or sick needs to be seen today". Where the clause sits is what tells a referral
    inside it from one beside it: the dog answer has "worth a call to the vet" flat, and a
    condition next to it, and only the second is a warning for later.
    """
    referral = REFER.search(sentence)
    if referral is None:
        return None
    head = sentence[:referral.start()]
    marker = None
    for found in RELATIVE.finditer(head):
        marker = found
    # "That is a vet visit rather than a brushing one" opens on a demonstrative, not on a
    # relative clause: there is no subject in front of it to describe.
    if marker is None or not head[:marker.start()].strip():
        return None
    start = marker.end()
    clause = head[start:]
    cut = None
    for found in REFER_VERB.finditer(clause):
        rest = clause[found.end():].strip(" ,")
        if len(rest.split()) <= 4 and "," not in rest:
            cut = found.start()
    if cut is None:
        return None
    words = clause[:cut].strip(" ,;:-").split()
    if not 2 <= len(words) <= 26:
        return None
    if words[-1].strip(",;:").lower() in CONDITION_HANGING:
        return None
    if words[0].strip(",;:").lower() not in CONDITION_VERBS:
        return None
    # The clause runs to where the referral itself begins: "worth a GP appointment" is the
    # answer's referral, and the cue inside it belongs to the condition rather than beside it.
    return start, referral.start(), " ".join(words)


def _in_a_described_clause(sentence, at):
    """True when position `at` in the sentence is inside the condition it describes."""
    found = _described_clause(sentence)
    return found is not None and found[0] <= at < found[1]


def _a_described_condition(sentence):
    """The relative clause a sentence hangs its referral on, or "" when it hangs on an "if"."""
    found = _described_clause(sentence)
    if found is None:
        return ""
    # Said as the answer's subject rather than as a thing that happens to it: the answer is about
    # "shaking", the condition is about "it", and repeating the subject back ("...if shaking has
    # crept on over months") reads as a definition rather than as a warning.
    return "it " + found[2]


def _an_if_that_is_a_condition(sentence):
    """Where the sentence's " if " puts a condition on the referral, or -1.

    "do not wait to see if it passes" is a test the person runs, not a condition for care, and
    reading it as one took the verdict off the pale-gums answer: "Ring the vet now and go in
    today ... do not wait to see if it passes" came back as "Ordinary on its own, yes. It stops
    being ordinary if it passes" - an all-clear over an answer that opens "Pale, white or blue
    gums are an emergency" (main answers it with the yes pool, and this keeps that). The word in
    front of the "if" is what tells the two apart.
    """
    start = 0
    while True:
        at = sentence.find(" if ", start)
        if at < 0:
            return -1
        before = re.findall(r"[a-z']+", sentence[:at].lower())
        if not before or before[-1] not in LOOK_AND_SEE:
            return at
        start = at + 4


# The verbs that make the "if" after them a test rather than a condition: "see if it passes",
# "check if the noise stops", "know if it is broken".
LOOK_AND_SEE = frozenset((
    "see", "check", "know", "wait", "tell", "find", "wonder", "decide", "guess", "ask",
    "notice",
))


def _a_judgement_fence(said):
    """The condition a closing, declarative referral puts on itself, or "".

    Only the last sentence is read, and only when it names a clinician and carries a list in
    front of the referral ("Anything hard, painless, fixed in place, or still there after three
    weeks needs a GP"). Narrow on purpose: `REFER` and `_when` are left exactly as they are, so
    no step or how-to answer changes.
    """
    sentences = [s for s in re.split(r"(?<=[.!?]) ", said.strip()) if s.strip()]
    if not sentences:
        return ""
    last = sentences[-1]
    if NAMES_A_CLINICIAN.search(last) is None:
        return ""
    found = re.search(r"(?i)\b(?:anything|any [a-z-]+)\b(.*?)\b(?:needs?|should be|is worth|wants)\b",
                      last)
    if found is None:
        return ""
    clause = found.group(1).strip(" ,;:-")
    if "," not in clause and " or " not in clause:
        return ""
    words = clause.split()
    if not 2 <= len(words) <= 26:
        return ""
    return clause


def _after_the_if(sentence):
    """The condition a sentence writes after its "if", cut where the answer asks something."""
    opens = re.match(r"(?:so )?if ", sentence, re.I)
    if opens:
        # "If the noise comes with pain or swelling, treat it as pain: ..." opens on its
        # condition, so the sentence carries the "if" without a space in front of it. The
        # condition runs to where the answer starts telling them to do something, not to the
        # first comma: "If it locks out twice, or you smell gas, stop and call ..." has two
        # conditions in it, and cutting at the comma kept the milder half.
        when = sentence[opens.end():]
        when = re.split(r"(?:^|, |; | and | then | so )(?:and )?(?:get|see|ring|call|take|go|"
                        r"book|treat|watch|keep|check|apply|cover|use|rest|ice|put|give|try|"
                        r"test|monitor|stop|unplug|switch|leave|turn|have|ask|phone|contact|"
                        r"speak|mention)\b", when)[0]
    else:
        at = sentence.find(" if ")
        if at < 0:
            return ""
        when = sentence[at + 4:].rstrip(" .")
        # The condition ends where the answer starts telling them to do something else. The
        # doing word has to begin a clause: "or you cannot put your weight on it" is the
        # condition itself, and cutting at "put" left "or you cannot".
        when = re.split(r"(?:^|, | and | then )(?:and )?(?:get|see|ring|call|take|go|book|"
                        r"treat|watch|keep|check|apply|cover|use|rest|ice|put|give|try|test|"
                        r"monitor|have|ask|phone|contact|speak|mention)\b", when)[0]
    # The cut lands mid-sentence whenever the answer joins its referral with a conjunction
    # ("... or the pain came on after a fall, and see a GP if it is no better"), and half a
    # sentence is worse than none: "See someone if ... a fall, and." A list that ends on a
    # joining word is still going somewhere, so drop it and the comma in front of it.
    when = RESTATED.split(when)[0]
    when = _no_hanging_end(when.strip(" ,."))
    return when if len(when.split()) >= 2 else ""


def _when(said):
    """The condition the answer itself put on getting someone in."""
    for sentence in re.split(r"(?<=[.!?]) ", said):
        if not REFER.search(sentence):
            continue
        opens = re.match(r"(?:so )?if ", sentence, re.I)
        # A sentence's " if " is a condition on the referral, or it is a test the person is told
        # to run ("do not wait to see if it passes"). Both cases keep the reader below; only the
        # second one is not a condition at all.
        if opens or _an_if_that_is_a_condition(sentence) >= 0:
            when = _after_the_if(sentence)
            if when:
                return when
            continue
        # The same condition written as a description instead: "Back pain that comes with
        # numbness, weakness or trouble passing water is a GP matter."
        when = _a_described_condition(sentence)
        if when:
            return when
    return ""


# A referral the answer states as its own judgement rather than as an instruction. REFER reads
# only the imperative ("see your GP"), and that is deliberate: read as an instruction, "Pins and
# needles in the fingers that wake you is worth a GP visit" annotated a wrist that is "usually an
# overused tendon" with "yes, that one wants a proper look". So `_when` finds no condition in the
# judgement shapes, and a person who asked "should i see someone" straight after one got the
# composer's own punt instead - "i have a sore throat" / "should i see someone" was answered
# "Can't call that one for you, sorry" over an answer that had already said "Worth a doctor if it
# is one-sided and bad, or if your voice has gone for more than a couple of weeks".
# DECLARATIVE_REFERRAL holds the "worth a GP" shapes; these are the two other ways the same
# judgement gets written.
JUDGED_REFERRAL = re.compile(
    r"\b(?:is|are|was|were) (?:a|the|your) reason to (?:ring|call|see|ask|contact|speak|get)\b"
    r"|\btake (?:it|that|this|them|him|her) (?:to|along to|back to) (?:a |your |the )?"
    r"(?:pharmacist|gp|doctor|nurse|vet|dentist|optician)\b",
    re.I,
)


# "Three or more in a year is worth a GP review", "A reading of 140/90 or higher, seen twice at
# home, is high and worth a GP check": the threshold is the subject and the referral is the
# answer's judgement on it.
STATES_A_REFERRAL = re.compile(
    r"^(?P<when>.+?)\s+(?:is|are)\s+(?:high and |low and |still )?"
    r"(?:worth|a reason to|the point (?:at which|where))\b",
    re.I,
)


# A subject that names nothing is the thing again rather than a threshold: "It is worth a GP
# visit if ..." and "Either of those is worth a call" have already said what they have to say.
NAMES_NOTHING = frozenset((
    "it", "that", "this", "they", "there", "which", "either", "one", "both", "any", "all",
    "any of that", "any of those", "any of them", "either of those", "either of them",
    "one of those", "both of those", "some of that", "all of that", "the rest", "one or both",
    "none of that", "anything", "something", "much", "most of it",
))


# A threshold is a short thing; a subject this long has become the paragraph again.
STATED_LONGEST = 16


def _stated_before_the_judgement(sentence):
    """The thing a sentence puts in front of its judgement ("blood in it is worth a GP's time")."""
    frame = STATES_A_REFERRAL.match(sentence)
    if frame is None:
        return ""
    when = _no_hanging_end(frame.group("when").strip(" ,;:"))
    if not 2 <= len(when.split()) <= STATED_LONGEST:
        return ""
    if when.strip(" .,").lower() in NAMES_NOTHING:
        return ""
    # A referral that is itself the subject ("A vet visit is worth it too - pain, a bad ear or
    # failing eyesight is often behind a first bite") says nothing about when, and "only reflux,
    # coughing or trouble feeding is worth a call" names the thing that is *not* worth it.
    if NAMES_A_CLINICIAN.search(when) or when.split()[0].lower() in ("only", "just"):
        return ""
    # The subject opens the sentence and these lines put it after a colon or a word, so a capital
    # there was only ever the capital of the sentence's first word.
    head = when.split()[0]
    if head[:1].isupper() and (head[1:].islower() or len(head) == 1) \
            and head.lower() not in ("i", "a&e", "nhs"):
        when = when[0].lower() + when[1:]
    return when


def _stated_referral(said):
    """The threshold the answer stated as its own judgement, and how it is written.

    The kind matters because the two cannot be phrased alike: a clause reads after an "if"
    ("...if it is one-sided and bad") and a thing does not ("if three weeks of it" is clipped),
    so a noun is named as the thing that changes the answer instead.
    """
    for sentence in re.split(r"(?<=[.!?]) ", said):
        if not (JUDGED_REFERRAL.search(sentence) or DECLARATIVE_REFERRAL.search(sentence)
                or REFER.search(sentence)):
            continue
        opens = re.match(r"(?:so )?if ", sentence, re.I)
        if opens or " if " in sentence:
            when = _after_the_if(sentence)
            if when:
                # The lines read the clause on the back of their own "if" or "unless", so a
                # second one in the middle of it doubles the word: "Not yet, unless it is
                # one-sided and bad, or if your voice has gone".
                when = re.sub(r"\b(or|and) if\b", r"\1", when)
                # A dash in the middle of one starts the aside that follows it ("... worth a GP
                # look only if it is painful, growing fast or stops you using the hand - they can
                # drain it, but a lot come back"), and the aside is not part of the threshold.
                when = _no_hanging_end(re.split(r"\s+-\s+|\s+--\s+", when)[0].strip(" ,.;:"))
                # "... it is this hard to wake most days, ask the GP about sleep apnoea" carries
                # the appointment after the threshold: "ask" is not one of the doing words the
                # cut above ends a condition at, and half a sentence bolted onto the back of the
                # line is the noise these lines exist to avoid.
                when = when.split(", ask ")[0].strip(" ,.;:")
                if len(when.split()) >= 2:
                    return when, "clause"
            continue
        when = _stated_before_the_judgement(sentence)
        if when:
            return when, "noun"
    return "", ""


# The verbs an answer uses when the point of it is a job to do. `_step` holds the ones a first
# move is made of, in the shape a person can be told back ("Bleed the radiator"); this is the
# wider list, only ever used to answer whether an answer is a how-to at all, so a long one can
# still count ("Cool the room before you get in, not after").
DOING = IMPERATIVES | frozenset((
    "run", "cool", "warm", "heat", "wipe", "spray", "scrape", "sand", "drain", "vacuum",
    "replace", "tighten", "loosen", "unscrew", "test", "brush", "scrub", "soak", "fill",
    "pour", "freeze", "thaw", "reheat", "serve", "add", "mix", "stir", "grate", "slice",
    "chop", "cover", "wrap", "store", "label", "weigh", "measure", "book", "text", "email",
    "write", "plant", "water", "prune", "feed", "repot", "keep", "hang", "place", "swap",
    "switch", "fit", "fix", "seal", "paint", "install", "bleed", "balance", "ventilate",
    "insulate", "lag", "defrost", "descale", "replace", "trim", "sweep", "mop", "hoover",
    # What a person does about the thing as often as the tools do: "if you are hungry in the
    # morning, eat something with protein and fibre" is the answer's job, and without "eat" the
    # skipping-breakfast answer read as an answer with nothing in it.
    "eat", "drink", "sleep", "nap", "walk", "stretch", "rest", "sit", "stand", "try",
))


def _danger(said):
    """The first harm the answer names that is not itself denied ("not dangerous").

    A harm named inside an "if" is the answer's warning for later, not its verdict now: "My arm
    aches" ends "treat a heavy left arm with tightness in the chest, sweating or breathlessness
    as an emergency", and that answer is not an answer that says the ache is an emergency.
    """
    best = None
    for word in DANGER:
        start = said.find(word)
        while start >= 0:
            before = said[max(0, start - 14):start]
            sentence = said[max(0, said.rfind(". ", 0, start)):start]
            condition = re.search(r"\b(?:if|unless|when|once)\b", sentence)
            if not NEGATED.search(before) and not condition:
                if best is None or start < best:
                    best = start
                break
            start = said.find(word, start + len(word))
    return best


def _a_how_to(said):
    """True when the point of the answer is a job to do, in any of its sentences."""
    # A step can open on "so" or follow a semicolon, and both are the answer telling somebody to
    # do something: "She is bringing food to the household rather than being naughty, so take the
    # bird away in gloves". Reading only the comma and "and" heads missed every step written that
    # way, and the answer came back as "I don't know enough to answer that honestly".
    for part in AFTER.split(said)[1:] + re.split(r"(?<=[.!?]) ", said):
        # Any clause of the sentence can be the doing, not only the first: "she is bringing food
        # to the household rather than being naughty, so take the bird away in gloves" is an
        # answer that tells somebody what to do, and reading only the head of the sentence made
        # it look like an answer with nothing in it.
        for clause in re.split(r",|;| and | then | so | but ", part.strip()):
            words = clause.strip(" .:;,-").split()
            if words and words[0].lower() in DOING:
                return True
    return False


def _round_robin(pool, said):
    """The same pool, rotated by a positional hash of the answer.

    `pick` seeds on the sum of the characters, and two long answers collide on that easily: the
    damp, the rice and the radiator are all ordinary healthy sentences, and the sum landed on
    the same line for all three, so three rows of the deck got one sentence word for word. A
    rotation weighted by where the letters sit in the answer spreads them; `pick` still decides
    which of the rotated pool is said, so the no-repeat rules keep working.
    """
    if not pool or not said:
        return pool
    start = sum((i + 1) * ord(c) for i, c in enumerate(said)) % len(pool)
    return tuple(pool[start:]) + tuple(pool[:start])


def _says_what_it_is(said):
    """True when some clause of the answer tells the person something rather than telling them
    to do something.

    "Half fill the kettle with equal parts water and white vinegar, boil it and leave it half an
    hour" is a recipe and nothing else: it answers how to clean a kettle, not whether limescale
    matters, so "is that bad" after it is still the person's own question and the composer has
    nothing to say about it. An answer that explains the thing first - "she is bringing food to
    the household rather than being naughty, so take the bird away" - has said something, and
    that reading is the verdict.
    """
    for part in AFTER.split(said)[1:] + re.split(r"(?<=[.!?]) ", said):
        for clause in re.split(r",|;| and | then | so | but |:", part.strip()):
            words = clause.strip(" .:;,-").split()
            # "Half fill the kettle ..." is an instruction with a qualifier in front of the verb,
            # so the verb can be the second word as well as the first.
            leads = [word.lower() for word in words[:2]]
            if len(words) >= 4 and not any(word in DOING for word in leads):
                return True
    return False


# A long stretch the person's own line says the thing has been going on: "for months", "six
# months now", "years". It is compared with the span the answer set on watching the thing, so a
# complaint older than the answer's own threshold is not called ordinary.
LONG_SPAN = re.compile(
    # "three weeks", "ten days", "5 weeks": the timescale said as a count of days or weeks, which
    # is the same timescale an answer sets with "if it's still the same in a week or two". The
    # count used to be read for months and years only, so a person who had already waited three
    # weeks was still told to watch it for a week or two.
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:days?|weeks?|fortnights?)\b|"
    r"\ba\s+fortnight\b|"
    r"\b\d+\s*(?:months|years)\b|\bmonths?\b|\byears?\b|\bfor\s+(?:a\s+long|ages)\b",
    re.I)


# The span an answer sets on watching it: "if it's still the same in a week or two", "you wake
# drenched for weeks", "if it has not shifted in a few days". Only days and weeks: an answer that
# already allows months is not shorter than what the person has had.
HEDGE_SPAN = re.compile(
    # "in a week", "in a fortnight", "within a fortnight": the article is how English sets almost
    # every threshold, and it was not in the list of counts, so the commonest hedge of all - "if
    # it's still the same in a week or two" - was read as no timescale at all.
    r"\b(?:in|for|after|within)\s+"
    r"(?:a few|a couple of|a|an|one|two|three|four|five|six|several|\d+)?\s*"
    r"(?:days?|weeks?|fortnights?)(?:\s+or\s+(?:two|three|four))?\b|"
    # "three weeks of it is a reason to ring the surgery or 111": the same timescale said as a
    # count of the thing itself rather than after "in" or "for".
    r"\b(?:two|three|four|five|six|seven|\d+)\s+(?:days?|weeks?)\s+of\s+(?:it|this|that)\b|"
    # "See a GP if it lasts more than three weeks": the threshold with no "in" or "for" in it,
    # which is how most cards write the point to come back. The cough card says exactly this, and
    # read as no timescale at all it told somebody who had coughed for months to watch for three
    # weeks first.
    r"\b(?:lasts?|lasted|lasting|continues?|continued|continuing|goes? on|gone on|drags? on|"
    r"more than|longer than|over|beyond|past)\s+"
    r"(?:a|an|one|two|three|four|five|six|seven|several|\d+)?\s*"
    r"(?:days?|weeks?|fortnights?|months?)\b",
    re.I)


def _the_line_it_answered(said, memory):
    """The person's own line that the answer in `said` was answering.

    Not the last line they typed: the line that prompted a bare "is that bad" is the one before
    it, and that is the line whose span says how long the thing has been going on.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not said:
        return ""
    for last in reversed(turns):
        if not isinstance(last, dict):
            continue
        # Both sides flattened: the answer is read back with its own capitals ("Run a hot 60C
        # service wash"), so a comparison against the raw text never matched and the line the
        # person wrote was never found - the timescale and the fence both stood down silently.
        if _flat(last.get("bot")) == _flat(said):
            return _flat(last.get("user"))
    return ""


def _past_the_timescale(said, memory):
    """True when the answer set a timescale on watching it and the person is already past it.

    Read only where the answer hedged on time and the person's own line says the thing has been
    going on longer: "i wake up soaked in sweat every night for months" is not answered by
    "Not the thing itself, no - what would change it is you wake drenched for weeks", because
    the answer's own threshold is already met. A line with no span ("i wake up soaked") keeps
    the ordinary reading: there the answer is telling them the timescale to watch.
    """
    if not said or HEDGE_SPAN.search(said) is None:
        return False
    line = _the_line_it_answered(said, memory) or ""
    if LONG_SPAN.search(line) is None:
        # The answer answered the how-to line, and the span is one line further up.
        line = _the_span_further_up(said, memory) or line
    ours = LONG_SPAN.search(line)
    # "three weeks ago" is behind the person, not in front of them: that is not a span they have
    # waited out.
    if ours is not None and re.search(r"\b(?:days?|weeks?)\s+ago\b", line, re.I):
        ours = None
    return ours is not None


def _subject_words(text):
    """The long words of a line, cut to five letters: "coughs" and "cough" are the same subject."""
    return {word[:5] for word in _words(text)
            if len(word) >= 5 and word not in FENCE_FILLER}


def _the_span_further_up(said, memory):
    """A span further up the chat, on the same subject as the answer in front of the doubt.

    The span and the doubt are rarely in the same line: "i have had a cough for months" / "what
    should i do first" / "is that bad" is one chat, and the answer that hedged on three weeks
    answered the middle line, which says nothing about how long. Read on its own, that line has no
    span, so the fence said "not yet - three weeks of it is the point where it wants a person" to
    somebody who is already at months.

    The subject is what keeps it honest: an earlier line counts only when the answer that answered
    it and the answer in front of us are about the same thing, so a "for months" about the rent
    cannot decide a cough. Getting this wrong errs one way - no span means the ordinary reading,
    which is what the chat had before - so where the span comes from is read generously.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or len(turns) < 2:
        return ""
    here = _subject_words(said)
    if not here:
        return ""
    for turn in reversed(turns[:-1]):
        if not isinstance(turn, dict):
            continue
        line = _flat(turn.get("user"))
        if LONG_SPAN.search(line) is None:
            continue
        if _subject_words(turn.get("bot")) & here:
            return line
    return ""


# The words a condition hangs its meaning on, kept out of the comparison below. Articles,
# pronouns and the little verbs a condition is built with carry no subject of their own: "it
# stops" says nothing about what stopped, and "feeding" does.
FENCE_FILLER = frozenset("""
a an the it its this that these those there is are was were be been being am i you your he she
they we my mine our their his her them us of to in on at for with and or but so then than if
when while as by from up out off down not no any more very still just also both either own same
other thing things way lot lots bit does do did done gets get getting goes going come comes
coming keep keeps kept start starts started stop stops stopped carry carries carried turn turns
turned become becomes became make makes made up
""".split())


def _stems(text):
    """The content words of a line, stemmed, so "feeding" and "feeds" are the same word."""
    words = set()
    for word in re.findall(r"[a-z']+", _flat(text).lower()):
        word = word.strip("'")
        if len(word) < 4 or word in FENCE_FILLER:
            continue
        for suffix in ("ing", "ed", "es", "s"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[: -len(suffix)]
                break
        words.add(word)
    return words


def _the_fence_is_their_own_line(said, memory):
    """True when the answer's condition is the very thing the person just told us.

    Read from the answer's own words against the person's own words, not from the topic: when
    half the condition's content words are theirs, the condition describes what they said, and
    quoting it back to them decides nothing. "i sweat a lot at night" / "is that bad" got "It
    stops being ordinary if you sweat buckets from one place or at night": the answer's own "if"
    is already true of the line in front of it, so the reassurance in front of it is wrong.
    """
    when = _when(said)
    if not when:
        return False
    fence = _stems(when)
    theirs = _stems(_the_line_it_answered(said, memory))
    if not fence or not theirs:
        return False
    shared = fence & theirs
    return bool(shared) and len(shared) * 2 >= len(fence)


# A death is not a symptom to ask about, nor a thing to rule ordinary. "i had a miscarriage" /
# "is that bad" was answered "Say a bit more: how long has it been like that, and what does it
# cost you day to day?", which is the coldest line in this file over a bereavement.
LOSS_WORDS = re.compile(
    r"\b(?:died|dies|death|dead|funeral|cremation|burial|passed away|miscarriage|miscarried"
    r"|stillborn|bereave\w*|lost (?:the|my) baby|took (?:his|her|their) own life)\b", re.I)


# A mood is not a thing to put right, and "nothing in that answer needs anyone yet" over a low
# line rules on a feeling the composer read as a fault to fix: "i cant be bothered to leave the
# house" / "is that bad" was told "Nothing in that answer needs anyone yet - it is the standard
# way to handle it", which is the reassurance a low line least wants. The backstop's line asks
# how long and what it costs, which is the question a friend asks.
MOOD = re.compile(
    r"\b(?:feel(?:ing|s|t)?\s+(?:\w+\s+){0,2}(?:low|down|flat|numb|sad|anxious|worried|stressed"
    r"|overwhelmed|lonely|rubbish|awful|miserable|hopeless|empty|knackered|exhausted)"
    r"|depress\w*|anxi\w*|panick?\w*|miserable|lonely|burnt out|burned out|burnout"
    r"|can(?:'t|t|not)? be bothered|no energy|no motivation|dont want to go out"
    r"|dont want to see anyone)\b", re.I)


def _a_mood(memory):
    """True when the line the ask follows is about how the person feels rather than a body."""
    return any(MOOD.search(line) for line in _the_last_person_lines(memory, 2))


def _about_a_death(memory):
    """True when one of the last few lines is a death or a miscarriage.

    The death word alone is not enough: a laptop, a battery and a boiler "die" too, and "dead"
    is as often the intensifier ("dead comfy", "dead quiet", "dead tired"). Read that way a
    fault got the condolence: "my laptop battery dies fast" / "is it safe" was answered "That is
    not a thing to call bad, and not a thing to carry on your own", which is the coldest line in
    this file over a flat battery. The thing the word is about decides, and `compose/loss.py` is
    where that reading lives - it is already the reader that tells a phone that stopped from a
    father who died.
    """
    for line in _the_last_person_lines(memory, 3):
        if not LOSS_WORDS.search(line):
            continue
        if _a_thing_stopped is not None and _a_thing_stopped(line):
            continue
        return True
    return False


def _the_last_person_lines(memory, count):
    """The last few things the person said, oldest first, skipping the echoes doubt asks make."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return ()
    lines = [_flat(turn.get("user")) for turn in turns if isinstance(turn, dict)]
    return [line for line in lines if line][-count:]
