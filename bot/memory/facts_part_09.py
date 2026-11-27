"""Part 9 of 11 of the module, split out of `facts`.

Everything here is re-exported from `facts`, so callers import it from there as before.
"""
import re


from . import taste
from .facts_part_01 import (
    CLAUSE_EDGE, NOT_NAMES, NOT_NAMES_EXTRA, NOT_PLACES, EVERYTHING, NAME_WORD, NOT_A_NAME,
    INCOME_PERIOD, INCOME_QUALIFIER,
)
from .facts_part_02 import (
    BABY_AGE, BIRTHDAY_PRONOUN, GROUP_NAMED_AGES, GROUP_NAMED_NAMES, HE, HOW_THEY_FEEL,
    MONTH_OLD_BABY, PRONOUN_AGE, RELATION_AGE, RELATION_BARE_NAME, RELATION_HAVE_NAME,
    RELATION_NAME, RELATION_NAMED_AGE, RELATION_PAIR_NAMES, RELATION_POSSESSIVE_AGE,
    RELATION_POSSESSIVE_NAME, RELATION_WHOS_AGE, SHE, THE_PLACE_AGE, _A_WORD_FOR_A_PERSON,
    _a_birthday_date, a_person_word, a_stated_number, CHAINED_RELATION_AGE, RELATIONS, _the_person,
    COMPOUND_AFTER, COMPOUND_THAT_IS_THEIRS, IN_LAW_AFTER,
)
from .facts_part_03 import (
    JOB_AS_A, JOB_MINE, JOB_OWN_VOICE, JOB_WANTED, JOB_AFTER, JOB_APPOSITIVE, JOB_BECOME, JOB_FRAME,
    JOB_GOT_AN_EMPLOYER, JOB_GOT_AT, JOB_GOT_FRAME, JOB_STOP, JOB_WAS, JOB_WORK, POSSESSION,
    SELF_JUDGEMENT, WAS_NOT_A_JOB, a_place_that_employs, CORRECTION, CORRECTION_MAKE,
    CORRECTION_PAIR, CORRECTION_SAID,
)
from .facts_part_04 import (
    _finish, _tidy, _tidy_a_titled_name, JOB_TAIL_PLACE, _first_tail, _is_a_judgement_phrase,
    _the_correction_named_a_thing, _the_role, without_the_moment, SELF_AS_A_ROLE, is_a_judgement,
)
from .facts_part_05 import (
    stated_not_asked, CLAUSE_BREAK, PRONOUN_SUBJECT,
)
from .facts_part_06 import (
    AGE_TAIL, DIET_GROUP, OTHER_BIRTHDAY, _month_age_after, KID_AGES, KID_AGES_AFTER_A_COMMA,
    KID_GROUP, KID_ONE_BY_ONE, _ages_held, _children_by_year_old, figures_as_digits, KID_ASKING,
    KID_COUNT, KID_COUNT_AND, KID_ELSEWHERE, KID_NONE, KID_NONE_NOT_AFTER_ALL, KID_NUMBERS,
    AGE_TO_COME, A_LIST_OF_AGES, KID_ADULTS_AGES, KID_AGES_NOT, KID_COUNT_AGES, KID_GROUP_AGES_ARE,
    _keep_the_ages, _kids_named_with_ages, _relation_before,
)
from .facts_part_07 import (
    _name_after_a_title, _not_a_name, _may_be_a_name, subject, A_RELATION_OWNED, SOMEONE_ELSE_HAS,
)
from .facts_part_08 import (
    _bare_name, _was_names_a_role, _the_clause_before,
)


