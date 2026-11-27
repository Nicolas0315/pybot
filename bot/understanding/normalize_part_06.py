"""Part 6 of 7 of the module, split out of `normalize`.

Everything here is re-exported from `normalize`, so callers import it from there as before.
"""
import re

from . import lexicon
from .normalize_part_01 import (
    DETERMINERS, LEXICON, _one_letter_apart, RAW_WORD, ASK_NOUNS, AUX_WORDS, BE_WORDS, HOW_DEGREE,
    NO_ASK_AFTER, SUBJECT_WORDS, WH_WORDS, RELATIVE_ASKS, COPULAS, NOMINAL_BEFORE_COPULA, RELATIVE,
    REPORTING, BREAKS,
)
from .normalize_part_02 import (
    _plain_word, fix_opener, _a_letter_wrong_in_a_state, _feeling_without_its_ending, spelled,
)
from .normalize_part_03 import (
    CONTRACTION_NEXT, LEFT_OFF_CONTRACTION, A_VERB_CAN_FOLLOW, BEEN_SUBJECT, BE_FORMS,
    BIN_CONTAINERS, HAVE_FORMS, HOW_FOLLOWS, KNOW_SUBJECT, MODAL_FORMS, NOT_BEFORE_KNOW,
    PERSON_PREPS, THING_POSSESSIVES,
)
from .normalize_part_04 import (
    _token, _is_person, _plain_chat, AINT_FORMS, AINT_PLURAL, AMOUNT_BEFORE_A_STATE, CLIPPED_THINGS,
    CLIPPED_UNITS, FIRST_PERSON_BE, HAS_SUBJECT, HV_HELPERS, HV_SUBJECTS, PAST_AS_PARTICIPLE,
    _clipped_thing, _counts_a_period, _family_short, _hr_is_the_department, _is_a_count,
    _is_a_thing_here, _is_be, _is_before_a_noun, _is_participle, _is_said_of_a_person,
    _kin_needs_a_helper, _says_one, _sounds_like_a_feeling, _spells_a_helper, _the_thing_has_been,
    _where_a_state_stands, _is_possessive,
)
from .normalize_part_05 import (
    ILL_GOES_ON, WEARS_AFTER, LETTER_C_IS_SEE, MI_BACK_VERBS, MI_IS_A_NAME_AFTER, MI_IS_ME_AFTER,
    MI_IS_ME_BEFORE, SOLFEGE, UP_TO_LEADS, UP_TO_SPELLINGS, UP_TO_TAGS, VEGGIES_AFTER,
    WHAT_ARE_YOU_AFTER, WHAT_ARE_YOU_SPELLINGS, YOU_ARE_AFTER, _digit_word, _one_of_the_parts,
    _sum_word, _were_for_another_word,
)


def _repair_openers(clauses, fixes):
    """Fix a typo in the word a clause opens with, in place.

    The opening word decides how the whole line is read: "whts the weather like tmrw" is a
    question, "thnks" a thanks, "hii" a hello, and one misspelt letter otherwise leaves the
    line looking like a statement. The repair stays very narrow: only a word no other rule
    knows, only where a clause begins (after a discourse word too: "so wy is my boiler..."),
    and only when exactly one opener is a single slip away.
    """
    for clause in clauses:
        for start in sorted({0, len(clause) - len(strip_leaders(clause))}):
            if start >= len(clause):
                continue
            word = clause[start]
            if _plain_word(word):
                continue
            fixed = fix_opener(word)
            if fixed:
                fixes.append((word, fixed))
                clause[start:start + 1] = _token(fixed, fixes)   # a chat form expands again
                break
    return clauses


def _only_leaders_before(words, index):
    """True when this clause so far is nothing but filler ("so am off to bed").

    "he banged his head and was knocked out" has a subject in front of the "and", so nothing was
    dropped there and the line must be left alone.
    """
    start = 0
    for i in range(index):
        if words[i] == "|":
            start = i + 1
    return all(word in LEADERS for word in words[start:index])


def _ill_is_i_will_going(token, before, after):
    """["i", "will"] for an "ill" with a verb after it that needs a subject, or None."""
    if token != "ill" or after not in ILL_GOES_ON:
        return None
    if before is not None and before != "|" and before not in LEADERS:
        return None
    return ["i", "will"]


def _an_ill_that_is_i_will(clean):
    """`clean` with an "ill" that can only be "i will" set down as the two words.

    The readers that answer match on `clean` and `words`, so the contraction has to be put right
    where the line is written or the knowledge base still sees somebody who is ill. The same test
    as `_ill_is_i_will_going`: the verb after it needs a subject, and nothing in front of the "ill"
    is one.
    """
    words = clean.split()
    changed = False
    for index, word in enumerate(words):
        if word != "ill" or index + 1 >= len(words):
            continue
        if words[index + 1] not in ILL_GOES_ON:
            continue
        before = words[index - 1] if index else None
        if before is not None and before != "|" and before not in LEADERS:
            continue
        words[index] = "i will"
        changed = True
    return " ".join(words) if changed else clean


def _left_off_contraction(token, before, after, before_before):
    """The two words a contraction written without its apostrophe stands for, or None.

    The next word has to be one only the contraction can be followed by, and the word in
    front must leave the plain reading out: "were going to spain" reads as the contraction,
    while "we were late", "how were things" and "were you there" keep their words.
    """
    words = LEFT_OFF_CONTRACTION.get(token)
    if not words or after not in CONTRACTION_NEXT:
        return None
    # "were" is the past of be after a subject ("we were late", "how were things"), so the
    # contraction is only taken where the clause has no subject in front of it yet.
    if before is not None and before != "|":
        leaders_only = before in LEADERS and (
            before_before in (None, "|") or before_before in LEADERS)
        if not leaders_only:
            return None
    return list(words)


def _wers_word(before):
    """The two words a typed "wers" stands for, from the word in front of it.

    "wers" is the e and the apostrophe gone from "where's" and the a gone from "wears", and no
    word list can say which: "wers my keys" is the lost keys, "she wers a red coat" is what she
    wears. The word in front decides, because the verb has to have a person doing the wearing
    in front of it and the question has to be at the front of its clause: after a person it is
    "wears", at the front of a line or a clause or after a lead-in word ("so wers my keys") it
    is "where is".
    """
    if before in (None, "|") or before in LEADERS:
        return ["where", "is"]
    if _plain_chat(before) in WEARS_AFTER or _is_person(before):
        return ["wears"]
    return ["where", "is"]


