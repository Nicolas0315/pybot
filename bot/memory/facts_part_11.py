"""Part 11 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re


from .facts_part_02 import (
    COMMITS_TO, SPOKEN_RELATION, a_limit_on_the_plan,
)
from .facts_part_03 import (
    A_MARKER_ON_THE_END, CORRECTION_SHAPE,
)
from .facts_part_04 import (
    TAKE_BACK,
)
from .facts_part_07 import (
    subject,
)
from .facts_part_08 import (
    ANY_SUBJECT, CONTINUATION_SPLIT, PERSON_SUBJECT, NOT_A_PART, OTHER_START, SELF_INTRO,
)
from .facts_part_09 import (
    CONTINUATION_KEYS, CONTINUATION_VERB, WISHING, SAME_PERSON_CLAUSE, SAME_PERSON_SPLIT,
    _the_relation_named, CORRECTION_OPENER, SUBJECT_OPENERS, _one_entry_per_person,
    _reported_clause, _union, bot_name, SAYS_WHAT_THEY_ARE, THEIR_NAME, THEIR_PLAN,
)
from .facts_part_10 import (
    _extract,
)


def _the_marker_in_front(text, question=False):
    """The line with a correction word moved from its end to its front, or None.

    "its the 4th actually" is "actually its the 4th". Only the word moves: what follows is read by
    the readers that already know the shape, so a date, a figure, a count and a name all come back
    the same way they do with the marker in front.

    The line left behind has to be a value and nothing else. "my mum is 70 actually" states the
    mother's age, and moving the word would file the 70 a second time as the correction of some
    other fact; "my son is jack actually" would correct the son's name to the name he was just
    given. So a head that says anything of its own is a statement with the word on the end, and a
    statement is not a correction.
    """
    said = str(text or "").strip()
    end = A_MARKER_ON_THE_END.search(said)
    if end is None:
        return None
    head = said[:end.start()].strip()
    if not head or len(head.split()) > 8:
        return None
    if _extract(head, question):
        return None
    return "actually " + head


def reread(value, key):
    """The facts a corrected value states when it is read in the shape that key arrives in."""
    shape = CORRECTION_SHAPE.get(key)
    value = re.sub(r"^(?:a|an|the)\s+", "", str(value or "").strip(), flags=re.I)
    if not shape or not value:
        return {}
    found = extract(shape.format(value))
    found.pop("correction", None)
    return found


def _continued_parts(text):
    """The later clauses of a line about them that leave their subject out, read as their own."""
    clauses, start = [], 0
    for match in CONTINUATION_SPLIT.finditer(text):
        clauses.append(text[start:match.start()])
        start = match.end()
    clauses.append(text[start:])
    words = clauses[0].replace(",", " ").split()
    subject = "person" if words and words[0].lower() in PERSON_SUBJECT else None
    if subject == "person" and WISHING.search(" ".join(words)):
        # "i want to move to bristol and work part time" says what they would like, not what is
        # true: the subject carries over the "and" but the frame does too, and putting it back
        # without the frame turns a wish into a job. Only a clause that states is read.
        return []
    parts = []
    for clause in clauses[1:]:
        clause = clause.strip(" .!?,")
        if not clause:
            continue
        first = clause.split()[0].lower().strip(",")
        if first in ANY_SUBJECT:
            subject = "person" if first in PERSON_SUBJECT else "other"
            continue
        if subject != "person" or first not in CONTINUATION_VERB:
            continue
        for lead in ("i ", "i'm "):
            read = _extract(lead + clause)
            read.pop("name", None)  # a name opens a line: "i like fish and chips" is not Chips
            read = {key: value for key, value in read.items() if key in CONTINUATION_KEYS}
            if read:
                parts.append(read)
                break
    return parts


def _a_clause_about_the_same_person(text):
    """The later clauses of a line that say more about the person the clause before named.

    Only a line that names a relation is read this way: "my mum is 70 and she loves gardening" is
    two facts about the mum, while "the cake is done and she loves it" names nobody and is left
    alone. What the clause says has to be a fact the store keeps about a person, so a clause about
    what they are doing tomorrow ("and she is coming on friday") adds nothing.

    The pronoun belongs to the person named last, not the first one the line opened with: in "my
    son is 7 and my daughter is 3 and she hates peas" the she is the daughter, and reading it onto
    the son filed the daughter's dislike on him as well.
    """
    clauses = [part for part in SAME_PERSON_SPLIT.split(text or "") if part.strip()]
    if len(clauses) < 2:
        return []
    named = _the_relation_named(clauses[0])
    if not named and not any(_the_relation_named(clause) for clause in clauses[1:]):
        return []
    parts = []
    for clause in clauses[1:]:
        found = SAME_PERSON_CLAUSE.match(clause.strip())
        if not found:
            # A clause that names somebody else takes the pronoun over: the next "she" is about
            # the daughter, not the son the line started with.
            named = _the_relation_named(clause) or named
            continue
        if not named:
            continue
        read = _extract("my " + named + " " + found.group("rest").strip())
        kept = []
        for entry in read.get("others") or []:
            if not (isinstance(entry, dict) and entry.get("who")
                    and str(entry["who"]).lower() == named.lower()):
                continue
            # A name only opens a line: "my mum is 70 but she is sharp" is a description, and the
            # name reader takes the word after "is" as one.
            entry = {key: value for key, value in entry.items() if key != "name"}
            if any(value for key, value in entry.items() if key != "who"):
                kept.append(entry)
        if kept:
            parts.append({"others": kept})
    return parts


def _self_intro_parts(text):
    """The list parts of a self-introduction, each read as a line of its own."""
    match = SELF_INTRO.match(text.strip())
    if not match:
        return []
    parts = []
    for piece in re.split(r",|\band\b|;", match.group("rest")):
        piece = piece.strip(" .!?")
        words = piece.split()
        if not words or set(w.lower() for w in words[:1]) & (OTHER_START | NOT_A_PART):
            continue
        # A part that opens with its own subject is a whole clause and is read as it stands: it
        # already says "i", and a lead put in front of it says it twice.
        leads = ("",) if words[0].lower() in PERSON_SUBJECT else ("i'm ", "i ")
        for lead in leads:
            read = _extract(lead + piece)
            if read:
                parts.append(read)
                break
    return parts


def a_correction_without_a_subject(text, before):
    """The fact a subject-less correction states, read with the turn before's subject put back."""
    low = str(text or "").strip().lower()
    if not low or not any(word in low for word in TAKE_BACK):
        return {}
    opener = CORRECTION_OPENER.match(low)
    if not opener:
        return {}
    rest = low[opener.end():].strip()
    if not rest or not any(word in rest for word in TAKE_BACK):
        return {}
    before = str(before or "").strip().lower()
    for shape, frame in SUBJECT_OPENERS:
        if shape.search(before):
            found = extract(frame + " " + rest)
            if found:
                return found
    return {}