def _relation_facts(text):
    """A relation's own name and age: [{"who": "mum", "name": "Janet", "age": "72"}]."""
    found = []
    text = stated_not_asked(text)
    if not text:
        return found

    def entry(who, name=""):
        """The entry for this person: one word for the relation is one person, unless a second
        name is said for it.

        "my son jack is 6 and my son sam is 9" has two sons, and the word they are both filed
        under is the same word, so filing by the word alone kept one entry whose name was the
        first and whose age was the last - one child made out of two. A name said for the
        relation is what tells the two apart, and a fact with no name of its own still goes on
        the person the chat just named.
        """
        who = a_person_word(who)
        for known in found:
            if known.get("who") != who:
                continue
            if name and known.get("name") and str(known["name"]).lower() != str(name).lower():
                continue
            return known
        made = {"who": who}
        found.append(made)
        return made

    for match in RELATION_POSSESSIVE_AGE.finditer(text):
        entry(match.group("who").lower())["age"] = int(match.group("age"))
    for pattern in (RELATION_NAME, RELATION_POSSESSIVE_NAME, RELATION_NAMED_AGE,
                    RELATION_HAVE_NAME):
        for match in pattern.finditer(text):
            name = _finish(match.group("name"))
            if not name or _not_a_name(match.group("name"), strict_ly=False):
                continue
            if not _name_after_a_title(match.group("name")):
                continue
            if str(match.group("name")).lower() in _A_WORD_FOR_A_PERSON:
                # "my eldest son is 8": the word after the person is another word for a person,
                # not a name, and reading it as one filed an "eldest" beside the son.
                continue
            # Main's `_tidy_a_titled_name` is the newer reading of the same name; this branch's
            # change is the name as the key for two people with one word, which is elsewhere.
            entry(match.group("who").lower(), _tidy(name)).setdefault(
                "name", _tidy_a_titled_name(name))
    for match in RELATION_BARE_NAME.finditer(text):
        name = _bare_name(match.group("name"))
        if name:
            entry(match.group("who").lower(), name).setdefault("name", name)
    for match in RELATION_PAIR_NAMES.finditer(text):
        # Two names under two people are kept as the pair they were said as: "my mum and dad are
        # dave and sue" does not say which name is whose, and the order is only a guess, so
        # pairing them off would file a fact about their mother they never gave. Each name with
        # its own age ("my kids are ada 7 and sam 4") is the line doing the pairing, and that is
        # read below.
        names = [_bare_name(match.group("name1"), pair=True),
                 _bare_name(match.group("name2"), pair=True)]
        if all(names):
            who1 = match.group("who1").lower()
            who2 = match.group("who2").lower()
            found.append({"who": who1 + " and " + who2, "names": names})
    for match in GROUP_NAMED_NAMES.finditer(text):
        said = [word for word in re.split(r"\s*(?:,|and)\s*", match.group("rest")) if word]
        names = [_bare_name(word, pair=True) for word in said]
        if len(names) < 2 or not all(names):
            continue
        who = match.group("who").lower()
        if match.group("who2"):
            who = who + " and " + match.group("who2").lower()
        found.append({"who": who, "names": names})
    for match in GROUP_NAMED_AGES.finditer(text):
        pair = re.findall(r"([A-Za-z][A-Za-z'-]{1,19})\s+(\d{1,3})", match.group("rest"))
        if len(pair) < 2:
            continue
        named = [(said, _bare_name(said, pair=True), age) for said, age in pair]
        if not all(name for _, name, _ in named):
            continue  # one word that is not a name makes the whole list somebody else's line
        for who, name, age in named:
            made = {"who": match.group("who").lower(), "name": name, "age": int(age)}
            if made not in found:
                found.append(made)
    for match in BABY_AGE.finditer(text):
        # The unit decides which fact it is, because a baby's age is kept in months: "4 months"
        # said back as "4" would read as four years.
        # The age is filed under the word the line used for the baby, because that is the word
        # every list of people the asks read is looked up by: "our little one is 10 months" then
        # "how old is our little one" found nobody when it was filed under "baby".
        made = entry(str(match.group("who") or match.group("little") or "baby").lower())
        if str(match.group("unit")).lower().startswith("month"):
            made.setdefault("months", int(match.group("age")))
        else:
            made.setdefault("age", int(match.group("age")))
    for match in MONTH_OLD_BABY.finditer(text):
        # The age is the name of the baby here, with no "is" after it: "our 7 month old", "my 18
        # month old". Nobody kept it, so "how old is he" after "our 7 month old is waking every
        # two hours" got a search hedge. A baby is what the line is about, and months is how the
        # age is kept.
        entry("baby").setdefault("months", int(match.group("age")))
    for pattern in (RELATION_AGE, THE_PLACE_AGE, RELATION_NAMED_AGE, RELATION_WHOS_AGE):
        # A clause ("my brother whos 30 is coming to stay") ends where the next verb starts, so
        # the age is read when what follows it is not a unit, rather than only when it is one of
        # the words an age ends with. The plain shapes keep the short list: "my son is 8 grams"
        # is a weight and not a birthday.
        clause = pattern is RELATION_WHOS_AGE
        for match in pattern.finditer(text):
            # The number is an age only when what follows it is the end of the fact or the words
            # an age is said with. Without this, "my mum is 68 kilos" matched the 6 in 68 and filed
            # a six-year-old, because 68 itself is followed by a unit and the pattern could take a
            # shorter number to get past it.
            rest = text[match.end():]
            months = _month_age_after(text, match.end())
            if months:
                # A baby's age is said in months and kept that way: "18 months old" is not
                # eighteen years old, and denying it on the next turn is worse than either.
                entry(match.group("who").lower()).setdefault("months", int(match.group("age")))
                continue
            if not (clause or AGE_TAIL.match(rest)):
                continue
            # The age belongs to the person the clause names, not to whoever shares their word
            # for the relation: "my son jack is 6 and my son sam is 9" is six and nine, not two
            # sons of nine. It is kept as a number, the way every other reader files an age: as a
            # string it was a fact the store held and the ask could not read, so "how old are my
            # kids" denied an age it had just been told.
            named = match.groupdict().get("name")
            known = (entry(match.group("who").lower(), _tidy(named)) if named
                     else entry(match.group("who").lower()))
            known.setdefault("age", int(match.group("age")))
    for tasted in taste.read_other(text):
        # What one of them likes is a fact about that person, filed on them like an age: "my
        # sister loves cooking" left the sister in the store with nothing about her in it, and
        # "what does my sister like" was a search hedge about somebody the chat had just named.
        thing = tasted.get("thing")
        if not thing:
            continue
        key = "likes" if tasted.get("how") == "yes" else "dislikes"
        if tasted.get("eaten") and set(str(thing).split()) & DIET_GROUP:
            # "she doesnt eat meat" is her diet, which the line's own reader has. Only a whole
            # food group is a diet, though: "wont eat vegetables" is a fussy eater rather than a
            # way of eating, and "my daughter wont eat peas" is one food she will not eat, which
            # the diet reader leaves alone (it wants a group). The store kept nothing at all
            # then, so the person had to say it twice and "what wont she eat" was answered "You
            # haven't told me what your daughter eats". A food they will not eat is a taste like
            # any other, so it goes on the list the dislike ask reads.
            continue
        who = tasted.get("who")
        if who:
            known = entry(who)
        else:
            known = next((made for made in found
                          if made.get("pronoun") == tasted.get("pronoun")
                          and not made.get("who")), None)
            if known is None:
                known = {"pronoun": tasted.get("pronoun") or ""}
                found.append(known)
        held = known.setdefault(key, [])
        if thing not in held:
            held.append(thing)
    for match in OTHER_BIRTHDAY.finditer(text):
        # Whose birthday it is: the relation the line names ("my mums birthday") or the pronoun,
        # which the store folds onto the person the chat is about the way it does an age.
        date = _a_birthday_date(match.group("date"))
        if not date:
            continue
        said_who = (match.groupdict().get("who") or "").lower()
        said_pronoun = (match.groupdict().get("pronoun") or "").lower()
        if said_who:
            known = entry(said_who)
        else:
            pronoun_word = BIRTHDAY_PRONOUN.get(said_pronoun, said_pronoun)
            person = _the_person_the_pronoun_is(text, match.end(), pronoun_word)
            if person:
                known = entry(person)
            else:
                known = next((made for made in found
                              if made.get("pronoun") == pronoun_word and not made.get("who")), None)
                if known is None:
                    known = {"pronoun": pronoun_word}
                    found.append(known)
        known.setdefault("birthday", date)
    pronoun = PRONOUN_AGE.search(text)
    if pronoun and a_stated_number(pronoun.group("age")) is None:
        pronoun = None
    if pronoun and pronoun.group("come"):
        # Only what the line says in the same breath as the age: "shes turning 40. she hates
        # being the centre of attention" is two thoughts, and the second is not about the 40.
        same_breath = re.split(r"[.!?]", text[pronoun.end():], 1)[0]
        if HOW_THEY_FEEL.search(same_breath):
            pronoun = None
    if pronoun and _month_age_after(text, pronoun.end()):
        # The same month age with only a pronoun: "shes 18 months old" after "my daughter...".
        fits = SHE if pronoun.group("who").lower() == "she" else HE
        for known in found:
            if "age" not in known and "months" not in known and known.get("who") in fits:
                known["months"] = a_stated_number(pronoun.group("age"))
                break
        else:
            # Nobody in this line took the age, which is not the same as nothing in `found`: a
            # line can hold a taste about the same person ("shes seven and loves dinosaurs") and
            # the taste entry is not where the age belongs, so the age was dropped and
            # "what age is she" denied an age the chat had just been given.
            if not any("months" in made for made in found):
                found.append({"months": a_stated_number(pronoun.group("age")),
                              "pronoun": pronoun.group("who").lower()})
    elif pronoun and AGE_TAIL.match(text[pronoun.end():]):
        # The line has to name somebody for "she" to be them: a bare "she is 72" with nobody
        # named is not a fact about anyone the store can name. And the pronoun has to fit: "my
        # mum is called janet and he is 72" is somebody else's 72, not the mum's.
        word = pronoun.group("who").lower()
        # The number is kept as one, the way every other reader files an age: as a string it was
        # a fact the store held and the answers could not read, so "my son is called tom" then
        # "he is 6" then "what should i get him" gave the grown-up list, and a birthday said
        # after it ("she turns 8 in june") replaced the age she is now instead of sitting beside
        # it. A month age above has always been read as a number.
        # "they" is nobody in particular, so it fits no relation and stands on its own.
        fits = SHE if word == "she" else HE if word == "he" else frozenset()
        for known in found:
            if "age" not in known and known.get("who") in fits:
                known["age"] = a_stated_number(pronoun.group("age"))
                break
        if not any("age" in made for made in found):
            # Nobody is named in this line, so the age is filed against the pronoun and the
            # store fills in the person the chat is about: "my mum is coming to stay next
            # weekend" then "shes 78 and doesnt walk far" is the mum's age, and without this
            # nothing held the two together and "how old is my mum" said she had never said.
            word = pronoun.group("who").lower()
            person = _the_person_the_pronoun_is(text, pronoun.start(), word)
            if person:
                # The line named them before the pronoun ("my mum, shes 60"): the age is theirs
                # rather than the store's guess at who "she" is.
                found.append({"who": person, "age": a_stated_number(pronoun.group("age"))})
            else:
                found.append({"age": a_stated_number(pronoun.group("age")), "pronoun": word})
    return [known for known in found if len(known) > 1 or "who" not in known]