def _positional_word(token, before, after, after_after=None, before_before=None,
                     before_words=None):
    """The word a quickly typed token stands for, from where it sits, or the token itself.

    "w" on its own is not a word and is "with"; "2" and "4" are "to" and "for" in front of a
    phrase opener, and in front of a demonstrative unless a period follows it; "no" is "know"
    between a subject and what a verb takes; "were" at the front of a line is "where" in front
    of a verb and "we are" in front of anything else.
    """
    if (token in UP_TO_SPELLINGS
            and (before is None or before == "|" or before in UP_TO_LEADS)
            and (after is None or after == "|" or after in UP_TO_TAGS)
            and (after_after is None or after_after == "|")):
        return ["what", "you", "up", "to"]
    if token in WHAT_ARE_YOU_SPELLINGS and after in WHAT_ARE_YOU_AFTER:
        return ["what", "you"]
    if token == "w":
        return ["with"]
    if token == "c" and after in LETTER_C_IS_SEE:
        # "c u later" is a goodbye typed with the letter for the word, the way "cu" is one
        # written as a single token, and it reached the bot as a line with nothing in it: "c u"
        # got the thanks-for-telling answer and "c u later" the shrug. The letter stays the
        # letter everywhere else - "vitamin c", "plan c", "hepatitis c", "c section" - so only
        # the second person pronoun in front of it turns it into "see".
        return ["see"]
    if token == "wers":
        return _wers_word(before)
    if token == "sum":
        return _sum_word(before, after)
    if token == "were":
        spelled = _were_for_another_word(before, after, after_after)
        if spelled:
            return spelled
    if token in CLIPPED_THINGS and _is_a_thing_here(before, after, after_after):
        return [_clipped_thing(token)]
    if token in CLIPPED_UNITS and (_is_a_count(before) or _says_one(before)):
        # "4 yr old", "2 hrs sleep", "ten mins". The count in front is what makes it safe: on
        # its own "yr" is how people type "your", and "hr" is the department.
        one, many = CLIPPED_UNITS[token]
        if token == "hr" and _hr_is_the_department(after):
            return [token]        # "this hr department", "past hr policies"
        if _says_one(before) or _is_before_a_noun(token, after):
            return [one]          # "1 hr drive", "a 3 hr flight", "next yr"
        return [many]
    contraction = _left_off_contraction(token, before, after, before_before)
    if contraction:
        return contraction
    going = _ill_is_i_will_going(token, before, after)
    if going:
        return going
    feeling = _sounds_like_a_feeling(token, before, after, before_before)
    if feeling:
        return [feeling]
    read = _digit_word(token, before, after, after_after)
    if read:
        return [read]
    if token == "wdyt" and after and after != "|":
        # "wdyt about moving house". `wdyt` is "what do you think", and the line it was in got the
        # initials said back to it ("Got it - wdyt about moving house"). Only with a subject after
        # it: a bare "wdyt" leans on the last turn, and every reader the expansion reaches wants
        # the subject in the line itself.
        return ["what", "do", "you", "think"]

    one_part = _one_of_the_parts(token, before, after)
    if one_part:
        return [one_part]
    if token == "ow" and after in HOW_FOLLOWS:
        # "ow do i clean a rug", "ow much is milk": the people who drop the h drop it every time.
        # The next word is what makes it safe - "ow my head" and "ow that hurt" keep their "ow".
        return ["how"]
    if token == "bout" and before not in DETERMINERS:
        return ["about"]                          # "arguin bout money", "whats that bout"
    if token == "no" and (before in KNOW_SUBJECT or before in NOT_BEFORE_KNOW):
        # The word after is read through the chat tables first: "i dont no y" and "dont no
        # wat to do" put a typed question word behind the "no", and the raw token is not the
        # word the list holds.
        after_read = _plain_chat(after) if after and after != "|" else after
        if (after is None or after == "|" or after in A_VERB_CAN_FOLLOW
                or after_read in A_VERB_CAN_FOLLOW):
            return ["know"]
    if token == "hv":
        before_read = _plain_chat(before) if before else ""
        after_read = _plain_chat(after) if after else ""
        if before_read in DETERMINERS:
            return [token]                        # "the hv", "my hv": the health visitor
        if before_read in HV_SUBJECTS or before_read in HV_HELPERS or after_read == "to":
            return ["have"]                       # "i hv", "shld hv", "hv to go"
        if after_read in HV_SUBJECTS:
            return ["have"]                       # "hv u got a min", "how many hv u got"
    if token == "bin":
        if before in HAVE_FORMS or (before or "").endswith("ve"):
            return ["been"]                       # "i have bin", "ive bin"
        if _is_person(before) and (after in PERSON_PREPS or _is_participle(after)
                                   or _is_said_of_a_person(after)):
            return ["been"]                       # "my mums bin in hospital", "my cats bin sick"
        if before_before in THING_POSSESSIVES \
                and (_plain_chat(before) if before else "") not in BIN_CONTAINERS \
                and _the_thing_has_been(after):
            return ["been"]                       # "my phones bin actin up all wk"
        if (before in BEEN_SUBJECT or before in BE_FORMS or before in (None, "|")) \
                and (_is_said_of_a_person(after) or (after or "").isdigit()
                     or _counts_a_period(after) or _counts_a_period(after_after)
                     or (before in BEEN_SUBJECT and after in ("a", "an"))):
            # "bin thinkin bout it", "that is bin 3 wks now", "its bin two months". The word in
            # front has to be the person or the helper, so "bin day" and "the bin lorry" are bins.
            return ["been"]
    if token == "of" and _plain_chat(before) in MODAL_FORMS and _is_participle(after) \
            and before_before not in DETERMINERS:
        # "should of started", "could of been". "what should i think of" keeps its "of", because
        # a line that names the spelling it asks about is a question about words, and a
        # determiner in front makes the modal the thing itself: "a can of red paint",
        # "the will of the people" and "her might of it" are cans, wills and mights.
        return ["have"]
    if token in AINT_FORMS:
        # "ain't" is whichever helper the writer left out. "have not" when the verb that
        # follows is a participle ("i aint eaten all day", "aint got a job yet"), "am not"
        # after "i" ("i aint happy"), "are not" after a plural subject, "is not" otherwise.
        # Reading every one as "is not" gives "i is not eaten all day", and a line whose
        # negation is left as a strange helper is a line the entries that key on it miss:
        # "aint got a job yet" came back congratulating them on the job.
        if _is_participle(after) or after in PAST_AS_PARTICIPLE:
            return ["has", "not"] if before in HAS_SUBJECT else ["have", "not"]
        if _plain_chat(before) == "i":
            return ["am", "not"]
        if _plain_chat(before) in AINT_PLURAL:
            return ["are", "not"]
        return ["is", "not"]
    if token == "of" and after == "to" and _is_be(before):
        return ["off"]                        # "im of to work", "we were of to spain"
    if token == "b" and _spells_a_helper(before):
        return ["be"]                          # "gona b late", "ill b there", "should b fine"
    if (after is None or after == "|") and _where_a_state_stands(
            before, before_before, after, before_words):
        # A state word with a letter typed wrong, said of the person and nothing after it: "im
        # hungy", "im thisty", "im colde". These are not a state missing an ending, so the rule
        # below cannot see them, and a word that says how they are with nothing after it is the
        # whole of the evidence that it is how they are and not what they are called. How many
        # measure words come before it does not change that: "im so so hungy" is still hungry.
        state = _a_letter_wrong_in_a_state(token)
        if state:
            return [state]
    if before in FIRST_PERSON_BE or (before_before in FIRST_PERSON_BE
                                    and before in AMOUNT_BEFORE_A_STATE):
        # A feeling with its ending left off, right where the person says how they are: "im
        # annoy", "im bore", "im excit", "im confuse". These are words already, so the
        # misspelling fixer may not touch them, and every one of them was answered "Nice to
        # meet you, Annoy". The word in front is the whole of the evidence, so a line about a
        # bush or a tyre is left alone. One measure word may stand between the two and says
        # nothing about which word comes next: "im still confus" and "im so bore" are the same
        # feeling, "im very tire" is tired rather than a tyre, and "im so nervou about
        # tomorrow" is nervous.

        feeling = _feeling_without_its_ending(token)
        if feeling:
            return [feeling]
    kin = _kin_needs_a_helper(token, before, after,
                              before_before is None or before_before == "|"
                              or before_before in LEADERS, after_after)
    if kin:
        return kin                             # "my mums got a chest infection" -> "my mum has got"
    if token in ("yr", "yrs") and (before or "").isdigit():
        # "my 9 yr old" is nine years old, not the "nine your old" the chat table alone gives:
        # `yr` is typed for "your" too ("yr welcome"), so the number in front decides it.
        return ["years" if token.endswith("s") or after == "old" else "year"]
    family = _family_short(token, before, after, after_after)
    if family:
        # "my mil" is my mother in law, "my oh" my other half, "my dd" my daughter
        return family
    if token == "veggies" and before in VEGGIES_AFTER:
        # "roast veggies" is a plate of vegetables; "3 are veggies" is three vegetarians.
        return ["vegetables"]
    if token in ("ur", "your") and after and after in YOU_ARE_AFTER:
        # The contracted spelling, because `plain` says the line back and "Noted: you're going
        # to love this" is how a friend writes it; the reading is still "you" and "are".
        # "your" is the same two words with the apostrophe left off, and the word after it is
        # what says so: a possessive is followed by the thing it owns ("your mum", "your
        # boiler"), never by an article, a word of degree or the word for what somebody is
        # doing. Read as a possessive, "your a good bot" was answered "Got it. Is there
        # anything you'd like a hand with?" while "you are a good bot" answered the question
        # about what the bot is, and "your going to love this" came back as "Noted: your going
        # to love this". Words a possessive does take are left alone, which is why "your kind"
        # and "your right" are not in the list: "your kind of tea", "your right hand".
        return ["you're"]                      # "ur a star", "your a good bot", "your so kind"
    if token == "mi" and after in MI_IS_ME_AFTER:
        # "mi and my friend went out", "mi too": here "mi" is how "me" is typed, and the word
        # after it is what says so. A possessive with nothing to possess is not a sentence -
        # read as "my" these came out "your and your friend went out" and "Noted: your and the
        # dog", which is worse than the slip.
        return ["me"]
    if token == "mi" and before in MI_IS_A_NAME_AFTER:
        # "the mi band is cheap", "this mi phone": a possessive cannot follow a determiner, so
        # the "mi" belongs to the name of the thing and is left as it was typed.
        return [token]
    if token == "mi" and after in MI_IS_ME_BEFORE:
        # "call mi later", "send mi the link", "tell mi what u think": nothing after it can be
        # owned, so it is "me" and not "my". Read as "my" these came out "call my later".
        return ["me"]
    if token == "mi" and after == "back" and before in MI_BACK_VERBS:
        # "text mi back", "ring mi back later tonight": the verb in front makes the "back" part
        # of it, so the "mi" between them is "me". Without a verb of that kind the "back" is a
        # body and "mi back is playing up" stays "my back".
        return ["me"]
    if token == "mi" and (after is None or after == "|"):
        # The line ends on it: "who is it? mi", "thats mi", "wait for mi". A possessive has
        # nothing to stand on there, so it is "me".
        return ["me"]
    if token == "mi" and not (before in SOLFEGE
                              and (after is None or after == "|" or after in SOLFEGE)):
        # "mi" is how "my" is typed in a lot of everyday writing ("mi mum is coming round",
        # "mi tea is cold", "mi boiler is broke"), and it is not an English word, so the only
        # thing that needs keeping out of the way is the note in a run of them: "do re mi fa",
        # where "so mi boss said no" is still "my boss".
        if before is not None and before != "|" and before not in LEXICON:
            # The last piece of a name rather than the start of a phrase: "i got a xiaomi mi band",
            # "a redmi mi note". The word in front of it is not one the lexicon knows, so it is
            # the end of a made-up one and "mi" belongs with it.
            return [token]
        return ["my"]
    return [token]


