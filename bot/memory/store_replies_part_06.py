"""Part 6 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import datetime
import re
from ..compose import pick
from ..memory import name, others, plan_line, plan_sentence, recent, user
from ..memory import ack
from ..memory import condition
from ..memory import facts as extract
from ..knowledge import cooking
from ..memory.store_lines import (
    DENIAL_SAY, CORRECTED_SAY, WEEK, PLURAL_PEOPLE, DIET_RULES_OUT, MONTH_ORDER, PLURAL_PEOPLE,
    SAME_FACT_THEIR_OWN, CONDITION_RULES_OUT, CONDITION_KEEPS_DOWN,
)
from ..memory.relations import (
    _ask_gender, _gender_of, _one_age, _plural_person, the_pronoun_said_with_a_name,
)
from ..modules.memory_tables import WEEKDAY_WORD
from bot.memory.corrected import ASK_START, DATE_PHRASE, MONTH_WORD
from .store_replies_part_01 import (
    MEATLESS_DIET, _still_holding, _the_ask_after_a_statement, ASK_WORD, CANT_HAVE, CAN_HAVE,
    CAN_THEY_HAVE, DIET_ASK, DIET_HOW_TO, EAT_ASK, OTHER_ASK, OTHER_FACT, CAN_THEY_HAVE_A_FOOD,
    HELP_ASK, THEM,
)
from .store_replies_part_03 import (
    _diet_words, _allergy_is_their_food, _they, _pointed_at, _the_pronoun_is_one_of_the_two,
    _and_list, _does_not, _is_are, _what_the_food_has, _a_condition_rules_out, _diet_is_their_food,
    _no_diet, _their_pronoun,
)
from .store_replies_part_04 import (
    DIET_NOT_THEIRS, DIET_NEGATED, BARE_AGE_WHO, PEOPLE_WORDS, SOMEONE_ELSE, AGE_COMPARE,
    THE_AGE_GAP, WHICH_ONE_AGE_WHO, MONTH_SAID, WHICH_FIRST_ASK, WHICH_FIRST_WORDS, MORE_FOODS,
    LIMIT_LIKE, HEDGED, AN_ASK_AT_THE_END, NEGATIVE_TAIL, SAME_FACT_ABOUT, SAME_FACT_AGAINST,
    SAME_FACT_AGAINST_PRONOUN, NOT_A_NAME, AN_ANIMAL, A_SMALL_UNIT, _a_pronoun_word, _HE, _SHE,
    WHAT_ABOUT_A_FOOD, _a_limit_kept_for_them, _someone_else_named, ADVICE_NOT_A_FACT, ASKING_AGAIN,
    A_ASK_FRAME, A_HAVE_QUESTION, A_LIMIT_NAMED, STATES_A_LIMIT, THE_PRONOUN, A_MEAL_WORD,
)
from .store_replies_part_05 import (
    _a_diet_predicate, _diet_how,
)


def _denial_this_turn(text, memory):
    """The short line that says what the bot has just stopped believing, on the turn they said it."""
    gone = memory.get("denial") if isinstance(memory, dict) else None
    if not isinstance(gone, dict) or gone.get("said") != " ".join(str(text or "").lower().split()):
        return None
    others = ("allergies", "condition", "diet")
    if gone.get("who"):
        # Somebody else's take-back is theirs, not the speaker's: "Nuts back on the table, then."
        # answers an allergy the person typing never said they had, when the line was about
        # their son.
        items = [str(item) for item in (gone.get("allergies") or []) if str(item)]
        if not items:
            return None
        who = str(gone.get("who"))
        theirs = "your " + who if who in extract.RELATIONS else "them"
        # The line lifts a restriction, so it says the food is fine now: "Right - no eggs for your
        # daughter, then." reads as a new restriction on the person who just lifted one.
        things = items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
        return pick(["Right \u2014 " + things + " back on the table for " + theirs + ", then.",
                     "Good \u2014 no allergy to " + things + " for " + theirs + ", then.",
                     "Noted \u2014 " + things + " back on for " + theirs + "."],
                    memory if isinstance(memory, dict) else {})
    if gone.get("pets_died") and not any(gone.get(key) for key in others):
        return None  # a death is not a take-back to say back to them
    kept = extract.extract(text)
    if gone.get("pets_given") and not any(gone.get(key) for key in others + ("pets",)):
        return None  # one of a set, so "no cat, then" would say they have none left
    for key in ("allergies", "condition", "diet", "pets"):
        value = gone.get(key)
        if value:
            if key == "pets":
                given_line = ack.pet_given_away(text, memory)
                if given_line:
                    # The animal was given to a new home, so the line they get is the warm one and
                    # not the record being crossed out: "Right \u2014 no dog, then." is what a clerk
                    # says to somebody who has just told you they had to give their dog up.
                    return given_line
                # A pet is a record, so the line names the animal rather than the record.
                animals = sorted({str(pet.get("animal") or "pet")
                                  for pet in value if isinstance(pet, dict)})
                if not gone.get("pets_all") and animals and _still_holding(memory, animals):
                    continue  # one of several: "no cat, then" would say they have none left
                shown = "pets" if gone.get("pets_all") else " or ".join(animals) or "pets"
            else:
                shown = ", ".join(str(item) for item in
                                   (value if isinstance(value, list) else [value]))
            fresh = kept.get(key)
            if fresh and key in CORRECTED_SAY:
                now = ", ".join(str(item) for item in
                                (fresh if isinstance(fresh, list) else [fresh]))
                return CORRECTED_SAY[key].format(thing=now, Thing=now[:1].upper() + now[1:],
                                                old=shown)
            if key == "diet" and not MEATLESS_DIET.search(shown):
                # A diet that is itself a negation is put back positively: after "im not eating
                # meat" the take-back is "eating meat again", where "no more not eating meat"
                # is a sentence a person stumbles on.
                put_back = _a_diet_put_back(shown)
                if put_back:
                    return pick(["Right \u2014 " + put_back + " again, then.",
                                 "Got it \u2014 " + put_back + " again, then.",
                                 "Fair enough \u2014 " + put_back + " again, then."],
                                memory if isinstance(memory, dict) else {})
                # "meat is back on the table" is the right thing after "im not vegetarian any
                # more" and the wrong one after "im not doing keto any more", which says nothing
                # about meat.
                label = "dieting" if str(shown).strip().lower() == "on a diet" \
                    else _diet_words(shown)
                return pick(["Right \u2014 no more " + label + ", then.",
                             "Right, " + label + " is off, then.",
                             "Fair enough \u2014 no more " + label + ", then."],
                            memory if isinstance(memory, dict) else {})
            return DENIAL_SAY.get(key, "{Thing} \u2014 scratch that, then.").format(
                thing=shown, Thing=shown[:1].upper() + shown[1:])
    return None


def _asks_about_someone(low, text, memory=None):
    """Whether this line asks about a fact the store keeps for someone else.

    "what is he allergic to" and "what cant she have" are about the person the chat was just
    told about, and the store has that fact; read by nobody they fell to the encyclopedia entry
    for the word "allergy", which answers a question about the world to someone who asked about
    their son. Only a question is read this way: "he is allergic to nuts" is telling, and the
    person typing is not "he" (that is DIET_ASK's job). Which person the line is about is left to
    the reader in `_other_person_reply`, which knows the relations, the names and the pronoun:
    a line with nobody in it gets no answer from it.

    A line that states a fact and then asks something else is read on its question: "my son is 7
    and has a nut allergy, what can i pack him for lunch" asks about a lunch, and answering the
    allergy leaves the question the person actually asked on the floor. The split is only made
    where the store would have answered the line as it stands: "my wife is allergic to shellfish,
    can she eat prawns" is answered by the answer modules, which say why prawns are out, and
    splitting it here handed the store's thin diet receipt the turn.
    """
    whole = str(low or "")
    if not _asks_the_line(whole, text):
        return False
    ask = _the_ask_after_a_statement(whole, memory)
    if ask.strip() == whole.strip():
        return True
    return _asks_the_line(ask, text)


def _asks_the_line(low, text):
    """Whether this line, read whole, asks about a fact the store keeps for someone else."""
    low = str(low or "")
    if OTHER_ASK.search(low):
        return True
    if _asks_for_a_limit_not_advice(low) and (
            ASK_WORD.search(low) or ASK_START.search(low)
            or str(text or "").strip().endswith("?")):
        # "does she need to avoid anything" names the limit and asks for it; it is the same ask
        # as "is she vegan", and none of the sets below hold the word "avoid".
        return True
    if DIET_ASK.search(low) and not DIET_HOW_TO.search(low):
        return False  # "what's my diet" is about them, whatever is kept for someone else
    if not (EAT_ASK.search(low) or CANT_HAVE.search(low) or CAN_HAVE.search(low)
            or CAN_THEY_HAVE.search(low) or OTHER_FACT.search(low)):
        return False
    return bool(ASK_WORD.search(low) or ASK_START.search(low) or CAN_THEY_HAVE.search(low)
                or str(text or "").strip().endswith("?"))


def _both_food_facts(who, allergies, diet):
    """An allergy and a diet kept for the same person, said in one answer.

    A line can carry both - "my mum is allergic to nuts and she doesnt eat meat" - and the ask
    that follows ("what can my mum eat") used to be answered with the diet alone, because a diet
    kept for a person answers before the allergy does. The allergy is the fact that could hurt
    them, so it goes first and the diet follows it rather than replacing it.
    """
    said = _allergy_is_their_food(who, allergies, only=False)
    them = _they(who)
    them = them[:1].upper() + them[1:]
    rest = _diet_sentence(who, diet)
    for lead in ((("Your " + who) if who else "They"), "They"):
        if rest.startswith(lead):
            rest = them + rest[len(lead):]
            break
    return said + " " + rest


def _their_own_diet(line):
    """Whether the line says the diet as the person's own, now.

    "my wife is on a diet" names somebody else's, "i was on a diet last year" names one that is
    behind them and "im thinking about going on a diet" names one they have not started, so none
    of the three may come back as their own when they ask what diet they are on. A diet the store
    files from the line, or one the line takes back, is theirs.
    """
    if extract.extract(line).get("diet") or extract.denials(line).get("diet"):
        return True
    if DIET_NOT_THEIRS.search(line):
        return False
    # "i mostly eat low fat stuff" is how they eat now, though the store files no diet from it,
    # and it is the honest line to quote when they ask about a diet.
    return bool(re.search(r"\b(?:i|we)\b[^.?!]*\b(?:eat|eats|eating|drink|drinks|diet)\w*\b",
                          line, re.I))


def _a_diet_put_back(shown):
    """The thing they are back on, when the diet held was a negation, else None."""
    bare = DIET_NEGATED.match(" ".join(str(shown or "").split()))
    if not bare:
        return None
    thing = bare.group(1).strip()
    words = thing.split()
    if not words or len(words) > 4 or words[0].lower() in ("more", "longer", "any", "the"):
        return None
    return thing


def _about_people(low):
    """Whether a comparison with nobody named is about people at all.

    "who is older" is. "is my laptop older than my phone" is not, and neither is "am i older than
    the dog": a comparison against something needs a person on the other side of the "than".
    """
    if not (BARE_AGE_WHO.match(low) or PEOPLE_WORDS.search(low)):
        return False
    if re.search(r"\bthan\b", low):
        return bool(SOMEONE_ELSE.search(low))
    return True


def _age_compare(memory, low):
    """Two ages the store holds, compared out loud: "You are - 34 to your wife's 32."

    A comparison is not knowledge about the world: it is the two numbers they gave, against each
    other, and the store is the only place both are kept. The two are the people the line names
    ("who is older, my son or my daughter"), the person it names against the speaker ("am i
    older than my wife"), or, with nobody named, the speaker against the last person heard of.
    One of the two missing keeps the turn free, because half an answer here is a guess.
    """
    if not AGE_COMPARE.search(low):
        return None
    said = memory.get("understood") or {}
    if said.get("kind") not in (None, "question"):
        # "my wife is older than me" states the comparison instead of asking it: it is something
        # the store should keep, not a turn to answer with the two numbers back.
        return None
    aged = [e for e in others(memory) if e.get("age") is not None and e.get("who")]
    by_who = {}
    for entry in aged:
        by_who.setdefault((entry.get("who") or "").lower(), entry)
    # The people the line names decide the comparison: "am i older than my brother" is not
    # answered from the wife's age, so a person named with no age of their own keeps the turn
    # free rather than standing in for whoever the store heard about last.
    kin = getattr(extract, "KIN", extract.RELATIONS)
    words = [w.lower() for w in
             re.findall(r"\b(?:my|our)\s+(" + "|".join(kin) + r")(?:'s|s)?\b", low)]
    if [w for w in words if w not in by_who]:
        return None
    # "is my car older than my wife's" compares two cars: a thing they own is not a person, and
    # the wife's age is no answer to it.
    if [w for w in re.findall(r"\bmy\s+([a-z']+)", low) if w not in kin]:
        return None
    named = []
    for word in words:
        if by_who[word] not in named:
            named.append(by_who[word])
    mine = user(memory).get("age")
    me = {"who": "", "age": mine} if mine is not None else None
    if len(named) >= 2:
        sides = named[:2]
    elif named and me is not None:
        sides = [me, named[0]]
    elif not named and me is not None and aged and _about_people(low):
        pointed = _pointed_at(aged, low)
        if pointed is None:
            return None
        sides = [me, pointed]
    elif (not named and me is None and len(by_who) == 2
          and not re.search(r"\b(?:me|myself|mine|i|im)\b", low)
          and (BARE_AGE_WHO.match(low) or WHICH_ONE_AGE_WHO.match(low))):
        # "who is older" names nobody and the person has given no age of their own, so the
        # comparison is the two people the store holds an age for: after "my daughter is 4 and
        # my son is 7" that question is the whole of it, and it was answered with the search
        # hedge ("I can't look that up from here, sorry"). Two is the number the line can be
        # about; with three ages and nobody named it could be about either pair, so the turn
        # stays free rather than guessing.
        sides = list(by_who.values())
    elif (not named and me is None and len(by_who) == 2 and THE_AGE_GAP.search(low)
            and not re.search(r"\b(?:me|myself|mine)\b", low)
            and _the_pronoun_is_one_of_the_two(by_who, low)):
        # "how much older is he" asks for the gap between the two people the store holds, and
        # it fell to the search hedge because the line names nobody with "my": the pronoun is
        # the only person named. A pronoun that fits neither of the two is a question about
        # somebody the store has no age for, so it keeps the turn free.
        sides = list(by_who.values())
    else:
        return None
    try:
        ages = [int(s.get("age")) for s in sides]
    except (TypeError, ValueError):
        return None
    first, second = sides
    if ages[0] == ages[1]:
        if not first.get("who"):
            return "Neither of you - you're both " + str(ages[0]) + "."
        return "Neither of them - your " + str(first["who"]) + " and your " + str(second["who"]) + " are both " + str(ages[0]) + "."
    younger = re.search(r"\b(?:younger|youngest)\b", low) is not None
    winner, other = (0, 1) if (ages[0] > ages[1]) != younger else (1, 0)
    win, lose = sides[winner], sides[other]
    gap = abs(ages[0] - ages[1])
    years = "year" if gap == 1 else "years"
    if re.search(r"\bhow (?:much|many years)\s+(?:older|younger)\b", low):
        if not first.get("who"):
            return str(gap) + " " + years + ": you're " + str(ages[0]) + " and your " + str(second["who"]) + " is " + str(ages[1]) + "."
        return str(gap) + " " + years + ": your " + str(first["who"]) + " is " + str(ages[0]) + " and your " + str(second["who"]) + " is " + str(ages[1]) + "."
    theirs = "your" if not lose.get("who") else "your " + str(lose["who"]) + "'s"
    said = re.search(r"\b(youngest|eldest|oldest)\b", low)
    if said:
        word = "the " + said.group(1)
    else:
        word = "older" if ages[winner] > ages[other] else "younger"
    if not win.get("who"):
        return "You're " + word + " - " + str(ages[winner]) + " to " + theirs + " " + str(ages[other]) + "."
    return "Your " + str(win["who"]) + "'s " + word + " - " + str(ages[winner]) + " to " + theirs + " " + str(ages[other]) + "."


def _the_day_a_plan_names(plan):
    """How many days away the day a plan names is, or None when it names no day.

    A month is counted from the first of that month, or from the day of the month when the plan
    says one, and a month already behind us in the calendar is next year's: "in may" said in
    June is the May coming. A weekday on its own is that day in the week we are in, which is the
    only reading "the dentist is on tuesday and the doctor on friday" needs.
    """
    low = " ".join(str(plan or "").lower().split())
    today = datetime.date.today()
    found = MONTH_SAID.search(low)
    if found:
        short = MONTH_WORD.search(found.group(0))
        name = [m for m in MONTH_ORDER if m.startswith(short.group(0)[:3])] if short else []
        if not name:
            return None
        index = MONTH_ORDER.index(name[0]) + 1
        day = 1
        near = (re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\b[^.?!]{0,12}" + re.escape(name[0]),
                          low)
                or re.search(re.escape(name[0]) + r"\b[^.?!]{0,12}?\b(\d{1,2})(?:st|nd|rd|th)?\b",
                             low))
        if near and 1 <= int(near.group(1)) <= 31:
            day = int(near.group(1))
        for year in (today.year, today.year + 1):
            try:
                when = datetime.date(year, index, day)
            except ValueError:
                continue
            if when >= today:
                return (when - today).days
        return None
    day = WEEKDAY_WORD.search(low)
    if day and not DATE_PHRASE.search(low):
        return (WEEK.index(day.group(0)) - today.weekday()) % 7
    return None


def _the_plans_in_date_order(memory):
    """The things the store holds a day for, earliest first, each said the way it was kept.

    A plan is kept as the phrase they gave ("my dads birthday is in april"), but a birthday said
    with its day of the month is filed with the person instead ("my daughters birthday is on 12
    june" is `others(memory)`), and it is a dated thing in the store just the same. Both are put
    back into one sentence so the order can be read across them.
    """
    known = user(memory)
    held = [p for p in (known.get("plans") or []) if isinstance(p, str) and p.strip()]
    latest = known.get("plan")
    if isinstance(latest, str) and latest.strip() and latest not in held:
        held.append(latest)
    for entry in others(memory):
        who = str(entry.get("who") or "").strip()
        day = str(entry.get("birthday") or "").strip()
        if not (who and day):
            continue
        # A birthday that is also a plan is in the store twice, and the plan is the way they said
        # it; only the person's own record is used when no plan holds that birthday.
        if any("birthday" in plan.lower() and re.search(r"\b" + re.escape(who) + r"s?\b",
                                                        plan.lower())
               for plan in held):
            continue
        # "3 may" takes "on", a month on its own takes "in": "your daughters birthday is on 12
        # june", "your dads birthday is in april".
        link = "on " if re.search(r"\d", day) else "in "
        held.append("my " + who + "s birthday is " + link + day)
    dated = []
    seen = set()
    for plan in held:
        days = _the_day_a_plan_names(plan)
        if days is None:
            continue
        said = plan_sentence(plan, plan_line(memory, plan)).rstrip(" .!?")
        if not said:
            continue
        # A birthday is often kept twice, as a plan and on the person, and the same day said
        # twice is one day in the order.
        key = (days, said.lower())
        if key in seen:
            continue
        seen.add(key)
        dated.append((days, said))
    dated.sort(key=lambda pair: pair[0])
    return dated


def _which_comes_first(memory, low):
    """Two dated plans in the order the calendar puts them: "May comes first, then June".

    Every plan is said back in the words it was given in, so nothing here composes a sentence
    about their life: the store has the dates and the words, and this only reads them in order.
    """
    found = WHICH_FIRST_ASK.search(low)
    if not found:
        return None
    said = memory.get("understood") or {}
    if said.get("kind") not in (None, "question"):
        return None
    rest = (low[:found.start()] + " " + low[found.end():])
    if [w for w in re.findall(r"[a-z']+", rest) if w not in WHICH_FIRST_WORDS]:
        return None
    dated = _the_plans_in_date_order(memory)
    if len(dated) < 2:
        return None
    first = dated[0][1]
    later = [said[:1].lower() + said[1:] for _, said in dated[1:4]]
    if dated[1][0] == dated[0][0]:
        return "Both land on the same day: " + first[:1].lower() + first[1:] + " and " + \
            later[0] + "."
    tail = ", then ".join(later)
    return first + ", so that one is first \u2014 then " + tail + "."


def _a_food(value):
    """Whether the thing they can't have is food: "nuts" is, "penicillin" is not."""
    word = str(value or "").strip().lower()
    if not word:
        return False
    if word in MORE_FOODS:
        return True
    if any(word in family for family in cooking.FAMILIES.values()):
        return True
    if word in cooking.CHEESES or re.search(r"\b" + cooking.FOOD + r"\b", word):
        return True
    return False


def _said_a_limit(memory):
    known = user(memory)
    if known.get("allergies") or known.get("condition") or known.get("diet"):
        return True
    for turn in (memory.get("turns") or [])[-12:]:
        said = str((turn or {}).get("user") or "")
        if said and LIMIT_LIKE.search(said):
            return True
    return False


def _the_answer_the_ask_gets(text, memory):
    """What the cards say to this line as a question, or "" when they have nothing to say.

    A hedge is not an answer: "I don't know enough to answer that honestly" is the composer
    giving up, and a fact the store can say back is better than that.
    """
    from ..modules import answers  # noqa: PLC0415 - answers imports this package
    fresh = {"turns": [], "aside": True}
    for key in ("user", "others", "facts_log"):
        if key in memory:
            fresh[key] = memory[key]
    try:
        reply = answers.respond(text, fresh) or ""
    except Exception:  # noqa: BLE001 - a store that cannot ask is a store that says the fact
        return ""
    said = " ".join(str(reply).split())
    if not said or HEDGED.search(said):
        return ""
    return said


def _the_ask_beats_the_receipt(text, memory):
    """True when a line that ends on a question is a question the cards can answer.

    Asked of the cards rather than assumed, because a line whose ask they cannot answer
    ("my wife is vegan and we are going out, where can we eat") keeps its receipt, which is at
    least true, instead of falling through to a shrug.
    """
    if not isinstance(text, str) or "?" in text:
        return False
    if not AN_ASK_AT_THE_END.search(" ".join(text.split())):
        return False
    return bool(_the_answer_the_ask_gets(text, memory))


def _only_a_pointer(flat):
    """True for a line that only points at a fact: "she isnt", "my wife is not coeliac", "my
    wife is too".

    Those are the fact given to someone and taken back, not something to say back about the
    person: quoting one answers "what do you know about my wife" with "you told me your wife
    isnt" or "your wife is too".
    """
    if SAME_FACT_ABOUT.match(flat):
        return True
    for shape in (SAME_FACT_AGAINST, SAME_FACT_AGAINST_PRONOUN):
        match = shape.match(flat)
        if not match:
            continue
        rest = (match.groupdict().get("rest") or "").strip(" ?!.")
        if not rest or rest.split()[0] in NEGATIVE_TAIL:
            return True
    return False


def _a_name_in_a_pronoun_line(line):
    """The name a line gives for the person it only calls "his"/"her", or "".

    "his name is tom", "his names tom", "her name's meg": the person is the one named a line
    before, so the name is theirs and the store can say "Your husband is called Tom".
    """
    match = re.match(r"^\s*(?:and\s+|also\s+)?(?:his|her|their)\s+names?\s*"
                     r"(?:'s|is\s+|are\s+)?(?P<name>[a-z]{2,})\b", str(line or ""), re.I)
    if not match:
        return ""
    name = match.group("name").lower()
    if name in NOT_A_NAME:
        return ""  # "his name is not important", "her names still the same": no name there
    return name


def _person_clauses(who, entry):
    """The predicates about one person, subject left off: "is 32", "doesn't eat meat".

    They are kept as clauses rather than sentences so two facts join into one line - "Your
    sister is 32 and allergic to nuts" - the way a person says it, not a list of six sentences.
    """
    be = "are" if _plural_person(who) else "is"
    clauses = []
    age = entry.get("age")
    if isinstance(age, int) and not isinstance(age, bool):
        clauses.append(be + " " + str(age))
    allergies = [str(one) for one in (entry.get("allergies") or []) if one]
    if allergies:
        clauses.append(be + " allergic to " + _and_list(allergies))
    condition = entry.get("condition")
    if isinstance(condition, list):
        condition = str(condition[0]) if condition else ""
    if str(condition or "").strip():
        clauses.append(be + " " + str(condition).strip())
    diet = str(entry.get("diet") or "").strip()
    if diet:
        clauses.append(_a_diet_predicate(who, diet))
    dislikes = [str(one) for one in (entry.get("dislikes") or []) if one]
    if dislikes:
        clauses.append((_does_not(who) + " like " + _and_list(dislikes)).strip())
    return clauses


def _a_pronoun_age(memory, low):
    """The age of a person the chat only ever pointed at, or None.

    "she is 5 next month" files nothing: the store keeps facts about a named person, and an age
    about nobody is not one. The line still said it, so "how old is she" a turn later is a
    question about what the chat was told, and the answer is the age with the pronoun in it.
    Only the same pronoun is taken ("he" is not read off a line about "she"), and only a line
    inside the last few turns.
    """
    match = re.search(r"\b(she|he|they)(?:'s|s|'re|re)?\b", str(low or ""))
    if not match:
        return None
    pronoun = match.group(1)
    lines = []
    for turn in recent(memory, 5):
        said = turn.get("user") if isinstance(turn, dict) else None
        lines.append(said if isinstance(said, str) else "")
    for i in range(len(lines) - 1, -1, -1):
        said = lines[i]
        if not said.strip():
            continue
        # A kitten, a puppy or a budgie is not a person: an age said about one is said in a unit
        # this path cannot give back in years, and "we got a kitten" then "he is 10 weeks old" is
        # the kitten. A pet in play with a small-unit age is that pet, so the pet reader (or the
        # hedge behind it) keeps the chat. A pet and a birthday still to come ("we have a dog" /
        # "she is 5 next month") is left to this path: a person says a pet's age in weeks and a
        # person's in years, and that difference is the only thing in the words to go on.
        small = A_SMALL_UNIT.search(said.lower())
        if AN_ANIMAL.search(said) or (small and (AN_ANIMAL.search(lines[i - 1] if i else "")
                                                  or memory.get("pets"))):
            continue
        # A baby's age is said in weeks or months and the fact reader keeps it as one, so the
        # unit is said as it was said: "She is 18 months old." rather than a year it is not.
        if small and _a_pronoun_word(said) == pronoun:
            was = "are" if pronoun == "they" else "is"
            return (pronoun + " " + was + " " + small.group(1) + " " + small.group(2)
                    + " old.").capitalize()
        for entry in extract.extract(said).get("others") or []:
            if not isinstance(entry, dict) or entry.get("who"):
                continue
            # The reader keeps the pronoun on most shapes and not on others ("he turns 6 in
            # june"), so a line with no pronoun of its own is read off the words it was said in.
            theirs = str(entry.get("pronoun") or "") or _a_pronoun_word(said)
            if theirs != pronoun:
                continue
            age = entry.get("age")
            if isinstance(age, str) and age.strip().isdigit():
                age = int(age.strip())
            if not isinstance(age, int):
                continue
            # A pronoun is never a name: when the store holds this same age for the one animal
            # the chat has been told about, the age is said with the animal in it ("Your greyhound
            # is 2.") rather than with the pronoun it was pointed at with. The rule and why the
            # name has to be earned are in `relations.the_pronoun_said_with_a_name`.
            named = the_pronoun_said_with_a_name(memory, age)
            if named:
                return named
            return _one_age(pronoun, age, str(entry.get("turns") or ""))
    return None


def _the_same_fact_about_someone(text, memory):
    """The fact standing about the person typing, given to someone they name: (reply, note).

    "and my wife is too", "my son as well", "same for my partner": the "too" is the allergy, the
    diet or the condition already on record, so it is said with the fact in it and kept on the
    person named - which is what makes "is she allergic to anything" answerable afterwards.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return None
    low = " ".join(text.lower().split()).strip(" ?!.")
    if not low or len(low.split()) > 7:
        return None
    match = SAME_FACT_AGAINST.match(low)
    against = bool(match)
    by_pronoun = False
    if not match:
        match = SAME_FACT_AGAINST_PRONOUN.match(low)
        against = by_pronoun = bool(match)
    if not match:
        match = SAME_FACT_ABOUT.match(low)
    if not match:
        return None
    if by_pronoun:
        # "she isnt" is about the person the last note was written on, which is the only person the
        # chat has named since.
        last = _the_person_last_given_a_fact(memory)
        if not last:
            return None
        who, kind, value = last
        if not _the_fact_said_against(kind, value, match.groupdict().get("rest") or ""):
            return None
        _take_the_fact_back(memory, who, kind)
        return (_ive_taken_it_back(who, kind, value), None)
    who = (match.group("who") or match.group("more") or "").strip()
    if who not in PLURAL_PEOPLE and who.endswith("s") and who[:-1] in extract.RELATIONS:
        who = who[:-1]
    if not who:
        return None
    same = (match.groupdict().get("same") or "").strip().lower()
    if not against and not same and not low.startswith("same for"):
        # "my wife" on its own is not the allergy said again: only a "too", an "as well" or a
        # "same for" says the fact carries over. "what about my wife" is not one of them - it is
        # a question about her, and reading it as the fact invents one they never gave.
        return None
    held = _the_fact_on_record(memory)
    if not held:
        return None
    given = extract.extract(text)
    if any(given.get(key) for key in SAME_FACT_THEIR_OWN):
        return None  # the line states a fact of its own, which is a reader's job above
    for known in others(memory):
        if known.get("who") == who and any(known.get(key) for key in SAME_FACT_THEIR_OWN):
            return None  # the store already has this person's own facts; it says those instead
    kind, value = held
    if against:
        if match.groupdict().get("same", "").lower() == "neither":
            return None
        if not _the_fact_said_against(kind, value, match.groupdict().get("rest") or ""):
            return None
        return (_isnt_this_too(who, kind, value), None)
    return (_this_too(who, kind, value), {kind: list(value) if isinstance(value, list) else value,
                                          "who": who})


def _the_fact_said_against(kind, value, rest):
    """True when what follows "my wife isnt" is the fact itself, or nothing at all.

    "my wife isnt allergic", "my wife isnt coeliac", "my wife isnt either" are the fact said
    against. "my wife is not responding" and "my son isnt well today" are not: those are about the
    person, and a denial read on them would put a memory note where help is wanted.
    """
    words = str(rest or "").strip(" ?!.").split()
    if not words:
        return True
    if words[0].lower() in NEGATIVE_TAIL:
        return all(word.lower() in NEGATIVE_TAIL for word in words)
    first = words[0].lower()
    if kind == "allergies":
        return first == "allergic"
    head = str(value[0] if isinstance(value, list) else value).lower()
    return bool(head) and (first == head or head.startswith(first))


def _the_person_last_given_a_fact(memory):
    """The person a "too" last gave a fact to, with that fact: (who, key, value) or None."""
    for known in reversed(others(memory)):
        if not isinstance(known, dict) or not known.get("who"):
            continue
        for key in ("allergies", "diet", "condition"):
            if known.get(key):
                return str(known["who"]), key, known[key]
    return None


def _take_the_fact_back(memory, who, kind):
    """Take the fact off the person it was given to: "she isnt" after "and my wife is too"."""
    for known in reversed(others(memory)):
        if not isinstance(known, dict) or known.get("who") != who:
            continue
        known.pop(kind, None)
        left = {key for key in known if key not in {"who", "name", "turns"}}
        if not left:
            # Nothing is left on the person, so the entry goes: "what do you know about my wife"
            # cannot answer with a fact that was taken back.
            others(memory).remove(known)
        return


def _ive_taken_it_back(who, kind, value):
    if kind == "allergies":
        said = "allergic to " + _and_list(value)
    elif isinstance(value, list):
        said = str(value[0])
    else:
        said = str(value)
    negative = " aren't " if _plural_person(who) else " isn't "
    return ("Your " + who + negative + said + ", then - I've taken that back off "
            + ("them" if _plural_person(who) else "her" if who in _SHE else
               "him" if who in _HE else "them") + ".")


def _the_fact_on_record(memory):
    """The one fact about the person typing that a "too" can carry: (key, value) or None.

    An allergy comes first because it is the one that changes what they can be given, then a diet,
    then a condition. Nothing else is inherited: a "too" after "my budget is 300" is about money
    the other person may not share.
    """
    them = user(memory) or {}
    for key in ("allergies", "diet", "condition"):
        value = them.get(key)
        if value:
            return key, value
    return None


def _both_of_you(who):
    """The pair the fact is now kept for: two people, or a family said as one word."""
    return "all of you" if _plural_person(who) else "both of you"


def _this_too(who, kind, value):
    if kind == "allergies":
        return ("Your " + who + _is_are(who) + "allergic to "
                + _and_list(value) + " too, then - I'll keep it out for "
                + _both_of_you(who) + ".")
    if kind == "condition":
        return ("Your " + who + _is_are(who) + str(value[0] if isinstance(value, list) else value)
                + " too, then - I'll keep it in mind for " + _both_of_you(who) + ".")
    return ("Your " + who + _is_are(who) + str(value) + " too, then - I'll plan around "
            + _both_of_you(who) + ".")


def _isnt_this_too(who, kind, value):
    if kind == "allergies":
        said = "allergic to " + _and_list(value)
    elif isinstance(value, list):
        said = str(value[0])
    else:
        said = str(value)
    negative = " aren't " if _plural_person(who) else " isn't "
    return ("Your " + who + negative + said + ", then - good to know. It's just you I'll plan for.")


def _the_person_still_in_hand(low, memory):
    """The person with a limit the chat was last told about, on a food ask that names nobody."""
    if not WHAT_ABOUT_A_FOOD.match(low):
        return ""
    person = memory.get("person") if isinstance(memory, dict) else None
    who = str((person or {}).get("who") or "").strip() if isinstance(person, dict) else ""
    if not who:
        return ""
    for known in others(memory):
        if known.get("who") == who and _a_food_word(low, known):
            return who
    return ""


def _a_food_word(low, entry):
    """True when the line names a food the limit kept for that person rules out.

    The food does not have to be one the bot has a list of on its own: what makes it a food here is
    that it is a thing this person cannot have, which is the only thing the store would be saying.
    """
    ruled = []
    condition = str(entry.get("condition") or "").lower()
    if condition in CONDITION_RULES_OUT:
        ruled.append(CONDITION_RULES_OUT[condition])
    diet = str(entry.get("diet") or "").lower()
    if diet in DIET_RULES_OUT:
        ruled.append(DIET_RULES_OUT[diet][0])
    return any(_what_the_food_has(low, thing)[0] for thing in ruled)


def _other_person_reply(memory, low):
    """What the user told us about someone else, said back: "Your mum doesn't eat meat."

    The person is the one the ask names ("my son", "your mum"); a bare "she"/"he" is the person
    the retired entry is about, which is the one the user just gave a fact about.
    """
    undeclared = _the_person_still_in_hand(low, memory)
    bare_limit_ask = _a_bare_limit_ask(low, memory)
    if not (undeclared or OTHER_FACT.search(low) or EAT_ASK.search(low)
            or CANT_HAVE.search(low) or CAN_HAVE.search(low) or CAN_THEY_HAVE.search(low)
            or bare_limit_ask):
        return None
    if CAN_THEY_HAVE_A_FOOD.search(low) and not _a_limit_kept_for_them(low, memory) \
            and not bare_limit_ask:
        # Which foods have nuts in them is the cooking entries' reading, not the store's: an
        # allergy alone answers "what are they allergic to", not "can he eat cake".
        return None
    who = _someone_else_named(low, memory) or undeclared
    entry = None
    for known in others(memory):
        if known.get("who") == who:
            entry = known
            break
    if entry is None:
        offered = _did_you_mean_the_person(memory, low)
        if offered:
            return offered
        # "what is my mum allergic to" when the mum was only mentioned in passing gets an honest
        # answer about the mum, not "you haven't mentioned an allergy to me". A line that asks
        # for advice ("what should my mum eat after the op") is a real question and is left to
        # the modules that answer those.
        if _a_bare_limit_ask(low, memory):
            # Before HELP_ASK, because "what can she not eat" has "can" in it and would be read
            # as a request for help. It is the same ask as "is she vegan" from the other side.
            return _nothing_kept_about_them(low)
        if HELP_ASK.search(low):
            return None
        if not who:
            # A bare "she"/"he"/"they" with nobody in the chat behind it: the line asks about a
            # person the store was never told about, and what it has kept is nothing. That is
            # still an answer, and the only true one. Left unsaid, these lines fell to the
            # composer's search hedge - "I don't know enough to answer that honestly. A search
            # should sort you out" - which points at the open web for a fact that can only come
            # from the person themselves, and it was the reply to "what was she allergic to
            # again", "is she vegan" and "what meat did i say he doesnt eat". The offer is the
            # part that helps: the fact is one line away, and the next line is where it is kept.
            # The first person is not this case ("do i have any allergies" is the store's own
            # already, and it says "you haven't mentioned an allergy to me"), so the line has to
            # be about somebody else before the store speaks for them.
            if _nobody_else_kept(memory) and _the_pronoun_in(low) \
                    and _asks_for_a_limit_not_advice(low):
                return _nothing_kept_about_them(low)
            return None
        if OTHER_FACT.search(low):
            return "You haven't told me about an allergy of your " + who + "."
        return _no_diet(who)
    if OTHER_FACT.search(low):
        allergies = entry.get("allergies") or []
        owner = ("Your " + who) if who else "They"
        if not allergies:
            return ("You haven't told me about an allergy of " + (("your " + who) if who else "theirs")
                    + ".")
        return owner + _is_are(who) + "allergic to " + ", ".join(allergies) + "."
    diet = entry.get("diet")
    allergies = entry.get("allergies") or []
    condition = entry.get("condition")
    if condition and (undeclared or CANT_HAVE.search(low) or CAN_HAVE.search(low)
                      or EAT_ASK.search(low) or CAN_THEY_HAVE.search(low)):
        # "my son is coeliac" then "what can he eat" / "can he have bread": the condition kept for
        # him is a food fact too, and it names the food it rules out for the two conditions that
        # rule one out. Said before the diet, because a condition is the sharper of the two.
        said = _condition_is_their_food(who, condition, low)
        if said:
            if diet and not allergies:
                return said + " " + _diet_sentence(who, diet)
            return said
    if diet and (undeclared or CANT_HAVE.search(low) or CAN_HAVE.search(low)
                 or CAN_THEY_HAVE.search(low) or EAT_ASK.search(low)):
        # "what cant she have" wants the food the diet rules out, not the diet's name again - and
        # the name again is the same sentence the store said last turn, so it would be passed over
        # and the turn handed to whatever else proposed. A plain "what does she eat" is the diet
        # as it was said ("Your mum doesn't eat meat."), so only a diet that names one food is
        # turned round into that food.
        ruled = _diet_is_their_food(who, diet, low, plain=bool(EAT_ASK.search(low)))
        if ruled and not allergies:
            return ruled
    if diet and allergies:
        # An allergy kept beside a diet belongs in the answer too: the diet on its own answered
        # the ask and left the allergy behind, and the allergy is the one that could hurt them.
        return _both_food_facts(who, allergies, diet)
    if not diet:
        allergies = entry.get("allergies") or []
        if allergies:
            # The allergy is a food fact, so "what can she eat" is answered from it rather than
            # with "you haven't told me what your mum eats" straight after she said she cannot
            # eat shellfish.
            return _allergy_is_their_food(who, allergies, low=low)
        condition = entry.get("condition") or []
        if condition and _a_condition_rules_out(condition):
            # A condition that rules a food out is a food fact the knowledge base can cook with:
            # "my sister is lactose intolerant" then "what can she have for breakfast" is a
            # breakfast question, and the honest answer says nothing a meal answer would not, so
            # it is left to the modules that answer meals. Before, the store claimed she had told
            # it nothing about her eating, one line after she had. A condition that names its food
            # is answered above, so this is only the condition the store cannot turn into a food.
            return None
        return _no_diet(who)
    return _diet_sentence(who, diet)


def _asks_for_a_limit_not_advice(low):
    """True for a line that asks for a kept fact about somebody's allergies or diet."""
    text = str(low or "")
    if ADVICE_NOT_A_FACT.search(text):
        return False
    if STATES_A_LIMIT.search(text) and not A_HAVE_QUESTION.search(text) \
            and not A_ASK_FRAME.search(text):
        return False
    if re.search(r"\bnot\s+eat\b", text):
        # "what can she not eat" asks for the limit from the other side, and it is the same ask as
        # "is she vegan". The positive "what does he eat" is not this line: it is answered by
        # saying they would have to be asked, and it keeps its own answer.
        return True
    if CANT_HAVE.search(text):
        # "what can she not eat" asks for the same limit as "is she vegan", from the other side.
        # A positive "what does he eat" is not this line: that one is answered by saying they
        # would have to be asked, and it keeps its own answer.
        return True
    return bool(A_LIMIT_NAMED.search(text) or ASKING_AGAIN.search(text))


def _the_pronoun_in(low):
    """The pronoun the line named its person with: "she", "he", "they", or "" for none."""
    found = [m.group(1).lower() for m in THE_PRONOUN.finditer(str(low or ""))]
    for word in found:
        if word in ("she", "her", "hers"):
            return "she"
        if word in ("he", "him", "his"):
            return "he"
    for word in found:
        if word in ("they", "them", "their"):
            return "they"
    return ""


def _nobody_else_kept(memory):
    """True when the store holds no fact about anybody else.

    Read, not called through `others()`: that one files an empty list into the memory it is asked
    about, and a store that was never asked about another person then carries an "others" key for
    the rest of the chat. It is a side effect no reader should be able to cause by looking, and
    measured on the deck it moved 12 turns of conversations that had nothing to do with it.
    """
    if not isinstance(memory, dict):
        return True
    kept = memory.get("others")
    return not (isinstance(kept, list) and kept)


def _a_bare_limit_ask(low, memory):
    """A limit asked for about somebody named only by a pronoun, with nobody in the chat behind it.

    "is she vegan", "does she have any allergies" and "what can she not eat" name a person the
    store could look up only if the chat had ever said who "she" is. It has not, so the asks that
    need a relation never took the line, and the composer's search hedge answered a question about
    the person in front of the bot: "That's beyond what I know well, sorry. Searching for it will
    turn up better sources". Nothing kept is itself the answer, and `_nothing_kept_about_them`
    says it; this is the gate that lets the line reach it.
    """
    text = str(low or "")
    # A line that also says what it is for - "is she vegan, shes coming for dinner" - is asking
    # for a meal, and the answer modules have a real one; the store's "you haven't told me" is
    # only the right answer to the bare ask.
    if A_MEAL_WORD.search(text):
        return False
    return bool(_nobody_else_kept(memory) and _the_pronoun_in(text)
                and _asks_for_a_limit_not_advice(text))


def _nothing_kept_about_them(low):
    """What the store says when a limit is asked about a person it was never told about.

    Nothing kept is an answer, and it is the only one that is true. The offer matters as much as
    the admission: the next line is where the fact comes in, and the bot says so.
    """
    pronoun = _the_pronoun_in(low)
    if OTHER_FACT.search(str(low or "")):
        theirs = {"she": "hers", "he": "his"}.get(pronoun, "theirs")
        return ("You haven't told me about an allergy of " + theirs
                + " yet \u2014 what is it? I'll keep it out of anything I suggest.")
    if pronoun in ("she", "he"):
        return ("You haven't told me how " + pronoun + " eats yet \u2014 what does " + pronoun
                + " avoid? I'll plan the meals round it.")
    return ("You haven't told me how they eat yet \u2014 what do they avoid? I'll plan the meals "
            "round it.")


def _did_you_mean_the_person(memory, low):
    """The one person the store holds, offered back when a pronoun fits nobody.

    "my mum is allergic to shellfish" then "what is he allergic to" is a slip of the keys nine
    times out of ten, and the definition of an allergy is no answer to it. The store asks rather
    than guesses which person was meant: "Did you mean your mum? She is allergic to shellfish."
    A second person in the store means the pronoun has a real choice to make, so this stays free.
    """
    held = [e for e in others(memory) if isinstance(e, dict) and e.get("who")]
    if len(held) != 1:
        return None
    # The offer answers a pronoun that fits nobody, so the line has to have one. "what is an
    # allergy" names no person and points at none: the one person in the store is not a typo
    # there, and "Did you mean your mum?" is no answer to a question about allergies.
    if not THEM.search(low):
        return None
    who = str(held[0].get("who"))
    said = ""
    if OTHER_FACT.search(low) and held[0].get("allergies"):
        said = "Your " + who + _is_are(who) + "allergic to " + ", ".join(held[0]["allergies"]) + "."
    elif EAT_ASK.search(low) and held[0].get("diet"):
        said = _diet_sentence(who, held[0]["diet"])
    elif EAT_ASK.search(low) and held[0].get("allergies"):
        said = _allergy_is_their_food(who, held[0]["allergies"])
    if not said:
        return None
    gender = _gender_of(who)
    pronoun = "She" if gender == "she" else "He" if gender == "he" else "They"
    tail = said[len("Your " + who):]
    if pronoun == "They":
        # "Your partner is allergic to shellfish" said again with a pronoun takes "are".
        tail = re.sub(r"^(\s+)is\b", r"\1are", tail)
        tail = re.sub(r"^(\s+)does not\b", r"\1do not", tail)
    ask_gender = _ask_gender(low)
    if ask_gender and gender and gender != ask_gender:
        # The ask says "he" about a person the store knows as a she, so the mismatch is said out
        # loud instead of answering a question they did not ask.
        him = "her" if gender == "she" else "him"
        return ("I've only got your " + who + " down, and " + pronoun.lower() + tail
                + " Did you mean " + him + "?")
    return "Did you mean your " + who + "? " + pronoun + tail


def _condition_is_their_food(who, condition, low=""):
    """What the condition kept for a person means for their plate, or None when it means nothing.

    "my son is coeliac" then "what can he eat" was a search hedge, because the store had kept
    the condition and had no sentence for it: the food it rules out is the answer, and it is the
    same answer the diet reader gives for "gluten-free". The tail is the same honest limit the
    allergy answer carries, so nothing is claimed beyond the one fact the person gave.
    """
    said = " ".join(str(low or "").lower().split())
    low = " ".join(str(condition or "").lower().split())
    owner = ("Your " + who) if who else "They"
    tail = " \u2014 that's all I have on food for " + _their_pronoun(who) + "."
    ruled = CONDITION_RULES_OUT.get(low)
    named, thing = _what_the_food_has(said, ruled) if (ruled and said) else ("", "")
    if named:
        # "can he have cheese" is answered about the cheese: a person asking about one food has
        # that food in their hand, and "nothing with dairy in it" leaves them to work it out.
        return (named[:1].upper() + named[1:] + " has " + thing + " in it, and " + owner.lower()
                + _is_are(who) + low + ".")
    if ruled:
        return (owner + _is_are(who) + low + ", so nothing with " + ruled + " in it" + tail)
    watched = CONDITION_KEEPS_DOWN.get(low)
    if watched:
        return (owner + _is_are(who) + low + ", so keep the " + watched + " down" + tail)
    if low:
        # A condition with no food of its own is still said back, so the ask is answered with
        # what the store knows instead of a hedge about a fact it was told a turn ago.
        return owner + _is_are(who) + low + tail
    return None


def _diet_sentence(who, diet):
    """A diet said as a sentence: "Your mum doesn't eat meat.", "They're vegetarian."."""
    if str(diet).startswith("eats ") or str(diet).startswith("no "):
        # "eats fish" is what a restriction becomes when the person puts it back, and it is a
        # sentence of its own: "Your son is eats fish." is not one.
        if who:
            return "Your " + who + " " + _a_diet_predicate(who, diet) + "."
        return "They eat " + str(diet)[5:] + "." if str(diet).startswith("eats ") \
            else "They don't " + _diet_how(diet) + " " + str(diet)[3:] + "."
    if who:
        return "Your " + who + _is_are(who) + str(diet) + "."
    return "They're " + str(diet) + "."