def _job_as_a(text):
    """The "job as a ..." lines that name the speaker's own job, as their matches.

    "i got a new job as a nurse" says what they do, while "my brother got a job as a chef" is
    his job and "i want a job as a teacher" is one they have not got: only a clause that opens
    in their own voice, with no wanting in it and nobody else named, files a job.
    """
    found = []
    for match in JOB_AS_A.finditer(text):
        clause = CLAUSE_EDGE.split(text[:match.start()])[-1]
        if JOB_WANTED.search(clause) or _people(clause):
            continue
        if not (JOB_OWN_VOICE.search(clause) or JOB_MINE.search(clause)):
            continue
        found.append(match)
    return found


def _job_and_city(text, name=None, question=False):
    job = city = None
    frame = ""
    if name:
        at = text.lower().find(name.lower())
        if at != -1:
            text = text[at + len(name):]
    matches = (list(JOB_AFTER.finditer(text)) or list(JOB_BECOME.finditer(text))
               or list(JOB_WORK.finditer(text)) or list(JOB_WAS.finditer(text))
               or _job_as_a(text) or list(JOB_GOT_AT.finditer(text)))
    if not matches and not POSSESSION.search(text):
        # The appositive is for a person naming what they do; after a having word the same shape
        # names the thing they have.
        matches = [match for match in JOB_APPOSITIVE.finditer(text)
                   if not _the_correction_named_a_thing(text, match)]
        if question:
            # A question with only an appositive is asking about the bot, not saying what the
            # person does: "what are you then, a robot?" filed `robot` as their job, and the next
            # turn told them "you're a robot in Leeds". The noun is theirs only when the line
            # puts them first ("call me jess, a nurse"), so an appositive with no "i" before it
            # says nothing about them.
            matches = [match for match in matches
                       if re.search(r"\bi(?:'m|m| am)\b", text[:match.start()], re.I)]
    if not matches:
        return job, city, frame
    for match in matches:
        groups = match.groups()
        was_working = len(groups) > 2
        phrase = (groups[-1] if was_working else groups[0]).strip()
        place_job = (was_working and (groups[0] or "").lower() in ("in", "at", "for", "on")) \
            or match.re is JOB_AS_A or match.re is JOB_GOT_AT
        cut = _first_tail(phrase)
        if place_job and not cut:
            cut = _first_tail(phrase, tails=JOB_TAIL_PLACE)
        if cut:
            at, tail = cut
            rest = phrase[at + len(tail):]
            if tail.strip() in ("in", "at") and not city:
                place = re.match(r"([A-Z][a-z]+(?: [A-Z][a-z]+)?)", rest.strip())
                if place and place.group(1).split()[0].lower() not in NOT_PLACES:
                    city = place.group(1)
            phrase = phrase[:at]
        if match.re is JOB_GOT_AT:
            if (groups[0] or "").lower() == "in" and not (groups[1] or "").strip():
                # "in" names where the work is only with an article in front of it: "i got a job
                # in a bakery" does, while "i got a job in two weeks" and "in may" name a time.
                continue
            if not a_place_that_employs(phrase):
                # A date, a shift or the person's own words about the past is not where they work.
                continue
        words = without_the_moment(phrase.split())
        if match.re is JOB_WAS and words and words[0].lower() in WAS_NOT_A_JOB:
            # "i was a kid", "i used to be a lad": how old they were, not what they did.
            continue
        if match.re is JOB_WAS and not _was_names_a_role(
                phrase, article=len(groups) > 1 and groups[1]):
            # "we were flat out", "i was eight weeks pregnant", "i was born in leeds": how they
            # were, and when - not what they did.
            continue
        if (not words or words[0].lower() in JOB_STOP or words[0].lower() in NOT_NAMES
                or words[0].lower() in NOT_NAMES_EXTRA
                # Only a phrase that *is* the judgement noun ("im a doormat", "im a joke",
                # "im an idiot sometimes") is one. "im a problem solver" and "im a waste
                # engineer" open with a word on that list and are what the person does: there the
                # noun describes the job rather than the person.
                or _is_a_judgement_phrase(words)):
            continue
        if name and words[0].lower() == name.lower():
            continue
        if words[0][:1].isupper() and len(words) == 1:
            continue
        if re.match(r"\s*\d", text[match.end(match.lastindex or 1):]):
            continue  # "im a size 12" measures them, it is not what they do
        if words[0].lower() in ("bit", "little", "lot", "couple", "few"):
            continue
        if words[0].lower() in ("my", "our", "his", "her", "their", "your"):
            # "i work on my own", "i work on their terms": a possessive names nobody's job.
            continue
        if words[0].lower() in SELF_JUDGEMENT:
            # "im an idiot", "im a hopeless cook", "im a lazy student": how they feel about
            # themselves, not what they do all day. The word is also never a job for anyone
            # else ("my brother is an idiot"), so it is skipped whoever the line is about.
            continue
        job = _the_role(words)
        if match.re is JOB_AS_A and not was_working:
            # "i got a new job as a chef": the line says how the job is said, so it is said back
            # the same way ("you work as a chef"), never with the frame of the job it replaced.
            # The article is read from the words the line used, not from a group: the job group
            # is the one every reader here takes its phrase from.
            article = re.search(r"\bas\s+(an?)\b", match.group(0), re.I)
            frame = "as " + (article.group(1).lower() if article else "a")
        elif match.re is JOB_WAS:
            # A job they had is said back in the past: the frame carries the tense the same way it
            # carries the preposition of a place, so every reader of the job says "You were a
            # teaching assistant" and never "You're a teaching assistant" to an ask that came
            # after "i was a teaching assistant before the kids".
            frame = "was"
        elif was_working and not (groups[0] or "").strip():
            # "i work nights", "i work two jobs", "i work from home": no preposition names where
            # the work is, so the verb itself is the frame and the reply says "you work ..." -
            # never "you're a nights".
            frame = "work"
        elif was_working and (groups[0] or "").lower() in JOB_FRAME | JOB_GOT_FRAME:
            # "in a warehouse", "for the council": the preposition and the article are how they
            # said where they work, so they are kept together and the reply follows them.
            frame = " ".join(part.strip() for part in groups[:2] if part and part.strip())
            if (match.re is JOB_GOT_AT and len(frame.split()) == 1
                    and job.lower() in JOB_GOT_AN_EMPLOYER):
                # "i got a job at school" names an employer without an article, and the store
                # says a workplace back with one: "You work at school" reads as a place the
                # person went to, where "You work at a school" is where they go now. The
                # article is added here rather than in the reply so every reader of the frame
                # (the whole job, the where-do-i-work ask) says it the same way.
                frame += " a"
        break
    return job, city, frame