# "The docs" is two different things: the surgery down the road ("should she go to the docs",
# "ring the docs in the morning") and a set of papers ("send the docs to my email", "the docs are
# in the folder"). The word "doctor" is what the health answers are keyed on, so a line about the
# surgery that says "docs" reached none of them - `my mums got a chest infection should she go to
# the docs` got the search hedge while the same line with "doctor" got the pharmacist-or-GP
# answer. The verb is what tells them apart: you go, ring, call, visit or see the doctor; you send,
# print, sign or read the documents.
DOCS_VISIT = frozenset("""go goes going gone went see sees seeing saw seen visit visits visiting
    ring rings ringing rang call calls calling called phone phones phoned ask asks asking asked
    book booked appointment appointments consult surgery gp""".split())


# A line with one of these in it is about paperwork, whatever else it says.
DOCS_PAPER = frozenset("""send sends sent email emails emailed print printed download downloaded
    upload uploaded scan scanned file files folder contract contracts paperwork invoice invoices
    lease leases tax read reading sign signed attach attached share forward forwarded page pages
    pdf copy copies draft document documents solicitor mortgage insurance check checked
    through""".split())


# A document can be the thing on a screen, which a verb of going or ringing says nothing about:
# "can i see the docs on my phone" is Google Docs, not a surgery appointment. These words name
# the screen itself, and the ones in DOCS_ON say "on the screen" rather than "ring the surgery".
DOCS_SCREEN = frozenset("""tablet laptop pc screen online app apps link links browser website web
    google drive cloud portal intranet""".split())