def extract(text, question=False):
    """Facts this line states about the user (only the keys it states).

    question says whether the line is a question: it can still state a fact ("I'm allergic to
    nuts, what can I have?"), but only a statement introduces a pet.
    """
    reported = _reported_clause(text)
    if reported:
        # Only when the thing reported is itself a fact: a report of a greeting or a thank you
        # ("i said thanks") names nothing and is read the way it was said.
        if _extract(reported, question):
            text = reported
    found = _extract(text, question)
    given = bot_name(text)
    if given:
        found["bot_name"] = given
    if a_limit_on_the_plan(text) is not None and not COMMITS_TO.search(text):
        # A limit on the plan is not a plan and not a correction: "keep it cheap" was kept as
        # something they are going to do and "no long walks" as a correction to nothing. A line
        # that commits to the plan keeps it - "im going to keep it cheap this month" is the month
        # they have planned, and the limit is how they mean to do it.
        found.pop("plan", None)
        found.pop("plans", None)
        correction = found.get("correction")
        if isinstance(correction, dict) and not correction.get("from"):
            found.pop("correction", None)
    for part in (_self_intro_parts(text) + _continued_parts(text)
                 + _a_clause_about_the_same_person(text)):
        for key, value in part.items():
            if key == "name":
                continue  # the name is the opening word of the line, not of a part
            if key in ("places", "others"):
                # A place and a fact about somebody else are lists that two clauses can both add
                # to: "my mum is 70 and she loves gardening" is one person with two facts.
                found[key] = _union(found.get(key), value)
                if key == "others":
                    found[key] = _one_entry_per_person(found[key])
            elif key not in found:
                found[key] = value
    # The person is kept as the relation, whichever reader found them. The readers that name a
    # person have each been read by now, and not all of them go through `subject` - the age, the
    # name and the condition are read by their own clauses - so "my gf is 30" filed an age under
    # a person the store cannot be asked about while "my girlfriend is 30" filed her own. One
    # mapping at the end is one place, and the entries are merged again because two ways of
    # saying the same person are one person.
    if found.get("others"):
        for entry in found["others"]:
            if isinstance(entry, dict) and entry.get("who") in SPOKEN_RELATION:
                entry["who"] = SPOKEN_RELATION[entry["who"]]
        found["others"] = _one_entry_per_person(found["others"])
    if not found.get("correction") and found.get("drop") is None:
        # A correction word on the end of the line takes the same values back as one in front of
        # it, and the line already reads with the word in front, so the read is that line's read:
        # only the correction is taken, because the rest of the words are the same words.
        marked = _the_marker_in_front(text, question)
        if marked is not None:
            again = _extract(marked, question)
            for key in ("correction", "drop"):
                if again.get(key) is not None:
                    found[key] = again[key]
    return found


def about_themselves(said):
    """The facts a line says about the person themselves, or None when it says none about them.

    A hello in front of a fact is the fact, said by somebody who said hello first: "hi, im
    vegetarian" keeps the diet, and the fact store is the reading that can tell that from
    "hi, im Sam". Three shapes are not that fact. Nothing is not one ("hi there"), a name is
    the chat module's own turn, and a plan is a request the modules that answer a want answer
    better than a note does - the greeting at least leaves the door open to it.
    """
    words = tuple(word.lower() for word in str(said or "").split())
    if not any(words[:len(lead)] == lead for lead in SAYS_WHAT_THEY_ARE):
        return None
    kept = extract(said)
    if not kept or set(kept) <= THEIR_NAME or set(kept) <= THEIR_PLAN:
        return None
    return kept