def kid_ages(text):
    """The ages the line gives the children, oldest reading only, or []."""
    if not isinstance(text, str):
        return []
    match = KID_AGES.search(figures_as_digits(text)) or KID_AGES_AFTER_A_COMMA.search(
        figures_as_digits(text))
    if match:
        ages = [int(number) for number in re.findall(r"\d{1,2}", match.group("ages"))]
        return [age for age in ages if 0 <= age <= 110]
    # A child given one by one is aged just as plainly: "we have a 3 year old" says the age of the
    # one child, and a reply that asks "How old are they?" asks for what the line just said.
    counted = _children_by_year_old(figures_as_digits(text))
    if counted:
        return _ages_held(counted)
    # "my boys are 4 and 7 years old" names the group rather than the children as such, and the
    # reader for the people a line names keeps that age under the group's own name.
    grouped = [entry for entry in _other_ages(text)
               if (entry.get("who") or "").lower() in KID_GROUP]
    if grouped and not any(entry.get("name") for entry in grouped):
        held = []
        for entry in grouped:
            held.extend(age for age in _ages_held(entry) if age not in held)
        if held:
            return held
    # Children named one at a time keep their ages under their own relation - "my daughter is 6
    # and my son is 9" - so the ages are read off the entries themselves, in the order the line
    # says them. One named child is left alone: "my son is 6" has an answer of its own.
    each = [entry for entry in _other_ages(text)
            if (entry.get("who") or "").lower() in KID_ONE_BY_ONE]
    if len(each) >= 2 and not any(entry.get("name") for entry in each):
        held = []
        for entry in each:
            held.extend(age for age in _ages_held(entry) if age not in held)
        if held:
            return held
    return []


def kid_count(text):
    """"i have two kids" -> 2, "i dont have any kids" -> 0: the number a line states, or None."""
    if not isinstance(text, str) or KID_ASKING.match(text):
        return None
    none = KID_NONE.search(text)
    if none and not KID_NONE_NOT_AFTER_ALL.search(text[none.end():]):
        return 0
    match = KID_COUNT.search(text) or KID_COUNT_AND.search(text)
    if not match:
        # Children given one by one are still a number of children: "i have a 4 year old and a 7
        # year old" and "my kids are 4 and 7" name two children in the same breath as their ages,
        # and the answer to "how many kids do i have" is the count of the ages the line gave.
        ages = kid_ages(text)
        if ages:
            return len(ages)
        counted = _children_by_year_old(figures_as_digits(text))
        if counted:
            return len(_ages_held(counted))
        grouped = [entry for entry in _other_ages(text)
                   if (entry.get("who") or "").lower() in KID_GROUP]
        if grouped and not any(entry.get("name") for entry in grouped):
            held = []
            for entry in grouped:
                held.extend(age for age in _ages_held(entry) if age not in held)
            if held:
                # "my boys are 4 and 7 years old" counts the children it has ages for.
                return len(held)
        # Children named one relation at a time, each with their own age: "my daughter is 6 and
        # my son is 9" says two children as plainly as "my kids are 6 and 9" does, and the store
        # could not count it, so the line came back as a receipt - "Noted: your daughter is 6 and
        # my son is 9" - while the same line with the word "kids" in it was answered "Two kids,
        # six and nine. What are they into at the moment?". Two or more, because one named child
        # ("my son is 6") has an age answer of its own that must keep its turn.
        each = [entry for entry in _other_ages(text)
                if (entry.get("who") or "").lower() in KID_ONE_BY_ONE
                and (entry.get("age") or _ages_held(entry))]
        if len(each) >= 2 and not any(entry.get("name") for entry in each):
            return len(each)
        return None
    if KID_ELSEWHERE.search(text[match.end():]):
        # "i have two kids in my class" is a teacher counting the class, not a parent counting
        # their own: the children are at school, and not in this person's house.
        return None
    said = (match.group("n") or match.group("m") or "").lower()
    if said.startswith("a couple"):
        return 2
    if said.isdigit():
        return int(said)
    return KID_NUMBERS.get(said)