DOCS_ON = frozenset(("on", "in", "via", "from", "as", "into"))


def _docs_on_a_screen(words):
    """Whether the line is about the docs on a screen rather than a visit to the surgery."""
    if any(word in DOCS_SCREEN for word in words):
        return True
    for index, word in enumerate(words):
        if word in ("phone", "tablet", "laptop", "pc", "screen", "file"):
            if any(back in DOCS_ON for back in words[max(0, index - 2):index]):
                return True
    return False


# The meal a person names when they say what to eat, and the words that put a word in that slot:
# "what should i have for tea", "whats for dinner", "anything after lunch". The food rows are
# keyed on the meal itself, so a meal word typed at speed costs the whole answer - "wot shud i av
# for tae" got "I don't know enough to answer that honestly. A search should sort you out
# quickly" while the same line with "tea" in it got the fifteen-minute dinner.
MEAL_WORDS = frozenset("""tea dinner supper lunch breakfast brunch snack food""".split())


FOOD_SLOT_LEAD = frozenset("""for at after before til till until round over about""".split())


# "for tee" is a golf tee as often as a cup of tea, and it is a word in its own right, so it is
# not a spelling of "tea" that this repair takes.
NOT_A_MEAL_TYPO = frozenset(("tee",))


# A meal stands at the end of the line or has the time it is for behind it: "whats for tae",
# "whats for brea tomorrow". Any other word after it means the word is not that slot's meal.
TIME_AFTER_MEAL = frozenset("time tonight tomorrow today now later".split())


def _near_a_meal(word, before, after=None):
    """The meal a misspelt word names, or None.

    Only in the slot a meal goes in (behind "for", "after", "before", ...), and only one letter
    out from one of the meals: "tae", "taa", "tay", "dinnar", "sunner". A word the lexicon knows
    is left alone, so "for two", "at tea", "for the launch" and a golf tee are untouched.

    The position is what keeps a real sentence out: the misspelt meal has to end the line or sit
    in front of a time word, because that is where a meal stands ("whats for tae", "whats for
    brea tomorrow"). Behind "for" alone it is far too easy - "ask for branch details", "for
    upper floor", "for inner peace", "for bunch of flowers" are all one letter from a meal and
    all words of their own, most of them outside the lexicon.
    """
    if not word or len(word) < 3 or word in LEXICON:
        return None
    if _plain_chat(before) not in FOOD_SLOT_LEAD:
        return None
    if after is not None and _plain_chat(after) not in TIME_AFTER_MEAL:
        return None
    if word in NOT_A_MEAL_TYPO:
        return None
    # The last letter left off is the other way people type at speed - "for lunc", "after dinn",
    # "whats for brea" - and behind the slot a meal is the only word it can be.
    for meal in sorted(MEAL_WORDS):
        if len(word) >= 4 and meal.startswith(word):
            return meal
    found = sorted(meal for meal in MEAL_WORDS if _one_letter_apart(word, meal))
    return found[0] if len(found) == 1 else None


def _a_meal_word_misspelt(clean, words):
    """Put a meal word typed at speed back in the line, in `clean` as well as the reading.

    It is repaired in `clean` for the reason the "docs" repair is: the kitchen's rows are keyed
    on the meal, so a reading fixed on its own would leave the reply where it was. The slot is
    what makes it safe - the word in front has to be the preposition a meal goes behind, and
    what follows has to be the end of the line or the time it is for - and that is what keeps a
    name out of it ("tae is coming over", "me and tae went out"). A name can sit behind "for"
    ("im waiting for tae" reads as the meal), so it is the position, not the name, that decides.
    """
    places = {}
    for index, word in enumerate(words):
        if not index:
            continue
        after = words[index + 1] if index + 1 < len(words) else None
        meal = _near_a_meal(word, words[index - 1], after)
        if meal:
            places[index] = meal
    if not places:
        return clean, words
    pieces, last = [], 0
    for index, match in enumerate(RAW_WORD.finditer(clean)):
        pieces.append(clean[last:match.start()])
        pieces.append(places.get(index, match.group(0)))
        last = match.end()
    pieces.append(clean[last:])
    for index, meal in places.items():
        words[index] = meal
    return "".join(pieces), words


def _docs_doctor(clean, words):
    """"Docs" is read as the doctor where the line is about the surgery, and left as it is.

    Only the two spellings people type for it, `doc` and `docs`, and only when a verb of going
    or ringing is within a few words on either side and the line names no paperwork at all. A
    line naming neither stays as typed: guessing one way would be worse than not guessing.

    It is the one repair made in `clean` rather than only in `plain`, because no table anywhere
    is keyed on "docs": the health answers hold "doctor" and the paperwork ones hold "pdf",
    "folder", "invoice". Repairing `plain` alone moves the reading and leaves the reply alone,
    which is where this line stood. The usual cost of repairing `clean` - a cue list that holds
    the typed form loses its match - cannot be paid here, because no list holds this one.
    """
    if not any(word in ("doc", "docs") for word in words):
        return clean, words
    if any(word in DOCS_PAPER for word in words):
        return clean, words
    if _docs_on_a_screen(words):
        return clean, words
    places = set()
    for index, word in enumerate(words):
        if word not in ("doc", "docs"):
            continue
        near = words[max(0, index - 4):index] + words[index + 1:index + 3]
        if any(other in DOCS_VISIT for other in near):
            places.add(index)
    if not places:
        return clean, words
    # The i-th match of RAW_WORD is the i-th word, so the two lists line up.
    pieces, last = [], 0
    for index, match in enumerate(RAW_WORD.finditer(clean)):
        pieces.append(clean[last:match.start()])
        pieces.append("doctor" if index in places else match.group(0))
        last = match.end()
    pieces.append(clean[last:])
    for index in places:
        words[index] = "doctor"
    return "".join(pieces), words


