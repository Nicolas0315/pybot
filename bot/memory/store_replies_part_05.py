"""Part 5 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import random
import re
from ..compose import pick
from ..memory import last_user, note, others, stem, user, you
from ..memory import ack
from ..memory.places import _asked_person, _other_place
from ..memory import facts as extract
from ..memory import resize
from ..memory.store_lines import (
    CORRECTION_SAY_DROP, CORRECTION_SAY, CORRECTION_SAY_PAIR, PET_RENAMED_SAY, BARE_ECHO_ONLY,
    _TENS_WORDS, CORRECTED_AGAIN, CORRECTED_AGAIN_WHO, CORRECTED_WHICH_PERSON, NAME_ADVICE,
    DENIAL_WORDS, DENIAL_STEMS,
)
from ..memory.relations import _a, _animal_family, _person_from_pronoun
from .store_replies_part_01 import (
    FEEDING_ASK, HEAD_COUNTS, HEAD_WORDS, _a_size, _the_portion_for_the_food,
    _the_size_on_the_screen, FOR_A_COUNT, MADE_ONLY, _size_in_grams, HOW_FAR_ALONG, OWN_LENGTH_ASK,
    PLAN_LOW_START, _the_second_pet_said, _bare,
)
from .store_replies_part_02 import (
    _turned, _a_kept_thing_behind, _a_thing_it_keeps, _same, FOOD_CATEGORIES, GROWN_UP_ASK,
)
from .store_replies_part_03 import (
    _a_pet_of_theirs_is_named, _pet_names, _the_pet_in_play, _the_whole_word_in, _third_person,
    _place_phrase, _yours, _from_reply, _grown_up_reply, _does_not, _eats, _is_are, _diet_words,
    _said_of_someone_else,
)
from .store_replies_part_04 import (
    PART_OF, JOB_PART, PART_ADVICE, PART_HELP, PART_ASK, PART_MINE, PART_POINTS, RECORD_PART,
    DRINK_DIET, TELLING_AFTER_ASK, YES_NO_ASK, YES_NO_FRAME, CONFIRM_FRAMES, DIET_ANY, CONFIRM_TAG,
    REMEMBERING_FRAME, RESTATED, SAYS_SOMETHING, NOT_THE_FOOD, PUTTING_BY, _NUMBER_WORDS, _a_number,
    BARE_WHAT_I_DO, JOB_LINE_WORDS, ALLERGY_SAID, AVOID_REST, EATING, POINTING, POINTING_ANY,
    NAME_ASK, _A_DATE_AT_THE_END, FOR_A_MEAL, IN_A_PLACE, IN_MY_PLACE, THEIR_PLACES,
    WORK_CIRCUMSTANCE, NEGATED_SAID, PLAN_DIETS, STOPPED_SAID, WAY_OF_EATING, ANY_MORE,
    ASKING_ABOUT_IT, A_CLAIM_OF_TELLING, PLANNING_IT,
)


def _the_people_that_size_feeds(text, memory):
    """What the amount in hand feeds, against the portion the knowledge keeps for that food, or None.

    "how long do i roast a chicken" / "its 2kg" / "is that enough for 6" is the question a person
    asks while holding the joint: the portion the cooking know-how already keeps ("500g a person
    on the bone", units.PER_PERSON) turns their size into a number of people, and nothing here is
    worked out that the knowledge does not already say.

    Only a line asking whether an amount will do for a head count, only for a food the chat has
    named, and only a size that is on the screen - said by them or worked out for them a turn ago.
    A food counted in pieces ("3 sandwiches each") has no weight to read a size against, so the
    reader stands back and lets the answer speak.
    """
    if not isinstance(memory, dict):
        return None
    said = " ".join(str(text or "").lower().split())
    found = FEEDING_ASK.search(said)
    if not found:
        return None
    count = HEAD_COUNTS.get(found.group(1).lower()) or HEAD_WORDS.get(found.group(1).lower())
    if not count:
        try:
            count = int(found.group(1))
        except (TypeError, ValueError):
            return None
    if not 2 <= count <= 40:
        return None
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    held = said + " " + " ".join(str(turn.get("user") or "").lower() for turn in turns[-3:])
    answers = " ".join(str(turn.get("bot") or "").lower() for turn in turns[-2:])
    portion = _the_portion_for_the_food(held, answers)
    if not portion:
        return None
    size = _a_size(text) or _the_size_on_the_screen(turns)
    if not size:
        return None
    return _the_portion_reply(size, portion, count)


def _the_amount_they_made(text, memory):
    """A line saying they only made this much, read against the total an answer worked out.

    "how much rice for 4 people" answers "About 75 g of dry rice each, so 300 g for four", and
    "i only made 200g" then got "5 minutes": the amount was read as a cooking question about a
    weight. The answer has the count and the figure it worked out, so the amount they made is read
    against the portion the answer gave, and the shortfall is said plainly.

    Only a line carrying the "only"/"just" that says it is short, only an amount with a weight in
    it, and only when the answer named the head count it worked the total out for. Everything else
    is left to whoever else reads it.
    """
    if not isinstance(memory, dict):
        return None
    said = " ".join(str(text or "").lower().split())
    if not MADE_ONLY.search(said):
        return None
    size = _a_size(text)
    if not size:
        return None
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    answer = " ".join(str(turn.get("bot") or "").lower() for turn in turns[-2:])
    counted = FOR_A_COUNT.search(str(turns[-1].get("bot") or "").lower()) if turns else None
    if not counted:
        return None
    count = HEAD_COUNTS.get(counted.group(1)) or HEAD_WORDS.get(counted.group(1))
    if not count:
        try:
            count = int(counted.group(1))
        except (TypeError, ValueError):
            return None
    if not 2 <= count <= 40:
        return None
    held = said + " " + " ".join(str(turn.get("user") or "").lower() for turn in turns[-3:])
    portion = _the_portion_for_the_food(held, answer)
    if not portion:
        # No portion for any food in the chat: the weight could be anything, so the line is left
        # to whoever else reads it rather than read against a figure that is not about a plate.
        return None
    return _the_portion_reply(size, portion, count)


def _the_portion_reply(size, portion, count):
    """One size read against one portion, or None when it does not feed anyone."""
    per, unit, noun, bone = portion
    if unit != "g":
        return None  # pieces and millilitres are not a weight the size can be read against
    grams = _size_in_grams(size)
    if not grams:
        return None
    feeds = int(grams // per)
    if feeds < 1:
        return None
    line = "{size} of {noun}{bone}is about {per}g a person, so it feeds {feeds}".format(
        size=size, noun=(noun + " ") if noun else "", bone="on the bone " if bone else "",
        per=("%g" % per), feeds=_a_number_word(feeds))
    if feeds >= count:
        if feeds > count:
            return line + " \u2014 enough for {count}, with a second helping in it.".format(
                count=_a_number_word(count))
        return line + "."  # the number of people it feeds is the answer, so it is not said twice
    wanted = count * per
    wants = ("%gkg" % (wanted / 1000.0)) if wanted >= 1000 else ("%gg" % wanted)
    return line + ", and {count} wants about {wants}.".format(
        count=_a_number_word(count), wants=wants)


def _how_far_along(memory, low):
    """The weeks a pregnancy the chat was told has run, said as a length: "Eight weeks."."""
    said = str(low or "")
    if not HOW_FAR_ALONG.search(said):
        return None
    holding = [entry for entry in others(memory)
               if isinstance(entry, dict) and isinstance(entry.get("weeks"), int)]
    # A relation the ask names is the one it is about, own pregnancy or not: "how far along is my
    # wife" in a chat that has both on file is not about the person asking.
    named = [entry for entry in holding
             if re.search(r"\b" + re.escape(str(entry.get("who") or "")) + r"\b", said)]
    if len(named) == 1:
        holding = named
    elif OWN_LENGTH_ASK.search(said):
        # The person's own pregnancy is kept on them (`memory["user"]`), not in `others`, so the
        # length is read from there before anything is said about somebody else.
        own = user(memory) or {}
        if isinstance(own.get("weeks"), int):
            return _a_number_word(int(own["weeks"])).capitalize() + " weeks."
        if own.get("pregnant"):
            # The pregnancy is on file and the length never was, so the honest answer is the one
            # thing missing rather than a search hedge about a fact they told the bot themselves.
            return ("You didn't say how many weeks — tell me and I'll keep it, so the meal plans "
                    "fit where you are.")
    if not holding:
        return None
    if len(holding) > 1:
        # Two pregnancies on file: the relation the ask names decided above, then the pronoun, and
        # without either the one told last is the one the chat is on.
        who = _person_from_pronoun(said, memory)
        if who:
            holding = [entry for entry in holding
                       if str(entry.get("who") or "").lower() == who] or holding[-1:]
    weeks = int(holding[-1]["weeks"])
    return _a_number_word(weeks).capitalize() + " weeks."


def _correction_this_turn(text, memory):
    """The short note that says which value the bot goes with, on the turn of the correction."""
    fixed = memory.get("correction") if isinstance(memory, dict) else None
    if not isinstance(fixed, dict):
        return None
    if fixed.get("said") != " ".join(str(text or "").lower().split()):
        return None
    return _correction_said(fixed, memory) or None


def _correction_said(fixed, memory=None):
    """The short line that says which value the bot is going with now."""
    if not isinstance(fixed, dict):
        return ""
    if fixed.get("key") == "pets_more":
        return _the_second_pet_said(fixed, memory)
    # A fact about someone else is worded by the reading that kept it ("I'll keep your mum off
    # those"), so its note is the whole line rather than a value in a shape.
    if fixed.get("note"):
        return str(fixed["note"])
    value = fixed.get("value")
    if not value:
        return ""
    if fixed.get("key") == "job":
        # A job is said in the words the person used for it: they told the bot where they work,
        # so the note says that back. "Hospital — got it, I'll say Hospital" is the bot talking
        # about its own wording, and it is not the fact.
        note = _job_note(str(value), user(memory) if isinstance(memory, dict) else None)
        if note:
            return note
    in_a_sentence = fixed.get("key") in ("budget", "plan", "birthday") and fixed.get("sentence")
    if in_a_sentence:
        value = " ".join(str(fixed["sentence"]).split())
        # The sentence is sometimes the person's own repair rather than the reading's:
        # "sorry, i mean saturday" was said back as "Got it — Sorry, you mean on Saturday", the
        # steering and the bot's own voice in one line. The frame is what they said to correct
        # themselves, not part of the day, so it comes off before the sentence is said back.
        unframed = ack.without_the_frame(value)
        if unframed and unframed != value:
            value = unframed
            if fixed.get("key") == "plan":
                bare = str(fixed.get("value") or "").strip()
                # A sentence that was only the frame and the new value ("sorry, i mean on
                # saturday") says the value on its own: "Got it — Saturday", not "— on Saturday".
                if bare and " ".join(value.split()).lower() in (
                        bare.lower(), "on " + bare.lower(), "in " + bare.lower(),
                        "at " + bare.lower()):
                    value = bare
        if fixed.get("key") == "plan":
            # The sentence is the person's own, so a note that says it in their voice is the bot
            # talking about itself: "my sister and i are going to spain" came back as "Got it —
            # my sister and i are going to spain", and "i start my new job on tuesday" as "Got it
            # — i start my new job on tuesday". The rest of the plan is said back in the second
            # person, so the note is too.
            value = you(value)
            value = value[:1].lower() + value[1:]
        # The sentence arrives as the person typed it, full stop and all, and the note adds its
        # own: "I'm going to Portugal in July." not "July..".
        value = value.rstrip(" .!?")
    shown = str(value)[:1].upper() + str(value)[1:]
    wrong = str(fixed.get("wrong") or "").strip()
    if wrong:
        if fixed.get("key") == "pet":
            # A name put right is answered warmly and in different words from turn to turn; the
            # two names are in every line, so what varies is only the one warm thing after. The
            # seed is the line itself, so two different corrections do not get the same sentence
            # and the same line twice always answers the same way for a comparison.
            return pick(PET_RENAMED_SAY, memory,
                        str(fixed.get("said") or "")).format(v=shown, w=wrong)
        # A correction that names both values says both back: "8 kilos, not 5 — got it."
        shape = CORRECTION_SAY_PAIR.get(fixed.get("key"), "{v}, not {w} — got it.")
        return shape.format(v=shown, w=wrong)
    if fixed.get("dropped"):
        shape = CORRECTION_SAY_DROP.get(fixed.get("key"), "Not {v} — got it.")
        said = str(value)
        return shape.format(v=said[:1].lower() + said[1:])
    if in_a_sentence:
        # A plan is said inside a sentence - "Got it — the gym at 7." - so the article or the
        # "my" in front of it is not capitalised the way a name in that place would be. A
        # birthday is said the same way: "Got it — your birthday is the 4th of May."
        first, _, rest = shown.partition(" ")
        if first.lower() in PLAN_LOW_START:
            shown = first.lower() + (" " + rest if rest else "")
    if fixed.get("key") is None:
        # No fact was corrected, so there is nothing to keep: the line is said back and dropped.
        return BARE_ECHO_ONLY.format(v=shown)
    shape = CORRECTION_SAY.get(fixed.get("key"), "{v} — got it, I'll go with {v}.")
    if "{a}" in shape:
        return shape.format(v=shown, a=str(fixed.get("animal") or "pet"))
    return shape.format(v=shown)


def _job_note(value, known):
    """The corrected job said back in the frame the person used, or "" when there is no frame.

    The frame is kept with the job (facts.extract writes job_frame), so "i work in a school" then
    "sorry i meant a hospital" says "Got it — you work in a hospital". A frame that is the shift
    rather than a place ("i work nights") is left to the short note: "you work a nurse" is not a
    sentence anybody says.
    """
    frame = str((known if isinstance(known, dict) else {}).get("job_frame") or "").strip()
    if frame == "work":
        # "my job is a teacher" then "i meant a nurse": the word they used for it was the job
        # itself, so the note says the job.
        return "Got it \u2014 your job is " + _a(str(value)) + "."
    if frame.split(" ")[0] not in ("at", "in", "for", "as"):
        return ""
    said = _job_said({"job": value, "job_frame": frame})
    if not said:
        return ""
    return "Got it \u2014 " + said[:1].lower() + said[1:] + "."


def _a_held_part(memory, line):
    """True when a fact the store keeps is one of the things the line names."""
    known = user(memory)
    for key, pattern in PART_OF:
        if pattern.search(line) and known.get(key):
            return True
    return False


def _a_part_of_the_job_never_said(memory, low):
    """The ask back for a part of the job the person never described, or None."""
    line = str(low or "").strip()
    if not line or len(line.split()) > 8:
        return None
    if not (user(memory) or {}).get("job"):
        return None
    if PART_ADVICE.search(line) or PART_HELP.search(line) or re.search(r"\d", line):
        return None
    if not JOB_PART.search(line):
        return None
    ask = _turned(line)
    if not ask:
        return None
    return "You haven't said - " + ask + "?"


def _the_part_it_never_said(memory, low):
    """The honest ask back for a part of a kept fact they never gave, or None.

    Called only when nothing else in the store answered, so a line the store can answer never
    reaches it. It is the hedge it replaces: without it "what do i do there" after "i work at a
    cafe" is pointed at a search engine, and "and what do i do there" after "where do i work"
    is the same sentence the bot just said.
    """
    line = str(low or "").strip()
    if not line or len(line.split()) > 8:
        return None
    if PART_ADVICE.search(line) or PART_HELP.search(line) or re.search(r"\d", line):
        return None
    if not PART_ASK.search(line) or not RECORD_PART.search(line):
        return None
    mine = PART_MINE.search(line)
    if mine:
        if not _a_thing_it_keeps(memory, mine.group(1)):
            return None
    elif not (PART_POINTS.search(line)
              or (re.search(r"\b(?:i|im)\b", line) and _a_held_part(memory, line))):
        return None
    # A pointing word is about what was just said, so there has to be a fact line behind it and
    # not another question: "where do i work" then "and what do i do there" leans on the fact
    # line two turns back, which the store holds anyway.
    if not _a_kept_thing_behind(memory):
        return None
    ask = _turned(line)
    if not ask:
        return None
    return "You haven't said - " + ask + "?"


def _diet_how(diet):
    """The verb a diet is said with: what you drink is not what you eat."""
    words = set(re.split(r"[ ,]+", str(diet or "")[3:].strip().lower()))
    return "drink" if words & DRINK_DIET else "eat"


def _after_the_yes_no_frame(text):
    """What the line says after a yes/no question about someone else, or ""."""
    line = " ".join(str(text or "").split())
    match = YES_NO_FRAME.match(line)
    if match:
        return line[match.end():].strip()
    # Most people type no mark at all. The ask is the frame, and it ends where the telling
    # begins: at the next clause that has a person and a verb of its own. Without this the whole
    # line was read as the ask, so both the ask and the fact told with it went unanswered.
    opened = YES_NO_ASK.match(line)
    if not opened:
        return ""
    after_who = line[opened.end():]
    telling = TELLING_AFTER_ASK.search(after_who)
    if not telling:
        return ""
    return after_who[telling.start():].strip()


def _statement(text):
    """The plain statement a yes/no question about the person makes.

    "am i vegetarian?" is "i am vegetarian", "do i live in leeds?" is "i live in leeds", and
    "is my budget 500?" is "my budget is 500". None when the line is not that shape.
    """
    low = " ".join(text.lower().split()).strip(" ?!.")
    low = re.sub(r"^(?:sorry|hey|hi|ok|okay|so|but|and|well|quick one)[, ]+", "", low)
    for pattern, lead in CONFIRM_FRAMES:
        match = pattern.match(low)
        if match:
            return lead + match.group(1)
    # "is my dog called biscuit" -> "my dog is called biscuit". Only a short answer is read
    # this way, so "is my name hard to say" is not taken for a fact about the name.
    match = re.match(r"^(?:is|was) my\s+(\S+)\s+(.+)$", low)
    if match and (re.match(r"^(?:called |named )?\S+$", match.group(2))
                  or match.group(2).startswith("called ")):
        return "my " + match.group(1) + " is " + match.group(2)
    return None


def _said_matches(key, said, known):
    """Whether what the question states is what they told you. None when it is not about a
    fact the store would keep."""
    if key == "name":
        return _same(said, known) if known else False
    if key == "age":
        return known is not None and str(said) == str(known)
    if key == "diet" and DIET_ANY.match(str(said).strip()):
        # They asked about a diet in general, not about a diet they named: "im vegan" is not a
        # "no" to "am i on a diet". Left to the diet reader, which says the fact back.
        return None
    if key in ("job", "city", "from", "diet"):
        return _same(said, known) if known else False
    if key == "budget":
        mine = re.sub(r"[^0-9]", "", str(said))
        theirs = re.sub(r"[^0-9]", "", str(known or ""))
        return bool(mine) and mine == theirs
    if key == "allergies":
        stored = {str(a).lower() for a in (known or [])}
        return bool(said) and all(str(a).lower() in stored for a in said)
    if key == "pets":
        for pet in known or []:
            if _animal_family(pet.get("animal")) != _animal_family(said.get("animal")):
                continue
            if not said.get("name") or _same(pet.get("name"), said.get("name")):
                return True
        return False
    return None


def _restated(text, typed=None):
    """The statement behind a remembering frame: "do you remember that i live in leeds" ->
    "i live in leeds". None when the line is not that shape.

    The frame has to be asking something: a question mark, an auxiliary in front of it ("do you
    remember"), the bare verb ("remember that im 34"), or the tag that asks for the yes ("you
    know im veggie right"). "just so you know, im called sam" states the fact and is not a
    question about the store, so it is left to the ordinary reply.
    """
    low = " ".join(str(text or "").lower().split()).strip()
    tagged = bool(CONFIRM_TAG.search(low))
    low = CONFIRM_TAG.sub("", low).strip(" ?!.,")
    frame = REMEMBERING_FRAME.match(low)
    if not frame:
        return None
    question = "?" in str(text if typed is None else typed)
    # "you remember im allergic to nuts" is a confirmation seek; "you know im veggie" without a
    # question mark is the person telling you again ("just so you know, im called sam"), and
    # that is not a question about the store.
    asking = (question or tagged or frame.group("aux") or frame.group("bare")
              or (frame.group("verb") or "").startswith(("remember", "recall")))
    if not asking:
        return None
    rest = low[frame.end():].strip(" ?!.,")
    if not rest or not RESTATED.match(rest):
        return None
    return rest


def _behind_a_remembering_frame(text):
    """The line a remembering frame is around, when it is a line the store can read.

    _restated covers the person's own statements ("do you remember that i live in leeds"). This
    covers the rest: "can you remember that my son is allergic to nuts" and "can you remember the
    dentist is on tuesday" are the same shape - a frame with a fact behind it - and both were
    answered as questions about the bot's memory, which is not what the line asks. The test is
    the store's own: what is left after the frame is read as a fact, or the frame is left alone.
    """
    low = " ".join(str(text or "").lower().split()).strip(" ?!.,")
    frame = REMEMBERING_FRAME.match(low)
    if not frame:
        return None
    questioning = ("?" in str(text or "") or frame.group("aux") or frame.group("bare")
                   or (frame.group("verb") or "").startswith(("remember", "recall")))
    if not questioning:
        return None
    rest = low[frame.end():].strip(" ?!.,")
    if not rest or rest == low:
        return None
    if not SAYS_SOMETHING.search(rest):
        # "do you remember my mums age" is a question about a fact, not the fact: the words
        # behind the frame only name the thing asked about. Read as a statement they filed the
        # word "age" as the mum's name and answered "Age is 68."
        return None
    if extract.extract(rest):
        return rest
    return None


def _the_food_named(rest):
    """The category a bare food phrase names, or "" when it names none of them."""
    said = [word for word in re.findall(r"[a-z']+", str(rest or "").lower())
            if word not in NOT_THE_FOOD]
    if not said:
        return ""
    for category, words in FOOD_CATEGORIES:
        if all(any(word == one or word == one.rstrip("s") or word.rstrip("s") == one.rstrip("s")
                   for one in words) for word in said):
            return category
    return ""


def _a_rate_changed(text, memory):
    """True when the figure this line changed is money put by each month, not a word of a fact."""
    rewritten = resize.rewritten(text, memory)
    if not rewritten or resize.rate(rewritten) is None:
        return False
    return bool(PUTTING_BY.search(rewritten))


def _a_number_word(number):
    """A number said in words: 8 -> "eight", 71 -> "seventy-one", 105 -> "one hundred and five"."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        return str(number)
    if number < 0:
        return str(number)
    if number < len(_NUMBER_WORDS):
        return _NUMBER_WORDS[number]
    if number < 100:
        tens, ones = divmod(number, 10)
        return _TENS_WORDS[tens] + ("-" + _NUMBER_WORDS[ones] if ones else "")
    if number < 1000:
        hundreds, rest = divmod(number, 100)
        said = _NUMBER_WORDS[hundreds] + " hundred"
        return said if not rest else said + " and " + _a_number_word(rest)
    return str(number)


def _fact_moved_this_turn(text, memory):
    """The correction that moves a fact to another person: "Your daughter, not your son - got it."."""
    moved = memory.get("fact_moved") if isinstance(memory, dict) else None
    if not isinstance(moved, dict) or moved.get("said") != " ".join(str(text or "").lower().split()):
        return None
    memory.pop("fact_moved", None)
    who = str(moved.get("who") or "").strip()
    was_who = str(moved.get("was_who") or "").strip()
    value = moved.get("value")
    if moved.get("kind") == "age":
        number = _a_number(value)
        if not number:
            return None
        said_value = _a_number_word(number)
    elif isinstance(value, str):
        said_value = value
    else:
        return None
    if not (who and was_who and said_value):
        return None
    return pick(CORRECTED_WHICH_PERSON, memory, seed_text=text).format(
        Value=said_value[:1].upper() + said_value[1:], value=said_value, who=who,
        was_who=was_who)


def _fact_fixed_this_turn(text, memory):
    """The line that says a fact about someone has been put right: "Eight, not seven - got it."."""
    fixed = memory.get("fact_fixed") if isinstance(memory, dict) else None
    if not isinstance(fixed, dict) or fixed.get("said") != " ".join(str(text or "").lower().split()):
        return None
    memory.pop("fact_fixed", None)
    who = str(fixed.get("who") or "").strip()
    was = fixed.get("was")
    value = fixed.get("value")
    # An age arrives as a figure in one shape and as a word in the other ("8" from the reader,
    # and 7 already stored), so both sides are read as numbers before the words are chosen.
    new_number, old_number = (_a_number(value), _a_number(was))
    if fixed.get("kind") == "age" and new_number and old_number:
        value_said = _a_number_word(new_number)
        was_said = _a_number_word(old_number)
        said = pick(CORRECTED_AGAIN, memory, seed_text=text).format(
            Value=value_said[:1].upper() + value_said[1:], was=was_said,
            were=was_said[:1].upper() + was_said[1:], who=who,
            value=value_said)
    elif isinstance(value, str) and isinstance(was, str):
        said = pick(CORRECTED_AGAIN_WHO, memory, seed_text=text).format(
            Value=value[:1].upper() + value[1:], who=who or "you", value=value)
    else:
        return None
    return said


def _the_job_was_just_said(memory):
    """True when the line before the ask is where the job was given, and is nothing but the job.

    "what do i do" answers the line it follows, so the job has to be in that line: a turn later
    the chat has moved on and the same words ask about whatever it moved on to. The last line is
    read from the history the store keeps, so a job said two turns back does not wrongly claim
    the ask, and a job the person only implied is not guessed at.

    The line also has to be *only* the job. In "im a builder and i fell off a ladder" the job is a
    detail of a report, and the whole of what the person is asking about is the fall: the ask is
    the emergency, and "You told me you're a builder" in place of the 999 line is worse than any
    entry the store was shadowing. What may stand around the job is the words people frame it
    with - "i work as a", "my job is a", "im a" - and nothing that says anything else.
    """
    job = str(user(memory).get("job") or "").strip().lower()
    if not job:
        return False
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("user") or "").strip()
        if not said:
            continue
        if BARE_WHAT_I_DO.match(_bare(said)):
            continue  # the ask again: it answers the line before it too
        return job in said.lower() and _nothing_but_the_job(said, job, memory)
    return False


def _nothing_but_the_job(said, job, memory):
    """True when the job is all the line said, once the words around it are set aside."""
    rest = str(said).lower().replace(job, " ")
    frame = str(user(memory).get("job_frame") or "").strip().lower()
    if frame:
        rest = rest.replace(frame, " ")
    return not [word for word in re.findall(r"[a-z']+", rest)
                if len(word) > 2 and word not in JOB_LINE_WORDS]


def _the_allergy_is_what_is_asked(text, memory):
    """True when an ask for advice about what to avoid is a question about the allergy.

    The answer names a fact, so the fact has to be what is being asked about. Two things say it
    is not, and both stand the store down:

    * a word after the ask that names the thing to avoid. "what should i avoid in the sun" is
      about sunburn and "on the roads" about driving, unless the thing named is something eaten
      ("what should i avoid in a stir fry").
    * an allergy that is not on the table. The store answers a fact it holds, and a chat that
      has moved on to the boiler and then asks what to watch out for is asking about the
      boiler: the last thing answered is what is in front of them, not the allergy. The fact is on the
      table when they said it in this line or the turn before, and when nothing else has been
      said at all.
    """
    rest = AVOID_REST.search(text)
    tail = " ".join(rest.group(1).split()) if rest else ""
    if tail and not EATING.search(tail):
        return False
    said = " ".join(text.split())
    before = last_user(memory)
    if ALLERGY_SAID.search(said) or ALLERGY_SAID.search(before or ""):
        return True
    return not before


def _points_at_something_else(low):
    """True when the line points at a thing that is not an animal ("this song", "my new business").

    Only the word that follows the pointing word is read: "what should i call this song" and
    "what should i call this function in python" name no animal, and the pet in memory is not what
    they are about. A word that names an animal, or that points at nothing in particular ("call it",
    "this one", "a name"), leaves the pet in play.
    """
    for word in POINTING.findall(low or ""):
        if word in extract.ANIMALS or word in POINTING_ANY:
            continue
        return True
    return False


def _a_name_for_the_pet(text, memory, low):
    """A short list of names for the pet in play, or None when the line is not about naming one."""
    if not NAME_ASK.search(low or ""):
        return None
    family = _the_pet_in_play(low, memory)
    if not family or family == "pet":
        return None
    if _points_at_something_else(low):
        return None
    if _a_pet_of_theirs_is_named(low, family, memory):
        # "what shall i call him" a turn after the name was settled is not a request for three
        # more names: the pet in play has one, and the store answers with it.
        return None
    pool = list(_pet_names(family))
    # A different three each time, so asking twice does not get the same list back.
    seed = len(memory.get("turns") or []) * 7919 + sum(ord(c) for c in str(text).lower())
    shuffled = random.Random(seed).sample(pool, 3)
    advice = NAME_ADVICE[seed % len(NAME_ADVICE)]
    animal = _a(family)
    return ("For " + animal + ": " + ", ".join(shuffled[:-1]) + " or " + shuffled[-1] + ". "
            + advice)


def _the_verb_from_the_line(plan, line):
    """The words the other half of the line carries, for a half that was left without a verb.

    "my niece turns 5 in may and my nephew in june" keeps "my nephew in june", and the ask that
    names nothing ("when is my nephew") has no verb to put back: what the half left out is still
    in the line, in the other half's own words ("turns 5")."""
    wanted = " ".join(str(plan or "").lower().split())
    text = " ".join(str(line or "").split())
    if not wanted or not text:
        return ""
    for piece in re.split(r"\s+and\s+|,|;", text):
        clause = " ".join(piece.split()).strip(" ,.;:-!")
        if not clause or " ".join(clause.lower().split()) == wanted:
            continue
        match = _A_DATE_AT_THE_END.match(clause)
        if not match:
            continue
        # The other half is "my niece turns 5": the determiner and the person, then the words
        # that are left are what the half this ask names was never given ("turns 5").
        before = match.group("subject").split()
        if len(before) < 3 or before[0].lower() not in ("my", "our", "the", "his", "her", "their"):
            continue
        body = " ".join(before[2:]).strip(" ,")
        words = body.split()
        if not words or len(words) > 4 or not words[0].isalpha():
            continue
        # A small count in the other half is said in words when the half is said whole: "my
        # nephew turns 5 in june" is "Your nephew turns five in June".
        words = [_a_number_word(word) if word.isdigit() and len(word) < 3 else word
                 for word in words]
        body = " ".join(words)
        # a half it cannot stand on its own is not a verb: "is" alone says nothing about the day
        if words[0].lower() in ("is", "are", "was", "were", "am"):
            continue
        return body
    return ""


def _the_verb_they_asked(plan, low, line=""):
    """The plan with the verb the ask named put back into it: "my course in february" is what a
    line with two things in it keeps of "i start my new job in january and my course in
    february", and "when does my course start" names the word the half left out.

    Only a plan with a date at the end and nothing but the thing before it, so the phrase the ask
    gives is the verb of that thing and not the rest of the question.
    """
    text = " ".join(str(plan or "").split())
    match = _A_DATE_AT_THE_END.match(text)
    if not match:
        return plan
    subject = match.group("subject")
    # "my daughters" is the thing, and "is" is the verb with its predicate left out: the ask
    # ("when is my daughters birthday") has the predicate, and it goes before the date.
    if subject.split()[-1] in ("is", "are", "was", "were"):
        subject = " ".join(subject.split()[:-1])
    asked = " ".join(str(low or "").split()).strip("?.! ")
    at = _the_whole_word_in(asked, subject)
    if at < 0:
        return plan
    rest = asked[at + len(subject):].strip()
    if not rest or rest in ("again", "now", "this year", "next year"):
        # The ask names nothing the half left out, so the line it came from does: a half that keeps
        # no verb is completed from the other half's words, and said whole.
        borrowed = _the_verb_from_the_line(plan, line)
        if borrowed:
            return subject + " " + borrowed + " " + match.group("date")
        return plan
    words = rest.split()
    if len(words) > 4:
        return plan
    # The verb the person asked with, in the form it takes about a thing of theirs. A word that is
    # not a doing word ("birthday" in "when is my daughters birthday") is the predicate left out
    # of the plan, and it is said as it is.
    doing = ("birthday", "bday", "dob", "date of birth", "name")
    if words[0].lower() in doing:
        return subject + " " + rest + " is " + match.group("date")
    if words[0].lower().endswith("ing") and len(words[0]) > 4:
        # "when is my nephew turning 5" is the doing word as it is, with the "is" it needs: a
        # third person "turnings" is not a word.
        return subject + " is " + " ".join(words) + " " + match.group("date")
    if words[0].lower() in ("is", "are", "was", "were", "will", "would", "can", "could",
                            "has", "had", "does", "did"):
        return subject + " " + " ".join(words) + " " + match.group("date")
    if words[0].lower().endswith("s") and not words[0].lower().endswith("ss"):
        # A word already said in the plural after the thing is more of the thing, not the verb:
        # "when are my dentist appointments" is the appointment they told me about, and reading
        # "appointments" as a verb made "Your dentist appointmentses is on the 3rd of June". A verb
        # the ask names comes in the form the ask is built with ("when does my course start"), and
        # a verb misspelled in the plural loses nothing by being left out.
        return plan
    words[0] = _third_person(words[0])
    return subject + " " + " ".join(words) + " " + match.group("date")


def _their_place(low):
    """The place they asked about, when the line asks what is in one of their own food places."""
    for pattern in (IN_A_PLACE, IN_MY_PLACE):
        found = pattern.search(low)
        if found and found.group(1) in THEIR_PLACES:
            return found.group(1)
    if FOR_A_MEAL.search(low):
        return "fridge"  # what to have for dinner is answered from what is in it
    return None


def _job_reply(memory, where=False):
    known = user(memory)
    job, city = known.get("job"), known.get("city")
    place = str(known.get("workplace") or "").strip()
    if where and place:
        # The place is exactly what was asked for, so it is the answer, with the role left out.
        return "You work " + _place_phrase(place) + "."
    if job and city:
        said = _job_said(known)
        return pick([said + " in " + city + ".",
                     "You're in " + city + " — " + said[:1].lower() + said[1:] + "."],
                    memory)
    if job:
        return _job_said(known) + "."
    if city and where:
        # Only a where-ask can be answered with the town: "what do i do for a living" with no job
        # kept was answered "You said you live in Leeds", which answers a different question.
        # The honest line below says the store has no job, which is what was asked.
        return "You said you live in " + city + "."
    return _deny(memory, "job", pick(["You haven't told me what you do yet.",
                                      "I don't know your job — you haven't said."], memory))


def _a_circumstance(job):
    """Whether the word after "I work" is how they work, not what they do.

    "i work nights", "i work part time", "i work two jobs" are circumstances, so the verb is
    kept: "you work nights". "my job is a chef" arrives with the same frame but names a role, so
    it is "you're a chef". A plural is a circumstance too ("nights", "shifts"); a singular role
    noun is not.
    """
    words = re.findall(r"[a-z0-9']+", job.lower())
    if not words:
        return True
    if any(word in WORK_CIRCUMSTANCE for word in words):
        return True
    last = words[-1]
    return last.endswith("s") and not last.endswith("ss")


def _job_said(known):
    """The job said back the way they said it: "You work in a warehouse", "You're a nurse".

    A job told with a place preposition is a place, so it is not "you're a warehouse": the
    frame is kept with the job (facts.extract writes job_frame) and the reply follows it. "at"
    names a place, so it keeps its capital: "You work at Tesco".
    """
    job = _yours(str(known.get("job") or "").strip())
    frame = str(known.get("job_frame") or "").strip()
    preposition = frame.split(" ")[0]
    if frame == "was":
        # The job was given in the past ("i was a teaching assistant before the kids"), so it is
        # said back in the past. The tense is kept with the frame, the same way a place
        # preposition is, so it cannot be lost between the line and the ask.
        if _a_circumstance(job):
            return "You did " + job
        return "You were " + _a(job)
    if frame == "work":
        # "i work nights", "i work two jobs", "i work part time": the verb is the frame, so it is
        # "you work ..." and never "you're a nights". A role said with the same frame is the
        # exception: "my job is a chef" is "you're a chef", never "you work chef".
        if _a_circumstance(job):
            return "You work " + job
        return "You're " + _a(job)
    if preposition in ("in", "for", "on", "with"):
        # "in a warehouse", "on the tills", "with the council": the preposition they said is the one
        # said back, so it is never "You told me you're a council".
        return "You work " + frame + " " + job
    if preposition == "as":
        # "i got a new job as a chef": the article they said is kept, so it is "as a chef" and
        # "as an engineer".
        return "You work " + frame + " " + job
    if preposition == "at":
        # "at" alone is followed by a name, which keeps its capital ("You work at Tesco"); with its
        # article it is an ordinary place, so the job stays as it was said ("at the hospital").
        if frame == "at":
            return "You work at " + job[:1].upper() + job[1:]
        return "You work " + frame + " " + job
    return "You told me you're " + _a(job)


def _job_phrase(known):
    """The job as a clause inside another sentence: "you work nights", "you're a nurse".

    The summary is a sentence, not a reply, so it needs the clause without the capital and
    without "You told me". The frame still decides the words: a shift is "you work nights",
    never "a nights".
    """
    said = _job_said(known)
    low = said[:1].lower() + said[1:]
    head = "you told me "
    if low.startswith(head):
        low = low[len(head):]
    return low


def _places_reply(memory, low):
    known = user(memory)
    # "where does my sister live" is about her, not about the user: the place is in the line
    # that put her there, so read it back out of the conversation.
    # "whereabouts does my sister live" is the same ask: the same where-word the gate reads.
    who = _asked_person(memory, low)
    if who:
        hers = _other_place(memory, who)
        if hers:
            return hers
        return ("You haven't said where your " + who
                + (" live." if who.lower().endswith("s") else " lives."))
    city = known.get("city")
    if re.search(r"\bborn\b", low):
        # A birth is not where they are from: "i was born in lagos but i grew up in ibadan" has
        # both, and the two questions want different answers.
        born = known.get("born")
        if isinstance(born, str) and born:
            return pick(["You were born in " + born + ".", born + " — you were born there."],
                        memory)
        origin = known.get("from")
        if isinstance(origin, str) and origin:
            return pick(["You haven't told me where you were born — you're from " + origin + ".",
                         "I don't know where you were born. You told me you're from " + origin + "."],
                        memory)
        return pick(["You haven't told me where you were born.",
                     "I don't know that one — you haven't said where you were born."], memory)
    if re.search(r"\bhometown\b", low):
        return _from_reply(memory)
    if GROWN_UP_ASK.search(low):
        # "where did i grow up" asks the same fact as "where am i from": the line that gave it
        # said it as growing up somewhere, and the extractor files it as where they are from.
        # It is said back as growing up, though - "You're from Dublin" answers the question but
        # not the words they asked it with.
        return _grown_up_reply(memory)
    going = re.search(r"\bgoing\b|\btrip\b|\bholiday\b|\btravel", low)
    # "where am I from" asks where they grew up, not where they live now.
    if (isinstance(city, str) and city and known.get("home") and not going
            and not re.search(r"\bfrom\b", low)):
        # The home as they said it when they said where it stands ("a small village near York"):
        # the place is theirs, and the answer is neither a denial nor a different place.
        said_with = known.get("home")
        return "You live in " + (said_with if isinstance(said_with, str) else city) + "."
    if re.search(r"\bfrom\b|\bcome from\b", low):
        return _from_reply(memory)
    places = [p for p in (known.get("places") or []) if isinstance(p, str)]
    if going:
        # "where am I going" is about the trip, so the place they live is not the answer.
        away = [p for p in places if isinstance(city, str) and p != city] or places
        places = away
    if "city" in low or "town" in low:
        cities = [p for p in places if p.lower() not in extract.COUNTRIES]
        if cities:
            places = cities
    if not places:
        return _deny(memory, "place", "You haven't mentioned a place yet.")
    if re.search(r"\bwhere (?:do|does) (?:i|we) live\b|\bwhere am i (?:living|based)\b", low):
        # They asked where they live and never said: the place they named is not an answer.
        # A place they are from is the one thing worth naming here, and saying it keeps the
        # two questions apart: "im from cork" does not answer "where do i live?".
        origin = known.get("from")
        if isinstance(origin, str) and origin:
            return pick(["You haven't told me where you live — I know you're from " + origin + ".",
                         "I don't know where you live. You're from " + origin + ", that I do know."],
                        memory)
        return ("You haven't told me where you live. You mentioned " + places[0] + "."
                if len(places) == 1 else
                "You haven't told me where you live. You mentioned " + places[0] + ", then "
                + ", ".join(places[1:]) + ".")
    first = places[0]
    rest = [p for p in places[1:] if p != first]
    if rest:
        return "You said " + first + " first, then " + ", ".join(rest) + "."
    return "You mentioned " + first + "."


def _a_diet_predicate(who, diet):
    """A person's diet as the words after their name: "eats fish", "doesn't eat meat", "is vegan".

    The store keeps a restriction as "no fish", and what somebody eats put back as "eats fish":
    a take-back of a restriction is not an empty record, it is the food they eat now, so the
    recall says "Your son eats fish." where "Your son is eats fish." is not a sentence.
    """
    said = str(diet or "").strip()
    if said.startswith("eats "):
        return (_eats(who) + " " + said[5:]).strip()
    if said.startswith("no "):
        # What they drink is not what they eat: "my mate is teetotal" is kept as `no alcohol`
        # and said back "Your mate doesn't drink alcohol."
        return (_does_not(who) + " " + _diet_how(said) + " " + said[3:]).strip()
    return (_is_are(who) + said).strip()


def _a_take_back_said_back(line, gone):
    """Their own take-back, said back as a statement: "You told me you stopped doing keto."

    A take-back is not a wrong fact and it is not a fact at all, so neither the store's value
    ("you're doing keto") nor the line as a quote ("You said: "i stopped keto"") answers the
    question someone asked. What they said, said plainly, does.
    """
    said = " ".join(str(line or "").split())
    if STOPPED_SAID.match(said):
        rest = re.sub(r"^(?:i|we)(?:'ve|ve|\s+have|\s+had)?\s+", "", said, flags=re.I)
        return "You told me you " + " ".join(rest.split()) + "."
    if str(gone).strip().lower() in ("diet", "dieting", "on a diet"):
        return "You told me you're not on a diet any more."
    if NEGATED_SAID.search(said):
        # "im not vegetarian" is a fact about now, not a take-back of one they had: restating the
        # negative is true, and "you stopped being vegetarian" says they once were.
        return _a_negation_said_back(gone, said)
    if gone in WAY_OF_EATING:
        return "You told me you stopped being " + _diet_words(gone) + "."
    if gone in PLAN_DIETS:
        return "You told me you stopped doing " + _diet_words(gone) + "."
    return "You told me you stopped " + _diet_words(gone) + "."


def _a_negation_said_back(gone, line=""):
    """"You told me you're not vegetarian", for a diet said as a negation rather than left."""
    value = str(gone or "").strip().lower()
    tail = " any more" if ANY_MORE.search(str(line or "")) else ""
    if not value:
        return "You told me you're not on a diet" + tail + "."
    if value.startswith("no "):
        return "You told me you don't " + _diet_how(value) + " " + value[3:] + tail + "."
    if value in WAY_OF_EATING:
        return "You told me you're not " + _diet_words(value) + tail + "."
    if value in PLAN_DIETS:
        return "You told me you're not doing " + _diet_words(value) + tail + "."
    return "You told me you're not " + _diet_words(value) + tail + "."


def _says_the_fact(line, key):
    """Whether a past line tells the thing a denial would deny, rather than asking about it.

    A line that only carries the word is not a fact: "how do i stick to a budget", "am i
    allergic to anything" and "what job should i look for" are questions, and "we need to
    save for a deposit" is a plan, so quoting any of them back answers the question with
    itself. What they said in other words is still what they said - "my budget is tight this
    month", "i mostly eat low fat stuff" - so those stay quotable.
    """
    if (extract.extract(line) or {}).get(key):
        return True
    low = " ".join(str(line or "").lower().split())
    if ASKING_ABOUT_IT.search(low) or PLANNING_IT.search(low):
        return False
    if A_CLAIM_OF_TELLING.match(low):
        # "i told you about the damp" carries the word and says nothing about the damp: it is the
        # person complaining that they said it, so quoting it back answered "what did i say about
        # the damp" with the complaint. A claim carrying a clause ("i told you my dog died") names
        # the fact itself and never reaches here - extract() finds it in the branch above.
        return False
    return True


def _the_line_about(memory, key, own=None):
    """The last line the person sent that says the thing a denial would deny, or "".

    own, when it is given, says whether a line that carries the words carries the fact itself:
    "my wife is on a diet" has the word "diet" in it and is not their diet, so a denial must
    not quote it back as one.
    """
    words = DENIAL_WORDS.get(key) or ()
    stems = DENIAL_STEMS.get(key) or ()
    if not words and not stems:
        return ""
    parts = [r"\b" + re.escape(word) + r"\b" for word in words]
    parts += [r"\b" + re.escape(stem) for stem in stems]
    wanted = re.compile("|".join(parts))
    for turn in reversed(memory.get("turns") or []):
        line = str((turn or {}).get("user") or "") if isinstance(turn, dict) else ""
        found = " ".join(re.findall(r"[a-z']+", line.lower()))
        if not found:
            continue
        if not wanted.search(found):
            continue
        if key in (extract.denials(line) or {}):
            continue  # a line that takes the fact back is not the fact said
        # A line that asks about the thing, or plans around it, is not a line that tells it:
        # "how do i stick to a budget" and "we need to save for a deposit" carry the word a
        # budget denial would deny, and quoting either back answers the question with itself.
        if not _says_the_fact(line, key):
            continue
        if _said_of_someone_else(line, wanted):
            continue
        if own is not None and not own(line):
            continue
        return " ".join(line.split())
    return ""


def _deny(memory, key, denial, own=None):
    """The denial, unless they did say it: then their own line is the honest answer."""
    said = _the_line_about(memory, key, own)
    if said:
        return "You said: \"" + said + "\""
    return denial