def _other_ages(text):
    """[{"who", "age"}] for the people the line gives an age for, or []."""
    text = figures_as_digits(text)
    found = []
    text = stated_not_asked(text)
    if not text:
        return found
    # Longest first, so "my mother in law is 68" is about the mother-in-law and not about a
    # "mother" who is somehow "in law is 68". Unsorted, the shorter relation won and the age was
    # dropped on the floor: the reply said the age back and the store held nothing.
    relations = "|".join(sorted(RELATIONS, key=len, reverse=True))
    # "my mother in law is 68" is a person of her own: the relation keeps its second word, so the
    # age is filed against the mother-in-law instead of being dropped on the floor ("how old is
    # she" then said "You haven't told me how old your mother in law is" about a line that did).
    who_one = r"(?:" + relations + r")(?:\s+in\s+laws?)?"
    # A word that is already a group is a group whether or not a singular of it is in the list
    # above: "my parents are 66 and 70" and "my grandparents are 80 and 82" were read by nothing
    # at all, because this wanted the singular word and then an "s".
    group_two = "grandparents|grandchildren"
    pattern = re.compile(r"\bmy\s+(?:(?P<many>(?:" + who_one + r"|" + group_two
                         + r")s?)\s+are|(?P<one>" + who_one + r")\s*(?:'s|is|was))\s+"
                         r"(?P<age>\d{1,3})\b", re.I)
    # "my son and my daughter are 7 and 4" gives the ages in the order the people come, so the
    # numbers are paired with them rather than one number taken for one person.
    pair = re.compile(r"\bmy\s+(?P<a>" + who_one + r")\s+and\s+(?:my\s+)?(?P<b>"
                      + who_one + r")s?\s+(?:are|is)\s+(?P<ages>\d{1,3}"
                      r"(?:\s*(?:,|and)\s*\d{1,3})+)", re.I)
    for match in pair.finditer(text):
        ages = [int(number) for number in re.findall(r"\d{1,3}", match.group("ages"))]
        if not all(0 <= age <= 120 for age in ages) or len(ages) < 2:
            continue
        for who, age in zip((match.group("a").lower(), match.group("b").lower()), ages):
            entry = next((one for one in found if one.get("who") == who), None)
            if entry is None:
                found.append({"who": who, "age": age})
            else:
                entry["age"] = age
    for kid_pattern in (KID_GROUP_AGES_ARE, KID_COUNT_AGES, KID_ADULTS_AGES):
        for match in kid_pattern.finditer(text):
            ages = [int(number) for number in re.findall(r"\d{1,3}", match.group("ages"))]
            if not ages or not all(0 <= number <= 120 for number in ages):
                continue
            if KID_AGES_NOT.search(text[:match.start("ages")]):
                continue
            if not AGE_TAIL.match(text[match.end():]):
                continue
            who = (match.groupdict().get("who") or "").lower()
            if not who:
                # A reading that names no word for the people is about the children the line has
                # already named, so it joins that group instead of a second one of its own. "my
                # children are 4 and 7" is read twice - once with the word, once by the pattern
                # for a line that only counts them - and the second reading filed "kids" beside
                # "children" on one line of one chat, so "how old are my kids" answered "Your
                # children are 4 and 7 and your kids are 4 and 7."
                who = next((one["who"] for one in found
                            if (one.get("who") or "").lower() in KID_GROUP), "kids")
            # The ages are kept in the order they were said, as one list: the children are a
            # group and the answer says them as one ("your kids are 4 and 7").
            _keep_the_ages(found, {"who": who, "ages": ages} if len(ages) > 1
                           else {"who": who, "age": ages[0]})
    # "my son whos 7 and my daughter whos 4": the clause names the person and gives their age,
    # the same fact as "my son is 7", so the ages are numbers here like every other age the store
    # keeps and "how old are my kids" can list them.
    for match in CHAINED_RELATION_AGE.finditer(text):
        age = int(match.group("age"))
        if not 0 <= age <= 120 or _month_age_after(text, match.end("age")):
            continue
        first = re.sub(r"(?:'s|\u2019s|s)$", "", match.group("first").lower())
        entry = {"who": first + "'s " + match.group("second").lower(), "age": age}
        name = match.groupdict().get("name")
        if name and name.lower() not in _A_WORD_FOR_A_PERSON:
            # "my mums friend julie is 70" gives the pair and her name, so the ask that uses
            # either ("how old is my mums friend", "how old is julie") finds the one age.
            entry["name"] = name
        found.append(entry)
    for match in RELATION_WHOS_AGE.finditer(text):
        age = int(match.group("age"))
        if not 0 <= age <= 120 or _month_age_after(text, match.end()):
            continue
        found.append({"who": match.group("who").lower(), "age": age})
    for match in AGE_TO_COME.finditer(text):
        # The clause is read to the end of the birthday rather than to its start: "shes 70 next
        # month" is the whole line, so the pronoun that says whose age it is sits inside the part
        # read, and reading only what comes before it found no subject at all.
        kind, who = subject(text, match.end())
        if kind != "other" or (who and who not in RELATIONS):
            continue
        age = int(match.group(1))
        if not 0 <= age <= 120:
            continue
        turns = " ".join(match.group(2).lower().split())
        if not who:
            # "my mum is 72 and she is 73 next month": the clause names no relation, but the line
            # does, and the pronoun is that person. Read to the pronoun alone, the birthday would
            # be filed against "she" beside a person called mum, which is two people where the
            # line has one.
            who = _relation_before(text, match.start())
        if who:
            # A birthday folded onto a person the line already gave an age for is the same person
            # said twice: "my mum is 72 and she is 73 next month" keeps 72 as the age she is and
            # "next month" as the day the next one comes, rather than a second entry beside her.
            entry = next((one for one in found if one.get("who") == who), None)
            if entry is not None and not entry.get("turns"):
                entry["turns"] = turns
                if entry.get("age") != age:
                    # "my daughter is 3, she turns 4 next month" gives the age she is and the one
                    # still to come. Keeping only the day left the store saying she turns 3.
                    entry["to_come"] = age
                continue
            found.append({"who": who, "age": age, "turns": turns})
        else:
            # The line gives the age of somebody it never names ("she is 70 next month"). The fact
            # is filed against the pronoun rather than against nobody: an entry with an empty
            # "who" is not a person, and the store points a pronoun at the person the chat is
            # about.
            pronoun = _the_pronoun(text, match.end())
            if pronoun:
                person = _the_person_the_pronoun_is(text, match.start(), pronoun)
                if person:
                    found.append({"who": person, "age": age, "turns": turns})
                else:
                    found.append({"pronoun": pronoun, "age": age, "turns": turns})
    # "my son tom is 7": the name sits between the relation and the age, and the number is still
    # the son's. The name itself is read by `_a_relations_name`, which files it with the same
    # person; here it is only stepped over, and only when it can be a name.
    named = re.compile(r"\bmy\s+(?P<who>" + relations + r")\s+(?P<name>[A-Za-z][a-z'-]{1,19})"
                       r"\s*(?:'s|is|was)\s+(?P<age>\d{1,3})\b", re.I)
    for match in named.finditer(text):
        name = match.group("name")
        if not _may_be_a_name(name):
            continue
        if not AGE_TAIL.match(text[match.end():]):
            continue
        age = int(match.group("age"))
        if not 0 <= age <= 120:
            continue
        who = match.group("who").lower()
        if who.endswith("s") and who[:-1] in RELATIONS:
            who = who[:-1]
        kept = _tidy(name)
        entry = _the_person(found, who, kept)
        if entry is None:
            found.append({"who": who, "name": kept, "age": age})
        else:
            entry.setdefault("name", kept)
            entry["age"] = age
    for match in pattern.finditer(text):
        plural = match.group("many")
        if plural:
            listed = A_LIST_OF_AGES.match(text, match.start("age"))
            if listed:
                ages = [int(number) for number in re.findall(r"\d{1,3}", listed.group("ages"))]
                if (len(ages) > 1 and all(0 <= one <= 120 for one in ages)
                        and AGE_TAIL.match(text[listed.end():])):
                    # One word for the family and two ages said for it: "my brothers are 20 and 24"
                    # was filed as the first figure on the singular word, so the ask answered
                    # "Your brother is 20" - half the fact, in the wrong number. Every ask reader
                    # already keeps a group as a word plus a list of ages (that is how "my kids are
                    # 4 and 7" is answered), so the list is filed that way and said back whole.
                    _keep_the_ages(found, {"who": " ".join(plural.lower().split()), "ages": ages})
                    continue
        rest = text[match.end():]
        if not AGE_TAIL.match(rest):
            continue  # a weight, a height or a span of time, not an age
        age = int(match.group("age"))
        if not 0 <= age <= 120:
            continue
        who = match.group("many") or match.group("one")
        who = " ".join(who.lower().split())
        who = re.sub(r"\bin laws$", "in law", who)
        if who.endswith("s") and who[:-1] in RELATIONS:
            who = who[:-1]  # "my sons are 7" is kept as the son, so "how old is my son" reads it
        entry = _the_person(found, who)
        if entry is None:
            found.append({"who": who, "age": age})
        else:
            # The age the line gives plainly is the age they are now; an entry that already
            # carries a birthday to come keeps the day and takes this as its age.
            if entry.get("turns") and entry.get("age") not in (None, age):
                # "my daughter is 3, she turns 4 next month": the number the entry carried was the
                # birthday still to come, and dropping it left the chat saying she turns 3.
                entry["to_come"] = entry["age"]
            entry["age"] = age
    counted = _children_by_year_old(text)
    if counted:
        _keep_the_ages(found, counted)
    for entry in _kids_named_with_ages(text):
        if not any(one["who"] == entry["who"] and one.get("name") == entry["name"]
                   for one in found):
            found.append(entry)
    return found