# A relation a person has one of keeps its "s" when a verb that takes a single person follows
# it: "my mums got a bad chest" is "my mum has got a bad chest", and the health of one woman is
# what the line is about, not several mothers. Only one-and-only relations are in the set, so
# "my kids got chickenpox" and "my sisters got married" keep the plural they mean, and only after
# a possessive, so "the mums got together" is left alone.
ONE_RELATION = frozenset("""mum mom mam mummy mommy dad daddy nan nana gran granny grandad
    grandpa granddad grandma grandmother grandfather mother father husband wife""".split())


# The verbs that take a "has" in front of them, so the possessive's "'s" comes back as a word.
HAS_FORMS = frozenset(("got", "bin", "had"))


# The words a single person is the subject of in an everyday line: a helper, "got", or one of the
# verbs a parent turns up as the subject of ("my mums said", "my mums wont eat").
# `called` and `rang` are left out on purpose: after "my mums" they are the verb of the
# sentence only when the line is about someone ringing. "my mums called janet" is the name of
# the mum, which the composer reads back to the person ("your mum's called janet"), so taking
# the "s" off there would change a name into a phone call.
ONE_RELATION_VERBS = frozenset("""got bin wont cant said says told went came goes needs wants
    keeps lives works gets thinks loves hates""".split())


# "sor" is a sore spot typed with a letter missing, and it is also the front of "sorry": a
# repair wherever the word turns up read "i am sor about that" as a sore body and answered
# "That sounds wearing..." where main shrugs. A body word names itself, so "sor" comes back as
# "sore" in front of a part of the body or after the verb that says how it is, and nowhere else.
SORE_IN_FRONT = frozenset("""is are was were been feels feel felt gets get got still""".split())


# "so", "very" and "really" come after a verb of being in "my back is very sor" and after a
# person in "im so sor i forgot", which is the apology. The word is only stepped over when a
# verb of being stands in front of it, so the apology keeps its own reading.
SORE_FILLERS = frozenset("""so very really bit little too pretty quiet that""".split())


SORE_PARTS = frozenset("""throat back head neck shoulder shoulders knee leg legs foot feet arm
    arms toe toes hip ankle wrist elbow ear ears eye eyes tooth teeth gum mouth hand hands
    finger fingers belly stomach muscle muscles chest side sides rib ribs heel heels jaw skin
    tongue sunburn""".split())


def a_sor_bit_is_sore(tokens):
    """"my throat is sor" is "my throat is sore", and "i am sor about that" is left alone."""
    out = []
    for index, token in enumerate(tokens):
        if token == "sor":
            before = tokens[index - 1] if index else None
            after = tokens[index + 1] if index + 1 < len(tokens) else None
            fills = (index > 1 and before in SORE_FILLERS
                     and tokens[index - 2] in SORE_IN_FRONT)
            if ((before is not None and (before in SORE_IN_FRONT or fills))
                    or (after is not None and after in SORE_PARTS)):
                out.append("sore")
                continue
        out.append(token)
    return out


def _one_relation_says(words):
    """"my mums got a bad chest" is "my mum has got a bad chest".

    The possessive left out its "'s", so the relation is the subject on its own: the "s" on it
    is the "has" or the "is" of the line and not a plural, and it goes when a verb that takes
    one person follows it. A verb that takes a "has" in front of it gets the "has" back, which
    is the way the line would be spelt out: "my mums had a fall" is "my mum has had a fall".
    """
    out = []
    for index, word in enumerate(words):
        after = words[index + 1] if index + 1 < len(words) else None
        if (index and after and word.endswith("s") and word[:-1] in ONE_RELATION
                and _is_possessive(words[index - 1])):
            read = _plain_chat(after)
            if read in ONE_RELATION_VERBS or read in HAVE_FORMS or read in BE_FORMS \
                    or read in MODAL_FORMS:
                out.append(word[:-1])
                if read in HAS_FORMS:
                    out.append("has")
                continue
        out.append(word)
    return out


def _ask_start(clause):
    """Where an ask begins inside a clause that did not open with one, or None.

    Only shapes that read as a real question are taken: a question word with an auxiliary
    or a degree word after it ("what could be wrong", "how long until he sleeps"), or an
    auxiliary with a subject after it ("... can i take ibuprofen"). A question word that
    introduces a reported clause ("i do not know what to do", "what to do next", "the book
    which i read") is left alone, so a feeling is still a feeling.
    """
    if not clause or clause[0] in WH_WORDS or clause[0] in AUX_WORDS:
        return None                  # the clause already opens like a question
    for start in range(1, len(clause)):
        token = clause[start]
        following = clause[start + 1] if start + 1 < len(clause) else None
        after = clause[start + 2] if start + 2 < len(clause) else None
        if following is None:
            continue
        if token in WH_WORDS:
            if following in AUX_WORDS or _a_word_between_the_ask_and_its_aux(clause, start):
                if _reported(clause, start):
                    continue
                return start
            if following in HOW_DEGREE or (following in ASK_NOUNS and after in AUX_WORDS):
                if _reported(clause, start):
                    continue
                return start
        elif token in AUX_WORDS and following in SUBJECT_WORDS:
            if clause[start - 1] in NO_ASK_AFTER:
                continue
            if clause[start - 1] in SUBJECT_WORDS:
                # "we have you down for tuesday", "they have you booked in": the auxiliary is
                # the verb of the subject already in front of it, so it opens nothing
                continue
            if token in BE_WORDS:
                # "the thing is i do not know", "my worry is i will not finish",
                # "what matters is you get there": a be-form in front of a person links a
                # clause, and a yes/no question never opens with "is i" or "was she".
                continue
            return start
    return None