def _people(text):
    """The people this line is about. "my parents evening" is an evening, not the people in it.

    A relation word names someone when it stands on its own in the clause ("my parents are
    coming", "my son's allergy", "I saw my mum"): what gives it away is a noun straight after it.
    """
    found = []
    for relation in RELATIONS:
        for match in re.finditer(r"\b" + relation + r"s?\b", text, re.I):
            after = text[match.end():]
            said_possessive = after.startswith("'s") or after.startswith("s'")
            if said_possessive:
                after = after.split("'", 1)[1][1:]  # "my son's allergy": the son is still a person
            # "my brother-in-law is coming" is the in-law, not the brother: the suffix is the
            # person the line named, and dropping it filed a brother the chat had never mentioned.
            if IN_LAW_AFTER.match(after):
                found.append(relation + " in law")
                break
            words = [word.strip(".,!?;:'") for word in after.split()]
            words = [word for word in words if word]  # a lone "'" is not a word
            next_word = words[0].lower() if words else ""
            if next_word in COMPOUND_AFTER:
                # "my daughters birthday" and "my daughter's birthday" are one fact: the "s" with
                # no apostrophe is the possessive people type out, and reading the whole thing as
                # a compound noun ("my parents evening") left the daughter out of the chat, so the
                # age said for her two turns later ("shes turning 6") had nobody to belong to and
                # "how old is my daughter" answered "You haven't told me". The school evening is
                # the one compound that is genuinely an event rather than a thing of theirs.
                if not ((str(match.group(0)).lower().endswith("s") or said_possessive)
                        and next_word in COMPOUND_THAT_IS_THEIRS):
                    continue
            before = _the_clause_before(text, match.start())
            if SOMEONE_ELSE_HAS.search(before) or A_RELATION_OWNED.search(before):
                # somebody else's relation, said as theirs: the owner is the person the line is
                # about and this one is not the person's own
                continue
            if SELF_AS_A_ROLE.search(text[:match.start()]) and is_a_judgement(text):
                # "im a bad mum" is their own role, judged, not someone they know. A role they
                # are simply stating - "im a mum of two", "im a teacher" - is a fact about the
                # person and is kept, or the store notes it and then says it did not hear it.
                continue
            # "my mother in law" is one person and she is called that: kept as "mother", the
            # next answer about her said "Your mother is vegetarian".
            inlaw = re.match(r"\s+in\s+laws?\b", after, re.I)
            found.append(relation + (" " + " ".join(inlaw.group(0).split()) if inlaw else ""))
            break
    return found


# The frames that make the line a wish or a condition rather than a fact about them. A
# continuation under one of these keeps the frame, so it says nothing about what is true.
WISHING = re.compile(
    r"\b(?:want|wanna|wish|hope|might|may|could|would|should|plan|planning|thinking|thought|"
    r"going to|gonna|used to|trying|try|like to|love to|if|unless|pretend|imagine)\b", re.I)


# The clause has to open with a verb that takes the person as its subject; a noun opening one
# ("and a tin of tomatoes") is part of the list before it, and "i tin of tomatoes" is not a job.
CONTINUATION_VERB = frozenset("""live work have got am 'm was were come comes came moved move
drive study teach train run play commute rent own need want speak hold""".split())


# Only what the stream keeps as a fact about them: the other stream (plans, deeds) reads a
# whole line and its own subject, and half a clause is not enough for it.
CONTINUATION_KEYS = frozenset("""places home city town job job_frame age pets allergies people diet
diets conditions name country county""".split())


# The pronoun that carries a second clause on about the person the first clause named: "my mum is
# 70 and she loves gardening" says two things about the mum, and the store kept only the age. The
# clause is put back under the relation the line named ("my mum loves gardening") and read as a
# line of its own, because that is what it is.
SAME_PERSON_CLAUSE = re.compile(
    r"^\W*(?:she|he|they)\s+(?P<rest>[a-z0-9'\u2019 ]{3,80}?)\s*$", re.I)


# The clauses one line can carry more than one fact in: a full stop, a comma, or the little
# conjunctions people join two facts with ("and", "but", "also", "n").
SAME_PERSON_SPLIT = re.compile(r"[.!?;]+|,\s*|\s+(?:and|but|also|n)\s+", re.I)


def _the_relation_named(clause):
    """The relation a clause names with "my"/"our", or None."""
    for relation in RELATIONS:
        if re.search(r"\b(?:my|our)\s+" + relation + r"(?:'s|s)?\b", clause, re.I):
            return relation
    return None


def _same_thing(one, other):
    """The same fact under a plural: "pets" and "pet", "cats" and "cat"."""
    one = _tidy(str(one)).lower().strip()
    other = _tidy(str(other)).lower().strip()
    if not one or not other:
        return False
    return one == other or one.rstrip("s") == other.rstrip("s")


def _is_only_the_take_back(value, gone):
    """"no pets" is not a correction to something called "Pets": a line that takes a fact back
    corrects nothing, and "Pets" is not a value anybody holds.

    Only a value the line says it is denying is skipped. A line can correct and take something
    back at once, and the correction is the half worth keeping: "im not allergic to nuts, no i
    mean dairy" puts dairy back on the table while it takes nuts off, and the "no" in it opens
    the correction, not the denial.
    """
    if not gone:
        return False
    for fact, said in gone.items():
        if _same_thing(value, fact):
            return True
        for item in (said if isinstance(said, list) else [said]):
            if isinstance(item, dict):
                item = item.get("animal") or item.get("name") or ""
            if str(item) == EVERYTHING:
                # "no pets" takes the lot, so there is nothing left for a value to be about.
                return True
            if _same_thing(value, item):
                return True
    return False