# A word belongs to the question phrase in front of it rather than to a clause of its own:
# "what else do i need", "which size should i get", "what kind of paint do i need", "what
# present would she like". Cut at the auxiliary instead and the ask reads "do i need", which is
# no ask at all, so the question word is where the ask begins.
WH_QUANTIFIERS = frozenset("""else other others kind sort type size colour color number
    make model brand version flavour flavor""".split())


# What cannot stand between a question word and the auxiliary that asks it. A pronoun, a
# determiner or another verb there means the question word is reported or relative, not asked.
NOT_IN_A_QUESTION_PHRASE = frozenset("""
    i me my mine we us our you your he him his she her it its they them their
    the a an this that these those some each every which what who whom whose
    to of for in on at by with from about as than if whether there here
    do does did is are was were am be been being have has had will would shall should can
    could may might must not no never""".split()) | WH_QUANTIFIERS


# A question word asks through an auxiliary only when the auxiliary is followed by the person or
# thing that does it: "what present would she like" asks, while "she keeps forgetting where things
# are in the kitchen" and "my printer says paper jam when there is not one" report where something
# is or how something is, because the auxiliary comes after its subject rather than in front.
AFTER_AN_INVERTED_AUX = frozenset("""
    i we you he she they there it this that these those
    the a an my our your his her their some any""".split()) | SUBJECT_WORDS


def _a_word_between_the_ask_and_its_aux(clause, start):
    """True when the question word at clause[start] reaches an auxiliary over a few words.

    "what present would she like", "what sort of shoes do i need", "what party games would he
    like": the words between belong to the question, and the auxiliary that follows asks it. A
    pronoun, a determiner or a second verb between them means the question word is reported or
    relative, so that is left alone.
    """
    span = clause[start + 1:start + 6]
    for offset, word in enumerate(span):
        if word in AUX_WORDS:
            crossed = [w for w in span[:offset] if w not in WH_QUANTIFIERS
                       and w not in ("of", "for")]
            subject = clause[start + 2 + offset] if start + 2 + offset < len(clause) else None
            return (len(crossed) <= 2 and not (set(crossed) & NOT_IN_A_QUESTION_PHRASE)
                    and subject in AFTER_AN_INVERTED_AUX)
    return False


def _inverted_ask(clause, start):
    """True when the relative word is really the question: "who should i see"."""
    after = clause[start + 1:start + 3]
    return (len(after) > 1 and after[0] in RELATIVE_ASKS
            and after[1] in SUBJECT_WORDS)


def _reported(clause, start):
    """True when the question word at clause[start] reports or names rather than asks."""
    before = clause[max(0, start - 2):start]
    if not before:
        return False
    if set(before) & REPORTING:
        return True
    if (clause[start] in RELATIVE
            and not _inverted_ask(clause, start)
            and before[-1] not in AUX_WORDS and before[-1] not in WH_WORDS
            and before[-1] not in REPORTING
            and (before[-1] in DETERMINERS or len(before) > 1
                 and (before[-2] in DETERMINERS or before[-2] in NOMINAL_BEFORE_COPULA))):
        return True
    return (before[-1] in COPULAS
            and (len(before) < 2 or before[-2] in NOMINAL_BEFORE_COPULA))


def _split_ask(clauses):
    """Clauses with an ask that sits inside one moved out into a clause of its own.

    "im knackered all the time what could be wrong" becomes two clauses, so the focus, the
    kind and every module that reads the ask see the question rather than the news.
    """
    out = []
    for clause in clauses:
        start = _ask_start(clause)
        if start is None or start >= len(clause) - 1:
            out.append(clause)
            continue
        out.append(clause[:start])
        out.append(clause[start:])
    return out


# A clause can begin with one of these, so a discourse marker in front of one starts a clause.
CLAUSE_OPENERS = frozenset("""i we you they he she it this that there anyone anybody someone
    everyone somebody nobody nothing""".split())


def _opens_clause(token):
    """Can a clause of its own begin with this word?"""
    return (token in CLAUSE_OPENERS or token in SUBJECT_WORDS or token in WH_WORDS
            or token in BREAKS or token in LEADERS)


# "she's got", "he's been", "she's had a fall": the apostrophe-s after a pronoun is "has" in
# front of a participle and "is" everywhere else. English has no "she is got", so the word in
# front decides it. Only the three participles that cannot be a state are here: "she is told
# off", "he is said to be leaving", "she is known for her cakes", "she is paid weekly" and "he
# is kept busy" are all passives and right as typed, so "told", "said", "known", "paid" and
# "kept" stay out. "she is tired", "it is gone" and "the job is done" keep the "is" the same way.
HAS_AFTER = frozenset("""got been had""".split())


# Only a person in front moves the verb. "it's been a long week" is a state the speaker is in
# and reads as small talk, and "it is gone", "that is done" are states of the thing named, so
# "it", "that", "this" and "there" keep the "is" they were typed with.
HAS_SUBJECTS = frozenset("she he who".split())


def _says_has(words):
    """"she is got a cold" -> "she has got a cold": a pronoun, an "is" and a participle.

    "gone" counts only with a word after it: "she is gone to the doctors" is "she has gone to
    the doctors", while a bare "she is gone" is a person who is dead or away, which is a state
    and stays as it was typed.
    """
    for index in range(1, len(words) - 1):
        if words[index] != "is" or words[index - 1] not in HAS_SUBJECTS:
            continue
        after = words[index + 1]
        if after in HAS_AFTER or (after == "gone" and index + 2 < len(words)):
            words[index] = "has"
    return words


def _clauses(tokens):
    """Split a run-on line into clauses at punctuation and discourse markers.

    A marker only opens a clause when a clause can begin after it. "my landlord still has
    not fixed the boiler" and "i wanted to go but could not afford it" keep it: there the
    marker is part of the clause, and cutting it off left "has not fixed the boiler" and
    "could not afford it", which read as yes/no questions.
    """
    out, current = [], []
    for n, token in enumerate(tokens):
        if token == "|":
            if current:
                out.append(current)
                current = []
            continue
        following = tokens[n + 1] if n + 1 < len(tokens) else None
        if (token in BREAKS and len(current) >= 2 and following
                and _opens_clause(following)):
            out.append(current)
            current = []
            continue
        current.append(token)
    if current:
        out.append(current)
    return out