# The name a person gives the bot: "im going to call you bob", "your name is Pip from now on",
# "i'll call you max from here". Only a naming, never a question - "what should i call you" asks
# and names nothing - and never a time: "i'll call you when i get there" names no one.
BOT_NAME = re.compile(
    r"\b(?:call|calling|callin|name|naming|named)\s+(?:you|u)\s+([A-Za-z][a-z'-]{1,19})\b"
    r"|\byour name(?:'s| is| will be)\s+([A-Za-z][a-z'-]{1,19})\b", re.I)


# The words that make a line a question about the name rather than a gift of one: "what should i
# call you", "which name do you want", "your name is bob right?". A question that offers the name -
# "can i call you bob", "shall i call you bob" - is the person choosing it, so it names the bot.
BOT_NAME_ASKED = re.compile(r"\bwhat\b|\bwhich\b|\bwho\b", re.I)


# A tag on the end of the line takes the gift back: "your name is bob right?" asks instead of says.
BOT_NAME_TAG = re.compile(r"\bright\s*\?|\bam i right\b|\barent you\b|\bisnt it\b", re.I)


BOT_NAME_TITLE = frozenset("mr mrs ms miss mx dr doctor sir lady lord captain prof professor "
                           "prince princess saint dame".split())


# What can follow "call you" without being a name: a time, a reason, a person, a politeness.
BOT_NAME_STOP = frozenset("""when then tomorrow tonight today later back after before if once until
soon now again please ok okay mate guys someone somebody him her them it me you us everyone
all every one two three four five six seven eight nine ten eleven twelve
day week month year morning evening night weekend christmas
at in on by around about this next last half noon midnight oclock o'clock
really very so quite pretty much always never just only definitely
short tall long great cool funny weird silly fine good bad better best worse worst wrong right
hard easy nice lovely rubbish dumb stupid same different strange odd lovely amazing awesome
useless perfect brilliant terrible awful""".split())


# The ask for the name the person gave the bot: "whats your name", "what should i call you",
# "what do they call you". Only the ask - "do you like your name" is a question about a taste,
# and "who are you" is the identity ask, which another module answers.
BOT_NAME_ASK = re.compile(
    r"\bwhat(?:'s|s| is| was)?\s+your name\b|\byour name (?:again|now)\b"
    r"|\bwhat (?:should|shall|do|can|would) (?:i|we|they) (?:call|name) you\b"
    r"|\bwhat(?:'s|s| is| was) (?:it|that) (?:i|we) (?:call|called) you\b"
    r"|\b(?:do|have) you (?:got |have )?(?:a |any )?(?:name|nickname)\b"
    r"|\bwhat are you called\b"
    r"|\bcall you again\b", re.I)


def bot_name(text):
    """The name they have just given the bot, or None.

    A name is theirs to give: kept, it is what the bot says when asked its name later in the chat,
    and without it the bot claims to have no name after being named. The word after "call you" is
    read as a name only when the line is not a question and the word is not a time or a person
    ("i'll call you when i get there", "i'll call you back").
    """
    if not isinstance(text, str):
        return None
    match = BOT_NAME.search(text)
    if not match:
        return None
    if BOT_NAME_ASKED.search(text[:match.start()]) or BOT_NAME_TAG.search(text):
        # "what should i call you" and "your name is bob right?" ask; they do not name this bot.
        return None
    word = (match.group(1) or match.group(2) or "").strip()
    if not word or word.lower() in BOT_NAME_STOP or word.lower() in NOT_A_NAME:
        return None
    if word.lower() in BOT_NAME_TITLE:
        # "call you Mrs Whiskers" is a whole name, not the title in front of it.
        more = re.match(r"\s+([A-Za-z][a-z'-]{1,19})\b", text[match.end():])
        if more:
            word = word + " " + more.group(1)
    if not all(NAME_WORD.match(part) for part in word.split()):
        return None
    return word[:1].upper() + word[1:] if word.islower() else word


# The correction people say on its own, with the subject left out: "im an accountant" then
# "actually an engineer rather than an accountant". Read on its own the line names nothing (no
# "im", no "i work"), so the take-back never reached the store and the old job was still the
# answer a turn later. The subject is the words the turn before opened with, and the line is read
# with them put back - only when the line opens with a correction and takes a value back, so a
# bare "actually" with no value in it and a plain "no" are still nothing.
CORRECTION_OPENER = re.compile(r"^\s*(?:(?:no|nope|sorry|actually|wait|ah|oh|i\s+mean(?:t)?|"
                               r"make\s+that|or\s+rather)[,.\s!\u2014-]+)+", re.I)


SUBJECT_OPENERS = ((re.compile(r"^\s*(?:i'?m|i\s+am|im)\b", re.I), "im"),
                   (re.compile(r"^\s*i\s+work(?:s|ed)?\s+as\b", re.I), "i work as"),
                   (re.compile(r"^\s*i\s+work(?:s|ed)?\s+(?:in|at|for)\b", re.I), "i work in"),
                   (re.compile(r"^\s*i\s+live(?:s|d)?\s+in\b", re.I), "i live in"),
                   (re.compile(r"^\s*(?:i\s+have|i'?ve\s+got|i\s+have\s+got)\b", re.I),
                    "i have"))


# "i said the party is on tuesday", "i told you i live in leeds": the line is the person
# saying the same thing again, in the words that report it. Read as it stands, the report verb is
# a past one, so the dated thing inside it is filed as something that has already happened ("i
# said the party is on tuesday" put a "done" fact in the store and no plan, and the correction
# that followed it had nothing to land on). The report is a frame, and what is inside the frame
# is the fact: the words after it are read the way they would be if they were said on their own.
# A line that corrects ("no, i said 700") is left to the correction readers, which need the
# marker in front to know the value is going back up.
REPORTED = re.compile(
    r"^\W{0,3}(?:(?:ok|okay|so|and|but|well|no|nope|look|see|yes|yeah|actually|honestly|literally|"
    r"i\s+mean)[, ]+)*"
    r"(?:(?:i|we)\s+(?:already\s+|did\s+|just\s+|definitely\s+)?(?:said|told\s+you|mentioned)|"
    r"like\s+i\s+said|as\s+i\s+said|to\s+repeat)\b[\s,:]*(?P<rest>[^?]*\S)", re.I)


def _reported_clause(text):
    """The thing a line reports having said, when the line is only the reporting of it."""
    text = (text or "").strip()
    if not text or "?" in text:
        return None
    if (CORRECTION_SAID.search(text) or CORRECTION.search(text)
            or CORRECTION_PAIR.search(text) or CORRECTION_MAKE.search(text)):
        return None  # a correction says the value again; it is not a report of a fact
    match = REPORTED.match(text)
    if not match:
        return None
    rest = match.group("rest").strip(" ,.;:-")
    return rest or None