LEADERS = frozenset("""and so but also then ok okay oh well right now anyway anyways
hi hiya hey hello morning evening thanks thank thx cheers ty please just actually still
finally instead otherwise plus however meanwhile btw honestly anyway""".split())


# A line that opens on "like" is opening on a filler, and the clause behind it starts with one
# of these: "like my cat wont eat", "like im so tired", "like what should i cook". The word
# itself is a real one, so the frame is what tells the two apart: "like a sauna in here",
# "like butter", "it is like that", "like this one" and "like father like son" all keep it,
# because nothing that opens a clause follows the "like".
LIKE_STARTS_A_CLAUSE = frozenset("""
i im ive id ill me my mine we were weve us our ours you youre youve your he hes she shes it its
they theyre theyve their them
what why how when where who which whose
can cant cannot could couldnt should shouldnt would wouldnt do dont doesnt did didnt
is are was were will wont have has had havent hasnt dont didnt get got gets need needs want
wants keep keeps just never not so too always still really gonna wanna dunno idk
u ur ya yall
""".split())


def _a_leading_like_is_a_filler(clean):
    """"like my cat wont eat" is about the cat, so the "like" is not part of the line.

    People open a line with "like" the way they open it with "so" or "well", and the word is a
    real one, so it was read as a comparison and the line lost its answer: "like my cat wont
    eat" was noted back and "like my broadband keeps dropping out" got the warm line where "my
    broadband keeps dropping out" gets the router answer. Only a clause opener after it makes
    it the filler, which is what keeps a comparison out of it.
    """
    head, _, rest = clean.partition(" ")
    if head.strip(",.!?") != "like" or not rest:
        return clean
    after = rest.split(" ", 1)[0].strip(",.!?")
    if after not in LIKE_STARTS_A_CLAUSE:
        return clean
    return rest


# An exclamation after a question word is the person's surprise, not a thing the line is about.
# "what on earth", "how on earth", "what in the world": the Earth card answered "what on earth"
# with the Earth's layers, and "why on earth is my boiler not lighting" was read as a line about
# the planet instead of the boiler. Only a question word in front makes it an exclamation, so
# "the coldest place on earth" and "how old is the earth" keep their Earth. The two that name
# nothing ("the hell", "the heck") are left alone: no card reads them, and taking them out leaves
# a bare question where "Go on - what happened?" is the warmer answer.
EXCLAIMED_AFTER_A_QUESTION = re.compile(
    r"\b(what|how|why|where|who|which|when|whatever|however|whoever|whenever)\s+"
    r"(?:on\s+earth|in\s+the\s+world|the\s+dickens|the\s+blazes|on\s+god'?s\s+earth)\b")


# A line can open on an exclamation of exasperation, and the word is not the person's subject:
# "god i hate mondays" was filed as a fact about them and said back as "Noted: god you hate
# mondays.", which reads as nonsense. The same for "honestly", "ugh", "jesus", "blimey", "omg"
# and a run of them ("oh god i forgot"). The words only go when a subject follows, so "thank god
# i got out", "oh no" and "oh the bus" keep every word they have.
EXCLAMATION_OPENS = frozenset("""god honestly ugh jesus christ blimey crikey cor gosh omg
    jeez sheesh oh ah""".split())


# The exclamations that are a phrase rather than a word: "oh my god i love it", "my god i love
# it". Read before the single words, or the "my" would look like the person's own and stay.
EXCLAMATION_PHRASE = re.compile(
    r"^(?:oh\s+my\s+god|my\s+god|good\s+grief|for\s+goodness'?\s*sake|"
    r"for\s+god'?s?\s*sake)\s+")


_EXCLAMATION_SUBJECTS = frozenset("""i im ive id ill we weve youre you he hes she shes they
    theyre it its my me your our""".split())


def without_a_leading_exclamation(clean):
    """The line without the exasperation it opens on: "god i hate mondays" is "i hate mondays".

    Public because the composer says a line back in its own words and works from the line as it
    was typed, not from `clean`: "god i hate mondays" came back as "Noted: god you hate mondays."
    """
    return _an_exclamation_in_front(clean)


def _an_exclamation_in_front(clean):
    """The line without the exasperation it opens on: "god i hate mondays" is "i hate mondays"."""
    for _ in range(3):
        phrase = EXCLAMATION_PHRASE.match(clean)
        if phrase:
            rest = clean[phrase.end():]
            if rest and rest.split(" ", 1)[0].strip(",.!?;:-|") in _EXCLAMATION_SUBJECTS:
                clean = rest
                continue
            return clean
        head, _, rest = clean.partition(" ")
        if not rest or head.strip(",.!?;:-|") not in EXCLAMATION_OPENS:
            return clean
        after = rest.split(" ", 1)[0].strip(",.!?;:-|")
        if after in _EXCLAMATION_SUBJECTS or after in EXCLAMATION_OPENS:
            clean = rest
            continue
        return clean
    return clean


def _an_exclamation_is_not_a_thing(clean):
    """The line without the surprise after a question word: "what on earth" is "what".

    "wtf" is expanded to "what" (lexicon.CHAT_SPEAK), which is the same repair from the other
    side: the question about the boiler, not a warning about the planet. This one holds for the
    phrase typed out - "what on earth do i do about my boiler".
    """
    return EXCLAIMED_AFTER_A_QUESTION.sub(r"\1", clean)


def strip_leaders(clause):
    """A clause without the filler it opens with."""
    start = 0
    while start < len(clause) - 1 and clause[start] in LEADERS:
        start += 1
    return clause[start:]


# The same rule for a line of text, for the readings that match a shape against the whole line and
# so never see past the filler. A child's name and age is read as a pair in "my daughters name is
# mia and shes 6", and behind a leader - "oh and my daughter is called mia", "and my sons called
# tom, hes 9" - not one of those shapes matched, because every one of them starts at "my". A
# leader can be stacked ("oh and", "so then"), so the rule is applied until it stops.
_LEADER_WORD = re.compile(r"^\s*([A-Za-z']+)\s*[,.;:!\-\u2014]*\s*")


def without_leaders(text):
    """The line without the filler it opens with: "oh and my son is 9" -> "my son is 9"."""
    said = str(text or "")
    while True:
        match = _LEADER_WORD.match(said)
        if not match or match.group(1).lower() not in LEADERS:
            return said
        rest = said[match.end():]
        if not rest.strip():
            return said
        said = rest


# A time word ends a place phrase: "when i was at the gym last week" says the gym, not the week.
_PLACE_STOP = frozenset("""last next this that yesterday today tomorrow tonight morning
    afternoon evening night week weekend month year hour minute monday tuesday wednesday
    thursday friday saturday sunday""".split())


# The words that put a place after them: a be-form ("i was in the garden") or a verb of going
# or starting ("it began at work").
_PLACE_LEADS = frozenset("""was were is am are been being s started starts began begins
    went go goes coming came got get stays stayed lived living working""".split())


# A question word opens a question of its own wherever it sits ("even after washing what helps"),
# so it ends the clause in front of it. A bare auxiliary does not: "when i was in the garden"
# holds one, and it is part of the clause, not the start of a new one.
_WH_QUESTIONS = frozenset("what why how when where who whose which".split())


def _clause_stop(norm, index):
    """The position just past the clause that opens at `index`.

    A clause ends where the next one may open: at a conjunction, or at a question of its own.
    "it started last summer after a picnic, what should i do" gives the picnic in the background
    and leaves the ask alone.
    """
    stop = index + 1
    while (stop < len(norm) and norm[stop] not in lexicon.CLAUSE_BREAKS
           and norm[stop] not in _WH_QUESTIONS):
        stop += 1
    return stop


def background_clause(norm):
    """The positions a clause saying WHEN or WHERE something happened takes up, or an empty set.

    A line that says when or where it happened gives that time or place in a clause of its own:
    "it started this morning when i was in the garden" is about whatever started. Only a clause
    with the line's own words before it counts; a line that opens on the subordinator asks about
    it ("when should i plant tomatoes"), a reporting verb in front of it makes it the thing being
    asked about ("no i mean where did i move from"), and a line with a subject of its own keeps
    its own clauses ("the garden flooded when it rained"). The clause stops where the next one
    opens, so it never covers an ask of its own ("my feet smell even after washing what helps").
    """
    norm = list(norm)
    for index, word in enumerate(norm):
        if not index or word not in lexicon.BACKGROUND_STARTS:
            continue
        if norm[index - 1] in REPORTING:
            continue
        return set(range(index, _clause_stop(norm, index)))
    return set()


# Words that open a clause giving the reason for the rest of the line. What is inside such a
# clause is why something happened, not what the line is about: "i cant sleep because my back
# hurts" is a sleep problem, and "my back has been killing me since i moved the sofa" is the back.
REASON_STARTS = frozenset("""because cause cos cus coz since""".split())


def reason_positions(norm):
    """The positions a clause giving the reason for the line takes up, or an empty set.

    Only a clause with the line's own words before it counts, so a line that opens on the
    subordinator ("since when do i need a licence") keeps its own reading.
    """
    norm = list(norm)
    for index, word in enumerate(norm):
        if not index or word not in REASON_STARTS:
            continue
        return set(range(index, _clause_stop(norm, index)))
    return set()


def background_positions(norm):
    """The positions in this line taken by words that only say WHERE it happened.

    Those words are not what the line is about: "it started at work in the garden centre" is
    about whatever started, not about the garden, and "it started this morning when i was in the
    garden" says the same with the place inside a when-clause. Only a place phrase counts - a
    preposition and the thing it introduces - so the rest of the clause keeps its meaning:
    "i get a rash when i eat strawberries" is a health line, and "how do i stop shaking before a
    talk" is about the talk.
    """
    norm = list(norm)
    skip = set()
    spans = []
    if norm[:1] == ["it"] and len(norm) > 1 and norm[1] in lexicon.START_VERBS:
        # A line that only reports when it began has no subject of its own, so every place in it
        # is where it happened: "it started at work in the garden centre". It stops where the
        # next clause opens, so a question after it keeps its own place.
        spans.append((0, _clause_stop(norm, 1), True))
    clause = background_clause(norm)
    if clause:
        spans.append((min(clause), max(clause) + 1, False))
    for start, stop, anywhere in spans:
        index = start
        while index < stop:
            if norm[index] not in lexicon.PLACE_PREPS:
                index += 1
                continue
            # In a when-clause a place follows a be-form or a verb of going or starting: "when i
            # was in the garden". "hand in my notice" and "what happens at security" have
            # something else in front of the preposition, so what follows is the thing acted on
            # or the thing happening, not a place.
            if not anywhere and index and not (norm[index - 1] in _PLACE_LEADS
                                               or index - 1 in skip):
                index += 1
                continue
            index += 1
            taken = 0
            while (index < stop and taken < 3
                   and norm[index] not in lexicon.CLAUSE_BREAKS
                   and norm[index] not in _PLACE_STOP
                   and norm[index] not in lexicon.PLACE_PREPS):
                skip.add(index)
                index += 1
                taken += 1
    return skip


def _the_measure_clause(clause):
    """True for a clause that is only a measure word, with or without its noun.

    "how long", "how much water", "how many hours sleep": the second word is the measure, and
    whatever follows it inside the clause is the thing measured, so the whole clause belongs to
    the ask that comes after it. A leading "and" or "so" is a leader, not part of the measure:
    "and how long do they stay on" is the same ask as "how long do they stay on".
    """
    stripped = strip_leaders(clause)
    return len(stripped) > 1 and stripped[0] == "how" and stripped[1] in HOW_DEGREE


def _asking(clauses, focus):
    """The clause that asks, with the measure word it was said with.

    `focus` is the clause carrying the ask, and for "how long do they stay on" that is "do they
    stay on": the measure word sits in the clause before it. A reader that reads the ask - the
    shape of the answer, or the thing the question attaches to - needs the word that says which
    measure is wanted, or a how-long reads as a yes/no. So the measure clause in front of the
    focus is joined to it here, once, rather than by every reader of the ask.

    Nothing else is added: a line with no measure word gets its focus back unchanged.
    """
    if not focus:
        return []
    at = None
    for index, clause in enumerate(clauses):
        if clause is focus:
            at = index
            break
    if at is None:
        for index, clause in enumerate(clauses):
            if clause == focus:
                at = index
                break
    if at and _the_measure_clause(clauses[at - 1]):
        return list(clauses[at - 1]) + list(focus)
    return list(focus)