def _paid_by_a_period(text, end):
    """Whether a period follows the figure, with the household allowed in the gap.

    "we bring home 3000 between us a month" says the same as "we bring home 3000 a month", and
    the words in the middle name who the money is for rather than a count of something else. The
    words are read from the short list above, so "i get 300 emails a week" is still a routine.
    """
    qualifier = INCOME_QUALIFIER.match(text[end:])
    return bool(INCOME_PERIOD.match(text, end + (qualifier.end() if qualifier else 0)))


def _a_years_pay(figure):
    """Whether a figure with no period is a year's wage rather than a count.

    "i earn 32000" and "my salary is 32k" are a year's pay and nobody says the period; "i get 300
    emails" and "i make 2000 cookies" are counts and their period is what said so. So the figure
    itself has to be the size of a wage: four digits, or a figure in thousands.
    """
    said = str(figure or "")
    if re.search(r"\d[\d,.]*\s?(?:k|grand|thousand)\b", said, re.I):
        return True
    return len(re.sub(r"[^\d]", "", said)) >= 4


# The ways a line says what the person is, what they have or what they do, right after a hello:
# "hi, I'm vegetarian", "hi, I have a bad back", "hi, I work nights". The lead is what says the
# rest of the line is about them rather than about somebody else or about the day.
SAYS_WHAT_THEY_ARE = (("i", "am"), ("im",), ("i'm",), ("i", "have"), ("i", "work"),
                      ("i", "live"), ("i", "take"), ("i", "get"))


# What a line keeps about them and is still not what they are: their name, which is the chat
# module's to answer ("hi, I'm Sam"), and a thing they are after, which is a request rather than
# a fact about them - "im looking for a plumber" is asking for a plumber.
THEIR_NAME = frozenset(("name",))


THEIR_PLAN = frozenset(("plan", "plans"))


def _one_entry_per_person(entries):
    """One entry per person: a line that says the same thing twice is still one person.

    "my mum is 72 and she is 73 next month" is read twice. The first reading has both numbers and
    keeps them the right way round (72 now, 73 next month); the later clause is then read on its
    own, as "my mum she is 73 next month", and cannot see the 72 in front of it, so it hands back a
    second entry for the same woman. Two entries for one person is two mums to everything that
    reads the store, and the age the line opened with is lost from the reply.

    The fold is the store's own (`bot/memory/__init__._fold_into`): a birthday still to come sits
    beside the age they are rather than replacing it, and an entry that only repeats the birthday
    already kept adds nothing. Two entries are one person only when they name the same person - the
    same word for them, and the same name if either gave one - so "my kids are ada 7 and sam 4"
    stays two children.
    """
    out = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        who = str(entry.get("who") or "").lower()
        kept = None
        if who and not entry.get("pronoun"):
            for one in out:
                if str(one.get("who") or "").lower() != who or one.get("pronoun"):
                    continue
                mine = str(one.get("name") or "").lower()
                theirs = str(entry.get("name") or "").lower()
                if mine and theirs and mine != theirs:
                    continue  # two children with one word for them are two children
                kept = one
                break
        if kept is None:
            out.append(dict(entry))
            continue
        for key, value in entry.items():
            if key in ("who", "pronoun"):
                continue
            if key == "name":
                # A name read on the line goes onto the person the line already named: "my son
                # tom is allergic to nuts" is one boy with a name and an allergy, and dropping
                # the name left the store unable to answer to "what is tom allergic to". The
                # spelling that keeps its capital is the one to keep: the reader that catches a
                # name as it was typed says "Meg", and one that takes the word after the verb
                # says "meg", and a store that answers "your sister is called meg" is a store
                # that looks like it was not listening.
                mine = str(one.get("name") or "")
                if not mine or (mine[:1].islower() and str(value)[:1].isupper()):
                    one["name"] = value
                continue
            if key == "age":
                # The birthday already kept, said again: the age they are stays.
                if one.get("to_come") == value:
                    continue
                if one.get("turns") and not one.get("age"):
                    one["age"] = value
                    continue
                if isinstance(one.get("age"), int) and isinstance(value, int) and one["age"] != value:
                    if not one.get("turns"):
                        one["age"] = value
                    continue
                one["age"] = value
                continue
            if key in ("turns", "to_come"):
                # The day belongs to the number it was said with, and the entry that already has
                # both is the one read with the line in front of it.
                if not one.get("turns"):
                    one["turns"] = value
                    if key == "to_come" and one.get("age") != value:
                        one["to_come"] = value
                continue
            if not isinstance(value, (list, tuple)):
                one.setdefault(key, value)
                continue
            have = one.setdefault(key, [])
            if isinstance(have, list):
                have.extend(item for item in value if item not in have)
    return out


def _union(one, other):
    out = list(one or [])
    for value in other or []:
        if value not in out:
            out.append(value)
    return out


def _the_pronoun(text, pos):
    """Which person a clause that names no relation is about: "she", "he", or "" for none."""
    start = 0
    for match in CLAUSE_BREAK.finditer(text, 0, pos):
        start = match.end()
    found = PRONOUN_SUBJECT.search(text, start, pos)
    if not found:
        return ""
    word = found.group("pron").lower()
    return {"her": "she", "him": "he", "them": "they", "shes": "she", "hes": "he",
            "theyre": "they"}.get(word, word)


# A relation the line names with their possessive, kept with an in-law's second word: "my mum",
# "my mums", "my mother in law". Longest first, so "mother in law" is not read as "mother".
RELATION_SAID = re.compile(
    r"\b(?:my|our)\s+(?P<who>" + "|".join(sorted(RELATIONS, key=len, reverse=True))
    + r")(?P<plural>s?)(?P<inlaw>\s+in\s+laws?)?\b", re.I)


def _the_person_the_pronoun_is(text, pos, pronoun):
    """The relation the line named before a bare pronoun, when it names exactly one.

    A line can name a person and then go on about them with a pronoun: "my mum is coming on
    sunday, shes 60", "my sister is staying, her birthday is 3 May". The clause the pronoun sits
    in names nobody, so the fact was filed against "she" and the store put it on whoever it had
    heard of last - a sister from an earlier line got the mum's age, and then "how old is my
    sister" said 60 while "how old is my mum" said she had never given it. The line named one
    person, so that is who the pronoun is.

    "" when the line names nobody (the store folds the pronoun onto the person the chat is about),
    names more than one ("my mum and my sister are coming, shes 60" is genuinely either), or names
    somebody the pronoun does not fit ("my mum is called janet and he is 72" is somebody else's
    72, and a fact on the wrong person is worse than one on nobody).
    """
    fits = SHE if pronoun == "she" else HE if pronoun == "he" else frozenset()
    if not fits:
        return ""
    who = ""
    for match in RELATION_SAID.finditer(text, 0, pos):
        word = a_person_word(" ".join((match.group("who")
                                       + (match.group("inlaw") or "")).split()).lower())
        if who and word != who:
            return ""
        who = word
    if not who:
        return ""
    parts = [part for part in re.split(r"[-\s]+", who) if part]
    return who if who in fits or any(part in fits for part in parts) else ""
